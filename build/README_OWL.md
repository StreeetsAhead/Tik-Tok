# "The owl" running gag — 18.0s

The 20-second list edit restructured around an escalating gag. Six beats:

| t | beat | what happens |
|---|---|---|
| 0.0–2.2 | **01 The owl.** | pale background, the *almost*-normal Duo (dark rings, eyes slightly off, one-frame red flicker every ~0.6s). "He's just… watching." |
| 2.2–5.4 | It's a **game.** | kinetic word-pop headline with a yellow marker wiping in behind "game.", their real homepage tagline on a tilted card, red hand-drawn circle, three sticker chips (no flashcards / ads every lesson / grammar? guess.) |
| 5.4–8.0 | **03 The owl. Again.** | background drops to near-black with a red vignette; the mid owl, bigger and closer, eyes pulsing, glitch bursts every second. "Miss one day. He knows." |
| 8.0–11.2 | Half wrong? You still **pass.** | green marker on "pass.", the 5/10 meter on a tilted card, chips (hearts run out / streak guilt / plateaus at A2) |
| 11.2–15.0 | **THE OWL.** | black + throbbing red vignette; the extreme owl at 1.45× zooming to 2.25× so the eyes fill the screen; jitter every frame, glitch burst every 8 frames, a strobe flash every half-second; giant red headline shaking |
| 15.0–18.0 | outro | indigo circle-wipe: "This is why I created **verbavia.com** — to solve all these problems." + pill |

A 15-second countdown pill runs top-right across the five content beats (red inside the
last four seconds). Every beat opens with a 5-frame camera shake and scale punch.

## The three owls

One parametric horror pass over the real homepage Duo, `make_owls.py` (scratchpad), with a
single `level` knob from 0 to 1 driving colour drain, contrast crush, eye-socket paint,
glow, blood tears (from 0.45 up), glitch-slice count, RGB split, scanlines, grain and the
vertical stretch. The three assets are levels **0.22 / 0.62 / 1.0**.

## Audio — cut your music here

The guide bed is built for you to cut the track on the owl entries. Each owl sting is
preceded by a **60 ms hard mute** and starts with zero attack at exactly these points:

```
0:00.00   owl 1   (short sting: noise burst + inharmonic screech + sub drop)
0:05.40   owl 2   (bigger sting + 36 Hz drone + heartbeat at 70 bpm)
0:11.20   owl 3   (full sting + drone + heartbeat at 118 bpm + a 3.2 kHz vibrato whine)
0:15.00   outro   (silence, then a clean tap and the pill pop)
```

Normal beats carry only clock ticks and pops on the chips, so your track can sit on top
of them untouched. Duck or cut it at 0:05.40 and 0:11.20; bring it back on the indigo.

## Build

```
python3 render_owl.py style
python3 render_owl.py full         # -> OWL_silent.mp4
python3 render_audio_owl.py        # -> owl.wav
ffmpeg -y -i OWL_silent.mp4 -i owl.wav -af loudnorm=I=-15:TP=-1.0:LRA=14 \
  -c:v libx264 -preset slow -crf 19 -maxrate 7500k -bufsize 15000k -profile:v high \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest THE_OWL_GAG.mp4
```
