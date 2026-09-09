# Comeback frame (no caption — added downstream)

A reply image to Duolingo's own "end your streak and I'll end you" post. Two-panel joke:
their threat, then this. Built to mirror their staging exactly — black void, spotlight cone,
grey floor ellipse, brand name top-centre in the cone, big white caption underneath — so the
parallel reads before anyone processes the content.

## Assets — nothing generated

- **Compass**: your real 🧭 from the verbavia.com header (`<span class="brand">`), rendered
  from Noto Color Emoji's 109px bitmap strike and scaled up.
- **Duo**: the actual mascot cut out of the live duolingo.com homepage capture
  (`shots/duo_home_m.png`, region 573,755–965,1125). Flood-fill background removal plus a
  hue mask to drop the neighbouring characters, then squashed to 80% and rotated 14° into a
  collapsed pose. X eyes and tongue drawn in his own flat vector style.
- **Knife**: drawn as flat vector to match the art style.

## The occlusion trick

The tip has to be *in* him, not over him. Three passes:

1. blade composited underneath
2. Duo on top — hides the whole knife
3. only the part of the knife above the entry line composited again

Plus a flat green entry shadow at the wound. The knife's tip and handle positions are found
empirically — magenta/cyan marker pixels drawn at both ends, rotated with the image, then
located by colour — so placement is exact rather than guessed at through rotation maths.

Deliberately bloodless: X eyes and a planted knife carry it, and the clean version survives
being screenshotted out of context.

## Output

- `verbavia_kill.png` — 1500×1024, matches their aspect
- `verbavia_kill_portrait.png` — 1080×1350 for feed

`python3 make_kill.py` regenerates both. Knife angle/length are `KN_ANG` / `KN_LEN`; the
entry point is `TIP_TARGET` as a fraction of Duo's bounding box.


---

## v2 — the lit render (`make_kill2.py`)

v1 was flat clip-art. v2 is a lit scene, supersampled 2x and downsampled.

- **Brand**: the real `.brand` lockup screenshotted at 6x DPI (`brand_mark.png`), white keyed
  out by corner flood-fill so the compass keeps its interior whites, purple lifted ~30% so
  #4F46E5 holds against near-black, then a two-pass glow behind it.
- **Stage**: floor plane with an elliptical light pool (soft falloff plus a hotter core),
  ambient wash, and a volumetric cone above it modulated by a blurred noise field for haze.
- **Knife**: blade is a numpy gradient — specular band, secondary roll-off, dark bevels on
  both edges, brightening toward the tip — masked to the blade polygon. Wrapped handle,
  lit guard edge, pommel highlight.
- **Grounding**: every sprite is `trim()`ed to its alpha bbox first. Rotation padding was
  what made v1's subjects levitate — the "bottom" of the image wasn't the bottom of the
  object. Contact shadows are squashed alpha, blurred, multiplied into the floor.
- **Penetration**: the entry point is *computed*, not placed. Walk back along the blade axis
  from the tip until Duo's alpha drops below 128 — that's exactly where the blade crosses
  his silhouette. An oriented dimple, slit and edge-catch glint go there, all rotated to the
  blade angle.
- **Relight**: subjects get a vertical light ramp plus a rim term. Duo's rim is near zero on
  purpose — his cutout carries a faint white fringe from the page background, and any rim
  light amplifies it into a halo.
- **Grade**: contrast, cool shadows, warm highlights, gentle vignette, bloom on highlights,
  fine grain.

Deliberately bloodless. Add a trickle by drawing from `ENTRY` along `(ux,uy)` if wanted.
