# "THE LONG LOOK" — 11.5s European edit

Twelve European faces spanning roughly 2,100 years, match-cut with the **eyes locked to one
point on screen**, accelerating into a strobe, ending on the Verbavia card. No text anywhere
until the end card. Every asset is CC0.

## Why it works

Eye contact is the hardest thing on a feed to scroll past, and the eye-lock turns a slideshow
into a single face morphing through history. The chain is chronological, so without a word of
text you feel it travel: **carved marble → painted panel → photograph**. That progression is
the whole argument — these people are not gone, and neither is what they spoke.

It opens *inside* a marble eye at 2.8× and pulls back over 1.27s. For the first half second
you cannot tell what you are looking at — it reads as abstract stone — and then it resolves
into a face from 270 BCE.

## The chain

Ptolemaic queen (270 BCE) → Augustus → Fayum woman in red → the boy Eutyches → Caracalla →
Constantine → a Gothic head of Joseph (1230) → Portrait of a Carthusian (1446) → Netherlandish
woman (1520) → Bronzino (1530s) → Lemuel Shaw daguerreotype (1850) → Maniglier (1850).

The two Fayum mummy portraits are the secret weapon: encaustic panels from Roman Egypt that
look uncannily like photographs, and are the direct ancestor of icon painting. They sit in the
middle of the chain and are the moment most viewers realise something strange is happening.

## Grid and cuts

**120 BPM, beat = 0.5s.** Cut lengths in frames @30fps:

```
38, 22, 22, 19, 19, 15, 15, 11, 11, 8, 8, 8   accelerating   (0.00–6.53s)
12 x 3                                         strobe         (6.53–7.73s)
29                                             hold last face (7.73–8.70s)
9                                              fade           (8.70–9.00s)
74                                             end card       (9.00–11.47s)
```

`longlook.wav` is a guide bed, not music: a sub impact on **every** picture cut, a riser into
the strobe, ticks through it, and a big hit on the final face. Line your track up against
those and the picture locks.

## Music

**Verdi, Requiem — "Dies Irae".** Start at 0:00; the four hammer blows land on the first frame
and the frantic strings underneath drive the acceleration exactly as the cuts shorten. It is
also, unarguably, European.

Alternates: Mozart's *Confutatis*; Zbigniew Preisner's *Lacrimosa*; or for a modern edit sound,
Hans Zimmer's "Why So Serious?" — the rising note works against the strobe.

Avoid "O Fortuna" and "Lux Aeterna". Both fit and both are so overused they read as parody.

## How the eye-lock is built

1. `detect_eyes.py` runs OpenCV Haar cascades over each source, finds the face, then the eyes
   inside it, and writes `eye_cx`, `eye_cy` and interocular distance as fractions of the image.
   Sculpture and painting defeat the eye cascade often enough that there is a geometric
   fallback (eyes at 40% down the face box); two faces failed outright and were dropped.
2. `align2.py` renders a crosshair contact sheet so alignment can be checked by eye. **Do this
   before rendering** — bad alignment is invisible in code and obvious in one glance.
3. `render_europe.py` builds one oversampled, eye-aligned base per face, then crops each
   frame's zoom out of that cache. Twelve resizes instead of 344, so the whole film renders in
   under a minute. Face 0 gets a 2.8× base so the opening pull has resolution to spend.

## Build

```
pip install numpy pillow "opencv-python-headless<5"
python3 detect_eyes.py          # -> eyes.json
python3 align2.py               # -> align2.png   CHECK THIS
python3 render_europe.py        # -> LONGLOOK_silent.mp4
python3 render_audio_eu.py      # -> longlook.wav
ffmpeg -y -i LONGLOOK_silent.mp4 -i longlook.wav -af loudnorm=I=-15:TP=-1.5:LRA=11 \
  -c:v libx264 -preset slow -crf 20 -maxrate 8000k -bufsize 16000k -profile:v high \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest THE_LONG_LOOK.mp4
```

Faces are `(met_key, scale_adj)` in `CHAIN`; `scale_adj` normalises apparent head size. Swap
or reorder freely — the eye-lock is computed, not hand-placed.

## A note on framing

"Save Europe" as a slogan is closely associated with identitarian politics. The edit itself is
art history and needs no such framing; captioning it that way would attach Verbavia to a
political movement. Let the faces do it.
