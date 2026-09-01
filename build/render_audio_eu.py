"""THE LONG LOOK - guide bed (11.47s). Impacts sit exactly on the picture cuts so a real
track can be lined up by ear. 120 BPM reference grid."""
import numpy as np, wave
SR, FPS = 48000, 30
HOLDS = [38,22,22,19,19,15,15,11,11,8,8,8]
starts, f = [], 0
for d in HOLDS: starts.append(f); f += d
STROBE0 = f; HOLD0 = STROBE0 + 12*3; FADE0 = HOLD0 + 29; CARD0 = FADE0 + 9; NF = CARD0 + 74
DUR = NF/FPS
N = int(SR*DUR); t = np.arange(N)/SR
rng = np.random.default_rng(3); mix = np.zeros(N)

def env(s, L, atk=0.002, p=2.2):
    e = np.zeros(N); i0=int(s*SR); i1=min(int((s+L)*SR), N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(atk*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:]=(1-np.linspace(0,1,n-a))**p
    e[i0:i1]=seg; return e

def hit(s, f0=92, f1=32, L=1.2, amp=0.9, glide=0.05):
    i0=int(s*SR); i1=min(int((s+L)*SR), N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; fr=f1+(f0-f1)*np.exp(-lt/glide)
    mix[i0:i1]+=amp*np.sin(2*np.pi*np.cumsum(fr)/SR)*env(s,L,0.001,2.6)[i0:i1]

def tick(s, amp=0.4, L=0.10, tone=2200):
    nz=rng.normal(0,1,N); b=np.sin(2*np.pi*tone*t)*0.3+nz*0.7
    mix[:]+=amp*(b*0.35+np.concatenate(([0],b[:-1]))*0.65)*env(s,L,0.0006,4.5)

def drone(s, e, a0=0.10, a1=0.26):
    i0,i1=int(s*SR),min(int(e*SR),N)
    lt=np.arange(i1-i0)/SR; d=np.zeros(i1-i0)
    for fq,a in [(43.7,1.0),(65.4,0.5),(87.3,0.28),(130.8,0.12)]:
        d+=a*np.sin(2*np.pi*fq*lt)*(1+0.07*np.sin(2*np.pi*0.31*lt))
    d/=1.9
    ramp=a0+(a1-a0)*np.linspace(0,1,i1-i0)
    fade=np.clip(lt/0.5,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(0.4*SR),0,1)
    mix[i0:i1]+=ramp*d*fade

def riser(s, e, amp=0.24):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.linspace(0,1,i1-i0)
    sw=np.sin(2*np.pi*(200+1100*lt**2)*np.arange(i1-i0)/SR)
    mix[i0:i1]+=amp*(rng.normal(0,1,i1-i0)*0.3+sw*0.7)*(lt**2.3)

def tone_(s, e, fq=87.3, amp=0.12):
    i0,i1=int(s*SR),min(int(e*SR),N); lt=np.arange(i1-i0)/SR
    sig=np.sin(2*np.pi*fq*lt)*0.6+np.sin(2*np.pi*fq*1.5*lt)*0.22
    fade=np.clip(lt/0.7,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(1.0*SR),0,1)
    mix[i0:i1]+=amp*sig*fade

hit(0.0, 110, 30, 2.0, 1.0, 0.07)                      # frame one
drone(0.0, HOLD0/FPS + 0.6, 0.09, 0.28)
for j, sf in enumerate(starts[1:], start=1):            # a hit on every cut, escalating
    hit(sf/FPS, 86, 33, 0.7, 0.34 + 0.045*j, 0.035)
    tick(sf/FPS, 0.18 + 0.02*j, tone=1500+70*j)
riser(starts[-1]/FPS, STROBE0/FPS, 0.26)
hit(STROBE0/FPS, 120, 30, 1.6, 1.0, 0.045)              # the strobe lands
for j in range(12):
    tick((STROBE0 + j*3)/FPS, 0.30, L=0.055, tone=2600+90*j)
hit(HOLD0/FPS, 130, 27, 2.6, 1.0, 0.06)                 # the last face
tone_(CARD0/FPS, DUR, 87.3, 0.13)

mix -= mix.mean(); pk = np.max(np.abs(mix))
mix = np.tanh(mix/max(pk,1e-9)*1.4)*0.92
mix *= np.clip(np.arange(N)/(0.004*SR),0,1) * np.clip((N-np.arange(N))/(0.05*SR),0,1)
st = np.stack([mix, mix*0.985], axis=1)
with wave.open("/home/user/Tik-Tok/build/longlook.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print(f"wrote longlook.wav {DUR:.2f}s  cuts at frames {starts} strobe@{STROBE0} hold@{HOLD0}")
