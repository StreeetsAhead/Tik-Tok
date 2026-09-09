from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np, math

SS=3; FW,FH=962,655; W,H=FW*SS,FH*SS
def px(v): return int(round(v*SS))
FV="fonts/InterVar.ttf"
def F(sz,wt):
    f=ImageFont.truetype(FV,px(sz))
    try: f.set_variation_by_axes([32 if sz>=30 else 14, wt])
    except Exception: pass
    return f

G_LT=(126,216,62); G_MD=(103,195,43); G_DK=(74,160,28); G_SH=(88,178,36)
ORG=(244,166,36); ORG_D=(226,142,26); PNK=(226,141,190); PNK_L=(240,168,208)
STAGE=(158,158,158); CONE=(58,58,58); SHDW=(124,124,126); CROSS=(58,58,58)

img=Image.new("RGB",(W,H),(6,6,6)); d=ImageDraw.Draw(img)
d.polygon([(px(268),0),(px(712),0),(px(830),px(472)),(px(150),px(472))], fill=CONE)
d.ellipse([px(135),px(150),px(825),px(478)], fill=STAGE)

# ---------- Duo's body mass ----------
BODY=[(462,296,168,124),(396,230,74,60),(566,286,78,80),(470,368,142,48),(608,378,44,28),(300,212,30,19)]
mask=Image.new("L",(W,H),0); md=ImageDraw.Draw(mask)
for cx,cy,rx,ry in BODY: md.ellipse([px(cx-rx),px(cy-ry),px(cx+rx),px(cy+ry)], fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(px(1.2)))

# cast shadow on the stage
sh=Image.new("L",(W,H),0)
ImageDraw.Draw(sh).ellipse([px(330),px(360),px(660),px(432)], fill=255)
sh=sh.filter(ImageFilter.GaussianBlur(px(9)))
base=np.asarray(img).astype(np.float32)
shn=np.asarray(sh).astype(np.float32)[...,None]/255.0
img=Image.fromarray(np.clip(base*(1-shn*0.30),0,255).astype(np.uint8))

# green with a top-lit gradient
ys,xs=np.mgrid[0:H,0:W]
t=np.clip((ys-px(175))/px(240),0,1)[...,None]
grad=np.array(G_LT)*(1-t)+np.array(G_DK)*t
body=Image.fromarray(np.clip(grad,0,255).astype(np.uint8)).convert("RGBA")
body.putalpha(mask)

# shading + highlight inside the silhouette
sl=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sl)
for cx,cy,rx,ry,col in [(386,292,62,46,G_SH),(474,356,104,36,G_DK),(560,330,58,34,G_SH),(606,380,40,24,G_DK),(430,268,52,30,G_SH)]:
    sd.ellipse([px(cx-rx),px(cy-ry),px(cx+rx),px(cy+ry)], fill=col+(150,))
sl=sl.filter(ImageFilter.GaussianBlur(px(7)))
hl=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(hl)
hd.ellipse([px(360),px(196),px(492),px(258)], fill=(170,234,106,120))
hd.ellipse([px(508),px(214),px(600),px(262)], fill=(170,234,106,85))
hl=hl.filter(ImageFilter.GaussianBlur(px(9)))
body.alpha_composite(sl); body.alpha_composite(hl)
body.putalpha(mask)
img=img.convert("RGBA"); img.alpha_composite(body)
d=ImageDraw.Draw(img)

# ---------- feet ----------
for cx,cy,rx,ry in [(316,340,29,23),(408,378,33,25)]:
    d.ellipse([px(cx-rx),px(cy-ry),px(cx+rx),px(cy+ry)], fill=ORG)
    d.ellipse([px(cx-rx*0.72),px(cy-ry*0.86),px(cx+rx*0.26),px(cy+ry*0.10)], fill=(250,186,74))

# ---------- beak + tongue ----------
d.polygon([(px(448),px(212)),(px(492),px(222)),(px(462),px(248))], fill=ORG)
d.polygon([(px(452),px(242)),(px(494),px(236)),(px(474),px(262))], fill=ORG_D)
d.ellipse([px(448),px(232),px(486),px(292)], fill=PNK)
d.ellipse([px(456),px(242),px(474),px(280)], fill=PNK_L)

# ---------- eyes ----------
def cross(cx,cy,s):
    a=px(s); b=px(s*0.29); r=px(s*0.14)
    d.rounded_rectangle([px(cx)-b,px(cy)-a,px(cx)+b,px(cy)+a], r, fill=CROSS)
    d.rounded_rectangle([px(cx)-a,px(cy)-b,px(cx)+a,px(cy)+b], r, fill=CROSS)
for cx,cy,rx,ry,cs in [(455,212,40,38,17),(538,268,46,44,19)]:
    d.ellipse([px(cx-rx),px(cy-ry),px(cx+rx),px(cy+ry)], fill=(255,255,255))
    cross(cx,cy,cs)

# ---------- text ----------
def ctext(s,y,size,wt):
    f=F(size,wt); w=d.textlength(s,font=f); d.text((W/2-w/2,px(y)),s,font=f,fill=(255,255,255))
ctext("duolingo",112,23,600)
ctext("It's Duo or Die!",578,42,800)

img.convert("RGB").resize((FW,FH), Image.LANCZOS).save("duo_or_die.png")
mask.resize((FW,FH), Image.LANCZOS).save("duo_mask.png")
print("frame rebuilt", (FW,FH))
