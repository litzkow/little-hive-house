"""Ink Cities, engraved edition (set A).

Nine cities redrawn in the style of the engraved Paris plate (ink_cities_fine.paris): a rich pen-and-ink
engraving on warm paper, tonal hatching and cross-hatching that build form and atmosphere, a real perspective
camera, a soft vignette dissolving into the paper (no hard frame), small people, trees, lamps and birds, one
restrained colour wash, and the city name + coordinates set below the picture.

Every plate has its own true viewpoint: London from the Albert Embankment, the Brooklyn Bridge promenade, the
Chicago River from the Riverwalk with a raised bascule bridge, the Colosseum at the end of a cobbled Roman
street, a Lisbon tram climbing a tiled hill, the Charles Bridge toward the Lesser Town tower and the Castle, a
Venetian rio with gondolas, an Amsterdam canal from a bicycle bridge, and the lane up to the Yasaka pagoda.

Also writes one clean line-art Paris for the City Sketches collection (framed sketchbook page).

Run from tools/designs:  python3 ink_engraved_a.py [slug ...]
"""
import math
import random
import sys

from common import DMS, save
from gouache import smooth_closed, smooth_open, wash, strokes
from kitchen_ink import clipped, cr, nib, poly
from ink_cities_fine import (INK, PAPER, RED, F, H, P, ST, XH, Cam, accent, bbox, bird, border, cloud, cobbles,
                             coords_line, cyclist, eiffel, elizabeth_tower, f1, facade, finish, ground_paper, homog,
                             hpat, lamp, lerp, flag, bridge_house, double_decker, lobe, name_size, pen, person, pt, quad_sub, ripples, scallop_d,
                             scallop_pts, seg, segs, sketch, soft_frame, T, tree, umbrella_pine, corncob, vespa, car)

COLL = "ink-cities"
SKETCH = "city-sketches"
OCHRE = ("#F0D9A0", "#D9A441", "#A8741C")      # Lisbon's tram: faded ochre instead of the vermilion

CITIES = {
    "london": ("London", "51.5072° N · 0.1276° W"),
    "new-york": ("New York", "40.7128° N · 74.0060° W"),
    "chicago": ("Chicago", "41.8781° N · 87.6298° W"),
    "rome": ("Rome", "41.9028° N · 12.4964° E"),
    "lisbon": ("Lisbon", "38.7223° N · 9.1393° W"),
    "prague": ("Prague", "50.0755° N · 14.4378° E"),
    "venice": ("Venice", "45.4408° N · 12.3155° E"),
    "amsterdam": ("Amsterdam", "52.3676° N · 4.9041° E"),
    "kyoto": ("Kyoto", "35.0116° N · 135.7681° E"),
    "paris": ("Paris", "48.8566° N · 2.3522° E"),
}

DESIGNS = {}


def design(slug, coll=COLL):
    def deco(fn):
        DESIGNS[(coll, slug)] = fn
        return fn
    return deco


class Ids:
    def __init__(self, slug, pre="iea"):
        self.slug, self.n, self.pre = slug, 0, pre

    def __call__(self, tag="u"):
        self.n += 1
        return f"{self.pre}-{self.slug}-{tag}{self.n}"

    def seed(self):
        self.n += 1
        return self.n * 7 + 3


# ================================================================ shared engraving kit
class CamO(Cam):
    """Cam standing at X = ox instead of X = 0 (keeps a kerb at X = 0 from projecting as a vertical line)."""
    def __init__(self, f=300, cx=300, vpy=300, eye=1.6, ox=0.0):
        super().__init__(f, cx, vpy, eye)
        self.ox = ox

    def __call__(self, X, Y, Z):
        return super().__call__(X - self.ox, Y, Z)


def Wm(C, a, b, Y0, Y1):
    """Exact perspective map of a vertical wall standing on the ground segment a=(X, Z) -> b=(X, Z):
    (u, v) with u 0..1 along the wall, v 0 at height Y1 (top) .. 1 at Y0 (bottom); extrapolates freely."""
    def m(u, v):
        return C(lerp(a[0], b[0], u), lerp(Y1, Y0, v), lerp(a[1], b[1], u))
    return m


def Q(m, u0, v0, u1, v1):
    return [m(u0, v0), m(u1, v0), m(u1, v1), m(u0, v1)]


def mp(m, pts):
    return [m(u, v) for u, v in pts]


def tone(U, clip, lvl, ang=75, box=None, dark=None, span=(0, 1)):
    """Engraved tonal value 1 (light) .. 4 (deep shadow) as hatching / cross-hatching."""
    if lvl <= 0:
        return ""
    g, w, op = {1: (4.4, 0.7, 0.55), 2: (3.2, 0.8, 0.8), 3: (3.0, 0.8, 0.9), 4: (2.3, 0.85, 1.0)}[lvl]
    if lvl >= 3:
        return (H(U, clip, ang, g, w, op=op, box=box, dark=dark, span=span)
                + H(U, clip, ang - 60, g * 1.2, w, op=op, box=box, dark=dark, span=span))
    return H(U, clip, ang, g, w, op=op, box=box, dark=dark, span=span)


def arch_u(u0, u1, v0, v1, spring=0.4, pointed=0.0, n=8):
    """Unit-space window with a round (pointed=0) or pointed (pointed>0) head; v grows downward."""
    cx, rx = (u0 + u1) / 2, (u1 - u0) / 2
    vs = v0 + (v1 - v0) * spring
    pts = [(u0, v1), (u0, vs)]
    for i in range(1, n):
        t = i / n
        if pointed:
            a = math.pi * t
            x = cx - rx * math.cos(a)
            k = math.sin(a) ** (1 - 0.6 * pointed)
            y = vs - (vs - v0) * (k if t <= 0.5 else k)
            if abs(t - 0.5) < 1e-6:
                y = v0
        else:
            a = math.pi - math.pi * t
            x, y = cx + rx * math.cos(a), vs - (vs - v0) * math.sin(a)
        pts.append((x, y))
    if pointed:
        pts.insert(1 + n // 2 + 1, (cx, v0))
    pts += [(u1, vs), (u1, v1)]
    return pts


def ogee_u(u0, u1, v0, v1, spring=0.45):
    """Venetian ogee (flame) arch window in unit space."""
    cx, rx = (u0 + u1) / 2, (u1 - u0) / 2
    vs = v0 + (v1 - v0) * spring
    hh = vs - v0
    return [(u0, v1), (u0, vs), (u0 + rx * 0.15, vs - hh * 0.45), (u0 + rx * 0.55, vs - hh * 0.62), (cx - rx * 0.12, vs - hh * 0.8),
            (cx, v0), (cx + rx * 0.12, vs - hh * 0.8), (u1 - rx * 0.55, vs - hh * 0.62), (u1 - rx * 0.15, vs - hh * 0.45), (u1, vs), (u1, v1)]


def glass(U, ang=80, gap=2.2, w=0.9):
    """Engraved window glass: a fine hatch pattern. Returns (defs, fill)."""
    return hpat(U, ang, gap, w)


def windows(m, shapes, fill, op=1.0, stroke=1.0):
    """Many unit-space window shapes mapped through m and filled with a hatch pattern (or ink)."""
    d = " ".join(poly(mp(m, s)) for s in shapes)
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{stroke}"/>' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{o}/>' + s


def rules_u(m, lines, w=0.8, seed=1, op=1.0, color=INK):
    return segs([(m(*a), m(*b)) for a, b in lines], w, seed, 0.05, op, color)


def sky_rules(U, x0, x1, y0, y1, g0=3.2, g1=9.0, op=0.45, seed=3):
    """Fine engraved horizontal rules thinning out upward (atmosphere near the horizon)."""
    ls = []
    y = y1
    while y > y0:
        t = (y1 - y) / max(1, y1 - y0)
        ls.append(((x0, y), (x1, y)))
        y -= lerp(g0, g1, t)
    return segs(ls, 0.6, seed, 0.15, op=op)


def plate(U, slug, art, seed, frame=(300, 252, 262, 222), expo=3.4, inset=0.24, ny=503, cy=534):
    """Paper, the vignetted picture, name + coordinates below, grain."""
    name, coords = CITIES[slug]
    out = [ground_paper(U, seed)]
    cx, cyf, rx, ry = frame
    out.append(soft_frame(U, cx, cyf, rx, ry, seed, "".join(art), expo=expo, inset=inset))
    out.append(T(300, ny, name, DMS, name_size(name)))
    out.append(coords_line(300, cy, coords, rule_len=30, diamonds=True))
    out.append(finish(U))
    return "".join(out)


def person3(C, X, Y, Z, seed, flip=False, bag=False, h=1.72, op=1.0):
    x, y = C(X, Y, Z)
    return person(x, y, C.f * h / Z, seed, op=op, bag=bag, flip=flip)


def tree3(U, C, X, Y, Z, h, w, seed, light=(-1, -1), lobes=6, trunk=0.42):
    x, yb = C(X, Y, Z)
    s = C.f / Z
    return tree(U, x, yb, h * s, w * s, seed, light=light, trunk_h=trunk, lobes=lobes, lw=max(1.1, min(2.0, w * s / 60)))


def hull(pts):
    """Convex hull (monotone chain) of 2D points."""
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p_ in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p_) <= 0:
            lo.pop()
        lo.append(p_)
    for p_ in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p_) <= 0:
            hi.pop()
        hi.append(p_)
    return lo[:-1] + hi[:-1]


def box_shadow(C, X0, X1, Z0, Z1, Ht, sx, sz, Y=0.0):
    """Screen polygon of the ground shadow cast by an axis-aligned box (sun vector per metre of height sx, sz)."""
    g = [(X0, Z0), (X1, Z0), (X1, Z1), (X0, Z1)]
    w = g + [(x + sx * Ht, z + sz * Ht) for x, z in g]
    return [C(x, Y, z) for x, z in hull(w)]


def gulls(pts, seed=1):
    return "".join(bird(x, y, s, seed + i) for i, (x, y, s) in enumerate(pts))


# ================================================================ LONDON
def gothic_front(U, C, a, b, Y0, Y1, seed, bay=7.0, tiers=((4.5, 8.6), (10.6, 14.6), (16.4, 19.6)), lvl=1, gl=None):
    """The Palace of Westminster river front on the wall a->b: Perpendicular Gothic bays of pointed windows
    between buttress turrets, string courses, a pierced parapet, pinnacles, and the steep roofs behind."""
    rnd = random.Random(seed)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    m = Wm(C, a, b, Y0, Y1)
    out = []
    body = Q(m, 0, 0, 1, 1)
    hgt = Y1 - Y0
    # roofs behind the parapet (set back), dark slate
    dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, nz = dz, -dx                      # pointing away from the camera side
    if (a[0] * nx + a[1] * nz) < 0:
        nx, nz = -nx, -nz
    ridge = Wm(C, (a[0] + nx * 9, a[1] + nz * 9), (b[0] + nx * 9, b[1] + nz * 9), Y0, Y1 + 7)
    roof = [m(0, 0), m(1, 0), ridge(1, 0), ridge(0, 0)]
    out.append(F(roof, PAPER) + tone(U, roof, 3, 80) + pen([ridge(0, 0), ridge(1, 0)], 1.4, seed, 0.1))
    # roof turrets / louvres along the ridge
    for u in [i / 9 + 0.04 for i in range(9)]:
        p0, p1 = ridge(u, 0), ridge(u, 0)
        s = C.f / lerp(a[1], b[1], u)
        tw = 1.6 * s
        th = 4.5 * s
        q = [(p0[0] - tw / 2, p0[1] - th), (p0[0] + tw / 2, p0[1] - th), (p0[0] + tw / 2, p0[1]), (p0[0] - tw / 2, p0[1])]
        out.append(F(q, PAPER) + H(U, q, 90, 1.4, 0.7, span=(0.5, 1), dark=(q[1][0] + 5, q[1][1])) + sketch(q, 0.9, seed + int(u * 50), 0.3))
        out.append(F([q[0], (p0[0], p0[1] - th - 2.2 * s), q[1]], PAPER) + pen([q[0], (p0[0], p0[1] - th - 2.2 * s), q[1]], 1.0, seed, 0.05))
    out.append(F(body, PAPER))
    # windows: two lancets per bay in each tier
    nb = max(1, int(L / bay))
    shapes = []
    mull = []
    for i in range(nb):
        for t0, t1 in tiers:
            v0, v1 = 1 - (t1 - Y0) / hgt, 1 - (t0 - Y0) / hgt
            for k in (0, 1):
                u0 = (i + 0.22 + k * 0.32) / nb
                u1 = u0 + 0.22 / nb
                shapes.append(arch_u(u0, u1, v0, v1, 0.3, pointed=1.0, n=8))
                mull.append(((u0 + (u1 - u0) / 2, v0 + (v1 - v0) * 0.25), (u0 + (u1 - u0) / 2, v1)))
                mull.append(((u0, v0 + (v1 - v0) * 0.55), (u1, v0 + (v1 - v0) * 0.55)))
    out.append(windows(m, shapes, gl, stroke=0.8))
    out.append(rules_u(m, mull, 0.6, seed, color=PAPER))
    # string courses + panel tracery bands between tiers
    sc = []
    for t0, t1 in tiers:
        for Y in (t0 - 0.6, t1 + 0.7):
            v = 1 - (Y - Y0) / hgt
            sc.append(((0, v), (1, v)))
    out.append(rules_u(m, sc, 0.9, seed + 1))
    pan = []
    for i in range(nb * 4):
        u = (i + 0.5) / (nb * 4)
        for t0, t1 in zip([Y0 + 0.5] + [t[1] + 0.9 for t in tiers[:-1]], [t[0] - 0.8 for t in tiers]):
            pan.append(((u, 1 - (t1 - Y0) / hgt), (u, 1 - (t0 - Y0) / hgt)))
    out.append(rules_u(m, pan, 0.55, seed + 2, op=0.8))
    # tone of the whole face (light from the left, the wall turned a little from it) + weathering stipple
    out.append(tone(U, body, lvl, 78))
    out.append(ST(U, poly(body), int(L * 6), light=(0, 0), r=(0.35, 0.8), op=0.45, box=bbox(body)))
    # buttress turrets: narrow projecting shafts with a shaded side, rising into pinnacles
    pins = []
    for i in range(nb + 1):
        u = i / nb
        big = i % 3 == 0
        w_ = 0.9 if not big else 1.6
        du = w_ / L
        top = Y1 + (2.2 if not big else 5.5)
        tm = Wm(C, a, b, Y0, top)
        sh = [tm(u - du, 0), tm(u + du, 0), tm(u + du, 1), tm(u - du, 1)]
        out.append(F(sh, PAPER))
        out.append(H(U, [tm(u, 0), tm(u + du, 0), tm(u + du, 1), tm(u, 1)], 90, 1.5, 0.75, wob=0.1, brk=0))
        out.append(segs([(tm(u - du, 0), tm(u - du, 1)), (tm(u + du, 0), tm(u + du, 1))], 1.1, seed + i, 0.05))
        s = C.f / lerp(a[1], b[1], u)
        px, py = tm(u, 0)
        ph = (3.5 if not big else 6.0) * s
        hw_ = (du * L) * s * 1.1
        pins.append([(px - hw_, py), (px, py - ph), (px + hw_, py)])
        if big:
            for sg in (-1, 1):
                qx = px + sg * hw_ * 1.6
                pins.append([(qx - hw_ * 0.4, py + 0.6 * s), (qx, py - ph * 0.45), (qx + hw_ * 0.4, py + 0.6 * s)])
    out.append(f'<path d="{" ".join(poly(p_) for p_ in pins)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.0" stroke-linejoin="round"/>')
    # crenellated parapet line with small pinnacles
    cren = []
    n_c = int(L / 1.6)
    for j in range(n_c):
        u0, u1 = j / n_c, (j + 0.5) / n_c
        cren.append(((u0, 0), (u0, -0.035)))
        cren.append(((u0, -0.035), (u1, -0.035)))
        cren.append(((u1, -0.035), (u1, 0)))
    out.append(rules_u(m, cren, 0.7, seed + 3))
    out.append(pen([m(0, 0), m(1, 0)], 1.6, seed, 0.1) + pen([m(0, 1), m(1, 1)], 1.8, seed + 1, 0.1))
    return "".join(out)


def bridge_lamp(U, x, base, h, seed):
    """Westminster Bridge lamp standard: a fluted Gothic cast-iron post on a moulded plinth, a crowned lantern on
    top and two more on scrolled arms. Drawn as an engraved solid when large, as pen strokes when small."""
    out = []
    w = max(1.2, h * 0.022)
    big = h > 90
    pl = [(x - h * 0.055, base), (x + h * 0.055, base), (x + h * 0.045, base - h * 0.05), (x + h * 0.035, base - h * 0.14),
          (x - h * 0.035, base - h * 0.14), (x - h * 0.045, base - h * 0.05)]
    out.append(F(pl, PAPER) + H(U, [(x + h * 0.01, base), (x + h * 0.055, base), (x + h * 0.045, base - h * 0.05), (x + h * 0.035, base - h * 0.14),
                                    (x + h * 0.01, base - h * 0.14)], 90, 1.4 if big else 1.2, 0.7) + pen(pl, max(1.0, w * 0.8), seed, 0.1, True))
    if big:
        out.append(seg(x - h * 0.045, base - h * 0.05, x + h * 0.045, base - h * 0.05, 1.0, seed, 0))
        out.append(H(U, pl, 0, 2.6, 0.6, op=0.5))
    y0, y1 = base - h * 0.14, base - h * 0.86
    pw0, pw1 = h * 0.024, h * 0.013
    post = [(x - pw0, y0), (x - pw1, y1), (x + pw1, y1), (x + pw0, y0)]
    if big:
        out.append(F(post, PAPER))
        out.append(H(U, [(x, y0), (x, y1), (x + pw1, y1), (x + pw0, y0)], 90, 1.3, 0.8, wob=0.1, brk=0))
        out.append(segs([((x - pw0 * 0.45, y0), (x - pw1 * 0.45, y1))], 0.7, seed, 0))
        out.append(pen([(x - pw0, y0), (x - pw1, y1)], 1.5, seed, 0.1) + pen([(x + pw0, y0), (x + pw1, y1)], 2.0, seed + 1, 0.1))
    else:
        out.append(nib([(x, y0), (x, (y0 + y1) / 2), (x, y1)], w * 1.7, taper=(1.3, 0.8), ramp=0.3, seed=seed, color=INK))
    for yy, k in ((base - h * 0.3, 1.9), (base - h * 0.62, 1.6)):
        out.append(F([(x - pw0 * k, yy - h * 0.012), (x + pw0 * k, yy - h * 0.012), (x + pw0 * k, yy + h * 0.012), (x - pw0 * k, yy + h * 0.012)], INK, 0.9))
    ay = base - h * 0.7
    for sg in (-1, 1):
        ex = x + sg * h * 0.17
        out.append(P(f"M {f1(x)} {f1(ay + h * 0.05)} Q {f1(x + sg * h * 0.12)} {f1(ay + h * 0.05)} {f1(ex)} {f1(ay - h * 0.005)}", max(1.0, w * 0.8)))
        out.append(P(f"M {f1(x + sg * h * 0.03)} {f1(ay + h * 0.05)} q {f1(sg * h * 0.03)} {f1(h * 0.04)} {f1(sg * h * 0.07)} {f1(h * 0.01)}", max(0.8, w * 0.5)))
        out.append(lantern(U, ex, ay, h * 0.14, seed + sg, w, big))
    out.append(lantern(U, x, y1, h * 0.17, seed + 3, w, big))
    return "".join(out)


def lantern(U, x, yb, h, seed, w=1.4, big=False):
    """A lantern standing at (x, yb): tapered glazed body with glazing bars, shaded right side, crown, finial."""
    lw_ = h * 0.34
    body = [(x - lw_ * 0.62, yb), (x + lw_ * 0.62, yb), (x + lw_, yb - h * 0.62), (x - lw_, yb - h * 0.62)]
    out = [F(body, PAPER)]
    if big:
        out.append(H(U, [(x + lw_ * 0.2, yb), (x + lw_ * 0.62, yb), (x + lw_, yb - h * 0.62), (x + lw_ * 0.3, yb - h * 0.62)], 90, 1.3, 0.6))
    out.append(segs([((x, yb), (x, yb - h * 0.62)), ((x - lw_ * 0.8, yb - h * 0.31), (x + lw_ * 0.8, yb - h * 0.31))], max(0.6, w * 0.4), seed, 0))
    out.append(pen(body, max(0.9, w * 0.55), seed, 0.05, True))
    out.append(F([(x - lw_ * 0.5, yb + h * 0.08), (x + lw_ * 0.5, yb + h * 0.08), (x + lw_ * 0.62, yb), (x - lw_ * 0.62, yb)], INK, 0.9))
    crown = [(x - lw_ * 1.15, yb - h * 0.62), (x - lw_ * 0.6, yb - h * 0.8), (x, yb - h * 0.95), (x + lw_ * 0.6, yb - h * 0.8), (x + lw_ * 1.15, yb - h * 0.62)]
    if big:
        out.append(F(crown, PAPER) + H(U, crown, 90, 1.2, 0.6, span=(0.5, 1), dark=(x + lw_, yb - h * 0.7)) + pen(crown, max(1.0, w * 0.6), seed, 0.05, True))
    else:
        out.append(F(crown, INK, 0.9))
    out.append(seg(x, yb - h * 0.95, x, yb - h * 1.12, max(0.8, w * 0.5), seed, 0))
    out.append(f'<circle cx="{f1(x)}" cy="{f1(yb - h * 1.14)}" r="{f1(max(0.9, h * 0.04))}" fill="{INK}"/>')
    return "".join(out)


def bus3(U, C, X0, Z0, seed, L=10.5, W=2.5, Ht=4.4):
    """A double-decker coming toward us: front face at Z0, its left flank (X0) receding; vermilion wash."""
    X1 = X0 + W
    front = C.qz(Z0, X0, X1, 0.3, Ht)
    side = C.qx(X0, Z0, Z0 + L, 0.3, Ht)
    roof = [C(X0, Ht, Z0), C(X1, Ht, Z0), C(X1, Ht, Z0 + L), C(X0, Ht, Z0 + L)]
    out = [F(side, PAPER), F(front, PAPER), F(roof, PAPER)]
    out.append(accent(U, poly(side) + " " + poly(front), bbox(side + front), seed, op=0.85, n=26, length=(6, 18), width=(1.5, 3.2)))
    out.append(H(U, side, 70, 2.8, 0.75, op=0.55) + H(U, front, 70, 3.6, 0.7, op=0.35))
    fm, sm_ = homog(front), homog(side)
    # side windows: upper and lower deck bands, pillars between
    for v0, v1 in ((0.1, 0.36), (0.5, 0.74)):
        out.append(F(Q(sm_, 0.04, v0, 0.97, v1), INK, 0.86))
        out.append(segs([(sm_(u, v0), sm_(u, v1)) for u in (0.2, 0.36, 0.52, 0.68, 0.84)], 1.0, seed, 0, color=PAPER))
    out.append(segs([(sm_(0, 0.44), sm_(1, 0.44)), (sm_(0, 0.8), sm_(1, 0.8))], 0.9, seed, 0))
    # front: destination blind, upper windscreen, lower windscreen, grille, lamps
    out.append(F(Q(fm, 0.1, 0.05, 0.9, 0.13), INK, 0.9))
    out.append(F(Q(fm, 0.06, 0.16, 0.94, 0.38), INK, 0.82))
    out.append(seg(*fm(0.5, 0.16), *fm(0.5, 0.38), 1.0, seed, 0, color=PAPER))
    out.append(F(Q(fm, 0.05, 0.5, 0.95, 0.76), INK, 0.82))
    out.append(seg(*fm(0.5, 0.5), *fm(0.5, 0.76), 1.0, seed, 0, color=PAPER))
    out.append(F(Q(fm, 0.3, 0.84, 0.7, 0.9), INK, 0.7))
    for u in (0.14, 0.86):
        x, y = fm(u, 0.87)
        out.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(abs(fm(1, 0.9)[0] - fm(0, 0.9)[0]) * 0.06)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    out.append(H(U, roof, 0, 1.6, 0.6, op=0.6))
    out.append(H(U, Q(sm_, 0, 0.8, 1, 1), 0, 1.5, 0.7))
    for q in (side, front, roof):
        out.append(sketch(q, 1.5, seed, 0.5))
    # wheels on the flank
    for u in (0.12, 0.78):
        x, y = sm_(u, 0.97)
        r = 0.5 * C.f / (Z0 + u * L)
        out.append(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{f1(r * 0.45)}" ry="{f1(r)}" fill="{INK}"/>')
    return "".join(out)


def portcullis(U, C, X0, X1, Z0, Z1, Ht, seed, gl):
    """A sandstone office block on the corner of Bridge Street: south face toward us (Z0) and its east flank,
    regular deep windows, a row of tall bronze chimney stacks on the roof."""
    out = []
    front = C.qz(Z0, X0, X1, 0, Ht)
    flank = C.qx(X0, Z0, Z1, 0, Ht)
    out += [F(flank, PAPER), F(front, PAPER)]
    fm, sm_ = homog(front), homog(flank)
    cols, rows = 9, 6
    out.append(windows(fm, [[(u0, v0), (u0 + 0.6 / cols, v0), (u0 + 0.6 / cols, v0 + 0.55 / rows), (u0, v0 + 0.55 / rows)]
                            for u0 in [(i + 0.2) / cols for i in range(cols)] for v0 in [(j + 0.25) / rows for j in range(rows - 1)]], gl, stroke=0.7))
    out.append(F(Q(fm, 0, 0.84, 1, 1), INK, 0.8))
    out.append(segs([(fm(i / cols, 0.84), fm(i / cols, 1)) for i in range(1, cols)], 1.0, seed, 0, color=PAPER))
    out.append(windows(sm_, [[(u0, v0), (u0 + 0.55 / 7, v0), (u0 + 0.55 / 7, v0 + 0.55 / rows), (u0, v0 + 0.55 / rows)]
                             for u0 in [(i + 0.2) / 7 for i in range(7)] for v0 in [(j + 0.25) / rows for j in range(rows - 1)]], gl, stroke=0.6))
    out.append(tone(U, flank, 4, 80))
    out.append(tone(U, front, 2, 80))
    # chimney stacks
    for i in range(6):
        Xc = lerp(X0 + 2, X1 - 2, i / 5)
        st = C.qz(Z0 + 2, Xc - 1.3, Xc + 1.3, Ht, Ht + 8)
        out.append(F(st, PAPER) + H(U, [pt(st[0], st[1], 0.45), st[1], st[2], pt(st[3], st[2], 0.45)], 90, 1.3, 0.7) + sketch(st, 1.0, seed + i, 0.3))
        out.append(F([pt(st[0], st[1], -0.2), pt(st[0], st[1], 1.2), (st[1][0] + 1, st[1][1] + 3), (st[0][0] - 1, st[0][1] + 3)], INK, 0.85))
    out.append(sketch(front, 1.5, seed, 0.6) + sketch(flank, 1.5, seed + 1, 0.6))
    return "".join(out)


def gothic_spire(U, x, base, top, hw, seed):
    """The Central Tower of the Palace: an octagonal lantern with tall windows under a crocketed spire."""
    out = []
    Hh = base - top
    drum = [(x - hw, base - Hh * 0.45), (x + hw, base - Hh * 0.45), (x + hw, base), (x - hw, base)]
    out.append(F(drum, PAPER))
    for k in range(4):
        u0 = x - hw + (k + 0.25) * hw / 2
        out.append(F(arch_u(u0, u0 + hw * 0.25, base - Hh * 0.42, base - Hh * 0.08, 0.25, pointed=1.0), INK, 0.85))
    out.append(H(U, [(x + hw * 0.3, base - Hh * 0.45), (x + hw, base - Hh * 0.45), (x + hw, base), (x + hw * 0.3, base)], 90, 1.5, 0.7))
    out.append(sketch(drum, 1.3, seed, 0.4))
    sp = [(x - hw * 0.95, base - Hh * 0.45), (x, top), (x + hw * 0.95, base - Hh * 0.45)]
    out.append(F(sp, PAPER) + H(U, [(x, top), (x + hw * 0.95, base - Hh * 0.45), (x, base - Hh * 0.45)], 90, 1.4, 0.7) + pen(sp, 1.3, seed, 0.05))
    cro = []
    for i in range(1, 8):
        t = i / 8
        for sg in (-1, 1):
            px = lerp(x + sg * hw * 0.95, x, t)
            py = lerp(base - Hh * 0.45, top, t)
            cro.append(((px, py), (px + sg * 2.2, py - 1.5)))
    out.append(segs(cro, 1.0, seed, 0))
    for sg in (-1, 1):
        px = x + sg * hw
        out.append(F([(px - 2, base - Hh * 0.45), (px, base - Hh * 0.62), (px + 2, base - Hh * 0.45)], PAPER) + pen([(px - 2, base - Hh * 0.45), (px, base - Hh * 0.62), (px + 2, base - Hh * 0.45)], 1.0, seed, 0.05))
    return "".join(out)


@design("london")
def london(U):
    """On the pavement of Westminster Bridge looking west: Elizabeth Tower rising at the bridge's end, the Palace
    river front beyond the parapet with the Thames below, Gothic lamp standards receding along the parapet,
    a red double-decker coming toward us, Bridge Street opening between the tower and the sandstone offices."""
    C = CamO(f=440, cx=300, vpy=356, eye=2.4, ox=-1.6)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    # sky: the soft ruled haze of a London afternoon
    art.append(sky_rules(U, 0, 600, 70, C.vpy - 30, 3.0, 9.5, 0.3, 9))
    art.append(cloud(U, 432, 98, 150, 28, 11) + cloud(U, 506, 156, 80, 14, 12) + cloud(U, 128, 120, 120, 22, 13) + cloud(U, 330, 176, 70, 11, 14))
    art.append(gulls([(352, 214, 7), (372, 200, 5), (150, 196, 6), (486, 214, 5)], 15))
    # the Central Tower spire, far left behind the palace roofs
    gx = C(-128, 0, 210)[0]
    art.append(gothic_spire(U, gx, C(-128, 26, 210)[1], C(-128, 88, 210)[1], 4.5 * C.f / 210, 19))
    # the Palace river front (frontal, across the river)
    ZP = 160.0
    art.append(gothic_front(U, C, (-22.0, ZP), (-215.0, ZP), 2.0, 25.0, 21, bay=8.0, gl=gl, lvl=3))
    tw_ = C.qz(ZP, -215, -22, -7, 2)
    art.append(F(tw_, PAPER) + H(U, tw_, 0, 1.5, 0.8) + pen([tw_[0], tw_[1]], 1.4, 23, 0.1) + pen([tw_[3], tw_[2]], 1.6, 23, 0.1))
    # Bridge Street: Portcullis-style offices on the right corner, Norman Shaw turrets beyond
    nsh = []
    for X, Zt, sd in ((48, 250, 1), (70, 250, 2)):
        x, yb = C(X, 0, Zt)
        top = C(X, 34, Zt)[1]
        q = [(x - 18, top + 10), (x + 18, top + 10), (x + 18, yb), (x - 18, yb)]
        nsh.append(F(q, PAPER) + facade(U, [(x - 16, top + 14), (x + 16, top + 14), (x + 16, yb - 4), (x - 16, yb - 4)], 6, 6, "pane", sd, dark_p=0.3, w=0.6)
                   + tone(U, q, 1, 80) + sketch(q, 1.0, sd, 0.4))
        for sx in (-1, 1):
            tq = [(x + sx * 18 - 5, top + 10), (x + sx * 18 - 5, top), (x + sx * 18, top - 8), (x + sx * 18 + 5, top), (x + sx * 18 + 5, top + 10)]
            nsh.append(F(tq, PAPER) + pen(tq, 1.0, sd, 0.1))
    art.append(f'<g opacity="0.8">{"".join(nsh)}</g>')
    art.append(portcullis(U, C, 22, 64, 146, 200, 30, 24, gl))
    # Elizabeth Tower
    TX, TZ = -16.0, 150.0
    art.append(elizabeth_tower(U, C(TX, 0, TZ)[0], C(TX, 0, TZ)[1], C(TX, 96, TZ)[1], 6.0 * C.f / TZ, 22))
    # trees on the Embankment beyond the north parapet
    for X, Z, sd in ((30, 120, 1), (40, 104, 2), (54, 96, 3), (36, 78, 4), (34, 62, 5)):
        art.append(tree3(U, C, X, 0, Z, 15, 11, 600 + sd))
    # the river seen over the south parapet
    PX = -4.5                          # south parapet inner face
    water = [(30, C(-22, -7, ZP)[1]), C(-22, -7, ZP), C(PX, 1.1, 140), C(PX, 1.1, 3.0), (30, 640)]
    art.append(ripples(U, 30, 300, C(-22, -7, ZP)[1], 470, 41, dens=1.1, gap=(2.2, 8.0), refl=[(C(TX, 0, TZ)[0] - 16, C(TX, 0, TZ)[0] + 16, 0.9), (40, 230, 0.35)],
                       skip=[(120, 160)], clip=poly(water)))
    # a river boat passing under the palace
    bx, by = C(-58, 0, 112)
    hull = [(bx - 44, by), (bx + 36, by), (bx + 28, by + 8), (bx - 40, by + 8)]
    cab = [(bx - 32, by), (bx - 32, by - 10), (bx + 18, by - 10), (bx + 18, by)]
    art.append(F(hull, PAPER) + H(U, hull, 0, 1.6, 0.8) + sketch(hull, 1.4, 42, 0.6))
    art.append(F(cab, PAPER) + facade(U, [(bx - 30, by - 8), (bx + 16, by - 8), (bx + 16, by - 2), (bx - 30, by - 2)], 8, 1, "dark", 43, mx=0.15, my=0.1)
               + sketch(cab, 1.2, 44, 0.5))
    art.append(P(f"M {bx + 36} {by + 4} q 18 2 40 7 M {bx - 44} {by + 4} q -16 1 -34 0", 0.9, INK, 0.8))
    # bridge deck: pavement (flags), kerb, road (setts of asphalt hatching), far pavement
    Z0, Z1 = 2.5, 140.0
    road = [C(0, 0, Z0), C(0, 0, Z1), C(16, 0, Z1), C(16, 0, Z0)]
    art.append(F([C(PX, 0, Z0), C(PX, 0, Z1), C(19.5, 0, Z1), C(19.5, 0, Z0)], PAPER))
    rows = []
    z = Z0
    rr = random.Random(50)
    while z < Z1:
        xa = rr.uniform(0, 3)
        while xa < 16:
            xb = min(16, xa + rr.uniform(2.5, 7))
            rows.append((C(xa, 0, z), C(xb, 0, z)))
            xa = xb + rr.uniform(0.3, 1.5)
        z = z * 1.075 + 0.15
    art.append(segs(rows, 0.6, 50, 0.1, op=0.45))
    art.append(ST(U, poly(road), 1400, light=(300, 300), r=(0.4, 0.9), op=0.5, power=1.0))
    art.append(H(U, road, 2, 2.8, 0.6, op=0.55, span=(0.0, 1)))
    art.append(segs([(C(x_, 0, Z0), C(x_, 0, Z1)) for x_ in (3.2, 12.8)], 0.6, 49, 0.1, op=0.35))
    shad = [C(PX, 0.01, Z0), C(PX, 0.01, Z1), C(PX + 0.9, 0.01, Z1), C(PX + 0.9, 0.01, Z0)]
    art.append(tone(U, shad, 2, 75))
    art.append(segs([(C(7.8, 0, z), C(7.8, 0, z + 2.2)) for z in [4 + 6 * k for k in range(22)]], 1.4, 51, 0))
    for X0p, X1p in ((PX, 0), (16, 19.5)):
        flg = [(C(X0p, 0.12, z), C(X1p, 0.12, z)) for z in [Z0 + 0.9 * 1.06 ** k * k for k in range(60) if Z0 + 0.9 * 1.06 ** k * k < Z1]]
        art.append(segs(flg, 0.6, 52, 0, op=0.6))
        art.append(pen([C(X1p if X0p == PX else X0p, 0.12, Z0), C(X1p if X0p == PX else X0p, 0.12, Z1)], 1.5, 53, 0.1))
    # north parapet + lamps (far side of the road)
    np_ = C.qx(19.5, Z0 + 10, Z1, 0, 1.15)
    art.append(F(np_, PAPER) + rules_u(homog(np_), [((i / 120, 0.12), (i / 120, 0.95)) for i in range(120)], 0.6, 54) + sketch(np_, 1.2, 55, 0.3))
    for z in (26, 48, 72, 100, 130):
        x, yb = C(19.6, 1.15, z)
        art.append(bridge_lamp(U, x, yb, C.f * 6.2 / z, 70 + z))
    # traffic: black cab, the bus, a cyclist
    cx_, cy_ = C(10.8, 0, 58)
    cs = C.f / 58
    cab_ = [(cx_ - 0.9 * cs, cy_), (cx_ - 0.85 * cs, cy_ - 1.1 * cs), (cx_ - 0.6 * cs, cy_ - 1.6 * cs), (cx_ + 0.6 * cs, cy_ - 1.6 * cs), (cx_ + 0.85 * cs, cy_ - 1.1 * cs), (cx_ + 0.9 * cs, cy_)]
    art.append(F(cab_, INK, 0.92) + F([(cx_ - 0.55 * cs, cy_ - 1.1 * cs), (cx_ - 0.45 * cs, cy_ - 1.5 * cs), (cx_ + 0.45 * cs, cy_ - 1.5 * cs), (cx_ + 0.55 * cs, cy_ - 1.1 * cs)], PAPER, 0.5))
    for X, z, sd, fl in ((17.4, 21, 11, False), (18.3, 23, 12, True), (17.5, 40, 5, True), (18.2, 70, 6, False), (17.2, 96, 7, True), (16.8, 118, 8, False)):
        art.append(person3(C, X, 0.12, z, 80 + sd, flip=fl, bag=sd == 5))
    # late sun low in the west ahead of us: long shadows run back toward us and to the right
    SX, SZ = 1.1, -0.95
    sh = [box_shadow(C, 1.2, 3.7, 19, 30, 4.4, SX, SZ)]
    for z in (24, 42, 64, 92, 126):
        hh = 6.2
        sh.append([C(PX + 0.1, 0, z - 0.3), C(PX + 0.1, 0, z + 0.3), C(PX + SX * hh, 0, z + SZ * hh + 0.15), C(PX + SX * hh, 0, z + SZ * hh - 0.15)])
    for X, z in ((-1.9, 13), (-1.2, 14.2), (-1.0, 24), (-3.0, 38)):
        sh.append([C(X - 0.2, 0, z), C(X + 0.2, 0, z), C(X + SX * 1.7 + 0.1, 0, z + SZ * 1.7), C(X + SX * 1.7 - 0.1, 0, z + SZ * 1.7)])
    art.append(clipped(U("shd"), " ".join(poly(q) for q in sh), tone(U, [(0, 300), (600, 300), (600, 600), (0, 600)], 4, 70)))
    art.append(double_decker(U, C, 1.2, 19.0, 61, length=10.5, width=2.5, height=4.4))
    x, yb = C(10.5, 0, 34)
    art.append(cyclist(x, yb, C.f * 1.8 / 34, 62, flip=True))
    # pedestrians on both pavements
    for X, z, sd, fl in ((-1.9, 13, 1, False), (-1.2, 14.2, 9, False), (-1.0, 24, 2, True), (-3.0, 38, 3, False), (-1.4, 58, 4, True), (-2.6, 80, 10, False)):
        art.append(person3(C, X, 0.12, z, 80 + sd, flip=fl, bag=sd == 2))
    # the south parapet (we stand beside it): balustrade receding to the tower, lamp standards
    sp = C.qx(PX, Z0, Z1, 0, 1.15)
    art.append(F(sp, PAPER) + H(U, sp, 90, 2.4, 0.8, op=0.75))
    bal = []
    z = Z0
    while z < Z1:
        a_, b_ = C(PX, 0.1, z), C(PX, 1.0, z)
        if a_[0] - C(PX, 0.1, z + 0.5)[0] < -1.2 or True:
            bal.append((a_, b_))
        z *= 1.035
        z += 0.12
    art.append(segs(bal, 0.9, 56, 0))
    art.append(pen([C(PX, 1.15, Z0), C(PX, 1.15, Z1)], 2.6, 57, 0.1) + pen([C(PX, 1.0, Z0), C(PX, 1.0, Z1)], 1.0, 58, 0.1) + pen([C(PX, 0.1, Z0), C(PX, 0.1, Z1)], 1.6, 59, 0.1))
    for z in (24, 42, 64, 92, 126):
        x, yb = C(PX, 1.15, z)
        art.append(bridge_lamp(U, x, yb, C.f * 6.2 / z, 90 + int(z)))
    return plate(U, "london", art, 31, frame=(300, 244, 264, 208))


# ================================================================ NEW YORK
def skyline_strip(U, x0, x1, base, seed, hmax=150, op=0.75, gl=None):
    """Lower Manhattan across the river, pale with distance: setback towers, a tapering spire tower, a stepped
    Gothic top, slab blocks with window grids."""
    rnd = random.Random(seed)
    out = []
    x = x0
    i = 0
    while x < x1:
        w = rnd.uniform(14, 30)
        h = rnd.uniform(0.25, 0.7) * hmax
        st = rnd.choice(("grid", "pane", "slit"))
        q = [(x, base - h), (x + w, base - h), (x + w, base), (x, base)]
        out.append(F(q, PAPER) + facade(U, [(x + 1.5, base - h + 3), (x + w - 1.5, base - h + 3), (x + w - 1.5, base), (x + 1.5, base)],
                                        max(2, int(w / 5)), max(3, int(h / 7)), st, seed + i, dark_p=0.18, w=0.6))
        if rnd.random() < 0.45:
            out.append(H(U, [(x + w * 0.6, base - h), (x + w, base - h), (x + w, base), (x + w * 0.6, base)], 90, 1.6, 0.6))
        if rnd.random() < 0.35:                      # setback crown
            cq = [(x + w * 0.2, base - h - h * 0.12), (x + w * 0.8, base - h - h * 0.12), (x + w * 0.8, base - h), (x + w * 0.2, base - h)]
            out.append(F(cq, PAPER) + H(U, cq, 90, 1.8, 0.6, span=(0.5, 1), dark=(x + w, base - h)) + sketch(cq, 0.9, seed + i, 0.3))
        out.append(sketch(q, 1.0, seed + i, 0.4))
        x += w * rnd.uniform(0.75, 1.05)
        i += 1
    return f'<g opacity="{op}">' + "".join(out) + "</g>"


def spire_tower(U, cx, base, top, w, seed):
    """A tall tapering glass tower (chamfered square plan seen corner-on) with a slender mast."""
    out = []
    h = base - top
    body = [(cx - w / 2, base), (cx - w * 0.28, top + h * 0.06), (cx + w * 0.28, top + h * 0.06), (cx + w / 2, base)]
    out.append(F(body, PAPER))
    out.append(segs([((cx, base), (cx, top + h * 0.06))], 0.9, seed, 0))
    out.append(H(U, [(cx, base), (cx, top + h * 0.06), (cx + w * 0.28, top + h * 0.06), (cx + w / 2, base)], 90, 1.6, 0.7))
    out.append(H(U, body, 0, 3.0, 0.5, op=0.6))
    out.append(sketch(body, 1.2, seed, 0.6))
    out.append(nib([(cx, top + h * 0.06), (cx, top)], 1.6, taper=(1, 0.3), seed=seed, color=INK))
    return "".join(out)


def walk_lamp(U, x, base, h, seed):
    """Brooklyn Bridge promenade lamp: slim post, two arms with lanterns."""
    out = [nib([(x, base), (x, base - h * 0.5), (x, base - h * 0.82)], max(1.4, h * 0.035), taper=(1.2, 0.8), seed=seed, color=INK)]
    out.append(P(f"M {f1(x)} {f1(base - h * 0.8)} Q {f1(x)} {f1(base - h * 0.9)} {f1(x - h * 0.12)} {f1(base - h * 0.86)} "
                 f"M {f1(x)} {f1(base - h * 0.8)} Q {f1(x)} {f1(base - h * 0.9)} {f1(x + h * 0.12)} {f1(base - h * 0.86)}", max(1.0, h * 0.02)))
    for sg in (-1, 1):
        out.append(lantern(U, x + sg * h * 0.12, base - h * 0.74, h * 0.13, seed + sg, max(1.0, h * 0.02), h > 120))
    out.append(F([(x - h * 0.03, base), (x + h * 0.03, base), (x + h * 0.02, base - h * 0.06), (x - h * 0.02, base - h * 0.06)], INK, 0.9))
    return "".join(out)


@design("new-york")
def new_york(U):
    """On the Brooklyn Bridge promenade at midspan, walking toward the Gothic granite tower: the boardwalk
    converging into the central pier, the main cables sweeping up to the saddles with the web of suspenders and
    stays, Lower Manhattan seen through the twin pointed arches, the flag (the accent) on top."""
    C = Cam(f=330, cx=300, vpy=362, eye=1.6)
    TZ, DEP = 58.0, 18.0
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 470, 112, 120, 22, 4) + cloud(U, 128, 132, 110, 18, 5) + cloud(U, 520, 196, 70, 11, 6))
    # Lower Manhattan, far beyond (drawn first; the tower covers most of it)
    hor = C(0, -40, 1500)[1]
    sky_ = skyline_strip(U, 40, 560, hor, 7, hmax=95)
    sky_ += spire_tower(U, 352, hor, hor - 150, 26, 8)
    art.append(sky_)
    art.append(sky_rules(U, 40, 560, hor - 30, hor + 2, 2.6, 5.0, 0.35, 9))
    # the tower: front face at TZ, two pointed arches, central pier, cornice
    tx0, tx1 = -20.0, 20.0
    TOP = 44.0
    face = C.qz(TZ, tx0, tx1, -1.0, TOP)
    fm = homog(face)

    def arch(Z, a, b, y0=0.0, spring=26.0, apex=35.5):
        pts = [C(a, y0, Z), C(a, spring, Z)]
        cxa = (a + b) / 2
        hw = (b - a) / 2
        for k in range(1, 12):
            t = k / 12
            ang = math.pi * t
            xx = cxa - hw * math.cos(ang)
            yy = spring + (apex - spring) * math.sin(ang) ** 0.75
            if k == 6:
                yy = apex
            pts.append(C(xx, yy, Z))
        pts += [C(b, spring, Z), C(b, y0, Z)]
        return pts
    arches = [(-15.4, -5.4), (5.4, 15.4)]
    fronts = [arch(TZ, a, b) for a, b in arches]
    backs = [arch(TZ + DEP, a, b) for a, b in arches]
    body = poly(face) + " " + " ".join(poly(p_) for p_ in fronts)
    art.append(f'<path d="{body}" fill="{PAPER}" fill-rule="evenodd"/>')
    # ashlar courses + staggered joints
    crs = []
    rr = random.Random(11)
    Y = -1.0
    k = 0
    while Y < TOP - 4:
        crs.append((C(tx0, Y, TZ), C(tx1, Y, TZ)))
        X = tx0 + (k % 2) * 0.9 + rr.uniform(0, 0.4)
        while X < tx1:
            crs.append((C(X, Y, TZ), C(X, Y + 1.15, TZ)))
            X += rr.uniform(1.6, 2.6)
        Y += 1.15
        k += 1
    art.append(clipped(U("tw"), body, segs(crs, 0.55, 12, 0.05, op=0.55)))
    art.append(clipped(U("tw2"), body, ST(U, poly(face), 1600, light=(200, 120), r=(0.35, 0.85), op=0.5)
                        + H(U, [C(10, -1, TZ), C(tx1, -1, TZ), C(tx1, TOP, TZ), C(10, TOP, TZ)], 90, 3.2, 0.7, op=0.55)
                        + H(U, [C(-2.5, -1, TZ), C(2.5, -1, TZ), C(2.5, 33, TZ), C(-2.5, 33, TZ)], 90, 4.0, 0.6, op=0.45)))
    # pilaster strips flanking each arch and the recessed panel above
    pil = []
    for a, b in arches:
        for X in (a - 1.2, b + 1.2):
            pil.append((C(X, -1, TZ), C(X, 37.5, TZ)))
    art.append(segs(pil, 1.1, 13, 0.05))
    pan = [C(-16.6, 37.5, TZ), C(16.6, 37.5, TZ)]
    art.append(pen(pan, 1.4, 14, 0.05))
    # through the arches: shadowed jambs/soffits, then the sky and skyline seen through the far opening
    for fr, bk in zip(fronts, backs):
        art.append(F(fr, PAPER) + tone(U, fr, 4, 80))
        inner = sky_ + spire_tower(U, 352, hor, hor - 150, 26, 8)
        art.append(clipped(U("thr"), poly(bk), f'<rect x="0" y="0" width="600" height="600" fill="{PAPER}"/>' + inner
                           + sky_rules(U, 40, 560, hor - 30, hor + 2, 2.6, 5.0, 0.35, 9)))
        art.append(pen(bk, 1.0, 15, 0.05, closed=False))
        art.append(pen(fr, 2.0, 16, 0.05, closed=False))
        # arch moulding
        art.append(pen([pt(p_, (300, 200), -0.02) for p_ in fr[1:-1]], 0.9, 17, 0.05))
    # cornice and attic
    cor = [C(tx0 - 0.8, TOP - 3.2, TZ - 0.8), C(tx1 + 0.8, TOP - 3.2, TZ - 0.8), C(tx1 + 0.8, TOP - 1.6, TZ - 0.8), C(tx0 - 0.8, TOP - 1.6, TZ - 0.8)]
    art.append(F(cor, PAPER) + H(U, cor, 0, 1.4, 0.8) + sketch(cor, 1.6, 18, 0.6))
    att = [C(tx0 + 0.4, TOP, TZ), C(tx1 - 0.4, TOP, TZ), C(tx1 - 0.4, TOP - 1.6, TZ), C(tx0 + 0.4, TOP - 1.6, TZ)]
    art.append(F(att, PAPER) + segs([(C(X, TOP - 1.6, TZ), C(X, TOP - 0.4, TZ)) for X in [tx0 + 1 + i * 1.3 for i in range(30)]], 0.8, 19, 0)
               + sketch(att, 1.6, 20, 0.6))
    art.append(seg(*C(tx0 - 0.9, TOP - 3.4, TZ - 0.8), *C(tx1 + 0.9, TOP - 3.4, TZ - 0.8), 2.0, 21, 0))
    art.append(pen([C(tx0, -1, TZ), C(tx0, TOP - 3.2, TZ)], 2.4, 22, 0.1) + pen([C(tx1, -1, TZ), C(tx1, TOP - 3.2, TZ)], 2.8, 23, 0.1))
    # the flag on its staff at the top (the accent)
    fx, fy = C(0, TOP, TZ)
    fs = C.f / TZ
    art.append(seg(fx, fy, fx, fy - 9 * fs, 1.6, 24, 0))
    art.append(flag(U, fx, fy - 9 * fs, 4.2 * fs, 2.6 * fs, 25))
    # cables: two inner planes beside the promenade, two outer planes; suspenders + diagonal stays
    def cy(Z, Yt=40.5, Y0=2.0):
        return Y0 + (Yt - Y0) * (max(0.0, Z) / TZ) ** 2
    for X in (-13.0, 13.0, -4.6, 4.6):
        inner = abs(X) < 6
        sus, sty = [], []
        Z = 1.0
        while Z < TZ - 0.8:
            sus.append((C(X, cy(Z), Z), C(X, -0.6 if inner else -1.6, Z)))
            Z += 1.9
        for k in range(1, 12):
            Zk = TZ - k * 3.6
            if Zk < 1.5:
                break
            sty.append((C(X, 39.5, TZ - 0.5), C(X, -0.6 if inner else -1.6, Zk)))
        art.append(segs(sus, 0.75 if inner else 0.6, int(X * 10) + 30, 0.05, op=0.95))
        art.append(segs(sty, 0.7 if inner else 0.55, int(X * 10) + 31, 0.05, op=0.85))
        cab = [C(X, cy(Z), Z) for Z in [0.6 + i * 0.5 for i in range(int((TZ - 0.6) / 0.5) + 1)]]
        cab = [p_ for p_ in cab if -60 < p_[0] < 660]
        art.append(nib(cab, 3.4 if inner else 2.6, taper=(1, 0.7), ramp=0.1, seed=int(X) + 40, color=INK))
    # lower roadways seen past the promenade edges: dark under-structure, car roofs
    for sg in (-1, 1):
        rd = [C(sg * 2.8, -1.2, 2), C(sg * 2.8, -1.2, TZ), C(sg * 16, -1.2, TZ), C(sg * 16, -1.2, 2)]
        art.append(F(rd, PAPER) + tone(U, rd, 2, 75 if sg < 0 else 105))
    # the promenade: planks, centre line, edge beams, railings
    W_ = 2.8
    walk = [C(-W_, 0, 4.0), C(-W_, 0, TZ), C(W_, 0, TZ), C(W_, 0, 4.0)]
    art.append(F(walk, PAPER))
    pl = []
    Z = 1.2
    while Z < TZ:
        pl.append((C(-W_, 0, Z), C(W_, 0, Z)))
        Z += 0.32 if Z > 6 else 0.26
    art.append(segs(pl, 0.7, 50, 0.1, op=0.75))
    rr = random.Random(51)
    jt = []
    Z = 1.2
    while Z < TZ * 0.5:
        X = -W_ + rr.uniform(0, 1.5)
        while X < W_:
            jt.append((C(X, 0, Z), C(X, 0, Z + 0.3)))
            X += rr.uniform(1.0, 2.4)
        Z += 0.3
    art.append(segs(jt, 0.6, 52, 0, op=0.6))
    art.append(H(U, [C(0.2, 0, 1.2), C(0.2, 0, TZ), C(W_, 0, TZ), C(W_, 0, 1.2)], 80, 4.0, 0.6, op=0.35))
    art.append(segs([(C(-0.08, 0.01, 1.2), C(-0.08, 0.01, TZ)), (C(0.08, 0.01, 1.2), C(0.08, 0.01, TZ))], 1.0, 53, 0.05))
    for sg in (-1, 1):
        rl = [C(sg * W_, 1.05, 1.2), C(sg * W_, 1.05, TZ)]
        posts = [(C(sg * W_, 0, Z), C(sg * W_, 1.05, Z)) for Z in [1.6 * 1.08 ** k for k in range(40) if 1.6 * 1.08 ** k < TZ]]
        bars = [(C(sg * W_, 0.0, Z), C(sg * W_, 1.05, Z)) for Z in [1.5 + 0.14 * k * (1 + k * 0.02) for k in range(200) if 1.5 + 0.14 * k * (1 + k * 0.02) < TZ]]
        art.append(segs(bars, 0.5, 54, 0, op=0.65) + segs(posts, 1.4, 55, 0))
        art.append(pen(rl, 2.0, 56, 0.1) + pen([C(sg * W_, 0.5, 1.2), C(sg * W_, 0.5, TZ)], 0.9, 57, 0.1)
                   + pen([C(sg * W_, 0, 1.2), C(sg * W_, 0, TZ)], 1.6, 58, 0.1))
    # promenade lamps
    for Z in (14, 25, 37, 48):
        for sg in (-1, 1):
            x, yb = C(sg * (W_ - 0.1), 0, Z)
            art.append(walk_lamp(U, x, yb, C.f * 4.4 / Z, int(Z) + sg))
    # people on the boardwalk
    for X, Z, sd, fl in ((-1.6, 34, 1, False), (1.2, 30, 2, True), (0.5, 24, 3, False), (-0.9, 20, 4, True), (1.8, 16, 5, False),
                         (-1.9, 12.5, 6, True), (-1.4, 12.8, 7, True), (0.4, 44, 8, False), (-0.6, 50, 9, True)):
        art.append(person3(C, X, 0, Z, 80 + sd, flip=fl, bag=sd == 5))
    x, yb = C(1.0, 0, 11.0)
    art.append(cyclist(x, yb, C.f * 1.75 / 11.0, 90, flip=True))
    art.append(gulls([(108, 220, 7), (126, 206, 5), (494, 240, 6)], 91))
    return plate(U, "new-york", art, 41, frame=(300, 246, 262, 208))


# ================================================================ CHICAGO
def bay_facade(U, q, bays, floors, seed, gl, kind="chicago", piers=True, op=1.0):
    """Windows on a wall quad laid out in structural bays: 'chicago' = a wide fixed pane between two narrow sashes
    under hatched spandrels; 'deco' = tall paired slots between continuous piers; 'sash' = paired sash windows."""
    m = homog(q)
    shapes, bars = [], []
    for i in range(bays):
        u0, u1 = i / bays, (i + 1) / bays
        for j in range(floors):
            v0, v1 = j / floors, (j + 1) / floors
            a, b = u0 + (u1 - u0) * 0.1, u1 - (u1 - u0) * 0.1
            c, d = v0 + (v1 - v0) * 0.2, v1 - (v1 - v0) * 0.12
            if kind == "chicago":
                shapes.append([(a, c), (b, c), (b, d), (a, d)])
                for f in (0.24, 0.76):
                    bars.append(((lerp(a, b, f), c), (lerp(a, b, f), d)))
            elif kind == "deco":
                for k in range(2):
                    aa = lerp(a, b, 0.08 + k * 0.5)
                    shapes.append([(aa, c - (v1 - v0) * 0.08), (aa + (b - a) * 0.34, c - (v1 - v0) * 0.08), (aa + (b - a) * 0.34, d + (v1 - v0) * 0.08),
                                   (aa, d + (v1 - v0) * 0.08)])
            else:
                for k in range(2):
                    aa = lerp(a, b, 0.1 + k * 0.48)
                    shapes.append([(aa, c), (aa + (b - a) * 0.32, c), (aa + (b - a) * 0.32, d), (aa, d)])
                    bars.append(((aa, (c + d) / 2), (aa + (b - a) * 0.32, (c + d) / 2)))
    out = [windows(m, shapes, gl, op=op, stroke=0.6)]
    if bars:
        out.append(rules_u(m, bars, 0.6, seed, color=PAPER))
    if piers:
        out.append(rules_u(m, [((i / bays, 0), (i / bays, 1)) for i in range(1, bays)], 0.8, seed + 1, op=0.8))
    return "".join(out)


def face_x(U, C, X, Z0, Z1, Y0, Y1, seed, cols=None, rows=None, style="pane", lvl=0, gl=None, dark_p=0.2, cornice=True, ang=78):
    """A building wall in the plane X between Z0..Z1 (near..far), windows in perspective, tone, contour."""
    q = C.qx(X, Z0, Z1, Y0, Y1)
    out = [F(q, PAPER)]
    c = cols or max(2, int((Z1 - Z0) / 6.5))
    r = rows or max(2, int((Y1 - Y0) / 4.0))
    m = homog(q)
    inner = [m(0.0, 0.03), m(1.0, 0.03), m(1.0, 0.98), m(0.0, 0.98)]
    if style in ("chicago", "deco", "sash"):
        out.append(bay_facade(U, inner, c, r, seed, gl, style))
    else:
        out.append(facade(U, inner, c, r, style, seed, dark_p=dark_p, w=0.7, mx=0.22, my=0.24))
    out.append(tone(U, q, lvl, ang))
    if cornice:
        out.append(pen([C(X, Y1 - 1.2, Z0), C(X, Y1 - 1.2, Z1)], 1.1, seed, 0.05))
    out.append(sketch(q, 1.5, seed + 1, 0.8))
    return "".join(out)


def bascule_leaf(U, C, X0, sg, Zf, Zb, ang, L, Y0, seed):
    """A raised bascule leaf: two through-girders (Warren-truss lattice) rising from the pivot on the bank,
    floor beams between them seen from below, the counterweight pit edge."""
    out = []
    a = math.radians(ang)
    ux, uy = sg * math.cos(a), math.sin(a)          # along the leaf (world X, Y)
    nx, ny = -sg * math.sin(a) * -1, math.cos(a)    # perpendicular, toward the outer chord

    def P3(s, d, Z):
        dd = lerp(4.2, 1.6, s / L) * d
        return C(X0 + ux * s - sg * math.sin(a) * dd * 0, Y0 + uy * s + dd, Z) if False else \
            C(X0 + ux * s + (-sg) * math.sin(a) * dd * -1 * 0 + nx * 0, Y0 + uy * s, Z)

    def pt3(s, d, Z):
        dd = lerp(4.4, 1.8, s / L) * d          # girder depth tapers to the tip
        px = X0 + ux * s + (-math.sin(a) * sg) * dd
        py = Y0 + uy * s + math.cos(a) * dd
        return C(px, py, Z)
    n = 9
    for Z, op_, w0 in ((Zb, 0.7, 1.0), (Zf, 1.0, 1.6)):
        top = [pt3(L * i / n, 1, Z) for i in range(n + 1)]
        bot = [pt3(L * i / n, 0, Z) for i in range(n + 1)]
        g = top + bot[::-1]
        part = [F(g, PAPER)]
        diag = []
        for i in range(n):
            diag.append((bot[i], top[i + 1]) if i % 2 == 0 else (top[i], bot[i + 1]))
            diag.append((top[i], bot[i]))
        part.append(segs(diag, 1.0 * w0, seed, 0.05))
        part.append(H(U, g, ang * (1 if sg > 0 else -1) + 90, 2.6, 0.7, op=0.5))
        part.append(pen(top, 1.6 * w0, seed, 0.05) + pen(bot, 1.6 * w0, seed + 1, 0.05) + pen([top[-1], bot[-1]], 1.4 * w0, seed, 0.05))
        out.append(f'<g opacity="{op_}">' + "".join(part) + "</g>")
        if Z == Zb:
            # floor beams across the leaf, seen from beneath (between the girders)
            fb = []
            for i in range(n + 1):
                fb.append((pt3(L * i / n, 0, Zb), pt3(L * i / n, 0, Zf)))
            deck = [pt3(0, 0, Zf), pt3(L, 0, Zf), pt3(L, 0, Zb), pt3(0, 0, Zb)]
            out.append(F(deck, PAPER) + tone(U, deck, 3, 20 if sg > 0 else 160) + segs(fb, 1.1, seed + 3, 0.05)
                       + pen([deck[1], deck[2]], 1.4, seed, 0.05))
    return "".join(out)


def deco_crown(U, cx, top, w, h, seed):
    """A stepped Art Deco crown with a ribbed dome and lantern (the cupola of a 1920s jewellers' tower)."""
    out = []
    t1 = [(cx - w * 0.5, top + h), (cx + w * 0.5, top + h), (cx + w * 0.5, top + h * 0.62), (cx - w * 0.5, top + h * 0.62)]
    t2 = [(cx - w * 0.36, top + h * 0.62), (cx + w * 0.36, top + h * 0.62), (cx + w * 0.36, top + h * 0.42), (cx - w * 0.36, top + h * 0.42)]
    for q, sd in ((t1, 1), (t2, 2)):
        out.append(F(q, PAPER) + H(U, [pt(q[0], q[1], 0.6), q[1], q[2], pt(q[3], q[2], 0.6)], 90, 1.5, 0.7)
                   + segs([(pt(q[0], q[1], u), pt(q[3], q[2], u)) for u in (0.2, 0.4, 0.6, 0.8)], 0.8, seed + sd, 0) + sketch(q, 1.2, seed + sd, 0.4))
    dome = [(cx - w * 0.3, top + h * 0.42)] + [(cx - w * 0.3 * math.cos(t), top + h * 0.42 - h * 0.3 * math.sin(t)) for t in [i * math.pi / 12 for i in range(1, 12)]] + [(cx + w * 0.3, top + h * 0.42)]
    out.append(F(dome, PAPER) + H(U, dome, 90, 1.4, 0.7, span=(0.55, 1), dark=(cx + w, top + h * 0.3))
               + segs([((cx + w * 0.3 * u, top + h * 0.42), (cx + w * 0.12 * u, top + h * 0.14)) for u in (-0.66, -0.33, 0, 0.33, 0.66)], 0.7, seed, 0)
               + pen(dome, 1.3, seed, 0.05))
    lan = [(cx - w * 0.06, top + h * 0.13), (cx + w * 0.06, top + h * 0.13), (cx + w * 0.06, top + h * 0.03), (cx - w * 0.06, top + h * 0.03)]
    out.append(F(lan, PAPER) + sketch(lan, 1.0, seed, 0.2) + seg(cx, top + h * 0.03, cx, top - h * 0.06, 1.2, seed, 0))
    return "".join(out)


def tour_boat3(U, C, X, Z0, Z1, seed):
    """A river architecture-tour boat, its port side toward us: long low hull (the accent), open upper deck with
    seated passengers under a canopy rail, wake."""
    out = []
    hull = [C(X, 1.2, Z0), C(X, 1.2, Z1), C(X, 0.0, Z1 - 1.2), C(X, -0.2, Z0 + 0.8)]
    bow = [C(X, 1.2, Z0), C(X + 2.0, 1.25, Z0 - 2.4), C(X + 4.0, 1.2, Z0), C(X + 2, -0.2, Z0 - 0.6), C(X, -0.2, Z0 + 0.8)]
    out.append(F(bow, PAPER) + H(U, bow, 0, 1.8, 0.7) + sketch(bow, 1.4, seed, 0.3))
    out.append(F(hull, PAPER))
    band = [C(X, 1.2, Z0), C(X, 1.2, Z1), C(X, 0.5, Z1 - 0.6), C(X, 0.5, Z0 + 0.3)]
    out.append(H(U, band, 0, 2.2, 0.6, op=0.5))
    out.append(H(U, [C(X, 0.5, Z0 + 0.3), C(X, 0.5, Z1 - 0.6), C(X, 0.0, Z1 - 1.2), C(X, -0.2, Z0 + 0.8)], 0, 1.8, 0.8))
    out.append(sketch(hull, 1.8, seed + 1, 0.5))
    cab = C.qx(X + 0.4, Z0 + 1.5, Z1 - 1.5, 1.2, 3.0)
    out.append(F(cab, PAPER) + sketch(cab, 1.3, seed + 2, 0.3))
    m = homog(cab)
    out.append(f'<path d="{" ".join(poly([m((i + 0.15) / 12, 0.2), m((i + 0.85) / 12, 0.2), m((i + 0.85) / 12, 0.8), m((i + 0.15) / 12, 0.8)]) for i in range(12))}" fill="{INK}" opacity="0.85"/>')
    rail = [C(X + 0.4, 4.0, Z0 + 1.5), C(X + 0.4, 4.0, Z1 - 1.5)]
    out.append(pen(rail, 1.2, seed, 0.05) + segs([(C(X + 0.4, 3.0, z), C(X + 0.4, 4.0, z)) for z in [Z0 + 1.5 + i * 1.6 for i in range(int((Z1 - Z0 - 3) / 1.6) + 1)]], 0.8, seed, 0))
    rr = random.Random(seed)
    for z in [Z0 + 2.2 + i * 1.5 for i in range(int((Z1 - Z0 - 4) / 1.5))]:
        if rr.random() < 0.8:
            x, y = C(X + 1.2, 3.0, z)
            s = C.f / z
            out.append(f'<circle cx="{f1(x)}" cy="{f1(y - 1.15 * s)}" r="{f1(0.22 * s)}" fill="{INK}"/>'
                       + F(smooth_closed([(x - 0.3 * s, y), (x + 0.3 * s, y), (x + 0.26 * s, y - 0.9 * s), (x - 0.26 * s, y - 0.9 * s)]), INK, 0.9))
    w0 = C(X - 0.2, 0, Z0 - 1)
    w1 = C(X - 3, 0, Z0 - 6)
    out.append(P(f"M {f1(w0[0])} {f1(w0[1])} Q {f1((w0[0] + w1[0]) / 2)} {f1(w0[1] + 4)} {f1(w1[0])} {f1(w1[1] + 6)}", 1.2, INK, 0.85))
    return "".join(out)


def sailboat3(U, C, Xc, Z0, L, beam, mh, seed, head=30.0):
    """A sloop under sail heading away from us at an angle (head degrees to the right of straight ahead): vermilion
    hull with its starboard side and transom toward us, mast, a bellied mainsail on the boom, a jib."""
    h = math.radians(head)
    sh, ch = math.sin(h), math.cos(h)

    def W3(al, ac, Y):           # along the keel from the stern, across to starboard (+), height
        return C(Xc + al * sh + ac * ch, Y, Z0 + al * ch - ac * sh)
    out = []
    hb = beam / 2
    side = [W3(0, hb, 1.0), W3(L * 0.75, hb * 0.9, 1.05), W3(L, 0, 1.35), W3(L * 0.92, 0, -0.1), W3(L * 0.5, hb * 0.85, -0.3), W3(0.3, hb * 0.8, -0.1)]
    tr_ = [W3(0, -hb, 1.0), W3(0, hb, 1.0), W3(0.2, hb * 0.8, -0.15), W3(0.2, -hb * 0.8, -0.15)]
    deck = [W3(0, -hb, 1.0), W3(0, hb, 1.0), W3(L * 0.75, hb * 0.9, 1.05), W3(L, 0, 1.35), W3(L * 0.75, -hb * 0.9, 1.05)]
    out.append(F(deck, PAPER) + segs([(W3(0.5, -hb * 0.7, 1.0), W3(L * 0.7, -hb * 0.6, 1.05)), (W3(0.5, hb * 0.7, 1.0), W3(L * 0.7, hb * 0.6, 1.05))], 0.6, seed, 0))
    for q in (side, tr_):
        out.append(F(q, PAPER) + accent(U, poly(q), bbox(q), seed, op=0.95, ang=0, n=14, length=(5, 14), width=(1.2, 2.6)))
    out.append(H(U, tr_, 0, 2.0, 0.7, op=0.6) + H(U, side, 0, 2.6, 0.6, op=0.4, span=(0.5, 1), dark=side[4]))
    out.append(sketch(side, 1.4, seed, 0.3) + sketch(tr_, 1.4, seed + 1, 0.3) + pen(deck, 1.0, seed, 0.05, True))
    cab = [W3(L * 0.3, -hb * 0.5, 1.0), W3(L * 0.3, hb * 0.5, 1.0), W3(L * 0.3, hb * 0.45, 1.6), W3(L * 0.3, -hb * 0.45, 1.6)]
    out.append(F(cab, PAPER) + H(U, cab, 0, 1.4, 0.7) + sketch(cab, 1.0, seed, 0.2))
    mz = L * 0.5
    out.append(nib([W3(mz, 0, 1.0), W3(mz, 0, mh)], 2.0, taper=(1, 0.4), seed=seed, color=INK))
    boom_end = W3(0.4, -1.6, 2.3)                      # boom swung out to port
    main_ = [W3(mz, 0, 2.1), W3(mz - 0.2, -0.5, mh * 0.55), W3(mz, 0, mh - 0.4), boom_end, W3(mz * 0.5, -1.2, 2.0)]
    jib = [W3(L * 0.97, 0, 1.5), W3(mz + 0.1, 0, mh * 0.82), W3(mz + 0.4, -1.1, 2.0)]
    out.append(F(jib, PAPER) + H(U, jib, 90, 1.8, 0.6, span=(0.6, 1), dark=jib[2]) + pen(jib, 1.2, seed + 3, 0.05, True))
    out.append(F(main_, PAPER, smooth=False) + H(U, main_, 90, 1.8, 0.6, span=(0.55, 1), dark=boom_end) + pen(main_, 1.3, seed + 2, 0.05, True))
    out.append(pen([W3(mz, 0, 2.1), boom_end], 1.8, seed + 4, 0.05))
    out.append(segs([((W3(mz, 0, 2.1 + k * 2.2)), W3(mz - 0.3, -0.35 - k * 0.04, 2.1 + k * 2.2 + 0.2)) for k in range(1, 6)], 0.6, seed, 0, op=0.7))
    wk = W3(0, 0, 0)
    out.append(P(f"M {f1(wk[0] - 14)} {f1(wk[1] + 3)} q 14 7 28 0 M {f1(wk[0] - 24)} {f1(wk[1] + 10)} q 24 9 48 0", 1.1, INK, 0.8))
    return "".join(out)


@design("chicago")
def chicago(U):
    """From the bow of a river boat heading west up the main branch: a bascule bridge ahead with both leaves
    raised to let a red-hulled sailboat through, Marina City's twin corncob towers rising on the north bank
    beyond it, the Wacker Drive towers in shadow above the Riverwalk vaults on the left, the river below."""
    C = Cam(f=260, cx=300, vpy=338, eye=3.0)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 470, 94, 120, 20, 4) + cloud(U, 214, 126, 90, 14, 5) + cloud(U, 540, 168, 60, 10, 6))
    art.append(gulls([(250, 176, 7), (268, 162, 5), (470, 206, 5)], 7))
    # the far corridor
    far = []
    for X0, X1, Z, Ht, sd in ((-62, -34, 560, 140, 1), (-30, -6, 720, 120, 2), (8, 30, 700, 160, 3), (40, 70, 520, 110, 4), (74, 110, 600, 130, 5)):
        q = C.qz(Z, X0, X1, 0, Ht)
        far.append(F(q, PAPER) + facade(U, quad_sub(q, 0.05, 0.03, 0.95, 1), 4, int(Ht / 10), "grid", sd, dark_p=0.2, w=0.5) + H(U, q, 90, 2.4, 0.6, op=0.5)
                   + sketch(q, 0.9, sd, 0.3))
    art.append('<g opacity="0.6">' + "".join(far) + "</g>")
    # north bank beyond the bridge: black steel slab, the two cobs
    slab = C.qx(34, 250, 290, 0, 200)
    sfront = C.qz(250, 34, 64, 0, 200)
    art.append(F(sfront, PAPER) + facade(U, sfront, 8, 56, "grid", 9, dark_p=0.0, w=0.45) + tone(U, sfront, 4, 90) + sketch(sfront, 1.3, 10, 0.4))
    art.append(F(slab, PAPER) + facade(U, slab, 10, 56, "grid", 7, dark_p=0.0, w=0.45) + tone(U, slab, 3, 90) + sketch(slab, 1.3, 8, 0.4))
    for X, Z, sd, fh in ((46, 218, 11, 4.0), (48, 172, 12, 4.8)):
        x, base = C(X, 2, Z)
        top = C(X, 179, Z)[1]
        R = 15.5 * C.f / Z
        art.append(corncob(U, x, top, base, R, C.vpy, sd, fh=fh))
    marina = [C(30, 2.2, 150), C(30, 2.2, 300), C(30, 0, 300), C(30, 0, 150)]
    art.append(F(marina, PAPER) + H(U, marina, 0, 1.4, 0.8) + pen([marina[0], marina[1]], 1.4, 13, 0.05))
    # the right bank, nearer: stone and glass blocks facing the river (lit side) down to the bridge
    for z0, z1, ht, st, sd in ((96, 150, 46, "sash", 14), (62, 96, 70, "chicago", 15), (20, 62, 38, "sash", 16), (-2, 20, 58, "chicago", 17)):
        art.append(face_x(U, C, 34, max(z0, 4), z1, 2, ht, sd, style=st, lvl=1, gl=gl))
    # the left bank: Wacker Drive towers (their river faces in shadow), the Riverwalk vaults beneath
    blds = [(2, 30, 70, "chicago"), (30, 58, 126, "deco"), (58, 90, 88, "sash"), (90, 130, 150, "deco"), (130, 180, 104, "chicago"), (180, 280, 130, "grid")]
    for i, (z0, z1, ht, st) in enumerate(reversed(blds)):
        art.append(face_x(U, C, -48, max(z0, 3), z1, 8, ht, 30 + i, style=st, lvl=3, gl=gl, dark_p=0.3))
    WK = -36.0
    vault = C.qx(WK, 3, 240, 2, 8)
    art.append(F(vault, PAPER) + H(U, vault, 0, 2.8, 0.6, op=0.5))
    arcs = []
    zs = [z for z in [3 * 1.16 ** k for k in range(40)] if z < 240]
    for za, zb in zip(zs, zs[1:]):
        a_, b_ = za + (zb - za) * 0.15, zb - (zb - za) * 0.15
        arcs.append([C(WK, 2, a_), C(WK, 4.8, a_)] + [C(WK, 4.8 + 1.8 * math.sin(math.pi * t / 8), lerp(a_, b_, t / 8)) for t in range(1, 8)]
                    + [C(WK, 4.8, b_), C(WK, 2, b_)])
    art.append(f'<path d="{" ".join(poly(p_) for p_ in arcs)}" fill="{INK}" opacity="0.86"/>')
    art.append(F(C.qx(WK, 3, 240, 8, 9.1), PAPER)
               + segs([(C(WK, 8, z), C(WK, 9.1, z)) for z in [3 + 0.5 * k * (1 + 0.03 * k) for k in range(160) if 3 + 0.5 * k * (1 + 0.03 * k) < 240]], 0.7, 43, 0)
               + pen([C(WK, 9.1, 3), C(WK, 9.1, 240)], 1.6, 44, 0.05) + pen([C(WK, 8, 3), C(WK, 8, 240)], 1.4, 44, 0.05)
               + pen([C(WK, 2, 3), C(WK, 2, 240)], 1.4, 45, 0.05))
    for z in (14, 24, 38, 58):
        x, yb = C(WK, 9.1, z)
        art.append(lamp(x, yb, C.f * 5.5 / z, 46 + z, "lantern", max(1.2, 24 / z)))
    rw = [C(WK, 2, 3), C(WK, 2, 240), C(-30, 2, 240), C(-30, 2, 3)]
    art.append(F(rw, PAPER) + clipped(U("rwk"), poly(rw), segs([(C(WK, 2, z), C(-30, 2, z)) for z in [3 * 1.08 ** k for k in range(70) if 3 * 1.08 ** k < 240]], 0.6, 47, 0, op=0.5)))
    ew = [C(-30, 2, 3), C(-30, 2, 240), C(-30, 0, 240), C(-30, 0, 3)]
    art.append(F(ew, PAPER) + H(U, ew, 0, 1.6, 0.8) + pen([ew[0], ew[1]], 1.8, 48, 0.05))
    for z, sd in ((48, 3), (30, 2), (19, 1)):
        art.append(tree3(U, C, -33.5, 2, z, 7.0, 6.0, 700 + sd, light=(-1, -1), lobes=5))
    for X, z, sd, fl in ((-31.5, 13, 1, False), (-34, 16, 2, True), (-31.2, 24, 3, False), (-32.5, 36, 5, True), (-31.6, 58, 6, False)):
        art.append(person3(C, X, 2, z, 80 + sd, flip=fl, bag=sd == 3))
    # the bridge ahead: raised leaves, tender houses, a sailboat going through (the accent)
    ZF, ZB = 46.0, 58.0
    art.append(bascule_leaf(U, C, 30, -1, ZF, ZB, 71, 27, 2.6, 22))
    art.append(bascule_leaf(U, C, -30, 1, ZF, ZB, 71, 27, 2.6, 23))
    for X, sd, fl in ((-30, 24, False), (30, 25, True)):
        x0_, yb = C(X, 2.2, ZF - 1)
        w_ = 8 * C.f / (ZF - 1)
        art.append(bridge_house(U, x0_ - (w_ if not fl else 0), yb, w_, 6.5 * C.f / (ZF - 1), sd, flip=fl))
    # the river
    water = [C(-30, 0, 2), C(-30, 0, 900), C(30, 0, 900), C(30, 0, 2), (640, 640), (-40, 640)]
    art.append(ripples(U, 0, 600, C.vpy + 1, 620, 26, dens=0.75, gap=(1.8, 10.0), ln=((3, 9), (14, 40)), w=(0.7, 1.3),
                       refl=[(C(48, 0, 172)[0] - 18, C(48, 0, 172)[0] + 18, 0.7), (C(34, 0, 250)[0] - 2, C(34, 0, 250)[0] + 12, 0.9),
                             (C(-30, 0, 46)[0] - 8, C(-30, 0, 46)[0] + 30, 0.6), (C(30, 0, 46)[0] - 30, C(30, 0, 46)[0] + 8, 0.6), (0, 150, 0.6)],
                       skip=[(286, 316)], clip=poly(water)))
    # on the river: a sloop heading for the open bridge, an architecture-tour boat (the accent) coming our way
    art.append(tour_boat3(U, C, 11, 17, 40, 26))
    art.append(sailboat3(U, C, -4.5, 24, 10, 3.4, 14, 27, head=12))
    return plate(U, "chicago", art, 51, frame=(300, 248, 262, 210))


def stone_pine(U, x, base, h, w, seed, lean=0.0, light=(-1, -1)):
    """An Italian stone pine: a tall, slightly leaning bare trunk forking high up into a few limbs, carrying a broad
    domed parasol of clumped needles, flat and dark underneath."""
    rnd = random.Random(seed)
    out = []
    ch = h * 0.24                                  # canopy depth
    cy = base - h + ch * 0.55                      # canopy underside
    tx = x + lean * h
    trunk = [(x, base), (x + lean * h * 0.35 + rnd.uniform(-2, 2), base - h * 0.4), (tx, cy + 2)]
    out.append(nib(trunk, max(3.0, w * 0.045), taper=(1.3, 0.7), ramp=0.4, seed=seed, color=INK))
    fork = (lerp(x, tx, 0.75), lerp(base, cy, 0.78))
    for k in (-1, 0.15, 1):
        ex = tx + k * w * 0.3
        out.append(nib([fork, (lerp(fork[0], ex, 0.6), lerp(fork[1], cy, 0.7)), (ex, cy + 3)], max(1.8, w * 0.022), taper=(1, 0.3), seed=seed + int(k * 3), color=INK))
    under = smooth_closed([(tx - w * 0.5, cy - ch * 0.15), (tx + w * 0.5, cy - ch * 0.15), (tx + w * 0.42, cy + ch * 0.12), (tx, cy + ch * 0.2), (tx - w * 0.42, cy + ch * 0.12)])
    out.append(F(under, INK, 0.88))
    rows = [(5, 0.0, 0.5), (4, -0.42, 0.4), (3, -0.78, 0.28)]
    for r_i, (n, dy, span) in enumerate(rows):
        for i in range(n):
            f = (i + 0.5) / n
            cx_ = tx + (f - 0.5) * 2 * span * w * 0.92 + rnd.uniform(-3, 3)
            cy_ = cy - ch * 0.15 + dy * ch + rnd.uniform(-2, 2)
            out.append(lobe(U, cx_, cy_, w * (0.15 if r_i < 2 else 0.13) + rnd.uniform(0, 3), ch * 0.34 + rnd.uniform(0, 2), seed * 11 + r_i * 10 + i,
                            light=light, w=1.4, dense=1.15))
    return "".join(out)


# ================================================================ ROME
def roman_face(U, C, X, Z0, Z1, Y1, seed, gl, floors=4, bay=3.6, shade=0, shops=True):
    """A Roman palazzo front in the plane X: rendered stucco, windows with stone frames and louvred shutters
    folded open, a moulded cornice on brackets, the eaves of a tiled roof, shop arches at the ground floor."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1
    out = []
    q = C.qx(X, Z0, Z1, 0, Y1)
    out.append(F(q, PAPER))
    m = Wm(C, (X, Z0), (X, Z1), 0, Y1)
    L = Z1 - Z0
    nb = max(1, int(L / bay))
    fh = (Y1 - 4.6) / floors
    shapes, shut, frames, sills = [], [], [], []
    for i in range(nb):
        u0, u1 = i / nb, (i + 1) / nb
        uc = (u0 + u1) / 2
        ww = (u1 - u0) * 0.32
        for j in range(floors):
            yb = 4.6 + j * fh + fh * 0.18
            yt = yb + fh * 0.62
            v0, v1 = 1 - yt / Y1, 1 - yb / Y1
            w_ = [(uc - ww / 2, v0), (uc + ww / 2, v0), (uc + ww / 2, v1), (uc - ww / 2, v1)]
            if rnd.random() < 0.55:
                shapes.append(w_)
                for sgn in (-1, 1):
                    a_ = uc + sgn * ww / 2
                    b_ = uc + sgn * ww * 0.98
                    shut.append([(a_, v0), (b_, v0), (b_, v1), (a_, v1)])
            else:
                shut.append(w_)
            frames.append([(uc - ww * 0.62, v0 - 0.012), (uc + ww * 0.62, v0 - 0.012), (uc + ww * 0.62, v1 + 0.006), (uc - ww * 0.62, v1 + 0.006)])
            sills.append(((uc - ww * 0.7, v1 + 0.01), (uc + ww * 0.7, v1 + 0.01)))
    out.append(windows(m, frames, PAPER, stroke=0.7))
    out.append(windows(m, shapes, gl, stroke=0.8))
    shd, surl = hpat(U, 0, 1.6, 0.8)
    out.append(shd + windows(m, shut, surl, stroke=0.8))
    out.append(rules_u(m, sills, 1.2, seed))
    # string course + cornice on brackets + roof eaves
    out.append(rules_u(m, [((0, 1 - 4.4 / Y1), (1, 1 - 4.4 / Y1)), ((0, 1 - 4.0 / Y1), (1, 1 - 4.0 / Y1))], 0.9, seed + 1))
    cor = [m(0, 0), m(1, 0), C(X + sg * 0.7, Y1 - 0.9, Z1), C(X + sg * 0.7, Y1 - 0.9, Z0)]
    eave = [C(X + sg * 0.7, Y1 + 0.15, Z0), C(X + sg * 0.7, Y1 + 0.15, Z1), C(X + sg * 1.1, Y1 + 0.35, Z1), C(X + sg * 1.1, Y1 + 0.35, Z0)]
    out.append(F(cor, PAPER) + H(U, cor, 90, 1.6, 0.8) + segs([(C(X, Y1 - 0.9, z), C(X + sg * 0.7, Y1 - 0.9, z)) for z in [Z0 + k * 0.7 for k in range(int(L / 0.7))]], 0.8, seed, 0))
    out.append(F(eave, PAPER) + H(U, eave, 0, 1.3, 0.8) + pen([eave[2], eave[3]], 1.6, seed, 0.05))
    # ground floor: shop arches and doors
    if shops:
        arches = []
        for i in range(nb):
            u0, u1 = (i + 0.18) / nb, (i + 0.82) / nb
            arches.append(arch_u(u0, u1, 1 - 3.7 / Y1, 1.0, 0.25))
        out.append(windows(m, arches, INK, op=0.85, stroke=1.0))
    out.append(ST(U, poly(q), int(L * 30), light=(150, 100), r=(0.35, 0.8), op=0.45))
    out.append(tone(U, q, shade, 78))
    out.append(pen([m(0, 1), m(1, 1)], 1.4, seed, 0.05) + pen([m(1, 0), m(1, 1)], 1.6, seed + 2, 0.05) + pen([m(0, 0), m(0, 1)], 2.0, seed + 3, 0.05))
    return "".join(out)


def colosseum(U, C, Xc, Zc, a, b, seed, gl):
    """The Flavian Amphitheatre as an elliptical drum: the intact four-storey outer wall (arches between engaged
    columns, the attic with its small windows and corbels) sweeping round on the right, the brick buttress where
    it stops, and the inner ring's ragged two-storey arcade beyond it on the left. Light from the left."""
    TIERS = [(0.0, 10.5), (10.5, 22.0), (22.0, 33.5), (33.5, 48.5)]
    out = []
    NB = 80

    def Pt(th, Y, shrink=0.0):
        return C(Xc + (b - shrink) * math.sin(th), Y, Zc - (a - shrink) * math.cos(th))
    TH0 = -0.1                         # the outer wall begins here (buttress); left of it only the inner ring stands
    ths = [-math.pi / 2 + math.pi * i / (NB // 2) for i in range(NB // 2 + 1)]
    # inner ring on the left (theta < TH0)
    inner = []
    itop = []
    for i in range(len(ths) - 1):
        t0, t1 = ths[i], ths[i + 1]
        if t1 > TH0 + 0.02:
            continue
        rnd = random.Random(i)
        topY = 30 + 3 * math.sin(i * 1.7) + rnd.uniform(-1.5, 1.5) - (abs(t0) - 0.2) * 6
        for (y0, y1) in ((0.0, 10.5), (10.5, 22.0), (22.0, topY)):
            if y1 <= y0 + 1:
                continue
            q = [Pt(t0, y1, 12), Pt(t1, y1, 12), Pt(t1, y0, 12), Pt(t0, y0, 12)]
            if abs(q[1][0] - q[0][0]) < 0.6:
                continue
            inner.append(F(q, PAPER))
            if y1 - y0 > 8:
                m = homog(q)
                inner.append(F([m(0.2, 1.0), m(0.2, 0.45), m(0.35, 0.26), m(0.5, 0.2), m(0.65, 0.26), m(0.8, 0.45), m(0.8, 1.0)], INK, 0.82))
            inner.append(pen([q[0], q[3]], 0.9, i, 0))
            inner.append(H(U, q, 90, 2.6, 0.6, op=0.55))
        itop.append(Pt(t0, topY, 12))
    out.append("".join(inner))
    if itop:
        out.append(pen(itop, 1.6, seed, 0.3))
    # the outer wall, bay by bay (right side)
    wall, hq = [], []
    for i in range(len(ths) - 1):
        t0, t1 = ths[i], ths[i + 1]
        if t0 < TH0:
            continue
        nx = math.sin((t0 + t1) / 2)          # +1 = facing right (away from the light)
        shade = max(0.0, min(1.0, 0.3 + 0.7 * nx))
        for k, (y0, y1) in enumerate(TIERS):
            q = [Pt(t0, y1), Pt(t1, y1), Pt(t1, y0), Pt(t0, y0)]
            if abs(q[1][0] - q[0][0]) < 0.6:
                continue
            wall.append(F(q, PAPER))
            m = homog(q)
            if k < 3:
                op_ = [m(0.22, 1.0), m(0.22, 0.42), m(0.3, 0.27), m(0.4, 0.2), m(0.5, 0.18), m(0.6, 0.2), m(0.7, 0.27), m(0.78, 0.42), m(0.78, 1.0)]
                wall.append(F(op_, INK, 0.9 if k < 2 else 0.8))
                wall.append(segs([(m(0.0, 0.05), m(0.0, 1.0)), (m(0.08, 0.1), m(0.08, 1.0)), (m(0.92, 0.1), m(0.92, 1.0))], 0.8, i + k, 0))
            else:
                wall.append(seg(*m(0.0, 0.0), *m(0.0, 1.0), 0.9, i, 0))
                if i % 2 == 0:
                    wall.append(F([m(0.38, 0.42), m(0.62, 0.42), m(0.62, 0.62), m(0.38, 0.62)], INK, 0.85))
                wall.append(segs([(m(u, 0.1), m(u, 0.18)) for u in (0.25, 0.5, 0.75)], 0.9, i, 0))
            hq.append((q, shade))
        for Y in (10.5, 22.0, 33.5, 48.5):
            wall.append(pen([Pt(t0, Y), Pt(t1, Y)], 1.4 if Y < 48 else 2.0, i, 0))
        for Y in (11.6, 23.1, 34.6):
            wall.append(pen([Pt(t0, Y), Pt(t1, Y)], 0.7, i + 1, 0))
    out.append("".join(wall))
    for q, sh in hq:
        if sh > 0.35:
            out.append(H(U, q, 90, lerp(4.2, 1.7, sh), 0.7, wob=0.1, brk=0.05, op=min(1, sh)))
    # the brick buttress where the outer ring stops
    tb = [Pt(TH0, 48.5), Pt(TH0 - 0.015, 36), Pt(TH0 - 0.035, 18), Pt(TH0 - 0.05, 0), Pt(TH0, 0)]
    out.append(F(tb, PAPER) + H(U, tb, 0, 1.8, 0.8) + H(U, tb, 90, 3.2, 0.6, op=0.6) + pen(tb, 1.6, seed, 0.1, True))
    edge = [Pt(th, 48.5) for th in [TH0 + (math.pi / 2 - TH0) * k / 40 for k in range(41)]]
    out.append(pen(edge, 2.4, seed + 1, 0.1))
    out.append(pen([Pt(th, 0) for th in [-math.pi / 2 + math.pi * k / 40 for k in range(41)]], 2.0, seed + 2, 0.1))
    clip_d = poly(edge + [Pt(math.pi / 2, 0), Pt(TH0, 0)])
    out.append(ST(U, clip_d, 900, light=(200, 150), r=(0.35, 0.85), op=0.45))
    return "".join(out)


@design("rome")
def rome(U):
    """Down a cobbled Roman street at the end of the afternoon: ochre palazzi with folded shutters on the left, the
    Colle Oppio's garden wall and umbrella pines on the right, and filling the end of the street the Colosseum, its
    intact outer wall curving away on the right, the inner arcades showing where it broke. A red scooter."""
    C = Cam(f=262, cx=300, vpy=356, eye=1.6)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 440, 96, 120, 20, 4) + cloud(U, 190, 118, 90, 14, 5))
    art.append(gulls([(266, 150, 6), (282, 140, 4), (330, 128, 5), (346, 136, 4)], 6))
    # the Colosseum
    art.append(colosseum(U, C, 6, 146, 94, 78, 7, gl))
    # piazza at its foot
    pz = [C(-60, 0, 40), C(-60, 0, 70), C(120, 0, 70), C(120, 0, 40)]
    art.append(F(pz, PAPER) + clipped(U("pz"), poly(pz), segs([(C(-60, 0, z), C(120, 0, z)) for z in [40 + k * 2.0 for k in range(16)]], 0.6, 8, 0.1, op=0.5)))
    for X, z, sd, fl in ((2, 50, 1, False), (4.5, 52, 2, True), (14, 48, 3, False), (22, 56, 4, True), (-3, 58, 5, False)):
        art.append(person3(C, X, 0, z, 30 + sd, flip=fl))
    # umbrella pines on the right, beyond the garden wall (far to near)
    for X, z, h, w, sd in ((36, 64, 19, 15, 3), (17, 42, 18, 15, 2), (14, 21, 18.5, 15, 1)):
        x, yb = C(X, 0, z)
        s = C.f / z
        art.append(stone_pine(U, x, yb, h * s, w * s, 300 + sd, lean=0.03 if sd != 2 else -0.04))
    # garden wall on the right
    gw = C.qx(8, 4, 40, 0, 2.2)
    rr = random.Random(9)
    blk = []
    for k, y in enumerate((0.0, 0.55, 1.1, 1.65)):
        blk.append((C(8, y, 4), C(8, y, 40)))
        z = 4 + rr.uniform(0, 0.8)
        while z < 40:
            blk.append((C(8, y, z), C(8, y + 0.55, z)))
            z += rr.uniform(0.7, 1.3) * (1 + z * 0.04)
    art.append(F(gw, PAPER) + clipped(U("gw"), poly(gw), segs(blk, 0.6, 9, 0.1, op=0.7) + ST(U, poly(gw), 500, r=(0.4, 0.9), op=0.5)) + sketch(gw, 1.6, 10, 0.5))
    cap = [C(8, 2.2, 4), C(8, 2.2, 40), C(8.6, 2.35, 40), C(8.6, 2.35, 4)]
    art.append(F(cap, PAPER) + pen([cap[0], cap[1]], 1.8, 11, 0.05))
    # left: the palazzi
    for z0, z1, ht, sd, sh in ((28, 40, 19, 12, 0), (15, 28, 21, 13, 0), (3, 15, 18, 14, 0)):
        art.append(roman_face(U, C, -7.5, z0, z1, ht, sd, gl))
    # street: sampietrini setts, kerbs, narrow pavements
    road = [C(-5.6, 0, 2.5), C(-5.6, 0, 40), C(8, 0, 40), C(8, 0, 2.5)]
    art.append(F(road, PAPER) + clipped(U("rd"), poly(road), cobbles(U, C, -5.6, 8, 2.5, 40, 15, row=0.32, stone=0.36, w=0.7, op=0.65)))
    walk = [C(-7.5, 0.15, 2.5), C(-7.5, 0.15, 40), C(-5.6, 0.15, 40), C(-5.6, 0.15, 2.5)]
    art.append(F(walk, PAPER) + segs([(C(-7.5, 0.15, z), C(-5.6, 0.15, z)) for z in [2.5 + k * 1.1 for k in range(35)]], 0.6, 16, 0, op=0.6)
               + pen([C(-5.6, 0.15, 2.5), C(-5.6, 0.15, 40)], 1.5, 17, 0.1))
    # shadow of the palazzi across the street (sun low in the west, to the left)
    shd = [C(-5.6, 0, 2.5), C(-5.6, 0, 40), C(-1.0, 0, 40), C(1.5, 0, 2.5)]
    art.append(tone(U, shd, 2, 70))
    # life: a café table, a scooter (the accent), people, lamp
    for z, sd in ((9.0, 1), (12.5, 2)):
        tx_, ty_ = C(-6.6, 0.75, z)
        bx_, by_ = C(-6.6, 0.15, z)
        r = C.f * 0.35 / z
        art.append(f'<ellipse cx="{f1(tx_)}" cy="{f1(ty_)}" rx="{f1(r)}" ry="{f1(r * 0.3)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>'
                   + seg(tx_, ty_, bx_, by_, 1.4, sd, 0))
    for X, z, sd, fl in ((-6.2, 10.8, 1, False), (-6.0, 24, 2, True), (-1.5, 19, 3, False), (-0.9, 19.6, 4, True), (3.5, 30, 5, False), (6.6, 14, 6, True)):
        art.append(person3(C, X, 0.15 if X < -5.6 else 0, z, 40 + sd, flip=fl, bag=sd == 5))
    x, yb = C(-4.4, 0, 9.5)
    art.append(vespa(U, x, yb, C.f * 1.9 / 9.5, 50, flip=True))
    x, yb = C(7.4, 0, 12)
    art.append(lamp(x, yb, C.f * 4.4 / 12, 51, "lantern", 1.8))
    return plate(U, "rome", art, 61, frame=(300, 248, 262, 210))


# ================================================================ LISBON
def accent_ochre(U, d, box, seed=1, op=0.9, ang=-80, n=26, length=(10, 30), width=(2, 4)):
    """Lisbon's tram yellow, laid like the vermilion accent: a faded ochre wash with brush strokes."""
    light, base, dark = OCHRE
    return (f'<g opacity="{op:.2f}">' + wash(d, base, seed, layers=3, spread=1.0, opacity=0.45)
            + strokes(U("oc"), d, box, [light, dark, base, light], seed, n=n, angle=ang, length=length, width=width,
                      opacity=(0.15, 0.4)) + "</g>")


def bell_tower(U, x, base, top, w, seed):
    """A whitewashed Lisbon church bell tower: belfry arch, cornice, small dome and cross."""
    out = []
    h = base - top
    body = [(x - w / 2, top + h * 0.3), (x + w / 2, top + h * 0.3), (x + w / 2, base), (x - w / 2, base)]
    out.append(F(body, PAPER) + H(U, [(x + w * 0.1, top + h * 0.3), (x + w / 2, top + h * 0.3), (x + w / 2, base), (x + w * 0.1, base)], 90, 1.6, 0.7))
    out.append(F(arch_u(x - w * 0.28, x + w * 0.28, top + h * 0.36, top + h * 0.62, 0.35), INK, 0.88))
    out.append(sketch(body, 1.4, seed, 0.4) + seg(x - w * 0.6, top + h * 0.3, x + w * 0.6, top + h * 0.3, 1.8, seed, 0))
    dome = [(x - w * 0.45, top + h * 0.3)] + [(x - w * 0.45 * math.cos(t), top + h * 0.3 - h * 0.2 * math.sin(t)) for t in [i * math.pi / 10 for i in range(1, 10)]] + [(x + w * 0.45, top + h * 0.3)]
    out.append(F(dome, PAPER) + H(U, dome, 90, 1.4, 0.7, span=(0.55, 1), dark=(x + w, top)) + pen(dome, 1.3, seed, 0.05))
    out.append(seg(x, top + h * 0.1, x, top - h * 0.02, 1.4, seed, 0) + seg(x - w * 0.12, top + h * 0.02, x + w * 0.12, top + h * 0.02, 1.2, seed, 0))
    return "".join(out)


def front_house(U, C, Z, X0, X1, Yb, Ht, seed, gl, kind="tile", floors=3, s=0.0, lvl=0, laundry=False, shutters=0.3):
    """A Lisbon house front facing us in the plane Z, standing on a street rising with slope s (ground Y = s*X):
    azulejo lattice or plain stucco, tall windows in stone frames, iron balconies jutting toward us with their
    shadows, a cornice, the scalloped eaves of a tiled roof, a door on the hill."""
    rnd = random.Random(seed)
    Yt = Yb + Ht
    wall = [C(X0, Yt, Z), C(X1, Yt, Z), C(X1, s * X1, Z), C(X0, s * X0, Z)]
    out = [F(wall, PAPER)]
    W_ = X1 - X0
    if kind == "tile":
        lat = []
        d = 0.5
        k = -int(Ht / d) - 2
        while k * d < W_ + Ht:
            x0 = X0 + k * d
            lat.append((C(x0, Yb - 2, Z), C(x0 + Ht + 2, Yt, Z)))
            lat.append((C(x0 + Ht + 2, Yb - 2, Z), C(x0, Yt, Z)))
            k += 1
        dots = []
        for i in range(int(W_ / d) + 1):
            for j in range(int(Ht / d) + 1):
                x, y = C(X0 + (i + 0.5) * d, Yb + (j + 0.5) * d - 0.25, Z)
                dots.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="0.9"/>')
        out.append(clipped(U("az"), poly(wall), segs(lat, 0.5, seed, 0.02, op=0.7) + f'<g fill="{INK}" opacity="0.7">{"".join(dots)}</g>'))
    else:
        out.append(ST(U, poly(wall), int(W_ * 40), light=(100, 60), r=(0.35, 0.8), op=0.45))
    out.append(tone(U, wall, lvl, 70))
    m = Wm(C, (X0, Z), (X1, Z), Yb, Yt)
    nb = max(1, int(W_ / 2.6))
    fh = (Ht - 3.6) / floors
    frames, shapes, shut, bals = [], [], [], []
    for i in range(nb):
        uc = (i + 0.5) / nb
        ww = 1.0 / nb * 0.42
        for j in range(floors):
            y0 = Yb + 3.6 + j * fh + fh * 0.12
            y1 = y0 + fh * 0.7
            v0, v1 = 1 - (y1 - Yb) / Ht, 1 - (y0 - Yb) / Ht
            frames.append([(uc - ww * 0.66, v0 - 0.025), (uc + ww * 0.66, v0 - 0.025), (uc + ww * 0.66, v1 + 0.01), (uc - ww * 0.66, v1 + 0.01)])
            w_ = [(uc - ww / 2, v0), (uc + ww / 2, v0), (uc + ww / 2, v1), (uc - ww / 2, v1)]
            (shut if rnd.random() < shutters else shapes).append(w_)
            if rnd.random() < 0.75:
                bals.append((X0 + (uc - ww * 0.8) * W_, X0 + (uc + ww * 0.8) * W_, y0))
    out.append(windows(m, frames, PAPER, stroke=1.0))
    out.append(windows(m, shapes, gl, stroke=0.9))
    shd, surl = hpat(U, 0, 1.5, 0.8)
    out.append(shd + windows(m, shut, surl, stroke=0.9))
    for xa, xb, y0 in bals:
        # shadow of the balcony on the wall, slab, railing, a pot of geraniums now and then
        sh_ = [C(xa + 0.15, y0 - 0.05, Z), C(xb + 0.15, y0 - 0.05, Z), C(xb + 0.45, y0 - 0.55, Z), C(xa + 0.45, y0 - 0.55, Z)]
        out.append(H(U, sh_, 20, 1.4, 0.7))
        slab = [C(xa, y0, Z), C(xb, y0, Z), C(xb, y0, Z - 0.7), C(xa, y0, Z - 0.7)]
        out.append(F(slab, PAPER) + pen(slab, 1.0, seed, 0.02, True))
        front = [C(xa, y0 + 1.0, Z - 0.7), C(xb, y0 + 1.0, Z - 0.7), C(xb, y0, Z - 0.7), C(xa, y0, Z - 0.7)]
        bars = [(C(x, y0, Z - 0.7), C(x, y0 + 1.0, Z - 0.7)) for x in [xa + k * 0.13 for k in range(int((xb - xa) / 0.13) + 1)]]
        out.append(segs(bars, 0.55, seed, 0) + pen([front[0], front[1]], 1.3, seed, 0.02)
                   + segs([(C(xa, y0 + 1.0, Z), C(xa, y0 + 1.0, Z - 0.7)), (C(xb, y0 + 1.0, Z), C(xb, y0 + 1.0, Z - 0.7))], 1.0, seed, 0))
        out.append(P(" ".join(f"M {f1(C(x, y0 + 0.5, Z - 0.7)[0] - 1.6)} {f1(C(x, y0 + 0.5, Z - 0.7)[1])} a 1.6 1.6 0 1 0 3.2 0" for x in
                              [xa + (xb - xa) * f for f in (0.3, 0.7)]), 0.7) if rnd.random() < 0.6 else "")
        if rnd.random() < 0.4:
            px, py = C(xa + (xb - xa) * 0.25, y0 + 1.0, Z - 0.7)
            r = C.f / Z * 0.35
            out.append(f'<rect x="{f1(px - r * 0.5)}" y="{f1(py - r * 0.6)}" width="{f1(r)}" height="{f1(r * 0.6)}" fill="{INK}" opacity="0.85"/>'
                       + lobe(U, px, py - r * 0.9, r * 0.9, r * 0.55, seed + int(px), w=0.9, dense=1.3))
    # door on the slope
    xc = X0 + W_ * (0.5 if nb % 2 else 0.5 / nb + 0.0)
    g0 = s * xc
    dq = [C(xc - 0.6, g0 + 2.6, Z), C(xc + 0.6, g0 + 2.6, Z), C(xc + 0.6, s * (xc + 0.6), Z), C(xc - 0.6, s * (xc - 0.6), Z)]
    out.append(F(dq, PAPER) + F(quad_sub(dq, 0.1, 0.06, 0.9, 1.0), INK, 0.85) + sketch(dq, 1.1, seed, 0.2))
    # cornice, eave shadow, tiled roof edge
    out.append(pen([C(X0, Yt - 0.45, Z), C(X1, Yt - 0.45, Z)], 1.0, seed, 0.03))
    es = [C(X0, Yt, Z), C(X1, Yt, Z), C(X1, Yt - 0.8, Z), C(X0, Yt - 0.8, Z)]
    out.append(H(U, es, 0, 1.4, 0.7, op=0.8))
    eave = [C(X0 - 0.3, Yt + 0.4, Z - 0.6), C(X1 + 0.3, Yt + 0.4, Z - 0.6), C(X1 + 0.3, Yt, Z - 0.6), C(X0 - 0.3, Yt, Z - 0.6)]
    roof = [C(X0 - 0.3, Yt + 0.4, Z - 0.6), C(X1 + 0.3, Yt + 0.4, Z - 0.6), C(X1 + 0.3, Yt + 2.6, Z + 4), C(X0 - 0.3, Yt + 2.6, Z + 4)]
    out.append(F(roof, PAPER) + segs([(C(x, Yt + 0.4, Z - 0.6), C(x, Yt + 2.6, Z + 4)) for x in [X0 - 0.3 + k * 0.32 for k in range(int((W_ + 0.6) / 0.32) + 1)]], 0.7, seed, 0)
               + H(U, roof, 0, 2.2, 0.6, op=0.6) + pen([roof[2], roof[3]], 1.2, seed, 0.03))
    sc = []
    x = X0 - 0.3
    while x < X1 + 0.3:
        a_, b_ = C(x, Yt + 0.2, Z - 0.6), C(min(X1 + 0.3, x + 0.32), Yt + 0.2, Z - 0.6)
        sc.append(f"M {f1(a_[0])} {f1(a_[1])} Q {f1((a_[0] + b_[0]) / 2)} {f1(a_[1] + 4)} {f1(b_[0])} {f1(b_[1])}")
        x += 0.32
    out.append(F(eave, PAPER) + P(" ".join(sc), 0.9) + pen([eave[0], eave[1]], 1.3, seed, 0.03))
    if laundry:
        y0 = Yb + 3.6 + fh * 1.05
        xa, xb = X0 + W_ * 0.15, X0 + W_ * 0.85
        out.append(pen([C(xa, y0 + 1.6, Z - 0.7), C((xa + xb) / 2, y0 + 1.35, Z - 0.7), C(xb, y0 + 1.6, Z - 0.7)], 0.8, seed, 0.02, smooth=True))
        for t in (0.12, 0.3, 0.52, 0.7, 0.88):
            xx = lerp(xa, xb, t)
            yy = y0 + 1.6 - 0.25 * math.sin(math.pi * t)
            ww_ = rnd.uniform(0.3, 0.5)
            q = [C(xx - ww_, yy, Z - 0.7), C(xx + ww_, yy, Z - 0.7), C(xx + ww_ * 0.9, yy - rnd.uniform(0.6, 1.0), Z - 0.7), C(xx - ww_ * 0.9, yy - rnd.uniform(0.6, 1.0), Z - 0.7)]
            out.append(F(q, PAPER) + (H(U, q, 90, 1.5, 0.6, op=0.7) if rnd.random() < 0.5 else "") + pen(q, 0.9, seed + int(t * 10), 0.1, True))
    out.append(pen([wall[0], wall[3]], 1.6, seed + 2, 0.03) + pen([wall[1], wall[2]], 1.6, seed + 3, 0.03))
    return "".join(out)


def tram_side(U, C, X0, Z, s, seed, L=8.5, Ht=3.2):
    """A Lisbon electric tram climbing to the right, broadside on and tilted with the hill: rounded ends, window
    bays, the clerestory roof, trolley pole up to the wire, the ochre accent."""
    out = []

    def Pq(u, y, dz=0.0):                   # u along the tram (m from the rear/left end), y above the rails
        x = X0 + u
        return C(x, s * x + 0.35 + y, Z + dz)
    body = [Pq(0.15, Ht), Pq(L - 0.15, Ht), Pq(L, Ht - 0.4), Pq(L, 0.3), Pq(0, 0.3), Pq(0, Ht - 0.4)]
    out.append(F(body, PAPER))
    out.append(accent_ochre(U, poly(body), bbox(body), seed, op=0.95, n=30, length=(6, 18), width=(1.5, 3.2), ang=-80))
    out.append(H(U, [Pq(0, 1.15), Pq(L, 1.15), Pq(L, 0.3), Pq(0, 0.3)], 0, 1.8, 0.7, op=0.8))
    wins = []
    for i in range(7):
        a_ = 0.55 + i * (L - 1.1) / 7
        b_ = a_ + (L - 1.1) / 7 * 0.82
        wins.append([Pq(a_, Ht - 0.45), Pq(b_, Ht - 0.45), Pq(b_, 1.55), Pq(a_, 1.55)])
    out.append(f'<path d="{" ".join(poly(w_) for w_ in wins)}" fill="{INK}" opacity="0.86"/>')
    out.append(segs([(Pq(0, 1.35), Pq(L, 1.35)), (Pq(0, 1.15), Pq(L, 1.15)), (Pq(0, Ht - 0.3), Pq(L, Ht - 0.3))], 0.9, seed, 0.02))
    # door at the front end, people inside
    out.append(F([Pq(L - 0.95, Ht - 0.45), Pq(L - 0.25, Ht - 0.45), Pq(L - 0.25, 0.4), Pq(L - 0.95, 0.4)], INK, 0.8))
    for i in (1, 3, 4, 6):
        a_ = 0.55 + (i + 0.4) * (L - 1.1) / 7
        hx, hy = Pq(a_, 2.15)
        r = C.f / Z * 0.18
        out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(r)}" fill="{PAPER}" opacity="0.45"/>')
    clr = [Pq(1.2, Ht + 0.35), Pq(L - 1.2, Ht + 0.35), Pq(L - 1.2, Ht), Pq(1.2, Ht)]
    out.append(F(clr, PAPER) + H(U, clr, 0, 1.3, 0.7) + sketch(clr, 1.1, seed, 0.2))
    roof = [Pq(0.15, Ht), Pq(L - 0.15, Ht), Pq(L - 0.6, Ht + 0.18, 0.8), Pq(0.6, Ht + 0.18, 0.8)]
    out.append(pen(body, 1.8, seed, 0.03, True))
    # bumpers and wheels
    for u in (-0.15, L + 0.15):
        out.append(seg(*Pq(u, 0.5), *Pq(u, 0.25), 2.0, seed, 0))
    for u in (1.8, L - 1.8):
        x, y = Pq(u, 0.1)
        r = C.f / Z * 0.42
        out.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(r)}" fill="{INK}"/>')
    out.append(F([Pq(0.4, 0.32), Pq(L - 0.4, 0.32), Pq(L - 0.4, -0.05), Pq(0.4, -0.05)], INK, 0.8))
    # headlamp + destination box on the front end
    hx, hy = Pq(L, 1.0)
    out.append(f'<circle cx="{f1(hx + 1)}" cy="{f1(hy)}" r="2.6" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(F([Pq(L - 0.6, Ht + 0.3), Pq(L - 0.05, Ht + 0.3), Pq(L - 0.05, Ht - 0.1), Pq(L - 0.6, Ht - 0.1)], INK, 0.9))
    # trolley pole trailing back to the wire
    b0 = Pq(L * 0.62, Ht + 0.35)
    tip = Pq(L * 0.62 - 4.2, Ht + 2.55)
    out.append(pen([b0, tip], 1.6, seed, 0.03) + f'<circle cx="{f1(tip[0])}" cy="{f1(tip[1])}" r="1.8" fill="{INK}"/>')
    return "".join(out)


def castle_walls(U, pts, seed):
    """Crenellated castle walls and square towers along a hilltop silhouette (pts = ground line, left to right)."""
    out = []
    rnd = random.Random(seed)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        h = 22
        wall = [(x0, y0 - h), (x1, y1 - h), (x1, y1), (x0, y0)]
        out.append(F(wall, PAPER) + H(U, wall, 0, 2.6, 0.6, op=0.6) + ST(U, wall, 80, r=(0.4, 0.8), op=0.5))
        mer = []
        n = max(2, int((x1 - x0) / 7))
        for k in range(n):
            a_ = lerp(x0, x1, k / n)
            ya = lerp(y0, y1, k / n) - h
            mer.append([(a_, ya), (a_, ya - 4), (a_ + (x1 - x0) / n * 0.55, ya - 4 + (y1 - y0) / n * 0.55), (a_ + (x1 - x0) / n * 0.55, ya + (y1 - y0) / n * 0.55)])
        out.append(f'<path d="{" ".join(poly(q) for q in mer)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
        out.append(pen([(x0, y0 - h), (x1, y1 - h)], 1.3, seed, 0.1))
        tw = 16 + rnd.uniform(-3, 3)
        th = 40 + rnd.uniform(-6, 8)
        tq = [(x1 - tw / 2, y1 - th), (x1 + tw / 2, y1 - th), (x1 + tw / 2, y1), (x1 - tw / 2, y1)]
        out.append(F(tq, PAPER) + H(U, [(x1, y1 - th), (x1 + tw / 2, y1 - th), (x1 + tw / 2, y1), (x1, y1)], 90, 1.6, 0.7) + sketch(tq, 1.3, seed, 0.4))
        out.append(f'<path d="{" ".join(poly([(x1 - tw / 2 + k * tw / 4, y1 - th), (x1 - tw / 2 + k * tw / 4, y1 - th - 4), (x1 - tw / 2 + (k + 0.55) * tw / 4, y1 - th - 4), (x1 - tw / 2 + (k + 0.55) * tw / 4, y1 - th)]) for k in range(4))}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
        out.append(F([(x1 - 1.5, y1 - th * 0.6), (x1 + 1.5, y1 - th * 0.6), (x1 + 1.5, y1 - th * 0.45), (x1 - 1.5, y1 - th * 0.45)], INK, 0.85))
    return "".join(out)


def calcada(U, C, X0, X1, Z0, Z1, s, seed):
    """Portuguese pavement: small setts in a wave pattern (dark waves on light), on ground Y = s*X + 0.15."""
    rnd = random.Random(seed)
    out = []
    waves = []
    for k in range(9):
        zc = lerp(Z0, Z1, (k + 0.5) / 9)
        pts = []
        x = X0
        while x <= X1:
            pts.append(C(x, s * x + 0.15, zc + 0.35 * math.sin(x * 0.9 + k * 0.6)))
            x += 0.4
        waves.append(pts)
    for pts in waves:
        band = pts + [(p_[0], p_[1] + 2.2) for p_ in pts[::-1]]
        out.append(F(band, INK, 0.5))
    dots = []
    for i in range(1300):
        x = rnd.uniform(X0, X1)
        z = rnd.uniform(Z0, Z1)
        px, py = C(x, s * x + 0.15, z)
        dots.append(f'<rect x="{f1(px)}" y="{f1(py)}" width="1.4" height="1.0" fill="{INK}" opacity="0.35"/>')
    return "".join(out) + "".join(dots)


@design("lisbon")
def lisbon(U):
    """Across a steep Alfama street: azulejo-tiled and stuccoed house fronts stepping up the hill with iron
    balconies, geraniums and laundry, an old tram (the ochre accent) grinding up to the right under its wire,
    the castle walls on the hilltop above the roofs, the wave-pattern pavement at our feet, people on the climb."""
    s = 0.2
    C = Cam(f=250, cx=300, vpy=362, eye=1.6)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 168, 112, 120, 20, 4) + cloud(U, 262, 76, 70, 10, 5))
    art.append(gulls([(240, 120, 7), (258, 108, 5), (120, 150, 5)], 6))
    # the castle on the hill crest, above the roofs at upper right
    art.append(castle_walls(U, [(300, 176), (380, 146), (450, 128), (540, 118)], 7))
    hill = [(250, 196), (300, 176), (380, 146), (450, 128), (540, 118), (620, 112), (620, 260), (250, 260)]
    art.append(H(U, hill, 0, 3.6, 0.6, op=0.4))
    for x, y, r in ((330, 176, 14), (420, 150, 16), (500, 136, 13), (270, 196, 12)):
        art.append(lobe(U, x, y, r, r * 0.7, int(x), w=1.1, dense=1.1))
    # a twin-towered church further down the hill on the left, its façade between the towers
    for x in (128, 206):
        art.append(bell_tower(U, x, 232, 120, 30, int(x)))
    fa = [(143, 232), (191, 232), (191, 168), (167, 150), (143, 168)]
    art.append(F(fa, PAPER) + H(U, fa, 0, 3.0, 0.6, op=0.5) + F(arch_u(158, 176, 186, 232, 0.4), INK, 0.85) + pen(fa, 1.4, 8, 0.1, True)
               + f'<circle cx="167" cy="170" r="5" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    # the row of houses across the street, stepping up to the right
    Z = 15.0
    rows = [(-26, -18, 10.5, "plain", 1), (-18, -10.5, 12.5, "tile", 0), (-10.5, -3.5, 11.0, "plain", 0), (-3.5, 4.5, 12.5, "tile", 0),
            (4.5, 11.0, 10.5, "plain", 1), (11.0, 19.0, 12.0, "tile", 0), (19.0, 27.0, 10.5, "plain", 0)]
    for i, (x0, x1, ht, kd, lv) in enumerate(rows):
        Yb = s * x0
        art.append(front_house(U, C, Z + (0.4 if i % 2 else 0), x0, x1, Yb, ht + s * (x1 - x0), 20 + i, gl, kd,
                               floors=3, s=s, lvl=lv, laundry=i in (2, 5), shutters=0.25 if kd == "tile" else 0.45))
    # the street surface rising to the right, setts, the tram rails
    road = [C(-30, -30 * s, 8), C(32, 32 * s, 8), C(32, 32 * s, Z), C(-30, -30 * s, Z)]
    rr = random.Random(10)
    sets = []
    for k in range(18):
        zz = lerp(8, Z, k / 18)
        sets.append((C(-30, -30 * s, zz), C(32, 32 * s, zz)))
        x = -30 + rr.uniform(0, 0.5)
        while x < 32:
            sets.append((C(x, s * x, zz), C(x, s * x, zz + (Z - 8) / 18)))
            x += rr.uniform(0.35, 0.55)
    art.append(F(road, PAPER) + clipped(U("rd"), poly(road), segs(sets, 0.55, 11, 0.05, op=0.55)))
    for zr in (11.2, 12.6):
        art.append(pen([C(-30, -30 * s, zr), C(32, 32 * s, zr)], 1.5, 12, 0.02))
    # overhead wire + span wires to the house fronts
    art.append(pen([C(-30, -30 * s + 6.3, 11.9), C(32, 32 * s + 6.3, 11.9)], 0.9, 13, 0.02))
    for x in (-14, 2, 18):
        art.append(pen([C(x, s * x + 6.3, 11.9), C(x, s * x + 6.8, Z)], 0.7, 14, 0.02))
    # the tram climbing right
    art.append(tram_side(U, C, -4.5, 11.0, s, 15))
    # the near kerb and our pavement with its wave pattern
    kerb = [C(-30, -30 * s + 0.15, 8), C(32, 32 * s + 0.15, 8), C(32, 32 * s, 8), C(-30, -30 * s, 8)]
    pave = [C(-30, -30 * s + 0.15, 4), C(32, 32 * s + 0.15, 4), C(32, 32 * s + 0.15, 8), C(-30, -30 * s + 0.15, 8)]
    art.append(F(pave, PAPER) + clipped(U("cal"), poly(pave), calcada(U, C, -30, 32, 4, 8, s, 16)))
    art.append(F(kerb, PAPER) + pen([kerb[0], kerb[1]], 2.0, 17, 0.02))
    # people on the climb, a lamp post on our side
    for X, z, sd, fl in ((-12, 13.6, 1, False), (-9.5, 13.9, 2, False), (8.5, 13.8, 3, True), (14, 13.6, 4, False), (-3, 7.0, 5, True), (6, 6.4, 6, False)):
        art.append(person3(C, X, s * X + 0.15, z, 60 + sd, flip=fl, bag=sd in (1, 6)))
    x, yb = C(-7.2, -7.2 * s + 0.15, 9.0)
    art.append(lamp(x, yb, C.f * 4.2 / 9.0, 18, "lantern", 2.0))
    return plate(U, "lisbon", art, 71, frame=(300, 248, 262, 210))



# ================================================================ PRAGUE
def saint(U, x, base, h, seed, kind=0, flip=False):
    """A blackened Baroque statue on its pedestal (h = total height px): moulded plinth with a panel, then a
    robed figure - with a cross, with a halo of stars, or a pair - lit only along one edge."""
    rnd = random.Random(seed)
    k = -1 if flip else 1
    out = []
    ph = h * 0.34
    pw = h * 0.15
    ped = [(x - pw, base), (x + pw, base), (x + pw, base - ph), (x - pw, base - ph)]
    cap = [(x - pw * 1.15, base - ph), (x + pw * 1.15, base - ph), (x + pw * 1.1, base - ph - h * 0.04), (x - pw * 1.1, base - ph - h * 0.04)]
    plinth = [(x - pw * 1.15, base), (x + pw * 1.15, base), (x + pw * 1.1, base - h * 0.05), (x - pw * 1.1, base - h * 0.05)]
    for q in (ped, cap, plinth):
        out.append(F(q, PAPER))
    out.append(tone(U, ped, 3, 80) + H(U, cap, 0, 1.4, 0.7) + H(U, plinth, 0, 1.4, 0.7))
    pan = [(x - pw * 0.6, base - ph * 0.25), (x + pw * 0.6, base - ph * 0.25), (x + pw * 0.6, base - ph * 0.8), (x - pw * 0.6, base - ph * 0.8)]
    out.append(F(pan, PAPER, 0.85) + H(U, pan, 0, 2.2, 0.6, op=0.5) + sketch(pan, 0.9, seed, 0.2))
    for q in (ped, cap, plinth):
        out.append(sketch(q, max(1.0, h * 0.008), seed, 0.4))
    # the figure
    fb = base - ph - h * 0.04
    fh = h - ph - h * 0.04
    w = fh * 0.34

    def robe(cx, sc, lean):
        return [(cx - w * 0.5 * sc, fb), (cx - w * 0.42 * sc + lean * 0.2, fb - fh * 0.35 * sc), (cx - w * 0.32 * sc + lean * 0.5, fb - fh * 0.62 * sc),
                (cx - w * 0.22 * sc + lean, fb - fh * 0.8 * sc), (cx + w * 0.22 * sc + lean, fb - fh * 0.82 * sc), (cx + w * 0.36 * sc + lean * 0.5, fb - fh * 0.6 * sc),
                (cx + w * 0.48 * sc + lean * 0.2, fb - fh * 0.3 * sc), (cx + w * 0.55 * sc, fb)]
    figs = [(x, 1.0, k * w * 0.15)] if kind != 2 else [(x - w * 0.32, 0.92, -w * 0.1), (x + w * 0.35, 1.0, w * 0.12)]
    for cx, sc, lean in figs:
        rb = robe(cx, sc, lean)
        rd = smooth_closed(rb)
        bx_ = (cx - w, fb - fh, cx + w, fb + 2)
        g_ = max(1.3, min(2.4, h * 0.011))
        if h < 70:
            out.append(F(rd, INK, 0.9))
        else:
            out.append(F(rd, PAPER) + H(U, rd, 80, g_, 0.8, box=bx_, wob=0.2, brk=0.1)
                       + H(U, rd, 20, g_ * 1.1, 0.8, box=bx_, span=(0.25, 1), dark=(cx + w, fb), wob=0.2, brk=0.1)
                       + H(U, rd, -40, g_ * 1.2, 0.8, box=bx_, span=(0.55, 1), dark=(cx + w, fb), wob=0.2, brk=0.1))
            folds = [((cx - w * 0.25 * sc + lean * 0.3 + i * w * 0.14, fb - fh * 0.04), (cx - w * 0.14 * sc + lean * 0.8 + i * w * 0.1, fb - fh * 0.66 * sc)) for i in range(4)]
            out.append(segs(folds, max(0.9, h * 0.006), seed, 0.8))
            out.append(P(rd, max(1.2, h * 0.009)))
        hx, hy = cx + lean, fb - fh * 0.9 * sc
        out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(w * 0.17 * sc)}" fill="{INK}" opacity="0.92"/>')
        if kind == 1:
            out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(w * 0.42)}" fill="none" stroke="{INK}" stroke-width="{max(0.8, h * 0.005):.2f}"/>')
            for i in range(5):
                a = -math.pi / 2 + (i - 2) * 0.5
                out.append(f'<circle cx="{f1(hx + math.cos(a) * w * 0.42)}" cy="{f1(hy + math.sin(a) * w * 0.42)}" r="{f1(max(0.9, w * 0.05))}" fill="{INK}"/>')
    if kind in (0, 1):
        cxx = x + k * w * 0.42
        out.append(nib([(cxx, fb - fh * 0.3), (cxx + k * w * 0.05, fb - fh * 1.08)], max(1.2, h * 0.012), taper=(1, 1), seed=seed, color=INK))
        out.append(seg(cxx - w * 0.2, fb - fh * 0.9, cxx + w * 0.2, fb - fh * 0.92, max(1.1, h * 0.011), seed, 0))
        out.append(P(f"M {f1(x + k * w * 0.1)} {f1(fb - fh * 0.62)} Q {f1(x + k * w * 0.3)} {f1(fb - fh * 0.6)} {f1(cxx)} {f1(fb - fh * 0.7)}", max(1.4, h * 0.016)))
    else:
        out.append(P(f"M {f1(x + w * 0.45)} {f1(fb - fh * 0.65)} Q {f1(x + w * 0.75)} {f1(fb - fh * 0.75)} {f1(x + w * 0.8)} {f1(fb - fh * 0.98)}", max(1.4, h * 0.016)))
    return "".join(out)


def bridge_tower_prague(U, x, base, top, w, seed):
    """The Lesser Town Bridge Tower: a tall square Gothic tower with a pointed gate arch, blind tracery, a gallery,
    and a steep slate tented roof with corner turrets and pinnacles; in shadow (the sun is behind it)."""
    out = []
    h = base - top
    rb = top + h * 0.42                   # roof base
    body = [(x - w / 2, rb), (x + w / 2, rb), (x + w / 2, base), (x - w / 2, base)]
    out.append(F(body, PAPER) + tone(U, body, 2, 78) + ST(U, body, 260, r=(0.4, 0.9), op=0.5))
    gate = arch_u(x - w * 0.22, x + w * 0.22, base - h * 0.27, base, 0.45, pointed=1.0)
    out.append(F(gate, INK, 0.9))
    for yy in (base - h * 0.34, rb + h * 0.05):
        out.append(seg(x - w / 2, yy, x + w / 2, yy, 1.2, seed, 0))
    for i in range(3):
        a_ = x - w * 0.36 + i * w * 0.27
        out.append(F(arch_u(a_, a_ + w * 0.18, rb + h * 0.1, rb + h * 0.24, 0.35, pointed=1.0), INK, 0.8))
    out.append(segs([((x - w * 0.42 + i * w * 0.12, base - h * 0.34), (x - w * 0.42 + i * w * 0.12, rb + h * 0.28)) for i in range(8)], 0.7, seed, 0, op=0.7))
    out.append(sketch(body, 1.6, seed, 0.4))
    # gallery / machicolation band
    gal = [(x - w * 0.56, rb), (x + w * 0.56, rb), (x + w * 0.56, rb + h * 0.035), (x - w * 0.56, rb + h * 0.035)]
    out.append(F(gal, PAPER) + segs([((x - w * 0.56 + i * w * 0.08, rb), (x - w * 0.56 + i * w * 0.08, rb + h * 0.035)) for i in range(15)], 0.8, seed, 0) + sketch(gal, 1.3, seed, 0.3))
    # tented roof with turrets
    roof = [(x - w * 0.5, rb), (x - w * 0.08, top + h * 0.03), (x + w * 0.08, top + h * 0.03), (x + w * 0.5, rb)]
    out.append(F(roof, PAPER) + tone(U, roof, 3, 90) + H(U, [(x, rb), (x, top), (x + w * 0.5, rb)], 60, 1.8, 0.7) + pen(roof, 1.6, seed, 0.05, True))
    for sgn in (-1, 1):
        tx = x + sgn * w * 0.5
        tur = [(tx - w * 0.07, rb), (tx, rb - h * 0.2), (tx + w * 0.07, rb)]
        out.append(F(tur, PAPER) + H(U, tur, 90, 1.3, 0.7) + pen(tur, 1.2, seed, 0.05, True) + seg(tx, rb - h * 0.2, tx, rb - h * 0.25, 1.1, seed, 0))
        mt = x + sgn * w * 0.25
        tur2 = [(mt - w * 0.04, rb - h * 0.08), (mt, rb - h * 0.2), (mt + w * 0.04, rb - h * 0.08)]
        out.append(F(tur2, PAPER) + pen(tur2, 1.0, seed, 0.05, True))
    out.append(seg(x, top + h * 0.03, x, top - h * 0.04, 1.4, seed, 0) + f'<circle cx="{f1(x)}" cy="{f1(top - h * 0.045)}" r="1.6" fill="{INK}"/>')
    return "".join(out)


def st_vitus(U, x, base, h, seed):
    """Prague Castle on the hill: the long palace front with rows of windows, St Vitus Cathedral's twin west
    spires and its great south tower with the bulbous Renaissance helmet."""
    out = []
    # palace wing
    pw = [(x - h * 1.5, base - h * 0.2), (x + h * 0.9, base - h * 0.22), (x + h * 0.9, base), (x - h * 1.5, base)]
    out.append(F(pw, PAPER) + facade(U, quad_sub(pw, 0.01, 0.15, 0.99, 0.9), 34, 3, "dark", seed, mx=0.3, my=0.25) + H(U, pw, 0, 2.6, 0.6, op=0.5) + sketch(pw, 1.2, seed, 0.3))
    rf = [(x - h * 1.52, base - h * 0.2), (x + h * 0.92, base - h * 0.22), (x + h * 0.88, base - h * 0.29), (x - h * 1.48, base - h * 0.27)]
    out.append(F(rf, PAPER) + H(U, rf, 0, 1.5, 0.7) + sketch(rf, 1.1, seed, 0.2))
    # nave of the cathedral behind
    nv = [(x - h * 0.55, base - h * 0.26), (x + h * 0.35, base - h * 0.26), (x + h * 0.3, base - h * 0.5), (x - h * 0.5, base - h * 0.5)]
    out.append(F(nv, PAPER) + H(U, nv, 90, 2.0, 0.6) + sketch(nv, 1.1, seed, 0.2))
    for i in range(7):
        bx = x - h * 0.5 + i * h * 0.13
        out.append(F([(bx - 2, base - h * 0.48), (bx, base - h * 0.6), (bx + 2, base - h * 0.48)], PAPER) + pen([(bx - 2, base - h * 0.48), (bx, base - h * 0.6), (bx + 2, base - h * 0.48)], 0.9, seed, 0.05))
    # twin west spires
    for sx in (-0.62, -0.46):
        cx = x + h * sx
        tw = [(cx - h * 0.05, base - h * 0.26), (cx + h * 0.05, base - h * 0.26), (cx + h * 0.05, base - h * 0.62), (cx - h * 0.05, base - h * 0.62)]
        out.append(F(tw, PAPER) + H(U, [(cx, base - h * 0.26), (cx + h * 0.05, base - h * 0.26), (cx + h * 0.05, base - h * 0.62), (cx, base - h * 0.62)], 90, 1.4, 0.7)
                   + F(arch_u(cx - h * 0.025, cx + h * 0.025, base - h * 0.58, base - h * 0.46, 0.35, pointed=1.0), INK, 0.8) + sketch(tw, 1.1, seed, 0.2))
        sp = [(cx - h * 0.055, base - h * 0.62), (cx, base - h * 0.98), (cx + h * 0.055, base - h * 0.62)]
        out.append(F(sp, PAPER) + H(U, [(cx, base - h * 0.62), (cx, base - h * 0.98), (cx + h * 0.055, base - h * 0.62)], 90, 1.3, 0.7) + pen(sp, 1.2, seed, 0.05, True))
        out.append(segs([((cx - h * 0.055 * (1 - t), base - h * (0.62 + 0.36 * t)), (cx - h * 0.055 * (1 - t) - 2, base - h * (0.62 + 0.36 * t) - 1.5)) for t in (0.2, 0.4, 0.6, 0.8)]
                        + [((cx + h * 0.055 * (1 - t), base - h * (0.62 + 0.36 * t)), (cx + h * 0.055 * (1 - t) + 2, base - h * (0.62 + 0.36 * t) - 1.5)) for t in (0.2, 0.4, 0.6, 0.8)], 0.8, seed, 0))
    # the great south tower with its helmet
    cx = x + h * 0.08
    tw = [(cx - h * 0.08, base - h * 0.26), (cx + h * 0.08, base - h * 0.26), (cx + h * 0.08, base - h * 0.7), (cx - h * 0.08, base - h * 0.7)]
    out.append(F(tw, PAPER) + H(U, [(cx + h * 0.01, base - h * 0.26), (cx + h * 0.08, base - h * 0.26), (cx + h * 0.08, base - h * 0.7), (cx + h * 0.01, base - h * 0.7)], 90, 1.4, 0.7)
               + F(arch_u(cx - h * 0.045, cx + h * 0.045, base - h * 0.66, base - h * 0.48, 0.35, pointed=1.0), INK, 0.85) + sketch(tw, 1.2, seed, 0.2))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(base - h * 0.4)}" r="{f1(h * 0.04)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    helm = [(cx - h * 0.085, base - h * 0.7), (cx - h * 0.1, base - h * 0.76), (cx - h * 0.05, base - h * 0.82), (cx - h * 0.065, base - h * 0.86), (cx, base - h * 0.95),
            (cx + h * 0.065, base - h * 0.86), (cx + h * 0.05, base - h * 0.82), (cx + h * 0.1, base - h * 0.76), (cx + h * 0.085, base - h * 0.7)]
    out.append(F(smooth_closed(helm), PAPER) + H(U, helm, 90, 1.4, 0.7, span=(0.5, 1), dark=(cx + h, base - h * 0.8)) + P(smooth_closed(helm), 1.3))
    out.append(seg(cx, base - h * 0.95, cx, base - h * 1.02, 1.3, seed, 0))
    return "".join(out)


def dome_church(U, x, base, h, seed):
    """St Nicholas in the Lesser Town: a great green-copper dome on a drum with a lantern, and its belfry beside."""
    out = []
    dr = [(x - h * 0.22, base - h * 0.35), (x + h * 0.22, base - h * 0.35), (x + h * 0.22, base), (x - h * 0.22, base)]
    out.append(F(dr, PAPER) + segs([((x + u * h * 0.22, base - h * 0.05), (x + u * h * 0.22, base - h * 0.3)) for u in (-0.6, -0.2, 0.2, 0.6)], 1.0, seed, 0)
               + H(U, [(x, base - h * 0.35), (x + h * 0.22, base - h * 0.35), (x + h * 0.22, base), (x, base)], 90, 1.5, 0.7) + sketch(dr, 1.2, seed, 0.3))
    dome = [(x - h * 0.26, base - h * 0.35)] + [(x - h * 0.26 * math.cos(t), base - h * 0.35 - h * 0.34 * math.sin(t)) for t in [i * math.pi / 14 for i in range(1, 14)]] + [(x + h * 0.26, base - h * 0.35)]
    out.append(F(dome, PAPER) + H(U, dome, 90, 1.5, 0.7, span=(0.5, 1), dark=(x + h, base - h * 0.5))
               + segs([((x + u * h * 0.26, base - h * 0.35), (x + u * h * 0.08, base - h * 0.66)) for u in (-0.7, -0.35, 0, 0.35, 0.7)], 0.7, seed, 0) + pen(dome, 1.4, seed, 0.05))
    ln = [(x - h * 0.05, base - h * 0.68), (x + h * 0.05, base - h * 0.68), (x + h * 0.05, base - h * 0.8), (x - h * 0.05, base - h * 0.8)]
    out.append(F(ln, PAPER) + sketch(ln, 1.0, seed, 0.2) + F([(x - h * 0.06, base - h * 0.8), (x, base - h * 0.9), (x + h * 0.06, base - h * 0.8)], INK, 0.85)
               + seg(x, base - h * 0.9, x, base - h * 0.97, 1.2, seed, 0))
    bx = x + h * 0.48
    bt = [(bx - h * 0.09, base - h * 0.62), (bx + h * 0.09, base - h * 0.62), (bx + h * 0.09, base + h * 0.1), (bx - h * 0.09, base + h * 0.1)]
    out.append(F(bt, PAPER) + H(U, [(bx, base - h * 0.62), (bx + h * 0.09, base - h * 0.62), (bx + h * 0.09, base + h * 0.1), (bx, base + h * 0.1)], 90, 1.4, 0.7)
               + F(arch_u(bx - h * 0.04, bx + h * 0.04, base - h * 0.55, base - h * 0.38, 0.4), INK, 0.85) + sketch(bt, 1.2, seed, 0.3))
    bh = [(bx - h * 0.1, base - h * 0.62), (bx - h * 0.06, base - h * 0.72), (bx, base - h * 0.85), (bx + h * 0.06, base - h * 0.72), (bx + h * 0.1, base - h * 0.62)]
    out.append(F(smooth_closed(bh), PAPER) + H(U, bh, 90, 1.3, 0.7, span=(0.5, 1), dark=(bx + h, base - h)) + P(smooth_closed(bh), 1.2) + seg(bx, base - h * 0.85, bx, base - h * 0.92, 1.1, seed, 0))
    return "".join(out)


def roofs_row(U, x0, x1, base, seed, hmin=18, hmax=34):
    """A huddle of old red-tiled roofs and gables (pale, middle distance)."""
    rnd = random.Random(seed)
    out = []
    x = x0
    while x < x1:
        w = rnd.uniform(22, 40)
        h = rnd.uniform(hmin, hmax)
        wall = [(x, base - h), (x + w, base - h), (x + w, base), (x, base)]
        out.append(F(wall, PAPER) + facade(U, quad_sub(wall, 0.08, 0.2, 0.92, 0.9), max(2, int(w / 8)), 2, "pane", seed + int(x), dark_p=0.4, w=0.6) + sketch(wall, 1.0, seed, 0.3))
        rh = rnd.uniform(10, 18)
        if rnd.random() < 0.5:
            rf = [(x - 2, base - h), (x + w * 0.5, base - h - rh * 1.3), (x + w + 2, base - h)]
        else:
            rf = [(x - 2, base - h), (x + 4, base - h - rh), (x + w - 4, base - h - rh), (x + w + 2, base - h)]
        out.append(F(rf, PAPER) + H(U, rf, 0, 1.8, 0.7, op=0.8) + pen(rf, 1.1, seed, 0.1, True))
        if rnd.random() < 0.5:
            cx = x + w * rnd.uniform(0.2, 0.8)
            out.append(F([(cx - 2, base - h - rh * 0.6), (cx + 2, base - h - rh * 0.6), (cx + 2, base - h - rh * 1.1), (cx - 2, base - h - rh * 1.1)], INK, 0.8))
        x += w * rnd.uniform(0.8, 1.0)
    return "".join(out)


@design("prague")
def prague(U):
    """On the Charles Bridge toward the Lesser Town in the late sun: the blackened Baroque saints on their
    pedestals marching along both parapets (one huge beside us), lanterns between them, the cobbled deck and the
    crowd narrowing to the Gothic bridge tower and its gate, St Nicholas's dome, and the Castle with St Vitus's
    spires on the hill above. The accent: a painter's red umbrella."""
    C = Cam(f=520, cx=318, vpy=338, eye=1.65)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 170, 96, 140, 22, 4) + cloud(U, 470, 82, 100, 14, 5))
    art.append(gulls([(250, 132, 7), (268, 120, 5), (520, 150, 5)], 6))
    # the castle hill
    hill = [(30, 266), (150, 236), (300, 214), (440, 200), (600, 196), (600, 340), (30, 340)]
    art.append(F(hill, PAPER) + H(U, hill, 0, 3.0, 0.6, op=0.45))
    for i in range(16):
        x = 60 + i * 34
        art.append(lobe(U, x, 250 - i * 3 + (i % 3) * 6, 18, 11, 100 + i, w=1.1, dense=1.1))
    art.append(st_vitus(U, 470, 214, 150, 7))
    art.append(roofs_row(U, 40, 600, 300, 8))
    art.append(dome_church(U, 196, 268, 112, 9))
    art.append(roofs_row(U, 60, 600, 326, 10, 14, 26))
    # the bridge tower + the lower Judith tower and the gate between
    TZ = 125.0
    tx, tb = C(0, 0, TZ)
    s = C.f / TZ
    jt = [(tx - 13 * s, tb - 24 * s), (tx - 4 * s, tb - 24 * s), (tx - 4 * s, tb), (tx - 13 * s, tb)]
    art.append(F(jt, PAPER) + tone(U, jt, 2, 78) + sketch(jt, 1.3, 11, 0.4))
    jr = [(tx - 13.6 * s, tb - 24 * s), (tx - 8.5 * s, tb - 31 * s), (tx - 3.4 * s, tb - 24 * s)]
    art.append(F(jr, PAPER) + tone(U, jr, 3, 90) + pen(jr, 1.2, 12, 0.05, True))
    art.append(bridge_tower_prague(U, tx + 4 * s, tb, tb - 43 * s, 11 * s, 13))
    # the bridge deck: setts, kerbs, the far crowd
    road = [C(-4.8, 0, 3), C(-4.8, 0, TZ), C(4.8, 0, TZ), C(4.8, 0, 3)]
    art.append(F(road, PAPER) + clipped(U("rd"), poly(road), cobbles(U, C, -4.8, 4.8, 3, TZ, 14, row=0.35, stone=0.5, w=0.6, op=0.6)))
    art.append(tone(U, [C(-4.8, 0, 3), C(-4.8, 0, TZ), C(-3.6, 0, TZ), C(-2.6, 0, 3)], 2, 70))
    rr = random.Random(15)
    crowd = []
    for i in range(26):
        z = 30 * ((TZ - 4) / 30) ** rr.random()
        X = rr.uniform(-4.2, 4.2)
        crowd.append((z, X, i))
    crowd.sort(reverse=True)
    # parapets with their statues and lamps, far to near, people interleaved by depth
    items = []
    for i, z in enumerate((112, 96, 81, 67, 55, 44, 34, 25)):
        items.append((z, "statue", -5.4, i))
        items.append((z + 6, "statue", 5.4, i + 20))
        items.append((z + 3.5, "lamp", -5.3, i))
        items.append((z - 3.0, "lamp", 5.3, i))
    items.append((14.5, "statue", -5.4, 99))
    for z, X, i in crowd:
        items.append((z, "person", X, i))
    items.sort(key=lambda t: -t[0])
    par_l = [C(-5.0, 1.05, 3), C(-5.0, 1.05, TZ), C(-5.0, 0, TZ), C(-5.0, 0, 3)]
    par_r = [C(5.0, 1.05, 3), C(5.0, 1.05, TZ), C(5.0, 0, TZ), C(5.0, 0, 3)]
    art.append(F(par_r, PAPER) + tone(U, par_r, 2, 80) + pen([par_r[0], par_r[1]], 1.6, 16, 0.05))
    art.append(F(par_l, PAPER) + H(U, par_l, 0, 2.6, 0.6, op=0.6) + pen([par_l[0], par_l[1]], 1.8, 17, 0.05))
    for z, kind, X, i in items:
        x, yb = C(X, 1.05 if kind != "person" else 0, z)
        sc = C.f / z
        if kind == "statue":
            art.append(saint(U, x, yb, 6.2 * sc, 200 + i, kind=i % 3, flip=X > 0))
        elif kind == "lamp":
            art.append(lamp(x, yb, 4.2 * sc, 300 + i, "lantern", max(1.0, min(2.4, sc * 0.05))))
        else:
            art.append(person(x, yb, 1.72 * sc, 400 + i, flip=bool(i % 2), bag=i % 5 == 0))
    # a painter at his easel under a red umbrella (the accent), near the right parapet
    px, py = C(3.6, 0, 22)
    sc = C.f / 22
    um = [(px - 1.3 * sc, py - 2.2 * sc), (px - 0.6 * sc, py - 2.65 * sc), (px, py - 2.75 * sc), (px + 0.6 * sc, py - 2.65 * sc), (px + 1.3 * sc, py - 2.2 * sc)]
    ud = smooth_open(um) + f" L {f1(um[-1][0])} {f1(um[-1][1])} Q {f1(px)} {f1(py - 2.05 * sc)} {f1(um[0][0])} {f1(um[0][1])} Z"
    art.append(F(ud, PAPER) + accent(U, ud, bbox(um, 6), 17, op=0.95, ang=-20, n=14, length=(6, 14), width=(1.4, 2.6)) + P(ud, 1.3))
    art.append(seg(px, py - 2.7 * sc, px, py, 1.4, 18, 0))
    ez = [(px - 0.9 * sc, py), (px - 0.6 * sc, py - 1.5 * sc), (px - 0.3 * sc, py)]
    art.append(pen(ez, 1.2, 19, 0.05) + F([(px - 1.0 * sc, py - 1.0 * sc), (px - 0.25 * sc, py - 1.0 * sc), (px - 0.25 * sc, py - 1.55 * sc), (px - 1.0 * sc, py - 1.55 * sc)], PAPER)
               + sketch([(px - 1.0 * sc, py - 1.0 * sc), (px - 0.25 * sc, py - 1.0 * sc), (px - 0.25 * sc, py - 1.55 * sc), (px - 1.0 * sc, py - 1.55 * sc)], 1.1, 20, 0.2))
    art.append(person(px + 0.4 * sc, py, 1.6 * sc, 21, flip=True))
    # nearer walkers and a dog
    for X, z, sd, fl in ((-1.6, 24, 1, False), (-1.0, 24.5, 2, False), (1.6, 29, 3, True)):
        art.append(person3(C, X, 0, z, 500 + sd, flip=fl, bag=sd == 3))
    dx, dy = C(-0.4, 0, 23.0)
    ds = C.f / 23.0
    art.append(F(smooth_closed([(dx, dy - 0.25 * ds), (dx + 0.55 * ds, dy - 0.3 * ds), (dx + 0.62 * ds, dy - 0.5 * ds), (dx + 0.7 * ds, dy - 0.42 * ds),
                                (dx + 0.6 * ds, dy - 0.22 * ds), (dx + 0.1 * ds, dy - 0.15 * ds)]), INK, 0.92)
               + segs([((dx + 0.08 * ds, dy - 0.2 * ds), (dx + 0.05 * ds, dy)), ((dx + 0.5 * ds, dy - 0.25 * ds), (dx + 0.52 * ds, dy))], 1.4, 22, 0)
               + P(f"M {f1(dx)} {f1(dy - 0.25 * ds)} q {f1(-0.15 * ds)} {f1(-0.1 * ds)} {f1(-0.2 * ds)} {f1(-0.25 * ds)}", 1.2))
    # the parapet's stone courses and the statues' shadows on the deck
    art.append(clipped(U("pl"), poly(par_l), segs([(C(-5.0, 0.0, z), C(-5.0, 1.05, z)) for z in [3 * 1.12 ** k for k in range(40) if 3 * 1.12 ** k < TZ]], 0.7, 23, 0)))
    return plate(U, "prague", art, 81, frame=(300, 246, 262, 212))


# ================================================================ VENICE
def palazzo_x(U, C, X, Z0, Z1, Y0, Y1, seed, gl, style="renaissance", lvl=0, floors=3, bay=3.4, base_h=3.2):
    """A Venetian palace wall rising straight out of the water in the plane X: a rusticated water storey stained
    by the tide, water gates, then floors of round-arched (renaissance), ogee (gothic) or barred square (rustic)
    windows between string courses, a cornice; light from the left."""
    rnd = random.Random(seed)
    m = Wm(C, (X, Z0), (X, Z1), Y0, Y1)
    q = Q(m, 0, 0, 1, 1)
    out = [F(q, PAPER)]
    L = Z1 - Z0
    hh = Y1 - Y0
    nb = max(1, int(L / bay))

    def v(Y):
        return 1 - (Y - Y0) / hh
    # rustication courses on the water storey (and all over for 'rustic')
    top_r = Y1 if style == "rustic" else Y0 + base_h
    rus = []
    Y = Y0 + 0.5
    k = 0
    while Y < top_r:
        rus.append(((0, v(Y)), (1, v(Y))))
        z = rnd.uniform(0, 1.2)
        while z < L:
            rus.append(((z / L, v(Y)), (z / L, v(min(top_r, Y + 0.55)))))
            z += rnd.uniform(1.1, 1.6) if style == "rustic" else rnd.uniform(1.4, 2.2)
        Y += 0.55
        k += 1
    out.append(rules_u(m, rus, 0.55, seed, op=0.65))
    # water stain band + water gates
    stain = Q(m, 0, v(Y0 + 1.1), 1, 1)
    out.append(H(U, stain, 80, 1.6, 0.7, op=0.8))
    gates = []
    for i in range(nb):
        if i % 3 == 1:
            uc = (i + 0.5) / nb
            gates.append(arch_u(uc - 0.35 / nb, uc + 0.35 / nb, v(Y0 + 2.8), 1.0, 0.35))
    if gates:
        out.append(windows(m, gates, INK, op=0.88, stroke=1.0))
    # floors
    fh = (hh - base_h - 1.2) / floors
    shapes, bars = [], []
    for j in range(floors):
        yb = Y0 + base_h + 0.4 + j * fh
        yt = yb + fh * 0.66
        for i in range(nb):
            uc = (i + 0.5) / nb
            ww = 0.36 / nb
            if style == "renaissance":
                for k2 in (-1, 1):
                    a_ = uc + k2 * ww * 0.55 - ww * 0.4
                    shapes.append(arch_u(a_, a_ + ww * 0.8, v(yt), v(yb), 0.3))
                bars.append(((uc - ww * 1.3, v(yb) + 0.004), (uc + ww * 1.3, v(yb) + 0.004)))
            elif style == "gothic":
                shapes.append(ogee_u(uc - ww * 0.55, uc + ww * 0.55, v(yt), v(yb), 0.4))
                bars.append(((uc - ww * 0.7, v(yb) + 0.004), (uc + ww * 0.7, v(yb) + 0.004)))
            else:
                ys = yb + fh * 0.12
                shapes.append([(uc - ww * 0.45, v(ys + fh * 0.4)), (uc + ww * 0.45, v(ys + fh * 0.4)), (uc + ww * 0.45, v(ys)), (uc - ww * 0.45, v(ys))])
                for f_ in (0.25, 0.5, 0.75):
                    bars.append(((uc - ww * 0.45 + ww * 0.9 * f_, v(ys + fh * 0.4)), (uc - ww * 0.45 + ww * 0.9 * f_, v(ys))))
                bars.append(((uc - ww * 0.45, v(ys + fh * 0.2)), (uc + ww * 0.45, v(ys + fh * 0.2))))
        out.append(rules_u(m, [((0, v(yb - 0.25)), (1, v(yb - 0.25))), ((0, v(yb - 0.5)), (1, v(yb - 0.5)))], 0.9, seed + j))
    out.append(windows(m, shapes, gl if style != "rustic" else INK, op=1.0 if style != "rustic" else 0.86, stroke=0.8))
    out.append(rules_u(m, bars, 1.0 if style == "rustic" else 0.9, seed + 7, color=PAPER if style == "rustic" else INK))
    if style == "renaissance":
        out.append(rules_u(m, [((i / nb, v(Y0 + base_h)), (i / nb, 0.02)) for i in range(1, nb)], 0.8, seed + 8, op=0.8))
    out.append(ST(U, poly(q), int(L * 14), r=(0.35, 0.85), op=0.45))
    out.append(tone(U, q, lvl, 78))
    cor = [m(0, 0), m(1, 0), m(1, 0.03), m(0, 0.03)]
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.2, 0.7) + pen([m(0, 0), m(1, 0)], 1.8, seed, 0.05))
    out.append(pen([m(0, 0), m(0, 1)], 1.8, seed + 1, 0.05) + pen([m(0, 1), m(1, 1)], 1.4, seed + 2, 0.05))
    return "".join(out)


def bridge_of_sighs(U, C, Z, X0, X1, Y0, seed):
    """The enclosed Baroque bridge between the palace and the prisons: a segmental arch under a stone box with two
    small windows behind stone grilles, rusticated sides, volutes and a curved crown with a carved mask; light from
    the left, its soffit seen from below."""
    out = []
    Yt = Y0 + 6.2
    m = Wm(C, (X0, Z), (X1, Z), Y0 - 2.2, Yt)
    face = Q(m, 0, 0, 1, 1)
    # the arch cut out of the face (sky/canal seen beneath)
    hh = Yt - (Y0 - 2.2)

    def v(Y):
        return 1 - (Y - (Y0 - 2.2)) / hh
    arc = [m(0, 1)] + [m(t / 16, v(Y0 - 2.2 + 2.3 * math.sin(math.pi * t / 16) ** 0.6)) for t in range(1, 16)] + [m(1, 1)]
    body = face[:2] + [m(1, 1)] + arc[::-1][1:-1] + [m(0, 1)]
    out.append(F(body, PAPER) + ST(U, poly(body), 300, r=(0.35, 0.8), op=0.5))
    # soffit seen from below, deep shade
    sof = arc + [C(X1, Y0 - 2.2, Z + 4.0)] + [C(lerp(X1, X0, t / 16), Y0 - 2.2 + 2.3 * math.sin(math.pi * (16 - t) / 16) ** 0.6, Z + 4.0) for t in range(1, 16)] + [C(X0, Y0 - 2.2, Z + 4.0)]
    out.append(F(sof, PAPER) + tone(U, sof, 4, 10))
    out.append(pen(arc, 1.8, seed, 0.05, smooth=True))
    # rusticated pilasters at the sides
    for a_, b_ in ((0.0, 0.14), (0.86, 1.0)):
        pq = Q(m, a_, 0.08, b_, v(Y0 - 0.2))
        out.append(F(pq, PAPER) + rules_u(homog(pq), [((0, j / 8), (1, j / 8)) for j in range(1, 8)], 0.7, seed) + sketch(pq, 1.2, seed, 0.2))
        out.append(H(U, pq, 90, 2.0, 0.6, op=0.5 if a_ == 0 else 0.8))
    # two windows with stone grilles
    for a_ in (0.24, 0.58):
        wq = Q(m, a_, v(Yt - 1.6), a_ + 0.18, v(Y0 + 1.0))
        out.append(F(wq, INK, 0.88))
        wm = homog(wq)
        gr = []
        for t in (0.2, 0.4, 0.6, 0.8):
            gr.append((wm(t, 0), wm(t, 1)))
            gr.append((wm(0, t), wm(1, t)))
        out.append(segs(gr, 1.3, seed, 0, color=PAPER) + sketch(wq, 1.4, seed + 1, 0.2))
        fr = Q(m, a_ - 0.025, v(Yt - 1.6) - 0.03, a_ + 0.205, v(Y0 + 1.0) + 0.02)
        out.append(pen(fr, 1.0, seed + 2, 0.05, True))
    # cornice + curved crown with volutes and the mask
    out.append(pen([m(-0.02, v(Yt - 1.0)), m(1.02, v(Yt - 1.0))], 1.6, seed, 0.05) + pen([m(-0.02, v(Yt - 1.25)), m(1.02, v(Yt - 1.25))], 0.9, seed, 0.05))
    crown = [m(0.04, v(Yt - 1.0))] + [m(0.04 + 0.92 * t / 14, v(Yt - 1.0 + 1.6 * math.sin(math.pi * t / 14))) for t in range(1, 14)] + [m(0.96, v(Yt - 1.0))]
    out.append(F(crown, PAPER) + H(U, crown, 0, 1.5, 0.6, span=(0.0, 0.35), dark=crown[0]) + pen(crown, 1.6, seed, 0.05, smooth=True))
    for u in (0.08, 0.92):
        cx_, cy_ = m(u, v(Yt - 0.75))
        r = abs(m(0.05, 0)[0] - m(0, 0)[0]) * 0.9 + 1.5
        out.append(P(f"M {f1(cx_ - r)} {f1(cy_)} a {f1(r)} {f1(r)} 0 1 1 {f1(r)} {f1(r)}", 1.3))
    mx_, my_ = m(0.5, v(Yt - 0.35))
    r = abs(m(0.06, 0)[0] - m(0, 0)[0]) + 2
    out.append(f'<circle cx="{f1(mx_)}" cy="{f1(my_)}" r="{f1(r)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>'
               + f'<circle cx="{f1(mx_ - r * 0.35)}" cy="{f1(my_ - r * 0.1)}" r="{f1(r * 0.15)}" fill="{INK}"/><circle cx="{f1(mx_ + r * 0.35)}" cy="{f1(my_ - r * 0.1)}" r="{f1(r * 0.15)}" fill="{INK}"/>')
    out.append(sketch(face[:2] + [m(1, 1), m(0, 1)], 1.8, seed + 3, 0.6, closed=False))
    return "".join(out)


def gondola3(U, C, Xc, Z0, L, seed, passengers=2, skew=-0.15):
    """A gondola seen from above and behind, sliding away from us: the long black lacquered hull rising at both
    ends, the ferro on the prow, a cushioned seat with passengers, the gondolier standing at the stern with his
    oar in the forcola."""
    out = []

    def pts(side):
        res = []
        for i in range(13):
            t = i / 12
            w = 0.7 * math.sin(math.pi * min(1, max(0, t * 1.04 - 0.02))) ** 0.7
            y = 0.35 + 0.75 * (2 * t - 1) ** 4
            res.append(C(Xc + side * w + skew * t, y, Z0 + t * L))
        return res
    lft, rgt = pts(-1), pts(1)
    hull = lft + rgt[::-1]
    out.append(F(hull, INK, 0.92))
    out.append(pen(lft, 1.2, seed, 0.05, smooth=True, color=PAPER, op=0.7) if False else P(smooth_open(lft[2:10]), 0.9, PAPER, 0.6))
    # inside: the deck / seats (paper) between the gunwales in the middle third
    inner = [pt(lft[i], rgt[i], 0.18) for i in range(4, 10)] + [pt(lft[i], rgt[i], 0.82) for i in range(9, 3, -1)]
    out.append(F(inner, PAPER, 0.9) + H(U, inner, 0, 1.5, 0.6, op=0.6))
    cu = [pt(lft[6], rgt[6], 0.2), pt(lft[6], rgt[6], 0.8), pt(lft[7], rgt[7], 0.8), pt(lft[7], rgt[7], 0.2)]
    out.append(F(cu, PAPER) + accent(U, poly(cu), bbox(cu), seed, op=0.9, ang=0, n=8, length=(4, 10), width=(1.2, 2.2)) + sketch(cu, 1.0, seed, 0.2))
    # prow ferro
    tip = rgt[-1]
    s = C.f / (Z0 + L)
    fer = [(tip[0], tip[1]), (tip[0] + 0.1 * s, tip[1] - 1.1 * s), (tip[0] + 0.45 * s, tip[1] - 1.25 * s), (tip[0] + 0.35 * s, tip[1] - 0.2 * s)]
    out.append(F(fer, INK, 0.92) + segs([((tip[0] + 0.12 * s, tip[1] - (0.3 + 0.18 * k) * s), (tip[0] + 0.42 * s, tip[1] - (0.3 + 0.18 * k) * s)) for k in range(5)], 0.8, seed, 0, color=PAPER))
    # passengers seated
    for k in range(passengers):
        px, py = pt(lft[7 - k], rgt[7 - k], 0.35 + 0.3 * k)
        ss = C.f / (Z0 + L * (7 - k) / 12)
        out.append(F(smooth_closed([(px - 0.28 * ss, py), (px + 0.28 * ss, py), (px + 0.22 * ss, py - 0.7 * ss), (px - 0.22 * ss, py - 0.7 * ss)]), INK, 0.95)
                   + f'<circle cx="{f1(px)}" cy="{f1(py - 0.85 * ss)}" r="{f1(0.15 * ss)}" fill="{INK}"/>')
    # the gondolier on the stern deck, rowing
    gx, gy = pt(lft[1], rgt[1], 0.65)
    gs = C.f / (Z0 + L * 0.08)
    out.append(person(gx, gy, 1.8 * gs, seed + 3, flip=True))
    hat = [(gx - 0.2 * gs, gy - 1.7 * gs), (gx + 0.2 * gs, gy - 1.7 * gs)]
    out.append(seg(*hat[0], *hat[1], max(1.2, gs * 0.06), seed, 0))
    for k in range(3):
        y_ = gy - (1.05 + k * 0.12) * gs
        out.append(seg(gx - 0.11 * gs, y_, gx + 0.11 * gs, y_, max(0.8, gs * 0.03), seed + k, 0, color=PAPER))
    ox0 = (gx + 0.15 * gs, gy - 1.2 * gs)
    oe = C(Xc + 1.6 + skew * 0.3, 0.0, Z0 + L * 0.3)
    out.append(nib([ox0, oe], max(1.2, gs * 0.05), taper=(1, 0.8), seed=seed, color=INK))
    out.append(P(f"M {f1(oe[0] - 6)} {f1(oe[1] + 1)} q 6 3 12 0", 1.0, INK, 0.8))
    wk = C(Xc, 0, Z0 - 0.4)
    out.append(P(f"M {f1(wk[0] - 18)} {f1(wk[1] + 6)} Q {f1(wk[0])} {f1(wk[1] - 2)} {f1(wk[0] + 18)} {f1(wk[1] + 6)} M {f1(wk[0] - 30)} {f1(wk[1] + 16)} Q {f1(wk[0])} {f1(wk[1] + 4)} {f1(wk[0] + 30)} {f1(wk[1] + 16)}", 1.1, INK, 0.75))
    return "".join(out)


def paline(U, C, X, Z, Y1, seed, stripes=True):
    """A Venetian mooring pole, its upper part spiral-striped (vermilion) under a gilded knob."""
    out = []
    x0, y0 = C(X, 0, Z)
    x1, y1 = C(X, Y1, Z)
    w = max(2.0, C.f * 0.11 / Z)
    q = [(x0 - w, y0), (x1 - w, y1), (x1 + w, y1), (x0 + w, y0)]
    out.append(F(q, PAPER))
    if stripes:
        sd = []
        n = 7
        for k in range(n):
            ya = lerp(y1, lerp(y1, y0, 0.55), k / n)
            yb_ = lerp(y1, lerp(y1, y0, 0.55), (k + 0.5) / n)
            sd.append(poly([(x1 - w, ya), (x1 + w, ya - w * 0.8), (x1 + w, yb_ - w * 0.8), (x1 - w, yb_)]))
        d = " ".join(sd)
        out.append(accent(U, d, (x1 - w * 2, y1 - w * 2, x1 + w * 2, lerp(y1, y0, 0.6)), seed, op=0.95, ang=-30, n=10, length=(4, 10), width=(1.2, 2.4)))
        out.append(H(U, d, -30, 1.8, 0.6, box=(x1 - w * 2, y1 - w * 2, x1 + w * 2, lerp(y1, y0, 0.6)), op=0.5))
    out.append(H(U, [(x0, y0), (x1, y1), (x1 + w, y1), (x0 + w, y0)], 90, 1.4, 0.7))
    out.append(pen([q[0], q[1]], 1.3, seed, 0.05) + pen([q[2], q[3]], 1.8, seed + 1, 0.05))
    out.append(f'<circle cx="{f1(x1)}" cy="{f1(y1 - w * 0.6)}" r="{f1(w * 1.2)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>')
    return "".join(out)


@design("venice")
def venice(U):
    """From the Ponte della Paglia, looking up the Rio di Palazzo: the Doge's Palace's carved flank on the left in
    the light, the rusticated prisons in shadow on the right, the Bridge of Sighs spanning between them, a gondola
    sliding beneath with its gondolier, striped mooring poles (the accent) at our feet."""
    C = Cam(f=360, cx=300, vpy=300, eye=4.4)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 300, 78, 100, 16, 4) + cloud(U, 372, 116, 56, 9, 5))
    art.append(gulls([(272, 140, 6), (288, 130, 4), (330, 160, 5)], 6))
    BZ = 23.0
    # the far end of the rio: the next bridge, a far palazzo across the end
    far = C.qz(110, -4.5, 4.5, 0, 16)
    art.append(F(far, PAPER) + facade(U, quad_sub(far, 0.05, 0.1, 0.95, 0.85), 4, 4, "pane", 7, dark_p=0.3, w=0.6) + H(U, far, 0, 2.4, 0.6, op=0.5) + sketch(far, 1.1, 8, 0.3))
    br = [C(-4.2, 0.0, 70), C(-4.2, 2.6, 70)] + [C(-4.2 + 8.4 * t / 10, 2.6 + 0.9 * math.sin(math.pi * t / 10), 70) for t in range(1, 10)] + [C(4.2, 2.6, 70), C(4.2, 0, 70)]
    art.append(F(br, PAPER) + H(U, br, 0, 1.6, 0.6, op=0.6) + pen(br, 1.2, 9, 0.05))
    # the canal walls: palace (left, lit) and prisons (right, shade), far to near
    art.append(palazzo_x(U, C, 4.3, BZ + 3, 110, 0, 13, 10, gl, "rustic", lvl=3, floors=3))
    art.append(palazzo_x(U, C, -4.3, BZ + 3, 110, 0, 22, 11, gl, "gothic", lvl=1, floors=3))
    art.append(bridge_of_sighs(U, C, BZ, -4.3, 4.3, 6.0, 12))
    art.append(palazzo_x(U, C, 4.3, 3, BZ, 0, 14, 13, gl, "rustic", lvl=3, floors=3))
    art.append(palazzo_x(U, C, -4.3, 3, BZ, 0, 24, 14, gl, "renaissance", lvl=0, floors=3, bay=3.0))
    # the water
    water = [C(-4.3, 0, 11), C(-4.3, 0, 110), C(4.3, 0, 110), C(4.3, 0, 11)]
    art.append(ripples(U, 120, 480, C(0, 0, 110)[1], 470, 15, dens=0.9, gap=(1.5, 7.0), ln=((3, 8), (9, 24)), w=(0.75, 1.25),
                       refl=[(120, C(-4.3, 0, 40)[0] + 10, 0.35), (C(4.3, 0, 40)[0] - 10, 480, 0.7)], skip=[(290, 312)], clip=poly(water)))
    art.append(gondola3(U, C, -1.6, 12.5, 11.0, 15, skew=2.4))
    # moored poles at the mouth of the rio
    for X, Z, Y1, sd in ((3.5, 13.5, 6.2, 17), (2.8, 15.5, 5.8, 18)):
        art.append(paline(U, C, X, Z, Y1, sd))
    # a lamp bracket on the palace corner and the edge of our bridge's parapet
    return plate(U, "venice", art, 91, frame=(300, 248, 262, 210))


# ================================================================ AMSTERDAM
def gable_pts(kind, G):
    """Gable outline above the eaves in (u, dy): u 0..1 across the house front, dy metres above the eaves line.
    Runs from (0, 0) to (1, 0)."""
    if kind == "step":
        n = 4
        L = [(0, 0)]
        for i in range(n):
            u = 0.1 * i
            L += [(u, G * (i + 0.8) / (n + 0.8)), (u + 0.1, G * (i + 0.8) / (n + 0.8))]
        L += [(0.4, G), (0.6, G)]
        R = [(1 - u, dy) for u, dy in L[::-1]][2:]
        return L + R
    if kind == "neck":
        L = [(0, 0), (0.02, G * 0.12), (0.1, G * 0.16), (0.2, G * 0.26), (0.24, G * 0.4), (0.25, G * 0.78), (0.21, G * 0.78),
             (0.5, G)]
        return L + [(1 - u, dy) for u, dy in L[::-1]][1:]
    if kind == "bell":
        L = [(0, 0), (0.06, G * 0.08), (0.17, G * 0.22), (0.21, G * 0.42), (0.23, G * 0.62), (0.3, G * 0.82), (0.4, G * 0.94),
             (0.5, G)]
        return L + [(1 - u, dy) for u, dy in L[::-1]][1:]
    if kind == "spout":
        L = [(0, 0), (0.08, G * 0.1), (0.36, G * 0.78), (0.4, G * 0.78), (0.4, G), (0.6, G), (0.6, G * 0.78), (0.64, G * 0.78),
             (0.92, G * 0.1), (1, 0)]
        return L
    # cornice house: flat top with a small crest
    return [(0, 0), (-0.03, 0.4), (-0.03, 0.8), (0.32, 0.8), (0.4, G * 0.75), (0.5, G), (0.6, G * 0.75), (0.68, 0.8),
            (1.03, 0.8), (1.03, 0.4), (1, 0)]


def canal_house(U, C, X, Z0, Z1, Yb, Ht, kind, seed, gl, lvl=0, brick=True, bays=3, G=None):
    """An Amsterdam canal house front in the plane X: tall sash windows with white frames, a raised stoop, brick
    courses, sandstone trim, its gable (step / neck / bell / spout / cornice) against the sky, a hoist beam."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1
    W = Z1 - Z0

    def M(u, Y):
        return C(X, Y, lerp(Z0, Z1, u))
    G = G if G is not None else (W * 0.85 if kind != "cornice" else 1.9)
    top = Yb + Ht
    gp = gable_pts(kind, G)
    outline = [M(0, Yb)] + [M(u, top + dy) for u, dy in gp] + [M(1, Yb)]
    out = [F(outline, PAPER)]
    near_w = abs(M(1, Yb)[0] - M(0, Yb)[0])
    inner = []
    if brick and near_w > 6:
        cl = []
        Y = Yb + 0.35
        while Y < top + G:
            cl.append((M(-0.05, Y), M(1.05, Y)))
            Y += 0.42
        inner.append(segs(cl, 0.5, seed, 0, op=0.4))
    inner.append(tone(U, outline, lvl, 78))
    out.append(clipped(U("ch"), poly(outline), "".join(inner)))
    # windows
    fl = [Yb + 1.2] + [Yb + 4.2 + 3.0 * k for k in range(int((Ht - 4.6) / 3.0) + 1)]
    fl = [f for f in fl if f + 2.2 < top - 0.3]
    wins, bars, frames = [], [], []
    door_bay = rnd.randrange(bays)
    for j, y0 in enumerate(fl):
        hgt = 2.4 if j else 2.3
        for i in range(bays):
            u0, u1 = (i + 0.24) / bays, (i + 0.76) / bays
            if j == 0 and i == door_bay:
                continue
            q = [M(u0, y0 + hgt), M(u1, y0 + hgt), M(u1, y0), M(u0, y0)]
            wins.append(q)
            if abs(q[1][0] - q[0][0]) > 4:
                bars.append((pt(q[0], q[1], 0.5), pt(q[3], q[2], 0.5)))
                for t in (0.33, 0.62):
                    bars.append((pt(q[0], q[3], t), pt(q[1], q[2], t)))
                frames.append(q)
    if wins:
        far = near_w < 14
        fill = INK if far else gl
        out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{fill}" opacity="{0.8 if far else 1}"/>')
        out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="none" stroke="{INK}" stroke-width="{0.9 if far else 1.1}"/>')
        out.append(segs(bars, 0.9, seed, 0, color=PAPER))
    # door + stoop with railings
    u0, u1 = (door_bay + 0.2) / bays, (door_bay + 0.8) / bays
    dq = [M(u0, Yb + 3.3), M(u1, Yb + 3.3), M(u1, Yb + 1.0), M(u0, Yb + 1.0)]
    out.append(F(dq, INK, 0.85))
    if near_w > 20:
        fan = [M(u0, Yb + 3.3), M((u0 + u1) / 2, Yb + 3.95), M(u1, Yb + 3.3)]
        out.append(F(fan, PAPER) + pen(fan, 0.9, seed, 0.05) + seg(*M(u0 - 0.05, Yb + 4.1), *M(u1 + 0.05, Yb + 4.1), 1.0, seed, 0))
    st = [C(X, Yb + 1.0, lerp(Z0, Z1, u0 - 0.06)), C(X, Yb + 1.0, lerp(Z0, Z1, u1 + 0.06)),
          C(X + sg * 0.8, Yb, lerp(Z0, Z1, u1 + 0.06)), C(X + sg * 0.8, Yb, lerp(Z0, Z1, u0 - 0.06))]
    out.append(F(st, PAPER) + H(U, st, 0, 2.0, 0.6, op=0.6) + pen(st, 0.8, seed, 0.05, True))
    # string course + cornice line at the eaves, sandstone trim on the gable edges
    out.append(pen([M(0, top), M(1, top)], 1.2, seed, 0.05))
    out.append(pen([M(0, Yb + 4.0), M(1, Yb + 4.0)], 0.8, seed + 1, 0.05, op=0.8))
    # gable window / hoist door + hoist beam
    if kind != "cornice":
        gq = [M(0.42, top + G * 0.62), M(0.58, top + G * 0.62), M(0.58, top + G * 0.15), M(0.42, top + G * 0.15)]
        out.append(F(gq, INK, 0.85))
        hb = top + G * 0.72
    else:
        hb = top + 0.4
    a, b = M(0.5, hb), C(X + sg * 1.1, hb, lerp(Z0, Z1, 0.5))
    out.append(seg(a[0], a[1], b[0], b[1], max(1.0, near_w / 40), seed, 0) + seg(b[0], b[1], b[0], b[1] + max(2, near_w / 12), 0.7, seed, 0))
    if kind == "cornice":
        cq = [M(-0.03, top + 0.8), M(1.03, top + 0.8), C(X + sg * 0.5, top + 0.8, Z1 + 0.03 * W), C(X + sg * 0.5, top + 0.8, Z0 - 0.03 * W)]
        out.append(F(cq, INK, 0.6))
    out.append(pen(outline, 1.5 if near_w > 12 else 1.1, seed, 0.15, closed=True))
    return "".join(out)


def bike(x, y, L, seed=1, flip=False, basket=False, w=None):
    """A Dutch upright bicycle, side view, wheels on y, length L px (front to the right unless flip)."""
    s = -1 if flip else 1
    r = L * 0.2
    w = w or max(0.7, L * 0.03)
    a, b = (x - s * L * 0.3, y - r), (x + s * L * 0.3, y - r)
    crank = (x - s * L * 0.03, y - r)
    seat = (x - s * L * 0.12, y - r - L * 0.36)
    head = (x + s * L * 0.2, y - r - L * 0.36)
    hlow = (x + s * L * 0.23, y - r - L * 0.2)
    out = [f'<circle cx="{f1(c[0])}" cy="{f1(c[1])}" r="{f1(r)}" fill="none" stroke="{INK}" stroke-width="{w:.2f}"/>' for c in (a, b)]
    out.append(P(f"M {f1(a[0])} {f1(a[1])} L {f1(crank[0])} {f1(crank[1])} L {f1(seat[0])} {f1(seat[1])} L {f1(a[0])} {f1(a[1])} "
                 f"M {f1(crank[0])} {f1(crank[1])} Q {f1(x + s * L * 0.1)} {f1(y - r - L * 0.05)} {f1(hlow[0])} {f1(hlow[1])} "
                 f"M {f1(head[0])} {f1(head[1])} L {f1(b[0])} {f1(b[1])} "
                 f"M {f1(head[0])} {f1(head[1])} q {f1(-s * L * 0.02)} {f1(-L * 0.08)} {f1(-s * L * 0.12)} {f1(-L * 0.08)} "
                 f"M {f1(seat[0] - s * L * 0.07)} {f1(seat[1] - L * 0.02)} L {f1(seat[0] + s * L * 0.05)} {f1(seat[1] - L * 0.02)}", w * 1.2))
    out.append(P(f"M {f1(a[0] - s * r * 1.05)} {f1(a[1] - r * 0.3)} Q {f1(a[0])} {f1(a[1] - r * 1.25)} {f1(a[0] + s * r * 0.9)} {f1(a[1] - r * 0.5)}", w * 0.9))
    if basket:
        bq = [(head[0] + s * L * 0.02, head[1] + L * 0.02), (head[0] + s * L * 0.2, head[1] + L * 0.02),
              (head[0] + s * L * 0.18, head[1] + L * 0.14), (head[0] + s * L * 0.04, head[1] + L * 0.14)]
        out.append(F(bq, PAPER) + pen(bq, w, seed, 0.05, True) + P(" ".join(
            f"M {f1(lerp(bq[0][0], bq[1][0], t))} {f1(bq[0][1])} L {f1(lerp(bq[3][0], bq[2][0], t))} {f1(bq[3][1])}" for t in (0.33, 0.66)), w * 0.6))
    return "".join(out)


def westertoren(U, x, base, h, seed, op=1.0):
    """The Westerkerk tower: square brick base, two open stone stages, an octagonal lantern, the crowned cap."""
    out = []
    w = h * 0.16
    k = h / 100.0
    segs_ = [(0, 42, 1.0), (42, 56, 0.82), (56, 68, 0.66), (68, 78, 0.5)]
    for y0, y1, s in segs_:
        q = [(x - w * s / 2, base - y1 * k), (x + w * s / 2, base - y1 * k), (x + w * s / 2, base - y0 * k), (x - w * s / 2, base - y0 * k)]
        out.append(F(q, PAPER) + H(U, [pt(q[0], q[1], 0.55), q[1], q[2], pt(q[3], q[2], 0.55)], 90, 1.3, 0.6)
                   + sketch(q, 1.0, seed + y0, 0.3))
        if y0 >= 42:
            for t in (0.3, 0.7):
                xx = lerp(q[0][0], q[1][0], t)
                out.append(F(arch_u(xx - w * s * 0.08, xx + w * s * 0.08, base - y1 * k + 2, base - y0 * k - 1.5, 0.3), INK, 0.8))
        else:
            out.append(H(U, q, 0, 1.8, 0.5, op=0.6))
        out.append(seg(q[0][0] - 1.5, q[0][1], q[1][0] + 1.5, q[1][1], 1.2, seed, 0))
    cap = [(x - w * 0.27, base - 78 * k), (x - w * 0.3, base - 84 * k), (x - w * 0.12, base - 90 * k), (x, base - 92 * k),
           (x + w * 0.12, base - 90 * k), (x + w * 0.3, base - 84 * k), (x + w * 0.27, base - 78 * k)]
    out.append(F(cap, PAPER) + H(U, cap, 90, 1.2, 0.6, span=(0.5, 1), dark=(x + w, base - 85 * k)) + pen(cap, 1.0, seed, 0.05, smooth=True))
    # the imperial crown and the mast
    cy = base - 95 * k
    out.append(F(smooth_closed([(x - w * 0.16, cy + 2 * k), (x - w * 0.18, cy - 1.5 * k), (x, cy - 3.2 * k), (x + w * 0.18, cy - 1.5 * k),
                                (x + w * 0.16, cy + 2 * k)]), INK, 0.85))
    out.append(nib([(x, cy - 3 * k), (x, base - h)], 1.4, taper=(1, 0.3), seed=seed, color=INK))
    out.append(f'<circle cx="{f1(x)}" cy="{f1(base - h * 0.995)}" r="1.4" fill="{INK}"/>')
    return f'<g opacity="{op}">' + "".join(out) + "</g>"


def sloep(U, C, Xc, Zb, L, seed, people=3):
    """An open canal boat coming toward us: the hull's flanks take the accent wash, people on the thwarts."""
    rnd = random.Random(seed)
    half = 1.05
    plan = [(0.0, 0.0), (0.55, 0.06), (0.9, 0.2), (1.0, 0.42), (1.02, 0.7), (0.95, 0.98)]  # (half-width k, along t)
    gun = [(Xc + half * k, Zb + L * t) for k, t in plan] + [(Xc - half * k, Zb + L * t) for k, t in plan[::-1]]
    top = [C(x, 0.65, z) for x, z in gun]
    wl = [C(x * 0.96 + Xc * 0.04, 0.0, z + 0.15) for x, z in gun]
    out = []
    side = top + wl[::-1]
    hullp = hull(top + wl)
    out.append(F(hullp, PAPER))
    out.append(accent(U, poly(hullp), bbox(hullp), seed, op=0.9, ang=-10, n=16, length=(6, 16), width=(1.5, 2.6)))
    out.append(H(U, hullp, 0, 1.6, 0.7, op=0.55))
    inner = [C(Xc + (x - Xc) * 0.86, 0.5, z + 0.12) for x, z in gun]
    out.append(F(inner, PAPER) + H(U, inner, 20, 2.0, 0.6, op=0.5))
    out.append(pen(top, 1.5, seed, 0.1, closed=True))
    out.append(pen(inner, 0.9, seed, 0.1, closed=True))
    th = []
    for t in (0.35, 0.6, 0.85):
        z = Zb + L * t
        th.append((C(Xc - half * 0.92, 0.5, z), C(Xc + half * 0.92, 0.5, z)))
    out.append(segs(th, 1.4, seed, 0))
    for i in range(people):
        t = (0.45, 0.72, 0.9, 0.58)[i]
        X = Xc + (0.4 if i % 2 else -0.35)
        x, yb = C(X, 0.5, Zb + L * t)
        hh = C.f * 1.05 / (Zb + L * t)
        out.append(F(smooth_closed([(x - hh * 0.2, yb), (x + hh * 0.2, yb), (x + hh * 0.17, yb - hh * 0.62), (x - hh * 0.17, yb - hh * 0.62)]), INK, 0.92))
        out.append(f'<circle cx="{f1(x)}" cy="{f1(yb - hh * 0.8)}" r="{f1(hh * 0.15)}" fill="{INK}"/>')
    # the helmsman standing at the stern
    x, yb = C(Xc + 0.1, 0.5, Zb + L * 0.97)
    out.append(person(x, yb, C.f * 1.7 / (Zb + L), seed + 7))
    # bow wave
    b0 = C(Xc, 0.0, Zb + 0.1)
    out.append(P(f"M {f1(b0[0])} {f1(b0[1])} q -14 4 -34 8 M {f1(b0[0])} {f1(b0[1])} q 14 4 34 8", 1.0, INK, 0.85))
    return "".join(out)


def houseboat(U, C, X0, X1, Z0, Z1, seed, gl):
    """A woonboot moored along the quay: dark hull, a cabin with a row of windows, pot plants on the roof."""
    rnd = random.Random(seed)
    out = []
    hs = C.qx(X1, Z0, Z1, -0.1, 0.8)
    hf = C.qz(Z0, X0, X1, -0.1, 0.8)
    out.append(F(hs, INK, 0.85) + F(hf, INK, 0.75))
    cx0, cx1, cz0, cz1 = X0 + 0.25, X1 - 0.25, Z0 + 0.6, Z1 - 0.4
    deck = [C(X0, 0.8, Z0), C(X1, 0.8, Z0), C(X1, 0.8, Z1), C(X0, 0.8, Z1)]
    out.append(F(deck, PAPER) + pen(deck, 0.9, seed, 0.05, True))
    cs = C.qx(cx1, cz0, cz1, 0.8, 2.5)
    cf = C.qz(cz0, cx0, cx1, 0.8, 2.5)
    roof = [C(cx0 - 0.1, 2.5, cz0 - 0.1), C(cx1 + 0.1, 2.5, cz0 - 0.1), C(cx1 + 0.1, 2.5, cz1), C(cx0 - 0.1, 2.5, cz1)]
    out.append(F(cs, PAPER) + F(cf, PAPER) + tone(U, cf, 2, 80) + H(U, cs, 0, 2.2, 0.6, op=0.6))
    sm_ = homog(cs)
    out.append(windows(sm_, [[(u0, 0.25), (u0 + 0.09, 0.25), (u0 + 0.09, 0.62), (u0, 0.62)] for u0 in [0.06 + k * 0.125 for k in range(8)]], gl, stroke=0.8))
    out.append(F(roof, PAPER) + pen(roof, 1.1, seed, 0.05, True))
    for q in (cs, cf):
        out.append(sketch(q, 1.1, seed, 0.3))
    for k in range(5):
        z = lerp(cz0 + 0.6, cz1 - 0.6, k / 4)
        x, y = C(lerp(cx0, cx1, rnd.uniform(0.3, 0.7)), 2.5, z)
        r = C.f * rnd.uniform(0.35, 0.5) / z
        out.append(lobe(U, x, y - r * 0.7, r * 1.1, r * 0.8, seed * 10 + k, w=0.9, dense=1.3))
    return "".join(out)


@design("amsterdam")
def amsterdam(U):
    """Down the Herengracht from the crown of a canal bridge on a bright afternoon: gabled houses with step, neck
    and bell gables standing shoulder to shoulder, the shaded row on the right behind its elms, a hump bridge
    across the canal with bicycles chained to its railing, an open boat (the accent) gliding toward us, and the
    Westertoren rising far beyond the roofs."""
    C = Cam(f=265, cx=300, vpy=300, eye=4.2)
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 236, 84, 110, 18, 4) + cloud(U, 366, 120, 60, 9, 5))
    art.append(gulls([(330, 150, 7), (346, 138, 5), (262, 166, 5)], 6))
    QY = 2.2      # quay (street) level above the water
    XW = 8.0      # canal half width
    XF = 14.0     # house fronts
    # the far end: a row of gables across the canal's bend, the tower beyond
    art.append(westertoren(U, C(6, 0, 230)[0], C(6, QY, 230)[1], C.f * 85 / 230, 7, op=0.85))
    ZE = 170.0
    xe = -XF
    rr = random.Random(8)
    far = []
    while xe < XF:
        w = rr.uniform(5, 8)
        kd = rr.choice(("step", "neck", "bell", "spout", "cornice"))
        ht = rr.uniform(12, 15)
        gp = gable_pts(kd, w * 0.85 if kd != "cornice" else 1.9)
        q = [C(xe, QY, ZE)] + [C(xe + u * w, QY + ht + dy, ZE) for u, dy in gp] + [C(xe + w, QY, ZE)]
        far.append(F(q, PAPER) + H(U, q, 80, 1.8, 0.55, op=0.55) + pen(q, 0.9, int(xe * 10), 0.05, closed=True))
        far.append(facade(U, C.qz(ZE, xe + w * 0.15, xe + w * 0.85, QY + 1.5, QY + ht - 0.6), 3, 4, "dark", int(xe * 7) + 99, mx=0.3, my=0.3, w=0.5))
        xe += w
    art.append(f'<g opacity="0.85">{"".join(far)}</g>')
    # far water beyond the bridge
    fw = [C(-XW, 0, 48), C(-XW, 0, ZE), C(XW, 0, ZE), C(XW, 0, 48)]
    art.append(ripples(U, 200, 400, C(0, 0, ZE)[1], C(0, 0, 48)[1] + 2, 9, dens=1.3, gap=(1.2, 2.6), ln=((2, 6), (6, 14)), w=(0.7, 1.0),
                       refl=[(200, 262, 0.5), (338, 400, 0.8)], clip=poly(fw)))
    # the house rows, far to near; quay walls and quay tops
    kinds = ["neck", "step", "bell", "cornice", "spout", "neck", "bell", "step", "cornice", "neck", "bell", "spout", "step", "neck"]
    for sgn, side_seed in ((-1, 30), (1, 60)):
        X = sgn * XF
        rows = []
        z = 13.0
        i = 0
        rr = random.Random(side_seed)
        while z < ZE:
            w = rr.uniform(5.5, 8.5) * (1 + z / 260)
            ht = rr.uniform(12.5, 16.0)
            kd = kinds[(i + side_seed) % len(kinds)]
            lv = (rr.choice((0, 0, 1, 2)) if sgn < 0 else 3)
            rows.append((z, z + w, ht, kd, side_seed + i, lv))
            z += w
            i += 1
        for z0, z1, ht, kd, sd, lv in rows[::-1]:
            art.append(canal_house(U, C, X, z0, z1, QY, ht, kd, sd, gl, lvl=lv, brick=lv < 3, bays=3 if z1 - z0 < 7.5 else 4))
        # quay top (cobbled street) and the quay wall
        top = [C(sgn * XW, QY, 9), C(sgn * XW, QY, ZE), C(X, QY, ZE), C(X, QY, 9)]
        art.append(F(top, PAPER) + clipped(U("qt"), poly(top), cobbles(U, C, min(sgn * XW, X), max(sgn * XW, X), 9, ZE, side_seed,
                                                                         row=0.9, stone=1.1, w=0.6, op=0.45)))
        wall = C.qx(sgn * XW, 9, ZE, 0, QY)
        art.append(F(wall, PAPER) + tone(U, wall, 2 if sgn < 0 else 4, 80) + pen([wall[0], wall[1]], 1.4, side_seed, 0.05))
        # bollards along the quay edge
        bl = []
        z = 9.5
        while z < 70:
            a, b = C(sgn * (XW + 0.4), QY, z), C(sgn * (XW + 0.4), QY + 0.9, z)
            bl.append((a, b))
            z += 2.2
        art.append(segs(bl, 1.0, side_seed, 0) if False else "".join(
            nib([a, b], max(1.0, 2.2 * (a[1] - b[1]) / 9), taper=(1, 0.9), smooth=False, seed=side_seed, color=INK) for a, b in bl))
    # shadow of the right row on its quay, the elms on the right quay (far to near), lamps
    for z, sd in ((120, 5), (88, 4), (64, 3)):
        art.append(tree3(U, C, 10.6, QY, z, 11.5, 8.5, 700 + sd, light=(-1, -1), lobes=6, trunk=0.36))
    for z, sd in ((130, 3), (96, 2)):
        art.append(tree3(U, C, -10.6, QY, z, 11.0, 8.0, 720 + sd, light=(-1, -1), lobes=5, trunk=0.36))
    for X, z in ((-8.9, 34), (8.9, 19.5)):
        x, yb = C(X, QY, z)
        art.append(lamp(x, yb, C.f * 4.4 / z, 77, "lantern", max(1.2, 30 / z)))
    # bicycles and people on the quays
    for X, z, sd, fl in ((-9.2, 20, 1, False), (-9.6, 27, 2, True), (-12.4, 46, 3, False), (12.2, 33, 4, True)):
        x, yb = C(X, QY, z)
        art.append(person(x, yb, C.f * 1.72 / z, 80 + sd, flip=fl, bag=sd == 1))
    for X, z, sd, fl in ((-9.0, 16, 11, False), (-9.0, 17.2, 12, True), (9.1, 37, 13, True)):
        x, yb = C(X, QY, z)
        art.append(bike(x, yb, C.f * 1.75 / z, sd, flip=fl, basket=sd == 12))
    # the hump bridge across the canal
    ZB = 23.0

    def deck(X):
        return QY + 0.75 * math.cos(math.pi * X / (2 * XW)) ** 2
    xs = [-XW - 0.6 + i * (2 * XW + 1.2) / 32 for i in range(33)]
    face = [C(-XW - 0.6, 0, ZB)] + [C(X, deck(X), ZB) for X in xs] + [C(XW + 0.6, 0, ZB)]
    arch = [C(-4.4 + 8.8 * t / 24, 1.95 * math.sin(math.pi * t / 24) ** 0.8 - 0.05, ZB) for t in range(25)]
    deck_top = [C(X, deck(X), ZB) for X in xs] + [C(X, deck(X), ZB + 7) for X in xs[::-1]]
    art.append(F(deck_top, PAPER) + H(U, deck_top, 0, 2.2, 0.6, op=0.5))
    art.append(F(face, PAPER))
    brick_l = []
    for Y in [0.3 * k for k in range(1, 10)]:
        brick_l.append((C(-XW - 0.6, Y, ZB), C(XW + 0.6, Y, ZB)))
    art.append(clipped(U("bf"), poly(face), segs(brick_l, 0.55, 3, 0, op=0.55) + tone(U, face, 1, 80)))
    art.append(F(arch, INK, 0.92))
    # light at the far mouth of the arch, low on the water
    mouth = [C(-3.0 + 6.0 * t / 12, 0.9 * math.sin(math.pi * t / 12) - 0.05, ZB + 7) for t in range(13)]
    art.append(F(mouth, PAPER, 0.85) + ripples(U, 200, 400, C(0, 0.9, ZB + 7)[1], C(0, 0, ZB + 7)[1], 31, dens=1.4, gap=(1.4, 1.8),
                                                ln=((2, 6), (3, 8)), w=(0.6, 0.8), clip=poly(mouth)))
    art.append(pen(arch, 1.6, 4, 0.05, smooth=True))
    # voussoirs round the arch
    vs = []
    for t in range(1, 24, 2):
        a = math.pi * t / 24
        Xa, Ya = -4.4 * math.cos(a), 1.95 * math.sin(a) ** 0.8
        vs.append((C(Xa, Ya, ZB), C(Xa * 1.12, Ya + 0.35 * math.sin(a), ZB)))
    art.append(segs(vs, 0.8, 5, 0))
    art.append(pen([C(X, deck(X), ZB) for X in xs], 1.8, 6, 0.05, smooth=True))
    # bicycles chained to the railing, a cyclist crossing, the railing over them
    for X, sd, fl, bk in ((-6.6, 1, False, True), (-5.3, 2, True, False), (-4.1, 3, False, False), (3.0, 4, True, True),
                          (4.3, 5, False, False), (5.6, 6, False, False)):
        x, yb = C(X, deck(X), ZB + 0.35)
        art.append(bike(x, yb, C.f * 1.75 / (ZB + 0.35), 40 + sd, flip=fl, basket=bk))
    x, yb = C(-0.6, deck(-0.6), ZB + 3.5)
    art.append(cyclist(x, yb, C.f * 1.75 / (ZB + 3.5), 50, flip=True))
    x, yb = C(1.4, deck(1.4), ZB + 4.5)
    art.append(person(x, yb, C.f * 1.72 / (ZB + 4.5), 51))
    rail = []
    for X in [-XW - 0.4 + k * 0.24 for k in range(int((2 * XW + 0.8) / 0.24) + 1)]:
        rail.append((C(X, deck(X), ZB), C(X, deck(X) + 1.0, ZB)))
    art.append(segs(rail, 0.7, 7, 0, op=0.9))
    art.append(pen([C(X, deck(X) + 1.0, ZB) for X in xs], 1.5, 8, 0.05, smooth=True))
    art.append(pen([C(X, deck(X) + 0.15, ZB) for X in xs], 1.0, 9, 0.05, smooth=True))
    for X in (-XW - 0.4, XW + 0.4):
        x, yb = C(X, deck(X) + 1.0, ZB)
        art.append(lamp(x, yb + 2, C.f * 3.6 / ZB, 52, "lantern", 1.2))
    # the near water: reflections of the arch, the shaded row, the boat
    water = [C(-XW, 0, 9), C(-XW, 0, ZB), C(XW, 0, ZB), C(XW, 0, 9)]
    ax0, ax1 = C(-4.4, 0, ZB)[0], C(4.4, 0, ZB)[0]
    refl = [(ax0 + 4, ax1 - 4, 1.0), (C(XW, 0, 12)[0] - 120, 620, 0.5)]
    art.append(ripples(U, 0, 600, C(0, 0, ZB)[1], 600, 11, dens=0.75, gap=(1.8, 8.0), ln=((3, 8), (10, 26)), w=(0.7, 1.15), refl=refl,
                       skip=[(268, 296)], clip=poly(water)))
    rf = [C(-4.4 + 8.8 * t / 24, -1.6 * math.sin(math.pi * t / 24) ** 0.8, ZB) for t in range(25)]
    art.append(clipped(U("rf"), poly(rf), segs([((0, y), (600, y)) for y in range(int(C(0, 0, ZB)[1]), int(C(0, -1.7, ZB)[1]), 2)], 1.3, 12, 0.2)))
    art.append(houseboat(U, C, -7.9, -5.5, 11.0, 21.5, 14, gl))
    art.append(sloep(U, C, 1.6, 9.6, 5.4, 13))
    return plate(U, "amsterdam", art, 81, frame=(300, 248, 262, 210))


# ================================================================ KYOTO
def pagoda(U, cx, base, top, seed, op=1.0):
    """The Yasaka pagoda in elevation: five storeys under deep upswept eaves with dense bracketing beneath, a
    balcony railing on each upper storey, the bronze sorin spire with its nine rings and flame finial."""
    out = []
    Hh = base - top
    spire = 0.3 * Hh
    body_top = top + spire
    hs = [0.2, 0.19, 0.2, 0.2, 0.21]
    tot = sum(hs)
    hs = [h * (base - body_top) / tot for h in hs]
    W0 = 0.17 * Hh
    y0 = base
    shapes = []
    for i in range(5):
        h = hs[i]
        w = W0 * (1 - 0.075 * i)
        wn = W0 * (1 - 0.075 * (i + 1))
        R = W0 * (1.42 - 0.085 * i)
        hb = h * 0.42
        yb_top = y0 - hb
        ytip = yb_top - h * 0.12
        th = h * 0.1
        yr = y0 - h
        # body with doors and panels, balcony
        bq = [(cx - w / 2, yb_top), (cx + w / 2, yb_top), (cx + w / 2, y0), (cx - w / 2, y0)]
        out.append(F(bq, PAPER))
        out.append(F([(cx - w * 0.14, yb_top + hb * 0.25), (cx + w * 0.14, yb_top + hb * 0.25), (cx + w * 0.14, y0), (cx - w * 0.14, y0)], INK, 0.85))
        out.append(segs([((cx + k * w / 2, yb_top), (cx + k * w / 2, y0)) for k in (-0.62, -0.32, 0.32, 0.62)], 0.8, seed + i, 0))
        out.append(H(U, [(cx + w * 0.15, yb_top), (cx + w / 2, yb_top), (cx + w / 2, y0), (cx + w * 0.15, y0)], 90, 1.4, 0.7))
        out.append(H(U, bq, 0, 2.2, 0.6, op=0.5, span=(0, 0.35)))
        out.append(sketch(bq, 1.1, seed + i, 0.3))
        if i:
            rl = [(cx - w * 0.62, y0 - hb * 0.22), (cx + w * 0.62, y0 - hb * 0.22), (cx + w * 0.62, y0), (cx - w * 0.62, y0)]
            out.append(F(rl, PAPER) + segs([((lerp(rl[0][0], rl[1][0], t / 14), rl[0][1]), (lerp(rl[0][0], rl[1][0], t / 14), y0))
                                            for t in range(15)], 0.6, seed, 0) + pen([rl[0], rl[1]], 1.0, seed, 0.05) + pen([rl[3], rl[2]], 1.0, seed, 0.05))
        # roof: soffit with brackets, fascia, tiled surface sweeping up to the next storey
        L_up = [(cx - R - th * 0.6, ytip - th * 1.6), (cx - R * 0.72, ytip - th * 0.55), (cx - R * 0.45, yr + (ytip - yr) * 0.45),
                (cx - wn * 0.62, yr)]
        R_up = [(2 * cx - x, y) for x, y in L_up[::-1]]
        roof = L_up + R_up + [(cx + R + th * 0.6, ytip - th * 0.6), (cx + R * 0.7, ytip + th * 0.25), (cx + w / 2, yb_top),
                              (cx - w / 2, yb_top), (cx - R * 0.7, ytip + th * 0.25), (cx - R - th * 0.6, ytip - th * 0.6)]
        out.append(F(roof, PAPER, smooth=False))
        soff = [(cx - R * 0.7, ytip + th * 0.25), (cx - w / 2, yb_top), (cx + w / 2, yb_top), (cx + R * 0.7, ytip + th * 0.25),
                (cx + R + th * 0.6, ytip - th * 0.6), (cx + R * 0.72, ytip - th * 0.05), (cx - R * 0.72, ytip - th * 0.05),
                (cx - R - th * 0.6, ytip - th * 0.6)]
        out.append(F(soff, INK, 0.88))
        br = [((cx + k * R * 0.07, ytip - th * 0.05), (cx + k * w * 0.05, yb_top)) for k in range(-13, 14)]
        out.append(segs(br, 0.6, seed, 0, color=PAPER, op=0.55))
        tiles = []
        for k in range(-18, 19):
            t = k / 18
            tiles.append(((cx + t * R * 0.96, ytip - th * (0.6 + 0.9 * abs(t) ** 3)), (cx + t * wn * 0.6, yr)))
        out.append(clipped(U("pg"), poly(L_up + R_up + [(cx + R, ytip), (cx - R, ytip)]), segs(tiles, 0.6, seed + i, 0.05, op=0.8)
                           + H(U, poly([(cx, yr - 2), (cx + R + 4, ytip - th * 2), (cx + R + 4, ytip + 2), (cx, ytip + 2)]), 90, 1.3, 0.6,
                               box=(cx, yr - 4, cx + R + 6, ytip + 4))))
        out.append(pen(L_up, 1.3, seed + i, 0.05, smooth=True) + pen(R_up, 1.3, seed + i + 1, 0.05, smooth=True))
        edge = [(cx - R - th * 0.6, ytip - th * 1.6), (cx - R - th * 0.6, ytip - th * 0.6), (cx - R * 0.7, ytip + th * 0.25),
                (cx + R * 0.7, ytip + th * 0.25), (cx + R + th * 0.6, ytip - th * 0.6), (cx + R + th * 0.6, ytip - th * 1.6)]
        out.append(pen(edge, 1.6, seed + i + 2, 0.05, smooth=True))
        out.append(pen([(cx - R * 0.72, ytip - th * 0.05), (cx + R * 0.72, ytip - th * 0.05)], 0.9, seed, 0.05))
        # wind bells at the corners
        for sg in (-1, 1):
            bx = cx + sg * (R + th * 0.4)
            out.append(seg(bx, ytip - th * 0.8, bx, ytip + th * 0.6, 0.7, seed, 0) + f'<circle cx="{f1(bx)}" cy="{f1(ytip + th * 0.8)}" r="{f1(max(0.9, th * 0.22))}" fill="{INK}"/>')
        y0 = yr
    # sorin
    sb = [(cx - W0 * 0.18, y0), (cx + W0 * 0.18, y0), (cx + W0 * 0.14, y0 - spire * 0.08), (cx - W0 * 0.14, y0 - spire * 0.08)]
    out.append(F(sb, PAPER) + H(U, sb, 90, 1.2, 0.6, span=(0.5, 1), dark=(cx + W0, y0)) + pen(sb, 1.0, seed, 0.05, True))
    out.append(nib([(cx, y0 - spire * 0.08), (cx, top + spire * 0.06)], max(1.6, W0 * 0.05), taper=(1, 0.6), seed=seed, color=INK))
    rings = []
    for k in range(9):
        yy = y0 - spire * (0.16 + 0.055 * k)
        rw = W0 * (0.1 - 0.004 * k)
        rings.append(((cx - rw, yy), (cx + rw, yy)))
    out.append(segs(rings, 1.3, seed, 0))
    fl = [(cx, top + spire * 0.04), (cx - W0 * 0.08, top + spire * 0.16), (cx, top + spire * 0.22), (cx + W0 * 0.08, top + spire * 0.16)]
    out.append(F(fl, PAPER) + pen(fl, 1.0, seed, 0.05, closed=True, smooth=True))
    out.append(nib([(cx, top + spire * 0.04), (cx, top)], 1.2, taper=(1, 0.3), seed=seed, color=INK))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(top + spire * 0.025)}" r="{f1(max(1.2, W0 * 0.04))}" fill="{INK}"/>')
    return f'<g opacity="{op}">' + "".join(out) + "</g>"


def machiya(U, C, X, Z0, Z1, g, seed, gl, lvl=0, door=0.5, lantern=False, red_lantern=False, noren=True, sign=False):
    """A Kyoto townhouse front in the plane X on a lane rising with g(Z): wooden lattice, inuyarai fence, a deep
    tiled pent roof, the slatted mushiko-mado window above, the main eave; we look up into the soffits."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1
    Yr = g(Z1)

    def M(u, Y):
        return C(X, Y, lerp(Z0, Z1, u))
    near_w = abs(M(1, Yr)[0] - M(0, Yr)[0])
    out = []
    wall = [M(0, g(Z0) - 0.05), M(0, Yr + 6.0), M(1, Yr + 6.0), M(1, Yr - 0.05)]
    out.append(F(wall, PAPER))
    # stone plinth where the lane drops away
    pl = [M(0, g(Z0) - 0.05), M(0, Yr + 0.35), M(1, Yr + 0.35), M(1, Yr - 0.05)]
    out.append(F(pl, PAPER) + H(U, pl, 0, 1.8, 0.6, op=0.7) + pen([pl[1], pl[2]], 0.9, seed, 0.05))
    # ground floor: lattice with a doorway
    d0, d1 = door - 0.14, door + 0.14
    lat = []
    n = int(near_w / 2.2) + 6
    for k in range(n + 1):
        u = k / n
        if d0 <= u <= d1:
            continue
        lat.append((M(u, Yr + 0.4), M(u, Yr + 2.7)))
    gq = [M(0, Yr + 2.7), M(1, Yr + 2.7), M(1, Yr + 0.35), M(0, Yr + 0.35)]
    out.append(H(U, gq, 90, 3.0, 0.5, op=0.35) + tone(U, gq, lvl, 80))
    out.append(segs(lat, 0.75 if near_w > 40 else 0.6, seed, 0, op=0.95))
    out.append(segs([(M(0, Yr + 2.7), M(1, Yr + 2.7)), (M(0, Yr + 0.4), M(1, Yr + 0.4)), (M(0, Yr + 1.55), M(1, Yr + 1.55))], 1.0, seed, 0))
    dq = [M(d0, Yr + 2.7), M(d1, Yr + 2.7), M(d1, Yr + 0.35), M(d0, Yr + 0.35)]
    out.append(F(dq, INK, 0.9))
    if noren and near_w > 18:
        nq = [M(d0, Yr + 2.7), M(d1, Yr + 2.7), M(d1, Yr + 1.75), M(d0, Yr + 1.75)]
        out.append(F(nq, PAPER) + H(U, nq, 90, 1.6, 0.6, op=0.6))
        nm = homog(nq)
        out.append(segs([(nm(t, 0.1), nm(t, 1)) for t in (0.33, 0.66)], 1.2, seed, 0, color=PAPER) + pen(nq, 0.9, seed, 0.05, True))
        if near_w > 60:
            cx_, cy_ = nm(0.5, 0.55)
            out.append(f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(abs(nq[1][0] - nq[0][0]) * 0.12)}" fill="{PAPER}" stroke="{INK}" stroke-width="0.9"/>')
    # inuyarai: curved bamboo fence at the foot of the wall
    if near_w > 24:
        cv = []
        for k in range(int(near_w / 2.6)):
            u = (k + 0.5) / int(near_w / 2.6)
            if d0 - 0.03 <= u <= d1 + 0.03:
                continue
            z = lerp(Z0, Z1, u)
            a, b = C(X + sg * 0.55, g(z), z), C(X, Yr + 1.0, z)
            m = C(X + sg * 0.5, Yr + 0.7, z)
            cv.append(f"M {f1(a[0])} {f1(a[1])} Q {f1(m[0])} {f1(m[1])} {f1(b[0])} {f1(b[1])}")
        out.append(P(" ".join(cv), 0.8, INK, 0.9))
    # pent roof (ichimonji): soffit seen from below, fascia with round tile ends
    ps = [M(0, Yr + 3.25), M(1, Yr + 3.25), C(X + sg * 0.95, Yr + 2.95, Z1), C(X + sg * 0.95, Yr + 2.95, Z0)]
    out.append(F(ps, PAPER) + tone(U, ps, 4, 0) + segs([(M(u, Yr + 3.25), C(X + sg * 0.95, Yr + 2.95, lerp(Z0, Z1, u))) for u in
                                                         [k / 14 for k in range(15)]], 0.5, seed, 0, color=PAPER, op=0.5))
    fa = [C(X + sg * 0.95, Yr + 2.95, Z0), C(X + sg * 0.95, Yr + 2.95, Z1), C(X + sg * 0.95, Yr + 3.3, Z1), C(X + sg * 0.95, Yr + 3.3, Z0)]
    out.append(F(fa, PAPER) + pen(fa, 1.2, seed, 0.05, True))
    if near_w > 30:
        bumps = []
        k = int(near_w / 4)
        for i in range(k):
            p0 = C(X + sg * 0.95, Yr + 3.3, lerp(Z0, Z1, i / k))
            p1 = C(X + sg * 0.95, Yr + 3.3, lerp(Z0, Z1, (i + 1) / k))
            bumps.append(f"M {f1(p0[0])} {f1(p0[1])} Q {f1((p0[0] + p1[0]) / 2)} {f1(p0[1] - abs(p1[0] - p0[0]) * 0.6)} {f1(p1[0])} {f1(p1[1])}")
        out.append(P(" ".join(bumps), 0.8))
    # upper floor: plaster with the slatted window
    up = [M(0, Yr + 5.5), M(1, Yr + 5.5), M(1, Yr + 3.3), M(0, Yr + 3.3)]
    out.append(tone(U, up, max(0, lvl - 1), 80))
    mq = [M(0.18, Yr + 4.85), M(0.82, Yr + 4.85), M(0.82, Yr + 3.85), M(0.18, Yr + 3.85)]
    out.append(F(mq, INK, 0.85))
    mm = homog(mq)
    out.append(segs([(mm(t, 0.02), mm(t, 0.98)) for t in [(k + 0.5) / max(4, int(near_w / 3.5)) for k in range(max(4, int(near_w / 3.5)))]],
                    max(0.6, min(1.6, near_w / 50)), seed, 0, color=PAPER))
    out.append(pen(mq, 1.0, seed, 0.05, True))
    # main eave soffit with rafter ends
    ms = [M(0, Yr + 5.55), M(1, Yr + 5.55), C(X + sg * 1.25, Yr + 5.85, Z1), C(X + sg * 1.25, Yr + 5.85, Z0)]
    out.append(F(ms, PAPER) + tone(U, ms, 4, 0))
    raf = []
    for k in range(int(near_w / 3) + 3):
        u = k / (int(near_w / 3) + 2)
        raf.append((M(u, Yr + 5.55), C(X + sg * 1.2, Yr + 5.84, lerp(Z0, Z1, u))))
    out.append(segs(raf, 0.6, seed, 0, color=PAPER, op=0.6))
    fb = [C(X + sg * 1.25, Yr + 5.85, Z0), C(X + sg * 1.25, Yr + 5.85, Z1), C(X + sg * 1.25, Yr + 6.25, Z1), C(X + sg * 1.25, Yr + 6.25, Z0)]
    out.append(F(fb, PAPER) + H(U, fb, 0, 1.5, 0.6, op=0.6) + pen(fb, 1.3, seed, 0.05, True))
    rt = [C(X + sg * 1.25, Yr + 6.25, Z0), C(X + sg * 1.25, Yr + 6.25, Z1), C(X - sg * 0.6, Yr + 7.3, Z1), C(X - sg * 0.6, Yr + 7.3, Z0)]
    rm = homog(rt)
    nt = max(6, int(near_w / 2.4))
    out.append(F(rt, PAPER) + tone(U, rt, 1, 0) + rules_u(rm, [((k / nt, 0), (k / nt, 1)) for k in range(nt + 1)], 0.6, seed, op=0.85)
               + pen([rt[0], rt[1]], 1.4, seed, 0.05) + pen([rt[3], rt[2]], 1.6, seed + 1, 0.05)
               + pen([rt[1], rt[2]], 1.2, seed, 0.05))
    out.append(segs([(M(0, g(Z0)), M(0, Yr + 5.55)), (M(1, Yr), M(1, Yr + 5.55))], 1.3, seed, 0.05))
    # paper lanterns and a hanging sign
    if lantern:
        z = lerp(Z0, Z1, d1 + 0.08)
        x, y = C(X + sg * 0.75, Yr + 2.9, z)
        r = C.f * 0.24 / z
        hh = C.f * 0.55 / z
        ld = smooth_closed([(x, y), (x + r, y + hh * 0.2), (x + r * 1.05, y + hh * 0.55), (x + r * 0.85, y + hh * 0.9), (x, y + hh),
                            (x - r * 0.85, y + hh * 0.9), (x - r * 1.05, y + hh * 0.55), (x - r, y + hh * 0.2)])
        out.append(F(ld, PAPER))
        if red_lantern:
            out.append(accent(U, ld, (x - r * 1.2, y, x + r * 1.2, y + hh), seed, op=0.95, ang=0, n=8, length=(3, 8), width=(1, 2)))
        out.append(clipped(U("lt"), ld, segs([((x - r * 1.2, y + hh * t), (x + r * 1.2, y + hh * t)) for t in (0.2, 0.35, 0.5, 0.65, 0.8)], 0.6, seed, 0.2)
                           + H(U, ld, 90, 1.4, 0.6, span=(0.55, 1), dark=(x + r * 2, y + hh / 2), box=(x - r * 1.2, y, x + r * 1.2, y + hh))))
        out.append(P(ld, 1.0) + F([(x - r * 0.55, y - hh * 0.08), (x + r * 0.55, y - hh * 0.08), (x + r * 0.55, y + hh * 0.06), (x - r * 0.55, y + hh * 0.06)], INK)
                   + F([(x - r * 0.55, y + hh * 0.94), (x + r * 0.55, y + hh * 0.94), (x + r * 0.55, y + hh * 1.06), (x - r * 0.55, y + hh * 1.06)], INK))
    if sign:
        z = lerp(Z0, Z1, 0.15)
        sq = [C(X + sg * 0.2, Yr + 2.6, z), C(X + sg * 0.6, Yr + 2.6, z), C(X + sg * 0.6, Yr + 0.9, z), C(X + sg * 0.2, Yr + 0.9, z)]
        out.append(F(sq, PAPER) + H(U, sq, 90, 1.5, 0.6, op=0.5) + pen(sq, 1.0, seed, 0.05, True))
    return "".join(out)


def kimono(x, y, h, seed=1, flip=False, parasol=False, op=1.0):
    """A small figure in kimono: straight column robe, obi, hair in a bun; optionally under a parasol."""
    s = -1 if flip else 1
    body = [(x - h * 0.12, y - h * 0.81), (x + h * 0.12, y - h * 0.81), (x + h * 0.2, y - h * 0.74), (x + h * 0.21, y - h * 0.46),
            (x + h * 0.12, y - h * 0.46), (x + h * 0.1, y - h * 0.08), (x + h * 0.13, y), (x - h * 0.13, y), (x - h * 0.1, y - h * 0.08),
            (x - h * 0.12, y - h * 0.46), (x - h * 0.21, y - h * 0.46), (x - h * 0.2, y - h * 0.74)]
    out = [F(body, INK, op * 0.95)]
    out.append(P(f"M {f1(x - h * 0.11)} {f1(y - h * 0.6)} L {f1(x + h * 0.11)} {f1(y - h * 0.6)}", max(0.9, h * 0.06), PAPER, op * 0.85))
    out.append(P(f"M {f1(x + s * h * 0.02)} {f1(y - h * 0.57)} l {f1(-s * h * 0.06)} {f1(h * 0.08)}", max(0.7, h * 0.03), PAPER, op * 0.7))
    out.append(f'<circle cx="{f1(x)}" cy="{f1(y - h * 0.9)}" r="{f1(h * 0.095)}" fill="{INK}" opacity="{op:.2f}"/>'
               f'<circle cx="{f1(x - s * h * 0.03)}" cy="{f1(y - h * 1.0)}" r="{f1(h * 0.06)}" fill="{INK}" opacity="{op:.2f}"/>')
    if parasol:
        cy = y - h * 1.15
        r = h * 0.42
        cap = [(x - r, cy + r * 0.25), (x - r * 0.6, cy - r * 0.15), (x, cy - r * 0.3), (x + r * 0.6, cy - r * 0.15), (x + r, cy + r * 0.25)]
        out.append(F(cap, PAPER, smooth=False) + pen(cap, max(0.8, h * 0.05), seed, 0.05, closed=True, smooth=True)
                   + segs([((x, cy - r * 0.3), (x + k * r * 0.33, cy + r * 0.2)) for k in (-2, -1, 0, 1, 2)], 0.6, seed, 0)
                   + seg(x, cy - r * 0.3, x + s * h * 0.05, y - h * 0.62, max(0.7, h * 0.03), seed, 0))
    return "".join(out)


def nodate(U, C, X, Y, Z, seed):
    """The teahouse's big red parasol (the accent) over a bench spread with a red cloth."""
    out = []
    s = C.f / Z
    top = C(X, Y + 3.1, Z)
    rim = []
    for k in range(25):
        a = math.pi * k / 24
        rim.append(C(X - 1.35 * math.cos(a), Y + 2.3, Z - 1.35 * math.sin(a) * 0.9))
    for k in range(1, 24):
        a = math.pi + math.pi * k / 24
        rim.append(C(X - 1.35 * math.cos(a), Y + 2.3, Z - 1.35 * math.sin(a) * 0.9))
    can = hull(rim + [top])
    out.append(F(can, PAPER))
    out.append(accent(U, poly(can), bbox(can), seed, op=0.95, ang=-30, n=22, length=(6, 14), width=(1.5, 3)))
    under = [C(X - 1.35 * math.cos(math.pi * k / 24), Y + 2.3, Z - 1.35 * math.sin(math.pi * k / 24) * 0.9) for k in range(25)]
    ctr = C(X, Y + 2.55, Z)
    out.append(segs([(ctr, p) for p in under[::2]], 0.7, seed, 0, op=0.8))
    out.append(H(U, poly(under + [ctr]), 0, 1.8, 0.6, op=0.6, box=bbox(under + [ctr])))
    out.append(pen(can, 1.3, seed, 0.1, closed=True))
    pb = C(X, Y, Z)
    out.append(seg(ctr[0], ctr[1], pb[0], pb[1], max(1.2, 0.06 * s), seed, 0))
    # bench with the red cloth
    bz0, bz1 = Z - 0.9, Z + 0.9
    bt = [C(X - 0.6, Y + 0.45, bz0), C(X - 0.6, Y + 0.45, bz1), C(X + 0.0, Y + 0.45, bz1), C(X + 0.0, Y + 0.45, bz0)]
    bf = C.qx(X + 0.0, bz0, bz1, Y + 0.2, Y + 0.45) if X < 0 else C.qx(X - 0.6, bz0, bz1, Y + 0.2, Y + 0.45)
    out.append(F(bt, PAPER) + F(bf, PAPER) + accent(U, poly(bt) + " " + poly(bf), bbox(bt + bf), seed + 1, op=0.9, ang=0, n=8, length=(4, 10), width=(1, 2)))
    out.append(pen(bt, 1.0, seed, 0.05, True) + pen(bf, 1.0, seed, 0.05, True))
    for zz in (bz0 + 0.1, bz1 - 0.1):
        a, b = C(X - 0.3 if X > 0 else X - 0.0, Y + 0.2, zz), C(X - 0.3 if X > 0 else X - 0.0, Y, zz)
        out.append(seg(a[0], a[1], b[0], b[1], 1.2, seed, 0))
    return "".join(out)


@design("kyoto")
def kyoto(U):
    """Up the stone-paved Yasaka lane in Higashiyama on a still morning: wooden machiya with lattices, deep
    tiled eaves and paper lanterns stepping up the hill on both sides, a teahouse's red parasol (the accent),
    people in kimono, and at the top of the lane the five-storey Yasaka pagoda against the wooded hills."""
    s = 0.07
    C = Cam(f=480, cx=300, vpy=394, eye=1.6)

    def g(Z):
        return s * Z
    art = []
    gdef, gl = glass(U)
    art.append(gdef)
    art.append(cloud(U, 168, 96, 110, 18, 4) + cloud(U, 452, 140, 76, 12, 5))
    art.append(gulls([(410, 196, 6), (426, 184, 4)], 6))
    # Higashiyama: wooded hills behind the pagoda
    PZ, PX = 80.0, 0.5
    hill = []
    rr = random.Random(5)
    for k in range(15):
        x = 130 + k * 24
        y = 312 - 70 * math.sin(math.pi * (k / 14)) ** 0.7 + rr.uniform(-8, 8)
        hill.append(lobe(U, x, y, rr.uniform(22, 30), rr.uniform(15, 20), 900 + k, light=(-1, -1), w=1.0, dense=0.9))
    art.append(f'<g opacity="0.55">{"".join(hill)}</g>')
    # the pagoda
    px, pb = C(PX, 0, PZ)[0], C(PX, g(PZ) + 1.2, PZ)[1]
    art.append(pagoda(U, px, pb, C(PX, g(PZ) + 47, PZ)[1], 7))
    # a pine and a maple beside the pagoda
    x, yb = C(-8.5, g(70) + 1.0, 70)
    art.append(tree(U, x, yb, C.f * 13 / 70, C.f * 10 / 70, 41, light=(-1, -1), trunk_h=0.4, lobes=6, lw=1.1))
    x, yb = C(8.0, g(72) + 1.0, 72)
    art.append(tree(U, x, yb, C.f * 11 / 72, C.f * 9 / 72, 42, light=(-1, -1), trunk_h=0.4, lobes=5, lw=1.1))
    # the house across the head of the lane
    ZE = 62.0
    eq = C.qz(ZE, -6, 6, g(ZE), g(ZE) + 5.6)
    art.append(F(eq, PAPER) + tone(U, eq, 2, 80) + facade(U, quad_sub(eq, 0.1, 0.2, 0.9, 0.5), 6, 1, "slit", 3, w=0.6))
    es = [C(-6.5, g(ZE) + 5.6, ZE - 1.0), C(6.5, g(ZE) + 5.6, ZE - 1.0), C(6.5, g(ZE) + 6.3, ZE - 1.0), C(-6.5, g(ZE) + 6.3, ZE - 1.0)]
    art.append(F(es, PAPER) + H(U, es, 0, 1.4, 0.6) + sketch(es, 1.1, 4, 0.3) + sketch(eq, 1.0, 5, 0.3))
    # the machiya, far to near, both sides
    for sgn, sd0 in ((-1, 10), (1, 30)):
        z = 5.5
        rows = []
        rr = random.Random(sd0)
        i = 0
        while z < ZE - 0.5:
            w = min(ZE - 0.5 - z, rr.uniform(6.5, 9.5))
            rows.append((z, z + w, i))
            z += w
            i += 1
        for z0, z1, i in rows[::-1]:
            lv = 1 if sgn < 0 else 3
            art.append(machiya(U, C, sgn * 3.4, z0, z1, g, sd0 + i, gl, lvl=lv, door=rr.uniform(0.3, 0.7), lantern=(i % 2 == 0),
                               red_lantern=False, noren=True, sign=(i % 3 == 1)))
    # the lane: stone slabs, gutters, steps here and there
    Z0, Z1 = 8.6, ZE
    lane = [C(-3.4, g(Z0), Z0), C(-3.4, g(Z1), Z1), C(3.4, g(Z1), Z1), C(3.4, g(Z0), Z0)]
    art.append(F(lane, PAPER))
    rr = random.Random(12)
    ls = []
    z = Z0
    while z < Z1:
        dz = 0.55 * (1 + z / 40)
        ls.append((C(-3.0, g(z), z), C(3.0, g(z), z)))
        x = -3.0 + rr.uniform(0, 0.6)
        while x < 3.0:
            x2 = min(3.0, x + rr.uniform(0.6, 1.1))
            ls.append((C(x2, g(z), z), C(x2, g(z + dz), z + dz)))
            x = x2
        z += dz
    art.append(clipped(U("ln"), poly(lane), segs(ls, 0.65, 13, 0.1, op=0.6)))
    for X in (-3.0, 3.0):
        art.append(pen([C(X, g(Z0), Z0), C(X, g(Z1), Z1)], 1.2, 14, 0.05))
    for sgn in (-1, 1):
        gut = [C(sgn * 3.0, g(Z0), Z0), C(sgn * 3.0, g(Z1), Z1), C(sgn * 3.4, g(Z1), Z1), C(sgn * 3.4, g(Z0), Z0)]
        art.append(H(U, gut, 75, 2.0, 0.6, op=0.7))
    for zs in (13.0, 19.0, 27.0, 36.0):
        a, b = C(-3.0, g(zs), zs), C(3.0, g(zs), zs)
        st = [a, b, C(3.0, g(zs) + 0.16, zs + 0.01), C(-3.0, g(zs) + 0.16, zs + 0.01)]
        art.append(pen([a, b], 1.6, int(zs), 0.05) + H(U, [C(-3.0, g(zs), zs), C(3.0, g(zs), zs), C(3.0, g(zs + 0.8), zs + 0.8),
                                                            C(-3.0, g(zs + 0.8), zs + 0.8)], 0, 1.6, 0.6, op=0.5))
    # morning shadow of the left row across the lane
    sh = [C(-3.0, g(Z0), Z0), C(-3.0, g(Z1), Z1), C(-1.0, g(Z1), Z1), C(-0.4, g(Z0), Z0)]
    art.append(tone(U, sh, 1, 70))
    # life: the red parasol of a teahouse, people in kimono, a lamp
    art.append(nodate(U, C, 2.0, g(15.5), 15.5, 15))
    for X, z, sd, fl, par in ((-1.0, 17.5, 1, False, True), (-0.4, 18.4, 2, True, False), (1.0, 26, 3, False, False),
                              (-1.8, 31, 4, True, True), (0.4, 38, 5, False, False), (1.6, 44, 6, True, False), (-0.9, 51, 7, False, False)):
        x, yb = C(X, g(z), z)
        art.append(kimono(x, yb, C.f * 1.6 / z, 60 + sd, flip=fl, parasol=par))
    for X, z, sd, fl in ((-2.4, 22, 1, False), (2.6, 34, 2, True)):
        art.append(person3(C, X, g(z), z, 70 + sd, flip=fl))
    return plate(U, "kyoto", art, 91, frame=(300, 246, 262, 208))


# ================================================================ PARIS (line-art, City Sketches)
@design("paris", SKETCH)
def paris_sketch(U):
    """The Tower from the Debilly footbridge: the Pont d'Iéna striding across the Seine on its five arches,
    plane trees along the Quai Branly, a bateau-mouche flying the tricolour (the accent) on the river."""
    out = [ground_paper(U, 23)]
    pic = [(56, 56), (544, 56), (544, 468), (56, 468)]
    art = []
    art.append(cloud(U, 150, 112, 150, 28, 11) + cloud(U, 214, 168, 90, 15, 12) + cloud(U, 492, 126, 100, 20, 13))
    art.append(bird(250, 210, 7, 15) + bird(266, 198, 5, 16) + bird(470, 214, 6, 17))
    # the Tower on the Champ de Mars, its feet among the trees
    TX = 352
    art.append(eiffel(U, TX, 62, 330, 7))
    QY = 334           # far quay line
    rr = random.Random(3)
    trees = []
    for i, x in enumerate(list(range(48, 290, 19)) + list(range(410, 560, 19))):
        trees.append(lobe(U, x + rr.uniform(-3, 3), QY - 14 - rr.uniform(0, 6), rr.uniform(14, 18), rr.uniform(12, 15), 200 + i,
                          light=(-1, -1), w=1.2, dense=0.9))
    for i, x in enumerate(range(300, 410, 16)):
        trees.append(lobe(U, x, QY - 8, 10, 8, 260 + i, light=(-1, -1), w=1.0, dense=0.9))
    art.append("".join(trees))
    # quay wall
    qw = [(56, QY), (544, QY), (544, QY + 8), (56, QY + 8)]
    art.append(F(qw, PAPER) + H(U, qw, 0, 2.2, 0.7, op=0.7) + seg(56, QY, 544, QY, 1.6, 4, 0.2) + seg(56, QY + 8, 544, QY + 8, 1.2, 5, 0.2))
    # Pont d'Iéna: five segmental arches in elevation, parapet, cutwaters, the eagles at the far ends
    BY0, BY1 = 352, 396          # deck, springing line
    deck = [(56, BY0 - 9), (544, BY0 - 9), (544, BY1 + 10), (56, BY1 + 10)]
    art.append(F(deck, PAPER))
    spans = [(60, 140), (152, 236), (248, 352), (364, 448), (460, 540)]
    arches = []
    for x0, x1 in spans:
        rise = (x1 - x0) * 0.36
        pts = [(x0, BY1 + 12)] + [(lerp(x0, x1, t / 16), BY1 - rise * math.sin(math.pi * t / 16) ** 0.75) for t in range(17)] + [(x1, BY1 + 12)]
        arches.append(pts)
    art.append(clipped(U("bd"), poly(deck), H(U, deck, 0, 3.4, 0.6, op=0.45) + "".join(F(a, PAPER) for a in arches)))
    for i, a in enumerate(arches):
        art.append(clipped(U("ba"), poly(deck), H(U, a, 0, 2.0, 0.7, op=0.85) + pen(a[1:-1], 1.6, 30 + i, 0.05, smooth=True)))
    for (x0, x1), (x2, x3) in zip(spans, spans[1:]):
        xm = (x1 + x2) / 2
        cw = [(x1 + 1, BY1 + 10), (x1 + 1, BY1 - 4), (xm, BY1 - 10), (x2 - 1, BY1 - 4), (x2 - 1, BY1 + 10)]
        art.append(pen(cw, 1.1, int(xm), 0.05))
        art.append(f'<circle cx="{f1(xm)}" cy="{f1(BY0 + 3)}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>')
    art.append(seg(56, BY0 - 9, 544, BY0 - 9, 2.0, 6, 0.2) + seg(56, BY0 - 2, 544, BY0 - 2, 1.0, 7, 0.2) + seg(56, BY0 + 1, 544, BY0 + 1, 1.6, 8, 0.2))
    bal = [((x, BY0 - 8), (x, BY0 - 2.5)) for x in range(58, 544, 4)]
    art.append(segs(bal, 0.7, 9, 0))
    for x in (100, 196, 300, 406, 500):
        art.append(lamp(x, BY0 - 9, 36, 10 + x, "lantern", 1.5))
    # traffic and walkers on the bridge
    art.append(car(U, 150, BY0 - 9, 34, 12, flip=True, kind="classic"))
    art.append(person(232, BY0 - 9, 19, 13) + person(246, BY0 - 9, 18, 14, flip=True) + person(470, BY0 - 9, 18, 15, bag=True))
    art.append(cyclist(352, BY0 - 9, 20, 16))
    # the Seine
    art.append(ripples(U, 56, 544, BY1 + 10, 470, 41, dens=1.0, refl=[(x0 + 4, x1 - 4, 0.0) for x0, x1 in spans] + [(TX - 10, TX + 10, 0.6)],
                       skip=[(120, 150), (420, 440)], clip=poly([(56, BY1 + 10), (544, BY1 + 10), (544, 470), (56, 470)])))
    # bateau-mouche: long glazed cabin, open upper deck with passengers, the tricolour at the stern
    bx, by, L = 150, 432, 160
    hullp = [(bx - L / 2, by - 10), (bx + L / 2 + 14, by - 12), (bx + L / 2, by + 4), (bx - L / 2 + 6, by + 4)]
    cab = [(bx - L / 2 + 14, by - 10), (bx - L / 2 + 22, by - 30), (bx + L / 2 - 8, by - 30), (bx + L / 2 + 2, by - 11)]
    art.append(F(hullp, PAPER) + H(U, hullp, 0, 1.8, 0.8) + sketch(hullp, 1.8, 42, 0.8))
    art.append(F(cab, PAPER) + facade(U, [(bx - L / 2 + 22, by - 27), (bx + L / 2 - 8, by - 27), (bx + L / 2 - 6, by - 14), (bx - L / 2 + 18, by - 14)],
                                      16, 1, "dark", 43, mx=0.12, my=0.08) + sketch(cab, 1.5, 44, 0.6))
    art.append(seg(bx - L / 2 + 20, by - 33, bx + L / 2 - 6, by - 33, 1.4, 45, 0))
    art.append(segs([((x, by - 30), (x, by - 33)) for x in range(int(bx - L / 2 + 22), int(bx + L / 2 - 6), 6)], 0.8, 46, 0))
    for k, x in enumerate(range(int(bx - L / 2 + 34), int(bx + L / 2 - 20), 15)):
        art.append(person(x, by - 30, 12, 50 + k, flip=k % 2 == 1))
    art.append(flag(U, bx - L / 2 + 2, by - 44, 18, 11, 47))
    art.append(P(f"M {bx + L / 2 + 14} {by - 6} q 22 4 52 12 M {bx + L / 2 + 6} {by + 2} q 18 5 44 14 M {bx - L / 2} {by + 2} q -16 2 -34 1", 1.0, INK, 0.8))
    out.append(clipped(U("pic"), poly(pic), "".join(art)))
    out.append(sketch(pic, 2.6, 46, 1.4))
    out.append(border(U, 47, 47, 553, 553, 47, double=False, w=(1.2, 1.2)))
    from kitchen_ink import ribbon
    sz = name_size("Paris", 300, 60)
    out.append(ribbon(U("rb"), 300, 466, 300, 62, "Paris", DMS, sz, fill=PAPER, color=INK, bend=6, seed=48, text_dy=sz * 0.36))
    out.append(coords_line(300, 534, CITIES["paris"][1], rule_len=26))
    out.append(finish(U))
    return "".join(out)


# ================================================================ build
def main(slugs):
    for (coll, slug), fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save(coll, slug, fn(Ids(slug, "ies" if coll == SKETCH else "iea")))
        print("wrote", coll, slug)


if __name__ == "__main__":
    main(sys.argv[1:])
