"""Painted website decor for NEW YEAR, VALENTINE, ST PATRICK'S, SPRING, SUMMER and JULY 4 (the other seasons live in
decor_seasons.py / decor.py). decor_seasons.py's season functions call into here and keep the file names.

Each scene (380 x 330, transparent ground) is a small gouache painting: a soft-edged vignette of sky and distance
behind a lit foreground subject, with washes, form-following brush strokes, pooled edges, dry-brush highlights,
cast shadows and a warm ink line used sparingly. Everything is plain SVG (gradients, masks, clipPaths, patterns)
and has to read on the cream day page (#FFF6E5) and on the dark brown night page (#1C1610).
"""
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash  # noqa: E402

INK = "#3A2418"
TW = 320


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


def lg(uid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    return f'<linearGradient id="{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(uid, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    return f'<radialGradient id="{uid}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


def glow(uid, cx, cy, rx, ry, col, op, mid=0.45):
    return (f'<defs>{rg(uid, [(0, col, op), (0.5, col, round(op * mid, 3)), (1, col, 0)])}</defs>'
            f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{uid})"/>')


def shadow(cx, cy, rx, ry, op=0.14, col=INK):
    return f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="{col}" opacity="{op}"/>'


def soft_shadow(uid, cx, cy, rx, ry, op=0.3, col=INK):
    """Cast shadow with a soft edge (radial fade)."""
    return (f'<defs>{rg(uid, [(0, col, op), (0.6, col, round(op * 0.6, 3)), (1, col, 0)])}</defs>'
            f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{uid})"/>')


def paint(uid, d, box, base, seed, tints=None, angle=-90, n=None, ink_col=None, ink_w=1.5, length=None, width=None,
          op=(0.25, 0.55), curve=0.25, edge_op=0.6, layers=2, grad=None):
    """Wash (or gradient fill) + clipped brush strokes + inked edge: the basic gouache object."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    m = min(w, h)
    tints = tints or [lt(base, 0.22), dk(base, 0.18), lt(base, 0.4)]
    n = int(max(8, min(110, w * h / 55))) if n is None else n
    length = length or (max(3, m * 0.15), max(6, m * 0.5))
    width = width or (0.5, max(1.0, m * 0.035))
    if grad:
        o = f'<defs>{grad[0]}</defs><path d="{d}" fill="url(#{grad[1]})"/>'
    else:
        o = wash(d, base, seed, layers, 0.8, 0.5)
    if n:
        o += strokes(uid, d, box, tints, seed + 1, n=n, angle=angle, length=length, width=width, opacity=op, curve=curve)
    if ink_w:
        o += ink(d, ink_col or inkc(base), ink_w, seed + 2, 2, edge_op)
    return o


def gpaint(uid, d, box, light, base, dark, seed, direction=(0, 1), **kw):
    """paint() whose base is a linear gradient from the light colour to the dark one along direction."""
    dx, dy = direction
    x1, y1 = 0.5 - dx * 0.5, 0.5 - dy * 0.5
    x2, y2 = 0.5 + dx * 0.5, 0.5 + dy * 0.5
    g = lg(uid + "-lg", [(0, light), (0.55, base), (1, dark)], x1, y1, x2, y2)
    kw.setdefault("tints", [lt(base, 0.25), dk(base, 0.2), light])
    return paint(uid, d, box, base, seed, grad=(g, uid + "-lg"), **kw)


def rim(uid, d, col, sx, sy, k=2.0, op=0.75):
    """Light band hugging the inside of a shape on the (sx, sy) side."""
    return (f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{2 * k:.1f}" opacity="{op}" '
            f'transform="translate({F(-sx * k)} {F(-sy * k)})"/></g>')


def shade(uid, d, col, sx, sy, k=6.0, op=0.35):
    """Soft shade side: the outline stroked, shifted away, clipped to the shape (a crescent on the (sx, sy) side)."""
    return rim(uid, d, col, sx, sy, k, op)


def clipped(uid, d, inner):
    return f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">{inner}</g>'


def grain(uid, box, col="#3A2418", seed=9, op=0.5, density=70):
    """Speck pattern over an area (adds paper tooth to flat colour). Used inside a clip."""
    rnd = random.Random(seed)
    sp = "".join(f'<circle cx="{rnd.uniform(0, 60):.1f}" cy="{rnd.uniform(0, 60):.1f}" r="{rnd.uniform(0.3, 0.8):.2f}" fill="{rnd.choice([col, "#FFFFFF"])}" opacity="{rnd.uniform(0.08, 0.22):.2f}"/>'
                 for _ in range(density))
    x0, y0, x1, y1 = box
    return (f'<defs><pattern id="{uid}" width="60" height="60" patternUnits="userSpaceOnUse">{sp}</pattern></defs>'
            f'<rect x="{F(x0)}" y="{F(y0)}" width="{F(x1 - x0)}" height="{F(y1 - y0)}" fill="url(#{uid})" opacity="{op}"/>')


def vignette(uid, inner, cx, cy, rx, ry, seed=1, edge=0.55, wobble=0.05, ground=None, gfade=0.3):
    """inner drawn through a soft-edged mask: opaque near (cx, cy), fading to nothing at an irregular painted edge.
    With ground=y, everything below y also stays solid down to the bottom edge (fading only at the sides)."""
    d = blob(cx, cy, rx, ry, seed, wobble, 22)
    extra = ""
    if ground is not None:
        ramp = 8
        extra = "".join(f'<rect x="0" y="{F(ground + i * 6)}" width="380" height="6.5" fill="url(#{uid}-gg)" opacity="{(i + 1) / (ramp + 1):.2f}"/>' for i in range(ramp))
        extra += f'<rect x="0" y="{F(ground + ramp * 6)}" width="380" height="{F(330 - ground - ramp * 6)}" fill="url(#{uid}-gg)"/>'
    gdef = lg(uid + "-gg", [(0, "#000"), (gfade, "#FFF"), (1 - gfade, "#FFF"), (1, "#000")], 0, 0, 1, 0) if ground is not None else ""
    return (f'<defs>{rg(uid + "-g", [(0, "#FFF"), (edge, "#FFF"), (1, "#000")])}{gdef}'
            f'<mask id="{uid}"><path d="{d}" fill="url(#{uid}-g)"/>{extra}</mask></defs>'
            f'<g mask="url(#{uid})">{inner}</g>')


def hmask(uid, inner, x0, x1, y0, y1, fade=0.3):
    """inner through a mask that fades out at the left and right ends (and softly at the top)."""
    return (f'<defs>{lg(uid + "-g", [(0, "#000"), (fade, "#FFF"), (1 - fade, "#FFF"), (1, "#000")], 0, 0, 1, 0)}'
            f'<mask id="{uid}"><rect x="{F(x0)}" y="{F(y0)}" width="{F(x1 - x0)}" height="{F(y1 - y0)}" fill="url(#{uid}-g)"/></mask></defs>'
            f'<g mask="url(#{uid})">{inner}</g>')


def vmask(uid, inner, x0, x1, y0, y1, top=0.0, bottom=0.3):
    """inner through a mask that fades out toward the bottom (and optionally the top)."""
    stops = [(0, "#000"), (top, "#FFF"), (1 - bottom, "#FFF"), (1, "#000")] if top > 0 else [(0, "#FFF"), (1 - bottom, "#FFF"), (1, "#000")]
    return (f'<defs>{lg(uid + "-g", stops, 0, 0, 0, 1)}'
            f'<mask id="{uid}"><rect x="{F(x0)}" y="{F(y0)}" width="{F(x1 - x0)}" height="{F(y1 - y0)}" fill="url(#{uid}-g)"/></mask></defs>'
            f'<g mask="url(#{uid})">{inner}</g>')


def heart_d(cx, cy, s, rot_=0):
    pts = [(0, 0.85), (-0.2, 0.6), (-1.0, 0.15), (-0.95, -0.35), (-0.9, -0.85), (-0.25, -0.95), (0, -0.45),
           (0.25, -0.95), (0.9, -0.85), (0.95, -0.35), (1.0, 0.15), (0.2, 0.6), (0, 0.85)]
    p = [rot(cx + x * s, cy + y * s, cx, cy, rot_) for x, y in pts]
    d = f"M {F(p[0][0])} {F(p[0][1])}"
    for i in range(1, 13, 3):
        d += f" C {F(p[i][0])} {F(p[i][1])} {F(p[i + 1][0])} {F(p[i + 1][1])} {F(p[i + 2][0])} {F(p[i + 2][1])}"
    return d + " Z"


def star_pts(cx, cy, r, inner=0.48, rot_=-90, n=5):
    out = []
    for i in range(2 * n):
        a = math.radians(rot_ + i * 180 / n)
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def swag_y(x, top=10, sag=34):
    t = x / TW
    return (1 - t) ** 3 * top + 3 * (1 - t) ** 2 * t * sag + 3 * (1 - t) * t * t * sag + t ** 3 * top


def swag_slope(x, **kw):
    return math.degrees(math.atan2(swag_y(x + 0.5, **kw) - swag_y(x - 0.5, **kw), 1))


def swag_d(top=10, sag=34):
    return f"M 0 {top} C 80 {sag} 240 {sag} 320 {top}"


def wrap(fn, x, margin):
    """Draw an item at x and, if it crosses a tile edge, again one tile over so the seam matches."""
    out = fn(x)
    if x < margin:
        out += fn(x + TW)
    if x > TW - margin:
        out += fn(x - TW)
    return out


def rope(uid, col, hi, dark, w=3.0, top=10, sag=34, twist=5):
    """Twisted cord along the swag: dark under-line, body, a light twist running along it."""
    d = swag_d(top, sag)
    return (f'<path d="{d}" stroke="{dark}" stroke-width="{F(w + 1.2)}" fill="none" opacity="0.5"/>'
            f'<path d="{d}" stroke="{col}" stroke-width="{F(w)}" fill="none"/>'
            f'<path d="{d}" stroke="{hi}" stroke-width="{F(w * 0.45)}" fill="none" stroke-dasharray="{twist} {twist}" opacity="0.85" transform="translate(0 -0.4)"/>'
            f'<path d="{d}" stroke="{dark}" stroke-width="{F(w * 0.3)}" fill="none" stroke-dasharray="{twist} {twist}" stroke-dashoffset="{twist}" opacity="0.5" transform="translate(0 0.6)"/>')


def tapered(pts, w0, w1, col, op=1.0, extra=""):
    """A brush stroke of varying width along an open polyline (tapers from w0 to w1)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        xp, yp = pts[max(i - 1, 0)]
        xn, yn = pts[min(i + 1, n - 1)]
        tx, ty = xn - xp, yn - yp
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    d = smooth_open(left) + " " + smooth_open(right[::-1]).replace("M", "L", 1) + " Z"
    return f'<path d="{d}" fill="{col}" opacity="{op}"{extra}/>'


def dry_brush(seed, box, cols, n, angle=0, length=(10, 30), width=(0.6, 2.0), op=(0.2, 0.6), curve=0.3):
    """Loose brush strokes (not clipped) for texture over a region."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    o = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(*length)
        w = rnd.uniform(*width)
        a = math.radians(angle + rnd.uniform(-10, 10))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        bend = L * curve * rnd.uniform(-1, 1)
        mx, my = x + dx / 2 + nx * bend, y + dy / 2 + ny * bend
        o.append(f'<path d="M {F(x)} {F(y)} Q {F(mx + nx * w)} {F(my + ny * w)} {F(x + dx)} {F(y + dy)} Q {F(mx - nx * w)} {F(my - ny * w)} {F(x)} {F(y)} Z" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(o)


def leafy(uid, x, y, L, w, ang, col, seed, vein=None, light=None, ink_w=0.8):
    """A painted leaf: pointed oval along ang, mid vein, lit half, inked edge."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (x + ux * L, y + uy * L)
    pts = [(x, y), (x + ux * L * 0.3 + nx * w, y + uy * L * 0.3 + ny * w), (x + ux * L * 0.72 + nx * w * 0.72, y + uy * L * 0.72 + ny * w * 0.72), tip,
           (x + ux * L * 0.72 - nx * w * 0.72, y + uy * L * 0.72 - ny * w * 0.72), (x + ux * L * 0.3 - nx * w, y + uy * L * 0.3 - ny * w)]
    pts = jitter(pts, seed, w * 0.08)
    d = smooth_closed(pts)
    half = smooth_closed([pts[0], pts[1], pts[2], tip, (x + ux * L * 0.5, y + uy * L * 0.5)])
    return (f'<path d="{d}" fill="{col}"/>'
            f'<path d="{half}" fill="{light or lt(col, 0.3)}" opacity="0.5"/>'
            f'<path d="M {F(x)} {F(y)} Q {F(x + ux * L * 0.5 + nx * w * 0.1)} {F(y + uy * L * 0.5 + ny * w * 0.1)} {F(tip[0])} {F(tip[1])}" stroke="{vein or lt(col, 0.45)}" stroke-width="{F(max(0.6, w * 0.1))}" fill="none" opacity="0.8"/>'
            + (ink(d, dk(col, 0.45), ink_w, seed, 1, 0.55) if ink_w else ""))


def sparkle(cx, cy, r, col="#FFF3C4", edge=None, soft=0.15):
    d = (f"M {F(cx)} {F(cy - r)} Q {F(cx + r * soft)} {F(cy - r * soft)} {F(cx + r)} {F(cy)} Q {F(cx + r * soft)} {F(cy + r * soft)} {F(cx)} {F(cy + r)} "
         f"Q {F(cx - r * soft)} {F(cy + r * soft)} {F(cx - r)} {F(cy)} Q {F(cx - r * soft)} {F(cy - r * soft)} {F(cx)} {F(cy - r)} Z")
    e = f' stroke="{edge}" stroke-width="{F(max(0.5, r * 0.1))}" stroke-linejoin="round"' if edge else ""
    return f'<path d="{d}" fill="{col}"{e}/>'


def bird(uid, x, y, s, body, belly, wing, beak="#E2A23A", flip=False, seed=5, eye="#1E1410"):
    """A small perched songbird facing right (flip for left): round chest, folded wing, tail, tiny legs. (x, y) = feet."""
    def p(px, py):
        return (x + (-px if flip else px) * s, y + py * s)
    bd = smooth_closed([p(-16, -4), p(-18, -12), p(-10, -22), p(2, -26), p(12, -22), p(16, -14), p(14, -6), p(6, -1), p(-6, -1)])
    o = [f'<path d="{bd}" fill="{body}"/>']
    belly_d = smooth_closed([p(-8, -3), p(-2, -12), p(8, -14), p(14, -8), p(12, -3), p(4, -1), p(-4, -1)])
    o.append(f'<path d="{belly_d}" fill="{belly}" opacity="0.9"/>')
    wd = smooth_closed([p(-10, -18), p(-2, -22), p(6, -18), p(2, -10), p(-6, -7), p(-14, -9)])
    o.append(f'<path d="{wd}" fill="{wing}"/>')
    o.append(f'<path d="M {F(p(-8, -14)[0])} {F(p(-8, -14)[1])} Q {F(p(-2, -12)[0])} {F(p(-2, -12)[1])} {F(p(2, -10)[0])} {F(p(2, -10)[1])}" stroke="{dk(wing, 0.3)}" stroke-width="{F(0.8 * s)}" fill="none" opacity="0.7"/>')
    tail = smooth_closed([p(-14, -10), p(-26, -16), p(-28, -11), p(-16, -5)])
    o.append(f'<path d="{tail}" fill="{dk(body, 0.15)}"/>')
    hd = blob(*p(10, -22), 7 * s, 6.3 * s, seed, 0.04, 12)
    o.append(f'<path d="{hd}" fill="{body}"/>')
    o.append(f'<path d="M {F(p(16, -22)[0])} {F(p(16, -22)[1])} l {F((-6 if flip else 6) * s)} {F(1.6 * s)} l {F((6 if flip else -6) * s)} {F(1.8 * s)} Z" fill="{beak}" stroke="{dk(beak, 0.4)}" stroke-width="0.5"/>')
    o.append(f'<circle cx="{F(p(12, -23)[0])}" cy="{F(p(12, -23)[1])}" r="{F(1.5 * s)}" fill="{eye}"/><circle cx="{F(p(12.5, -23.6)[0])}" cy="{F(p(12.5, -23.6)[1])}" r="{F(0.5 * s)}" fill="#FFF"/>')
    o.append(f'<path d="M {F(p(0, -1)[0])} {F(p(0, -1)[1])} l {F(0.5 * s)} {F(4 * s)} m {F(5 * s)} {F(-4 * s)} l {F(-0.5 * s)} {F(4 * s)}" stroke="{dk(beak, 0.3)}" stroke-width="{F(1.1 * s)}" stroke-linecap="round" fill="none"/>')
    o.append(ink(bd, dk(body, 0.5), 0.8 * s, seed, 1, 0.5))
    return "".join(o)


def cloud_puffs(uid, cx, cy, w, seed, col="#FFFFFF", shade_col="#C9D6E6", n=5, ink_col=None):
    """Cumulus from several puffs, lit from above, with a shaded underside."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(n):
        t = (i + 0.5) / n
        px = cx - w / 2 + w * t + rnd.uniform(-w * 0.04, w * 0.04)
        r = w * (0.14 + 0.1 * math.sin(math.pi * t)) * rnd.uniform(0.85, 1.1)
        puffs.append((px, cy - r * 0.35, r))
    puffs.append((cx, cy + w * 0.04, w * 0.14))
    o = []
    for k, (px, py, r) in enumerate(puffs):
        o.append(f'<path d="{blob(px, py, r, r * 0.9, seed + k, 0.06, 14)}" fill="{col}"/>')
    base = f"M {F(cx - w * 0.52)} {F(cy + w * 0.08)} L {F(cx + w * 0.52)} {F(cy + w * 0.08)} L {F(cx + w * 0.52)} {F(cy + w * 0.3)} L {F(cx - w * 0.52)} {F(cy + w * 0.3)} Z"
    o.append(f'<path d="{blob(cx, cy + w * 0.06, w * 0.5, w * 0.1, seed + 9, 0.05, 16)}" fill="{shade_col}" opacity="0.7"/>')
    for k, (px, py, r) in enumerate(puffs[:-1]):
        o.append(f'<path d="{blob(px, py + r * 0.5, r * 0.8, r * 0.35, seed + 20 + k, 0.1, 10)}" fill="{shade_col}" opacity="0.45"/>')
    del base
    return "".join(o)


# ================================================================ NEW YEAR
GOLD = ("#E2B04A", "#F8DC8A", "#B07E22", "#7A5212")
SILVER = ("#C4CAD4", "#F2F4F8", "#8A93A3", "#5A6272")
NAVY = "#2E3F6E"
CONFETTI = ["#E2B04A", "#C4CAD4", "#E8869A", "#3FA3B5", "#F6C23E", "#B48ED6", "#F8DC8A"]


def firework_burst(uid, cx, cy, r, col, seed, n=22, droop=0.18, glow_op=0.55):
    """Peony burst: tapered rays that curve down under gravity, sparks at the tips, a bright core and a soft glow."""
    rnd = random.Random(seed)
    o = [glow(uid + "-g", cx, cy, r * 1.3, r * 1.2, col, glow_op, 0.35)]
    light, darkc = lt(col, 0.55), dk(col, 0.25)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.1, 0.1)
        L = r * rnd.uniform(0.7, 1.0)
        pts = []
        for k in range(6):
            t = k / 5
            rr = L * t
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr + droop * rr * t * (1 + 0.3 * math.cos(a))
            pts.append((x, y))
        o.append(tapered(pts, 0.6, r * 0.045 + 1.2, darkc, 0.55))
        o.append(tapered(pts[:5], 0.5, r * 0.03 + 0.8, col, 0.95))
        o.append(tapered([pts[0], pts[1], pts[2]], 0.4, r * 0.02 + 0.6, light, 0.9))
        tx, ty = pts[-1]
        o.append(f'<circle cx="{F(tx)}" cy="{F(ty)}" r="{F(rnd.uniform(0.9, 1.8))}" fill="{light}"/>')
        if rnd.random() < 0.6:
            o.append(f'<circle cx="{F(tx + rnd.uniform(-5, 5))}" cy="{F(ty + rnd.uniform(2, 9))}" r="{F(rnd.uniform(0.6, 1.2))}" fill="{col}" opacity="0.8"/>')
    o.append(glow(uid + "-c", cx, cy, r * 0.3, r * 0.3, "#FFF8E0", 0.95, 0.5))
    o.append(sparkle(cx, cy, r * 0.14, "#FFFDF2"))
    return "".join(o)


def skyline(uid, x0, x1, base, seed, col="#2A2C52", win="#F6D27A", haze="#5A4C7E"):
    """Distant city at night: a row of irregular towers with scattered lit windows, sunk in haze."""
    rnd = random.Random(seed)
    o = []
    x = x0
    towers = []
    while x < x1:
        w = rnd.uniform(10, 26)
        h = rnd.uniform(14, 58) * (1 - 0.5 * abs((x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2)
        towers.append((x, w, h))
        x += w + rnd.uniform(-2, 3)
    for k, (tx, w, h) in enumerate(towers):
        top = base - h
        d = poly([(tx, base + 4), (tx, top), (tx + w, top + rnd.choice([0, 0, 3, -2])), (tx + w, base + 4)])
        o.append(f'<path d="{d}" fill="{mix(col, haze, rnd.uniform(0.0, 0.35))}"/>')
        if rnd.random() < 0.45 and h > 30:
            o.append(f'<path d="M {F(tx + w * 0.5)} {F(top)} l 0 {F(-rnd.uniform(4, 10))}" stroke="{col}" stroke-width="1.2"/>')
        for _ in range(int(w * h / 90)):
            wx, wy = tx + rnd.uniform(1.5, w - 3), rnd.uniform(top + 3, base - 4)
            o.append(f'<rect x="{F(wx)}" y="{F(wy)}" width="1.6" height="2" fill="{win}" opacity="{rnd.uniform(0.35, 0.95):.2f}"/>')
    return "".join(o)


def champagne_flute(uid, bx, by, h, tilt, seed, fill_t=0.72):
    """Flute standing at (bx, by), h tall, rotated tilt degrees about its foot. Glass painted as light, not line."""
    stem_h = h * 0.36
    top = by - h
    bw, bb = h * 0.125, h * 0.03
    bowl_pts = [(bx - bb, by - stem_h), (bx - bw * 0.9, by - stem_h - (h - stem_h) * 0.42), (bx - bw, top + 3), (bx - bw * 0.98, top),
                (bx + bw * 0.98, top), (bx + bw, top + 3), (bx + bw * 0.9, by - stem_h - (h - stem_h) * 0.42), (bx + bb, by - stem_h)]
    bd = smooth_closed(bowl_pts)
    liq_y = top + (h - stem_h) * (1 - fill_t)
    o = [f'<g transform="rotate({tilt} {F(bx)} {F(by)})">']
    # foot and stem
    o.append(f'<ellipse cx="{F(bx)}" cy="{F(by)}" rx="{F(h * 0.12)}" ry="{F(h * 0.028)}" fill="#D8E2EE" fill-opacity="0.55" stroke="#8E9CB2" stroke-width="1.1"/>')
    o.append(f'<path d="M {F(bx - h * 0.08)} {F(by - 1)} Q {F(bx)} {F(by - h * 0.05)} {F(bx + h * 0.08)} {F(by - 1)}" stroke="#FFFFFF" stroke-width="1" fill="none" opacity="0.7"/>')
    o.append(f'<path d="M {F(bx)} {F(by - 2)} L {F(bx)} {F(by - stem_h)}" stroke="#9AA8BE" stroke-width="{F(h * 0.03)}" stroke-linecap="round"/>'
             f'<path d="M {F(bx - h * 0.006)} {F(by - 4)} L {F(bx - h * 0.006)} {F(by - stem_h + 2)}" stroke="#F6F9FC" stroke-width="{F(h * 0.012)}" stroke-linecap="round" opacity="0.9"/>')
    # glass body: pale fill, then champagne clipped inside
    o.append(f'<defs>{lg(uid + "-gl", [(0, "#FFFFFF", 0.42), (0.5, "#DCE6F2", 0.18), (1, "#FFFFFF", 0.35)], 0, 0, 1, 0)}</defs><path d="{bd}" fill="url(#{uid}-gl)"/>')
    rnd = random.Random(seed)
    liq = (f'<defs>{lg(uid + "-ch", [(0, "#F8D77A"), (0.6, "#E8B548"), (1, "#C98E2C")], 0.2, 0, 0.8, 1)}</defs>'
           f'<rect x="{F(bx - bw - 2)}" y="{F(liq_y)}" width="{F(2 * bw + 4)}" height="{F(h)}" fill="url(#{uid}-ch)"/>'
           f'<rect x="{F(bx + bw * 0.25)}" y="{F(liq_y)}" width="{F(bw)}" height="{F(h)}" fill="#B87A22" opacity="0.5"/>'
           f'<rect x="{F(bx - bw * 0.75)}" y="{F(liq_y)}" width="{F(bw * 0.3)}" height="{F(h)}" fill="#FFF0B8" opacity="0.5"/>'
           f'<ellipse cx="{F(bx)}" cy="{F(liq_y)}" rx="{F(bw * 1.05)}" ry="{F(h * 0.018)}" fill="#FFF3C8"/>'
           f'<ellipse cx="{F(bx)}" cy="{F(liq_y - 1)}" rx="{F(bw * 0.95)}" ry="{F(h * 0.012)}" fill="#FFFFFF" opacity="0.8"/>')
    liq += "".join(f'<circle cx="{F(bx + rnd.uniform(-0.75, 0.75) * bw * (0.4 + 0.6 * t))}" cy="{F(by - stem_h - 5 - t * (by - stem_h - liq_y - 7))}" r="{F(rnd.uniform(0.6, 1.4))}" fill="#FFF8DC" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>'
                   for t in [rnd.random() for _ in range(18)])
    o.append(clipped(uid + "-c", bd, liq))
    # reflections and the rim
    o.append(f'<path d="M {F(bx - bw * 0.62)} {F(top + 8)} Q {F(bx - bw * 0.8)} {F(by - stem_h - (h - stem_h) * 0.42)} {F(bx - bb * 1.4)} {F(by - stem_h - 5)}" stroke="#FFFFFF" stroke-width="{F(h * 0.02)}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    o.append(f'<path d="M {F(bx + bw * 0.72)} {F(top + 14)} Q {F(bx + bw * 0.78)} {F(top + (h - stem_h) * 0.5)} {F(bx + bw * 0.5)} {F(by - stem_h - 10)}" stroke="#FFFFFF" stroke-width="{F(h * 0.009)}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    o.append(ink(bd, "#8E9CB2", h * 0.012, seed, 2, 0.8))
    o.append(f'<ellipse cx="{F(bx)}" cy="{F(top)}" rx="{F(bw)}" ry="{F(h * 0.016)}" fill="none" stroke="#F4F8FC" stroke-width="{F(h * 0.012)}"/>')
    o.append("</g>")
    return "".join(o)


def brass_clock(u, cx, cy, r, seed=141):
    """Round brass mantel/alarm clock reading two minutes to midnight."""
    gb, gl, gd, gi = GOLD
    o = [soft_shadow(u + "-sh", cx + 4, cy + r + 12, r * 1.1, 7, 0.35)]
    for sg in (-1, 1):
        lx = cx + sg * r * 0.6
        o.append(f'<path d="M {F(lx)} {F(cy + r * 0.72)} L {F(lx + sg * r * 0.2)} {F(cy + r + 9)}" stroke="{gi}" stroke-width="{F(r * 0.13)}" stroke-linecap="round"/>'
                 f'<path d="M {F(lx)} {F(cy + r * 0.72)} L {F(lx + sg * r * 0.2)} {F(cy + r + 9)}" stroke="{gb}" stroke-width="{F(r * 0.08)}" stroke-linecap="round"/>'
                 f'<path d="M {F(lx - sg)} {F(cy + r * 0.72)} L {F(lx + sg * r * 0.18)} {F(cy + r + 7)}" stroke="{gl}" stroke-width="{F(r * 0.025)}" stroke-linecap="round" opacity="0.8"/>')
        bx, by = cx + sg * r * 0.62, cy - r * 0.92
        bell = f"M {F(bx - r * 0.34)} {F(by + r * 0.08)} Q {F(bx - r * 0.36)} {F(by - r * 0.4)} {F(bx)} {F(by - r * 0.4)} Q {F(bx + r * 0.36)} {F(by - r * 0.4)} {F(bx + r * 0.34)} {F(by + r * 0.08)} Q {F(bx)} {F(by + r * 0.01)} {F(bx - r * 0.34)} {F(by + r * 0.08)} Z"
        o.append(f'<g transform="rotate({sg * 30} {F(bx)} {F(by)})">'
                 + gpaint(f"{u}-bl{sg + 1}", bell, (bx - r * 0.4, by - r * 0.45, bx + r * 0.4, by + r * 0.12), gl, gb, gd, seed + sg, direction=(0.7, 0.7), angle=-60, n=12, ink_col=gi, ink_w=1.2)
                 + f'<circle cx="{F(bx)}" cy="{F(by - r * 0.42)}" r="{F(r * 0.06)}" fill="{gd}"/></g>')
    o.append(f'<path d="M {F(cx)} {F(cy - r)} L {F(cx)} {F(cy - r * 1.2)}" stroke="{gi}" stroke-width="{F(r * 0.07)}" stroke-linecap="round"/>'
             f'<path d="M {F(cx - r * 0.13)} {F(cy - r * 1.22)} L {F(cx + r * 0.13)} {F(cy - r * 1.22)}" stroke="{gi}" stroke-width="{F(r * 0.09)}" stroke-linecap="round"/>'
             f'<path d="M {F(cx - r * 0.1)} {F(cy - r * 1.23)} L {F(cx + r * 0.08)} {F(cy - r * 1.23)}" stroke="{gb}" stroke-width="{F(r * 0.035)}" stroke-linecap="round"/>')
    body = blob(cx, cy, r, r * 0.99, seed, 0.012, 24)
    o.append(gpaint(u + "-b", body, (cx - r, cy - r, cx + r, cy + r), "#F2CC6A", gb, "#8E6218", seed, direction=(0.55, 0.85), angle=-55, n=46, ink_col=gi, ink_w=1.7,
                    length=(r * 0.1, r * 0.4), width=(0.5, 1.6), tints=[gl, gd, "#FFF0B8"]))
    o.append(shade(u + "-bs", body, "#6E4A10", 0.6, 0.8, k=r * 0.14, op=0.45))
    o.append(rim(u + "-br", body, "#FFF4C8", -0.6, -0.8, k=r * 0.06, op=0.7))
    face = blob(cx, cy, r * 0.76, r * 0.75, seed + 1, 0.01, 24)
    o.append(f'<defs>{rg(u + "-fg", [(0, "#FFFBF0"), (0.8, "#F6ECD4"), (1, "#E2D2AE")], 0.4, 0.35, 0.7)}</defs><path d="{face}" fill="url(#{u}-fg)"/>')
    o.append(shade(u + "-fs", face, "#B8A47E", -0.5, -0.7, k=r * 0.07, op=0.55) + ink(face, gi, 1.3, seed, 1, 0.75))
    ticks = []
    for i in range(60):
        a = math.radians(i * 6 - 90)
        if i % 5 == 0:
            r0 = r * (0.56 if i % 15 else 0.52)
            ticks.append(f'<path d="M {F(cx + math.cos(a) * r0)} {F(cy + math.sin(a) * r0)} L {F(cx + math.cos(a) * r * 0.66)} {F(cy + math.sin(a) * r * 0.66)}" stroke="{NAVY}" stroke-width="{F(r * 0.04 if i % 15 else r * 0.055)}" stroke-linecap="round"/>')
        else:
            ticks.append(f'<circle cx="{F(cx + math.cos(a) * r * 0.64)}" cy="{F(cy + math.sin(a) * r * 0.64)}" r="{F(r * 0.012)}" fill="{NAVY}" opacity="0.7"/>')
    o.append("".join(ticks))
    # hands: minute at 58 past, hour just before twelve
    for ang, L, wdt in ((-90 - 12, r * 0.56, r * 0.05), (-90 - 2, r * 0.38, r * 0.07)):
        a = math.radians(ang)
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        tail = (cx - math.cos(a) * r * 0.1, cy - math.sin(a) * r * 0.1)
        nx, ny = -math.sin(a) * wdt, math.cos(a) * wdt
        o.append(f'<path d="{poly([tail, (cx + nx, cy + ny), tip, (cx - nx, cy - ny)])}" fill="{NAVY}" stroke="#1C2846" stroke-width="0.8" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 0.06)}" fill="{gb}" stroke="{gi}" stroke-width="0.9"/>')
    # glass glint
    o.append(f'<path d="M {F(cx - r * 0.6)} {F(cy - r * 0.3)} A {F(r * 0.68)} {F(r * 0.68)} 0 0 1 {F(cx - r * 0.18)} {F(cy - r * 0.66)}" stroke="#FFFFFF" stroke-width="{F(r * 0.055)}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    o.append(f'<path d="M {F(cx + r * 0.3)} {F(cy + r * 0.62)} A {F(r * 0.68)} {F(r * 0.68)} 0 0 1 {F(cx + r * 0.6)} {F(cy + r * 0.32)}" stroke="#FFFFFF" stroke-width="{F(r * 0.03)}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    return "".join(o)


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
    d = poly(jitter(sp, seed, r * 0.03))
    o = [paint(uid, d, bbox(sp), base, seed, tints=[light, darkc, light], angle=rot_ + 150, n=int(r * 1.2), ink_col=inkc_, ink_w=ink_w,
               length=(r * 0.2, r * 0.7), width=(0.3, max(0.6, r * 0.06)), op=(0.3, 0.7))]
    facets = []
    for i in range(0, 10, 2):
        a, b = sp[i], sp[(i + 1) % 10]
        facets.append(f"M {F(cx)} {F(cy)} L {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])} Z")
    o.append(f'<path d="{" ".join(facets)}" fill="{light}" opacity="0.45"/>')
    o.append(f'<path d="{" ".join(f"M {F(cx)} {F(cy)} L {F(p[0])} {F(p[1])}" for p in sp[::2])}" stroke="{darkc}" stroke-width="{F(max(0.5, r * 0.04))}" opacity="0.6"/>')
    return "".join(o)


def confetti(seed, box, n, avoid=(), cols=CONFETTI, scale=1.0):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    o = []
    for _ in range(n):
        for _try in range(20):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if not any((x - ax) ** 2 / rx ** 2 + (y - ay) ** 2 / ry ** 2 < 1 for ax, ay, rx, ry in avoid):
                break
        c = rnd.choice(cols)
        e = dk(c, 0.4)
        kind = rnd.random()
        a = rnd.uniform(0, 180)
        s = scale * rnd.uniform(0.8, 1.2)
        if kind < 0.45:
            w, h = 3.4 * s, 6.5 * s
            o.append(f'<rect x="{F(x - w / 2)}" y="{F(y - h / 2)}" width="{F(w)}" height="{F(h)}" rx="0.8" fill="{c}" stroke="{e}" stroke-width="0.5" transform="rotate({F(a)} {F(x)} {F(y)})"/>'
                     f'<rect x="{F(x - w / 2)}" y="{F(y - h / 2)}" width="{F(w * 0.4)}" height="{F(h)}" fill="#FFFFFF" opacity="0.35" transform="rotate({F(a)} {F(x)} {F(y)})"/>')
        elif kind < 0.72:
            o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(2.2 * s)}" fill="{c}" stroke="{e}" stroke-width="0.5"/><circle cx="{F(x - 0.7 * s)}" cy="{F(y - 0.7 * s)}" r="{F(0.7 * s)}" fill="#FFFFFF" opacity="0.6"/>')
        else:
            L = 9 * s
            dd = f"M {F(x)} {F(y)} q {F(L * 0.25)} {F(-L * 0.4)} {F(L * 0.5)} 0 t {F(L * 0.5)} 0"
            o.append(f'<path d="{dd}" stroke="{e}" stroke-width="{F(2.6 * s)}" fill="none" stroke-linecap="round" transform="rotate({F(a)} {F(x)} {F(y)})"/>'
                     f'<path d="{dd}" stroke="{c}" stroke-width="{F(1.6 * s)}" fill="none" stroke-linecap="round" transform="rotate({F(a)} {F(x)} {F(y)})"/>')
    return "".join(o)


def newyear_scene(u="ny"):
    o = []
    # --- night sky, fireworks and a far city, all inside the soft vignette
    sky = (f'<defs>{lg(u + "-sky", [(0, "#141B3E"), (0.55, "#22305E"), (0.85, "#4B3F74"), (1, "#7A5C86")])}</defs>'
           f'<rect x="0" y="0" width="380" height="330" fill="url(#{u}-sky)"/>')
    rnd = random.Random(3)
    sky += "".join(f'<circle cx="{F(rnd.uniform(0, 380))}" cy="{F(rnd.uniform(0, 190))}" r="{F(rnd.uniform(0.4, 1.1))}" fill="#FFF6D8" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>' for _ in range(70))
    sky += glow(u + "-hz", 230, 232, 190, 60, "#A07A9A", 0.55)      # city haze
    sky += firework_burst(u + "-fw1", 112, 92, 58, "#F2C04E", 1, n=24)
    sky += firework_burst(u + "-fw2", 282, 62, 42, "#F08AA0", 2, n=20)
    sky += firework_burst(u + "-fw3", 206, 44, 26, "#C8D8F4", 3, n=16, glow_op=0.4)
    sky += firework_burst(u + "-fw4", 332, 150, 24, "#F2C04E", 4, n=14, glow_op=0.35)
    # rising trails
    for x, y0, y1, c in ((112, 300, 150, "#F2C04E"), (282, 300, 110, "#F08AA0")):
        sky += f'<path d="M {x} {y0} Q {x + 6} {(y0 + y1) / 2} {x} {y1}" stroke="{c}" stroke-width="1.2" fill="none" stroke-dasharray="3 5" opacity="0.55"/>'
    sky += skyline(u + "-ct", 0, 380, 244, 5)
    sky += f'<path d="M 0 244 L 380 244 L 380 262 L 0 262 Z" fill="#3A3058" opacity="0.8"/>'
    sky += "".join(f'<path d="M {F(rnd.uniform(0, 380))} 246 l 0 {F(rnd.uniform(6, 14))}" stroke="#F6D27A" stroke-width="{F(rnd.uniform(0.6, 1.6))}" opacity="{rnd.uniform(0.15, 0.45):.2f}"/>' for _ in range(40))
    o.append(vignette(u + "-vg", sky, 198, 166, 196, 150, seed=7, edge=0.42, wobble=0.03))
    # --- the terrace table with a white cloth, lit warm from the right
    cloth_top = smooth_closed([(10, 262), (120, 254), (250, 252), (372, 258), (368, 276), (250, 282), (120, 284), (14, 280)])
    cloth = (f'<defs>{lg(u + "-cl", [(0, "#F7F0E2"), (0.6, "#E8E0D2"), (1, "#C9C2BC")])}'
             f'{lg(u + "-clf", [(0, "#DCD6CC"), (1, "#B4ADA8")])}</defs>'
             f'<path d="M 10 270 L 372 266 L 376 330 L 6 330 Z" fill="url(#{u}-clf)"/>'
             f'<path d="{cloth_top}" fill="url(#{u}-cl)"/>')
    # folds down the front
    for k, x in enumerate((40, 96, 150, 214, 268, 330)):
        cloth += f'<path d="M {x} 278 Q {x + (3 if k % 2 else -3)} 304 {x + (1 if k % 2 else -2)} 330" stroke="#A9A19C" stroke-width="{F(3 + k % 3)}" fill="none" opacity="0.35" stroke-linecap="round"/>'
        cloth += f'<path d="M {x + 6} 279 Q {x + 9} 304 {x + 7} 330" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="0.5" stroke-linecap="round"/>'
    cloth += f'<path d="M 10 270 Q 190 262 372 266" stroke="#B4ADA8" stroke-width="1.2" fill="none" opacity="0.6"/>'
    cloth += glow(u + "-tg", 290, 268, 110, 22, "#FFD58A", 0.5)
    cloth += dry_brush(11, (20, 256, 360, 282), ["#FFFFFF", "#E2D8C8", "#F6EEE0"], 70, angle=-4, length=(10, 30), width=(0.5, 1.6), op=(0.2, 0.5))
    o.append(vmask(u + "-tv", hmask(u + "-tm", cloth, 0, 380, 240, 330, fade=0.16), 0, 380, 240, 330, bottom=0.4))
    # reflections of the glasses and the clock on the cloth
    o.append(f'<ellipse cx="262" cy="282" rx="14" ry="3" fill="#E2B04A" opacity="0.25"/><ellipse cx="312" cy="284" rx="14" ry="3" fill="#E2B04A" opacity="0.25"/>')
    # --- confetti and streamers scattered on the cloth and in the air
    o.append(confetti(8, (20, 256, 360, 288), 18, avoid=((150, 240, 60, 52), (262, 230, 30, 90), (312, 230, 30, 90)), scale=0.9))
    o.append(curl_ribbon(74, 236, 44, GOLD, turns=3, amp=3.6, w=4.2, seed=2) + curl_ribbon(340, 226, 50, SILVER, turns=3.2, amp=3.2, w=4, seed=4))
    # --- clock and the toast
    o.append(brass_clock(u + "-ck", 150, 220, 46))
    o.append(soft_shadow(u + "-fs1", 266, 290, 22, 5, 0.3) + soft_shadow(u + "-fs2", 318, 290, 22, 5, 0.3))
    o.append(champagne_flute(u + "-f1", 266, 288, 132, 9, 11))
    o.append(champagne_flute(u + "-f2", 318, 288, 132, -10, 12))
    # clink sparkle where the rims meet
    sx, sy = 294, 162
    o.append(glow(u + "-cg", sx, sy, 26, 22, "#FFE9A8", 0.7, 0.4))
    o.append("".join(f'<path d="M {F(sx + math.cos(math.radians(a)) * 9)} {F(sy + math.sin(math.radians(a)) * 9)} l {F(math.cos(math.radians(a)) * 8)} {F(math.sin(math.radians(a)) * 8)}" stroke="#F8DC8A" stroke-width="1.8" stroke-linecap="round"/>' for a in (-160, -125, -90, -55, -20)))
    o.append(sparkle(sx, sy - 2, 9, "#FFFDF2") + sparkle(sx + 16, sy - 14, 4, "#FFF3C4") + sparkle(sx - 18, sy - 10, 3.5, "#FFF3C4"))
    o.append(sparkle(232, 120, 5, "#FFF3C4") + sparkle(352, 108, 4, "#FFFFFF") + sparkle(60, 170, 4, "#FFF3C4"))
    # airborne confetti
    o.append(confetti(9, (30, 30, 360, 240), 34, avoid=((150, 220, 56, 60), (266, 200, 24, 110), (318, 200, 24, 110), (112, 92, 40, 40), (282, 62, 30, 30)), scale=0.85))
    return "".join(o)


def newyear_garland(u="nyg"):
    """Gold cord with warm fairy lights, curling gold and silver streamers and painted stars."""
    o = [rope(u, "#D9A83E", "#F8DC8A", "#7A5212", w=3.0, twist=4)]
    # fairy lights: glow halo, then the bulb
    for k in range(10):
        x = 16 + 32 * k
        y = swag_y(x) + 2
        o.append(glow(f"{u}-lg{k}", x, y + 3, 11, 11, "#FFD36A", 0.6, 0.4))
    for k in range(10):
        x = 16 + 32 * k
        y = swag_y(x)
        o.append(f'<path d="M {F(x)} {F(y)} l 0 3" stroke="#7A5212" stroke-width="1.4"/><rect x="{F(x - 1.6)}" y="{F(y + 2.5)}" width="3.2" height="2.4" fill="#8A6A3A"/>'
                 f'<path d="{blob(x, y + 8, 3.0, 3.6, k, 0.04, 10)}" fill="#FFE9A0" stroke="#C99A2E" stroke-width="0.6"/><circle cx="{F(x - 0.8)}" cy="{F(y + 7)}" r="0.9" fill="#FFFFFF"/>')
    for k in range(8):
        x = 32 + 40 * k
        y = swag_y(x) + 1
        if k % 2 == 0:
            o.append(curl_ribbon(x, y, 36 + (k % 3) * 5, GOLD if k % 4 == 0 else SILVER, turns=3, amp=3.4, w=4.2, seed=k))
        else:
            L = 8 + (k % 3) * 4
            o.append(f'<path d="M {x} {F(y)} l 0 {L}" stroke="#8A93A3" stroke-width="0.9"/>')
            o.append(painted_star(f"{u}-s{k}", x, y + L + 9, 9.5, SILVER if k % 4 == 1 else GOLD, 20 + k, rot_=-90 + (k % 3 - 1) * 8))
    rnd = random.Random(5)
    o.append("".join(f'<circle cx="{F(rnd.uniform(0, 320))}" cy="{F(rnd.uniform(26, 70))}" r="{F(rnd.uniform(0.8, 1.6))}" fill="{rnd.choice(["#F8DC8A", "#C4CAD4", "#E8869A"])}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>' for _ in range(26)))
    for x, y, r in ((60, 56, 3.2), (140, 62, 3.6), (222, 60, 3), (300, 52, 3.6)):
        o.append(sparkle(x, y, r, "#FFF3C4"))
    return "".join(o)


def particles_confetti():
    return [("confetti1", curl_ribbon(20, 4, 32, GOLD, turns=2.5, amp=3.6, w=5, seed=1)),
            ("confetti2", confetti(21, (8, 8, 32, 32), 5, scale=1.3)),
            ("confetti3", painted_star("pc3", 20, 21, 15, GOLD, 3) + sparkle(33, 8, 4.5, "#FFFFFF", "#8A93A3"))]


# ================================================================ VALENTINE
def rose_bloom(uid, cx, cy, r, col, seed, ink_w=0.9):
    """Garden rose seen from above-front: a ring of outer petals, a cupped middle ring and a tight spiral heart."""
    rnd = random.Random(seed)
    light, darkc, deep = lt(col, 0.3), dk(col, 0.3), dk(col, 0.55)
    o = []
    a0 = rnd.uniform(0, 360)
    for ring, (rr, k_n, sz) in enumerate(((1.0, 6, 0.55), (0.66, 5, 0.42))):
        for k in range(k_n):
            a = math.radians(a0 + ring * 30 + k * 360 / k_n + rnd.uniform(-8, 8))
            px, py = cx + math.cos(a) * r * rr * 0.6, cy + math.sin(a) * r * rr * 0.6
            d = blob(px, py, r * sz, r * sz * 0.8, seed + ring * 10 + k, 0.1, 10, rot=math.degrees(a))
            c = mix(col, light, 0.25 * (1 - ring)) if math.sin(a) < 0 else mix(col, darkc, 0.3)
            o.append(f'<path d="{d}" fill="{c}"/>')
            o.append(f'<path d="{d}" fill="none" stroke="{deep}" stroke-width="{F(max(0.5, r * 0.05))}" opacity="0.5"/>')
    o.append(f'<path d="{blob(cx, cy, r * 0.42, r * 0.38, seed + 30, 0.08, 10)}" fill="{darkc}"/>')
    # spiral heart
    sp = []
    for i in range(22):
        t = i / 21
        a = math.radians(a0 + t * 720)
        rr = r * 0.4 * (1 - t) + r * 0.04
        sp.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85))
    o.append(f'<path d="{smooth_open(sp)}" stroke="{deep}" stroke-width="{F(max(0.7, r * 0.07))}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    o.append(f'<path d="{smooth_open(sp[6:14])}" stroke="{light}" stroke-width="{F(max(0.5, r * 0.05))}" fill="none" stroke-linecap="round" opacity="0.7" transform="translate(-0.6 -0.8)"/>')
    o.append(f'<path d="M {F(cx - r * 0.62)} {F(cy - r * 0.28)} Q {F(cx - r * 0.3)} {F(cy - r * 0.7)} {F(cx + r * 0.12)} {F(cy - r * 0.62)}" stroke="#FFFFFF" stroke-width="{F(max(0.7, r * 0.08))}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    return "".join(o)


def envelope(uid, cx, cy, w, h, rot_, col="#FBF3E6", seal="#C8323A", seed=1, flap_open=False):
    pts = jitter([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], seed, 0.4)
    d = poly(pts)
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">', f'<path d="{d}" fill="{col}"/>']
    o.append(f'<path d="{d}" fill="{dk(col, 0.12)}" opacity="0.5" transform="translate(1 1.4)"/><path d="{d}" fill="{col}"/>')
    o.append(f'<path d="M {F(cx - w / 2)} {F(cy - h / 2)} L {F(cx)} {F(cy + h * 0.14)} L {F(cx + w / 2)} {F(cy - h / 2)}" fill="{dk(col, 0.08)}" stroke="#B89A80" stroke-width="0.8" stroke-linejoin="round"/>')
    o.append(f'<path d="M {F(cx - w / 2)} {F(cy + h / 2)} L {F(cx - w * 0.08)} {F(cy + h * 0.02)} M {F(cx + w / 2)} {F(cy + h / 2)} L {F(cx + w * 0.08)} {F(cy + h * 0.02)}" stroke="#D2BCA4" stroke-width="0.7"/>')
    o.append(ink(d, "#8A6A52", 0.9, seed, 1, 0.65))
    o.append(f'<path d="{heart_d(cx, cy + h * 0.1, h * 0.17)}" fill="{seal}" stroke="{dk(seal, 0.4)}" stroke-width="0.6"/><circle cx="{F(cx - h * 0.06)}" cy="{F(cy + h * 0.02)}" r="{F(h * 0.04)}" fill="#FFFFFF" opacity="0.7"/>')
    o.append("</g>")
    return "".join(o)


def painted_heart(uid, cx, cy, s, col, seed, rot_=0, ink_w=None, shine=True, stitch=None, paper=False):
    d = heart_d(cx, cy, s, rot_)
    box = (cx - 1.1 * s, cy - 1.1 * s, cx + 1.1 * s, cy + 1.0 * s)
    o = [gpaint(uid, d, box, lt(col, 0.2), col, dk(col, 0.2), seed, direction=(0.4, 0.9), angle=-60, n=int(max(8, s * 2.2)), ink_w=ink_w if ink_w is not None else max(0.9, s * 0.07),
                length=(s * 0.3, s * 0.9), width=(s * 0.03, s * 0.08), op=(0.2, 0.5))]
    o.append(shade(uid + "-sh", d, dk(col, 0.35), 0.7, 0.8, k=s * 0.16, op=0.35))
    if paper:
        a, b = rot(cx, cy - 0.45 * s, cx, cy, rot_), rot(cx, cy + 0.85 * s, cx, cy, rot_)
        o.append(f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{dk(col, 0.3)}" stroke-width="{F(max(0.6, s * 0.05))}" opacity="0.5"/>'
                 f'<path d="{heart_d(cx, cy, s, rot_)}" fill="#FFFFFF" opacity="0.18" clip-path="url(#{uid}-pc)"/>'
                 f'<clipPath id="{uid}-pc"><rect x="{F(cx - 1.2 * s)}" y="{F(cy - 1.2 * s)}" width="{F(1.2 * s)}" height="{F(2.4 * s)}" transform="rotate({rot_} {F(cx)} {F(cy)})"/></clipPath>')
    if stitch:
        d2 = heart_d(cx, cy + 0.02 * s, s * 0.74, rot_)
        o.append(f'<path d="{d2}" fill="none" stroke="{stitch}" stroke-width="{F(max(0.7, s * 0.06))}" stroke-dasharray="{s * 0.16:.1f} {s * 0.12:.1f}" stroke-linecap="round" opacity="0.85"/>')
    if shine:
        a = rot(cx - 0.55 * s, cy - 0.5 * s, cx, cy, rot_)
        b = rot(cx - 0.72 * s, cy - 0.1 * s, cx, cy, rot_)
        c = rot(cx - 0.8 * s, cy - 0.55 * s, cx, cy, rot_)
        o.append(f'<path d="M {F(a[0])} {F(a[1])} Q {F(c[0])} {F(c[1])} {F(b[0])} {F(b[1])}" stroke="#FFFFFF" stroke-width="{F(max(1, s * 0.12))}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    return "".join(o)


def picket_fence(uid, x0, x1, y, h, seed, col="#F4EBDC", shade_col="#C9BBA8", ink_col="#8A7A66", step=18):
    """Low white picket fence along y (the rail), pickets h tall, lit from the left."""
    rnd = random.Random(seed)
    o = []
    x = x0
    while x < x1:
        w = 7
        top = y - h + rnd.uniform(-2, 2)
        d = poly(jitter([(x - w / 2, y + 12), (x - w / 2, top + 5), (x, top), (x + w / 2, top + 5), (x + w / 2, y + 12)], seed + int(x), 0.4))
        o.append(f'<path d="{d}" fill="{col}"/><path d="{poly([(x + 1, y + 12), (x + 1, top + 4.5), (x + w / 2, top + 5), (x + w / 2, y + 12)])}" fill="{shade_col}" opacity="0.7"/>')
        o.append(ink(d, ink_col, 0.7, seed + int(x), 1, 0.5))
        x += step
    for ry in (y - h * 0.55, y + 2):
        o.append(f'<path d="M {F(x0 - 6)} {F(ry)} L {F(x1 + 6)} {F(ry)} L {F(x1 + 6)} {F(ry + 5)} L {F(x0 - 6)} {F(ry + 5)} Z" fill="{col}" stroke="{ink_col}" stroke-width="0.7"/>'
                 f'<path d="M {F(x0 - 6)} {F(ry + 3.6)} L {F(x1 + 6)} {F(ry + 3.6)}" stroke="{shade_col}" stroke-width="1.6" opacity="0.8"/>')
    return "".join(o)


def rose_vine(uid, pts, seed, leaf_col="#4E7A3E", n_leaves=10, thorns=True):
    """A climbing stem along pts with alternating leaves."""
    rnd = random.Random(seed)
    d = smooth_open(pts)
    o = [f'<path d="{d}" stroke="#3E5A2A" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="{d}" stroke="#6E8A48" stroke-width="1" fill="none" stroke-linecap="round" transform="translate(-0.6 0)"/>']
    n = len(pts)
    for k in range(n_leaves):
        t = (k + 0.5) / n_leaves
        i = min(int(t * (n - 1)), n - 2)
        f = t * (n - 1) - i
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
        y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        side = 1 if k % 2 else -1
        ang = math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])) + side * rnd.uniform(55, 80)
        L = rnd.uniform(11, 16)
        o.append(leafy(f"{uid}-l{k}", x, y, L, L * 0.38, ang, leaf_col if k % 3 else lt(leaf_col, 0.15), seed + k))
        if thorns and k % 2 == 0:
            o.append(f'<path d="M {F(x)} {F(y)} l {F(-side * 2.5)} {F(-3)}" stroke="#5A3A2A" stroke-width="1.2" stroke-linecap="round"/>')
    return "".join(o)


def valentine_scene(u="vl"):
    o = []
    # --- blush morning: sky, a far blossom tree line and a picket fence, inside the vignette
    sky = (f'<defs>{lg(u + "-sky", [(0, "#E394B0"), (0.4, "#F3BCB2"), (0.72, "#F0BFD4"), (1, "#E4B4D0")])}</defs>'
           f'<rect width="380" height="330" fill="url(#{u}-sky)"/>')
    sky += glow(u + "-sun", 118, 84, 130, 100, "#FFF0C0", 0.95)
    rnd = random.Random(21)
    # far trees: mauve and pink rounded masses
    for k in range(14):
        x = 10 + k * 28 + rnd.uniform(-8, 8)
        r = rnd.uniform(22, 40)
        c = rnd.choice(["#D9A9BC", "#CFA0B8", "#E4B6C6", "#C797AE"])
        sky += f'<path d="{blob(x, 232 - r * 0.5, r, r * 0.8, 30 + k, 0.1, 14)}" fill="{c}" opacity="0.85"/>'
    sky += f'<path d="M 0 228 L 380 228 L 380 262 L 0 262 Z" fill="#D7B3C4" opacity="0.6"/>'
    sky += glow(u + "-mist", 190, 236, 220, 30, "#FBE7E4", 0.9)
    sky += picket_fence(u + "-pf", 8, 376, 236, 30, 4)
    # grass verge with a path, inside the vignette too (fades at the edges)
    sky += (f'<defs>{lg(u + "-gr", [(0, "#8FB45A"), (1, "#5E8A3E")])}</defs>'
            f'<path d="{smooth_closed([(0, 250), (120, 246), (260, 246), (380, 250), (380, 330), (0, 330)])}" fill="url(#{u}-gr)"/>')
    sky += f'<path d="{smooth_closed([(96, 330), (150, 292), (236, 268), (330, 262), (380, 266), (380, 284), (318, 282), (262, 296), (232, 330)])}" fill="#D9C6A8"/>'
    sky += dry_brush(31, (100, 264, 380, 330), ["#C6B08E", "#E8DAC0", "#B89E7A"], 60, angle=-6, length=(8, 22), width=(0.6, 1.8), op=(0.2, 0.5))
    sky += dry_brush(32, (0, 250, 380, 330), ["#A7C86A", "#4E7A34", "#7FA84E", "#B8D47A"], 200, angle=-80, length=(4, 12), width=(0.5, 1.4), op=(0.25, 0.6))
    sky += "".join(f'<ellipse cx="{F(rnd.uniform(0, 380))}" cy="{F(rnd.uniform(256, 328))}" rx="2" ry="1.2" fill="{rnd.choice(["#F6A8C0", "#FCE2EA", "#F28AA0"])}" transform="rotate({F(rnd.uniform(0, 180))} 0 0)" opacity="0.9"/>' for _ in range(0))
    o.append(vignette(u + "-vg", sky, 200, 184, 196, 156, seed=9, edge=0.2, wobble=0.03, ground=232, gfade=0.22))
    # petals on the grass (outside the mask so they stay crisp)
    o.append("".join(f'<g transform="rotate({F(rnd.uniform(0, 180))} {F(x := rnd.uniform(40, 340))} {F(y := rnd.uniform(262, 316))})"><ellipse cx="{F(x)}" cy="{F(y)}" rx="2.4" ry="1.4" fill="{rnd.choice(["#F6A8C0", "#FCE2EA", "#F28AA0"])}" opacity="0.9"/></g>' for _ in range(26)))
    # --- cast shadow of the post and box on the grass (light from the upper left)
    o.append(soft_shadow(u + "-sh", 262, 312, 70, 9, 0.32))
    o.append(f'<path d="{poly([(238, 316), (300, 308), (330, 318), (250, 322)])}" fill="{INK}" opacity="0.14"/>')
    # --- post
    post = jitter([(228, 186), (248, 186), (250, 318), (226, 318)], 4, 0.6)
    o.append(gpaint(u + "-post", poly(post), bbox(post), "#B98A5A", "#8E6238", "#5A3A22", 5, direction=(1, 0), angle=-89, n=36, ink_col="#4A2E18", ink_w=1.3, tints=["#C99A6A", "#6A4428", "#D9B080"]))
    o.append(f'<path d="M 231 190 L 231 316 M 243 200 L 243 316" stroke="#5A3A22" stroke-width="0.8" opacity="0.5"/>')
    # --- mailbox: body seen from the front-left; door open on the left end
    body = ("M 174 196 L 174 150 C 174 134 186 124 206 122 L 280 122 C 298 124 308 136 308 152 L 308 196 Z")
    o.append(gpaint(u + "-mb", body, (170, 118, 312, 198), "#E8716C", "#C93A48", "#8A1E2C", 6, direction=(0.5, 0.86), angle=-6, n=70, ink_col="#5E1018", ink_w=1.6,
                    tints=["#E8605E", "#9E1E2C", "#F08A84", "#B8303E"], length=(8, 28), width=(0.6, 2.0)))
    o.append(shade(u + "-mbs", body, "#6A0E1C", 0.3, 1, k=7, op=0.4))
    o.append(rim(u + "-mbh", body, "#FFB8AE", -0.3, -1, k=2.4, op=0.75))
    o.append(f'<path d="M 196 132 Q 240 124 290 128" stroke="#FFD2CC" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0.7"/>')
    # ribs of the pressed-steel body and the bottom seam
    o.append(f'<path d="M 206 124 L 206 196 M 278 123 L 278 196" stroke="#8A1E2C" stroke-width="1.2" fill="none" opacity="0.4"/>'
             f'<path d="M 176 192 L 306 192" stroke="#6A0E1C" stroke-width="1.4" opacity="0.5"/>')
    o.append(painted_heart(u + "-mh", 246, 160, 12, "#FBF0E6", 9, ink_w=0.9, shine=False, stitch="#D8344A"))
    # open front (the dark mouth) with letters stuffed in it
    mouth = "M 160 196 L 160 152 C 160 136 170 126 184 124 L 196 124 C 180 128 174 138 174 152 L 174 196 Z"
    o.append(f'<path d="{mouth}" fill="#A82A38" stroke="#5E1018" stroke-width="1.5" stroke-linejoin="round"/>'
             f'<path d="M 164 194 L 164 154 C 164 140 172 132 184 128 C 176 134 172 142 172 154 L 172 194 Z" fill="#3E1420"/>')
    o.append(envelope(u + "-e1", 166, 150, 30, 20, -24, seed=2) + envelope(u + "-e2", 160, 168, 30, 20, 8, col="#F8DDE2", seed=3) + envelope(u + "-e3", 170, 182, 28, 18, -8, seed=8))
    # the door, swung down on its bottom hinge and hanging open toward us
    door = "M 158 198 L 158 228 C 158 238 164 243 176 243 L 178 243 L 178 198 Z"
    o.append(gpaint(u + "-dr", door, (154, 194, 182, 246), "#F08A84", "#D64C56", "#8A1E2C", 7, direction=(0.2, 1), angle=-88, n=14, ink_col="#5E1018", ink_w=1.3))
    o.append(f'<path d="M 164 202 L 164 234" stroke="#F6B8B0" stroke-width="1.6" fill="none" opacity="0.6"/><rect x="166" y="236" width="6" height="3" rx="1" fill="#6A0E1C"/>'
             f'<path d="M 158 198 L 178 198" stroke="#5E1018" stroke-width="2" stroke-linecap="round"/>')
    # flag up, with a heart on it
    o.append(f'<path d="M 296 160 L 298 100" stroke="#7A5212" stroke-width="4" stroke-linecap="round"/><path d="M 296 160 L 298 100" stroke="#E9B949" stroke-width="2.2" stroke-linecap="round"/>')
    flag = jitter([(298, 96), (326, 94), (326, 114), (298, 116)], 5, 0.6)
    o.append(gpaint(u + "-fl", poly(flag), bbox(flag), "#F6D88A", "#E9B949", "#B88A1E", 8, direction=(0.7, 0.7), angle=0, n=10, ink_col="#7A5212", ink_w=1.0))
    o.append(f'<path d="{heart_d(312, 105, 5.5)}" fill="#D8344A"/><circle cx="296" cy="160" r="3" fill="#7A5212"/>')
    # --- climbing rose on the post, roses at the foot
    o.append(rose_vine(u + "-rv", [(222, 316), (232, 290), (246, 268), (238, 244), (248, 222), (236, 204), (244, 192)], 12, n_leaves=9))
    for k, (x, y, r, c) in enumerate(((236, 240, 9, "#D8344A"), (246, 206, 7.5, "#F28AA0"), (230, 272, 8, "#E8556A"))):
        o.append(rose_bloom(f"{u}-vr{k}", x, y, r, c, 50 + k))
    lv = [(180, 306, 22, 8, -150), (196, 290, 20, 7, -115), (280, 300, 22, 8, -30), (262, 286, 18, 7, -70), (306, 310, 18, 6, -8),
          (160, 314, 18, 6, -168), (212, 296, 18, 7, -100), (294, 290, 18, 6, -48), (242, 284, 16, 6, -88), (318, 316, 14, 5, 12), (150, 318, 14, 5, 190), (330, 306, 15, 5, -20)]
    for k, (x, y, L, w, a) in enumerate(lv):
        o.append(leafy(f"{u}-lf{k}", x, y + 6, L, w, a, "#4E7A3E" if k % 2 else "#3E6A34", 30 + k))
    for k, (x, y, r, c) in enumerate(((190, 300, 13, "#D8344A"), (214, 288, 11, "#F28AA0"), (270, 294, 14, "#C8263A"), (300, 306, 11, "#F28AA0"),
                                      (168, 310, 10, "#E8556A"), (242, 304, 12, "#E8556A"), (208, 312, 9, "#F6B3C0"), (276, 316, 9, "#D8344A"), (326, 316, 8, "#E8556A"))):
        o.append(rose_bloom(f"{u}-r{k}", x, y, r, c, 40 + k))
    # letters that did not fit
    o.append(envelope(u + "-e4", 112, 300, 34, 22, -12, col="#F8DDE2", seed=6) + envelope(u + "-e5", 134, 312, 32, 21, 6, seed=7))
    o.append(envelope(u + "-e6", 120, 226, 28, 18, -40, seed=13))     # one fluttering down
    # --- the rosefinch on the box
    o.append(bird(u + "-bd", 216, 124, 1.0, "#9A7A6A", "#E8859A", "#7A5E52", beak="#5A4A3E", flip=True, seed=15))
    # drifting hearts
    for k, (x, y, s, c, r_) in enumerate(((78, 150, 7, "#F28AA0", -12), (330, 70, 5, "#D8344A", 14), (352, 128, 6, "#F28AA0", -6), (160, 92, 4.5, "#E8556A", 8), (288, 62, 3.6, "#F6B3C0", -18))):
        o.append(painted_heart(f"{u}-sm{k}", x, y, s, c, 60 + k, rot_=r_, ink_w=0.7))
    return "".join(o)


def valentine_garland(u="vg"):
    """Rose-pink cord with folded paper hearts on strings, rosebuds and eucalyptus sprigs tied in with twine."""
    o = [rope(u, "#C87A8A", "#F2C6CE", "#7A3A4A", w=2.4, twist=4)]
    cols = ["#D8344A", "#F28AA0", "#C8263A", "#F6B3C0", "#E8556A", "#F28AA0", "#D8344A"]
    # eucalyptus sprigs behind the hearts
    for k, x in enumerate((60, 150, 240)):
        y = swag_y(x)
        for sgn in (-1, 1):
            pts = [(x, y), (x + sgn * 10, y + 10), (x + sgn * 16, y + 24)]
            o.append(f'<path d="{smooth_open(pts)}" stroke="#7A9A80" stroke-width="1.2" fill="none"/>')
            for j, t in enumerate((0.35, 0.65, 0.95)):
                px, py = x + sgn * 16 * t, y + 24 * t * t
                o.append(f'<ellipse cx="{F(px)}" cy="{F(py)}" rx="3.2" ry="2.4" fill="{"#9FBBA3" if j % 2 else "#86A88C"}" stroke="#5E7A62" stroke-width="0.5" transform="rotate({F(sgn * 30 + j * 20)} {F(px)} {F(py)})"/>')
    for k in range(7):
        x = 23 + k * 45.7
        y = swag_y(x)
        big = k % 2 == 0
        s = 11 if big else 8.5
        L = 6 if big else 11
        rr = (-1) ** k * 8
        o.append(f'<path d="M {F(x)} {F(y)} L {F(x + rr * 0.1)} {F(y + L)}" stroke="#9A6A72" stroke-width="0.9"/>')
        o.append(painted_heart(f"{u}-h{k}", x, y + L + s * 0.9, s, cols[k], 10 + k, rot_=rr, stitch="#FFF3F0" if k in (0, 4) else None, paper=k in (2, 6)))
    # twine bows at the hanging points and small rosebuds
    for x in (45.7, 137, 228, 0, 320):
        y = swag_y(x)
        o.append(f'<path d="M {F(x - 5)} {F(y - 2)} q 5 -4 5 2 q 0 -6 5 -2 q -3 4 -5 2 q -2 2 -5 -2 Z" fill="#E9CFA8" stroke="#9A7A52" stroke-width="0.6"/>')
    for k, x in enumerate((100, 190, 286)):
        y = swag_y(x) + 2
        o.append(f'<path d="M {F(x)} {F(y)} q -3 6 -1 12" stroke="#5E7A3E" stroke-width="1.1" fill="none"/>' + rose_bloom(f"{u}-rb{k}", x - 1, y + 14, 5.5, "#E8556A" if k % 2 else "#F28AA0", 70 + k))
    return "".join(o)


def particles_hearts():
    return [("heart1", painted_heart("ph1", 20, 19, 15, "#D8344A", 1, rot_=-8, paper=True)),
            ("heart2", painted_heart("ph2", 20, 19, 13, "#F28AA0", 2, rot_=10, stitch="#FFF3F0"))]


# ================================================================ ST PATRICK'S
SHAM = ("#3E9A4E", "#6CC070", "#24703A", "#1E4A2A")
SHAM2 = ("#5DB35A", "#8ED27E", "#3A8A3E", "#244E26")


def shamrock(uid, cx, cy, s, cols, seed, rot_=0, four=False, stem=True, lite=False):
    """Painted shamrock: three (or four) heart-shaped leaflets round a centre, lit from above, with a curved stem."""
    base, light, darkc, inkc_ = cols
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    if stem:
        sd = f"M {F(cx)} {F(cy + s * 0.1)} Q {F(cx + s * 0.1)} {F(cy + s * 0.7)} {F(cx + s * 0.38)} {F(cy + s * 1.1)}"
        o.append(f'<path d="{sd}" stroke="{inkc_}" stroke-width="{F(max(1.6, s * 0.17))}" fill="none" stroke-linecap="round"/>'
                 f'<path d="{sd}" stroke="{darkc}" stroke-width="{F(max(0.9, s * 0.1))}" fill="none" stroke-linecap="round"/>')
    angs = (-90, 0, 90, 180) if four else (-90, 30, 150)
    for k, a in enumerate(angs):
        rr = math.radians(a)
        lx, ly = cx + math.cos(rr) * s * 0.5, cy + math.sin(rr) * s * 0.5
        d = heart_d(lx, ly, s * 0.5, a + 90)
        box = (lx - s * 0.6, ly - s * 0.6, lx + s * 0.6, ly + s * 0.6)
        c = mix(base, light, 0.25) if a < 45 else base if a < 100 else mix(base, darkc, 0.2)
        if lite:
            o.append(f'<defs>{lg(f"{uid}-{k}g", [(0, light), (0.5, c), (1, darkc)], 0.5 - math.cos(rr) * 0.4, 0.3 - math.sin(rr) * 0.4, 0.5 + math.cos(rr) * 0.4, 0.7 + math.sin(rr) * 0.4)}</defs>'
                     f'<path d="{d}" fill="url(#{uid}-{k}g)" stroke="{inkc_}" stroke-width="{F(max(0.7, s * 0.06))}" stroke-opacity="0.7" stroke-linejoin="round"/>')
            o.append(f'<path d="M {F(cx)} {F(cy)} L {F(cx + math.cos(rr) * s * 0.74)} {F(cy + math.sin(rr) * s * 0.74)}" stroke="{light}" stroke-width="{F(max(0.6, s * 0.05))}" opacity="0.8" stroke-linecap="round"/>')
            continue
        o.append(gpaint(f"{uid}-{k}", d, box, light, c, darkc, seed + k, direction=(math.cos(rr) * 0.6, math.sin(rr) * 0.6 + 0.4), angle=a, n=int(max(6, s * 0.9)), ink_col=inkc_, ink_w=max(0.8, s * 0.06),
                        length=(s * 0.12, s * 0.4), width=(0.3, max(0.6, s * 0.04)), op=(0.25, 0.55), tints=[light, darkc, light]))
        o.append(f'<path d="M {F(cx)} {F(cy)} L {F(cx + math.cos(rr) * s * 0.74)} {F(cy + math.sin(rr) * s * 0.74)}" stroke="{light}" stroke-width="{F(max(0.6, s * 0.05))}" opacity="0.8" stroke-linecap="round"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(s * 0.08)}" fill="{darkc}"/>')
    o.append("</g>")
    return "".join(o)


def rainbow(u, cx, cy, R, bw, a0, a1, seed=1, op=0.85):
    """Soft painted rainbow: six bands, each with dry-brush streaks running along it."""
    cols = ["#E8604C", "#F2944A", "#F6C94E", "#7CB860", "#4E9AD0", "#8A6AC0"]
    rnd = random.Random(seed)
    o = []
    for i, c in enumerate(cols):
        r = R - bw * (i + 0.5)
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        o.append(f'<path d="M {F(p0[0])} {F(p0[1])} A {F(r)} {F(r)} 0 0 1 {F(p1[0])} {F(p1[1])}" stroke="{c}" stroke-width="{F(bw + 0.8)}" fill="none" opacity="{op}"/>')
        for j in range(3):
            rr = r + rnd.uniform(-bw * 0.32, bw * 0.32)
            q0 = (cx + rr * math.cos(math.radians(a0)), cy + rr * math.sin(math.radians(a0)))
            q1 = (cx + rr * math.cos(math.radians(a1)), cy + rr * math.sin(math.radians(a1)))
            dash = f"{rnd.uniform(14, 40):.0f} {rnd.uniform(6, 20):.0f} {rnd.uniform(8, 30):.0f} {rnd.uniform(4, 14):.0f}"
            o.append(f'<path d="M {F(q0[0])} {F(q0[1])} A {F(rr)} {F(rr)} 0 0 1 {F(q1[0])} {F(q1[1])}" stroke="{(lt(c, 0.35), dk(c, 0.15), lt(c, 0.2))[j]}" '
                     f'stroke-width="{F(rnd.uniform(0.8, 1.8))}" fill="none" stroke-dasharray="{dash}" stroke-dashoffset="{rnd.uniform(0, 40):.0f}" stroke-linecap="round" opacity="{op * 0.8:.2f}"/>')
    return "".join(o)


def thatched_cottage(u, x, base, w, seed=161):
    """Whitewashed Irish cottage with a thatched roof, a red half-door and warm windows; (x, base) = front-left corner."""
    h = w * 0.42
    wall = jitter([(x, base), (x, base - h), (x + w, base - h), (x + w, base)], seed, 0.6)
    o = [soft_shadow(u + "-sh", x + w * 0.5 + 8, base + 2, w * 0.62, 7, 0.3)]
    # gable end (right side) in shade
    gab = poly([(x + w, base), (x + w, base - h), (x + w + w * 0.22, base - h + 4), (x + w + w * 0.22, base + 2)])
    o.append(f'<path d="{gab}" fill="#C9C2B2"/>' + dry_brush(seed + 3, (x + w, base - h, x + w * 1.22, base), ["#B8B0A0", "#D9D2C2", "#A8A090"], 24, angle=-88, length=(6, 20), width=(0.6, 2), op=(0.2, 0.5)))
    o.append(gpaint(u + "-w", poly(wall), bbox(wall), "#FFFDF4", "#F3EEE0", "#D9D2C0", seed + 1, direction=(1, 0.3), angle=-88, n=50, ink_col="#8A7A62", ink_w=1.2,
                    tints=["#FFFFFF", "#E2DBC8", "#F6F0E0"], length=(6, 22), width=(0.6, 2.2), op=(0.2, 0.5)))
    # thatch: deep overhanging roof with straw strokes and a ridge of knotted thatch
    ridge_y = base - h - w * 0.3
    roof = smooth_closed([(x - w * 0.08, base - h + 4), (x - w * 0.05, base - h - w * 0.1), (x + w * 0.2, ridge_y + 3), (x + w * 0.55, ridge_y), (x + w * 0.9, ridge_y + 2),
                          (x + w * 1.3, base - h - w * 0.06), (x + w * 1.32, base - h + 6), (x + w * 1.26, base - h + 10), (x + w * 0.5, base - h + 14)])
    o.append(gpaint(u + "-r", roof, (x - w * 0.1, ridge_y - 4, x + w * 1.34, base - h + 16), "#E2B96A", "#C49242", "#8A5E22", seed + 2, direction=(0.2, 1), angle=-70, n=140, ink_col="#6A4418", ink_w=1.4,
                    tints=["#F2D28A", "#A87A32", "#D9A850", "#F8E0A0"], length=(8, 26), width=(0.5, 1.6), op=(0.3, 0.7)))
    o.append(shade(u + "-rs", roof, "#6A4418", 0, 1, k=5, op=0.4))
    o.append(f'<path d="M {F(x + w * 0.12)} {F(ridge_y + 6)} Q {F(x + w * 0.55)} {F(ridge_y - 1)} {F(x + w * 1.0)} {F(ridge_y + 5)}" stroke="#8A5E22" stroke-width="3" fill="none" stroke-linecap="round"/>'
             f'<path d="M {F(x + w * 0.12)} {F(ridge_y + 5)} Q {F(x + w * 0.55)} {F(ridge_y - 2)} {F(x + w * 1.0)} {F(ridge_y + 4)}" stroke="#F2D28A" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.8"/>')
    for k in range(9):
        tx = x + w * 0.14 + k * w * 0.1
        o.append(f'<path d="M {F(tx)} {F(ridge_y + 4)} l 0 {F(w * 0.06)}" stroke="#8A5E22" stroke-width="1.4" opacity="0.6"/>')
    # chimney and smoke
    cxm = x + w * 0.78
    o.append(f'<path d="{poly([(cxm - 6, ridge_y + 3), (cxm - 6, ridge_y - 16), (cxm + 6, ridge_y - 16), (cxm + 6, ridge_y + 3)])}" fill="#D9D2C0" stroke="#8A7A62" stroke-width="1"/>'
             f'<path d="M {F(cxm - 7)} {F(ridge_y - 16)} l 14 0" stroke="#8A7A62" stroke-width="2.2"/>')
    rnd = random.Random(seed)
    for k in range(6):
        sx_, sy_ = cxm + 2 + k * 5 + rnd.uniform(-2, 2), ridge_y - 22 - k * 9
        o.append(f'<path d="{blob(sx_, sy_, 5 + k * 1.6, 4 + k * 1.2, seed + k, 0.1, 10)}" fill="#F4F2EC" opacity="{0.55 - k * 0.07:.2f}"/>')
    # door (red half-door) and windows with glow and curtains
    dx = x + w * 0.42
    o.append(f'<rect x="{F(dx)}" y="{F(base - h * 0.78)}" width="{F(w * 0.16)}" height="{F(h * 0.78)}" fill="#B8382E" stroke="#5E1A14" stroke-width="1.1"/>'
             f'<rect x="{F(dx + 1.5)}" y="{F(base - h * 0.76)}" width="{F(w * 0.065)}" height="{F(h * 0.74)}" fill="#D04A3C" opacity="0.6"/>'
             f'<path d="M {F(dx)} {F(base - h * 0.4)} l {F(w * 0.16)} 0" stroke="#5E1A14" stroke-width="1.2"/><circle cx="{F(dx + w * 0.13)}" cy="{F(base - h * 0.36)}" r="1.2" fill="#E2B04A"/>')
    for wx in (x + w * 0.12, x + w * 0.7):
        wy, ww, wh = base - h * 0.7, w * 0.15, h * 0.4
        o.append(glow(f"{u}-wg{int(wx)}", wx + ww / 2, wy + wh / 2, ww * 1.4, wh * 1.3, "#FFD88A", 0.55))
        o.append(f'<rect x="{F(wx)}" y="{F(wy)}" width="{F(ww)}" height="{F(wh)}" fill="#F6C65A" stroke="#6A5A3A" stroke-width="1.2"/>'
                 f'<path d="M {F(wx + ww / 2)} {F(wy)} l 0 {F(wh)} M {F(wx)} {F(wy + wh / 2)} l {F(ww)} 0" stroke="#6A5A3A" stroke-width="1"/>'
                 f'<path d="M {F(wx)} {F(wy)} q {F(ww * 0.25)} {F(wh * 0.5)} 0 {F(wh)} Z M {F(wx + ww)} {F(wy)} q {F(-ww * 0.25)} {F(wh * 0.5)} 0 {F(wh)} Z" fill="#FBF3E6" opacity="0.9"/>')
        # window box with red flowers
        o.append(f'<rect x="{F(wx - 2)}" y="{F(wy + wh)}" width="{F(ww + 4)}" height="4" fill="#6A4A2A"/>' + "".join(
            f'<circle cx="{F(wx + 2 + i * ww / 4)}" cy="{F(wy + wh - 1.5)}" r="2.2" fill="{"#D8344A" if i % 2 else "#F06A6A"}"/>' for i in range(5)))
    return "".join(o)


def drystone_wall(u, x0, x1, y_top, h, seed):
    """Irish drystone wall: irregular grey stones in rough courses, moss in the joints, lit from the upper right."""
    rnd = random.Random(seed)
    o = [f'<path d="{poly([(x0, y_top + h + 4), (x0, y_top + 2), (x1, y_top), (x1, y_top + h + 4)])}" fill="#5A5A58"/>']
    y = y_top
    course = 0
    cols = ["#9A9A92", "#B2AFA4", "#8A8C86", "#A8A49A", "#C2BEB2", "#7E8078"]
    while y < y_top + h - 2:
        ch = rnd.uniform(8, 13)
        x = x0 + (rnd.uniform(0, 10) if course % 2 else 0)
        while x < x1:
            sw = rnd.uniform(12, 26)
            pts = jitter([(x, y), (x + sw, y + rnd.uniform(-1, 1)), (x + sw, y + ch), (x, y + ch + rnd.uniform(-1, 1))], seed + int(x) + course, 1.2)
            d = smooth_closed(pts)
            c = rnd.choice(cols)
            o.append(f'<path d="{d}" fill="{c}"/>')
            o.append(f'<path d="{d}" fill="none" stroke="{lt(c, 0.35)}" stroke-width="1.4" opacity="0.6" transform="translate(0.8 -0.8)" clip-path="url(#{u}-s{int(x)}_{course})"/>'
                     f'<clipPath id="{u}-s{int(x)}_{course}"><path d="{d}"/></clipPath>')
            o.append(f'<path d="{d}" fill="none" stroke="#3E3E3A" stroke-width="0.9" opacity="0.55"/>')
            x += sw + rnd.uniform(1.5, 4)
        y += ch + rnd.uniform(1, 3)
        course += 1
    # moss and lichen in the joints
    for _ in range(26):
        mx, my = rnd.uniform(x0, x1), rnd.uniform(y_top, y_top + h)
        o.append(f'<path d="{blob(mx, my, rnd.uniform(2, 5), rnd.uniform(1.5, 3), seed + int(mx), 0.15, 8)}" fill="{rnd.choice(["#7AA048", "#9EBE60", "#D9C860"])}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    # capstones
    o.append("".join(f'<path d="{blob(x0 + 8 + i * 16, y_top - 2 + (i % 2), 9, 4, seed + 90 + i, 0.12, 10)}" fill="{rnd.choice(cols)}" stroke="#3E3E3A" stroke-width="0.8"/>' for i in range(int((x1 - x0) / 16) + 1)))
    return "".join(o)


def kettle(u, cx, base, s=1.0, seed=5):
    """Black enamel kettle with a copper lid, sitting on the wall, a wisp of steam."""
    def p(x, y):
        return (cx + x * s, base + y * s)
    body = smooth_closed([p(-22, 0), p(-24, -14), p(-18, -26), p(-6, -32), p(8, -32), p(20, -26), p(24, -12), p(22, 0)])
    o = [soft_shadow(u + "-sh", cx + 3 * s, base + 1, 26 * s, 4 * s, 0.4)]
    o.append(gpaint(u + "-b", body, bbox([p(-24, -34), p(24, 0)]), "#5A5660", "#2C2830", "#121014", seed, direction=(0.8, 0.5), angle=-80, n=30, ink_col="#0A0A0C", ink_w=1.3, tints=["#4A4650", "#18161C", "#6A6670"]))
    o.append(rim(u + "-rm", body, "#9AC8A8", -0.6, -0.8, k=1.8, op=0.7))
    o.append(f'<path d="M {F(p(-10, -26)[0])} {F(p(-10, -26)[1])} Q {F(p(-16, -16)[0])} {F(p(-16, -16)[1])} {F(p(-14, -6)[0])} {F(p(-14, -6)[1])}" stroke="#FFFFFF" stroke-width="{F(2.4 * s)}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    # spout, lid, handle
    o.append(f'<path d="M {F(p(20, -22)[0])} {F(p(20, -22)[1])} Q {F(p(34, -30)[0])} {F(p(34, -30)[1])} {F(p(36, -40)[0])} {F(p(36, -40)[1])} L {F(p(31, -41)[0])} {F(p(31, -41)[1])} Q {F(p(26, -30)[0])} {F(p(26, -30)[1])} {F(p(16, -26)[0])} {F(p(16, -26)[1])} Z" fill="#2C2830" stroke="#0A0A0C" stroke-width="1"/>')
    o.append(f'<ellipse cx="{F(p(1, -32)[0])}" cy="{F(p(1, -32)[1])}" rx="{F(11 * s)}" ry="{F(3.2 * s)}" fill="#C47A3A" stroke="#6A3A14" stroke-width="1"/><circle cx="{F(p(1, -36)[0])}" cy="{F(p(1, -36)[1])}" r="{F(2.4 * s)}" fill="#C47A3A" stroke="#6A3A14" stroke-width="0.8"/>')
    hd = f"M {F(p(-14, -30)[0])} {F(p(-14, -30)[1])} Q {F(p(0, -56)[0])} {F(p(0, -56)[1])} {F(p(14, -30)[0])} {F(p(14, -30)[1])}"
    o.append(f'<path d="{hd}" stroke="#0A0A0C" stroke-width="{F(4.4 * s)}" fill="none" stroke-linecap="round"/><path d="{hd}" stroke="#4A4650" stroke-width="{F(2.2 * s)}" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M {F(p(-5, -43)[0])} {F(p(-5, -43)[1])} Q {F(p(0, -50)[0])} {F(p(0, -50)[1])} {F(p(5, -43)[0])} {F(p(5, -43)[1])}" stroke="#9AC8A8" stroke-width="1" fill="none" opacity="0.6"/>')
    # steam
    rnd = random.Random(seed)
    for k in range(4):
        sx, sy = p(36 + k * 3 + rnd.uniform(-3, 3), -46 - k * 9)
        o.append(f'<path d="{blob(sx, sy, 5 + k * 2, 3.5 + k, seed + k, 0.14, 8)}" fill="#FFFFFF" opacity="{0.5 - k * 0.1:.2f}"/>')
    return "".join(o)


def sheep(x, y, s=1.0, seed=1):
    return (f'<path d="{blob(x, y - 4 * s, 6 * s, 4.2 * s, seed, 0.14, 10)}" fill="#F6F2E8"/><path d="{blob(x, y - 2 * s, 5 * s, 2.4 * s, seed + 1, 0.14, 8)}" fill="#C9C4B8" opacity="0.6"/>'
            f'<circle cx="{F(x + 5.5 * s)}" cy="{F(y - 5 * s)}" r="{F(2.2 * s)}" fill="#2A2420"/><path d="M {F(x - 3 * s)} {F(y - 1)} l 0 {F(3 * s)} M {F(x + 2 * s)} {F(y - 1)} l 0 {F(3 * s)}" stroke="#2A2420" stroke-width="{F(1.1 * s)}"/>')


def stpatricks_scene(u="sp"):
    o = []
    rnd = random.Random(17)
    # --- sky after rain: grey cloud at the upper left, clearing to warm light on the right; rainbow
    sky = (f'<defs>{lg(u + "-sky", [(0, "#8FA7C4"), (0.35, "#B9CDE0"), (0.7, "#E4EAE6"), (1, "#F2E8C8")])}</defs>'
           f'<rect width="380" height="330" fill="url(#{u}-sky)"/>')
    sky += glow(u + "-sun", 320, 60, 150, 120, "#FFF2C4", 0.95)
    for k, (x, y, w, c, sc) in enumerate(((60, 52, 170, "#8A9AB4", "#6A7A96"), (150, 36, 120, "#A4B2C8", "#7E8EA8"), (14, 98, 110, "#A8B4C8", "#7E8EA8"))):
        sky += cloud_puffs(f"{u}-cl{k}", x, y, w, 40 + k, col=c, shade_col=sc, n=6)
    for k, (x, y, w) in enumerate(((230, 54, 120), (100, 120, 90))):
        sky += cloud_puffs(f"{u}-wc{k}", x, y, w, 50 + k, col="#FFFFFF", shade_col="#C5D2E2", n=6)
    sky += rainbow(u + "-rb", 232, 300, 232, 11, 192, 328, 3, op=0.75)
    # --- far hills (bluer and paler further away), fields, hedgerows, sheep
    sky += f'<path d="{smooth_closed([(0, 176), (60, 160), (150, 170), (230, 150), (320, 162), (380, 150), (380, 240), (0, 240)])}" fill="#8FB49A"/>'
    sky += f'<path d="{smooth_closed([(0, 198), (80, 182), (190, 192), (290, 176), (380, 190), (380, 260), (0, 260)])}" fill="#6FA468"/>'
    sky += dry_brush(61, (0, 176, 380, 236), ["#8FBE78", "#5A8A4E", "#A8D088"], 70, angle=-8, length=(10, 40), width=(0.6, 2.4), op=(0.2, 0.5))
    # hedgerows and walls on the mid hill
    for pts, c, w in (([(40, 196), (120, 188), (210, 196), (300, 182)], "#3E6A3A", 2.4), ([(130, 208), (160, 192)], "#8A8A82", 1.8), ([(250, 204), (330, 186)], "#8A8A82", 1.8)):
        sky += f'<path d="{smooth_open(pts)}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" opacity="0.8"/>'
    for k, (x, y, s) in enumerate(((80, 212, 0.55), (96, 206, 0.5), (300, 200, 0.55), (318, 206, 0.5), (112, 214, 0.5))):
        sky += sheep(x, y, s, 70 + k)
    sky += f'<path d="{smooth_closed([(0, 226), (70, 214), (170, 222), (260, 210), (380, 222), (380, 330), (0, 330)])}" fill="#5E9A4C"/>'
    sky += (f'<defs>{lg(u + "-gr", [(0, "#79B35C"), (1, "#4E8A3E")])}</defs>'
            f'<path d="{smooth_closed([(0, 258), (90, 250), (200, 256), (300, 248), (380, 254), (380, 330), (0, 330)])}" fill="url(#{u}-gr)"/>')
    sky += dry_brush(62, (0, 214, 380, 330), ["#A7D06A", "#3E7A34", "#7FB84E", "#C8E08A"], 260, angle=-82, length=(4, 14), width=(0.5, 1.5), op=(0.25, 0.6))
    # path to the door
    sky += f'<path d="{smooth_closed([(228, 330), (240, 300), (250, 270), (262, 254), (272, 254), (266, 272), (262, 300), (268, 330)])}" fill="#C9B78E" opacity="0.9"/>'
    o.append(vignette(u + "-vg", sky, 200, 184, 198, 160, seed=13, edge=0.3, wobble=0.03, ground=224, gfade=0.2))
    # --- the cottage on the mid ground
    o.append(thatched_cottage(u + "-ct", 212, 254, 96))
    # --- foreground: drystone wall with the kettle, shamrocks and wildflowers
    o.append(soft_shadow(u + "-ws", 92, 310, 110, 8, 0.35))
    o.append(drystone_wall(u + "-dw", 0, 186, 268, 36, 5))
    o.append(kettle(u + "-kt", 122, 266, 0.78))
    for k in range(10):
        x, y = rnd.uniform(0, 200), rnd.uniform(300, 326)
        o.append(f'<path d="M {F(x)} {F(y)} q {F(rnd.uniform(-3, 3))} {F(-8)} {F(rnd.uniform(-4, 4))} {F(-16)}" stroke="{rnd.choice(["#3E8A44", "#5DAA5A"])}" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    for k, (x, y, s, r_) in enumerate(((36, 300, 13, -12), (76, 310, 11, 8), (162, 306, 12, -6), (18, 318, 9, 14), (120, 316, 10, -18), (196, 318, 9, 10), (56, 320, 8, 4), (104, 300, 8, 20), (146, 320, 7, -10))):
        o.append(shamrock(f"{u}-c{k}", x, y, s, SHAM if k % 2 else SHAM2, 20 + k, rot_=r_))
    o.append(shamrock(u + "-four", 222, 304, 15, SHAM2, 31, rot_=12, four=True))
    for k, (x, y) in enumerate(((300, 300), (340, 312), (318, 322), (356, 296))):
        o.append(f'<path d="M {F(x)} {F(y + 8)} q 1 -6 0 -12" stroke="#4E7A34" stroke-width="1.2" fill="none"/>' + "".join(
            f'<ellipse cx="{F(x + math.cos(math.radians(a)) * 2.6)}" cy="{F(y - 4 + math.sin(math.radians(a)) * 2.6)}" rx="2" ry="1.1" fill="#FFF8E6" transform="rotate({a} {F(x + math.cos(math.radians(a)) * 2.6)} {F(y - 4 + math.sin(math.radians(a)) * 2.6)})"/>' for a in range(0, 360, 60))
            + f'<circle cx="{x}" cy="{y - 4}" r="1.3" fill="#F2C14E"/>')
    for x, y, r in ((300, 120, 4), (364, 86, 3.4)):
        o.append(sparkle(x, y, r, "#FFFFFF"))
    return "".join(o)


def stpatricks_garland(u="spg"):
    """Shamrock vine on a green cord with small tricolour ribbon bows and the odd gold coin."""
    o = [rope(u, "#2E6A3A", "#8ED27E", "#163A20", w=2.4, twist=4)]
    pts = [(x, swag_y(x) + 2.2 * math.sin(x / TW * 2 * math.pi * 4)) for x in range(0, TW + 1, 8)]
    vd = smooth_open(pts)
    o.append(f'<path d="{vd}" stroke="#3E7A3E" stroke-width="1.6" fill="none"/>')
    rnd = random.Random(4)
    for k, x in enumerate(range(12, TW, 23)):
        y = swag_y(x)
        side = -1 if k % 2 else 1
        s = rnd.uniform(9, 12)
        o.append(f'<path d="M {F(x)} {F(y)} q {F(side * 3)} {F(4)} {F(side * 4)} {F(9)}" stroke="#2E6A3A" stroke-width="1.1" fill="none"/>')
        o.append(shamrock(f"{u}-s{k}", x + side * 4, y + 9 + s * 0.6, s, SHAM if k % 3 else SHAM2, 30 + k, rot_=180 + side * rnd.uniform(5, 30), stem=False, lite=True))
    for k, x in enumerate((48, 160, 272)):
        y = swag_y(x)
        for j, c in enumerate(("#2E8A4A", "#F4F0E6", "#E8863A")):
            o.append(f'<path d="M {F(x)} {F(y)} q {F(-14 + j * 4)} {F(6 + j * 2)} {F(-10 + j * 3)} {F(16 + j * 4)}" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
                     f'<path d="M {F(x)} {F(y)} q {F(14 - j * 4)} {F(6 + j * 2)} {F(10 - j * 3)} {F(16 + j * 4)}" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M {F(x - 7)} {F(y - 3)} q 7 -5 7 2 q 0 -7 7 -2 q -3 5 -7 2 q -4 3 -7 -2 Z" fill="#F4F0E6" stroke="#8A7A52" stroke-width="0.6"/>')
    for k, x in enumerate((104, 216)):
        y = swag_y(x) + 2
        o.append(f'<path d="M {F(x)} {F(y)} l 0 10" stroke="#8A6212" stroke-width="0.9"/>')
        o.append(f'<circle cx="{F(x)}" cy="{F(y + 18)}" r="8.5" fill="#F2C14E" stroke="#8A5E12" stroke-width="1.1"/><circle cx="{F(x)}" cy="{F(y + 18)}" r="6.2" fill="none" stroke="#C9922A" stroke-width="0.9"/>'
                 f'<path d="M {F(x - 5)} {F(y + 14.5)} A 5.5 5.5 0 0 1 {F(x)} {F(y + 12.5)}" stroke="#FFF3C4" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
                 + shamrock(f"{u}-cs{k}", x, y + 18, 4, SHAM, 90 + k, stem=False, lite=True))
    return "".join(o)


def particles_clovers():
    return [("clover1", shamrock("pc1", 20, 17, 15, SHAM, 1, rot_=-10)),
            ("clover2", shamrock("pc2", 20, 17, 13, SHAM2, 2, rot_=15, four=True))]


# ================================================================ SPRING
def tulip(uid, x, base, top, col, seed, lean=0, s=13, leaves=True):
    """Tulip on a stem from (x, base) to the head at (x + lean, top): three visible cupped petals, lit from the left."""
    hx, hy = x + lean, top
    stem = smooth_open([(x, base), (x + lean * 0.4, (base + top) / 2), (hx, hy + 8)])
    o = [f'<path d="{stem}" stroke="#3E6A2E" stroke-width="{F(s * 0.28)}" fill="none" stroke-linecap="round"/><path d="{stem}" stroke="#7FA84E" stroke-width="{F(s * 0.1)}" fill="none" stroke-linecap="round" transform="translate(-0.8 0)"/>']
    if leaves:
        rnd = random.Random(seed)
        for side in (-1, 1):
            L = (base - top) * rnd.uniform(0.45, 0.65)
            tipx = x + side * L * 0.45 + lean * 0.2
            pts = [(x, base - 2), (x + side * L * 0.2 + lean * 0.1, base - L * 0.5), (tipx, base - L), (x + side * L * 0.32 + lean * 0.1, base - L * 0.45), (x + side * 3, base - 4)]
            d = smooth_closed(pts)
            o.append(f'<path d="{d}" fill="{"#5E8A3E" if side < 0 else "#4E7A34"}"/><path d="{smooth_open([(x, base - 2), (x + side * L * 0.22 + lean * 0.1, base - L * 0.5), (tipx, base - L)])}" stroke="#8FBE68" stroke-width="{F(s * 0.07)}" fill="none" opacity="0.7"/>'
                     + ink(d, "#2E5224", 0.8, seed + side, 1, 0.5))
    light, darkc = lt(col, 0.35), dk(col, 0.3)
    # back petal, two front petals
    back = smooth_closed([(hx - s * 0.55, hy - s * 0.3), (hx - s * 0.35, hy - s * 1.0), (hx, hy - s * 1.2), (hx + s * 0.35, hy - s * 1.0), (hx + s * 0.55, hy - s * 0.3), (hx, hy + s * 0.1)])
    o.append(f'<path d="{back}" fill="{darkc}"/>')
    for side in (1, -1):
        pet = smooth_closed([(hx, hy + s * 0.55), (hx + side * s * 0.72, hy - s * 0.2), (hx + side * s * 0.6, hy - s * 0.9), (hx + side * s * 0.3, hy - s * 0.55), (hx + side * s * 0.05, hy - s * 0.2)])
        c = mix(col, light, 0.3) if side < 0 else col
        o.append(gpaint(f"{uid}-p{side + 1}", pet, (hx - s * 0.8, hy - s * 1.0, hx + s * 0.8, hy + s * 0.6), light, c, darkc, seed + side, direction=(side * 0.5, 0.8), angle=-85, n=10,
                        ink_col=dk(col, 0.5), ink_w=0.9, length=(s * 0.3, s * 0.9), width=(0.4, 1.2), op=(0.2, 0.5)))
    o.append(f'<path d="M {F(hx - s * 0.42)} {F(hy - s * 0.75)} Q {F(hx - s * 0.55)} {F(hy - s * 0.1)} {F(hx - s * 0.3)} {F(hy + s * 0.25)}" stroke="#FFFFFF" stroke-width="{F(s * 0.1)}" fill="none" opacity="0.55" stroke-linecap="round"/>')
    return "".join(o)


def galvanized_can(u, x, base, s=1.0, seed=61):
    """Old galvanized watering can seen from the front-left: tapered body, hoop handle over the top, long spout with a rose."""
    def p(px, py):
        return (x + px * s, base + py * s)
    zinc, zl, zd, zi = "#9EB2BE", "#DCE8EE", "#5E7482", "#3A4A54"
    o = [soft_shadow(u + "-sh", *p(14, 2), 50 * s, 7 * s, 0.35)]
    # hoop handle over the top (back half first; the front half is drawn after the body)
    hoop = f"M {F(p(-22, -64)[0])} {F(p(-22, -64)[1])} C {F(p(-20, -100)[0])} {F(p(-20, -100)[1])} {F(p(22, -100)[0])} {F(p(22, -100)[1])} {F(p(24, -64)[0])} {F(p(24, -64)[1])}"
    o.append(f'<path d="{hoop}" stroke="{zi}" stroke-width="{F(7 * s)}" fill="none" stroke-linecap="round"/><path d="{hoop}" stroke="{zinc}" stroke-width="{F(4.6 * s)}" fill="none" stroke-linecap="round"/>'
             f'<path d="{hoop}" stroke="{zl}" stroke-width="{F(1.4 * s)}" fill="none" stroke-linecap="round" transform="translate(-1.2 -1)" opacity="0.9"/>')
    # spout
    sp = [p(-30, -20), p(-56, -54), p(-62, -66), p(-54, -70), p(-28, -40)]
    o.append(gpaint(u + "-sp", smooth_closed(sp), bbox(sp), zl, zinc, zd, seed + 1, direction=(0.7, 0.7), angle=-52, n=12, ink_col=zi, ink_w=1.1))
    rose_ = blob(*p(-60, -70), 8 * s, 5 * s, seed, 0.03, 12, rot=-52)
    o.append(f'<path d="{rose_}" fill="{zd}" stroke="{zi}" stroke-width="1.1"/>' + "".join(f'<circle cx="{F(p(-60 + dx, -70 + dy)[0])}" cy="{F(p(-60 + dx, -70 + dy)[1])}" r="0.8" fill="#2A3A44"/>' for dx, dy in ((-3, 1), (0, -1.5), (3, -4), (1, 2), (-2, -3))))
    # body
    body = jitter([p(-30, -62), p(32, -62), p(38, -4), p(36, 0), p(-34, 0), p(-36, -4)], seed, 0.6)
    bd = smooth_closed(body)
    o.append(f'<defs>{lg(u + "-bg", [(0, zl), (0.28, zinc), (0.72, "#7E94A2"), (1, zd)], 0, 0, 1, 0)}</defs><path d="{bd}" fill="url(#{u}-bg)"/>')
    o.append(strokes(u + "-bs", bd, bbox(body), ["#C9D8E0", "#6E8290", "#B0C2CC", "#E6EEF2"], seed + 2, n=90, angle=-89, length=(8, 30), width=(0.5, 2.2), opacity=(0.2, 0.5), curve=0.1))
    # dents, rust spots and a seam
    rnd = random.Random(seed)
    o.append(clipped(u + "-bc", bd, "".join(f'<path d="{blob(*p(rnd.uniform(-28, 30), rnd.uniform(-56, -6)), rnd.uniform(2, 5), rnd.uniform(1.5, 3), seed + k, 0.2, 8)}" fill="{rnd.choice(["#B8784A", "#8E5A34"])}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>' for k in range(7))
                     + f'<path d="M {F(p(-33, -30)[0])} {F(p(-33, -30)[1])} L {F(p(38, -30)[0])} {F(p(38, -30)[1])}" stroke="{zd}" stroke-width="1" opacity="0.5"/>'))
    o.append(f'<path d="{smooth_open([p(-22, -56), p(-24, -30), p(-22, -8)])}" stroke="#FFFFFF" stroke-width="{F(3.2 * s)}" fill="none" opacity="0.5" stroke-linecap="round"/>')
    o.append(ink(bd, zi, 1.4, seed, 2, 0.7))
    for yy in (-58, -5):
        o.append(f'<path d="M {F(p(-33, yy)[0])} {F(p(-33, yy)[1])} L {F(p(35, yy)[0])} {F(p(35, yy)[1])}" stroke="{zd}" stroke-width="2.2" opacity="0.6"/><path d="M {F(p(-33, yy - 1.6)[0])} {F(p(-33, yy - 1.6)[1])} L {F(p(35, yy - 1.6)[0])} {F(p(35, yy - 1.6)[1])}" stroke="{zl}" stroke-width="0.8" opacity="0.7"/>')
    # top rim (elliptical opening) with dark inside
    o.append(f'<path d="{blob(*p(1, -63), 31 * s, 5 * s, seed + 3, 0.02, 16)}" fill="{zd}" stroke="{zi}" stroke-width="1.2"/><path d="{blob(*p(1, -63), 26 * s, 3 * s, seed + 4, 0.03, 14)}" fill="#2E3E48"/>')
    # front half of the hoop
    o.append(f'<path d="M {F(p(-22, -64)[0])} {F(p(-22, -64)[1])} l 0 6 M {F(p(24, -64)[0])} {F(p(24, -64)[1])} l 0 6" stroke="{zi}" stroke-width="{F(5 * s)}" stroke-linecap="round"/>')
    return "".join(o)


def blossom(uid, cx, cy, r, col, seed, center="#F2C14E", rot_=0, open_=1.0):
    """Five-petal cherry blossom, each petal a notched oval with a deeper pink base."""
    o = []
    rnd = random.Random(seed)
    for i in range(5):
        a = math.radians(rot_ + i * 72 - 90 + rnd.uniform(-6, 6))
        px, py = cx + math.cos(a) * r * 0.5 * open_, cy + math.sin(a) * r * 0.5 * open_
        d = blob(px, py, r * 0.46, r * 0.36, seed + i, 0.1, 9, rot=math.degrees(a))
        o.append(f'<path d="{d}" fill="{col}" stroke="{dk(col, 0.35)}" stroke-width="{F(max(0.5, r * 0.05))}" stroke-opacity="0.6"/>')
        o.append(f'<path d="M {F(cx)} {F(cy)} l {F(math.cos(a) * r * 0.55)} {F(math.sin(a) * r * 0.55)}" stroke="{dk(col, 0.25)}" stroke-width="{F(max(0.6, r * 0.07))}" opacity="0.5" stroke-linecap="round"/>')
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 0.2)}" fill="{dk(col, 0.4)}" opacity="0.5"/>')
    o.append("".join(f'<circle cx="{F(cx + math.cos(math.radians(rot_ + k * 45)) * r * 0.22)}" cy="{F(cy + math.sin(math.radians(rot_ + k * 45)) * r * 0.22)}" r="{F(max(0.6, r * 0.08))}" fill="{center}"/>' for k in range(8)))
    return "".join(o)


def blossom_branch(u, pts, seed, n_bloss=12):
    """Cherry branch along pts: dark bark with a lit edge, side twigs, blossoms, buds and small fresh leaves."""
    rnd = random.Random(seed)
    o = [tapered(pts, 7, 2.2, "#5A3E2E"), tapered(pts, 3, 1, "#8A6A52", 0.6, ' transform="translate(0 -1.2)"')]
    n = len(pts)
    items = []
    for k in range(n_bloss):
        t = (k + 0.5) / n_bloss
        i = min(int(t * (n - 1)), n - 2)
        f = t * (n - 1) - i
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
        y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        side = 1 if k % 2 else -1
        tx, ty = x + rnd.uniform(-6, 6), y + side * rnd.uniform(8, 18)
        o.append(f'<path d="M {F(x)} {F(y)} Q {F((x + tx) / 2 + 3)} {F((y + ty) / 2)} {F(tx)} {F(ty)}" stroke="#5A3E2E" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
        items.append((tx, ty, k))
    for tx, ty, k in items:
        kind = rnd.random()
        if kind < 0.65:
            o.append(blossom(f"{u}-b{k}", tx, ty, rnd.uniform(7, 10), rnd.choice(["#F7B9CC", "#FAD0DC", "#F39CB8"]), seed + k, rot_=rnd.uniform(0, 72)))
        elif kind < 0.85:
            o.append(f'<path d="{blob(tx, ty, 3.2, 4.2, seed + k, 0.08, 8)}" fill="#E9789A" stroke="#A84468" stroke-width="0.6"/><path d="M {F(tx)} {F(ty + 3)} l 0 3" stroke="#5A3E2E" stroke-width="1"/>')
        else:
            o.append(leafy(f"{u}-lf{k}", tx, ty, 9, 3.4, rnd.uniform(-120, -60), "#7FB84E", seed + k))
    return "".join(o)


def butterfly(uid, x, y, s, c1, c2, rot_=0, seed=3):
    o = [f'<g transform="translate({F(x)} {F(y)}) rotate({rot_})">']
    for sg in (-1, 1):
        up = blob(sg * 6 * s, -4 * s, 6.5 * s, 5.5 * s, seed, 0.08, 10, rot=sg * 20)
        lo = blob(sg * 5 * s, 5 * s, 4.5 * s, 4 * s, seed + 1, 0.08, 10, rot=sg * -20)
        o.append(f'<path d="{up}" fill="{c1}" stroke="{dk(c1, 0.45)}" stroke-width="0.8"/><path d="{lo}" fill="{c2}" stroke="{dk(c2, 0.45)}" stroke-width="0.8"/>')
        o.append(f'<path d="M 0 {F(-2 * s)} Q {F(sg * 5 * s)} {F(-6 * s)} {F(sg * 10 * s)} {F(-5 * s)} M 0 {F(-1 * s)} Q {F(sg * 6 * s)} {F(-2 * s)} {F(sg * 11 * s)} {F(-1 * s)}" stroke="{dk(c1, 0.4)}" stroke-width="0.6" fill="none" opacity="0.7"/>')
        o.append(f'<circle cx="{F(sg * 7.5 * s)}" cy="{F(-5 * s)}" r="{F(1.6 * s)}" fill="#FFFFFF" opacity="0.85"/><circle cx="{F(sg * 6 * s)}" cy="{F(6 * s)}" r="{F(1 * s)}" fill="{dk(c2, 0.5)}" opacity="0.7"/>')
    o.append(f'<path d="M 0 {F(-7 * s)} L 0 {F(8 * s)}" stroke="#3A2418" stroke-width="{F(1.8 * s)}" stroke-linecap="round"/>'
             f'<path d="M 0 {F(-7 * s)} q -2 -5 -4 -6 M 0 {F(-7 * s)} q 2 -5 4 -6" stroke="#3A2418" stroke-width="0.7" fill="none"/></g>')
    return "".join(o)


def terracotta_pot_tipped(u, cx, cy, s, seed=7):
    """Clay pot lying on its side (opening to the right), soil spilling out."""
    def p(x, y):
        return (cx + x * s, cy + y * s)
    body = smooth_closed(jitter([p(-30, -14), p(16, -20), p(18, 20), p(-30, 12)], seed, 0.6))
    o = [soft_shadow(u + "-sh", *p(-4, 20), 34 * s, 5 * s, 0.35)]
    o.append(f'<path d="{blob(*p(34, 12), 26 * s, 7 * s, seed + 5, 0.12, 12)}" fill="#5A3A24"/>' + "".join(f'<circle cx="{F(p(24 + k * 5, 8 + (k % 3))[0])}" cy="{F(p(24 + k * 5, 8 + (k % 3))[1])}" r="{F(1.2 * s)}" fill="#3E2816"/>' for k in range(7)))
    o.append(gpaint(u + "-b", body, bbox([p(-32, -22), p(20, 22)]), "#E0905E", "#C66A3D", "#8A4420", seed, direction=(0.2, 1), angle=-5, n=40, ink_col="#6E3418", ink_w=1.3, tints=["#D88A5A", "#9A4A26", "#E8A070"], length=(8, 26), width=(0.6, 2)))
    o.append(shade(u + "-bs", body, "#7A3418", 0, 1, k=6, op=0.35))
    rimd = smooth_closed(jitter([p(14, -24), p(24, -26), p(26, 24), p(16, 24)], seed + 1, 0.5))
    o.append(gpaint(u + "-r", rimd, bbox([p(12, -28), p(28, 26)]), "#E8A070", "#D27A4A", "#8A4420", seed + 2, direction=(0.2, 1), angle=-5, n=14, ink_col="#6E3418", ink_w=1.2))
    o.append(f'<path d="{blob(*p(26, 0), 3.5 * s, 22 * s, seed + 3, 0.03, 12)}" fill="#4A2A18"/>')
    return "".join(o)


def grass_tufts(seed, box, n, cols=("#5E8A3E", "#7FA84E", "#3E6A2E"), h=(6, 16)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    s = "".join(f'<path d="M {F(x)} {F(y)} q {F(rnd.uniform(-3, 3))} {F(-hh / 2)} {F(rnd.uniform(-5, 5))} {F(-hh)}" stroke="{rnd.choice(cols)}"/>'
                for x, y, hh in [(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(*h)) for _ in range(n)])
    return f'<g stroke-width="1.6" stroke-linecap="round" fill="none">{s}</g>'


def daisy(cx, cy, r, seed=1, col="#FFFDF6", center="#F2C14E"):
    rnd = random.Random(seed)
    o = ["".join(f'<ellipse cx="{F(cx + math.cos(math.radians(a)) * r * 0.6)}" cy="{F(cy + math.sin(math.radians(a)) * r * 0.6)}" rx="{F(r * 0.45)}" ry="{F(r * 0.2)}" fill="{col}" stroke="#C9BFA8" stroke-width="0.4" transform="rotate({a + rnd.uniform(-8, 8):.0f} {F(cx + math.cos(math.radians(a)) * r * 0.6)} {F(cy + math.sin(math.radians(a)) * r * 0.6)})"/>' for a in range(0, 360, 40))]
    o.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r * 0.3)}" fill="{center}" stroke="#B88A1E" stroke-width="0.5"/><circle cx="{F(cx - r * 0.1)}" cy="{F(cy - r * 0.1)}" r="{F(r * 0.12)}" fill="#FFE9A0"/>')
    return "".join(o)


def spring_scene(u="sp"):
    o = []
    rnd = random.Random(23)
    # --- soft spring morning: sky, far blossom tree and meadow, inside the vignette
    sky = (f'<defs>{lg(u + "-sky", [(0, "#A9CFEA"), (0.5, "#D6E8F2"), (0.8, "#F3EFD8"), (1, "#E9EBC8")])}</defs>'
           f'<rect width="380" height="330" fill="url(#{u}-sky)"/>')
    sky += glow(u + "-sun", 90, 60, 130, 100, "#FFF6CC", 0.9)
    sky += cloud_puffs(u + "-c1", 200, 70, 90, 3, shade_col="#D4E0EC", n=5) + cloud_puffs(u + "-c2", 60, 120, 70, 4, shade_col="#D4E0EC", n=4)
    # far meadow and a blossoming tree
    sky += f'<path d="{smooth_closed([(0, 214), (90, 204), (200, 210), (300, 200), (380, 206), (380, 260), (0, 260)])}" fill="#A6CB86"/>'
    sky += f'<path d="M 60 212 l 0 -26 M 52 196 l 16 0" stroke="#7A5A3E" stroke-width="3" stroke-linecap="round"/>'
    for k in range(9):
        a = k * 40
        sky += f'<path d="{blob(60 + math.cos(math.radians(a)) * 20, 184 + math.sin(math.radians(a)) * 12, 14, 11, 80 + k, 0.1, 10)}" fill="{rnd.choice(["#F3B6CA", "#F7C9D8", "#EFA3BE"])}"/>'
    sky += f'<path d="{blob(60, 178, 26, 18, 99, 0.08, 14)}" fill="#F7C9D8"/>'
    sky += picket_fence(u + "-pf", 120, 380, 222, 24, 6, step=16)
    sky += (f'<defs>{lg(u + "-gr", [(0, "#8CBE62"), (1, "#5A8A3E")])}</defs>'
            f'<path d="{smooth_closed([(0, 236), (100, 230), (220, 234), (380, 228), (380, 330), (0, 330)])}" fill="url(#{u}-gr)"/>')
    sky += dry_brush(42, (0, 228, 380, 330), ["#B4D47A", "#4E7A34", "#7FA84E", "#D2E69A"], 260, angle=-82, length=(4, 14), width=(0.5, 1.5), op=(0.25, 0.6))
    sky += glow(u + "-dap", 250, 300, 90, 30, "#FFF6C0", 0.5)
    o.append(vignette(u + "-vg", sky, 198, 186, 200, 160, seed=15, edge=0.3, wobble=0.03, ground=226, gfade=0.2))
    # --- background tulips and grass behind the can
    for k, (x, top, c, lean) in enumerate(((132, 196, "#F6C23E", -6), (150, 184, "#F2D25E", 4), (170, 200, "#F6C23E", 8), (318, 206, "#F28AA0", 6), (338, 196, "#D8344A", -4))):
        o.append(tulip(f"{u}-bt{k}", x, 262 if k < 3 else 268, top, c, 10 + k, lean, s=11))
    o.append(grass_tufts(5, (0, 250, 380, 318), 90))
    # --- the can with its bouquet
    o.append(galvanized_can(u + "-wc", 246, 300, 1.0))
    tl = [(226, 150, "#D8344A", -16), (246, 128, "#F28AA0", -2), (268, 144, "#E8556A", 12), (236, 168, "#F6B3C0", -6), (284, 170, "#D8344A", 18), (256, 160, "#F6C23E", 4)]
    for k, (x, top, c, lean) in enumerate(tl):
        o.append(tulip(f"{u}-t{k}", x, 240, top, c, 20 + k, lean, s=13, leaves=k in (0, 2, 4)))
    o.append(f'<path d="{blob(247, 237, 31, 5, 31, 0.02, 16)}" fill="#3A4A54" opacity="0.9"/>')
    # bluebird on the hoop
    o.append(bird(u + "-bd", 258, 203, 0.95, "#4C8BD0", "#E89A5A", "#2F5FA6", beak="#4A4A4A", flip=True, seed=25))
    # --- front: tipped pot, daisies, a butterfly, the blossom branch and falling petals
    o.append(terracotta_pot_tipped(u + "-pot", 104, 296, 1.0))
    for k, (x, y, r) in enumerate(((180, 310, 6), (322, 312, 5.5), (60, 318, 5), (346, 300, 4.5), (152, 318, 4.5))):
        o.append(f'<path d="M {F(x)} {F(y + 6)} q 1 -8 0 -14" stroke="#4E7A34" stroke-width="1.2" fill="none"/>' + daisy(x, y - 6, r, k))
    o.append(blossom_branch(u + "-br", [(384, 18), (340, 34), (300, 42), (262, 64), (236, 88)], 33, n_bloss=12))
    o.append(blossom_branch(u + "-br2", [(372, 40), (340, 70), (322, 100)], 44, n_bloss=5))
    o.append(butterfly(u + "-bf", 150, 130, 1.25, "#F2A0B8", "#F6CC6A", -15))
    o.append(f'<path d="M 160 142 q 20 18 44 6 q 18 -10 30 4" stroke="#8A6A42" stroke-width="0.9" stroke-dasharray="2 2.6" fill="none" opacity="0.6"/>')
    for k in range(16):
        x, y = rnd.uniform(120, 370), rnd.uniform(80, 290)
        a = rnd.uniform(0, 180)
        o.append(f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="3.2" ry="1.9" fill="{rnd.choice(["#F7B9CC", "#FAD0DC", "#F39CB8"])}" stroke="#D88AA2" stroke-width="0.4" transform="rotate({F(a)} {F(x)} {F(y)})" opacity="0.95"/>')
    return "".join(o)


def spring_garland(u="sg"):
    """Cherry-blossom bough: a twisting branch along the swag with blossoms, buds, leaves and loose petals."""
    pts = [(x, swag_y(x) + 2.2 * math.sin(x / TW * 2 * math.pi * 3)) for x in range(0, TW + 1, 8)]
    o = [tapered(pts, 5.5, 5.5, "#5A3E2E"), tapered(pts, 2.2, 2.2, "#8A6A52", 0.55, ' transform="translate(0 -1.2)"')]
    rnd = random.Random(4)
    for k, x in enumerate(range(10, TW, 20)):
        y = swag_y(x)
        side = -1 if k % 2 else 1
        tx, ty = x + rnd.uniform(-4, 4), y + side * rnd.uniform(7, 14)
        o.append(f'<path d="M {F(x)} {F(y)} Q {F((x + tx) / 2 + 2)} {F((y + ty) / 2)} {F(tx)} {F(ty)}" stroke="#5A3E2E" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
        kind = k % 5
        if kind in (0, 2, 3):
            o.append(blossom(f"{u}-b{k}", tx, ty, rnd.uniform(7.5, 10), rnd.choice(["#F7B9CC", "#FAD0DC", "#F39CB8"]), 50 + k, rot_=rnd.uniform(0, 72)))
        elif kind == 1:
            o.append(f'<path d="{blob(tx, ty, 3.4, 4.4, 60 + k, 0.08, 8)}" fill="#E9789A" stroke="#A84468" stroke-width="0.6"/>')
        else:
            o.append(leafy(f"{u}-lf{k}", tx, ty, 11, 4, side * 70 + rnd.uniform(-20, 20) + (180 if side < 0 else 0), "#7FB84E", 70 + k))
    for k in range(12):
        x, y = rnd.uniform(0, 320), rnd.uniform(40, 70)
        o.append(f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="2.6" ry="1.5" fill="{rnd.choice(["#F7B9CC", "#FAD0DC"])}" stroke="#D88AA2" stroke-width="0.4" transform="rotate({F(rnd.uniform(0, 180))} {F(x)} {F(y)})"/>')
    return "".join(o)


def petal(uid, cx, cy, s, col, rot_, seed, edge=None):
    pts = [(0, -1.0), (0.18, -0.82), (0.55, -0.5), (0.62, 0.05), (0.35, 0.6), (0, 0.9), (-0.35, 0.6), (-0.62, 0.05), (-0.55, -0.5), (-0.18, -0.82)]
    pts = [rot(cx + x * s, cy + y * s, cx, cy, rot_) for x, y in pts]
    pts[0] = rot(cx, cy - 0.74 * s, cx, cy, rot_)
    d = smooth_closed(pts)
    o = [gpaint(uid, d, bbox(pts), lt(col, 0.35), col, dk(col, 0.12), seed, direction=(0, 1), angle=rot_ - 90, n=10, ink_col=edge or dk(col, 0.35), ink_w=1.0,
                length=(s * 0.4, s * 1.2), width=(0.4, 1.0), op=(0.3, 0.6))]
    a = rot(cx, cy + 0.85 * s, cx, cy, rot_)
    b = rot(cx, cy + 0.1 * s, cx, cy, rot_)
    o.append(f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{dk(col, 0.25)}" stroke-width="0.9" opacity="0.6" stroke-linecap="round"/>')
    o.append(f'<path d="{blob(*rot(cx, cy + 0.55 * s, cx, cy, rot_), 0.2 * s, 0.25 * s, seed, 0.05, 8)}" fill="#E05A88" opacity="0.35"/>')
    return "".join(o)


def particles_petals():
    return [("petal1", petal("pp1", 20, 20, 15, "#F6A8C0", 20, 1)),
            ("petal2", petal("pp2", 20, 20, 13, "#FCE2EA", -30, 2, edge="#D88AA2")),
            ("petal3", blossom("pp3", 20, 20, 15, "#F8C0D2", 3, rot_=10))]


# ================================================================ SUMMER
def umbrella(uid, cx, cy, R, rot_, cols, seed, ink_col="#6A2E1E"):
    """Beach umbrella canopy centred on the pole top (cx, cy), radius R, tilted rot_ degrees; scalloped edge, lit from the right."""
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})">']
    n = 7
    rimy = cy + R * 0.42
    xs = [cx - R + 2 * R * i / n for i in range(n + 1)]
    apex = (cx, cy - R * 0.06)
    for i in range(n):
        x0, x1 = xs[i], xs[i + 1]
        mid = (x0 + x1) / 2
        d = (f"M {F(apex[0])} {F(apex[1])} Q {F(x0 + (apex[0] - x0) * 0.35)} {F(cy - R * 0.25)} {F(x0)} {F(rimy)} "
             f"Q {F(mid)} {F(rimy + R * 0.13)} {F(x1)} {F(rimy)} Q {F(x1 + (apex[0] - x1) * 0.35)} {F(cy - R * 0.25)} {F(apex[0])} {F(apex[1])} Z")
        c = cols[i % 2]
        lit = 0.5 + 0.5 * (mid - cx) / R          # right side faces the sun
        base = mix(dk(c, 0.22), lt(c, 0.12), lit)
        o.append(gpaint(f"{uid}-{i}", d, (x0 - 4, cy - R * 0.4, x1 + 4, rimy + R * 0.16), lt(c, 0.25), base, dk(c, 0.3), seed + i, direction=(0, 1), angle=-90 + (mid - cx) * 0.4, n=18,
                        tints=[lt(c, 0.25), dk(c, 0.12), lt(c, 0.45)], ink_col=ink_col, ink_w=1.1, length=(6, 24), width=(0.5, 1.8)))
    under = f"M {F(xs[0])} {F(rimy)} " + " ".join(f"Q {F((xs[i] + xs[i + 1]) / 2)} {F(rimy + R * 0.13)} {F(xs[i + 1])} {F(rimy)}" for i in range(n))
    o.append(f'<path d="{under}" stroke="{ink_col}" stroke-width="1.6" fill="none" opacity="0.7"/>')
    o.append(f'<path d="{under}" stroke="#FFF3DC" stroke-width="2.4" stroke-dasharray="0.1 8" stroke-linecap="round" fill="none" transform="translate(0 3)" opacity="0.9"/>')
    o.append(f'<path d="{blob(apex[0], apex[1] - 3, 5, 4, 2, 0.05, 10)}" fill="#E2B04A" stroke="#7A5212" stroke-width="1"/><path d="M {F(apex[0])} {F(apex[1] - 6)} l 0 -8" stroke="#7A5212" stroke-width="2" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def deck_chair(u, x, base, s=1.0, seed=71, c1="#2F6FB8", c2="#FBF4E6"):
    """Folding deck chair seen from the front-left: wooden frame, striped canvas sling with a sag, lit from the right."""
    def p(px, py):
        return (x + px * s, base + py * s)
    wood, wd, wi = "#C9995A", "#8A6232", "#4A3218"
    o = [soft_shadow(u + "-sh", *p(6, 2), 46 * s, 7 * s, 0.35)]
    def bar(a, b, w=4.2):
        return (f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{wi}" stroke-width="{F((w + 1.6) * s)}" stroke-linecap="round"/>'
                f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{wood}" stroke-width="{F(w * s)}" stroke-linecap="round"/>'
                f'<path d="M {F(a[0])} {F(a[1])} L {F(b[0])} {F(b[1])}" stroke="{wd}" stroke-width="{F(w * 0.35 * s)}" stroke-linecap="round" opacity="0.6" transform="translate(1 1)"/>')
    # back legs (far side) and the rear frame
    o.append(bar(p(28, 0), p(8, -62), 3.6) + bar(p(44, -4), p(24, -66), 3.6))
    # seat bar and front legs
    o.append(bar(p(-18, -2), p(-4, -38), 3.6) + bar(p(0, 2), p(12, -36), 3.6))
    # canvas sling: from the top bar down to the front bar, sagging
    top_l, top_r = p(8, -62), p(24, -66)
    bot_l, bot_r = p(-10, -24), p(8, -22)
    sling = (f"M {F(top_l[0])} {F(top_l[1])} L {F(top_r[0])} {F(top_r[1])} C {F(p(30, -46)[0])} {F(p(30, -46)[1])} {F(p(22, -30)[0])} {F(p(22, -30)[1])} {F(bot_r[0])} {F(bot_r[1])} "
             f"L {F(bot_l[0])} {F(bot_l[1])} C {F(p(2, -32)[0])} {F(p(2, -32)[1])} {F(p(12, -46)[0])} {F(p(12, -46)[1])} Z")
    o.append(f'<path d="{sling}" fill="{c2}"/>')
    stripes = []
    for i in range(7):
        t0, t1 = i / 7, (i + 1) / 7
        if i % 2:
            continue
        a0 = (top_l[0] + (top_r[0] - top_l[0]) * t0, top_l[1] + (top_r[1] - top_l[1]) * t0)
        a1 = (top_l[0] + (top_r[0] - top_l[0]) * t1, top_l[1] + (top_r[1] - top_l[1]) * t1)
        b0 = (bot_l[0] + (bot_r[0] - bot_l[0]) * t0, bot_l[1] + (bot_r[1] - bot_l[1]) * t0)
        b1 = (bot_l[0] + (bot_r[0] - bot_l[0]) * t1, bot_l[1] + (bot_r[1] - bot_l[1]) * t1)
        m0 = ((a0[0] + b0[0]) / 2 + 10 * s, (a0[1] + b0[1]) / 2 + 2 * s)
        m1 = ((a1[0] + b1[0]) / 2 + 10 * s, (a1[1] + b1[1]) / 2 + 2 * s)
        stripes.append(f"M {F(a0[0])} {F(a0[1])} L {F(a1[0])} {F(a1[1])} Q {F(m1[0])} {F(m1[1])} {F(b1[0])} {F(b1[1])} L {F(b0[0])} {F(b0[1])} Q {F(m0[0])} {F(m0[1])} {F(a0[0])} {F(a0[1])} Z")
    o.append(clipped(u + "-sc", sling, f'<path d="{" ".join(stripes)}" fill="{c1}"/>'
                     + strokes(u + "-ss", sling, bbox([top_l, top_r, bot_l, bot_r], 12), [lt(c1, 0.3), dk(c1, 0.3), "#FFFFFF", "#D9CFBE"], seed, n=60, angle=-62, length=(6, 20), width=(0.4, 1.4), opacity=(0.15, 0.4))
                     + f'<path d="{sling}" fill="{INK}" opacity="0.18" transform="translate(-6 0)"/>'))
    o.append(shade(u + "-sls", sling, "#3A2418", 1, 0, k=5 * s, op=0.25))
    o.append(ink(sling, "#4A3218", 1.1, seed, 1, 0.6))
    # top bar and the front frame bar in front of the canvas
    o.append(bar(p(8, -62), p(24, -66), 4.4) + bar(p(-10, -24), p(8, -22), 4.4))
    o.append(bar(p(-18, -2), p(12, -36), 0.1))
    return "".join(o)


def seashell(cx, cy, s, col, seed, rot_=0):
    d = smooth_closed(jitter([(cx - 5 * s, cy + 2 * s), (cx - 4 * s, cy - 3 * s), (cx, cy - 6 * s), (cx + 4 * s, cy - 3 * s), (cx + 5 * s, cy + 2 * s), (cx, cy + 3 * s)], seed, 0.3))
    o = [f'<g transform="rotate({rot_} {F(cx)} {F(cy)})"><path d="{d}" fill="{col}"/>']
    o.append("".join(f'<path d="M {F(cx)} {F(cy + 2.5 * s)} L {F(cx + dx * s)} {F(cy - 4.5 * s + abs(dx) * 0.5 * s)}" stroke="{dk(col, 0.3)}" stroke-width="{F(0.6 * s)}" opacity="0.7"/>' for dx in (-3.5, -1.8, 0, 1.8, 3.5)))
    o.append(f'<path d="{d}" fill="none" stroke="{dk(col, 0.45)}" stroke-width="{F(0.7 * s)}" opacity="0.7"/><path d="M {F(cx - 3 * s)} {F(cy - 1 * s)} q 2 -3 4 -3.4" stroke="#FFFFFF" stroke-width="{F(0.8 * s)}" fill="none" opacity="0.7"/></g>')
    return "".join(o)


def pail(uid, cx, base, s=1.0, seed=81):
    def p(px, py):
        return (cx + px * s, base + py * s)
    top, wt, wb, h = base - 40 * s, 44 * s, 34 * s, 40 * s
    body = jitter([(cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2, base), (cx - wb / 2, base)], seed, 0.5)
    o = [soft_shadow(uid + "-sh", cx - 4 * s, base + 1, 28 * s, 5 * s, 0.35)]
    o.append(f'<path d="M {F(cx + 3 * s)} {F(top + 8 * s)} L {F(cx + 16 * s)} {F(top - 30 * s)}" stroke="#B8862E" stroke-width="{F(5 * s)}" stroke-linecap="round"/><path d="M {F(cx + 3 * s)} {F(top + 8 * s)} L {F(cx + 16 * s)} {F(top - 30 * s)}" stroke="#F6C23E" stroke-width="{F(3 * s)}" stroke-linecap="round"/>')
    o.append(f'<path d="{smooth_closed([p(14, -70), p(24, -84), p(20, -92), p(11, -88), p(9, -74)])}" fill="#F6C23E" stroke="#8A6212" stroke-width="1.1"/>')
    o.append(gpaint(uid, poly(body), bbox(body), "#8AD6E0", "#3FA3B5", "#1E6A78", seed, direction=(-1, 0.2), angle=-88, n=36, ink_col="#1E5A66", tints=["#6EC2D0", "#2A7A8A", "#9AD8E2"]))
    o.append(clipped(uid + "-c", poly(body), f'<path d="M {F(cx - 30 * s)} {F(top + 14 * s)} L {F(cx + 30 * s)} {F(top + 14 * s)}" stroke="#FFF6E6" stroke-width="{F(6 * s)}"/>'
                     f'<path d="M {F(cx - 30 * s)} {F(top + 14 * s)} L {F(cx + 30 * s)} {F(top + 14 * s)}" stroke="#F2644A" stroke-width="{F(6 * s)}" stroke-dasharray="4 6"/>'))
    o.append(f'<path d="{blob(cx, top, wt / 2, 4 * s, seed, 0.03, 14)}" fill="#2A7A8A" stroke="#1E5A66" stroke-width="1.2"/><path d="{blob(cx, top + 1, wt / 2 - 4 * s, 2.4 * s, seed + 1, 0.05, 12)}" fill="#E2BE7E"/>')
    o.append(f'<path d="M {F(cx - wt / 2 + 2)} {F(top + 3)} Q {F(cx)} {F(top - 34 * s)} {F(cx + wt / 2 - 2)} {F(top + 3)}" stroke="#1E5A66" stroke-width="{F(2.2 * s)}" fill="none"/>')
    return "".join(o)


def beach_ball(uid, cx, cy, r, seed):
    d = blob(cx, cy, r, r * 0.98, seed, 0.02, 16)
    o = [soft_shadow(uid + "-sh", cx - 4, cy + r - 1, r * 1.05, 3.6, 0.35), f'<path d="{d}" fill="#FFF8EE"/>']
    inner = []
    for k, (a0, col) in enumerate(((-150, "#E8604C"), (-30, "#F6C23E"), (90, "#3B7DC4"))):
        a1, a2 = math.radians(a0 - 22), math.radians(a0 + 22)
        inner.append(f'<path d="M {F(cx - 0.18 * r)} {F(cy - 0.3 * r)} L {F(cx + math.cos(a1) * r * 1.4)} {F(cy + math.sin(a1) * r * 1.4)} L {F(cx + math.cos(a2) * r * 1.4)} {F(cy + math.sin(a2) * r * 1.4)} Z" fill="{col}"/>')
    inner.append(f'<circle cx="{F(cx - 0.18 * r)}" cy="{F(cy - 0.3 * r)}" r="{F(r * 0.16)}" fill="#FFF8EE" stroke="#B8A88A" stroke-width="0.6"/>')
    o.append(clipped(uid + "-c", d, "".join(inner)))
    o.append(shade(uid + "-s", d, "#3A2418", -0.7, 0.7, k=r * 0.22, op=0.25))
    o.append(f'<path d="M {F(cx + 0.2 * r)} {F(cy - 0.7 * r)} Q {F(cx + 0.62 * r)} {F(cy - 0.6 * r)} {F(cx + 0.64 * r)} {F(cy - 0.2 * r)}" stroke="#FFFFFF" stroke-width="{F(r * 0.12)}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(ink(d, "#6A3E2A", 1.3, seed, 2, 0.6))
    return "".join(o)


def sailboat(x, y, s=1.0):
    return (f'<path d="M {F(x - 9 * s)} {F(y)} L {F(x + 9 * s)} {F(y)} L {F(x + 6 * s)} {F(y + 4 * s)} L {F(x - 7 * s)} {F(y + 4 * s)} Z" fill="#3A3A4A"/>'
            f'<path d="M {F(x)} {F(y)} L {F(x)} {F(y - 22 * s)}" stroke="#3A3A4A" stroke-width="{F(1 * s)}"/>'
            f'<path d="M {F(x + 1 * s)} {F(y - 21 * s)} Q {F(x + 9 * s)} {F(y - 10 * s)} {F(x + 8 * s)} {F(y - 1 * s)} L {F(x + 1 * s)} {F(y - 1 * s)} Z" fill="#FFFDF6"/>'
            f'<path d="M {F(x - 1 * s)} {F(y - 18 * s)} Q {F(x - 7 * s)} {F(y - 8 * s)} {F(x - 6 * s)} {F(y - 1 * s)} L {F(x - 1 * s)} {F(y - 1 * s)} Z" fill="#F2E8D6"/>')


def gull(x, y, s=1.0, col="#4A4A58"):
    return f'<path d="M {F(x - 7 * s)} {F(y)} q 4 -5 7 0 q 3 -5 7 0" stroke="{col}" stroke-width="{F(1.3 * s)}" fill="none" stroke-linecap="round"/>'


def summer_scene(u="sm"):
    o = []
    rnd = random.Random(27)
    # --- sky, sun, sea and the shore inside the vignette
    sky = (f'<defs>{lg(u + "-sky", [(0, "#4F9ACB"), (0.35, "#9CCBE6"), (0.55, "#F6E6C8"), (1, "#FBE4B8")])}</defs>'
           f'<rect width="380" height="330" fill="url(#{u}-sky)"/>')
    sky += glow(u + "-sun", 326, 58, 110, 90, "#FFF4CC", 1.0) + glow(u + "-sun2", 326, 58, 34, 30, "#FFFFFF", 0.95, 0.6)
    sky += cloud_puffs(u + "-c1", 110, 96, 80, 3, shade_col="#D9E6F0", n=5) + cloud_puffs(u + "-c2", 220, 60, 56, 4, shade_col="#D9E6F0", n=4)
    # sea: deep at the horizon, turquoise near the shore, sun glitter
    sky += (f'<defs>{lg(u + "-sea", [(0, "#2B6FA8"), (0.4, "#3C9EC2"), (0.8, "#6FD0D8"), (1, "#A8E6E2")])}</defs>'
            f'<rect x="0" y="162" width="380" height="76" fill="url(#{u}-sea)"/>')
    sky += dry_brush(51, (0, 166, 380, 232), ["#2B6FA8", "#8FDDE2", "#FFFFFF", "#3C9EC2"], 110, angle=-2, length=(8, 40), width=(0.4, 1.6), op=(0.2, 0.5), curve=0.05)
    sky += "".join(f'<ellipse cx="{F(rnd.uniform(220, 380))}" cy="{F(rnd.uniform(166, 215))}" rx="{F(rnd.uniform(1.5, 5))}" ry="0.7" fill="#FFF8DC" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(60))
    sky += sailboat(70, 178, 0.9) + sailboat(150, 170, 0.5)
    sky += gull(230, 118, 1.1) + gull(252, 108, 0.9) + gull(96, 140, 0.8)
    # breaking wave foam and the wet sand
    foam = smooth_closed([(0, 232), (40, 228), (90, 234), (150, 229), (210, 235), (270, 230), (330, 236), (380, 231), (380, 252), (0, 252)])
    sky += f'<path d="{foam}" fill="#EAF6F4"/>'
    sky += "".join(f'<path d="{blob(rnd.uniform(0, 380), rnd.uniform(230, 240), rnd.uniform(6, 16), rnd.uniform(2, 4), 100 + k, 0.2, 10)}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>' for k in range(24))
    sky += (f'<defs>{lg(u + "-wet", [(0, "#C9BFA0"), (1, "#E6D3A6")])}</defs>'
            f'<path d="{smooth_closed([(0, 246), (60, 242), (140, 248), (230, 243), (320, 249), (380, 244), (380, 268), (0, 268)])}" fill="url(#{u}-wet)"/>')
    sky += f'<path d="M 0 248 Q 190 240 380 246" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.7"/>'
    # dry sand with warm texture
    sky += (f'<defs>{lg(u + "-sand", [(0, "#F0DCAE"), (1, "#E2C488")])}</defs>'
            f'<path d="{smooth_closed([(0, 262), (90, 258), (200, 264), (300, 258), (380, 262), (380, 330), (0, 330)])}" fill="url(#{u}-sand)"/>')
    sky += dry_brush(52, (0, 262, 380, 330), ["#F8E8C0", "#D4B478", "#E8CE96", "#FFF4D8"], 120, angle=-3, length=(8, 30), width=(0.5, 1.8), op=(0.2, 0.5))
    sky += "".join(f'<circle cx="{F(rnd.uniform(0, 380))}" cy="{F(rnd.uniform(262, 330))}" r="{F(rnd.uniform(0.4, 1.0))}" fill="#A8824A" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>' for _ in range(70))
    sky += glow(u + "-warm", 300, 290, 110, 40, "#FFE4A0", 0.45)
    o.append(vignette(u + "-vg", sky, 198, 176, 200, 158, seed=19, edge=0.3, wobble=0.03, ground=244, gfade=0.2))
    # --- umbrella shadow on the sand, then the pole, the chair under the umbrella, the canopy
    o.append(soft_shadow(u + "-us", 186, 292, 96, 16, 0.3, col="#5A4A6A"))
    tilt = -12
    top = (250, 92)
    ux, uy = -math.sin(math.radians(tilt)), math.cos(math.radians(tilt))
    bot = (top[0] + ux * 214, top[1] + uy * 214)
    o.append(f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#6A4A2A" stroke-width="5.6" stroke-linecap="round"/>'
             f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#FFF3DC" stroke-width="3.6" stroke-linecap="round" stroke-dasharray="10 10"/>'
             f'<path d="M {F(top[0])} {F(top[1])} L {F(bot[0])} {F(bot[1])}" stroke="#E8604C" stroke-width="3.6" stroke-linecap="round" stroke-dasharray="10 10" stroke-dashoffset="10"/>'
             f'<path d="M {F(top[0] - 1.2)} {F(top[1])} L {F(bot[0] - 1.2)} {F(bot[1])}" stroke="#FFFFFF" stroke-width="0.9" stroke-linecap="round" opacity="0.6"/>')
    o.append(deck_chair(u + "-dc", 190, 302, 1.15))
    o.append(umbrella(u + "-um", top[0], top[1], 118, tilt, ("#E8604C", "#FBF1DA"), 10))
    # --- beach things in front
    o.append(pail(u + "-pl", 322, 304, 0.95))
    o.append(beach_ball(u + "-bb", 108, 300, 18, 6))
    for k, (x, y, s, c, r_) in enumerate(((150, 318, 1.1, "#F6C8B8", -20), (262, 322, 0.9, "#FFF3E6", 15), (60, 322, 0.8, "#F2D6A8", 30), (290, 312, 0.7, "#F6C8B8", -40))):
        o.append(seashell(x, y, s, c, 40 + k, r_))
    sp = star_pts(238, 318, 11, 0.45, -80)
    sd = smooth_closed(jitter(sp, 4, 0.6))
    o.append(gpaint(u + "-st", sd, bbox(sp), "#F8B070", "#F08A4B", "#B85A24", 4, direction=(-0.6, 0.8), angle=10, n=14, ink_w=1.0)
             + "".join(f'<circle cx="{F(238 + math.cos(math.radians(-80 + i * 72)) * 11 * t)}" cy="{F(318 + math.sin(math.radians(-80 + i * 72)) * 11 * t)}" r="0.9" fill="#FFD9A8"/>' for i in range(5) for t in (0.3, 0.55, 0.8)))
    # flip-flops by the chair
    for k, (x, y, r_) in enumerate(((56, 296, -14), (74, 300, -6))):
        d = blob(x, y, 7, 12, 60 + k, 0.05, 12, rot=r_)
        o.append(f'<path d="{d}" fill="#F6C23E" stroke="#8A6212" stroke-width="0.9"/><path d="M {F(x)} {F(y - 7)} l -4 7 M {F(x)} {F(y - 7)} l 4 7" stroke="#E8604C" stroke-width="1.6" fill="none" stroke-linecap="round" transform="rotate({r_} {F(x)} {F(y)})"/>')
    return "".join(o)


def summer_garland(u="sg"):
    """Nautical cloth bunting on a rope: coral, teal, sun-yellow and sea-blue flags with weave, plus shells and a starfish charm."""
    o = [rope(u, "#B9A078", "#E8D8B8", "#6A5A3A", w=3.0, twist=5)]
    flags = [("#F2644A", "stripes", "#FFF3DC"), ("#2FA6B0", "dots", "#FFF3DC"), ("#F6C23E", "sun", "#E8604C"), ("#3B7DC4", "zig", "#FFF3DC"), ("#F28AA0", "dots", "#FFFFFF")]
    xs = [32, 96, 160, 224, 288]
    for k, x in enumerate(xs):
        base, pat, pc = flags[k]
        w, h = 44, 42
        a, b = (x - w / 2, swag_y(x - w / 2) + 1), (x + w / 2, swag_y(x + w / 2) + 1)
        tip = (x + 1.5, (a[1] + b[1]) / 2 + h)
        d = (f"M {F(a[0])} {F(a[1])} Q {F(x)} {F((a[1] + b[1]) / 2 + 3)} {F(b[0])} {F(b[1])} "
             f"Q {F((b[0] + tip[0]) / 2 + 1.5)} {F((b[1] + tip[1]) / 2)} {F(tip[0])} {F(tip[1])} "
             f"Q {F((a[0] + tip[0]) / 2 - 1.5)} {F((a[1] + tip[1]) / 2)} {F(a[0])} {F(a[1])} Z")
        box = (a[0] - 2, min(a[1], b[1]) - 2, b[0] + 2, tip[1] + 2)
        o.append(gpaint(f"{u}-f{k}", d, box, lt(base, 0.15), base, dk(base, 0.2), 90 + k, direction=(0.6, 0.8), angle=-90, n=22, length=(6, 18), width=(0.5, 1.6), ink_col=dk(base, 0.5), ink_w=1.2))
        inner = ""
        if pat == "stripes":
            inner = f'<g stroke="{pc}" stroke-width="3.4" opacity="0.9">' + "".join(f'<path d="M {F(a[0] - 4)} {F(a[1] + 8 + i * 9)} L {F(b[0] + 4)} {F(b[1] + 8 + i * 9)}"/>' for i in range(4)) + "</g>"
        elif pat == "dots":
            inner = f'<g fill="{pc}" opacity="0.9">' + "".join(f'<circle cx="{F(x + (i - 2) * 9 + (j % 2) * 4.5)}" cy="{F((a[1] + b[1]) / 2 + 6 + j * 8)}" r="2"/>' for i in range(5) for j in range(4)) + "</g>"
        elif pat == "zig":
            inner = f'<path d="{"M " + " L ".join(f"{F(a[0] - 4 + i * 5)} {F((a[1] + b[1]) / 2 + 14 + (i % 2) * 5)}" for i in range(11))}" stroke="{pc}" stroke-width="2.6" fill="none"/>'
        else:
            sx, sy = x, (a[1] + b[1]) / 2 + 14
            inner = f'<circle cx="{F(sx)}" cy="{F(sy)}" r="5" fill="{pc}"/>' + "".join(f'<path d="M {F(sx + math.cos(math.radians(t)) * 7)} {F(sy + math.sin(math.radians(t)) * 7)} l {F(math.cos(math.radians(t)) * 3)} {F(math.sin(math.radians(t)) * 3)}" stroke="{pc}" stroke-width="1.6" stroke-linecap="round"/>' for t in range(0, 360, 45))
        # cloth weave
        weave = "".join(f'<path d="M {F(a[0] - 4)} {F(min(a[1], b[1]) + i * 3)} l 60 0" stroke="#000" stroke-width="0.5" opacity="0.06"/>' for i in range(16))
        weave += "".join(f'<path d="M {F(a[0] + i * 3)} {F(min(a[1], b[1]) - 2)} l 0 50" stroke="#FFF" stroke-width="0.5" opacity="0.12"/>' for i in range(16))
        o.append(clipped(f"{u}-c{k}", d, inner + weave))
        o.append(f'<path d="{poly([(a[0] + 6, a[1] + 4), (b[0] - 6, b[1] + 4), (tip[0], tip[1] - 9)])}" fill="none" stroke="#FFFFFF" stroke-width="0.9" stroke-dasharray="2.4 2" opacity="0.7" stroke-linejoin="round"/>')
        o.append(f'<path d="M {F(a[0])} {F(a[1])} Q {F(x)} {F((a[1] + b[1]) / 2 + 3)} {F(b[0])} {F(b[1])}" stroke="#6A5A3A" stroke-width="1.6" fill="none" opacity="0.6"/>')
    for k, x in enumerate((64, 192)):
        y = swag_y(x) + 1
        o.append(f'<path d="M {F(x)} {F(y)} l 0 9" stroke="#8A7A5A" stroke-width="0.9"/>' + seashell(x, y + 16, 1.1, "#F6C8B8" if k else "#FFF3E6", 20 + k, 180))
    x, y = 256, swag_y(256) + 1
    o.append(f'<path d="M {F(x)} {F(y)} l 0 8" stroke="#8A7A5A" stroke-width="0.9"/>')
    sp = star_pts(x, y + 17, 9, 0.45, -90)
    o.append(gpaint(u + "-sf", smooth_closed(jitter(sp, 3, 0.5)), bbox(sp), "#F8B070", "#F08A4B", "#B85A24", 3, direction=(-0.6, 0.8), angle=10, n=10, ink_w=0.9))
    return "".join(o)


# ================================================================ JULY 4
RED = ("#C8323A", "#E8605E", "#8E1A20", "#5E0C12")
BLUE = ("#2E4A8A", "#5A78B8", "#1E3060", "#121E40")
CREAM = ("#FBF4E8", "#FFFFFF", "#D9CDB8", "#8A7A62")


def fan_bunting(u, cx, top, R, seed):
    """Pleated half-rosette hanging below (cx, top): red, cream and blue rings with a star in the blue centre."""
    o = []
    rings = [(R, RED), (R * 0.82, CREAM), (R * 0.64, RED), (R * 0.46, CREAM), (R * 0.3, BLUE)]
    n_pleat = 9
    for k, (r, cols) in enumerate(rings):
        pts = [(cx - r, top)]
        for i in range(n_pleat * 2 + 1):
            a = math.pi - math.pi * i / (n_pleat * 2)
            rr = r * (1.0 if i % 2 else 0.94)
            pts.append((cx + math.cos(a) * rr, top + math.sin(a) * rr * 0.9))
        pts.append((cx + r, top))
        d = "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in pts[:1]) + " " + smooth_open(pts[1:-1]).replace("M", "L", 1) + f" L {F(cx + r)} {F(top)} Z"
        o.append(paint(f"{u}-{k}", d, (cx - r, top - 1, cx + r, top + r), cols[0], seed + k, tints=[cols[1], cols[2]], angle=90, n=int(r * 0.9),
                       ink_col=cols[3], ink_w=1.0, length=(r * 0.15, r * 0.5), width=(0.3, 1.0), op=(0.2, 0.5)))
    pl = []
    for i in range(1, n_pleat * 2, 2):
        a = math.pi - math.pi * i / (n_pleat * 2)
        pl.append(f"M {F(cx + math.cos(a) * R * 0.3)} {F(top + math.sin(a) * R * 0.27)} L {F(cx + math.cos(a) * R * 0.97)} {F(top + math.sin(a) * R * 0.87)}")
    o.append(f'<path d="{" ".join(pl)}" stroke="#5E2A22" stroke-width="0.9" opacity="0.45"/>')
    o.append(f'<path d="{" ".join(pl)}" stroke="#FFFFFF" stroke-width="0.7" opacity="0.4" transform="translate(1.2 0)"/>')
    o.append(f'<path d="{poly(star_pts(cx, top + R * 0.14, R * 0.12, 0.45))}" fill="#FBF4E8"/>')
    o.append(f'<path d="M {F(cx - R - 1)} {F(top)} L {F(cx + R + 1)} {F(top)}" stroke="{BLUE[3]}" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(o)


def swag_drape(u, x0, x1, top, sag, depth, seed, weave=True):
    """Draped bunting between two hanging points: blue band with stars over red / cream / red, with gathers and cloth weave."""
    def curve(t, extra):
        x = x0 + (x1 - x0) * t
        y = top + 4 * t * (1 - t) * (sag + extra)
        return x, y
    bands = [(0, 0.26, BLUE), (0.26, 0.5, RED), (0.5, 0.74, CREAM), (0.74, 1.0, RED)]
    o = []
    whole = smooth_open([curve(i / 16, 0) for i in range(17)]) + " " + smooth_open([curve(i / 16, depth) for i in range(17)][::-1]).replace("M", "L", 1) + " Z"
    for k, (f0, f1, cols) in enumerate(bands):
        a = [curve(i / 16, depth * f0) for i in range(17)]
        b = [curve(i / 16, depth * f1) for i in range(17)][::-1]
        d = smooth_open(a) + " " + smooth_open(b).replace("M", "L", 1) + " Z"
        box = (x0, top - 2, x1, top + sag + depth + 4)
        o.append(paint(f"{u}-{k}", d, box, cols[0], seed + k, tints=[cols[1], cols[2]], angle=0, n=26, ink_w=0, length=(8, 22), width=(0.4, 1.2), op=(0.2, 0.5)))
    if weave:
        o.append(clipped(f"{u}-wv", whole, "".join(f'<path d="M {F(x0)} {F(top + i * 3)} L {F(x1)} {F(top + i * 3)}" stroke="#000" stroke-width="0.5" opacity="0.07"/>' for i in range(int((sag + depth) / 3) + 2))))
    outline_top = smooth_open([curve(i / 16, 0) for i in range(17)])
    outline_bot = smooth_open([curve(i / 16, depth) for i in range(17)])
    o.append(ink(outline_bot, RED[3], 1.2, seed, 1, 0.7) + ink(outline_top, BLUE[3], 1.0, seed, 1, 0.6))
    g = []
    for sgn, xa in ((1, x0), (-1, x1)):
        for j in range(4):
            t0 = 0.02 + j * 0.035
            t = t0 if sgn > 0 else 1 - t0
            p0 = curve(t, 0)
            p1 = curve(t + sgn * 0.08, depth)
            g.append(f"M {F(p0[0])} {F(p0[1])} Q {F((p0[0] + p1[0]) / 2 + sgn * 2)} {F((p0[1] + p1[1]) / 2)} {F(p1[0])} {F(p1[1])}")
    o.append(f'<path d="{" ".join(g)}" stroke="#3A1A14" stroke-width="0.8" fill="none" opacity="0.4"/>')
    for i in range(1, 6):
        t = i / 6
        sx, sy = curve(t, depth * 0.13)
        o.append(f'<path d="{poly(star_pts(sx, sy, 2.6, 0.45))}" fill="#FBF4E8"/>')
    return "".join(o)


def firework_burst_lite(uid, cx, cy, r, col, seed, n=18):
    return firework_burst(uid, cx, cy, r, col, seed, n=n, droop=0.2, glow_op=0.5)


def pie_slice(u, x, y, s=1.0, seed=5):
    """Wedge of lattice-top cherry pie on a plate, seen from the front: the cut face shows the filling."""
    def p(px, py):
        return (x + px * s, y + py * s)
    o = [soft_shadow(u + "-sh", *p(2, 8), 40 * s, 6 * s, 0.35)]
    # plate
    o.append(f'<ellipse cx="{F(p(0, 4)[0])}" cy="{F(p(0, 4)[1])}" rx="{F(40 * s)}" ry="{F(11 * s)}" fill="#F4F1EA" stroke="#B8B0A4" stroke-width="1"/>'
             f'<ellipse cx="{F(p(0, 3)[0])}" cy="{F(p(0, 3)[1])}" rx="{F(31 * s)}" ry="{F(7.5 * s)}" fill="none" stroke="#3B6FB0" stroke-width="{F(1.2 * s)}" opacity="0.7"/>')
    # cut face (front): crust edges top and bottom, cherry filling between
    face = smooth_closed(jitter([p(-24, -6), p(22, -8), p(22, 4), p(-24, 6)], seed, 0.5))
    o.append(f'<path d="{face}" fill="#A61E2A"/>')
    rnd = random.Random(seed)
    o.append(clipped(u + "-fc", face, "".join(f'<path d="{blob(*p(rnd.uniform(-22, 20), rnd.uniform(-5, 4)), rnd.uniform(3, 5) * s, rnd.uniform(2.5, 4) * s, seed + k, 0.1, 8)}" fill="{rnd.choice(["#C8323A", "#7E1420", "#E04A50"])}" opacity="0.9"/>' for k in range(10))
                     + f'<path d="M {F(p(-24, -5)[0])} {F(p(-24, -5)[1])} L {F(p(22, -7)[0])} {F(p(22, -7)[1])}" stroke="#F2B8A0" stroke-width="{F(2 * s)}" opacity="0.5"/>'))
    o.append(f'<path d="{smooth_closed(jitter([p(-24, 2), p(22, 0), p(22, 6), p(-24, 8)], seed + 1, 0.4))}" fill="#D9A25A" stroke="#8A5A22" stroke-width="0.9"/>')
    # top: wedge receding back, lattice strips over the filling
    topd = smooth_closed(jitter([p(-24, -6), p(22, -8), p(2, -30), p(-8, -30)], seed + 2, 0.6))
    o.append(f'<path d="{topd}" fill="#B8262E"/>')
    lat = "".join(f'<path d="M {F(p(-26 + i * 8, -4)[0])} {F(p(-26 + i * 8, -4)[1])} L {F(p(-14 + i * 4, -32)[0])} {F(p(-14 + i * 4, -32)[1])}" stroke="#E2B46A" stroke-width="{F(3.4 * s)}"/>' for i in range(7))
    lat += "".join(f'<path d="M {F(p(-26, -8 - j * 7)[0])} {F(p(-26, -8 - j * 7)[1])} L {F(p(24, -9 - j * 7)[0])} {F(p(24, -9 - j * 7)[1])}" stroke="#D9A25A" stroke-width="{F(3.2 * s)}"/>' for j in range(4))
    o.append(clipped(u + "-lc", topd, lat + "".join(f'<path d="M {F(p(-26 + i * 8, -4)[0])} {F(p(-26 + i * 8, -4)[1])} L {F(p(-14 + i * 4, -32)[0])} {F(p(-14 + i * 4, -32)[1])}" stroke="#F6D898" stroke-width="{F(1 * s)}" opacity="0.7" transform="translate(-0.8 0)"/>' for i in range(7))))
    # crimped crust rim along the back edge, the front edge of the top
    o.append(f'<path d="M {F(p(-25, -6)[0])} {F(p(-25, -6)[1])} L {F(p(23, -8)[0])} {F(p(23, -8)[1])}" stroke="#C98A3A" stroke-width="{F(3 * s)}" stroke-linecap="round"/>')
    crimp = "".join(f'<circle cx="{F(p(-8 + k * 2.4, -30 - (k % 2) * 0.6)[0])}" cy="{F(p(-8 + k * 2.4, -30 - (k % 2) * 0.6)[1])}" r="{F(2.2 * s)}" fill="#E2B46A" stroke="#8A5A22" stroke-width="0.6"/>' for k in range(5))
    o.append(crimp)
    o.append(ink(face, "#5E0C12", 0.9, seed, 1, 0.6))
    # a fork beside it
    o.append(f'<path d="M {F(p(30, 6)[0])} {F(p(30, 6)[1])} L {F(p(46, -10)[0])} {F(p(46, -10)[1])}" stroke="#9AA4B4" stroke-width="{F(2.4 * s)}" stroke-linecap="round"/>'
             f'<path d="M {F(p(26, 8)[0])} {F(p(26, 8)[1])} l 2 -6 l 2 6 M {F(p(29, 10)[0])} {F(p(29, 10)[1])} l 2 -6" stroke="#9AA4B4" stroke-width="{F(1.4 * s)}" stroke-linecap="round" fill="none"/>')
    return "".join(o)


def mason_jar(u, cx, base, s=1.0, seed=9):
    """Mason jar of lemonade with ice, a striped paper straw and a lemon wheel on the rim."""
    def p(px, py):
        return (cx + px * s, base + py * s)
    o = [soft_shadow(u + "-sh", *p(2, 1), 20 * s, 4 * s, 0.35)]
    body = smooth_closed([p(-16, 0), p(-17, -12), p(-16, -40), p(-13, -46), p(13, -46), p(16, -40), p(17, -12), p(16, 0)])
    o.append(f'<defs>{lg(u + "-gl", [(0, "#FFFFFF", 0.5), (0.5, "#DCE6F0", 0.25), (1, "#FFFFFF", 0.4)], 0, 0, 1, 0)}</defs><path d="{body}" fill="url(#{u}-gl)"/>')
    liq = (f'<rect x="{F(p(-18, -36)[0])}" y="{F(p(-18, -36)[1])}" width="{F(36 * s)}" height="{F(40 * s)}" fill="#F7DC6A"/>'
           f'<rect x="{F(p(6, -36)[0])}" y="{F(p(6, -36)[1])}" width="{F(12 * s)}" height="{F(40 * s)}" fill="#D9B23A" opacity="0.5"/>'
           f'<ellipse cx="{F(p(0, -36)[0])}" cy="{F(p(0, -36)[1])}" rx="{F(17 * s)}" ry="{F(2.6 * s)}" fill="#FFF3B0"/>')
    for k, (ix, iy) in enumerate(((-8, -28), (4, -22), (-2, -12), (8, -8))):
        liq += f'<path d="{smooth_closed(jitter([p(ix - 5, iy - 4), p(ix + 5, iy - 5), p(ix + 6, iy + 4), p(ix - 4, iy + 5)], seed + k, 0.5))}" fill="#FFFFFF" opacity="0.55" stroke="#C9DDE8" stroke-width="0.6"/>'
    o.append(clipped(u + "-c", body, liq))
    # threads at the neck and the rim
    for k in range(3):
        yy = -44 + k * 2.6
        o.append(f'<path d="M {F(p(-15, yy)[0])} {F(p(-15, yy)[1])} Q {F(p(0, yy + 1.2)[0])} {F(p(0, yy + 1.2)[1])} {F(p(15, yy)[0])} {F(p(15, yy)[1])}" stroke="#8E9CB2" stroke-width="{F(0.9 * s)}" fill="none" opacity="0.7"/>')
    o.append(ink(body, "#8E9CB2", 1.2 * s, seed, 2, 0.8))
    o.append(f'<path d="M {F(p(-12, -40)[0])} {F(p(-12, -40)[1])} Q {F(p(-14, -20)[0])} {F(p(-14, -20)[1])} {F(p(-12, -4)[0])} {F(p(-12, -4)[1])}" stroke="#FFFFFF" stroke-width="{F(2.2 * s)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append(f'<ellipse cx="{F(p(0, -46)[0])}" cy="{F(p(0, -46)[1])}" rx="{F(13 * s)}" ry="{F(3 * s)}" fill="none" stroke="#F4F8FC" stroke-width="{F(1.2 * s)}"/>')
    # straw and lemon wheel
    sd = f"M {F(p(6, -30)[0])} {F(p(6, -30)[1])} L {F(p(14, -70)[0])} {F(p(14, -70)[1])}"
    o.append(f'<path d="{sd}" stroke="#F4F1EA" stroke-width="{F(3.6 * s)}" stroke-linecap="round"/><path d="{sd}" stroke="#C8323A" stroke-width="{F(3.6 * s)}" stroke-linecap="round" stroke-dasharray="3 3"/>')
    lx, ly = p(-13, -48)
    o.append(f'<circle cx="{F(lx)}" cy="{F(ly)}" r="{F(7 * s)}" fill="#F7E27A" stroke="#D9A82A" stroke-width="1.2"/><circle cx="{F(lx)}" cy="{F(ly)}" r="{F(5.2 * s)}" fill="#FFF3B0"/>'
             + "".join(f'<path d="M {F(lx)} {F(ly)} l {F(math.cos(math.radians(a)) * 5 * s)} {F(math.sin(math.radians(a)) * 5 * s)}" stroke="#F0C840" stroke-width="0.8"/>' for a in range(0, 360, 45)))
    return "".join(o)


def little_flag(uid, x, base, h, lean, seed, fw=34, fh=22):
    tx, ty = x + lean, base - h
    o = [f'<path d="M {F(x)} {F(base)} L {F(tx)} {F(ty)}" stroke="#6A4A2A" stroke-width="2.4" stroke-linecap="round"/>',
         f'<circle cx="{F(tx)}" cy="{F(ty - 1)}" r="2.2" fill="#E2B04A" stroke="#7A5212" stroke-width="0.6"/>']
    def P(u_, v):
        return (tx + 1 + u_ * fw, ty + 1 + v * fh + math.sin(u_ * math.pi * 1.6) * 2.4)
    outline = [P(i / 8, 0) for i in range(9)] + [P(1 - i / 8, 1) for i in range(9)]
    d = poly(outline)
    o.append(f'<path d="{d}" fill="#FBF4E8"/>')
    stripes = []
    for j in range(7):
        if j % 2 == 0:
            v0, v1 = j / 7, (j + 1) / 7
            stripes.append(poly([P(i / 8, v0) for i in range(9)] + [P(1 - i / 8, v1) for i in range(9)]))
    o.append(f'<path d="{" ".join(stripes)}" fill="{RED[0]}"/>')
    o.append(f'<path d="{poly([P(0, 0), P(0.14, 0), P(0.28, 0), P(0.42, 0), P(0.42, 0.56), P(0.28, 0.56), P(0.14, 0.56), P(0, 0.56)])}" fill="{BLUE[0]}"/>')
    o.append("".join(f'<circle cx="{F(P(u_, v)[0])}" cy="{F(P(u_, v)[1])}" r="0.9" fill="#FBF4E8"/>' for u_ in (0.08, 0.2, 0.32) for v in (0.12, 0.28, 0.44)))
    o.append(clipped(uid + "-sc", d, "".join(f'<path d="M {F(P(u_, 0)[0])} {F(P(u_, 0)[1] - 4)} L {F(P(u_, 1)[0])} {F(P(u_, 1)[1] + 4)}" stroke="#3A2418" stroke-width="5" opacity="{0.08 if k % 2 else 0.0}"/>' for k, u_ in enumerate((0.3, 0.62, 0.9)))))
    o.append(ink(d, "#5E2A22", 1.0, seed, 1, 0.6))
    return "".join(o)


def july4_scene(u="j4"):
    o = []
    rnd = random.Random(29)
    # --- dusk sky over a lake, far pines, fireworks and their reflections
    sky = (f'<defs>{lg(u + "-sky", [(0, "#1E2A5A"), (0.4, "#4A3F7A"), (0.62, "#C06A6E"), (0.75, "#F2B07A"), (1, "#F8D8A0")])}</defs>'
           f'<rect width="380" height="330" fill="url(#{u}-sky)"/>')
    sky += "".join(f'<circle cx="{F(rnd.uniform(0, 380))}" cy="{F(rnd.uniform(0, 110))}" r="{F(rnd.uniform(0.4, 1.0))}" fill="#FFF6D8" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>' for _ in range(40))
    sky += firework_burst(u + "-fw1", 120, 72, 54, "#E8404A", 1, n=24)
    sky += firework_burst(u + "-fw2", 262, 54, 44, "#F2C04E", 2, n=22)
    sky += firework_burst(u + "-fw3", 330, 118, 30, "#6A8EE0", 3, n=16, glow_op=0.45)
    sky += firework_burst(u + "-fw4", 196, 120, 22, "#F8F0F8", 4, n=12, glow_op=0.35)
    # far shore: pine silhouettes and a few cabin lights
    pts = [(0, 196)]
    x = 0
    while x < 380:
        h = rnd.uniform(8, 22)
        w = rnd.uniform(5, 9)
        pts += [(x + w * 0.5, 196 - h), (x + w, 196)]
        x += w
    sky += f'<path d="{poly(pts + [(380, 196), (380, 206), (0, 206)])}" fill="#1E1E3A"/>'
    sky += f'<path d="M 0 200 L 380 200 L 380 206 L 0 206 Z" fill="#141430"/>'
    sky += "".join(f'<rect x="{F(x)}" y="192" width="2.2" height="2.2" fill="#FFD27A"/>' for x in (46, 52, 288, 294, 300))
    # lake with reflections
    sky += (f'<defs>{lg(u + "-lk", [(0, "#2A2A5A"), (0.3, "#5A4A80"), (0.6, "#B07A80"), (1, "#3A3A6A")])}</defs>'
            f'<rect x="0" y="206" width="380" height="60" fill="url(#{u}-lk)"/>')
    for cx_, col, w in ((120, "#E8404A", 26), (262, "#F2C04E", 22), (330, "#6A8EE0", 14), (196, "#F8F0F8", 8)):
        for k in range(10):
            yy = 208 + k * 5.4
            sky += f'<path d="M {F(cx_ - w * (1 - k * 0.06) + rnd.uniform(-3, 3))} {F(yy)} l {F(w * 2 * (1 - k * 0.06))} 0" stroke="{col}" stroke-width="{F(rnd.uniform(1.2, 2.4))}" opacity="{0.55 - k * 0.045:.2f}" stroke-linecap="round"/>'
    sky += "".join(f'<path d="M {F(rnd.uniform(0, 380))} {F(rnd.uniform(208, 262))} l {F(rnd.uniform(6, 20))} 0" stroke="#F8D8A0" stroke-width="1" opacity="{rnd.uniform(0.15, 0.45):.2f}" stroke-linecap="round"/>' for _ in range(40))
    sky += "".join(f'<rect x="{F(x)}" y="207" width="2.2" height="6" fill="#FFD27A" opacity="0.5"/>' for x in (46, 52, 288, 294, 300))
    # porch floor/rail region is drawn solid below
    o.append(vignette(u + "-vg", sky, 198, 150, 200, 150, seed=23, edge=0.3, wobble=0.03, ground=250, gfade=0.18))
    # --- porch rail: white-painted wood, lit warm from the porch light at the right
    rail = []
    rail.append(f'<defs>{lg(u + "-rw", [(0, "#F6F0E4"), (1, "#D9CFBF")], 0, 0, 0, 1)}{lg(u + "-rb", [(0, "#E8E0D2"), (1, "#C9BFAE")], 1, 0, 0, 0)}</defs>')
    # balusters
    for k in range(13):
        bx = 14 + k * 30
        rail.append(f'<rect x="{F(bx - 4)}" y="266" width="8" height="64" fill="url(#{u}-rb)"/><rect x="{F(bx - 4)}" y="266" width="2" height="64" fill="#FFFFFF" opacity="0.7"/><rect x="{F(bx + 2)}" y="266" width="2" height="64" fill="#A89E8E" opacity="0.6"/>')
    rail.append(f'<rect x="0" y="312" width="380" height="9" fill="#E2D9CA"/><rect x="0" y="312" width="380" height="2" fill="#FFFFFF" opacity="0.7"/>')
    # top rail with a lit top face
    rail.append(f'<path d="M 0 262 L 380 262 L 380 274 L 0 274 Z" fill="url(#{u}-rw)"/><path d="M 0 254 L 380 254 L 380 262 L 0 262 Z" fill="#FFFDF8"/>'
                f'<path d="M 0 262 L 380 262" stroke="#B8AE9E" stroke-width="1"/><path d="M 0 274 L 380 274" stroke="#8A8072" stroke-width="1.2"/>')
    rail.append(dry_brush(71, (0, 254, 380, 276), ["#FFFFFF", "#E2D9CA", "#CFC5B4"], 60, angle=0, length=(10, 40), width=(0.5, 1.4), op=(0.2, 0.45)))
    rail.append(glow(u + "-pl", 340, 268, 90, 40, "#FFD58A", 0.45))
    o.append(hmask(u + "-rm", "".join(rail), 0, 380, 250, 330, fade=0.16))
    # bunting on the rail front
    for x0, x1 in ((18, 190), (190, 362)):
        o.append(swag_drape(f"{u}-d{x0}", x0, x1, 276, 12, 24, 10 + x0))
    for x in (18, 190, 362):
        o.append(fan_bunting(f"{u}-f{x}", x, 274, 24, 30 + x))
    # --- on the rail: pie, lemonade, a little flag in the pie plate's jar? the flag stands in a planter at the left
    o.append(f'<path d="{blob(70, 254, 18, 6, 41, 0.04, 12)}" fill="#8A5A3A"/><path d="{blob(70, 252, 16, 4, 42, 0.06, 12)}" fill="#5A3A24"/>')
    o.append(little_flag(u + "-fl1", 62, 252, 60, -6, 1, fw=34, fh=22) + little_flag(u + "-fl2", 76, 252, 50, 8, 2, fw=28, fh=18))
    for k, (x, y, c) in enumerate(((56, 250, "#D8344A"), (84, 248, "#F6F0E4"), (70, 246, "#2E4A8A"))):
        o.append("".join(f'<ellipse cx="{F(x + math.cos(math.radians(a)) * 3)}" cy="{F(y + math.sin(math.radians(a)) * 3)}" rx="2.4" ry="1.3" fill="{c}" transform="rotate({a} {F(x + math.cos(math.radians(a)) * 3)} {F(y + math.sin(math.radians(a)) * 3)})"/>' for a in range(0, 360, 60)) + f'<circle cx="{x}" cy="{y}" r="1.4" fill="#F2C14E"/>')
    o.append(pie_slice(u + "-pie", 214, 246, 1.05))
    o.append(mason_jar(u + "-jar", 318, 254, 1.0))
    # fireflies
    for k in range(9):
        fx, fy = rnd.uniform(40, 360), rnd.uniform(130, 300)
        o.append(glow(f"{u}-ff{k}", fx, fy, 7, 7, "#F2E27A", 0.7, 0.4) + f'<circle cx="{F(fx)}" cy="{F(fy)}" r="1.3" fill="#FFF6B0"/>')
    o.append(sparkle(296, 150, 4, "#FFFFFF") + sparkle(60, 150, 3.4, "#FFF3C4"))
    return "".join(o)


def july4_garland(u="j4g"):
    o = []
    for x0, x1 in ((0, 160), (160, 320)):
        o.append(swag_drape(f"{u}-d{x0}", x0, x1, 6, 10, 22, 10 + x0))
    for x, y, r, cols in ((80, 50, 7.5, RED), (240, 50, 7.5, BLUE)):
        o.append(f'<path d="M {x} 38 L {x} {y - r}" stroke="#8A7A62" stroke-width="0.8"/>')
        o.append(painted_star(f"{u}-s{x}", x, y, r, cols, x))
    for x in (0, 160, 320):
        o.append(fan_bunting(f"{u}-f{x}", x, 4, 28, 30 + x))
    for x, y in ((40, 46), (120, 44), (200, 46), (280, 44)):
        o.append(glow(f"{u}-g{x}", x, y, 8, 8, "#FFD36A", 0.6, 0.4) + sparkle(x, y, 3, "#FBF4E8", "#8A7A62"))
    return "".join(o)


def particles_stars():
    return [("star1", painted_star("ps1", 20, 21, 16, RED, 1, rot_=-84)),
            ("star2", painted_star("ps2", 20, 21, 15, BLUE, 2, rot_=-96) + rim("ps2r", poly(jitter(star_pts(20, 21, 15, 0.5, -96), 2, 0.45)), "#C8D6F6", -1, -1, k=1.2, op=0.9))]
