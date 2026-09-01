"""UNREAD - opening hook (0.0-4.5s). Renders 1080x1920 @30fps frame sequence."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os, math

SRC   = "/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad/src"
OUT   = "/home/user/Tik-Tok/build/frames"
W, H, FPS = 1080, 1920, 30
os.makedirs(OUT, exist_ok=True)

# shot: (source, cx, cy, width_frac, zoom_start, zoom_end, duration_s)
SHOTS = [
    ("f78r_hi", 0.62, 0.82, 0.40, 1.00, 1.10, 0.50),   # figures in the green pools - TIGHT
    ("f71r_hi", 0.42, 0.38, 0.52, 1.06, 1.00, 0.40),   # zodiac wheel
    ("f75r_hi", 0.33, 0.55, 0.42, 1.00, 1.08, 0.30),   # figures in the stream
    ("f33v_hi", 0.50, 0.60, 0.60, 1.05, 1.00, 0.30),   # plant that does not exist
    ("f78r_hi", 0.24, 0.32, 0.26, 1.00, 1.09, 1.10),   # the script itself - pure text column
    ("f78r_hi", 0.55, 0.60, 0.78, 1.00, 1.06, 1.90),   # pull wide, counter enters
]
FONT_S = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def ease(t):                      # smooth in/out
    return t*t*(3-2*t)

def load(name):
    return Image.open(f"{SRC}/{name}.jpg").convert("RGB")

CACHE = {n: load(n) for n in {s[0] for s in SHOTS}}

def vignette_mask(w, h, strength=0.62, radius=0.78):
    y, x = np.ogrid[0:h, 0:w]
    cx, cy = w/2, h/2
    d = np.sqrt(((x-cx)/(w/2))**2 + ((y-cy)/(h/2))**2) / (radius*1.414)
    m = 1.0 - strength*np.clip(d-0.35, 0, None)**1.8
    return np.clip(m, 0, 1)[..., None]

VIG = vignette_mask(W, H, strength=0.46, radius=0.95)

def letterspace(draw, xy, text, font, fill, sp=0, anchor_center=True):
    widths = [draw.textlength(c, font=font) for c in text]
    total  = sum(widths) + sp*(len(text)-1)
    x, y   = xy
    if anchor_center: x -= total/2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + sp
    return total

def text_layer(kind):
    """Returns RGBA overlay."""
    L = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(L)
    if kind == "hook":
        scrim = Image.new("RGBA", (W, H), (0,0,0,0))
        sd = ImageDraw.Draw(scrim)
        sd.ellipse([-W*0.35, H*0.60, W*1.35, H*1.02], fill=(0,0,0,168))
        L.alpha_composite(scrim.filter(ImageFilter.GaussianBlur(70)))
        f = ImageFont.truetype(FONT_S, 78)
        letterspace(d, (W/2, H*0.715), "Nobody has ever", f, (250,247,240,255), sp=3)
        letterspace(d, (W/2, H*0.715+96), "read this.", f, (250,247,240,255), sp=3)
    elif kind == "counter":
        fn = ImageFont.truetype(FONT_N, 156)
        letterspace(d, (W*0.855, H*0.075), "5", fn, (245,242,235,255), sp=0)
        fl = ImageFont.truetype(FONT_N, 26)
        letterspace(d, (W*0.855, H*0.075+150), "OF 5", fl, (245,242,235,190), sp=6)
        # progress bar
        bx0, bx1, by = W*0.08, W*0.92, H*0.055
        d.rectangle([bx0, by, bx1, by+4], fill=(245,242,235,60))
        d.rectangle([bx0, by, bx0+(bx1-bx0)*0.02, by+4], fill=(245,242,235,235))
    return L

LAYERS = {"hook": text_layer("hook"), "counter": text_layer("counter")}

def key_light(w, h, cy=0.45, r=1.35):
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt(((x-w/2)/(w*0.92))**2 + ((y-h*cy)/(h*0.82))**2) / r
    return np.clip(1.10 - 0.72*np.clip(d, 0, None)**1.35, 0.34, 1.10)[..., None]

KEY = None

def grade(arr):
    a = arr.astype(np.float32)/255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = lum[..., None] + (a - lum[..., None]) * 0.62      # heavy desaturate
    a = a * KEY                                           # candlelit falloff
    a = np.clip(a, 0, 1) * 0.88                           # pull exposure down
    a = (a - 0.5) * 1.24 + 0.46                           # crush + contrast
    a = np.clip(a, 0, 1)
    a[..., 2] += 0.075*(1-a[..., 2])**2.2                 # cold shadows
    a[..., 0] += 0.055*(a[..., 0]**1.5)                   # candle warmth in highlight
    a[..., 1] += 0.018*(a[..., 1]**1.6)
    return np.clip(a, 0, 1)

KEY = key_light(W, H)

# ---- render -------------------------------------------------------------
timeline, t0 = [], 0.0
for s in SHOTS:
    timeline.append((t0, t0+s[6], s)); t0 += s[6]
TOTAL = t0
N = int(round(TOTAL*FPS))
rng = np.random.default_rng(7)
print(f"total {TOTAL:.2f}s -> {N} frames")

for i in range(N):
    t = i/FPS
    for (a, b, s) in timeline:
        if a <= t < b or (b == TOTAL and t >= b): shot, la, lb = s, a, b; break
    name, cx, cy, wf, z0, z1, _ = shot
    im = CACHE[name]; IW, IH = im.size
    lt = ease(min(max((t-la)/(lb-la), 0), 1))
    zoom = z0 + (z1-z0)*lt
    cw = IW*wf/zoom; ch = cw*16/9
    if ch > IH: ch = IH; cw = ch*9/16
    x = min(max(cx*IW - cw/2, 0), IW-cw); y = min(max(cy*IH - ch/2, 0), IH-ch)
    fr = im.crop((int(x), int(y), int(x+cw), int(y+ch))).resize((W, H), Image.LANCZOS)

    arr = grade(np.asarray(fr))

    # candle flicker
    arr *= (1.0 + 0.018*math.sin(t*11.3) + 0.012*math.sin(t*27.7) + rng.normal(0, 0.004))
    # film grain
    arr += rng.normal(0, 0.016, arr.shape).astype(np.float32) * (0.35 + 0.65*(1-arr))
    arr *= VIG
    arr = np.clip(arr, 0, 1)

    frame = Image.fromarray((arr*255).astype(np.uint8))

    # 4-frame black flash before the counter beat (2.60s)
    if 2.50 <= t < 2.60:
        frame = Image.new("RGB", (W, H), (0,0,0))

    def blend(layer, alpha):
        if alpha <= 0: return
        l = layer.copy()
        al = l.split()[3].point(lambda p: int(p*alpha))
        l.putalpha(al)
        frame.paste(l, (0,0), l)

    if 1.80 <= t < 2.50:  blend(LAYERS["hook"], min((t-1.80)/0.22, 1.0))
    if t >= 2.60:         blend(LAYERS["counter"], min((t-2.60)/0.18, 1.0))

    frame.save(f"{OUT}/f{i:04d}.png")

print("frames written:", len(os.listdir(OUT)))
