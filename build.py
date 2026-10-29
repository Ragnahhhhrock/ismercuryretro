#!/usr/bin/env python3
"""Builds the logo SVGs, icons, social cards (PNG) and style-guide.html.
Needs: fonttools, brotli, playwright (+ chromium).   Run: python3 build.py"""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).parent
(root / "assets").mkdir(exist_ok=True)
(root / "social").mkdir(exist_ok=True)

# ---- Palette (matches tokens.css) ----
FG, BG, PANEL = "#0F1A2E", "#EAEFF5", "#F7F9FC"
YES, YES_BG, NO, NO_BG = "#C2410C", "#FBE4D6", "#0F766E", "#D5EEEA"
D_FG, D_YES = "#E7ECF5", "#FF9A63"

# ---- Glyph outlines for "R" and "x" (Bricolage Grotesque 800) ----
font = TTFont(root / "fonts/bricolage-grotesque.woff2")
gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm

def glyph(ch, size, x, baseline):
    """SVG path of a character; size = em in px; origin at (x, baseline)."""
    s = size / upm
    pen = SVGPathPen(gs)
    gs[cmap[ord(ch)]].draw(TransformPen(pen, (s, 0, 0, -s, x, baseline)))
    return pen.getCommands(), gs[cmap[ord(ch)]].width * s

_gw, _gd = (root / "assets/rx-glyph.txt").read_text().split("\n")[:2]
GLYPH_W, GLYPH_D = float(_gw), _gd

_mw, _md = (root / "assets/mercury-glyph.txt").read_text().split("\n")[:2]
MERC_W, MERC_D = float(_mw), _md   # U+263F outlines from DejaVu Sans Bold (free license), 100 units tall

def merc(x, cy, height, fill):
    """The Mercury symbol with its left edge at x, centred on cy. Returns (svg, width)."""
    k = height / 100
    return (f'<path transform="translate({x:.2f} {cy - height / 2:.2f}) scale({k:.4f})" d="{MERC_D}" fill="{fill}" stroke="{fill}" stroke-width="5" stroke-linejoin="round"/>', MERC_W * k)

def rx(x, cy, height, fill):
    """The retrograde glyph with its left edge at x, vertically centred on cy. Returns (svg, width)."""
    k = height / 100
    return (f'<path transform="translate({x:.2f} {cy - height / 2:.2f}) scale({k:.4f})" d="{GLYPH_D}" fill="{fill}"/>',
            GLYPH_W * k)

def lockup(fg, xcol, uid="lk", h=100):
    """Mercury symbol in the ink color + retrograde glyph in orange."""
    m, mw = merc(0, 50, 92, fg)
    gx = mw + 16
    g, gw = rx(gx, 50, 54, xcol)
    W = gx + gw + 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {h}" role="img" aria-label="Mercury retrograde">{m}{g}</svg>'), W

def icon_only(fill, uid="ic"):
    m, mw = merc(0, 50, 100, fill)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw:.0f} 100" role="img" aria-label="Mercury">{m}</svg>'

def glyph_svg(fill):
    body, gw = rx(0, 50, 100, fill)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {gw:.0f} 100" role="img" aria-label="Retrograde">{body}</svg>'

def tile_icon(bg=None, pad=0, size=64):
    """Orange tile with the white glyph: favicon, touch icon, manifest icons."""
    t = size - 2 * pad
    gh = t * 0.58
    gw = GLYPH_W * gh / 100
    body, _ = rx(size / 2 - gw / 2, size / 2, gh, "#FFFFFF")
    if bg:
        base = f'<rect width="{size}" height="{size}" fill="{bg}"/><rect x="{pad}" y="{pad}" width="{t}" height="{t}" rx="{t*0.22:.1f}" fill="{YES}"/>'
    else:
        base = f'<rect width="{size}" height="{size}" rx="{size*0.22:.1f}" fill="{YES}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">{base}{body}</svg>'

# Write standalone logo files
light, LW = lockup(FG, YES, "a")
dark, _ = lockup(D_FG, D_YES, "b")
(root / "assets/logo.svg").write_text(light)
(root / "assets/logo-dark.svg").write_text(dark)
(root / "assets/logo-icon.svg").write_text(icon_only(FG))
(root / "assets/logo-icon-dark.svg").write_text(icon_only(D_FG))
(root / "assets/logo-glyph.svg").write_text(glyph_svg(YES))
(root / "assets/logo-glyph-dark.svg").write_text(glyph_svg(D_YES))
fav = tile_icon()
(root / "assets/favicon.svg").write_text(fav)
(root / "assets/mark.svg").write_text(fav)

# ---- Social cards ----
def card_html(h):
    lk, _ = lockup(FG, YES, "c")
    lk = lk.replace("<svg ", '<svg height="84" ')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<style>
@font-face{{font-family:"Bricolage Grotesque";src:url("../fonts/bricolage-grotesque.woff2");font-weight:200 800}}
@font-face{{font-family:"JetBrains Mono";src:url("../fonts/jetbrains-mono.woff2");font-weight:100 800}}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:{h}px;position:relative;overflow:hidden;font-family:"Bricolage Grotesque",sans-serif;color:{FG}}}
.layer{{position:absolute;inset:0}}
.no{{background:{NO_BG}}}
.yes{{background:{YES_BG};clip-path:polygon(57% 0,100% 0,100% 100%,45% 100%)}}
.logo{{position:absolute;left:60px;top:40px}}
.q{{position:absolute;left:64px;top:144px;font:600 40px/1.1 "Bricolage Grotesque";letter-spacing:-0.005em}}
.url{{position:absolute;right:64px;top:66px;font:500 26px/1 "JetBrains Mono"}}
.ans{{position:absolute;bottom:34px;font:800 280px/0.86 "Bricolage Grotesque";letter-spacing:-0.035em}}
.a-no{{left:56px;color:{NO}}}
.a-yes{{right:52px;color:{YES}}}
</style></head><body>
<div class="layer no"><div class="logo">{lk}</div><div class="q">Is Mercury retrograde?</div><div class="ans a-no">NO</div></div>
<div class="layer yes"><div class="url">ismercuryretro.com</div><div class="ans a-yes">YES</div></div>
</body></html>'''

(root / "social/og.html").write_text(card_html(630))
(root / "social/twitter.html").write_text(card_html(600))

# ---- Style guide: inject inline logos (theme-aware via CSS variables) ----
src = root / "style-guide.src.html"
if src.exists():
    lk_var, _ = lockup("var(--fg)", "var(--yes)", "g1")
    lk_dark, _ = lockup(D_FG, D_YES, "g2")
    lk_light, _ = lockup(FG, YES, "g3")
    html = (src.read_text()
            .replace("{{LOGO_THEMED}}", lk_var)
            .replace("{{LOGO_ON_DARK}}", lk_dark)
            .replace("{{LOGO_ON_LIGHT}}", lk_light)
            .replace("{{LOGO_ICON}}", icon_only("var(--fg)"))
            .replace("{{LOGO_TILE}}", tile_icon())
            .replace("{{LOGO_GLYPH}}", glyph_svg("var(--yes)")))
    (root / "style-guide.html").write_text(html)

# ---- Render PNGs ----
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, h, out in (("og", 630, "assets/og-image.png"), ("twitter", 600, "assets/twitter-card.png")):
        pg = b.new_page(viewport={"width": 1200, "height": h})
        pg.goto((root / f"social/{name}.html").as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(root / out))
    for size, out, bg in ((180, "assets/apple-touch-icon.png", BG), (192, "assets/icon-192.png", BG), (512, "assets/icon-512.png", BG)):
        pg = b.new_page(viewport={"width": size, "height": size})
        svg = tile_icon(bg, pad=int(size*0.06), size=size).replace("<svg ", f'<svg width="{size}" height="{size}" ', 1)
        pg.set_content(f'<body style="margin:0">{svg}</body>')
        pg.screenshot(path=str(root / out))
    b.close()
print("built")
