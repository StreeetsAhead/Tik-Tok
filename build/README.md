# "UNREAD" — a 31.5s TikTok edit

Five things humans wrote that no living person can read, counted down 5 → 1. The
language-app logo appears only in the final two seconds. Nothing is shot; every frame is
public-domain or openly-licensed material pulled off the web.

## The grid

**80 BPM, beat = 0.75s, first downbeat at 0:00.** Every cut in the edit lands on a beat.
Cards are exactly 4.5s (6 beats), so card boundaries fall at 4.50 / 9.00 / 13.50 / 18.00 /
22.50 / 27.00 — alternating between bar downbeats and the third beat of a bar.

## Music

Cut for **Jóhann Jóhannsson — "The Beast"** (*Sicario*, 2015). It is a single escalating
throb that never resolves, which is the exact shape of this countdown. Jóhannsson also
scored *Arrival*, a film about an undecipherable script, so it is the right composer for
this by more than coincidence.

Two sync points matter more than strict tempo matching:

- **0:03.00** — the counter drops in. Put the track's first real swell here.
- **0:27.00** — the turn. Put the track's climax here.

`full.wav` is a synthesized guide bed (sub impacts, wax-cylinder crackle, a noise riser, a
41.2Hz drone stack, escalating kick). It is licence-free and ships in the muxed cut. Mute it
and lay your track over the top, or keep the impacts underneath for weight — they are on the
same grid.

## Timeline

| t | card | imagery | text |
|---|---|---|---|
| 0.00 | hook | 4 Voynich folios, fast | — |
| 1.80 | | script column | "Nobody has ever read this." |
| 3.00 | | (black flash) counter enters | `5 OF 5` |
| 4.50 | **5** | Phaistos Disc, spiral push → full object | 241 symbols · only one · too short to crack |
| 9.00 | **4** | Rongorongo glyph detail → Easter Island | 26 tablets · last readers died in the 1860s |
| 13.50 | **3** | Linear A tablet, wide → incisions | *We know how it sounds. We do not know what it means.* |
| 18.00 | **2** | Indus seal, script detail → full seal | 5m people · 4,000 inscriptions · avg. 5 characters |
| 22.50 | **1** | Voynich zodiac → script column | beat the cryptographers who broke PURPLE |
| 27.00 | turn | fade to black | "Some languages can never be learned." |
| 29.10 | | black | "Yours isn't one of them." |
| 30.15 | | | **logo** |

Card 3 is the one to protect in any recut. "We know how it sounds, we do not know what it
means" is the single best beat in the video — Linear A shares signs with Linear B, which
Ventris deciphered in 1952, so the phonetic values carry over but the language behind them
does not. Hold it half a second longer than feels comfortable.

## Swapping in the real logo

`render_full.py` sets the end card in two constants near the top:

```python
LOGO_TEXT = "VERBAVIA"      # wordmark
LOGO_URL  = "verbavia.com"  # destination, held under the mark
```

The domain is the only call to action in the whole edit, so it holds for the last 1.35s
under the wordmark. To use a real logo file instead, replace `logo_layer()`:

```python
def logo_layer():
    L = Image.new("RGBA", (W, H), (0,0,0,0))
    lg = Image.open("logo.png").convert("RGBA")
    lg.thumbnail((int(W*0.46), int(H*0.12)), Image.LANCZOS)
    L.paste(lg, ((W-lg.width)//2, int(H*0.545)), lg)
    d = ImageDraw.Draw(L)
    lspace(d, (W/2, H*0.545+lg.height+34), LOGO_URL,
           ImageFont.truetype(FONT_N, 31), (238,233,222,205), sp=9)
    return L
```

Keep it inside the frame's world — the grain and drone keep running under it on purpose. A
hard cut to a clean white brand card breaks the spell and craters the completion rate at the
exact moment it counts.

## Build

```
pip install numpy pillow && apt-get install -y ffmpeg
python3 fetch_assets.py          # -> assets/src (Voynich), assets/wm (Commons)
python3 render_full.py           # -> UNREAD_full_silent.mp4  (~10 min, pipes to ffmpeg)
python3 render_audio_full.py     # -> full.wav
# master (CRF 17, ~41 MB)
ffmpeg -y -i UNREAD_full_silent.mp4 -i full.wav -af loudnorm=I=-15:TP=-1.5:LRA=11 \
       -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest UNREAD_full.mp4

# upload copy (CRF 23, ~15 MB) - film grain is expensive to compress, so the
# master is large; this is visually equivalent after TikTok re-encodes anyway
ffmpeg -y -i UNREAD_full_silent.mp4 -i full.wav -af loudnorm=I=-15:TP=-1.5:LRA=11 \
       -c:v libx264 -preset slow -crf 23 -maxrate 6500k -bufsize 13000k \
       -profile:v high -pix_fmt yuv420p -c:a aac -b:a 160k \
       -movflags +faststart -shortest UNREAD_full_web.mp4
```

Shots are `(start, end, key, cx, cy, width_frac, zoom0, zoom1, mode)` in `SHOTS`. `mode` is
`fill` (9:16 crop, for tight pushes) or `fit` (whole object centred on a dark ground, for
museum pieces wider than 9:16). Retiming is a one-line change.

`render_opener.py` is the standalone 4.5s hook, kept because it renders in about a minute
and is useful for iterating on the look without waiting for the full pass.

## Sources and licences

See `../ATTRIBUTION.md`. The Voynich, the Phaistos Disc and the Easter Island plate are
public domain; the Linear A and Indus plates are CC BY-SA, which is worth a decision before
this runs as a paid ad.
