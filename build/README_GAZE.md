# "THE GAZE" — 13.8s conqueror edit

Six conquerors through their most famous images, eye-anchored and composited in layers.
No text until the Verbavia end card.

## Structure (30fps, cuts on frames 0 / 60 / 97 / 134 / 171 / 208 / 283 / 313 / 339)

1. **Caesar** (0–2.0s) — deep zoom out of the Tusculum marble, an antique map of Europe
   multiplied over the stone, Turner storm screened low underneath. Cold grade.
2. **Alexander** (2.0–3.2) — the mosaic face; the battle detail (spears, horses) screened
   over it, drifting.
3. **Charlemagne** (3.2–4.5) — Dürer gold; Turner's Parliament fire rising behind the
   crown; heavy bloom.
4. **Genghis** (4.5–5.7) — slow push, storm drifting, coldest grade.
5. **Mehmed** (5.7–6.9) — Bellini; map multiplied, embers screened.
6. **Napoleon** (6.9–9.4) — the climax: starts on the bicorne, then a 17x exponential
   zoom-out reveal to the full David painting while the storm swirls; reds pushed so the
   cloak burns.
7. **Gaze strobe** (9.4–10.4) — six eye close-ups at 5 frames each, alternating warm/cold.
8. **The compiled gaze** (10.4–11.1) — all six pairs of eyes stacked as horizontal bands,
   breathing a few pixels each. The poster frame.
9. Black, then the end card (11.3–13.8).

Every cut carries 4 impact frames: luminance flash, decaying RGB split, frame shake.
Global passes: film grain, dust motes, gold radial wash, chromatic aberration at the
edges, face-centred vignette.

## Music

**Verdi — Requiem, "Dies Irae", from 0:00.** The hammer blows land on the opening and the
cut impacts; the string fury underneath is the acceleration. Alternate for a colder cut:
Beethoven 7, second movement. Avoid "O Fortuna" / "Lux Aeterna" (parody territory).
`conq.wav` is the guide bed — an impact on every cut, risers into Napoleon and the strobe.

## Workflow notes

- Haar cascades fail on paintings; the eye anchors were placed by **dot-probe**: draw
  labelled candidate dots on the source, look, correct. Sub-1% precision matters for the
  stacked-eye bands.
- `python3 render_conquerors.py style` renders ~a dozen key frames in seconds — always
  tune the look there before a full pass.
- Shots are rows in `SHOTS`: `(f0,f1,key,z0,z1,curve,[texture layers],warmth,bloom,red)`.
  A texture layer is `(key, blend, opacity, drift_x, drift_y, scale0, scale1)`.

## Build

```
python3 render_conquerors.py full     # -> CONQ_silent.mp4
python3 render_audio_cq.py            # -> conq.wav
ffmpeg -y -i CONQ_silent.mp4 -i conq.wav -af loudnorm=I=-15:TP=-1.5:LRA=11 \
  -c:v libx264 -preset slow -crf 20 -maxrate 8000k -bufsize 16000k -profile:v high \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest THE_GAZE.mp4
```
