# "The owl" running gag — 24.8s

The 20-second list edit restructured around an escalating gag. A 1.8s title card, then five
content beats that total exactly 20.0s under an honest 20-second countdown, then the outro:

| t | beat | what happens |
|---|---|---|
| 0.0–1.8 | title | "This is **everything wrong** with Duolingo in **20** seconds." — word-pop with yellow and red markers, no timer yet |
| 1.8–2.6 | **01 The owl.** — jumpscare | 0.8s. The almost-normal Duo slams in at full size with a 30px shake; red-eye flicker on frames 7 and 15; hard cut out. Timer starts at 20.0 |
| 2.6–10.1 | It's a **game.** | 7.5s, two acts: headline + their homepage tagline on a tilted card + red circle + three sticker chips; at 5.0s the card slides out and **Fun ≠ fluent.** pops in |
| 10.1–11.0 | **03 The owl. Again.** — jumpscare | 0.9s. Near-black, red vignette, the mid owl at 1.25×, jitter every frame, glitch every 6 frames; hard cut out |
| 11.0–18.8 | Half wrong? You still **pass.** | 7.8s, two acts: the 5/10 meter counts and passes, chips; at 5.0s the card slides out and **Green screens. Zero learning.** pops in |
| 18.8–21.8 | **THE OWL.** | 3.0s. Black + throbbing red vignette; extreme owl zooming 1.45× → 2.25× until the eyes fill the frame; jitter, glitch every 8 frames, strobe every half-second; giant red headline shaking |
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
0:01.80   owl 1   (0.8s sting, hard-stopped with the picture at 0:02.60)
0:10.10   owl 2   (0.9s sting, hard-stopped at 0:11.00)
0:18.80   owl 3   (3.0s: full sting + drone + heartbeat at 118 bpm + vibrato whine)
0:21.80   outro   (silence, then a clean tap and the pill pop)
```

The two short stings are cut with the picture — a 30 ms fade to zero at the frame the
speaking card returns — so the exit is as abrupt as the entry. Cut your track at the
three owl timecodes and bring it back on the speaking cards.

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
