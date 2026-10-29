"""Renders the launch-post images. Run: python3 social/launch/build_launch.py (needs Playwright + Chromium)."""
import pathlib, re
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parents[2]
out = pathlib.Path(__file__).resolve().parent
fonts = f'''@font-face{{font-family:"Bricolage Grotesque";src:url("file://{root}/fonts/bricolage-grotesque.woff2");font-weight:200 800}}
@font-face{{font-family:"JetBrains Mono";src:url("file://{root}/fonts/jetbrains-mono.woff2");font-weight:100 800}}
*{{box-sizing:border-box;margin:0}}body{{position:relative;overflow:hidden;font-family:"Bricolage Grotesque",sans-serif}}
.abs{{position:absolute}}'''

def logo(dark, h):
    svg = (root / "assets" / ("logo-dark.svg" if dark else "logo.svg")).read_text()
    return re.sub(r"<svg ", f'<svg height="{h}" ', svg, count=1)

pages = {}

# Instagram 1080x1350, light, rising diagonal split
pages["instagram-1080x1350"] = (1080, 1350, f'''<style>{fonts}
body{{width:1080px;height:1350px;background:#D5EEEA;color:#0F1A2E}}
.yes{{inset:0;background:#FBE4D6;clip-path:polygon(0 72%,100% 40%,100% 100%,0 100%)}}
.ans{{font:800 470px/0.86 "Bricolage Grotesque";letter-spacing:-0.035em}}
</style><div class="abs" style="left:72px;top:72px">{logo(False,110)}</div>
<div class="abs" style="right:72px;top:96px;font:500 32px/1 'JetBrains Mono'">ismercuryretro.com</div>
<div class="abs" style="left:72px;top:260px;font:600 64px/1.08 'Bricolage Grotesque'">Is Mercury<br>retrograde?</div>
<div class="abs yes"></div>
<div class="abs ans" style="left:64px;top:430px;color:#0F766E">NO</div>
<div class="abs ans" style="right:60px;bottom:64px;color:#C2410C">YES</div>''')

# Threads 1080x1080, dark, falling diagonal
pages["threads-1080x1080"] = (1080, 1080, f'''<style>{fonts}
body{{width:1080px;height:1080px;background:#0F2A27;color:#E7ECF5}}
.yes{{inset:0;background:#2B1A12;clip-path:polygon(100% 0,100% 100%,0 100%,0 74%)}}
.ans{{font:800 360px/0.86 "Bricolage Grotesque";letter-spacing:-0.035em}}
</style><div class="abs" style="left:72px;top:72px">{logo(True,96)}</div>
<div class="abs" style="left:72px;top:216px;font:600 56px/1.1 'Bricolage Grotesque'">Is Mercury retrograde?</div>
<div class="abs yes"></div>
<div class="abs ans" style="left:60px;top:310px;color:#5EE0C4">NO</div>
<div class="abs ans" style="right:56px;bottom:56px;color:#FF9A63">YES</div>
<div class="abs" style="left:72px;bottom:72px;font:500 30px/1 'JetBrains Mono';color:#9AA7BF">ismercuryretro.com</div>''')

# X 1600x900, light, brand OG split scaled up
pages["x-1600x900"] = (1600, 900, f'''<style>{fonts}
body{{width:1600px;height:900px;background:#D5EEEA;color:#0F1A2E}}
.yes{{inset:0;background:#FBE4D6;clip-path:polygon(57% 0,100% 0,100% 100%,45% 100%)}}
.ans{{font:800 400px/0.86 "Bricolage Grotesque";letter-spacing:-0.035em}}
.chip{{font:600 24px/1 'JetBrains Mono';letter-spacing:.08em;text-transform:uppercase;border:2px solid #CBD4E2;background:#F7F9FC;border-radius:999px;padding:14px 22px;color:#55627A}}
</style><div class="abs" style="left:80px;top:60px">{logo(False,116)}</div>
<div class="abs" style="left:84px;top:210px;font:600 62px/1.1 'Bricolage Grotesque'">Is Mercury retrograde?</div>
<div class="abs" style="left:84px;top:300px;display:flex;gap:14px"><span class="chip">Live answer</span><span class="chip">Countdown</span></div>
<div class="abs ans" style="left:72px;bottom:44px;color:#0F766E">NO</div>
<div class="abs yes"></div>
<div class="abs" style="right:84px;top:92px;font:500 36px/1 'JetBrains Mono'">ismercuryretro.com</div>
<div class="abs ans" style="right:70px;bottom:44px;color:#C2410C">YES</div>''')

# LinkedIn 1200x627, light, panel + two verdict cards
pages["linkedin-1200x627"] = (1200, 627, f'''<style>{fonts}
body{{width:1200px;height:627px;background:#EAEFF5;color:#0F1A2E}}
.card{{width:250px;height:420px;border:2px solid #CBD4E2;border-radius:22px;display:flex;flex-direction:column;justify-content:space-between;padding:30px 28px}}
.lab{{font:600 22px/1 'JetBrains Mono';letter-spacing:.08em;text-transform:uppercase}}
.big{{font:800 100px/0.86 "Bricolage Grotesque";letter-spacing:-0.035em}}
</style><div class="abs" style="left:72px;top:64px">{logo(False,84)}</div>
<div class="abs" style="left:72px;top:210px;font:800 62px/1.02 'Bricolage Grotesque';letter-spacing:-0.02em;width:520px">One question.<br>One word.</div>
<div class="abs" style="left:72px;top:360px;font:500 28px/1.4 'Bricolage Grotesque';color:#55627A;width:480px">A live yes or no on Mercury retrograde, with a countdown to when it ends.</div>
<div class="abs" style="left:72px;bottom:60px;font:500 26px/1 'JetBrains Mono'">ismercuryretro.com</div>
<div class="abs card" style="left:660px;top:104px;background:#D5EEEA;color:#0F766E"><span class="lab">Direct</span><span class="big">NO</span></div>
<div class="abs card" style="left:934px;top:104px;background:#FBE4D6;color:#C2410C"><span class="lab">Retrograde</span><span class="big">YES</span></div>''')

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (w, h, html) in pages.items():
        f = out / f"{name}.html"; f.write_text(f'<!doctype html><html><head><meta charset="utf-8"></head><body>{html}</body></html>')
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(f"file://{f}"); pg.wait_for_timeout(400)
        pg.screenshot(path=str(out / f"{name}.png")); pg.close()
        f.unlink()
    b.close()
