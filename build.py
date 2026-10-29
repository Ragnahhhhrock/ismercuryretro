#!/usr/bin/env python3
"""Builds favicon/mark SVGs, the social card HTML, renders the PNGs and
fills the loop path into style-guide.html.  Run: python3 build.py"""
import pathlib
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).parent
loop_wide = (root / "assets/loop-wide.txt").read_text().strip()
loop_mark = (root / "assets/loop-mark.txt").read_text().strip()

INK, DAY, PINK, ORCHID, COPPER = "#12154f", "#e9eeff", "#ff5fa2", "#ffe3f2", "#b8795a"
TRANSIT = "#1a1f6b"

# ---- Mark / favicon: Mercury's looping path on Transit blue ----
mark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="{TRANSIT}"/>
<path d="{loop_mark}" fill="none" stroke="{PINK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="32" cy="32" r="0" fill="{COPPER}"/>
</svg>'''
(root / "assets/favicon.svg").write_text(mark)
(root / "assets/mark.svg").write_text(mark)

# ---- Social card (shared by Open Graph 1200x630 and Twitter 1200x600) ----
def card_html(h):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<style>
@font-face{{font-family:"Bricolage Grotesque";src:url("../fonts/bricolage-grotesque.woff2");font-weight:200 800;font-stretch:75% 100%}}
@font-face{{font-family:"Instrument Sans";src:url("../fonts/instrument-sans.woff2");font-weight:400 700;font-stretch:75% 100%}}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:{h}px;position:relative;overflow:hidden;font-family:"Instrument Sans",sans-serif}}
.layer{{position:absolute;inset:0}}
.day{{background:{DAY};color:{INK}}}
.night{{background:{TRANSIT};color:{ORCHID};clip-path:polygon(58% 0,100% 0,100% 100%,46% 100%)}}
.q{{position:absolute;left:64px;top:52px;font:600 46px/1.1 "Bricolage Grotesque";font-stretch:100%;letter-spacing:-0.01em}}
.url{{position:absolute;right:64px;top:62px;font:500 28px/1 "Instrument Sans";color:{PINK}}}
.ans{{position:absolute;bottom:{h-h+48}px;font:800 380px/0.8 "Bricolage Grotesque";font-stretch:75%;letter-spacing:-0.03em}}
.no{{left:56px}}
.yes{{right:56px;color:{PINK}}}
svg.loop{{position:absolute;left:0;bottom:0;width:1200px;height:{h}px}}
</style></head><body>
<div class="layer day">
  <div class="q">Is Mercury retrograde?</div>
  <div class="ans no">NO</div>
</div>
<div class="layer night">
  <div class="url">ismercuryretro.com</div>
  <div class="ans yes">YES</div>
</div>
</body></html>'''

(root / "social/og.html").write_text(card_html(630))
(root / "social/twitter.html").write_text(card_html(600))

# ---- style-guide.html: inject loop path ----
src = root / "style-guide.src.html"
if src.exists():
    (root / "style-guide.html").write_text(src.read_text().replace("{{LOOP_WIDE}}", loop_wide))

# ---- Render ----
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, h, out in (("og", 630, "assets/og-image.png"), ("twitter", 600, "assets/twitter-card.png")):
        pg = b.new_page(viewport={"width": 1200, "height": h})
        pg.goto((root / f"social/{name}.html").as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(root / out))
    pg = b.new_page(viewport={"width": 180, "height": 180})
    pg.set_content(f'<body style="margin:0">{mark.replace("<svg ", "<svg width=180 height=180 ")}</body>')
    pg.screenshot(path=str(root / "assets/apple-touch-icon.png"))
    b.close()
print("built")
