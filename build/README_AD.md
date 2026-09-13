# Verbavia ad (`make_ad.py`)

1080x1350 (4:5) plus a 1:1 crop, rendered at 3x supersample. Built on Verbavia's own
palette: indigo #4F46E5, ink #1A1E30, surface #F7F8FB, Inter variable.

## Everything on it is sourced, not invented

| Claim | Where it comes from |
|---|---|
| "Learn a language, actually get fluent." | the site's own hero headline |
| "One real lesson a day — from your first word to C2." | hero subhead |
| "A 300-lesson syllabus, A1 through C2" | comparison section |
| "Grammar explained — the rule first, then the test" | "Teaches the rule properly, then tests it" |
| "most apps plateau here" at A2 | the site's own "Plateau somewhere around A2" |
| 15 languages, all flags | scraped from the live page |
| Free | the hero badge |

Flags are real crops from a full-page capture, not emoji — several of these languages
(Rapa Nui, Shanghainese, Esperanto) have no flag emoji at all. They're located by scanning
the page for saturated pixel bands, which finds all 15 without needing selectors, then
tightened with a per-language height cap so neighbouring label text doesn't bleed in.

## The CEFR meter

Originally drafted as indigo-vs-grey (Verbavia vs everyone else). The dataviz validator
failed it: `#9CA3AF` falls below the chroma floor and "reads gray," with contrast 2.47
against the surface.

That's the right call, and the fix isn't a different grey — it's a different **form**. A
two-category comparison was never the honest encoding here. It's now a single-hue meter on
a recessive track with one annotated reference marker at A2. One hue, direct labels on every
level, identity never carried by colour alone.

```
node scripts/validate_palette.js "#4F46E5,#9CA3AF" --mode light
  [FAIL] Chroma floor      below floor (reads gray): #9CA3AF 0.019
  [WARN] Contrast          below 3:1: #9CA3AF 2.47
```

## Copy note

"including seven nobody else teaches" was softened to "most apps ignore" — the stronger
version is hard to prove, since another app may well carry Samoan. The weaker claim is
defensible and lands the same way.
