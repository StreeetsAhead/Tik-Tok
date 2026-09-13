# Verbavia ad (`make_ad.py`)

1080x1350 feed, 1:1 and 1080x1920 story, rendered at 3x supersample. Brand palette:
indigo #4F46E5, ink #1A1E30, surface #F7F8FB, Inter variable.

## Source of truth

Every line is the live site's own copy, re-scraped at build time (`site_copy.txt`):

- headline and subhead — the current hero, verbatim
- the badge "8 LANGUAGES · A1 TO C2 · FREE" — the hero badge
- the three coverage figures and their caveat — the "WHY THE ORDER MATTERS" section
- "8 courses, one method" and "no account needed" — the language picker
- "web and Android" — the footer

**Not used: the 300-lesson figure.** The site still says "A 300-lesson syllabus that runs
to C2" in its comparison table, but the course is past that now — worth fixing on the site,
since it undersells. The ad says "A1 to C2" instead, which stays true as the course grows.

**Not used: the Pacific languages.** An earlier draft led on Tok Pisin, Samoan, Fijian,
Marshallese, Kiribati, Palauan and Rapa Nui. Only eight courses are live, all non-Pacific.
`audit.py` re-checks: it counts `.language-card` elements and prints each name, so the ad's
language row can be regenerated against reality rather than memory.

## The chart

Magnitude of one measure across three ordered categories, so: horizontal bars, **one hue**,
no legend (a single series is named by its own title), direct value labels on every bar,
recessive track, 6px rounded ends.

The 1,000-word row is the subject of the headline, so it carries full-strength indigo and
bold ink while the other two sit in a lighter tint of the same hue — a focus/context
treatment within one hue, not a categorical palette. The caveat line travels with the
figures rather than being dropped, because "about" is doing real work in those numbers.

An earlier version encoded Verbavia-vs-other-apps as indigo-vs-grey and failed the
validator (`#9CA3AF` below the chroma floor, contrast 2.47). The fix was to change form,
not colour.
