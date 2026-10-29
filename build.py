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

# ---- Planet: a flat, emoji-style Mercury in a 100x100 box ----
def planet(ox=0, oy=0, k=1.0, uid="p"):
    t = f'transform="translate({ox} {oy}) scale({k})"'
    return f'''<g {t}>
<defs><clipPath id="{uid}"><circle cx="50" cy="50" r="46"/></clipPath></defs>
<circle cx="50" cy="50" r="46" fill="#8E877F"/>
<circle cx="44" cy="44" r="37" fill="#C9C2B9" clip-path="url(#{uid})"/>
<g fill="#A9A198">
<circle cx="31" cy="38" r="8"/><circle cx="60" cy="29" r="5.5"/><circle cx="62" cy="60" r="9.5"/>
<circle cx="35" cy="67" r="5.5"/><circle cx="74" cy="42" r="3.5"/>
</g>
<g fill="#B8B0A6"><circle cx="29" cy="36" r="3.2"/><circle cx="59" cy="27.5" r="2.2"/><circle cx="60" cy="57.5" r="3.8"/></g>
</g>'''

def rx(x, cy, cap, fg, xcol):
    """'Rx' with cap-height `cap`, vertically centred on cy. x is smaller, like the retrograde symbol."""
    size = cap / 0.70                      # Bricolage cap-height ~0.70 em
    base = cy + cap / 2
    r_d, r_w = glyph("R", size, x, base)
    x_d, x_w = glyph("x", size * 0.78, x + r_w - size * 0.03, base + size * 0.06)
    return (f'<path d="{r_d}" fill="{fg}"/><path d="{x_d}" fill="{xcol}"/>', r_w + x_w - size * 0.03)

def lockup(fg, xcol, uid="lk", h=100):
    body, w = rx(114, 50, 58, fg, xcol)
    W = 114 + w + 4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {h}" role="img" aria-label="Mercury Rx">'
           f'{planet(0, 0, 1, uid)}{body}</svg>')
    return svg, W

def icon_only(uid="ic"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="Mercury">{planet(0, 0, 1, uid)}</svg>'

def badge_icon(bg=None, uid="fv", pad=0):
    """Planet with an orange Rx badge: favicon, touch icon, manifest icons. 64x64 box."""
    d = 64
    bgrect = f'<rect width="{d}" height="{d}" fill="{bg}"/>' if bg else ""
    body, w = rx(0, 0, 11, "#FFFFFF", "#FFFFFF")
    # centre the Rx inside the badge
    body = body.replace("<path", "<path transform=\"translate(%.2f %.2f)\"" % (46 - w / 2, 46), 2)
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {d} {d}">{bgrect}'
         f'{planet(pad + 2, pad + 2, (d - 2*pad - 4) / 100, uid)}'
         f'<circle cx="46" cy="46" r="16.5" fill="{YES}" stroke="{BG if bg else "#FFFFFF"}" stroke-width="2.5"/>'
         f'{body}</svg>')
    return s

# Write standalone logo files
light, LW = lockup(FG, YES, "a")
dark, _ = lockup(D_FG, D_YES, "b")
(root / "assets/logo.svg").write_text(light)
(root / "assets/logo-dark.svg").write_text(dark)
(root / "assets/logo-icon.svg").write_text(icon_only())
fav = badge_icon(None, "f")
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
            .replace("{{LOGO_ICON}}", icon_only("g4"))
            .replace("{{LOGO_BADGE}}", badge_icon(None, "g5")))
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
        svg = badge_icon(bg, "t", pad=6).replace("<svg ", f'<svg width="{size}" height="{size}" ')
        pg.set_content(f'<body style="margin:0">{svg}</body>')
        pg.screenshot(path=str(root / out))
    b.close()
print("built")
