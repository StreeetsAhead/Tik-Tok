# "Everything wrong with Duolingo in 20 seconds" — 23.0s

Nine reasons at 2.2s each under a draining 20-second timer (top-right pill + a thin bar
across the very top; both go red inside the last five seconds), then a 3-second indigo
outro: "That's why I created **verbavia.com** — a site which solves all these problems."

| # | t | reason | widget |
|---|---|---|---|
| 01 | 0.0 | No flashcards. | three blank cards fan, red X strokes through |
| 02 | 2.2 | It's a game. | their real homepage tagline, hand-drawn circle round "chess, and more!" |
| 03 | 4.4 | Half wrong? You pass. | counter to 5/10 in red, bar fills green, SECTION PASSED |
| 04 | 6.6 | Streaks over skills. | "Streak 412 days" fills orange; "Can order a coffee — " stays empty |
| 05 | 8.8 | Hearts. | five hearts grey out one by one; "Out of hearts. Try again tomorrow." |
| 06 | 11.0 | Ads. | schematic dark ad card, "Skip in 5… 1" |
| 07 | 13.2 | Grammar? Guess. | "Ella come manzanas." — "Why 'come' and not 'como'? (no explanation given)" |
| 08 | 15.4 | Plateau at A2. | line chart rises then flatlines under a dashed C2 |
| 09 | 17.6 | **The owl.** | background drops to black with a red vignette; the horror Duo |
| — | 20.0 | outro | indigo wipe, the line, verbavia.com pill |

## The owl

Not generated. It is the real Duo cut from the live duolingo.com homepage capture and
put through a treatment: flood-fill background removal (keeps the eye whites), a hue mask
to cut the neighbouring characters, connected-component cleanup, colour drained to a
rotten green, contrast crushed, eye whites painted deep red with an additive glow, blood
tears, sixteen horizontal glitch slices, RGB split, scanlines, grain, and an 8% vertical
stretch. In the video it jitters every other frame, the eyes pulse, and a glitch burst
fires every 23 frames. `owl_horror.png` is the baked asset; the recipe is in the
scratchpad script and reproduced in the commit message.

Risk note, once: distorting a competitor's mascot is a step beyond screenshotting their
site. It's parody/critique and Duolingo themselves market "evil Duo", but it is the one
element in these four videos a lawyer would flag first.

## Sound

`fast.wav`: a clock tick on every second (higher, softer for 0–15, lower and harder for
15–20), a tap on each reason, a sub sting + 36 Hz drone + heartbeat under the owl, a whoosh
into the outro, a pop on the pill. It's mixed as a guide; a track on top should be fast and
dry — the ticks are the metronome.

## Build

```
python3 render_fast.py style   # key frames
python3 render_fast.py full    # -> FAST_silent.mp4
python3 render_audio_fs.py     # -> fast.wav
ffmpeg -y -i FAST_silent.mp4 -i fast.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 \
  -c:v libx264 -preset slow -crf 19 -maxrate 7000k -bufsize 14000k -profile:v high \
  -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -shortest EVERYTHING_WRONG_20S.mp4
```

`render_fast.py` imports the primitives from `render_promo.py` (type, cards, strokes,
easing) so the two videos share one design system.

## If you voice the 20 seconds too

One clipped line per reason, on the tap: "No flashcards." / "It's a game — that's their
homepage." / "Get half wrong, you still pass." / "Streaks over skills." / "Run out of hearts,
run out of learning." / "Ads. Every lesson." / "Grammar? Guess." / "You plateau at A2." /
(silence — let the owl sit) — then your outro line over the indigo.
