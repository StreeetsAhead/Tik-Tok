# "come and try" — comeback frame

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
