# The World Today — Sunday 22 November 2026

One image summing up the world's news of Sunday 22 November 2026:
54 stories from one day — 3 lead stories, 12 medium stories, 39 more in
"Also Today", a world map with numbered pins, a By the Numbers strip, and a
markets ticker labelled with the Friday 20 November close (markets shut on
Sunday).

`main.py` is pure Python 3 standard library (no network, no clock, no
randomness). It draws the 1024x1024 front page with its own 5x7 bitmap font
and PNG encoder, and writes it deterministically to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py`

Facts: researched from Reuters, AP, BBC, CNN, Al Jazeera, AFP, Sky Sports,
The Times, FT and One Turn for 22 Nov 2026. Final scores confirmed after the
research cutoff: Liverpool 4-0 Manchester United (Reuters/Sky); NFL Week 11
early-game finals via Sportradar (late games not claimed). Markets are the
official Friday 20 Nov settlements.
