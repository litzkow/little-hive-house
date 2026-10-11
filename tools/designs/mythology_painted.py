"""Mythology, hand-painted (antique book of myths / museum poster) edition: 30 magnets.

The great myths of the world, each painted as a luminous plate from an old illustrated book of myths: one god,
hero, creature or sacred object shown in a real scene with light and atmosphere, its name lettered with care
and a small line naming the culture and a one-line hook (or a short classical line in translation).

Everything comes from the ancient sources and classical art (Homer, Hesiod, Ovid, Apollonius, the Eddas, the
Book of the Dead, the Kojiki, the Epic of Gilgamesh, the Shahnameh and Attar, Livy, folk tales), never from any
modern film, comic or game. Figures are painted with dignity: in silhouette, from behind, or as statue forms.
Creatures and sacred objects carry most of the pieces.

Painted in the house gouache idiom (layered washes with pooled edges, brush strokes following the form, a warm
pen line, soft light, grain on top). Colour story: lapis and midnight blues, burnished gold, Etruscan
terracotta, marble cream and verdigris, with each culture's own accent (Egyptian turquoise, Norse slate and
aurora green, Japanese vermilion, Chinese jade, Persian rose).

Run from tools/designs:  python3 mythology_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, shift, sky, soft_glow, specks, taper, catmull, mist)
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
from paint import conifer, rough
import holidays_gouache as hg
from storybook_classics_painted import T, ell_pts, pd, tx, gilt, gilt_fill, stars_field, flourish, laurel, leaf_simple
from fairy_tales_painted import Doc2, aurora, swell, multi, arch_pts

COL = "mythology"
INK = "#3A2418"

lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
GOLD = ("#FBE7A4", "#D9A945", "#8A6020")
BRONZE = ("#F2C886", "#B07A3A", "#4E2E12")
MARBLE = ("#FFFFFF", "#ECE6DA", "#A89E90")
STONE = ("#D8D2C4", "#A09888", "#585046")
TERRA = ("#F0A070", "#C0603A", "#6A2A14")
OLIVE = ("#C8D0A0", "#8A9A62", "#3E4A2A")
RAVEN = ("#5A6278", "#1A1C26", "#05060A")
LAPIS = ("#5A7AD0", "#1E3A8A", "#0A1A4A")
TURQ = ("#8AE0D0", "#2AA0A0", "#0E5A62")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def fin(D, out, seed, color="#000000", op=0.5):
    return finish(D, out, seed, color, op)


# ================================================================ toolkit
def poly(pts, fill, op=None, extra=""):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{smooth_closed(pts)}" fill="{fill}"{o}{extra}/>'


def sharp(pts, fill, op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<path d="{pd(pts)}" fill="{fill}"{o}/>'


def moon(D, cx, cy, r, seed, pal=("#FFFDF2", "#F2EAD0", "#C8BC9A"), glow="#FFF6D8", gs=0.55, glow_r=3.0):
    """Full moon: halo, painted disc, soft maria and a lit limb."""
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, cy, r * glow_r, glow, gs)]
    out.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.004, 36), pal, seed, sdir=(0.5, 0.4), sk=0.06, angle=-30, n=30, inkw=0, hi=0.3))
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    mar = []
    for (dx, dy, rx, ry) in ((-0.3, -0.25, 0.28, 0.2), (0.15, -0.35, 0.2, 0.16), (0.25, 0.1, 0.3, 0.22), (-0.15, 0.3, 0.22, 0.14), (-0.45, 0.15, 0.12, 0.18)):
        mar.append(f'<path d="{blob(cx + dx * r, cy + dy * r, rx * r, ry * r, rnd.randint(0, 999), 0.2, 12)}" fill="{pal[2]}" opacity="0.32"/>')
    out.append(f'<g {cid}>{"".join(mar)}</g>')
    return "".join(out)


def meander(x0, x1, y, h, col, w=2.2, unit=None):
    """Greek key band between x0 and x1, centred on y, height h."""
    u = unit or h
    out = []
    x = x0
    while x + u <= x1 + 0.1:
        a, b = y - h / 2, y + h / 2
        k = u / 5
        out.append(f'<path d="M {x:.1f} {b:.1f} L {x:.1f} {a:.1f} L {x + 4 * k:.1f} {a:.1f} L {x + 4 * k:.1f} {b - k:.1f} L {x + 2 * k:.1f} {b - k:.1f} '
                   f'L {x + 2 * k:.1f} {a + 2 * k:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="miter"/>')
        out.append(f'<path d="M {x:.1f} {b:.1f} L {x + u:.1f} {b:.1f}" stroke="{col}" stroke-width="{w}"/>')
        x += u
    return "".join(out)


def wave_scroll(x0, x1, y, h, col, w=2.4):
    """Running-dog (Vitruvian) wave scroll."""
    out = []
    x = x0
    u = h * 1.6
    while x + u <= x1 + 0.1:
        out.append(f'<path d="M {x:.1f} {y + h / 2:.1f} C {x + u * 0.35:.1f} {y + h / 2:.1f} {x + u * 0.55:.1f} {y - h / 2:.1f} {x + u * 0.42:.1f} {y - h * 0.15:.1f} '
                   f'C {x + u * 0.32:.1f} {y + h * 0.05:.1f} {x + u * 0.2:.1f} {y - h * 0.12:.1f} {x + u * 0.3:.1f} {y - h * 0.25:.1f} '
                   f'M {x + u * 0.48:.1f} {y - h * 0.38:.1f} C {x + u * 0.7:.1f} {y - h * 0.6:.1f} {x + u * 0.9:.1f} {y + h / 2:.1f} {x + u:.1f} {y + h / 2:.1f}" '
                   f'fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
        x += u
    return "".join(out)


def robed_figure(x, base, s, col, facing=1, rim=None, arm=None, cloak=0.0, head="bare", lean=0.0, wreath=None):
    """A classical figure from behind in a long chiton with a himation over one shoulder, about 122*s tall.
    arm: None, 'up' (raised forward), 'out' (held out to the side), 'down'. head: 'bare' or 'helmet'."""
    def L(pts):
        return T(pts, x, base, s, facing < 0, lean)
    out = []
    body = L([(-5, -101), (-14, -97), (-22, -93), (-24, -84), (-21, -70), (-17, -58), (-19, -40), (-23, -18), (-27, -1), (-12, 1), (2, 0),
              (14, 1), (27, -1), (23, -18), (19, -40), (17, -58), (21, -70), (24, -84), (22, -93), (14, -97), (5, -101)])
    out.append(poly(body, col))
    if cloak:
        out.append(poly(L([(12, -97), (24, -88), (28 + cloak * 16, -50), (32 + cloak * 30, -6), (20, -2), (14, -40), (12, -80)]), col))
    if head == "helmet":
        out.append(poly(L([(-9, -104), (-10, -114), (-6, -122), (2, -124), (9, -118), (10, -108), (8, -100), (-6, -100)]), col))
        out.append(taper(L([(-4, -124), (4, -134), (16, -130), (22, -118)]), 6 * s, 2 * s, col))
    else:
        out.append(f'<path d="{blob(*L([(0, -110)])[0], 8.4 * s, 10 * s, 7, 0.06, 12)}" fill="{col}"/>')
        out.append(f'<path d="{blob(*L([(-1, -104)])[0], 7 * s, 4 * s, 8, 0.1, 10)}" fill="{col}"/>')
    if wreath:
        for k in range(7):
            a = math.radians(-200 + k * 32)
            px, py = L([(math.cos(a) * 8.6, -112 + math.sin(a) * 7)])[0]
            out.append(f'<path d="{blob(px, py, 2.6 * s, 1.3 * s, k, 0.05, 8, math.degrees(a) + 90)}" fill="{wreath}"/>')
    if arm == "up":
        out.append(taper(L([(14, -90), (26, -100), (36, -116)]), 6 * s, 4 * s, col))
    elif arm == "out":
        out.append(taper(L([(16, -90), (30, -84), (44, -84)]), 6 * s, 4.4 * s, col))
    elif arm == "down":
        out.append(taper(L([(16, -90), (22, -70), (24, -52)]), 6 * s, 4 * s, col))
    out.append(taper(L([(-16, -90), (-22, -70), (-21, -52)]), 6 * s, 4 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(4, -119), (8, -112), (6, -102), (14, -97), (23, -90), (22, -72), (17, -58), (19, -40), (25, -10)])), rim, 1.6, 3, 1, 0.75))
    return "".join(out)


def hero_figure(x, base, s, col, facing=1, rim=None, arm="up", drape=None, stride=1.0, lean=0.0):
    """A heroic classical figure seen from behind, statue-like: broad shoulders, tapering torso, a himation wrapped
    at the hips, striding legs; arm 'up' (raised forward-high), 'fwd' (reaching forward) or 'down'. ~132*s tall."""
    def L(pts):
        return T(pts, x, base, s, facing < 0, lean)
    out = []
    # legs
    out.append(taper(catmull(L([(-8, -50), (-12 - 4 * stride, -26), (-18 - 6 * stride, -2)]), 6), 14 * s, 7 * s, col))
    out.append(taper(catmull(L([(8, -50), (14 + 4 * stride, -26), (18 + 8 * stride, -2)]), 6), 14 * s, 7 * s, col))
    for fx in (-18 - 6 * stride, 18 + 8 * stride):
        out.append(poly(L([(fx - 7, 0), (fx + 9, 0), (fx + 4, -5), (fx - 5, -5)]), col))
    torso = L([(-5, -104), (-15, -102), (-24, -99), (-29, -92), (-27, -82), (-21, -70), (-16, -58), (-17, -46), (17, -46), (16, -58), (21, -70), (27, -82), (29, -92), (24, -99), (15, -102), (5, -104)])
    out.append(poly(torso, col))
    out.append(poly(L([(-5, -112), (-5, -102), (5, -102), (5, -112)]), col))
    out.append(f'<path d="{blob(*L([(0, -119)])[0], 8.6 * s, 9.6 * s, 4, 0.08, 12)}" fill="{col}"/>')
    # the himation wrapped round the hips, one end falling
    dr = drape or col
    out.append(poly(L([(-19, -58), (19, -60), (22, -40), (16, -30), (-2, -34), (-20, -32), (-23, -44)]), dr))
    out.append(poly(L([(-20, -40), (-30, -20), (-34, -2), (-24, -4), (-16, -26)]), dr))
    # arms
    if arm == "up":
        out.append(taper(catmull(L([(24, -97), (36, -112), (44, -132)]), 6), 9 * s, 6 * s, col))
    elif arm == "fwd":
        out.append(taper(catmull(L([(24, -97), (40, -96), (56, -100)]), 6), 9 * s, 6 * s, col))
    else:
        out.append(taper(catmull(L([(24, -97), (30, -76), (30, -56)]), 6), 9 * s, 6 * s, col))
    out.append(taper(catmull(L([(-24, -97), (-31, -76), (-30, -56)]), 6), 9 * s, 6 * s, col))
    # muscle hints: spine and shoulder blades
    hint = lt(col, 0.18)
    out.append(pline(L([(0, -100), (1, -80), (0, -60)]), hint, 1.4 * s, 3, 0.6, 1))
    for sg in (-1, 1):
        out.append(pline(L([(sg * 6, -94), (sg * 15, -86), (sg * 12, -76)]), hint, 1.2 * s, 4 + sg, 0.5, 1))
    if rim:
        out.append(ink(smooth_open(L([(3, -128), (8, -122), (8, -113), (16, -102), (27, -97), (29, -90), (27, -82), (21, -70), (16, -58)])), rim, 2.0, 3, 1, 0.85))
        out.append(ink(smooth_open(L([(14 + 4 * stride, -26), (18 + 8 * stride, -4)])), rim, 1.6, 5, 1, 0.7))
        if arm == "up":
            out.append(ink(smooth_open(L([(28, -100), (39, -113), (47, -130)])), rim, 1.6, 6, 1, 0.8))
    return "".join(out)


def stone_blocks(D, d, box, seed, col, rows=6, op=0.35, w=1.2):
    """Ashlar courses drawn inside a clip (masonry)."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{d}"/>')
    h = (y1 - y0) / rows
    lines = []
    for r in range(rows):
        y = y0 + r * h
        lines.append(f'<path d="M {x0} {y:.1f} L {x1} {y + rnd.uniform(-1, 1):.1f}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
        xx = x0 + (r % 2) * h * 0.9 + rnd.uniform(0, h)
        while xx < x1:
            lines.append(f'<path d="M {xx:.1f} {y:.1f} L {xx + rnd.uniform(-1, 1):.1f} {y + h:.1f}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
            xx += h * rnd.uniform(1.4, 2.2)
    return f'<g {cid}>{"".join(lines)}</g>'


def ray_fan(cx, cy, r0, r1, n, col, op, a0=0, a1=360, w=0.06, seed=1):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n + rnd.uniform(-2, 2))
        ww = w * rnd.uniform(0.6, 1.4)
        rr = r1 * rnd.uniform(0.7, 1.05)
        out.append(f'<path d="M {cx + math.cos(a - ww) * r0:.1f} {cy + math.sin(a - ww) * r0:.1f} L {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f} '
                   f'L {cx + math.cos(a + ww) * r0:.1f} {cy + math.sin(a + ww) * r0:.1f} Z" fill="{col}" opacity="{op * rnd.uniform(0.6, 1.1):.2f}"/>')
    return "".join(out)


def snake(D, pts, w0, w1, pal, seed, head=True, tongue="#C8282A", eye="#F2D24A"):
    """A painted serpent along pts (tail first, head last): tapered body, belly highlight, scale ticks, head."""
    path = catmull(pts, 6)
    out = [taper(path, w0, w1, pal[1])]
    out.append(taper([(x - 0.4, y - w1 * 0.18) for x, y in path], w0 * 0.35, w1 * 0.35, pal[0], 0.7))
    rnd = random.Random(seed)
    for i in range(2, len(path) - 2, 2):
        (xa, ya), (xb, yb) = path[i], path[i + 1]
        a = math.atan2(yb - ya, xb - xa)
        ww = (w0 + (w1 - w0) * i / len(path)) * 0.35
        out.append(f'<path d="M {xa - math.sin(a) * ww:.1f} {ya + math.cos(a) * ww:.1f} l {math.cos(a) * 2:.1f} {math.sin(a) * 2:.1f}" stroke="{pal[2]}" stroke-width="1" opacity="0.6"/>')
    if head:
        (xa, ya), (xb, yb) = path[-2], path[-1]
        a = math.degrees(math.atan2(yb - ya, xb - xa))
        hl = w1 * 1.6
        hx, hy = xb + math.cos(math.radians(a)) * hl * 0.3, yb + math.sin(math.radians(a)) * hl * 0.3
        out.append(f'<path d="{blob(hx, hy, hl * 0.62, w1 * 0.62, seed, 0.06, 10, a)}" fill="{pal[1]}"/>')
        out.append(f'<path d="{blob(hx - math.sin(math.radians(a)) * w1 * 0.15, hy - w1 * 0.15, hl * 0.4, w1 * 0.25, seed + 1, 0.06, 10, a)}" fill="{pal[0]}" opacity="0.6"/>')
        tx_, ty_ = hx + math.cos(math.radians(a)) * hl * 0.62, hy + math.sin(math.radians(a)) * hl * 0.62
        if tongue:
            fa = math.radians(a)
            out.append(f'<path d="M {tx_:.1f} {ty_:.1f} l {math.cos(fa) * hl * 0.5:.1f} {math.sin(fa) * hl * 0.5:.1f} l {math.cos(fa - 0.5) * hl * 0.2:.1f} {math.sin(fa - 0.5) * hl * 0.2:.1f} '
                       f'M {tx_ + math.cos(fa) * hl * 0.5:.1f} {ty_ + math.sin(fa) * hl * 0.5:.1f} l {math.cos(fa + 0.5) * hl * 0.2:.1f} {math.sin(fa + 0.5) * hl * 0.2:.1f}" '
                       f'stroke="{tongue}" stroke-width="{max(1, w1 * 0.12):.1f}" fill="none" stroke-linecap="round"/>')
        if eye:
            ex, ey = hx + math.cos(math.radians(a)) * hl * 0.15 - math.sin(math.radians(a)) * w1 * 0.2, hy + math.sin(math.radians(a)) * hl * 0.15 - w1 * 0.2
            out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(1.0, w1 * 0.13):.1f}" fill="{eye}"/>')
    return "".join(out)


def bird_feathers(D, pts, pal, seed, n=None, size=(4, 8), angle=90, op=(0.4, 0.8)):
    """Overlapping scalloped feather marks inside a body outline."""
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    n = n or int((x1 - x0) * (y1 - y0) / 50)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        s = rnd.uniform(*size)
        a = math.radians(angle + rnd.uniform(-15, 15))
        ux, uy = math.cos(a), math.sin(a)
        out.append(f'<path d="M {x - uy * s:.1f} {y + ux * s:.1f} Q {x + ux * s * 1.2:.1f} {y + uy * s * 1.2:.1f} {x + uy * s:.1f} {y - ux * s:.1f}" '
                   f'fill="none" stroke="{rnd.choice(pal)}" stroke-width="{rnd.uniform(1, 1.8):.1f}" opacity="{rnd.uniform(*op):.2f}" stroke-linecap="round"/>')
    return f'<g {cid}>{"".join(out)}</g>'


def chelys_lyre(D, cx, base, s, seed, glow=True, strings="#FFF2C0"):
    """Greek lyre: tortoise-shell sound box, two curved horn arms, crossbar, seven strings. Upright, ~150*s tall."""
    def L(pts):
        return T(pts, cx, base, s)
    out = []
    if glow:
        out.append(soft_glow(D, cx, base - 80 * s, 120 * s, "#FFE8A0", 0.5))
    for sg in (-1, 1):
        arm = L([(sg * 18, -36), (sg * 34, -70), (sg * 30, -104), (sg * 40, -132), (sg * 52, -142)])
        out.append(taper(catmull(arm, 6), 10 * s, 5 * s, "#5A3414"))
        out.append(taper(catmull([(x - sg * 1.5, y - 1) for x, y in arm], 6), 3.4 * s, 1.6 * s, "#E8C27A", 0.85))
        tx_, ty_ = arm[-1]
        out.append(f'<circle cx="{tx_:.1f}" cy="{ty_:.1f}" r="{5 * s:.1f}" fill="#E8C27A" stroke="#5A3414" stroke-width="{1.6 * s:.1f}"/>')
    bar = L([(-40, -120), (40, -120)])
    out.append(taper(catmull([bar[0], (cx, bar[0][1] - 3 * s), bar[1]], 6), 7 * s, 7 * s, "#7A4A1E"))
    out.append(taper([(bar[0][0], bar[0][1] - 2 * s), (bar[1][0], bar[1][1] - 2 * s)], 2 * s, 2 * s, "#F2D08A", 0.8))
    shell = L([(-34, -30), (-26, -46), (0, -52), (26, -46), (34, -30), (30, -10), (0, 2), (-30, -10)])
    out.append(painted(D, shell, ("#E8C27A", "#A8692E", "#4A2A0E"), seed, sdir=(0.5, 0.6), sk=0.18, angle=-20, n=16, inkw=1.4 * s, inkc="#2A1404", hi=0.45))
    for (px, py) in ((0, -26), (-16, -32), (16, -32), (-12, -14), (12, -14)):
        q = L([(px - 7, py), (px, py - 7), (px + 7, py), (px, py + 6)])
        out.append(f'<path d="{pd(q)}" fill="none" stroke="#4A2A0E" stroke-width="{1.2 * s:.1f}" opacity="0.7"/>')
    for k in range(7):
        t = (k - 3) / 3
        a = L([(t * 14, -18)])[0]
        b = L([(t * 30, -120)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{strings}" stroke-width="{max(1.1, 1.3 * s):.1f}" opacity="0.95"/>')
    br = L([(-16, -18), (16, -18)])
    out.append(f'<path d="M {br[0][0]:.1f} {br[0][1]:.1f} L {br[1][0]:.1f} {br[1][1]:.1f}" stroke="#2A1404" stroke-width="{3 * s:.1f}" stroke-linecap="round"/>')
    return "".join(out)


# ================================================================ 1. medusa — seen only in the bronze shield
def helmet_profile(D, cx, cy, s, seed, rim="#F2C870"):
    """Perseus seen from behind-left: a Corinthian helmet in profile (facing left) with a red horsehair crest,
    neck and cloaked shoulder; dark bronze with a warm rim light. (cx, cy) = base of the neck."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = []
    # cloak over the shoulders
    sh = L([(-80, 160), (-74, 70), (-50, 34), (-14, 18), (24, 20), (60, 40), (96, 80), (120, 160)])
    out.append(painted(D, sh, ("#6A2A20", "#2A0E0A", "#0A0302"), seed + 9, sdir=(0.6, 0.3), sk=0.2, angle=-60, n=24, inkw=0, hi=0.3))
    out.append(ink(smooth_open(L([(-74, 70), (-50, 34), (-14, 18)])), rim, 2.2, seed, 1, 0.6))
    out.append(taper(L([(-30, 26), (-18, 60), (-24, 120)]), 4 * s, 2 * s, "#000000", 0.5))
    # neck
    out.append(poly(L([(-16, 22), (-12, -10), (14, -12), (20, 22)]), "#1A0E08"))
    helm = L([(40, -6), (34, -30), (38, -62), (26, -90), (0, -102), (-26, -94), (-42, -72), (-46, -48), (-42, -42), (-48, -34), (-50, -12),
              (-46, 0), (-34, 4), (-20, 12), (-8, 8), (4, -8), (18, 2), (32, 6)])
    out.append(painted(D, helm, ("#E8B868", "#7A5020", "#2A1806"), seed, sdir=(0.7, 0.5), sk=0.22, angle=-70, n=30, inkw=1.8, inkc="#140A02", hi=0.5))
    # eye slot, brow ridge, cheek line and the bright rim along the dome
    out.append(poly(L([(-46, -44), (-34, -48), (-24, -44), (-34, -38)]), "#0A0402"))
    out.append(ink(smooth_open(L([(-44, -50), (-28, -56), (-10, -54)])), "#3A2208", 2, seed + 1, 1, 0.7))
    out.append(ink(smooth_open(L([(-26, -36), (-24, -14), (-30, 2)])), "#3A2208", 1.6, seed + 2, 1, 0.6))
    out.append(ink(smooth_open(L([(-42, -72), (-26, -94), (0, -102), (26, -90)])), "#FFE6A8", 3, seed + 3, 1, 0.8))
    # crest holder and the horsehair crest sweeping back
    out.append(poly(L([(-8, -100), (-4, -110), (6, -110), (10, -100)]), "#5A3A12"))
    crest = L([(-40, -100), (-30, -124), (-6, -138), (24, -136), (52, -120), (70, -92), (78, -56), (74, -30), (62, -40), (58, -78), (40, -106), (14, -116), (-12, -112)])
    out.append(painted(D, crest, ("#F27A5A", "#A82418", "#3A0806"), seed + 4, sdir=(0.6, 0.6), sk=0.18, angle=20, n=50, inkw=1.4, inkc="#2A0402", hi=0.4))
    rnd = random.Random(seed)
    for k in range(26):
        t = rnd.uniform(0.05, 0.95)
        p = catmull(L([(-34, -112), (-6, -130), (24, -128), (52, -112), (66, -86), (72, -50)]), 8)
        x, y = p[int(t * (len(p) - 1))]
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(4, 10):.1f} {rnd.uniform(4, 10):.1f} {rnd.uniform(6, 14):.1f} {rnd.uniform(10, 18):.1f}" stroke="{rnd.choice(["#FFB090", "#6A0A06", "#D8402A"])}" stroke-width="1.5" fill="none" opacity="0.75"/>')
    out.append(ink(smooth_open(L([(-30, -124), (-6, -138), (24, -136), (52, -120)])), "#FFD0A0", 2.4, seed + 5, 1, 0.8))
    return "".join(out)


def medusa_silhouette(D, cx, cy, s, seed, col="#0E1C14"):
    """Head and shoulders with a writhing crown of serpents, dark against the light."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = []
    body = L([(-12, 20), (-34, 30), (-64, 46), (-82, 74), (-90, 140), (90, 140), (82, 74), (64, 46), (34, 30), (12, 20)])
    out.append(poly(body, col))
    rnd = random.Random(seed)
    specs = []
    for k in range(11):
        a0 = math.radians(-196 + k * (212 / 10) + rnd.uniform(-5, 5))
        specs.append((a0, rnd.uniform(52, 78), rnd.choice((-1, 1))))
    pal = ("#6A8A4A", "#22381E", "#060C06")
    # back snakes first (darker), then the head, then front snakes
    for layer in (0, 1):
        for k, (a0, r, curl) in enumerate(specs):
            if (k % 2) != layer:
                continue
            p = [(math.cos(a0) * 14, -14 + math.sin(a0) * 16)]
            for j in range(1, 6):
                t = j / 5
                bend = curl * math.sin(t * math.pi * 1.6) * 0.55
                a = a0 + bend
                p.append((math.cos(a0) * (14 + r * t) + math.cos(a + math.pi / 2) * 10 * math.sin(t * 6), -14 + math.sin(a0) * (16 + r * t) + math.sin(a + math.pi / 2) * 10 * math.sin(t * 6)))
            # the head turns back toward the viewer at the end
            ex, ey = p[-1]
            p.append((ex + math.cos(a0 + curl * 1.2) * 10, ey + math.sin(a0 + curl * 1.2) * 10))
            pp = pal if layer else (lt(pal[0], 0.0), dk(pal[1], 0.25), pal[2])
            out.append(snake(D, L(p), 12 * s, 7 * s, pp, seed + k, tongue="#E8402A", eye="#E8F27A"))
        if layer == 0:
            out.append(poly(L([(-20, -2), (-22, -26), (-12, -40), (4, -42), (18, -32), (22, -10), (16, 10), (8, 22), (-8, 22), (-16, 12)]), col))
            for sg in (-1, 1):
                ex, ey = L([(sg * 8, -14)])[0]
                out.append(f'<path d="{blob(ex, ey, 3.2 * s, 1.6 * s, seed + sg, 0.05, 8)}" fill="#E8F27A" opacity="0.9"/>')
    return "".join(out)


@design("medusa")
def medusa():
    D = Doc2("my-md")
    out = [sky(D, [(0, "#0A1614"), (0.5, "#14302A"), (1, "#060C0A")], 1, 600, ["#1E3A32", "#040A08", "#2A4A3E"], 70)]
    # light shaft from the cave mouth, top left
    g = D.lin([(0, "#E8F2C8", 0.32), (1, "#E8F2C8", 0)], 0, 0, 1, 1)
    out.append(f'<path d="M -20 -10 L 150 -10 L 520 600 L 230 600 Z" fill="{g}"/>')
    rnd = random.Random(3)
    for side in (-1, 1):
        xs = 0 if side < 0 else 600
        wall = [(xs, -10)] + [(xs - side * (44 + 30 * math.sin(y / 60 + side) + rnd.uniform(-8, 8)), y) for y in range(0, 620, 40)] + [(xs, 620)]
        out.append(painted(D, wall, ("#3A4A40", "#18241E", "#060A08"), 4 + side, sdir=(side, 0), sk=0.2, angle=-88, n=60, inkw=0, hi=0.2))
    for k in range(16):
        x = rnd.uniform(-10, 610)
        L_ = rnd.uniform(20, 70) * (1.4 if (x < 140 or x > 460) else 0.6)
        w = L_ * 0.22
        out.append(painted(D, [(x - w, -10), (x + w, -10), (x + w * 0.3, L_ * 0.7), (x, L_), (x - w * 0.3, L_ * 0.7)], ("#5A6A5A", "#243028", "#0A100C"), 20 + k, sk=0.15, n=4, inkw=0, hi=0.4))
        out.append(f'<circle cx="{x:.1f}" cy="{L_ + 6:.1f}" r="1.6" fill="#DFF2D8" opacity="0.7"/>')
    # rubble and a fallen stone hand on the floor (a victim, turned to stone)
    out.append(painted(D, [(-20, 600), (-20, 520), (60, 500), (150, 520), (220, 560), (240, 620)], ("#4A5A4A", "#1E2A22", "#080E0A"), 5, sdir=(0.6, 0.4), sk=0.15, angle=-10, n=30, inkw=0, hi=0.3))
    for (bx, by, br) in ((70, 522, 16), (120, 540, 11), (40, 552, 12), (168, 556, 9)):
        out.append(painted(D, blob_pts(bx, by, br, br * 0.7, int(bx), 0.15, 12), ("#B8BCAE", "#7A7E72", "#30342E"), int(bx), sdir=(0.6, 0.6), sk=0.25, n=4, inkw=1, inkc="#141814", hi=0.5))
    # the shield
    cx, cy, R = 290, 318, 168
    out.append(cast(D, cx + 30, cy + 40, R * 1.1, R * 1.05, "#000000", 0.55, 2))
    rim_pts = ell_pts(cx, cy, R, R, 0, 360, 60)
    rg_ = D.lin([(0, "#FFE7A0"), (0.3, "#C8903A"), (0.55, "#5A3612"), (0.8, "#B07A30"), (1, "#3A2008")], 0, 0, 1, 1)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{rg_}"/>')
    out.append(strokes(D.nid(), smooth_closed(rim_pts), (cx - R, cy - R, cx + R, cy + R), ["#FFE8A8", "#6A4012", "#E8B860"], 5, n=90, angle=-45, length=(10, 30), width=(1, 3), opacity=(0.15, 0.4)))
    # a meander chased into the rim, then rivets
    for k in range(40):
        a = 2 * math.pi * k / 40
        r1, r2 = R - 5, R - 16
        a2 = a + 2 * math.pi / 80
        out.append(f'<path d="M {cx + math.cos(a) * r1:.1f} {cy + math.sin(a) * r1:.1f} L {cx + math.cos(a) * r2:.1f} {cy + math.sin(a) * r2:.1f} L {cx + math.cos(a2) * r2:.1f} {cy + math.sin(a2) * r2:.1f} L {cx + math.cos(a2) * (r1 - 4):.1f} {cy + math.sin(a2) * (r1 - 4):.1f}" stroke="#4A2A08" stroke-width="1.6" fill="none" opacity="0.7"/>')
    Ri = R - 24
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri + 3}" fill="#2A1806"/>')
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{Ri}"/>')
    sc = [f'<rect x="{cx - Ri}" y="{cy - Ri}" width="{2 * Ri}" height="{2 * Ri}" fill="{D.rad([(0, "#F2F6CC"), (0.45, "#A8BA80"), (1, "#2A3A22")], cx=0.5, cy=0.42, r=0.62)}"/>']
    sc.append(f'<path d="{smooth_closed([(cx - 110, cy + 150), (cx - 96, cy - 30), (cx - 50, cy - 104), (cx + 10, cy - 120), (cx + 70, cy - 96), (cx + 106, cy - 20), (cx + 116, cy + 150)])}" fill="#FAFCE6" opacity="0.5"/>')
    sc.append(strokes(D.nid(), f"M {cx - Ri} {cy - Ri} L {cx + Ri} {cy - Ri} L {cx + Ri} {cy + Ri} L {cx - Ri} {cy + Ri} Z", (cx - Ri, cy - Ri, cx + Ri, cy + Ri),
                      ["#F2F6D0", "#5A7048", "#C8D8A0"], 7, n=80, angle=-80, length=(20, 60), width=(2, 5), opacity=(0.1, 0.25)))
    for sg in (-1, 1):
        sc.append(poly([(cx + sg * 150, cy + 150), (cx + sg * 126, cy - 40), (cx + sg * 96, cy - 120), (cx + sg * 70, cy - 150), (cx + sg * 160, cy - 160)], "#1A2A1E", 0.9))
    # two of her victims, turned to stone, flanking her in the reflection
    for sg, h in ((-1, 0.62), (1, 0.55)):
        fx = cx + sg * 92
        sc.append(robed_figure(fx, cy + 150, h, "#9A9C90", facing=-sg, arm="up", head="helmet"))
    sc.append(medusa_silhouette(D, cx, cy + 22, 1.0, 11))
    sc.append(f'<path d="{smooth_open(ell_pts(cx - 20, cy - 16, Ri * 0.92, Ri * 0.9, 190, 260, 12))}" stroke="#FFFFFF" stroke-width="10" fill="none" opacity="0.18" stroke-linecap="round"/>')
    sc.append(f'<path d="{smooth_open(ell_pts(cx - 20, cy - 16, Ri * 0.8, Ri * 0.78, 200, 236, 8))}" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/>')
    sc.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri}" fill="{D.rad([(0, "#000000", 0), (0.75, "#000000", 0), (1, "#2A1806", 0.6)])}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri}" fill="none" stroke="#FFE7A0" stroke-width="2" opacity="0.6"/>')
    out.append(ink(smooth_closed(rim_pts), "#1A0C02", 2.4, 6, 2, 0.8))
    # Perseus: his arm up to the rim, his crested helmet turned to the shield
    out.append(taper(catmull([(520, 560), (480, 500), (452, 468), (436, 456)], 6), 30, 22, "#1A0A06"))
    out.append(ink(smooth_open([(500, 520), (470, 482), (446, 462)]), "#F2C870", 2, 4, 1, 0.6))
    out.append(f'<path d="{blob(432, 452, 15, 12, 4, 0.12, 10, -30)}" fill="#3A2214"/>')
    out.append(helmet_profile(D, 484, 512, 0.92, 12))
    # lettering
    out.append(gilt(D, 300, 104, "MEDUSA", CINZEL, 66, ls=16, max_w=420, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 134, "GREEK · SEEN ONLY IN THE BRONZE SHIELD", CINZEL, 16, "#DCEAD0", ls=2.5, max_w=430))
    return fin(D, out, 14)


# ================================================================ 2. the labyrinth — Ariadne's thread, from above
def make_maze(nx, ny, seed, court=None):
    """Recursive-backtracker maze; returns open set of grid cells on a (2nx+1)x(2ny+1) lattice."""
    rnd = random.Random(seed)
    W, H = 2 * nx + 1, 2 * ny + 1
    open_ = set()
    seen = set()
    if court:
        cx0, cy0, cx1, cy1 = court
        for i in range(cx0, cx1 + 1):
            for j in range(cy0, cy1 + 1):
                seen.add((i, j))
                for gi in range(2 * i + 1, 2 * i + 2):
                    pass
        for gx in range(2 * cx0 + 1, 2 * cx1 + 2):
            for gy in range(2 * cy0 + 1, 2 * cy1 + 2):
                open_.add((gx, gy))
    start = (0, ny - 1)
    stack = [start]
    seen.add(start)
    open_.add((1, 2 * (ny - 1) + 1))
    while stack:
        cx, cy = stack[-1]
        nb = [(cx + dx, cy + dy, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= cx + dx < nx and 0 <= cy + dy < ny and (cx + dx, cy + dy) not in seen]
        if not nb:
            stack.pop()
            continue
        nx_, ny_, dx, dy = rnd.choice(nb)
        seen.add((nx_, ny_))
        open_.add((2 * cx + 1 + dx, 2 * cy + 1 + dy))
        open_.add((2 * nx_ + 1, 2 * ny_ + 1))
        stack.append((nx_, ny_))
    if court:
        open_.add((2 * ((court[0] + court[2]) // 2) + 1, 2 * court[3] + 2))
    return open_, W, H


def maze_path(open_, a, b):
    from collections import deque
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in open_ and n not in prev:
                prev[n] = c
                q.append(n)
    path = []
    c = b
    while c is not None:
        path.append(c)
        c = prev.get(c)
    return path[::-1]


@design("the-labyrinth")
def the_labyrinth():
    D = Doc2("my-lb")
    # dusk-lit hillside of Crete around the maze
    out = [sky(D, [(0, "#6A5A3A"), (1, "#3A3020")], 1, 600, ["#7A6A44", "#2A2214", "#8A7A50"], 80)]
    out.append(grass(2, (0, 0, 600, 600), ["#6A7A3A", "#4A5A2A", "#8A9A4A"], 260, (6, 12), 1.4))
    nx, ny = 11, 8
    cell, wall = 26, 12
    per = cell + wall
    W, H = 2 * nx + 1, 2 * ny + 1
    tw = (nx + 1) * wall + nx * cell
    th = (ny + 1) * wall + ny * cell
    x0, y0 = 300 - tw / 2, 84
    court = (4, 3, 6, 5)
    open_, _, _ = make_maze(nx, ny, 7, court)
    ent = (11, H - 1)
    open_.add(ent)
    open_.add((11, H - 2))

    def gx(i):
        return x0 + (i // 2) * per + (wall if i % 2 else 0)

    def gw(i):
        return cell if i % 2 else wall

    def gy(j):
        return y0 + (j // 2) * per + (wall if j % 2 else 0)
    # floor
    floor = rect_pts(x0, y0, x0 + tw, y0 + th, 30, 2, 0.6)
    out.append(painted(D, floor, ("#D8B078", "#A87A42", "#5A3A1A"), 3, sdir=(0.6, 0.6), sk=0.0, angle=-10, n=200, slen=(10, 30), sw=(1, 3), inkw=0, hi=0))
    out.append(f'<path d="{pd(floor)}" fill="{D.rad([(0, "#000000", 0), (0.5, "#000000", 0.1), (1, "#1A0A04", 0.55)], cx=0.45, cy=0.4, r=0.75)}"/>')
    out.append(specks(4, (x0, y0, x0 + tw, y0 + th), ["#8A6A3A", "#F2DCA8"], 260, (0.6, 1.8), (0.3, 0.7)))
    # torch glows (under the walls)
    path = maze_path(open_, ent, (2 * 5 + 1, 2 * 4 + 1))
    assert len(path) > 10, len(path)
    glow_at = [path[int(len(path) * t)] for t in (0.18, 0.62)]
    for (i, j) in glow_at:
        out.append(soft_glow(D, gx(i) + gw(i) / 2, gy(j) + gw(j) / 2, 70, "#FFC860", 0.55))
    # the walls: shadow pass, then the lit tops
    shadows, tops = [], []
    rnd = random.Random(9)
    for i in range(W):
        for j in range(H):
            if (i, j) in open_:
                continue
            x, y, w, h = gx(i), gy(j), gw(i), gw(j)
            shadows.append(f'<rect x="{x + 5:.1f}" y="{y + 8:.1f}" width="{w + 1:.1f}" height="{h + 1:.1f}" fill="#1A0A04" opacity="0.6"/>')
            tops.append((x, y, w, h))
    out.append("".join(shadows))
    tg = D.lin([(0, "#F6E2B8"), (1, "#C8A06A")], 0, 0, 1, 1)
    out.append("".join(f'<rect x="{x - 0.3:.1f}" y="{y - 0.3:.1f}" width="{w + 0.6:.1f}" height="{h + 0.6:.1f}" fill="{tg}"/>' for x, y, w, h in tops))
    # south faces (a little height), block joints and wear
    for x, y, w, h in tops:
        out.append(f'<rect x="{x:.1f}" y="{y + h - 2.6:.1f}" width="{w:.1f}" height="2.6" fill="#9A6A3A" opacity="0.7"/>')
        if w > wall:
            out.append(f'<path d="M {x + w * rnd.uniform(0.3, 0.7):.1f} {y:.1f} l 0 {h:.1f}" stroke="#8A6A40" stroke-width="1" opacity="0.6"/>')
        if h > wall:
            out.append(f'<path d="M {x:.1f} {y + h * rnd.uniform(0.3, 0.7):.1f} l {w:.1f} 0" stroke="#8A6A40" stroke-width="1" opacity="0.6"/>')
        if rnd.random() < 0.18:
            out.append(f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, h):.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="#6A7A3A" opacity="0.8"/>')
    out.append(ink(pd([(x0, y0), (x0 + tw, y0), (x0 + tw, y0 + th), (x0, y0 + th)]), "#3A2410", 1.6, 3, 1, 0.6))
    # Ariadne's thread from the gate to the court
    pts = []
    rnd2 = random.Random(5)
    for k, (i, j) in enumerate(path):
        if k % 1 == 0:
            pts.append((gx(i) + gw(i) / 2 + rnd2.uniform(-2.5, 2.5), gy(j) + gw(j) / 2 + rnd2.uniform(-2.5, 2.5)))
    pts.insert(0, (pts[0][0], pts[0][1] + 40))
    thread = catmull(pts, 4)
    stop = int(len(thread) * 0.62)
    out.append(taper([(x + 1.5, y + 2) for x, y in thread[:stop]], 2.6, 2.6, "#2A0A04", 0.35))
    out.append(taper(thread[:stop], 3, 3, "#D8202A"))
    out.append(taper([(x - 0.6, y - 0.6) for x, y in thread[:stop]], 1, 1, "#FF9A8A", 0.8))
    # Theseus from above with his torch, the ball of thread unwinding in his hand
    hx, hy = thread[stop - 1]
    out.append(soft_glow(D, hx, hy, 60, "#FFD070", 0.75))
    out.append(f'<ellipse cx="{hx + 3:.1f}" cy="{hy + 5:.1f}" rx="9" ry="7" fill="#1A0A04" opacity="0.4"/>')
    out.append(f'<path d="{blob(hx, hy, 9, 6.5, 3, 0.1, 12, 30)}" fill="#7A2A1A"/>')
    out.append(f'<circle cx="{hx - 1:.1f}" cy="{hy - 1:.1f}" r="4.6" fill="#3A2210"/>')
    out.append(f'<circle cx="{hx + 9:.1f}" cy="{hy - 7:.1f}" r="4" fill="#FFE070"/><circle cx="{hx + 9:.1f}" cy="{hy - 7:.1f}" r="2" fill="#FFFFFF"/>')
    out.append(f'<circle cx="{hx - 8:.1f}" cy="{hy + 5:.1f}" r="4" fill="#D8202A"/>')
    # the Minotaur waiting in the central court: horned shadow from above
    ccx, ccy = gx(11) + cell / 2, gy(9) + cell / 2 + 4
    out.append(soft_glow(D, ccx, ccy, 70, "#1A0A04", 0.5))
    out.append(f'<ellipse cx="{ccx + 6:.1f}" cy="{ccy + 10:.1f}" rx="26" ry="20" fill="#1A0A04" opacity="0.45"/>')
    out.append(poly([(ccx - 22, ccy + 18), (ccx - 26, ccy + 2), (ccx - 14, ccy - 8), (ccx, ccy - 10), (ccx + 14, ccy - 8), (ccx + 26, ccy + 2), (ccx + 22, ccy + 18), (ccx, ccy + 22)], "#2A1408"))
    out.append(poly([(ccx - 9, ccy - 6), (ccx - 8, ccy - 22), (ccx, ccy - 28), (ccx + 8, ccy - 22), (ccx + 9, ccy - 6)], "#2A1408"))
    for sg in (-1, 1):
        out.append(taper(catmull([(ccx + sg * 6, ccy - 20), (ccx + sg * 22, ccy - 24), (ccx + sg * 32, ccy - 36), (ccx + sg * 30, ccy - 48)], 6), 6, 1.4, "#EADBB8"))
    out.append(f'<circle cx="{ccx - 3:.1f}" cy="{ccy - 26:.1f}" r="1.6" fill="#FF6A3A"/><circle cx="{ccx + 3:.1f}" cy="{ccy - 26:.1f}" r="1.6" fill="#FF6A3A"/>')
    # title band: Minoan spirals and a gilt name
    by = 444
    band = rect_pts(-10, by, 610, 620, 40, 3, 0.5)
    out.append(painted(D, band, ("#3A1A14", "#24100C", "#0C0404"), 6, sdir=(0, -1), sk=0.05, angle=0, n=40, inkw=0, hi=0))
    out.append(f'<path d="M 0 {by} L 600 {by}" stroke="#D9A945" stroke-width="3"/>')
    for k in range(13):
        x = 24 + k * 46
        out.append(f'<path d="M {x - 14} {by + 14} C {x - 14} {by + 6} {x} {by + 4} {x} {by + 12} C {x} {by + 18} {x - 8} {by + 18} {x - 8} {by + 13}" stroke="#D9A945" stroke-width="2.2" fill="none"/>')
        out.append(f'<path d="M {x} {by + 12} C {x} {by + 22} {x + 16} {by + 22} {x + 16} {by + 13} C {x + 16} {by + 6} {x + 8} {by + 7} {x + 8} {by + 12}" stroke="#D9A945" stroke-width="2.2" fill="none"/>')
    out.append(gilt(D, 300, 506, "The Labyrinth", SERIF_IT, 58, max_w=420, seed=8, deboss="#000000", dop=0.8))
    out.append(tx(300, 536, "GREEK · FOLLOW ARIADNE’S THREAD", CINZEL, 17, "#F2D8B0", ls=3, max_w=420))
    return fin(D, out, 15)


# ================================================================ 3. orpheus — the lyre at the gates of the underworld
def cerberus_asleep(x, base, s, col, rim=None, flip=False):
    """Three-headed hound lying down, all three heads lowered on the paws, asleep."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-70, 0), (-74, -18), (-60, -34), (-20, -40), (20, -38), (46, -30), (50, -10), (40, 0)]), col)]
    out.append(taper(L([(-70, -10), (-92, -14), (-104, -6), (-112, -10)]), 8 * s, 3 * s, col))
    for k, (hx, hy, a) in enumerate(((36, -24, -10), (54, -14, 10), (26, -8, 25))):
        out.append(taper(L([(20, -26), (hx - 6, hy - 4), (hx, hy)]), 18 * s, 14 * s, col))
        out.append(poly(L([(hx - 4, hy - 8), (hx + 18, hy - 4), (hx + 30, hy + 2), (hx + 28, hy + 8), (hx + 6, hy + 8), (hx - 6, hy + 4)]), col))
        out.append(poly(L([(hx + 2, hy - 8), (hx + 6, hy - 18), (hx + 10, hy - 7)]), col))
        if rim:
            out.append(ink(smooth_open(L([(hx + 6, hy - 18), (hx + 10, hy - 7), (hx + 18, hy - 4), (hx + 30, hy + 2)])), rim, 1.3, k, 1, 0.7))
    out.append(taper(L([(30, 0), (60, 2), (76, 4)]), 8 * s, 6 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(-74, -18), (-60, -34), (-20, -40), (20, -38)])), rim, 1.5, 9, 1, 0.6))
    return "".join(out)


def cerberus_sitting(D, x, base, s, col, rim=None, flip=False):
    """Three-headed hound sitting up on guard (facing left), the three heads drooping asleep."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = []
    body = L([(-26, 0), (-17, 0), (-15, -30), (-6, -38), (10, -32), (22, -8), (42, 0), (58, -4), (56, -30), (44, -54), (22, -68), (2, -78),
              (-14, -80), (-24, -68), (-27, -40)])
    out.append(poly(body, col))
    out.append(taper(L([(56, -4), (76, 0), (88, -8), (84, -18)]), 9 * s, 3 * s, col))
    out.append(taper(L([(-10, -30), (-8, -6), (-6, 0)]), 8 * s, 7 * s, col))
    heads = [((-6, -74), (-34, -66), 18), ((-2, -78), (-22, -98), -4), ((6, -76), (10, -104), -20)]
    for k, (n0, (hx, hy), a) in enumerate(heads):
        out.append(taper(L([n0, ((n0[0] + hx) / 2, (n0[1] + hy) / 2 - 2), (hx, hy)]), 18 * s, 14 * s, col))
        hp = T([(-24, 4), (-26, -2), (-14, -6), (-4, -12), (4, -10), (8, 0), (2, 8), (-12, 8)], 0, 0, 1, False, a)
        out.append(poly(L([(hx + px, hy + py) for px, py in hp]), col))
        ep = T([(-2, -10), (0, -22), (6, -10)], 0, 0, 1, False, a)
        out.append(poly(L([(hx + px, hy + py) for px, py in ep]), col))
        if rim:
            rp = T([(0, -22), (6, -10), (8, 0), (2, 8)], 0, 0, 1, False, a)
            out.append(ink(smooth_open(L([(hx + px, hy + py) for px, py in rp])), rim, 1.6, k, 1, 0.8))
        # closed eye, a sleepy line
        ce = T([(-10, -4), (-6, -3)], 0, 0, 1, False, a)
        q = L([(hx + px, hy + py) for px, py in ce])
        out.append(f'<path d="M {q[0][0]:.1f} {q[0][1]:.1f} L {q[1][0]:.1f} {q[1][1]:.1f}" stroke="{rim or "#FFFFFF"}" stroke-width="1.4" opacity="0.7"/>')
    # a spiked collar on each neck
    for k, (n0, (hx, hy), a) in enumerate(heads):
        cx_, cy_ = L([((n0[0] * 0.4 + hx * 0.6), (n0[1] * 0.4 + hy * 0.6))])[0]
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{3 * s:.1f}" fill="#C8902A"/>')
    if rim:
        out.append(ink(smooth_open(L([(22, -68), (44, -54), (56, -30), (58, -4)])), rim, 2, 9, 1, 0.8))
    return "".join(out)


def asphodel(D, x, base, h, seed, col="#F2ECF8"):
    rnd = random.Random(seed)
    out = [taper([(x, base), (x + rnd.uniform(-3, 3), base - h * 0.5), (x + rnd.uniform(-4, 4), base - h)], 2.2, 1, "#6A8A6A")]
    for k in range(8):
        t = 0.55 + k * 0.06
        px, py = x + rnd.uniform(-4, 4) * t, base - h * t
        for sg in (-1, 1):
            out.append(f'<path d="{blob(px + sg * 3.5, py, 3.4, 1.8, seed + k * 2 + sg, 0.1, 8, sg * 30)}" fill="{col}" opacity="0.9"/>')
    return "".join(out)


@design("orpheus")
def orpheus():
    D = Doc2("my-or")
    out = [sky(D, [(0, "#120A22"), (0.45, "#2A1A44"), (0.75, "#4A2A5A"), (1, "#1A0E24")], 1, 600, ["#3A2A5A", "#0A0614", "#5A3A6A"], 60)]
    # the great cavern mouth of Hades and its bronze gates
    gx0, gx1, gtop, gbase = 300, 520, 150, 400
    cave = [(200, 420), (214, 300), (250, 200), (320, 132), (410, 112), (500, 132), (566, 200), (600, 300), (610, 420)]
    out.append(painted(D, [(140, 430), (150, 260), (210, 140), (330, 70), (460, 60), (580, 100), (640, 200), (640, 430)], ("#4A3A5A", "#24182E", "#0A0610"), 2, sdir=(0.6, 0.2), sk=0.12, angle=-80, n=80, inkw=0, hi=0.25))
    out.append(poly(cave, "#06040A"))
    out.append(soft_glow(D, 410, 300, 160, "#B84A3A", 0.45))
    out.append(soft_glow(D, 410, 320, 80, "#FF9A5A", 0.4))
    gw_ = 74
    for side in (-1, 1):
        x_a = 410 + (0 if side < 0 else 6)
        x_b = 410 + side * gw_ * (0.65 if side < 0 else 0.55)
        # each leaf swung slightly open, drawn as a skewed panel
        top_y, bot_y = 196, 404
        leaf = [(x_a + side * 3, top_y + 4), (x_b, top_y - side * 6 - 4), (x_b, bot_y + 6), (x_a + side * 3, bot_y)]
        out.append(painted(D, poly_pts(leaf, 12, 3 + side, 0.4), ("#C89A5A", "#6A4420", "#24140A"), 5 + side, sdir=(side, 0.2), sk=0.2, angle=-90, n=30, inkw=1.6, inkc="#100804", hi=0.35))
        for k in range(5):
            t = (k + 0.5) / 5
            xa, xb = x_a + side * 3, x_b
            y_a = top_y + 4 + (bot_y - top_y - 4) * t
            y_b = top_y - side * 6 - 4 + (bot_y + 10 - top_y + side * 6) * t
            out.append(f'<path d="M {xa:.1f} {y_a:.1f} L {xb:.1f} {y_b:.1f}" stroke="#2A160A" stroke-width="2.2" opacity="0.7"/>')
            for j in range(3):
                u = (j + 0.5) / 3
                out.append(f'<circle cx="{xa + (xb - xa) * u:.1f}" cy="{y_a + (y_b - y_a) * u - 10:.1f}" r="2" fill="#F2C870" opacity="0.85"/>')
    # Eurydice, a pale shade, waiting in the opening between the gates
    out.append(soft_glow(D, 412, 330, 50, "#E8E8FF", 0.5))
    out.append(robed_figure(412, 402, 0.62, "#DCDCF2", facing=1, arm=None))
    out.append(f'<path d="{smooth_closed(T([(-10, -98), (-26, -60), (-30, -10), (-16, -4), (-12, -60)], 412, 402, 0.62))}" fill="#C8C8E8" opacity="0.6"/>')
    # Cerberus asleep at the threshold
    out.append(soft_glow(D, 506, 360, 120, "#E8603A", 0.55))
    out.append(cerberus_sitting(D, 500, 424, 1.05, "#0E0812", rim="#FFB080"))
    for k, (zx, zy) in enumerate(((474, 270), (488, 252), (504, 232))):
        out.append(tx(zx, zy, "z", SERIF_IT, 15 + k * 4, "#FFD8C0", max_w=40, op=0.85))
    # the dark river and its far bank
    out.append(sea(D, 420, 620, [(0, "#2A1E3A"), (0.5, "#140E24"), (1, "#06040C")], 7, ["#4A3A6A", "#06040C", "#8A6AA0"], 70))
    out.append(f'<path d="{blob(410, 434, 70, 8, 3, 0.2, 14)}" fill="#FF9A5A" opacity="0.25"/>')
    out.append(wave_lines(8, (0, 428, 600, 600), ["#8A6AA0", "#F2C8A0", "#3A2A5A"], 60, (10, 30), 1.6, 2, (0.3, 0.6)))
    # Charon's ferry with its lantern, far off on the water
    bx, bw = 330, 0
    out.append(poly([(bx - 46, 452), (bx + 40, 452), (bx + 54, 442), (bx + 34, 462), (bx - 36, 462), (bx - 56, 444)], "#06040A"))
    out.append(taper([(bx + 4, 452), (bx + 30, 398), (bx + 36, 386)], 2.6, 2, "#06040A"))
    out.append(robed_figure(bx - 6, 454, 0.38, "#06040A", facing=1, cloak=0.3, arm="up"))
    out.append(f'<path d="{blob(bx - 6, 412, 6, 5, 2, 0.1, 10)}" fill="#06040A"/>')
    out.append(soft_glow(D, bx - 40, 432, 28, "#FFD070", 0.85))
    out.append(taper([(bx - 30, 418), (bx - 40, 422), (bx - 40, 428)], 1.6, 1.4, "#06040A"))
    out.append(f'<circle cx="{bx - 40}" cy="432" r="3" fill="#FFF2B0"/>')
    out.append(f'<path d="{blob(bx - 40, 470, 8, 14, 3, 0.2, 10)}" fill="#FFD070" opacity="0.3"/>')
    # Orpheus on the near rock with his lyre, from behind
    out.append(painted(D, [(-20, 600), (-20, 470), (60, 452), (150, 462), (230, 500), (280, 560), (300, 620)], ("#4A3A52", "#20162A", "#06040A"), 12, sdir=(0.7, 0.3), sk=0.15, angle=-10, n=40, inkw=0, hi=0.3))
    for k in range(9):
        out.append(asphodel(D, 20 + k * 30 + (k % 2) * 8, 478 + (k % 3) * 8, 30 + (k % 4) * 6, 30 + k))
    out.append(robed_figure(150, 486, 1.45, "#0A0610", facing=1, rim="#FFB070", cloak=0.5, arm="out", wreath="#C8A040"))
    out.append(chelys_lyre(D, 226, 382, 0.72, 4))
    # music rising toward the gates: golden sparks and notes
    rnd = random.Random(14)
    sp = catmull([(232, 290), (280, 250), (330, 248), (380, 270)], 10)
    for k, (x, y) in enumerate(sp):
        out.append(sparkle(x + rnd.uniform(-10, 10), y + rnd.uniform(-14, 14), rnd.uniform(2, 5), rnd.choice(["#FFE8A0", "#FFFFFF", "#FFC870"]), rnd.uniform(0.6, 1)))
    # lettering
    out.append(gilt(D, 300, 104, "ORPHEUS", CINZEL, 58, ls=14, max_w=380, seed=10, deboss="#000000", dop=0.8))
    out.append(tx(300, 134, "GREEK · THE SINGER AT THE GATES OF HADES", CINZEL, 15, "#E8D8F2", ls=2, max_w=430))
    out.append(letters(D, 300, 552, "Don’t look back.", SERIF_IT, 52, "#FFF2E0", ["#FFFFFF", "#FFE0C0", "#F2D8FF"], 15, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.5))
    return fin(D, out, 16)


# ================================================================ 4. athena's owl — on the olive above the Acropolis
def little_owl(D, cx, cy, s, seed):
    """Athene noctua: compact body, flat round head, white brows, yellow eyes, spotted brown plumage. cy ~ belly."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = [poly(L([(-12, 50), (-16, 76), (0, 82), (16, 76), (12, 50)]), "#5A3A1A")]
    for k in range(3):
        a_, b_ = L([(-8 + k * 8, 56), (-9 + k * 9, 78)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#F2E2C8" stroke-width="1.4" opacity="0.6"/>')
    body = L([(-34, -30), (-40, 0), (-34, 34), (-20, 52), (0, 58), (20, 52), (34, 34), (40, 0), (34, -30), (0, -40)])
    out.append(painted(D, body, ("#D8B88A", "#9A7448", "#4A3218"), seed, sdir=(0.6, 0.4), sk=0.2, angle=-90, n=40, inkw=1.8, inkc="#2A1A0A", hi=0.4))
    # pale streaked breast
    breast = L([(-20, -16), (-24, 14), (-14, 44), (0, 50), (14, 44), (24, 14), (20, -16), (0, -22)])
    out.append(painted(D, breast, ("#FFF6E6", "#EAD8BA", "#B89A72"), seed + 1, sdir=(0.5, 0.4), sk=0.15, angle=-90, n=14, inkw=0, hi=0.3))
    rnd = random.Random(seed)
    for k in range(26):
        px, py = L([(rnd.uniform(-18, 18), rnd.uniform(-12, 44))])[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} q 1 {4 * s:.1f} 0 {8 * s:.1f}" stroke="#7A5430" stroke-width="{2.2 * s:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    # wings folded on each side with white spots
    for sg in (-1, 1):
        wing = L([(sg * 22, -24), (sg * 40, -6), (sg * 42, 24), (sg * 32, 50), (sg * 18, 62), (sg * 22, 30), (sg * 20, 0)])
        out.append(painted(D, wing, ("#C09A6A", "#7A5430", "#3A2410"), seed + 2 + sg, sdir=(-sg * 0.3, 0.5), sk=0.2, angle=-80, n=16, inkw=1.6, inkc="#2A1A0A", hi=0.3))
        for k in range(9):
            px, py = L([(sg * rnd.uniform(26, 38), rnd.uniform(-8, 46))])[0]
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(1.4, 2.6) * s:.1f}" fill="#FFF6E6" opacity="0.9"/>')
    out.append(bird_feathers(D, body, ["#5A3A1A", "#F2E2C8"], seed + 3, n=60, size=(3, 6), angle=90, op=(0.25, 0.6)))
    # head, turned a little toward us
    hx_, hy_ = L([(0, -40)])[0]
    out.append(f'<g transform="rotate(-7 {hx_:.1f} {hy_:.1f})">')
    head = L([(-36, -46), (-38, -64), (-30, -84), (-12, -92), (12, -92), (30, -84), (38, -64), (36, -46), (20, -36), (0, -34), (-20, -36)])
    out.append(painted(D, head, ("#D8B88A", "#9A7448", "#4A3218"), seed + 5, sdir=(0.5, 0.5), sk=0.15, angle=-60, n=24, inkw=1.8, inkc="#2A1A0A", hi=0.4))
    for k in range(22):
        px, py = L([(rnd.uniform(-30, 30), rnd.uniform(-88, -70))])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(1, 1.8) * s:.1f}" fill="#FFF6E6" opacity="0.85"/>')
    # facial disc, brows, eyes, beak
    for sg in (-1, 1):
        ex, ey = L([(sg * 15, -60)])[0]
        out.append(f'<path d="{blob(ex, ey + 2 * s, 16 * s, 15 * s, seed + 7 + sg, 0.06, 14)}" fill="#E8D2AE"/>')
        out.append(taper(catmull(L([(sg * 3, -70), (sg * 14, -78), (sg * 28, -72)]), 6), 5 * s, 2 * s, "#FFFDF4"))
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{10 * s:.1f}" fill="#F6C81C" stroke="#3A2408" stroke-width="{1.6 * s:.1f}"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5.6 * s:.1f}" fill="#0A0604"/>')
        out.append(f'<circle cx="{ex - 2.2 * s:.1f}" cy="{ey - 2.6 * s:.1f}" r="{2 * s:.1f}" fill="#FFFFFF"/>')
    out.append(sharp(L([(-4, -54), (4, -54), (0, -42)]), "#C8B070"))
    out.append(taper(L([(-6, -40), (0, -38), (6, -40)]), 2 * s, 2 * s, "#FFFDF4", 0.9))
    out.append(ink(smooth_open(L([(-30, -84), (-12, -92), (12, -92), (30, -84), (38, -64)])), "#FFF6DA", 2.2, seed, 1, 0.55))
    out.append('</g>')
    # talons on the branch
    for sg in (-1, 1):
        for k in range(3):
            fx, fy = L([(sg * 10 + (k - 1) * 4, 58)])[0]
            out.append(f'<path d="M {fx:.1f} {fy:.1f} q {1.5 * s:.1f} {5 * s:.1f} {-1 * s:.1f} {8 * s:.1f}" stroke="#4A3A2A" stroke-width="{2.4 * s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def parthenon(D, cx, base, w, seed, col="#E8E0F2", shade="#8A80A8", lit="#FFF8E8"):
    out = []
    h = w * 0.36
    x0, x1 = cx - w / 2, cx + w / 2
    st = base - h * 0.12
    for k in range(3):
        out.append(f'<rect x="{x0 - 6 + k * 2:.1f}" y="{base - (k + 1) * h * 0.04:.1f}" width="{w + 12 - k * 4:.1f}" height="{h * 0.04:.1f}" fill="{col if k % 2 else shade}"/>')
    n = 9
    for i in range(n):
        x = x0 + 4 + (w - 8) * i / (n - 1)
        out.append(f'<rect x="{x - w * 0.018:.1f}" y="{base - h * 0.78:.1f}" width="{w * 0.036:.1f}" height="{h * 0.66:.1f}" fill="{col}"/>')
        out.append(f'<rect x="{x + w * 0.004:.1f}" y="{base - h * 0.78:.1f}" width="{w * 0.014:.1f}" height="{h * 0.66:.1f}" fill="{shade}" opacity="0.6"/>')
    out.append(f'<rect x="{x0 - 2:.1f}" y="{base - h * 0.92:.1f}" width="{w + 4:.1f}" height="{h * 0.14:.1f}" fill="{col}"/>')
    out.append(f'<path d="M {x0 - 4:.1f} {base - h * 0.92:.1f} L {cx:.1f} {base - h * 1.12:.1f} L {x1 + 4:.1f} {base - h * 0.92:.1f} Z" fill="{lit}"/>')
    out.append(f'<path d="M {x0 + 8:.1f} {base - h * 0.94:.1f} L {cx:.1f} {base - h * 1.06:.1f} L {x1 - 8:.1f} {base - h * 0.94:.1f} Z" fill="{shade}" opacity="0.5"/>')
    return "".join(out)


def olive_branch(D, pts, seed, s=1.0, olives=True, pal=("#D8DCC0", "#8A9A72", "#3E4A30")):
    path = catmull(pts, 8)
    out = [taper(path, 12 * s, 3 * s, "#5A4630")]
    out.append(taper([(x, y - 2 * s) for x, y in path], 3 * s, 1 * s, "#A08A6A", 0.7))
    rnd = random.Random(seed)
    for i in range(3, len(path) - 1, 3):
        (xa, ya), (xb, yb) = path[i], path[i + 1]
        a = math.degrees(math.atan2(yb - ya, xb - xa))
        for sg in (-1, 1):
            if rnd.random() < 0.15:
                continue
            ang = a + sg * rnd.uniform(30, 60)
            L_ = rnd.uniform(26, 38) * s
            out.append(leaf_simple(D, xa, ya, L_, L_ * 0.2, ang, pal if rnd.random() < 0.6 else ("#E8ECD8", "#A8B494", "#5A6A48"), seed + i * 3 + sg, vein=True, inkw=1.0, inkc="#2E3A22"))
        if olives and rnd.random() < 0.3:
            ox, oy = xa + rnd.uniform(-6, 6), ya + rnd.uniform(6, 12)
            out.append(f'<path d="{blob(ox, oy, 5.4 * s, 7 * s, seed + i, 0.05, 10, 20)}" fill="#2A2A3A"/><circle cx="{ox - 1.6 * s:.1f}" cy="{oy - 2.4 * s:.1f}" r="{1.6 * s:.1f}" fill="#B8B8D8"/>')
    return "".join(out)


@design("athenas-owl")
def athenas_owl():
    D = Doc2("my-ow")
    out = [sky(D, [(0, "#0A1430"), (0.55, "#1E3A6A"), (0.85, "#3A4A7A"), (1, "#6A6A8A")], 1, 600, ["#2A4A7A", "#0A1430", "#5A6A9A"], 60)]
    out.append(stars_field(3, (0, 0, 600, 360), 110))
    out.append(moon(D, 372, 232, 124, 4, gs=0.6))
    # the Acropolis rock and the Parthenon, moonlit, far below; the lamps of Athens
    rock = [(-20, 600), (-20, 452), (30, 436), (66, 404), (100, 394), (232, 392), (262, 404), (300, 430), (360, 456), (440, 480), (620, 500), (620, 600)]
    out.append(painted(D, rock, ("#9A8AA8", "#5A4A6A", "#24182E"), 5, sdir=(-0.4, 0.6), sk=0.15, angle=-80, n=70, inkw=0, hi=0.35))
    out.append(ink(smooth_open(rock[2:7]), "#E8E0FF", 2, 5, 1, 0.4))
    out.append(soft_glow(D, 160, 370, 120, "#FFF2D8", 0.25))
    out.append(parthenon(D, 160, 396, 124, 6))
    for (cx_, h_) in ((60, 34), (246, 30), (272, 26)):
        out.append(conifer(cx_, 410 if cx_ < 100 else 404, h_, "#1A1430", cx_, width=0.22))
    rnd = random.Random(8)
    for k in range(90):
        x, y = rnd.uniform(0, 600), rnd.uniform(462, 600)
        if y < 452 + x * 0.08:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFD27A" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append(mist(D, 470, 50, 9, "#C8B8D8", 0.35))
    # the olive branch and the owl on it, against the moon
    out.append(olive_branch(D, [(650, 420), (560, 426), (470, 438), (380, 440), (300, 452), (230, 478)], 10, 1.1))
    out.append(cast(D, 378, 440, 60, 9, "#000000", 0.45, 3))
    out.append(little_owl(D, 376, 352, 1.5, 11))
    out.append(olive_branch(D, [(470, 600), (500, 520), (540, 470), (600, 440)], 12, 0.9))
    # lettering below, on the dark of the city
    g = D.lin([(0, "#060A1E", 0), (0.4, "#060A1E", 0.7), (1, "#060A1E", 0.9)])
    out.append(f'<rect x="0" y="440" width="600" height="160" fill="{g}"/>')
    out.append(letters(D, 300, 512, "Athena’s Owl", SERIF_IT, 66, "#FFF2D0", ["#FFFFFF", "#FFE6A8", "#E8D0A0"], 12, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 540, "GREEK · WISDOM SEES IN THE DARK", CINZEL, 17, "#DCE4F8", ls=3, max_w=420))
    return fin(D, out, 17)


# ================================================================ 5. huginn and muninn — thought and memory on the rune stone
def raven_perched(D, x, y, s, seed, flip=False, head_tilt=0):
    """A raven standing in profile (facing right unless flip): heavy bill, shaggy throat, wedge tail. (x,y)=feet."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    body = L([(-56, -18), (-30, -40), (0, -52), (22, -60), (30, -66), (40, -60), (36, -44), (22, -28), (6, -12), (-14, -6), (-34, -6), (-70, 4), (-76, -2)])
    out.append(painted(D, body, RAVEN, seed, sdir=(0.5 if not flip else -0.5, 0.7), sk=0.2, angle=-10 if not flip else 190, n=30, inkw=1.4, inkc="#000000", hi=0.45, cols=["#5A6A9A", "#000000", "#2A2E4A", "#7A6AA0"]))
    wing = L([(-62, -10), (-30, -30), (6, -40), (18, -30), (0, -14), (-36, -6)])
    out.append(painted(D, wing, ("#4A5070", "#14161E", "#020204"), seed + 1, sdir=(0.4, 0.8), sk=0.15, angle=-10 if not flip else 190, n=16, inkw=1.0, inkc="#000000", hi=0.35))
    for k in range(5):
        a, b = L([(-60 + k * 8, -4 - k * 4), (-30 + k * 8, -20 - k * 4)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#6A7AAA" stroke-width="1.2" opacity="0.5"/>')
    hx, hy = 34, -62
    head = T([(-10, 2), (-6, -10), (4, -14), (14, -8), (16, 2), (8, 8), (-6, 8)], 0, 0, 1, False, head_tilt)
    head = [(hx + px, hy + py) for px, py in head]
    out.append(painted(D, L(head), RAVEN, seed + 2, sdir=(0.5, 0.6), sk=0.15, n=8, inkw=1.2, inkc="#000000", hi=0.5, cols=["#5A6A9A", "#000000", "#7A6AA0"]))
    bill = T([(12, -6), (32, -2), (40, 4), (28, 4), (12, 4)], 0, 0, 1, False, head_tilt)
    out.append(sharp(L([(hx + px, hy + py) for px, py in bill]), "#0A0A10"))
    out.append(pline(L([(hx + px, hy + py) for px, py in T([(14, -4), (34, -1)], 0, 0, 1, False, head_tilt)]), "#6A7090", 1.0, seed, 0.8, 1))
    ex, ey = L([(hx + px, hy + py) for px, py in T([(6, -6)], 0, 0, 1, False, head_tilt)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#1A1A22"/><circle cx="{ex + 0.6:.1f}" cy="{ey - 0.8:.1f}" r="{1.0 * s:.1f}" fill="#E8ECFF"/>')
    # shaggy throat hackles
    for k in range(5):
        a, = L([(26 + k * 2, -48 + k * 3)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} l {(-3 if flip else 3) * s:.1f} {6 * s:.1f}" stroke="#0A0A12" stroke-width="{2 * s:.1f}" stroke-linecap="round"/>')
    for sg in (-4, 6):
        a, b, c = L([(sg, -10), (sg + 2, 0), (sg + 8, 2)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f} L {c[0]:.1f} {c[1]:.1f}" stroke="#14141A" stroke-width="{2.6 * s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def raven_flying(D, x, y, s, seed, flip=False):
    """A raven landing: wings raised and spread, fingered primaries, wedge tail fanned."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    for k, sg in enumerate((-1, 1)):
        far = sg < 0
        wpts = [(-6, -6), (-10, -40), (-18, -70), (-30, -96), (-22, -98), (-14, -88), (-12, -100), (-2, -96), (0, -86), (4, -96), (12, -90), (10, -76), (18, -80), (22, -70), (16, -50), (12, -20), (6, -4)]
        if far:
            wpts = [(px * 0.8 + 14, py * 0.8 - 6) for px, py in wpts]
        out.append(painted(D, L(wpts), ("#4A5070", "#14161E", "#020204") if not far else ("#3A3E52", "#0E1016", "#020204"), seed + k, sdir=(0.4, 0.6), sk=0.15, angle=-80, n=16, inkw=1.0, inkc="#000000", hi=0.35))
        for j in range(5):
            a, b = L([(-4 + j * 4 + (14 if far else 0), -10), (-20 + j * 8 + (14 if far else 0), -80)])
            out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#6A7AAA" stroke-width="1" opacity="0.4"/>')
    body = L([(-46, 18), (-26, 2), (-4, -8), (18, -12), (30, -18), (40, -14), (36, -4), (20, 8), (0, 16), (-20, 20)])
    out.append(painted(D, body, RAVEN, seed + 3, sdir=(0.5, 0.7), sk=0.2, angle=-10, n=16, inkw=1.2, inkc="#000000", hi=0.4))
    out.append(poly(L([(-40, 16), (-70, 18), (-80, 30), (-70, 34), (-40, 24)]), "#0E1016"))
    out.append(sharp(L([(38, -18), (56, -14), (40, -8)]), "#0A0A10"))
    ex, ey = L([(32, -16)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.2 * s:.1f}" fill="#1A1A22"/><circle cx="{ex + 0.5:.1f}" cy="{ey - 0.6:.1f}" r="{0.9 * s:.1f}" fill="#E8ECFF"/>')
    for k in range(2):
        a, b = L([(-4 + k * 8, 14), (-2 + k * 8, 34)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#14141A" stroke-width="{2.4 * s:.1f}" stroke-linecap="round"/>')
    return "".join(out)


def rune(x, y, h, kind, col, w=2.2):
    """One Elder-Futhark-like rune (stave plus twigs) standing on baseline y, height h."""
    k = h / 3
    shapes = {
        0: f"M {x} {y} l 0 {-h} M {x} {y - h} l {k} {k} M {x} {y - h + k} l {k} {k}",            # fehu
        1: f"M {x} {y} l 0 {-h} l {k * 1.2} {k} l 0 {h - k}",                                      # uruz
        2: f"M {x} {y} l 0 {-h} M {x} {y - h + k * 0.6} l {k} {k * 0.7} l {-k} {k * 0.7}",        # thurisaz
        3: f"M {x} {y} l 0 {-h} M {x} {y - h + k * 0.4} l {k} {k * 0.8} M {x} {y - h + k * 1.4} l {k} {k * 0.8}",  # ansuz
        4: f"M {x} {y} l 0 {-h} M {x} {y - h} l {k} {k} l {-k} {k} l {k} {k}",                    # raido
        5: f"M {x - k * 0.6} {y} l 0 {-h} M {x + k * 0.6} {y} l 0 {-h} M {x - k * 0.6} {y - h * 0.6} l {k * 1.2} {-k * 0.6}",  # hagalaz
        6: f"M {x} {y} l 0 {-h} M {x - k * 0.8} {y - h + k * 0.8} l {k * 0.8} {-k * 0.8} l {k * 0.8} {k * 0.8}",  # tiwaz
        7: f"M {x} {y} l 0 {-h} M {x} {y - h * 0.5} l {k} {-k} M {x} {y - h * 0.5} l {k} {k}",   # kaunan-like
    }
    return f'<path d="{shapes[kind % 8]}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'


def rune_serpent(D, pts, w, seed, band="#C8503A", line="#2A1A10", runes="#2A1A10"):
    """Rune-stone serpent: a painted ribbon band carrying runes along its length, ending in a head."""
    path = catmull(pts, 10)
    out = [taper(path, w + 5, w + 5, line, 0.8)]
    out.append(taper(path, w, w, band))
    out.append(taper([(x - 1, y - 1) for x, y in path], w * 0.25, w * 0.25, lt(band, 0.4), 0.5))
    rnd = random.Random(seed)
    step = 3
    for i in range(4, len(path) - 4, step):
        (xa, ya), (xb, yb) = path[i - 1], path[i + 1]
        a = math.degrees(math.atan2(yb - ya, xb - xa))
        x, y = path[i]
        out.append(f'<g transform="rotate({a + 90:.1f} {x:.1f} {y:.1f})">{rune(x, y + w * 0.32, w * 0.64, rnd.randint(0, 7), runes, max(1.2, w * 0.12))}</g>')
    return "".join(out)


@design("huginn-and-muninn")
def huginn_and_muninn():
    D = Doc2("my-hm")
    out = [sky(D, [(0, "#2A3A5A"), (0.4, "#7A8AA8"), (0.62, "#F2C890"), (0.72, "#F6DCB0")], 1, 420, ["#5A6A8A", "#F2D0A0", "#9AA8C0"], 60)]
    out.append(soft_glow(D, 420, 330, 230, "#FFE2A0", 0.6))
    # fjord: steep mountain walls each side, the water between, mist
    for k, (pal, top, seed) in enumerate(((("#A8AEC8", "#868CAA", "#646A88"), 210, 3), (("#6A6A8A", "#4A4A6A", "#2A2A44"), 250, 4))):
        lpts = ridge([(-20, top - 30 + k * 30), (60, top - 60 + k * 50), (150, top + 20 + k * 30), (230, 360 + k * 10), (300, 412)], seed, 16)
        rpts = ridge([(330, 412), (400, 350 + k * 10), (470, top + k * 40), (540, top - 50 + k * 40), (620, top - 20 + k * 30)], seed + 5, 16)
        out.append(hill(D, lpts, 430, pal, seed, inkw=0, lit="#FFE0B0"))
        out.append(hill(D, rpts, 430, pal, seed + 1, inkw=0, lit="#FFE0B0"))
        if k == 0:
            for (px, py) in (lpts[4], rpts[-6]):
                out.append(f'<path d="{blob(px, py + 8, 24, 6, k, 0.2, 10)}" fill="#FFFFFF" opacity="0.55"/>')
    out.append(sea(D, 404, 470, [(0, "#F6DEB4"), (1, "#7A8AA8")], 4, ["#FFE8C0", "#5A6A8A"], 30))
    out.append(mist(D, 398, 46, 5, "#FFF2E0", 0.65))
    out.append(f'<path d="M 360 408 l 14 0 l -6 -10 Z" fill="#2A2A3A"/><path d="M 368 398 l 0 10" stroke="#2A2A3A" stroke-width="1.6"/>')
    # the hilltop and the standing stone
    gnd = [(-20, 470), (100, 440), (240, 446), (360, 470), (480, 478), (620, 470)]
    out.append(hill(D, gnd, 620, ("#9AA066", "#5A6A3A", "#2A3418"), 6, inkw=1.4))
    out.append(grass(7, (0, 450, 600, 600), ["#B8BA7A", "#4A5A2A", "#7A8A4A", "#D8C890"], 180, (8, 22), 1.6))
    sx, sb = 222, 520
    stone = [(sx - 70, sb), (sx - 76, sb - 120), (sx - 64, sb - 230), (sx - 36, sb - 270), (sx + 10, sb - 280), (sx + 52, sb - 256), (sx + 70, sb - 200), (sx + 76, sb - 100), (sx + 72, sb)]
    out.append(cast(D, sx + 60, sb, 110, 14, "#1A1A10", 0.5, 2))
    out.append(painted(D, stone, ("#D8D2C0", "#9A9484", "#4A463E"), 8, sdir=(-0.6, 0.3), sk=0.2, angle=-86, n=60, inkw=2, inkc="#2A2620", hi=0.45))
    out.append(specks(9, (sx - 70, sb - 260, sx + 70, sb), ["#6A7A4A", "#C8C060", "#FFFFFF"], 50, (1, 3), (0.3, 0.6)))
    # the rune-serpent looping round the face of the stone, head biting its tail at the foot
    band = [(sx - 20, sb - 16), (sx - 50, sb - 40), (sx - 58, sb - 130), (sx - 40, sb - 210), (sx, sb - 236), (sx + 40, sb - 212), (sx + 56, sb - 130), (sx + 46, sb - 44), (sx + 16, sb - 18)]
    out.append(rune_serpent(D, band, 20, 3))
    hx, hy = band[-1]
    out.append(poly([(hx + 8, hy - 12), (hx - 6, hy - 8), (hx - 16, hy + 2), (hx - 4, hy + 10), (hx + 12, hy + 6)], "#C8503A"))
    out.append(ink(smooth_closed([(hx + 8, hy - 12), (hx - 6, hy - 8), (hx - 16, hy + 2), (hx - 4, hy + 10), (hx + 12, hy + 6)]), "#2A1A10", 2, 3, 1, 0.8))
    out.append(f'<circle cx="{hx - 2}" cy="{hy - 1}" r="2.4" fill="#2A1A10"/>')
    # a ring-knot in the middle of the loop, painted blue
    kx, ky = sx, sb - 128
    for a0 in (0, 120, 240):
        a = math.radians(a0 - 90)
        out.append(f'<path d="{smooth_closed(ell_pts(kx + math.cos(a) * 16, ky + math.sin(a) * 16, 22, 22, 0, 360, 20))}" fill="none" stroke="#2A1A10" stroke-width="9" opacity="0.8"/>')
        out.append(f'<path d="{smooth_closed(ell_pts(kx + math.cos(a) * 16, ky + math.sin(a) * 16, 22, 22, 0, 360, 20))}" fill="none" stroke="#2A5A8A" stroke-width="5"/>')
    out.append(ink(smooth_open(stone[3:7]), "#FFE8C0", 2.4, 4, 1, 0.6))
    # the two ravens: Muninn perched on the stone, Huginn coming in to land
    out.append(raven_perched(D, sx - 6, sb - 270, 1.25, 12, flip=False, head_tilt=-8))
    out.append(raven_flying(D, 438, 286, 1.3, 13, flip=True))
    # lettering
    out.append(multi(300, 108, [("Huginn ", "#1A2034"), ("&", "#A8402A"), (" Muninn", "#1A2034")], DMS, 64, max_w=440, shadow="#FFF2D8", sdy=2.5))
    out.append(tx(300, 140, "NORSE · THOUGHT AND MEMORY", CINZEL, 17, "#1A2034", ls=4, max_w=380))
    out.append(tx(300, 536, "“Every day they fly over the wide world.”", SERIF_IT, 23, "#FFF6E0", max_w=440))
    return fin(D, out, 18)


# ================================================================ 6. the boat of ra — the sun's night voyage
def wedjat(cx, cy, s, col="#0A1A3A", fill="#FFFFFF", iris="#0A1A3A"):
    """The Eye of Horus: almond eye, brow, the falcon-cheek drop and the spiral tail."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = [taper(catmull(L([(-26, -18), (0, -24), (28, -18)]), 6), 5 * s, 4 * s, col)]
    eye = L([(-26, 0), (-10, -10), (10, -10), (28, -2), (10, 6), (-10, 6)])
    out.append(f'<path d="{smooth_closed(eye)}" fill="{fill}" stroke="{col}" stroke-width="{3 * s:.1f}"/>')
    ix, iy = L([(2, -2)])[0]
    out.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{6.4 * s:.1f}" fill="{iris}"/>')
    out.append(taper(L([(28, -2), (40, -2)]), 4 * s, 3 * s, col))
    out.append(taper(catmull(L([(-4, 6), (-6, 18), (-8, 28)]), 6), 4 * s, 3 * s, col))
    out.append(taper(catmull(L([(6, 6), (14, 18), (26, 24), (34, 18), (30, 10), (24, 14)]), 6), 4 * s, 3 * s, col))
    return "".join(out)


def star5(cx, cy, r, col, op=1.0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = math.radians(-90 + i * 36)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return f'<path d="{pd(pts)}" fill="{col}" opacity="{op}"/>'


def papyrus_boat(D, cx, wl, s, seed):
    """Papyriform solar barque: long hull rising to papyrus-umbel prow and stern, a shrine with the sun disc."""
    def L(pts):
        return T(pts, cx, wl, s)
    out = []
    hull = L([(-170, -70), (-160, -40), (-130, -12), (-60, 6), (60, 6), (130, -12), (160, -40), (170, -70), (176, -60), (168, -20), (140, 6), (70, 20), (-70, 20), (-140, 6), (-168, -20), (-176, -60)])
    out.append(painted(D, hull, ("#F6D27A", "#C8902A", "#5A3A0A"), seed, sdir=(0.3, 0.8), sk=0.2, angle=0, n=40, inkw=1.8, inkc="#2A1804", hi=0.45))
    for k in range(9):
        a, b = L([(-140 + k * 34, -4 + abs(k - 4) * -1), (-136 + k * 34, 18)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#7A5010" stroke-width="2" opacity="0.6"/>')
    # lashing bands and a turquoise stripe
    out.append(taper(L([(-150, -10), (-60, 8), (60, 8), (150, -10)]), 5 * s, 5 * s, "#1E8A8A"))
    out.append(taper(L([(-150, -6), (-60, 12), (60, 12), (150, -6)]), 2 * s, 2 * s, "#C8402A"))
    # papyrus umbels at both ends
    for sg in (-1, 1):
        ux, uy = L([(sg * 172, -70)])[0]
        fan = [(ux, uy)]
        for k in range(7):
            a = math.radians(-90 + sg * (-40 + k * 18))
            fan.append((ux + math.cos(a) * 26 * s, uy + math.sin(a) * 26 * s))
        out.append(painted(D, fan, ("#B8E0A0", "#4A9A5A", "#1E4A2A"), seed + sg, sk=0.15, n=8, inkw=1.4, inkc="#1A2A10", hi=0.4))
        for k in range(7):
            a = math.radians(-90 + sg * (-40 + k * 18))
            out.append(f'<path d="M {ux:.1f} {uy:.1f} L {ux + math.cos(a) * 24 * s:.1f} {uy + math.sin(a) * 24 * s:.1f}" stroke="#1A3A1A" stroke-width="1.2" opacity="0.7"/>')
    # the Eye of Horus painted on the bow
    ex, ey = L([(118, -12)])[0]
    out.append(wedjat(ex, ey, 0.42 * s, "#0A1A3A"))
    # the kiosk: two papyrus columns and a corniced roof, the sun disc ringed by the serpent Mehen
    for sg in (-1, 1):
        col_ = L([(sg * 46 - 5, 0), (sg * 46 - 4, -92), (sg * 46 + 4, -92), (sg * 46 + 5, 0)])
        out.append(painted(D, col_, ("#F6E6C0", "#D8C08A", "#7A6A40"), seed + 10 + sg, sk=0.2, angle=-90, n=6, inkw=1.2, inkc="#2A1804", hi=0.4))
        cap = L([(sg * 46 - 12, -96), (sg * 46 + 12, -96), (sg * 46 + 4, -88), (sg * 46 - 4, -88)])
        out.append(painted(D, cap, ("#B8E0A0", "#4A9A5A", "#1E4A2A"), seed + 12 + sg, sk=0.1, n=4, inkw=1.2, inkc="#1A2A10", hi=0.3))
    roof = L([(-62, -96), (62, -96), (66, -108), (-66, -108)])
    out.append(painted(D, roof, ("#6AC8D0", "#1E7A8A", "#0A3A44"), seed + 5, sk=0.1, n=6, inkw=1.4, inkc="#0A1A1A", hi=0.3))
    for k in range(12):
        a, = L([(-58 + k * 10.5, -102)])
        out.append(f'<rect x="{a[0] - 2:.1f}" y="{a[1] - 4:.1f}" width="{4 * s:.1f}" height="{8 * s:.1f}" fill="{("#F2C84A", "#C8402A")[k % 2]}"/>')
    sx, sy = L([(0, -48)])[0]
    out.append(soft_glow(D, sx, sy, 190 * s, "#FFB040", 0.9))
    out.append(ray_fan(sx, sy, 36 * s, 120 * s, 28, "#FFE08A", 0.25, seed=seed))
    out.append(painted(D, blob_pts(sx, sy, 32 * s, 32 * s, seed, 0.004, 28), ("#FFF2A8", "#F2861E", "#A8340A"), seed + 6, sdir=(0.4, 0.5), sk=0.12, n=18, inkw=1.4, inkc="#6A1A04", hi=0.5))
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{39 * s:.1f}" fill="none" stroke="#1A3A1A" stroke-width="{7 * s:.1f}"/>')
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{39 * s:.1f}" fill="none" stroke="#C8B04A" stroke-width="{4.4 * s:.1f}"/>')
    for k in range(24):
        a = 2 * math.pi * k / 24
        out.append(f'<path d="M {sx + math.cos(a) * 37 * s:.1f} {sy + math.sin(a) * 37 * s:.1f} L {sx + math.cos(a) * 41 * s:.1f} {sy + math.sin(a) * 41 * s:.1f}" stroke="#4A6A1A" stroke-width="1.2"/>')
    hx_, hy_ = sx + 2 * s, sy - 40 * s
    out.append(poly([(hx_ - 4 * s, hy_ + 2 * s), (hx_ + 2 * s, hy_ - 12 * s), (hx_ + 10 * s, hy_ - 6 * s), (hx_ + 6 * s, hy_ + 3 * s)], "#2A8A4A"))
    # steering oar at the stern
    out.append(taper(L([(-130, -40), (-150, 10), (-160, 40)]), 4 * s, 3 * s, "#5A3A14"))
    out.append(poly(L([(-160, 26), (-156, 58), (-166, 60), (-168, 30)]), "#5A3A14"))
    return "".join(out)


def egypt_figure(x, base, s, col, flip=False, head="set", spear=True, rim=None):
    """A striding figure in the Egyptian manner (profile head and legs, broad shoulders), kilt; head 'set' (the
    Set animal: long curved snout, tall square-tipped ears) or 'man'. With a spear thrust down and forward."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = []
    out.append(taper(L([(-4, -46), (-12, -22), (-18, 0)]), 7 * s, 5 * s, col))
    out.append(taper(L([(4, -46), (12, -22), (20, 0)]), 7 * s, 5 * s, col))
    out.append(poly(L([(-24, 0), (-12, 0), (-14, -4)]), col))
    out.append(poly(L([(14, 0), (28, 0), (16, -4)]), col))
    out.append(sharp(L([(-12, -54), (12, -54), (18, -32), (-14, -32)]), col))
    out.append(poly(L([(-9, -54), (-17, -80), (-14, -86), (14, -86), (17, -80), (9, -54)]), col))
    out.append(poly(L([(-4, -84), (-4, -94), (4, -94), (4, -84)]), col))
    if head == "set":
        out.append(poly(L([(-8, -92), (-8, -104), (2, -108), (14, -104), (26, -96), (24, -92), (8, -94), (4, -90)]), col))
        for dx in (-6, 0):
            out.append(sharp(L([(dx, -104), (dx - 2, -124), (dx + 5, -124), (dx + 4, -104)]), col))
    else:
        out.append(f'<path d="{blob(*L([(2, -100)])[0], 7 * s, 8 * s, 3, 0.06, 10)}" fill="{col}"/>')
    if spear:
        out.append(taper(L([(12, -82), (24, -70), (34, -60)]), 6 * s, 5 * s, col))
        out.append(taper(L([(-12, -82), (6, -74), (24, -64)]), 6 * s, 5 * s, col))
        a, b = L([(-24, -98), (78, -16)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{3.4 * s:.1f}" stroke-linecap="round"/>')
        out.append(sharp(L([(70, -26), (88, -10), (76, -18)]), col))
    if rim:
        out.append(ink(smooth_open(L([(2, -108), (14, -104), (26, -96)])), rim, 1.4, 2, 1, 0.8))
        out.append(ink(smooth_open(L([(14, -86), (17, -80), (9, -54), (18, -32)])), rim, 1.4, 3, 1, 0.8))
    return "".join(out)


@design("the-boat-of-ra")
def the_boat_of_ra():
    D = Doc2("my-ra")
    # tomb-ceiling sky: lapis blue strewn with yellow stars
    out = [sky(D, [(0, "#0A1A4A"), (0.6, "#1A2E6A"), (1, "#2A2A5A")], 1, 600, ["#1E3A8A", "#0A1240", "#3A4A9A"], 70)]
    rnd = random.Random(3)
    for r_ in range(7):
        for c_ in range(10):
            x = 30 + c_ * 60 + (r_ % 2) * 30 + rnd.uniform(-3, 3)
            y = 128 + r_ * 40 + rnd.uniform(-3, 3)
            if y < 380:
                out.append(star5(x, y, 7, "#F2C84A", 0.7))
    # upper frieze band: lotus and bud, in the Egyptian manner (decorative, bleeds off the top)
    out.append(painted(D, rect_pts(-10, -10, 610, 96, 40, 1, 0.3), ("#F6E6C0", "#E8D2A0", "#A08A60"), 4, sdir=(0, 1), sk=0.05, angle=0, n=60, inkw=0, hi=0))
    for y, c in ((86, "#1E3A8A"), (92, "#C8402A"), (98, "#1E8A8A")):
        out.append(f'<rect x="0" y="{y}" width="600" height="6" fill="{c}"/>')
    for k in range(-1, 14):
        x = k * 48 + 20
        out.append(f'<path d="M {x} 84 C {x - 18} 64 {x - 16} 42 {x - 12} 38 L {x} 58 L {x + 12} 38 C {x + 16} 42 {x + 18} 64 {x} 84 Z" fill="#1E7A8A"/>')
        out.append(f'<path d="M {x} 58 L {x - 6} 38 L {x} 30 L {x + 6} 38 Z" fill="#C8402A"/>')
        out.append(f'<path d="M {x + 24} 84 L {x + 24} 62" stroke="#1E7A8A" stroke-width="2"/><path d="{blob(x + 24, 56, 5, 8, k, 0.05, 10)}" fill="#1E3A8A"/>')
    # the river of the night
    wl = 392
    out.append(sea(D, wl, 620, [(0, "#1A2A6A"), (0.4, "#0E1640"), (1, "#060A20")], 5, ["#3A4A9A", "#060A20", "#F2B040"], 80))
    out.append(soft_glow(D, 300, wl + 6, 170, "#FFB040", 0.35))
    for k in range(34):
        y = wl + 8 + (k / 34) ** 1.4 * 70
        w = 30 + (y - wl) * 0.8
        x = 300 + rnd.uniform(-w, w) * 0.5
        out.append(taper([(x - w * 0.2, y), (x, y - 1.5), (x + w * 0.2, y)], 0.8, rnd.uniform(1.5, 3.5), "#FFD070", rnd.uniform(0.4, 0.85)))
    # Apophis, the serpent of chaos, coiling through the dark water and rising at the prow
    ap = ("#6A6A8A", "#2A2A44", "#0A0A16")
    for (x0_, x1_) in ((40, 130), (150, 240), (380, 470)):
        out.append(painted(D, [(x0_, wl + 64), (x0_ + 10, wl + 40), ((x0_ + x1_) / 2, wl + 30), (x1_ - 10, wl + 40), (x1_, wl + 64), ((x0_ + x1_) / 2, wl + 56)], ap, x0_, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.4, inkc="#000000", hi=0.4))
        for j_ in range(5):
            xx = x0_ + 14 + j_ * (x1_ - x0_ - 28) / 4
            out.append(f'<path d="M {xx - 5:.1f} {wl + 44:.1f} q 5 -4 10 0" stroke="#9A9AC0" stroke-width="1.2" fill="none" opacity="0.6"/>')
        out.append(f'<path d="{blob((x0_ + x1_) / 2, wl + 62, (x1_ - x0_) * 0.6, 5, x0_, 0.2, 12)}" fill="#8AA0E0" opacity="0.3"/>')
    out.append(snake(D, [(470, wl + 60), (512, wl + 34), (540, wl - 6), (536, wl - 34), (512, wl - 44)], 26, 18, ap, 8, eye="#FF4A2A", tongue="#FF4A2A"))
    out.append(papyrus_boat(D, 286, wl + 4, 1.0, 9))
    # Set at the prow, spearing the serpent
    out.append(egypt_figure(420, wl - 16, 0.86, "#0A0A18", head="set", rim="#FFC870"))
    out.append(wave_lines(10, (0, wl + 20, 600, 600), ["#6A7AC8", "#F2C870", "#0A1240"], 50, (10, 30), 1.6, 2, (0.3, 0.6)))
    # lettering on the night water
    out.append(gilt(D, 300, 512, "THE BOAT OF RA", CINZEL, 50, ls=8, max_w=440, seed=4, deboss="#000000", dop=0.85))
    out.append(tx(300, 540, "EGYPTIAN · THE SUN SAILS THROUGH THE NIGHT", CINZEL, 16, "#F6E2B0", ls=2.5, max_w=440))
    return fin(D, out, 19)


# ================================================================ horses and sea-horses
HORSE_BODY = [(-150, -10), (-146, 0), (-130, 4), (-112, -4), (-96, 12), (-80, 40), (-62, 58), (-20, 62), (30, 60), (60, 52), (80, 40),
              (98, 14), (94, -12), (62, -24), (10, -18), (-30, -26), (-62, -46), (-92, -58), (-108, -60), (-114, -76), (-104, -64),
              (-124, -48), (-148, -24)]


def leg(D, root, knee, fet, hoof_dir, s, col, rim=None, hoof="#1A1410", w=(17, 9)):
    """One horse leg: tapered upper + cannon, a fetlock bend, a hoof."""
    pts = catmull([root, knee, fet], 6)
    out = [taper(pts, w[0] * s, w[1] * s, col)]
    hx, hy = fet[0] + hoof_dir[0], fet[1] + hoof_dir[1]
    out.append(taper([fet, ((fet[0] + hx) / 2, (fet[1] + hy) / 2), (hx, hy)], w[1] * s, w[1] * 1.1 * s, col))
    a = math.degrees(math.atan2(hoof_dir[1], hoof_dir[0]))
    out.append(f'<path d="{blob(hx, hy, 6 * s, 4.4 * s, int(hx * 3), 0.1, 10, a)}" fill="{hoof}"/>')
    if rim:
        out.append(taper([(x - 1.5 * s, y - 1 * s) for x, y in pts], 1.6, 1.2, rim, 0.6))
    return "".join(out)


def horse(D, x, y, s, seed, pal, legs, flip=False, mane="#F2F2F6", tail=True, rim=None, dapple=True, head_only=False):
    """A galloping horse in side view facing left (unless flip). legs: list of local (root, knee, fetlock, hoof_dir).
    (x, y) = the horse's local origin (mid back). Returns svg."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    far = [lg_ for lg_ in legs if lg_[4] == "far"]
    near = [lg_ for lg_ in legs if lg_[4] != "far"]
    for root, knee, fet, hd, _ in far:
        r_, k_, f_ = L([root, knee, fet])
        hd_ = (hd[0] * s * (-1 if flip else 1), hd[1] * s)
        out.append(leg(D, r_, k_, f_, hd_, s, dk(pal[1], 0.3)))
    if tail:
        for k in range(6):
            t = catmull(L([(92, -8), (130, -2 + k * 4), (160, 18 + k * 6), (176, 40 + k * 8)]), 6)
            out.append(taper(t, 10 * s, 1.5 * s, mane if k % 2 else dk(mane, 0.15), 0.9))
    body = L(HORSE_BODY)
    out.append(painted(D, body, pal, seed, sdir=(0.3 if not flip else -0.3, 0.8), sk=0.18, angle=-10 if not flip else 190, n=50, inkw=1.6 * s, inkc="#1A1A24", hi=0.45))
    if dapple:
        cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
        rnd = random.Random(seed)
        dd = []
        for k in range(26):
            px, py = L([(rnd.uniform(-60, 90), rnd.uniform(-16, 50))])[0]
            dd.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(3, 7) * s:.1f}" fill="none" stroke="{pal[0]}" stroke-width="{1.4 * s:.1f}" opacity="0.45"/>')
        out.append(f'<g {cid}>{"".join(dd)}</g>')
    # muscle lines
    for p in ([(-60, 52), (-50, 30), (-56, 10)], [(62, 48), (66, 24), (52, 4)], [(-96, -6), (-80, -22), (-62, -30)]):
        out.append(pline(L(p), pal[2], 1.4 * s, seed, 0.5, 1))
    # mane
    for k in range(9):
        t = k / 8
        px, py = L([(-108 + t * 76, -60 + t * 34)])[0]
        ex, ey = L([(-96 + t * 76 + 22, -70 + t * 34 + 4)])[0]
        out.append(taper([(px, py), ((px + ex) / 2, (py + ey) / 2 - 4 * s), (ex, ey)], 7 * s, 1.5 * s, mane if k % 2 else dk(mane, 0.12)))
    # eye, nostril, mouth line
    ex, ey = L([(-122, -34)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.8 * s:.1f}" fill="#141418"/><circle cx="{ex - 0.6:.1f}" cy="{ey - 0.8:.1f}" r="{1 * s:.1f}" fill="#FFFFFF"/>')
    nx, ny = L([(-144, -8)])[0]
    out.append(f'<path d="{blob(nx, ny, 2.6 * s, 1.8 * s, 2, 0.1, 8)}" fill="{pal[2]}"/>')
    for root, knee, fet, hd, _ in near:
        r_, k_, f_ = L([root, knee, fet])
        hd_ = (hd[0] * s * (-1 if flip else 1), hd[1] * s)
        out.append(leg(D, r_, k_, f_, hd_, s, pal[1], rim=pal[0]))
    if rim:
        out.append(ink(smooth_open(L([(-148, -24), (-124, -48), (-104, -64), (-92, -58), (-62, -46), (-30, -26), (10, -18), (62, -24), (94, -12)])), rim, 2.2 * s, seed, 1, 0.75))
    return "".join(out)


def hippocamp(D, x, y, s, seed, pal, fin=("#FBE7A4", "#D9A945", "#8A6020"), flip=False, rim=None):
    """Sea-horse of Poseidon rearing (facing left unless flip): a horse's head and arched neck with a finned mane,
    forelegs pawing with webbed hooves, and a long coiling fish tail. (x, y) = chest."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    # the tail coils down and back under the body, scales and a fan fin at its end
    spine = catmull(L([(20, 10), (54, 50), (66, 104), (40, 140), (0, 138), (-12, 112)]), 8)
    widths = [44 * s * (1 - i / len(spine)) ** 0.8 + 4 * s for i in range(len(spine))]
    left, right = [], []
    for i, (px, py) in enumerate(spine):
        a = spine[max(0, i - 1)]
        b = spine[min(len(spine) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ln, dx / Ln
        left.append((px + nx * widths[i] / 2, py + ny * widths[i] / 2))
        right.append((px - nx * widths[i] / 2, py - ny * widths[i] / 2))
    tail = left + right[::-1]
    out.append(painted(D, tail, pal, seed + 1, sdir=(0.4, 0.8), sk=0.2, angle=20, n=40, inkw=1.6, inkc="#06242A", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(tail)}"/>')
    sc = []
    for i in range(2, len(spine) - 2, 2):
        px, py = spine[i]
        w = widths[i] * 0.4
        for j in (-1, 0, 1):
            sc.append(f'<path d="M {px + j * w * 0.7 - w * 0.3:.1f} {py + j * w * 0.3:.1f} q {w * 0.3:.1f} {w * 0.4:.1f} {w * 0.6:.1f} 0" stroke="{pal[2]}" stroke-width="1.2" fill="none" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    ex, ey = spine[-1]
    fan = [(ex, ey)]
    for k in range(7):
        a = math.radians(-150 + k * 22) if not flip else math.radians(-30 - k * 22)
        fan.append((ex + math.cos(a) * 40 * s, ey + math.sin(a) * 40 * s))
    out.append(painted(D, fan, fin, seed + 2, sk=0.15, n=10, inkw=1.4, inkc="#5A3A08", hi=0.4))
    for k in range(7):
        a = math.radians(-150 + k * 22) if not flip else math.radians(-30 - k * 22)
        out.append(f'<path d="M {ex:.1f} {ey:.1f} L {ex + math.cos(a) * 36 * s:.1f} {ey + math.sin(a) * 36 * s:.1f}" stroke="#8A6020" stroke-width="1.2" opacity="0.7"/>')
    # far foreleg
    r_, k_, f_ = L([(-14, 4), (-44, 22), (-50, 50)])
    out.append(taper(catmull([r_, k_, f_], 6), 15 * s, 8 * s, dk(pal[1], 0.25)))
    # forequarters: rearing body, arched neck, long head lifted
    fq = L([(-92, -92), (-90, -82), (-80, -77), (-66, -76), (-56, -80), (-48, -58), (-40, -24), (-26, 8), (0, 24), (24, 22), (36, -4), (22, -42),
            (-6, -80), (-34, -108), (-38, -128), (-30, -112), (-54, -108), (-84, -100)])
    out.append(painted(D, fq, pal, seed, sdir=(0.3, 0.8), sk=0.18, angle=-60, n=40, inkw=1.6, inkc="#06242A", hi=0.5))
    out.append(pline(L([(-60, -84), (-66, -92), (-62, -100)]), pal[2], 1.4, seed, 0.6, 1))
    out.append(pline(L([(-36, -30), (-30, -10), (-16, 2)]), pal[2], 1.4, seed + 1, 0.5, 1))
    # finned mane along the crest
    mane = L([(-36, -110), (-30, -130), (-12, -118), (-6, -106), (10, -104), (12, -86), (28, -80), (30, -60), (40, -52), (22, -42), (-6, -80)])
    out.append(painted(D, mane, fin, seed + 10, sk=0.15, n=10, inkw=1.2, inkc="#5A3A08", hi=0.5))
    for k in range(6):
        a_, b_ = L([(-30 + k * 9, -100 + k * 10), (-22 + k * 10, -118 + k * 12)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#8A6020" stroke-width="1.2" opacity="0.7"/>')
    # near foreleg pawing high, webbed fin at the hoof
    r_, k_, f_ = L([(-30, -4), (-66, -16), (-74, 12)])
    out.append(taper(catmull([r_, k_, f_], 6), 16 * s, 8 * s, pal[1]))
    out.append(taper(catmull([(px - 1, py - 1) for px, py in (r_, k_, f_)], 6), 3 * s, 1.5 * s, pal[0], 0.6))
    for (fx, fy), k in ((f_, 0), (L([(-50, 50)])[0], 1)):
        web = [(fx, fy)] + [(fx + math.cos(math.radians(a_)) * 16 * s * (-1 if flip else 1), fy + math.sin(math.radians(a_)) * 16 * s) for a_ in (50, 90, 130, 170)]
        out.append(painted(D, web, fin, seed + 5 + k, sk=0.1, n=4, inkw=1.0, inkc="#5A3A08", hi=0.4))
    ex, ey = L([(-58, -98)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3 * s:.1f}" fill="#06242A"/><circle cx="{ex - 0.6:.1f}" cy="{ey - 0.8:.1f}" r="{1.1 * s:.1f}" fill="#FFFFFF"/>')
    nx, ny = L([(-86, -90)])[0]
    out.append(f'<path d="{blob(nx, ny, 2.6 * s, 1.8 * s, 2, 0.1, 8)}" fill="{pal[2]}"/>')
    if rim:
        out.append(ink(smooth_open(L([(-84, -100), (-54, -108), (-38, -128), (-30, -112)])), rim, 2.0, seed, 1, 0.8))
    return "".join(out)


def flame(D, x, y, h, seed, pal=("#FFF6B0", "#FFB030", "#E8501A"), lean=0.0):
    """A painted flame tongue cluster rising from (x, y), about h tall."""
    rnd = random.Random(seed)
    out = [soft_glow(D, x, y - h * 0.4, h * 1.6, "#FFB040", 0.6)]
    for k, (c, sc) in enumerate(((pal[2], 1.0), (pal[1], 0.75), (pal[0], 0.45))):
        pts = [(x - h * 0.28 * sc, y)]
        for j in range(5):
            t = (j + 1) / 6
            pts.append((x - h * 0.3 * sc * (1 - t) + rnd.uniform(-3, 3) + lean * h * t, y - h * sc * t * rnd.uniform(0.8, 1.05)))
        pts.append((x + lean * h + rnd.uniform(-4, 4), y - h * sc * 1.1))
        for j in range(5, 0, -1):
            t = j / 6
            pts.append((x + h * 0.3 * sc * (1 - t) + rnd.uniform(-3, 3) + lean * h * t, y - h * sc * t * rnd.uniform(0.75, 1.0)))
        pts.append((x + h * 0.28 * sc, y))
        out.append(poly(pts, c))
    return "".join(out)


# ================================================================ 7. prometheus — the fire in the fennel stalk
@design("prometheus")
def prometheus():
    D = Doc2("my-pr")
    out = [sky(D, [(0, "#0E0E22"), (0.45, "#2A2244"), (0.8, "#5A3A54"), (1, "#7A4A50")], 1, 600, ["#3A2E54", "#0A0A1A", "#6A4A6A"], 70)]
    # storm clouds rolling over the peaks; a far bolt of Zeus
    for (cx_, cy_, w_, sd) in ((110, 140, 260, 3), (470, 120, 300, 4), (300, 210, 240, 5)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#6A5A7A", "#3A2E4A", "#16101E"), op=0.95))
    bolt = [(520, 150), (508, 196), (522, 200), (500, 262), (514, 266), (488, 330)]
    out.append(soft_glow(D, 508, 230, 70, "#C8D8FF", 0.45))
    out.append(pline(bolt, "#F2F6FF", 3, 2, 1, 1))
    out.append(pline(bolt, "#9AB0FF", 7, 2, 0.3, 1))
    # far valley of mortals: dark hills with the first small fires being lit
    far = ridge([(-20, 440), (120, 420), (260, 446), (400, 430), (620, 450)], 6, 12)
    out.append(hill(D, far, 620, ("#3A3050", "#201A30", "#0A0814"), 6, inkw=0))
    rnd = random.Random(9)
    for k in range(9):
        fx, fy = rnd.uniform(40, 250), rnd.uniform(462, 500)
        out.append(soft_glow(D, fx, fy, 18, "#FF9A3A", 0.7))
        out.append(f'<path d="M {fx - 2:.1f} {fy:.1f} q 2 -7 4 0 Z" fill="#FFD070"/>')
        out.append(f'<rect x="{fx - 10:.1f}" y="{fy - 4:.1f}" width="7" height="6" fill="#120E1A"/><path d="M {fx - 11:.1f} {fy - 4:.1f} l 4.5 -5 l 4.5 5 Z" fill="#120E1A"/>')
    out.append(mist(D, 450, 40, 7, "#8A6A8A", 0.4))
    # the mountain ridge he is coming down, lit from his torch
    rk = [(190, 620), (240, 560), (310, 528), (390, 506), (450, 490), (510, 470), (560, 440), (620, 420), (640, 620)]
    out.append(painted(D, rk, ("#8A6A6A", "#4A3444", "#160E18"), 10, sdir=(0.6, 0.4), sk=0.18, angle=-60, n=80, inkw=1.6, inkc="#0A060C", hi=0.0))
    out.append(soft_glow(D, 360, 300, 260, "#FF9A3A", 0.42))
    out.append(ink(smooth_open(rk[1:8]), "#FFB060", 3, 4, 1, 0.65))
    for k in range(10):
        x0_ = rnd.uniform(260, 600)
        out.append(pline([(x0_, 540 + (x0_ - 260) * -0.2 + rnd.uniform(10, 40)), (x0_ + rnd.uniform(10, 30), 560 + (x0_ - 260) * -0.2 + rnd.uniform(20, 50))], "#0E080E", 1.6, k, 0.5, 1))
    # Prometheus, striding down, the stolen fire held high in a hollow fennel stalk
    fx, fy = 452, 494
    # his cloak streaming back in the storm wind
    out.append(painted(D, [(fx - 10, fy - 150), (fx + 30, fy - 150), (fx + 90, fy - 120), (fx + 150, fy - 70), (fx + 120, fy - 60), (fx + 140, fy - 30), (fx + 40, fy - 60), (fx, fy - 100)],
                       ("#6A2A2A", "#3A1414", "#120606"), 4, sdir=(0.4, 0.6), sk=0.2, angle=10, n=16, inkw=0, hi=0.3))
    out.append(hero_figure(fx, fy, 1.55, "#140C10", facing=-1, rim="#FFB060", arm="up", drape="#2A1416", lean=-4))
    hx, hy = T([(44, -132)], fx, fy, 1.55, True, -4)[0]
    stalk_top = (hx - 50, hy - 62)
    out.append(taper([(hx + 10, hy + 18), (hx - 12, hy - 26), stalk_top], 6, 4, "#6A7A3A"))
    for k in range(3):
        a, = T([(0, -20 - k * 22)], hx + 6, hy + 10, 1, False, 0)
        out.append(f'<path d="M {hx + 8 - k * 10:.1f} {hy + 6 - k * 22:.1f} l 6 -2" stroke="#3A4A1A" stroke-width="2"/>')
    out.append(flame(D, stalk_top[0], stalk_top[1] + 8, 66, 3, lean=-0.2))
    for k in range(16):
        out.append(sparkle(stalk_top[0] + rnd.uniform(-40, 70), stalk_top[1] + rnd.uniform(-80, 40), rnd.uniform(1.5, 4), rnd.choice(["#FFE070", "#FFB040", "#FFFFFF"]), rnd.uniform(0.6, 1)))
    # Zeus' eagle circling above
    for (ex_, ey_, es) in ((150, 236, 1.0),):
        out.append(poly([(ex_ - 40 * es, ey_ - 4), (ex_ - 20 * es, ey_ - 14), (ex_ - 6, ey_ - 6), (ex_, ey_ - 10), (ex_ + 6, ey_ - 6), (ex_ + 20 * es, ey_ - 14), (ex_ + 42 * es, ey_ - 2),
                         (ex_ + 24 * es, ey_ - 4), (ex_ + 10, ey_ + 2), (ex_ + 4, ey_ + 12), (ex_ - 4, ey_ + 12), (ex_ - 10, ey_ + 2), (ex_ - 24 * es, ey_ - 4)], "#0A0810"))
    # lettering
    out.append(gilt(D, 300, 106, "PROMETHEUS", CINZEL, 54, ls=10, max_w=440, seed=11, deboss="#000000", dop=0.8))
    out.append(tx(300, 136, "GREEK · HE STOLE FIRE FOR US", CINZEL, 17, "#F2D8C8", ls=3, max_w=420))
    out.append(letters(D, 300, 538, "Every hearth began with him.", SERIF_IT, 32, "#FFE8C8", ["#FFFFFF", "#FFD8A0"], 12, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.4))
    return fin(D, out, 20)


# ================================================================ 8. the golden fleece — on the oak in the grove of Ares
def fleece(D, cx, top, s, seed):
    """The golden ram's fleece hung by its forelegs: curly gold wool, dangling legs, the ram's head with spiral horns."""
    def L(pts):
        return T(pts, cx, top, s)
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, top + 60 * s, 170 * s, "#FFD860", 0.75)]
    pelt = L([(-40, 0), (-58, -6), (-62, 6), (-46, 20), (-40, 60), (-46, 100), (-60, 128), (-50, 136), (-30, 120), (0, 128), (30, 120), (50, 136),
              (60, 128), (46, 100), (40, 60), (46, 20), (62, 6), (58, -6), (40, 0), (20, 6), (-20, 6)])
    out.append(painted(D, pelt, ("#FFF0A0", "#E8B030", "#8A5A10"), seed, sdir=(0.5, 0.6), sk=0.2, angle=-90, n=30, inkw=1.8, inkc="#5A3A08", hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(pelt)}"/>')
    curls = []
    for k in range(110):
        px, py = L([(rnd.uniform(-56, 56), rnd.uniform(-2, 130))])[0]
        r = rnd.uniform(3, 6) * s
        c = rnd.choice(["#FFF6C8", "#C88A1E", "#FFE070", "#A86A10"])
        curls.append(f'<path d="M {px:.1f} {py:.1f} m {-r:.1f} 0 a {r:.1f} {r:.1f} 0 1 1 {r * 1.4:.1f} {r * 0.8:.1f}" stroke="{c}" stroke-width="{1.4 * s:.1f}" fill="none" opacity="0.8"/>')
    out.append(f'<g {cid}>{"".join(curls)}</g>')
    # hind legs dangling with small hooves
    for sg in (-1, 1):
        p = L([(sg * 52, 130), (sg * 56, 150), (sg * 54, 170)])
        out.append(taper(p, 8 * s, 5 * s, "#C88A20"))
        out.append(f'<path d="{blob(p[-1][0], p[-1][1] + 3 * s, 4.6 * s, 3.4 * s, seed + sg, 0.1, 8)}" fill="#3A2A10"/>')
    # the ram's head at the top, between the forelegs tied to the branch
    hx, hy = L([(0, 6)])[0]
    head = L([(-14, 0), (-12, 18), (-6, 34), (0, 38), (6, 34), (12, 18), (14, 0), (0, -6)])
    out.append(painted(D, head, ("#FFF0A0", "#E0A830", "#8A5A10"), seed + 4, sk=0.2, n=8, inkw=1.4, inkc="#5A3A08", hi=0.5))
    for sg in (-1, 1):
        sp = []
        for i in range(22):
            t = i / 21
            a = math.radians(-90 + sg * 30 + sg * t * 560)
            r = (16 - 12 * t) * s
            ox, oy = hx + sg * 18 * s, hy + 8 * s
            sp.append((ox + math.cos(a) * r * (1 if sg > 0 else -1) * -1 if False else ox + math.cos(a) * r, oy + math.sin(a) * r))
        out.append(taper(sp, 7 * s, 2.4 * s, "#B8862A"))
        out.append(taper([(x_ - 0.6, y_ - 0.6) for x_, y_ in sp], 2.4 * s, 1 * s, "#FFF0B0", 0.7))
        ex, ey = L([(sg * 7, 12)])[0]
        out.append(f'<path d="M {ex - 2.4 * s:.1f} {ey:.1f} q {2.4 * s:.1f} {1.6 * s:.1f} {4.8 * s:.1f} 0" stroke="#5A3A08" stroke-width="{1.4 * s:.1f}" fill="none"/>')
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        out.append(sparkle(cx + math.cos(a) * rnd.uniform(60, 110) * s, top + 60 * s + math.sin(a) * rnd.uniform(60, 110) * s, rnd.uniform(2, 5), "#FFF6C0", rnd.uniform(0.6, 1)))
    return "".join(out)


def argo(x, wl, s, col="#0E1422", sail="#E8D8B8"):
    def L(pts):
        return T(pts, x, wl, s)
    out = [poly(L([(-70, -6), (60, -6), (80, -20), (88, -34), (82, -14), (64, 6), (-60, 6), (-78, -4), (-90, -14)]), col)]
    out.append(taper(L([(0, -6), (0, -84)]), 3 * s, 2 * s, col))
    out.append(sharp(L([(-30, -78), (30, -78), (34, -24), (-34, -24)]), sail))
    out.append(f'<path d="M {L([(-30, -60)])[0][0]:.1f} {L([(-30, -60)])[0][1]:.1f} L {L([(30, -60)])[0][0]:.1f} {L([(30, -60)])[0][1]:.1f}" stroke="#A8846A" stroke-width="{1.2 * s:.1f}"/>')
    for k in range(9):
        a, b = L([(-56 + k * 13, 2), (-62 + k * 13, 16)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{1.4 * s:.1f}"/>')
    for k in range(7):
        a, = L([(-50 + k * 15, -9)])
        out.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="{3 * s:.1f}" fill="#C8963A" stroke="{col}" stroke-width="0.8"/>')
    return "".join(out)


def dragon_head(D, x, y, s, ang, pal, seed, flip=False, eye="#FFE040", horn="#E8D8A0", jaw=0.6):
    """A Greek drakon's head (facing left unless flip): long snout, jaws parted with teeth, swept-back horns,
    a glowing eye and a spiny frill. (x, y) = back of the skull; ang rotates the whole head."""
    def L(pts):
        return T(pts, x, y, s, flip, ang)
    out = []
    for sg in (-1, 1):
        h = L([(2, -8 + sg * 4), (16, -22 + sg * 8), (30, -28 + sg * 10)])
        out.append(taper(catmull(h, 6), 6 * s, 1.5 * s, horn))
    for k in range(5):
        a, b, c = L([(4 + k * 5, -10 + k * 3), (14 + k * 6, -20 + k * 5), (8 + k * 5, -6 + k * 3)])
        out.append(sharp([a, b, c], pal[2]))
    lower = L([(-2, 4), (-20, 8 + jaw * 6), (-44, 14 + jaw * 10), (-48, 18 + jaw * 10), (-26, 18 + jaw * 4), (-4, 14)])
    out.append(painted(D, lower, pal, seed + 1, sdir=(0.4, 0.8), sk=0.2, n=6, inkw=1.4 * s, inkc="#06140C", hi=0.4))
    out.append(poly(L([(-6, 4), (-44, 8 + jaw * 6), (-44, 12 + jaw * 8), (-8, 10)]), "#6A0A10"))
    upper = L([(2, -10), (-14, -16), (-30, -14), (-48, -8), (-58, -2), (-52, 3), (-30, 2), (-12, 5), (4, 6)])
    out.append(painted(D, upper, pal, seed, sdir=(0.4, 0.8), sk=0.2, n=10, inkw=1.4 * s, inkc="#06140C", hi=0.5))
    for k in range(6):
        a, b, c = L([(-48 + k * 6, 2), (-45 + k * 6, 7), (-42 + k * 6, 2)])
        out.append(sharp([a, b, c], "#FFF6E0"))
        a, b, c = L([(-44 + k * 6, 13 + jaw * 9 - k * 1.2), (-41 + k * 6, 8 + jaw * 8 - k * 1.2), (-38 + k * 6, 13 + jaw * 9 - k * 1.2)])
        out.append(sharp([a, b, c], "#FFF6E0"))
    ex, ey = L([(-20, -8)])[0]
    out.append(soft_glow(D, ex, ey, 14 * s, eye, 0.8))
    out.append(f'<path d="{blob(ex, ey, 4.4 * s, 2.6 * s, seed, 0.05, 10, ang + (180 if flip else 0))}" fill="{eye}"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.3 * s:.1f}" fill="#1A0A04"/>')
    nx, ny = L([(-52, -4)])[0]
    out.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{1.4 * s:.1f}" fill="#06140C"/>')
    return "".join(out)


def oak_crown_cluster(D, cx, cy, rx, ry, seed, pals):
    return dab_crown(D, cx, cy, rx, ry, pals, seed, n=int(rx * ry / 40), size=(6, 12), light=(0.3, -0.9), inkw=0)


@design("the-golden-fleece")
def the_golden_fleece():
    D = Doc2("my-gf")
    out = [sky(D, [(0, "#06121E"), (0.6, "#123040"), (1, "#1E4048")], 1, 600, ["#1A3A4A", "#06121E", "#2A5058"], 60)]
    out.append(stars_field(4, (0, 0, 600, 300), 80))
    out.append(moon(D, 470, 150, 34, 5, gs=0.5))
    # the sea of Colchis through the trees, the Argo waiting
    out.append(sea(D, 360, 460, [(0, "#3A6A78"), (1, "#16303A")], 6, ["#6A9AA0", "#0A1A22"], 40))
    out.append(f'<path d="{blob(470, 368, 20, 60, 3, 0.2, 10)}" fill="#FFF6D8" opacity="0.12"/>')
    out.append(argo(470, 378, 0.62))
    # the dark grove: background trees
    for k, x_ in enumerate((40, 120, 540, 590)):
        out.append(painted(D, [(x_ - 16, 620), (x_ - 12, 300), (x_ + 12, 300), (x_ + 18, 620)], ("#2A3A30", "#14201A", "#060C08"), 30 + k, sk=0.15, angle=-90, n=10, inkw=0, hi=0.2))
    for (cx_, cy_, rx_, ry_) in ((60, 230, 120, 120), (560, 220, 110, 110), (300, 60, 300, 110)):
        out.append(oak_crown_cluster(D, cx_, cy_, rx_, ry_, cx_ + cy_, [("#3A5A3A", "#1E3A26", "#0A1A10"), ("#4A6A3A", "#24402A", "#0C1C10")]))
    # ground
    gnd = [(-20, 452), (120, 440), (300, 450), (460, 444), (620, 456)]
    out.append(hill(D, gnd, 620, ("#4A5A3A", "#24301E", "#0A1008"), 6, inkw=0))
    out.append(grass(7, (0, 440, 600, 600), ["#4A6A3A", "#1E2E16", "#7A8A4A"], 200, (8, 22), 1.6))
    # the sacred oak: a massive gnarled trunk and its great branch
    tx_, base = 230, 500
    from fairy_tales_painted import gnarled_trunk
    out.append(gnarled_trunk(D, tx_, base, base - 330, 96, 8, pal=("#7A6A50", "#3A2E22", "#120C08"), rim="#FFE8A0", branches=1, rim_side=1))
    branch = catmull([(tx_ + 30, base - 290), (tx_ + 100, base - 316), (tx_ + 190, base - 320), (tx_ + 290, base - 340), (tx_ + 360, base - 330)], 8)
    out.append(taper(branch, 34, 10, "#3A2E22"))
    out.append(taper([(x, y - 6) for x, y in branch], 8, 2, "#8A7A5A", 0.5))
    out.append(oak_crown_cluster(D, 420, 120, 140, 70, 12, [("#5A7A3A", "#2E4A26", "#0E1E10"), ("#6A8A3A", "#3A5A2A", "#14240E")]))
    # the fleece hangs from the branch, glowing
    fx, fy = tx_ + 160, base - 306
    out.append(pline([(fx - 30, fy - 16), (fx - 10, fy + 8)], "#5A3A14", 2.4, 1, 1, 1))
    out.append(pline([(fx + 30, fy - 18), (fx + 10, fy + 8)], "#5A3A14", 2.4, 2, 1, 1))
    out.append(fleece(D, fx, fy + 6, 1.15, 13))
    # the sleepless dragon coiled about the trunk, head raised toward us
    dp = ("#6AB08A", "#1E6A4A", "#0A2A1E")
    for k, yy in enumerate((base - 40, base - 120, base - 200)):
        coil = [(tx_ - 62 + k * 4, yy + 18), (tx_ - 20, yy + 30), (tx_ + 30, yy + 22), (tx_ + 62 - k * 4, yy - 2)]
        out.append(snake(D, coil, 26 - k * 3, 24 - k * 3, dp, 20 + k, head=False))
        for j in range(6):
            sx_ = tx_ - 40 + j * 16
            out.append(f'<path d="M {sx_:.1f} {yy + 34 - abs(j - 3) * 2:.1f} l 6 -6" stroke="#E8D070" stroke-width="2" opacity="0.6"/>')
    neck = [(tx_ - 50, base - 210), (tx_ - 96, base - 240), (tx_ - 110, base - 290), (tx_ - 80, base - 320), (tx_ - 50, base - 318)]
    for k in range(7):
        px_, py_ = catmull(neck, 4)[2 + k * 2]
        out.append(sharp([(px_ - 7, py_ - 6), (px_ - 2, py_ - 24), (px_ + 6, py_ - 6)], "#C8A040"))
    out.append(snake(D, neck, 30, 22, dp, 30, head=False))
    out.append(dragon_head(D, tx_ - 56, base - 318, 1.25, -8, dp, 31, flip=True))
    # lettering
    out.append(gilt(D, 300, 104, "The Golden Fleece", SERIF_IT, 60, max_w=460, seed=14, deboss="#000000", dop=0.85))
    out.append(tx(300, 134, "GREEK · JASON AND THE ARGONAUTS", CINZEL, 17, "#D8F0E8", ls=3, max_w=420))
    out.append(tx(300, 532, "Guarded by a dragon that never sleeps", SERIF_IT, 24, "#FFF2C8", max_w=430))
    return fin(D, out, 21)


# ================================================================ 9. the sirens — bound to the mast
def siren(D, x, y, s, seed, flip=False, pal=("#E8C8A0", "#9A6A4A", "#3A2418"), wing_up=False):
    """A Siren as in Greek vase painting: a bird's body and wings, a woman's head with long hair (in silhouette/profile)."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    body = L([(-24, 0), (-12, -14), (8, -16), (22, -8), (40, 8), (52, 14), (30, 14), (6, 18), (-14, 12)])
    out.append(painted(D, body, pal, seed, sdir=(0.4, 0.8), sk=0.2, angle=0, n=10, inkw=1.2, inkc="#1A0E08", hi=0.4))
    wing = L([(-6, -8), (12, -22), (34, -24), (56, -14), (42, -8), (54, -4), (34, 0), (14, 2)]) if not wing_up else L([(-6, -8), (0, -40), (10, -60), (26, -66), (28, -48), (36, -44), (24, -18), (12, 0)])
    out.append(painted(D, wing, (lt(pal[1], 0.2), dk(pal[1], 0.15), pal[2]), seed + 1, sdir=(0.4, 0.8), sk=0.2, angle=-20, n=10, inkw=1.2, inkc="#1A0E08", hi=0.4))
    for k in range(4):
        a, b = L([(4 + k * 9, -8), (16 + k * 9, -18 if not wing_up else -40)]) if not wing_up else L([(4 + k * 4, -10), (8 + k * 6, -50 + k * 4)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{pal[2]}" stroke-width="1" opacity="0.6"/>')
    # a woman's head in profile, long dark hair falling down the back
    out.append(taper(catmull(L([(-24, -28), (-14, -18), (-8, -4), (-2, 8)]), 6), 12 * s, 3 * s, "#2A1410"))
    out.append(poly(L([(-20, -16), (-26, -10), (-22, -2), (-14, -6)]), "#E8C4A0"))
    head = L([(-18, -24), (-22, -32), (-30, -32), (-35, -26), (-37, -20), (-34, -18), (-35, -14), (-31, -11), (-26, -10), (-20, -14)])
    out.append(painted(D, head, ("#FBE2C8", "#E8BC98", "#A8785A"), seed + 7, sdir=(0.6, 0.4), sk=0.15, n=4, inkw=1.0, inkc="#5A3020", hi=0.4))
    out.append(poly(L([(-18, -22), (-20, -32), (-28, -35), (-34, -30), (-28, -30), (-24, -24), (-22, -14), (-16, -14)]), "#2A1410"))
    out.append(poly(L([(-26, -36), (-22, -42), (-16, -38), (-20, -33)]), "#2A1410"))
    for k in range(2):
        a, b = L([(-4, 16), (-6 + k * 8, 28)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A1A10" stroke-width="{2 * s:.1f}" stroke-linecap="round"/>')
    return "".join(out)


def galley(D, x, wl, s, seed, col="#14100E"):
    """Greek pentekonter: black hull, bronze ram, the painted eye, a row of oars, the mast with Odysseus bound to it."""
    def L(pts):
        return T(pts, x, wl, s)
    out = []
    hull = L([(-170, -24), (-150, -10), (-100, 0), (100, 0), (150, -8), (176, -12), (196, 6), (170, 8), (150, 14), (-110, 18), (-160, 6), (-178, -20), (-196, -44), (-184, -48)])
    out.append(painted(D, hull, ("#5A4A42", "#1E1614", "#060404"), seed, sdir=(0.3, 0.8), sk=0.2, angle=0, n=30, inkw=1.6, inkc="#000000", hi=0.4))
    out.append(taper(L([(-160, -8), (0, -2), (150, -6)]), 3 * s, 3 * s, "#C8402A"))
    out.append(sharp(L([(176, -6), (210, 2), (176, 8)]), "#C8902A"))
    ex, ey = L([(150, -4)])[0]
    out.append(f'<path d="{blob(ex, ey, 7 * s, 3.6 * s, 2, 0.05, 10)}" fill="#FFFFFF"/><circle cx="{ex + 1:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="#000000"/>')
    for k in range(13):
        a, b = L([(-120 + k * 19, 6), (-136 + k * 19, 44)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{2.2 * s:.1f}" stroke-linecap="round"/>')
    # rowers' heads along the rail, ears stopped with wax
    for k in range(9):
        hx, hy = L([(-110 + k * 24, -8)])[0]
        out.append(f'<path d="{blob(hx, hy, 5.2 * s, 6 * s, k, 0.08, 10)}" fill="{col}"/>')
    # the curling stern ornament
    out.append(taper(catmull(L([(-178, -22), (-200, -50), (-196, -76), (-180, -84), (-172, -72)]), 6), 10 * s, 3 * s, col))
    # mast, yard, furled sail, rigging
    mx, mb = L([(10, -2)])[0]
    top = L([(10, -250)])[0]
    out.append(taper([(mx, mb), top], 7 * s, 4 * s, "#3A2A1E"))
    out.append(taper(L([(-90, -224), (110, -230)]), 5 * s, 4 * s, "#3A2A1E"))
    out.append(taper(L([(-84, -218), (10, -214), (104, -222)]), 12 * s, 10 * s, "#E8D8B8"))
    out.append(pline(L([(-84, -212), (10, -206), (104, -216)]), "#A8906A", 1.4, 3, 0.8, 1))
    for (a, b) in (((10, -248), (-170, -30)), ((10, -248), (180, -12)), ((-90, -224), (-130, -6)), ((110, -230), (130, -6))):
        p, q = L([a, b])
        out.append(f'<path d="M {p[0]:.1f} {p[1]:.1f} L {q[0]:.1f} {q[1]:.1f}" stroke="#2A1E16" stroke-width="{1.2 * s:.1f}" opacity="0.8"/>')
    # Odysseus bound to the mast, straining toward the song
    ox, ob = L([(10, -2)])[0]
    out.append(robed_figure(ox + 4 * s, ob, 0.9 * s, col, facing=1, rim="#FFC870", head="bare", lean=6))
    for k in range(4):
        yy = ob - (26 + k * 16) * s
        out.append(f'<path d="M {ox - 14 * s:.1f} {yy:.1f} q {14 * s:.1f} {6 * s:.1f} {28 * s:.1f} {-2 * s:.1f}" stroke="#D8B878" stroke-width="{2.4 * s:.1f}" fill="none"/>')
    return "".join(out)


@design("the-sirens")
def the_sirens():
    D = Doc2("my-sr")
    out = [sky(D, [(0, "#2A3A6A"), (0.35, "#8A6A8A"), (0.62, "#F2A86A"), (0.72, "#FCD89A")], 1, 380, ["#6A6A9A", "#F2B87A", "#C88A8A"], 60)]
    sx, sy = 430, 330
    out.append(soft_glow(D, sx, sy, 240, "#FFE0A0", 0.7))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="44" fill="#FFF2C8"/>')
    for (cx_, cy_, w_, sd) in ((110, 236, 190, 2), (300, 206, 130, 3), (560, 196, 130, 4)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#FFE2C0", "#C89A9A", "#7A5A7A"), op=0.85))
    # the wine-dark sea
    out.append(sea(D, 360, 620, [(0, "#C8786A"), (0.3, "#5A3A5A"), (1, "#1A1430")], 5, ["#F2A87A", "#1A1430", "#8A5A7A"], 80))
    rnd = random.Random(4)
    for k in range(40):
        y = 364 + (k / 40) ** 1.5 * 160
        w = 10 + (y - 360) * 0.6
        x = sx + rnd.uniform(-w, w) * 0.5
        out.append(taper([(x - w * 0.3, y), (x, y - 1.5), (x + w * 0.3, y)], 0.8, rnd.uniform(1.5, 3.5), "#FFE2A0", rnd.uniform(0.4, 0.85)))
    # the Sirens' rocky isle, strewn with bones, the singers on its crags
    isle = [(330, 372), (360, 340), (392, 300), (420, 282), (452, 262), (478, 270), (500, 250), (530, 262), (560, 300), (600, 330), (640, 360), (640, 400), (330, 400)]
    out.append(painted(D, isle, ("#7A5A6A", "#3A2A3A", "#140C16"), 7, sdir=(-0.6, 0.4), sk=0.2, angle=-70, n=50, inkw=1.4, inkc="#0A0610", hi=0.0))
    out.append(ink(smooth_open(isle[1:10]), "#FFD8A0", 2.4, 4, 1, 0.7))
    for (bx_, by_) in ((370, 372), (396, 378), (560, 368)):
        out.append(pline([(bx_, by_), (bx_ + 10, by_ - 2)], "#F2E8D8", 2.4, 1, 0.9, 1))
        out.append(f'<circle cx="{bx_:.1f}" cy="{by_:.1f}" r="2.2" fill="#F2E8D8"/><circle cx="{bx_ + 10:.1f}" cy="{by_ - 2:.1f}" r="2.2" fill="#F2E8D8"/>')
    out.append(siren(D, 398, 300, 1.15, 1, flip=False, wing_up=True))
    out.append(siren(D, 470, 256, 1.25, 2, flip=False))
    out.append(siren(D, 512, 318, 1.05, 3, flip=False, wing_up=True))
    # their song drifting over the water
    for k in range(3):
        p = catmull([(400, 270 - k * 10), (330, 250 - k * 18), (260, 268 - k * 12), (200, 250 - k * 16)], 8)
        out.append(taper(p, 2.4, 0.6, "#FFF2D8", 0.6 - k * 0.12))
    for k in range(6):
        out.append(sparkle(rnd.uniform(220, 380), rnd.uniform(220, 280), rnd.uniform(2, 4), "#FFF6E0", 0.8))
    out.append(wave_lines(8, (0, 380, 600, 600), ["#F2B88A", "#1A1430", "#8A5A7A"], 60, (10, 34), 1.8, 2.5, (0.3, 0.7)))
    # the black ship sailing past, Odysseus bound upright to the mast
    out.append(galley(D, 220, 470, 0.95, 9))
    out.append(swell(D, 500, 6, 160, 0.4, ("#8A5A7A", "#4A2E4A", "#1A1024"), 20))
    # lettering
    out.append(letters(D, 300, 110, "The Sirens", SERIF_IT, 70, "#FFF6E6", ["#FFFFFF", "#FFE2C0", "#F2D0D8"], 13, max_w=380,
                       shadow="#2A1A3A", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(301.5, 143.5, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#2A1A3A", ls=3, max_w=380, op=0.6))
    out.append(tx(300, 142, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#FFF2E0", ls=3, max_w=380))
    out.append(tx(300, 538, "“Bind me fast to the mast.”", SERIF_IT, 30, "#FFF2E0", max_w=420))
    return fin(D, out, 22)


# ================================================================ 10. poseidon — the trident and the sea-horses
def arc_text(D, cx, cy, r, s, font, size, fill, ls=0, a_mid=-90, flip=False, extra=""):
    """Text centred on an arc (top of a circle) using textPath."""
    uid = D.nid()
    fs = size
    W = measure(s, font, fs, ls)
    span = W / r
    a0 = math.radians(a_mid) - span / 2 - 0.3
    a1 = math.radians(a_mid) + span / 2 + 0.3
    d = f"M {cx + math.cos(a0) * r:.1f} {cy + math.sin(a0) * r:.1f} A {r} {r} 0 0 1 {cx + math.cos(a1) * r:.1f} {cy + math.sin(a1) * r:.1f}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    D.defs.append(f'<path id="{uid}" d="{d}"/>')
    return f'<text {font} font-size="{fs}"{lsa} fill="{fill}"{extra}><textPath href="#{uid}" startOffset="50%" text-anchor="middle">{esc(s)}</textPath></text>'


def trident(D, cx, top, h, seed, pal=GOLD):
    out = []
    shaft = [(cx - 5, top + 40), (cx + 5, top + 40), (cx + 4, top + h), (cx - 4, top + h)]
    out.append(painted(D, shaft, pal, seed, sdir=(0.8, 0.1), sk=0.2, angle=-90, n=10, inkw=1.4, inkc="#4A2A06", hi=0.5))
    for sg in (-1, 0, 1):
        if sg == 0:
            prong = [(cx - 5, top + 40), (cx - 5, top + 10), (cx - 10, top + 12), (cx, top - 12), (cx + 10, top + 12), (cx + 5, top + 10), (cx + 5, top + 40)]
        else:
            x0 = cx + sg * 38
            prong = [(cx + sg * 4, top + 48), (x0 - sg * 6, top + 40), (x0 - sg * 4, top + 18), (x0 - sg * 10, top + 20), (x0, top - 2), (x0 + sg * 8, top + 22),
                     (x0 + sg * 4, top + 22), (x0 + sg * 4, top + 50), (cx + sg * 4, top + 62)]
        out.append(painted(D, prong, pal, seed + sg + 3, sdir=(0.8, 0.2), sk=0.2, angle=-90, n=8, inkw=1.4, inkc="#4A2A06", hi=0.55))
    out.append(painted(D, [(cx - 14, top + 54), (cx + 14, top + 54), (cx + 12, top + 70), (cx - 12, top + 70)], pal, seed + 9, sk=0.2, n=4, inkw=1.2, inkc="#4A2A06", hi=0.5))
    return "".join(out)


@design("poseidon")
def poseidon():
    D = Doc2("my-po")
    out = [sky(D, [(0, "#0A2A3A"), (0.5, "#1E5A6A"), (1, "#3A8A8A")], 1, 600, ["#2A6A7A", "#0A2A3A", "#5AA0A0"], 60)]
    cx = 300
    out.append(soft_glow(D, cx, 300, 300, "#E8FFF2", 0.45))
    out.append(ray_fan(cx, 300, 40, 430, 36, "#F2FFF6", 0.14, seed=3))
    # towering wave crests framing the scene on both sides
    for sg in (-1, 1):
        crest = [(cx + sg * 330, 620), (cx + sg * 330, 200), (cx + sg * 300, 150), (cx + sg * 250, 140), (cx + sg * 210, 170), (cx + sg * 214, 200),
                 (cx + sg * 240, 196), (cx + sg * 250, 220), (cx + sg * 220, 280), (cx + sg * 190, 380), (cx + sg * 170, 620)]
        out.append(painted(D, crest, ("#7ACAC0", "#1E7078", "#06303A"), 4 + sg, sdir=(sg * -0.6, 0.4), sk=0.2, angle=-70 if sg < 0 else -110, n=60, inkw=1.6, inkc="#04202A", hi=0.5))
        for k in range(14):
            t = k / 13
            p = catmull([(cx + sg * 250, 140), (cx + sg * 210, 170), (cx + sg * 236, 196)], 6)
            x_, y_ = p[min(len(p) - 1, int(t * (len(p) - 1)))]
            out.append(f'<path d="{blob(x_ + sg * -4, y_, 9, 6, k + sg * 50, 0.2, 10)}" fill="#F2FFFA" opacity="0.9"/>')
        for k in range(5):
            p = catmull([(cx + sg * (300 - k * 14), 200 + k * 30), (cx + sg * (250 - k * 10), 260 + k * 40), (cx + sg * (230 - k * 6), 400 + k * 40)], 6)
            out.append(taper(p, 1, 3, "#B8F0E8", 0.5))
    # the whirlpool the trident rises from
    for k in range(9):
        r = 200 - k * 20
        out.append(f'<path d="{smooth_closed(ell_pts(cx, 470, r, r * 0.26, 0, 360, 30))}" fill="none" stroke="{("#F2FFFA", "#6AC0B8", "#1E6A72")[k % 3]}" stroke-width="{3 - k * 0.2:.1f}" opacity="0.65"/>')
    out.append(sea(D, 470, 620, [(0, "#2A8088"), (1, "#06303A")], 6, ["#6AC0B8", "#04202A"], 40))
    for k in range(5):
        r = 220 - k * 36
        out.append(f'<path d="{smooth_open(ell_pts(cx, 474, r, r * 0.22, 10, 170, 20))}" fill="none" stroke="#E8FFF8" stroke-width="2.4" opacity="0.55"/>')
    # the two hippocamps rearing toward the trident
    out.append(hippocamp(D, 130, 316, 1.05, 7, ("#9AE0D0", "#2A9090", "#0A3A44"), flip=True, rim="#F2FFF6"))
    out.append(hippocamp(D, 470, 316, 1.05, 8, ("#9AE0D0", "#2A9090", "#0A3A44"), flip=False, rim="#F2FFF6"))
    # the trident
    out.append(soft_glow(D, cx, 210, 120, "#FFF2B0", 0.6))
    out.append(trident(D, cx, 168, 304, 9))
    for k in range(12):
        a = random.Random(k).uniform(0, 6.28)
        out.append(sparkle(cx + math.cos(a) * 60, 200 + math.sin(a) * 50, 2 + k % 3, "#FFFFFF", 0.85))
    # spray
    rnd = random.Random(5)
    for k in range(60):
        out.append(f'<circle cx="{rnd.uniform(60, 540):.1f}" cy="{rnd.uniform(420, 470):.1f}" r="{rnd.uniform(1, 3):.1f}" fill="#F2FFFA" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # lettering: the name arched above, the epithet below
    out.append(arc_text(D, cx, 360, 270, "POSEIDON", CINZEL, 54, "#04202A", ls=12, extra=' opacity="0.5" transform="translate(2 3)"'))
    out.append(arc_text(D, cx, 360, 270, "POSEIDON", CINZEL, 54, gilt_fill(D, 70, 140), ls=12))
    out.append(tx(cx + 1.5, 534, "GREEK · THE EARTH-SHAKER, LORD OF THE SEA", CINZEL, 17, "#04202A", ls=2, max_w=440, op=0.6))
    out.append(tx(cx, 532, "GREEK · THE EARTH-SHAKER, LORD OF THE SEA", CINZEL, 17, "#F2FFF6", ls=2, max_w=440))
    return fin(D, out, 23)


# ================================================================ 11. sleipnir — Odin's eight-legged horse over the clouds
@design("sleipnir")
def sleipnir():
    D = Doc2("my-sl")
    out = [sky(D, [(0, "#060A1E"), (0.5, "#10203A"), (1, "#1E3A4A")], 1, 600, ["#14284A", "#04081A", "#2A4A5A"], 60)]
    out.append(stars_field(5, (0, 0, 600, 600), 160))
    out.append(aurora(D, 6, 90, 330, cols=("#7AF0C0", "#5AE0A0", "#8AC8F0")))
    out.append(moon(D, 500, 236, 38, 7, gs=0.45))
    # a sea of clouds below, lit by the moon
    for (cx_, cy_, w_, sd) in ((80, 470, 260, 3), (330, 500, 320, 4), (560, 470, 240, 5), (200, 560, 300, 6), (470, 580, 300, 7)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#E8F0FF", "#8A9AC0", "#3A4A6A"), op=0.95))
    # Sleipnir at full gallop, eight legs reaching and gathering
    legs = [((-66, 50), (-100, 70), (-130, 66), (-12, 8), "far"), ((-58, 52), (-80, 84), (-74, 112), (-8, 10), "far"),
            ((70, 48), (96, 78), (130, 96), (10, 6), "far"), ((60, 50), (64, 86), (48, 116), (-8, 10), "far"),
            ((-70, 50), (-110, 60), (-144, 46), (-14, 4), "near"), ((-54, 54), (-66, 88), (-52, 118), (-6, 10), "near"),
            ((74, 44), (110, 64), (150, 70), (12, 4), "near"), ((56, 48), (52, 84), (30, 112), (-10, 8), "near")]
    hx, hy = 318, 326
    out.append(cast(D, hx, 470, 170, 14, "#1A2A4A", 0.4, 2))
    out.append(horse(D, hx, hy, 1.1, 8, ("#E8ECF2", "#A8B0C0", "#4A5268"), legs, mane="#F8FAFF", rim="#E8FFF4"))
    # Odin riding: a cloaked figure with a broad hat and a spear, cloak streaming back
    rx, ry = hx - 14, hy - 40
    cloak = [(rx - 10, ry - 70), (rx + 40, ry - 60), (rx + 120, ry - 50), (rx + 170, ry - 30), (rx + 130, ry - 20), (rx + 150, ry - 6), (rx + 60, ry + 6), (rx + 10, ry + 20), (rx - 14, ry)]
    out.append(painted(D, cloak, ("#4A5A8A", "#1E2848", "#080C1E"), 9, sdir=(0.3, 0.8), sk=0.2, angle=0, n=20, inkw=1.2, inkc="#04060E", hi=0.35))
    out.append(poly([(rx - 16, ry + 20), (rx - 20, ry - 30), (rx - 12, ry - 66), (rx + 8, ry - 70), (rx + 16, ry - 40), (rx + 14, ry + 10)], "#0E1428"))
    out.append(taper([(rx - 4, ry + 14), (rx - 22, ry + 44), (rx - 30, ry + 70)], 10, 7, "#0E1428"))
    out.append(f'<path d="{blob(rx - 4, ry - 80, 9, 10, 3, 0.06, 10)}" fill="#0E1428"/>')
    out.append(taper([(rx - 10, ry - 74), (rx - 22, ry - 50), (rx - 18, ry - 30)], 8, 2, "#C8D0E8"))
    out.append(poly([(rx - 30, ry - 84), (rx + 24, ry - 86), (rx + 12, ry - 90), (rx + 4, ry - 108), (rx - 10, ry - 106), (rx - 16, ry - 90)], "#0E1428"))
    out.append(ink(smooth_open([(rx - 30, ry - 84), (rx + 24, ry - 86)]), "#E8FFF4", 1.6, 2, 1, 0.8))
    out.append(taper([(rx + 50, ry + 30), (rx - 30, ry - 70), (rx - 70, ry - 120)], 3.2, 2.6, "#C8B890"))
    out.append(sharp([(rx - 64, ry - 112), (rx - 82, ry - 138), (rx - 72, ry - 110)], "#E8ECF2"))
    out.append(taper([(rx - 14, ry - 50), (rx - 40, ry - 52), (rx - 52, ry - 66)], 7, 5, "#0E1428"))
    out.append(ink(smooth_open([(rx + 8, ry - 70), (rx + 16, ry - 40), (rx + 14, ry + 10)]), "#E8FFF4", 1.6, 3, 1, 0.7))
    # lettering
    out.append(letters(D, 300, 124, "Sleipnir", DMS, 92, "#F2FFF8", ["#FFFFFF", "#C8F0E0", "#E8F0FF"], 14, max_w=380,
                       shadow="#04081A", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 160, "NORSE · ODIN’S EIGHT-LEGGED STEED", CINZEL, 16, "#C8F0E0", ls=3, max_w=420))
    return fin(D, out, 24)


# ================================================================ 12. bifröst — the burning rainbow bridge
def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def offset(path, d):
    out = []
    for i, (x, y) in enumerate(path):
        a = path[max(0, i - 1)]
        b = path[min(len(path) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L_ = math.hypot(dx, dy) or 1
        out.append((x - dy / L_ * d, y + dx / L_ * d))
    return out


@design("bifrost")
def bifrost():
    D = Doc2("my-bf")
    out = [sky(D, [(0, "#24305E"), (0.35, "#5A6AA8"), (0.62, "#E8B0A8"), (0.78, "#FCE0C0")], 1, 470, ["#4A5A9A", "#FFD8B8", "#8A8AC0"], 60)]
    out.append(stars_field(3, (0, 0, 600, 140), 40))
    out.append(soft_glow(D, 440, 180, 220, "#FFF2C8", 0.6))
    # Asgard: golden halls on a cloud-mountain, high on the right
    for (cx_, cy_, w_, sd) in ((470, 300, 300, 3), (540, 272, 200, 4), (360, 300, 200, 5)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#FFF6E8", "#E8C8C8", "#A88AA8"), op=0.95))
    # Midgard below: fjord mountains, water, the near hill with its pines
    m1 = ridge([(-20, 400), (60, 330), (150, 356), (240, 310), (330, 380), (420, 350), (520, 390), (620, 360)], 9, 16)
    out.append(hill(D, m1, 480, ("#A8A0C8", "#7A72A0", "#4A4270"), 9, inkw=0, lit="#FFE8D8"))
    out.append(sea(D, 440, 500, [(0, "#F2C8B8"), (1, "#5A5A8A")], 4, ["#FFE8D8", "#4A4A7A"], 30))
    out.append(mist(D, 440, 30, 6, "#FFF2E8", 0.5))
    m2 = ridge([(-20, 460), (60, 430), (140, 420), (220, 444), (300, 476), (360, 486), (620, 476)], 10, 12)
    out.append(hill(D, m2, 620, ("#6A7A6A", "#3A4A44", "#141E1C"), 10, inkw=1.4))
    for k in range(13):
        out.append(conifer(300 + k * 22 + (k % 3) * 6, 490 + (k % 2) * 6, 24 + (k % 4) * 6, "#1A2620", k, width=0.26))
    # the bridge: seven luminous bands from the near hill up into the clouds, the red band burning
    spine = bezier((96, 436), (120, 160), (300, 100), (408, 236), 60)
    out.append(taper(spine, 90, 90, "#FFFFFF", 0.12))
    out.append(taper(spine, 120, 120, "#FFE8D0", 0.08))
    cols = ["#F2503A", "#F6963A", "#F8D85A", "#7ACB6A", "#4AA0E0", "#5A62C8", "#9A62C8"]
    out.append(taper(offset(spine, -10), 110, 110, "#FFFFFF", 0.0))
    g = D.lin([(0, "#FFFFFF", 0), (0.15, "#FFFFFF", 0.35), (1, "#FFFFFF", 0.1)], 0, 0, 1, 0)
    for k, c in enumerate(cols):
        band = offset(spine, (k - 3) * 10)
        out.append(taper(band, 11, 11, c, 0.74))
    out.append(taper(offset(spine, -4), 4, 4, "#FFFFFF", 0.35))
    rnd = random.Random(11)
    edge = offset(spine, -36)
    for i in range(4, len(edge) - 6):
        x, y = edge[i]
        (xa, ya), (xb, yb) = edge[i - 1], edge[i + 1]
        a = math.atan2(yb - ya, xb - xa) + math.pi / 2
        for _ in range(2):
            h = rnd.uniform(8, 20)
            ox, oy = x + rnd.uniform(-3, 3), y + rnd.uniform(-3, 3)
            tipx, tipy = ox - math.cos(a) * h + rnd.uniform(-3, 3), oy - math.sin(a) * h
            out.append(f'<path d="M {ox - 4:.1f} {oy:.1f} Q {ox + rnd.uniform(-3, 3):.1f} {oy - math.sin(a) * h * 0.5:.1f} {tipx:.1f} {tipy:.1f} Q {ox + 2:.1f} {oy - math.sin(a) * h * 0.4:.1f} {ox + 4:.1f} {oy:.1f} Z" '
                       f'fill="{rnd.choice(["#FFB040", "#FF6A2A", "#FFE070"])}" opacity="0.85"/>')
    out.append(soft_glow(D, 130, 240, 120, "#FFB070", 0.25))
    # the far end disappears into the cloud of Asgard
    out.append(puff_cloud(D, 400, 282, 170, 12, ("#FFFFFF", "#F6E2DA", "#D8B8C0"), op=0.97))
    for k in range(18):
        p = spine[rnd.randint(4, len(spine) - 8)]
        out.append(sparkle(p[0] + rnd.uniform(-40, 40), p[1] + rnd.uniform(-30, 30), rnd.uniform(1.5, 4), "#FFFFFF", rnd.uniform(0.6, 1)))
    hall_x, hall_y = 456, 214
    out.append(soft_glow(D, hall_x, hall_y - 30, 120, "#FFE070", 0.85))
    for (dx, w, h, sd) in ((-74, 30, 50, 1), (78, 34, 56, 2), (0, 56, 84, 3)):
        x0 = hall_x + dx
        wall = poly_pts([(x0 - w, hall_y), (x0 - w, hall_y - h * 0.4), (x0 + w, hall_y - h * 0.4), (x0 + w, hall_y)], 8, sd, 0.3)
        out.append(painted(D, wall, ("#F6E2B0", "#C89A50", "#6A4A18"), 6 + sd, sdir=(0.6, 0.3), sk=0.15, angle=-90, n=8, inkw=1.2, inkc="#5A3A08", hi=0.4))
        for k in range(int(w / 10)):
            out.append(f'<rect x="{x0 - w + 8 + k * 20:.1f}" y="{hall_y - h * 0.32:.1f}" width="5" height="{h * 0.22:.1f}" fill="#FFF6C0"/>')
        roof = poly_pts([(x0 - w - 8, hall_y - h * 0.36), (x0 - w * 0.55, hall_y - h), (x0 + w * 0.55, hall_y - h), (x0 + w + 8, hall_y - h * 0.36)], 8, sd + 5, 0.3)
        out.append(painted(D, roof, GOLD, 9 + sd, sdir=(0.6, 0.4), sk=0.2, angle=0, n=12, inkw=1.4, inkc="#6A4A10", hi=0.55))
        for r_ in range(1, 4):
            yy = hall_y - h * 0.36 - (h * 0.64) * r_ / 4
            xl = x0 - w - 8 + (w * 0.45 + 8) * r_ / 4
            out.append(f'<path d="M {xl:.1f} {yy:.1f} L {2 * x0 - xl:.1f} {yy:.1f}" stroke="#8A6020" stroke-width="1.2" opacity="0.7"/>')
            for q in range(int((2 * x0 - 2 * xl) / 9)):
                out.append(f'<path d="M {xl + 4 + q * 9:.1f} {yy:.1f} q 4.5 6 9 0" stroke="#8A6020" stroke-width="1" fill="none" opacity="0.5"/>')
        for sg in (-1, 1):
            ex = x0 + sg * w * 0.55
            out.append(taper(catmull([(ex, hall_y - h), (ex + sg * 6, hall_y - h - 12), (ex + sg * 14, hall_y - h - 14), (ex + sg * 16, hall_y - h - 8)], 5), 4, 1.5, "#B8802A"))
    out.append(mist(D, 218, 22, 13, "#FFFFFF", 0.6, 360, 560))
    # Heimdall at the foot of the bridge, Gjallarhorn raised
    hx, hb = 132, 452
    out.append(soft_glow(D, hx, hb - 50, 50, "#FFE8C0", 0.45))
    out.append(robed_figure(hx, hb, 0.62, "#141A1E", facing=1, rim="#FFE0B0", cloak=0.5, head="helmet", arm="up"))
    out.append(taper(catmull([(hx + 16, hb - 66), (hx + 26, hb - 82), (hx + 40, hb - 92)], 6), 2.4, 9, "#E8D8B0"))
    # lettering, low on the dark hill
    out.append(letters(D, 300, 520, "Bifröst", SERIF_IT, 84, "#FFFFFF", ["#FFFFFF", "#FFE8D8", "#E8E8FF"], 15, max_w=320,
                       shadow="#0A1010", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 548 - 10, "NORSE · THE BURNING BRIDGE TO ASGARD", CINZEL, 16, "#FFE8D0", ls=2.5, max_w=430))
    return fin(D, out, 25)


# ================================================================ 13. thor's goats — the thunder-chariot across the storm
def goat(D, x, y, s, seed, pal, legs_phase=0, flip=False, rim=None):
    """A galloping billy goat in side view (facing left): beard, back-swept ridged horns, short tail up."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    ph = legs_phase
    legs = [((-34, 20), (-58 - 6 * ph, 30), (-70 - 4 * ph, 48)), ((-26, 22), (-30 + 10 * ph, 40), (-20 + 8 * ph, 58)),
            ((34, 18), (52 + 4 * ph, 34), (66 + 6 * ph, 46)), ((28, 20), (24 - 6 * ph, 38), (12 - 6 * ph, 54))]
    for k in (1, 3):
        r_, k_, f_ = L(list(legs[k]))
        out.append(taper(catmull([r_, k_, f_], 6), 9 * s, 4.4 * s, dk(pal[1], 0.3)))
        out.append(f'<path d="{blob(f_[0], f_[1], 4 * s, 3 * s, k, 0.1, 8)}" fill="#1A1410"/>')
    body = L([(-50, -6), (-40, -18), (-10, -22), (30, -20), (50, -12), (56, 4), (46, 20), (20, 24), (-20, 26), (-42, 22), (-52, 10)])
    out.append(painted(D, body, pal, seed, sdir=(0.3, 0.8), sk=0.2, angle=-10, n=26, inkw=1.4, inkc="#100A06", hi=0.4))
    # shaggy coat strokes
    rnd = random.Random(seed)
    for k in range(18):
        px, py = L([(rnd.uniform(-40, 46), rnd.uniform(8, 24))])[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} l {-2 * s:.1f} {7 * s:.1f}" stroke="{pal[2]}" stroke-width="{1.4 * s:.1f}" stroke-linecap="round" opacity="0.7"/>')
    out.append(poly(L([(50, -12), (60, -26), (64, -22), (56, -8)]), pal[1]))
    # neck and head
    neck = L([(-40, -16), (-58, -34), (-70, -40), (-66, -24), (-50, 4)])
    out.append(painted(D, neck, pal, seed + 1, sdir=(0.3, 0.8), sk=0.15, n=8, inkw=1.2, inkc="#100A06", hi=0.4))
    head = L([(-62, -42), (-72, -46), (-90, -38), (-98, -30), (-96, -24), (-84, -22), (-70, -26), (-62, -30)])
    out.append(painted(D, head, pal, seed + 2, sdir=(0.3, 0.8), sk=0.15, n=8, inkw=1.2, inkc="#100A06", hi=0.45))
    out.append(poly(L([(-86, -24), (-82, -10), (-76, 0), (-74, -14), (-74, -24)]), lt(pal[0], 0.2)))
    out.append(poly(L([(-66, -44), (-58, -50), (-56, -44), (-62, -40)]), pal[2]))
    horn = catmull(L([(-70, -46), (-64, -64), (-46, -78), (-24, -76), (-14, -64)]), 8)
    out.append(taper(horn, 9 * s, 2.4 * s, "#E8D8B0"))
    for i in range(2, len(horn) - 3, 2):
        out.append(f'<circle cx="{horn[i][0]:.1f}" cy="{horn[i][1]:.1f}" r="{1.6 * s:.1f}" fill="#8A7A5A" opacity="0.6"/>')
    out.append(taper([(px - 0.6, py - 0.6) for px, py in horn], 2 * s, 0.6 * s, "#FFFFFF", 0.6))
    ex, ey = L([(-78, -38)])[0]
    out.append(f'<path d="{blob(ex, ey, 3 * s, 2 * s, seed, 0.05, 8)}" fill="#F2C84A"/><path d="M {ex - 2 * s:.1f} {ey:.1f} l {4 * s:.1f} 0" stroke="#1A1006" stroke-width="{1.4 * s:.1f}"/>')
    for k in (0, 2):
        r_, k_, f_ = L(list(legs[k]))
        out.append(taper(catmull([r_, k_, f_], 6), 10 * s, 4.6 * s, pal[1]))
        out.append(f'<path d="{blob(f_[0], f_[1], 4.2 * s, 3 * s, k, 0.1, 8)}" fill="#1A1410"/>')
    if rim:
        out.append(ink(smooth_open(L([(-98, -30), (-90, -38), (-72, -46), (-58, -34), (-40, -18), (-10, -22), (30, -20), (50, -12)])), rim, 1.8, seed, 1, 0.75))
    return "".join(out)


def spoked_wheel(D, cx, cy, r, seed, col="#2A1E14", hub="#C8963A", spokes=8, rot_=0):
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{col}" stroke-width="{r * 0.16:.1f}"/>']
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.92:.1f}" fill="none" stroke="{lt(col, 0.2)}" stroke-width="1.2" opacity="0.6"/>')
    for k in range(spokes):
        a = math.radians(rot_ + k * 360 / spokes)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * r * 0.92:.1f} {cy + math.sin(a) * r * 0.92:.1f}" stroke="{col}" stroke-width="{r * 0.08:.1f}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.18:.1f}" fill="{hub}" stroke="{col}" stroke-width="1.4"/>')
    return "".join(out)


@design("thors-goats")
def thors_goats():
    D = Doc2("my-tg")
    out = [sky(D, [(0, "#14182A"), (0.5, "#2A3048"), (1, "#4A4A5A")], 1, 600, ["#3A4060", "#0E1020", "#5A5A70"], 70)]
    # rain slanting across the far storm
    rnd = random.Random(3)
    for k in range(80):
        x, y = rnd.uniform(-40, 600), rnd.uniform(120, 600)
        out.append(f'<path d="M {x:.1f} {y:.1f} l -10 26" stroke="#9AA8C8" stroke-width="1.2" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    # far storm clouds and the light breaking through
    out.append(soft_glow(D, 470, 200, 200, "#C8D8FF", 0.35))
    for (cx_, cy_, w_, sd) in ((90, 200, 260, 3), (500, 160, 260, 4), (300, 250, 220, 5)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#7A80A0", "#3A4060", "#14182A"), op=0.95))
    # forked lightning
    for (pts, w) in (([(150, 150), (166, 196), (150, 200), (176, 250), (160, 254), (186, 300)], 3), ([(166, 196), (200, 214), (214, 240)], 2), ([(560, 170), (548, 210), (562, 214), (544, 262)], 2)):
        out.append(soft_glow(D, pts[len(pts) // 2][0], pts[len(pts) // 2][1], 80, "#C8D8FF", 0.4))
        out.append(pline(pts, "#9AB0FF", w * 3, 2, 0.3, 1))
        out.append(pline(pts, "#FFFFFF", w, 2, 1, 1))
    # the cloud road the chariot runs on
    for (cx_, cy_, w_, sd) in ((60, 480, 260, 6), (300, 500, 340, 7), (540, 480, 260, 8), (180, 570, 300, 9), (440, 580, 320, 10)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#B8C0D8", "#6A7090", "#2A2E44"), op=0.97))
    # the chariot, wheels throwing sparks, Thor at the reins
    cx_, cy_ = 430, 384
    out.append(painted(D, [(cx_ - 56, cy_ - 34), (cx_ + 66, cy_ - 40), (cx_ + 78, cy_ - 4), (cx_ + 56, cy_ + 14), (cx_ - 44, cy_ + 14), (cx_ - 62, cy_ - 4)],
                       ("#C8925E", "#7A4A26", "#2A1408"), 4, sdir=(0.3, 0.8), sk=0.2, angle=0, n=20, inkw=1.6, inkc="#100804", hi=0.4))
    for k in range(5):
        out.append(f'<path d="M {cx_ - 48 + k * 27:.1f} {cy_ - 32:.1f} q 6 20 0 40" stroke="#C8963A" stroke-width="2" fill="none" opacity="0.8"/>')
    out.append(taper([(cx_ - 58, cy_ - 4), (cx_ - 150, cy_ - 4), (cx_ - 220, cy_ - 14)], 7, 5, "#5A3418"))
    # Thor: a big figure seen from behind-side, red cloak and red beard flying back, reins in his fists
    tx_, tb = cx_ + 14, cy_ - 30
    out.append(painted(D, [(tx_ - 6, tb - 112), (tx_ + 50, tb - 104), (tx_ + 120, tb - 86), (tx_ + 146, tb - 50), (tx_ + 108, tb - 52), (tx_ + 70, tb - 24), (tx_ + 22, tb)],
                       ("#E05A44", "#8A2018", "#2A0806"), 6, sdir=(0.3, 0.8), sk=0.2, angle=10, n=18, inkw=1.2, inkc="#100404", hi=0.35))
    out.append(hero_figure(tx_, tb + 4, 1.04, "#16141C", facing=-1, rim="#C8D8FF", arm="fwd", drape="#3A3040", stride=0.5))
    hx_, hy_ = T([(0, -119)], tx_, tb + 4, 1.04, True)[0]
    out.append(taper(catmull([(hx_ - 8, hy_ + 2), (hx_ - 4, hy_ + 14), (hx_ + 14, hy_ + 22), (hx_ + 40, hy_ + 22)], 6), 12, 2, "#D8602A"))
    out.append(taper(catmull([(hx_ - 4, hy_ - 8), (hx_ + 18, hy_ - 14), (hx_ + 42, hy_ - 8)], 6), 9, 2, "#C84A22"))
    out.append(ink(smooth_open([(hx_ - 8, hy_ + 2), (hx_ - 4, hy_ + 14), (hx_ + 14, hy_ + 22)]), "#FFB080", 1.4, 3, 1, 0.8))
    for k in range(2):
        out.append(pline([(cx_ - 46, cy_ - 72 + k * 6), (cx_ - 130, cy_ - 36 + k * 4), (cx_ - 214, cy_ - 60 + k * 6)], "#2A1A0E", 1.8, k, 0.9, 1))
    for (wx, wr) in ((cx_ - 24, 34), (cx_ + 50, 34)):
        out.append(spoked_wheel(D, wx, cy_ + 22, wr, wx, rot_=wx))
        for k in range(10):
            a = rnd.uniform(100, 250)
            out.append(pline([(wx + math.cos(math.radians(a)) * wr, cy_ + 22 + math.sin(math.radians(a)) * wr * 0.3 + 22),
                              (wx + math.cos(math.radians(a)) * wr * 1.7 + 10, cy_ + 34 + rnd.uniform(-6, 18))], "#E8F0FF", 1.4, k, 0.8, 1))
        out.append(soft_glow(D, wx, cy_ + 50, 44, "#C8D8FF", 0.5))
    # the two goats, Tanngrisnir and Tanngnjostr, leaping ahead
    out.append(goat(D, 214, 334, 1.3, 11, ("#9A8A7A", "#5A4A3E", "#1E1812"), legs_phase=0, rim="#C8D8FF"))
    out.append(goat(D, 156, 368, 1.36, 12, ("#E8E0D0", "#A89C8A", "#4A4236"), legs_phase=1, rim="#FFFFFF"))
    # lettering
    out.append(gilt(D, 300, 106, "Thor’s Goats", SERIF_IT, 66, max_w=400, seed=13, deboss="#000000", dop=0.85, pal="silver"))
    out.append(tx(300, 138, "NORSE · TANNGRISNIR & TANNGNJÓSTR", CINZEL, 16, "#E8ECFF", ls=2.5, max_w=420))
    out.append(tx(301.5, 539.5, "When it thunders, Thor is riding.", SERIF_IT, 28, "#14182A", max_w=420, op=0.7))
    out.append(tx(300, 538, "When it thunders, Thor is riding.", SERIF_IT, 28, "#FFFFFF", max_w=420))
    return fin(D, out, 26)


# ================================================================ 14. the weighing of the heart — a papyrus vignette
def anubis_figure(D, x, base, s, seed, flip=False):
    """Anubis in the Egyptian manner: black jackal head in profile with tall ears, broad shoulders, gold collar,
    white pleated kilt, striding legs. Faces right unless flip. ~150*s tall."""
    def L(pts):
        return T(pts, x, base, s, flip)
    skin = ("#4A4A5A", "#16161E", "#000000")
    out = []
    for (hip, knee, foot) in (((-6, -60), (-10, -30), (-18, 0)), ((6, -60), (14, -30), (24, 0))):
        out.append(taper(catmull(L([hip, knee, foot]), 6), 10 * s, 7 * s, skin[1]))
    for fx in (-18, 24):
        out.append(poly(L([(fx - 4, 0), (fx + 14, 0), (fx + 10, -5), (fx - 2, -6)]), skin[1]))
    kilt = L([(-14, -76), (16, -76), (24, -40), (-16, -40)])
    out.append(painted(D, kilt, ("#FFFFFF", "#F2EEE2", "#A8A08A"), seed, sk=0.15, angle=-80, n=8, inkw=1.2, inkc="#3A3020", hi=0.3))
    for k in range(5):
        a, b = L([(-10 + k * 6, -74), (-12 + k * 8, -42)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#B8B09A" stroke-width="1"/>')
    out.append(sharp(L([(-14, -78), (16, -78), (16, -72), (-14, -72)]), "#C8402A"))
    torso = L([(-12, -76), (-22, -108), (-18, -116), (20, -116), (24, -108), (14, -76)])
    out.append(painted(D, torso, skin, seed + 1, sdir=(0.6, 0.4), sk=0.2, n=10, inkw=1.2, inkc="#000000", hi=0.4))
    # broad collar in bands
    for k, c in enumerate(("#1E7A8A", "#D9A945", "#C8402A", "#D9A945")):
        r = 20 - k * 3.4
        a, b, c2 = L([(-r, -114 + k * 2.4), (0, -102 + k * 3.6), (r + 2, -114 + k * 2.4)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {b[0]:.1f} {b[1] + 4 * s:.1f} {c2[0]:.1f} {c2[1]:.1f}" stroke="{c}" stroke-width="{3.6 * s:.1f}" fill="none"/>')
    # arms reaching forward to the scale
    out.append(taper(catmull(L([(18, -110), (34, -96), (50, -100)]), 6), 8 * s, 6 * s, skin[1]))
    out.append(taper(catmull(L([(-16, -110), (10, -92), (36, -88)]), 6), 8 * s, 6 * s, skin[1]))
    for (px, py) in ((30, -96), (8, -92)):
        q = L([(px, py)])[0]
        out.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{3 * s:.1f}" fill="#D9A945"/>')
    # neck, jackal head, tripartite wig
    out.append(poly(L([(-6, -116), (-6, -128), (8, -128), (8, -116)]), skin[1]))
    wig = L([(-14, -122), (-16, -150), (-4, -158), (10, -152), (12, -128), (2, -116), (-10, -112)])
    out.append(painted(D, wig, ("#3A5A9A", "#1E2A5A", "#0A1028"), seed + 2, sk=0.15, angle=-90, n=8, inkw=1.0, inkc="#000000", hi=0.3))
    for k in range(4):
        a, b = L([(-12 + k * 6, -148), (-12 + k * 6, -118)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#D9A945" stroke-width="1.2" opacity="0.7"/>')
    head = L([(-4, -150), (6, -158), (18, -156), (40, -148), (44, -144), (38, -140), (16, -138), (6, -132), (-2, -136)])
    out.append(painted(D, head, skin, seed + 3, sdir=(0.5, 0.5), sk=0.15, n=8, inkw=1.2, inkc="#000000", hi=0.5))
    for dx in (-2, 6):
        out.append(painted(D, L([(dx, -152), (dx - 2, -180), (dx + 8, -156)]), skin, seed + 4 + dx, sk=0.1, n=3, inkw=1, inkc="#000000", hi=0.45))
    out.append(poly(L([(1, -156), (1, -172), (5, -158)]), "#C8902A"))
    ex, ey = L([(18, -150)])[0]
    out.append(f'<path d="{blob(ex, ey, 3.6 * s, 1.8 * s, seed, 0.05, 8)}" fill="#FFFFFF"/><circle cx="{ex + 0.6:.1f}" cy="{ey:.1f}" r="{1.3 * s:.1f}" fill="#000000"/>')
    out.append(pline(L([(10, -150), (16, -146), (24, -150)]), "#D9A945", 1.4 * s, seed, 0.9, 1))
    return "".join(out)


def heart_jar(D, cx, cy, s, seed):
    """The ib heart as the Egyptians drew it: a small jar-like vessel with lug handles."""
    def L(pts):
        return T(pts, cx, cy, s)
    pts = L([(-8, -16), (-12, -10), (-14, 4), (-10, 14), (0, 18), (10, 14), (14, 4), (12, -10), (8, -16)])
    out = [painted(D, pts, ("#F27A6A", "#B8282A", "#5A0A10"), seed, sdir=(0.5, 0.5), sk=0.2, n=8, inkw=1.4, inkc="#3A0408", hi=0.5)]
    out.append(sharp(L([(-9, -20), (9, -20), (8, -15), (-8, -15)]), "#5A0A10"))
    for sg in (-1, 1):
        out.append(f'<path d="{blob(*L([(sg * 15, -6)])[0], 3.4 * s, 4.6 * s, seed + sg, 0.05, 8)}" fill="#8A1A1E"/>')
    return "".join(out)


def maat_feather(D, cx, base, h, seed):
    """The ostrich feather of Ma'at: upright, curled at the tip, white with ochre shaft."""
    pts = [(cx - 2, base), (cx - 8, base - h * 0.3), (cx - 10, base - h * 0.7), (cx - 4, base - h * 0.95), (cx + 8, base - h), (cx + 14, base - h * 0.92),
           (cx + 8, base - h * 0.84), (cx + 10, base - h * 0.6), (cx + 8, base - h * 0.3), (cx + 2, base)]
    out = [painted(D, pts, ("#FFFFFF", "#F2EEE0", "#A8A08A"), seed, sk=0.15, angle=-90, n=10, inkw=1.2, inkc="#3A3020", hi=0.4)]
    out.append(pline([(cx, base), (cx - 1, base - h * 0.6), (cx + 6, base - h * 0.96)], "#C8902A", 1.6, seed, 0.9, 1))
    for k in range(9):
        y = base - h * (0.1 + k * 0.09)
        out.append(f'<path d="M {cx:.1f} {y:.1f} l -7 -6 M {cx:.1f} {y:.1f} l 7 -5" stroke="#B8B09A" stroke-width="0.9" opacity="0.7"/>')
    return "".join(out)


def glyph(kind, x, y, s, col):
    """A few hieroglyph-like signs drawn as simple shapes (decorative columns)."""
    if kind == 0:   # reed leaf
        return f'<path d="M {x:.1f} {y + 10 * s:.1f} q {-5 * s:.1f} {-10 * s:.1f} 0 {-20 * s:.1f} q {4 * s:.1f} {10 * s:.1f} 0 {20 * s:.1f} Z" fill="{col}"/>'
    if kind == 1:   # water ripple
        return f'<path d="M {x - 10 * s:.1f} {y:.1f} l 4 -3 l 4 3 l 4 -3 l 4 3 l 4 -3" stroke="{col}" stroke-width="{1.6 * s:.1f}" fill="none"/>'
    if kind == 2:   # bread loaf
        return f'<path d="M {x - 7 * s:.1f} {y + 3 * s:.1f} q {7 * s:.1f} {-12 * s:.1f} {14 * s:.1f} 0 Z" fill="{col}"/>'
    if kind == 3:   # eye
        return f'<path d="M {x - 8 * s:.1f} {y:.1f} q {8 * s:.1f} {-7 * s:.1f} {16 * s:.1f} 0 q {-8 * s:.1f} {6 * s:.1f} {-16 * s:.1f} 0 Z" fill="none" stroke="{col}" stroke-width="{1.4 * s:.1f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{2 * s:.1f}" fill="{col}"/>'
    if kind == 4:   # owl
        return (f'<path d="M {x - 5 * s:.1f} {y + 9 * s:.1f} L {x - 6 * s:.1f} {y - 2 * s:.1f} Q {x - 4 * s:.1f} {y - 10 * s:.1f} {x + 3 * s:.1f} {y - 8 * s:.1f} '
                f'L {x + 6 * s:.1f} {y + 2 * s:.1f} L {x + 4 * s:.1f} {y + 9 * s:.1f} Z" fill="{col}"/>')
    if kind == 5:   # ankh
        return (f'<path d="M {x:.1f} {y - 2 * s:.1f} m 0 0 a {3.4 * s:.1f} {4.6 * s:.1f} 0 1 1 0.1 0 M {x:.1f} {y - 2 * s:.1f} L {x:.1f} {y + 10 * s:.1f} M {x - 6 * s:.1f} {y:.1f} L {x + 6 * s:.1f} {y:.1f}" '
                f'stroke="{col}" stroke-width="{1.8 * s:.1f}" fill="none"/>')
    if kind == 6:   # sun disc
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 * s:.1f}" fill="none" stroke="{col}" stroke-width="{1.6 * s:.1f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{1.4 * s:.1f}" fill="{col}"/>'
    return f'<path d="M {x - 6 * s:.1f} {y + 4 * s:.1f} L {x:.1f} {y - 8 * s:.1f} L {x + 6 * s:.1f} {y + 4 * s:.1f}" stroke="{col}" stroke-width="{1.6 * s:.1f}" fill="none"/>'


@design("the-weighing-of-the-heart")
def the_weighing_of_the_heart():
    D = Doc2("my-wh")
    # papyrus ground: warm, fibrous, with a grid of crossed strips
    out = [sky(D, [(0, "#F2DEB0"), (1, "#E2C690")], 1, 600, ["#F6E6C0", "#C8A870", "#E8D2A0"], 90, angle=0)]
    rnd = random.Random(2)
    for k in range(0, 620, 22):
        out.append(f'<path d="M 0 {k + rnd.uniform(-2, 2):.1f} L 600 {k + rnd.uniform(-2, 2):.1f}" stroke="#B89A60" stroke-width="1.2" opacity="0.28"/>')
        out.append(f'<path d="M {k + rnd.uniform(-2, 2):.1f} 0 L {k + rnd.uniform(-2, 2):.1f} 600" stroke="#B89A60" stroke-width="0.8" opacity="0.16"/>')
    for k in range(260):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(6, 20):.1f} {rnd.uniform(-0.6, 0.6):.1f}" stroke="#A8864A" stroke-width="0.8" opacity="{rnd.uniform(0.1, 0.3):.2f}"/>')
    # border bands, top and bottom
    for (y0, flipb) in ((20, False), (560, True)):
        for k, c in enumerate(("#1E3A8A", "#D9A945", "#C8402A", "#1E7A8A")):
            out.append(f'<rect x="0" y="{y0 + k * 5:.1f}" width="600" height="5" fill="{c}"/>')
        for k in range(30):
            out.append(f'<rect x="{k * 20 + 4}" y="{y0 + (22 if not flipb else -14)}" width="12" height="10" fill="{("#1E3A8A", "#C8402A", "#1E7A8A")[k % 3]}"/>')
    # columns of signs across the top register, as on a Book of the Dead papyrus
    for c in range(12):
        x = 78 + c * 40
        for r in range(3):
            out.append(glyph((c * 3 + r * 5) % 8, x, 66 + r * 22, 1.0, "#2A1A0A"))
        out.append(f'<path d="M {x + 20} 52 L {x + 20} 122" stroke="#2A1A0A" stroke-width="1.2" opacity="0.6"/>')
    out.append(f'<path d="M 60 128 L 540 128" stroke="#2A1A0A" stroke-width="2"/>')
    # the great balance
    bx, btop, bbase = 330, 196, 452
    out.append(painted(D, poly_pts([(bx - 30, bbase), (bx + 30, bbase), (bx + 22, bbase - 18), (bx - 22, bbase - 18)], 10, 1, 0.3), GOLD, 3, sk=0.2, n=6, inkw=1.4, inkc="#4A2A06", hi=0.5))
    out.append(painted(D, poly_pts([(bx - 6, bbase - 18), (bx + 6, bbase - 18), (bx + 5, btop), (bx - 5, btop)], 14, 2, 0.3), ("#6AC8D0", "#1E7A8A", "#0A3A44"), 4, sk=0.2, angle=-90, n=8, inkw=1.4, inkc="#0A1A1A", hi=0.4))
    for k in range(5):
        out.append(f'<rect x="{bx - 7}" y="{bbase - 60 - k * 40}" width="14" height="5" fill="#D9A945"/>')
    tilt = 0
    beam = [(bx - 120, btop + tilt), (bx + 120, btop - tilt)]
    out.append(taper(beam, 7, 7, "#8A6020"))
    out.append(taper([(beam[0][0], beam[0][1] - 2), (beam[1][0], beam[1][1] - 2)], 2, 2, "#FBE7A4", 0.8))
    for sg in (-1, 1):
        ex = bx + sg * 116
        out.append(f'<path d="{blob(ex, btop, 6, 4, sg + 5, 0.05, 8)}" fill="#D9A945"/>')
        for dd in (-26, 0, 26):
            out.append(f'<path d="M {ex:.1f} {btop:.1f} L {ex + dd:.1f} {btop + 108:.1f}" stroke="#4A2A06" stroke-width="1.4"/>')
        out.append(painted(D, [(ex - 36, btop + 108), (ex + 36, btop + 108), (ex + 26, btop + 120), (ex - 26, btop + 120)], GOLD, 5 + sg, sk=0.2, n=6, inkw=1.4, inkc="#4A2A06", hi=0.5))
    # the heart in the left pan, the feather of truth in the right — perfectly balanced
    out.append(heart_jar(D, bx - 116, btop + 90, 1.1, 7))
    out.append(maat_feather(D, bx + 116, btop + 106, 70, 8))
    # the plumb bob hanging true
    out.append(f'<path d="M {bx:.1f} {btop + 6:.1f} L {bx:.1f} {btop + 40:.1f}" stroke="#4A2A06" stroke-width="1.2"/>')
    out.append(sharp([(bx - 6, btop + 40), (bx + 6, btop + 40), (bx, btop + 52)], "#C8402A"))
    # the sun disc with the ankh above the balance, giver of life
    out.append(f'<circle cx="{bx}" cy="{btop - 30}" r="16" fill="#C8402A" stroke="#4A1A0A" stroke-width="1.6"/>')
    out.append(f'<circle cx="{bx}" cy="{btop - 30}" r="16" fill="none" stroke="#D9A945" stroke-width="1.4" opacity="0.8"/>')
    out.append(f'<path d="M {bx} {btop - 14} L {bx} {btop - 4}" stroke="#4A2A06" stroke-width="2"/>')
    # Anubis at the scale, steadying the plummet
    out.append(anubis_figure(D, 124, 452, 1.42, 9))
    # ground line
    out.append(f'<path d="M 60 454 L 540 454" stroke="#2A1A0A" stroke-width="2.4"/>')
    # lettering
    out.append(multi(300, 498, [("The Weighing of the Heart", "#2A1A0A")], DMS, 44, max_w=450, shadow="#FFF6E0", sdy=1.5))
    out.append(tx(300, 528, "EGYPTIAN · LIGHT AS THE FEATHER OF MA’AT", CINZEL, 16, "#8A2A1A", ls=2, max_w=430))
    return fin(D, out, 27, "#3A2418", 0.6)


# ================================================================ 15. bastet — the bronze cat in the temple at sunset
def bronze_cat(D, cx, base, s, seed):
    """A seated cat statue in the Egyptian manner (facing left): tall and slender, ears up, gold earring and nose
    ring, a silver pectoral with the Eye of Horus; patinated bronze lit gold by the sunset."""
    def L(pts):
        return T(pts, cx, base, s)
    out = []
    body = L([(-36, 0), (-34, -40), (-31, -80), (-34, -104), (-30, -128), (-27, -144), (-36, -150), (-44, -158), (-45, -165), (-38, -175), (-33, -184),
              (-31, -199), (-28, -214), (-21, -197), (-13, -193), (-7, -207), (-2, -212), (2, -190), (4, -172), (2, -156), (5, -140), (16, -112),
              (32, -80), (45, -44), (48, -14), (44, 0)])
    out.append(painted(D, body, ("#7AA090", "#3A5A4E", "#10221C"), seed, sdir=(0.7, 0.4), sk=0.22, angle=-90, n=60, inkw=1.6, inkc="#06120E", hi=0.0))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    pat = [f'<path d="{blob(*L([(rnd.uniform(-30, 40), rnd.uniform(-190, -4))])[0], rnd.uniform(4, 10) * s, rnd.uniform(3, 7) * s, k, 0.2, 10)}" fill="{rnd.choice(["#9AC8B0", "#2A4038", "#B8D8C0"])}" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>' for k in range(34)]
    pat.append(f'<path d="{smooth_closed(body)}" fill="{D.lin([(0, "#FFB060", 0.55), (0.45, "#FFB060", 0)], 0, 0, 1, 0)}"/>')
    # the front leg and the haunch modelled
    pat.append(taper(L([(-24, -100), (-25, -50), (-24, 0)]), 3 * s, 3 * s, "#10221C", 0.5))
    pat.append(f'<path d="{smooth_open(L([(-4, -96), (24, -78), (38, -40), (30, -6)]))}" stroke="#10221C" stroke-width="{2.4 * s:.1f}" fill="none" opacity="0.45"/>')
    pat.append(f'<path d="{smooth_open(L([(-6, -92), (20, -76), (32, -40)]))}" stroke="#B8E0C8" stroke-width="{1.6 * s:.1f}" fill="none" opacity="0.4"/>')
    out.append(f'<g {cid}>{"".join(pat)}</g>')
    out.append(ink(smooth_open(L([(-38, -175), (-45, -165), (-44, -158), (-36, -150), (-27, -144), (-30, -128), (-34, -104), (-31, -80), (-34, -40), (-36, 0)])), "#FFC870", 3, seed, 1, 0.85))
    out.append(ink(smooth_open(L([(-31, -199), (-28, -214), (-21, -197)])), "#FFC870", 2.2, seed + 1, 1, 0.8))
    # inner ears, eye, nose ring, earring
    out.append(poly(L([(-29, -198), (-28, -208), (-24, -197)]), "#C8902A", 0.8))
    out.append(poly(L([(-5, -196), (-3, -206), (-1, -194)]), "#C8902A", 0.8))
    ex, ey = L([(-32, -172)])[0]
    out.append(f'<path d="{blob(ex, ey, 4.2 * s, 2.2 * s, seed, 0.05, 8, -12)}" fill="#F2D06A"/><path d="M {ex - 1:.1f} {ey - 2 * s:.1f} l 0 {4 * s:.1f}" stroke="#06120E" stroke-width="{1.4 * s:.1f}"/>')
    rx, ry = L([(-43, -160)])[0]
    out.append(f'<circle cx="{rx:.1f}" cy="{ry + 3 * s:.1f}" r="{2.6 * s:.1f}" fill="none" stroke="#F2C84A" stroke-width="{1.4 * s:.1f}"/>')
    ex2, ey2 = L([(-14, -178)])[0]
    out.append(f'<circle cx="{ex2:.1f}" cy="{ey2 + 8 * s:.1f}" r="{4.4 * s:.1f}" fill="none" stroke="#F2C84A" stroke-width="{1.8 * s:.1f}"/>')
    # broad collar and pectoral
    for k, c in enumerate(("#F2C84A", "#1E8A8A", "#F2C84A")):
        a, b = L([(-30, -146 + k * 4), (4, -150 + k * 4)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {(a[0] + b[0]) / 2:.1f} {a[1] + 10 * s:.1f} {b[0]:.1f} {b[1]:.1f}" stroke="{c}" stroke-width="{2.6 * s:.1f}" fill="none"/>')
    px, py = L([(-18, -122)])[0]
    out.append(f'<path d="{blob(px, py, 10 * s, 8 * s, seed + 3, 0.05, 10)}" fill="#E8E0D0" stroke="#F2C84A" stroke-width="{1.6 * s:.1f}"/>')
    out.append(wedjat(px - 1 * s, py - 1 * s, 0.24 * s, "#1E3A8A"))
    # tail curled round the front paws
    out.append(taper(catmull(L([(44, -6), (20, 4), (-12, 6), (-38, 2), (-46, -8)]), 6), 10 * s, 5 * s, "#2A4A40"))
    out.append(taper(catmull(L([(44, -8), (20, 1), (-12, 3), (-38, -1)]), 6), 3 * s, 2 * s, "#FFC870", 0.5))
    return "".join(out)


@design("bastet")
def bastet():
    D = Doc2("my-ba")
    out = [sky(D, [(0, "#3A1E3A"), (0.45, "#C8603A"), (0.7, "#F2A85A"), (1, "#F6D08A")], 1, 600, ["#E8884A", "#5A2A3A", "#F6C07A"], 60)]
    out.append(soft_glow(D, 300, 330, 220, "#FFE0A0", 0.7))
    out.append(f'<circle cx="300" cy="340" r="54" fill="#FFF0C0" opacity="0.9"/>')
    # the Nile and palms seen between the columns
    out.append(sea(D, 380, 470, [(0, "#F2B870"), (1, "#8A4A3A")], 3, ["#FFE0A0", "#6A2A2A"], 30))
    for k in range(12):
        out.append(taper([(240 + k * 10, 386 + k * 6), (300, 384 + k * 6), (360 - k * 10, 386 + k * 6)], 1, 2.4, "#FFE8B0", 0.5))
    from summer_gouache import palm
    for (px, ph, sd) in ((214, 130, 1), (248, 96, 2), (396, 118, 3)):
        out.append(palm(D, (px, 392), (px + 8, 392 - ph), sd, L=56, width=7, sil="#3A1A1E", leaf_cols=["#3A1A1E", "#4A2228", "#2A1014"], nuts=False))
    # temple: two great columns with papyrus capitals framing the view, lintel above
    for (x0, x1, sd) in ((60, 170, 1), (430, 540, 2)):
        col_ = poly_pts([(x0, 620), (x0 + 6, 160), (x1 - 6, 160), (x1, 620)], 20, sd, 0.4)
        out.append(painted(D, col_, ("#F2C890", "#B8865A", "#4A2A1A"), sd, sdir=(0.6 if sd == 1 else -0.6, 0.2), sk=0.25, angle=-90, n=50, inkw=1.6, inkc="#2A1408", hi=0.35))
        for k in range(6):
            y = 220 + k * 64
            out.append(f'<path d="M {x0 + 4:.1f} {y} L {x1 - 4:.1f} {y}" stroke="#2A1408" stroke-width="1.4" opacity="0.5"/>')
            for j in range(3):
                out.append(glyph((k + j + sd) % 8, x0 + 26 + j * 30, y + 30, 1.1, "#3A1A0A"))
        cap = [(x0 - 20, 160), (x1 + 20, 160), (x1 + 4, 120), (x0 - 4, 120)]
        out.append(painted(D, poly_pts(cap, 14, sd + 4, 0.4), ("#8AC8A0", "#3A7A5A", "#16382A"), sd + 4, sk=0.2, angle=-90, n=14, inkw=1.4, inkc="#0A1A10", hi=0.4))
        for k in range(7):
            xx = x0 - 14 + k * (x1 - x0 + 28) / 6
            out.append(f'<path d="M {xx:.1f} 158 L {(x0 + x1) / 2 + (xx - (x0 + x1) / 2) * 0.7:.1f} 122" stroke="#16382A" stroke-width="1.4"/>')
    lint = poly_pts([(-10, 30), (610, 30), (610, 122), (-10, 122)], 30, 7, 0.4)
    out.append(painted(D, lint, ("#F2C890", "#B8865A", "#4A2A1A"), 7, sdir=(0, 0.8), sk=0.2, angle=0, n=40, inkw=1.6, inkc="#2A1408", hi=0.3))
    # the winged sun disc carved on the lintel
    out.append(f'<circle cx="300" cy="84" r="12" fill="#C8402A" stroke="#2A1408" stroke-width="1.4"/>')
    for sg in (-1, 1):
        for k in range(4):
            out.append(taper([(300 + sg * 14, 80 + k * 4), (300 + sg * (60 + k * 6), 76 + k * 6), (300 + sg * (110 - k * 10), 74 + k * 7)], 5 - k * 0.6, 1.4, ("#1E3A8A", "#1E7A8A", "#D9A945", "#1E3A8A")[k]))
    # plinth and the statue
    pl = poly_pts([(206, 470), (394, 470), (394, 410), (206, 410)], 16, 9, 0.4)
    out.append(cast(D, 330, 470, 160, 20, "#2A0A0A", 0.5, 3))
    out.append(painted(D, pl, ("#F2D8A8", "#C89A68", "#5A3A20"), 9, sdir=(0.6, 0.3), sk=0.2, angle=0, n=20, inkw=1.6, inkc="#2A1408", hi=0.35))
    for k in range(5):
        out.append(glyph((k * 3) % 8, 236 + k * 32, 440, 1.0, "#5A2A10"))
    out.append(bronze_cat(D, 296, 412, 1.32, 10))
    # lotus offerings at the foot of the plinth
    for (lx, ly) in ((196, 480), (404, 482)):
        for k in range(5):
            a = math.radians(-150 + k * 30)
            out.append(f'<path d="{blob(lx + math.cos(a) * 9, ly - 6 + math.sin(a) * 9, 8, 3.4, k, 0.05, 8, math.degrees(a))}" fill="{("#F2A0C0", "#FFFFFF")[k % 2]}"/>')
    # floor
    out.append(painted(D, poly_pts([(-10, 470), (610, 470), (610, 620), (-10, 620)], 30, 12, 0.4), ("#8A5A3A", "#5A3420", "#1E0E08"), 12, sdir=(0, 1), sk=0.1, angle=0, n=40, inkw=0, hi=0.2))
    # lettering
    out.append(gilt(D, 300, 518, "BASTET", CINZEL, 54, ls=14, max_w=380, seed=13, deboss="#000000", dop=0.85))
    out.append(tx(300, 542, "EGYPTIAN · GUARDIAN OF HOME AND HEARTH", CINZEL, 15, "#F6E2C0", ls=2, max_w=420))
    return fin(D, out, 28)


# ================================================================ 16. the sphinx — guardian of the horizon at sunrise
def great_sphinx(D, cx, base, s, seed):
    """The Great Sphinx in profile (facing left): long recumbent lion body with strata of weathered limestone,
    forepaws stretched out, the nemes headdress with its lappet, a calm weathered face. (cx, base) = ground under the chest."""
    def L(pts):
        return T(pts, cx, base, s)
    lime = ("#F8DCA8", "#CC9E64", "#6A4424")
    out = [cast(D, cx + 80 * s, base + 4, 220 * s, 12 * s, "#4A2A1A", 0.45, seed)]
    body = L([(-176, 0), (-178, -20), (-90, -24), (-80, -40), (-74, -78), (-60, -98), (-20, -104), (40, -98), (100, -96), (150, -100), (186, -88),
              (204, -60), (208, -24), (204, 0)])
    out.append(painted(D, body, lime, seed, sdir=(-0.6, 0.5), sk=0.18, angle=-4, n=60, inkw=1.8, inkc="#3A2010", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    strata = []
    rnd = random.Random(seed)
    for k in range(9):
        y = -8 - k * 11
        pts_ = [(x_, y + rnd.uniform(-2, 2)) for x_ in range(-180, 220, 30)]
        strata.append(f'<path d="{smooth_open(L(pts_))}" stroke="#8A5A30" stroke-width="{2 * s:.1f}" fill="none" opacity="0.4"/>')
        strata.append(f'<path d="{smooth_open(L([(x_, y_ - 3) for x_, y_ in pts_]))}" stroke="#FFF0C8" stroke-width="{1.2 * s:.1f}" fill="none" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(strata)}</g>')
    out.append(pline(L([(150, -100), (176, -60), (170, -20), (180, -4)]), lime[2], 2.2, seed, 0.6, 1))
    out.append(pline(L([(-90, -24), (-60, -20), (-30, -8)]), lime[2], 2, seed, 0.6, 1))
    # nemes headdress: wide headcloth flaring to the shoulders, striped, with the lappet in front
    nem = L([(-66, -128), (-62, -158), (-48, -176), (-24, -182), (-4, -172), (6, -150), (14, -116), (22, -96), (-10, -96), (-32, -104), (-44, -110)])
    out.append(painted(D, nem, lime, seed + 2, sdir=(-0.5, 0.5), sk=0.2, angle=-90, n=30, inkw=1.6, inkc="#3A2010", hi=0.45))
    cid2 = D.clip(f'<path d="{smooth_closed(nem)}"/>')
    st = []
    for k in range(12):
        a_, b_ = L([(-60 + k * 7, -186), (-50 + k * 7, -90)])
        st.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#8A5A30" stroke-width="{2.4 * s:.1f}" opacity="0.35"/>')
    out.append(f'<g {cid2}>{"".join(st)}</g>')
    lap = L([(-60, -128), (-48, -128), (-48, -80), (-62, -76)])
    out.append(painted(D, lap, lime, seed + 5, sdir=(-0.5, 0.3), sk=0.25, angle=-90, n=6, inkw=1.4, inkc="#3A2010", hi=0.4))
    for k in range(5):
        a_, b_ = L([(-61, -120 + k * 9), (-48, -120 + k * 9)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#8A5A30" stroke-width="{1.6 * s:.1f}" opacity="0.5"/>')
    # the face in profile, under the headcloth band
    face = L([(-62, -160), (-70, -156), (-72, -148), (-80, -140), (-76, -134), (-78, -128), (-74, -122), (-74, -116), (-66, -110), (-56, -112), (-54, -132), (-56, -156)])
    out.append(painted(D, face, lime, seed + 3, sdir=(-0.6, 0.4), sk=0.2, n=10, inkw=1.6, inkc="#3A2010", hi=0.55))
    out.append(taper(L([(-66, -162), (-58, -162), (-50, -160)]), 4 * s, 4 * s, "#B8864A"))
    out.append(pline(L([(-70, -146), (-62, -146)]), "#3A2010", 2.2, seed, 0.8, 1))
    out.append(pline(L([(-72, -147), (-66, -149)]), "#3A2010", 1.4, seed, 0.6, 1))
    out.append(pline(L([(-76, -126), (-70, -126)]), "#3A2010", 1.4, seed, 0.6, 1))
    out.append(ink(smooth_open(L([(-62, -158), (-48, -176), (-24, -182), (-4, -172)])), "#FFEAB8", 2.6, seed + 4, 1, 0.8))
    out.append(ink(smooth_open(L([(-72, -148), (-80, -140), (-76, -134), (-78, -128)])), "#FFF2C8", 2, seed + 6, 1, 0.8))
    return "".join(out)


def pyramid(D, cx, base, w, h, seed, lit=("#F6C890", "#E0A060", "#A8683A"), shade=("#B87A50", "#8A5434", "#4A2A18")):
    out = [painted(D, [(cx - w / 2, base), (cx, base - h), (cx, base)], lit, seed, sk=0.05, angle=-60, n=24, inkw=0, hi=0.2)]
    out.append(painted(D, [(cx, base), (cx, base - h), (cx + w / 2, base)], shade, seed + 1, sk=0.05, angle=-120, n=24, inkw=0, hi=0.1))
    for k in range(1, 12):
        y = base - h * k / 12
        hw = w / 2 * (1 - k / 12)
        out.append(f'<path d="M {cx - hw:.1f} {y:.1f} L {cx + hw:.1f} {y:.1f}" stroke="#6A3A1A" stroke-width="0.9" opacity="0.3"/>')
    return "".join(out)


@design("the-sphinx")
def the_sphinx():
    D = Doc2("my-sx")
    out = [sky(D, [(0, "#4A5A8A"), (0.4, "#C88A9A"), (0.62, "#F6B87A"), (0.75, "#FCE2A0")], 1, 460, ["#8A7A9A", "#FFD8A0", "#E8A08A"], 60)]
    # the sun rising on the horizon, between the pyramids
    sx, sy = 112, 340
    out.append(soft_glow(D, sx, sy, 230, "#FFE8A0", 0.75))
    out.append(ray_fan(sx, sy, 50, 420, 30, "#FFF2C8", 0.12, a0=180, a1=360, seed=3))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="46" fill="#FFF6D0"/>')
    # pyramids
    out.append(pyramid(D, 450, 396, 300, 210, 4))
    out.append(pyramid(D, 590, 400, 200, 150, 5))
    out.append(pyramid(D, 330, 400, 130, 84, 6))
    # desert
    d1 = ridge([(-20, 396), (120, 390), (300, 400), (460, 392), (620, 398)], 7, 6)
    out.append(hill(D, d1, 620, ("#F6D8A0", "#E0B070", "#A8703A"), 7, inkw=0, lit="#FFF2C8"))
    d2 = [(-20, 470), (160, 452), (330, 468), (480, 456), (620, 470)]
    out.append(hill(D, d2, 620, ("#F2C890", "#D8A060", "#8A5A2A"), 8, inkw=1.2, inkc="#6A3A1A"))
    rnd = random.Random(8)
    for k in range(20):
        x = rnd.uniform(0, 600)
        y = rnd.uniform(470, 600)
        out.append(taper([(x - 20, y), (x, y - 2), (x + 20, y)], 0.6, 2, "#A8703A", 0.4))
    # the Sphinx, lit gold on its sun-facing side
    out.append(great_sphinx(D, 356, 500, 1.86, 9))
    # a caravan of camels far off on the dune line, against the sunrise
    for k in range(4):
        x = 40 + k * 24
        out.append(poly([(x, 404), (x + 4, 396), (x + 10, 394), (x + 14, 398), (x + 18, 392), (x + 22, 394), (x + 20, 404)], "#5A2A2A"))
        for dx in (2, 8, 14, 20):
            out.append(f'<path d="M {x + dx} 403 l 0 8" stroke="#5A2A2A" stroke-width="1.6"/>')
    # lettering
    out.append(gilt(D, 300, 110, "The Sphinx", SERIF_IT, 70, max_w=420, seed=11, deboss="#2A1A3A", dop=0.7))
    out.append(tx(300, 142, "EGYPTIAN · GUARDIAN OF THE HORIZON", CINZEL, 16, "#FFFFFF", ls=3, max_w=420))
    out.append(tx(300, 536, "He has watched the sun rise for 4,500 years.", SERIF_IT, 23, "#5A2A14", max_w=440))
    return fin(D, out, 29)


# ================================================================ 17. the phoenix — reborn from its own ashes
def feather_fan(D, pivot, angles, lengths, width, pals, seed, eye=None):
    """A row of long painted feathers radiating from a pivot (for wings and tails)."""
    out = []
    for k, (a, L_) in enumerate(zip(angles, lengths)):
        ar = math.radians(a)
        ux, uy = math.cos(ar), math.sin(ar)
        nx, ny = -uy, ux
        pts = []
        for i in range(9):
            t = i / 8
            w = width * math.sin(math.pi * min(1, t * 1.05)) ** 0.6 * (0.5 + 0.5 * t)
            pts.append((pivot[0] + ux * L_ * t + nx * w, pivot[1] + uy * L_ * t + ny * w))
        for i in range(8, -1, -1):
            t = i / 8
            w = width * 0.8 * math.sin(math.pi * min(1, t * 1.05)) ** 0.6 * (0.5 + 0.5 * t)
            pts.append((pivot[0] + ux * L_ * t - nx * w, pivot[1] + uy * L_ * t - ny * w))
        pal = pals[k % len(pals)]
        out.append(painted(D, pts, pal, seed + k, sk=0.15, angle=a, n=6, inkw=1.0, inkc="#4A0A04", hi=0.4))
        out.append(pline([pivot, (pivot[0] + ux * L_ * 0.92, pivot[1] + uy * L_ * 0.92)], pal[2], 1.1, seed + k, 0.6, 1))
        if eye:
            ex, ey = pivot[0] + ux * L_ * 0.85, pivot[1] + uy * L_ * 0.85
            out.append(f'<path d="{blob(ex, ey, width * 0.55, width * 0.4, seed + k, 0.05, 10, a)}" fill="{eye[0]}"/>')
            out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{width * 0.22:.1f}" fill="{eye[1]}"/>')
    return "".join(out)


@design("the-phoenix")
def the_phoenix():
    D = Doc2("my-ph")
    out = [sky(D, [(0, "#1A0A24"), (0.4, "#5A1A3A"), (0.75, "#C8402A"), (1, "#F28A3A")], 1, 600, ["#7A2A4A", "#1A0A24", "#E8603A"], 70)]
    cx, cy = 300, 336
    out.append(soft_glow(D, cx, cy, 320, "#FFB040", 0.6))
    out.append(ray_fan(cx, cy, 60, 460, 40, "#FFE08A", 0.12, seed=4))
    out.append(f'<circle cx="{cx}" cy="{cy - 10}" r="120" fill="#FFD070" opacity="0.25"/>')
    # the palm-top nest of cinnamon and myrrh, burning
    nx_, ny_ = 300, 478
    out.append(taper(catmull([(nx_ - 10, 640), (nx_ - 4, 560), (nx_, ny_ + 10)], 6), 26, 18, "#3A1A10"))
    for k in range(9):
        out.append(f'<path d="M {nx_ - 12:.1f} {ny_ + 30 + k * 14:.1f} l 24 -4" stroke="#1A0A06" stroke-width="2" opacity="0.6"/>')
    for k in range(9):
        a = math.radians(-180 + k * 22.5)
        out.append(taper(catmull([(nx_, ny_ + 16), (nx_ + math.cos(a) * 64, ny_ + 8 + math.sin(a) * 14), (nx_ + math.cos(a) * 112, ny_ + 24)], 6), 10, 1.5, "#2A1A10"))
    rnd = random.Random(5)
    for k in range(26):
        x0_ = nx_ + rnd.uniform(-70, 70)
        out.append(taper([(x0_ - 14, ny_ + rnd.uniform(-6, 10)), (x0_ + 14, ny_ + rnd.uniform(-6, 10))], 5, 5, rnd.choice(["#8A4A1E", "#C8783A", "#5A2A10"])))
    for k in range(5):
        out.append(flame(D, nx_ - 60 + k * 30, ny_ - 2, rnd.uniform(40, 70), 10 + k, lean=rnd.uniform(-0.2, 0.2)))
    # the bird rising: wings spread high, tail of flame-feathers streaming down
    fire = [("#FFE680", "#F69020", "#A8300A"), ("#FFC070", "#EE5A22", "#7A1206"), ("#FF9A88", "#D0242A", "#5A0610")]
    out.append(feather_fan(D, (cx, cy + 40), [92 + k * 9 for k in range(-4, 5)], [160 - abs(k) * 12 for k in range(-4, 5)], 13, fire, 20, eye=("#7A2A9A", "#FFE070")))
    for sg in (-1, 1):
        def mir(a_):
            return a_ if sg > 0 else 180 - a_
        sh, el, wr = (cx + sg * 18, cy - 16), (cx + sg * 80, cy - 70), (cx + sg * 130, cy - 124)
        arm = catmull([sh, el, wr], 8)
        # flight feathers: secondaries hanging along the arm, primaries fanning from the wrist
        for i in range(len(arm) - 1, 0, -1):
            t = i / (len(arm) - 1)
            out.append(feather_fan(D, arm[i], [mir(40 - 30 * t)], [104 - 14 * t], 19, fire, 30 + i + sg * 40))
        out.append(feather_fan(D, wr, [mir(a_) for a_ in (2, -10, -22, -34, -46, -58, -70)], [96, 106, 112, 114, 110, 100, 88], 17, fire, 60 + sg * 10))
        # the wing's covert area and two rows of small coverts on top
        cov = arm + [(x_ + 26 * math.cos(math.radians(mir(40))), y_ + 26 * math.sin(math.radians(mir(40)))) for x_, y_ in arm[::-1]]
        out.append(painted(D, cov, ("#FFF2B0", "#F6B030", "#B8500A"), 70 + sg, sk=0.15, angle=mir(-40), n=14, inkw=1.2, inkc="#6A1A04", hi=0.5))
        for row, (off, L_) in enumerate(((6, 44), (2, 30))):
            for i in range(1, len(arm), 2):
                t = i / (len(arm) - 1)
                p = arm[i]
                out.append(feather_fan(D, (p[0], p[1] + off), [mir(40 - 26 * t)], [L_], 12, [("#FFF6C0", "#FFC84A", "#C8701A"), ("#FFE8A0", "#F6A030", "#A8400A")], 80 + i + row * 20 + sg * 30))
        out.append(ink(smooth_open(arm), "#FFF6C8", 2.4, 3 + sg, 1, 0.8))
    body = [(cx - 22, cy - 30), (cx - 26, cy + 10), (cx - 12, cy + 50), (cx, cy + 58), (cx + 12, cy + 50), (cx + 26, cy + 10), (cx + 22, cy - 30), (cx, cy - 40)]
    out.append(painted(D, body, ("#FFE8A0", "#F2902A", "#A8300A"), 60, sdir=(0.4, 0.6), sk=0.2, angle=-90, n=16, inkw=1.4, inkc="#4A0A04", hi=0.5))
    out.append(bird_feathers(D, body, ["#B8400A", "#FFF2B0"], 61, n=40, size=(3, 6), angle=90, op=(0.3, 0.6)))
    # neck and head lifted in profile, crest of flame plumes
    neck = [(cx - 14, cy - 34), (cx - 10, cy - 70), (cx - 2, cy - 92), (cx + 14, cy - 100), (cx + 22, cy - 92), (cx + 14, cy - 76), (cx + 14, cy - 34)]
    out.append(painted(D, neck, ("#FFE8A0", "#F2902A", "#A8300A"), 62, sdir=(0.4, 0.6), sk=0.15, n=10, inkw=1.4, inkc="#4A0A04", hi=0.5))
    out.append(sharp([(cx + 20, cy - 98), (cx + 40, cy - 92), (cx + 20, cy - 88)], "#F2C84A"))
    out.append(f'<circle cx="{cx + 10:.1f}" cy="{cy - 94:.1f}" r="3" fill="#2A0A04"/><circle cx="{cx + 10.8:.1f}" cy="{cy - 95:.1f}" r="1.1" fill="#FFFFFF"/>')
    for k in range(5):
        a = math.radians(-150 + k * 16)
        out.append(taper(catmull([(cx + 2, cy - 100), (cx + 2 + math.cos(a) * 20, cy - 104 + math.sin(a) * 20), (cx - 6 + math.cos(a) * 36, cy - 104 + math.sin(a) * 34)], 6), 4, 1, ("#FFE070", "#F2702A")[k % 2]))
        ex = cx - 6 + math.cos(a) * 36
        ey = cy - 104 + math.sin(a) * 34
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3" fill="#FFF2A0"/>')
    # rising sparks
    for k in range(50):
        x, y = rnd.uniform(80, 520), rnd.uniform(140, 480)
        out.append(sparkle(x, y, rnd.uniform(1.2, 3.6), rnd.choice(["#FFE070", "#FFFFFF", "#FFA040"]), rnd.uniform(0.5, 1)))
    # lettering
    out.append(gilt(D, 300, 100, "THE PHOENIX", CINZEL, 52, ls=10, max_w=420, seed=12, deboss="#1A0408", dop=0.85))
    out.append(tx(301.5, 537.5, "GREEK & EGYPTIAN · REBORN FROM ITS OWN ASHES", CINZEL, 16, "#3A0A10", ls=2, max_w=440, op=0.6))
    out.append(tx(300, 536, "GREEK & EGYPTIAN · REBORN FROM ITS OWN ASHES", CINZEL, 16, "#FFF2D8", ls=2, max_w=440))
    return fin(D, out, 30)


# ================================================================ 18. romulus and remus — the she-wolf of the Tiber
def canine(D, x, y, s, seed, pal, flip=False, kind="wolf", rim=None, tails=1, head_drop=0, tail_pose="down"):
    """A wolf or fox standing in side view (facing left unless flip). (x, y) = ground under the body.
    kind 'fox' gives a slimmer build, larger ears and a white-tipped brush; tails > 1 fans extra tails."""
    def L(pts):
        return T(pts, x, y, s, flip)
    fox = kind == "fox"
    k_ = 0.82 if fox else 1.0
    out = []
    lw = (10, 4.6) if fox else (14, 6.4)
    # far legs (darker)
    for pts in (((-44, -56), (-44, -36), (-46, -12), (-42, 0)), ((50, -64), (40, -36), (56, -16), (50, 0))):
        out.append(taper(catmull(L([(px, py * k_ if py < -20 else py) for px, py in pts]), 6), lw[0] * s * 0.9, lw[1] * s, dk(pal[1], 0.3)))
    # tail(s)
    for t in range(tails):
        spread = (t - (tails - 1) / 2) * 16
        if fox:
            tp = [(66, -74 * k_), (96, -80 * k_ - spread * 0.4), (122 + abs(spread) * 0.2, -64 * k_ - spread * 1.1), (134, -34 * k_ - spread * 1.8)]
        elif tail_pose == "down":
            tp = [(66, -74), (84, -62), (92, -40), (88, -20)]
        else:
            tp = [(66, -74), (90, -82), (110, -72), (120, -56)]
        tpath = catmull(L(tp), 8)
        out.append(taper(tpath, (20 if fox else 16) * s, (12 if fox else 5) * s, pal[1]))
        out.append(taper([(px - 1, py - 2) for px, py in tpath], 6 * s, 3 * s, pal[0], 0.5))
        out.append(taper([(px + 1, py + 2) for px, py in tpath], 5 * s, 2 * s, pal[2], 0.4))
        if fox:
            ex, ey = tpath[-1]
            out.append(f'<path d="{blob(ex, ey, 10 * s, 8 * s, seed + t, 0.12, 10)}" fill="#FFFDF4"/>')
    hd = head_drop
    body = [(-70, -64), (-66, -54), (-54, -48), (-30, -50), (0, -56), (26, -60), (46, -58), (66, -54), (74, -62), (72, -76), (64, -82), (30, -84), (-24, -92), (-48, -100)]
    head = [(-60, -112), (-66, -118), (-72, -134 - (8 if fox else 0)), (-78, -118), (-90, -110), (-98, -102), (-112, -96), (-116, -92), (-112, -88), (-98, -84), (-86, -80), (-76, -70)]
    head = [(px, py * k_ + hd * (-(px + 60) / 50)) for px, py in head]
    body = [(px, py * k_) for px, py in body]
    outline = L(body + head)
    out.append(painted(D, outline, pal, seed, sdir=(0.3 if not flip else -0.3, 0.8), sk=0.2, angle=-8 if not flip else 188, n=40, inkw=1.4, inkc="#140C06", hi=0.45))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(outline)}"/>')
    fur = []
    for k in range(50):
        px, py = L([(rnd.uniform(-80, 66), rnd.uniform(-96, -54) * k_)])[0]
        fur.append(f'<path d="M {px:.1f} {py:.1f} l {(3 if not flip else -3) * s:.1f} {5 * s:.1f}" stroke="{rnd.choice([pal[0], pal[2]])}" stroke-width="{1.3 * s:.1f}" stroke-linecap="round" opacity="0.55"/>')
    # neck ruff and darker saddle
    fur.append(f'<path d="{smooth_closed(L([(-20, -92 * k_), (30, -86 * k_), (60, -80 * k_), (20, -70 * k_), (-20, -76 * k_)]))}" fill="{pal[2]}" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(fur)}</g>')
    for k in range(6):
        a_, b_ = L([(-58 + k * 4, -70 * k_ - k * 5), (-66 + k * 4, -60 * k_ - k * 5)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{pal[0]}" stroke-width="{1.6 * s:.1f}" stroke-linecap="round" opacity="0.7"/>')
    # pale muzzle and throat
    hp = lambda pts: L([(px, py * k_ + hd * (-(px + 60) / 50)) for px, py in pts])
    out.append(poly(hp([(-112, -90), (-98, -85), (-84, -80), (-72, -70), (-66, -58), (-76, -76), (-92, -92), (-104, -96)]), "#F6EEE0", 0.85))
    ex, ey = hp([(-88, -104)])[0]
    out.append(f'<path d="{blob(ex, ey, 3.2 * s, 1.8 * s, seed, 0.05, 8, 10 if not flip else -10)}" fill="#F2C84A"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.3 * s:.1f}" fill="#1A0A04"/>')
    nx_, ny_ = hp([(-114, -93)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{2.8 * s:.1f}" fill="#1A1008"/>')
    out.append(poly(hp([(-68, -118), (-72, -132 - (8 if fox else 0)), (-76, -118)]), pal[2]))
    out.append(pline(hp([(-110, -88), (-96, -84), (-90, -84)]), "#1A1008", 1.2 * s, seed, 0.7, 1))
    # near legs
    for pts in (((-56, -58), (-56, -36), (-58, -12), (-62, 0)), ((58, -64), (46, -36), (66, -16), (60, 0))):
        out.append(taper(catmull(L([(px, py * k_ if py < -20 else py) for px, py in pts]), 6), lw[0] * s, lw[1] * s, pal[1]))
        fx_, fy_ = L([pts[-1]])[0]
        out.append(f'<path d="{blob(fx_ - (3 if not flip else -3) * s, fy_ - 2 * s, 6.4 * s, 3.2 * s, int(fx_), 0.1, 8)}" fill="{pal[2] if not fox else "#1A1008"}"/>')
    if rim:
        out.append(ink(smooth_open(hp([(-104, -98), (-90, -110), (-78, -118), (-60, -112)]) + L([(-48, -100 * k_), (-24, -92 * k_), (30, -84 * k_), (64, -82 * k_)])), rim, 2, seed, 1, 0.8))
    return "".join(out)


def baby_in_basket(D, cx, cy, s, seed):
    def L(pts):
        return T(pts, cx, cy, s)
    out = [cast(D, cx, cy + 22 * s, 70 * s, 8 * s, "#1A0A04", 0.4, seed)]
    for k, dx in enumerate((-18, 16)):
        hx, hy = L([(dx, -16 - k * 2)])[0]
        out.append(painted(D, blob_pts(hx, hy, 12 * s, 11.4 * s, seed + k, 0.04, 14), ("#FFE2C8", "#F2C0A0", "#B87A5A"), seed + k, sdir=(0.4, 0.5), sk=0.15, n=4, inkw=1.0, inkc="#6A3A2A", hi=0.4))
        out.append(f'<path d="M {hx - 5 * s:.1f} {hy + 1 * s:.1f} q {2 * s:.1f} {-2 * s:.1f} {4 * s:.1f} 0 M {hx + 2 * s:.1f} {hy + 1 * s:.1f} q {2 * s:.1f} {-2 * s:.1f} {4 * s:.1f} 0" stroke="#6A3A2A" stroke-width="1" fill="none"/>')
        out.append(f'<path d="M {hx - 4 * s:.1f} {hy - 10 * s:.1f} q {4 * s:.1f} {-6 * s:.1f} {8 * s:.1f} {-1 * s:.1f}" stroke="#6A3A1A" stroke-width="{1.8 * s:.1f}" fill="none"/>')
        out.append(taper(L([(dx + 8 - k * 16, -6), (dx + 12 - k * 22, -20), (dx + 14 - k * 26, -28)]), 4 * s, 3.4 * s, "#F2C0A0"))
    blanket = L([(-40, -2), (40, -4), (36, 8), (-36, 8)])
    out.append(painted(D, blanket, ("#F6F0E2", "#E2D8C0", "#A89A7A"), seed + 3, sk=0.15, n=6, inkw=1.0, inkc="#5A4A30", hi=0.3))
    bask = L([(-52, -2), (52, -4), (44, 22), (-44, 22)])
    out.append(painted(D, bask, ("#E8C27A", "#B8863A", "#5A3A14"), seed + 4, sk=0.2, angle=0, n=10, inkw=1.4, inkc="#3A2008", hi=0.4))
    for k in range(9):
        a, b = L([(-46 + k * 11, 0), (-40 + k * 10, 20)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#5A3A14" stroke-width="1.2" opacity="0.6"/>')
    for k in range(3):
        a, b = L([(-48, 4 + k * 6), (48, 2 + k * 6)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#F2D8A0" stroke-width="1" opacity="0.5"/>')
    return "".join(out)


@design("romulus-and-remus")
def romulus_and_remus():
    D = Doc2("my-rr")
    out = [sky(D, [(0, "#3A4A7A"), (0.45, "#C88A7A"), (0.7, "#F6C08A"), (0.8, "#FCE2B0")], 1, 420, ["#6A6A9A", "#FFD8A8", "#E8A08A"], 60)]
    out.append(soft_glow(D, 430, 330, 200, "#FFE8B0", 0.7))
    # the seven hills, hazy, a few pines and the river Tiber winding through
    hills_ = ridge([(-20, 360), (60, 330), (130, 346), (200, 320), (270, 350), (340, 326), (420, 350), (480, 332), (560, 352), (620, 340)], 4, 10)
    out.append(hill(D, hills_, 460, ("#D8B8B0", "#A88A90", "#6A5A6A"), 4, inkw=0, lit="#FFE8D0"))
    for k, (px, py) in enumerate(((70, 336), (210, 326), (350, 332), (490, 338))):
        out.append(f'<path d="{blob(px, py - 14, 16, 8, k, 0.2, 10)}" fill="#5A4A5A"/>')
        out.append(taper([(px, py), (px, py - 10)], 2, 2, "#5A4A5A"))
    out.append(sea(D, 400, 470, [(0, "#F6D0A0"), (1, "#8A7A9A")], 5, ["#FFE8C0", "#6A5A7A"], 30))
    out.append(wave_lines(5, (0, 404, 600, 470), ["#FFF2D8", "#6A5A7A"], 30, (10, 28), 1.4, 2, (0.3, 0.6)))
    # reeds and the near bank
    bank = [(-20, 452), (100, 440), (250, 450), (400, 446), (620, 460)]
    out.append(hill(D, bank, 620, ("#9AA066", "#5A6A3A", "#24301A"), 6, inkw=1.4))
    out.append(grass(7, (0, 446, 600, 600), ["#B8BA7A", "#4A5A2A", "#7A8A4A"], 160, (8, 20), 1.6))
    for k in range(14):
        x = 20 + k * 9 + (k % 3) * 4
        out.append(taper([(x, 470), (x + (k % 3 - 1) * 4, 400 + (k % 4) * 10)], 3, 1, "#3A4A22"))
        if k % 3 == 0:
            out.append(f'<path d="{blob(x + (k % 3 - 1) * 4, 404 + (k % 4) * 10, 3, 9, k, 0.05, 8)}" fill="#6A4A2A"/>')
    # the sacred fig, its branch overhead, a woodpecker (the bird of Mars who also fed them)
    out.append(taper(catmull([(560, 640), (548, 470), (530, 360), (500, 270), (470, 210)], 8), 40, 22, "#5A3A2A"))
    out.append(taper(catmull([(520, 340), (440, 300), (360, 262), (300, 240)], 8), 18, 6, "#5A3A2A"))
    for (cx_, cy_, rx_, ry_) in ((530, 236, 110, 66), (410, 240, 96, 40)):
        out.append(dab_crown(D, cx_, cy_, rx_, ry_, [("#7A9A4A", "#3E5A2A", "#16261A"), ("#8AAA5A", "#4A6A2E", "#1E321A")], cx_, n=int(rx_ * ry_ / 30), size=(8, 15), light=(-0.4, -0.9), inkw=0))
    for k in range(8):
        a = random.Random(k).uniform(0, 6.28)
        out.append(f'<circle cx="{470 + math.cos(a) * 80:.1f}" cy="{246 + math.sin(a) * 30:.1f}" r="4" fill="#7A3A5A"/>')
    wx, wy = 346, 254
    out.append(poly([(wx - 10, wy), (wx - 6, wy - 12), (wx + 6, wy - 14), (wx + 14, wy - 4), (wx + 20, wy + 10), (wx + 4, wy + 4)], "#2A2A2A"))
    out.append(f'<path d="{blob(wx - 6, wy - 16, 6, 5, 3, 0.05, 8)}" fill="#C8202A"/>')
    out.append(sharp([(wx - 12, wy - 14), (wx - 22, wy - 12), (wx - 12, wy - 10)], "#3A3A3A"))
    for k in range(3):
        out.append(f'<path d="M {wx + 2 + k * 4} {wy - 8} l 2 6" stroke="#FFFFFF" stroke-width="1.2"/>')
    # the she-wolf standing over the twins in their basket, washed ashore
    out.append(cast(D, 300, 486, 150, 12, "#1A1008", 0.45, 3))
    out.append(canine(D, 360, 486, 1.42, 8, ("#8A7A70", "#4A3E38", "#16100C"), rim="#FFD8A0", head_drop=14))
    out.append(baby_in_basket(D, 222, 474, 1.12, 9))
    # lettering
    out.append(multi(300, 108, [("Romulus ", "#2A1A3A"), ("&", "#A8302A"), (" Remus", "#2A1A3A")], DMS, 62, max_w=440, shadow="#FFF2D8", sdy=2.5))
    out.append(tx(300, 140, "ROMAN · THE SHE-WOLF OF THE TIBER", CINZEL, 17, "#2A1A3A", ls=3, max_w=420))
    out.append(tx(301.5, 539.5, "Rome began with a mother’s kindness.", SERIF_IT, 26, "#14100A", max_w=440, op=0.6))
    out.append(tx(300, 538, "Rome began with a mother’s kindness.", SERIF_IT, 26, "#FFF6E0", max_w=440))
    return fin(D, out, 31)


# ================================================================ 19. the selkie — the sealskin left on the rocks
def seated_back(x, base, s, col, rim=None, hair=None, flip=False):
    """A woman seated on a rock seen from behind, long hair down her back, looking out to sea. ~92*s tall."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-30, 0), (-34, -18), (-26, -40), (-18, -60), (-20, -70), (-12, -74), (12, -74), (20, -70), (18, -60), (24, -40), (30, -18), (28, 0)]), col)]
    out.append(f'<path d="{blob(*L([(0, -84)])[0], 9 * s, 10.4 * s, 3, 0.06, 12)}" fill="{col}"/>')
    hc = hair or col
    out.append(poly(L([(-9, -92), (-12, -80), (-14, -60), (-12, -40), (-6, -28), (0, -24), (6, -30), (12, -44), (12, -66), (10, -84), (4, -94)]), hc))
    out.append(taper(L([(-16, -66), (-24, -46), (-30, -30)]), 6 * s, 4 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(4, -94), (10, -84), (12, -66), (18, -60), (24, -40), (30, -18)])), rim, 1.8, 3, 1, 0.85))
    return "".join(out)


def sealskin(D, cx, cy, s, seed):
    """A grey dappled sealskin draped over a rock: the pelt folded, a fore-flipper and the tail flippers hanging."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = []
    pelt = L([(-70, -10), (-50, -22), (-10, -26), (30, -22), (64, -12), (80, 8), (70, 30), (52, 24), (40, 40), (20, 34), (-10, 38), (-40, 30), (-62, 40), (-80, 22)])
    out.append(painted(D, pelt, ("#C8D0D8", "#7A8494", "#2A303C"), seed, sdir=(0.4, 0.8), sk=0.22, angle=-10, n=30, inkw=1.6, inkc="#141820", hi=0.5))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(pelt)}"/>')
    spots = [f'<path d="{blob(*L([(rnd.uniform(-70, 70), rnd.uniform(-20, 34))])[0], rnd.uniform(2, 5) * s, rnd.uniform(1.5, 3.5) * s, k, 0.2, 8)}" fill="#2A303C" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>' for k in range(40)]
    spots.append(f'<path d="{smooth_open(L([(-60, 0), (-20, -6), (20, -4), (60, 4)]))}" stroke="#E8F0F8" stroke-width="{3 * s:.1f}" fill="none" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(spots)}</g>')
    for (pts, w) in (([(-78, 22), (-90, 44), (-96, 58)], 12), ([(70, 30), (82, 52), (76, 66)], 10)):
        p = L(pts)
        out.append(taper(catmull(p, 6), w * s, w * 0.6 * s, "#5A6474"))
        ex, ey = p[-1]
        out.append(f'<path d="{blob(ex, ey, 10 * s, 6 * s, int(ex), 0.1, 10, 60)}" fill="#3A4252"/>')
        for k in range(3):
            out.append(f'<path d="M {ex - 4 * s + k * 4 * s:.1f} {ey:.1f} l {1.5 * s:.1f} {6 * s:.1f}" stroke="#141820" stroke-width="1" opacity="0.6"/>')
    return "".join(out)


def seal_head(D, x, y, s, seed, flip=False):
    def L(pts):
        return T(pts, x, y, s, flip)
    head = L([(-14, 4), (-16, -6), (-10, -14), (2, -16), (12, -10), (18, -4), (16, 2), (6, 6)])
    out = [painted(D, head, ("#8A96A8", "#3A4454", "#10141C"), seed, sdir=(0.5, 0.6), sk=0.2, n=4, inkw=1.0, inkc="#0A0C12", hi=0.5)]
    ex, ey = L([(4, -8)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="#06080C"/><circle cx="{ex - 0.5:.1f}" cy="{ey - 0.6:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    out.append(f'<path d="{blob(*L([(0, 8)])[0], 26 * s, 3 * s, seed, 0.2, 10)}" fill="#E8F0FF" opacity="0.4"/>')
    return "".join(out)


@design("the-selkie")
def the_selkie():
    D = Doc2("my-sk")
    out = [sky(D, [(0, "#0A1028"), (0.5, "#1E2E58"), (0.8, "#4A5A84"), (1, "#6A7A9A")], 1, 400, ["#2A3A6A", "#0A1028", "#6A7AA8"], 60)]
    out.append(stars_field(3, (0, 0, 600, 300), 90))
    mx, my = 370, 250
    out.append(moon(D, mx, my, 64, 4, pal=("#FFFFFF", "#EEF2FA", "#B8C4D8"), glow="#E8F0FF", gs=0.55))
    for (cx_, cy_, w_, sd) in ((150, 300, 200, 3), (520, 330, 180, 4)):
        out.append(puff_cloud(D, cx_, cy_, w_, sd, ("#8A9AC0", "#4A5A84", "#1E2A4A"), op=0.7))
    # the northern sea with a silver road under the moon, a far headland
    out.append(painted(D, [(-20, 372), (40, 350), (110, 344), (170, 360), (230, 370), (-20, 380)], ("#4A5274", "#2A3050", "#10142A"), 2, sk=0.1, n=10, inkw=0, hi=0.2))
    out.append(sea(D, 370, 620, [(0, "#4A5A84"), (0.4, "#1E2A50"), (1, "#0A1028")], 5, ["#6A7AAA", "#0A1028", "#A8B8D8"], 80))
    rnd = random.Random(6)
    for k in range(60):
        y = 374 + (k / 60) ** 1.5 * 200
        w = 10 + (y - 370) * 0.7
        x = mx + rnd.uniform(-w, w) * 0.5
        out.append(taper([(x - w * 0.3, y), (x, y - 1.5), (x + w * 0.3, y)], 0.8, rnd.uniform(1.5, 3.5), "#F2F6FF", rnd.uniform(0.4, 0.95)))
    out.append(wave_lines(7, (0, 376, 600, 600), ["#8A9AC8", "#0A1028", "#C8D4F0"], 60, (10, 30), 1.6, 2, (0.3, 0.6)))
    # her seal kin waiting in the water
    for (hx, hy, hs, fl) in ((300, 430, 1.1, True), (440, 410, 0.9, False), (500, 452, 1.2, False), (210, 404, 0.8, True)):
        out.append(seal_head(D, hx, hy, hs, int(hx), flip=fl))
    # the shore rocks, wet and moonlit
    r1 = [(-20, 620), (-20, 470), (30, 440), (100, 430), (170, 448), (220, 480), (250, 540), (260, 620)]
    out.append(painted(D, r1, ("#4A5268", "#20263A", "#080A14"), 8, sdir=(-0.5, 0.6), sk=0.2, angle=-30, n=40, inkw=1.4, inkc="#04060C", hi=0.0))
    out.append(ink(smooth_open(r1[2:6]), "#C8D4F0", 2.4, 3, 1, 0.7))
    r2 = [(330, 620), (360, 540), (420, 504), (500, 496), (570, 510), (620, 540), (620, 620)]
    out.append(painted(D, r2, ("#4A5268", "#20263A", "#080A14"), 9, sdir=(-0.5, 0.6), sk=0.2, angle=-30, n=40, inkw=1.4, inkc="#04060C", hi=0.0))
    out.append(ink(smooth_open(r2[1:5]), "#C8D4F0", 2.4, 4, 1, 0.7))
    for k in range(18):
        x = rnd.uniform(0, 240) if k % 2 else rnd.uniform(360, 600)
        out.append(f'<path d="{blob(x, rnd.uniform(500, 600), rnd.uniform(4, 10), rnd.uniform(2, 4), k, 0.3, 8)}" fill="#3A5A3A" opacity="0.6"/>')
    # the skin she left on the rock, and the woman herself, looking out to the sea
    out.append(sealskin(D, 480, 480, 0.9, 10))
    out.append(seated_back(120, 440, 1.25, "#0C1020", rim="#DCE6FF", hair="#141828"))
    # lettering
    out.append(letters(D, 300, 114, "The Selkie", SERIF_IT, 72, "#F2F6FF", ["#FFFFFF", "#DCE6FF", "#C8D8F8"], 13, max_w=380,
                       shadow="#000010", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 146, "SCOTTISH & IRISH FOLKLORE · THE SEAL WIFE", CINZEL, 15, "#DCE6FF", ls=2, max_w=430))
    out.append(tx(300, 548 - 10, "The sea will always call her home.", SERIF_IT, 26, "#F2F6FF", max_w=420))
    return fin(D, out, 32)


# ================================================================ 20. amaterasu — the sun comes out of the cave
def rooster(D, x, y, s, seed, flip=False, pal=("#F2E8D8", "#C8B8A0", "#5A4A3A")):
    """A long-tailed rooster (onagadori) perched, crowing: comb, wattle, arching sickle tail. (x, y) = feet."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    for k in range(6):
        tp = L([(10, -20), (34 + k * 4, -34 + k * 3), (60 + k * 6, -20 + k * 6), (70 + k * 8, 10 + k * 12)])
        out.append(taper(catmull(tp, 6), 5 * s, 1.5 * s, ("#1A1A2A", "#2A4A3A", "#3A2A4A")[k % 3]))
    body = L([(-16, -20), (-10, -32), (8, -34), (20, -26), (18, -12), (4, -6), (-12, -8)])
    out.append(painted(D, body, pal, seed, sk=0.2, n=6, inkw=1.2, inkc="#2A1A0A", hi=0.4))
    out.append(painted(D, L([(-8, -30), (-14, -46), (-20, -54), (-14, -60), (-6, -54), (-2, -40), (2, -32)]), ("#FFD080", "#E8902A", "#8A4A10"), seed + 1, sk=0.2, n=4, inkw=1.0, inkc="#2A1A0A", hi=0.4))
    out.append(poly(L([(-20, -60), (-22, -68), (-17, -64), (-15, -70), (-12, -64), (-9, -68), (-10, -58)]), "#D8202A"))
    out.append(sharp(L([(-21, -56), (-30, -58), (-22, -52)]), "#E8B830"))
    out.append(poly(L([(-20, -52), (-22, -46), (-18, -44)]), "#D8202A"))
    ex, ey = L([(-16, -58)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.4 * s:.1f}" fill="#1A0A04"/>')
    for k in range(2):
        a, b = L([(-2 + k * 6, -8), (0 + k * 6, 0)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#C8902A" stroke-width="{2 * s:.1f}"/>')
    return "".join(out)


def bronze_mirror(D, cx, cy, r, seed):
    out = [soft_glow(D, cx, cy, r * 3, "#FFF2C0", 0.8)]
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{D.rad([(0, "#FFFFFF"), (0.5, "#FFF2C0"), (1, "#E8B850")])}" stroke="#8A6020" stroke-width="{r * 0.16:.1f}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.8:.1f}" fill="none" stroke="#C8902A" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<path d="M {cx - r * 0.5:.1f} {cy - r * 0.3:.1f} q {r * 0.3:.1f} {-r * 0.3:.1f} {r * 0.6:.1f} {-r * 0.3:.1f}" stroke="#FFFFFF" stroke-width="{r * 0.12:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def magatama(cx, cy, r, ang, col):
    pts = T([(0, -1), (0.8, -0.6), (1, 0.2), (0.6, 0.9), (-0.2, 1.1), (-0.6, 1.6), (-0.4, 0.8), (-0.9, 0.2), (-0.6, -0.7)], cx, cy, r, False, ang)
    return poly(pts, col) + f'<circle cx="{T([(0.1, -0.2)], cx, cy, r, False, ang)[0][0]:.1f}" cy="{T([(0.1, -0.2)], cx, cy, r, False, ang)[0][1]:.1f}" r="{r * 0.18:.1f}" fill="#FFFFFF" opacity="0.7"/>'


@design("amaterasu")
def amaterasu():
    D = Doc2("my-am")
    out = [sky(D, [(0, "#0A0A24"), (0.6, "#1E1E44"), (1, "#3A2A44")], 1, 600, ["#2A2A54", "#06061A", "#4A3A5A"], 60)]
    out.append(stars_field(3, (0, 0, 600, 260), 80))
    # the rock face of the heavenly cave and the great boulder rolled aside
    cliff = [(140, 620), (150, 420), (170, 300), (210, 200), (280, 150), (380, 140), (470, 170), (540, 240), (600, 300), (620, 620)]
    out.append(painted(D, cliff, ("#6A5A6A", "#3A2E40", "#100A16"), 3, sdir=(-0.4, 0.4), sk=0.18, angle=-80, n=80, inkw=1.4, inkc="#06040A", hi=0.0))
    cave = [(300, 470), (296, 380), (310, 300), (346, 250), (396, 240), (440, 262), (466, 320), (474, 400), (480, 470)]
    cx_, cy_ = 388, 360
    out.append(poly(cave, "#FFF6D0"))
    out.append(soft_glow(D, cx_, cy_, 280, "#FFE070", 0.8))
    out.append(ray_fan(cx_, cy_ + 20, 60, 520, 34, "#FFF2B0", 0.22, a0=150, a1=390, seed=5))
    out.append(soft_glow(D, cx_, cy_, 120, "#FFFFFF", 0.9))
    out.append(ink(smooth_open(cave), "#FFE8A0", 3, 3, 1, 0.8))
    boulder = blob_pts(520, 420, 82, 92, 6, 0.08, 22)
    out.append(painted(D, boulder, ("#9A8A8A", "#5A4A52", "#1A121A"), 6, sdir=(0.7, 0.4), sk=0.22, angle=-60, n=40, inkw=1.6, inkc="#06040A", hi=0.0))
    out.append(ink(smooth_open(boulder[12:20]), "#FFE8A0", 3, 6, 1, 0.75))
    out.append(taper(catmull([(470, 340), (520, 360), (580, 350), (610, 370)], 6), 6, 6, "#D8C8A0"))
    # the sakaki tree with the mirror, the strings of magatama jewels and white paper streamers
    tx_ = 168
    out.append(taper(catmull([(tx_ + 10, 600), (tx_, 460), (tx_ + 10, 330), (tx_ - 4, 230)], 8), 22, 8, "#3A2418"))
    for (bx, by, ang) in ((tx_ + 6, 300, -30), (tx_ + 2, 360, 200), (tx_ + 6, 420, -20)):
        out.append(taper(catmull([(bx, by), (bx + math.cos(math.radians(ang)) * 50, by + math.sin(math.radians(ang)) * 30 - 10), (bx + math.cos(math.radians(ang)) * 90, by + math.sin(math.radians(ang)) * 40 - 20)], 6), 8, 2, "#3A2418"))
    out.append(dab_crown(D, tx_ - 6, 220, 90, 56, [("#5A8A5A", "#2A5A3A", "#0E2418"), ("#6A9A5A", "#3A6A3A", "#14301A")], 7, n=150, size=(6, 11), light=(0.8, -0.2), inkw=0))
    out.append(dab_crown(D, tx_ + 60, 300, 50, 30, [("#5A8A5A", "#2A5A3A", "#0E2418")], 8, n=40, size=(6, 10), light=(0.8, -0.2), inkw=0))
    out.append(taper([(tx_ + 30, 274), (tx_ + 30, 300)], 2, 2, "#C8A060"))
    out.append(bronze_mirror(D, tx_ + 30, 318, 22, 9))
    for k, (x0_, y0_) in enumerate(((tx_ - 40, 240), (tx_ + 76, 300))):
        for j in range(7):
            out.append(magatama(x0_ + (j % 2) * 3, y0_ + j * 14, 5.2, 30 + j * 10, ("#2A8A6A", "#C8402A", "#2A6AC8", "#E8B830")[(j + k) % 4]))
    for (sx_, sy_) in ((tx_ - 70, 260), (tx_ + 40, 340), (tx_ - 20, 300)):
        for j in range(4):
            out.append(sharp([(sx_ + (j % 2) * 8, sy_ + j * 10), (sx_ + 10 + (j % 2) * 8, sy_ + j * 10), (sx_ + (j % 2) * 8 + 2, sy_ + j * 10 + 12)], "#FFFFFF", 0.92))
    # the long-crowing roosters on their perch: the first torii
    py = 470
    for px in (236, 290):
        out.append(taper([(px, 620), (px, py - 4)], 8, 7, "#B83020"))
    out.append(taper([(222, py), (304, py - 2)], 9, 9, "#C8402A"))
    out.append(taper([(226, py + 18), (300, py + 18)], 6, 6, "#B83020"))
    out.append(rooster(D, 248, py - 4, 1.0, 11))
    out.append(rooster(D, 286, py - 4, 0.9, 12, flip=True, pal=("#4A4A5A", "#22222E", "#0A0A12")))
    # ground in the light
    out.append(painted(D, [(-20, 620), (-20, 520), (200, 506), (400, 498), (620, 510), (620, 620)], ("#6A5A4A", "#3A2E28", "#100A08"), 13, sk=0.1, angle=0, n=30, inkw=0, hi=0.2))
    out.append(soft_glow(D, 390, 500, 160, "#FFE070", 0.5))
    # lettering
    out.append(gilt(D, 300, 104, "AMATERASU", CINZEL, 56, ls=10, max_w=420, seed=14, deboss="#000000", dop=0.85))
    out.append(tx(300, 134, "JAPANESE · THE SUN RETURNS TO THE WORLD", CINZEL, 15, "#FFF2D0", ls=2, max_w=430))
    out.append(tx(301.5, 539.5, "Light always finds its way out.", SERIF_IT, 27, "#1A0A04", max_w=420, op=0.6))
    out.append(tx(300, 538, "Light always finds its way out.", SERIF_IT, 27, "#FFF6E0", max_w=420))
    return fin(D, out, 33)


# ================================================================ 21. kitsune — the nine-tailed fox under the moon
def foxfire(D, x, y, r, seed, col="#8AF0E0"):
    out = [soft_glow(D, x, y, r * 4, col, 0.7)]
    out.append(poly([(x - r, y + r * 0.4), (x - r * 0.6, y - r), (x, y - r * 2.4), (x + r * 0.4, y - r * 1.2), (x + r, y + r * 0.2), (x, y + r)], col, 0.85))
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


@design("kitsune")
def kitsune():
    D = Doc2("my-ks")
    out = [sky(D, [(0, "#0A1430"), (0.5, "#1E2E5A"), (0.85, "#3A4A7A"), (1, "#5A5A84")], 1, 600, ["#2A3A6A", "#0A1430", "#4A5A8A"], 60)]
    out.append(stars_field(4, (0, 0, 600, 360), 100))
    mx, my = 300, 250
    out.append(moon(D, mx, my, 140, 5, pal=("#FFFDF0", "#F6EEDA", "#D8CCAA"), gs=0.55))
    # far hills, a vermilion torii on the ridge, pines
    far = ridge([(-20, 400), (100, 380), (220, 396), (340, 376), (460, 394), (620, 380)], 6, 8)
    out.append(hill(D, far, 620, ("#4A4A74", "#2A2A4E", "#10102A"), 6, inkw=0))
    tx_, tb = 494, 392
    for dx in (-14, 14):
        out.append(taper([(tx_ + dx, tb), (tx_ + dx * 0.9, tb - 40)], 4, 3.4, "#C8302A"))
    out.append(taper([(tx_ - 26, tb - 42), (tx_, tb - 40), (tx_ + 26, tb - 42)], 5, 5, "#C8302A"))
    out.append(taper([(tx_ - 20, tb - 32), (tx_ + 20, tb - 32)], 3, 3, "#C8302A"))
    out.append(taper([(tx_ - 28, tb - 46), (tx_ + 28, tb - 46)], 3, 3, "#1A0A0A"))
    for k in range(5):
        out.append(conifer(60 + k * 30, 392 + (k % 2) * 4, 30 + (k % 3) * 8, "#14143A", k, width=0.3))
    # the field of susuki grass, silver plumes catching the moon
    near = [(-20, 470), (140, 446), (300, 452), (460, 444), (620, 466)]
    out.append(hill(D, near, 620, ("#4A5A5A", "#24302E", "#0A1210"), 8, inkw=0))
    rnd = random.Random(8)
    for k in range(70):
        x = rnd.uniform(-10, 610)
        base = rnd.uniform(470, 620)
        h = rnd.uniform(60, 130)
        lean = rnd.uniform(-0.4, 0.1)
        p = [(x, base), (x + lean * h * 0.4, base - h * 0.6), (x + lean * h, base - h)]
        out.append(taper(p, 2, 0.8, "#2A3A30"))
        if k % 2:
            out.append(taper(catmull([p[2], (p[2][0] - 6, p[2][1] + 10), (p[2][0] - 14, p[2][1] + 26)], 4), 6, 1.5, "#E8E0D0", 0.8))
    # the fox on the rise, nine tails fanned, foxfire floating about her
    out.append(cast(D, 304, 452, 120, 10, "#000000", 0.4, 2))
    out.append(canine(D, 300, 450, 1.25, 9, ("#FFFFFF", "#ECE6DA", "#A8A090"), kind="fox", tails=9, rim="#FFFFFF"))
    # her face markings in vermilion, as on the shrine foxes
    for (ax, ay) in ((-92, -102), (-82, -96)):
        px, py = T([(ax, ay * 0.82)], 300, 450, 1.25)[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} l {6 * 1.25:.1f} {-4 * 1.25:.1f}" stroke="#D8302A" stroke-width="2.2" stroke-linecap="round"/>')
    for (fx, fy, fr) in ((150, 360, 6), (200, 300, 5), (460, 330, 6), (520, 410, 5), (110, 430, 4), (410, 280, 4)):
        out.append(foxfire(D, fx, fy, fr, int(fx)))
    # lettering
    out.append(letters(D, 300, 116, "Kitsune", SERIF_IT, 80, "#FFFFFF", ["#FFFFFF", "#FFE8E0", "#E8F0FF"], 14, max_w=360,
                       shadow="#0A1430", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 150, "JAPANESE · THE NINE-TAILED FOX", CINZEL, 16, "#E8F0FF", ls=3, max_w=420))
    out.append(tx(300, 538, "A tail for every hundred years of wisdom", SERIF_IT, 24, "#F2F6FF", max_w=440))
    return fin(D, out, 34)


# ================================================================ 22. the dragon's pearl — the long dragon in the clouds
def ruyi_cloud(D, x, y, s, seed, pal=("#F2F6F0", "#9AC8C0", "#3A7A78")):
    """An auspicious cloud in the Chinese manner: a cluster of curling scrolls with a trailing tail."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    blobs = [(0, 0, 26), (-30, 6, 20), (28, 8, 18), (-10, -18, 18), (14, -16, 14)]
    shapes = []
    for k, (dx, dy, r) in enumerate(blobs):
        shapes.append(blob(*L([(dx, dy)])[0], r * s, r * 0.9 * s, seed + k, 0.04, 14))
    tail = L([(30, 14), (70, 22), (100, 14), (120, 22), (90, 30), (40, 26)])
    shapes.append(smooth_closed(tail))
    allp = " ".join(shapes)
    out.append(f'<path d="{allp}" fill="{pal[0]}"/>')
    for k, (dx, dy, r) in enumerate(blobs):
        cx_, cy_ = L([(dx, dy)])[0]
        sp = []
        for i in range(16):
            t = i / 15
            a = math.radians(200 + t * 300)
            rr = r * s * (0.8 - 0.55 * t)
            sp.append((cx_ + math.cos(a) * rr, cy_ + math.sin(a) * rr))
        out.append(taper(sp, 3.2 * s, 1 * s, pal[2], 0.85))
    out.append(f'<path d="{allp}" fill="none" stroke="{pal[2]}" stroke-width="{1.8 * s:.1f}" opacity="0.7"/>')
    out.append(f'<path d="{blob(*L([(0, 10)])[0], 40 * s, 12 * s, seed, 0.1, 12)}" fill="{pal[1]}" opacity="0.35"/>')
    return "".join(out)


def long_dragon(D, spine_pts, w, seed, pal=("#FFE08A", "#E8A030", "#8A4A10"), belly="#F6E6B0", fin_col="#C8302A"):
    """A Chinese long: serpentine scaled body along spine_pts (tail first), dorsal flames, belly plates, four legs
    with eagle claws. Returns (svg, head point, head angle)."""
    path = catmull(spine_pts, 10)
    n = len(path)
    widths = [w * (0.25 + 0.75 * math.sin(math.pi * min(1, (i / (n - 1)) * 1.05 + 0.05)) ** 0.6) for i in range(n)]
    left, right, norms = [], [], []
    for i, (x, y) in enumerate(path):
        a = path[max(0, i - 1)]
        b = path[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / L_, dx / L_
        norms.append((nx, ny))
        left.append((x + nx * widths[i] / 2, y + ny * widths[i] / 2))
        right.append((x - nx * widths[i] / 2, y - ny * widths[i] / 2))
    out = []
    # dorsal fin flames along the top edge
    rnd = random.Random(seed)
    for i in range(3, n - 4, 3):
        x, y = left[i]
        nx, ny = norms[i]
        h = widths[i] * 0.55
        tx_, ty_ = x + nx * h + (path[min(n - 1, i - 2)][0] - path[i][0]) * 0.3, y + ny * h + (path[min(n - 1, i - 2)][1] - path[i][1]) * 0.3
        out.append(poly([(x - ny * 4, y + nx * 4), (tx_, ty_), (x + ny * 6, y - nx * 6)], fin_col))
    body = left + right[::-1]
    out.append(painted(D, body, pal, seed, sdir=(0.3, 0.8), sk=0.2, angle=-20, n=60, inkw=1.6, inkc="#3A1A04", hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    sc = []
    for i in range(2, n - 2, 2):
        x, y = path[i]
        nx, ny = norms[i]
        ww = widths[i]
        for j in (-0.25, 0.0, 0.25):
            sx, sy = x + nx * ww * j, y + ny * ww * j
            r = ww * 0.16
            ux, uy = ny, -nx
            sc.append(f'<path d="M {sx - nx * r:.1f} {sy - ny * r:.1f} Q {sx + ux * r * 1.2:.1f} {sy + uy * r * 1.2:.1f} {sx + nx * r:.1f} {sy + ny * r:.1f}" stroke="{pal[2]}" stroke-width="1.2" fill="none" opacity="0.65"/>')
    # belly plates along the lower edge
    for i in range(2, n - 2, 2):
        x, y = right[i]
        nx, ny = norms[i]
        sc.append(f'<path d="M {x:.1f} {y:.1f} l {nx * widths[i] * 0.28:.1f} {ny * widths[i] * 0.28:.1f}" stroke="{belly}" stroke-width="{max(2, widths[i] * 0.2):.1f}" opacity="0.8"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # legs with four-toed claws at a few points
    for t, side in ((0.32, 1), (0.42, -1), (0.66, 1), (0.76, -1)):
        i = int(t * (n - 1))
        x, y = path[i]
        nx, ny = norms[i]
        sg = -side
        kx, ky = x + nx * sg * widths[i] * 0.9 + (path[i + 3][0] - x) * 0.6, y + ny * sg * widths[i] * 0.9 + (path[i + 3][1] - y) * 0.6
        fx, fy = kx + nx * sg * widths[i] * 0.6, ky + ny * sg * widths[i] * 0.6
        out.append(taper(catmull([(x, y), (kx, ky), (fx, fy)], 6), widths[i] * 0.42, widths[i] * 0.2, pal[1]))
        for c in range(4):
            a = math.atan2(ny * sg, nx * sg) + (c - 1.5) * 0.45
            out.append(taper([(fx, fy), (fx + math.cos(a) * 9, fy + math.sin(a) * 9), (fx + math.cos(a + 0.6) * 13, fy + math.sin(a + 0.6) * 13)], 3, 1, "#F6E6B0"))
    hx, hy = path[-1]
    ha = math.degrees(math.atan2(path[-1][1] - path[-3][1], path[-1][0] - path[-3][0]))
    return "".join(out), (hx, hy), ha


def long_head(D, x, y, s, ang, seed, pal=("#FFE08A", "#E8A030", "#8A4A10")):
    """Head of a Chinese dragon facing along +x (rotated by ang): long snout, open jaws, whiskers, antlers, mane."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = []
    # flowing mane behind the head
    for k in range(7):
        a = -150 + k * 18
        p = L([(0, 0), (-20 + math.cos(math.radians(a)) * 10, math.sin(math.radians(a)) * 24), (-50 + math.cos(math.radians(a)) * 6, math.sin(math.radians(a)) * 40)])
        out.append(taper(catmull(p, 5), 10 * s, 2 * s, ("#C8302A", "#E8602A")[k % 2]))
    # antlers
    for sg in (-1, 1):
        p = L([(4, sg * -10), (-14, sg * -30), (-34, sg * -40)])
        out.append(taper(catmull(p, 5), 5 * s, 2 * s, "#F6E6B0"))
        q = L([(-14, sg * -30), (-8, sg * -46)])
        out.append(taper(q, 3 * s, 1.4 * s, "#F6E6B0"))
    upper = L([(-6, -14), (14, -18), (34, -16), (56, -12), (62, -4), (40, -2), (16, -2), (-4, 2)])
    lower = L([(-2, 4), (18, 6), (44, 14), (52, 22), (30, 20), (6, 16)])
    out.append(painted(D, lower, pal, seed + 1, sk=0.2, n=6, inkw=1.2, inkc="#3A1A04", hi=0.4))
    out.append(poly(L([(10, 0), (46, 2), (44, 12), (12, 8)]), "#8A1A10"))
    out.append(painted(D, upper, pal, seed, sk=0.2, n=10, inkw=1.2, inkc="#3A1A04", hi=0.5))
    for k in range(5):
        a, b, c = L([(18 + k * 8, -2), (21 + k * 8, 4), (24 + k * 8, -2)])
        out.append(sharp([a, b, c], "#FFFFFF"))
    # whiskers
    for sg, curl in ((-1, -1), (1, 1)):
        p = L([(56, -8), (74, -20 * sg * -1), (92, -6 * sg * -1), (104, 16 * curl)])
        out.append(taper(catmull(p, 6), 3 * s, 0.8 * s, "#F6E6B0"))
    # brow and eye
    out.append(poly(L([(4, -16), (20, -26), (30, -18), (16, -14)]), "#C8302A"))
    ex, ey = L([(18, -12)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.6 * s:.1f}" fill="#FFF6C0" stroke="#3A1A04" stroke-width="1.2"/><circle cx="{ex + 1:.1f}" cy="{ey:.1f}" r="{2 * s:.1f}" fill="#1A0A04"/>')
    nx_, ny_ = L([(58, -12)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{2 * s:.1f}" fill="#3A1A04"/>')
    return "".join(out)


@design("the-dragons-pearl")
def the_dragons_pearl():
    D = Doc2("my-dp")
    out = [sky(D, [(0, "#0A2A2E"), (0.5, "#14444A"), (1, "#0A2428")], 1, 600, ["#1E5A5A", "#04181C", "#2A6A6A"], 70)]
    out.append(soft_glow(D, 420, 210, 260, "#FFF2C0", 0.35))
    # auspicious clouds, back layer
    for (x, y, s_, sd) in ((90, 170, 1.1, 1), (470, 440, 1.2, 2), (130, 470, 0.9, 3), (520, 130, 0.8, 4)):
        out.append(ruyi_cloud(D, x, y, s_, sd, pal=("#2A6A6A", "#1E5A5A", "#0A2A2E")))
    # the dragon coiling through the sky
    spine = [(560, 560), (520, 470), (420, 430), (300, 470), (180, 440), (130, 340), (200, 250), (320, 270), (380, 330)]
    svg, (hx, hy), ha = long_dragon(D, spine, 46, 5)
    out.append(svg)
    out.append(long_head(D, hx - 6, hy - 4, 1.15, ha - 40, 6))
    # the flaming pearl it chases
    px, py = 456, 240
    out.append(soft_glow(D, px, py, 120, "#FFF6D0", 0.9))
    rnd = random.Random(7)
    for k in range(10):
        a = math.radians(-90 + (k - 4.5) * 22)
        out.append(taper(catmull([(px + math.cos(a) * 20, py + math.sin(a) * 20), (px + math.cos(a) * 34 + rnd.uniform(-4, 4), py + math.sin(a) * 34 - 6), (px + math.cos(a) * 46, py + math.sin(a) * 44 - 16)], 5), 7, 1, rnd.choice(["#FF8A3A", "#FFC84A", "#E8402A"]), 0.9))
    out.append(f'<circle cx="{px}" cy="{py}" r="22" fill="{D.rad([(0, "#FFFFFF"), (0.6, "#F2F6FF"), (1, "#B8C8E8")], cx=0.4, cy=0.35)}" stroke="#E8D8B0" stroke-width="1.6"/>')
    out.append(f'<path d="M {px - 10} {py - 6} q 6 -8 14 -6" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # front clouds
    for (x, y, s_, sd) in ((380, 520, 1.0, 5), (60, 300, 0.8, 6)):
        out.append(ruyi_cloud(D, x, y, s_, sd))
    # lettering
    out.append(gilt(D, 300, 104, "The Dragon’s Pearl", SERIF_IT, 58, max_w=440, seed=8, deboss="#000000", dop=0.85))
    out.append(tx(300, 134, "CHINESE · CHASING THE FLAMING PEARL OF WISDOM", CINZEL, 15, "#E8F6F0", ls=2, max_w=440))
    return fin(D, out, 35)


# ================================================================ 23. the moon rabbit — pounding the elixir of life
def rabbit_pounding(D, x, y, s, seed, flip=False):
    """The jade rabbit standing up on its hind legs with a long pestle over a mortar (facing left)."""
    def L(pts):
        return T(pts, x, y, s, flip)
    pal = ("#FFFFFF", "#EEEAF2", "#A8A0B8")
    out = []
    # mortar
    mort = L([(-74, -38), (-30, -38), (-34, -20), (-40, 0), (-64, 0), (-70, -20)])
    out.append(painted(D, mort, ("#C8B8A0", "#8A7A68", "#3A3028"), seed + 9, sk=0.2, angle=-90, n=8, inkw=1.4, inkc="#2A2018", hi=0.4))
    out.append(f'<path d="{blob(*L([(-52, -38)])[0], 22 * s, 5 * s, seed, 0.05, 12)}" fill="#3A3028"/>')
    out.append(f'<path d="{blob(*L([(-52, -39)])[0], 16 * s, 3 * s, seed + 1, 0.05, 12)}" fill="#F2F6E8"/>')
    # hind leg and foot
    out.append(painted(D, L([(-10, -2), (24, -2), (30, -14), (20, -34), (0, -30)]), pal, seed + 2, sk=0.2, n=6, inkw=1.2, inkc="#4A4258", hi=0.4))
    body = L([(-14, -20), (-22, -50), (-18, -76), (-8, -90), (10, -88), (22, -70), (26, -44), (22, -20), (8, -10)])
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.5), sk=0.2, angle=-90, n=16, inkw=1.4, inkc="#4A4258", hi=0.4))
    out.append(f'<path d="{blob(*L([(28, -30)])[0], 9 * s, 8 * s, seed + 3, 0.15, 10)}" fill="#FFFFFF"/>')
    head = L([(-26, -92), (-30, -102), (-22, -114), (-6, -116), (4, -106), (2, -94), (-10, -88)])
    out.append(painted(D, head, pal, seed + 4, sdir=(0.5, 0.5), sk=0.15, n=6, inkw=1.4, inkc="#4A4258", hi=0.5))
    for k, (a0, a1) in enumerate((((-10, -112), (-4, -160)), ((-2, -110), (12, -154)))):
        ear = L([(a0[0] - 4, a0[1]), ((a0[0] + a1[0]) / 2 - 6, (a0[1] + a1[1]) / 2), a1, ((a0[0] + a1[0]) / 2 + 6, (a0[1] + a1[1]) / 2), (a0[0] + 4, a0[1])])
        out.append(painted(D, ear, pal, seed + 5 + k, sk=0.15, n=4, inkw=1.2, inkc="#4A4258", hi=0.4))
        out.append(poly(L([(a0[0], a0[1] - 4), ((a0[0] + a1[0]) / 2 - 2, (a0[1] + a1[1]) / 2), (a1[0], a1[1] + 8), ((a0[0] + a1[0]) / 2 + 2, (a0[1] + a1[1]) / 2)]), "#F2C8D0", 0.8))
    ex, ey = L([(-16, -104)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="#C8302A"/><circle cx="{ex - 0.5:.1f}" cy="{ey - 0.6:.1f}" r="{0.8 * s:.1f}" fill="#FFFFFF"/>')
    out.append(f'<circle cx="{L([(-29, -100)])[0][0]:.1f}" cy="{L([(-29, -100)])[0][1]:.1f}" r="{1.6 * s:.1f}" fill="#E8A0B0"/>')
    # the pestle held in both paws, raised
    p0, p1 = L([(-48, -40), (-10, -132)])
    out.append(taper([p0, p1], 7 * s, 6 * s, "#8A5A2A"))
    out.append(taper([(p0[0] - 1, p0[1]), (p1[0] - 1, p1[1])], 2 * s, 2 * s, "#C8925A", 0.7))
    for (ax, ay) in ((-22, -70), (-18, -84)):
        out.append(f'<path d="{blob(*L([(ax, ay)])[0], 6 * s, 4.6 * s, int(ax), 0.1, 8)}" fill="#FFFFFF" stroke="#4A4258" stroke-width="1"/>')
    return "".join(out)


@design("the-moon-rabbit")
def the_moon_rabbit():
    D = Doc2("my-mr")
    out = [sky(D, [(0, "#0E0A2A"), (0.5, "#1E1A48"), (1, "#3A2A5A")], 1, 600, ["#2A2A5A", "#06041A", "#4A3A6A"], 60)]
    out.append(stars_field(4, (0, 0, 600, 600), 120))
    cx, cy, R = 300, 300, 176
    out.append(soft_glow(D, cx, cy, R * 1.8, "#FFF2C8", 0.5))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{D.rad([(0, "#FFFDF0"), (0.7, "#F8EED0"), (1, "#E8D8A8")], cx=0.42, cy=0.38)}"/>')
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{R}"/>')
    sc = []
    rnd = random.Random(4)
    for k in range(14):
        sc.append(f'<path d="{blob(cx + rnd.uniform(-R, R), cy + rnd.uniform(-R, R), rnd.uniform(20, 60), rnd.uniform(14, 40), k, 0.2, 12)}" fill="#D8C8A0" opacity="0.3"/>')
    sc.append(strokes(D.nid(), f"M {cx - R} {cy - R} L {cx + R} {cy - R} L {cx + R} {cy + R} L {cx - R} {cy + R} Z", (cx - R, cy - R, cx + R, cy + R), ["#FFFFFF", "#E8D8A8"], 5, n=60, angle=-20, length=(20, 60), width=(2, 6), opacity=(0.1, 0.3)))
    # on the moon: the cassia tree, the ground, the rabbit at its mortar
    sc.append(painted(D, [(cx - R, cy + 110), (cx - 60, cy + 92), (cx + 40, cy + 100), (cx + R, cy + 86), (cx + R, cy + R), (cx - R, cy + R)], ("#E8D8B0", "#C8B488", "#8A7A58"), 6, sk=0.1, angle=0, n=20, inkw=1.2, inkc="#8A7A58", hi=0.2))
    tx_, tb = cx + 92, cy + 96
    sc.append(taper(catmull([(tx_, tb), (tx_ - 6, tb - 60), (tx_ + 4, tb - 120)], 6), 14, 6, "#8A6A4A"))
    for (a, L_) in ((-150, 60), (-40, 50), (-100, 40)):
        sc.append(taper(catmull([(tx_ + 2, tb - 90), (tx_ + math.cos(math.radians(a)) * L_ * 0.6, tb - 100 + math.sin(math.radians(a)) * L_ * 0.5), (tx_ + math.cos(math.radians(a)) * L_, tb - 110 + math.sin(math.radians(a)) * L_ * 0.6)], 5), 6, 2, "#8A6A4A"))
    sc.append(dab_crown(D, tx_ - 4, tb - 150, 70, 44, [("#B8C8A0", "#8AA07A", "#4A6A4A")], 9, n=70, size=(5, 9), light=(-0.6, -0.8), inkw=0))
    for k in range(30):
        sc.append(f'<circle cx="{tx_ - 4 + rnd.uniform(-60, 60):.1f}" cy="{tb - 150 + rnd.uniform(-36, 36):.1f}" r="2" fill="#F2B83A"/>')
    sc.append(cast(D, cx - 40, cy + 100, 70, 8, "#8A7A58", 0.4, 3))
    sc.append(rabbit_pounding(D, cx - 10, cy + 100, 1.2, 7))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#FFF6D8" stroke-width="2" opacity="0.6"/>')
    # drifting night clouds across the moon's foot, and hanging lanterns
    for (x, y, s_, sd) in ((120, 470, 1.0, 1), (480, 450, 0.9, 2)):
        out.append(ruyi_cloud(D, x, y, s_, sd, pal=("#4A3A7A", "#3A2A6A", "#1A1240")))
    for (lx, ly, h) in ((90, 150, 60), (510, 170, 80)):
        out.append(f'<path d="M {lx} 0 L {lx} {ly - 22}" stroke="#2A1A2A" stroke-width="1.6"/>')
        out.append(soft_glow(D, lx, ly, 50, "#FF8A4A", 0.6))
        out.append(painted(D, blob_pts(lx, ly, 20, 24, lx, 0.04, 18), ("#FF8A6A", "#D8282A", "#7A0A10"), lx, sdir=(0.4, 0.4), sk=0.2, angle=-90, n=10, inkw=1.2, inkc="#4A0408", hi=0.5))
        for k in range(3):
            out.append(f'<path d="M {lx - 18 + k * 12} {ly - 20} q 4 20 0 40" stroke="#7A0A10" stroke-width="1" fill="none" opacity="0.6"/>')
        out.append(f'<rect x="{lx - 8}" y="{ly - 28}" width="16" height="6" fill="#D9A945"/><rect x="{lx - 8}" y="{ly + 22}" width="16" height="6" fill="#D9A945"/>')
        out.append(f'<path d="M {lx} {ly + 28} L {lx} {ly + 44}" stroke="#D9A945" stroke-width="2"/>')
    # osmanthus sprig in the foreground corner
    out.append(taper(catmull([(640, 560), (560, 520), (470, 500), (420, 500)], 8), 8, 2, "#4A3A2A"))
    for k in range(9):
        lx_, ly_ = catmull([(640, 560), (560, 520), (470, 500), (420, 500)], 8)[k * 2 + 4]
        out.append(leaf_simple(D, lx_, ly_, 24, 7, -150 + (k % 2) * 80, ("#7AA06A", "#3A6A3A", "#1A3A1E"), k + 40, inkw=0.8))
        for j in range(4):
            out.append(f'<circle cx="{lx_ + rnd.uniform(-8, 8):.1f}" cy="{ly_ + rnd.uniform(-8, 8):.1f}" r="2.2" fill="#F6C24A"/>')
    # lettering
    out.append(letters(D, 300, 82 + 24, "The Moon Rabbit", SERIF_IT, 62, "#FFF6E0", ["#FFFFFF", "#FFE8C0", "#F2E0FF"], 12, max_w=420,
                       shadow="#06041A", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 538, "CHINESE · POUNDING THE ELIXIR OF LIFE", CINZEL, 16, "#F2E8D8", ls=2.5, max_w=430))
    return fin(D, out, 36)


# ================================================================ 24. the churning of the ocean — samudra manthan
def turtle_shell(D, cx, cy, rx, ry, seed):
    out = [painted(D, blob_pts(cx, cy, rx, ry, seed, 0.03, 26), ("#9AB08A", "#4A6A4A", "#1A2A1A"), seed, sdir=(0.4, 0.6), sk=0.2, angle=-20, n=20, inkw=1.6, inkc="#0A140A", hi=0.45)]
    for k in range(-2, 3):
        x = cx + k * rx * 0.36
        out.append(f'<path d="{smooth_closed(ell_pts(x, cy - ry * 0.2 + abs(k) * ry * 0.12, rx * 0.16, ry * 0.32, 0, 360, 12))}" fill="none" stroke="#1A2A1A" stroke-width="1.6" opacity="0.6"/>')
    return "".join(out)


@design("the-churning-of-the-ocean")
def the_churning_of_the_ocean():
    D = Doc2("my-co")
    out = [sky(D, [(0, "#3A2A6A"), (0.4, "#C8709A"), (0.7, "#F6B88A"), (0.82, "#FCE6C0")], 1, 440, ["#7A5A9A", "#FFD8B0", "#E8909A"], 60)]
    out.append(soft_glow(D, 300, 380, 300, "#FFF0C8", 0.55))
    for (x, y, w, sd) in ((80, 240, 200, 3), (520, 220, 220, 4)):
        out.append(puff_cloud(D, x, y, w, sd, ("#FFE8E0", "#E0A8B8", "#9A6A9A"), op=0.85))
    # the ocean of milk
    out.append(sea(D, 400, 620, [(0, "#FFFAF0"), (0.5, "#F2E8E0"), (1, "#C8B8C8")], 5, ["#FFFFFF", "#D8C8D0", "#FFF6E8"], 80))
    # the great turtle beneath, the mountain churning-rod upon its back
    out.append(turtle_shell(D, 300, 452, 120, 34, 6))
    for sg in (-1, 1):
        out.append(f'<path d="{blob(300 + sg * 128, 456, 20, 9, 7 + sg, 0.1, 10, sg * 20)}" fill="#4A6A4A"/>')
    mt = [(250, 440), (258, 380), (262, 300), (270, 230), (286, 176), (300, 160), (316, 176), (330, 230), (338, 300), (342, 380), (350, 440)]
    out.append(painted(D, mt, ("#B8A0C8", "#6A5A80", "#2A1E3A"), 8, sdir=(0.7, 0.2), sk=0.25, angle=-90, n=60, inkw=1.6, inkc="#140A1E", hi=0.0))
    out.append(ink(smooth_open(mt[:6]), "#FFE8D0", 3, 3, 1, 0.75))
    for k in range(6):
        out.append(conifer(272 + k * 10, 236 + (k % 3) * 40 + k * 18, 16 + (k % 2) * 6, "#2A3A2A", k, width=0.4))
    # Vasuki, the serpent-king, wound around the mountain as the churning rope, its ends running off to either side
    vp = ("#8AC0A0", "#2A7A5A", "#0A3A2A")
    for k, y in enumerate((260, 320, 380)):
        out.append(snake(D, [(250, y + 16), (300, y + 30), (352, y + 18)], 22, 22, vp, 10 + k, head=False))
    out.append(snake(D, [(254, 274), (180, 300), (90, 330), (-10, 350)], 22, 18, vp, 13, head=False))
    out.append(snake(D, [(346, 394), (420, 370), (520, 340), (640, 320)], 22, 18, vp, 14, head=False))
    for k in range(5):
        out.append(f'<path d="M {120 + k * 30} {320 + k * -6} l 6 6" stroke="#F2F6D8" stroke-width="2" opacity="0.6"/>')
    # foam churned up in great swirls
    rnd = random.Random(9)
    for k in range(5):
        r = 140 + k * 26
        out.append(f'<path d="{smooth_open(ell_pts(300, 450, r, r * 0.16, 200, 340, 20))}" fill="none" stroke="#FFFFFF" stroke-width="{4 - k * 0.5:.1f}" opacity="0.8"/>')
    for k in range(60):
        out.append(f'<circle cx="{rnd.uniform(60, 540):.1f}" cy="{rnd.uniform(420, 500):.1f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    # the treasures rising from the milk: the crescent moon, a lotus, and the golden pot of amrita
    out.append(soft_glow(D, 120, 210, 60, "#FFFFFF", 0.6))
    out.append(f'<path d="M 110 186 A 26 26 0 1 0 138 236 A 20 20 0 1 1 110 186 Z" fill="#FFFDF0"/>')
    lx, ly = 470, 470
    for k in range(8):
        a = math.radians(-180 + k * 25.7)
        out.append(f'<path d="{blob(lx + math.cos(a) * 16, ly - 10 + math.sin(a) * 14, 15, 6, k, 0.05, 10, math.degrees(a))}" fill="{("#F6A8C0", "#FFD0DC")[k % 2]}"/>')
    out.append(f'<circle cx="{lx}" cy="{ly - 12}" r="6" fill="#F6C84A"/>')
    kx, ky = 136, 486
    out.append(soft_glow(D, kx, ky - 30, 80, "#FFE070", 0.8))
    pot = [(kx - 22, ky - 30), (kx - 26, ky - 10), (kx - 18, ky + 6), (kx + 18, ky + 6), (kx + 26, ky - 10), (kx + 22, ky - 30), (kx + 10, ky - 40), (kx - 10, ky - 40)]
    out.append(painted(D, pot, GOLD, 12, sk=0.2, n=10, inkw=1.4, inkc="#5A3A08", hi=0.5))
    out.append(painted(D, [(kx - 10, ky - 40), (kx + 10, ky - 40), (kx + 14, ky - 50), (kx - 14, ky - 50)], GOLD, 13, sk=0.2, n=4, inkw=1.2, inkc="#5A3A08", hi=0.5))
    for k in range(5):
        a = math.radians(-150 + k * 30)
        out.append(f'<path d="{blob(kx + math.cos(a) * 10, ky - 56 + math.sin(a) * 8, 8, 3.6, k, 0.05, 8, math.degrees(a))}" fill="#4A8A4A"/>')
    for k in range(10):
        out.append(sparkle(kx + rnd.uniform(-40, 40), ky - 40 + rnd.uniform(-40, 30), rnd.uniform(2, 4), "#FFFFFF", 0.9))
    # lettering
    out.append(gilt(D, 300, 100, "The Churning of the Ocean", SERIF_IT, 48, max_w=460, seed=15, deboss="#1A0A2A", dop=0.75))
    out.append(tx(300, 130, "HINDU · SAMUDRA MANTHAN, THE OCEAN OF MILK", CINZEL, 15, "#FFF6EE", ls=2, max_w=430))
    out.append(tx(300, 538, "From the churning came the nectar of life", SERIF_IT, 24, "#5A3A6A", max_w=440))
    return fin(D, out, 37)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
