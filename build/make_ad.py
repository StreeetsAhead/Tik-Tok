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
BG=(247,248,251); INK=(26,30,48); SUB=(107,113,134); MUT=(154,160,178)
IND=(79,70,229); PILL=(233,232,252); CARD=(255,255,255); LINE=(229,231,242)

img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
ys,xs=np.mgrid[0:H,0:W]
g=np.clip(1-np.sqrt(((xs-W*0.5)/(W*0.95))**2+((ys-H*0.08)/(H*0.38))**2),0,1)**1.8
img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)+g[...,None]*np.array([-7,-9,9]),0,255).astype(np.uint8))
d=ImageDraw.Draw(img)

def text(s,x,y,sz,wt,fill,anchor="l",ls=0):
    f=F(sz,wt); wdt=d.textlength(s,font=f)+ls*(len(s)-1)
    if anchor=="c": x-=wdt/2
    if anchor=="r": x-=wdt
    if ls:
        cx=x
        for ch in s: d.text((cx,y),ch,font=f,fill=fill); cx+=d.textlength(ch,font=f)+ls
    else: d.text((x,y),s,font=f,fill=fill)
    return wdt

def shadow_card(x,y,w,h,r):
    sh=Image.new("RGBA",(int(w+px(26)),int(h+px(26))),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle([px(13),px(15),px(13)+w,px(15)+h],r,fill=(20,25,60,30))
    reg=(int(x-px(13)),int(y-px(15)),int(x-px(13))+sh.width,int(y-px(15))+sh.height)
    img.paste(Image.alpha_composite(img.crop(reg).convert("RGBA"),
              sh.filter(ImageFilter.GaussianBlur(px(6)))).convert("RGB"),(reg[0],reg[1]))
    d.rounded_rectangle([x,y,x+w,y+h],r,fill=CARD)

# ---- lockup + badge ----
lg=Image.open("verbavia_logo.png").convert("RGBA")
lsz=px(60); lg=lg.resize((lsz,int(lg.height*lsz/lg.width)),Image.LANCZOS)
fw=F(36,800); tw=d.textlength("Verbavia",font=fw); lx=(W-(lg.width+px(13)+tw))/2
img.paste(lg,(int(lx),px(44)),lg); d.text((lx+lg.width+px(13),px(50)),"Verbavia",font=fw,fill=IND)
bt="8 LANGUAGES · A1 TO C2 · FREE"; fb=F(18,750)
bw=d.textlength(bt,font=fb)+px(3.2)*len(bt); bx=(W-(bw+px(44)))/2; by=px(124)
d.rounded_rectangle([bx,by,bx+bw+px(44),by+px(43)],px(22),fill=PILL)
text(bt,W/2,by+px(11),18,750,IND,"c",ls=px(3.2)/SS)

# ---- headline ----
text("A real course,",W/2,px(190),56,850,INK,"c")
text("not a tapping game.",W/2,px(262),56,850,IND,"c")
text("Every lesson covers all five skills — then you're done for the day.",W/2,px(352),23,500,SUB,"c")

# ---- the five skills (this is the point) ----
SK=[("Vocabulary","vocab"),("Grammar","gram"),("Reading","read"),("Listening","listen"),("Writing","write")]
n=len(SK); CW=px(186); GAP=px(14); CH=px(156); sx=(W-(n*CW+(n-1)*GAP))/2; CY=px(408)
def icon(kind,cx,cy,s):
    c=IND
    if kind=="vocab":
        for k,off in enumerate([px(10),px(4),-px(3)]):
            d.rounded_rectangle([cx-s*0.46+off,cy-s*0.34+off,cx+s*0.40+off,cy+s*0.30+off],px(6),
                                fill=(CARD if k<2 else c), outline=c, width=px(3))
    elif kind=="gram":
        d.rounded_rectangle([cx-s*0.44,cy-s*0.40,cx+s*0.44,cy+s*0.40],px(7),outline=c,width=px(4))
        d.line([cx,cy-s*0.40,cx,cy+s*0.40],fill=c,width=px(4))
        for i in range(3):
            yy=cy-s*0.18+i*s*0.20
            d.line([cx-s*0.32,yy,cx-s*0.08,yy],fill=c,width=px(3))
            d.line([cx+s*0.08,yy,cx+s*0.32,yy],fill=c,width=px(3))
    elif kind=="read":
        d.rounded_rectangle([cx-s*0.44,cy-s*0.40,cx+s*0.44,cy+s*0.40],px(7),outline=c,width=px(4))
        for i,wd in enumerate([0.62,0.74,0.50,0.68]):
            yy=cy-s*0.24+i*s*0.17
            d.line([cx-s*0.30,yy,cx-s*0.30+s*wd*0.78,yy],fill=c,width=px(3))
    elif kind=="listen":
        d.polygon([(cx-s*0.34,cy-s*0.14),(cx-s*0.10,cy-s*0.14),(cx+s*0.12,cy-s*0.40),
                   (cx+s*0.12,cy+s*0.40),(cx-s*0.10,cy+s*0.14),(cx-s*0.34,cy+s*0.14)],fill=c)
        for i,r in enumerate([0.20,0.34]):
            d.arc([cx+s*0.10-s*r,cy-s*r,cx+s*0.10+s*r,cy+s*r],-60,60,fill=c,width=px(4))
    elif kind=="write":
        d.polygon([(cx-s*0.38,cy+s*0.38),(cx-s*0.30,cy+s*0.14),(cx+s*0.26,cy-s*0.42),
                   (cx+s*0.40,cy-s*0.28),(cx-s*0.16,cy+s*0.28)],fill=c)
        d.line([cx-s*0.38,cy+s*0.40,cx+s*0.40,cy+s*0.40],fill=c,width=px(4))
for i,(label,kind) in enumerate(SK):
    x=sx+i*(CW+GAP)
    shadow_card(x,CY,CW,CH,px(18))
    icon(kind,x+CW/2,CY+px(54),px(50))
    text(label,x+CW/2,CY+px(104),19,750,INK,"c")

# ---- what one lesson holds ----
text("WHAT'S IN ONE LESSON",W/2,px(604),17,800,MUT,"c",ls=px(2.4)/SS)
ROWS=["3 reading parts and 3 listening parts",
      "8 new words, most-used first from a frequency list",
      "One grammar point — explained properly, then tested",
      "A writing task, from lesson 7",
      "Around 20–30 minutes, then you're done"]
LX=px(150); y=px(648)
for r in ROWS:
    d.ellipse([LX,y+px(2),LX+px(26),y+px(28)],fill=IND)
    d.line([LX+px(7),y+px(15),LX+px(12),y+px(21)],fill=(255,255,255),width=px(3))
    d.line([LX+px(12),y+px(21),LX+px(20),y+px(9)],fill=(255,255,255),width=px(3))
    text(r,LX+px(44),y,23,600,INK,"l")
    y+=px(50)
text("Complete lessons; shorter options if that's more than your day allows.",W/2,px(906),18,500,MUT,"c")

# ---- languages ----
text("8 courses, one method.",W/2,px(958),25,800,INK,"c")
LIVE=[("spanish","Spanish"),("french","French"),("italian","Italian"),("portuguese","Portuguese"),
      ("german","German"),("mandarin","Mandarin"),("esperanto","Esperanto"),("shanghainese","Shanghainese")]
n2=len(LIVE); CW2=px(106); GAP2=px(10); CH2=px(120); sx2=(W-(n2*CW2+(n2-1)*GAP2))/2; CY2=px(1006)
for i,(key,label) in enumerate(LIVE):
    x=sx2+i*(CW2+GAP2)
    shadow_card(x,CY2,CW2,CH2,px(14))
    fl=Image.open(f"lang/flag_{key}.png").convert("RGB")
    fw2=px(62); fl=fl.resize((fw2,int(fl.height*fw2/fl.width)),Image.LANCZOS)
    fm=Image.new("L",fl.size,0); ImageDraw.Draw(fm).rounded_rectangle([0,0,fl.width-1,fl.height-1],px(5),fill=255)
    img.paste(fl,(int(x+(CW2-fl.width)/2),CY2+px(18)),fm)
    text(label,x+CW2/2,CY2+px(86),13 if len(label)>9 else 15,700,INK,"c")

# ---- CTA ----
BY=px(1180); BH2=px(86); BW2=px(548); BX=(W-BW2)/2
d.rounded_rectangle([BX,BY+px(6),BX+BW2,BY+BH2+px(6)],BH2//2,fill=(120,112,236,70))
d.rounded_rectangle([BX,BY,BX+BW2,BY+BH2],BH2//2,fill=IND)
text("Start free at verbavia.com",W/2,BY+px(23),28,750,(255,255,255),"c")
text("No account needed · web and Android",W/2,px(1290),19,550,MUT,"c")

img.resize((AW,AH),Image.LANCZOS).save("verbavia_ad.png")
print("ad saved")
