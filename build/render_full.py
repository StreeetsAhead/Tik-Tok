"""UNREAD - full edit (0.0-31.5s), 1080x1920 @30fps.
Grid: 80 BPM, beat = 0.75s. Every cut lands on a beat; cards are 4.5s (6 beats).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os, math

VOY = "/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad/src"
WM  = "/tmp/claude-0/-home-user-Tik-Tok/6a0caed4-01c4-5934-8009-1cc90f821d97/scratchpad/wm"
OUT = "/home/user/Tik-Tok/build/frames_full"
W, H, FPS = 1080, 1920, 30
BEAT = 0.75
TOTAL = 31.5
os.makedirs(OUT, exist_ok=True)

FONT_S = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SB= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SRC = {
 "f78r": f"{VOY}/f78r_hi.jpg", "f71r": f"{VOY}/f71r_hi.jpg",
 "f75r": f"{VOY}/f75r_hi.jpg", "f33v": f"{VOY}/f33v_hi.jpg",
 "phaistos_a": f"{WM}/phaistos_a.jpg", "phaistos_b": f"{WM}/phaistos_b.jpg",
 "roro_champ": f"{WM}/roro_champ.jpg", "roro_chile": f"{WM}/roro_chile.jpg",
 "lineara":    f"{WM}/lineara_1.jpg",  "indus": f"{WM}/indus_eleph.jpg",
 "moai":       f"{WM}/moai_rano.jpg",
}
_cache = {}
def img(k):
    if k not in _cache:
        im = Image.open(SRC[k]).convert("RGB")
        if max(im.size) > 3600:
            s = 3600/max(im.size); im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
        _cache[k] = im
    return _cache[k]

# ---- shots: (start, end, key, cx, cy, width_frac, z0, z1, mode) ----------
SHOTS = [
 # OPENER
 (0.00, 0.50, "f78r", 0.62, 0.82, 0.40, 1.00, 1.10, "fill"),
 (0.50, 0.90, "f71r", 0.42, 0.38, 0.52, 1.06, 1.00, "fill"),
 (0.90, 1.20, "f75r", 0.33, 0.55, 0.42, 1.00, 1.08, "fill"),
 (1.20, 1.50, "f33v", 0.50, 0.60, 0.60, 1.05, 1.00, "fill"),
 (1.50, 3.00, "f78r", 0.24, 0.32, 0.26, 1.00, 1.09, "fill"),
 (3.00, 4.50, "f78r", 0.55, 0.60, 0.78, 1.00, 1.06, "fill"),
 # 5 PHAISTOS
 (4.50, 6.75, "phaistos_a", 0.50, 0.49, 0.34, 1.00, 1.12, "fill"),
 (6.75, 9.00, "phaistos_b", 0.50, 0.50, 1.00, 1.04, 1.00, "fit"),
 # 4 RONGORONGO
 (9.00, 11.25, "roro_chile", 0.46, 0.52, 0.32, 1.00, 1.11, "fill"),
 (11.25, 13.50, "moai",      0.50, 0.63, 0.50, 1.07, 1.00, "fill"),
 # 3 LINEAR A
 (13.50, 15.75, "lineara", 0.50, 0.52, 0.58, 1.00, 1.06, "fill"),
 (15.75, 18.00, "lineara", 0.44, 0.42, 0.30, 1.00, 1.12, "fill"),
 # 2 INDUS
 (18.00, 20.25, "indus", 0.50, 0.22, 0.30, 1.00, 1.10, "fill"),
 (20.25, 22.50, "indus", 0.50, 0.50, 1.00, 1.05, 1.00, "fit"),
 # 1 VOYNICH
 (22.50, 24.75, "f71r", 0.42, 0.38, 0.42, 1.00, 1.10, "fill"),
 (24.75, 28.80, "f78r", 0.24, 0.34, 0.28, 1.00, 1.14, "fill"),
]
CARD_STARTS = [4.50, 9.00, 13.50, 18.00, 22.50]
FLASH = [(s-0.067, s) for s in CARD_STARTS] + [(2.90, 3.00)]

# ---- cards --------------------------------------------------------------
CARDS = [
 dict(n=5, t0=4.50,  t1=9.00,  title="PHAISTOS DISC", sub="CRETE  ·  c.1700 BC", years="3,700",
      a=(4.95, 6.75, ["241 symbols, pressed", "into wet clay."]),
      b=(6.90, 9.00, ["There is only one.", "It is too short to ever crack."])),
 dict(n=4, t0=9.00,  t1=13.50, title="RONGORONGO", sub="EASTER ISLAND", years="160",
      a=(9.45, 11.25, ["Twenty-six wooden tablets."]),
      b=(11.40, 13.50, ["The last people who could", "read them died in the 1860s."])),
 dict(n=3, t0=13.50, t1=18.00, title="LINEAR A", sub="MINOAN CRETE  ·  c.1800 BC", years="3,500",
      a=(13.95, 15.75, ["We know how it sounds."]),
      b=(15.90, 18.00, ["We do not know", "what it means."])),
 dict(n=2, t0=18.00, t1=22.50, title="THE INDUS SCRIPT", sub="c.2600 BC", years="3,900",
      a=(18.45, 20.25, ["Five million people.", "Four thousand inscriptions."]),
      b=(20.40, 22.50, ["Average length:", "five characters."])),
 dict(n=1, t0=22.50, t1=27.00, title="THE VOYNICH MANUSCRIPT", sub="CARBON-DATED 1404–1438", years="600",
      a=(22.95, 24.75, ["It beat the cryptographers", "who broke PURPLE."]),
      b=(24.90, 27.00, ["Nobody knows if there is", "a language in it at all."])),
]
TURN_A = (27.15, 28.65, ["Some languages can", "never be learned."])
TURN_B = (29.10, 31.50, ["Yours isn\u2019t one of them."])
LOGO_T = 30.15
LOGO_TEXT = "VERBAVIA"          # wordmark - swap for the real logo PNG if you have one
LOGO_URL  = "verbavia.com"      # destination, held under the mark

# ---- look ---------------------------------------------------------------
def vignette_mask(w, h, strength=0.46, radius=0.95):
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt(((x-w/2)/(w/2))**2 + ((y-h/2)/(h/2))**2) / (radius*1.414)
    return np.clip(1.0 - strength*np.clip(d-0.35, 0, None)**1.8, 0, 1)[..., None]

def key_light(w, h, cy=0.45, r=1.35):
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt(((x-w/2)/(w*0.92))**2 + ((y-h*cy)/(h*0.82))**2) / r
    return np.clip(1.10 - 0.72*np.clip(d, 0, None)**1.35, 0.34, 1.10)[..., None]

VIG, KEY = vignette_mask(W, H), key_light(W, H)

def grade(a):
    a = a.astype(np.float32)/255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = lum[..., None] + (a - lum[..., None])*0.62
    a = a*KEY
    a = np.clip(a, 0, 1)*0.88
    a = (a-0.5)*1.24 + 0.46
    a = np.clip(a, 0, 1)
    a[..., 2] += 0.075*(1-a[..., 2])**2.2
    a[..., 0] += 0.055*(a[..., 0]**1.5)
    a[..., 1] += 0.018*(a[..., 1]**1.6)
    return np.clip(a, 0, 1)

def ease(t): return t*t*(3-2*t)

# ---- type ---------------------------------------------------------------
def lspace(d, xy, text, font, fill, sp=0, center=True):
    ws = [d.textlength(c, font=font) for c in text]
    total = sum(ws) + sp*(len(text)-1)
    x, y = xy
    if center: x -= total/2
    for c, cw in zip(text, ws):
        d.text((x, y), c, font=font, fill=fill); x += cw + sp
    return total

def scrim(L, top=0.56, alpha=176):
    s = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(s).ellipse([-W*0.35, H*top, W*1.35, H*1.06], fill=(0,0,0,alpha))
    L.alpha_composite(s.filter(ImageFilter.GaussianBlur(72)))

def body_layer(lines, size=70, y0=0.705):
    L = Image.new("RGBA", (W, H), (0,0,0,0))
    scrim(L, top=max(0.08, y0-0.17), alpha=190)
    d = ImageDraw.Draw(L); f = ImageFont.truetype(FONT_S, size)
    for i, ln in enumerate(lines):
        lspace(d, (W/2, H*y0 + i*(size*1.28)), ln, f, (250,247,240,255), sp=3)
    return L

def head_layer(title, sub):
    L = Image.new("RGBA", (W, H), (0,0,0,0))
    s = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(s).ellipse([-W*0.35, -H*0.10, W*1.35, H*0.34], fill=(0,0,0,150))
    L.alpha_composite(s.filter(ImageFilter.GaussianBlur(70)))
    d = ImageDraw.Draw(L)
    size = 62 if len(title) <= 18 else 48
    lspace(d, (W/2, H*0.175), title, ImageFont.truetype(FONT_SB, size), (252,250,245,255), sp=5)
    lspace(d, (W/2, H*0.175 + size + 26), sub, ImageFont.truetype(FONT_N, 27), (228,222,208,215), sp=7)
    return L

def hud_layer(numeral, years, fill_frac):
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    bx0, bx1, by = W*0.08, W*0.92, H*0.055
    d.rectangle([bx0, by, bx1, by+4], fill=(245,242,235,55))
    d.rectangle([bx0, by, bx0+(bx1-bx0)*fill_frac, by+4], fill=(245,242,235,235))
    lspace(d, (W*0.855, H*0.075), numeral, ImageFont.truetype(FONT_N, 156), (245,242,235,255))
    lspace(d, (W*0.855, H*0.075+178), "OF 5", ImageFont.truetype(FONT_N, 24), (245,242,235,180), sp=6)
    if years:
        f  = ImageFont.truetype(FONT_N, 25)
        fb = ImageFont.truetype(FONT_SB, 27)
        lspace(d, (W*0.155, H*0.079), "UNREAD FOR", f, (238,233,222,205), sp=7)
        lspace(d, (W*0.155, H*0.079+36), f"{years} YEARS", fb, (245,241,231,255), sp=7)
    return L

def logo_layer():
    L = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(L)
    d.rectangle([W*0.36, H*0.545, W*0.64, H*0.545+1], fill=(235,230,218,110))
    lspace(d, (W/2, H*0.583), LOGO_TEXT, ImageFont.truetype(FONT_S, 68), (250,247,240,255), sp=13)
    lspace(d, (W/2, H*0.583+104), LOGO_URL, ImageFont.truetype(FONT_N, 31), (238,233,222,205), sp=9)
    return L

HOOK = body_layer(["Nobody has ever", "read this."], size=78, y0=0.715)
LAYERS = {}
for c in CARDS:
    LAYERS[f"h{c['n']}"] = head_layer(c["title"], c["sub"])
    LAYERS[f"a{c['n']}"] = body_layer(c["a"][2])
    LAYERS[f"b{c['n']}"] = body_layer(c["b"][2])
    LAYERS[f"u{c['n']}"] = hud_layer(str(c["n"]), c["years"], (6-c["n"])/5)
LAYERS["u_open"] = hud_layer("5", None, 0.02)
LAYERS["turnA"]  = body_layer(TURN_A[2], size=76, y0=0.40)
LAYERS["turnB"]  = body_layer(TURN_B[2], size=76, y0=0.40)
LAYERS["logo"]   = logo_layer()

# ---- render -------------------------------------------------------------
import subprocess, sys
N = int(round(TOTAL*FPS))
rng = np.random.default_rng(7)
MP4 = "/home/user/Tik-Tok/build/UNREAD_full_silent.mp4"
print(f"rendering {N} frames ({TOTAL}s @ {FPS}fps) -> {MP4}", flush=True)
ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
    "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-c:v","libx264","-profile:v","high",
    "-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",MP4], stdin=subprocess.PIPE)
QC = {0,15,45,75,135,165,205,245,290,330,375,420,470,510,560,600,650,690,740,780,830,860,880,905,935}

def frame_bg(t):
    for (a, b, k, cx, cy, wf, z0, z1, mode) in SHOTS:
        if a <= t < b: break
    else:
        return None
    im = img(k); IW, IH = im.size
    lt = ease(min(max((t-a)/(b-a), 0), 1)); zoom = z0 + (z1-z0)*lt
    if mode == "fill":
        cw = IW*wf/zoom; ch = cw*16/9
        if ch > IH: ch = IH; cw = ch*9/16
        x = min(max(cx*IW-cw/2, 0), IW-cw); y = min(max(cy*IH-ch/2, 0), IH-ch)
        return im.crop((int(x), int(y), int(x+cw), int(y+ch))).resize((W, H), Image.LANCZOS, reducing_gap=3.0)
    # fit: object over a blurred, darkened cover-crop of itself
    cs = max(W/IW, H/IH)*1.06
    bw, bh = int(IW*cs), int(IH*cs)
    bg = im.resize((bw, bh), Image.BILINEAR, reducing_gap=2.0).crop(
        ((bw-W)//2, (bh-H)//2, (bw-W)//2+W, (bh-H)//2+H))
    bg = bg.filter(ImageFilter.GaussianBlur(46)).point(lambda v: int(v*0.55))
    sc = (W*1.02)/IW/zoom
    sw, sh = max(int(IW*sc), 2), max(int(IH*sc), 2)
    fg = im.resize((sw, sh), Image.LANCZOS, reducing_gap=3.0)
    ox, oy = (W-sw)//2, int(H*0.43) - sh//2
    # feather the object into the dark with a soft ellipse - no hard rectangle edge
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse(
        [ox+sw*0.035, oy+sh*0.045, ox+sw*0.965, oy+sh*0.955], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(58))
    lay = Image.new("RGB", (W, H), (0, 0, 0))
    lay.paste(fg, (ox, oy))
    return Image.composite(lay, bg, mask)

for i in range(N):
    t = i/FPS
    black = any(a <= t < b for (a, b) in FLASH) or t >= 28.80
    if black:
        arr = np.zeros((H, W, 3), dtype=np.float32)
    else:
        bg = frame_bg(t)
        if bg is None: bg = Image.new("RGB", (W, H), (8, 9, 12))
        arr = grade(np.asarray(bg))
        arr *= (1.0 + 0.018*math.sin(t*11.3) + 0.012*math.sin(t*27.7) + rng.normal(0, 0.004))
        arr += rng.normal(0, 0.016, arr.shape).astype(np.float32)*(0.35 + 0.65*(1-arr))
        m = float(arr.mean())
        if m > 1e-4:
            arr *= min(max((0.26/m)**0.55, 0.62), 1.22)
        arr *= VIG
        if 28.30 <= t < 28.80:                      # fade to the turn
            arr *= 1.0 - ease((t-28.30)/0.50)
    frame = Image.fromarray((np.clip(arr, 0, 1)*255).astype(np.uint8))

    def blend(layer, alpha):
        if alpha <= 0: return
        l = layer.copy(); l.putalpha(l.split()[3].point(lambda p: int(p*min(alpha, 1.0))))
        frame.paste(l, (0, 0), l)

    if 1.80 <= t < 2.90: blend(HOOK, (t-1.80)/0.22)
    if 3.00 <= t < 4.50: blend(LAYERS["u_open"], (t-3.00)/0.18)
    for c in CARDS:
        if c["t0"] <= t < c["t1"]:
            blend(LAYERS[f"u{c['n']}"], (t-c["t0"])/0.20)
            blend(LAYERS[f"h{c['n']}"], min((t-c["t0"]-0.10)/0.25, 1.0))
            for tag in ("a", "b"):
                s0, s1, _ = c[tag]
                if s0 <= t < s1: blend(LAYERS[f"{tag}{c['n']}"], (t-s0)/0.25)
    if TURN_A[0] <= t < TURN_A[1]: blend(LAYERS["turnA"], (t-TURN_A[0])/0.30)
    if TURN_B[0] <= t < TURN_B[1]: blend(LAYERS["turnB"], (t-TURN_B[0])/0.30)
    if t >= LOGO_T:                blend(LAYERS["logo"], (t-LOGO_T)/0.45)

    if i in QC: frame.save(f"{OUT}/qc_{i:04d}.png")
    ff.stdin.write(frame.tobytes())
    if i % 150 == 0: print(f"  {i}/{N}  t={t:.2f}", flush=True)
ff.stdin.close(); ff.wait()
print("done ->", MP4)
