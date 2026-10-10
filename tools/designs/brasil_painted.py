"""Brasil, hand-painted (gouache / storybook) edition: 30 magnets for Brazilians abroad and anyone who loves Brazil.

Repaints the six original Brasil designs (saudade, bom-dia, cafe-com-leite, tamo-junto, brasil, cafune) with the
same slugs and words, and adds 24 new ones, all in Brazilian Portuguese. Everything is painted in the house gouache
idiom: warm paper, layered washes with pooled edges, brush strokes that follow each form, a warm brown pen line,
hand-placed brush lettering, soft light and paper grain. Colour story: Brazilian greens, sunny yellows, cobalt and
azulejo blues, terracotta, tropical pinks.

Run from tools/designs:  python3 brasil_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, qpts, catmull, steam_wisps)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import (rot, rect_pts, poly_pts, frond, palm, puff_cloud, sparkle, wave_lines, hibiscus, monstera,
                            stripes_in, sea, banana_leaf, hammock, seagull, umbrella_top, towel_top)
import holidays_gouache as hg

COL = "brasil"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
VERDE = ("#7CCB7A", "#1F8A4C", "#0E5230")
MATA = ("#5E9A5A", "#2E6A3A", "#163E22")
AMAR = ("#FFE58A", "#F6C21C", "#C08A0A")
AZUL = ("#6A96DE", "#1F4FA0", "#0E2A62")
COBALT = ("#5A7ED0", "#1E3F9A", "#0C2060")
TERRA = ("#EE9E72", "#C8603A", "#7A3218")
ROSA = ("#FFA8C0", "#E8507A", "#A82450")
TURQ = ("#8EE0D8", "#1FA5A0", "#0E6464")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
CHOC = ("#7A4A30", "#4A2614", "#24100A")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
RED = ("#F28A7A", "#D8382E", "#8A1414")
ORANGE = ("#FFC07A", "#F2872A", "#B04E0E")
PURPLE = ("#B48AE0", "#6A3AB0", "#36186A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Doc2(Doc):
    """fall_painted.Doc plus the Pn interface (id / lg / rg / glow) so holidays_gouache helpers work with it."""

    def id(self, p="g"):
        return self.nid()

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        return self.lin(stops, x1, y1, x2, y2, units)[5:-1]

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        return self.rad(stops, cx, cy, r, fx, fy)[5:-1]

    def glow(self, x, y, r, col, s=0.7, ry=None):
        g = self.rad([(0, col, s), (0.35, col, s * 0.5), (1, col, 0)])
        if ry:
            return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{g}"/>'


lt, dk = hg.lt, hg.dk


# ================================================================ brasil toolkit
def ell_pts(cx, cy, rx, ry, a0=0, a1=360, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def pd(pts, close=True):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")


def shade_over(D, d, col="#1A0A04", op=0.4, x1=0, y1=0, x2=1, y2=1, start=0.35):
    """Gradient shadow laid over a form (transparent toward the light, `col` on the far side)."""
    g = D.lin([(0, col, 0), (start, col, 0), (1, col, op)], x1, y1, x2, y2)
    return f'<path d="{d}" fill="{g}"/>'


def light_over(D, d, col="#FFFFFF", op=0.45, x1=0, y1=0, x2=1, y2=1, end=0.55):
    g = D.lin([(0, col, op), (end, col, 0)], x1, y1, x2, y2)
    return f'<path d="{d}" fill="{g}"/>'


def gingham(D, d, col, base="#FFFFFF", cell=13, rot_=0, op=0.55):
    c = cell
    pat = D.pattern(2 * c, 2 * c, f'<rect width="{2 * c}" height="{2 * c}" fill="{base}"/>'
                                   f'<rect width="{c}" height="{2 * c}" fill="{col}" opacity="{op}"/>'
                                   f'<rect width="{2 * c}" height="{c}" fill="{col}" opacity="{op}"/>',
                    transform=f"rotate({rot_})" if rot_ else "")
    return f'<path d="{d}" fill="{pat}"/>'


def cloth(D, pts, col, seed, base="#FFFDF6", cell=12, rot_=0, light=(0.2, 0.0, 0.8, 1.0), inkw=1.8, folds=()):
    """Checked cotton cloth: gingham, soft fold shadows, woven brush texture, pen line."""
    d = smooth_closed(pts)
    out = [gingham(D, d, col, base, cell, rot_)]
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for (a, b, c) in folds:
        inner.append(taper([a, b, c], 10, 2, "#2A0E06", 0.18))
        inner.append(taper([(a[0] - 5, a[1] - 3), (b[0] - 5, b[1] - 3), (c[0] - 5, c[1] - 3)], 5, 1, "#FFFFFF", 0.35))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(shade_over(D, d, "#2A0E06", 0.35, *light))
    x0, y0, x1, y1 = bbox(pts)
    out.append(strokes(D.nid(), d, (x0, y0, x1, y1), ["#FFFFFF", dk(col, 0.3)], seed, n=int((x1 - x0) * (y1 - y0) / 300) + 10,
                       angle=rot_ - 10, length=(8, 24), width=(0.8, 2), opacity=(0.1, 0.3), curve=0.1))
    if inkw:
        out.append(ink(d, INK, inkw, seed, 2, 0.7))
    return "".join(out)


def chita_tile(cell, bg, cols, leaf_c, seed):
    """One tile of chita (Brazilian floral cotton): big round flowers with dark centres, leaves and dots."""
    rnd = random.Random(seed)
    out = [f'<rect width="{cell}" height="{cell}" fill="{bg}"/>']
    spots = [(0.25, 0.25, 0.2), (0.75, 0.72, 0.21), (0.78, 0.2, 0.11), (0.2, 0.78, 0.12), (0.5, 0.5, 0.07)]
    for k, (fx, fy, fr) in enumerate(spots):
        for dx in (-cell, 0, cell):
            for dy in (-cell, 0, cell):
                cx, cy, r = fx * cell + dx, fy * cell + dy, fr * cell
                if cx + 2 * r < 0 or cx - 2 * r > cell or cy + 2 * r < 0 or cy - 2 * r > cell:
                    continue
                c = cols[k % len(cols)]
                if fr > 0.15:
                    for j in range(3):
                        a = rnd.uniform(0, 6.28) + j * 2.1
                        lx, ly = cx + math.cos(a) * r * 1.15, cy + math.sin(a) * r * 1.15
                        out.append(f'<path d="{blob(lx, ly, r * 0.55, r * 0.24, seed + k * 7 + j, 0.1, 10, math.degrees(a))}" fill="{leaf_c}"/>')
                    for j in range(6):
                        a = math.radians(j * 60 + k * 17)
                        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5, r * 0.55, r * 0.45, seed + j + k, 0.12, 10, math.degrees(a))}" fill="{c}"/>')
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.42:.1f}" fill="{dk(c, 0.35)}"/>')
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.2:.1f}" fill="#F6D24A"/>')
                    for j in range(6):
                        a = math.radians(j * 60 + 30)
                        out.append(f'<path d="M {cx + math.cos(a) * r * 0.25:.1f} {cy + math.sin(a) * r * 0.25:.1f} L {cx + math.cos(a) * r * 0.85:.1f} {cy + math.sin(a) * r * 0.85:.1f}" stroke="{lt(c, 0.5)}" stroke-width="{max(1, r * 0.06):.1f}" stroke-linecap="round" opacity="0.7"/>')
                else:
                    for j in range(5):
                        a = math.radians(j * 72)
                        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.6:.1f}" cy="{cy + math.sin(a) * r * 0.6:.1f}" r="{r * 0.5:.1f}" fill="{c}"/>')
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.4:.1f}" fill="#FFF4C8"/>')
    for _ in range(14):
        out.append(f'<circle cx="{rnd.uniform(0, cell):.1f}" cy="{rnd.uniform(0, cell):.1f}" r="{rnd.uniform(1.2, 2.4):.1f}" fill="#FFF6E0" opacity="0.85"/>')
    return "".join(out)


def chita(D, d, cell=120, bg="#C8243A", cols=("#F6C21C", "#2E6AC8", "#FFFFFF", "#F28AB0"), leaf_c="#1F8A4C", seed=7, rot_=0):
    pat = D.pattern(cell, cell, chita_tile(cell, bg, cols, leaf_c, seed), transform=f"rotate({rot_})" if rot_ else "")
    return f'<path d="{d}" fill="{pat}"/>'


def flag_string(D, x0, y0, x1, y1, sag, n, cols, seed, size=30, rope="#6A4A2A", inkc=INK, alt=False):
    """Festa junina bandeirinhas: little rectangular flags with a V cut, hanging along a sagging string."""
    out = []

    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)

    out.append(ink(smooth_open([pt(i / 30) for i in range(31)]), rope, 1.8, seed, 2, 0.95))
    rnd = random.Random(seed)
    for i in range(n):
        t0, t1 = (i + 0.14) / n, (i + 0.86) / n
        a, b = pt(t0), pt(t1)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        h = size * rnd.uniform(1.05, 1.25)
        sw = rnd.uniform(-0.12, 0.12) * size
        bl = (a[0] + nx * h + sw, a[1] + ny * h)
        br = (b[0] + nx * h + sw, b[1] + ny * h)
        mid = ((a[0] + b[0]) / 2 + nx * h * 0.7 + sw, (a[1] + b[1]) / 2 + ny * h * 0.7)
        poly = [a, b, br, mid, bl]
        col = cols[i % len(cols)]
        dd = hg.org_poly(poly, seed + i, 0.4, 8, 1.5)
        out.append(f'<path d="{dd}" fill="{col}"/>')
        out.append(strokes(D.nid(), dd, bbox(poly), [lt(col, 0.35), dk(col, 0.2)], seed + i, n=7, angle=-80, length=(6, 16), width=(1, 2.4), opacity=(0.2, 0.45)))
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f} L {b[0] + nx * 5:.1f} {b[1] + ny * 5:.1f} L {a[0] + nx * 5:.1f} {a[1] + ny * 5:.1f} Z" fill="#FFFFFF" opacity="0.25"/>')
        out.append(ink(dd, inkc, 1.3, seed + i, 1, 0.6))
    return "".join(out)


def leaf_simple(D, x, y, L, W, ang, pal, seed, vein=True, inkw=1.4, inkc=INK):
    """Pointed tropical leaf from base point (x, y) toward `ang` degrees."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(13):
        t = i / 12
        w = W * math.sin(math.pi * t) ** 0.85 * (1 - 0.3 * t)
        bend = 0.08 * L * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.14, angle=ang + 35, n=int(L * W / 60) + 6, slen=(W * 0.4, W * 1.2),
                   sw=(0.8, max(1.2, W * 0.12)), inkw=inkw, inkc=inkc, inkop=0.6, hi=0.3, hik=0.08)]
    if vein:
        sp = [(x + ux * L * t + nx * 0.08 * L * t * t, y + uy * L * t + ny * 0.08 * L * t * t) for t in (0.05, 0.5, 0.92)]
        out.append(pline(sp, lt(pal[0], 0.35), max(1, W * 0.08), seed, 0.7, 1))
    return "".join(out)


def bird_v(x, y, s, col=INK, op=0.85):
    return pline([(x - s, y - s * 0.2), (x - s * 0.45, y - s * 0.5), (x, y)], col, max(1.5, s * 0.16), int(x * 7), op, 1) + \
        pline([(x, y), (x + s * 0.45, y - s * 0.5), (x + s, y - s * 0.25)], col, max(1.5, s * 0.16), int(y * 7), op, 1)


def heart_d(cx, cy, s, rot_=0):
    pts = []
    for i in range(40):
        t = i / 40 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s / 16, cy + y * s / 16))
    return rot(pts, cx, cy, rot_)


def p_heart(D, cx, cy, s, pal, seed, rot_=0, inkw=1.4):
    return painted(D, heart_d(cx, cy, s, rot_), pal, seed, sdir=(0.6, 0.7), sk=0.15, angle=-60, n=int(s * 0.8) + 4,
                   inkw=inkw, hi=0.4, hik=0.1)


def drop_shape(cx, cy, r, L):
    """Teardrop pointing up: round bottom at (cx, cy), tip L above the centre."""
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-30, 211, 20)]
    return [(cx, cy - L)] + pts[::-1][:0] + pts


def steam(cx, y, h, seed, col="#FFFFFF", n=3, gap=22, w=6, op=0.6):
    return steam_wisps(cx, y, h, seed, col, n, gap, w, op)


def wood_planks(D, y0, y1, seed, pal=WOOD, n=4, vertical=False, x0=0, x1=600, gaps=True):
    """Painted wooden planks (tabletop / floor) with grain and knots."""
    rnd = random.Random(seed)
    out = []
    if vertical:
        w = (x1 - x0) / n
        for i in range(n):
            a = x0 + i * w
            d = pd([(a, y0), (a + w, y0), (a + w, y1), (a, y1)])
            c = mix(pal[1], rnd.choice([pal[0], pal[2]]), rnd.uniform(0.05, 0.25))
            out.append(f'<path d="{d}" fill="{c}"/>')
            out.append(strokes(D.nid(), d, (a, y0, a + w, y1), [pal[0], pal[2], lt(pal[0], 0.2)], seed + i, n=int(w * (y1 - y0) / 220),
                               angle=-90, length=(40, 120), width=(0.8, 2.4), opacity=(0.18, 0.45), curve=0.04))
            if gaps:
                out.append(pline([(a + 1, y0), (a + 2, (y0 + y1) / 2), (a + 1, y1)], dk(pal[2], 0.3), 2.2, seed + i, 0.7, 1))
    else:
        h = (y1 - y0) / n
        for i in range(n):
            b = y0 + i * h
            d = pd([(x0, b), (x1, b), (x1, b + h), (x0, b + h)])
            c = mix(pal[1], rnd.choice([pal[0], pal[2]]), rnd.uniform(0.05, 0.25))
            out.append(f'<path d="{d}" fill="{c}"/>')
            out.append(strokes(D.nid(), d, (x0 - 40, b, x1, b + h), [pal[0], pal[2], lt(pal[0], 0.2)], seed + i, n=int((x1 - x0) * h / 200),
                               angle=0, length=(50, 160), width=(0.8, 2.2), opacity=(0.18, 0.45), curve=0.04))
            if rnd.random() < 0.6:
                kx, ky = rnd.uniform(x0 + 40, x1 - 40), b + h * rnd.uniform(0.35, 0.65)
                out.append(f'<ellipse cx="{kx:.1f}" cy="{ky:.1f}" rx="{h * 0.22:.1f}" ry="{h * 0.1:.1f}" fill="none" stroke="{pal[2]}" stroke-width="1.4" opacity="0.6"/>')
            if gaps and i:
                out.append(pline([(x0, b), ((x0 + x1) / 2, b + 1), (x1, b)], dk(pal[2], 0.3), 2.2, seed + i, 0.7, 1))
    return "".join(out)


def cup_saucer(D, cx, base, w, seed, rim=COBALT, coffee="#3A1A0A", body=WHITE, handle=1):
    """Little porcelain coffee cup on its saucer, coffee showing; `base` = bottom of the saucer."""
    out = [cast(D, cx + 6, base, w * 0.75, 7, strength=0.4, seed=seed)]
    sau = ell_pts(cx, base - 6, w * 0.68, w * 0.13, 0, 360, 28)
    out.append(painted(D, sau, body, seed, sdir=(0.5, 1), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(ink(smooth_open(ell_pts(cx, base - 7, w * 0.6, w * 0.1, 20, 160, 12)), rim[1], 2.2, seed, 1, 0.8))
    top, h = base - 8 - w * 0.62, w * 0.62
    l, r = cx - w / 2, cx + w / 2
    hx = r if handle > 0 else l
    out.append(ink(f"M {hx - 3 * handle:.1f} {top + h * 0.2:.1f} q {w * 0.28 * handle:.1f} {-h * 0.05:.1f} {w * 0.2 * handle:.1f} {h * 0.42:.1f} q {-w * 0.06 * handle:.1f} {h * 0.18:.1f} {-w * 0.2 * handle:.1f} {h * 0.18:.1f}",
                   body[2], 5, seed, 1, 1))
    out.append(ink(f"M {hx - 3 * handle:.1f} {top + h * 0.2:.1f} q {w * 0.28 * handle:.1f} {-h * 0.05:.1f} {w * 0.2 * handle:.1f} {h * 0.42:.1f} q {-w * 0.06 * handle:.1f} {h * 0.18:.1f} {-w * 0.2 * handle:.1f} {h * 0.18:.1f}",
                   body[0], 2.4, seed + 1, 1, 1))
    cup = [(l, top), (l + w * 0.04, top + h * 0.55), (l + w * 0.18, top + h * 0.92), (cx, top + h), (r - w * 0.18, top + h * 0.92), (r - w * 0.04, top + h * 0.55), (r, top)]
    out.append(painted(D, cup, body, seed + 2, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=14, inkw=1.8, hi=0.5, hik=0.08))
    out.append(ink(smooth_open([(l + 2, top + h * 0.22), (cx, top + h * 0.3), (r - 2, top + h * 0.22)]), rim[1], 2.6, seed + 3, 1, 0.85))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 24))}" fill="{body[1]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1.5, w / 2 - 4, w * 0.09, 0, 360, 24))}" fill="{coffee}"/>')
    out.append(f'<path d="{blob(cx - w * 0.12, top, w * 0.12, w * 0.025, seed, 0.1, 8)}" fill="#C8905A" opacity="0.7"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 24)), INK, 1.4, seed + 4, 1, 0.7))
    out.append(taper([(l + w * 0.1, top + h * 0.2), (l + w * 0.13, top + h * 0.6)], 3, 1, "#FFFFFF", 0.9))
    return "".join(out)


def finish_b(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


# ---------------------------------------------------------------- little painted houses (morro and interior towns)
def town_house(D, x, base, w, h, seed, wall, kind="slab", haze=0.0, side=0.22):
    """A small painted house in 3/4 view: lit front wall, shaded side wall, windows and a door.
    kind='slab': flat concrete roof of the morro (sometimes a blue water tank, sometimes bare brick);
    kind='gable': whitewashed interior-town house with a terracotta roof."""
    rnd = random.Random(seed)
    hz = lambda c: mix(c, "#C8D8E8", haze) if haze else c
    out = []
    sw_ = w * side
    brick = kind == "slab" and rnd.random() < 0.22
    wc = "#C8683A" if brick else wall
    front = rect_pts(x, base - h, x + w, base, 10, seed, 0.5)
    sidep = [(x + w, base - h), (x + w + sw_, base - h - sw_ * 0.35), (x + w + sw_, base - sw_ * 0.35), (x + w, base)]
    out.append(f'<path d="{pd(sidep)}" fill="{hz(dk(wc, 0.28))}"/>')
    out.append(painted(D, front, (hz(lt(wc, 0.3)), hz(wc), hz(dk(wc, 0.25))), seed, sdir=(1, 0.3), sk=0.08, angle=-80, n=max(6, int(w * h / 120)), inkw=1.1, inkop=0.5, hi=0.25))
    if brick:
        for j in range(1, int(h / 7)):
            out.append(f'<path d="M {x + 1:.1f} {base - j * 7:.1f} L {x + w - 1:.1f} {base - j * 7:.1f}" stroke="{hz("#8A3A1E")}" stroke-width="0.9" opacity="0.6"/>')
    if kind == "slab":
        out.append(f'<path d="{pd([(x - 2, base - h - 3), (x + w + 2, base - h - 3), (x + w + sw_ + 2, base - h - sw_ * 0.35 - 3), (x + w + sw_, base - h - sw_ * 0.35), (x + w, base - h), (x - 2, base - h + 2)])}" fill="{hz("#B8B0A6")}"/>')
        if rnd.random() < 0.4:
            tx = x + rnd.uniform(0.2, 0.6) * w
            out.append(f'<path d="{hg.org_rect(tx, base - h - 13, 13, 11, seed + 3, 0.3, 6, 2)}" fill="{hz("#2E7AC8")}"/>')
            out.append(f'<path d="{smooth_closed(ell_pts(tx + 6.5, base - h - 13, 6.5, 2, 0, 360, 10))}" fill="{hz("#5AA0E0")}"/>')
    else:
        rf = [(x - 4, base - h + 1), (x + w * 0.5, base - h - w * 0.32), (x + w + 4, base - h + 1)]
        out.append(painted(D, rf, (hz("#E88A5A"), hz("#C0582E"), hz("#7A2E14")), seed + 4, sk=0.15, angle=0, n=6, inkw=1, inkop=0.5, hi=0.3))
        out.append(f'<path d="{pd([(x + w + 4, base - h + 1), (x + w * 0.5, base - h - w * 0.32), (x + w * 0.5 + sw_, base - h - w * 0.32 - sw_ * 0.35), (x + w + sw_ + 4, base - h - sw_ * 0.35 + 1)])}" fill="{hz("#9A4220")}"/>')
    win = hz("#2A3A4A") if rnd.random() < 0.8 else hz("#FFE8A0")
    frame = hz(rnd.choice(["#FFFFFF", "#2E62B0", "#1F8A4C", "#F6C21C"])) if kind == "slab" else hz("#2E62B0")
    nwin = 1 if w < 30 else 2
    for k in range(nwin):
        wx = x + w * (0.22 + 0.42 * k) if nwin == 2 else x + w * 0.5 - 4
        wy = base - h * 0.78
        ww_, wh_ = min(9, w * 0.22), min(10, h * 0.3)
        out.append(f'<path d="{hg.org_rect(wx - 1.5, wy - 1.5, ww_ + 3, wh_ + 3, seed + 10 + k, 0.3, 6, 1)}" fill="{frame}"/>')
        out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww_:.1f}" height="{wh_:.1f}" fill="{win}"/>')
    if h > 22 and rnd.random() < 0.6:
        dx = x + w * rnd.uniform(0.3, 0.6)
        out.append(f'<path d="{hg.org_rect(dx, base - h * 0.42, min(9, w * 0.22), h * 0.42, seed + 20, 0.3, 6, 1)}" fill="{hz(rnd.choice(["#2E62B0", "#8A4A2A", "#1F8A4C", "#C8382E"]))}"/>')
    return "".join(out)


# ================================================================ 1. pão de queijo — a basket of cheese breads, steaming
def cheese_bread(D, cx, cy, r, seed, light=(-0.6, -0.8)):
    """A pão de queijo: golden dome, crackled top, toasty freckles, pale underside."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.86, seed, 0.05, 18)
    pts = [(x, y if y < cy + r * 0.45 else cy + r * 0.45 + (y - cy - r * 0.45) * 0.6) for x, y in pts]
    pal = ("#FCE7A6", "#EDB955", "#B07428")
    out = [painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-40, n=int(r * 1.4), slen=(r * 0.2, r * 0.6),
                   sw=(r * 0.03, r * 0.08), cols=["#FFF0C0", "#C8862E", "#F6CE76", "#A8661E"], inkw=max(1.2, r * 0.045), inkop=0.6,
                   hi=0.45, hik=0.1, curve=0.5)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    # browned crown and toasty freckles
    inner.append(f'<path d="{blob(cx + r * 0.1, cy - r * 0.15, r * 0.55, r * 0.4, seed + 3, 0.2, 12)}" fill="#C8802A" opacity="0.28"/>')
    for _ in range(int(r * 0.5)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.85
        inner.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr * 0.8:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="{rnd.choice(["#9A5A1A", "#B8742A", "#FFF2C8"])}" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    # cracks: pale fissures with dark lips
    for k in range(rnd.randint(2, 3)):
        a = rnd.uniform(-2.6, -0.5)
        x0, y0 = cx + math.cos(a) * r * 0.15, cy - r * 0.2 + rnd.uniform(-4, 4)
        L = r * rnd.uniform(0.45, 0.75)
        crack = [(x0, y0), (x0 + math.cos(a) * L * 0.5 + rnd.uniform(-3, 3), y0 + math.sin(a) * L * 0.35), (x0 + math.cos(a) * L, y0 + math.sin(a) * L * 0.55)]
        inner.append(taper([(x + 1, y + 1.5) for x, y in crack], max(2.5, r * 0.09), 0.6, "#8A4E14", 0.55))
        inner.append(taper(crack, max(2, r * 0.07), 0.5, "#FFF3CC", 0.95))
    inner.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.38, r * 0.2, r * 0.1, seed + 5, 0.2, 10, -30)}" fill="#FFFBE8" opacity="0.65"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def wicker_basket(D, cx, rim_y, rx, ry, bottom, bot_rx, seed, front=True):
    """Front half of a woven basket: body (rows of over-under weave), stakes, shading and a braided rim."""
    out = []
    fr = ell_pts(cx, rim_y, rx, ry, 0, 180, 24)
    body = fr + [(cx - bot_rx, bottom - 6), (cx - bot_rx * 0.7, bottom + 4), (cx + bot_rx * 0.7, bottom + 4), (cx + bot_rx, bottom - 6)][::-1]
    body = [(cx + rx, rim_y)] + [(cx + bot_rx, bottom - 6), (cx + bot_rx * 0.6, bottom + 5), (cx - bot_rx * 0.6, bottom + 5), (cx - bot_rx, bottom - 6), (cx - rx, rim_y)] + fr[::-1][1:-1]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="#B07A3E"/>')
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    w = []
    rows = int((bottom - rim_y) / 13) + 2
    for i in range(rows):
        y = rim_y + ry * 0.5 + i * 13
        k = 0
        x = cx - rx - 20 + (i % 2) * 16
        while x < cx + rx + 20:
            t = (x - cx) / rx
            yy = y + ry * 0.9 * math.sqrt(max(0, 1 - min(1, t * t))) - ry * 0.5
            c = rnd.choice(["#E2B06A", "#D49E58", "#ECC07A"])
            w.append(f'<path d="{blob(x + 8, yy, 13, 5.2, seed + i * 31 + k, 0.12, 10, -4 + t * 10)}" fill="{c}"/>')
            w.append(f'<path d="M {x:.1f} {yy + 3:.1f} Q {x + 8:.1f} {yy + 5.5:.1f} {x + 16:.1f} {yy + 3:.1f}" stroke="#7A4A1E" stroke-width="1.2" fill="none" opacity="0.55"/>')
            x += 32
            k += 1
    for j in range(-9, 10):
        x = cx + j * rx / 9.5
        w.append(pline([(x, rim_y), (cx + (x - cx) * bot_rx / rx, bottom + 6)], "#6E431C", 2.2, seed + j, 0.35, 1))
    w.append(shade_over(D, d, "#3A1A06", 0.55, 0, 0, 1, 0.4, 0.25))
    w.append(light_over(D, d, "#FFE8B8", 0.35, 0, 0, 0.6, 0.6))
    out.append(f'<g {cid}>{"".join(w)}</g>')
    out.append(ink(d, INK, 2.2, seed, 2, 0.75))
    # braided rim (front half)
    rim = ell_pts(cx, rim_y, rx, ry, -6, 186, 36)
    out.append(taper(rim, 13, 13, "#9A6830"))
    for i in range(len(rim) - 1):
        (x0, y0), (x1, y1) = rim[i], rim[i + 1]
        out.append(f'<path d="{blob((x0 + x1) / 2, (y0 + y1) / 2, 6.5, 4.2, seed + i, 0.1, 8, 35)}" fill="{"#E8BA74" if i % 2 else "#D29E56"}"/>')
    out.append(ink(smooth_open(rim), "#5A3412", 1.4, seed + 3, 1, 0.5))
    return "".join(out)


@design("pao-de-queijo")
def pao_de_queijo():
    D = Doc2("pq")
    out = [paper(D.nid(), "#F4E6CA", FLECK, 21)]
    out.append(blooms(4, ["#A8D2C2", "#8CC4B4", "#C8E2D2"], 6, (60, 60, 540, 420), (120, 200), (0.12, 0.2)))
    # wooden table
    out.append(wood_planks(D, 470, 600, 22, WOOD, 3))
    out.append(f'<rect y="466" width="600" height="8" fill="#5E3618" opacity="0.5"/>')
    out.append(soft_glow(D, 300, 360, 250, "#FFE6A0", 0.55))
    cx, rim_y, rx, ry = 300, 392, 168, 44
    out.append(cast(D, 318, 528, 200, 22, strength=0.45, seed=3))
    # inside of the basket, cloth lining rising behind the breads
    out.append(f'<path d="{blob(cx, rim_y, rx - 4, ry - 4, 5, 0.01, 24)}" fill="#5E3A16"/>')
    back = [(cx - rx + 10, rim_y + 6), (cx - rx - 8, rim_y - 70), (cx - rx + 4, rim_y - 102), (cx - rx + 52, rim_y - 64), (cx - 60, rim_y - 52),
            (cx + 40, rim_y - 56), (cx + rx - 60, rim_y - 70), (cx + rx - 6, rim_y - 108), (cx + rx + 10, rim_y - 66), (cx + rx - 10, rim_y + 6)]
    out.append(cloth(D, back, "#D8382E", 31, cell=11, rot_=8, light=(0.0, 0.0, 1.0, 0.6),
                     folds=[((cx - rx + 10, rim_y - 90), (cx - rx + 30, rim_y - 50), (cx - rx + 40, rim_y)),
                            ((cx + rx - 14, rim_y - 96), (cx + rx - 40, rim_y - 50), (cx + rx - 50, rim_y))]))
    breads = [(196, 352, 38), (262, 336, 40), (336, 334, 40), (404, 350, 37), (232, 300, 37), (300, 290, 39), (370, 300, 36),
              (300, 252, 34), (180, 386, 40), (256, 382, 42), (340, 380, 42), (420, 386, 40)]
    for i, (x, y, r) in enumerate(sorted(breads, key=lambda b: b[1])):
        out.append(cheese_bread(D, x, y, r, 40 + i))
    out.append(wicker_basket(D, cx, rim_y, rx, ry, 520, 128, 7))
    # a corner of the cloth spilling over the front rim
    flap = [(cx - 120, rim_y + 30), (cx - 40, rim_y + 44), (cx - 52, rim_y + 82), (cx - 84, rim_y + 122), (cx - 104, rim_y + 92), (cx - 124, rim_y + 60)]
    out.append(cloth(D, flap, "#D8382E", 32, cell=11, rot_=-12, light=(0, 0, 0.6, 1), folds=[((cx - 70, rim_y + 44), (cx - 82, rim_y + 80), (cx - 86, rim_y + 112))]))
    # one bread broken open on the table: stretchy cheese
    bx, by = 492, 520
    out.append(cast(D, bx + 6, by + 22, 70, 10, strength=0.4, seed=8))
    for k, (dx, ang) in enumerate(((-24, -14), (28, 16))):
        pts = rot([(bx + dx - 26, by + 12), (bx + dx - 30, by - 8), (bx + dx - 14, by - 26), (bx + dx + 8, by - 26), (bx + dx + 22, by - 10), (bx + dx + 20, by + 12)], bx + dx, by, ang)
        out.append(painted(D, pts, ("#FCE7A6", "#EDB955", "#B07428"), 60 + k, sdir=(0.6, 0.8), sk=0.2, angle=-40, n=18, inkw=1.6, hi=0.4))
        face = blob(bx + dx + (8 if dx < 0 else -8), by + 2, 16, 11, 62 + k, 0.1, 12, ang)
        out.append(f'<path d="{face}" fill="#FFF6D8"/>')
        out.append(specks(70 + k, (bx + dx - 10, by - 6, bx + dx + 10, by + 10), ["#E8C88A", "#D8B070"], 10, (0.8, 1.8), (0.5, 0.9)))
        out.append(ink(face, "#C08A3A", 1.2, 64 + k, 1, 0.6))
    out.append(taper([(bx - 10, by), (bx, by + 4), (bx + 12, by - 1)], 6, 4, "#FFF6D8", 0.95))
    out.append(taper([(bx - 10, by - 3), (bx, by + 1), (bx + 12, by - 4)], 1.5, 1, "#FFFFFF", 0.9))
    # steam
    out.append(steam(300, 228, 70, 11, "#FFFFFF", 3, 26, 7, 0.55))
    out.append(steam(220, 272, 50, 12, "#FFFFFF", 2, 22, 5, 0.45))
    out.append(steam(380, 272, 50, 13, "#FFFFFF", 2, 22, 5, 0.45))
    # lettering
    out.append(cup_saucer(D, 112, 528, 64, 65))
    out.append(steam(112, 474, 40, 66, "#FFFFFF", 2, 18, 5, 0.6))
    out.append(ruled(300, 88, "PÃO DE", "#1F6A40", font=JOS, size=34, ls=12, line_w=60, gap=18))
    out.append(letters(D, 300, 206, "queijo", SERIF_IT, 130, "#B0461E", ["#D8683A", "#8A2E12", "#E88A52"], 77, max_w=400,
                       shadow="#5A2210", soff=(0.02, 0.035), angle=-40, hi="#FFE2B8"))
    return finish_b(D, out, 23)


# ================================================================ 2. brigadeiro — a party plate, one already gone
def brig(D, cx, cy, r, seed, cup=("#E8B860", "#B8823A", "#7A4E1E"), eaten=False):
    """Top-down brigadeiro in a pleated paper cup: dark fudge ball covered in chocolate sprinkles."""
    rnd = random.Random(seed)
    out = [cast(D, cx + r * 0.18, cy + r * 0.22, r * 1.45, r * 1.38, strength=0.35, seed=seed)]
    R = r * 1.42
    pts = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        rr = R * (1 + 0.05 * math.cos(a * 18))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = smooth_closed(jitter(pts, seed, 0.4))
    out.append(f'<path d="{d}" fill="{cup[1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    pl = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        pl.append(f'<path d="M {cx + math.cos(a) * r * 0.7:.1f} {cy + math.sin(a) * r * 0.7:.1f} L {cx + math.cos(a) * R * 1.1:.1f} {cy + math.sin(a) * R * 1.1:.1f}" '
                  f'stroke="{cup[0] if i % 2 else cup[2]}" stroke-width="{max(1.2, r * 0.06):.1f}" opacity="0.55"/>')
    pl.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 1.02:.1f}" fill="{cup[2]}" opacity="0.6"/>')
    pl.append(shade_over(D, d, "#2A1206", 0.35, 0, 0, 1, 1, 0.4))
    pl.append(light_over(D, d, "#FFF4D8", 0.4, 0, 0, 0.7, 0.7))
    out.append(f'<g {cid}>{"".join(pl)}</g>')
    out.append(ink(d, INK, 1.4, seed, 1, 0.6))
    if eaten:
        for _ in range(9):
            a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.8)
            out.append(f'<path d="M {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#2A1206" stroke-width="2.2" stroke-linecap="round"/>')
        out.append(f'<path d="{blob(cx + 4, cy + 2, r * 0.45, r * 0.3, seed + 4, 0.25, 10)}" fill="#3A1A0A" opacity="0.35"/>')
        return "".join(out)
    bp = blob_pts(cx, cy, r, r * 0.97, seed + 1, 0.04, 16)
    bd = smooth_closed(bp)
    out.append(f'<path d="{bd}" fill="#3E1E10"/>')
    cid2 = D.clip(f'<path d="{bd}"/>')
    s = []
    for _ in range(int(r * 3.4)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 1.02
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        lit = -(math.cos(a) * 0.6 + math.sin(a) * 0.7) * rr / r
        c = rnd.choice(["#7A4A2E", "#5A2E18", "#8A5A3A"]) if lit > 0.25 else rnd.choice(["#24100A", "#3A1A0C", "#4A2414"])
        L = rnd.uniform(r * 0.1, r * 0.17)
        t = rnd.uniform(0, 3.14)
        s.append(f'<path d="M {x - math.cos(t) * L / 2:.1f} {y - math.sin(t) * L / 2:.1f} l {math.cos(t) * L:.1f} {math.sin(t) * L:.1f}" stroke="{c}" stroke-width="{max(1.6, r * 0.075):.1f}" stroke-linecap="round"/>')
    s.append(shade_over(D, bd, "#0A0402", 0.55, 0, 0, 1, 1, 0.35))
    s.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.38, r * 0.32, r * 0.2, seed + 2, 0.2, 10, -35)}" fill="#FFE8D0" opacity="0.28"/>')
    out.append(f'<g {cid2}>{"".join(s)}</g>')
    for _ in range(5):
        a = rnd.uniform(-2.6, -1.6)
        x, y = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(1.5, 3):.1f} {rnd.uniform(-1, 1):.1f}" stroke="#FFF0E0" stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>')
    out.append(ink(bd, "#1A0A04", 1.3, seed, 1, 0.55))
    return "".join(out)


@design("brigadeiro")
def brigadeiro():
    D = Doc2("bg")
    out = [paper(D.nid(), "#F8DCD6", "#8A4A4A", 31)]
    rnd = random.Random(3)
    dots = "".join(f'<circle cx="{x * 60 + (30 if y % 2 else 0) + rnd.uniform(-2, 2):.1f}" cy="{y * 52 + rnd.uniform(-2, 2):.1f}" r="{rnd.uniform(5, 6.5):.1f}" fill="#FFFFFF" opacity="0.55"/>'
                   for x in range(-1, 11) for y in range(0, 13))
    out.append(dots)
    out.append(blooms(5, ["#F2B0B0", "#E89A9A", "#FFE0D8"], 7, (0, 0, 600, 600), (100, 200), (0.1, 0.18)))
    # porcelain cake plate with a scalloped blue rim
    cx, cy, R = 300, 382, 162
    out.append(cast(D, cx + 16, cy + 22, R + 12, R * 0.96, strength=0.35, seed=4))
    scal = [(cx + (R + 6 * math.cos(i * 2 * math.pi / 64 * 16)) * math.cos(i * 2 * math.pi / 64), cy + (R + 6 * math.cos(i * 2 * math.pi / 64 * 16)) * math.sin(i * 2 * math.pi / 64)) for i in range(64)]
    sd = smooth_closed(scal)
    out.append(painted(D, scal, ("#FFFFFF", "#F6F2EC", "#C8C0B8"), 5, sdir=(0.6, 0.7), sk=0.05, angle=-30, n=60, inkw=2, hi=0.4))
    out.append(f'<path d="{blob(cx, cy, R - 24, R - 24, 6, 0.01, 30)}" fill="#EEE8E0"/>')
    out.append(ink(blob(cx, cy, R - 24, R - 24, 6, 0.01, 30), "#B8B0A8", 1.4, 6, 1, 0.6))
    for i in range(32):
        a = 2 * math.pi * i / 32
        x, y = cx + (R - 11) * math.cos(a), cy + (R - 11) * math.sin(a)
        out.append(f'<path d="{blob(x, y, 5, 3.2, 10 + i, 0.15, 8, math.degrees(a) + 90)}" fill="#2E5AB8" opacity="0.85"/>')
        if i % 2 == 0:
            out.append(f'<circle cx="{cx + (R - 2) * math.cos(a + 0.098):.1f}" cy="{cy + (R - 2) * math.sin(a + 0.098):.1f}" r="2.2" fill="#2E5AB8" opacity="0.7"/>')
    out.append(shade_over(D, sd, "#3A2A2A", 0.18, 0, 0, 1, 1, 0.5))
    # seven brigadeiros, one eaten
    cups = [("#E8B860", "#B8823A", "#7A4E1E"), ("#F6A8B8", "#D86A88", "#8A2E4A"), ("#E8B860", "#B8823A", "#7A4E1E"),
            ("#9AD0E8", "#4A8AC0", "#1E4E7A"), ("#E8B860", "#B8823A", "#7A4E1E"), ("#F6A8B8", "#D86A88", "#8A2E4A"), ("#C8E0A0", "#7EAE4E", "#3E6A20")]
    spots = [(cx, cy)] + [(cx + 96 * math.cos(math.radians(a)), cy + 96 * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    for i, (x, y) in enumerate(spots):
        out.append(brig(D, x, y, 31, 80 + i * 3, cups[i], eaten=(i == 2)))
    # a few stray sprinkles on the plate and table
    for _ in range(26):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(40, 190)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        if any(math.hypot(x - sx, y - sy) < 48 for sx, sy in spots):
            continue
        t = rnd.uniform(0, 3.14)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(t) * 5:.1f} {math.sin(t) * 5:.1f}" stroke="#3A1A0C" stroke-width="2.4" stroke-linecap="round"/>')
    for x, y, s in ((92, 520, 9), (520, 250, 8), (80, 260, 7), (528, 520, 10)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.9))
    out.append(letters(D, 300, 152, "brigadeiro", SERIF_IT, 124, "#5A2414", ["#7A3A22", "#3A140A", "#8A4A30"], 41, max_w=460,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#E8A890"))
    out.append(ruled(300, 196, "SÓ MAIS UM, PROMETO", "#B8325A", font=MONO, size=19, ls=4, line_w=34, gap=14))
    return finish_b(D, out, 33, "#5A2A2A")


# ================================================================ 3. café passado — cloth filter dripping into an enamel pot
def enamel_pot(D, cx, top, w, h, seed, body=WHITE, rim=COBALT, handle_side=1, flowers=True, chips=True):
    """Enamelled pot / caneca: white body, cobalt rolled rim, chips showing dark metal, little painted flowers."""
    l, r = cx - w / 2, cx + w / 2
    bot = top + h
    pts = [(l + 3, top + 6), (l, top + h * 0.5), (l + 4, bot - 10), (l + 14, bot), (r - 14, bot), (r - 4, bot - 10), (r, top + h * 0.5), (r - 3, top + 6)]
    out = [cast(D, cx + 10, bot + 2, w * 0.7, 10, strength=0.45, seed=seed)]
    # handle
    hx = r if handle_side > 0 else l
    hp = [(hx - 2 * handle_side, top + h * 0.2), (hx + 30 * handle_side, top + h * 0.18), (hx + 38 * handle_side, top + h * 0.5),
          (hx + 22 * handle_side, top + h * 0.78), (hx - 2 * handle_side, top + h * 0.8)]
    out.append(ink(smooth_open(hp), rim[2], 12, seed, 1, 1))
    out.append(ink(smooth_open(hp), rim[1], 7, seed + 1, 1, 1))
    out.append(painted(D, pts, body, seed, sdir=(0.9, 0.3), sk=0.12, angle=-90, n=40, slen=(10, 30), sw=(1, 3), inkw=2, hi=0.5, hik=0.06))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = [shade_over(D, d, "#2A3A5A", 0.35, 0, 0, 1, 0, 0.45)]
    if flowers:
        rnd = random.Random(seed)
        for k, (fx, fy) in enumerate(((cx - w * 0.15, top + h * 0.5), (cx + w * 0.18, top + h * 0.62), (cx + w * 0.02, top + h * 0.8))):
            for j in range(5):
                a = math.radians(j * 72 + k * 20)
                inner.append(f'<path d="{blob(fx + math.cos(a) * 6, fy + math.sin(a) * 6, 5.5, 3.6, seed + k * 9 + j, 0.1, 8, math.degrees(a))}" fill="{rim[1]}" opacity="0.85"/>')
            inner.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3" fill="#F6C21C"/>')
            inner.append(leaf_simple(D, fx + 8, fy + 4, 16, 4, 20 + k * 30, ("#8ACB8A", "#3E8A4E", "#1E5A2E"), seed + 30 + k, vein=False, inkw=0))
    if chips:
        for (x, y, s) in ((l + 10, bot - 14, 5), (r - 18, top + 30, 4), (cx + 6, bot - 6, 3.5)):
            inner.append(f'<path d="{blob(x, y, s, s * 0.7, seed + int(x), 0.25, 8)}" fill="#1E1E28"/>')
            inner.append(f'<path d="{blob(x, y, s + 2, s * 0.7 + 2, seed + int(x), 0.25, 8)}" fill="none" stroke="#9AA4B8" stroke-width="1"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(l + 12, top + 16), (l + 10, top + h * 0.45), (l + 14, bot - 20)], 5, 1, "#FFFFFF", 0.85))
    # rolled rim
    rim_pts = ell_pts(cx, top + 6, w / 2 - 2, 7, 0, 360, 24)
    out.append(f'<path d="{smooth_closed(rim_pts)}" fill="{rim[1]}"/>')
    out.append(f'<path d="{blob(cx, top + 6, w / 2 - 7, 4.5, seed, 0.02, 20)}" fill="#3A2014"/>')
    out.append(taper(ell_pts(cx, top + 6, w / 2 - 2, 7, 190, 350, 12), 2, 2, rim[0], 0.8))
    out.append(ink(smooth_closed(rim_pts), INK, 1.6, seed, 1, 0.7))
    out.append(f'<path d="M {l + 2:.1f} {bot - 6:.1f} Q {cx:.1f} {bot + 6:.1f} {r - 2:.1f} {bot - 6:.1f}" stroke="{rim[1]}" stroke-width="5" fill="none"/>')
    return "".join(out)


@design("cafe-passado")
def cafe_passado():
    D = Doc2("cp")
    # deep green kitchen wall, morning light from the left
    out = [sky(D, [(0, "#2E5A44"), (1, "#1E3E30")], 3, 600, ["#3E7A5A", "#16302A", "#4A8A64"], 120, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 120, 160, 360, "#FFE2A0", 0.35))
    out.append(blooms(8, ["#4A8A64", "#16302A", "#5A9A70"], 8, (0, 0, 600, 470), (90, 170), (0.08, 0.14)))
    # wooden table
    out.append(wood_planks(D, 470, 600, 41, WOOD, 3))
    out.append(f'<rect y="464" width="600" height="10" fill="#4A2A12" opacity="0.6"/>')
    # wooden stand: base, post, arm and the ring
    st = ("#D8A06A", "#9A6232", "#5A3214")
    out.append(cast(D, 390, 474, 110, 10, strength=0.5, seed=5))
    out.append(painted(D, rect_pts(310, 446, 470, 470, 20, 1, 0.6), st, 42, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=2, hi=0.4))
    out.append(painted(D, rect_pts(424, 208, 446, 452, 20, 2, 0.6), st, 43, sdir=(1, 0), sk=0.25, angle=-90, n=24, inkw=2, hi=0.4))
    out.append('<g transform="translate(0 12)">')
    out.append(painted(D, rect_pts(350, 200, 446, 218, 20, 3, 0.6), st, 44, sdir=(0, 1), sk=0.2, angle=0, n=18, inkw=2, hi=0.4))
    out.append(f'<circle cx="435" cy="209" r="3.2" fill="#3A2010"/>')
    # cloth filter bag hanging from a wire ring
    bag = [(244, 230), (240, 262), (250, 300), (268, 334), (290, 352), (306, 354), (328, 340), (346, 304), (356, 262), (352, 230)]
    bd = smooth_closed(bag)
    out.append(f'<path d="{bd}" fill="#F2E8D4"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    g = D.lin([(0, "#F2E8D4", 0), (0.35, "#C89A62", 0.35), (0.7, "#7A4A22", 0.85), (1, "#4A2410", 1)])
    inner = [f'<rect x="230" y="230" width="140" height="130" fill="{g}"/>',
             strokes(D.nid(), bd, (236, 226, 362, 360), ["#FFFFFF", "#B8925E", "#8A5A2E"], 45, n=60, angle=-95, length=(14, 40), width=(1, 3), opacity=(0.15, 0.4)),
             shade_over(D, bd, "#2A1206", 0.4, 0, 0, 1, 0, 0.45)]
    for a, b, c in (((262, 236), (266, 290), (288, 346)), ((330, 236), (328, 292), (310, 348))):
        inner.append(taper([a, b, c], 3.5, 1, "#8A6A44", 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(bd, INK, 2, 46, 2, 0.75))
    # cloth folded over the ring
    out.append(painted(D, [(238, 222), (298, 216), (358, 222), (360, 238), (330, 244), (298, 240), (266, 244), (236, 238)], ("#FFFDF4", "#EDE2CC", "#B8A888"), 49,
                       sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    # the wire ring (front half over the bag)
    out.append(ink(smooth_closed(ell_pts(298, 228, 58, 11, 0, 360, 28)), "#4A4A52", 3.2, 47, 1, 0.95))
    out.append(ink(smooth_open(ell_pts(298, 228, 58, 11, 10, 170, 14)), "#B8BCC8", 1.4, 48, 1, 0.8))
    # coffee drips
    for k, (x, y, s) in enumerate(((298, 372, 4.2), (299, 392, 3.4), (298, 410, 2.6))):
        dpts = [(x, y - s * 2.2)] + [(x + s * math.cos(math.radians(a)), y + s * math.sin(math.radians(a))) for a in range(-20, 201, 20)]
        out.append(f'<path d="{smooth_closed(dpts)}" fill="#4A2410"/><circle cx="{x - s * 0.35:.1f}" cy="{y - s * 0.1:.1f}" r="{s * 0.3:.1f}" fill="#FFE2C0" opacity="0.8"/>')
    out.append(taper([(298, 352), (298, 362)], 3, 1.2, "#4A2410"))
    out.append("</g>")
    # enamel pot underneath
    out.append(enamel_pot(D, 300, 404, 118, 74, 49, handle_side=-1))
    out.append(steam(300, 392, 34, 50, "#FFFFFF", 2, 34, 5, 0.5))
    # a red enamel mug waiting, and a sugar bowl
    out.append(enamel_pot(D, 138, 404, 76, 66, 52, body=("#F68A7A", "#D8382E", "#8A1414"), rim=WHITE, handle_side=-1, flowers=False, chips=False))
    out.append(steam(138, 392, 46, 53, "#FFFFFF", 2, 20, 5, 0.55))
    out.append(painted(D, [(484, 430), (480, 456), (490, 470), (530, 470), (540, 456), (536, 430)], ("#FFF6E6", "#F0E2C8", "#B8A07A"), 54,
                       sdir=(0.9, 0.3), sk=0.15, angle=-90, n=10, inkw=1.8, hi=0.4))
    out.append(f'<path d="{blob(510, 430, 27, 6, 55, 0.04, 14)}" fill="#FFFFFF"/>' + ink(blob(510, 430, 27, 6, 55, 0.04, 14), INK, 1.4, 55, 1, 0.6))
    for k, (x, y) in enumerate(((500, 424), (514, 422), (520, 428))):
        out.append(f'<path d="{blob(x, y, 5, 4, 56 + k, 0.1, 6)}" fill="#FFFFFF" stroke="#C8B89A" stroke-width="1"/>')
    out.append(pline([(484, 448), (510, 450), (538, 448)], "#2E5AB8", 3, 57, 0.9, 1))
    # lettering
    out.append(letters(D, 300, 154, "café", SERIF_IT, 116, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 61, max_w=330,
                       shadow="#0E2418", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 300, 200, "PASSADO", BEBAS, 48, "#F6C21C", ["#FFE07A", "#D89A10"], 62, ls=14, max_w=360, shadow="#0E2418", wob=0.5))
    out.append(label(300, 526, "NO COADOR DE PANO", MONO, 19, "#FFF2D8", ls=4))
    return finish_b(D, out, 63)


# ---------------------------------------------------------------- clay-tile roof (used by the porch and the taipa house)
def tile_roof(D, pts, seed, pal=TERRA, rows=6, cols=14):
    """Colonial clay-tile roof: a painted plane with rows of half-round tiles (light crowns, dark troughs)."""
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    x0, y0, x1, y1 = bbox(pts)
    rnd = random.Random(seed)
    inner = []
    hh = (y1 - y0) / rows
    ww = (x1 - x0) / cols
    for j in range(rows):
        for i in range(cols + 2):
            x = x0 + (i - 0.5) * ww + (j % 2) * ww * 0.08
            y = y0 + j * hh
            c = mix(pal[1], rnd.choice([pal[0], pal[2], "#E8B070"]), rnd.uniform(0.1, 0.4))
            tile = blob(x + ww / 2, y + hh * 0.55, ww * 0.42, hh * 0.62, seed + i * 13 + j, 0.06, 12)
            inner.append(f'<path d="{tile}" fill="{c}"/>')
            inner.append(taper([(x + ww * 0.3, y + hh * 0.15), (x + ww * 0.32, y + hh * 0.9)], 2.5, 1, lt(pal[0], 0.3), 0.6))
            inner.append(taper([(x + ww * 0.9, y + hh * 0.2), (x + ww * 0.92, y + hh * 1.0)], 3, 1, pal[2], 0.55))
        inner.append(f'<path d="M {x0:.1f} {y + hh * 1.02:.1f} L {x1:.1f} {y + hh * 1.02:.1f}" stroke="{pal[2]}" stroke-width="2.2" opacity="0.55"/>')
    inner.append(shade_over(D, d, "#2A0A04", 0.3, 0, 0, 0, 1, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, INK, 2, seed, 2, 0.75))
    return "".join(out)


# ================================================================ 5. tucano — a naturalist's plate
def toucan(D, ox, oy, s, seed, flip=False):
    """Toco toucan perched, facing left; (ox, oy) = feet on the branch; s = scale (1 ~ 300 px tall)."""
    k = s

    def P(x, y):
        return (ox + (-x if flip else x) * k, oy + y * k)

    def L(pts):
        return [P(x, y) for x, y in pts]

    out = []
    # tail hanging behind the branch
    tail = L([(10, -20), (40, -26), (62, 54), (54, 92), (34, 96), (14, 36)])
    out.append(painted(D, tail, ("#4A4A58", "#1E1C24", "#0A0A0E"), seed, sdir=(1, 0.3), sk=0.2, angle=80, n=20, inkw=1.8, inkc="#0A0A0E", hi=0.25))
    for t in (0.3, 0.55, 0.8):
        out.append(pline(L([(16 + 40 * t, -10 + 100 * t), (34 + 30 * t, -14 + 112 * t)]), "#5A5A6A", 1.4, seed, 0.5, 1))
    # body
    body = L([(-46, -150), (-14, -168), (26, -150), (46, -100), (44, -40), (26, -8), (-4, 0), (-30, -20), (-46, -70), (-50, -120)])
    out.append(painted(D, body, ("#5A5E78", "#22202C", "#08080C"), seed + 1, sdir=(1, 0.4), sk=0.18, angle=60, n=80,
                       cols=["#4A4E68", "#2A2A3A", "#6A7090", "#101016"], sop=(0.25, 0.55), inkw=2, inkc="#08080C", hi=0.45, hik=0.08))
    # feather scallops on the body
    rnd = random.Random(seed)
    for i in range(16):
        x, y = rnd.uniform(-34, 34), rnd.uniform(-120, -30)
        out.append(pline(L([(x - 6, y), (x, y + 4), (x + 6, y)]), "#5A6078", 1.3, seed + i, 0.5, 1))
    # wing
    wing = L([(-8, -138), (24, -130), (42, -90), (40, -40), (22, -22), (8, -60)])
    out.append(painted(D, wing, ("#3A3A48", "#16141C", "#040406"), seed + 2, sdir=(1, 0.2), sk=0.15, angle=75, n=20, inkw=1.6, inkc="#000000", hi=0.3))
    for t in (0.25, 0.5, 0.75):
        out.append(pline(L([(8 + 30 * t, -130 + 10 * t), (12 + 26 * t, -40 - 20 * t)]), "#5A6078", 1.2, seed, 0.45, 1))
    # red under-tail coverts
    out.append(painted(D, L([(-6, -12), (16, -16), (26, -4), (12, 6), (-4, 4)]), ("#FF7A6A", "#D8282A", "#8A0A12"), seed + 3, sk=0.2, n=8, inkw=1.4, hi=0.3))
    # white bib with a buttery wash
    bib = L([(-50, -168), (-22, -180), (-2, -160), (-2, -120), (-22, -96), (-44, -104), (-56, -138)])
    out.append(painted(D, bib, ("#FFFFFF", "#FFF8E8", "#E8D8B0"), seed + 4, sdir=(1, 0.5), sk=0.12, angle=-60, n=16, inkw=1.6, hi=0.3))
    out.append(f'<path d="{smooth_closed(L([(-40, -136), (-20, -140), (-12, -120), (-28, -108), (-44, -114)]))}" fill="#FFE07A" opacity="0.45"/>')
    # head (black cap)
    head = L([(-56, -178), (-40, -206), (-10, -212), (12, -196), (18, -170), (0, -152), (-22, -158), (-46, -160)])
    out.append(painted(D, head, ("#4A4A5A", "#1E1C26", "#08080C"), seed + 5, sdir=(1, 0.4), sk=0.15, angle=0, n=20, inkw=1.8, inkc="#08080C", hi=0.35))
    # bill: big orange, darker culmen line, red-orange base band and black tip
    bill = L([(-52, -200), (-90, -214), (-150, -212), (-200, -196), (-224, -180), (-218, -174), (-186, -170), (-130, -164), (-80, -164), (-52, -170)])
    bd = smooth_closed(bill)
    out.append(painted(D, bill, ("#FFC060", "#F28A1E", "#B0500A"), seed + 6, sdir=(0.2, 1), sk=0.12, angle=-8, n=40,
                       cols=["#FFD27A", "#E8701A", "#FFB040", "#C85A0A"], inkw=0, hi=0.45, hik=0.08))
    cid = D.clip(f'<path d="{bd}"/>')
    tip = smooth_closed(L([(-178, -230), (-240, -200), (-230, -150), (-190, -150), (-172, -190)]))
    base = smooth_closed(L([(-50, -230), (-66, -230), (-70, -150), (-50, -150)]))
    inner = [f'<path d="{tip}" fill="#16120E"/>', f'<path d="{base}" fill="#D8382E" opacity="0.7"/>',
             f'<path d="{smooth_closed(L([(-60, -176), (-200, -184), (-226, -150), (-60, -150)]))}" fill="#C8401A" opacity="0.35"/>',
             taper(L([(-70, -205), (-120, -208), (-170, -200)]), 4 * k, 1, "#FFF2C8", 0.75)]
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(pline(L([(-56, -168), (-120, -171), (-200, -176), (-220, -177)]), "#7A2A0A", 1.8, seed, 0.8, 1))
    out.append(ink(bd, "#5A2006", 2, seed + 7, 2, 0.8))
    # eye: blue bare skin, orange ring, dark iris, highlight
    ex, ey = P(-30, -186)
    out.append(f'<path d="{blob(ex, ey, 15 * k, 12 * k, seed + 8, 0.08, 12)}" fill="#3E7AD0"/>')
    out.append(f'<path d="{blob(ex, ey, 8.5 * k, 8.5 * k, seed + 9, 0.04, 10)}" fill="#F2A81D"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5.6 * k:.1f}" fill="#120C08"/><circle cx="{ex - 1.8 * k:.1f}" cy="{ey - 2 * k:.1f}" r="{1.8 * k:.1f}" fill="#FFFFFF"/>')
    # feet gripping the branch
    for dx in (-10, 8):
        fx, fy = P(dx, 0)
        out.append(ink(f"M {fx - 6 * k:.1f} {fy + 4 * k:.1f} q {6 * k:.1f} {-10 * k:.1f} {12 * k:.1f} 0", "#5A6A8A", 4 * k, seed + dx, 1, 1))
    return "".join(out)


def branch(D, pts, w0, w1, seed, pal=("#A8805A", "#6E4A2E", "#3A2414")):
    out = [taper(pts, w0, w1, pal[1])]
    out.append(taper([(x, y - w0 * 0.22) for x, y in pts], w0 * 0.35, w1 * 0.3, pal[0], 0.6))
    out.append(taper([(x, y + w0 * 0.28) for x, y in pts], w0 * 0.3, w1 * 0.3, pal[2], 0.5))
    rnd = random.Random(seed)
    for i in range(1, len(pts) - 1, 2):
        x, y = pts[i]
        out.append(f'<path d="M {x - 6:.1f} {y + rnd.uniform(-2, 2):.1f} q 6 -3 12 0" stroke="{pal[2]}" stroke-width="1.2" fill="none" opacity="0.6"/>')
    return "".join(out)


def berries(D, x, y, n, seed, pal=RED, r=6):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        bx, by = x + rnd.uniform(-r * 1.8, r * 1.8), y + rnd.uniform(-r * 1.2, r * 1.6)
        out.append(pline([(x, y - r * 2), (bx, by)], "#4A5A22", 1.2, seed + i, 0.8, 1))
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="{pal[1]}"/><circle cx="{bx + r * 0.25:.1f}" cy="{by + r * 0.25:.1f}" r="{r * 0.7:.1f}" fill="{pal[2]}" opacity="0.5"/>'
                   f'<circle cx="{bx - r * 0.35:.1f}" cy="{by - r * 0.35:.1f}" r="{r * 0.28:.1f}" fill="#FFFFFF" opacity="0.8"/>'
                   f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.5"/>')
    return "".join(out)


@design("tucano")
def tucano():
    D = Doc2("tc")
    out = [paper(D.nid(), "#F2E8D2", FLECK, 51)]
    out.append(blooms(6, ["#C8D8B0", "#E8D8A8", "#B8D0C0"], 6, (100, 120, 500, 460), (110, 180), (0.12, 0.2)))
    # plate frame
    out.append(f'<rect x="50" y="50" width="500" height="500" fill="none" stroke="#2E5A3A" stroke-width="2.2"/>')
    out.append(f'<rect x="58" y="58" width="484" height="484" fill="none" stroke="#2E5A3A" stroke-width="1.2" opacity="0.7"/>')
    for x, y in ((50, 50), (550, 50), (50, 550), (550, 550)):
        out.append(f'<path d="{blob(x, y, 7, 7, x + y, 0.1, 8)}" fill="#C8603A"/>')
    out.append(ruled(300, 92, "AVES DO BRASIL · Nº 7", "#2E5A3A", font=MONO, size=16, ls=4, line_w=26, gap=10))
    # big leaves behind
    out.append(leaf_simple(D, 520, 360, 130, 34, -120, MATA, 52))
    out.append(leaf_simple(D, 520, 360, 110, 30, -75, VERDE, 53))
    out.append(leaf_simple(D, 92, 380, 110, 30, -60, MATA, 54))
    out.append(leaf_simple(D, 92, 380, 90, 24, -100, VERDE, 154))
    # branch
    bp = catmull([(64, 392), (170, 386), (280, 376), (390, 366), (470, 368), (538, 352)], 5)
    out.append(branch(D, bp, 18, 9, 55))
    out.append(taper(catmull([(430, 368), (468, 336), (500, 318)], 5), 8, 3, "#6E4A2E"))
    out.append(taper(catmull([(150, 388), (124, 420), (110, 446)], 5), 7, 3, "#6E4A2E"))
    out.append(berries(D, 492, 394, 7, 56, RED, 6.5))
    out.append(berries(D, 112, 456, 5, 57, ("#FFB07A", "#F26A1E", "#A03A0A"), 5.5))
    out.append(leaf_simple(D, 236, 380, 76, 20, 140, VERDE, 58))
    out.append(leaf_simple(D, 500, 318, 70, 18, -30, VERDE, 59))
    out.append(leaf_simple(D, 124, 420, 60, 16, 170, MATA, 159))
    for k, (x, y) in enumerate(((270, 370), (178, 380), (520, 340))):
        out.append(hibiscus(D, x, y - 8, 12, ("#FFF2B0", "#F6C21C", "#C08A0A"), 160 + k, k * 40, inkw=1, stamen="#E86A1E"))
    # the toucan
    out.append(toucan(D, 396, 354, 0.92, 60))
    out.append(leaf_simple(D, 340, 372, 60, 16, 110, MATA, 61))
    out.append(leaf_simple(D, 540, 352, 54, 15, 80, VERDE, 62))
    # caption
    out.append(letters(D, 290, 500, "Tucano", SERIF_IT, 62, "#1F4A2E", ["#2E6A40", "#123A20"], 63, max_w=300, angle=-40, wob=0.6))
    out.append(label(290, 530, "RAMPHASTOS TOCO", MONO, 16, "#7A3218", ls=5))
    return finish_b(D, out, 64)


# ================================================================ 6. carnaval — mask, plumes, frevo umbrella, confetti
def feather(D, x, y, L, ang, pal, seed, w=None):
    """Plume feather from its quill base (x, y) toward ang: soft barbs either side of a pale shaft."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    w = w or L * 0.22
    rnd = random.Random(seed)
    out = []
    shaft = [(x + ux * L * t + nx * L * 0.08 * t * t, y + uy * L * t + ny * L * 0.08 * t * t) for t in (0, 0.3, 0.6, 1)]
    for i in range(26):
        t = 0.15 + 0.85 * i / 25
        px, py = x + ux * L * t + nx * L * 0.08 * t * t, y + uy * L * t + ny * L * 0.08 * t * t
        ww = w * math.sin(math.pi * min(1, t * 1.05)) ** 0.6
        for sg in (-1, 1):
            ex, ey = px + (nx * sg * 0.9 + ux * 0.45) * ww, py + (ny * sg * 0.9 + uy * 0.45) * ww
            c = rnd.choice([pal[0], pal[1], pal[1], pal[2]])
            out.append(taper([(px, py), ((px + ex) / 2 + ux * 3, (py + ey) / 2 + uy * 3), (ex, ey)], 3.2, 0.8, c, rnd.uniform(0.75, 1)))
    out.append(taper(catmull(shaft, 4), 3, 1, lt(pal[0], 0.6), 0.9))
    return "".join(out)


def frevo_umbrella(D, cx, cy, r, ang, seed, cols=("#F6C21C", "#1F8A4C", "#D8382E", "#2E6AC8", "#F6C21C", "#1F8A4C", "#D8382E", "#2E6AC8")):
    """Sombrinha de frevo: small domed umbrella in bright segments, scalloped hem, white piping, curved handle."""
    out = [f'<g transform="rotate({ang} {cx} {cy})">']
    hx, hy = cx, cy + r * 1.35
    out.append(ink(f"M {cx} {cy} L {hx} {hy} q 0 {r * 0.22:.1f} {-r * 0.14:.1f} {r * 0.22:.1f}", "#3A2418", 4, seed, 1, 1))
    n = len(cols)
    pts = []
    for i in range(n):
        a0 = math.radians(180 + 180 * i / n)
        a1 = math.radians(180 + 180 * (i + 1) / n)
        p0 = (cx + r * math.cos(a0), cy + r * 0.5 + r * 0.62 * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * 0.5 + r * 0.62 * math.sin(a1))
        top = (cx, cy - r * 0.62)
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + r * 0.08)
        seg = [top, (top[0] + (p0[0] - top[0]) * 0.5 - 2, top[1] + (p0[1] - top[1]) * 0.5 - 4), p0, mid, p1,
               (top[0] + (p1[0] - top[0]) * 0.5 + 2, top[1] + (p1[1] - top[1]) * 0.5 - 4)]
        c = cols[i]
        out.append(painted(D, seg, (lt(c, 0.35), c, dk(c, 0.35)), seed + i, sdir=(0.5, 0.8), sk=0.12, angle=-60, n=8, inkw=1.4, hi=0.3, hik=0.1))
        pts.append(p0)
    # white piping along the ribs
    for i in range(n + 1):
        a = math.radians(180 + 180 * i / n)
        p = (cx + r * math.cos(a), cy + r * 0.5 + r * 0.62 * math.sin(a))
        out.append(pline([(cx, cy - r * 0.62), ((cx + p[0]) / 2, (cy - r * 0.62 + p[1]) / 2 - 4), p], "#FFFFFF", 2, seed + i, 0.85, 1))
    out.append(f'<circle cx="{cx}" cy="{cy - r * 0.62:.1f}" r="{r * 0.07:.1f}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>')
    out.append("</g>")
    return "".join(out)


def sequin_mask(D, cx, cy, w, seed):
    """Colombina mask covered in gold sequins, with turquoise trim and painted eye holes."""
    h = w * 0.42
    pts = [(cx, cy - h * 0.2), (cx - w * 0.12, cy - h * 0.48), (cx - w * 0.32, cy - h * 0.55), (cx - w * 0.5, cy - h * 0.62), (cx - w * 0.47, cy - h * 0.1),
           (cx - w * 0.36, cy + h * 0.32), (cx - w * 0.14, cy + h * 0.4), (cx, cy + h * 0.12), (cx + w * 0.14, cy + h * 0.4), (cx + w * 0.36, cy + h * 0.32),
           (cx + w * 0.47, cy - h * 0.1), (cx + w * 0.5, cy - h * 0.62), (cx + w * 0.32, cy - h * 0.55), (cx + w * 0.12, cy - h * 0.48)]
    d = smooth_closed(pts)
    out = [cast(D, cx + 8, cy + h * 0.6, w * 0.5, h * 0.12, strength=0.3, seed=seed)]
    out.append(f'<path d="{d}" fill="#E8A81E"/>')
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    inner = []
    for j in range(16):
        for i in range(30):
            x = cx - w * 0.55 + i * w / 27 + (j % 2) * w / 54
            y = cy - h * 0.7 + j * h / 13
            lit = (-(x - cx) / w * 0.6 - (y - cy) / h * 0.8)
            base = "#FFE07A" if lit > 0.35 else ("#C8860E" if lit < -0.3 else rnd.choice(["#F6C21C", "#F2B020", "#FFD24A"]))
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{w / 58:.1f}" fill="{base}" stroke="#9A6008" stroke-width="0.8"/>')
            if rnd.random() < 0.18:
                inner.append(f'<circle cx="{x - 1:.1f}" cy="{y - 1:.1f}" r="1.6" fill="#FFFFFF" opacity="0.9"/>')
    inner.append(shade_over(D, d, "#5A2A00", 0.35, 0, 0, 0.3, 1, 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # eye holes
    for sg in (-1, 1):
        e = blob_pts(cx + sg * w * 0.22, cy - h * 0.08, w * 0.11, h * 0.2, seed + sg, 0.05, 14, sg * -12)
        e = [(x, y - (h * 0.12 if (x - cx) * sg > w * 0.27 else 0)) for x, y in e]
        out.append(f'<path d="{smooth_closed(e)}" fill="#3A1A4A"/>')
        out.append(ink(smooth_closed(e), "#1FA5A0", 4, seed + sg, 1, 1))
    out.append(ink(d, "#1FA5A0", 5, seed + 5, 1, 1))
    out.append(ink(d, "#5A2A00", 1.6, seed + 6, 1, 0.7))
    for k in range(9):
        t = k / 8
        x = cx - w * 0.36 + t * w * 0.72
        y = cy + h * 0.32 + (0.08 * h if 0.25 < t < 0.75 else 0) - (h * 0.25 if abs(t - 0.5) < 0.1 else 0)
    return "".join(out)


@design("carnaval")
def carnaval():
    D = Doc2("cv")
    out = [sky(D, [(0, "#3A1A6E"), (0.55, "#7A2A8A"), (1, "#C8306A")], 3, 600, ["#8A3AB0", "#2A0E50", "#E84A8A"], 90, angle=-30, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 270, 280, "#FF9AD0", 0.4))
    out.append(soft_glow(D, 300, 270, 140, "#FFE6A0", 0.35))
    # sunbeam spotlights
    for a in (-30, -12, 8, 26):
        x = 300 + a * 9
        out.append(f'<path d="M {300 + a * 2} -10 L {x - 40} 610 L {x + 40} 610 Z" fill="#FFFFFF" opacity="0.045"/>')
    # serpentine streamers from the top corners
    for k, (pts, c) in enumerate(((catmull([(-10, 120), (40, 90), (70, 150), (120, 110), (150, 170), (210, 150)], 6), "#F6C21C"),
                                  (catmull([(610, 90), (560, 70), (540, 130), (490, 100), (470, 160), (420, 140)], 6), "#1FC8B0"),
                                  (catmull([(-10, 420), (40, 460), (80, 420), (110, 480), (90, 540)], 6), "#FF6AA8"),
                                  (catmull([(610, 440), (560, 400), (540, 470), (500, 450), (510, 530)], 6), "#F6C21C"))):
        out.append(hg.streamer(D, pts, 9, c, 70 + k))
    # plumes behind the mask
    plume = [((-168, 0.8), "#F6C21C"), ((-150, 0.95), "#1F8A4C"), ((-132, 1.05), "#F6C21C"), ((-116, 1.1), "#2E6AC8"), ((-100, 1.05), "#E8307A"),
             ((-84, 1.0), "#1FB5A0"), ((-68, 0.9), "#F6C21C"), ((-54, 0.8), "#FF7A3A")]
    out.append('<g transform="rotate(-7 300 290)">')
    for k, ((ang, s), c) in enumerate(plume):
        out.append(feather(D, 186, 222, 170 * s, ang, (lt(c, 0.4), c, dk(c, 0.3)), 80 + k, w=34 * s))
    out.append(sequin_mask(D, 300, 290, 290, 90))
    # jewel where the plumes meet
    out.append(painted(D, blob_pts(184, 222, 18, 18, 91, 0.04, 12), ("#9AF0E8", "#1FB5A0", "#0E6464"), 91, sk=0.2, n=6, inkw=1.6, hi=0.5))
    out.append(sparkle(178, 215, 7, "#FFFFFF", 0.95))
    out.append("</g>")
    # frevo umbrella
    out.append(frevo_umbrella(D, 470, 160, 82, 20, 92))
    # confetti everywhere
    out.append(hg.confetti(93, 140, (40, 40, 560, 560), ["#F6C21C", "#1FC8B0", "#FF6AA8", "#FFFFFF", "#7AD06A", "#FF9A3A"],
                           avoid=((150, 355, 450, 520),), s=(6, 12)))
    out.append(hg.sparkles(94, 16, (60, 60, 540, 540), "#FFF6C8", (5, 11), avoid=((140, 360, 460, 520),)))
    # lettering
    out.append(letters(D, 300, 452, "Carnaval", SERIF_IT, 132, "#FFD23A", ["#FFE88A", "#F2A81D", "#FFF2B8"], 95, max_w=450,
                       shadow="#2A0A3A", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 502, "TODO MUNDO NA FOLIA", "#FFFFFF", font=MONO, size=19, ls=4, line_w=32, gap=14, line="#FF9AC8"))
    return finish_b(D, out, 96, "#FFFFFF", 0.6)


# ================================================================ 7. saudade — an airmail envelope from home
def stamp(D, x, y, w, h, seed, art):
    """Postage stamp: perforated white edge, a painted vignette inside (art drawn in a clip), slight tilt."""
    pts = []
    n_w, n_h = int(w / 9), int(h / 9)
    for i in range(n_w):
        pts += [(x + i * w / n_w, y), (x + (i + 0.5) * w / n_w, y + 3.2)]
    for i in range(n_h):
        pts += [(x + w, y + i * h / n_h), (x + w - 3.2, y + (i + 0.5) * h / n_h)]
    for i in range(n_w):
        pts += [(x + w - i * w / n_w, y + h), (x + w - (i + 0.5) * w / n_w, y + h - 3.2)]
    for i in range(n_h):
        pts += [(x, y + h - i * h / n_h), (x + 3.2, y + h - (i + 0.5) * h / n_h)]
    out = [f'<path d="{pd([(px + 3, py + 4) for px, py in pts])}" fill="#3A2418" opacity="0.18"/>',
           f'<path d="{pd(pts)}" fill="#FFFDF6"/>']
    ix0, iy0, ix1, iy1 = x + 9, y + 9, x + w - 9, y + h - 9
    cid = D.clip(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}"/>')
    out.append(f'<g {cid}>{art(ix0, iy0, ix1, iy1)}</g>')
    out.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.6"/>')
    out.append(ink(pd(pts), "#B8A890", 1, seed, 1, 0.7))
    return "".join(out)


@design("saudade")
def saudade():
    D = Doc2("sd")
    out = [paper(D.nid(), "#F6EEDC", FLECK, 71)]
    # airmail chevron border, bleeding off the edge
    cols = ["#1F8A4C", "#F6C21C", "#1F4FA0", "#F6C21C"]
    band = 36
    edge = []
    k = 0
    for side in range(4):
        for i in range(-1, 16):
            t0, t1 = i * 40, i * 40 + 26
            c = cols[k % 4]
            k += 1
            if side == 0:
                poly = [(t0, 0), (t1, 0), (t1 - band, band), (t0 - band, band)]
            elif side == 1:
                poly = [(600, t0), (600, t1), (600 - band, t1 - band), (600 - band, t0 - band)]
            elif side == 2:
                poly = [(600 - t0, 600), (600 - t1, 600), (600 - t1 + band, 600 - band), (600 - t0 + band, 600 - band)]
            else:
                poly = [(0, 600 - t0), (0, 600 - t1), (band, 600 - t1 + band), (band, 600 - t0 + band)]
            edge.append(f'<path d="{hg.org_poly(poly, k, 0.5, 10, 1)}" fill="{c}" opacity="0.92"/>')
    out.append("".join(edge))
    out.append(f'<rect x="{band}" y="{band}" width="{600 - 2 * band}" height="{600 - 2 * band}" fill="none" stroke="#C8B894" stroke-width="1.4"/>')
    # VIA AÉREA label
    out.append(painted(D, rect_pts(70, 76, 250, 116, 18, 72, 0.6), AZUL, 72, sdir=(0.5, 1), sk=0.1, angle=0, n=16, inkw=1.6, hi=0.3))
    out.append(label(160, 105, "VIA AÉREA", JOS, 24, "#FFFFFF", ls=4, max_w=164))

    # stamp with a painted ipê on a green hill
    def ipe_art(x0, y0, x1, y1):
        a = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{D.lin([(0, "#7EC8E8"), (1, "#E8F6F0")])}"/>',
             f'<circle cx="{x1 - 16}" cy="{y0 + 18}" r="9" fill="#FFE07A"/>',
             hill(D, [(x0 - 5, y1 - 26), ((x0 + x1) / 2, y1 - 36), (x1 + 5, y1 - 24)], y1 + 5, VERDE, 73, inkw=0, n=20),
             taper([((x0 + x1) / 2, y1 - 32), ((x0 + x1) / 2 - 2, y1 - 52), ((x0 + x1) / 2 + 2, y1 - 62)], 5, 2.5, "#5A3A22")]
        a.append(dab_crown(D, (x0 + x1) / 2, y1 - 74, 30, 20, [AMAR, ("#FFF2A0", "#F2D040", "#D8A010")], 74, n=40, size=(3, 6), inkw=0))
        return "".join(a)
    out.append('<g transform="rotate(4 470 128)">' + stamp(D, 418, 72, 104, 118, 75, ipe_art) + "</g>")
    # postmark: double ring with a heart, wavy cancellation lines
    pm = [f'<circle cx="402" cy="160" r="38" fill="none" stroke="#2A3A6A" stroke-width="2.2" opacity="0.6"/>',
          f'<circle cx="402" cy="160" r="30" fill="none" stroke="#2A3A6A" stroke-width="1.4" opacity="0.6"/>']
    pm.append(f'<path d="{smooth_closed(heart_d(402, 162, 11))}" fill="#2A3A6A" opacity="0.55"/>')
    for k2 in range(4):
        y = 132 + k2 * 14
        pm.append(f'<path d="M 300 {y} q 10 -6 20 0 t 20 0 t 20 0 t 20 0" stroke="#2A3A6A" stroke-width="2" fill="none" opacity="0.5"/>')
    out.append("".join(pm))
    # address lines (ruled, like the front of the envelope)
    for y in (430, 470):
        out.append(pline([(150, y), (300, y + 1), (450, y)], "#B8A890", 1.6, y, 0.8, 1))
    # hero word, handwritten feel
    out.append(letters(D, 300, 330, "saudade", SERIF_IT, 138, "#1F3F8A", ["#2E5AB8", "#14286A", "#3E6AC8"], 76, max_w=450,
                       shadow="#C8D4EC", soff=(0.015, 0.03), angle=-40, hi="#8AA8E8", rot=-4))
    out.append(letters(D, 300, 410, "a falta que você me faz", SERIF_IT, 38, "#7A3218", ["#9A4A28", "#5A2210"], 77, max_w=380, wob=0.4, rot=-2))
    # wax seal heart with a pressed ipê sprig
    sx, sy = 300, 490
    out.append(cast(D, sx + 4, sy + 34, 52, 9, strength=0.3, seed=78))
    seal = blob_pts(sx, sy, 44, 41, 79, 0.1, 18)
    out.append(painted(D, seal, ("#F07A6A", "#C02A2A", "#7A0E12"), 79, sdir=(0.6, 0.8), sk=0.18, angle=-40, n=20, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(sx, sy, 30, 29, 83, 0.04, 16)}" fill="none" stroke="#7A0E12" stroke-width="2" opacity="0.5"/>')
    out.append(painted(D, heart_d(sx, sy + 1, 19), ("#E05A50", "#A01C1E", "#600A0E"), 80, sdir=(-0.6, -0.8), sk=0.25, n=6, inkw=1, hi=0.2))
    out.append(leaf_simple(D, sx - 40, sy + 4, 56, 12, -170, VERDE, 84))
    out.append(leaf_simple(D, sx + 40, sy - 2, 56, 12, -10, VERDE, 85))
    for k2, (dx, dy, a) in enumerate(((-70, -8, -160), (66, -16, -20), (-56, 22, 160), (88, 10, 0))):
        for j in range(5):
            aa = math.radians(j * 72 + k2 * 30)
            fx, fy = sx + dx + math.cos(aa) * 8, sy + dy + math.sin(aa) * 8
            out.append(f'<path d="{blob(fx, fy, 8.5, 6, 81 + k2 * 7 + j, 0.15, 8, math.degrees(aa))}" fill="{["#F6C21C", "#FFD84A", "#E8A810"][j % 3]}"/>')
            out.append(ink(blob(fx, fy, 8.5, 6, 81 + k2 * 7 + j, 0.15, 8, math.degrees(aa)), "#B8700A", 0.9, j, 1, 0.5))
        out.append(f'<circle cx="{sx + dx}" cy="{sy + dy}" r="3.2" fill="#B8700A"/>')
    return finish_b(D, out, 82)


# ================================================================ 8. bom dia — a bem-te-vi singing at sunrise
def bem_te_vi(D, ox, oy, s, seed, sing=True):
    """Bem-te-vi (great kiskadee) perched facing left: yellow belly, brown back, rufous wing edges, bold black
    and white striped head, black bill (open when singing). (ox, oy) = feet on the branch."""
    def L(pts):
        return [(ox + x * s, oy + y * s) for x, y in pts]
    out = []
    out.append(painted(D, L([(14, -40), (34, -50), (74, 30), (64, 40), (50, 36)]), ("#A8845A", "#6E5034", "#3A2818"), seed, sdir=(1, 0.3), sk=0.2,
                       angle=60, n=12, inkw=1.6, hi=0.3))
    body = L([(-36, -100), (-10, -122), (24, -112), (38, -76), (34, -36), (14, -8), (-12, -4), (-30, -24), (-40, -60)])
    out.append(painted(D, body, ("#FFF08A", "#F6CC24", "#C0900A"), seed + 1, sdir=(0.8, 0.4), sk=0.15, angle=70, n=40,
                       cols=["#FFF2A0", "#E8B010", "#FFE060"], inkw=1.8, hi=0.45))
    wing = L([(-4, -112), (24, -112), (40, -76), (40, -40), (26, -20), (6, -52)])
    out.append(painted(D, wing, ("#A8845A", "#7A5A3A", "#3E2A18"), seed + 2, sdir=(1, 0.3), sk=0.15, angle=70, n=16, inkw=1.6, hi=0.3))
    for t in (0.3, 0.55, 0.8):
        out.append(pline(L([(6 + 30 * t, -100 + 10 * t), (10 + 26 * t, -40 - 16 * t)]), "#D8783A", 2.2, seed, 0.75, 1))
    head = L([(-44, -132), (-36, -160), (-10, -170), (14, -158), (20, -134), (6, -112), (-20, -108), (-40, -116)])
    hd = smooth_closed(head)
    out.append(f'<path d="{hd}" fill="#FFFDF4"/>')
    cid = D.clip(f'<path d="{hd}"/>')
    inner = [f'<path d="{smooth_closed(L([(-48, -150), (-30, -174), (20, -174), (24, -148), (-10, -152)]))}" fill="#16120E"/>',
             f'<path d="{smooth_closed(L([(-44, -138), (-10, -140), (24, -136), (24, -122), (-8, -128), (-44, -128)]))}" fill="#16120E"/>',
             strokes(D.nid(), hd, (ox - 50 * s, oy - 175 * s, ox + 30 * s, oy - 100 * s), ["#FFFFFF", "#D8D0C0"], seed, n=12, angle=0, length=(4 * s, 10 * s), width=(0.8, 1.6), opacity=(0.2, 0.4))]
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(hd, INK, 1.6, seed + 3, 1, 0.7))
    ex, ey = ox - 22 * s, oy - 134 * s
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.2 * s:.1f}" fill="#3A1A0A"/><circle cx="{ex - 1.2 * s:.1f}" cy="{ey - 1.3 * s:.1f}" r="{1.4 * s:.1f}" fill="#FFFFFF"/>')
    # bill
    up = L([(-38, -142), (-80, -144), (-82, -139), (-38, -130)])
    lo = L([(-38, -128), (-72, -120), (-74, -116), (-38, -121)]) if sing else L([(-38, -130), (-78, -136), (-38, -125)])
    out.append(f'<path d="{smooth_closed(up)}" fill="#1A1410"/><path d="{smooth_closed(lo)}" fill="#2A2018"/>')
    for dx in (-8, 8):
        fx, fy = ox + dx * s, oy
        out.append(ink(f"M {fx - 5 * s:.1f} {fy + 3 * s:.1f} q {5 * s:.1f} {-8 * s:.1f} {10 * s:.1f} 0", "#3A3030", 3 * s, seed + dx, 1, 1))
    return "".join(out)


def note(x, y, s, col, op=0.9, rot_=0):
    return (f'<g transform="rotate({rot_} {x} {y})" opacity="{op}"><ellipse cx="{x}" cy="{y}" rx="{s * 0.55:.1f}" ry="{s * 0.4:.1f}" transform="rotate(-20 {x} {y})" fill="{col}"/>'
            f'<path d="M {x + s * 0.5:.1f} {y - s * 0.1:.1f} L {x + s * 0.5:.1f} {y - s * 1.6:.1f} q {s * 0.3:.1f} {s * 0.5:.1f} {s * 0.8:.1f} {s * 0.6:.1f}" stroke="{col}" stroke-width="{max(1.8, s * 0.16):.1f}" fill="none" stroke-linecap="round"/></g>')


@design("bom-dia")
def bom_dia():
    D = Doc2("bd")
    out = [sky(D, [(0, "#8ED0EA"), (0.38, "#CDEBE8"), (0.6, "#FFE6A8"), (0.78, "#FFC878")], 3, 600, ["#FFFFFF", "#FFE8B0", "#A8DCEE"], 80)]
    # the sun coming up behind the hills
    out.append(soft_glow(D, 236, 408, 300, "#FFF2B0", 0.75))
    for i in range(18):
        a = math.radians(-180 + i * 10 + 5)
        out.append(f'<path d="M 236 408 L {236 + 600 * math.cos(a - 0.04):.1f} {408 + 600 * math.sin(a - 0.04):.1f} L {236 + 600 * math.cos(a + 0.04):.1f} {408 + 600 * math.sin(a + 0.04):.1f} Z" fill="#FFFFFF" opacity="0.12"/>')
    sun = blob_pts(236, 408, 108, 108, 81, 0.01, 30)
    out.append(painted(D, sun, ("#FFF4B0", "#FFD23A", "#F2A01A"), 81, sdir=(0.3, 0.8), sk=0.06, angle=-30, n=60, slen=(20, 60), sw=(2, 5), inkw=0, hi=0.5, hik=0.05, curve=0.5))
    out.append(puff_cloud(D, 470, 236, 120, 82, ("#FFFFFF", "#FFF6EC", "#F4C8A8")))
    out.append(puff_cloud(D, 96, 262, 90, 83, ("#FFFFFF", "#FFF6EC", "#F4C8A8"), op=0.9))
    # hills: far (morning haze) and near
    out.append(hill(D, ridge([(-20, 430), (100, 404), (230, 424), (380, 398), (500, 420), (620, 400)], 84, 6), 620, ("#B8DCB0", "#90C49A", "#6AA27A"), 84, inkw=0, sop=(0.1, 0.25)))
    out.append(hill(D, ridge([(-20, 476), (140, 456), (300, 470), (460, 450), (620, 466)], 85, 5), 620, ("#A8D47A", "#6EAE4A", "#3E7A2A"), 85, inkw=1.4, inkop=0.4))
    # roofs of a little town in the valley
    rnd = random.Random(86)
    # the little church on the rise, then the houses of the town tumbling down the valley
    chx, chb = 150, 446
    out.append(painted(D, rect_pts(chx - 22, chb - 40, chx + 22, chb, 8, 860, 0.3), ("#FFFFFF", "#F4EEE0", "#B8B0A0"), 860, sk=0.1, n=6, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(chx - 9, chb - 74, chx + 9, chb - 38, 6, 861, 0.3), ("#FFFFFF", "#F4EEE0", "#B8B0A0"), 861, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(f'<path d="M {chx - 11} {chb - 73} L {chx} {chb - 90} L {chx + 11} {chb - 73} Z" fill="#2E62B0"/>')
    out.append(f'<path d="M {chx} {chb - 90} L {chx} {chb - 100} M {chx - 4} {chb - 96} L {chx + 4} {chb - 96}" stroke="#7A4A1E" stroke-width="1.8"/>')
    out.append(f'<path d="M {chx - 26} {chb - 38} L {chx} {chb - 54} L {chx + 26} {chb - 38} Z" fill="#C0582E"/>')
    out.append(f'<path d="{hg.org_rect(chx - 5, chb - 18, 10, 18, 862, 0.3, 6, 4)}" fill="#2E62B0"/><circle cx="{chx}" cy="{chb - 62}" r="3.4" fill="#2E62B0"/>')
    for i, (x, b_, w) in enumerate(((60, 452, 30), (92, 458, 34), (196, 452, 32), (236, 460, 36), (280, 456, 30), (318, 462, 34), (100, 476, 30), (170, 472, 36))):
        out.append(town_house(D, x, b_, w, w * 0.62, 870 + i, rnd.choice(["#FFFDF4", "#FFF4D8", "#FCE0C8", "#E8F0F8"]), "gable", haze=0.1))
    out.append(grass(88, (0, 470, 600, 600), ["#3E7A2A", "#5E9A3A", "#9ACB5A"], 120, (8, 18)))
    # flowering branch from the right, with the bird
    bp = catmull([(620, 446), (540, 434), (450, 428), (380, 432), (330, 446)], 6)
    out.append(branch(D, bp, 16, 7, 89))
    for k, (x, y, a) in enumerate(((560, 428, -120), (520, 440, 60), (400, 428, -100), (360, 438, 120), (604, 436, -60))):
        out.append(leaf_simple(D, x, y, 60, 15, a, VERDE, 90 + k))
    out.append(bem_te_vi(D, 470, 428, 1.2, 95))
    for k, (x, y) in enumerate(((540, 420), (404, 424), (380, 446), (346, 442))):
        out.append(hibiscus(D, x, y, 13, ("#FFC8D8", "#F06A98", "#B02A5A"), 96 + k, k * 50, inkw=1))
    # notes of the song
    for k, (x, y, s, r_) in enumerate(((326, 262, 18, -10), (292, 236, 15, 8), (334, 216, 13, -6))):
        out.append(note(x, y, s, "#7A4A1E", 0.85, r_))
    # lettering
    out.append(letters(D, 300, 162, "bom dia!", SERIF_IT, 134, "#1F6A40", ["#2E8A50", "#0E4A2A", "#4AA060"], 97, max_w=440,
                       shadow="#FFFDF0", soff=(0.02, 0.03), angle=-40, hi="#A8E0A0"))
    out.append(label(300, 532, "QUE SEU DIA SEJA LEVE", MONO, 19, "#FFFDF0", ls=4, max_w=420))
    return finish_b(D, out, 98)


# ================================================================ 9. café com leite — copo americano and pão na chapa
def copo_americano(D, cx, base, h, seed, fill=0.9, drink=("#E8C8A0", "#C08A58", "#7A4A26"), foam="#F2E2C8"):
    """The faceted bakery glass: slight taper, smooth band near the rim, vertical facets below, thick base."""
    wt, wb = h * 0.58, h * 0.48
    top = base - h
    l_t, r_t, l_b, r_b = cx - wt / 2, cx + wt / 2, cx - wb / 2, cx + wb / 2
    out = [cast(D, cx + 10, base + 2, wt * 0.8, 9, strength=0.4, seed=seed)]
    glass = [(l_t, top), (r_t, top), (r_b, base - 3), (r_b - 4, base), (l_b + 4, base), (l_b, base - 3)]
    gd = pd(glass)
    out.append(f'<path d="{gd}" fill="#EAF2F2" opacity="0.5"/>')
    # drink inside
    ly = top + h * (1 - fill)
    liq = [(l_t + 4 + (wt - wb) / 2 * (ly - top) / h * 0, ly), (r_t - 4, ly), (r_b - 5, base - 14), (l_b + 5, base - 14)]
    def x_at(y, left):
        f = (y - top) / h
        return (l_t + (l_b - l_t) * f + 4) if left else (r_t + (r_b - r_t) * f - 4)
    liq = [(x_at(ly, True), ly), (x_at(ly, False), ly), (x_at(base - 14, False), base - 14), (x_at(base - 14, True), base - 14)]
    ld = pd(liq)
    g = D.lin([(0, drink[0]), (0.25, drink[1]), (1, drink[2])], 0, 0, 0, 1)
    out.append(f'<path d="{ld}" fill="{g}"/>')
    out.append(strokes(D.nid(), ld, bbox(liq), [drink[0], drink[2]], seed, n=20, angle=-90, length=(10, 30), width=(1, 3), opacity=(0.12, 0.3)))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, ly, (x_at(ly, False) - x_at(ly, True)) / 2, 6, 0, 360, 20))}" fill="{foam}"/>')
    out.append(specks(seed, (cx - wt * 0.3, ly - 3, cx + wt * 0.3, ly + 3), ["#FFFFFF", "#D8B890"], 14, (0.8, 1.6), (0.5, 0.9)))
    # facets: vertical light / dark bands on the lower 3/4
    cid = D.clip(f'<path d="{gd}"/>')
    fac = []
    nf = 9
    for i in range(nf + 1):
        t = i / nf
        xa = l_t + 0.0 + (r_t - l_t) * t
        xb = l_b + (r_b - l_b) * t
        ya = top + h * 0.26
        fac.append(f'<path d="M {xa:.1f} {ya:.1f} L {xb:.1f} {base - 8:.1f}" stroke="{"#FFFFFF" if i % 2 else "#5A6A6A"}" stroke-width="{2.4 if i % 2 else 1.2}" opacity="{0.55 if i % 2 else 0.35}"/>')
        if i < nf:
            fac.append(f'<path d="M {xa:.1f} {ya:.1f} q {(r_t - l_t) / nf / 2:.1f} -6 {(r_t - l_t) / nf:.1f} 0" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>')
    fac.append(f'<path d="M {l_t:.1f} {top + h * 0.24:.1f} L {r_t:.1f} {top + h * 0.24:.1f}" stroke="#FFFFFF" stroke-width="2.2" opacity="0.6"/>')
    fac.append(shade_over(D, gd, "#2A3A3A", 0.3, 0, 0, 1, 0, 0.5))
    fac.append(taper([(l_t + 8, top + 8), (l_t + 9, top + h * 0.22)], 6, 3, "#FFFFFF", 0.85))
    fac.append(f'<path d="{pd([(l_b, base - 12), (r_b, base - 12), (r_b, base), (l_b, base)])}" fill="#C8D8D8" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(fac)}</g>')
    out.append(ink(gd, "#5A6A6A", 1.8, seed, 2, 0.75))
    out.append(ink(smooth_closed(ell_pts(cx, top, wt / 2, 5, 0, 360, 24)), "#5A6A6A", 1.6, seed + 1, 1, 0.7))
    out.append(taper(ell_pts(cx, top, wt / 2, 5, 200, 340, 10), 2, 2, "#FFFFFF", 0.9))
    return "".join(out)


def pao_frances(D, cx, cy, w, seed, rot_=0, butter=True):
    """Pão francês na chapa: split roll, toasted face, crisp crust with the pestana, melting butter."""
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    h = w * 0.42
    crust = blob_pts(cx, cy, w / 2, h / 2, seed, 0.04, 22)
    out.append(painted(D, crust, ("#F6C27A", "#D8883A", "#8A4A16"), seed, sdir=(0.5, 0.9), sk=0.2, angle=-20, n=40, inkw=1.8, hi=0.45))
    # pestana (the ridge) and scoring
    out.append(taper([(cx - w * 0.4, cy - h * 0.05), (cx - w * 0.1, cy - h * 0.25), (cx + w * 0.2, cy - h * 0.2), (cx + w * 0.42, cy - h * 0.02)], 6, 3, "#FFE2A8", 0.85))
    out.append(taper([(cx - w * 0.38, cy), (cx - w * 0.1, cy - h * 0.18), (cx + w * 0.2, cy - h * 0.13), (cx + w * 0.4, cy + h * 0.02)], 3, 1.5, "#8A4A16", 0.6))
    # toasted, buttered cut face
    face = blob_pts(cx, cy + h * 0.12, w * 0.42, h * 0.26, seed + 1, 0.05, 18)
    out.append(painted(D, face, ("#FFF4D8", "#F2DCA8", "#C8A060"), seed + 1, sdir=(0.5, 0.9), sk=0.12, n=14, inkw=1.2, hi=0.3))
    out.append(specks(seed, (cx - w * 0.36, cy + h * 0.02, cx + w * 0.36, cy + h * 0.28), ["#C8803A", "#A8602A", "#E8B060"], 30, (0.8, 2.2), (0.4, 0.9)))
    if butter:
        out.append(painted(D, blob_pts(cx + w * 0.08, cy + h * 0.1, w * 0.12, h * 0.1, seed + 2, 0.15, 10), ("#FFF8C0", "#FFE680", "#E8C040"), seed + 2, sk=0.1, n=4, inkw=1, hi=0.5))
        out.append(f'<path d="{blob(cx + w * 0.12, cy + h * 0.18, w * 0.2, h * 0.09, seed + 3, 0.2, 10)}" fill="#FFE680" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


@design("cafe-com-leite")
def cafe_com_leite():
    D = Doc2("cl")
    # padaria wall of little white tiles with a green band, wooden counter
    out = [f'<rect width="600" height="600" fill="#EEF2EA"/>']
    rnd = random.Random(101)
    tiles = []
    for j in range(0, 18):
        for i in range(0, 20):
            x, y = i * 32, j * 32
            c = mix("#F6F8F2", rnd.choice(["#DDE8E0", "#FFFFFF", "#E8EEE6"]), rnd.uniform(0.2, 0.8))
            tiles.append(f'<path d="{hg.org_rect(x + 1.5, y + 1.5, 29, 29, i * 31 + j, 0.4, 10, 3)}" fill="{c}"/>')
            if rnd.random() < 0.3:
                tiles.append(f'<path d="M {x + 6} {y + 7} l 8 -2" stroke="#FFFFFF" stroke-width="2" opacity="0.9" stroke-linecap="round"/>')
    out.append(f'<rect width="600" height="600" fill="#C8D4C8"/>' + "".join(tiles))
    out.append(f'<path d="{hg.org_rect(-10, 372, 620, 28, 102, 0.6, 14, 1)}" fill="#2E7A50"/>')
    out.append(f'<path d="{hg.org_rect(-10, 372, 620, 6, 103, 0.4, 14, 1)}" fill="#5EAA7A" opacity="0.7"/>')
    out.append(blooms(104, ["#FFFFFF", "#C8D8C0"], 6, (0, 0, 600, 400), (100, 180), (0.1, 0.2)))
    out.append(soft_glow(D, 430, 120, 300, "#FFF4C8", 0.5))
    # wooden counter
    out.append(wood_planks(D, 424, 600, 105, ("#C8885A", "#94582E", "#5A3014"), 3))
    out.append(f'<path d="{hg.org_rect(-10, 410, 620, 18, 106, 0.4, 14, 1)}" fill="#7A4420"/>')
    out.append(f'<rect y="410" width="600" height="4" fill="#E8B07A" opacity="0.6"/>')
    # the glass of café com leite
    out.append(copo_americano(D, 214, 514, 196, 107))
    out.append(steam(214, 310, 46, 108, "#FFFFFF", 3, 24, 6, 0.75))
    # pão na chapa on a little plate
    out.append(cast(D, 414, 512, 110, 14, strength=0.4, seed=109))
    plate = ell_pts(410, 494, 104, 26, 0, 360, 30)
    out.append(painted(D, plate, ("#FFFFFF", "#F2EEE6", "#B8B0A0"), 110, sdir=(0.4, 1), sk=0.15, angle=0, n=20, inkw=1.8, hi=0.4))
    out.append(ink(smooth_open(ell_pts(410, 494, 92, 20, 10, 170, 14)), "#2E7A50", 2.2, 111, 1, 0.8))
    out.append(pao_frances(D, 392, 468, 136, 112, -8))
    out.append(pao_frances(D, 446, 486, 120, 113, 10, butter=True))
    # a sugar packet and a spoon
    out.append(taper([(100, 528), (150, 512), (170, 506)], 4, 3, "#B8BCC4"))
    out.append(f'<path d="{blob(96, 530, 11, 6, 114, 0.1, 10, -16)}" fill="#C8CCD4"/>' + ink(blob(96, 530, 11, 6, 114, 0.1, 10, -16), INK, 1.2, 114, 1, 0.6))
    # lettering: CAFÉ big, com leite in script tucked under
    out.append(letters(D, 300, 178, "CAFÉ", ANTON, 112, "#5A2E16", ["#7A4224", "#3A1A0A", "#8A5232"], 115, ls=10, max_w=330,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-70, wob=0.5))
    out.append(letters(D, 304, 244, "com leite", SERIF_IT, 72, "#2E7A50", ["#3E9A64", "#1E5A38"], 116, max_w=330,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, rot=-3))
    return finish_b(D, out, 117)


# ================================================================ 10. tamo junto — two parakeets snuggled on a branch
def parakeet(D, ox, oy, s, seed, flip=False, lean=0, pal=(("#B8E87A", "#4AA83A", "#1E6A22"))):
    """Periquito: green teardrop body, long tapering tail, yellowish face, pale hooked beak. (ox, oy) feet; faces left
    unless flip."""
    sx = -1 if flip else 1

    def L(pts):
        return rot([(ox + sx * x * s, oy + y * s) for x, y in pts], ox, oy, lean * sx)
    out = []
    tail = L([(4, -20), (22, -26), (32, 50), (28, 82), (18, 84), (8, 34)])
    out.append(painted(D, tail, ("#7ACB6A", "#2E8A3A", "#14501E"), seed, sdir=(1, 0.3), sk=0.2, angle=80, n=14, inkw=1.6, hi=0.3))
    out.append(pline(L([(16, -10), (24, 78)]), "#1E6A2A", 1.4, seed, 0.6, 1))
    body = L([(-30, -86), (-6, -104), (22, -92), (32, -56), (26, -20), (8, -2), (-14, -4), (-28, -28), (-34, -60)])
    out.append(painted(D, body, pal, seed + 1, sdir=(0.8, 0.4), sk=0.16, angle=70, n=40, cols=[pal[0], pal[2], "#D8F28A", pal[1]], inkw=1.8, hi=0.45))
    wing = L([(-2, -92), (22, -88), (34, -56), (30, -24), (14, -16), (2, -50)])
    out.append(painted(D, wing, ("#7ACB6A", "#2E8A3A", "#14501E"), seed + 2, sdir=(1, 0.3), sk=0.15, angle=70, n=16, inkw=1.6, hi=0.3))
    rnd = random.Random(seed)
    for i in range(7):
        x, y = rnd.uniform(6, 26), rnd.uniform(-80, -30)
        out.append(pline(L([(x - 5, y), (x, y + 4), (x + 5, y)]), "#1E6A22", 1.3, seed + i, 0.55, 1))
    head = blob_pts(0, 0, 1, 1, seed + 3, 0.04, 14)
    head = L([(-12 + 26 * x, -108 + 24 * y) for x, y in head])
    out.append(painted(D, head, ("#E8F890", "#9AD24A", "#4E8A22"), seed + 3, sdir=(0.8, 0.5), sk=0.15, n=14, inkw=1.6, hi=0.45))
    # beak
    bk = L([(-34, -118), (-46, -114), (-48, -104), (-40, -98), (-32, -100)])
    out.append(painted(D, bk, ("#FFF0E0", "#F2C8B0", "#B88A70"), seed + 4, sk=0.2, n=4, inkw=1.4, hi=0.4))
    # eye with a pale ring
    ex, ey = L([(-18, -112)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{6 * s:.1f}" fill="#FFF8E0"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3.8 * s:.1f}" fill="#1A1008"/>'
               f'<circle cx="{ex - 1.2 * s:.1f}" cy="{ey - 1.4 * s:.1f}" r="{1.3 * s:.1f}" fill="#FFFFFF"/>')
    ck = L([(-16, -98)])[0]
    out.append(f'<circle cx="{ck[0]:.1f}" cy="{ck[1]:.1f}" r="{5 * s:.1f}" fill="#F28A8A" opacity="0.45"/>')
    for dx in (-8, 8):
        fx, fy = L([(dx, 0)])[0]
        out.append(ink(f"M {fx - 5 * s:.1f} {fy + 3 * s:.1f} q {5 * s:.1f} {-8 * s:.1f} {10 * s:.1f} 0", "#A87A6A", 3 * s, seed + dx, 1, 1))
    return "".join(out)


@design("tamo-junto")
def tamo_junto():
    D = Doc2("tj")
    out = [sky(D, [(0, "#24508A"), (1, "#1A3A6E")], 3, 600, ["#2E5A9A", "#14306A", "#3E6AAA"], 110, angle=-30, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 214, 260, "#FFE8A0", 0.4))
    # a big full moon rising behind the pair, the canopy dark below
    out.append(painted(D, blob_pts(300, 214, 124, 124, 117, 0.008, 36), ("#FFFBEA", "#F6EACB", "#D8C8A0"), 117, sdir=(0.5, 0.7), sk=0.06, angle=-30, n=50, inkw=0, hi=0.4, edge=False))
    for k, (x, y, r) in enumerate(((256, 170, 18), (350, 240, 24), (310, 300, 12), (232, 262, 10), (372, 160, 9))):
        out.append(f'<path d="{blob(x, y, r, r * 0.85, 118 + k, 0.1, 12)}" fill="#D8C8A0" opacity="0.45"/>')
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#0A1A3A", 0), (0.6, "#0A1A3A", 0), (1, "#0A1A3A", 0.5)])}"/>')
    # big leaf silhouettes framing the corners
    for k, (x, y, a, L_) in enumerate(((-10, 90, 30, 170), (610, 120, 150, 180), (-10, 560, -20, 150), (610, 580, -160, 160))):
        out.append(banana_leaf(D, x, y, a, L_, 34, 120 + k, ("#3E7A5A", "#1E5A3E", "#0E3A26"), bg=None, splits=0))
    # branch across, little flowers
    rnd = random.Random(119)
    for _ in range(40):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 340)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    bp = catmull([(40, 290), (150, 274), (300, 266), (430, 270), (560, 256)], 6)
    out.append(branch(D, bp, 18, 9, 121))
    for k, (x, y, a) in enumerate(((90, 282, 130), (180, 270, -110), (420, 268, -70), (500, 260, 60), (540, 256, -120))):
        out.append(leaf_simple(D, x, y, 64, 16, a, VERDE, 122 + k))
    # the two of them, leaning in
    out.append(parakeet(D, 262, 268, 1.05, 130, flip=True, lean=-8))
    out.append(parakeet(D, 346, 268, 1.05, 131, flip=False, lean=8, pal=("#C8F08A", "#5AB844", "#226E26")))
    out.append(p_heart(D, 304, 104, 20, ("#FF9A9A", "#E8484A", "#9A1A20"), 132, -6))
    for x, y, s in ((256, 120, 6), (352, 90, 5), (236, 84, 4)):
        out.append(sparkle(x, y, s * 1.6, "#FFF2B0", 0.9))
    for k, (x, y) in enumerate(((130, 266), (470, 258), (560, 248))):
        out.append(hibiscus(D, x, y, 12, ("#FFF2B0", "#F6C21C", "#C08A0A"), 133 + k, k * 40, inkw=1, stamen="#E86A1E"))
    # lettering
    out.append(letters(D, 300, 462, "TAMO", ANTON, 128, "#FFF6E0", ["#FFFFFF", "#E8DCC0"], 140, ls=14, max_w=330,
                       shadow="#0E1E3E", soff=(0.025, 0.035), angle=-75, wob=0.5))
    out.append(letters(D, 324, 508, "junto", SERIF_IT, 88, "#F6C21C", ["#FFE07A", "#D89A10", "#FFF2B0"], 141, max_w=300,
                       shadow="#0E1E3E", soff=(0.02, 0.03), angle=-40, rot=-4))
    return finish_b(D, out, 142, "#FFFFFF", 0.6)


# ================================================================ 11. brasil — retro postcard: Sugarloaf at golden hour
@design("brasil")
def brasil():
    D = Doc2("br")
    out = [sky(D, [(0, "#3E8ACB"), (0.42, "#8ACBE0"), (0.62, "#FFE2A8"), (0.72, "#FFC888")], 3, 600, ["#FFFFFF", "#A8DCEE", "#FFE8B0"], 80)]
    out.append(soft_glow(D, 470, 370, 220, "#FFF0B0", 0.7))
    out.append(puff_cloud(D, 120, 300, 110, 150, ("#FFFFFF", "#FFF4EC", "#D8C8D8")))
    out.append(puff_cloud(D, 520, 196, 90, 151, ("#FFFFFF", "#FFF4EC", "#D8C8D8"), op=0.9))
    out.append('<g transform="translate(0 40)">')
    # far headlands
    out.append(hill(D, ridge([(-20, 360), (60, 330), (120, 344), (200, 316), (260, 350)], 152, 6), 600, ("#A8C0CC", "#8AA8B8", "#6A8A9A"), 152, inkw=0, sop=(0.05, 0.15)))
    # Sugarloaf (right) and Morro da Urca (left): rounded granite domes with green skirts
    def dome(pts, seed, rock=("#D8B8A0", "#9A8478", "#5A4A48")):
        o = [painted(D, pts, rock, seed, sdir=(-0.8, 0.2), sk=0.24, angle=-84, n=80, slen=(20, 70), sw=(1.5, 4),
                     cols=[rock[0], rock[2], "#F2D2B0", rock[1]], inkw=2, hi=0.5, hik=0.08)]
        x0, y0, x1, y1 = bbox(pts)
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        rnd = random.Random(seed)
        streaks = "".join(taper([(x, y0 + rnd.uniform(10, 60)), (x + rnd.uniform(-4, 4), y1 - rnd.uniform(40, 90))], rnd.uniform(2, 5), 0.6, "#4A3A38", rnd.uniform(0.15, 0.35))
                          for x in [x0 + (x1 - x0) * (0.15 + 0.7 * rnd.random()) for _ in range(9)])
        o.append(f'<g {cid}>' + streaks + light_over(D, smooth_closed(pts), "#FFD0A0", 0.55, 1, 0, 0.3, 0.3, 0.6) +
                 dab_crown(D, (x0 + x1) / 2, y1, (x1 - x0) * 0.7, (y1 - y0) * 0.3, [MATA, VERDE, ("#9ACB6A", "#5E9A3A", "#2E5A1E")], seed + 3, n=320,
                           size=(5, 10), inkw=0, base=True) + "</g>")
        return "".join(o)
    out.append(dome([(330, 420), (352, 300), (384, 228), (420, 196), (452, 204), (480, 244), (500, 320), (520, 420)], 153))
    out.append(dome([(150, 420), (176, 360), (214, 326), (256, 322), (290, 350), (316, 420)], 154))
    # the cable car line, with a little car
    out.append(f'<path d="M 252 324 Q 340 268 428 202" stroke="#3A3030" stroke-width="1.6" fill="none"/>')
    out.append(f'<path d="M 252 328 Q 340 272 428 206" stroke="#3A3030" stroke-width="1.2" fill="none" opacity="0.7"/>')
    out.append(f'<g transform="rotate(-30 352 262)"><path d="{hg.org_rect(342, 262, 22, 14, 155, 0.3, 6, 2)}" fill="#E8382E"/>'
               f'<rect x="345" y="265" width="16" height="5" fill="#FFF4D8"/><path d="M 353 262 L 353 256" stroke="#3A3030" stroke-width="1.6"/></g>')
    out.append("</g>")
    # the bay
    out.append(sea(D, 450, 600, [(0, "#7EC8D8"), (0.3, "#2E9AB8"), (1, "#1A5A8A")], 156, ["#FFFFFF", "#A8E0EE", "#1E6A9A"], 70,
                   ticks=["#FFFFFF", "#D8F4F8"]))
    out.append(f'<path d="{blob(450, 464, 120, 8, 157, 0.1, 16)}" fill="#FFF2C0" opacity="0.5"/>')
    for x, y, s in ((180, 520, 1.2), (330, 500, 0.9), (452, 484, 0.7)):
        out.append(f'<path d="M {x} {y} L {x} {y - 34 * s:.1f} L {x + 20 * s:.1f} {y - 4 * s:.1f} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>'
                   f'<path d="M {x - 2} {y - 30 * s:.1f} L {x - 14 * s:.1f} {y - 4 * s:.1f} L {x - 2} {y - 4 * s:.1f} Z" fill="#F6C21C" stroke="{INK}" stroke-width="1"/>'
                   f'<path d="M {x - 18 * s:.1f} {y - 2} L {x + 24 * s:.1f} {y - 2} L {x + 18 * s:.1f} {y + 5 * s:.1f} L {x - 14 * s:.1f} {y + 5 * s:.1f} Z" fill="#1F4FA0"/>'
                   f'<path d="M {x - 22 * s:.1f} {y + 8 * s:.1f} q 20 4 46 0" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.7"/>')
    for x, y, sz in ((300, 250, 8), (324, 238, 6), (200, 262, 7)):
        out.append(bird_v(x, y, sz, "#3A3048", 0.8))
    # palms framing the foreground
    out.append(palm(D, (30, 640), (70, 250), 158, [(-170, 1.0), (-140, 0.9), (-110, 0.8), (-75, 0.85), (-40, 0.95), (-10, 1.0), (-195, 0.8), (20, 0.85)], L=120, width=20))
    out.append(palm(D, (600, 650), (556, 300), 159, [(-170, 1.0), (-140, 0.9), (-110, 0.8), (-75, 0.85), (-200, 0.85), (-30, 0.7)], L=104, width=18))
    # postcard border and stamp corner
    out.append(f'<rect x="22" y="22" width="556" height="556" fill="none" stroke="#FFF8EC" stroke-width="7"/>')
    out.append(f'<rect x="30" y="30" width="540" height="540" fill="none" stroke="#FFF8EC" stroke-width="1.6" opacity="0.8"/>')
    # lettering: "lembranças do" + big BRASIL with a retro drop shade
    out.append(letters(D, 300, 114, "lembranças do", SERIF_IT, 48, "#FFFDF0", ["#FFFFFF", "#F2E2C0"], 160, max_w=330,
                       shadow="#0E2A4A", soff=(0.03, 0.04), angle=-40, rot=-3))
    out.append(letters(D, 300, 222, "BRASIL", ANTON, 104, "#F6C21C", ["#FFE07A", "#D89A10", "#FFF2B0"], 161, ls=12, max_w=420,
                       shadow="#0E3A22", soff=(0.04, 0.05), angle=-75, wob=0.4, hi="#FFFFFF"))
    return finish_b(D, out, 162)


# ================================================================ 12. cafuné — a dictionary card, taped to a sage wall
@design("cafune")
def cafune():
    D = Doc2("cf")
    out = [sky(D, [(0, "#B8CCB0"), (1, "#98B494")], 3, 600, ["#C8DCC0", "#88A884", "#D8E8D0"], 120, angle=-40, sop=(0.06, 0.16))]
    out.append(blooms(170, ["#D8E8D0", "#7E9E7A"], 8, (0, 0, 600, 600), (120, 200), (0.06, 0.12)))
    # tropical leaves peeking from behind the card
    for k, (x, y, a, L_, pal) in enumerate(((560, 40, 120, 190, MATA), (40, 600, -60, 200, VERDE), (600, 560, -140, 170, VERDE), (10, 60, 50, 150, MATA))):
        out.append(banana_leaf(D, x, y, a, L_, 38, 171 + k, pal, bg=None, splits=0))
    out.append(monstera(D, 520, 470, 70, -30, 175, ("#7ACB6A", "#2E8A3A", "#14501E")))
    # the card
    card = rect_pts(78, 92, 522, 512, 30, 176, 0.8)
    out.append('<g transform="rotate(-2.5 300 300)">')
    out.append(f'<path d="{pd([(x + 8, y + 10) for x, y in card])}" fill="#2A3A22" opacity="0.25"/>')
    out.append(painted(D, card, ("#FFFFFA", "#FBF6EA", "#D8CCB0"), 176, sdir=(0.4, 1), sk=0.04, angle=-10, n=50, slen=(30, 90), sw=(2, 5),
                       sop=(0.06, 0.16), inkw=1.4, inkop=0.5, hi=0.2))
    for y in range(206, 500, 38):
        out.append(f'<path d="M 92 {y} L 508 {y}" stroke="#8AB0D8" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<path d="M 92 168 L 508 168" stroke="#E86A6A" stroke-width="2" opacity="0.75"/>')
    # washi tape at the top corners
    for x, a in ((84, -40), (516, 40)):
        t = rot(rect_pts(x - 34, 84, x + 34, 106, 12, x, 0.4), x, 95, a)
        out.append(f'<path d="{smooth_closed(t)}" fill="#F6C21C" opacity="0.8"/>')
        out.append(stripes_in(D, smooth_closed(t), bbox(t), a + 90, [6, 8], ["#FFFFFF", None], x, 0.35))
    out.append(letters(D, 300, 156, "cafuné", SERIF_IT, 112, "#1F6A40", ["#2E8A50", "#0E4A2A"], 177, max_w=310, angle=-40, wob=0.6))
    out.append(label(300, 196, "/ka·fu·NÉ/  (s.m.)", MONO, 20, "#C8603A", ls=2))
    lines = ["carinho de passar", "os dedos no cabelo", "de quem a gente ama"]
    for k, s_ in enumerate(lines):
        out.append(label(300, 256 + k * 38, s_, SERIF_IT, 34, "#3A2418", max_w=380))
    out.append(label(300, 370, "ex.: “vem cá, deixa eu te", JOST, 23, "#5A6A8A", max_w=380))
    out.append(label(300, 406, "fazer um cafuné”", JOST, 23, "#5A6A8A", max_w=380))
    out.append(p_heart(D, 300, 460, 18, ("#FF9A9A", "#E8484A", "#9A1A20"), 178, -4))
    out.append("</g>")
    # a hibiscus tucked at the corner of the card
    out.append(leaf_simple(D, 100, 480, 70, 18, -150, VERDE, 179))
    out.append(leaf_simple(D, 100, 480, 64, 16, 120, MATA, 180))
    out.append(hibiscus(D, 104, 482, 34, ("#FFA8C0", "#E8507A", "#A82450"), 181, 20, inkw=1.4))
    return finish_b(D, out, 182)


# ================================================================ 13. feijoada de sábado — the Saturday table, from above
def bowl_top(D, cx, cy, r, seed, glaze=WHITE, rim=None, inside=None):
    """Round bowl seen from above: glazed rim ring, inner wall shading. Returns (svg, inner_radius)."""
    out = [cast(D, cx + r * 0.12, cy + r * 0.14, r * 1.04, r * 1.02, strength=0.35, seed=seed)]
    outer = blob_pts(cx, cy, r, r, seed, 0.012, 28)
    out.append(painted(D, outer, glaze, seed, sdir=(0.6, 0.7), sk=0.12, angle=-30, n=int(r * 0.6), inkw=1.8, hi=0.45))
    if rim:
        out.append(ink(blob(cx, cy, r * 0.9, r * 0.9, seed + 1, 0.01, 24), rim, max(2, r * 0.05), seed, 1, 0.85))
    ri = r * 0.8
    inner = blob(cx, cy, ri, ri, seed + 2, 0.01, 24)
    out.append(f'<path d="{inner}" fill="{inside or dk(glaze[1], 0.08)}"/>')
    g = D.rad([(0, "#000000", 0), (0.7, "#000000", 0.05), (1, "#000000", 0.28)], 0.42, 0.4, 0.62)
    out.append(f'<path d="{inner}" fill="{g}"/>')
    return "".join(out), ri


def beans(D, cx, cy, r, seed, n=None):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.01, 24)
    out = [f'<path d="{d}" fill="#2A161A"/>']
    cid = D.clip(f'<path d="{d}"/>')
    b = []
    for _ in range(n or int(r * r / 22)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        t = rnd.uniform(0, 180)
        c = rnd.choice(["#3A1E24", "#4A2630", "#2A1418", "#5A3038"])
        b.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="4.6" ry="3" transform="rotate({t:.0f} {x:.1f} {y:.1f})" fill="{c}"/>')
        if rnd.random() < 0.5:
            b.append(f'<ellipse cx="{x - 1.2:.1f}" cy="{y - 1:.1f}" rx="1.8" ry="0.9" transform="rotate({t:.0f} {x:.1f} {y:.1f})" fill="#B88A98" opacity="0.7"/>')
    b.append(f'<path d="{d}" fill="{D.rad([(0, "#5A2A1A", 0.25), (1, "#000000", 0.45)], 0.4, 0.4, 0.6)}"/>')
    out.append(f'<g {cid}>{"".join(b)}</g>')
    return "".join(out)


def sausage_slice(D, x, y, r, seed):
    rnd = random.Random(seed)
    out = [painted(D, blob_pts(x, y, r, r * 0.92, seed, 0.06, 12), ("#E8907A", "#B8503A", "#6A2014"), seed, sk=0.25, n=6, inkw=1.2, hi=0.3)]
    out.append(f'<path d="{blob(x, y, r * 0.72, r * 0.66, seed + 1, 0.08, 10)}" fill="#D8806A"/>')
    for _ in range(6):
        out.append(f'<circle cx="{x + rnd.uniform(-r * 0.5, r * 0.5):.1f}" cy="{y + rnd.uniform(-r * 0.5, r * 0.5):.1f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFE8D8" opacity="0.85"/>')
    return "".join(out)


def rice(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.04, 20)
    out = [f'<path d="{d}" fill="#F6F2E8"/>']
    cid = D.clip(f'<path d="{d}"/>')
    g = []
    for _ in range(int(r * r / 9)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        t = rnd.uniform(0, 180)
        g.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.4" ry="1.5" transform="rotate({t:.0f} {x:.1f} {y:.1f})" fill="{rnd.choice(["#FFFFFF", "#E8E0D0", "#FFFDF6"])}" stroke="#C8BCA8" stroke-width="0.5"/>')
    g.append(f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0.2), (1, "#8A7A60", 0.35)], 0.4, 0.4, 0.6)}"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    return "".join(out)


def farofa(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.05, 20)
    out = [f'<path d="{d}" fill="#E8B868"/>']
    cid = D.clip(f'<path d="{d}"/>')
    g = [specks(seed, (cx - r, cy - r, cx + r, cy + r), ["#F6D290", "#C8883A", "#FFF0C0", "#A8682A"], int(r * r / 3), (0.8, 2.2), (0.5, 1))]
    for _ in range(8):
        x, y = cx + rnd.uniform(-r * 0.6, r * 0.6), cy + rnd.uniform(-r * 0.6, r * 0.6)
        g.append(f'<path d="{blob(x, y, 4, 3, rnd.randint(1, 999), 0.2, 8)}" fill="#9A3A1E"/>')
    for _ in range(6):
        x, y = cx + rnd.uniform(-r * 0.6, r * 0.6), cy + rnd.uniform(-r * 0.6, r * 0.6)
        g.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#4A8A3A" stroke-width="2.6" stroke-linecap="round"/>')
    g.append(f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0.15), (1, "#5A3010", 0.35)], 0.4, 0.4, 0.6)}"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    return "".join(out)


def couve(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.06, 20)
    out = [f'<path d="{d}" fill="#2E6A2A"/>']
    cid = D.clip(f'<path d="{d}"/>')
    g = []
    for _ in range(int(r * 2.4)):
        x, y = cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r)
        t = rnd.uniform(0, 6.28)
        L = rnd.uniform(8, 18)
        g.append(taper([(x, y), (x + math.cos(t) * L * 0.5 + rnd.uniform(-3, 3), y + math.sin(t) * L * 0.5 + rnd.uniform(-3, 3)), (x + math.cos(t) * L, y + math.sin(t) * L)],
                       2.6, 1.6, rnd.choice(["#4E9A3A", "#7AC050", "#1E4E1E", "#3E8A34"]), 0.95))
    for _ in range(10):
        g.append(f'<circle cx="{cx + rnd.uniform(-r * 0.7, r * 0.7):.1f}" cy="{cy + rnd.uniform(-r * 0.7, r * 0.7):.1f}" r="1.6" fill="#FFF0C0"/>')
    g.append(f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0.1), (1, "#000000", 0.35)], 0.4, 0.4, 0.6)}"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    return "".join(out)


def orange_slice(D, cx, cy, r, seed, rot_=0, half=False):
    out = [painted(D, blob_pts(cx, cy, r, r, seed, 0.02, 20), ("#FFC060", "#F28A1E", "#B0500A"), seed, sk=0.1, n=8, inkw=1.4, hi=0.3)]
    out.append(f'<path d="{blob(cx, cy, r * 0.86, r * 0.86, seed + 1, 0.02, 20)}" fill="#FFF2D8"/>')
    for i in range(9):
        a0 = math.radians(rot_ + i * 40 + 3)
        a1 = math.radians(rot_ + (i + 1) * 40 - 3)
        seg = [(cx + math.cos(a0) * r * 0.12, cy + math.sin(a0) * r * 0.12), (cx + math.cos(a0) * r * 0.78, cy + math.sin(a0) * r * 0.78),
               (cx + math.cos((a0 + a1) / 2) * r * 0.82, cy + math.sin((a0 + a1) / 2) * r * 0.82), (cx + math.cos(a1) * r * 0.78, cy + math.sin(a1) * r * 0.78)]
        out.append(f'<path d="{smooth_closed(seg)}" fill="#FFA83A"/>')
        out.append(f'<path d="{smooth_closed([(x * 0.55 + cx * 0.45, y * 0.55 + cy * 0.45) for x, y in seg])}" fill="#FFD27A" opacity="0.7"/>')
    return "".join(out)


@design("feijoada-de-sabado")
def feijoada_de_sabado():
    D = Doc2("fj")
    out = [f'<rect width="600" height="600" fill="#8A5A34"/>', wood_planks(D, 0, 600, 190, ("#B8804E", "#8A5A30", "#4E2E14"), 5, vertical=True)]
    out.append(soft_glow(D, 300, 300, 360, "#FFE2A8", 0.3))
    out.append('<g transform="translate(0 18)">')
    # round woven straw placemat under the pot
    out.append(cast(D, 308, 392, 196, 192, strength=0.3, seed=191))
    out.append(f'<path d="{blob(300, 382, 190, 188, 191, 0.01, 36)}" fill="#D8B070"/>')
    for k in range(17):
        r_ = 186 - k * 11
        out.append(f'<path d="{blob(300, 382, r_, r_ - 1, 192 + k, 0.006, 40)}" fill="none" stroke="{"#B88A48" if k % 2 else "#EAC888"}" stroke-width="6" opacity="0.9"/>')
        out.append(f'<path d="{blob(300, 382, r_, r_ - 1, 192 + k, 0.006, 40)}" fill="none" stroke="#7A5420" stroke-width="1" stroke-dasharray="4 7" opacity="0.6"/>')
    out.append(ink(blob(300, 382, 190, 188, 191, 0.01, 36), "#6A4418", 2, 191, 1, 0.7))
    # clay pot of feijoada with a wooden ladle
    cx, cy = 300, 382
    out.append(cast(D, cx + 16, cy + 20, 150, 138, strength=0.5, seed=193))
    for sg in (-1, 1):
        ear = blob_pts(cx + sg * 146, cy, 26, 18, 194 + sg, 0.08, 12)
        out.append(painted(D, ear, ("#C8724A", "#8A3E1E", "#4A1A0A"), 194 + sg, sk=0.2, n=6, inkw=1.6, hi=0.3))
    pot = blob_pts(cx, cy, 136, 134, 195, 0.012, 30)
    out.append(painted(D, pot, ("#C8724A", "#8A3E1E", "#4A1A0A"), 195, sdir=(0.6, 0.7), sk=0.12, angle=-30, n=70, inkw=2.2, hi=0.4))
    out.append(beans(D, cx, cy, 112, 196))
    rnd = random.Random(197)
    for k in range(9):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(20, 90)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        if x > cx + 10 and y < cy:
            continue
        out.append(sausage_slice(D, x, y, rnd.uniform(9, 13), 198 + k))
    for k, (x, y) in enumerate(((cx - 52, cy + 44), (cx + 30, cy + 66), (cx - 70, cy - 26))):
        pts = rot([(x - 16, y - 8), (x + 16, y - 10), (x + 18, y + 8), (x - 14, y + 10)], x, y, k * 40)
        out.append(painted(D, pts, ("#E8A890", "#B8604A", "#6A2A1A"), 210 + k, sk=0.2, n=6, inkw=1.2, hi=0.3))
        out.append(taper(rot([(x - 14, y - 4), (x + 14, y - 5)], x, y, k * 40), 3, 2, "#FFE8D8", 0.85))
    for k in range(3):
        out.append(f'<path d="{blob(cx - 20 + k * 30, cy + 10 + (k % 2) * 30, 6, 4, 220 + k, 0.2, 8)}" fill="#FFFFFF" opacity="0.18"/>')
    out.append(taper([(cx + 50, cy - 40), (cx + 110, cy - 110), (cx + 172, cy - 172)], 14, 10, "#C8905A"))
    out.append(taper([(cx + 50, cy - 40), (cx + 120, cy - 120), (cx + 200, cy - 200)], 4, 3, "#F2C890", 0.7))
    out.append(painted(D, blob_pts(cx + 40, cy - 30, 30, 22, 221, 0.05, 14, -45), ("#E8B880", "#B8844A", "#6E4420"), 221, sk=0.2, n=8, inkw=1.6, hi=0.4))
    out.append(steam(cx - 30, cy - 70, 70, 222, "#FFFFFF", 3, 30, 7, 0.5))
    # rice, farofa, couve, orange slices around the pot
    s1, ri = bowl_top(D, 104, 296, 64, 223, WHITE, rim="#1F4FA0")
    out.append(s1 + rice(D, 104, 296, ri, 224))
    s2, ri2 = bowl_top(D, 500, 312, 62, 225, ("#E8A878", "#C0784A", "#7A4220"))
    out.append(s2 + farofa(D, 500, 312, ri2, 226))
    s3, ri3 = bowl_top(D, 126, 506, 60, 227, WHITE, rim="#1F8A4C")
    out.append(s3 + couve(D, 126, 506, ri3, 228))
    out.append(cast(D, 488, 516, 70, 58, strength=0.35, seed=229))
    out.append(painted(D, blob_pts(480, 508, 66, 56, 230, 0.03, 20), WHITE, 230, sk=0.12, n=12, inkw=1.6, hi=0.4))
    out.append(orange_slice(D, 462, 498, 28, 231, 10) + orange_slice(D, 506, 520, 26, 232, 30) + orange_slice(D, 500, 484, 22, 233, 50))
    # lettering
    out.append("</g>")
    out.append(letters(D, 300, 146, "feijoada", SERIF_IT, 116, "#FFF4DC", ["#FFFFFF", "#F2DCB8", "#FFE8C8"], 234, max_w=420,
                       shadow="#2A1206", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 194, "DE SÁBADO", "#F6C21C", font=JOS, size=26, ls=10, line_w=40, gap=14, line="#FFF4DC"))
    return finish_b(D, out, 235)


# ================================================================ 14. açaí na tigela — the bowl, from above, on a beach-kiosk table
def pinnate_frond(D, x, y, ang, L, seed, pals=(VERDE, MATA), droop=0.25, leaflet=0.32, n=22, shadow=False):
    """A feathery palm frond (açaí / coconut) seen from above: curved rachis with many narrow leaflets."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    spine = [(x + ux * L * t + nx * droop * L * t * t, y + uy * L * t + ny * droop * L * t * t) for t in [i / 20 for i in range(21)]]
    out = []
    for i in range(2, n):
        t = i / n
        k = int(t * 20)
        px, py = spine[k]
        qx, qy = spine[min(20, k + 1)]
        ta = math.atan2(qy - py, qx - px)
        for sg in (-1, 1):
            la = ta + sg * math.radians(rnd.uniform(48, 62))
            ll = L * leaflet * math.sin(math.pi * (0.15 + 0.85 * t)) * rnd.uniform(0.85, 1.1)
            ex, ey = px + math.cos(la) * ll, py + math.sin(la) * ll
            mx, my = (px + ex) / 2 + math.cos(ta) * ll * 0.12, (py + ey) / 2 + math.sin(ta) * ll * 0.12
            pal = rnd.choice(pals)
            col = "#0E3A3A" if shadow else (pal[0] if sg < 0 and rnd.random() < 0.4 else pal[1])
            out.append(taper([(px, py), (mx, my), (ex, ey)], max(3, ll * 0.14), 0.8, col, 0.95))
            if not shadow:
                out.append(taper([(px, py), (mx, my), (ex, ey)], 1, 0.5, pal[2], 0.6))
    out.append(taper(spine, 7, 2, "#0E3A3A" if shadow else "#C8B870"))
    return "".join(out)


def acai_berries(D, cx, cy, seed, n=26, spread=46):
    """A bunch of açaí berries on their branching stalks."""
    rnd = random.Random(seed)
    out = []
    stems = []
    for k in range(5):
        a = math.radians(-160 + k * 30 + rnd.uniform(-8, 8))
        ex, ey = cx + math.cos(a) * spread * 1.3, cy + math.sin(a) * spread * 0.9 + 30
        stems.append((ex, ey))
        out.append(taper([(cx, cy - 20), ((cx + ex) / 2, (cy + ey) / 2 - 10), (ex, ey)], 3.4, 1.4, "#B8783A"))
    pts = []
    for _ in range(n):
        sx, sy = rnd.choice(stems)
        t = rnd.uniform(0.4, 1.0)
        pts.append((cx + (sx - cx) * t + rnd.uniform(-8, 8), cy - 20 + (sy - cy + 20) * t + rnd.uniform(-8, 8)))
    for x, y in sorted(pts, key=lambda p: p[1]):
        r = rnd.uniform(8.5, 10.5)
        out.append(f'<circle cx="{x + 2:.1f}" cy="{y + 3:.1f}" r="{r:.1f}" fill="#0E2A2A" opacity="0.3"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#3A1446"/>')
        out.append(f'<circle cx="{x + r * 0.2:.1f}" cy="{y + r * 0.2:.1f}" r="{r * 0.75:.1f}" fill="#1E0828"/>')
        out.append(f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.25:.1f}" fill="#C8A8E0" opacity="0.8"/>')
    return "".join(out)


@design("acai-na-tigela")
def acai_na_tigela():
    D = Doc2("ac")
    out = [sky(D, [(0, "#8EE0D8"), (1, "#4EC0C0")], 3, 600, ["#B8F0E8", "#2EA8A8", "#D8FFF8"], 100, angle=-40, sop=(0.08, 0.18))]
    # leaf shadows and leaves around the edge
    fronds = ((630, 290, -160, 210), (-30, 96, 22, 196), (-30, 600, -40, 200), (630, 640, -128, 240))
    for k, (x, y, a, L_) in enumerate(fronds):
        out.append(f'<g opacity="0.16" transform="translate(18 20)">{pinnate_frond(D, x, y, a, L_, 240 + k, shadow=True)}</g>')
    for k, (x, y, a, L_) in enumerate(fronds):
        out.append(pinnate_frond(D, x, y, a, L_, 240 + k, pals=(VERDE, MATA, ("#9ACB6A", "#5E9A3A", "#2E5A1E"))))
    out.append(acai_berries(D, 108, 470, 247, n=28, spread=46))
    # the bowl (coconut shell)
    cx, cy, R = 300, 382, 156
    out.append(cast(D, cx + 18, cy + 22, R + 6, R, strength=0.45, seed=249, color="#0E3A3A"))
    shell = blob_pts(cx, cy, R, R * 0.98, 250, 0.015, 30)
    out.append(painted(D, shell, ("#C8905A", "#8A5A30", "#4A2A12"), 250, sdir=(0.6, 0.7), sk=0.14, angle=-60, n=120, slen=(10, 30), sw=(1, 2.4),
                       cols=["#B07A44", "#5A3416", "#D8A070", "#7A4A22"], inkw=2.2, hi=0.4))
    out.append(f'<path d="{blob(cx, cy, R - 12, R - 12, 251, 0.01, 30)}" fill="#F2E8D2"/>')
    ac = blob(cx, cy, R - 20, R - 20, 252, 0.03, 26)
    out.append(f'<path d="{ac}" fill="#4A1A4A"/>')
    cid = D.clip(f'<path d="{ac}"/>')
    rnd = random.Random(253)
    a_ = [strokes(D.nid(), ac, (cx - R, cy - R, cx + R, cy + R), ["#6A2A6A", "#2E0E30", "#8A4A8A", "#5A2058"], 253, n=160, angle=-20, length=(10, 30), width=(2, 5), opacity=(0.3, 0.6), curve=0.6)]
    a_.append(f'<path d="{ac}" fill="{D.rad([(0, "#FFFFFF", 0.08), (1, "#100010", 0.45)], 0.4, 0.4, 0.62)}"/>')
    out.append(f'<g {cid}>{"".join(a_)}</g>')
    # granola heap (left)
    for _ in range(70):
        a, rr = rnd.uniform(1.6, 4.2), rnd.uniform(20, 112)
        x, y = cx + math.cos(a) * rr * 0.9, cy + math.sin(a) * rr * 0.7 + 10
        if math.hypot(x - cx, y - cy) > R - 26:
            continue
        out.append(f'<path d="{blob(x, y, rnd.uniform(4, 8), rnd.uniform(3, 6), rnd.randint(1, 9999), 0.25, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#D8A050", "#B8782E", "#E8C078", "#9A5A22"])}" stroke="#6A3A12" stroke-width="0.8"/>')
    # banana rounds (top arc)
    for k, a in enumerate(range(-150, -20, 26)):
        x, y = cx + math.cos(math.radians(a)) * 86, cy + math.sin(math.radians(a)) * 86
        out.append(painted(D, blob_pts(x, y, 19, 18, 260 + k, 0.04, 14), ("#FFFBE0", "#F6E8A8", "#C8B060"), 260 + k, sk=0.15, n=4, inkw=1.2, hi=0.4))
        out.append(f'<path d="{blob(x, y, 7, 6, 270 + k, 0.1, 8)}" fill="#E8D488" opacity="0.8"/>')
        for j in range(3):
            aa = math.radians(j * 120 + k * 20)
            out.append(f'<circle cx="{x + math.cos(aa) * 3:.1f}" cy="{y + math.sin(aa) * 3:.1f}" r="1.1" fill="#7A6A3A"/>')
    # strawberry halves (right)
    for k, (dx, dy, a) in enumerate(((66, 26, 20), (102, -14, -24), (40, 78, 64), (96, 60, 8))):
        x, y = cx + dx, cy + dy
        S = 1.35
        pts = rot([(x, y - 22 * S), (x + 17 * S, y - 9 * S), (x + 14 * S, y + 10 * S), (x, y + 19 * S), (x - 14 * S, y + 10 * S), (x - 17 * S, y - 9 * S)], x, y, a)
        out.append(painted(D, pts, ("#FF8A8A", "#E8283A", "#8A0A1A"), 280 + k, sk=0.2, n=6, inkw=1.4, hi=0.3))
        inner = rot([(x, y - 15 * S), (x + 11 * S, y - 5 * S), (x + 9 * S, y + 8 * S), (x, y + 13 * S), (x - 9 * S, y + 8 * S), (x - 11 * S, y - 5 * S)], x, y, a)
        out.append(f'<path d="{smooth_closed(inner)}" fill="#FFD8D0"/>')
        core = rot([(x, y - 8 * S), (x + 4 * S, y), (x, y + 9 * S), (x - 4 * S, y)], x, y, a)
        out.append(f'<path d="{smooth_closed(core)}" fill="#FFFFFF" opacity="0.9"/>')
        for j in range(7):
            px, py = rot([(x + rnd.uniform(-9, 9) * S, y + rnd.uniform(-10, 9) * S)], x, y, a)[0]
            out.append(f'<path d="M {px:.1f} {py:.1f} l 2 3" stroke="#F04A5A" stroke-width="1.4" stroke-linecap="round" opacity="0.7"/>')
        lp = rot([(x - 9 * S, y - 22 * S), (x, y - 31 * S), (x + 9 * S, y - 22 * S), (x, y - 19 * S)], x, y, a)
        out.append(f'<path d="{smooth_closed(lp)}" fill="#3E8A3A"/>')
    # a dusting of coconut flakes
    for _ in range(26):
        a_, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 120
        x, y = cx + math.cos(a_) * rr, cy + math.sin(a_) * rr
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#FFFDF4" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>')
    # honey drizzle in loose loops
    hz = [(cx - 84 + 150 * t + 16 * math.cos(9 * math.pi * t), cy - 18 + 40 * t + 14 * math.sin(9 * math.pi * t)) for t in [i / 120 for i in range(121)]]
    out.append(taper([(x + 1.5, y + 2) for x, y in hz], 5, 3, "#5A2A08", 0.35))
    out.append(taper(hz, 5, 3, "#E8A020", 0.95))
    out.append(taper([(x - 1, y - 1) for x, y in hz], 1.6, 1, "#FFF0B0", 0.9))
    out.append(leaf_simple(D, cx - 6, cy + 4, 34, 11, -60, VERDE, 290))
    out.append(leaf_simple(D, cx - 6, cy + 4, 30, 10, 200, VERDE, 291))
    # spoon resting on the rim
    out.append(taper([(cx + 110, cy + 120), (cx + 170, cy + 170), (cx + 230, cy + 220)], 12, 9, "#E8B87A"))
    out.append(painted(D, blob_pts(cx + 90, cy + 100, 24, 15, 292, 0.04, 14, 42), ("#F2D0A0", "#D8A870", "#8A5A2E"), 292, sk=0.2, n=6, inkw=1.4, hi=0.4))
    # lettering
    out.append(letters(D, 300, 166, "açaí", SERIF_IT, 132, "#4A1A5A", ["#6A2A7A", "#2E0A3A", "#8A4A9A"], 293, max_w=300,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#C8A0E0"))
    out.append(ruled(300, 214, "NA TIGELA", "#FFFFFF", font=JOS, size=26, ls=10, line_w=40, gap=14))
    return finish_b(D, out, 294)


# ================================================================ 15. coxinha — paixão nacional, one already bitten
def coxinha(D, cx, base, h, seed, bite=False, lean=0):
    """Coxinha: drumstick-shaped croquette (round bottom, tapering to a soft point), crunchy golden crumb,
    a cast shadow; optionally bitten to show the creamy shredded-chicken filling."""
    from summer_gouache import bite_out
    w = h * 0.8
    pts = []
    for i in range(48):
        t = i / 48 * 2 * math.pi
        x = math.sin(t) * abs(math.sin(t / 2)) ** 1.15 * (w / 2) * 1.0
        y = math.cos(t)      # 1 at the tip (t=0), -1 at the bottom
        pts.append((cx + x, base - h * 0.5 - y * h * 0.5))
    pts = [(x, min(y, base - 4 + (y - base + 4) * 0.25)) for x, y in pts]
    pts = rot(pts, cx, base, lean)
    out = [cast(D, cx + w * 0.12, base + 2, w * 0.62, 9, strength=0.45, seed=seed)]
    full = smooth_closed(pts)
    if bite:
        bx, by = rot([(cx + w * 0.34, base - h * 0.58)], cx, base, lean)[0]
        br = w * 0.3
        pts = bite_out(pts, bx, by, br, 12)
    pal = ("#F6C478", "#D8883A", "#8A4612")
    out.append(painted(D, pts, pal, seed, sdir=(0.7, 0.5), sk=0.18, angle=-80, n=40, cols=["#FFD898", "#B86A22", "#E8A050", "#9A5214"],
                       inkw=0, hi=0.45, hik=0.1))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    cr = []
    x0, y0, x1, y1 = bbox(pts)
    for _ in range(int(w * h / 24)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        lit = -(x - cx) / w - (y - (base - h / 2)) / h
        c = rnd.choice(["#FFE2A8", "#F6C478"]) if lit > 0.2 else rnd.choice(["#B8641E", "#8A4612", "#D8883A"])
        cr.append(f'<path d="{blob(x, y, rnd.uniform(1.4, 3.2), rnd.uniform(1.2, 2.6), rnd.randint(1, 9999), 0.3, 6)}" fill="{c}" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    cr.append(taper(rot([(cx - w * 0.2, base - h * 0.62), (cx - w * 0.3, base - h * 0.38), (cx - w * 0.24, base - h * 0.16)], cx, base, lean), max(3, w * 0.06), 1, "#FFF2D0", 0.6))
    if bite:
        # the cut face: a crescent just inside the bite, golden crust rim then creamy filling
        k = 0.42
        fx, fy = bx + (cx - bx) * 0.0 - br * k * (bx - cx) / math.hypot(bx - cx, by - (base - h * 0.45)), by - br * k * (by - (base - h * 0.45)) / math.hypot(bx - cx, by - (base - h * 0.45))
        cr.append(f'<path d="{blob(fx, fy, br * 1.12, br * 1.12, seed + 5, 0.02, 20)}" fill="#E8B060"/>')
        cr.append(f'<path d="{blob(fx, fy, br * 1.04, br * 1.04, seed + 6, 0.03, 20)}" fill="#FFF2D6"/>')
        for _ in range(26):
            a_, rr = rnd.uniform(0, 6.28), rnd.uniform(br * 0.4, br * 1.0)
            x, y = fx + math.cos(a_) * rr, fy + math.sin(a_) * rr
            cr.append(taper([(x, y), (x + rnd.uniform(-7, 7), y + rnd.uniform(-5, 5))], 3.2, 1, rnd.choice(["#F2D080", "#E8B860", "#FFE8A8", "#D89A50"]), 0.95))
        cr.append(f'<path d="{blob(fx - br * 0.2, fy + br * 0.35, br * 0.3, br * 0.18, seed + 4, 0.2, 8)}" fill="#FFFFFF" opacity="0.95"/>')
        cr.append(f'<path d="{blob(fx - br * 0.2, fy + br * 0.35, br * 0.3, br * 0.18, seed + 4, 0.2, 8)}" fill="none" stroke="#E8D8B8" stroke-width="1.2"/>')
    out.append(f'<g {cid}>{"".join(cr)}</g>')
    out.append(ink(d, "#7A3A0E", 2, seed + 2, 2, 0.75))
    return "".join(out)


@design("coxinha")
def coxinha_d():
    D = Doc2("cx")
    out = [f'<rect width="600" height="600" fill="#F6C23A"/>']
    for i in range(24):
        a = math.radians(i * 15)
        out.append(f'<path d="M 300 360 L {300 + 700 * math.cos(a - 0.065):.1f} {360 + 700 * math.sin(a - 0.065):.1f} L {300 + 700 * math.cos(a + 0.065):.1f} {360 + 700 * math.sin(a + 0.065):.1f} Z" fill="{"#FFD866" if i % 2 else "#F2B020"}"/>')
    out.append(blooms(300, ["#FFE89A", "#E8A010"], 8, (0, 0, 600, 600), (100, 200), (0.1, 0.2)))
    out.append(soft_glow(D, 300, 380, 230, "#FFF6D0", 0.6))
    # a red-and-white paper tray on the counter
    out.append(f'<path d="{hg.org_rect(-10, 500, 620, 110, 301, 0.6, 14, 1)}" fill="#C8382E"/>')
    out.append(stripes_in(D, pd([(-10, 500), (610, 500), (610, 610), (-10, 610)]), (-10, 500, 610, 610), 0, [30, 30], ["#FFFFFF", None], 302, 0.9))
    out.append(f'<rect y="498" width="600" height="6" fill="#7A1A12" opacity="0.5"/>')
    tray = [(92, 512), (508, 512), (540, 470), (60, 470)]
    out.append(painted(D, poly_pts(tray, 20, 303, 0.6), ("#FFFFFF", "#F6F0E6", "#C8B8A8"), 303, sdir=(0, 1), sk=0.15, angle=0, n=20, inkw=1.8, hi=0.3))
    for x in range(80, 540, 16):
        out.append(f'<path d="M {x} 474 L {x + 8} 508" stroke="#E8DCC8" stroke-width="1.2"/>')
    # three coxinhas (one bitten) and a little dish of pimenta
    out.append(coxinha(D, 178, 494, 190, 304, lean=-8))
    out.append(coxinha(D, 422, 494, 190, 305, lean=9))
    out.append(coxinha(D, 300, 506, 220, 306, bite=True, lean=-2))
    out.append(cast(D, 520, 520, 44, 8, strength=0.4, seed=307))
    out.append(painted(D, ell_pts(510, 504, 40, 14, 0, 360, 20), WHITE, 307, sk=0.15, n=6, inkw=1.4, hi=0.4))
    out.append(f'<path d="{blob(510, 502, 30, 8, 308, 0.05, 14)}" fill="#D82A1E"/>')
    out.append(specks(309, (484, 496, 536, 508), ["#FFE07A", "#8A0A0A"], 12, (0.8, 1.6), (0.7, 1)))
    out.append(steam(300, 262, 34, 310, "#FFFFFF", 3, 30, 6, 0.6))
    # lettering
    out.append(letters(D, 300, 160, "coxinha", SERIF_IT, 136, "#C8282E", ["#E8484A", "#8A1014", "#F06A5A"], 311, max_w=430,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB0A0"))
    out.append(ruled(300, 206, "PAIXÃO NACIONAL", "#7A2A10", font=JOS, size=26, ls=8, line_w=36, gap=14))
    return finish_b(D, out, 312)


# ================================================================ 16. churrasco com a família — the grill, the skewers, the caramelo
def skewer(D, x0, y0, x1, y1, items, seed, handle="#7A4A22"):
    """Espeto: steel rod with a wooden handle at the left and meat threaded along it."""
    out = [taper([(x0 - 60, y0), (x1 + 20, y1)], 3.4, 3.0, "#8A8A94"), taper([(x0 - 60, y0 - 1), (x1 + 20, y1 - 1)], 1.2, 1.0, "#E8E8F0", 0.8)]
    out.append(painted(D, rect_pts(x0 - 104, y0 - 7, x0 - 54, y0 + 7, 10, seed, 0.4), WOOD, seed, sdir=(0, 1), sk=0.2, angle=0, n=6, inkw=1.4, hi=0.4))
    rnd = random.Random(seed)
    n = len(items)
    for i, kind in enumerate(items):
        t = (i + 0.5) / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if kind == "picanha":
            # a thick slice folded into a C on the skewer, fat cap arching over the top
            # a thick slice folded into a C on the skewer: side view of the arch, fat cap riding on the outside
            p = [(x - 34, y + 16), (x - 36, y - 6), (x - 26, y - 26), (x, y - 34), (x + 26, y - 26), (x + 36, y - 6), (x + 34, y + 16), (x + 18, y + 22), (x, y + 18), (x - 18, y + 22)]
            out.append(painted(D, jitter(p, seed + i, 1.2), ("#C86A50", "#8A3424", "#3E120A"), seed + i, sdir=(0.4, 1), sk=0.22, angle=-60, n=16, inkw=1.4, hi=0.25))
            cap = [(x - 36, y - 2), (x - 30, y - 24), (x, y - 38), (x + 30, y - 24), (x + 36, y - 2), (x + 31, y - 6), (x + 24, y - 21), (x, y - 30), (x - 24, y - 21), (x - 31, y - 6)]
            out.append(painted(D, cap, ("#FFF4D8", "#EED4A0", "#B88A50"), seed + i + 50, sdir=(0.3, 1), sk=0.15, angle=0, n=6, inkw=1.2, hi=0.3))
            for k in range(4):
                bx_, by_ = x - 24 + k * 16, y - 30 + abs(k - 1.5) * 6
                out.append(f'<path d="{blob(bx_, by_, 3, 2, seed + k, 0.2, 6)}" fill="#7A3A10" opacity="0.7"/>')
            out.append(f'<path d="{blob(x, y - 4, 16, 9, seed + i, 0.15, 10)}" fill="#D87A60" opacity="0.55"/>')
            for k in range(3):
                out.append(f'<path d="M {x - 18 + k * 14} {y - 10} l 9 16" stroke="#2A0A04" stroke-width="2.6" opacity="0.55" stroke-linecap="round"/>')
        elif kind == "linguica":
            p = blob_pts(x, y, 22, 13, seed + i, 0.05, 14)
            out.append(painted(D, p, ("#E89A6A", "#B0502A", "#5A1E0A"), seed + i, sdir=(0.5, 1), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
            for k in range(2):
                out.append(f'<path d="M {x - 10 + k * 14} {y - 10} l 6 18" stroke="#3A0E04" stroke-width="2.2" opacity="0.6" stroke-linecap="round"/>')
        elif kind == "pao":
            p = blob_pts(x, y, 20, 15, seed + i, 0.04, 14)
            out.append(painted(D, p, ("#FFE2A0", "#E8B058", "#9A6A22"), seed + i, sdir=(0.5, 1), sk=0.15, angle=0, n=8, inkw=1.4, hi=0.4))
            out.append(taper([(x - 10, y - 4), (x + 12, y - 6)], 5, 3, "#FFF6C8", 0.9))
            out.append(specks(seed + i, (x - 12, y - 8, x + 12, y + 6), ["#3E8A2E", "#5AAA3A"], 8, (0.8, 1.6), (0.8, 1)))
        elif kind == "coracao":
            for k in range(2):
                p = blob_pts(x - 8 + k * 16, y, 9, 11, seed + i + k, 0.08, 10)
                out.append(painted(D, p, ("#B85A5A", "#7A2A2A", "#3A0E0E"), seed + i + k, sk=0.2, n=4, inkw=1.2, hi=0.4))
        elif kind == "frango":
            p = blob_pts(x, y, 19, 16, seed + i, 0.1, 12)
            out.append(painted(D, p, ("#F2C080", "#C8843A", "#7A4612"), seed + i, sk=0.2, n=8, inkw=1.4, hi=0.4))
    return "".join(out)


def caramelo(D, cx, cy, s, seed):
    """Vira-lata caramelo peeking up from the bottom edge: head, perky-floppy ears, tongue out, hopeful eyes."""
    def L(pts):
        return [(cx + x * s, cy + y * s) for x, y in pts]
    pal = ("#F2B060", "#C8782E", "#7A4214")
    out = []
    body = L([(-60, 120), (-54, 30), (-30, 0), (30, 0), (54, 30), (60, 120)])
    out.append(painted(D, body, pal, seed, sdir=(0.7, 0.4), sk=0.18, angle=-80, n=24, inkw=2, hi=0.35))
    out.append(f'<path d="{smooth_closed(L([(-24, 10), (24, 10), (18, 70), (-18, 70)]))}" fill="#FFF0D8" opacity="0.85"/>')
    for sg in (-1, 1):
        ear = L([(sg * 34, -70), (sg * 66, -96), (sg * 74, -60), (sg * 56, -40)])
        out.append(painted(D, ear, ("#D8904A", "#A85A1E", "#5A2A08"), seed + sg, sdir=(0.5, 0.5), sk=0.2, angle=-60, n=8, inkw=1.8, hi=0.3))
    head = L([(-52, -40), (-40, -76), (0, -88), (40, -76), (52, -40), (40, -6), (0, 6), (-40, -6)])
    out.append(painted(D, head, pal, seed + 2, sdir=(0.7, 0.4), sk=0.15, angle=-60, n=30, inkw=2, hi=0.4))
    muzzle = L([(-26, -24), (0, -36), (26, -24), (22, 0), (0, 8), (-22, 0)])
    out.append(painted(D, muzzle, ("#FFFAF0", "#FFF0D8", "#D8B890"), seed + 3, sk=0.12, n=8, inkw=1.4, hi=0.3))
    nx, ny = L([(0, -26)])[0]
    out.append(f'<path d="{blob(nx, ny, 10 * s, 7 * s, seed, 0.1, 10)}" fill="#2A1810"/><ellipse cx="{nx - 3 * s:.1f}" cy="{ny - 2.5 * s:.1f}" rx="{3 * s:.1f}" ry="{1.6 * s:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(pline(L([(0, -19), (0, -10), (-10, -4)]), "#2A1810", 2 * s, seed, 1, 1) + pline(L([(0, -10), (10, -4)]), "#2A1810", 2 * s, seed + 1, 1, 1))
    out.append(painted(D, L([(-8, -4), (8, -4), (9, 14), (0, 20), (-9, 14)]), ("#FF9AA8", "#E85A70", "#A02A40"), seed + 4, sk=0.15, n=4, inkw=1.4, hi=0.4))
    for sg in (-1, 1):
        ex, ey = L([(sg * 20, -52)])[0]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{7.5 * s:.1f}" fill="#2A1810"/><circle cx="{ex + 2 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{2.6 * s:.1f}" fill="#FFFFFF"/>'
                   f'<circle cx="{ex - 2.5 * s:.1f}" cy="{ey + 2.5 * s:.1f}" r="{1.2 * s:.1f}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(pline(L([(sg * 12, -66), (sg * 22, -70), (sg * 30, -66)]), "#7A4214", 2 * s, seed + sg, 0.8, 1))
    return "".join(out)


@design("churrasco-com-a-familia")
def churrasco():
    D = Doc2("ch")
    out = [sky(D, [(0, "#F2A86A"), (0.5, "#FAD08A"), (1, "#FCE6B8")], 3, 600, ["#FFFFFF", "#F8C080", "#FCE6B0"], 70)]
    out.append(soft_glow(D, 300, 420, 300, "#FFB060", 0.45))
    # string of lights across the top
    pts = [(-10, 210 + 40 * math.sin(math.pi * i / 20) * 1.0 - 0) for i in range(21)]
    cord = [(-10 + i * 31, 214 + 46 * math.sin(math.pi * i / 20)) for i in range(21)]
    out.append(ink(smooth_open(cord), "#3A2418", 1.8, 320, 1, 0.9))
    for i in range(1, 20, 2):
        x, y = cord[i]
        out.append(D.glow(x, y + 10, 22, "#FFE08A", 0.6))
        out.append(f'<path d="{blob(x, y + 10, 6, 8, 321 + i, 0.05, 10)}" fill="#FFF2B8"/><rect x="{x - 3:.1f}" y="{y - 1:.1f}" width="6" height="5" fill="#3A3030"/>')
    # brick barbecue
    brick = rect_pts(40, 290, 560, 640, 30, 322, 1.0)
    bd = smooth_closed(brick)
    out.append(f'<path d="{bd}" fill="#B8583A"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(323)
    bk = []
    for j in range(15):
        y = 290 + j * 22
        off = 0 if j % 2 else 26
        for i in range(-1, 12):
            x = 40 + i * 52 + off
            c = mix("#C8643E", rnd.choice(["#E0805A", "#A8462A", "#D87048", "#B8503A"]), rnd.uniform(0.2, 0.8))
            bk.append(f'<path d="{hg.org_rect(x + 2, y + 2, 48, 18, i * 17 + j, 0.6, 10, 3)}" fill="{c}"/>')
            bk.append(taper([(x + 5, y + 4.5), (x + 46, y + 4 + rnd.uniform(-0.6, 0.6))], 2.4, 1.2, lt(c, 0.35), 0.6))
            bk.append(taper([(x + 4, y + 18.5), (x + 48, y + 18)], 2, 2, dk(c, 0.3), 0.5))
            if rnd.random() < 0.3:
                bk.append(f'<circle cx="{x + rnd.uniform(8, 44):.1f}" cy="{y + rnd.uniform(7, 15):.1f}" r="{rnd.uniform(1, 2):.1f}" fill="{dk(c, 0.35)}" opacity="0.6"/>')
    bk.append(strokes(D.nid(), bd, (40, 290, 560, 640), ["#E8906A", "#8A3A1E", "#F2B08A"], 328, n=160, angle=-4, length=(14, 40), width=(1.4, 3.4), opacity=(0.1, 0.28)))
    bk.append(f'<path d="{blob(300, 330, 250, 40, 329, 0.2, 16)}" fill="#2A1008" opacity="0.28"/>')
    bk.append(shade_over(D, bd, "#2A0A04", 0.35, 0, 0, 0, 1, 0.4))
    out.append(f'<g {cid}><rect x="0" y="280" width="600" height="400" fill="#E8D0B8"/>{"".join(bk)}</g>')
    out.append(ink(bd, INK, 2.2, 324, 2, 0.75))
    # firebox opening with embers
    fb = rect_pts(96, 330, 504, 500, 24, 325, 0.8)
    fbd = smooth_closed(fb)
    out.append(f'<path d="{fbd}" fill="#1E0E0A"/>')
    cid2 = D.clip(f'<path d="{fbd}"/>')
    em = [D.glow(300, 500, 240, "#FF7A1E", 0.75)]
    for _ in range(90):
        x, y = rnd.uniform(100, 500), rnd.uniform(462, 500)
        em.append(f'<path d="{blob(x, y, rnd.uniform(5, 11), rnd.uniform(3, 6), rnd.randint(1, 9999), 0.25, 8)}" fill="{rnd.choice(["#FF8A2A", "#FFC04A", "#C8381E", "#3A1A10", "#FFE08A"])}"/>')
    out.append(f'<g {cid2}>{"".join(em)}</g>')
    out.append(ink(fbd, "#1A0A04", 2, 326, 1, 0.8))
    # top ledge
    out.append(painted(D, rect_pts(26, 278, 574, 300, 20, 327, 0.6), ("#E8D8C0", "#C8B498", "#8A7A60"), 327, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=2, hi=0.4))
    # skewers over the fire
    sk_rows = [(372, ["picanha", "picanha", "picanha"]), (408, ["linguica", "linguica", "linguica", "linguica", "linguica"]),
               (446, ["pao", "coracao", "pao", "coracao", "pao"])]
    for k, (y, items) in enumerate(sk_rows):
        out.append(skewer(D, 176, y, 470, y - 4, items, 330 + k * 10))
    # smoke rising
    for k, x in enumerate((220, 330, 420)):
        sm = catmull([(x, 352), (x - 14, 320), (x + 10, 290), (x - 8, 262), (x + 14, 236)], 6)
        out.append(taper(sm, 14, 4, "#FFFFFF", 0.35))
    # on the ledge: a bowl of vinagrete, a bowl of farofa, a glass of guaraná-ish soda
    out.append(cast(D, 104, 282, 40, 6, strength=0.4, seed=343))
    out.append(painted(D, [(70, 266), (138, 266), (130, 286), (78, 286)], WHITE, 343, sk=0.15, angle=0, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(104, 266, 34, 6, 344, 0.05, 14)}" fill="#E8483A"/>')
    out.append(specks(345, (74, 261, 134, 270), ["#FFFFFF", "#3E8A3A", "#FFE0A0", "#A82A1E"], 22, (1, 2.2), (0.8, 1)))
    out.append(painted(D, [(150, 268), (204, 268), (198, 286), (156, 286)], ("#E8A878", "#C0784A", "#7A4220"), 346, sk=0.15, angle=0, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(177, 268, 26, 5, 347, 0.05, 14)}" fill="#E8B868"/>')
    out.append(specks(348, (154, 263, 200, 271), ["#C8883A", "#FFF0C0"], 14, (0.8, 1.6), (0.8, 1)))
    gl = [(500, 220), (530, 220), (527, 286), (503, 286)]
    out.append(cast(D, 518, 284, 22, 5, strength=0.4, seed=349))
    out.append(f'<path d="{pd([(502, 232), (528, 232), (527, 284), (503, 284)])}" fill="#8A3A10"/>')
    out.append(specks(349, (504, 236, 526, 282), ["#FFD8A0", "#FFFFFF"], 12, (0.8, 1.6), (0.6, 1)))
    out.append(f'<path d="{pd(gl)}" fill="#FFFFFF" opacity="0.25"/>' + ink(pd(gl), "#5A6A6A", 1.6, 349, 1, 0.8))
    out.append(taper([(505, 226), (506, 280)], 3, 2, "#FFFFFF", 0.7))
    # the caramelo, hoping
    out.append(caramelo(D, 486, 520, 0.9, 340))
    # lettering
    out.append(letters(D, 300, 138, "churrasco", SERIF_IT, 120, "#7A1E12", ["#A8301E", "#5A0E08", "#C8483A"], 341, max_w=450,
                       shadow="#FFF0D8", soff=(0.02, 0.03), angle=-40, hi="#F8A880"))
    out.append(ruled(300, 184, "COM A FAMÍLIA", "#1F5A36", font=JOS, size=28, ls=9, line_w=40, gap=14))
    return finish_b(D, out, 342)


# ================================================================ 17. domingo é dia de futebol — the campinho, flip-flop goalposts
def chinelo(D, cx, cy, L, seed, sole=AMAR, strap=VERDE, rot_=0, squash=0.55):
    """A flip-flop seen from above, foreshortened by `squash`."""
    out = [f'<g transform="translate({cx} {cy}) scale(1 {squash}) rotate({rot_})">']
    pts = []
    for i in range(32):
        t = i / 32 * 2 * math.pi
        y = -math.cos(t) * L / 2
        w = L * (0.2 + 0.08 * math.cos(t * 1) * -1 + 0.06 * math.sin(t * 2) ** 2)
        if -math.cos(t) > 0:
            w = L * 0.17 + L * 0.06 * (1 - abs(-math.cos(t)))
        pts.append((math.sin(t) * w, y))
    out.append(f'<path d="{smooth_closed([(x + 3, y + 5) for x, y in pts])}" fill="#3A2418" opacity="0.25"/>')
    out.append(painted(D, pts, sole, seed, sdir=(0.5, 0.8), sk=0.1, angle=-90, n=10, inkw=1.6, hi=0.35))
    out.append(f'<path d="{smooth_closed([(x * 0.86, y * 0.9) for x, y in pts])}" fill="{sole[0]}" opacity="0.5"/>')
    tx, ty = 0, -L * 0.28
    for sg in (-1, 1):
        out.append(taper([(tx, ty), (sg * L * 0.12, -L * 0.1), (sg * L * 0.19, L * 0.04)], L * 0.08, L * 0.07, strap[1]))
        out.append(taper([(tx, ty - 1), (sg * L * 0.12, -L * 0.11), (sg * L * 0.19, L * 0.03)], L * 0.025, L * 0.02, strap[0], 0.8))
    out.append(f'<circle cx="{tx}" cy="{ty}" r="{L * 0.045:.1f}" fill="{strap[2]}"/>')
    out.append("</g>")
    return "".join(out)


def soccer_ball(D, cx, cy, r, seed, tilt=(-18, 24, 8)):
    """Classic ball, built as a real truncated icosahedron (pentagon centres = icosahedron vertices, cut at
    1/3 along each edge), orthographically projected; black pentagons, grey seams, painted shading."""
    phi = (1 + 5 ** 0.5) / 2
    V = []
    for a_ in (-1, 1):
        for b_ in (-phi, phi):
            V += [(0, a_, b_), (a_, b_, 0), (b_, 0, a_)]

    def norm(p):
        n = math.sqrt(sum(v * v for v in p))
        return tuple(v / n for v in p)

    def rx(p, a):
        x, y, z = p
        return x, y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)

    def ry(p, a):
        x, y, z = p
        return x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a)

    def rz(p, a):
        x, y, z = p
        return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z

    # rotate so (0, 1, phi) faces the viewer, then tilt
    a0 = math.atan2(1, phi)

    def T(p):
        p = rx(p, a0)
        p = rx(p, math.radians(tilt[0]))
        p = ry(p, math.radians(tilt[1]))
        return rz(p, math.radians(tilt[2]))
    nb = {i: [j for j in range(12) if i != j and abs(math.dist(V[i], V[j]) - 2) < 1e-6] for i in range(12)}

    def cut(i, j):
        return T(norm(tuple(V[i][k] + (V[j][k] - V[i][k]) / 3 for k in range(3))))

    def proj(p):
        x, y, z = p
        if z < 0:
            n = math.hypot(x, y) or 1
            x, y = x / n, y / n
        return cx + x * r, cy - y * r
    out = [cast(D, cx + r * 0.25, cy + r * 0.95, r * 1.05, r * 0.2, strength=0.5, seed=seed)]
    d = blob(cx, cy, r, r, seed, 0.004, 32)
    out.append(f'<path d="{d}" fill="#FAFAF6"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    seams = set()
    for i in range(12):
        c = T(norm(V[i]))
        vs = [cut(i, j) for j in nb[i]]
        # order around the centre in screen space
        vs.sort(key=lambda p: math.atan2(p[1] - c[1], p[0] - c[0]))
        if c[2] > -0.2:
            pts = [proj(p) for p in vs]
            inner.append(f'<path d="{hg.org_poly(pts, seed + i, 0.3, 6, 1.0)}" fill="#1E1C22"/>')
        for j in nb[i]:
            for k in nb[j]:
                if k in nb[i]:
                    # hexagon edge between the cut points of edge (i,j) and edge (i,k)? -> that is a pentagon edge; skip
                    pass
            key = tuple(sorted((i, j)))
            seams.add(key)
    for i, j in seams:
        p, q = cut(i, j), cut(j, i)
        if p[2] > 0 and q[2] > 0:
            inner.append(pline([proj(p), proj(q)], "#7A7A84", 1.5, seed + i, 0.75, 1))
    inner.append(f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0), (0.55, "#2A2A40", 0.08), (1, "#1A1A2A", 0.55)], 0.36, 0.32, 0.72)}"/>')
    inner.append(f'<path d="{blob(cx + r * 0.1, cy + r * 0.88, r * 0.8, r * 0.22, seed, 0.2, 12)}" fill="#A8743A" opacity="0.35"/>')
    inner.append(strokes(D.nid(), d, (cx - r, cy - r, cx + r, cy + r), ["#FFFFFF", "#8A8A9A"], seed, n=int(r * 0.6), angle=-40, length=(r * 0.2, r * 0.5), width=(1, 3), opacity=(0.1, 0.25), curve=0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - r * 0.66, cy - r * 0.2), (cx - r * 0.56, cy - r * 0.5), (cx - r * 0.3, cy - r * 0.7)], max(2, r * 0.08), 1, "#FFFFFF", 0.9))
    out.append(ink(d, INK, max(1.8, r * 0.035), seed, 2, 0.8))
    return "".join(out)


@design("domingo-e-dia-de-futebol")
def domingo_futebol():
    D = Doc2("df")
    out = [sky(D, [(0, "#5AB0E0"), (0.45, "#A8DCEE"), (0.62, "#FFE8B8")], 3, 600, ["#FFFFFF", "#8ACBEA", "#FFF2D0"], 70)]
    out.append(soft_glow(D, 480, 300, 200, "#FFF4C0", 0.6))
    out.append(puff_cloud(D, 470, 236, 96, 350, ("#FFFFFF", "#FFF8F0", "#C8D8E8")))
    # the morro: a hillside of colourful little houses, rows stacked up the slope
    out.append(hill(D, ridge([(-20, 300), (120, 250), (260, 276), (380, 240), (520, 270), (620, 256)], 351, 6), 600, ("#9ACB7A", "#6EA85A", "#3E7A3A"), 351, inkw=1.2, inkop=0.35))
    rnd = random.Random(352)
    cols = ["#F6C21C", "#E8507A", "#2E8AC8", "#F28A3A", "#FFFDF4", "#7ACB6A", "#C8A0E0", "#FF8A7A", "#5AC8C0"]
    for j in range(5):
        x = -20 + rnd.uniform(0, 20)
        while x < 610:
            w, h = rnd.uniform(28, 46) * (0.8 + j * 0.06), rnd.uniform(20, 34) * (0.8 + j * 0.06)
            ybase = 296 - 30 * math.sin(math.pi * (x + 20) / 640) + j * 20 + rnd.uniform(-3, 3)
            out.append(town_house(D, x, ybase, w, h, 352 + j * 40 + int(x), rnd.choice(cols), "slab", haze=0.35 - j * 0.08))
            x += w + rnd.uniform(-4, 4)
        if j == 2:
            # a washing line strung between two roofs
            out.append(pline([(150, 300), (210, 306), (270, 300)], "#5A4A3A", 1, 359, 0.8, 1))
            for k, c in enumerate(("#E8507A", "#FFFFFF", "#2E8AC8", "#F6C21C")):
                out.append(f'<path d="{hg.org_rect(160 + k * 26, 302 + abs(k - 1.5) * 1.5, 12, 14, 360 + k, 0.3, 6, 1)}" fill="{c}"/>')
    # the dirt and grass field
    out.append(hill(D, ridge([(-20, 384), (300, 378), (620, 386)], 353, 2), 620, ("#B8D47A", "#86B050", "#4E7A2E"), 353, inkw=1.2, inkop=0.4))
    pitch = [(40, 420), (560, 420), (640, 620), (-40, 620)]
    out.append(painted(D, pitch, ("#F0D0A0", "#D8A870", "#A8784A"), 354, sdir=(0, 1), sk=0.06, angle=-4, n=90, slen=(30, 90), inkw=0, hi=0.25))
    out.append(grass(355, (0, 384, 600, 430), ["#4E7A2E", "#6E9A3A", "#A8C860"], 90, (6, 14)))
    out.append(grass(356, (0, 540, 70, 600), ["#4E7A2E", "#6E9A3A"], 30, (8, 16)))
    out.append(grass(357, (530, 540, 600, 600), ["#4E7A2E", "#6E9A3A"], 30, (8, 16)))
    # chalk line scuffed in the dirt
    out.append(taper([(60, 520), (300, 516), (540, 522)], 4, 4, "#FFFFFF", 0.55))
    # bunting across
    out.append(hg.bunting(D, -10, 228, 610, 228, 40, 12, ["#1F8A4C", "#F6C21C", "#1F4FA0", "#FFFFFF"], 358, size=22))
    # flip-flop goalposts and the ball
    out.append(chinelo(D, 96, 470, 96, 359, AMAR, VERDE, -8))
    out.append(chinelo(D, 140, 488, 96, 360, AMAR, VERDE, 14))
    out.append(chinelo(D, 462, 470, 96, 361, AZUL, AMAR, 6))
    out.append(chinelo(D, 506, 490, 96, 362, AZUL, AMAR, -12))
    out.append(soccer_ball(D, 300, 448, 66, 363))
    for k, (x, y) in enumerate(((236, 506), (370, 508), (250, 496))):
        out.append(f'<path d="{blob(x, y, 12, 4, 364 + k, 0.2, 8)}" fill="#C8986A" opacity="0.6"/>')
    # lettering
    out.append(letters(D, 300, 104, "domingo é dia de", SERIF_IT, 50, "#1F3F8A", ["#2E5AB8", "#14286A"], 365, max_w=420, wob=0.5))
    out.append(letters(D, 300, 206, "FUTEBOL", ANTON, 104, "#F6C21C", ["#FFE07A", "#D89A10", "#FFF2B0"], 366, ls=8, max_w=440,
                       shadow="#1F6A40", soff=(0.035, 0.045), angle=-75, wob=0.5, hi="#FFFFFF"))
    return finish_b(D, out, 367)


# ================================================================ 18. vai dar certo — a jangada sailing into the sunrise
def jangada(D, x, wl, s, seed):
    """Jangada: a raft of logs riding low, a tall curved triangular sail with patches, mast and boom, a fisherman."""
    def L(pts):
        return [(x + px * s, wl + py * s) for px, py in pts]
    out = []
    out.append(f'<path d="{blob(x + 10 * s, wl + 6 * s, 90 * s, 7 * s, seed, 0.1, 14)}" fill="#0E2A4A" opacity="0.35"/>')
    raft = L([(-80, -8), (84, -10), (92, -2), (80, 6), (-76, 8), (-86, 0)])
    out.append(painted(D, raft, WOOD, seed, sdir=(0, 1), sk=0.2, angle=0, n=12, inkw=1.6, hi=0.4))
    for k in range(1, 3):
        out.append(pline(L([(-82, -8 + k * 5), (86, -10 + k * 5)]), WOOD[2], 1.2, seed + k, 0.6, 1))
    # mast, sail, boom
    out.append(taper(L([(10, -6), (6, -110), (2, -230)]), 4.5 * s, 2.5 * s, "#5A3418"))
    sail = L([(2, -228), (16, -200), (40, -140), (70, -70), (90, -26), (14, -24), (8, -120)])
    out.append(painted(D, sail, ("#FFFFFF", "#FAF2E2", "#C8B898"), seed + 1, sdir=(1, 0.4), sk=0.12, angle=-70, n=30, inkw=1.8, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(sail)}"/>')
    pat = [f'<path d="{smooth_closed(L([(10, -110), (48, -110), (52, -86), (12, -86)]))}" fill="#F2A01A" opacity="0.85"/>',
           f'<path d="{smooth_closed(L([(10, -70), (70, -70), (76, -54), (10, -54)]))}" fill="#E8484A" opacity="0.8"/>',
           shade_over(D, smooth_closed(sail), "#5A4A3A", 0.3, 0, 0, 1, 0, 0.5)]
    out.append(f'<g {cid}>{"".join(pat)}</g>')
    out.append(taper(L([(8, -26), (92, -28)]), 3 * s, 2 * s, "#5A3418"))
    # fisherman with a straw hat
    out.append(painted(D, L([(-40, -8), (-46, -36), (-36, -50), (-26, -36), (-30, -8)]), ("#5A8AC8", "#2E5A9A", "#14305A"), seed + 2, sk=0.2, n=4, inkw=1.2, hi=0.3))
    hx, hy = L([(-36, -56)])[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{7 * s:.1f}" fill="#8A5A3A"/>')
    out.append(f'<path d="{blob(hx, hy - 5 * s, 15 * s, 4 * s, seed, 0.1, 10)}" fill="#E8C878"/><path d="{blob(hx, hy - 8 * s, 7 * s, 5 * s, seed + 1, 0.1, 10)}" fill="#E8C878"/>')
    return "".join(out)


@design("vai-dar-certo")
def vai_dar_certo():
    D = Doc2("vd")
    out = [sky(D, [(0, "#4A6AB8"), (0.3, "#B88AC0"), (0.52, "#FFB08A"), (0.62, "#FFE0A0")], 3, 600, ["#FFFFFF", "#F8B0A0", "#C8A0D0"], 80)]
    out.append(soft_glow(D, 250, 372, 300, "#FFF0B0", 0.8))
    out.append(puff_cloud(D, 120, 300, 110, 370, ("#FFE8E0", "#F8C8C0", "#C88AA8"), op=0.9))
    out.append(puff_cloud(D, 480, 270, 130, 371, ("#FFE8E0", "#F8C8C0", "#C88AA8"), op=0.9))
    sun = blob_pts(250, 372, 84, 84, 372, 0.01, 30)
    out.append(painted(D, sun, ("#FFF6C0", "#FFD84A", "#F2A01A"), 372, sdir=(0.3, 0.8), sk=0.05, angle=-30, n=40, inkw=0, hi=0.5, hik=0.05))
    # sea, with the sun's path of light
    out.append(sea(D, 372, 600, [(0, "#F8B08A"), (0.15, "#5A8AC0"), (1, "#1E3E7A")], 373, ["#FFFFFF", "#F8C8A0", "#14306A"], 70))
    rnd = random.Random(374)
    for i in range(46):
        y = rnd.uniform(380, 590)
        w = 10 + (y - 372) * 0.35
        x = 250 + rnd.uniform(-w, w) * 0.9
        out.append(taper([(x - 10 - (y - 372) * 0.05, y), (x + 10 + (y - 372) * 0.05, y)], 2.2, 2.2, rnd.choice(["#FFF2B0", "#FFE080", "#FFFFFF"]), rnd.uniform(0.5, 0.95)))
    # a bit of beach with a coconut palm on the right edge
    out.append(hill(D, [(400, 610), (470, 520), (540, 500), (620, 494)], 620, ("#FFF0CE", "#F2D8A0", "#C9A066"), 375, inkw=1.2, inkop=0.4))
    out.append(palm(D, (560, 620), (520, 360), 376, [(-170, 1.0), (-140, 0.9), (-110, 0.8), (-75, 0.85), (-40, 0.9), (-200, 0.85), (-10, 0.8)], L=100, width=16))
    out.append(jangada(D, 340, 470, 0.95, 377))
    for x, y, s in ((120, 404, 0.0), (90, 250, 8), (110, 236, 6), (430, 210, 7)):
        if s:
            out.append(bird_v(x, y, s, "#3A2A48", 0.8))
    # lettering
    out.append(letters(D, 300, 128, "vai dar", SERIF_IT, 90, "#FFF6E8", ["#FFFFFF", "#F8E0D0"], 378, max_w=330,
                       shadow="#2A2A6A", soff=(0.02, 0.035), angle=-40))
    out.append(letters(D, 300, 232, "certo", SERIF_IT, 140, "#FFD84A", ["#FFE88A", "#F2A81D", "#FFF6C8"], 379, max_w=360,
                       shadow="#2A2A6A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    return finish_b(D, out, 380)


# ================================================================ 20. oxe! — sertão noon: the mandacaru, the sun, a goat
def mandacaru(D, x, base, h, seed, arms=((0.45, -1, 0.42), (0.6, 1, 0.38))):
    """Columnar cactus with upturned arms: ribbed green columns, spines, a pink flower."""
    pal = ("#8ACB7A", "#3E8A4A", "#1E5230")
    out = []
    w = h * 0.12

    def column(px, pb, ph, ww, sd):
        pts = rect_pts(px - ww / 2, pb - ph, px + ww / 2, pb, 14, sd, 0.6)
        pts = [(xx, yy if yy > pb - ph + ww * 0.5 else pb - ph + ww * 0.5 - math.sqrt(max(0, (ww / 2) ** 2 - (xx - px) ** 2)) * 0.9) for xx, yy in pts]
        o = [painted(D, pts, pal, sd, sdir=(1, 0), sk=0.22, angle=-90, n=int(ph / 6), slen=(10, 30), sw=(1, 2.4), inkw=1.8, hi=0.4, hik=0.12)]
        for k in (-0.25, 0.05, 0.3):
            o.append(pline([(px + k * ww, pb - ph + ww * 0.3), (px + k * ww, pb)], pal[2], 1.4, sd, 0.55, 1))
        rnd = random.Random(sd)
        for _ in range(int(ph / 9)):
            sx_, sy_ = px + rnd.choice((-0.5, 0.5)) * ww, rnd.uniform(pb - ph + ww * 0.4, pb)
            o.append(f'<path d="M {sx_:.1f} {sy_:.1f} l {math.copysign(5, sx_ - px):.1f} -2" stroke="#FFF6D8" stroke-width="1.1"/>')
        return "".join(o)
    out.append(column(x, base, h, w, seed))
    for k, (t, side, ah) in enumerate(arms):
        ay = base - h * t
        ax = x + side * w * 1.6
        out.append(taper([(x + side * w * 0.3, ay), (x + side * w * 1.2, ay + 4), (ax, ay - 6)], w * 0.8, w * 0.8, pal[1]))
        out.append(column(ax, ay + 2, h * ah, w * 0.85, seed + k + 3))
    fx, fy = x + w * 0.1, base - h - w * 0.2 + w * 0.5
    for j in range(6):
        a = math.radians(-90 + (j - 2.5) * 22)
        out.append(f'<path d="{blob(fx + math.cos(a) * 8, fy + math.sin(a) * 8, 8, 4, seed + j, 0.1, 8, math.degrees(a))}" fill="#FFFFFF" stroke="#E8A0B8" stroke-width="1"/>')
    return "".join(out)


def goat(D, x, base, s, seed, flip=1):
    """Bode do sertão, side view facing left: deep-chested body with brown patches, long face, swept-back
    horns, floppy ear, beard, jointed legs with dark hooves, tail flicked up."""
    k = s

    def L(pts):
        return [(x + flip * px * k, base + py * k) for px, py in pts]
    coat = ("#FFFDF4", "#EEE4D0", "#B8A888")
    brown = ("#C88A5A", "#8A5432", "#4A2A16")
    out = [cast(D, x, base + 2, 62 * k, 7 * k, strength=0.4, seed=seed)]
    # far legs (darker)
    for pts in (([(-30, -34), (-33, -18), (-30, -4), (-31, 0)]), ([(34, -36), (40, -20), (34, -6), (35, 0)])):
        out.append(taper(L(pts), 7 * k, 4.5 * k, "#A8987A"))
        hx, hy = L([pts[-1]])[0]
        out.append(f'<path d="{blob(hx, hy - 2 * k, 3.4 * k, 2.4 * k, seed, 0.1, 8)}" fill="#3A2A1A"/>')
    body = L([(-46, -64), (-24, -72), (10, -70), (36, -68), (52, -58), (54, -42), (44, -30), (16, -26), (-14, -28), (-36, -30), (-50, -42)])
    out.append(painted(D, body, coat, seed, sdir=(0.4, 0.9), sk=0.2, angle=-8, n=30, inkw=1.8, hi=0.4))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    patch = smooth_closed(L([(4, -74), (40, -72), (58, -52), (40, -40), (14, -46), (0, -60)]))
    patch2 = smooth_closed(L([(-30, -40), (-10, -44), (-4, -30), (-26, -26)]))
    out.append(f'<g {cid}><path d="{patch}" fill="{brown[1]}" opacity="0.9"/><path d="{patch2}" fill="{brown[1]}" opacity="0.8"/>'
               f'{strokes(D.nid(), bd, bbox(body), [coat[2], "#FFFFFF", brown[2]], seed + 7, n=40, angle=80, length=(4, 10), width=(0.8, 1.6), opacity=(0.2, 0.5), curve=0.4)}</g>')
    # near legs with knees and hocks
    for pts in (([(-38, -34), (-41, -16), (-37, -4), (-38, 0)]), ([(28, -36), (34, -20), (27, -6), (28, 0)])):
        out.append(taper(L(pts), 8 * k, 5 * k, coat[1]))
        out.append(ink(smooth_open(L(pts)), "#8A7A60", 1.0, seed, 1, 0.5))
        hx, hy = L([pts[-1]])[0]
        out.append(f'<path d="{blob(hx, hy - 2 * k, 3.8 * k, 2.6 * k, seed + 1, 0.1, 8)}" fill="#3A2A1A"/>')
    # neck and head
    neck = L([(-36, -60), (-48, -82), (-57, -102), (-42, -112), (-30, -90), (-18, -66)])
    out.append(painted(D, neck, coat, seed + 1, sdir=(0.4, 0.9), sk=0.2, angle=-60, n=8, inkw=1.6, hi=0.35))
    head = L([(-46, -112), (-58, -118), (-72, -112), (-84, -100), (-86, -91), (-78, -87), (-66, -92), (-50, -98)])
    out.append(painted(D, head, coat, seed + 2, sdir=(0.4, 0.9), sk=0.18, angle=-30, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(L([(-60, -114), (-74, -106), (-80, -98), (-68, -100), (-58, -106)]))}" fill="{brown[1]}" opacity="0.75"/>')
    # horns sweeping back, ear, eye, nostril, beard
    out.append(taper(catmull(L([(-56, -112), (-50, -126), (-38, -132), (-28, -126)]), 4), 6 * k, 2 * k, "#7A6A50"))
    out.append(taper(catmull(L([(-56, -112), (-50, -126), (-38, -132), (-28, -126)]), 4), 2 * k, 0.8 * k, "#C8B898", 0.8))
    out.append(painted(D, L([(-54, -104), (-44, -100), (-36, -90), (-40, -86), (-52, -96)]), brown, seed + 3, sk=0.2, n=3, inkw=1.2, hi=0.3))
    ex, ey = L([(-66, -106)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{2.6 * k:.1f}" ry="{1.8 * k:.1f}" fill="#2A1A10"/>')
    out.append(f'<circle cx="{ex - flip * 0.8 * k:.1f}" cy="{ey - 0.6 * k:.1f}" r="{0.7 * k:.1f}" fill="#FFFFFF"/>')
    nx_, ny_ = L([(-83, -94)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{1.2 * k:.1f}" fill="#4A3A2A"/>')
    out.append(taper(L([(-76, -88), (-78, -78), (-74, -70)]), 6 * k, 1.5 * k, "#D8CCB0"))
    out.append(taper(L([(50, -62), (58, -72), (62, -80)]), 5 * k, 1.6 * k, coat[1]))
    return "".join(out)


def casa_taipa(D, x, base, w, h, seed):
    """Little wattle-and-daub house: ochre plaster with the stick lattice showing where it has fallen,
    a blue door and window, a clay-tile roof."""
    wall = rect_pts(x, base - h, x + w, base, 14, seed, 0.8)
    out = [cast(D, x + w / 2, base + 2, w * 0.6, 6, strength=0.35, seed=seed)]
    out.append(painted(D, wall, ("#F2C890", "#D89A5A", "#8A5A2A"), seed, sdir=(1, 0.3), sk=0.1, angle=-80, n=30, inkw=1.6, hi=0.3))
    lat = blob(x + w * 0.72, base - h * 0.55, w * 0.14, h * 0.2, seed, 0.2, 12)
    out.append(f'<path d="{lat}" fill="#8A5A30"/>')
    cid = D.clip(f'<path d="{lat}"/>')
    grid = "".join(f'<path d="M {x + w * 0.5 + i * 7:.1f} {base - h:.1f} l 0 {h:.1f}" stroke="#D8B07A" stroke-width="2"/>' for i in range(12))
    grid += "".join(f'<path d="M {x:.1f} {base - h + j * 7:.1f} l {w:.1f} 0" stroke="#C89A5A" stroke-width="1.6"/>' for j in range(12))
    out.append(f'<g {cid}>{grid}</g>')
    out.append(painted(D, rect_pts(x + w * 0.18, base - h * 0.62, x + w * 0.38, base, 8, seed + 1, 0.4), AZUL, seed + 1, sdir=(1, 0.3), sk=0.15, n=6, inkw=1.4, hi=0.3))
    out.append(painted(D, rect_pts(x + w * 0.52, base - h * 0.66, x + w * 0.66, base - h * 0.42, 8, seed + 2, 0.4), AZUL, seed + 2, sk=0.15, n=4, inkw=1.4, hi=0.3))
    out.append(tile_roof(D, [(x - w * 0.1, base - h + 2), (x + w * 0.1, base - h - h * 0.42), (x + w * 0.9, base - h - h * 0.42), (x + w * 1.1, base - h + 2), (x + w * 1.08, base - h + 8), (x - w * 0.08, base - h + 8)], seed + 3, TERRA, 3, 9))
    return "".join(out)


@design("oxe")
def oxe():
    D = Doc2("ox")
    out = [sky(D, [(0, "#F07A34"), (0.45, "#F8B04A"), (0.8, "#FCE09A")], 3, 600, ["#FFE08A", "#E86A2A", "#FFF0C0"], 90, angle=-6)]
    # woodcut-style sun with triangular rays, low over the serra
    cx, cy = 300, 360
    out.append(soft_glow(D, cx, cy, 300, "#FFF6C0", 0.6))
    for i in range(24):
        a = math.radians(i * 15 + 7)
        r0, r1 = 112, 196 if i % 2 else 160
        p = [(cx + math.cos(a - 0.09) * r0, cy + math.sin(a - 0.09) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1), (cx + math.cos(a + 0.09) * r0, cy + math.sin(a + 0.09) * r0)]
        out.append(f'<path d="{hg.org_poly(p, 420 + i, 0.6, 10, 1)}" fill="{"#FFF0A0" if i % 2 else "#FFE07A"}" opacity="0.85"/>')
    out.append(painted(D, blob_pts(cx, cy, 100, 100, 421, 0.01, 30), ("#FFF6C0", "#FFD23A", "#F29A1A"), 421, sk=0.06, angle=-30, n=50, inkw=2, inkc="#B8600A", hi=0.5, hik=0.05))
    # serra and caatinga scrub
    out.append(hill(D, ridge([(-20, 410), (90, 384), (190, 400), (300, 376), (420, 396), (520, 372), (620, 392)], 422, 7), 620, ("#E8A870", "#C8784A", "#8A4A2A"), 422, inkw=1.2, inkop=0.4, sop=(0.1, 0.3)))
    rnd = random.Random(423)
    for i in range(16):
        x = rnd.uniform(0, 600)
        y = 414 + rnd.uniform(-6, 14)
        out.append(taper([(x, y), (x + rnd.uniform(-6, 6), y - rnd.uniform(14, 26))], 2.4, 1, "#6A4A2A", 0.8))
        out.append(taper([(x + 2, y - 10), (x + rnd.uniform(6, 12), y - rnd.uniform(18, 24))], 1.6, 0.8, "#6A4A2A", 0.8))
    out.append(hill(D, [(-20, 442), (200, 434), (420, 444), (620, 436)], 620, ("#F2D49A", "#DDB070", "#A87A40"), 424, inkw=1.4, inkop=0.5))
    for i in range(22):
        x, y = rnd.uniform(20, 580), rnd.uniform(470, 590)
        pts = [(x, y)]
        for _ in range(3):
            x, y = x + rnd.uniform(-22, 22), y + rnd.uniform(-8, 10)
            pts.append((x, y))
        out.append(taper(pts, 2.2, 0.6, "#8A5A2A", 0.6))
    # little taipa house on the left, mandacaru on the right, the bode in front
    out.append(casa_taipa(D, 64, 446, 104, 58, 425))
    out.append(mandacaru(D, 476, 524, 250, 426))
    for k, (x, y) in enumerate(((390, 522), (110, 538), (566, 470), (210, 462))):
        for j in range(3):
            out.append(painted(D, blob_pts(x + j * 10 - 10, y - 8 - (j % 2) * 6, 6, 12, 430 + k * 3 + j, 0.08, 10), ("#8ACB7A", "#3E8A4A", "#1E5230"), 430 + k * 3 + j, sk=0.2, n=3, inkw=1.2, hi=0.3))
    out.append(goat(D, 270, 538, 1.3, 428, flip=1))
    # lettering
    out.append(letters(D, 300, 186, "Oxe!", SERIF_IT, 160, "#7A1E0E", ["#A8301E", "#5A0E06", "#C8482A"], 438, max_w=400,
                       shadow="#FFF6D0", soff=(0.02, 0.03), angle=-40, hi="#F8A880"))
    out.append(ruled(300, 238, "ARRETADO DEMAIS", "#7A1E0E", font=JOS, size=24, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 439)


# ================================================================ 21. uai, sô! — Minas: the wood stove, cheese and goiabada
@design("uai-so")
def uai_so():
    D = Doc2("us")
    # kitchen wall: warm lime-wash, a blue painted barrado below
    out = [sky(D, [(0, "#FBEFD6"), (1, "#F2DEB8")], 3, 600, ["#FFFFFF", "#E8CC98", "#FFF6E0"], 90, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(430, ["#E8C890", "#FFFFFF"], 6, (0, 0, 600, 360), (90, 160), (0.06, 0.12)))
    out.append(f'<path d="M -10 300 L 610 300 L 610 610 L -10 610 Z" fill="#5A8AC0"/>')
    out.append(strokes(D.nid(), "M -10 300 L 610 300 L 610 610 L -10 610 Z", (-40, 300, 610, 610), ["#7AA6D8", "#3E6AA0", "#8AB4E0"], 431, n=90, angle=-80, length=(30, 80), width=(3, 8), opacity=(0.15, 0.35)))
    out.append(pline([(-10, 300), (300, 302), (610, 299)], "#2E4A7A", 2.4, 432, 0.8, 1))
    # the window: open blue shutters on the hills of Minas and a little white church
    wx0, wy0, wx1, wy1 = 336, 222, 504, 318
    win = hg.org_rect(wx0, wy0, wx1 - wx0, wy1 - wy0, 433, 0.5, 12, 2)
    wcid = D.clip(f'<path d="{win}"/>')
    land = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#8ACBE8"), (1, "#E8F4F0")])}"/>',
            puff_cloud(D, 380, 248, 60, 434, ("#FFFFFF", "#FFFFFF", "#C8DCE8")),
            hill(D, ridge([(wx0 - 10, 292), (370, 270), (420, 284), (470, 262), (wx1 + 10, 280)], 435, 4), wy1 + 10, ("#8AB88A", "#5E9A6A", "#3E7A4E"), 435, inkw=0),
            hill(D, ridge([(wx0 - 10, 312), (400, 300), (450, 308), (wx1 + 10, 296)], 436, 3), wy1 + 10, ("#B8D47A", "#86B050", "#4E7A2E"), 436, inkw=1, inkop=0.3)]
    ch = 452
    land.append(painted(D, rect_pts(ch - 20, 270, ch + 20, 296, 8, 437, 0.3), ("#FFFFFF", "#F4EEE0", "#B8B0A0"), 437, sk=0.1, n=4, inkw=1, hi=0.3))
    for tx in (ch - 18, ch + 10):
        land.append(painted(D, rect_pts(tx, 256, tx + 9, 272, 6, 438 + tx, 0.2), ("#FFFFFF", "#F4EEE0", "#B8B0A0"), 438 + tx, sk=0.1, n=2, inkw=1, hi=0.3))
        land.append(f'<path d="M {tx - 1} 257 L {tx + 4.5} 248 L {tx + 10} 257 Z" fill="#2E6AB8"/>')
    land.append(f'<path d="M {ch - 22} 272 L {ch} 260 L {ch + 22} 272 Z" fill="#C0603A"/><rect x="{ch - 4}" y="282" width="8" height="14" fill="#2E6AB8"/>')
    out.append(f'<g {wcid}>{"".join(land)}</g>')
    out.append(ink(win, "#2E4A7A", 5, 439, 1, 1))
    out.append(pline([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], "#2E4A7A", 4, 440, 1, 1))
    for sg, sx in ((-1, wx0 - 46), (1, wx1 + 4)):
        sh_ = rect_pts(sx, wy0 - 2, sx + 42, wy1 + 2, 12, 441 + sg, 0.5)
        out.append(painted(D, sh_, ("#6A9ADC", "#2E62B0", "#163A70"), 441 + sg, sdir=(1, 0.4), sk=0.12, angle=-90, n=10, inkw=1.6, hi=0.35))
        for kk in range(1, 6):
            out.append(pline([(sx + 3, wy0 + kk * (wy1 - wy0) / 6), (sx + 39, wy0 + kk * (wy1 - wy0) / 6)], "#163A70", 1.6, 442 + kk, 0.7, 1))
    out.append(painted(D, rect_pts(wx0 - 10, wy1, wx1 + 10, wy1 + 10, 14, 443, 0.4), ("#FFFDF4", "#EEE6D2", "#A8A08A"), 443, sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
    # string of linguiça drying on a pole over the stove (fumeiro)
    out.append(taper([(52, 226), (290, 230)], 6, 6, "#6A4220"))
    for i in range(5):
        x = 80 + i * 44
        lk = catmull([(x - 12, 232), (x - 15, 254), (x - 6, 276), (x + 6, 276), (x + 15, 254), (x + 12, 232)], 5)
        out.append(taper([(px + 2, py + 3) for px, py in lk], 14, 14, "#3A1008", 0.3))
        out.append(taper(lk, 14, 14, "#9A3020"))
        out.append(taper([(px - 2.5, py - 1) for px, py in lk], 4, 4, "#E0705A", 0.65))
        out.append(ink(smooth_open(lk), "#4A1008", 1.2, 600 + i, 1, 0.5))
        for t in (0.3, 0.7):
            px, py = lk[int(t * (len(lk) - 1))]
            out.append(f'<path d="M {px - 7:.1f} {py:.1f} L {px + 7:.1f} {py:.1f}" stroke="#F2E2C0" stroke-width="2" stroke-linecap="round"/>')
    # the wood stove: black iron top with rings, whitewashed body with a red vermelhão edge
    body = [(36, 424), (564, 424), (568, 610), (32, 610)]
    out.append(painted(D, poly_pts(body, 24, 444, 0.8), ("#FFFDF6", "#F2EADA", "#C8BCA0"), 444, sdir=(1, 0.4), sk=0.05, angle=-80, n=70, inkw=2, hi=0.25))
    out.append(painted(D, rect_pts(30, 416, 570, 438, 24, 445, 0.6), ("#E8806A", "#C0402E", "#7A1A10"), 445, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(painted(D, rect_pts(40, 396, 560, 418, 24, 446, 0.6), ("#5A5A64", "#2E2E36", "#141418"), 446, sdir=(0, 1), sk=0.2, angle=0, n=40, inkw=2, hi=0.35))
    for x in (150, 300, 450):
        out.append(f'<path d="{blob(x, 405, 56, 6, x, 0.03, 18)}" fill="none" stroke="#6A6A74" stroke-width="2.4"/>')
    # fornalha door with the fire, soot above it
    out.append(f'<path d="{blob(160, 456, 70, 20, 447, 0.2, 14)}" fill="#3A3030" opacity="0.18"/>')
    fd = rect_pts(110, 462, 214, 534, 14, 448, 0.6)
    out.append(painted(D, fd, ("#5A5A64", "#2E2E36", "#141418"), 448, sk=0.15, n=10, inkw=2, hi=0.3))
    out.append(f'<path d="{hg.org_rect(122, 474, 80, 48, 449, 0.4, 10, 2)}" fill="#2A1008"/>')
    out.append(D.glow(162, 508, 70, "#FF8A2A", 0.85))
    rnd = random.Random(450)
    for _ in range(22):
        out.append(f'<path d="{blob(rnd.uniform(130, 194), rnd.uniform(506, 520), rnd.uniform(5, 9), 4, rnd.randint(1, 999), 0.2, 8)}" fill="{rnd.choice(["#FFC04A", "#FF7A1E", "#FFE08A", "#C8381E"])}"/>')
    for k in range(3):
        out.append(painted(D, [(140 + k * 18, 520), (148 + k * 18, 488 - (k % 2) * 8), (156 + k * 18, 520)], ("#FFF2A0", "#FFB030", "#E8601A"), 451 + k, sk=0.1, n=3, inkw=0, hi=0.4, edge=False))
    for x in (130, 150, 170, 190):
        out.append(f'<path d="M {x} 474 L {x} 522" stroke="#141418" stroke-width="2.8"/>')
    # firewood in the niche
    out.append(f'<path d="{hg.org_rect(246, 462, 120, 72, 452, 0.5, 12, 6)}" fill="#3A2A20" opacity="0.85"/>')
    for k in range(6):
        x, y = 272 + (k % 3) * 36, 516 - (k // 3) * 26
        out.append(painted(D, blob_pts(x, y, 20, 12, 453 + k, 0.06, 12), WOOD, 453 + k, sk=0.2, n=5, inkw=1.4, hi=0.3))
        out.append(f'<path d="{blob(x + 14, y, 7, 10, 460 + k, 0.08, 10)}" fill="#E8C08A"/><path d="{blob(x + 14, y, 4, 6, 467 + k, 0.08, 10)}" fill="none" stroke="#A87A44" stroke-width="1.2"/>')
    # iron pot of beans and the enamel coffee pot on the plate
    out.append(cast(D, 170, 400, 76, 7, strength=0.5, seed=474))
    pot = [(104, 334), (236, 334), (232, 372), (216, 398), (124, 398), (108, 372)]
    out.append(painted(D, pot, ("#6A6A74", "#34343C", "#16161A"), 475, sdir=(0.8, 0.4), sk=0.2, angle=-90, n=30, inkw=2, hi=0.4))
    out.append(painted(D, ell_pts(170, 334, 70, 11, 0, 360, 24), ("#5A5A64", "#2E2E36", "#141418"), 476, sk=0.15, n=10, inkw=1.6, hi=0.3))
    out.append(f'<path d="{blob(170, 332, 60, 7, 477, 0.04, 16)}" fill="#5A2A14"/>')
    out.append(specks(478, (116, 328, 224, 336), ["#2A0E06", "#8A4A24"], 30, (1.2, 2.4), (0.6, 1)))
    for sg in (-1, 1):
        out.append(ink(f"M {170 + sg * 68} 344 q {sg * 16} 0 {sg * 16} 14", "#16161A", 5, 479, 1, 1))
    out.append(steam(170, 318, 26, 480, "#FFFFFF", 3, 24, 6, 0.7))
    out.append(enamel_pot(D, 440, 322, 88, 74, 481, body=("#FFFFFF", "#F4F0E8", "#B8B0A6"), rim=RED, handle_side=1))
    out.append(taper([(396, 342), (376, 330), (364, 312)], 10, 5, "#F4F0E8") + ink(smooth_open([(396, 342), (376, 330), (364, 312)]), INK, 1.4, 482, 1, 0.6))
    out.append(steam(366, 302, 24, 483, "#FFFFFF", 1, 20, 5, 0.6))
    # board with queijo minas and goiabada (romeu e julieta) in front
    out.append(cast(D, 470, 540, 120, 10, strength=0.45, seed=484))
    out.append(painted(D, rect_pts(372, 500, 568, 534, 20, 485, 0.6), WOOD, 485, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
    qs = [(394, 446), (476, 446), (486, 454), (486, 504), (476, 510), (394, 510), (384, 504), (384, 454)]
    out.append(painted(D, qs, ("#FFFFF6", "#F8F2E0", "#D8CCAA"), 486, sdir=(0.9, 0.4), sk=0.1, angle=-90, n=14, inkw=1.8, hi=0.4))
    out.append(f'<path d="{blob(435, 450, 44, 7, 487, 0.03, 16)}" fill="#FFFFFF"/>' + ink(blob(435, 450, 44, 7, 487, 0.03, 16), "#C8BC9A", 1.2, 487, 1, 0.7))
    for kk in range(5):
        out.append(f'<circle cx="{398 + kk * 18}" cy="{472 + (kk % 2) * 14}" r="1.6" fill="#D8CCAA"/>')
    gb = [(496, 470), (550, 466), (556, 474), (556, 510), (500, 514), (492, 506)]
    out.append(painted(D, gb, ("#E8706A", "#B8282E", "#6A0A12"), 488, sdir=(0.9, 0.4), sk=0.15, angle=-90, n=12, inkw=1.8, hi=0.35))
    out.append(f'<path d="{pd([(496, 470), (550, 466), (556, 474), (502, 478)])}" fill="#D8484A"/>')
    # lettering on the wall
    out.append(letters(D, 300, 152, "Uai, sô!", SERIF_IT, 128, "#1F3F6A", ["#2E5A8A", "#0E2448", "#3E6A9A"], 489, max_w=430,
                       shadow="#F2D6A8", soff=(0.02, 0.035), angle=-40, hi="#A8C8E8"))
    out.append(ruled(300, 200, "TREM BÃO DEMAIS", "#A8361E", font=JOS, size=24, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 490)


# ================================================================ 22. bah, tchê! — chimarrão on the pampa at sundown
def cuia(D, cx, base, h, seed):
    """Chimarrão gourd: round-bellied gourd narrowing to a neck, chased-silver mouth ring, a mound of green
    erva with a little foam, the silver bomba with a gold mouthpiece."""
    w = h * 0.82
    prof = [(0.36, 0.0), (0.34, 0.07), (0.32, 0.17), (0.37, 0.3), (0.46, 0.46), (0.5, 0.62), (0.48, 0.78), (0.4, 0.9), (0.26, 0.98), (0.1, 1.0)]
    top = base - h
    right = [(cx + r * w, top + t * h) for r, t in prof]
    body = right + [(cx - (x - cx), y) for x, y in right[::-1]]
    out = [cast(D, cx + 12, base + 2, w * 0.55, 9, strength=0.5, seed=seed)]
    gourd = ("#D8A868", "#9A6A34", "#4A2E14")
    out.append(painted(D, body, gourd, seed, sdir=(0.85, 0.35), sk=0.2, angle=-90, n=70, cols=["#E0B070", "#5A3A18", "#B07A40", "#3A2410"], inkw=2.2, hi=0.45, hik=0.08))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(seed)
    tx = []
    for k in range(9):
        x0 = cx - w * 0.5 + k * w * 0.125
        tx.append(pline([(x0, top + h * 0.2), (x0 + (x0 - cx) * 0.25, top + h * 0.6), (x0 + (x0 - cx) * 0.05, base)], "#4A2E14", 1.4, seed + k, 0.25, 1))
    for _ in range(70):
        tx.append(f'<circle cx="{rnd.uniform(cx - w / 2, cx + w / 2):.1f}" cy="{rnd.uniform(top, base):.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="{rnd.choice(["#3A2410", "#F0C888"])}" opacity="0.35"/>')
    # a branded leather-like band with stitched edges round the belly
    by0, by1 = top + h * 0.5, top + h * 0.62
    tx.append(f'<path d="M {cx - w:.1f} {by0:.1f} Q {cx:.1f} {by0 + 14:.1f} {cx + w:.1f} {by0:.1f} L {cx + w:.1f} {by1:.1f} Q {cx:.1f} {by1 + 14:.1f} {cx - w:.1f} {by1:.1f} Z" fill="#5A3418" opacity="0.85"/>')
    for yy in (by0 + 3, by1 - 3):
        tx.append(f'<path d="M {cx - w:.1f} {yy:.1f} Q {cx:.1f} {yy + 14:.1f} {cx + w:.1f} {yy:.1f}" fill="none" stroke="#F2D8A8" stroke-width="1.4" stroke-dasharray="4 3" opacity="0.8"/>')
    for k in range(5):
        x = cx - w * 0.3 + k * w * 0.15
        tx.append(f'<path d="{blob(x, (by0 + by1) / 2 + 6 - abs(k - 2) * 1.5, 5, 4, seed + k, 0.1, 8)}" fill="#E8C890" opacity="0.8"/>')
    tx.append(shade_over(D, bd, "#1A0A04", 0.45, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(tx)}</g>')
    out.append(taper([(cx - w * 0.36, top + h * 0.32), (cx - w * 0.42, top + h * 0.55), (cx - w * 0.36, top + h * 0.78)], 6, 2, "#FFE8B8", 0.55))
    # silver mouth ring
    rw = w * 0.36
    ry_ = top + 2
    band = [(cx - rw - 3, ry_ - 2), (cx + rw + 3, ry_ - 2), (cx + rw + 1, ry_ + 18), (cx - rw - 1, ry_ + 18)]
    out.append(painted(D, band, ("#FFFFFF", "#C8CCD4", "#6A707C"), seed + 2, sdir=(0.8, 0.3), sk=0.25, angle=-90, n=14, inkw=1.6, hi=0.5))
    for k in range(11):
        x = cx - rw + 4 + k * (2 * rw - 8) / 10
        out.append(f'<path d="M {x - 3:.1f} {ry_ + 12:.1f} q 3 -6 6 0" stroke="#7A808C" stroke-width="1.2" fill="none"/>')
    # erva mound (higher at the back-left, where the bomba goes in) and foam
    erva = [(cx - rw, ry_ - 1), (cx - rw * 0.6, ry_ - 16), (cx - rw * 0.1, ry_ - 20), (cx + rw * 0.4, ry_ - 10), (cx + rw, ry_ - 2), (cx, ry_ + 6)]
    out.append(painted(D, erva, ("#A8D06A", "#5E8A2E", "#2E4A14"), seed + 3, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=12, inkw=1.4, hi=0.4))
    out.append(specks(seed, (cx - rw, ry_ - 18, cx + rw, ry_ + 2), ["#C8E08A", "#3E6A1E", "#E8F0C0"], 40, (0.8, 2), (0.6, 1)))
    out.append(f'<path d="{blob(cx + rw * 0.45, ry_ - 3, rw * 0.38, 5, seed + 4, 0.1, 12)}" fill="#E8F0C0" opacity="0.75"/>')
    # bomba
    bp = [(cx - rw * 0.25, ry_ - 8), (cx - rw * 0.1, top - h * 0.2), (cx + rw * 0.2, top - h * 0.36), (cx + rw * 0.55, top - h * 0.4)]
    out.append(taper(catmull(bp, 6), 7, 6, "#8A909C"))
    out.append(taper(catmull([(x - 1.6, y - 0.6) for x, y in bp], 6), 2.2, 1.6, "#FFFFFF", 0.85))
    out.append(ink(smooth_open(bp), "#3A3E48", 1.2, seed, 1, 0.5))
    mx, my = bp[-1]
    out.append(painted(D, blob_pts(mx + 5, my, 9, 4.5, seed + 5, 0.1, 10, 10), ("#FFF0A0", "#E8B830", "#9A6A10"), seed + 5, sk=0.2, n=3, inkw=1.2, hi=0.5))
    return "".join(out)


def chaleira(D, cx, base, w, seed):
    """Aluminium kettle (chaleira) for the chimarrão water: round body, long spout, arched handle, steam."""
    h = w * 0.62
    alu = ("#F4F6FA", "#B8BEC8", "#5A606C")
    out = [cast(D, cx + 10, base + 2, w * 0.6, 8, strength=0.45, seed=seed)]
    sp = [(cx - w * 0.36, base - h * 0.42), (cx - w * 0.56, base - h * 0.62), (cx - w * 0.7, base - h * 0.98), (cx - w * 0.64, base - h * 1.02), (cx - w * 0.5, base - h * 0.7), (cx - w * 0.3, base - h * 0.56)]
    out.append(painted(D, sp, alu, seed, sdir=(0.8, 0.4), sk=0.2, angle=-60, n=8, inkw=1.6, hi=0.5))
    body = [(cx - w * 0.44, base - h * 0.1), (cx - w * 0.46, base - h * 0.5), (cx - w * 0.3, base - h * 0.84), (cx + w * 0.3, base - h * 0.84), (cx + w * 0.46, base - h * 0.5), (cx + w * 0.44, base - h * 0.1), (cx + w * 0.34, base), (cx - w * 0.34, base)]
    out.append(painted(D, body, alu, seed + 1, sdir=(0.9, 0.3), sk=0.22, angle=-90, n=30, inkw=2, hi=0.55, hik=0.08))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    out.append(f'<g {cid}><path d="{blob(cx + w * 0.1, base - h * 0.4, w * 0.3, h * 0.2, seed, 0.2, 12)}" fill="#F8A060" opacity="0.12"/>'
               f'<path d="{blob(cx - w * 0.22, base - h * 0.5, w * 0.06, h * 0.26, seed + 1, 0.1, 10)}" fill="#FFFFFF" opacity="0.8"/></g>')
    out.append(painted(D, ell_pts(cx, base - h * 0.84, w * 0.3, h * 0.08, 0, 360, 16), alu, seed + 2, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(painted(D, blob_pts(cx, base - h * 0.92, w * 0.07, h * 0.06, seed + 3, 0.05, 10), ("#5A4A3A", "#2A1E14", "#0A0604"), seed + 3, sk=0.2, n=2, inkw=1.2, hi=0.4))
    hd = f"M {cx - w * 0.3:.1f} {base - h * 0.8:.1f} Q {cx:.1f} {base - h * 1.5:.1f} {cx + w * 0.3:.1f} {base - h * 0.8:.1f}"
    out.append(ink(hd, "#3A3E48", 6, seed, 1, 1) + ink(hd, "#C8CCD4", 2.4, seed + 1, 1, 0.9))
    out.append(steam(cx - w * 0.68, base - h * 1.06, 40, seed + 4, "#FFFFFF", 2, 14, 5, 0.65))
    return "".join(out)


def poncho_fold(D, x0, y0, x1, y1, seed):
    """A folded gaúcho poncho / pala: wool stripes and a fringe."""
    pts = rect_pts(x0, y0, x1, y1, 16, seed, 0.8)
    d = smooth_closed(pts)
    out = [f'<path d="{smooth_closed(shift(pts, 6, 6))}" fill="#2A1008" opacity="0.25"/>', f'<path d="{d}" fill="#8A1E1E"/>']
    out.append(stripes_in(D, d, (x0 - 10, y0, x1 + 10, y1), 0, [8, 5, 3, 5, 14, 5], ["#2A1410", None, "#F2D8A8", None, "#1E1410", None], seed))
    out.append(strokes(D.nid(), d, (x0, y0, x1, y1), ["#C84A3A", "#4A0E0E", "#F2D8A8"], seed, n=50, angle=0, length=(8, 20), width=(1, 2), opacity=(0.15, 0.4)))
    out.append(ink(d, INK, 1.6, seed, 1, 0.6))
    for i in range(int((x1 - x0) / 6)):
        x = x0 + 3 + i * 6
        out.append(pline([(x, y1), (x + 1, y1 + 10)], "#8A1E1E", 2, seed + i, 1, 1))
    return "".join(out)


def chapeu_campeiro(D, cx, cy, R, seed):
    """The gaúcho's black felt hat lying on the table: wide flat brim, low flat crown, a band and the chin cord."""
    felt = ("#5A4A44", "#2A201E", "#0E0A0A")
    out = [cast(D, cx + 8, cy + R * 0.18, R * 1.05, R * 0.2, strength=0.45, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, R, R * 0.3, seed, 0.02, 28), felt, seed, sdir=(0.3, 1), sk=0.15, angle=-4, n=30, inkw=1.8, inkc="#000000", hi=0.4))
    out.append(f'<path d="{blob(cx - R * 0.2, cy - R * 0.08, R * 0.6, R * 0.08, seed + 1, 0.1, 14)}" fill="#8A7A74" opacity="0.4"/>')
    cw, ch_ = R * 0.52, R * 0.42
    crown = [(cx - cw, cy - R * 0.02), (cx - cw * 0.96, cy - ch_), (cx + cw * 0.96, cy - ch_), (cx + cw, cy - R * 0.02), (cx, cy + R * 0.12)]
    out.append(painted(D, crown, felt, seed + 2, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=16, inkw=1.8, inkc="#000000", hi=0.45))
    out.append(painted(D, ell_pts(cx, cy - ch_, cw * 0.96, R * 0.1, 0, 360, 20), ("#6A5A54", "#3A2E2A", "#1A1210"), seed + 3, sk=0.15, n=6, inkw=1.4, inkc="#000000", hi=0.4))
    band = [(cx - cw * 0.99, cy - R * 0.12), (cx, cy - R * 0.02), (cx + cw * 0.99, cy - R * 0.12), (cx + cw * 0.98, cy - R * 0.24), (cx, cy - R * 0.14), (cx - cw * 0.98, cy - R * 0.24)]
    out.append(painted(D, band, ("#C8A070", "#8A5A30", "#4A2C14"), seed + 4, sk=0.15, n=4, inkw=1.2, hi=0.4))
    out.append(pline([(cx + cw * 0.7, cy - R * 0.06), (cx + cw * 1.1, cy + R * 0.2), (cx + cw * 1.6, cy + R * 0.3), (cx + cw * 1.9, cy + R * 0.18)], "#C8A070", 2.2, seed, 1, 1))
    out.append(f'<circle cx="{cx + cw * 1.9:.1f}" cy="{cy + R * 0.18:.1f}" r="3" fill="#E8C890" stroke="#6A4A2A" stroke-width="1"/>')
    return "".join(out)


@design("bah-tche")
def bah_tche():
    D = Doc2("bt")
    out = [sky(D, [(0, "#3E4E8A"), (0.38, "#C87A8A"), (0.6, "#F8B070"), (0.7, "#FCD890")], 3, 600, ["#F8C090", "#5A5A9A", "#FFE0B0"], 80)]
    out.append(soft_glow(D, 430, 374, 240, "#FFE8A0", 0.7))
    out.append(painted(D, blob_pts(430, 380, 40, 40, 460, 0.01, 24), ("#FFF6C0", "#FFD84A", "#F29A1A"), 460, sk=0.05, n=20, inkw=0, hi=0.5, edge=False))
    out.append(puff_cloud(D, 130, 290, 110, 461, ("#FFD8C0", "#F2A8A0", "#A86A8A"), op=0.85))
    out.append(puff_cloud(D, 520, 270, 80, 471, ("#FFD8C0", "#F2A8A0", "#A86A8A"), op=0.7))
    # rolling coxilhas of the pampa
    out.append(hill(D, ridge([(-20, 396), (140, 378), (300, 392), (460, 374), (620, 388)], 462, 4), 620, ("#8AB070", "#5E8A50", "#3A5A34"), 462, inkw=0, sop=(0.08, 0.2)))
    out.append(hill(D, ridge([(-20, 432), (200, 414), (400, 428), (620, 412)], 463, 3), 620, ("#B8C870", "#86A048", "#4E6A2A"), 463, inkw=1.2, inkop=0.4))
    # a lone umbu, a fence and a gaúcho on horseback on the ridge
    out.append(taper([(540, 400), (536, 378), (542, 358)], 7, 4, "#3A2A20"))
    out.append(dab_crown(D, 540, 350, 34, 22, [("#5E8A50", "#3A5A34", "#1E3A1E")], 464, n=50, size=(4, 7), inkw=0))
    for x in range(20, 280, 26):
        out.append(f'<path d="M {x} {402 - x * 0.03:.1f} l 0 -12" stroke="#3A2A20" stroke-width="2.2"/>')
    out.append(f'<path d="M 16 394 L 284 386" stroke="#3A2A20" stroke-width="1.2"/><path d="M 16 400 L 284 392" stroke="#3A2A20" stroke-width="1.2"/>')
    gx, gy = 356, 382
    horse = [(gx - 18, gy - 14), (gx + 10, gy - 16), (gx + 18, gy - 24), (gx + 24, gy - 22), (gx + 20, gy - 12), (gx + 12, gy - 6), (gx - 16, gy - 6), (gx - 22, gy - 10)]
    out.append(f'<path d="{smooth_closed(horse)}" fill="#2A1E2A"/>')
    for lx in (gx - 16, gx - 10, gx + 6, gx + 12):
        out.append(f'<path d="M {lx} {gy - 8} L {lx + 1} {gy + 2}" stroke="#2A1E2A" stroke-width="2.4"/>')
    out.append(f'<path d="M {gx - 22} {gy - 12} q -6 4 -6 12" stroke="#2A1E2A" stroke-width="2" fill="none"/>')
    out.append(f'<path d="M {gx - 6} {gy - 14} L {gx - 4} {gy - 30} L {gx + 4} {gy - 30} L {gx + 2} {gy - 14} Z" fill="#2A1E2A"/>')
    out.append(f'<ellipse cx="{gx}" cy="{gy - 33}" rx="9" ry="2.4" fill="#2A1E2A"/><path d="M {gx - 4} {gy - 34} q 4 -8 8 0" fill="#2A1E2A"/>')
    for x, y, sz in ((250, 290, 7), (272, 280, 5), (296, 292, 6)):
        out.append(bird_v(x, y, sz, "#3A2A48", 0.8))
    out.append(grass(465, (0, 440, 600, 480), ["#4E6A2A", "#6E8A3A", "#A8B860"], 80, (10, 20)))
    # rustic wooden table in front
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="#8A5A30"/>')
    out.append(wood_planks(D, 470, 600, 466, ("#C8945A", "#8A5A30", "#4A2C14"), 3))
    out.append(taper([(-10, 471), (300, 470), (610, 471)], 3, 3, "#F8C890", 0.6))
    # the pala folded on the left, the cuia centre, the chaleira right
    out.append(chapeu_campeiro(D, 124, 506, 80, 467))
    out.append(cuia(D, 270, 532, 200, 468))
    out.append(chaleira(D, 452, 532, 132, 469))
    # lettering
    out.append(letters(D, 300, 140, "Bah, tchê!", SERIF_IT, 128, "#FFF4DC", ["#FFFFFF", "#F8DCC0"], 470, max_w=440,
                       shadow="#2A2450", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 190, "BAITA SAUDADE", "#FFE07A", font=JOS, size=24, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 472)


# ================================================================ 23. jabuticaba — the fruit that grows on the trunk
def jabu(cx, cy, r, seed):
    """One glossy jabuticaba: near-black purple sphere, a soft bloom, a sharp window highlight, the little
    four-point crown where it joins the bark."""
    rnd = random.Random(seed)
    return (f'<circle cx="{cx + r * 0.18:.1f}" cy="{cy + r * 0.22:.1f}" r="{r:.1f}" fill="#1A0A10" opacity="0.3"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#3A1840"/>'
            f'<circle cx="{cx + r * 0.16:.1f}" cy="{cy + r * 0.16:.1f}" r="{r * 0.82:.1f}" fill="#1E0A22"/>'
            f'<path d="{blob(cx - r * 0.2, cy - r * 0.25, r * 0.6, r * 0.45, seed, 0.1, 10, -30)}" fill="#7A5A8A" opacity="0.35"/>'
            f'<path d="{blob(cx - r * 0.38, cy - r * 0.42, r * 0.26, r * 0.15, seed, 0.1, 8, -35)}" fill="#F2E8F8" opacity="0.9"/>'
            f'<circle cx="{cx + r * 0.45:.1f}" cy="{cy + r * 0.38:.1f}" r="{r * 0.1:.1f}" fill="#B89AC8" opacity="0.7"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#0A0410" stroke-width="1.3" opacity="0.7"/>')


@design("jabuticaba")
def jabuticaba():
    D = Doc2("jb")
    # dappled orchard light
    out = [sky(D, [(0, "#E8F0C8"), (1, "#C8DCA0")], 3, 600, ["#F4F8E0", "#A8C888", "#FFFFFF"], 90, angle=-60, sop=(0.08, 0.2))]
    out.append(blooms(470, ["#FFFFFF", "#8AB070", "#F8F0C0"], 8, (0, 0, 600, 600), (80, 160), (0.08, 0.16)))
    for k, (x, y, rx, ry) in enumerate(((60, 300, 150, 110), (560, 250, 150, 120), (520, 520, 140, 90), (60, 560, 120, 80))):
        out.append(f'<g opacity="0.55">{dab_crown(D, x, y, rx, ry, [("#C8DCA0", "#9ABC7A", "#6E9A5A")], 475 + k * 7, n=160, size=(8, 14), inkw=0)}</g>')
    # the trunk: smooth mottled bark that peels in patches, two big limbs
    bark = ("#E0D0A8", "#B09A70", "#6A5A3A")
    limbs = [([(300, 640), (296, 540), (288, 440), (270, 340), (238, 250), (214, 150)], 120, 64),
             ([(292, 470), (360, 410), (440, 350), (520, 300), (600, 280)], 66, 40),
             ([(286, 400), (220, 360), (150, 330), (70, 320), (-10, 330)], 58, 36)]
    rnd = random.Random(474)
    for k, (pts, w0, w1) in enumerate(limbs):
        cp = catmull(pts, 6)
        out.append(taper([(x + 6, y + 8) for x, y in cp], w0, w1, "#3A3020", 0.25))
        out.append(taper(cp, w0 + 4, w1 + 4, "#4A3A24"))
        out.append(taper(cp, w0, w1, bark[1]))
        out.append(taper([(x - w0 * 0.2, y) if k == 0 else (x, y - w0 * 0.18) for x, y in cp], w0 * 0.35, w1 * 0.3, bark[0], 0.7))
        out.append(taper([(x + w0 * 0.3, y) if k == 0 else (x, y + w0 * 0.28) for x, y in cp], w0 * 0.2, w1 * 0.15, bark[2], 0.5))
        for _ in range(int(len(cp) * 4)):
            x, y = rnd.choice(cp)
            ox = rnd.uniform(-0.4, 0.4) * (w0 if k == 0 else w1)
            out.append(f'<path d="{blob(x + (ox if k == 0 else 0), y + (0 if k == 0 else ox * 0.6), rnd.uniform(6, 16), rnd.uniform(4, 9), rnd.randint(1, 999), 0.25, 8, rnd.uniform(0, 180))}" '
                       f'fill="{rnd.choice(["#F0E4C8", "#8A7A54", "#C8B488", "#9A8660", "#D8C8A0"])}" opacity="0.65"/>')
    # leaves crossing the top corners behind the panel's edge
    for i in range(16):
        x, y = rnd.choice([(rnd.uniform(-20, 100), rnd.uniform(220, 300)), (rnd.uniform(500, 620), rnd.uniform(200, 280))])
        out.append(leaf_simple(D, x, y, rnd.uniform(40, 56), rnd.uniform(10, 13), rnd.uniform(0, 360), rnd.choice([MATA, VERDE]), 480 + i, vein=True, inkw=0.9))
    # a cream label panel for the lettering
    out.append(f'<path d="{hg.org_rect(64, 62, 472, 150, 471, 0.6, 20, 18)}" fill="#3A1840" opacity="0.2" transform="translate(6 8)"/>')
    panel = hg.org_rect(64, 62, 472, 150, 471, 0.6, 20, 18)
    out.append(f'<path d="{panel}" fill="#FFF8EC"/>')
    out.append(f'<path d="{hg.org_rect(74, 72, 452, 130, 473, 0.5, 20, 12)}" fill="none" stroke="#5A2A6A" stroke-width="2"/>')
    # fruit pressed straight onto the bark, in clusters, with a few white blossoms
    for k, (pts, w0, w1) in enumerate(limbs):
        cp = catmull(pts, 10)
        for j, (x, y) in enumerate(cp):
            if y < 236 or y > 560 or x < 40 or x > 560:
                continue
            ww = w0 + (w1 - w0) * j / len(cp)
            clump = math.sin(j * 0.9 + k * 2) > -0.1
            for _ in range(3 if k == 0 else 2):
                if clump and rnd.random() < 0.6:
                    off = rnd.uniform(-0.5, 0.5) * ww
                    fx, fy = (x + off, y + rnd.uniform(-6, 6)) if k == 0 else (x + rnd.uniform(-6, 6), y + off * 0.8)
                    out.append(jabu(fx, fy, rnd.uniform(11, 15), rnd.randint(1, 9999)))
            if rnd.random() < 0.1:
                bx, by = x + rnd.uniform(-ww, ww) * 0.35, y + rnd.uniform(-6, 6)
                for f in range(4):
                    a = math.radians(f * 90 + 45)
                    out.append(f'<path d="{blob(bx + math.cos(a) * 4.5, by + math.sin(a) * 4.5, 4.5, 2.6, rnd.randint(1, 99), 0.1, 6, math.degrees(a))}" fill="#FFFFFF" stroke="#C8C0A0" stroke-width="0.6"/>')
                out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.2" fill="#F2E08A"/>')
    # a bowl of picked fruit at the foot
    out.append(cast(D, 456, 540, 74, 9, strength=0.4, seed=476))
    bowl = [(386, 496), (526, 496), (512, 526), (486, 540), (426, 540), (400, 526)]
    out.append(painted(D, bowl, ("#FFFFFF", "#F2EEE6", "#B8B0A0"), 477, sk=0.15, n=10, inkw=1.6, hi=0.4))
    for x, y in ((404, 490), (428, 484), (454, 488), (480, 486), (504, 490), (440, 498), (468, 498), (418, 498), (492, 498)):
        out.append(jabu(x, y, 13, int(x + y)))
    out.append(ink(smooth_open([(388, 502), (456, 510), (524, 502)]), "#1F4FA0", 2.4, 478, 1, 0.85))
    out.append(ink(smooth_open([(394, 514), (456, 522), (518, 514)]), "#1F4FA0", 1.4, 479, 1, 0.6))
    # lettering on the panel
    out.append(letters(D, 300, 152, "jabuticaba", SERIF_IT, 104, "#4A1A5A", ["#6A2A7A", "#2E0A3A", "#8A4A9A"], 490, max_w=420,
                       shadow="#E8D0B0", soff=(0.02, 0.035), angle=-40, hi="#C8A0E0"))
    out.append(ruled(300, 190, "DIRETO DO PÉ", "#2E6A2E", font=JOS, size=20, ls=8, line_w=30, gap=12))
    return finish_b(D, out, 491)


# ================================================================ 24. ipê amarelo — a golden tree on the cerrado hill
@design("ipe-amarelo")
def ipe_amarelo():
    D = Doc2("ip")
    out = [sky(D, [(0, "#2E78C8"), (0.5, "#7EC0E8"), (0.75, "#D8F0F4")], 3, 600, ["#FFFFFF", "#5AA8E0", "#C8E8F4"], 80)]
    out.append(puff_cloud(D, 120, 280, 120, 480, ("#FFFFFF", "#FFFFFF", "#B8D0E4")))
    out.append(puff_cloud(D, 500, 250, 100, 481, ("#FFFFFF", "#FFFFFF", "#B8D0E4"), op=0.9))
    # cerrado hills: far blue-green, near golden grass
    out.append(hill(D, ridge([(-20, 400), (120, 380), (260, 394), (400, 372), (620, 390)], 482, 5), 620, ("#A8C8B0", "#84A898", "#5A8070"), 482, inkw=0, sop=(0.08, 0.2)))
    rnd = random.Random(483)
    for i in range(10):
        x = rnd.uniform(0, 600)
        out.append(dab_crown(D, x, 392 + rnd.uniform(-6, 6), rnd.uniform(10, 16), rnd.uniform(7, 10), [("#7AA070", "#4E7A4A", "#2E5A30")], 484 + i, n=14, size=(3, 5), inkw=0))
    out.append(hill(D, ridge([(-20, 470), (140, 440), (300, 430), (460, 446), (620, 466)], 495, 3), 620, ("#E8D890", "#C8B060", "#8A7A3A"), 495, inkw=1.4, inkop=0.4, angle=-6))
    out.append(grass(496, (0, 440, 600, 600), ["#A8904A", "#D8C070", "#6E7A3A", "#E8D8A0"], 180, (10, 24)))
    # carpet of fallen yellow flowers under the tree
    for _ in range(160):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = 300 + math.cos(a) * rr * 190, 470 + math.sin(a) * rr * 34
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 6), rnd.uniform(2, 4), rnd.randint(1, 9999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#FFD23A", "#F6C21C", "#FFE680", "#E8A810"])}"/>')
    # the ipê: twisted dark trunk, golden crown painted as dabs
    out.append(taper(catmull([(300, 474), (296, 420), (306, 370), (296, 320)], 6), 30, 16, "#3A2A20"))
    for pts, w0 in (([(300, 380), (250, 330), (210, 290)], 12), ([(302, 360), (350, 310), (392, 280)], 12), ([(298, 330), (290, 270), (296, 230)], 10),
                    ([(260, 340), (200, 320), (160, 300)], 8), ([(340, 320), (420, 310), (450, 296)], 8)):
        out.append(taper(catmull(pts, 5), w0, 3, "#3A2A20"))
    gold = [("#FFF2A0", "#F6C21C", "#C08A0A"), ("#FFE680", "#F2B010", "#B07A08"), ("#FFFBD0", "#FFD84A", "#D89A10")]
    out.append(soft_glow(D, 300, 270, 200, "#FFF0A0", 0.5))
    for (x, y, rx, ry, sd) in ((300, 250, 150, 96, 497), (210, 290, 80, 52, 498), (400, 280, 86, 54, 499), (300, 196, 100, 56, 500)):
        out.append(dab_crown(D, x, y, rx, ry, gold, sd, n=int(rx * ry / 18), size=(6, 12), light=(-0.5, -0.9), inkw=0))
    for _ in range(18):
        x, y = rnd.uniform(150, 450), rnd.uniform(180, 330)
        out.append(taper([(x, y), (x + rnd.uniform(-10, 10), y + rnd.uniform(4, 10))], 2.2, 1, "#3A2A20", 0.8))
    # petals drifting in the wind
    for _ in range(14):
        x, y = rnd.uniform(380, 560), rnd.uniform(300, 440)
        out.append(f'<path d="{blob(x, y, 5, 3, rnd.randint(1, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="#FFD23A"/>')
    # lettering
    out.append(letters(D, 300, 128, "ipê amarelo", SERIF_IT, 108, "#FFFDF0", ["#FFFFFF", "#E8F4FF"], 501, max_w=440,
                       shadow="#1A3E7A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 546 - 10, "O INVERNO MAIS BONITO DO BRASIL", MONO, 17, "#5A3A10", ls=2, max_w=440))
    return finish_b(D, out, 502)


# ================================================================ 25. casa de vó — azulejo barrado, filtro de barro, bolo de fubá
def azulejo(D, x, y, s, seed, blue=COBALT, ground="#F8F5EC"):
    """One hand-painted Portuguese tile: glaze ground, corner quarter-rosettes and edge half-dots that join into
    circles across neighbouring tiles, a four-petal centre flower with leaf sprigs, cobalt pooled darker at the edges."""
    rnd = random.Random(seed)
    cx, cy = x + s / 2, y + s / 2
    g = mix(ground, rnd.choice(["#FFFFFF", "#E6E0CC", "#EEF0F2"]), rnd.uniform(0.1, 0.6))
    out = [f'<path d="{hg.org_rect(x + 1, y + 1, s - 2, s - 2, seed, 0.4, 10, 2)}" fill="{g}"/>']
    b = mix(blue[1], rnd.choice([blue[0], blue[2]]), rnd.uniform(0, 0.3))

    def sector(qx, qy, r, a0, n=7):
        pts = [(qx, qy)] + [(qx + r * math.cos(math.radians(a0 + 90 * i / n)), qy + r * math.sin(math.radians(a0 + 90 * i / n))) for i in range(n + 1)]
        return jitter(pts, rnd.randint(1, 9999), s * 0.008)
    for (qx, qy, a0) in ((x, y, 0), (x + s, y, 90), (x + s, y + s, 180), (x, y + s, 270)):
        out.append(f'<path d="{pd(sector(qx, qy, s * 0.34, a0))}" fill="{b}" opacity="0.92"/>')
        out.append(f'<path d="{pd(sector(qx, qy, s * 0.22, a0))}" fill="{g}"/>')
        out.append(f'<path d="{pd(sector(qx, qy, s * 0.12, a0))}" fill="{blue[0]}"/>')
    for (mx, my, a0) in ((cx, y, 0), (x + s, cy, 90), (cx, y + s, 180), (x, cy, 270)):
        pts = [(mx + s * 0.09 * math.cos(math.radians(a0 + 180 * i / 8)), my + s * 0.09 * math.sin(math.radians(a0 + 180 * i / 8))) for i in range(9)]
        out.append(f'<path d="{pd(pts)}" fill="{b}" opacity="0.9"/>')
    for k in range(4):
        a = math.radians(45 + 90 * k)
        px, py = cx + math.cos(a) * s * 0.17, cy + math.sin(a) * s * 0.17
        out.append(f'<path d="{blob(px, py, s * 0.17, s * 0.075, seed + k, 0.08, 10, math.degrees(a))}" fill="{b}" opacity="0.95"/>')
        out.append(f'<path d="{blob(px - math.cos(a) * s * 0.02, py - math.sin(a) * s * 0.02, s * 0.09, s * 0.03, seed + k + 9, 0.08, 8, math.degrees(a))}" fill="{blue[0]}" opacity="0.8"/>')
        a2 = math.radians(90 * k)
        lx, ly = cx + math.cos(a2) * s * 0.3, cy + math.sin(a2) * s * 0.3
        out.append(taper([(cx + math.cos(a2) * s * 0.1, cy + math.sin(a2) * s * 0.1), (lx, ly)], max(1.4, s * 0.035), 1, b, 0.9))
        for sg in (-1, 1):
            a3 = a2 + sg * 0.7
            out.append(f'<path d="{blob(lx - math.cos(a2) * s * 0.06 + math.cos(a3) * s * 0.05, ly - math.sin(a2) * s * 0.06 + math.sin(a3) * s * 0.05, s * 0.05, s * 0.022, seed + k * 3 + sg, 0.1, 8, math.degrees(a3))}" fill="{b}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.07:.1f}" fill="{g}" stroke="{blue[2]}" stroke-width="{max(1.2, s * 0.025):.1f}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.025:.1f}" fill="{blue[1]}"/>')
    # glaze: a soft sheen and a crackle or two
    out.append(f'<path d="{blob(x + s * 0.3, y + s * 0.25, s * 0.25, s * 0.08, seed + 50, 0.2, 10, -35)}" fill="#FFFFFF" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    if rnd.random() < 0.25:
        px, py = x + rnd.uniform(0.2, 0.8) * s, y + rnd.uniform(0.2, 0.8) * s
        out.append(pline([(px, py), (px + rnd.uniform(-8, 8), py + rnd.uniform(4, 10)), (px + rnd.uniform(-10, 10), py + rnd.uniform(10, 18))], "#8A8A96", 0.9, seed, 0.5, 1))
    return "".join(out)


def filtro_barro(D, cx, base, h, seed):
    """The clay water filter: two stacked terracotta urns, a lid with a knob, a painted band, a little tap."""
    clay = ("#E8946A", "#B85A36", "#6A2814")
    w = h * 0.5
    out = [cast(D, cx + 8, base, w * 0.75, 9, strength=0.45, seed=seed)]
    # lower vessel
    lo = []
    for i in range(25):
        t = i / 24
        y = base - t * h * 0.5
        k = 0.78 + 0.26 * math.sin(math.pi * (0.15 + 0.8 * t))
        lo.append((cx + w / 2 * k, y))
    lower = lo + [(cx - (x - cx), y) for x, y in lo[::-1]]
    out.append(painted(D, lower, clay, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=60, inkw=2.2, hi=0.45, hik=0.07))
    # upper vessel sits on it, a touch narrower
    up = []
    for i in range(25):
        t = i / 24
        y = base - h * 0.5 - t * h * 0.38
        k = 0.7 + 0.22 * math.sin(math.pi * (0.1 + 0.85 * t))
        up.append((cx + w / 2 * k, y))
    upper = up + [(cx - (x - cx), y) for x, y in up[::-1]]
    out.append(painted(D, upper, clay, seed + 1, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=50, inkw=2.2, hi=0.45, hik=0.07))
    # joint ring, decorative bands of cream dots and a little wave
    for yy, ww in ((base - h * 0.5, w * 0.72), (base - h * 0.88, w * 0.62)):
        out.append(painted(D, ell_pts(cx, yy, ww / 2 + 4, 6, 0, 360, 20), ("#C8704A", "#8A3E20", "#4A1A0A"), seed + int(yy), sk=0.2, n=6, inkw=1.4, hi=0.3))
    for yy, ww in ((base - h * 0.27, w * 0.98), (base - h * 0.7, w * 0.86)):
        pts = [(cx - ww / 2 + ww * i / 20, yy + 5 * math.sin(i * 1.2) - 4 * abs(i / 20 - 0.5)) for i in range(21)]
        out.append(pline(pts, "#FFF0D8", 2.4, seed + int(yy), 0.8, 1))
        for i in range(1, 10):
            px = cx - ww / 2 + ww * i / 10
            out.append(f'<circle cx="{px:.1f}" cy="{yy + 12 - 6 * abs(i / 10 - 0.5):.1f}" r="2.2" fill="#FFF0D8" opacity="0.85"/>')
    # lid and knob
    lid = [(cx - w * 0.33, base - h * 0.88), (cx - w * 0.28, base - h * 0.95), (cx, base - h * 0.98), (cx + w * 0.28, base - h * 0.95), (cx + w * 0.33, base - h * 0.88)]
    out.append(painted(D, lid, clay, seed + 2, sdir=(0.8, 0.5), sk=0.2, n=10, inkw=1.8, hi=0.5))
    out.append(painted(D, blob_pts(cx, base - h, w * 0.08, w * 0.06, seed + 3, 0.05, 10), clay, seed + 3, sk=0.2, n=3, inkw=1.4, hi=0.5))
    # chrome tap on the lower vessel
    ty = base - h * 0.16
    out.append(painted(D, rect_pts(cx - w * 0.48, ty - 5, cx - w * 0.3, ty + 5, 6, seed + 4, 0.3), ("#FFFFFF", "#B8BCC8", "#5A606C"), seed + 4, sk=0.2, n=3, inkw=1.4, hi=0.6))
    out.append(painted(D, rect_pts(cx - w * 0.53, ty - 4, cx - w * 0.45, ty + 14, 6, seed + 5, 0.3), ("#FFFFFF", "#B8BCC8", "#5A606C"), seed + 5, sk=0.2, n=3, inkw=1.4, hi=0.6))
    out.append(painted(D, rect_pts(cx - w * 0.47, ty - 13, cx - w * 0.39, ty - 4, 6, seed + 6, 0.3), ("#FFFFFF", "#B8BCC8", "#5A606C"), seed + 6, sk=0.2, n=2, inkw=1.2, hi=0.6))
    out.append(f'<path d="{blob(cx - w * 0.49, ty + 21, 2.4, 3.6, seed, 0.1, 8)}" fill="#BFE6F6" stroke="#5A8AB8" stroke-width="0.8"/>')
    return "".join(out)


def bolo_fuba(D, cx, cy, rx, seed):
    """Bolo de fubá seen from a little above: golden ring cake with a hole, crackled top, darker baked sides."""
    ry = rx * 0.34
    hgt = rx * 0.62
    crust = ("#FAD27A", "#E2A440", "#9A5E1A")
    out = [cast(D, cx + 6, cy + hgt + 4, rx * 1.05, ry * 0.7, strength=0.4, seed=seed)]
    side = [(cx + rx, cy)] + ell_pts(cx, cy + hgt, rx, ry, 0, 180, 16) + [(cx - rx, cy)]
    out.append(painted(D, side, ("#E8A84A", "#B8742A", "#6A3A10"), seed, sdir=(0.9, 0.2), sk=0.16, angle=-90, n=40, inkw=2, hi=0.3))
    top = ell_pts(cx, cy, rx, ry, 0, 360, 30)
    out.append(painted(D, top, crust, seed + 1, sdir=(0.6, 0.8), sk=0.1, angle=-10, n=40, inkw=1.8, hi=0.45, hik=0.06))
    # crackled dome on top, dusting of fubá
    rnd = random.Random(seed)
    for _ in range(9):
        a = rnd.uniform(0, 6.28)
        r0 = rnd.uniform(0.35, 0.7)
        px, py = cx + math.cos(a) * rx * r0, cy + math.sin(a) * ry * r0
        out.append(pline([(px, py), (px + rnd.uniform(-12, 12), py + rnd.uniform(-3, 3)), (px + rnd.uniform(-20, 20), py + rnd.uniform(-4, 4))], "#9A5A18", 1.6, rnd.randint(1, 99), 0.55, 1))
    out.append(specks(seed, (cx - rx * 0.8, cy - ry * 0.7, cx + rx * 0.8, cy + ry * 0.7), ["#FFF2C0", "#FFFFFF"], 50, (0.6, 1.4), (0.4, 0.8)))
    hole = ell_pts(cx, cy - 1, rx * 0.2, ry * 0.26, 0, 360, 16)
    out.append(f'<path d="{smooth_closed(hole)}" fill="#7A4A1A"/>' + ink(smooth_closed(hole), INK, 1.4, seed, 1, 0.7))
    return "".join(out)


def bolo_slice(D, x, y, s, seed):
    """An upright wedge of bolo de fubá: crumbly yellow face with tiny holes, a golden-brown top crust."""
    face = [(x, y), (x + s, y + 1), (x + s * 0.92, y - s * 0.62), (x + s * 0.06, y - s * 0.64)]
    out = [cast(D, x + s * 0.55, y + 2, s * 0.7, 6, strength=0.4, seed=seed)]
    out.append(painted(D, face, ("#FFF2B0", "#F8D86E", "#D0A848"), seed, sdir=(0.6, 0.8), sk=0.1, angle=-90, n=14, inkw=1.6, hi=0.3))
    rnd = random.Random(seed)
    for _ in range(30):
        out.append(f'<path d="{blob(rnd.uniform(x + s * 0.1, x + s * 0.9), rnd.uniform(y - s * 0.52, y - s * 0.06), rnd.uniform(0.8, 2), rnd.uniform(0.6, 1.4), rnd.randint(1, 999), 0.2, 6)}" fill="#C0903A" opacity="0.65"/>')
    crust = [(x + s * 0.02, y - s * 0.6), (x + s * 0.5, y - s * 0.74), (x + s * 0.96, y - s * 0.6), (x + s * 0.92, y - s * 0.52), (x + s * 0.5, y - s * 0.62), (x + s * 0.08, y - s * 0.52)]
    out.append(painted(D, crust, ("#E8A848", "#B8742A", "#6A3A10"), seed + 1, sdir=(0.5, 0.8), sk=0.2, angle=0, n=6, inkw=1.4, hi=0.4))
    out.append(specks(seed, (x + s * 0.1, y - s * 0.7, x + s * 0.9, y - s * 0.6), ["#FFF2C0"], 10, (0.6, 1.2), (0.5, 0.9)))
    return "".join(out)


def thermos_florida(D, cx, base, h, seed, body=("#FFFDF6", "#F2EAD8", "#B8AA90"), cap=RED):
    """The flowered garrafa térmica: cream body printed with little red flowers, red pump top and handle."""
    w = h * 0.42
    out = [cast(D, cx + 8, base, w * 0.75, 8, strength=0.45, seed=seed)]
    bpts = rect_pts(cx - w / 2, base - h * 0.74, cx + w / 2, base, 14, seed, 0.5)
    bpts = [(x, y + (8 * (1 - ((x - cx) / (w / 2)) ** 2) if y > base - 2 else 0)) for x, y in bpts]
    out.append(painted(D, bpts, body, seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=30, inkw=2, hi=0.5, hik=0.06))
    bd = smooth_closed(bpts)
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(seed)
    fl = []
    for j in range(5):
        for i in range(4):
            fx = cx - w / 2 + (i + 0.5 + (j % 2) * 0.5) * w / 4 + rnd.uniform(-3, 3)
            fy = base - h * 0.7 + j * h * 0.14 + rnd.uniform(-3, 3)
            c = rnd.choice([RED[1], "#E8607A", "#F2872A"])
            for p in range(5):
                a = math.radians(p * 72 + rnd.uniform(0, 30))
                fl.append(f'<circle cx="{fx + math.cos(a) * 4:.1f}" cy="{fy + math.sin(a) * 4:.1f}" r="3.2" fill="{c}"/>')
            fl.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2" fill="#F6C21C"/>')
            fl.append(f'<path d="{blob(fx + 7, fy + 5, 4, 2, rnd.randint(1, 99), 0.1, 8, 30)}" fill="#3E8A4A"/>')
    fl.append(shade_over(D, bd, "#3A2010", 0.35, 0, 0, 1, 0, 0.45))
    fl.append(light_over(D, bd, "#FFFFFF", 0.4, 0, 0, 1, 0, 0.3))
    out.append(f'<g {cid}>{"".join(fl)}</g>')
    # shoulder, pump top, spout and handle
    sh = rect_pts(cx - w * 0.5, base - h * 0.82, cx + w * 0.5, base - h * 0.72, 10, seed + 1, 0.4)
    out.append(painted(D, sh, cap, seed + 1, sdir=(1, 0.3), sk=0.2, angle=0, n=8, inkw=1.6, hi=0.45))
    top = [(cx - w * 0.36, base - h * 0.82), (cx - w * 0.3, base - h * 0.95), (cx + w * 0.3, base - h * 0.95), (cx + w * 0.36, base - h * 0.82)]
    out.append(painted(D, top, cap, seed + 2, sdir=(1, 0.3), sk=0.2, angle=-90, n=8, inkw=1.6, hi=0.45))
    out.append(painted(D, blob_pts(cx, base - h * 0.97, w * 0.2, h * 0.035, seed + 3, 0.05, 12), ("#FFFFFF", "#E8E4DC", "#9A948A"), seed + 3, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(painted(D, [(cx - w * 0.3, base - h * 0.9), (cx - w * 0.56, base - h * 0.9), (cx - w * 0.6, base - h * 0.86), (cx - w * 0.3, base - h * 0.84)], cap, seed + 4, sk=0.2, n=3, inkw=1.4, hi=0.4))
    hd = f"M {cx + w * 0.5:.1f} {base - h * 0.66:.1f} q {w * 0.42:.1f} {h * 0.04:.1f} {w * 0.36:.1f} {h * 0.25:.1f} q {-w * 0.04:.1f} {h * 0.16:.1f} {-w * 0.36:.1f} {h * 0.2:.1f}"
    out.append(ink(hd, cap[2], 9, seed, 1, 1) + ink(hd, cap[1], 5.5, seed + 1, 1, 1) + ink(hd, cap[0], 1.6, seed + 2, 1, 0.8))
    return "".join(out)


def doily(D, cx, cy, rx, ry, seed, bg="#8A5A30"):
    """Crochet doily (toalhinha de crochê) lying flat: scalloped edge, rings of holes, a centre rosette."""
    out = []
    sc = []
    n = 26
    for i in range(n):
        a = 2 * math.pi * i / n
        sc.append(f'<ellipse cx="{cx + math.cos(a) * rx:.1f}" cy="{cy + math.sin(a) * ry:.1f}" rx="{rx * 0.1:.1f}" ry="{ry * 0.12:.1f}" fill="#FFFDF4"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx + 4, cy + 5, rx * 1.05, ry * 1.06, 0, 360, 30))}" fill="#3A2010" opacity="0.18"/>')
    out.append("".join(sc))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 30))}" fill="#FFFDF4"/>')
    for k, (fr, m) in enumerate(((0.9, 26), (0.72, 20), (0.54, 16), (0.36, 12))):
        for i in range(m):
            a = 2 * math.pi * (i + 0.5 * (k % 2)) / m
            out.append(f'<ellipse cx="{cx + math.cos(a) * rx * fr:.1f}" cy="{cy + math.sin(a) * ry * fr:.1f}" rx="{rx * 0.035:.1f}" ry="{ry * 0.05:.1f}" fill="{bg}" opacity="0.55"/>')
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx * (fr - 0.09), ry * (fr - 0.09), 0, 360, 30))}" fill="none" stroke="#D8CCB0" stroke-width="1.2" stroke-dasharray="3 3"/>')
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(f'<circle cx="{cx + math.cos(a) * rx * 1.04:.1f}" cy="{cy + math.sin(a) * ry * 1.04:.1f}" r="1.4" fill="{bg}" opacity="0.5"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx * 1.08, ry * 1.1, 0, 360, 40)), "#B8A888", 1.0, seed, 1, 0.5))
    return "".join(out)


@design("casa-de-vo")
def casa_de_vo():
    D = Doc2("cvo")
    # upper wall: warm lime-wash
    out = [sky(D, [(0, "#FBF1DC"), (1, "#F2E2C2")], 3, 600, ["#FFFFFF", "#E8D2A8", "#FFF8E8"], 90, angle=-75, sop=(0.06, 0.16))]
    out.append(blooms(500, ["#E8C890", "#FFFFFF"], 6, (0, 0, 600, 260), (90, 160), (0.06, 0.12)))
    # azulejo barrado
    s = 60
    y0 = 250
    for j in range(4):
        for i in range(10):
            out.append(azulejo(D, i * s, y0 + j * s, s, 600 + j * 17 + i))
    out.append(f'<rect x="0" y="{y0}" width="600" height="{4 * s}" fill="{D.lin([(0, "#0C2060", 0), (0.6, "#0C2060", 0), (1, "#0C2060", 0.22)])}"/>')
    for i in range(11):
        out.append(f'<path d="M {i * s} {y0} L {i * s + 0.6} {y0 + 4 * s}" stroke="#C8C4B8" stroke-width="1.6" opacity="0.8"/>')
    for j in range(5):
        out.append(f'<path d="M 0 {y0 + j * s} L 600 {y0 + j * s + 0.5}" stroke="#C8C4B8" stroke-width="1.6" opacity="0.8"/>')
    # frieze line on top of the tiles
    out.append(painted(D, rect_pts(-10, y0 - 12, 610, y0 + 2, 30, 640, 0.6), COBALT, 640, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.4, hi=0.3))
    # a little window with lace curtain? no: a pano de prato on a hook between the objects
    # wooden table
    out.append(f'<path d="M -10 486 L 610 486 L 610 610 L -10 610 Z" fill="#8A5A30"/>')
    out.append(wood_planks(D, 486, 600, 641, WOOD, 3))
    out.append(f'<rect x="0" y="486" width="600" height="10" fill="#3A2010" opacity="0.3"/>')
    out.append(taper([(-10, 486), (300, 487), (610, 486)], 3, 3, "#F2C890", 0.6))
    # filtro de barro (left), garrafa florida (right), bolo de fubá on the doily (centre), a cup
    out.append(filtro_barro(D, 130, 510, 252, 642))
    out.append(doily(D, 318, 512, 112, 34, 643))
    out.append(thermos_florida(D, 486, 512, 206, 644))
    out.append(painted(D, ell_pts(318, 500, 92, 22, 0, 360, 28), WHITE, 645, sdir=(0.4, 1), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(ink(smooth_open(ell_pts(318, 501, 84, 18, 15, 165, 14)), COBALT[1], 2.2, 646, 1, 0.85))
    out.append(bolo_fuba(D, 318, 438, 82, 647))
    out.append(steam(318, 400, 50, 648, "#FFFFFF", 2, 26, 6, 0.7))
    out.append(cup_saucer(D, 410, 552, 46, 649, rim=COBALT))
    out.append(steam(410, 512, 34, 650, "#FFFFFF", 2, 16, 5, 0.6))
    out.append(bolo_slice(D, 196, 556, 52, 651))
    # lettering
    out.append(letters(D, 300, 148, "casa de vó", SERIF_IT, 116, "#1E3F9A", ["#2E5AB8", "#0C2060", "#4A72C8"], 652, max_w=460,
                       shadow="#F2D6A8", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 206, "TEM CAFÉ, TEM BOLO, TEM COLO", "#A8461E", font=JOS, size=22, ls=3, line_w=26, gap=12, max_w=400))
    return finish_b(D, out, 653)


# ================================================================ 26. guaraná — the glass, the fizz and the fruit that looks back at you
def guarana_fruit(D, cx, cy, r, seed, open_=0.0, rot_=0):
    """A guaraná capsule: glossy red-orange; open_ > 0 splits it to show the white aril and the black seed (the 'eye')."""
    out = []
    rnd = random.Random(seed)
    red = ("#FF8A5A", "#E0331E", "#8A1208")
    if open_ <= 0:
        out.append(painted(D, blob_pts(cx, cy, r, r * 1.05, seed, 0.04, 14, rot_), red, seed, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=6, inkw=1.4, hi=0.5, hik=0.1))
        out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.4, r * 0.25, r * 0.14, seed, 0.1, 8, -40)}" fill="#FFFFFF" opacity="0.6"/>')
        out.append(pline([(cx, cy - r * 0.9), (cx + r * 0.08, cy), (cx, cy + r * 0.9)], red[2], 1.2, seed, 0.5, 1))
        return "".join(out)
    # split husk: two red valves peeled back
    for sg in (-1, 1):
        a = math.radians(rot_ + sg * 55)
        px, py = cx + math.cos(a - math.pi / 2) * r * 0.55 * open_, cy + math.sin(a - math.pi / 2) * r * 0.2
        out.append(painted(D, blob_pts(cx + sg * r * 0.55, cy + r * 0.1, r * 0.62, r * 1.0, seed + sg, 0.06, 12, sg * 28 + rot_), red, seed + sg,
                           sdir=(0.6, 0.7), sk=0.2, angle=-60, n=5, inkw=1.4, hi=0.45))
    out.append(painted(D, blob_pts(cx, cy, r * 0.78, r * 0.86, seed + 5, 0.04, 14), ("#FFFFFF", "#F8F2E6", "#C8BCA8"), seed + 5, sdir=(0.5, 0.8), sk=0.15, n=4, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(cx, cy + r * 0.05, r * 0.46, r * 0.48, seed + 6, 0.04, 12), ("#4A3A3A", "#1A1010", "#000000"), seed + 6, sdir=(0.5, 0.8), sk=0.2, n=3, inkw=1.2, hi=0.3))
    out.append(f'<path d="{blob(cx - r * 0.16, cy - r * 0.16, r * 0.14, r * 0.1, seed, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


def guarana_leaf(D, x, y, L, ang, seed, pal=VERDE):
    return leaf_simple(D, x, y, L, L * 0.24, ang, pal, seed, inkw=1.3)


def soda_glass(D, cx, base, h, seed):
    """Tall tumbler of guaraná: amber fizz, foam, ice cubes, rising bubbles, condensation."""
    wt, wb = h * 0.5, h * 0.4
    top = base - h
    glass = [(cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2, base - 6), (cx + wb / 2 - 6, base), (cx - wb / 2 + 6, base), (cx - wb / 2, base - 6)]
    gd = pd(glass)
    out = [cast(D, cx + 10, base + 2, wt * 0.7, 10, strength=0.4, seed=seed)]
    out.append(f'<ellipse cx="{cx + 18:.1f}" cy="{base + 4:.1f}" rx="{wt * 0.5:.1f}" ry="8" fill="#F2A040" opacity="0.25"/>')
    out.append(f'<path d="{gd}" fill="#FFF8EC" opacity="0.4"/>')
    lt_ = top + h * 0.12
    drink = [(cx - wt / 2 + (wt - wb) / 2 * 0.12 + 3, lt_), (cx + wt / 2 - (wt - wb) / 2 * 0.12 - 3, lt_), (cx + wb / 2 - 3, base - 8), (cx + wb / 2 - 9, base - 4), (cx - wb / 2 + 9, base - 4), (cx - wb / 2 + 3, base - 8)]
    dd = pd(drink)
    g = D.lin([(0, "#F6B04A"), (0.5, "#E07A1E"), (1, "#A8460E")])
    out.append(f'<path d="{dd}" fill="{g}"/>')
    cid = D.clip(f'<path d="{dd}"/>')
    rnd = random.Random(seed)
    inner = []
    # ice cubes
    for k, (ix, iy, s_, a) in enumerate(((cx - 22, lt_ + 26, 38, 12), (cx + 20, lt_ + 18, 34, -18), (cx - 4, lt_ + 66, 36, 30), (cx + 18, lt_ + 104, 30, -8))):
        cube = rot(rect_pts(ix - s_ / 2, iy - s_ / 2, ix + s_ / 2, iy + s_ / 2, 8, seed + k, 1.5), ix, iy, a)
        inner.append(f'<path d="{smooth_closed(cube)}" fill="#FFE2A8" opacity="0.55"/>')
        inner.append(f'<path d="{smooth_closed(cube)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>')
        inner.append(taper([(ix - s_ * 0.3, iy - s_ * 0.25), (ix + s_ * 0.1, iy - s_ * 0.32)], 3, 1, "#FFFFFF", 0.8))
    for _ in range(70):
        bx, by = rnd.uniform(cx - wt / 2, cx + wt / 2), rnd.uniform(lt_ + 10, base - 6)
        r_ = rnd.uniform(1, 3.4)
        inner.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r_:.1f}" fill="none" stroke="#FFF2D0" stroke-width="1" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    inner.append(strokes(D.nid(), dd, (cx - wt / 2, lt_, cx + wt / 2, base), ["#FFD080", "#B8500E", "#F6A040"], seed, n=40, angle=-90, length=(20, 60), width=(2, 5), opacity=(0.12, 0.3)))
    inner.append(shade_over(D, dd, "#5A1A04", 0.45, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # foam head
    foam = blob_pts(cx, lt_ + 2, wt / 2 - 5, 9, seed + 1, 0.08, 18)
    out.append(painted(D, foam, ("#FFFDF4", "#FFE8C0", "#E8B878"), seed + 1, sdir=(0.3, 1), sk=0.2, angle=0, n=12, inkw=0, hi=0.6))
    for _ in range(16):
        out.append(f'<circle cx="{rnd.uniform(cx - wt / 2 + 8, cx + wt / 2 - 8):.1f}" cy="{rnd.uniform(lt_ - 6, lt_ + 6):.1f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    for _ in range(8):
        out.append(f'<circle cx="{rnd.uniform(cx - wt / 2, cx + wt / 2):.1f}" cy="{rnd.uniform(top - 30, lt_ - 8):.1f}" r="{rnd.uniform(1.2, 2.6):.1f}" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.8"/>')
    # glass walls: rim, thick base, highlights, condensation drops
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, wt / 2, 7, 0, 360, 24))}" fill="none" stroke="#FFFFFF" stroke-width="2.4" opacity="0.85"/>')
    out.append(f'<path d="{pd([(cx - wb / 2 + 2, base - 12), (cx + wb / 2 - 2, base - 12), (cx + wb / 2 - 6, base), (cx - wb / 2 + 6, base)])}" fill="#FFF2DC" opacity="0.45"/>')
    out.append(taper([(cx - wt / 2 + 12, top + 16), (cx - wb / 2 + 10, base - 20)], 7, 3, "#FFFFFF", 0.55))
    out.append(taper([(cx + wt / 2 - 14, top + 30), (cx + wb / 2 - 12, top + h * 0.45)], 3, 1, "#FFFFFF", 0.6))
    for _ in range(14):
        t = rnd.random()
        dx = rnd.uniform(-0.42, 0.42)
        px = cx + dx * (wt + (wb - wt) * t)
        py = top + 20 + t * (h - 40)
        out.append(f'<path d="{smooth_closed(drop_shape(px, py, 2.4, 5))}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(ink(smooth_closed(glass), "#8A5A30", 1.6, seed, 1, 0.55))
    return "".join(out)


@design("guarana")
def guarana():
    D = Doc2("gu")
    out = [sky(D, [(0, "#1E6A3A"), (0.55, "#2E8A46"), (1, "#14502A")], 3, 600, ["#3E9A50", "#0E4A24", "#5AB060"], 110, angle=-70, sop=(0.08, 0.22))]
    out.append(soft_glow(D, 360, 330, 290, "#FFE89A", 0.55))
    # jungle leaves at the edges, dark
    for k, (x, y, a, L_) in enumerate(((-10, 260, -20, 170), (610, 230, 200, 160), (-20, 560, -40, 200), (620, 520, 210, 190), (560, -10, 120, 140))):
        out.append(banana_leaf(D, x, y, a, L_, 34, 700 + k, ("#3E8A4A", "#1E5A2E", "#0C3418"), splits=0))
    # table edge
    out.append(f'<path d="M -10 486 Q 300 478 610 486 L 610 610 L -10 610 Z" fill="#8A5A30"/>')
    out.append(wood_planks(D, 486, 600, 705, WOOD, 3))
    out.append(taper([(-10, 486), (300, 481), (610, 486)], 3, 3, "#F2C890", 0.7))
    # the glass
    out.append(soda_glass(D, 352, 512, 260, 706))
    # straw
    out.append(taper([(380, 290), (398, 244), (408, 224)], 9, 9, "#FFFFFF"))
    for k in range(4):
        t0 = 0.2 + k * 0.2
        x_, y_ = 380 + (408 - 380) * t0, 290 + (224 - 290) * t0
        out.append(taper([(x_ - 4, y_ + 3), (x_ + 4, y_ - 4)], 4, 4, "#E0331E", 0.9))
    out.append(ink(smooth_open([(376, 292), (394, 244), (404, 224)]), INK, 1.2, 707, 1, 0.5))
    # a sprig of guaraná fruit arching in from the left
    stem_ = catmull([(-10, 250), (70, 262), (140, 300), (190, 350), (214, 400)], 6)
    out.append(taper(stem_, 9, 4, "#6A4A2A"))
    for k, (x, y, L_, a) in enumerate(((40, 256, 100, -120), (96, 274, 110, -60), (150, 312, 96, -20), (60, 262, 92, 150), (120, 290, 90, 100), (184, 344, 70, 20))):
        out.append(guarana_leaf(D, x, y, L_, a, 710 + k))
    fruits = [(200, 384, 20, 0), (232, 398, 21, 1), (176, 410, 20, 1), (214, 428, 21, 0), (248, 436, 19, 0), (190, 448, 20, 1),
              (226, 464, 20, 1), (160, 446, 18, 0), (204, 488, 19, 0), (240, 500, 17, 1)]
    for k, (x, y, r, o) in enumerate(fruits):
        out.append(guarana_fruit(D, x, y, r, 720 + k, open_=o, rot_=(k * 13) % 30 - 15))
    # two loose fruits by the glass
    out.append(guarana_fruit(D, 470, 524, 17, 740, 1, 10))
    out.append(guarana_fruit(D, 504, 512, 15, 741, 0))
    # lettering
    out.append(letters(D, 300, 156, "guaraná", SERIF_IT, 132, "#FFF4DC", ["#FFFFFF", "#FFE8B0", "#F8D890"], 742, max_w=440,
                       shadow="#0C3418", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 206, "BEM GELADINHO", "#FFD23A", font=JOS, size=24, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 743)


# ================================================================ 27. mãe é mãe — an embroidery hoop on chita
def stitched(D, x, y, s, font, size, col, seed, max_w=400, ls=0, stitch_ang=60):
    """Lettering embroidered in satin stitch: thread colour, angled stitch lines clipped to the glyphs, a darker
    back-stitched outline and a soft shadow on the linen."""
    fs = fit_size(s, font, size, max_w, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    xx = x + ls / 2 if ls else x
    t = f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="middle" {font} font-size="{fs}"{lsa}>{esc(s)}</text>'
    out = [f'<g fill="#5A3A20" opacity="0.25" transform="translate(1.5 2.5)">{t}</g>', f'<g fill="{col[1]}">{t}</g>']
    uid = D.nid()
    W = measure(s, font, fs, ls)
    rnd = random.Random(seed)
    st = []
    step = max(2.6, fs * 0.035)
    a = math.radians(stitch_ang)
    L = fs * 2
    k = -W
    while k < W + fs:
        px = x - W / 2 + k
        c = rnd.choice([col[0], col[2], col[0]])
        st.append(f'<path d="M {px:.1f} {y + fs * 0.3:.1f} l {L * math.cos(a):.1f} {-L * math.sin(a):.1f}" stroke="{c}" stroke-width="{step * 0.45:.1f}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
        k += step
    out.append(f'<clipPath id="{uid}">{t}</clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    out.append(f'<g fill="none" stroke="{col[2]}" stroke-width="{max(1.4, fs * 0.018):.1f}" stroke-dasharray="{fs * 0.05:.1f} {fs * 0.02:.1f}" opacity="0.8">{t}</g>')
    return "".join(out)


def lazy_daisy(cx, cy, r, col, seed, n=6, center="#F6C21C", rot_=0, w=2.4):
    """An embroidered lazy-daisy flower: looped petal stitches and a French-knot centre."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = math.radians(rot_ + i * 360 / n + rnd.uniform(-6, 6))
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(f'<path d="{blob(px, py, r * 0.42, r * 0.17, seed + i, 0.05, 10, math.degrees(a))}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.97:.1f}" cy="{cy + math.sin(a) * r * 0.97:.1f}" r="{w * 0.45:.1f}" fill="{col}"/>')
    for i in range(5):
        a = rnd.uniform(0, 6.28)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.1:.1f}" cy="{cy + math.sin(a) * r * 0.1:.1f}" r="{max(1.6, r * 0.12):.1f}" fill="{center}" stroke="{dk(center, 0.3)}" stroke-width="0.8"/>')
    return "".join(out)


def stitch_leaf(x, y, L, ang, col, seed, w=2.2):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    out = []
    for i in range(1, 8):
        t = i / 8
        hw = L * 0.28 * math.sin(math.pi * t)
        px, py = x + ux * L * t, y + uy * L * t
        for sg in (-1, 1):
            out.append(f'<path d="M {px:.1f} {py:.1f} L {px + ux * L * 0.08 + sg * nx * hw:.1f} {py + uy * L * 0.08 + sg * ny * hw:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
    out.append(f'<path d="M {x:.1f} {y:.1f} L {x + ux * L:.1f} {y + uy * L:.1f}" stroke="{dk(col, 0.25)}" stroke-width="{w * 0.8:.1f}" stroke-linecap="round"/>')
    return "".join(out)


@design("mae-e-mae")
def mae_e_mae():
    D = Doc2("me")
    # chita (Brazilian floral cotton) stretched behind the hoop
    out = [chita(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", 150, "#D8243A", ("#F6C21C", "#2E6AC8", "#FFFFFF", "#F28AB0"), "#1F8A4C", 750, rot_=-8)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0.08), (1, "#000000", 0.3)])}"/>')
    cx, cy, R = 300, 322, 198
    # hoop shadow, linen, fabric weave
    out.append(f'<circle cx="{cx + 8}" cy="{cy + 12}" r="{R + 14}" fill="#3A0A0A" opacity="0.35"/>')
    lin = smooth_closed(blob_pts(cx, cy, R, R, 751, 0.004, 40))
    out.append(f'<path d="{lin}" fill="#F8F0DE"/>')
    weave = D.pattern(6, 6, '<path d="M 0 1.5 L 6 1.5 M 1.5 0 L 1.5 6" stroke="#C8B48A" stroke-width="0.7" opacity="0.5"/>')
    out.append(f'<path d="{lin}" fill="{weave}"/>')
    out.append(f'<path d="{lin}" fill="{D.rad([(0, "#FFFFFF", 0.5), (0.7, "#FFFFFF", 0), (1, "#8A6A3A", 0.25)], 0.4, 0.35, 0.7)}"/>')
    # wooden hoop: two rings and the brass screw clamp at the top
    for rr, ww, c in ((R + 10, 22, "#C8925A"), (R + 10, 14, "#E2B07A")):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{c}" stroke-width="{ww}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 3}" fill="none" stroke="#8A5A2A" stroke-width="2.4" opacity="0.8"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 21}" fill="none" stroke="#6A3E18" stroke-width="2.4" opacity="0.8"/>')
    out.append(strokes(D.nid(), f"M {cx - R - 22} {cy} a {R + 22} {R + 22} 0 1 0 {2 * R + 44} 0 a {R + 22} {R + 22} 0 1 0 {-2 * R - 44} 0 Z M {cx - R} {cy} a {R} {R} 0 1 1 {2 * R} 0 a {R} {R} 0 1 1 {-2 * R} 0 Z",
                       (cx - R - 24, cy - R - 24, cx + R + 24, cy + R + 24), ["#F2C890", "#8A5A2A", "#FFE0B0"], 752, n=160, angle=0, length=(10, 30), width=(1, 2.4), opacity=(0.2, 0.5),
                       clip_extra=' clip-rule="evenodd"'))
    out.append(painted(D, rect_pts(cx - 26, cy - R - 40, cx + 26, cy - R - 12, 8, 753, 0.4), ("#FFF0A0", "#D8A830", "#7A5A10"), 753, sk=0.2, angle=0, n=8, inkw=1.6, hi=0.55))
    out.append(painted(D, rect_pts(cx - 8, cy - R - 58, cx + 8, cy - R - 38, 6, 754, 0.3), ("#FFF0A0", "#D8A830", "#7A5A10"), 754, sk=0.2, n=4, inkw=1.4, hi=0.55))
    out.append(painted(D, blob_pts(cx, cy - R - 62, 16, 8, 755, 0.05, 12), ("#FFF0A0", "#D8A830", "#7A5A10"), 755, sk=0.2, n=4, inkw=1.4, hi=0.55))
    # embroidered wreath: vine, leaves, lazy-daisies, little heart
    rnd = random.Random(756)
    vine = [(cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176) for a in range(232, 309, 6)]
    out.append(f'<path d="{smooth_open(vine)}" fill="none" stroke="#3E8A4A" stroke-width="2.6" stroke-dasharray="6 3"/>')
    for k, a in enumerate((236, 246, 258, 282, 294, 304)):
        x, y = cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176
        out.append(stitch_leaf(x, y, 24, a + (60 if k % 2 else -60) + 90, "#3E9A50", 757 + k))
    for k, (a, col) in enumerate(((240, "#E8507A"), (270, "#F2872A"), (300, "#1F6AC8"))):
        x, y = cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176
        out.append(lazy_daisy(x, y, 20 if k != 1 else 24, col, 770 + k, n=7, rot_=k * 20))
    vine2 = [(cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176) for a in range(60, 121, 6)]
    out.append(f'<path d="{smooth_open(vine2)}" fill="none" stroke="#3E8A4A" stroke-width="2.6" stroke-dasharray="6 3"/>')
    for k, a in enumerate((64, 80, 100, 116)):
        x, y = cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176
        out.append(stitch_leaf(x, y, 22, a + (60 if k % 2 else -60) + 90, "#3E9A50", 780 + k))
    for k, (a, col) in enumerate(((72, "#F6C21C"), (108, "#E8507A"))):
        x, y = cx + math.cos(math.radians(a)) * 176, cy + math.sin(math.radians(a)) * 176
        out.append(lazy_daisy(x, y, 18, col, 790 + k, n=6, center="#FFFFFF" if col == "#F6C21C" else "#F6C21C"))
    out.append(lazy_daisy(cx, cy + 176, 15, "#1F6AC8", 793, n=6))
    # the words, satin-stitched
    out.append(stitched(D, cx, 296, "mãe", SERIF_IT, 150, ("#F27A98", "#D8204A", "#8A0A28"), 795, max_w=290))
    out.append(stitched(D, cx, 374, "é mãe", SERIF_IT, 90, ("#F27A98", "#D8204A", "#8A0A28"), 796, max_w=290))
    hp = heart_d(cx, 404, 11)
    out.append(f'<path d="{smooth_closed(hp)}" fill="#D8204A"/>')
    out.append(f'<path d="{smooth_closed(hp)}" fill="none" stroke="#8A0A28" stroke-width="1.4" stroke-dasharray="3 2"/>')
    out.append(label(cx, 444, "COLO DE MÃE NÃO TEM IGUAL", JOS, 19, "#2E6A40", ls=2, max_w=290))
    # a loose thread and the needle resting on the linen
    out.append(pline([(cx + 96, 488), (cx + 130, 480), (cx + 150, 456), (cx + 156, 430)], "#D8204A", 1.8, 797, 0.9, 1))
    out.append(taper([(cx + 154, 438), (cx + 170, 382)], 3.2, 1.2, "#8A909C"))
    out.append(taper([(cx + 153, 436), (cx + 167, 386)], 1, 0.6, "#FFFFFF", 0.8))
    return finish_b(D, out, 798)


# ================================================================ 28. fitinha do Bonfim — wishes tied to the church railing
FITA_COLS = [("#7ED08A", "#1F9A4C", "#0E5A2A"), ("#FFE58A", "#F6C21C", "#B8820A"), ("#7AA6E8", "#1F5AC0", "#0E2E70"),
             ("#FF8A7A", "#E0302A", "#8A1010"), ("#FFB0D0", "#EC5A9A", "#A0245A"), ("#FFFFFF", "#F4F0E6", "#B8B0A0"),
             ("#C0A0F0", "#7A4AC8", "#3E1E7A"), ("#FFC07A", "#F2872A", "#A8500E"), ("#A8E8F0", "#3EBAD8", "#1A6A88")]


def fita(D, x, y, L, w, pal, seed, wind=1.0, amp=10, waves=1.6, ph=0.0, text_marks=True):
    """A Bonfim ribbon hanging from (x, y): a thin satin strip that twists as it flutters (width shrinks where
    it turns edge-on, the back face shows darker), forked tail, faint printed lettering."""
    rnd = random.Random(seed)
    n = 40
    spine = []
    for i in range(n + 1):
        t = i / n
        sx = x + wind * L * 0.28 * t ** 1.6 + amp * math.sin(2 * math.pi * waves * t + ph) * t
        sy = y + L * t * (1 - 0.12 * wind * t)
        spine.append((sx, sy))
    segs = []
    for i in range(n):
        (ax, ay), (bx, by) = spine[i], spine[i + 1]
        tw = math.cos(2 * math.pi * waves * 0.8 * i / n + ph * 1.3)
        ww = w * (0.25 + 0.75 * abs(tw)) / 2
        ww2 = w * (0.25 + 0.75 * abs(math.cos(2 * math.pi * waves * 0.8 * (i + 1) / n + ph * 1.3))) / 2
        col = pal[1] if tw > 0 else dk(pal[1], 0.18)
        segs.append(f'<path d="M {ax - ww:.1f} {ay:.1f} L {ax + ww:.1f} {ay:.1f} L {bx + ww2:.1f} {by + 0.6:.1f} L {bx - ww2:.1f} {by + 0.6:.1f} Z" fill="{col}"/>')
        if tw > 0.55 and i % 2 == 0:
            segs.append(f'<path d="M {ax - ww * 0.55:.1f} {ay:.1f} L {bx - ww2 * 0.55:.1f} {by:.1f}" stroke="{pal[0]}" stroke-width="{max(1.2, w * 0.14):.1f}" opacity="0.7"/>')
        if text_marks and tw > 0.7 and i % 3 == 1 and 4 < i < n - 4:
            segs.append(f'<path d="M {ax + ww * 0.2:.1f} {ay + 1:.1f} L {bx + ww2 * 0.2:.1f} {by - 1:.1f}" stroke="{pal[2]}" stroke-width="1.4" stroke-dasharray="2 1.5" opacity="0.6"/>')
    ex, ey = spine[-1]
    px, py = spine[-2]
    segs.append(f'<path d="M {px - w / 2:.1f} {py:.1f} L {px + w / 2:.1f} {py:.1f} L {ex + w / 2 + 1:.1f} {ey + 7:.1f} L {ex:.1f} {ey + 1:.1f} L {ex - w / 2 + 1:.1f} {ey + 7:.1f} Z" fill="{pal[1]}"/>')
    edge = smooth_open([(sx - 0.0, sy) for sx, sy in spine])
    out = [f'<path d="{edge}" fill="none" stroke="#3A2010" stroke-width="{w * 0.9:.1f}" opacity="0.12" transform="translate(5 6)"/>']
    out.append("".join(segs))
    out.append(ink(edge, pal[2], 0.9, seed, 1, 0.35))
    return "".join(out)


def iron_rail(D, x0, x1, y, h, seed, col=("#5A8AD8", "#1E4A9A", "#0C2458")):
    out = [painted(D, rect_pts(x0, y - h / 2, x1, y + h / 2, 30, seed, 0.6), col, seed, sdir=(0, 1), sk=0.25, angle=0, n=int((x1 - x0) / 8), inkw=1.8, hi=0.5, hik=0.15)]
    out.append(taper([(x0, y - h * 0.25), (x1, y - h * 0.25)], h * 0.18, h * 0.18, "#FFFFFF", 0.35))
    return "".join(out)


@design("fitinha-do-bonfim")
def fitinha_do_bonfim():
    D = Doc2("fb")
    # whitewashed church wall in warm Bahia light, a strip of blue sky above
    out = [sky(D, [(0, "#FFF6E6"), (1, "#F6E6C8")], 3, 600, ["#FFFFFF", "#F2DCB8", "#FFF8EC"], 90, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(800, ["#F2D0A0", "#FFFFFF", "#E8C8A0"], 7, (0, 0, 600, 600), (90, 170), (0.05, 0.1)))
    out.append(soft_glow(D, 300, 380, 300, "#FFF2C8", 0.6))
    # railing: posts, scrolls, lower rail
    rail_y = 262
    for x in range(30, 600, 60):
        out.append(painted(D, rect_pts(x - 5, rail_y, x + 5, 620, 20, x, 0.5), ("#5A8AD8", "#1E4A9A", "#0C2458"), x, sdir=(1, 0), sk=0.3, angle=-90, n=10, inkw=1.4, hi=0.5))
    for x in range(60, 600, 60):
        sc = [(x, rail_y + 40), (x - 12, rail_y + 22), (x - 2, rail_y + 10), (x + 6, rail_y + 18), (x, rail_y + 26)]
        out.append(pline(sc, "#1E4A9A", 4, x, 1, 1))
        sc2 = [(x, rail_y + 40), (x + 12, rail_y + 58), (x + 2, rail_y + 70), (x - 6, rail_y + 62), (x, rail_y + 54)]
        out.append(pline(sc2, "#1E4A9A", 4, x + 1, 1, 1))
    out.append(iron_rail(D, -10, 610, rail_y + 100, 12, 801))
    out.append(iron_rail(D, -10, 610, rail_y, 16, 802))
    # the ribbons, knotted on the top rail and fluttering in the breeze
    rnd = random.Random(803)
    xs = []
    x = 18
    while x < 600:
        xs.append(x)
        x += rnd.uniform(16, 24)
    order = list(range(len(xs)))
    rnd.shuffle(order)
    for k in order:
        x = xs[k]
        pal = FITA_COLS[k % len(FITA_COLS)]
        L = rnd.uniform(130, 260)
        gust = 0.6 + 0.6 * math.sin(x / 90 + 1.2)
        out.append(fita(D, x, rail_y + 6, L, rnd.uniform(11, 14), pal, 810 + k, wind=gust + rnd.uniform(-0.25, 0.25), amp=rnd.uniform(8, 22),
                        waves=rnd.uniform(0.9, 2.2), ph=rnd.uniform(0, 6.28)))
    for k, x in enumerate(xs):
        pal = FITA_COLS[k % len(FITA_COLS)]
        out.append(painted(D, blob_pts(x, rail_y + 1, 7.5, 10, 900 + k, 0.1, 10), pal, 900 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
        out.append(taper([(x - 2, rail_y + 6), (x - 8 - rnd.uniform(0, 4), rail_y + 24)], 5, 2, pal[1]))
    # a sparrow perched on the rail
    bx, by = 470, rail_y - 8
    out.append(painted(D, [(bx - 22, by - 6), (bx - 6, by - 18), (bx + 12, by - 16), (bx + 22, by - 4), (bx + 6, by + 2), (bx - 16, by)], ("#C8A07A", "#8A6040", "#4A3020"), 940, sk=0.2, angle=-10, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(bx + 18, by - 20, 10, 9, 941, 0.05, 10), ("#C8A07A", "#8A6040", "#4A3020"), 941, sk=0.2, n=3, inkw=1.4, hi=0.4))
    out.append(f'<path d="M {bx + 27} {by - 22} l 7 2 l -7 3 Z" fill="#3A2418"/><circle cx="{bx + 21}" cy="{by - 23}" r="1.8" fill="#1A1008"/>')
    out.append(f'<path d="{blob(bx + 17, by - 13, 6, 4, 942, 0.1, 8)}" fill="#F2E8D8"/>')
    out.append(taper([(bx - 18, by - 4), (bx - 36, by - 12)], 7, 3, "#5A3E28"))
    out.append(pline([(bx - 2, by), (bx - 2, by + 8)], "#5A3E28", 1.6, 943, 1, 1) + pline([(bx + 6, by), (bx + 6, by + 8)], "#5A3E28", 1.6, 944, 1, 1))
    # one long ribbon in front, carrying the words of the wish
    fp = [(56, 520), (170, 486), (300, 512), (430, 482), (546, 506)]
    sp = catmull(fp, 8)
    band = []
    for i, (px, py) in enumerate(sp):
        a, b = sp[max(i - 1, 0)], sp[min(i + 1, len(sp) - 1)]
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        nx, ny = -(b[1] - a[1]) / L_, (b[0] - a[0]) / L_
        band.append(((px + nx * 17, py + ny * 17), (px - nx * 17, py - ny * 17)))
    poly = [p for p, q in band] + [q for p, q in band][::-1]
    out.append(f'<path d="{smooth_closed(shift(poly, 5, 7))}" fill="#3A2010" opacity="0.18"/>')
    out.append(painted(D, poly, ("#FFF0A0", "#F6C21C", "#B8820A"), 945, sdir=(0, 1), sk=0.12, angle=-4, n=40, inkw=1.6, hi=0.4, hik=0.12))
    tail = [(56, 520), (30, 532), (40, 520), (22, 506), (52, 502)]
    out.append(painted(D, [(58, 502), (24, 500), (36, 514), (20, 528), (58, 536)], ("#FFF0A0", "#E0AA14", "#9A6A08"), 946, sk=0.2, n=4, inkw=1.4, hi=0.3))
    pid = D.nid()
    D.defs.append(f'<path id="{pid}" d="{smooth_open(sp)}"/>')
    fs = fit_size("LEMBRANÇA DO BONFIM DA BAHIA", JOS, 19, 440, 2)
    out.append(f'<text {JOS} font-size="{fs}" letter-spacing="2" fill="#1E3A8A" dy="6.5"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">LEMBRANÇA DO BONFIM DA BAHIA</textPath></text>')
    # lettering
    out.append(letters(D, 300, 156, "fitinha", SERIF_IT, 132, "#1E4A9A", ["#2E62B8", "#0C2458", "#4A7AD0"], 947, max_w=430, ls=7,
                       shadow="#F6C21C", soff=(0.025, 0.04), angle=-40, hi="#A8C4F0"))
    out.append(ruled(300, 210, "DO BONFIM · FAÇA TRÊS PEDIDOS", "#C8302A", font=JOS, size=20, ls=3, line_w=22, gap=10, max_w=410))
    return finish_b(D, out, 948)


# ================================================================ 29. calçadão de Copacabana — sea, sand and the wave stones, from above
@design("calcadao-de-copacabana")
def calcadao_de_copacabana():
    D = Doc2("cc")
    # the sea along the top, with foam lines
    out = [sky(D, [(0, "#0E6A9A"), (0.6, "#1FA0B8"), (1, "#7AD8D0")], 3, 160, ["#FFFFFF", "#5AC8D8", "#0E5A8A"], 60, angle=-2)]
    rnd = random.Random(820)
    for k, y in enumerate((44, 92, 128)):
        pts = [(x, y + 6 * math.sin(x / 40 + k) + rnd.uniform(-2, 2)) for x in range(-20, 640, 30)]
        out.append(taper(pts, 7 - k, 7 - k, "#FFFFFF", 0.75 - k * 0.1))
        out.append(taper([(x, y_ + 6) for x, y_ in pts], 3, 3, "#BFF0F0", 0.5))
    # wet sand, then dry sand
    out.append(f'<path d="{smooth_open([(x, 150 + 5 * math.sin(x / 50)) for x in range(-20, 640, 40)])} L 620 260 L -20 260 Z" fill="#F2DCA8"/>')
    out.append(f'<path d="{smooth_open([(x, 150 + 5 * math.sin(x / 50)) for x in range(-20, 640, 40)])} L 620 172 L -20 172 Z" fill="#D8BC88" opacity="0.6"/>')
    out.append(specks(821, (0, 150, 600, 250), ["#C8A870", "#FFF4D8", "#B89058"], 160, (0.6, 1.6), (0.3, 0.8)))
    out.append(umbrella_top(D, 120, 196, 44, [RED, ("#FFFFFF", "#FFFFFF", "#D8D0C0")], 822, n=8, shadow=(14, 14)))
    out.append(towel_top(D, 230, 210, 70, 34, -8, ["#F6C21C", "#1F8A4C"], 823))
    out.append(umbrella_top(D, 470, 200, 40, [AMAR, AZUL], 824, n=8, shadow=(14, 14)))
    out.append(towel_top(D, 372, 214, 64, 30, 10, ["#EC5A9A", "#FFFFFF"], 825))
    # the calçadão: wave pattern in black and white stones
    top = 260
    out.append(f'<rect x="-10" y="{top}" width="620" height="350" fill="#F4EEE0"/>')
    lam, A, per = 260, 30, 64
    bands = []
    for j in range(-1, 7):
        y0 = top + j * per
        up = [(x, y0 + A * math.sin(2 * math.pi * x / lam)) for x in range(-20, 641, 20)]
        dn = [(x, y0 + per / 2 + A * math.sin(2 * math.pi * x / lam)) for x in range(-20, 641, 20)]
        bands.append(smooth_open(up) + " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in dn[::-1]) + " Z")
    bd = " ".join(bands)
    clip_top = D.clip(f'<rect x="-10" y="{top}" width="620" height="350"/>')
    out.append(f'<g {clip_top}><path d="{bd}" fill="#2A2622"/>')
    out.append(strokes(D.nid(), bd, (-20, top - 40, 620, 620), ["#4A4440", "#141210"], 826, n=120, angle=-5, length=(30, 80), width=(2, 5), opacity=(0.2, 0.45)))
    # stone joints: an irregular mosaic grid drawn over everything
    joints = []
    st = 13
    for j in range(int(350 / st) + 2):
        y = top + j * st
        joints.append(smooth_open([(x, y + rnd.uniform(-2.2, 2.2)) for x in range(-10, 621, 26)]))
    for j in range(int(350 / st) + 2):
        y = top + j * st
        x = rnd.uniform(0, st)
        while x < 610:
            joints.append(f"M {x:.1f} {y:.1f} L {x + rnd.uniform(-2, 2):.1f} {y + st:.1f}")
            x += rnd.uniform(st * 0.8, st * 1.4)
    out.append(f'<path d="{" ".join(joints)}" fill="none" stroke="#C8BCA4" stroke-width="1.6" opacity="0.75"/>')
    out.append(f'<path d="{" ".join(joints)}" fill="none" stroke="#FFFFFF" stroke-width="0.7" opacity="0.4" transform="translate(-1 -1)"/>')
    out.append(f'<rect x="-10" y="{top}" width="620" height="350" fill="{D.lin([(0, "#3A2A10", 0.18), (0.25, "#3A2A10", 0), (1, "#FFF2D8", 0.1)])}"/></g>')
    # the kerb between sand and stones
    out.append(painted(D, rect_pts(-10, top - 6, 610, top + 6, 30, 827, 0.5), ("#FFFFFF", "#E8E2D4", "#A8A090"), 827, sdir=(0, 1), sk=0.3, angle=0, n=20, inkw=1.4, hi=0.4))
    # the street-name plate (blue enamel)
    px0, py0, px1, py1 = 96, 300, 504, 446
    out.append(f'<path d="{hg.org_rect(px0 + 7, py0 + 9, px1 - px0, py1 - py0, 828, 0.4, 20, 14)}" fill="#141210" opacity="0.35"/>')
    plate = hg.org_rect(px0, py0, px1 - px0, py1 - py0, 829, 0.5, 20, 14)
    out.append(f'<path d="{plate}" fill="#1E4A9A"/>')
    out.append(strokes(D.nid(), plate, (px0, py0, px1, py1), ["#2E62B8", "#14306E", "#4A7AD0"], 830, n=60, angle=-4, length=(30, 90), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(f'<path d="{plate}" fill="{D.lin([(0, "#FFFFFF", 0.25), (0.4, "#FFFFFF", 0), (1, "#000000", 0.2)])}"/>')
    out.append(f'<path d="{hg.org_rect(px0 + 9, py0 + 9, px1 - px0 - 18, py1 - py0 - 18, 831, 0.4, 20, 10)}" fill="none" stroke="#FFFDF4" stroke-width="3"/>')
    for sx, sy in ((px0 + 20, py0 + 20), (px1 - 20, py0 + 20), (px0 + 20, py1 - 20), (px1 - 20, py1 - 20)):
        out.append(f'<circle cx="{sx}" cy="{sy}" r="4" fill="#D8DCE4" stroke="#5A606C" stroke-width="1.2"/>')
    out.append(ink(plate, "#0C1A40", 2, 832, 1, 0.8))
    out.append(label(300, py0 + 46, "CALÇADÃO DE", JOS, 22, "#F6C21C", ls=6, max_w=300))
    out.append(letters(D, 300, py0 + 118, "Copacabana", SERIF_IT, 84, "#FFFDF4", ["#FFFFFF", "#E0E8F8"], 833, max_w=350, wob=0.4, angle=-40))
    # coconut with straw and chinelos left on the stones
    cx_, cy_ = 164, 500
    out.append(cast(D, cx_ + 12, cy_ + 14, 40, 14, strength=0.45, seed=834))
    out.append(painted(D, blob_pts(cx_, cy_, 44, 39, 835, 0.06, 16), ("#9ACB5A", "#5E9A2E", "#2E5A14"), 835, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=20, inkw=1.8, hi=0.45))
    out.append(painted(D, blob_pts(cx_ - 4, cy_ - 6, 13, 11, 836, 0.08, 12), ("#FFFDF0", "#F2EAD0", "#B8AA88"), 836, sk=0.15, n=4, inkw=1.4, hi=0.3))
    out.append(taper([(cx_ - 4, cy_ - 6), (cx_ + 22, cy_ - 40), (cx_ + 36, cy_ - 46)], 6, 6, "#FFFFFF"))
    for k in range(4):
        t0 = 0.15 + 0.22 * k
        out.append(taper([(cx_ - 4 + 40 * t0 - 3, cy_ - 6 - 40 * t0 + 3), (cx_ - 4 + 40 * t0 + 3, cy_ - 6 - 40 * t0 - 3)], 3.5, 3.5, "#1F8A4C", 0.9))
    out.append(chinelo(D, 410, 498, 104, 837, sole=AMAR, strap=VERDE, rot_=-24, squash=0.9))
    out.append(chinelo(D, 478, 506, 104, 838, sole=AMAR, strap=VERDE, rot_=6, squash=0.9))
    return finish_b(D, out, 839)


# ================================================================ 30. festa junina — the arraiá: bandeirinhas, fogueira, milho, quentão
def fogueira(D, cx, base, h, seed):
    """The bonfire: a stacked square of logs, tall layered flames, glowing embers and sparks."""
    out = [D.glow(cx, base - h * 0.35, h * 1.4, "#FF9A3A", 0.55), D.glow(cx, base - h * 0.4, h * 0.7, "#FFE07A", 0.5)]
    out.append(cast(D, cx, base + 6, h * 0.75, 12, color="#1A0A04", strength=0.5, seed=seed))
    rnd = random.Random(seed)
    # crossed log stack (back logs, then flames, then front logs)
    logs_back = [((cx - h * 0.42, base - h * 0.28), (cx + h * 0.36, base - h * 0.3)), ((cx - h * 0.36, base - h * 0.12), (cx + h * 0.44, base - h * 0.1))]
    for k, (a, b) in enumerate(logs_back):
        out.append(taper([a, b], 15, 13, "#5A3418"))
        out.append(taper([(a[0], a[1] - 4), (b[0], b[1] - 4)], 4, 3, "#A8703A", 0.7))
    for k, (s_, fc) in enumerate(((1.0, ("#FF8A2A", "#E04A10", "#8A1A04")), (0.72, ("#FFC04A", "#FF8A1A", "#C84A0A")), (0.44, ("#FFF6B0", "#FFD84A", "#F29A1A")))):
        pts = []
        for i in range(17):
            t = i / 16
            a = math.pi * t
            r_ = h * 0.34 * s_
            tip = 1 + 1.6 * math.exp(-((t - 0.5) / 0.12) ** 2) + 0.6 * math.exp(-((t - 0.25) / 0.06) ** 2) + 0.7 * math.exp(-((t - 0.72) / 0.07) ** 2)
            pts.append((cx - r_ * math.cos(a), base - h * 0.16 - r_ * math.sin(a) * tip * 0.9))
        pts.append((cx + h * 0.3 * s_, base - h * 0.08))
        pts.append((cx - h * 0.3 * s_, base - h * 0.08))
        out.append(painted(D, pts, fc, seed + k, sdir=(0.3, 1), sk=0.12, angle=-90, n=20, inkw=0, hi=0.4, edge=False))
    logs_front = [((cx - h * 0.46, base - h * 0.02), (cx + h * 0.2, base - h * 0.2)), ((cx + h * 0.46, base - h * 0.02), (cx - h * 0.18, base - h * 0.22)),
                  ((cx - h * 0.3, base + h * 0.04), (cx + h * 0.34, base + h * 0.03))]
    for k, (a, b) in enumerate(logs_front):
        out.append(taper([a, b], 17, 15, "#6A3E1E"))
        out.append(taper([(a[0], a[1] - 5), (b[0], b[1] - 5)], 5, 4, "#C8884A", 0.7))
        out.append(f'<path d="{blob(a[0], a[1], 8, 8, seed + k, 0.1, 10)}" fill="#E8B87A" stroke="#6A3E1E" stroke-width="1.6"/>')
        out.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="3.5" fill="none" stroke="#A8703A" stroke-width="1"/>')
        out.append(taper([(a[0] + (b[0] - a[0]) * 0.6, a[1] + (b[1] - a[1]) * 0.6 - 2), (b[0], b[1] - 2)], 4, 2, "#FF8A2A", 0.7))
    for _ in range(26):
        x, y = cx + rnd.uniform(-h * 0.5, h * 0.5), base - h * rnd.uniform(0.6, 1.5)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="{rnd.choice(["#FFE07A", "#FFB04A", "#FFFFFF"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    return "".join(out)


def milho(D, cx, cy, L, ang, seed, husk=True):
    """An ear of corn with rows of kernels, the green husk peeled back."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    W = L * 0.2
    out = []
    if husk:
        for sg, k in ((-1, 0), (1, 1), (-0.4, 2)):
            pts = [(cx - ux * L * 0.1, cy - uy * L * 0.1), (cx - ux * L * 0.55 + nx * sg * W * 1.6, cy - uy * L * 0.55 + ny * sg * W * 1.6),
                   (cx - ux * L * 0.75 + nx * sg * W * 0.8, cy - uy * L * 0.75 + ny * sg * W * 0.8), (cx - ux * L * 0.35, cy - uy * L * 0.35)]
            out.append(painted(D, pts, ("#C8D88A", "#8AA84A", "#4E6A22"), seed + k, sk=0.2, angle=ang, n=6, inkw=1.4, hi=0.35))
    body = []
    for i in range(13):
        t = i / 12
        w = W * (0.85 + 0.15 * math.sin(math.pi * t)) * (1 - 0.35 * t ** 2)
        body.append((cx + ux * L * (t - 0.2) + nx * w, cy + uy * L * (t - 0.2) + ny * w))
    body2 = []
    for i in range(13):
        t = 1 - i / 12
        w = W * (0.85 + 0.15 * math.sin(math.pi * t)) * (1 - 0.35 * t ** 2)
        body2.append((cx + ux * L * (t - 0.2) - nx * w, cy + uy * L * (t - 0.2) - ny * w))
    pts = body + [(cx + ux * L * 0.84, cy + uy * L * 0.84)] + body2
    out.append(painted(D, pts, ("#FFE680", "#F6C21C", "#C08A0A"), seed + 5, sdir=(nx, ny), sk=0.15, angle=ang, n=10, inkw=1.6, hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    k_ = []
    for r in range(-3, 4):
        for i in range(14):
            t = -0.18 + i * 0.075
            px, py = cx + ux * L * t + nx * r * W * 0.3, cy + uy * L * t + ny * r * W * 0.3
            k_.append(f'<path d="{blob(px, py, L * 0.032, W * 0.14, seed + r * 20 + i, 0.08, 8, ang)}" fill="{"#FFF0A0" if r < 0 else "#E8A810"}" opacity="0.75"/>')
    out.append(f'<g {cid}>{"".join(k_)}</g>')
    return "".join(out)


def straw_hat_jn(D, cx, cy, R, seed):
    """Chapéu de palha caipira: wide frayed straw brim, a patch, a red chita band."""
    out = [cast(D, cx + 6, cy + R * 0.28, R * 1.05, R * 0.16, strength=0.4, seed=seed)]
    brim = blob_pts(cx, cy, R, R * 0.3, seed, 0.05, 26)
    straw = ("#FFE8A0", "#E2BA5A", "#9A7A2A")
    out.append(painted(D, brim, straw, seed, sdir=(0.3, 1), sk=0.12, angle=-4, n=40, inkw=1.8, hi=0.4))
    crown = [(cx - R * 0.48, cy - R * 0.02), (cx - R * 0.42, cy - R * 0.44), (cx - R * 0.1, cy - R * 0.54), (cx + R * 0.3, cy - R * 0.5), (cx + R * 0.46, cy - R * 0.38), (cx + R * 0.5, cy)]
    out.append(painted(D, crown, straw, seed + 1, sdir=(0.8, 0.4), sk=0.18, angle=-90, n=24, inkw=1.8, hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(crown)}"/>')
    weave = "".join(f'<path d="M {cx - R:.1f} {cy - R * 0.5 + k * 7:.1f} q {R:.1f} 4 {2 * R:.1f} 0" stroke="#B8902E" stroke-width="1.1" fill="none" opacity="0.55"/>' for k in range(10))
    band = f'<path d="M {cx - R * 0.6:.1f} {cy - R * 0.16:.1f} q {R * 0.6:.1f} 10 {R * 1.2:.1f} 0 l 0 {R * 0.14:.1f} q {-R * 0.6:.1f} 10 {-R * 1.2:.1f} 0 Z" fill="#D8243A"/>'
    dots = "".join(f'<circle cx="{cx - R * 0.45 + k * R * 0.14:.1f}" cy="{cy - R * 0.06 + 2 * math.sin(k):.1f}" r="2" fill="#F6C21C"/>' for k in range(7))
    out.append(f'<g {cid}>{weave}{band}{dots}</g>')
    out.append(painted(D, rect_pts(cx + R * 0.05, cy - R * 0.44, cx + R * 0.28, cy - R * 0.26, 6, seed + 2, 0.6), ("#8AB8E8", "#2E6AB8", "#14306E"), seed + 2, sk=0.15, n=3, inkw=1.2, hi=0.3))
    out.append(f'<path d="{hg.org_rect(cx + R * 0.05, cy - R * 0.44, R * 0.23, R * 0.18, seed + 3, 0.3, 6, 1)}" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-dasharray="3 2"/>')
    rnd = random.Random(seed)
    for _ in range(40):
        a = rnd.uniform(0, 6.28)
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R * 0.3
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * rnd.uniform(4, 9):.1f} {math.sin(a) * rnd.uniform(2, 5):.1f}" stroke="#C89A3A" stroke-width="1.4" stroke-linecap="round"/>')
    return "".join(out)


@design("festa-junina")
def festa_junina():
    D = Doc2("fsj")
    out = [sky(D, [(0, "#14183E"), (0.55, "#2A2E6A"), (1, "#5A3A6A")], 3, 600, ["#3A3E8A", "#0E1030", "#6A4A8A"], 80)]
    rnd = random.Random(850)
    for _ in range(50):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 330)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    out.append(sparkle(520, 240, 7, "#FFF6D8"))
    out.append(sparkle(90, 250, 6, "#FFF6D8"))
    # distant barraquinhas with warm light and a little chapel
    out.append(hill(D, ridge([(-20, 380), (160, 368), (360, 376), (620, 364)], 851, 3), 620, ("#4A3A5A", "#2E2440", "#1A1428"), 851, inkw=0, sop=(0.08, 0.2)))
    for k, x in enumerate((70, 150, 450, 530)):
        out.append(painted(D, rect_pts(x - 34, 344, x + 34, 378, 12, 852 + k, 0.5), ("#8A5A3A", "#5A3A2A", "#2E1E14"), 852 + k, sk=0.1, n=6, inkw=0, hi=0.2))
        out.append(f'<path d="{hg.org_rect(x - 26, 352, 52, 18, 860 + k, 0.4, 8, 2)}" fill="#FFC04A"/>')
        out.append(D.glow(x, 360, 50, "#FFB04A", 0.4))
        roof = [(x - 42, 346), (x, 322), (x + 42, 346)]
        out.append(painted(D, roof, (RED if k % 2 else AMAR), 870 + k, sk=0.1, n=6, inkw=1.2, hi=0.3))
        for j in range(4):
            out.append(f'<circle cx="{x - 30 + j * 20}" cy="{346}" r="2.2" fill="#FFE07A"/>')
    cx0 = 300
    out.append(painted(D, rect_pts(cx0 - 26, 320, cx0 + 26, 372, 12, 880, 0.4), ("#FFFDF4", "#E8E0D0", "#A8A090"), 880, sk=0.1, n=6, inkw=1.2, hi=0.3))
    out.append(painted(D, [(cx0 - 32, 322), (cx0, 296), (cx0 + 32, 322)], TERRA, 881, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(cx0 - 7, 278, cx0 + 7, 300, 6, 882, 0.3), ("#FFFDF4", "#E8E0D0", "#A8A090"), 882, sk=0.1, n=2, inkw=1.2, hi=0.3))
    out.append(f'<path d="M {cx0} 266 L {cx0} 280 M {cx0 - 5} 271 L {cx0 + 5} 271" stroke="#FFF6D8" stroke-width="2"/>')
    out.append(f'<path d="{hg.org_rect(cx0 - 9, 344, 18, 28, 883, 0.3, 6, 6)}" fill="#FFC04A"/>')
    # couples dancing the quadrilha in front of the stalls, lit from the fire
    def dancer(x, base, h, dress, seed, man=False, flip=1):
        o = []
        hx, hy = x, base - h
        if man:
            o.append(taper([(x - 3, base - h * 0.45), (x - 4, base)], 4, 3.5, "#2A2440"))
            o.append(taper([(x + 3, base - h * 0.45), (x + 5 * flip, base)], 4, 3.5, "#2A2440"))
            o.append(painted(D, rect_pts(x - 6, base - h * 0.82, x + 6, base - h * 0.42, 4, seed, 0.3), dress, seed, sk=0.2, n=3, inkw=0.8, hi=0.3))
            o.append(f'<path d="M {x - 6} {base - h * 0.74:.1f} L {x + 6} {base - h * 0.66:.1f} M {x - 6} {base - h * 0.6:.1f} L {x + 6} {base - h * 0.52:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="0.6"/>')
            o.append(f'<circle cx="{hx}" cy="{hy + 4:.1f}" r="4.6" fill="#C8885A"/>')
            o.append(f'<ellipse cx="{hx}" cy="{hy + 1:.1f}" rx="9" ry="2.4" fill="#E2BA5A"/><path d="M {hx - 4} {hy + 1:.1f} q 4 -8 8 0" fill="#E2BA5A"/>')
        else:
            o.append(taper([(x - 2, base - h * 0.3), (x - 2, base)], 3, 3, "#C8885A"))
            o.append(taper([(x + 2, base - h * 0.3), (x + 3, base)], 3, 3, "#C8885A"))
            sk_ = [(x - 5, base - h * 0.78), (x + 5, base - h * 0.78), (x + 13, base - h * 0.28), (x + 4, base - h * 0.24), (x - 4, base - h * 0.28), (x - 13, base - h * 0.24)]
            o.append(painted(D, sk_, dress, seed, sk=0.2, n=4, inkw=0.8, hi=0.35))
            for j in range(3):
                o.append(f'<circle cx="{x - 7 + j * 7}" cy="{base - h * 0.4:.1f}" r="1.6" fill="#FFFFFF" opacity="0.8"/>')
            o.append(f'<circle cx="{hx}" cy="{hy + 4:.1f}" r="4.4" fill="#C8885A"/>')
            o.append(f'<path d="M {hx - 5} {hy + 3:.1f} q 0 -6 5 -6 q 5 0 5 6 l 2 8 l -3 -2 Z" fill="#3A2010"/>')
        return "".join(o)
    for k, (x, sd) in enumerate(((104, 0), (128, 1), (196, 2), (222, 3), (380, 4), (404, 5), (482, 6), (506, 7))):
        man = k % 2 == 1
        pal = [RED, ("#8AB8E8", "#2E6AB8", "#14306E"), AMAR, ROSA][k // 2 % 4] if not man else (("#E8A0A0", "#C83A3A", "#7A1414") if k % 4 == 1 else ("#8ACB8A", "#3E8A4E", "#1E5A2E"))
        out.append(dancer(x, 400 + (k % 3), 40, pal, 900 + sd, man=man, flip=1 if k % 4 < 2 else -1))
        if man:
            out.append(pline([(x - 6, 400 - 26), (x - 12, 400 - 30), (x - 18, 400 - 26)], "#C8885A", 2.2, k, 1, 1))
    # the yard, lit by the fire
    out.append(hill(D, ridge([(-20, 400), (300, 392), (620, 400)], 884, 2), 620, ("#C8885A", "#8A5A3A", "#4A2E1E"), 884, inkw=0, sop=(0.1, 0.25)))
    out.append(f'<ellipse cx="300" cy="500" rx="300" ry="110" fill="{D.rad([(0, "#FFB04A", 0.55), (1, "#FFB04A", 0)])}"/>')
    out.append(grass(885, (0, 400, 600, 600), ["#6A4A2A", "#A8703A", "#3A2A1A"], 60, (6, 12)))
    # bandeirinhas, two crossing strings
    jcols = ["#E0302A", "#F6C21C", "#1F9A4C", "#2E6AC8", "#EC5A9A", "#F2872A", "#FFFFFF", "#7A4AC8"]
    out.append(flag_string(D, -20, 24, 620, 60, 46, 15, jcols, 886, size=26))
    out.append(flag_string(D, -20, 70, 620, 30, 50, 16, jcols[3:] + jcols[:3], 887, size=24))
    # fogueira centre, hat, corn and quentão around it
    out.append(fogueira(D, 300, 498, 170, 888))
    out.append(straw_hat_jn(D, 132, 500, 82, 889))
    out.append(milho(D, 470, 496, 96, -30, 890))
    out.append(milho(D, 512, 520, 84, -60, 891, husk=True))
    # quentão in an enamel mug
    mx, mb = 418, 538
    out.append(cast(D, mx + 4, mb + 2, 30, 6, strength=0.45, seed=892))
    mug = [(mx - 22, mb - 46), (mx + 22, mb - 46), (mx + 20, mb - 2), (mx - 20, mb - 2)]
    out.append(painted(D, mug, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 893, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=8, inkw=1.6, hi=0.4))
    out.append(ink(f"M {mx + 22} {mb - 38} q 16 2 12 18 q -2 10 -14 10", "#B8B0A6", 5, 894, 1, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(mx, mb - 46, 22, 5, 0, 360, 16))}" fill="#8A2A14"/>')
    out.append(ink(smooth_closed(ell_pts(mx, mb - 46, 22, 5, 0, 360, 16)), "#1E3F9A", 2.4, 895, 1, 0.9))
    out.append(steam(mx, mb - 56, 34, 896, "#FFFFFF", 2, 14, 5, 0.6))
    out.append(taper([(mx - 4, mb - 50), (mx + 10, mb - 70)], 4, 3, "#A8703A"))
    # lettering
    out.append(letters(D, 300, 214, "festa junina", SERIF_IT, 104, "#FFE07A", ["#FFF0A0", "#F6C21C", "#FFB04A"], 897, max_w=460,
                       shadow="#8A1A10", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 262, "ARRAIÁ DE SÃO JOÃO", "#FFF6E0", font=JOS, size=22, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 898)


# ================================================================ 31. rede na varanda — a hammock on the porch, a cat in the hammock
def samambaia(D, cx, top, s, seed):
    """Hanging fern in a clay pot: long arching fronds with paired leaflets."""
    out = []
    rnd = random.Random(seed)
    for k in (-1, 1):
        out.append(pline([(cx, top - 70), (cx + k * s * 0.42, top)], "#8A6A3A", 1.6, seed + k, 0.9, 1))
    for i in range(14):
        a = math.radians(rnd.uniform(-170, -10) if i < 4 else rnd.uniform(10, 170))
        L = s * rnd.uniform(0.7, 1.25)
        x0, y0 = cx + math.cos(a) * s * 0.2, top + 6
        pts = [(x0, y0)]
        for j in range(1, 9):
            t = j / 8
            pts.append((x0 + math.cos(a) * L * t * 0.7, y0 + (math.sin(a) * L * t * 0.4) + L * t * t * 0.9))
        out.append(pline(pts, "#2E6A2A", 1.8, seed + i, 0.9, 1))
        for j in range(1, 9):
            px, py = pts[j]
            qx, qy = pts[j - 1]
            ang = math.degrees(math.atan2(py - qy, px - qx))
            for sg in (-1, 1):
                out.append(f'<path d="{blob(px + sg * 4 * math.cos(math.radians(ang + 90)), py + sg * 4 * math.sin(math.radians(ang + 90)), 6 * (1 - j / 12), 2.6, rnd.randint(1, 9999), 0.1, 8, ang + sg * 50)}" fill="{rnd.choice(["#4E9A3A", "#2E7A2A", "#7AC05A"])}"/>')
    pot = [(cx - s * 0.36, top - 8), (cx + s * 0.36, top - 8), (cx + s * 0.28, top + 34), (cx - s * 0.28, top + 34)]
    out.append(painted(D, pot, TERRA, seed + 50, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.4))
    out.append(painted(D, rect_pts(cx - s * 0.4, top - 14, cx + s * 0.4, top - 2, 8, seed + 51, 0.4), TERRA, seed + 51, sk=0.2, n=4, inkw=1.4, hi=0.4))
    return "".join(out)


def cat_curled(D, cx, cy, s, seed, pal=("#FFC88A", "#E8903A", "#9A5418")):
    """A ginger cat asleep in a curl: round body, tail wrapped round, ears, closed eyes, tabby stripes."""
    out = []
    body = blob_pts(cx, cy, s, s * 0.62, seed, 0.04, 18)
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=-30, n=20, inkw=1.8, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    st = "".join(taper([(cx - s * 0.5 + k * s * 0.22, cy - s * 0.58), (cx - s * 0.45 + k * s * 0.22, cy - s * 0.2)], 6, 2, pal[2], 0.45) for k in range(5))
    out.append(f'<g {cid}>{st}</g>')
    hx, hy = cx - s * 0.62, cy - s * 0.12
    head = blob_pts(hx, hy, s * 0.42, s * 0.36, seed + 1, 0.04, 14)
    for sg in (-1, 1):
        ex = hx + sg * s * 0.22
        out.append(painted(D, [(ex - s * 0.14, hy - s * 0.2), (ex + sg * s * 0.04, hy - s * 0.52), (ex + s * 0.14, hy - s * 0.2)], pal, seed + 2 + sg, sk=0.15, n=3, inkw=1.4, hi=0.3))
        out.append(f'<path d="M {ex - s * 0.06:.1f} {hy - s * 0.24:.1f} L {ex + sg * s * 0.02:.1f} {hy - s * 0.42:.1f} L {ex + s * 0.06:.1f} {hy - s * 0.24:.1f} Z" fill="#F8B0A0"/>')
    out.append(painted(D, head, pal, seed + 1, sdir=(0.5, 0.8), sk=0.15, angle=-30, n=8, inkw=1.6, hi=0.4))
    for sg in (-1, 1):
        ex = hx + sg * s * 0.15
        out.append(pline([(ex - s * 0.08, hy), (ex, hy + s * 0.05), (ex + s * 0.08, hy)], "#3A2010", 2, seed + sg, 1, 1))
    out.append(f'<path d="M {hx - 3:.1f} {hy + s * 0.12:.1f} l 3 3 l 3 -3 Z" fill="#E87A7A"/>')
    for sg in (-1, 1):
        out.append(pline([(hx + sg * s * 0.18, hy + s * 0.16), (hx + sg * s * 0.46, hy + s * 0.12)], "#FFFFFF", 1, seed, 0.8, 1))
    tail = catmull([(cx + s * 0.9, cy), (cx + s * 0.6, cy + s * 0.5), (cx - s * 0.2, cy + s * 0.6), (cx - s * 0.7, cy + s * 0.3)], 5)
    out.append(taper(tail, s * 0.26, s * 0.18, pal[1]))
    out.append(taper([(x, y - 2) for x, y in tail], s * 0.08, s * 0.05, pal[0], 0.7))
    out.append(ink(smooth_open(tail), INK, 1.4, seed, 1, 0.5))
    return "".join(out)


@design("rede-na-varanda")
def rede_na_varanda():
    D = Doc2("rv")
    # late afternoon outside the porch
    out = [sky(D, [(0, "#F6A86A"), (0.4, "#FAD08A"), (0.7, "#FCEBC0")], 3, 600, ["#FFFFFF", "#F8B880", "#FFE8B8"], 70)]
    out.append(soft_glow(D, 420, 330, 230, "#FFF2B8", 0.75))
    out.append(painted(D, blob_pts(420, 334, 34, 34, 900, 0.01, 20), ("#FFFBE0", "#FFE070", "#F2A030"), 900, sk=0.04, n=10, inkw=0, hi=0.5, edge=False))
    out.append(hill(D, ridge([(-20, 360), (100, 330), (240, 352), (380, 320), (520, 346), (620, 330)], 901, 6), 620, ("#C0B8B8", "#9A98A8", "#6E7088"), 901, inkw=0, sop=(0.06, 0.16)))
    out.append(hill(D, ridge([(-20, 398), (160, 376), (330, 392), (500, 372), (620, 388)], 902, 5), 620, ("#A8C07A", "#7A9A50", "#4E6E34"), 902, inkw=1.2, inkop=0.35))
    for k, x in enumerate((90, 180, 470, 540)):
        out.append(dab_crown(D, x, 384 - (k % 2) * 6, 22, 14, [("#6E9A4A", "#4E7A34", "#2E5020")], 903 + k, n=30, size=(3, 6), inkw=0))
    out.append(palm(D, (520, 470), (500, 300), 907, [(-170, 0.9), (-130, 0.8), (-90, 0.7), (-50, 0.8), (-10, 0.9), (-200, 0.7)], L=60, width=8))
    for x, y, sz in ((300, 250, 8), (322, 240, 6), (260, 262, 6)):
        out.append(bird_v(x, y, sz, "#7A4A3A", 0.8))
    # porch: wooden floor, railing with turned balusters, two posts, the beam and the tile eave
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="#B8703A"/>')
    out.append(wood_planks(D, 470, 600, 908, ("#E8A870", "#B8703A", "#6A3A18"), 4))
    out.append(f'<rect x="0" y="470" width="600" height="14" fill="#3A1A08" opacity="0.25"/>')
    for x in range(64, 540, 30):
        bal = [(x - 5, 470), (x - 7, 456), (x - 4, 444), (x - 7, 430), (x - 5, 412), (x + 5, 412), (x + 7, 430), (x + 4, 444), (x + 7, 456), (x + 5, 470)]
        out.append(painted(D, bal, ("#FFFDF4", "#EEE6D2", "#A8A08A"), 910 + x, sdir=(1, 0), sk=0.3, angle=-90, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(40, 400, 560, 414, 30, 909, 0.5), ("#FFFDF4", "#EEE6D2", "#A8A08A"), 909, sdir=(0, 1), sk=0.3, angle=0, n=20, inkw=1.6, hi=0.4))
    for x in (40, 560):
        out.append(painted(D, rect_pts(x - 15, 90, x + 15, 480, 24, 940 + x, 0.6), WOOD, 940 + x, sdir=(1, 0), sk=0.25, angle=-90, n=30, inkw=1.8, hi=0.35))
    out.append(painted(D, rect_pts(-10, 72, 610, 98, 30, 945, 0.5), WOOD, 945, sdir=(0, 1), sk=0.25, angle=0, n=30, inkw=1.8, hi=0.35))
    out.append(tile_roof(D, [(-10, -10), (610, -10), (610, 72), (-10, 72)], 946, TERRA, 2, 16))
    out.append(f'<rect x="-10" y="98" width="620" height="16" fill="{D.lin([(0, "#3A1A08", 0.35), (1, "#3A1A08", 0)])}"/>')
    # the hammock with a sleeping cat; hanging fern; coffee on the rail
    out.append(hammock(D, 56, 280, 544, 280, 70, 947, ["#F6C21C", "#1F8A4C", "#D8382E", "#2E6AB8", "#FFFFFF", "#EC5A9A"]))
    for x in (54, 546):
        out.append(f'<circle cx="{x}" cy="280" r="6" fill="#6A6A74" stroke="#2A2A30" stroke-width="1.6"/>')
    rnd = random.Random(948)
    for i in range(34):
        t = 0.12 + 0.76 * i / 33
        x = 56 + 488 * t
        y = 280 + 70 * math.sin(math.pi * t) ** 1.3 + 0.75 * (46 * math.sin(math.pi * t) ** 0.8 + 4) - 2
        c = ["#F6C21C", "#1F8A4C", "#D8382E", "#2E6AB8", "#FFFFFF", "#EC5A9A"][i % 6]
        L_ = rnd.uniform(12, 18)
        out.append(pline([(x, y), (x + rnd.uniform(-1.5, 1.5), y + L_)], c, 2.2, i, 1, 1))
        out.append(f'<circle cx="{x:.1f}" cy="{y + L_ + 1:.1f}" r="2.4" fill="{c}"/>')
    out.append(cat_curled(D, 300, 316, 52, 949))
    out.append(samambaia(D, 96, 136, 50, 950))
    out.append(cup_saucer(D, 470, 400, 40, 951, rim=RED))
    out.append(steam(470, 362, 30, 952, "#FFFFFF", 2, 14, 5, 0.6))
    # lettering under the eave
    out.append(letters(D, 342, 194, "rede na varanda", SERIF_IT, 90, "#7A2E14", ["#A8461E", "#5A1E0A", "#C0603A"], 953, max_w=356,
                       shadow="#FFF4DC", soff=(0.02, 0.03), angle=-40, hi="#F6B07A"))
    out.append(ruled(342, 238, "E O MUNDO QUE ESPERE", "#1F6A40", font=JOS, size=20, ls=4, line_w=22, gap=10, max_w=280))
    return finish_b(D, out, 954)


# ================================================================ 32. gratidão — a wreath of Brazilian flowers at sunrise
def passion_flower(D, cx, cy, r, seed, rot_=0):
    """Flor de maracujá: ten white petals, the purple-white banded corona of fine filaments, green stamens."""
    rnd = random.Random(seed)
    out = []
    for i in range(10):
        a = math.radians(rot_ + i * 36 + rnd.uniform(-4, 4))
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(painted(D, blob_pts(px, py, r * 0.48, r * 0.16, seed + i, 0.06, 12, math.degrees(a)), ("#FFFFFF", "#F2F0F6", "#B8B0C8"), seed + i,
                           sdir=(math.cos(a), math.sin(a)), sk=0.15, angle=math.degrees(a), n=3, inkw=1, inkop=0.5, hi=0.3, edge=False))
    for i in range(60):
        a = math.radians(rot_ + i * 6)
        x1, y1 = cx + math.cos(a) * r * 0.12, cy + math.sin(a) * r * 0.12
        x2, y2 = cx + math.cos(a) * r * 0.72, cy + math.sin(a) * r * 0.72
        out.append(f'<path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}" stroke="#5A2A8A" stroke-width="1.6" stroke-linecap="round"/>')
        xm, ym = cx + math.cos(a) * r * 0.42, cy + math.sin(a) * r * 0.42
        out.append(f'<path d="M {xm:.1f} {ym:.1f} L {cx + math.cos(a) * r * 0.55:.1f} {cy + math.sin(a) * r * 0.55:.1f}" stroke="#FFFFFF" stroke-width="1.6"/>')
        out.append(f'<path d="M {cx + math.cos(a) * r * 0.62:.1f} {cy + math.sin(a) * r * 0.62:.1f} L {x2 + math.cos(a + 0.3) * 2:.1f} {y2 + math.sin(a + 0.3) * 2:.1f}" stroke="#B88AE0" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.16:.1f}" fill="#7A3A9A"/>')
    for i in range(5):
        a = math.radians(rot_ + i * 72 + 18)
        ex, ey = cx + math.cos(a) * r * 0.32, cy + math.sin(a) * r * 0.32
        out.append(pline([(cx, cy), (ex, ey)], "#8AB04A", 2.2, seed + i, 1, 1))
        out.append(f'<path d="{blob(ex, ey, r * 0.1, r * 0.05, seed + i, 0.1, 8, math.degrees(a) + 90)}" fill="#E8D04A" stroke="#8A7A1A" stroke-width="0.8"/>')
    for i in range(3):
        a = math.radians(rot_ + i * 120 - 90)
        out.append(pline([(cx, cy), (cx + math.cos(a) * r * 0.18, cy + math.sin(a) * r * 0.18 - 3)], "#6A3A2A", 2.6, seed + 30 + i, 1, 1))
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.18:.1f}" cy="{cy + math.sin(a) * r * 0.18 - 3:.1f}" r="{max(1.6, r * 0.04):.1f}" fill="#4A2A1A"/>')
    return "".join(out)


def ipe_blossom(D, cx, cy, r, seed, rot_=0, pal=("#FFF2A0", "#F6C21C", "#C08A0A")):
    """A trumpet-shaped ipê flower, frilled mouth facing out."""
    rnd = random.Random(seed)
    out = []
    a = math.radians(rot_)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    tube = [(cx - ux * r * 0.9 + nx * r * 0.12, cy - uy * r * 0.9 + ny * r * 0.12), (cx + nx * r * 0.3, cy + ny * r * 0.3),
            (cx - nx * r * 0.3, cy - ny * r * 0.3), (cx - ux * r * 0.9 - nx * r * 0.12, cy - uy * r * 0.9 - ny * r * 0.12)]
    out.append(painted(D, tube, pal, seed, sk=0.2, angle=rot_, n=4, inkw=1.2, hi=0.3))
    for i in range(5):
        b = math.radians(rot_ - 80 + i * 40)
        px, py = cx + ux * r * 0.2 + math.cos(b) * r * 0.42, cy + uy * r * 0.2 + math.sin(b) * r * 0.42
        out.append(painted(D, blob_pts(px, py, r * 0.36, r * 0.28, seed + i, 0.15, 10, math.degrees(b)), pal, seed + i, sk=0.15, n=3, inkw=1.1, inkop=0.5, hi=0.35))
    out.append(pline([(cx + ux * r * 0.05, cy + uy * r * 0.05), (cx + ux * r * 0.4, cy + uy * r * 0.4)], "#B86A0A", 1.6, seed, 0.8, 1))
    return "".join(out)


@design("gratidao")
def gratidao():
    D = Doc2("gr")
    out = [sky(D, [(0, "#FCE6CC"), (1, "#F8D2B0")], 3, 600, ["#FFFFFF", "#F2B890", "#FFF0DC"], 80, angle=-30, sop=(0.06, 0.16))]
    out.append(blooms(960, ["#F2A880", "#FFFFFF", "#F8C8A0"], 7, (60, 60, 540, 540), (110, 190), (0.06, 0.12)))
    cx, cy, R = 300, 304, 190
    # soft sunrise rays fanning from behind the wreath
    for i in range(24):
        a0, a1 = math.radians(i * 15), math.radians(i * 15 + 7.5)
        out.append(f'<path d="M {cx} {cy} L {cx + 520 * math.cos(a0):.1f} {cy + 520 * math.sin(a0):.1f} L {cx + 520 * math.cos(a1):.1f} {cy + 520 * math.sin(a1):.1f} Z" fill="#FFFFFF" opacity="0.22"/>')
    out.append(soft_glow(D, cx, cy, 260, "#FFF6E0", 0.9))
    # the wreath ring: a painted vine
    ring = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(0, 361, 15)]
    out.append(taper(catmull(ring, 4), 5, 5, "#5A7A3A", 0.9))
    rnd = random.Random(961)
    # leaves all round (alternating tropical greens), then flowers in clusters
    for k, a in enumerate(range(0, 360, 11)):
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        side = 1 if k % 2 else -1
        out.append(leaf_simple(D, x, y, rnd.uniform(48, 66), rnd.uniform(12, 16), a + 90 + side * 48 + rnd.uniform(-10, 10),
                               rnd.choice([VERDE, MATA, ("#9ACB6A", "#5E9A3A", "#2E5A1E")]), 962 + k, inkw=1.1))
    for k, a in enumerate(range(4, 360, 16)):
        x, y = cx + (R + rnd.uniform(-6, 10)) * math.cos(math.radians(a)), cy + (R + rnd.uniform(-6, 10)) * math.sin(math.radians(a))
        out.append(leaf_simple(D, x, y, 38, 10, a + rnd.choice([-60, 60, 0]), ("#B8D88A", "#7AA850", "#3E6A28"), 1100 + k, inkw=1))
    for k, a in enumerate(range(20, 360, 45)):
        x, y = cx + (R + 4) * math.cos(math.radians(a)), cy + (R + 4) * math.sin(math.radians(a))
        out.append(monstera(D, x, y, 30, a + 90, 1150 + k, ("#7ACB6A", "#2E8A3A", "#14501E")))
    # flowers: maracujá at top-left and bottom-right, hibiscus, ipê sprays, little buds
    out.append(passion_flower(D, cx + R * math.cos(math.radians(222)), cy + R * math.sin(math.radians(222)), 56, 1000, 10))
    out.append(passion_flower(D, cx + R * math.cos(math.radians(42)), cy + R * math.sin(math.radians(42)), 52, 1001, -8))
    out.append(hibiscus(D, cx + R * math.cos(math.radians(318)), cy + R * math.sin(math.radians(318)), 46, ("#FFA8C0", "#E8507A", "#A82450"), 1002, 20))
    out.append(hibiscus(D, cx + R * math.cos(math.radians(140)), cy + R * math.sin(math.radians(140)), 44, ("#FFC07A", "#F2872A", "#B04E0E"), 1003, -30))
    for k, a in enumerate((256, 272, 288, 160, 198, 100, 84, 64)):
        x, y = cx + (R + rnd.uniform(-8, 8)) * math.cos(math.radians(a)), cy + (R + rnd.uniform(-8, 8)) * math.sin(math.radians(a))
        out.append(ipe_blossom(D, x, y, 24, 1010 + k, a + rnd.uniform(-40, 40),
                               pal=("#FFF2A0", "#F6C21C", "#C08A0A") if k % 3 else ("#FFC8E8", "#E870B0", "#A0306A")))
    for k, a in enumerate(range(10, 360, 24)):
        for j in range(3):
            x, y = cx + (R - 22 + j * 5) * math.cos(math.radians(a + j * 4)), cy + (R - 22 + j * 5) * math.sin(math.radians(a + j * 4))
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{["#E8304A", "#F6C21C", "#7A3A9A"][k % 3]}" stroke="#5A2A1A" stroke-width="0.9"/>')
            out.append(f'<circle cx="{x - 1.4:.1f}" cy="{y - 1.4:.1f}" r="1.3" fill="#FFFFFF" opacity="0.8"/>')
    # a hummingbird (beija-flor) visiting the top
    hx, hy = 386, 100
    out.append(painted(D, [(hx - 26, hy + 6), (hx - 8, hy - 6), (hx + 14, hy - 4), (hx + 20, hy + 4), (hx + 2, hy + 12), (hx - 18, hy + 14)], ("#7AE0B0", "#1FA07A", "#0E5A44"), 1030, sk=0.2, angle=-10, n=6, inkw=1.4, hi=0.5))
    out.append(painted(D, blob_pts(hx + 18, hy - 6, 9, 8, 1031, 0.05, 10), ("#7AE0B0", "#1FA07A", "#0E5A44"), 1031, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(taper([(hx + 26, hy - 6), (hx + 52, hy + 4)], 3, 1, "#2A2018"))
    out.append(f'<circle cx="{hx + 21}" cy="{hy - 8}" r="1.8" fill="#1A1008"/>')
    out.append(f'<path d="{blob(hx + 12, hy + 2, 6, 3, 1032, 0.1, 8)}" fill="#E8304A"/>')
    for sg, op in ((-1, 0.75), (1, 0.55)):
        out.append(f'<path d="{blob(hx - 4, hy - 22 + sg * 2, 24, 7, 1033 + sg, 0.1, 10, -70 + sg * 20)}" fill="#D8F4F0" opacity="{op}" stroke="#5A8A80" stroke-width="1"/>')
    out.append(taper([(hx - 24, hy + 8), (hx - 46, hy + 18)], 7, 2, "#0E5A44"))
    # lettering in the middle
    out.append(letters(D, 300, 314, "gratidão", SERIF_IT, 104, "#A8361E", ["#C8502A", "#7A1E0E", "#E0703A"], 1040, max_w=250,
                       shadow="#FFE8C8", soff=(0.02, 0.03), angle=-40, hi="#F8B08A"))
    out.append(ruled(300, 364, "POR TUDO, SEMPRE", "#2E6A40", font=JOS, size=20, ls=5, line_w=20, gap=10, max_w=230))
    return finish_b(D, out, 1041)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        # the folder holds exactly this set: clear out artwork for slugs that were dropped
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
