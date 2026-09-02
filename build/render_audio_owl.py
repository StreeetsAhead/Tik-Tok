"""Running-gag guide bed. Normal beats: ticks + taps. Owl entries: a 60ms hard mute, then an
ABRUPT sting (noise burst + inharmonic screech + sub drop), escalating across the three."""
import numpy as np, wave
SR,FPS=48000,30; NF=540; DUR=NF/FPS; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(21); mix=np.zeros(N)
def env(s,L,atk=0.002,p=2.4):
    e=np.zeros(N); i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(atk*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:]=(1-np.linspace(0,1,n-a))**p
    e[i0:i1]=seg; return e
def tap(s,f0=200,amp=0.5,L=0.22,g=0.02):
    i0=int(s*SR); i1=min(int((s+L)*SR),N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; fr=f0*0.55+f0*0.45*np.exp(-lt/g)
    mix[i0:i1]+=amp*np.sin(2*np.pi*np.cumsum(fr)/SR)*env(s,L,0.001,3.0)[i0:i1]
def tick(s,amp=0.25,tone=3200,L=0.05):
    nz=rng.normal(0,1,N); b=np.sin(2*np.pi*tone*t)*0.5+nz*0.5; mix[:]+=amp*b*env(s,L,0.0004,5.0)
def pop(s,amp=0.35,f=900):
    i0=int(s*SR); i1=min(int((s+0.09)*SR),N); lt=np.arange(i1-i0)/SR
    mix[i0:i1]+=amp*np.sin(2*np.pi*(f*np.exp(-lt/0.03))*lt)*env(s,0.09,0.0005,3)[i0:i1]
def sting(s,level):
    """level 1..3. Zero attack. Everything starts on the same sample."""
    amp=[0,0.55,0.8,1.0][level]
    # hard mute 60 ms before
    i0=int((s-0.06)*SR); mix[max(i0,0):int(s*SR)]=0.0
    L=[0,0.9,1.4,2.2][level]; i1=min(int((s+L)*SR),N); n=i1-int(s*SR); lt=np.arange(n)/SR
    e=(1-np.clip(lt/L,0,1))**2.2
    seg=np.zeros(n)
    seg+=rng.normal(0,1,n)*e*0.55                                     # noise burst
    for k,f in enumerate([1130,1370,1790,2210,2860,3410][:3+level]):   # inharmonic screech
        seg+=np.sin(2*np.pi*f*lt+rng.random()*6.28)*np.exp(-lt/(0.22+0.05*level))*0.35
    fr=28+(110-28)*np.exp(-lt/0.08); seg+=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-lt/0.6)*1.2  # sub drop
    if level>=2:                                                       # drone + heartbeat
        d=np.sin(2*np.pi*36*lt)+0.5*np.sin(2*np.pi*54.3*lt); d*=1+0.2*np.sin(2*np.pi*(0.7+0.4*level)*lt)
        seg+=d*0.35*np.clip(lt/0.2,0,1)
        bpm=[0,0,70,118][level]; per=60/bpm
        for b in np.arange(0.25,L,per):
            j=int(b*SR); k=min(j+int(0.25*SR),n); ll=np.arange(k-j)/SR
            seg[j:k]+=np.sin(2*np.pi*(45+30*np.exp(-ll/0.03))*ll)*np.exp(-ll/0.09)*0.7
    if level==3:                                                       # high whine with vibrato
        seg+=np.sin(2*np.pi*3200*lt+8*np.sin(2*np.pi*6*lt))*0.12*np.clip(lt/0.3,0,1)*(1-np.clip((lt-L+0.3)/0.3,0,1))
    mix[int(s*SR):i1]+=amp*seg
    mix[int(s*SR):int(s*SR)+int(0.004*SR)]*=np.linspace(1,1,int(0.004*SR))    # keep the hard edge

# timeline (s): owl1 0.0-2.2 | r1 2.2-5.4 | owl2 5.4-8.0 | r2 8.0-11.2 | owl3 11.2-15.0 | out 15.0-18.0
sting(0.0,1)
for s in np.arange(2.2,5.4,1.0): tick(s,0.22)
tap(2.2,210,0.5); [pop(2.2+f/FPS) for f in (40,48,56)]
sting(5.4,2)
for s in np.arange(8.0,11.2,1.0): tick(s,0.26,2600)
tap(8.0,210,0.5); [pop(8.0+f/FPS) for f in (44,52,60)]
for f in (30,36,42,48,54): tick(8.0+f/FPS,0.15,3100)
sting(11.2,3)
# outro: cut to silence then a clean tap + pop on the pill
mix[int(15.0*SR)-int(0.06*SR):int(15.0*SR)]=0
tap(15.0,220,0.5); tap(15.0+30/FPS,320,0.45,0.3)
mix-=mix.mean(); pk=np.max(np.abs(mix)); mix=np.tanh(mix/max(pk,1e-9)*1.3)*0.9
mix*=np.clip((N-np.arange(N))/(0.04*SR),0,1)
st=np.stack([mix,mix*0.99],axis=1)
with wave.open("/home/user/Tik-Tok/build/owl.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print("owl.wav",DUR)
