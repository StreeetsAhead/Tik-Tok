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

---

## v3 — flat vector, the version that shipped

v2's lit render was the wrong direction. v3 goes back to matching Duolingo's own flat art
style (which is also their reference frame's style), rendered at **3x supersample** and
downsampled once — so every edge is crisp and nothing is blurred.

- **Logo**: `verbavia_logo.svg`, a vector rebuild of the real Verbavia compass. The site's
  `favicon.svg` is only an emoji in a purple circle, so this was reconstructed from the
  supplied artwork: ring and lug in a #7C74E8→#4F46C9 gradient, lavender face, 8-point rose
  generated programmatically (4 long cardinals, 4 short diagonals) with each point split
  into two facets and lit/shadowed by dot product against an upper-left light vector, red
  north, white hub. Rendered through headless Chromium at any resolution.
- **Wound**: sharp, not blurred. A rotated slit stamped at the computed entry point (walk
  back along the blade axis until Duo's alpha drops), dark rim plus a near-black core.
- **Blood**: flat vector in three tones. Pool built from layered organic blobs — an ellipse
  whose radius is modulated by four sine harmonics, so it reads hand-drawn rather than
  geometric. Drips are tapered polygons with a bulb at the tip, masked to Duo's silhouette
  so they run down his body and stop at his edge. A smear runs up the blade from the wound,
  masked to the blade's alpha.
- **Halo fix**: Duo's alpha is eroded with a 9px MinFilter. His cutout carries a white
  fringe from the page background, and anything less leaves a visible outline.

`python3 render_svg.py verbavia_logo.svg out.png 1200` re-renders the logo at any size.
`python3 make_kill3.py` rebuilds both crops.

---

## v4 — planted sword (`make_sword.py`)

Minimal edit off v3. Duo's pose, the blood pool, the drips, the floor and the cone are all
unchanged; only the weapon and the mascot's position moved.

- **Sword replaces the dagger**: longer blade with a fuller (the central groove) running most
  of its length, flared quillons on the crossguard with rounded terminals, a wrapped grip
  and a disc pommel.
- **Near-vertical**: the blade sits at ~77° so it reads as *planted* and standing in him
  rather than mid-thrust. Driven deeper too — the tip sits at 70% of his body height.
- **Mascot beside the hilt** rather than gripping it, which is what "has planted it" looks
  like.

The wound, drips and blade smear all reposition automatically: the entry point is computed
by walking back along the blade axis, so changing the angle or length moves everything
downstream with it. Length is the one value to watch — much above `px(520)` and the hilt
runs off the top of the frame.

---

## v5 — drop-in overlay (`make_sword_overlay.py`)

For compositing onto Duolingo's own "It's Duo or Die!" frame, which can't be edited here —
images pasted into chat render but never land on disk, and `/mnt/attach` stays empty.

`sword_overlay.png` is **962x655 with alpha**, matching that screenshot pixel for pixel, so
it aligns at 0,0 with no scaling. Contents: the planted sword, the entry wound, drips, the
ground pool and the blade smear.

Three masking rules make it composite correctly on top of an image it can't see:

- **Blade** is erased wherever Duo's silhouette is, so the tip reads as buried rather than
  lying across him.
- **Drips** are clipped *to* the silhouette, so they run down his body and stop at his edge.
- **Pool** is clipped to the *inverse* silhouette, so it rings him on the stage instead of
  painting over him.

Duo's silhouette is traced by hand in `duo_mask` as five ellipses matching that frame. If
the real file ever lands on disk, swap that trace for his actual alpha and everything
downstream (entry point, drips, pool) recomputes itself.
