"""Painted website decor for fall, halloween, thanksgiving, christmas and winter (scenes, garlands, particles).

Each 380 x 330 scene is a small gouache painting on a transparent ground: a soft-edged vignette (sky, light, distance)
that fades out toward the page, with the subject painted in front of it with washes, form-following strokes, pooled
edges, dry-brush highlights and a warm ink line used sparingly. Everything reads on the cream day page (#FFF6E5) and on
the dark brown night page (#1C1610): dark subjects carry a rim light, white subjects a blue shade side.

decor.py (fall) and decor_seasons.py (the other four) call the *_scene / *_garland / particle functions here and write
the files; this module writes nothing itself and imports nothing from them (no import cycles)."""
import math
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash  # noqa: E402
from paint import rough  # noqa: E402

INK = "#3A2418"
TW = 320


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



# ---------------------------------------------------------------- small utilities
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


def rpts(pts, cx, cy, deg):
    return [rot(x, y, cx, cy, deg) for x, y in pts]


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
    """Light band hugging the inside of a shape on the (sx, sy) side (sx, sy point toward the light)."""
    return (f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2 * k:.1f}" opacity="{op}" '
            f'transform="translate({F(-sx * k)} {F(-sy * k)})"/></g>')


def shade(uid, d, col, sx, sy, k=6.0, op=0.35):
    """Soft shade crescent inside a shape on the (sx, sy) side."""
    return rim(uid, d, col, sx, sy, k, op)


def rgrad(uid, cx, cy, r, stops, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    f = f' fx="{F(fx)}" fy="{F(fy)}"' if fx is not None else ""
    return f'<radialGradient id="{uid}" cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}"{f} gradientUnits="userSpaceOnUse">{s}</radialGradient>'


def lgrad(uid, x1, y1, x2, y2, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<linearGradient id="{uid}" x1="{F(x1)}" y1="{F(y1)}" x2="{F(x2)}" y2="{F(y2)}" gradientUnits="userSpaceOnUse">{s}</linearGradient>'


def glow(uid, cx, cy, rx, ry, col, op, mid=0.45):
    return (f'<defs>{rgrad(uid, 0.5, 0.5, 0.5, [(0, col, op), (0.5, col, op * mid), (1, col, 0)]).replace(" gradientUnits=\"userSpaceOnUse\"", "")}</defs>'
            f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{uid})"/>')


def shadow(cx, cy, rx, ry, op=0.16, col=INK):
    return f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="{col}" opacity="{op}"/>'


def vignette(uid, body, blots, box=(0, 0, 380, 330)):
    """Soft-edged painted backdrop: body (sky, hills, ground...) shown through a luminance mask built from a few
    overlapping radial fades, so the painting has an organic, brushed-out edge instead of a hard rectangle."""
    defs, ells = [], []
    for k, (cx, cy, rx, ry, inner) in enumerate(blots):
        g = f"{uid}-m{k}"
        defs.append(rgrad(g, 0.5, 0.5, 0.5, [(0, "#FFFFFF", 1), (inner, "#FFFFFF", 1), (1, "#FFFFFF", 0)]).replace(' gradientUnits="userSpaceOnUse"', ""))
        ells.append(f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{g})"/>')
    x0, y0, x1, y1 = box
    return (f'<defs>{"".join(defs)}<mask id="{uid}" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}">'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#000"/>{"".join(ells)}</mask></defs>'
            f'<g mask="url(#{uid})">{body}</g>')


def sky_rect(uid, stops, box=(0, 0, 380, 330)):
    x0, y0, x1, y1 = box
    return (f'<defs>{lgrad(uid, 0, y0, 0, y1, stops)}</defs>'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{uid})"/>')


def hstrokes(uid, d, box, cols, seed, n, angle=0, length=(10, 30), width=(0.8, 2.2), op=(0.2, 0.5), curve=0.15):
    return strokes(uid, d, box, cols, seed, n=n, angle=angle, length=length, width=width, opacity=op, curve=curve)


def lines(d_list, col, w, op=1.0, cap="round"):
    return f'<path d="{" ".join(d_list)}" stroke="{col}" stroke-width="{F(w)}" fill="none" stroke-linecap="{cap}" opacity="{op}"/>'


def ridge(pts, seed, base, amp=6, depth=4):
    line = rough(pts, seed, amp, depth)
    return poly(line + [(line[-1][0], base), (line[0][0], base)]), line


def grass_tufts(seed, box, cols, n=60, h=(6, 16), sw=1.5):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        lean = rnd.uniform(-5, 2)
        out.append(f'<path d="M {F(x)} {F(y)} q {F(lean * 0.4)} {F(-hh / 2)} {F(lean)} {F(-hh)}" stroke="{rnd.choice(cols)}"/>')
    return f'<g fill="none" stroke-width="{sw}" stroke-linecap="round">' + "".join(out) + "</g>"


def speck(seed, box, cols, n, r=(0.6, 1.6), op=(0.4, 0.9)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.2f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))


def swag_y(x, top=10, sag=34):
    t = x / TW
    return (1 - t) ** 3 * top + 3 * (1 - t) ** 2 * t * sag + 3 * (1 - t) * t * t * sag + t ** 3 * top


def swag_slope(x, **kw):
    return math.degrees(math.atan2(swag_y(x + 0.5, **kw) - swag_y(x - 0.5, **kw), 1))


def wrap(fn, x, margin):
    out = fn(x)
    if x < margin:
        out += fn(x + TW)
    if x > TW - margin:
        out += fn(x - TW)
    return out


# ---------------------------------------------------------------- painted pieces shared by several seasons
def maple(uid, cx, cy, s, fill, dark, rot_=0, seed=1, light=None, stem=True):
    """Gouache maple leaf: five lobes with toothed edges, pooled darker wash on one side, veins, a stem."""
    rnd = random.Random(seed)
    tips = [(0, -1.0), (0.22, -0.62), (0.62, -0.78), (0.52, -0.38), (0.98, -0.16), (0.62, 0.0), (0.68, 0.36), (0.34, 0.26), (0.1, 0.5),
            (0, 0.48), (-0.1, 0.5), (-0.34, 0.26), (-0.68, 0.36), (-0.62, 0.0), (-0.98, -0.16), (-0.52, -0.38), (-0.62, -0.78), (-0.22, -0.62)]
    pts = []
    for i, (x, y) in enumerate(tips):
        k = 1 + rnd.uniform(-0.04, 0.04)
        pts.append((cx + x * s * k, cy + y * s * k))
        if i % 2 == 0:  # tooth between lobe tip and notch
            nx, ny = tips[(i + 1) % len(tips)]
            pts.append((cx + (x * 0.62 + nx * 0.38) * s * 1.06, cy + (y * 0.62 + ny * 0.38) * s * 1.06))
    pts = rpts(pts, cx, cy, rot_)
    d = poly(pts)
    light = light or lt(fill, 0.35)
    o = [f'<g>']
    o.append(wash(d, fill, seed, 2, 0.6, 0.5))
    o.append(strokes(uid, d, bbox(pts), [dark, light, fill, lt(fill, 0.55)], seed + 1, n=int(s * 1.6), angle=-90 + rot_, length=(s * 0.3, s * 0.9),
                     width=(0.4, s * 0.05), opacity=(0.25, 0.5), curve=0.3))
    o.append(shade(uid + "-s", d, dark, 0.8, 0.5, k=s * 0.22, op=0.4))
    vb = rot(cx, cy + 0.42 * s, cx, cy, rot_)
    veins = []
    for tx, ty in ((0, -0.95), (0.6, -0.74), (-0.6, -0.74), (0.94, -0.14), (-0.94, -0.14)):
        tp = rot(cx + tx * s * 0.88, cy + ty * s * 0.88, cx, cy, rot_)
        veins.append(f"M {F(vb[0])} {F(vb[1])} Q {F((vb[0] + tp[0]) / 2 + (tp[1] - vb[1]) * 0.05)} {F((vb[1] + tp[1]) / 2)} {F(tp[0])} {F(tp[1])}")
    o.append(lines(veins, lt(fill, 0.6), max(0.7, s * 0.04), 0.8))
    o.append(ink(d, dark, max(0.7, s * 0.045), seed + 2, 1, 0.55))
    if stem:
        se = rot(cx + 0.06 * s, cy + 0.98 * s, cx, cy, rot_)
        o.append(f'<path d="M {F(vb[0])} {F(vb[1])} Q {F((vb[0] + se[0]) / 2 - 1)} {F((vb[1] + se[1]) / 2)} {F(se[0])} {F(se[1])}" stroke="{dark}" stroke-width="{F(max(1.1, s * 0.08))}" fill="none" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def oak_leaf(uid, cx, cy, s, fill, dark, rot_=0, seed=2, stem=True):
    pts = []
    for i in range(0, 360, 10):
        a = math.radians(i)
        wob = 1 + 0.22 * math.sin(a * 5 + 0.4) if 15 < i < 345 else 1
        pts.append((cx + 0.44 * s * math.sin(a) * wob, cy - s * math.cos(a) * 0.9))
    pts = rpts(jitter(pts, seed, 0.3), cx, cy, rot_)
    d = smooth_closed(pts)
    o = [wash(d, fill, seed, 2, 0.6, 0.5)]
    o.append(strokes(uid, d, bbox(pts), [dark, lt(fill, 0.35), fill], seed + 1, n=int(s * 1.2), angle=-90 + rot_, length=(s * 0.25, s * 0.7), width=(0.4, s * 0.045), opacity=(0.25, 0.5)))
    o.append(shade(uid + "-s", d, dark, 0.8, 0.3, k=s * 0.18, op=0.4))
    a, b = rot(cx, cy - 0.82 * s, cx, cy, rot_), rot(cx, cy + 0.88 * s, cx, cy, rot_)
    vs = [f"M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}"]
    for t in (0.2, 0.42, 0.64):
        p0 = rot(cx, cy - 0.85 * s + 1.7 * s * t, cx, cy, rot_)
        for sg in (-1, 1):
            p1 = rot(cx + sg * 0.42 * s, cy - 0.85 * s + 1.7 * s * (t + 0.1), cx, cy, rot_)
            vs.append(f"M {F(p0[0])} {F(p0[1])} L {F(p1[0])} {F(p1[1])}")
    o.append(lines(vs, lt(fill, 0.55), max(0.6, s * 0.04), 0.75))
    o.append(ink(d, dark, max(0.7, s * 0.045), seed + 2, 1, 0.5))
    if stem:
        se = rot(cx, cy + 1.2 * s, cx, cy, rot_)
        o.append(f'<path d="M {F(b[0])} {F(b[1])} L {F(se[0])} {F(se[1])}" stroke="{dark}" stroke-width="{F(max(1.1, s * 0.08))}" stroke-linecap="round"/>')
    return "".join(o)


def acorn_p(uid, cx, cy, s, rot_=0, seed=3):
    nut = blob(cx, cy + 0.3 * s, 0.4 * s, 0.56 * s, seed, 0.04, 14)
    cap = (f"M {F(cx - 0.5 * s)} {F(cy + 0.02 * s)} Q {F(cx)} {F(cy - 0.62 * s)} {F(cx + 0.5 * s)} {F(cy + 0.02 * s)} "
           f"Q {F(cx)} {F(cy + 0.2 * s)} {F(cx - 0.5 * s)} {F(cy + 0.02 * s)} Z")
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    o.append(paint(uid + "-n", nut, (cx - 0.5 * s, cy - 0.3 * s, cx + 0.5 * s, cy + 0.9 * s), "#B9773A", seed, tints=["#D9975A", "#8E5426", "#F0C080"], angle=-85, n=int(s * 0.8), ink_col="#5A3416", ink_w=max(0.7, s * 0.05)))
    o.append(shade(uid + "-ns", nut, "#6E3E1A", 0.7, 0.5, k=s * 0.14, op=0.4))
    o.append(f'<path d="M {F(cx - 0.18 * s)} {F(cy + 0.1 * s)} q {F(-0.04 * s)} {F(0.3 * s)} {F(0.02 * s)} {F(0.5 * s)}" stroke="#FFE2B8" stroke-width="{F(max(0.8, s * 0.07))}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    o.append(paint(uid + "-c", cap, (cx - 0.55 * s, cy - 0.65 * s, cx + 0.55 * s, cy + 0.25 * s), "#6E4A2A", seed + 1, tints=["#8A6238", "#4A3018"], angle=0, n=int(s * 0.5), ink_col="#3A2210", ink_w=max(0.7, s * 0.05)))
    rnd = random.Random(seed)
    o.append(speck(seed, (cx - 0.4 * s, cy - 0.45 * s, cx + 0.4 * s, cy + 0.05 * s), ["#A8865A", "#3A2210"], int(s * 0.9), r=(0.3, s * 0.035), op=(0.4, 0.8)))
    o.append(f'<path d="M {F(cx)} {F(cy - 0.3 * s)} q {F(0.05 * s)} {F(-0.2 * s)} {F(0.16 * s)} {F(-0.26 * s)}" stroke="#4A3018" stroke-width="{F(max(1, s * 0.09))}" fill="none" stroke-linecap="round"/></g>')
    return "".join(o)


def pumpkin(uid, cx, cy, w, h, seed, body="#E8792E", dark="#B9531E", light="#F8A85A", stem="#6B5A2E", leaf="#6E8A3E", lit=(1, -1), rimcol=None, vine=True):
    """Gouache pumpkin: segmented ribs as separate washed lobes, curved rib strokes, shade crescent, dry-brush highlight, ink."""
    out = [shadow(cx + 2, cy + 0.5 * h, 0.56 * w, 0.08 * h, 0.2)]
    outline = blob(cx, cy, 0.56 * w, 0.5 * h, seed, 0.03, 22)
    lobes = [(-0.33, 0.24, 0.45, dark), (0.33, 0.24, 0.45, dark), (-0.17, 0.27, 0.5, body), (0.17, 0.27, 0.5, body), (0, 0.24, 0.52, body)]
    for k, (dx, rx, ry, col) in enumerate(lobes):
        out.append(wash(blob(cx + dx * w, cy, rx * w, ry * h, seed + k, 0.035, 16), col, seed + k, layers=2, spread=0.8, opacity=0.5))
    out.append(strokes(f"{uid}-st", outline, (cx - 0.6 * w, cy - 0.55 * h, cx + 0.6 * w, cy + 0.55 * h), [light, dark, lt(light, 0.4), dk(dark, 0.2)], seed,
                       n=int(w * 1.1), angle=-90, length=(0.12 * h, 0.4 * h), width=(0.012 * w, 0.03 * w), opacity=(0.18, 0.45), curve=0.15))
    for dx in (-0.27, -0.1, 0.1, 0.27):
        out.append(ink(f"M {F(cx + dx * w)} {F(cy - 0.44 * h)} Q {F(cx + dx * 1.45 * w)} {F(cy)} {F(cx + dx * w)} {F(cy + 0.47 * h)}", dark, max(1.1, 0.02 * w), seed + 7, 1, 0.6))
    out.append(shade(f"{uid}-sh", outline, dk(dark, 0.25), -lit[0], -lit[1] * 0.6, k=0.07 * w, op=0.38))
    hx = cx - lit[0] * 0.22 * w
    out.append(f'<path d="M {F(hx)} {F(cy - 0.3 * h)} Q {F(hx - lit[0] * 0.08 * w)} {F(cy - 0.02 * h)} {F(hx - lit[0] * 0.01 * w)} {F(cy + 0.24 * h)}" stroke="#FFE9C4" stroke-width="{F(max(1.5, 0.035 * w))}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    if rimcol:
        out.append(rim(f"{uid}-rm", outline, rimcol, lit[0], lit[1], k=max(1.2, 0.02 * w), op=0.7))
    out.append(ink(outline, mix(dark, INK, 0.4), max(1.1, 0.02 * w), seed + 3, 2, 0.5))
    sd = (f"M {F(cx - 0.07 * w)} {F(cy - 0.43 * h)} q {F(-0.03 * w)} {F(-0.2 * h)} {F(0.08 * w)} {F(-0.3 * h)} q {F(0.04 * w)} {F(-0.02 * h)} {F(0.08 * w)} {F(0.04 * h)} "
          f"q {F(-0.08 * w)} {F(0.1 * h)} {F(-0.03 * w)} {F(0.27 * h)} Z")
    out.append(f'<path d="{sd}" fill="{stem}"/><path d="{sd}" fill="none" stroke="{dk(stem, 0.4)}" stroke-width="{F(max(0.8, 0.012 * w))}"/>')
    out.append(f'<path d="M {F(cx - 0.02 * w)} {F(cy - 0.5 * h)} q {F(0.02 * w)} {F(-0.14 * h)} {F(0.07 * w)} {F(-0.2 * h)}" stroke="{lt(stem, 0.4)}" stroke-width="{F(max(0.8, 0.012 * w))}" fill="none" opacity="0.7"/>')
    if vine:
        out.append(ink(f"M {F(cx + 0.05 * w)} {F(cy - 0.5 * h)} q {F(0.18 * w)} {F(-0.12 * h)} {F(0.2 * w)} {F(-0.26 * h)} q {F(-0.01 * w)} {F(-0.08 * h)} {F(-0.08 * w)} {F(-0.05 * h)}", leaf, max(0.9, 0.012 * w), seed + 9, 1, 0.9))
        lf = blob(cx + 0.26 * w, cy - 0.52 * h, 0.13 * w, 0.065 * w, seed + 11, 0.12, 12, rot=-20)
        out.append(f'<path d="{lf}" fill="{leaf}"/><path d="M {F(cx + 0.15 * w)} {F(cy - 0.49 * h)} L {F(cx + 0.38 * w)} {F(cy - 0.57 * h)}" stroke="{dk(leaf, 0.4)}" stroke-width="{F(max(0.7, 0.01 * w))}"/>')
    return "".join(out)


def conifer_p(uid, x, base, h, seed, cols=("#2F5F48", "#1E4232", "#4C8460", "#7FAE84"), snow=None, width=0.34, lean=0.0, light=(-1, -0.3), ink_w=0.0):
    """Painted spruce: an irregular silhouette, then needle strokes in three tints following the drooping branches,
    a darker core, a lit edge and optional snow on the branch tops."""
    rnd = random.Random(seed)
    base_c, darkc, light_c, hi = cols
    levels = max(7, int(h / 6))
    left, right = [], []
    maxw = h * width / 2
    for i in range(levels + 1):
        t = i / levels
        y = base - h * 0.08 - t * h * 0.92
        cx = x + lean * t * h * 0.08
        w = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        step = h * 0.92 / levels
        left += [(cx - w, y), (cx - w * rnd.uniform(0.5, 0.75), y - step * 0.55)]
        w2 = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        right += [(cx + w2, y - step * 0.2), (cx + w2 * rnd.uniform(0.5, 0.75), y - step * 0.7)]
    tip = (x + lean * h * 0.08, base - h)
    pts = [(x - 1.5, base)] + left + [tip] + right[::-1] + [(x + 1.5, base)]
    d = poly(pts)
    box = bbox(pts)
    o = [f'<path d="M {F(x - h * 0.02)} {F(base - h * 0.25)} l {F(h * 0.04)} 0 l {F(h * 0.01)} {F(h * 0.25)} l {F(-h * 0.06)} 0 Z" fill="#4A3018"/>']
    o.append(f'<path d="{d}" fill="{base_c}"/>')
    # needle strokes: left half droops down-left, right half down-right
    n = int(h * width * 2.2)
    o.append(strokes(uid + "-l", d, (box[0], box[1], x + 2, box[3]), [darkc, light_c, base_c, hi], seed + 1, n=n, angle=150, length=(h * 0.05, h * 0.14), width=(0.5, max(1.2, h * 0.012)), opacity=(0.35, 0.75), curve=0.2))
    o.append(strokes(uid + "-r", d, (x - 2, box[1], box[2], box[3]), [darkc, light_c, base_c, hi], seed + 2, n=n, angle=30, length=(h * 0.05, h * 0.14), width=(0.5, max(1.2, h * 0.012)), opacity=(0.35, 0.75), curve=0.2))
    # dark trunk-side core
    core = poly([(x - maxw * 0.22, base), (x - maxw * 0.08, base - h * 0.6), (x, base - h * 0.9), (x + maxw * 0.08, base - h * 0.6), (x + maxw * 0.22, base)])
    o.append(f'<path d="{core}" fill="{darkc}" opacity="0.35"/>')
    o.append(rim(uid + "-rm", d, hi, light[0], light[1], k=max(1.2, h * 0.012), op=0.55))
    if snow:
        sn = []
        rnd2 = random.Random(seed + 9)
        for i in range(0, len(left) - 1, 2):
            lx, ly = left[i]
            w = abs(lx - x)
            for sg, pxs in ((-1, left), (1, right)):
                px, py = pxs[i]
                L = abs(px - x)
                if L < 4:
                    continue
                a = (x + sg * L * 0.18, py - L * 0.16 - rnd2.uniform(0, 2))
                b = (px, py)
                sn.append(f"M {F(a[0])} {F(a[1])} Q {F((a[0] + b[0]) / 2)} {F(min(a[1], b[1]) - L * 0.1)} {F(b[0])} {F(b[1])}")
        o.append(f'<path d="{" ".join(sn)}" stroke="{snow[1]}" stroke-width="{F(max(2.6, h * 0.028))}" fill="none" stroke-linecap="round" opacity="0.9" transform="translate(0 1.2)"/>')
        o.append(f'<path d="{" ".join(sn)}" stroke="{snow[0]}" stroke-width="{F(max(2.2, h * 0.024))}" fill="none" stroke-linecap="round"/>')
    if ink_w:
        o.append(ink(d, darkc, ink_w, seed + 3, 1, 0.5))
    return "".join(o)


def crow(uid, x, y, s=1.0, flip=False, seed=5, rimcol="#9C8CC8"):
    """Crow in profile standing at (x, y) (feet), facing left; glossy black with a lavender rim light."""
    def p(px, py):
        return (x + (-px if flip else px) * s, y + py * s)
    body = [p(-16, -14), p(-10, -22), p(2, -25), p(12, -21), p(18, -12), p(14, -6), p(0, -2), p(-10, -4)]
    bd = smooth_closed(body)
    tail = smooth_closed([p(12, -14), p(30, -10), p(34, -4), p(28, -3), p(12, -6)])
    head = smooth_closed([p(-14, -22), p(-10, -31), p(-2, -32), p(4, -28), p(2, -22), p(-6, -19)])
    beak = poly([p(-14, -29), p(-28, -25), p(-14, -22)])
    o = [f'<path d="{tail}" fill="#1E1A28"/>' + ink(tail, "#0C0A12", 0.8 * s, seed, 1, 0.6)]
    o.append(paint(uid, bd, bbox(body), "#23202E", seed, tints=["#3A3650", "#121018", "#4E4A6A"], angle=-30, n=int(26 * s), ink_col="#0C0A12", ink_w=1.0 * s, length=(3 * s, 9 * s), width=(0.4, 1.2 * s)))
    o.append(f'<path d="{smooth_open([p(-6, -19), p(6, -18), p(14, -10)])}" stroke="#4E4A6A" stroke-width="{F(1.1 * s)}" fill="none" opacity="0.8"/>')
    o.append(f'<path d="{head}" fill="#23202E"/>' + ink(head, "#0C0A12", 0.9 * s, seed + 1, 1, 0.6))
    o.append(f'<path d="{beak}" fill="#2A2630" stroke="#0C0A12" stroke-width="{F(0.7 * s)}" stroke-linejoin="round"/>')
    o.append(rim(uid + "-r", bd + " " + head, rimcol, 0.3, -1, k=1.0 * s, op=0.55))
    ex, ey = p(-8, -27)
    o.append(f'<circle cx="{F(ex)}" cy="{F(ey)}" r="{F(1.5 * s)}" fill="#F0E6C8"/><circle cx="{F(ex + 0.3 * s)}" cy="{F(ey)}" r="{F(0.8 * s)}" fill="#000"/>')
    o.append(f'<g stroke="#2A2630" stroke-width="{F(1.5 * s)}" stroke-linecap="round" fill="none"><path d="M {F(p(-4, -3)[0])} {F(p(-4, -3)[1])} l {F(-1 * s)} {F(4 * s)} m 0 0 l {F(-3 * s)} 0 m {F(3 * s)} 0 l {F(3 * s)} 0"/>'
             f'<path d="M {F(p(4, -3)[0])} {F(p(4, -3)[1])} l {F(0)} {F(4 * s)} m 0 0 l {F(-3 * s)} 0 m {F(3 * s)} 0 l {F(3 * s)} 0"/></g>')
    return "".join(o)


def leaf_fly(uid, cx, cy, s, fill, dark, rot_, seed):
    return maple(uid, cx, cy, s, fill, dark, rot_=rot_, seed=seed)


# ================================================================ FALL: scarecrow at a fence, golden hour
PLAID_ID = None


def plaid(uid, a="#B8432E", b="#7E2A1E", c="#F2C46A", size=18, rot_=6):
    return (f'<pattern id="{uid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" patternTransform="rotate({rot_})">'
            f'<rect width="{size}" height="{size}" fill="{a}"/><rect width="{size}" height="{size * 0.32:.1f}" y="{size * 0.34:.1f}" fill="{b}" opacity="0.75"/>'
            f'<rect width="{size * 0.32:.1f}" height="{size}" x="{size * 0.34:.1f}" fill="{b}" opacity="0.65"/><rect width="{size}" height="1.4" y="{size * 0.1:.1f}" fill="{c}" opacity="0.7"/>'
            f'<rect width="1.4" height="{size}" x="{size * 0.82:.1f}" fill="{c}" opacity="0.7"/></pattern>')


def straw_bunch(x, y, ang, n, seed, L=(10, 24), w=2.0, cols=("#E6C26A", "#D2A24A", "#F2D88A", "#B88A34")):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a = math.radians(ang + rnd.uniform(-28, 28))
        ln = rnd.uniform(*L)
        sx, sy = x + rnd.uniform(-3, 3), y + rnd.uniform(-3, 3)
        out.append(f'<path d="M {F(sx)} {F(sy)} q {F(math.cos(a) * ln * 0.5 + rnd.uniform(-3, 3))} {F(math.sin(a) * ln * 0.5 + rnd.uniform(-2, 4))} {F(math.cos(a) * ln)} {F(math.sin(a) * ln)}" stroke="{rnd.choice(cols)}"/>')
    return f'<g fill="none" stroke-width="{w}" stroke-linecap="round">' + "".join(out) + "</g>"


def barn(uid, x, y, w, haze=0.0):
    """Small gambrel-roof barn seen from the front-left, hazy with distance (haze 0..1 toward the sky colour)."""
    def c(col):
        return mix(col, "#E9C9A0", haze)
    h = w * 0.55
    body = poly([(x, y), (x + w, y), (x + w, y - h * 0.55), (x + w * 0.5, y - h * 0.55), (x, y - h * 0.55)])
    gable = poly([(x + w * 0.05, y - h * 0.55), (x + w * 0.95, y - h * 0.55), (x + w * 0.88, y - h * 0.8), (x + w * 0.5, y - h), (x + w * 0.12, y - h * 0.8)])
    o = [f'<path d="{body}" fill="{c("#9E3A2E")}"/><path d="{gable}" fill="{c("#B04A3A")}"/>']
    o.append(f'<path d="M {F(x + w * 0.02)} {F(y - h * 0.55)} L {F(x + w * 0.12)} {F(y - h * 0.82)} L {F(x + w * 0.5)} {F(y - h * 1.03)} L {F(x + w * 0.88)} {F(y - h * 0.82)} L {F(x + w * 0.98)} {F(y - h * 0.55)}" stroke="{c("#5A2A22")}" stroke-width="{F(max(1.2, w * 0.03))}" fill="none" stroke-linejoin="round"/>')
    o.append(f'<path d="{poly([(x + w * 0.36, y), (x + w * 0.64, y), (x + w * 0.64, y - h * 0.4), (x + w * 0.36, y - h * 0.4)])}" fill="{c("#5A2A22")}"/>')
    o.append(f'<path d="M {F(x + w * 0.36)} {F(y - h * 0.4)} L {F(x + w * 0.64)} {F(y)} M {F(x + w * 0.64)} {F(y - h * 0.4)} L {F(x + w * 0.36)} {F(y)} M {F(x + w * 0.5)} {F(y - h * 0.4)} l 0 {F(h * 0.4)}" stroke="{c("#F2E2C8")}" stroke-width="{F(max(0.9, w * 0.018))}" opacity="0.8"/>')
    o.append(f'<rect x="{F(x + w * 0.42)}" y="{F(y - h * 0.86)}" width="{F(w * 0.16)}" height="{F(w * 0.16)}" fill="{c("#F7D98A")}" stroke="{c("#F2E2C8")}" stroke-width="{F(max(0.8, w * 0.015))}"/>')
    o.append(f'<path d="M {F(x + w * 0.46)} {F(y - h)} l {F(w * 0.08)} 0 l 0 {F(-w * 0.1)} l {F(-w * 0.08)} 0 Z" fill="{c("#5A2A22")}"/>')
    o.append(f'<path d="M {F(x + w * 0.06)} {F(y - h * 0.5)} L {F(x + w * 0.06)} {F(y)} M {F(x + w * 0.2)} {F(y - h * 0.52)} L {F(x + w * 0.2)} {F(y)} M {F(x + w * 0.8)} {F(y - h * 0.52)} L {F(x + w * 0.8)} {F(y)} M {F(x + w * 0.94)} {F(y - h * 0.5)} L {F(x + w * 0.94)} {F(y)}" stroke="{c("#7A2E26")}" stroke-width="{F(max(0.7, w * 0.012))}" opacity="0.6"/>')
    return "".join(o)


def fence(uid, posts, rails, seed=4, col="#8A6A48", dark="#5E4430", light="#C9A878", pw=9):
    """Weathered wooden fence. posts: list of (x, top, bottom); rails: list of ((x0, y0), (x1, y1), thickness) in order."""
    o = []
    rnd = random.Random(seed)
    for k, ((x0, y0), (x1, y1), t) in enumerate(rails):
        pts = [(x0, y0 - t / 2), (x1, y1 - t / 2), (x1, y1 + t / 2), (x0, y0 + t / 2)]
        d = poly(jitter(pts, seed + k, 0.6))
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        o.append(paint(f"{uid}-r{k}", d, bbox(pts), col, seed + k, tints=[dark, light, lt(col, 0.15), "#A88A62"], angle=ang, n=int(abs(x1 - x0) * 0.35), length=(10, 36), width=(0.5, 1.5), op=(0.3, 0.6), ink_col=dark, ink_w=1.2, curve=0.05))
        o.append(shade(f"{uid}-rs{k}", d, dark, 0, -1, k=t * 0.3, op=0.35))
        o.append(f'<path d="M {F(x0)} {F(y0 - t * 0.3)} L {F(x1)} {F(y1 - t * 0.3)}" stroke="{lt(light, 0.3)}" stroke-width="1.2" opacity="0.6"/>')
    for k, (x, top, bot) in enumerate(posts):
        pts = [(x - pw / 2, top), (x + pw / 2, top + 1), (x + pw / 2 + 1, bot), (x - pw / 2 - 1, bot)]
        d = poly(jitter(pts, seed + 20 + k, 0.7))
        o.append(shadow(x + 6, bot, pw * 1.6, 2.5, 0.2))
        o.append(paint(f"{uid}-p{k}", d, bbox(pts), dk(col, 0.1), seed + 20 + k, tints=[dark, light, "#A88A62"], angle=-88, n=int((bot - top) * 0.5), length=(8, 30), width=(0.5, 1.6), op=(0.3, 0.6), ink_col=dark, ink_w=1.3, curve=0.05))
        o.append(shade(f"{uid}-ps{k}", d, dark, -1, 0, k=pw * 0.3, op=0.4))
        o.append(f'<path d="M {F(x - pw / 2)} {F(top)} L {F(x + pw / 2)} {F(top + 1)}" stroke="{lt(light, 0.4)}" stroke-width="2" opacity="0.7"/>')
        for _ in range(2):
            yy = rnd.uniform(top + 8, bot - 8)
            o.append(f'<path d="M {F(x - pw / 2 + 1)} {F(yy)} l {F(pw * 0.6)} {F(rnd.uniform(-1, 1))}" stroke="{dark}" stroke-width="0.8" opacity="0.5"/>')
    return "".join(o)


def scarecrow_fig(u, cx, base):
    """Scarecrow leaning on the top rail: torso tipped left, left sleeve draped over the rail, right arm out on the
    crossbar, head tilted, straw blowing left. (cx, base) = where the pole meets the ground line; light from upper right."""
    o = []
    rnd = random.Random(8)
    tilt = -7
    def R(pts):
        return rpts(pts, cx, base - 80, tilt)
    # pole + crossbar (mostly hidden)
    o.append(f'<path d="M {F(cx - 4)} {F(base)} L {F(cx + 4)} {F(base)} L {F(cx + 3)} {F(base - 180)} L {F(cx - 3)} {F(base - 180)} Z" fill="#6E4A2A" transform="rotate({tilt} {F(cx)} {F(base - 80)})"/>')
    # legs: denim overalls, straw at the cuffs, the pole runs behind
    legs = R([(cx - 24, base - 92), (cx + 26, base - 92), (cx + 30, base - 30), (cx + 10, base - 26), (cx + 2, base - 62), (cx - 6, base - 26), (cx - 28, base - 30)])
    ld = smooth_closed(legs)
    for lx in (cx - 16, cx + 20):
        o.append(straw_bunch(lx, base - 30, 95, 10, 31 + int(lx), L=(8, 18), w=2))
    o.append(paint(u + "-lg", ld, bbox(legs), "#3E5E88", 12, tints=["#2E4A70", "#6A8AB4", "#5A7AA4", "#8EAACB"], angle=-90 + tilt, n=90, length=(8, 26), width=(0.6, 2), op=(0.25, 0.5), ink_col="#22344E", ink_w=1.5))
    o.append(shade(u + "-lgs", ld, "#1E3050", -1, 0.2, k=7, op=0.4))
    o.append(f'<path d="M {F(cx + 1)} {F(base - 62)} L {F(cx + 3)} {F(base - 92)}" stroke="#22344E" stroke-width="2" stroke-linecap="round" opacity="0.7" transform="rotate({tilt} {F(cx)} {F(base - 80)})"/>')
    # torso: plaid shirt with folds, then the overall bib
    o.append(f'<defs>{plaid(u + "-pl")}</defs>')
    torso = R([(cx - 30, base - 160), (cx + 30, base - 162), (cx + 36, base - 120), (cx + 32, base - 90), (cx - 28, base - 88), (cx - 34, base - 122)])
    td = smooth_closed(torso)
    o.append(f'<path d="{td}" fill="url(#{u}-pl)"/>')
    # right arm (viewer's right) along the crossbar, slightly up; left arm dropped over the rail
    ra = R([(cx + 24, base - 158), (cx + 70, base - 150), (cx + 110, base - 136), (cx + 112, base - 122), (cx + 70, base - 128), (cx + 26, base - 134)])
    la = R([(cx - 26, base - 158), (cx - 64, base - 150), (cx - 88, base - 120), (cx - 100, base - 86), (cx - 80, base - 82), (cx - 68, base - 112), (cx - 50, base - 134), (cx - 26, base - 134)])
    rad, lad = smooth_closed(ra), smooth_closed(la)
    o.append(straw_bunch(*R([(cx + 112, base - 129)])[0], 10, 14, 41, L=(12, 26), w=2.2))
    # the forearm hangs down in front of the rail: drawn later (returned separately)
    fa_pts = [(cx - 98, base - 90), (cx - 78, base - 84), (cx - 74, base - 50), (cx - 80, base - 36), (cx - 102, base - 38), (cx - 104, base - 56)]
    fad = smooth_closed(fa_pts)
    fore = [straw_bunch(cx - 92, base - 36, 100, 14, 42, L=(10, 24), w=2.2), f'<path d="{fad}" fill="url(#{u}-pl)"/>',
            strokes(f"{u}-ff", fad, bbox(fa_pts), ["#5A1A12", "#F2C46A", "#8E2E22"], 57, n=30, angle=-85, length=(6, 18), width=(0.6, 2), opacity=(0.12, 0.3), curve=0.3),
            shade(f"{u}-fs", fad, "#4A140E", -1, 0.4, k=5, op=0.4), rim(f"{u}-fr", fad, "#FFD88A", 1, -0.4, k=1.4, op=0.4), ink(fad, "#5A2216", 1.5, 58, 2, 0.6),
            shadow(cx - 88, base - 36, 16, 3, 0.2)]
    for ad, pts, k in ((rad, ra, 0), (lad, la, 1)):
        o.append(f'<path d="{ad}" fill="url(#{u}-pl)"/>')
        o.append(strokes(f"{u}-af{k}", ad, bbox(pts), ["#5A1A12", "#F2C46A", "#8E2E22"], 50 + k, n=50, angle=-10 - k * 70, length=(6, 20), width=(0.6, 2.2), opacity=(0.12, 0.3), curve=0.3))
        o.append(shade(f"{u}-as{k}", ad, "#4A140E", 0, 1, k=5, op=0.4))
        o.append(rim(f"{u}-ar{k}", ad, "#FFD88A", 0.6, -1, k=1.6, op=0.45))
        o.append(ink(ad, "#5A2216", 1.5, 60 + k, 2, 0.6))
    # fold strokes on the torso and the shade down the left side
    o.append(strokes(u + "-tf", td, bbox(torso), ["#5A1A12", "#F2C46A", "#8E2E22"], 52, n=60, angle=-80, length=(8, 26), width=(0.6, 2.4), opacity=(0.12, 0.3), curve=0.3))
    o.append(shade(u + "-ts", td, "#4A140E", -1, 0.3, k=7, op=0.4))
    o.append(rim(u + "-tr", td, "#FFD88A", 1, -0.6, k=1.6, op=0.45))
    o.append(ink(td, "#5A2216", 1.5, 53, 2, 0.6))
    bib = R([(cx - 18, base - 128), (cx + 20, base - 128), (cx + 26, base - 86), (cx - 24, base - 86)])
    bd = smooth_closed(bib)
    o.append(paint(u + "-bib", bd, bbox(bib), "#4A6E9A", 14, tints=["#2E4A70", "#6A8AB4", "#8EAACB"], angle=-88 + tilt, n=40, length=(6, 18), width=(0.6, 1.8), op=(0.25, 0.5), ink_col="#22344E", ink_w=1.3))
    o.append(shade(u + "-bs", bd, "#1E3050", -1, 0.2, k=5, op=0.35))
    for sx, sy in R([(cx - 16, base - 128), (cx + 18, base - 128)]):
        o.append(f'<circle cx="{F(sx)}" cy="{F(sy + 4)}" r="3.4" fill="#E2C27A" stroke="#8A6A2A" stroke-width="0.8"/>')
    s1, s2 = R([(cx - 16, base - 126), (cx + 18, base - 126)])
    t1, t2 = R([(cx - 22, base - 160), (cx + 24, base - 162)])
    o.append(f'<path d="M {F(s1[0])} {F(s1[1])} L {F(t1[0])} {F(t1[1])} M {F(s2[0])} {F(s2[1])} L {F(t2[0])} {F(t2[1])}" stroke="#3E5E88" stroke-width="7" stroke-linecap="round"/>'
             f'<path d="M {F(s1[0])} {F(s1[1])} L {F(t1[0])} {F(t1[1])} M {F(s2[0])} {F(s2[1])} L {F(t2[0])} {F(t2[1])}" stroke="#22344E" stroke-width="1" opacity="0.5" transform="translate(-3 0)"/>')
    px, py = R([(cx + 8, base - 70)])[0]
    o.append(f'<g transform="rotate(-8 {F(px)} {F(py)})"><rect x="{F(px - 9)}" y="{F(py - 8)}" width="18" height="16" rx="2" fill="#D98A3A"/>'
             f'<rect x="{F(px - 9)}" y="{F(py - 8)}" width="18" height="16" rx="2" fill="none" stroke="#7A3A12" stroke-width="1" stroke-dasharray="2.2 2"/></g>')
    # straw at the collar
    hx, hy = R([(cx - 2, base - 182)])[0]
    o.append(straw_bunch(hx, hy + 16, -150, 16, 43, L=(8, 20), w=2))
    # burlap head, tilted a little more than the body
    hy += 6
    head = blob(hx, hy, 26, 28, 21, 0.045, rot=tilt - 4)
    o.append(wash(head, "#D9B98A", 7, 2, 0.8, 0.5))
    o.append(strokes(u + "-bu", head, (hx - 34, hy - 36, hx + 34, hy + 36), ["#B8945E", "#F0D8AA", "#A07A48"], 9, n=60, angle=tilt - 4, length=(6, 16), width=(0.4, 1.0), opacity=(0.4, 0.8)))
    o.append(strokes(u + "-bu2", head, (hx - 34, hy - 36, hx + 34, hy + 36), ["#B8945E", "#A07A48"], 10, n=40, angle=tilt - 94, length=(6, 16), width=(0.4, 1.0), opacity=(0.3, 0.6)))
    o.append(shade(u + "-hs", head, "#8A6238", -1, 0.4, k=7, op=0.4))
    o.append(rim(u + "-hr", head, "#FFE6B0", 1, -0.6, k=2, op=0.6))
    o.append(ink(head, "#7A5A32", 1.6, 8, 2, 0.6))
    # face: stitched smile, button eyes (one bigger), rosy patches, a patch on the cheek
    e1, e2, m0, m1, m2 = rpts([(hx - 10, hy - 4), (hx + 10, hy - 5), (hx - 11, hy + 9), (hx, hy + 15), (hx + 11, hy + 8)], hx, hy, tilt - 4)
    o.append(f'<circle cx="{F(e1[0])}" cy="{F(e1[1])}" r="4.6" fill="#2A1A10"/><circle cx="{F(e2[0])}" cy="{F(e2[1])}" r="4.2" fill="#2A1A10"/>'
             f'<circle cx="{F(e1[0] - 1.2)}" cy="{F(e1[1] - 1.4)}" r="1.3" fill="#FFF"/><circle cx="{F(e2[0] - 1.2)}" cy="{F(e2[1] - 1.4)}" r="1.2" fill="#FFF"/>'
             f'<path d="M {F(e1[0] - 2)} {F(e1[1] - 1)} l 4 2 M {F(e1[0] - 2)} {F(e1[1] + 1)} l 4 -2 M {F(e2[0] - 2)} {F(e2[1] - 1)} l 4 2 M {F(e2[0] - 2)} {F(e2[1] + 1)} l 4 -2" stroke="#D9B98A" stroke-width="0.9"/>')
    o.append(f'<circle cx="{F(e1[0] - 5)}" cy="{F(e1[1] + 11)}" r="5" fill="#E8836A" opacity="0.4"/><circle cx="{F(e2[0] + 5)}" cy="{F(e2[1] + 11)}" r="5" fill="#E8836A" opacity="0.4"/>')
    o.append(f'<path d="M {F(m0[0])} {F(m0[1])} Q {F(m1[0])} {F(m1[1])} {F(m2[0])} {F(m2[1])}" stroke="#3A2418" stroke-width="2" fill="none" stroke-linecap="round"/>')
    for t in (0.2, 0.4, 0.6, 0.8):
        qx = (1 - t) ** 2 * m0[0] + 2 * (1 - t) * t * m1[0] + t * t * m2[0]
        qy = (1 - t) ** 2 * m0[1] + 2 * (1 - t) * t * m1[1] + t * t * m2[1]
        o.append(f'<path d="M {F(qx)} {F(qy - 3)} l 0 6" stroke="#3A2418" stroke-width="1.4"/>')
    px2, py2 = rot(hx + 14, hy + 12, hx, hy, tilt - 4)
    o.append(f'<path d="{blob(px2, py2, 6, 5, 4, 0.1, 8, rot=20)}" fill="#C9A26A"/><path d="{blob(px2, py2, 6, 5, 4, 0.1, 8, rot=20)}" fill="none" stroke="#7A5A32" stroke-width="0.8" stroke-dasharray="1.8 1.6"/>')
    # straw hat: wide brim, dented crown, ribbon band, a leaf tucked in
    hb = rpts([(hx - 44, hy - 20), (hx - 20, hy - 30), (hx + 24, hy - 32), (hx + 48, hy - 22), (hx + 38, hy - 14), (hx, hy - 11), (hx - 36, hy - 12)], hx, hy, tilt - 2)
    hc = rpts([(hx - 24, hy - 26), (hx - 22, hy - 48), (hx - 9, hy - 60), (hx + 9, hy - 56), (hx + 22, hy - 60), (hx + 26, hy - 28)], hx, hy, tilt - 2)
    brim, crown = smooth_closed(hb), smooth_closed(hc)
    o.append(shadow(hx, hy - 16, 40, 6, 0.25))
    o.append(wash(crown, "#D9A84E", 11, 2, 0.6, 0.5) + wash(brim, "#E6BC62", 12, 2, 0.6, 0.5))
    o.append(strokes(u + "-hat", crown + " " + brim, bbox(hb + hc), ["#B8862E", "#F6D88A", "#A87628", "#FFF0C0"], 13, n=110, angle=tilt - 4, length=(6, 20), width=(0.4, 1.3), opacity=(0.35, 0.75)))
    o.append(shade(u + "-hcs", crown, "#8A5A22", -1, 0.3, k=6, op=0.4) + shade(u + "-hbs", brim, "#8A5A22", 0, 1, k=3, op=0.4))
    o.append(rim(u + "-hcr", crown, "#FFF0C0", 1, -0.6, k=1.8, op=0.6))
    band = rpts([(hx - 23, hy - 34), (hx, hy - 29), (hx + 25, hy - 35), (hx + 25, hy - 42), (hx, hy - 36), (hx - 23, hy - 41)], hx, hy, tilt - 2)
    o.append(f'<path d="{smooth_closed(band)}" fill="#7E2A1E"/>' + shade(u + "-bds", smooth_closed(band), "#4A140E", -1, 0, k=5, op=0.4))
    o.append(ink(crown, "#8A5A22", 1.5, 14, 2, 0.6) + ink(brim, "#8A5A22", 1.5, 15, 2, 0.6))
    lx, ly = rot(hx + 20, hy - 40, hx, hy, tilt - 2)
    o.append(maple(u + "-hl", lx, ly, 8, "#E8792E", "#B9531E", rot_=30, seed=3))
    return "".join(o), (hx, hy), "".join(fore)


def fall_scene(u="fa"):
    o = []
    # --- vignette: golden-hour sky, low sun at the right, hazy hills, a distant barn, a golden field
    back = [sky_rect(u + "-sky", [(0, "#B9A6C8", 1), (0.3, "#E8C09A", 1), (0.6, "#F6D58C", 1), (0.72, "#F3C266", 1), (1, "#C98A3A", 1)], (0, 0, 380, 330))]
    back.append(f'<defs>{rgrad(u + "-sun", 330, 150, 150, [(0, "#FFF4CC", 0.95), (0.25, "#FFE08A", 0.7), (0.6, "#F6B85A", 0.25), (1, "#F6B85A", 0)])}</defs><circle cx="330" cy="150" r="150" fill="url(#{u}-sun)"/>')
    back.append(f'<circle cx="330" cy="154" r="20" fill="#FFF8DC" opacity="0.9"/>')
    # cloud wisps
    for k, (x, y, w) in enumerate(((60, 60, 90), (190, 42, 70), (250, 96, 110), (90, 120, 80))):
        back.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="{w / 14}" fill="#FFE9C8" opacity="0.5"/><ellipse cx="{x + w * 0.2}" cy="{y - 3}" rx="{w / 3}" ry="{w / 16}" fill="#FFF4E0" opacity="0.6"/>')
    far, _ = ridge([(0, 192), (70, 180), (150, 188), (230, 176), (300, 186), (380, 178)], 3, 330, amp=5)
    back.append(f'<path d="{far}" fill="#C9A8A0" opacity="0.75"/>')
    near, line = ridge([(0, 208), (80, 200), (160, 206), (240, 198), (330, 204), (380, 200)], 5, 330, amp=4)
    back.append(f'<path d="{near}" fill="#C9A26A"/>')
    # tree line on the ridge and the barn
    rnd = random.Random(7)
    tl = []
    for x in range(-6, 390, 9):
        yy = 203 + 3 * math.sin(x * 0.07)
        h = rnd.uniform(9, 18)
        tl.append(f'<path d="{blob(x, yy - h * 0.5, rnd.uniform(5, 8), h * 0.55, int(x) + 1, 0.12, 10)}" fill="{rnd.choice(["#A8703E", "#B9802E", "#9A5A2E", "#C9903A"])}" opacity="0.9"/>')
    back.append("".join(tl))
    back.append(barn(u + "-barn", 54, 206, 58, haze=0.25))
    back.append(f'<path d="M 62 206 L 42 206 L 46 200 Z M 120 206 l 14 0 l -3 -6 Z" fill="#9A6A3E" opacity="0.6"/>')
    # field: warm gold wash with horizontal strokes, greener and darker toward the foreground
    field = poly([(0, 206), (380, 203), (380, 330), (0, 330)])
    back.append(f'<path d="{field}" fill="#D9A64A"/>')
    back.append(f'<defs>{lgrad(u + "-fg", 0, 206, 0, 330, [(0, "#F2CF7A", 0.9), (0.35, "#C9933A", 0.3), (1, "#8A5A24", 0.7)])}</defs><rect x="0" y="206" width="380" height="124" fill="url(#{u}-fg)"/>')
    back.append(hstrokes(u + "-fs", field, (0, 206, 380, 330), ["#E6BC62", "#B8862E", "#F6D88A", "#A8742A", "#8E9A4E"], 21, n=190, angle=-2, length=(10, 40), width=(0.8, 2.6), op=(0.2, 0.45)))
    back.append(grass_tufts(22, (0, 212, 380, 236), ["#B8862E", "#D9A84E", "#8E9A4E"], n=80, h=(3, 8), sw=1.1))
    o.append(vignette(u + "-v", "".join(back), [(200, 190, 186, 128, 0.42), (280, 220, 105, 100, 0.4), (110, 240, 108, 78, 0.35), (230, 110, 120, 90, 0.3)]))
    # --- fence receding from the left foreground to the right
    posts = [(44, 222, 300), (184, 208, 276), (326, 196, 254)]
    rails = [((8, 250), (378, 214), 9), ((8, 278), (378, 236), 8)]
    o.append(fence(u + "-fn", [posts[2]], [], seed=4))
    # scarecrow stands behind the fence near the middle post
    fig, (hx, hy), fore = scarecrow_fig(u + "-sc", 262, 290)
    o.append(fig)
    o.append(crow(u + "-cr", hx + 28, hy - 32, s=1.0, seed=5))
    o.append(fence(u + "-fn2", posts[:2], rails, seed=6))
    o.append(fore)
    # --- foreground: pumpkins and gourds at the fence foot, long grass, fallen leaves
    o.append(grass_tufts(23, (0, 284, 380, 316), ["#A8742A", "#C9933A", "#7A8A3E", "#E6BC62"], n=70, h=(8, 18), sw=1.4))
    o.append(pumpkin(u + "-p1", 112, 288, 98, 66, 41, lit=(1, -1)))
    o.append(pumpkin(u + "-p2", 196, 300, 62, 42, 43, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF", stem="#6B5A2E", lit=(1, -1)))
    o.append(pumpkin(u + "-p3", 46, 306, 50, 36, 44, body="#E2A23A", dark="#B87A1E", light="#F6CE6A", lit=(1, -1), vine=False))
    o.append(pumpkin(u + "-p4", 254, 306, 44, 30, 45, body="#7E9A4E", dark="#5A7432", light="#B8CC7A", lit=(1, -1), vine=False))
    o.append(grass_tufts(24, (0, 310, 380, 326), ["#8A5A24", "#C9933A", "#6E7A32"], n=50, h=(5, 12), sw=1.5))
    o.append(acorn_p(u + "-ac", 160, 316, 12, rot_=20) + oak_leaf(u + "-ol", 300, 318, 11, "#B8862E", "#7A5418", rot_=70, seed=6))
    o.append(maple(u + "-ml1", 232, 322, 10, "#C9442E", "#8E2A1A", rot_=-40, seed=7) + maple(u + "-ml2", 20, 324, 9, "#E8792E", "#B9531E", rot_=110, seed=8))
    # --- wind: maple leaves in the air, blowing to the left
    for k, (x, y, s, c, d, r) in enumerate(((150, 92, 10, "#E8792E", "#B9531E", -30), (96, 128, 8, "#C9442E", "#8E2A1A", 40), (60, 86, 7, "#E2A23A", "#A8701A", -70),
                                            (320, 60, 9, "#C9442E", "#8E2A1A", 20), (350, 120, 7, "#E8792E", "#B9531E", 80), (200, 48, 7, "#D98A3A", "#9A5A1E", -100),
                                            (24, 170, 6, "#E8792E", "#B9531E", 60), (300, 180, 6, "#E2A23A", "#A8701A", -50))):
        o.append(maple(f"{u}-fl{k}", x, y, s, c, d, rot_=r, seed=10 + k))
    return "".join(o)


def fall_garland(u="fg"):
    """Seamless 320 x 74: jute twine with painted maple and oak leaves, acorns and bittersweet berries hanging from it,
    each with a soft cast shadow."""
    o = []
    d = "M 0 10 C 80 34 240 34 320 10"
    o.append(f'<path d="{d}" stroke="#6E4E2E" stroke-width="3" fill="none" opacity="0.9"/><path d="{d}" stroke="#C9A878" stroke-width="1.1" fill="none" stroke-dasharray="2.5 3.5"/>')
    items = [(22, "maple", "#E8792E", "#B9531E", 17), (66, "oak", "#B8862E", "#7A5418", 15), (104, "acorn", None, None, 13), (140, "maple", "#C9442E", "#8E2A1A", 16),
             (186, "berries", None, None, 10), (222, "maple", "#E2A23A", "#A8701A", 16), (262, "oak", "#8A9A3E", "#5A6A22", 14), (298, "acorn", None, None, 12)]
    for k, (x, kind, c, dd, s) in enumerate(items):
        y = swag_y(x)
        tilt = (-1) ** k * 10
        def item(xx, kind=kind, c=c, dd=dd, s=s, y=y, k=k, tilt=tilt):
            out = [f'<path d="M {F(xx)} {F(y)} q {F(tilt * 0.1)} 5 {F(tilt * 0.15)} 9" stroke="#6E4E2E" stroke-width="1.1" fill="none"/>']
            cx, cy = xx + tilt * 0.15, y + 9
            if kind == "maple":
                out.append(f'<g opacity="0.18" transform="translate(2 3)">{maple(f"{u}-sh{k}", cx, cy + s, s, INK, INK, rot_=180 + tilt, seed=k, light=INK)}</g>')
                out.append(maple(f"{u}-m{k}", cx, cy + s, s, c, dd, rot_=180 + tilt, seed=k))
            elif kind == "oak":
                out.append(f'<g opacity="0.18" transform="translate(2 3)">{oak_leaf(f"{u}-sho{k}", cx, cy + s * 0.9, s, INK, INK, rot_=180 + tilt, seed=k)}</g>')
                out.append(oak_leaf(f"{u}-o{k}", cx, cy + s * 0.9, s, c, dd, rot_=180 + tilt, seed=k))
            elif kind == "acorn":
                out.append(f'<ellipse cx="{F(cx + 2)}" cy="{F(cy + s * 0.5 + 3)}" rx="{F(s * 0.5)}" ry="{F(s * 0.6)}" fill="{INK}" opacity="0.15"/>')
                out.append(acorn_p(f"{u}-a{k}", cx, cy + s * 0.2, s, rot_=180 + tilt, seed=k))
            else:  # bittersweet: a twig with orange berries
                out.append(f'<path d="M {F(cx)} {F(cy - 4)} q 2 10 -3 18 M {F(cx)} {F(cy + 4)} q 6 2 9 8" stroke="#6E4E2E" stroke-width="1.3" fill="none" stroke-linecap="round"/>')
                for bx, by in ((cx - 3, cy + 14), (cx + 3, cy + 9), (cx + 9, cy + 12), (cx - 1, cy + 20), (cx + 6, cy + 18)):
                    out.append(f'<circle cx="{F(bx + 1)}" cy="{F(by + 1.5)}" r="3.4" fill="{INK}" opacity="0.15"/><circle cx="{F(bx)}" cy="{F(by)}" r="3.2" fill="#E8692E"/>'
                               f'<circle cx="{F(bx)}" cy="{F(by)}" r="3.2" fill="none" stroke="#8E2A1A" stroke-width="0.7" opacity="0.7"/><circle cx="{F(bx - 1)}" cy="{F(by - 1)}" r="0.9" fill="#FFE2B8" opacity="0.8"/>')
            return "".join(out)
        o.append(wrap(item, x, 26))
    return "".join(o)


def fall_particles():
    """-> dict name -> body (40 x 40)."""
    return {"fall-leaf1": maple("pl1", 20, 19, 15, "#E8792E", "#B9531E", rot_=-12, seed=1),
            "fall-leaf2": maple("pl2", 20, 19, 15, "#C9442E", "#8E2A1A", rot_=10, seed=2),
            "fall-leaf3": maple("pl3", 20, 19, 15, "#E2A23A", "#A8701A", rot_=-30, seed=3),
            "fall-leaf4": oak_leaf("pl4", 20, 18, 15, "#B8862E", "#7A5418", rot_=20, seed=4)}


# ================================================================ HALLOWEEN: porch steps, jack-o'-lanterns, cat, moon
BAT = "#241C34"
LAV = "#A898D0"


def bat_p(uid, cx, cy, s, rot_=0, flap=0.0, seed=1, rimcol=LAV, eyes=True, body=BAT):
    """Painted bat, wings spread: scalloped membranes with finger bones, furry body, a moonlit rim. s = half wingspan."""
    def q(x, y):
        return f"{F(x * s)} {F(y * s)}"
    def wing(sg):
        g = lambda x, y: q(sg * x, y)  # noqa: E731
        return (f"M {g(0.08, -0.12)} Q {g(0.4, -0.62 - flap)} {g(1.0, -0.42 - flap * 0.6)} Q {g(0.93, -0.2)} {g(0.84, 0.02)} "
                f"Q {g(0.7, -0.12)} {g(0.58, 0.1)} Q {g(0.44, -0.04)} {g(0.3, 0.16)} Q {g(0.2, 0.06)} {g(0.1, 0.2)} Z")
    wings = wing(1) + " " + wing(-1)
    bodyd = blob(0, 0.06 * s, 0.16 * s, 0.24 * s, seed, 0.06, 12)
    head = blob(0, -0.2 * s, 0.14 * s, 0.12 * s, seed + 1, 0.05, 10)
    ears = (f"M {q(-0.12, -0.24)} L {q(-0.17, -0.47)} L {q(-0.02, -0.31)} Z M {q(0.12, -0.24)} L {q(0.17, -0.47)} L {q(0.02, -0.31)} Z")
    o = [f'<g transform="translate({F(cx)} {F(cy)}) rotate({rot_})">', f'<path d="{wings}" fill="{body}"/>']
    if s > 10:
        o.append(strokes(uid + "-w", wings, (-s, -0.7 * s, s, 0.25 * s), [lt(body, 0.12), dk(body, 0.3), "#3E3058"], seed, n=int(s * 1.6), angle=-25, length=(s * 0.12, s * 0.4), width=(0.4, s * 0.03), opacity=(0.3, 0.6), curve=0.3))
    bones = "".join(f'<path d="M {q(sg * 0.1, -0.08)} Q {q(sg * x * 0.6, y * 0.9 - 0.12)} {q(sg * x, y)}"/>' for sg in (1, -1) for x, y in ((1.0, -0.42 - flap * 0.6), (0.84, 0.02), (0.58, 0.1), (0.3, 0.16)))
    o.append(f'<g stroke="{lt(body, 0.28)}" stroke-width="{F(max(0.6, s * 0.03))}" opacity="0.7" fill="none" stroke-linecap="round">{bones}</g>')
    o.append(rim(uid + "-r", wings, rimcol, 0, -1, k=max(0.7, s * 0.045), op=0.75))
    o.append(f'<path d="{ears}" fill="{body}"/><path d="{bodyd}" fill="{body}"/><path d="{head}" fill="{body}"/>')
    if s > 10:
        o.append(strokes(uid + "-b", bodyd, (-0.2 * s, -0.2 * s, 0.2 * s, 0.32 * s), [lt(body, 0.2), "#3E3058"], seed + 2, n=int(s * 0.6), angle=-80, length=(s * 0.05, s * 0.14), width=(0.3, s * 0.02), opacity=(0.4, 0.7)))
    o.append(rim(uid + "-rh", head + " " + ears + " " + bodyd, rimcol, -0.3, -1, k=max(0.6, s * 0.04), op=0.7))
    if eyes:
        o.append(f'<circle cx="{F(-0.05 * s)}" cy="{F(-0.21 * s)}" r="{F(max(0.8, 0.032 * s))}" fill="#FFD25E"/><circle cx="{F(0.05 * s)}" cy="{F(-0.21 * s)}" r="{F(max(0.8, 0.032 * s))}" fill="#FFD25E"/>')
    o.append(ink(wings, dk(body, 0.5), max(0.6, s * 0.03), seed + 3, 1, 0.6) + "</g>")
    return "".join(o)


def moon(uid, cx, cy, r, seed=3):
    o = [f'<defs>{rgrad(uid + "-h", cx, cy, r * 1.9, [(0, "#F6E6B0", 0.55), (0.5, "#E9D59A", 0.22), (1, "#E9D59A", 0)])}</defs><circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 1.9)}" fill="url(#{uid}-h)"/>']
    d = blob(cx, cy, r, r, seed, 0.012, 24)
    o.append(f'<defs>{rgrad(uid + "-g", cx, cy, r, [(0, "#FFF6D6", 1), (0.7, "#F3E2A8", 1), (1, "#D9C27E", 1)], fx=cx - r * 0.3, fy=cy - r * 0.3)}</defs><path d="{d}" fill="url(#{uid}-g)"/>')
    rnd = random.Random(seed)
    o.append(f'<clipPath id="{uid}-c"><path d="{d}"/></clipPath><g clip-path="url(#{uid}-c)">')
    for k, (a, t, cs) in enumerate(((0.4, 0.55, 0.16), (2.1, 0.7, 0.11), (3.4, 0.4, 0.13), (4.6, 0.75, 0.08), (5.5, 0.3, 0.1), (1.3, 0.25, 0.07), (2.9, 0.82, 0.06), (0.9, 0.86, 0.05))):
        rr = t * r
        px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        cr = cs * r
        o.append(f'<path d="{blob(px, py, cr, cr * 0.85, seed + k, 0.1, 10)}" fill="#C9B070" opacity="{rnd.uniform(0.3, 0.55):.2f}"/>'
                 f'<path d="{blob(px - cr * 0.15, py - cr * 0.15, cr * 0.7, cr * 0.6, seed + k + 20, 0.1, 10)}" fill="#E6D398" opacity="0.5"/>')
    o.append(strokes(uid + "-s", d, (cx - r, cy - r, cx + r, cy + r), ["#E6D398", "#FFF9E0", "#D4BC78"], seed + 5, n=int(r * 0.8), angle=-15, length=(r * 0.15, r * 0.5), width=(0.6, r * 0.02), opacity=(0.15, 0.4), curve=0.4))
    o.append("</g>")
    o.append(shade(uid + "-sh", d, "#B89A58", -0.8, 0.6, k=r * 0.1, op=0.35))
    o.append(ink(d, "#B89A58", 1.1, seed, 1, 0.45))
    return "".join(o)


def cat_side(u, x, y, s=1.0, seed=11, moon_side=(-0.6, -1), warm_side=(1, 0.2)):
    """Black cat sitting in profile facing right, head turned to us, tail wrapped along the ground. (x, y) = front paws."""
    def p(px, py):
        return (x + px * s, y + py * s)
    body = [p(-38, -4), p(-44, -24), p(-38, -48), p(-22, -60), p(-4, -62), p(10, -52), p(14, -34), p(16, -10), p(14, 0), p(-10, 1)]
    bd = smooth_closed(body)
    hx, hy = p(10, -70)
    head = blob(hx, hy, 15 * s, 13.5 * s, seed, 0.04, 16)
    ears = poly([p(-2, -78), p(-6, -95), p(6, -84)]) + " " + poly([p(16, -84), p(24, -97), p(24, -78)])
    tail = smooth_open([p(-36, -10), p(-52, -4), p(-56, 6), p(-40, 10), p(-16, 8), p(4, 10)])
    tints = ["#3A3050", "#120E1A", "#4A4064"]
    o = [shadow(x - 10 * s, y + 3, 44 * s, 5 * s, 0.22)]
    o.append(f'<path d="{tail}" stroke="{BAT}" stroke-width="{F(8 * s)}" fill="none" stroke-linecap="round"/>'
             f'<path d="{tail}" stroke="{LAV}" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(0 {F(-2.6 * s)})"/>')
    o.append(paint(u + "-b", bd, bbox(body), BAT, seed, tints=tints, angle=-70, n=70, ink_col="#0E0A14", ink_w=1.2 * s, length=(5 * s, 16 * s), width=(0.5, 1.6 * s)))
    o.append(rim(u + "-mr", bd, LAV, moon_side[0], moon_side[1], k=1.8 * s, op=0.7))
    o.append(rim(u + "-wr", bd, "#F0963A", warm_side[0], warm_side[1], k=1.6 * s, op=0.55))
    # front leg line and the haunch
    o.append(f'<path d="{smooth_open([p(2, -36), p(0, -16), p(2, -2)])}" stroke="#4A4064" stroke-width="{F(1.3 * s)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append(f'<path d="{smooth_open([p(-30, -44), p(-34, -24), p(-26, -8)])}" stroke="#4A4064" stroke-width="{F(1.2 * s)}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    for px_ in (-8, 8):
        o.append(f'<path d="{blob(*p(px_, 0), 7 * s, 3.4 * s, seed + px_, 0.06, 9)}" fill="#2E2640"/>')
    o.append(f'<path d="{ears}" fill="{BAT}" stroke="#0E0A14" stroke-width="{F(1.1 * s)}" stroke-linejoin="round"/>')
    o.append(f'<path d="{poly([p(-2, -82), p(-5, -93), p(4, -86)])}" fill="#C77A92" opacity="0.6"/><path d="{poly([p(18, -86), p(24, -96), p(24, -82)])}" fill="#C77A92" opacity="0.6"/>')
    o.append(paint(u + "-h", head, (hx - 16 * s, hy - 15 * s, hx + 16 * s, hy + 15 * s), BAT, seed + 5, tints=tints, angle=-90, n=24, ink_col="#0E0A14", ink_w=1.2 * s, length=(3 * s, 9 * s), width=(0.5, 1.2 * s)))
    o.append(rim(u + "-hr", head + " " + ears, LAV, moon_side[0], moon_side[1], k=1.6 * s, op=0.75) + rim(u + "-hw", head, "#F0963A", warm_side[0], warm_side[1], k=1.2 * s, op=0.5))
    for sg, ex, ey in ((-1, 4, -72), (1, 16, -71)):
        ex, ey = p(ex, ey)
        o.append(f'<ellipse cx="{F(ex)}" cy="{F(ey)}" rx="{F(4.2 * s)}" ry="{F(3.2 * s)}" fill="#D8EC6A" transform="rotate({sg * -10} {F(ex)} {F(ey)})"/>'
                 f'<ellipse cx="{F(ex)}" cy="{F(ey)}" rx="{F(1.1 * s)}" ry="{F(2.7 * s)}" fill="#14101A"/><circle cx="{F(ex - 1.3 * s)}" cy="{F(ey - 1.2 * s)}" r="{F(0.8 * s)}" fill="#FFFFFF"/>')
    nx, ny = p(11, -65)
    o.append(f'<path d="M {F(nx - 2.2 * s)} {F(ny)} L {F(nx + 2.2 * s)} {F(ny)} L {F(nx)} {F(ny + 2.2 * s)} Z" fill="#E59AB0"/>')
    o.append(f'<path d="M {F(nx)} {F(ny + 2.2 * s)} q {F(-2 * s)} {F(2.6 * s)} {F(-4 * s)} {F(0.8 * s)} M {F(nx)} {F(ny + 2.2 * s)} q {F(2 * s)} {F(2.6 * s)} {F(4 * s)} {F(0.8 * s)}" stroke="#B9A6E0" stroke-width="{F(0.9 * s)}" fill="none" stroke-linecap="round"/>')
    wh = "".join(f'<path d="M {F(nx + sg * 5 * s)} {F(ny + dy * s)} q {F(sg * 8 * s)} {F(dl * s * 0.3)} {F(sg * 15 * s)} {F(dl * s)}"/>' for sg in (-1, 1) for dy, dl in ((-0.5, -3), (2, 1)))
    o.append(f'<g stroke="#D9CCF2" stroke-width="{F(0.7 * s)}" opacity="0.75" stroke-linecap="round" fill="none">{wh}</g>')
    return "".join(o)


def jack(uid, cx, cy, w, h, kind, seed, body="#E8792E", dark="#B9531E", light="#F8A85A"):
    """Jack-o'-lantern: painted pumpkin, then the carved face glowing from a candle inside, light pooling below."""
    o = [glow(uid + "-pool", cx, cy + 0.5 * h, 0.9 * w, 0.22 * h, "#FFB547", 0.45)]
    o.append(pumpkin(uid, cx, cy, w, h, seed, body=body, dark=dark, light=light, lit=(-1, -1), rimcol="#C9B8E8"))
    g = uid + "-fg"
    o.append(f'<defs>{rgrad(g, cx, cy + 0.12 * h, 0.45 * w, [(0, "#FFFBD8", 1), (0.4, "#FFD24A", 1), (1, "#F5921E", 1)])}</defs>')
    o.append(glow(uid + "-sk", cx, cy + 0.08 * h, 0.5 * w, 0.42 * h, "#FFE07A", 0.5))
    holes, teeth = [], []
    if kind == "classic":
        for sg in (-1, 1):
            holes.append(poly(jitter([(cx + sg * 0.3 * w, cy + 0.0 * h), (cx + sg * 0.19 * w, cy - 0.28 * h), (cx + sg * 0.07 * w, cy - 0.01 * h)], seed, 0.6)))
        holes.append(poly([(cx - 0.045 * w, cy + 0.08 * h), (cx, cy - 0.04 * h), (cx + 0.045 * w, cy + 0.08 * h)]))
        holes.append(f"M {F(cx - 0.34 * w)} {F(cy + 0.1 * h)} Q {F(cx)} {F(cy + 0.32 * h)} {F(cx + 0.34 * w)} {F(cy + 0.1 * h)} Q {F(cx)} {F(cy + 0.6 * h)} {F(cx - 0.34 * w)} {F(cy + 0.1 * h)} Z")
        teeth = [(cx - 0.12 * w, cy + 0.18 * h, 0.075 * w, 0.1 * h), (cx + 0.11 * w, cy + 0.24 * h, 0.075 * w, 0.1 * h)]
    elif kind == "happy":
        for sg in (-1, 1):
            ex, ey = cx + sg * 0.19 * w, cy - 0.08 * h
            holes.append(f"M {F(ex - 0.1 * w)} {F(ey + 0.05 * h)} Q {F(ex)} {F(ey - 0.24 * h)} {F(ex + 0.1 * w)} {F(ey + 0.05 * h)} Q {F(ex)} {F(ey - 0.07 * h)} {F(ex - 0.1 * w)} {F(ey + 0.05 * h)} Z")
        holes.append(f"M {F(cx - 0.26 * w)} {F(cy + 0.12 * h)} Q {F(cx)} {F(cy + 0.3 * h)} {F(cx + 0.26 * w)} {F(cy + 0.12 * h)} Q {F(cx)} {F(cy + 0.5 * h)} {F(cx - 0.26 * w)} {F(cy + 0.12 * h)} Z")
        teeth = [(cx, cy + 0.22 * h, 0.08 * w, 0.08 * h)]
    else:  # sly
        for sg in (-1, 1):
            holes.append(poly([(cx + sg * 0.3 * w, cy - 0.2 * h), (cx + sg * 0.06 * w, cy - 0.06 * h), (cx + sg * 0.21 * w, cy + 0.04 * h)]))
        z = [(-0.3, 0.12), (0, 0.2), (0.3, 0.12), (0.22, 0.34), (0.11, 0.26), (0, 0.4), (-0.11, 0.26), (-0.22, 0.34)]
        holes.append(poly([(cx + x * w, cy + y * h) for x, y in z]))
    for hd in holes:
        o.append(f'<path d="{hd}" fill="#7A2E0E" stroke="#7A2E0E" stroke-width="1.4" stroke-linejoin="round"/>')
        o.append(f'<path d="{hd}" fill="url(#{g})" transform="translate(0.5 1.3)"/>')
    for tx, ty, tw, th in teeth:
        o.append(f'<path d="{blob(tx, ty, tw / 2, th / 2, 7, 0.05, 10)}" fill="{body}"/>')
    return "".join(o)


def cobweb(x, y, r, a0, a1, col="#D9CCF2", n=6, rings=5):
    rays = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        rays.append(f"M {F(x)} {F(y)} L {F(x + math.cos(a) * r)} {F(y + math.sin(a) * r)}")
    arcs = []
    for k in range(1, rings + 1):
        rr = r * k / rings
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            arcs.append(f"M {F(x0)} {F(y0)} Q {F(mx + (x - mx) * 0.22)} {F(my + (y - my) * 0.22)} {F(x1)} {F(y1)}")
    return lines(rays + arcs, col, 0.8, 0.8)


def porch(u):
    """Painted porch corner: plank floor with two steps coming toward us, a turned post, a bit of railing."""
    o = []
    wood, dark, light = "#7A5A42", "#4E3828", "#A88A66"
    # landing, then riser + tread twice, coming toward us; grain runs along the boards, risers darker
    rows = [("tread", 236, 256, 60), ("riser", 256, 270, 40), ("tread", 270, 288, 20), ("riser", 288, 302, 0), ("tread", 302, 322, 0)]
    for k, (kind, y0, y1, xl) in enumerate(rows):
        pts = [(xl, y0), (380, y0), (380, y1), (xl - 6, y1)]
        d = poly(jitter(pts, 20 + k, 0.5))
        if kind == "riser":
            o.append(paint(f"{u}-r{k}", d, bbox(pts), dk(wood, 0.32), 31 + k, tints=[dark, "#5E4432", "#3A2A1E"], angle=0, n=50, length=(14, 50), width=(0.6, 2), op=(0.25, 0.5), ink_col=dark, ink_w=1.1, curve=0.05))
            o.append(f'<path d="M {F(xl)} {F(y1 - 1)} L 380 {F(y1 - 1)}" stroke="#2A1C14" stroke-width="2.2" opacity="0.5"/>')
        else:
            o.append(paint(f"{u}-t{k}", d, bbox(pts), lt(wood, 0.06) if k == 0 else wood, 21 + k, tints=[dark, light, "#8E6E50", "#5E4432"], angle=0, n=90, length=(16, 60), width=(0.6, 2.2), op=(0.25, 0.5), ink_col=dark, ink_w=1.1, curve=0.03))
            o.append(lines([f"M {F(x)} {F(y0 + 1)} L {F(x - 5 - k)} {F(y1 - 1)}" for x in range(70 + k * 11, 390, 54)], dark, 1.0, 0.5))
            o.append(f'<path d="M {F(xl)} {F(y1 - 1.6)} L 380 {F(y1 - 1.6)}" stroke="{lt(light, 0.45)}" stroke-width="1.8" opacity="0.6"/>')
            o.append(f'<path d="M {F(xl)} {F(y0 + 1)} L 380 {F(y0 + 1)}" stroke="{dark}" stroke-width="1.2" opacity="0.5"/>')
    # the post at the right with a little bracket, and the rail going off to the right
    post = [(338, 40), (356, 40), (358, 238), (336, 238)]
    pd = poly(jitter(post, 9, 0.6))
    o.append(paint(u + "-post", pd, bbox(post), lt(wood, 0.1), 10, tints=[dark, light, "#8E6E50"], angle=-89, n=80, length=(14, 50), width=(0.6, 2), op=(0.25, 0.5), ink_col=dark, ink_w=1.3, curve=0.03))
    o.append(shade(u + "-ps", pd, dark, -1, 0, k=5, op=0.4) + rim(u + "-pr", pd, "#D9CCF2", 1, -0.2, k=1.2, op=0.35))
    o.append(f'<path d="M 336 70 l -14 0 l 0 -8 l 14 -8 Z" fill="{dark}"/><path d="M 356 70 l 14 0 l 0 -8 l -14 -8 Z" fill="{dark}"/>')
    o.append(paint(u + "-rail", poly([(358, 150), (380, 148), (380, 160), (358, 162)]), (356, 146, 382, 164), wood, 12, angle=0, n=10, ink_col=dark, ink_w=1.1))
    return "".join(o)


def halloween_scene(u="hw"):
    back = [sky_rect(u + "-sky", [(0, "#1A1636", 1), (0.45, "#2E2552", 1), (0.72, "#4A3660", 1), (1, "#2A1E34", 1)], (0, 0, 380, 330))]
    rnd = random.Random(4)
    back.append(speck(5, (0, 0, 380, 200), ["#FFF6D0", "#E9D9FF"], 50, r=(0.5, 1.3), op=(0.3, 0.9)))
    back.append(moon(u + "-moon", 246, 108, 68))
    # distant rooftops and bare trees against the sky
    far, line = ridge([(0, 214), (60, 206), (120, 212), (200, 204), (280, 210), (380, 202)], 6, 330, amp=4)
    back.append(f'<path d="{far}" fill="#17122A"/>')
    for x, hh in ((34, 60), (96, 48), (160, 70), (300, 56)):
        tx = []
        rnd2 = random.Random(x)
        def branch(bx, by, ang, L, d):
            if d == 0 or L < 4:
                return
            ex, ey = bx + math.cos(math.radians(ang)) * L, by + math.sin(math.radians(ang)) * L
            tx.append((bx, by, ex, ey, max(0.7, L * 0.06)))
            for da in (-28, 22):
                branch(ex, ey, ang + da + rnd2.uniform(-10, 10), L * rnd2.uniform(0.55, 0.75), d - 1)
        branch(x, 210, -90 + rnd2.uniform(-6, 6), hh * 0.45, 5)
        back.append("".join(f'<path d="M {F(a)} {F(b)} L {F(c)} {F(d)}" stroke="#17122A" stroke-width="{F(w)}" stroke-linecap="round"/>' for a, b, c, d, w in tx))
    back.append(porch(u + "-po"))
    # warm light spilling from the jack-o'-lanterns onto the boards, and the cat's moon-shadow
    back.append(glow(u + "-wl", 236, 252, 170, 30, "#FF9A3A", 0.45) + glow(u + "-wl2", 180, 290, 150, 24, "#FF9A3A", 0.35))
    for k, (x, y, s, r, fl) in enumerate(((150, 58, 24, -14, 0.1), (300, 42, 17, 12, -0.06), (330, 128, 12, -6, 0.0), (70, 118, 10, 8, 0.12), (212, 160, 9, -4, 0.05))):
        back.append(bat_p(f"{u}-b{k}", x, y, s, rot_=r, flap=fl, seed=k + 1, rimcol="#E9D9A0" if abs(x - 232) < 90 and y < 180 else LAV))
    o = [vignette(u + "-v", "".join(back), [(215, 175, 180, 145, 0.45), (246, 112, 118, 104, 0.7), (120, 250, 115, 75, 0.4), (290, 255, 100, 70, 0.4)])]
    o.append(cobweb(338, 238, 40, 180, 270) + f'<path d="M 364 162 l 0 30" stroke="#D9CCF2" stroke-width="0.8" opacity="0.8"/>'
             f'<ellipse cx="364" cy="196" rx="3.6" ry="4.2" fill="#241C34"/><circle cx="364" cy="191" r="2.4" fill="#241C34"/>'
             + lines([f"M 364 193 q {sg * 4} {dy} {sg * 7} {dy + 3}" for sg in (-1, 1) for dy in (-3, 0, 3)], "#241C34", 1.1, 0.9)
             + '<path d="M 361.5 190 a 3 3 0 0 1 4 -2" stroke="#A898D0" stroke-width="0.8" fill="none" opacity="0.8"/>')
    o.append(cat_side(u + "-cat", 104, 250, 1.0))
    o.append(jack(u + "-j1", 236, 220, 100, 66, "classic", 61, body="#E2702A", dark="#B04A18", light="#F8A85A"))
    o.append(jack(u + "-j2", 150, 262, 68, 48, "happy", 62))
    o.append(jack(u + "-j3", 306, 262, 54, 44, "sly", 63, body="#EE8A34", dark="#BE5A1E", light="#FFB86A"))
    o.append(maple(u + "-l1", 56, 310, 9, "#C9442E", "#8E2A1A", rot_=-40, seed=7) + oak_leaf(u + "-l2", 206, 312, 8, "#B8862E", "#7A5418", rot_=60, seed=8)
             + maple(u + "-l3", 352, 296, 8, "#E8792E", "#B9531E", rot_=100, seed=9))
    return "".join(o)


def halloween_garland(u="hg"):
    """Seamless 320 x 74: a string of glowing jack-o'-lantern lights with bats and little cobwebs."""
    o = []
    d = "M 0 10 C 80 34 240 34 320 10"
    o.append(f'<path d="{d}" stroke="#2E2440" stroke-width="2.6" fill="none"/><path d="{d}" stroke="#8A78B4" stroke-width="0.9" fill="none" stroke-dasharray="2 4" opacity="0.8"/>')
    xs = [(34, "classic", 0.1), (98, "happy", -0.1), (162, "sly", 0.05), (226, "classic", -0.06), (288, "happy", 0.08)]
    for k, (x, kind, tl) in enumerate(xs):
        y = swag_y(x)
        def item(xx, y=y, kind=kind, k=k, tl=tl):
            cx, cy = xx + tl * 20, y + 20
            out = [f'<path d="M {F(xx)} {F(y)} Q {F(xx + tl * 8)} {F(y + 6)} {F(cx)} {F(cy - 12)}" stroke="#2E2440" stroke-width="1.4" fill="none"/>',
                   f'<rect x="{F(cx - 3)}" y="{F(cy - 14)}" width="6" height="5" rx="1" fill="#3A2E52" stroke="#1A1228" stroke-width="0.6"/>',
                   glow(f"{u}-g{k}", cx, cy, 24, 20, "#FFB547", 0.5)]
            out.append(jack(f"{u}-j{k}", cx, cy, 26, 19, kind, 70 + k))
            return "".join(out)
        o.append(wrap(item, x, 24))
    for k, (x, s, r, fl) in enumerate(((66, 11, -12, 0.1), (130, 9, 10, -0.05), (194, 10, -5, 0.08), (258, 9, 8, 0.0))):
        y = swag_y(x) + 30
        o.append(wrap(lambda xx, y=y, s=s, r=r, fl=fl, k=k: bat_p(f"{u}-b{k}", xx, y, s, rot_=r, flap=fl, seed=k + 3), x, 16))
    o.append(cobweb(0, 0, 30, 0, 90, n=5, rings=4) + cobweb(320, 0, 30, 90, 180, n=5, rings=4))
    return "".join(o)


def halloween_particles():
    return {"halloween-bat": bat_p("pb", 20, 22, 17, rot_=-8, flap=0.06, seed=9)}


# ================================================================ THANKSGIVING: harvest table corner in lamp light
def wheat_stalk(x, y, ang, L, seed, col="#D9A84E", w=1.0):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bend = rnd.uniform(-0.08, 0.08) * L
    tip = (x + ux * L + nx * bend, y + uy * L + ny * bend)
    o = [f'<path d="M {F(x)} {F(y)} Q {F(x + ux * L * 0.5 + nx * bend * 0.3)} {F(y + uy * L * 0.5 + ny * bend * 0.3)} {F(tip[0])} {F(tip[1])}" stroke="{dk(col, 0.3)}" stroke-width="{F(1.3 * w)}" fill="none" stroke-linecap="round"/>']
    kern, awns = [], []
    n = 7
    for i in range(n):
        t = 0.58 + 0.4 * i / (n - 1)
        px, py = x + ux * L * t + nx * bend * t * t, y + uy * L * t + ny * bend * t * t
        k = (1 - 0.3 * i / n) * w
        for sg in (-1, 1):
            ka = ang + sg * 26
            kx, ky = px + nx * sg * 2.0 * k, py + ny * sg * 2.0 * k
            kern.append(blob(kx, ky, 3.4 * k, 1.8 * k, seed + i, 0.05, 8, rot=ka))
            aa = math.radians(ka - sg * 8)
            awns.append(f"M {F(kx + math.cos(aa) * 2 * k)} {F(ky + math.sin(aa) * 2 * k)} l {F(math.cos(aa) * 10 * k)} {F(math.sin(aa) * 10 * k)}")
    kern.append(blob(tip[0], tip[1], 3.2 * w, 1.7 * w, seed + 9, 0.05, 8, rot=ang))
    o.append(lines(awns, lt(col, 0.25), 0.55 * w, 0.85))
    o.append(f'<path d="{"".join(kern)}" fill="{col}" stroke="{dk(col, 0.42)}" stroke-width="{F(0.6 * w)}"/>')
    o.append(f'<path d="{"".join(kern)}" fill="{lt(col, 0.45)}" opacity="0.35" transform="translate({F(-0.6 * w)} {F(-0.6 * w)})"/>')
    return "".join(o)


def feather(uid, x, y, L, ang, cols, seed, w=0.15):
    """Turkey tail feather from quill base (x, y) pointing ang degrees: bronze vane, dark band, pale tip, barb lines."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    def P(t, k):
        return (x + ux * L * t + nx * L * w * k, y + uy * L * t + ny * L * w * k)
    pts = [P(0.08, 0.08), P(0.3, 0.55), P(0.55, 0.9), P(0.8, 1.0), P(0.95, 0.7), P(1.0, 0), P(0.95, -0.7), P(0.8, -1.0), P(0.55, -0.9), P(0.3, -0.55), P(0.08, -0.08)]
    d = smooth_closed(jitter(pts, seed, 0.5))
    base_c, dark_c, light_c = cols
    o = [paint(uid, d, bbox(pts), base_c, seed, tints=[dark_c, light_c, lt(base_c, 0.2)], angle=ang + 40, n=int(L * 0.4), length=(L * 0.06, L * 0.16), width=(0.4, 1.0), op=(0.25, 0.5), ink_col=dk(base_c, 0.5), ink_w=0.9, curve=0.1)]
    bands = [(0.72, 0.8, light_c, 0.85), (0.8, 0.9, dk(base_c, 0.5), 0.85), (0.9, 1.02, "#E9D8B0", 0.9)]
    o.append(f'<clipPath id="{uid}-bc"><path d="{d}"/></clipPath><g clip-path="url(#{uid}-bc)">')
    for t0, t1, c, op in bands:
        o.append(f'<path d="{poly([P(t0, 1.2), P(t1, 1.2), P(t1, -1.2), P(t0, -1.2)])}" fill="{c}" opacity="{op}"/>')
    barbs = []
    for i in range(16):
        t = 0.12 + 0.86 * i / 15
        for sg in (-1, 1):
            p0 = P(t, 0)
            p1 = P(t + 0.12, sg * 1.1)
            barbs.append(f"M {F(p0[0])} {F(p0[1])} L {F(p1[0])} {F(p1[1])}")
    o.append(lines(barbs, dk(base_c, 0.45), 0.6, 0.45) + "</g>")
    o.append(f'<path d="M {F(x)} {F(y)} L {F(P(0.97, 0)[0])} {F(P(0.97, 0)[1])}" stroke="{lt(base_c, 0.55)}" stroke-width="1.2" opacity="0.85"/><path d="M {F(x)} {F(y)} L {F(P(0.4, 0)[0])} {F(P(0.4, 0)[1])}" stroke="{dk(base_c, 0.55)}" stroke-width="1.8" stroke-linecap="round"/>')
    return "".join(o)


def jug(u, cx, base, w, h, seed=21, col="#8E9AA8", glaze="#D9D2C2"):
    """Stoneware jug with a cream glaze dripping over a blue-grey body."""
    pts = [(cx - w * 0.3, base - h), (cx + w * 0.3, base - h), (cx + w * 0.34, base - h * 0.84), (cx + w * 0.5, base - h * 0.55), (cx + w * 0.46, base - h * 0.15), (cx + w * 0.38, base),
           (cx - w * 0.38, base), (cx - w * 0.46, base - h * 0.15), (cx - w * 0.5, base - h * 0.55), (cx - w * 0.34, base - h * 0.84)]
    d = smooth_closed(pts)
    o = [shadow(cx + 6, base, w * 0.55, 5, 0.22)]
    o.append(paint(u, d, bbox(pts), col, seed, tints=[dk(col, 0.25), lt(col, 0.3), "#6E7A8A"], angle=-88, n=70, length=(8, 26), width=(0.6, 2.2), op=(0.2, 0.45), ink_col="#3E4650", ink_w=1.4))
    gl = smooth_closed([(cx - w * 0.34, base - h * 0.84), (cx - w * 0.3, base - h), (cx + w * 0.3, base - h), (cx + w * 0.34, base - h * 0.84), (cx + w * 0.4, base - h * 0.6), (cx + w * 0.26, base - h * 0.5),
                        (cx + w * 0.14, base - h * 0.62), (cx, base - h * 0.46), (cx - w * 0.12, base - h * 0.6), (cx - w * 0.3, base - h * 0.52), (cx - w * 0.42, base - h * 0.66)])
    o.append(f'<clipPath id="{u}-gc"><path d="{d}"/></clipPath><g clip-path="url(#{u}-gc)">' + paint(u + "-gl", gl, bbox(pts), glaze, seed + 1, tints=[dk(glaze, 0.15), "#FFFFFF", "#C9BEA8"], angle=-88, n=40, length=(6, 20), width=(0.6, 2), op=(0.2, 0.45), ink_col="#8A8070", ink_w=1.0) + "</g>")
    o.append(shade(u + "-s", d, "#3E4650", -1, 0.1, k=w * 0.14, op=0.4) + rim(u + "-r", d, "#FFF0C8", 1, -0.3, k=2.2, op=0.6))
    o.append(f'<path d="M {F(cx - w * 0.14)} {F(base - h * 0.8)} q {F(-w * 0.04)} {F(h * 0.3)} {F(w * 0.02)} {F(h * 0.6)}" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.45"/>')
    o.append(f'<ellipse cx="{F(cx)}" cy="{F(base - h)}" rx="{F(w * 0.3)}" ry="{F(w * 0.07)}" fill="#4E4A3E"/><ellipse cx="{F(cx)}" cy="{F(base - h - 1)}" rx="{F(w * 0.3)}" ry="{F(w * 0.07)}" fill="none" stroke="{lt(glaze, 0.3)}" stroke-width="1.6"/>')
    return "".join(o)


def pie(u, cx, cy, w, seed=31):
    """Lattice pumpkin pie in a fluted red dish, seen from a little above: a slice is out, a curl of steam rises."""
    rx, ry = w * 0.46, w * 0.17
    side = w * 0.1
    o = [shadow(cx + 8, cy + side + ry * 0.9, w * 0.56, ry * 0.9, 0.24)]
    # dish: outer rim ellipse + fluted side below it
    dish_top = blob(cx, cy, rx * 1.1, ry * 1.12, seed, 0.015, 24)
    dish_side = smooth_closed([(cx - rx * 1.1, cy), (cx - rx * 1.02, cy + side * 1.3), (cx, cy + side * 1.3 + ry * 1.05), (cx + rx * 1.02, cy + side * 1.3), (cx + rx * 1.1, cy), (cx, cy + ry * 1.12)])
    o.append(paint(u + "-ds", dish_side, (cx - rx * 1.15, cy - 2, cx + rx * 1.15, cy + side * 1.3 + ry * 1.1), "#B8502E", seed, tints=["#8E3418", "#D9764E", "#E89A6E"], angle=-88, n=50, length=(4, 12), width=(0.5, 1.6), op=(0.25, 0.5), ink_col="#5E2210", ink_w=1.3))
    o.append(lines([f"M {F(cx + math.cos(t) * rx * 1.08)} {F(cy + math.sin(t) * ry * 1.1)} q 0 {F(side * 0.6)} {F(-math.cos(t) * rx * 0.06)} {F(side * 1.2)}" for t in [0.2 + i * 0.27 for i in range(10)]], "#7A2E16", 1.0, 0.45))
    o.append(shade(u + "-dsh", dish_side, "#5E2210", -1, 0.2, k=w * 0.05, op=0.4))
    o.append(f'<path d="{dish_top}" fill="#C9603A"/><path d="{dish_top}" fill="none" stroke="#E89A6E" stroke-width="2" opacity="0.7"/>' + ink(dish_top, "#5E2210", 1.2, seed + 1, 1, 0.6))
    # pie: crust side, filling on top, lattice, rolled crimped edge
    crust_side = smooth_closed([(cx - rx, cy), (cx - rx * 0.96, cy + side), (cx, cy + side + ry * 0.96), (cx + rx * 0.96, cy + side), (cx + rx, cy), (cx, cy + ry)])
    o.append(paint(u + "-cs", crust_side, (cx - rx, cy, cx + rx, cy + side + ry), "#C9903E", seed + 2, tints=["#9A6220", "#E6B468", "#F2CB80"], angle=-88, n=40, length=(4, 10), width=(0.5, 1.4), op=(0.25, 0.5), ink_col="#7A4A16", ink_w=1.1))
    top = blob(cx, cy, rx, ry, seed + 3, 0.015, 24)
    o.append(paint(u + "-f", top, (cx - rx, cy - ry, cx + rx, cy + ry), "#C25A24", seed + 4, tints=["#9A3E14", "#E07A3A", "#F2A05A"], angle=0, n=50, length=(4, 14), width=(0.5, 1.6), op=(0.25, 0.5), ink_w=0))
    o.append(f'<clipPath id="{u}-lc"><path d="{top}"/></clipPath><g clip-path="url(#{u}-lc)">')
    for ang in (38, -38):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a) * 0.38
        nx, ny = -math.sin(a), math.cos(a) * 0.38
        for k in range(-3, 4):
            ox, oy = nx * k * w * 0.19, ny * k * w * 0.19
            d = f"M {F(cx + ox + ux * w * 0.6)} {F(cy + oy + uy * w * 0.6)} L {F(cx + ox - ux * w * 0.6)} {F(cy + oy - uy * w * 0.6)}"
            o.append(f'<path d="{d}" stroke="#7A3A14" stroke-width="{F(w * 0.05)}" stroke-linecap="round" opacity="0.45" transform="translate(0 {F(w * 0.014)})"/>'
                     f'<path d="{d}" stroke="#E6B468" stroke-width="{F(w * 0.045)}" stroke-linecap="round"/><path d="{d}" stroke="#F6D898" stroke-width="{F(w * 0.012)}" stroke-linecap="round" opacity="0.7" transform="translate(0 {F(-w * 0.012)})"/>')
    o.append("</g>")
    o.append(f'<path d="{top}" fill="none" stroke="#D9A054" stroke-width="{F(w * 0.05)}"/>')
    o.append("".join(f'<circle cx="{F(cx + math.cos(t) * rx)}" cy="{F(cy + math.sin(t) * ry)}" r="{F(w * 0.028)}" fill="#E6B468" stroke="#9A6220" stroke-width="0.7"/>' for t in [i * 0.2 for i in range(32)]))
    o.append(shade(u + "-ts", top, "#7A3A14", -0.6, 0.8, k=w * 0.04, op=0.3))
    # the slice taken out: a wedge from the centre to the front-left, dark cut faces with the filling showing
    wedge = f"M {F(cx)} {F(cy)} L {F(cx - rx * 0.98)} {F(cy + ry * 0.3)} Q {F(cx - rx * 0.7)} {F(cy + ry * 0.9)} {F(cx - rx * 0.3)} {F(cy + ry * 0.98)} Z"
    o.append(f'<path d="{wedge}" fill="#C9603A"/><path d="{wedge}" fill="#8E3418" opacity="0.5"/>')
    cut1 = f"M {F(cx)} {F(cy)} L {F(cx - rx * 0.3)} {F(cy + ry * 0.98)} l 0 {F(side)} L {F(cx)} {F(cy + side)} Z"
    o.append(f'<path d="{cut1}" fill="#D9742E"/><path d="{cut1}" fill="none" stroke="#7A3A14" stroke-width="1"/>')
    o.append(f'<path d="M {F(cx - rx * 0.3)} {F(cy + ry * 0.98)} l 0 {F(side)} M {F(cx)} {F(cy)} l 0 {F(side)}" stroke="#E6B468" stroke-width="{F(w * 0.03)}"/>')
    o.append(f'<path d="M {F(cx - rx * 0.3)} {F(cy + ry * 0.98 + side * 0.3)} L {F(cx)} {F(cy + side * 0.3)}" stroke="#F2CB80" stroke-width="{F(w * 0.035)}" opacity="0.9"/>')
    o.append(lines([f"M {F(cx + 8)} {F(cy - 12)} c -8 -10 6 -16 -2 -28", f"M {F(cx + 22)} {F(cy - 10)} c 8 -8 -4 -14 4 -24", f"M {F(cx - 10)} {F(cy - 10)} c -6 -8 4 -14 -2 -22"], "#FFFFFF", 2.2, 0.5))
    return "".join(o)


def oil_lamp(u, cx, base, h, seed=41):
    """Brass hurricane lamp with a glass chimney, a flame and a big warm glow."""
    o = [glow(u + "-gl", cx, base - h * 0.55, h * 1.4, h * 1.1, "#FFC55A", 0.55, mid=0.4)]
    o.append(shadow(cx + 4, base, h * 0.22, 4, 0.25))
    brass, bdark, blight = "#B8862E", "#6E4A12", "#F2D07A"
    foot = smooth_closed([(cx - h * 0.2, base), (cx + h * 0.2, base), (cx + h * 0.14, base - h * 0.05), (cx + h * 0.06, base - h * 0.1), (cx - h * 0.06, base - h * 0.1), (cx - h * 0.14, base - h * 0.05)])
    bowl = smooth_closed([(cx - h * 0.06, base - h * 0.1), (cx + h * 0.06, base - h * 0.1), (cx + h * 0.2, base - h * 0.2), (cx + h * 0.22, base - h * 0.32), (cx + h * 0.1, base - h * 0.4), (cx - h * 0.1, base - h * 0.4), (cx - h * 0.22, base - h * 0.32), (cx - h * 0.2, base - h * 0.2)])
    for k, d in enumerate((foot, bowl)):
        o.append(paint(f"{u}-m{k}", d, (cx - h * 0.25, base - h * 0.42, cx + h * 0.25, base + 2), brass, seed + k, tints=[bdark, blight, "#D9A84E"], angle=-85, n=30, length=(4, 12), width=(0.5, 1.6), op=(0.3, 0.6), ink_col=bdark, ink_w=1.1))
        o.append(shade(f"{u}-ms{k}", d, bdark, -1, 0, k=h * 0.05, op=0.45) + rim(f"{u}-mr{k}", d, "#FFF4C0", 1, -0.5, k=1.4, op=0.7))
    o.append(f'<rect x="{F(cx - h * 0.07)}" y="{F(base - h * 0.47)}" width="{F(h * 0.14)}" height="{F(h * 0.08)}" rx="1" fill="{brass}" stroke="{bdark}" stroke-width="0.9"/>')
    o.append(f'<circle cx="{F(cx + h * 0.2)}" cy="{F(base - h * 0.44)}" r="{F(h * 0.045)}" fill="none" stroke="{bdark}" stroke-width="1.6"/>')
    chim = smooth_closed([(cx - h * 0.1, base - h * 0.47), (cx + h * 0.1, base - h * 0.47), (cx + h * 0.16, base - h * 0.62), (cx + h * 0.12, base - h * 0.8), (cx + h * 0.05, base - h * 1.0), (cx - h * 0.05, base - h * 1.0), (cx - h * 0.12, base - h * 0.8), (cx - h * 0.16, base - h * 0.62)])
    fl = f"M {F(cx - h * 0.04)} {F(base - h * 0.5)} Q {F(cx - h * 0.06)} {F(base - h * 0.62)} {F(cx)} {F(base - h * 0.74)} Q {F(cx + h * 0.06)} {F(base - h * 0.62)} {F(cx + h * 0.04)} {F(base - h * 0.5)} Z"
    o.append(f'<path d="{chim}" fill="#FFF2C0" opacity="0.4"/><path d="{fl}" fill="#FFB236" transform="scale(1 1.3)" transform-origin="{F(cx)} {F(base - h * 0.5)}"/><path d="{fl}" fill="#FFF5C8" transform="translate(0 {F(h * 0.03)}) scale(0.6)" transform-origin="{F(cx)} {F(base - h * 0.52)}"/>')
    o.append(glow(u + "-fg", cx, base - h * 0.62, h * 0.16, h * 0.2, "#FFE38A", 0.8))
    o.append(f'<path d="{chim}" fill="none" stroke="#B8A880" stroke-width="1.4" opacity="0.9"/><path d="{chim}" fill="none" stroke="#FFFFFF" stroke-width="2.2" opacity="0.45" transform="translate({F(-h * 0.03)} 0)" stroke-dasharray="{F(h * 0.3)} {F(h * 0.5)}"/>')
    return "".join(o)


def apple_p(uid, cx, cy, r, col, seed, rot_=0, leaf=True):
    pts = [(0, -0.72), (0.4, -0.95), (0.88, -0.62), (1.0, -0.05), (0.78, 0.62), (0.32, 0.92), (0, 0.84), (-0.32, 0.92), (-0.78, 0.62), (-1.0, -0.05), (-0.88, -0.62), (-0.4, -0.95)]
    pts = [rot(cx + x * r, cy + y * r, cx, cy, rot_) for x, y in jitter(pts, seed, 0.03)]
    d = smooth_closed(pts)
    o = [shadow(cx + 2, cy + r * 0.95, r * 0.9, r * 0.2, 0.22)]
    o.append(paint(uid, d, bbox(pts), col, seed, tints=[lt(col, 0.25), dk(col, 0.25), "#F6C24E"], angle=-90 + rot_, n=int(r * 1.6), ink_col=inkc(col), ink_w=max(0.9, r * 0.08), length=(r * 0.3, r * 0.9), width=(0.4, max(0.8, r * 0.07)), curve=0.4))
    o.append(shade(uid + "-s", d, dk(col, 0.45), -0.7, 0.6, k=r * 0.25, op=0.45) + rim(uid + "-r", d, "#FFF0C0", 1, -0.5, k=r * 0.1, op=0.6))
    hx, hy = rot(cx - 0.4 * r, cy - 0.3 * r, cx, cy, rot_)
    o.append(f'<ellipse cx="{F(hx)}" cy="{F(hy)}" rx="{F(0.12 * r)}" ry="{F(0.26 * r)}" fill="#FFFFFF" opacity="0.5" transform="rotate({F(20 + rot_)} {F(hx)} {F(hy)})"/>')
    sx, sy = rot(cx, cy - 0.75 * r, cx, cy, rot_)
    tx, ty = rot(cx + 0.12 * r, cy - 1.15 * r, cx, cy, rot_)
    o.append(f'<path d="M {F(sx)} {F(sy)} Q {F(sx - 0.05 * r)} {F((sy + ty) / 2)} {F(tx)} {F(ty)}" stroke="#5A3A1E" stroke-width="{F(max(1, r * 0.1))}" fill="none" stroke-linecap="round"/>')
    if leaf:
        lf = blob((sx + tx) / 2 + r * 0.3, (sy + ty) / 2, r * 0.32, r * 0.13, seed, 0.1, 10, rot=-25 + rot_)
        o.append(f'<path d="{lf}" fill="#6E8A3E"/><path d="{lf}" fill="none" stroke="#3E5A22" stroke-width="0.7"/>')
    return "".join(o)


def thanksgiving_scene(u="tg"):
    back = []
    # a warm room: wall washed by lamp light, darker toward the edges, a hint of a window at the upper left
    back.append(sky_rect(u + "-wall", [(0, "#6E4A3A", 1), (0.5, "#A86E4E", 1), (1, "#7A4E38", 1)], (0, 0, 380, 330)))
    back.append(f'<defs>{rgrad(u + "-lamp", 300, 150, 230, [(0, "#FFD98A", 0.9), (0.4, "#F2B45E", 0.45), (1, "#F2B45E", 0)])}</defs><circle cx="300" cy="150" r="230" fill="url(#{u}-lamp)"/>')
    win = poly([(40, 44), (124, 44), (124, 134), (40, 134)])
    back.append(f'<path d="{win}" fill="#3E3A5E"/><path d="{win}" fill="none" stroke="#6E4E3A" stroke-width="5"/><path d="M 82 44 l 0 90 M 40 90 l 84 0" stroke="#6E4E3A" stroke-width="3"/>')
    back.append(speck(8, (42, 46, 122, 132), ["#FFF6D0", "#E9D9FF"], 8, r=(0.5, 1.1), op=(0.4, 0.9)) + '<circle cx="104" cy="64" r="6" fill="#F6E6B0" opacity="0.9"/>')
    back.append(f'<path d="M 40 134 Q 82 126 124 134 L 124 142 L 40 142 Z" fill="#8A6648"/>')
    # the table: top seen from a little above, a linen runner, the front edge and a leg; grain runs left-right
    top = smooth_closed(jitter([(0, 212), (380, 196), (380, 262), (0, 282)], 2, 0.6))
    back.append(paint(u + "-top", top, (0, 194, 380, 284), "#8A5A36", 3, tints=["#5E3A1E", "#B07A4A", "#A86E3E", "#6E4628"], angle=-3, n=170, length=(16, 60), width=(0.6, 2.4), op=(0.25, 0.5), ink_col="#4A2E18", ink_w=1.3, curve=0.03))
    back.append(lines([f"M 0 {F(226 + k * 16)} Q 190 {F(218 + k * 16)} 380 {F(206 + k * 16)}" for k in range(3)], "#5E3A1E", 1.0, 0.35))
    front = smooth_closed(jitter([(0, 282), (380, 262), (380, 284), (0, 304)], 4, 0.6))
    back.append(paint(u + "-fr", front, (0, 260, 380, 306), "#5E3A1E", 5, tints=["#3E2410", "#8A5A36"], angle=-3, n=60, length=(16, 50), width=(0.6, 2), op=(0.25, 0.5), ink_col="#3A2210", ink_w=1.2, curve=0.03))
    back.append(f'<path d="M 0 282 Q 190 272 380 262" stroke="#C99A62" stroke-width="1.8" opacity="0.55" fill="none"/>')
    back.append(paint(u + "-leg", poly([(300, 284), (324, 282), (322, 330), (302, 330)]), (298, 280, 326, 332), "#4E2E16", 6, angle=-88, n=20, ink_col="#2E1A0C", ink_w=1.1))
    runner = smooth_closed(jitter([(96, 206), (290, 198), (310, 268), (76, 278)], 7, 0.8))
    back.append(paint(u + "-run", runner, (74, 196, 312, 280), "#E9DCC4", 8, tints=["#C9B89A", "#FFFFFF", "#D9C8A8"], angle=-3, n=90, length=(10, 40), width=(0.6, 2), op=(0.2, 0.45), ink_col="#9A8A6E", ink_w=1.1, curve=0.05))
    back.append(f'<clipPath id="{u}-rc"><path d="{runner}"/></clipPath><g clip-path="url(#{u}-rc)" stroke="#B8532E" stroke-width="1.6" opacity="0.7" fill="none">'
                + "".join(f'<path d="M {F(x)} 196 L {F(x - 20)} 282"/>' for x in (108, 114, 290, 296)) + "</g>")
    back.append(shade(u + "-rs", runner, "#8A7A5E", 0, 1, k=4, op=0.3))
    o = [vignette(u + "-v", "".join(back), [(200, 190, 185, 140, 0.42), (290, 170, 110, 120, 0.5), (110, 240, 110, 80, 0.4), (130, 100, 110, 90, 0.3)])]
    # centerpiece: jug with wheat and turkey feathers, a small pumpkin and apples, a pie at the front, the lamp at the right
    o.append(shadow(206, 232, 60, 8, 0.2))
    for k, (ang, L, cols) in enumerate(((-134, 96, ("#8A4A26", "#5E2E14", "#E2A23A")), (-112, 112, ("#C2642E", "#7A3A16", "#F2C070")), (-96, 118, ("#A8562A", "#6E3416", "#E2A23A")), (-78, 108, ("#C2642E", "#7A3A16", "#F2C070")), (-58, 90, ("#7A4426", "#4E2810", "#D98A3A")))):
        o.append(feather(f"{u}-ft{k}", 206 + (k - 2) * 5, 200, L, ang, cols, 20 + k))
    for k, (ang, L, c) in enumerate(((-100, 96, "#D9A84E"), (-86, 104, "#E6BC62"), (-114, 84, "#C9933A"), (-72, 84, "#D9A84E"), (-92, 112, "#E6BC62"), (-124, 70, "#C9933A"), (-80, 92, "#D9A84E"))):
        o.append(wheat_stalk(206 + (k - 3) * 3, 196, ang, L, 10 + k, col=c, w=1.0))
    o.append(jug(u + "-jug", 206, 236, 58, 56))
    o.append(pumpkin(u + "-pk", 268, 232, 48, 34, 71, body="#E8792E", dark="#B9531E", light="#F8A85A", lit=(1, -1), vine=False))
    o.append(pumpkin(u + "-pk2", 132, 240, 40, 28, 72, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF", stem="#6B5A2E", lit=(1, -1), vine=False))
    o.append(apple_p(u + "-a1", 160, 254, 11, "#C8323A", 5) + apple_p(u + "-a2", 244, 258, 10, "#D9A23A", 6, rot_=15, leaf=False))
    o.append(pie(u + "-pie", 116, 262, 108))
    o.append(oil_lamp(u + "-lamp", 320, 266, 104))
    o.append(acorn_p(u + "-ac", 178, 278, 10, rot_=-20) + acorn_p(u + "-ac2", 190, 282, 9, rot_=30) + oak_leaf(u + "-ol", 262, 278, 10, "#B8862E", "#7A5418", rot_=70, seed=6)
             + maple(u + "-ml", 74, 290, 9, "#C9442E", "#8E2A1A", rot_=-30, seed=7))
    # a bunch of grapes trailing from the runner edge
    rnd = random.Random(9)
    for j, n in enumerate((4, 3, 2)):
        for i in range(n):
            x, y = 286 + (i - (n - 1) / 2) * 7 + rnd.uniform(-0.5, 0.5), 252 + j * 6.5
            c = mix("#6E3E7E", "#9A6AB0", rnd.uniform(0, 0.4))
            o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="4" fill="{c}" stroke="#3E2048" stroke-width="0.7"/><circle cx="{F(x - 1.2)}" cy="{F(y - 1.3)}" r="1.1" fill="#FFFFFF" opacity="0.55"/>')
    return "".join(o)


def thanksgiving_garland(u="tgg"):
    """Seamless 320 x 74: twine with painted leaves, mini gourds, wheat and dried orange slices."""
    o = []
    d = "M 0 10 C 80 34 240 34 320 10"
    o.append(f'<path d="{d}" stroke="#6E4E2E" stroke-width="3" fill="none" opacity="0.9"/><path d="{d}" stroke="#C9A878" stroke-width="1.1" fill="none" stroke-dasharray="2.5 3.5"/>')
    items = [(26, "maple", "#E8792E", "#B9531E"), (70, "gourd", "#E8792E", None), (112, "orange", None, None), (152, "oak", "#B8862E", "#7A5418"), (196, "gourd", "#F1E6D2", None),
             (238, "wheat", None, None), (278, "maple", "#C9442E", "#8E2A1A"), (308, "gourd", "#7E9A4E", None)]
    gc = {"#E8792E": ("#E8792E", "#B9531E", "#F8A85A"), "#F1E6D2": ("#F1E6D2", "#C9B79A", "#FFFFFF"), "#7E9A4E": ("#7E9A4E", "#5A7432", "#B8CC7A")}
    for k, (x, kind, c, dd) in enumerate(items):
        y = swag_y(x)
        tilt = (-1) ** k * 9
        def item(xx, kind=kind, c=c, dd=dd, y=y, k=k, tilt=tilt):
            out = [f'<path d="M {F(xx)} {F(y)} q {F(tilt * 0.1)} 5 {F(tilt * 0.15)} 8" stroke="#6E4E2E" stroke-width="1.1" fill="none"/>']
            cx, cy = xx + tilt * 0.15, y + 8
            if kind == "maple":
                out.append(f'<g opacity="0.18" transform="translate(2 3)">{maple(f"{u}-sh{k}", cx, cy + 16, 16, INK, INK, rot_=180 + tilt, seed=k, light=INK)}</g>' + maple(f"{u}-m{k}", cx, cy + 16, 16, c, dd, rot_=180 + tilt, seed=k))
            elif kind == "oak":
                out.append(f'<g opacity="0.18" transform="translate(2 3)">{oak_leaf(f"{u}-sho{k}", cx, cy + 14, 15, INK, INK, rot_=180 + tilt, seed=k)}</g>' + oak_leaf(f"{u}-o{k}", cx, cy + 14, 15, c, dd, rot_=180 + tilt, seed=k))
            elif kind == "gourd":
                b, dk_, li = gc[c]
                out.append(f'<ellipse cx="{F(cx + 2)}" cy="{F(cy + 20)}" rx="14" ry="6" fill="{INK}" opacity="0.14"/>')
                out.append(pumpkin(f"{u}-g{k}", cx, cy + 16, 26, 18, 80 + k, body=b, dark=dk_, light=li, stem="#6B5A2E", vine=False))
            elif kind == "wheat":
                for i, ang in enumerate((70, 90, 110)):
                    out.append(wheat_stalk(cx + (i - 1) * 2, cy - 2, ang, 30, 30 + i, col=("#D9A84E", "#E6BC62", "#C9933A")[i], w=0.8))
                out.append(f'<path d="M {F(cx - 5)} {F(cy + 2)} q 5 3 10 0" stroke="#B8532E" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
            else:  # dried orange slice
                r = 11
                out.append(f'<circle cx="{F(cx + 2)}" cy="{F(cy + r + 3)}" r="{r}" fill="{INK}" opacity="0.14"/>')
                out.append(f'<circle cx="{F(cx)}" cy="{F(cy + r)}" r="{r}" fill="#E8902E"/><circle cx="{F(cx)}" cy="{F(cy + r)}" r="{r - 1.6}" fill="#F6B04A"/><circle cx="{F(cx)}" cy="{F(cy + r)}" r="{r - 3.2}" fill="#FFD27A" opacity="0.9"/>')
                segs = "".join(f'<path d="M {F(cx)} {F(cy + r)} L {F(cx + math.cos(a) * (r - 2))} {F(cy + r + math.sin(a) * (r - 2))}" />' for a in [i * math.pi / 4 for i in range(8)])
                out.append(f'<g stroke="#E8902E" stroke-width="1.2" opacity="0.9">{segs}</g>')
                out.append("".join(f'<path d="M {F(cx + math.cos(a + 0.39) * (r - 3.5))} {F(cy + r + math.sin(a + 0.39) * (r - 3.5))} Q {F(cx + math.cos(a + 0.39) * (r - 6))} {F(cy + r + math.sin(a + 0.39) * (r - 6))} {F(cx + math.cos(a + 0.25) * (r - 4))} {F(cy + r + math.sin(a + 0.25) * (r - 4))}" fill="#FFE9B0" opacity="0.7"/>' for a in [i * math.pi / 4 for i in range(8)]))
                out.append(f'<circle cx="{F(cx)}" cy="{F(cy + r)}" r="{r}" fill="none" stroke="#B9531E" stroke-width="1" opacity="0.7"/>')
            return "".join(out)
        o.append(wrap(item, x, 24))
    return "".join(o)


# ================================================================ CHRISTMAS: a fir by the window, a cat under the tree
def bauble(uid, cx, cy, r, col, seed, cap="#D9C27A", hook=0, lit=(-0.6, -0.8)):
    d = blob(cx, cy, r, r * 1.02, seed, 0.03, 14)
    o = []
    if hook:
        o.append(f'<path d="M {F(cx)} {F(cy - r - 2)} l 0 {F(-hook)}" stroke="#8A7A5A" stroke-width="0.9"/>')
    o.append(f'<path d="{d}" fill="{col}"/>')
    o.append(strokes(uid + "-s", d, (cx - r, cy - r, cx + r, cy + r), [lt(col, 0.25), dk(col, 0.25)], seed, n=int(r * 1.5), angle=-80, length=(r * 0.3, r * 0.9), width=(0.4, r * 0.1), opacity=(0.2, 0.45), curve=0.4))
    o.append(shade(uid, d, dk(col, 0.5), -lit[0], -lit[1], k=r * 0.3, op=0.55))
    o.append(f'<ellipse cx="{F(cx + lit[0] * 0.4 * r)}" cy="{F(cy + lit[1] * 0.4 * r)}" rx="{F(0.2 * r)}" ry="{F(0.3 * r)}" fill="#FFFFFF" opacity="0.8" transform="rotate(30 {F(cx + lit[0] * 0.4 * r)} {F(cy + lit[1] * 0.4 * r)})"/>')
    o.append(f'<path d="M {F(cx - lit[0] * 0.55 * r)} {F(cy + 0.2 * r)} q {F(lit[0] * 0.1 * r)} {F(0.4 * r)} {F(lit[0] * 0.5 * r)} {F(0.6 * r)}" stroke="{lt(col, 0.55)}" stroke-width="{F(max(0.6, r * 0.1))}" fill="none" opacity="0.6" stroke-linecap="round"/>')
    o.append(ink(d, inkc(col), max(0.8, r * 0.1), seed, 1, 0.6))
    o.append(f'<rect x="{F(cx - 0.3 * r)}" y="{F(cy - r - 0.3 * r)}" width="{F(0.6 * r)}" height="{F(0.4 * r)}" rx="1" fill="{cap}" stroke="{dk(cap, 0.4)}" stroke-width="0.6"/>')
    return "".join(o)


def xmas_fir(u, cx, top, base, hw, tiers=6, seed=40, cols=("#2C6448", "#1A4030", "#4C8C62", "#8CC08A"), light=(-1, -0.4)):
    """Full painted fir: drooping tiers with scalloped hems, needle strokes along the branches, dark undersides,
    a lit edge toward the window, a deeper core behind the trunk."""
    base_c, darkc, light_c, hi = cols
    H = base - top
    o = []
    o.append(f'<path d="M {F(cx - 9)} {F(base - 12)} L {F(cx + 9)} {F(base - 12)} L {F(cx + 11)} {F(base + 14)} L {F(cx - 11)} {F(base + 14)} Z" fill="#5E3A1E"/>')
    for i in reversed(range(tiers)):
        t0, t1 = i / tiers, (i + 1) / tiers
        apex = top + H * max(0, t0 - 0.08)
        bot = top + H * (t1 ** 0.92) + 6
        w = hw * (0.3 + 0.7 * t1 ** 0.9)
        rnd = random.Random(seed + i)
        n_sc = 3 + i
        pts = [(cx, apex), (cx + w * 0.35, apex + (bot - apex) * 0.4), (cx + w * 0.78, bot - 10), (cx + w, bot + 2)]
        for j in range(1, n_sc):
            x = cx + w - 2 * w * j / n_sc
            pts.append((x + w / n_sc * 0.5 + rnd.uniform(-2, 2), bot - 4 + rnd.uniform(-2, 1)))
            pts.append((x + rnd.uniform(-2, 2), bot + 6 + rnd.uniform(-1, 3)))
        pts += [(cx - w, bot + 2), (cx - w * 0.78, bot - 10), (cx - w * 0.35, apex + (bot - apex) * 0.4)]
        d = smooth_closed(pts)
        box = bbox(pts)
        o.append(wash(d, base_c, seed + i, 2, 0.8, 0.5))
        n = int(w * 1.1)
        o.append(strokes(f"{u}-l{i}", d, (box[0], box[1], cx + 3, box[3]), [light_c, darkc, hi, base_c], seed + 10 + i, n=n, angle=155, length=(5, 16), width=(0.5, 1.5), opacity=(0.35, 0.8), curve=0.3))
        o.append(strokes(f"{u}-r{i}", d, (cx - 3, box[1], box[2], box[3]), [light_c, darkc, hi, base_c], seed + 20 + i, n=n, angle=25, length=(5, 16), width=(0.5, 1.5), opacity=(0.35, 0.8), curve=0.3))
        o.append(shade(f"{u}-s{i}", d, darkc, 0.1, 1, k=7, op=0.6))
        o.append(rim(f"{u}-h{i}", d, hi, light[0], light[1], k=1.6, op=0.55))
        o.append(f'<path d="{poly([(cx - w * 0.16, bot + 4), (cx, apex + (bot - apex) * 0.5), (cx + w * 0.16, bot + 4)])}" fill="{darkc}" opacity="0.45"/>')
        o.append(ink(d, darkc, 1.2, seed + 30 + i, 1, 0.5))
    return "".join(o)


def gift_p(uid, x, y, w, h, dd, col, rib, seed, pattern=None, pcol="#FFFFFF", bow=True):
    front = jitter([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed, 0.8)
    top = [(x, y), (x + dd, y - dd * 0.55), (x + w + dd, y - dd * 0.55), (x + w, y)]
    side = [(x + w, y), (x + w + dd, y - dd * 0.55), (x + w + dd, y + h - dd * 0.55), (x + w, y + h)]
    fd, td, sd = poly(front), poly(top), poly(side)
    o = [shadow(x + w / 2 + dd / 2, y + h, w * 0.66, 4, 0.2)]
    o.append(paint(uid + "-f", fd, bbox(front), col, seed, angle=-80, n=int(w * h / 40), ink_w=0))
    o.append(f'<path d="{sd}" fill="{dk(col, 0.25)}"/><path d="{td}" fill="{lt(col, 0.22)}"/>')
    o.append(strokes(uid + "-ts", td, bbox(top), [lt(col, 0.4), col], seed + 5, n=12, angle=-30, length=(4, 12), width=(0.5, 1.4), opacity=(0.2, 0.45)))
    if pattern == "dots":
        rnd = random.Random(seed)
        o.append(f'<clipPath id="{uid}-pc"><path d="{fd} {sd}"/></clipPath><g clip-path="url(#{uid}-pc)" fill="{pcol}" opacity="0.85">'
                 + "".join(f'<circle cx="{F(x + (i % 6) * w / 4.5 + (j % 2) * w / 9)}" cy="{F(y + j * h / 4 + 3)}" r="{F(rnd.uniform(1.4, 2))}"/>' for i in range(7) for j in range(5)) + "</g>")
    elif pattern == "stripes":
        o.append(f'<clipPath id="{uid}-pc"><path d="{fd} {sd} {td}"/></clipPath><g clip-path="url(#{uid}-pc)" stroke="{pcol}" stroke-width="2.4" opacity="0.8">'
                 + "".join(f'<path d="M {F(x - h + i * 9)} {F(y + h + 4)} l {F(h + 20)} {F(-h - 20)}"/>' for i in range(int((w + h + dd) / 9) + 4)) + "</g>")
    rw = max(3, w * 0.13)
    mx = x + w / 2
    o.append(f'<path d="{poly([(mx - rw / 2, y), (mx + rw / 2, y), (mx + rw / 2, y + h), (mx - rw / 2, y + h)])}" fill="{rib}"/>')
    o.append(f'<path d="{poly([(mx - rw / 2, y), (mx + rw / 2, y), (mx + rw / 2 + dd, y - dd * 0.55), (mx - rw / 2 + dd, y - dd * 0.55)])}" fill="{lt(rib, 0.15)}"/>')
    o.append(f'<path d="{poly([(x + w, y + h / 2 - rw / 2), (x + w + dd, y + h / 2 - rw / 2 - dd * 0.55), (x + w + dd, y + h / 2 + rw / 2 - dd * 0.55), (x + w, y + h / 2 + rw / 2)])}" fill="{dk(rib, 0.2)}"/>')
    o.append(f'<path d="M {F(mx - rw / 2 + 1)} {F(y + 1)} L {F(mx - rw / 2 + 1)} {F(y + h - 1)}" stroke="{lt(rib, 0.45)}" stroke-width="0.9" opacity="0.8"/>')
    o.append(shade(uid + "-sh", fd, dk(col, 0.5), -1, 0.3, k=w * 0.1, op=0.3))
    o.append(ink(fd + " " + sd + " " + td, inkc(col), 1.1, seed, 1, 0.6))
    if bow:
        bx, by = mx + dd / 2, y - dd * 0.28
        s = max(6, w * 0.22)
        for sg in (-1, 1):
            lp = blob(bx + sg * s * 0.55, by - s * 0.25, s * 0.55, s * 0.32, seed + sg, 0.06, 12, rot=sg * -20)
            o.append(paint(f"{uid}-bw{sg}", lp, (bx - s * 1.2, by - s, bx + s * 1.2, by + s * 0.2), rib, seed + 3 + sg, n=8, ink_w=0.9, angle=sg * 20))
            o.append(f'<path d="M {F(bx)} {F(by)} q {F(sg * s * 0.3)} {F(s * 0.5)} {F(sg * s * 0.55)} {F(s * 0.85)}" stroke="{rib}" stroke-width="{F(s * 0.22)}" stroke-linecap="round" fill="none"/>')
        o.append(f'<circle cx="{F(bx)}" cy="{F(by - s * 0.15)}" r="{F(s * 0.2)}" fill="{dk(rib, 0.15)}" stroke="{inkc(rib)}" stroke-width="0.7"/>')
    return "".join(o)


def cat_curled(u, cx, cy, s=1.0, seed=17, col="#D98A3A", dark="#9A5A1E", light="#F2C080", stripes="#8A4A14"):
    """Ginger tabby curled up asleep: an oval body, the head resting on the paws, tail wrapped round, tabby markings."""
    def p(x, y):
        return (cx + x * s, cy + y * s)
    body = [p(-44, 4), p(-40, -16), p(-22, -28), p(6, -30), p(30, -22), p(40, -6), p(34, 10), p(6, 18), p(-24, 16)]
    bd = smooth_closed(body)
    o = [shadow(cx, cy + 16 * s, 50 * s, 7 * s, 0.22)]
    o.append(paint(u + "-b", bd, bbox(body), col, seed, tints=[dark, light, lt(col, 0.2)], angle=-30, n=90, ink_col="#5E3A14", ink_w=1.3 * s, length=(4 * s, 14 * s), width=(0.5, 1.5 * s), curve=0.35))
    # lighter belly / lower flank, then tabby stripes: tapered strokes falling from the spine
    o.append(f'<clipPath id="{u}-sc"><path d="{bd}"/></clipPath><g clip-path="url(#{u}-sc)">')
    o.append(f'<path d="{blob(cx - 6 * s, cy + 10 * s, 36 * s, 9 * s, seed + 4, 0.08, 12)}" fill="{light}" opacity="0.5"/>')
    st = []
    for k, x in enumerate((-30, -20, -10, 0, 10, 20)):
        L = (14 + 4 * (k % 2)) * s
        x0, y0 = p(x, -30 + 2 * abs(x) / 10)
        st.append(f'<path d="M {F(x0)} {F(y0)} Q {F(x0 - 4 * s + 1.6 * s)} {F(y0 + L * 0.5)} {F(x0 - 6 * s)} {F(y0 + L)} Q {F(x0 - 4 * s - 1.6 * s)} {F(y0 + L * 0.5)} {F(x0)} {F(y0)} Z" fill="{stripes}" opacity="0.55"/>')
    o.append("".join(st) + "</g>")
    o.append(shade(u + "-bs", bd, dark, -0.5, 1, k=6 * s, op=0.4) + rim(u + "-br", bd, "#FFE6B0", 0.8, -0.8, k=1.8 * s, op=0.6))
    # tail wrapping along the front
    tail = smooth_open([p(30, 12), p(10, 21), p(-16, 21), p(-38, 15), p(-48, 3)])
    o.append(f'<path d="{tail}" stroke="#5E3A14" stroke-width="{F(10.6 * s)}" fill="none" stroke-linecap="round" opacity="0.35" transform="translate(0 {F(1.6 * s)})"/><path d="{tail}" stroke="{col}" stroke-width="{F(8.5 * s)}" fill="none" stroke-linecap="round"/>'
             f'<path d="{tail}" stroke="{stripes}" stroke-width="{F(8.5 * s)}" fill="none" stroke-linecap="butt" stroke-dasharray="{F(4 * s)} {F(10 * s)}" opacity="0.5"/>'
             f'<path d="{tail}" stroke="{light}" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round" opacity="0.7" transform="translate(0 {F(-2.8 * s)})"/>')
    # head resting on the paws at the right, a little bigger than life so the face reads
    hx, hy = p(28, -2)
    head = blob(hx, hy, 18 * s, 15.5 * s, seed + 1, 0.04, 14)
    ears = poly([p(16, -12), p(12, -30), p(27, -17)]) + " " + poly([p(32, -17), p(44, -30), p(43, -12)])
    o.append(f'<path d="{ears}" fill="{col}" stroke="#5E3A14" stroke-width="{F(1.1 * s)}" stroke-linejoin="round"/>')
    o.append(f'<path d="{poly([p(17, -14), p(15, -25), p(24, -17)])}" fill="#E9A8A0" opacity="0.8"/><path d="{poly([p(34, -17), p(41, -26), p(41, -14)])}" fill="#E9A8A0" opacity="0.8"/>')
    o.append(paint(u + "-h", head, (hx - 19 * s, hy - 17 * s, hx + 19 * s, hy + 17 * s), col, seed + 2, tints=[dark, light], angle=-90, n=34, ink_col="#5E3A14", ink_w=1.2 * s, length=(3 * s, 8 * s), width=(0.5, 1.2 * s)))
    o.append(f'<path d="{blob(hx, hy + 7 * s, 11 * s, 6 * s, seed + 5, 0.08, 10)}" fill="{light}" opacity="0.55"/>')
    o.append(f'<path d="M {F(hx - 3 * s)} {F(hy - 14 * s)} l 0 {F(7 * s)} M {F(hx + 3 * s)} {F(hy - 14 * s)} l 0 {F(7 * s)} M {F(hx - 9 * s)} {F(hy - 12 * s)} l 1 {F(6 * s)} M {F(hx + 9 * s)} {F(hy - 12 * s)} l -1 {F(6 * s)}" stroke="{stripes}" stroke-width="{F(2 * s)}" stroke-linecap="round" opacity="0.6"/>')
    o.append(rim(u + "-hr", head, "#FFE6B0", 0.8, -0.8, k=1.6 * s, op=0.6))
    o.append(f'<path d="M {F(hx - 11 * s)} {F(hy + 0.5 * s)} q {F(3.5 * s)} {F(3.4 * s)} {F(7 * s)} 0 M {F(hx + 4 * s)} {F(hy + 0.5 * s)} q {F(3.5 * s)} {F(3.4 * s)} {F(7 * s)} 0" stroke="#3A2210" stroke-width="{F(1.5 * s)}" fill="none" stroke-linecap="round"/>')
    nx, ny = hx, hy + 6.5 * s
    o.append(f'<path d="M {F(nx - 2.4 * s)} {F(ny)} L {F(nx + 2.4 * s)} {F(ny)} L {F(nx)} {F(ny + 2.4 * s)} Z" fill="#E59AB0"/>')
    o.append(f'<path d="M {F(nx)} {F(ny + 2.4 * s)} q {F(-2 * s)} {F(2.6 * s)} {F(-4.5 * s)} {F(0.8 * s)} M {F(nx)} {F(ny + 2.4 * s)} q {F(2 * s)} {F(2.6 * s)} {F(4.5 * s)} {F(0.8 * s)}" stroke="#5E3A14" stroke-width="{F(1 * s)}" fill="none" stroke-linecap="round"/>')
    o.append(f'<g stroke="#FFF4E0" stroke-width="{F(0.8 * s)}" opacity="0.85" stroke-linecap="round" fill="none">' + "".join(f'<path d="M {F(nx + sg * 6 * s)} {F(ny + dy * s)} q {F(sg * 8 * s)} {F(dl * s * 0.3)} {F(sg * 15 * s)} {F(dl * s)}"/>' for sg in (-1, 1) for dy, dl in ((-0.5, -3), (2.5, 1))) + "</g>")
    o.append(f'<path d="{blob(*p(14, 15), 9 * s, 4.5 * s, seed + 3, 0.06, 9)}" fill="{lt(col, 0.1)}" stroke="#5E3A14" stroke-width="{F(0.9 * s)}"/><path d="M {F(p(11, 16)[0])} {F(p(11, 16)[1])} l 0 3 M {F(p(15, 16)[0])} {F(p(15, 16)[1])} l 0 3" stroke="#5E3A14" stroke-width="{F(0.8 * s)}"/>')
    return "".join(o)


def window_snow(u, x, y, w, h):
    """Window with night snowfall outside: frame, six panes, a snowy hill with a lit cottage and pines, snow on the sill."""
    o = []
    o.append(f'<defs>{lgrad(u + "-ng", 0, y, 0, y + h, [(0, "#1E2A58", 1), (0.6, "#3A4A80", 1), (1, "#6A7AA8", 1)])}</defs><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{u}-ng)"/>')
    hill, line = ridge([(x, y + h * 0.7), (x + w * 0.4, y + h * 0.62), (x + w, y + h * 0.68)], 3, y + h, amp=4)
    o.append(f'<clipPath id="{u}-wc"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#{u}-wc)">')
    o.append(f'<path d="{hill}" fill="#DCE6F4"/><path d="{hill}" fill="#AFC4DC" opacity="0.5" transform="translate(0 6)"/>')
    for k, (tx, th) in enumerate(((x + w * 0.1, h * 0.26), (x + w * 0.22, h * 0.34), (x + w * 0.86, h * 0.3), (x + w * 0.72, h * 0.2))):
        o.append(conifer_p(f"{u}-wp{k}", tx, y + h * 0.7, th, 50 + k, cols=("#2A4A48", "#1A3030", "#3E6A62", "#7A9A94"), snow=("#F4F8FF", "#AFC4DC"), width=0.42))
    cx_, cy_ = x + w * 0.5, y + h * 0.66
    o.append(f'<path d="{poly([(cx_ - 14, cy_), (cx_ + 14, cy_), (cx_ + 14, cy_ - 12), (cx_, cy_ - 22), (cx_ - 14, cy_ - 12)])}" fill="#4E3A34"/>'
             f'<path d="{poly([(cx_ - 16, cy_ - 11), (cx_, cy_ - 24), (cx_ + 16, cy_ - 11), (cx_ + 12, cy_ - 9), (cx_, cy_ - 19), (cx_ - 12, cy_ - 9)])}" fill="#F4F8FF"/>'
             f'<rect x="{F(cx_ - 9)}" y="{F(cy_ - 9)}" width="6" height="6" fill="#FFD66A"/><rect x="{F(cx_ + 3)}" y="{F(cy_ - 9)}" width="6" height="6" fill="#FFD66A"/>'
             f'<rect x="{F(cx_ + 6)}" y="{F(cy_ - 24)}" width="4" height="7" fill="#4E3A34"/>' + glow(u + "-cg", cx_, cy_ - 6, 22, 14, "#FFD66A", 0.5))
    o.append(speck(12, (x, y, x + w, y + h), ["#FFFFFF", "#DCE6F4"], 70, r=(0.6, 1.8), op=(0.5, 1)))
    o.append("</g>")
    # frame and muntins, frost in the pane corners, snow on the outer sill
    fr = "#F4EEE2"
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{fr}" stroke-width="9"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#B8A890" stroke-width="1"/>'
             f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" fill="none" stroke="#B8A890" stroke-width="1.2"/>')
    o.append(f'<path d="M {F(x + w / 2)} {y} l 0 {h} M {x} {F(y + h / 3)} l {w} 0 M {x} {F(y + 2 * h / 3)} l {w} 0" stroke="{fr}" stroke-width="5"/><path d="M {F(x + w / 2)} {y} l 0 {h} M {x} {F(y + h / 3)} l {w} 0 M {x} {F(y + 2 * h / 3)} l {w} 0" stroke="#B8A890" stroke-width="0.8" opacity="0.7"/>')
    for px, py in ((x + 4, y + h / 3 - 3), (x + w / 2 + 3, y + 2 * h / 3 - 3), (x + 4, y + h - 3), (x + w / 2 + 3, y + h - 3), (x + w - 4, y + h / 3 - 3)):
        sg = 1 if px < x + w / 2 + 2 else -1
        o.append(f'<path d="M {F(px)} {F(py)} q {F(sg * 10)} 0 {F(sg * 14)} -12 q -2 8 -14 12 Z" fill="#FFFFFF" opacity="0.55"/>')
    sill = smooth_closed([(x - 12, y + h + 4), (x + w + 12, y + h + 4), (x + w + 12, y + h + 14), (x - 12, y + h + 14)])
    o.append(paint(u + "-sill", sill, (x - 14, y + h + 2, x + w + 14, y + h + 16), "#E9E0D0", 4, tints=["#C9BCA8", "#FFFFFF"], angle=0, n=30, length=(10, 30), width=(0.6, 1.6), op=(0.2, 0.4), ink_col="#9A8A72", ink_w=1.0))
    return "".join(o)


def christmas_scene(u="xm"):
    back = []
    back.append(sky_rect(u + "-wall", [(0, "#8A6E5A", 1), (0.5, "#B89A80", 1), (1, "#7A5E4A", 1)], (0, 0, 380, 330)))
    back.append(f'<defs>{rgrad(u + "-tg", 262, 170, 190, [(0, "#FFE2A0", 0.85), (0.5, "#F2C070", 0.35), (1, "#F2C070", 0)])}</defs><circle cx="262" cy="170" r="190" fill="url(#{u}-tg)"/>')
    # floor boards with a round braided rug
    floor = smooth_closed(jitter([(0, 252), (380, 246), (380, 330), (0, 330)], 2, 0.6))
    back.append(paint(u + "-fl", floor, (0, 244, 380, 332), "#8A5A36", 3, tints=["#5E3A1E", "#B07A4A", "#A86E3E"], angle=-2, n=140, length=(16, 60), width=(0.6, 2.4), op=(0.25, 0.5), ink_col="#4A2E18", ink_w=1.2, curve=0.03))
    back.append(lines([f"M 0 {F(268 + k * 18)} L 380 {F(262 + k * 18)}" for k in range(4)], "#5E3A1E", 1.0, 0.4))
    rug = blob(150, 300, 118, 26, 5, 0.02, 24)
    back.append(paint(u + "-rug", rug, (30, 272, 270, 328), "#9A3A34", 6, tints=["#6E2420", "#C9605A", "#D9A05A"], angle=-2, n=60, length=(8, 30), width=(0.6, 2), op=(0.25, 0.5), ink_col="#4A1A16", ink_w=1.1))
    back.append(f'<clipPath id="{u}-rc"><path d="{rug}"/></clipPath><g clip-path="url(#{u}-rc)" fill="none" stroke-width="2.4">' + "".join(f'<ellipse cx="150" cy="300" rx="{F(118 - k * 14)}" ry="{F(26 - k * 3.1)}" stroke="{["#D9A05A", "#2F6B4F", "#E9DCC4"][k % 3]}" opacity="0.7"/>' for k in range(1, 8)) + "</g>")
    back.append(window_snow(u + "-w", 44, 48, 108, 150))
    # a curtain gathered at the left of the window
    cur = smooth_closed(jitter([(14, 36), (46, 36), (44, 120), (52, 200), (18, 212), (10, 120)], 7, 1))
    back.append(paint(u + "-cur", cur, (8, 34, 54, 214), "#B8323A", 8, tints=["#7A1A20", "#E86060", "#C9403E"], angle=-88, n=60, length=(10, 40), width=(0.8, 2.6), op=(0.25, 0.5), ink_col="#5E1418", ink_w=1.2, curve=0.05))
    back.append(f'<path d="M 12 126 q 18 -8 38 0" stroke="#E2B04A" stroke-width="4" fill="none" stroke-linecap="round"/>')
    o = [vignette(u + "-v", "".join(back), [(200, 185, 185, 140, 0.45), (262, 170, 118, 130, 0.55), (110, 240, 110, 80, 0.4), (90, 110, 100, 95, 0.4)])]
    # the tree with its decorations
    o.append(xmas_fir(u + "-t", 266, 54, 258, 96))
    for k, (y0, y1, hw) in enumerate(((104, 118, 32), (150, 170, 52), (198, 222, 74))):
        d = f"M {F(266 - hw)} {F(y0)} Q 266 {F(y1 + 14)} {F(266 + hw)} {F(y0 + 8)}"
        o.append(f'<path d="{d}" stroke="#7A5212" stroke-width="3.4" fill="none" stroke-dasharray="0.1 6.5" stroke-linecap="round" transform="translate(0.6 1.2)" opacity="0.6"/>'
                 f'<path d="{d}" stroke="#F2C14E" stroke-width="3.4" fill="none" stroke-dasharray="0.1 6.5" stroke-linecap="round"/>')
    lights = [(250, 92), (284, 100), (236, 136), (298, 142), (266, 126), (216, 186), (318, 184), (246, 176), (292, 206), (200, 236), (330, 238), (268, 246), (232, 222), (306, 230)]
    o.append(f'<defs><radialGradient id="{u}-lg"><stop offset="0" stop-color="#FFF2B0" stop-opacity="0.95"/><stop offset="1" stop-color="#FFD25E" stop-opacity="0"/></radialGradient></defs>')
    for x, y in lights:
        o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="url(#{u}-lg)"/><circle cx="{x}" cy="{y}" r="2.1" fill="#FFF6C8"/>')
    balls = [(256, 78, 6.5, "#C8323A"), (280, 116, 7, "#3E7CB1"), (242, 124, 6.5, "#E9B949"), (222, 166, 7.5, "#C8323A"), (304, 170, 7.5, "#F3E6D0"), (266, 160, 7, "#C8323A"),
             (198, 222, 8, "#3E7CB1"), (244, 212, 8, "#E9B949"), (292, 206, 8, "#C8323A"), (334, 224, 8, "#E9B949"), (222, 256, 8, "#F3E6D0"), (310, 258, 8, "#3E7CB1"), (180, 262, 7, "#C8323A")]
    for k, (x, y, r, c) in enumerate(balls):
        o.append(bauble(f"{u}-ba{k}", x, y, r, c, 50 + k))
    o.append(glow(u + "-sg", 266, 50, 40, 40, "#FFE08A", 0.85))
    sp = [(266 + 17 * math.cos(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.46), 50 + 17 * math.sin(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.46)) for i in range(10)]
    sd = poly(sp)
    o.append(paint(u + "-star", sd, bbox(sp), "#F2C14E", 9, tints=["#FFE59A", "#D29A22", "#FFF4C8"], angle=-60, n=20, ink_col="#8A5E12", ink_w=1.3))
    # presents under the tree and the cat asleep on the rug
    o.append(gift_p(u + "-g1", 300, 272, 50, 36, 14, "#C8323A", "#F2C14E", 61, pattern="dots", pcol="#FFF3DE"))
    o.append(gift_p(u + "-g2", 204, 286, 40, 26, 12, "#2F7A57", "#C8323A", 62, pattern="stripes", pcol="#F3E6D0"))
    o.append(gift_p(u + "-g3", 258, 292, 32, 22, 10, "#F3E6D0", "#3E7CB1", 63))
    o.append(cat_curled(u + "-cat", 124, 290, 1.0))
    # a mug of cocoa on the sill and a candy cane fallen by the presents
    o.append(f'<path d="M 92 202 l 18 0 l -2 16 l -14 0 Z" fill="#2F6B4F" stroke="#163626" stroke-width="1"/><path d="M 110 206 q 8 0 6 8 q -1 3 -5 3" stroke="#163626" stroke-width="2" fill="none"/>'
             f'<path d="M 94 204 l 14 0 l -1 3 l -12 0 Z" fill="#6E4628"/>' + lines(["M 98 196 c -4 -6 4 -8 0 -14", "M 104 198 c 4 -6 -4 -8 0 -14"], "#FFFFFF", 1.6, 0.6))
    cc = "M 46 300 L 46 278 A 7 7 0 0 1 60 278 L 60 284"
    o.append(f'<g transform="rotate(-70 46 300)"><path d="{cc}" stroke="#7A1218" stroke-width="7" fill="none" stroke-linecap="round"/><path d="{cc}" stroke="#FFF8F0" stroke-width="5.4" fill="none" stroke-linecap="round"/>'
             f'<path d="{cc}" stroke="#D2323A" stroke-width="5.4" fill="none" stroke-dasharray="4.5 4.5"/></g>')
    return "".join(o)


def pinecone(uid, cx, cy, s, rot_, seed=3):
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    body = blob(cx, cy, 0.55 * s, 0.8 * s, seed, 0.04, 14)
    o.append(f'<path d="{body}" fill="#5E3A1E"/>')
    rnd = random.Random(seed)
    for row in range(5):
        y = cy - 0.6 * s + row * 0.3 * s
        n = 3 if row in (0, 4) else 4
        for i in range(n):
            x = cx + (i - (n - 1) / 2) * 0.28 * s
            d = f"M {F(x - 0.14 * s)} {F(y)} Q {F(x)} {F(y + 0.3 * s)} {F(x + 0.14 * s)} {F(y)} Q {F(x)} {F(y - 0.08 * s)} {F(x - 0.14 * s)} {F(y)} Z"
            o.append(f'<path d="{d}" fill="{rnd.choice(["#8A5A32", "#A8743E", "#7A4E28"])}" stroke="#3E2410" stroke-width="{F(max(0.5, s * 0.04))}"/><path d="M {F(x - 0.08 * s)} {F(y + 0.12 * s)} q {F(0.08 * s)} {F(0.06 * s)} {F(0.16 * s)} 0" stroke="#D9B080" stroke-width="{F(max(0.5, s * 0.04))}" fill="none" opacity="0.7"/>')
    o.append("</g>")
    return "".join(o)


def holly(uid, cx, cy, s, rot_, seed=5):
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    for sg in (-1, 1):
        pts = [(cx, cy), (cx + sg * 0.3 * s, cy - 0.25 * s), (cx + sg * 0.55 * s, cy - 0.12 * s), (cx + sg * 0.8 * s, cy - 0.28 * s), (cx + sg * 1.0 * s, cy), (cx + sg * 0.8 * s, cy + 0.28 * s), (cx + sg * 0.55 * s, cy + 0.12 * s), (cx + sg * 0.3 * s, cy + 0.25 * s)]
        d = poly(jitter(pts, seed + sg, 0.4))
        o.append(f'<path d="{d}" fill="#2F6B4F"/><path d="{d}" fill="#4C8C62" opacity="0.5" transform="translate({F(-sg * 0.6)} -1)"/><path d="M {F(cx)} {F(cy)} L {F(cx + sg * 0.95 * s)} {F(cy)}" stroke="#8CC08A" stroke-width="{F(max(0.6, s * 0.05))}" opacity="0.8"/>' + ink(d, "#163626", max(0.6, s * 0.05), seed, 1, 0.6))
    for dx, dy in ((0, -0.1), (-0.22, 0.2), (0.22, 0.2)):
        o.append(f'<circle cx="{F(cx + dx * s)}" cy="{F(cy + dy * s)}" r="{F(0.2 * s)}" fill="#C8323A" stroke="#6E1418" stroke-width="0.6"/><circle cx="{F(cx + dx * s - 0.06 * s)}" cy="{F(cy + dy * s - 0.07 * s)}" r="{F(0.06 * s)}" fill="#FFFFFF" opacity="0.8"/>')
    o.append("</g>")
    return "".join(o)


def christmas_garland(u="xg"):
    """Seamless 320 x 74: a pine rope with pinecones, holly, glowing warm bulbs and a red bow at the hanging point."""
    o = []
    rnd = random.Random(5)
    layers = [("#163626", 220, 1.9, 0.9), ("#2F6B4F", 260, 1.5, 0.95), ("#4C8C62", 200, 1.2, 0.9), ("#8CC08A", 90, 1.0, 0.85)]
    for col, n, w, op in layers:
        segs = []
        for _ in range(n):
            x = rnd.uniform(0, TW)
            y = swag_y(x) + rnd.uniform(-5, 5)
            a = rnd.uniform(0, 2 * math.pi)
            L = rnd.uniform(5, 11)
            dx, dy = L * math.cos(a), L * math.sin(a) * 0.8
            for sh in (0, TW, -TW):
                xx = x + sh
                if -12 < xx < TW + 12:
                    segs.append(f"M {F(xx)} {F(y)} q {F(dx * 0.5 + rnd.uniform(-2, 2))} {F(dy * 0.5 + 1)} {F(dx)} {F(dy)}")
        o.append(f'<path d="{" ".join(segs)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="{op}" fill="none"/>')
    o.append(pinecone(u + "-pc1", 104, swag_y(104) + 6, 11, swag_slope(104) + 70) + pinecone(u + "-pc2", 232, swag_y(232) + 6, 11, swag_slope(232) + 100))
    o.append(holly(u + "-h1", 60, swag_y(60) + 4, 12, swag_slope(60) - 10) + holly(u + "-h2", 180, swag_y(180) + 4, 12, 8) + holly(u + "-h3", 272, swag_y(272) + 4, 12, swag_slope(272) + 12))
    for k, (x, c, L) in enumerate(((38, "#C8323A", 10), (132, "#E9B949", 16), (206, "#3E7CB1", 14), (298, "#C8323A", 9))):
        y = swag_y(x)
        o.append(f'<path d="M {F(x)} {F(y)} L {F(x)} {F(y + L)}" stroke="#7A6A4A" stroke-width="0.9"/>')
        o.append(bauble(f"{u}-b{k}", x, y + L + 10, 8.5, c, 80 + k))
    for k, x in enumerate((20, 80, 158, 250, 300)):
        y = swag_y(x) + 2
        o.append(f'<path d="M {F(x)} {F(y)} l 1 6" stroke="#2A2A33" stroke-width="1"/>' + glow(f"{u}-lg{k}", x + 1, y + 10, 10, 10, "#FFD25E", 0.8)
                 + f'<path d="{blob(x + 1, y + 10, 3.2, 4.2, k, 0.05, 10)}" fill="#FFF2B0" stroke="#D9A84E" stroke-width="0.6"/><rect x="{F(x - 1)}" y="{F(y + 4)}" width="4" height="3" fill="#2A2A33"/>')
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


def snowflake_p(uid, cx, cy, r, kind, rot_=0, edge="#8FB6DC"):
    """Painted snowflake with real crystal structure: hexagonal plate, six arms with paired side branches, tip
    crystals; white over a soft blue halo so it reads on cream and on dark brown."""
    arms = []
    for i in range(6):
        a = math.radians(rot_ + i * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        def P(t, off=0.0):
            return cx + (ca * t - sa * off) * r, cy + (sa * t + ca * off) * r
        x1, y1 = P(1)
        arms.append(f"M {F(cx)} {F(cy)} L {F(x1)} {F(y1)}")
        branches = {1: ((0.42, 0.3, 32), (0.68, 0.22, 32)), 2: ((0.5, 0.34, 48),), 3: ((0.36, 0.2, 30), (0.6, 0.26, 30), (0.82, 0.14, 30))}[kind]
        for t, L, ang in branches:
            for sg in (-1, 1):
                bx, by = P(t)
                ex, ey = P(t + L * math.cos(math.radians(ang)), sg * L * math.sin(math.radians(ang)))
                arms.append(f"M {F(bx)} {F(by)} L {F(ex)} {F(ey)}")
    d = " ".join(arms)
    w = max(1.4, r * 0.13)
    o = [f'<path d="{d}" stroke="{edge}" stroke-width="{F(w + 2.4)}" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.85"/>',
         f'<path d="{d}" stroke="#FFFFFF" stroke-width="{F(w)}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>']
    hexd = poly([(cx + 0.24 * r * math.cos(math.radians(rot_ + i * 60)), cy + 0.24 * r * math.sin(math.radians(rot_ + i * 60))) for i in range(6)])
    o.append(f'<path d="{hexd}" fill="#FFFFFF" stroke="{edge}" stroke-width="1.2"/><path d="{poly([(cx + 0.12 * r * math.cos(math.radians(rot_ + i * 60)), cy + 0.12 * r * math.sin(math.radians(rot_ + i * 60))) for i in range(6)])}" fill="none" stroke="{edge}" stroke-width="0.8" opacity="0.8"/>')
    for i in range(6):
        a = math.radians(rot_ + i * 60 - 90)
        tx, ty = cx + math.cos(a) * r, cy + math.sin(a) * r
        if kind == 2:
            o.append(f'<path d="{poly([(tx + 0.1 * r * math.cos(a + 2.1), ty + 0.1 * r * math.sin(a + 2.1)), (tx + 0.12 * r * math.cos(a), ty + 0.12 * r * math.sin(a)), (tx + 0.1 * r * math.cos(a - 2.1), ty + 0.1 * r * math.sin(a - 2.1))])}" fill="#FFFFFF" stroke="{edge}" stroke-width="0.9"/>')
        else:
            o.append(f'<circle cx="{F(tx)}" cy="{F(ty)}" r="{F(w * 0.75)}" fill="#FFFFFF" stroke="{edge}" stroke-width="0.9"/>')
    o.append(f'<path d="{d}" stroke="#E6F1FB" stroke-width="{F(w * 0.4)}" stroke-linecap="round" fill="none" opacity="0.9" transform="translate(-0.4 -0.4)"/>')
    return "".join(o)


def snow_particles():
    return {"snow1": snowflake_p("ps1", 20, 20, 16, 1, 0), "snow2": snowflake_p("ps2", 20, 20, 15, 2, 15), "snow3": snowflake_p("ps3", 20, 20, 14, 3, 5)}


# ================================================================ WINTER: snowman at dusk, cardinal, lanterns
SNOW_SH = "#AFC4DC"
SNOW_INK = "#7D93AE"


def snowball(uid, cx, cy, rx, ry, seed, warm=(-1, -0.3), cool=(0.7, 0.75)):
    d = blob(cx, cy, rx, ry, seed, 0.035, 18)
    box = (cx - rx - 3, cy - ry - 3, cx + rx + 3, cy + ry + 3)
    return (f'<path d="{d}" fill="#F8FAFD"/>'
            + strokes(uid, d, box, ["#DDE7F3", "#FFFFFF", "#C9D8EA", "#E9EFF8"], seed, n=int(rx * 1.4), angle=-20, length=(rx * 0.2, rx * 0.6), width=(0.6, 1.8), opacity=(0.4, 0.8), curve=0.4)
            + shade(uid + "-sh", d, "#9EB4D0", cool[0], cool[1], k=rx * 0.26, op=0.7)
            + shade(uid + "-sh2", d, "#C4A8C8", cool[0] * 0.5, 1, k=rx * 0.12, op=0.45)
            + rim(uid + "-hi", d, "#FFFFFF", -0.4, -0.8, k=2.2, op=0.9)
            + rim(uid + "-wm", d, "#FFE2A8", warm[0], warm[1], k=rx * 0.1, op=0.5)
            + ink(d, SNOW_INK, 1.4, seed, 2, 0.6))


def stick_arm_p(pts, seed, w=5.2):
    d = smooth_open(pts)
    rnd = random.Random(seed)
    tw = []
    for i in (1, 2):
        x, y = pts[i]
        x2, y2 = pts[min(i + 1, len(pts) - 1)]
        a = math.atan2(y2 - y, x2 - x) + rnd.choice([-0.7, 0.7])
        tw.append(f"M {F(x)} {F(y)} l {F(math.cos(a) * 11)} {F(math.sin(a) * 11)}")
    x, y = pts[-1]
    x0, y0 = pts[-2]
    a = math.atan2(y - y0, x - x0)
    for da in (-0.6, 0.5):
        tw.append(f"M {F(x)} {F(y)} l {F(math.cos(a + da) * 9)} {F(math.sin(a + da) * 9)}")
    t = " ".join(tw)
    return (f'<path d="{d}" stroke="#3E2614" stroke-width="{F(w)}" fill="none" stroke-linecap="round"/><path d="{d}" stroke="#7A5232" stroke-width="{F(w * 0.62)}" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="#B88A5A" stroke-width="{F(w * 0.2)}" fill="none" stroke-linecap="round" opacity="0.7" transform="translate(0 -1.2)"/>'
            f'<path d="{t}" stroke="#3E2614" stroke-width="{F(w * 0.6)}" fill="none" stroke-linecap="round"/><path d="{t}" stroke="#7A5232" stroke-width="{F(w * 0.3)}" fill="none" stroke-linecap="round"/>')


def cardinal_p(uid, x, y, s=1.0, flip=False, seed=41):
    """Northern cardinal perched, facing left: plump red body, tall crest, black mask, conical orange bill, wing
    with layered feathers, long tail; (x, y) = feet."""
    def p(px, py):
        return (x + (-px if flip else px) * s, y + py * s)
    body = [p(-12, -20), p(-9, -29), p(0, -33), p(9, -31), p(15, -22), p(14, -11), p(8, -4), p(-4, -2), p(-11, -8)]
    bd = smooth_closed(body)
    tail = smooth_closed([p(10, -12), p(26, -5), p(32, 0), p(27, 3), p(10, -3)])
    crest = smooth_closed([p(-6, -31), p(-4, -40), p(0, -44), p(4, -40), p(6, -32), p(0, -29)])
    wing = smooth_closed([p(-1, -26), p(10, -24), p(18, -12), p(10, -6), p(0, -12)])
    o = [f'<path d="{tail}" fill="#8E161C"/>' + ink(tail, "#4E080C", 0.9 * s, seed, 1, 0.6)
         + f'<path d="{smooth_open([p(12, -10), p(26, -3)])} {smooth_open([p(12, -6), p(24, 1)])}" stroke="#5E0C12" stroke-width="{F(0.8 * s)}" fill="none" opacity="0.6"/>']
    o.append(f'<path d="{crest}" fill="#C8262A"/>' + strokes(uid + "-cr", crest, bbox([p(-6, -44), p(6, -29)]), ["#F0584A", "#8E161C"], seed + 1, n=8, angle=-75, length=(3 * s, 8 * s), width=(0.4, 1.0), opacity=(0.3, 0.6)) + ink(crest, "#6E1016", 0.8 * s, seed + 1, 1, 0.6))
    o.append(paint(uid, bd, bbox(body), "#C8262A", seed, tints=["#F0584A", "#8E161C", "#F57A62", "#D83A3A"], angle=-40, n=36, ink_col="#5E0C12", ink_w=1.1 * s, length=(3 * s, 9 * s), width=(0.4, 1.1 * s), curve=0.4))
    o.append(shade(uid + "-bs", bd, "#6E1016", 0.6, 0.8, k=4 * s, op=0.4) + rim(uid + "-br", bd, "#FFB0A0", -0.6, -0.8, k=1.4 * s, op=0.6))
    o.append(f'<path d="{wing}" fill="#A81E24"/>' + strokes(uid + "-w", wing, bbox([p(-1, -26), p(18, -6)]), ["#8E161C", "#D83A3A"], seed + 2, n=14, angle=-35, length=(3 * s, 9 * s), width=(0.4, 1.0), opacity=(0.3, 0.6)))
    o.append(lines([f"M {F(p(2, -22)[0])} {F(p(2, -22)[1])} L {F(p(13, -9)[0])} {F(p(13, -9)[1])}", f"M {F(p(5, -24)[0])} {F(p(5, -24)[1])} L {F(p(16, -11)[0])} {F(p(16, -11)[1])}", f"M {F(p(-1, -19)[0])} {F(p(-1, -19)[1])} L {F(p(9, -7)[0])} {F(p(9, -7)[1])}"], "#5E0C12", 0.8 * s, 0.7))
    o.append(f'<path d="{smooth_closed([p(-13, -28), p(-6, -30), p(-3, -22), p(-8, -17), p(-14, -20)])}" fill="#1A0E0E"/>')
    o.append(f'<path d="{poly([p(-12, -27), p(-21, -23), p(-12, -20)])}" fill="#F2913A" stroke="#9A5A1A" stroke-width="0.6" stroke-linejoin="round"/><path d="M {F(p(-12, -23.5)[0])} {F(p(-12, -23.5)[1])} L {F(p(-19, -23)[0])} {F(p(-19, -23)[1])}" stroke="#9A5A1A" stroke-width="0.6"/>')
    ex, ey = p(-8, -26)
    o.append(f'<circle cx="{F(ex)}" cy="{F(ey)}" r="{F(1.5 * s)}" fill="#000"/><circle cx="{F(ex - 0.4 * s)}" cy="{F(ey - 0.5 * s)}" r="{F(0.55 * s)}" fill="#FFFFFF"/>')
    o.append(f'<g stroke="#4A2E24" stroke-width="{F(1.3 * s)}" stroke-linecap="round" fill="none"><path d="M {F(p(-3, -3)[0])} {F(p(-3, -3)[1])} l -1 4 m 1 -4 l 2 4"/><path d="M {F(p(4, -4)[0])} {F(p(4, -4)[1])} l -1 4 m 1 -4 l 2 4"/></g>')
    return "".join(o)


def lantern(u, cx, base, h, seed=51, hang=None):
    """Iron lantern with a candle: pointed cap, ring handle, four glass panes, warm glow. Optional hanging line to (x, y)."""
    w = h * 0.5
    o = [glow(u + "-gl", cx, base - h * 0.45, h * 1.2, h * 1.0, "#FFC55A", 0.6, mid=0.4)]
    if hang:
        o.append(f'<path d="M {F(hang[0])} {F(hang[1])} L {F(cx)} {F(base - h * 1.08)}" stroke="#3E2614" stroke-width="1.6"/>')
    irn, idk, ilt = "#3A3236", "#1A1618", "#6E646A"
    o.append(f'<rect x="{F(cx - w * 0.5)}" y="{F(base - h * 0.08)}" width="{F(w)}" height="{F(h * 0.08)}" rx="1" fill="{irn}" stroke="{idk}" stroke-width="0.8"/>')
    gl = poly([(cx - w * 0.42, base - h * 0.08), (cx + w * 0.42, base - h * 0.08), (cx + w * 0.42, base - h * 0.74), (cx - w * 0.42, base - h * 0.74)])
    o.append(f'<path d="{gl}" fill="#FFE9A8" opacity="0.7"/>')
    fl = f"M {F(cx - h * 0.045)} {F(base - h * 0.26)} Q {F(cx - h * 0.06)} {F(base - h * 0.4)} {F(cx)} {F(base - h * 0.52)} Q {F(cx + h * 0.06)} {F(base - h * 0.4)} {F(cx + h * 0.045)} {F(base - h * 0.26)} Z"
    o.append(f'<rect x="{F(cx - h * 0.06)}" y="{F(base - h * 0.26)}" width="{F(h * 0.12)}" height="{F(h * 0.16)}" fill="#F6ECD2" stroke="#B8A880" stroke-width="0.7"/>')
    o.append(f'<path d="{fl}" fill="#FFB236"/><path d="{fl}" fill="#FFF5C8" transform="scale(0.55 0.6)" transform-origin="{F(cx)} {F(base - h * 0.27)}"/>' + glow(u + "-fg", cx, base - h * 0.38, h * 0.2, h * 0.22, "#FFE38A", 0.85))
    o.append(f'<path d="{gl}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.35" transform="translate({F(-w * 0.06)} 0)"/>')
    # frame bars, cap and ring
    o.append(lines([f"M {F(cx - w * 0.44)} {F(base - h * 0.08)} L {F(cx - w * 0.44)} {F(base - h * 0.74)}", f"M {F(cx + w * 0.44)} {F(base - h * 0.08)} L {F(cx + w * 0.44)} {F(base - h * 0.74)}",
                    f"M {F(cx)} {F(base - h * 0.08)} L {F(cx)} {F(base - h * 0.74)}"], irn, max(1.6, h * 0.035), 1.0, cap="butt"))
    o.append(lines([f"M {F(cx - w * 0.44)} {F(base - h * 0.74)} L {F(cx - w * 0.44)} {F(base - h * 0.08)}"], ilt, max(0.6, h * 0.012), 0.6))
    cap = smooth_closed([(cx - w * 0.56, base - h * 0.74), (cx + w * 0.56, base - h * 0.74), (cx + w * 0.3, base - h * 0.86), (cx + w * 0.1, base - h * 0.98), (cx - w * 0.1, base - h * 0.98), (cx - w * 0.3, base - h * 0.86)])
    o.append(paint(u + "-cap", cap, (cx - w * 0.6, base - h, cx + w * 0.6, base - h * 0.7), irn, seed, tints=[idk, ilt], angle=-60, n=16, length=(3, 9), width=(0.5, 1.4), op=(0.3, 0.6), ink_col=idk, ink_w=1.0))
    o.append(rim(u + "-cr", cap, "#FFD98A", -0.6, -1, k=1.2, op=0.6))
    o.append(f'<rect x="{F(cx - w * 0.5)}" y="{F(base - h * 0.76)}" width="{F(w)}" height="{F(h * 0.04)}" fill="{irn}"/>')
    o.append(f'<path d="M {F(cx - w * 0.16)} {F(base - h * 0.98)} a {F(w * 0.16)} {F(w * 0.16)} 0 1 1 {F(w * 0.32)} 0" stroke="{irn}" stroke-width="{F(max(1.4, h * 0.03))}" fill="none"/>')
    o.append(shade(u + "-sb", gl, "#B89A58", 1, 0, k=w * 0.12, op=0.25))
    return "".join(o)


def top_hat(u, cx, base, w, seed=61):
    """Battered black top hat with a red band and a holly sprig; lavender rim so it reads on the dark page."""
    brim = blob(cx, base, w * 0.62, w * 0.1, seed, 0.03, 18)
    crown = smooth_closed([(cx - w * 0.38, base - w * 0.02), (cx - w * 0.4, base - w * 0.46), (cx - w * 0.34, base - w * 0.66), (cx + w * 0.3, base - w * 0.7), (cx + w * 0.42, base - w * 0.5), (cx + w * 0.38, base - w * 0.02)])
    col, tints = "#2A2630", ["#3E3850", "#121018", "#4E4866"]
    o = [paint(u + "-c", crown, (cx - w * 0.45, base - w * 0.72, cx + w * 0.45, base), col, seed, tints=tints, angle=-86, n=50, length=(6, 20), width=(0.6, 2), op=(0.3, 0.6), ink_col="#0E0C12", ink_w=1.3)]
    o.append(shade(u + "-cs", crown, "#0E0C12", 1, 0.2, k=w * 0.1, op=0.5) + rim(u + "-crm", crown, LAV, -1, -0.4, k=1.8, op=0.7))
    band = smooth_closed([(cx - w * 0.39, base - w * 0.06), (cx + w * 0.39, base - w * 0.06), (cx + w * 0.4, base - w * 0.2), (cx - w * 0.4, base - w * 0.2)])
    o.append(paint(u + "-bd", band, (cx - w * 0.42, base - w * 0.22, cx + w * 0.42, base - w * 0.04), "#B8262E", seed + 1, tints=["#E8605E", "#7A1218"], angle=0, n=12, length=(6, 18), width=(0.6, 1.8), op=(0.3, 0.5), ink_col="#5E0C12", ink_w=1.0))
    o.append(paint(u + "-b", brim, (cx - w * 0.64, base - w * 0.12, cx + w * 0.64, base + w * 0.12), col, seed + 2, tints=tints, angle=0, n=30, length=(6, 20), width=(0.6, 1.8), op=(0.3, 0.6), ink_col="#0E0C12", ink_w=1.3))
    o.append(rim(u + "-brm", brim, LAV, -0.4, -1, k=1.5, op=0.7))
    o.append(holly(u + "-h", cx + w * 0.28, base - w * 0.14, w * 0.16, -20))
    return "".join(o)


def snowman_p(u, cx, base, s=1.0):
    """Snowman in three-quarter view: three snowballs, stick arms (left arm holds a lantern, right arm out for the
    cardinal), coal eyes and smile, carrot nose, red knit scarf blowing, a top hat with holly."""
    def p(x, y):
        return (cx + x * s, base + y * s)
    o = [shadow(cx + 10 * s, base - 4, 62 * s, 9 * s, 0.14, "#5E6EA8")]
    o.append(stick_arm_p([p(-34, -96), p(-58, -104), p(-76, -118), p(-88, -134)], 3, w=5.4 * s))
    o.append(stick_arm_p([p(34, -98), p(60, -100), p(84, -104), p(100, -102)], 4, w=5.4 * s))
    o.append(snowball(u + "-b1", *p(0, -46), 50 * s, 44 * s, 11))
    o.append(snowball(u + "-b2", *p(-2, -110), 37 * s, 33 * s, 12))
    o.append(snowball(u + "-b3", *p(-4, -164), 28 * s, 26 * s, 13))
    for k, y in enumerate((-118, -100, -58)):
        bx, by = p(2 if y > -60 else 0, y)
        o.append(f'<path d="{blob(bx, by, 3.6 * s, 3.4 * s, 20 + k, 0.1, 9)}" fill="#2A2A33"/><circle cx="{F(bx - 1)}" cy="{F(by - 1.2)}" r="1" fill="#8A8A9A"/>')
    hx, hy = p(-4, -164)
    for sg, ex in ((-1, -13), (1, 6)):
        ex, ey = p(ex, -170)
        o.append(f'<path d="{blob(ex, ey, 3.6 * s, 4 * s, 30 + sg, 0.1, 9)}" fill="#2A2A33"/><circle cx="{F(ex - 1)}" cy="{F(ey - 1.4)}" r="1.1" fill="#FFFFFF"/>')
    o.append(f'<circle cx="{F(p(-22, -156)[0])}" cy="{F(p(-22, -156)[1])}" r="{F(5.5 * s)}" fill="#F08A8A" opacity="0.4"/><circle cx="{F(p(14, -157)[0])}" cy="{F(p(14, -157)[1])}" r="{F(5 * s)}" fill="#F08A8A" opacity="0.35"/>')
    o.append("".join(f'<circle cx="{F(p(x, -148 + 0.011 * x * x)[0])}" cy="{F(p(x, -148 + 0.011 * x * x)[1])}" r="{F(1.9 * s)}" fill="#2A2A33"/>' for x in (-14, -9, -4, 1, 6)))
    nose = smooth_closed([p(-6, -164), p(-34, -158), p(-6, -156)])
    o.append(paint(u + "-n", nose, (cx - 36 * s, base - 166 * s, cx - 4 * s, base - 154 * s), "#EE7A2A", 5, tints=["#F8A85A", "#B9531E"], angle=172, n=8, ink_col="#8A3A12", ink_w=0.9))
    o.append(f'<path d="M {F(p(-14, -162)[0])} {F(p(-14, -162)[1])} l -1 2 M {F(p(-22, -161)[0])} {F(p(-22, -161)[1])} l -1 2" stroke="#9A4A14" stroke-width="0.8"/>')
    # scarf: a wrap around the neck and a long end streaming to the right in the wind, with knit ribs and fringe
    wrapd = smooth_closed([p(-30, -140), p(-4, -132), p(26, -140), p(30, -128), p(0, -118), p(-32, -126)])
    o.append(paint(u + "-sc", wrapd, (cx - 34 * s, base - 144 * s, cx + 32 * s, base - 116 * s), "#C2343A", 6, tints=["#E8605E", "#8E1A20"], angle=0, n=24, ink_col="#6E1418", ink_w=1.2))
    endd = smooth_closed([p(14, -134), p(30, -138), p(56, -128), p(84, -126), p(96, -118), p(86, -112), p(58, -114), p(34, -120), p(18, -122)])
    o.append(paint(u + "-se", endd, (cx + 12 * s, base - 140 * s, cx + 98 * s, base - 110 * s), "#C2343A", 7, tints=["#E8605E", "#8E1A20"], angle=0, n=26, ink_col="#6E1418", ink_w=1.2))
    o.append(f'<clipPath id="{u}-scc"><path d="{wrapd} {endd}"/></clipPath><g clip-path="url(#{u}-scc)" stroke="#F6EEDD" stroke-width="3" opacity="0.9" fill="none">'
             + "".join(f'<path d="M {F(p(-40 + i * 12, -146)[0])} {F(p(-40 + i * 12, -146)[1])} q 2 14 4 28"/>' for i in range(7))
             + "".join(f'<path d="M {F(p(40 + i * 16, -142)[0])} {F(p(40 + i * 16, -142)[1])} q -3 14 -2 30"/>' for i in range(4)) + "</g>")
    o.append(shade(u + "-ses", endd, "#6E1418", 0, 1, k=4, op=0.35) + shade(u + "-scs", wrapd, "#6E1418", 0, 1, k=4, op=0.35))
    o.append('<g stroke="#C2343A" stroke-width="1.6" stroke-linecap="round">' + "".join(f'<path d="M {F(p(96, -120 + i * 2.2)[0])} {F(p(96, -120 + i * 2.2)[1])} l 7 {F(-2 + i * 1.2)}"/>' for i in range(5)) + "</g>")
    o.append(top_hat(u + "-hat", hx - 2 * s, hy - 20 * s, 66 * s))
    return "".join(o)


def winter_scene(u="wn"):
    back = [sky_rect(u + "-sky", [(0, "#2E3A6A", 1), (0.35, "#5E6EA8", 1), (0.6, "#B8A0C0", 1), (0.72, "#F2C8B0", 1), (0.8, "#E9D8E6", 1), (1, "#C9D4E6", 1)], (0, 0, 380, 330))]
    back.append(f'<defs>{rgrad(u + "-dusk", 120, 232, 170, [(0, "#FFD9B0", 0.7), (0.5, "#F2B090", 0.25), (1, "#F2B090", 0)])}</defs><circle cx="120" cy="232" r="170" fill="url(#{u}-dusk)"/>')
    back.append(speck(6, (0, 0, 380, 150), ["#FFFFFF", "#E9E0FF"], 30, r=(0.5, 1.2), op=(0.3, 0.8)))
    far, _ = ridge([(0, 234), (90, 222), (170, 230), (260, 218), (380, 228)], 3, 330, amp=5)
    back.append(f'<path d="{far}" fill="#C9D4EA"/><path d="{far}" fill="#A8B8D8" opacity="0.6" transform="translate(0 8)"/>')
    rnd = random.Random(8)
    for x in range(-4, 390, 7):
        back.append(conifer_p(f"{u}-ft{x + 4}", x, 236 + 3 * math.sin(x * 0.05), rnd.uniform(14, 26), x + 9, cols=("#5E6E98", "#4A5A84", "#7A8AB0", "#A8B8D8"), width=0.36))
    snow = poly([(0, 240), (380, 236), (380, 330), (0, 330)])
    back.append(f'<path d="{snow}" fill="#EEF3FA"/>')
    back.append(f'<defs>{lgrad(u + "-sg", 0, 240, 0, 330, [(0, "#FFFFFF", 0.9), (0.4, "#DCE6F4", 0.3), (1, "#B8C8E0", 0.8)])}</defs><rect x="0" y="240" width="380" height="90" fill="url(#{u}-sg)"/>')
    back.append(hstrokes(u + "-ss", snow, (0, 240, 380, 330), ["#FFFFFF", "#C9D8EA", "#E9F0F8", "#D4C8E0"], 21, n=160, angle=-3, length=(12, 44), width=(0.8, 2.6), op=(0.2, 0.45)))
    for k, (x, y, w) in enumerate(((60, 300, 90), (300, 284, 70), (200, 318, 110))):
        d = blob(x, y, w / 2, w / 9, 40 + k, 0.05, 14)
        back.append(f'<path d="{d}" fill="#FFFFFF"/>' + shade(f"{u}-md{k}", d, "#B8C8E0", 0.4, 1, k=w * 0.05, op=0.6))
    # snowy pines right and left (the right one tall, close)
    back.append(conifer_p(u + "-p1", 338, 300, 236, 70, cols=("#2C5848", "#183A2E", "#467A62", "#8EB29C"), snow=("#F8FBFF", "#AFC4DC"), width=0.46, light=(-1, -0.3)))
    back.append(conifer_p(u + "-p2", 24, 294, 160, 71, cols=("#2C5848", "#183A2E", "#467A62", "#8EB29C"), snow=("#F8FBFF", "#AFC4DC"), width=0.44, light=(1, -0.3)))
    back.append(conifer_p(u + "-p3", 72, 286, 92, 72, cols=("#355E52", "#1E4236", "#4E806A", "#9AC0A8"), snow=("#F8FBFF", "#AFC4DC"), width=0.42, light=(1, -0.3)))
    # footprints wandering in from the left
    for k in range(7):
        fx, fy = 30 + k * 22, 318 - k * 6
        back.append(f'<ellipse cx="{F(fx + (k % 2) * 6)}" cy="{F(fy)}" rx="4" ry="2.6" fill="#B8C8E0" opacity="0.8"/>')
    o = [vignette(u + "-v", "".join(back), [(200, 190, 186, 138, 0.45), (120, 230, 120, 100, 0.5), (280, 220, 110, 100, 0.45), (230, 100, 120, 90, 0.3)])]
    o.append(snowman_p(u + "-sm", 190, 306, 1.0))
    o.append(lantern(u + "-la", 104, 206, 44, hang=(102, 172)))
    o.append(lantern(u + "-lb", 290, 300, 50))
    o.append(cardinal_p(u + "-cd", 262, 204, 1.2))
    # soft snow falling in front
    o.append(speck(9, (0, 20, 380, 310), ["#FFFFFF"], 60, r=(1.0, 2.6), op=(0.5, 0.95)))
    for k, (x, y, r) in enumerate(((60, 60, 5), (300, 50, 4.5), (150, 30, 3.6), (340, 150, 3.4), (30, 150, 4), (230, 70, 3))):
        o.append(snowflake_p(f"{u}-fl{k}", x, y, r, 3 if k % 2 else 2, k * 11, edge="#C9D8EA"))
    return "".join(o)


def winter_garland(u="wg"):
    """Seamless 320 x 74: a snow-capped evergreen rope with icicles, pinecones, red berries and snowflakes."""
    o = []
    rnd = random.Random(12)
    # icicles under the rope
    for x in range(8, TW, 14):
        if abs(x - 90) < 10 or abs(x - 230) < 10:
            continue
        L = rnd.choice([8, 13, 19, 10, 15, 23, 28])
        y = swag_y(x) + 4
        d = f"M {F(x - 3.2)} {F(y)} Q {F(x - 2)} {F(y + L * 0.6)} {F(x + 0.3)} {F(y + L)} Q {F(x + 1.6)} {F(y + L * 0.5)} {F(x + 3.2)} {F(y)} Z"
        o.append(f'<path d="{d}" fill="#E6F1FB" stroke="#7FA6CC" stroke-width="0.9" stroke-linejoin="round"/><path d="M {F(x - 1.2)} {F(y + 2)} Q {F(x - 0.8)} {F(y + L * 0.5)} {F(x)} {F(y + L * 0.8)}" stroke="#FFFFFF" stroke-width="1.1" fill="none" stroke-linecap="round"/>')
    layers = [("#1E4A38", 200, 1.8, 0.9), ("#2F6B4F", 220, 1.4, 0.95), ("#4C8C62", 160, 1.1, 0.9), ("#8CC08A", 60, 1.0, 0.8)]
    for col, n, w, op in layers:
        segs = []
        for _ in range(n):
            x = rnd.uniform(0, TW)
            y = swag_y(x) + rnd.uniform(-4, 4)
            a = rnd.uniform(0, 2 * math.pi)
            L = rnd.uniform(5, 10)
            dx, dy = L * math.cos(a), L * math.sin(a) * 0.8
            for sh in (0, TW, -TW):
                xx = x + sh
                if -12 < xx < TW + 12:
                    segs.append(f"M {F(xx)} {F(y)} q {F(dx * 0.5 + rnd.uniform(-2, 2))} {F(dy * 0.5 + 1)} {F(dx)} {F(dy)}")
        o.append(f'<path d="{" ".join(segs)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="{op}" fill="none"/>')
    # snow lying on top of the rope
    cap_top = [(x, swag_y(x) - 4 - 2.2 * abs(math.sin(x * 0.09)) - 1.2 * abs(math.sin(x * 0.23))) for x in range(-6, TW + 7, 6)]
    cap_bot = [(x, swag_y(x) + 0.5 + 1.2 * abs(math.sin(x * 0.17))) for x in range(TW + 6, -7, -6)]
    capd = smooth_closed(cap_top + cap_bot)
    o.append(f'<path d="{capd}" fill="#F8FBFF"/>' + shade(u + "-cs", capd, "#AFC4DC", 0, 1, k=2.2, op=0.8) + ink(capd, "#8FB0D0", 0.9, 3, 1, 0.6))
    o.append(pinecone(u + "-pc1", 150, swag_y(150) + 6, 10, swag_slope(150) + 80) + pinecone(u + "-pc2", 290, swag_y(290) + 6, 10, swag_slope(290) + 100))
    for x in (50, 200, 262):
        y = swag_y(x) + 3
        o.append("".join(f'<circle cx="{F(x + dx)}" cy="{F(y + dy)}" r="2.8" fill="#C2343A" stroke="#6E1418" stroke-width="0.6"/><circle cx="{F(x + dx - 0.9)}" cy="{F(y + dy - 0.9)}" r="0.9" fill="#FFFFFF" opacity="0.8"/>' for dx, dy in ((-3, 1), (2.5, 3), (0, 6.5))))
    for k, (x, L, r, kind) in enumerate(((90, 12, 10, 1), (230, 16, 9.5, 2))):
        y = swag_y(x)
        o.append(f'<path d="M {x} {F(y)} L {x} {F(y + L)}" stroke="#7FA6CC" stroke-width="0.9"/>' + snowflake_p(f"{u}-sf{k}", x, y + L + r, r, kind, 0, edge="#88B0D8"))
    return "".join(o)
