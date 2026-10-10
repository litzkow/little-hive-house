"""Seasonal website decor for every season after fall (fall lives in decor.py): a seamless 320 x 74 garland tile,
a 380 x 330 painted scene for the hero and small 40 x 40 drifting particles. Same hand-painted gouache idiom as
the fall scarecrow: organic washes, brush strokes clipped inside shapes, variable inked outlines.

Everything is drawn on a transparent ground and has to read on the cream day page (#FFF6E5) and on the dark
brown night page (#1C1610): dark subjects (cat, bats, black pennants) get a lavender rim light, white subjects
(snow, snowmen, flakes) get a blue shade side and a blue-grey ink line.

Run:  python3 tools/decor_seasons.py            (writes assets/decor/<season>-*.svg and the particle files)
"""
import math
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from decor import INK, OUT, svg  # noqa: E402  (decor.py also puts tools/designs on sys.path)
from gouache import blob, ink, jitter, maple_leaf, oak, painted_pumpkin, smooth_closed, smooth_open, strokes, wash  # noqa: E402

GROUND = 316  # scene ground line
TW = 320      # garland tile width


# ---------------------------------------------------------------- compact output
# The painted look comes from hundreds of tiny brush-stroke paths and from washes / inked edges that repeat the same
# outline two or three times. compact() keeps the picture identical but writes it smaller: brush strokes become short
# relative paths grouped by colour, and any long outline used more than once is defined once and reused with <use>.
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_STROKE = re.compile(r'<path d="M (-?[\d.]+) (-?[\d.]+) Q (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) Q (-?[\d.]+) (-?[\d.]+) \1 \2 Z" '
                     r'fill="(#[0-9A-Fa-f]{6})" opacity="([\d.]+)"/>')


def _n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return "0" if s in ("", "-0", "-") else s


def _pair(a, b):
    sb = _n(b)
    return _n(a) + ("" if sb.startswith("-") else " ") + sb


def _stroke_runs(m_list):
    by = {}
    for g in m_list:
        x, y, q1x, q1y, ex, ey, q2x, q2y = (float(v) for v in g[:8])
        d = (f"M{_pair(x, y)}q{_pair(q1x - x, q1y - y)} {_pair(ex - x, ey - y)}"
             f"q{_pair(q2x - ex, q2y - ey)} {_pair(x - ex, y - ey)}z")
        op = _n(round(float(g[9]), 1))
        by.setdefault(g[8], []).append(f'<path d="{d}" opacity="{op}"/>')
    return "".join(f'<g fill="{c}">{"".join(v)}</g>' for c, v in by.items())


def compact(body):
    # 1. brush strokes: each run of consecutive stroke paths becomes colour groups of short relative paths
    out, pos = [], 0
    run = []
    run_start = None
    for m in _STROKE.finditer(body):
        if run and m.start() != run_end:
            out.append(body[pos:run_start] + _stroke_runs(run))
            pos, run = run_end, []
        if not run:
            run_start = m.start()
        run.append(m.groups())
        run_end = m.end()
    if run:
        out.append(body[pos:run_start] + _stroke_runs(run))
        pos = run_end
    out.append(body[pos:])
    body = "".join(out)
    # 2. long outlines used more than once -> <defs> + <use>
    counts = {}
    for d in re.findall(r'<path d="([^"]{120,})"', body):
        counts[d] = counts.get(d, 0) + 1
    defs = []
    for i, (d, k) in enumerate(sorted(((d, k) for d, k in counts.items() if k > 1), key=lambda t: -len(t[0]))):
        pid = f"o{i}"
        defs.append(f'<path id="{pid}" d="{d}"/>')
        body = body.replace(f'<path d="{d}"', f'<use href="#{pid}"')
    # 3. trim number noise in what is left
    body = (f"<defs>{''.join(defs)}</defs>" if defs else "") + body
    body = re.sub(r' d="([^"]*)"', lambda m: f' d="{_mind(m.group(1))}"', body)
    body = re.sub(r'(transform|stroke-width)="([^"]*)"', lambda m: f'{m.group(1)}="{_NUM.sub(lambda q: _n(float(q.group(0))), m.group(2))}"', body)
    return re.sub(r"(?<=\d)\.0(?=[^\d])", "", body)


def _mind(d):
    """Shortest equivalent spelling of SVG path data (1-decimal numbers, no redundant spaces)."""
    d = _NUM.sub(lambda m: _n(float(m.group(0))), d)
    d = re.sub(r"\s*([A-Za-z])\s*", r"\1", d)
    d = re.sub(r"\s+(?=-)", "", d)
    d = re.sub(r"(\.\d+)\s+(?=\.)", r"\1", d)
    return d.strip()


def save(name, w, h, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text(svg(w, h, compact(body)), encoding="utf-8")


# ---------------------------------------------------------------- colour + small utilities
def F(v):
    return f"{v:.1f}"


def _hx(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    A, B = _hx(a), _hx(b)
    return "#" + "".join(f"{round(A[i] + (B[i] - A[i]) * t):02X}" for i in range(3))


def lt(c, t=0.3):
    return mix(c, "#FFFFFF", t)


def dk(c, t=0.3):
    return mix(c, "#000000", t)


def inkc(c):
    """A warm dark line colour related to the fill (pen under paint, never pure black)."""
    return mix(dk(c, 0.5), INK, 0.35)


def bbox(pts, pad=3):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def poly(pts):
    return "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in pts) + " Z"


def rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def paint(uid, d, box, base, seed, tints=None, angle=-90, n=None, ink_col=None, ink_w=1.5, length=None, width=None,
          op=(0.25, 0.55), curve=0.25, edge_op=0.6, layers=2):
    """Wash + clipped brush strokes + inked edge: the basic gouache object."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    m = min(w, h)
    tints = tints or [lt(base, 0.22), dk(base, 0.18), lt(base, 0.4)]
    n = int(max(8, min(110, w * h / 55))) if n is None else n
    length = length or (max(3, m * 0.15), max(6, m * 0.5))
    width = width or (0.5, max(1.0, m * 0.035))
    o = wash(d, base, seed, layers, 0.8, 0.5)
    if n:
        o += strokes(uid, d, box, tints, seed + 1, n=n, angle=angle, length=length, width=width, opacity=op, curve=curve)
    if ink_w:
        o += ink(d, ink_col or inkc(base), ink_w, seed + 2, 2, edge_op)
    return o


def paint_pts(uid, pts, base, seed, **kw):
    return paint(uid, smooth_closed(pts), bbox(pts), base, seed, **kw)


def rim(uid, d, col, sx, sy, k=2.0, op=0.75):
    """Light (or shade) band hugging the inside of a shape on the (sx, sy) side."""
    return (f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2 * k:.1f}" opacity="{op}" '
            f'transform="translate({F(-sx * k)} {F(-sy * k)})"/></g>')


def shade(uid, d, col, sx, sy, k=6.0, op=0.35):
    """Soft shade side: the shape filled, shifted away, clipped to itself (crescent on the (sx, sy) side)."""
    return (f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2 * k:.1f}" opacity="{op}" '
            f'transform="translate({F(-sx * k)} {F(-sy * k)})"/></g>')


def glow(uid, cx, cy, rx, ry, col, op):
    return (f'<defs><radialGradient id="{uid}"><stop offset="0" stop-color="{col}" stop-opacity="{op}"/>'
            f'<stop offset="0.5" stop-color="{col}" stop-opacity="{op * 0.45:.2f}"/>'
            f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{uid})"/>')


def shadow(cx, cy, rx, ry, op=0.14):
    return f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="{INK}" opacity="{op}"/>'


def heart_d(cx, cy, s, rot_=0):
    pts = [(0, 0.85), (-0.2, 0.6), (-1.0, 0.15), (-0.95, -0.35), (-0.9, -0.85), (-0.25, -0.95), (0, -0.45),
           (0.25, -0.95), (0.9, -0.85), (0.95, -0.35), (1.0, 0.15), (0.2, 0.6), (0, 0.85)]
    p = [rot(cx + x * s, cy + y * s, cx, cy, rot_) for x, y in pts]
    d = f"M {F(p[0][0])} {F(p[0][1])}"
    for i in range(1, 13, 3):
        d += f" C {F(p[i][0])} {F(p[i][1])} {F(p[i + 1][0])} {F(p[i + 1][1])} {F(p[i + 2][0])} {F(p[i + 2][1])}"
    return d + " Z"


def painted_heart(uid, cx, cy, s, col, seed, rot_=0, ink_w=None, shine=True, stitch=None):
    d = heart_d(cx, cy, s, rot_)
    box = (cx - 1.1 * s, cy - 1.1 * s, cx + 1.1 * s, cy + 1.0 * s)
    o = [paint(uid, d, box, col, seed, angle=-60, n=int(max(8, s * 2.2)), ink_w=ink_w if ink_w is not None else max(0.9, s * 0.07),
               length=(s * 0.3, s * 0.9), width=(s * 0.03, s * 0.08), op=(0.2, 0.5))]
    o.append(shade(uid + "-sh", d, dk(col, 0.35), 0.7, 0.8, k=s * 0.16, op=0.35))
    if stitch:
        d2 = heart_d(cx, cy + 0.02 * s, s * 0.74, rot_)
        o.append(f'<path d="{d2}" fill="none" stroke="{stitch}" stroke-width="{max(0.7, s * 0.06):.1f}" stroke-dasharray="{s * 0.16:.1f} {s * 0.12:.1f}" stroke-linecap="round" opacity="0.85"/>')
    if shine:
        a = rot(cx - 0.55 * s, cy - 0.5 * s, cx, cy, rot_)
        b = rot(cx - 0.72 * s, cy - 0.1 * s, cx, cy, rot_)
        c = rot(cx - 0.8 * s, cy - 0.55 * s, cx, cy, rot_)
        o.append(f'<path d="M {F(a[0])} {F(a[1])} Q {F(c[0])} {F(c[1])} {F(b[0])} {F(b[1])}" stroke="#FFFFFF" stroke-width="{max(1, s * 0.12):.1f}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    return "".join(o)


def star_pts(cx, cy, r, inner=0.48, rot_=-90, n=5):
    out = []
    for i in range(2 * n):
        a = math.radians(rot_ + i * 180 / n)
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def swag_y(x, top=10, sag=34):
    """The garland's hanging curve (same shape as the fall garland); seamless at x = 0 / 320."""
    t = x / TW
    return (1 - t) ** 3 * top + 3 * (1 - t) ** 2 * t * sag + 3 * (1 - t) * t * t * sag + t ** 3 * top


def swag_slope(x, **kw):
    return math.degrees(math.atan2(swag_y(x + 0.5, **kw) - swag_y(x - 0.5, **kw), 1))


def twine(col="#8A6A42", hi="#C9A878", w=2.2, top=10, sag=34):
    d = f"M -2 {F(swag_y(0, top, sag))} C 80 {sag} 240 {sag} 322 {F(swag_y(TW, top, sag))}"
    d = f"M 0 {top} C 80 {sag} 240 {sag} 320 {top}"
    return (f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none"/>'
            f'<path d="{d}" stroke="{hi}" stroke-width="{w * 0.36:.1f}" fill="none" stroke-dasharray="3 3"/>')


def wrap(fn, x, margin):
    """Draw an item at x and, if it crosses a tile edge, again one tile over so the seam matches."""
    out = fn(x)
    if x < margin:
        out += fn(x + TW)
    if x > TW - margin:
        out += fn(x - TW)
    return out


# ================================================================ HALLOWEEN
CAT = "#2B2236"
CAT_RIM = "#A898D0"
BAT = "#2E2440"


def bat(uid, cx, cy, s, rot_=0, flap=0.0, body=BAT, rimc=CAT_RIM, eyes=True, seed=1):
    """Painted bat, wings spread; s = half wingspan."""
    def P(x, y):
        return F(x * s), F(y * s)
    def wing(sg):
        q = lambda x, y: f"{F(sg * x * s)} {F(y * s)}"  # noqa: E731
        return (f"M {q(0.1, -0.1)} Q {q(0.45, -0.58 - flap)} {q(1.0, -0.4 - flap * 0.5)} Q {q(0.9, -0.14)} {q(0.8, 0.06)} "
                f"Q {q(0.68, -0.06)} {q(0.55, 0.12)} Q {q(0.42, 0.0)} {q(0.12, 0.16)} Z")
    wings = wing(1) + " " + wing(-1)
    bodyd = blob(0, 0.04 * s, 0.17 * s, 0.25 * s, seed, 0.05, 14)
    head = blob(0, -0.2 * s, 0.15 * s, 0.13 * s, seed + 1, 0.04, 12)
    ears = f"M {P(-0.13, -0.22)[0]} {P(-0.13, -0.22)[1]} L {P(-0.15, -0.46)[0]} {P(-0.15, -0.46)[1]} L {P(-0.02, -0.3)[0]} {P(-0.02, -0.3)[1]} Z " \
           f"M {P(0.13, -0.22)[0]} {P(0.13, -0.22)[1]} L {P(0.15, -0.46)[0]} {P(0.15, -0.46)[1]} L {P(0.02, -0.3)[0]} {P(0.02, -0.3)[1]} Z"
    sw = max(0.6, s * 0.03)
    o = [f'<g transform="translate({F(cx)} {F(cy)}) rotate({rot_})">']
    o.append(f'<path d="{wings}" fill="{body}"/>')
    if s > 12:
        o.append(strokes(uid + "-w", wings, (-s, -0.7 * s, s, 0.2 * s), [lt(body, 0.15), dk(body, 0.3), lt(body, 0.28)], seed,
                         n=int(s * 1.4), angle=-20, length=(s * 0.15, s * 0.4), width=(0.4, s * 0.025), opacity=(0.3, 0.6)))
    bones = "".join(f'<path d="M {F(sg * 0.13 * s)} {F(-0.06 * s)} L {F(sg * x * s)} {F(y * s)}"/>'
                    for sg in (1, -1) for x, y in ((1.0, -0.4 - flap * 0.5), (0.8, 0.06), (0.55, 0.12)))
    o.append(f'<g stroke="{lt(body, 0.3)}" stroke-width="{sw:.2f}" opacity="0.7" fill="none" stroke-linecap="round">{bones}</g>')
    o.append(rim(uid + "-r", wings, rimc, 0, -1, k=max(0.7, s * 0.05), op=0.85))
    o.append(f'<path d="{ears}" fill="{body}"/><path d="{bodyd}" fill="{body}"/><path d="{head}" fill="{body}"/>')
    o.append(f'<path d="{bodyd}" fill="none" stroke="{lt(body, 0.22)}" stroke-width="{sw:.2f}" opacity="0.6"/>')
    o.append(rim(uid + "-rh", head + " " + ears, rimc, 0, -1, k=max(0.6, s * 0.04), op=0.8))
    o.append(f'<ellipse cx="0" cy="{F(0.06 * s)}" rx="{F(0.09 * s)}" ry="{F(0.15 * s)}" fill="{lt(body, 0.18)}" opacity="0.8"/>')
    if eyes:
        o.append(f'<circle cx="{F(-0.055 * s)}" cy="{F(-0.2 * s)}" r="{F(max(0.8, 0.035 * s))}" fill="#FFD25E"/>'
                 f'<circle cx="{F(0.055 * s)}" cy="{F(-0.2 * s)}" r="{F(max(0.8, 0.035 * s))}" fill="#FFD25E"/>')
    o.append(ink(wings, mix(body, "#000000", 0.5), max(0.6, s * 0.035), seed + 3, 1, 0.7))
    o.append("</g>")
    return "".join(o)


def jack_face(uid, cx, cy, w, h, kind, skin):
    g = f"{uid}-fg"
    o = [f'<defs><radialGradient id="{g}" cx="{F(cx)}" cy="{F(cy + 0.1 * h)}" r="{F(0.42 * w)}" gradientUnits="userSpaceOnUse">'
         '<stop offset="0" stop-color="#FFF8C8"/><stop offset="0.45" stop-color="#FFD24A"/><stop offset="1" stop-color="#F5921E"/></radialGradient></defs>']
    o.append(glow(f"{uid}-sk", cx, cy + 0.08 * h, 0.5 * w, 0.44 * h, "#FFE07A", 0.55))
    holes, teeth = [], []
    if kind == "classic":
        for sg in (-1, 1):
            holes.append(poly(jitter([(cx + sg * 0.3 * w, cy + 0.0 * h), (cx + sg * 0.19 * w, cy - 0.28 * h), (cx + sg * 0.07 * w, cy - 0.01 * h)], 3, 0.6)))
        holes.append(poly([(cx - 0.045 * w, cy + 0.08 * h), (cx, cy - 0.04 * h), (cx + 0.045 * w, cy + 0.08 * h)]))
        holes.append(f"M {F(cx - 0.34 * w)} {F(cy + 0.1 * h)} Q {F(cx)} {F(cy + 0.32 * h)} {F(cx + 0.34 * w)} {F(cy + 0.1 * h)} "
                     f"Q {F(cx)} {F(cy + 0.6 * h)} {F(cx - 0.34 * w)} {F(cy + 0.1 * h)} Z")
        teeth = [(cx - 0.12 * w, cy + 0.18 * h, 0.075 * w, 0.1 * h), (cx + 0.11 * w, cy + 0.24 * h, 0.075 * w, 0.1 * h)]
    elif kind == "happy":
        for sg in (-1, 1):
            ex, ey = cx + sg * 0.19 * w, cy - 0.08 * h
            holes.append(f"M {F(ex - 0.1 * w)} {F(ey + 0.05 * h)} Q {F(ex)} {F(ey - 0.24 * h)} {F(ex + 0.1 * w)} {F(ey + 0.05 * h)} "
                         f"Q {F(ex)} {F(ey - 0.07 * h)} {F(ex - 0.1 * w)} {F(ey + 0.05 * h)} Z")
        holes.append(f"M {F(cx - 0.26 * w)} {F(cy + 0.12 * h)} Q {F(cx)} {F(cy + 0.3 * h)} {F(cx + 0.26 * w)} {F(cy + 0.12 * h)} "
                     f"Q {F(cx)} {F(cy + 0.5 * h)} {F(cx - 0.26 * w)} {F(cy + 0.12 * h)} Z")
        teeth = [(cx, cy + 0.22 * h, 0.08 * w, 0.08 * h)]
    else:  # sly
        for sg in (-1, 1):
            holes.append(poly([(cx + sg * 0.3 * w, cy - 0.2 * h), (cx + sg * 0.06 * w, cy - 0.06 * h), (cx + sg * 0.21 * w, cy + 0.04 * h)]))
        z = [(-0.3, 0.12), (0, 0.2), (0.3, 0.12), (0.22, 0.34), (0.11, 0.26), (0, 0.4), (-0.11, 0.26), (-0.22, 0.34)]
        holes.append(poly([(cx + x * w, cy + y * h) for x, y in z]))
    for hd in holes:
        o.append(f'<path d="{hd}" fill="#7A2E0E" stroke="#7A2E0E" stroke-width="1.2" stroke-linejoin="round"/>')
        o.append(f'<path d="{hd}" fill="url(#{g})" transform="translate(0.5 1.3)"/>')
    for tx, ty, tw, th in teeth:
        o.append(f'<path d="{blob(tx, ty, tw / 2, th / 2, 7, 0.05, 10)}" fill="{skin}"/>')
    return "".join(o)


def witch_hat(uid, cx, base, s, rot_=0, seed=3):
    hat, band = "#3B2D52", "#E8792E"
    brim = blob(cx, base, 0.66 * s, 0.13 * s, seed, 0.04, 20)
    cone_pts = [(cx - 0.31 * s, base), (cx - 0.22 * s, base - 0.38 * s), (cx - 0.08 * s, base - 0.76 * s), (cx + 0.1 * s, base - 0.98 * s),
                (cx + 0.36 * s, base - 1.02 * s), (cx + 0.15 * s, base - 0.86 * s), (cx + 0.11 * s, base - 0.56 * s), (cx + 0.31 * s, base)]
    cone = smooth_closed(cone_pts)
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(base)})">']
    o.append(paint(uid + "-b", brim, (cx - 0.7 * s, base - 0.16 * s, cx + 0.7 * s, base + 0.16 * s), hat, seed,
                   tints=["#54427A", "#221934", "#6E5A96"], angle=0, n=26, ink_col="#1A1228"))
    o.append(rim(uid + "-br", brim, CAT_RIM, 0, -1, k=1.2, op=0.7))
    o.append(paint(uid + "-c", cone, bbox(cone_pts), hat, seed + 4, tints=["#54427A", "#221934", "#6E5A96"], angle=-80, n=40, ink_col="#1A1228"))
    o.append(rim(uid + "-cr", cone, CAT_RIM, -1, -0.3, k=1.5, op=0.75))
    bd = f"M {F(cx - 0.33 * s)} {F(base - 0.03 * s)} L {F(cx - 0.29 * s)} {F(base - 0.2 * s)} Q {F(cx)} {F(base - 0.14 * s)} {F(cx + 0.27 * s)} {F(base - 0.2 * s)} L {F(cx + 0.33 * s)} {F(base - 0.03 * s)} Q {F(cx)} {F(base + 0.04 * s)} {F(cx - 0.33 * s)} {F(base - 0.03 * s)} Z"
    o.append(paint(uid + "-bd", bd, (cx - 0.35 * s, base - 0.22 * s, cx + 0.35 * s, base + 0.05 * s), band, seed + 7,
                   tints=["#F6A35A", "#B9531E"], angle=0, n=14, ink_w=1.0))
    o.append(f'<rect x="{F(cx - 0.07 * s)}" y="{F(base - 0.19 * s)}" width="{F(0.14 * s)}" height="{F(0.14 * s)}" rx="1.5" fill="none" stroke="#F6CC52" stroke-width="{F(max(1.4, 0.035 * s))}"/>')
    o.append("</g>")
    return "".join(o)


def cat(uid, cx, base, s, seed=11):
    """Black cat sitting, facing us, tail curled round the front paws. s = scale (1 = ~100 px tall)."""
    def p(x, y):
        return (cx + x * s, base + y * s)
    body_pts = [p(-27, 0), p(-31, -22), p(-24, -46), p(-13, -60), p(0, -63), p(13, -60), p(23, -46), p(30, -22), p(27, 0)]
    body = smooth_closed(body_pts)
    ears = poly([p(-19, -78), p(-21, -100), p(-5, -88)]) + " " + poly([p(5, -88), p(20, -101), p(19, -78)])
    head = blob(cx, base - 74 * s, 21 * s, 17.5 * s, seed, 0.04, 16)
    tail = smooth_open([p(24, -6), p(40, -12), p(44, -28), p(36, -40)])
    o = [shadow(cx + 6 * s, base, 40 * s, 6 * s, 0.16)]
    o.append(f'<path d="{tail}" stroke="{CAT}" stroke-width="{F(8 * s)}" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{tail}" stroke="{CAT_RIM}" stroke-width="{F(1.8 * s)}" fill="none" stroke-linecap="round" opacity="0.7" transform="translate({F(1.5 * s)} {F(-2 * s)})"/>')
    tints = ["#3E3350", "#1A1420", "#4E4264"]
    o.append(paint(uid + "-b", body, bbox(body_pts), CAT, seed, tints=tints, angle=-95, n=50, ink_col="#120C18", length=(5 * s, 16 * s), width=(0.6, 1.6 * s)))
    o.append(rim(uid + "-br", body, CAT_RIM, -1, -0.4, k=1.6 * s, op=0.75))
    o.append(f'<path d="M {F(p(-8, -36)[0])} {F(p(-8, -36)[1])} Q {F(p(-10, -14)[0])} {F(p(-10, -14)[1])} {F(p(-8, -2)[0])} {F(p(-8, -2)[1])} '
             f'M {F(p(8, -36)[0])} {F(p(8, -36)[1])} Q {F(p(10, -14)[0])} {F(p(10, -14)[1])} {F(p(8, -2)[0])} {F(p(8, -2)[1])}" stroke="#4E4264" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    for sg in (-1, 1):
        o.append(f'<path d="{blob(*p(sg * 14, -2), 8 * s, 4 * s, seed + sg, 0.05, 10)}" fill="#3A3048"/>')
    # tail tip wrapping over the paws
    tip = smooth_open([p(30, -2), p(14, 4), p(-6, 2), p(-16, -4)])
    o.append(f'<path d="{tip}" stroke="{CAT}" stroke-width="{F(7 * s)}" fill="none" stroke-linecap="round"/>'
             f'<path d="{tip}" stroke="{CAT_RIM}" stroke-width="{F(1.4 * s)}" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(0 {F(-2.4 * s)})"/>')
    o.append(f'<path d="{ears}" fill="{CAT}" stroke="#120C18" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(f'<path d="{poly([p(-17, -82), p(-19, -95), p(-9, -87)])}" fill="#C77A92" opacity="0.7"/><path d="{poly([p(9, -87), p(18, -96), p(17, -82)])}" fill="#C77A92" opacity="0.7"/>')
    o.append(paint(uid + "-h", head, (cx - 22 * s, base - 92 * s, cx + 22 * s, base - 56 * s), CAT, seed + 5, tints=tints, angle=-90, n=26, ink_col="#120C18",
                   length=(3 * s, 9 * s), width=(0.5, 1.2 * s)))
    o.append(rim(uid + "-hr", head + " " + ears, CAT_RIM, -1, -0.6, k=1.4 * s, op=0.8))
    # collar + bell
    o.append(f'<path d="M {F(p(-15, -61)[0])} {F(p(-15, -61)[1])} Q {F(cx)} {F(base - 54 * s)} {F(p(15, -61)[0])} {F(p(15, -61)[1])}" stroke="#7A4E9E" stroke-width="{F(4 * s)}" fill="none" stroke-linecap="round"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(base - 54 * s)}" r="{F(3.6 * s)}" fill="#F2C14E" stroke="#8A6212" stroke-width="0.8"/><circle cx="{F(cx - 1 * s)}" cy="{F(base - 55.2 * s)}" r="{F(1 * s)}" fill="#FFF3C0"/>')
    # face
    for sg in (-1, 1):
        ex, ey = p(sg * 8.5, -75)
        o.append(f'<ellipse cx="{F(ex)}" cy="{F(ey)}" rx="{F(5.2 * s)}" ry="{F(4.2 * s)}" fill="#D8EC6A" transform="rotate({sg * -8} {F(ex)} {F(ey)})"/>')
        o.append(f'<ellipse cx="{F(ex)}" cy="{F(ey)}" rx="{F(1.3 * s)}" ry="{F(3.6 * s)}" fill="#14101A"/><circle cx="{F(ex - 1.6 * s)}" cy="{F(ey - 1.6 * s)}" r="{F(1 * s)}" fill="#FFFFFF"/>')
    nx, ny = p(0, -67)
    o.append(f'<path d="M {F(nx - 2.4 * s)} {F(ny)} L {F(nx + 2.4 * s)} {F(ny)} L {F(nx)} {F(ny + 2.4 * s)} Z" fill="#E59AB0"/>')
    o.append(f'<path d="M {F(nx)} {F(ny + 2.4 * s)} q {F(-2 * s)} {F(2.6 * s)} {F(-4 * s)} {F(0.6 * s)} M {F(nx)} {F(ny + 2.4 * s)} q {F(2 * s)} {F(2.6 * s)} {F(4 * s)} {F(0.6 * s)}" stroke="#B9A6E0" stroke-width="{F(0.9 * s)}" fill="none" stroke-linecap="round"/>')
    wh = "".join(f'<path d="M {F(nx + sg * 6 * s)} {F(ny + dy * s)} l {F(sg * 14 * s)} {F(dl * s)}"/>' for sg in (-1, 1) for dy, dl in ((0, -2), (2.4, 1.5)))
    o.append(f'<g stroke="#D9CCF2" stroke-width="{F(0.7 * s)}" opacity="0.75" stroke-linecap="round">{wh}</g>')
    return "".join(o)


def broom(uid, bx, by, ang, handle, brist, seed=21):
    """Witch's broom: binding point (bx, by), ang = direction from binding toward the bristle tips (deg)."""
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -uy, ux
    def at(a, b):
        return (bx + ux * a + nx * b, by + uy * a + ny * b)
    top = at(-handle, 0)
    hpts = [top, at(-handle * 0.66, 1.2), at(-handle * 0.33, -1), at(4, 0)]
    hd = smooth_open(hpts)
    o = [f'<path d="{hd}" stroke="#4A2E18" stroke-width="7.4" fill="none" stroke-linecap="round"/>',
         f'<path d="{hd}" stroke="#9A6A3E" stroke-width="5" fill="none" stroke-linecap="round"/>',
         f'<path d="{hd}" stroke="#D4A26A" stroke-width="1.4" fill="none" stroke-linecap="round" opacity="0.8" transform="translate({F(-nx * 1.3)} {F(-ny * 1.3)})"/>']
    tx, ty = top
    o.append(f'<path d="M {F(tx)} {F(ty)} l {F(-ux * 6 + nx * 5)} {F(-uy * 6 + ny * 5)}" stroke="#7A5232" stroke-width="2.4" stroke-linecap="round"/>')
    bp = [at(0, 6), at(10, 10), at(brist * 0.6, 18), at(brist, 24), at(brist + 4, 12), at(brist + 2, 0), at(brist + 4, -12), at(brist, -24), at(brist * 0.6, -18), at(10, -10), at(0, -6)]
    d = smooth_closed(bp)
    o.append(paint(uid, d, bbox(bp), "#D9A84E", seed, tints=["#F2D07A", "#A8742A", "#C9933A", "#FFF0B8"], angle=ang, n=60,
                   length=(10, 26), width=(0.5, 1.4), op=(0.45, 0.9), ink_col="#7A4E22", ink_w=1.3))
    rnd = random.Random(seed)
    tufts = "".join(f'<path d="M {F(at(brist - 2, b)[0])} {F(at(brist - 2, b)[1])} l {F(ux * rnd.uniform(4, 9) + nx * rnd.uniform(-2, 2))} {F(uy * rnd.uniform(4, 9) + ny * rnd.uniform(-2, 2))}"/>'
                    for b in [rnd.uniform(-22, 22) for _ in range(16)])
    o.append(f'<g stroke="#C9933A" stroke-width="1.2" stroke-linecap="round">{tufts}</g>')
    for a in (3, 11):
        p0, p1 = at(a, -11 + a * 0.1), at(a, 11 - a * 0.1)
        o.append(f'<path d="M {F(p0[0])} {F(p0[1])} L {F(p1[0])} {F(p1[1])}" stroke="#6A3E8A" stroke-width="3.2" stroke-linecap="round"/>')
    return "".join(o)


def spider_thread(x, y0, y1, s=1.0):
    legs = "".join(f'<path d="M {F(x)} {F(y1)} q {F(sg * 5 * s)} {F(dy * s)} {F(sg * 8 * s)} {F((dy + 4) * s)}"/>' for sg in (-1, 1) for dy in (-4, -1, 2))
    return (f'<path d="M {F(x)} {F(y0)} L {F(x)} {F(y1 - 4 * s)}" stroke="#B9A6E0" stroke-width="0.8" opacity="0.9"/>'
            f'<g stroke="#2A2036" stroke-width="{F(1.2 * s)}" fill="none" stroke-linecap="round">{legs}</g>'
            f'<ellipse cx="{F(x)}" cy="{F(y1)}" rx="{F(4.2 * s)}" ry="{F(4.8 * s)}" fill="#2A2036"/>'
            f'<circle cx="{F(x)}" cy="{F(y1 - 5 * s)}" r="{F(2.8 * s)}" fill="#2A2036"/>'
            f'<path d="M {F(x - 3 * s)} {F(y1 - 2 * s)} a {F(4 * s)} {F(4 * s)} 0 0 1 {F(5 * s)} {F(-3 * s)}" stroke="{CAT_RIM}" stroke-width="0.9" fill="none" opacity="0.8"/>'
            f'<circle cx="{F(x - 1 * s)}" cy="{F(y1 - 5.4 * s)}" r="{F(0.8 * s)}" fill="#FFFFFF"/><circle cx="{F(x + 1 * s)}" cy="{F(y1 - 5.4 * s)}" r="{F(0.8 * s)}" fill="#FFFFFF"/>')


def candy_corn(cx, cy, s, rot_=0):
    d = f"M {F(cx - 0.5 * s)} {F(cy + 0.42 * s)} Q {F(cx - 0.4 * s)} {F(cy - 0.2 * s)} {F(cx)} {F(cy - 0.6 * s)} Q {F(cx + 0.4 * s)} {F(cy - 0.2 * s)} {F(cx + 0.5 * s)} {F(cy + 0.42 * s)} Q {F(cx)} {F(cy + 0.56 * s)} {F(cx - 0.5 * s)} {F(cy + 0.42 * s)} Z"
    return (f'<g transform="rotate({rot_} {F(cx)} {F(cy)})"><clipPath id="cc{int(cx)}{int(cy)}"><path d="{d}"/></clipPath>'
            f'<g clip-path="url(#cc{int(cx)}{int(cy)})"><rect x="{F(cx - s)}" y="{F(cy - s)}" width="{F(2 * s)}" height="{F(2 * s)}" fill="#F6E9D2"/>'
            f'<rect x="{F(cx - s)}" y="{F(cy - 0.22 * s)}" width="{F(2 * s)}" height="{F(1.2 * s)}" fill="#F2A23A"/>'
            f'<rect x="{F(cx - s)}" y="{F(cy + 0.18 * s)}" width="{F(2 * s)}" height="{F(s)}" fill="#E8692E"/></g>'
            f'<path d="{d}" fill="none" stroke="#8A3A12" stroke-width="0.9" opacity="0.7"/></g>')


def halloween_scene(u="hw"):
    o = [shadow(195, 318, 176, 11, 0.13)]
    o.append(glow(u + "-glow", 190, 222, 170, 140, "#FFB547", 0.38))
    o.append(bat(u + "-b1", 70, 62, 27, rot_=-12, flap=0.08, seed=1))
    o.append(bat(u + "-b2", 312, 46, 20, rot_=14, flap=-0.05, seed=2))
    o.append(bat(u + "-b3", 352, 128, 13, rot_=-6, seed=3))
    o.append(bat(u + "-b4", 26, 150, 11, rot_=10, flap=0.1, seed=4))
    o.append(broom(u + "-br", 318, 258, 58, 150, 58))
    # stacked jack-o'-lanterns, bottom up
    o.append(painted_pumpkin(u + "-p1", 190, 270, 152, 92, 61, body="#E2702A", dark="#B04A18", light="#F8A85A"))
    o.append(jack_face(u + "-f1", 190, 270, 152, 92, "classic", "#E2702A"))
    o.append(painted_pumpkin(u + "-p2", 186, 198, 112, 70, 62))
    o.append(jack_face(u + "-f2", 186, 200, 112, 70, "happy", "#E8792E"))
    o.append(painted_pumpkin(u + "-p3", 192, 144, 78, 52, 63, body="#EE8A34", dark="#BE5A1E", light="#FFB86A"))
    o.append(jack_face(u + "-f3", 192, 146, 78, 52, "sly", "#EE8A34"))
    o.append(witch_hat(u + "-hat", 190, 122, 78, rot_=-10))
    o.append(spider_thread(236, 116, 156, 0.9))
    o.append(cat(u + "-cat", 70, 316, 1.22))
    o.append(painted_pumpkin(u + "-p4", 292, 302, 50, 32, 64, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF", stem="#6B5A2E"))
    o.append(candy_corn(120, 318, 11, -20) + candy_corn(134, 320, 10, 25) + candy_corn(258, 318, 10, 10))
    o.append(maple_leaf(334, 316, 9, "#C9442E", "#8E2A1A", rot=-30, seed=5) + oak(150, 322, 7, "#D98A3A", "#9A5A1E", rot=70))
    return "".join(o)


def halloween_garland(u="hg"):
    o = [twine("#5A4466", "#A898D0", 2.2)]
    cols = [("#E8792E", ["#F6A35A", "#B9531E", "#FFC27A"], "#FFE2B8"), (BAT, ["#4A3D5E", "#1A1424", "#5E4E78"], CAT_RIM),
            ("#E8792E", ["#F6A35A", "#B9531E", "#FFC27A"], "#FFE2B8"), ("#7A4E9E", ["#9A70C0", "#5A3478", "#B48ED6"], "#E8D8FF")]
    xs = [40, 120, 200, 280]
    for k, x in enumerate(xs):
        base, tints, stitch = cols[k]
        w, h = 46, 40
        a, b = (x - w / 2, swag_y(x - w / 2) + 1), (x + w / 2, swag_y(x + w / 2) + 1)
        tip = (x + (k % 2 * 2 - 1) * 1.5, (a[1] + b[1]) / 2 + h)
        d = (f"M {F(a[0])} {F(a[1])} Q {F(x)} {F((a[1] + b[1]) / 2 + 3)} {F(b[0])} {F(b[1])} "
             f"Q {F((b[0] + tip[0]) / 2 + 2)} {F((b[1] + tip[1]) / 2)} {F(tip[0])} {F(tip[1])} "
             f"Q {F((a[0] + tip[0]) / 2 - 2)} {F((a[1] + tip[1]) / 2)} {F(a[0])} {F(a[1])} Z")
        o.append(paint(f"{u}-f{k}", d, (a[0] - 2, min(a[1], b[1]) - 2, b[0] + 2, tip[1] + 2), base, 70 + k, tints=tints, angle=-90, n=30,
                       length=(6, 18), width=(0.5, 1.6), ink_col=dk(base, 0.55), ink_w=1.4))
        if base == BAT:
            o.append(rim(f"{u}-fr{k}", d, CAT_RIM, -1, 0, k=1.4, op=0.8))
        # stitched hem + a tiny motif
        inner = [(a[0] + 6, a[1] + 4), (b[0] - 6, b[1] + 4), (tip[0], tip[1] - 9)]
        o.append(f'<path d="{poly(inner)}" fill="none" stroke="{stitch}" stroke-width="1" stroke-dasharray="2.4 2" opacity="0.8" stroke-linejoin="round"/>')
        cx_, cy_ = x, (a[1] + b[1]) / 2 + 13
        if k == 2:  # little ghost
            gd = (f"M {F(cx_ - 6)} {F(cy_ + 7)} L {F(cx_ - 6)} {F(cy_ - 1)} Q {F(cx_ - 6)} {F(cy_ - 9)} {F(cx_)} {F(cy_ - 9)} Q {F(cx_ + 6)} {F(cy_ - 9)} {F(cx_ + 6)} {F(cy_ - 1)} "
                  f"L {F(cx_ + 6)} {F(cy_ + 7)} L {F(cx_ + 3)} {F(cy_ + 4.5)} L {F(cx_)} {F(cy_ + 7)} L {F(cx_ - 3)} {F(cy_ + 4.5)} Z")
            o.append(f'<path d="{gd}" fill="#FFF8EC" stroke="#8A4A1E" stroke-width="0.8" stroke-linejoin="round"/>'
                     f'<circle cx="{F(cx_ - 2.2)}" cy="{F(cy_ - 2.5)}" r="1.1" fill="#3A1A0A"/><circle cx="{F(cx_ + 2.2)}" cy="{F(cy_ - 2.5)}" r="1.1" fill="#3A1A0A"/>'
                     f'<ellipse cx="{F(cx_)}" cy="{F(cy_ + 1)}" rx="1" ry="1.4" fill="#3A1A0A"/>')
        elif base == "#E8792E":
            o.append(f'<path d="M {F(cx_ - 5)} {F(cy_ - 3)} l 2.5 -4 l 2.5 4 Z M {F(cx_ + 5)} {F(cy_ - 3)} l -2.5 -4 l -2.5 4 Z M {F(cx_ - 6)} {F(cy_ + 1)} Q {F(cx_)} {F(cy_ + 7)} {F(cx_ + 6)} {F(cy_ + 1)} Q {F(cx_)} {F(cy_ + 4)} {F(cx_ - 6)} {F(cy_ + 1)} Z" fill="#3A1A0A" opacity="0.85"/>')
        elif base == BAT:
            o.append(f'<path d="M {F(cx_ + 2)} {F(cy_ - 7)} A 6 6 0 1 0 {F(cx_ + 3)} {F(cy_ + 5)} A 4.6 4.6 0 1 1 {F(cx_ + 2)} {F(cy_ - 7)} Z" fill="#F6D88A"/>')
        else:
            o.append(f'<path d="{poly(star_pts(cx_, cy_, 6, 0.45))}" fill="#F6CC52" stroke="#B88A1E" stroke-width="0.6"/>')
        o.append(f'<circle cx="{F(a[0] + 1)}" cy="{F(a[1] - 0.5)}" r="1.6" fill="{dk(base, 0.4)}"/><circle cx="{F(b[0] - 1)}" cy="{F(b[1] - 0.5)}" r="1.6" fill="{dk(base, 0.4)}"/>')
    o.append(bat(u + "-b1", 80, 52, 12, rot_=-10, flap=0.1, seed=5))
    o.append(bat(u + "-b2", 240, 54, 11, rot_=12, flap=-0.05, seed=6))
    o.append(bat(u + "-b3", 160, 66, 7, rot_=4, seed=7, eyes=False))
    return "".join(o)


def particles_halloween():
    save("halloween-bat", 40, 40, bat("pb", 20, 22, 17, rot_=-8, flap=0.06, seed=9))


# ================================================================ CHRISTMAS
def glass_bulb(uid, cx, cy, r, col, seed, cap="#D9C27A", hook_len=0):
    d = blob(cx, cy, r, r * 1.02, seed, 0.03, 14)
    o = []
    if hook_len:
        o.append(f'<path d="M {F(cx)} {F(cy - r - 2)} l 0 {F(-hook_len)}" stroke="#8A7A5A" stroke-width="0.9"/>')
    o.append(f'<path d="{d}" fill="{col}"/>')
    o.append(shade(uid, d, dk(col, 0.45), 0.6, 0.8, k=r * 0.28, op=0.55))
    o.append(f'<ellipse cx="{F(cx - 0.35 * r)}" cy="{F(cy - 0.35 * r)}" rx="{F(0.22 * r)}" ry="{F(0.3 * r)}" fill="#FFFFFF" opacity="0.75" transform="rotate(30 {F(cx - 0.35 * r)} {F(cy - 0.35 * r)})"/>')
    o.append(f'<path d="M {F(cx + 0.55 * r)} {F(cy + 0.2 * r)} q {F(-0.1 * r)} {F(0.4 * r)} {F(-0.5 * r)} {F(0.6 * r)}" stroke="{lt(col, 0.5)}" stroke-width="{F(max(0.6, r * 0.1))}" fill="none" opacity="0.6" stroke-linecap="round"/>')
    o.append(ink(d, inkc(col), max(0.8, r * 0.1), seed, 1, 0.6))
    o.append(f'<rect x="{F(cx - 0.32 * r)}" y="{F(cy - r - 0.3 * r)}" width="{F(0.64 * r)}" height="{F(0.42 * r)}" rx="1" fill="{cap}" stroke="{dk(cap, 0.4)}" stroke-width="0.6"/>')
    return "".join(o)


def fir_tier(cx, apex, bot, hw, seed, n_sc=4, droop=4):
    rnd = random.Random(seed)
    pts = [(cx, apex), (cx + hw * 0.3, apex + (bot - apex) * 0.38), (cx + hw * 0.72, bot - 8), (cx + hw, bot + droop)]
    for i in range(1, n_sc):
        x = cx + hw - 2 * hw * i / n_sc
        pts.append((x + rnd.uniform(-3, 3), bot - 2 + rnd.uniform(-1, 2)))
        pts.append((x - hw / n_sc + rnd.uniform(-2, 2), bot + 5 + rnd.uniform(-1, 3)))
    pts = pts[:3 + 2 * (n_sc - 1) + 1]
    pts += [(cx - hw, bot + droop), (cx - hw * 0.72, bot - 8), (cx - hw * 0.3, apex + (bot - apex) * 0.38)]
    return pts


def fir(uid, cx, top, base, hw, tiers, seed, cols=("#2F6B4F", "#4C8C62", "#1E4A38", "#6FA474"), snow=False, inkcol="#163626"):
    """Painted fir built from overlapping drooping tiers (top tier drawn last)."""
    base_c, light, darkc, hi = cols
    o = []
    H = base - top
    specs = []
    for i in range(tiers):
        t0 = i / tiers
        apex = top + H * max(0, t0 * 0.92 - 0.04)
        bot = top + H * (0.28 + 0.72 * (i + 1) / tiers) if i < tiers - 1 else base
        bot = top + H * ((i + 1) / tiers) * 0.98 + 4
        hw_i = hw * (0.38 + 0.62 * (i + 1) / tiers)
        specs.append((apex, bot, hw_i))
    for i in reversed(range(tiers)):
        apex, bot, hw_i = specs[i]
        pts = fir_tier(cx, apex, bot, hw_i, seed + i, n_sc=3 + i // 2)
        d = smooth_closed(pts)
        box = bbox(pts)
        o.append(wash(d, base_c, seed + i, 2, 0.8, 0.5))
        o.append(strokes(f"{uid}-l{i}", d, (box[0], box[1], cx, box[3]), [light, darkc, hi, base_c], seed + 10 + i, n=int(hw_i * 0.72),
                         angle=118, length=(5, 14), width=(0.5, 1.6), opacity=(0.35, 0.8), curve=0.3))
        o.append(strokes(f"{uid}-r{i}", d, (cx, box[1], box[2], box[3]), [light, darkc, hi, base_c], seed + 20 + i, n=int(hw_i * 0.72),
                         angle=62, length=(5, 14), width=(0.5, 1.6), opacity=(0.35, 0.8), curve=0.3))
        o.append(shade(f"{uid}-s{i}", d, darkc, 0.15, 1, k=5, op=0.55))
        o.append(rim(f"{uid}-h{i}", d, hi, -1, -0.5, k=1.4, op=0.6))
        if snow:
            sp = []
            for j in range(9):
                tt = j / 8
                x = cx - hw_i * 0.92 + 2 * hw_i * 0.92 * tt
                yb = apex + (bot - apex) * (abs(x - cx) / hw_i) ** 0.9 * 0.95
                sp.append((x, yb - 1))
            top_edge = [(x, y - 4 - 2 * math.sin(k * 1.7 + seed)) for k, (x, y) in enumerate(sp)]
            bot_edge = [(x, y + 3 + 2.5 * abs(math.sin(k * 2.3 + seed))) for k, (x, y) in enumerate(reversed(sp))]
            sd = smooth_closed([(cx, apex - 2)] + top_edge[len(top_edge) // 2 + 1:] + bot_edge + top_edge[:len(top_edge) // 2])
            o.append(f'<path d="{sd}" fill="#F8FBFF"/>')
            o.append(shade(f"{uid}-sn{i}", sd, "#B7CCE2", 0, 1, k=2.2, op=0.8))
            o.append(ink(sd, "#7D93AE", 0.9, seed + i, 1, 0.55))
        o.append(ink(d, inkcol, 1.3, seed + 30 + i, 1, 0.55))
    return "".join(o)


def gift(uid, x, y, w, h, dd, col, rib, seed, pattern=None, pcol="#FFFFFF", bow=True):
    """Wrapped gift in 3/4 view: (x, y) top-left of the front face, dd = depth."""
    front = jitter([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed, 0.8)
    top = [(x, y), (x + dd, y - dd * 0.55), (x + w + dd, y - dd * 0.55), (x + w, y)]
    side = [(x + w, y), (x + w + dd, y - dd * 0.55), (x + w + dd, y + h - dd * 0.55), (x + w, y + h)]
    fd, td, sd = poly(front), poly(top), poly(side)
    o = [shadow(x + w / 2 + dd / 2, y + h, w * 0.62, 4, 0.18)]
    o.append(paint(uid + "-f", fd, bbox(front), col, seed, angle=-80, n=int(w * h / 40), ink_w=0))
    o.append(f'<path d="{sd}" fill="{dk(col, 0.22)}"/><path d="{td}" fill="{lt(col, 0.2)}"/>')
    if pattern == "dots":
        rnd = random.Random(seed)
        o.append(f'<clipPath id="{uid}-pc"><path d="{fd} {sd}"/></clipPath><g clip-path="url(#{uid}-pc)" fill="{pcol}" opacity="0.85">'
                 + "".join(f'<circle cx="{F(x + (i % 5) * w / 4 + (j % 2) * w / 8)}" cy="{F(y + j * h / 4 + 3)}" r="{F(rnd.uniform(1.4, 2))}"/>' for i in range(6) for j in range(5)) + "</g>")
    elif pattern == "stripes":
        o.append(f'<clipPath id="{uid}-pc"><path d="{fd} {sd} {td}"/></clipPath><g clip-path="url(#{uid}-pc)" stroke="{pcol}" stroke-width="2.4" opacity="0.8">'
                 + "".join(f'<path d="M {F(x - h + i * 9)} {F(y + h + 4)} l {F(h + 20)} {F(-h - 20)}"/>' for i in range(int((w + h + dd) / 9) + 4)) + "</g>")
    # ribbon: vertical on front, across top, horizontal on side
    rw = max(3, w * 0.13)
    mx = x + w / 2
    o.append(f'<path d="M {F(mx - rw / 2)} {F(y)} L {F(mx + rw / 2)} {F(y)} L {F(mx + rw / 2)} {F(y + h)} L {F(mx - rw / 2)} {F(y + h)} Z" fill="{rib}"/>')
    o.append(f'<path d="{poly([(mx - rw / 2, y), (mx + rw / 2, y), (mx + rw / 2 + dd, y - dd * 0.55), (mx - rw / 2 + dd, y - dd * 0.55)])}" fill="{lt(rib, 0.15)}"/>')
    o.append(f'<path d="{poly([(x + w, y + h / 2 - rw / 2), (x + w + dd, y + h / 2 - rw / 2 - dd * 0.55), (x + w + dd, y + h / 2 + rw / 2 - dd * 0.55), (x + w, y + h / 2 + rw / 2)])}" fill="{dk(rib, 0.2)}"/>')
    o.append(f'<path d="M {F(mx - rw / 2 + 1)} {F(y + 1)} L {F(mx - rw / 2 + 1)} {F(y + h - 1)}" stroke="{lt(rib, 0.45)}" stroke-width="0.9" opacity="0.8"/>')
    o.append(ink(fd + " " + sd + " " + td, inkc(col), 1.2, seed, 1, 0.6))
    if bow:
        bx, by = mx + dd / 2, y - dd * 0.28
        s = max(6, w * 0.22)
        for sg in (-1, 1):
            lp = blob(bx + sg * s * 0.55, by - s * 0.25, s * 0.55, s * 0.32, seed + sg, 0.06, 12, rot=sg * -20)
            o.append(paint(f"{uid}-bw{sg}", lp, (bx - s * 1.2, by - s, bx + s * 1.2, by + s * 0.2), rib, seed + 3 + sg, n=8, ink_w=0.9, angle=sg * 20))
            o.append(f'<path d="M {F(bx)} {F(by)} q {F(sg * s * 0.3)} {F(s * 0.5)} {F(sg * s * 0.55)} {F(s * 0.85)}" stroke="{rib}" stroke-width="{F(s * 0.22)}" stroke-linecap="round" fill="none"/>')
        o.append(f'<circle cx="{F(bx)}" cy="{F(by - s * 0.15)}" r="{F(s * 0.2)}" fill="{dk(rib, 0.15)}" stroke="{inkc(rib)}" stroke-width="0.7"/>')
    return "".join(o)


def santa_hat(uid, cx, base, w, seed, droop=1):
    """Red Santa hat sitting on a head: band centred at (cx, base), w = band width; the tip flops to one side."""
    pts = [(cx - w * 0.46, base), (cx - w * 0.36, base - w * 0.42), (cx - w * 0.05, base - w * 0.72), (cx + droop * w * 0.34, base - w * 0.7),
           (cx + droop * w * 0.62, base - w * 0.38), (cx + droop * w * 0.66, base - w * 0.14), (cx + droop * w * 0.5, base - w * 0.3),
           (cx + droop * w * 0.22, base - w * 0.42), (cx + w * 0.46, base)]
    d = smooth_closed(pts)
    o = [paint(uid, d, bbox(pts), "#C8323A", seed, tints=["#E8605E", "#8E1A20", "#F07A70"], angle=-30 * droop, n=34, ink_col="#6E1418", ink_w=1.4,
               length=(4, 12), width=(0.5, 1.4))]
    o.append(shade(uid + "-s", d, "#7A1218", 0.6 * droop, 0.8, k=4, op=0.4))
    band = smooth_closed([(cx - w * 0.56, base + 3), (cx - w * 0.52, base - w * 0.12), (cx, base - w * 0.16), (cx + w * 0.52, base - w * 0.12),
                          (cx + w * 0.56, base + 3), (cx, base + w * 0.08)])
    o.append(f'<path d="{band}" fill="#FBF6EE"/>' + strokes(uid + "-f", band, (cx - w * 0.6, base - w * 0.2, cx + w * 0.6, base + w * 0.1),
                                                           ["#DCD2C2", "#FFFFFF", "#C9BCA8"], seed, n=30, angle=-70, length=(2, 5), width=(0.4, 1),
                                                           opacity=(0.5, 0.9), curve=0.6) + ink(band, "#9A8A72", 1.1, seed, 1, 0.6))
    px, py = cx + droop * w * 0.66, base - w * 0.12
    pom = blob(px, py, w * 0.15, w * 0.14, seed + 2, 0.14, 14)
    o.append(f'<path d="{pom}" fill="#FBF6EE"/>' + strokes(uid + "-p", pom, (px - w * 0.2, py - w * 0.2, px + w * 0.2, py + w * 0.2),
                                                          ["#DCD2C2", "#FFFFFF", "#C9BCA8"], seed + 3, n=18, angle=-60, length=(2, 5), width=(0.4, 1),
                                                          opacity=(0.5, 0.9), curve=0.6) + ink(pom, "#9A8A72", 1, seed, 1, 0.6))
    return "".join(o)


def candy_cane(cx, top, h, rot_=0, w=5):
    d = f"M {F(cx)} {F(top + h)} L {F(cx)} {F(top + w * 1.4)} A {F(w * 1.5)} {F(w * 1.5)} 0 0 0 {F(cx - w * 3)} {F(top + w * 1.4)} L {F(cx - w * 3)} {F(top + w * 2.6)}"
    return (f'<g transform="rotate({rot_} {F(cx)} {F(top + h)})" fill="none" stroke-linecap="round">'
            f'<path d="{d}" stroke="#7A1218" stroke-width="{F(w + 1.6)}"/><path d="{d}" stroke="#FFF8F0" stroke-width="{F(w)}"/>'
            f'<path d="{d}" stroke="#D2323A" stroke-width="{F(w)}" stroke-dasharray="{F(w * 0.9)} {F(w * 0.9)}" stroke-linecap="butt"/>'
            f'<path d="{d}" stroke="#FFFFFF" stroke-width="{F(w * 0.25)}" opacity="0.6" transform="translate(-1 0)"/></g>')


def xmas_snowman(u, cx, base, s=1.0):
    """Little snowman in a Santa hat with a plaid-green scarf, holding a candy cane."""
    def p(x, y):
        return (cx + x * s, base + y * s)
    o = [shadow(cx + 4 * s, base - 2, 46 * s, 6, 0.12)]
    o.append(stick_arm([p(-20, -76), p(-38, -88), p(-52, -100), p(-60, -114)], 5))
    o.append(stick_arm([p(20, -78), p(36, -76), p(50, -80), p(60, -84)], 6))
    o.append(snowball(u + "-b1", *p(0, -30), 38 * s, 31 * s, 21))
    o.append(snowball(u + "-b2", *p(0, -80), 27 * s, 24 * s, 22))
    o.append(snowball(u + "-b3", *p(0, -122), 21 * s, 19 * s, 23))
    for k, y in enumerate((-88, -74, -40)):
        bx, by = p(1, y)
        o.append(f'<path d="{blob(bx, by, 3.2 * s, 3 * s, 24 + k, 0.1, 9)}" fill="#2A2A33"/><circle cx="{F(bx - 0.8)}" cy="{F(by - 1)}" r=".9" fill="#8A8A9A"/>')
    hx, hy = p(0, -124)
    for sg in (-1, 1):
        o.append(f'<path d="{blob(hx + sg * 7 * s, hy - 2 * s, 2.6 * s, 3 * s, 33 + sg, 0.1, 9)}" fill="#2A2A33"/><circle cx="{F(hx + sg * 7 * s - 0.8)}" cy="{F(hy - 3 * s)}" r=".8" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{F(hx + sg * 12 * s)}" cy="{F(hy + 7 * s)}" r="{F(4 * s)}" fill="#F08A8A" opacity="0.45"/>')
    o.append(f'<path d="M {F(hx - 6 * s)} {F(hy + 9 * s)} Q {F(hx)} {F(hy + 14 * s)} {F(hx + 6 * s)} {F(hy + 9 * s)}" stroke="#2A2A33" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round"/>')
    nose = smooth_closed([(hx - 1, hy + 1), (hx + 19 * s, hy + 6 * s), (hx - 1, hy + 7 * s)])
    o.append(paint(u + "-n", nose, (hx - 2, hy, hx + 20 * s, hy + 8 * s), "#EE7A2A", 5, tints=["#F8A85A", "#B9531E"], angle=8, n=6, ink_col="#8A3A12", ink_w=0.8))
    # scarf: green with red stripes, one end hanging
    sy = base - 102 * s
    wrapd = smooth_closed([(cx - 22 * s, sy - 3 * s), (cx, sy + 2 * s), (cx + 22 * s, sy - 3 * s), (cx + 23 * s, sy + 6 * s), (cx, sy + 11 * s), (cx - 23 * s, sy + 6 * s)])
    endd = smooth_closed([(cx - 16 * s, sy + 4 * s), (cx - 6 * s, sy + 6 * s), (cx - 8 * s, sy + 24 * s), (cx - 6 * s, sy + 38 * s), (cx - 18 * s, sy + 38 * s), (cx - 18 * s, sy + 22 * s)])
    for k, dd in enumerate((endd, wrapd)):
        o.append(paint(f"{u}-sc{k}", dd, (cx - 26 * s, sy - 6 * s, cx + 26 * s, sy + 40 * s), "#2F7A57", 40 + k, tints=["#4C9C72", "#1E5A3E"], angle=-84 if k == 0 else 0,
                       n=14, ink_col="#163626", ink_w=1.1))
    o.append(f'<clipPath id="{u}-scc"><path d="{wrapd} {endd}"/></clipPath><g clip-path="url(#{u}-scc)" stroke="#C8323A" stroke-width="{F(2.6 * s)}" opacity="0.9">'
             + "".join(f'<path d="M {F(cx - 30 * s + i * 9 * s)} {F(sy - 6 * s)} l {F(4 * s)} {F(18 * s)}"/>' for i in range(7))
             + f'<path d="M {F(cx - 22 * s)} {F(sy + 24 * s)} l {F(18 * s)} 0 M {F(cx - 22 * s)} {F(sy + 31 * s)} l {F(18 * s)} 0"/></g>')
    o.append('<g stroke="#2F7A57" stroke-width="1.5" stroke-linecap="round">' + "".join(
        f'<path d="M {F(cx - 17 * s + i * 2.6 * s)} {F(sy + 38 * s)} l {F(0.3 * (i - 2))} {F(5 * s)}"/>' for i in range(5)) + "</g>")
    o.append(santa_hat(u + "-hat", hx, hy - 12 * s, 40 * s, 8, droop=1))
    # candy cane in the raised left hand
    lx, ly = p(-60, -114)
    o.append(candy_cane(lx + 4, ly - 26 * s, 50 * s, -12, w=4.4 * s))
    return "".join(o)


def snow_bank(uid, x0, x1, y, h, seed):
    rnd = random.Random(seed)
    n = 9
    top = [(x0 + (x1 - x0) * i / (n - 1), y - h * (0.5 + 0.5 * math.sin(math.pi * i / (n - 1))) - rnd.uniform(0, 3)) for i in range(n)]
    pts = [(x0 - 4, y + 2)] + top + [(x1 + 4, y + 2), (x1 - 10, y + 7), ((x0 + x1) / 2, y + 9), (x0 + 10, y + 7)]
    d = smooth_closed(pts)
    return (f'<path d="{d}" fill="#F7FAFE"/>' + shade(uid, d, "#AFC4DC", 0.2, 1, k=3.5, op=0.75)
            + strokes(uid + "-s", d, bbox(pts), ["#DCE7F3", "#FFFFFF", "#C7D7E8"], seed, n=36, angle=-4, length=(8, 22), width=(0.6, 1.4), opacity=(0.4, 0.8))
            + ink(d, "#7D93AE", 1.1, seed, 1, 0.55))


def christmas_scene(u="xm"):
    o = [glow(u + "-gl", 150, 150, 150, 160, "#FFE6A0", 0.35)]
    o.append(snow_bank(u + "-snow", 10, 372, 312, 14, 3))
    # pot + trunk
    o.append(f'<path d="M 141 268 L 159 268 L 160 292 L 140 292 Z" fill="#6E4A2A"/>')
    pot = [(116, 284), (184, 284), (178, 314), (122, 314)]
    o.append(paint(u + "-pot", smooth_closed(jitter(pot, 2, 0.5)) if False else poly(jitter(pot, 2, 0.6)), bbox(pot), "#B8323A", 7, angle=-88, n=30))
    o.append(paint(u + "-rim", poly([(112, 280), (188, 280), (187, 290), (113, 290)]), (110, 278, 190, 292), "#E2B04A", 8, angle=0, n=14, ink_w=1.0))
    o.append(fir(u + "-t", 150, 50, 282, 104, 4, 40))
    # bead garlands
    for k, (y0, y1, hw) in enumerate(((112, 128, 40), (164, 186, 62), (214, 240, 84))):
        d = f"M {F(150 - hw)} {F(y0)} Q {F(150)} {F(y1 + 14)} {F(150 + hw)} {F(y0 + 10)}"
        o.append(f'<path d="{d}" stroke="#7A5212" stroke-width="3.2" fill="none" stroke-dasharray="0.1 6.5" stroke-linecap="round" transform="translate(0.6 1)" opacity="0.6"/>'
                 f'<path d="{d}" stroke="#F2C14E" stroke-width="3.2" fill="none" stroke-dasharray="0.1 6.5" stroke-linecap="round"/>')
    # fairy lights
    rnd = random.Random(6)
    lights = [(132, 96), (168, 104), (118, 146), (184, 150), (148, 134), (100, 200), (200, 196), (128, 186), (172, 222), (86, 252), (214, 254), (150, 262), (114, 236)]
    o.append(f'<defs><radialGradient id="{u}-lg"><stop offset="0" stop-color="#FFF2B0" stop-opacity="0.9"/><stop offset="1" stop-color="#FFD25E" stop-opacity="0"/></radialGradient></defs>')
    for x, y in lights:
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#{u}-lg)"/><circle cx="{x}" cy="{y}" r="1.9" fill="#FFF6C8"/>')
    # baubles
    balls = [(140, 82, 6.5, "#C8323A"), (162, 120, 7, "#3E7CB1"), (126, 128, 6.5, "#E9B949"), (104, 172, 7.5, "#C8323A"), (186, 176, 7.5, "#F3E6D0"),
             (150, 166, 7, "#C8323A"), (80, 228, 8, "#3E7CB1"), (128, 218, 8, "#E9B949"), (176, 210, 8, "#C8323A"), (220, 230, 8, "#E9B949"),
             (106, 262, 8, "#F3E6D0"), (190, 266, 8, "#3E7CB1"), (60, 270, 7, "#C8323A")]
    for k, (x, y, r, c) in enumerate(balls):
        o.append(glass_bulb(f"{u}-ba{k}", x, y, r, c, 50 + k))
    # star topper
    o.append(glow(u + "-sg", 150, 44, 34, 34, "#FFE08A", 0.8))
    sp = star_pts(150, 44, 17, 0.46)
    sd = smooth_closed(sp) if False else poly(sp)
    o.append(paint(u + "-star", sd, bbox(sp), "#F2C14E", 9, tints=["#FFE59A", "#D29A22", "#FFF4C8"], angle=-60, n=20, ink_col="#8A5E12", ink_w=1.3))
    o.append(f'<path d="{sd}" fill="none" stroke="#8A5E12" stroke-width="1.6" stroke-linejoin="round" opacity="0.6"/>')
    # gifts
    o.append(gift(u + "-g1", 22, 270, 52, 40, 14, "#C8323A", "#F2C14E", 61, pattern="dots", pcol="#FFF3DE"))
    o.append(gift(u + "-g2", 172, 284, 40, 28, 12, "#2F7A57", "#C8323A", 62, pattern="stripes", pcol="#F3E6D0"))
    o.append(gift(u + "-g3", 84, 292, 34, 22, 10, "#F3E6D0", "#C8323A", 63))
    o.append(xmas_snowman(u + "-sm", 302, 312, 1.0))
    return "".join(o)


def christmas_garland(u="xg"):
    o = []
    rnd = random.Random(5)
    # rope of needles: dark under-layer, mid, then bright tips; every needle also drawn one tile over near the edges
    layers = [("#1E4A38", 230, 1.7, 0.9), ("#2F6B4F", 260, 1.5, 0.95), ("#4C8C62", 180, 1.2, 0.9), ("#7FB27E", 80, 1.0, 0.85)]
    for col, n, w, op in layers:
        segs = []
        for _ in range(n):
            x = rnd.uniform(0, TW)
            y = swag_y(x) + rnd.uniform(-5, 5)
            a = rnd.uniform(0, 2 * math.pi)
            L = rnd.uniform(5, 10)
            dx, dy = L * math.cos(a), L * math.sin(a) * 0.8
            for sh in (0, TW, -TW):
                xx = x + sh
                if -12 < xx < TW + 12:
                    segs.append(f'M {F(xx)} {F(y)} l {F(dx)} {F(dy)}')
        o.append(f'<path d="{" ".join(segs)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="{op}" fill="none"/>')
    # little pine cones and red berries along the rope
    def cone(x):
        y = swag_y(x) + 3
        return (f'<g transform="rotate({F(swag_slope(x) + 80)} {F(x)} {F(y)})"><path d="{blob(x, y, 7, 4.2, 3, 0.05, 12)}" fill="#8A5A32"/>'
                + "".join(f'<path d="M {F(x - 5 + i * 3.3)} {F(y - 3)} q 1.5 3 0 6" stroke="#4E2E16" stroke-width="0.9" fill="none"/>' for i in range(4))
                + f'<path d="M {F(x - 5)} {F(y - 2)} q 5 -2 10 0" stroke="#C99A62" stroke-width="0.8" fill="none" opacity="0.8"/></g>')
    def berries(x):
        y = swag_y(x) + 1
        return "".join(f'<circle cx="{F(x + dx)}" cy="{F(y + dy)}" r="2.6" fill="#C8323A" stroke="#6E1418" stroke-width="0.6"/><circle cx="{F(x + dx - 0.8)}" cy="{F(y + dy - 0.8)}" r="0.8" fill="#FFFFFF" opacity="0.8"/>'
                       for dx, dy in ((0, 0), (4, 2), (1.5, 4.5)))
    o.append(cone(112) + cone(220) + berries(76) + berries(176) + berries(262))
    # glass bulbs hanging below
    for k, (x, c, L) in enumerate(((52, "#C8323A", 10), (140, "#E9B949", 16), (192, "#3E7CB1", 14), (284, "#C8323A", 9))):
        y = swag_y(x)
        o.append(f'<path d="M {F(x)} {F(y)} L {F(x)} {F(y + L)}" stroke="#7A6A4A" stroke-width="0.9"/>')
        o.append(glass_bulb(f"{u}-b{k}", x, y + L + 10, 8, c, 80 + k))
    o.append(glass_bulb(f"{u}-b9", 240, swag_y(240) + 16, 6.5, "#F3E6D0", 89))
    # red bow at the hanging point (drawn at both edges so the halves meet)
    def bow(x):
        y = 9
        out = []
        for sg in (-1, 1):
            tl = smooth_closed([(x + sg * 2, y + 2), (x + sg * 6, y + 14), (x + sg * 9, y + 30), (x + sg * 4, y + 27), (x + sg * 2, y + 31), (x + sg * 2, y + 14)])
            out.append(f'<path d="{tl}" fill="#B8262E"/>' + ink(tl, "#6E1418", 0.9, 4, 1, 0.6))
            lp = blob(x + sg * 11, y - 1, 11, 6.5, 7 + sg, 0.06, 12, rot=sg * 14)
            out.append(paint(f"{u}-bw{sg}{int(x)}", lp, (x - 24, y - 10, x + 24, y + 8), "#C8323A", 9 + sg, tints=["#E8605E", "#8E1A20"], angle=sg * 14, n=10, ink_col="#6E1418", ink_w=1.1))
            out.append(f'<path d="M {F(x + sg * 4)} {F(y - 2)} q {F(sg * 7)} -4 {F(sg * 14)} 0" stroke="#F28A80" stroke-width="1.2" fill="none" opacity="0.8"/>')
        out.append(f'<path d="{blob(x, y, 4.6, 5, 3, 0.05, 10)}" fill="#A81E26" stroke="#6E1418" stroke-width="0.9"/>')
        return "".join(out)
    o.append(bow(0) + bow(TW))
    return "".join(o)


def snowflake(cx, cy, r, kind, rot_=0, edge="#9EC2E2"):
    """Painted snowflake: white arms over a soft blue edge so it reads on cream and on dark brown."""
    arms = []
    for i in range(6):
        a = math.radians(rot_ + i * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        def P(t, off=0.0):
            return cx + (ca * t - sa * off) * r, cy + (sa * t + ca * off) * r
        x1, y1 = P(1)
        arms.append(f"M {F(cx)} {F(cy)} L {F(x1)} {F(y1)}")
        if kind == 1:
            for t, L in ((0.5, 0.3), (0.75, 0.2)):
                for sg in (-1, 1):
                    bx, by = P(t)
                    ex, ey = P(t + L * 0.7, sg * L)
                    arms.append(f"M {F(bx)} {F(by)} L {F(ex)} {F(ey)}")
        elif kind == 2:
            bx, by = P(0.55)
            for sg in (-1, 1):
                ex, ey = P(0.82, sg * 0.24)
                arms.append(f"M {F(bx)} {F(by)} L {F(ex)} {F(ey)}")
        else:
            for t in (0.42,):
                for sg in (-1, 1):
                    bx, by = P(t)
                    ex, ey = P(t + 0.22, sg * 0.24)
                    arms.append(f"M {F(bx)} {F(by)} L {F(ex)} {F(ey)}")
    d = " ".join(arms)
    w = max(1.4, r * 0.16)
    out = [f'<path d="{d}" stroke="{edge}" stroke-width="{F(w + 2.2)}" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>',
           f'<path d="{d}" stroke="#FFFFFF" stroke-width="{F(w)}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>']
    if kind == 2:
        hx = poly([(cx + 0.26 * r * math.cos(math.radians(rot_ + i * 60)), cy + 0.26 * r * math.sin(math.radians(rot_ + i * 60))) for i in range(6)])
        out.append(f'<path d="{hx}" fill="#FFFFFF" stroke="{edge}" stroke-width="1.2"/>')
    if kind == 3:
        for i in range(6):
            a = math.radians(rot_ + i * 60 - 90)
            out.append(f'<circle cx="{F(cx + math.cos(a) * r)}" cy="{F(cy + math.sin(a) * r)}" r="{F(w * 0.9)}" fill="#FFFFFF" stroke="{edge}" stroke-width="1"/>')
    out.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(w * 0.9)}" fill="#FFFFFF" stroke="{edge}" stroke-width="0.9"/>')
    return "".join(out)


def particles_snow():
    save("snow1", 40, 40, snowflake(20, 20, 16, 1, 0))
    save("snow2", 40, 40, snowflake(20, 20, 15, 2, 15))
    save("snow3", 40, 40, snowflake(20, 20, 13, 3, 5))


# ================================================================ WINTER
def snowball(uid, cx, cy, rx, ry, seed):
    d = blob(cx, cy, rx, ry, seed, 0.035, 18)
    box = (cx - rx - 3, cy - ry - 3, cx + rx + 3, cy + ry + 3)
    return (f'<path d="{d}" fill="#F8FAFD"/>'
            + shade(uid + "-sh", d, "#B9CCE2", 0.65, 0.75, k=rx * 0.22, op=0.75)
            + strokes(uid, d, box, ["#DDE7F3", "#FFFFFF", "#C9D8EA"], seed, n=int(rx * 1.2), angle=-10, length=(rx * 0.2, rx * 0.6), width=(0.6, 1.8), opacity=(0.4, 0.8), curve=0.4)
            + rim(uid + "-hi", d, "#FFFFFF", -0.7, -0.7, k=2, op=0.9)
            + ink(d, "#7D93AE", 1.5, seed, 2, 0.6))


def stick_arm(pts, seed):
    d = smooth_open(pts)
    rnd = random.Random(seed)
    tw = []
    for i in (1, 2):
        x, y = pts[i]
        x2, y2 = pts[min(i + 1, len(pts) - 1)]
        a = math.atan2(y2 - y, x2 - x) + rnd.choice([-0.7, 0.7])
        tw.append(f"M {F(x)} {F(y)} l {F(math.cos(a) * 12)} {F(math.sin(a) * 12)}")
    x, y = pts[-1]
    x0, y0 = pts[-2]
    a = math.atan2(y - y0, x - x0)
    for da in (-0.6, 0.5):
        tw.append(f"M {F(x)} {F(y)} l {F(math.cos(a + da) * 9)} {F(math.sin(a + da) * 9)}")
    t = " ".join(tw)
    return (f'<path d="{d}" stroke="#4A2E18" stroke-width="5.2" fill="none" stroke-linecap="round"/><path d="{d}" stroke="#8A5A32" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
            f'<path d="{t}" stroke="#4A2E18" stroke-width="3.2" fill="none" stroke-linecap="round"/><path d="{t}" stroke="#8A5A32" stroke-width="1.8" fill="none" stroke-linecap="round"/>')


def cardinal(uid, x, y, s=1.0, flip=False, seed=41):
    """Red cardinal perched, facing left; (x, y) = feet."""
    def p(px, py):
        return (x + (-px if flip else px) * s, y + py * s)
    body = [p(-10, -22), p(-6, -30), p(4, -29), p(12, -22), p(14, -12), p(6, -3), p(-6, -3), p(-12, -10)]
    crest = poly([p(-8, -27), p(-6, -38), p(0, -29)])
    tail = smooth_closed([p(10, -10), p(26, -2), p(30, 2), p(24, 4), p(8, -4)])
    wing = smooth_closed([p(-2, -22), p(10, -20), p(20, -8), p(12, -6), p(0, -12)])
    o = [f'<path d="{tail}" fill="#8E161C"/>' + ink(tail, "#4E080C", 0.9, seed, 1, 0.6)]
    o.append(f'<path d="{crest}" fill="#C8262A" stroke="#6E1016" stroke-width="0.8" stroke-linejoin="round"/>')
    o.append(paint(uid, smooth_closed(body), bbox(body), "#C8262A", seed, tints=["#F0584A", "#8E161C", "#F57A62"], angle=-40, n=24, ink_col="#5E0C12", ink_w=1.1,
                   length=(3, 9), width=(0.4, 1.1)))
    o.append(f'<path d="{wing}" fill="#9E1A20"/><path d="{smooth_open([p(0, -18), p(10, -14), p(18, -8)])}" stroke="#5E0C12" stroke-width="0.9" fill="none" opacity="0.8"/>')
    o.append(f'<path d="{smooth_closed([p(-12, -26), p(-6, -27), p(-4, -20), p(-9, -16), p(-13, -19)])}" fill="#1A0E0E"/>')
    o.append(f'<path d="{poly([p(-11, -25), p(-18, -22), p(-11, -19)])}" fill="#F2913A" stroke="#9A5A1A" stroke-width="0.6" stroke-linejoin="round"/>')
    ex, ey = p(-7, -24)
    o.append(f'<circle cx="{F(ex)}" cy="{F(ey)}" r="{F(1.4 * s)}" fill="#000"/><circle cx="{F(ex - 0.4 * s)}" cy="{F(ey - 0.5 * s)}" r="{F(0.5 * s)}" fill="#FFFFFF"/>')
    o.append(f'<path d="{smooth_open([p(-4, -29), p(4, -28), p(11, -22)])}" stroke="#FF9A84" stroke-width="{F(1.2 * s)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append(f'<g stroke="#4A2E24" stroke-width="1.3" stroke-linecap="round" fill="none"><path d="M {F(p(-3, -3)[0])} {F(p(-3, -3)[1])} l 0 3"/><path d="M {F(p(3, -3)[0])} {F(p(3, -3)[1])} l 0 3"/></g>')
    return "".join(o)


def knit_hat(uid, cx, base, w, h, col, band, seed):
    pts = [(cx - w / 2, base), (cx - w * 0.46, base - h * 0.5), (cx - w * 0.25, base - h * 0.92), (cx, base - h), (cx + w * 0.25, base - h * 0.92),
           (cx + w * 0.46, base - h * 0.5), (cx + w / 2, base)]
    d = smooth_closed(pts)
    o = [paint(uid, d, bbox(pts), col, seed, angle=-90, n=30, length=(4, 10), width=(0.6, 1.4))]
    # ribbing columns
    o.append(f'<clipPath id="{uid}-c"><path d="{d}"/></clipPath><g clip-path="url(#{uid}-c)" stroke="{dk(col, 0.25)}" stroke-width="1" opacity="0.6">'
             + "".join(f'<path d="M {F(cx - w / 2 + i * w / 9)} {F(base)} Q {F(cx - w / 2 + i * w / 9 + (i - 4.5) * 0.8)} {F(base - h * 0.6)} {F(cx + (i - 4.5) * 2)} {F(base - h)}"/>' for i in range(1, 9)) + "</g>")
    bd = smooth_closed([(cx - w / 2 - 3, base + 1), (cx - w / 2 - 1, base - h * 0.28), (cx, base - h * 0.32), (cx + w / 2 + 1, base - h * 0.28), (cx + w / 2 + 3, base + 1), (cx, base + 4)])
    o.append(paint(uid + "-bd", bd, (cx - w / 2 - 4, base - h * 0.34, cx + w / 2 + 4, base + 5), band, seed + 3, angle=0, n=16, ink_w=1.1))
    o.append(f'<g fill="none" stroke="{col}" stroke-width="1.4" stroke-linecap="round">' + "".join(
        f'<path d="M {F(cx - w / 2 + 3 + i * (w - 2) / 7)} {F(base - h * 0.12)} l 2.5 -3 l 2.5 3"/>' for i in range(7)) + "</g>")
    pom = blob(cx + 1, base - h - 6, 9, 8.5, seed, 0.12, 14)
    o.append(f'<path d="{pom}" fill="#FBF6EE"/>' + strokes(uid + "-pm", pom, (cx - 10, base - h - 16, cx + 12, base - h + 4), ["#DCD2C2", "#FFFFFF", "#C9BCA8"], seed, n=22,
                                                            angle=-60, length=(2, 6), width=(0.4, 1), opacity=(0.5, 0.9), curve=0.6)
             + ink(pom, "#9A8A72", 1, seed, 1, 0.6))
    return "".join(o)


def winter_scene(u="wn"):
    o = []
    o.append(fir(u + "-p1", 62, 64, 300, 54, 5, 70, cols=("#2C5848", "#467A62", "#183A2E", "#6E9E86"), snow=True))
    o.append(fir(u + "-p2", 330, 110, 302, 44, 4, 80, cols=("#2C5848", "#467A62", "#183A2E", "#6E9E86"), snow=True))
    o.append(fir(u + "-p3", 22, 190, 304, 26, 3, 90, cols=("#355E52", "#4E806A", "#1E4236", "#7AA690"), snow=True))
    cx = 192
    o.append(stick_arm([(cx - 28, 196), (cx - 54, 180), (cx - 78, 166), (cx - 92, 150)], 3))
    o.append(stick_arm([(cx + 28, 196), (cx + 54, 186), (cx + 82, 176), (cx + 100, 172)], 4))
    o.append(snowball(u + "-b1", cx, 268, 54, 44, 11))
    o.append(snow_bank(u + "-sb", 4, 376, 316, 16, 7))
    o.append(snowball(u + "-b2", cx, 198, 39, 34, 12))
    o.append(snowball(u + "-b3", cx, 142, 29, 27, 13))
    for k, y in enumerate((186, 204, 222)):
        o.append(f'<path d="{blob(cx + 2, y, 3.6, 3.4, 20 + k, 0.1, 9)}" fill="#2A2A33"/><circle cx="{cx + 1}" cy="{y - 1.2}" r="1" fill="#8A8A9A"/>')
    # face
    for sg in (-1, 1):
        o.append(f'<path d="{blob(cx + sg * 10, 136, 3.4, 3.8, 30 + sg, 0.1, 9)}" fill="#2A2A33"/><circle cx="{cx + sg * 10 - 1}" cy="134.8" r="1" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{cx + sg * 17}" cy="148" r="5" fill="#F08A8A" opacity="0.45"/>')
    o.append("".join(f'<circle cx="{F(cx + x)}" cy="{F(156 + 0.012 * x * x)}" r="1.9" fill="#2A2A33"/>' for x in (-9, -4.5, 0, 4.5, 9)))
    nose = smooth_closed([(cx - 1, 140), (cx + 26, 147), (cx - 1, 149)])
    o.append(paint(u + "-n", nose, (cx - 2, 138, cx + 27, 151), "#EE7A2A", 5, tints=["#F8A85A", "#B9531E"], angle=8, n=8, ink_col="#8A3A12", ink_w=0.9))
    o.append(f'<path d="M {cx + 6} 141.5 l 1 2 M {cx + 13} 143.5 l 1 2" stroke="#9A4A14" stroke-width="0.8"/>')
    # scarf: wrap + hanging end, red with cream stripes and fringe
    wrapd = smooth_closed([(cx - 30, 163), (cx, 170), (cx + 30, 163), (cx + 31, 175), (cx, 182), (cx - 31, 175)])
    o.append(paint(u + "-sc", wrapd, (cx - 33, 160, cx + 33, 184), "#C2343A", 6, tints=["#E8605E", "#8E1A20"], angle=0, n=20, ink_col="#6E1418", ink_w=1.2))
    endd = smooth_closed([(cx + 12, 174), (cx + 26, 172), (cx + 30, 196), (cx + 33, 218), (cx + 18, 220), (cx + 16, 196)])
    o.append(paint(u + "-se", endd, (cx + 10, 170, cx + 35, 222), "#C2343A", 7, tints=["#E8605E", "#8E1A20"], angle=-84, n=14, ink_col="#6E1418", ink_w=1.2))
    o.append(f'<clipPath id="{u}-scc"><path d="{wrapd} {endd}"/></clipPath><g clip-path="url(#{u}-scc)" stroke="#F6EEDD" stroke-width="3.2" opacity="0.9">'
             + "".join(f'<path d="M {cx - 40 + i * 12} 160 l 6 26"/>' for i in range(7)) + f'<path d="M {cx + 10} 200 l 30 -3 M {cx + 10} 208 l 30 -3"/></g>')
    o.append('<g stroke="#C2343A" stroke-width="1.6" stroke-linecap="round">' + "".join(f'<path d="M {cx + 19 + i * 3.2} 219 l {0.3 * (i - 2)} 6"/>' for i in range(5)) + "</g>")
    o.append(knit_hat(u + "-hat", cx + 1, 124, 58, 40, "#34507A", "#F3E6D0", 8))
    o.append(cardinal(u + "-cd", cx + 86, 172, 1.25))
    # a few soft falling flakes
    for k, (x, y, r) in enumerate(((120, 40, 5), (262, 68, 4.5), (300, 30, 3.6), (36, 40, 3.6), (238, 92, 3.4), (366, 60, 4))):
        o.append(snowflake(x, y, r, 3 if k % 2 else 2, k * 11))
    return "".join(o)


def winter_garland(u="wg"):
    o = []
    # icicles hanging under the snowy twig
    rnd = random.Random(12)
    ic = []
    for x in range(6, TW, 13):
        if abs(x - 80) < 9 or abs(x - 240) < 9:
            continue
        L = rnd.choice([9, 14, 20, 11, 16, 24])
        y = swag_y(x) + 2
        d = f"M {F(x - 3)} {F(y)} Q {F(x - 1.8)} {F(y + L * 0.6)} {F(x + 0.3)} {F(y + L)} Q {F(x + 1.4)} {F(y + L * 0.5)} {F(x + 3)} {F(y)} Z"
        ic.append((d, x, y, L))
    for d, x, y, L in ic:
        o.append(f'<path d="{d}" fill="#E6F1FB" stroke="#7FA6CC" stroke-width="0.9" stroke-linejoin="round"/>'
                 f'<path d="M {F(x - 1.2)} {F(y + 2)} Q {F(x - 0.8)} {F(y + L * 0.5)} {F(x)} {F(y + L * 0.8)}" stroke="#FFFFFF" stroke-width="1" fill="none" stroke-linecap="round"/>')
    # birch twig garland with a snow cap
    tw = f"M 0 10 C 80 34 240 34 320 10"
    o.append(f'<path d="{tw}" stroke="#6E5A48" stroke-width="3.6" fill="none"/><path d="{tw}" stroke="#A89480" stroke-width="1.2" fill="none" stroke-dasharray="5 7"/>')
    cap_top = [(x, swag_y(x) - 3.2 - 1.4 * abs(math.sin(x * 0.11))) for x in range(-4, TW + 5, 8)]
    cap_bot = [(x, swag_y(x) + 0.6) for x in range(TW + 4, -5, -8)]
    capd = "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in cap_top + cap_bot) + " Z"
    o.append(f'<path d="{capd}" fill="#F8FBFF" stroke="#8FB0D0" stroke-width="0.9" stroke-linejoin="round"/>')
    # snowflakes dangling on threads
    for k, (x, L, r, kind) in enumerate(((80, 14, 10, 1), (240, 18, 10, 2))):
        y = swag_y(x)
        o.append(f'<path d="M {x} {F(y)} L {x} {F(y + L)}" stroke="#7FA6CC" stroke-width="0.9"/>')
        o.append(snowflake(x, y + L + r, r, kind, 0, edge="#88B0D8"))
    # pine sprigs at the hanging points and in the middle, with red berries
    def sprig(x, flip=1):
        y = swag_y(x) - 1
        out = []
        r2 = random.Random(int(x) + 3)
        for side in (-1, 1):
            for j in range(16):
                t = j / 15
                bx = x + side * t * 22
                by = swag_y(min(max(bx, 0), TW)) - 1 if 0 <= bx <= TW else y + t * 2
                a = math.radians((-60 if j % 2 else 60) + r2.uniform(-15, 15) + (180 if side < 0 else 0))
                L = 7 - t * 3
                out.append(f"M {F(bx)} {F(by)} l {F(math.cos(a) * L)} {F(math.sin(a) * L)}")
        p = " ".join(out)
        b = "".join(f'<circle cx="{F(x + dx)}" cy="{F(y + dy)}" r="2.5" fill="#C2343A" stroke="#6E1418" stroke-width="0.6"/>' for dx, dy in ((-2, 3), (2.5, 4), (0, 7)))
        return (f'<path d="{p}" stroke="#1E4A38" stroke-width="1.8" stroke-linecap="round" fill="none"/>'
                f'<path d="{p}" stroke="#4C8C62" stroke-width="0.9" stroke-linecap="round" fill="none" transform="translate(-0.4 -0.6)"/>' + b)
    o.append(sprig(0) + sprig(TW) + sprig(160))
    return "".join(o)


# ================================================================ VALENTINE
def rose(uid, cx, cy, r, col, seed):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r * 0.92, seed, 0.12, 12)
    o = [paint(uid, d, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), col, seed, tints=[lt(col, 0.25), dk(col, 0.3)], angle=-30, n=10, ink_col=dk(col, 0.55), ink_w=1.0)]
    # spiral petals
    arcs = []
    for k, rr in enumerate((0.78, 0.55, 0.34)):
        a0 = rnd.uniform(0, 360)
        for j in range(2):
            a = math.radians(a0 + j * 170)
            x0, y0 = cx + rr * r * math.cos(a), cy + rr * r * math.sin(a)
            a2 = a + math.radians(150)
            x1, y1 = cx + rr * r * math.cos(a2), cy + rr * r * math.sin(a2)
            arcs.append(f"M {F(x0)} {F(y0)} A {F(rr * r)} {F(rr * r * 0.9)} 0 0 1 {F(x1)} {F(y1)}")
    o.append(f'<path d="{" ".join(arcs)}" stroke="{dk(col, 0.42)}" stroke-width="{F(max(0.8, r * 0.1))}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    o.append(f'<path d="M {F(cx - 0.6 * r)} {F(cy - 0.5 * r)} A {F(0.8 * r)} {F(0.8 * r)} 0 0 1 {F(cx + 0.3 * r)} {F(cy - 0.75 * r)}" stroke="{lt(col, 0.45)}" stroke-width="{F(max(0.8, r * 0.12))}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append(f'<circle cx="{F(cx + 0.05 * r)}" cy="{F(cy)}" r="{F(r * 0.14)}" fill="{dk(col, 0.4)}"/>')
    return "".join(o)


def leaf(uid, x, y, L, w, ang, col, seed, vein=None):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (x + ux * L, y + uy * L)
    pts = [(x, y), (x + ux * L * 0.3 + nx * w, y + uy * L * 0.3 + ny * w), (x + ux * L * 0.7 + nx * w * 0.7, y + uy * L * 0.7 + ny * w * 0.7), tip,
           (x + ux * L * 0.7 - nx * w * 0.7, y + uy * L * 0.7 - ny * w * 0.7), (x + ux * L * 0.3 - nx * w, y + uy * L * 0.3 - ny * w)]
    d = smooth_closed(pts)
    o = [f'<path d="{d}" fill="{col}"/>', f'<path d="M {F(x)} {F(y)} Q {F(x + ux * L * 0.5 + nx * w * 0.15)} {F(y + uy * L * 0.5 + ny * w * 0.15)} {F(tip[0])} {F(tip[1])}" stroke="{vein or lt(col, 0.35)}" stroke-width="0.8" fill="none" opacity="0.8"/>',
         f'<path d="{poly([(x, y), pts[1], pts[2], tip])}" fill="{dk(col, 0.2)}" opacity="0.35"/>', ink(d, dk(col, 0.45), 0.8, seed, 1, 0.6)]
    return "".join(o)


def envelope(uid, cx, cy, w, h, rot_, col="#FBF3E6", seal="#C8323A", seed=1):
    pts = jitter([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], seed, 0.4)
    d = poly(pts)
    return (f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">'
            f'<path d="{d}" fill="{col}"/>'
            f'<path d="M {F(cx - w / 2)} {F(cy - h / 2)} L {F(cx)} {F(cy + h * 0.12)} L {F(cx + w / 2)} {F(cy - h / 2)}" fill="{dk(col, 0.07)}" stroke="#B89A80" stroke-width="0.8" stroke-linejoin="round"/>'
            f'<path d="M {F(cx - w / 2)} {F(cy + h / 2)} L {F(cx - w * 0.1)} {F(cy)} M {F(cx + w / 2)} {F(cy + h / 2)} L {F(cx + w * 0.1)} {F(cy)}" stroke="#D2BCA4" stroke-width="0.7"/>'
            + ink(d, "#8A6A52", 1.0, seed, 1, 0.7)
            + f'<path d="{heart_d(cx, cy + h * 0.08, h * 0.17)}" fill="{seal}" stroke="{dk(seal, 0.4)}" stroke-width="0.6"/></g>')


def balloon(uid, cx, cy, s, col, rot_, seed, tie):
    o = []
    tipx, tipy = rot(cx, cy + 0.85 * s, cx, cy, rot_)
    # curly string down to the tie point
    tx, ty = tie
    pts = [(tipx, tipy + 3)]
    n = 6
    for i in range(1, n):
        t = i / n
        pts.append((tipx + (tx - tipx) * t + (5 if i % 2 else -5), tipy + 3 + (ty - tipy - 3) * t))
    pts.append((tx, ty))
    o.append(f'<path d="{smooth_open(pts)}" stroke="#9A7A8A" stroke-width="1" fill="none"/>')
    o.append(painted_heart(uid, cx, cy, s, col, seed, rot_=rot_, ink_w=1.3))
    o.append(f'<path d="M {F(tipx - 3)} {F(tipy + 4)} L {F(tipx)} {F(tipy - 1)} L {F(tipx + 3)} {F(tipy + 4)} Z" fill="{dk(col, 0.15)}" stroke="{inkc(col)}" stroke-width="0.7"/>')
    return "".join(o)


def valentine_scene(u="vl"):
    o = [shadow(196, 318, 150, 9, 0.14)]
    tie = (204, 214)
    o.append(balloon(u + "-h1", 104, 70, 30, "#D8344A", -14, 1, tie))
    o.append(balloon(u + "-h2", 178, 34, 26, "#F28AA0", 6, 2, tie))
    o.append(balloon(u + "-h3", 300, 64, 32, "#E8556A", 12, 3, tie))
    # post
    post = jitter([(197, 196), (211, 196), (212, 316), (196, 316)], 4, 0.6)
    o.append(paint(u + "-post", poly(post), bbox(post), "#A8774E", 5, tints=["#C99A6A", "#7A5034"], angle=-90, n=16, ink_col="#5A3A22", ink_w=1.2))
    o.append(f'<path d="M 194 214 q 10 5 20 0" stroke="#D8344A" stroke-width="2.4" fill="none"/>'
             f'<path d="M 204 216 q -8 -10 -12 -2 q 4 6 12 2 q 8 -10 12 -2 q -4 6 -12 2" fill="#E8556A" stroke="#8E1A2A" stroke-width="0.8"/>')
    # mailbox body (side), then the open front with letters, then the door hanging open
    side = [(150, 132), (204, 128), (262, 126), (276, 136), (279, 160), (276, 188), (262, 196), (204, 198), (150, 200)]
    sd = smooth_closed(side)
    o.append(paint(u + "-mb", sd, bbox(side), "#C93A48", 6, tints=["#E8605E", "#9E1E2C", "#F08A84"], angle=-4, n=60, ink_col="#5E1018", ink_w=1.6))
    o.append(shade(u + "-mbs", sd, "#7A1220", 0, 1, k=6, op=0.4))
    o.append(rim(u + "-mbh", sd, "#F6A8A0", 0, -1, k=2, op=0.7))
    o.append(f'<path d="M 166 138 Q 220 131 268 134" stroke="#F6B8B0" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(painted_heart(u + "-mh", 222, 166, 13, "#FBF0E6", 9, ink_w=0.9, shine=False, stitch="#D8344A"))
    front = blob(150, 166, 22, 35, 9, 0.02, 16)
    o.append(f'<path d="{front}" fill="#A82A38" stroke="#5E1018" stroke-width="1.6"/>')
    o.append(f'<path d="{blob(151, 167, 16, 29, 10, 0.02, 14)}" fill="#4A1A22"/>')
    o.append(envelope(u + "-e1", 150, 160, 30, 20, -24, seed=2))
    o.append(envelope(u + "-e2", 146, 176, 30, 20, 8, col="#F8DDE2", seed=3))
    # door swung open toward us on its left hinge (seen almost edge-on)
    door = blob(124, 170, 9, 34, 11, 0.02, 16)
    o.append(paint(u + "-dr", door, (112, 134, 136, 206), "#E8707A", 7, tints=["#F6A8A0", "#C93A48"], angle=-90, n=12, ink_col="#5E1018", ink_w=1.4))
    o.append(f'<path d="{blob(126, 170, 4, 26, 12, 0.03, 12)}" fill="#C93A48" opacity="0.6"/>')
    o.append(f'<path d="M 132 150 L 136 152 M 132 190 L 136 188" stroke="#5E1018" stroke-width="2.2" stroke-linecap="round"/>')
    # flag (raised)
    o.append(f'<path d="M 252 162 L 254 104" stroke="#8A6212" stroke-width="4" stroke-linecap="round"/><path d="M 252 162 L 254 104" stroke="#E9B949" stroke-width="2.4" stroke-linecap="round"/>')
    flag = jitter([(254, 100), (282, 98), (282, 116), (254, 118)], 5, 0.6)
    o.append(paint(u + "-fl", poly(flag), bbox(flag), "#E9B949", 8, tints=["#F6D88A", "#B88A1E"], angle=0, n=10, ink_col="#7A5212", ink_w=1.1))
    o.append(f'<path d="{heart_d(268, 108, 5)}" fill="#D8344A"/>')
    o.append(f'<circle cx="252" cy="162" r="3.2" fill="#8A6212"/>')
    # rose bushes at the foot of the post
    lv = [(150, 304, 22, 8, -150), (170, 290, 20, 7, -110), (238, 300, 22, 8, -30), (222, 286, 18, 7, -70), (266, 308, 18, 6, -10),
          (128, 312, 18, 6, -170), (186, 296, 18, 7, -100), (248, 290, 18, 6, -50), (204, 284, 16, 6, -88), (276, 314, 14, 5, 10), (118, 316, 14, 5, 190)]
    for k, (x, y, L, w, a) in enumerate(lv):
        o.append(leaf(f"{u}-lf{k}", x, y + 6, L, w, a, "#4E7A3E" if k % 2 else "#3E6A34", 30 + k))
    for k, (x, y, r, c) in enumerate(((160, 298, 13, "#D8344A"), (184, 286, 11, "#F28AA0"), (230, 292, 14, "#C8263A"), (256, 304, 11, "#F28AA0"),
                                      (138, 308, 10, "#E8556A"), (206, 302, 12, "#E8556A"), (178, 308, 9, "#F6B3C0"), (232, 312, 9, "#D8344A"))):
        o.append(rose(f"{u}-r{k}", x, y, r, c, 40 + k))
    o.append(envelope(u + "-e4", 86, 306, 34, 22, -12, col="#F8DDE2", seed=6))
    o.append(envelope(u + "-e5", 300, 308, 30, 20, 14, seed=7))
    for x, y, s, c in ((60, 130, 7, "#F28AA0"), (240, 60, 5, "#D8344A"), (340, 140, 6, "#F28AA0"), (130, 140, 4.5, "#E8556A")):
        o.append(painted_heart(f"{u}-sm{x}", x, y, s, c, x, ink_w=0.7))
    return "".join(o)


def valentine_garland(u="vg"):
    o = [twine("#9A6A72", "#E8B8C0", 1.8)]
    cols = ["#D8344A", "#F28AA0", "#C8263A", "#F6B3C0", "#E8556A", "#D8344A", "#F28AA0"]
    for k in range(7):
        x = 23 + k * 45.7
        y = swag_y(x)
        big = k % 2 == 0
        s = 11 if big else 8
        L = 6 if big else 10
        rr = (-1) ** k * 8
        o.append(f'<path d="M {F(x)} {F(y)} L {F(x)} {F(y + L)}" stroke="#9A6A72" stroke-width="0.9"/>')
        o.append(painted_heart(f"{u}-h{k}", x, y + L + s * 0.9, s, cols[k], 10 + k, rot_=rr, stitch="#FFF3F0" if k in (0, 4) else None))
    for x in (45.7, 137, 228, 0, 320):
        y = swag_y(x)
        o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="2" fill="#F2C14E" stroke="#9A7A2A" stroke-width="0.5"/>')
    return "".join(o)


def particles_valentine():
    save("heart1", 40, 40, painted_heart("ph1", 20, 19, 15, "#D8344A", 1, rot_=-8))
    save("heart2", 40, 40, painted_heart("ph2", 20, 19, 13, "#F28AA0", 2, rot_=10, stitch="#FFF3F0"))


# ================================================================ SPRING
def tulip(uid, x, base, top, col, seed, lean=0):
    hx, hy = x + lean, top
    stem = smooth_open([(x, base), (x + lean * 0.4, (base + top) / 2), (hx, hy + 8)])
    o = [f'<path d="{stem}" stroke="#3E6A2E" stroke-width="3.6" fill="none" stroke-linecap="round"/><path d="{stem}" stroke="#6E9A48" stroke-width="1.2" fill="none" stroke-linecap="round" transform="translate(-0.8 0)"/>']
    s = 13
    cup = [(hx - s * 0.75, hy - s * 0.3), (hx - s * 0.5, hy - s * 1.05), (hx - s * 0.2, hy - s * 0.62), (hx, hy - s * 1.15), (hx + s * 0.22, hy - s * 0.62),
           (hx + s * 0.52, hy - s * 1.05), (hx + s * 0.75, hy - s * 0.3), (hx + s * 0.5, hy + s * 0.4), (hx, hy + s * 0.55), (hx - s * 0.5, hy + s * 0.4)]
    d = smooth_closed(cup)
    o.append(paint(uid, d, bbox(cup), col, seed, tints=[lt(col, 0.3), dk(col, 0.25), lt(col, 0.5)], angle=-90, n=18, length=(4, 12), width=(0.5, 1.4)))
    o.append(f'<path d="M {F(hx)} {F(hy - s * 1.0)} Q {F(hx - s * 0.1)} {F(hy - s * 0.1)} {F(hx)} {F(hy + s * 0.5)}" stroke="{dk(col, 0.3)}" stroke-width="1" fill="none" opacity="0.7"/>')
    o.append(f'<path d="M {F(hx - s * 0.45)} {F(hy - s * 0.7)} Q {F(hx - s * 0.62)} {F(hy - s * 0.1)} {F(hx - s * 0.36)} {F(hy + s * 0.2)}" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.5" stroke-linecap="round"/>')
    return "".join(o)


def blade(uid, x, base, L, w, lean, col, seed):
    tip = (x + lean, base - L)
    pts = [(x - w / 2, base), (x - w * 0.5 + lean * 0.3, base - L * 0.45), (tip[0], tip[1]), (x + w * 0.4 + lean * 0.5, base - L * 0.5), (x + w / 2, base)]
    d = smooth_closed(pts)
    return paint(uid, d, bbox(pts), col, seed, tints=[lt(col, 0.3), dk(col, 0.25)], angle=-90 + lean * 0.4, n=10, ink_w=0.9, length=(6, 18), width=(0.4, 1.2))


def pot(uid, cx, top, bottom, wt, wb, seed, soil=True):
    rimh = 13
    body = jitter([(cx - wt / 2 + 4, top + rimh), (cx + wt / 2 - 4, top + rimh), (cx + wb / 2, bottom), (cx - wb / 2, bottom)], seed, 0.6)
    rimp = jitter([(cx - wt / 2, top), (cx + wt / 2, top), (cx + wt / 2 - 1, top + rimh), (cx - wt / 2 + 1, top + rimh)], seed + 1, 0.5)
    o = [shadow(cx + 4, bottom, wb * 0.7, 5, 0.18)]
    o.append(paint(uid + "-b", poly(body), bbox(body), "#C66A3D", seed, tints=["#D88A5A", "#9A4A26", "#E8A070"], angle=-88, n=40, ink_col="#6E3418"))
    o.append(shade(uid + "-bs", poly(body), "#7A3418", 1, 0, k=7, op=0.35))
    o.append(paint(uid + "-r", poly(rimp), bbox(rimp), "#D27A4A", seed + 2, tints=["#E89A6A", "#A85A2E"], angle=0, n=18, ink_col="#6E3418"))
    o.append(f'<path d="M {F(cx - wt / 2 + 2)} {F(top + rimh + 1.5)} L {F(cx + wt / 2 - 2)} {F(top + rimh + 1.5)}" stroke="#7A3418" stroke-width="2" opacity="0.4"/>')
    if soil:
        o.append(f'<path d="{blob(cx, top + 1, wt / 2 - 3, 3.6, seed, 0.05, 14)}" fill="#5A3A24"/>')
    return "".join(o)


def bunny(uid, cx, base, s, seed=51):
    def p(x, y):
        return (cx + x * s, base + y * s)
    fur, tints = "#D9C4A6", ["#EADBC4", "#B89E7E", "#C9B08E"]
    o = [shadow(cx, base, 34 * s, 5 * s, 0.16)]
    tailp = p(-27, -14)
    o.append(f'<path d="{blob(*tailp, 7 * s, 6.5 * s, seed, 0.15, 12)}" fill="#FFFDF8" stroke="#B8A890" stroke-width="0.9"/>')
    bpts = [p(-28, -4), p(-30, -22), p(-20, -38), p(-4, -44), p(12, -38), p(18, -22), p(16, -4), p(0, 0)]
    bd = smooth_closed(bpts)
    o.append(paint(uid + "-b", bd, bbox(bpts), fur, seed, tints=tints, angle=-60, n=40, ink_col="#7A6248", length=(3, 9), width=(0.5, 1.2)))
    o.append(shade(uid + "-bs", bd, "#9A7E5E", -0.4, 1, k=4, op=0.3))
    o.append(f'<path d="{blob(*p(-14, -6), 9 * s, 5 * s, seed + 3, 0.06, 12)}" fill="{fur}" stroke="#7A6248" stroke-width="1"/>')
    # ears
    for k, (ex, ang) in enumerate(((2, -100), (10, -74))):
        e = smooth_closed([p(ex - 4, -52), p(ex - 6 + (ang + 90) * 0.1, -74), p(ex + (ang + 90) * 0.25, -88), p(ex + 5 + (ang + 90) * 0.12, -74), p(ex + 4, -52)])
        o.append(paint(f"{uid}-e{k}", e, (cx + (ex - 10) * s, base - 92 * s, cx + (ex + 12) * s, base - 48 * s), fur, seed + 5 + k, tints=tints, angle=-90, n=10, ink_col="#7A6248", ink_w=1.1))
        o.append(f'<path d="{smooth_closed([p(ex - 1.5, -56), p(ex - 2.5 + (ang + 90) * 0.1, -72), p(ex + (ang + 90) * 0.22, -82), p(ex + 2.5 + (ang + 90) * 0.1, -72), p(ex + 1.6, -56)])}" fill="#F2B6B8" opacity="0.9"/>')
    hd = blob(*p(8, -50), 15 * s, 13 * s, seed + 7, 0.04, 14)
    o.append(paint(uid + "-h", hd, (cx - 8 * s, base - 64 * s, cx + 24 * s, base - 36 * s), fur, seed + 8, tints=tints, angle=-20, n=18, ink_col="#7A6248"))
    o.append(f'<path d="{blob(*p(16, -45), 7 * s, 5.5 * s, seed + 9, 0.05, 10)}" fill="#FFF8EE" opacity="0.9"/>')
    o.append(f'<circle cx="{F(p(13, -53)[0])}" cy="{F(p(13, -53)[1])}" r="{F(2.6 * s)}" fill="#2A1A10"/><circle cx="{F(p(12.2, -53.8)[0])}" cy="{F(p(12.2, -53.8)[1])}" r="{F(0.9 * s)}" fill="#FFFFFF"/>')
    o.append(f'<path d="{heart_d(*p(22, -48), 1.8 * s, 180)}" fill="#E07A8A"/>')
    o.append(f'<circle cx="{F(p(15, -45)[0])}" cy="{F(p(15, -45)[1])}" r="{F(3.4 * s)}" fill="#F2A0A6" opacity="0.4"/>')
    o.append(f'<g stroke="#9A8468" stroke-width="0.6" opacity="0.8">' + "".join(f'<path d="M {F(p(20, -46)[0])} {F(p(20, -46)[1])} l {F(10 * s)} {F(dy * s)}"/>' for dy in (-2, 1)) + "</g>")
    o.append(f'<path d="{blob(*p(10, -3), 6 * s, 3.4 * s, seed + 11, 0.06, 10)}" fill="#EADBC4" stroke="#7A6248" stroke-width="0.9"/>')
    return "".join(o)


def watering_can(uid, x, base, s, col="#86AFC0", seed=61):
    def p(px, py):
        return (x + px * s, base + py * s)
    o = [shadow(*p(0, 0), 40 * s, 5 * s, 0.18)]
    hd = smooth_open([p(-14, -66), p(4, -82), p(24, -76), p(30, -58)])
    o.append(f'<path d="{hd}" stroke="#4A6A78" stroke-width="{F(9 * s)}" fill="none" stroke-linecap="round"/><path d="{hd}" stroke="{col}" stroke-width="{F(6 * s)}" fill="none" stroke-linecap="round"/>')
    sp = [p(-26, -24), p(-50, -60), p(-56, -70), p(-50, -72), p(-26, -40)]
    o.append(paint(uid + "-sp", smooth_closed(sp), bbox(sp), col, seed + 1, angle=-55, n=10, ink_col="#3E5A68"))
    rose_ = blob(*p(-54, -72), 7 * s, 4 * s, seed, 0.03, 12, rot=-55)
    o.append(f'<path d="{rose_}" fill="{dk(col, 0.1)}" stroke="#3E5A68" stroke-width="1.1"/>')
    o.append("".join(f'<circle cx="{F(p(-54 + dx, -72 + dy)[0])}" cy="{F(p(-54 + dx, -72 + dy)[1])}" r="0.7" fill="#2E4A58"/>' for dx, dy in ((-2, 1), (0, -1), (2, -3), (1, 2))))
    body = jitter([p(-30, -62), p(30, -62), p(34, -4), p(32, 0), p(-32, 0), p(-34, -4)], seed, 0.6)
    bd = smooth_closed(body)
    o.append(paint(uid, bd, bbox(body), col, seed, tints=[lt(col, 0.3), dk(col, 0.2), lt(col, 0.5)], angle=-90, n=50, ink_col="#3E5A68"))
    o.append(shade(uid + "-s", bd, "#3E5A68", 1, 0.2, k=8, op=0.3))
    o.append(f'<path d="{smooth_open([p(-22, -56), p(-24, -30), p(-22, -8)])}" stroke="#FFFFFF" stroke-width="{F(3 * s)}" fill="none" opacity="0.45" stroke-linecap="round"/>')
    for yy in (-58, -6):
        o.append(f'<path d="M {F(p(-31, yy)[0])} {F(p(-31, yy)[1])} L {F(p(32, yy)[0])} {F(p(32, yy)[1])}" stroke="#4A6A78" stroke-width="1.6" opacity="0.7"/>')
    o.append(f'<path d="{blob(*p(0, -63), 20 * s, 4 * s, seed + 2, 0.03, 14)}" fill="#3E5A68" stroke="#2E4A58" stroke-width="1"/>')
    # painted daisies on the side
    for k, (fx, fy, r) in enumerate(((-4, -34, 7), (12, -22, 5.5), (16, -44, 4.5))):
        fx, fy = p(fx, fy)
        o.append("".join(f'<ellipse cx="{F(fx + math.cos(math.radians(a)) * r * 0.6)}" cy="{F(fy + math.sin(math.radians(a)) * r * 0.6)}" rx="{F(r * 0.45)}" ry="{F(r * 0.22)}" fill="#FFFDF6" transform="rotate({a} {F(fx + math.cos(math.radians(a)) * r * 0.6)} {F(fy + math.sin(math.radians(a)) * r * 0.6)})"/>' for a in range(0, 360, 45)))
        o.append(f'<circle cx="{F(fx)}" cy="{F(fy)}" r="{F(r * 0.28)}" fill="#F2C14E"/>')
    return "".join(o)


def butterfly(x, y, s, c1, c2, rot_=0):
    o = [f'<g transform="translate({F(x)} {F(y)}) rotate({rot_})">']
    for sg in (-1, 1):
        o.append(f'<path d="{blob(sg * 6 * s, -4 * s, 6.5 * s, 5.5 * s, 3, 0.08, 10, rot=sg * 20)}" fill="{c1}" stroke="{dk(c1, 0.45)}" stroke-width="0.8"/>')
        o.append(f'<path d="{blob(sg * 5 * s, 5 * s, 4.5 * s, 4 * s, 4, 0.08, 10, rot=sg * -20)}" fill="{c2}" stroke="{dk(c2, 0.45)}" stroke-width="0.8"/>')
        o.append(f'<circle cx="{F(sg * 7 * s)}" cy="{F(-5 * s)}" r="{F(1.6 * s)}" fill="#FFFFFF" opacity="0.8"/>')
    o.append(f'<path d="M 0 {F(-7 * s)} L 0 {F(8 * s)}" stroke="#3A2418" stroke-width="{F(1.8 * s)}" stroke-linecap="round"/>'
             f'<path d="M 0 {F(-7 * s)} q -2 -5 -4 -6 M 0 {F(-7 * s)} q 2 -5 4 -6" stroke="#3A2418" stroke-width="0.7" fill="none"/></g>')
    return "".join(o)


def grass(x0, x1, y, seed, n=40, cols=("#5E8A3E", "#7FA84E", "#3E6A2E")):
    rnd = random.Random(seed)
    s = "".join(f'<path d="M {F(x)} {F(y + rnd.uniform(0, 3))} q {F(rnd.uniform(-3, 3))} {F(-h / 2)} {F(rnd.uniform(-5, 5))} {F(-h)}" stroke="{rnd.choice(cols)}"/>'
                for x, h in [(rnd.uniform(x0, x1), rnd.uniform(6, 16)) for _ in range(n)])
    return f'<g stroke-width="1.6" stroke-linecap="round" fill="none">{s}</g>'


def spring_scene(u="sp"):
    o = [shadow(200, 318, 170, 9, 0.12)]
    o.append(f'<path d="{smooth_closed([(6, 318), (60, 306), (190, 304), (320, 306), (376, 318), (190, 326)])}" fill="#8DB25E" opacity="0.55"/>')
    o.append(grass(10, 370, 316, 3, 70))
    o.append(watering_can(u + "-wc", 316, 314, 1.0))
    o.append(butterfly(84, 98, 1.3, "#F2A0B8", "#F6CC6A", -15))
    o.append(butterfly(318, 96, 1.05, "#8EC0E2", "#F6E08A", 18))
    o.append(f'<path d="M 92 112 q 20 18 44 6 q 18 -10 30 4" stroke="#8A6A42" stroke-width="0.9" stroke-dasharray="2 2.6" fill="none" opacity="0.7"/>')
    # small pot (left) with yellow tulips
    for k, (x, top, c, lean) in enumerate(((104, 196, "#F6C23E", -8), (124, 184, "#F2D25E", 4))):
        o.append(tulip(f"{u}-ty{k}", x, 262, top, c, 10 + k, lean))
    o.append(blade(u + "-bl0", 100, 266, 46, 9, -14, "#5E8A3E", 1) + blade(u + "-bl1", 128, 266, 40, 8, 12, "#6E9A48", 2))
    o.append(pot(u + "-p2", 114, 258, 316, 64, 46, 5))
    # big pot with red and pink tulips
    tl = [(184, 140, "#D8344A", -14), (204, 118, "#F28AA0", 0), (226, 134, "#E8556A", 12), (196, 160, "#F6B3C0", -4), (240, 162, "#D8344A", 18)]
    for k, (x, top, c, lean) in enumerate(tl):
        o.append(tulip(f"{u}-t{k}", x, 240, top, c, 20 + k, lean))
    for k, (x, L, w, lean, c) in enumerate(((180, 70, 12, -26, "#5E8A3E"), (196, 56, 10, -6, "#6E9A48"), (222, 62, 11, 14, "#5E8A3E"), (240, 70, 12, 30, "#4E7A34"), (210, 44, 9, 4, "#7FA84E"))):
        o.append(blade(f"{u}-b{k}", x, 244, L, w, lean, c, 30 + k))
    o.append(pot(u + "-p1", 210, 236, 316, 96, 72, 7))
    o.append(painted_heart(u + "-ph", 210, 282, 9, "#F2E2C8", 4, ink_w=0.8, shine=False))
    o.append(bunny(u + "-bun", 52, 316, 1.15))
    for x, y in ((280, 316), (150, 318), (16, 314)):
        o.append("".join(f'<ellipse cx="{F(x + math.cos(math.radians(a)) * 3)}" cy="{F(y - 6 + math.sin(math.radians(a)) * 3)}" rx="2.4" ry="1.3" fill="#FFFFFF" transform="rotate({a} {F(x + math.cos(math.radians(a)) * 3)} {F(y - 6 + math.sin(math.radians(a)) * 3)})"/>' for a in range(0, 360, 60))
                 + f'<circle cx="{x}" cy="{y - 6}" r="1.4" fill="#F2C14E"/>')
    return "".join(o)


def blossom(cx, cy, r, col, center="#F2C14E", rot_=0):
    pet = []
    for i in range(5):
        a = math.radians(rot_ + i * 72 - 90)
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        pet.append(f'<ellipse cx="{F(px)}" cy="{F(py)}" rx="{F(r * 0.5)}" ry="{F(r * 0.38)}" transform="rotate({F(math.degrees(a))} {F(px)} {F(py)})"/>')
    return (f'<g fill="{col}" stroke="{dk(col, 0.3)}" stroke-width="0.8">{"".join(pet)}</g>'
            f'<g fill="none" stroke="{dk(col, 0.15)}" stroke-width="0.7" opacity="0.8">' + "".join(
                f'<path d="M {F(cx)} {F(cy)} l {F(math.cos(math.radians(rot_ + i * 72 - 90)) * r * 0.6)} {F(math.sin(math.radians(rot_ + i * 72 - 90)) * r * 0.6)}"/>' for i in range(5)) + "</g>"
            f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 0.24)}" fill="{center}" stroke="#B88A1E" stroke-width="0.5"/>')


def bee(x, y, s, rot_=0):
    return (f'<g transform="translate({F(x)} {F(y)}) rotate({rot_}) scale({s})">'
            '<ellipse cx="-2" cy="-7" rx="5" ry="7" fill="#FFFFFF" stroke="#7FA6CC" stroke-width="0.8" opacity="0.9" transform="rotate(-25 -2 -7)"/>'
            '<ellipse cx="4" cy="-7" rx="4.4" ry="6" fill="#FFFFFF" stroke="#7FA6CC" stroke-width="0.8" opacity="0.9" transform="rotate(25 4 -7)"/>'
            '<ellipse cx="0" cy="0" rx="9" ry="6.4" fill="#F6C23E" stroke="#3A2418" stroke-width="1.1"/>'
            '<path d="M -3 -6 q -1.4 6 0 12 M 2 -6.2 q -1.4 6 0 12.4" stroke="#3A2418" stroke-width="2.4" fill="none"/>'
            '<circle cx="8" cy="-1" r="3.6" fill="#3A2418"/><circle cx="9" cy="-2" r="0.9" fill="#FFFFFF"/>'
            '<path d="M -9 0 l -3 0" stroke="#3A2418" stroke-width="1.4" stroke-linecap="round"/></g>')


def spring_garland(u="sg"):
    o = []
    # vine twisting around the swag
    pts = [(x, swag_y(x) + 2.5 * math.sin(x / TW * 2 * math.pi * 3)) for x in range(0, TW + 1, 10)]
    vd = smooth_open(pts)
    o.append(f'<path d="{vd}" stroke="#3E6A2E" stroke-width="2.6" fill="none"/><path d="{vd}" stroke="#7FA84E" stroke-width="0.9" fill="none" transform="translate(0 -0.8)"/>')
    rnd = random.Random(4)
    for k, x in enumerate(range(14, TW, 26)):
        y = swag_y(x)
        side = -1 if k % 2 else 1
        o.append(leaf(f"{u}-l{k}", x, y, 13, 5, 90 * side + rnd.uniform(-35, 35) - 10, "#5E8A3E" if k % 3 else "#6E9A48", 50 + k))
    # tendrils
    for x in (60, 200, 290):
        y = swag_y(x)
        o.append(f'<path d="M {x} {F(y)} q 4 6 0 10 q -4 3 -2 -2" stroke="#5E8A3E" stroke-width="0.9" fill="none"/>')
    for k, (x, c, r) in enumerate(((36, "#F6B3C8", 8.5), (100, "#FFF6F2", 8), (170, "#F28AA8", 9), (232, "#F6B3C8", 7.5), (300, "#FFF6F2", 8.5))):
        y = swag_y(x) + (3 if k % 2 else -1)
        o.append(blossom(x, y, r, c, rot_=k * 17))
    for x, y in ((70, swag_y(70) + 6), (264, swag_y(264) + 5)):
        o.append(f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="3" ry="4.2" fill="#F28AA8" stroke="#B8506A" stroke-width="0.6"/><path d="M {F(x - 3)} {F(y - 2)} q 3 -4 6 0" stroke="#5E8A3E" stroke-width="1.4" fill="none"/>')
    o.append(f'<path d="M 108 60 q 8 -10 18 -2 q 8 6 14 -4" stroke="#8A6A42" stroke-width="0.9" stroke-dasharray="2 2.4" fill="none" opacity="0.8"/>')
    o.append(bee(150, 54, 0.95, -6))
    return "".join(o)


def petal(uid, cx, cy, s, col, rot_, seed, edge=None):
    pts = [(0, -1.0), (0.18, -0.82), (0.55, -0.5), (0.62, 0.05), (0.35, 0.6), (0, 0.9), (-0.35, 0.6), (-0.62, 0.05), (-0.55, -0.5), (-0.18, -0.82)]
    pts = [rot(cx + x * s, cy + y * s, cx, cy, rot_) for x, y in pts]
    pts[0] = rot(cx, cy - 0.74 * s, cx, cy, rot_)  # the little notch at the tip
    d = smooth_closed(pts)
    o = [paint(uid, d, bbox(pts), col, seed, tints=[lt(col, 0.4), dk(col, 0.12)], angle=rot_ - 90, n=10, ink_col=edge or dk(col, 0.35), ink_w=1.0,
               length=(s * 0.4, s * 1.2), width=(0.4, 1.0), op=(0.3, 0.6))]
    a = rot(cx, cy + 0.85 * s, cx, cy, rot_)
    b = rot(cx, cy + 0.1 * s, cx, cy, rot_)
    o.append(f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{dk(col, 0.25)}" stroke-width="0.9" opacity="0.6" stroke-linecap="round"/>')
    o.append(f'<path d="{blob(*rot(cx, cy + 0.55 * s, cx, cy, rot_), 0.2 * s, 0.25 * s, seed, 0.05, 8)}" fill="#E05A88" opacity="0.35"/>')
    return "".join(o)


def particles_spring():
    save("petal1", 40, 40, petal("pp1", 20, 20, 15, "#F6A8C0", 20, 1))
    save("petal2", 40, 40, petal("pp2", 20, 20, 13, "#FCE2EA", -30, 2, edge="#D88AA2"))
    save("petal3", 40, 40, blossom(20, 20, 15, "#F8C0D2", rot_=10))


# ================================================================ SUMMER
def umbrella(uid, cx, cy, R, rot_, cols, seed):
    """Beach umbrella canopy centred on the pole top (cx, cy), radius R, tilted rot_ degrees."""
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    n = 6
    rimy = cy + R * 0.42
    xs = [cx - R + 2 * R * i / n for i in range(n + 1)]
    apex = (cx, cy - R * 0.06)
    for i in range(n):
        x0, x1 = xs[i], xs[i + 1]
        mid = (x0 + x1) / 2
        d = (f"M {F(apex[0])} {F(apex[1])} Q {F(x0 + (apex[0] - x0) * 0.35)} {F(cy - R * 0.25)} {F(x0)} {F(rimy)} "
             f"Q {F(mid)} {F(rimy + R * 0.13)} {F(x1)} {F(rimy)} Q {F(x1 + (apex[0] - x1) * 0.35)} {F(cy - R * 0.25)} {F(apex[0])} {F(apex[1])} Z")
        c = cols[i % 2]
        o.append(paint(f"{uid}-{i}", d, (x0 - 4, cy - R * 0.4, x1 + 4, rimy + R * 0.16), c, seed + i, angle=-90 + (mid - cx) * 0.4, n=16,
                       tints=[lt(c, 0.25), dk(c, 0.12), lt(c, 0.45)], ink_col="#6A2E1E", ink_w=1.2, length=(6, 22), width=(0.5, 1.6)))
    under = f"M {F(xs[0])} {F(rimy)} " + " ".join(f"Q {F((xs[i] + xs[i + 1]) / 2)} {F(rimy + R * 0.13)} {F(xs[i + 1])} {F(rimy)}" for i in range(n))
    o.append(f'<path d="{under}" stroke="#6A2E1E" stroke-width="1.6" fill="none" opacity="0.7"/>')
    o.append(f'<path d="{under}" stroke="#F2C14E" stroke-width="2.2" stroke-dasharray="0.1 9" stroke-linecap="round" fill="none" transform="translate(0 3)"/>')
    o.append(f'<path d="{blob(apex[0], apex[1] - 3, 5, 4, 2, 0.05, 10)}" fill="#F2C14E" stroke="#7A5212" stroke-width="1"/>')
    o.append("</g>")
    return "".join(o)


def sandcastle(uid, x, base, seed=71):
    sand, tints = "#E2BE7E", ["#F2D8A6", "#C29A5A", "#D8B06E", "#F8E6C0"]
    o = [shadow(x + 54, base, 66, 6, 0.18)]
    def block(k, pts, n=26):
        d = poly(jitter(pts, seed + k, 0.8))
        return paint(f"{uid}-{k}", d, bbox(pts), sand, seed + k, tints=tints, angle=-4, n=n, ink_col="#8A6232", ink_w=1.2, length=(4, 12), width=(0.4, 1.2), op=(0.35, 0.7))
    def crenel(x0, x1, y, h=6, n=3):
        pts = [(x0, y + h)]
        w = (x1 - x0) / (2 * n - 1)
        for i in range(2 * n - 1):
            yy = y if i % 2 == 0 else y + h
            pts += [(x0 + i * w, yy), (x0 + (i + 1) * w, yy)]
        pts.append((x1, y + h))
        return pts
    # keep
    keep = [(x + 22, base), (x + 22, base - 52)] + crenel(x + 22, x + 86, base - 58, 7, 4)[1:-1] + [(x + 86, base - 52), (x + 86, base)]
    o.append(block(1, keep, 40))
    o.append(shade(uid + "-ks", poly(keep), "#9A7040", 1, 0, k=6, op=0.3))
    # centre tower
    tower = [(x + 42, base - 50), (x + 42, base - 84)] + crenel(x + 40, x + 68, base - 90, 6, 3)[1:-1] + [(x + 66, base - 84), (x + 66, base - 50)]
    o.append(block(2, tower, 22))
    # side towers
    for k, (tx, th) in enumerate(((x, 74), (x + 84, 64))):
        tp = [(tx, base), (tx + 2, base - th + 6)] + crenel(tx, tx + 26, base - th, 6, 2)[1:-1] + [(tx + 24, base - th + 6), (tx + 26, base)]
        o.append(block(3 + k, tp, 26))
        o.append(f'<path d="M {tx + 9} {base - th + 26} q 4 -6 8 0 l 0 8 l -8 0 Z" fill="#7A5232" opacity="0.85"/>')
    # door, windows, shells, flag
    o.append(f'<path d="M {x + 46} {base} L {x + 46} {base - 18} Q {x + 54} {base - 30} {x + 62} {base - 18} L {x + 62} {base} Z" fill="#7A5232"/>')
    o.append(f'<path d="M {x + 50} {base - 66} q 4 -6 8 0 l 0 7 l -8 0 Z" fill="#7A5232" opacity="0.85"/>')
    o.append(f'<path d="M {x + 54} {base - 90} L {x + 54} {base - 114}" stroke="#6A4A2A" stroke-width="1.6"/><path d="M {x + 54} {base - 114} q 9 3 16 0 q -4 4 0 8 q -8 3 -16 0 Z" fill="#E8604C" stroke="#8A2E1E" stroke-width="0.8"/>')
    for sx, sy, c in ((x + 30, base - 30, "#F6B3A8"), (x + 76, base - 24, "#FFF3E6"), (x + 12, base - 44, "#F6CC9A")):
        o.append(f'<path d="M {sx - 4} {sy + 2} Q {sx} {sy - 6} {sx + 4} {sy + 2} Z" fill="{c}" stroke="#9A6A4A" stroke-width="0.7"/>'
                 f'<path d="M {sx} {sy + 2} l 0 -5 M {sx - 2} {sy + 2} l -1 -3.6 M {sx + 2} {sy + 2} l 1 -3.6" stroke="#9A6A4A" stroke-width="0.5"/>')
    return "".join(o)


def pail(uid, cx, base, seed=81):
    top, wt, wb, h = base - 46, 56, 42, 46
    body = jitter([(cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2, base), (cx - wb / 2, base)], seed, 0.5)
    o = [shadow(cx + 4, base, 34, 5, 0.18)]
    # shovel sticking out behind the rim
    o.append(f'<path d="M {cx + 4} {top + 10} L {cx + 22} {top - 34}" stroke="#B8862E" stroke-width="5" stroke-linecap="round"/><path d="M {cx + 4} {top + 10} L {cx + 22} {top - 34}" stroke="#F6C23E" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<path d="{smooth_closed([(cx + 18, top - 34), (cx + 30, top - 52), (cx + 26, top - 60), (cx + 16, top - 56), (cx + 14, top - 40)])}" fill="#F6C23E" stroke="#8A6212" stroke-width="1.1"/>')
    o.append(paint(uid, poly(body), bbox(body), "#3FA3B5", seed, tints=["#6EC2D0", "#2A7A8A", "#9AD8E2"], angle=-88, n=36, ink_col="#1E5A66"))
    o.append(shade(uid + "-s", poly(body), "#1E5A66", 1, 0, k=7, op=0.3))
    o.append(f'<clipPath id="{uid}-c"><path d="{poly(body)}"/></clipPath><g clip-path="url(#{uid}-c)"><path d="M {cx - 40} {top + 18} L {cx + 40} {top + 18}" stroke="#FFF6E6" stroke-width="7"/>'
             f'<path d="M {cx - 40} {top + 18} L {cx + 40} {top + 18}" stroke="#F2644A" stroke-width="7" stroke-dasharray="4 6"/></g>')
    o.append(f'<path d="{blob(cx, top, wt / 2, 4.6, seed, 0.03, 14)}" fill="#2A7A8A" stroke="#1E5A66" stroke-width="1.2"/>')
    o.append(f'<path d="{blob(cx, top + 1, wt / 2 - 4, 2.6, seed + 1, 0.05, 12)}" fill="#E2BE7E"/>')
    o.append(f'<path d="M {cx - wt / 2 + 2} {top + 3} Q {cx} {top - 40} {cx + wt / 2 - 2} {top + 3}" stroke="#1E5A66" stroke-width="2.2" fill="none"/>')
    return "".join(o)


def starfish(uid, cx, cy, r, col, rot_, seed):
    sp = star_pts(cx, cy, r, 0.45, rot_ - 90)
    d = smooth_closed([p for i, p in enumerate(sp)])
    d = smooth_closed(jitter(sp, seed, 0.6))
    o = [paint(uid, d, bbox(sp), col, seed, tints=[lt(col, 0.3), dk(col, 0.2)], angle=rot_, n=14, ink_w=1.1)]
    rnd = random.Random(seed)
    for i in range(5):
        a = math.radians(rot_ - 90 + i * 72)
        for t in (0.3, 0.5, 0.7):
            o.append(f'<circle cx="{F(cx + math.cos(a) * r * t)}" cy="{F(cy + math.sin(a) * r * t)}" r="{F(max(0.8, r * 0.07))}" fill="{lt(col, 0.55)}"/>')
    del rnd
    return "".join(o)


def beach_ball(uid, cx, cy, r, seed):
    d = blob(cx, cy, r, r * 0.98, seed, 0.02, 16)
    o = [shadow(cx + 3, cy + r - 1, r * 1.05, 3.4, 0.2), f'<path d="{d}" fill="#FFF8EE"/>',
         f'<clipPath id="{uid}-c"><path d="{d}"/></clipPath><g clip-path="url(#{uid}-c)">']
    for k, (a0, col) in enumerate(((-150, "#E8604C"), (-30, "#F6C23E"), (90, "#3B7DC4"))):
        a1, a2 = math.radians(a0 - 22), math.radians(a0 + 22)
        o.append(f'<path d="M {F(cx - 0.18 * r)} {F(cy - 0.3 * r)} L {F(cx + math.cos(a1) * r * 1.4)} {F(cy + math.sin(a1) * r * 1.4)} '
                 f'L {F(cx + math.cos(a2) * r * 1.4)} {F(cy + math.sin(a2) * r * 1.4)} Z" fill="{col}"/>')
    o.append(f'<circle cx="{F(cx - 0.18 * r)}" cy="{F(cy - 0.3 * r)}" r="{F(r * 0.16)}" fill="#FFF8EE" stroke="#B8A88A" stroke-width="0.6"/></g>')
    o.append(shade(uid + "-s", d, "#3A2418", 0.7, 0.7, k=r * 0.22, op=0.22))
    o.append(f'<path d="M {F(cx - 0.62 * r)} {F(cy - 0.2 * r)} Q {F(cx - 0.6 * r)} {F(cy - 0.62 * r)} {F(cx - 0.2 * r)} {F(cy - 0.7 * r)}" stroke="#FFFFFF" stroke-width="{F(r * 0.12)}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(ink(d, "#6A3E2A", 1.3, seed, 2, 0.6))
    return "".join(o)


def summer_scene(u="sm"):
    o = []
    sandpts = [(4, 320), (40, 300), (120, 292), (220, 294), (320, 298), (376, 318), (300, 328), (190, 330), (80, 328)]
    sd = smooth_closed(sandpts)
    o.append(paint(u + "-sand", sd, bbox(sandpts), "#EED29A", 2, tints=["#F8E4B8", "#D8B672", "#E2C080"], angle=-3, n=60, ink_col="#B8925A", ink_w=1.1, length=(8, 24), width=(0.5, 1.4)))
    rnd = random.Random(9)
    o.append("".join(f'<circle cx="{F(rnd.uniform(30, 350))}" cy="{F(rnd.uniform(300, 322))}" r="{F(rnd.uniform(0.5, 1.1))}" fill="#A8824A" opacity="0.5"/>' for _ in range(40)))
    # umbrella: pole then canopy
    tilt = -14
    top = (172, 86)
    ux, uy = -math.sin(math.radians(tilt)), math.cos(math.radians(tilt))
    bot = (top[0] + ux * 228, top[1] + uy * 228)
    o.append(shadow(bot[0] - 40, 312, 90, 8, 0.12))
    o.append(f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#6A4A2A" stroke-width="5.4" stroke-linecap="round"/>'
             f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#FFF3DC" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="10 10"/>'
             f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#E8604C" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="10 10" stroke-dashoffset="10"/>')
    o.append(umbrella(u + "-um", top[0], top[1], 128, tilt, ("#E8604C", "#F8D46A"), 10))
    o.append(sandcastle(u + "-sc", 28, 310))
    o.append(pail(u + "-pl", 300, 312))
    o.append(starfish(u + "-st", 196, 312, 14, "#F08A4B", 12, 4))
    o.append(beach_ball(u + "-bb", 352, 298, 17, 6))
    o.append(f'<path d="{smooth_closed([(242, 318), (246, 306), (254, 302), (262, 306), (266, 318)])}" fill="#F8D2C8" stroke="#B8725E" stroke-width="1"/>'
             + "".join(f'<path d="M 254 318 L {x} 305" stroke="#C88A76" stroke-width="0.8"/>' for x in (246, 250, 254, 258, 262)))
    return "".join(o)


def summer_garland(u="sg"):
    o = [twine("#3E6A8A", "#9AC8E2", 2)]
    flags = [("#F2644A", "stripes", "#FFF3DC"), ("#2FA6B0", "dots", "#FFF3DC"), ("#F6C23E", "plain", "#E8604C"), ("#3B7DC4", "zig", "#FFF3DC"), ("#F28AA0", "dots", "#FFFFFF")]
    xs = [32, 96, 160, 224, 288]
    for k, x in enumerate(xs):
        base, pat, pc = flags[k]
        w, h = 44, 40
        a, b = (x - w / 2, swag_y(x - w / 2) + 1), (x + w / 2, swag_y(x + w / 2) + 1)
        tip = (x, (a[1] + b[1]) / 2 + h)
        d = (f"M {F(a[0])} {F(a[1])} Q {F(x)} {F((a[1] + b[1]) / 2 + 3)} {F(b[0])} {F(b[1])} "
             f"Q {F((b[0] + tip[0]) / 2 + 1.5)} {F((b[1] + tip[1]) / 2)} {F(tip[0])} {F(tip[1])} "
             f"Q {F((a[0] + tip[0]) / 2 - 1.5)} {F((a[1] + tip[1]) / 2)} {F(a[0])} {F(a[1])} Z")
        o.append(paint(f"{u}-f{k}", d, (a[0] - 2, min(a[1], b[1]) - 2, b[0] + 2, tip[1] + 2), base, 90 + k, angle=-90, n=26, length=(6, 18), width=(0.5, 1.6),
                       ink_col=dk(base, 0.5), ink_w=1.3))
        clip = f'<clipPath id="{u}-c{k}"><path d="{d}"/></clipPath>'
        if pat == "stripes":
            o.append(clip + f'<g clip-path="url(#{u}-c{k})" stroke="{pc}" stroke-width="3.4" opacity="0.9">' + "".join(f'<path d="M {F(a[0] - 4)} {F(a[1] + 8 + i * 9)} L {F(b[0] + 4)} {F(b[1] + 8 + i * 9)}"/>' for i in range(4)) + "</g>")
        elif pat == "dots":
            o.append(clip + f'<g clip-path="url(#{u}-c{k})" fill="{pc}" opacity="0.9">' + "".join(
                f'<circle cx="{F(x + (i - 2) * 9 + (j % 2) * 4.5)}" cy="{F((a[1] + b[1]) / 2 + 6 + j * 8)}" r="2"/>' for i in range(5) for j in range(4)) + "</g>")
        elif pat == "zig":
            zz = "M " + " L ".join(f"{F(a[0] - 4 + i * 5)} {F((a[1] + b[1]) / 2 + 14 + (i % 2) * 5)}" for i in range(11))
            o.append(clip + f'<g clip-path="url(#{u}-c{k})"><path d="{zz}" stroke="{pc}" stroke-width="2.6" fill="none"/></g>')
        else:
            sx, sy = x, (a[1] + b[1]) / 2 + 13
            o.append(f'<circle cx="{F(sx)}" cy="{F(sy)}" r="5" fill="{pc}"/>' + "".join(
                f'<path d="M {F(sx + math.cos(math.radians(t)) * 7)} {F(sy + math.sin(math.radians(t)) * 7)} l {F(math.cos(math.radians(t)) * 3)} {F(math.sin(math.radians(t)) * 3)}" stroke="{pc}" stroke-width="1.6" stroke-linecap="round"/>' for t in range(0, 360, 45)))
        o.append(f'<path d="{poly([(a[0] + 6, a[1] + 4), (b[0] - 6, b[1] + 4), (tip[0], tip[1] - 9)])}" fill="none" stroke="#FFFFFF" stroke-width="0.9" stroke-dasharray="2.4 2" opacity="0.7" stroke-linejoin="round"/>')
    return "".join(o)


# ================================================================ THANKSGIVING
def ell_d(cx, cy, rx, ry, deg):
    """A rotated ellipse as compact path data (two arcs)."""
    a = math.radians(deg)
    dx, dy = rx * math.cos(a), rx * math.sin(a)
    return (f"M{F(cx - dx)} {F(cy - dy)}a{F(rx)} {F(ry)} {F(deg)} 1 0 {F(2 * dx)} {F(2 * dy)}"
            f"a{F(rx)} {F(ry)} {F(deg)} 1 0 {F(-2 * dx)} {F(-2 * dy)}z")


def wheat(x, y, ang, L, seed, col="#D9A84E", w=1.0):
    """A stalk of wheat from (x, y) pointing ang degrees (-90 = up), L long; grain head on the outer 40%."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bend = rnd.uniform(-0.06, 0.06) * L
    tip = (x + ux * L + nx * bend, y + uy * L + ny * bend)
    o = [f'<path d="M {F(x)} {F(y)} Q {F(x + ux * L * 0.5 + nx * bend * 0.3)} {F(y + uy * L * 0.5 + ny * bend * 0.3)} {F(tip[0])} {F(tip[1])}" '
         f'stroke="{dk(col, 0.3)}" stroke-width="{F(1.4 * w)}" fill="none" stroke-linecap="round"/>']
    kern, awns = [], []
    n = 6
    for i in range(n):
        t = 0.6 + 0.38 * i / (n - 1)
        px, py = x + ux * L * t + nx * bend * t * t, y + uy * L * t + ny * bend * t * t
        k = (1 - 0.35 * i / n) * w
        for sg in (-1, 1):
            ka = ang + sg * 28
            kx, ky = px + nx * sg * 2.2 * k, py + ny * sg * 2.2 * k
            kern.append(ell_d(kx, ky, 3.6 * k, 1.9 * k, ka))
            aa = math.radians(ka)
            ex, ey = kx + math.cos(aa) * 3.4 * k, ky + math.sin(aa) * 3.4 * k
            awns.append(f"M {F(ex)} {F(ey)} l {F(math.cos(aa) * 9 * k)} {F(math.sin(aa) * 9 * k)}")
    kx, ky = tip
    kern.append(ell_d(kx, ky, 3.4 * w, 1.8 * w, ang))
    o.append(f'<path d="{" ".join(awns)}" stroke="{lt(col, 0.2)}" stroke-width="{F(0.6 * w)}" fill="none" stroke-linecap="round" opacity="0.9"/>')
    o.append(f'<path d="{"".join(kern)}" fill="{col}" stroke="{dk(col, 0.42)}" stroke-width="{F(0.7 * w)}"/>')
    return "".join(o)


def wheat_bundle(x, y, seed, s=1.0, ribbon="#B8532E", spread=40, L=46, n=5, base=-90):
    """Sheaf of wheat stalks fanning up from a tie at (x, y)."""
    o = []
    for i in range(n):
        ang = base - spread / 2 + spread * i / (n - 1)
        bx, by = x - math.cos(math.radians(ang)) * 16 * s, y - math.sin(math.radians(ang)) * 16 * s
        o.append(wheat(bx, by, ang, (L + (6 if i == n // 2 else 0)) * s, seed + i, col=("#D9A84E", "#E6BC62", "#C9933A")[i % 3], w=s))
    o.append(f'<path d="M {F(x - 5 * s)} {F(y - 1 * s)} Q {F(x)} {F(y + 2 * s)} {F(x + 5 * s)} {F(y - 1 * s)}" stroke="{ribbon}" stroke-width="{F(3.2 * s)}" fill="none" stroke-linecap="round"/>')
    for sg in (-1, 1):
        o.append(f'<path d="{blob(x + sg * 5 * s, y - 1 * s, 4.6 * s, 2.8 * s, seed + sg, 0.08, 10, rot=sg * 20)}" fill="{ribbon}" stroke="{dk(ribbon, 0.4)}" stroke-width="0.7"/>')
        o.append(f'<path d="M {F(x)} {F(y)} q {F(sg * 3 * s)} {F(6 * s)} {F(sg * 5 * s)} {F(11 * s)}" stroke="{ribbon}" stroke-width="{F(2.2 * s)}" fill="none" stroke-linecap="round"/>')
    o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(2.4 * s)}" fill="{dk(ribbon, 0.15)}"/>')
    return "".join(o)


def apple(uid, cx, cy, r, col, seed, leafy=True, rot_=0):
    pts = [(0, -0.72), (0.4, -0.95), (0.88, -0.62), (1.0, -0.05), (0.78, 0.62), (0.32, 0.92), (0, 0.84), (-0.32, 0.92), (-0.78, 0.62), (-1.0, -0.05),
           (-0.88, -0.62), (-0.4, -0.95)]
    pts = [rot(cx + x * r, cy + y * r, cx, cy, rot_) for x, y in jitter(pts, seed, 0.03)]
    d = smooth_closed(pts)
    o = [paint(uid, d, bbox(pts), col, seed, tints=[lt(col, 0.25), dk(col, 0.25), "#F6C24E"], angle=-90 + rot_, n=int(r * 1.6), ink_col=inkc(col), ink_w=max(0.9, r * 0.08),
               length=(r * 0.3, r * 0.9), width=(0.4, max(0.8, r * 0.07)), curve=0.4)]
    o.append(shade(uid + "-s", d, dk(col, 0.4), 0.6, 0.7, k=r * 0.25, op=0.4))
    hx, hy = rot(cx - 0.45 * r, cy - 0.3 * r, cx, cy, rot_)
    o.append(f'<ellipse cx="{F(hx)}" cy="{F(hy)}" rx="{F(0.13 * r)}" ry="{F(0.28 * r)}" fill="#FFFFFF" opacity="0.6" transform="rotate({F(20 + rot_)} {F(hx)} {F(hy)})"/>')
    sx, sy = rot(cx, cy - 0.75 * r, cx, cy, rot_)
    tx, ty = rot(cx + 0.12 * r, cy - 1.2 * r, cx, cy, rot_)
    o.append(f'<path d="M {F(sx)} {F(sy)} Q {F(sx - 0.05 * r)} {F((sy + ty) / 2)} {F(tx)} {F(ty)}" stroke="#5A3A1E" stroke-width="{F(max(1, r * 0.1))}" fill="none" stroke-linecap="round"/>')
    if leafy:
        o.append(leaf(uid + "-lf", (sx + tx) / 2, (sy + ty) / 2, r * 0.75, r * 0.26, -20 + rot_, "#6E8A3E", seed))
    return "".join(o)


def grapes(cx, cy, s, col="#6E3E7E", seed=1):
    rnd = random.Random(seed)
    rows = [5, 4, 4, 3, 2, 1]
    o = [f'<path d="M {F(cx)} {F(cy - 4 * s)} q {F(2 * s)} {F(-6 * s)} {F(6 * s)} {F(-8 * s)}" stroke="#5A3A1E" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round"/>']
    o.append(leaf("gl" + str(seed), cx + 3 * s, cy - 8 * s, 14 * s, 6 * s, -150, "#6E8A3E", seed))
    for j, n in enumerate(rows):
        for i in range(n):
            x = cx + (i - (n - 1) / 2) * 5.6 * s + rnd.uniform(-0.6, 0.6)
            y = cy + j * 4.8 * s + rnd.uniform(-0.6, 0.6)
            c = mix(col, "#9A6AB0", rnd.uniform(0, 0.4))
            o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(3.3 * s)}" fill="{c}" stroke="{dk(col, 0.45)}" stroke-width="0.7"/>'
                     f'<circle cx="{F(x - 1 * s)}" cy="{F(y - 1.1 * s)}" r="{F(0.9 * s)}" fill="#FFFFFF" opacity="0.55"/>')
    return "".join(o)


def corn_ear(uid, x, y, L, ang, seed):
    """Ear of corn lying at angle ang (deg), base at (x, y), husks peeled back at the base."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    def P(t, o_):
        return (x + ux * L * t + nx * o_, y + uy * L * t + ny * o_)
    w = L * 0.17
    pts = [P(0.02, -w * 0.8), P(0.35, -w), P(0.75, -w * 0.8), P(1.0, 0), P(0.75, w * 0.8), P(0.35, w), P(0.02, w * 0.8)]
    d = smooth_closed(pts)
    o = [f'<path d="{d}" fill="#F2C14E"/>']
    dots = []
    for i in range(9):
        t = 0.08 + i * 0.1
        for j in (-2, -1, 0, 1, 2):
            wf = w * (1 - abs(t - 0.4) * 0.5)
            px, py = P(t + (j % 2) * 0.04, j * wf * 0.36)
            if abs(j) * 0.36 < 0.9:
                dots.append(f'<ellipse cx="{F(px)}" cy="{F(py)}" rx="{F(L * 0.04)}" ry="{F(w * 0.15)}" transform="rotate({F(ang)} {F(px)} {F(py)})"/>')
    o.append(f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})"><g fill="#F8DA7A" stroke="#C9922A" stroke-width="0.5">{"".join(dots)}</g></g>')
    o.append(shade(uid + "-s", d, "#B8862E", nx, ny, k=w * 0.4, op=0.45))
    o.append(ink(d, "#8A5E12", 1.0, seed, 1, 0.6))
    for sg, c in ((-1, "#D9C08A"), (1, "#C9AE72"), (0, "#E6D29E")):
        hp = [P(0, 0), P(0.25, sg * w * 1.6 + w * 0.3 * (sg == 0)), P(0.5, sg * w * 1.3), P(0.32, sg * w * 0.4), P(0.08, sg * w * 0.2)]
        hd = smooth_closed(hp)
        o.append(f'<path d="{hd}" fill="{c}"/>' + ink(hd, "#8A6A3A", 0.9, seed + sg, 1, 0.6)
                 + f'<path d="M {F(P(0.04, 0)[0])} {F(P(0.04, 0)[1])} Q {F(P(0.25, sg * w)[0])} {F(P(0.25, sg * w)[1])} {F(P(0.42, sg * w * 1.2)[0])} {F(P(0.42, sg * w * 1.2)[1])}" stroke="#A88A52" stroke-width="0.7" fill="none"/>')
    return "".join(o)


TK_FEATHERS = ["#8A4A26", "#C2642E", "#E2A23A", "#A8562A", "#D98A3A", "#7A4426"]


def turkey(u, cx, base, s=1.0, seed=101):
    """Friendly storybook turkey facing us, tail fanned out behind."""
    def p(x, y):
        return (cx + x * s, base + y * s)
    o = [shadow(cx, base, 52 * s, 6 * s, 0.16)]
    tcx, tcy = p(0, -62)
    for row, (R, W, cols) in enumerate(((100 * s, 22 * s, TK_FEATHERS), (80 * s, 19 * s, TK_FEATHERS[2:] + TK_FEATHERS[:2]))):
        n = 9 if row == 0 else 8
        for i in range(n):
            ang = -168 + 156 * i / (n - 1) if row == 0 else -160 + 140 * i / (n - 1)
            a = math.radians(ang)
            ux, uy = math.cos(a), math.sin(a)
            nx, ny = -uy, ux
            pts = [(tcx + ux * R * t + nx * W * k, tcy + uy * R * t + ny * W * k) for t, k in
                   ((0.15, 0.12), (0.55, 0.46), (0.86, 0.52), (1.0, 0.3), (1.04, 0), (1.0, -0.3), (0.86, -0.52), (0.55, -0.46), (0.15, -0.12))]
            d = smooth_closed(pts)
            col = cols[i % len(cols)]
            o.append(paint(f"{u}-f{row}{i}", d, bbox(pts), col, seed + row * 10 + i, tints=[lt(col, 0.25), dk(col, 0.25), lt(col, 0.4)], angle=ang, n=int(R * 0.1),
                           ink_col=dk(col, 0.55), ink_w=1.1 * s, length=(R * 0.08, R * 0.25), width=(0.4, 1.1 * s), curve=0.15))
            # banded tip + quill
            tip = smooth_open([(tcx + ux * R * 0.8 + nx * W * 0.5, tcy + uy * R * 0.8 + ny * W * 0.5), (tcx + ux * R * 0.88, tcy + uy * R * 0.88),
                               (tcx + ux * R * 0.8 - nx * W * 0.5, tcy + uy * R * 0.8 - ny * W * 0.5)])
            o.append(f'<path d="{tip}" stroke="{lt(col, 0.55)}" stroke-width="{F(2.6 * s)}" fill="none" stroke-linecap="round" opacity="0.85"/>')
            o.append(f'<path d="M {F(tcx + ux * R * 0.2)} {F(tcy + uy * R * 0.2)} L {F(tcx + ux * R * 0.95)} {F(tcy + uy * R * 0.95)}" stroke="{dk(col, 0.4)}" stroke-width="{F(0.9 * s)}" opacity="0.7"/>')
    # legs
    for sg in (-1, 1):
        lx, ly = p(sg * 12, -16)
        fx, fy = p(sg * 14, 0)
        o.append(f'<path d="M {F(lx)} {F(ly)} L {F(fx)} {F(fy - 2 * s)} M {F(fx)} {F(fy - 2 * s)} l {F(-7 * s)} {F(2 * s)} M {F(fx)} {F(fy - 2 * s)} l {F(1 * s)} {F(3 * s)} '
                 f'M {F(fx)} {F(fy - 2 * s)} l {F(7 * s)} {F(2 * s)}" stroke="#D9822E" stroke-width="{F(3 * s)}" stroke-linecap="round" fill="none"/>')
    # body
    bpts = [p(-36, -54), p(-28, -84), p(0, -96), p(28, -84), p(36, -54), p(26, -22), p(0, -12), p(-26, -22)]
    bd = smooth_closed(bpts)
    o.append(paint(u + "-b", bd, bbox(bpts), "#7A4A2A", seed, tints=["#9A6238", "#5A3218", "#A8703E"], angle=-90, n=44, ink_col="#3A2010", ink_w=1.6 * s,
                   length=(5 * s, 14 * s), width=(0.5, 1.5 * s)))
    # chest scallops
    sc = []
    for j, y in enumerate((-70, -58, -46, -34)):
        n = 4 - (j == 3)
        for i in range(n):
            x = (i - (n - 1) / 2) * 11
            sc.append(f"M {F(p(x - 5.5, y)[0])} {F(p(x, y)[1])} Q {F(p(x, y + 7)[0])} {F(p(x, y + 7)[1])} {F(p(x + 5.5, y)[0])} {F(p(x, y)[1])}")
    o.append(f'<path d="{" ".join(sc)}" stroke="#C99A62" stroke-width="{F(1.4 * s)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    for sg in (-1, 1):
        wpts = [p(sg * 26, -78), p(sg * 40, -60), p(sg * 38, -36), p(sg * 28, -28), p(sg * 22, -52)]
        wd = smooth_closed(wpts)
        o.append(paint(f"{u}-w{sg}", wd, bbox(wpts), "#5E3A20", seed + 40 + sg, tints=["#7A4E2C", "#3E2410"], angle=-80, n=16, ink_col="#2E1A0C", ink_w=1.2 * s))
        o.append(f'<path d="{smooth_open([p(sg * 30, -60), p(sg * 34, -46), p(sg * 30, -34)])}" stroke="#A8703E" stroke-width="{F(1.1 * s)}" fill="none" opacity="0.8"/>')
    # neck + head
    hpts = [p(-15, -96), p(-17, -112), p(-12, -128), p(0, -134), p(12, -128), p(17, -112), p(15, -96), p(0, -90)]
    hd = smooth_closed(hpts)
    o.append(paint(u + "-h", hd, bbox(hpts), "#B07A4A", seed + 50, tints=["#C99062", "#8A5A32"], angle=-90, n=18, ink_col="#3A2010", ink_w=1.4 * s))
    for sg in (-1, 1):
        ex, ey = p(sg * 6.5, -118)
        o.append(f'<ellipse cx="{F(ex)}" cy="{F(ey)}" rx="{F(4.4 * s)}" ry="{F(5 * s)}" fill="#FFFDF6" stroke="#3A2010" stroke-width="0.9"/>'
                 f'<circle cx="{F(ex + sg * 0.6 * s)}" cy="{F(ey + 0.8 * s)}" r="{F(2.6 * s)}" fill="#1E140C"/><circle cx="{F(ex + sg * 0.6 * s - 0.9 * s)}" cy="{F(ey - 0.3 * s)}" r="{F(0.9 * s)}" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{F(p(sg * 11, -106)[0])}" cy="{F(p(sg * 11, -106)[1])}" r="{F(3.4 * s)}" fill="#F08A6A" opacity="0.5"/>')
    # wattle, beak
    wat = smooth_closed([p(1, -110), p(6, -104), p(7, -94), p(4, -88), p(1, -94)])
    o.append(f'<path d="{wat}" fill="#D2363A" stroke="#7A1418" stroke-width="0.9"/>')
    o.append(f'<path d="{smooth_closed([p(-5, -111), p(5, -111), p(0, -103)])}" fill="#F2A23A" stroke="#9A5A12" stroke-width="0.9" stroke-linejoin="round"/>')
    # a little pilgrim-ish hat? keep it simple: a tuft of head feathers
    o.append(f'<path d="M {F(p(-2, -133)[0])} {F(p(-2, -133)[1])} q {F(-4 * s)} {F(-8 * s)} {F(-2 * s)} {F(-12 * s)} M {F(p(1, -134)[0])} {F(p(1, -134)[1])} q {F(2 * s)} {F(-8 * s)} {F(6 * s)} {F(-10 * s)}" stroke="#7A4A2A" stroke-width="{F(2 * s)}" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def cornucopia(u, mx, my, seed=121):
    """Woven horn lying on the ground, mouth (mx, my) facing left, tail curling up to the right."""
    cl = [(mx, my), (mx + 40, my + 2), (mx + 78, my - 4), (mx + 104, my - 22), (mx + 114, my - 46), (mx + 106, my - 62), (mx + 92, my - 64)]
    widths = [38, 32, 24, 16, 10, 6, 3]
    left, right = [], []
    for i, (x, y) in enumerate(cl):
        x0, y0 = cl[max(i - 1, 0)]
        x1, y1 = cl[min(i + 1, len(cl) - 1)]
        tx, ty = x1 - x0, y1 - y0
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        left.append((x + nx * widths[i], y + ny * widths[i]))
        right.append((x - nx * widths[i], y - ny * widths[i]))
    pts = left + right[::-1]
    d = smooth_closed(pts)
    o = [shadow(mx + 54, my + 36, 70, 6, 0.16)]
    o.append(paint(u, d, bbox(pts), "#C9933A", seed, tints=["#E2B65A", "#A8742A", "#F2D07A"], angle=0, n=50, ink_col="#6E4A1A", ink_w=1.6))
    # woven rings + diagonal weave
    rings = []
    for i in range(1, 22):
        t = i / 22 * (len(cl) - 1)
        k = int(t)
        f = t - k
        if k >= len(cl) - 1:
            break
        a = (left[k][0] + (left[k + 1][0] - left[k][0]) * f, left[k][1] + (left[k + 1][1] - left[k][1]) * f)
        b = (right[k][0] + (right[k + 1][0] - right[k][0]) * f, right[k][1] + (right[k + 1][1] - right[k][1]) * f)
        c = (cl[k][0] + (cl[k + 1][0] - cl[k][0]) * f + 3, cl[k][1] + (cl[k + 1][1] - cl[k][1]) * f)
        rings.append(f"M {F(a[0])} {F(a[1])} Q {F(c[0] + 4)} {F(c[1])} {F(b[0])} {F(b[1])}")
    o.append(f'<clipPath id="{u}-c"><path d="{d}"/></clipPath><g clip-path="url(#{u}-c)">'
             f'<path d="{" ".join(rings)}" stroke="#8A5E22" stroke-width="2.2" fill="none" opacity="0.65"/>'
             f'<path d="{" ".join(rings)}" stroke="#F6DA8A" stroke-width="0.9" fill="none" opacity="0.7" transform="translate(-2 0)"/>'
             + "".join(f'<path d="M {F(mx - 10 + i * 9)} {F(my - 70)} l 40 120" stroke="#A8742A" stroke-width="1" opacity="0.35"/>' for i in range(16))
             + "</g>")
    o.append(shade(u + "-s", d, "#6E4A1A", 0, 1, k=6, op=0.35))
    # curled tip
    o.append(f'<path d="M {F(cl[-1][0])} {F(cl[-1][1])} q -10 4 -8 12 q 3 6 9 2" stroke="#A8742A" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # mouth: dark inside, plaited rim
    mouth = blob(mx, my, 13, 38, seed, 0.02, 16)
    o.append(f'<path d="{mouth}" fill="#5A3818"/><path d="{blob(mx + 2, my + 2, 9, 32, seed + 1, 0.03, 14)}" fill="#3A2210"/>')
    o.append(f'<path d="{mouth}" fill="none" stroke="#E2B65A" stroke-width="6"/><path d="{mouth}" fill="none" stroke="#8A5E22" stroke-width="6" stroke-dasharray="3 3" opacity="0.6"/>')
    o.append(ink(mouth, "#6E4A1A", 1.2, seed, 1, 0.7))
    return "".join(o)


def thanksgiving_scene(u="tg"):
    o = [shadow(196, 318, 178, 10, 0.12)]
    o.append(glow(u + "-gl", 150, 180, 170, 150, "#F6C46A", 0.3))
    # tall wheat sheaves behind
    o.append(wheat_bundle(34, 296, 3, s=1.6, spread=34, L=118, n=5) + wheat_bundle(330, 274, 9, s=1.4, spread=30, L=96, n=4))
    o.append(turkey(u + "-tk", 150, 314, 1.32))
    o.append(cornucopia(u + "-cn", 250, 272))
    # produce spilling out of the horn
    o.append(grapes(240, 250, 1.15, seed=4))
    o.append(corn_ear(u + "-co", 238, 290, 62, 165, 3))
    o.append(painted_pumpkin(u + "-p1", 268, 302, 50, 32, 71, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF", stem="#6B5A2E"))
    o.append(apple(u + "-a1", 222, 304, 14, "#C8323A", 5))
    o.append(apple(u + "-a2", 300, 310, 12, "#D9A23A", 6, leafy=False, rot_=20))
    o.append(painted_pumpkin(u + "-p2", 62, 296, 74, 48, 72))
    o.append(painted_pumpkin(u + "-p3", 336, 306, 42, 28, 73, body="#7E9A4E", dark="#5A7432", light="#B8CC7A", stem="#6B5A2E"))
    o.append(apple(u + "-a3", 108, 312, 11, "#B8262E", 7, rot_=-15))
    o.append(maple_leaf(186, 318, 9, "#E8792E", "#B9531E", rot=-30, seed=5) + oak(20, 318, 8, "#B8862E", "#7A5418", rot=70)
             + maple_leaf(366, 318, 8, "#C9442E", "#8E2A1A", rot=24, seed=6))
    return "".join(o)


def thanksgiving_garland(u="tgg"):
    o = [twine()]
    items = [(34, "maple", "#E8792E", "#B9531E"), (80, "gourd", "#E8792E", None), (122, "oak", "#B8862E", "#7A5418"), (160, "wheat", None, None),
             (200, "gourd", "#F1E6D2", None), (240, "maple", "#C9442E", "#8E2A1A"), (284, "gourd", "#7E9A4E", None)]
    gcols = {"#E8792E": ("#E8792E", "#B9531E", "#F8A85A"), "#F1E6D2": ("#F1E6D2", "#C9B79A", "#FFFFFF"), "#7E9A4E": ("#7E9A4E", "#5A7432", "#B8CC7A")}
    for k, (x, kind, c, d) in enumerate(items):
        y = swag_y(x)
        if kind == "maple":
            o.append(f'<path d="M {x} {F(y)} l 0 8" stroke="#8A6A42" stroke-width="1"/>' + maple_leaf(x, y + 22, 14, c, d, rot=(-1) ** k * 12 + 180, seed=k))
        elif kind == "oak":
            o.append(f'<path d="M {x} {F(y)} l 0 6" stroke="#8A6A42" stroke-width="1"/>' + oak(x, y + 22, 14, c, d, rot=(-1) ** k * 10 + 180))
        elif kind == "wheat":
            o.append(wheat_bundle(x, y + 2, 21, s=0.62, spread=44, L=46, n=5, base=90, ribbon="#C9442E"))
        else:
            b, dd, li = gcols[c]
            o.append(f'<path d="M {x} {F(y)} l 0 9" stroke="#8A6A42" stroke-width="1"/>'
                     + painted_pumpkin(f"{u}-g{k}", x, y + 24, 24, 17, 80 + k, body=b, dark=dd, light=li, stem="#6B5A2E"))
    # wheat sheaf with a ribbon at the hanging point, drawn on both edges so the halves meet
    o.append(wheat_bundle(0, 12, 11, s=0.62, spread=60, L=44, n=5, base=90) + wheat_bundle(TW, 12, 11, s=0.62, spread=60, L=44, n=5, base=90))
    return "".join(o)


# ================================================================ NEW YEAR
GOLD = ("#E2B04A", "#F8DC8A", "#B07E22", "#7A5212")    # base, light, dark, ink
SILVER = ("#C4CAD4", "#F2F4F8", "#8A93A3", "#5A6272")
NAVY = "#2E3F6E"


def curl_ribbon(x, y, L, cols, turns=3.0, amp=4.0, w=4.2, seed=1):
    """Curling ribbon streamer hanging from (x, y): a helix seen from the side (front faces light, back faces dark)."""
    base, light, darkc, inkc_ = cols
    n = int(turns * 10)
    pts = []
    for i in range(n + 1):
        t = i / n
        ph = 2 * math.pi * turns * t
        pts.append((x + amp * math.sin(ph) * (0.6 + 0.4 * t), y + L * t, w * math.cos(ph) * (1 - 0.25 * t), math.cos(ph)))
    o = []
    for i in range(n):
        x0, y0, w0, c0 = pts[i]
        x1, y1, w1, c1 = pts[i + 1]
        col = light if (c0 + c1) > 0.6 else base if (c0 + c1) > -0.6 else darkc
        q = [(x0 - abs(w0) * 0.2, y0 - w0 * 0.5), (x1 - abs(w1) * 0.2, y1 - w1 * 0.5), (x1 + abs(w1) * 0.2, y1 + w1 * 0.5), (x0 + abs(w0) * 0.2, y0 + w0 * 0.5)]
        o.append(f'<path d="{poly(q)}" fill="{col}" stroke="{col}" stroke-width="0.6" stroke-linejoin="round"/>')
    edge = smooth_open([(px, py - pw * 0.5) for px, py, pw, _ in pts]) + " " + smooth_open([(px, py + pw * 0.5) for px, py, pw, _ in pts])
    o.append(f'<path d="{edge}" stroke="{inkc_}" stroke-width="0.6" fill="none" opacity="0.55"/>')
    return "".join(o)


def painted_star(uid, cx, cy, r, cols, seed, rot_=-90, inner=0.5, ink_w=1.2):
    base, light, darkc, inkc_ = cols
    sp = star_pts(cx, cy, r, inner, rot_)
    # soften the points a little so it looks cut from paper by hand
    d = smooth_closed(jitter(sp, seed, r * 0.03)).replace("C", "C", 1)
    d = poly(jitter(sp, seed, r * 0.03))
    o = [paint(uid, d, bbox(sp), base, seed, tints=[light, darkc, light], angle=rot_ + 90 + 60, n=int(r * 1.2), ink_col=inkc_, ink_w=ink_w,
               length=(r * 0.2, r * 0.7), width=(0.3, max(0.6, r * 0.06)), op=(0.3, 0.7))]
    # bevel: light on the upper-left facets
    facets = []
    for i in range(0, 10, 2):
        a = sp[i]
        b = sp[(i + 1) % 10]
        facets.append(f"M {F(cx)} {F(cy)} L {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])} Z")
    o.append(f'<path d="{" ".join(facets)}" fill="{light}" opacity="0.45"/>')
    o.append(f'<path d="{" ".join(f"M {F(cx)} {F(cy)} L {F(p[0])} {F(p[1])}" for p in sp[::2])}" stroke="{darkc}" stroke-width="{F(max(0.5, r * 0.04))}" opacity="0.6"/>')
    return "".join(o)


def twinkle(cx, cy, r, col="#FFF3C4", edge="#C99A2E"):
    d = (f"M {F(cx)} {F(cy - r)} Q {F(cx + r * 0.15)} {F(cy - r * 0.15)} {F(cx + r)} {F(cy)} Q {F(cx + r * 0.15)} {F(cy + r * 0.15)} {F(cx)} {F(cy + r)} "
         f"Q {F(cx - r * 0.15)} {F(cy + r * 0.15)} {F(cx - r)} {F(cy)} Q {F(cx - r * 0.15)} {F(cy - r * 0.15)} {F(cx)} {F(cy - r)} Z")
    return f'<path d="{d}" fill="{col}" stroke="{edge}" stroke-width="{F(max(0.5, r * 0.1))}" stroke-linejoin="round"/>'


CONFETTI = ["#E2B04A", "#C4CAD4", "#E8869A", "#3FA3B5", "#2E3F6E", "#F6C23E", "#B48ED6"]


def confetti(seed, box, n, avoid=()):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    o = []
    for _ in range(n):
        for _try in range(20):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if not any((x - ax) ** 2 / rx ** 2 + (y - ay) ** 2 / ry ** 2 < 1 for ax, ay, rx, ry in avoid):
                break
        c = rnd.choice(CONFETTI)
        e = dk(c, 0.45) if c != "#2E3F6E" else "#8A9AC8"
        kind = rnd.random()
        a = rnd.uniform(0, 180)
        if kind < 0.45:
            w, h = rnd.uniform(3, 5), rnd.uniform(5.5, 8)
            o.append(f'<rect x="{F(x - w / 2)}" y="{F(y - h / 2)}" width="{F(w)}" height="{F(h)}" rx="0.8" fill="{c}" stroke="{e}" stroke-width="0.6" transform="rotate({F(a)} {F(x)} {F(y)})"/>')
        elif kind < 0.7:
            o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(rnd.uniform(1.8, 2.8))}" fill="{c}" stroke="{e}" stroke-width="0.6"/>')
        else:
            L = rnd.uniform(7, 11)
            o.append(f'<path d="M {F(x)} {F(y)} q {F(L * 0.25)} {F(-L * 0.4)} {F(L * 0.5)} 0 t {F(L * 0.5)} 0" stroke="{e}" stroke-width="3" fill="none" stroke-linecap="round" transform="rotate({F(a)} {F(x)} {F(y)})"/>'
                     f'<path d="M {F(x)} {F(y)} q {F(L * 0.25)} {F(-L * 0.4)} {F(L * 0.5)} 0 t {F(L * 0.5)} 0" stroke="{c}" stroke-width="1.8" fill="none" stroke-linecap="round" transform="rotate({F(a)} {F(x)} {F(y)})"/>')
    return "".join(o)


def round_balloon(uid, cx, cy, r, col, seed, tie, rot_=0, light=None, inkcol=None):
    pts = [(0, -1.0), (0.62, -0.84), (0.96, -0.32), (0.9, 0.3), (0.55, 0.82), (0.12, 1.1), (0, 1.12), (-0.12, 1.1), (-0.55, 0.82), (-0.9, 0.3), (-0.96, -0.32), (-0.62, -0.84)]
    pts = [rot(cx + x * r, cy + y * r, cx, cy, rot_) for x, y in pts]
    d = smooth_closed(pts)
    tipx, tipy = rot(cx, cy + 1.12 * r, cx, cy, rot_)
    tx, ty = tie
    sp = [(tipx, tipy + 3)]
    for i in range(1, 7):
        t = i / 7
        sp.append((tipx + (tx - tipx) * t + (4 if i % 2 else -4) * (1 - t), tipy + 3 + (ty - tipy - 3) * t))
    sp.append((tx, ty))
    o = [f'<path d="{smooth_open(sp)}" stroke="#9A8A7A" stroke-width="1" fill="none"/>']
    o.append(paint(uid, d, bbox(pts), col, seed, tints=[light or lt(col, 0.3), dk(col, 0.25), lt(col, 0.45)], angle=-70 + rot_, n=int(r * 1.3), ink_col=inkcol or inkc(col),
                   ink_w=max(1, r * 0.05), length=(r * 0.3, r * 0.9), width=(0.4, max(0.8, r * 0.05)), curve=0.4))
    o.append(shade(uid + "-s", d, dk(col, 0.35), 0.6, 0.7, k=r * 0.2, op=0.4))
    hx, hy = rot(cx - 0.42 * r, cy - 0.45 * r, cx, cy, rot_)
    o.append(f'<ellipse cx="{F(hx)}" cy="{F(hy)}" rx="{F(0.14 * r)}" ry="{F(0.3 * r)}" fill="#FFFFFF" opacity="0.65" transform="rotate({F(35 + rot_)} {F(hx)} {F(hy)})"/>')
    o.append(f'<path d="M {F(tipx - 3.4)} {F(tipy + 4.5)} L {F(tipx)} {F(tipy - 1)} L {F(tipx + 3.4)} {F(tipy + 4.5)} Z" fill="{dk(col, 0.15)}" stroke="{inkcol or inkc(col)}" stroke-width="0.7" stroke-linejoin="round"/>')
    return "".join(o)


def flute(uid, bx, by, h, tilt, seed):
    """Champagne flute standing at (bx, by), h tall, rotated tilt degrees about its foot."""
    stem_h = h * 0.38
    top = by - h
    bw_top, bw_bot = h * 0.13, h * 0.035
    bowl = [(bx - bw_bot, by - stem_h), (bx - bw_top * 0.82, by - stem_h - (h - stem_h) * 0.45), (bx - bw_top, top), (bx + bw_top, top),
            (bx + bw_top * 0.82, by - stem_h - (h - stem_h) * 0.45), (bx + bw_bot, by - stem_h)]
    bd = smooth_closed(bowl[:3] + [(bx, top - 1)] + bowl[3:] + [(bx, by - stem_h + 4)])
    liq_top = top + (h - stem_h) * 0.22
    o = [f'<g transform="rotate({tilt} {F(bx)} {F(by)})">']
    o.append(f'<path d="{blob(bx, by, h * 0.13, h * 0.026, seed, 0.03, 12)}" fill="#FFFFFF" fill-opacity="0.35" stroke="#7E8A9E" stroke-width="1.2"/>')
    o.append(f'<path d="M {F(bx)} {F(by - 1)} L {F(bx)} {F(by - stem_h)}" stroke="#7E8A9E" stroke-width="3.6" stroke-linecap="round"/>'
             f'<path d="M {F(bx)} {F(by - 1)} L {F(bx)} {F(by - stem_h)}" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round"/>')
    o.append(f'<path d="{bd}" fill="#FFFFFF" fill-opacity="0.3"/>')
    # champagne
    o.append(f'<clipPath id="{uid}-c"><path d="{bd}"/></clipPath><g clip-path="url(#{uid}-c)">'
             f'<rect x="{F(bx - h * 0.2)}" y="{F(liq_top)}" width="{F(h * 0.4)}" height="{F(h)}" fill="#F2C65A"/>'
             f'<rect x="{F(bx + bw_top * 0.2)}" y="{F(liq_top)}" width="{F(h * 0.2)}" height="{F(h)}" fill="#D9A23A" opacity="0.7"/>'
             f'<ellipse cx="{F(bx)}" cy="{F(liq_top)}" rx="{F(bw_top * 1.1)}" ry="2.2" fill="#FFF0B8"/>')
    rnd = random.Random(seed)
    o.append("".join(f'<circle cx="{F(bx + rnd.uniform(-bw_top * 0.6, bw_top * 0.6) * (0.3 + 0.7 * t))}" cy="{F(by - stem_h - 6 - t * (by - stem_h - liq_top - 8))}" r="{F(rnd.uniform(0.7, 1.5))}" fill="none" stroke="#FFF6D6" stroke-width="0.7"/>'
                     for t in [rnd.random() for _ in range(14)]))
    o.append("</g>")
    o.append(ink(bd, "#7E8A9E", 1.4, seed, 2, 0.75))
    o.append(f'<path d="M {F(bx - bw_top * 0.6)} {F(top + 6)} Q {F(bx - bw_top * 0.75)} {F(by - stem_h - (h - stem_h) * 0.45)} {F(bx - bw_bot * 0.6)} {F(by - stem_h - 6)}" stroke="#FFFFFF" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.85"/>')
    o.append(f'<path d="M {F(bx - bw_top)} {F(top)} L {F(bx + bw_top)} {F(top)}" stroke="#E6ECF4" stroke-width="1.2" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def alarm_clock(u, cx, cy, r, seed=141):
    gb, gl, gd, gi = GOLD
    o = [shadow(cx, cy + r + 14, r * 0.95, 6, 0.18)]
    # legs, bells, hammer
    for sg in (-1, 1):
        lx = cx + sg * r * 0.62
        o.append(f'<path d="M {F(lx)} {F(cy + r * 0.7)} L {F(lx + sg * r * 0.2)} {F(cy + r + 10)}" stroke="{gi}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M {F(lx)} {F(cy + r * 0.7)} L {F(lx + sg * r * 0.2)} {F(cy + r + 10)}" stroke="{gb}" stroke-width="4.6" stroke-linecap="round"/>')
        bx, by = cx + sg * r * 0.62, cy - r * 0.9
        bell = f"M {F(bx - r * 0.34)} {F(by + r * 0.08)} Q {F(bx - r * 0.34)} {F(by - r * 0.36)} {F(bx)} {F(by - r * 0.36)} Q {F(bx + r * 0.34)} {F(by - r * 0.36)} {F(bx + r * 0.34)} {F(by + r * 0.08)} Q {F(bx)} {F(by + r * 0.02)} {F(bx - r * 0.34)} {F(by + r * 0.08)} Z"
        o.append(f'<g transform="rotate({sg * 32} {F(bx)} {F(by)})">' + paint(f"{u}-bl{sg}", bell, (bx - r * 0.4, by - r * 0.4, bx + r * 0.4, by + r * 0.12), gb, seed + sg,
                                                                            tints=[gl, gd], angle=-60, n=14, ink_col=gi, ink_w=1.3)
                 + f'<circle cx="{F(bx)}" cy="{F(by - r * 0.4)}" r="{F(r * 0.06)}" fill="{gd}"/></g>')
    o.append(f'<path d="M {F(cx)} {F(cy - r)} L {F(cx)} {F(cy - r * 1.22)}" stroke="{gi}" stroke-width="3.4" stroke-linecap="round"/>'
             f'<path d="M {F(cx - r * 0.12)} {F(cy - r * 1.24)} L {F(cx + r * 0.12)} {F(cy - r * 1.24)}" stroke="{gi}" stroke-width="5" stroke-linecap="round"/>')
    # ringing marks
    for sg in (-1, 1):
        x0 = cx + sg * r * 1.08
        o.append("".join(f'<path d="M {F(x0 + sg * k * 7)} {F(cy - r * 0.95 - k * 3)} q {F(sg * 5)} {F(8)} 0 {F(16)}" stroke="#E2A23A" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="{0.9 - k * 0.25:.2f}"/>' for k in range(3)))
    # body + face
    body = blob(cx, cy, r, r * 0.98, seed, 0.02, 20)
    o.append(paint(u + "-b", body, (cx - r, cy - r, cx + r, cy + r), gb, seed, tints=[gl, gd, "#FFF0B8"], angle=-60, n=50, ink_col=gi, ink_w=1.8,
                   length=(r * 0.1, r * 0.4), width=(0.5, 1.6)))
    o.append(shade(u + "-bs", body, gd, 0.6, 0.8, k=r * 0.14, op=0.5))
    face = blob(cx, cy, r * 0.78, r * 0.77, seed + 1, 0.015, 20)
    o.append(f'<path d="{face}" fill="#FFF8EA"/>' + shade(u + "-fs", face, "#D9C9A8", -0.6, -0.7, k=r * 0.08, op=0.6) + ink(face, gi, 1.4, seed, 1, 0.7))
    ticks = []
    for i in range(12):
        a = math.radians(i * 30 - 90)
        r0 = r * (0.6 if i % 3 else 0.54)
        if i == 0:
            continue
        ticks.append(f"M {F(cx + math.cos(a) * r0)} {F(cy + math.sin(a) * r0)} L {F(cx + math.cos(a) * r * 0.68)} {F(cy + math.sin(a) * r * 0.68)}")
    o.append(f'<path d="{" ".join(ticks)}" stroke="{NAVY}" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(f'<path d="{poly(star_pts(cx, cy - r * 0.6, r * 0.11, 0.45))}" fill="#E2B04A" stroke="{gi}" stroke-width="0.8" stroke-linejoin="round"/>')
    # both hands at twelve
    o.append(f'<path d="M {F(cx - r * 0.05)} {F(cy + r * 0.06)} L {F(cx)} {F(cy - r * 0.5)} L {F(cx + r * 0.05)} {F(cy + r * 0.06)} Z" fill="{NAVY}" stroke="{NAVY}" stroke-width="1" stroke-linejoin="round"/>')
    o.append(f'<path d="M {F(cx - r * 0.085)} {F(cy + r * 0.04)} L {F(cx)} {F(cy - r * 0.33)} L {F(cx + r * 0.085)} {F(cy + r * 0.04)} Z" fill="#1E2A4A"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 0.07)}" fill="{gb}" stroke="{gi}" stroke-width="1"/>')
    o.append(f'<path d="M {F(cx - r * 0.62)} {F(cy - r * 0.38)} A {F(r * 0.72)} {F(r * 0.72)} 0 0 1 {F(cx - r * 0.2)} {F(cy - r * 0.7)}" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.8"/>')
    return "".join(o)


def party_hat(uid, tipx, tipy, bx, by, w, seed):
    """Cone party hat lying with its tip at (tipx, tipy) and the middle of its opening at (bx, by)."""
    ang = math.atan2(by - tipy, bx - tipx)
    nx, ny = -math.sin(ang), math.cos(ang)
    a, b = (bx + nx * w / 2, by + ny * w / 2), (bx - nx * w / 2, by - ny * w / 2)
    d = f"M {F(tipx)} {F(tipy)} L {F(a[0])} {F(a[1])} Q {F(bx + math.cos(ang) * w * 0.18)} {F(by + math.sin(ang) * w * 0.18)} {F(b[0])} {F(b[1])} Z"
    o = [shadow((tipx + bx) / 2, max(tipy, by) + 6, abs(bx - tipx) * 0.6 + 6, 4, 0.16)]
    o.append(paint(uid, d, bbox([(tipx, tipy), a, b]), NAVY, seed, tints=["#4A5E92", "#1E2A4A"], angle=math.degrees(ang), n=20, ink_col="#141C34", ink_w=1.3))
    # gold stripes + dots
    L = math.hypot(bx - tipx, by - tipy)
    o.append(f'<clipPath id="{uid}-c"><path d="{d}"/></clipPath><g clip-path="url(#{uid}-c)">'
             + "".join(f'<path d="M {F(tipx + math.cos(ang) * L * t + nx * w)} {F(tipy + math.sin(ang) * L * t + ny * w)} L {F(tipx + math.cos(ang) * L * (t + 0.12) - nx * w)} {F(tipy + math.sin(ang) * L * (t + 0.12) - ny * w)}" stroke="#E2B04A" stroke-width="3.4"/>'
                       for t in (0.18, 0.42, 0.66, 0.9)) + "</g>")
    o.append(f'<path d="M {F(a[0])} {F(a[1])} Q {F(bx + math.cos(ang) * w * 0.18)} {F(by + math.sin(ang) * w * 0.18)} {F(b[0])} {F(b[1])}" stroke="#C4CAD4" stroke-width="3.6" fill="none" stroke-linecap="round"/>')
    pom = blob(tipx, tipy, 6, 5.5, seed, 0.15, 12)
    o.append(f'<path d="{pom}" fill="#F8DC8A" stroke="#B07E22" stroke-width="0.9"/>'
             + "".join(f'<path d="M {F(tipx)} {F(tipy)} l {F(math.cos(t) * 7)} {F(math.sin(t) * 7)}" stroke="#E2B04A" stroke-width="1.2" stroke-linecap="round"/>' for t in [i * 0.9 for i in range(7)]))
    return "".join(o)


def newyear_scene(u="ny"):
    o = [shadow(200, 318, 170, 9, 0.12)]
    o.append(glow(u + "-gl", 200, 180, 170, 150, "#FFE6A0", 0.32))
    tie = (70, 300)
    o.append(round_balloon(u + "-b1", 66, 92, 30, NAVY, 1, tie, rot_=-10, light="#5A6E9E", inkcol="#141C34"))
    o.append(rim(u + "-b1r", smooth_closed([rot(66 + x * 30, 92 + y * 30, 66, 92, -10) for x, y in [(0, -1.0), (0.62, -0.84), (0.96, -0.32), (0.9, 0.3), (0.55, 0.82), (0.12, 1.1), (0, 1.12), (-0.12, 1.1), (-0.55, 0.82), (-0.9, 0.3), (-0.96, -0.32), (-0.62, -0.84)]]),
                 "#9AAEDC", -1, -0.6, k=1.6, op=0.7))
    o.append(round_balloon(u + "-b2", 122, 58, 27, GOLD[0], 2, tie, rot_=8, light=GOLD[1], inkcol=GOLD[3]))
    o.append(round_balloon(u + "-b3", 40, 160, 24, SILVER[0], 3, tie, rot_=-18, light=SILVER[1], inkcol=SILVER[3]))
    o.append(round_balloon(u + "-b4", 110, 138, 22, "#E8869A", 4, tie, rot_=12))
    o.append(f'<path d="{blob(70, 304, 8, 6, 5, 0.06, 10)}" fill="#E2B04A" stroke="#7A5212" stroke-width="1"/><path d="M 64 300 q 6 -6 12 0" stroke="#7A5212" stroke-width="1" fill="none"/>')
    o.append(alarm_clock(u + "-ck", 184, 236, 56))
    o.append(party_hat(u + "-ph", 102, 290, 128, 316, 30, 7))
    o.append(flute(u + "-f1", 266, 312, 146, 9, 11))
    o.append(flute(u + "-f2", 356, 312, 146, -9, 12))
    # clink: splash and sparkles where the rims meet
    sx, sy = 311, 158
    o.append("".join(f'<path d="M {F(sx + math.cos(math.radians(a)) * 10)} {F(sy + math.sin(math.radians(a)) * 10)} l {F(math.cos(math.radians(a)) * 9)} {F(math.sin(math.radians(a)) * 9)}" stroke="#E2A23A" stroke-width="2" stroke-linecap="round"/>' for a in (-150, -120, -90, -60, -30)))
    o.append("".join(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="#F8DC8A" stroke="#B07E22" stroke-width="0.6"/>' for x, y, r in ((302, 146, 2.4), (318, 140, 2), (326, 152, 1.6), (310, 136, 1.4))))
    o.append(twinkle(258, 104, 8) + twinkle(354, 120, 6) + twinkle(234, 150, 5, "#FFFFFF", "#8A93A3") + twinkle(160, 120, 6))
    o.append(confetti(8, (10, 20, 370, 312), 46, avoid=((66, 92, 34, 40), (122, 58, 30, 36), (40, 160, 26, 32), (110, 138, 24, 30), (184, 236, 70, 80), (312, 236, 60, 90))))
    return "".join(o)


def newyear_garland(u="nyg"):
    o = []
    d = "M 0 10 C 80 34 240 34 320 10"
    o.append(f'<path d="{d}" stroke="#7A5212" stroke-width="4.2" fill="none"/><path d="{d}" stroke="#E2B04A" stroke-width="3" fill="none"/>'
             f'<path d="{d}" stroke="#E6EAF0" stroke-width="3" fill="none" stroke-dasharray="5 5"/>'
             f'<path d="{d}" stroke="#FFFFFF" stroke-width="0.8" fill="none" stroke-dasharray="2 8" transform="translate(0 -0.8)"/>')
    # tinsel sparkle ticks along the rope
    rnd = random.Random(3)
    ticks = []
    for _ in range(70):
        x = rnd.uniform(0, TW)
        y = swag_y(x)
        a = rnd.uniform(0, 2 * math.pi)
        for sh in (0, TW, -TW):
            if -8 < x + sh < TW + 8:
                ticks.append(f"M {F(x + sh)} {F(y)} l {F(math.cos(a) * 4)} {F(math.sin(a) * 4)}")
    o.append(f'<path d="{" ".join(ticks)}" stroke="#F8DC8A" stroke-width="1" stroke-linecap="round" opacity="0.9"/>')
    for k in range(8):
        x = 20 + 40 * k
        y = swag_y(x) + 1
        if k % 2 == 0:
            cols = GOLD if k % 4 == 0 else SILVER
            o.append(curl_ribbon(x, y, 38 + (k % 3) * 4, cols, turns=3, amp=3.4, w=4.4, seed=k))
        else:
            cols = SILVER if k % 4 == 1 else GOLD
            L = 8 + (k % 3) * 4
            o.append(f'<path d="M {x} {F(y)} l 0 {L}" stroke="#8A93A3" stroke-width="0.9"/>')
            o.append(painted_star(f"{u}-s{k}", x, y + L + 9, 10, cols, 20 + k, rot_=-90 + (k % 3 - 1) * 8))
    for x, y, r in ((40, 52, 3.4), (120, 60, 4), (200, 58, 3.4), (282, 50, 4)):
        o.append(twinkle(x, y, r))
    return "".join(o)


def particles_confetti():
    save("confetti1", 40, 40, curl_ribbon(20, 4, 32, GOLD, turns=2.5, amp=3.6, w=5, seed=1))
    save("confetti2", 40, 40, '<rect x="9" y="11" width="9" height="14" rx="1.4" fill="#E8869A" stroke="#9A3A4E" stroke-width="0.9" transform="rotate(-24 13 18)"/>'
                              '<rect x="21" y="17" width="8" height="13" rx="1.4" fill="#3FA3B5" stroke="#1E5A66" stroke-width="0.9" transform="rotate(18 25 23)"/>'
                              '<circle cx="28" cy="10" r="3.4" fill="#C4CAD4" stroke="#5A6272" stroke-width="0.8"/>')
    save("confetti3", 40, 40, painted_star("pc3", 20, 21, 15, GOLD, 3) + twinkle(33, 8, 4.5, "#FFFFFF", "#8A93A3"))


# ================================================================ ST PATRICK'S
SHAM = ("#3E9A4E", "#6CC070", "#24703A", "#1E4A2A")     # base, light, dark, ink
SHAM2 = ("#5DB35A", "#8ED27E", "#3A8A3E", "#244E26")


def shamrock(uid, cx, cy, s, cols, seed, rot_=0, four=False, stem=True):
    """Painted shamrock: three (or four) heart-shaped leaves round a centre, with a curved stem."""
    base, light, darkc, inkc_ = cols
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    if stem:
        o.append(f'<path d="M {F(cx)} {F(cy + s * 0.1)} Q {F(cx + s * 0.1)} {F(cy + s * 0.7)} {F(cx + s * 0.38)} {F(cy + s * 1.05)}" stroke="{inkc_}" stroke-width="{F(max(1.6, s * 0.17))}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M {F(cx)} {F(cy + s * 0.1)} Q {F(cx + s * 0.1)} {F(cy + s * 0.7)} {F(cx + s * 0.38)} {F(cy + s * 1.05)}" stroke="{darkc}" stroke-width="{F(max(0.9, s * 0.1))}" fill="none" stroke-linecap="round"/>')
    angs = (-90, 0, 90, 180) if four else (-90, 30, 150)
    for k, a in enumerate(angs):
        rr = math.radians(a)
        lx, ly = cx + math.cos(rr) * s * 0.5, cy + math.sin(rr) * s * 0.5
        d = heart_d(lx, ly, s * 0.5, a + 90)
        box = (lx - s * 0.6, ly - s * 0.6, lx + s * 0.6, ly + s * 0.6)
        o.append(paint(f"{uid}-{k}", d, box, base, seed + k, tints=[light, darkc, light], angle=a, n=int(max(6, s * 0.9)), ink_col=inkc_, ink_w=max(0.8, s * 0.06),
                       length=(s * 0.12, s * 0.4), width=(0.3, max(0.6, s * 0.04)), op=(0.25, 0.55)))
        o.append(f'<path d="M {F(cx)} {F(cy)} L {F(cx + math.cos(rr) * s * 0.72)} {F(cy + math.sin(rr) * s * 0.72)}" stroke="{light}" stroke-width="{F(max(0.6, s * 0.05))}" opacity="0.8" stroke-linecap="round"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(s * 0.08)}" fill="{darkc}"/>')
    o.append("</g>")
    return "".join(o)


def coin(cx, cy, r, seed=1, tilt=0.0, mark=True):
    """Gold coin; tilt 0 = facing us, 1 = seen edge-on (squashed vertically)."""
    ry = r * (1 - 0.72 * tilt)
    o = []
    if tilt > 0.05:
        o.append(f'<ellipse cx="{F(cx)}" cy="{F(cy + r * 0.16 * tilt + 0.6)}" rx="{F(r)}" ry="{F(ry)}" fill="#A8741A" stroke="#6E4A0E" stroke-width="0.8"/>')
    o.append(f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(r)}" ry="{F(ry)}" fill="#F2C14E" stroke="#8A5E12" stroke-width="{F(max(0.7, r * 0.09))}"/>')
    o.append(f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(r * 0.74)}" ry="{F(ry * 0.74)}" fill="none" stroke="#C9922A" stroke-width="{F(max(0.5, r * 0.08))}"/>')
    o.append(f'<path d="M {F(cx - r * 0.55)} {F(cy - ry * 0.3)} A {F(r * 0.6)} {F(ry * 0.6)} 0 0 1 {F(cx - r * 0.05)} {F(cy - ry * 0.62)}" stroke="#FFF3C4" stroke-width="{F(max(0.6, r * 0.12))}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    if mark and r > 5:
        sx = r * 0.17
        o.append(f'<g fill="#C9922A" transform="translate({F(cx)} {F(cy)}) scale(1 {F(ry / r)})">'
                 + "".join(f'<circle cx="{F(math.cos(math.radians(a)) * sx)}" cy="{F(math.sin(math.radians(a)) * sx)}" r="{F(sx * 0.95)}"/>' for a in (-90, 30, 150)) + "</g>")
    return "".join(o)


def rainbow(u, cx, cy, R, bw, a0, a1, seed=1):
    """Painted rainbow arc centred at (cx, cy), outer radius R, band width bw, from angle a0 to a1 (deg, screen coords)."""
    cols = ["#E8604C", "#F2944A", "#F6C94E", "#7CB860", "#4E9AD0", "#8A6AC0"]
    rnd = random.Random(seed)
    o = []
    for i, c in enumerate(cols):
        r = R - bw * (i + 0.5)
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        d = f"M {F(p0[0])} {F(p0[1])} A {F(r)} {F(r)} 0 0 1 {F(p1[0])} {F(p1[1])}"
        o.append(f'<path d="{d}" stroke="{c}" stroke-width="{F(bw + 0.6)}" fill="none" opacity="0.92"/>')
        # dry-brush streaks running along the band
        for j in range(3):
            off = rnd.uniform(-bw * 0.32, bw * 0.32)
            rr = r + off
            q0 = (cx + rr * math.cos(math.radians(a0)), cy + rr * math.sin(math.radians(a0)))
            q1 = (cx + rr * math.cos(math.radians(a1)), cy + rr * math.sin(math.radians(a1)))
            dash = f"{rnd.uniform(14, 40):.0f} {rnd.uniform(6, 20):.0f} {rnd.uniform(8, 30):.0f} {rnd.uniform(4, 14):.0f}"
            o.append(f'<path d="M {F(q0[0])} {F(q0[1])} A {F(rr)} {F(rr)} 0 0 1 {F(q1[0])} {F(q1[1])}" stroke="{(lt(c, 0.35), dk(c, 0.15), lt(c, 0.2))[j]}" '
                     f'stroke-width="{F(rnd.uniform(0.8, 1.8))}" fill="none" stroke-dasharray="{dash}" stroke-dashoffset="{rnd.uniform(0, 40):.0f}" stroke-linecap="round" opacity="0.8"/>')
    # soft inked edges
    for r in (R, R - bw * len(cols)):
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        o.append(f'<path d="M {F(p0[0])} {F(p0[1])} A {F(r)} {F(r)} 0 0 1 {F(p1[0])} {F(p1[1])}" stroke="#6A4A3A" stroke-width="1" fill="none" opacity="0.4"/>')
    return "".join(o)


def cloud(uid, cx, cy, w, seed):
    puffs = [(-0.36, 0.08, 0.22), (-0.14, -0.12, 0.28), (0.14, -0.06, 0.26), (0.36, 0.1, 0.2), (0, 0.14, 0.3)]
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        best = None
        for px, py, pr in puffs:
            # furthest point of the union along this direction (rough)
            dx, dy = math.cos(a), math.sin(a)
            t = (px * dx + py * dy) + math.sqrt(max(0, pr * pr - (px * dy - py * dx) ** 2))
            best = t if best is None or t > best else best
        pts.append((cx + math.cos(a) * best * w, cy + min(math.sin(a) * best * w, w * 0.2)))
    d = smooth_closed(jitter(pts, seed, 0.6))
    return (f'<path d="{d}" fill="#FBFDFF"/>' + shade(uid + "-s", d, "#B8CCE2", 0, 1, k=w * 0.06, op=0.8)
            + strokes(uid, d, bbox(pts), ["#E2ECF6", "#FFFFFF", "#CFDDEC"], seed, n=30, angle=-10, length=(6, 18), width=(0.6, 1.6), opacity=(0.4, 0.8), curve=0.5)
            + ink(d, "#7D93AE", 1.3, seed, 1, 0.6))


def cauldron(u, cx, base, w, seed=161):
    """Black pot of gold with a heap of coins."""
    h = w * 0.7
    body = smooth_closed([(cx - w * 0.44, base - h * 0.86), (cx - w * 0.52, base - h * 0.5), (cx - w * 0.4, base - h * 0.1), (cx, base),
                          (cx + w * 0.4, base - h * 0.1), (cx + w * 0.52, base - h * 0.5), (cx + w * 0.44, base - h * 0.86)])
    pot_c = "#2E2A32"
    o = [shadow(cx, base, w * 0.6, 6, 0.2)]
    for sg in (-1, 1):
        o.append(f'<path d="M {F(cx + sg * w * 0.28)} {F(base - h * 0.08)} l {F(sg * 5)} 10" stroke="#1E1A22" stroke-width="7" stroke-linecap="round"/>')
    # coin heap (back part, above the rim)
    rnd = random.Random(seed)
    heap = []
    for i in range(34):
        t = rnd.random()
        x = cx + (t - 0.5) * w * 0.86
        top = base - h * 0.86 - (1 - ((t - 0.5) * 2) ** 2) * h * 0.4
        y = rnd.uniform(top, base - h * 0.8)
        heap.append((y, x))
    heap.sort()
    o.append(f'<path d="{blob(cx, base - h * 0.88, w * 0.44, h * 0.3, seed, 0.06, 14)}" fill="#C9922A"/>')
    for y, x in heap:
        o.append(coin(x, y, rnd.uniform(5.5, 7.5), tilt=rnd.uniform(0.35, 0.75), mark=False))
    o.append(glow(u + "-g", cx, base - h * 0.95, w * 0.55, h * 0.45, "#FFE07A", 0.5))
    o.append(paint(u + "-b", body, (cx - w * 0.55, base - h * 0.9, cx + w * 0.55, base + 2), pot_c, seed, tints=["#4A4452", "#18141C", "#5E5868"], angle=-90, n=40,
                   ink_col="#0E0A12", ink_w=1.6))
    o.append(rim(u + "-br", body, "#9AD0A0", -1, -0.3, k=2, op=0.7))
    o.append(f'<path d="M {F(cx - w * 0.36)} {F(base - h * 0.6)} Q {F(cx - w * 0.42)} {F(base - h * 0.35)} {F(cx - w * 0.3)} {F(base - h * 0.16)}" stroke="#8A8494" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    rimd = blob(cx, base - h * 0.86, w * 0.5, h * 0.09, seed + 2, 0.02, 16)
    o.append(f'<path d="{rimd}" fill="none" stroke="#3E3A44" stroke-width="7"/><path d="{rimd}" fill="none" stroke="#6E6878" stroke-width="2" transform="translate(0 -1.6)"/>')
    # front coins tumbling over the rim
    for x, y, r, t in ((cx - w * 0.2, base - h * 0.88, 7, 0.5), (cx + w * 0.06, base - h * 0.9, 7.5, 0.4), (cx + w * 0.28, base - h * 0.86, 7, 0.55)):
        o.append(coin(x, y, r, tilt=t, mark=False))
    return "".join(o)


def leprechaun_hat(uid, cx, base, s, rot_=0, seed=171):
    """Green top hat with a black band and gold buckle; base = brim line."""
    g = ("#2F8A4A", "#5AB26A", "#1E5A32", "#123A20")
    crown = smooth_closed(jitter([(cx - 0.36 * s, base - 0.04 * s), (cx - 0.4 * s, base - 0.9 * s), (cx + 0.4 * s, base - 0.9 * s), (cx + 0.36 * s, base - 0.04 * s)], seed, 0.6))
    top = blob(cx, base - 0.9 * s, 0.4 * s, 0.09 * s, seed, 0.02, 14)
    brim = blob(cx, base, 0.66 * s, 0.13 * s, seed + 1, 0.03, 18)
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(base)})">']
    o.append(paint(uid + "-br", brim, (cx - 0.7 * s, base - 0.15 * s, cx + 0.7 * s, base + 0.15 * s), g[0], seed, tints=[g[1], g[2]], angle=0, n=24, ink_col=g[3]))
    o.append(paint(uid + "-c", crown, (cx - 0.42 * s, base - 0.95 * s, cx + 0.42 * s, base), g[0], seed + 2, tints=[g[1], g[2], g[1]], angle=-90, n=40, ink_col=g[3]))
    o.append(shade(uid + "-cs", crown, g[2], 1, 0, k=0.08 * s, op=0.5))
    o.append(f'<path d="{top}" fill="{g[1]}" stroke="{g[3]}" stroke-width="1.2"/>')
    o.append(f'<path d="M {F(cx - 0.375 * s)} {F(base - 0.2 * s)} L {F(cx + 0.375 * s)} {F(base - 0.2 * s)} L {F(cx + 0.38 * s)} {F(base - 0.36 * s)} L {F(cx - 0.38 * s)} {F(base - 0.36 * s)} Z" fill="#2A2420"/>')
    o.append(f'<rect x="{F(cx - 0.12 * s)}" y="{F(base - 0.39 * s)}" width="{F(0.24 * s)}" height="{F(0.22 * s)}" rx="1.5" fill="none" stroke="#F2C14E" stroke-width="{F(0.05 * s)}"/>')
    o.append(shamrock(uid + "-sh", cx + 0.24 * s, base - 0.58 * s, 0.13 * s, SHAM2, seed, rot_=20, stem=False))
    o.append("</g>")
    return "".join(o)


def clover_patch(uid, x0, x1, y, seed, n=12):
    rnd = random.Random(seed)
    o = [grass(x0, x1, y, seed, n * 3, cols=("#3E8A44", "#5DAA5A", "#2E6A34"))]
    for k in range(n):
        x = rnd.uniform(x0, x1)
        s = rnd.uniform(6, 10)
        o.append(shamrock(f"{uid}{k}", x, y - s * 1.1 - rnd.uniform(0, 5), s, SHAM if k % 2 else SHAM2, seed + k, rot_=rnd.uniform(-25, 25)))
    return "".join(o)


def stpatricks_scene(u="sp"):
    o = [shadow(196, 318, 176, 9, 0.12)]
    o.append(f'<path d="{smooth_closed([(8, 318), (70, 304), (190, 300), (320, 304), (374, 318), (190, 326)])}" fill="#7CB860" opacity="0.5"/>')
    # rainbow from a cloud on the left down into the pot on the right
    o.append(rainbow(u + "-rb", 178, 286, 168, 11, 205, 355, 3))
    o.append(cloud(u + "-cl", 60, 226, 100, 4))
    o.append(cauldron(u + "-pot", 292, 306, 104))
    o.append(glow(u + "-gl2", 300, 230, 70, 40, "#FFE07A", 0.35))
    o.append(leprechaun_hat(u + "-hat", 192, 306, 70, rot_=-6))
    # coins spilled on the grass
    for k, (x, y, r, t) in enumerate(((236, 312, 7, 0.7), (250, 316, 6.5, 0.75), (342, 314, 7, 0.7), (356, 308, 6, 0.6), (226, 302, 6, 0.3))):
        o.append(coin(x, y, r, tilt=t, mark=t < 0.5))
    o.append(clover_patch(u + "-cp", 18, 140, 318, 7, n=9))
    o.append(shamrock(u + "-big", 120, 278, 20, SHAM, 9, rot_=-12))
    o.append(shamrock(u + "-four", 62, 296, 14, SHAM2, 11, rot_=14, four=True))
    for x, y, r in ((120, 84, 6), (336, 96, 5), (250, 60, 4), (40, 150, 4)):
        o.append(twinkle(x, y, r))
    return "".join(o)


def stpatricks_garland(u="spg"):
    o = [twine("#2E6A3A", "#8ED27E", 2)]
    for k in range(8):
        x = 20 + 40 * k
        y = swag_y(x)
        if k % 2 == 0:
            L = 6 + (k % 4) * 2
            o.append(f'<path d="M {x} {F(y)} l 0 {L}" stroke="#2E6A3A" stroke-width="1"/>')
            o.append(shamrock(f"{u}-s{k}", x, y + L + 11, 12, SHAM if k % 4 == 0 else SHAM2, 30 + k, rot_=180 + (-1) ** (k // 2) * 10, stem=False))
            o.append(f'<path d="M {x} {F(y + L)} l 0 4" stroke="{SHAM[3]}" stroke-width="2" stroke-linecap="round"/>')
        else:
            L = 12 + (k % 3) * 3
            o.append(f'<path d="M {x} {F(y)} l 0 {L}" stroke="#8A6212" stroke-width="0.9"/>')
            o.append(coin(x, y + L + 8, 8, seed=k))
    return "".join(o)


def particles_clover():
    save("clover1", 40, 40, shamrock("pc1", 20, 17, 15, SHAM, 1, rot_=-10))
    save("clover2", 40, 40, shamrock("pc2", 20, 17, 13, SHAM2, 2, rot_=15, four=True))


# ================================================================ JULY 4
RED = ("#C8323A", "#E8605E", "#8E1A20", "#5E0C12")
BLUE = ("#2E4A8A", "#5A78B8", "#1E3060", "#121E40")
CREAM = ("#FBF4E8", "#FFFFFF", "#D9CDB8", "#8A7A62")


def fan_bunting(u, cx, top, R, seed):
    """Pleated half-rosette hanging below (cx, top): blue centre with a star, then cream, red, cream, red rings."""
    o = []
    rings = [(R, RED), (R * 0.82, CREAM), (R * 0.64, RED), (R * 0.46, CREAM), (R * 0.3, BLUE)]
    n_pleat = 9
    for k, (r, cols) in enumerate(rings):
        # scalloped outer edge: one bump per pleat
        pts = [(cx - r, top)]
        for i in range(n_pleat * 2 + 1):
            a = math.pi - math.pi * i / (n_pleat * 2)
            rr = r * (1.0 if i % 2 else 0.94)
            pts.append((cx + math.cos(a) * rr, top + math.sin(a) * rr * 0.9))
        pts.append((cx + r, top))
        d = "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in pts[:1]) + " " + smooth_open(pts[1:-1]).replace("M", "L", 1) + f" L {F(cx + r)} {F(top)} Z"
        o.append(paint(f"{u}-{k}", d, (cx - r, top - 1, cx + r, top + r), cols[0], seed + k, tints=[cols[1], cols[2]], angle=90, n=int(r * 0.9),
                       ink_col=cols[3], ink_w=1.0, length=(r * 0.15, r * 0.5), width=(0.3, 1.0), op=(0.2, 0.5)))
    # pleat lines radiating from the centre
    pl = []
    for i in range(1, n_pleat * 2, 2):
        a = math.pi - math.pi * i / (n_pleat * 2)
        pl.append(f"M {F(cx + math.cos(a) * R * 0.3)} {F(top + math.sin(a) * R * 0.27)} L {F(cx + math.cos(a) * R * 0.97)} {F(top + math.sin(a) * R * 0.87)}")
    o.append(f'<path d="{" ".join(pl)}" stroke="#5E2A22" stroke-width="0.9" opacity="0.45"/>')
    o.append(f'<path d="{" ".join(pl)}" stroke="#FFFFFF" stroke-width="0.7" opacity="0.4" transform="translate(1.2 0)"/>')
    o.append(f'<path d="{poly(star_pts(cx, top + R * 0.14, R * 0.12, 0.45))}" fill="#FBF4E8"/>')
    o.append(f'<path d="M {F(cx - R - 1)} {F(top)} L {F(cx + R + 1)} {F(top)}" stroke="{BLUE[3]}" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(o)


def swag_drape(u, x0, x1, top, sag, depth, seed):
    """Draped bunting between two hanging points: blue band with stars, then red / cream / red."""
    def curve(t, extra):
        x = x0 + (x1 - x0) * t
        y = top + 4 * t * (1 - t) * (sag + extra)
        return x, y
    bands = [(0, 0.26, BLUE), (0.26, 0.5, RED), (0.5, 0.74, CREAM), (0.74, 1.0, RED)]
    o = []
    for k, (f0, f1, cols) in enumerate(bands):
        a = [curve(i / 16, depth * f0) for i in range(17)]
        b = [curve(i / 16, depth * f1) for i in range(17)][::-1]
        d = smooth_open(a) + " " + smooth_open(b).replace("M", "L", 1) + " Z"
        box = (x0, top - 2, x1, top + sag + depth + 4)
        o.append(paint(f"{u}-{k}", d, box, cols[0], seed + k, tints=[cols[1], cols[2]], angle=0, n=26, ink_w=0, length=(8, 22), width=(0.4, 1.2), op=(0.2, 0.5)))
    outline_top = smooth_open([curve(i / 16, 0) for i in range(17)])
    outline_bot = smooth_open([curve(i / 16, depth) for i in range(17)])
    o.append(ink(outline_bot, RED[3], 1.2, seed, 1, 0.7) + ink(outline_top, BLUE[3], 1.0, seed, 1, 0.6))
    # gathers near the hanging points
    g = []
    for sgn, xa in ((1, x0), (-1, x1)):
        for j in range(4):
            t0 = 0.02 + j * 0.035
            t = t0 if sgn > 0 else 1 - t0
            p0 = curve(t, 0)
            p1 = curve(t + sgn * 0.08, depth)
            g.append(f"M {F(p0[0])} {F(p0[1])} Q {F((p0[0] + p1[0]) / 2 + sgn * 2)} {F((p0[1] + p1[1]) / 2)} {F(p1[0])} {F(p1[1])}")
    o.append(f'<path d="{" ".join(g)}" stroke="#3A1A14" stroke-width="0.8" fill="none" opacity="0.4"/>')
    # stars on the blue band
    for i in range(1, 6):
        t = i / 6
        sx, sy = curve(t, depth * 0.13)
        o.append(f'<path d="{poly(star_pts(sx, sy, 2.6, 0.45))}" fill="#FBF4E8"/>')
    return "".join(o)


def july4_garland(u="j4g"):
    o = []
    for x0, x1 in ((0, 160), (160, 320)):
        o.append(swag_drape(f"{u}-d{x0}", x0, x1, 6, 10, 22, 10 + x0))
    for x, y, r, cols in ((80, 50, 7, RED), (240, 50, 7, BLUE)):
        o.append(f'<path d="M {x} 38 L {x} {y - r}" stroke="#8A7A62" stroke-width="0.8"/>')
        o.append(painted_star(f"{u}-s{x}", x, y, r, cols, x))
    for x in (0, 160, 320):
        o.append(fan_bunting(f"{u}-f{x}", x, 4, 28, 30 + x))
    for x, y in ((40, 46), (120, 44), (200, 46), (280, 44)):
        o.append(twinkle(x, y, 3, "#FBF4E8", "#8A7A62"))
    return "".join(o)


def firework(cx, cy, r, col, seed, n=16):
    rnd = random.Random(seed)
    o = []
    rays, dots = [], []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.08, 0.08)
        r0, r1 = r * rnd.uniform(0.25, 0.35), r * rnd.uniform(0.75, 0.95)
        rays.append(f"M {F(cx + math.cos(a) * r0)} {F(cy + math.sin(a) * r0)} Q {F(cx + math.cos(a + 0.06) * (r0 + r1) / 2)} {F(cy + math.sin(a + 0.06) * (r0 + r1) / 2 + 2)} {F(cx + math.cos(a) * r1)} {F(cy + math.sin(a) * r1 + 3)}")
        dots.append(f'<circle cx="{F(cx + math.cos(a) * r * 1.04)}" cy="{F(cy + math.sin(a) * r * 1.04 + 4)}" r="{F(rnd.uniform(1.2, 2.2))}"/>')
    o.append(f'<path d="{" ".join(rays)}" stroke="{dk(col, 0.35)}" stroke-width="3.2" fill="none" stroke-linecap="round" opacity="0.5"/>')
    o.append(f'<path d="{" ".join(rays)}" stroke="{col}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{" ".join(rays)}" stroke="#FFF6D6" stroke-width="0.7" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(f'<g fill="{col}" stroke="{dk(col, 0.35)}" stroke-width="0.6">{"".join(dots)}</g>')
    o.append(twinkle(cx, cy, r * 0.16, "#FFF6D6", dk(col, 0.2)))
    return "".join(o)


def little_flag(uid, x, base, h, lean, seed, fw=34, fh=22):
    """A small stick flag (stripes and a starry canton), waving a little."""
    tx, ty = x + lean, base - h
    o = [f'<path d="M {F(x)} {F(base)} L {F(tx)} {F(ty)}" stroke="#6A4A2A" stroke-width="2.4" stroke-linecap="round"/>',
         f'<circle cx="{F(tx)}" cy="{F(ty - 1)}" r="2.2" fill="#E2B04A" stroke="#7A5212" stroke-width="0.6"/>']
    def P(u_, v):  # u_ along the flag (0..1), v down (0..1), with a gentle wave
        return (tx + 1 + u_ * fw, ty + 1 + v * fh + math.sin(u_ * math.pi * 1.6) * 2.4)
    outline = [P(i / 8, 0) for i in range(9)] + [P(1 - i / 8, 1) for i in range(9)]
    d = poly(outline)
    o.append(f'<path d="{d}" fill="#FBF4E8"/>')
    stripes = []
    for j in range(7):
        if j % 2 == 0:
            v0, v1 = j / 7, (j + 1) / 7
            pts = [P(i / 8, v0) for i in range(9)] + [P(1 - i / 8, v1) for i in range(9)]
            stripes.append(poly(pts))
    o.append(f'<path d="{" ".join(stripes)}" fill="{RED[0]}"/>')
    cant = [P(i / 8 * 0.42, 0) for i in range(4)] + [P(0.42, 0.56), P(0, 0.56)]
    o.append(f'<path d="{poly([P(0, 0), P(0.14, 0), P(0.28, 0), P(0.42, 0), P(0.42, 0.56), P(0.28, 0.56), P(0.14, 0.56), P(0, 0.56)])}" fill="{BLUE[0]}"/>')
    del cant
    o.append("".join(f'<circle cx="{F(P(u_, v)[0])}" cy="{F(P(u_, v)[1])}" r="0.9" fill="#FBF4E8"/>' for u_ in (0.08, 0.2, 0.32) for v in (0.12, 0.28, 0.44)))
    o.append(ink(d, "#5E2A22", 1.0, seed, 1, 0.6))
    return "".join(o)


def picnic_basket(u, cx, base, w, h, seed=181):
    wick, wl, wd, wi = "#C99A5A", "#E6C48A", "#9A6A32", "#5E3E1A"
    body_pts = [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w / 2 - 6, base), (cx - w / 2 + 6, base)]
    bd = poly(jitter(body_pts, seed, 0.8))
    o = [shadow(cx, base, w * 0.6, 6, 0.2)]
    # handle
    hd = f"M {F(cx - w * 0.3)} {F(base - h)} Q {F(cx - w * 0.32)} {F(base - h * 2.15)} {F(cx)} {F(base - h * 2.15)} Q {F(cx + w * 0.32)} {F(base - h * 2.15)} {F(cx + w * 0.3)} {F(base - h)}"
    o.append(f'<path d="{hd}" stroke="{wi}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="{hd}" stroke="{wick}" stroke-width="6.4" fill="none" stroke-linecap="round"/>'
             f'<path d="{hd}" stroke="{wd}" stroke-width="6.4" fill="none" stroke-dasharray="3 4"/>')
    # gingham cloth spilling out of the top
    cloth = smooth_closed([(cx - w * 0.52, base - h + 4), (cx - w * 0.44, base - h - 14), (cx - w * 0.1, base - h - 20), (cx + w * 0.2, base - h - 16),
                           (cx + w * 0.5, base - h - 10), (cx + w * 0.56, base - h + 6), (cx + w * 0.4, base - h + 22), (cx + w * 0.3, base - h + 8), (cx, base - h + 6)])
    o.append(f'<path d="{cloth}" fill="#FBF4E8"/>')
    o.append(f'<clipPath id="{u}-cc"><path d="{cloth}"/></clipPath><g clip-path="url(#{u}-cc)" fill="{RED[0]}" opacity="0.55">'
             + "".join(f'<rect x="{F(cx - w * 0.6 + i * 8)}" y="{F(base - h - 26)}" width="4" height="60"/>' for i in range(int(w * 1.2 / 8) + 2))
             + "".join(f'<rect x="{F(cx - w * 0.6)}" y="{F(base - h - 26 + j * 8)}" width="{F(w * 1.3)}" height="4"/>' for j in range(8)) + "</g>")
    o.append(ink(cloth, RED[3], 1.1, seed, 1, 0.6))
    # wicker body with weave
    o.append(paint(u + "-b", bd, bbox(body_pts), wick, seed, tints=[wl, wd], angle=0, n=30, ink_col=wi, ink_w=1.6))
    weave = []
    for j in range(int(h / 7)):
        y = base - h + 5 + j * 7
        for i in range(int(w / 10) + 1):
            x = cx - w / 2 + 4 + i * 10 + (j % 2) * 5
            weave.append(f"M {F(x - 3.5)} {F(y)} Q {F(x)} {F(y + 3.5)} {F(x + 3.5)} {F(y)}")
    o.append(f'<clipPath id="{u}-bc"><path d="{bd}"/></clipPath><g clip-path="url(#{u}-bc)">'
             f'<path d="{" ".join(weave)}" stroke="{wd}" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
             f'<path d="{" ".join(weave)}" stroke="{wl}" stroke-width="0.8" fill="none" stroke-linecap="round" transform="translate(0 -1.4)"/></g>')
    o.append(shade(u + "-bs", bd, wi, 1, 0.3, k=6, op=0.35))
    rimd = f"M {F(cx - w / 2 - 3)} {F(base - h)} L {F(cx + w / 2 + 3)} {F(base - h)}"
    o.append(f'<path d="{rimd}" stroke="{wi}" stroke-width="7" stroke-linecap="round"/><path d="{rimd}" stroke="{wl}" stroke-width="4.4" stroke-linecap="round"/>'
             f'<path d="{rimd}" stroke="{wd}" stroke-width="4.4" stroke-dasharray="4 3"/>')
    return "".join(o)


def watermelon_slice(uid, cx, cy, r, rot_, seed, bite=False):
    """Wedge of watermelon: rind arc at the bottom, point at the top."""
    a0, a1 = math.radians(50), math.radians(130)
    tip = (cx, cy - r * 0.15)
    arc = [(cx + math.cos(a0 + (a1 - a0) * i / 10) * r, cy - r * 0.15 + math.sin(a0 + (a1 - a0) * i / 10) * r) for i in range(11)]
    flesh = [tip] + arc
    rind_out = [(cx + math.cos(a0 + (a1 - a0) * i / 10) * (r + 5), cy - r * 0.15 + math.sin(a0 + (a1 - a0) * i / 10) * (r + 5)) for i in range(11)]
    rot_pts = lambda pts: [rot(x, y, cx, cy, rot_) for x, y in pts]  # noqa: E731
    rd = poly(rot_pts(arc[::-1] + rind_out))
    fd = smooth_closed(rot_pts(flesh)) if False else poly(rot_pts(flesh))
    o = [f'<path d="{rd}" fill="#3E8A44" stroke="#1E4A2A" stroke-width="1.2" stroke-linejoin="round"/>']
    o.append(f'<path d="{poly(rot_pts([(x, y - 1.6) for x, y in arc[::-1]] + [(x, y + 1.4) for x, y in arc]))}" fill="#E8F2C8"/>')
    o.append(paint(uid, fd, bbox(rot_pts(flesh)), "#E8505A", seed, tints=["#F27A7A", "#C8323A", "#FF9A94"], angle=-90 + rot_, n=int(r * 1.2), ink_col="#8E1A20", ink_w=1.1,
                   length=(r * 0.15, r * 0.5), width=(0.4, 1.2)))
    rnd = random.Random(seed)
    for _ in range(int(r * 0.35)):
        t, f = rnd.uniform(0.35, 0.8), rnd.uniform(-0.45, 0.45)
        x, y = cx + f * r * t * 0.8, cy - r * 0.15 + r * t * 0.9
        x, y = rot(x, y, cx, cy, rot_)
        o.append(f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="1.1" ry="1.9" fill="#2A1A14" transform="rotate({F(rot_ + f * 40)} {F(x)} {F(y)})"/>')
    return "".join(o)


def july4_scene(u="j4"):
    o = []
    # fireworks in the sky behind
    o.append(firework(86, 70, 46, "#D8344A", 1, 18))
    o.append(firework(290, 56, 40, "#3E6AC0", 2, 16))
    o.append(firework(196, 30, 24, "#E2B04A", 3, 12))
    o.append(firework(350, 150, 22, "#D8344A", 4, 12))
    # picnic blanket (red gingham) in perspective
    bl = smooth_closed([(20, 300), (120, 284), (270, 284), (366, 300), (340, 324), (190, 330), (40, 324)])
    o.append(f'<path d="{bl}" fill="#FBF4E8"/>')
    o.append(f'<clipPath id="{u}-bl"><path d="{bl}"/></clipPath><g clip-path="url(#{u}-bl)" fill="{RED[0]}" opacity="0.5">'
             + "".join(f'<path d="M {F(190 + (i - 14) * 9)} 284 L {F(190 + (i - 14) * 13)} 332 L {F(190 + (i - 14) * 13 + 6.5)} 332 L {F(190 + (i - 14) * 9 + 4.5)} 284 Z"/>' for i in range(29))
             + "".join(f'<rect x="0" y="{F(284 + j * 6)}" width="380" height="{F(3 + j * 0.3)}"/>' for j in range(8)) + "</g>")
    o.append(ink(bl, RED[3], 1.2, 2, 1, 0.55))
    o.append(little_flag(u + "-fl1", 172, 230, 104, -12, 1, fw=36, fh=23))
    o.append(little_flag(u + "-fl2", 192, 230, 116, 6, 2, fw=40, fh=26))
    o.append(picnic_basket(u + "-bk", 196, 304, 128, 64))
    o.append(watermelon_slice(u + "-w1", 70, 268, 40, -8, 5))
    o.append(watermelon_slice(u + "-w2", 106, 280, 32, 14, 6))
    o.append(painted_star(u + "-st", 298, 292, 13, RED, 7, rot_=-80))
    o.append(painted_star(u + "-st2", 326, 302, 10, BLUE, 8, rot_=-100))
    o.append(rim(u + "-st2r", poly(jitter(star_pts(326, 302, 10, 0.5, -100), 8, 0.3)), "#B8C8F0", -1, -1, k=1, op=0.7))
    o.append(painted_star(u + "-st3", 282, 314, 8, CREAM, 9, rot_=-95))
    return "".join(o)


def particles_stars():
    save("star1", 40, 40, painted_star("ps1", 20, 21, 16, RED, 1, rot_=-84))
    save("star2", 40, 40, painted_star("ps2", 20, 21, 15, BLUE, 2, rot_=-96) + rim("ps2r", poly(jitter(star_pts(20, 21, 15, 0.5, -96), 2, 0.45)), "#C8D6F6", -1, -1, k=1.2, op=0.9))


# ================================================================ build
SEASONS = {
    "halloween": lambda: (save("halloween-scene", 380, 330, halloween_scene()), save("halloween-garland", 320, 74, halloween_garland()), particles_halloween()),
    "thanksgiving": lambda: (save("thanksgiving-scene", 380, 330, thanksgiving_scene()), save("thanksgiving-garland", 320, 74, thanksgiving_garland())),
    "christmas": lambda: (save("christmas-scene", 380, 330, christmas_scene()), save("christmas-garland", 320, 74, christmas_garland()), particles_snow()),
    "newyear": lambda: (save("newyear-scene", 380, 330, newyear_scene()), save("newyear-garland", 320, 74, newyear_garland()), particles_confetti()),
    "winter": lambda: (save("winter-scene", 380, 330, winter_scene()), save("winter-garland", 320, 74, winter_garland()), particles_snow()),
    "valentine": lambda: (save("valentine-scene", 380, 330, valentine_scene()), save("valentine-garland", 320, 74, valentine_garland()), particles_valentine()),
    "stpatricks": lambda: (save("stpatricks-scene", 380, 330, stpatricks_scene()), save("stpatricks-garland", 320, 74, stpatricks_garland()), particles_clover()),
    "spring": lambda: (save("spring-scene", 380, 330, spring_scene()), save("spring-garland", 320, 74, spring_garland()), particles_spring()),
    "july4": lambda: (save("july4-scene", 380, 330, july4_scene()), save("july4-garland", 320, 74, july4_garland()), particles_stars()),
    "summer": lambda: (save("summer-scene", 380, 330, summer_scene()), save("summer-garland", 320, 74, summer_garland())),
}


def build(only=None):
    for name, fn in SEASONS.items():
        if only is None or name in only:
            fn()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
