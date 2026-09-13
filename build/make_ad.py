from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

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
IND=(79,70,229); IND_SOFT=(199,203,245); PILLBG=(233,232,252); CARD=(255,255,255)

img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
ys,xs=np.mgrid[0:H,0:W]
g=np.clip(1-np.sqrt(((xs-W*0.5)/(W*0.95))**2+((ys-H*0.09)/(H*0.40))**2),0,1)**1.8
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

# lockup
lg=Image.open("verbavia_logo.png").convert("RGBA")
lsz=px(64); lg=lg.resize((lsz,int(lg.height*lsz/lg.width)),Image.LANCZOS)
fw=F(38,800); tw=d.textlength("Verbavia",font=fw)
lx=(W-(lg.width+px(14)+tw))/2
img.paste(lg,(int(lx),px(48)),lg); d.text((lx+lg.width+px(14),px(54)),"Verbavia",font=fw,fill=IND)

# badge
bt="8 LANGUAGES · A1 TO C2 · FREE"; fb=F(19,750); bw=d.textlength(bt,font=fb)+px(10)*7
bx=(W-(bw+px(48)))/2; by=px(136)
d.rounded_rectangle([bx,by,bx+bw+px(48),by+px(46)],px(23),fill=PILLBG)
text(bt,W/2,by+px(12),19,750,IND,"c",ls=px(3.4)/SS)

# headline (site's own words)
text("Learn the words people actually use,",W/2,px(214),47,850,INK,"c")
text("in the order they use them.",W/2,px(278),47,850,IND,"c")
text("Every course is built on a frequency list. The thousand most",W/2,px(360),24,500,SUB,"c")
text("common words are about 80% of everyday speech — so that is",W/2,px(394),24,500,SUB,"c")
text("where lesson one starts.",W/2,px(428),24,500,SUB,"c")

# ---- the chart: single measure, one hue, focus row emphasised, direct labels ----
text("HOW MUCH OF EVERYDAY SPEECH YOUR FIRST WORDS COVER",W/2,px(498),17,800,MUT,"c",ls=px(2.2)/SS)
X0,X1=px(118),px(962); BARH=px(46)
rows=[("Your first 100 words",0.50,"about half",False),
      ("Your first 1,000 words",0.80,"about 80%",True),
      ("Your first 3,000 words",0.90,"about 90%",False)]
y=px(548)
for label,frac,val,focus in rows:
    text(label,X0,y,21,700,INK if focus else SUB,"l")
    by2=y+px(30)
    d.rounded_rectangle([X0,by2,X1,by2+BARH],px(6),fill=(234,236,246))
    bw2=(X1-X0)*frac
    d.rounded_rectangle([X0,by2,X0+bw2,by2+BARH],px(6),fill=IND if focus else IND_SOFT)
    text(val,X0+bw2-px(16),by2+px(10),26,800,(255,255,255) if focus else (90,96,140),"r")
    y+=px(116)
text("Typical figures for conversation; the exact share varies by language.",W/2,px(898),18,500,MUT,"c")

# languages
text("8 courses, one method.",W/2,px(952),27,800,INK,"c")
LIVE=[("spanish","Spanish"),("french","French"),("italian","Italian"),("portuguese","Portuguese"),
      ("german","German"),("mandarin","Mandarin"),("esperanto","Esperanto"),("shanghainese","Shanghainese")]
n=len(LIVE); CW=px(108); GAP=px(10); CH=px(128)
sx=(W-(n*CW+(n-1)*GAP))/2; CY=px(1004)
for i,(key,label) in enumerate(LIVE):
    x=sx+i*(CW+GAP)
    sh=Image.new("RGBA",(CW+px(24),CH+px(24)),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle([px(12),px(14),px(12)+CW,px(14)+CH],px(14),fill=(20,25,60,30))
    reg=(int(x-px(12)),CY-px(14),int(x-px(12))+sh.width,CY-px(14)+sh.height)
    img.paste(Image.alpha_composite(img.crop(reg).convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(px(5)))).convert("RGB"),(reg[0],reg[1]))
    d.rounded_rectangle([x,CY,x+CW,CY+CH],px(14),fill=CARD)
    fl=Image.open(f"lang/flag_{key}.png").convert("RGB")
    fw2=px(64); fl=fl.resize((fw2,int(fl.height*fw2/fl.width)),Image.LANCZOS)
    fm=Image.new("L",fl.size,0); ImageDraw.Draw(fm).rounded_rectangle([0,0,fl.width-1,fl.height-1],px(5),fill=255)
    img.paste(fl,(int(x+(CW-fl.width)/2),CY+px(20)),fm)
    text(label,x+CW/2,CY+px(92),14 if len(label)>9 else 16,700,INK,"c")

# CTA
BY=px(1188); BH2=px(88); BW2=px(556); BX=(W-BW2)/2
d.rounded_rectangle([BX,BY+px(6),BX+BW2,BY+BH2+px(6)],BH2//2,fill=(120,112,236,70))
d.rounded_rectangle([BX,BY,BX+BW2,BY+BH2],BH2//2,fill=IND)
text("Start free at verbavia.com",W/2,BY+px(24),29,750,(255,255,255),"c")
text("No account needed · web and Android",W/2,px(1298),20,550,MUT,"c")

img.resize((AW,AH),Image.LANCZOS).save("verbavia_ad.png")
print("ad saved")
