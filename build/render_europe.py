"""THE LONG LOOK - 11.2s, 1080x1920 @30fps.
Twelve European faces across ~2,100 years, match-cut with the EYES locked to one point on
screen, accelerating into a strobe. No text until the end card. Grid: 120 BPM (beat 0.5s).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os, math, json, subprocess

SP  = "/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad"
HI  = f"{SP}/hi"
OUT = "/home/user/Tik-Tok/build/frames_eu"
W, H, FPS = 1080, 1920, 30
EYE_X, EYE_Y, IOD_F, ZMAX = 0.50, 0.40, 0.26, 1.09
os.makedirs(OUT, exist_ok=True)
FONT_S = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LOGO_TEXT, LOGO_URL = "VERBAVIA", "verbavia.com"

EYES = json.load(open(f"{SP}/eyes.json"))
# (key, scale adj) in chronological order
CHAIN = [
 ("01_ptolemy", 1.14), ("02_augustus", 1.06), ("05_fayum_red", 1.00),
 ("04_eutyches", 0.98), ("06_caracalla", 0.96), ("07_constantine", 1.00),
 ("08_joseph", 1.32), ("09_carthusian", 0.94), ("10_woman", 1.00),
 ("11_bronzino", 1.14), ("13_daguerreotype", 1.06), ("14_maniglier", 1.12),
]

# ---- cut list, in frames: accelerating, then a strobe through all twelve ----
HOLDS = [38, 22, 22, 19, 19, 15, 15, 11, 11, 8, 8, 8]     # 196f = 6.53s
STROBE_F, HOLD_F, FADE_F = 3, 29, 9                        # strobe 36f, hold, fade
CUTS = []                                                  # (start_f, end_f, chain_idx)
f = 0
for i, d in enumerate(HOLDS):
    CUTS.append((f, f+d, i)); f += d
STROBE0 = f
for i in range(len(CHAIN)):
    CUTS.append((f, f+STROBE_F, i)); f += STROBE_F
HOLD0 = f
CUTS.append((f, f+HOLD_F, len(CHAIN)-1)); f += HOLD_F
FADE0 = f; f += FADE_F
CARD0 = f
N = CARD0 + 74                                             # 2.47s end card
TOTAL = N/FPS

# ---- build one oversampled, eye-aligned base per face (12 resizes total) ----
def build_base(key, adj, zmax=ZMAX):
    e = EYES[key]
    im = Image.open(f"{HI}/{key}.jpg").convert("RGB")
    iw, ih = im.size
    BW, BH = int(W*zmax), int(H*zmax)
    scale = (IOD_F*W)/max(e["iod"]*iw, 1e-6) * adj * zmax
    # guarantee the frame is covered - no black edges
    scale = max(scale, BW/iw*1.002, BH/ih*1.002)
    nw, nh = max(int(iw*scale), 2), max(int(ih*scale), 2)
    im = im.resize((nw, nh), Image.LANCZOS, reducing_gap=3.0)
    ex, ey = e["eye_cx"]*nw, e["eye_cy"]*nh
    left, top = ex - EYE_X*BW, ey - EYE_Y*BH
    left = min(max(left, 0), max(nw-BW, 0)); top = min(max(top, 0), max(nh-BH, 0))
    return im.crop((int(left), int(top), int(left+BW), int(top+BH)))

ZOPEN = 2.80          # face 0 is oversampled deep so the film can open inside the eye
print("building aligned bases...")
BASES = {}
for j, (k, a) in enumerate(CHAIN):
    zm = ZOPEN if j == 0 else ZMAX
    BASES[k] = (build_base(k, a, zm), zm)

def framed(idx, zoom):
    b, zm = BASES[CHAIN[idx][0]]
    BWi, BHi = int(W*zm), int(H*zm)
    zoom = min(zoom, zm)
    ww, wh = W*zm/zoom, H*zm/zoom
    lx = EYE_X*W*zm*(1 - 1/zoom); ty = EYE_Y*H*zm*(1 - 1/zoom)
    lx = min(max(lx, 0), BWi-ww); ty = min(max(ty, 0), BHi-wh)
    return b.crop((int(lx), int(ty), int(lx+ww), int(ty+wh))).resize((W, H), Image.LANCZOS)

# ---- look ----
def vignette(w, h, strength=0.72, radius=0.90, cy=0.40):
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt(((x-w/2)/(w*0.62))**2 + ((y-h*cy)/(h*0.52))**2)/radius
    return np.clip(1.0 - strength*np.clip(d-0.42, 0, None)**1.5, 0.05, 1)[..., None]
VIG = vignette(W, H)

def grade(a):
    a = a.astype(np.float32)/255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = lum[..., None] + (a - lum[..., None])*0.74          # keep marble/skin warmth
    a = (a-0.5)*1.30 + 0.44
    a = np.clip(a, 0, 1)
    a[..., 2] += 0.085*(1-a[..., 2])**2.3                   # cold shadow
    a[..., 0] += 0.070*(a[..., 0]**1.4)                     # warm highlight
    a[..., 1] += 0.020*(a[..., 1]**1.6)
    return np.clip(a, 0, 1)

def lspace(d, xy, text, font, fill, sp=0):
    ws = [d.textlength(c, font=font) for c in text]
    x = xy[0] - (sum(ws)+sp*(len(text)-1))/2
    for c, cw in zip(text, ws):
        d.text((x, xy[1]), c, font=font, fill=fill); x += cw + sp

def card_layer():
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    d.rectangle([W*0.36, H*0.443, W*0.64, H*0.443+1], fill=(235,230,218,110))
    lspace(d, (W/2, H*0.478), LOGO_TEXT, ImageFont.truetype(FONT_S, 68), (250,247,240,255), sp=13)
    lspace(d, (W/2, H*0.478+104), LOGO_URL, ImageFont.truetype(FONT_N, 31), (238,233,222,205), sp=9)
    return L
CARD = card_layer()

# ---- render ----
rng = np.random.default_rng(5)
MP4 = "/home/user/Tik-Tok/build/LONGLOOK_silent.mp4"
print(f"rendering {N} frames ({TOTAL:.2f}s) -> {MP4}", flush=True)
ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
    "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-c:v","libx264","-profile:v","high",
    "-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",MP4], stdin=subprocess.PIPE)
QC = {0, 6, 14, 24, 37, 55, 90, 130, 165, 190, 205, 225, 250, 268, 285, 320}

for i in range(N):
    if i >= CARD0 or FADE0 <= i < CARD0:
        arr = np.zeros((H, W, 3), dtype=np.float32)
        if FADE0 <= i < CARD0:                     # fade the last face out
            k = 1.0 - (i-FADE0)/FADE_F
            seg = next(c for c in CUTS if c[0] <= FADE0-1 < c[1])
            arr = grade(np.asarray(framed(seg[2], 1.06)))*VIG*k
    else:
        seg = next(c for c in CUTS if c[0] <= i < c[1])
        s, e, idx = seg
        lt = (i-s)/max(e-s, 1)
        if i >= STROBE0:                            # strobe: no push, punchier
            zoom = 1.045
        elif s == 0:                                # open inside the eye, pull back
            k = lt*lt*(3-2*lt)
            zoom = ZOPEN + (1.0-ZOPEN)*k
        else:
            zoom = 1.0 + 0.075*lt
        arr = grade(np.asarray(framed(idx, zoom)))
        arr *= (1.0 + 0.016*math.sin(i*0.9) + rng.normal(0, 0.004))
        arr += rng.normal(0, 0.015, arr.shape).astype(np.float32)*(0.35+0.65*(1-arr))
        arr *= VIG
    frame = Image.fromarray((np.clip(arr, 0, 1)*255).astype(np.uint8))
    if i >= CARD0:
        a = min((i-CARD0)/12.0, 1.0)
        l = CARD.copy(); l.putalpha(l.split()[3].point(lambda p: int(p*a)))
        frame.paste(l, (0,0), l)
    if i in QC: frame.save(f"{OUT}/qc_{i:04d}.png")
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); ff.wait()
print(f"done -> {MP4}  ({N} frames, {TOTAL:.2f}s)")
