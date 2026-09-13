from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math

SS=3; AW,AH=1080,1350; W,H=AW*SS,AH*SS
def px(v): return int(round(v*SS))
FV="fonts/InterVar.ttf"
_F={}
def F(sz,wt):
    k=(sz,wt)
    if k not in _F:
        f=ImageFont.truetype(FV, px(sz))
        try: f.set_variation_by_axes([32 if sz>=34 else 14, wt])
        except Exception: pass
        _F[k]=f
    return _F[k]

BG=(247,248,251); INK=(26,30,48); SUB=(107,113,134); MUT=(150,156,176)
IND=(79,70,229); IND_D=(62,54,196); TRACK=(228,230,242); CARD=(255,255,255)

img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)

# soft indigo wash behind the headline
ys,xs=np.mgrid[0:H,0:W]
g=np.clip(1-np.sqrt(((xs-W*0.5)/(W*0.95))**2+((ys-H*0.10)/(H*0.42))**2),0,1)**1.8
base=np.asarray(img).astype(np.float32)
base=base+g[...,None]*np.array([-6,-8,10])*1.0
img=Image.fromarray(np.clip(base,0,255).astype(np.uint8)); d=ImageDraw.Draw(img)

def text(s,x,y,sz,wt,fill,anchor="l",ls=0):
    f=F(sz,wt)
    wdt=d.textlength(s,font=f)+ls*(len(s)-1)
    if anchor=="c": x=x-wdt/2
    if anchor=="r": x=x-wdt
    if ls:
        cx=x
        for ch in s: d.text((cx,y),ch,font=f,fill=fill); cx+=d.textlength(ch,font=f)+ls
    else: d.text((x,y),s,font=f,fill=fill)
    return wdt

# ---------------- lockup ----------------
lg=Image.open("verbavia_logo.png").convert("RGBA")
lsz=px(70); lg=lg.resize((lsz,int(lg.height*lsz/lg.width)), Image.LANCZOS)
wm="Verbavia"; fw=F(40,800)
tw=d.textlength(wm,font=fw)
tot=lg.width+px(14)+tw; lx=(W-tot)/2
img.paste(lg,(int(lx),px(52)),lg)
d.text((lx+lg.width+px(16), px(62)), wm, font=fw, fill=IND)

# ---------------- headline ----------------
text("Learn a language,", W/2, px(168), 74, 850, INK, "c")
text("actually get fluent.", W/2, px(256), 74, 850, IND, "c")
text("One real lesson a day — from your first word to C2.", W/2, px(362), 27, 500, SUB, "c")

# ---------------- CEFR meter: one hue, recessive track, one annotation ----------------
MX0,MX1,MY = px(120), px(960), px(492)
BARH=px(26)
d.rounded_rectangle([MX0,MY,MX1,MY+BARH], BARH//2, fill=TRACK)
d.rounded_rectangle([MX0,MY,MX1,MY+BARH], BARH//2, fill=IND)
levels=["A1","A2","B1","B2","C1","C2"]
for i,lv in enumerate(levels):
    x=MX0+(MX1-MX0)*i/(len(levels)-1)
    text(lv, x, MY+BARH+px(18), 23, 700, INK if i==len(levels)-1 else SUB, "c")
# reference marker where most apps stop
ax=MX0+(MX1-MX0)*(1/5)
d.rectangle([ax-px(1.5),MY-px(26),ax+px(1.5),MY+BARH+px(4)], fill=(255,255,255))
d.rectangle([ax-px(1),MY-px(24),ax+px(1),MY+BARH+px(2)], fill=MUT)
text("most apps plateau here", ax+px(12), MY-px(34), 21, 600, MUT, "l")
text("Verbavia runs the whole way", MX1, MY-px(34), 21, 700, IND, "r")

# ---------------- language strip ----------------
text("15 languages", W/2, px(610), 30, 800, INK, "c")
text("including seven Pacific languages most apps ignore", W/2, px(652), 25, 500, SUB, "c")

PACIFIC=[("tokpisin","Tok Pisin"),("samoan","Samoan"),("fijian","Fijian"),("marshallese","Marshallese"),
         ("kiribati","Kiribati"),("palauan","Palauan"),("rapanui","Rapa Nui")]
n=len(PACIFIC); CW=px(124); GAP=px(14)
total=n*CW+(n-1)*GAP; sx=(W-total)/2; CY=px(714); CH=px(150)
for i,(key,label) in enumerate(PACIFIC):
    x=sx+i*(CW+GAP)
    card=Image.new("RGBA",(CW+px(20),CH+px(20)),(0,0,0,0))
    ImageDraw.Draw(card).rounded_rectangle([px(10),px(12),px(10)+CW,px(12)+CH],px(16),fill=(20,25,60,34))
    img.paste(Image.alpha_composite(img.crop((int(x-px(10)),CY-px(12),int(x-px(10))+card.width,CY-px(12)+card.height)).convert("RGBA"),
              card.filter(ImageFilter.GaussianBlur(px(5)))).convert("RGB"), (int(x-px(10)),CY-px(12)))
    d.rounded_rectangle([x,CY,x+CW,CY+CH], px(16), fill=CARD)
    fl=Image.open(f"lang/flag_{key}.png").convert("RGB")
    fw2=px(74); fl=fl.resize((fw2,int(fl.height*fw2/fl.width)), Image.LANCZOS)
    fm=Image.new("L",fl.size,0); ImageDraw.Draw(fm).rounded_rectangle([0,0,fl.width-1,fl.height-1],px(6),fill=255)
    img.paste(fl,(int(x+(CW-fl.width)/2), CY+px(22)), fm)
    text(label, x+CW/2, CY+px(104), 17, 700, INK, "c")

# ---------------- proof points ----------------
PROOF=[("Real flashcard decks","spaced repetition, not guessing"),
       ("A 300-lesson syllabus","structured A1 through C2"),
       ("Grammar explained","the rule first, then the test")]
PY0=px(924)
for i,(h,sb) in enumerate(PROOF):
    y=PY0+i*px(84)
    d.ellipse([px(126),y+px(4),px(126)+px(30),y+px(34)], fill=IND)
    d.line([px(134),y+px(19),px(140),y+px(26)], fill=(255,255,255), width=px(3))
    d.line([px(140),y+px(26),px(150),y+px(12)], fill=(255,255,255), width=px(3))
    text(h, px(176), y, 27, 750, INK, "l")
    text(sb, px(176), y+px(34), 22, 500, SUB, "l")

# ---------------- CTA ----------------
BY=px(1198); BH2=px(92); BW2=px(520); BX=(W-BW2)/2
d.rounded_rectangle([BX,BY+px(6),BX+BW2,BY+BH2+px(6)], BH2//2, fill=(120,112,236,70))
d.rounded_rectangle([BX,BY,BX+BW2,BY+BH2], BH2//2, fill=IND)
text("Start free at verbavia.com", W/2, BY+px(26), 30, 750, (255,255,255), "c")
text("No streaks. No hearts. No ads.", W/2, px(1312), 21, 600, MUT, "c")

img.resize((AW,AH), Image.LANCZOS).save("verbavia_ad.png")
print("ad saved", (AW,AH))
