from PIL import Image, ImageDraw, ImageFilter
import numpy as np
SRC=Image.open("shots/duo_home_m.png").convert("RGB")
def base():
    owl=SRC.crop((573,755,965,1125)).resize((392*3,370*3),Image.LANCZOS); W,H=owl.size
    ff=owl.copy()
    for pt in [(2,2),(W-3,2),(2,H-3),(W-3,H-3),(W//2,2)]: ImageDraw.floodfill(ff,pt,(255,0,255),thresh=28)
    a=np.asarray(ff); bg=(a[...,0]>240)&(a[...,1]<30)&(a[...,2]>240)
    rgb=np.asarray(owl).astype(np.float32)/255
    mx=rgb.max(-1); mn=rgb.min(-1); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]; d=np.maximum(mx-mn,1e-6)
    hue=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    keep=(~bg)&~((sat>0.22)&(hue>195)&(hue<345))
    binm=Image.fromarray((keep*255).astype(np.uint8)).convert("RGB")
    ImageDraw.floodfill(binm,(int(W*0.55),int(H*0.50)),(255,0,0),thresh=0)
    bb=np.asarray(binm); keep=(bb[...,0]==255)&(bb[...,1]==0)
    alpha=Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    return rgb, alpha, (W,H)

def make(level, seed=13):
    """level 0..1 : 0 = barely off, 1 = full horror"""
    rgb,alpha,(W,H)=base(); arr=rgb.copy(); rng=np.random.default_rng(seed)
    lum=arr@np.array([0.299,0.587,0.114],dtype=np.float32)
    arr=lum[...,None]+(arr-lum[...,None])*(1-0.6*level)
    arr=(arr-0.5)*(1+0.55*level)+0.5-0.22*level; arr=np.clip(arr,0,1)
    arr[...,1]*=1-0.10*level; arr[...,2]*=1-0.30*level
    eyes=[(0.44,0.38),(0.66,0.36)]; yy,xx=np.mgrid[0:H,0:W]; white=(rgb.min(-1)>0.80)
    for ex,ey in eyes:
        dd=np.sqrt(((xx-ex*W)/(W*0.10))**2+((yy-ey*H)/(H*0.11))**2)
        socket=(dd<1.0)&white
        red=np.array([0.55,0.02,0.03]); wht=np.array([1,1,1])
        arr[socket]=arr[socket]*(1-level)+ (red*level+wht*(1-level))*level + arr[socket]*0  if level>0 else arr[socket]
        core=np.clip(1-dd/0.55,0,1)**1.3; halo=np.clip(1-dd/2.4,0,1)**2.4
        arr[...,0]+=(core*0.9+halo*0.45)*level; arr[...,1]+=(core*0.10-halo*0.10)*level; arr[...,2]+=(core*0.05-halo*0.14)*level
        # subtle level: darken the pupils / ring under the eye
        ring=(dd>0.95)&(dd<1.25)
        arr[ring]*=1-0.35*min(level*2,1)
        if level>0.45:
            for k in range(3):
                x0=int(ex*W+(k-1)*W*0.025); w0=max(int(W*0.012),3); L=int(H*(0.18+0.10*(k%2))*level); y0=int(ey*H+H*0.09)
                arr[y0:y0+L,x0:x0+w0]=arr[y0:y0+L,x0:x0+w0]*0.35+np.array([0.42,0.01,0.02])*0.65
    arr=np.clip(arr,0,1)
    for _ in range(int(18*level)):
        y0=rng.integers(0,H-40); hgt=rng.integers(6,44); dx=rng.integers(-44,44)
        arr[y0:y0+hgt]=np.roll(arr[y0:y0+hgt],dx,axis=1)
    sp=int(8*level)
    if sp: arr[...,0]=np.roll(arr[...,0],sp,axis=1); arr[...,2]=np.roll(arr[...,2],-sp,axis=1)
    if level>0.3: arr[::3]*=1-0.28*level
    arr+=rng.normal(0,0.012+0.045*level,arr.shape).astype(np.float32)
    out=Image.fromarray((np.clip(arr,0,1)*255).astype(np.uint8)).convert("RGBA"); out.putalpha(alpha)
    if level>0.5: out=out.resize((W,int(H*(1+0.10*level))),Image.BICUBIC)
    return out
for name,lv in [("owl_l1",0.22),("owl_l2",0.62),("owl_l3",1.0)]:
    im=make(lv); im.save(f"{name}.png"); print(name,im.size)
sheet=Image.new("RGB",(3*400,430),(20,18,24))
for i,n in enumerate(["owl_l1","owl_l2","owl_l3"]):
    im=Image.open(f"{n}.png"); im.thumbnail((380,410)); bg=Image.new("RGBA",im.size,(240,240,245,255) if i==0 else (20,18,24,255)); bg.alpha_composite(im); sheet.paste(bg.convert("RGB"),(i*400+10,10))
sheet.save("owls_sheet.png")
