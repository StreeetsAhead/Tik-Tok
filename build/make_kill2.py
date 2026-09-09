from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np, math

SS = 2
W, H = 1500*SS, 1024*SS
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def blur(im, r): return im.filter(ImageFilter.GaussianBlur(r*SS))
def trim(im):
    bb = im.split()[3].getbbox()
    return im.crop(bb) if bb else im
def np_(im): return np.asarray(im).astype(np.float32)/255.0
def pil(a): return Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8))

# ---------------------------------------------------------------- subjects
def cutout_duo():
    src = Image.open("shots/duo_home_m.png").convert("RGB")
    d = src.crop((573,755,965,1125)).resize((392*3,370*3), Image.LANCZOS)
    w,h = d.size
    ff = d.copy()
    for pt in [(2,2),(w-3,2),(2,h-3),(w-3,h-3),(w//2,2)]:
        ImageDraw.floodfill(ff,pt,(255,0,255),thresh=28)
    a=np.asarray(ff); bg=(a[...,0]>240)&(a[...,1]<30)&(a[...,2]>240)
    rgb=np_(d); mx=rgb.max(-1); mn=rgb.min(-1)
    sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]; dd=np.maximum(mx-mn,1e-6)
    hue=np.where(mx==r,((g-b)/dd)%6,np.where(mx==g,(b-r)/dd+2,(r-g)/dd+4))*60
    keep=(~bg)&~((sat>0.22)&(hue>195)&(hue<345))
    bm=Image.fromarray((keep*255).astype(np.uint8)).convert("RGB")
    ImageDraw.floodfill(bm,(int(w*0.55),int(h*0.50)),(255,0,0),thresh=0)
    bb=np.asarray(bm); keep=(bb[...,0]==255)&(bb[...,1]==0)
    d.putalpha(Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)))
    return d.convert("RGBA")

duo = cutout_duo(); dw,dh = duo.size
dd = ImageDraw.Draw(duo)
for ex,ey in [(0.44,0.38),(0.66,0.36)]:                       # X eyes
    cx,cy = ex*dw, ey*dh; rr=dw*0.060; t=int(dw*0.024)
    dd.line([cx-rr,cy-rr,cx+rr,cy+rr], fill=(26,26,30,255), width=t)
    dd.line([cx+rr,cy-rr,cx-rr,cy+rr], fill=(26,26,30,255), width=t)
tx,ty = 0.545*dw, 0.50*dh                                      # tongue
dd.ellipse([tx-dw*0.033,ty-dh*0.012,tx+dw*0.033,ty+dh*0.115], fill=(226,124,158,255))
dd.ellipse([tx-dw*0.020,ty+dh*0.02,tx+dw*0.012,ty+dh*0.085], fill=(240,150,180,255))
duo = duo.resize((int(dw*1.0),int(dh*0.80)), Image.LANCZOS).rotate(14, resample=Image.BICUBIC, expand=True)
duo = trim(duo)
duo = duo.resize((int(560*SS), int(duo.height*560*SS/duo.width)), Image.LANCZOS)
_da = duo.split()[3].filter(ImageFilter.MinFilter(7))
duo.putalpha(_da)

def emoji(ch, px):
    f=__import__("PIL.ImageFont",fromlist=["x"]).truetype(EMO,109)
    t=Image.new("RGBA",(300,300),(0,0,0,0)); ImageDraw.Draw(t).text((10,10),ch,font=f,embedded_color=True)
    return t.crop(t.getbbox()).resize((px,px), Image.LANCZOS)
comp = trim(emoji("🧭", int(330*SS)).rotate(-18, resample=Image.BICUBIC, expand=True))

# ---------------------------------------------------------------- knife (shaded metal)
def knife(L):
    Wd=int(L*0.46); cx=Wd//2; bw=L*0.070; gy=L*0.315
    shape=Image.new("L",(Wd,L),0); sd=ImageDraw.Draw(shape)
    sd.polygon([(cx-bw,gy),(cx+bw,gy),(cx+bw*0.52,L*0.945),(cx,L),(cx-bw*0.52,L*0.945)], fill=255)
    ys,xs=np.mgrid[0:L,0:Wd]
    t=np.clip((xs-(cx-bw))/(2*bw),0,1)                    # 0 = left edge, 1 = right edge
    v=(0.30+0.62*np.exp(-((t-0.30)**2)/0.020)             # main specular band
        +0.34*np.exp(-((t-0.72)**2)/0.055)                # secondary roll-off
        -0.26*np.exp(-((t-0.02)**2)/0.004)                # dark left bevel
        -0.30*np.exp(-((t-0.99)**2)/0.004))               # dark right bevel
    v*= (0.86+0.22*np.clip((ys-gy)/(L*0.63),0,1))         # brighter toward the tip
    metal=np.dstack([v*0.97, v*1.00, v*1.06])             # cool steel
    blade=pil(np.clip(metal,0,1)).convert("RGBA")
    blade.putalpha(shape.filter(ImageFilter.GaussianBlur(0.6*SS)))

    k=Image.new("RGBA",(Wd,L),(0,0,0,0))
    k.alpha_composite(blade)
    kd=ImageDraw.Draw(k)
    # guard with a lit top edge
    kd.rounded_rectangle([cx-L*0.150,gy-L*0.030,cx+L*0.150,gy+L*0.030],int(L*0.028), fill=(78,86,102,255))
    kd.rounded_rectangle([cx-L*0.150,gy-L*0.030,cx+L*0.150,gy-L*0.006],int(L*0.020), fill=(126,136,156,255))
    # handle, wrapped
    kd.rounded_rectangle([cx-L*0.082,L*0.045,cx+L*0.082,gy-L*0.014],int(L*0.038), fill=(41,32,29,255))
    for i in range(7):
        yy=L*0.075+i*(gy-L*0.115)/7
        kd.rounded_rectangle([cx-L*0.082,yy,cx+L*0.082,yy+L*0.020],int(L*0.010), fill=(58,46,41,255))
    kd.rounded_rectangle([cx-L*0.082,L*0.045,cx-L*0.038,gy-L*0.014],int(L*0.026), fill=(74,60,53,200))
    kd.ellipse([cx-L*0.060,L*0.008,cx+L*0.060,L*0.082], fill=(88,96,112,255))
    kd.ellipse([cx-L*0.060,L*0.008,cx+L*0.010,L*0.052], fill=(130,140,160,255))
    return k

KN_ANG, KN_LEN = 48, int(600*SS)
def marked(L):
    k=knife(L); d=ImageDraw.Draw(k)
    d.rectangle([k.width//2-1,L-3,k.width//2+1,L-1], fill=(255,0,255,255))
    d.rectangle([k.width//2-1,int(L*0.05),k.width//2+1,int(L*0.05)+2], fill=(0,255,255,255))
    return k
_m=np.asarray(marked(KN_LEN).rotate(KN_ANG,resample=Image.BICUBIC,expand=True))
_t=np.argwhere((_m[...,0]>200)&(_m[...,1]<80)&(_m[...,2]>200))
_h=np.argwhere((_m[...,0]<80)&(_m[...,1]>200)&(_m[...,2]>200))
TIP_OFF=(int(_t[:,1].mean()),int(_t[:,0].mean())); HDL_OFF=(int(_h[:,1].mean()),int(_h[:,0].mean()))
kn = knife(KN_LEN).rotate(KN_ANG, resample=Image.BICUBIC, expand=True)

# ---------------------------------------------------------------- layout
DUO_BASE = int(H*0.815)
DUO_XY = (int(W*0.430), 0)
DUO_XY = (DUO_XY[0], DUO_BASE-duo.height)
TIP    = (DUO_XY[0]+int(duo.width*0.44), DUO_XY[1]+int(duo.height*0.50))
KN_XY  = (TIP[0]-TIP_OFF[0], TIP[1]-TIP_OFF[1])
HDL    = (KN_XY[0]+HDL_OFF[0], KN_XY[1]+HDL_OFF[1])
COMP_XY= (int(HDL[0]-comp.width*0.62), int(HDL[1]-comp.height*0.60))
POOL   = (int(W*0.545), int(H*0.815))                 # spotlight pool centre on the floor

# ---------------------------------------------------------------- stage
ys,xs = np.mgrid[0:H,0:W]
base = np.zeros((H,W,3), np.float32)
base[:] = np.array([0.030,0.030,0.040])
HOR = int(H*0.30)
floor = np.clip((ys-HOR)/(H*0.28),0,1)
base += floor[...,None]*np.array([0.070,0.072,0.085])
d_pool = np.sqrt(((xs-POOL[0])/(W*0.33))**2 + ((ys-POOL[1])/(H*0.185))**2)
pool = np.clip(1-d_pool,0,1)
pool = pool**1.35
base += (pool*floor)[...,None]*np.array([0.60,0.60,0.605])
core = np.clip(1-d_pool*1.55,0,1)**1.9
base += (core*floor)[...,None]*np.array([0.13,0.13,0.125])
d_amb = np.sqrt(((xs-POOL[0])/(W*0.95))**2+((ys-POOL[1])/(H*0.95))**2)
base += (np.clip(1-d_amb,0,1)**2.2)[...,None]*np.array([0.085,0.085,0.115])
stage = pil(base).convert("RGBA")

# volumetric cone
cone = Image.new("L",(W,H),0)
ImageDraw.Draw(cone).polygon([(W*0.470,-H*0.05),(W*0.560,-H*0.05),
                              (POOL[0]+W*0.38,POOL[1]),(POOL[0]-W*0.38,POOL[1])], fill=255)
cone = np.asarray(blur(cone,26)).astype(np.float32)/255.0
cone *= np.clip(1-(ys/ (H*0.95)),0.12,1)**1.25
haze = np.random.default_rng(3).normal(0,1,(H//8,W//8))
haze = np.asarray(Image.fromarray(((haze-haze.min())/np.ptp(haze)*255).astype(np.uint8))
                  .resize((W,H), Image.BICUBIC)).astype(np.float32)/255.0
cone *= (0.80+0.40*haze)
stage = pil(np_(stage.convert("RGB")) + cone[...,None]*np.array([0.085,0.085,0.105])).convert("RGBA")

# ---------------------------------------------------------------- shadows + reflections
def soft_shadow(sub, xy, squash=0.20, blur_r=26, opacity=0.72, dy=0.0, dx=0.0):
    a = sub.split()[3]
    sh = Image.new("L",(W,H),0)
    sq = a.resize((int(sub.width*1.06), max(int(sub.height*squash),2)), Image.LANCZOS)
    sh.paste(sq,(int(xy[0]-sub.width*0.03+dx*SS), int(xy[1]+sub.height*(1-squash)+dy*SS)))
    sh = blur(sh, blur_r)
    return Image.fromarray((np.asarray(sh).astype(np.float32)*opacity).astype(np.uint8))

def apply_shadow(canvas, mask):
    c = np_(canvas.convert("RGB")); m = np.asarray(mask).astype(np.float32)/255.0
    return pil(c*(1-m[...,None]*0.88)).convert("RGBA")

def reflection(sub, xy, strength=0.24, squash=0.42, blur_r=9):
    r = sub.transpose(Image.FLIP_TOP_BOTTOM)
    r = r.resize((sub.width, max(int(sub.height*squash),2)), Image.LANCZOS)
    g = np.linspace(strength,0.0,r.height)[:,None]
    al = (np.asarray(r.split()[3]).astype(np.float32)*g).astype(np.uint8)
    r.putalpha(Image.fromarray(al))
    lay = Image.new("RGBA",(W,H),(0,0,0,0))
    lay.alpha_composite(r,(xy[0], xy[1]+sub.height))
    return blur(lay, blur_r)

# ---------------------------------------------------------------- relighting
def relight(sub, origin_y, warm=1.0, top=1.34, bottom=0.46, rim=0.30):
    a=np_(sub.convert("RGB")); h=sub.height
    g=np.linspace(top,bottom,h)[:,None,None]
    a=a*g*np.array([1.02*warm,1.0,0.97/warm])
    al=np.asarray(sub.split()[3]).astype(np.float32)/255.0
    edge=np.clip(al-np.asarray(blur(sub.split()[3],3)).astype(np.float32)/255.0,0,1)
    a+=edge[...,None]*rim*np.array([1.0,0.98,0.92])
    out=pil(np.clip(a,0,1)).convert("RGBA"); out.putalpha(sub.split()[3]); return out

duo_l  = relight(duo,  DUO_XY[1], top=1.20, bottom=0.74, rim=0.05)
comp_l = relight(comp, COMP_XY[1], top=1.16, bottom=0.78, rim=0.26)
kn_l   = relight(kn,   KN_XY[1],  top=1.16, bottom=0.92, rim=0.08)

# ---------------------------------------------------------------- compose
img = stage
img = apply_shadow(img, soft_shadow(duo_l,  DUO_XY,  squash=0.10, blur_r=12, opacity=1.0, dy=-46, dx=10))
img = apply_shadow(img, soft_shadow(comp_l, COMP_XY, squash=0.09, blur_r=40, opacity=0.42, dy=430, dx=95))
img.alpha_composite(reflection(duo_l, DUO_XY, 0.13, squash=0.30, blur_r=13))

img.alpha_composite(kn_l, KN_XY)                                  # blade under
img.alpha_composite(duo_l, DUO_XY)                                # his body occludes it

# where does the blade cross his silhouette? walk back along the axis from the tip
_al = np.asarray(duo_l.split()[3])
vx, vy = TIP[0]-HDL[0], TIP[1]-HDL[1]
_L = math.hypot(vx,vy); ux, uy = vx/_L, vy/_L
ENTRY = TIP
for t in range(0, int(_L)):
    px, py = TIP[0]-ux*t, TIP[1]-uy*t
    ix, iy = int(px-DUO_XY[0]), int(py-DUO_XY[1])
    if not (0 <= ix < _al.shape[1] and 0 <= iy < _al.shape[0]) or _al[iy,ix] < 128:
        ENTRY = (int(px), int(py)); break

ang = math.degrees(math.atan2(vy,vx))
def oriented(w,h,fill,blur_r):
    box = Image.new("RGBA",(int(w*2),int(h*2)),(0,0,0,0))
    ImageDraw.Draw(box).ellipse([w*0.5,h*0.5,w*1.5,h*1.5], fill=fill)
    box = box.rotate(-ang, resample=Image.BICUBIC, expand=True)
    return blur(box, blur_r)

# darkened dimple around the entry, then the slit itself
dim = oriented(int(150*SS), int(96*SS), (10,34,4,150), 9)
img.alpha_composite(dim, (ENTRY[0]-dim.width//2, ENTRY[1]-dim.height//2))
slit = oriented(int(86*SS), int(26*SS), (16,44,8,235), 2.2)
img.alpha_composite(slit, (ENTRY[0]-slit.width//2, ENTRY[1]-slit.height//2))

# the blade edge catching light right at the wound
spark = Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(spark).ellipse([ENTRY[0]-int(26*SS),ENTRY[1]-int(9*SS),
                               ENTRY[0]+int(26*SS),ENTRY[1]+int(9*SS)], fill=(226,232,244,120))
img.alpha_composite(blur(spark,4))

img.alpha_composite(comp_l, COMP_XY)

# ---------------------------------------------------------------- brand lockup
brand = Image.open("shots/brand_mark.png").convert("RGB")
_bf = brand.copy()
for pt in [(1,1),(brand.width-2,1),(1,brand.height-2),(brand.width-2,brand.height-2)]:
    ImageDraw.floodfill(_bf, pt, (255,0,255), thresh=18)
_ba = np.asarray(_bf)
_bg = (_ba[...,0]>240)&(_ba[...,1]<40)&(_ba[...,2]>240)
_alpha = ((~_bg)*255).astype(np.uint8)
brand_rgba = brand.convert("RGBA")
brand_rgba.putalpha(Image.fromarray(_alpha).filter(ImageFilter.GaussianBlur(0.7)))
_bc = np_(brand_rgba.convert("RGB"))
_purple = (_bc[...,2]>_bc[...,1]+0.10)
_bc[_purple] = np.clip(_bc[_purple]*1.30+0.10, 0, 1)
brand_rgba = pil(_bc).convert("RGBA")
brand_rgba.putalpha(Image.fromarray(_alpha).filter(ImageFilter.GaussianBlur(0.7)))
bw = int(W*0.27); brand_rgba = brand_rgba.resize((bw,int(brand_rgba.height*bw/brand_rgba.width)), Image.LANCZOS)
BX = (W//2-brand_rgba.width//2, int(H*0.055))
glow = Image.new("RGBA",(W,H),(0,0,0,0)); glow.alpha_composite(brand_rgba, BX)
img.alpha_composite(blur(glow,22))
img.alpha_composite(blur(glow,9))
img.alpha_composite(brand_rgba, BX)

# ---------------------------------------------------------------- grade
a = np_(img.convert("RGB"))
a = np.clip((a-0.5)*1.16+0.5, 0, 1)
a[...,2] += 0.030*(1-a[...,2])**2.0
a[...,0] += 0.022*(a[...,0]**1.5)
vg = np.clip(1-np.sqrt(((xs-W/2)/(W*1.15))**2+((ys-H*0.55)/(H*1.15))**2),0,1)**0.70
a *= (0.66+0.34*vg)[...,None]
hi = np.clip(a-0.76,0,None)
a = np.clip(a + np_(blur(pil(hi),18))*0.55, 0, 1)
a += np.random.default_rng(11).normal(0,0.0075,a.shape).astype(np.float32)
out = pil(np.clip(a,0,1)).resize((W//SS,H//SS), Image.LANCZOS)
out.save("verbavia_kill.png")
port = Image.new("RGB",(1080,1350),(6,6,9))
band = out.resize((1080,int(out.height*1080/out.width)), Image.LANCZOS)
port.paste(band,(0,int(1350*0.5-band.height*0.5))); port.save("verbavia_kill_portrait.png")
print("saved", out.size, port.size, "| tip",TIP,"handle",HDL,"comp",COMP_XY)
