"""Ink Cities, engraved edition (set B).

Ten more cities drawn in the manner of the approved engraved Paris plate (ink_cities_fine.paris): a rich
pen-and-ink engraving on warm paper, with tonal hatching and cross-hatching that build form and atmosphere,
a true, deep viewpoint (real perspective cameras where it is a street), small life everywhere (people, trees,
lamps, birds, boats, carriages), one faded-vermilion accent per plate, the picture dissolving into the paper
through a soft vignette (no hard frame), and the city name + coordinates set below exactly as on Paris.

Each plate has its own viewpoint and composition:
    washington-dc   the Capitol's west front across the Reflecting Pool, framed by Mall elms, its dome mirrored
    new-orleans     a French Quarter street of iron-lace galleries toward the cathedral's three spires
    san-francisco   looking down a steep street: a cable car climbing, Victorians stepping down, the bay beyond
    savannah        an oak-lined square: live oaks draped in Spanish moss arching over a tiered iron fountain
    istanbul        across the Golden Horn: the Galata Bridge, ferries and boats, domes and minarets on the hill
    nashville       Lower Broadway at dusk from a corner: honky-tonks with marquee blade signs, a busker
    boston          Acorn Street on Beacon Hill: a narrow cobbled lane between brick rowhouses with gas lamps
    charleston      Rainbow Row seen along East Bay Street: palmettos and a horse-drawn carriage
    havana          a colonial street of arcades and balconies running down to the Malecon, a vintage car
    barcelona       from a balcony over a tree-lined avenue toward the great basilica's spires (generic)

Run from tools/designs:  python3 ink_engraved_b.py [slug ...]
"""
import math
import random
import sys

from common import DMS, save
from gouache import smooth_closed, smooth_open
from kitchen_ink import clipped, cr, nib, poly
from ink_cities_fine import (INK, PAPER, Cam, F, P, T, XH, accent, bbox, bird, cloud, cobbles, coords_line,
                             cyclist, f1, facade, finish, ground_paper, homog, lamp, lerp, lobe, name_size, palm, pen, person,
                             pt, scallop_d, scallop_pts, seg, segs, sketch, soft_frame, tree, ST)
import ink_cities_fine as icf


def H(U, clip, ang=45, gap=4.0, w=1.0, box=None, **kw):
    """ink_cities_fine.H, but a hatch box that runs far off the page (a ground plane projected from just in
    front of the camera) is cut back to the page so the file does not fill with invisible lines."""
    if box is None:
        box = bbox(clip) if not isinstance(clip, str) else (0, 0, 600, 600)
    x0, y0, x1, y1 = box
    if x0 < -300 or y0 < -300 or x1 > 900 or y1 > 900:
        box = (max(x0, -40), max(y0, -40), min(x1, 640), min(y1, 640))
    return icf.H(U, clip, ang, gap, w, box=box, **kw)

COL = "ink-cities"

CITIES = {
    "washington-dc": ("Washington, DC", "38.9072° N · 77.0369° W"),
    "new-orleans": ("New Orleans", "29.9511° N · 90.0715° W"),
    "san-francisco": ("San Francisco", "37.7749° N · 122.4194° W"),
    "savannah": ("Savannah", "32.0809° N · 81.0912° W"),
    "istanbul": ("Istanbul", "41.0082° N · 28.9784° E"),
    "nashville": ("Nashville", "36.1627° N · 86.7816° W"),
    "boston": ("Boston", "42.3601° N · 71.0589° W"),
    "charleston": ("Charleston", "32.7765° N · 79.9311° W"),
    "havana": ("Havana", "23.1136° N · 82.3666° W"),
    "barcelona": ("Barcelona", "41.3874° N · 2.1686° E"),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Ids(icf.Ids):
    """Id factory with this file's own prefix (the line-art set already uses icf-<slug>-...)."""
    def __call__(self, tag="u"):
        self.n += 1
        return f"ieb-{self.slug}-{tag}{self.n}"


# ================================================================ plate
def plate(U, slug, art, seed, cy=252, rx=262, ry=222, expo=3.4, inset=0.24, paper_seed=21):
    """Paper, the drawing dissolving into it through a soft vignette, and the Paris title system below."""
    name, coords = CITIES[slug]
    return (ground_paper(U, paper_seed)
            + soft_frame(U, 300, cy, rx, ry, seed, "".join(art), expo=expo, inset=inset)
            + T(300, 503, name, DMS, name_size(name))
            + coords_line(300, 534, coords, rule_len=30, diamonds=True)
            + finish(U))


# ================================================================ engraving tools
def tone(U, clip, lvl, ang=70, box=None, dark=None, op=1.0, wob=0.25, brk=0.08, span=(0, 1)):
    """Engraved tone: 1 light hatch, 2 close hatch, 3 cross-hatch, 4 dense triple hatch."""
    if lvl <= 0:
        return ""
    g = {1: 4.0, 2: 2.9, 3: 2.7, 4: 2.2}[min(4, int(round(lvl)))]
    w = {1: 0.7, 2: 0.8, 3: 0.85, 4: 0.9}[min(4, int(round(lvl)))]
    out = H(U, clip, ang, g, w, op=op, box=box, dark=dark, wob=wob, brk=brk, span=span)
    if lvl >= 3:
        out += H(U, clip, ang + 62, g * 1.25, w * 0.9, op=op, box=box, dark=dark, wob=wob, brk=brk, span=span)
    if lvl >= 4:
        out += H(U, clip, ang - 48, g * 1.5, w * 0.85, op=op, box=box, dark=dark, wob=wob, brk=brk, span=span)
    return out


class YCam(Cam):
    """Pinhole camera turned by `yaw` radians about the vertical (positive = looking toward +X)."""
    def __init__(self, f=300, cx=300, vpy=300, eye=1.6, yaw=0.0, ox=0.0):
        super().__init__(f, cx, vpy, eye)
        self.c, self.s, self.ox = math.cos(yaw), math.sin(yaw), ox

    def __call__(self, X, Y, Z):
        X = X + self.ox
        x = X * self.c - Z * self.s
        z = X * self.s + Z * self.c
        z = max(z, 0.05)
        return (self.cx + self.f * x / z, self.vpy + self.f * (self.eye - Y) / z)

    def depth(self, X, Z):
        return (X + self.ox) * self.s + Z * self.c


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def mirror_use(U, gid, yw, k=0.5, op=0.5, clip=None, seed=1, x0=0, x1=600, y1=600, dens=1.0):
    """Reflection of the group `gid` in still water at y = yw, squashed by k and broken into horizontal
    strokes like an engraver's reflection."""
    rnd = random.Random(seed)
    mid = U("mm")
    bars = []
    y = yw + 1.0
    while y < y1:
        t = (y - yw) / max(1.0, y1 - yw)
        gap = lerp(1.5, 3.6, t)
        x = x0 - rnd.uniform(0, 30)
        while x < x1:
            L = rnd.uniform(12, 60) * (1 + t)
            bars.append(f"M {f1(x)} {f1(y)} L {f1(x + L)} {f1(y)}")
            x += L + rnd.uniform(1.5, 9) / dens
        y += gap
    mask = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">'
            f'<path d="{" ".join(bars)}" stroke="#fff" stroke-width="{1.3:.1f}" fill="none"/></mask>')
    body = (f'<g mask="url(#{mid})" opacity="{op:.2f}"><use href="#{gid}" '
            f'transform="matrix(1 0 0 {-k:.3f} 0 {(1 + k) * yw:.2f})"/></g>')
    if clip:
        return f"<defs>{mask}</defs>" + clipped(U("mc"), clip, body)
    return f"<defs>{mask}</defs>" + body


def strokes_h(x0, x1, y0, y1, seed, gap=(2.4, 6), ln=(6, 26), w=0.9, op=0.8, clip=None, U=None):
    """Loose horizontal ground strokes (grass, sand, paving shadow)."""
    rnd = random.Random(seed)
    ls = []
    y = y0
    while y < y1:
        t = (y - y0) / max(1, y1 - y0)
        x = x0 - rnd.uniform(0, ln[1])
        while x < x1:
            L = rnd.uniform(*ln) * (0.6 + t)
            ls.append(((x, y + rnd.uniform(-0.6, 0.6)), (x + L, y + rnd.uniform(-0.6, 0.6))))
            x += L + rnd.uniform(3, 12)
        y += lerp(gap[0], gap[1], t)
    out = segs(ls, w, seed, 0.4, op)
    if clip is not None and U is not None:
        return clipped(U("sh"), clip, out)
    return out


def grass(x0, x1, y, seed, h=4, dens=1.0, w=0.8, op=0.85):
    """Tufts of grass strokes along a ground line."""
    rnd = random.Random(seed)
    ls = []
    x = x0
    while x < x1:
        for _ in range(rnd.randint(2, 4)):
            a = rnd.uniform(-0.5, 0.5)
            hh = h * rnd.uniform(0.5, 1.2)
            ls.append(((x, y), (x + a * hh, y - hh)))
        x += rnd.uniform(2, 7) / dens
    return segs(ls, w, seed, 0.2, op)


def colonnade(U, x0, x1, top, bot, n, seed, w=1.0, back=0.9, shade=(0.55, 1.0), base_h=None, cap_h=None):
    """A row of n columns face-on: dark loggia behind, lit shafts with a hatched shadow side, capitals and bases."""
    out = [F(rect(x0, top, x1, bot), INK, back)]
    step = (x1 - x0) / n
    cw = step * 0.56
    ch = cap_h if cap_h is not None else max(1.5, (bot - top) * 0.07)
    bh = base_h if base_h is not None else max(1.2, (bot - top) * 0.05)
    shafts = []
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        shafts.append(rect(cx - cw / 2, top + ch, cx + cw / 2, bot - bh))
    out.append(F(" ".join(poly(s) for s in shafts), PAPER))
    if cw > 3:
        sh = [rect(cx - cw / 2 + cw * shade[0], top + ch, cx + cw / 2, bot - bh)
              for cx in [x0 + step * (i + 0.5) for i in range(n)]]
        out.append(H(U, " ".join(poly(s) for s in sh), 90, max(1.0, cw * 0.18), 0.6, box=(x0, top, x1, bot), wob=0, brk=0))
        out.append(segs([((s[0][0], s[0][1]), (s[3][0], s[3][1])) for s in shafts]
                        + [((s[1][0], s[1][1]), (s[2][0], s[2][1])) for s in shafts], w * 0.7, seed, 0.1))
    out.append(F(rect(x0 - 1, top, x1 + 1, top + ch), PAPER) + F(rect(x0 - 1, bot - bh, x1 + 1, bot), PAPER))
    out.append(segs([((x0 - 1, top), (x1 + 1, top)), ((x0 - 1, top + ch), (x1 + 1, top + ch)),
                     ((x0 - 1, bot - bh), (x1 + 1, bot - bh)), ((x0 - 1, bot), (x1 + 1, bot))], w, seed + 1, 0.2))
    return "".join(out)


def balustrade(x0, x1, y, h, seed, step=3.0, w=0.8, op=1.0):
    """A stone balustrade seen face-on: rail, plinth and a row of small balusters."""
    ls = [((x0, y - h), (x1, y - h)), ((x0, y), (x1, y))]
    x = x0 + step / 2
    while x < x1:
        ls.append(((x, y - h * 0.85), (x, y - h * 0.1)))
        x += step
    return segs(ls, w, seed, 0.1, op)


def window_grid(U, x0, x1, y0, y1, cols, rows, seed, mx=0.3, my=0.25, dark=0.86, sill=True, w=0.9, lit=0.0):
    """Face-on windows: dark panes with lintels and sills."""
    rnd = random.Random(seed)
    cw, rh = (x1 - x0) / cols, (y1 - y0) / rows
    panes, ls = [], []
    for i in range(cols):
        for j in range(rows):
            a, b = x0 + cw * (i + mx / 2), x0 + cw * (i + 1 - mx / 2)
            c, d = y0 + rh * (j + my / 2), y0 + rh * (j + 1 - my / 2)
            if lit and rnd.random() < lit:
                ls += [((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c))]
            else:
                panes.append(rect(a, c, b, d))
            if sill:
                ls.append(((a - 0.8, d + 0.6), (b + 0.8, d + 0.6)))
                ls.append(((a - 0.5, c - 1.0), (b + 0.5, c - 1.0)))
    out = F(" ".join(poly(p) for p in panes), INK, dark) if panes else ""
    return out + segs(ls, w, seed, 0.05)


def dark_tree_mass(U, pts, seed, lvl=3, ang=80, light=(-1, -1)):
    """A distant belt of trees: scalloped top, paper fill, tonal hatching and a few leaf ticks."""
    xs = [p[0] for p in pts]
    d = poly(pts)
    out = [F(d, PAPER), tone(U, d, lvl, ang, box=bbox(pts), wob=0.3, brk=0.2)]
    out.append(P(d, 1.0))
    return "".join(out)


def crown(U, cx, cy, rx, ry, seed, light=(-1, -1), lw=1.4, dense=1.0, n=7, flat=0.0, spread=1.0):
    """A big tree crown built from several foliage lobes (back ones darker), for framing trees."""
    rnd = random.Random(seed)
    spots = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random()) * 0.55 * spread
        spots.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r * (1 - flat), rx * rnd.uniform(0.38, 0.52),
                      ry * rnd.uniform(0.36, 0.5)))
    spots.sort(key=lambda s: -((s[0] - cx) * light[0] + (s[1] - cy) * light[1]))
    under = smooth_closed(scallop_pts(cx, cy, rx * 0.9, ry * 0.85, seed + 7, 14, 0.1))
    out = [F(under, INK, 0.85)]
    for i, (x, y, a, b) in enumerate(spots):
        out.append(lobe(U, x, y, a, b, seed * 17 + i, light=light, w=lw, dense=dense))
    return "".join(out)


def limb(pts, w0, seed, taper=(1, 0.35)):
    return nib(pts, w0, taper=taper, ramp=0.3, seed=seed, color=INK)


def gull(x, y, s, seed=1, w=1.5):
    """A gull in flight: a deeper M than the generic bird, with a dot body."""
    rnd = random.Random(seed)
    a = rnd.uniform(-0.15, 0.15)
    return (nib([(x - s, y - s * (0.1 + a)), (x - s * 0.55, y - s * 0.55), (x - s * 0.12, y - s * 0.12), (x, y)], w,
                taper=(0.15, 0.7), seed=seed, color=INK)
            + nib([(x, y), (x + s * 0.12, y - s * 0.12), (x + s * 0.55, y - s * 0.55), (x + s, y - s * (0.1 - a))], w,
                  taper=(0.7, 0.15), seed=seed + 1, color=INK)
            + f'<ellipse cx="{f1(x)}" cy="{f1(y + s * 0.05)}" rx="{f1(s * 0.18)}" ry="{f1(s * 0.09)}" fill="{INK}"/>')


def duck(x, y, s, seed=1, flip=False, wake=True):
    k = -1 if flip else 1
    body = [(x - k * s * 0.6, y), (x - k * s * 0.5, y - s * 0.35), (x + k * s * 0.1, y - s * 0.4), (x + k * s * 0.35, y - s * 0.25),
            (x + k * s * 0.45, y - s * 0.75), (x + k * s * 0.62, y - s * 0.8), (x + k * s * 0.7, y - s * 0.7),
            (x + k * s * 0.88, y - s * 0.66), (x + k * s * 0.62, y - s * 0.55), (x + k * s * 0.55, y - s * 0.2),
            (x + k * s * 0.5, y)]
    out = F(body, INK, 0.92)
    if wake:
        out += segs([((x - k * s * 0.8, y + 1.2), (x - k * s * 2.6, y + s * 0.35)), ((x - k * s * 0.8, y + 1.2), (x - k * s * 2.4, y - s * 0.05)),
                     ((x - s * 0.9, y + 2.5), (x + s * 0.9, y + 2.5))], 0.8, seed, 0.3)
    return out


def walker(x, y, h, seed=1, flip=False, kind="plain", op=1.0):
    """person() with a few variants: a dress, a hat, a child, a dog alongside."""
    out = [person(x, y, h, seed, op=op, flip=flip, bag=(kind == "bag"))]
    s = -1 if flip else 1
    if kind == "dress":
        out.append(F([(x - h * 0.11, y - h * 0.5), (x + h * 0.11, y - h * 0.5), (x + h * 0.17, y - h * 0.18), (x - h * 0.17, y - h * 0.18)], INK, op))
    if kind == "hat":
        out.append(F(smooth_closed([(x - h * 0.15, y - h * 0.97), (x + h * 0.15, y - h * 0.97), (x + h * 0.08, y - h * 1.0), (x - h * 0.08, y - h * 1.0)]), INK, op))
        out.append(F(rect(x - h * 0.07, y - h * 1.08, x + h * 0.07, y - h * 0.97), INK, op))
    if kind == "dog":
        d = h * 0.3
        dx = x + s * h * 0.35
        out.append(F(smooth_closed([(dx - d * 0.6, y - d * 0.55), (dx + d * 0.5, y - d * 0.6), (dx + d * 0.55, y - d * 0.35), (dx - d * 0.6, y - d * 0.3)]), INK, op))
        out.append(P(f"M {f1(dx - d * 0.5)} {f1(y - d * 0.35)} L {f1(dx - d * 0.55)} {f1(y)} M {f1(dx + d * 0.45)} {f1(y - d * 0.35)} L {f1(dx + d * 0.5)} {f1(y)}", max(1.0, d * 0.12), INK, op))
        out.append(f'<circle cx="{f1(dx + s * d * 0.65)}" cy="{f1(y - d * 0.72)}" r="{f1(d * 0.2)}" fill="{INK}" opacity="{op:.2f}"/>')
        out.append(P(f"M {f1(x + s * h * 0.12)} {f1(y - h * 0.5)} Q {f1(x + s * h * 0.3)} {f1(y - h * 0.3)} {f1(dx + s * d * 0.5)} {f1(y - d * 0.7)}", 0.7, INK, op))
    if kind == "child":
        pass
    return "".join(out)


# ================================================================ WASHINGTON, DC
def flag_small(U, x, y, w, h, seed):
    """A small flag on a mast standing on a roof: stripes in the vermilion accent, a dark canton."""
    d = smooth_open([(x, y), (x + w * 0.35, y - h * 0.18), (x + w * 0.7, y + h * 0.05), (x + w, y - h * 0.08)])
    d += " L " + smooth_open([(x + w, y + h - h * 0.08), (x + w * 0.7, y + h + h * 0.05), (x + w * 0.35, y + h - h * 0.18), (x, y + h)])[2:] + " Z"
    out = [F(d, PAPER), accent(U, d, (x, y - h, x + w, y + h * 2), seed, op=1.0, ang=0, n=10, length=(5, 10), width=(1, 1.8))]
    out.append(clipped(U("fs"), d, segs([((x, y + h * t), (x + w, y + h * t - h * 0.05)) for t in (0.2, 0.42, 0.64, 0.86)], 0.8, seed, 0.2)
                       + F(rect(x, y - h, x + w * 0.42, y + h * 0.5), INK, 0.85)))
    out.append(P(d, 0.9) + seg(x, y - 1.5, x, y + h * 2.6, 1.2, seed, 0))
    return "".join(out)


def stone_front(U, x0, x1, top, bot, seed, cols, rows, win_op=0.7, course=3.4, pil=True):
    """A lit marble front face-on: coursing, small dark windows with pediments, pilasters between bays."""
    out = [F(rect(x0, top, x1, bot), PAPER)]
    ls = [((x0, y), (x1, y)) for y in [top + course * i for i in range(1, int((bot - top) / course))]]
    out.append(segs(ls, 0.45, seed, 0.1, op=0.5))
    cw = (x1 - x0) / cols
    rh = (bot - top) / rows
    panes, lines = [], []
    for i in range(cols):
        for j in range(rows):
            a, b = x0 + cw * (i + 0.3), x0 + cw * (i + 0.7)
            c, d = top + rh * (j + 0.28), top + rh * (j + 0.82)
            panes.append(rect(a, c, b, d))
            lines.append(((a - 0.8, c - 1.4), (b + 0.8, c - 1.4)))
            lines.append(((a - 0.6, d + 0.6), (b + 0.6, d + 0.6)))
        if pil and i:
            xp = x0 + cw * i
            lines.append(((xp, top + 1), (xp, bot - 1)))
    out.append(F(" ".join(poly(p) for p in panes), INK, win_op))
    out.append(segs(lines, 0.7, seed + 1, 0.05))
    return "".join(out)


def capitol(U, cx, yb, k, seed=1):
    """The Capitol's west front in elevation (k px per foot, yb = ground line under the building): wings with
    colonnaded fronts, the central block, the cast-iron dome on its peristyle and attic, lantern and Freedom.
    Light from the upper left."""
    out = []

    def Y(ft):
        return yb - ft * k

    def X(ft):
        return cx + ft * k
    # --- wings and connectors ------------------------------------------------------------------------------
    for sgn in (-1, 1):
        a, b = sorted((X(sgn * 150), X(sgn * 240)))
        out.append(stone_front(U, a, b, Y(60), yb, seed + sgn, 7, 3, win_op=0.62))
        out.append(F(rect(a - 1, Y(64), b + 1, Y(60)), PAPER) + H(U, rect(a, Y(60), b, Y(57)), 0, 1.2, 0.6))
        out.append(balustrade(a, b, Y(64), 4 * k, seed + 2, 2.4, 0.6))
        out.append(sketch(rect(a, Y(64), b, yb), 1.0, seed + 3, 0.3))
        a, b = sorted((X(sgn * 240), X(sgn * 376)))
        out.append(stone_front(U, a, b, Y(64), yb, seed + 3 * sgn, 10, 3, win_op=0.62))
        pa, pb = sorted((X(sgn * 268), X(sgn * 348)))
        out.append(F(rect(pa - 2, Y(70), pb + 2, yb), PAPER))
        out.append(colonnade(U, pa, pb, Y(64), Y(24), 10, seed + 4, w=0.8, back=0.7))
        out.append(stone_front(U, pa - 2, pb + 2, Y(24), yb, seed + 5, 8, 1, win_op=0.6, pil=False))
        out.append(F(rect(pa - 3, Y(70), pb + 3, Y(64)), PAPER) + H(U, rect(pa - 3, Y(66), pb + 3, Y(64)), 0, 1.0, 0.6))
        out.append(F(rect(a - 1, Y(68), b + 1, Y(64)), PAPER) + balustrade(a, b, Y(68), 4 * k, seed + 6, 2.4, 0.6))
        out.append(sketch(rect(a, Y(68), b, yb), 1.2, seed + 7, 0.4) + sketch(rect(pa - 2, Y(70), pb + 2, yb), 1.0, seed + 8, 0.3))
        out.append(H(U, rect(pb + 2 if sgn > 0 else pa - 6, Y(64), pb + 6 if sgn > 0 else pa - 2, yb), 90, 1.4, 0.6))
        out.append(flag_small(U, (a + b) / 2, Y(68) - 26 * k, 15 * k, 8 * k, seed + 9 + sgn))
    # --- central block ---------------------------------------------------------------------------------------
    a, b = X(-150), X(150)
    out.append(stone_front(U, a, b, Y(70), yb, seed + 11, 14, 3, win_op=0.62))
    out.append(F(rect(a - 1, Y(74), b + 1, Y(70)), PAPER) + H(U, rect(a, Y(70), b, Y(67)), 0, 1.0, 0.6))
    out.append(balustrade(a, b, Y(74), 4 * k, seed + 15, 2.4, 0.6))
    out.append(F(rect(X(-60), Y(76), X(60), yb), PAPER))
    out.append(colonnade(U, X(-56), X(56), Y(70), Y(26), 10, seed + 12, w=0.8, back=0.9))
    out.append(stone_front(U, X(-60), X(60), Y(26), yb, seed + 13, 9, 1, win_op=0.65, pil=False))
    out.append(F(rect(X(-62), Y(78), X(62), Y(70)), PAPER) + H(U, rect(X(-62), Y(72), X(62), Y(70)), 0, 1.0, 0.6)
               + sketch(rect(X(-62), Y(78), X(62), Y(70)), 1.0, seed, 0.3))
    out.append(sketch(rect(X(-60), Y(76), X(60), yb), 1.1, seed + 14, 0.3) + sketch(rect(a, Y(74), b, yb), 1.3, seed + 16, 0.5))
    # shadow cast by the projecting centre on the block to its right
    out.append(H(U, rect(X(60), Y(70), X(70), yb), 90, 1.3, 0.6))
    # --- dome podium ---------------------------------------------------------------------------------------
    pod = rect(X(-74), Y(96), X(74), Y(78))
    out.append(F(pod, PAPER) + window_grid(U, X(-68), X(68), Y(93), Y(81), 12, 1, seed + 18, dark=0.7, sill=False))
    out.append(H(U, rect(X(20), Y(96), X(74), Y(78)), 90, (3.0, 1.6), (0.5, 0.8), dark=(X(74), Y(88))) + sketch(pod, 1.3, seed + 17, 0.5))
    # --- peristyle: drum wall behind 36 columns -----------------------------------------------------------
    R = 62
    pt_, pb_ = Y(154), Y(98)
    drum = rect(X(-R + 3), pt_, X(R - 3), pb_)
    out.append(F(drum, INK, 0.62))
    out.append(H(U, drum, 90, 1.6, 0.8, dark=(X(R), pb_)))
    cols = sorted(math.sin(2 * math.pi * (i + 0.5) / 36) for i in range(36) if math.cos(2 * math.pi * (i + 0.5) / 36) > 0.05)
    shafts, shade = [], []
    for s_ in cols:
        x = X(R * s_)
        cwid = max(1.3, 5.2 * k * math.sqrt(max(0.05, 1 - s_ * s_)) + 0.6)
        c_ = rect(x - cwid / 2, pt_ + 4 * k, x + cwid / 2, pb_ - 3 * k)
        shafts.append(c_)
        # each shaft is shaded on its right; the shade widens toward the right of the drum
        f = 0.25 + 0.5 * (s_ + 1) / 2
        shade.append(rect(x + cwid * (0.5 - f), pt_ + 4 * k, x + cwid / 2, pb_ - 3 * k))
    out.append(F(" ".join(poly(s) for s in shafts), PAPER))
    out.append(H(U, " ".join(poly(s) for s in shade), 90, 1.15, 0.55, box=(X(-R), pt_, X(R), pb_), wob=0, brk=0))
    out.append(segs([((s[0][0], s[0][1]), (s[3][0], s[3][1])) for s in shafts] + [((s[1][0], s[1][1]), (s[2][0], s[2][1])) for s in shafts],
                    0.55, seed, 0))
    out.append(H(U, rect(X(R * 0.55), pt_, X(R), pb_), 0, 2.2, 0.6, op=0.8))
    ent = rect(X(-R - 2), Y(162), X(R + 2), pt_ + 4 * k)
    out.append(F(ent, PAPER) + H(U, rect(X(-R - 2), Y(158), X(R + 2), pt_ + 4 * k), 0, 1.1, 0.6)
               + H(U, rect(X(R * 0.45), Y(162), X(R + 2), pt_ + 4 * k), 90, 1.6, 0.6) + sketch(ent, 1.2, seed + 19, 0.4))
    out.append(balustrade(X(-R + 1), X(R - 1), Y(162), 4 * k, seed + 20, 2.0, 0.6))
    out.append(F(rect(X(-R - 2), pb_ - 3 * k, X(R + 2), pb_), PAPER) + sketch(rect(X(-R - 2), pb_ - 3 * k, X(R + 2), pb_), 1.0, seed, 0.2))
    # --- attic with its tall windows -------------------------------------------------------------------------
    A = 55
    at = rect(X(-A), Y(190), X(A), Y(162))
    out.append(F(at, PAPER))
    wins, pils = [], []
    for i in range(24):
        th = 2 * math.pi * (i + 0.5) / 24
        if math.cos(th) < 0.12:
            continue
        x = X(A * 0.92 * math.sin(th))
        ww = 4.2 * k * math.cos(th)
        wins.append(rect(x - ww / 2, Y(184), x + ww / 2, Y(168)))
        xp = X(A * 0.92 * math.sin(th + math.pi / 24))
        pils.append(((xp, Y(188)), (xp, Y(163))))
    out.append(F(" ".join(poly(w_) for w_ in wins), INK, 0.85) + segs(pils, 0.6, seed, 0))
    out.append(H(U, at, 90, (3.2, 1.4), (0.5, 0.85), dark=(X(A), Y(176)), span=(0.4, 1), wob=0.1, brk=0))
    out.append(sketch(at, 1.3, seed + 21, 0.4))
    cor = rect(X(-A - 3), Y(194), X(A + 3), Y(190))
    out.append(F(cor, PAPER) + H(U, rect(X(-A - 3), Y(191.5), X(A + 3), Y(190)), 0, 0.9, 0.6) + sketch(cor, 1.2, seed + 22, 0.4))
    # --- dome -----------------------------------------------------------------------------------------------
    D, Dh = 50, 58
    y0 = Y(194)

    def dp(ph, t):           # ph: around (-pi/2 .. pi/2 visible), t: elevation 0..1 ; a slight view from below
        r = math.cos(t * math.pi / 2)
        return (X(D * r * math.sin(ph)), y0 - Dh * k * math.sin(t * math.pi / 2) ** 0.95 + 2.2 * k * r * math.cos(ph))
    prof = [dp(-math.pi / 2, i / 20) for i in range(21)]
    dome = prof + [(2 * cx - p[0], p[1]) for p in prof[::-1]]
    # the dome's base line bows down a little (we look slightly up at it)
    base_arc = [dp(-math.pi / 2 + math.pi * i / 20, 0) for i in range(21)]
    dome = prof + [(2 * cx - p[0], p[1]) for p in prof[::-1][1:]] + base_arc[::-1]
    out.append(F(dome, PAPER))
    # rings and ribs
    rings, ribs = [], []
    for t in (0.18, 0.4, 0.62, 0.8):
        rings.append([dp(-math.pi / 2 + math.pi * i / 24, t) for i in range(25)])
    for i in range(1, 16):
        ph = -math.pi / 2 + math.pi * i / 16
        ribs.append([dp(ph, j / 14) for j in range(15)])
    out.append("".join(pen(r, 0.75, seed + i, 0.05, smooth=True, op=0.85) for i, r in enumerate(ribs)))
    out.append("".join(pen(r, 1.0, seed + i, 0.05, smooth=True) for i, r in enumerate(rings)))
    # three tiers of windows between the rings
    tw = []
    for t0, t1, n in ((0.04, 0.15, 16), (0.24, 0.35, 16), (0.46, 0.56, 16)):
        for i in range(n):
            ph = -math.pi / 2 + math.pi * (i + 0.5) / n
            if math.cos(ph) < 0.15:
                continue
            p0, p1 = dp(ph - 0.05, t0), dp(ph + 0.05, t1)
            tw.append(rect(min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])))
    out.append(F(" ".join(poly(w_) for w_ in tw), INK, 0.8))
    # tone: curving hatch heavier toward the right, crossed at the shadow edge
    out.append(H(U, dome, 75, (3.4, 1.6), (0.5, 0.9), dark=(X(D), y0 - 8), span=(0.3, 1), box=bbox(dome), wob=0.3, brk=0))
    out.append(H(U, dome, 15, (3.0, 2.0), 0.6, dark=(X(D), y0), span=(0.66, 1), box=bbox(dome), wob=0.2, brk=0))
    out.append(pen(dome[:41], 1.8, seed + 23, 0.1, smooth=True))
    # --- lantern + Freedom ----------------------------------------------------------------------------------
    L = 12
    lt, lb = Y(270), Y(250)
    out.append(F(rect(X(-L - 4), lb, X(L + 4), lb + 3 * k), PAPER) + sketch(rect(X(-L - 4), lb, X(L + 4), lb + 3 * k), 1.0, seed, 0.3))
    out.append(F(rect(X(-L - 6), lb + 3 * k, X(L + 6), Y(240)), PAPER) + H(U, rect(X(-L - 6), lb + 3 * k, X(L + 6), Y(240)), 90, 1.4, 0.6, span=(0.6, 1), dark=(X(30), lb))
               + sketch(rect(X(-L - 6), lb + 3 * k, X(L + 6), Y(240)), 1.0, seed, 0.3))
    out.append(colonnade(U, X(-L), X(L), lt, lb, 5, seed + 24, w=0.7, back=0.9, cap_h=1.2, base_h=1.0))
    cap = [(X(-L - 2), lt), (X(-L * 0.7), lt - 6 * k), (X(0), lt - 9 * k), (X(L * 0.7), lt - 6 * k), (X(L + 2), lt)]
    out.append(F(cap, PAPER) + H(U, cap, 90, 1.3, 0.6, span=(0.5, 1), dark=(X(L), lt)) + pen(cap, 1.2, seed, 0.05, smooth=True))
    sb = lt - 9 * k
    out.append(F(rect(X(-2.6), sb - 4 * k, X(2.6), sb + 0.5), INK))
    fig = [(X(-2.6), sb - 4 * k), (X(-3.2), sb - 11 * k), (X(-2.0), sb - 17 * k), (X(-1.3), sb - 20 * k), (X(1.5), sb - 20 * k),
           (X(2.2), sb - 16 * k), (X(3.0), sb - 11 * k), (X(2.6), sb - 4 * k)]
    out.append(F(smooth_closed(fig), INK))
    out.append(f'<circle cx="{f1(X(0))}" cy="{f1(sb - 21.8 * k)}" r="{f1(2.0 * k)}" fill="{INK}"/>')
    out.append(F([(X(-1.5), sb - 23 * k), (X(0.2), sb - 28 * k), (X(1.8), sb - 23 * k)], INK))
    out.append(seg(X(3.0), sb - 12 * k, X(4.2), sb - 24 * k, 1.0, seed, 0))
    return "".join(out)


def elm(U, x, base, h, w, seed, light=(-1, -1), lw=1.6, lean=0.0, n=10):
    """An American elm: a tall vase of forking limbs opening into a broad, slightly drooping crown."""
    rnd = random.Random(seed)
    out = []
    top = base - h
    fork = base - h * 0.34
    fx = x + lean * h * 0.08
    out.append(limb([(x, base), (x + lean * h * 0.04, base - h * 0.18), (fx, fork)], max(2.4, w * 0.075), seed, (1, 0.7)))
    for i, u in enumerate((-0.4, -0.18, 0.06, 0.3, 0.44)):
        tx = x + u * w + lean * h * 0.25
        ty = top + h * (0.22 + abs(u) * 0.3)
        mx = fx + u * w * 0.3 + lean * h * 0.1
        out.append(limb([(fx, fork), (mx, base - h * 0.58), (tx, ty)], max(1.5, w * 0.04), seed + i, (1, 0.3)))
    spots = []
    for i in range(n):
        t = i / (n - 1)
        a = math.pi * (1.08 - 1.16 * t)
        sx = x + lean * h * 0.25 + math.cos(a) * w * 0.46
        sy = top + h * 0.3 - math.sin(a) * h * 0.2 + rnd.uniform(-1, 1) * h * 0.03
        spots.append((sx, sy, w * rnd.uniform(0.16, 0.22), h * rnd.uniform(0.11, 0.15)))
    for i in range(max(3, n // 3)):
        spots.append((x + lean * h * 0.25 + rnd.uniform(-0.25, 0.25) * w, top + h * rnd.uniform(0.12, 0.22),
                      w * rnd.uniform(0.17, 0.23), h * rnd.uniform(0.1, 0.13)))
    spots.sort(key=lambda s: -((s[0] - x) * light[0] + (s[1] - top) * light[1]))
    under = smooth_closed(scallop_pts(x + lean * h * 0.25, top + h * 0.28, w * 0.5, h * 0.2, seed + 5, 14, 0.12))
    out.append(F(under, INK, 0.88))
    for i, (sx, sy, a, b) in enumerate(spots):
        out.append(lobe(U, sx, sy, a, b, seed * 31 + i, light=light, w=lw, dense=1.25))
    return "".join(out)


@design("washington-dc")
def washington_dc(U):
    """The Capitol's west front across the Reflecting Pool on a clear morning: the dome mirrored in the water,
    rows of Mall elms receding on both sides toward it, the Grant Memorial at the pool's head, ducks, walkers."""
    art = []
    C = Cam(f=175, cx=300, vpy=261, eye=1.0)
    yw = 322          # far edge of the pool (water line)
    PW = 1.143        # pool half width
    Zf, Zn = 2.87, 1.0
    gid = U("cap")
    # sky
    art.append(cloud(U, 168, 142, 120, 20, 3))
    art.append(cloud(U, 452, 112, 100, 17, 6))
    art.append(cloud(U, 132, 214, 60, 10, 9))
    # the Capitol on its hill: building, terraces, dark belts of trees on the slope, the Grant Memorial
    cap = [capitol(U, 300, 264, 0.64, 11)]
    hill = rect(0, 262, 600, yw)
    cap.append(F(hill, PAPER))
    for sgn in (-1, 1):
        rnd = random.Random(40 + sgn)
        pts = [(300 + sgn * 62, yw)]
        x = 62
        while x < 340:
            pts.append((300 + sgn * x, 270 + rnd.uniform(-7, 5) + (x - 62) * 0.02))
            x += rnd.uniform(9, 16)
        pts += [(300 + sgn * 340, yw)]
        d = scallop_d(pts[1:-1] + [(300 + sgn * 340, yw), (300 + sgn * 62, yw)], 300 + sgn * 200, 300, 0.25, 41 + sgn)
        cap.append(F(d, PAPER) + tone(U, d, 4, 80 if sgn < 0 else 100, box=(0, 250, 600, yw), wob=0.4, brk=0.25))
        for i in range(5):
            xx = 300 + sgn * (78 + i * 34 + rnd.uniform(-5, 5))
            cap.append(lobe(U, xx, 278 + rnd.uniform(-4, 4), 15 + rnd.uniform(-2, 3), 11, 760 + i * 3 + sgn, light=(-1, -1), w=1.0, dense=1.2))
    cap.append(F(rect(256, 264, 344, 300), PAPER))
    cap.append(segs([((262 - i * 1.0, 266 + i * 2.6), (338 + i * 1.0, 266 + i * 2.6)) for i in range(13)], 0.7, 4, 0))
    cap.append(H(U, rect(325, 264, 344, 300), 90, 1.5, 0.6))
    cap.append(balustrade(196, 404, 279, 4.5, 3, 2.8, 0.7) + balustrade(214, 386, 300, 4, 5, 2.6, 0.6))
    cap.append(F(rect(214, 300, 386, yw), PAPER) + strokes_h(214, 386, 304, yw, 6, gap=(2.6, 3.4), ln=(4, 14), w=0.6, op=0.6))
    gm = rect(238, 310, 362, 319)
    cap.append(F(gm, PAPER) + H(U, rect(238, 315, 362, 319), 0, 1.3, 0.6) + sketch(gm, 1.2, 7, 0.4))
    ped = rect(289, 296, 311, 310)
    cap.append(F(ped, PAPER) + H(U, rect(302, 296, 311, 310), 90, 1.3, 0.6) + sketch(ped, 1.1, 8, 0.3))
    horse = [(291, 296), (292, 290), (295, 288), (305, 288), (308, 284), (311, 283), (312, 286), (309, 289), (309, 296), (307, 296),
             (306, 291), (296, 291), (294, 296)]
    cap.append(F(horse, INK) + F(smooth_closed([(298, 288), (301.5, 288), (301.5, 281), (299.8, 279), (298, 281)]), INK))
    cap.append(f'<circle cx="299.8" cy="277.6" r="1.7" fill="{INK}"/>')
    for gx in (252, 348):
        cap.append(F(rect(gx - 11, 305, gx + 11, 310), PAPER) + sketch(rect(gx - 11, 305, gx + 11, 310), 0.9, gx, 0.2))
        cap.append(F(smooth_closed([(gx - 10, 305), (gx - 8, 299), (gx - 3, 296), (gx + 3, 297), (gx + 8, 300), (gx + 10, 305)]), INK, 0.92))
    art.append(f'<g id="{gid}">' + "".join(cap) + "</g>")
    # lawns either side of the pool, receding
    for sgn in (-1, 1):
        lawn = [C(sgn * PW, 0, Zf), C(sgn * 9, 0, Zf), C(sgn * 9, 0, 0.75), C(sgn * PW, 0, 0.75)]
        art.append(F(lawn, PAPER))
        ls = []
        rnd = random.Random(60 + sgn)
        for i in range(140):
            Z = 0.78 + (Zf - 0.78) * rnd.random() ** 1.6
            X = sgn * rnd.uniform(PW + 0.05, 4.0)
            (xa, ya), (xb, yb) = C(X, 0, Z), C(X + sgn * 0.12, 0, Z)
            ls.append(((xa, ya), (xb, yb)))
        art.append(clipped(U("lw"), poly(lawn), segs(ls, 0.6, 61, 0.2, op=0.55)
                           + H(U, lawn, 0, (5, 2.6), 0.55, dark=C(sgn * 2, 0, Zf), op=0.5, wob=0.2, brk=0.3)))
        # gravel walk along the pool
        wk = [C(sgn * (PW + 0.02), 0, Zf), C(sgn * (PW + 0.22), 0, Zf), C(sgn * (PW + 0.22), 0, 0.75), C(sgn * (PW + 0.02), 0, 0.75)]
        art.append(F(wk, PAPER) + pen([wk[1], wk[2]], 0.9, 62, 0.1))
    # the pool
    pool = [C(-PW, 0, Zf), C(PW, 0, Zf), C(PW, 0, Zn), C(-PW, 0, Zn)]
    art.append(F(pool, PAPER))
    art.append(H(U, pool, 0, (3.8, 2.2), 0.55, dark=(300, 436), op=0.55, wob=0.3, brk=0.35))
    art.append(mirror_use(U, gid, yw, k=0.62, op=0.7, clip=poly(pool), seed=12, y1=440, dens=1.2))
    art.append(icf.ripples(U, 90, 510, yw + 2, 436, 13, dens=0.45, gap=(3.0, 9.0), ln=((4, 12), (12, 34)), w=(0.6, 1.2),
                           skip=[(262, 338)], op=0.6, clip=poly(pool)))
    for sgn in (-1, 1):
        art.append(pen([C(sgn * PW, 0, Zf), C(sgn * PW, 0, Zn)], 1.6, 63 + sgn, 0.1))
        art.append(pen([C(sgn * (PW + 0.04), 0.02, Zf), C(sgn * (PW + 0.04), 0.02, Zn)], 0.8, 64 + sgn, 0.1))
    art.append(seg(C(-PW, 0, Zf)[0], yw, C(PW, 0, Zf)[0], yw, 1.6, 14, 0.1))
    art.append(duck(236, 372, 8, 21) + duck(254, 381, 7, 22) + duck(386, 350, 5, 23, flip=True))
    # near coping and plaza
    cop = [C(-PW - 0.06, 0, Zn), C(PW + 0.06, 0, Zn), C(PW + 0.06, -0.06, Zn), C(-PW - 0.06, -0.06, Zn)]
    art.append(F(cop, PAPER) + H(U, cop, 0, 1.4, 0.7) + pen([cop[0], cop[1]], 2.0, 16, 0.1))
    plaza = rect(0, 447, 600, 486)
    art.append(F(plaza, PAPER) + H(U, plaza, 0, (4.6, 2.6), 0.6, dark=(300, 486), op=0.55, wob=0.2, brk=0.25))
    art.append(segs([(C(x, -0.06, Zn), (300 + (C(x, -0.06, Zn)[0] - 300) * 1.4, 486)) for x in (-0.9, -0.45, 0, 0.45, 0.9)], 0.6, 17, 0, op=0.6))
    # elms in rows, far to near
    rows = [3.5, 2.6, 1.9, 1.4, 1.05, 0.8]
    for i, Z in enumerate(rows):
        for sgn in (-1, 1):
            X = sgn * 1.4
            x, yb = C(X, 0, Z)
            h = C.f * 1.7 / Z
            art.append(elm(U, x, yb, h, h * 0.9, 300 + i * 7 + sgn, light=(-1, -1) if sgn > 0 else (1, -1),
                           lw=max(0.9, min(2.0, h / 140)), lean=-sgn * 0.1, n=12 if h > 150 else 8))
    # people on the plaza and the walks
    for X, Z, sd, kind, fl in ((-1.3, 2.2, 1, "plain", False), (-1.28, 1.6, 2, "dress", True), (1.32, 2.0, 3, "plain", True),
                               (1.3, 1.35, 4, "dog", False)):
        x, yb = C(X, 0, Z)
        art.append(walker(x, yb, C.f * 0.11 / Z, 40 + sd, flip=fl, kind=kind))
    art.append(walker(160, 452, 38, 41, kind="dress") + walker(173, 453, 41, 42))
    art.append(walker(193, 449, 23, 43, flip=True))
    # the accent: a red balloon on a string held by the child
    bd = smooth_closed([(200, 396), (193, 388), (194, 378), (201, 374), (208, 378), (209, 388)])
    art.append(F(bd, PAPER) + accent(U, bd, (191, 372, 211, 398), 3, op=1.0, ang=-70, n=12, length=(6, 12), width=(1.5, 2.5))
               + H(U, bd, 60, 1.6, 0.6, span=(0.55, 1), dark=(209, 396)) + P(bd, 1.3)
               + pen([(200, 396), (198, 402), (201, 413), (197, 425), (196, 434)], 0.8, 5, 0.3, smooth=True))
    art.append(walker(418, 451, 38, 44, flip=True, kind="dog"))
    art.append(walker(460, 454, 42, 45, kind="hat"))
    art.append(gull(372, 214, 9, 51) + bird(236, 196, 6, 52) + bird(252, 184, 5, 53) + bird(398, 168, 5, 54))
    return plate(U, "washington-dc", art, 5, cy=250)


# ================================================================ NEW ORLEANS
def uvd(m, pts):
    """Path data for points given in a quad's unit square (u along, v down), mapped through homography m."""
    q = [m(u, v) for u, v in pts]
    return "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in q)


def lace(U, q, n, seed, w=0.7, op=1.0, rails=True):
    """Cast-iron lace railing on a perspective quad [TL, TR, BR, BL]: top and bottom rails, balusters and a
    repeating motif of rings and C-scrolls in every bay."""
    m = homog(q)
    px = math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]) / max(1, n)
    d = []
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        uc, du = (u0 + u1) / 2, (u1 - u0)
        d.append(uvd(m, [(u0, 0.0), (u0, 1.0)]))
        if px > 5:
            ring = [(uc + du * 0.2 * math.cos(a), 0.5 + 0.17 * math.sin(a)) for a in [j * math.pi / 8 for j in range(17)]]
            d.append(uvd(m, ring))
            for sg in (-1, 1):
                sc = [(uc + sg * du * (0.2 + 0.24 * math.sin(a)), 0.12 + 0.19 * (1 - math.cos(a))) for a in [j * math.pi / 10 for j in range(11)]]
                d.append(uvd(m, sc))
        if px > 9:
            d.append(uvd(m, [(uc, 0.0), (uc, 0.22)]) + " " + uvd(m, [(uc, 0.74), (uc, 1.0)]))
            for sg in (-1, 1):
                d.append(uvd(m, [(uc + sg * du * 0.5 * math.cos(a) * 0.5, 0.86 + 0.1 * math.sin(a)) for a in [j * math.pi / 6 for j in range(7)]]))
        elif px <= 5:
            d.append(uvd(m, [(uc, 0.0), (uc, 1.0)]))
    out = [P(" ".join(d), w, INK, op)]
    if rails:
        out.append(pen([q[0], q[1]], w * 2.2, seed, 0.05) + pen([q[3], q[2]], w * 1.6, seed + 1, 0.05))
    return "".join(out)


def bracket_frieze(m, n, w=0.7):
    """Arched lace brackets between gallery posts (along the top of a gallery level)."""
    d = []
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        arc = [(lerp(u0, u1, t), 0.15 + 0.85 * (1 - math.sin(t * math.pi)) ** 1.6) for t in [j / 12 for j in range(13)]]
        d.append(uvd(m, arc))
        d.append(uvd(m, [(u0, 0.0), (u1, 0.0)]))
    return P(" ".join(d), w)


def louvered(U, q, seed, dark=False, w=0.7, slats=None):
    """A louvered shutter / door leaf on a perspective quad."""
    m = homog(q)
    hgt = abs(q[3][1] - q[0][1])
    n = slats or max(3, int(hgt / 2.6))
    out = [F(q, INK if dark else PAPER, 0.85 if dark else 1.0)]
    d = [uvd(m, [(0.12, 0.06 + 0.88 * j / n), (0.88, 0.06 + 0.88 * j / n + 0.02)]) for j in range(n + 1)]
    out.append(P(" ".join(d), w, PAPER if dark else INK, 0.8))
    out.append(sketch(q, w * 1.4, seed, 0.2))
    return "".join(out)


def gallery_block(U, C, X, Xc, Z0, Z1, seed, levels=(4.2, 8.2), top=12.0, bay=2.6, shade=3, shutters_accent=False,
                  ferns=True):
    """A Creole/Spanish townhouse on the plane X with deep cast-iron galleries out to the curb line Xc on every upper
    level: dark shaded wall with tall French doors, posts, lace railings, bracket friezes, hanging ferns, a hipped
    gallery roof. Built for the right-hand side of a street (X > 0)."""
    rnd = random.Random(seed)
    out = []
    wall = C.qx(X, Z0, Z1, 0, top)
    out.append(F(wall, PAPER))
    out.append(tone(U, wall, 2, 75, box=bbox(wall), wob=0.2, brk=0.05))
    gq = C.qx(X - 0.01, Z0, Z1, 0, levels[0])
    out.append(H(U, gq, 15, 3.0, 0.7, box=bbox(gq), wob=0.2, brk=0.05))
    # floors of French doors with shutters folded back
    z = Z0 + 0.5
    doors = []
    while z + 1.6 < Z1:
        for y0, y1 in ((0.2, 3.4), (levels[0] + 0.35, levels[0] + 3.2), (levels[1] + 0.35, levels[1] + 3.1)):
            dq = C.qx(X, z + 0.5, z + 1.6, y0, y1)
            doors.append(dq)
            w_ = abs(dq[1][0] - dq[0][0])
            if w_ > 3:
                for za, zb in ((z + 0.1, z + 0.5), (z + 1.6, z + 2.0)):
                    sq = C.qx(X - 0.02, za, zb, y0, y1)
                    if y0 < 1 and shutters_accent and 7.5 < z < 13:
                        out.append(F(sq, PAPER) + accent(U, poly(sq), bbox(sq), seed + int(z * 10), op=1.0, ang=-90, n=10,
                                                         length=(6, 14), width=(1.2, 2.4)) + louvered(U, sq, seed, w=0.55)[len(F(sq, PAPER)):])
                    else:
                        out.append(louvered(U, sq, seed + int(z * 10), w=0.55))
        z += bay
    out.append(F(" ".join(poly(d) for d in doors), INK, 0.9))
    out.append(segs([(pt(d[0], d[1], 0.5), pt(d[3], d[2], 0.5)) for d in doors if abs(d[1][0] - d[0][0]) > 4], 0.7, seed, 0, color=PAPER, op=0.7))
    # galleries
    for li, yl in enumerate(levels):
        slab = [C(X, yl, Z0), C(X, yl, Z1), C(Xc, yl, Z1), C(Xc, yl, Z0)]
        out.append(F(slab, INK, 0.9))
        fas = C.qx(Xc, Z0, Z1, yl - 0.25, yl + 0.05)
        out.append(F(fas, PAPER) + pen([fas[0], fas[1]], 1.1, seed, 0.05) + pen([fas[3], fas[2]], 1.1, seed + 1, 0.05))
        rq = C.qx(Xc, Z0, Z1, yl + 0.05, yl + 1.1)
        nb = max(4, int((Z1 - Z0) / 0.36))
        out.append(F(rq, PAPER, 0.82) + lace(U, rq, nb, seed + li, w=0.7))
        # bracket frieze at the top of this level
        yt = levels[li + 1] - 0.25 if li + 1 < len(levels) else top - 0.6
        fq = C.qx(Xc, Z0, Z1, yt - 0.7, yt)
        out.append(bracket_frieze(homog(fq), max(2, int((Z1 - Z0) / 1.3)), 0.7))
    # ground floor: the walk under the first gallery is in shadow
    # posts on the curb line
    posts = []
    zp = Z0 + 0.15
    while zp <= Z1 + 0.01:
        a, b = C(Xc, 0, zp), C(Xc, top - 0.6, zp)
        posts.append((a, b))
        zp += bay * 0.5 if (Z1 - Z0) < 6 else bay
    for a, b in posts:
        wpx = max(1.0, min(3.6, 260 * 0.12 / max(1, (C.f and 1) * 1) / max(1.0, (a[1] - C.vpy) and 1)))
        out.append(seg(a[0], a[1], b[0], b[1], max(1.0, min(3.4, (a[1] - C.vpy) * 0.035)), seed, 0))
    # roof
    rf = [C(X, top + 0.8, Z0), C(X, top + 0.8, Z1), C(Xc - 0.15, top - 0.6, Z1), C(Xc - 0.15, top - 0.6, Z0)]
    out.append(F(rf, PAPER) + H(U, rf, 0, 2.0, 0.7, op=0.8) + segs([(C(X, top + 0.8, z_), C(Xc - 0.15, top - 0.6, z_)) for z_ in
                                                                 [Z0 + i * 0.5 for i in range(int((Z1 - Z0) / 0.5) + 1)]], 0.6, seed, 0, op=0.7))
    out.append(pen([rf[3], rf[2]], 1.6, seed, 0.05))
    # parapet / wall above the gallery roof
    par = C.qx(X, Z0, Z1, top + 0.8, top + 2.2)
    out.append(F(par, PAPER) + H(U, par, 0, 2.2, 0.6) + sketch(par, 1.2, seed, 0.3))
    # hanging ferns
    if ferns:
        for li, yl in enumerate(levels):
            zf = Z0 + 1.0 + rnd.uniform(0, 0.6)
            while zf < Z1 - 0.5:
                cx_, cy_ = C(Xc + 0.25, yl + 2.0 - li * 0.0, zf)
                r = 260 * 0.34 / max(zf, 1)
                a = C(Xc + 0.25, levels[li + 1] - 0.3 if li + 1 < len(levels) else top - 0.6, zf)
                out.append(seg(a[0], a[1], cx_, cy_ - r * 0.5, 0.6, seed, 0))
                out.append(fern_ball(U, cx_, cy_, r, seed + int(zf * 7)))
                zf += bay * rnd.choice((1, 2))
    out.append(pen([C(X, 0, Z1), C(X, top, Z1)], 1.6, seed, 0.1))
    return "".join(out)


def fern_ball(U, cx, cy, r, seed):
    """A hanging basket of Boston fern: a dark pot and a fountain of drooping fronds."""
    rnd = random.Random(seed)
    out = []
    fr = []
    for i in range(int(12 + r * 1.2)):
        a = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
        L = r * rnd.uniform(0.9, 1.7)
        sx, sy = cx + math.cos(a) * r * 0.25, cy - r * 0.1
        ex, ey = cx + math.cos(a) * L * 0.8, cy + L * rnd.uniform(0.3, 0.9)
        fr.append(f"M {f1(sx)} {f1(sy)} Q {f1(sx + math.cos(a) * L * 0.6)} {f1(sy + math.sin(a) * L * 0.5)} {f1(ex)} {f1(ey)}")
    out.append(P(" ".join(fr), max(0.7, r * 0.11), INK, 0.9))
    out.append(F([(cx - r * 0.3, cy - r * 0.2), (cx + r * 0.3, cy - r * 0.2), (cx + r * 0.22, cy + r * 0.2), (cx - r * 0.22, cy + r * 0.2)], INK))
    return "".join(out)


def creole_front(U, C, X, Z0, Z1, top, seed, balcony=(4.3, 8.3), bay=2.4, plaster=True, gallery=False):
    """A lit Creole townhouse front on the left of the street (X < 0): stucco coursing, tall shuttered openings,
    narrow lace balconies, a cornice or dentil parapet."""
    rnd = random.Random(seed)
    sg = 1                               # toward the street (+X) for the left side
    out = []
    wall = C.qx(X, Z0, Z1, 0, top)
    out.append(F(wall, PAPER))
    if plaster:
        cl = [(C(X, y, Z0), C(X, y, Z1)) for y in [0.45 * i for i in range(1, int(top / 0.45))]]
        out.append(segs(cl, 0.45, seed, 0, op=0.35))
    out.append(H(U, wall, 80, 3.6, 0.55, op=0.45, wob=0.2, brk=0.2))
    z = Z0 + 0.45
    doors = []
    while z + 1.5 < Z1:
        for y0, y1 in [(0.2, 3.3)] + [(b + 0.3, b + 3.0) for b in balcony if b + 3 < top]:
            dq = C.qx(X, z + 0.45, z + 1.45, y0, y1)
            doors.append(dq)
            for za, zb in ((z + 0.07, z + 0.45), (z + 1.45, z + 1.83)):
                sq = C.qx(X + 0.02, za, zb, y0, y1)
                if abs(sq[1][0] - sq[0][0]) > 1.6:
                    out.append(louvered(U, sq, seed + int(z * 13 + y0), w=0.5))
                else:
                    out.append(F(sq, INK, 0.5))
            lin = C.qx(X + 0.03, z + 0.35, z + 1.55, y1 + 0.1, y1 + 0.4)
            out.append(F(lin, PAPER) + sketch(lin, 0.7, seed, 0.1))
        z += bay
    out.append(F(" ".join(poly(d) for d in doors), INK, 0.88))
    for b in balcony:
        if b + 3 >= top:
            continue
        slab = [C(X, b, Z0), C(X, b, Z1), C(X + sg * 0.9, b, Z1), C(X + sg * 0.9, b, Z0)]
        out.append(F(slab, INK, 0.85))
        rq = C.qx(X + sg * 0.9, Z0, Z1, b + 0.05, b + 1.05)
        out.append(F(rq, PAPER, 0.7) + lace(U, rq, max(4, int((Z1 - Z0) / 0.3)), seed + int(b), w=0.6))
        # brackets under the balcony
        br = []
        zb = Z0 + 0.4
        while zb < Z1:
            br.append((C(X, b - 0.6, zb), C(X + sg * 0.9, b, zb)))
            zb += 1.2
        out.append(segs(br, 0.8, seed, 0))
        # shadow cast on the wall under the balcony
        sh = C.qx(X + 0.01, Z0, Z1, b - 1.1, b)
        out.append(H(U, sh, 90, 1.7, 0.7, op=0.9))
    cor = C.qx(X, Z0, Z1, top - 0.6, top)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.4, 0.6) + sketch(cor, 1.0, seed, 0.2))
    den = []
    zd = Z0 + 0.1
    while zd < Z1:
        den.append((C(X + 0.05, top - 0.6, zd), C(X + 0.05, top - 0.3, zd)))
        zd += 0.3
    out.append(segs(den, 0.6, seed, 0))
    out.append(pen([C(X, 0, Z0), C(X, top, Z0)], 1.3, seed, 0.1) + pen([C(X, top, Z0), C(X, top, Z1)], 1.6, seed + 1, 0.1))
    return "".join(out)


def cathedral_nola(U, cx, yb, s, seed=1):
    """St. Louis Cathedral's three spires seen from up the street (elevation, s px per metre): the tall central
    tower with clock and belfry under a slender hexagonal spire, two shorter flanking spires, the roof between."""
    out = []

    def Y(m):
        return yb - m * s

    def X(m):
        return cx + m * s
    # roof mass between the towers
    body = rect(X(-15), Y(18), X(15), yb)
    out.append(F(body, PAPER) + H(U, rect(X(-15), Y(18), X(-5), yb), 90, 1.8, 0.6) + sketch(body, 1.1, seed, 0.4))
    gab = [(X(-6), Y(18)), (X(0), Y(24)), (X(6), Y(18))]
    out.append(F(gab, PAPER) + pen(gab, 1.2, seed, 0.1) + H(U, [(X(0), Y(24)), (X(6), Y(18)), (X(0), Y(18))], 90, 1.6, 0.6))
    for sg, hh in ((-1, 30), (1, 30)):
        tx = X(sg * 12.5)
        tw = rect(tx - 3 * s, Y(19), tx + 3 * s, yb)
        out.append(F(tw, PAPER) + sketch(tw, 1.1, seed + sg, 0.3))
        out.append(F(rect(tx - 1.2 * s, Y(17), tx + 1.2 * s, Y(13)), INK, 0.85))
        out.append(H(U, rect(tx - 3 * s, Y(19), tx - 0.6 * s, yb), 90, 1.5 if sg < 0 else 2.4, 0.6))
        bel = rect(tx - 2.3 * s, Y(23), tx + 2.3 * s, Y(19))
        out.append(F(bel, PAPER) + F(rect(tx - 1.0 * s, Y(22.5), tx + 1.0 * s, Y(19.6)), INK, 0.85) + sketch(bel, 1.0, seed, 0.2))
        sp = [(tx - 2.3 * s, Y(23)), (tx, Y(hh + 3)), (tx + 2.3 * s, Y(23))]
        out.append(F(sp, PAPER) + H(U, [(tx, Y(hh + 3)), (tx - 2.3 * s, Y(23)), (tx - 0.5 * s, Y(23))], 90, 1.3, 0.6)
                   + pen(sp, 1.3, seed + 3, 0.05) + seg(tx, Y(23), tx + 0.3 * s, Y(hh + 3), 0.6, seed, 0))
        out.append(seg(tx, Y(hh + 3), tx, Y(hh + 5.5), 1.0, seed, 0) + seg(tx - 0.6 * s, Y(hh + 4.6), tx + 0.6 * s, Y(hh + 4.6), 0.9, seed, 0))
    # central tower: base, clock stage, belfry, spire
    t = rect(X(-4.2), Y(22), X(4.2), yb)
    out.append(F(t, PAPER) + H(U, rect(X(-4.2), Y(22), X(-1.6), yb), 90, 1.5, 0.6) + H(U, t, 0, 3.4, 0.5, op=0.6) + sketch(t, 1.2, seed + 5, 0.3))
    ck = rect(X(-3.6), Y(28), X(3.6), Y(22))
    out.append(F(ck, PAPER) + sketch(ck, 1.1, seed + 6, 0.2))
    out.append(f'<circle cx="{f1(X(0))}" cy="{f1(Y(25))}" r="{f1(2.2 * s)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>'
               + P(f"M {f1(X(0))} {f1(Y(25))} L {f1(X(0))} {f1(Y(26.6))} M {f1(X(0))} {f1(Y(25))} L {f1(X(1.1))} {f1(Y(25))}", 0.9))
    bf = rect(X(-3.1), Y(34), X(3.1), Y(28))
    out.append(F(bf, PAPER) + sketch(bf, 1.1, seed + 7, 0.2) + F(rect(X(-1.7), Y(33.2), X(-0.3), Y(28.8)), INK, 0.85)
               + F(rect(X(0.3), Y(33.2), X(1.7), Y(28.8)), INK, 0.85) + H(U, rect(X(-3.1), Y(34), X(-1.9), Y(28)), 90, 1.3, 0.6))
    out.append(F(rect(X(-3.6), Y(34.8), X(3.6), Y(34)), INK, 0.9))
    sp = [(X(-3.1), Y(34.8)), (X(0), Y(52)), (X(3.1), Y(34.8))]
    out.append(F(sp, PAPER) + H(U, [(X(0), Y(52)), (X(-3.1), Y(34.8)), (X(-0.7), Y(34.8))], 90, 1.3, 0.7)
               + segs([(pt((X(-3.1), Y(34.8)), (X(0), Y(52)), t_), pt((X(3.1), Y(34.8)), (X(0), Y(52)), t_)) for t_ in (0.2, 0.4, 0.6)], 0.6, seed, 0)
               + pen(sp, 1.5, seed + 8, 0.05) + seg(X(0), Y(34.8), X(0.4), Y(52), 0.7, seed, 0))
    out.append(seg(X(0), Y(52), X(0), Y(56), 1.2, seed, 0) + seg(X(-0.9), Y(54.6), X(0.9), Y(54.6), 1.1, seed, 0))
    return "".join(out)


def trumpeter(x, y, h, seed=1, flip=False):
    """A street musician in a hat playing a trumpet, bell raised."""
    s = -1 if flip else 1
    out = [person(x, y, h, seed, flip=flip)]
    out.append(F(smooth_closed([(x - h * 0.15, y - h * 0.97), (x + h * 0.15, y - h * 0.97), (x + h * 0.08, y - h * 1.0), (x - h * 0.08, y - h * 1.0)]), INK))
    out.append(F(rect(x - h * 0.07, y - h * 1.07, x + h * 0.07, y - h * 0.97), INK))
    mx, my = x + s * h * 0.08, y - h * 0.88
    bx, by = x + s * h * 0.42, y - h * 0.98
    out.append(P(f"M {f1(mx)} {f1(my)} L {f1(bx)} {f1(by)}", max(1.0, h * 0.035)))
    out.append(F([(bx, by), (bx + s * h * 0.08, by - h * 0.07), (bx + s * h * 0.09, by + h * 0.04)], INK))
    out.append(P(f"M {f1(x + s * h * 0.1)} {f1(y - h * 0.72)} L {f1(x + s * h * 0.24)} {f1(y - h * 0.86)}", h * 0.06))
    return "".join(out)


def wall_lantern(x, y, s, seed=1, flip=False):
    """A New Orleans gas lantern on a scrolled wall bracket."""
    k = -1 if flip else 1
    out = [P(f"M {f1(x)} {f1(y - s * 0.2)} Q {f1(x + k * s * 0.6)} {f1(y - s * 0.45)} {f1(x + k * s * 0.9)} {f1(y - s * 0.2)} "
             f"M {f1(x)} {f1(y + s * 0.15)} Q {f1(x + k * s * 0.4)} {f1(y)} {f1(x + k * s * 0.55)} {f1(y - s * 0.32)}", max(0.9, s * 0.07))]
    lx = x + k * s * 0.9
    lt = [(lx - s * 0.18, y - s * 0.1), (lx + s * 0.18, y - s * 0.1), (lx + s * 0.24, y + s * 0.4), (lx - s * 0.24, y + s * 0.4)]
    out.append(F(lt, PAPER) + pen(lt, max(0.8, s * 0.06), seed, 0.05, True))
    out.append(F([(lx - s * 0.26, y - s * 0.1), (lx, y - s * 0.3), (lx + s * 0.26, y - s * 0.1)], INK))
    out.append(F([(lx - s * 0.28, y + s * 0.4), (lx + s * 0.28, y + s * 0.4), (lx, y + s * 0.52)], INK))
    out.append(seg(lx, y - s * 0.08, lx, y + s * 0.38, max(0.6, s * 0.04), seed, 0))
    return "".join(out)


@design("new-orleans")
def new_orleans(U):
    """Orleans Street in the French Quarter, late afternoon: deep cast-iron galleries hung with ferns on the shaded
    right, lit balconied townhouses on the left, gas lanterns, a trumpeter on the banquette, and the cathedral's
    three spires rising over St. Anthony's Garden at the end of the street."""
    art = []
    C = Cam(f=260, cx=236, vpy=330, eye=1.6)
    # sky + cloud
    art.append(cloud(U, 360, 92, 110, 18, 12))
    art.append(cloud(U, 118, 170, 70, 11, 14))
    # the cathedral beyond the end of the street, with the garden's trees
    yb = C(0, 0, 62)[1]
    art.append(cathedral_nola(U, 238, yb - 2, 4.3, 21))
    for i, x in enumerate(range(200, 284, 11)):
        art.append(lobe(U, x, yb - 22 - (i % 3) * 6, 13, 12, 900 + i, light=(1, -1), w=1.0, dense=1.3))
    for i, x in enumerate(range(206, 280, 14)):
        art.append(lobe(U, x, yb - 9, 11, 9, 950 + i, light=(1, -1), w=1.0, dense=1.4))
    art.append(seg(180, yb, 300, yb, 1.2, 3, 0))
    # street and banquettes
    road = [C(-4.2, 0, 4), C(-4.2, 0, 60), C(4.0, 0, 60), C(4.0, 0, 4)]
    art.append(F(road, PAPER) + H(U, road, 0, (4.0, 2.6), 0.6, dark=(300, 560), op=0.55, wob=0.3, brk=0.3))
    art.append(H(U, [C(1.5, 0, 4), C(1.5, 0, 60), C(4.0, 0, 60), C(4.0, 0, 4)], 80, 3.0, 0.6, op=0.5))
    for sx, x0, x1 in ((-1, -5.6, -4.2), (1, 4.0, 5.6)):
        walk = [C(x0, 0.15, 4), C(x0, 0.15, 60), C(x1, 0.15, 60), C(x1, 0.15, 4)]
        art.append(F(walk, PAPER))
        art.append(segs([(C(x0, 0.15, z), C(x1, 0.15, z)) for z in [4 + i * 0.9 for i in range(62)]], 0.55, 5, 0, op=0.55))
        cx_ = -4.2 if sx < 0 else 4.0
        art.append(pen([C(cx_, 0.15, 4), C(cx_, 0.15, 60)], 1.5, 6, 0.1) + pen([C(cx_, 0, 4), C(cx_, 0, 60)], 0.9, 7, 0.1))
    art.append(H(U, [C(4.0, 0.15, 4), C(4.0, 0.15, 60), C(5.6, 0.15, 60), C(5.6, 0.15, 4)], 70, 2.6, 0.7, op=0.8))
    # left side: lit townhouses of varied height, receding
    zs = [(52, 60, 9.5, False), (42, 52, 12.5, True), (33, 42, 10.0, True), (24, 33, 13.0, True), (15, 24, 11.0, True), (6, 15, 13.5, True)]
    for i, (z0, z1, top, bal) in enumerate(zs):
        art.append(creole_front(U, C, -5.6, z0, z1, top, 60 + i, balcony=(4.3, 8.3) if bal else (4.3,), bay=2.6))
    # right side: galleried buildings, far to near
    gs = [(46, 60, 11.0, False), (32, 46, 12.0, False), (19, 32, 12.5, False), (4.2, 19, 12.5, True)]
    for i, (z0, z1, top, acc) in enumerate(gs):
        art.append(gallery_block(U, C, 5.6, 4.1, z0, z1, 80 + i, levels=(4.2, 8.2), top=top, bay=2.7, shade=3,
                                 shutters_accent=acc, ferns=True))
    # gas lanterns on the left walls and on the gallery posts
    for z in (12, 22, 36):
        x, y = C(-5.6, 3.6, z)
        art.append(wall_lantern(x, y, 260 * 0.9 / z, 30 + z))
    for z in (9.6, 24):
        x, y = C(4.1, 3.4, z)
        art.append(wall_lantern(x, y, 260 * 0.9 / z, 40 + int(z), flip=True))
    # people: trumpeter under the gallery, strollers, a couple crossing, a cyclist
    x, y = C(4.9, 0.15, 7.2)
    art.append(trumpeter(x, y, 260 * 1.75 / 7.2, 51, flip=True))
    for X, Z, sd, kind, fl in ((-4.8, 9.5, 52, "dress", False), (-5.0, 18, 53, "plain", True), (-4.9, 27, 54, "bag", False),
                               (4.7, 14, 55, "hat", True), (4.6, 22, 56, "plain", False), (-1.0, 20, 57, "dress", True),
                               (-0.6, 20.4, 58, "plain", True), (4.8, 34, 59, "plain", True), (-4.9, 40, 60, "plain", False)):
        x, y = C(X, 0.15 if abs(X) > 4 else 0, Z)
        art.append(walker(x, y, 260 * 1.7 / Z, sd, flip=fl, kind=kind))
    x, y = C(1.8, 0, 30)
    art.append(cyclist(x, y, 260 * 1.75 / 30, 61))
    art.append(bird(176, 120, 6, 62) + bird(190, 108, 4.5, 63) + bird(312, 182, 5, 64))
    return plate(U, "new-orleans", art, 15)


# ================================================================ SAN FRANCISCO
SF_KNOTS = [(-60, 15.6), (20, -5.2), (27, -5.2), (52, -11.7), (59, -11.7), (92, -20.3), (99, -20.3), (170, -35.0), (3000, -35.0)]


def sf_ground(Z):
    for (z0, y0), (z1, y1) in zip(SF_KNOTS, SF_KNOTS[1:]):
        if z0 <= Z <= z1:
            return lerp(y0, y1, (Z - z0) / (z1 - z0))
    return SF_KNOTS[-1][1]


def vic3d(U, C, X, Z0, Z1, ht, seed, shade=0, gable=True, bay=True):
    """A Victorian row house on the plane X (left side if X < 0) of a street that falls away with Z: level floors
    stepping down the hill over a plinth and garage, a three-sided bay on two floors, clapboard, bracketed cornice,
    and either a fish-scale gable or a flat false front."""
    rnd = random.Random(seed)
    sg = 1 if X < 0 else -1                # toward the street
    yb = sf_ground(Z0)
    yl = sf_ground(Z1)
    out = []
    wall = C.qx(X, Z0, Z1, yb, yb + ht)
    out.append(F(wall, PAPER))
    out.append(segs([(C(X, yb + y, Z0), C(X, yb + y, Z1)) for y in [0.32 * i for i in range(1, int(ht / 0.32))]], 0.45, seed, 0, op=0.5))
    # plinth below the floor at the downhill end
    if yb - yl > 0.05:
        pl = [C(X, yb, Z0), C(X, yb, Z1), C(X, yl, Z1), C(X, yb, Z0)]
        out.append(F(pl, PAPER) + H(U, pl, 0, 1.8, 0.7) + pen([pl[0], pl[1], pl[2]], 1.0, seed, 0.1))
    W = Z1 - Z0
    # garage + entry stair on the ground floor
    gq = C.qx(X, Z0 + W * 0.52, Z0 + W * 0.9, yl, yb + 2.4)
    out.append(F(gq, INK, 0.85))
    out.append(segs([(pt(gq[0], gq[3], t), pt(gq[1], gq[2], t)) for t in (0.2, 0.4, 0.6, 0.8)], 0.6, seed, 0, color=PAPER, op=0.5))
    dq = C.qx(X, Z0 + W * 0.12, Z0 + W * 0.3, yb + 0.2, yb + 2.6)
    out.append(F(dq, INK, 0.9))
    hood = C.qx(X + sg * 0.1, Z0 + W * 0.08, Z0 + W * 0.34, yb + 2.6, yb + 3.0)
    out.append(F(hood, PAPER) + sketch(hood, 0.8, seed, 0.1))
    # windows on the flat part (2 floors)
    wins = []
    for y0, y1 in ((3.4, 5.4), (6.4, 8.4)):
        if y1 + 0.5 < ht:
            wins.append(C.qx(X, Z0 + W * 0.12, Z0 + W * 0.3, yb + y0, yb + y1))
    out.append(F(" ".join(poly(w_) for w_ in wins), INK, 0.85) + "".join(
        seg(*pt(w_[0], w_[1], 0) , *pt(w_[0], w_[1], 1), 1.2, seed, 0) for w_ in wins))
    # three-sided bay: plan points along Z, projecting d toward the street
    if bay:
        za, zb, d = Z0 + W * 0.42, Z0 + W * 0.95, 0.75
        plan = [(X, za), (X + sg * d, za + d), (X + sg * d, zb - d), (X, zb)]
        for (xa, z_a), (xb_, z_b) in ((plan[0], plan[1]), (plan[1], plan[2])):
            for y0, y1 in ((2.9, 5.9), (5.9, 8.9)):
                if y1 > ht:
                    continue
                q = [C(xa, yb + y1, z_a), C(xb_, yb + y1, z_b), C(xb_, yb + y0, z_b), C(xa, yb + y0, z_a)]
                out.append(F(q, PAPER))
                m = homog(q)
                win = [m(0.14, 0.14), m(0.86, 0.14), m(0.86, 0.8), m(0.14, 0.8)]
                out.append(F(win, INK, 0.86) + seg(*m(0.5, 0.14), *m(0.5, 0.8), 0.7, seed, 0, color=PAPER))
                if (xa, z_a) == plan[0]:
                    out.append(H(U, q, 90, 1.6, 0.6, op=0.7))
                out.append(sketch(q, 0.9, seed + int(y0), 0.2))
        top_ = [C(plan[0][0], yb + 8.9, plan[0][1]), C(plan[1][0], yb + 8.9, plan[1][1]), C(plan[2][0], yb + 8.9, plan[2][1]),
                C(plan[3][0], yb + 8.9, plan[3][1])]
        out.append(pen(top_, 1.3, seed, 0.05))
    # cornice with brackets
    cor = C.qx(X + sg * 0.35, Z0, Z1, yb + ht - 0.5, yb + ht)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.2, 0.6) + sketch(cor, 1.1, seed, 0.2))
    br = [(C(X + sg * 0.3, yb + ht - 0.5, z), C(X + sg * 0.3, yb + ht - 0.9, z)) for z in [Z0 + W * (i + 0.5) / 7 for i in range(7)]]
    out.append(segs(br, 1.4, seed, 0))
    if gable:
        apex = C(X, yb + ht + W * 0.42, (Z0 + Z1) / 2)
        g = [C(X, yb + ht, Z0), apex, C(X, yb + ht, Z1)]
        out.append(F(g, PAPER))
        sc = []
        for j in range(1, 7):
            y_ = yb + ht + j * W * 0.06
            k_ = 1 - j / 7.2
            a_ = C(X, y_, (Z0 + Z1) / 2 - W / 2 * k_)
            b_ = C(X, y_, (Z0 + Z1) / 2 + W / 2 * k_)
            n_ = max(2, int(abs(b_[0] - a_[0]) / 3.2))
            dd = []
            for i in range(n_):
                p0, p1 = pt(a_, b_, i / n_), pt(a_, b_, (i + 1) / n_)
                dd.append(f"M {f1(p0[0])} {f1(p0[1])} Q {f1((p0[0] + p1[0]) / 2)} {f1((p0[1] + p1[1]) / 2 + 2.2)} {f1(p1[0])} {f1(p1[1])}")
            sc.append(" ".join(dd))
        out.append(P(" ".join(sc), 0.55, INK, 0.75))
        out.append(pen([C(X, yb + ht, Z0 - 0.3), apex, C(X, yb + ht, Z1 + 0.3)], 1.7, seed, 0.05))
        gw = C.qx(X, (Z0 + Z1) / 2 - W * 0.08, (Z0 + Z1) / 2 + W * 0.08, yb + ht + W * 0.08, yb + ht + W * 0.22)
        out.append(F(gw, INK, 0.85))
    else:
        fp = C.qx(X, Z0, Z1, yb + ht, yb + ht + 1.2)
        out.append(F(fp, PAPER) + segs([(C(X, yb + ht + 0.15, z), C(X, yb + ht + 1.05, z)) for z in [Z0 + W * (i + 0.5) / 8 for i in range(8)]], 0.6, seed, 0)
                   + sketch(fp, 1.1, seed, 0.2) + pen([C(X + sg * 0.3, yb + ht + 1.2, Z0), C(X + sg * 0.3, yb + ht + 1.2, Z1)], 1.6, seed, 0.05))
    if shade:
        out.append(tone(U, wall + [], shade, 75, box=bbox(wall), op=0.85))
    out.append(pen([C(X, yb, Z0), C(X, yb + ht, Z0)], 1.4, seed, 0.1) + pen([C(X, yl, Z1), C(X, yb + ht, Z1)], 1.6, seed + 1, 0.1))
    return "".join(out)


def cable_car_front(U, C, X, Z, seed, L=8.4, Wd=2.5, Hh=3.3):
    """A cable car climbing toward us: front end with the open grip section, roof with a blank route sign and
    headlamp, the inner side with riders on the running board; lower panels in the vermilion accent. Its floor
    follows the grade."""
    g0, g1 = sf_ground(Z), sf_ground(Z + L)
    x0, x1 = X - Wd / 2, X + Wd / 2
    s = C.f / C.depth(X, Z)
    out = []
    # inner side face (x1 plane), visible because the car runs left of the centre line
    side = [C(x1, g0 + Hh, Z), C(x1, g1 + Hh, Z + L), C(x1, g1 + 0.35, Z + L), C(x1, g0 + 0.35, Z)]
    out.append(F(side, PAPER))
    m = homog(side)
    sw = [[m(u + 0.01, 0.12), m(u + 0.07, 0.12), m(u + 0.07, 0.45), m(u + 0.01, 0.45)] for u in [0.4 + 0.1 * i for i in range(6)]]
    out.append(F(" ".join(poly(w) for w in sw), INK, 0.85))
    low = [m(0, 0.62), m(1, 0.62), m(1, 1), m(0, 1)]
    out.append(accent(U, poly(low), bbox(low), seed, op=1.0, ang=0, n=14, length=(6, 16), width=(1.2, 2.4)))
    out.append(H(U, low, 0, 1.6, 0.6, op=0.7) + sketch(side, 1.2, seed, 0.2))
    # front end
    fr = [C(x0, g0 + Hh, Z), C(x1, g0 + Hh, Z), C(x1, g0 + 0.35, Z), C(x0, g0 + 0.35, Z)]
    out.append(F(fr, PAPER))
    fm = homog(fr)
    dash = [fm(0, 0.6), fm(1, 0.6), fm(1, 1), fm(0, 1)]
    out.append(accent(U, poly(dash), bbox(dash), seed + 1, op=1.0, ang=-90, n=14, length=(6, 14), width=(1.2, 2.4)))
    out.append(H(U, dash, 0, 1.5, 0.6, op=0.7))
    # the open front: dark interior between posts, the gripman at his lever
    inner = [fm(0.06, 0.1), fm(0.94, 0.1), fm(0.94, 0.58), fm(0.06, 0.58)]
    out.append(F(inner, INK, 0.9))
    out.append(segs([(fm(u, 0.06), fm(u, 0.6)) for u in (0.05, 0.36, 0.64, 0.95)], max(1.2, s * 0.09), seed, 0, color=PAPER))
    gx, gy = fm(0.5, 0.6)
    out.append(person(gx, gy, s * 1.55, seed + 3, op=1.0))
    out.append(segs([(fm(0.52, 0.6), fm(0.6, 0.32))], max(1.0, s * 0.05), seed, 0, color=PAPER))
    # roof, sign box, headlamp
    roof = [C(x0 - 0.1, g0 + Hh + 0.05, Z - 0.2), C(x1 + 0.1, g0 + Hh + 0.05, Z - 0.2), C(x1 + 0.1, g1 + Hh + 0.05, Z + L), C(x0 - 0.1, g1 + Hh + 0.05, Z + L)]
    out.append(F(roof, PAPER) + H(U, roof, 0, 1.3, 0.6, op=0.8) + sketch(roof, 1.3, seed, 0.2))
    sign = [C(x0 + 0.5, g0 + Hh + 0.55, Z), C(x1 - 0.5, g0 + Hh + 0.55, Z), C(x1 - 0.5, g0 + Hh + 0.08, Z), C(x0 + 0.5, g0 + Hh + 0.08, Z)]
    out.append(F(sign, PAPER) + sketch(sign, 1.0, seed, 0.1))
    hx, hy = C(X, g0 + 0.95, Z - 0.05)
    out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(s * 0.16)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(sketch(fr, 1.6, seed + 4, 0.2))
    # running board + riders hanging on the inner side
    rb = [C(x1 + 0.35, g0 + 0.35, Z + 0.3), C(x1 + 0.35, g1 + 0.35, Z + L * 0.5), C(x1, g1 + 0.3, Z + L * 0.5), C(x1, g0 + 0.3, Z + 0.3)]
    out.append(F(rb, INK, 0.9))
    for k, u in enumerate((0.08, 0.2, 0.33)):
        zz = Z + 0.3 + u * L
        px_, py_ = C(x1 + 0.3, sf_ground(zz) + 0.4, zz)
        dz = C.depth(x1, zz)
        out.append(person(px_, py_, C.f * 1.65 / dz, seed + 10 + k, flip=k == 1))
        hx_, hy_ = C(x1 + 0.12, sf_ground(zz) + 2.2, zz)
        out.append(seg(px_, py_ - C.f * 1.2 / dz, hx_, hy_, max(0.9, C.f * 0.06 / dz), seed, 0))
    # wheels/truck under the front
    for u in (0.2, 0.8):
        wx, wy = fm(u, 1.0)
        out.append(f'<ellipse cx="{f1(wx)}" cy="{f1(wy + s * 0.08)}" rx="{f1(s * 0.22)}" ry="{f1(s * 0.12)}" fill="{INK}"/>')
    return "".join(out)


def bay_and_hills(U, yh, seed):
    """The bay seen over the bottom of the hill: Marin headlands under a fog bank, Angel Island, Alcatraz with
    its lighthouse and cellhouse, sailboats; water ruled in fine horizontal lines."""
    out = []
    # fog bank rolling over the headlands
    fog = [(60, yh - 14), (110, yh - 30), (170, yh - 26), (240, yh - 40), (300, yh - 34), (360, yh - 46), (430, yh - 36), (500, yh - 44),
           (560, yh - 30), (600, yh - 22), (600, yh), (60, yh)]
    fd = scallop_d(fog[:-2], 330, yh + 40, 0.3, seed)
    # headlands (pale, fine hatching) with the fog lying on them
    hills = [(40, yh), (90, yh - 16), (150, yh - 24), (200, yh - 18), (250, yh - 30), (330, yh - 22), (380, yh - 34), (440, yh - 28),
             (500, yh - 20), (560, yh - 26), (600, yh - 14), (600, yh), (40, yh)]
    hd = smooth_closed(hills)
    out.append(F(hd, PAPER) + H(U, hd, 70, 2.4, 0.6, box=(0, yh - 40, 600, yh), op=0.6, wob=0.2, brk=0.2)
               + pen(hills[:-2], 1.0, seed, 0.2, smooth=True, op=0.8))
    out.append(H(U, rect(0, yh - 60, 600, yh - 20), 0, 2.4, 0.5, op=0.25))
    # water
    w = rect(0, yh, 600, yh + 110)
    out.append(F(w, PAPER) + segs([((x, y), (x + L, y)) for y, x, L in
                                   [(yh + 2 + j * 2.6, (j * 37) % 23 + i * 31, 18 + (i * 7 + j) % 11) for j in range(40) for i in range(-1, 20)]],
                                  0.55, seed, 0.2, op=0.55))
    # Angel Island (left), Alcatraz (centre right)
    ai = [(70, yh + 2), (100, yh - 10), (140, yh - 16), (170, yh - 8), (196, yh + 2)]
    out.append(F(smooth_open(ai) + " Z", PAPER) + H(U, smooth_open(ai) + " Z", 80, 1.8, 0.7, box=(60, yh - 20, 200, yh + 4)) + pen(ai, 1.1, seed, 0.1, smooth=True))
    ax = 352
    rock = [(ax - 44, yh + 6), (ax - 36, yh - 2), (ax - 20, yh - 6), (ax + 10, yh - 7), (ax + 34, yh - 3), (ax + 46, yh + 6)]
    out.append(F(rock, PAPER) + H(U, rock, 80, 1.6, 0.7) + pen(rock, 1.3, seed, 0.1))
    ch = rect(ax - 18, yh - 15, ax + 20, yh - 6)
    out.append(F(ch, PAPER) + H(U, rect(ax + 6, yh - 15, ax + 20, yh - 6), 90, 1.2, 0.6) + sketch(ch, 1.0, seed, 0.2)
               + segs([((ax - 16 + i * 3.4, yh - 13), (ax - 16 + i * 3.4, yh - 9)) for i in range(11)], 0.7, seed, 0))
    lh = [(ax - 28, yh - 4), (ax - 27, yh - 24), (ax - 25, yh - 24), (ax - 24, yh - 4)]
    out.append(F(lh, PAPER) + pen(lh, 1.0, seed, 0.05, True) + F(rect(ax - 28, yh - 27, ax - 24, yh - 24), INK))
    out.append(F(rect(ax + 26, yh - 14, ax + 29, yh - 4), PAPER) + sketch(rect(ax + 26, yh - 14, ax + 29, yh - 4), 0.8, seed, 0.1))
    # sailboats
    # a ferry crossing, wake behind it
    fx, fy = 236, yh + 52
    hull = [(fx - 30, fy), (fx + 34, fy), (fx + 28, fy + 6), (fx - 26, fy + 6)]
    out.append(F(hull, INK, 0.9) + F(rect(fx - 22, fy - 7, fx + 20, fy), PAPER) + window_grid(U, fx - 20, fx + 18, fy - 6, fy - 1, 9, 1, seed, dark=0.85, sill=False)
               + sketch(rect(fx - 22, fy - 7, fx + 20, fy), 0.9, seed, 0.1) + F(rect(fx - 12, fy - 12, fx + 8, fy - 7), PAPER)
               + sketch(rect(fx - 12, fy - 12, fx + 8, fy - 7), 0.9, seed, 0.1) + seg(fx - 2, fy - 12, fx - 2, fy - 18, 1.2, seed, 0))
    out.append(segs([((fx + 36 + i * 9, fy + 3 + i * 0.4), (fx + 44 + i * 9, fy + 3 + i * 0.4)) for i in range(8)], 0.8, seed, 0.2))
    for bx, by, s_ in ((250, yh + 14, 9), (500, yh + 10, 7), (330, yh + 30, 11), (140, yh + 22, 7), (420, yh + 60, 13), (180, yh + 80, 10)):
        out.append(F([(bx, by - s_ * 1.4), (bx, by - 1), (bx + s_ * 0.7, by - 1)], PAPER) + pen([(bx, by - s_ * 1.4), (bx, by - 1), (bx + s_ * 0.7, by - 1), (bx, by - s_ * 1.4)], 0.9, int(bx), 0.05)
                   + F([(bx - s_ * 0.5, by - 1), (bx + s_ * 0.9, by - 1), (bx + s_ * 0.7, by + 1.5), (bx - s_ * 0.3, by + 1.5)], INK)
                   + seg(bx - s_ * 0.6, by + 3, bx + s_ * 0.9, by + 3, 0.6, int(bx), 0))
    return "".join(out)


@design("san-francisco")
def san_francisco(U):
    """From the sidewalk near the crest of Hyde Street, looking down and across to the bay on an afternoon with
    fog over the headlands: the row of Victorians stepping down the hill like a staircase, the street plunging
    to the water, a cable car (vermilion panels) grinding up toward us, Alcatraz and sailboats beyond."""
    art = []
    C = YCam(f=1100, cx=300, vpy=128, eye=1.6, yaw=0.0)

    def D(X, Z):
        return C.depth(X, Z)
    art.append(cloud(U, 196, 64, 104, 14, 31) + cloud(U, 452, 46, 70, 10, 32))
    art.append(bay_and_hills(U, 130, 34))
    # waterfront park at the bottom of the hill
    yw = C(0, sf_ground(170), 170)[1]
    ys = C(0, sf_ground(170), 300)[1]
    # the flat ground at the bottom of the hill: a little park with the turntable, lawns and trees, the shore
    flat = rect(0, ys, 600, yw + 2)
    art.append(F(flat, PAPER) + H(U, flat, 0, (3.6, 2.4), 0.55, dark=(300, yw), op=0.45, wob=0.3, brk=0.3))
    q = [C(-4.5, sf_ground(170), 300), C(4.5, sf_ground(170), 300), C(4.5, sf_ground(170), 170), C(-4.5, sf_ground(170), 170)]
    art.append(F(q, PAPER) + H(U, q, 0, 2.6, 0.5, op=0.5))
    # a belt of park trees along the shore, broken where the street runs down to the turntable
    rnd_ = random.Random(601)
    for xa, xb in ((60, 282), (318, 540)):
        top = []
        x = xa
        while x < xb:
            top.append((x, ys - rnd_.uniform(4, 13)))
            x += rnd_.uniform(5, 11)
        top.append((xb, ys - 3))
        mass = [(xa, ys + 7)] + top + [(xb, ys + 7)]
        art.append(F(mass, PAPER)
                   + tone(U, mass, 3, 80, box=bbox(mass, 8)) + pen(top, 1.0, 603, 0.4, smooth=True))
    for X, Z, sd in ((-2.5, 240, 1), (3.5, 210, 2), (-6, 200, 3)):
        x, y = C(X, sf_ground(170), Z)
        art.append(walker(x, y, C.f * 1.7 / Z, 650 + sd))
    art.append(seg(0, ys, 600, ys, 1.4, 9, 0.2) + seg(0, ys + 2.5, 600, ys + 2.5, 0.7, 10, 0.2))
    def street(z0, z1):
        o = []
        q = [C(-4.5, sf_ground(z1), z1), C(4.5, sf_ground(z1), z1), C(4.5, sf_ground(z0), z0), C(-4.5, sf_ground(z0), z0)]
        flat = abs(sf_ground(z0) - sf_ground(z1)) < 0.01
        o.append(F(q, PAPER))
        o.append(H(U, q, 0, (3.0, 1.8) if not flat else (4.6, 3.6), 0.6, dark=(200, 480), op=0.6 if not flat else 0.4, wob=0.2, brk=0.2))
        for xr in (-2.4, -0.8, 0.8, 2.4):
            o.append(pen([C(xr, sf_ground(z0), z0), C(xr, sf_ground(z1), z1)], 0.9, int(xr * 10), 0.05))
        for xr in (-1.6, 1.6):
            o.append(pen([C(xr, sf_ground(z0), z0), C(xr, sf_ground(z1), z1)], 0.6, int(xr * 10) + 3, 0.05, op=0.8))
        if flat:
            cw = []
            for j in range(10):
                xa = -4.2 + j * 0.9
                cw.append([C(xa, sf_ground(z0), z0 + 0.4), C(xa + 0.45, sf_ground(z0), z0 + 0.4), C(xa + 0.45, sf_ground(z0), z0 + 2.6),
                           C(xa, sf_ground(z0), z0 + 2.6)])
            o.append(F(" ".join(poly(c) for c in cw), PAPER) + "".join(sketch(c, 0.6, 9, 0.1) for c in cw))
        for sx in (-1, 1):
            if flat:
                wq = [C(sx * 4.5, sf_ground(z0), z0), C(sx * 4.5, sf_ground(z1), z1), C(sx * 30, sf_ground(z1), z1), C(sx * 30, sf_ground(z0), z0)]
                o.append(F(wq, PAPER) + H(U, wq, 0, 4.4, 0.5, op=0.4))
                continue
            wq = [C(sx * 4.5, sf_ground(z0) + 0.15, z0), C(sx * 4.5, sf_ground(z1) + 0.15, z1), C(sx * 7, sf_ground(z1) + 0.15, z1),
                  C(sx * 7, sf_ground(z0) + 0.15, z0)]
            o.append(F(wq, PAPER) + segs([(C(sx * 4.5, sf_ground(z) + 0.15, z), C(sx * 7, sf_ground(z) + 0.15, z)) for z in
                                          [z0 + i * 1.0 for i in range(int(z1 - z0))]], 0.5, 5, 0, op=0.6))
            o.append(pen([wq[0], wq[1]], 1.3, 6, 0.05))
        return "".join(o)
    blocks = [(99, 168), (59, 92), (27, 52), (12.0, 20)]
    crossings = {1: (92, 99), 2: (52, 59), 3: (20, 27)}
    for bi, (b0, b1) in enumerate(blocks):
        if bi in crossings:
            art.append(street(*crossings[bi]))
            # the cross street's far corner houses, seen beyond the crossing (left side, shaded)
        art.append(street(b0, b1))
        for sx in (-1, 1):
            z = b0 + 0.3
            k = 0
            while z < b1 - 2:
                W = 7.4
                z1 = min(b1, z + W)
                ht = 9.4 + ((k * 7 + bi * 3 + (sx > 0)) % 3) * 1.2
                art.append(vic3d(U, C, sx * 7, z, z1, ht, 100 + bi * 20 + k * 2 + (sx > 0), shade=2 if sx < 0 else 0,
                                 gable=(k + bi + (sx > 0)) % 2 == 0))
                z = z1
                k += 1
    # sidewalk trees and lamp posts
    for sx, z in ():
        x, y = C(sx * 5.5, sf_ground(z) + 0.15, z)
        h = C.f * 6.5 / D(sx * 5.5, z)
        art.append(tree(U, x, y, h, h * 0.6, 400 + int(z), light=(-1, -1), trunk_h=0.42, lobes=5, lw=max(1.0, min(1.8, h / 120))))
    for sx, z in ((-1, 29.0), (1, 36.0), (-1, 50), (1, 69), (-1, 86)):
        x, y = C(sx * 4.9, sf_ground(z) + 0.15, z)
        art.append(lamp(x, y, C.f * 4.4 / D(sx * 4.9, z), 70 + int(z), "globe", max(1.1, min(2.4, 60 / D(sx * 4.9, z)))))
    # the cable car
    art.append(cable_car_front(U, C, -1.7, 37.0, 81))
    # people climbing the sidewalks
    for X, Z, sd, kind, fl in ((5.7, 30.5, 91, "bag", True), (5.9, 39, 94, "dog", True), (5.4, 66, 95, "plain", False),
                               (-5.6, 33, 92, "dress", False), (-5.7, 62, 93, "plain", False), (5.6, 47, 96, "plain", False),
                               (-5.4, 45, 97, "hat", True), (2.0, 26.6, 98, "plain", False), (-0.6, 25.9, 99, "dress", True),
                               (-3.0, 25.3, 100, "bag", False), (3.4, 27.4, 101, "plain", True)):
        x, y = C(X, sf_ground(Z) + (0.15 if abs(X) > 4.5 else 0), Z)
        art.append(walker(x, y, C.f * 1.7 / D(X, Z), sd, flip=fl, kind=kind))
    art.append(gull(318, 92, 8, 97) + gull(344, 80, 6, 98) + bird(240, 86, 5, 99) + gull(270, 196, 7, 100))
    return plate(U, "san-francisco", art, 25, cy=250)


# ================================================================ SAVANNAH
def moss(x, y, L, seed, n=None, spread=None, w=0.7, op=0.9):
    """Spanish moss: a hanging curtain of fine wavy strands, longer in the middle."""
    rnd = random.Random(seed)
    n = n or max(3, int(L / 3))
    spread = spread if spread is not None else L * 0.35
    d = []
    for i in range(n):
        t = (i + 0.5) / n
        x0 = x + (t - 0.5) * spread + rnd.uniform(-1, 1)
        ll = L * (0.45 + 0.55 * math.sin(math.pi * t)) * rnd.uniform(0.75, 1.1)
        pts = []
        k = max(3, int(ll / 4))
        for j in range(k + 1):
            u = j / k
            pts.append((x0 + math.sin(u * 7 + i) * 1.4 * u + rnd.uniform(-0.6, 0.6), y + ll * u))
        d.append(smooth_open(pts))
    return P(" ".join(d), w, INK, op)


def live_oak(U, x, base, limbs, seed, light=(1, -1), lw=1.6, moss_k=1.0, tw=22, lobe_k=1.0, dense=1.4):
    """A southern live oak drawn from explicit limbs (lists of points from the trunk head outward): a short, massive
    textured trunk, long sprawling limbs, big clumped crowns riding along them with dark undersides, and curtains
    of Spanish moss hanging below."""
    rnd = random.Random(seed)
    out = []
    head = limbs[0][0]
    tr = [(x - tw * 1.1, base), (x - tw * 0.55, base - tw * 0.6), (head[0] - tw * 0.5, head[1] + tw * 0.4), (head[0] + tw * 0.5, head[1] + tw * 0.3),
          (x + tw * 0.55, base - tw * 0.6), (x + tw * 1.2, base)]
    trd = smooth_closed(tr)
    out.append(F(trd, PAPER) + H(U, trd, 92, (2.6, 1.4), (0.6, 1.0), dark=(x + tw, base - tw), box=bbox(tr), wob=0.6, brk=0.25)
               + H(U, trd, 20, 3.0, 0.6, span=(0.5, 1), dark=(x + tw, base), box=bbox(tr), wob=0.4, brk=0.3) + P(trd, 1.8))
    spots = []
    bands = []
    for i, L in enumerate(limbs):
        pts = cr(L, False, 5)
        n = len(pts)
        top, bot = [], []
        for j in range(int(n * 0.3), n):
            px_, py_ = pts[j]
            t = j / n
            r = (40 - 16 * t) * lobe_k
            top.append((px_, py_ - r * 0.75))
            bot.append((px_, py_ + r * 0.35))
        if len(top) > 2:
            bands.append(top + bot[::-1])
        step = max(1, int(n / 11))
        for j in range(int(n * 0.3), n, step):
            px_, py_ = pts[j]
            t = j / n
            r = (40 - 16 * t) * lobe_k * rnd.uniform(0.85, 1.15)
            spots.append((px_ + rnd.uniform(-5, 5), py_ - r * 0.4 + rnd.uniform(-4, 4) * lobe_k, r, r * rnd.uniform(0.5, 0.62)))
    for bd in bands:
        d = smooth_closed(bd)
        out.append(F(d, PAPER) + tone(U, d, 4, 100, box=bbox(bd), wob=0.4, brk=0.25))
    for i, L in enumerate(limbs):
        w0 = tw * (0.9 - 0.1 * i)
        out.append(nib(L, max(3, w0), taper=(1, 0.18), ramp=0.2, seed=seed + i, color=INK))
    spots.sort(key=lambda q: q[1])
    for i, (cx_, cy_, a, b) in enumerate(spots):
        out.append(lobe(U, cx_, cy_, a, b, seed * 13 + i, light=light, w=lw, dense=dense, shade=1.2))
    for i, (cx_, cy_, a, b) in enumerate(spots):
        if rnd.random() < 0.9 * moss_k:
            out.append(moss(cx_ + rnd.uniform(-a, a) * 0.5, cy_ + b * 0.7, rnd.uniform(1.2, 2.4) * b * 1.6, seed * 7 + i, spread=a * 0.9,
                            w=max(0.5, lw * 0.42), n=int(a / 2.2)))
    return "".join(out)


def fountain(U, cx, yb, s, seed=1):
    """A tiered cast-iron fountain (elevation, s px per unit): wide basin with a coping and iron fence, four tritons
    blowing jets, a fluted pedestal, a broad lower bowl and a smaller upper bowl spilling curtains of water, and a
    robed figure on top. Lit from the left."""
    out = []

    def X(u):
        return cx + u * s

    def Y(v):
        return yb - v * s
    # basin: rim ellipse, water surface, coping face
    rx, ry = 13.0, 2.2
    rim_back = [(X(rx * math.cos(a)), Y(1.2) - ry * s * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]]
    rim_front = [(X(rx * math.cos(a)), Y(1.2) + ry * s * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]]
    water = rim_back + rim_front[::-1]
    out.append(F(water, PAPER))
    out.append(H(U, water, 0, (2.2, 3.4), 0.6, dark=(cx, Y(1.2) - ry * s), op=0.7, wob=0.3, brk=0.3))
    face = rim_front + [(X(-rx), Y(0)) ]
    face = rim_front[::-1] + [(X(rx * math.cos(a)), Y(0) + ry * s * math.sin(a)) for a in [math.pi * i / 30 for i in range(31)]]
    out.append(F(face, PAPER) + H(U, face, 90, (3.0, 1.6), (0.6, 0.9), dark=(X(rx), Y(0.5)), span=(0.35, 1), wob=0.1, brk=0) + pen(face, 1.3, seed, 0.1))
    out.append(pen(rim_back, 1.3, seed, 0.1, smooth=True) + pen(rim_front, 1.8, seed + 1, 0.1, smooth=True))
    # pedestal base in the water, tritons, jets
    pb = rect(X(-2.2), Y(4.2), X(2.2), Y(1.2))
    out.append(F(pb, PAPER) + H(U, rect(X(0.6), Y(4.2), X(2.2), Y(1.2)), 90, 1.5, 0.7) + sketch(pb, 1.3, seed, 0.3))
    for k, (u, fl) in enumerate(((-3.6, -1), (-1.4, -1), (1.4, 1), (3.6, 1))):
        bx, by = X(u), Y(1.6)
        body = [(bx - fl * 0.9 * s, by), (bx - fl * 1.1 * s, by - 1.6 * s), (bx - fl * 0.2 * s, by - 2.8 * s), (bx + fl * 0.5 * s, by - 3.1 * s),
                (bx + fl * 0.8 * s, by - 2.2 * s), (bx + fl * 0.6 * s, by - 0.8 * s), (bx + fl * 1.2 * s, by)]
        out.append(F(smooth_closed(body), INK, 0.88))
        out.append(f'<circle cx="{f1(bx + fl * 0.15 * s)}" cy="{f1(by - 3.4 * s)}" r="{f1(0.45 * s)}" fill="{INK}" opacity="0.9"/>')
        hx, hy = bx + fl * 0.6 * s, by - 3.6 * s
        out.append(P(f"M {f1(hx)} {f1(hy)} L {f1(hx + fl * 0.9 * s)} {f1(hy - 0.5 * s)}", max(1.2, 0.3 * s)))
        jet = [(hx + fl * 0.9 * s, hy - 0.5 * s), (hx + fl * 3.0 * s, hy - 2.4 * s), (hx + fl * 4.6 * s, by - 0.6 * s)]
        out.append(P(smooth_open(jet), 0.9) + P(smooth_open([(a + fl * 0.6, b + 0.8) for a, b in jet]), 0.6, INK, 0.7))
        sx_, sy_ = jet[-1]
        out.append(segs([((sx_ - 3 + j * 1.5, sy_ + 0.5), (sx_ - 4 + j * 2, sy_ - 3 - (j % 2) * 2)) for j in range(5)], 0.6, seed + k, 0.3))
    # fluted pedestal up to the lower bowl
    ped = [(X(-1.4), Y(4.2)), (X(-0.9), Y(8.0)), (X(-1.5), Y(9.0)), (X(1.5), Y(9.0)), (X(0.9), Y(8.0)), (X(1.4), Y(4.2))]
    out.append(F(ped, PAPER) + segs([((X(u), Y(4.3)), (X(u * 0.68), Y(7.9))) for u in (-0.8, -0.3, 0.2, 0.7)], 0.7, seed, 0)
               + H(U, [(X(0.4), Y(4.2)), (X(1.4), Y(4.2)), (X(0.9), Y(8.0)), (X(0.3), Y(8.0))], 90, 1.3, 0.7) + pen(ped, 1.4, seed, 0.05, True))
    # lower bowl
    lb = [(X(-7.2), Y(10.2)), (X(-6.4), Y(9.4)), (X(-3.0), Y(8.6)), (X(3.0), Y(8.6)), (X(6.4), Y(9.4)), (X(7.2), Y(10.2))]
    lbd = smooth_open(lb) + f" L {f1(X(7.2))} {f1(Y(10.6))} L {f1(X(-7.2))} {f1(Y(10.6))} Z"
    out.append(F(lbd, PAPER) + H(U, lbd, 75, (2.6, 1.4), (0.6, 0.9), dark=(X(7), Y(9)), span=(0.25, 1), box=(X(-7.5), Y(10.8), X(7.5), Y(8.4)))
               + P(lbd, 1.5))
    # water curtain from the lower bowl
    cur = []
    for i in range(29):
        u = -7.0 + i * 0.5
        top_ = Y(10.0) if abs(u) > 6.2 else Y(9.6 - (6.2 - abs(u)) * 0.12)
        cur.append(((X(u * 1.02), Y(10.2)), (X(u * 1.12), Y(1.6))))
    out.append(segs(cur, 0.5, seed, 0.4, op=0.55))
    # upper pedestal + bowl + figure
    up = [(X(-0.7), Y(10.6)), (X(-0.45), Y(14.0)), (X(-0.9), Y(14.6)), (X(0.9), Y(14.6)), (X(0.45), Y(14.0)), (X(0.7), Y(10.6))]
    out.append(F(up, PAPER) + H(U, [(X(0.1), Y(10.6)), (X(0.7), Y(10.6)), (X(0.45), Y(14.0)), (X(0.1), Y(14.0))], 90, 1.2, 0.6) + pen(up, 1.2, seed, 0.05, True))
    ub = [(X(-3.6), Y(15.6)), (X(-3.1), Y(15.0)), (X(-1.2), Y(14.4)), (X(1.2), Y(14.4)), (X(3.1), Y(15.0)), (X(3.6), Y(15.6))]
    ubd = smooth_open(ub) + f" L {f1(X(3.6))} {f1(Y(15.9))} L {f1(X(-3.6))} {f1(Y(15.9))} Z"
    out.append(F(ubd, PAPER) + H(U, ubd, 75, (2.4, 1.4), (0.6, 0.85), dark=(X(3.5), Y(15)), span=(0.3, 1), box=(X(-3.8), Y(16.1), X(3.8), Y(14.2)))
               + P(ubd, 1.4))
    out.append(segs([((X(u), Y(15.6)), (X(u * 1.25), Y(10.4))) for u in [-3.4 + i * 0.4 for i in range(18)]], 0.5, seed, 0.4, op=0.55))
    fig = [(X(-0.9), Y(15.9)), (X(-0.8), Y(17.6)), (X(-0.5), Y(19.6)), (X(-0.3), Y(20.6)), (X(0.4), Y(20.6)), (X(0.6), Y(19.4)),
           (X(1.3), Y(19.8)), (X(1.4), Y(19.2)), (X(0.7), Y(18.6)), (X(0.8), Y(17.4)), (X(0.9), Y(15.9))]
    out.append(F(smooth_closed(fig), PAPER) + H(U, smooth_closed(fig), 90, 1.1, 0.6, span=(0.45, 1), dark=(X(1.4), Y(18)),
                                                 box=(X(-1), Y(21), X(1.5), Y(15.8))) + P(smooth_closed(fig), 1.2))
    out.append(f'<circle cx="{f1(X(0.05))}" cy="{f1(Y(21.2))}" r="{f1(0.62 * s)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>')
    out.append(nib([(X(-0.2), Y(19.8)), (X(-1.0), Y(21.4)), (X(-1.3), Y(22.8))], max(1.2, 0.3 * s), taper=(1, 0.5), seed=seed, color=INK))
    # the iron fence round the basin (front arc)
    fence = []
    for i in range(41):
        a = math.pi * i / 40
        x_, y_ = X((rx + 1.6) * math.cos(a)), Y(-0.6) + (ry + 0.5) * s * math.sin(a)
        fence.append(((x_, y_), (x_, y_ - 1.8 * s)))
    out.append(segs(fence, 0.8, seed, 0))
    out.append(pen([(X((rx + 1.6) * math.cos(math.pi * i / 40)), Y(-0.6) + (ry + 0.5) * s * math.sin(math.pi * i / 40) - 1.8 * s) for i in range(41)],
                   1.2, seed, 0.05, smooth=True))
    out.append(pen([(X((rx + 1.6) * math.cos(math.pi * i / 40)), Y(-0.6) + (ry + 0.5) * s * math.sin(math.pi * i / 40) - 0.9 * s) for i in range(41)],
                   0.8, seed + 1, 0.05, smooth=True))
    return "".join(out)


def azalea(U, x, y, r, seed, acc=True):
    """An azalea bush in bloom: a rounded clump, the blossoms washed in the vermilion accent."""
    d = scallop_d(scallop_pts(x, y, r, r * 0.6, seed, 12, 0.12), x, y, 0.3, seed)
    out = [F(d, PAPER)]
    if acc:
        out.append(accent(U, d, (x - r * 1.3, y - r, x + r * 1.3, y + r), seed, op=0.95, ang=-30, n=int(8 + r), length=(3, 8), width=(1.4, 2.6)))
    rnd = random.Random(seed)
    dots = "".join(f'<circle cx="{f1(x + rnd.uniform(-r, r) * 0.9)}" cy="{f1(y + rnd.uniform(-r, r) * 0.5)}" r="{rnd.uniform(0.6, 1.2):.1f}"/>' for _ in range(int(r * 2)))
    out.append(clipped(U("az"), d, f'<g fill="{INK}" opacity="0.8">{dots}</g>' + H(U, d, 100, 2.0, 0.6, span=(0.6, 1), dark=(x + r, y + r))))
    out.append(P(d, 1.0))
    return "".join(out)


def bench_persp(x, y, L, h, seed, flip=False):
    """A park bench seen three-quarters: slatted seat and back, iron ends."""
    k = -1 if flip else 1
    out = []
    a, b = (x, y), (x + k * L, y - L * 0.12)
    for j in range(3):
        out.append(seg(a[0], a[1] - h * 0.5 - j * 1.6, b[0], b[1] - h * 0.5 - j * 1.6, 1.1, seed + j, 0))
    for j in range(3):
        out.append(seg(a[0] - k * 1, a[1] - h * 0.9 - j * 2.2, b[0] - k * 1, b[1] - h * 0.9 - j * 2.2, 1.0, seed + 5 + j, 0))
    for p in (a, b):
        out.append(P(f"M {f1(p[0])} {f1(p[1])} L {f1(p[0])} {f1(p[1] - h * 1.3)} M {f1(p[0] + k * 2)} {f1(p[1])} L {f1(p[0])} {f1(p[1] - h * 0.5)}", 1.3))
    return "".join(out)


@design("savannah")
def savannah(U):
    """Under the live oaks of a Savannah square on a spring morning: two great oaks arch their mossy limbs over
    the path toward a sunlit tiered fountain ringed by azaleas (the accent), benches in the dappled shade, a
    couple strolling, a dog walker, townhouses glimpsed through the trees."""
    art = []
    C = Cam(f=300, cx=300, vpy=318, eye=1.6)
    # far townhouses through the trees (pale, fine line)
    for i, (x0, x1, top) in enumerate(((84, 150, 220), (150, 210, 232), (392, 452, 228), (452, 520, 214))):
        q = rect(x0, top, x1, 318)
        art.append(F(q, PAPER) + window_grid(U, x0 + 4, x1 - 4, top + 10, 312, max(3, int((x1 - x0) / 14)), 4, 200 + i, dark=0.45, w=0.6)
                   + segs([((x0, top), (x1, top)), ((x0, top + 4), (x1, top + 4))], 0.9, i, 0.1, op=0.6)
                   + pen([(x0, 318), (x0, top), (x1, top), (x1, 318)], 0.9, i, 0.1, op=0.6))
    # middle-distance oaks at the sides, behind the fountain
    art.append(live_oak(U, 150, 322, [[(150, 268), (120, 238), (70, 222)], [(150, 268), (176, 236), (214, 222)], [(150, 268), (148, 230), (140, 200)]],
                        31, lw=1.0, tw=9, lobe_k=0.62, dense=1.6))
    art.append(live_oak(U, 452, 322, [[(452, 268), (482, 238), (532, 222)], [(452, 268), (424, 236), (386, 222)], [(452, 268), (456, 230), (462, 200)]],
                        37, lw=1.0, tw=9, lobe_k=0.62, dense=1.6))
    # lawn and the sand path toward the fountain
    lawn = rect(0, 318, 600, 490)
    art.append(F(lawn, PAPER) + H(U, lawn, 0, (5.0, 2.6), 0.55, dark=(300, 490), op=0.5, wob=0.3, brk=0.3))
    path = [C(-3.0, 0, 40), C(3.0, 0, 40), C(3.0, 0, 3), C(-3.0, 0, 3)]
    rr = random.Random(5)
    art.append(F(path, PAPER) + clipped(U("pd"), poly(path), "".join(
        f'<circle cx="{f1(300 + rr.uniform(-220, 220))}" cy="{f1(326 + rr.random() ** 1.5 * 170)}" r="0.7" fill="{INK}" opacity="0.6"/>'
        for i in range(300))))
    art.append(pen([path[0], path[3]], 1.2, 3, 0.2) + pen([path[1], path[2]], 1.2, 4, 0.2))
    art.append(grass(0, 600, 319, 5, h=4, dens=0.7, w=0.7, op=0.7))
    # the fountain, sunlit, with azaleas round the fence
    art.append(fountain(U, 300, 340, 7.0, 41))
    for i, (x, y, r) in enumerate(((190, 348, 13), (216, 354, 11), (384, 354, 11), (410, 348, 13), (164, 340, 9), (436, 340, 9))):
        art.append(azalea(U, x, y, r, 50 + i))
    # dappled shade of the canopy over the foreground lawn
    sh = [(0, 404), (110, 392), (200, 414), (300, 404), (400, 416), (490, 394), (600, 404), (600, 500), (0, 500)]
    art.append(H(U, smooth_closed(sh), 10, 2.6, 0.7, box=(0, 386, 600, 500), op=0.7, wob=0.3, brk=0.2))
    rnd = random.Random(9)
    for i in range(14):
        x, y = rnd.uniform(60, 540), rnd.uniform(410, 470)
        art.append(F(smooth_closed(scallop_pts(x, y, rnd.uniform(6, 14), rnd.uniform(1.6, 3), 300 + i, 8, 0.2)), PAPER))
    # benches and people
    art.append(bench_persp(118, 396, 46, 12, 61) + bench_persp(482, 396, 46, 12, 62, flip=True))
    art.append(walker(140, 388, 34, 63, kind="dress") + walker(470, 386, 34, 64, flip=True, kind="hat"))
    art.append(walker(258, 380, 31, 65, kind="dress") + walker(272, 381, 34, 66))
    art.append(walker(352, 384, 34, 67, flip=True, kind="dog"))
    art.append(walker(234, 356, 17, 68, flip=True) + walker(372, 358, 18, 69))
    # the two great oaks framing the plate, their limbs arching toward each other overhead
    L = [[(70, 330), (92, 250), (170, 170), (252, 120)], [(70, 330), (40, 250), (30, 150)], [(70, 330), (120, 262), (200, 240), (250, 236)],
         [(70, 330), (90, 220), (170, 110), (290, 58)], [(70, 330), (70, 220), (90, 110), (110, 50)]]
    R = [[(x_ and 600 - x_, y_) for x_, y_ in l] for l in L]
    R[0][-1] = (348, 116)
    R[3][-1] = (318, 50)
    art.append(live_oak(U, 66, 456, L, 71, lw=1.7, tw=24, lobe_k=1.2))
    art.append(live_oak(U, 536, 452, R, 77, lw=1.7, tw=23, lobe_k=1.2))
    art.append(bird(300, 132, 6, 81) + bird(316, 120, 4.5, 82))
    return plate(U, "savannah", art, 35)


# ================================================================ ISTANBUL
def dome_pts(cx, base, r, h=None, n=20):
    h = h if h is not None else r
    return [(cx - r * math.cos(math.pi * i / n), base - h * math.sin(math.pi * i / n) ** 0.85) for i in range(n + 1)]


def minaret(U, x, base, h, w, seed, balconies=2, lvl=2):
    """A pencil minaret: slender shaft, corbelled balconies (serefe), a tall conical lead cap with a finial."""
    out = []
    cap_h = h * 0.16
    shaft = rect(x - w / 2, base - h + cap_h, x + w / 2, base)
    out.append(F(shaft, PAPER) + (tone(U, shaft, lvl, 90, box=bbox(shaft), wob=0, brk=0) if lvl else "") + sketch(shaft, max(0.7, w * 0.22), seed, 0.2))
    for k in range(balconies):
        yb = base - h * (0.52 + 0.17 * k)
        bal = [(x - w * 1.1, yb - w * 0.5), (x + w * 1.1, yb - w * 0.5), (x + w * 0.6, yb + w * 0.4), (x - w * 0.6, yb + w * 0.4)]
        out.append(F(bal, INK, 0.9))
        out.append(seg(x - w * 1.1, yb - w * 1.1, x + w * 1.1, yb - w * 1.1, max(0.5, w * 0.18), seed, 0))
    cone = [(x - w * 0.62, base - h + cap_h), (x, base - h), (x + w * 0.62, base - h + cap_h)]
    out.append(F(cone, INK, 0.85) + seg(x, base - h, x, base - h - w * 1.4, max(0.6, w * 0.2), seed, 0))
    return "".join(out)


def mosque(U, cx, base, s, seed, minarets=((-1.0, 1.0), (1.0, 1.0)), semis=2, lvl=2, dome_h=0.95, body_w=1.25, courtyard=0.0):
    """An imperial mosque (s = main dome radius in px), backlit: a cascade of semi-domes and half-domes rising to
    the great dome on its windowed drum, buttress turrets, a block body with arcades, and pencil minarets.
    minarets = [(x offset in s, height in units of 4.2 s)]."""
    rnd = random.Random(seed)
    out = []
    by = base - s * 0.55              # top of the body
    # minarets behind the outer edges first
    for ox, hk in minarets:
        if abs(ox) > body_w + 0.1:
            out.append(minaret(U, cx + ox * s, base, s * 4.2 * hk, max(2.2, s * 0.13), seed + int(ox * 10), balconies=3 if hk > 0.62 else 2, lvl=lvl))
    body = rect(cx - s * body_w, by, cx + s * body_w, base)
    out.append(F(body, PAPER) + tone(U, body, lvl, 85, box=bbox(body), wob=0.1, brk=0.05))
    arches = []
    n = max(4, int(body_w * 2 * s / 7))
    for i in range(n):
        ax = cx - s * body_w + (i + 0.5) * 2 * s * body_w / n
        aw = s * body_w / n * 0.5
        arches.append(f"M {f1(ax - aw)} {f1(base - 1)} L {f1(ax - aw)} {f1(by + s * 0.22)} Q {f1(ax)} {f1(by + s * 0.08)} {f1(ax + aw)} {f1(by + s * 0.22)} L {f1(ax + aw)} {f1(base - 1)} Z")
    out.append(f'<path d="{" ".join(arches)}" fill="{INK}" opacity="0.8"/>')
    out.append(sketch(body, max(0.8, s * 0.04), seed, 0.3))
    if courtyard:
        cw = s * courtyard
        side = -1 if courtyard > 0 else 1
        cq = rect(cx - s * body_w - cw, base - s * 0.34, cx - s * body_w, base)
        out.append(F(cq, PAPER) + tone(U, cq, lvl, 85, box=bbox(cq)) + sketch(cq, 0.8, seed, 0.2))
        k = max(3, int(cw / (s * 0.3)))
        for i in range(k):
            dx = cx - s * body_w - cw + (i + 0.5) * cw / k
            dd = dome_pts(dx, base - s * 0.34, cw / k * 0.45, cw / k * 0.4, 8)
            out.append(F(dd, PAPER) + pen(dd, 0.7, seed + i, 0.05))
    # outer half-domes and small domes
    for k in range(semis, 0, -1):
        r = s * (0.45 + 0.18 * (semis - k))
        for sg in (-1, 1):
            dx = cx + sg * s * (0.55 + 0.32 * k)
            dy = by - s * 0.12 * (semis - k)
            dd = dome_pts(dx, dy, r, r * 0.8, 14)
            out.append(F(dd + [(dx + r, dy + 2), (dx - r, dy + 2)], PAPER) + H(U, dd, 0, 1.8, 0.6, box=bbox(dd)) + pen(dd, max(0.8, s * 0.035), seed + k, 0.05, smooth=True))
    # drum with windows
    dr = s * 1.02
    drum = rect(cx - dr, by - s * 0.55, cx + dr, by + 1)
    out.append(F(drum, PAPER) + tone(U, drum, lvl, 90, box=bbox(drum), wob=0, brk=0))
    wn = 14
    ws = []
    for i in range(wn):
        a = math.pi * (i + 0.5) / wn
        wx = cx - dr * math.cos(a)
        ww = max(0.8, s * 0.12 * math.sin(a))
        ws.append(rect(wx - ww / 2, by - s * 0.45, wx + ww / 2, by - s * 0.12))
    out.append(F(" ".join(poly(w) for w in ws), INK, 0.85))
    out.append(sketch(drum, max(0.8, s * 0.035), seed + 2, 0.2))
    # buttress turrets with little domes
    for sg in (-1, 1):
        tx = cx + sg * dr * 1.02
        tq = rect(tx - s * 0.09, by - s * 0.75, tx + s * 0.09, by + 1)
        out.append(F(tq, PAPER) + sketch(tq, 0.8, seed, 0.1))
        dd = dome_pts(tx, by - s * 0.75, s * 0.11, s * 0.16, 8)
        out.append(F(dd, INK, 0.85))
    # the great dome
    dd = dome_pts(cx, by - s * 0.55, s, s * dome_h * 0.62, 24)
    out.append(F(dd, PAPER))
    out.append(H(U, dd, 0, (3.2, 1.8), (0.6, 0.9), dark=(cx, by - s * 0.55), box=bbox(dd), wob=0.2, brk=0))
    ribs = []
    for i in range(1, 12):
        ph = -math.pi / 2 + math.pi * i / 12
        ribs.append([(cx + s * math.sin(ph) * math.cos(t * math.pi / 2), by - s * 0.55 - s * dome_h * 0.62 * math.sin(t * math.pi / 2) ** 0.85)
                     for t in [j / 8 for j in range(9)]])
    out.append("".join(pen(r, max(0.5, s * 0.02), seed + i, 0.02, smooth=True, op=0.7) for i, r in enumerate(ribs)))
    out.append(pen(dd, max(1.0, s * 0.05), seed + 3, 0.05, smooth=True))
    top = by - s * 0.55 - s * dome_h * 0.62
    out.append(seg(cx, top, cx, top - s * 0.3, max(0.8, s * 0.04), seed, 0))
    out.append(P(f"M {f1(cx - s * 0.08)} {f1(top - s * 0.36)} A {f1(s * 0.08)} {f1(s * 0.08)} 0 1 0 {f1(cx + s * 0.08)} {f1(top - s * 0.36)}", max(0.7, s * 0.03)))
    # minarets in front of / beside the body
    for ox, hk in minarets:
        if abs(ox) <= body_w + 0.1:
            out.append(minaret(U, cx + ox * s, base, s * 4.2 * hk, max(2.2, s * 0.13), seed + int(ox * 10), balconies=3 if hk > 0.62 else 2, lvl=lvl))
    return "".join(out)


def vapur(U, x, wl, L, seed, flip=False, flag=True):
    """An Istanbul passenger ferry broadside: dark lower hull, white two-deck superstructure with rows of windows,
    a tall raked funnel, a flag at the stern (the vermilion accent), bow wave and wake."""
    k = -1 if flip else 1

    def X(u):
        return x + k * u * L
    h = L * 0.16
    out = []
    hull = [(X(-0.5), wl - h * 0.55), (X(0.5), wl - h * 0.7), (X(0.46), wl), (X(-0.44), wl)]
    out.append(F(hull, INK, 0.92))
    out.append(seg(X(-0.48), wl - h * 0.5, X(0.49), wl - h * 0.62, 1.0, seed, 0, color=PAPER, op=0.8))
    d1 = [(X(-0.44), wl - h * 1.2), (X(0.36), wl - h * 1.3), (X(0.4), wl - h * 0.6), (X(-0.46), wl - h * 0.55)]
    d2 = [(X(-0.36), wl - h * 1.8), (X(0.24), wl - h * 1.85), (X(0.28), wl - h * 1.25), (X(-0.4), wl - h * 1.2)]
    for d, rows, seedk in ((d1, 1, 1), (d2, 1, 2)):
        out.append(F(d, PAPER))
        m = homog(d)
        wins = [[m((i + 0.2) / 16, 0.22), m((i + 0.8) / 16, 0.22), m((i + 0.8) / 16, 0.62), m((i + 0.2) / 16, 0.62)] for i in range(16)]
        out.append(F(" ".join(poly(w) for w in wins), INK, 0.85))
        out.append(H(U, d, 0, 1.6, 0.6, span=(0.75, 1), dark=pt(d[3], d[2], 0.5), box=bbox(d)) + sketch(d, 1.1, seed + seedk, 0.2))
    out.append(seg(X(-0.46), wl - h * 1.85, X(0.3), wl - h * 1.9, 1.3, seed, 0))
    # bridge house + funnel
    bh = [(X(0.06), wl - h * 2.3), (X(0.2), wl - h * 2.32), (X(0.2), wl - h * 1.85), (X(0.06), wl - h * 1.85)]
    out.append(F(bh, PAPER) + F([pt(bh[0], bh[1], 0.15), pt(bh[0], bh[1], 0.9), pt(bh[3], bh[2], 0.9), pt(bh[3], bh[2], 0.15)], INK, 0.0)
               + segs([(pt(bh[0], bh[3], 0.35), pt(bh[1], bh[2], 0.35))], 2.0, seed, 0) + sketch(bh, 1.0, seed, 0.1))
    fu = [(X(-0.1), wl - h * 1.85), (X(-0.02), wl - h * 1.85), (X(-0.05 - 0.06), wl - h * 3.3), (X(-0.14 - 0.06), wl - h * 3.25)]
    out.append(F(fu, PAPER) + H(U, fu, 90, 1.2, 0.6, span=(0.5, 1), dark=fu[1], box=bbox(fu)) + F([fu[3], fu[2], pt(fu[2], fu[1], 0.18), pt(fu[3], fu[0], 0.18)], INK, 0.9)
               + sketch(fu, 1.1, seed, 0.1))
    # mast + flag at the stern
    mx = X(-0.42)
    out.append(seg(mx, wl - h * 1.2, mx, wl - h * 2.6, 1.0, seed, 0))
    if flag:
        fw, fh = L * 0.08, L * 0.05
        fx0 = mx
        fd = smooth_open([(fx0, wl - h * 2.6), (fx0 - k * fw * 0.5, wl - h * 2.6 - fh * 0.15), (fx0 - k * fw, wl - h * 2.6 + fh * 0.05)])
        fd += " L " + smooth_open([(fx0 - k * fw, wl - h * 2.6 + fh * 1.05), (fx0 - k * fw * 0.5, wl - h * 2.6 + fh * 0.85), (fx0, wl - h * 2.6 + fh)])[2:] + " Z"
        out.append(F(fd, PAPER) + accent(U, fd, (fx0 - fw * 1.2, wl - h * 2.6 - fh, fx0 + fw * 1.2, wl - h * 2.6 + fh * 2), seed, op=1.0, ang=0, n=10,
                                         length=(4, 9), width=(1.4, 2.4)) + P(fd, 0.8))
        ccx, ccy = fx0 - k * fw * 0.42, wl - h * 2.6 + fh * 0.5
        out.append(f'<circle cx="{f1(ccx)}" cy="{f1(ccy)}" r="{f1(fh * 0.26)}" fill="{PAPER}"/><circle cx="{f1(ccx - k * fh * 0.08)}" cy="{f1(ccy)}" r="{f1(fh * 0.2)}" fill="#CF6B55"/>')
    # people at the rail
    for i in range(6):
        px_ = X(-0.34 + i * 0.1)
        out.append(F(rect(px_ - 1.2, wl - h * 1.85 - 4.5, px_ + 1.2, wl - h * 1.85), INK, 0.85))
    # bow wave + wake
    out.append(segs([((X(0.5), wl), (X(0.62), wl + 3)), ((X(0.48), wl + 1), (X(0.66), wl + 1.5))] +
                    [((X(-0.5 - i * 0.12), wl + 1 + i * 0.6), (X(-0.6 - i * 0.12), wl + 1 + i * 0.6)) for i in range(7)], 0.9, seed, 0.3))
    return "".join(out)


def rowboat(x, wl, L, seed, flip=False, fisher=True):
    k = -1 if flip else 1
    hull = [(x - L / 2, wl - L * 0.18), (x + L / 2, wl - L * 0.22), (x + k * L * 0.38, wl), (x - k * L * 0.36, wl)]
    hull = [(x - L / 2, wl - L * 0.16), (x + L / 2, wl - L * 0.2), (x + L * 0.38, wl), (x - L * 0.38, wl)]
    out = [F(hull, INK, 0.9)]
    if fisher:
        out.append(person(x + k * L * 0.1, wl - L * 0.16, L * 0.55, seed))
        out.append(P(f"M {f1(x + k * L * 0.16)} {f1(wl - L * 0.5)} Q {f1(x + k * L * 0.6)} {f1(wl - L * 1.0)} {f1(x + k * L * 0.95)} {f1(wl - L * 0.75)} L {f1(x + k * L * 0.95)} {f1(wl + 2)}", 0.6))
    out.append(seg(x - L * 0.5, wl + 1.5, x + L * 0.5, wl + 1.5, 0.6, seed, 0.2))
    return "".join(out)


@design("istanbul")
def istanbul(U):
    """Across the Golden Horn from the Karakoy quay at sunset: the Suleymaniye on its hill with four minarets, the
    New Mosque at the end of the Galata Bridge, Hagia Sophia faint beyond, houses and cypresses climbing the slope;
    the bridge lined with anglers' rods, ferries (one flying the vermilion flag), fishing boats and gulls."""
    art = []
    hz = 300           # far shore water line
    # sky: low sun behind the peninsula, rays, graded hatching toward the top
    sky = rect(0, 0, 600, hz)
    art.append(H(U, sky, 0, (2.6, 7.0), 0.6, dark=(300, 0), op=0.55, wob=0.2, brk=0.2, span=(0.0, 0.62)))
    sx_, sy_ = 168, 236
    rays = []
    for i in range(30):
        a = math.pi * (1.05 + 0.9 * i / 29)
        rays.append(((sx_ + math.cos(a) * 30, sy_ + math.sin(a) * 30), (sx_ + math.cos(a) * 190, sy_ + math.sin(a) * 190)))
    art.append(segs(rays, 0.5, 3, 0.2, op=0.35))
    art.append(f'<circle cx="{sx_}" cy="{sy_}" r="22" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    art.append(cloud(U, 420, 84, 120, 15, 4) + cloud(U, 250, 122, 90, 11, 6))
    # Hagia Sophia, faint, on the far left horizon
    art.append(f'<g opacity="0.55">{mosque(U, 76, 262, 15, 5, minarets=((-1.6, 0.55), (1.6, 0.55), (-2.3, 0.6), (2.3, 0.6)), semis=1, lvl=1, dome_h=0.75, body_w=1.6)}</g>')
    # the peninsula: hill with houses and cypresses
    hill = [(0, 268), (60, 262), (130, 252), (200, 236), (270, 218), (330, 206), (390, 200), (450, 204), (520, 218), (600, 230), (600, hz), (0, hz)]
    hd = smooth_closed(hill)
    art.append(F(hd, PAPER) + tone(U, hd, 2, 80, box=(0, 190, 600, hz), wob=0.3, brk=0.15))
    rnd = random.Random(11)
    houses = []
    for row in range(6):
        y0 = 216 + row * 14
        x = rnd.uniform(-10, 10)
        while x < 600:
            w_ = rnd.uniform(10, 20)
            hh = rnd.uniform(8, 13)
            # skip where the mosques stand
            if not (360 < x < 470 and row < 3) and not (180 < x < 300 and row > 3):
                ytop = y0 - hh
                houses.append((x, ytop, w_, hh, row))
            x += w_ + rnd.uniform(3, 12)
    def hill_y(x):
        for (xa, ya), (xb, yb_) in zip(hill, hill[1:10]):
            if xa <= x <= xb:
                return lerp(ya, yb_, (x - xa) / (xb - xa))
        return 230
    for (x, ytop, w_, hh, row) in sorted(houses, key=lambda q: q[1]):
        if ytop < hill_y(x + w_ / 2) - 2:
            continue
        q = rect(x, ytop, x + w_, ytop + hh)
        art.append(F(q, PAPER) + H(U, rect(x + w_ * 0.55, ytop, x + w_, ytop + hh), 90, 1.8, 0.6, op=0.8, wob=0, brk=0) + sketch(q, 0.7, int(x), 0.2))
        art.append(F([(x - 1, ytop), (x + w_ / 2, ytop - hh * 0.3), (x + w_ + 1, ytop)], INK, 0.75))
        art.append(F(" ".join(poly(rect(x + 2 + i * 4, ytop + 3, x + 3.6 + i * 4, ytop + 6)) for i in range(int((w_ - 2) / 4))), INK, 0.7))
    for i in range(16):
        cx_ = rnd.uniform(20, 580)
        cy_ = rnd.uniform(228, 290)
        hh = rnd.uniform(14, 26)
        if cy_ - hh < hill_y(cx_) - 6:
            continue
        art.append(F(smooth_closed([(cx_, cy_ - hh), (cx_ + 3.2, cy_ - hh * 0.5), (cx_ + 2.6, cy_), (cx_ - 2.6, cy_), (cx_ - 3.2, cy_ - hh * 0.5)]), INK, 0.88))
    # Suleymaniye on the crest, the New Mosque by the water
    art.append(mosque(U, 418, 214, 40, 21, minarets=((-1.75, 0.66), (1.75, 0.66), (-2.75, 0.52), (2.75, 0.52)), semis=2, lvl=2, body_w=1.5))
    art.append(mosque(U, 248, 292, 31, 23, minarets=((-1.8, 0.6), (1.8, 0.6)), semis=2, lvl=2, body_w=1.35, courtyard=1.6))
    # the far quay
    art.append(F(rect(0, hz - 6, 600, hz), PAPER) + seg(0, hz - 6, 600, hz - 6, 1.0, 3, 0.2) + H(U, rect(0, hz - 6, 600, hz), 0, 1.6, 0.6))
    # the water: ripples, sun glitter path, broken reflections
    water = rect(0, hz, 600, 490)
    art.append(F(water, PAPER))
    art.append(icf.ripples(U, 0, 600, hz + 2, 490, 17, dens=1.0, gap=(2.4, 7.0), ln=((5, 14), (14, 40)), w=(0.7, 1.5),
                           refl=[(200, 300, 0.6), (380, 460, 0.5)], skip=[(150, 186)], op=0.85))
    # Galata Bridge: running from the right foreground to the far shore by the New Mosque
    A, B = (612, 392), (300, 300)

    def bp(t, dy=0.0):
        x_ = lerp(A[0], B[0], t)
        sc = lerp(1.0, 0.32, t)
        return (x_, lerp(A[1], B[1], t) + dy * sc)
    deck_top, deck_bot = -46, -30
    low_top, low_bot = -30, -8
    seg_n = 40
    up = [bp(i / seg_n, deck_top) for i in range(seg_n + 1)]
    dn = [bp(i / seg_n, deck_bot) for i in range(seg_n + 1)]
    lt = [bp(i / seg_n, low_top) for i in range(seg_n + 1)]
    lb = [bp(i / seg_n, low_bot) for i in range(seg_n + 1)]
    wl_ = [bp(i / seg_n, 0) for i in range(seg_n + 1)]
    # piers in the water
    for i in range(1, seg_n, 4):
        p0, p1 = bp(i / seg_n, low_bot), bp(i / seg_n + 0.03, low_bot)
        q = [p0, p1, bp(i / seg_n + 0.03, 4), bp(i / seg_n, 4)]
        art.append(F(q, PAPER) + H(U, q, 90, 1.4, 0.7) + sketch(q, 1.0, i, 0.1))
    # lower deck: arcade of restaurants
    low = lt + lb[::-1]
    art.append(F(low, PAPER) + tone(U, low, 3, 80, box=bbox(low), wob=0.2, brk=0.05))
    ar = []
    for i in range(seg_n):
        a0, a1 = bp(i / seg_n, low_top + 4), bp((i + 0.75) / seg_n, low_top + 4)
        b0, b1 = bp(i / seg_n, low_bot), bp((i + 0.75) / seg_n, low_bot)
        ar.append([a0, a1, b1, b0])
    art.append(F(" ".join(poly(q) for q in ar), INK, 0.8))
    art.append(segs([(bp(i / seg_n, low_bot - 9), bp((i + 0.75) / seg_n, low_bot - 9)) for i in range(seg_n)], 0.6, 5, 0, color=PAPER, op=0.8))
    art.append(pen(lb, 1.3, 6, 0.05))
    # road deck fascia and rail
    fas = up + dn[::-1]
    art.append(F(fas, PAPER) + H(U, fas, 0, 1.6, 0.6, box=bbox(fas)) + pen(up, 1.5, 7, 0.05) + pen(dn, 1.3, 8, 0.05))
    rail = [bp(i / seg_n, deck_top - 7) for i in range(seg_n + 1)]
    art.append(pen(rail, 1.0, 9, 0.05) + segs([(bp(i / 80, deck_top), bp(i / 80, deck_top - 7)) for i in range(81)], 0.5, 9, 0))
    # lamp posts, anglers with rods leaning out over the water, a tram
    for i in range(2, seg_n, 5):
        t = i / seg_n
        x0, y0 = bp(t, deck_top)
        sc = lerp(1.0, 0.32, t)
        art.append(seg(x0, y0, x0, y0 - 60 * sc, max(0.8, 1.8 * sc), i, 0) + seg(x0 - 6 * sc, y0 - 60 * sc, x0 + 6 * sc, y0 - 60 * sc, max(0.7, 1.4 * sc), i, 0)
                   + f'<circle cx="{f1(x0 - 6 * sc)}" cy="{f1(y0 - 57 * sc)}" r="{f1(2.2 * sc)}" fill="{INK}"/><circle cx="{f1(x0 + 6 * sc)}" cy="{f1(y0 - 57 * sc)}" r="{f1(2.2 * sc)}" fill="{INK}"/>')
    for i in range(1, 64, 2):
        t = i / 64 + random.Random(i).uniform(-0.004, 0.004)
        x0, y0 = bp(t, deck_top)
        sc = lerp(1.0, 0.32, t)
        art.append(person(x0, y0, 30 * sc, 300 + i, flip=i % 4 == 1))
        rx_, ry_ = x0 - 34 * sc, y0 - 56 * sc
        art.append(P(f"M {f1(x0 - 2 * sc)} {f1(y0 - 20 * sc)} Q {f1(x0 - 20 * sc)} {f1(y0 - 44 * sc)} {f1(rx_)} {f1(ry_)}", max(0.5, 0.9 * sc)))
        if i % 6 == 1:
            art.append(P(f"M {f1(rx_)} {f1(ry_)} L {f1(rx_ - 3 * sc)} {f1(y0 + 40 * sc)}", 0.4, INK, 0.7))
    # a ferry in the foreground and another beyond the bridge; small boats
    art.append(vapur(U, 170, 428, 220, 31))
    art.append(vapur(U, 360, 330, 92, 33, flip=True, flag=False))
    art.append(rowboat(478, 438, 28, 41) + rowboat(80, 352, 18, 42, flip=True) + rowboat(318, 352, 14, 43, fisher=True))
    for i, (x, y, s_) in enumerate(((300, 150, 9), (330, 136, 7), (520, 120, 8), (540, 168, 6), (110, 160, 6), (448, 300, 7), (236, 376, 8), (560, 300, 6))):
        art.append(gull(x, y, s_, 50 + i))
    return plate(U, "istanbul", art, 45)


# ================================================================ NASHVILLE
def uvpoly(m, pts):
    return [m(u, v) for u, v in pts]


def blade3d(U, C, X0, X1, Z, Y0, Y1, icon, seed, acc=False, rays=True):
    """A marquee blade sign standing out from a facade (in the plane Z), lit at dusk: paper panel with a ruled
    double border, a row of bulbs round the edge, rays of light into the dark, and an icon (no lettering)."""
    q = C.qz(Z, X0, X1, Y0, Y1)          # TL, TR, BR, BL
    m = homog(q)
    out = []
    cx, cy = m(0.5, 0.5)
    hh = abs(q[3][1] - q[0][1])
    if rays:
        rl = []
        for i in range(26):
            a = 2 * math.pi * i / 26
            r0, r1 = hh * 0.62, hh * (0.8 + 0.25 * (i % 2))
            rl.append(((cx + math.cos(a) * r0 * 0.6, cy + math.sin(a) * r0), (cx + math.cos(a) * r1 * 0.6, cy + math.sin(a) * r1)))
        out.append(segs(rl, 0.6, seed, 0.1, color=PAPER, op=0.9))
    out.append(F(q, PAPER))
    if acc:
        out.append(accent(U, poly(q), bbox(q), seed, op=1.0, ang=-90, n=16, length=(6, 18), width=(1.5, 3)))
    inner = uvpoly(m, [(0.12, 0.06), (0.88, 0.06), (0.88, 0.94), (0.12, 0.94)])
    out.append(sketch(q, 1.6, seed, 0.3) + sketch(inner, 0.8, seed + 1, 0.2))
    if hh > 18:
        bl = []
        for j in range(9):
            for u in (0.05, 0.95):
                x, y = m(u, 0.08 + 0.84 * j / 8)
                bl.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{max(0.7, hh * 0.012):.2f}"/>')
        out.append(f'<g fill="{INK}">{"".join(bl)}</g>')
    # icons in the panel's own (u, v) space, drawn upright in the middle 60%
    def I(pts):
        return uvpoly(m, [(0.5 + (u - 0.5) * 0.7, 0.5 + (v - 0.5) * 0.62) for u, v in pts])
    if icon == "guitar":
        body = [(0.5, 0.95), (0.28, 0.86), (0.25, 0.72), (0.33, 0.62), (0.3, 0.52), (0.38, 0.45), (0.5, 0.48), (0.62, 0.45), (0.7, 0.52),
                (0.67, 0.62), (0.75, 0.72), (0.72, 0.86)]
        out.append(F(smooth_closed(I(body)), INK, 0.92))
        hx, hy = I([(0.5, 0.72)])[0]
        out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{max(0.8, hh * 0.035):.2f}" fill="{PAPER}"/>')
        out.append(F(I([(0.47, 0.48), (0.53, 0.48), (0.53, 0.12), (0.47, 0.12)]), INK, 0.92))
        out.append(F(I([(0.44, 0.13), (0.56, 0.13), (0.55, 0.02), (0.45, 0.02)]), INK))
    elif icon == "boot":
        out.append(F(I([(0.34, 0.05), (0.6, 0.05), (0.6, 0.62), (0.88, 0.75), (0.9, 0.92), (0.3, 0.92), (0.3, 0.62)]), INK, 0.9))
        out.append(F(I([(0.3, 0.92), (0.4, 0.92), (0.4, 0.98), (0.3, 0.98)]), INK))
        out.append(P(" ".join(f"M {f1(a[0])} {f1(a[1])} L {f1(b[0])} {f1(b[1])}" for a, b in
                              [I([(0.38, 0.2), (0.56, 0.3)]), I([(0.38, 0.3), (0.56, 0.2)])]), 0.8, PAPER))
    elif icon == "star":
        out.append(F(I([(0.5 + math.cos(math.radians(-90 + i * 36)) * (0.45 if i % 2 == 0 else 0.19),
                         0.5 + math.sin(math.radians(-90 + i * 36)) * (0.45 if i % 2 == 0 else 0.19)) for i in range(10)]), INK, 0.9))
    elif icon == "note":
        e = [(0.38 + 0.13 * math.cos(a), 0.82 + 0.08 * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
        out.append(F(I(e), INK, 0.92))
        out.append(F(I([(0.49, 0.82), (0.53, 0.82), (0.53, 0.08), (0.49, 0.08)]), INK))
        out.append(P(smooth_open(I([(0.53, 0.08), (0.72, 0.22), (0.76, 0.4), (0.68, 0.52)])), max(1.0, hh * 0.03)))
    elif icon == "hat":
        out.append(F(smooth_closed(I([(0.1, 0.72), (0.3, 0.62), (0.3, 0.3), (0.5, 0.36), (0.7, 0.3), (0.7, 0.62), (0.9, 0.72), (0.5, 0.78)])), INK, 0.9))
    elif icon == "fiddle":
        body = [(0.5, 0.95), (0.32, 0.88), (0.3, 0.74), (0.38, 0.66), (0.34, 0.56), (0.4, 0.46), (0.5, 0.48), (0.6, 0.46), (0.66, 0.56),
                (0.62, 0.66), (0.7, 0.74), (0.68, 0.88)]
        out.append(F(smooth_closed(I(body)), INK, 0.92))
        out.append(F(I([(0.47, 0.48), (0.53, 0.48), (0.53, 0.14), (0.47, 0.14)]), INK, 0.92))
        out.append(P(smooth_open(I([(0.5, 0.14), (0.56, 0.08), (0.52, 0.03), (0.47, 0.06)])), 1.0))
        out.append(P(" ".join(f"M {f1(a[0])} {f1(a[1])} L {f1(b[0])} {f1(b[1])}" for a, b in [I([(0.15, 0.95), (0.9, 0.35)])]), max(0.8, hh * 0.02)))
    # bracket to the wall
    a, b = C(X1, Y1 + 0.2, Z), C(X1 + (0.6 if X1 > X0 else -0.6), Y1 + 0.2, Z)
    out.append(seg(q[1][0], q[1][1], b[0], b[1], 1.0, seed, 0))
    return "".join(out)


def tonk(U, C, X, Z0, Z1, ht, floors, seed, signs=(), dark=3, lit_p=0.55):
    """A three/four-storey brick honky-tonk front on the plane X (right-hand side, X > 0) at dusk: dark hatched
    brick, tall round-headed windows (some lit), a bracketed cornice, a glowing storefront with a crowd inside."""
    rnd = random.Random(seed)
    out = []
    q = C.qx(X, Z0, Z1, 0, ht)
    out.append(F(q, PAPER))
    out.append(segs([(C(X, y, Z0), C(X, y, Z1)) for y in [0.36 * k for k in range(1, int(ht / 0.36))]], 0.45, seed, 0, op=0.5))
    out.append(tone(U, q, dark, 78, box=bbox(q), wob=0.15, brk=0.05))
    nb = max(2, int((Z1 - Z0) / 2.3))
    bw = (Z1 - Z0) / nb
    lit, dk = [], []
    for f_ in range(floors - 1):
        y0 = 4.6 + f_ * ((ht - 5.6) / (floors - 1))
        y1 = y0 + (ht - 5.6) / (floors - 1) * 0.68
        for b in range(nb):
            za, zb = Z0 + b * bw + bw * 0.28, Z0 + (b + 1) * bw - bw * 0.28
            pts = [C(X, y0, za), C(X, y1 - (zb - za) * 0.5, za)] + [C(X, y1 - (zb - za) * 0.5 + math.sin(t * math.pi) * (zb - za) * 0.5, lerp(za, zb, t))
                                                                    for t in [i / 8 for i in range(1, 8)]] + [C(X, y1 - (zb - za) * 0.5, zb), C(X, y0, zb)]
            (lit if rnd.random() < lit_p else dk).append(pts)
    if dk:
        out.append(F(" ".join(poly(p) for p in dk), INK, 0.9))
    if lit:
        out.append(F(" ".join(poly(p) for p in lit), PAPER))
        out.append(P(" ".join(poly(p) for p in lit), 0.9))
        out.append(segs([(pt(p[0], p[-1], 0.5), pt(p[1], p[-2], 0.5)) for p in lit] + [(pt(p[0], p[1], 0.55), pt(p[-1], p[-2], 0.55)) for p in lit], 0.6, seed, 0))
    # cornice
    cor = [C(X, ht, Z0), C(X, ht, Z1), C(X - 0.5, ht + 0.8, Z1), C(X - 0.5, ht + 0.8, Z0)]
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.3, 0.7) + sketch(cor, 1.2, seed, 0.2))
    out.append(segs([(C(X - 0.3, ht + 0.1, z), C(X - 0.3, ht - 0.5, z)) for z in [Z0 + (i + 0.5) * (Z1 - Z0) / (nb * 2) for i in range(nb * 2)]], 1.3, seed, 0))
    # glowing storefront with the crowd silhouetted inside, transom and sign band above
    sf = C.qx(X, Z0 + 0.4, Z1 - 0.4, 0.3, 3.4)
    out.append(F(sf, PAPER))
    m = homog(sf)
    mul = [(m(u, 0), m(u, 1)) for u in [i / max(2, nb * 2) for i in range(1, nb * 2)]]
    out.append(segs(mul, 0.9, seed, 0) + segs([(m(0, 0.22), m(1, 0.22))], 0.8, seed, 0))
    for i in range(int(nb * 3)):
        u = rnd.uniform(0.05, 0.95)
        hx, hy = m(u, 1.0)
        top = m(u, 0.3)
        hgt = (hy - top[1]) * rnd.uniform(0.8, 1.0)
        out.append(person(hx, hy, hgt, seed * 3 + i, op=0.9, flip=rnd.random() < 0.5))
    out.append(sketch(sf, 1.2, seed, 0.2))
    band = C.qx(X, Z0 + 0.2, Z1 - 0.2, 3.5, 4.3)
    out.append(F(band, INK, 0.9) + segs([(pt(band[0], band[3], 0.5), pt(band[1], band[2], 0.5))], 0.8, seed, 0, color=PAPER))
    # glow spilling on the sidewalk in front
    out.append(pen([C(X, 0, Z0), C(X, ht, Z0)], 1.4, seed, 0.1))
    return "".join(out)


@design("nashville")
def nashville(U):
    """Lower Broadway at dusk from a street corner: a row of brick honky-tonks receding toward the river, their
    marquee blade signs (guitar, boot in vermilion, star, note, fiddle, hat) lit against the darkening sky; glowing
    storefronts, crowds on the sidewalk, a busker with his guitar case open, the twin-spired tower beyond."""
    art = []
    C = YCam(f=420, cx=440, vpy=330, eye=1.6, yaw=0.45)
    # dusk sky: dense hatching, darker toward the top, a crescent moon and a few stars
    sky = rect(0, 0, 600, 330)
    art.append(H(U, sky, 0, (1.8, 4.2), (0.9, 0.6), dark=(300, 0), wob=0.15, brk=0.1))
    art.append(H(U, rect(0, 0, 600, 200), 70, (2.4, 6.0), 0.6, dark=(300, 0), op=0.7, wob=0.15, brk=0.1, span=(0, 0.6)))
    art.append(F(smooth_closed([(112, 84), (120, 82), (128, 90), (130, 100), (124, 108), (114, 110), (121, 101), (122, 92)]), PAPER))
    rnd = random.Random(3)
    for i in range(26):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 220)
        r = rnd.uniform(0.8, 1.8)
        art.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{r:.1f}" fill="{PAPER}"/>')
    # the twin-spired tower far up the street (pale against the sky)
    tx = 212
    tw_ = rect(tx - 16, 150, tx + 16, 312)
    art.append(F(tw_, PAPER) + segs([((tx - 16 + i * 4, 156), (tx - 16 + i * 4, 312)) for i in range(1, 8)], 0.5, 4, 0, op=0.7)
               + segs([((tx - 16, 156 + j * 6), (tx + 16, 156 + j * 6)) for j in range(26)], 0.45, 5, 0, op=0.5)
               + H(U, tw_, 90, 2.6, 0.6, op=0.8) + H(U, rect(tx + 4, 150, tx + 16, 312), 0, 1.8, 0.6) + sketch(tw_, 1.1, 6, 0.3))
    rl = random.Random(12)
    art.append(F(" ".join(poly(rect(tx - 14 + 4 * rl.randint(0, 7), 158 + 6 * rl.randint(0, 24), tx - 12 + 4 * rl.randint(0, 7) + 0.1, 161 + 6 * rl.randint(0, 24)))
                          for _ in range(0)), PAPER))
    art.append("".join(f'<rect x="{tx - 15 + 4 * rl.randint(0, 7)}" y="{158 + 6 * rl.randint(0, 24)}" width="2.4" height="3" fill="{PAPER}"/>' for _ in range(40)))
    for sx_ in (tx - 11, tx + 11):
        sp = [(sx_ - 3, 150), (sx_, 98), (sx_ + 3, 150)]
        art.append(F(sp, PAPER) + pen(sp, 1.1, 7, 0.05))
    art.append(F([(tx - 16, 150), (tx - 8, 140), (tx, 128), (tx + 8, 140), (tx + 16, 150)], PAPER) + pen([(tx - 16, 150), (tx - 8, 140), (tx, 128), (tx + 8, 140), (tx + 16, 150)], 1.1, 8, 0.05))
    # far side of the street (left): darker brick fronts seen edge-on, a few lit windows, their own blade signs
    for i, (z0, z1, ht, fl) in enumerate(((150, 260, 11, 3), (118, 150, 13, 4), (90, 118, 10.5, 3), (72, 90, 14, 4), (56, 72, 11, 3),
                                          (40, 56, 14, 4))):
        art.append(tonk(U, C, -9, z0, z1, ht, fl, 20 + i * 3, dark=3, lit_p=0.4))
    for i, (z, icon) in enumerate(((44, "star"), (66, "note"), (100, "guitar"))):
        art.append(blade3d(U, C, -9.0, -7.0, z, 5.0, 8.6, icon, 30 + i, rays=True))
    # the street: asphalt in dark hatching with streaks of reflected light, centre dashes
    road = [C(-9, 0, 2), C(-9, 0, 260), C(6, 0, 260), C(6, 0, 2)]
    art.append(F(road, PAPER) + tone(U, road, 3, 2, box=(0, 300, 600, 500), wob=0.3, brk=0.15))
    # wet-street reflections of the lamps and lit storefronts: broken vertical streaks of bare paper
    rf = []
    rnd_ = random.Random(39)
    for z in (9, 19, 31, 46, 68, 14, 25, 37, 51):
        for X in (5.6, 4.6):
            a = C(X, 0, z)
            L = C.f * 1.6 / C.depth(X, z)
            y = a[1] + 1
            while y < a[1] + L:
                l_ = rnd_.uniform(2, 6)
                rf.append(((a[0] + rnd_.uniform(-1.2, 1.2), y), (a[0] + rnd_.uniform(-1.2, 1.2), y + l_)))
                y += l_ + rnd_.uniform(1, 3)
    art.append(segs(rf, 1.3, 38, 0.2, color=PAPER, op=0.85))
    art.append(segs([(C(-1.5, 0, z), C(-1.5, 0, z + 2.5)) for z in range(4, 140, 6)], 1.4, 40, 0, color=PAPER))
    # near sidewalk (right) lit by the storefronts
    walk = [C(6, 0.15, 2), C(6, 0.15, 260), C(9, 0.15, 260), C(9, 0.15, 2)]
    art.append(F(walk, PAPER) + segs([(C(6, 0.15, z), C(9, 0.15, z)) for z in [2 + i * 1.4 for i in range(80)]], 0.55, 41, 0, op=0.6))
    art.append(pen([C(6, 0.15, 2), C(6, 0.15, 260)], 1.6, 42, 0.05) + pen([C(6, 0, 2), C(6, 0, 260)], 1.0, 43, 0.05))
    # the honky-tonk row on the right, far to near
    row = [(110, 160, 12, 3), (84, 110, 14, 4), (64, 84, 11, 3), (48, 64, 15, 4), (34, 48, 12, 3), (22, 34, 14.5, 4), (12, 22, 12, 3), (2, 12, 15, 4)]
    for i, (z0, z1, ht, fl) in enumerate(row):
        art.append(tonk(U, C, 9, z0, z1, ht, fl, 50 + i * 3, dark=3))
    signs = [(14.5, "fiddle", False, 6.0, 11.0), (25.0, "boot", True, 5.2, 10.4), (37.5, "guitar", False, 5.0, 10.6), (51, "star", False, 5.2, 9.6),
             (67, "note", False, 5.0, 9.2), (87, "hat", False, 5.5, 10.0)]
    for i, (z, icon, acc, y0, y1) in reversed(list(enumerate(signs))):
        art.append(blade3d(U, C, 6.6, 8.9, z, y0, y1, icon, 60 + i, acc=acc))
    # crowds on the near sidewalk, a busker on the corner, a pedicab passing
    rnd = random.Random(70)
    for i in range(22):
        z = 5 + rnd.random() ** 1.3 * 70
        X = rnd.uniform(6.6, 8.6)
        x, y = C(X, 0.15, z)
        art.append(walker(x, y, C.f * 1.7 / C.depth(X, z), 80 + i, flip=rnd.random() < 0.5, kind=rnd.choice(("plain", "plain", "dress", "hat"))))
    x, y = C(6.9, 0.15, 3.6)
    art.append(icf.busker(x, y, C.f * 1.75 / C.depth(6.9, 3.6), 99))
    for i in range(10):
        z = 20 + rnd.random() * 60
        X = rnd.uniform(-8.8, -7.4)
        x, y = C(X, 0.15, z)
        art.append(walker(x, y, C.f * 1.7 / C.depth(X, z), 120 + i, flip=True, op=0.95))
    # lamp posts along the curb, crossing walkers in the foreground
    for z in (9, 19, 31, 46, 68):
        x, y = C(6.3, 0.15, z)
        art.append(lamp(x, y, C.f * 5.0 / C.depth(6.3, z), 140 + z, "globe", max(1.0, min(2.4, 70 / C.depth(6.3, z)))))
    cw = [[C(-9 + i * 1.3, 0, 10.5), C(-8.4 + i * 1.3, 0, 10.5), C(-8.4 + i * 1.3, 0, 13.0), C(-9 + i * 1.3, 0, 13.0)] for i in range(12)]
    art.append(F(" ".join(poly(c) for c in cw), PAPER, 0.92))
    for i, (X, z, kind) in enumerate(((-2.0, 11.6, "dress"), (-1.2, 11.3, "plain"), (-5.6, 12.2, "hat"), (1.2, 11.9, "bag"), (3.4, 12.4, "plain"))):
        x, y = C(X, 0, z)
        art.append(walker(x, y, C.f * 1.7 / C.depth(X, z), 150 + i, flip=i % 2 == 0, kind=kind))
    return plate(U, "nashville", art, 55)


# ================================================================ BOSTON
BOS_G = 0.075        # Acorn Street rises gently away from us


def bg(Z):
    return BOS_G * max(0.0, Z)


def river_stones(U, C, X0, X1, Z0, Z1, seed, row=0.24):
    """Rounded river-stone paving in perspective: dark joints under irregular paper stones, each with a shaded
    lower lip near us; rows of scalloped strokes in the distance."""
    rnd = random.Random(seed)
    out_f, out_s, far = [], [], []
    Z = Z0
    k = 0
    while Z < Z1:
        z2 = Z + row * rnd.uniform(0.85, 1.15) * (1 + Z * 0.02)
        a, b = C(X0, bg(Z), Z), C(X1, bg(Z), Z)
        sw = C.f * row / Z
        if sw > 3.4:
            X = X0 - rnd.uniform(0, row)
            while X < X1:
                w_ = row * rnd.uniform(0.6, 1.25)
                zc = (Z + z2) / 2 + rnd.uniform(-0.04, 0.04)
                cx_, cy_ = C(X + w_ / 2, bg(zc), zc)
                rx = C.f * w_ * 0.44 / zc
                ry = max(0.8, (C(0, bg(Z), Z)[1] - C(0, bg(z2), z2)[1]) * rnd.uniform(0.36, 0.46))
                ph = rnd.uniform(0, 6.28)
                pts = [(cx_ + rx * math.cos(t) * (1 + 0.12 * math.sin(2 * t + ph)), cy_ + ry * math.sin(t) * (1 + 0.1 * math.cos(3 * t + ph)))
                       for t in [i * math.pi / 7 for i in range(14)]]
                out_f.append(smooth_closed(pts))
                if rx > 2.4:
                    out_s.append(f"M {f1(cx_ - rx * 0.75)} {f1(cy_ + ry * 0.35)} Q {f1(cx_)} {f1(cy_ + ry * 1.15)} {f1(cx_ + rx * 0.75)} {f1(cy_ + ry * 0.35)}")
                    out_s.append(f"M {f1(cx_ - rx * 0.5)} {f1(cy_ + ry * 0.62)} Q {f1(cx_)} {f1(cy_ + ry * 0.95)} {f1(cx_ + rx * 0.5)} {f1(cy_ + ry * 0.62)}")
                X += w_ * rnd.uniform(1.0, 1.08)
        else:
            n = max(3, int(abs(b[0] - a[0]) / 3))
            dd = [f"M {f1(a[0])} {f1(a[1])}"]
            for i in range(n):
                p0, p1 = pt(a, b, i / n), pt(a, b, (i + 1) / n)
                dd.append(f"Q {f1((p0[0] + p1[0]) / 2)} {f1(p0[1] + 1.4)} {f1(p1[0])} {f1(p1[1])}")
            far.append(" ".join(dd))
        Z = z2
        k += 1
    out = []
    if out_f:
        zl = min(Z1, C.f * row / 3.4)
        joint = [C(X0, bg(zl), zl), C(X1, bg(zl), zl), C(X1, bg(Z0), Z0), C(X0, bg(Z0), Z0)]
        out.append(F(joint, INK, 0.55))
        out.append(f'<path d="{" ".join(out_f)}" fill="{PAPER}" stroke="{INK}" stroke-width="0.8"/>')
    if out_s:
        out.append(P(" ".join(out_s), 0.8, INK, 0.85))
    if far:
        out.append(P(" ".join(far), 0.6, INK, 0.8))
    return "".join(out)


def brick_courses(U, C, X, Z0, Z1, y0, y1, seed, course=0.2, op=0.45):
    """Perspective brick on the plane X: bed joints and staggered head joints where they are large enough."""
    rnd = random.Random(seed)
    lines, joints = [], []
    y = y0 + course
    k = 0
    while y < y1:
        a, b = C(X, y, Z0), C(X, y, Z1)
        lines.append((a, b))
        z = Z0 + (k % 2) * 0.12
        while z < Z1:
            p0 = C(X, y, z)
            p1 = C(X, y - course, z)
            if abs(C(X, y, z + 0.24)[0] - p0[0]) > 3.2:
                joints.append((p0, p1))
            z += 0.24
        y += course
        k += 1
    return segs(lines, 0.45, seed, 0.05, op=op) + segs(joints, 0.45, seed + 1, 0, op=op * 0.8)


def rowhouse(U, C, X, Z0, Z1, ht, seed, acc=False, door_at=0.22, box=True):
    """A Beacon Hill brick rowhouse on the plane X (right side of the lane, X > 0): brick courses, 6-over-6 sash
    windows with dark louvered shutters and granite lintels, a panelled door with a fanlight up granite steps,
    window boxes, a dentil cornice, a slate roof with a dormer."""
    rnd = random.Random(seed)
    out = []
    yb = bg(Z0)
    q = C.qx(X, Z0, Z1, yb - 0.2, yb + ht)
    out.append(F(q, PAPER))
    out.append(brick_courses(U, C, X, Z0, Z1, yb - 0.2, yb + ht, seed, op=0.5 if Z0 < 20 else 0.35))
    out.append(H(U, q, 80, 4.2, 0.55, op=0.5, wob=0.2, brk=0.2))
    W = Z1 - Z0
    # granite base course
    base = C.qx(X, Z0, Z1, bg(Z1) - 0.2, yb + 0.6)
    out.append(F([C(X, yb + 0.6, Z0), C(X, yb + 0.6, Z1), C(X, bg(Z1) - 0.05, Z1), C(X, bg(Z0) - 0.05, Z0)], PAPER)
               + H(U, [C(X, yb + 0.6, Z0), C(X, yb + 0.6, Z1), C(X, bg(Z1), Z1), C(X, bg(Z0), Z0)], 0, 1.6, 0.6, op=0.7))
    # door with fanlight + steps
    za, zb = Z0 + W * door_at, Z0 + W * door_at + 1.1
    dq = C.qx(X, za, zb, yb + 0.7, yb + 3.0)
    if acc:
        out.append(F(dq, PAPER) + accent(U, poly(dq), bbox(dq), seed, op=1.0, ang=-88, n=18, length=(8, 20), width=(1.5, 3))
                   + H(U, dq, 80, 2.2, 0.6, op=0.7))
        mm = homog(dq)
        out.append(segs([(mm(u, 0.08), mm(u, 0.45)) for u in (0.15, 0.85)] + [(mm(u, 0.55), mm(u, 0.92)) for u in (0.15, 0.85)]
                        + [(mm(0.15, v), mm(0.85, v)) for v in (0.08, 0.45, 0.55, 0.92)], 0.6, seed, 0))
    else:
        out.append(F(dq, INK, 0.92))
    m = homog(dq)
    out.append(segs([(m(0.5, 0.05), m(0.5, 0.95)), (m(0.1, 0.5), m(0.9, 0.5))], 0.7, seed, 0, color=PAPER, op=0.6))
    fan = [C(X, yb + 3.0 + math.sin(t * math.pi) * 0.5, lerp(za, zb, t)) for t in [i / 10 for i in range(11)]]
    out.append(F(fan, PAPER) + pen(fan, 1.0, seed, 0.05) + segs([(C(X, yb + 3.0, (za + zb) / 2), f_) for f_ in fan[1:-1:2]], 0.5, seed, 0))
    surround = C.qx(X - 0.06, za - 0.2, zb + 0.2, yb + 0.6, yb + 3.7)
    out.append(sketch(surround, 1.0, seed, 0.1))
    for k in range(3):
        st = [C(X - 0.35 * (3 - k), yb + 0.2 * k, za - 0.3), C(X - 0.35 * (3 - k), yb + 0.2 * k, zb + 0.3),
              C(X - 0.35 * (3 - k), yb + 0.2 * (k + 1), zb + 0.3), C(X - 0.35 * (3 - k), yb + 0.2 * (k + 1), za - 0.3)]
        top = [C(X - 0.35 * (3 - k), yb + 0.2 * (k + 1), za - 0.3), C(X - 0.35 * (3 - k), yb + 0.2 * (k + 1), zb + 0.3),
               C(X, yb + 0.2 * (k + 1), zb + 0.3), C(X, yb + 0.2 * (k + 1), za - 0.3)]
        out.append(F(top, PAPER) + pen(top, 0.8, seed + k, 0.05, True) + F(st, PAPER) + H(U, st, 0, 1.2, 0.6))
    # windows: ground floor + 2 floors, two or three bays
    bays = [z for z in (Z0 + W * 0.58, Z0 + W * 0.84) if z + 0.6 < Z1] if door_at < 0.4 else [Z0 + W * 0.18]
    rows = [(1.0, 2.7), (4.0, 6.2), (7.2, 9.2)] if ht > 10 else [(1.0, 2.7), (4.0, 6.0)]
    for j, (y0, y1) in enumerate(rows):
        zs = bays if j == 0 else sorted(set([Z0 + W * door_at + 0.55] + bays))
        for zc in zs:
            w0, w1 = zc - 0.45, zc + 0.45
            wq = C.qx(X, w0, w1, yb + y0, yb + y1)
            out.append(F(wq, INK, 0.85))
            m = homog(wq)
            out.append(segs([(m(1 / 3, 0), m(1 / 3, 1)), (m(2 / 3, 0), m(2 / 3, 1)), (m(0, 0.5), m(1, 0.5)), (m(0, 0.25), m(1, 0.25)),
                             (m(0, 0.75), m(1, 0.75))], 0.55, seed, 0, color=PAPER, op=0.75))
            for sa, sb in ((w0 - 0.5, w0 - 0.05), (w1 + 0.05, w1 + 0.5)):
                sq = C.qx(X - 0.03, sa, sb, yb + y0, yb + y1)
                if abs(sq[1][0] - sq[0][0]) > 1.5:
                    out.append(louvered(U, sq, seed + int(sa * 10), dark=True, w=0.5))
            lt = C.qx(X - 0.05, w0 - 0.1, w1 + 0.1, yb + y1, yb + y1 + 0.28)
            out.append(F(lt, PAPER) + sketch(lt, 0.8, seed, 0.1))
            if box and j == 0:
                bx = [C(X - 0.3, yb + y0 - 0.05, w0 - 0.1), C(X - 0.3, yb + y0 - 0.05, w1 + 0.1), C(X - 0.3, yb + y0 - 0.45, w1 + 0.1), C(X - 0.3, yb + y0 - 0.45, w0 - 0.1)]
                out.append(F(bx, PAPER) + H(U, bx, 0, 1.3, 0.6) + sketch(bx, 0.8, seed, 0.1))
                fl = []
                for t in [i / 7 for i in range(8)]:
                    fx, fy = pt(bx[0], bx[1], t)
                    rr = max(1.2, abs(bx[1][0] - bx[0][0]) / 9)
                    fl.append((fx, fy - rr * 0.5, rr))
                d = " ".join(smooth_closed(scallop_pts(fx, fy, rr, rr * 0.8, int(fx), 7, 0.2)) for fx, fy, rr in fl)
                out.append(F(d, PAPER))
                if acc:
                    out.append(accent(U, d, bbox([(fx, fy) for fx, fy, _ in fl], 8), seed, op=1.0, ang=-40, n=14, length=(3, 8), width=(1.4, 2.6)))
                out.append(P(d, 0.7))
    # cornice + roof + dormer
    cor = C.qx(X - 0.3, Z0, Z1, yb + ht - 0.5, yb + ht)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.2, 0.6) + sketch(cor, 1.1, seed, 0.2))
    out.append(segs([(C(X - 0.3, yb + ht - 0.5, z), C(X - 0.3, yb + ht - 0.75, z)) for z in [Z0 + i * 0.25 for i in range(int(W / 0.25))]], 0.8, seed, 0))
    roof = [C(X - 0.3, yb + ht, Z0), C(X - 0.3, yb + ht, Z1), C(X + 2.2, yb + ht + 2.4, Z1), C(X + 2.2, yb + ht + 2.4, Z0)]
    out.append(F(roof, PAPER) + H(U, roof, 0, 2.0, 0.7) + pen([roof[0], roof[1]], 1.3, seed, 0.05))
    dq = C.qx(X + 0.6, Z0 + W * 0.4, Z0 + W * 0.68, yb + ht + 0.4, yb + ht + 1.9)
    out.append(F(dq, PAPER) + F(C.qx(X + 0.6, Z0 + W * 0.46, Z0 + W * 0.62, yb + ht + 0.6, yb + ht + 1.6), INK, 0.85) + sketch(dq, 0.9, seed, 0.1))
    pk = C(X + 0.6, yb + ht + 2.5, Z0 + W * 0.54)
    out.append(F([dq[0], pk, dq[1]], PAPER) + pen([dq[0], pk, dq[1]], 1.0, seed, 0.05))
    out.append(pen([C(X, yb - 0.2, Z0), C(X, yb + ht, Z0)], 1.4, seed, 0.1))
    return "".join(out)


@design("boston")
def boston(U):
    """Acorn Street on Beacon Hill on an autumn morning, looking up the lane: river-stone cobbles between a row of
    brick houses with black shutters, granite steps and fanlit doors (one window box of red geraniums, the accent)
    and a garden wall with arched gates in shade, house backs above it; gas lamps, a man walking his bike, a woman
    and her dog, elms over the top of the hill."""
    art = []
    C = Cam(f=262, cx=300, vpy=300, eye=1.6)
    Z0, ZE = 3.2, 52
    art.append(cloud(U, 330, 92, 92, 13, 61))
    art.append(cloud(U, 170, 132, 60, 9, 62))
    # elms closing the top of the lane, behind the far house
    for i, (x, y, r) in enumerate(((262, 214, 30), (304, 196, 36), (348, 212, 30), (228, 236, 22), (384, 236, 22))):
        art.append(lobe(U, x, y, r, r * 0.74, 700 + i, light=(-1, -1), w=1.2, dense=1.3))
    # the house that closes the far end
    fe = C.qz(ZE, -3.2, 2.9, bg(ZE), bg(ZE) + 9.5)
    art.append(F(fe, PAPER) + brick_courses(U, C, 0, ZE, ZE, 0, 0, 1)
               + window_grid(U, fe[0][0] + 3, fe[1][0] - 3, fe[0][1] + 5, fe[3][1] - 4, 4, 3, 66, dark=0.8)
               + H(U, fe, 90, 2.6, 0.5, op=0.7) + sketch(fe, 1.1, 67, 0.2))
    # the lane: river stones, brick sidewalk, granite curb
    lane = [C(-2.0, bg(ZE), ZE), C(1.6, bg(ZE), ZE), C(1.6, bg(Z0), Z0 - 2.5), C(-2.0, bg(Z0), Z0 - 2.5)]
    art.append(F(lane, PAPER))
    art.append(clipped(U("ln"), poly(lane), river_stones(U, C, -2.0, 1.6, Z0 - 1.0, ZE, 3, row=0.2)))
    art.append(H(U, [C(-2.0, bg(ZE), ZE), C(-0.9, bg(ZE), ZE), C(-0.3, 0, 1.0), C(-2.0, 0, 1.0)], 75, 2.6, 0.7, op=0.7))
    walk = [C(1.6, bg(ZE) + 0.14, ZE), C(2.8, bg(ZE) + 0.14, ZE), C(2.8, 0.14, 1.0), C(1.6, 0.14, 1.0)]
    art.append(F(walk, PAPER) + clipped(U("wk"), poly(walk), segs([(C(1.6, bg(z) + 0.14, z), C(2.8, bg(z) + 0.14, z))
                                                                  for z in [1.0 + i * 0.22 for i in range(232)]], 0.5, 4, 0, op=0.55)))
    art.append(pen([C(1.6, 0.14, 1.5), C(1.6, bg(ZE) + 0.14, ZE)], 1.5, 5, 0.05) + pen([C(1.6, 0, 1.5), C(1.6, bg(ZE), ZE)], 0.9, 6, 0.05))
    # left: house backs set back behind the garden wall, in shade
    for i, (z0, z1, ht) in enumerate(((36, ZE, 10.5), (24, 36, 12), (13, 24, 11.5))):
        hb = C.qx(-6.0, z0, z1, bg(z0), bg(z0) + ht)
        win = C.qx(-6.0, z0 + 0.6, z1 - 0.6, bg(z0) + 4.6, bg(z0) + ht - 1.2)
        art.append(F(hb, PAPER) + brick_courses(U, C, -6.0, z0, z1, bg(z0), bg(z0) + ht, 80 + i, op=0.35)
                   + facade(U, win, max(2, int((z1 - z0) / 2.4)), 2, "pane", 81 + i, dark_p=0.7, w=0.8)
                   + tone(U, hb, 2, 70, box=bbox(hb)) + sketch(hb, 1.1, 82 + i, 0.2))
        cor = C.qx(-5.8, z0, z1, bg(z0) + ht - 0.4, bg(z0) + ht)
        art.append(F(cor, PAPER) + H(U, cor, 0, 1.3, 0.6) + sketch(cor, 0.9, 83 + i, 0.1))
        rf = [C(-6.0, bg(z0) + ht, z0), C(-6.0, bg(z0) + ht, z1), C(-8.0, bg(z0) + ht + 2.2, z1), C(-8.0, bg(z0) + ht + 2.2, z0)]
        art.append(F(rf, PAPER) + H(U, rf, 0, 1.8, 0.7) + sketch(rf, 1.0, 84 + i, 0.2))
    # garden trees over the wall (near), framing the left of the picture
    for i, (z, X, h, w) in enumerate(((16, -4.2, 9.5, 7.0), (9.0, -4.0, 9.0, 6.4), (4.6, -4.4, 8.5, 6.0))):
        x, y = C(X, bg(z) + 1.2, z)
        art.append(tree(U, x, y, C.f * h / z, C.f * w / z, 760 + i, light=(-1, -1), trunk_h=0.3, lobes=7,
                        lw=max(1.1, min(2.0, 18 / z)), dense=1.1))
    wh = 2.6
    zw = 2.0
    wall = [C(-2.0, bg(ZE) + wh, ZE), C(-2.0, bg(zw) + wh, zw), C(-2.0, 0, zw), C(-2.0, bg(ZE), ZE)]
    art.append(F(wall, PAPER) + brick_courses(U, C, -2.0, zw, ZE, 0, wh + 0.2, 90, op=0.5) + tone(U, wall, 2, 72, box=bbox(wall)))
    cap = [C(-2.0, bg(ZE) + wh, ZE), C(-2.0, wh, zw), C(-2.25, wh + 0.2, zw), C(-2.25, bg(ZE) + wh + 0.2, ZE)]
    art.append(F(cap, PAPER) + pen([cap[0], cap[1]], 1.8, 91, 0.05) + pen([cap[3], cap[2]], 1.0, 92, 0.05))
    for z in (5.4, 15, 28):
        gq = C.qx(-1.99, z, z + 1.0, bg(z), bg(z) + 1.95)
        arch = [C(-1.99, bg(z) + 1.95 + math.sin(t * math.pi) * 0.35, lerp(z, z + 1.0, t)) for t in [i / 8 for i in range(9)]]
        door = [gq[3], gq[2]] + arch[::-1]
        art.append(F(door, INK, 0.92) + segs([(pt(gq[0], gq[1], t), pt(gq[3], gq[2], t)) for t in (0.33, 0.66)], 0.6, int(z), 0,
                                              color=PAPER, op=0.5))
        sur = [C(-1.97, bg(z) + 1.95 + math.sin(t * math.pi) * 0.35 + 0.2, lerp(z - 0.15, z + 1.15, t)) for t in [i / 8 for i in range(9)]]
        art.append(pen(sur, 1.2, int(z), 0.05))
    # a downspout, an iron boot-scraper grille and curtains of ivy down the near wall
    a, b = C(-1.95, 0, 3.6), C(-1.95, wh, 3.6)
    art.append(seg(a[0], a[1], b[0], b[1], 3.2, 93, 0) + seg(a[0] + 1.5, a[1], b[0] + 1.5, b[1], 0.8, 94, 0, color=PAPER))
    rnd = random.Random(95)
    for z0_, z1_, drop in ((2.2, 3.2, 1.6), (6.8, 8.2, 1.2), (10.5, 11.4, 0.9)):
        leaves = []
        for _ in range(int(60 / z0_ * 9)):
            z = rnd.uniform(z0_, z1_)
            yy = wh - rnd.uniform(0, drop) * rnd.random()
            x, y = C(-1.98, bg(z) + yy, z)
            r = C.f * 0.032 / z
            leaves.append(smooth_closed(scallop_pts(x, y, r, r * 0.8, rnd.randint(0, 9999), 5, 0.3)))
        art.append(F(" ".join(leaves), INK, 0.85))
    # ivy tumbling over the wall
    for i, (z, n) in enumerate(((3.0, 3), (7.5, 3), (12, 3), (21, 4), (33, 3))):
        x, y = C(-2.1, bg(z) + wh + 0.1, z)
        r = C.f * 0.5 / z
        for j in range(n):
            art.append(lobe(U, x + j * r * 0.9, y + r * (0.15 + 0.35 * (j % 2)), r * 0.85, r * 0.6, 800 + i * 9 + j,
                            light=(1, -1), w=max(0.8, min(1.4, r / 14)), dense=1.4))
        if i == 0:
            vines = [f"M {f1(x + r * k)} {f1(y)} q {f1(r * 0.2)} {f1(r * 1.0)} {f1(-r * 0.1)} {f1(r * (1.4 + k * 0.3))}" for k in (0.4, 1.3, 2.1)]
            art.append(P(" ".join(vines), 0.9))
            for k in range(14):
                vx, vy = x + r * (0.3 + k % 3 * 0.8), y + r * (0.3 + k * 0.12)
                art.append(F(scallop_pts(vx, vy, 2.6, 2.0, 870 + k, 5, 0.3), INK, 0.85))
    # right: the brick row, far to near
    row = [(44, ZE, 9.8, 0.25, False), (37, 44, 11, 0.2, False), (30, 37, 10.2, 0.6, False), (23, 30, 11.2, 0.22, False),
           (16, 23, 10.4, 0.6, False), (9.5, 16, 11.2, 0.2, True), (3.6, 9.5, 10.6, 0.55, False)]
    for i, (z0, z1, ht, door_at, acc) in enumerate(row):
        art.append(rowhouse(U, C, 2.8, z0, z1, ht, 100 + i * 7, acc=acc, door_at=door_at))
    # gas lamps on the sidewalk
    for X, z in ((2.25, 7.4), (2.25, 20.5), (-1.75, 26), (2.25, 34)):
        x, y = C(X, bg(z) + 0.14, z)
        art.append(lamp(x, y, C.f * 3.4 / z, 120 + int(z), "lantern", max(1.0, min(2.6, 30 / z))))
    # life: a woman with her dog, a man walking his bike, two figures up the hill, a cat on the steps
    for X, z, sd, kind, fl in ((0.3, 8.6, 131, "dog", True), (-0.9, 24, 132, "plain", False), (2.2, 29, 133, "dress", True),
                               (0.4, 38, 134, "hat", False)):
        x, y = C(X, bg(z) + (0.14 if X > 1.6 else 0), z)
        art.append(walker(x, y, C.f * 1.68 / z, sd, flip=fl, kind=kind))
    x, y = C(-0.9, bg(14), 14)
    art.append(cyclist(x, y, C.f * 1.7 / 14, 134, flip=True))
    cx_, cy_ = C(2.0, bg(12.6) + 0.55, 12.4)
    s = 0.8
    art.append(F(smooth_closed([(cx_ - 4 * s, cy_), (cx_ + 3 * s, cy_), (cx_ + 3 * s, cy_ - 5 * s), (cx_, cy_ - 8 * s), (cx_ - 3 * s, cy_ - 6 * s)]), INK)
               + F([(cx_ - 1 * s, cy_ - 8 * s), (cx_ - 0.3 * s, cy_ - 11 * s), (cx_ + 1 * s, cy_ - 8 * s)], INK)
               + F([(cx_ + 1 * s, cy_ - 8 * s), (cx_ + 2 * s, cy_ - 11 * s), (cx_ + 2.6 * s, cy_ - 7 * s)], INK)
               + P(f"M {f1(cx_ - 4 * s)} {f1(cy_)} Q {f1(cx_ - 9 * s)} {f1(cy_ - 1)} {f1(cx_ - 8 * s)} {f1(cy_ - 6 * s)}", 1.1))
    art.append(bird(300, 150, 5, 140) + bird(314, 140, 4, 141) + bird(206, 176, 4, 142))
    return plate(U, "boston", art, 65, cy=246, ry=214)


# ================================================================ CHARLESTON
def palmetto(U, x, base, h, seed, lean=0.0, n=24, span=1.0, lw=1.5):
    """A sabal palmetto: a straight grey trunk with a herringbone of leaf-boots under the crown, and a round,
    spiky head of costapalmate leaves, each a folded blade splitting into drooping segments; the leaves behind
    in dark ink, the near ones lit."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    tw = max(2.0, h * 0.04)
    out = []
    left = [(lerp(x, tx, t) - tw * (1.08 - 0.15 * t), lerp(base, ty, t)) for t in [i / 10 for i in range(11)]]
    right = [(lerp(x, tx, t) + tw * (1.08 - 0.15 * t), lerp(base, ty, t)) for t in [i / 10 for i in range(11)]]
    trunk = left + right[::-1]
    out.append(F(trunk, PAPER))
    bt = []
    nb = int(h / 5)
    for i in range(nb):
        t = 0.62 + 0.38 * i / max(1, nb)
        cx_, cy_ = lerp(x, tx, t), lerp(base, ty, t)
        ww = tw * (1.08 - 0.15 * t)
        off = (i % 2) * ww * 0.45
        bt.append(((cx_ - ww * 1.1 + off, cy_ + ww * 0.8), (cx_ - ww * 0.05 + off, cy_ - ww * 0.1)))
        bt.append(((cx_ + ww * 1.1 - off, cy_ + ww * 0.8), (cx_ + ww * 0.05 - off, cy_ - ww * 0.1)))
    ticks = []
    for i in range(int(h / 6)):
        t = rnd.uniform(0.02, 0.6)
        cx_, cy_ = lerp(x, tx, t), lerp(base, ty, t)
        ticks.append(((cx_ - tw, cy_), (cx_ - tw * rnd.uniform(0.3, 0.7), cy_ + 0.6)))
    out.append(clipped(U("pm"), poly(trunk), segs(bt, 0.9, seed, 0.3) + segs(ticks, 0.6, seed + 1, 0.2)
                       + H(U, [pt(l_, r_, 0.45) for l_, r_ in zip(left, right)] + right[::-1], 88, 1.5, 0.7, wob=0.1, brk=0.1)
                       + H(U, [pt(l_, r_, 0.75) for l_, r_ in zip(left, right)] + right[::-1], 20, 1.6, 0.6, wob=0.1, brk=0.1)))
    out.append(pen(left, lw * 0.9, seed, 0.3, smooth=True) + pen(right, lw * 1.3, seed + 1, 0.3, smooth=True))
    # crown
    R = h * 0.33 * span
    out.append(F(smooth_closed(scallop_pts(tx, ty + R * 0.06, R * 0.34, R * 0.27, seed, 14, 0.3)), INK, 0.8))
    out.append(F(smooth_closed(scallop_pts(tx, ty + R * 0.04, R * 0.2, R * 0.16, seed, 9, 0.25)), INK, 0.92))
    leaves = []
    for k in range(n):
        a = -math.pi * 1.12 + math.pi * 1.24 * (k + rnd.uniform(-0.3, 0.3)) / (n - 1)
        back = rnd.random() < 0.3
        L = R * rnd.uniform(0.82, 1.08)
        leaves.append((back, a, L))
    for k in range(6):
        a = math.pi * rnd.uniform(0.18, 0.82)
        leaves.append((True, a, R * rnd.uniform(0.55, 0.7)))
    leaves.sort(key=lambda l: not l[0])
    for back, a, L in leaves:
        ca, sa = math.cos(a), math.sin(a)
        E = (tx + ca * L * 0.32, ty + sa * L * 0.32 + L * 0.04)
        out.append(nib([(tx, ty), ((tx + E[0]) / 2, (ty + E[1]) / 2 - L * 0.03), E], max(1.2, lw), taper=(1, 0.5), seed=seed, color=INK))
        m = 11
        spread = 0.5
        segs_d, inner = [], []
        for j in range(m):
            aa = a + spread * (2 * j / (m - 1) - 1)
            r = L * 0.68 * (1 - 0.25 * abs(2 * j / (m - 1) - 1)) * rnd.uniform(0.9, 1.08)
            dro = r * (0.06 + 0.22 * abs(math.cos(aa))) * (1.8 if sa > 0.2 else 1.0)
            c1 = (E[0] + math.cos(aa) * r * 0.55, E[1] + math.sin(aa) * r * 0.55 - r * 0.04)
            e1 = (E[0] + math.cos(aa) * r * 0.95, E[1] + math.sin(aa) * r * 0.95 + dro)
            segs_d.append(f"M {f1(E[0])} {f1(E[1])} Q {f1(c1[0])} {f1(c1[1])} {f1(e1[0])} {f1(e1[1])}")
            inner.append((E[0] + math.cos(aa) * r * 0.6, E[1] + math.sin(aa) * r * 0.6 + dro * 0.3))
        blade = [E] + inner
        if back:
            out.append(F(blade, INK, 0.9) + P(" ".join(segs_d), 1.1, INK, 0.85))
        else:
            out.append(F(blade, PAPER) + F(blade, INK, 0.28) + clipped(U("pb"), poly(blade), H(U, blade, math.degrees(a) + 90, 1.5, 0.6, span=(0.0, 1),
                                                                         dark=(E[0] + R, E[1] + R))))
            out.append(P(" ".join(segs_d), 0.85) + pen(blade[:1] + blade[1::2], 0.7, seed, 0.1))
    return "".join(out)


def georgian(U, C, Zf, X0, X1, ht, seed, lvl=1, ang=80, roof="parapet", acc=False, bal=False, shop=False, wins=3,
             floors=3, side=None):
    """One Rainbow Row house, its stuccoed front in the plane Z = Zf (facing us) between X0 (left) and X1: a tonal
    ground standing in for its pastel colour, shuttered sash windows with lintels and sills, a shopfront or an
    arched door, a cornice with dentils and a parapet / hipped roof / curved gable. `side` = height of the
    nearer neighbour: the part of this house's party wall that shows above it is drawn in shade."""
    rnd = random.Random(seed)
    out = []
    q = C.qz(Zf, X0, X1, 0, ht)
    out.append(F(q, PAPER))
    if acc:
        out.append(accent(U, poly(q), bbox(q), seed, op=0.75, ang=-86, n=40, length=(14, 40), width=(2, 4)))
    if lvl:
        out.append(H(U, q, ang, {1: 4.0, 2: 2.6, 3: 2.3}[lvl], 0.7, box=bbox(q), op=0.85, wob=0.15, brk=0.1))
        if lvl >= 3:
            out.append(H(U, q, ang + 70, 3.0, 0.6, box=bbox(q), op=0.75, wob=0.15, brk=0.1))
    else:
        out.append(ST(U, q, int(abs(q[1][0] - q[0][0]) * abs(q[3][1] - q[0][1]) / 120), r=(0.45, 0.9), op=0.6))
    # stucco joints (scored ashlar) on the ground floor
    out.append(segs([(C(X0, y, Zf), C(X1, y, Zf)) for y in (0.8, 1.6, 2.4, 3.2)], 0.45, seed, 0, op=0.5))
    W = X1 - X0
    # upper floors
    rows = [(4.3, 6.4), (7.5, 9.3)][:floors - 1]
    panes, bars, sh_l = [], [], []
    for j, (y0, y1) in enumerate(rows):
        for i in range(wins):
            xc = X0 + W * (i + 0.5) / wins
            w0, w1 = xc - 0.45, xc + 0.45
            wq = C.qz(Zf, w0, w1, y0, y1)
            panes.append(wq)
            mm = homog(wq)
            bars += [(mm(0.5, 0), mm(0.5, 1)), (mm(0, 1 / 3), mm(1, 1 / 3)), (mm(0, 2 / 3), mm(1, 2 / 3))]
            for sa, sb in ((w0 - 0.48, w0 - 0.04), (w1 + 0.04, w1 + 0.48)):
                sq = C.qz(Zf - 0.03, sa, sb, y0, y1)
                out.append(louvered(U, sq, seed + i * 7 + j, dark=(seed + i) % 3 == 0, w=0.5))
            lt = C.qz(Zf - 0.05, w0 - 0.12, w1 + 0.12, y1, y1 + 0.3)
            sl = C.qz(Zf - 0.08, w0 - 0.1, w1 + 0.1, y0 - 0.14, y0)
            out.append(F(lt, PAPER) + sketch(lt, 0.7, seed, 0.1) + F(sl, PAPER) + sketch(sl, 0.6, seed + 1, 0.1))
            # cast shadow of the lintel
            out.append(F(C.qz(Zf - 0.01, w0 - 0.1, w1 + 0.1, y1 - 0.22, y1), INK, 0.35))
    out.append(F(" ".join(poly(p) for p in panes), INK, 0.88))
    out.append(segs(bars, 0.55, seed, 0, color=PAPER, op=0.7))
    # balcony on the 2nd floor
    if bal:
        slab = [C(X0 + 0.3, 4.2, Zf), C(X1 - 0.3, 4.2, Zf), C(X1 - 0.3, 4.2, Zf - 0.8), C(X0 + 0.3, 4.2, Zf - 0.8)]
        out.append(F(slab, INK, 0.85))
        rq = C.qz(Zf - 0.8, X0 + 0.3, X1 - 0.3, 4.2, 5.2)
        out.append(lace(U, rq, max(5, int(W / 0.35)), seed, w=0.6))
        out.append(segs([(C(X0 + 0.3, 4.2, Zf), C(X0 + 0.3, 5.2, Zf - 0.8)), (C(X1 - 0.3, 4.2, Zf), C(X1 - 0.3, 5.2, Zf - 0.8))], 0.7, seed, 0))
        out.append(F(C.qz(Zf - 0.01, X0 + 0.3, X1 - 0.3, 3.6, 4.2), INK, 0.45))
    # ground floor
    if shop:
        sq = C.qz(Zf, X0 + 0.5, X1 - 1.7, 0.4, 3.2)
        out.append(F(sq, INK, 0.9))
        mm = homog(sq)
        out.append(segs([(mm(u, 0), mm(u, 1)) for u in (0.25, 0.5, 0.75)] + [(mm(0, 0.3), mm(1, 0.3))], 0.6, seed, 0, color=PAPER, op=0.6))
        ins = C.qz(Zf - 0.05, X0 + 0.35, X1 - 1.55, 3.2, 3.6)
        out.append(F(ins, PAPER) + H(U, ins, 0, 1.2, 0.6) + sketch(ins, 0.8, seed, 0.1))
        dq = C.qz(Zf, X1 - 1.4, X1 - 0.5, 0.2, 2.9)
    else:
        for i in range(wins - 1):
            xc = X0 + W * (i + 0.5) / wins
            wq = C.qz(Zf, xc - 0.45, xc + 0.45, 0.9, 2.9)
            out.append(F(wq, INK, 0.88) + segs([(pt(wq[0], wq[1], 0.5), pt(wq[3], wq[2], 0.5))], 0.55, seed, 0, color=PAPER, op=0.7))
            lt = C.qz(Zf - 0.05, xc - 0.57, xc + 0.57, 2.9, 3.2)
            out.append(F(lt, PAPER) + sketch(lt, 0.7, seed, 0.1))
        xc = X0 + W * (wins - 0.5) / wins
        dq = C.qz(Zf, xc - 0.5, xc + 0.5, 0.2, 2.6)
    # door with fanlight
    out.append(F(dq, INK, 0.92))
    da, db = homog(dq)(0, 0), homog(dq)(1, 0)
    fan = [pt(da, db, t) for t in [i / 10 for i in range(11)]]
    rr = abs(db[0] - da[0]) / 2
    fan = [(fx, fy - math.sin(i / 10 * math.pi) * rr * 0.9) for i, (fx, fy) in enumerate(fan)]
    out.append(F(fan, INK, 0.75) + pen(fan, 0.9, seed, 0.05))
    # a step at the door
    stp = [pt(dq[3], dq[2], -0.15), pt(dq[3], dq[2], 1.15)]
    out.append(segs([(stp[0], stp[1])], 1.2, seed, 0))
    # cornice, dentils
    cor = C.qz(Zf - 0.25, X0 - 0.05, X1 + 0.05, ht - 0.55, ht)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.3, 0.6) + sketch(cor, 1.0, seed, 0.15))
    den = [(C(X, ht - 0.55, Zf - 0.25), C(X, ht - 0.8, Zf - 0.25)) for X in [X0 + 0.12 + 0.24 * i for i in range(int(W / 0.24))]]
    out.append(segs(den, 0.7, seed, 0))
    out.append(F(C.qz(Zf - 0.01, X0, X1, ht - 1.2, ht - 0.55), INK, 0.3))
    # roof
    if roof == "parapet":
        par = C.qz(Zf - 0.1, X0, X1, ht, ht + 0.9)
        out.append(F(par, PAPER) + sketch(par, 1.0, seed, 0.15))
        bal_ = []
        X = X0 + 0.3
        while X < X1 - 0.2:
            bal_.append((C(X, ht + 0.1, Zf - 0.1), C(X, ht + 0.75, Zf - 0.1)))
            X += 0.28
        out.append(segs(bal_, 0.7, seed, 0))
        top = ht + 0.9
    elif roof == "hip":
        rf = [C(X0 + 0.2, ht, Zf - 0.2), C(X1 - 0.2, ht, Zf - 0.2), C(X1 - 1.6, ht + 2.6, Zf + 3.0), C(X0 + 1.6, ht + 2.6, Zf + 3.0)]
        out.append(F(rf, PAPER) + H(U, rf, 0, 1.8, 0.7) + segs([(pt(rf[0], rf[1], t), pt(rf[3], rf[2], t)) for t in (0.2, 0.4, 0.6, 0.8)], 0.5, seed, 0)
                   + sketch(rf, 1.2, seed, 0.2))
        ch = C.qz(Zf + 2.0, X1 - 1.4, X1 - 0.8, ht + 1.5, ht + 3.6)
        out.append(F(ch, PAPER) + H(U, ch, 90, 1.4, 0.6) + sketch(ch, 1.0, seed, 0.1))
        top = ht + 2.6
    else:   # curvilinear gable
        g = [C(X0, ht, Zf - 0.1)]
        for t in [i / 16 for i in range(17)]:
            X = lerp(X0, X1, t)
            yy = ht + 2.6 * (math.sin(t * math.pi) ** 0.6) + 0.35 * math.sin(t * math.pi * 3) * math.sin(t * math.pi)
            g.append(C(X, yy, Zf - 0.1))
        g.append(C(X1, ht, Zf - 0.1))
        out.append(F(g, PAPER) + sketch(g, 1.2, seed, 0.1))
        if lvl:
            out.append(H(U, g, ang, 3.4, 0.6, op=0.7))
        cq = C.qz(Zf - 0.12, (X0 + X1) / 2 - 0.35, (X0 + X1) / 2 + 0.35, ht + 0.6, ht + 1.7)
        out.append(F(cq, INK, 0.85))
        top = ht + 2.6
    # the party wall showing above the nearer neighbour, in shade
    if side is not None and side < ht:
        sw = [C(X1, ht, Zf), C(X1, ht, Zf + 9), C(X1, side, Zf + 9), C(X1, side, Zf)]
        out.append(F(sw, PAPER) + tone(U, sw, 3, 75, box=bbox(sw)) + sketch(sw, 1.0, seed, 0.1))
    out.append(sketch(q, 1.3, seed, 0.3))
    return "".join(out)


def carriage(U, C, Xc, Zc, seed):
    """A horse-drawn tour carriage moving along the street (toward +X) seen from the side: canopy with a fringe,
    rows of passengers, big rear wheels, driver up front, a horse in harness. Drawn on the plane Z = Zc."""
    rnd = random.Random(seed)

    def Pp(u, v):
        return C(Xc + u, v, Zc)

    def path(pts):
        return [Pp(u, v) for u, v in pts]
    out = []
    # far-side wheels peeking out
    for u, r in ((-4.6, 0.62), (-1.4, 0.45)):
        ring = [C(Xc + u + 0.12 + r * math.cos(a), r + r * math.sin(a), Zc + 1.6) for a in [i * math.pi / 12 for i in range(24)]]
        out.append(pen(ring, 0.9, seed, 0.05, closed=True, op=0.8))
    # bed + canopy
    bed = path([(-5.9, 0.85), (-0.9, 0.85), (-0.7, 1.35), (-5.9, 1.35)])
    out.append(F(bed, PAPER) + H(U, bed, 0, 1.6, 0.7) + sketch(bed, 1.2, seed, 0.1))
    for k, u in enumerate((-5.3, -4.3, -3.3, -2.3)):        # passengers on the benches
        hx, hy = Pp(u, 2.05)
        s_ = abs(Pp(0, 1)[1] - Pp(0, 0)[1])
        out.append(F(smooth_closed([Pp(u - 0.28, 1.35), Pp(u + 0.28, 1.35), Pp(u + 0.24, 1.85), Pp(u - 0.24, 1.85)]), INK, 0.92))
        out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(s_ * 0.16)}" fill="{INK}"/>')
        if k == 1:
            out.append(F(smooth_closed([Pp(u - 0.3, 2.18), Pp(u + 0.3, 2.18), Pp(u + 0.12, 2.25), Pp(u - 0.12, 2.25)]), INK))
    can = path([(-6.1, 2.55), (-0.6, 2.55), (-0.75, 2.8), (-5.95, 2.8)])
    out.append(F(can, PAPER) + H(U, can, 0, 1.4, 0.6) + sketch(can, 1.2, seed + 1, 0.1))
    fr = []
    for i in range(46):
        u = lerp(-6.05, -0.65, i / 45)
        a, b = Pp(u, 2.55), Pp(u, 2.42 + 0.05 * (i % 2))
        fr.append((a, b))
    out.append(segs(fr, 0.7, seed, 0))
    out.append(segs([(Pp(u, 1.35), Pp(u, 2.55)) for u in (-5.95, -3.4, -0.85)], 1.0, seed, 0))
    # near wheels: rims, spokes, hubs
    for u, r in ((-4.6, 0.62), (-1.4, 0.45)):
        cx_, cy_ = Pp(u, r)
        rim = [Pp(u + r * math.cos(a), r + r * math.sin(a)) for a in [i * math.pi / 14 for i in range(28)]]
        rim2 = [Pp(u + r * 0.86 * math.cos(a), r + r * 0.86 * math.sin(a)) for a in [i * math.pi / 14 for i in range(28)]]
        out.append(pen(rim, 1.6, seed, 0.05, closed=True) + pen(rim2, 0.7, seed + 1, 0.05, closed=True))
        out.append(segs([((cx_, cy_), Pp(u + r * 0.86 * math.cos(a), r + r * 0.86 * math.sin(a))) for a in [i * math.pi / 6 for i in range(12)]], 0.6, seed, 0))
        out.append(f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="2" fill="{INK}"/>')
    # driver
    dx, dy = Pp(-0.95, 1.35)
    s_ = abs(Pp(0, 1)[1] - Pp(0, 0)[1])
    out.append(F(smooth_closed([Pp(-1.2, 1.35), Pp(-0.75, 1.35), Pp(-0.8, 2.0), Pp(-1.15, 2.0)]), INK))
    hx, hy = Pp(-0.97, 2.15)
    out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(s_ * 0.15)}" fill="{INK}"/>')
    out.append(F(smooth_closed([Pp(-1.25, 2.27), Pp(-0.7, 2.27), Pp(-0.85, 2.33), Pp(-1.1, 2.33)]), INK))
    out.append(F(path([(-1.12, 2.28), (-0.82, 2.28), (-0.86, 2.48), (-1.08, 2.48)]), INK))
    # reins + shafts
    out.append(P(f"M {f1(Pp(-0.8, 1.7)[0])} {f1(Pp(-0.8, 1.7)[1])} Q {f1(Pp(0.6, 1.5)[0])} {f1(Pp(0.6, 1.5)[1])} {f1(Pp(2.0, 1.85)[0])} {f1(Pp(2.0, 1.85)[1])}", 0.7))
    out.append(segs([(Pp(-0.8, 1.05), Pp(1.6, 1.2))], 1.4, seed, 0))
    # the horse
    body = [(0.0, 1.45), (0.15, 1.58), (0.6, 1.55), (1.2, 1.5), (1.65, 1.62), (1.9, 1.85), (2.15, 2.15), (2.3, 2.3),
            (2.4, 2.24), (2.55, 2.0), (2.78, 1.78), (2.74, 1.67), (2.55, 1.66), (2.35, 1.76), (2.2, 1.58), (2.05, 1.2),
            (1.92, 1.0), (1.6, 0.95), (0.9, 0.95), (0.5, 1.0), (0.15, 1.05), (0.0, 1.22)]
    hb = path([(u + 0.25, v) for u, v in body])
    legs = [[(0.45, 1.0), (0.38, 0.55), (0.48, 0.05)], [(0.32, 1.0), (0.16, 0.55), (0.26, 0.05)],
            [(1.95, 1.05), (2.05, 0.55), (2.0, 0.05)], [(1.78, 1.0), (1.62, 0.55), (1.5, 0.12)]]
    lw_ = max(1.6, s_ * 0.13)
    for i, lg in enumerate(legs):
        out.append(nib(path([(u + 0.25, v) for u, v in lg]), lw_, taper=(1, 0.6), seed=seed + i, color=INK, op=0.85 if i % 2 else 1))
        hx2, hy2 = Pp(lg[-1][0] + 0.25, lg[-1][1])
        out.append(F([(hx2 - lw_ * 0.6, hy2 - lw_ * 0.6), (hx2 + lw_ * 0.9, hy2 - lw_ * 0.6), (hx2 + lw_, hy2 + lw_ * 0.5), (hx2 - lw_ * 0.6, hy2 + lw_ * 0.5)], INK))
    out.append(F(smooth_closed(hb), PAPER) + clipped(U("hs"), smooth_closed(hb), tone(U, smooth_closed(hb), 2, 60, box=bbox(hb))
                                                     + H(U, smooth_closed(hb), 0, 1.8, 0.7, box=bbox(hb), span=(0.6, 1), dark=Pp(1.0, 0.8)))
               + P(smooth_closed(hb), 1.3))
    ear = path([(2.27, 2.26), (2.32, 2.45), (2.38, 2.25)])
    out.append(F(ear, INK))
    mane = " ".join(f"M {f1(Pp(lerp(2.25, 1.75, t) + 0.25, lerp(2.27, 1.7, t))[0])} {f1(Pp(lerp(2.25, 1.75, t) + 0.25, lerp(2.27, 1.7, t))[1])} "
                    f"l {f1(-s_ * 0.12)} {f1(s_ * 0.1)}" for t in [i / 9 for i in range(10)])
    out.append(P(mane, 1.0))
    tail = [Pp(0.27, 1.45), Pp(0.05, 1.2), Pp(0.1, 0.65)]
    out.append(nib(tail, max(1.6, s_ * 0.12), taper=(0.8, 0.2), seed=seed, color=INK))
    # harness: collar, saddle pad, breeching
    out.append(nib([Pp(2.05, 1.95), Pp(2.18, 1.6), Pp(2.25, 1.25)], max(1.4, s_ * 0.1), taper=(1, 1), seed=seed, color=INK))
    out.append(F(path([(1.15, 1.48), (1.55, 1.5), (1.5, 1.2), (1.2, 1.18)]), INK, 0.9))
    out.append(P(f"M {f1(Pp(0.4, 1.45)[0])} {f1(Pp(0.4, 1.45)[1])} Q {f1(Pp(0.3, 1.2)[0])} {f1(Pp(0.3, 1.2)[1])} {f1(Pp(0.55, 1.1)[0])} {f1(Pp(0.55, 1.1)[1])} L {f1(Pp(1.3, 1.2)[0])} {f1(Pp(1.3, 1.2)[1])}", 0.9))
    out.append(P(f"M {f1(Pp(2.85, 1.75)[0])} {f1(Pp(2.85, 1.75)[1])} L {f1(Pp(2.45, 2.15)[0])} {f1(Pp(2.45, 2.15)[1])}", 0.8))
    return "".join(out)


def steeple(U, cx, base, s, seed=1):
    """A white Charleston church steeple in elevation (s px per metre): square tower, a pedimented belfry stage
    with columns and a clock, two diminishing octagonal stages and a slender spire with a weathervane."""
    out = []

    def Y(m):
        return base - m * s

    def X(m):
        return cx + m * s
    stages = [(0, 14, 4.2), (14, 21, 3.6), (21, 26, 2.8), (26, 30, 2.1)]
    for i, (y0, y1, hw) in enumerate(stages):
        r = rect(X(-hw), Y(y1), X(hw), Y(y0))
        out.append(F(r, PAPER) + H(U, rect(X(hw * 0.35), Y(y1), X(hw), Y(y0)), 90, 1.5, 0.6))
        out.append(F(rect(X(-hw - 0.4), Y(y1) - 0.2 * s, X(hw + 0.4), Y(y1) + 0.3 * s), PAPER)
                   + sketch(rect(X(-hw - 0.4), Y(y1) - 0.2 * s, X(hw + 0.4), Y(y1) + 0.3 * s), 0.9, seed + i, 0.1))
        if i == 0:
            out.append(F(rect(X(-1.1), Y(11), X(1.1), Y(6)), INK, 0.85))
            for xx in (-2.8, 2.8):
                out.append(seg(X(xx), Y(y0), X(xx), Y(y1), 0.7, seed, 0))
        elif i == 1:
            for xx in (-2.6, -0.9, 0.9, 2.6):
                out.append(F(rect(X(xx - 0.3), Y(y1 - 0.6), X(xx + 0.3), Y(y0 + 0.4)), PAPER) + sketch(rect(X(xx - 0.3), Y(y1 - 0.6), X(xx + 0.3), Y(y0 + 0.4)), 0.7, seed, 0.05))
            out.append(F(rect(X(-0.55), Y(y1 - 1.0), X(0.55), Y(y0 + 1.0)), INK, 0.8))
            out.append(f'<circle cx="{f1(X(0))}" cy="{f1(Y(y1 + 0.0) + 0.0)}" r="0" fill="none"/>')
        else:
            for xx in (-hw * 0.55, hw * 0.55):
                out.append(F(rect(X(xx - 0.35), Y(y1 - 0.7), X(xx + 0.35), Y(y0 + 0.6)), INK, 0.8))
        out.append(sketch(r, 1.0, seed + i, 0.1))
    ck = (X(0), Y(12.7))
    out.append(f'<circle cx="{f1(ck[0])}" cy="{f1(ck[1])}" r="{f1(1.1 * s)}" fill="{PAPER}" stroke="{INK}" stroke-width="0.9"/>')
    sp = [(X(-2.0), Y(30.3)), (X(0), Y(44)), (X(2.0), Y(30.3))]
    out.append(F(sp, PAPER) + H(U, [(X(0), Y(44)), (X(0.4), Y(30.3)), (X(2.0), Y(30.3))], 90, 1.3, 0.6) + pen(sp, 1.2, seed, 0.05))
    out.append(seg(X(0), Y(44), X(0), Y(47), 0.9, seed, 0) + seg(X(-0.8), Y(46), X(0.9), Y(46.2), 1.1, seed, 0))
    return "".join(out)


@design("charleston")
def charleston(U):
    """Rainbow Row on East Bay Street on a bright morning, seen from the waterfront side: the row of Georgian
    houses runs away to the left in a long oblique perspective, each house a different engraved tone for its
    pastel colour (the pink one takes the vermilion), shutters, balconies, parapets and a curved gable; a carriage
    tour clops past, gas lamps, strollers, sabal palmettos frame the left, a white steeple over the far roofs."""
    art = []
    C = YCam(f=230, cx=282, vpy=330, eye=1.6, yaw=-0.35)
    Zf = 16.0
    ZC = Zf - 2.2          # far curb
    art.append(cloud(U, 372, 82, 96, 14, 71))
    art.append(cloud(U, 180, 64, 60, 9, 72))
    art.append(gull(330, 138, 8, 73) + gull(352, 124, 6, 74) + bird(300, 160, 5, 75) + gull(408, 118, 6, 79))
    # the steeple over the far roofs, with treetops
    art.append(steeple(U, 262, 300, 5.0, 76))
    for i in range(9):
        x, y = C(-60 + i * 4.0, 7.5, Zf + 22)
        art.append(lobe(U, x, y, 12, 10, 760 + i, light=(-1, -1), w=0.9, dense=1.3))
    # the street: asphalt, granite curbs, far sidewalk
    road = [C(-120, 0, 3.6), C(-120, 0, ZC), C(16, 0, ZC), C(16, 0, 3.6)]
    art.append(F(road, PAPER) + H(U, road, 2, (3.6, 1.8), 0.65, op=0.65, dark=(300, 640), wob=0.3, brk=0.25)
               + H(U, [C(-120, 0, 3.6), C(-120, 0, 6.5), C(16, 0, 6.5), C(16, 0, 3.6)], 160, (5, 2.6), 0.55, op=0.5, dark=(300, 640), wob=0.3, brk=0.3))
    fw = [C(-120, 0.15, ZC), C(-120, 0.15, Zf), C(16, 0.15, Zf), C(16, 0.15, ZC)]
    art.append(F(fw, PAPER) + clipped(U("fw"), poly(fw), segs([(C(X, 0.15, ZC), C(X, 0.15, Zf)) for X in [-120 + 1.1 * i for i in range(124)]], 0.5, 77, 0, op=0.5)))
    art.append(pen([C(-120, 0.15, ZC), C(16, 0.15, ZC)], 1.5, 78, 0.05) + pen([C(-120, 0, ZC), C(16, 0, ZC)], 0.9, 79, 0.05))
    # the row, far (left) to near (right)
    row = [(-90, -82, 9.6, 1, 75, "parapet", False, False, False, 3, 3), (-82, -75, 10.8, 2, 85, "hip", False, False, False, 3, 3),
           (-75, -69, 9.0, 0, 80, "parapet", False, True, False, 2, 3), (-69, -62, 11.0, 1, 60, "hip", False, False, True, 3, 3),
           (-62, -55, 10.2, 2, 80, "parapet", False, False, False, 3, 3), (-55, -48, 11.4, 1, 70, "gable", False, False, True, 3, 3),
           (-48, -41, 9.6, 3, 80, "parapet", False, True, False, 3, 3), (-41, -34, 10.8, 0, 75, "hip", False, False, False, 3, 3),
           (-34, -27, 10.2, 2, 80, "parapet", False, False, False, 3, 3), (-27, -20.5, 9.4, 0, 75, "hip", False, False, True, 3, 3),
           (-20.5, -13.5, 11.0, 1, 85, "parapet", False, True, False, 3, 3), (-13.5, -6.5, 10.0, 0, 80, "gable", True, False, True, 3, 3),
           (-6.5, 1.0, 11.6, 1, 70, "hip", False, True, False, 3, 3), (1.0, 9.0, 10.4, 2, 82, "parapet", False, False, True, 3, 3),
           (9.0, 17.0, 11.2, 0, 80, "hip", False, True, False, 3, 3)]
    for i, (x0, x1, ht, lvl, ang, roof, acc, bal, shop, wins, fl) in enumerate(row):
        if C(x1, 0, Zf)[0] < 20:        # wholly outside the picture
            continue
        nxt = row[i + 1][2] if i + 1 < len(row) else None
        art.append(georgian(U, C, Zf, x0, x1, ht, 200 + i * 11, lvl=lvl, ang=ang, roof=roof, acc=acc, bal=bal, shop=shop,
                            wins=wins, floors=fl, side=nxt))
    # gas lamps along the far curb and strollers on the far sidewalk
    for X in (-30, -13, 4):
        x, y = C(X, 0.15, ZC + 0.3)
        dp = C.depth(X, ZC + 0.3)
        art.append(lamp(x, y, C.f * 3.6 / dp, 230 + int(-X), "lantern", max(1.0, min(2.2, 26 / dp))))
    for X, z, sd, kind, fl in ((-36, Zf - 1.0, 241, "plain", False), (-25, Zf - 0.8, 242, "dress", True), (-21, Zf - 1.2, 243, "hat", False),
                               (-8, Zf - 1.1, 244, "dog", True), (-11, Zf - 0.9, 245, "dress", False), (7, Zf - 1.0, 246, "bag", True)):
        x, y = C(X, 0.15, z)
        art.append(walker(x, y, C.f * 1.7 / C.depth(X, z), sd, flip=fl, kind=kind))
    # shadows thrown across the street by the palmettos behind us, and under the carriage
    for (bx, by, L, sd) in ((122, 440, 150, 1), (500, 452, 170, 2)):
        ex, ey = bx + L * 0.42, by - L * 0.34
        sh = smooth_closed([(ex + math.cos(a_) * L * 0.36 * (1.0 if k_ % 2 else 0.55), ey + math.sin(a_) * L * 0.1 * (1.0 if k_ % 2 else 0.55)) for k_, a_ in enumerate([j * math.pi / 11 for j in range(22)])])
        art.append(F(sh, PAPER) + tone(U, sh, 3, 20, box=(ex - L * 0.5, ey - L * 0.15, ex + L * 0.5, ey + L * 0.15))
                   + nib([(bx, by), (ex - L * 0.02, ey + L * 0.05)], 3.0, taper=(1, 0.6), seed=sd, color=INK, op=0.8))
    a, b = C(-9.4, 0, 8.4), C(-0.4, 0, 8.4)
    a2, b2 = C(-9.4, 0, 9.8), C(-0.4, 0, 9.8)
    shc = [a, b, b2, a2]
    art.append(tone(U, shc, 3, 15, box=bbox(shc)))
    # the carriage
    art.append(carriage(U, C, -3.2, 8.6, 250))
    # our side: curb and sidewalk, a horse-head hitching post, the waterfront palmettos framing the view
    nw = [C(-120, 0.15, 0.8), C(-120, 0.15, 3.6), C(16, 0.15, 3.6), C(16, 0.15, 0.8)]
    art.append(F(nw, PAPER) + pen([C(-120, 0.15, 3.6), C(16, 0.15, 3.6)], 1.8, 80, 0.05) + H(U, nw, 10, 3.0, 0.6, op=0.6))
    art.append(palmetto(U, 118, 452, 352, 251, lean=0.025, span=1.0))
    art.append(palmetto(U, 508, 470, 380, 253, lean=-0.03, span=0.95))
    return plate(U, "charleston", art, 75)


# ================================================================ HAVANA
HAV_SLOPE, HAV_END = 0.075, 24.0       # the street runs gently down to the Malecón


class SlopeCam(Cam):
    """A camera over ground that falls away ahead of us: every point is lowered by the street's drop at its Z."""
    def __call__(self, X, Y, Z):
        return super().__call__(X, Y - HAV_SLOPE * min(max(Z, 0.0), HAV_END), Z)


def mediopunto(U, m, seed, w=0.7):
    """A Cuban mediopunto: the half-round fanlight over a door, its glass split into radiating panes and a ring,
    mapped through the homography m of the half-round's bounding quad (u across, v down)."""
    arc = [(0.5 + 0.5 * math.cos(math.pi + math.pi * t), 1 - math.sin(math.pi * t)) for t in [i / 16 for i in range(17)]]
    inner = [(0.5 + 0.22 * math.cos(math.pi + math.pi * t), 1 - 0.44 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
    d = uvd(m, arc) + " Z"
    out = [F(d, PAPER), H(U, d, 90, 1.6, 0.5, op=0.6)]
    spokes = []
    for k in range(7):
        a = math.pi + math.pi * (k + 0.5) / 7
        spokes.append(uvd(m, [(0.5 + 0.22 * math.cos(a), 1 + 0.44 * math.sin(a)), (0.5 + 0.5 * math.cos(a), 1 + math.sin(a))]))
    out.append(P(" ".join(spokes) + " " + uvd(m, inner), w))
    out.append(P(d, w * 1.5))
    return "".join(out)


def iron_rail(U, q, seed, w=0.7):
    """A Havana balcony railing on a quad [TL, TR, BR, BL]: rails and close bars with a band of rings."""
    m = homog(q)
    L = math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1])
    n = max(4, int(L / 2.6))
    d = [uvd(m, [(i / n, 0), (i / n, 1)]) for i in range(n + 1)]
    if L / n > 3.5:
        for i in range(n):
            uc = (i + 0.5) / n
            d.append(uvd(m, [(uc + 0.32 / n * math.cos(a), 0.3 + 0.12 * math.sin(a)) for a in [j * math.pi / 6 for j in range(13)]]))
    return P(" ".join(d), w) + pen([q[0], q[1]], w * 2.2, seed, 0.05) + pen([q[3], q[2]], w * 1.6, seed + 1, 0.05)


def laundry(x0, y0, x1, y1, seed, n=5, s=1.0):
    """A sagging line of washing between two points: shirts, towels and sheets pegged on."""
    rnd = random.Random(seed)
    sag = abs(x1 - x0) * 0.08 + 2
    out = [P(f"M {f1(x0)} {f1(y0)} Q {f1((x0 + x1) / 2)} {f1((y0 + y1) / 2 + sag * 2)} {f1(x1)} {f1(y1)}", 0.6)]
    for i in range(n):
        t = (i + 0.6) / (n + 0.2)
        x = lerp(x0, x1, t)
        y = lerp(y0, y1, t) + sag * 2 * 4 * t * (1 - t) * 0.5
        w = abs(x1 - x0) / (n + 1) * rnd.uniform(0.55, 0.8)
        h = w * rnd.uniform(0.8, 1.5) * s
        if rnd.random() < 0.4:     # shirt
            sh = [(x - w / 2, y), (x - w * 0.15, y), (x, y + h * 0.12), (x + w * 0.15, y), (x + w / 2, y), (x + w * 0.62, y + h * 0.3),
                  (x + w * 0.38, y + h * 0.36), (x + w * 0.36, y + h), (x - w * 0.36, y + h), (x - w * 0.38, y + h * 0.36), (x - w * 0.62, y + h * 0.3)]
        else:
            sh = [(x - w / 2, y), (x + w / 2, y), (x + w / 2 + rnd.uniform(-1, 1), y + h), (x - w / 2 + rnd.uniform(-1, 1), y + h * rnd.uniform(0.9, 1.1))]
        dark = rnd.random() < 0.3
        out.append(F(sh, INK if dark else PAPER, 0.8 if dark else 1) + pen(sh, 0.7, seed + i, 0.2, closed=True))
        if not dark:
            out.append(segs([((x - w * 0.3, y + h * f), (x + w * 0.3, y + h * f)) for f in (0.5, 0.75)], 0.45, seed, 0.3, op=0.6))
    return "".join(out)


def habana_front(U, C, X, Z0, Z1, top, seed, floors=(4.8, 8.8), acc=False, peel=True, side=-1, lvl=1, wash=False):
    """A colonial house front in Old Havana on the plane X (left side when side = -1): stucco with peeling
    patches, tall panelled doors under mediopunto fanlights, French windows with small iron balconies on the
    upper floors, a cornice and a balustraded parapet with urns."""
    rnd = random.Random(seed)
    sg = -side                       # toward the street
    out = []
    wall = C.qx(X, Z0, Z1, 0, top)
    out.append(F(wall, PAPER))
    if lvl:
        out.append(H(U, wall, 80 if side < 0 else 100, 3.8 if lvl == 1 else 2.6, 0.6, op=0.6, wob=0.2, brk=0.15))
    if lvl >= 3:
        out.append(H(U, wall, 20, 3.0, 0.6, op=0.7, wob=0.2, brk=0.15))
    out.append(segs([(C(X, y, Z0), C(X, y, Z1)) for y in [0.6] + [f_ + d_ for f_ in floors for d_ in (-0.35, 0.0)]], 0.6, seed, 0, op=0.6))
    # peeling plaster: patches of exposed brick
    if peel:
        for _ in range(3):
            z = rnd.uniform(Z0 + 0.5, Z1 - 1.2)
            y = rnd.uniform(1.0, top - 2)
            pts = [C(X, y + 0.42 * math.sin(a) * rnd.uniform(0.5, 1.15), z + 0.6 * math.cos(a) * rnd.uniform(0.5, 1.15)) for a in [k * math.pi / 6 for k in range(12)]]
            dd = smooth_closed(pts)
            bk = segs([(C(X, y + yy, z - 1), C(X, y + yy, z + 1)) for yy in [-0.5 + 0.12 * k for k in range(9)]], 0.5, seed, 0.1)
            bk += segs([(C(X, y + yy, z + zz), C(X, y + yy + 0.12, z + zz)) for k, yy in enumerate([-0.5 + 0.12 * k for k in range(8)]) for zz in [-0.6 + 0.24 * j + 0.12 * (k % 2) for j in range(6)]], 0.45, seed, 0)
            out.append(F(dd, PAPER) + clipped(U("pl"), dd, bk) + pen(pts[:7], 1.0, seed, 0.3) + pen(pts[6:] + pts[:1], 0.6, seed, 0.3))
    # openings
    W = Z1 - Z0
    nb = max(1, int(W / 2.8))
    bay = W / nb
    # pilasters between the bays and rusticated ground storey
    for i in range(nb + 1):
        z = Z0 + bay * i
        pq = C.qx(X - sg * 0.02, max(Z0, z - 0.22), min(Z1, z + 0.22), 0, top - 0.6)
        out.append(F(pq, PAPER) + H(U, [pq[0], pt(pq[0], pq[1], 0.5), pt(pq[3], pq[2], 0.5), pq[3]] if side > 0 else [pt(pq[0], pq[1], 0.5), pq[1], pq[2], pt(pq[3], pq[2], 0.5)], 90, 1.4, 0.6)
                   + sketch(pq, 0.8, seed + i, 0.05))
    out.append(segs([(C(X, y, Z0), C(X, y, Z1)) for y in (0.95, 1.6, 2.25, 2.9, 3.55)], 0.5, seed + 2, 0, op=0.6))
    for i in range(nb):
        zc = Z0 + bay * (i + 0.5)
        za, zb = zc - 0.62, zc + 0.62
        # ground floor door with fanlight
        dq = C.qx(X, za, zb, 0.25, 3.3)
        fq = C.qx(X, za, zb, 3.3, 3.95)
        out.append(F(dq, INK, 0.9))
        m = homog(dq)
        if abs(dq[1][0] - dq[0][0]) > 5:
            out.append(segs([(m(0.5, 0), m(0.5, 1))] + [(m(0.1, v), m(0.9, v)) for v in (0.3, 0.62)], 0.6, seed, 0, color=PAPER, op=0.6))
            out.append(mediopunto(U, homog(fq), seed + i))
        sur = C.qx(X - sg * 0.04, za - 0.18, zb + 0.18, 0.2, 4.15)
        out.append(sketch(sur, 0.9, seed + i, 0.1))
        # upper floors: French windows with balconies
        for j, yf in enumerate(floors):
            if yf + 3.1 > top:
                continue
            wq = C.qx(X, za + 0.08, zb - 0.08, yf + 0.35, yf + 3.0)
            out.append(F(wq, INK, 0.88))
            mm = homog(wq)
            if abs(wq[1][0] - wq[0][0]) > 4:
                out.append(segs([(mm(0.5, 0), mm(0.5, 1)), (mm(0, 0.35), mm(1, 0.35))], 0.55, seed, 0, color=PAPER, op=0.6))
            if (i + j + seed) % 3 != 2:     # shutters folded half open
                lq = C.qx(X - sg * 0.02, za + 0.08, za + 0.55, yf + 0.35, yf + 3.0)
                out.append(louvered(U, lq, seed + i * 5 + j, w=0.5))
            lt = C.qx(X - sg * 0.05, za - 0.12, zb + 0.12, yf + 3.0, yf + 3.35)
            out.append(F(lt, PAPER) + sketch(lt, 0.7, seed, 0.1))
            slab = [C(X, yf + 0.3, za - 0.25), C(X, yf + 0.3, zb + 0.25), C(X + sg * 0.75, yf + 0.3, zb + 0.25), C(X + sg * 0.75, yf + 0.3, za - 0.25)]
            out.append(F(slab, INK, 0.55) + H(U, slab, 0, 1.4, 0.6))
            rq = C.qx(X + sg * 0.75, za - 0.25, zb + 0.25, yf + 0.3, yf + 1.3)
            out.append(iron_rail(U, rq, seed + i + j))
            out.append(segs([(C(X, yf + 0.3, za - 0.25), C(X + sg * 0.75, yf + 1.3, za - 0.25)), (C(X, yf + 0.3, zb + 0.25), C(X + sg * 0.75, yf + 1.3, zb + 0.25))], 0.6, seed, 0))
            out.append(F(C.qx(X + sg * 0.01, za - 0.25, zb + 0.25, yf - 0.35, yf + 0.3), INK, 0.35))
            if (i * 3 + j + seed) % 4 == 0:      # a potted plant on the balcony
                px_, py_ = C(X + sg * 0.5, yf + 1.5, zc + 0.2)
                r = C.f * 0.35 / max(zc, 1)
                out.append(lobe(U, px_, py_, r, r * 0.8, seed + i * 9 + j, light=(1, -1), w=0.8, dense=1.4))
    if wash:
        z = Z0 + bay * 0.5
        a, b = C(X + sg * 0.75, floors[0] + 2.2, z - 0.25), C(X + sg * 0.75, floors[0] + 2.2, z + bay)
        out.append(laundry(a[0], a[1], b[0], b[1], seed, 4))
    # cornice, parapet with balusters and urns
    cor = C.qx(X + sg * 0.25, Z0, Z1, top - 0.6, top)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.4, 0.6) + sketch(cor, 1.0, seed, 0.1))
    out.append(F(C.qx(X + sg * 0.01, Z0, Z1, top - 1.1, top - 0.6), INK, 0.3))
    par = C.qx(X + sg * 0.1, Z0, Z1, top, top + 1.0)
    out.append(F(par, PAPER) + sketch(par, 1.0, seed + 1, 0.1))
    bl = []
    z = Z0 + 0.4
    while z < Z1 - 0.3:
        bl.append((C(X + sg * 0.1, top + 0.15, z), C(X + sg * 0.1, top + 0.8, z)))
        z += 0.3
    out.append(segs(bl, 0.7, seed, 0))
    for z in (Z0 + 0.15, Z1 - 0.15):
        ux, uy = C(X + sg * 0.15, top + 1.0, z)
        r = max(1.5, C.f * 0.3 / max(z, 1))
        out.append(F(smooth_closed([(ux - r, uy), (ux + r, uy), (ux + r * 0.8, uy - r * 1.6), (ux, uy - r * 2.4), (ux - r * 0.8, uy - r * 1.6)]), PAPER)
                   + pen([(ux - r, uy), (ux + r * 0.8, uy - r * 1.6), (ux, uy - r * 2.4), (ux - r * 0.8, uy - r * 1.6), (ux - r, uy)], 0.9, seed, 0.1))
    out.append(pen([C(X, 0, Z1), C(X, top, Z1)], 1.4, seed, 0.1) + pen([C(X, 0, Z0), C(X, top, Z0)], 1.2, seed + 1, 0.1))
    return "".join(out)


def portales(U, C, Xc, Xw, Z0, Z1, top, seed, span=3.0, floors=(5.2, 9.0)):
    """The right side of the street: a building whose front stands on an arcade of columns at the curb line
    Xc (the walk under it in deep shade back to the wall Xw), upper floors with balconies above."""
    out = []
    # the shaded walk under the arcade: back wall, doors, ceiling
    back = C.qx(Xw, Z0, Z1, 0, floors[0] - 0.6)
    out.append(F(back, PAPER) + tone(U, back, 4, 75, box=bbox(back)))
    ceil = [C(Xc, floors[0] - 0.6, Z0), C(Xc, floors[0] - 0.6, Z1), C(Xw, floors[0] - 0.6, Z1), C(Xw, floors[0] - 0.6, Z0)]
    out.append(F(ceil, PAPER) + tone(U, ceil, 3, 10, box=bbox(ceil)))
    # upper floors on the plane Xc
    up = C.qx(Xc, Z0, Z1, floors[0] - 0.6, top)
    out.append(F(up, PAPER) + tone(U, up, 2, 100, box=bbox(up)))
    n = max(1, int(round((Z1 - Z0) / span)))
    sp = (Z1 - Z0) / n
    wins = []
    for i in range(n):
        zc = Z0 + sp * (i + 0.5)
        for yf in floors:
            if yf + 3 > top:
                continue
            wq = C.qx(Xc, zc - 0.55, zc + 0.55, yf + 0.3, yf + 2.9)
            wins.append(wq)
            lt = C.qx(Xc - 0.05, zc - 0.7, zc + 0.7, yf + 2.9, yf + 3.25)
            out.append(F(lt, PAPER) + H(U, lt, 0, 1.4, 0.5) + sketch(lt, 0.7, seed, 0.1))
            slab = [C(Xc, yf + 0.25, zc - 0.85), C(Xc, yf + 0.25, zc + 0.85), C(Xc - 0.7, yf + 0.25, zc + 0.85), C(Xc - 0.7, yf + 0.25, zc - 0.85)]
            out.append(F(slab, INK, 0.9))
            rq = C.qx(Xc - 0.7, zc - 0.85, zc + 0.85, yf + 0.25, yf + 1.25)
            out.append(F(rq, PAPER, 0.5) + iron_rail(U, rq, seed + i))
    out.append(F(" ".join(poly(w) for w in wins), INK, 0.92))
    # arches and columns
    arches = []
    for i in range(n):
        za, zb = Z0 + sp * i, Z0 + sp * (i + 1)
        spring = floors[0] - 0.6 - sp * 0.5 - 0.3
        arc = [C(Xc, spring + math.sin(t * math.pi) * sp * 0.42, lerp(za + 0.22, zb - 0.22, t)) for t in [k / 14 for k in range(15)]]
        spand = [C(Xc, floors[0] - 0.6, za), C(Xc, floors[0] - 0.6, zb)] + [C(Xc, spring, zb - 0.22)] + arc[::-1] + [C(Xc, spring, za + 0.22)]
        out.append(F(spand, PAPER) + tone(U, spand, 2, 100, box=bbox(spand)) + pen(arc, 1.1, seed + i, 0.05))
        arches.append(arc)
    for i in range(n + 1):
        z = Z0 + sp * i
        col = [C(Xc, 0, z - 0.22), C(Xc, 0, z + 0.22), C(Xc, floors[0] - 1.0, z + 0.22), C(Xc, floors[0] - 1.0, z - 0.22)]
        out.append(F(col, PAPER) + H(U, [col[0], pt(col[0], col[1], 0.45), pt(col[3], col[2], 0.45), col[3]], 90, 1.4, 0.6)
                   + sketch(col, 1.0, seed + i, 0.1))
        cap = C.qx(Xc - 0.06, z - 0.32, z + 0.32, floors[0] - 1.25, floors[0] - 1.0)
        bs = C.qx(Xc - 0.06, z - 0.32, z + 0.32, 0, 0.35)
        out.append(F(cap, PAPER) + sketch(cap, 0.8, seed, 0.05) + F(bs, PAPER) + sketch(bs, 0.8, seed, 0.05))
    cor = C.qx(Xc - 0.25, Z0, Z1, top - 0.6, top)
    out.append(F(cor, PAPER) + H(U, cor, 0, 1.3, 0.6) + sketch(cor, 1.0, seed, 0.1))
    out.append(pen([C(Xc, 0, Z0), C(Xc, top, Z0)], 1.4, seed, 0.1))
    return "".join(out)


def classic_car(U, C, Xr, Zc, seed, acc=True):
    """A 1950s American sedan in profile driving along the plane Z = Zc toward +X (Xr = rear bumper): tail fins,
    wraparound glass, two-tone paint (the lower body takes the vermilion), a chrome spear, whitewall tyres."""
    def Pp(u, v):
        return C(Xr + u, v, Zc)

    def path(pts):
        return [Pp(u, v) for u, v in pts]
    out = []
    s_ = abs(Pp(0, 1)[1] - Pp(0, 0)[1])
    # cast shadow
    sh = [C(Xr - 0.1, 0, Zc + 0.1), C(Xr + 5.3, 0, Zc + 0.1), C(Xr + 5.4, 0, Zc + 1.9), C(Xr + 0.1, 0, Zc + 1.9)]
    out.append(F(sh, INK, 0.7))
    body = [(0.0, 0.36), (-0.04, 0.62), (0.0, 0.9), (0.1, 1.12), (0.55, 0.98), (1.3, 0.93), (1.48, 0.96), (1.78, 1.38),
            (2.0, 1.43), (2.95, 1.43), (3.2, 1.36), (3.5, 0.97), (3.7, 0.94), (4.75, 0.9), (5.08, 0.86), (5.22, 0.72),
            (5.2, 0.42), (5.0, 0.3), (4.5, 0.3), (4.45, 0.52), (4.12, 0.72), (3.75, 0.52), (3.7, 0.3), (1.45, 0.3),
            (1.4, 0.52), (1.05, 0.72), (0.7, 0.52), (0.62, 0.3), (0.1, 0.3)]
    bp = path(body)
    out.append(F(bp, PAPER))
    lower = path([(-0.04, 0.62), (0.06, 0.8), (5.15, 0.74), (5.2, 0.66), (5.16, 0.4), (5.0, 0.3), (4.5, 0.3), (4.45, 0.52), (4.12, 0.72),
                  (3.75, 0.52), (3.7, 0.3), (1.45, 0.3), (1.4, 0.52), (1.05, 0.72), (0.7, 0.52), (0.62, 0.3), (0.1, 0.3), (0.0, 0.36)])
    if acc:
        out.append(accent(U, poly(lower), bbox(lower), seed, op=1.0, ang=-4, n=22, length=(10, 26), width=(1.5, 3)))
    out.append(H(U, lower, 0, 2.0, 0.6, span=(0.45, 1), dark=Pp(2.6, 0.2), op=0.85))
    # glass
    glass = path([(1.56, 0.98), (1.82, 1.36), (2.95, 1.37), (3.22, 1.33), (3.44, 0.98)])
    out.append(F(glass, INK, 0.85) + segs([(Pp(2.45, 0.98), Pp(2.42, 1.37)), (Pp(1.95, 0.98), Pp(2.0, 1.36))], 1.2, seed, 0, color=PAPER, op=0.9))
    out.append(segs([(Pp(2.8, 1.33), Pp(3.1, 1.05)), (Pp(2.65, 1.33), Pp(2.9, 1.1))], 0.7, seed, 0.1, color=PAPER, op=0.7))
    # roof shade, chrome spear, trim, handles, lamps, bumpers
    out.append(H(U, path([(1.8, 1.38), (2.0, 1.43), (2.95, 1.43), (3.2, 1.36), (3.18, 1.37), (1.82, 1.36)]), 0, 1.0, 0.5))
    spear = path([(0.3, 0.8), (2.4, 0.8), (2.9, 0.66), (4.9, 0.66)])
    out.append(pen(spear, 1.4, seed, 0.05) + pen([Pp(0.3, 0.83), Pp(2.4, 0.83)], 0.6, seed, 0.05, color=PAPER))
    out.append(segs([(Pp(3.48, 0.95), Pp(3.48, 0.32)), (Pp(1.5, 0.95), Pp(1.5, 0.36))], 0.7, seed, 0))
    out.append(segs([(Pp(3.0, 0.88), Pp(3.2, 0.88)), (Pp(1.65, 0.88), Pp(1.85, 0.88))], 1.4, seed, 0))
    out.append(F(path([(5.02, 0.82), (5.18, 0.8), (5.2, 0.66), (5.02, 0.68)]), PAPER) + pen(path([(5.02, 0.82), (5.18, 0.8), (5.2, 0.66), (5.02, 0.68)]), 0.8, seed, 0.05, True))
    out.append(F(path([(0.0, 0.84), (0.08, 1.04), (0.2, 0.84)]), INK, 0.9))
    out.append(pen(path([(0.12, 1.08), (0.55, 0.96), (1.3, 0.92)]), 0.7, seed, 0.05))
    for bpts in ([(-0.12, 0.34), (0.1, 0.32), (0.12, 0.5), (-0.12, 0.52)], [(5.05, 0.32), (5.32, 0.34), (5.32, 0.52), (5.1, 0.52)]):
        b = path(bpts)
        out.append(F(b, PAPER) + pen(b, 1.1, seed, 0.05, True) + seg(*pt(b[0], b[3], 0.5), *pt(b[1], b[2], 0.5), 0.5, seed, 0))
    out.append(pen(bp, 1.5, seed, 0.1, closed=True))
    # wheels: tyre, whitewall, hubcap
    for u in (1.05, 4.1):
        cx_, cy_ = Pp(u, 0.36)
        rr = s_ * 0.36
        out.append(f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(rr)}" fill="{INK}"/>'
                   f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(rr * 0.68)}" fill="{PAPER}"/>'
                   f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(rr * 0.46)}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
                   f'<circle cx="{f1(cx_)}" cy="{f1(cy_)}" r="{f1(rr * 0.14)}" fill="{INK}"/>')
        out.append(segs([((cx_ + rr * 0.18 * math.cos(a), cy_ + rr * 0.18 * math.sin(a)), (cx_ + rr * 0.42 * math.cos(a), cy_ + rr * 0.42 * math.sin(a)))
                         for a in [k * math.pi / 4 for k in range(8)]], 0.6, seed, 0))
    # driver's head and elbow on the sill
    hx, hy = Pp(2.75, 1.16)
    out.append(f'<circle cx="{f1(hx)}" cy="{f1(hy)}" r="{f1(s_ * 0.13)}" fill="{PAPER}" opacity="0.35"/>')
    return "".join(out)


def morro(U, x, y, s, seed=1):
    """El Morro's headland across the harbour mouth: a low cliff and fortress wall, the lighthouse tower."""
    out = []
    land = [(x - 60 * s, y), (x - 40 * s, y - 6 * s), (x - 10 * s, y - 8 * s), (x + 4 * s, y - 11 * s), (x + 30 * s, y - 10 * s),
            (x + 60 * s, y - 4 * s), (x + 80 * s, y)]
    out.append(F(land, PAPER) + H(U, land, 0, 1.6, 0.6) + pen(land, 0.9, seed, 0.1))
    fort = rect(x - 18 * s, y - 13 * s, x + 14 * s, y - 8 * s)
    out.append(F(fort, PAPER) + H(U, fort, 90, 1.4, 0.5) + sketch(fort, 0.8, seed, 0.1))
    t = [(x - 2.4 * s, y - 13 * s), (x + 2.4 * s, y - 13 * s), (x + 1.7 * s, y - 34 * s), (x - 1.7 * s, y - 34 * s)]
    out.append(F(t, PAPER) + H(U, [t[0], pt(t[0], t[1], 0.4), pt(t[3], t[2], 0.4), t[3]], 90, 1.0, 0.5) + pen(t, 0.9, seed, 0.05, True))
    lt = rect(x - 2.2 * s, y - 38 * s, x + 2.2 * s, y - 34 * s)
    out.append(F(lt, INK, 0.85) + F([(x - 2.6 * s, y - 38 * s), (x, y - 41 * s), (x + 2.6 * s, y - 38 * s)], INK))
    out.append(segs([((x - 2.6 * s, y - 34 * s), (x + 2.6 * s, y - 34 * s))], 1.0, seed, 0))
    return "".join(out)


@design("havana")
def havana(U):
    """Old Havana in the late afternoon: a colonial street running gently down to the Malecón, its sunlit left
    side all mediopunto fanlights, iron balconies, washing and peeling stucco, the right side an arcade of
    columns in deep shade; overhead wires, a royal palm, boys with a bat and ball, a 1950s sedan rolling past in
    the foreground (the vermilion), and at the end the sea wall, a wave bursting over it and El Morro's lighthouse."""
    art = []
    C = SlopeCam(f=232, cx=300, vpy=292, eye=1.9)
    yH = C.vpy
    gy = -HAV_SLOPE * HAV_END
    art.append(cloud(U, 300, 84, 104, 16, 81))
    art.append(cloud(U, 262, 196, 64, 10, 82))
    # the sea beyond the wall, El Morro, a ship on the horizon
    art.append(F(rect(200, yH, 420, yH + 60), PAPER))
    art.append(morro(U, 352, yH + 1, 0.7, 83))
    art.append(icf.ripples(U, 200, 420, yH, C(0, gy + 0.8, 31)[1], 84, dens=1.3, gap=(1.4, 4.0), ln=((2, 6), (6, 16)), w=(0.7, 1.2)))
    art.append(seg(200, yH, 420, yH, 1.0, 85, 0))
    sx_ = 268
    art.append(F([(sx_ - 7, yH - 1), (sx_ + 8, yH - 1), (sx_ + 6, yH + 1.5), (sx_ - 6, yH + 1.5)], INK) + seg(sx_, yH - 1, sx_, yH - 7, 0.8, 1, 0))
    # the Malecón: road, sea wall, a wave bursting over it
    mal = [C(-30, gy, HAV_END), C(30, gy, HAV_END), C(30, gy, 31), C(-30, gy, 31)]
    art.append(F(mal, PAPER) + H(U, mal, 0, 1.7, 0.6, op=0.7))
    sw = [C(-30, gy + 0.8, 31), C(30, gy + 0.8, 31), C(30, gy, 31), C(-30, gy, 31)]
    art.append(F(sw, PAPER) + H(U, sw, 0, 1.0, 0.5) + pen([sw[0], sw[1]], 1.3, 86, 0.05))
    bx, by = C(1.3, gy + 0.8, 31.5)
    rnd = random.Random(87)
    plume = []
    for k in range(17):
        t = k / 16
        a = math.pi * (1 + t)
        r = 22 * (0.75 + 0.45 * math.sin(t * math.pi)) * (1.18 if k % 2 else 0.86)
        plume.append((bx + math.cos(a) * r * 1.15, by + math.sin(a) * r * 1.5 * (0.6 + 0.4 * math.sin(t * math.pi))))
    pd = smooth_closed(plume)
    art.append(F(pd, PAPER) + ST(U, pd, 260, light=(bx, by - 40), r=(0.4, 0.9), op=0.85, box=(bx - 40, by - 48, bx + 40, by + 2))
               + H(U, pd, 0, 1.5, 0.55, span=(0.7, 1), dark=(bx, by + 10), box=(bx - 40, by - 48, bx + 40, by + 2)) + P(pd, 0.8))
    jets = []
    for k in range(9):
        a = math.radians(-90 + (k - 4) * 16)
        r0, r1 = rnd.uniform(18, 26), rnd.uniform(34, 46)
        jets.append(((bx + math.cos(a) * r0, by + math.sin(a) * r0), (bx + math.cos(a) * r1, by + math.sin(a) * r1)))
    art.append(segs(jets, 0.7, 88, 0.6, op=0.8))
    drops = "".join(f'<circle cx="{f1(bx + rnd.uniform(-36, 36))}" cy="{f1(by - rnd.uniform(20, 52))}" r="{rnd.uniform(0.6, 1.3):.1f}" fill="{INK}"/>' for _ in range(30))
    art.append(drops)
    x_, y_ = C(-3.4, gy, 28)
    art.append(palm(U, x_, y_, C.f * 17 / 28, 88, lean=-0.04, fronds=11, span=0.85, w=1.3))
    # the street: worn asphalt down the middle, sidewalks
    road = [C(-5.0, 0, 2.0), C(-5.0, 0, HAV_END), C(5.5, 0, HAV_END), C(5.5, 0, 2.0)]
    art.append(F(road, PAPER) + H(U, road, 0, (3.2, 1.8), 0.6, op=0.4, dark=(300, 620), wob=0.3, brk=0.3))
    art.append(clipped(U("cb"), poly(road), cobbles(U, C, -5.0, 5.5, 2.0, HAV_END, 89, row=0.32, stone=0.42, w=0.7, op=0.65)))
    art.append(H(U, [C(2.5, 0, 2.0), C(2.5, 0, HAV_END), C(5.5, 0, HAV_END), C(5.5, 0, 2.0)], 80, 2.8, 0.6, op=0.6))
    for i in range(18):      # patches and cracks in the old asphalt
        z = rnd.uniform(3, 20)
        X = rnd.uniform(-4.5, 4.5)
        a, b = C(X, 0, z), C(X + rnd.uniform(-0.8, 0.8), 0, z + rnd.uniform(0.3, 1.2))
        art.append(seg(a[0], a[1], b[0], b[1], 0.7, 90 + i, 0.6))
    lw_ = [C(-6.6, 0.15, 2.0), C(-6.6, 0.15, HAV_END), C(-5.0, 0.15, HAV_END), C(-5.0, 0.15, 2.0)]
    art.append(F(lw_, PAPER) + clipped(U("lw"), poly(lw_), segs([(C(-6.6, 0.15, z), C(-5.0, 0.15, z)) for z in [2 + i * 0.8 for i in range(28)]], 0.5, 91, 0, op=0.5)))
    art.append(pen([C(-5.0, 0.15, 2.0), C(-5.0, 0.15, HAV_END)], 1.5, 92, 0.05) + pen([C(-5.0, 0, 2.0), C(-5.0, 0, HAV_END)], 0.8, 93, 0.05))
    # left: sunlit colonial fronts, far to near
    lf = [(18.5, HAV_END, 12.6, (4.8, 8.8), 1, False), (12.5, 18.5, 9.6, (4.8,), 0, False), (6.5, 12.5, 13.4, (4.8, 8.8), 1, True),
          (2.6, 6.5, 13.0, (4.8, 8.8), 1, False)]
    for i, (z0, z1, top, fl, lvl, wash) in enumerate(lf):
        art.append(habana_front(U, C, -6.6, z0, z1, top, 300 + i * 9, floors=fl, lvl=lvl, wash=wash))
    # right: the arcade in shade
    art.append(portales(U, C, 5.5, 8.6, 13, HAV_END, 13.4, 320, span=2.75))
    art.append(portales(U, C, 5.5, 8.6, 2.6, 13, 14.2, 330, span=3.47))
    # wires sagging across the street
    for (za, ya, zb, yb, sag) in ((6, 11.5, 9, 12.5, 22), (15, 10.0, 11, 11.2, 14), (20, 9.5, 22, 10.5, 8), (8, 12.6, 16, 11.8, 18)):
        a, b = C(-6.5, ya, za), C(5.4, yb, zb)
        art.append(P(f"M {f1(a[0])} {f1(a[1])} Q {f1((a[0] + b[0]) / 2)} {f1((a[1] + b[1]) / 2 + sag)} {f1(b[0])} {f1(b[1])}", 0.8))
    # life: boys playing ball in the street, neighbours in doorways and under the arcade, a dog
    for X, z, sd, kind, fl in ((-5.6, 9.0, 341, "dress", False), (-5.5, 16.5, 342, "plain", True), (6.6, 10.5, 343, "hat", True),
                               (6.8, 17.5, 344, "plain", False), (-2.0, 19.0, 345, "plain", True), (6.2, 6.4, 346, "bag", False)):
        x, y = C(X, 0.15 if abs(X) > 5 else 0, z)
        art.append(walker(x, y, C.f * 1.7 / z, sd, flip=fl, kind=kind))
    x, y = C(-0.5, 0, 14.0)
    h = C.f * 1.35 / 14
    art.append(person(x, y, h, 347) + nib([(x + h * 0.08, y - h * 0.62), (x + h * 0.32, y - h * 1.0), (x + h * 0.45, y - h * 1.25)], 1.4, taper=(0.6, 1.1), seed=1, color=INK))
    x2, y2 = C(1.6, 0, 16.5)
    art.append(person(x2, y2, C.f * 1.3 / 16.5, 348, flip=True) + f'<circle cx="{f1((x + x2) / 2 + 6)}" cy="{f1(y - h * 1.5)}" r="1.3" fill="{INK}"/>')
    # the car
    art.append(classic_car(U, C, -3.8, 6.6, 349))
    art.append(bird(232, 128, 6, 350) + bird(250, 116, 4.5, 351) + gull(352, 152, 6, 352))
    return plate(U, "havana", art, 85)


# ================================================================ BARCELONA
def spire(U, cx, base, top, w0, seed, shade=0.42, finial="mitre", holes=True, lw=1.2):
    """A tall, tapering, perforated basilica spire in elevation: a parabolic shaft pierced by spiralling rows of
    slits, the shadow side hatched, crowned by a mitre of knobbed lobes (or a star cross)."""
    rnd = random.Random(seed)
    H_ = base - top
    n = 18
    L, R = [], []
    for i in range(n + 1):
        t = i / n
        hw = w0 * (1 - t ** 1.7) * (1 - 0.18 * t) + w0 * 0.12
        y = base - H_ * 0.86 * t
        L.append((cx - hw, y))
        R.append((cx + hw, y))
    shaft = L + R[::-1]
    out = [F(shaft, PAPER)]
    sh = [pt(l_, r_, 1 - shade) for l_, r_ in zip(L, R)] + R[::-1]
    out.append(H(U, sh, 90, 1.3, 0.6, wob=0.1, brk=0.05))
    out.append(H(U, shaft, 0, 3.2, 0.45, op=0.5, wob=0.1, brk=0.2))
    if holes:
        sl = []
        for j in range(int(H_ * 0.72 / 6)):
            t = (j + 0.5) / (H_ * 0.72 / 6) * 0.82
            y = base - H_ * 0.86 * t
            hw = w0 * (1 - t ** 1.7) * (1 - 0.18 * t) + w0 * 0.12
            k = 3 if hw > 6 else 2
            for m_ in range(k):
                ph = (m_ + 0.5 + 0.5 * (j % 2)) / k
                x = cx - hw + 2 * hw * ph * 0.92 + hw * 0.04
                sl.append(rect(x - 0.6, y - 2.6, x + 0.6, y))
        out.append(F(" ".join(poly(r_) for r_ in sl), INK, 0.85))
    out.append(pen(L, lw, seed, 0.05, smooth=True) + pen(R, lw * 1.2, seed + 1, 0.05, smooth=True))
    tx, ty = cx, base - H_ * 0.86
    s = w0 * 0.55 + 1
    if finial == "mitre":
        # the knobbed pinnacle: a stack of lobes and a crown of small balls
        stem = [(tx - s * 0.8, ty), (tx + s * 0.8, ty), (tx + s * 0.4, ty - H_ * 0.08), (tx - s * 0.4, ty - H_ * 0.08)]
        out.append(F(stem, PAPER) + pen(stem, 0.9, seed, 0.05, True) + H(U, [pt(stem[0], stem[1], 0.6), stem[1], stem[2], pt(stem[3], stem[2], 0.6)], 90, 1.2, 0.5))
        my = ty - H_ * 0.08
        cap = smooth_closed([(tx - s * 1.3, my), (tx + s * 1.3, my), (tx + s * 1.1, my - s * 2.2), (tx, my - s * 3.4), (tx - s * 1.1, my - s * 2.2)])
        out.append(F(cap, PAPER) + clipped(U("mt"), cap, H(U, cap, 60, 1.4, 0.6, box=(tx - s * 2, my - s * 4, tx + s * 2, my + 1), span=(0.45, 1)))
                   + P(cap, 1.0))
        for a in (-0.9, -0.45, 0, 0.45, 0.9):
            bx, by = tx + math.sin(a) * s * 1.35, my - s * 1.4 - math.cos(a) * s * 1.6
            out.append(f'<circle cx="{f1(bx)}" cy="{f1(by)}" r="{f1(max(0.9, s * 0.38))}" fill="{PAPER}" stroke="{INK}" stroke-width="0.8"/>')
        out.append(f'<circle cx="{f1(tx)}" cy="{f1(my - s * 3.6)}" r="{f1(max(1.0, s * 0.5))}" fill="{INK}"/>')
    else:
        # a star-cross on a slender needle
        out.append(seg(tx, ty, tx, ty - H_ * 0.1, 1.3, seed, 0))
        cy_ = ty - H_ * 0.1
        r = s * 1.6
        out.append(segs([((tx - r, cy_), (tx + r, cy_)), ((tx, cy_ - r), (tx, cy_ + r)), ((tx - r * 0.7, cy_ - r * 0.7), (tx + r * 0.7, cy_ + r * 0.7)),
                         ((tx - r * 0.7, cy_ + r * 0.7), (tx + r * 0.7, cy_ - r * 0.7))], 1.3, seed, 0))
        out.append(f'<circle cx="{f1(tx)}" cy="{f1(cy_)}" r="{f1(r * 0.35)}" fill="{INK}"/>')
    return "".join(out)


def basilica(U, cx, base, s, seed=1):
    """A great generic basilica of spires in elevation (s px per metre): two rows of perforated bell towers, the
    taller crossing tower behind, apse pinnacles, a gabled portal with sculpted relief between the front towers,
    and a construction crane at work beside it."""
    out = []

    def X(m):
        return cx + m * s

    def Y(m):
        return base - m * s
    # crane behind, to the right
    mx = X(52)
    mast = rect(mx - 1.6 * s, Y(118), mx + 1.6 * s, base)
    out.append(segs([((mast[0][0], mast[0][1]), (mast[3][0], mast[3][1])), ((mast[1][0], mast[1][1]), (mast[2][0], mast[2][1]))], 0.9, seed, 0))
    zz = []
    y = base
    k = 0
    while y > Y(118):
        y2 = y - 3.2 * s
        zz.append(((mast[0][0] if k % 2 else mast[1][0], y), (mast[1][0] if k % 2 else mast[0][0], y2)))
        y = y2
        k += 1
    out.append(segs(zz, 0.6, seed, 0))
    jib = [(X(20), Y(118)), (X(74), Y(118)), (X(74), Y(115.5)), (X(20), Y(115.5))]
    out.append(pen([jib[0], jib[1]], 1.0, seed, 0.02) + pen([jib[3], jib[2]], 0.9, seed, 0.02)
               + segs([((X(20 + 2.5 * i), Y(118)), (X(22.5 + 2.5 * i), Y(115.5))) for i in range(21)], 0.5, seed, 0))
    out.append(segs([((mx, Y(126)), (X(30), Y(118))), ((mx, Y(126)), (X(70), Y(118))), ((mx, Y(126)), (mx, Y(118)))], 0.7, seed, 0))
    out.append(F(rect(X(24), Y(117), X(28), Y(112)), INK) + seg(X(64), Y(115.5), X(64), Y(92), 0.6, seed, 0)
               + F(rect(X(62.5), Y(92), X(65.5), Y(89)), INK))
    # apse pinnacles and the far towers (paler)
    for m, h, w in ((-44, 70, 4.2), (44, 70, 4.2), (-22, 108, 4.6), (22, 108, 4.6)):
        out.append(spire(U, X(m), base, Y(h), w * s, seed + m, shade=0.45, holes=True, lw=1.0))
    # the crossing tower, tallest, with its star
    out.append(spire(U, X(0), base, Y(150), 9.5 * s, seed + 3, shade=0.4, finial="star", lw=1.4))
    for m in (-9, 9):
        out.append(spire(U, X(m), base, Y(122), 5.0 * s, seed + 5 + m, shade=0.45, holes=False, lw=1.0))
    # nave roof and pinnacles
    nave = [(X(-38), Y(44)), (X(-30), Y(58)), (X(30), Y(58)), (X(38), Y(44)), (X(38), base), (X(-38), base)]
    out.append(F(nave, PAPER) + H(U, nave, 0, 2.6, 0.5, op=0.7) + pen(nave[:4], 1.1, seed, 0.05))
    for m in range(-34, 36, 6):
        h = 58 if abs(m) < 30 else 48
        out.append(F([(X(m - 1.2), Y(h)), (X(m), Y(h + 8)), (X(m + 1.2), Y(h))], PAPER) + pen([(X(m - 1.2), Y(h)), (X(m), Y(h + 8)), (X(m + 1.2), Y(h))], 0.8, seed + m, 0.02))
    # front: four bell towers and the portal between
    gab = [(X(-14), Y(46)), (X(0), Y(72)), (X(14), Y(46)), (X(14), base), (X(-14), base)]
    out.append(F(gab, PAPER) + ST(U, gab, 900, light=(X(-20), Y(80)), r=(0.4, 0.9), op=0.75) + H(U, [(X(3), Y(66)), (X(14), Y(46)), (X(14), base), (X(3), base)], 90, 1.6, 0.6)
               + pen(gab[:3], 1.2, seed, 0.05))
    out.append(F([(X(-5), Y(30)), (X(0), Y(42)), (X(5), Y(30)), (X(5), base), (X(-5), base)], INK, 0.85))
    for m, h, w in ((-26, 98, 5.6), (-11, 112, 5.4), (11, 112, 5.4), (26, 98, 5.6)):
        out.append(spire(U, X(m), base, Y(h), w * s, seed + 20 + m, shade=0.42, lw=1.3))
    return "".join(out)


def eix_front(U, C, a, b, top, seed, lit=True, floors=6, tribune=False, shops=True):
    """An Eixample apartment front between ground points a=(X, Z) and b=(X, Z): a tall shop storey, five floors
    of balconied French windows (iron rails, shutters), a cornice and a roof terrace with a water tank."""
    rnd = random.Random(seed)
    (xa, za), (xb, zb) = a, b
    q = [C(xa, top, za), C(xb, top, zb), C(xb, 0, zb), C(xa, 0, za)]
    m = homog(q)
    out = [F(q, PAPER)]
    L = math.hypot(xb - xa, zb - za)
    cols = max(2, int(L / 3.4))
    # storey lines
    gh = 5.0
    fh = (top - gh - 1.2) / (floors - 1)
    ys = [gh + fh * j for j in range(floors - 1)]
    out.append(segs([(m(0, 1 - y / top), m(1, 1 - y / top)) for y in [gh] + [top - 1.2]], 0.7, seed, 0, op=0.8))
    wins = []
    for i in range(cols):
        u0, u1 = (i + 0.3) / cols, (i + 0.7) / cols
        for y in ys:
            v0, v1 = 1 - (y + fh * 0.82) / top, 1 - (y + 0.25) / top
            wins.append([m(u0, v0), m(u1, v0), m(u1, v1), m(u0, v1)])
    out.append(F(" ".join(poly(w) for w in wins), INK, 0.86))
    # balcony slabs + rails (drawn as thicker bars under each window)
    rl = []
    for w in wins:
        bl, br = w[3], w[2]
        dy = abs(w[3][1] - w[0][1]) * 0.32
        rl.append(((bl[0] - 1, bl[1]), (br[0] + 1, br[1])))
        rl.append(((bl[0] - 1, bl[1] - dy), (br[0] + 1, br[1] - dy)))
    out.append(segs(rl, 0.9, seed, 0))
    if abs(q[1][0] - q[0][0]) / cols > 9:
        bars = []
        for w in wins:
            dy = abs(w[3][1] - w[0][1]) * 0.32
            for t in (0.2, 0.4, 0.6, 0.8):
                p = pt(w[3], w[2], t)
                bars.append((p, (p[0], p[1] - dy)))
        out.append(segs(bars, 0.5, seed + 1, 0))
    if tribune:     # a glazed gallery stacked up the middle of the front
        uc = 0.5
        tq = [m(uc - 0.09, 1 - (top - 2.5) / top), m(uc + 0.09, 1 - (top - 2.5) / top), m(uc + 0.09, 1 - gh / top), m(uc - 0.09, 1 - gh / top)]
        out.append(F(tq, PAPER) + segs([(pt(tq[0], tq[3], t), pt(tq[1], tq[2], t)) for t in [j / 12 for j in range(13)]], 0.6, seed, 0)
                   + segs([(pt(tq[0], tq[1], t), pt(tq[3], tq[2], t)) for t in (0.33, 0.66)], 0.5, seed, 0) + sketch(tq, 1.0, seed, 0.1))
    # shops: dark openings and awnings
    if shops:
        sh = []
        for i in range(cols):
            u0, u1 = (i + 0.15) / cols, (i + 0.85) / cols
            sh.append([m(u0, 1 - 4.0 / top), m(u1, 1 - 4.0 / top), m(u1, 1), m(u0, 1)])
        out.append(F(" ".join(poly(w) for w in sh), INK, 0.8))
    # cornice + roof terrace
    cq = [m(0, 0), m(1, 0), m(1, 1.2 / top), m(0, 1.2 / top)]
    out.append(F(cq, PAPER) + H(U, cq, 0, 1.4, 0.6) + sketch(cq, 1.0, seed, 0.1))
    if not lit:
        out.append(tone(U, q, 2, 70, box=bbox(q)))
    else:
        out.append(H(U, q, 100, 4.0, 0.5, op=0.45, wob=0.2, brk=0.2))
    # water tank / stair hut on the roof
    zc = lerp(za, zb, rnd.uniform(0.3, 0.7))
    xc = lerp(xa, xb, 0.5) + (-3 if xa < 0 else 3)
    hut = [C(xc, top + 2.6, zc - 1.5), C(xc, top + 2.6, zc + 1.5), C(xc, top, zc + 1.5), C(xc, top, zc - 1.5)]
    out.append(F(hut, PAPER) + H(U, hut, 90, 1.6, 0.6, op=0.8) + sketch(hut, 0.9, seed, 0.1))
    out.append(sketch(q, 1.2, seed, 0.2))
    return "".join(out)


def iron_balcony(U, x0, x1, ytop, ybot, seed):
    """Our own balcony rail in the foreground, face-on: heavy handrail, bars, a band of S-scrolls and rings."""
    out = []
    out.append(F(rect(x0, ytop - 5, x1, ytop + 3), INK) + seg(x0, ytop - 3.5, x1, ytop - 3.5, 0.8, seed, 0.1, color=PAPER))
    out.append(F(rect(x0, ybot - 4, x1, ybot + 6), INK))
    bars = []
    step = 15
    x = x0 + step / 2
    while x < x1:
        bars.append(((x, ytop + 3), (x, ybot - 4)))
        x += step
    out.append(segs(bars, 2.2, seed, 0.2))
    sc = []
    x = x0 + step / 2
    k = 0
    my = ytop + (ybot - ytop) * 0.5
    while x + step < x1 + 1:
        cx_ = x + step / 2
        r = step * 0.42
        sc.append(f"M {f1(cx_ - r)} {f1(my)} a {f1(r)} {f1(r)} 0 1 1 {f1(2 * r)} 0 a {f1(r)} {f1(r)} 0 1 1 {f1(-2 * r)} 0")
        sc.append(f"M {f1(x)} {f1(ytop + 6)} Q {f1(cx_)} {f1(ytop + 16)} {f1(x + step)} {f1(ytop + 6)}")
        sc.append(f"M {f1(x)} {f1(ybot - 7)} Q {f1(cx_)} {f1(ybot - 17)} {f1(x + step)} {f1(ybot - 7)}")
        x += step
        k += 1
    out.append(P(" ".join(sc), 1.4))
    return "".join(out)


def geranium_pot(U, x, y, s, seed, acc=True):
    """A terracotta pot of geraniums on the balcony: a tapered pot, scalloped leaves, flower heads in vermilion."""
    rnd = random.Random(seed)
    pot = [(x - s * 0.5, y - s * 0.75), (x + s * 0.5, y - s * 0.75), (x + s * 0.38, y), (x - s * 0.38, y)]
    out = [F(pot, PAPER) + H(U, pot, 90, 1.6, 0.7, span=(0.5, 1), dark=(x + s, y)) + pen(pot, 1.3, seed, 0.1, True)
           + F(rect(x - s * 0.55, y - s * 0.85, x + s * 0.55, y - s * 0.72), PAPER) + sketch(rect(x - s * 0.55, y - s * 0.85, x + s * 0.55, y - s * 0.72), 1.1, seed, 0.1)]
    for k in range(6):
        lx, ly = x + rnd.uniform(-0.7, 0.7) * s, y - s * rnd.uniform(0.9, 1.4)
        out.append(lobe(U, lx, ly, s * 0.32, s * 0.24, seed * 7 + k, light=(-1, -1), w=1.0, dense=1.6))
    heads = []
    for k in range(4):
        hx, hy = x + rnd.uniform(-0.6, 0.6) * s, y - s * rnd.uniform(1.5, 1.95)
        out.append(seg(hx, hy, hx + rnd.uniform(-3, 3), hy + s * 0.4, 1.0, seed + k, 0.2))
        heads.append(smooth_closed(scallop_pts(hx, hy, s * 0.2, s * 0.17, seed + k * 3, 9, 0.35)))
    d = " ".join(heads)
    out.append(F(d, PAPER))
    if acc:
        out.append(accent(U, d, (x - s * 1.2, y - s * 2.4, x + s * 1.2, y - s * 1.2), seed, op=1.0, ang=-30, n=26, length=(3, 8), width=(1.4, 2.6)))
    out.append(P(d, 0.9))
    return "".join(out)


@design("barcelona")
def barcelona(U):
    """Morning from a fourth-floor balcony in the Eixample: a tree-lined avenue runs straight to a great basilica
    whose perforated spires (and a crane at work) rise over the far roofs; apartment fronts with balconies and
    tribunes, chamfered corners at the crossing, plane trees, strollers, a scooter and a bus; our own iron
    balcony across the foot of the picture, its pots of geraniums the vermilion accent."""
    art = []
    C = Cam(f=250, cx=300, vpy=262, eye=13.0)
    art.append(cloud(U, 170, 92, 96, 14, 91))
    art.append(cloud(U, 446, 120, 80, 12, 92))
    art.append(bird(392, 160, 6, 93) + bird(408, 148, 4.5, 94) + bird(206, 176, 5, 95))
    # the basilica beyond the crossing
    yb = C(0, 0, 150)[1]
    art.append(basilica(U, 300, yb, 250 / 150, 96))
    # buildings beyond the cross street, either side of the basilica square (far, pale)
    for xa, xb in ((-80, -17), (17, 80)):
        q = C.qz(135, xa, xb, 0, 22)
        art.append(F(q, PAPER) + window_grid(U, q[0][0] + 2, q[1][0] - 2, q[0][1] + 6, q[3][1] - 4, max(2, int(abs(q[1][0] - q[0][0]) / 9)), 5, 97, dark=0.6)
                   + H(U, q, 90, 2.8, 0.5, op=0.6) + sketch(q, 1.0, 98, 0.1))
    # the avenue: side roads, a central promenade between plane trees
    ground = [C(-17, 0, 24), C(-17, 0, 135), C(17, 0, 135), C(17, 0, 24)]
    art.append(F(ground, PAPER))
    prom = [C(-8, 0, 24), C(-8, 0, 115), C(8, 0, 115), C(8, 0, 24)]
    art.append(clipped(U("pv"), poly(prom), cobbles(U, C, -8, 8, 24, 115, 99, row=1.6, stone=2.4, w=0.6, op=0.5)))
    for sx in (-1, 1):
        rd = [C(sx * 8, 0, 24), C(sx * 8, 0, 115), C(sx * 14, 0, 115), C(sx * 14, 0, 24)]
        art.append(H(U, rd, 90, 3.0, 0.55, op=0.55))
        art.append(pen([C(sx * 8, 0, 24), C(sx * 8, 0, 115)], 1.1, 100, 0.05) + pen([C(sx * 14, 0, 24), C(sx * 14, 0, 115)], 1.1, 101, 0.05))
        art.append(segs([(C(sx * 11, 0, z), C(sx * 11, 0, z + 3)) for z in range(26, 112, 7)], 1.0, 102, 0))
    # the cross street at the far end of the block
    cs = [C(-60, 0, 115), C(-60, 0, 135), C(60, 0, 135), C(60, 0, 115)]
    art.append(H(U, cs, 0, 2.0, 0.55, op=0.6) + segs([(C(X, 0, 117), C(X, 0, 133)) for X in range(-12, 13, 3)], 1.6, 103, 0, color=PAPER))
    # left fronts in shade, right fronts lit, two buildings to each side of the block
    for sx, lit in ((-1, False), (1, True)):
        art.append(eix_front(U, C, (sx * 17, 64), (sx * 17, 115), 22, 114 + sx, lit=lit, tribune=True))
        art.append(eix_front(U, C, (sx * 17, 14), (sx * 17, 64), 23.5, 116 + sx, lit=lit, tribune=True))
    # plane trees along the promenade, far to near
    for sx in (-1, 1):
        for i, z in enumerate([108 - 7.5 * k for k in range(11)]):
            x, y = C(sx * 7.0, 0, z)
            h = 250 * 9.5 / z
            art.append(tree(U, x, y, h, 250 * 6.4 / z, 400 + i * 2 + (sx > 0), light=(-1, -1), trunk_h=0.38, lobes=6,
                            lw=max(0.8, min(1.6, 30 / z)), dense=1.1))
    # life on the promenade, a bus and a scooter in the side roads
    rnd = random.Random(104)
    for k in range(24):
        z = rnd.uniform(30, 100)
        X = rnd.uniform(-5, 5)
        x, y = C(X, 0, z)
        art.append(walker(x, y, 250 * 1.7 / z, 410 + k, flip=rnd.random() < 0.5, kind=rnd.choice(("plain", "dress", "bag", "plain"))))
    # our balcony: the shutter of our window on the left, the rail, the pots
    sh_ = [(34, 40), (84, 40), (80, 440), (34, 440)]
    art.append(louvered(U, sh_, 106, dark=False, w=0.8, slats=56) + H(U, sh_, 75, 2.0, 0.7))
    art.append(iron_balcony(U, 20, 580, 382, 440, 107))
    for x, s, sd in ((128, 34, 108), (170, 28, 109), (488, 30, 110)):
        art.append(geranium_pot(U, x, 379, s, sd))
    return plate(U, "barcelona", art, 95)


def main(slugs):
    for slug, fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save(COL, slug, fn(Ids(slug)))
        print("wrote", slug)


if __name__ == "__main__":
    main(sys.argv[1:])
