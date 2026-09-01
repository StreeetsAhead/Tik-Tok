"""THE GAZE - guide bed (13.8s). Impacts on every cut; riser into Napoleon and the strobe."""
import numpy as np, wave
SR, FPS = 48000, 30
CUTS=[0,60,97,134,171,208]; STROBE0=283; STROBE_F=5; STACK0=313; BLACK1=339; CARD0=339; NF=414
DUR=NF/FPS; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(4); mix=np.zeros(N)
def env(s,L,atk=0.002,p=2.2):
    e=np.zeros(N); i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(atk*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:]=(1-np.linspace(0,1,n-a))**p
    e[i0:i1]=seg; return e
def hit(s,f0=95,f1=30,L=1.2,amp=0.9,g=0.05):
    i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; fr=f1+(f0-f1)*np.exp(-lt/g)
    mix[i0:i1]+=amp*np.sin(2*np.pi*np.cumsum(fr)/SR)*env(s,L,0.001,2.6)[i0:i1]
def tick(s,amp=0.4,L=0.1,tone=2200):
    nz=rng.normal(0,1,N); b=np.sin(2*np.pi*tone*t)*0.3+nz*0.7
    mix[:]+=amp*(b*0.35+np.concatenate(([0],b[:-1]))*0.65)*env(s,L,0.0006,4.5)
def drone(s,e,a0=0.10,a1=0.27):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.arange(i1-i0)/SR; d=np.zeros(i1-i0)
    for fq,a in [(38.9,1.0),(58.3,0.5),(77.8,0.3),(116.5,0.12)]:
        d+=a*np.sin(2*np.pi*fq*lt)*(1+0.07*np.sin(2*np.pi*0.29*lt))
    d/=1.9; ramp=a0+(a1-a0)*np.linspace(0,1,i1-i0)
    fade=np.clip(lt/0.5,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(0.4*SR),0,1)
    mix[i0:i1]+=ramp*d*fade
def riser(s,e,amp=0.24):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.linspace(0,1,i1-i0)
    sw=np.sin(2*np.pi*(180+1000*lt**2)*np.arange(i1-i0)/SR)
    mix[i0:i1]+=amp*(rng.normal(0,1,i1-i0)*0.3+sw*0.7)*(lt**2.3)
def tone_(s,e,fq=77.8,amp=0.12):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.arange(i1-i0)/SR
    sig=np.sin(2*np.pi*fq*lt)*0.6+np.sin(2*np.pi*fq*1.5*lt)*0.22
    fade=np.clip(lt/0.7,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(1.0*SR),0,1)
    mix[i0:i1]+=amp*sig*fade

hit(0.0,115,28,2.0,1.0,0.07); drone(0.0,STACK0/FPS+0.5,0.09,0.29)
for j,cf in enumerate(CUTS[1:],1):
    hit(cf/FPS,88,32,0.8,0.40+0.06*j,0.04); tick(cf/FPS,0.20+0.02*j,tone=1400+90*j)
riser((CUTS[-1]-22)/FPS,CUTS[-1]/FPS,0.20)          # into Napoleon
riser((STROBE0-30)/FPS,STROBE0/FPS,0.26)            # into the strobe
hit(STROBE0/FPS,125,29,1.4,1.0,0.045)
for j in range(6): tick((STROBE0+j*STROBE_F)/FPS,0.32,L=0.06,tone=2400+110*j)
hit(STACK0/FPS,135,26,2.4,1.0,0.06)                 # the stacked gaze
tone_(CARD0/FPS,DUR,77.8,0.13)
mix-=mix.mean(); pk=np.max(np.abs(mix))
mix=np.tanh(mix/max(pk,1e-9)*1.4)*0.92
mix*=np.clip(np.arange(N)/(0.004*SR),0,1)*np.clip((N-np.arange(N))/(0.05*SR),0,1)
st=np.stack([mix,mix*0.985],axis=1)
with wave.open("/home/user/Tik-Tok/build/conq.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print(f"conq.wav {DUR:.2f}s")
