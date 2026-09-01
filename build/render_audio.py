"""UNREAD - opener sound design (0.0-4.5s). No licensed music: fully synthesized bed."""
import numpy as np, wave, struct

SR, DUR = 48000, 4.50
N = int(SR*DUR)
t = np.arange(N)/SR
rng = np.random.default_rng(11)
mix = np.zeros(N, dtype=np.float64)

def env(start, length, attack=0.002, decay=None, power=2.2):
    """Exponential-ish AD envelope as a full-length array."""
    e = np.zeros(N)
    i0 = int(start*SR); i1 = min(int((start+length)*SR), N)
    if i1 <= i0: return e
    n = i1-i0
    a = max(int(attack*SR), 1)
    seg = np.ones(n)
    seg[:a] = np.linspace(0, 1, a)
    d = np.linspace(0, 1, n-a) if n > a else np.array([])
    if len(d): seg[a:] = (1-d)**power
    e[i0:i1] = seg
    return e

def sub_hit(start, f0=58, f1=34, length=1.1, amp=0.9, glide=0.09):
    """Deep impact with a downward pitch glide."""
    i0 = int(start*SR); i1 = min(int((start+length)*SR), N)
    if i1 <= i0: return
    lt = np.arange(i1-i0)/SR
    f = f1 + (f0-f1)*np.exp(-lt/glide)
    ph = 2*np.pi*np.cumsum(f)/SR
    mix[i0:i1] += amp*np.sin(ph)*env(start, length, 0.001, power=2.6)[i0:i1]

def transient(start, amp=0.5, length=0.16, tone=1800):
    """Dry percussive tick - filtered noise + short body."""
    e = env(start, length, 0.0008, power=4.0)
    nz = rng.normal(0, 1, N)
    b = np.sin(2*np.pi*tone*t)*0.25 + nz*0.75
    # cheap one-pole lowpass
    y = np.zeros(N); a = 0.35
    for _ in range(1):
        y = b*a + np.concatenate(([0], b[:-1]))*(1-a)
    mix[:] += amp*y*e

def kick(start, amp=0.85):
    sub_hit(start, f0=120, f1=44, length=0.55, amp=amp, glide=0.028)
    transient(start, amp=0.16, length=0.05, tone=2600)

def drone(start, end, amp=0.16):
    i0, i1 = int(start*SR), min(int(end*SR), N)
    lt = np.arange(i1-i0)/SR
    d = np.zeros(i1-i0)
    for f, a in [(41.2, 1.0), (61.8, 0.55), (82.4, 0.30), (123.5, 0.12)]:
        lfo = 1 + 0.08*np.sin(2*np.pi*(0.23+f*0.003)*lt)
        d += a*np.sin(2*np.pi*f*lt)*lfo
    d /= 2.0
    fade = np.clip(lt/0.35, 0, 1)*np.clip((i1-i0-np.arange(i1-i0))/(0.2*SR), 0, 1)
    mix[i0:i1] += amp*d*fade

def crackle(amp=0.055, rate=140):
    """Sparse wax-cylinder pops + hiss floor."""
    n_pops = int(rate*DUR)
    idx = rng.integers(0, N-64, n_pops)
    for i in idx:
        L = rng.integers(6, 40)
        mix[i:i+L] += amp*rng.normal(0, 1, L)*np.linspace(1, 0, L)**2
    mix[:] += 0.006*rng.normal(0, 1, N)

def riser(start, end, amp=0.20):
    i0, i1 = int(start*SR), min(int(end*SR), N)
    lt = np.linspace(0, 1, i1-i0)
    nz = rng.normal(0, 1, i1-i0)
    # rising band-ish noise via modulated amplitude + upward sine sweep
    sweep = np.sin(2*np.pi*(180+900*lt**2)*np.arange(i1-i0)/SR)
    mix[i0:i1] += amp*(nz*0.35 + sweep*0.65)*(lt**2.4)

# ---- arrangement --------------------------------------------------------
crackle()
sub_hit(0.00, f0=70, f1=32, length=1.5, amp=1.0)   # frame-one impact
transient(0.00, amp=0.55)
for b in (0.50, 0.90, 1.20):                       # the three folio cuts
    transient(b, amp=0.42, tone=1400)
    sub_hit(b, f0=54, f1=36, length=0.35, amp=0.30)
transient(1.50, amp=0.30, tone=900)
sub_hit(1.80, f0=48, f1=30, length=0.9, amp=0.35)  # swell under the hook line
riser(1.90, 2.50, amp=0.22)                        # build into the cut

mix[int(2.50*SR):int(2.60*SR)] = 0.0               # hard silence on the black flash

drone(2.60, 4.50, amp=0.19)                        # the bed enters
for k in (2.60, 3.457, 4.314):                     # 70 bpm
    kick(k, amp=0.85 if k == 2.60 else 0.62)

# ---- master -------------------------------------------------------------
mix -= mix.mean()
peak = np.max(np.abs(mix))
mix = np.tanh(mix/max(peak, 1e-9)*1.35)*0.92       # soft clip / glue
mix *= np.clip(np.arange(N)/(0.004*SR), 0, 1)      # de-click head
mix *= np.clip((N-np.arange(N))/(0.02*SR), 0, 1)

stereo = np.stack([mix, mix], axis=1)
stereo[:, 0] *= 1.0; stereo[:, 1] *= 0.985          # hair of width
pcm = (np.clip(stereo, -1, 1)*32767).astype(np.int16)

with wave.open("/home/user/Tik-Tok/build/opener.wav", "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote opener.wav  {DUR}s  peak={peak:.2f}")
