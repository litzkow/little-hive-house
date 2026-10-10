"""Ink Cities, fine edition.

The twelve Ink Cities redrawn as rich pen-and-ink plates, like the pages of an architect's sketchbook or an
engraved travel print: warm black ink on cream paper, bold contours over fine detail lines, hatching,
cross-hatching and stippling for shade, ink ripples on water, scribbled foliage, and small storytelling
details (boats, cars, people, lamps, birds). Each plate has its own viewpoint and layout. One restrained accent
is allowed per plate: a faded vermilion wash on a single story element (a flag, an awning, a bus, a cable car).

Typographic system shared by the whole series (and by ink_cities_new.py):
    city name   DM Serif Display, ink, auto-fit (NAME_MAX px max)
    coordinates DM Mono 500, ink, COORD_SIZE px, letter-spacing COORD_LS

Run from tools/designs:  python3 ink_cities_fine.py [slug ...]
"""
import math
import random
import sys

from common import DMS, MONO, esc, fit_size, measure, save
from gouache import grain, paper, smooth_closed, smooth_open, wash, strokes
from kitchen_ink import E, cr, clipped, hatch, nib, poly, stipple

COL = "ink-cities"
INK = "#1E1A16"
PAPER = "#F3EADA"
FLECK = "#6E5A44"
RED = ("#EBB2A0", "#CF6B55", "#A9442F")     # faded vermilion wash: the single accent
GREY = "#1E1A16"                              # ink wash (used at low opacity)
NAME_MAX = 70
COORD_SIZE = 18
COORD_LS = 3

CITIES = {
    "atlanta": ("Atlanta", "33.7490° N · 84.3880° W"),
    "new-york": ("New York", "40.7128° N · 74.0060° W"),
    "chicago": ("Chicago", "41.8781° N · 87.6298° W"),
    "miami": ("Miami", "25.7617° N · 80.1918° W"),
    "nashville": ("Nashville", "36.1627° N · 86.7816° W"),
    "boston": ("Boston", "42.3601° N · 71.0589° W"),
    "seattle": ("Seattle", "47.6062° N · 122.3321° W"),
    "san-francisco": ("San Francisco", "37.7749° N · 122.4194° W"),
    "paris": ("Paris", "48.8566° N · 2.3522° E"),
    "london": ("London", "51.5072° N · 0.1276° W"),
    "rome": ("Rome", "41.9028° N · 12.4964° E"),
    "rio": ("Rio de Janeiro", "22.9068° S · 43.1729° W"),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Ids:
    def __init__(self, slug):
        self.slug, self.n = slug, 0

    def __call__(self, tag="u"):
        self.n += 1
        return f"icf-{self.slug}-{tag}{self.n}"

    def seed(self):
        self.n += 1
        return self.n * 7 + 3


# ================================================================ geometry
def f1(v):
    return f"{v:.1f}"


def lerp(a, b, t):
    return a + (b - a) * t


def pt(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def bbox(pts, pad=4):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def homog(q):
    """Projective map from the unit square (u right, v down) onto quad q = [TL, TR, BR, BL]."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    dx1, dx2, dx3 = x1 - x2, x3 - x2, x0 - x1 + x2 - x3
    dy1, dy2, dy3 = y1 - y2, y3 - y2, y0 - y1 + y2 - y3
    if abs(dx3) < 1e-9 and abs(dy3) < 1e-9:
        g = h = 0.0
    else:
        den = dx1 * dy2 - dx2 * dy1
        g = (dx3 * dy2 - dx2 * dy3) / den
        h = (dx1 * dy3 - dx3 * dy1) / den
    a, b, c = x1 - x0 + g * x1, x3 - x0 + h * x3, x0
    d, e, f = y1 - y0 + g * y1, y3 - y0 + h * y3, y0

    def m(u, v):
        w = g * u + h * v + 1
        return ((a * u + b * v + c) / w, (d * u + e * v + f) / w)
    return m


def quad_sub(q, u0, v0, u1, v1):
    m = homog(q)
    return [m(u0, v0), m(u1, v0), m(u1, v1), m(u0, v1)]


# ================================================================ pen work
def P(d, w=1.5, color=INK, op=1.0, extra=""):
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round"{o}{extra}/>')


def F(pts_or_d, color=PAPER, op=1.0, smooth=False):
    d = pts_or_d if isinstance(pts_or_d, str) else (smooth_closed(pts_or_d) if smooth else poly(pts_or_d))
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    return f'<path d="{d}" fill="{color}"{o}/>'


def wd(pts, seed=0, wob=0.6, closed=False):
    """Path data for a hand-drawn polyline: each segment bows very slightly."""
    rnd = random.Random(seed)
    Pp = list(pts) + ([pts[0]] if closed else [])
    d = [f"M {f1(Pp[0][0])} {f1(Pp[0][1])}"]
    for (ax, ay), (bx, by) in zip(Pp, Pp[1:]):
        L = math.hypot(bx - ax, by - ay) or 1
        bow = rnd.uniform(-wob, wob) * min(1.0, L / 50)
        mx, my = (ax + bx) / 2 - (by - ay) / L * bow, (ay + by) / 2 + (bx - ax) / L * bow
        d.append(f"Q {f1(mx)} {f1(my)} {f1(bx)} {f1(by)}")
    return " ".join(d)


def pen(pts, w=1.5, seed=0, wob=0.6, closed=False, op=1.0, color=INK, smooth=False):
    if smooth:
        d = smooth_closed(pts) if closed else smooth_open(pts)
    else:
        d = wd(pts, seed, wob, closed)
    return P(d, w, color, op)


def seg(x0, y0, x1, y1, w=1.4, seed=0, wob=0.5, over=0.0, op=1.0, color=INK):
    if over:
        L = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        x0, y0, x1, y1 = x0 - ux * over, y0 - uy * over, x1 + ux * over, y1 + uy * over
    return pen([(x0, y0), (x1, y1)], w, seed, wob, op=op, color=color)


def segs(lines, w=1.2, seed=0, wob=0.4, op=1.0, color=INK):
    """Many separate short strokes in one path element."""
    rnd = random.Random(seed)
    d = []
    for ln in lines:
        (ax, ay), (bx, by) = ln[0], ln[1]
        L = math.hypot(bx - ax, by - ay) or 1
        bow = rnd.uniform(-wob, wob) * min(1.0, L / 50)
        mx, my = (ax + bx) / 2 - (by - ay) / L * bow, (ay + by) / 2 + (bx - ax) / L * bow
        d.append(f"M {f1(ax)} {f1(ay)} Q {f1(mx)} {f1(my)} {f1(bx)} {f1(by)}")
    return P(" ".join(d), w, color, op) if d else ""


def sketch(pts, w=1.8, seed=0, over=1.6, closed=True, wob=0.5, op=1.0, color=INK):
    """Architect's outline: every edge drawn as its own stroke, overshooting the corners a touch."""
    rnd = random.Random(seed)
    Pp = list(pts) + ([pts[0]] if closed else [])
    lines = []
    for a, b in zip(Pp, Pp[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        o0, o1 = over * rnd.uniform(0.2, 1.2), over * rnd.uniform(0.2, 1.2)
        lines.append(((a[0] - ux * o0, a[1] - uy * o0), (b[0] + ux * o1, b[1] + uy * o1)))
    return segs(lines, w, seed, wob, op, color)


def H(U, clip, ang=45, gap=4.0, w=1.0, dark=None, span=(0, 1), op=1.0, wob=0.4, brk=0.06, box=None, clip2=None):
    """Hatching inside a polygon (list of points) or path data."""
    if isinstance(clip, str):
        d = clip
        box = box or (0, 0, 600, 600)
    else:
        d = poly(clip)
        box = box or bbox(clip)
    g = gap if isinstance(gap, tuple) else (gap, gap)
    ww = w if isinstance(w, tuple) else (w, w)
    return hatch(U("h"), d, box, ang, g, ww, color=INK, seed=U.seed(), op=op, span=span, wob=wob, dark=dark, brk=brk,
                 clip2=clip2)


def XH(U, clip, ang=45, gap=4.0, w=1.0, ang2=None, gap2=None, span2=(0, 1), op=1.0, dark=None, box=None, **kw):
    a2 = ang + 70 if ang2 is None else ang2
    return (H(U, clip, ang, gap, w, op=op, dark=dark, box=box, **kw)
            + H(U, clip, a2, gap2 or gap, w, op=op, span=span2, dark=dark, box=box, **kw))


def ST(U, clip, n, light=None, r=(0.6, 1.2), op=0.9, box=None, power=1.6):
    if isinstance(clip, str):
        d, box = clip, box or (0, 0, 600, 600)
    else:
        d, box = poly(clip), box or bbox(clip, 0)
    return stipple(U("s"), d, box, n, U.seed(), light=light, r=r, color=INK, op=op, power=power)


def wash_grey(U, d, op=0.08, seed=1):
    """A thin ink wash (diluted grey) laid on paper."""
    return f'<g opacity="{op:.3f}">' + wash(d, GREY, seed, layers=3, spread=1.4, opacity=0.6) + "</g>"


def accent(U, d, box, seed=1, op=0.85, ang=-80, n=26, length=(10, 30), width=(2, 4)):
    """The single faded-vermilion wash allowed on each plate, laid under the ink."""
    light, base, dark = RED
    return (f'<g opacity="{op:.2f}">' + wash(d, base, seed, layers=3, spread=1.0, opacity=0.45)
            + strokes(U("ac"), d, box, [light, dark, base, light], seed, n=n, angle=ang, length=length, width=width,
                      opacity=(0.15, 0.4)) + "</g>")


# ================================================================ drawn things
def facade(U, q, cols, rows, style="pane", seed=1, mx=0.18, my=0.22, dark_p=0.25, w=1.1, op=1.0, frame=True):
    """Windows on a (perspective) wall quad [TL, TR, BR, BL]."""
    rnd = random.Random(seed)
    m = homog(q)
    out = []
    lines = []
    fills = []
    if style == "grid":            # curtain wall: floor lines + mullions
        for j in range(1, rows):
            lines.append((m(0, j / rows), m(1, j / rows)))
        for i in range(1, cols):
            lines.append((m(i / cols, 0), m(i / cols, 1)))
        out.append(segs(lines, w, seed, 0.2, op))
        for i in range(cols):
            for j in range(rows):
                if rnd.random() < dark_p:
                    fills.append([m((i + 0.08) / cols, (j + 0.1) / rows), m((i + 0.92) / cols, (j + 0.1) / rows),
                                  m((i + 0.92) / cols, (j + 0.9) / rows), m((i + 0.08) / cols, (j + 0.9) / rows)])
        if fills:
            out.insert(0, f'<path d="{" ".join(poly(f) for f in fills)}" fill="{INK}" opacity="{0.75 * op:.2f}"/>')
        return "".join(out)
    for i in range(cols):
        for j in range(rows):
            u0, u1 = (i + mx) / cols, (i + 1 - mx) / cols
            v0, v1 = (j + my) / rows, (j + 1 - my) / rows
            c = [m(u0, v0), m(u1, v0), m(u1, v1), m(u0, v1)]
            if style == "dark" or rnd.random() < dark_p:
                fills.append(c)
                if style == "pane" and frame:
                    lines += [(c[0], c[1]), (c[1], c[2]), (c[2], c[3]), (c[3], c[0])]
            elif style == "slit":
                lines.append((pt(c[0], c[3], 0), pt(c[1], c[2], 0)))
            else:
                lines += [(c[0], c[1]), (c[1], c[2]), (c[2], c[3]), (c[3], c[0])]
                if style == "pane":   # glazing bar + shade on top
                    lines.append((pt(c[0], c[1], 0.5), pt(c[3], c[2], 0.5)))
                    lines.append((pt(c[0], c[3], 0.3), pt(c[1], c[2], 0.3)))
    if fills:
        out.append(f'<path d="{" ".join(poly(f) for f in fills)}" fill="{INK}" opacity="{0.85 * op:.2f}"/>')
    out.append(segs(lines, w, seed, 0.15, op))
    return "".join(out)


def scallop_pts(cx, cy, rx, ry, seed, n=13, depth=0.12, flat=0.0):
    rnd = random.Random(seed)
    out = []
    ph = rnd.uniform(0, 6.28)
    for i in range(n):
        a = 2 * math.pi * i / n + ph
        k = 1 + depth * rnd.uniform(-1, 1)
        y = math.sin(a) * ry * k
        if flat and y > 0:
            y *= (1 - flat)
        out.append((cx + math.cos(a) * rx * k, cy + y))
    return out


def scallop_d(pts, cx, cy, puff=0.35, seed=None):
    """Bumpy foliage/cloud outline: arcs bulging outward between successive points."""
    rnd = random.Random(seed) if seed is not None else None
    d = [f"M {f1(pts[0][0])} {f1(pts[0][1])}"]
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ox, oy = mx - cx, my - cy
        L = math.hypot(ox, oy) or 1
        ch = math.hypot(b[0] - a[0], b[1] - a[1])
        pf = puff * (rnd.uniform(0.6, 1.35) if rnd else 1)
        d.append(f"Q {f1(mx + ox / L * ch * pf)} {f1(my + oy / L * ch * pf)} {f1(b[0])} {f1(b[1])}")
    return " ".join(d) + " Z"


def scribble(x0, x1, y, r, seed, loops=None, drift=0.0):
    """A looping 'eeee' scribble from x0 to x1 (used for foliage shade)."""
    rnd = random.Random(seed)
    L = x1 - x0
    loops = loops or max(2, int(L / (r * 1.3)))
    pts = []
    k = loops * 8
    for i in range(k + 1):
        t = i / k
        a = t * loops * 2 * math.pi
        rr = r * rnd.uniform(0.8, 1.15)
        pts.append((x0 + L * t + rr * 0.9 * math.cos(a + math.pi), y + rr * 0.75 * math.sin(a) + drift * t))
    return smooth_open(pts)


def lobe(U, cx, cy, rx, ry, seed, light=(-1, -1), w=1.6, dense=1.0, fill=PAPER, n=None, loopr=None, shade=1.0, **_):
    """One clump of foliage: paper fill, irregular scalloped outline, leaf-tick texture that thickens into
    hatched shade on the side away from the light."""
    rnd = random.Random(seed)
    n = n or max(9, int((rx + ry) / 3.6))
    pts = scallop_pts(cx, cy, rx, ry, seed, n, 0.1)
    d = scallop_d(pts, cx, cy, 0.34, seed)
    out = [F(d, fill)]
    lr = loopr or max(1.8, min(4.2, rx / 8))
    lx, ly = light
    ll = math.hypot(lx, ly) or 1
    lx, ly = lx / ll, ly / ll
    ticks, darks = [], []
    tries = int(rx * ry * 3.1 / (lr * lr) * 2.0 * dense)
    for _ in range(tries):
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(rnd.random())
        ux, uy = rr * math.cos(a), rr * math.sin(a)
        sh = -(ux * lx + uy * ly)
        t = max(0.0, min(1.0, (sh + 0.35) / 1.25)) * shade
        if rnd.random() > t ** 1.4:
            continue
        x, y = cx + ux * rx, cy + uy * ry
        r = lr * rnd.uniform(0.7, 1.25)
        tilt = rnd.uniform(-0.4, 0.4) * r
        ticks.append(f"M {f1(x - r)} {f1(y - tilt)} Q {f1(x)} {f1(y + r * 1.25)} {f1(x + r)} {f1(y + tilt)}")
        if t > 0.72 and rnd.random() < 0.55:
            darks.append(f"M {f1(x - r * 0.8)} {f1(y + r * 0.2)} Q {f1(x)} {f1(y + r * 1.25)} {f1(x + r * 0.8)} {f1(y + r * 0.2 + tilt)} "
                         f"Q {f1(x)} {f1(y + r * 0.7)} {f1(x - r * 0.8)} {f1(y + r * 0.2)} Z")
    uid = U("lb")
    inner = P(" ".join(ticks), 0.85, INK, 0.9)
    if darks:
        inner += f'<path d="{" ".join(darks)}" fill="{INK}" opacity="0.85"/>'
    inner += H(U, d, 100 if lx < 0 else 80, max(1.8, lr * 0.75), 0.75, span=(0.72, 1),
               dark=(cx - lx * rx * 2, cy - ly * ry * 2), box=(cx - rx * 1.4, cy - ry * 1.4, cx + rx * 1.4, cy + ry * 1.4),
               wob=0.3, brk=0.25)
    out.append(f'<clipPath id="{uid}"><path d="{d}"/></clipPath><g clip-path="url(#{uid})">{inner}</g>')
    out.append(P(d, w * 0.7))
    # heavier contour on the shadow side
    half = [p for p in pts if (p[0] - cx) * lx + (p[1] - cy) * ly < 0]
    if len(half) > 2:
        half.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    out.append(clipped(U("lc"), poly([(cx - lx * 3 * rx + ly * 3 * rx, cy - ly * 3 * ry - lx * 3 * ry),
                                      (cx - lx * 3 * rx - ly * 3 * rx, cy - ly * 3 * ry + lx * 3 * ry),
                                      (cx - ly * 3 * rx, cy + lx * 3 * ry), (cx + ly * 3 * rx, cy - lx * 3 * ry)]),
                       P(d, w * 1.35)))
    return "".join(out)


def tree(U, cx, base, h, w, seed, light=(-1, -1), trunk_h=0.3, lobes=5, lw=1.6, dense=1.0):
    """Deciduous tree: forked trunk and clumped scribbled foliage."""
    rnd = random.Random(seed)
    out = []
    th = h * trunk_h
    tw = max(2.0, w * 0.06)
    top = base - h
    # trunk + branches
    tp = [(cx + rnd.uniform(-1, 1), base), (cx + rnd.uniform(-2, 2), base - th * 0.6), (cx + rnd.uniform(-3, 3), base - th * 1.4)]
    out.append(nib(tp, tw * 2, taper=(1, 0.5), ramp=0.4, seed=seed, color=INK))
    for k in (-1, 1):
        out.append(nib([tp[1], (cx + k * w * 0.18, base - th * 1.3), (cx + k * w * 0.3, base - th * 1.9)], tw, seed=seed + k,
                       taper=(0.9, 0.2), color=INK))
    # foliage lobes, back to front, top first
    cy = top + h * 0.36
    spots = [(0, -0.28, 0.5, 0.42)]
    for i in range(lobes - 1):
        a = -math.pi * (0.1 + 0.8 * i / max(1, lobes - 2))
        spots.append((math.cos(a) * 0.32, 0.05 + 0.18 * (i % 2) - 0.12 * math.sin(-a), rnd.uniform(0.32, 0.4), rnd.uniform(0.28, 0.34)))
    spots.sort(key=lambda s: s[1])
    under = smooth_closed(scallop_pts(cx, cy + h * 0.04, w * 0.55, h * 0.4, seed + 99, 12, 0.08))
    out.append(F(under, INK, 0.85))
    for i, (ox, oy, sx, sy) in enumerate(spots):
        out.append(lobe(U, cx + ox * w, cy + oy * h, sx * w, sy * h, seed * 13 + i, light=light, w=lw, dense=dense))
    return "".join(out)


def cone_tree(U, cx, base, h, w, seed, lw=1.4):
    """Conifer in pen: zigzag tiers with dark scribble on the shadow side."""
    rnd = random.Random(seed)
    tiers = max(4, int(h / 9))
    L, R, sh = [], [], []
    for i in range(tiers + 1):
        t = i / tiers
        y = base - h * 0.08 - (h * 0.92) * (1 - t)
        half = w / 2 * (0.08 + 0.92 * t) * rnd.uniform(0.85, 1.1)
        L.append((cx - half, y))
        R.append((cx + half, y))
        if i:
            L.insert(len(L) - 1, (cx - half * 0.55, y - h / tiers * 0.35))
            R.insert(len(R) - 1, (cx + half * 0.55, y - h / tiers * 0.35))
    top = (cx, base - h)
    outline = [top] + R + L[::-1]
    out = [F(outline, PAPER)]
    # shade right half with dense short strokes
    lines = []
    for i in range(int(h * 0.9)):
        y = base - h * 0.08 - rnd.uniform(0, h * 0.85)
        t = 1 - (base - h * 0.08 - y) / (h * 0.92)
        half = w / 2 * (0.08 + 0.92 * t)
        x = cx + rnd.uniform(-0.1, 1) * half
        lines.append(((x, y), (x + rnd.uniform(2, 5), y + rnd.uniform(2, 4))))
    out.append(clipped(U("ct"), poly(outline), segs(lines, 0.9, seed, 0.2)))
    out.append(seg(cx, base - h * 0.1, cx, base, max(1.6, w * 0.08), seed))
    out.append(pen(outline, lw, seed, 0.3, closed=True))
    return "".join(out)


def palm(U, x, base, h, seed, lean=0.1, fronds=9, span=1.0, w=1.6):
    """Ink palm: ringed trunk and arching fronds of fine leaflets."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    trunk = [(x, base), (x + lean * h * 0.35, base - h * 0.5), (tx, ty)]
    C = cr(trunk, False, 3)
    out = []
    left, right = [], []
    for i, (px, py) in enumerate(C):
        t = i / (len(C) - 1)
        hw = lerp(h * 0.035, h * 0.022, t) + 1
        left.append((px - hw, py))
        right.append((px + hw, py))
    out.append(F(left + right[::-1], PAPER))
    rings = []
    for i in range(2, len(C) - 1, 2):
        px, py = C[i]
        t = i / (len(C) - 1)
        hw = lerp(h * 0.035, h * 0.022, t) + 1
        rings.append(((px - hw, py), (px + hw, py + 1.6)))
    out.append(segs(rings, 0.9, seed, 0.6))
    out.append(clipped(U("pt"), poly(left + right[::-1]), "".join(
        P(f"M {f1(px + 1)} {f1(py)} L {f1(px + 6)} {f1(py)}", 1.6, INK, 0.9) for px, py in C[::2])))
    out.append(pen(left, 1.4, seed, 0.3, smooth=True))
    out.append(pen(right, 1.6, seed + 1, 0.3, smooth=True))
    # fronds
    for k in range(fronds):
        a = math.radians(-180 + 180 * (k + 0.5) / fronds + rnd.uniform(-8, 8))
        if k == fronds // 2:
            a = math.radians(-90 + rnd.uniform(-15, 15))
        L = h * rnd.uniform(0.38, 0.5) * span
        droop = h * 0.22 * (abs(math.cos(a)) + 0.2) * span
        p0 = (tx, ty)
        p1 = (tx + math.cos(a) * L * 0.55, ty + math.sin(a) * L * 0.55 - L * 0.12)
        p2 = (tx + math.cos(a) * L, ty + math.sin(a) * L * 0.6 + droop)
        spine = cr([p0, p1, p2], False, 2.5)
        out.append(nib([p0, p1, p2], 2.2, taper=(1, 0.2), ramp=0.5, seed=seed + k, color=INK))
        lv = []
        for i in range(3, len(spine) - 1, 2):
            t = i / len(spine)
            sx, sy = spine[i]
            ax, ay = spine[i + 1][0] - spine[i - 1][0], spine[i + 1][1] - spine[i - 1][1]
            al = math.hypot(ax, ay) or 1
            nx, ny = -ay / al, ax / al
            ll = L * 0.24 * math.sin(math.pi * min(1, t * 1.1)) + 2
            for sgn in (-1, 1):
                ex = sx + nx * ll * sgn * 0.8 + ax / al * ll * 0.35
                ey = sy + ny * ll * sgn * 0.8 + ay / al * ll * 0.35 + ll * 0.45
                lv.append(((sx, sy), (ex, ey)))
        out.append(segs(lv, 1.05, seed + k, 0.8))
    out.append(F(smooth_closed([(tx - 4, ty - 2), (tx + 4, ty - 2), (tx + 5, ty + 5), (tx - 5, ty + 5)]), INK, 0.9))
    return "".join(out)


def ripples(U, x0, x1, y0, y1, seed, dens=1.0, gap=(2.6, 9.0), ln=((3, 10), (12, 34)), w=(0.9, 1.7), refl=(),
            skip=(), op=1.0, clip=None):
    """Ink water: short horizontal strokes, finer and tighter toward the horizon. refl = [(xa, xb, k)] adds
    stacked strokes (a broken reflection) under dark objects; skip = [(xa, xb)] keeps a glint of bare paper."""
    rnd = random.Random(seed)
    lines = []
    heavy = []
    y = y0 + gap[0] * 0.5
    while y < y1:
        t = (y - y0) / max(1, y1 - y0)
        g = lerp(gap[0], gap[1], t ** 1.2)
        L0, L1 = lerp(ln[0][0], ln[1][0], t), lerp(ln[0][1], ln[1][1], t)
        x = x0 - rnd.uniform(0, L1)
        while x < x1:
            L = rnd.uniform(L0, L1)
            gapx = rnd.uniform(L0 * 0.6, L1 * 1.6) / dens
            k = 0
            for xa, xb, kk in refl:
                if xa <= x + L / 2 <= xb:
                    k = max(k, kk)
            if any(xa <= x + L / 2 <= xb for xa, xb in skip):
                x += L + gapx
                continue
            if k:
                gapx *= (1 - 0.8 * k)
                L *= 1 + 0.3 * k
            yy = y + rnd.uniform(-g * 0.25, g * 0.25)
            bend = rnd.uniform(0.3, 1.2) * (1 if rnd.random() < 0.7 else -1)
            seg_ = ((x, yy), (x + L, yy + rnd.uniform(-0.4, 0.4)), bend)
            (heavy if k > 0.5 or t > 0.75 and rnd.random() < 0.35 else lines).append(seg_)
            x += L + gapx
        y += g
    def dd(lst):
        return " ".join(f"M {f1(a[0])} {f1(a[1])} Q {f1((a[0] + b[0]) / 2)} {f1((a[1] + b[1]) / 2 - bend)} {f1(b[0])} {f1(b[1])}"
                        for a, b, bend in lst)
    out = P(dd(lines), lerp(w[0], w[1], 0.45), INK, 0.9 * op) + (P(dd(heavy), w[1], INK, op) if heavy else "")
    if clip:
        return clipped(U("rp"), clip, out)
    return out


def cloud(U, cx, cy, w, h, seed, lw=1.3, shade=True):
    rnd = random.Random(seed)
    n = 9
    pts = []
    for i in range(n):
        a = math.pi + math.pi * i / (n - 1)
        r = 1 + rnd.uniform(-0.15, 0.25)
        pts.append((cx + math.cos(a) * w / 2 * r, cy + math.sin(a) * h * r))
    base = [(cx + w * 0.55, cy + h * 0.12), (cx - w * 0.55, cy + h * 0.12)]
    outline = pts + base
    d = scallop_d(pts, cx, cy + h * 0.2, 0.42)
    d = d[:-2] + f" Q {f1(cx + w * 0.62)} {f1(cy + h * 0.15)} {f1(cx + w * 0.3)} {f1(cy + h * 0.16)} L {f1(cx - w * 0.3)} {f1(cy + h * 0.16)} Q {f1(cx - w * 0.62)} {f1(cy + h * 0.15)} {f1(pts[0][0])} {f1(pts[0][1])} Z"
    out = [F(d, PAPER)]
    if shade:
        out.append(H(U, d, 0, 2.6, 0.8, box=(cx - w, cy - h * 1.4, cx + w, cy + h * 0.3), span=(0.62, 1), dark=(cx, cy + h),
                     wob=0.2, brk=0.2))
    out.append(P(d, lw))
    return "".join(out)


def bird(x, y, s, seed=1, w=1.6):
    rnd = random.Random(seed)
    a = rnd.uniform(-0.2, 0.2)
    return nib([(x - s, y - s * (0.35 + a)), (x - s * 0.45, y - s * 0.5), (x, y)], w, taper=(0.2, 0.6), seed=seed, color=INK) + \
        nib([(x, y), (x + s * 0.5, y - s * 0.55), (x + s * 1.05, y - s * (0.3 - a))], w, taper=(0.6, 0.2), seed=seed + 1, color=INK)


def person(x, y, h, seed=1, op=1.0, bag=False, flip=False):
    """A small pedestrian silhouette standing at (x, y)."""
    rnd = random.Random(seed)
    s = -1 if flip else 1
    hr = h * 0.1
    sh = h * 0.2
    stride = rnd.uniform(0.05, 0.12) * h
    body = [(x - h * 0.11, y - h * 0.78), (x + h * 0.11, y - h * 0.78), (x + h * 0.09, y - h * 0.45), (x - h * 0.09, y - h * 0.45)]
    out = [F(smooth_closed([(x - h * 0.12, y - h * 0.8), (x + h * 0.12, y - h * 0.8), (x + h * 0.11, y - h * 0.42),
                            (x - h * 0.11, y - h * 0.42)]), INK, op),
           f'<circle cx="{f1(x + s * h * 0.01)}" cy="{f1(y - h * 0.9)}" r="{f1(hr)}" fill="{INK}" opacity="{op:.2f}"/>',
           P(f"M {f1(x - h * 0.05)} {f1(y - h * 0.45)} L {f1(x - stride)} {f1(y)} M {f1(x + h * 0.05)} {f1(y - h * 0.45)} "
             f"L {f1(x + stride)} {f1(y)}", max(1.2, h * 0.08), INK, op)]
    if bag:
        out.append(f'<rect x="{f1(x + s * h * 0.1)}" y="{f1(y - h * 0.55)}" width="{f1(h * 0.12)}" height="{f1(h * 0.14)}" fill="{INK}" opacity="{op:.2f}"/>')
    return "".join(out)


def lamp(x, base, h, seed=1, kind="globe", w=2.0):
    """Street lamp: post, collar, lantern."""
    out = [nib([(x, base), (x, base - h * 0.5), (x, base - h * 0.86)], w * 1.4, taper=(1.2, 0.8), seed=seed, color=INK)]
    out.append(P(f"M {f1(x - h * 0.06)} {f1(base)} L {f1(x + h * 0.06)} {f1(base)} M {f1(x - h * 0.04)} {f1(base - h * 0.12)} "
                 f"L {f1(x + h * 0.04)} {f1(base - h * 0.12)}", w))
    if kind == "globe":
        r = h * 0.075
        out.append(f'<circle cx="{f1(x)}" cy="{f1(base - h * 0.93)}" r="{f1(r)}" fill="{PAPER}" stroke="{INK}" stroke-width="{w * 0.8:.1f}"/>')
    else:   # lantern
        t = base - h
        lw_ = h * 0.09
        L = [(x - lw_ * 0.6, t + h * 0.04), (x + lw_ * 0.6, t + h * 0.04), (x + lw_, t + h * 0.14), (x - lw_, t + h * 0.14)]
        out.append(F(L, PAPER) + pen(L, w * 0.8, seed, 0.1, True))
        out.append(F([(x - lw_ * 0.9, t + h * 0.04), (x, t - h * 0.02), (x + lw_ * 0.9, t + h * 0.04)], INK))
        out.append(P(f"M {f1(x)} {f1(t + h * 0.14)} L {f1(x)} {f1(t + h * 0.04)}", 1.0))
    return "".join(out)


def car(U, x, y, L, seed=1, flip=False, kind="sedan", fill=None):
    """Side view of a small car with its wheels on y (front to the right unless flip)."""
    s = -1 if flip else 1
    h = L * 0.36

    def X(u):
        return x + s * (u - 0.5) * L
    if kind == "classic":
        body = [(X(0.0), y - h * 0.3), (X(0.02), y - h * 0.62), (X(0.25), y - h * 0.7), (X(0.33), y - h * 1.08),
                (X(0.66), y - h * 1.08), (X(0.76), y - h * 0.72), (X(0.98), y - h * 0.62), (X(1.0), y - h * 0.3),
                (X(0.95), y - h * 0.18), (X(0.05), y - h * 0.18)]
    else:
        body = [(X(0.0), y - h * 0.3), (X(0.03), y - h * 0.62), (X(0.22), y - h * 0.7), (X(0.32), y - h * 1.05),
                (X(0.7), y - h * 1.05), (X(0.82), y - h * 0.68), (X(0.98), y - h * 0.6), (X(1.0), y - h * 0.3),
                (X(0.96), y - h * 0.18), (X(0.04), y - h * 0.18)]
    out = [F(body, PAPER, smooth=False)]
    if fill:
        out.append(fill(poly(body)))
    glass = [(X(0.36), y - h * 0.98), (X(0.66), y - h * 0.98), (X(0.75), y - h * 0.72), (X(0.27), y - h * 0.72)]
    out.append(F(glass, INK, 0.82))
    out.append(seg(X(0.51), y - h * 0.98, X(0.51), y - h * 0.72, 1.4, seed, 0, color=PAPER))
    out.append(H(U, body, 0, 2.4, 0.8, span=(0.0, 0.3), dark=(x, y)))
    out.append(pen(body, 1.6, seed, 0.2, True))
    out.append(seg(X(0.3), y - h * 0.5, X(0.86), y - h * 0.5, 0.9, seed))
    for u in (0.2, 0.8):
        out.append(f'<circle cx="{f1(X(u))}" cy="{f1(y - h * 0.18)}" r="{f1(h * 0.26)}" fill="{INK}"/>'
                   f'<circle cx="{f1(X(u))}" cy="{f1(y - h * 0.18)}" r="{f1(h * 0.1)}" fill="{PAPER}"/>')
    return "".join(out)


def flag(U, x, y, w, h, seed=1, wave=0.18, stripes=True):
    """A small flag on a staff, waving to the right; the stripes take the vermilion accent."""
    pts_top = [(x, y), (x + w * 0.33, y - h * wave), (x + w * 0.66, y + h * wave * 0.4), (x + w, y - h * wave * 0.3)]
    pts_bot = [(x + w, y + h - h * wave * 0.3), (x + w * 0.66, y + h + h * wave * 0.4), (x + w * 0.33, y + h - h * wave), (x, y + h)]
    d = smooth_open(pts_top) + " L " + smooth_open(pts_bot)[2:] + " Z"
    out = [F(d, PAPER)]
    if stripes:
        out.append(accent(U, d, (x, y - h * 0.3, x + w, y + h * 1.3), seed, op=0.9, ang=0, n=10, length=(6, 12), width=(1, 2)))
        out.append(clipped(U("fl"), d, F([(x, y - h), (x + w * 0.42, y - h), (x + w * 0.42, y + h * 0.55), (x, y + h * 0.55)], INK, 0.8)))
    out.append(P(d, 1.2))
    out.append(seg(x, y - 2, x, y + h * 3.2, 1.6, seed, 0))
    return "".join(out)


# ================================================================ plate furniture
def ground_paper(U, seed=5):
    return paper(U("paper"), PAPER, FLECK, seed, 1.2)


def finish(U, seed=9, op=0.7):
    return grain(U("grain"), INK, seed, op)


def border(U, x0=50, y0=50, x1=550, y1=550, seed=1, double=True, w=(2.8, 1.1), gap=6, corners=False):
    """Hand-ruled plate border."""
    out = [sketch([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w[0], seed, 2.5, wob=0.6)]
    if double:
        out.append(sketch([(x0 + gap, y0 + gap), (x1 - gap, y0 + gap), (x1 - gap, y1 - gap), (x0 + gap, y1 - gap)], w[1], seed + 1, 1.5,
                          wob=0.4))
    if corners:
        for cx, cy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            out.append(F([(cx - 5, cy), (cx, cy - 5), (cx + 5, cy), (cx, cy + 5)], INK))
    return "".join(out)


def name_size(name, max_w=430, mx=NAME_MAX):
    return fit_size(name, DMS, mx, max_w)


def T(x, y, s, font, size, fill=INK, ls=0, anchor="middle", extra=""):
    if anchor == "middle" and ls:
        x = x + ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def coords_line(cx, y, coords, rules=True, rule_len=34, gap=14, size=COORD_SIZE, color=INK, diamonds=False):
    w = measure(coords, MONO, size, COORD_LS)
    out = [T(cx, y, coords, MONO, size, color, COORD_LS)]
    if rules:
        my = y - size * 0.33
        a, b = cx - w / 2 - gap, cx + w / 2 + gap
        out.append(segs([((a - rule_len, my), (a, my)), ((b, my), (b + rule_len, my))], 1.6, 3, 0.3, color=color))
        if diamonds:
            for xd in (a - rule_len - 5, b + rule_len + 5):
                out.append(F([(xd - 3.5, my), (xd, my - 3.5), (xd + 3.5, my), (xd, my + 3.5)], color))
    return "".join(out)


def title_block(U, slug, cx, y_name, max_w=430, coord_gap=34, mx=NAME_MAX, rules=True, diamonds=False):
    name, coords = CITIES[slug]
    sz = name_size(name, max_w, mx)
    return T(cx, y_name, name, DMS, sz) + coords_line(cx, y_name + coord_gap, coords, rules, diamonds=diamonds)


def cartouche(U, slug, cx, cy, w, h, seed=3, mx=NAME_MAX, notch=10):
    """A ruled title panel with notched corners, laid over the foot of the picture."""
    name, coords = CITIES[slug]
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    n = notch

    def notched(a0, b0, a1, b1, k):
        return [(a0 + k, b0), (a1 - k, b0), (a1 - k, b0 + k * 0.0), (a1, b0 + k), (a1, b1 - k), (a1 - k, b1), (a0 + k, b1),
                (a0, b1 - k), (a0, b0 + k)]
    outer = notched(x0, y0, x1, y1, n)
    inner = notched(x0 + 6, y0 + 6, x1 - 6, y1 - 6, n - 2)
    out = [F(outer, PAPER), sketch(outer, 2.6, seed, 1.2), sketch(inner, 1.1, seed + 1, 0.8)]
    sz = name_size(name, w - 50, mx)
    ny = cy + sz * 0.12
    out.append(T(cx, ny, name, DMS, sz))
    out.append(coords_line(cx, ny + 32, coords, rules=True, rule_len=22, gap=12))
    return "".join(out)


def vignette(U, cx, cy, rx, ry, seed, inner, soft=0.72):
    """Lay `inner` into an irregular oval that fades out into the paper (ink-wash vignette)."""
    mid = U("vg")
    gid = U("vgg")
    rnd = random.Random(seed)
    pts = []
    n = 40
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + 0.06 * math.sin(3 * a + seed) + 0.04 * rnd.uniform(-1, 1)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = smooth_closed(pts)
    return (f'<defs><radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{max(rx, ry)}" gradientUnits="userSpaceOnUse" '
            f'gradientTransform="translate({cx} {cy}) scale({rx / max(rx, ry):.3f} {ry / max(rx, ry):.3f}) translate({-cx} {-cy})">'
            f'<stop offset="0" stop-color="#fff"/><stop offset="{soft}" stop-color="#fff"/><stop offset="1" stop-color="#000"/>'
            f'</radialGradient><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">'
            f'<path d="{d}" fill="url(#{gid})"/></mask></defs><g mask="url(#{mid})">{inner}</g>')



class Cam:
    """Pinhole camera: X right, Y up (metres), Z forward; screen centre (cx, vpy)."""
    def __init__(self, f=300, cx=300, vpy=300, eye=1.6):
        self.f, self.cx, self.vpy, self.eye = f, cx, vpy, eye

    def __call__(self, X, Y, Z):
        return (self.cx + self.f * X / Z, self.vpy + self.f * (self.eye - Y) / Z)

    def qx(self, X, Z0, Z1, Y0, Y1):
        """Wall in the plane X = const as [TL, TR, BR, BL] (near edge first)."""
        return [self(X, Y1, Z0), self(X, Y1, Z1), self(X, Y0, Z1), self(X, Y0, Z0)]

    def qz(self, Z, X0, X1, Y0, Y1):
        return [self(X0, Y1, Z), self(X1, Y1, Z), self(X1, Y0, Z), self(X0, Y0, Z)]


def hpat(U, ang=45, gap=3.0, w=0.9, op=1.0, cross=None, bg=None):
    """A hatch fill pattern (cheap engraved shading for many small shapes). Returns (defs, fill-url)."""
    pid = U("hp")
    b = f'<rect width="{gap}" height="{gap}" fill="{bg}"/>' if bg else ""
    c = (f'<path d="M 0 {gap / 2:.2f} L {gap} {gap / 2:.2f}" stroke="{INK}" stroke-width="{w * 0.85:.2f}"/>' if cross else "")
    return (f'<defs><pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({ang})">{b}<path d="M {gap / 2:.2f} 0 L {gap / 2:.2f} {gap}" stroke="{INK}" '
            f'stroke-width="{w}" opacity="{op}"/>{c}</pattern></defs>', f"url(#{pid})")


def cobbles(U, C, X0, X1, Z0, Z1, seed, row=0.5, stone=0.7, w=0.8, op=0.7):
    """Paving setts in perspective on the ground plane Y=0."""
    rnd = random.Random(seed)
    lines = []
    Z = Z0
    k = 0
    while Z < Z1:
        z2 = Z + row
        a, b = C(X0, 0, Z), C(X1, 0, Z)
        lines.append((a, b))
        if C(0, 0, Z)[1] - C(0, 0, z2)[1] > 1.6:
            X = X0 + (k % 2) * stone / 2 + rnd.uniform(0, 0.2)
            while X < X1:
                lines.append((C(X, 0, Z), C(X, 0, z2)))
                X += stone * rnd.uniform(0.85, 1.15)
        Z = z2 * 1.0
        k += 1
    return segs(lines, w, seed, 0.1, op)



def soft_frame(U, cx, cy, rx, ry, seed, inner, expo=3.0, rings=14, inset=0.2, wash_op=0.0):
    """Vignette: `inner` fades out through a ragged superellipse edge, like a drawing dissolving into the paper."""
    mid = U("sf")
    rnd = random.Random(seed)
    shapes = []
    for r in range(rings):
        k = 1 - inset * r / (rings - 1)
        pts = []
        n = 48
        ph = rnd.uniform(0, 6.28)
        for i in range(n):
            a = 2 * math.pi * i / n
            c, s_ = math.cos(a), math.sin(a)
            sx = math.copysign(abs(c) ** (2 / expo), c)
            sy = math.copysign(abs(s_) ** (2 / expo), s_)
            j = 1 + 0.035 * math.sin(5 * a + ph) + 0.02 * rnd.uniform(-1, 1)
            pts.append((cx + rx * k * j * sx, cy + ry * k * j * sy))
        shapes.append(f'<path d="{smooth_closed(pts)}" fill="#fff" opacity="0.24"/>')
    w = ""
    if wash_op:
        w = f'<path d="{shapes[0].split(chr(34))[1]}" fill="{GREY}" opacity="{wash_op}"/>'
    return (f'<defs><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">'
            f'<rect width="600" height="600" fill="#000"/>{"".join(shapes)}</mask></defs>'
            f'<g mask="url(#{mid})">{w}{inner}</g>')


def eiffel(U, cx, apex, base, seed=1, shade_right=True):
    """The Eiffel Tower in elevation (true proportions): curved lattice legs, arch, three levels, lantern."""
    k = (base - apex) / 330.0

    def Y(m):
        return base - m * k
    prof = [(0, 62.5), (12, 55), (30, 46), (57, 35.5), (80, 28), (115, 19.5), (150, 13.5), (190, 9.5), (230, 7), (276, 5.2)]

    def hw(m):
        for (m0, w0), (m1, w1) in zip(prof, prof[1:]):
            if m0 <= m <= m1:
                return lerp(w0, w1, (m - m0) / (m1 - m0)) * k
        return prof[-1][1] * k
    ms = [i * 3 for i in range(93)]
    L = [(cx - hw(m), Y(m)) for m in ms]
    R = [(cx + hw(m), Y(m)) for m in ms]
    sil = L + R[::-1]
    # openings (negative space)
    arch = [(cx - 37 * k, Y(0))] + [(cx - 37 * k * math.cos(a), Y(39 * math.sin(a) ** 0.9 + 0)) for a in
                                     [i * math.pi / 24 for i in range(1, 24)]] + [(cx + 37 * k, Y(0))]
    arch = [(cx - 37 * k, Y(0) + 4)] + arch + [(cx + 37 * k, Y(0) + 4)]
    mid = [(cx - 19 * k, Y(63)), (cx - 10 * k, Y(98)), (cx - 4 * k, Y(108)), (cx, Y(110)), (cx + 4 * k, Y(108)),
           (cx + 10 * k, Y(98)), (cx + 19 * k, Y(63))]
    upper = [(cx - 5 * k, Y(120)), (cx - 1.2 * k, Y(178)), (cx, Y(186)), (cx + 1.2 * k, Y(178)), (cx + 5 * k, Y(120))]
    holes = [arch, mid, upper]
    out = [F(sil, PAPER)]
    lat = H(U, poly(sil), 58, 4.2, 0.75, box=bbox(sil), wob=0.1, brk=0) + H(U, poly(sil), -58, 4.2, 0.75, box=bbox(sil), wob=0.1, brk=0)
    hz = []
    for m in range(6, 276, 7):
        hz.append(((cx - hw(m), Y(m)), (cx + hw(m), Y(m))))
    lat += segs(hz, 0.7, seed, 0)
    if shade_right:
        half = [(cx + 2, Y(0)), (cx + 2, Y(276))] + R[::-1][:-1]
        half = [(cx, Y(276))] + R[::-1] + [(cx, Y(0))]
        lat += H(U, half, 90, 2.0, 0.8, span=(0.35, 1), dark=(cx + 60, Y(40)), wob=0.1, brk=0)
    out.append(lat)
    for hl in holes:
        out.append(F(hl, PAPER))
        out.append(pen(hl, 1.4, seed, 0.1, closed=False, smooth=True))
    # outer edges, bold, with a slight swell
    out.append(nib(L[::3] + [L[-1]], 2.6, taper=(1, 0.6), ramp=0.1, seed=seed, color=INK, smooth=False))
    out.append(nib(R[::3] + [R[-1]], 3.0, taper=(1, 0.6), ramp=0.1, seed=seed + 1, color=INK, smooth=False))
    # inner leg edges (two faces of each leg seen at once)
    for sgn in (-1, 1):
        edge = [(cx + sgn * (hw(m) - lerp(26, 6, min(1, m / 180)) * k * 0.55), Y(m)) for m in range(0, 186, 6)]
        out.append(pen(edge, 0.9, seed + 2, 0.1, smooth=True))
    # levels
    for m0, m1, w_, arches in ((57, 64, 39.5, 18), (115, 119, 22, 8)):
        y0, y1 = Y(m1), Y(m0)
        q = [(cx - w_ * k, y0), (cx + w_ * k, y0), (cx + w_ * k, y1), (cx - w_ * k, y1)]
        out.append(F(q, PAPER))
        aw = 2 * w_ * k / arches
        ad = []
        for i in range(arches):
            ax = cx - w_ * k + i * aw
            ad.append(f"M {f1(ax)} {f1(y1)} Q {f1(ax + aw / 2)} {f1(y1 - (y1 - y0) * 1.3)} {f1(ax + aw)} {f1(y1)}")
        out.append(P(" ".join(ad), 0.8))
        out.append(H(U, [(cx + w_ * k * 0.55, y0), (cx + w_ * k, y0), (cx + w_ * k, y1), (cx + w_ * k * 0.55, y1)], 90, 1.6, 0.7))
        out.append(sketch(q, 1.8, seed + int(m0), 1.2))
        out.append(seg(cx - w_ * k - 1, y0 - 1.5, cx + w_ * k + 1, y0 - 1.5, 1.0, seed))
        # little flag-pole railings
        out.append(segs([((x, y0 - 1.5), (x, y0 - 4)) for x in [cx - w_ * k + j * 4 for j in range(int(2 * w_ * k / 4) + 1)]], 0.6, seed, 0))
    # lantern, dome, antenna
    ly0, ly1 = Y(292), Y(276)
    lq = [(cx - 6 * k, ly0), (cx + 6 * k, ly0), (cx + 6 * k, ly1), (cx - 6 * k, ly1)]
    out.append(F(lq, PAPER) + H(U, lq, 90, 1.5, 0.7, span=(0.5, 1), dark=(cx + 10, ly1)) + sketch(lq, 1.6, seed + 3, 0.8))
    out.append(seg(cx - 8 * k, ly1, cx + 8 * k, ly1, 1.8, seed))
    dome = [(cx - 5 * k, ly0), (cx - 3.6 * k, Y(298)), (cx, Y(301)), (cx + 3.6 * k, Y(298)), (cx + 5 * k, ly0)]
    out.append(F(dome, PAPER) + pen(dome, 1.5, seed, 0.1, smooth=True))
    out.append(nib([(cx, Y(301)), (cx, Y(318)), (cx, Y(330))], 2.0, taper=(1, 0.3), ramp=0.6, seed=seed, color=INK))
    out.append(seg(cx - 2, Y(312), cx + 2, Y(312), 1.6, seed))
    return "".join(out)


def cyclist(x, y, h, seed=1, flip=False):
    s = -1 if flip else 1
    r = h * 0.22
    a, b = (x - s * h * 0.32, y - r), (x + s * h * 0.32, y - r)
    out = [f'<circle cx="{f1(a[0])}" cy="{f1(a[1])}" r="{f1(r)}" fill="none" stroke="{INK}" stroke-width="1.2"/>',
           f'<circle cx="{f1(b[0])}" cy="{f1(b[1])}" r="{f1(r)}" fill="none" stroke="{INK}" stroke-width="1.2"/>']
    seat = (x - s * h * 0.06, y - h * 0.52)
    bar = (x + s * h * 0.24, y - h * 0.58)
    crank = (x, y - r)
    out.append(P(f"M {f1(a[0])} {f1(a[1])} L {f1(crank[0])} {f1(crank[1])} L {f1(seat[0])} {f1(seat[1])} L {f1(a[0])} {f1(a[1])} "
                 f"M {f1(crank[0])} {f1(crank[1])} L {f1(bar[0] - s * 2)} {f1(bar[1] + 3)} L {f1(seat[0])} {f1(seat[1])} "
                 f"M {f1(b[0])} {f1(b[1])} L {f1(bar[0])} {f1(bar[1])} l {f1(-s * 3)} -1", 1.3))
    # rider
    hip = (seat[0], seat[1] - h * 0.04)
    sh = (x + s * h * 0.08, y - h * 0.95)
    out.append(P(f"M {f1(hip[0])} {f1(hip[1])} L {f1(sh[0])} {f1(sh[1])}", h * 0.14))
    out.append(P(f"M {f1(hip[0])} {f1(hip[1])} L {f1(crank[0] + s * 3)} {f1(crank[1] - 6)} L {f1(crank[0] + s * 2)} {f1(crank[1])} "
                 f"M {f1(sh[0])} {f1(sh[1] + 2)} L {f1(bar[0])} {f1(bar[1] - 1)}", h * 0.07))
    out.append(f'<circle cx="{f1(sh[0] + s * 1.5)}" cy="{f1(sh[1] - h * 0.13)}" r="{f1(h * 0.09)}" fill="{INK}"/>')
    return "".join(out)


# ================================================================ NEW YORK
@design("new-york")
def new_york(U):
    """Brooklyn Bridge: the Brooklyn tower close up from the park, cables sweeping to Manhattan."""
    out = [ground_paper(U, 11)]
    pic = [(57, 57), (543, 57), (543, 432), (57, 432)]
    art = []
    # --- sky: engraved horizontal rules fading toward the horizon
    sky = []
    y = 62
    while y < 300:
        t = (y - 62) / 238
        sky.append(((57, y), (543, y)))
        y += lerp(3.2, 9, t)
    art.append(clipped(U("sk"), poly([(57, 57), (543, 57), (543, 330), (57, 330)]),
                       segs(sky, 0.7, 3, 0.15, op=0.55)))
    art.append(cloud(U, 470, 100, 110, 22, 4))
    art.append(cloud(U, 395, 135, 70, 14, 7))
    # --- Lower Manhattan skyline across the river (x 250..543, base 334)
    BASE = 334
    bl = []

    def tower(x0, x1, top, seed, style="pane", cols=None, rows=None, roof=None, shade=True):
        q = [(x0, top), (x1, top), (x1, BASE), (x0, BASE)]
        o = [F(q, PAPER)]
        c = cols or max(2, int((x1 - x0) / 6))
        r = rows or max(3, int((BASE - top) / 7))
        o.append(facade(U, [(x0 + 2, top + 4), (x1 - 2, top + 4), (x1 - 2, BASE), (x0 + 2, BASE)], c, r, style, seed,
                        dark_p=0.18, w=0.8))
        if shade:
            o.append(H(U, [(x1 - (x1 - x0) * 0.32, top), (x1, top), (x1, BASE), (x1 - (x1 - x0) * 0.32, BASE)], 90, 2.2, 0.8))
        o.append(sketch(q, 1.3, seed, 1.0))
        if roof:
            o.append(roof)
        return "".join(o)
    # far row (lighter)
    far = [(268, 286, 262), (300, 318, 250), (330, 344, 232), (354, 372, 246), (446, 466, 256), (472, 490, 240),
           (516, 534, 248), (530, 548, 262)]
    for i, (a, b, t) in enumerate(far):
        bl.append(f'<g opacity="0.55">{tower(a, b, t, 40 + i, "grid")}</g>')
    # One World Trade Center: faceted taper and spire
    ox, ow, otop = 352, 38, 150
    one = [(ox - ow / 2, BASE), (ox - ow * 0.33, otop), (ox + ow * 0.33, otop), (ox + ow / 2, BASE)]
    bl.append(F(one, PAPER))
    bl.append(F([(ox, otop), (ox + ow * 0.33, otop), (ox + ow / 2, BASE), (ox, BASE)], PAPER))
    bl.append(H(U, [(ox, otop), (ox + ow * 0.33, otop), (ox + ow / 2, BASE), (ox + ow * 0.08, BASE)], 90, 2.0, 0.8))
    bl.append(H(U, [(ox - ow * 0.33, otop), (ox, otop), (ox + ow * 0.08, BASE), (ox - ow / 2, BASE)], 0, 3.6, 0.6, op=0.7))
    bl.append(segs([((ox - ow * 0.33, otop), (ox + ow * 0.08, BASE)), ((ox, otop), (ox + ow * 0.08, BASE)),
                    ((ox + ow * 0.33, otop), (ox + ow * 0.08, BASE)), ((ox, otop), (ox - ow / 2, BASE))], 1.0, 5, 0.1))
    bl.append(sketch(one, 1.6, 6, 1.0))
    bl.append(F([(ox - ow * 0.36, otop), (ox + ow * 0.36, otop), (ox + ow * 0.3, otop - 6), (ox - ow * 0.3, otop - 6)], INK))
    bl.append(seg(ox, otop - 6, ox, otop - 52, 1.8, 7, 0))
    bl.append(seg(ox, otop - 52, ox, otop - 68, 1.0, 8, 0))
    # 8 Spruce: rippled stainless tower
    sx0, sx1, stop = 392, 418, 196
    q = [(sx0, stop), (sx1, stop), (sx1, BASE), (sx0, BASE)]
    bl.append(F(q, PAPER))
    rip = []
    for j in range(int((BASE - stop) / 3.2)):
        yy = stop + 3 + j * 3.2
        a = 2.4 * math.sin(j * 0.45)
        rip.append(f"M {f1(sx0 + 1)} {f1(yy)} Q {f1((sx0 + sx1) / 2 + a)} {f1(yy + a * 0.6)} {f1(sx1 - 1)} {f1(yy)}")
    bl.append(P(" ".join(rip), 0.75, INK, 0.8))
    bl.append(H(U, [(sx1 - 9, stop), (sx1, stop), (sx1, BASE), (sx1 - 9, BASE)], 90, 2.0, 0.8))
    bl.append(sketch(q, 1.4, 9, 1.0))
    # Woolworth Building: gothic crown
    wx, wtop = 436, 214
    bl.append(tower(424, 448, wtop + 26, 12, "slit", 4, 14))
    crown = [(428, wtop + 26), (428, wtop + 12), (431, wtop + 6), (441, wtop + 6), (444, wtop + 12), (444, wtop + 26)]
    bl.append(F(crown, PAPER) + sketch(crown, 1.3, 13, 0.6, closed=False))
    bl.append(F([(431, wtop + 6), (436, wtop - 8), (441, wtop + 6)], PAPER) + H(U, [(436, wtop - 8), (441, wtop + 6), (436, wtop + 6)], 90, 1.6, 0.7)
              + sketch([(431, wtop + 6), (436, wtop - 8), (441, wtop + 6)], 1.3, 14, 0.5, closed=False))
    bl.append(seg(436, wtop - 8, 436, wtop - 16, 1.0, 15, 0))
    for px in (426, 446):
        bl.append(seg(px, wtop + 26, px, wtop + 16, 1.0, 16, 0) + seg(px, wtop + 16, px, wtop + 11, 0.8, 17, 0))
    # mid buildings
    mids = [(254, 276, 288, "pane"), (280, 302, 270, "slit"), (306, 330, 284, "pane"), (372, 390, 268, "grid"),
            (452, 476, 290, "pane"), (496, 520, 280, "slit"), (520, 543, 296, "pane")]
    for i, (a, b, t, st) in enumerate(mids):
        bl.append(tower(a, b, t, 60 + i, st))
    art.append("".join(bl))
    # waterfront line
    art.append(F([(57, BASE - 1), (543, BASE - 1), (543, BASE + 4), (57, BASE + 4)], PAPER))
    art.append(seg(240, BASE + 1, 543, BASE + 1, 2.2, 21, 0.4))
    piers = [((x, BASE + 1), (x, BASE + 5)) for x in range(250, 540, 5)]
    art.append(segs(piers, 0.8, 22, 0))
    # --- water
    art.append(H(U, [(240, BASE + 4), (543, BASE + 4), (543, BASE + 12), (240, BASE + 12)], 0, 1.8, 0.7, op=0.8))
    art.append(ripples(U, 57, 543, BASE + 5, 432, 31, dens=1.0, refl=[(104, 262, 0.95), (334, 370, 0.55), (476, 514, 0.6), (392, 418, 0.4)],
                       skip=[(400, 440)]))
    # --- far (Manhattan) tower of the bridge, small
    fx0, fx1, ftop = 480, 512, 236
    ft = [(fx0, BASE + 2), (fx0, ftop + 8), (fx0 + 3, ftop), (fx1 - 3, ftop), (fx1, ftop + 8), (fx1, BASE + 2)]
    art.append(F(ft, PAPER))
    art.append(H(U, [(fx1 - 8, ftop), (fx1, ftop), (fx1, BASE), (fx1 - 8, BASE)], 90, 1.8, 0.8))
    for ax in (fx0 + 6, fx0 + 19):
        arch = [(ax, 296), (ax, 262), (ax + 3.5, 252), (ax + 7, 262), (ax + 7, 296)]
        art.append(F(arch, INK, 0.85))
    art.append(sketch(ft, 1.5, 33, 0.6, closed=False))
    # --- deck receding toward Manhattan
    DX0, DX1 = 262, 543
    dtop = lambda x: lerp(276, 297, (x - DX0) / (DX1 - DX0))
    dbot = lambda x: lerp(292, 302, (x - DX0) / (DX1 - DX0))
    deck = [(DX0, dtop(DX0)), (DX1, dtop(DX1)), (DX1, dbot(DX1)), (DX0, dbot(DX0))]
    art.append(F(deck, PAPER))
    tr_ = []
    x = DX0 + 4
    k = 0
    while x < DX1:
        tr_.append(((x, dtop(x) + 1), (x, dbot(x) - 1)))
        nx_ = x + lerp(9, 4, (x - DX0) / (DX1 - DX0))
        if k % 2 == 0:
            tr_.append(((x, dtop(x) + 1), (nx_, dbot(nx_) - 1)))
        else:
            tr_.append(((x, dbot(x) - 1), (nx_, dtop(nx_) + 1)))
        x = nx_
        k += 1
    art.append(segs(tr_, 0.8, 34, 0))
    art.append(pen([(DX0, dtop(DX0)), (DX1, dtop(DX1))], 1.8, 35, 0.2) + pen([(DX0, dbot(DX0)), (DX1, dbot(DX1))], 2.2, 36, 0.2))
    # --- near tower (Brooklyn): front face with two gothic arches, side face in shade
    TX0, TX1, TT, TB = 128, 262, 92, 432
    side = [(104, TT + 8), (TX0, TT), (TX0, TB), (104, TB)]
    # cables first (behind tower face, in front of skyline)
    cab = []
    # main cables to Manhattan: from tower top to the far tower
    for (sx, sy, ex, ey, my_) in ((236, 104, 484, 238, 292), (252, 108, 508, 240, 296)):
        cab.append((sx, sy, ex, ey, my_))
    cables = []
    hangers = []
    for sx, sy, ex, ey, low in cab:
        c1 = (sx + (ex - sx) * 0.42, low + 26)
        cables.append(f"M {f1(sx)} {f1(sy)} Q {f1(c1[0])} {f1(c1[1])} {f1(ex)} {f1(ey)}")
        for i in range(1, 36):
            t = i / 36
            bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * c1[0] + t * t * ex
            by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * c1[1] + t * t * ey
            if by < dtop(bx) - 1:
                hangers.append(((bx, by), (bx, dtop(bx))))
    art.append(segs(hangers, 0.7, 37, 0, op=0.9))
    # diagonal stays fanning from the tower top down to the deck
    stays = [((TX1 - 4, TT + 18 + i * 1.5), (TX1 + 14 + i * 13, dtop(TX1 + 14 + i * 13))) for i in range(9)]
    art.append(segs(stays, 0.8, 38, 0))
    art.append(P(" ".join(cables), 2.2))
    # cables toward Brooklyn (left, out of frame)
    lc = []
    lh = []
    for sx, sy, ex, ey, c in ((112, 106, 40, 238, (80, 196)), (124, 102, 40, 226, (90, 184))):
        lc.append(f"M {f1(sx)} {f1(sy)} Q {f1(c[0])} {f1(c[1])} {f1(ex)} {f1(ey)}")
    ldeck = [(57, 279), (TX0, 276), (TX0, 292), (57, 296)]
    art.append(F(ldeck, PAPER) + H(U, ldeck, 0, 2.6, 0.8, span=(0.5, 1), dark=(80, 296)))
    art.append(segs([((x, lerp(279, 276, (x - 57) / (TX0 - 57)) + 1), (x + 6, lerp(296, 292, (x - 57) / (TX0 - 57)) - 1))
                     for x in range(60, TX0 - 4, 7)], 0.8, 70, 0))
    art.append(pen([(57, 279), (TX0, 276)], 1.8, 71, 0.2) + pen([(57, 296), (TX0, 292)], 2.2, 72, 0.2))
    for sx, sy, ex, ey, c in ((112, 106, 40, 238, (80, 196)), (124, 102, 40, 226, (90, 184))):
        for i in range(1, 16):
            t = i / 16
            bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * c[0] + t * t * ex
            by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * c[1] + t * t * ey
            if 57 < bx < TX0 - 2:
                lh.append(((bx, by), (bx, lerp(279, 276, (bx - 57) / (TX0 - 57)))))
    art.append(segs(lh, 0.7, 73, 0))
    art.append(P(" ".join(lc), 2.2))
    # tower body
    face = [(TX0, TT), (TX1, TT), (TX1, TB), (TX0, TB)]
    art.append(F(side, PAPER) + F(face, PAPER))
    art.append(XH(U, side, 90, 2.4, 0.9, ang2=30, gap2=3.2, span2=(0, 1)))
    # stone courses on the front face
    courses = []
    y = TT + 30
    while y < TB:
        courses.append(((TX0, y), (TX1, y)))
        y += 7.5
    joints = []
    rj = random.Random(5)
    y = TT + 30
    row = 0
    while y < TB - 7:
        x = TX0 + (row % 2) * 9 + rj.uniform(0, 4)
        while x < TX1:
            joints.append(((x, y), (x, y + 7.5)))
            x += rj.uniform(14, 22)
        y += 7.5
        row += 1
    art.append(clipped(U("sc"), poly(face), segs(courses, 0.6, 39, 0.3, op=0.55) + segs(joints, 0.6, 74, 0, op=0.45)))
    # arches: pointed openings from the deck up
    AW, ADECK, ASPRING, ATOP = 34, 276, 178, 140
    arch_d = []
    for ax in (TX0 + 20, TX0 + 20 + AW + 26):
        cx = ax + AW / 2
        arc = [(ax, ADECK + 30), (ax, ASPRING)] + [
            (cx - AW / 2 + AW / 2 * (1 - math.cos(a)) * 0.0 + (AW / 2) * (1 - math.cos(a)), ASPRING - (ASPRING - ATOP) * math.sin(a))
            for a in [k * math.pi / 2 / 6 for k in range(1, 7)]]
        L = [(ax, ADECK + 30), (ax, ASPRING)]
        for k in range(1, 7):
            a = k * math.pi / 2 / 6
            L.append((ax + AW / 2 * (1 - math.cos(a)) * 1.0, ASPRING - (ASPRING - ATOP) * math.sin(a)))
        R = [(2 * cx - x_, y_) for x_, y_ in L[::-1]]
        A = L + R
        arch_d.append(A)
    for A in arch_d:
        art.append(F(A, PAPER))
        # what is seen through the arch: sky rules + cables beyond
        art.append(clipped(U("ar"), poly(A), segs([((A[0][0], yy), (A[-1][0], yy)) for yy in range(ATOP, ADECK, 6)], 0.6, 40, 0, op=0.5)
                           + P(f"M {f1(A[0][0])} {f1(ADECK - 6)} L {f1(A[-1][0])} {f1(ADECK - 10)}", 1.0)))
        # reveal (thickness) shading on the left jamb + soffit
        jam = [A[0], A[1]] + A[2:7] + [(A[6][0] + 5, A[6][1] + 3)] + [(p[0] + 5, p[1] + 2) for p in A[5:1:-1]] + [(A[1][0] + 5, A[1][1]), (A[0][0] + 5, A[0][1])]
        art.append(F(jam, PAPER) + H(U, jam, 90, 1.6, 0.8))
        art.append(pen(A, 2.0, 41, 0.2, closed=False))
        # drip-mould over the arch
        mould = [(x_ - (2.5 if x_ < (A[0][0] + A[-1][0]) / 2 else -2.5), y_ - 4) for x_, y_ in A[1:-1]]
        art.append(pen(mould, 1.2, 42, 0.2))
    # deck passing through the arches
    art.append(F([(TX0 + 20, ADECK), (TX1 - 20, ADECK), (TX1 - 20, ADECK + 16), (TX0 + 20, ADECK + 16)], PAPER))
    art.append(H(U, [(TX0 + 20, ADECK), (TX1 - 20, ADECK), (TX1 - 20, ADECK + 16), (TX0 + 20, ADECK + 16)], 0, 2.4, 0.8))
    art.append(seg(TX0 + 18, ADECK, TX1 - 18, ADECK, 1.6, 43, 0) + seg(TX0 + 18, ADECK + 16, TX1 - 18, ADECK + 16, 1.6, 44, 0))
    # pier panels (recessed buttresses) and cornices
    for px0, px1 in ((TX0 + 4, TX0 + 16), (TX0 + 20 + AW + 6, TX0 + 20 + AW + 20), (TX1 - 16, TX1 - 4)):
        pnl = [(px0, ASPRING - 30), (px1, ASPRING - 30), (px1, ADECK - 6), (px0, ADECK - 6)]
        art.append(H(U, pnl, 90, 2.0, 0.7) + sketch(pnl, 1.0, 45, 0.5))
    for yy, ww in ((TT + 6, 2.0), (TT + 12, 1.2), (TT + 26, 1.6), (TT + 30, 1.0), (ADECK - 2, 1.2), (ADECK + 22, 1.2)):
        art.append(seg(TX0 - 2, yy, TX1 + 2, yy, ww, int(yy), 0.2))
    # cap
    cap = [(TX0 - 4, TT + 6), (TX1 + 4, TT + 6), (TX1 + 4, TT), (TX0 - 4, TT)]
    art.append(F(cap, PAPER) + H(U, cap, 0, 1.8, 0.8) + sketch(cap, 1.8, 46, 1.0))
    # saddles: cables come over the top
    art.append(P("M 104 112 Q 118 96 136 100 M 238 104 Q 252 96 266 104", 2.4))
    # base: rusticated stone, shade, waterline
    art.append(H(U, [(TX0, ADECK + 22), (TX1, ADECK + 22), (TX1, TB), (TX0, TB)], 90, 3.4, 0.7, span=(0.55, 1), dark=(TX1, 380)))
    art.append(H(U, face, 90, 2.6, 0.8, span=(0.86, 1), dark=(TX1, 300)))
    art.append(sketch(face, 3.0, 47, 1.5, closed=False))
    art.append(pen([(104, TT + 8), (104, TB)], 2.4, 48, 0.3) + pen([(104, TT + 8), (TX0, TT)], 2.0, 49, 0.2))
    art.append(seg(104, 384, TX1 + 6, 384, 2.0, 50, 0.4))
    # flag on the tower (the one vermilion accent)
    art.append(flag(U, 195, 66, 26, 15, 51))
    art.append(seg(195, 66, 195, TT, 1.6, 52, 0))
    # --- foreground: Brooklyn pier railing, lamp, a couple at the rail
    pier = [(57, 404), (300, 410), (300, 432), (57, 432)]
    art.append(F(pier, PAPER))
    art.append(H(U, pier, 0, 3.0, 0.9))
    pil = []
    for x in range(64, 300, 22):
        yy = lerp(404, 410, (x - 57) / 243)
        pil.append(((x, yy), (x, 432)))
    art.append(segs(pil, 2.2, 53, 0.3))
    art.append(pen([(57, 404), (300, 410)], 2.6, 54, 0.3))
    rail_y = lambda x: lerp(384, 391, (x - 57) / 243)
    rails = [((57, rail_y(57)), (300, rail_y(300))), ((57, rail_y(57) + 9), (300, rail_y(300) + 9))]
    posts = [((x, rail_y(x)), (x, lerp(404, 410, (x - 57) / 243))) for x in range(60, 300, 18)]
    art.append(segs(rails, 1.8, 55, 0.2) + segs(posts, 1.6, 56, 0.1))
    art.append(lamp(276, 409, 64, 57, "lantern", 1.8))
    art.append(person(214, 406, 26, 58) + person(226, 407, 24, 59, flip=True))
    # boats
    tug = [(392, 386), (436, 386), (432, 396), (396, 396)]
    art.append(F(tug, PAPER) + H(U, tug, 0, 1.8, 0.8) + sketch(tug, 1.8, 60, 0.6))
    cab_ = [(404, 386), (404, 376), (420, 376), (420, 386)]
    art.append(F(cab_, PAPER) + sketch(cab_, 1.4, 61, 0.4) + F([(407, 379), (412, 379), (412, 383), (407, 383)], INK))
    art.append(F([(411, 376), (415, 376), (415, 366), (411, 366)], INK))
    art.append(P("M 392 392 q -24 1 -46 6 M 394 396 q -20 3 -38 10", 1.0, INK, 0.8))
    # gulls
    art.append(bird(318, 118, 8, 62) + bird(336, 104, 6, 63) + bird(296, 140, 5, 64))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 65, 1.4))
    out.append(border(U, 48, 48, 552, 552, 66, double=False, w=(1.2, 1.2)))
    out.append(title_block(U, "new-york", 300, 498, 440))
    out.append(finish(U))
    return "".join(out)



# ================================================================ PARIS
def haussmann(U, C, X, Z0, Z1, seed, shade=False, bay=2.7, shops="dark"):
    """A Haussmann block face in the plane X (left side if X < 0): stone courses, tall French windows,
    continuous iron balconies on the 2nd and 5th floors, cornice, zinc mansard with dormers and chimneys."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1          # direction toward the street
    out = []
    wall = C.qx(X, Z0, Z1, 0, 18)
    out.append(F(wall, PAPER))
    # mansard roof
    roof = [C(X, 18, Z0), C(X, 18, Z1), C(X - sg * 2.2, 21.6, Z1), C(X - sg * 2.2, 21.6, Z0)]
    out.append(F(roof, PAPER))
    seams = [(C(X, 18, z), C(X - sg * 2.2, 21.6, z)) for z in [Z0 + i * 0.45 for i in range(int((Z1 - Z0) / 0.45) + 1)]]
    out.append(segs(seams, 0.7, seed, 0, op=0.8))
    out.append(H(U, roof, 0, 2.2, 0.7, op=0.6))
    # stone courses
    cl = []
    for yy in [0.9 * i for i in range(1, 20)]:
        cl.append((C(X, yy, Z0), C(X, yy, Z1)))
    out.append(segs(cl, 0.6, seed + 1, 0, op=0.45))
    # windows: four storeys of French windows
    dpat, durl = hpat(U, 80, 2.2, 0.9)
    out.append(dpat)
    wins = []
    bars = []
    z = Z0 + 0.6
    while z + 1.4 < Z1:
        for y0, y1 in ((5.0, 7.7), (8.4, 10.7), (11.3, 13.4), (14.1, 16.3)):
            q = C.qx(X, z + 0.65, z + 1.95, y0, y1)
            wins.append(q)
            if abs(q[0][0] - q[1][0]) > 7:
                bars.append((pt(q[0], q[1], 0.5), pt(q[3], q[2], 0.5)))
                bars.append((pt(q[0], q[3], 0.3), pt(q[1], q[2], 0.3)))
            # pediment / lintel over each window
            a, b = C(X, y1 + 0.35, z + 0.5), C(X, y1 + 0.35, z + 2.1)
            out.append(seg(a[0], a[1], b[0], b[1], 1.0, seed, 0))
        z += bay
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{durl}"/>')
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="none" stroke="{INK}" stroke-width="1.0"/>')
    out.append(segs(bars, 0.9, seed, 0, color=PAPER))
    # balconies (2nd and 5th floors): slab, rail, balusters
    for yb in (5.0, 14.1):
        slab = [C(X, yb, Z0), C(X, yb, Z1), C(X + sg * 0.6, yb, Z1), C(X + sg * 0.6, yb, Z0)]
        out.append(F(slab, INK, 0.85))
        top = [C(X + sg * 0.6, yb + 1.0, Z0), C(X + sg * 0.6, yb + 1.0, Z1)]
        bal = []
        zz = Z0
        while zz < Z1:
            a, b = C(X + sg * 0.6, yb, zz), C(X + sg * 0.6, yb + 1.0, zz)
            if abs(C(X + sg * 0.6, yb, zz + 0.25)[0] - a[0]) > 1.4:
                bal.append((a, b))
            zz += 0.25
        out.append(segs(bal, 0.7, seed, 0))
        out.append(pen(top, 1.3, seed, 0.1))
        out.append(pen([C(X + sg * 0.6, yb + 0.5, Z0), C(X + sg * 0.6, yb + 0.5, Z1)], 0.7, seed, 0.1))
    # cornice
    cor = [C(X, 17.2, Z0), C(X, 17.2, Z1), C(X + sg * 0.5, 18.0, Z1), C(X + sg * 0.5, 18.0, Z0)]
    out.append(F(cor, PAPER) + H(U, cor, 90, 1.8, 0.8))
    out.append(pen([cor[0], cor[1]], 1.2, seed, 0.1) + pen([cor[3], cor[2]], 1.8, seed, 0.1))
    # dormers and chimneys
    z = Z0 + 0.6
    i = 0
    while z + 1.4 < Z1:
        fa = C.qx(X - sg * 0.9, z + 0.55, z + 2.05, 18.3, 20.1)
        if abs(fa[0][0] - fa[1][0]) > 2.5:
            out.append(F(fa, PAPER))
            out.append(F(C.qx(X - sg * 0.9, z + 0.85, z + 1.75, 18.6, 19.8), INK, 0.8))
            pk = C(X - sg * 0.9, 20.9, z + 1.3)
            out.append(F([fa[0], pk, fa[1]], PAPER) + pen([fa[0], pk, fa[1]], 1.1, seed + i, 0.1))
            out.append(sketch(fa, 1.0, seed + i, 0.4))
        if i % 3 == 1:
            ch = C.qx(X - sg * 2.4, z + 1.9, z + 2.6, 21.4, 23.2)
            out.append(F(ch, PAPER) + H(U, ch, 0, 1.6, 0.7) + sketch(ch, 1.1, seed, 0.3))
            for pz in (z + 2.05, z + 2.3, z + 2.5):
                a = C(X - sg * 2.4, 23.2, pz)
                out.append(seg(a[0], a[1], a[0], a[1] - max(1.5, 250 * 0.5 / pz), 1.4, seed, 0))
        z += bay
        i += 1
    # ground floor shops: dark glass between pilasters
    shop = []
    z = Z0 + 0.4
    while z + 1.5 < Z1:
        shop.append(C.qx(X, z + 0.3, z + 2.3, 0.5, 3.8))
        z += bay
    out.append(f'<path d="{" ".join(poly(w) for w in shop)}" fill="{INK}" opacity="0.82"/>')
    out.append(segs([(C(X, 4.4, Z0), C(X, 4.4, Z1)), (C(X, 4.1, Z0), C(X, 4.1, Z1))], 1.0, seed, 0))
    if shade:
        out.append(XH(U, wall + [], 75, 3.0, 0.8, ang2=15, gap2=3.6, op=0.9))
        out.append(H(U, roof, 75, 2.4, 0.8))
    out.append(pen([C(X, 0, Z0), C(X, 0, Z1)], 1.6, seed, 0.1))
    out.append(pen([C(X - sg * 2.2, 21.6, Z0), C(X - sg * 2.2, 21.6, Z1)], 2.0, seed, 0.1))
    out.append(pen([C(X + sg * 0.5, 18.0, Z1), C(X, 18, Z1), C(X - sg * 2.2, 21.6, Z1)], 1.6, seed, 0.1))
    out.append(pen([C(X, 0, Z1), C(X, 17.2, Z1)], 2.0, seed, 0.1))
    return "".join(out)


@design("paris")
def paris(U):
    """A Left Bank street at morning: café awning, Haussmann façades, plane trees, the Tower at the end."""
    out = [ground_paper(U, 21)]
    C = Cam(f=250, cx=300, vpy=352, eye=1.6)
    art = []
    art.append(cloud(U, 420, 112, 96, 18, 5))
    art.append(cloud(U, 196, 150, 74, 13, 8))
    art.append(eiffel(U, 300, 72, 352, 7))
    # Champ de Mars trees at the foot of the tower
    for i, x in enumerate(range(236, 372, 15)):
        art.append(lobe(U, x + (i % 2) * 4, 330 - (i % 3) * 4, 13, 11, 300 + i, light=(1, -1), w=1.1, dense=1.2))
    art.append(seg(220, 352, 380, 352, 1.4, 3, 0))
    # street surface
    road = [C(-6.5, 0, 6), C(-6.5, 0, 46), C(6.5, 0, 46), C(6.5, 0, 6)]
    art.append(F(road, PAPER))
    art.append(clipped(U("rd"), poly(road), cobbles(U, C, -6.5, 6.5, 6, 46, 4, row=0.45, stone=0.55, w=0.7, op=0.6)))
    for sx in (-1, 1):
        walk = [C(sx * 6.5, 0.15, 6), C(sx * 6.5, 0.15, 46), C(sx * 9, 0.15, 46), C(sx * 9, 0.15, 6)]
        art.append(F(walk, PAPER))
        flags = [(C(sx * 6.5, 0.15, z), C(sx * 9, 0.15, z)) for z in [6 + i * 1.2 for i in range(34)]]
        art.append(segs(flags, 0.6, 5, 0, op=0.6))
        art.append(pen([C(sx * 6.5, 0.15, 6), C(sx * 6.5, 0.15, 46)], 1.6, 6, 0.1))
        art.append(pen([C(sx * 6.5, 0, 6), C(sx * 6.5, 0, 46)], 1.0, 7, 0.1))
    art.append(H(U, [C(6.5, 0, 6), C(6.5, 0, 46), C(2, 0, 46), C(1, 0, 6)], 75, 3.2, 0.7, op=0.6))
    # façades
    art.append(haussmann(U, C, -9, 6.5, 46, 31))
    art.append(haussmann(U, C, 9, 6.5, 46, 41, shade=True))
    # trees on the right pavement, far to near
    for z, sd in ((33, 3), (21, 2), (11.5, 1)):
        x, yb = C(7.4, 0, z)
        r = 250 * 2.9 / z
        art.append(tree(U, x, yb, 250 * 8.2 / z, r * 2, 500 + sd, light=(-1, -1), trunk_h=0.42, lobes=6,
                        lw=max(1.1, min(2.0, r / 30)), dense=1.0))
    # café awning (the vermilion accent) on the left
    Za, Zb = 8.6, 22.5
    aw = [C(-9, 4.3, Za), C(-9, 4.3, Zb), C(-7.0, 3.3, Zb), C(-7.0, 3.3, Za)]
    art.append(F(aw, PAPER))
    stripes = []
    z = Za
    k = 0
    while z < Zb - 0.01:
        z2 = min(Zb, z + 0.5)
        if k % 2 == 0:
            stripes.append(poly([C(-9, 4.3, z), C(-9, 4.3, z2), C(-7.0, 3.3, z2), C(-7.0, 3.3, z)]))
            stripes.append(poly([C(-7.0, 3.3, z), C(-7.0, 3.3, z2), C(-7.0, 2.85, z2), C(-7.0, 2.85, z)]))
        z = z2
        k += 1
    sd = " ".join(stripes)
    b = bbox(aw + [C(-7.0, 2.85, Za)])
    art.append(accent(U, sd, b, 3, op=0.95, ang=-60, n=30, length=(8, 22), width=(1.5, 3)))
    art.append(H(U, sd, 30, 2.6, 0.8, box=b, op=0.6))
    val = [C(-7.0, 3.3, Za), C(-7.0, 3.3, Zb), C(-7.0, 2.85, Zb), C(-7.0, 2.85, Za)]
    sc = []
    z = Za
    while z < Zb:
        a, bb_ = C(-7.0, 2.85, z), C(-7.0, 2.85, min(Zb, z + 0.5))
        sc.append(f"Q {f1((a[0] + bb_[0]) / 2)} {f1(a[1] + (bb_[0] - a[0]) * 0.35 + 1)} {f1(bb_[0])} {f1(bb_[1])}")
        z += 0.5
    a0 = C(-7.0, 2.85, Za)
    art.append(P(f"M {f1(a0[0])} {f1(a0[1])} " + " ".join(sc), 1.3))
    art.append(sketch(aw, 1.8, 9, 1.0) + pen([val[0], val[3]], 1.4, 10, 0.1))
    # café tables and chairs under the awning, a few people
    for i, z in enumerate((9.6, 12.2, 15.0, 18.0, 21.0)):
        tx_, ty_ = C(-7.6, 0.76, z)
        bx_, by_ = C(-7.6, 0.0, z)
        r = 250 * 0.33 / z
        art.append(f'<ellipse cx="{f1(tx_)}" cy="{f1(ty_)}" rx="{f1(r)}" ry="{f1(r * 0.3)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>')
        art.append(seg(tx_, ty_, bx_, by_, 1.4, i, 0) + seg(bx_ - r * 0.5, by_, bx_ + r * 0.5, by_, 1.2, i, 0))
        for dz, sgn in ((-0.45, -1), (0.45, 1)):
            cxp, cyp = C(-7.6, 0.45, z + dz)
            cb = C(-7.6, 0.0, z + dz)
            ch = 250 * 0.45 / (z + dz)
            art.append(P(f"M {f1(cxp - ch * 0.3)} {f1(cyp)} L {f1(cxp + ch * 0.3)} {f1(cyp)} M {f1(cxp + sgn * ch * 0.3)} {f1(cyp)} "
                         f"L {f1(cxp + sgn * ch * 0.35)} {f1(cyp - ch * 0.9)} M {f1(cxp - ch * 0.25)} {f1(cyp)} L {f1(cxp - ch * 0.3)} {f1(cb[1])} "
                         f"M {f1(cxp + ch * 0.25)} {f1(cyp)} L {f1(cxp + ch * 0.3)} {f1(cb[1])}", max(0.9, ch * 0.07)))
        if i in (0, 2, 3):
            px_, py_ = C(-7.6, 0.45, z + 0.45)
            hh = 250 * 1.25 / (z + 0.45)
            art.append(F(smooth_closed([(px_ - hh * 0.12, py_), (px_ + hh * 0.12, py_), (px_ + hh * 0.1, py_ - hh * 0.55),
                                        (px_ - hh * 0.1, py_ - hh * 0.55)]), INK, 0.95))
            art.append(f'<circle cx="{f1(px_)}" cy="{f1(py_ - hh * 0.68)}" r="{f1(hh * 0.1)}" fill="{INK}"/>')
    # lamps
    for X, z in ((-6.9, 26), (6.9, 16.5)):
        x, yb = C(X, 0, z)
        art.append(lamp(x, yb, 250 * 4.6 / z, 77, "lantern", max(1.2, 30 / z)))
    # pedestrians and a cyclist
    for X, z, sd, fl in ((-8.0, 31, 1, False), (-7.9, 38, 2, True), (7.8, 27, 3, True), (7.9, 13.5, 4, False)):
        x, yb = C(X, 0.15, z)
        art.append(person(x, yb, 250 * 1.72 / z, 80 + sd, flip=fl, bag=sd == 4))
    x, yb = C(1.4, 0, 15)
    art.append(cyclist(x, yb, 250 * 1.75 / 15, 90))
    x, yb = C(-1.2, 0, 34)
    art.append(car(U, x, yb, 250 * 4.0 / 34, 91, flip=True))
    # birds over the street
    art.append(bird(352, 168, 7, 92) + bird(370, 150, 5, 93) + bird(250, 196, 5, 94))
    out.append(soft_frame(U, 300, 252, 262, 222, 5, "".join(art), expo=3.4, inset=0.24))
    out.append(T(300, 503, "Paris", DMS, name_size("Paris")))
    out.append(coords_line(300, 534, CITIES["paris"][1], rule_len=30, diamonds=True))
    out.append(finish(U))
    return "".join(out)



# ================================================================ LONDON
def gothic_panel(x0, x1, y0, y1, n, w=0.8):
    """Rows of narrow pointed lancet panels between x0..x1 (tracery on a Gothic Revival wall)."""
    d = []
    pw = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * pw + pw * 0.18, x0 + (i + 1) * pw - pw * 0.18
        m = (a + b) / 2
        ah = (b - a) * 0.9
        d.append(f"M {f1(a)} {f1(y1)} L {f1(a)} {f1(y0 + ah)} Q {f1(a)} {f1(y0 + ah * 0.3)} {f1(m)} {f1(y0)} "
                 f"Q {f1(b)} {f1(y0 + ah * 0.3)} {f1(b)} {f1(y0 + ah)} L {f1(b)} {f1(y1)}")
    return P(" ".join(d), w)


def elizabeth_tower(U, cx, base, top, hw, seed=1):
    """Elizabeth Tower (the clock tower at Westminster) in elevation, light from the left."""
    H_ = base - top
    y = lambda f: base - H_ * f             # f = fraction of height (0 base, 1 finial)
    out = []
    # shaft
    sh = [(cx - hw, y(0.585)), (cx + hw, y(0.585)), (cx + hw, base), (cx - hw, base)]
    out.append(F(sh, PAPER))
    # corner buttresses and recessed panels
    bw = hw * 0.22
    for yy0, yy1 in ((0.585, 0.43), (0.43, 0.28), (0.28, 0.14), (0.14, 0.0)):
        out.append(gothic_panel(cx - hw + bw, cx + hw - bw, y(yy0) + 3, y(yy1) - 2, 4, 0.8))
        out.append(seg(cx - hw, y(yy1), cx + hw, y(yy1), 1.2, seed, 0.1))
        out.append(seg(cx - hw, y(yy1) - 2.2, cx + hw, y(yy1) - 2.2, 0.7, seed, 0.1))
    out.append(H(U, [(cx + hw * 0.45, y(0.585)), (cx + hw, y(0.585)), (cx + hw, base), (cx + hw * 0.45, base)], 90, 1.9, 0.8))
    out.append(H(U, [(cx + hw - bw, y(0.585)), (cx + hw, y(0.585)), (cx + hw, base), (cx + hw - bw, base)], 20, 2.0, 0.8))
    out.append(segs([((cx - hw + bw, y(0.585)), (cx - hw + bw, base)), ((cx + hw - bw, y(0.585)), (cx + hw - bw, base))], 1.0, seed, 0.1))
    out.append(pen([(cx - hw, y(0.585)), (cx - hw, base)], 2.4, seed, 0.2) + pen([(cx + hw, y(0.585)), (cx + hw, base)], 2.8, seed + 1, 0.2))
    # clock stage (slightly wider)
    cw = hw * 1.12
    c0, c1 = y(0.69), y(0.585)
    cs = [(cx - cw, c0), (cx + cw, c0), (cx + cw, c1), (cx - cw, c1)]
    out.append(F(cs, PAPER))
    out.append(H(U, cs, 45, 2.0, 0.8))
    out.append(H(U, [(cx + cw * 0.6, c0), (cx + cw, c0), (cx + cw, c1), (cx + cw * 0.6, c1)], -45, 2.0, 0.8))
    r = min(cw * 0.78, (c1 - c0) * 0.42)
    ccx, ccy = cx, (c0 + c1) / 2
    out.append(f'<circle cx="{f1(ccx)}" cy="{f1(ccy)}" r="{f1(r + 2.5)}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<circle cx="{f1(ccx)}" cy="{f1(ccy)}" r="{f1(r - 3)}" fill="none" stroke="{INK}" stroke-width="0.8"/>')
    tk = []
    for i in range(12):
        a = i * math.pi / 6
        tk.append(((ccx + math.cos(a) * (r - 3), ccy + math.sin(a) * (r - 3)), (ccx + math.cos(a) * (r + 1), ccy + math.sin(a) * (r + 1))))
    out.append(segs(tk, 1.6, seed, 0))
    # tracery rose inside the dial
    out.append(P(" ".join(f"M {f1(ccx)} {f1(ccy)} L {f1(ccx + math.cos(i * math.pi / 6 + 0.26) * (r - 4))} {f1(ccy + math.sin(i * math.pi / 6 + 0.26) * (r - 4))}" for i in range(12)), 0.5, INK, 0.6))
    out.append(P(f"M {f1(ccx)} {f1(ccy)} L {f1(ccx + r * 0.42)} {f1(ccy + r * 0.12)} M {f1(ccx)} {f1(ccy)} L {f1(ccx - r * 0.12)} {f1(ccy - r * 0.68)}", 1.9))
    out.append(f'<circle cx="{f1(ccx)}" cy="{f1(ccy)}" r="1.6" fill="{INK}"/>')
    out.append(sketch(cs, 2.2, seed + 2, 1.2))
    for yy in (c0 - 2, c0 - 5):
        out.append(seg(cx - cw - 2, yy, cx + cw + 2, yy, 1.3, seed, 0))
    # belfry with three pointed openings
    b0, b1 = y(0.775), c0 - 5
    bf = [(cx - hw, b0), (cx + hw, b0), (cx + hw, b1), (cx - hw, b1)]
    out.append(F(bf, PAPER))
    ow = 2 * hw / 3
    for i in range(3):
        a, b = cx - hw + i * ow + ow * 0.2, cx - hw + (i + 1) * ow - ow * 0.2
        m = (a + b) / 2
        op_ = [(a, b1 - 2), (a, b0 + (b - a) * 1.2), (m, b0 + 3), (b, b0 + (b - a) * 1.2), (b, b1 - 2)]
        out.append(F(op_, INK, 0.88))
    out.append(H(U, [(cx + hw * 0.5, b0), (cx + hw, b0), (cx + hw, b1), (cx + hw * 0.5, b1)], 90, 1.8, 0.8))
    out.append(sketch(bf, 1.8, seed + 3, 1.0))
    # corner pinnacles and the gable band
    for sx in (-1, 1):
        px = cx + sx * (hw + 1)
        out.append(F([(px - 3, b0), (px, b0 - H_ * 0.06), (px + 3, b0)], PAPER) + pen([(px - 3, b0), (px, b0 - H_ * 0.06), (px + 3, b0)], 1.3, seed, 0.1))
    gl = []
    for i in range(5):
        a = cx - hw + i * hw * 2 / 5
        b = a + hw * 2 / 5
        gl.append((a, b0))
        gl.append(((a + b) / 2, b0 - 6))
    gl.append((cx + hw, b0))
    out.append(F(gl + [(cx + hw, b0 + 1), (cx - hw, b0 + 1)], PAPER) + pen(gl, 1.2, seed, 0.1))
    # spire roof: steep, with lucarnes, hatched
    r0, r1 = y(0.775) - 2, y(0.93)
    roof = [(cx - hw * 0.92, r0), (cx - hw * 0.34, r1), (cx + hw * 0.34, r1), (cx + hw * 0.92, r0)]
    out.append(F(roof, PAPER))
    out.append(H(U, roof, 90, 2.2, 0.8, span=(0.0, 1)))
    out.append(H(U, [(cx, r0), (cx + hw * 0.92, r0), (cx + hw * 0.34, r1), (cx, r1)], 60, 2.0, 0.8))
    for i, f in enumerate((0.25, 0.55)):
        ly = lerp(r0, r1, f)
        lw = lerp(hw * 0.92, hw * 0.34, f) * 0.45
        luc = [(cx - lw, ly + 8), (cx - lw, ly), (cx, ly - 7), (cx + lw, ly), (cx + lw, ly + 8)]
        out.append(F(luc, PAPER) + F([(cx - lw * 0.4, ly + 8), (cx - lw * 0.4, ly + 1), (cx, ly - 2), (cx + lw * 0.4, ly + 1), (cx + lw * 0.4, ly + 8)], INK, 0.85)
                   + pen(luc, 1.1, seed + i, 0.1))
    out.append(sketch(roof, 2.0, seed + 4, 0.8, closed=False))
    # lantern + flèche + finial
    l0 = y(0.965)
    ln = [(cx - hw * 0.34, l0), (cx + hw * 0.34, l0), (cx + hw * 0.34, r1), (cx - hw * 0.34, r1)]
    out.append(F(ln, PAPER) + segs([((cx + i * hw * 0.17, l0 + 1), (cx + i * hw * 0.17, r1 - 1)) for i in (-1, 0, 1)], 1.0, seed, 0)
               + sketch(ln, 1.4, seed + 5, 0.6))
    out.append(F([(cx - hw * 0.3, l0), (cx, y(1.0) + 6), (cx + hw * 0.3, l0)], PAPER) + H(U, [(cx, l0), (cx, y(1.0) + 6), (cx + hw * 0.3, l0)], 90, 1.4, 0.7)
               + pen([(cx - hw * 0.3, l0), (cx, y(1.0) + 6), (cx + hw * 0.3, l0)], 1.5, seed, 0.1))
    out.append(seg(cx, y(1.0) + 6, cx, y(1.0) - 2, 1.4, seed, 0) + seg(cx - 3, y(1.0) + 2, cx + 3, y(1.0) + 2, 1.2, seed, 0))
    return "".join(out)


def palace_front(U, x0, x1, base, h, seed, bay=26):
    """The Palace of Westminster's river front, frontal: rhythmic Gothic bays, pavilions, pinnacles."""
    rnd = random.Random(seed)
    top = base - h
    out = []
    body = [(x0, top), (x1, top), (x1, base), (x0, base)]
    out.append(F(body, PAPER))
    # window rows
    rows = [(top + h * 0.12, top + h * 0.3), (top + h * 0.4, top + h * 0.58), (top + h * 0.66, top + h * 0.84)]
    wl = []
    x = x0 + 3
    while x < x1 - 4:
        for a, b in rows:
            wl.append([(x + 1, a + 2), (x + 1, b), (x + 4, b), (x + 4, a + 2), (x + 2.5, a)])
        x += 6
    out.append(f'<path d="{" ".join(poly(w) for w in wl)}" fill="{INK}" opacity="0.8"/>')
    for a, b in rows:
        out.append(seg(x0, b + 1.5, x1, b + 1.5, 0.8, seed, 0.1))
    # pavilions every bay with pinnacles
    x = x1 - bay * 0.5
    i = 0
    pins = []
    while x > x0 - bay:
        pw = 10 if i % 3 == 0 else 6
        ph = h * (0.32 if i % 3 == 0 else 0.16)
        pv = [(x - pw / 2, base), (x - pw / 2, top - ph), (x + pw / 2, top - ph), (x + pw / 2, base)]
        out.append(F(pv, PAPER) + H(U, [(x, top - ph), (x + pw / 2, top - ph), (x + pw / 2, base), (x, base)], 90, 1.6, 0.8))
        out.append(sketch(pv, 1.2, seed + i, 0.6, closed=False))
        for sx in (-1, 1):
            pins.append([(x + sx * pw / 2 - 1.6, top - ph), (x + sx * pw / 2, top - ph - (9 if i % 3 == 0 else 6)), (x + sx * pw / 2 + 1.6, top - ph)])
        if i % 3 == 0:
            pins.append([(x - pw / 2 + 2, top - ph), (x, top - ph - 13), (x + pw / 2 - 2, top - ph)])
        x -= bay
        i += 1
    # small pinnacles along the parapet
    xx = x0 + 3
    while xx < x1:
        pins.append([(xx - 1, top), (xx, top - 4), (xx + 1, top)])
        xx += 6
    out.append(f'<path d="{" ".join(poly(p_) for p_ in pins)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"/>')
    out.append(H(U, body, 90, 2.6, 0.7, op=0.5))
    out.append(pen([(x0, top), (x1, top)], 1.8, seed, 0.2))
    # embankment wall
    emb = [(x0, base), (x1, base), (x1, base + 8), (x0, base + 8)]
    out.append(F(emb, PAPER) + H(U, emb, 0, 1.8, 0.8) + pen([(x0, base + 8), (x1, base + 8)], 2.0, seed, 0.2))
    return "".join(out)


def double_decker(U, C, X0, Z0, seed, length=11.0, width=2.5, height=4.4, Yd=0.0):
    """A London double-decker on the road plane, seen from behind/side (vermilion accent)."""
    X1 = X0 + width
    back = [C(X0, Yd + height, Z0), C(X1, Yd + height, Z0), C(X1, Yd + 0.35, Z0), C(X0, Yd + 0.35, Z0)]
    side = [C(X0, Yd + height, Z0), C(X0, Yd + height, Z0 + length), C(X0, Yd + 0.35, Z0 + length), C(X0, Yd + 0.35, Z0)]
    roof = [C(X0, Yd + height, Z0), C(X0, Yd + height, Z0 + length), C(X1, Yd + height, Z0 + length), C(X1, Yd + height, Z0)]
    out = [F(side, PAPER), F(back, PAPER), F(roof, PAPER)]
    d = poly(side) + " " + poly(back)
    out.append(accent(U, d, bbox(side + back), seed, op=0.95, n=18, length=(6, 16), width=(1.5, 3)))
    # windows: upper and lower deck bands
    for (a, b) in ((2.65, 3.95), (1.15, 2.3)):
        out.append(F(quad_sub(side, 0.04, 1 - b / height, 0.96, 1 - a / height), INK, 0.85))
        out.append(F(quad_sub(back, 0.12, 1 - b / height, 0.88, 1 - a / height), INK, 0.85))
        m = homog(side)
        out.append(segs([(m(u, 1 - b / height), m(u, 1 - a / height)) for u in (0.2, 0.4, 0.6, 0.8)], 0.9, seed, 0, color=PAPER))
    out.append(H(U, back, 0, 1.6, 0.6, span=(0.0, 1), op=0.55))
    for q in (side, back, roof):
        out.append(sketch(q, 1.3, seed, 0.5))
    for u in (0.18, 0.82):
        wx, wy = C(X0 - 0.02, Yd + 0.45, Z0 + u * length)
        rr = 0.5 * C.f / (Z0 + u * length)
        out.append(f'<ellipse cx="{f1(wx)}" cy="{f1(wy)}" rx="{f1(rr * 0.55)}" ry="{f1(rr)}" fill="{INK}"/>')
    return "".join(out)


@design("london")
def london(U):
    """Westminster from the bridge: the clock tower, the long Gothic river front, a red bus, the Thames."""
    out = [ground_paper(U, 31)]
    C = Cam(f=735, cx=360, vpy=315, eye=12)
    pic = [(56, 56), (544, 56), (544, 468), (56, 468)]
    art = []
    # London sky: piled clouds with hatched undersides
    art.append(cloud(U, 150, 112, 150, 30, 11))
    art.append(cloud(U, 250, 160, 110, 20, 12))
    art.append(cloud(U, 500, 150, 120, 24, 13))
    art.append(cloud(U, 470, 92, 70, 14, 14))
    art.append(bird(250, 214, 7, 15) + bird(268, 200, 5, 16) + bird(470, 220, 6, 17))
    # river front of the Palace, left of the tower
    WATER = 350
    art.append(palace_front(U, 40, 372, WATER - 8, 74, 21))
    # Elizabeth Tower
    art.append(elizabeth_tower(U, 392, WATER - 4, 66, 22, 22))
    # the bridge, receding toward the tower's foot
    Zn, Zf = 30.0, 250.0
    deck = [C(12, 10, Zn), C(12, 10, Zf), C(38, 10, Zf), C(38, 10, Zn)]
    art.append(F(deck, PAPER))
    art.append(H(U, deck, 0, 3.0, 0.7, op=0.6))
    face = [C(12, 10.2, Zn), C(12, 10.2, Zf), C(12, 0, Zf), C(12, 0, Zn)]
    # arches cut into the visible side face
    arches = []
    spans = [(30, 62), (68, 100), (106, 138), (144, 174), (180, 208), (214, 238)]
    for z0, z1 in spans:
        pts3 = [C(12, 0, z0)]
        for k in range(1, 12):
            t = k / 12
            zz = lerp(z0, z1, t)
            yy = 6.6 * math.sin(math.pi * t) ** 0.6
            pts3.append(C(12, yy, zz))
        pts3.append(C(12, 0, z1))
        arches.append(pts3)
    art.append(F(face, PAPER))
    art.append(clipped(U("bf"), poly(face), "".join(
        [H(U, face, 0, 2.6, 0.8, op=0.7)] + [F(a, INK, 0.92) for a in arches])))
    art.append(clipped(U("bf2"), poly(face), "".join(pen(a, 1.3, 30 + i, 0.1, smooth=True) for i, a in enumerate(arches))))
    # cutwaters on the piers
    for z0, z1 in zip([s_[1] for s_ in spans[:-1]], [s_[0] for s_ in spans[1:]]):
        a, b = C(12, 0, z0), C(12, 3.5, (z0 + z1) / 2)
        art.append(seg(b[0], b[1], b[0], a[1], 1.0, 33, 0))
    # parapet with balusters + Gothic lamps
    par_top = [C(12, 11.2, Zn), C(12, 11.2, Zf)]
    par = [C(12, 11.2, Zn), C(12, 11.2, Zf), C(12, 10.2, Zf), C(12, 10.2, Zn)]
    art.append(F(par, PAPER))
    bal = []
    z = Zn
    while z < Zf:
        a, b = C(12, 10.25, z), C(12, 11.1, z)
        if C(12, 10.25, z + 0.6)[0] - a[0] < -1.5:
            bal.append((a, b))
        z += 0.6
    art.append(segs(bal, 0.8, 34, 0))
    art.append(pen(par_top, 1.8, 35, 0.2) + pen([C(12, 10.2, Zn), C(12, 10.2, Zf)], 2.2, 36, 0.2))
    art.append(pen([C(38, 11.2, Zn), C(38, 11.2, Zf)], 1.2, 37, 0.2, op=0.8))
    for z in (36, 58, 84, 114, 150, 196):
        x, yb = C(12.2, 11.2, z)
        hh = 735 * 5.5 / z
        art.append(nib([(x, yb), (x, yb - hh * 0.6), (x, yb - hh * 0.82)], max(1.4, hh * 0.05), taper=(1.3, 0.8), seed=z, color=INK))
        for sx in (-1, 0, 1):
            lx_, ly_ = x + sx * hh * 0.13, yb - hh * (0.9 if sx == 0 else 0.8)
            rr = max(1.2, hh * 0.045)
            art.append(f'<rect x="{f1(lx_ - rr)}" y="{f1(ly_ - rr * 2.2)}" width="{f1(rr * 2)}" height="{f1(rr * 2.6)}" fill="{PAPER}" stroke="{INK}" stroke-width="{max(0.8, rr * 0.5):.1f}"/>')
        art.append(seg(x - hh * 0.13, yb - hh * 0.74, x + hh * 0.13, yb - hh * 0.74, max(1.0, hh * 0.03), z, 0))
    # traffic: the bus (accent) and a black cab
    art.append(double_decker(U, C, 16.5, 52, 38, Yd=10))
    cx_, cy_ = C(22, 10, 118)
    art.append(F([(cx_ - 7, cy_), (cx_ - 6, cy_ - 7), (cx_ + 5, cy_ - 7), (cx_ + 7, cy_)], INK, 0.9))
    art.append(person(*C(14, 10, 70), 735 * 1.7 / 70, 39) + person(*C(14.6, 10, 96), 735 * 1.7 / 96, 40, flip=True))
    # the Thames
    art.append(ripples(U, 56, 544, WATER, 470, 41, dens=1.1, refl=[(370, 414, 0.9), (60, 372, 0.35)], skip=[(150, 190)],
                       clip=poly([(56, WATER), (C(12, 0, Zf)[0], WATER), C(12, 0, Zn), (56, 470)])))
    # a river boat
    bx, by = 172, 404
    hull = [(bx - 46, by), (bx + 40, by), (bx + 30, by + 10), (bx - 42, by + 10)]
    cabin = [(bx - 34, by), (bx - 34, by - 12), (bx + 22, by - 12), (bx + 22, by)]
    art.append(F(hull, PAPER) + H(U, hull, 0, 1.8, 0.8) + sketch(hull, 1.8, 42, 0.8))
    art.append(F(cabin, PAPER) + facade(U, [(bx - 32, by - 10), (bx + 20, by - 10), (bx + 20, by - 3), (bx - 32, by - 3)], 9, 1, "dark", 43, mx=0.15, my=0.1)
               + sketch(cabin, 1.4, 44, 0.6) + seg(bx - 38, by - 13, bx + 26, by - 13, 1.6, 45, 0))
    art.append(P(f"M {bx + 40} {by + 4} q 20 2 46 8 M {bx + 34} {by + 10} q 18 4 40 12", 1.0, INK, 0.8))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 46, 1.4))
    out.append(border(U, 47, 47, 553, 553, 47, double=False, w=(1.2, 1.2)))
    # ribbon title straddling the foot of the picture, coordinates below
    from kitchen_ink import ribbon
    sz = name_size("London", 300, 60)
    out.append(ribbon(U("rb"), 300, 466, 300, 62, "London", DMS, sz, fill=PAPER, color=INK, bend=6, seed=48, text_dy=sz * 0.36))
    out.append(coords_line(300, 534, CITIES["london"][1], rule_len=26))
    out.append(finish(U))
    return "".join(out)


# ================================================================ build
def main(slugs):
    for slug, fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save(COL, slug, fn(Ids(slug)))
        print("wrote", slug)


if __name__ == "__main__":
    main(sys.argv[1:])
