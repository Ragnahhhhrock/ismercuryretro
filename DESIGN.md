# Design system: ismercuryretro.com

The system the live site already uses, written down, plus the logo.
Pages: `index.html` (Today) plus `dates/`, `science/`, `astrology/`, `tips/` (each a real page sharing `style.css` and `app.js`).
Tokens: `tokens.css` (mirrors the CSS in `index.html`). Live reference: `style-guide.html`.

## Idea
The answer is the page. One word, set huge, in the color of its state: burnt orange for YES, teal for NO. Everything else is quiet: one 460px column, soft panels, monospace for data.

## Logo
The Mercury symbol ☿ (U+263F) in the ink color next to ℞, the astrological symbol for retrograde (U+211E), in retrograde orange.
- `assets/logo.svg` lockup for light backgrounds, `assets/logo-dark.svg` for dark ones.
- `assets/logo-icon.svg` / `logo-icon-dark.svg` the ☿ alone. `assets/logo-glyph.svg` / `logo-glyph-dark.svg` the ℞ glyph alone.
- `assets/favicon.svg`, apple-touch and manifest icons: white ℞ on an orange tile, so it reads at small sizes.
- Both symbols are saved as vector outlines (℞ from Inter ExtraBold, SIL Open Font License, in `assets/rx-glyph.txt`; ☿ from DejaVu Sans Bold, thickened slightly, in `assets/mercury-glyph.txt`), so they render the same everywhere without a font.
- Clear space: half the logo height on every side. Minimum: lockup 80px wide, ☿ 16px tall, bare ℞ 12px tall.
- Don't recolor the glyphs, redraw or retype the glyph, stack the lockup or place it on low-contrast backgrounds.

## Color
Light / dark. Use semantic tokens, never raw hex, in components.
| Token | Light | Dark |
|---|---|---|
| --bg | #EAEFF5 | #0B1220 |
| --panel | #F7F9FC | #121B2D |
| --fg | #0F1A2E | #E7ECF5 |
| --muted | #55627A | #9AA7BF |
| --line | #CBD4E2 | #26324A |
| --yes / --yes-bg | #C2410C / #FBE4D6 | #FF9A63 / #2B1A12 |
| --no / --no-bg | #0F766E / #D5EEEA | #5EE0C4 / #0F2A27 |

`data-state="yes|no"` on the page wrapper sets `--state` and `--state-bg`. Answer colors are for large text, tags and the active tab only.

## Type
- Bricolage Grotesque for display and body. Answer: 800, line-height 0.86, tracking −0.035em, clamp(6.5rem, 36vw, 11rem).
- JetBrains Mono for data, labels and tags (tabular numbers; labels uppercase, +0.08em).
- Body 16px / 1.5, max 65ch. Page title 2–2.6rem / 800. Section title 1.3rem / 700.

## Shape and space
460px column, 20px between blocks. Radii: verdict 22, panel 16, stat 14, tab 12, control 10, tag 6, chip/button pill. 1px `--line` borders, no shadows. Controls at least 44px tall; tab bar items 56px.

## Components
Verdict card, panels with label + rows, retrograde period list with "now" tag, chips, buttons and date input, stat tiles, callout, bottom tab bar, chart styles. All are demonstrated in `style-guide.html`.

## Motion and access
No decorative animation, except one data intro on Today at page load (`.intro` on `#app`, set in `app.js`, rules at the end of `style.css`): the answer rises in, numbers count up, the chart line draws, then the retrograde shading and markers fade in. It plays once, is off for reduced motion, and never replays when the date changes. 1px press on buttons (off for reduced motion). 2px focus outline in the state color. The answer is `role="status"` and always shows the word, never color alone.

## Voice
Answer first, then facts. Plain verbs, no horoscope language. Controls say what they do.

## Metadata and social
`head.html` holds the title, description, canonical, theme colors, icons, Open Graph, Twitter card and JSON-LD. `assets/og-image.png` (1200×630) and `assets/twitter-card.png` (1200×600) show the logo, the question, and NO and YES split diagonally, so they stay correct whatever today's answer is.

Regenerate logos, icons, cards and the style guide with `python3 build.py` (needs fonttools, brotli, Playwright + Chromium). Sources: `build.py`, `style-guide.src.html`.
