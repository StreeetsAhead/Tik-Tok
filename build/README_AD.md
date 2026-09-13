# Verbavia ad (`make_ad.py`)

1080x1350 feed, 1:1, 1080x1920 story. 3x supersample. Indigo #4F46E5, ink #1A1E30,
surface #F7F8FB, Inter variable.

## What it argues

That Verbavia is a **course**, not a vocabulary tool. Five skill cards — Vocabulary,
Grammar, Reading, Listening, Writing — carry the top half, and vocabulary is deliberately
one of five rather than the headline.

An earlier draft led on the frequency chart (100 / 1,000 / 3,000 words vs share of speech).
It was accurate and it tested well as a graphic, but it left the impression the product was
flashcards. Frequency is the *method*, not the offer; it now appears as one line inside the
lesson anatomy instead of as the hero.

## Source of truth

Scraped live, not remembered. `captures/audit_languages.py` counts live courses;
`lesson_copy.txt` and `course_copy.txt` hold the in-product copy.

| On the ad | Where it comes from |
|---|---|
| "A real course, not a tapping game." | the course intro screen, verbatim |
| Vocabulary · Grammar · Reading · Listening · Writing | the course dashboard's own skill list |
| 3 reading parts and 3 listening parts | lesson-length chooser, Complete tier |
| 8 new words a lesson | same |
| One grammar point, explained then tested | same, plus the comparison table |
| A writing task, from lesson 7 | same |
| Around 20–30 minutes | same |
| "8 LANGUAGES · A1 TO C2 · FREE" | hero badge |
| No account needed · web and Android | picker copy and footer |

The lesson figures are the **Complete** tier, so the ad says so in a footnote — Balanced and
Essentials are shorter. Quoting the fullest tier without that note would overstate it.

**Deliberately absent:** the 300-lesson count (the course has outgrown it; the site's own
comparison table still carries the stale figure), and the Pacific languages (listed in an
older build of the site, not currently live).
