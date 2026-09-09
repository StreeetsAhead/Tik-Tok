from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math

W,H = 1500,1024
FV = "fonts/InterVar.ttf"
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def F(sz,w):
    f=ImageFont.truetype(FV,sz)
    try: f.set_variation_by_axes([32 if sz>=50 else 14, w])
    except Exception: pass
    return f

# ---------- Duo, cut out of the real homepage ----------
src = Image.open("shots/duo_home_m.png").convert("RGB")
duo = src.crop((573,755,965,1125)).resize((392*3,370*3), Image.LANCZOS)
dw,dh = duo.size
ff = duo.copy()
for pt in [(2,2),(dw-3,2),(2,dh-3),(dw-3,dh-3),(dw//2,2)]:
    ImageDraw.floodfill(ff,pt,(255,0,255),thresh=28)
a=np.asarray(ff); bg=(a[...,0]>240)&(a[...,1]<30)&(a[...,2]>240)
rgb=np.asarray(duo).astype(np.float32)/255
mx=rgb.max(-1); mn=rgb.min(-1); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]; dd=np.maximum(mx-mn,1e-6)
hue=np.where(mx==r,((g-b)/dd)%6,np.where(mx==g,(b-r)/dd+2,(r-g)/dd+4))*60
keep=(~bg)&~((sat>0.22)&(hue>195)&(hue<345))
binm=Image.fromarray((keep*255).astype(np.uint8)).convert("RGB")
ImageDraw.floodfill(binm,(int(dw*0.55),int(dh*0.50)),(255,0,0),thresh=0)
bb=np.asarray(binm); keep=(bb[...,0]==255)&(bb[...,1]==0)
duo.putalpha(Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
duo = duo.convert("RGBA")

# X eyes + lolling tongue, drawn in his own flat style
d = ImageDraw.Draw(duo)
for ex,ey in [(0.44,0.38),(0.66,0.36)]:
    cx,cy = ex*dw, ey*dh; rr = dw*0.062; t = int(dw*0.026)
    d.line([cx-rr,cy-rr,cx+rr,cy+rr], fill=(30,30,35,255), width=t)
    d.line([cx+rr,cy-rr,cx-rr,cy+rr], fill=(30,30,35,255), width=t)
tx,ty = 0.545*dw, 0.50*dh
d.ellipse([tx-dw*0.035,ty,tx+dw*0.035,ty+dh*0.135], fill=(240,140,175,255))
d.ellipse([tx-dw*0.035,ty-dh*0.012,tx+dw*0.035,ty+dh*0.05], fill=(240,140,175,255))

# collapse him: squash + rotate
duo_flat = duo.resize((int(dw*1.0), int(dh*0.80)), Image.LANCZOS).rotate(14, resample=Image.BICUBIC, expand=True)
sc = 640/duo_flat.width
duo_flat = duo_flat.resize((640, int(duo_flat.height*sc)), Image.LANCZOS)

# ---------- compass ----------
ef = ImageFont.truetype(EMO,109)
tmp = Image.new("RGBA",(300,300),(0,0,0,0))
ImageDraw.Draw(tmp).text((10,10),"🧭",font=ef,embedded_color=True)
comp = tmp.crop(tmp.getbbox()).resize((330,330), Image.LANCZOS).rotate(-16, resample=Image.BICUBIC, expand=True)

# ---------- knife ----------
def knife(L=620):
    Wd=int(L*0.46); k=Image.new("RGBA",(Wd,L),(0,0,0,0)); kd=ImageDraw.Draw(k)
    cx=Wd//2
    bw=L*0.072                       # blade half-width
    gy=L*0.315                       # guard line
    kd.polygon([(cx-bw,gy),(cx+bw,gy),(cx+bw*0.55,L*0.94),(cx,L),(cx-bw*0.55,L*0.94)], fill=(216,221,230,255))
    kd.polygon([(cx-bw,gy),(cx-bw*0.18,gy),(cx-bw*0.12,L*0.94),(cx-bw*0.55,L*0.94)], fill=(247,250,253,255))
    kd.polygon([(cx+bw*0.22,gy),(cx+bw,gy),(cx+bw*0.55,L*0.94),(cx+bw*0.20,L*0.94)], fill=(158,167,182,255))
    kd.rounded_rectangle([cx-L*0.155,gy-L*0.030,cx+L*0.155,gy+L*0.030],int(L*0.028), fill=(92,100,116,255))
    kd.rounded_rectangle([cx-L*0.155,gy-L*0.030,cx-L*0.055,gy+L*0.030],int(L*0.022), fill=(126,135,152,255))
    kd.rounded_rectangle([cx-L*0.085,L*0.045,cx+L*0.085,gy-L*0.018],int(L*0.040), fill=(48,39,35,255))
    kd.rounded_rectangle([cx-L*0.085,L*0.045,cx-L*0.030,gy-L*0.018],int(L*0.030), fill=(80,66,58,255))
    kd.ellipse([cx-L*0.062,L*0.010,cx+L*0.062,L*0.085], fill=(92,100,116,255))
    return k

KN_ANG = 48
KN_LEN = 520
def knife_marked(L):
    k = knife(L); kd = ImageDraw.Draw(k)
    kd.point((100, L-2), fill=(255,0,255,255)); kd.point((100, int(L*0.05)), fill=(0,255,255,255))
    return k
_km = knife_marked(KN_LEN).rotate(KN_ANG, resample=Image.BICUBIC, expand=True)
_a = np.asarray(_km)
_mg = np.argwhere((_a[...,0]>200)&(_a[...,1]<80)&(_a[...,2]>200))
_cy = np.argwhere((_a[...,0]<80)&(_a[...,1]>200)&(_a[...,2]>200))
TIP_OFF = (int(_mg[:,1].mean()), int(_mg[:,0].mean())) if len(_mg) else (0,0)
HDL_OFF = (int(_cy[:,1].mean()), int(_cy[:,0].mean())) if len(_cy) else (0,0)
kn = knife(KN_LEN).rotate(KN_ANG, resample=Image.BICUBIC, expand=True)
print("tip offset", TIP_OFF, "handle offset", HDL_OFF, "knife size", kn.size)

# ---------- scene ----------
img = Image.new("RGB",(W,H),(8,8,10))
dr = ImageDraw.Draw(img,"RGBA")
cone = Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(cone).polygon([(W*0.42,0),(W*0.58,0),(W*0.90,H*0.74),(W*0.10,H*0.74)], fill=(58,58,62,255))
img.paste(Image.alpha_composite(img.convert("RGBA"),cone.filter(ImageFilter.GaussianBlur(3))).convert("RGB"),(0,0))
dr = ImageDraw.Draw(img,"RGBA")
dr.ellipse([W*0.10,H*0.42,W*0.90,H*0.90], fill=(150,150,152,255))
dr.ellipse([W*0.30,H*0.66,W*0.74,H*0.80], fill=(126,126,129,120))

img = img.convert("RGBA")
DUO_XY = (int(W*0.395), int(H*0.44))
duo_cx = DUO_XY[0] + duo_flat.width*0.55
duo_cy = DUO_XY[1] + duo_flat.height*0.52

TIP_TARGET = (int(DUO_XY[0]+duo_flat.width*0.40), int(DUO_XY[1]+duo_flat.height*0.66))   # chest
KN_XY = (TIP_TARGET[0]-TIP_OFF[0], TIP_TARGET[1]-TIP_OFF[1])
HDL_PT = (KN_XY[0]+HDL_OFF[0], KN_XY[1]+HDL_OFF[1])
COMP_XY = (int(HDL_PT[0]-comp.width*0.70), int(HDL_PT[1]-comp.height*0.68))
print("tip",TIP_TARGET,"handle",HDL_PT,"comp",COMP_XY,"duo",duo_flat.size)

img.alpha_composite(kn, KN_XY)                              # 1) blade underneath
img.alpha_composite(duo_flat, DUO_XY)                       # 2) Duo hides the tip

ENTRY_Y = TIP_TARGET[1] - 58                                # 3) everything above re-emerges
cut = ENTRY_Y - KN_XY[1]
m = Image.new("L", kn.size, 0)
if cut > 0:
    ImageDraw.Draw(m).rectangle([0,0,kn.size[0],min(cut,kn.size[1])], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(2))
kn_top = kn.copy()
kn_top.putalpha(Image.fromarray(
    (np.asarray(kn.split()[3]).astype(np.float32)*np.asarray(m).astype(np.float32)/255).astype(np.uint8)))
img.alpha_composite(kn_top, KN_XY)

ov = Image.new("RGBA",(W,H),(0,0,0,0))                      # flat entry shadow at the wound
ImageDraw.Draw(ov).ellipse([TIP_TARGET[0]-52,ENTRY_Y-20,TIP_TARGET[0]+30,ENTRY_Y+22], fill=(52,120,22,190))
img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
img.alpha_composite(kn_top, KN_XY)
img.alpha_composite(comp, COMP_XY)

d2 = ImageDraw.Draw(img)
def ctext(s,y,size,wt,fill=(255,255,255,255)):
    f=F(size,wt); w=d2.textlength(s,font=f); d2.text((W/2-w/2,y),s,font=f,fill=fill)
ctext("verbavia", H*0.035, 52, 700)
ctext("come and try", H*0.855, 92, 900)
img.convert("RGB").save("verbavia_kill.png")

# 4:5 portrait crop for feed/TikTok
PW,PH = 1080,1350
port = Image.new("RGB",(PW,PH),(8,8,10))
band = img.convert("RGB").resize((PW,int(H*PW/W)), Image.LANCZOS)
port.paste(band,(0,int(PH*0.5-band.height*0.5)))
pd = ImageDraw.Draw(port)
def pt(sv,y,size,wt):
    f=F(size,wt); w=pd.textlength(sv,font=f); pd.text((PW/2-w/2,y),sv,font=f,fill=(255,255,255))
port.paste(band,(0,int(PH*0.5-band.height*0.5)))
pt("verbavia", PH*0.075, 46, 700)
pt("come and try", PH*0.855, 84, 900)
port.save("verbavia_kill_portrait.png")
print("saved", img.size, port.size)
