# "The owl" running gag — 24.8s

The 20-second list edit restructured around an escalating gag. A 1.8s title card, then five
content beats that total exactly 20.0s under an honest 20-second countdown, then the outro:

| t | beat | what happens |
|---|---|---|
| 0.0–1.8 | title | "This is **everything wrong** with Duolingo in **20** seconds." — word-pop with yellow and red markers, no timer yet |
| 1.8–4.7 | **01 The owl.** | pale background, the *almost*-normal Duo (dark rings, eyes slightly off, one-frame red flicker every ~0.6s). "He's just… watching." Timer starts at 20.0 here |
| 4.7–9.0 | It's a **game.** | kinetic headline, yellow marker behind "game.", their real homepage tagline on a tilted card, red hand-drawn circle, three sticker chips |
| 9.0–12.5 | **03 The owl. Again.** | near-black with red vignette; the mid owl, closer, eyes pulsing, glitch bursts. "Miss one day. He knows." |
| 12.5–16.7 | Half wrong? You still **pass.** | green marker, the 5/10 meter on a tilted card, chips |
| 16.7–21.8 | **THE OWL.** | black + throbbing red vignette; extreme owl zooming from 1.45× to 2.25× until the eyes fill the frame; jitter every frame, glitch every 8 frames, strobe every half-second; giant red headline shaking |
| 21.8–24.8 | outro | indigo circle-wipe: "This is why I created **verbavia.com** — to solve all these problems." + pill |

A 20-second countdown pill runs top-right across the five content beats (red inside the
last five seconds); it is hidden on the title so the number the title promises is the
number the clock starts on. Every beat opens with a 5-frame camera shake and scale punch.

## The three owls

One parametric horror pass over the real homepage Duo, `make_owls.py` (scratchpad), with a
single `level` knob from 0 to 1 driving colour drain, contrast crush, eye-socket paint,
glow, blood tears (from 0.45 up), glitch-slice count, RGB split, scanlines, grain and the
vertical stretch. The three assets are levels **0.22 / 0.62 / 1.0**.

## Audio — cut your music here

The guide bed is built for you to cut the track on the owl entries. Each owl sting is
preceded by a **60 ms hard mute** and starts with zero attack at exactly these points:

```
0:01.80   owl 1   (short sting: noise burst + inharmonic screech + sub drop)
0:09.00   owl 2   (bigger sting + 36 Hz drone + heartbeat at 70 bpm)
0:16.73   owl 3   (full sting + drone + heartbeat at 118 bpm + a 3.2 kHz vibrato whine)
0:21.80   outro   (silence, then a clean tap and the pill pop)
```

The title (0–1.8s) has a tap and four soft pops on the words — your track can start there.

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
