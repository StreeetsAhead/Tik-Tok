"""Fast-list guide bed: clock tick every second, tap per reason, horror sting + heartbeat under the owl."""
import numpy as np, wave
SR,FPS=48000,30; NF=690; DUR=NF/FPS; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(8); mix=np.zeros(N)
def env(s,L,atk=0.002,p=2.4):
    e=np.zeros(N); i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(atk*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:]=(1-np.linspace(0,1,n-a))**p
    e[i0:i1]=seg; return e
def tap(s,f0=210,amp=0.5,L=0.22,g=0.02):
    i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; fr=f0*0.55+f0*0.45*np.exp(-lt/g)
    mix[i0:i1]+=amp*np.sin(2*np.pi*np.cumsum(fr)/SR)*env(s,L,0.001,3.0)[i0:i1]
def tick(s,amp=0.25,tone=3200,L=0.05):
    nz=rng.normal(0,1,N); b=np.sin(2*np.pi*tone*t)*0.5+nz*0.5
    mix[:]+=amp*b*env(s,L,0.0004,5.0)
def whoosh(s,L=0.5,amp=0.22):
    i0,i1=int(s*SR),min(int((s+L)*SR),N); lt=np.linspace(0,1,i1-i0); nz=rng.normal(0,1,i1-i0)
    mix[i0:i1]+=amp*(nz*0.5+np.concatenate(([0],nz[:-1]))*0.5)*np.sin(np.pi*lt)**1.5
def drone(s,e,amp=0.22):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.arange(i1-i0)/SR
    d=np.sin(2*np.pi*36*lt)+0.5*np.sin(2*np.pi*54.3*lt)+0.25*np.sin(2*np.pi*72*lt)
    d*=1+0.15*np.sin(2*np.pi*0.7*lt)
    fade=np.clip(lt/0.3,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(0.25*SR),0,1)
    mix[i0:i1]+=amp*d/1.75*fade
for s in range(0,20): tick(s+0.0,0.22 if s<15 else 0.34, 3200 if s<15 else 2400)     # the clock
for k in range(9): tap(k*2.2,190 if k<8 else 70,0.5 if k<8 else 0.9,0.25 if k<8 else 0.9)
tap(17.6,55,1.0,1.4,0.06); drone(17.6,20.0,0.24)                                     # owl sting + drone
for b in np.arange(17.9,20.0,0.62): tap(b,62,0.55,0.3,0.03); tap(b+0.17,58,0.35,0.25,0.03)  # heartbeat
whoosh(19.85,0.55,0.26); tap(20.0,200,0.5); tap(20.0+24/FPS,320,0.45,0.3)
mix-=mix.mean(); pk=np.max(np.abs(mix)); mix=np.tanh(mix/max(pk,1e-9)*1.25)*0.88
mix*=np.clip(np.arange(N)/(0.003*SR),0,1)*np.clip((N-np.arange(N))/(0.04*SR),0,1)
st=np.stack([mix,mix*0.99],axis=1)
with wave.open("/home/user/Tik-Tok/build/fast.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print("fast.wav",DUR)
