# Design system: Transit

Site: ismercuryretro.com. Job: give a yes or no answer to "Is Mercury retrograde?" instantly, then the dates.
Tokens live in `tokens.css`. Live reference: `style-guide.html`.

## Idea
The answer is the page, and the page changes sides with it.
- **No** (Mercury moving direct): Daybreak, a light page.
- **Yes** (retrograde): Transit, a dark ultramarine page.
Set `data-state="direct"` or `data-state="retrograde"` on `<html>`. Components only use semantic tokens (`--bg`, `--text`, `--accent`, …), so they follow automatically.

The one memorable element is the answer set huge (Bricolage Grotesque 800, 75% width, line-height 0.82) above a thin line tracing Mercury's apparent loop. The line draws itself once on load. Nothing else animates on its own.

## Color
| Token | Hex | Use |
|---|---|---|
| Ultramarine 900 | #12154f | Ink on Daybreak |
| Ultramarine 800 | #1a1f6b | Transit background |
| Daybreak 100 | #e9eeff | No background |
| Orchid 100 | #ffe3f2 | Text on Transit |
| Signal 500 | #ff5fa2 | Yes answer, accent on Transit |
| Clear 600 | #1b7f6d | No answer, accent on Daybreak |
| Copper 500 | #b8795a | Mercury itself, at most once per page |

Contrast: ink on Daybreak 14.6:1; orchid on Transit 12.1:1; Signal on Transit 5.1:1; Clear on Daybreak 4.2:1 (large text such as the answer, and UI, never small body text).

## Type
- Display: Bricolage Grotesque (variable, weight 200–800, width 75–100%).
- Body: Instrument Sans (variable).
- Sentence case everywhere. Only the answer is set in capitals.
- Body 17px / 1.55, measure 60ch. Scale: answer clamp(7rem, 34vw, 26rem); h1 2–3.5rem; h2 1.5–2rem; h3 1.25rem; small 0.875rem.

## Layout
Left-aligned. Answer first, full width, then one supporting line and the dates. Single column up to 1040px. 4px spacing scale; 16px gutter on mobile.

## Shape and depth
Two radii: 6px (controls, cards), full pill (status label). 2px borders. No shadows.

## Motion
One load animation (loop draws, 1600ms). UI feedback 140ms. Both go to 0 under `prefers-reduced-motion`.

## Accessibility
Visible 3px focus ring in `--accent`, text contrast ≥ 4.5:1, works at 320px wide, state is conveyed by the word YES/NO as well as color.

## Voice
Answer first, then facts. Plain verbs, no horoscope language. Buttons name their action ("Copy link").

## Metadata and social
- `head.html`: title, description, canonical, theme-color, icons, Open Graph, Twitter card, JSON-LD.
- `assets/og-image.png` 1200×630 and `assets/twitter-card.png` 1200×600: a diagonal split, NO on Daybreak and YES on Transit. State-independent so it stays correct whatever the answer is.
- Regenerate with `python3 build.py` (needs Playwright + Chromium). Sources: `build.py`, `style-guide.src.html`.
