"""EVERYTHING WRONG WITH DUOLINGO IN 20 SECONDS - 23.0s, 1080x1920 @30fps.
Nine reasons at 2.2s each under a draining 20s timer; 3s Verbavia outro."""
import sys, os, math, subprocess
sys.path.insert(0, "/home/user/Tik-Tok/build")
from render_promo import *          # W,H,FPS,BG,INK,SUB,IND,RED,GRN,WHT,F,eo,spring,with_shadow,cards,text_layer,slide_text,paste_anim,stroke_path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
OUT="/home/user/Tik-Tok/build/frames_fs"; os.makedirs(OUT,exist_ok=True)
N=690; REASON_F=66; TIMER_END=600; ORG=(242,122,32); GREY=(214,216,226)
OWL=Image.open(f"{SP}/owl_horror.png").convert("RGBA")

def hud(fr,i,dark=False):
    """eyebrow + countdown pill + draining bar."""
    col_txt=WHT if dark else INK; col_sub=(200,200,215) if dark else SUB
    text_layer(fr,"EVERYTHING WRONG WITH DUOLINGO",26,700,col_sub,64,58,align="l",ls=3)
    secs=max(0.0,20.0-i/FPS)
    urgent=secs<5.0
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    pc=RED if urgent else (IND if not dark else WHT)
    d.rounded_rectangle([W-64-232,40,W-64,40+84],42,fill=pc+(255,))
    d.rounded_rectangle([0,0,W*(secs/20.0),10],0,fill=(RED if urgent else IND)+(255,))
    fr.alpha_composite(L)
    tcol=WHT if (urgent or not dark) else IND
    text_layer(fr,f"{secs:04.1f}s",44,800,tcol,W-64-116,52+2)

def reason_head(fr,n,title,sub,i,dark=False):
    c1=WHT if dark else INK; c2=(210,205,225) if dark else SUB
    slide_text(fr,f"{n:02d}",34,800,RED,64,168,0,i,dur=7,dy=20,align="l",ls=2)
    slide_text(fr,title,88,800,c1,64,214,2,i,dur=8,dy=40,align="l")
    if sub: slide_text(fr,sub,42,500,c2,64,214+112,6,i,dur=8,dy=30,align="l")

def card_widget(fr,draw_fn,cw,ch,cy,t0,i,dur=10):
    t=(i-t0)/dur
    if t<=0: return
    e=eo(t); card=Image.new("RGB",(cw,ch),WHT); draw_fn(ImageDraw.Draw(card),card)
    wc,pad=with_shadow(card,30,26,55,12)
    a=wc.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
    fr.alpha_composite(a,(int(W/2-a.width/2),int(cy+60*(1-e)-a.height/2)))

def heart(d,cx,cy,s,fill):
    d.ellipse([cx-s,cy-s*0.9,cx,cy+s*0.1],fill=fill); d.ellipse([cx,cy-s*0.9,cx+s,cy+s*0.1],fill=fill)
    d.polygon([(cx-s*0.98,cy-s*0.15),(cx+s*0.98,cy-s*0.15),(cx,cy+s*1.0)],fill=fill)

# ---------------- reasons ----------------
def r_flash(fr,i):
    reason_head(fr,1,"No flashcards.","No decks. No spaced repetition.",i)
    ct=(i-8)/10
    if ct>0:
        e=eo(ct)
        for dx,ang in [(-215,-10),(0,0),(215,10)]:
            card=Image.new("RGB",(380,520),WHT); dd=ImageDraw.Draw(card)
            dd.rounded_rectangle([24,360,356,400],10,fill=(238,239,246)); dd.rounded_rectangle([24,420,235,460],10,fill=(238,239,246))
            dd.ellipse([120,90,260,230],outline=(228,229,240),width=8)
            wc,pad=with_shadow(card,26,22,50,10); a=wc.copy(); a.putalpha(a.split()[3].point(lambda p:int(p*e)))
            ii=a.rotate(ang*e,resample=Image.BICUBIC,expand=True)
            fr.alpha_composite(ii,(int(W/2+dx*e-ii.width/2),int(H*0.64+70*(1-e)-ii.height/2)))
    stroke_path(fr,[(W*0.30,H*0.545),(W*0.70,H*0.735)],(i-26)/7,RED,26)
    stroke_path(fr,[(W*0.70,H*0.545),(W*0.30,H*0.735)],(i-32)/7,RED,26)

def r_game(fr,i):
    reason_head(fr,2,"It's a game.","Their homepage, not mine:",i)
    c=cards(); paste_anim(fr,*c["tag"],cx=W/2,cy=H*0.62,t0=8,i=i,dur=10,dy=70)
    bt=(i-22)/12
    if bt>0:
        cw=900; chh=int(506*(900/1077)); x0=W/2-cw/2; y0=H*0.62-chh/2
        mx,my=x0+cw*0.640,y0+chh*0.660; rx,ry=cw*0.360,chh*0.430
        L=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(L).arc([mx-rx,my-ry,mx+rx,my+ry],-70,-70+380*eo(min(bt,1)),fill=RED+(255,),width=10)
        fr.alpha_composite(L)

def r_bar(fr,i):
    reason_head(fr,3,"Half wrong? You pass.",None,i)
    def dr(d,card):
        k=min(max((i-14)/26,0),1)
        d.text((60,54),"Answers correct",font=F(34,600),fill=SUB)
        d.text((60,108),f"{int(round(5*k))} / 10",font=F(96,850),fill=RED)
        d.rounded_rectangle([60,262,700,306],22,fill=(238,239,246))
        pw=640*min(eo((i-18)/24),1)
        if pw>4: d.rounded_rectangle([60,262,60+pw,306],22,fill=GRN)
        if i>44: d.text((60,330),"SECTION PASSED",font=F(34,800),fill=GRN)
    card_widget(fr,dr,760,420,H*0.62,8,i)
    if i>46: stroke_path(fr,[(W*0.685,H*0.665),(W*0.703,H*0.680),(W*0.735,H*0.644)],(i-46)/8,GRN,9)

def r_streak(fr,i):
    reason_head(fr,4,"Streaks over skills.",None,i)
    def dr(d,card):
        k=min(max((i-12)/30,0),1)
        d.text((60,50),"Streak",font=F(34,600),fill=SUB)
        d.text((60,96),f"{int(412*eo(k))} days",font=F(72,850),fill=ORG)
        d.rounded_rectangle([60,190,700,224],17,fill=(238,239,246)); d.rounded_rectangle([60,190,60+640*eo(k),224],17,fill=ORG)
        d.text((60,262),"Can order a coffee",font=F(34,600),fill=SUB)
        d.text((60,306),"—",font=F(72,850),fill=GREY)
        d.rounded_rectangle([60,400,700,434],17,fill=(238,239,246))
    card_widget(fr,dr,760,480,H*0.62,6,i)

def r_hearts(fr,i):
    reason_head(fr,5,"Hearts.","Run out of mistakes, run out of learning.",i)
    def dr(d,card):
        for j in range(5):
            lost = i > 18+j*7
            heart(d,110+j*135,150,52,GREY if lost else RED)
        if i>52: d.text((60,250),"Out of hearts. Try again tomorrow.",font=F(36,700),fill=INK)
    card_widget(fr,dr,760,330,H*0.62,6,i)

def r_ads(fr,i):
    reason_head(fr,6,"Ads.","After every lesson, on free.",i)
    def dr(d,card):
        d.rounded_rectangle([0,0,759,419],30,fill=(28,30,40))
        d.rounded_rectangle([36,36,116,80],10,fill=(255,204,0)); d.text((52,42),"AD",font=F(30,900),fill=(28,30,40))
        d.polygon([(340,150),(340,290),(460,220)],fill=WHT)
        n=max(1,5-int((i-10)/9)); d.text((520,352),f"Skip in {n}",font=F(32,600),fill=(200,200,215))
    card_widget(fr,dr,760,420,H*0.62,6,i)

def r_grammar(fr,i):
    reason_head(fr,7,"Grammar? Guess.","Rules are never explained.",i)
    def dr(d,card):
        d.text((60,60),"Ella come manzanas.",font=F(60,700),fill=INK)
        d.text((60,140),"She eats apples.",font=F(36,500),fill=SUB)
        if i>18:
            d.text((60,230),"Why 'come' and not 'como'?",font=F(36,600),fill=INK)
            d.text((60,282),"(no explanation given)",font=F(34,500),fill=RED)
    card_widget(fr,dr,760,360,H*0.60,6,i)
    slide_text(fr,"?",300,900,(232,233,244),W*0.80,H*0.30,10,i,dur=12,dy=40)

def r_plateau(fr,i):
    reason_head(fr,8,"Plateau at A2.","Then it just... stops.",i)
    def dr(d,card):
        d.line([(60,330),(700,330)],fill=(238,239,246),width=3)
        d.line([(60,80),(700,80)],fill=(238,239,246),width=3)
        d.text((610,44),"C2",font=F(28,700),fill=SUB); d.text((610,338),"A1",font=F(28,700),fill=SUB)
        k=min(max((i-10)/40,0),1)
        pts=[]
        for s in range(0,int(60*k)+1):
            x=60+s/60*640; y=330-min(s/22,1)**0.8*150 if s<22 else 330-150
            pts.append((x,y))
        if len(pts)>1: d.line(pts,fill=IND,width=10,joint="curve")
        if k>0.5: d.text((330,150),"A2",font=F(40,800),fill=IND)
    card_widget(fr,dr,760,400,H*0.62,6,i)

def r_owl(fr,i):
    reason_head(fr,9,"The owl.","Miss one day. He remembers.",i,dark=True)
    rng=np.random.default_rng(i)
    sc=0.98+0.10*eo(i/66); ow=OWL.resize((int(OWL.width*sc*0.82),int(OWL.height*sc*0.82)),Image.BILINEAR)
    jx,jy=(rng.integers(-3,4),rng.integers(-3,4)) if i%2==0 else (0,0)
    pulse=0.75+0.25*math.sin(i*0.55)
    a=ow.copy()
    if i%23 in (0,1):                              # glitch burst
        arr=np.asarray(a).copy()
        for _ in range(6):
            y0=rng.integers(0,arr.shape[0]-30); hh=rng.integers(4,30); arr[y0:y0+hh]=np.roll(arr[y0:y0+hh],rng.integers(-60,60),axis=1)
        a=Image.fromarray(arr)
    fr.alpha_composite(a,(int(W/2-a.width/2+jx),int(H*0.60-a.height/2+jy)))
    # red eye pulse overlay
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for ex,ey in [(0.44,0.38),(0.66,0.36)]:
        cx=W/2-a.width/2+jx+ex*a.width; cy=H*0.60-a.height/2+jy+ey*a.height/1.08
        r=int(a.width*0.085*pulse)
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,30,30,int(90*pulse)))
    fr.alpha_composite(L.filter(ImageFilter.GaussianBlur(18)))

REASONS=[r_flash,r_game,r_bar,r_streak,r_hearts,r_ads,r_grammar,r_plateau,r_owl]

def scene_out(i):
    fr=Image.new("RGBA",(W,H),IND+(255,))
    slide_text(fr,"That's why I created",70,700,WHT,W/2,H*0.36,2,i)
    slide_text(fr,"verbavia.com",110,850,WHT,W/2,H*0.36+90,5,i)
    slide_text(fr,"a site which solves all these problems.",46,600,WHT,W/2,H*0.36+250,12,i)
    bt=(i-24)/12
    if bt>0:
        e=eo(bt); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        bw,bh=470*e,104*e
        d.rounded_rectangle([W/2-bw/2,H*0.66-bh/2,W/2+bw/2,H*0.66+bh/2],int(52*e),fill=(255,255,255,255))
        fr.alpha_composite(L)
        if e>0.6: text_layer(fr,"verbavia.com",52,750,IND,W/2,H*0.66-34,alpha=(e-0.6)/0.4)
    return fr

def render_frame(i):
    if i>=TIMER_END:
        fr=scene_out(i-TIMER_END)
        if i<TIMER_END+12:
            t=eo((i-TIMER_END)/12); prev=render_reason(TIMER_END-1)
            m=Image.new("L",(W,H),0); r=int(t*H*1.25)
            ImageDraw.Draw(m).ellipse([W/2-r,H-r*1.6,W/2+r,H+r*0.4],fill=255)
            fr=Image.composite(fr,prev,m)
    else:
        fr=render_reason(i)
    out=np.asarray(fr.convert("RGB"),dtype=np.float32)/255.0
    out+=np.random.default_rng(i).normal(0,0.0045 if i//REASON_F!=8 else 0.02,out.shape).astype(np.float32)
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))

def render_reason(i):
    k=min(i//REASON_F,8); li=i-k*REASON_F
    dark=(k==8)
    if dark:
        fr=Image.new("RGBA",(W,H),(6,4,7,255))
        yy,xx=np.mgrid[0:H,0:W]; vg=np.clip(1-np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H*0.6)/(H*0.55))**2),0,1)**1.6
        b=np.asarray(fr.convert("RGB")).astype(np.float32); b[...,0]+=vg*80; b[...,2]+=vg*8
        fr=Image.fromarray(np.clip(b,0,255).astype(np.uint8)).convert("RGBA")
    else:
        fr=Image.new("RGBA",(W,H),BG+(255,))
    REASONS[k](fr,li)
    hud(fr,i,dark)
    return fr

STYLE=[20,60,100,150,215,260,330,400,460,520,545,580,615,660]
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "style"
    if mode=="style":
        for i in STYLE: render_frame(i).save(f"{OUT}/st_{i:04d}.png")
        print("style done")
    else:
        MP4="/home/user/Tik-Tok/build/FAST_silent.mp4"
        ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
            "-r",str(FPS),"-i","pipe:0","-c:v","libx264","-profile:v","high","-crf","17","-pix_fmt","yuv420p",
            "-movflags","+faststart",MP4],stdin=subprocess.PIPE)
        for i in range(N):
            ff.stdin.write(render_frame(i).tobytes())
            if i%90==0: print(i,flush=True)
        ff.stdin.close(); ff.wait(); print("done ->",MP4)
