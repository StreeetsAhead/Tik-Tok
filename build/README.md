# "UNREAD" — TikTok edit pipeline

A 28s music-driven edit about five scripts no living person can read.
The language-app logo appears only in the final two seconds.

Currently built: **the opening hook (0.0–4.5s).**

## Sources

All assets are fetched, not shot. The Voynich Manuscript (Beinecke MS 408)
is served by Yale's IIIF endpoint as public-domain scans:

    https://collections.library.yale.edu/manifests/2002046   # 213 canvases
    https://collections.library.yale.edu/iiif/2/<id>/full/2600,/0/default.jpg

Native resolution is 2793x3761; the server returns 400 above ~2600px wide.
`folios.json` maps folio numbers (`52r`, `78r`, ...) to IIIF ids.

Folios used in the hook:

| folio | id      | shot |
|-------|---------|------|
| 78r   | 1006214 | figures in the green pools; also the wide finish and the script column |
| 71r   | 1006202 | zodiac wheel |
| 75r   | 1006208 | figures in the stream |
| 33v   | 1006139 | plant with no known species |

## Build

    pip install numpy pillow && apt-get install -y ffmpeg
    python3 render_opener.py     # -> build/frames/*.png   (135 frames)
    python3 render_audio.py      # -> build/opener.wav
    ffmpeg -y -framerate 30 -i frames/f%04d.png -i opener.wav \
      -c:v libx264 -profile:v high -crf 17 -pix_fmt yuv420p -r 30 \
      -c:a aac -b:a 192k -movflags +faststart -shortest UNREAD_opener.mp4

## Notes

`render_opener.py` composites every frame in Pillow/numpy rather than in an
ffmpeg filtergraph — the grade, candle-light falloff, flicker, grain and
vignette are all explicit and tunable in one place. Shots are defined as
`(source, cx, cy, width_frac, zoom_start, zoom_end, duration)`.

`render_audio.py` synthesizes the whole bed from scratch (no licensed track):
sub impacts with pitch glide, wax-cylinder crackle, a noise riser, and a
41.2Hz drone stack with a 70bpm kick. Swap in a real track by muxing it in
place of `opener.wav`.
