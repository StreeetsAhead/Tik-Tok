from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math

SS = 3
FW, FH = 962, 655                       # matches the screenshot exactly
W, H = FW*SS, FH*SS
def px(v): return int(round(v*SS))
def trim(im):
    bb = im.split()[3].getbbox(); return im.crop(bb) if bb else im

BLOOD_D=(140,16,24,255); BLOOD=(183,24,32,255); BLOOD_L=(214,46,52,255)

# ---- Duo's silhouette in the screenshot, traced so blood can be masked to him ----
duo_mask = Image.new("L",(W,H),0); m = ImageDraw.Draw(duo_mask)
for cx,cy,rx,ry in [(458,302,163,108),(398,238,78,62),(548,252,86,72),(600,372,48,30),(470,352,120,60)]:
    m.ellipse([px(cx-rx),px(cy-ry),px(cx+rx),px(cy+ry)], fill=255)
duo_mask = duo_mask.filter(ImageFilter.GaussianBlur(px(1)))

# ---- sword ----
def sword(L):
    Wd=int(L*0.34); k=Image.new("RGBA",(Wd,L),(0,0,0,0)); kd=ImageDraw.Draw(k)
    cx=Wd//2; POM=L*0.036; G0,G1=L*0.055,L*0.170; GY0,GY1=L*0.170,L*0.205; BL0=L*0.205; bw=L*0.052
    kd.polygon([(cx-bw,BL0),(cx+bw,BL0),(cx+bw*0.42,L*0.955),(cx,L),(cx-bw*0.42,L*0.955)], fill=(203,211,223,255))
    kd.polygon([(cx-bw,BL0),(cx-bw*0.06,BL0),(cx-bw*0.04,L*0.955),(cx-bw*0.42,L*0.955)], fill=(240,245,251,255))
    kd.polygon([(cx+bw*0.40,BL0),(cx+bw,BL0),(cx+bw*0.42,L*0.955),(cx+bw*0.26,L*0.955)], fill=(146,157,174,255))
    kd.polygon([(cx-bw*0.30,BL0+L*0.012),(cx+bw*0.30,BL0+L*0.012),(cx+bw*0.14,L*0.855),(cx-bw*0.14,L*0.855)], fill=(176,186,201,255))
    qh=L*0.150
    kd.polygon([(cx-qh,GY0+L*0.006),(cx+qh,GY0+L*0.006),(cx+qh*0.86,GY1),(cx-qh*0.86,GY1)], fill=(74,82,98,255))
    kd.rounded_rectangle([cx-qh,GY0-L*0.004,cx+qh,GY0+L*0.014],int(L*0.010), fill=(116,127,147,255))
    kd.ellipse([cx-qh-L*0.020,GY0-L*0.004,cx-qh+L*0.026,GY1+L*0.006], fill=(96,106,124,255))
    kd.ellipse([cx+qh-L*0.026,GY0-L*0.004,cx+qh+L*0.020,GY1+L*0.006], fill=(74,82,98,255))
    kd.rounded_rectangle([cx-L*0.030,G0,cx+L*0.030,G1],int(L*0.016), fill=(43,34,31,255))
    kd.rounded_rectangle([cx-L*0.030,G0,cx-L*0.010,G1],int(L*0.010), fill=(68,55,48,255))
    for i in range(5):
        yy=G0+L*0.012+i*(G1-G0-L*0.020)/5
        kd.rounded_rectangle([cx-L*0.030,yy,cx+L*0.030,yy+L*0.008],int(L*0.004), fill=(58,46,41,255))
    kd.ellipse([cx-POM,G0-POM*1.5,cx+POM,G0+POM*0.5], fill=(88,97,114,255))
    kd.ellipse([cx-POM*0.72,G0-POM*1.32,cx+POM*0.16,G0-POM*0.10], fill=(126,137,157,255))
    return k

ANG, LEN = 20, px(300)
def marked(L):
    k=sword(L); d=ImageDraw.Draw(k)
    d.rectangle([k.width//2-1,L-3,k.width//2+1,L-1], fill=(255,0,255,255))
    d.rectangle([k.width//2-1,int(L*0.020),k.width//2+1,int(L*0.020)+2], fill=(0,255,255,255))
    return k
_m=np.asarray(marked(LEN).rotate(ANG,resample=Image.BICUBIC,expand=True))
_t=np.argwhere((_m[...,0]>200)&(_m[...,1]<80)&(_m[...,2]>200))
_h=np.argwhere((_m[...,0]<80)&(_m[...,1]>200)&(_m[...,2]>200))
TIP_OFF=(int(_t[:,1].mean()),int(_t[:,0].mean())); HDL_OFF=(int(_h[:,1].mean()),int(_h[:,0].mean()))
sw = sword(LEN).rotate(ANG, resample=Image.BICUBIC, expand=True)

TIP = (px(448), px(362))                       # in his body mass, clear of the face
SW_XY = (TIP[0]-TIP_OFF[0], TIP[1]-TIP_OFF[1])
HDL = (SW_XY[0]+HDL_OFF[0], SW_XY[1]+HDL_OFF[1])

ov = Image.new("RGBA",(W,H),(0,0,0,0))

# blood pool on the stage, under him
bl = Image.new("RGBA",(W,H),(0,0,0,0)); bd = ImageDraw.Draw(bl)
def blob(cx,cy,rx,ry,seed,n=64,amp=0.20):
    rng=np.random.default_rng(seed); ph=rng.uniform(0,6.28,4); fr=np.array([2,3,5,7]); pts=[]
    for i in range(n):
        t=2*math.pi*i/n
        mm=1+amp*sum(math.sin(fr[k]*t+ph[k])/(k+1.6) for k in range(4))
        pts.append((cx+math.cos(t)*rx*mm, cy+math.sin(t)*ry*mm))
    return pts
PCX,PCY = px(455), px(415)
bd.polygon(blob(PCX,PCY,px(178),px(44),7,amp=0.16), fill=BLOOD_D)
bd.polygon(blob(PCX-px(8),PCY-px(4),px(144),px(34),11,amp=0.18), fill=BLOOD)
bd.polygon(blob(PCX-px(42),PCY-px(8),px(50),px(11),3,amp=0.22), fill=BLOOD_L)
for sx,sy,rr,sd in [(-238,16,16,21),(-198,34,10,22),(214,26,14,23),(252,8,8,24),(-146,46,7,25),(176,42,6,26)]:
    bd.polygon(blob(PCX+px(sx),PCY+px(sy),px(rr),px(rr*0.44),sd,n=26,amp=0.24), fill=BLOOD)
_binv = np.clip(255 - np.asarray(duo_mask).astype(np.int16), 0, 255).astype(np.float32)
bl.putalpha(Image.fromarray((np.asarray(bl.split()[3]).astype(np.float32)*_binv/255).astype(np.uint8)))
ov.alpha_composite(bl)

# cut the blade where his body begins, so the tip reads as buried once composited
sw_lay = Image.new("RGBA",(W,H),(0,0,0,0)); sw_lay.alpha_composite(sw, SW_XY)
_inv = 255 - np.asarray(duo_mask).astype(np.int16)
sw_lay.putalpha(Image.fromarray((np.asarray(sw_lay.split()[3]).astype(np.float32)
                                 *np.clip(_inv,0,255).astype(np.float32)/255).astype(np.uint8)))
ov.alpha_composite(sw_lay)

# entry point: walk back along the blade until we leave his silhouette
_al=np.asarray(duo_mask)
vx,vy=TIP[0]-HDL[0], TIP[1]-HDL[1]; _L=math.hypot(vx,vy); ux,uy=vx/_L, vy/_L
ENTRY=TIP
for t in range(int(_L)):
    p=(TIP[0]-ux*t, TIP[1]-uy*t); ix,iy=int(p[0]),int(p[1])
    if not(0<=ix<W and 0<=iy<H) or _al[iy,ix]<128: ENTRY=(int(p[0]),int(p[1])); break
ang=math.degrees(math.atan2(vy,vx))

def stamp(w,h,fn,a):
    lay=Image.new("RGBA",(w*2,h*2),(0,0,0,0)); fn(ImageDraw.Draw(lay),w,h)
    return lay.rotate(-a, resample=Image.BICUBIC, expand=True)
def _w(d_,w,h):
    d_.ellipse([w*0.5,h*0.5,w*1.5,h*1.5], fill=BLOOD_D)
    d_.ellipse([w*0.5+w*0.12,h*0.5+h*0.20,w*1.5-w*0.12,h*1.5-h*0.20], fill=(96,8,14,255))
wd=stamp(px(64),px(16),_w,ang)
ov.alpha_composite(wd,(ENTRY[0]-wd.width//2, ENTRY[1]-wd.height//2))

# drips down his body, clipped to his silhouette
dl=Image.new("RGBA",(W,H),(0,0,0,0)); dd_=ImageDraw.Draw(dl)
def drip(d_,x,y,ln,wt,bulb=1.5):
    wb=wt*0.42
    d_.polygon([(x-wt,y),(x+wt,y),(x+wb,y+ln),(x-wb,y+ln)], fill=BLOOD)
    d_.ellipse([x-wb*bulb,y+ln-wb*0.9,x+wb*bulb,y+ln+wb*bulb*1.5], fill=BLOOD)
for dx0,ln,wt in [(-18,86,4.2),(2,150,5.0),(24,60,3.4),(44,112,3.9),(-36,52,2.8)]:
    drip(dd_, ENTRY[0]+px(dx0), ENTRY[1]+px(2), px(ln), px(wt))
dl.putalpha(Image.fromarray((np.asarray(dl.split()[3]).astype(np.float32)
                             *np.asarray(duo_mask).astype(np.float32)/255).astype(np.uint8)))
ov.alpha_composite(dl)
ov.alpha_composite(wd,(ENTRY[0]-wd.width//2, ENTRY[1]-wd.height//2))

# blood smear up the blade
sm=Image.new("RGBA",(W,H),(0,0,0,0)); smd=ImageDraw.Draw(sm)
for k_ in range(30):
    f=k_/30.0; bx,by=ENTRY[0]-ux*px(72)*f, ENTRY[1]-uy*px(72)*f; rr=px(6)*(1-f*0.85)
    smd.ellipse([bx-rr,by-rr*0.8,bx+rr,by+rr*0.8], fill=BLOOD)
swm=sw_lay.split()[3]
sm.putalpha(Image.fromarray((np.asarray(sm.split()[3]).astype(np.float32)
                             *np.asarray(swm).astype(np.float32)/255).astype(np.uint8)))
ov.alpha_composite(sm)

ov.resize((FW,FH), Image.LANCZOS).save("sword_overlay.png")
print("overlay saved", (FW,FH), "| entry", (ENTRY[0]//SS, ENTRY[1]//SS), "| angle", round(ang,1))
