"""Ink Cities, engraved edition (set C).

Ten more Ink Cities drawn in the manner of the Paris plate in ink_cities_fine.py: a rich pen-and-ink
engraving on warm paper, tonal hatching and cross-hatching that build the form and the air, a true street- or
shore-level perspective (a pinhole camera, `Cam` / `Cam2`), small people, trees, lamps and boats for life,
one faded-vermilion accent per plate, and soft vignetted edges dissolving into the paper (`soft_frame`, no
hard border). The name (DM Serif Display) and coordinates (DM Mono, ruled with diamonds) sit underneath,
exactly as on Paris.

Each plate has its own true viewpoint:
    miami          Ocean Drive face-on from Lummus Park: Art Deco hotels with eyebrows, towers and parasols, palms
    philadelphia   Independence Hall's tower over the square, between the elms
    austin         Congress Avenue looking up the hill to the Capitol dome
    sydney         the Harbour Bridge arch from the Dawes Point foreshore, ferries below
    rio            Sugarloaf over Botafogo bay from the wave-paved promenade
    atlanta        Midtown towers over the Piedmont Park lake under a live oak
    denver         Union Station closing 17th Street, the Front Range beyond
    seattle        a pier apron beside an old shed, a ferry crossing, Mount Rainier over Elliott Bay
    edinburgh      the castle on its rock above Princes Street Gardens
    los-angeles    a palm-lined street toward the hills and the observatory domes

Run from tools/designs:  python3 ink_engraved_c.py [slug ...]
"""
import math
import random
import sys

from common import DMS, save
from gouache import smooth_closed, smooth_open
from kitchen_ink import cr, clipped, nib, poly
from ink_cities_fine import (INK, PAPER, Cam, Ids, F, H, P, ST, T, XH, accent, bbox, bird, cloud, coords_line, cyclist,
                             f1, facade, finish, ground_paper, homog, hpat, lamp, lerp, lobe, name_size, palm, pen, person,
                             pt, ripples, seg, segs, sketch, soft_frame, tree, cone_tree, duck, bench, ferry, frigatebird,
                             granite_dome, pelican, scallop_pts, scallop_d, prism, mountain, flag, car)

COL = "ink-cities"
CITIES = {
    "miami": ("Miami", "25.7617° N · 80.1918° W"),
    "philadelphia": ("Philadelphia", "39.9526° N · 75.1652° W"),
    "austin": ("Austin", "30.2672° N · 97.7431° W"),
    "sydney": ("Sydney", "33.8688° S · 151.2093° E"),
    "rio": ("Rio de Janeiro", "22.9068° S · 43.1729° W"),
    "atlanta": ("Atlanta", "33.7490° N · 84.3880° W"),
    "denver": ("Denver", "39.7392° N · 104.9903° W"),
    "seattle": ("Seattle", "47.6062° N · 122.3321° W"),
    "edinburgh": ("Edinburgh", "55.9533° N · 3.1883° W"),
    "los-angeles": ("Los Angeles", "34.0522° N · 118.2437° W"),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Uids(Ids):
    """Unique ids per plate, prefixed so these never clash with the line-art plates on the same page."""
    def __call__(self, tag="u"):
        self.n += 1
        return f"iec-{self.slug}-{tag}{self.n}"


# ================================================================ camera + projection helpers
class Cam2(Cam):
    """Cam with a yaw (degrees, + turns the view to the right). World: X right, Y up, Z forward."""
    def __init__(self, f=250, cx=300, vpy=300, eye=1.6, yaw=0.0, pos=(0.0, 0.0)):
        super().__init__(f, cx, vpy, eye)
        a = math.radians(yaw)
        self.c, self.s = math.cos(a), math.sin(a)
        self.ox, self.oz = pos

    def rot(self, X, Z):
        X, Z = X - self.ox, Z - self.oz
        return X * self.c - Z * self.s, X * self.s + Z * self.c

    def __call__(self, X, Y, Z):
        x, z = self.rot(X, Z)
        z = max(z, 0.05)
        return (self.cx + self.f * x / z, self.vpy + self.f * (self.eye - Y) / z)

    def d(self, X, Z):
        return max(0.05, self.rot(X, Z)[1])

    def px(self, X, Z, size):
        """Screen size of `size` metres standing at (X, Z)."""
        return self.f * size / self.d(X, Z)


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def ppl(C, X, Z, seed, Y=0.0, h=1.72, **kw):
    x, y = C(X, Y, Z)
    return person(x, y, C.px(X, Z, h), seed, **kw)


def plamp(C, X, Z, seed, kind="globe", h=4.4):
    x, y = C(X, 0, Z)
    return lamp(x, y, C.px(X, Z, h), seed, kind, max(1.1, min(2.4, C.px(X, Z, 0.12))))


def ptree(U, C, X, Z, h, w, seed, light=(-1, -1), **kw):
    x, y = C(X, 0, Z)
    hp, wp = C.px(X, Z, h), C.px(X, Z, w)
    return tree(U, x, y, hp, wp, seed, light=light, lw=max(1.0, min(2.0, wp / 60)), **kw)


def ppalm(U, C, X, Z, h, seed, lean=0.1, fronds=9, span=1.0):
    x, y = C(X, 0, Z)
    hp = C.px(X, Z, h)
    return palm(U, x, y, hp, seed, lean=lean, fronds=fronds, span=span, w=max(1.0, min(1.8, hp / 120)))


def umbrella(U, C, X, Z, seed, r=1.25, rim=2.05, apex=2.6, acc=True):
    """A café parasol in perspective: lit top (vermilion gores), shaded underside, scalloped valance, pole."""
    rim_pts = [C(X + r * math.cos(a), rim, Z + r * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
    ap = C(X, apex, Z)
    hl = hull(rim_pts + [ap])
    out = [F(hl, PAPER)]
    if acc:
        gores = [poly([ap, rim_pts[i], rim_pts[(i + 1) % 16]]) for i in range(0, 16, 2)]
        out.append(accent(U, " ".join(gores), bbox(hl, 2), seed, op=0.95, ang=-70, n=6, length=(4, 9), width=(1, 2)))
    under = rim_pts
    out.append(F(under, INK, 0.55))
    out.append(H(U, hl, 70, 2.0, 0.6, span=(0.55, 1), dark=(hl[0][0] + 40, ap[1])))
    b = C(X, 0, Z)
    out.append(seg(ap[0], ap[1], b[0], b[1], max(0.9, C.px(X, Z, 0.07)), seed, 0))
    out.append(pen(hl, max(0.9, min(1.5, C.px(X, Z, 0.06))), seed, 0.1, closed=True))
    return "".join(out)


def car_rear(U, x, y, w, seed=1, acc=False, shade=True):
    """A small car seen from behind (or the front), wheels on y, width w px."""
    h = w * 0.62
    body = [(x - w * 0.5, y - h * 0.18), (x - w * 0.5, y - h * 0.52), (x - w * 0.36, y - h * 0.6), (x - w * 0.3, y - h * 0.95),
            (x + w * 0.3, y - h * 0.95), (x + w * 0.36, y - h * 0.6), (x + w * 0.5, y - h * 0.52), (x + w * 0.5, y - h * 0.18)]
    out = [F([(x - w * 0.46, y - h * 0.2), (x - w * 0.46, y), (x - w * 0.3, y), (x - w * 0.3, y - h * 0.2)], INK),
           F([(x + w * 0.46, y - h * 0.2), (x + w * 0.46, y), (x + w * 0.3, y), (x + w * 0.3, y - h * 0.2)], INK)]
    out.append(F(body, PAPER))
    if acc:
        out.append(accent(U, poly(body), bbox(body), seed, op=0.95, ang=-10, n=6, length=(4, 10), width=(1, 2)))
    glass = [(x - w * 0.27, y - h * 0.9), (x + w * 0.27, y - h * 0.9), (x + w * 0.32, y - h * 0.63), (x - w * 0.32, y - h * 0.63)]
    out.append(F(glass, INK, 0.8))
    if shade:
        out.append(H(U, body, 0, 1.6, 0.6, span=(0.0, 0.35), dark=(x, y)))
    out.append(F([(x - w * 0.45, y - h * 0.48), (x - w * 0.33, y - h * 0.48), (x - w * 0.33, y - h * 0.38), (x - w * 0.45, y - h * 0.38)], INK))
    out.append(F([(x + w * 0.45, y - h * 0.48), (x + w * 0.33, y - h * 0.48), (x + w * 0.33, y - h * 0.38), (x + w * 0.45, y - h * 0.38)], INK))
    out.append(pen(body, max(0.9, min(1.6, w / 22)), seed, 0.1, closed=True))
    out.append(F([(x - w * 0.55, y + 0.5), (x + w * 0.55, y + 0.5), (x + w * 0.45, y + h * 0.12), (x - w * 0.45, y + h * 0.12)], INK, 0.35))
    return "".join(out)


def coco_palm(U, x, base, h, seed, lean=0.12, fronds=13, span=1.0, light=-1, dark_fronds=True):
    """An engraved palm: curved, tapering ringed trunk shaded on the side away from the light, a crown of
    arching feathered fronds (leaflets hanging from each spine, darker underneath), dead fronds and nuts."""
    rnd = random.Random(seed)
    out = []
    tx, ty = x + lean * h, base - h
    ctrl = [(x, base), (x + lean * h * 0.15, base - h * 0.45), (x + lean * h * 0.55, base - h * 0.8), (tx, ty)]
    C_ = cr(ctrl, False, 2.5)
    n = len(C_)
    left, right = [], []
    for i, (px, py) in enumerate(C_):
        t = i / (n - 1)
        hw = lerp(h * 0.03, h * 0.019, t) + 0.8
        left.append((px - hw, py))
        right.append((px + hw, py))
    trunk = left + right[::-1]
    out.append(F(trunk, PAPER))
    rings = []
    step = max(2.2, h * 0.018)
    i = 0
    while i < n - 1:
        (lx, ly), (rx, ry) = left[i], right[i]
        rings.append(f"M {f1(lx)} {f1(ly)} Q {f1((lx + rx) / 2)} {f1(ly + step * 0.55)} {f1(rx)} {f1(ry)}")
        i += max(1, int(step / 2.5 * 1.4 + rnd.uniform(0, 1.5)))
    inner = P(" ".join(rings), max(0.6, min(1.0, h / 200)), INK, 0.6)
    shade_side = right if light < 0 else left
    sh = [(px, py) for px, py in C_]
    half = (sh + shade_side[::-1])
    inner += H(U, half, 90, max(1.3, h * 0.008), 0.7, wob=0.1, brk=0)
    out.append(clipped(U("tk"), poly(trunk), inner))
    out.append(pen(left, max(1.0, min(1.8, h / 120)), seed, 0.2, smooth=True))
    out.append(pen(right, max(1.1, min(2.0, h / 110)), seed + 1, 0.2, smooth=True))
    # fronds: a fan of arching feathered leaves, leaflets hanging from both sides of each spine; the side ones
    # long, the ones toward/away from us foreshortened, a few dead ones drooping under the crown
    angs = []
    for k in range(fronds):
        a = math.radians(-195 + 210 * (k + 0.5) / fronds + rnd.uniform(-7, 7))
        angs.append((a, False))
    if dark_fronds:
        angs += [(math.radians(rnd.uniform(60, 80)), True), (math.radians(rnd.uniform(100, 120)), True)]
    rnd.shuffle(angs)
    angs.sort(key=lambda q: q[1], reverse=True)
    for a, dead in angs:
        fore = rnd.uniform(0.55, 1.0) if abs(math.cos(a)) < 0.5 else rnd.uniform(0.85, 1.05)
        L = h * rnd.uniform(0.32, 0.4) * span * (0.45 if dead else fore)
        g = rnd.uniform(0.55, 0.85) * (1.3 if dead else 1)
        p0 = (tx, ty)
        dx, dy = math.cos(a), math.sin(a)
        p1 = (tx + dx * L * 0.52, ty + dy * L * 0.52 + g * L * 0.08)
        p2 = (tx + dx * L, ty + dy * L + g * L * 0.75)
        spine = cr([p0, p1, p2], False, max(1.9, h * 0.011))
        m = len(spine)
        lv, dk = [], []
        for i in range(2, m - 1):
            t = i / m
            sx, sy = spine[i]
            ax, ay = spine[i + 1][0] - spine[i - 1][0], spine[i + 1][1] - spine[i - 1][1]
            al = math.hypot(ax, ay) or 1
            ux, uy = ax / al, ay / al
            nx, ny = -uy, ux
            ll = L * 0.2 * math.sin(math.pi * min(1, 0.15 + t * 0.95)) + 1.2
            for sgn in (-1, 1):
                ex = sx + nx * ll * sgn * 0.35 + ux * ll * 0.45
                ey = sy + ny * ll * sgn * 0.35 + uy * ll * 0.45 + ll * 0.75
                mx_, my_ = (sx + ex) / 2 + nx * sgn * ll * 0.12, (sy + ey) / 2 - ll * 0.05
                (dk if (sgn * ny > 0 or dead) else lv).append(f"M {f1(sx)} {f1(sy)} Q {f1(mx_)} {f1(my_)} {f1(ex)} {f1(ey)}")
        if dk:
            out.append(P(" ".join(dk), max(0.6, min(1.1, h / 240)), INK, 0.95 if dead else 0.85))
        if lv:
            out.append(P(" ".join(lv), max(0.55, min(0.9, h / 300)), INK, 0.7))
        out.append(nib([p0, p1, p2], max(1.3, h * 0.011), taper=(1, 0.2), ramp=0.5, seed=seed + int(a * 10), color=INK))
    # nuts
    for k in range(3):
        out.append(f'<circle cx="{f1(tx + rnd.uniform(-1, 1) * h * 0.02)}" cy="{f1(ty + h * 0.02 + k * 0.4)}" r="{f1(max(1.4, h * 0.016))}" fill="{INK}"/>')
    return "".join(out)


def pcoco(U, C, X, Z, h, seed, **kw):
    x, y = C(X, 0, Z)
    return coco_palm(U, x, y, C.px(X, Z, h), seed, **kw)


def vis_faces(C, foot, y0, y1):
    """Visible vertical faces of a prism standing on footprint `foot` [(X, Z), ...]: list of
    (quad [TL, TR, BR, BL], (nx, nz), (a, b)) sorted far to near. The camera sits at the world origin."""
    cxm = sum(p[0] for p in foot) / len(foot)
    czm = sum(p[1] for p in foot) / len(foot)
    res = []
    n = len(foot)
    for i in range(n):
        a, b = foot[i], foot[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ez) or 1
        nx, nz = ez / L, -ex / L
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if (mx - cxm) * nx + (mz - czm) * nz < 0:
            nx, nz = -nx, -nz
        if (getattr(C, "ox", 0) - mx) * nx + (getattr(C, "oz", 0) - mz) * nz <= 0:
            continue
        # order so that TL is on the screen-left
        pa, pb = C(a[0], y0, a[1]), C(b[0], y0, b[1])
        if pa[0] > pb[0]:
            a, b = b, a
        q = [C(a[0], y1, a[1]), C(b[0], y1, b[1]), C(b[0], y0, b[1]), C(a[0], y0, a[1])]
        res.append((q, (nx, nz), (a, b), math.hypot(mx - getattr(C, "ox", 0), mz - getattr(C, "oz", 0))))
    res.sort(key=lambda r: -r[3])
    return [r[:3] for r in res]


def tone_of(nrm, light=(-0.6, -0.8)):
    """0 = full light .. 1 = deep shade, for a face with horizontal normal nrm and light coming from `light`."""
    lx, lz = light
    L = math.hypot(lx, lz)
    return max(0.0, min(1.0, (1 - (nrm[0] * lx + nrm[1] * lz) / L) / 2))


def shade(U, q, t, ang=90, seed=1, base=3.4):
    """Tonal engraving on a face: none for light, single hatch for half-tone, cross-hatch for deep shade."""
    if t < 0.3:
        return ""
    out = H(U, q, ang, lerp(base, 1.5, (t - 0.3) / 0.7), lerp(0.55, 0.85, t), wob=0.1, brk=0.03)
    if t > 0.62:
        out += H(U, q, ang - 70, lerp(3.6, 2.0, (t - 0.62) / 0.38), 0.6, wob=0.1, brk=0.05, op=0.85)
    return out


def qlines(q, vs, axis="h"):
    """Lines across a perspective quad at parameters vs (h: horizontal courses at v; v: verticals at u)."""
    m = homog(q)
    return [(m(0, v), m(1, v)) if axis == "h" else (m(v, 0), m(v, 1)) for v in vs]


def octagon(xc, zc, r, rot=22.5):
    R = r / math.cos(math.radians(22.5))
    return [(xc + R * math.cos(math.radians(rot + 45 * k)), zc + R * math.sin(math.radians(rot + 45 * k))) for k in range(8)]


def box(xa, xb, za, zb):
    return [(xa, za), (xb, za), (xb, zb), (xa, zb)]


def canopy(U, cx, base, h, w, seed, light=(-1, -1), lobe_r=26, trunk=True, dense=1.0, lw=1.4, shape=0.62):
    """A big broadleaf tree built like the Paris planes: a forked trunk, then many small scalloped foliage
    clumps packed into a rounded crown (back and top first), each ticked and hatched toward the shade."""
    rnd = random.Random(seed)
    out = []
    top = base - h
    ccy = top + h * shape * 0.5
    rx, ry = w / 2, h * shape / 2
    if trunk:
        tw = max(2.5, w * 0.05)
        tp = [(cx, base), (cx + rnd.uniform(-3, 3), base - h * 0.25), (cx + rnd.uniform(-5, 5), ccy + ry * 0.3)]
        out.append(nib(tp, tw * 2, taper=(1, 0.55), ramp=0.4, seed=seed, color=INK))
        for k in (-1, 1):
            out.append(nib([tp[1], (cx + k * rx * 0.35, ccy + ry * 0.5), (cx + k * rx * 0.6, ccy)], tw * 1.1, taper=(0.9, 0.2), seed=seed + k, color=INK))
    under = smooth_closed(scallop_pts(cx, ccy + ry * 0.1, rx * 0.86, ry * 0.84, seed + 99, 16, 0.08))
    out.append(F(under, INK, 0.8))
    lr = lobe_r
    spots = []
    rows = max(2, int(2 * ry / (lr * 1.15)))
    for j in range(rows + 1):
        v = -1 + 2 * j / rows
        half = rx * math.sqrt(max(0.0, 1 - v * v)) * 0.92
        y = ccy + v * ry * 0.82
        k = max(1, int(2 * half / (lr * 1.25)) + 1)
        for i in range(k):
            u = (i + 0.5) / k if k > 1 else 0.5
            x = cx - half + 2 * half * u + rnd.uniform(-lr * 0.25, lr * 0.25)
            spots.append((y + rnd.uniform(-lr * 0.3, lr * 0.3), x))
    spots.sort()
    for i, (y, x) in enumerate(spots):
        r = lr * rnd.uniform(0.95, 1.25)
        out.append(lobe(U, x, y, r, r * rnd.uniform(0.78, 0.9), seed * 17 + i, light=light, w=lw, dense=dense))
    return "".join(out)


def pcanopy(U, C, X, Z, h, w, seed, **kw):
    x, y = C(X, 0, Z)
    return canopy(U, x, y, C.px(X, Z, h), C.px(X, Z, w), seed, **kw)


def forest_fill(U, d, box, seed, r=5.0, light=(-1, -1), skip=None):
    """Cover a hill silhouette (path d) with rows of small scribbled foliage clumps, back to front."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [F(d, INK, 0.75)]
    lobes_ = []
    y = y0 + r * 0.4
    while y < y1 + r:
        x = x0 - r + rnd.uniform(0, r)
        while x < x1 + r:
            if skip is None or not skip(x, y):
                lobes_.append(lobe(U, x, y + rnd.uniform(-r * 0.3, r * 0.3), r * rnd.uniform(0.9, 1.25), r * rnd.uniform(0.7, 0.9),
                                   seed * 13 + len(lobes_), light=light, w=0.7, dense=1.1))
            x += r * rnd.uniform(1.2, 1.6)
        y += r * 0.95
    out.append(clipped(U("ff"), d, "".join(lobes_)))
    out.append(P(d, 1.4))
    return "".join(out)


def sky_rules(U, x0, x1, y0, y1, seed, op=0.3, g0=9.0, g1=3.6):
    """Faint engraved sky: horizontal rules, closer together toward the horizon."""
    ls = []
    y = y0
    while y < y1:
        t = (y - y0) / max(1, y1 - y0)
        ls.append(((x0, y), (x1, y)))
        y += lerp(g0, g1, t)
    return segs(ls, 0.6, seed, 0.15, op=op)


def plate(U, slug, art, seed, frame=(300, 252, 262, 222), expo=3.4, inset=0.24, name_y=503, coord_y=534):
    """Paper, the vignetted engraving, the name and coordinates underneath (the Paris layout)."""
    name, coords = CITIES[slug]
    cx, cy, rx, ry = frame
    out = [ground_paper(U, seed)]
    out.append(soft_frame(U, cx, cy, rx, ry, seed, "".join(art), expo=expo, inset=inset))
    out.append(T(300, name_y, name, DMS, name_size(name)))
    out.append(coords_line(300, coord_y, coords, rule_len=30, diamonds=True))
    out.append(finish(U))
    return "".join(out)


# ================================================================ MIAMI
def deco_front(U, C, x0, x1, ZF, h, seed, style="tower", floors=3, tower_h=6.5, tone=0.0):
    """An Ocean Drive Art Deco hotel front in the plane Z = ZF, nearly face-on: stuccoed and sunlit, ribbon
    windows under deep eyebrows (each throwing a hard shadow), a ground-floor terrace arcade, and one of three
    signature crowns: a finned central tower with porthole ('tower'), a stepped ziggurat parapet with racing
    stripes ('ziggurat'), or a rounded corner with wraparound eyebrows and a blade sign ('corner')."""
    rnd = random.Random(seed)
    out = []
    cx = (x0 + x1) / 2

    def q(xa, xb, ya, yb, dz=0.0):
        return C.qz(ZF - dz, xa, xb, ya, yb)
    wall = q(x0, x1, 0, h)
    out.append(F(wall, PAPER))
    out.append(ST(U, wall, int(abs(wall[1][0] - wall[0][0]) * 1.6), r=(0.3, 0.55), op=0.35))
    if tone:
        out.append(H(U, wall, 90, 3.4, 0.45, op=0.35 * tone, wob=0.05, brk=0.05))
    # storeys: ribbon windows with eyebrows
    fh = (h - 4.0) / floors
    wins, shadows, brows, mull = [], [], [], []
    for f_ in range(floors):
        yb = 4.0 + f_ * fh
        yt = yb + fh * 0.62
        spans = []
        if style == "tower":
            spans = [(x0 + 0.8, cx - 2.2), (cx + 2.2, x1 - 0.8)]
        elif style == "ziggurat":
            spans = [(x0 + 0.8, cx - 0.6), (cx + 0.6, x1 - 0.8)]
        else:
            spans = [(x0 + 0.6, x1 - 2.6)]
        for xa, xb in spans:
            wq = q(xa, xb, yb + 0.5, yt)
            wins.append(wq)
            n = max(2, int((xb - xa) / 1.25))
            mq = homog(wq)
            mull += [(mq(i / n, 0), mq(i / n, 1)) for i in range(1, n)]
            brow = [C(xa - 0.4, yt + 0.25, ZF), C(xb + 0.4, yt + 0.25, ZF), C(xb + 0.4, yt + 0.25, ZF - 0.7), C(xa - 0.4, yt + 0.25, ZF - 0.7)]
            brows.append(brow)
            shadows.append(q(xa - 0.3, xb + 0.3, yt - 0.55, yt + 0.25))
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.8"/>')
    out.append(segs(mull, 0.7, seed, 0, color=PAPER, op=0.85))
    for sq in shadows:
        out.append(H(U, sq, 0, 1.0, 0.6, wob=0.05, brk=0))
    for bw in brows:
        out.append(F(bw, PAPER) + pen([bw[3], bw[2]], 1.4, seed, 0.05) + pen([bw[0], bw[1]], 0.8, seed, 0.05))
    # ground floor terrace arcade
    n = max(3, int((x1 - x0) / 3.2))
    arc = []
    for i in range(n):
        xa, xb = x0 + (x1 - x0) * (i + 0.12) / n, x0 + (x1 - x0) * (i + 0.88) / n
        arc.append(arch_q(q(xa, xb, 0.0, 3.0), 0.3, 6) if style != "corner" else q(xa, xb, 0.0, 3.0))
    out.append(f'<path d="{" ".join(poly(a_) for a_ in arc)}" fill="{INK}" opacity="0.82"/>')
    cano = [C(x0, 3.4, ZF), C(x1, 3.4, ZF), C(x1, 3.4, ZF - 0.9), C(x0, 3.4, ZF - 0.9)]
    out.append(F(cano, PAPER) + H(U, q(x0, x1, 2.9, 3.4), 0, 1.0, 0.6) + pen([cano[3], cano[2]], 1.4, seed, 0.05))
    # parapet and crown
    if style == "tower":
        cap = q(x0, x1, h, h + 0.8)
        out.append(F(cap, PAPER) + segs(qlines(cap, [0.5]), 0.8, seed, 0) + pen(cap, 1.2, seed, 0.05, closed=True))
        tw = q(cx - 2.0, cx + 2.0, 3.4, h + tower_h, 0.4)
        out.append(F(tw, PAPER))
        side = [C(cx + 2.0, h + tower_h, ZF - 0.4), C(cx + 2.0, h + tower_h, ZF), C(cx + 2.0, 3.4, ZF), C(cx + 2.0, 3.4, ZF - 0.4)]
        out.append(F(side, PAPER) + H(U, side, 90, 1.2, 0.6))
        fins = [(C(cx + u, h + tower_h - 0.8, ZF - 0.4), C(cx + u, 4.2, ZF - 0.4)) for u in (-1.1, -0.37, 0.37, 1.1)]
        out.append(segs(fins, 1.5, seed, 0))
        out.append(H(U, q(cx - 1.6, cx + 1.6, 4.2, h + tower_h - 2.2, 0.4), 0, 1.4, 0.55, op=0.6))
        for k, (ya, wa) in enumerate(((h + tower_h, 1.4), (h + tower_h + 1.0, 0.8))):
            st = q(cx - wa, cx + wa, ya, ya + 1.0, 0.4)
            out.append(F(st, PAPER) + pen(st, 1.2, seed + k, 0.05, closed=True))
        a_, b_ = C(cx, h + tower_h + 2.0, ZF - 0.4), C(cx, h + tower_h + 4.2, ZF - 0.4)
        out.append(seg(a_[0], a_[1], b_[0], b_[1], 1.4, seed, 0))
        ring = [C(cx + 0.9 * math.cos(2 * math.pi * k / 16), h + tower_h - 2.6 + 0.9 * math.sin(2 * math.pi * k / 16), ZF - 0.4) for k in range(16)]
        out.append(F(ring, PAPER) + pen(ring, 1.2, seed, 0.05, closed=True) + F([C(cx + 0.55 * math.cos(2 * math.pi * k / 12), h + tower_h - 2.6 + 0.55 * math.sin(2 * math.pi * k / 12), ZF - 0.4) for k in range(12)], INK, 0.85))
        out.append(pen(tw, 1.5, seed, 0.05, closed=True))
    elif style == "ziggurat":
        for k in range(4):
            w_ = (x1 - x0) / 2 * (1 - 0.22 * k)
            st = q(cx - w_, cx + w_, h + k * 1.0, h + (k + 1) * 1.0)
            out.append(F(st, PAPER) + pen(st, 1.2, seed + k, 0.05, closed=True))
        out.append(segs([(C(x0, h - 0.6 - 0.45 * k, ZF), C(x1, h - 0.6 - 0.45 * k, ZF)) for k in range(3)], 1.1, seed, 0))
        out.append(segs([(C(cx + u, h + 3.6, ZF), C(cx + u, 4.2, ZF)) for u in (-0.3, 0.3)], 1.2, seed, 0))
        for xs_ in (x0 + 0.3, x1 - 0.3):
            fn = q(xs_ - 0.3, xs_ + 0.3, h, h + 2.4)
            out.append(F(fn, PAPER) + pen(fn, 1.0, seed, 0.05, closed=True))
    else:
        # rounded corner at x1 (curving away), wraparound brows, a blade sign
        R = 2.4
        cyl = []
        for k in range(9):
            a = math.pi / 2 * k / 8
            cyl.append((x1 - R + R * math.sin(a), ZF + R - R * math.cos(a)))
        rnd2 = [C(px_, h, pz_) for px_, pz_ in cyl] + [C(px_, 0, pz_) for px_, pz_ in cyl[::-1]]
        out.append(F(rnd2, PAPER) + H(U, rnd2, 90, (3.4, 1.0), 0.6, box=bbox(rnd2), dark=(rnd2[8][0], rnd2[8][1]), wob=0.05, brk=0))
        for f_ in range(floors):
            yt = 4.0 + f_ * fh + fh * 0.62
            out.append(pen([C(px_ + 0.4 * math.sin(math.pi / 2 * k / 8), yt + 0.25, pz_ - 0.6 * math.cos(math.pi / 2 * k / 8)) for k, (px_, pz_) in enumerate(cyl)], 1.4, seed, 0.05, smooth=True))
            out.append(pen([C(px_, yt - 0.1, pz_) for px_, pz_ in cyl], 3.0, seed, 0.05, op=0.85, smooth=True))
        out.append(pen([C(px_, h, pz_) for px_, pz_ in cyl], 1.6, seed, 0.05, smooth=True))
        cap = q(x0, x1 - R, h, h + 0.8)
        out.append(F(cap, PAPER) + pen(cap, 1.2, seed, 0.05, closed=True))
        bl = q(x1 - 3.4, x1 - 2.8, 5.0, h + 3.6, 1.6)
        out.append(F(bl, PAPER) + H(U, bl, 0, 1.6, 0.6, op=0.7) + pen(bl, 1.3, seed, 0.05, closed=True))
        dots = [C(x1 - 3.1, 5.6 + k * 0.8, ZF - 1.6) for k in range(int((h + 3.0 - 5.6) / 0.8))]
        out.append("".join(f'<circle cx="{f1(x_)}" cy="{f1(y_)}" r="0.9" fill="{INK}"/>' for x_, y_ in dots))
    out.append(pen([wall[0], wall[3]], 1.3, seed, 0.05) + pen([wall[1], wall[2]], 1.3, seed, 0.05) + pen([wall[0], wall[1]], 1.1, seed, 0.05))
    return "".join(out)


@design("miami")
def miami(U):
    """Ocean Drive on a bright morning, seen across the street from the edge of Lummus Park: a row of Art Deco
    hotels almost face-on (a finned tower with a porthole, a stepped ziggurat with racing stripes, a rounded
    corner with a blade sign), their eyebrows throwing hard shadows, vermilion parasols on the terraces,
    coconut palms framing the view, pelicans gliding over, strollers, a cyclist and a classic convertible."""
    C = Cam2(f=300, cx=300, vpy=296, eye=3.4, yaw=12)
    art = []
    HZ = C.vpy
    ZF = 30.0
    ZW0, ZR0, ZR1, ZN = 25.5, 17.5, 25.5, 13.0

    def gnd(Z0, Z1, Y):
        return [C(-0.68 * Z0, Y, Z0), C(1.62 * Z0, Y, Z0), C(1.62 * Z1, Y, Z1), C(-0.68 * Z1, Y, Z1)]

    def xs(Z, step):
        return [x for x in range(int(-0.68 * Z), int(1.62 * Z), step)]
    art.append(cloud(U, 470, 84, 120, 18, 5) + cloud(U, 150, 96, 80, 12, 8))
    # the hotels, right (far) to left (near), then the rest of the row receding to the right
    row = [(70, 92, 12.0, "ziggurat", 3), (52, 70, 11.5, "corner", 3), (30, 52, 13.0, "tower", 3), (12, 30, 11.0, "ziggurat", 3), (-6, 12, 12.5, "tower", 3),
           (-26, -6, 11.0, "corner", 3)]
    for x0, x1, h, st, fl in row:
        art.append(deco_front(U, C, x0, x1, ZF, h, 40 + int(x0), style=st, floors=fl, tower_h=6.0 if st == "tower" else 0,
                              tone=0.6 if st == "corner" else 0.0))
    # far sidewalk, terrace tables and parasols (the vermilion accent)
    walk = gnd(ZW0, ZF, 0.15)
    art.append(F(walk, PAPER) + segs([(C(x, 0.15, ZW0), C(x, 0.15, ZF)) for x in xs(ZW0, 2)], 0.5, 9, 0, op=0.5))
    art.append(pen([C(-0.68 * ZW0, 0.15, ZW0), C(1.62 * ZW0, 0.15, ZW0)], 1.4, 10, 0.1))
    for i, X in enumerate([-23, -16.5, -10, -3.5, 3, 9.5, 16, 22.5, 29, 35.5, 42, 48.5, 55, 61.5, 68, 74.5, 81, 87.5]):
        Z = ZF - 2.4
        if i % 2:
            tx_, ty_ = C(X, 0.75, Z)
            r = C.px(X, Z, 0.45)
            art.append(seg(tx_, ty_, tx_, C(X, 0, Z)[1], 1.0, i, 0))
            art.append(f'<ellipse cx="{f1(tx_)}" cy="{f1(ty_)}" rx="{f1(r)}" ry="{f1(r * 0.3)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
            art.append(ppl(C, X + 0.8, Z + 0.4, 70 + i, h=1.25))
        art.append(umbrella(U, C, X, Z, 60 + i, r=1.25, rim=2.1, apex=2.6))
    # Ocean Drive: road with a classic convertible and a cyclist
    road = gnd(ZR0, ZR1, 0)
    art.append(F(road, PAPER) + H(U, road, 0, 1.9, 0.55, op=0.55))
    dash = [poly([C(x, 0.01, 21.35), C(x + 2.2, 0.01, 21.35), C(x + 2.2, 0.01, 21.65), C(x, 0.01, 21.65)]) for x in xs(21.5, 6)]
    art.append(f'<path d="{" ".join(dash)}" fill="{PAPER}"/>')
    x, y = C(2.0, 0, 23.6)
    art.append(car(U, x, y, C.px(2.0, 23.6, 4.8), 91, flip=True, kind="classic"))
    x, y = C(28.0, 0, 19.5)
    art.append(car(U, x, y, C.px(28.0, 19.5, 4.4), 92, flip=False))
    x, y = C(-12, 0, 19.5)
    art.append(cyclist(x, y, C.px(-12, 19.5, 1.75), 93, flip=False))
    # near sidewalk, low coral-stone wall of the park
    nw = gnd(ZN, ZR0, 0.15)
    art.append(F(nw, PAPER) + segs([(C(x, 0.15, ZN), C(x, 0.15, ZR0)) for x in xs(ZN, 2)], 0.5, 11, 0, op=0.45))
    art.append(pen([C(-0.68 * ZR0, 0.15, ZR0), C(1.62 * ZR0, 0.15, ZR0)], 1.4, 12, 0.1))
    wall = C.qz(ZN, -0.68 * ZN, 1.62 * ZN, 0, 0.7)
    art.append(F(wall, PAPER) + ST(U, wall, 500, r=(0.4, 0.9), op=0.7) + H(U, wall, 0, 1.6, 0.5, op=0.5) + pen([wall[0], wall[1]], 1.4, 13, 0.1))
    for X, Z, sd, fl in ((-16, 15.5, 1, False), (-1, 15.0, 2, True), (10, 16.0, 3, False), (24, 14.6, 4, True), (38, 15.8, 5, False), (50, 15.2, 6, True)):
        art.append(ppl(C, X, Z, 80 + sd, Y=0.15, flip=fl, bag=sd == 3))
    # the park: lawn, sea-grape shrubs, lamps, palms
    lawn = gnd(2.6, ZN, 0.15)
    art.append(F(lawn, PAPER))
    rnd = random.Random(14)
    gl = []
    for i in range(1800):
        Z = math.exp(rnd.uniform(math.log(3.2), math.log(ZN - 0.1)))
        X = rnd.uniform(-1.2, 1.4) * Z
        x, y = C(X, 0.15, Z)
        L = C.px(X, Z, 0.11)
        gl.append(((x, y), (x + rnd.uniform(-1, 1), y - L)))
    art.append(clipped(U("lw"), poly(lawn), segs(gl, 0.6, 15, 0.2, op=0.75) + H(U, lawn, 0, (3.4, 2.0), 0.5, op=0.35, box=(0, HZ, 600, 600), dark=(300, 600))))
    # palm shadows pooled on the lawn
    spat, surl = hpat(U, 5, 1.7, 0.8)
    art.append(spat)
    for X, Z, w_ in ((-2.0, 8.8, 2.6), (8.8, 8.2, 2.4), (22.0, 11.2, 2.4)):
        art.append(F(smooth_closed([C(X + w_ * math.cos(2 * math.pi * k / 12) * random.Random(k + int(X)).uniform(0.8, 1.2), 0.16,
                                      Z + w_ * 0.45 * math.sin(2 * math.pi * k / 12)) for k in range(12)]), surl, 0.9))
    for X, Z in ((-9, 12.0), (-6.8, 12.2), (16, 11.8), (18.4, 12.0), (34, 12.2)):
        x, y = C(X, 0.15, Z)
        r = C.px(X, Z, 1.0)
        art.append(lobe(U, x, y - r * 0.55, r * 1.2, r * 0.75, 300 + int(X * 10), light=(-1, -1), w=1.0, dense=1.3))
    for X, Z in ((-1, 12.4), (27, 12.4)):
        x, y = C(X, 0.15, Z)
        art.append(lamp(x, y, C.px(X, Z, 4.4), 50 + int(X), "globe", 1.6))
    # palms: a mid row along the wall, two great ones framing the view
    for k, (X, Z, h, ln) in enumerate(((24, 11.6, 14.0, -0.05), (40, 12.4, 13.0, 0.08), (-12, 12.0, 12.5, -0.04))):
        art.append(pcoco(U, C, X, Z, h, 100 + k, lean=ln, span=1.0))
    for X, Z, sd, fl in ((1.5, 9.4, 7, False), (4.2, 10.6, 8, True), (12.5, 10.2, 9, False)):
        art.append(ppl(C, X, Z, 80 + sd, Y=0.15, flip=fl))
    x, y = C(-3.0, 0.15, 10.4)
    art.append(bench(x - 4, y, C.px(-3.0, 10.4, 1.8), 95))
    art.append(ppl(C, -2.4, 10.5, 96, Y=0.55, h=1.2))
    art.append(pcoco(U, C, -3.6, 7.0, 8.2, 120, lean=0.18, fronds=15, span=1.0))
    art.append(pcoco(U, C, 7.8, 6.4, 7.8, 121, lean=-0.22, fronds=15, span=1.0))
    # pelicans
    art.append(pelican(392, 132, 18, 98) + pelican(436, 152, 13, 99, 0.1) + pelican(350, 160, 10, 100, -0.05))
    return plate(U, "miami", art, 61)


# ================================================================ PHILADELPHIA
def brick_face(U, C, q, seed, rows=1.0, t=0.0, op=0.55):
    """A brick wall in perspective: fine course lines (rows per metre given by the quad height) plus tone."""
    out = [F(q, PAPER)]
    hpx = abs(q[3][1] - q[0][1]) + abs(q[2][1] - q[1][1])
    n = max(4, int(hpx / 2 / 2.1))
    out.append(segs(qlines(q, [k / n for k in range(1, n)]), 0.5, seed, 0, op=op))
    out.append(H(U, q, 80, 3.0, 0.5, op=0.35, wob=0.1, brk=0.1))
    out.append(shade(U, q, t, 90, seed))
    return "".join(out)


def sash_q(U, q, seed, rows=4, cols=3, lintel=True, w=1.0):
    """A sash window on a perspective wall quad: dark glass, glazing bars, stone lintel with keystone, sill."""
    m = homog(q)
    out = [F(q, INK, 0.85)]
    bars = [(m(i / cols, 0), m(i / cols, 1)) for i in range(1, cols)] + [(m(0, j / rows), m(1, j / rows)) for j in range(1, rows)]
    out.append(segs(bars, max(0.6, w * 0.7), seed, 0, color=PAPER, op=0.9))
    out.append(pen(q, w, seed, 0, closed=True, color=INK))
    if lintel:
        lt = [m(-0.15, -0.22), m(1.15, -0.22), m(1.12, 0), m(-0.12, 0)]
        out.append(F(lt, PAPER) + pen(lt, w * 0.9, seed, 0, closed=True))
        ks = [m(0.4, -0.27), m(0.6, -0.27), m(0.57, 0.04), m(0.43, 0.04)]
        out.append(F(ks, PAPER) + pen(ks, w * 0.8, seed, 0, closed=True))
    sl = [m(-0.12, 1.0), m(1.12, 1.0), m(1.12, 1.07), m(-0.12, 1.07)]
    out.append(F(sl, PAPER) + pen(sl, w * 0.9, seed, 0, closed=True))
    return "".join(out)


def arch_q(q, spring=0.4, n=10):
    """Points of a round-headed opening inside a perspective quad (u across, v down)."""
    m = homog(q)
    pts = [m(0, 1), m(0, spring)]
    for i in range(1, n):
        a = math.pi - math.pi * i / n
        pts.append(m(0.5 + 0.5 * math.cos(a), spring - spring * math.sin(a)))
    pts += [m(1, spring), m(1, 1)]
    return pts


def ring3(C, xc, y, zc, r, n=24, plane="z"):
    """A circle in 3D: in a plane of constant z (facing us) or horizontal (constant y)."""
    if plane == "z":
        return [C(xc + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), zc) for k in range(n)]
    return [C(xc + r * math.cos(2 * math.pi * k / n), y, zc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


@design("philadelphia")
def philadelphia(U):
    """Independence Hall from Independence Square: the brick hall and its tower, the white wooden steeple
    with its clock, framed by the square's big trees; brick paths, lanterns, visitors, a flag on the lawn."""
    TX, TZ = 4.0, 42.0                      # tower centre
    POS = (0.0, 9.0)
    yaw = math.degrees(math.atan2(TX - POS[0], TZ - POS[1]))
    C = Cam2(f=250, cx=300, vpy=390, eye=1.6, yaw=yaw, pos=POS)
    LIGHT = (0.55, -0.85)
    art = []
    art.append(cloud(U, 150, 120, 110, 20, 5) + cloud(U, 470, 150, 80, 14, 6))
    # --- the square: lawns and brick paths
    lawn = [C(-40, 0, 17), C(-40, 0, 46), C(50, 0, 46), C(50, 0, 17)]
    art.append(F(lawn, PAPER))
    rnd = random.Random(5)
    gl = []
    for i in range(900):
        X = rnd.uniform(-40, 50)
        Z = 9 + math.exp(rnd.uniform(math.log(8), math.log(37)))
        if abs(X - TX) < 3.0 or abs(Z - 27) < 1.6:
            continue
        x, y = C(X, 0, Z)
        if not (0 < x < 600):
            continue
        L = C.px(X, Z, 0.3)
        gl.append(((x, y), (x + rnd.uniform(-0.3, 0.3) * L, y - L)))
    art.append(segs(gl, 0.7, 7, 0.2, op=0.75))
    art.append(H(U, lawn, 0, (2.2, 3.4), 0.55, op=0.45, box=(0, 370, 600, 470), dark=(300, 470)))
    paths = [[C(TX - 2.4, 0.02, 16), C(TX - 2.4, 0.02, 40), C(TX + 2.4, 0.02, 40), C(TX + 2.4, 0.02, 16)],
             [C(-40, 0.02, 25.5), C(50, 0.02, 25.5), C(50, 0.02, 28.5), C(-40, 0.02, 28.5)],
             [C(-40, 0.02, 41), C(50, 0.02, 41), C(50, 0.02, 44), C(-40, 0.02, 44)]]
    for pq in paths:
        art.append(F(pq, PAPER))
    bl = []
    z = 16.0
    while z < 40:
        bl.append((C(TX - 2.4, 0.02, z), C(TX + 2.4, 0.02, z)))
        z += 0.6
    bl += [(C(TX + k, 0.02, 16), C(TX + k, 0.02, 40)) for k in (-1.2, 0, 1.2)]
    art.append(segs(bl, 0.6, 8, 0, op=0.6))
    for zz in (25.5, 28.5, 41, 44):
        art.append(pen([C(-40, 0.02, zz), C(50, 0.02, zz)], 1.0, 9, 0.1))
    for xx in (TX - 2.4, TX + 2.4):
        art.append(pen([C(xx, 0.02, 16), C(xx, 0.02, 40)], 1.2, 10, 0.1))
    art.append(segs([(C(X, 0.02, 25.5), C(X, 0.02, 28.5)) for X in range(-40, 50, 1)] + [(C(X, 0.02, 41), C(X, 0.02, 44)) for X in range(-40, 50, 1)], 0.5, 11, 0, op=0.5))
    # --- neighbours at either end (Old City Hall / Congress Hall), behind the trees
    for xa, xb in ((TX - 44, TX - 22), (TX + 22, TX + 44)):
        for q, nrm, _ in vis_faces(C, box(xa, xb, 50, 64), 0, 11):
            t = tone_of(nrm, LIGHT)
            art.append(brick_face(U, C, q, 20, t=t))
            if abs(nrm[1]) > 0.9:
                for k in range(5):
                    for y0 in (1.8, 6.6):
                        u0 = (k + 0.3) / 5
                        art.append(sash_q(U, quad_sub3(q, u0, 1 - (y0 + 3.4) / 11, u0 + 0.4 / 5 * 2, 1 - y0 / 11), 30 + k, rows=3, cols=2, w=0.8))
            art.append(sketch(q, 1.4, 21, 0.4))
        roof = [C(xa, 11, 50), C(xb, 11, 50), C(xb - 1, 14, 56), C(xa + 1, 14, 56)]
        art.append(F(roof, PAPER) + H(U, roof, 0, 1.8, 0.6, op=0.8) + sketch(roof, 1.3, 22, 0.4))
        cx_, cz_ = (xa + xb) / 2, 56
        for q, nrm, _ in vis_faces(C, octagon(cx_, cz_, 1.2), 14, 16.5):
            art.append(F(q, PAPER) + shade(U, q, tone_of(nrm, LIGHT), 90, 23) + sketch(q, 0.9, 23, 0.2))
        tip = C(cx_, 18.5, cz_)
        b0, b1 = C(cx_ - 1.3, 16.5, cz_), C(cx_ + 1.3, 16.5, cz_)
        art.append(F([b0, tip, b1], PAPER) + pen([b0, tip, b1], 1.1, 24, 0.1))
    # --- the hall: roof, end chimneys, the long front, then the tower
    X0, X1, ZF, EAVE = TX - 17, TX + 17, 44.0, 12.5
    roof = [C(X0, EAVE, ZF), C(X1, EAVE, ZF), C(X1, 17, 51), C(X0, 17, 51)]
    art.append(F(roof, PAPER) + H(U, roof, 0, 1.7, 0.65, op=0.9) + H(U, roof, 88, 4.0, 0.5, op=0.5) + sketch(roof, 1.5, 25, 0.5))
    bal = C.qz(51, X0 + 3, X1 - 3, 17, 18.1)
    art.append(F(bal, PAPER) + segs(qlines(bal, [k / 60 for k in range(1, 60)], "v"), 0.7, 26, 0) + sketch(bal, 1.2, 26, 0.3))
    for xa in (X0, X1 - 1.6):
        for zc in (47.5, 54.5):
            for q, nrm, _ in vis_faces(C, box(xa, xa + 1.6, zc - 0.9, zc + 0.9), EAVE, 20.5):
                art.append(brick_face(U, C, q, 27, t=tone_of(nrm, LIGHT)) + sketch(q, 1.1, 27, 0.3))
        arch_ = C.qz(51, xa, xa + 1.6, 17, 19.5)
        art.append(F(arch_, PAPER) + shade(U, arch_, 0.7, 90, 28) + sketch(arch_, 1.0, 28, 0.2))
    front = C.qz(ZF, X0, X1, 0, EAVE)
    art.append(brick_face(U, C, front, 29, t=0.1))
    # marble water table, belt course, cornice
    for ya, yb in ((0, 1.1), (6.0, 6.5)):
        bq = C.qz(ZF - 0.05, X0, X1, ya, yb)
        art.append(F(bq, PAPER) + sketch(bq, 0.9, 30, 0.2))
    cor = [C(X0 - 0.3, EAVE, ZF - 0.5), C(X1 + 0.3, EAVE, ZF - 0.5), C(X1, EAVE - 0.7, ZF), C(X0, EAVE - 0.7, ZF)]
    art.append(F(cor, PAPER) + H(U, cor, 0, 1.3, 0.6) + pen([cor[0], cor[1]], 1.8, 31, 0.1))
    # windows: five bays either side of the tower, two storeys, marble panels between
    for side in (-1, 1):
        for k in range(5):
            xc = TX + side * (6.2 + k * 2.45)
            for y0, y1 in ((1.9, 5.3), (7.3, 11.0)):
                art.append(sash_q(U, C.qz(ZF - 0.02, xc - 0.65, xc + 0.65, y0, y1), 40 + k, rows=4, cols=3, w=1.0))
            pnl = C.qz(ZF - 0.02, xc - 0.65, xc + 0.65, 5.75, 6.85)
            art.append(F(pnl, PAPER) + sketch(pnl, 0.7, 41, 0.1))
    art.append(sketch(front, 1.8, 32, 0.6))
    # tower (brick, three stages)
    tfoot = box(TX - 4.2, TX + 4.2, TZ - 2.0, ZF)
    for q, nrm, _ in vis_faces(C, tfoot, 0, 21):
        t = tone_of(nrm, LIGHT)
        art.append(brick_face(U, C, q, 33, t=t))
        art.append(sketch(q, 1.8, 34, 0.5))
    TF = TZ - 2.0
    for yy in (EAVE - 0.7, 17.0):
        band = C.qz(TF - 0.05, TX - 4.2, TX + 4.2, yy, yy + 0.6)
        art.append(F(band, PAPER) + H(U, band, 0, 1.4, 0.6) + sketch(band, 1.0, 35, 0.2))
    cor = [C(TX - 4.6, 21, TF - 0.5), C(TX + 4.6, 21, TF - 0.5), C(TX + 4.2, 20.3, TF), C(TX - 4.2, 20.3, TF)]
    art.append(F(cor, PAPER) + H(U, cor, 0, 1.2, 0.6) + pen([cor[0], cor[1]], 1.8, 36, 0.1))
    # door with fanlight, Palladian window, the tall arched window
    door = arch_q(C.qz(TF - 0.02, TX - 1.3, TX + 1.3, 0.1, 5.2), 0.42)
    art.append(F(door, INK, 0.9) + pen(door, 1.4, 37, 0, closed=True))
    surround = arch_q(C.qz(TF - 0.03, TX - 1.8, TX + 1.8, 0.1, 5.9), 0.42)
    art.append(pen(surround, 1.2, 38, 0, closed=False))
    pal = arch_q(C.qz(TF - 0.02, TX - 0.9, TX + 0.9, 7.2, 11.4), 0.3)
    art.append(F(pal, INK, 0.85) + pen(pal, 1.2, 39, 0, closed=True))
    for xs in (-1, 1):
        sq = C.qz(TF - 0.02, TX + xs * 1.25 - 0.5, TX + xs * 1.25 + 0.5, 8.6, 11.4)
        art.append(sash_q(U, sq, 50 + xs, rows=3, cols=2, lintel=False, w=0.9))
    tall = arch_q(C.qz(TF - 0.02, TX - 1.1, TX + 1.1, 13.2, 19.6), 0.32)
    art.append(F(tall, INK, 0.85) + pen(tall, 1.3, 51, 0, closed=True))
    art.append(segs([(pt(tall[0], tall[-1], 0.5), pt(tall[0], tall[-1], 0.5)[:1] + (C(TX, 18.3, TF)[1],))], 0.9, 52, 0, color=PAPER))
    # --- the white wooden steeple
    sc = TZ
    sqf = box(TX - 3.3, TX + 3.3, sc - 3.3, sc + 3.3)
    for q, nrm, _ in vis_faces(C, sqf, 21, 26.3):
        t = tone_of(nrm, LIGHT)
        art.append(F(q, PAPER) + shade(U, q, t * 0.85, 90, 53) + sketch(q, 1.5, 54, 0.4))
        m = homog(q)
        art.append(segs([(m(0.08, 0), m(0.08, 1)), (m(0.92, 0), m(0.92, 1))], 0.9, 55, 0))
    clock = ring3(C, TX, 23.7, sc - 3.32, 1.35)
    art.append(F(clock, PAPER) + pen(clock, 1.5, 56, 0, closed=True))
    cc = C(TX, 23.7, sc - 3.32)
    r_ = C.px(TX, sc, 1.35)
    ticks = [((cc[0] + math.cos(a) * r_ * 0.78, cc[1] + math.sin(a) * r_ * 0.78), (cc[0] + math.cos(a) * r_ * 0.92, cc[1] + math.sin(a) * r_ * 0.92))
             for a in [k * math.pi / 6 for k in range(12)]]
    art.append(segs(ticks, 0.8, 57, 0) + P(f"M {f1(cc[0])} {f1(cc[1])} l {f1(-r_ * 0.35)} {f1(-r_ * 0.35)} M {f1(cc[0])} {f1(cc[1])} l {f1(r_ * 0.05)} {f1(-r_ * 0.62)}", 1.1))
    def ledge(y, r, seed, urns=True, h=0.5):
        out = []
        for q, nrm, _ in vis_faces(C, octagon(TX, sc, r) if r < 3.4 else box(TX - r, TX + r, sc - r, sc + r), y, y + h):
            out.append(F(q, PAPER) + H(U, q, 0, 1.2, 0.6) + sketch(q, 1.1, seed, 0.2))
        if urns:
            for k in range(8):
                a = math.radians(22.5 + 45 * k)
                X_, Z_ = TX + r * 1.05 * math.cos(a), sc + r * 1.05 * math.sin(a)
                if Z_ > sc + 0.3:
                    continue
                ux, uy = C(X_, y + h, Z_)
                s_ = C.px(X_, Z_, 0.55)
                out.append(F(smooth_closed([(ux - s_ * 0.35, uy), (ux + s_ * 0.35, uy), (ux + s_ * 0.45, uy - s_ * 0.6), (ux, uy - s_ * 1.1),
                                            (ux - s_ * 0.45, uy - s_ * 0.6)]), INK, 0.9))
        return "".join(out)
    art.append(ledge(26.3, 3.55, 58, urns=True, h=0.55))
    # octagonal belfry with arched openings
    for q, nrm, _ in vis_faces(C, octagon(TX, sc, 2.7), 26.85, 32.0):
        t = tone_of(nrm, LIGHT)
        art.append(F(q, PAPER) + shade(U, q, t * 0.8, 90, 59))
        op_ = arch_q(quad_sub3(q, 0.22, 0.12, 0.78, 0.9), 0.35)
        art.append(F(op_, INK, 0.88) + pen(op_, 1.0, 60, 0, closed=True))
        art.append(sketch(q, 1.4, 61, 0.3))
    art.append(ledge(32.0, 2.95, 62, urns=True, h=0.45))
    for q, nrm, _ in vis_faces(C, octagon(TX, sc, 1.9), 32.45, 35.4):
        t = tone_of(nrm, LIGHT)
        art.append(F(q, PAPER) + shade(U, q, t * 0.8, 90, 63))
        m = homog(q)
        ox, oy = m(0.5, 0.45)
        rr = max(1.4, abs(q[1][0] - q[0][0]) * 0.22)
        art.append(f'<ellipse cx="{f1(ox)}" cy="{f1(oy)}" rx="{f1(rr)}" ry="{f1(rr * 1.2)}" fill="{INK}" opacity="0.85"/>')
        art.append(sketch(q, 1.2, 64, 0.2))
    art.append(ledge(35.4, 2.05, 65, urns=False, h=0.35))
    # bell dome, lantern, finial, weathervane
    prof = [(1.9, 35.75), (1.85, 36.6), (1.55, 37.5), (1.0, 38.2), (0.55, 38.6)]
    L_ = [C(TX - r, y, sc) for r, y in prof]
    R_ = [C(TX + r, y, sc) for r, y in prof]
    dome = L_ + R_[::-1]
    art.append(F(dome, PAPER) + clipped(U("dm"), poly(dome), H(U, dome, 90, 1.5, 0.7, span=(0.55, 1), dark=(R_[0][0] + 4, R_[0][1])) +
                                         segs([(C(TX + r * k, y, sc), C(TX + r * k, prof[-1][1], sc)) for k in (-0.5, 0, 0.5) for r, y in prof[:1]], 0.6, 66, 0))
               + pen(L_, 1.4, 67, 0.1, smooth=True) + pen(R_, 1.6, 68, 0.1, smooth=True))
    lan = C.qz(sc, TX - 0.5, TX + 0.5, 38.6, 40.6)
    art.append(F(lan, PAPER) + F(C.qz(sc, TX - 0.25, TX + 0.25, 38.9, 40.2), INK, 0.85) + sketch(lan, 1.1, 69, 0.2))
    cap = [C(TX - 0.7, 40.6, sc), C(TX, 41.6, sc), C(TX + 0.7, 40.6, sc)]
    art.append(F(cap, PAPER) + pen(cap, 1.2, 70, 0))
    tip0, tip1 = C(TX, 41.6, sc), C(TX, 45.5, sc)
    art.append(nib([tip0, tip1], 2.0, taper=(1, 0.3), ramp=0.5, seed=71, color=INK))
    ball = C(TX, 42.6, sc)
    art.append(f'<circle cx="{f1(ball[0])}" cy="{f1(ball[1])}" r="{f1(C.px(TX, sc, 0.28))}" fill="{INK}"/>')
    vy = C(TX, 44.6, sc)
    art.append(nib([(vy[0] - 6, vy[1]), (vy[0] + 7, vy[1] - 1)], 1.6, taper=(0.4, 1), seed=72, color=INK)
               + F([(vy[0] + 7, vy[1] - 4), (vy[0] + 11, vy[1] - 1), (vy[0] + 7, vy[1] + 2)], INK))
    # --- life in the square: lanterns, benches, visitors, the flag, the big trees
    for z in (37, 31.5):
        for xs in (-1, 1):
            art.append(plamp(C, TX + xs * 3.2, z, 80 + int(z) + xs, "lantern", 3.8))
    for X, Z, sd, fl in ((TX - 0.6, 37, 1, False), (TX + 0.9, 33, 2, True), (TX - 0.4, 24, 3, False), (TX + 0.5, 19, 4, True),
                         (TX - 9, 27, 5, False), (TX + 12, 26.8, 6, True), (TX + 14, 27.2, 7, False), (TX - 20, 42.5, 8, True),
                         (TX + 20, 42.6, 9, False), (TX + 1.0, 21, 10, False), (TX - 3, 26.5, 11, True)):
        art.append(ppl(C, X, Z, 90 + sd, Y=0.02, flip=fl, bag=sd in (3, 7)))
    for X, Z in ((TX - 6, 29.5), (TX + 9, 29.5)):
        x, y = C(X, 0, Z)
        art.append(bench(x - C.px(X, Z, 0.9), y, C.px(X, Z, 1.8), 110 + int(X)))
    FX, FZ = TX - 11, 37
    fx, fy = C(FX, 0, FZ)
    ph = C.px(FX, FZ, 10)
    art.append(nib([(fx, fy), (fx, fy - ph)], max(1.4, C.px(FX, FZ, 0.14)), taper=(1, 0.6), seed=112, color=INK))
    art.append(us_flag(U, fx, fy - ph + 1, C.px(FX, FZ, 2.4), C.px(FX, FZ, 1.4), 113))
    for X, Z, h, w, sd in ((-20, 40, 18, 14, 1), (28, 42, 19, 15, 2), (-9, 23, 17, 12, 3), (17, 24, 17.5, 12.5, 4)):
        art.append(pcanopy(U, C, X, Z, h, w, 500 + sd, light=(1, -1), lobe_r=max(12, C.px(X, Z, 1.6))))
    art.append(bird(250, 128, 6, 120) + bird(268, 112, 5, 121) + bird(390, 96, 5, 122))
    return plate(U, "philadelphia", art, 71)


def quad_sub3(q, u0, v0, u1, v1):
    m = homog(q)
    return [m(u0, v0), m(u1, v0), m(u1, v1), m(u0, v1)]


def us_flag(U, x, y, w, h, seed):
    """A small waving flag with the canton dark and the stripes in the vermilion accent."""
    def at(u, v):
        return (x + u * w, y + v * h + math.sin(u * 5.5 + 0.4) * h * 0.12 * u)
    outline = [at(u / 10, 0) for u in range(11)] + [at(1 - u / 10, 1) for u in range(11)]
    out = [F(outline, PAPER)]
    stripes = []
    for k in range(0, 7, 2):
        v0, v1 = k / 7, (k + 1) / 7
        stripes.append(poly([at(u / 10, v0) for u in range(11)] + [at(1 - u / 10, v1) for u in range(11)]))
    out.append(accent(U, " ".join(stripes), bbox(outline, 2), seed, op=0.95, ang=0, n=8, length=(4, 9), width=(1, 2)))
    out.append(F([at(u / 10, 0) for u in range(5)] + [at(0.4 - u / 10, 4 / 7) for u in range(5)], INK, 0.85))
    out.append(pen(outline, 1.0, seed, 0, closed=True))
    return "".join(out)


# ================================================================ AUSTIN
def commercial(U, C, X, Z0, Z1, Hh, seed, gy, floors=3, t=0.0, arch=True, awning=False, depth=14.0, end=True, ang=75):
    """A 19th-century Congress Avenue commercial front in the plane X: storefront glass between iron
    pilasters, tall arched (or flat-headed) windows, a bracketed cornice, and the bare end wall toward us."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1
    b0, b1 = gy(Z0), gy(Z1)
    top = b0 + Hh
    out = []
    if end:
        ef = [C(X - sg * depth, top, Z0), C(X, top, Z0), C(X, b0, Z0), C(X - sg * depth, b0, Z0)]
        out.append(F(ef, PAPER) + shade(U, ef, 0.55, 90, seed) + sketch(ef, 1.2, seed, 0.3))
    wall = [C(X, top, Z0), C(X, top, Z1), C(X, b1, Z1), C(X, b0, Z0)]
    out.append(F(wall, PAPER))
    m = homog(wall)
    L = Z1 - Z0
    nb = max(2, int(round(L / 2.8)))
    # storey courses
    out.append(segs([(m(0, v), m(1, v)) for v in [k / 18 for k in range(2, 18, 2)]], 0.5, seed, 0, op=0.4))
    # upper windows
    wins = []
    fh = (Hh - 5.0) / max(1, floors - 1)
    for j in range(floors - 1):
        ya = 5.4 + j * fh
        yb = ya + fh * 0.62
        for i in range(nb):
            u0, u1 = (i + 0.27) / nb, (i + 0.73) / nb
            q = [m(u0, 1 - yb / Hh), m(u1, 1 - yb / Hh), m(u1, 1 - ya / Hh), m(u0, 1 - ya / Hh)]
            if abs(q[1][0] - q[0][0]) < 1.6:
                continue
            wins.append(arch_q(q, 0.3, 6) if arch else q)
    if wins:
        out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.82"/>')
        out.append(P(" ".join(poly(w) for w in wins), 0.8))
    # storefronts
    sf = []
    for i in range(nb):
        sf.append([m((i + 0.12) / nb, 1 - 3.6 / Hh), m((i + 0.88) / nb, 1 - 3.6 / Hh), m((i + 0.88) / nb, 1 - 0.3 / Hh),
                   m((i + 0.12) / nb, 1 - 0.3 / Hh)])
    out.append(f'<path d="{" ".join(poly(w) for w in sf)}" fill="{INK}" opacity="0.78"/>')
    out.append(segs([(m(i / nb, 1 - 4.4 / Hh), m(i / nb, 1)) for i in range(nb + 1)], 1.0, seed, 0))
    out.append(segs([(m(0, 1 - 4.4 / Hh), m(1, 1 - 4.4 / Hh)), (m(0, 1 - 4.0 / Hh), m(1, 1 - 4.0 / Hh))], 1.0, seed, 0))
    if awning:
        aw = [C(X, b0 + 4.0, Z0 + 0.4), C(X, b0 + 4.0, Z1 - 0.4), C(X + sg * 1.8, b0 + 3.2, Z1 - 0.4), C(X + sg * 1.8, b0 + 3.2, Z0 + 0.4)]
        out.append(F(aw, PAPER) + H(U, aw, 15, 1.8, 0.6) + sketch(aw, 1.0, seed, 0.2))
    out.append(shade(U, wall, t, ang, seed))
    # cornice with brackets
    cor = [C(X, top - 0.9, Z0), C(X, top - 0.9, Z1), C(X + sg * 0.9, top, Z1), C(X + sg * 0.9, top, Z0)]
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.4, 0.6, op=0.9))
    br = []
    z = Z0 + 0.4
    while z < Z1:
        br.append(poly([C(X, top - 0.9, z), C(X, top - 0.9, z + 0.3), C(X, top - 1.6, z + 0.3), C(X, top - 1.6, z)]))
        z += 1.2
    out.append(f'<path d="{" ".join(br)}" fill="{INK}" opacity="0.85"/>')
    out.append(pen([cor[3], cor[2]], 1.5, seed, 0.1))
    if rnd.random() < 0.5:
        pd = [C(X, top, (Z0 + Z1) / 2 - L * 0.18), C(X, top + 1.6, (Z0 + Z1) / 2), C(X, top, (Z0 + Z1) / 2 + L * 0.18)]
        out.append(F(pd, PAPER) + pen(pd, 1.2, seed, 0.1))
    out.append(pen([C(X, b0, Z0), C(X, top, Z0)], 1.8, seed, 0.1))
    return "".join(out)


def tower_block(U, C, foot, y0, y1, seed, light, cols_per_m=0.45, rows_per_m=0.28, crown=None):
    out = []
    for q, nrm, (a, b) in vis_faces(C, foot, y0, y1):
        t = tone_of(nrm, light)
        w = math.hypot(b[0] - a[0], b[1] - a[1])
        out.append(F(q, PAPER))
        out.append(facade(U, q, max(2, int(w * cols_per_m)), max(3, int((y1 - y0) * rows_per_m)), "grid", seed, dark_p=0.12, w=0.6))
        out.append(shade(U, q, t, 90, seed))
        out.append(sketch(q, 1.3, seed, 0.4))
    return "".join(out)


def capitol(U, C, Zf, base, seed):
    """The Texas Capitol in elevation: wings, central pavilion and portico with pediment, the two-tier
    colonnaded drum, ribbed dome with its windows, lantern and the statue on top. Light from the left."""
    out = []
    def Q(x0, x1, y0, y1, z=Zf):
        return C.qz(z, x0, x1, base + y0, base + y1)
    # wings and their hipped pavilions
    for sgn in (-1, 1):
        wx0, wx1 = sorted((sgn * 22, sgn * 84))
        wq = Q(wx0, wx1, 0, 22, Zf + 6)
        out.append(F(wq, PAPER) + facade(U, wq, 22, 4, "pane", seed + sgn, dark_p=0.4, w=0.6, my=0.3))
        out.append(H(U, wq, 0, 2.8, 0.5, op=0.5))
        out.append(sketch(wq, 1.2, seed, 0.3))
        rf = [C(wx0, base + 22, Zf + 6), C(wx1, base + 22, Zf + 6), C(wx1 - sgn * 0, base + 25, Zf + 12), C(wx0, base + 25, Zf + 12)]
        out.append(F(rf, PAPER) + H(U, rf, 0, 1.5, 0.6) + sketch(rf, 1.0, seed, 0.2))
        px0, px1 = sorted((sgn * 60, sgn * 76))
        pq = Q(px0, px1, 0, 25, Zf + 4)
        out.append(F(pq, PAPER) + facade(U, pq, 4, 4, "pane", seed + 3, dark_p=0.4, w=0.6) + sketch(pq, 1.2, seed, 0.3))
        hip = [C(px0, base + 25, Zf + 4), C((px0 + px1) / 2, base + 31, Zf + 8), C(px1, base + 25, Zf + 4)]
        out.append(F(hip, PAPER) + H(U, hip, 0, 1.3, 0.6) + pen(hip, 1.2, seed, 0.1))
    # central pavilion
    cq = Q(-22, 22, 0, 26)
    out.append(F(cq, PAPER) + facade(U, cq, 12, 4, "pane", seed + 5, dark_p=0.45, w=0.7, my=0.28) + H(U, cq, 0, 2.4, 0.5, op=0.45))
    out.append(sketch(cq, 1.5, seed, 0.4))
    # portico: four columns, pediment
    pt_ = Q(-9, 9, 0, 21, Zf - 6)
    out.append(F(pt_, INK, 0.75))
    cols = []
    for k in range(5):
        xk = -9 + k * 4.5
        cols.append(Q(xk - 0.8, xk + 0.8, 4, 20, Zf - 6))
    for q in cols:
        out.append(F(q, PAPER) + H(U, q, 90, 1.3, 0.5, span=(0.6, 1), dark=(q[1][0] + 3, q[1][1])) + sketch(q, 0.9, seed, 0.1))
    ent = Q(-10, 10, 20, 22.5, Zf - 6)
    out.append(F(ent, PAPER) + H(U, ent, 0, 1.2, 0.5) + sketch(ent, 1.2, seed, 0.2))
    ped = [C(-10.5, base + 22.5, Zf - 6), C(0, base + 28, Zf - 6), C(10.5, base + 22.5, Zf - 6)]
    out.append(F(ped, PAPER) + H(U, ped, 0, 1.6, 0.5, op=0.6) + pen(ped, 1.5, seed, 0.1))
    stp = Q(-12, 12, 0, 4, Zf - 7)
    out.append(F(stp, PAPER) + segs(qlines(stp, [k / 8 for k in range(1, 8)]), 0.6, seed, 0) + sketch(stp, 1.0, seed, 0.2))
    # drum: lower colonnade, upper colonnade
    DZ = Zf + 18
    for y0, y1, r, n, seed2 in ((28, 41, 17, 16, 1), (41, 52, 15, 14, 2)):
        q = C.qz(DZ, -r, r, base + y0, base + y1)
        out.append(F(q, PAPER))
        lines = []
        for k in range(n):
            a = math.pi * (k + 0.5) / n
            xk = -r * math.cos(a)
            lines.append((C(xk, base + y0 + 1.2, DZ), C(xk, base + y1 - 1.6, DZ)))
        win = []
        for k in range(n - 1):
            a0, a1 = math.pi * (k + 0.5) / n, math.pi * (k + 1.5) / n
            xa, xb = -r * math.cos(a0), -r * math.cos(a1)
            if xb - xa < 0.9:
                continue
            win.append(arch_q(C.qz(DZ, xa + (xb - xa) * 0.28, xb - (xb - xa) * 0.28, base + y0 + 3, base + y1 - 3), 0.3, 6))
        out.append(f'<path d="{" ".join(poly(w) for w in win)}" fill="{INK}" opacity="0.8"/>')
        out.append(segs(lines, 1.1, seed + seed2, 0))
        out.append(H(U, q, 90, 1.4, 0.6, span=(0.68, 1), dark=(q[1][0] + 10, q[1][1])))
        cap = [C(-r - 0.8, base + y1, DZ), C(r + 0.8, base + y1, DZ), C(r + 0.8, base + y1 - 1.2, DZ), C(-r - 0.8, base + y1 - 1.2, DZ)]
        out.append(F(cap, PAPER) + H(U, cap, 0, 1.2, 0.6) + sketch(cap, 1.2, seed, 0.2))
        out.append(pen([q[0], q[3]], 1.6, seed, 0.1) + pen([q[1], q[2]], 1.8, seed, 0.1))
    # dome (slightly pointed), ribs, windows
    prof = [(14.5, 52), (14.4, 56), (13.6, 61), (12.0, 66), (9.6, 70.5), (6.6, 74), (3.6, 76.4), (2.0, 77.2)]
    Lp = [C(-r, base + y, DZ) for r, y in prof]
    Rp = [C(r, base + y, DZ) for r, y in prof]
    dome = Lp + Rp[::-1]
    inner = H(U, dome, 90, 1.5, 0.7, span=(0.62, 1), dark=(Rp[0][0] + 10, Rp[0][1]))
    ribs = []
    for k in range(1, 12):
        a = math.pi * k / 12
        ribs.append(smooth_open([C(-r * math.cos(a), base + y, DZ) for r, y in prof]))
    inner += P(" ".join(ribs), 0.8, INK, 0.9)
    wins = []
    for k in range(12):
        a = math.pi * (k + 0.5) / 12
        for r0, y0 in ((13.9, 58.5), (11.0, 67.5)):
            x = -r0 * math.cos(a)
            wx, wy = C(x, base + y0, DZ)
            sz = C.px(0, DZ, 0.75) * math.sin(a) + 0.4
            wins.append(f'<ellipse cx="{f1(wx)}" cy="{f1(wy)}" rx="{f1(sz)}" ry="{f1(C.px(0, DZ, 1.0))}"/>')
    inner += f'<g fill="{INK}" opacity="0.85">{"".join(wins)}</g>'
    out.append(F(dome, PAPER) + clipped(U("dm"), poly(dome), inner) + pen(Lp, 1.6, seed, 0.1, smooth=True) + pen(Rp, 1.9, seed + 1, 0.1, smooth=True))
    # lantern, small dome, statue
    lq = C.qz(DZ, -2.4, 2.4, base + 77.2, base + 83)
    out.append(F(lq, PAPER) + segs(qlines(lq, [k / 6 for k in range(1, 6)], "v"), 0.9, seed, 0) + H(U, lq, 90, 1.3, 0.6, span=(0.6, 1), dark=(lq[1][0] + 4, lq[1][1])) + sketch(lq, 1.2, seed, 0.2))
    sd_ = [C(-2.8, base + 83, DZ), C(-2.0, base + 85, DZ), C(0, base + 86.2, DZ), C(2.0, base + 85, DZ), C(2.8, base + 83, DZ)]
    out.append(F(sd_, PAPER) + pen(sd_, 1.3, seed, 0.1, smooth=True))
    sx, sy = C(0, base + 86.2, DZ)
    k = C.px(0, DZ, 1.0)
    statue = [(sx - 0.9 * k, sy), (sx + 0.9 * k, sy), (sx + 0.6 * k, sy - 3.0 * k), (sx + 0.4 * k, sy - 4.2 * k), (sx - 0.4 * k, sy - 4.2 * k),
              (sx - 0.6 * k, sy - 3.0 * k)]
    out.append(F(statue, INK) + f'<circle cx="{f1(sx)}" cy="{f1(sy - 4.7 * k)}" r="{f1(0.55 * k)}" fill="{INK}"/>')
    out.append(nib([(sx + 0.4 * k, sy - 3.8 * k), (sx + 1.0 * k, sy - 5.6 * k), (sx + 1.1 * k, sy - 6.6 * k)], max(1.2, 0.35 * k), taper=(1, 1), seed=seed, color=INK))
    st_ = (sx + 1.1 * k, sy - 6.9 * k)
    out.append(F([(st_[0], st_[1] - 0.8 * k), (st_[0] + 0.25 * k, st_[1] - 0.1 * k), (st_[0] + 0.8 * k, st_[1]), (st_[0] + 0.25 * k, st_[1] + 0.2 * k),
                   (st_[0], st_[1] + 0.8 * k), (st_[0] - 0.25 * k, st_[1] + 0.2 * k), (st_[0] - 0.8 * k, st_[1]), (st_[0] - 0.25 * k, st_[1] - 0.1 * k)], INK))
    return "".join(out)


def pickup(U, x, y, w, seed=1, acc=True):
    """A pickup truck from behind: cab with rear window over a low tailgate."""
    h = w * 0.68
    cab = [(x - w * 0.36, y - h * 0.55), (x - w * 0.3, y - h), (x + w * 0.3, y - h), (x + w * 0.36, y - h * 0.55)]
    body = [(x - w * 0.5, y - h * 0.15), (x - w * 0.5, y - h * 0.58), (x + w * 0.5, y - h * 0.58), (x + w * 0.5, y - h * 0.15)]
    out = [F([(x - w * 0.46, y - h * 0.2), (x - w * 0.46, y), (x - w * 0.3, y), (x - w * 0.3, y - h * 0.2)], INK),
           F([(x + w * 0.46, y - h * 0.2), (x + w * 0.46, y), (x + w * 0.3, y), (x + w * 0.3, y - h * 0.2)], INK)]
    out.append(F(cab, PAPER))
    if acc:
        out.append(accent(U, poly(cab), bbox(cab), seed, op=0.95, ang=-10, n=6, length=(4, 10), width=(1, 2)))
    out.append(F([(x - w * 0.24, y - h * 0.94), (x + w * 0.24, y - h * 0.94), (x + w * 0.28, y - h * 0.66), (x - w * 0.28, y - h * 0.66)], INK, 0.85))
    out.append(pen(cab, max(0.9, w / 26), seed, 0.1, closed=True))
    out.append(F(body, PAPER))
    if acc:
        out.append(accent(U, poly(body), bbox(body), seed + 1, op=0.95, ang=-10, n=6, length=(4, 10), width=(1, 2)))
    out.append(H(U, body, 0, 1.5, 0.6, span=(0.0, 0.4), dark=(x, y)))
    out.append(seg(x - w * 0.42, y - h * 0.4, x + w * 0.42, y - h * 0.4, 0.8, seed, 0))
    for sx in (-1, 1):
        out.append(F([(x + sx * w * 0.47, y - h * 0.52), (x + sx * w * 0.37, y - h * 0.52), (x + sx * w * 0.37, y - h * 0.38), (x + sx * w * 0.47, y - h * 0.38)], INK))
    out.append(pen(body, max(0.9, w / 24), seed + 1, 0.1, closed=True))
    out.append(F([(x - w * 0.55, y + 0.5), (x + w * 0.55, y + 0.5), (x + w * 0.45, y + h * 0.12), (x - w * 0.45, y + h * 0.12)], INK, 0.35))
    return "".join(out)


@design("austin")
def austin(U):
    """Congress Avenue from the middle of the street, looking up the hill: Victorian commercial fronts in
    long perspective (the east side in shade), lamps and street trees, traffic and a vermilion pickup, the
    Capitol and its dome closing the avenue under a big Texas sky."""
    C = Cam2(f=680, cx=300, vpy=350, eye=1.6, yaw=0)
    LIGHT = (1.0, -0.4)
    def gy(Z):
        return max(0.0, Z - 60) * 0.045
    ZC = 292.0
    art = []
    art.append(cloud(U, 150, 92, 150, 26, 5) + cloud(U, 420, 74, 110, 18, 6) + cloud(U, 500, 140, 70, 12, 7))
    # ground: the avenue rising toward the Capitol
    def road_q(x0, x1, za, zb, y=0.0):
        return [C(x0, gy(za) + y, za), C(x0, gy(zb) + y, zb), C(x1, gy(zb) + y, zb), C(x1, gy(za) + y, za)]
    zs = [10, 30, 60, 90, 130, 180, 240]
    road = []
    for za, zb in zip(zs, zs[1:]):
        road += [road_q(-12, 12, za, zb)]
    for q in road:
        art.append(F(q, PAPER))
    # asphalt tone: horizontal strokes, closer with distance; lane dashes; crossing at 11th
    st = []
    z = 10.0
    while z < 240:
        st.append((C(-12, gy(z), z), C(12, gy(z), z)))
        z *= 1.035
    art.append(segs(st, 0.55, 3, 0.1, op=0.45))
    dash = []
    for xl in (-8, -4, 4, 8):
        z = 16.0
        while z < 236:
            dash.append(poly([C(xl - 0.07, gy(z), z), C(xl + 0.07, gy(z), z), C(xl + 0.07, gy(z + 3), z + 3), C(xl - 0.07, gy(z + 3), z + 3)]))
            z += 9
    art.append(f'<path d="{" ".join(dash)}" fill="{INK}" opacity="0.7"/>')
    art.append(pen([C(-0.2, gy(z), z) for z in range(16, 240, 6)], 0.8, 4, 0.1) + pen([C(0.2, gy(z), z) for z in range(16, 240, 6)], 0.8, 5, 0.1))
    for sx in (-1, 1):
        sw = road_q(sx * 12, sx * 19, 30, 240, 0.15)
        art.append(F(sw, PAPER) + segs([(C(sx * 12, gy(z) + 0.15, z), C(sx * 19, gy(z) + 0.15, z)) for z in range(30, 240, 2)], 0.5, 6, 0, op=0.45))
        art.append(pen([C(sx * 12, gy(z) + 0.15, z) for z in range(30, 240, 5)], 1.4, 7, 0.1))
    # the Capitol grounds: cross street, fence and gate, lawn, the Great Walk
    lawn = road_q(-60, 60, 248, ZC - 6)
    art.append(F(lawn, PAPER) + H(U, lawn, 0, 1.6, 0.5, op=0.55))
    walk = road_q(-4, 4, 248, ZC - 6, 0.05)
    art.append(F(walk, PAPER) + pen([walk[0], walk[1]], 0.9, 8, 0) + pen([walk[3], walk[2]], 0.9, 9, 0))
    art.append(capitol(U, C, ZC, gy(ZC), 10))
    # live oaks on the grounds, either side of the walk
    for X, Z, h, w, sd in ((-26, 300, 13, 22, 1), (28, 298, 13, 22, 2), (-20, 270, 12, 18, 3), (22, 268, 12, 18, 4)):
        x, y = C(X, gy(Z), Z)
        art.append(canopy(U, x, y, C.px(X, Z, h), C.px(X, Z, w), 700 + sd, light=(-1, -1), lobe_r=max(6, C.px(X, Z, 1.6)), shape=0.7, lw=1.0))
    fence = [C(-60, gy(247) + 1.8, 247), C(60, gy(247) + 1.8, 247)]
    art.append(segs([(C(X, gy(247), 247), C(X, gy(247) + 1.8, 247)) for X in [x / 2 for x in range(-120, 121)] if abs(X) > 4.5], 0.6, 11, 0)
               + pen(fence, 1.1, 12, 0))
    for sx in (-1, 1):
        gp = C.qz(247, sx * 4.5 - 0.6, sx * 4.5 + 0.6, gy(247), gy(247) + 4.2)
        art.append(F(gp, PAPER) + shade(U, gp, 0.5, 90, 13) + sketch(gp, 1.0, 13, 0.1))
    # towers behind the old fronts
    for foot, h, sd in ((box(-58, -40, 170, 188), 50, 1), (box(36, 54, 175, 195), 46, 2), (box(-48, -32, 205, 222), 38, 3)):
        g0 = gy(foot[0][1])
        art.append(tower_block(U, C, foot, g0, g0 + h, 800 + sd, LIGHT))
    # the two rows of commercial fronts, far to near
    rnd = random.Random(14)
    for sx in (-1, 1):
        zs_ = [30]
        while zs_[-1] < 240:
            zs_.append(zs_[-1] + rnd.choice((9, 11, 13, 16, 20)))
        blocks = list(zip(zs_, zs_[1:]))
        for i, (z0, z1) in reversed(list(enumerate(blocks))):
            hh = rnd.choice((11, 13.5, 16, 18.5, 21))
            fl = 3 if hh < 15 else 4
            art.append(commercial(U, C, sx * 19, z0, min(z1, 240), hh, 900 + i * 7 + sx, gy, floors=fl,
                                  t=0.78 if sx > 0 else 0.12, arch=rnd.random() < 0.6, awning=rnd.random() < 0.35, ang=75 if sx > 0 else 105))
    # street lamps and sidewalk trees
    for sx in (-1, 1):
        for z in (210, 170, 135, 105, 80, 58, 42):
            x, y = C(sx * 13, gy(z), z)
            art.append(lamp(x, y, C.px(sx * 13, z, 6.0), 20 + z, "globe", max(1.1, min(2.2, C.px(sx * 13, z, 0.16)))))
        for z in (190, 150, 118, 92, 70, 50):
            x, y = C(sx * 16, gy(z), z)
            art.append(canopy(U, x, y, C.px(sx * 16, z, 8), C.px(sx * 16, z, 6.5), 300 + z + sx, light=(-1, -1),
                              lobe_r=max(5, C.px(sx * 16, z, 1.3)), lw=1.0))
    # traffic and people
    for X, Z, sd in ((6, 150, 1), (-6, 120, 2), (-2, 200, 3), (2, 85, 4), (-9.6, 70, 5), (-6, 46, 6)):
        x, y = C(X, gy(Z), Z)
        art.append(car_rear(U, x, y, C.px(X, Z, 1.9), 30 + sd))
    x, y = C(5.8, 0, 30)
    art.append(pickup(U, x, y, C.px(5.8, 30, 2.0), 40))
    for sx in (-1, 1):
        for k, z in enumerate((190, 140, 100, 64, 44)):
            X = sx * (14.5 + (k % 3) * 1.2)
            x, y = C(X, gy(z) + 0.15, z)
            art.append(person(x, y, C.px(X, z, 1.72), 50 + k * 3 + sx, flip=(k + sx) % 2 == 0, bag=k == 2))
    art.append(bird(240, 140, 6, 60) + bird(262, 124, 5, 61) + bird(372, 112, 5, 62))
    return plate(U, "austin", art, 81)


# ================================================================ SYDNEY
def yacht(U, x, wl, s, seed, spin=False, flip=False, heel=0.0):
    """A small sloop: hull, mast, mainsail hatched on its shaded side, jib (or a vermilion spinnaker)."""
    k = -1 if flip else 1
    out = []
    hull = [(x - k * s * 0.55, wl - s * 0.1), (x + k * s * 0.6, wl - s * 0.14), (x + k * s * 0.42, wl + s * 0.04), (x - k * s * 0.45, wl + s * 0.04)]
    mx = x + k * s * 0.02
    top = (mx + heel * s, wl - s * 1.25)
    main = [(mx, wl - s * 0.16), top, (mx - k * s * 0.5 + heel * s * 0.2, wl - s * 0.18)]
    out.append(F(main, PAPER) + H(U, main, 90, max(1.2, s * 0.05), 0.6, span=(0.55, 1), dark=(mx - k * s, wl)) + pen(main, max(0.8, s * 0.03), seed, 0.1, closed=True))
    if spin:
        sp = smooth_closed([(mx + k * s * 0.05, wl - s * 1.15), (mx + k * s * 0.6, wl - s * 0.95), (mx + k * s * 0.72, wl - s * 0.5),
                            (mx + k * s * 0.5, wl - s * 0.22), (mx + k * s * 0.08, wl - s * 0.25)])
        out.append(F(sp, PAPER) + accent(U, sp, (mx - s, wl - s * 1.3, mx + s, wl), seed, op=0.95, ang=-60, n=10, length=(4, 10), width=(1, 2.5))
                   + P(sp, max(0.8, s * 0.03)))
        out.append(segs([((mx + k * s * 0.08, wl - s * (0.3 + 0.2 * j)), (mx + k * s * 0.62, wl - s * (0.4 + 0.15 * j))) for j in range(3)], 0.6, seed, 0.3, op=0.6))
    else:
        jib = [(mx + k * s * 0.03, wl - s * 1.1), (mx + k * s * 0.55, wl - s * 0.16), (mx + k * s * 0.05, wl - s * 0.2)]
        out.append(F(jib, PAPER) + pen(jib, max(0.8, s * 0.03), seed + 1, 0.1, closed=True))
    out.append(seg(mx, wl - s * 0.14, top[0], top[1], max(0.9, s * 0.03), seed, 0))
    out.append(F(hull, INK, 0.88))
    out.append(P(f"M {f1(x - s * 0.7)} {f1(wl + s * 0.12)} l {f1(s * 1.4)} 0 M {f1(x - s * 0.4)} {f1(wl + s * 0.22)} l {f1(s * 0.8)} 0", max(0.7, s * 0.025), INK, 0.8))
    return "".join(out)


def harbour_ferry(U, x0, x1, wl, seed):
    """A Sydney double-ended harbour ferry broadside: dark lower hull, cream two-deck superstructure with a
    long run of windows, open upper deck rail, wheelhouses at both ends, a short funnel, a bow wave."""
    L = x1 - x0
    h = L * 0.07
    out = []
    hull = [(x0 - L * 0.02, wl - h * 1.1), (x1 + L * 0.02, wl - h * 1.1), (x1 - L * 0.05, wl), (x0 + L * 0.05, wl)]
    out.append(F(hull, INK, 0.88))
    out.append(seg(x0 - L * 0.02, wl - h * 1.1, x1 + L * 0.02, wl - h * 1.1, max(1.0, L * 0.012), seed, 0))
    d1 = [(x0 + L * 0.01, wl - h * 2.3), (x1 - L * 0.01, wl - h * 2.3), (x1 - L * 0.01, wl - h * 1.1), (x0 + L * 0.01, wl - h * 1.1)]
    out.append(F(d1, PAPER) + sketch(d1, max(0.9, L * 0.01), seed, 0.2))
    m = homog(d1)
    n = max(6, int(L / 7))
    out.append(f'<path d="{" ".join(poly([m((i + 0.18) / n, 0.22), m((i + 0.82) / n, 0.22), m((i + 0.82) / n, 0.68), m((i + 0.18) / n, 0.68)]) for i in range(n))}" fill="{INK}" opacity="0.85"/>')
    d2 = [(x0 + L * 0.1, wl - h * 3.3), (x1 - L * 0.1, wl - h * 3.3), (x1 - L * 0.08, wl - h * 2.3), (x0 + L * 0.08, wl - h * 2.3)]
    out.append(F(d2, PAPER) + sketch(d2, max(0.9, L * 0.01), seed + 1, 0.2))
    out.append(segs([((x, wl - h * 2.3), (x, wl - h * 3.0)) for x in [x0 + L * 0.1 + i * L * 0.8 / 24 for i in range(25)]], 0.7, seed, 0))
    out.append(H(U, d2, 0, max(1.1, h * 0.35), 0.6, op=0.8))
    for wx in (x0 + L * 0.1, x1 - L * 0.22):
        wh = [(wx, wl - h * 4.2), (wx + L * 0.12, wl - h * 4.2), (wx + L * 0.12, wl - h * 3.3), (wx, wl - h * 3.3)]
        out.append(F(wh, PAPER) + F(quad_sub3(wh, 0.1, 0.2, 0.9, 0.55), INK, 0.85) + sketch(wh, max(0.9, L * 0.01), seed + 2, 0.2))
    fx = (x0 + x1) / 2
    fn = [(fx - L * 0.025, wl - h * 3.3), (fx - L * 0.02, wl - h * 4.9), (fx + L * 0.03, wl - h * 4.9), (fx + L * 0.035, wl - h * 3.3)]
    out.append(F(fn, PAPER) + F(quad_sub3(fn, 0, 0, 1, 0.25), INK) + H(U, fn, 90, 1.2, 0.6, span=(0.5, 1), dark=(fx + 20, wl)) + sketch(fn, 1.0, seed + 3, 0.2))
    out.append(P(f"M {f1(x1 - L * 0.02)} {f1(wl - 1)} q {f1(L * 0.18)} {f1(h * 0.4)} {f1(L * 0.42)} {f1(h * 1.2)} M {f1(x1 - L * 0.06)} {f1(wl + 1)} q {f1(L * 0.12)} {f1(h * 0.6)} {f1(L * 0.3)} {f1(h * 1.6)} "
                 f"M {f1(x0 + L * 0.05)} {f1(wl + 1)} q {f1(-L * 0.2)} {f1(h * 0.3)} {f1(-L * 0.5)} {f1(h * 0.5)}", max(0.9, L * 0.008), INK, 0.85))
    return "".join(out)


@design("sydney")
def sydney(U):
    """The Harbour Bridge from the sandstone sea wall at Dawes Point: the south pylons close by, the great
    arch striding across the water to the north shore, harbour ferries and yachts beneath (one vermilion
    spinnaker), a glitter path of light on the water, a fig bough and strollers on the promenade."""
    th = math.radians(40)
    dx, dz = math.cos(th), math.sin(th)
    px_, pz_ = -dz, dx                      # lateral (toward the far side)
    S = (-150.0, 230.0)
    SPAN = 503.0
    def A(sv, lat=0.0):
        return (S[0] + dx * SPAN * sv + px_ * lat, S[1] + dz * SPAN * sv + pz_ * lat)
    yaw = math.degrees(math.atan2((A(0.0)[0] + A(1.0)[0]) / 2, (A(0.0)[1] + A(1.0)[1]) / 2)) - 7.5
    C = Cam2(f=345, cx=300, vpy=356, eye=4.0, yaw=yaw)
    def yb(sv):
        return 12 + 104 * (1 - (2 * sv - 1) ** 2)
    def yt(sv):
        return yb(sv) + 18 + 40 * (2 * sv - 1) ** 2
    def Pp(sv, y, lat):
        X, Z = A(sv, lat)
        return C(X, y, Z)
    art = []
    art.append(cloud(U, 380, 104, 150, 24, 5) + cloud(U, 150, 156, 130, 20, 7) + cloud(U, 500, 190, 90, 13, 10))
    HZ = C.vpy
    # north shore: hills, houses, a few towers, in pale haze
    rnd = random.Random(3)
    ridge = [(30, HZ - 10), (90, HZ - 22), (150, HZ - 16), (210, HZ - 26), (270, HZ - 18), (330, HZ - 30), (400, HZ - 20), (470, HZ - 28), (570, HZ - 14)]
    hill = ridge + [(570, HZ + 1), (30, HZ + 1)]
    art.append(F(smooth_open(ridge) + f" L 570 {HZ + 1} L 30 {HZ + 1} Z", PAPER))
    art.append(H(U, smooth_open(ridge) + f" L 570 {HZ + 1} L 30 {HZ + 1} Z", 0, 2.4, 0.5, op=0.55, box=(30, HZ - 40, 570, HZ + 2)))
    houses = []
    for i in range(70):
        x = rnd.uniform(40, 560)
        yr = HZ - 14 - 8 * math.sin(x / 40)
        w_ = rnd.uniform(4, 9)
        h_ = rnd.uniform(3, 7)
        y0 = rnd.uniform(yr, HZ - 2)
        houses.append([(x, y0 - h_), (x + w_, y0 - h_), (x + w_, y0), (x, y0)])
    art.append(f'<path d="{" ".join(poly(q) for q in houses)}" fill="{PAPER}" stroke="{INK}" stroke-width="0.6" opacity="0.8"/>')
    for x0_, w_, h_ in ((448, 12, 46), (462, 10, 36), (474, 14, 54), (490, 9, 30), (500, 12, 40)):
        q = [(x0_, HZ - 20 - h_), (x0_ + w_, HZ - 20 - h_), (x0_ + w_, HZ - 8), (x0_, HZ - 8)]
        art.append(F(q, PAPER) + facade(U, q, 2, int(h_ / 5), "grid", x0_, dark_p=0.1, w=0.5, op=0.7) + sketch(q, 0.9, x0_, 0.2, op=0.8))
    art.append(P(smooth_open(ridge), 1.1, INK, 0.7))
    # water
    water = [(0, HZ), (600, HZ), (600, 600), (0, 600)]
    sx_ = Pp(0.5, 0, 0)[0]
    art.append(ripples(U, 20, 580, HZ + 0.5, 470, 9, dens=0.95, gap=(1.6, 8.0), ln=((3, 9), (14, 40)), w=(0.7, 1.5),
                       skip=[(sx_ - 26, sx_ + 26)], clip=poly(water)))
    # --- the bridge: far truss, deck, near truss, pylons
    NP = 28
    def chord(lat, fn, a=0.0, b=1.0, n=60):
        return [Pp(a + (b - a) * i / n, fn(a + (b - a) * i / n), lat) for i in range(n + 1)]
    def truss(lat, w_main, w_web, op):
        out = []
        top, bot = chord(lat, yt), chord(lat, yb)
        band = top + bot[::-1]
        out.append(F(band, PAPER, op))
        webs = []
        for i in range(NP + 1):
            sv = i / NP
            webs.append((Pp(sv, yb(sv), lat), Pp(sv, yt(sv), lat)))
            if i < NP:
                s2 = (i + 1) / NP
                if i < NP / 2:
                    webs.append((Pp(sv, yt(sv), lat), Pp(s2, yb(s2), lat)))
                else:
                    webs.append((Pp(sv, yb(sv), lat), Pp(s2, yt(s2), lat)))
        out.append(segs(webs, w_web, 3, 0, op=op))
        out.append(clipped(U("tr"), poly(band), H(U, band, 90, 1.6, 0.55, op=0.55 * op)))
        out.append(P(smooth_open(top), w_main, INK, op) + P(smooth_open(bot), w_main * 1.15, INK, op))
        # second line on each chord: the chords are deep box girders
        out.append(P(smooth_open(chord(lat, lambda v: yt(v) - 3.2)), w_main * 0.6, INK, op) + P(smooth_open(chord(lat, lambda v: yb(v) + 3.6)), w_main * 0.6, INK, op))
        return "".join(out)
    art.append(truss(15, 1.3, 0.7, 0.8))
    # lateral bracing between the top chords (seen from below)
    br = []
    for i in range(NP):
        sv, s2 = i / NP, (i + 1) / NP
        br.append((Pp(sv, yb(sv), 15), Pp(s2, yb(s2), -15)))
        br.append((Pp(sv, yb(sv), -15), Pp(s2, yb(s2), 15)))
    art.append(segs(br, 0.6, 4, 0, op=0.55))
    # deck: underside, fascia, hangers
    DY = 49.0
    s_ext = (-0.32, 1.18)
    under = [Pp(s_ext[0], DY - 3, 24), Pp(s_ext[1], DY - 3, 24), Pp(s_ext[1], DY - 3, -24), Pp(s_ext[0], DY - 3, -24)]
    art.append(F(under, PAPER) + H(U, under, 0, 1.5, 0.6) + H(U, under, 60, 2.6, 0.5, op=0.7))
    girders = [(Pp(sv, DY - 3, -24), Pp(sv, DY - 3, 24)) for sv in [s_ext[0] + k * 0.025 for k in range(int((s_ext[1] - s_ext[0]) / 0.025) + 1)]]
    art.append(segs(girders, 0.6, 5, 0, op=0.7))
    fas = [Pp(s_ext[0], DY + 1.5, -24), Pp(s_ext[1], DY + 1.5, -24), Pp(s_ext[1], DY - 3, -24), Pp(s_ext[0], DY - 3, -24)]
    art.append(F(fas, PAPER) + segs(qlines(fas, [0.5]), 0.7, 6, 0) + pen([fas[0], fas[1]], 1.6, 7, 0.1) + pen([fas[3], fas[2]], 1.4, 8, 0.1))
    rail = [(Pp(sv, DY + 1.5, -24), Pp(sv, DY + 2.8, -24)) for sv in [s_ext[0] + k * 0.006 for k in range(int((s_ext[1] - s_ext[0]) / 0.006))]]
    art.append(segs(rail, 0.5, 9, 0, op=0.7) + pen([Pp(s_ext[0], DY + 2.8, -24), Pp(s_ext[1], DY + 2.8, -24)], 0.9, 10, 0.1))
    hang = []
    for i in range(1, NP):
        sv = i / NP
        if yb(sv) > DY + 2:
            hang.append((Pp(sv, yb(sv), -15), Pp(sv, DY + 1.5, -15)))
            hang.append((Pp(sv, yb(sv), 15), Pp(sv, DY + 1.5, 15)))
    art.append(segs(hang, 0.9, 11, 0))
    # approach-span piers on the north side
    for sv in (1.06, 1.12):
        for q, nrm, _ in vis_faces(C, [A(sv - 0.006, -20), A(sv + 0.006, -20), A(sv + 0.006, 20), A(sv - 0.006, 20)], 0, DY - 3):
            art.append(F(q, PAPER) + shade(U, q, 0.5, 90, 12) + sketch(q, 0.9, 12, 0.2))
    art.append(truss(-15, 2.0, 1.0, 1.0))
    # pylons: north pair (far) then south pair (near)
    def pylon(sv, lat, seed):
        out = []
        c = A(sv, lat)
        foot = [(c[0] + dx * -11 + px_ * -9, c[1] + dz * -11 + pz_ * -9), (c[0] + dx * 11 + px_ * -9, c[1] + dz * 11 + pz_ * -9),
                (c[0] + dx * 11 + px_ * 9, c[1] + dz * 11 + pz_ * 9), (c[0] + dx * -11 + px_ * 9, c[1] + dz * -11 + pz_ * 9)]
        for q, nrm, (a, b) in vis_faces(C, foot, 0, 84):
            t = tone_of(nrm, (0.3, 1.0))
            out.append(F(q, PAPER))
            out.append(segs(qlines(q, [k / 30 for k in range(1, 30)]), 0.5, seed, 0, op=0.55))
            out.append(shade(U, q, t, 90, seed))
            # the window openings near the top and the cornice
            m = homog(q)
            for u0 in (0.3, 0.58):
                out.append(F(arch_q([m(u0, 0.08), m(u0 + 0.12, 0.08), m(u0 + 0.12, 0.2), m(u0, 0.2)], 0.4, 6), INK, 0.85))
            out.append(segs([(m(0, 0.04), m(1, 0.04)), (m(0, 0.23), m(1, 0.23)), (m(0, 0.27), m(1, 0.27))], 1.0, seed, 0))
            out.append(sketch(q, 1.6, seed, 0.4))
        top_ = [C(p[0], 84, p[1]) for p in foot]
        cap = vis_faces(C, foot, 84, 89)
        for q, nrm, _ in cap:
            out.append(F(q, PAPER) + shade(U, q, tone_of(nrm, (0.3, 1.0)) * 0.8, 90, seed) + sketch(q, 1.3, seed, 0.3))
        return out, math.hypot(*c)
    pys = []
    for sv in (1.0, 0.0):
        for lat in (24, -24):
            o, dd = pylon(sv, lat, 20 + int(sv * 10) + lat)
            pys.append((dd, o))
    for dd, o in sorted(pys, key=lambda q: -q[0]):
        art += o
    # --- harbour traffic
    art.append(harbour_ferry(U, 318, 488, 388, 30))
    gx, gy_ = Pp(0.8, 0, -60)
    art.append(harbour_ferry(U, gx - 16, gx + 22, gy_, 31))
    for sv, lat, s_, sp, fl in ((0.62, -90, 16, False, True), (0.2, -60, 14, False, False), (0.92, -30, 10, False, True)):
        x, y = Pp(sv, 0, lat)
        art.append(yacht(U, x, y, s_, 40 + int(sv * 100), spin=sp, flip=fl))
    art.append(yacht(U, 512, 380, 34, 140, spin=True, flip=False))
    # --- foreground: sandstone sea wall, railing, lamp, people, a fig bough
    wall_top = 420
    sw = [(-10, wall_top - 20), (610, wall_top + 6), (610, 620), (-10, 620)]
    art.append(F(sw, PAPER))
    blocks = []
    for r in range(4):
        y0 = lerp(wall_top - 20, wall_top + 6, 0) + r * 9
        blocks.append(((-10, wall_top - 20 + r * 9), (610, wall_top + 6 + r * 9)))
    art.append(clipped(U("sw"), poly(sw), segs(blocks, 0.8, 50, 0.2) + H(U, sw, 70, 2.6, 0.6, op=0.6)))
    joints = []
    for r in range(4):
        x = (r % 2) * 20 - 10
        while x < 610:
            ya = wall_top - 20 + r * 9 + (x + 10) / 620 * 26
            joints.append(((x, ya), (x, ya + 9)))
            x += 40
    art.append(clipped(U("sj"), poly(sw), segs(joints, 0.8, 51, 0)))
    art.append(pen([(-10, wall_top - 20), (610, wall_top + 6)], 2.0, 52, 0.2))
    # railing
    rl = []
    for k in range(-1, 32):
        x = k * 20
        ya = wall_top - 20 + (x + 10) / 620 * 26
        rl.append(((x, ya), (x, ya - 34 + x * 0.01)))
    art.append(segs(rl, 1.6, 53, 0.1))
    art.append(pen([(-10, wall_top - 54), (610, wall_top - 22)], 2.2, 54, 0.2) + pen([(-10, wall_top - 38), (610, wall_top - 8)], 1.2, 55, 0.2))
    # strollers leaning on the rail
    for x, h, sd, fl in ((196, 40, 1, False), (214, 38, 2, True), (420, 42, 3, False), (500, 40, 4, True)):
        ya = wall_top - 20 + (x + 10) / 620 * 26
        art.append(person(x, ya - 2, h, 60 + sd, flip=fl, bag=sd == 3))
    art.append(lamp(262, wall_top - 7, 96, 70, "lantern", 2.0))
    # gulls
    art.append(bird(300, 186, 8, 80) + bird(322, 170, 6, 81) + bird(250, 206, 5, 82) + bird(430, 150, 6, 83))
    # fig bough from the top left
    return plate(U, "sydney", art, 91)


# ================================================================ RIO DE JANEIRO
def wave_pavement(U, C, x0, x1, z0, z1, seed, lam=7.5, amp=0.55, band=0.62):
    """Portuguese-stone wave pavement on the ground plane between x0..x1, z0..z1 (waves run along Z):
    alternating ink and paper bands whose edges undulate, drawn in perspective with a stone texture."""
    out = []
    bands = []
    k = 0
    x = x0 - amp
    zs = []
    z = z0
    while z < z1:
        zs.append(z)
        z += max(0.12, z * 0.025)
    zs.append(z1)
    while x < x1 + amp:
        if k % 2 == 0:
            left = [C(x + amp * math.sin(2 * math.pi * zz / lam), 0.02, zz) for zz in zs]
            right = [C(x + band + amp * math.sin(2 * math.pi * zz / lam), 0.02, zz) for zz in zs]
            bands.append(poly(left + right[::-1]))
        x += band
        k += 1
    clip = poly([C(x0, 0.02, z0), C(x0, 0.02, z1), C(x1, 0.02, z1), C(x1, 0.02, z0)])
    out.append(F(clip, PAPER))
    out.append(clipped(U("wp"), clip, f'<path d="{" ".join(bands)}" fill="{INK}" opacity="0.86"/>'))
    rnd = random.Random(seed)
    dots = []
    for i in range(700):
        X = rnd.uniform(x0, x1)
        Z = math.exp(rnd.uniform(math.log(z0), math.log(min(z1, 60))))
        px_, py_ = C(X, 0.02, Z)
        dots.append(f'<circle cx="{f1(px_)}" cy="{f1(py_)}" r="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(clipped(U("wq"), clip, f'<g fill="{PAPER}" opacity="0.5">{"".join(dots)}</g>'))
    return "".join(out)


def apartment(U, C, foot, h, seed, light, floors=None):
    """A Rio apartment block: visible faces with continuous balcony slabs, dark openings, roof parapet."""
    out = []
    floors = floors or max(4, int(h / 3.0))
    for q, nrm, (a, b) in vis_faces(C, foot, 0, h):
        t = tone_of(nrm, light)
        w = math.hypot(b[0] - a[0], b[1] - a[1])
        out.append(F(q, PAPER))
        m = homog(q)
        cols = max(2, int(w / 3.2))
        out.append(facade(U, quad_sub3(q, 0, 0.04, 1, 0.9), cols, floors, "pane", seed, dark_p=0.55, w=0.6, my=0.3))
        out.append(segs([(m(0, (j + 0.04) / floors), m(1, (j + 0.04) / floors)) for j in range(1, floors)], 1.1, seed, 0))
        out.append(F(quad_sub3(q, 0, 0.9, 1, 1), INK, 0.7))
        out.append(shade(U, q, t, 90, seed))
        out.append(sketch(q, 1.3, seed, 0.3))
    return "".join(out)


def beach_umbrella(U, x, y, r, seed, tilt=0.15):
    """A vermilion beach parasol on the sand, gores radiating, pole, a folding chair."""
    cx, cy = x + r * tilt, y - r * 1.6
    rim = [(cx - r, cy + r * 0.28), (cx - r * 0.5, cy + r * 0.38), (cx, cy + r * 0.42), (cx + r * 0.5, cy + r * 0.36), (cx + r, cy + r * 0.24)]
    ap = (cx + r * 0.05, cy - r * 0.32)
    d = smooth_open(rim) + f" Q {f1(cx + r * 0.6)} {f1(cy - r * 0.2)} {f1(ap[0])} {f1(ap[1])} Q {f1(cx - r * 0.6)} {f1(cy - r * 0.18)} {f1(rim[0][0])} {f1(rim[0][1])} Z"
    gores = " ".join(poly([ap, rim[i], rim[i + 1]]) for i in (0, 2))
    out = [F(d, PAPER), accent(U, d, (cx - r, cy - r, cx + r, cy + r), seed, op=0.95, ang=-60, n=10, length=(4, 10), width=(1, 2.5))]
    out.append(clipped(U("bu"), d, f'<path d="{gores}" fill="{INK}" opacity="0.18"/>'))
    out.append(P(d, 1.3) + segs([(ap, rim[k]) for k in range(1, 4)], 0.7, seed, 0))
    out.append(seg(ap[0], ap[1], x, y, 1.4, seed, 0))
    out.append(P(f"M {f1(x + r * 0.4)} {f1(y)} l {f1(r * 0.35)} {f1(-r * 0.45)} l {f1(r * 0.25)} {f1(-r * 0.05)} M {f1(x + r * 0.5)} {f1(y - r * 0.3)} l {f1(r * 0.4)} 0 l {f1(r * 0.1)} {f1(r * 0.3)}", 1.1))
    out.append(F([(x - r * 0.9, y + 1.5), (x + r * 0.9, y + 1.5), (x + r * 0.6, y + 4), (x - r * 0.7, y + 4)], INK, 0.25))
    return "".join(out)


@design("rio")
def rio(U):
    """Botafogo at the end of the afternoon: Sugarloaf and Urca across the cove, the cable car between
    them, moored yachts on the water, the beach with a vermilion parasol, the wave-paved promenade sweeping
    away under royal palms, apartment blocks along the avenue, frigatebirds overhead."""
    C = Cam2(f=420, cx=300, vpy=350, eye=1.6, yaw=-12)
    LIGHT = (-0.5, -1.0)
    art = []
    HZ = C.vpy
    art.append(cloud(U, 160, 92, 140, 20, 5) + cloud(U, 420, 120, 90, 14, 6))
    # far Niterói hills at the mouth of the bay
    far = [(40, HZ - 6), (80, HZ - 14), (120, HZ - 10), (160, HZ - 18), (200, HZ - 8), (230, HZ - 3)]
    fd = smooth_open(far) + f" L 230 {HZ + 1} L 40 {HZ + 1} Z"
    art.append(F(fd, PAPER) + H(U, fd, 0, 2.4, 0.5, op=0.5, box=(40, HZ - 24, 240, HZ + 2)) + P(smooth_open(far), 1.0, INK, 0.6))
    # the bay
    water = [(0, HZ), (600, HZ), (600, 600), (0, 600)]
    art.append(ripples(U, 0, 600, HZ + 0.5, 440, 7, dens=0.9, gap=(1.5, 7.5), ln=((2, 7), (10, 30)), w=(0.6, 1.3),
                       refl=[(150, 330, 0.45)], clip=poly(water)))
    # Sugarloaf (behind, right) and Urca (front, left), with the cable car
    def M(X, Y, Z):
        return C(X, Y, Z)
    SX, SZ = -235, 1080
    sug = [M(SX - 158, 0, SZ), M(SX - 156, 100, SZ), M(SX - 147, 200, SZ), M(SX - 126, 292, SZ), M(SX - 94, 356, SZ), M(SX - 52, 392, SZ),
           M(SX - 8, 404, SZ), M(SX + 34, 396, SZ), M(SX + 74, 364, SZ), M(SX + 106, 304, SZ), M(SX + 128, 214, SZ), M(SX + 140, 112, SZ), M(SX + 146, 0, SZ)]
    art.append(granite_dome(U, sug, 8, streaks=34, veg_base=8))
    UX, UZ = -400, 820
    urca = [M(UX - 230, 0, UZ), M(UX - 200, 36, UZ), M(UX - 150, 86, UZ), M(UX - 90, 122, UZ), M(UX - 30, 140, UZ), M(UX + 30, 152, UZ),
            M(UX + 80, 148, UZ), M(UX + 125, 124, UZ), M(UX + 160, 78, UZ), M(UX + 182, 28, UZ), M(UX + 190, 0, UZ)]
    ud = smooth_open(urca) + " Z"
    ub = bbox(urca, 0)
    rx_face = urca[7][0]
    art.append(forest_fill(U, ud, ub, 9, r=4.6, skip=lambda x, y: x > rx_face - 6 and y < ub[1] + (ub[3] - ub[1]) * 0.55))
    face = [urca[6], urca[7], urca[8], (urca[8][0] - 14, urca[8][1] + 6), (urca[7][0] - 12, urca[7][1] + 16)]
    art.append(F(face, PAPER) + clipped(U("uf"), poly(face), H(U, face, 75, 1.8, 0.7) + segs([((x, urca[7][1]), (x - 3, urca[8][1] + 6)) for x in range(int(face[0][0]) - 10, int(face[2][0]) + 4, 4)], 0.8, 15, 0.4)))
    s1, s2 = M(UX + 40, 154, UZ), M(SX - 6, 406, SZ)
    for off in (-1.5, 1.5):
        art.append(P(f"M {f1(s1[0])} {f1(s1[1] + off)} Q {f1((s1[0] + s2[0]) / 2)} {f1((s1[1] + s2[1]) / 2 + 9 + off)} {f1(s2[0])} {f1(s2[1] + off)}", 0.8))
    for st, sd in ((s1, 11), (s2, 12)):
        q = [(st[0] - 6, st[1] + 2), (st[0] + 6, st[1] + 2), (st[0] + 6, st[1] - 5), (st[0] - 6, st[1] - 5)]
        art.append(F(q, PAPER) + sketch(q, 1.0, sd, 0.2))
    gx, gy_ = pt(s1, s2, 0.58)
    gy_ += 7
    gq = [(gx - 4, gy_), (gx + 4, gy_), (gx + 3.5, gy_ + 6), (gx - 3.5, gy_ + 6)]
    art.append(seg(gx, gy_ - 4, gx, gy_, 0.9, 13, 0) + F(gq, INK, 0.85))
    art.append(pen([(0, HZ), (600, HZ)], 0.9, 14, 0.1, op=0.6))
    # moored yachts across the cove, far to near
    rnd = random.Random(10)
    boats = []
    for i in range(70):
        X = rnd.uniform(-420, -14)
        Z = math.exp(rnd.uniform(math.log(40), math.log(650)))
        if X > -0.1 * Z - 8:
            continue
        x, y = C(X, 0, Z)
        if not (10 < x < 590) or y < HZ + 1:
            continue
        s_ = min(26, C.px(X, Z, 9))
        if 170 < x < 330 and s_ > 12:
            continue
        boats.append((Z, x, y, s_))
    for Z, x, y, s_ in sorted(boats, reverse=True):
        if s_ < 9:
            hull = [(x - s_ * 0.5, y - s_ * 0.08), (x + s_ * 0.55, y - s_ * 0.08), (x + s_ * 0.4, y + s_ * 0.06), (x - s_ * 0.4, y + s_ * 0.06)]
            art.append(F(hull, PAPER) + pen(hull, 0.8, int(x), 0, closed=True) + seg(x, y - s_ * 0.08, x + 0.5, y - s_ * 1.2, 0.8, int(y), 0)
                       + P(f"M {f1(x - s_ * 0.3)} {f1(y + s_ * 0.2)} l {f1(s_ * 0.6)} 0", 0.6))
        else:
            art.append(yacht(U, x, y, s_, int(x * 7) % 997, flip=int(x) % 2 == 0))
    # the beach: sand from the water's edge to the promenade wall
    shore = [C(-6.5, 0, 9), C(-7.5, 0, 90), C(-14, 0, 200), C(-40, 0, 320), C(-110, 0, 460)]
    sand = shore + [C(-1.2, 0, 420), C(-1.2, 0, 9)]
    sand_d = smooth_open(shore) + " " + poly([C(-1.2, 0, 420), C(-1.2, 0, 9)], closed=False).replace("M", "L") + " Z"
    art.append(F(sand_d, PAPER))
    art.append(ST(U, sand_d, 2200, light=(500, HZ), r=(0.45, 1.0), op=0.7, box=(0, HZ - 2, 600, 480)))
    art.append(P(smooth_open(shore), 1.4))
    art.append(P(smooth_open([(p[0], p[1] - 2.5) for p in shore]), 0.9, INK, 0.7))
    x, y = C(-3.6, 0, 22)
    art.append(beach_umbrella(U, x, y, C.px(-3.6, 22, 1.1), 20))
    for X, Z, sd, fl in ((-5.0, 30, 1, False), (-6.2, 52, 2, True), (-9, 120, 3, False), (-3.0, 70, 4, True)):
        art.append(ppl(C, X, Z, 30 + sd, flip=fl))
    # promenade: low wall, wave pavement, road
    art.append(wave_pavement(U, C, -1.2, 6.0, 7.5, 420, 21))
    pw = C.qx(-1.2, 7.5, 420, 0, 0.5)
    art.append(F(pw, PAPER) + H(U, pw, 0, 1.4, 0.6) + pen([pw[0], pw[1]], 1.3, 22, 0.1))
    road = [C(6.0, 0, 9), C(6.0, 0, 420), C(16, 0, 420), C(16, 0, 9)]
    art.append(F(road, PAPER) + H(U, road, 2, 2.0, 0.5, op=0.5))
    art.append(pen([C(6.0, 0.02, 8), C(6.0, 0.02, 420)], 1.4, 23, 0.1))
    # apartment blocks along the avenue, far to near
    for k, (z0, z1, h) in enumerate(((330, 360, 38), (280, 318, 32), (232, 270, 40), (190, 222, 30), (150, 182, 36), (112, 142, 42), (80, 106, 33))):
        art.append(apartment(U, C, box(18, 34, z0, z1), h, 40 + k, LIGHT))
    # royal palms along the promenade, far to near; lamps
    for k, z in enumerate((300, 220, 160, 116, 84, 60, 43, 31)):
        art.append(pcoco(U, C, 6.6, z, 17 + (k % 3), 60 + k, lean=-0.04 + 0.03 * (k % 3), fronds=11, span=0.95))
    for z in (190, 100, 52):
        art.append(plamp(C, 5.6, z, 70 + z, "globe", 4.6))
    # people on the promenade: joggers, a cyclist, a couple
    for X, Z, sd, fl in ((2.0, 140, 1, False), (0.6, 90, 2, True), (3.6, 62, 3, False), (1.0, 40, 4, True), (2.8, 26, 5, False)):
        art.append(ppl(C, X, Z, 50 + sd, Y=0.02, flip=fl, bag=sd == 3))
    x, y = C(4.2, 0.02, 34)
    art.append(cyclist(x, y, C.px(4.2, 34, 1.75), 58))
    x, y = C(-7.5, 0, 14)
    art.append(coco_palm(U, x, y, 300, 77, lean=-0.2, fronds=13, span=0.9))
    art.append(frigatebird(250, 138, 16, 90) + frigatebird(290, 112, 11, 91) + frigatebird(360, 150, 9, 92))
    return plate(U, "rio", art, 101)


# ================================================================ ATLANTA
def gothic_top(U, x0, x1, top, seed, h=46):
    """One Atlantic Center's copper pyramid with gabled dormers, pinnacles and a finial (light from left)."""
    out = []
    cx = (x0 + x1) / 2
    roof = [(x0 - 1, top), (cx, top - h), (x1 + 1, top)]
    out.append(F(roof, PAPER) + H(U, [(cx, top - h), (x1 + 1, top), (cx, top)], 90, 1.4, 0.8) + H(U, roof, 0, 2.6, 0.6, op=0.7))
    out.append(sketch(roof, 1.5, seed, 0.6, closed=False))
    for gx, gh in ((x0 + (x1 - x0) * 0.22, 12), (x1 - (x1 - x0) * 0.22, 12), (cx, 16)):
        gy = top - (14 if gh == 16 else 0)
        g = [(gx - 4.5, gy), (gx, gy - gh), (gx + 4.5, gy)]
        out.append(F(g, PAPER) + pen(g, 1.1, seed, 0.1) + F([(gx - 2, gy - 1), (gx, gy - gh + 5), (gx + 2, gy - 1)], INK, 0.8))
        out.append(seg(gx, gy - gh, gx, gy - gh - 5, 1.0, seed, 0))
    out.append(nib([(cx, top - h), (cx, top - h - 22)], 2.0, taper=(1, 0.2), seed=seed, color=INK))
    return "".join(out)


def lattice_top(U, x0, x1, top, seed, h=44):
    """Bank of America Plaza: chamfered shoulders, an open lattice pyramid, the spire."""
    out = []
    cx = (x0 + x1) / 2
    sh = [(x0, top), (x0 + 3, top - 7), (x1 - 3, top - 7), (x1, top)]
    out.append(F(sh, PAPER) + sketch(sh, 1.2, seed, 0.5, closed=False))
    pyr = [(x0 + 3, top - 7), (cx, top - h), (x1 - 3, top - 7)]
    out.append(F(pyr, PAPER))
    lat = []
    for i in range(1, 7):
        t = i / 7
        ya = lerp(top - 7, top - h, t)
        lat.append(((lerp(x0 + 3, cx, t), ya), (lerp(x1 - 3, cx, t), ya)))
    for i in range(1, 6):
        lat.append(((lerp(x0 + 3, x1 - 3, i / 6), top - 7), (cx, top - h)))
    out.append(segs(lat, 0.7, seed, 0))
    out.append(clipped(U("lt"), poly(pyr), H(U, [(cx, top - h), (x1 - 3, top - 7), (cx, top - 7)], 90, 1.5, 0.7)))
    out.append(sketch(pyr, 1.3, seed, 0.5, closed=False))
    out.append(nib([(cx, top - h), (cx, top - h - 26)], 1.8, taper=(1, 0.2), seed=seed, color=INK))
    return "".join(out)


def stepped_top(U, x0, x1, top, seed, steps=4, h=30):
    """A stepped pyramid crown with corner finials (Promenade II style)."""
    out = []
    w = x1 - x0
    for k in range(steps):
        a, b = x0 + w * 0.1 * k, x1 - w * 0.1 * k
        y0, y1 = top - h / steps * k, top - h / steps * (k + 1)
        q = [(a, y1), (b, y1), (b, y0), (a, y0)]
        out.append(F(q, PAPER) + H(U, [((a + b) / 2 + (b - a) * 0.2, y1), (b, y1), (b, y0), ((a + b) / 2 + (b - a) * 0.2, y0)], 90, 1.4, 0.7) + sketch(q, 1.1, seed + k, 0.3))
        for fx in (a + 1.5, b - 1.5):
            out.append(seg(fx, y1, fx, y1 - 4, 1.0, seed, 0))
    cx = (x0 + x1) / 2
    out.append(nib([(cx, top - h), (cx, top - h - 16)], 1.6, taper=(1, 0.2), seed=seed, color=INK))
    return "".join(out)


def fin_top(U, x0, x1, top, seed):
    """A glass tower crown of tall flared fins round a spire (1180 Peachtree style)."""
    out = []
    cx = (x0 + x1) / 2
    for k, (dx_, hh) in enumerate(((-0.5, 18), (-0.2, 30), (0.2, 30), (0.5, 18))):
        fx = cx + dx_ * (x1 - x0)
        f = [(fx - 3, top), (fx + dx_ * 4 - 1, top - hh), (fx + dx_ * 4 + 1.5, top - hh + 3), (fx + 3, top)]
        out.append(F(f, PAPER) + pen(f, 1.0, seed + k, 0.1, closed=True))
    out.append(nib([(cx, top), (cx, top - 52)], 1.6, taper=(1, 0.2), seed=seed, color=INK))
    return "".join(out)


def picnic(U, x, y, w, seed):
    """A vermilion checked picnic blanket in perspective, a basket and a couple sitting on it."""
    q = [(x - w * 0.5, y - w * 0.12), (x + w * 0.42, y - w * 0.16), (x + w * 0.55, y + w * 0.08), (x - w * 0.4, y + w * 0.12)]
    out = [F(q, PAPER), accent(U, poly(q), bbox(q), seed, op=0.95, ang=-10, n=12, length=(6, 14), width=(1.5, 3))]
    m = homog(q)
    out.append(segs([(m(i / 6, 0), m(i / 6, 1)) for i in range(1, 6)] + [(m(0, j / 4), m(1, j / 4)) for j in range(1, 4)], 0.8, seed, 0, color=PAPER))
    out.append(pen(q, 1.2, seed, 0.1, closed=True))
    bx, by = m(0.75, 0.4)
    bk = [(bx - w * 0.07, by), (bx + w * 0.07, by), (bx + w * 0.06, by - w * 0.08), (bx - w * 0.06, by - w * 0.08)]
    out.append(F(bk, PAPER) + H(U, bk, 0, 1.3, 0.6) + pen(bk, 1.0, seed, 0) + P(f"M {f1(bx - w * 0.05)} {f1(by - w * 0.08)} Q {f1(bx)} {f1(by - w * 0.16)} {f1(bx + w * 0.05)} {f1(by - w * 0.08)}", 1.0))
    for k, (u, v, fl) in enumerate(((0.28, 0.5, False), (0.48, 0.45, True))):
        px_, py_ = m(u, v)
        hh = w * 0.3
        out.append(F(smooth_closed([(px_ - hh * 0.16, py_), (px_ + hh * 0.16, py_), (px_ + hh * 0.13, py_ - hh * 0.6), (px_ - hh * 0.13, py_ - hh * 0.6)]), INK, 0.95))
        out.append(f'<circle cx="{f1(px_ + (0.02 if fl else -0.02) * hh)}" cy="{f1(py_ - hh * 0.74)}" r="{f1(hh * 0.13)}" fill="{INK}"/>')
        out.append(P(f"M {f1(px_ - hh * 0.1)} {f1(py_)} l {f1((-1 if fl else 1) * hh * 0.5)} {f1(hh * 0.05)}", max(1.2, hh * 0.1)))
    out.append(F([(x - w * 0.55, y + w * 0.14), (x + w * 0.6, y + w * 0.1), (x + w * 0.5, y + w * 0.16), (x - w * 0.45, y + w * 0.2)], INK, 0.2))
    return "".join(out)


def live_oak(U, cx, base, seed, crown=(170, 78), cy=None, lobe_r=20):
    """A Southern live oak: a short, massive trunk that forks low into long, sinuous, near-horizontal limbs,
    carrying a broad, flat-domed crown much wider than it is tall (clumps ticked and hatched toward the shade)."""
    rnd = random.Random(seed)
    rx, ry = crown
    cy = cy if cy is not None else base - 230
    out = []
    # crown underside in shade first
    under = smooth_closed(scallop_pts(cx + 10, cy + ry * 0.25, rx * 0.95, ry * 0.75, seed + 9, 18, 0.08))
    out.append(F(under, INK, 0.82))
    # trunk and limbs
    fork = (cx + 4, base - 62)

    def bough(pts, w, sd, taper=(1, 0.35)):
        o = nib(pts, w, taper=taper, ramp=0.55, seed=sd, color=INK, cal=0.2)
        o += nib([(x_, y_ - w * 0.16) for x_, y_ in pts], w * 0.6, taper=taper, ramp=0.55, seed=sd, color=PAPER, cal=0.2)
        C_ = cr(pts, False, 2.2)
        ticks = []
        n_ = len(C_)
        for i in range(1, n_ - 1):
            (ax, ay), (bx, by) = C_[i - 1], C_[i + 1]
            L = math.hypot(bx - ax, by - ay) or 1
            ux, uy = (bx - ax) / L, (by - ay) / L
            nx, ny = -uy, ux
            if ny < 0:
                nx, ny = -nx, -ny          # toward the underside
            t = i / n_
            half = w * lerp(taper[0], taper[1], t) * 0.36
            px_, py_ = C_[i]
            a0 = rnd.uniform(-0.75, -0.2) * half
            ticks.append(f"M {f1(px_ + nx * a0)} {f1(py_ + ny * a0)} L {f1(px_ + nx * half + ux * 1.2)} {f1(py_ + ny * half + uy * 1.2)}")
        o += P(" ".join(ticks), 0.8, INK, 0.85)
        return o
    out.append(bough([(cx - 4, base), (cx - 2, base - 30), fork], 42, seed, taper=(1.15, 0.7)))
    limbs = [[fork, (cx - 30, base - 74), (cx - 70, base - 84), (cx - 112, base - 110), (cx - rx * 0.9, cy + ry * 0.6)],
             [fork, (cx + 34, base - 80), (cx + 80, base - 92), (cx + 128, base - 122), (cx + rx * 0.95, cy + ry * 0.55)],
             [fork, (cx + 6, base - 110), (cx + 30, base - 150), (cx + 30, base - 182), (cx + 66, cy + ry * 0.2)],
             [fork, (cx - 10, base - 104), (cx - 34, base - 140), (cx - 30, base - 176), (cx - 62, cy + ry * 0.25)]]
    for k, lb in enumerate(limbs):
        out.append(bough(lb, rnd.uniform(17, 21), seed + k))
    # bark: a few pale fissures on the trunk
    out.append(P(" ".join(f"M {f1(cx - 9 + 5 * k)} {f1(base - 4)} q {f1(rnd.uniform(-3, 3))} -25 {f1(rnd.uniform(-2, 4))} -50" for k in range(4)), 0.8, PAPER, 0.6))
    # crown clumps: rows across a flattened dome, top rows first, edges drooping lower
    spots = []
    rows = 5
    for j in range(rows):
        v = -0.85 + 1.7 * j / (rows - 1)
        half = rx * math.sqrt(max(0.05, 1 - (v * 0.9) ** 2))
        k = max(2, int(2 * half / (lobe_r * 1.35)) + 1)
        for i in range(k):
            u = (i + 0.5) / k
            x = cx - half + 2 * half * u + rnd.uniform(-lobe_r * 0.3, lobe_r * 0.3)
            droop = (abs(x - cx) / rx) ** 2 * ry * 0.45
            spots.append((cy + v * ry * 0.8 + droop + rnd.uniform(-lobe_r * 0.25, lobe_r * 0.25), x))
    spots.sort()
    for i, (y, x) in enumerate(spots):
        r = lobe_r * rnd.uniform(0.9, 1.25)
        out.append(lobe(U, x, y, r, r * rnd.uniform(0.72, 0.86), seed * 17 + i, light=(1, -1), w=1.4, dense=1.4))
    return "".join(out)


@design("atlanta")
def atlanta(U):
    """Midtown from the shore of Lake Clara Meer in Piedmont Park: a great oak spreading over the lawn, the
    towers (One Atlantic Center's copper pyramid, the lattice crown of Bank of America Plaza, a finned glass
    crown, a stepped crown) across the water with broken reflections, the boardwalk dock, ducks, and a
    vermilion picnic blanket under the oak."""
    art = []
    SH = 330          # far shore line
    art.append(cloud(U, 470, 96, 120, 20, 5) + cloud(U, 330, 70, 70, 12, 8))
    art.append(sky_rules(U, 200, 600, 236, SH - 8, 3, op=0.28, g0=9, g1=3.4))
    # back row of pale towers
    back = []
    for i, (a, b, t) in enumerate(((206, 222, 236), (232, 246, 252), (338, 352, 226), (468, 486, 214), (500, 516, 238), (526, 542, 250))):
        back.append(F([(a, t), (b + 3, t), (b + 3, SH), (a, SH)], PAPER) + prism(U, a, b, 3, t, SH, 100 + i, style="grid", dark_p=0.08, w=0.9))
    art.append(f'<g opacity="0.55">{"".join(back)}</g>')
    # the named crowns
    towers = [
        (262, 286, 176, 7, "fin", 200, 6, 26),
        (304, 334, 158, 8, "gothic", 201, 6, 30),
        (366, 388, 170, 6, "stepped", 202, 5, 24),
        (420, 446, 150, 8, "lattice", 203, 5, 30),
        (452, 470, 222, 5, "flat", 204, 4, 16),
        (398, 414, 236, 5, "flat", 205, 3, 13),
    ]
    for x0, x1, top, sw, kind, sd, c, r in sorted(towers, key=lambda t: -t[2]):
        art.append(prism(U, x0, x1, sw, top, SH, sd, cols=c, rows=r, style="slit" if kind in ("gothic", "lattice") else "grid", dark_p=0.15, w=1.3))
        if kind == "gothic":
            art.append(gothic_top(U, x0, x1 + sw, top, sd))
        elif kind == "lattice":
            art.append(lattice_top(U, x0, x1 + sw, top, sd))
        elif kind == "stepped":
            art.append(stepped_top(U, x0, x1 + sw, top, sd))
        elif kind == "fin":
            art.append(fin_top(U, x0, x1 + sw, top, sd))
    # far shore: tree line
    rnd = random.Random(7)
    tl = []
    x = 150
    while x < 600:
        r = rnd.uniform(7, 12)
        tl.append(lobe(U, x, SH - r * 0.5 - rnd.uniform(0, 5), r, r * 0.75, 300 + int(x), light=(-1, -1), w=1.0, dense=1.0))
        x += r * 1.2
    art.append("".join(tl))
    art.append(pen([(140, SH + 1), (600, SH + 1)], 1.2, 8, 0.1))
    # lake with broken reflections of the towers
    water = [(0, SH + 1), (600, SH + 1), (600, 600), (0, 600)]
    refl = [(x0, x1 + sw, 0.55) for x0, x1, top, sw, *_ in towers]
    art.append(ripples(U, 0, 600, SH + 1.5, 470, 9, dens=0.8, gap=(1.8, 8.5), ln=((3, 9), (12, 34)), w=(0.6, 1.3), refl=refl, clip=poly(water)))
    # ducks
    art.append(duck(330, 384, 7, 10) + duck(350, 392, 6, 11, flip=True) + duck(232, 360, 5, 12))
    # boardwalk dock from the right
    C = Cam2(f=330, cx=300, vpy=SH, eye=1.6, yaw=0)
    dk = [C(4.0, 0.8, 6), C(4.0, 0.8, 34), C(7.0, 0.8, 34), C(7.0, 0.8, 6)]
    art.append(F(dk, PAPER) + segs([(C(4.0, 0.8, z), C(7.0, 0.8, z)) for z in [6 + 0.3 * k for k in range(94)]], 0.6, 13, 0, op=0.8))
    side = [C(4.0, 0.8, 6), C(4.0, 0.8, 34), C(4.0, 0.5, 34), C(4.0, 0.5, 6)]
    art.append(F(side, INK, 0.7))
    posts = [(C(4.0, 0.5, z), C(4.0, -0.3, z)) for z in (6, 8, 11, 15, 20, 26, 33)]
    art.append(segs(posts, 1.6, 14, 0))
    for X in (4.0, 7.0):
        art.append(pen([C(X, 1.9, 6), C(X, 1.9, 34)], 1.2, 15, 0.1) + segs([(C(X, 0.8, z), C(X, 1.9, z)) for z in (6, 7.5, 9.3, 11.5, 14.4, 18, 22.5, 28, 34)], 1.0, 16, 0))
    for X, Z, sd, fl in ((5.6, 26, 1, False), (5.2, 19, 2, True), (5.9, 14, 3, False)):
        art.append(ppl(C, X, Z, 20 + sd, Y=0.8, flip=fl, bag=sd == 2))
    # near shore lawn (bottom left), the oak, the picnic
    lawn_top = [(-10, 398), (90, 400), (170, 406), (240, 418), (300, 436), (340, 460)]
    ld = smooth_open(lawn_top) + " L 340 620 L -10 620 Z"
    art.append(F(ld, PAPER))
    gl = []
    for i in range(500):
        x = rnd.uniform(-10, 330)
        y = rnd.uniform(396, 470)
        L = lerp(3, 7, (y - 396) / 74)
        gl.append(((x, y), (x + rnd.uniform(-1, 1), y - L)))
    art.append(clipped(U("lw"), ld, segs(gl, 0.7, 17, 0.2, op=0.8) + H(U, ld, 0, (3.4, 2.0), 0.55, op=0.5, box=(-10, 396, 340, 480), dark=(0, 480))))
    art.append(P(smooth_open(lawn_top), 1.6))
    art.append(P(smooth_open([(x, y + 4) for x, y in lawn_top]), 0.8, INK, 0.7))
    # the oak: a broad crown over the lawn, its shadow pooled on the grass
    art.append(F(smooth_closed([(0, 416), (150, 408), (250, 420), (130, 436), (0, 432)]), INK, 0.25))
    art.append(live_oak(U, 92, 424, 400, crown=(168, 72), cy=176, lobe_r=19))
    art.append(picnic(U, 218, 420, 62, 18))
    art.append(bird(380, 120, 6, 30) + bird(398, 108, 5, 31))
    return plate(U, "atlanta", art, 111)


# ================================================================ DENVER
def snow_range(U, pts, base, seed, op=1.0, snow_k=0.45, gap=1.8):
    """An engraved mountain range from a fine ridgeline: the major summits are found along it, each summit's
    right-hand flank (away from the light) is hatched dark along the fall line, the lit flanks stay paper above
    a ragged snowline and take sparse forest hatching below it; rock ribs fall from the summits."""
    rnd = random.Random(seed)
    d = poly(pts + [(pts[-1][0], base + 2), (pts[0][0], base + 2)])
    top = min(p[1] for p in pts)
    sl = top + (base - top) * snow_k
    n = len(pts)
    W = 4
    summ = [i for i in range(n) if pts[i][1] <= min(p[1] for p in pts[max(0, i - W):i + W + 1])]
    sadd = [i for i in range(n) if pts[i][1] >= max(p[1] for p in pts[max(0, i - W):i + W + 1])]
    snowline = [(x, sl + 7 * math.sin(x / 13 + seed) + rnd.uniform(-5, 5)) for x in range(int(pts[0][0]) - 4, int(pts[-1][0]) + 8, 6)]
    below = poly(snowline + [(pts[-1][0] + 8, base + 5), (pts[0][0] - 4, base + 5)])
    inner = [H(U, d, 72, gap * 2.8, 0.55, box=(pts[0][0], top, pts[-1][0], base), wob=0.4, brk=0.3, op=0.75, clip2=below)]
    for si in summ:
        nxt = [j for j in sadd if j > si]
        if not nxt:
            continue
        vi = nxt[0]
        sx_, sy_ = pts[si]
        vx_, vy_ = pts[vi]
        if vx_ - sx_ < 4:
            continue
        sh = pts[si:vi + 1] + [(vx_ - (vx_ - sx_) * 0.1, base + 2), (sx_ + (vx_ - sx_) * 0.25, base + 2)]
        b = bbox(sh)
        inner.append(H(U, sh, 64, (gap * 1.5, gap * 0.75), (0.55, 0.85), box=b, dark=(vx_, base), wob=0.3, brk=0.12))
        inner.append(H(U, sh, 128, gap * 1.8, 0.55, box=b, dark=(vx_, base), span=(0.35, 1), wob=0.3, brk=0.2, op=0.7, clip2=below))
        # ribs falling down-left from the summit across the lit face
        for k in range(rnd.randint(1, 3)):
            ang = math.radians(rnd.uniform(100, 125))
            L = (base - sy_) * rnd.uniform(0.25, 0.55)
            rib = [(sx_ - k * 2, sy_ + 2), (sx_ + math.cos(ang) * L * 0.5, sy_ + math.sin(ang) * L * 0.5), (sx_ + math.cos(ang) * L, sy_ + math.sin(ang) * L)]
            inner.append(nib(rib, rnd.uniform(1.0, 1.8), taper=(0.3, 0.2), ramp=0.4, seed=seed + si + k, color=INK, op=0.8))
    cv = []
    for _ in range(60):
        x = rnd.uniform(pts[0][0], pts[-1][0])
        y = rnd.uniform(top, sl)
        cv.append(f"M {f1(x)} {f1(y)} q 2 1 4.5 0.4")
    inner.append(P(" ".join(cv), 0.5, INK, 0.55))
    out = F(d, PAPER) + clipped(U("sr"), d, "".join(inner)) + pen(pts, 1.5, seed, 0.1)
    return f'<g opacity="{op:.2f}">{out}</g>'


def balloon(x, y, r, seed, U):
    d = smooth_closed([(x, y - r), (x + r * 0.85, y - r * 0.25), (x + r * 0.5, y + r * 0.75), (x, y + r), (x - r * 0.5, y + r * 0.75), (x - r * 0.85, y - r * 0.25)])
    return (F(d, PAPER) + accent(U, d, (x - r, y - r, x + r, y + r), seed, op=0.95, ang=-60, n=5, length=(3, 6), width=(1, 2))
            + P(d, 1.0) + P(f"M {f1(x - r * 0.35)} {f1(y - r * 0.4)} q {f1(r * 0.1)} {f1(-r * 0.3)} {f1(r * 0.4)} {f1(-r * 0.35)}", 0.8, PAPER))


@design("denver")
def denver(U):
    """Late afternoon down 17th Street: LoDo brick warehouses with fire escapes on the left in shade, a lower
    lit row with patio trees on the right, Union Station closing the street across its plaza (three great
    arched windows, clock, granite base, long wings), and the snowy Front Range spread along the horizon
    behind it; a child with a vermilion balloon, strollers, a cyclist."""
    C = Cam2(f=300, cx=300, vpy=350, eye=1.6, yaw=4)
    LIGHT = (0.6, 0.8)                         # low sun behind the station (from the west)
    art = []
    HZ = C.vpy
    art.append(cloud(U, 150, 92, 120, 20, 5) + cloud(U, 430, 74, 110, 16, 6))
    # the Front Range across the horizon: the high snowy range (broader massifs left and right), the darker
    # forested foothills in front
    def peaks_ridge(x0, x1, yb, specs, seed, noise=2.5):
        rnd_ = random.Random(seed)
        out_ = []
        x = x0
        while x <= x1:
            h_ = max([0.0] + [ph * max(0.0, 1 - abs(x - pc) / pw) ** 0.85 for pc, ph, pw in specs])
            out_.append((x, yb - h_ + rnd_.uniform(-noise, noise)))
            x += 3
        return out_
    rs = random.Random(57)
    specs = []
    x = -20
    while x < 640:
        big = 1.0 + 0.9 * math.exp(-((x - 215) / 70) ** 2) + 0.6 * math.exp(-((x - 455) / 80) ** 2)
        specs.append((x, rs.uniform(22, 38) * big, rs.uniform(44, 74)))
        x += rs.uniform(30, 50)
    hi = peaks_ridge(-10, 610, HZ - 92, specs, 51)
    art.append(snow_range(U, hi, HZ - 30, 5, op=0.8, snow_k=0.42, gap=1.9))
    lo = peaks_ridge(-10, 610, HZ - 40, [(x_, rs.uniform(8, 20), rs.uniform(30, 60)) for x_ in range(-20, 640, 36)], 52, noise=1.2)
    art.append(snow_range(U, lo, HZ - 8, 6, op=0.95, snow_k=-0.2, gap=1.5))
    rnd0 = random.Random(53)
    trees_ = []
    for i in range(500):
        x = rnd0.uniform(-10, 610)
        ytop_ = min(y for xx, y in lo if abs(xx - x) < 6) if any(abs(xx - x) < 6 for xx, y in lo) else HZ - 44
        y = rnd0.uniform(ytop_ + 2, HZ - 10)
        h_ = rnd0.uniform(2.5, 5)
        trees_.append(f"M {f1(x - h_ * 0.35)} {f1(y)} L {f1(x)} {f1(y - h_)} L {f1(x + h_ * 0.35)} {f1(y)} Z")
    art.append(f'<path d="{" ".join(trees_)}" fill="{INK}" opacity="0.6"/>')
    # --- Union Station across the plaza
    ZF = 84.0
    HX = 0.0
    for wx0, wx1 in ((HX - 70, HX - 22), (HX + 22, HX + 70)):
        for q, nrm, _ in vis_faces(C, box(wx0, wx1, ZF + 3, ZF + 20), 0, 12):
            t = tone_of(nrm, LIGHT)
            art.append(F(q, PAPER) + segs(qlines(q, [k / 14 for k in range(1, 14)]), 0.5, 9, 0, op=0.5))
            if abs(nrm[1]) > 0.9:
                m = homog(q)
                n = 12
                wins = []
                for i in range(n):
                    for v0, v1 in ((0.2, 0.46), (0.6, 0.92)):
                        wins.append(arch_q([m((i + 0.25) / n, v0), m((i + 0.75) / n, v0), m((i + 0.75) / n, v1), m((i + 0.25) / n, v1)], 0.35, 6))
                art.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.82"/>')
                art.append(segs([(m(0, 0.53), m(1, 0.53)), (m(0, 0.1), m(1, 0.1))], 1.0, 10, 0))
            art.append(shade(U, q, t, 90, 11) + sketch(q, 1.3, 12, 0.4))
        rf = [C(wx0, 12, ZF + 3), C(wx1, 12, ZF + 3), C(wx1, 15, ZF + 11), C(wx0, 15, ZF + 11)]
        art.append(F(rf, PAPER) + H(U, rf, 0, 1.4, 0.6) + sketch(rf, 1.1, 13, 0.3))
    hall = box(HX - 22, HX + 22, ZF, ZF + 24)
    for q, nrm, _ in vis_faces(C, hall, 0, 21):
        t = tone_of(nrm, LIGHT)
        art.append(F(q, PAPER))
        m = homog(q)
        art.append(segs(qlines(q, [k / 26 for k in range(1, 26)]), 0.5, 14, 0, op=0.45))
        art.append(segs(qlines(quad_sub3(q, 0, 0.8, 1, 1), [k / 6 for k in range(1, 6)]), 0.8, 15, 0, op=0.8))
        art.append(shade(U, q, t, 90, 19))
        if abs(nrm[1]) > 0.9:
            for i in range(3):
                u0, u1 = 0.08 + i * 0.3, 0.08 + i * 0.3 + 0.24
                wq = [m(u0, 0.16), m(u1, 0.16), m(u1, 0.78), m(u0, 0.78)]
                ar = arch_q(wq, 0.3, 14)
                art.append(F(ar, INK, 0.86))
                mm = homog(wq)
                art.append(segs([(mm(k / 4, 0.12), mm(k / 4, 1)) for k in range(1, 4)] + [(mm(0, v), mm(1, v)) for v in (0.42, 0.62, 0.82)], 0.8, 16 + i, 0, color=PAPER, op=0.75))
                art.append(pen(ar, 1.4, 17 + i, 0.05, closed=True))
                art.append(pen(arch_q(quad_sub3(q, u0 - 0.02, 0.14, u1 + 0.02, 0.8), 0.3, 14), 0.9, 18 + i, 0.05))
            cc = m(0.5, 0.085)
            cr_ = abs(m(0.545, 0.085)[0] - cc[0])
            art.append(f'<circle cx="{f1(cc[0])}" cy="{f1(cc[1])}" r="{f1(cr_)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>'
                       + P(f"M {f1(cc[0])} {f1(cc[1])} l 0 {f1(-cr_ * 0.7)} M {f1(cc[0])} {f1(cc[1])} l {f1(cr_ * 0.45)} {f1(cr_ * 0.2)}", 1.0))
            for i in range(3):
                u0 = 0.14 + i * 0.3
                art.append(F(quad_sub3(q, u0, 0.84, u0 + 0.12, 1.0), INK, 0.9))
        art.append(sketch(q, 1.7, 20, 0.5))
    for q, nrm, _ in vis_faces(C, [(HX - 22.6, ZF - 0.6), (HX + 22.6, ZF - 0.6), (HX + 22.6, ZF + 24.6), (HX - 22.6, ZF + 24.6)], 21, 22.4):
        art.append(F(q, PAPER) + H(U, q, 0, 1.2, 0.6) + sketch(q, 1.2, 21, 0.3))
    for q, nrm, _ in vis_faces(C, box(HX - 21, HX + 21, ZF + 1, ZF + 23), 22.4, 23.8):
        art.append(F(q, PAPER) + segs(qlines(q, [k / 70 for k in range(1, 70)], "v"), 0.55, 22, 0) + sketch(q, 1.0, 22, 0.3))
    # the plaza in front, with fountain jets
    plaza = [C(-30, 0, 66), C(-30, 0, ZF), C(30, 0, ZF), C(30, 0, 66)]
    art.append(F(plaza, PAPER) + segs([(C(-30, 0, z), C(30, 0, z)) for z in [66 + 1.5 * k for k in range(12)]], 0.5, 23, 0, op=0.5))
    rnd = random.Random(30)
    jets, spray = [], []
    for i in range(7):
        for j in range(3):
            X, Z = -12 + i * 4, 70 + j * 3.6
            x, y = C(X, 0, Z)
            hh = C.px(X, Z, rnd.uniform(1.4, 2.4))
            jets.append(f"M {f1(x)} {f1(y)} q {f1(hh * 0.05)} {f1(-hh * 0.7)} {f1(hh * 0.12)} {f1(-hh)}")
            for _ in range(5):
                spray.append(f'<circle cx="{f1(x + rnd.uniform(-hh * 0.3, hh * 0.35))}" cy="{f1(y - hh * rnd.uniform(0.5, 1.05))}" r="{rnd.uniform(0.35, 0.7):.2f}"/>')
    art.append(P(" ".join(jets), 0.8, INK, 0.85) + f'<g fill="{INK}" opacity="0.7">{"".join(spray)}</g>')
    # 17th Street: roadway and sidewalks
    road = [C(-8, 0, 7), C(-8, 0, 66), C(8, 0, 66), C(8, 0, 7)]
    art.append(F(road, PAPER) + H(U, road, 0, (3.0, 1.4), 0.6, op=0.55, box=(0, 340, 600, 560), dark=(300, 560)))
    dash = []
    z = 7.0
    while z < 70:
        dash.append(poly([C(-0.08, 0, z), C(0.08, 0, z), C(0.08, 0, z + 2.5), C(-0.08, 0, z + 2.5)]))
        z += 6
    art.append(f'<path d="{" ".join(dash)}" fill="{INK}" opacity="0.75"/>')
    for sx in (-1, 1):
        wk = [C(sx * 8, 0.15, 5), C(sx * 8, 0.15, 70), C(sx * 14, 0.15, 70), C(sx * 14, 0.15, 5)]
        art.append(F(wk, PAPER) + segs([(C(sx * 8, 0.15, z), C(sx * 14, 0.15, z)) for z in [5 + 1.5 * k for k in range(44)]], 0.55, 24, 0, op=0.5))
        art.append(pen([C(sx * 8, 0.15, 5), C(sx * 8, 0.15, 70)], 1.4, 25, 0.1))
    # left: tall LoDo brick warehouses in shade, with fire escapes
    for k, (z0, z1, h, fl) in enumerate(((50, 66, 12, 3), (32, 50, 16, 4), (12, 32, 14, 4))):
        q = C.qx(-14, z0, z1, 0, h)
        art.append(brick_face(U, C, q, 30 + k, t=0.7))
        m = homog(q)
        nb = int((z1 - z0) / 3)
        wins = []
        for j in range(1, fl):
            for i in range(nb):
                wins.append(arch_q([m((i + 0.25) / nb, (j + 0.25) / fl - 1 / fl), m((i + 0.75) / nb, (j + 0.25) / fl - 1 / fl),
                                    m((i + 0.75) / nb, (j + 0.85) / fl - 1 / fl), m((i + 0.25) / nb, (j + 0.85) / fl - 1 / fl)], 0.3, 5))
        art.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.9"/>')
        art.append(f'<path d="{" ".join(poly(quad_sub3(q, (i + 0.15) / nb, 1 - 0.8 / fl, (i + 0.85) / nb, 1)) for i in range(nb))}" fill="{INK}" opacity="0.85"/>')
        # fire escape: landings and zig-zag stairs on the middle bays
        zm = (z0 + z1) / 2
        fe = []
        for j in range(1, fl):
            yy = h * j / fl + 0.2
            fe.append((C(-13.2, yy, zm - 2.5), C(-13.2, yy, zm + 2.5)))
            fe.append((C(-13.2, yy + 0.9, zm - 2.5), C(-13.2, yy + 0.9, zm + 2.5)))
            if j < fl - 1:
                a_, b_ = (zm - 2.3, zm + 2.3) if j % 2 else (zm + 2.3, zm - 2.3)
                fe.append((C(-13.2, yy, a_), C(-13.2, h * (j + 1) / fl + 0.2, b_)))
        art.append(segs(fe, 1.1, 40 + k, 0))
        cor = [C(-14, h, z0), C(-14, h, z1), C(-13.2, h + 0.6, z1), C(-13.2, h + 0.6, z0)]
        art.append(F(cor, PAPER) + H(U, cor, 0, 1.2, 0.6) + pen([cor[3], cor[2]], 1.4, 41, 0.1))
        art.append(pen([C(-14, 0, z0), C(-14, h, z0)], 1.8, 42, 0.1))
        art.append(F(C.qz(z0, -40, -14, 0, h), PAPER) if False else "")
    # right: lower lit row with a patio and street trees
    for k, (z0, z1, h) in enumerate(((48, 66, 12), (30, 48, 9), (12, 30, 14))):
        art.append(commercial(U, C, 14, z0, z1, h, 50 + k, lambda Z: 0.0, floors=3, t=0.1, arch=k != 1, awning=k == 1, ang=105))
    for z in (62, 44, 27, 15):
        x, y = C(10.6, 0.15, z)
        art.append(canopy(U, x, y, C.px(10.6, z, 7.5), C.px(10.6, z, 5.5), 700 + z, light=(-1, -1), lobe_r=max(6, C.px(10.6, z, 1.1)), lw=1.1))
    for z in (58, 38, 20):
        art.append(plamp(C, -8.6, z, 60 + z, "lantern", 4.4))
    # people, a cyclist, the child with the balloon
    for X, Z, sd, fl in ((-11, 60, 1, False), (-10.5, 40, 2, True), (11.5, 52, 3, False), (12, 33, 4, True), (-12, 24, 5, False),
                         (4, 74, 6, True), (-6, 76, 7, False), (12, 78, 8, True)):
        art.append(ppl(C, X, Z, 70 + sd, Y=0.15, flip=fl, bag=sd in (3, 5)))
    x, y = C(3.0, 0, 30)
    art.append(cyclist(x, y, C.px(3.0, 30, 1.75), 79))
    for X, Z, sd in ((-4, 52, 1), (4.2, 44, 2), (-4.4, 22, 3)):
        x, y = C(X, 0, Z)
        art.append(car_rear(U, x, y, C.px(X, Z, 1.9), 85 + sd))
    X, Z = 10.2, 17.5
    x, y = C(X, 0.15, Z)
    hp = C.px(X, Z, 1.1)
    art.append(person(x, y, hp, 80))
    art.append(ppl(C, X + 0.7, Z + 0.3, 81, Y=0.15, flip=True))
    bx, by = x - hp * 0.4, y - hp * 2.5
    art.append(P(f"M {f1(x - hp * 0.12)} {f1(y - hp * 0.6)} Q {f1(x - hp * 0.5)} {f1(y - hp * 1.4)} {f1(bx)} {f1(by + hp * 0.32)}", 0.8))
    art.append(balloon(bx, by, hp * 0.32, 82, U))
    art.append(bird(250, 176, 6, 90) + bird(270, 162, 5, 91))
    return plate(U, "denver", art, 121)


# ================================================================ SEATTLE
def gable_shed(U, C, xa, xb, z0, z1, eave, ridge, seed, light, arch=True):
    """A waterfront pier shed: long gabled building (ridge along X) on a pile-supported deck; the near long
    wall with windows, the shoreward gable with a great arched door, the roof seen from above."""
    out = []
    zc = (z0 + z1) / 2
    # deck and piles
    deck = [C(xa - 2, 0.9, z0 - 3), C(xb + 3, 0.9, z0 - 3), C(xb + 3, 0.9, z1 + 3), C(xa - 2, 0.9, z1 + 3)]
    out.append(F(deck, PAPER) + pen([deck[0], deck[1]], 1.0, seed, 0.1))
    piles = []
    for X in range(int(xa), int(xb) + 4, 3):
        a_, b_ = C(X, 0.9, z0 - 3), C(X, -0.6, z0 - 3)
        piles.append((a_, b_))
    out.append(segs(piles, 1.0, seed, 0) + F([C(xa - 2, 0.9, z0 - 3), C(xb + 3, 0.9, z0 - 3), C(xb + 3, 0.2, z0 - 3), C(xa - 2, 0.2, z0 - 3)], INK, 0.6))
    # near long wall
    wall = C.qz(z0, xa, xb, 0.9, eave)
    t = tone_of((0, -1), light)
    out.append(F(wall, PAPER) + segs(qlines(wall, [k / 40 for k in range(1, 40)], "v"), 0.5, seed, 0, op=0.55))
    m = homog(wall)
    n = max(4, int((xb - xa) / 5))
    wins = [arch_q([m((i + 0.3) / n, 0.25), m((i + 0.7) / n, 0.25), m((i + 0.7) / n, 0.65), m((i + 0.3) / n, 0.65)], 0.35, 5) for i in range(n)]
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.82"/>')
    out.append(shade(U, wall, t, 90, seed) + sketch(wall, 1.2, seed, 0.3))
    # shoreward gable end
    g = [C(xb, 0.9, z0), C(xb, eave, z0), C(xb, ridge, zc), C(xb, eave, z1), C(xb, 0.9, z1)]
    out.append(F(g, PAPER) + segs([(C(xb, 0.9, z), C(xb, min(eave + (ridge - eave) * (1 - abs(z - zc) / (zc - z0)), ridge), z)) for z in [z0 + k * 0.7 for k in range(1, int((z1 - z0) / 0.7))]], 0.5, seed, 0, op=0.55))
    if arch:
        dq = C.qx(xb, zc - 4.5, zc + 4.5, 0.9, eave + 1.5)
        out.append(F(arch_q(dq, 0.4, 10), INK, 0.85))
        for zz in (zc - 8, zc + 8):
            out.append(F(arch_q(C.qx(xb, zz - 1.2, zz + 1.2, 4, 8), 0.4, 6), INK, 0.85))
    out.append(shade(U, g, tone_of((1, 0), light), 90, seed) + pen(g, 1.4, seed, 0.1, closed=True))
    # roof seen from above (near slope), standing seams
    rf = [C(xa, eave, z0), C(xb, eave, z0), C(xb, ridge, zc), C(xa, ridge, zc)]
    out.append(F(rf, PAPER) + segs(qlines(rf, [k / 50 for k in range(1, 50)], "v"), 0.55, seed, 0, op=0.75) + sketch(rf, 1.3, seed, 0.3))
    return "".join(out)


def tug(U, x, wl, s, seed):
    """A little harbour tug in the vermilion accent: tall wheelhouse, stack, fender bow, white bone in her teeth."""
    k = s
    hull = [(x - k, wl - k * 0.28), (x + k * 0.95, wl - k * 0.38), (x + k * 0.8, wl), (x - k * 0.85, wl)]
    out = [F(hull, PAPER), accent(U, poly(hull), bbox(hull), seed, op=0.95, ang=0, n=8, length=(4, 10), width=(1, 2.5)), pen(hull, 1.2, seed, 0.1, closed=True)]
    cab = [(x - k * 0.5, wl - k * 0.3), (x + k * 0.25, wl - k * 0.34), (x + k * 0.25, wl - k * 0.75), (x - k * 0.4, wl - k * 0.75)]
    wh = [(x - k * 0.25, wl - k * 0.75), (x + k * 0.2, wl - k * 0.75), (x + k * 0.2, wl - k * 1.05), (x - k * 0.2, wl - k * 1.05)]
    out.append(F(cab, PAPER) + F(quad_sub3(cab, 0.1, 0.25, 0.9, 0.55), INK, 0.85) + pen(cab, 1.1, seed, 0, closed=True))
    out.append(F(wh, PAPER) + F(quad_sub3(wh, 0.1, 0.3, 0.9, 0.7), INK, 0.85) + pen(wh, 1.1, seed, 0, closed=True))
    st = [(x - k * 0.62, wl - k * 0.3), (x - k * 0.5, wl - k * 0.3), (x - k * 0.52, wl - k * 0.95), (x - k * 0.64, wl - k * 0.95)]
    out.append(F(st, INK, 0.9))
    out.append(P(f"M {f1(x + k * 0.9)} {f1(wl - 1)} q {f1(k * 0.4)} {f1(k * 0.15)} {f1(k * 1.0)} {f1(k * 0.25)} M {f1(x - k * 0.85)} {f1(wl + 1)} q {f1(-k * 0.6)} {f1(k * 0.1)} {f1(-k * 1.6)} {f1(k * 0.12)}", 1.0))
    return "".join(out)


def wsf_ferry(U, x0, x1, wl, seed):
    """A big Puget Sound ferry broadside: long white hull with a dark band, car deck, two cabin decks with
    runs of windows, a pilothouse at each end and the central stack."""
    L = x1 - x0
    h = L * 0.05
    out = []
    hull = [(x0 - L * 0.02, wl - h * 1.2), (x1 + L * 0.02, wl - h * 1.2), (x1 - L * 0.04, wl), (x0 + L * 0.04, wl)]
    out.append(F(hull, PAPER) + F(quad_sub3(hull, 0, 0.55, 1, 1), INK, 0.85) + sketch(hull, 1.2, seed, 0.2))
    cd = [(x0, wl - h * 2.4), (x1, wl - h * 2.4), (x1, wl - h * 1.2), (x0, wl - h * 1.2)]
    out.append(F(cd, PAPER) + sketch(cd, 1.0, seed, 0.2))
    n = 14
    m = homog(cd)
    out.append(f'<path d="{" ".join(poly([m((i + 0.1) / n, 0.2), m((i + 0.9) / n, 0.2), m((i + 0.9) / n, 0.95), m((i + 0.1) / n, 0.95)]) for i in range(n))}" fill="{INK}" opacity="0.8"/>')
    for k, (a, b, y0, y1) in enumerate(((0.06, 0.94, 2.4, 3.6), (0.14, 0.86, 3.6, 4.6))):
        q = [(x0 + L * a, wl - h * y1), (x0 + L * b, wl - h * y1), (x0 + L * b, wl - h * y0), (x0 + L * a, wl - h * y0)]
        mq = homog(q)
        nn = int(L * (b - a) / 4)
        out.append(F(q, PAPER) + f'<path d="{" ".join(poly([mq((i + 0.2) / nn, 0.3), mq((i + 0.8) / nn, 0.3), mq((i + 0.8) / nn, 0.7), mq((i + 0.2) / nn, 0.7)]) for i in range(nn))}" fill="{INK}" opacity="0.85"/>'
                   + sketch(q, 1.0, seed + k, 0.2))
    for px_ in (x0 + L * 0.14, x1 - L * 0.22):
        ph = [(px_, wl - h * 5.6), (px_ + L * 0.08, wl - h * 5.6), (px_ + L * 0.08, wl - h * 4.6), (px_, wl - h * 4.6)]
        out.append(F(ph, PAPER) + F(quad_sub3(ph, 0.1, 0.25, 0.9, 0.65), INK, 0.85) + sketch(ph, 1.0, seed + 5, 0.2))
    fx = (x0 + x1) / 2
    fn = [(fx - L * 0.03, wl - h * 4.6), (fx - L * 0.025, wl - h * 6.8), (fx + L * 0.03, wl - h * 6.8), (fx + L * 0.035, wl - h * 4.6)]
    out.append(F(fn, PAPER) + F(quad_sub3(fn, 0, 0, 1, 0.22), INK) + H(U, fn, 90, 1.2, 0.6, span=(0.5, 1), dark=(fx + 20, wl)) + sketch(fn, 1.0, seed + 6, 0.2))
    out.append(P(f"M {f1(x0 + L * 0.04)} {f1(wl + 1)} q {f1(-L * 0.2)} {f1(h * 0.5)} {f1(-L * 0.55)} {f1(h * 0.7)} M {f1(x0 + L * 0.1)} {f1(wl + 2)} q {f1(-L * 0.25)} {f1(h * 1.2)} {f1(-L * 0.6)} {f1(h * 1.8)}"
                 f" M {f1(x1 - L * 0.03)} {f1(wl)} q {f1(L * 0.06)} {f1(h * 0.4)} {f1(L * 0.14)} {f1(h * 0.6)}", 1.0, INK, 0.85))
    return "".join(out)


def rainier(U, cx, top, base, half, seed, op=0.85):
    """Mount Rainier as engraved: a broad, heavy massif with a flattened summit dome (Liberty Cap a little lower
    at left), Little Tahoma as a sharp shoulder on the right, glaciers left as paper and broken by crevasse
    ticks, dark rock cleavers splitting them, the east flank hatched in shade and the forested foot in haze."""
    rnd = random.Random(seed)
    Hh = base - top
    prof = [(-1.0, 1.0), (-0.86, 0.9), (-0.72, 0.79), (-0.58, 0.66), (-0.46, 0.52), (-0.36, 0.38), (-0.27, 0.25), (-0.2, 0.15), (-0.15, 0.1),
            (-0.11, 0.075), (-0.07, 0.07), (-0.04, 0.035), (0.0, 0.0), (0.06, 0.005), (0.12, 0.03), (0.18, 0.08), (0.24, 0.16), (0.3, 0.25),
            (0.34, 0.29), (0.37, 0.26), (0.4, 0.3), (0.46, 0.4), (0.56, 0.53), (0.68, 0.66), (0.82, 0.8), (1.0, 0.94)]
    pts = []
    for i, (u, v) in enumerate(prof):
        j = rnd.uniform(-0.008, 0.008) if 0 < i < len(prof) - 1 else 0
        pts.append((cx + u * half, top + (v + j) * Hh))
    ridge = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(abs(bx - ax) / 6))
        for i in range(n):
            t = i / n
            ridge.append((lerp(ax, bx, t) + rnd.uniform(-0.6, 0.6), lerp(ay, by, t) + rnd.uniform(-0.8, 0.8) * (0.3 + abs(ax - cx) / half)))
    ridge.append(pts[-1])
    d = poly(ridge + [(cx + half, base + 2), (cx - half, base + 2)])
    inner = []
    # shade on the right (east) flank, densest under Little Tahoma
    inner.append(H(U, d, 60, (3.6, 1.5), (0.55, 0.85), box=(cx - half * 0.05, top, cx + half, base), span=(0.45, 1), dark=(cx + half, base), wob=0.4, brk=0.2))
    inner.append(H(U, d, 128, 3.0, 0.55, box=(cx + half * 0.2, top, cx + half, base), span=(0.55, 1), dark=(cx + half, base), wob=0.4, brk=0.3, op=0.75))
    # cleavers: dark tapering rock ribs fanning out from below the summit, longer on the shaded side
    for k in range(17):
        f = (k + 0.5) / 17
        x0 = cx + (f - 0.5) * half * 0.55 + rnd.uniform(-4, 4)
        y0 = top + Hh * (0.05 + abs(f - 0.5) * 0.28 + rnd.uniform(0, 0.06))
        ang = math.radians(lerp(128, 50, f) + rnd.uniform(-5, 5))
        L = Hh * rnd.uniform(0.3, 0.7) / max(0.45, math.sin(ang))
        mid = (x0 + math.cos(ang) * L * 0.5 + rnd.uniform(-3, 3), y0 + math.sin(ang) * L * 0.5)
        end = (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L)
        inner.append(nib([(x0, y0), mid, end], rnd.uniform(1.8, 3.4) * (1.3 if f > 0.5 else 0.85), taper=(0.15, 0.5), ramp=0.45, seed=seed + k, color=INK, op=0.88))
        # a few branching spurs
        if rnd.random() < 0.6:
            a2 = ang + rnd.choice((-1, 1)) * math.radians(rnd.uniform(18, 30))
            L2 = L * rnd.uniform(0.2, 0.35)
            inner.append(nib([mid, (mid[0] + math.cos(a2) * L2, mid[1] + math.sin(a2) * L2)], 1.4, taper=(0.6, 0.2), seed=seed + 40 + k, color=INK, op=0.8))
    # crevasse ticks in arcs across the glaciers
    cv = []
    for _ in range(140):
        y = top + Hh * rnd.uniform(0.04, 0.6)
        w_ = (y - top) / Hh * half * 1.1
        x = cx + rnd.uniform(-w_, w_ * 0.5)
        L = rnd.uniform(3, 7)
        cv.append(f"M {f1(x)} {f1(y)} q {f1(L / 2)} {f1(1.2)} {f1(L)} 0")
    inner.append(P(" ".join(cv), 0.55, INK, 0.6))
    # the forested foothills and haze at the foot
    fh = []
    for x in range(int(cx - half), int(cx + half), 2):
        hgt = rnd.uniform(3, 9) + 6 * math.sin(x / 31) ** 2
        fh.append(((x, base), (x + rnd.uniform(-0.6, 0.6), base - hgt)))
    inner.append(segs(fh, 0.8, seed + 30, 0.2, op=0.8))
    out = F(d, PAPER) + clipped(U("rn"), d, "".join(inner)) + pen(ridge[1:-1], 1.7, seed, 0.1)
    return f'<g opacity="{op:.2f}">{out}</g>'


def pier_shed(U, C, XW, Z0, Z1, seed, deck=2.3, eave=10.0, ridge=15.5, width=22.0):
    """A Seattle pier shed seen from its own apron: the long board-and-batten wall (lit by the low western
    sun) with big arched windows, cargo doors, pilasters and a bracketed eave; the clerestory monitor above;
    the near gable end in shade with its great arched portal and oculus."""
    rnd = random.Random(seed)
    out = []
    xr = XW - width / 2
    # clerestory monitor (behind, above the eave)
    cl = C.qx(XW - 6.5, Z0 + 1, Z1, eave + 2.0, eave + 4.4)
    out.append(F(cl, PAPER) + segs(qlines(cl, [k / 60 for k in range(1, 60)], "v"), 0.45, seed, 0, op=0.5))
    m = homog(cl)
    nb = int((Z1 - Z0) / 2.5)
    out.append(f'<path d="{" ".join(poly([m((i + 0.25) / nb, 0.25), m((i + 0.75) / nb, 0.25), m((i + 0.75) / nb, 0.8), m((i + 0.25) / nb, 0.8)]) for i in range(nb))}" fill="{INK}" opacity="0.8"/>')
    out.append(sketch(cl, 1.0, seed, 0.2))
    cr_ = [C(XW - 6.5, eave + 4.4, Z0 + 1), C(XW - 6.5, eave + 4.4, Z1), C(XW - 5.8, eave + 4.0, Z1), C(XW - 5.8, eave + 4.0, Z0 + 1)]
    out.append(F(cr_, INK, 0.8))
    # the long wall
    wall = C.qx(XW, Z0, Z1, deck, eave)
    out.append(F(wall, PAPER))
    bat = []
    z = Z0
    while z < Z1:
        a_, b_ = C(XW, deck, z), C(XW, eave, z)
        if abs(C(XW, deck, z + 0.45)[0] - a_[0]) > 1.3:
            bat.append((a_, b_))
        z += 0.45
    out.append(segs(bat, 0.45, seed, 0, op=0.55))
    bay = 5.0
    wins, doors, pil, bars = [], [], [], []
    z = Z0 + 0.8
    k = 0
    while z + bay * 0.8 < Z1:
        q = C.qx(XW, z + 1.0, z + 4.0, 4.6, 8.8)
        ar = arch_q(q, 0.32, 10)
        wins.append(ar)
        mq = homog(q)
        if abs(q[1][0] - q[0][0]) > 6:
            bars += [(mq(u, 0.12), mq(u, 1)) for u in (0.25, 0.5, 0.75)] + [(mq(0, v), mq(1, v)) for v in (0.45, 0.72)]
        dq = C.qx(XW, z + 1.1, z + 3.9, deck, 4.1)
        doors.append((dq, k % 2 == 0))
        a_, b_ = C(XW + 0.15, deck, z), C(XW + 0.15, eave, z)
        pil.append((a_, b_))
        z += bay
        k += 1
    out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.86"/>')
    out.append(segs(bars, 0.7, seed, 0, color=PAPER, op=0.8))
    for w in wins:
        out.append(pen(w, 1.0, seed, 0.05))
    for dq, dark in doors:
        if dark:
            out.append(F(dq, INK, 0.8))
        else:
            out.append(F(dq, PAPER) + segs(qlines(dq, [0.25, 0.5, 0.75], "v") + [(dq[0], dq[2]), (dq[1], dq[3])], 0.6, seed, 0, op=0.8) + pen(dq, 0.9, seed, 0.05, closed=True))
    out.append(segs(pil, 1.6, seed, 0))
    # bracketed eave
    ev = [C(XW, eave, Z0), C(XW, eave, Z1), C(XW + 0.9, eave + 0.2, Z1), C(XW + 0.9, eave + 0.2, Z0)]
    out.append(F(ev, INK, 0.82))
    br = []
    z = Z0 + 0.4
    while z < Z1:
        a_, b_ = C(XW, eave - 0.8, z), C(XW + 0.8, eave, z)
        if abs(a_[0] - b_[0]) > 1.0:
            br.append((a_, b_))
        z += 1.25
    out.append(segs(br, 0.9, seed, 0))
    out.append(H(U, C.qx(XW, Z0, Z1, eave - 0.9, eave), 0, 1.3, 0.55, wob=0.05, brk=0))
    out.append(pen([C(XW, deck, Z0), C(XW, deck, Z1)], 1.4, seed, 0.1))
    # the near gable end, in shade, with portal and oculus
    g = [C(XW, deck, Z0), C(XW, eave, Z0), C(xr, ridge, Z0), C(XW - width, eave, Z0), C(XW - width, deck, Z0)]
    out.append(F(g, PAPER))
    out.append(segs([(C(x, deck, Z0), C(x, eave + (ridge - eave) * (1 - abs(x - xr) / (width / 2)), Z0)) for x in [XW - 0.45 * i for i in range(1, int(width / 0.45))]],
                    0.5, seed, 0, op=0.6))
    out.append(H(U, g, 80, 2.2, 0.65, op=0.9) + H(U, g, 15, 3.4, 0.5, op=0.6))
    pq = C.qz(Z0, xr - 3.2, xr + 3.2, deck, 9.0)
    out.append(F(arch_q(pq, 0.36, 12), INK, 0.88))
    oc = [C(xr + 1.1 * math.cos(2 * math.pi * i / 18), 12.6 + 1.1 * math.sin(2 * math.pi * i / 18), Z0) for i in range(18)]
    out.append(F(oc, INK, 0.85) + pen(oc, 1.0, seed, 0.05, closed=True))
    tr = [C(XW + 0.3, eave + 0.25, Z0 - 0.3), C(xr, ridge + 0.4, Z0 - 0.3), C(XW - width - 0.3, eave + 0.25, Z0 - 0.3)]
    out.append(pen(tr, 2.0, seed, 0.1) + pen(g, 1.4, seed + 1, 0.1, closed=True))
    a_ = C(xr, ridge + 0.4, Z0 - 0.3)
    out.append(seg(a_[0], a_[1], a_[0], a_[1] - C.px(xr, Z0, 3.5), 1.2, seed, 0))
    return "".join(out)


@design("seattle")
def seattle(U):
    """Late afternoon on the apron of an old waterfront pier: the board-and-batten shed with its arched windows
    running away on the left, lamps and strollers along the railing, the water of Elliott Bay opening on the
    right with a big ferry crossing, a vermilion tug, a gull on a piling, and Mount Rainier rising pale and
    enormous beyond the water."""
    C = Cam2(f=290, cx=300, vpy=300, eye=4.0, yaw=11)
    art = []
    HZ = C.vpy
    rnd = random.Random(131)
    art.append(cloud(U, 470, 92, 120, 18, 5) + cloud(U, 300, 70, 70, 11, 8))
    # Mount Rainier, pale over a band of haze
    art.append(rainier(U, 418, 162, HZ - 4, 200, 8, op=0.85))
    art.append(sky_rules(U, 210, 600, HZ - 26, HZ - 2, 4, op=0.3, g0=3.4, g1=2.0))
    # West Seattle and the port on the far right: a low dark shore with cranes
    far = [(370, HZ - 3), (430, HZ - 9), (490, HZ - 12), (550, HZ - 10), (610, HZ - 7)]
    fd = smooth_open(far) + f" L 610 {HZ + 1} L 370 {HZ + 1} Z"
    art.append(F(fd, PAPER) + H(U, fd, 0, 1.3, 0.55, op=0.75, box=(370, HZ - 20, 610, HZ + 2)) + P(smooth_open(far), 1.0, INK, 0.8))
    cr_ = []
    for x in (470, 492, 514):
        y0 = HZ - 9
        cr_ += [((x, y0), (x, y0 - 16)), ((x - 3, y0), (x - 3, y0 - 16)), ((x - 11, y0 - 16), (x + 11, y0 - 18)), ((x, y0 - 16), (x + 1, y0 - 22)),
                ((x + 1, y0 - 22), (x + 11, y0 - 18)), ((x + 1, y0 - 22), (x - 11, y0 - 16))]
    art.append(segs(cr_, 0.8, 6, 0, op=0.75))
    # the bay
    water = [(0, HZ), (600, HZ), (600, 600), (0, 600)]
    art.append(ripples(U, 0, 600, HZ + 0.5, 480, 7, dens=0.95, gap=(1.3, 8.0), ln=((2, 8), (10, 32)), w=(0.6, 1.4),
                       refl=[(370, 540, 0.3)], skip=[(300, 330)], clip=poly(water)))
    # distant piers and the downtown bluff on the left, beyond our shed
    bl = []
    for i, (x0, w, h) in enumerate(((150, 18, 70), (166, 14, 48), (178, 16, 84), (192, 12, 40), (202, 16, 60), (216, 10, 30))):
        bl.append(prism(U, x0, x0 + w, 3, HZ - 6 - h, HZ, 400 + i, style="grid", dark_p=0.1, w=0.9))
    art.append(f'<g opacity="0.5">{"".join(bl)}</g>')
    art.append(gable_shed(U, C, -70, -14, 220, 250, 8.5, 13.0, 30, (0.7, -0.7)))
    # the ferry and the tug, sailboats
    art.append(wsf_ferry(U, 340, 520, 305, 70))
    art.append(tug(U, 316, 324, 22, 71))
    art.append(yacht(U, 566, 303, 14, 72, flip=True) + yacht(U, 262, 306, 9, 73) + yacht(U, 540, 318, 18, 74))
    # our pier: deck, its edge, pilings, the shed, the railing
    XW, DX, Z0, Z1 = -9.5, 2.2, 15.0, 120.0
    deck = [C(XW, 2.3, 2.6), C(XW, 2.3, Z1), C(DX, 2.3, Z1), C(DX, 2.3, 2.6)]
    art.append(F(deck, PAPER))
    planks = [(C(XW, 2.3, z), C(DX, 2.3, z)) for z in [2.6 + 0.22 * k for k in range(600) if 2.6 + 0.22 * k < Z1]]
    art.append(clipped(U("dk"), poly(deck), segs(planks, 0.55, 74, 0.05, op=0.65) + H(U, deck, 0, (4.0, 2.0), 0.5, op=0.3, box=(0, 300, 420, 600), dark=(150, 600))))
    edge = [C(DX, 2.3, 4.5), C(DX, 2.3, Z1), C(DX, 1.9, Z1), C(DX, 1.9, 4.5)]
    art.append(F(edge, PAPER) + H(U, edge, 4, 2.0, 0.7, op=0.8) + pen([edge[3], edge[2]], 1.2, 73, 0.1))
    piles = []
    for z in [17 + 2.4 * k for k in range(60) if 17 + 2.4 * k < Z1]:
        a_, b_ = C(DX - 0.2, 1.6, z), C(DX - 0.2, -0.4, z)
        hw = max(0.6, C.px(DX, z, 0.18))
        piles.append(poly([(a_[0] - hw, a_[1]), (a_[0] + hw, a_[1]), (b_[0] + hw, b_[1]), (b_[0] - hw, b_[1])]))
    art.append(f'<path d="{" ".join(piles)}" fill="{INK}" opacity="0.85"/>')
    art.append(pier_shed(U, C, XW, Z0, Z1, 33))
    # a gap in the shed wall at the near end: the open apron with a lamp and a bench
    rp = []
    for z in [2.6 + 1.5 * k for k in range(80) if 2.6 + 1.5 * k <= Z1]:
        a_, b_ = C(DX - 0.3, 2.3, z), C(DX - 0.3, 3.4, z)
        if abs(C(DX, 2.3, z + 1.5)[0] - a_[0]) > 1.2:
            rp.append((a_, b_))
    art.append(segs(rp, 1.2, 75, 0))
    for Y, w_ in ((3.4, 1.8), (2.85, 1.0)):
        art.append(pen([C(DX - 0.3, Y, 2.6), C(DX - 0.3, Y, Z1)], w_, 76, 0.15))
    for z in (9, 28, 52):
        x, y = C(DX - 0.6, 2.3, z)
        hp = C.px(DX - 0.6, z, 4.8)
        art.append(lamp(x, y, hp, 87 + z, "lantern", max(1.0, min(2.2, hp / 50))))
    x, y = C(-6.2, 2.3, 12)
    art.append(bench(x - 16, y, 30, 91))
    # crates and a coil of rope by the shed wall
    for X, Z, sz in ((-8.6, 18, 1.0), (-8.6, 19.3, 0.8), (-8.5, 18.6, 0.7)):
        x, y = C(X, 2.3 + (1.0 if sz == 0.7 else 0.0), Z)
        w_ = C.px(X, Z, sz)
        q = [(x - w_ / 2, y - w_), (x + w_ / 2, y - w_), (x + w_ / 2, y), (x - w_ / 2, y)]
        art.append(F(q, PAPER) + segs([((x - w_ / 2, y - w_ * k / 3), (x + w_ / 2, y - w_ * k / 3)) for k in (1, 2)] + [(q[0], q[2])], 0.7, 97, 0) + pen(q, 1.0, 97, 0.05, closed=True))
    for X, Z, sd, fl in ((0.9, 19, 1, False), (1.2, 20, 2, True), (-4.5, 34, 3, False), (-2.6, 9.0, 4, True), (0.6, 44, 5, True), (-5.6, 60, 6, False),
                         (-1.0, 78, 7, True), (-3.6, 25, 8, False), (-0.6, 30, 9, True)):
        art.append(ppl(C, X, Z, 80 + sd, Y=2.3, flip=fl, bag=sd == 3))
    # a dolphin of tied pilings in the water on the right, a gull on top
    for k, (X, Z) in enumerate(((7.0, 10.0), (7.7, 10.6), (8.4, 10.0))):
        a_, b_ = C(X, 3.4 - k * 0.3, Z), C(X, -0.3, Z)
        hw = C.px(X, Z, 0.2)
        pq = [(a_[0] - hw, a_[1]), (a_[0] + hw, a_[1]), (b_[0] + hw, b_[1]), (b_[0] - hw, b_[1])]
        art.append(F(pq, PAPER) + H(U, pq, 90, 1.2, 0.7, span=(0.4, 1), dark=(a_[0] + hw, a_[1])) + pen(pq, 1.4, 92 + k, 0.1, closed=True))
        art.append(f'<ellipse cx="{f1(a_[0])}" cy="{f1(a_[1])}" rx="{f1(hw)}" ry="{f1(hw * 0.35)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    wa, wb = C(6.8, 1.6, 10), C(8.6, 1.6, 10)
    art.append(segs([((wa[0], wa[1] + d_), (wb[0], wb[1] + d_)) for d_ in (0, 3, 6)], 1.4, 95, 0.4))
    gx, gy = C(7.7, 3.1, 10.6)
    gull = [(gx - 12, gy - 6), (gx - 4, gy - 12), (gx + 8, gy - 12), (gx + 14, gy - 16), (gx + 18, gy - 15), (gx + 14, gy - 10), (gx + 8, gy - 4), (gx - 4, gy - 3)]
    art.append(F(smooth_closed(gull), PAPER) + P(smooth_closed(gull), 1.2) + F([(gx - 12, gy - 6), (gx + 2, gy - 9), (gx - 2, gy - 4)], INK, 0.85)
               + F([(gx + 18, gy - 15), (gx + 23, gy - 13), (gx + 18, gy - 13)], INK) + segs([((gx, gy - 3), (gx - 1, gy)), ((gx + 4, gy - 3), (gx + 5, gy))], 1.0, 96, 0))
    # gulls aloft
    art.append(bird(296, 150, 9, 91) + bird(318, 136, 6, 92) + bird(520, 226, 5, 94) + bird(250, 186, 6, 93))
    return plate(U, "seattle", art, 131)


# ================================================================ EDINBURGH
def stone_block(U, x0, x1, top, base, seed, sw=0.0, sdy=0.3, cols=0, rows=0, t_front=0.2, t_side=0.72, roof=None, rh=0.0,
                crenel=False, chim=(), win=(0.32, 0.58), win_top=0.18, win_bot=0.86, courses=True, lw=1.4):
    """A castle building seen from below in oblique projection, light from the left: lit front face with ashlar
    courses and small dark windows, the right-hand return in shade, a slate roof (or battlements) on top."""
    rnd = random.Random(seed)
    out = []
    front = [(x0, top), (x1, top), (x1, base), (x0, base)]
    side = [(x1, top), (x1 + sw, top - sw * sdy), (x1 + sw, base - sw * sdy), (x1, base)] if sw else None
    # roof first (it sits behind the parapet line)
    if roof == "pitch" and rh:
        rf = [(x0 - 1, top), (x1 + 1, top), (x1 + sw * 0.5 + 1, top - rh), (x0 + sw * 0.5 - 1, top - rh)]
        out.append(F(rf, PAPER) + H(U, rf, 0, 1.5, 0.7, wob=0.1, brk=0.05) + H(U, rf, 100, 3.4, 0.5, op=0.6, wob=0.1, brk=0.1))
        out.append(sketch(rf, 1.2, seed, 0.4))
        if side:
            g = [(x1, top), (x1 + sw * 0.5 + 1, top - rh), (x1 + sw, top - sw * sdy)]
            out.append(F(g, PAPER) + H(U, g, 90, 1.6, 0.7) + pen(g, 1.1, seed, 0.1))
        for cxp in chim:
            cx_ = x0 + (x1 - x0) * cxp
            ch = [(cx_ - 3, top - rh * 0.6), (cx_ + 3, top - rh * 0.6), (cx_ + 3, top - rh - 9), (cx_ - 3, top - rh - 9)]
            out.append(F(ch, PAPER) + H(U, [(cx_, ch[2][1]), ch[2], ch[1], (cx_, ch[1][1])], 90, 1.2, 0.6) + sketch(ch, 1.0, seed, 0.2))
            out.append(segs([((cx_ - 2, top - rh - 9), (cx_ - 2, top - rh - 12)), ((cx_ + 1.5, top - rh - 9), (cx_ + 1.5, top - rh - 12))], 1.3, seed, 0))
    out.append(F(front, PAPER))
    if courses:
        out.append(segs([((x0, y), (x1, y)) for y in [top + 2.6 * k for k in range(1, int((base - top) / 2.6))]], 0.45, seed, 0.1, op=0.3))
    if t_front >= 0.3:
        out.append(H(U, front, 90, lerp(4.4, 2.0, t_front), 0.5, op=0.6, wob=0.1, brk=0.06))
    if cols and rows:
        wins = []
        for i in range(cols):
            for j in range(rows):
                u = (i + 0.5) / cols
                v = win_top + (win_bot - win_top) * (j + 0.5) / rows
                ww = (x1 - x0) / cols * win[0]
                hh = (base - top) * (win_bot - win_top) / rows * win[1]
                xc, yc = x0 + (x1 - x0) * u, top + (base - top) * v
                wins.append([(xc - ww / 2, yc - hh / 2), (xc + ww / 2, yc - hh / 2), (xc + ww / 2, yc + hh / 2), (xc - ww / 2, yc + hh / 2)])
        out.append(f'<path d="{" ".join(poly(w) for w in wins)}" fill="{INK}" opacity="0.85"/>')
        out.append(segs([((w[3][0] - 0.8, w[3][1] + 0.9), (w[2][0] + 0.8, w[2][1] + 0.9)) for w in wins], 0.8, seed, 0))
    if side:
        out.append(F(side, PAPER))
        out.append(H(U, side, 90, lerp(3.0, 1.4, t_side), 0.7, wob=0.1, brk=0.03))
        if t_side > 0.55:
            out.append(H(U, side, 20, 2.6, 0.55, op=0.8, wob=0.1, brk=0.05))
        if rows and sw > 8:
            m = homog(side)
            k = max(1, int(sw / 7))
            ws = []
            for i in range(k):
                for j in range(rows):
                    v = win_top + (win_bot - win_top) * (j + 0.5) / rows
                    dv = (win_bot - win_top) / rows * win[1] / 2
                    ws.append([m((i + 0.3) / k, v - dv), m((i + 0.7) / k, v - dv), m((i + 0.7) / k, v + dv), m((i + 0.3) / k, v + dv)])
            out.append(f'<path d="{" ".join(poly(w) for w in ws)}" fill="{INK}" opacity="0.9"/>')
        out.append(sketch(side, lw * 0.85, seed + 1, 0.5))
    if crenel:
        out.append(battlements(U, x0, x1 + sw, top, seed, slope=-sdy if sw else 0, x_side=x1))
    out.append(sketch(front, lw, seed + 2, 0.7))
    return "".join(out)


def battlements(U, x0, x1, y, seed, m=4.2, h=3.6, slope=0.0, x_side=None):
    """Crenellations along a wall top from x0 to x1 (merlons as small blocks with a shaded right edge)."""
    rnd = random.Random(seed)
    out = []
    x = x0
    blocks = []
    while x < x1 - 1:
        w = min(m, x1 - x)
        yy = y + (slope * (x - x_side) if (x_side is not None and x > x_side) else 0)
        blocks.append([(x, yy - h), (x + w, yy - h), (x + w, yy), (x, yy)])
        x += m * 2
    out.append(f'<path d="{" ".join(poly(b) for b in blocks)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.0"/>')
    out.append(f'<path d="{" ".join(poly([(b[1][0] - 1.4, b[1][1]), b[1], b[2], (b[2][0] - 1.4, b[2][1])]) for b in blocks)}" fill="{INK}" opacity="0.7"/>')
    return "".join(out)


def turret(U, cx, top, base, r, seed, cone=1.6):
    """A round bartizan / turret with a conical slate cap and a finial."""
    body = [(cx - r, top), (cx + r, top), (cx + r, base), (cx - r * 0.6, base + r * 0.8), (cx - r, base)]
    out = [F(body, PAPER), H(U, body, 90, (3.0, 1.2), (0.5, 0.8), box=(cx - r, top, cx + r, base + r), dark=(cx + r, top), wob=0.05, brk=0)]
    out.append(F([(cx - r * 0.25, top + (base - top) * 0.35), (cx + r * 0.05, top + (base - top) * 0.35), (cx + r * 0.05, top + (base - top) * 0.6),
                  (cx - r * 0.25, top + (base - top) * 0.6)], INK, 0.9))
    out.append(pen(body, 1.2, seed, 0.1, closed=True))
    cap = [(cx - r - 1.2, top), (cx, top - r * cone * 2), (cx + r + 1.2, top)]
    out.append(F(cap, PAPER) + H(U, [(cx, cap[1][1]), cap[2], (cx, top)], 90, 1.2, 0.6) + H(U, cap, 0, 1.8, 0.5, op=0.6) + pen(cap, 1.2, seed, 0.1, closed=True))
    out.append(seg(cx, top - r * cone * 2, cx, top - r * cone * 2 - 5, 1.1, seed, 0))
    return "".join(out)


def crow_gable(U, x0, x1, base, h, seed, steps=4, shade=0.0):
    """A crow-stepped gable end facing us."""
    pts = [(x0, base)]
    cx = (x0 + x1) / 2
    for k in range(steps):
        xa = lerp(x0, cx - 2.5, k / steps)
        ya = base - h * k / steps
        pts += [(xa, ya - h / steps), (lerp(x0, cx - 2.5, (k + 1) / steps), ya - h / steps)]
    pts.append((cx - 2.5, base - h - 3))
    pts.append((cx + 2.5, base - h - 3))
    for k in range(steps - 1, -1, -1):
        xa = lerp(x1, cx + 2.5, (k + 1) / steps)
        ya = base - h * (k + 1) / steps
        pts += [(xa, ya), (lerp(x1, cx + 2.5, k / steps), ya)]
    pts.append((x1, base))
    out = [F(pts, PAPER), segs([((x0, y), (x1, y)) for y in [base - 2.6 * k for k in range(1, int(h / 2.6))]], 0.45, seed, 0.1, op=0.5)]
    if shade:
        out.append(H(U, pts, 90, lerp(3.0, 1.4, shade), 0.7))
    out.append(F([(cx - 2, base - h * 0.55), (cx + 2, base - h * 0.55), (cx + 2, base - h * 0.3), (cx - 2, base - h * 0.3)], INK, 0.85))
    out.append(pen(pts, 1.2, seed, 0.1))
    return out and "".join(out)


def castle_rock(U, top_pts, base, seed):
    """The volcanic crag: basalt in columnar buttresses and clefts. Each column is broken into stacked
    blocks with their own tone (lit buttress faces left almost bare, shadowed clefts cross-hatched), joints and
    fissures in nib strokes, ledges with scrub, the foot lost in trees."""
    rnd = random.Random(seed)
    jag = [top_pts[0]]
    for (ax, ay), (bx, by) in zip(top_pts, top_pts[1:]):
        n = max(1, int(abs(bx - ax) / 7))
        for i in range(1, n + 1):
            t = i / n
            jag.append((lerp(ax, bx, t) + rnd.uniform(-1.5, 1.5), lerp(ay, by, t) + (rnd.uniform(-1.2, 2.6) if i < n else 0)))
    top_pts = jag
    d = poly(top_pts + [(top_pts[-1][0] + 20, base + 10), (top_pts[0][0] - 20, base + 10)])
    xs = [p[0] for p in top_pts]
    x0, x1 = min(xs) - 20, max(xs) + 20
    ys = [p[1] for p in top_pts]

    def ytop(x):
        for (ax, ay), (bx, by) in zip(top_pts, top_pts[1:]):
            if ax <= x <= bx:
                return lerp(ay, by, (x - ax) / max(1e-6, bx - ax))
        return ys[0] if x < xs[0] else ys[-1]
    inner = [F(d, INK, 0.08)]
    x = x0
    k = 0
    joints = []
    while x < x1:
        w = rnd.uniform(8, 22)
        xa, xb = x, x + w
        base_t = 0.5 + 0.3 * rnd.random() + 0.2 * (xa - 300) / 300
        lit = (k % 4 == 1) or rnd.random() < 0.18
        y = min(ytop(xa), ytop(xb)) - 6
        lean = rnd.uniform(-0.12, 0.12)
        while y < base + 10:
            hgt = rnd.uniform(18, 46)
            y2 = min(base + 12, y + hgt)
            o1, o2 = (y - 200) * lean, (y2 - 200) * lean
            blk = [(xa + o1 + rnd.uniform(-1.5, 1.5), y), (xb + o1 + rnd.uniform(-1.5, 1.5), y + rnd.uniform(-3, 3)),
                   (xb + o2 + rnd.uniform(-1.5, 1.5), y2), (xa + o2 + rnd.uniform(-1.5, 1.5), y2)]
            t = base_t + rnd.uniform(-0.15, 0.15) + 0.15 * (y - 220) / 120
            if lit:
                t = rnd.uniform(0.08, 0.3)
            t = max(0.05, min(0.98, t))
            gap = lerp(5.0, 1.35, t)
            b = bbox(blk)
            inner.append(F(blk, PAPER))
            inner.append(H(U, blk, rnd.uniform(82, 98), (gap * 1.25, gap * 0.85), (0.5, 0.85), box=b, dark=(xb, y2), wob=0.3, brk=0.2))
            if t > 0.5:
                inner.append(H(U, blk, rnd.uniform(15, 35), lerp(3.8, 1.7, t), 0.6, box=b, span=(0.1, 1), dark=(xb, y2), wob=0.3, brk=0.3, op=0.85))
            if t > 0.78:
                inner.append(H(U, blk, -35, 2.2, 0.55, box=b, span=(0.35, 1), dark=(xb, y2), wob=0.3, brk=0.3, op=0.8))
            if lit:
                inner.append(nib([blk[1], pt(blk[1], blk[2], 0.5), blk[2]], 2.2, taper=(0.4, 0.6), seed=seed + k * 7 + int(y), color=INK))
            joints.append((blk[3], blk[2]))
            y = y2
        jp = [(xb + rnd.uniform(-1, 1), ytop(xb) + rnd.uniform(0, 6))]
        yy = jp[0][1]
        while yy < base:
            yy += rnd.uniform(10, 22)
            jp.append((xb + (yy - 200) * lean + rnd.uniform(-2, 2), yy))
        inner.append(nib(jp, rnd.uniform(1.2, 2.4), taper=(0.2, 0.6), ramp=0.3, seed=seed + k, color=INK, op=0.95))
        x = xb
        k += 1
    inner.append(segs(joints, 1.0, seed + 3, 0.6, op=0.8))
    # ledges with scrub
    for i in range(18):
        lx = rnd.uniform(x0 + 20, x1 - 30)
        ly = rnd.uniform(ytop(lx) + 16, base - 8)
        L = rnd.uniform(12, 30)
        inner.append(nib([(lx, ly), (lx + L * 0.5, ly + rnd.uniform(-1, 2)), (lx + L, ly + rnd.uniform(0, 3))], 1.8, taper=(0.3, 0.3), seed=seed + 50 + i, color=INK))
        for j in range(rnd.randint(1, 3)):
            r = rnd.uniform(3.5, 6.5)
            inner.append(lobe(U, lx + rnd.uniform(0, L), ly - r * 0.4, r, r * 0.7, seed * 7 + i * 5 + j, light=(-1, -1), w=0.8, dense=1.3))
    out = [F(d, PAPER), clipped(U("ck"), d, "".join(inner)), pen(top_pts, 2.0, seed, 0.4)]
    return "".join(out)


def fountain(U, cx, base, h, seed):
    """A Victorian cast-iron fountain (after the one in West Princes Street Gardens): a wide basin, a pedestal
    ringed with seated figures, two tiers of bowls shedding water, a crowning figure."""
    s = h / 125.0
    out = []

    def ell(y, rx, ry, a0=0, a1=360, n=36):
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    def solid(pts, dark=0.6):
        b = bbox(pts, 0)
        return (F(pts, PAPER) + H(U, pts, 90, (3.2, 1.2), (0.5, 0.85), box=b, dark=(b[2], b[1]), span=(0.25, 1), wob=0.05, brk=0)
                + (H(U, pts, 20, 2.2, 0.55, box=b, dark=(b[2], b[3]), span=(0.55, 1), wob=0.1, brk=0.05) if dark > 0.5 else "")
                + pen(pts, max(1.0, 1.3 * s), seed, 0.05, closed=True))
    # basin: rim ellipse + front wall
    rx, ry = 64 * s, 11 * s
    yr = base - 12 * s
    wall = ell(yr, rx, ry, 0, 180) + ell(base, rx, ry, 180, 0)
    out.append(F(ell(yr, rx, ry), PAPER))
    # water in the basin
    wl = []
    rnd = random.Random(seed)
    for i in range(14):
        yy = yr - ry * 0.6 + i * ry * 0.09
        xa = cx + rnd.uniform(-rx * 0.85, rx * 0.5)
        wl.append(((xa, yy), (xa + rnd.uniform(6, 16) * s, yy)))
    out.append(clipped(U("fb"), poly(ell(yr, rx * 0.95, ry * 0.85)), segs(wl, 0.7, seed, 0.3, op=0.8)))
    out.append(solid(wall, 0.4))
    out.append(segs([(p, (p[0], p[1] + 10 * s)) for p in ell(yr, rx, ry, 10, 170, 12)[1:-1]], 0.7, seed, 0, op=0.7))
    out.append(pen(ell(yr, rx, ry), 1.3, seed, 0.05))
    # pedestal with seated figures
    ped = [(cx - 15 * s, yr - 2 * s), (cx - 11 * s, yr - 36 * s), (cx + 11 * s, yr - 36 * s), (cx + 15 * s, yr - 2 * s)]
    out.append(solid(ped))
    for sx_ in (-1, 1):
        fx = cx + sx_ * 19 * s
        fig = smooth_closed([(fx - 7 * s, yr - 4 * s), (fx + 7 * s, yr - 4 * s), (fx + 6 * s * sx_ * 0.6, yr - 16 * s), (fx + 2 * s * sx_, yr - 26 * s),
                             (fx - 2 * s * sx_, yr - 27 * s), (fx - 5 * s * sx_, yr - 16 * s)])
        out.append(solid([(fx - 7 * s, yr - 4 * s), (fx + 7 * s, yr - 4 * s), (fx + 5 * s, yr - 18 * s), (fx + 1 * s, yr - 26 * s), (fx - 3 * s, yr - 25 * s), (fx - 6 * s, yr - 16 * s)], 0.8))
        out.append(f'<circle cx="{f1(fx)}" cy="{f1(yr - 29 * s)}" r="{f1(3.4 * s)}" fill="{INK}" opacity="0.9"/>')
    # lower bowl
    yb = yr - 46 * s
    bowl = ell(yb, 36 * s, 6 * s, 0, 180) + [(cx + 6 * s, yb + 12 * s), (cx - 6 * s, yb + 12 * s)]
    out.append(solid(bowl))
    out.append(F(ell(yb, 36 * s, 6 * s), PAPER) + pen(ell(yb, 36 * s, 6 * s), 1.2, seed, 0.05))
    stem = [(cx - 5 * s, yb + 12 * s), (cx + 5 * s, yb + 12 * s), (cx + 7 * s, yr - 36 * s), (cx - 7 * s, yr - 36 * s)]
    out.append(solid(stem))
    # water veils falling from the bowl into the basin
    fall = []
    for k in range(9):
        a = math.radians(10 + 160 * k / 8)
        px_, py_ = cx + 36 * s * math.cos(a), yb + 6 * s * math.sin(a)
        ex = cx + (36 * s + 14 * s) * math.cos(a)
        fall.append(f"M {f1(px_)} {f1(py_)} Q {f1(px_ + (ex - px_) * 0.9)} {f1(py_ + 4 * s)} {f1(ex)} {f1(yr - 2 * s + 6 * s * math.sin(a))}")
    out.append(P(" ".join(fall), 0.7, INK, 0.6))
    # column with standing figures, upper bowl, crowning figure
    col = [(cx - 4 * s, yb - 1 * s), (cx + 4 * s, yb - 1 * s), (cx + 3 * s, yb - 32 * s), (cx - 3 * s, yb - 32 * s)]
    out.append(solid(col))
    for sx_ in (-1, 1):
        fx = cx + sx_ * 8 * s
        out.append(solid([(fx - 2.6 * s, yb - 1 * s), (fx + 2.6 * s, yb - 1 * s), (fx + 2 * s, yb - 18 * s), (fx - 2 * s, yb - 18 * s)], 0.8))
        out.append(f'<circle cx="{f1(fx)}" cy="{f1(yb - 21 * s)}" r="{f1(2.4 * s)}" fill="{INK}" opacity="0.9"/>')
    yu = yb - 34 * s
    ub = ell(yu, 18 * s, 3.4 * s, 0, 180) + [(cx + 3 * s, yu + 7 * s), (cx - 3 * s, yu + 7 * s)]
    out.append(solid(ub) + F(ell(yu, 18 * s, 3.4 * s), PAPER) + pen(ell(yu, 18 * s, 3.4 * s), 1.0, seed, 0.05))
    out.append(P(" ".join(f"M {f1(cx + sg * 18 * s)} {f1(yu)} Q {f1(cx + sg * 24 * s)} {f1(yu + 2 * s)} {f1(cx + sg * 27 * s)} {f1(yb - 2 * s)}" for sg in (-1, 1)), 0.7, INK, 0.6))
    fig = [(cx - 3.4 * s, yu - 1 * s), (cx + 3.4 * s, yu - 1 * s), (cx + 2.6 * s, yu - 16 * s), (cx + 1.6 * s, yu - 22 * s), (cx - 1.8 * s, yu - 22 * s), (cx - 2.8 * s, yu - 16 * s)]
    out.append(solid(fig, 0.8))
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(yu - 25 * s)}" r="{f1(2.6 * s)}" fill="{INK}"/>')
    out.append(nib([(cx + 1.5 * s, yu - 20 * s), (cx + 5 * s, yu - 26 * s), (cx + 6 * s, yu - 31 * s)], max(1.2, 1.8 * s), taper=(1, 0.5), seed=seed, color=INK))
    return "".join(out)


@design("edinburgh")
def edinburgh(U):
    """The Castle from West Princes Street Gardens on a bright morning: the crag of basalt with the Half Moon
    Battery, the Palace and its flag, the Great Hall, the Governor's House and the long Barracks along the
    summit; the wooded bank below; the gardens' lawn, a cast-iron fountain, a flower bed, lanterns and
    strollers on the curving path."""
    art = []
    art.append(cloud(U, 470, 92, 130, 20, 5) + cloud(U, 128, 120, 92, 14, 6) + cloud(U, 330, 62, 64, 10, 9))
    # ---- the rock (drawn first; buildings stand on it)
    KS, CY = 0.8, 196.0

    def K(x, y):
        return (300 + (x - 300) * KS, CY + (y - 225) * KS)
    top_pts = ([(44, 304), (58, 296), (66, 282), (80, 276), (88, 258), (100, 252), (108, 240), (122, 236), (136, 234)]
               + [K(x, y) for x, y in ((112, 228), (150, 226), (205, 223), (232, 216), (300, 212), (334, 216), (372, 222), (420, 232), (476, 236), (506, 244))]
               + [(470, 214), (482, 222), (496, 226), (508, 240), (522, 246), (536, 262), (552, 270), (566, 286), (588, 296)])
    # ---- castle, back to front (drawn at 1/0.8 and scaled into place over the crag)
    castle = []
    # Scottish National War Memorial (behind), with its gothic gable and fleche
    castle.append(stone_block(U, 222, 296, 140, 214, 31, sw=8, cols=5, rows=1, roof="pitch", rh=10, win=(0.34, 0.8), win_top=0.12, win_bot=0.5))
    fl = [(254, 130), (262, 130), (262, 112), (254, 112)]
    castle.append(F(fl, PAPER) + H(U, [(258, 112), (262, 112), (262, 130), (258, 130)], 90, 1.2, 0.6) + sketch(fl, 1.1, 32, 0.2))
    castle.append(F([(252, 112), (258, 92), (264, 112)], PAPER) + H(U, [(258, 92), (264, 112), (258, 112)], 90, 1.1, 0.6) + pen([(252, 112), (258, 92), (264, 112)], 1.2, 33, 0.1))
    castle.append(seg(258, 92, 258, 84, 1.1, 34, 0))
    # the Palace, its tower and flag
    castle.append(stone_block(U, 128, 206, 132, 200, 35, sw=10, cols=6, rows=3, roof="pitch", rh=9, chim=(0.18, 0.82), t_front=0.25))
    tw = (148, 170)
    castle.append(stone_block(U, tw[0], tw[1], 106, 134, 36, sw=6, cols=2, rows=2, win_top=0.2, win_bot=0.85, crenel=True))
    cup = smooth_closed([(tw[0] + 3, 102), (tw[1] - 3 + 3, 102), (tw[1] - 6 + 3, 92), (159 + 3, 86), (tw[0] + 6, 92)])
    castle.append(F(cup, PAPER) + H(U, cup, 90, 1.3, 0.6, span=(0.5, 1), dark=(tw[1] + 4, 90)) + P(cup, 1.2))
    castle.append(seg(162, 86, 162, 64, 1.4, 37, 0))
    castle.append(flag(U, 162, 66, 30, 15, 38, wave=0.2))
    # Great Hall with its tall roof
    castle.append(stone_block(U, 206, 262, 150, 214, 39, sw=6, cols=4, rows=1, roof="pitch", rh=12, win=(0.38, 0.75), win_top=0.18, win_bot=0.55, chim=(0.5,)))
    # Governor's House with crow-stepped gables and corner turrets
    castle.append(stone_block(U, 330, 372, 172, 222, 40, sw=7, cols=4, rows=2, roof="pitch", rh=9, win_top=0.2, win_bot=0.8))
    castle.append(crow_gable(U, 330, 346, 172, 18, 41, steps=4))
    castle.append(crow_gable(U, 356, 372, 172, 18, 42, steps=4, shade=0.2))
    castle.append(turret(U, 328, 178, 194, 4, 43) + turret(U, 374, 178, 194, 4, 44))
    # the New Barracks: long, tall and plain, stepping down the west slope
    castle.append(stone_block(U, 380, 478, 172, 232, 45, sw=12, cols=11, rows=4, win=(0.38, 0.55), crenel=False, t_front=0.3))
    castle.append(battlements(U, 380, 490, 172, 46, slope=-0.3, x_side=478))
    # curtain walls along the crag, battlements, a bartizan
    castle.append(stone_block(U, 196, 330, 196, 224, 47, cols=0, rows=0, crenel=True, t_front=0.35))
    for x_, y_ in ((214, 208), (240, 210), (274, 207), (302, 206)):
        castle.append(F([(x_ - 1.6, y_ - 1.2), (x_ + 1.6, y_ - 1.2), (x_ + 1.6, y_ + 1.6), (x_ - 1.6, y_ + 1.6)], INK, 0.85))
    castle.append(turret(U, 292, 188, 206, 5, 48))
    castle.append(stone_block(U, 478, 512, 216, 244, 49, crenel=True, t_front=0.35))
    # Half Moon Battery: the great drum, near side bulging toward us
    hm = [(112, 182)] + [(112 + 96 * i / 16, 182 - 7 * math.sin(math.pi * i / 16)) for i in range(1, 16)] + [(208, 182), (208, 228), (112, 230)]
    castle.append(F(hm, PAPER))
    castle.append(clipped(U("hm"), poly(hm), "".join(
        P(" ".join(f"M 110 {f1(y)} Q 160 {f1(y - 7)} 210 {f1(y)}" for y in [184 + 2.8 * k for k in range(17)]), 0.5, INK, 0.5)
        for _ in range(1)) + H(U, hm, 90, (4.6, 1.2), (0.45, 0.9), box=(112, 170, 208, 230), dark=(208, 200), wob=0.05, brk=0.02)
        + H(U, hm, 15, 2.6, 0.55, box=(112, 170, 208, 230), dark=(208, 230), span=(0.6, 1), op=0.8)))
    ports = []
    for i in range(6):
        u = (i + 0.5) / 6
        x_ = 112 + 96 * u
        y_ = 190 - 7 * math.sin(math.pi * u)
        ports.append([(x_ - 2.2, y_), (x_ + 2.2, y_), (x_ + 2.2, y_ + 4), (x_ - 2.2, y_ + 4)])
    castle.append(f'<path d="{" ".join(poly(p) for p in ports)}" fill="{INK}" opacity="0.9"/>')
    castle.append(P(smooth_open(hm[:17]), 2.0) + P(smooth_open([(p[0], p[1] + 3) for p in hm[:17]]), 0.9))
    castle.append(battlements(U, 113, 207, 181, 50, m=3.6, h=3.0))
    castle.append(pen([(112, 182), (112, 230)], 1.8, 51, 0.1) + pen([(208, 182), (208, 228)], 1.4, 52, 0.1))
    art.append(f'<g transform="translate({300 - 300 * KS:.1f} {CY - 225 * KS:.1f}) scale({KS})">' + "".join(castle) + "</g>")
    # the crag itself, in front of the building feet
    art.append(castle_rock(U, top_pts, 312, 53))
    # ---- wooded bank at the foot of the rock
    rnd = random.Random(60)
    bank = [F("M 20 292 L 590 292 L 590 330 L 20 330 Z", INK, 0.6)]
    for row, (y0, r0) in enumerate(((286, 8), (300, 10), (316, 12))):
        x = 30 + rnd.uniform(0, 10)
        while x < 580:
            r = r0 * rnd.uniform(0.8, 1.25)
            bank.append(lobe(U, x, y0 + rnd.uniform(-4, 4) - 5 * math.sin(x / 70), r, r * 0.78, 600 + row * 100 + int(x), light=(-1, -1), w=1.0, dense=1.2))
            x += r * rnd.uniform(1.3, 1.7)
    art.append("".join(bank))
    for x_, h_ in ((104, 64), (236, 50), (524, 60), (556, 44)):
        art.append(cone_tree(U, x_, 322, h_, h_ * 0.34, 70 + x_, lw=1.2))
    for x_, h_, w_ in ((172, 70, 54), (318, 62, 48), (420, 76, 58)):
        art.append(tree(U, x_, 326, h_, w_, 80 + x_, light=(-1, -1), trunk_h=0.3, lobes=5, lw=1.2, dense=1.1))
    # ---- the gardens: lawn rising to the bank, a curving path
    lawn = [(-10, 324), (610, 324), (610, 620), (-10, 620)]
    art.append(F(lawn, PAPER))
    gl = []
    for i in range(1000):
        x = rnd.uniform(-10, 610)
        y = rnd.uniform(326, 460)
        L = lerp(2, 7, (y - 326) / 134)
        gl.append(((x, y), (x + rnd.uniform(-1.2, 1.2), y - L)))
    art.append(clipped(U("ln"), poly(lawn), segs(gl, 0.65, 61, 0.2, op=0.75) + H(U, lawn, 2, (7.0, 3.4), 0.45, op=0.22, box=(-10, 324, 610, 470), dark=(300, 470), brk=0.5)))
    art.append(pen([(-10, 325), (610, 325)], 1.2, 62, 0.4, op=0.8))
    # path: from the bottom centre sweeping up and away to the right
    pl = [(186, 470), (226, 420), (290, 380), (362, 354), (430, 339), (510, 330), (600, 327)]
    pr = [(352, 470), (348, 426), (380, 390), (426, 366), (476, 349), (536, 336), (600, 332)]
    pd = smooth_open(pl) + " L " + smooth_open(pr[::-1])[2:] + " Z"
    art.append(F(pd, PAPER) + ST(U, pd, 1100, light=(560, 330), r=(0.4, 0.9), op=0.6, box=(180, 320, 610, 470), power=0.9))
    art.append(P(smooth_open(pl), 1.5) + P(smooth_open(pr), 1.5))
    art.append(P(smooth_open([(x - 3, y + 2) for x, y in pl]), 0.7, INK, 0.7) + P(smooth_open([(x + 3, y + 2) for x, y in pr]), 0.7, INK, 0.7))
    # flower bed on the left lawn
    bx, by = 150, 374
    bed = [(bx + 56 * math.cos(2 * math.pi * k / 32), by + 12 * math.sin(2 * math.pi * k / 32)) for k in range(32)]
    art.append(F(bed, PAPER) + pen(bed, 1.4, 63, 0.1, closed=True) + pen([(p[0] * 0.92 + bx * 0.08, p[1] * 0.85 + by * 0.15) for p in bed], 0.7, 64, 0.1, closed=True, op=0.7))
    art.append(F([(p[0], p[1] + 2) for p in bed[2:15]] + [(bx - 56, by + 2)], INK, 0.0))
    art.append("".join(lobe(U, bx + dx_, by - 3 + dy_, 9, 6, 650 + i, light=(-1, -1), w=0.8, dense=1.1) for i, (dx_, dy_) in enumerate(((-34, 2), (-14, -3), (8, -2), (30, 3), (0, 5)))))
    blooms = []
    for i in range(60):
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(rnd.random()) * 0.8
        x, y = bx + 56 * rr * math.cos(a), by + 12 * rr * math.sin(a)
        blooms.append(f'<circle cx="{f1(x)}" cy="{f1(y - 3)}" r="{rnd.uniform(1.0, 1.9):.2f}" fill="{PAPER}" stroke="{INK}" stroke-width="0.7"/>')
    art.append("".join(blooms))
    # the fountain
    art.append(F(smooth_closed([(372, 418), (512, 414), (524, 426), (362, 428)]), INK, 0.22))
    art.append(fountain(U, 446, 420, 142, 65))
    # lanterns and benches beside the path
    for x_, y_, h_ in ((232, 414, 76), (370, 352, 38), (470, 340, 26)):
        art.append(lamp(x_, y_, h_, 66 + x_, "lantern", max(1.1, h_ / 40)))
    art.append(bench(262, 386, 24, 67) + bench(508, 334, 13, 68))
    # strollers
    for x_, y_, h_, sd, fl in ((292, 430, 30, 1, False), (310, 426, 28, 2, True), (384, 380, 18, 3, False), (450, 350, 12, 4, True), (522, 334, 9, 5, False),
                               (566, 331, 8, 6, True), (96, 410, 22, 7, True)):
        art.append(person(x_, y_, h_, 80 + sd, flip=fl, bag=sd in (2, 6)))
    art.append(bird(388, 128, 7, 90) + bird(410, 112, 5, 91) + bird(110, 172, 6, 92))
    # a tree framing the left of the lawn
    art.append(canopy(U, 62, 436, 190, 132, 95, light=(1, -1), lobe_r=14, shape=0.62, lw=1.3))
    # a tree framing the left edge
    return plate(U, "edinburgh", art, 141)


# ================================================================ LOS ANGELES
def fan_palm(U, x, base, h, seed, lean=0.0, light=1):
    """A Mexican fan palm (Washingtonia robusta): very tall, slender, slightly curved trunk with ring scars, a
    small round head of fan leaves on long stalks, the lower ones drooping, over a dark skirt of dead fronds."""
    rnd = random.Random(seed)
    out = []
    tx, ty = x + lean * h, base - h
    ctrl = [(x, base), (x + lean * h * 0.2, base - h * 0.5), (tx, ty)]
    C_ = cr(ctrl, False, 3.0)
    n = len(C_)
    left, right = [], []
    for i, (px, py) in enumerate(C_):
        t = i / (n - 1)
        hw = lerp(h * 0.0085, h * 0.0055, t) + 0.6 + (h * 0.005 * (1 - t / 0.05) if t < 0.05 else 0)
        left.append((px - hw, py))
        right.append((px + hw, py))
    trunk = left + right[::-1]
    out.append(F(trunk, PAPER))
    shade_side = left if light > 0 else right
    inner = H(U, C_ + shade_side[::-1], 90, max(1.0, h * 0.004), 0.6, wob=0.05, brk=0)
    rings = []
    i = 2
    while i < n - 1:
        (lx, ly), (rx, ry) = left[i], right[i]
        rings.append(((lx, ly), (rx, ry + 0.6)))
        i += rnd.randint(2, 4)
    inner += segs(rings, max(0.5, min(0.8, h / 400)), seed, 0.2, op=0.6)
    out.append(clipped(U("fp"), poly(trunk), inner))
    out.append(pen(left, max(0.8, min(1.6, h / 260)), seed, 0.1, smooth=True) + pen(right, max(0.8, min(1.6, h / 260)), seed + 1, 0.1, smooth=True))
    r = h * 0.085
    # the skirt of dead fronds
    sk = [(tx - r * 0.34, ty + r * 0.1), (tx + r * 0.34, ty + r * 0.1), (tx + r * 0.22, ty + r * 0.9), (tx + r * 0.04, ty + r * 1.05), (tx - r * 0.2, ty + r * 0.92)]
    out.append(F(smooth_closed(sk), INK, 0.88))
    out.append(segs([((tx + rnd.uniform(-0.35, 0.35) * r, ty + r * 0.2), (tx + rnd.uniform(-0.3, 0.3) * r, ty + r * rnd.uniform(0.9, 1.25))) for _ in range(7)],
                    max(0.5, r * 0.04), seed, 0.3, color=PAPER, op=0.45))
    # fan leaves: a stalk out to a pleated fan, the lower ones drooping, the back ones darker
    leaves = []
    for k in range(15):
        a = math.radians(-200 + 220 * (k + rnd.uniform(0.2, 0.8)) / 15)
        back = rnd.random() < 0.3
        L = r * rnd.uniform(0.75, 1.05)
        droop = max(0.0, math.sin(a)) * 0.6 + 0.15
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.8 + L * droop * 0.5
        leaves.append((back, a, ex, ey, L))
    leaves.sort(key=lambda q: not q[0])
    for back, a, ex, ey, L in leaves:
        out.append(seg(tx, ty, ex, ey, max(0.6, r * 0.05), seed, 0.3))
        fw = L * 0.55
        ang = math.atan2(ey - ty, ex - tx)
        rays = []
        for j in range(9):
            b = ang + math.radians(-55 + 110 * j / 8)
            ll = fw * (0.75 + 0.25 * math.sin(math.pi * j / 8))
            fx_, fy_ = ex + math.cos(b) * ll, ey + math.sin(b) * ll + ll * 0.35
            rays.append(f"M {f1(ex)} {f1(ey)} Q {f1(ex + math.cos(b) * ll * 0.6)} {f1(ey + math.sin(b) * ll * 0.6)} {f1(fx_)} {f1(fy_)}")
        fan = [(ex, ey)] + [(ex + math.cos(ang + math.radians(-55 + 110 * j / 8)) * fw * (0.75 + 0.25 * math.sin(math.pi * j / 8)),
                            ey + math.sin(ang + math.radians(-55 + 110 * j / 8)) * fw * (0.75 + 0.25 * math.sin(math.pi * j / 8)) * 1.35) for j in range(9)]
        out.append(F(fan, INK if back else PAPER, 0.75 if back else 1.0))
        out.append(P(" ".join(rays), max(0.5, min(0.9, r * 0.035)), INK, 0.9))
    out.append(f'<circle cx="{f1(tx)}" cy="{f1(ty)}" r="{f1(max(1.2, r * 0.12))}" fill="{INK}"/>')
    return "".join(out)


def bungalow(U, C, X, Z0, Z1, seed, ht=3.8, roof_h=2.0, depth=10.0, shade=False, arches=True, tower=False):
    """A Spanish-revival bungalow facing the street from the plane X: stucco wall, arched picture window and
    porch, barrel-tile roof with a scalloped eave, a hedge in front."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1             # toward the street
    out = []
    wall = C.qx(X, Z0, Z1, 0, ht)
    roof = [C(X + sg * 0.5, ht, Z0), C(X + sg * 0.5, ht, Z1), C(X - sg * depth * 0.4, ht + roof_h, Z1 - 1.5), C(X - sg * depth * 0.4, ht + roof_h, Z0 + 1.5)]
    out.append(F(roof, PAPER))
    m = homog([roof[3], roof[2], roof[1], roof[0]])
    tiles = [(m(u, 0), m(u, 1)) for u in [k / max(8, int((Z1 - Z0) * 3)) for k in range(1, max(8, int((Z1 - Z0) * 3)))]]
    out.append(segs(tiles, 0.6, seed, 0.1, op=0.8))
    out.append(H(U, roof, 0, 2.2, 0.55, op=0.55))
    out.append(F(wall, PAPER))
    out.append(ST(U, wall, min(900, int(abs(wall[1][0] - wall[0][0]) * 2)), r=(0.3, 0.6), op=0.45))
    # openings
    n = max(2, int((Z1 - Z0) / 4))
    ops = []
    for i in range(n):
        za, zb = Z0 + (Z1 - Z0) * (i + 0.25) / n, Z0 + (Z1 - Z0) * (i + 0.75) / n
        q = C.qx(X, za, zb, 0.7 if i else 0.0, ht * 0.78)
        ops.append(arch_q(q, 0.32, 8) if arches else q)
    out.append(f'<path d="{" ".join(poly(o) for o in ops)}" fill="{INK}" opacity="0.85"/>')
    for o in ops:
        out.append(pen(o, 0.9, seed, 0.05))
    if shade:
        out.append(H(U, wall, 80, 2.2, 0.7, op=0.9) + H(U, wall, 10, 3.2, 0.55, op=0.6))
    # eave: scalloped tile ends and its shadow on the wall
    out.append(H(U, C.qx(X, Z0, Z1, ht - 0.45, ht), 0, 1.2, 0.6, wob=0.05, brk=0))
    ev = []
    k = 0
    z = Z0
    while z < Z1:
        a, b = C(X + sg * 0.5, ht, z), C(X + sg * 0.5, ht, min(Z1, z + 0.35))
        ev.append(f"Q {f1((a[0] + b[0]) / 2)} {f1(a[1] + max(0.8, abs(b[0] - a[0]) * 0.45))} {f1(b[0])} {f1(b[1])}")
        z += 0.35
    a0 = C(X + sg * 0.5, ht, Z0)
    out.append(P(f"M {f1(a0[0])} {f1(a0[1])} " + " ".join(ev), 0.9))
    out.append(pen([roof[3], roof[2]], 1.2, seed, 0.1) + pen([roof[0], roof[3]], 1.1, seed, 0.1))
    out.append(pen([C(X, 0, Z0), C(X, ht, Z0)], 1.6, seed, 0.1) + pen([C(X, 0, Z0), C(X, 0, Z1)], 1.2, seed, 0.1))
    if tower:
        zc = Z0 + (Z1 - Z0) * 0.3
        tq = C.qx(X + sg * 0.2, zc - 1.1, zc + 1.1, ht, ht + 3.0)
        out.append(F(tq, PAPER) + (H(U, tq, 80, 2.0, 0.6) if shade else "") + F(arch_q(quad_sub3(tq, 0.3, 0.2, 0.7, 0.7), 0.4, 6), INK, 0.85) + sketch(tq, 1.1, seed, 0.2))
        ap = C(X + sg * 0.2, ht + 4.4, zc)
        out.append(F([tq[0], ap, tq[1]], PAPER) + H(U, [tq[0], ap, tq[1]], 0, 1.4, 0.6) + pen([tq[0], ap, tq[1]], 1.1, seed, 0.1))
    return "".join(out)


def observatory(U, cx, base, w, seed):
    """The hilltop observatory, white against the hills: a long low hall with a central copper dome on a drum,
    two smaller domes on the wings, a colonnaded front, and the monument on the lawn before it (light from the
    right, so the left flanks are in shade)."""
    s = w / 100.0
    out = []

    def dome(x, y, r, drum):
        d_ = [(x - r, y - drum)] + [(x - r * math.cos(math.pi * i / 16), y - drum - r * math.sin(math.pi * i / 16)) for i in range(1, 16)] + [(x + r, y - drum)]
        dr = [(x - r * 0.98, y), (x + r * 0.98, y), (x + r * 0.98, y - drum), (x - r * 0.98, y - drum)]
        o = F(dr, PAPER) + H(U, [(x - r, y), (x - r * 0.2, y), (x - r * 0.2, y - drum), (x - r, y - drum)], 90, 1.1, 0.55) + sketch(dr, 1.0, seed, 0.2)
        o += F(d_, PAPER) + clipped(U("od"), poly(d_), H(U, d_, 90, (1.0, 3.4), 0.6, box=(x - r, y - drum - r, x + r, y - drum), dark=(x - r, y), wob=0.05, brk=0)
                                       + P(" ".join(f"M {f1(x - r)} {f1(y - drum - r * k / 4)} Q {f1(x)} {f1(y - drum - r * k / 4 + r * 0.12)} {f1(x + r)} {f1(y - drum - r * k / 4)}" for k in range(1, 4)), 0.5, INK, 0.6))
        o += pen(d_, 1.2, seed, 0.05) + seg(x, y - drum - r, x, y - drum - r - max(2, r * 0.3), 1.0, seed, 0)
        return o
    hall = [(cx - 50 * s, base - 9 * s), (cx + 50 * s, base - 9 * s), (cx + 50 * s, base), (cx - 50 * s, base)]
    out.append(F(hall, PAPER))
    cols = [((cx + u * s, base - 8.5 * s), (cx + u * s, base - 1 * s)) for u in range(-44, 45, 4) if abs(u) > 13]
    out.append(segs(cols, max(0.6, 0.9 * s), seed, 0))
    out.append(H(U, [(cx - 50 * s, base - 9 * s), (cx - 44 * s, base - 9 * s), (cx - 44 * s, base), (cx - 50 * s, base)], 90, 1.0, 0.6))
    out.append(sketch(hall, 1.2, seed, 0.3))
    out.append(dome(cx - 40 * s, base - 9 * s, 6.5 * s, 4 * s) + dome(cx + 40 * s, base - 9 * s, 6.5 * s, 4 * s))
    cb = [(cx - 14 * s, base - 16 * s), (cx + 14 * s, base - 16 * s), (cx + 14 * s, base), (cx - 14 * s, base)]
    out.append(F(cb, PAPER) + H(U, [(cx - 14 * s, base - 16 * s), (cx - 6 * s, base - 16 * s), (cx - 6 * s, base), (cx - 14 * s, base)], 90, 1.0, 0.6)
               + F(arch_q([(cx - 4 * s, base - 12 * s), (cx + 4 * s, base - 12 * s), (cx + 4 * s, base), (cx - 4 * s, base)], 0.4, 6), INK, 0.85) + sketch(cb, 1.2, seed, 0.3))
    out.append(dome(cx, base - 16 * s, 12 * s, 5 * s))
    # the monument on the lawn and the terrace wall
    out.append(nib([(cx - 2 * s, base + 7 * s), (cx - 2.4 * s, base - 20 * s)], max(1.4, 2.2 * s), taper=(1, 0.5), seed=seed, color=INK))
    out.append(pen([(cx - 62 * s, base + 2 * s), (cx + 62 * s, base + 2 * s)], 1.0, seed, 0.1))
    return "".join(out)


def ridge_band(U, pts, base, seed, tone=0.4, op=1.0, scrub=True, ang=70, houses=0):
    """A hill ridge in engraving: paper body, slope hatching graded to the shade side, chaparral stipple and
    scrub ticks, a few hillside houses."""
    rnd = random.Random(seed)
    d = smooth_open(pts) + f" L {f1(pts[-1][0])} {base} L {f1(pts[0][0])} {base} Z"
    x0, x1 = pts[0][0], pts[-1][0]
    top = min(p[1] for p in pts)
    inner = [H(U, d, ang, (lerp(5, 2.4, tone), lerp(3, 1.4, tone)), (0.5, 0.75), box=(x0, top, x1, base), dark=(x0, base), wob=1.2, brk=0.55),
             H(U, d, ang - 75, lerp(6, 3, tone), 0.5, box=(x0, top, x1, base), dark=(x0, base), span=(0.5, 1), wob=1.0, brk=0.6, op=0.6)]
    if scrub:
        inner.append(ST(U, d, int((x1 - x0) * (base - top) * 0.02), light=((x0 + x1) / 2 + 100, top), r=(0.5, 1.1), op=0.8, box=(x0, top, x1, base)))
        ticks = []
        for _ in range(int((x1 - x0) * 0.5)):
            x = rnd.uniform(x0, x1)
            y = rnd.uniform(top, base)
            ticks.append(f"M {f1(x - 1.6)} {f1(y)} q 1.6 2 3.2 0")
        inner.append(P(" ".join(ticks), 0.6, INK, 0.7))
    for _ in range(houses):
        x = rnd.uniform(x0 + 10, x1 - 10)
        y = rnd.uniform(top + 12, base - 4)
        w_, h_ = rnd.uniform(4, 8), rnd.uniform(3, 5)
        inner.append(F([(x, y - h_), (x + w_, y - h_), (x + w_, y), (x, y)], PAPER) + P(f"M {f1(x)} {f1(y - h_)} h {f1(w_)} v {f1(h_)} M {f1(x + w_ * 0.3)} {f1(y - h_ * 0.5)} h {f1(w_ * 0.3)}", 0.6))
    out = F(d, PAPER) + clipped(U("rb"), d, "".join(inner)) + P(smooth_open(pts), 1.4)
    return f'<g opacity="{op:.2f}">{out}</g>'


@design("los-angeles")
def los_angeles(U):
    """Late afternoon on a palm-lined street at the foot of the Hollywood Hills: rows of soaring fan palms
    marching to the hills, their long shadows striping the road, Spanish-revival bungalows behind hedges, the
    white observatory on its ridge, a vermilion convertible heading up the street, phone wires, a dog walker."""
    C = Cam2(f=290, cx=300, vpy=330, eye=1.7, yaw=-8)
    art = []
    HZ = C.vpy
    art.append(cloud(U, 476, 84, 110, 14, 5) + cloud(U, 128, 104, 80, 11, 6))
    # the hills: a pale far range, the observatory's ridge with its gullies, a nearer spur
    art.append(ridge_band(U, [(40, 236), (90, 214), (140, 204), (190, 210), (240, 196), (290, 188), (340, 198), (400, 184), (460, 192), (520, 178), (580, 200)],
                          HZ + 2, 3, tone=0.25, op=0.5, scrub=False, ang=58))
    obs_ridge = [(30, 292), (70, 262), (120, 236), (160, 216), (194, 198), (226, 192), (262, 196), (300, 214), (350, 238), (400, 248), (450, 246),
                 (510, 260), (580, 282)]
    art.append(ridge_band(U, obs_ridge, HZ + 2, 4, tone=0.55, op=1.0, houses=22))
    # gullies running down the ridge
    rnd = random.Random(44)
    gul = []
    for gx in (96, 140, 172, 290, 330, 372, 430, 488, 540):
        gy = min(y for x_, y in obs_ridge if abs(x_ - gx) < 60) + 10
        gul.append([(gx, gy), (gx + rnd.uniform(-6, 6), gy + 24), (gx + rnd.uniform(-10, 10), HZ - 4)])
    for k, g in enumerate(gul):
        art.append(nib(g, 1.6, taper=(0.2, 0.8), seed=44 + k, color=INK, op=0.85))
        art.append(H(U, [g[0], (g[0][0] + 14, g[1][1]), (g[2][0] + 18, g[2][1]), g[2], g[1]], 75, 1.6, 0.6, op=0.8))
    scrub = []
    for i in range(900):
        x = rnd.uniform(36, 578)
        ytop_ = min(lerp(a_[1], b_[1], (x - a_[0]) / (b_[0] - a_[0])) for a_, b_ in zip(obs_ridge, obs_ridge[1:]) if a_[0] <= x <= b_[0])
        y = ytop_ + 3 + (HZ - ytop_) * rnd.random() ** 0.8
        if 180 < x < 272 and y < 212:
            continue
        r = rnd.uniform(1.0, 2.4) * (0.8 + 0.5 * (y - 190) / 140)
        scrub.append(smooth_closed(scallop_pts(x, y, r * 1.3, r * 0.8, 3000 + i, 7, 0.25)))
    art.append(f'<path d="{" ".join(scrub)}" fill="{INK}" opacity="0.78"/>')
    art.append(observatory(U, 226, 194, 84, 5))
    art.append(ridge_band(U, [(330, 300), (380, 284), (430, 280), (480, 286), (540, 292), (600, 302)], HZ + 2, 6, tone=0.75, houses=6))
    art.append(ridge_band(U, [(0, 306), (60, 296), (120, 300), (190, 312), (240, 322)], HZ + 2, 7, tone=0.7, houses=4))
    # ground: road, curbs, parkways, sidewalks, lawns
    RW, PW, SW, HX = 5.0, 7.0, 8.6, 11.0
    road = [C(-RW, 0, 4), C(-RW, 0, 300), C(RW, 0, 300), C(RW, 0, 4)]
    art.append(F(road, PAPER) + H(U, road, 1, (4.2, 2.0), 0.5, op=0.45, box=(0, HZ, 600, 600), dark=(300, 600)))
    art.append(segs([(C(-0.12, 0, 5), C(-0.12, 0, 300)), (C(0.12, 0, 5), C(0.12, 0, 300))], 1.0, 7, 0.05))
    for sx in (-1, 1):
        pk = [C(sx * RW, 0.15, 4), C(sx * RW, 0.15, 300), C(sx * PW, 0.15, 300), C(sx * PW, 0.15, 4)]
        art.append(F(pk, PAPER) + clipped(U("pk"), poly(pk), segs([(C(sx * (RW + 0.2), 0.15, z), C(sx * (PW - 0.2), 0.15, z + 0.4)) for z in [4 + 0.5 * k for k in range(320)]], 0.6, 8, 0.2, op=0.6)))
        wk = [C(sx * PW, 0.15, 4), C(sx * PW, 0.15, 300), C(sx * SW, 0.15, 300), C(sx * SW, 0.15, 4)]
        art.append(F(wk, PAPER) + segs([(C(sx * PW, 0.15, z), C(sx * SW, 0.15, z)) for z in [4 + 1.5 * k for k in range(120)]], 0.55, 9, 0, op=0.5))
        art.append(pen([C(sx * RW, 0.15, 4), C(sx * RW, 0.15, 300)], 1.5, 10, 0.1) + pen([C(sx * RW, 0, 4), C(sx * RW, 0, 300)], 0.9, 11, 0.1))
        lawn = [C(sx * SW, 0.15, 4), C(sx * SW, 0.15, 300), C(sx * HX, 0.15, 300), C(sx * HX, 0.15, 4)]
        art.append(F(lawn, PAPER) + H(U, lawn, 0, (3.0, 1.6), 0.55, op=0.55, box=bbox(lawn)))
    # bungalows on both sides, far to near (right side in shade: the sun is low over the right-hand roofs)
    for sx in (-1, 1):
        z = 160.0
        k = 0
        rows = []
        while z > 9:
            L = random.Random(k * 13 + sx).uniform(11, 15)
            rows.append((max(5.0, z - L), z, k))
            z -= L + 3.5
            k += 1
        for z0, z1, k in rows:
            art.append(bungalow(U, C, sx * HX, z0, z1, 300 + k * 7 + sx, ht=3.6 + (k % 3) * 0.5, roof_h=1.8 + (k % 2) * 0.6, shade=sx > 0,
                                arches=k % 3 != 1, tower=(k % 4 == 2)))
            # hedge in front
            hx = sx * (HX - 1.0)
            for zz in [z0 + 1.2 + 2.2 * i for i in range(int((z1 - z0 - 1) / 2.2))]:
                x, y = C(hx, 0.15, zz)
                r = C.px(hx, zz, 0.9)
                if r > 1.5:
                    art.append(lobe(U, x, y - r * 0.6, r * 1.15, r * 0.8, 900 + int(zz * 10) + sx, light=(1, -1), w=max(0.6, min(1.1, r / 10)), dense=1.3))
    # long palm shadows across the road (cast from the right-hand palms toward the left)
    PZ = [24, 33, 42, 51, 60, 69, 78, 87, 96, 106, 117, 128, 140, 152]
    shd = []
    dxs, dzs = -0.74, -0.67
    for z in PZ:
        Bx, Bz = 6.1, z
        tm = min(21.0, (Bz - 3.8) / -dzs)
        Ex, Ez = Bx + dxs * tm, Bz + dzs * tm
        nx_, nz_ = 0.67 * 0.34, -0.74 * 0.34
        shd.append(poly([C(Bx + nx_, 0.01, Bz + nz_), C(Ex + nx_ * 0.8, 0.01, Ez + nz_ * 0.8), C(Ex - nx_ * 0.8, 0.01, Ez - nz_ * 0.8), C(Bx - nx_, 0.01, Bz - nz_)]))
        if tm >= 20.5:
            cx_, cz_ = Bx + dxs * 22.5, Bz + dzs * 22.5
            rr = random.Random(int(z))
            shd.append(smooth_closed([C(cx_ + 2.2 * math.cos(2 * math.pi * k / 14) * rr.uniform(0.7, 1.2), 0.01,
                                        cz_ + 1.9 * math.sin(2 * math.pi * k / 14) * rr.uniform(0.7, 1.2)) for k in range(14)]))
    spat, surl = hpat(U, 8, 1.6, 0.8)
    art.append(spat + f'<path d="{" ".join(shd)}" fill="{surl}" opacity="0.95"/>')
    # a ladder crosswalk across the near road
    cw = []
    for k in range(10):
        xa = -RW + 0.3 + k * 1.0
        cw.append(poly([C(xa, 0.01, 5.4), C(xa + 0.55, 0.01, 5.4), C(xa + 0.55, 0.01, 7.4), C(xa, 0.01, 7.4)]))
    art.append(f'<path d="{" ".join(cw)}" fill="{PAPER}"/>' + "".join(pen(poly_, 0.9, 12, 0.05, closed=True) for poly_ in
                                                           [[C(xa, 0.01, 5.4), C(xa + 0.55, 0.01, 5.4), C(xa + 0.55, 0.01, 7.4), C(xa, 0.01, 7.4)] for xa in [-RW + 0.3 + k * 1.0 for k in range(10)]]))
    # power poles and sagging wires down the left side
    poles = [(-8.0, z) for z in (13, 47, 81, 115, 149)]
    wires = []
    for (Xa, Za), (Xb, Zb) in zip(poles, poles[1:]):
        for dy, dx in ((9.6, -0.9), (9.6, 0.9), (8.8, 0.0)):
            pts = []
            for i in range(17):
                t = i / 16
                X = lerp(Xa, Xb, t) + dx
                Z = lerp(Za, Zb, t)
                Y = dy - 1.6 * 4 * t * (1 - t)
                pts.append(C(X, Y, Z))
            wires.append(smooth_open(pts))
    for X, Z in poles:
        a, b = C(X, 0, Z), C(X, 10.0, Z)
        art.append(seg(a[0], a[1], b[0], b[1], max(1.0, C.px(X, Z, 0.28)), int(Z), 0))
        c1, c2 = C(X - 1.2, 9.6, Z), C(X + 1.2, 9.6, Z)
        art.append(seg(c1[0], c1[1], c2[0], c2[1], max(0.8, C.px(X, Z, 0.16)), int(Z) + 1, 0))
    art.append(P(" ".join(wires), 0.6, INK, 0.85))
    # the palms, far to near on both sides
    for k, z in enumerate(PZ[::-1]):
        for sx in (-1, 1):
            if sx < 0 and z < 30:
                continue
            X = sx * 6.0
            zz = z + (0 if sx > 0 else 4.5)
            x, y = C(X, 0.15, zz)
            hp = C.px(X, zz, min(24 + (k % 3) * 2.5, 0.8 * zz))
            art.append(fan_palm(U, x, y, hp, 700 + k * 2 + sx, lean=0.012 * ((k + (sx > 0)) % 3 - 1), light=1))
    # a big pepper tree on the near left lawn
    x, y = C(-9.8, 0.15, 11)
    art.append(canopy(U, x, y, C.px(-9.8, 11, 9.5), C.px(-9.8, 11, 7.0), 777, light=(1, -1), lobe_r=13, shape=0.7, lw=1.3, dense=1.3))
    # lamps (twin-globe street lights)
    for sx, z in ((1, 28), (-1, 21), (1, 65), (-1, 56)):
        x, y = C(sx * 5.5, 0.15, z)
        hp = C.px(sx * 5.5, z, 5.0)
        art.append(lamp(x, y, hp, 50 + z, "globe", max(1.1, min(2.2, hp / 40))))
        art.append(f'<circle cx="{f1(x - hp * 0.09)}" cy="{f1(y - hp * 0.8)}" r="{f1(hp * 0.06)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
                   f'<circle cx="{f1(x + hp * 0.09)}" cy="{f1(y - hp * 0.8)}" r="{f1(hp * 0.06)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
                   + seg(x - hp * 0.09, y - hp * 0.76, x + hp * 0.09, y - hp * 0.76, 1.0, z, 0))
    # traffic: the vermilion convertible heading up the street, a car coming down
    x, y = C(2.4, 0, 19)
    art.append(car_rear(U, x, y, C.px(2.4, 19, 1.95), 60, acc=True))
    x, y = C(-2.5, 0, 72)
    art.append(car_rear(U, x, y, C.px(-2.5, 72, 1.9), 61))
    for X, Z, sd in ((4.0, 52, 62), (-4.0, 40, 63), (4.0, 33, 64), (-4.0, 26, 65), (-4.0, 14.5, 66)):
        x, y = C(X, 0, Z)
        art.append(car_rear(U, x, y, C.px(X, Z, 1.9), sd))
    # people: a dog walker, a jogger, neighbours
    X, Z = -7.8, 17
    x, y = C(X, 0.15, Z)
    hp = C.px(X, Z, 1.72)
    art.append(person(x, y, hp, 70, flip=False))
    dx_, dy_ = x + hp * 0.5, y
    dog = [(dx_ - hp * 0.18, dy_ - hp * 0.2), (dx_ + hp * 0.14, dy_ - hp * 0.22), (dx_ + hp * 0.2, dy_ - hp * 0.32), (dx_ + hp * 0.26, dy_ - hp * 0.26),
           (dx_ + hp * 0.16, dy_ - hp * 0.12), (dx_ - hp * 0.16, dy_ - hp * 0.1)]
    art.append(F(smooth_closed(dog), INK) + segs([((dx_ - hp * 0.14, dy_ - hp * 0.12), (dx_ - hp * 0.15, dy_)), ((dx_ + hp * 0.12, dy_ - hp * 0.12), (dx_ + hp * 0.13, dy_)),
                                                   ((dx_ - hp * 0.18, dy_ - hp * 0.18), (dx_ - hp * 0.26, dy_ - hp * 0.28))], max(1.0, hp * 0.04), 71, 0))
    art.append(P(f"M {f1(x + hp * 0.08)} {f1(y - hp * 0.5)} Q {f1(x + hp * 0.3)} {f1(y - hp * 0.25)} {f1(dx_ + hp * 0.2)} {f1(dy_ - hp * 0.3)}", 0.7))
    for X, Z, sd, fl in ((7.8, 26, 2, True), (8.0, 44, 3, False), (-7.9, 62, 4, True), (-7.7, 38, 5, False), (7.8, 90, 6, True)):
        art.append(ppl(C, X, Z, 70 + sd, Y=0.15, flip=fl, bag=sd == 5))
    art.append(bird(392, 150, 6, 80) + bird(410, 138, 5, 81) + bird(170, 176, 5, 82))
    return plate(U, "los-angeles", art, 151)


# ================================================================ build
def main(slugs):
    for slug, fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save(COL, slug, fn(Uids(slug)))
        print("wrote", slug)


if __name__ == "__main__":
    main(sys.argv[1:])
