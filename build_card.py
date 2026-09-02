#!/usr/bin/env python3
"""Regenerate dark_mode.svg and light_mode.svg for CPollreis.

Usage:  python3 build_card.py

Edit the RIGHT list below to change info-panel content, then run this.
Only the id="..._data" spans are touched by the daily Action; everything
else here is authored.

To rebuild the ASCII portrait from a new photo (writes ascii_portrait.txt):

  magick ASCII_photo.jpg -crop 700x950+128+10 +repage -colorspace Gray \\
    -sigmoidal-contrast 5,20% -clahe 14x14%+128+3 -contrast-stretch 2%x5% \\
    -brightness-contrast 2x-10 -attenuate 0.16 +noise Gaussian /tmp/p.png
  chafa -f symbols --symbols ascii -c none -s 36x25 --stretch --dither ordered \\
    /tmp/p.png | sed 's/[[:space:]]*$//' > ascii_portrait.txt

  (needs: brew install imagemagick chafa. Adjust the -crop box to your photo;
   keep the grid at 36x25 so it fits the card.)
"""
import pathlib

BASE = pathlib.Path(__file__).parent
SP = pathlib.Path(__file__).parent

X_ASCII, X_INFO = 15, 390
Y0, STEP = 30, 20
VCOL, WRAP = 22, 34          # right panel: value column, wrap width

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def wrap_terms(value, width):
    """Wrap a comma-separated list without breaking individual terms."""
    terms = [t.strip() for t in value.split(",")]
    lines, cur = [], ""
    for t in terms:
        cand = t if not cur else cur + ", " + t
        if len(cand) <= width or not cur:
            cur = cand
        else:
            lines.append(cur + ",")
            cur = t
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- ASCII portrait
# Both modes use ascii_portrait.txt. To give dark mode a different (e.g.
# inverted) render, drop it in as ascii_portrait_dark.txt and it's picked up.
def load_ascii(name):
    p = SP / name
    if not p.exists():
        p = SP / "ascii_portrait.txt"
    lines = p.read_text().split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    return lines

def ascii_block(fill, lines):
    out = [f'<text x="{X_ASCII}" y="{Y0}" fill="{fill}" class="ascii">']
    for i, ln in enumerate(lines):
        out.append(f'<tspan x="{X_ASCII}" y="{Y0+i*STEP}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "\n".join(out), Y0 + (len(lines)-1)*STEP

# ---------------------------------------------------------------- right panel
RIGHT = [
    ("hdr",  "caleb@pollreis"),
    ("kv",   "Major", "Computer Engineering (Co-op)"),
    ("gap",),
    ("head", "Skills"),
    ("kv",   "Languages", "C++, C, Python, Verilog, Java"),
    ("kv",   "Robotics.CV", "ROS2, OpenCV, PPO, NVIDIA Jetson Orin"),
    ("kv",   "ML", "PyTorch, TensorRT, CUDA, ONNX, Deep Learning, CNN, YOLO, "
                   "CLIP, Reinforcement Learning, "
                   "AWS (EC2/S3/SageMaker), Model Deployment, ML Evaluation"),
    ("kv",   "AI.Tools", "Claude, Claude Code, Codex, Cursor, LLMs, Generative AI"),
    ("gap",),
    ("stats",),
]

def kv(key, value, value_id=None, dots_id=None):
    prefix = f". {key}: "
    ndots = max(1, VCOL - len(prefix))
    dots = "." * ndots
    lines = wrap_terms(value, WRAP) if value else [""]
    did = f' id="{dots_id}"' if dots_id else ""
    vid = f' id="{value_id}"' if value_id else ""
    out = [f'<tspan class="cc">. </tspan><tspan class="key">{esc(key)}</tspan>:'
           f'<tspan class="cc"{did}> {dots} </tspan>'
           f'<tspan class="value"{vid}>{esc(lines[0])}</tspan>']
    for cont in lines[1:]:
        out.append(f'<tspan class="cc">. </tspan>'
                   f'<tspan>{" "*(VCOL-1)}</tspan>'
                   f'<tspan class="value">{esc(cont)}</tspan>')
    return out

def build_right():
    phys = []
    for e in RIGHT:
        if e[0] == "hdr":
            phys.append(f'{esc(e[1])} -{"—"*37}-—-')
        elif e[0] == "head":
            phys.append(f'- {esc(e[1])} -{"—"*(43-len(e[1]))}-—-')
        elif e[0] == "gap":
            phys.append('<tspan class="cc">. </tspan>')
        elif e[0] == "stats":
            phys += build_stats()
        elif e[0] == "kv":
            phys += kv(e[1], e[2])
    return phys

# ---------------------------------------------------------------- GitHub stats
# Values are left-aligned at VCOL, same column as the kv rows above. The daily
# Action only swaps the id="..._data" / loc_add / loc_del text; it must not
# touch the "_dots" spans, or the alignment breaks.
def build_stats():
    def line(key, vid, val, did, tail=""):
        prefix = f". {key}: "
        dots = "." * max(1, VCOL - len(prefix))
        return (f'<tspan class="cc">. </tspan><tspan class="key">{esc(key)}</tspan>:'
                f'<tspan class="cc" id="{did}"> {dots} </tspan>'
                f'<tspan class="value" id="{vid}">{val}</tspan>{tail}')
    loc_tail = (' ( <tspan class="addColor" id="loc_add">42,300</tspan>'
                '<tspan class="addColor">++</tspan>, '
                '<tspan class="delColor" id="loc_del">19,838</tspan>'
                '<tspan class="delColor">--</tspan> )')
    return [f'- GitHub Stats -{"—"*(43-len("GitHub Stats"))}-—-',
            line("Commits", "commit_data", "134", "commit_data_dots"),
            line("LOC", "loc_data", "22,462", "loc_data_dots", loc_tail)]

# ---------------------------------------------------------------- assemble
def text_block(x, phys, y_start):
    out = [f'<text x="{x}" y="{y_start}" fill="__INFO__">']
    for i, inner in enumerate(phys):
        y = y_start + i*STEP
        if inner.startswith("<tspan"):
            inner = inner.replace("<tspan", f'<tspan x="{x}" y="{y}"', 1)
        else:
            inner = f'<tspan x="{x}" y="{y}">{inner}</tspan>'
        out.append(inner)
    out.append("</text>")
    return "\n".join(out), y_start + (len(phys)-1)*STEP

right_phys = build_right()
right_svg, right_bottom = text_block(X_INFO, right_phys, Y0)

ascii_dark_lines = load_ascii("ascii_portrait_dark.txt")
ascii_light_lines = load_ascii("ascii_portrait.txt")
_, ascii_bottom = ascii_block("__ASCII__", ascii_dark_lines)

H = max(right_bottom, ascii_bottom) + 24
W = 985

TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{W}px" height="{H}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {KEY};}}
.value {{fill: {VALUE};}}
.addColor {{fill: {ADD};}}
.delColor {{fill: {DEL};}}
.cc {{fill: {CC};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{W}px" height="{H}px" fill="{RECT}" rx="15"/>
{ASCII}
{RIGHT}
</svg>
"""

MODES = {
    "dark_mode.svg":  dict(RECT="#161b22", INFO="#c9d1d9", ASCII="#c9d1d9",
                           KEY="#d2a8ff", VALUE="#a5d6ff", ADD="#3fb950",
                           DEL="#f85149", CC="#616e7f"),
    "light_mode.svg": dict(RECT="#f6f8fa", INFO="#24292f", ASCII="#24292f",
                           KEY="#8250df", VALUE="#0a3069", ADD="#1a7f37",
                           DEL="#cf222e", CC="#c2cfde"),
}
ASCII_FOR = {"dark_mode.svg": ascii_dark_lines, "light_mode.svg": ascii_light_lines}
for fn, c in MODES.items():
    ascii_svg_t, _ = ascii_block("__ASCII__", ASCII_FOR[fn])
    svg = TEMPLATE.format(
        W=W, H=H,
        ASCII=ascii_svg_t.replace("__ASCII__", c["ASCII"]),
        RIGHT=right_svg.replace("__INFO__", c["INFO"]),
        RECT=c["RECT"], KEY=c["KEY"], VALUE=c["VALUE"], ADD=c["ADD"],
        DEL=c["DEL"], CC=c["CC"])
    (BASE / fn).write_text(svg)
    print(f"wrote {fn}: {W}x{H}  (right y{right_bottom} / ascii y{ascii_bottom})")
