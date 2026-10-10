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

COL = "city-sketches"   # line-art set; the engraved Paris lives in ink-cities
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


def cartouche(U, slug, cx, cy, w, h, seed=3, mx=NAME_MAX, notch=10, name_k=0.12, cgap=32):
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
    ny = cy + sz * name_k
    out.append(T(cx, ny, name, DMS, sz))
    out.append(coords_line(cx, ny + cgap, coords, rules=True, rule_len=22, gap=12))
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


# ================================================================ shared pieces for the American plates
def prism(U, x0, x1, sw, top, base, seed, cols=None, rows=None, style="pane", side_style=None, dark_p=0.2, w=1.5,
          side_dy=0.0, wop=1.0, my=0.22):
    """A tower seen nearly face-on: a lit front face x0..x1 and a narrow hatched side face x1..x1+sw (light from
    the left)."""
    out = []
    front = [(x0, top), (x1, top), (x1, base), (x0, base)]
    c = cols or max(2, int((x1 - x0) / 6))
    r = rows or max(3, int((base - top) / 7))
    out.append(F(front, PAPER))
    out.append(facade(U, [(x0 + 1.5, top + 3), (x1 - 1.5, top + 3), (x1 - 1.5, base), (x0 + 1.5, base)], c, r, style, seed,
                      dark_p=dark_p, w=0.8, op=wop, my=my))
    if sw:
        side = [(x1, top), (x1 + sw, top + side_dy), (x1 + sw, base), (x1, base)]
        out.append(F(side, PAPER))
        out.append(facade(U, [(x1 + 1, top + 3 + side_dy), (x1 + sw - 1, top + 3 + side_dy), (x1 + sw - 1, base), (x1 + 1, base)],
                          max(1, int(sw / 5)), r, side_style or style, seed + 1, dark_p=0.5, w=0.7, op=wop, my=my))
        out.append(H(U, side, 90, 1.7, 0.8, wob=0.1, brk=0))
        out.append(sketch(side, w * 0.9, seed + 2, 0.8))
    out.append(sketch(front, w, seed + 3, 1.0))
    return "".join(out)


def dogwood(U, cx, cy, r, rot, seed, w=1.5):
    """A dogwood blossom: four notched bracts round a knot of tiny florets."""
    rnd = random.Random(seed)
    out = []
    for k in range(4):
        a = math.radians(rot + k * 90 + rnd.uniform(-8, 8))
        ca, sa = math.cos(a), math.sin(a)
        L = r * rnd.uniform(0.9, 1.08)
        Wd = r * 0.56

        def p(u, v):
            return (cx + ca * u - sa * v, cy + sa * u + ca * v)
        pts = [p(r * 0.12, 0), p(L * 0.45, -Wd * 0.62), p(L * 0.92, -Wd * 0.42), p(L * 0.95, -Wd * 0.1), p(L * 0.84, 0),
               p(L * 0.95, Wd * 0.1), p(L * 0.92, Wd * 0.42), p(L * 0.45, Wd * 0.62)]
        d = smooth_closed(pts)
        out.append(F(d, PAPER))
        veins = [(p(r * 0.2, 0), p(L * 0.78, 0)), (p(r * 0.3, 0), p(L * 0.7, -Wd * 0.3)), (p(r * 0.3, 0), p(L * 0.7, Wd * 0.3))]
        out.append(segs(veins, 0.7, seed + k, 0.5, op=0.8))
        out.append(H(U, d, math.degrees(a) + 90, 2.0, 0.6, span=(0.6, 1), dark=p(L * 0.5, Wd), wob=0.2, brk=0,
                     box=bbox(pts, 2)))
        out.append(P(d, w))
        notch = [p(L * 0.95, -Wd * 0.1), p(L * 0.84, 0), p(L * 0.95, Wd * 0.1)]
        out.append(F(notch + [p(L * 0.9, 0)], INK, 0.85))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.2)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>')
    dots = []
    for i in range(9):
        a, rr = rnd.uniform(0, 6.3), r * 0.13 * math.sqrt(rnd.random())
        dots.append(f'<circle cx="{f1(cx + math.cos(a) * rr)}" cy="{f1(cy + math.sin(a) * rr)}" r="{rnd.uniform(0.8, 1.4):.2f}"/>')
    out.append(f'<g fill="{INK}">{"".join(dots)}</g>')
    return "".join(out)


def twig(pts, w=2.0, seed=1):
    return nib(pts, w, taper=(1, 0.25), ramp=0.5, seed=seed, color=INK)


def duck(x, y, s, seed=1, flip=False):
    """A small duck afloat, drawn in a few strokes, with its own ring of ripples."""
    k = -1 if flip else 1
    body = [(x - k * s, y - s * 0.15), (x - k * s * 0.6, y - s * 0.55), (x + k * s * 0.3, y - s * 0.5), (x + k * s * 0.55, y - s * 0.8),
            (x + k * s * 0.7, y - s * 1.15), (x + k * s * 0.95, y - s * 1.2), (x + k * s * 1.05, y - s * 1.0), (x + k * s * 0.85, y - s * 0.6),
            (x + k * s * 0.95, y - s * 0.2), (x + k * s * 0.6, y), (x - k * s * 0.7, y)]
    out = [F(smooth_closed(body), PAPER), P(smooth_closed(body), 1.3)]
    out.append(F(smooth_closed([(x - k * s * 0.6, y - s * 0.12), (x + k * s * 0.5, y - s * 0.12), (x + k * s * 0.4, y), (x - k * s * 0.5, y)]), INK, 0.85))
    out.append(P(f"M {f1(x - k * s * 0.45)} {f1(y - s * 0.4)} Q {f1(x)} {f1(y - s * 0.55)} {f1(x + k * s * 0.35)} {f1(y - s * 0.32)}", 0.9))
    out.append(F([(x + k * s * 1.02, y - s * 1.08), (x + k * s * 1.38, y - s * 1.0), (x + k * s * 1.02, y - s * 0.92)], INK))
    out.append(f'<circle cx="{f1(x + k * s * 0.85)}" cy="{f1(y - s * 1.0)}" r="{f1(max(0.8, s * 0.08))}" fill="{INK}"/>')
    out.append(P(f"M {f1(x - k * s * 1.6)} {f1(y + 2)} q {f1(k * s)} 2 {f1(k * s * 2)} 0 M {f1(x + k * s * 0.6)} {f1(y + 3)} "
                 f"q {f1(k * s * 0.6)} 1.5 {f1(k * s * 1.4)} 0", 1.0, INK, 0.85))
    return "".join(out)


def kite(U, x, y, s, seed, tail_to):
    """A diamond kite in the vermilion accent, with a bowed tail and a long string."""
    pts = [(x, y - s), (x + s * 0.62, y - s * 0.15), (x, y + s * 0.95), (x - s * 0.62, y - s * 0.15)]
    out = [F(pts, PAPER), accent(U, poly(pts), bbox(pts), seed, op=0.95, ang=-60, n=14, length=(6, 14), width=(1.5, 3))]
    out.append(F([pts[0], pts[1], (x, y - s * 0.15)], INK, 0.25) + F([(x, y - s * 0.15), pts[3], pts[2]], INK, 0.18))
    out.append(segs([(pts[0], pts[2]), (pts[1], pts[3])], 1.0, seed, 0.2))
    out.append(sketch(pts, 1.6, seed, 0.6))
    # tail with little bows
    tx, ty = tail_to
    tail = [(x, y + s * 0.95), (x + (tx - x) * 0.3 + 8, y + s + (ty - y) * 0.3), (x + (tx - x) * 0.65 - 6, y + s + (ty - y) * 0.6), (tx, ty)]
    out.append(pen(tail, 1.0, seed, 0.3, smooth=True))
    C_ = cr(tail, False, 3)
    for i in (len(C_) // 4, len(C_) // 2, 3 * len(C_) // 4):
        bx, by = C_[i]
        out.append(F([(bx - 4, by - 2.5), (bx, by), (bx - 4, by + 2.5)], INK, 0.85) + F([(bx + 4, by - 2.5), (bx, by), (bx + 4, by + 2.5)], INK, 0.85))
    return "".join(out)


def bench(x, y, L, seed=1):
    """A park bench, side-on."""
    return (segs([((x, y - L * 0.22), (x + L, y - L * 0.22)), ((x, y - L * 0.27), (x + L, y - L * 0.27)),
                  ((x + L * 0.02, y - L * 0.4), (x + L * 0.98, y - L * 0.4)), ((x + L * 0.02, y - L * 0.47), (x + L * 0.98, y - L * 0.47))], 1.4, seed, 0.1)
            + segs([((x + L * 0.1, y - L * 0.22), (x + L * 0.08, y)), ((x + L * 0.9, y - L * 0.22), (x + L * 0.92, y)),
                    ((x + L * 0.1, y - L * 0.22), (x + L * 0.1, y - L * 0.5)), ((x + L * 0.9, y - L * 0.22), (x + L * 0.9, y - L * 0.5))], 1.8, seed + 1, 0))


def arch_window_pts(x0, x1, top, bot, spring=0.42, n=10):
    """Points of a round-topped (elliptical-headed) picture window."""
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    ys = top + (bot - top) * spring
    ry = ys - top
    pts = [(x0, bot), (x0, ys)]
    for i in range(1, n):
        a = math.pi - math.pi * i / n
        pts.append((cx + rx * math.cos(a), ys - ry * math.sin(a)))
    pts += [(x1, ys), (x1, bot)]
    return pts


# ================================================================ ATLANTA
@design("atlanta")
def atlanta(U):
    """Midtown from Piedmont Park: the skyline across Lake Clara Meer under a tall park oak, a dock, ducks, a kite
    (the vermilion accent), framed in an arch-topped window with dogwood blossoms in the spandrels."""
    out = [ground_paper(U, 41)]
    win = arch_window_pts(66, 534, 62, 430, spring=0.36, n=40)
    art = []
    SHORE = 318
    # sky: sparse engraved rules low on the horizon only, two clouds
    sky = []
    y = 210
    while y < SHORE:
        sky.append(((60, y), (540, y)))
        y += lerp(9, 3.4, (y - 210) / (SHORE - 210))
    art.append(segs(sky, 0.6, 3, 0.15, op=0.45))
    art.append(cloud(U, 440, 150, 120, 22, 4))
    art.append(cloud(U, 168, 118, 92, 16, 9))
    art.append(cloud(U, 330, 92, 60, 11, 12, shade=False))
    # -- far, pale towers (back row)
    back = []
    for i, (a, b, t) in enumerate(((112, 134, 262), (138, 156, 246), (196, 214, 238), (282, 300, 226), (344, 362, 236),
                                   (424, 444, 222), (450, 470, 248), (500, 520, 258))):
        back.append(prism(U, a, b, 4, t, SHORE, 100 + i, style="grid", dark_p=0.1, w=1.0))
    art.append("".join(F([(a, t), (b + 4, t), (b + 4, SHORE), (a, SHORE)], PAPER) for a, b, t in
                       ((112, 134, 262), (138, 156, 246), (196, 214, 238), (282, 300, 226), (344, 362, 236), (424, 444, 222),
                        (450, 470, 248), (500, 520, 258))))
    art.append(f'<g opacity="0.5">{"".join(back)}</g>')
    # -- Bank of America Plaza (tallest; open lattice pyramid and spire)
    bx0, bx1, btop = 372, 404, 160
    art.append(prism(U, bx0, bx1, 9, btop, SHORE, 11, cols=5, rows=26, style="slit"))
    # chamfered shoulders + lattice pyramid
    shoulder = [(bx0, btop), (bx0 + 4, btop - 8), (bx1 + 5, btop - 8), (bx1 + 9, btop)]
    art.append(F(shoulder, PAPER) + sketch(shoulder, 1.3, 12, 0.6, closed=False))
    pyr = [(bx0 + 4, btop - 8), ((bx0 + bx1) / 2 + 2, btop - 52), (bx1 + 5, btop - 8)]
    art.append(F(pyr, PAPER))
    lat = []
    for i in range(1, 7):
        t = i / 7
        ya = lerp(btop - 8, btop - 52, t)
        xa, xb = lerp(bx0 + 4, (bx0 + bx1) / 2 + 2, t), lerp(bx1 + 5, (bx0 + bx1) / 2 + 2, t)
        lat.append(((xa, ya), (xb, ya)))
    for i in range(1, 6):
        u = i / 6
        lat.append(((lerp(bx0 + 4, bx1 + 5, u), btop - 8), ((bx0 + bx1) / 2 + 2, btop - 52)))
    art.append(segs(lat, 0.8, 13, 0))
    art.append(clipped(U("bp"), poly(pyr), H(U, [((bx0 + bx1) / 2 + 2, btop - 52), (bx1 + 5, btop - 8), ((bx0 + bx1) / 2 + 2, btop - 8)], 90, 1.6, 0.7)))
    art.append(sketch(pyr, 1.5, 14, 0.6, closed=False))
    art.append(nib([((bx0 + bx1) / 2 + 2, btop - 52), ((bx0 + bx1) / 2 + 2, btop - 80)], 2.0, taper=(1, 0.2), seed=15, color=INK))
    # -- One Atlantic Center (granite piers, setbacks, Gothic copper pyramid with gables and finial)
    ox0, ox1, otop = 236, 270, 168
    art.append(prism(U, ox0, ox1, 9, otop, SHORE, 21, cols=6, rows=30, style="slit"))
    art.append(segs([((x, otop + 2), (x, SHORE)) for x in (ox0 + 6, ox0 + 12, ox1 - 12, ox1 - 6)], 1.0, 22, 0))
    s1 = [(ox0 + 3, otop), (ox0 + 3, otop - 14), (ox1 - 3, otop - 14), (ox1 - 3, otop)]
    art.append(F(s1, PAPER) + facade(U, [(ox0 + 5, otop - 12), (ox1 - 5, otop - 12), (ox1 - 5, otop - 1), (ox0 + 5, otop - 1)], 5, 2, "slit", 23)
               + H(U, [(ox1 - 10, otop - 14), (ox1 - 3, otop - 14), (ox1 - 3, otop), (ox1 - 10, otop)], 90, 1.6, 0.8) + sketch(s1, 1.4, 24, 0.6))
    rf0 = otop - 14
    roof = [(ox0 + 1, rf0), ((ox0 + ox1) / 2, rf0 - 46), (ox1 - 1, rf0)]
    art.append(F(roof, PAPER) + H(U, [((ox0 + ox1) / 2, rf0 - 46), (ox1 - 1, rf0), ((ox0 + ox1) / 2, rf0)], 90, 1.5, 0.8)
               + H(U, roof, 0, 3.0, 0.6, op=0.7) + sketch(roof, 1.6, 25, 0.6, closed=False))
    gab = []
    for gx in (ox0 + 9, ox1 - 9):
        gab.append([(gx - 5, rf0), (gx, rf0 - 13), (gx + 5, rf0)])
    gab.append([((ox0 + ox1) / 2 - 5, rf0 - 14), ((ox0 + ox1) / 2, rf0 - 28), ((ox0 + ox1) / 2 + 5, rf0 - 14)])
    for g in gab:
        art.append(F(g, PAPER) + pen(g, 1.2, 26, 0.1) + F([(g[0][0] + 3, g[0][1] - 1), (g[1][0], g[1][1] + 5), (g[2][0] - 3, g[2][1] - 1)], INK, 0.8))
    art.append(nib([((ox0 + ox1) / 2, rf0 - 46), ((ox0 + ox1) / 2, rf0 - 70)], 2.2, taper=(1, 0.2), seed=27, color=INK))
    art.append(seg((ox0 + ox1) / 2 - 3, rf0 - 52, (ox0 + ox1) / 2 + 3, rf0 - 52, 1.2, 28, 0))
    # -- 1180 Peachtree (glass tower with its tall sail-like fin)
    px0, px1, ptop = 162, 192, 192
    art.append(prism(U, px0, px1, 7, ptop, SHORE, 31, cols=6, rows=26, style="grid", dark_p=0.12))
    fin = [(px1 - 2, ptop), (px1 - 2, ptop - 50), (px1 + 4, ptop - 50), (px1 + 7, ptop)]
    art.append(F(fin, PAPER) + H(U, fin, 90, 1.4, 0.7) + sketch(fin, 1.4, 32, 0.5))
    art.append(segs([((px0, ptop - 2), (px1 - 2, ptop - 20))], 1.2, 33, 0))
    art.append(F([(px0, ptop), (px0, ptop - 2), (px1 - 2, ptop - 20), (px1 - 2, ptop)], PAPER) + H(U, [(px0, ptop), (px0, ptop - 2), (px1 - 2, ptop - 20), (px1 - 2, ptop)], 0, 2.0, 0.6))
    # -- Promenade II (stepped crown, pyramid, spire)
    qx0, qx1, qtop = 306, 336, 206
    art.append(prism(U, qx0, qx1, 8, qtop, SHORE, 41, cols=5, rows=22, style="pane", dark_p=0.25))
    for k, (dx, h) in enumerate(((3, 9), (6, 8), (9, 7))):
        yy = qtop - sum(hh for _, hh in ((3, 9), (6, 8), (9, 7))[:k])
        st = [(qx0 + dx, yy), (qx0 + dx, yy - h), (qx1 - dx, yy - h), (qx1 - dx, yy)]
        art.append(F(st, PAPER) + H(U, [(qx1 - dx - 6, yy - h), (qx1 - dx, yy - h), (qx1 - dx, yy), (qx1 - dx - 6, yy)], 90, 1.4, 0.7)
                   + sketch(st, 1.2, 42 + k, 0.4))
    cy_ = qtop - 24
    pyr2 = [(qx0 + 11, cy_), ((qx0 + qx1) / 2, cy_ - 20), (qx1 - 11, cy_)]
    art.append(F(pyr2, PAPER) + H(U, [((qx0 + qx1) / 2, cy_ - 20), (qx1 - 11, cy_), ((qx0 + qx1) / 2, cy_)], 90, 1.4, 0.7) + pen(pyr2, 1.3, 45, 0.1))
    art.append(nib([((qx0 + qx1) / 2, cy_ - 20), ((qx0 + qx1) / 2, cy_ - 42)], 1.7, taper=(1, 0.2), seed=46, color=INK))
    # -- mid row of nearer, lower buildings
    mids = [(70, 104, 270, "pane"), (120, 152, 252, "slit"), (204, 232, 262, "pane"), (276, 302, 258, "grid"),
            (346, 368, 250, "pane"), (414, 446, 262, "slit"), (452, 488, 280, "pane"), (494, 540, 246, "grid")]
    for i, (a, b, t, st) in enumerate(mids):
        art.append(prism(U, a, b, 6, t, SHORE, 60 + i, style=st, dark_p=0.22, w=1.3))
    # Westin-like cylinder on the right
    cx_, cr_, ctop = 516, 16, 214
    cyl = [(cx_ - cr_, ctop), (cx_ + cr_, ctop), (cx_ + cr_, SHORE), (cx_ - cr_, SHORE)]
    art.append(F(cyl, PAPER))
    art.append(clipped(U("cy"), poly(cyl), segs([((cx_ - cr_, y_), (cx_ + cr_, y_)) for y_ in range(ctop + 8, SHORE, 4)], 0.7, 70, 0)
                       + H(U, cyl, 90, 1.6, 0.8, span=(0.55, 1), dark=(cx_ + cr_, 300))))
    art.append(f'<ellipse cx="{cx_}" cy="{ctop}" rx="{cr_}" ry="3.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>')
    art.append(F([(cx_ - cr_ - 2, ctop + 6), (cx_ + cr_ + 2, ctop + 6), (cx_ + cr_ + 2, ctop + 12), (cx_ - cr_ - 2, ctop + 12)], INK, 0.85))
    art.append(pen([(cx_ - cr_, ctop), (cx_ - cr_, SHORE)], 1.4, 71, 0.1) + pen([(cx_ + cr_, ctop), (cx_ + cr_, SHORE)], 1.6, 72, 0.1))
    # -- far shore: tree line of scribbled canopies of mixed sizes hiding the tower feet
    rnd = random.Random(7)
    x = 46
    k = 0
    while x < 560:
        r = rnd.uniform(9, 24) if k % 3 else rnd.uniform(16, 26)
        art.append(lobe(U, x, SHORE - r * 0.5 + rnd.uniform(-3, 3), r, r * rnd.uniform(0.62, 0.85), 800 + int(x), light=(-1, -1), w=1.2,
                        dense=0.9))
        x += r * rnd.uniform(0.8, 1.3)
        k += 1
    art.append(F([(50, SHORE), (550, SHORE), (550, SHORE + 6), (50, SHORE + 6)], PAPER))
    art.append(H(U, [(50, SHORE), (550, SHORE), (550, SHORE + 6), (50, SHORE + 6)], 0, 1.6, 0.8))
    art.append(pen([(50, SHORE + 6), (550, SHORE + 6)], 1.8, 73, 0.4))
    # -- Lake Clara Meer
    art.append(ripples(U, 50, 550, SHORE + 7, 432, 74, dens=1.0,
                       refl=[(162, 200, 0.7), (236, 280, 0.8), (372, 414, 0.8), (306, 344, 0.5), (500, 532, 0.5), (66, 104, 0.4)],
                       skip=[(120, 150), (430, 470)]))
    # -- the dock (right): boardwalk on piles with rail, two figures, a lamp
    dk = [(372, 372), (550, 362), (550, 378), (372, 382)]
    art.append(F(dk, PAPER) + H(U, [(372, 377), (550, 370), (550, 378), (372, 382)], 0, 1.4, 0.8))
    art.append(segs([((x_, lerp(372, 362, (x_ - 372) / 178)), (x_ + 2, lerp(382, 378, (x_ - 372) / 178))) for x_ in range(376, 550, 6)], 0.7, 75, 0))
    art.append(pen([(372, 372), (550, 362)], 1.8, 76, 0.2) + pen([(372, 382), (550, 378)], 2.0, 77, 0.2))
    piles = [((x_, lerp(382, 378, (x_ - 372) / 178)), (x_, lerp(400, 396, (x_ - 372) / 178))) for x_ in range(380, 550, 22)]
    art.append(segs(piles, 2.2, 78, 0.2))
    art.append(segs([((x_, lerp(382, 378, (x_ - 372) / 178) + 18), (x_ + 8, lerp(382, 378, (x_ - 372) / 178) + 19)) for x_ in range(376, 550, 22)], 1.0, 79, 0.3))
    rail_y = lambda x_: lerp(372, 362, (x_ - 372) / 178) - 13
    art.append(segs([((372, rail_y(372)), (550, rail_y(550))), ((372, rail_y(372) + 6), (550, rail_y(550) + 6))], 1.2, 80, 0.2))
    art.append(segs([((x_, rail_y(x_)), (x_, rail_y(x_) + 13)) for x_ in range(374, 550, 14)], 1.2, 81, 0))
    art.append(person(452, lerp(372, 362, 80 / 178), 24, 82) + person(463, lerp(372, 362, 91 / 178), 22, 83, flip=True))
    art.append(lamp(528, lerp(372, 362, 156 / 178), 52, 84, "globe", 1.7))
    # ducks
    art.append(duck(236, 394, 8, 85) + duck(262, 402, 7, 86, flip=True) + duck(318, 414, 9, 87))
    # -- the oak (left): a heavy leaning trunk, three limbs, canopy overhead
    trunk_l = [(56, 440), (74, 396), (82, 352), (88, 312), (100, 276), (112, 256)]
    trunk_r = [(150, 440), (128, 404), (120, 362), (122, 322), (130, 290), (142, 266)]
    trunk = trunk_l + trunk_r[::-1]
    art.append(twig([(126, 270), (166, 236), (200, 214), (226, 206)], 12, 91) + twig([(104, 280), (80, 236), (58, 206)], 12, 92)
               + twig([(120, 268), (128, 214), (146, 160)], 10, 93) + twig([(166, 236), (180, 200), (186, 176)], 5, 94))
    art.append(F(smooth_closed(trunk), PAPER))
    bark = []
    for i in range(16):
        u = (i + 0.5) / 16
        pts_ = [(lerp(lx, rx_, u) + rnd.uniform(-1.5, 1.5), ly) for (lx, ly), (rx_, _) in zip(trunk_l, trunk_r)]
        bark.append(smooth_open(pts_))
    art.append(clipped(U("tk"), smooth_closed(trunk), P(" ".join(bark), 0.8, INK, 0.7)
                       + XH(U, trunk, 95, 2.2, 0.9, ang2=40, gap2=3.0, span2=(0.6, 1), dark=(150, 330), box=bbox(trunk, 6))
                       + H(U, trunk, 95, 2.2, 0.9, span=(0.55, 1), dark=(150, 330), box=bbox(trunk, 6))))
    art.append(pen(trunk_l, 2.8, 89, 0.4, smooth=True) + pen(trunk_r, 3.2, 90, 0.4, smooth=True))
    # roots flaring into the bank
    art.append(twig([(70, 420), (52, 436)], 6, 95) + twig([(140, 426), (170, 438)], 6, 96))
    for i, (cx2, cy2, rx2, ry2) in enumerate(((44, 150, 62, 60), (40, 236, 40, 40), (110, 100, 66, 44), (186, 150, 36, 28),
                                              (146, 140, 44, 34), (214, 196, 24, 18), (84, 196, 40, 30))):
        art.append(lobe(U, cx2, cy2, rx2, ry2, 900 + i, light=(1, -1), w=1.8, dense=1.1))
    # roots + grass bank in the foreground
    bank = [(50, 418), (120, 410), (240, 424), (300, 440), (50, 440)]
    art.append(F(smooth_closed(bank), PAPER) + H(U, bank, -20, 2.4, 0.8, span=(0.3, 1), dark=(60, 440), box=bbox(bank, 4)))
    grass_ = []
    for i in range(70):
        gx = rnd.uniform(52, 270)
        gy = lerp(414, 428, (gx - 52) / 218) + rnd.uniform(-2, 3)
        grass_.append(((gx, gy), (gx + rnd.uniform(-3, 3), gy - rnd.uniform(4, 10))))
    art.append(segs(grass_, 1.0, 94, 0.6))
    art.append(bench(170, 420, 44, 95))
    # the kite (accent) and birds
    art.append(kite(U, 474, 200, 14, 96, (440, 262)))
    art.append(pen([(474, 214), (470, 280), (466, 342)], 0.8, 97, 0.2, smooth=True, op=0.85))
    art.append(bird(250, 222, 7, 98) + bird(268, 210, 5, 99) + bird(470, 116, 6, 100))
    out.append(clipped(U("pic"), poly(win), "".join(art)))
    out.append(sketch(win, 2.8, 101, 1.6))
    outer = arch_window_pts(56, 544, 52, 440, spring=0.36, n=40)
    out.append(pen(outer, 1.2, 102, 0.3, closed=True))
    # dogwood blossoms in the upper spandrels
    out.append(twig([(44, 58), (72, 80), (100, 92)], 2.4, 103) + twig([(72, 80), (112, 62), (136, 58)], 1.8, 1031)
               + twig([(556, 58), (528, 80), (500, 92)], 2.4, 104) + twig([(528, 80), (488, 62), (464, 58)], 1.8, 1041))
    out.append(dogwood(U, 72, 80, 19, 20, 105) + dogwood(U, 112, 62, 12, 50, 106))
    out.append(dogwood(U, 528, 80, 19, -20, 107) + dogwood(U, 488, 62, 12, 10, 108))
    out.append(title_block(U, "atlanta", 300, 500, 420))
    out.append(finish(U))
    return "".join(out)


# ================================================================ CHICAGO
def corncob(U, cx, top, base, R, horizon, seed, park=0.34, fh=8.0, petals=16, k=0.05):
    """Marina City tower: a drum of white petal balconies (each lobe shaded like a kernel) over dark recessed
    glass, a spiral car park in the lower third with car noses at the ramp edge, an open service floor between,
    a thin roof slab. Light from the left."""
    rnd = random.Random(seed)
    out = []
    H_ = base - top
    n = int(H_ / fh)
    fh = H_ / n
    n_park = int(n * park)
    svc = n - n_park - 1          # the open service floor
    half = petals // 2

    def ey(y, th):
        return y - (horizon - y) * k * math.sin(th)

    def arc(y, r, a0=0.0, a1=math.pi, m=24):
        return [(cx + r * math.cos(a0 + (a1 - a0) * j / m), ey(y, a0 + (a1 - a0) * j / m)) for j in range(m + 1)]
    L, Rr = [], []
    for i in range(n):
        y0 = top + i * fh
        ts = fh * (0.5 if i < svc else 0.22)
        L += [(cx - R, y0 + 0.6), (cx - R - 0.8, y0 + ts * 0.5), (cx - R, y0 + ts), (cx - R * 0.9, y0 + ts + 0.6), (cx - R * 0.9, y0 + fh - 0.6)]
        Rr += [(cx + R, y0 + 0.6), (cx + R + 0.8, y0 + ts * 0.5), (cx + R, y0 + ts), (cx + R * 0.9, y0 + ts + 0.6), (cx + R * 0.9, y0 + fh - 0.6)]
    sil = [(cx - R, top)] + L + [(cx - R * 0.9, base), (cx + R * 0.9, base)] + Rr[::-1] + [(cx + R, top)]
    out.append(F(sil, PAPER))
    darks, divs, kern, cars, bands = [], [], [], [], []
    for i in range(n):
        y0 = top + i * fh
        parking = i > svc
        ts = fh * (0.5 if i < svc else 0.22)
        a = arc(y0 + ts, R * 0.9)
        b = arc(y0 + fh, R * 0.9)
        darks.append(a + b[::-1])
        if i == svc:
            for j in range(1, 14):
                th = math.pi * j / 14
                x = cx + R * 0.88 * math.cos(th)
                divs.append(((x, ey(y0 + ts, th)), (x, ey(y0 + fh, th))))
            continue
        bands.append(arc(y0 + ts, R))
        if not parking:
            off = 0.5 * (i % 2)
            for j in range(half + 1):
                t0 = math.pi * (j - 0.5 + off) / half
                t1 = math.pi * (j + 0.5 + off) / half
                t0, t1 = max(0.0, t0), min(math.pi, t1)
                if t1 - t0 < 0.05:
                    continue
                # petal boundary notch (deep, dark)
                xb = cx + R * math.cos(t1)
                if 0.05 < t1 < math.pi - 0.05:
                    divs.append(((xb, ey(y0 + 0.4, t1)), (xb, ey(y0 + ts, t1))))
                # kernel shade: the side of each lobe turned from the light, wider toward the right of the drum
                xa, xb2 = cx + R * math.cos(t0), cx + R * math.cos(t1)       # xa > xb2 (angles run right->left)
                wpx = abs(xa - xb2)
                if wpx < 1.6:
                    continue
                f = 0.2 + 0.25 * (0.5 - 0.5 * math.cos((t0 + t1) / 2))
                nstk = 1 + int(wpx * f / 1.6)
                for q in range(nstk):
                    xq = xb2 + 0.9 + q * 1.6
                    tq = math.acos(max(-1, min(1, (xq - cx) / R)))
                    kern.append(((xq, ey(y0 + 1.0, tq)), (xq, ey(y0 + ts - 0.8, tq))))
        else:
            for j in range(11):
                th = math.pi * (j + 0.5 + rnd.uniform(-0.2, 0.2)) / 11
                if rnd.random() < 0.6:
                    x = cx + R * 0.84 * math.cos(th)
                    w_ = R * 0.13 * math.sin(th) + 1.2
                    yb = ey(y0 + fh, th) - 0.6
                    cars.append(f"M {f1(x - w_)} {f1(yb)} L {f1(x - w_)} {f1(yb - fh * 0.42)} Q {f1(x)} {f1(yb - fh * 0.66)} "
                                f"{f1(x + w_)} {f1(yb - fh * 0.42)} L {f1(x + w_)} {f1(yb)} Z")
    out.append(f'<path d="{" ".join(poly(d) for d in darks)}" fill="{INK}" opacity="0.88"/>')
    if cars:
        out.append(f'<path d="{" ".join(cars)}" fill="{PAPER}" opacity="0.7"/>')
    out.append(segs([d for d in divs], 0.9, seed, 0, op=0.95))
    if kern:
        out.append(segs(kern, 0.75, seed + 3, 0, op=0.8))
    out.append(P(" ".join(smooth_open(b_) for b_ in bands), 0.8, INK, 0.9))
    # turn the drum: hatch the right flank
    out.append(clipped(U("cc"), poly(sil), H(U, [(cx + R * 0.45, top - 8), (cx + R + 4, top - 8), (cx + R + 4, base), (cx + R * 0.45, base)],
                                             90, 1.7, 0.8, span=(0.0, 1), dark=(cx + R, base), wob=0.1, brk=0)))
    # roof slab + rim
    rim = arc(top, R + 1)
    out.append(F(rim + [(cx + R + 1, top + 3), (cx - R - 1, top + 3)], PAPER) + P(smooth_open(rim), 1.8))
    out.append(P(smooth_open(arc(top + 3, R + 1)), 1.2))
    out.append(F([(cx - R * 0.3, top), (cx - R * 0.3, top - 5), (cx + R * 0.3, top - 5), (cx + R * 0.3, top)], PAPER)
               + sketch([(cx - R * 0.3, top), (cx - R * 0.3, top - 5), (cx + R * 0.3, top - 5), (cx + R * 0.3, top)], 1.2, seed, 0.3))
    out.append(pen(L, 1.5, seed + 1, 0.0) + pen(Rr, 1.9, seed + 2, 0.0))
    return "".join(out)


def bridge_house(U, x, base, w, h, seed, flip=False):
    """A Beaux-Arts bascule-bridge tender house: rusticated stone, arched windows, hipped roof, cornice."""
    out = []
    body = [(x, base - h), (x + w, base - h), (x + w, base), (x, base)]
    out.append(F(body, PAPER))
    out.append(segs([((x, base - h + j), (x + w, base - h + j)) for j in range(4, int(h), 4)], 0.6, seed, 0.2, op=0.6))
    for i in range(2):
        wx = x + w * (0.18 + 0.42 * i)
        ww = w * 0.24
        a = arch_window_pts(wx, wx + ww, base - h * 0.78, base - h * 0.32, spring=0.35, n=8)
        out.append(F(a, INK, 0.85))
    sh = [(x + w * (0.65 if not flip else 0), base - h), (x + w * (1 if not flip else 0.35), base - h),
          (x + w * (1 if not flip else 0.35), base), (x + w * (0.65 if not flip else 0), base)]
    out.append(H(U, sh, 90, 1.6, 0.8))
    cor = [(x - 2, base - h - 3), (x + w + 2, base - h - 3), (x + w + 2, base - h), (x - 2, base - h)]
    out.append(F(cor, PAPER) + sketch(cor, 1.3, seed, 0.6))
    roof = [(x - 1, base - h - 3), (x + w * 0.3, base - h - 3 - h * 0.45), (x + w * 0.7, base - h - 3 - h * 0.45), (x + w + 1, base - h - 3)]
    out.append(F(roof, PAPER) + H(U, roof, 0, 1.6, 0.7) + sketch(roof, 1.4, seed + 1, 0.5, closed=False))
    out.append(seg(x + w * 0.5, base - h - 3 - h * 0.45, x + w * 0.5, base - h - 8 - h * 0.45, 1.4, seed, 0))
    out.append(sketch(body, 1.6, seed + 2, 0.8))
    return "".join(out)


@design("chicago")
def chicago(U):
    """The Chicago River looking west from a bridge: Marina City's twin corncobs close up, a bascule bridge with its
    tender houses, the Wacker Drive wall, the black tower rising beyond, a tour boat (vermilion) on the river."""
    out = [ground_paper(U, 51)]
    VP = (236, 322)
    art = []

    def on(a, b, x):            # y on the line a-b at x
        return lerp(a[1], b[1], (x - a[0]) / (b[0] - a[0]))
    LB = ((0, 452), VP)         # left bank (south) wall top
    RB = ((600, 474), VP)       # right bank (north)
    # --- sky: fine engraved rules thickening toward the horizon, fading up into the title
    sky = []
    y = 190
    while y < 330:
        sky.append(((0, y), (600, y)))
        y += lerp(8, 3.2, (y - 190) / 140)
    art.append(segs(sky, 0.6, 3, 0.15, op=0.5))
    art.append(cloud(U, 120, 214, 120, 18, 4))
    # --- the black tower in the distance (bundled tubes, stepped tops, twin antennas)
    wx = 262
    tw_ = [(wx - 19, 212), (wx - 6, 212), (wx - 6, 202), (wx + 6, 202), (wx + 6, 220), (wx + 19, 220), (wx + 19, 330), (wx - 19, 330)]
    art.append(F(tw_, PAPER))
    art.append(clipped(U("wt"), poly(tw_), XH(U, tw_, 90, 1.8, 0.9, ang2=0, gap2=3.2, span2=(0, 1)) + H(U, tw_, 90, 1.8, 0.9, span=(0.5, 1), dark=(wx + 30, 300))))
    art.append(sketch(tw_, 1.5, 5, 0.6))
    art.append(segs([((wx - 6, 212), (wx - 6, 330)), ((wx + 6, 220), (wx + 6, 330))], 1.0, 6, 0, color=PAPER, op=0.7))
    art.append(nib([(wx - 3, 202), (wx - 3, 180)], 1.6, taper=(1, 0.3), seed=7, color=INK) + nib([(wx + 3, 202), (wx + 3, 184)], 1.6, taper=(1, 0.3), seed=8, color=INK))
    # --- the far skyline behind the river corridor
    for i, (a, b, t, st) in enumerate(((150, 176, 262, "grid"), (178, 204, 240, "pane"), (206, 232, 250, "slit"), (290, 312, 244, "grid"),
                                       (312, 336, 262, "pane"), (336, 352, 282, "slit"))):
        art.append(f'<g opacity="0.6">{prism(U, a, b, 5, t, 330, 20 + i, style=st, dark_p=0.15, w=1.1)}</g>')
    # --- left bank: the Wacker Drive wall, receding to the vanishing point
    lb = []
    xs = [-10, 64, 120, 160, 190, 212, 226]
    tops = [196, 226, 246, 266, 284, 296, 306]
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        t0 = tops[i]
        # top edge recedes toward VP
        t1 = lerp(t0, VP[1], (x1 - x0) / (VP[0] - x0))
        b0, b1 = on(*LB, x0), on(*LB, x1)
        q = [(x0, t0), (x1, t1), (x1, b1), (x0, b0)]
        lb.append(F(q, PAPER))
        rows = max(4, int((b0 - t0) / 9))
        cols = max(2, int((x1 - x0) / 9))
        lb.append(facade(U, [(x0 + 2, t0 + 6), (x1 - 1, t1 + 4), (x1 - 1, b1 - 10), (x0 + 2, b0 - 12)], cols, rows,
                         ("pane", "slit", "grid", "pane", "slit", "grid")[i], 30 + i, dark_p=0.25, w=0.8))
        lb.append(H(U, q, 0, 3.2, 0.6, op=0.45))
        lb.append(sketch(q, 1.5, 40 + i, 0.8))
        # near-side cornice band receding
        lb.append(seg(x0, t0 + 4, x1, t1 + 3, 1.0, 50 + i, 0))
    art.append("".join(lb))
    # the domed building on the left (cupola on a stepped tower)
    jx, jt = 136, 214
    jt_ = [(jx - 14, jt + 30), (jx + 14, jt + 30), (jx + 14, 300), (jx - 14, 300)]
    art.append(F(jt_, PAPER) + facade(U, [(jx - 12, jt + 34), (jx + 12, jt + 34), (jx + 12, 296), (jx - 12, 296)], 4, 8, "pane", 61)
               + H(U, [(jx + 6, jt + 30), (jx + 14, jt + 30), (jx + 14, 300), (jx + 6, 300)], 90, 1.6, 0.8) + sketch(jt_, 1.4, 62, 0.6))
    drum = [(jx - 10, jt + 30), (jx - 10, jt + 16), (jx + 10, jt + 16), (jx + 10, jt + 30)]
    art.append(F(drum, PAPER) + segs([((jx + d, jt + 17), (jx + d, jt + 29)) for d in (-6, -2, 2, 6)], 1.0, 63, 0) + sketch(drum, 1.3, 64, 0.4))
    dome = [(jx - 11, jt + 16), (jx - 8, jt + 4), (jx, jt - 2), (jx + 8, jt + 4), (jx + 11, jt + 16)]
    art.append(F(smooth_closed(dome), PAPER) + clipped(U("dm"), smooth_closed(dome), H(U, dome, 60, 1.6, 0.7, box=bbox(dome)))
               + pen(dome, 1.4, 65, 0.1, smooth=True))
    art.append(seg(jx, jt - 2, jx, jt - 10, 1.4, 66, 0))
    # river walls + riverwalk railing on the left
    lw_ = [(-10, on(*LB, -10)), VP, (VP[0], VP[1] + 2), (-10, on(*LB, -10) + 22)]
    art.append(F(lw_, PAPER) + H(U, lw_, 0, 2.0, 0.8, op=0.8))
    art.append(pen([(-10, on(*LB, -10)), VP], 1.8, 67, 0.2))
    rail = [((x, on(*LB, x) - lerp(14, 2, x / VP[0])), (x, on(*LB, x))) for x in range(0, VP[0] - 20, 9)]
    art.append(segs(rail, 1.0, 68, 0) + pen([(0, on(*LB, 0) - 14), (VP[0] - 20, on(*LB, VP[0] - 20) - 2.5)], 1.2, 69, 0.2))
    for x, h in ((40, 26), (72, 22), (180, 9)):
        art.append(person(x, on(*LB, x), h, 70 + x, flip=x > 60))
    art.append(corncob(U, 372, 238, on(*RB, 372) + 2, 44, VP[1], 91, fh=6.6))
    # --- the bascule bridge across the river, tender houses on each bank
    BY = 392
    deck = [(0, BY), (440, BY), (440, BY + 12), (0, BY + 12)]
    art.append(F(deck, PAPER))
    tr = []
    for i, x in enumerate(range(2, 440, 9)):
        tr.append(((x, BY + 1), (x + 9, BY + 11)) if i % 2 else ((x, BY + 11), (x + 9, BY + 1)))
    art.append(segs(tr, 0.8, 71, 0) + segs([((x, BY), (x, BY + 12)) for x in range(2, 440, 9)], 0.7, 72, 0))
    art.append(pen([(0, BY), (440, BY)], 2.0, 73, 0.2) + pen([(0, BY + 12), (440, BY + 12)], 2.4, 74, 0.2))
    art.append(segs([((x, BY), (x, BY - 7)) for x in range(2, 440, 5)], 0.7, 75, 0) + pen([(0, BY - 7), (440, BY - 7)], 1.3, 76, 0.2))
    art.append(H(U, [(0, BY + 12), (440, BY + 12), (440, BY + 18), (0, BY + 18)], 0, 1.2, 0.8))
    art.append(car(U, 170, BY - 1, 34, 77) + car(U, 318, BY - 1, 30, 78, flip=True, kind="classic"))
    art.append(person(226, BY - 1, 17, 79) + person(235, BY - 1, 16, 80, flip=True) + person(386, BY - 1, 17, 81))
    art.append(bridge_house(U, 72, BY + 2, 34, 34, 82))
    # --- Marina City: far tower then near tower, with the marina at their feet
    art.append(corncob(U, 474, 206, on(*RB, 474) + 2, 62, VP[1], 92, fh=9.0))
    # right river wall + marina slips
    rw = [(VP[0] + 40, on(*RB, VP[0] + 40)), (610, on(*RB, 610)), (610, on(*RB, 610) + 22), (VP[0] + 40, on(*RB, VP[0] + 40) + 3)]
    art.append(F(rw, PAPER) + H(U, rw, 0, 2.0, 0.8, op=0.8) + pen(rw[:2], 2.0, 93, 0.2))
    dock = lambda x: on(*RB, x) + lerp(10, 34, (x - 330) / 280)
    dk = [(330, dock(330)), (610, dock(610)), (610, dock(610) + 6), (330, dock(330) + 2)]
    art.append(F(dk, PAPER) + H(U, dk, 0, 1.4, 0.8) + pen(dk[:2], 1.6, 94, 0.2))
    art.append(segs([((x, dock(x) - lerp(4, 10, (x - 330) / 280)), (x, dock(x) + lerp(3, 8, (x - 330) / 280))) for x in range(336, 600, 22)], 1.8, 95, 0))
    # moored boats
    for x, L_ in ((380, 22), (452, 30), (540, 40)):
        yb = dock(x) + lerp(6, 14, (x - 330) / 270)
        hull = [(x - L_ / 2, yb - L_ * 0.12), (x + L_ / 2, yb - L_ * 0.18), (x + L_ * 0.38, yb), (x - L_ * 0.42, yb)]
        art.append(F(hull, PAPER) + H(U, hull, 0, 1.6, 0.7, span=(0.5, 1), dark=(x, yb)) + sketch(hull, 1.3, x, 0.4))
        art.append(F([(x - L_ * 0.2, yb - L_ * 0.14), (x - L_ * 0.18, yb - L_ * 0.3), (x + L_ * 0.12, yb - L_ * 0.3), (x + L_ * 0.18, yb - L_ * 0.16)], INK, 0.8))
    # --- the river
    water = [(-10, on(*LB, -10) + 22), (VP[0], VP[1] + 2), (610, on(*RB, 610) + 22), (610, 610), (-10, 610)]
    art.append(ripples(U, -10, 610, VP[1] + 2, 610, 95, dens=1.0, gap=(2.4, 10), ln=((3, 9), (14, 40)),
                       refl=[(412, 544, 0.85), (326, 418, 0.6), (240, 284, 0.6), (58, 90, 0.5), (414, 444, 0.5)], skip=[(180, 230)],
                       clip=poly(water)))
    # --- tour boat (the accent): long hull, open top deck with passengers, wake
    bx0, bx1, by = 92, 352, 516
    hull = [(bx0, by - 26), (bx1 - 6, by - 28), (bx1 + 16, by - 22), (bx1 + 4, by - 4), (bx0 + 10, by), (bx0 - 4, by - 14)]
    art.append(F(hull, PAPER))
    band = [(bx0 - 2, by - 20), (bx1 + 12, by - 22), (bx1 + 8, by - 15), (bx0, by - 13)]
    art.append(accent(U, poly(band), bbox(band), 96, op=0.95, ang=0, n=26, length=(10, 30), width=(1.5, 3)))
    art.append(H(U, [(bx0, by - 13), (bx1 + 8, by - 15), (bx1 + 4, by - 4), (bx0 + 10, by)], 0, 2.0, 0.8))
    art.append(sketch(hull, 2.2, 97, 0.8) + pen([(bx0 - 2, by - 20), (bx1 + 12, by - 22)], 1.0, 98, 0.1) + pen([(bx0, by - 13), (bx1 + 8, by - 15)], 1.0, 99, 0.1))
    # lower cabin windows
    cab = [(bx0 + 6, by - 26), (bx1 - 10, by - 28), (bx1 - 12, by - 44), (bx0 + 8, by - 42)]
    art.append(F(cab, PAPER) + sketch(cab, 1.6, 100, 0.6))
    m = homog([cab[3], cab[2], cab[1], cab[0]])
    wins = [[m((i + 0.15) / 14, 0.18), m((i + 0.85) / 14, 0.18), m((i + 0.85) / 14, 0.75), m((i + 0.15) / 14, 0.75)] for i in range(14)]
    art.append(f'<path d="{" ".join(poly(w_) for w_ in wins)}" fill="{INK}" opacity="0.85"/>')
    # top deck rail + seated passengers
    art.append(pen([(bx0 + 4, by - 44), (bx1 - 8, by - 46)], 1.6, 101, 0.1) + pen([(bx0 + 4, by - 52), (bx1 - 8, by - 54)], 1.2, 102, 0.1))
    art.append(segs([((x, lerp(by - 44, by - 46, (x - bx0) / (bx1 - bx0))), (x, lerp(by - 52, by - 54, (x - bx0) / (bx1 - bx0)))) for x in range(bx0 + 6, bx1 - 6, 8)], 0.9, 103, 0))
    rnd = random.Random(104)
    for x in range(bx0 + 14, bx1 - 14, 12):
        if rnd.random() < 0.78:
            yb = lerp(by - 46, by - 48, (x - bx0) / (bx1 - bx0))
            art.append(f'<circle cx="{f1(x)}" cy="{f1(yb - 13)}" r="2.6" fill="{INK}"/>'
                       + F(smooth_closed([(x - 3.6, yb - 2), (x + 3.6, yb - 2), (x + 3, yb - 10), (x - 3, yb - 10)]), INK, 0.9))
    art.append(nib([(bx1 - 4, by - 46), (bx1 + 6, by - 62)], 1.6, seed=105, color=INK))
    # wake
    art.append(P(f"M {bx1 + 14} {by - 8} q 40 6 90 26 M {bx1 + 6} {by - 2} q 30 10 60 34 M {bx0 - 4} {by - 6} q -30 6 -70 4", 1.2, INK, 0.85))
    # gulls
    art.append(bird(392, 120 + 120, 7, 106) + bird(410, 226, 5, 107))
    # bleed picture to the sheet edges, fading up into the title
    out.append(soft_frame(U, 300, 380, 330, 260, 6, "".join(art), expo=5.0, inset=0.18, rings=12))
    out.append(T(300, 128, "Chicago", DMS, name_size("Chicago")))
    out.append(coords_line(300, 162, CITIES["chicago"][1], rule_len=34))
    out.append(finish(U))
    return "".join(out)


# ================================================================ MIAMI
def deco_hotel(U, x0, x1, base, h, seed, pylon=0.5, pw=0.22, floors=3, port=True, corner="round", fins=3, step=3):
    """An Ocean Drive Art Deco hotel, face-on: eyebrow ledges over the windows, a stepped central pylon with
    fins, racing-stripe bands, porthole, terrace with a little awning. Light from the left."""
    rnd = random.Random(seed)
    out = []
    top = base - h
    W = x1 - x0
    sw = W * 0.08                       # side face (shade)
    body = [(x0, top), (x1, top), (x1, base), (x0, base)]
    side = [(x1, top + 2), (x1 + sw, top + 4), (x1 + sw, base), (x1, base)]
    out.append(F(side, PAPER) + H(U, side, 90, 1.6, 0.8) + sketch(side, 1.2, seed, 0.4))
    out.append(F(body, PAPER))
    # pylon
    px = x0 + W * pylon
    pyw = W * pw
    pt_ = top - h * 0.34
    py = [(px - pyw / 2, top), (px - pyw / 2, pt_ + step * 3), (px - pyw / 2 + 3, pt_ + step * 3), (px - pyw / 2 + 3, pt_ + step * 1.5),
          (px - pyw / 2 + 6, pt_ + step * 1.5), (px - pyw / 2 + 6, pt_), (px + pyw / 2 - 6, pt_), (px + pyw / 2 - 6, pt_ + step * 1.5),
          (px + pyw / 2 - 3, pt_ + step * 1.5), (px + pyw / 2 - 3, pt_ + step * 3), (px + pyw / 2, pt_ + step * 3), (px + pyw / 2, top)]
    out.append(F(py, PAPER))
    fl = [((px + (i - (fins - 1) / 2) * pyw / (fins + 1), pt_ + step * 3 + 2), (px + (i - (fins - 1) / 2) * pyw / (fins + 1), base - h * 0.25))
          for i in range(fins)]
    out.append(segs(fl, 1.6, seed, 0))
    out.append(H(U, [(px + pyw * 0.25, pt_), (px + pyw / 2, pt_), (px + pyw / 2, top), (px + pyw * 0.25, top)], 90, 1.5, 0.7))
    out.append(sketch(py, 1.5, seed + 1, 0.6, closed=False))
    if port:
        r = min(pyw * 0.22, 5)
        out.append(f'<circle cx="{f1(px)}" cy="{f1(pt_ + step * 3 + r + 4)}" r="{f1(r)}" fill="{INK}" opacity="0.85"/>'
                   f'<circle cx="{f1(px)}" cy="{f1(pt_ + step * 3 + r + 4)}" r="{f1(r + 1.6)}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    # windows + eyebrows, either side of the pylon
    fh = (h * 0.8) / floors
    wins, brows, sh = [], [], []
    for f_ in range(floors):
        yy = top + h * 0.06 + f_ * fh
        for a, b in ((x0 + 4, px - pyw / 2 - 3), (px + pyw / 2 + 3, x1 - 4)):
            n = max(1, int((b - a) / 13))
            ww = (b - a) / n
            for i in range(n):
                wx0, wx1 = a + i * ww + 2.2, a + (i + 1) * ww - 2.2
                wins.append([(wx0, yy + fh * 0.3), (wx1, yy + fh * 0.3), (wx1, yy + fh * 0.82), (wx0, yy + fh * 0.82)])
            brows.append(((a - 2, yy + fh * 0.22), (b + 2, yy + fh * 0.22)))
            sh.append([(a - 2, yy + fh * 0.22), (b + 2, yy + fh * 0.22), (b + 2, yy + fh * 0.36), (a - 2, yy + fh * 0.36)])
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.82"/>')
    for q in sh:
        out.append(H(U, q, 0, 1.3, 0.7, wob=0.1, brk=0))
    out.append(segs(brows, 2.0, seed + 2, 0.1))
    # racing stripes on the corner
    if corner == "round":
        out.append(segs([((x0 + 1, top + h * 0.06 + k * 3.2), (x0 + 12, top + h * 0.06 + k * 3.2)) for k in range(3)], 1.0, seed, 0))
    # parapet band and roof line
    out.append(seg(x0 - 1, top + 3, x1 + 1, top + 3, 1.0, seed, 0) + seg(x0 - 2, top, x1 + 2, top, 2.0, seed + 3, 0.1))
    # ground floor terrace: awning + dark doorway band
    gy = base - h * 0.14
    aw = [(x0 + 3, gy - 6), (x1 - 3, gy - 6), (x1 + 2, gy), (x0 - 2, gy)]
    out.append(F(aw, PAPER) + segs([((x0 + 3 + i * 5, gy - 6), (x0 - 2 + i * 5.25, gy)) for i in range(int(W / 5) + 1)], 0.9, seed, 0)
               + sketch(aw, 1.2, seed + 4, 0.4))
    out.append(F([(x0 + 4, gy + 1), (x1 - 4, gy + 1), (x1 - 4, base), (x0 + 4, base)], INK, 0.6))
    out.append(sketch(body, 1.7, seed + 5, 0.8))
    return "".join(out)


def pelican(x, y, s, seed=1, flap=0.0):
    """A brown pelican gliding: broad bowed wings, tucked head, long bill (side view, heading left)."""
    out = []
    wing_up = -s * (0.25 + flap)
    body = [(x - s * 0.55, y), (x - s * 0.2, y - s * 0.12), (x + s * 0.45, y - s * 0.06), (x + s * 0.75, y + s * 0.06),
            (x + s * 0.35, y + s * 0.14), (x - s * 0.3, y + s * 0.12)]
    out.append(F(smooth_closed(body), INK, 0.95))
    # wings (far + near)
    out.append(nib([(x - s * 0.1, y - s * 0.05), (x + s * 0.2, y + wing_up - s * 0.15), (x + s * 0.8, y + wing_up + s * 0.05), (x + s * 1.25, y + wing_up + s * 0.3)],
                   s * 0.22, taper=(1, 0.2), ramp=0.6, seed=seed, color=INK))
    out.append(nib([(x + s * 0.05, y), (x - s * 0.25, y + wing_up - s * 0.1), (x - s * 0.8, y + wing_up + s * 0.1), (x - s * 1.15, y + wing_up + s * 0.32)],
                   s * 0.22, taper=(1, 0.2), ramp=0.6, seed=seed + 1, color=INK))
    # head + bill
    out.append(f'<circle cx="{f1(x - s * 0.62)}" cy="{f1(y - s * 0.08)}" r="{f1(s * 0.12)}" fill="{INK}"/>')
    out.append(F([(x - s * 0.7, y - s * 0.12), (x - s * 1.35, y + s * 0.06), (x - s * 0.7, y + s * 0.06)], INK))
    return "".join(out)


@design("miami")
def miami(U):
    """South Beach in a deco porthole: a lifeguard tower (vermilion stripes) on the sand, palms along the
    promenade, the Ocean Drive hotels behind, pelicans over a breaking sea; sunburst rays in the corners."""
    out = [ground_paper(U, 61)]
    CX, CY, RR = 300, 252, 194
    # corner sunbursts (Art Deco rays) outside the porthole
    rays = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        r0 = RR + 14
        r1 = RR + 64 + (16 if i % 2 else 0)
        rays.append(((CX + math.cos(a) * r0, CY + math.sin(a) * r0), (CX + math.cos(a) * r1, CY + math.sin(a) * r1)))
    out.append(clipped(U("ry"), poly([(0, 0), (600, 0), (600, 452), (0, 452)]), segs(rays, 1.1, 1, 0, op=0.75)))
    art = []
    HZ = 292
    # sky: sun low on the right, ruled
    sky = []
    y = CY - RR
    while y < HZ:
        sky.append(((CX - RR, y), (CX + RR, y)))
        y += lerp(10, 4, (y - (CY - RR)) / (HZ - CY + RR))
    art.append(segs(sky, 0.6, 3, 0.15, op=0.4))
    sx, sy, sr = 430, 164, 30
    art.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{PAPER}"/>')
    art.append(clipped(U("sn"), f'<circle cx="{sx}" cy="{sy}" r="{sr}"/>',
                       segs([((sx - sr, yy), (sx + sr, yy)) for yy in range(sy - sr + 4, sy + sr, 4)], 1.0, 4, 0)))
    art.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    art.append(cloud(U, 196, 120, 110, 18, 5) + cloud(U, 380, 210, 90, 12, 6))
    # --- the sea (right): horizon, a far ship, a sailboat, breaking waves toward the shore
    sea = [(250, HZ), (CX + RR, HZ), (CX + RR, 470), (420, 470)]
    art.append(ripples(U, 230, CX + RR, HZ + 1, 420, 7, dens=1.0, gap=(2.2, 8), refl=[(400, 460, 0.6)],
                       clip=poly([(240, HZ), (CX + RR, HZ), (CX + RR, 400), (300, 330)])))
    art.append(pen([(236, HZ), (CX + RR, HZ)], 1.6, 8, 0.1))
    ship = [(452, HZ - 1), (500, HZ - 1), (496, HZ - 7), (458, HZ - 7)]
    art.append(F(ship, PAPER) + sketch(ship, 1.2, 9, 0.3) + F([(462, HZ - 7), (462, HZ - 13), (488, HZ - 13), (490, HZ - 7)], PAPER)
               + sketch([(462, HZ - 7), (462, HZ - 13), (488, HZ - 13), (490, HZ - 7)], 1.0, 10, 0.2) + F([(476, HZ - 13), (476, HZ - 18), (481, HZ - 18), (481, HZ - 13)], INK))
    art.append(segs([((x_, HZ - 9), (x_ + 2, HZ - 9)) for x_ in range(464, 488, 4)], 1.0, 11, 0))
    # sailboat
    sbx, sby = 424, 316
    art.append(F([(sbx - 16, sby), (sbx + 16, sby), (sbx + 11, sby + 5), (sbx - 12, sby + 5)], INK, 0.9))
    sail = [(sbx - 1, sby - 3), (sbx - 1, sby - 40), (sbx + 18, sby - 3)]
    jib = [(sbx - 3, sby - 36), (sbx - 3, sby - 3), (sbx - 18, sby - 3)]
    art.append(F(sail, PAPER) + H(U, sail, 90, 2.2, 0.7, span=(0.6, 1), dark=(sbx + 18, sby)) + pen(sail, 1.4, 12, 0.1, closed=True))
    art.append(F(jib, PAPER) + pen(jib, 1.2, 13, 0.1, closed=True))
    art.append(P(f"M {sbx - 18} {sby + 7} q 18 3 36 0", 1.0))
    # surf lines along the shore
    shore = lambda x_: lerp(470, 318, (x_ - 250) / 260)
    foam = []
    for k, off in enumerate((0, 10, 22, 38)):
        pts_ = [(x_, shore(x_) - off * 0.9 + 2.5 * math.sin(x_ * 0.11 + k)) for x_ in range(240, 520, 8)]
        foam.append(smooth_open(pts_))
    art.append(clipped(U("fm"), poly([(240, HZ + 4), (CX + RR, HZ + 4), (CX + RR, 480), (240, 480)]), P(" ".join(foam), 1.3, INK, 0.9)))
    # scalloped breaker crest
    crest = []
    for x_ in range(262, 512, 12):
        yb = shore(x_) - 38 * 0.9
        crest.append(f"M {f1(x_)} {f1(yb)} q 6 -7 12 0")
    art.append(P(" ".join(crest), 1.4))
    # --- the land (left): hotels, palms, promenade wall, sand
    hotels = [(102, 172, HZ - 2, 112, 41, dict(pylon=0.5, floors=4)),
              (176, 246, HZ - 2, 138, 42, dict(pylon=0.42, floors=5, pw=0.26)),
              (250, 300, HZ + 2, 92, 43, dict(pylon=0.6, floors=3, port=False))]
    for x0, x1, b, h, sd, kw in hotels:
        art.append(deco_hotel(U, x0, x1, b, h, sd, **kw))
    # sea wall / promenade + low wall
    wall = [(96, HZ - 2), (300, HZ + 2), (300, HZ + 12), (96, HZ + 10)]
    art.append(F(wall, PAPER) + H(U, wall, 0, 2.0, 0.8) + pen(wall[:2], 1.8, 14, 0.1))
    # palms (far to near)
    for x_, base, h, sd, lean, sp in ((174, HZ + 8, 96, 15, 0.04, 0.8), (248, HZ + 8, 118, 16, -0.05, 0.85),
                                     (300, HZ + 12, 168, 17, 0.14, 0.9)):
        art.append(palm(U, x_, base, h, sd, lean=lean, fronds=9, span=sp))
    # sand: stipple denser in the foreground, footprints, dune grass
    sand = [(CX - RR, HZ + 10), (300, HZ + 12), (250, 470), (CX - RR, 470)]
    sand2 = poly([(CX - RR, HZ + 10), (300, HZ + 12), (520, 318), (520, 470), (CX - RR, 470)])
    sandclip = f"M {CX - RR} {HZ + 10} L 300 {HZ + 12} L 520 318 L 520 470 L {CX - RR} 470 Z"
    wet = poly([(240, 480), (520, 330), (520, 480)])
    art.append(ST(U, sandclip, 1700, light=(300, HZ), r=(0.5, 1.1), op=0.75, box=(CX - RR, HZ, 520, 470)))
    rnd = random.Random(19)
    fp = []
    for i in range(14):
        x_, y_ = 150 + i * 13 + rnd.uniform(-2, 2), 432 - i * 8 + (4 if i % 2 else 0)
        fp.append(f'<ellipse cx="{f1(x_)}" cy="{f1(y_)}" rx="2.6" ry="1.3" transform="rotate(-30 {f1(x_)} {f1(y_)})"/>')
    art.append(f'<g fill="{INK}" opacity="0.6">{"".join(fp)}</g>')
    # beach umbrella + towel + people
    ux, uy = 196, 382
    um = [(ux - 30, uy - 40), (ux - 15, uy - 52), (ux, uy - 55), (ux + 15, uy - 52), (ux + 30, uy - 40)]
    ud = smooth_open(um) + f" L {ux} {uy - 40} Z"
    art.append(F(ud, PAPER))
    gores = []
    for i in range(4):
        a, b = um[i], um[i + 1]
        if i % 2 == 0:
            gores.append(poly([a, b, (ux, uy - 42)]))
    art.append(f'<path d="{" ".join(gores)}" fill="{INK}" opacity="0.82"/>')
    sc = "".join(f"Q {f1((um[i][0] + um[i + 1][0]) / 2)} {f1(max(um[i][1], um[i + 1][1]) + 5)} {f1(um[i + 1][0])} {f1(um[i + 1][1])} " for i in range(4))
    art.append(P(smooth_open(um), 1.6) + P(f"M {f1(um[0][0])} {f1(um[0][1])} {sc}", 1.3))
    art.append(seg(ux, uy - 55, ux + 3, uy + 2, 1.8, 20, 0))
    towel = [(ux - 26, uy + 6), (ux + 6, uy + 2), (ux + 14, uy + 10), (ux - 18, uy + 14)]
    art.append(F(towel, PAPER) + H(U, towel, -10, 3.0, 1.0) + sketch(towel, 1.2, 21, 0.3))
    art.append(person(ux + 36, uy + 6, 26, 22) + person(ux + 46, uy + 8, 22, 23, flip=True))
    # --- the lifeguard tower (accent): hut on stilts, ramp, flag
    lx, ly = 352, 410          # base centre
    hut = [(lx - 30, ly - 74), (lx + 30, ly - 74), (lx + 30, ly - 38), (lx - 30, ly - 38)]
    deck = [(lx - 40, ly - 38), (lx + 40, ly - 38), (lx + 40, ly - 32), (lx - 40, ly - 32)]
    roof = [(lx - 36, ly - 74), (lx - 24, ly - 90), (lx + 24, ly - 90), (lx + 36, ly - 74)]
    stilts = [((lx - 32, ly - 32), (lx - 34, ly)), ((lx + 32, ly - 32), (lx + 34, ly)), ((lx - 12, ly - 32), (lx - 12, ly - 2)),
              ((lx + 12, ly - 32), (lx + 12, ly - 2)), ((lx - 32, ly - 26), (lx + 32, ly - 6)), ((lx + 32, ly - 26), (lx - 32, ly - 6))]
    ramp = [(lx - 40, ly - 36), (lx - 96, ly + 2), (lx - 90, ly + 6), (lx - 40, ly - 30)]
    art.append(F(ramp, PAPER) + segs([((lx - 40 - i * 5.6, ly - 36 + i * 3.8), (lx - 40 - i * 5.0, ly - 30 + i * 3.6)) for i in range(10)], 0.9, 24, 0)
               + sketch(ramp, 1.5, 25, 0.5))
    art.append(segs([((lx - 40, ly - 50), (lx - 96, ly - 12))] + [((lx - 40 - i * 14, ly - 50 + i * 9.6), (lx - 40 - i * 14, ly - 36 + i * 9.6)) for i in range(5)], 1.2, 26, 0.1))
    art.append(segs(stilts, 2.0, 27, 0.1))
    art.append(F(hut, PAPER))
    stripes = " ".join(poly([(lx - 30 + i * 12, ly - 74), (lx - 24 + i * 12, ly - 74), (lx - 24 + i * 12, ly - 38), (lx - 30 + i * 12, ly - 38)]) for i in range(5))
    art.append(accent(U, stripes, bbox(hut), 28, op=0.95, ang=-90, n=22, length=(10, 24), width=(1.5, 3)))
    art.append(H(U, [(lx + 14, ly - 74), (lx + 30, ly - 74), (lx + 30, ly - 38), (lx + 14, ly - 38)], 90, 1.8, 0.9))
    art.append(f'<circle cx="{lx - 6}" cy="{ly - 58}" r="8" fill="{INK}" opacity="0.88"/><circle cx="{lx - 6}" cy="{ly - 58}" r="10.5" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    art.append(sketch(hut, 2.0, 29, 0.8))
    art.append(F(roof, PAPER) + H(U, roof, 0, 2.0, 0.8, span=(0.0, 1)) + sketch(roof, 1.9, 30, 0.8))
    art.append(F(deck, PAPER) + H(U, deck, 0, 1.6, 0.8) + sketch(deck, 1.6, 31, 0.6))
    art.append(segs([((lx + 40, ly - 38), (lx + 40, ly - 52)), ((lx + 30, ly - 52), (lx + 40, ly - 52))], 1.4, 32, 0))
    art.append(seg(lx, ly - 90, lx, ly - 120, 1.6, 33, 0))
    fd = smooth_open([(lx, ly - 120), (lx + 10, ly - 122), (lx + 20, ly - 117)]) + f" L {lx + 20} {ly - 109} " + smooth_open([(lx + 20, ly - 109), (lx + 10, ly - 113), (lx, ly - 110)])[1:] + " Z"
    art.append(F(fd, INK, 0.9))
    art.append(F([(lx - 36, ly + 1), (lx + 36, ly + 1), (lx + 30, ly + 5), (lx - 30, ly + 5)], INK, 0.25))
    # pelicans over the water
    art.append(pelican(404, 236, 18, 34) + pelican(462, 258, 14, 35, 0.12))
    out.append(clipped(U("pic"), f'<circle cx="{CX}" cy="{CY}" r="{RR}"/>', "".join(art)))
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{RR}" fill="none" stroke="{INK}" stroke-width="3"/>')
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{RR + 7}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    # porthole rivets
    out.append("".join(f'<circle cx="{f1(CX + math.cos(a) * (RR + 3.5))}" cy="{f1(CY + math.sin(a) * (RR + 3.5))}" r="1.3" fill="{INK}"/>'
                       for a in [i * math.pi / 18 for i in range(36)]))
    out.append(title_block(U, "miami", 300, 508, 400, coord_gap=28, mx=62))
    out.append(finish(U))
    return "".join(out)


# ================================================================ NASHVILLE
def busker(x, y, h, seed=1):
    """A street musician with a hat and an acoustic guitar, open case at his feet."""
    out = []
    # legs
    out.append(P(f"M {f1(x - h * 0.05)} {f1(y - h * 0.46)} L {f1(x - h * 0.1)} {f1(y)} M {f1(x + h * 0.05)} {f1(y - h * 0.46)} L {f1(x + h * 0.09)} {f1(y)}",
                 h * 0.085))
    out.append(P(f"M {f1(x - h * 0.15)} {f1(y)} L {f1(x - h * 0.05)} {f1(y)} M {f1(x + h * 0.05)} {f1(y)} L {f1(x + h * 0.16)} {f1(y)}", h * 0.05))
    # torso
    torso = [(x - h * 0.13, y - h * 0.8), (x + h * 0.13, y - h * 0.8), (x + h * 0.12, y - h * 0.44), (x - h * 0.12, y - h * 0.44)]
    out.append(F(smooth_closed(torso), INK, 0.95))
    # head + hat
    out.append(f'<circle cx="{f1(x)}" cy="{f1(y - h * 0.88)}" r="{f1(h * 0.075)}" fill="{INK}"/>')
    out.append(F(smooth_closed([(x - h * 0.16, y - h * 0.93), (x + h * 0.16, y - h * 0.93), (x + h * 0.1, y - h * 0.955), (x - h * 0.1, y - h * 0.955)]), INK))
    out.append(F(smooth_closed([(x - h * 0.07, y - h * 0.95), (x + h * 0.07, y - h * 0.95), (x + h * 0.06, y - h * 1.04), (x, y - h * 1.02), (x - h * 0.06, y - h * 1.04)]), INK))
    # guitar across the body: body bouts + neck
    gx, gy = x + h * 0.02, y - h * 0.5
    a = math.radians(-28)
    ca, sa = math.cos(a), math.sin(a)

    def g(u, v):
        return (gx + ca * u - sa * v, gy + sa * u + ca * v)
    bd = [g(-h * 0.2, 0), g(-h * 0.17, -h * 0.1), g(-h * 0.07, -h * 0.1), g(-h * 0.02, -h * 0.06), g(h * 0.05, -h * 0.075),
          g(h * 0.1, 0), g(h * 0.05, h * 0.075), g(-h * 0.02, h * 0.06), g(-h * 0.07, h * 0.1), g(-h * 0.17, h * 0.1)]
    out.append(F(smooth_closed(bd), PAPER) + P(smooth_closed(bd), max(1.2, h * 0.02)))
    c_ = g(-h * 0.06, 0)
    out.append(f'<circle cx="{f1(c_[0])}" cy="{f1(c_[1])}" r="{f1(h * 0.028)}" fill="{INK}"/>')
    n0, n1 = g(h * 0.1, 0), g(h * 0.42, 0)
    out.append(P(f"M {f1(n0[0])} {f1(n0[1])} L {f1(n1[0])} {f1(n1[1])}", max(1.6, h * 0.03)))
    hd = g(h * 0.47, -h * 0.01)
    out.append(P(f"M {f1(n1[0])} {f1(n1[1])} L {f1(hd[0])} {f1(hd[1])}", max(2.4, h * 0.045)))
    # arm over the guitar
    out.append(P(f"M {f1(x - h * 0.1)} {f1(y - h * 0.74)} Q {f1(x - h * 0.16)} {f1(y - h * 0.58)} {f1(x - h * 0.06)} {f1(y - h * 0.5)}", h * 0.06))
    out.append(P(f"M {f1(x + h * 0.11)} {f1(y - h * 0.74)} Q {f1(x + h * 0.24)} {f1(y - h * 0.7)} {f1(g(h * 0.3, 0)[0])} {f1(g(h * 0.3, 0)[1])}", h * 0.06))
    # open case
    cs = [(x - h * 0.55, y + h * 0.02), (x - h * 0.2, y + h * 0.02), (x - h * 0.22, y + h * 0.1), (x - h * 0.53, y + h * 0.1)]
    out.append(F(cs, INK, 0.85) + P(poly(cs), 1.2))
    out.append(P(f"M {f1(x - h * 0.55)} {f1(y + h * 0.02)} L {f1(x - h * 0.6)} {f1(y - h * 0.12)} L {f1(x - h * 0.25)} {f1(y - h * 0.12)} L {f1(x - h * 0.2)} {f1(y + h * 0.02)}", 1.3))
    return "".join(out)


def blade_sign(U, x, ytop, w, h, icon, seed, accent_on=False, bulbs=True):
    """A projecting blade sign seen face-on: a rimmed panel with marquee bulbs and an icon (no lettering)."""
    out = []
    q = [(x - w / 2, ytop), (x + w / 2, ytop), (x + w / 2, ytop + h), (x - w / 2, ytop + h)]
    out.append(F(q, PAPER))
    if accent_on:
        out.append(accent(U, poly(q), bbox(q), seed, op=0.9, ang=-90, n=14, length=(8, 20), width=(1.5, 3)))
    inner = [(x - w / 2 + 3, ytop + 3), (x + w / 2 - 3, ytop + 3), (x + w / 2 - 3, ytop + h - 3), (x - w / 2 + 3, ytop + h - 3)]
    out.append(sketch(q, 1.8, seed, 0.6) + sketch(inner, 0.9, seed + 1, 0.3))
    if bulbs:
        b = []
        for t in [i / 7 for i in range(8)]:
            for xx in (x - w / 2 + 1.5, x + w / 2 - 1.5):
                b.append(f'<circle cx="{f1(xx)}" cy="{f1(ytop + 4 + t * (h - 8))}" r="1.1"/>')
        out.append(f'<g fill="{INK}">{"".join(b)}</g>')
    cx, cy, s = x, ytop + h / 2, min(w * 0.36, h * 0.3)
    if icon == "guitar":
        bd = [(cx, cy + s * 0.95), (cx - s * 0.6, cy + s * 0.6), (cx - s * 0.42, cy + s * 0.1), (cx - s * 0.32, cy - s * 0.12),
              (cx, cy - s * 0.05), (cx + s * 0.32, cy - s * 0.12), (cx + s * 0.42, cy + s * 0.1), (cx + s * 0.6, cy + s * 0.6)]
        out.append(F(smooth_closed(bd), INK, 0.9))
        out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy + s * 0.32)}" r="{f1(s * 0.14)}" fill="{PAPER}"/>')
        out.append(P(f"M {f1(cx)} {f1(cy - s * 0.05)} L {f1(cx)} {f1(cy - s * 1.0)}", max(1.4, s * 0.16)))
        out.append(F([(cx - s * 0.12, cy - s * 0.95), (cx + s * 0.12, cy - s * 0.95), (cx + s * 0.1, cy - s * 1.25), (cx - s * 0.1, cy - s * 1.25)], INK))
    elif icon == "boot":
        bt = [(cx - s * 0.3, cy - s), (cx + s * 0.2, cy - s), (cx + s * 0.18, cy + s * 0.25), (cx + s * 0.75, cy + s * 0.55),
              (cx + s * 0.75, cy + s * 0.85), (cx - s * 0.35, cy + s * 0.85), (cx - s * 0.38, cy + s * 0.2)]
        out.append(F(bt, INK, 0.9) + P(f"M {f1(cx - s * 0.2)} {f1(cy - s * 0.6)} q {f1(s * 0.2)} {f1(s * 0.2)} {f1(s * 0.3)} 0", 1.0, PAPER))
    elif icon == "star":
        out.append(F([(cx + math.cos(math.radians(-90 + i * 36)) * (s if i % 2 == 0 else s * 0.42),
                       cy + math.sin(math.radians(-90 + i * 36)) * (s if i % 2 == 0 else s * 0.42)) for i in range(10)], INK, 0.9))
    elif icon == "note":
        out.append(f'<ellipse cx="{f1(cx - s * 0.3)}" cy="{f1(cy + s * 0.6)}" rx="{f1(s * 0.32)}" ry="{f1(s * 0.24)}" fill="{INK}" transform="rotate(-20 {f1(cx - s * 0.3)} {f1(cy + s * 0.6)})"/>')
        out.append(P(f"M {f1(cx)} {f1(cy + s * 0.55)} L {f1(cx)} {f1(cy - s)} Q {f1(cx + s * 0.5)} {f1(cy - s * 0.6)} {f1(cx + s * 0.45)} {f1(cy - s * 0.1)}",
                     max(1.4, s * 0.14)))
    return "".join(out)


@design("nashville")
def nashville(U):
    """Lower Broadway at dusk: a row of brick honky-tonks with marquee blade signs (one boot sign in vermilion),
    the twin-spired tower beyond, a busker in the foreground; framed, with a ruled title cartouche."""
    out = [ground_paper(U, 71)]
    pic = [(56, 56), (544, 56), (544, 476), (56, 476)]
    C = Cam(f=360, cx=380, vpy=300, eye=4.0)
    art = []
    # sky
    sky = []
    y = 56
    while y < 300:
        sky.append(((56, y), (544, y)))
        y += lerp(7, 3.2, (y - 56) / 244)
    art.append(segs(sky, 0.6, 3, 0.15, op=0.35))
    art.append(cloud(U, 470, 92, 96, 14, 4))
    art.append(bird(424, 128, 6, 5) + bird(440, 116, 5, 6))
    # --- the twin-spired tower at the end of the street
    bx0, bx1 = 356, 410
    shaft = [(bx0, 168), (bx1, 168), (bx1, 300), (bx0, 300)]
    art.append(F(shaft, PAPER) + facade(U, [(bx0 + 2, 172), (bx1 - 2, 172), (bx1 - 2, 300), (bx0 + 2, 300)], 9, 18, "grid", 7, dark_p=0.08, w=0.7))
    art.append(F([(bx0 + 20, 168), (bx1 - 20, 168), (bx1 - 20, 300), (bx0 + 20, 300)], PAPER)
               + segs([((x_, 170), (x_, 300)) for x_ in (bx0 + 22, (bx0 + bx1) / 2, bx1 - 22)], 0.9, 8, 0))
    art.append(H(U, [(bx1 - 10, 168), (bx1, 168), (bx1, 300), (bx1 - 10, 300)], 90, 1.6, 0.8) + sketch(shaft, 1.5, 9, 0.6))
    crown = [(bx0, 168), (bx0 + 4, 150), (bx0 + 18, 150), ((bx0 + bx1) / 2, 116), (bx1 - 18, 150), (bx1 - 4, 150), (bx1, 168)]
    art.append(F(crown, PAPER) + H(U, [((bx0 + bx1) / 2, 116), (bx1 - 18, 150), (bx1 - 4, 150), (bx1, 168), ((bx0 + bx1) / 2, 168)], 90, 1.5, 0.8)
               + segs([((bx0 + 18, 150), (bx0 + 18, 168)), ((bx1 - 18, 150), (bx1 - 18, 168))], 1.0, 10, 0) + sketch(crown, 1.6, 11, 0.6, closed=False))
    for sx_ in (bx0 + 7, bx1 - 7):
        sp = [(sx_ - 4, 150), (sx_ - 1.5, 98), (sx_, 74), (sx_ + 1.5, 98), (sx_ + 4, 150)]
        art.append(F(sp, PAPER) + H(U, [(sx_, 74), (sx_ + 1.5, 98), (sx_ + 4, 150), (sx_, 150)], 90, 1.2, 0.7) + pen(sp, 1.5, 12, 0.05))
    # --- far buildings closing the street
    for i, (a, b, t) in enumerate(((312, 342, 262), (416, 440, 268), (440, 462, 252))):
        art.append(f'<g opacity="0.65">{prism(U, a, b, 4, t, 302, 13 + i, style="pane", dark_p=0.3, w=1.1)}</g>')
    # --- right side of the street: a shaded row of older brick fronts
    for i, (z0, z1, ht) in enumerate(((20, 30, 13), (30, 42, 10), (42, 58, 14), (58, 84, 11), (84, 130, 12))):
        q = [C(12, ht, z1), C(12, ht, z0), C(12, 0, z0), C(12, 0, z1)]
        art.append(F(q, PAPER))
        rows = int(ht / 3.4)
        art.append(facade(U, [C(12, ht - 1.2, z1 - 0.4), C(12, ht - 1.2, z0 + 0.4), C(12, 3.6, z0 + 0.4), C(12, 3.6, z1 - 0.4)],
                          max(2, int((z1 - z0) / 2.6)), rows, "dark", 20 + i, mx=0.28, my=0.2))
        art.append(XH(U, q, 80, 2.6, 0.8, ang2=20, gap2=3.4, op=0.85))
        art.append(F([C(12, 3.2, z1), C(12, 3.2, z0), C(12, 0.3, z0), C(12, 0.3, z1)], INK, 0.75))
        art.append(sketch(q, 1.4, 30 + i, 0.6))
        art.append(pen([C(12, ht, z1), C(11.4, ht + 0.6, z1), C(11.4, ht + 0.6, z0), C(12, ht, z0)], 1.4, 35 + i, 0.1))
    # --- the street: asphalt, centre dashes, curbs, a crosswalk
    road = [C(-8, 0, 8), C(-8, 0, 200), C(12, 0, 200), C(12, 0, 8)]
    art.append(F(road, PAPER) + H(U, road, 0, 3.0, 0.6, op=0.5))
    dashes = []
    for z in range(9, 160, 6):
        a, b = C(0, 0, z), C(0, 0, z + 3)
        dashes.append((a, b))
    art.append(segs(dashes, 1.4, 40, 0))
    cw = [poly([C(-8 + i * 1.2, 0, 13.5), C(-7.4 + i * 1.2, 0, 13.5), C(-7.4 + i * 1.2, 0, 16.5), C(-8 + i * 1.2, 0, 16.5)]) for i in range(14)]
    art.append(f'<path d="{" ".join(cw)}" fill="{PAPER}"/>')
    art.append(f'<path d="{" ".join(cw)}" fill="none" stroke="{INK}" stroke-width="1.0" opacity="0.8"/>')
    art.append(pen([C(-8, 0.15, 8), C(-8, 0.15, 200)], 1.6, 41, 0.1) + pen([C(-8, 0, 8), C(-8, 0, 200)], 1.0, 42, 0.1))
    # sidewalk paving
    walk = [C(-12, 0.15, 8), C(-12, 0.15, 200), C(-8, 0.15, 200), C(-8, 0.15, 8)]
    art.append(F(walk, PAPER) + segs([(C(-12, 0.15, z), C(-8, 0.15, z)) for z in [8 + i * 1.5 for i in range(60)]], 0.6, 43, 0, op=0.6))
    # --- the honky-tonk row on the left: brick, arched windows, cornices, storefronts, blade signs
    row = [(11.0, 18.0, 13.5, 3, "guitar"), (18.0, 24.0, 11.0, 2, "boot"), (24.0, 32.0, 14.0, 3, "note"), (32.0, 41.0, 12.0, 3, "star"),
           (41.0, 53.0, 15.0, 3, None), (53.0, 70.0, 11.5, 3, None), (70.0, 100.0, 13.0, 3, None)]
    rnd = random.Random(44)
    signs = []
    for i, (z0, z1, ht, floors, icon) in enumerate(row):
        X = -12
        q = C.qx(X, z0, z1, 0, ht)
        art.append(F(q, PAPER))
        # brick courses
        courses = [(C(X, yy, z0), C(X, yy, z1)) for yy in [0.32 * k for k in range(1, int(ht / 0.32))]]
        art.append(segs(courses, 0.5, 45 + i, 0, op=0.4 if z0 < 30 else 0.3))
        # upper windows: tall round-headed, per bay
        nb = max(2, int((z1 - z0) / 2.2))
        bw = (z1 - z0) / nb
        wins = []
        heads = []
        for f_ in range(floors - 1):
            y0 = 4.4 + f_ * ((ht - 5.4) / (floors - 1))
            y1 = y0 + (ht - 5.4) / (floors - 1) * 0.66
            for b in range(nb):
                za, zb = z0 + b * bw + bw * 0.3, z0 + (b + 1) * bw - bw * 0.3
                pts_ = [C(X, y0, za), C(X, y0, zb)]
                for k in range(0, 9):
                    t = k / 8
                    ang = math.pi * t
                    zz = (za + zb) / 2 + (zb - za) / 2 * math.cos(ang)
                    yy = y1 + (zb - za) * 0.45 * math.sin(ang)
                    pts_.append(C(X, yy, zz))
                pts_ = [pts_[0], pts_[1]] + pts_[2:]
                wins.append(pts_)
                if abs(pts_[1][0] - pts_[0][0]) > 5:
                    heads.append([C(X, y1 + (zb - za) * 0.45 + 0.25, (za + zb) / 2)])
        art.append(f'<path d="{" ".join(poly(w_) for w_ in wins)}" fill="{INK}" opacity="0.84"/>')
        art.append(f'<path d="{" ".join(poly(w_) for w_ in wins)}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
        # sash bars on the near windows
        bars = []
        for w_ in wins:
            if abs(w_[1][0] - w_[0][0]) > 6:
                m0, m1 = w_[0], w_[1]
                top_ = w_[6]
                bars.append(((m0[0] * 0.5 + m1[0] * 0.5, m0[1] * 0.5 + m1[1] * 0.5), top_))
        art.append(segs(bars, 0.9, 50 + i, 0, color=PAPER, op=0.85))
        # cornice with brackets
        cor = [C(X, ht, z0), C(X, ht, z1), C(X + 0.5, ht - 0.7, z1), C(X + 0.5, ht - 0.7, z0)]
        art.append(F(cor, PAPER) + H(U, cor, 90, 1.6, 0.7))
        br = []
        z = z0 + 0.3
        while z < z1:
            a, b = C(X, ht - 0.7, z), C(X, ht - 1.3, z)
            if abs(C(X, ht, z + 0.6)[0] - a[0]) > 1.6:
                br.append((a, b))
            z += 0.6
        art.append(segs(br, 1.2, 55 + i, 0))
        art.append(pen([cor[0], cor[1]], 1.8, 56 + i, 0.1) + pen([cor[3], cor[2]], 1.1, 57 + i, 0.1))
        # storefront: dark glass, transom, door, pilasters
        sf = C.qx(X, z0 + 0.4, z1 - 0.4, 0.4, 3.3)
        art.append(F(sf, INK, 0.82))
        art.append(segs([(C(X, 2.6, z0 + 0.4), C(X, 2.6, z1 - 0.4))] + [(C(X, 0.4, z), C(X, 3.3, z)) for z in [z0 + 0.4 + k * (z1 - z0 - 0.8) / 4 for k in range(1, 4)]],
                        1.0, 58 + i, 0, color=PAPER, op=0.8))
        art.append(pen([C(X, 3.9, z0), C(X, 3.9, z1)], 1.6, 59 + i, 0.1))
        art.append(pen([C(X, 0, z0), C(X, ht, z0)], 2.2 if z0 < 30 else 1.4, 60 + i, 0.1))
        if icon:
            zc = z0 + (3.2 if i == 0 else 0.9)
            a = C(X, 8.2, zc)
            b = C(X + 2.4, 8.2, zc)
            c_ = C(X + 2.4, 4.6, zc)
            w_ = b[0] - a[0]
            h_ = c_[1] - b[1]
            signs.append((a[0] + w_ / 2 + 2, b[1], w_, h_, icon, 70 + i, icon == "boot", a, b))
    # pickup truck parked at the curb, people on the sidewalk
    art.append(car(U, *C(-6.6, 0, 26), 360 * 5.2 / 26, 80, flip=True, kind="classic"))
    for X, z, sd, fl in ((-9.4, 19, 1, False), (-10.2, 29, 2, True), (-9.0, 36, 3, False), (-10.6, 47, 4, True), (-9.6, 64, 5, False)):
        art.append(person(*C(X, 0.15, z), 360 * 1.75 / z, 90 + sd, flip=fl, bag=sd == 3))
    for X, z, sd in ((10.2, 34, 6), (9.4, 50, 7)):
        art.append(person(*C(X, 0.15, z), 360 * 1.75 / z, 95 + sd))
    # lamp posts along the curb
    for z in (16, 30, 56):
        x_, yb = C(-8.3, 0.15, z)
        art.append(lamp(x_, yb, 360 * 4.8 / z, 99 + z, "globe", max(1.1, 30 / z)))
    # traffic seen from behind, people on the crosswalk
    for X, z, sd in ((3.2, 30, 1), (-3.4, 52, 2), (4.0, 78, 3)):
        x_, y_ = C(X, 0, z)
        w_ = 360 * 1.9 / z
        body = [(x_ - w_ / 2, y_ - w_ * 0.18), (x_ - w_ / 2, y_ - w_ * 0.5), (x_ - w_ * 0.36, y_ - w_ * 0.78), (x_ + w_ * 0.36, y_ - w_ * 0.78),
                (x_ + w_ / 2, y_ - w_ * 0.5), (x_ + w_ / 2, y_ - w_ * 0.18)]
        art.append(F([(x_ - w_ * 0.46, y_ - w_ * 0.2), (x_ - w_ * 0.46, y_), (x_ - w_ * 0.3, y_), (x_ - w_ * 0.3, y_ - w_ * 0.2)], INK)
                   + F([(x_ + w_ * 0.46, y_ - w_ * 0.2), (x_ + w_ * 0.46, y_), (x_ + w_ * 0.3, y_), (x_ + w_ * 0.3, y_ - w_ * 0.2)], INK))
        art.append(F(body, PAPER) + H(U, body, 0, 1.6, 0.7, span=(0.0, 0.45), dark=(x_, y_)) + sketch(body, max(1.0, w_ * 0.03), 120 + sd, 0.3))
        art.append(F([(x_ - w_ * 0.3, y_ - w_ * 0.52), (x_ - w_ * 0.24, y_ - w_ * 0.72), (x_ + w_ * 0.24, y_ - w_ * 0.72), (x_ + w_ * 0.3, y_ - w_ * 0.52)], INK, 0.85))
        art.append(F([(x_ - w_ * 0.46, y_ - w_ * 0.44), (x_ - w_ * 0.32, y_ - w_ * 0.44), (x_ - w_ * 0.32, y_ - w_ * 0.36), (x_ - w_ * 0.46, y_ - w_ * 0.36)], INK)
                   + F([(x_ + w_ * 0.46, y_ - w_ * 0.44), (x_ + w_ * 0.32, y_ - w_ * 0.44), (x_ + w_ * 0.32, y_ - w_ * 0.36), (x_ + w_ * 0.46, y_ - w_ * 0.36)], INK))
    for X, sd, fl in ((-5.5, 1, False), (-4.6, 2, False), (1.5, 3, True), (6.0, 4, True)):
        art.append(person(*C(X, 0, 15), 360 * 1.72 / 15, 130 + sd, flip=fl, bag=sd == 2))
    # festoon lights strung across the street
    for zl, zr, sd in ((14, 22, 1), (30, 38, 2), (50, 58, 3)):
        a, b = C(-12, 10.4, zl), C(12, 10.4, zr)
        mid = ((a[0] + b[0]) / 2, max(a[1], b[1]) + 360 * 1.2 / ((zl + zr) / 2))
        art.append(P(f"M {f1(a[0])} {f1(a[1])} Q {f1(2 * mid[0] - (a[0] + b[0]) / 2)} {f1(2 * mid[1] - (a[1] + b[1]) / 2)} {f1(b[0])} {f1(b[1])}",
                     max(0.9, 20 / zl), INK, 0.95))
        bulbs = []
        for k in range(1, 18):
            t = k / 18
            qx = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * (2 * mid[0] - (a[0] + b[0]) / 2) + t * t * b[0]
            qy = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * (2 * mid[1] - (a[1] + b[1]) / 2) + t * t * b[1]
            bulbs.append(f'<circle cx="{f1(qx)}" cy="{f1(qy + 2.6)}" r="{max(1.1, 34 / zl):.2f}"/>')
        art.append(f'<g fill="{PAPER}" stroke="{INK}" stroke-width="1.1">{"".join(bulbs)}</g>')
    # blade signs (drawn last, they hang over the sidewalk)
    for sx_, sy_, w_, h_, icon, sd, acc, a, b in signs:
        art.append(segs([((a[0], a[1] - 2), (b[0] + 2, b[1] - 2)), ((a[0], a[1] + h_ * 0.5), (b[0], b[1] + 4))], 1.3, sd, 0))
        art.append(blade_sign(U, sx_, sy_, w_ * 0.8, h_, icon, sd, accent_on=acc))
    # the busker in the foreground
    art.append(busker(124, 432, 62, 110))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 111, 1.4))
    out.append(border(U, 46, 46, 554, 554, 112, double=False, w=(1.2, 1.2)))
    out.append(cartouche(U, "nashville", 300, 486, 436, 98, 113))
    out.append(finish(U))
    return "".join(out)


# ================================================================ BOSTON
def brick_wall(U, q, seed, course=3.2, op=0.45, w=0.55):
    """Brick courses with staggered head joints on a flat wall quad [TL, TR, BR, BL] (axis-aligned)."""
    rnd = random.Random(seed)
    (x0, y0), (x1, _), (_, y1), _ = q
    lines, joints = [], []
    y = y0 + course
    k = 0
    while y < y1:
        lines.append(((x0, y), (x1, y)))
        x = x0 + (k % 2) * course * 1.4 + rnd.uniform(0, 1.0)
        while x < x1:
            joints.append(((x, y - course), (x, y)))
            x += course * 2.8
        y += course
        k += 1
    return clipped(U("bw"), poly(q), segs(lines, w, seed, 0.2, op=op) + segs(joints, w * 0.9, seed + 1, 0, op=op * 0.8))


def sash(U, x0, y0, x1, y1, seed, rows=3, cols=2, dark=False, keystone=True, w=1.3):
    """A Georgian sash window: stone lintel with keystone, sill, glazing bars, dark panes."""
    out = []
    q = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out.append(F(q, INK, 0.82 if not dark else 0.9))
    bars = [((x0 + (x1 - x0) * i / cols, y0), (x0 + (x1 - x0) * i / cols, y1)) for i in range(1, cols)]
    bars += [((x0, y0 + (y1 - y0) * j / rows), (x1, y0 + (y1 - y0) * j / rows)) for j in range(1, rows)]
    out.append(segs(bars, 0.9, seed, 0, color=PAPER, op=0.85))
    out.append(sketch(q, w, seed, 0.3))
    lt = [(x0 - 3, y0 - 5), (x1 + 3, y0 - 5), (x1 + 2, y0), (x0 - 2, y0)]
    out.append(F(lt, PAPER) + H(U, lt, 0, 1.4, 0.6) + sketch(lt, 1.1, seed + 1, 0.3))
    if keystone:
        m = (x0 + x1) / 2
        out.append(F([(m - 2.5, y0 - 7), (m + 2.5, y0 - 7), (m + 1.8, y0 + 1), (m - 1.8, y0 + 1)], PAPER)
                   + pen([(m - 2.5, y0 - 7), (m + 2.5, y0 - 7), (m + 1.8, y0 + 1), (m - 1.8, y0 + 1)], 1.0, seed, 0, closed=True))
    out.append(seg(x0 - 3, y1 + 1.5, x1 + 3, y1 + 1.5, 1.6, seed + 2, 0))
    return "".join(out)


def heraldic_beast(x, y, s, kind="lion", flip=False, seed=1):
    """A small rampant lion or unicorn (reared on the hind legs, forepaws raised) for the gable shoulders."""
    k = -1 if flip else 1

    def p(u, v):
        return (x + k * u * s, y + v * s)
    body = [(-0.24, 0), (-0.08, 0), (-0.08, -0.12), (0.04, -0.1), (0.14, 0), (0.26, 0), (0.16, -0.16), (0.12, -0.3), (0.18, -0.42),
            (0.34, -0.5), (0.44, -0.62), (0.38, -0.66), (0.26, -0.56), (0.2, -0.58), (0.3, -0.7), (0.4, -0.76), (0.34, -0.8),
            (0.22, -0.74), (0.22, -0.82), (0.32, -0.86), (0.4, -0.86), (0.38, -0.94), (0.26, -1.0), (0.14, -0.98), (0.06, -0.88),
            (0.04, -0.72), (-0.06, -0.56), (-0.12, -0.36), (-0.2, -0.2)]
    out = [F([p(u, v) for u, v in body], INK, 0.95)]
    out.append(nib([p(-0.16, -0.28), p(-0.36, -0.46), p(-0.32, -0.7), p(-0.22, -0.74)], max(1.3, s * 0.05), taper=(1, 0.5), seed=seed, color=INK))
    if kind == "lion":
        rnd = random.Random(seed)
        mane = []
        for i in range(14):
            a = math.pi * 0.55 + 2 * math.pi * i / 14
            r = 0.17 if i % 2 else 0.11
            mane.append(p(0.16 + math.cos(a) * r, -0.86 + math.sin(a) * r * 1.1 + rnd.uniform(-0.01, 0.01)))
        out.append(F(mane, INK, 0.95))
        out.append(F([p(-0.36, -0.7), p(-0.26, -0.82), p(-0.2, -0.72)], INK))
    else:
        out.append(nib([p(0.3, -0.97), p(0.52, -1.2)], max(1.3, s * 0.05), taper=(1, 0.1), seed=seed, color=INK))
        out.append(nib([p(0.12, -0.96), p(0.02, -0.84), p(0.0, -0.66)], max(1.3, s * 0.06), taper=(0.6, 0.2), seed=seed + 1, color=INK))
    return "".join(out)


@design("boston")
def boston(U):
    """The Old State House from State Street, looking up: brick, stepped gable with lion and unicorn, the
    balcony hung with vermilion bunting, the tiered steeple, towers of the Financial District crowding behind,
    the cobblestone ring in the street. Notched frame with the title cartouche at the head."""
    out = [ground_paper(U, 81)]
    notch = 18
    x0, y0, x1, y1 = 52, 52, 548, 548
    pic = [(x0 + notch, y0), (x1 - notch, y0), (x1, y0 + notch), (x1, y1 - notch), (x1 - notch, y1), (x0 + notch, y1), (x0, y1 - notch),
           (x0, y0 + notch)]
    art = []
    # sky rules
    art.append(segs([((0, y), (600, y)) for y in range(60, 420, 6)], 0.55, 3, 0.15, op=0.35))
    art.append(cloud(U, 226, 222, 70, 12, 4, shade=True))
    # --- the towers crowding behind (worm's-eye: verticals lean in)
    def lean_tower(xa, xb, top, base, lean, seed, style, sw=10, cols=None, rows=None):
        q = [(xa + lean, top), (xb + lean, top), (xb, base), (xa, base)]
        o = [F(q, PAPER)]
        c = cols or max(3, int((xb - xa) / 8))
        r = rows or int((base - top) / 9)
        o.append(facade(U, [(xa + lean + 2, top + 4), (xb + lean - 2, top + 4), (xb - 2, base), (xa + 2, base)], c, r, style, seed, dark_p=0.025, w=0.8))
        if sw:
            if lean > 0:
                side = [(xa + lean - sw, top + 3), (xa + lean, top), (xa, base), (xa - sw * 1.2, base)]
            else:
                side = [(xb + lean, top), (xb + lean + sw, top + 3), (xb + sw * 1.2, base), (xb, base)]
            o.append(F(side, PAPER) + XH(U, side, 80, 1.8, 0.8, ang2=20, gap2=2.6) + sketch(side, 1.3, seed + 1, 0.6))
        o.append(sketch(q, 1.6, seed + 2, 0.8))
        return "".join(o)
    art.append(lean_tower(60, 150, 40, 420, 14, 11, "slit", sw=0, rows=40))
    art.append(lean_tower(150, 218, 120, 420, 8, 12, "pane", sw=12))
    art.append(lean_tower(392, 456, 96, 420, -8, 13, "slit", sw=12))
    art.append(lean_tower(456, 560, 30, 420, -14, 14, "slit", sw=0, cols=12, rows=44))
    # the gold-capped tower on the right: pyramidal pinnacle crown (75 State Street style)
    cx_ = 424
    crown = [(cx_ - 26, 96), (cx_ - 22, 78), (cx_ - 12, 78), (cx_ - 12, 66), (cx_, 50), (cx_ + 12, 66), (cx_ + 12, 78), (cx_ + 22, 78), (cx_ + 26, 96)]
    art.append(F(crown, PAPER) + H(U, [(cx_, 50), (cx_ + 12, 66), (cx_ + 12, 78), (cx_ + 22, 78), (cx_ + 26, 96), (cx_, 96)], 90, 1.4, 0.7)
               + sketch(crown, 1.5, 15, 0.6, closed=False))
    art.append(seg(cx_, 50, cx_, 40, 1.4, 16, 0))
    # --- the Old State House: tower first (behind the gable)
    TX = 300
    G = 290                      # height of the gable peak; the steeple is set out from it
    s1 = [(TX - 28, G - 28), (TX + 28, G - 28), (TX + 28, G + 30), (TX - 28, G + 30)]
    art.append(F(s1, PAPER) + brick_wall(U, s1, 17, 3.0) + H(U, [(TX + 12, G - 28), (TX + 28, G - 28), (TX + 28, G + 30), (TX + 12, G + 30)], 90, 1.6, 0.8))
    art.append(sketch(s1, 1.8, 19, 0.8))
    cor1 = [(TX - 32, G - 34), (TX + 32, G - 34), (TX + 32, G - 28), (TX - 32, G - 28)]
    art.append(F(cor1, PAPER) + H(U, cor1, 0, 1.6, 0.7) + sketch(cor1, 1.6, 20, 0.6))
    art.append(segs([((x, G - 42), (x, G - 34)) for x in range(TX - 30, TX + 32, 4)], 1.0, 21, 0) + pen([(TX - 32, G - 42), (TX + 32, G - 42)], 1.6, 22, 0.1))
    # stage 2: arcaded belfry
    s2 = [(TX - 21, G - 86), (TX + 21, G - 86), (TX + 21, G - 42), (TX - 21, G - 42)]
    art.append(F(s2, PAPER))
    for ax in (TX - 16, TX - 4, TX + 8):
        a_ = arch_window_pts(ax, ax + 8, G - 78, G - 46, spring=0.3, n=8)
        art.append(F(a_, INK, 0.86) + pen(a_, 1.0, int(ax), 0.05))
    art.append(H(U, [(TX + 10, G - 86), (TX + 21, G - 86), (TX + 21, G - 42), (TX + 10, G - 42)], 90, 1.5, 0.7))
    art.append(sketch(s2, 1.6, 24, 0.6))
    cor2 = [(TX - 25, G - 92), (TX + 25, G - 92), (TX + 25, G - 86), (TX - 25, G - 86)]
    art.append(F(cor2, PAPER) + H(U, cor2, 0, 1.5, 0.7) + sketch(cor2, 1.5, 25, 0.5))
    for ux in (TX - 25, TX + 25):
        art.append(F(smooth_closed([(ux - 3, G - 92), (ux - 4, G - 97), (ux - 2, G - 102), (ux + 2, G - 102), (ux + 4, G - 97), (ux + 3, G - 92)]), INK, 0.85))
        art.append(seg(ux, G - 102, ux, G - 106, 1.2, ux, 0))
    # stage 3: octagonal lantern
    s3 = [(TX - 12, G - 120), (TX + 12, G - 120), (TX + 12, G - 92), (TX - 12, G - 92)]
    art.append(F(s3, PAPER) + segs([((TX - 6, G - 118), (TX - 6, G - 92)), ((TX + 6, G - 118), (TX + 6, G - 92))], 1.0, 26, 0))
    for ax in (TX - 10, TX - 2, TX + 7):
        a_ = arch_window_pts(ax, ax + 3.5, G - 115, G - 96, spring=0.25, n=6)
        art.append(F(a_, INK, 0.85))
    art.append(H(U, [(TX + 6, G - 120), (TX + 12, G - 120), (TX + 12, G - 92), (TX + 6, G - 92)], 90, 1.4, 0.7) + sketch(s3, 1.5, 27, 0.5))
    # ogee cupola + finial + vane
    c0 = G - 120
    cup = [(TX - 14, c0), (TX - 13, c0 - 6), (TX - 7, c0 - 12), (TX - 3, c0 - 18), (TX, c0 - 24), (TX + 3, c0 - 18), (TX + 7, c0 - 12), (TX + 13, c0 - 6), (TX + 14, c0)]
    art.append(F(smooth_closed(cup), PAPER) + clipped(U("cu"), smooth_closed(cup), H(U, cup, 90, 1.4, 0.8, span=(0.5, 1), dark=(TX + 15, c0 - 4), box=bbox(cup)))
               + pen(cup, 1.6, 28, 0.05, smooth=True))
    art.append(seg(TX, c0 - 24, TX, c0 - 40, 1.5, 29, 0) + f'<circle cx="{TX}" cy="{c0 - 30}" r="2.2" fill="{INK}"/>')
    art.append(F([(TX, c0 - 40), (TX + 12, c0 - 38.5), (TX + 9, c0 - 36), (TX, c0 - 36)], INK) + seg(TX - 5, c0 - 34, TX + 5, c0 - 34, 1.0, 30, 0))
    # --- the east gable end
    GL, GR, EAVE, BASE = 168, 432, 398, 532
    wall = [(GL, EAVE), (GR, EAVE), (GR, BASE), (GL, BASE)]
    art.append(F(wall, PAPER) + brick_wall(U, wall, 31, 3.2, op=0.5))
    # stepped / scrolled gable
    gab = [(GL - 4, EAVE), (GL + 22, EAVE - 6), (GL + 28, EAVE - 28), (GL + 60, EAVE - 32), (GL + 66, EAVE - 54), (TX - 46, EAVE - 58),
           (TX - 40, EAVE - 86), (TX - 22, EAVE - 100), (TX, EAVE - 108), (TX + 22, EAVE - 100), (TX + 40, EAVE - 86), (TX + 46, EAVE - 58),
           (GR - 66, EAVE - 54), (GR - 60, EAVE - 32), (GR - 28, EAVE - 28), (GR - 22, EAVE - 6), (GR + 4, EAVE)]
    art.append(F(gab, PAPER) + clipped(U("gk"), poly(gab), brick_wall(U, [(GL, EAVE - 112), (GR, EAVE - 112), (GR, EAVE), (GL, EAVE)], 32, 3.2, op=0.5)))
    art.append(clipped(U("gb"), poly(gab), H(U, [(TX + 10, EAVE - 120), (GR + 8, EAVE - 120), (GR + 8, EAVE), (TX + 10, EAVE)], 90, 2.2, 0.8,
                                              span=(0.3, 1), dark=(GR, EAVE))))
    art.append(sketch(gab, 2.2, 33, 0.8, closed=False))
    # coping along the gable steps
    art.append(pen([(p_[0], p_[1] - 3) for p_ in gab[1:-1]], 1.2, 34, 0.1))
    # gable clock (round, stone surround) and the lion and unicorn on the shoulders
    art.append(f'<circle cx="{TX}" cy="{EAVE - 66}" r="20" fill="{PAPER}" stroke="{INK}" stroke-width="2.2"/>'
               f'<circle cx="{TX}" cy="{EAVE - 66}" r="15.5" fill="none" stroke="{INK}" stroke-width="0.9"/>')
    art.append(segs([((TX + math.cos(a) * 15.5, EAVE - 66 + math.sin(a) * 15.5), (TX + math.cos(a) * 19, EAVE - 66 + math.sin(a) * 19)) for a in [i * math.pi / 6 for i in range(12)]], 1.3, 35, 0))
    art.append(P(f"M {TX} {EAVE - 66} L {TX + 9} {EAVE - 62} M {TX} {EAVE - 66} L {TX - 3} {EAVE - 78}", 1.8))
    art.append(heraldic_beast(GL + 44, EAVE - 32, 32, "lion", flip=False, seed=36) + heraldic_beast(GR - 44, EAVE - 32, 32, "unicorn", flip=True, seed=37))
    # quoins
    for qx_, sg in ((GL, 1), (GR, -1)):
        for j, yy in enumerate(range(EAVE + 4, BASE, 13)):
            ww = 14 if j % 2 else 9
            qq = [(qx_, yy), (qx_ + sg * ww, yy), (qx_ + sg * ww, yy + 10), (qx_, yy + 10)]
            art.append(F(qq, PAPER) + sketch(qq, 0.9, 38 + j, 0.2))
    # windows: second and third floor, ground floor
    for i, wx in enumerate((196, 240, 344, 388)):
        art.append(sash(U, wx, EAVE + 14, wx + 22, EAVE + 48, 40 + i, rows=3))
        art.append(sash(U, wx, EAVE + 76, wx + 22, EAVE + 112, 50 + i, rows=3))
    # central balcony door + balcony with bunting (accent)
    dx0, dx1 = TX - 16, TX + 16
    door2 = arch_window_pts(dx0, dx1, EAVE + 10, EAVE + 62, spring=0.3, n=10)
    art.append(F(door2, INK, 0.86) + segs([((TX, EAVE + 20), (TX, EAVE + 62)), ((dx0, EAVE + 40), (dx1, EAVE + 40))], 1.0, 60, 0, color=PAPER) + pen(door2, 1.4, 61, 0.1))
    bal = [(TX - 36, EAVE + 62), (TX + 36, EAVE + 62), (TX + 36, EAVE + 66), (TX - 36, EAVE + 66)]
    art.append(F(bal, PAPER) + H(U, bal, 0, 1.2, 0.8) + sketch(bal, 1.6, 62, 0.4))
    art.append(segs([((x, EAVE + 50), (x, EAVE + 62)) for x in range(TX - 34, TX + 36, 4)], 0.9, 63, 0) + pen([(TX - 36, EAVE + 50), (TX + 36, EAVE + 50)], 1.5, 64, 0.1))
    bunt = []
    for k in range(3):
        a_ = TX - 36 + k * 24
        bunt.append(f"M {a_} {EAVE + 67} Q {a_ + 12} {EAVE + 84} {a_ + 24} {EAVE + 67} Q {a_ + 12} {EAVE + 76} {a_} {EAVE + 67} Z")
    bd = " ".join(bunt)
    art.append(F(bd, PAPER) + accent(U, bd, (TX - 38, EAVE + 64, TX + 38, EAVE + 86), 65, op=0.95, ang=0, n=16, length=(6, 16), width=(1.5, 3))
               + P(bd, 1.2))
    art.append(segs([((TX - 36, EAVE + 66), (TX - 36, EAVE + 72)), ((TX + 36, EAVE + 66), (TX + 36, EAVE + 72))], 1.0, 66, 0))
    # ground floor: door with fanlight, shop windows
    gd = arch_window_pts(TX - 15, TX + 15, EAVE + 92, BASE, spring=0.3, n=10)
    art.append(F(gd, INK, 0.88) + pen(gd, 1.6, 67, 0.1) + segs([((TX, EAVE + 104), (TX, BASE))], 1.0, 68, 0, color=PAPER))
    # string courses + eave cornice + plinth
    for yy, ww in ((EAVE + 2, 2.2), (EAVE + 6, 1.0), (EAVE + 64, 1.2), (EAVE + 122, 1.2)):
        art.append(seg(GL - 2, yy, GR + 2, yy, ww, int(yy), 0.2))
    art.append(H(U, [(GR - 40, EAVE), (GR, EAVE), (GR, BASE), (GR - 40, BASE)], 90, 2.0, 0.8, span=(0.4, 1), dark=(GR, 470)))
    art.append(pen([(GL, EAVE), (GL, BASE)], 2.4, 69, 0.2) + pen([(GR, EAVE), (GR, BASE)], 2.8, 70, 0.2))
    # --- street: lamp, people, the cobblestone ring
    st = [(0, BASE), (600, BASE), (600, 600), (0, 600)]
    art.append(F(st, PAPER) + H(U, st, 0, 3.0, 0.7, op=0.55))
    ring_c, ring_r = (300, 541), (50, 6)
    stones = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        stones.append(f'<ellipse cx="{f1(ring_c[0] + math.cos(a) * ring_r[0])}" cy="{f1(ring_c[1] + math.sin(a) * ring_r[1])}" rx="2.6" ry="1.5" '
                      f'fill="{PAPER}" stroke="{INK}" stroke-width="0.9"/>')
    art.append("".join(stones))
    art.append(seg(0, BASE, 600, BASE, 2.2, 71, 0.3))
    art.append(lamp(130, BASE + 4, 96, 72, "lantern", 2.0) + lamp(470, BASE + 4, 96, 73, "lantern", 2.0))
    art.append(person(176, BASE + 6, 40, 74) + person(190, BASE + 7, 37, 75, flip=True) + person(420, BASE + 8, 40, 76, bag=True)
               + person(92, BASE + 10, 42, 77, flip=True))
    art.append(bird(232, 150, 7, 78) + bird(250, 138, 5, 79) + bird(362, 128, 6, 80))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 81, 1.2))
    op_ = [(x0 - 6 + notch, y0 - 6), (x1 + 6 - notch, y0 - 6), (x1 + 6, y0 - 6 + notch), (x1 + 6, y1 + 6 - notch), (x1 + 6 - notch, y1 + 6),
           (x0 - 6 + notch, y1 + 6), (x0 - 6, y1 + 6 - notch), (x0 - 6, y0 - 6 + notch)]
    out.append(sketch(op_, 1.1, 82, 0.8))
    out.append(cartouche(U, "boston", 300, 96, 410, 94, 83, mx=56, name_k=0.06, cgap=30))
    out.append(finish(U))
    return "".join(out)


# ================================================================ SEATTLE
def ferry(U, x0, x1, wl, seed):
    """A double-ended car ferry broadside: hull with rubbing strake, car deck openings, passenger cabin with
    a long row of windows, sun deck rail, two wheelhouses, one funnel."""
    out = []
    L = x1 - x0
    hh = L * 0.075
    hull = [(x0 - 4, wl - hh), (x1 + 4, wl - hh), (x1 - 6, wl), (x0 + 6, wl)]
    out.append(F(hull, PAPER) + H(U, hull, 0, 1.6, 0.8, span=(0.3, 1), dark=((x0 + x1) / 2, wl)) + sketch(hull, 2.0, seed, 0.6))
    cd = [(x0 + 2, wl - hh - L * 0.06), (x1 - 2, wl - hh - L * 0.06), (x1 - 2, wl - hh), (x0 + 2, wl - hh)]
    out.append(F(cd, PAPER) + sketch(cd, 1.4, seed + 1, 0.4))
    ops = []
    n = 9
    for i in range(n):
        a = x0 + 8 + i * (L - 16) / n
        ops.append([(a + 2, wl - hh - L * 0.05), (a + (L - 16) / n - 2, wl - hh - L * 0.05), (a + (L - 16) / n - 2, wl - hh - 1), (a + 2, wl - hh - 1)])
    out.append(f'<path d="{" ".join(poly(o) for o in ops)}" fill="{INK}" opacity="0.85"/>')
    cab = [(x0 + L * 0.08, wl - hh - L * 0.06), (x1 - L * 0.08, wl - hh - L * 0.06), (x1 - L * 0.1, wl - hh - L * 0.12), (x0 + L * 0.1, wl - hh - L * 0.12)]
    out.append(F(cab, PAPER) + sketch(cab, 1.4, seed + 2, 0.4))
    m = homog([cab[3], cab[2], cab[1], cab[0]])
    wins = [[m((i + 0.18) / 22, 0.22), m((i + 0.82) / 22, 0.22), m((i + 0.82) / 22, 0.72), m((i + 0.18) / 22, 0.72)] for i in range(22)]
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.85"/>')
    yt = wl - hh - L * 0.12
    out.append(segs([((x, yt), (x, yt - 4)) for x in range(int(x0 + L * 0.1), int(x1 - L * 0.1), 4)], 0.8, seed, 0) + pen([(x0 + L * 0.1, yt - 4), (x1 - L * 0.1, yt - 4)], 1.1, seed, 0.1))
    for wx in (x0 + L * 0.14, x1 - L * 0.2):
        wh = [(wx, yt), (wx, yt - L * 0.05), (wx + L * 0.06, yt - L * 0.05), (wx + L * 0.06, yt)]
        out.append(F(wh, PAPER) + F([(wx + 1.5, yt - L * 0.04), (wx + L * 0.06 - 1.5, yt - L * 0.04), (wx + L * 0.06 - 1.5, yt - L * 0.025), (wx + 1.5, yt - L * 0.025)], INK, 0.85)
                   + sketch(wh, 1.3, seed + 3, 0.3))
    fx = (x0 + x1) / 2
    fn = [(fx - L * 0.03, yt), (fx - L * 0.025, yt - L * 0.08), (fx + L * 0.03, yt - L * 0.08), (fx + L * 0.035, yt)]
    out.append(F(fn, PAPER) + H(U, fn, 90, 1.3, 0.7, span=(0.5, 1), dark=(fx + 10, yt)) + F([(fn[1][0], fn[1][1]), (fn[2][0], fn[2][1]), (fn[2][0], fn[2][1] + 4), (fn[1][0], fn[1][1] + 4)], INK)
               + sketch(fn, 1.3, seed + 4, 0.3))
    out.append(P(f"M {f1(x1 - 4)} {f1(wl - 2)} q 30 4 64 12 M {f1(x1 - 10)} {f1(wl)} q 20 6 44 16 M {f1(x0 + 8)} {f1(wl)} q -30 4 -60 6", 1.1, INK, 0.85))
    return "".join(out)


def great_wheel(U, cx, cy, r, base, seed):
    """The observation wheel on the pier: rim truss, spokes, hub, gondolas, A-frame legs."""
    out = []
    # legs
    for sg in (-1, 1):
        out.append(nib([(cx, cy), (cx + sg * r * 0.55, base)], 3.0, taper=(0.8, 1), seed=seed + sg, color=INK))
        out.append(nib([(cx, cy), (cx + sg * r * 0.3, base)], 2.0, taper=(0.8, 1), seed=seed + sg + 3, color=INK))
    out.append(segs([((cx - r * 0.42, base - r * 0.25), (cx + r * 0.42, base - r * 0.25))], 1.2, seed, 0))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.93)}" fill="none" stroke="{INK}" stroke-width="1.0"/>')
    sp, tr = [], []
    for i in range(42):
        a = 2 * math.pi * i / 42
        sp.append(((cx + math.cos(a) * r * 0.08, cy + math.sin(a) * r * 0.08), (cx + math.cos(a) * r * 0.93, cy + math.sin(a) * r * 0.93)))
        a2 = 2 * math.pi * (i + 0.5) / 42
        tr.append(((cx + math.cos(a) * r * 0.93, cy + math.sin(a) * r * 0.93), (cx + math.cos(a2) * r, cy + math.sin(a2) * r)))
    out.append(segs(sp, 0.55, seed, 0, op=0.85) + segs(tr, 0.6, seed + 1, 0))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.1)}" fill="{INK}"/>')
    gond = []
    for i in range(14):
        a = 2 * math.pi * i / 14 + 0.1
        gx, gy = cx + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1)
        gond.append(f'<rect x="{f1(gx - 2.6)}" y="{f1(gy)}" width="5.2" height="5.6" rx="1.4" fill="{INK}"/>')
    out.append("".join(gond))
    return "".join(out)


def mountain(U, peak, left, right, base, seed, op=0.9):
    """A glaciated volcano in engraved line: rough ridgeline, snowfields left as paper, rock ribs and the
    shaded east face hatched."""
    rnd = random.Random(seed)
    px, py = peak
    pts = [(left, base)]
    k = 16
    Hh = base - py
    for i in range(1, k):
        d = 1 - i / k
        x = lerp(px - 22, left, d)
        y = py + 6 + (Hh - 6) * d ** 0.85 + rnd.uniform(-2, 2) * d
        pts.append((x, y))
    # broad summit dome with a lesser cap on the left
    pts += [(px - 22, py + 7), (px - 16, py + 3), (px - 8, py + 2), (px - 2, py), (px + 8, py + 1), (px + 18, py + 4), (px + 26, py + 8)]
    for i in range(1, k):
        d = i / k
        x = lerp(px + 26, right, d)
        y = py + 8 + (Hh - 8) * d ** 0.8 + rnd.uniform(-2, 2) * d
        pts.append((x, y))
    pts.append((right, base))
    out = [F(pts, PAPER)]
    # east flank in shade: slope-parallel hatching, darker toward the right
    inner = H(U, poly(pts), 58, (3.2, 1.8), (0.7, 1.0), box=bbox(pts), span=(0.5, 1), dark=(right, base), wob=0.3, brk=0.2)
    # rock ridges between the glaciers, radiating from the summit (tapered pen strokes)
    for i in range(11):
        f = (i + 0.5) / 11
        sx_ = px - 30 + 60 * f + rnd.uniform(-4, 4)
        ang = math.radians(lerp(128, 52, f) + rnd.uniform(-6, 6))
        L = rnd.uniform(0.45, 0.85) * Hh / max(0.35, math.sin(ang))
        mid = (sx_ + math.cos(ang) * L * 0.5 + rnd.uniform(-6, 6), py + 8 + math.sin(ang) * L * 0.5)
        end = (sx_ + math.cos(ang) * L, py + 8 + math.sin(ang) * L)
        inner += nib([(sx_, py + 8 + rnd.uniform(0, 6)), mid, end], rnd.uniform(1.6, 3.2) * (1.3 if f > 0.5 else 0.8), taper=(0.2, 0.3), ramp=0.4,
                     seed=seed + i, color=INK, op=0.85)
    # crevasse ticks on the snowfields
    cv = []
    for _ in range(46):
        t = rnd.random()
        yy = py + 16 + t * Hh * 0.55
        half = (yy - py) * 1.3
        x = px + rnd.uniform(-half, half * 0.4)
        cv.append(((x, yy), (x + rnd.uniform(4, 9), yy + rnd.uniform(-1, 1))))
    inner += segs(cv, 0.6, seed + 20, 0.4, op=0.6)
    # forested foothills along the base
    fh_ = []
    for x in range(int(left), int(right), 3):
        h_ = rnd.uniform(4, 12)
        fh_.append(((x, base), (x + rnd.uniform(-1, 1), base - h_)))
    inner += segs(fh_, 1.0, seed + 30, 0.3, op=0.8)
    out.append(clipped(U("mt"), poly(pts), inner))
    out.append(pen(pts[1:-1], 1.8, seed, 0.2))
    return f'<g opacity="{op:.2f}">' + "".join(out) + "</g>"


@design("seattle")
def seattle(U):
    """Elliott Bay panorama: the mountain under a lenticular cap, the downtown towers, the observation wheel on
    its pier, a car ferry crossing and a red tug; letterboxed between the name and the coordinates."""
    out = [ground_paper(U, 91)]
    bx0, by0, bx1, by1 = 46, 134, 554, 478
    band = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
    art = []
    HZ = 352
    sky = []
    y = by0 + 4
    while y < HZ:
        sky.append(((bx0, y), (bx1, y)))
        y += lerp(7.5, 3.2, (y - by0) / (HZ - by0))
    art.append(segs(sky, 0.55, 3, 0.15, op=0.4))
    # the mountain and its lenticular cap
    art.append(mountain(U, (446, 204), 236, 640, HZ - 6, 4))
    for k, (w_, dy) in enumerate(((100, 0), (80, -7), (56, -13))):
        d = f"M {446 - w_ / 2} {186 + dy} Q 446 {174 + dy - 6} {446 + w_ / 2} {186 + dy} Q 446 {190 + dy} {446 - w_ / 2} {186 + dy} Z"
        art.append(F(d, PAPER) + P(d, 1.2 - k * 0.2) + H(U, d, 0, 2.0, 0.6, box=(446 - w_, 160 + dy, 446 + w_, 194 + dy), span=(0.62, 1), dark=(446, 200)))
    art.append(cloud(U, 132, 186, 120, 16, 5))
    # --- the towers
    BASE = 358
    far = [(80, 100, 300), (104, 122, 284), (290, 306, 296), (312, 330, 306)]
    art.append("".join(F([(a, t), (b + 4, t), (b + 4, BASE), (a, BASE)], PAPER) for a, b, t in far))
    art.append(f'<g opacity="0.5">{"".join(prism(U, a, b, 4, t, BASE, 10 + i, style="grid", dark_p=0.1, w=1.0) for i, (a, b, t) in enumerate(far))}</g>')
    # 1201 Third: pointed crown
    art.append(prism(U, 150, 178, 7, 222, BASE, 21, cols=5, rows=22, style="slit"))
    cr_ = [(150, 222), (157, 208), (164, 196), (171, 208), (178, 222)]
    art.append(F(cr_, PAPER) + H(U, [(164, 196), (171, 208), (178, 222), (164, 222)], 90, 1.4, 0.7) + segs([((157, 208), (171, 208)), ((164, 196), (164, 222))], 0.9, 22, 0)
               + pen(cr_, 1.5, 23, 0.1) + seg(164, 196, 164, 184, 1.2, 24, 0))
    # Columbia Center: dark stepped tower
    cc = [(196, 246), (196, 202), (204, 202), (204, 186), (214, 186), (214, 172), (236, 172), (236, 186), (246, 186), (246, 202), (254, 202),
          (254, 360), (196, 360)]
    art.append(F(cc, PAPER) + clipped(U("cc"), poly(cc), XH(U, cc, 90, 2.0, 0.9, ang2=0, gap2=3.0) + H(U, cc, 90, 1.6, 0.9, span=(0.55, 1), dark=(260, 300))))
    art.append(segs([((204, 202), (204, 360)), ((214, 186), (214, 360)), ((236, 186), (236, 360)), ((246, 202), (246, 360))], 1.1, 25, 0, color=PAPER, op=0.75))
    art.append(sketch(cc, 1.6, 26, 0.6))
    # Municipal Tower: stepped shoulders
    art.append(prism(U, 262, 290, 7, 232, BASE, 27, cols=5, rows=18, style="grid", dark_p=0.18))
    art.append(prism(U, 268, 284, 4, 220, 232, 28, cols=3, rows=2, style="grid", dark_p=0.1))
    # others in the mid row
    for i, (a, b, t, st) in enumerate(((60, 92, 296, "pane"), (96, 130, 270, "slit"), (128, 150, 250, "grid"), (178, 196, 286, "pane"),
                                       (254, 266, 300, "slit"), (296, 318, 288, "pane"), (318, 344, 312, "grid"))):
        art.append(prism(U, a, b, 6, t, BASE, 30 + i, style=st, dark_p=0.2, w=1.3))
    # Smith Tower: white shaft and pyramid cap, older and shorter, to the right
    sx = 382
    sm = [(sx - 10, 270), (sx + 10, 270), (sx + 10, BASE), (sx - 10, BASE)]
    art.append(F([(sx - 22, 312), (sx + 24, 312), (sx + 24, BASE), (sx - 22, BASE)], PAPER)
               + facade(U, [(sx - 20, 316), (sx + 22, 316), (sx + 22, BASE), (sx - 20, BASE)], 7, 5, "pane", 39) + sketch([(sx - 22, 312), (sx + 24, 312), (sx + 24, BASE), (sx - 22, BASE)], 1.4, 40, 0.5))
    art.append(F(sm, PAPER) + facade(U, [(sx - 8, 274), (sx + 8, 274), (sx + 8, 312), (sx - 8, 312)], 3, 7, "pane", 41) + H(U, [(sx + 4, 270), (sx + 10, 270), (sx + 10, 312), (sx + 4, 312)], 90, 1.3, 0.7)
               + sketch(sm, 1.4, 42, 0.5))
    pyr = [(sx - 11, 270), (sx, 246), (sx + 11, 270)]
    art.append(F(pyr, PAPER) + H(U, [(sx, 246), (sx + 11, 270), (sx, 270)], 90, 1.2, 0.7) + pen(pyr, 1.4, 43, 0.05) + seg(sx, 246, sx, 238, 1.2, 44, 0)
               + f'<circle cx="{sx}" cy="258" r="2" fill="{INK}"/>')
    # stadium roofs low on the right
    st_ = [(408, BASE), (412, 334), (470, 326), (520, 334), (526, BASE)]
    art.append(F(st_, PAPER) + segs([((x, 336 - (x - 412) * 0.0), (x, BASE)) for x in range(416, 524, 8)], 0.7, 45, 0, op=0.6) + pen(st_, 1.5, 46, 0.1, smooth=True))
    # --- the waterfront: piers on pilings, the wheel
    pier = [(bx0, BASE), (bx1, BASE), (bx1, BASE + 8), (bx0, BASE + 8)]
    art.append(F(pier, PAPER) + H(U, pier, 0, 1.6, 0.8) + pen(pier[:2], 2.0, 47, 0.3))
    art.append(segs([((x, BASE + 8), (x, BASE + 14)) for x in range(bx0 + 2, bx1, 6)], 1.2, 48, 0))
    sheds = [(60, 126, 342), (190, 262, 340), (370, 430, 344)]
    for i, (a, b, t) in enumerate(sheds):
        sh_ = [(a, BASE), (a, t + 6), ((a + b) / 2, t), (b, t + 6), (b, BASE)]
        art.append(F(sh_, PAPER) + segs([((x, t + 8), (x, BASE - 2)) for x in range(int(a) + 6, int(b) - 4, 9)], 0.8, 49 + i, 0)
                   + H(U, [((a + b) / 2, t), (b, t + 6), (b, BASE), ((a + b) / 2, BASE)], 90, 1.8, 0.7) + sketch(sh_, 1.4, 52 + i, 0.4, closed=False))
    art.append(great_wheel(U, 322, 302, 44, BASE + 1, 55))
    # --- the bay
    art.append(ripples(U, bx0, bx1, BASE + 14, by1, 56, dens=1.0, gap=(2.4, 8.5),
                       refl=[(196, 254, 0.8), (150, 178, 0.6), (300, 344, 0.55), (372, 394, 0.4)], skip=[(430, 500)]))
    art.append(ferry(U, 84, 284, 452, 57))
    # the red tug (accent)
    tx, ty = 420, 430
    tug = [(tx - 30, ty - 10), (tx + 26, ty - 12), (tx + 36, ty - 18), (tx + 30, ty), (tx - 26, ty)]
    art.append(F(tug, PAPER) + accent(U, poly(tug), bbox(tug), 58, op=0.95, ang=0, n=16, length=(8, 18), width=(1.5, 3)) + H(U, tug, 0, 1.6, 0.7, span=(0.55, 1), dark=(tx, ty))
               + sketch(tug, 1.8, 59, 0.5))
    ch = [(tx - 16, ty - 11), (tx - 16, ty - 26), (tx + 6, ty - 26), (tx + 6, ty - 12)]
    art.append(F(ch, PAPER) + F([(tx - 13, ty - 23), (tx + 3, ty - 23), (tx + 3, ty - 18), (tx - 13, ty - 18)], INK, 0.85) + sketch(ch, 1.4, 60, 0.3))
    art.append(F([(tx - 8, ty - 26), (tx - 8, ty - 34), (tx - 2, ty - 34), (tx - 2, ty - 26)], INK) + seg(tx + 2, ty - 26, tx + 2, ty - 40, 1.1, 61, 0))
    art.append(P(f"M {tx - 30} {ty - 4} q -26 2 -54 10 M {tx - 26} {ty} q -16 4 -34 12", 1.0, INK, 0.85))
    # sailboat by the wheel, gulls
    sbx, sby = 484, 392
    art.append(F([(sbx - 12, sby), (sbx + 12, sby), (sbx + 8, sby + 4), (sbx - 9, sby + 4)], INK, 0.9))
    sail = [(sbx - 1, sby - 3), (sbx - 1, sby - 32), (sbx + 14, sby - 3)]
    art.append(F(sail, PAPER) + pen(sail, 1.3, 62, 0.1, closed=True) + F([(sbx - 3, sby - 28), (sbx - 3, sby - 3), (sbx - 13, sby - 3)], PAPER)
               + pen([(sbx - 3, sby - 28), (sbx - 3, sby - 3), (sbx - 13, sby - 3)], 1.1, 63, 0.1, closed=True))
    art.append(bird(300, 404, 8, 64) + bird(322, 392, 6, 65) + bird(540, 240, 6, 66) + bird(100, 250, 6, 67))
    out.append(clipped(U("band"), poly(band), "".join(art)))
    out.append(sketch(band, 2.6, 68, 1.4))
    out.append(sketch([(bx0 - 7, by0 - 7), (bx1 + 7, by0 - 7), (bx1 + 7, by1 + 7), (bx0 - 7, by1 + 7)], 1.1, 69, 1.0))
    # plate-mark ticks at the corners
    ticks = []
    for cx_, cy_ in ((bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)):
        sx_ = -1 if cx_ == bx0 else 1
        sy_ = -1 if cy_ == by0 else 1
        ticks += [((cx_ + sx_ * 10, cy_), (cx_ + sx_ * 20, cy_)), ((cx_, cy_ + sy_ * 10), (cx_, cy_ + sy_ * 20))]
    out.append(segs(ticks, 1.4, 70, 0))
    out.append(T(300, 112, "Seattle", DMS, name_size("Seattle")))
    out.append(coords_line(300, 520, CITIES["seattle"][1], rule_len=34, diamonds=True))
    out.append(finish(U))
    return "".join(out)


# ================================================================ SAN FRANCISCO
def victorian(U, x0, x1, base, ht, seed, gable=True, ground=0.0):
    """A San Francisco Victorian in elevation: clapboard, a three-sided bay window on two floors, entry stair
    and hooded door, bracketed cornice, fish-scale shingled gable (or a flat Italianate false front), a garage
    in the stone plinth. `ground` = how far the street falls below the base at the downhill corner."""
    rnd = random.Random(seed)
    out = []
    W = x1 - x0
    top = base - ht
    body = [(x0, top), (x1, top), (x1, base), (x0, base)]
    out.append(F(body, PAPER))
    out.append(clipped(U("cb"), poly(body), segs([((x0, y), (x1, y)) for y in [top + 3.2 * k for k in range(1, int(ht / 3.2) + 1)]], 0.55, seed, 0.2, op=0.45)))
    # plinth down to the street with a garage door
    if ground > 0:
        pl = [(x0, base), (x1, base), (x1, base + ground), (x0, base + ground * 0.15)]
        out.append(F(pl, PAPER) + H(U, pl, 0, 2.4, 0.7, op=0.8) + sketch(pl, 1.4, seed, 0.4))
    gx0, gx1 = x0 + W * 0.5, x1 - W * 0.08
    gq = [(gx0, base - ht * 0.2), (gx1, base - ht * 0.2), (gx1, base + max(0, ground * 0.85)), (gx0, base + max(0, ground * 0.85) * 0.6)]
    out.append(F(gq, INK, 0.82) + segs([((gx0, base - ht * 0.2 + k * 4), (gx1, base - ht * 0.2 + k * 4)) for k in range(1, 6)], 0.7, seed, 0, color=PAPER, op=0.5))
    # three-sided bay (right part of the front), two floors
    bx0, bx1 = x0 + W * 0.46, x1 - W * 0.04
    bs = (bx1 - bx0) * 0.2
    by0, by1 = top + ht * 0.14, base - ht * 0.24
    lf = [(bx0, by0), (bx0 + bs, by0 - 2), (bx0 + bs, by1 + 2), (bx0, by1)]
    cf = [(bx0 + bs, by0 - 2), (bx1 - bs, by0 - 2), (bx1 - bs, by1 + 2), (bx0 + bs, by1 + 2)]
    rf = [(bx1 - bs, by0 - 2), (bx1, by0), (bx1, by1), (bx1 - bs, by1 + 2)]
    out.append(F(lf, PAPER) + F(cf, PAPER) + F(rf, PAPER))
    wins = []
    for f_ in range(2):
        ya = lerp(by0, by1, 0.06 + f_ * 0.5)
        yb_ = lerp(by0, by1, 0.38 + f_ * 0.5)
        for q, mx_ in ((lf, 0.2), (cf, 0.12), (rf, 0.2)):
            xa, xb = lerp(q[0][0], q[1][0], mx_), lerp(q[0][0], q[1][0], 1 - mx_)
            wins.append([(xa, ya), (xb, ya), (xb, yb_), (xa, yb_)])
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.84"/>')
    out.append(segs([(((w[0][0] + w[1][0]) / 2, w[0][1]), ((w[0][0] + w[1][0]) / 2, w[2][1])) for w in wins[1::3]], 0.8, seed, 0, color=PAPER))
    out.append(H(U, rf, 90, 1.5, 0.8))
    for q in (lf, cf, rf):
        out.append(sketch(q, 1.1, seed + 1, 0.3))
    out.append(segs([((bx0 - 1, (by0 + by1) / 2 + 1), (bx1 + 1, (by0 + by1) / 2 + 1))], 1.6, seed + 2, 0))
    # entry: stair, hooded door, window above
    dx0, dx1 = x0 + W * 0.1, x0 + W * 0.34
    dtop = base - ht * 0.52
    door = arch_window_pts(dx0 + 3, dx1 - 3, dtop, base - ht * 0.24, spring=0.3, n=8)
    out.append(F(door, INK, 0.86) + pen(door, 1.1, seed, 0.05))
    hood = [(dx0 - 2, dtop - 2), ((dx0 + dx1) / 2, dtop - 10), (dx1 + 2, dtop - 2)]
    out.append(F(hood, PAPER) + pen(hood, 1.4, seed + 3, 0.05) + H(U, hood, 0, 1.4, 0.7))
    out.append(segs([((dx0 - 2, dtop - 2), (dx0 - 2, base - ht * 0.24)), ((dx1 + 2, dtop - 2), (dx1 + 2, base - ht * 0.24))], 1.2, seed + 4, 0))
    st = []
    for k in range(6):
        yy = base - ht * 0.24 + k * (ht * 0.24 + ground * 0.3) / 6
        st.append(((dx0 - 4 - k * 1.2, yy), (dx1 + 2, yy)))
    out.append(segs(st, 1.0, seed + 5, 0) + seg(dx1 + 2, base - ht * 0.24, dx1 + 2, base + ground * 0.3, 1.2, seed + 6, 0))
    uw = [(dx0 + 2, top + ht * 0.16), (dx1 - 2, top + ht * 0.16), (dx1 - 2, top + ht * 0.4), (dx0 + 2, top + ht * 0.4)]
    out.append(F(uw, INK, 0.84) + sketch(uw, 1.0, seed + 7, 0.2) + seg(dx0 - 1, top + ht * 0.14, dx1 + 1, top + ht * 0.14, 1.6, seed, 0))
    # cornice with brackets
    cor = [(x0 - 3, top - 7), (x1 + 3, top - 7), (x1 + 3, top), (x0 - 3, top)]
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.6, 0.7) + sketch(cor, 1.6, seed + 8, 0.6))
    out.append(segs([((x, top), (x, top + 4)) for x in [x0 + 2 + k * (W - 4) / 7 for k in range(8)]], 2.0, seed + 9, 0))
    if gable:
        g = [(x0 - 3, top - 7), ((x0 + x1) / 2, top - 7 - W * 0.52), (x1 + 3, top - 7)]
        out.append(F(g, PAPER))
        sc = []
        r = 3.2
        yy = top - 10
        row = 0
        while yy > top - 7 - W * 0.52:
            xx = x0 + (row % 2) * r
            while xx < x1:
                sc.append(f"M {f1(xx - r)} {f1(yy)} A {r} {r} 0 0 0 {f1(xx + r)} {f1(yy)}")
                xx += 2 * r
            yy -= r * 1.4
            row += 1
        out.append(clipped(U("gs"), poly(g), P(" ".join(sc), 0.7, INK, 0.75) + H(U, [((x0 + x1) / 2, top - 7 - W * 0.52), (x1 + 3, top - 7), ((x0 + x1) / 2, top - 7)], 90, 1.8, 0.7)))
        gw = arch_window_pts((x0 + x1) / 2 - 6, (x0 + x1) / 2 + 6, top - 7 - W * 0.3, top - 12, spring=0.4, n=8)
        out.append(F(gw, INK, 0.85) + pen(gw, 1.0, seed, 0.05))
        out.append(pen([(x0 - 6, top - 5), ((x0 + x1) / 2, top - 9 - W * 0.54), (x1 + 6, top - 5)], 2.0, seed + 10, 0.1))
        out.append(seg((x0 + x1) / 2, top - 9 - W * 0.54, (x0 + x1) / 2, top - 18 - W * 0.54, 1.4, seed, 0))
    else:
        fp = [(x0 - 3, top - 7), (x0 - 3, top - 22), (x1 + 3, top - 22), (x1 + 3, top - 7)]
        out.append(F(fp, PAPER) + segs([((x, top - 20), (x, top - 9)) for x in [x0 + 4 + k * (W - 8) / 6 for k in range(7)]], 0.9, seed, 0)
                   + sketch(fp, 1.4, seed + 11, 0.5) + seg(x0 - 5, top - 22, x1 + 5, top - 22, 2.0, seed, 0))
    out.append(pen([(x0, top), (x0, base)], 1.8, seed + 12, 0.2) + pen([(x1, top), (x1, base)], 2.2, seed + 13, 0.2))
    return "".join(out)


def cable_car_side(U, x, y, L, ang, seed):
    """A cable car broadside on the hill, tilted with the street: closed end cabins, the open grip section with
    outward benches and riders on the running boards, clerestory roof; the lower panels in vermilion."""
    ca, sa = math.cos(ang), math.sin(ang)

    def T_(u, v):                       # u along the street (downhill = +), v up from the rails
        return (x + u * ca + v * sa, y + u * sa - v * ca)

    def Q(u0, v0, u1, v1):
        return [T_(u0, v1), T_(u1, v1), T_(u1, v0), T_(u0, v0)]
    out = []
    Hh = L * 0.42
    body = Q(0, L * 0.06, L, Hh * 0.62)
    out.append(F(body, PAPER))
    low = Q(0.01 * L, L * 0.06, 0.99 * L, Hh * 0.3)
    out.append(accent(U, poly(low), bbox(low), seed, op=0.95, ang=math.degrees(ang), n=22, length=(10, 24), width=(1.5, 3)))
    out.append(H(U, low, math.degrees(ang), 2.0, 0.7, span=(0.55, 1), dark=T_(L / 2, 0)))
    # end cabins: windows band
    for u0, u1 in ((0.0, 0.3), (0.7, 1.0)):
        cab = Q(u0 * L, Hh * 0.3, u1 * L, Hh * 0.92)
        out.append(F(cab, PAPER) + sketch(cab, 1.4, seed + 1, 0.3))
        n = 4
        ws = [Q((u0 + (u1 - u0) * (i + 0.15) / n) * L, Hh * 0.42, (u0 + (u1 - u0) * (i + 0.85) / n) * L, Hh * 0.82) for i in range(n)]
        out.append(f'<path d="{" ".join(poly(w) for w in ws)}" fill="{INK}" opacity="0.84"/>')
    # open grip section: posts, bench back, riders
    posts = [(T_(u * L, Hh * 0.3), T_(u * L, Hh * 0.92)) for u in (0.3, 0.42, 0.58, 0.7)]
    out.append(segs(posts, 1.6, seed + 2, 0))
    out.append(seg(*T_(0.3 * L, Hh * 0.5), *T_(0.7 * L, Hh * 0.5), 1.3, seed + 3, 0))
    # roof + clerestory
    roof = Q(-0.04 * L, Hh * 0.92, 1.04 * L, Hh * 1.0)
    out.append(F(roof, PAPER) + H(U, roof, math.degrees(ang), 1.4, 0.8) + sketch(roof, 1.6, seed + 4, 0.4))
    cl_ = Q(0.12 * L, Hh * 1.0, 0.88 * L, Hh * 1.1)
    out.append(F(cl_, PAPER) + segs([(T_(u * L, Hh * 1.01), T_(u * L, Hh * 1.09)) for u in [0.16 + k * 0.06 for k in range(13)]], 0.8, seed, 0)
               + sketch(cl_, 1.2, seed + 5, 0.3))
    # running board + trucks
    rb = Q(0.04 * L, L * 0.03, 0.96 * L, L * 0.06)
    out.append(F(rb, INK, 0.9))
    for u in (0.2, 0.8):
        wx, wy = T_(u * L, L * 0.03)
        out.append(f'<circle cx="{f1(wx)}" cy="{f1(wy)}" r="{f1(L * 0.045)}" fill="{INK}"/>'
                   f'<circle cx="{f1(wx)}" cy="{f1(wy)}" r="{f1(L * 0.018)}" fill="{PAPER}"/>')
    out.append(sketch(body, 2.0, seed + 6, 0.6))
    # riders: seated heads in the open section, standing grip riders on the boards
    for u in (0.35, 0.47, 0.53, 0.65):
        hx, hy = T_(u * L, Hh * 0.62)
        out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(L * 0.03)}" fill="{INK}"/>'
                   + F(smooth_closed([(hx - L * 0.035, hy + L * 0.03), (hx + L * 0.035, hy + L * 0.03), (hx + L * 0.03, hy + L * 0.1), (hx - L * 0.03, hy + L * 0.1)]), INK, 0.9))
    for k, u in enumerate((0.33, 0.62, 0.69)):
        fx, fy = T_(u * L, L * 0.02)
        out.append(person(fx, fy + L * 0.02, Hh * 0.56, seed + 10 + k, flip=k % 2 == 1))
    # bell + grip lever
    out.append(seg(*T_(0.5 * L, Hh * 0.3), *T_(0.5 * L, Hh * 0.75), 2.0, seed + 7, 0))
    return "".join(out)


def compass(U, cx, cy, r, seed=1):
    """A small engraved compass rose."""
    out = [f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{INK}" stroke-width="1.4"/>',
           f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.82)}" fill="none" stroke="{INK}" stroke-width="0.8"/>']
    out.append(segs([((cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82), (cx + math.cos(a) * r, cy + math.sin(a) * r))
                     for a in [i * math.pi / 16 for i in range(32)]], 0.8, seed, 0))
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        L = r * (1.15 if i % 2 == 0 else 0.62)
        wd_ = r * (0.16 if i % 2 == 0 else 0.12)
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        l_ = (cx + math.cos(a - math.pi / 2) * wd_, cy + math.sin(a - math.pi / 2) * wd_)
        r_ = (cx + math.cos(a + math.pi / 2) * wd_, cy + math.sin(a + math.pi / 2) * wd_)
        out.append(F([(cx, cy), l_, tip], PAPER) + F([(cx, cy), r_, tip], INK, 0.9) + pen([l_, tip, r_], 1.0, seed + i, 0))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="2" fill="{INK}"/>')
    # north mark
    out.append(F([(cx - 3.5, cy - r * 1.15 - 4), (cx, cy - r * 1.15 - 11), (cx + 3.5, cy - r * 1.15 - 4)], INK))
    return "".join(out)


@design("san-francisco")
def san_francisco(U):
    """Hyde Street in elevation: Victorians stepping down the hill with fish-scale gables and bay windows, the
    cable car (vermilion panels) tilted on the grade, the bay beyond with Alcatraz and Telegraph Hill's tower;
    postcard layout with the name set left and a compass rose."""
    out = [ground_paper(U, 101)]
    pic = [(54, 54), (546, 54), (546, 432), (54, 432)]
    art = []
    HZ = 206
    slope = lambda x: lerp(262, 404, (x - 54) / 492)       # back of the sidewalk
    ang = math.atan2(404 - 262, 492)
    # sky
    art.append(segs([((54, y), (546, y)) for y in range(58, HZ, 5)], 0.55, 3, 0.15, op=0.32))
    art.append(cloud(U, 420, 92, 140, 20, 4) + cloud(U, 300, 132, 80, 12, 5))
    # Marin hills and the bay
    hills = [(250, HZ), (300, HZ - 14), (360, HZ - 22), (430, HZ - 12), (500, HZ - 20), (546, HZ - 10), (546, HZ)]
    art.append(F(hills, PAPER) + H(U, hills, 20, 2.4, 0.7, op=0.75) + pen(hills[:-1], 1.4, 6, 0.3, smooth=True))
    bay = [(54, HZ), (546, HZ), (546, 320), (54, 320)]
    art.append(F(bay, PAPER) + ripples(U, 54, 546, HZ + 1, 320, 7, dens=1.1, gap=(2.0, 6), ln=((3, 8), (8, 22)), w=(0.8, 1.3), skip=[(440, 480)]))
    # Alcatraz
    ax, ay = 488, HZ + 22
    isl = [(ax - 40, ay + 5), (ax - 30, ay - 4), (ax - 8, ay - 9), (ax + 14, ay - 10), (ax + 32, ay - 3), (ax + 42, ay + 5)]
    ild = smooth_closed(isl + [(ax, ay + 8)])
    art.append(F(ild, PAPER) + clipped(U("al"), ild, H(U, isl, 70, 1.6, 0.8, box=(ax - 44, ay - 14, ax + 46, ay + 10), span=(0.4, 1), dark=(ax + 42, ay)))
               + pen(isl, 1.5, 8, 0.2, smooth=True))
    ch = [(ax - 20, ay - 9), (ax + 16, ay - 10), (ax + 16, ay - 18), (ax - 20, ay - 16)]
    art.append(F(ch, PAPER) + segs([((ax - 18 + i * 4, ay - 15), (ax - 18 + i * 4, ay - 11)) for i in range(9)], 0.8, 9, 0) + sketch(ch, 1.2, 10, 0.3))
    lt = [(ax - 27, ay - 5), (ax - 27, ay - 28), (ax - 23, ay - 28), (ax - 23, ay - 5)]
    art.append(F(lt, PAPER) + pen(lt, 1.2, 11, 0) + F([(ax - 28, ay - 28), (ax - 25, ay - 33), (ax - 22, ay - 28)], INK))
    # Telegraph Hill and its fluted tower (behind the downhill houses)
    th = [(330, 320), (352, 262), (380, 238), (410, 232), (444, 246), (470, 280), (486, 320)]
    art.append(F(smooth_closed(th + [(410, 330)]), PAPER))
    trees = []
    rnd = random.Random(12)
    for i in range(34):
        tx_ = rnd.uniform(346, 476)
        ty_ = 244 + abs(tx_ - 410) * 0.6 + rnd.uniform(0, 30)
        trees.append(lobe(U, tx_, ty_, rnd.uniform(5, 9), rnd.uniform(4, 6), 300 + i, light=(-1, -1), w=0.9, dense=0.8))
    art.append("".join(trees))
    tw = [(401, 238), (401, 150), (419, 150), (419, 238)]
    art.append(F(tw, PAPER) + segs([((x, 166), (x, 236)) for x in (404, 407, 410, 413, 416)], 0.7, 13, 0) + H(U, [(413, 150), (419, 150), (419, 238), (413, 238)], 90, 1.3, 0.8)
               + sketch(tw, 1.5, 14, 0.4))
    arc_ = [arch_window_pts(403 + i * 4, 406 + i * 4, 152, 162, spring=0.4, n=6) for i in range(4)]
    art.append(f'<path d="{" ".join(poly(a_) for a_ in arc_)}" fill="{INK}" opacity="0.85"/>')
    cap = [(399, 150), (399, 144), (421, 144), (421, 150)]
    art.append(F(cap, PAPER) + segs([((x, 145), (x, 149)) for x in range(401, 421, 3)], 0.9, 15, 0) + sketch(cap, 1.3, 16, 0.3))
    # --- the street on the grade: sidewalk, curb, roadway with rails
    walk = [(54, slope(54)), (546, slope(546)), (546, slope(546) + 12), (54, slope(54) + 12)]
    art.append(F(walk, PAPER) + segs([((x, slope(x)), (x - 4, slope(x) + 12)) for x in range(60, 546, 14)], 0.6, 17, 0, op=0.6))
    road = [(54, slope(54) + 12), (546, slope(546) + 12), (546, 440), (54, 440)]
    art.append(F(road, PAPER) + H(U, road, math.degrees(ang), 3.0, 0.6, op=0.45))
    art.append(pen([(54, slope(54) + 12), (546, slope(546) + 12)], 2.0, 18, 0.2) + pen([(54, slope(54) + 14.5), (546, slope(546) + 14.5)], 1.0, 19, 0.2))
    for dv in (52, 58, 64, 70):
        art.append(pen([(54, slope(54) + dv), (546, slope(546) + dv)], 1.1 if dv in (52, 70) else 0.8, 20 + dv, 0.1))
    # --- the houses stepping down (uphill first so each downhill neighbour overlaps)
    row = [(48, 128, 168, True), (128, 204, 132, False), (204, 284, 124, True), (284, 358, 100, False), (358, 440, 92, True), (440, 552, 84, False)]
    for i, (x0, x1, ht, gb) in enumerate(row):
        base = slope(x0) - 2
        art.append(victorian(U, x0, x1, base, ht, 30 + i, gable=gb, ground=slope(x1) - base))
    # lamp, hydrant, people
    for x in (120, 300, 470):
        art.append(lamp(x, slope(x) + 12, 76, 40 + x, "globe", 1.6))
    art.append(person(98, slope(98) + 10, 34, 50) + person(420, slope(420) + 10, 32, 51, flip=True, bag=True))
    # the cable car on the grade
    cx0 = 176
    art.append(cable_car_side(U, cx0, slope(cx0) + 64, 180, ang, 60))
    art.append(bird(176, 112, 8, 61) + bird(196, 98, 6, 62) + bird(330, 196, 5, 63))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 117, 1.4))
    out.append(border(U, 44, 44, 556, 556, 118, double=False, w=(1.2, 1.2)))
    # postcard foot: name set left, coordinates under it, compass rose to the right
    name, coords = CITIES["san-francisco"]
    sz = name_size(name, 370, 62)
    out.append(T(64, 498, name, DMS, sz, anchor="start"))
    out.append(T(66, 532, coords, MONO, COORD_SIZE, ls=COORD_LS, anchor="start"))
    out.append(compass(U, 486, 490, 34, 120))
    out.append(finish(U))
    return "".join(out)


# ================================================================ ROME
def umbrella_pine(U, x, base, h, w, seed, lean=0.0):
    """A Roman stone pine: tall bare forked trunk and a flat spreading parasol canopy of clumps."""
    rnd = random.Random(seed)
    out = []
    top = base - h
    tx = x + lean * h
    out.append(nib([(x, base), (x + lean * h * 0.4, base - h * 0.45), (tx, top + h * 0.22)], max(3, w * 0.05), taper=(1.2, 0.6), ramp=0.4, seed=seed, color=INK))
    for k in (-1, 1):
        out.append(nib([(tx, top + h * 0.3), (tx + k * w * 0.22, top + h * 0.16), (tx + k * w * 0.34, top + h * 0.1)], max(2, w * 0.03), taper=(1, 0.3),
                       seed=seed + k, color=INK))
    under = smooth_closed([(tx - w * 0.5, top + h * 0.1), (tx + w * 0.5, top + h * 0.1), (tx + w * 0.4, top + h * 0.17), (tx - w * 0.4, top + h * 0.17)])
    out.append(F(under, INK, 0.85))
    n = 9
    for row_ in range(2):
        for i in range(n - row_ * 2):
            f = (i + 0.5 + row_) / n
            cx = tx + (f - 0.5) * w * 0.95
            cy = top + h * (0.085 - row_ * 0.045) - math.sin(f * math.pi) * h * 0.035 + rnd.uniform(-2, 2)
            out.append(lobe(U, cx, cy, w * 0.085 + rnd.uniform(0, 3), h * 0.04 + rnd.uniform(0, 2), seed * 7 + i + row_ * 20, light=(-1, -1), w=1.3, dense=1.1))
    return "".join(out)


def tabula_ansata(U, slug, cx, cy, w, h, seed=1, mx=NAME_MAX):
    """A Roman inscription tablet with dovetail handles; the name and coordinates cut into it."""
    name, coords = CITIES[slug]
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    ear = h * 0.42
    shape = [(x0, y0), (x1, y0), (x1 + ear, cy - h * 0.38), (x1 + ear * 0.45, cy), (x1 + ear, cy + h * 0.38), (x1, y1), (x0, y1),
             (x0 - ear, cy + h * 0.38), (x0 - ear * 0.45, cy), (x0 - ear, cy - h * 0.38)]
    out = [F(shape, PAPER)]
    out.append(H(U, [(x1, y0), (x1 + ear, cy - h * 0.38), (x1 + ear * 0.45, cy), (x1 + ear, cy + h * 0.38), (x1, y1)], 90, 2.0, 0.8))
    out.append(H(U, [(x0, y0), (x0 - ear, cy - h * 0.38), (x0 - ear * 0.45, cy), (x0 - ear, cy + h * 0.38), (x0, y1)], 0, 3.0, 0.6, op=0.7))
    out.append(sketch(shape, 2.6, seed, 1.0))
    inner = [(x0 + 7, y0 + 7), (x1 - 7, y0 + 7), (x1 - 7, y1 - 7), (x0 + 7, y1 - 7)]
    out.append(sketch(inner, 1.1, seed + 1, 0.6))
    # bevel shading on the lower and right inner edges (cut stone)
    out.append(H(U, [(x0 + 7, y1 - 7), (x1 - 7, y1 - 7), (x1 - 3, y1 - 3), (x0 + 3, y1 - 3)], 0, 1.2, 0.8))
    out.append(H(U, [(x1 - 7, y0 + 7), (x1 - 3, y0 + 3), (x1 - 3, y1 - 3), (x1 - 7, y1 - 7)], 90, 1.2, 0.8))
    for ex in (x0 - ear * 0.55, x1 + ear * 0.55):
        out.append(f'<circle cx="{f1(ex)}" cy="{f1(cy)}" r="2.6" fill="{INK}"/>')
    sz = name_size(name, w - 60, mx)
    ny = cy + sz * 0.1
    out.append(T(cx, ny, name, DMS, sz))
    out.append(coords_line(cx, ny + 27, coords, rules=False))
    return "".join(out)


def vespa(U, x, y, s, seed, flip=False):
    """A scooter side-on (vermilion body), rider-less, on its stand."""
    k = -1 if flip else 1

    def p(u, v):
        return (x + k * u * s, y - v * s)
    body = [p(-0.55, 0.22), p(-0.6, 0.42), p(-0.42, 0.55), p(-0.05, 0.5), p(0.05, 0.3), p(0.32, 0.28), p(0.38, 0.62), p(0.48, 0.62),
            p(0.52, 0.3), p(0.48, 0.16), p(-0.5, 0.16)]
    d = smooth_closed(body)
    out = [F(d, PAPER), accent(U, d, bbox(body), seed, op=0.95, ang=0, n=12, length=(5, 12), width=(1.2, 2.4)), P(d, 1.5)]
    out.append(F(smooth_closed([p(-0.48, 0.55), p(-0.1, 0.58), p(-0.08, 0.64), p(-0.46, 0.63)]), INK, 0.9))      # seat
    out.append(seg(*p(0.44, 0.62), *p(0.4, 0.86), 1.5, seed, 0) + seg(*p(0.3, 0.86), *p(0.52, 0.86), 1.6, seed + 1, 0))
    for u in (-0.4, 0.46):
        cx_, cy_ = p(u, 0.12)
        out.append(f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(s * 0.13)}" fill="{INK}"/><circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(s * 0.05)}" fill="{PAPER}"/>')
    return "".join(out)


@design("rome")
def rome(U):
    """The Colosseum close up from the Colle Oppio side: the intact four-storey outer wall sweeping round to
    the broken edge and the inner ring, umbrella pines, a scooter (vermilion) in the piazza; a Roman
    inscription tablet with dovetail handles carries the name."""
    out = [ground_paper(U, 121)]
    pic = [(56, 56), (544, 56), (544, 470), (56, 470)]
    C = Cam(f=470, cx=300, vpy=262, eye=16)
    art = []
    art.append(segs([((56, y), (544, y)) for y in range(60, 300, 6)], 0.55, 3, 0.15, op=0.32))
    art.append(cloud(U, 150, 100, 150, 22, 4) + cloud(U, 440, 86, 110, 16, 5) + cloud(U, 330, 128, 70, 10, 6))
    a_, b_, Zc = 94.0, 78.0, 205.0
    TIERS = [(0.0, 10.5), (10.5, 22.0), (22.0, 33.5), (33.5, 48.5)]
    NB = 80

    def Pt(th, Y, shrink=0.0):
        return C((a_ - shrink) * math.cos(th), Y, Zc + (b_ - shrink) * math.sin(th))

    def outer_h(th):
        """Height of the surviving outer wall at angle th (front half runs pi..2pi, left to right)."""
        t = (th - math.pi) / math.pi          # 0 at far left, 1 at far right
        if t < 0.56:
            return 48.5
        if t < 0.62:
            return lerp(48.5, 6.0, (t - 0.56) / 0.06)     # Valadier's stepped buttress
        return 0.0
    # the far side of the bowl, seen through the gap: the inner face of the north wall, tiers of dark vaults
    back = []
    for i in range(NB // 2):
        t0, t1 = math.pi * i / (NB // 2), math.pi * (i + 1) / (NB // 2)
        if math.cos(t0) < 0.05:
            continue
        for y0, y1 in TIERS:
            q = [Pt(t1, y1, 4), Pt(t0, y1, 4), Pt(t0, y0, 4), Pt(t1, y0, 4)]
            back.append(F(q, PAPER))
            m = homog(q)
            back.append(F([m(0.25, 0.85), m(0.25, 0.4), m(0.5, 0.22), m(0.75, 0.4), m(0.75, 0.85)], INK, 0.7))
        back.append(pen([Pt(t0, 48.5, 4), Pt(t1, 48.5, 4)], 1.4, i, 0))
    art.append(f'<g opacity="0.8">{"".join(back)}</g>')
    # inner ring (visible where the outer ring has gone): two arcaded storeys and a ragged top
    inner = []
    itop = []
    ths = [math.pi + math.pi * i / NB * 2 for i in range(NB // 2 + 1)]
    for i in range(len(ths) - 1):
        t0, t1 = ths[i], ths[i + 1]
        tt = (t0 - math.pi) / math.pi
        if tt < 0.5:
            continue
        rnd = random.Random(i)
        topY = 35 - (tt - 0.5) * 22 + 1.6 * math.sin(i * 1.3) + rnd.uniform(-0.6, 0.6)
        for (y0, y1) in ((0.0, 10.5), (10.5, 22.0), (22.0, topY)):
            if y1 <= y0 + 1:
                continue
            q = [Pt(t0, y1, 12), Pt(t1, y1, 12), Pt(t1, y0, 12), Pt(t0, y0, 12)]
            inner.append(F(q, PAPER))
            if y1 - y0 > 8:
                m = homog(q)
                op_ = [m(0.2, 1.0), m(0.2, 0.45), m(0.35, 0.26), m(0.5, 0.2), m(0.65, 0.26), m(0.8, 0.45), m(0.8, 1.0)]
                inner.append(F(op_, INK, 0.82))
            inner.append(pen([q[0], q[3]], 1.0, i, 0))
        itop.append(Pt(t0, topY, 12))
    art.append("".join(inner))
    art.append(pen(itop, 1.8, 59, 0.3))
    # the outer wall, bay by bay
    wall = []
    hatch_q = []
    for i in range(len(ths) - 1):
        t0, t1 = ths[i], ths[i + 1]
        tm = (t0 + t1) / 2
        H0 = min(outer_h(t0), outer_h(t1))
        if H0 <= 0.5:
            continue
        # light: from the left; the facade turns away toward the right
        nx = math.cos(tm)
        shade = max(0.0, min(1.0, 0.25 + 0.75 * (nx + 0.2)))
        for k, (y0, y1) in enumerate(TIERS):
            if y0 >= H0:
                break
            y1c = min(y1, H0)
            q = [Pt(t0, y1c), Pt(t1, y1c), Pt(t1, y0), Pt(t0, y0)]
            if abs(q[1][0] - q[0][0]) < 0.6:
                continue
            wall.append(F(q, PAPER))
            m = homog(q)
            if k < 3 and y1c >= y1 - 0.1:
                # arch opening between engaged half-columns
                op_ = [m(0.22, 1.0), m(0.22, 0.42), m(0.3, 0.27), m(0.4, 0.2), m(0.5, 0.18), m(0.6, 0.2), m(0.7, 0.27), m(0.78, 0.42), m(0.78, 1.0)]
                wall.append(F(op_, INK, 0.88 if k < 2 else 0.75))
                # impost lines + column edge
                wall.append(segs([(m(0.0, 0.0), m(0.0, 1.0)), (m(0.07, 0.08), m(0.07, 1.0))], 0.8, i + k, 0))
            elif k == 3:
                # attic: pilasters and small square windows in alternate bays, corbels near the top
                wall.append(seg(*m(0.0, 0.0), *m(0.0, 1.0), 0.8, i, 0))
                if i % 2 == 0 and y1c >= y1 - 0.1:
                    wall.append(F([m(0.38, 0.42), m(0.62, 0.42), m(0.62, 0.62), m(0.38, 0.62)], INK, 0.85))
                if y1c >= y1 - 0.1:
                    wall.append(segs([(m(u, 0.12), m(u, 0.2)) for u in (0.25, 0.5, 0.75)], 0.9, i, 0))
            if shade > 0.35:
                hatch_q.append((q, shade))
        # cornices between the storeys
        for Y in (10.5, 22.0, 33.5, 48.5):
            if Y <= H0 + 0.01:
                wall.append(pen([Pt(t0, Y), Pt(t1, Y)], 1.4 if Y < 48 else 2.0, i, 0))
        for Y in (11.6, 23.1, 34.6):
            if Y <= H0:
                wall.append(pen([Pt(t0, Y), Pt(t1, Y)], 0.7, i + 1, 0))
    art.append("".join(wall))
    # shade the turning wall with vertical hatching, denser toward the right
    for q, sh in hatch_q:
        art.append(H(U, q, 90, lerp(4.0, 1.7, sh), 0.7, wob=0.1, brk=0.05, op=min(1, sh)))
    # the broken edge: stepped brick buttress
    tb0 = math.pi + math.pi * 0.56
    tb1 = math.pi + math.pi * 0.62
    steps = []
    for j in range(7):
        f0, f1_ = j / 7, (j + 1) / 7
        th0, th1 = lerp(tb0, tb1, f0), lerp(tb0, tb1, f1_)
        Yt = lerp(48.5, 6.0, f1_)
        steps.append([Pt(th0, Yt + (48.5 - 6) / 7), Pt(th1, Yt), Pt(th1, 0), Pt(th0, 0)])
    for j, q in enumerate(steps):
        art.append(F(q, PAPER) + H(U, q, 0, 2.0, 0.8, op=0.9) + sketch(q, 1.4, 60 + j, 0.3))
    # silhouette / top edge of the outer wall + ground line
    edge = [Pt(th, outer_h(th)) for th in [math.pi + math.pi * 0.56 * k / 40 for k in range(41)]]
    art.append(pen(edge, 2.4, 70, 0.1))
    art.append(pen([Pt(math.pi, 0), Pt(math.pi, 48.5)], 2.2, 71, 0.1))
    base_line = [Pt(th, 0) for th in [math.pi + math.pi * k / 40 for k in range(41)]]
    art.append(pen(base_line, 2.2, 72, 0.1))
    # stipple weathering over the travertine
    clip_d = poly([Pt(th, outer_h(th)) for th in [math.pi + math.pi * 0.56 * k / 40 for k in range(41)]] + [Pt(math.pi * 1.56, 0), Pt(math.pi, 0)])
    art.append(ST(U, clip_d, 900, light=(120, 140), r=(0.4, 0.9), op=0.5, box=(56, 100, 544, 330)))
    # --- the piazza: paving, people, lamps, pines, scooter
    gy = Pt(1.5 * math.pi, 0)[1]
    pz = [(56, gy - 4), (544, gy - 4), (544, 470), (56, 470)]
    art.append(F([(56, gy + 2), (544, gy + 2), (544, 470), (56, 470)], PAPER))
    rows_ = []
    y = gy + 4
    k = 0
    while y < 470:
        rows_.append(((56, y), (544, y)))
        y += lerp(3, 14, (y - gy) / (470 - gy))
        k += 1
    art.append(segs(rows_, 0.7, 73, 0.2, op=0.6))
    rj = random.Random(74)
    joints = []
    y = gy + 4
    while y < 470:
        g = lerp(3, 14, (y - gy) / (470 - gy))
        x = 56 + rj.uniform(0, g * 4)
        while x < 544:
            if rj.random() < 0.5:
                joints.append(((x, y), (x + rj.uniform(-0.5, 0.5), y + g * 0.9)))
            x += g * rj.uniform(2.4, 4.0)
        y += g
    art.append(clipped(U("pz"), poly(pz), segs(joints, 0.55, 75, 0, op=0.3)))
    for x, h_, sd, fl in ((170, 30, 1, False), (184, 28, 2, True), (262, 22, 3, False), (360, 26, 4, True), (402, 32, 5, False), (470, 22, 6, True)):
        art.append(person(x, gy + 24 + (h_ - 22) * 4, h_, 80 + sd, flip=fl, bag=sd == 5))
    art.append(lamp(124, 456, 120, 90, "lantern", 2.2))
    art.append(umbrella_pine(U, 74, 470, 380, 150, 91, lean=0.03))
    art.append(umbrella_pine(U, 534, 470, 350, 120, 92, lean=-0.04))
    art.append(vespa(U, 300, 436, 46, 93))
    art.append(bird(250, 160, 7, 94) + bird(268, 148, 5, 95) + bird(380, 176, 6, 96))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 97, 1.4))
    out.append(border(U, 46, 46, 554, 554, 98, double=False, w=(1.2, 1.2)))
    out.append(tabula_ansata(U, "rome", 300, 494, 380, 92, 99, mx=52))
    out.append(finish(U))
    return "".join(out)


# ================================================================ RIO
def granite_dome(U, pts, seed, light=(-1, -0.4), streaks=26, veg_base=0):
    """A bare granite dome: paper body, curved contour hatching on the shade side, vertical exfoliation
    streaks, scribbled forest round the foot."""
    rnd = random.Random(seed)
    d = smooth_closed(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx = (x0 + x1) / 2
    out = [F(d, PAPER)]
    inner = []
    # contour hatching: arcs parallel to the right flank, denser to the right
    arcs = []
    for k in range(22):
        f = k / 21
        xx = lerp(cx - (x1 - x0) * 0.05, x1 + 4, f)
        arcs.append(f"M {f1(xx - (x1 - x0) * 0.08)} {f1(y0 - 4)} Q {f1(xx + (x1 - x0) * 0.08)} {f1((y0 + y1) / 2)} {f1(xx)} {f1(y1 + 4)}")
    inner.append(P(" ".join(arcs), 0.8, INK, 0.85))
    inner.append(H(U, d, 75, 2.0, 0.8, box=(x0, y0, x1, y1), span=(0.7, 1), dark=(x1, y1)))
    st = []
    for _ in range(streaks):
        x = rnd.uniform(x0 + 6, x1 - 6)
        ya = rnd.uniform(y0 + 8, y1 - 30)
        L = rnd.uniform(14, 46)
        st.append([(x, ya), (x + rnd.uniform(-2, 2), ya + L * 0.5), (x + rnd.uniform(-3, 3), ya + L)])
    for i, s_ in enumerate(st):
        inner.append(nib(s_, rnd.uniform(1.0, 2.2), taper=(0.2, 0.2), ramp=0.5, seed=seed + i, color=INK, op=0.75))
    inner.append(ST(U, d, 220, light=(x0, y0), r=(0.4, 0.9), op=0.5, box=(x0, y0, x1, y1)))
    out.append(clipped(U("gd"), d, "".join(inner)))
    out.append(P(d, 2.0))
    if veg_base:
        x = x0 - 6
        while x < x1 + 6:
            r = rnd.uniform(6, 11)
            out.append(lobe(U, x, y1 - r * 0.3 - rnd.uniform(0, veg_base), r, r * 0.7, seed * 31 + int(x), light=(-1, -1), w=1.0, dense=0.9))
            x += r * 1.1
    return "".join(out)


def frigatebird(x, y, s, seed=1):
    """A frigatebird soaring: long angled wings and a forked tail."""
    out = [nib([(x - s * 1.2, y - s * 0.1), (x - s * 0.6, y - s * 0.32), (x - s * 0.15, y - s * 0.05), (x, y)], s * 0.16, taper=(0.1, 0.8), ramp=0.5, seed=seed, color=INK),
           nib([(x, y), (x + s * 0.15, y - s * 0.05), (x + s * 0.6, y - s * 0.32), (x + s * 1.2, y - s * 0.1)], s * 0.16, taper=(0.8, 0.1), ramp=0.5, seed=seed + 1, color=INK)]
    out.append(P(f"M {f1(x)} {f1(y)} L {f1(x - s * 0.12)} {f1(y + s * 0.4)} M {f1(x)} {f1(y)} L {f1(x + s * 0.1)} {f1(y + s * 0.42)}", max(1.0, s * 0.07)))
    return "".join(out)


def copacabana_band(U, y0, y1, seed=1):
    """The wave pavement of the Copacabana promenade: undulating black and white bands, full bleed."""
    rnd = random.Random(seed)
    out = [F([(0, y0), (600, y0), (600, y1), (0, y1)], PAPER)]
    th = 9.0
    wl = 74.0
    amp = 9.0
    k = 0
    y = y0 - amp
    bands = []
    while y < y1 + amp:
        if k % 2 == 0:
            top = [(x, y + amp * math.sin(2 * math.pi * x / wl)) for x in range(-10, 611, 6)]
            bot = [(x, y + th + amp * math.sin(2 * math.pi * x / wl)) for x in range(610, -11, -6)]
            bands.append(poly(top + bot))
        y += th
        k += 1
    out.append(clipped(U("cp"), poly([(0, y0), (600, y0), (600, y1), (0, y1)]), f'<path d="{" ".join(bands)}" fill="{INK}" opacity="0.92"/>'))
    out.append(segs([((0, y0), (600, y0)), ((0, y0 - 5), (600, y0 - 5))], 1.6, seed, 0.3))
    return "".join(out)


@design("rio")
def rio(U):
    """Botafogo cove from the Dona Marta lookout: Sugarloaf and Urca with the cable car (vermilion gondola),
    the bay full of moored boats, the beach crescent and its apartment blocks, frigatebirds overhead; the
    Copacabana wave pavement runs along the foot of the plate."""
    out = [ground_paper(U, 131)]
    pic = [(56, 56), (544, 56), (544, 420), (56, 420)]
    art = []
    HZ = 206
    art.append(segs([((56, y), (544, y)) for y in range(60, HZ, 5)], 0.55, 3, 0.15, op=0.32))
    art.append(cloud(U, 170, 96, 140, 20, 4) + cloud(U, 350, 70, 90, 12, 5))
    # Niterói hills across the bay
    far = [(56, HZ), (90, HZ - 10), (140, HZ - 18), (190, HZ - 8), (240, HZ - 14), (290, HZ - 6), (330, HZ), ]
    art.append(F(far + [(330, HZ + 2), (56, HZ + 2)], PAPER) + H(U, far + [(330, HZ + 2), (56, HZ + 2)], 20, 2.6, 0.7, op=0.7) + pen(far, 1.3, 6, 0.3, smooth=True))
    # the bay
    bay = [(56, HZ), (544, HZ), (544, 360), (56, 360)]
    art.append(F(bay, PAPER) + ripples(U, 56, 544, HZ + 1, 360, 7, dens=0.75, gap=(2.6, 8.5), ln=((3, 8), (10, 24)), w=(0.7, 1.2),
                                       refl=[(392, 528, 0.6), (300, 410, 0.4)]))
    # Sugarloaf and Urca
    sugar = [(386, 300), (392, 236), (402, 176), (416, 136), (436, 112), (458, 102), (478, 106), (496, 124), (508, 160), (516, 214), (522, 262), (530, 300)]
    art.append(granite_dome(U, sugar, 8, streaks=30, veg_base=10))
    urca = [(286, 304), (298, 268), (318, 240), (344, 226), (370, 224), (394, 236), (410, 262), (418, 304)]
    art.append(granite_dome(U, urca, 9, streaks=12, veg_base=0))
    rnd = random.Random(10)
    veg = []
    for i in range(80):
        x = rnd.uniform(296, 414)
        ytop = 236 + abs(x - 356) * 0.62
        if ytop > 296:
            continue
        y = rnd.uniform(ytop + 4, 302)
        veg.append(lobe(U, x, y, rnd.uniform(3.5, 6), rnd.uniform(2.8, 4.2), 200 + i, light=(-1, -1), w=0.8, dense=1.2))
    art.append("".join(veg))
    # cable car: stations, cables, the gondola
    s1, s2 = (360, 222), (456, 104)
    art.append(F([(s1[0] - 9, s1[1] + 2), (s1[0] - 9, s1[1] - 8), (s1[0] + 9, s1[1] - 8), (s1[0] + 9, s1[1] + 2)], PAPER)
               + sketch([(s1[0] - 9, s1[1] + 2), (s1[0] - 9, s1[1] - 8), (s1[0] + 9, s1[1] - 8), (s1[0] + 9, s1[1] + 2)], 1.2, 11, 0.2))
    art.append(F([(s2[0] - 10, s2[1] + 2), (s2[0] - 10, s2[1] - 7), (s2[0] + 10, s2[1] - 7), (s2[0] + 10, s2[1] + 2)], PAPER)
               + sketch([(s2[0] - 10, s2[1] + 2), (s2[0] - 10, s2[1] - 7), (s2[0] + 10, s2[1] - 7), (s2[0] + 10, s2[1] + 2)], 1.2, 12, 0.2))
    for off in (-2, 2):
        art.append(P(f"M {s1[0] + 8} {s1[1] - 6 + off} Q {(s1[0] + s2[0]) / 2} {(s1[1] + s2[1]) / 2 + 14 + off} {s2[0] - 9} {s2[1] - 5 + off}", 0.9))
    gx, gy = 404, 172
    gd = [(gx - 7, gy), (gx + 7, gy), (gx + 6, gy + 10), (gx - 6, gy + 10)]
    art.append(seg(gx, gy - 6, gx, gy, 1.1, 13, 0) + F(gd, PAPER) + accent(U, poly(gd), bbox(gd), 14, op=0.95, ang=0, n=8, length=(4, 8), width=(1, 2))
               + F([(gx - 5, gy + 2), (gx + 5, gy + 2), (gx + 5, gy + 5), (gx - 5, gy + 5)], INK, 0.85) + pen(gd, 1.2, 15, 0, closed=True))
    # moored boats in the cove, with short reflections
    boats = []
    for i in range(34):
        bx = rnd.uniform(70, 360)
        by = rnd.uniform(244, 342)
        s_ = lerp(0.5, 1.2, (by - 244) / 98)
        if 286 < bx and by < 300:
            continue
        boats.append((bx, by, s_))
    for bx, by, s_ in sorted(boats, key=lambda b: b[1]):
        hull = [(bx - 7 * s_, by - 2 * s_), (bx + 7 * s_, by - 2 * s_), (bx + 5 * s_, by + 1.5 * s_), (bx - 5 * s_, by + 1.5 * s_)]
        art.append(F(hull, PAPER) + pen(hull, 1.0, int(bx), 0, closed=True) + seg(bx, by - 2 * s_, bx, by - 15 * s_, 0.9, int(by), 0)
                   + P(f"M {f1(bx - 4 * s_)} {f1(by + 4 * s_)} l {f1(8 * s_)} 0 M {f1(bx - 2 * s_)} {f1(by + 6.5 * s_)} l {f1(4 * s_)} 0", 0.8))
    # the beach crescent and promenade
    sand_top = [(56, 352), (140, 366), (240, 368), (330, 352), (410, 334), (480, 330), (544, 334)]
    sand_bot = [(544, 346), (480, 342), (410, 348), (330, 366), (240, 382), (140, 382), (56, 370)]
    sd = smooth_open(sand_top) + " L " + smooth_open(sand_bot)[2:] + " Z"
    art.append(F(sd, PAPER) + ST(U, sd, 500, light=None, r=(0.4, 0.9), op=0.7, box=(56, 326, 544, 386)))
    art.append(P(smooth_open(sand_top), 1.6) + P(smooth_open(sand_bot[::-1]), 1.2))
    surf = [(x, y - 3) for x, y in sand_top]
    art.append(P(smooth_open(surf), 1.0, INK, 0.8))
    # promenade road + palms
    road_top = [(56, 372), (140, 384), (240, 384), (330, 368), (410, 350), (480, 344), (544, 348)]
    art.append(P(smooth_open(road_top), 1.0) + P(smooth_open([(x, y + 8) for x, y in road_top]), 1.4))
    for i, x in enumerate(range(80, 530, 46)):
        yy = lerp(374, 350, max(0, (x - 240) / 300)) if x > 240 else 382
        art.append(palm(U, x, yy + 4, 34, 140 + i, lean=0.05 * (1 if i % 2 else -1), fronds=7, span=0.9, w=1.2))
    # apartment blocks on the shore, seen from above (foreground, bottom edge)
    blocks = [(56, 104, 388, 32), (100, 150, 392, 40), (150, 196, 394, 26), (196, 250, 396, 36), (250, 296, 392, 24), (296, 344, 382, 30),
              (344, 392, 372, 22), (440, 492, 362, 26), (492, 544, 364, 34)]
    for i, (x0, x1, top, hgt) in enumerate(blocks):
        roof = [(x0 + 4, top), (x1, top - 2), (x1 - 4, top + 8), (x0, top + 10)]
        front = [(x0, top + 10), (x1 - 4, top + 8), (x1 - 4, 430), (x0, 430)]
        art.append(F(front, PAPER) + facade(U, [(x0 + 2, top + 13), (x1 - 6, top + 11), (x1 - 6, 430), (x0 + 2, 430)], max(3, int((x1 - x0) / 9)), 4,
                                          "pane", 150 + i, dark_p=0.3, w=0.8) + sketch(front, 1.4, 160 + i, 0.4, closed=False))
        art.append(F(roof, PAPER) + H(U, roof, 0, 2.2, 0.6, op=0.6) + sketch(roof, 1.4, 170 + i, 0.4))
        # rooftop water tank
        if i % 3 == 0:
            tq = [(x0 + 12, top + 2), (x0 + 22, top + 1), (x0 + 22, top - 6), (x0 + 12, top - 5)]
            art.append(F(tq, PAPER) + H(U, tq, 90, 1.4, 0.7) + sketch(tq, 1.0, 180 + i, 0.2))
    # frigatebirds
    art.append(frigatebird(250, 140, 16, 190) + frigatebird(300, 120, 11, 191) + frigatebird(212, 168, 9, 192))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 193, 1.4))
    out.append(border(U, 46, 46, 554, 430, 194, double=False, w=(1.2, 1.2)))
    out.append(title_block(U, "rio", 300, 484, 440, coord_gap=30, mx=58))
    out.append(copacabana_band(U, 532, 600, 195))
    out.append(finish(U))
    return "".join(out)


# ================================================================ build
def main(slugs):
    for slug, fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save("ink-cities" if slug == "paris" else COL, slug, fn(Ids(slug)))
        print("wrote", slug)


if __name__ == "__main__":
    main(sys.argv[1:])
