# "Why doesn't Duolingo work?" — 22.5s infographic promo

Animated infographic in Verbavia's own palette (indigo #5047e5 on #F7F8FB, Inter
variable), built around REAL captures of both sites — nothing in the video is generated
imagery.

## Structure (30fps, 675 frames)

| t | scene |
|---|---|
| 0.0–3.0 | Hook: "Why doesn't Duolingo work?", red underline draws, real Duolingo homepage drops in as a phone card |
| 3.0–7.5 | 01 — No real flashcards. Three blank cards fan out, a red X strokes through them |
| 7.5–12.0 | 02 — Lessons never get serious. Their own homepage copy zooms in and a red hand-drawn circle animates around "...chess, and more!" |
| 12.0–16.5 | 03 — The bar is on the floor. Counter ticks to 5/10 in red while the progress pill fills green: SECTION PASSED ✓ |
| 16.5–22.5 | Indigo circle-wipe. "So I built Verbavia." Real verbavia.com captures (hero + the site's own "Why this isn't another tapping game" comparison), three drawn check rows, closing line, verbavia.com pill |

## Captures

`shoot.py` / `shoot2.py` (scratchpad) drive the preinstalled Chromium via Playwright.
Two environment quirks worth keeping:

- launch with `executable_path="/opt/pw-browsers/chromium"` (pip Playwright's own browser
  is a different build number and absent);
- launch args must include `--ssl-version-max=tls1.2 --disable-quic` — the egress relay
  drops Chromium's large post-quantum TLS 1.3 ClientHello (~1.8 KB) with a bare
  connection reset. curl works either way; the browser doesn't without this.
- duolingo.com never reaches `networkidle` (streaming analytics): use
  `domcontentloaded` + a fixed wait.

## Claims hygiene

The three claims are framed to stay on the right side of comparative advertising:
"no real flashcards" is verifiable (no in-app spaced-repetition decks; Tinycards was shut
down in 2020); "never get serious" is anchored to *their own homepage copy*, shown on
screen; "the bar is on the floor" is opinion illustrated with an obviously schematic
mock meter — it is NOT presented as a screenshot of their UI. Keep it that way: don't
caption the 5/10 card as if it were Duolingo's interface. Using a competitor's homepage
screenshot for direct comparison/critique is standard nominative use; showing their
mascot beyond what appears in the real capture is not something this edit does.

## Build

```
python3 render_promo.py style     # key frames in seconds - tune here first
python3 render_promo.py full      # -> PROMO_silent.mp4
python3 render_audio_pr.py        # -> promo.wav (UI taps/ticks guide)
ffmpeg -y -i PROMO_silent.mp4 -i promo.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 \
  -c:v libx264 -preset slow -crf 19 -maxrate 7000k -bufsize 14000k -profile:v high \
  -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -shortest WHY_DUOLINGO.mp4
```

Music: this one works with or without a track — the UI sounds carry it. If you add one,
something minimal and confident (soft four-on-the-floor house or a marimba-ish product
track), duck it under the section taps at 3.0 / 7.5 / 12.0 / 16.5s.
