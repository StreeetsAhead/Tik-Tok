from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math

SS=3; AW,AH=1080,1350; W,H=AW*SS,AH*SS
def px(v): return int(round(v*SS))
FV="fonts/InterVar.ttf"; _F={}
def F(sz,wt):
    k=(sz,wt)
    if k not in _F:
        f=ImageFont.truetype(FV,px(sz))
        try: f.set_variation_by_axes([32 if sz>=34 else 14, wt])
        except Exception: pass
        _F[k]=f
    return _F[k]

DEEP=(22,18,64); MID=(52,44,152); IND=(99,90,240); LILAC=(186,182,252)
ICON=(59,50,168); ICON2=(134,126,240)
WHT=(255,255,255); GOLD=(247,201,96); DIM=(160,158,208)

# ---- background: deep indigo with a lit top ----
ys,xs=np.mgrid[0:H,0:W]
t=np.clip(ys/H,0,1)[...,None]
bg=np.array(DEEP)*(1-t)+np.array((14,11,44))*t
glow=np.clip(1-np.sqrt(((xs-W*0.5)/(W*0.85))**2+((ys-H*0.05)/(H*0.55))**2),0,1)**1.7
bg=bg+glow[...,None]*np.array([54,46,150])
g2=np.clip(1-np.sqrt(((xs-W*0.18)/(W*0.55))**2+((ys-H*0.88)/(H*0.45))**2),0,1)**2.2
bg=bg+g2[...,None]*np.array([28,22,86])
img=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)); d=ImageDraw.Draw(img)

def text(s,x,y,sz,wt,fill,anchor="l",ls=0):
    f=F(sz,wt); wdt=d.textlength(s,font=f)+ls*(len(s)-1)
    if anchor=="c": x-=wdt/2
    if anchor=="r": x-=wdt
    if ls:
        cx=x
        for ch in s: d.text((cx,y),ch,font=f,fill=fill); cx+=d.textlength(ch,font=f)+ls
    else: d.text((x,y),s,font=f,fill=fill)
    return wdt

# ---- lockup + PREMIUM badge ----
lg=Image.open("verbavia_logo.png").convert("RGBA")
lsz=px(56); lg=lg.resize((lsz,int(lg.height*lsz/lg.width)),Image.LANCZOS)
fw=F(34,800); tw=d.textlength("Verbavia",font=fw)
lx=(W-(lg.width+px(12)+tw))/2
img.paste(lg,(int(lx),px(46)),lg); d.text((lx+lg.width+px(12),px(52)),"Verbavia",font=fw,fill=WHT)
bt="PREMIUM"; fb=F(19,850); bw=d.textlength(bt,font=fb)+px(5)*len(bt)
bx=(W-(bw+px(46)))/2; by=px(120)
d.rounded_rectangle([bx,by,bx+bw+px(46),by+px(46)],px(23),outline=GOLD,width=px(2))
text(bt,W/2,by+px(12),19,850,GOLD,"c",ls=px(5)/SS)

# ---- headline ----
text("No ads. No lost streaks.",W/2,px(196),52,850,WHT,"c")
text("No limit on languages.",W/2,px(264),52,850,LILAC,"c")
text("Everything in the free course, without the friction.",W/2,px(352),23,500,DIM,"c")

# ---- three benefits ----
def icon_noads(cx,cy,s):
    d.rounded_rectangle([cx-s*0.50,cy-s*0.34,cx+s*0.50,cy+s*0.34],px(7),outline=ICON,width=px(4))
    d.rounded_rectangle([cx-s*0.34,cy-s*0.16,cx+s*0.10,cy-s*0.04],px(3),fill=ICON)
    d.rounded_rectangle([cx-s*0.34,cy+s*0.04,cx-s*0.02,cy+s*0.16],px(3),fill=ICON)
    d.line([cx-s*0.62,cy+s*0.52,cx+s*0.62,cy-s*0.52],fill=(214,60,60),width=px(7))
def icon_freeze(cx,cy,s):
    for k in range(6):
        a=math.radians(k*60)
        ex,ey=cx+math.cos(a)*s*0.52, cy+math.sin(a)*s*0.52
        d.line([cx,cy,ex,ey],fill=ICON,width=px(4))
        for f2 in (0.34,0.52):
            bx2,by2=cx+math.cos(a)*s*f2, cy+math.sin(a)*s*f2
            for sgn in (-1,1):
                a2=a+sgn*math.radians(38)
                d.line([bx2,by2,bx2+math.cos(a2)*s*0.17,by2+math.sin(a2)*s*0.17],fill=ICON,width=px(3))
    d.ellipse([cx-s*0.10,cy-s*0.10,cx+s*0.10,cy+s*0.10],fill=(64,158,214))
def icon_multi(cx,cy,s):
    # globe: outline, equator + two latitudes, two meridians
    r=s*0.86; w=px(5)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=ICON,width=w)
    d.line([cx-r,cy,cx+r,cy],fill=ICON,width=w)
    for fy in (0.50,-0.50):
        hy=r*fy; hx=r*0.866
        d.arc([cx-hx,cy+hy-r*0.34,cx+hx,cy+hy+r*0.34],0,180 if fy>0 else 0,fill=ICON,width=w)
        d.line([cx-hx,cy+hy,cx+hx,cy+hy],fill=ICON,width=w)
    for fx in (0.42,):
        d.ellipse([cx-r*fx,cy-r,cx+r*fx,cy+r],outline=ICON,width=w)
    d.line([cx,cy-r,cx,cy+r],fill=ICON,width=w)

ROWS=[("No ads","Nothing between you and the lesson.",icon_noads),
      ("One streak freeze a month","Miss a day. Keep your run.",icon_freeze),
      ("Every language at once","Learn as many as you like, in parallel.",icon_multi)]
RX,RW,RH=px(96),px(888),px(136); y=px(422)
for title,sub,ic in ROWS:
    card=Image.new("RGBA",(RW,RH),(0,0,0,0))
    ImageDraw.Draw(card).rounded_rectangle([0,0,RW-1,RH-1],px(22),fill=(255,255,255,26),
                                           outline=(255,255,255,54),width=px(2))
    img.paste(Image.alpha_composite(img.crop((RX,y,RX+RW,y+RH)).convert("RGBA"),card).convert("RGB"),(RX,y))
    d.rounded_rectangle([RX+px(26),y+px(30),RX+px(26)+px(76),y+px(30)+px(76)],px(20),fill=(255,255,255,30))
    ic(RX+px(26)+px(38), y+px(30)+px(38), px(38))
    text(title,RX+px(128),y+px(34),29,800,WHT,"l")
    text(sub,RX+px(128),y+px(76),21,500,DIM,"l")
    y+=RH+px(20)

# ---- price ----
PY0=px(916)
text("7 DAYS FREE",W/2,PY0,19,850,GOLD,"c",ls=px(4)/SS)
fbig=F(96,900); pw=d.textlength("$4",font=fbig)
fsm=F(26,600); sw=d.textlength(" a month",font=fsm)
px0=(W-(pw+sw))/2
d.text((px0,PY0+px(38)),"$4",font=fbig,fill=WHT)
d.text((px0+pw+px(6),PY0+px(96)),"a month",font=fsm,fill=DIM)
text("after the trial · cancel anytime",W/2,PY0+px(160),20,500,DIM,"c")

# ---- CTA ----
BY=px(1156); BH2=px(92); BW2=px(596); BX=(W-BW2)/2
d.rounded_rectangle([BX,BY+px(7),BX+BW2,BY+BH2+px(7)],BH2//2,fill=(10,8,34))
d.rounded_rectangle([BX,BY,BX+BW2,BY+BH2],BH2//2,fill=WHT)
text("Start 7 days free at verbavia.com",W/2,BY+px(27),27,800,(30,26,90),"c")
text("Free course stays free · web and Android",W/2,px(1284),19,550,DIM,"c")

img.resize((AW,AH),Image.LANCZOS).save("verbavia_premium.png")
print("premium ad saved")
