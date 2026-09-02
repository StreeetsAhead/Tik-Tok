"""THE OWL (running gag) - 18.0s, 1080x1920 @30fps.
owl L1 (2.2s) > reason (3.2s) > owl L2 (2.6s) > reason (3.2s) > OWL L3 (3.8s) > outro (3.0s)."""
import sys, os, math, subprocess
sys.path.insert(0,"/home/user/Tik-Tok/build")
from render_promo import *
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
OUT="/home/user/Tik-Tok/build/frames_ow"; os.makedirs(OUT,exist_ok=True)
YEL=(255,214,10); PAPER=(238,240,255)
BEATS=[("owl1",0,88),("r1",88,216),("owl2",216,320),("r2",320,448),("owl3",448,600),("out",600,690)]
TITLE_F=54; N=690+TITLE_F; TIMER_LEN=600
OWLS={k:Image.open(f"{SP}/{k}.png").convert("RGBA") for k in ["owl_l1","owl_l2","owl_l3"]}

def hud(fr,i,dark=False,hide=False):
    if hide: return
    secs=max(0.0,20.0-i/FPS); urgent=secs<5.0
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    pc=RED if urgent else (WHT if dark else INK)
    d.rounded_rectangle([W-64-250,40,W-64,40+92],46,fill=pc+(255,))
    d.rounded_rectangle([0,0,W*(secs/20.0),12],0,fill=(RED if urgent else (WHT if dark else IND))+(255,))
    fr.alpha_composite(L)
    tc=WHT if (urgent or not dark) else INK
    text_layer(fr,f"{secs:04.1f}s",48,850,tc,W-64-125,56)
    text_layer(fr,"EVERYTHING WRONG WITH DUOLINGO",26,800,(200,200,215) if dark else INK,64,60,align="l",ls=3)

def pop_words(fr,words,y,size,color,t0,i,stagger=3,dur=7,cx=W/2,hl=None):
    """kinetic caption: each word pops with overshoot; hl = {word: colour} draws a marker behind it."""
    f=F(size,900); d0=ImageDraw.Draw(Image.new("RGBA",(1,1)))
    ws=[d0.textlength(w,font=f) for w in words]; gap=size*0.28
    total=sum(ws)+gap*(len(words)-1); x=cx-total/2
    for k,(w,ww) in enumerate(zip(words,ws)):
        t=(i-t0-k*stagger)/dur
        if t>0:
            e=min(t,1); s=spring(e) if e<1 else 1.0; a=eo(e)
            L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
            if hl and w in hl:
                mw=ww*eo(min((i-t0-k*stagger-2)/8,1)) if i-t0-k*stagger>2 else 0
                if mw>0: d.rounded_rectangle([x-10,y+size*0.18,x-10+mw+20,y+size*1.02],14,fill=hl[w]+(255,))
            d.text((x,y),w,font=f,fill=color+(255,))
            if s!=1.0:
                cxw,cyw=x+ww/2,y+size/2
                L=L.transform(L.size,Image.AFFINE,(1/s,0,cxw-cxw/s,0,1/s,cyw-cyw/s),resample=Image.BICUBIC)
            L.putalpha(L.split()[3].point(lambda p:int(p*a)))
            fr.alpha_composite(L)
        x+=ww+gap

def chip(fr,label,cx,cy,ang,t0,i,fill=WHT,fg=INK):
    t=(i-t0)/9
    if t<=0: return
    e=min(t,1); s=spring(e) if e<1 else 1.0
    f=F(38,800); tw=ImageDraw.Draw(Image.new("RGBA",(1,1))).textlength(label,font=f)
    cw,ch=int(tw+72),84
    card=Image.new("RGBA",(cw+60,ch+60),(0,0,0,0)); d=ImageDraw.Draw(card)
    d.rounded_rectangle([34,40,34+cw,40+ch],42,fill=(0,0,0,60)); 
    card=card.filter(ImageFilter.GaussianBlur(8)); d=ImageDraw.Draw(card)
    d.rounded_rectangle([30,30,30+cw,30+ch],42,fill=fill+(255,)); d.text((30+36,30+18),label,font=f,fill=fg+(255,))
    card=card.rotate(ang,resample=Image.BICUBIC,expand=True)
    card=card.resize((max(int(card.width*s),1),max(int(card.height*s),1)),Image.BILINEAR)
    card.putalpha(card.split()[3].point(lambda p:int(p*eo(e))))
    fr.alpha_composite(card,(int(cx-card.width/2),int(cy-card.height/2)))

def shake(fr,li,amp=14):
    if li>=5: return fr
    rng=np.random.default_rng(li*7+1); d=(5-li)/5
    dx,dy=int(rng.integers(-amp,amp+1)*d),int(rng.integers(-amp,amp+1)*d); s=1+0.06*d
    fr=fr.transform(fr.size,Image.AFFINE,(1/s,0,W/2-W/2/s-dx,0,1/s,H/2-H/2/s-dy),resample=Image.BILINEAR)
    return fr

# ---------------- beats ----------------
def beat_owl(fr,li,level,total):
    o={1:OWLS["owl_l1"],2:OWLS["owl_l2"],3:OWLS["owl_l3"]}[level]
    rng=np.random.default_rng(li*3+level)
    if level==1:
        sc=0.70*(1+0.06*li/total); jit=(0,0)
        if li%19==0 and li>10: jit=(rng.integers(-2,3),rng.integers(-2,3))
    elif level==2:
        sc=0.96*(1+0.10*li/total); jit=(rng.integers(-3,4),rng.integers(-3,4)) if li%3==0 else (0,0)
    else:
        sc=1.45*(1+0.55*eo(li/total)); jit=(rng.integers(-7,8),rng.integers(-7,8))
    ow=o.resize((int(o.width*sc),int(o.height*sc)),Image.BILINEAR)
    a=ow
    burst = (level==2 and li%30 in (0,1)) or (level==3 and li%8 in (0,1))
    if burst:
        arr=np.asarray(ow).copy()
        for _ in range(4+4*level):
            y0=rng.integers(0,arr.shape[0]-30); hh=rng.integers(4,40); arr[y0:y0+hh]=np.roll(arr[y0:y0+hh],rng.integers(-70,70),axis=1)
        a=Image.fromarray(arr)
    cy=H*0.60 if level<3 else H*0.52
    fr.alpha_composite(a,(int(W/2-a.width/2+jit[0]),int(cy-a.height/2+jit[1])))
    if level>=2:
        pulse=0.7+0.3*math.sin(li*(0.55 if level==2 else 1.1))
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        for ex,ey in [(0.44,0.38),(0.66,0.36)]:
            cx=W/2-a.width/2+jit[0]+ex*a.width; cyy=cy-a.height/2+jit[1]+ey*a.height/(1.062 if level==2 else 1.10)
            r=int(a.width*(0.085 if level==2 else 0.11)*pulse)
            d.ellipse([cx-r,cyy-r,cx+r,cyy+r],fill=(255,30,30,int((80 if level==2 else 140)*pulse)))
        fr.alpha_composite(L.filter(ImageFilter.GaussianBlur(22 if level==2 else 34)))
    if level==1 and li%19==1 and li>10:              # one-frame red eye flicker
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        for ex,ey in [(0.44,0.38),(0.66,0.36)]:
            cx=W/2-a.width/2+ex*a.width; cyy=cy-a.height/2+ey*a.height; r=int(a.width*0.07)
            d.ellipse([cx-r,cyy-r,cx+r,cyy+r],fill=(255,40,40,150))
        fr.alpha_composite(L.filter(ImageFilter.GaussianBlur(10)))

def scene(i):
    for name,a,b in BEATS:
        if a<=i<b: li=i-a; total=b-a; break
    if name=="owl1":
        fr=Image.new("RGBA",(W,H),(226,227,236,255))
        beat_owl(fr,li,1,total)
        slide_text(fr,"01",40,900,RED,64,170,0,li,dur=6,dy=16,align="l",ls=2)
        pop_words(fr,["The","owl."],205,112,INK,2,li,cx=64+230)
        slide_text(fr,"He's just… watching.",44,600,SUB,64,340,10,li,dur=8,align="l")
        hud(fr,i)
    elif name=="owl2":
        fr=Image.new("RGBA",(W,H),(26,22,30,255))
        yy,xx=np.mgrid[0:H,0:W]; vg=np.clip(1-np.sqrt(((xx-W/2)/(W*0.8))**2+((yy-H*0.6)/(H*0.6))**2),0,1)**1.6
        b=np.asarray(fr.convert("RGB")).astype(np.float32); b[...,0]+=vg*55; fr=Image.fromarray(np.clip(b,0,255).astype(np.uint8)).convert("RGBA")
        beat_owl(fr,li,2,total)
        slide_text(fr,"03",40,900,RED,64,170,0,li,dur=6,dy=16,align="l",ls=2)
        pop_words(fr,["The","owl.","Again."],205,104,WHT,1,li,cx=64+330)
        slide_text(fr,"Miss one day. He knows.",44,600,(215,210,225),64,340,8,li,dur=8,align="l")
        hud(fr,i,dark=True)
    elif name=="owl3":
        fr=Image.new("RGBA",(W,H),(4,2,5,255))
        yy,xx=np.mgrid[0:H,0:W]; vg=np.clip(1-np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H*0.55)/(H*0.55))**2),0,1)**1.4
        b=np.asarray(fr.convert("RGB")).astype(np.float32); b[...,0]+=vg*(95+25*math.sin(li*0.9)); fr=Image.fromarray(np.clip(b,0,255).astype(np.uint8)).convert("RGBA")
        beat_owl(fr,li,3,total)
        # strobe
        if li%15==0 and li>4:
            L=Image.new("RGBA",(W,H),(255,220,220,90)); fr.alpha_composite(L)
        rng=np.random.default_rng(li); sx,sy=rng.integers(-6,7),rng.integers(-6,7)
        pop_words(fr,["THE","OWL."],150+sy,150,RED,0,li,stagger=4,dur=6,cx=W/2+sx)
        hud(fr,i,dark=True)
    elif name in ("r1","r2"):
        fr=Image.new("RGBA",(W,H),PAPER+(255,)); c=cards()
        if name=="r1":
            pop_words(fr,["It's","a","game."],200,112,INK,0,li,hl={"game.":YEL})
            slide_text(fr,"their homepage, not my words:",42,600,SUB,W/2,345,8,li,dur=8)
            t=(li-8)/12
            if t>0:
                e=eo(min(t,1)); card,pad=c["tag"]; img=card.rotate(-3*(1-e)-2,resample=Image.BICUBIC,expand=True)
                a=img.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
                fr.alpha_composite(a,(int(W/2-a.width/2),int(H*0.56+80*(1-e)-a.height/2)))
            bt=(li-22)/14
            if bt>0:
                cw=900; chh=int(506*(900/1077)); x0=W/2-cw/2; y0=H*0.56-chh/2
                mx,my=x0+cw*0.640,y0+chh*0.660; rx,ry=cw*0.360,chh*0.430
                L=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(L).arc([mx-rx,my-ry,mx+rx,my+ry],-70,-70+380*eo(min(bt,1)),fill=RED+(255,),width=12); fr.alpha_composite(L)
            chip(fr,"no flashcards",W*0.30,H*0.775,-6,40,li,fill=INK,fg=WHT)
            chip(fr,"ads every lesson",W*0.68,H*0.805,4,48,li,fill=RED,fg=WHT)
            chip(fr,"grammar? guess.",W*0.42,H*0.865,-3,56,li)
        else:
            pop_words(fr,["Half","wrong?"],170,112,INK,0,li)
            pop_words(fr,["You","still","pass."],300,112,INK,6,li,hl={"pass.":GRN})
            def dr(d,card):
                k=min(max((li-16)/26,0),1)
                d.text((60,50),"Answers correct",font=F(34,700),fill=SUB)
                d.text((60,100),f"{int(round(5*k))} / 10",font=F(104,900),fill=RED)
                d.rounded_rectangle([60,262,700,310],24,fill=(232,233,244)); pw=640*min(eo((li-20)/24),1)
                if pw>4: d.rounded_rectangle([60,262,60+pw,310],24,fill=GRN)
                if li>46: d.text((60,336),"SECTION PASSED",font=F(36,900),fill=GRN)
            t=(li-10)/10
            if t>0:
                e=eo(min(t,1)); card=Image.new("RGB",(760,430),WHT); dr(ImageDraw.Draw(card),card)
                wc,pad=with_shadow(card,34,28,60,14); wc=wc.rotate(2*(1-e)+1.5,resample=Image.BICUBIC,expand=True)
                a=wc.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
                fr.alpha_composite(a,(int(W/2-a.width/2),int(H*0.60+70*(1-e)-a.height/2)))
            chip(fr,"hearts run out",W*0.32,H*0.79,5,44,li,fill=RED,fg=WHT)
            chip(fr,"streak guilt",W*0.70,H*0.82,-5,52,li,fill=INK,fg=WHT)
            chip(fr,"plateaus at A2",W*0.45,H*0.88,3,60,li)
        hud(fr,i)
    else:  # outro
        fr=Image.new("RGBA",(W,H),IND+(255,))
        pop_words(fr,["This","is","why","I","created"],H*0.33,74,WHT,2,li,stagger=2)
        pop_words(fr,["verbavia.com"],H*0.33+100,118,WHT,12,li)
        slide_text(fr,"to solve all these problems.",48,600,WHT,W/2,H*0.33+270,20,li)
        bt=(li-30)/12
        if bt>0:
            e=eo(bt); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); bw,bh=470*e,104*e
            d.rounded_rectangle([W/2-bw/2,H*0.66-bh/2,W/2+bw/2,H*0.66+bh/2],int(52*e),fill=(255,255,255,255)); fr.alpha_composite(L)
            if e>0.6: text_layer(fr,"verbavia.com",52,750,IND,W/2,H*0.66-34,alpha=(e-0.6)/0.4)
    return shake(fr,li,amp=18 if name.startswith("owl") else 12), name

def scene_title(li):
    fr=Image.new("RGBA",(W,H),PAPER+(255,))
    pop_words(fr,["This","is"],H*0.30,92,SUB,0,li,stagger=2,dur=6)
    pop_words(fr,["everything","wrong"],H*0.30+110,104,INK,4,li,stagger=3,dur=7,hl={"wrong":YEL})
    pop_words(fr,["with","Duolingo"],H*0.30+230,104,INK,10,li,stagger=3,dur=7)
    pop_words(fr,["in","20","seconds."],H*0.30+350,104,INK,16,li,stagger=3,dur=7,hl={"20":RED})
    text_layer(fr,"EVERYTHING WRONG WITH DUOLINGO",26,800,INK,64,60,align="l",ls=3)
    return shake(fr,li,amp=10),"title"

def render_frame(i):
    if i<TITLE_F: fr,name=scene_title(i)
    else:
        i=i-TITLE_F; fr,name=scene(i)
    if name=="out" and i<600+12:
        t=eo((i-600)/12); prev,_=scene(599); m=Image.new("L",(W,H),0); r=int(t*H*1.25)
        ImageDraw.Draw(m).ellipse([W/2-r,H-r*1.6,W/2+r,H+r*0.4],fill=255); fr=Image.composite(fr,prev,m)
    out=np.asarray(fr.convert("RGB"),dtype=np.float32)/255.0
    g=0.004 if not name.startswith("owl") else (0.012 if name=="owl1" else 0.03)
    out+=np.random.default_rng(i).normal(0,g,out.shape).astype(np.float32)
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))

STYLE=[6,22,44,60,110,180,290,420,520,640,700]
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "style"
    if mode=="style":
        for i in STYLE: render_frame(i).save(f"{OUT}/st_{i:04d}.png")
        print("style done")
    else:
        MP4="/home/user/Tik-Tok/build/OWL_silent.mp4"
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),
            "-i","pipe:0","-c:v","libx264","-profile:v","high","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",MP4],stdin=subprocess.PIPE)
        for i in range(N):
            ff.stdin.write(render_frame(i).tobytes())
            if i%90==0: print(i,flush=True)
        ff.stdin.close(); ff.wait(); print("done ->",MP4)
