"""Promo guide bed: soft UI taps on scene changes, ticks on checks, pop on the pill."""
import numpy as np, wave
SR,FPS=48000,30; NF=675; DUR=NF/FPS; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(6); mix=np.zeros(N)
def env(s,L,atk=0.002,p=2.4):
    e=np.zeros(N); i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(atk*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:]=(1-np.linspace(0,1,n-a))**p
    e[i0:i1]=seg; return e
def tap(s,f0=210,amp=0.5,L=0.22):
    i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; fr=f0*0.55+f0*0.45*np.exp(-lt/0.02)
    mix[i0:i1]+=amp*np.sin(2*np.pi*np.cumsum(fr)/SR)*env(s,L,0.001,3.0)[i0:i1]
def tick(s,amp=0.30,tone=2900,L=0.06):
    nz=rng.normal(0,1,N); b=np.sin(2*np.pi*tone*t)*0.45+nz*0.55
    mix[:]+=amp*b*env(s,L,0.0005,5.0)
def whoosh(s,L=0.5,amp=0.22):
    i0,i1=int(s*SR),min(int((s+L)*SR),N)
    lt=np.linspace(0,1,i1-i0); nz=rng.normal(0,1,i1-i0)
    y=nz*0.5+np.concatenate(([0],nz[:-1]))*0.5
    mix[i0:i1]+=amp*y*np.sin(np.pi*lt)**1.5

tap(0.0,180,0.6)
for f,fr in [(24,2600)]: tick(f/FPS,0.22,fr)            # underline
for sf in [90,225,360,495]: tap(sf/FPS,200,0.55)
for f in [44+90,52+90]: tick(f/FPS,0.24,2200)           # X strokes
tick((225+42)/FPS,0.22,2500)                             # circle
for f in [30,40,50,60,64]: tick((360+f)/FPS,0.16,3100)  # counter ticks
tick((360+70)/FPS,0.30,2400)                             # passed check
whoosh(495/FPS-0.15,0.55,0.26)                           # wipe
for f in [66,76,86]: tick((495+f)/FPS,0.26,2600)         # check rows
tap((495+126)/FPS,320,0.45,0.30)                         # pill pop
mix-=mix.mean(); pk=np.max(np.abs(mix))
mix=np.tanh(mix/max(pk,1e-9)*1.2)*0.85
mix*=np.clip(np.arange(N)/(0.003*SR),0,1)*np.clip((N-np.arange(N))/(0.04*SR),0,1)
st=np.stack([mix,mix*0.99],axis=1)
with wave.open("/home/user/Tik-Tok/build/promo.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print("promo.wav",DUR)
