"""WHY DUOLINGO DOESN'T WORK - 22.5s infographic promo, 1080x1920 @30fps.
Real screenshots (Playwright captures of duolingo.com and verbavia.com), animated
infographic style in Verbavia's own palette. style/full modes like the others.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os, sys, math, subprocess

SP="/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad"
OUT="/home/user/Tik-Tok/build/frames_pr"; os.makedirs(OUT,exist_ok=True)
W,H,FPS=1080,1920,30; N=675
BG=(247,248,251); INK=(30,34,53); SUB=(107,113,134)
IND=(80,71,229); RED=(229,72,77); GRN=(48,164,108); WHT=(255,255,255)
FV=f"{SP}/fonts/InterVar.ttf"
_F={}
def F(size,wght):
    k=(size,wght)
    if k not in _F:
        f=ImageFont.truetype(FV,size)
        try: f.set_variation_by_axes([32 if size>=54 else 14, wght])
        except Exception: pass
        _F[k]=f
    return _F[k]

def eo(t,p=3.0): t=min(max(t,0),1); return 1-(1-t)**p
def spring(t):
    t=min(max(t,0),1)
    return 1+(-math.exp(-6*t)*math.cos(9*t))*(1-t)*0.9 if t<1 else 1.0

# ---- pre-baked cards -----------------------------------------------------
def rounded(im,rad):
    m=Image.new("L",im.size,0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,im.width-1,im.height-1],rad,fill=255)
    out=im.convert("RGBA"); out.putalpha(m); return out

def with_shadow(im,rad=36,blur=30,alpha=70,dy=14):
    pad=blur*2+dy
    base=Image.new("RGBA",(im.width+pad*2,im.height+pad*2),(0,0,0,0))
    sh=Image.new("RGBA",base.size,(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle([pad,pad+dy,pad+im.width,pad+dy+im.height],rad,
                                         fill=(20,25,50,alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(rounded(im,rad),(pad,pad))
    return base,pad

def load_card(path,target_w,rad=36,border=None):
    im=Image.open(path).convert("RGB")
    s=target_w/im.width
    im=im.resize((target_w,int(im.height*s)),Image.LANCZOS,reducing_gap=3.0)
    if border:
        b=Image.new("RGB",(im.width+border*2,im.height+border*2),WHT)
        b.paste(im,(border,border)); im=b
    return with_shadow(im,rad)

CARDS={}
def cards():
    if CARDS: return CARDS
    CARDS["duo"]  =load_card(f"{SP}/shots/duo_home_m.png",560,rad=44,border=0)
    CARDS["tag"]  =load_card(f"{SP}/shots/duo_tagline.png",900,rad=28,border=26)
    CARDS["vhero"]=load_card(f"{SP}/shots/verb_hero.png",640,rad=32,border=0)
    CARDS["vcmp"] =load_card(f"{SP}/shots/verb_compare.png",760,rad=28,border=20)
    return CARDS

# ---- primitives ----------------------------------------------------------
def text_layer(fr,s,size,wght,color,cx,y,alpha=1.0,align="c",ls=0):
    if alpha<=0: return
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    f=F(size,wght)
    ww=d.textlength(s,font=f)+ls*(len(s)-1)
    x=cx-ww/2 if align=="c" else cx
    if ls:
        for c in s: d.text((x,y),c,font=f,fill=color+(255,)); x+=d.textlength(c,font=f)+ls
    else:
        d.text((x,y),s,font=f,fill=color+(255,))
    if alpha<1: L.putalpha(L.split()[3].point(lambda p:int(p*alpha)))
    fr.alpha_composite(L)

def slide_text(fr,s,size,wght,color,cx,y,t0,i,dur=10,dy=46,**kw):
    t=(i-t0)/dur
    if t<=0: return
    e=eo(t); text_layer(fr,s,size,wght,color,cx,y+dy*(1-e),alpha=e,**kw)

def paste_anim(fr,card,pad,cx,cy,t0,i,dur=14,dy=120,rot0=0.0,scale=1.0):
    t=(i-t0)/dur
    if t<=0: return
    e=eo(t,3.2); sp=spring(min(t,1.0))
    im=card
    if scale!=1.0:
        im=card.resize((int(card.width*scale),int(card.height*scale)),Image.BILINEAR)
    if rot0:
        ang=rot0*(1-e)
        im=im.rotate(ang,resample=Image.BICUBIC,expand=True)
    a=im.copy()
    if e<1: a.putalpha(a.split()[3].point(lambda p:int(p*e)))
    fr.alpha_composite(a,(int(cx-im.width/2),int(cy-im.height/2+dy*(1-e))))

def stroke_path(fr,pts,frac,color,width):
    if frac<=0: return
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    total=sum(math.dist(pts[j],pts[j+1]) for j in range(len(pts)-1)); left=total*min(frac,1)
    for j in range(len(pts)-1):
        seg=math.dist(pts[j],pts[j+1])
        if left<=0: break
        f=min(left/seg,1)
        x0,y0=pts[j]; x1,y1=pts[j+1]
        d.line([x0,y0,x0+(x1-x0)*f,y0+(y1-y0)*f],fill=color+(255,),width=width)
        d.ellipse([x0-width/2,y0-width/2,x0+width/2,y0+width/2],fill=color+(255,))
        ex,ey=x0+(x1-x0)*f,y0+(y1-y0)*f
        d.ellipse([ex-width/2,ey-width/2,ex+width/2,ey+width/2],fill=color+(255,))
        left-=seg
    fr.alpha_composite(L)

def ghost_num(fr,s,cx,cy,t0,i):
    t=(i-t0)/16
    if t<=0: return
    e=eo(t)
    text_layer(fr,s,560,900,(228,229,244),cx,cy-280*0+(-40)*(1-e)-280,alpha=e)

def check_row(fr,label,y,t0,i,cx=150):
    t=(i-t0)/12
    if t<=0: return
    e=eo(t)
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse([cx,y,cx+64,y+64],fill=(255,255,255,40))
    fr.alpha_composite(L)
    stroke_path(fr,[(cx+16,y+34),(cx+28,y+46),(cx+50,y+20)],(i-t0)/10,WHT,7)
    text_layer(fr,label,44,650,WHT,cx+92,y+8,alpha=e,align="l")

# ---- scenes --------------------------------------------------------------
def scene_hook(i):
    fr=Image.new("RGBA",(W,H),BG+(255,))
    c=cards()
    paste_anim(fr,*c["duo"],cx=W*0.50,cy=H*0.635,t0=8,i=i,dur=16,dy=170,rot0=-7)
    slide_text(fr,"Why doesn't",104,800,INK,W/2,H*0.115,2,i)
    slide_text(fr,"Duolingo work?",104,800,INK,W/2,H*0.115+118,7,i)
    ul=(i-24)/10
    if ul>0:
        d=ImageDraw.Draw(fr)
        x0,x1=W*0.284,W*0.284+W*0.435*min(eo(ul),1)
        d.rounded_rectangle([x0,H*0.115+248,x1,H*0.115+262],7,fill=RED+(255,))
    return fr

def scene_r1(i):
    fr=Image.new("RGBA",(W,H),BG+(255,))
    ghost_num(fr,"1",W*0.5,H*0.30,0,i)
    slide_text(fr,"No real flashcards",84,800,INK,W/2,H*0.205,6,i)
    slide_text(fr,"No decks. No spaced repetition.",44,500,SUB,W/2,H*0.205+112,12,i)
    slide_text(fr,"Nothing to review before bed.",44,500,SUB,W/2,H*0.205+170,16,i)
    # three fanned blank cards, then a struck X
    ct=(i-18)/14
    if ct>0:
        e=eo(ct)
        for j,(dx,ang) in enumerate([(-215,-10),(0,0),(215,10)]):
            cw,ch=380,520
            card=Image.new("RGB",(cw,ch),WHT)
            dd=ImageDraw.Draw(card)
            dd.rounded_rectangle([24,ch-160,cw-24,ch-120],10,fill=(238,239,246))
            dd.rounded_rectangle([24,ch-100,cw*0.62,ch-60],10,fill=(238,239,246))
            dd.ellipse([cw/2-70,90,cw/2+70,230],outline=(228,229,240),width=8)
            wc,pad=with_shadow(card,26,22,50,10)
            a=wc.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
            ii=a.rotate(ang*e,resample=Image.BICUBIC,expand=True)
            fr.alpha_composite(ii,(int(W/2+dx*e-ii.width/2),int(H*0.60+70*(1-e)-ii.height/2)))
    stroke_path(fr,[(W*0.30,H*0.505),(W*0.70,H*0.695)],(i-44)/9,RED,26)
    stroke_path(fr,[(W*0.70,H*0.505),(W*0.30,H*0.695)],(i-52)/9,RED,26)
    return fr

def scene_r2(i):
    fr=Image.new("RGBA",(W,H),BG+(255,))
    ghost_num(fr,"2",W*0.5,H*0.30,0,i)
    slide_text(fr,"Lessons never get serious",76,800,INK,W/2,H*0.205,6,i)
    slide_text(fr,"Don't take my word for it —",44,500,SUB,W/2,H*0.205+104,12,i)
    slide_text(fr,"this is their homepage:",44,500,SUB,W/2,H*0.205+162,15,i)
    c=cards()
    paste_anim(fr,*c["tag"],cx=W/2,cy=H*0.565,t0=20,i=i,dur=14,dy=90)
    # red box draws around "chess, and more!" inside the tagline card
    bt=(i-42)/14
    if bt>0:
        e=min(bt,1.0)
        cw=900; chh=int(506*(900/1077))
        x0=W/2-cw/2; y0=H*0.565-chh/2
        mx,my=x0+cw*0.640,y0+chh*0.660
        rx,ry=cw*0.360,chh*0.430
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        start=-70
        d.arc([mx-rx,my-ry,mx+rx,my+ry],start,start+380*eo(e),fill=RED+(255,),width=10)
        fr.alpha_composite(L)
    slide_text(fr,'"...chess, and more!"',56,700,RED,W/2,H*0.72,58,i)
    slide_text(fr,"A serious course this is not.",44,500,SUB,W/2,H*0.72+84,70,i)
    return fr

def scene_r3(i):
    fr=Image.new("RGBA",(W,H),BG+(255,))
    ghost_num(fr,"3",W*0.5,H*0.30,0,i)
    slide_text(fr,"The bar is on the floor",80,800,INK,W/2,H*0.205,6,i)
    slide_text(fr,"Get half of it wrong —",44,500,SUB,W/2,H*0.205+108,12,i)
    slide_text(fr,"you still move on.",44,500,SUB,W/2,H*0.205+166,15,i)
    ct=(i-20)/12
    if ct>0:
        e=eo(ct)
        cw,ch=760,420
        card=Image.new("RGB",(cw,ch),WHT); d=ImageDraw.Draw(card)
        # score counter
        k=min(max((i-30)/34,0),1)
        d.text((60,54),"Answers correct",font=F(34,600),fill=SUB)
        d.text((60,108),f"{int(round(5*k))} / 10",font=F(96,850),fill=RED)
        # progress pill
        d.rounded_rectangle([60,262,cw-60,306],22,fill=(238,239,246))
        pw=(cw-120)*min(eo((i-36)/26),1)
        if pw>4: d.rounded_rectangle([60,262,60+pw,306],22,fill=GRN)
        if i>66: d.text((60,330),"SECTION PASSED",font=F(34,800),fill=GRN)
        wc,pad=with_shadow(card,30,26,55,12)
        a=wc.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
        fr.alpha_composite(a,(int(W/2-a.width/2),int(H*0.575+70*(1-e)-a.height/2)))
    if i>70:
        stroke_path(fr,[(W*0.685,H*0.633),(W*0.703,H*0.648),(W*0.735,H*0.612)],(i-70)/10,GRN,9)
    slide_text(fr,"Green screens. No learning.",44,500,SUB,W/2,H*0.76,84,i)
    return fr

def scene_turn(i):
    fr=Image.new("RGBA",(W,H),IND+(255,))
    c=cards()
    slide_text(fr,"So I built Verbavia.",84,800,WHT,W/2,H*0.088,8,i)
    paste_anim(fr,*c["vhero"],cx=W*0.262,cy=H*0.335,t0=22,i=i,dur=16,dy=140,rot0=-5,scale=0.72)
    paste_anim(fr,*c["vcmp"],cx=W*0.685,cy=H*0.375,t0=32,i=i,dur=16,dy=140,rot0=4,scale=0.80)
    y0=H*0.600
    check_row(fr,"Real flashcard decks",y0,66,i)
    check_row(fr,"Serious, structured lessons",y0+96,76,i)
    check_row(fr,"A bar you actually have to clear",y0+192,86,i)
    slide_text(fr,"This is why I created verbavia.com —",46,600,WHT,W/2,H*0.812,104,i)
    slide_text(fr,"it solves every single one of these problems.",46,600,WHT,W/2,H*0.812+62,110,i)
    bt=(i-126)/12
    if bt>0:
        e=eo(bt)
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        bw,bh=470*e,104*e
        d.rounded_rectangle([W/2-bw/2,H*0.930-bh/2,W/2+bw/2,H*0.930+bh/2],int(52*e),fill=(255,255,255,255))
        fr.alpha_composite(L)
        if e>0.6: text_layer(fr,"verbavia.com",52,750,IND,W/2,H*0.930-34,alpha=(e-0.6)/0.4)
    return fr

SCENES=[(0,90,scene_hook),(90,225,scene_r1),(225,360,scene_r2),(360,495,scene_r3),(495,675,scene_turn)]
WIPE=495

def render_frame(i):
    for (a,b,fn) in SCENES:
        if a<=i<b: fr=fn(i-a); break
    # indigo circle wipe into the turn
    if WIPE-0<=i<WIPE+14 and i>=WIPE:
        t=eo((i-WIPE)/14)
        prev=SCENES[3][2](i-360) if i-360<200 else None
        if prev is not None and t<1:
            m=Image.new("L",(W,H),0)
            r=int(t*H*1.25)
            ImageDraw.Draw(m).ellipse([W/2-r,H-r*1.6,W/2+r,H+r*0.4],fill=255)
            prev=prev.convert("RGBA"); fr=Image.composite(fr,prev,m)
    out=np.asarray(fr.convert("RGB"),dtype=np.float32)/255.0
    rng=np.random.default_rng(i)
    out+=rng.normal(0,0.0045,out.shape).astype(np.float32)
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))

STYLE=[12,40,80,110,150,200,250,290,330,380,430,470,500,530,570,620,665]
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "style"
    if mode=="style":
        for i in STYLE: render_frame(i).save(f"{OUT}/st_{i:04d}.png")
        print("style done",STYLE)
    else:
        MP4="/home/user/Tik-Tok/build/PROMO_silent.mp4"
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
            "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-c:v","libx264","-profile:v","high",
            "-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",MP4],stdin=subprocess.PIPE)
        for i in range(N):
            ff.stdin.write(render_frame(i).tobytes())
            if i%90==0: print(i,flush=True)
        ff.stdin.close(); ff.wait(); print("done ->",MP4)
