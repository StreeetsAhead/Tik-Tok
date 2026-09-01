"""THE GAZE (conquerors) - 13.8s, 1080x1920 @30fps.
Six conquerors, eye-anchored, layered compositing: textures from Turner and the mosaic
drift against the portraits, impact frames with RGB split on every cut, bloom on the gold,
a strobe of gazes, then all six pairs of eyes stacked. End card as before.
Run: python3 render_conquerors.py style   -> style frames only (fast)
     python3 render_conquerors.py full    -> full render to CONQ_silent.mp4
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os, sys, math, json, subprocess

SP  = "/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad"
SRC = f"{SP}/conq"
OUT = "/home/user/Tik-Tok/build/frames_cq"; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
EYE_X, EYE_Y, IOD_F = 0.50, 0.40, 0.26
FONT_S="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_N="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EYES = json.load(open(f"{SP}/conq_eyes.json"))
# napoleon + alexander fixed in conq_eyes.json via dot-probe
EYES["charlemagne"]["eye_cy"]=0.255; EYES["mehmed"]["eye_cx"]=0.455

Image.MAX_IMAGE_PIXELS=400_000_000
_IM={}
def img(k):
    if k not in _IM:
        im=Image.open(f"{SRC}/{k}.jpg").convert("RGB")
        if max(im.size)>4300:
            s=4300/max(im.size); im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
        _IM[k]=im
    return _IM[k]

def framed(k, zoom):
    """Eye-anchored crop, padded onto near-black when the frame leaves the canvas."""
    e=EYES[k]; im=img(k); iw,ih=im.size
    scale=IOD_F*W*zoom/(e["iod"]*iw)
    cw,ch=W/scale,H/scale
    x=e["eye_cx"]*iw-EYE_X*cw; y=e["eye_cy"]*ih-EYE_Y*ch
    out=Image.new("RGB",(W,H),(6,6,8))
    x0,y0=max(x,0),max(y,0); x1,y1=min(x+cw,iw),min(y+ch,ih)
    if x1>x0 and y1>y0:
        c=im.crop((int(x0),int(y0),int(x1),int(y1)))
        tw,th=max(int((x1-x0)*scale),1),max(int((y1-y0)*scale),1)
        c=c.resize((tw,th),Image.LANCZOS,reducing_gap=3.0)
        out.paste(c,(int((x0-x)*scale),int((y0-y)*scale)))
    return out

# textures pre-scaled to cover frame + drift margin
_TX={}
def tex(k, t, dx, dy, s0=1.0, s1=1.0, lt=0.0):
    if k not in _TX:
        im=img(k); m=1.45
        sc=max(W*m/im.width, H*m/im.height)
        _TX[k]=im.resize((int(im.width*sc),int(im.height*sc)),Image.BILINEAR,reducing_gap=2.0)
    b=_TX[k]; sc=s0+(s1-s0)*lt
    ww,wh=int(W/sc),int(H/sc)
    cx=(b.width-ww)/2 + dx*t; cy=(b.height-wh)/2 + dy*t
    cx=min(max(cx,0),b.width-ww); cy=min(max(cy,0),b.height-wh)
    return np.asarray(b.crop((int(cx),int(cy),int(cx)+ww,int(cy)+wh)).resize((W,H),Image.BILINEAR),
                      dtype=np.float32)/255.0

def screen(a,b,op): return a+(1-(1-a)*(1-b)-a)*op
def mult(a,b,op):   return a+(a*b-a)*op
def softl(a,b,op):
    r=np.where(b<=0.5, a-(1-2*b)*a*(1-a), a+(2*b-1)*(np.sqrt(np.clip(a,0,1))-a))
    return a+(r-a)*op

# ---- shots -------------------------------------------------------------------
def ease(t): return t*t*(3-2*t)
def expo_out(t): return 1-pow(2,-7*t) if t<1 else 1.0

SHOTS=[  # (f0,f1,key,z0,z1,zcurve, layers=[(tex,mode,op,dx,dy,s0,s1)], warmth,bloom,red)
 (0,  60,"caesar",     2.60,1.15,"ease", [("map","mult",0.34,-26,-14,1.06,1.00),
                                          ("storm","screen",0.14, 18,  6,1.00,1.05)], -0.65,0.25,0),
 (60, 97,"alexander",  1.55,1.28,"ease", [("battle_tex","screen",0.24,-34,-8,1.05,1.00)], 0.10,0.30,0),
 (97, 134,"charlemagne",1.04,1.24,"ease",[("fire","screen",0.30,  10,-40,1.00,1.07)], 0.80,0.65,0),
 (134,171,"genghis",   1.52,1.70,"ease", [("storm","screen",0.24,-30,-10,1.00,1.06)], -0.35,0.20,0),
 (171,208,"mehmed",    1.14,1.34,"ease", [("map","mult",0.20, 20,-10,1.03,1.00),
                                          ("fire","screen",0.13,-14,-22,1.00,1.04)], 0.45,0.45,0),
 (208,283,"napoleon",  2.00,0.126,"expo",[("storm","screen",0.30,-40,-16,1.08,1.00)], 0.25,0.50,1),
]
ORDER=["caesar","alexander","charlemagne","genghis","mehmed","napoleon"]
STROBE0,STROBE_N,STROBE_F=283,6,5
STACK0,STACK1=313,333
BLACK1=339
CARD0,N=339,414
CUT_FRAMES=[s[0] for s in SHOTS[1:]]+[STROBE0]+[STROBE0+i*STROBE_F for i in range(1,STROBE_N)]+[STACK0]

def vign(w,h,strength=0.68,cy=0.42):
    y,x=np.ogrid[0:h,0:w]
    d=np.sqrt(((x-w/2)/(w*0.66))**2+((y-h*cy)/(h*0.56))**2)
    return np.clip(1-strength*np.clip(d-0.40,0,None)**1.5,0.04,1)[...,None].astype(np.float32)
VIG=vign(W,H)
_gw=None
def goldwash():
    global _gw
    if _gw is None:
        y,x=np.ogrid[0:H,0:W]
        d=np.sqrt(((x-W*0.5)/(W*0.9))**2+((y-H*0.36)/(H*0.7))**2)
        m=np.clip(1-d,0,1)[...,None].astype(np.float32)**2
        _gw=m*np.array([1.0,0.78,0.42],dtype=np.float32)
    return _gw

def grade(a, warmth=0.0, red=0):
    lum=a@np.array([0.299,0.587,0.114],dtype=np.float32)
    a=lum[...,None]+(a-lum[...,None])*0.80
    a=(a-0.5)*1.33+0.44
    a=np.clip(a,0,1)
    a[...,2]+=0.09*(1-a[...,2])**2.2*(1-0.5*warmth)
    a[...,0]+=(0.045+0.075*max(warmth,0))*(a[...,0]**1.4)
    a[...,1]+=(0.012+0.030*max(warmth,0))*(a[...,1]**1.6)
    if warmth<0:
        a[...,2]+=0.06*(-warmth)*(1-a[...,2]); a[...,0]*=1+0.02*warmth
    if red:  # let the cloak burn
        rm=np.clip(a[...,0]-np.maximum(a[...,1],a[...,2]),0,1)[...,None]
        a=np.clip(a+rm*np.array([0.22,-0.05,-0.05],dtype=np.float32),0,1)
    return np.clip(a,0,1)

def bloom(a, amt):
    if amt<=0: return a
    hi=np.clip(a-0.70,0,None)*amt*2.6
    b=np.asarray(Image.fromarray((np.clip(hi,0,1)*255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(22)),dtype=np.float32)/255.0
    return np.clip(a+b,0,1)

def chroma_edge(fr):
    r=fr.resize((int(W*1.004),int(H*1.004))).crop((int(W*0.002),int(H*0.002),int(W*0.002)+W,int(H*0.002)+H))
    b=fr.resize((int(W*0.996),int(H*0.996)))
    bb=Image.new("RGB",(W,H)); bb.paste(b,((W-b.width)//2,(H-b.height)//2))
    out=np.stack([np.asarray(r)[...,0],np.asarray(fr)[...,1],np.asarray(bb)[...,2]],axis=-1)
    return Image.fromarray(out)

def lspace(d,xy,text,font,fill,sp=0):
    ws=[d.textlength(c,font=font) for c in text]; x=xy[0]-(sum(ws)+sp*(len(text)-1))/2
    for c,cw in zip(text,ws): d.text((x,xy[1]),c,font=font,fill=fill); x+=cw+sp
def card_layer():
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rectangle([W*0.36,H*0.443,W*0.64,H*0.443+1],fill=(235,230,218,110))
    lspace(d,(W/2,H*0.478),"VERBAVIA",ImageFont.truetype(FONT_S,68),(250,247,240,255),sp=13)
    lspace(d,(W/2,H*0.478+104),"verbavia.com",ImageFont.truetype(FONT_N,31),(238,233,222,205),sp=9)
    return L
CARD=card_layer()

STRIPS=None
def strips():
    global STRIPS
    if STRIPS is None:
        STRIPS=[]
        sh=H//6
        for k in ORDER:
            f=framed(k,2.15)
            band=f.crop((0,int(H*EYE_Y)-sh//2,W,int(H*EYE_Y)-sh//2+sh))
            STRIPS.append(np.asarray(band,dtype=np.float32)/255.0)
    return STRIPS

rng=np.random.default_rng(9)
def render_frame(i):
    # ---- source composite -------------------------------------------------
    if i>=BLACK1:
        arr=np.zeros((H,W,3),dtype=np.float32)
    elif STACK0<=i<STACK1:
        st=strips(); sh=H//6
        arr=np.zeros((H,W,3),dtype=np.float32)
        for j,band in enumerate(st):
            off=int(2.5*math.sin((i-STACK0)*0.25+j*1.7))
            arr[j*sh:(j+1)*sh]=np.roll(band,off,axis=1)
        arr=grade(arr,0.15,0)
    elif i>=STROBE0:
        j=min((i-STROBE0)//STROBE_F,STROBE_N-1)
        arr=np.asarray(framed(ORDER[j],1.85),dtype=np.float32)/255.0
        arr=grade(arr,(0.6 if j%2 else -0.4),0)
    else:
        for (f0,f1,k,z0,z1,zc,layers,warm,bl,red) in SHOTS:
            if f0<=i<f1: break
        lt=(i-f0)/max(f1-f0,1)
        zt=expo_out(lt) if zc=="expo" else ease(lt)
        zoom=z0+(z1-z0)*zt
        arr=np.asarray(framed(k,zoom),dtype=np.float32)/255.0
        ts=(i-f0)/FPS
        for (tk,mode,op,dx,dy,s0,s1) in layers:
            tx=tex(tk,ts,dx,dy,s0,s1,lt)
            arr = screen(arr,tx,op) if mode=="screen" else (mult(arr,tx,op) if mode=="mult" else softl(arr,tx,op))
        arr=grade(arr,warm,red)
        arr=bloom(arr,bl)
        # gold wash breathing
        arr=np.clip(arr+goldwash()*(0.045+0.02*math.sin(i*0.21)),0,1)
    # ---- impacts on cuts --------------------------------------------------
    for cf in CUT_FRAMES:
        if 0<=i-cf<4:
            d=(4-(i-cf))/4.0
            arr=np.clip(arr*(1+0.35*d),0,1)
            sh_=int(9*d)
            if sh_: arr=np.roll(arr,(rng.integers(-sh_,sh_+1),rng.integers(-sh_,sh_+1)),axis=(0,1))
            sp=int(7*d)
            if sp:
                arr[...,0]=np.roll(arr[...,0],sp,axis=1); arr[...,2]=np.roll(arr[...,2],-sp,axis=1)
            break
    if i<BLACK1:
        arr*=(1.0+0.015*math.sin(i*0.8)+rng.normal(0,0.004))
        arr+=rng.normal(0,0.016,arr.shape).astype(np.float32)*(0.35+0.65*(1-arr))
        arr*=VIG
        if rng.random()<0.10:   # dust
            for _ in range(rng.integers(1,3)):
                x,y=rng.integers(60,W-60),rng.integers(60,H-60); l=rng.integers(3,14)
                arr[y:y+l,x:x+2]=np.clip(arr[y:y+l,x:x+2]+0.5,0,1)
    fr=Image.fromarray((np.clip(arr,0,1)*255).astype(np.uint8))
    if i<BLACK1: fr=chroma_edge(fr)
    if i>=CARD0:
        a=min((i-CARD0)/12.0,1.0)
        l=CARD.copy(); l.putalpha(l.split()[3].point(lambda p:int(p*a)))
        fr.paste(l,(0,0),l)
    return fr

STYLE=[8,30,70,110,150,190,214,240,278,290,306,320,360]
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "style"
    if mode=="style":
        for i in STYLE: render_frame(i).save(f"{OUT}/st_{i:04d}.png")
        print("style frames done:",STYLE)
    else:
        MP4="/home/user/Tik-Tok/build/CONQ_silent.mp4"
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
            "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-c:v","libx264","-profile:v","high",
            "-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",MP4],stdin=subprocess.PIPE)
        for i in range(N):
            ff.stdin.write(render_frame(i).tobytes())
            if i%60==0: print(f"  {i}/{N}",flush=True)
        ff.stdin.close(); ff.wait(); print("done ->",MP4)
