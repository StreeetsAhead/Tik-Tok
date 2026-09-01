"""UNREAD - full sound bed (31.5s), 80 BPM. Guide track: fully synthesized, no licensing."""
import numpy as np, wave

SR, DUR, BEAT = 48000, 31.5, 0.75
N = int(SR*DUR); t = np.arange(N)/SR
rng = np.random.default_rng(11)
mix = np.zeros(N)

def env(start, length, attack=0.002, power=2.2):
    e = np.zeros(N); i0=int(start*SR); i1=min(int((start+length)*SR), N)
    if i1<=i0: return e
    n=i1-i0; a=max(int(attack*SR),1); seg=np.ones(n); seg[:a]=np.linspace(0,1,a)
    if n>a: seg[a:] = (1-np.linspace(0,1,n-a))**power
    e[i0:i1]=seg; return e

def sub_hit(start, f0=58, f1=34, length=1.1, amp=0.9, glide=0.09):
    i0=int(start*SR); i1=min(int((start+length)*SR), N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR
    f=f1+(f0-f1)*np.exp(-lt/glide)
    mix[i0:i1] += amp*np.sin(2*np.pi*np.cumsum(f)/SR)*env(start,length,0.001,2.6)[i0:i1]

def transient(start, amp=0.5, length=0.16, tone=1800):
    e=env(start,length,0.0008,4.0); nz=rng.normal(0,1,N)
    b=np.sin(2*np.pi*tone*t)*0.25+nz*0.75
    y=b*0.35+np.concatenate(([0],b[:-1]))*0.65
    mix[:] += amp*y*e

def kick(start, amp=0.8):
    sub_hit(start, 120, 44, 0.55, amp, 0.028); transient(start, amp*0.18, 0.05, 2600)

def drone(start, end, a0=0.12, a1=0.30):
    i0,i1=int(start*SR),min(int(end*SR),N)
    if i1<=i0: return
    lt=np.arange(i1-i0)/SR; ramp=a0+(a1-a0)*np.linspace(0,1,i1-i0)
    d=np.zeros(i1-i0)
    for f,a in [(41.2,1.0),(61.8,0.55),(82.4,0.30),(123.5,0.14),(164.8,0.07)]:
        d += a*np.sin(2*np.pi*f*lt)*(1+0.08*np.sin(2*np.pi*(0.23+f*0.003)*lt))
    d/=2.0
    fade=np.clip(lt/0.4,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(0.5*SR),0,1)
    mix[i0:i1] += ramp*d*fade

def riser(start, end, amp=0.20):
    i0,i1=int(start*SR),min(int(end*SR),N)
    if i1<=i0: return
    lt=np.linspace(0,1,i1-i0)
    sweep=np.sin(2*np.pi*(180+900*lt**2)*np.arange(i1-i0)/SR)
    mix[i0:i1] += amp*(rng.normal(0,1,i1-i0)*0.35+sweep*0.65)*(lt**2.4)

def crackle(amp=0.05, rate=140):
    for i in rng.integers(0, N-64, int(rate*DUR)):
        L=rng.integers(6,40)
        mix[i:i+L] += amp*rng.normal(0,1,L)*np.linspace(1,0,L)**2
    mix[:] += 0.006*rng.normal(0,1,N)

def tone(start, end, f=110.0, amp=0.10):
    i0,i1=int(start*SR),min(int(end*SR),N)
    lt=np.arange(i1-i0)/SR
    sig=np.sin(2*np.pi*f*lt)*0.6+np.sin(2*np.pi*f*1.5*lt)*0.25+np.sin(2*np.pi*f*0.5*lt)*0.5
    fade=np.clip(lt/0.8,0,1)*np.clip((i1-i0-np.arange(i1-i0))/(1.2*SR),0,1)
    mix[i0:i1] += amp*sig*fade

CARDS = [4.50, 9.00, 13.50, 18.00, 22.50]
TURN  = 27.00

crackle()
# --- opener
sub_hit(0.00, 70, 32, 1.5, 1.00); transient(0.00, 0.55)
for b in (0.50, 0.90, 1.20):
    transient(b, 0.42, tone=1400); sub_hit(b, 54, 36, 0.35, 0.30)
transient(1.50, 0.30, tone=900)
sub_hit(1.80, 48, 30, 0.9, 0.35)
riser(1.95, 2.90, 0.22)
mix[int(2.90*SR):int(3.00*SR)] = 0.0

# --- countdown body
drone(3.00, TURN, a0=0.11, a1=0.32)
for c in CARDS:
    sub_hit(c, 96, 33, 1.3, 0.92)          # card impact
    transient(c, 0.34, tone=1200)
    riser(c-0.75, c, 0.16)
# kick pattern escalates: every 2 beats, then every beat from card 3
b = 3.00
while b < 13.50:
    kick(b, 0.62); b += 2*BEAT
while b < TURN:
    kick(b, 0.50 if round((b/BEAT)) % 2 else 0.70); b += BEAT

# --- the turn
sub_hit(TURN, 110, 28, 2.4, 1.00); transient(TURN, 0.40, tone=800)
drone(TURN, 28.80, a0=0.30, a1=0.05)
mix[int(28.80*SR):int(29.10*SR)] = 0.0
tone(29.10, 31.50, f=82.4, amp=0.13)
sub_hit(30.15, 62, 30, 1.4, 0.34)          # under the logo

mix -= mix.mean()
peak = np.max(np.abs(mix))
mix = np.tanh(mix/max(peak,1e-9)*1.35)*0.92
mix *= np.clip(np.arange(N)/(0.004*SR), 0, 1)
mix *= np.clip((N-np.arange(N))/(0.05*SR), 0, 1)
st = np.stack([mix, mix*0.985], axis=1)
with wave.open("/home/user/Tik-Tok/build/full.wav","w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print(f"wrote full.wav {DUR}s peak={peak:.2f}")
