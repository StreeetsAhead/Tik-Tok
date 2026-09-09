from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math

SS = 3
W, H = 1500*SS, 1024*SS
def px(v): return int(round(v*SS))
def trim(im):
    bb = im.split()[3].getbbox(); return im.crop(bb) if bb else im

BLOOD_D = (140, 16, 24, 255)      # deep
BLOOD   = (183, 24, 32, 255)      # body
BLOOD_L = (214, 46, 52, 255)      # highlight

# ------------------------------------------------------------------ Duo
src = Image.open("shots/duo_home_m.png").convert("RGB")
duo = src.crop((573,755,965,1125)).resize((392*3,370*3), Image.LANCZOS)
dw,dh = duo.size
ff = duo.copy()
for pt in [(2,2),(dw-3,2),(2,dh-3),(dw-3,dh-3),(dw//2,2)]:
    ImageDraw.floodfill(ff,pt,(255,0,255),thresh=28)
a=np.asarray(ff); bgm=(a[...,0]>240)&(a[...,1]<30)&(a[...,2]>240)
rgb=np.asarray(duo).astype(np.float32)/255
mx=rgb.max(-1); mn=rgb.min(-1); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]; dd=np.maximum(mx-mn,1e-6)
hue=np.where(mx==r,((g-b)/dd)%6,np.where(mx==g,(b-r)/dd+2,(r-g)/dd+4))*60
keep=(~bgm)&~((sat>0.22)&(hue>195)&(hue<345))
bm=Image.fromarray((keep*255).astype(np.uint8)).convert("RGB")
ImageDraw.floodfill(bm,(int(dw*0.55),int(dh*0.50)),(255,0,0),thresh=0)
bb2=np.asarray(bm); keep=(bb2[...,0]==255)&(bb2[...,1]==0)
duo.putalpha(Image.fromarray((keep*255).astype(np.uint8)))
duo = duo.convert("RGBA")
duo.putalpha(duo.split()[3].filter(ImageFilter.MinFilter(9)))

d = ImageDraw.Draw(duo)
for ex,ey in [(0.44,0.38),(0.66,0.36)]:
    cx,cy = ex*dw, ey*dh; rr=dw*0.058; t=int(dw*0.023)
    d.line([cx-rr,cy-rr,cx+rr,cy+rr], fill=(28,28,32,255), width=t)
    d.line([cx+rr,cy-rr,cx-rr,cy+rr], fill=(28,28,32,255), width=t)
tx,ty = 0.545*dw, 0.505*dh
d.ellipse([tx-dw*0.032,ty-dh*0.010,tx+dw*0.032,ty+dh*0.110], fill=(228,126,160,255))
d.ellipse([tx-dw*0.018,ty+dh*0.022,tx+dw*0.010,ty+dh*0.080], fill=(243,155,184,255))

duo = trim(duo.resize((dw, int(dh*0.80)), Image.LANCZOS).rotate(14, resample=Image.BICUBIC, expand=True))
duo = duo.resize((px(540), int(duo.height*px(540)/duo.width)), Image.LANCZOS)

# ------------------------------------------------------------------ logo
logo = trim(Image.open("verbavia_logo.png").convert("RGBA"))
logo = logo.resize((px(300), int(logo.height*px(300)/logo.width)), Image.LANCZOS)
logo = trim(logo.rotate(-14, resample=Image.BICUBIC, expand=True))

# ------------------------------------------------------------------ knife (flat vector)
def knife(L):
    Wd=int(L*0.44); k=Image.new("RGBA",(Wd,L),(0,0,0,0)); kd=ImageDraw.Draw(k)
    cx=Wd//2; bw=L*0.068; gy=L*0.325
    kd.polygon([(cx-bw,gy),(cx+bw,gy),(cx+bw*0.5,L*0.945),(cx,L),(cx-bw*0.5,L*0.945)], fill=(206,213,224,255))
    kd.polygon([(cx-bw,gy),(cx-bw*0.05,gy),(cx-bw*0.03,L*0.945),(cx-bw*0.5,L*0.945)], fill=(238,243,250,255))
    kd.polygon([(cx+bw*0.42,gy),(cx+bw,gy),(cx+bw*0.5,L*0.945),(cx+bw*0.30,L*0.945)], fill=(151,161,177,255))
    kd.rounded_rectangle([cx-L*0.150,gy-L*0.028,cx+L*0.150,gy+L*0.028],int(L*0.026), fill=(74,82,98,255))
    kd.rounded_rectangle([cx-L*0.150,gy-L*0.028,cx+L*0.150,gy-L*0.008],int(L*0.016), fill=(112,122,142,255))
    kd.rounded_rectangle([cx-L*0.078,L*0.050,cx+L*0.078,gy-L*0.012],int(L*0.036), fill=(43,34,31,255))
    kd.rounded_rectangle([cx-L*0.078,L*0.050,cx-L*0.032,gy-L*0.012],int(L*0.026), fill=(66,53,47,255))
    kd.ellipse([cx-L*0.056,L*0.012,cx+L*0.056,L*0.082], fill=(84,92,108,255))
    return k
KN_ANG, KN_LEN = 48, px(660)
def marked(L):
    k=knife(L); dd_=ImageDraw.Draw(k)
    dd_.rectangle([k.width//2-1,L-3,k.width//2+1,L-1], fill=(255,0,255,255))
    dd_.rectangle([k.width//2-1,int(L*0.055),k.width//2+1,int(L*0.055)+2], fill=(0,255,255,255))
    return k
_m=np.asarray(marked(KN_LEN).rotate(KN_ANG,resample=Image.BICUBIC,expand=True))
_t=np.argwhere((_m[...,0]>200)&(_m[...,1]<80)&(_m[...,2]>200))
_h=np.argwhere((_m[...,0]<80)&(_m[...,1]>200)&(_m[...,2]>200))
TIP_OFF=(int(_t[:,1].mean()),int(_t[:,0].mean())); HDL_OFF=(int(_h[:,1].mean()),int(_h[:,0].mean()))
kn = knife(KN_LEN).rotate(KN_ANG, resample=Image.BICUBIC, expand=True)

# ------------------------------------------------------------------ layout
FLOOR_CY = px(690); FLOOR_RX = px(600); FLOOR_RY = px(180)
DUO_BASE = FLOOR_CY + px(58)
DUO_XY = (px(690), DUO_BASE - duo.height)
TIP    = (DUO_XY[0]+int(duo.width*0.46), DUO_XY[1]+int(duo.height*0.46))
KN_XY  = (TIP[0]-TIP_OFF[0], TIP[1]-TIP_OFF[1])
HDL    = (KN_XY[0]+HDL_OFF[0], KN_XY[1]+HDL_OFF[1])
LOGO_XY= (int(HDL[0]-logo.width*0.76), int(HDL[1]-logo.height*0.72))

img = Image.new("RGBA",(W,H),(10,10,13,255))
dr = ImageDraw.Draw(img)
dr.polygon([(W*0.435,0),(W*0.565,0),(W*0.94,FLOOR_CY+px(30)),(W*0.06,FLOOR_CY+px(30))], fill=(45,45,50,255))
dr.ellipse([W/2-FLOOR_RX, FLOOR_CY-FLOOR_RY, W/2+FLOOR_RX, FLOOR_CY+FLOOR_RY], fill=(154,154,158,255))
dr.ellipse([W/2-FLOOR_RX*0.62, FLOOR_CY-FLOOR_RY*0.42, W/2+FLOOR_RX*0.62, FLOOR_CY+FLOOR_RY*0.86],
           fill=(133,133,138,255))

# ------------------------------------------------------------------ blood
def blob(cx, cy, rx, ry, seed, n=64, amp=0.20):
    rng=np.random.default_rng(seed)
    ph=rng.uniform(0,6.28,4); fr=np.array([2,3,5,7])
    pts=[]
    for i in range(n):
        t=2*math.pi*i/n
        m=1+amp*sum(math.sin(fr[k]*t+ph[k])/(k+1.6) for k in range(4))
        pts.append((cx+math.cos(t)*rx*m, cy+math.sin(t)*ry*m))
    return pts

bl = Image.new("RGBA",(W,H),(0,0,0,0)); bd = ImageDraw.Draw(bl)
PCX, PCY = DUO_XY[0]+int(duo.width*0.42), DUO_BASE - px(16)
bd.polygon(blob(PCX, PCY, px(252), px(62), 7, amp=0.16), fill=BLOOD_D)
bd.polygon(blob(PCX-px(12), PCY-px(5), px(208), px(48), 11, amp=0.18), fill=BLOOD)
bd.polygon(blob(PCX-px(58), PCY-px(12), px(78), px(17), 3, amp=0.22), fill=BLOOD_L)
for sx,sy,rr,sd in [(-322,22,22,21),(-268,46,13,22),(286,34,18,23),(338,12,11,24),(-196,62,9,25),(232,56,8,26)]:
    bd.polygon(blob(PCX+px(sx), PCY+px(sy), px(rr), px(rr*0.44), sd, n=26, amp=0.24), fill=BLOOD)
img.alpha_composite(bl)

# ------------------------------------------------------------------ knife + body
img.alpha_composite(kn, KN_XY)
img.alpha_composite(duo, DUO_XY)

_al = np.asarray(duo.split()[3])
vx, vy = TIP[0]-HDL[0], TIP[1]-HDL[1]
_L = math.hypot(vx,vy); ux, uy = vx/_L, vy/_L
ENTRY = TIP
for t in range(int(_L)):
    p=(TIP[0]-ux*t, TIP[1]-uy*t); ix,iy=int(p[0]-DUO_XY[0]), int(p[1]-DUO_XY[1])
    if not (0<=ix<_al.shape[1] and 0<=iy<_al.shape[0]) or _al[iy,ix]<128:
        ENTRY=(int(p[0]),int(p[1])); break
ang = math.degrees(math.atan2(vy,vx))

# crisp wound: sharp slit around the blade, drawn rotated, no blur
def stamp(w,h,draw_fn,angle):
    lay=Image.new("RGBA",(w*2,h*2),(0,0,0,0)); draw_fn(ImageDraw.Draw(lay), w, h)
    return lay.rotate(-angle, resample=Image.BICUBIC, expand=True)
def _wound(dw_, w, h):
    dw_.ellipse([w*0.5,h*0.5,w*1.5,h*1.5], fill=BLOOD_D)
    dw_.ellipse([w*0.5+w*0.12,h*0.5+h*0.20,w*1.5-w*0.12,h*1.5-h*0.20], fill=(96,8,14,255))
wd = stamp(px(96), px(24), _wound, ang)
img.alpha_composite(wd, (ENTRY[0]-wd.width//2, ENTRY[1]-wd.height//2))

# drips down the body from the wound
dl = Image.new("RGBA",(W,H),(0,0,0,0)); dld = ImageDraw.Draw(dl)
def drip(dd_, x, y, ln, wt, bulb=1.5):
    wb = wt*0.42
    dd_.polygon([(x-wt,y),(x+wt,y),(x+wb,y+ln),(x-wb,y+ln)], fill=BLOOD)
    dd_.ellipse([x-wb*bulb, y+ln-wb*0.9, x+wb*bulb, y+ln+wb*bulb*1.5], fill=BLOOD)
for dx0, ln, wt in [(-30,150,7.0),(2,268,8.5),(40,104,5.5),(74,196,6.5),(-62,88,4.5)]:
    drip(dld, ENTRY[0]+px(dx0), ENTRY[1]+px(2), px(ln), px(wt))
dmask = Image.new("L",(W,H),0)
dmask.paste(duo.split()[3], DUO_XY)
dl.putalpha(Image.fromarray((np.asarray(dl.split()[3]).astype(np.float32)
                             *np.asarray(dmask).astype(np.float32)/255).astype(np.uint8)))
img.alpha_composite(dl)
img.alpha_composite(wd, (ENTRY[0]-wd.width//2, ENTRY[1]-wd.height//2))

# blood on the blade near the wound
sm = Image.new("RGBA",(W,H),(0,0,0,0)); smd = ImageDraw.Draw(sm)
for k_ in range(30):
    f = k_/30.0
    bx, by = ENTRY[0]-ux*px(150)*f, ENTRY[1]-uy*px(150)*f
    rr = px(11)*(1-f*0.85)
    smd.ellipse([bx-rr,by-rr*0.8,bx+rr,by+rr*0.8], fill=BLOOD)
knm = Image.new("L",(W,H),0); knm.paste(kn.split()[3], KN_XY)
sm.putalpha(Image.fromarray((np.asarray(sm.split()[3]).astype(np.float32)
                             *np.asarray(knm).astype(np.float32)/255).astype(np.uint8)))
img.alpha_composite(sm)

img.alpha_composite(logo, LOGO_XY)

out = img.convert("RGB").resize((W//SS, H//SS), Image.LANCZOS)
out.save("verbavia_kill.png")
port = Image.new("RGB",(1080,1350),(10,10,13))
band = out.resize((1080,int(out.height*1080/out.width)), Image.LANCZOS)
port.paste(band,(0,int(1350*0.5-band.height*0.5))); port.save("verbavia_kill_portrait.png")
print("saved", out.size, "| entry", ENTRY, "angle", round(ang,1))
