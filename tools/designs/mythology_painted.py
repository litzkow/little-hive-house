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
                            ridge, shift, sky, soft_glow, specks, taper, catmull, mist, glow_window, smoke)
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea, palm
from paint import conifer, rough
import holidays_gouache as hg
from storybook_classics_painted import T, ell_pts, pd, tx, gilt, gilt_fill, stars_field, flourish, laurel, leaf_simple, bird_v, star4
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
    for (dx, dy, rx, ry) in ((-0.42, 0.02, 0.3, 0.46), (-0.08, -0.36, 0.24, 0.16), (0.24, -0.26, 0.15, 0.13), (0.34, 0.02, 0.17, 0.15), (0.06, 0.4, 0.2, 0.11), (-0.1, 0.08, 0.1, 0.08)):
        mar.append(f'<path d="{blob(cx + dx * r, cy + dy * r, rx * r, ry * r, rnd.randint(0, 999), 0.35, 16)}" fill="{pal[2]}" opacity="0.2"/>')
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
    out.append(tx(300, 134, "GREEK · SEEN ONLY IN THE SHIELD", CINZEL, 17, "#DCEAD0", ls=2.5, max_w=440))
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
    out.append(tx(300, 536, "GREEK · FOLLOW ARIADNE’S THREAD", CINZEL, 17, "#F2D8B0", ls=2.5, max_w=440))
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
    out.append(tx(300, 134, "GREEK · AT THE GATES OF HADES", CINZEL, 17, "#E8D8F2", ls=2, max_w=440))
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
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{9.6 * s:.1f}" fill="#3A2410"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{7.6 * s:.1f}" fill="{D.rad([(0, "#FFF6A0"), (0.6, "#F2C81C"), (1, "#C8901A")], cx=0.45, cy=0.4)}"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.4 * s:.1f}" fill="#0A0604"/>')
        out.append(f'<path d="M {ex - 8 * s:.1f} {ey - 4 * s:.1f} Q {ex:.1f} {ey - 10 * s:.1f} {ex + 8 * s:.1f} {ey - 4 * s:.1f}" stroke="#4A3018" stroke-width="{2.4 * s:.1f}" fill="none" opacity="0.7"/>')
        out.append(f'<circle cx="{ex - 2 * s:.1f}" cy="{ey - 2.2 * s:.1f}" r="{1.2 * s:.1f}" fill="#FFFFFF"/>')
    out.append(sharp(L([(-4, -54), (4, -54), (0, -42)]), "#C8B070"))
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
    out.append(tx(300, 540, "GREEK · WISDOM SEES IN THE DARK", CINZEL, 17, "#DCE4F8", ls=2.5, max_w=440))
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
    out.append(tx(300, 140, "NORSE · THOUGHT AND MEMORY", CINZEL, 17, "#1A2034", ls=2.5, max_w=440))
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
    out.append(tx(300, 540, "EGYPTIAN · SAILING THE NIGHT", CINZEL, 17, "#F6E2B0", ls=2.5, max_w=440))
    return fin(D, out, 19)


# ================================================================ horses and sea-horses
HORSE_BODY = [(-168, -6), (-162, 2), (-150, 4), (-134, -2), (-118, -12), (-100, 4), (-84, 30), (-72, 48), (-40, 60), (10, 58), (50, 54), (76, 42),
              (98, 16), (100, -4), (86, -18), (40, -20), (0, -18), (-40, -30), (-80, -48), (-110, -60), (-116, -76), (-106, -62), (-124, -50),
              (-146, -30), (-164, -16)]


def leg(D, root, knee, fet, hoof_dir, s, col, rim=None, hoof="#1A1410", w=(20, 9)):
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
        for k in range(30):
            px, py = L([(rnd.uniform(-60, 90), rnd.uniform(-16, 50))])[0]
            dd.append(f'<path d="{blob(px, py, rnd.uniform(3, 6) * s, rnd.uniform(2.5, 5) * s, k, 0.2, 10)}" fill="{pal[2]}" opacity="0.18"/>')
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
    ex, ey = L([(-130, -40)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.8 * s:.1f}" fill="#141418"/><circle cx="{ex - 0.6:.1f}" cy="{ey - 0.8:.1f}" r="{1 * s:.1f}" fill="#FFFFFF"/>')
    nx, ny = L([(-161, -10)])[0]
    out.append(f'<path d="{blob(nx, ny, 2.6 * s, 1.8 * s, 2, 0.1, 8)}" fill="{pal[2]}"/>')
    for root, knee, fet, hd, _ in near:
        r_, k_, f_ = L([root, knee, fet])
        hd_ = (hd[0] * s * (-1 if flip else 1), hd[1] * s)
        out.append(leg(D, r_, k_, f_, hd_, s, pal[1], rim=pal[0]))
    if rim:
        out.append(ink(smooth_open(L([(-164, -16), (-146, -30), (-124, -50), (-110, -60), (-80, -48), (-40, -30), (0, -18), (40, -20), (86, -18), (100, -4)])), rim, 2.2 * s, seed, 1, 0.75))
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
    ps = 1.4
    fy = 504

    def P(pts):
        return T(pts, fx, fy, ps, True)
    cloak = P([(-22, -124), (22, -124), (0, -118), (-30, -104), (-70, -96), (-110, -70), (-124, -40), (-96, -48), (-80, -20), (-50, -46), (-30, -60), (-24, -90)])
    out.append(painted(D, cloak, ("#8A3A2A", "#4A1814", "#140606"), 4, sdir=(-0.4, 0.6), sk=0.2, angle=10, n=20, inkw=1.2, inkc="#0A0202", hi=0.35))
    out.append(ink(smooth_open(cloak[3:8]), "#FFB060", 1.8, 3, 1, 0.5))
    out.append(walker_back(fx, fy, ps, "#140C10", rim="#FFB060", flip=True, stride=1.2, kilt="#2A1416"))
    # the torch arm raised high: shoulder, elbow, the fist round the fennel stalk
    out.append(taper(catmull(P([(22, -120), (34, -142), (40, -170), (42, -186)]), 6), 9 * ps, 6.4 * ps, "#140C10"))
    out.append(ink(smooth_open(P([(26, -122), (37, -144), (44, -176)])), "#FFB060", 2, 5, 1, 0.9))
    out.append(f'<path d="{blob(*P([(42, -188)])[0], 6 * ps, 5.4 * ps, 3, 0.1, 10)}" fill="#140C10"/>')
    hx, hy = P([(42, -188)])[0]
    stalk_top = P([(50, -216)])[0]
    out.append(taper([P([(38, -170)])[0], (hx, hy), stalk_top], 5, 4, "#6A7A3A"))
    for k in range(3):
        a_, b_ = P([(44 + k * 3, -200 - k * 10), (40 + k * 3, -198 - k * 10)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#3A4A1A" stroke-width="2"/>')
    out.append(flame(D, stalk_top[0], stalk_top[1] + 8, 52, 3, lean=-0.2))
    for k in range(16):
        out.append(sparkle(stalk_top[0] + rnd.uniform(-40, 70), stalk_top[1] + rnd.uniform(-20, 70), rnd.uniform(1.5, 4), rnd.choice(["#FFE070", "#FFB040", "#FFFFFF"]), rnd.uniform(0.6, 1)))
    # Zeus' eagle circling above
    for (ex_, ey_, es) in ((150, 236, 1.0),):
        out.append(poly([(ex_ - 40 * es, ey_ - 4), (ex_ - 20 * es, ey_ - 14), (ex_ - 6, ey_ - 6), (ex_, ey_ - 10), (ex_ + 6, ey_ - 6), (ex_ + 20 * es, ey_ - 14), (ex_ + 42 * es, ey_ - 2),
                         (ex_ + 24 * es, ey_ - 4), (ex_ + 10, ey_ + 2), (ex_ + 4, ey_ + 12), (ex_ - 4, ey_ + 12), (ex_ - 10, ey_ + 2), (ex_ - 24 * es, ey_ - 4)], "#0A0810"))
    # lettering
    out.append(gilt(D, 300, 106, "PROMETHEUS", CINZEL, 54, ls=10, max_w=440, seed=11, deboss="#000000", dop=0.8))
    out.append(tx(300, 136, "GREEK · HE STOLE FIRE FOR US", CINZEL, 17, "#F2D8C8", ls=2.5, max_w=440))
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
        nx_, ny_ = L([(sg * 3, 33)])[0]
        out.append(f'<path d="{blob(nx_, ny_, 1.6 * s, 1 * s, seed + sg, 0.1, 8)}" fill="#5A3A08"/>')
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
    out.append(tx(300, 134, "GREEK · JASON AND THE ARGONAUTS", CINZEL, 17, "#D8F0E8", ls=2.5, max_w=440))
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


def siren_sil(D, x, y, s, seed, flip=False, col="#1E1424", rim="#FFD08A", wings="up", lyre=False):
    """A Siren perched on a crag in silhouette against the sunset, as on Greek vases: a bird's body, raised
    fingered wings and tail, a woman's head in profile with long hair down her back (facing left)."""
    def L(pts):
        return T(pts, x, y, s, flip)
    rnd = random.Random(seed)
    out = []
    # wings
    if wings == "up":
        wing = [(4, -48), (2, -76), (12, -104), (24, -124), (28, -110), (36, -118), (38, -100), (48, -104), (44, -86), (52, -84), (36, -62), (22, -42)]
    else:
        wing = [(2, -46), (20, -60), (44, -66), (62, -60), (52, -54), (64, -48), (48, -44), (56, -36), (34, -34), (18, -30)]
    out.append(poly(L(wing), col))
    body = L([(-10, -8), (-15, -24), (-13, -40), (-7, -52), (6, -52), (15, -40), (21, -22), (34, 2), (26, 6), (18, 0), (10, -4)])
    out.append(poly(body, col))
    # legs gripping the rock
    for dx in (-4, 4):
        a_, b_ = L([(dx, -6), (dx - 2, 2)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{col}" stroke-width="{2.6 * s:.1f}" stroke-linecap="round"/>')
    # a woman's head in clear profile, hair bound up and falling down her back
    head = L([(-6, -82), (-12, -81), (-16, -76), (-17, -72), (-21, -68), (-17.5, -66), (-19, -63), (-16.5, -61), (-15.5, -57), (-10, -54), (-3, -54), (3, -60), (5, -71), (1, -79)])
    out.append(sharp(head, col))
    out.append(poly(L([(-4, -82), (6, -78), (12, -66), (16, -50), (19, -34), (10, -38), (3, -54), (-2, -60)]), col))
    out.append(f'<path d="{blob(*L([(4, -82)])[0], 5.4 * s, 4.6 * s, seed, 0.1, 10)}" fill="{col}"/>')
    if lyre:
        lx, ly = L([(-24, -38)])[0]
        sg = -1 if flip else 1
        for k in (-1, 1):
            out.append(taper(catmull([(lx + k * 6 * s, ly + 6 * s), (lx + k * 9 * s, ly - 6 * s), (lx + k * 7 * s, ly - 16 * s)], 5), 2.4 * s, 1.4 * s, "#E8B860"))
        out.append(f'<path d="M {lx - 7 * s:.1f} {ly - 14 * s:.1f} L {lx + 7 * s:.1f} {ly - 14 * s:.1f}" stroke="#E8B860" stroke-width="{1.8 * s:.1f}"/>')
        for k in range(4):
            out.append(f'<path d="M {lx - 4.5 * s + k * 3 * s:.1f} {ly + 5 * s:.1f} L {lx - 4.5 * s + k * 3 * s:.1f} {ly - 14 * s:.1f}" stroke="#FFE8B0" stroke-width="0.9"/>')
        out.append(f'<path d="{blob(lx, ly + 6 * s, 7 * s, 4 * s, seed, 0.05, 10)}" fill="#C8902A"/>')
    # rim light from the low sun behind
    out.append(ink(smooth_open(L(wing[1:9])), rim, 1.8 * s, seed, 1, 0.85))
    out.append(ink(smooth_open(L([(-12, -81), (-6, -82), (4, -86), (8, -80), (12, -66), (16, -50), (21, -22), (34, 2)])), rim, 1.6 * s, seed + 1, 1, 0.75))
    out.append(pline(L([(-16, -76), (-17, -72), (-21, -68), (-17.5, -66), (-19, -63), (-16.5, -61), (-15.5, -57)]), rim, 1.3 * s, seed + 2, 0.8, 1))
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
    out.append(siren_sil(D, 420, 286, 1.05, 1, wings="up"))
    out.append(siren_sil(D, 500, 254, 1.2, 2, wings="side", lyre=True))
    out.append(siren_sil(D, 568, 306, 0.95, 3, wings="up"))
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
    out.append(tx(301.5, 143.5, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#2A1A3A", ls=2.5, max_w=440, op=0.6))
    out.append(tx(300, 142, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#FFF2E0", ls=2.5, max_w=440))
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
    out.append(tx(cx + 1.5, 534, "GREEK · LORD OF THE SEA", CINZEL, 17, "#04202A", ls=2, max_w=440, op=0.6))
    out.append(tx(cx, 532, "GREEK · LORD OF THE SEA", CINZEL, 17, "#F2FFF6", ls=2, max_w=440))
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
    # the flying gallop of the old image stones: four legs reaching forward, four streaming back, in pairs
    legs = [((-60, 46), (-98, 52), (-134, 36), (-14, 2), "far"), ((-52, 48), (-88, 62), (-124, 54), (-14, 4), "far"),
            ((62, 44), (96, 58), (134, 62), (14, 4), "far"), ((54, 48), (86, 68), (122, 80), (14, 6), "far"),
            ((-70, 50), (-110, 58), (-148, 46), (-14, 4), "near"), ((-60, 54), (-98, 70), (-136, 66), (-14, 6), "near"),
            ((72, 46), (108, 62), (148, 68), (14, 4), "near"), ((62, 50), (96, 74), (134, 88), (14, 6), "near")]
    hx, hy = 322, 312
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
    out.append(taper([(rx + 60, ry + 6), (rx - 40, ry - 56), (rx - 104, ry - 96)], 3.2, 2.6, "#C8B890"))
    out.append(sharp([(rx - 100, ry - 88), (rx - 124, ry - 108), (rx - 106, ry - 98)], "#E8ECF2"))
    out.append(taper([(rx - 14, ry - 50), (rx - 40, ry - 52), (rx - 52, ry - 66)], 7, 5, "#0E1428"))
    out.append(ink(smooth_open([(rx + 8, ry - 70), (rx + 16, ry - 40), (rx + 14, ry + 10)]), "#E8FFF4", 1.6, 3, 1, 0.7))
    # lettering
    out.append(letters(D, 300, 124, "Sleipnir", DMS, 92, "#F2FFF8", ["#FFFFFF", "#C8F0E0", "#E8F0FF"], 14, max_w=380,
                       shadow="#04081A", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(301.5, 161.5, "NORSE · ODIN’S EIGHT-LEGGED STEED", CINZEL, 17, "#000000", ls=2.5, max_w=440, op=0.6))
    out.append(tx(300, 160, "NORSE · ODIN’S EIGHT-LEGGED STEED", CINZEL, 17, "#E0FFF2", ls=2.5, max_w=440))
    out.append(tx(300, 540, "“Of all horses, Sleipnir is the best.”", SERIF_IT, 25, "#1A2444", max_w=430))
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
    out.append(letters(D, 312, 504, "Bifröst", SERIF_IT, 80, "#FFFFFF", ["#FFFFFF", "#FFE8D8", "#E8E8FF"], 15, max_w=300,
                       shadow="#0A1010", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(301.5, 543.5, "NORSE · THE BRIDGE TO ASGARD", CINZEL, 17, "#000000", ls=2.5, max_w=440, op=0.5))
    out.append(tx(300, 542, "NORSE · THE BRIDGE TO ASGARD", CINZEL, 17, "#FFE8D0", ls=2.5, max_w=440))
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
    # Thor from behind, braced in the car: red cloak and red hair and beard streaming back, reins in his fists
    tx_, tb = cx_ + 10, cy_ + 4
    ts = 1.2

    def Q(pts):
        return T(pts, tx_, tb, ts, True)
    cape = Q([(-22, -124), (22, -124), (0, -116), (-40, -110), (-90, -100), (-140, -84), (-160, -60), (-120, -62), (-100, -40), (-60, -60), (-28, -70), (-22, -100)])
    out.append(painted(D, cape, ("#E05A44", "#8A2018", "#2A0806"), 6, sdir=(-0.3, 0.8), sk=0.2, angle=10, n=18, inkw=1.2, inkc="#100404", hi=0.35))
    out.append(walker_back(tx_, tb, ts, "#16141C", rim="#C8D8FF", flip=True, stride=0.4))
    for (sh, el, hd) in (((22, -120), (40, -104), (58, -98)), ((-22, -118), (14, -100), (52, -94))):
        out.append(taper(catmull(Q([sh, el, hd]), 6), 11 * ts, 7.4 * ts, "#16141C"))
        out.append(f'<path d="{blob(*Q([hd])[0], 5.4 * ts, 5 * ts, 3, 0.1, 10)}" fill="#16141C"/>')
    hx_, hy_ = Q([(0, -142)])[0]
    hair = Q([(6, -152), (-6, -154), (-20, -148), (-44, -144), (-64, -136), (-46, -132), (-60, -122), (-30, -126), (-10, -128), (8, -134)])
    out.append(painted(D, hair, ("#F08A4A", "#C04A1E", "#5A1A08"), 7, sk=0.2, angle=0, n=12, inkw=1.0, inkc="#3A0A04", hi=0.4))
    for k in range(5):
        out.append(pline(Q([(0, -150 + k * 4), (-24, -146 + k * 4), (-50 - k * 3, -138 + k * 3)]), "#FFB080", 1.1, 3 + k, 0.6, 1))
    out.append(ink(smooth_open(Q([(8, -150), (12, -140), (10, -130)])), "#C8D8FF", 1.6, 4, 1, 0.8))
    # the car's front rail over his legs
    out.append(painted(D, [(cx_ - 56, cy_ - 34), (cx_ + 66, cy_ - 40), (cx_ + 78, cy_ - 4), (cx_ + 56, cy_ + 14), (cx_ - 44, cy_ + 14), (cx_ - 62, cy_ - 4)],
                       ("#C8925E", "#7A4A26", "#2A1408"), 4, sdir=(0.3, 0.8), sk=0.2, angle=0, n=20, inkw=1.6, inkc="#100804", hi=0.4))
    for k in range(5):
        out.append(f'<path d="M {cx_ - 48 + k * 27:.1f} {cy_ - 32:.1f} q 6 20 0 40" stroke="#C8963A" stroke-width="2" fill="none" opacity="0.8"/>')
    for k in range(9):
        out.append(f'<circle cx="{cx_ - 50 + k * 14:.1f}" cy="{cy_ - 30 - k * 0.6:.1f}" r="2.2" fill="#E8C070"/>')
    for k in range(2):
        out.append(pline([(cx_ - 38, cy_ - 96 + k * 6), (cx_ - 130, cy_ - 50 + k * 4), (cx_ - 214, cy_ - 60 + k * 6)], "#2A1A0E", 1.8, k, 0.9, 1))
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
    out.append(tx(300, 138, "NORSE · TANNGRISNIR & TANNGNJÓSTR", CINZEL, 17, "#E8ECFF", ls=2.5, max_w=440))
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
    out.append(tx(300, 528, "EGYPTIAN · AS LIGHT AS A FEATHER", CINZEL, 17, "#8A2A1A", ls=2, max_w=440))
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
    out.append(tx(300, 542, "EGYPTIAN · GUARDIAN OF THE HOME", CINZEL, 17, "#F6E2C0", ls=2, max_w=440))
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


def sphinx_front(D, seed):
    """The Great Sphinx seen from the front, as from the causeway at dawn: the striped nemes headdress, the calm
    weathered face with its lost nose, the chest, the long forepaws reaching toward us and the Dream Stele between
    them. Limestone lit warm from the left, eroded into horizontal strata. Absolute coordinates."""
    rnd = random.Random(seed)
    LIT = ("#FBE2B0", "#E2B47A", "#9A6A3E")
    out = []

    def strata(pts, n, op=0.35):
        x0, y0, x1, y1 = bbox(pts)
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        o = []
        for k in range(n):
            y = y0 + (y1 - y0) * (k + rnd.uniform(0.2, 0.8)) / n
            o.append(f'<path d="M {x0 - 4:.1f} {y:.1f} Q {(x0 + x1) / 2:.1f} {y + rnd.uniform(-3, 3):.1f} {x1 + 4:.1f} {y + rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#7A4A24", "#FFF0D0"])}" stroke-width="{rnd.uniform(1, 2.4):.1f}" fill="none" opacity="{op * rnd.uniform(0.5, 1):.2f}"/>')
        return f'<g {cid}>{"".join(o)}</g>'
    # the body behind: shoulders and flanks
    body = poly_pts([(186, 478), (194, 352), (226, 318), (300, 306), (374, 318), (406, 352), (414, 478)], 10, seed, 0.8)
    out.append(painted(D, body, LIT, seed, sdir=(0.8, 0.2), sk=0.3, angle=0, n=50, inkw=1.6, inkc="#4A2A12", hi=0.5))
    out.append(strata(body, 16))
    head_out = out
    out = []
    # the nemes headdress, its lappets falling to the shoulders
    nem = [(300, 176), (328, 180), (346, 196), (354, 224), (358, 254), (372, 298), (378, 322), (346, 326), (338, 300), (334, 272), (266, 272), (262, 300), (254, 326), (222, 322), (228, 298), (242, 254), (246, 224), (254, 196), (272, 180)]
    out.append(painted(D, nem, LIT, seed + 1, sdir=(0.8, 0.2), sk=0.25, angle=-90, n=40, inkw=1.6, inkc="#4A2A12", hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(nem)}"/>')
    st = []
    for k in range(18):
        y = 214 + k * 6.4
        st.append(f'<path d="M 210 {y:.1f} L 390 {y + rnd.uniform(-1, 1):.1f}" stroke="#8A5A2E" stroke-width="2.4" opacity="0.4"/>')
    for k in range(9):
        a = math.radians(-160 + k * 17.5)
        st.append(f'<path d="M 300 236 L {300 + math.cos(a) * 80:.1f} {236 + math.sin(a) * 70:.1f}" stroke="#8A5A2E" stroke-width="2" opacity="0.35"/>')
    st.append(f'<path d="M 300 160 L 420 160 L 420 340 L 300 340 Z" fill="#5A3416" opacity="0.28"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    # the face: brow band, ears, the calm eyes, the nose lost to time, full lips
    face = [(270, 214), (300, 210), (330, 214), (334, 240), (330, 262), (318, 280), (300, 288), (282, 280), (270, 262), (266, 240)]
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(300 + sg * 36, 242, 6, 12, seed + sg, 0.06, 12), LIT, seed + 5 + sg, sk=0.3, n=4, inkw=1.2, inkc="#4A2A12", hi=0.4))
    out.append(painted(D, face, ("#FFE8BC", "#E8BC84", "#A87442"), seed + 2, sdir=(0.8, 0.3), sk=0.28, angle=-90, n=24, inkw=1.6, inkc="#4A2A12", hi=0.55))
    out.append(taper([(268, 214), (300, 208), (332, 214)], 7, 7, "#C8925A"))
    out.append(pline([(268, 217), (300, 211), (332, 217)], "#6A3A18", 1.4, seed, 0.7, 1))
    for sg in (-1, 1):
        ex = 300 + sg * 14
        out.append(f'<path d="{blob(ex, 230, 12, 6, seed + sg, 0.1, 12)}" fill="#A87442" opacity="0.45"/>')
        out.append(f'<path d="{smooth_closed([(ex - 8, 236), (ex, 232), (ex + 8, 236), (ex, 239)])}" fill="#5A3416" opacity="0.75"/>')
        out.append(pline([(ex - 10, 228), (ex, 225), (ex + 10, 228)], "#8A5A2E", 1.4, seed + sg, 0.6, 1))
        out.append(f'<path d="M {ex - 9} {241} Q {ex} {246} {ex + 9} {241}" stroke="#FFF0D0" stroke-width="1.2" fill="none" opacity="0.6"/>')
    out.append(f'<path d="{blob(300, 252, 7, 10, seed, 0.25, 10)}" fill="#C8925A"/>')
    out.append(pline([(296, 244), (294, 258), (300, 262)], "#6A3A18", 1.6, seed + 3, 0.7, 1))
    out.append(f'<path d="M 288 268 Q 300 264 312 268 Q 300 274 288 268 Z" fill="#9A6236"/>')
    out.append(pline([(286, 268), (300, 270), (314, 268)], "#4A2A12", 1.4, seed + 4, 0.8, 1))
    out.append(f'<path d="{smooth_closed(face)}" fill="{D.lin([(0, "#3A1A08", 0), (0.55, "#3A1A08", 0), (1, "#3A1A08", 0.35)], 0, 0, 1, 0)}"/>')
    # shadow under the chin, and the striped front lappets lying on the chest
    out.append(f'<path d="{blob(300, 296, 26, 10, seed, 0.1, 12)}" fill="#5A3416" opacity="0.35"/>')
    for sg in (-1, 1):
        lp = [(300 + sg * 30, 270), (300 + sg * 40, 272), (300 + sg * 42, 336), (300 + sg * 30, 334)]
        out.append(painted(D, lp, LIT, seed + 7 + sg, sk=0.25, n=6, inkw=1.2, inkc="#4A2A12", hi=0.4))
        for k in range(9):
            y = 276 + k * 6.6
            out.append(f'<path d="M {300 + sg * 30:.1f} {y:.1f} L {300 + sg * 41:.1f} {y:.1f}" stroke="#8A5A2E" stroke-width="2" opacity="0.5"/>')
    head_out.append(f'<g transform="translate(300 300) scale(0.84) translate(-300 -300)">{"".join(out)}</g>')
    out = head_out
    # forepaws reaching toward us, the Dream Stele between them
    for sg in (-1, 1):
        paw = poly_pts([(300 + sg * 96, 404), (300 + sg * 40, 404), (300 + sg * 34, 488), (300 + sg * 44, 504), (300 + sg * 112, 504), (300 + sg * 122, 488)], 8, seed + 10 + sg, 0.6)
        out.append(painted(D, paw, LIT, seed + 10 + sg, sdir=(0.8, 0.2), sk=0.25, angle=-90, n=20, inkw=1.6, inkc="#4A2A12", hi=0.5))
        out.append(strata(paw, 8, 0.4))
        for k in range(4):
            tx_ = 300 + sg * (52 + k * 16)
            out.append(pline([(tx_, 492), (tx_ + sg * 2, 503)], "#6A3A18", 1.6, seed + k, 0.7, 1))
    stele = [(280, 470), (280, 432), (284, 422), (300, 416), (316, 422), (320, 432), (320, 470)]
    out.append(painted(D, stele, ("#E8C8C0", "#A88A8A", "#5A4248"), seed + 20, sk=0.25, angle=-90, n=10, inkw=1.4, inkc="#3A2228", hi=0.4))
    out.append(f'<circle cx="300" cy="428" r="3.4" fill="#C8402A"/>')
    for sg in (-1, 1):
        out.append(taper([(300 + sg * 4, 428), (300 + sg * 16, 426)], 3, 1, "#5A4248"))
    for r in range(4):
        for c in range(4):
            out.append(f'<path d="{blob(287 + c * 9, 440 + r * 7, 2.2, 1.6, r * 4 + c, 0.2, 6)}" fill="#5A4248" opacity="0.7"/>')
    return "".join(out)


@design("the-sphinx")
def the_sphinx():
    D = Doc2("my-sx")
    out = [sky(D, [(0, "#3A4A7A"), (0.38, "#B8809A"), (0.62, "#F6B87A"), (0.76, "#FCE2A0")], 1, 470, ["#7A6A9A", "#FFD8A0", "#E8A08A"], 60)]
    out.append(stars_field(5, (0, 0, 600, 120), 30))
    # dawn coming up behind the plateau: light from the left
    out.append(soft_glow(D, 120, 400, 300, "#FFE8A0", 0.7))
    out.append(ray_fan(120, 400, 50, 520, 26, "#FFF2C8", 0.1, a0=200, a1=340, seed=3))
    out.append(pyramid(D, 140, 404, 300, 200, 4, lit=("#FBD8A8", "#E8B080", "#B87A50"), shade=("#C8907A", "#A06A58", "#5A3A30")))
    out.append(pyramid(D, 470, 408, 280, 190, 5, lit=("#FBD8A8", "#E8B080", "#B87A50"), shade=("#C8907A", "#A06A58", "#5A3A30")))
    out.append(pyramid(D, 560, 412, 110, 70, 6, lit=("#FBD8A8", "#E8B080", "#B87A50"), shade=("#C8907A", "#A06A58", "#5A3A30")))
    out.append(mist(D, 404, 30, 4, "#FFE8C8", 0.55))
    d1 = ridge([(-20, 404), (120, 398), (300, 406), (460, 400), (620, 406)], 7, 4)
    out.append(hill(D, d1, 620, ("#F6D8A0", "#E0B070", "#A8703A"), 7, inkw=0, lit="#FFF2C8"))
    out.append(cast(D, 300, 500, 170, 14, "#5A2A10", 0.45, 3))
    out.append(sphinx_front(D, 9))
    # the sand of the enclosure, rippled, and the long morning shadows
    rnd = random.Random(8)
    for k in range(26):
        x = rnd.uniform(0, 600)
        y = rnd.uniform(505, 600)
        out.append(taper([(x - 24, y), (x, y - 2), (x + 24, y)], 0.6, 2.2, "#A8703A", 0.4))
    for k in range(3):
        x = 40 + k * 22
        out.append(poly([(x, 402), (x + 4, 395), (x + 10, 393), (x + 14, 397), (x + 18, 391), (x + 22, 393), (x + 20, 402)], "#6A3A3A"))
        for dx in (2, 8, 14, 20):
            out.append(f'<path d="M {x + dx} 401 l 0 7" stroke="#6A3A3A" stroke-width="1.6"/>')
    # lettering
    out.append(gilt(D, 300, 100, "The Sphinx", SERIF_IT, 70, max_w=420, seed=11, deboss="#1A1030", dop=0.75))
    out.append(tx(300, 132, "EGYPTIAN · GUARDIAN OF THE HORIZON", CINZEL, 17, "#FFFFFF", ls=2.5, max_w=440))
    out.append(tx(300, 540, "He has watched the sun rise for 4,500 years.", SERIF_IT, 23, "#5A2A14", max_w=440))
    return fin(D, out, 29)


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
    out.append(tx(301.5, 537.5, "GREEK & EGYPTIAN · REBORN IN FIRE", CINZEL, 17, "#3A0A10", ls=2, max_w=440, op=0.6))
    out.append(tx(300, 536, "GREEK & EGYPTIAN · REBORN IN FIRE", CINZEL, 17, "#FFF2D8", ls=2, max_w=440))
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


def she_wolf(D, x, y, s, seed, pal=("#B8A898", "#6A5A50", "#241A14"), rim="#FFD8A0", head_ang=-16):
    """A she-wolf standing in profile (facing left), long-legged and lean, head lowered tenderly. (x, y) =
    ground under the body; about 230*s long."""
    def L(pts):
        return T(pts, x, y, s)
    piv = (-56, -86)

    def Hd(pts):
        return T([(px - piv[0], py - piv[1]) for px, py in pts], piv[0], piv[1], 1.0, False, head_ang)
    rnd = random.Random(seed)
    out = []
    far = dk(pal[1], 0.3)
    # far legs
    out.append(taper(catmull(L([(-30, -66), (-29, -44), (-27, -12), (-30, -1)]), 6), 12 * s, 7 * s, far))
    out.append(taper(catmull(L([(40, -62), (28, -40), (46, -20), (42, -1)]), 6), 14 * s, 7 * s, far))
    # tail
    tail = catmull(L([(60, -86), (78, -76), (88, -52), (84, -26)]), 8)
    out.append(taper(tail, 18 * s, 10 * s, pal[1]))
    head = Hd([(-50, -94), (-62, -98), (-66, -100), (-74, -122), (-80, -102), (-86, -98), (-94, -92), (-106, -86), (-118, -80), (-120, -75), (-112, -71),
               (-100, -70), (-86, -68), (-70, -64)])
    body = [(-48, -94), (-28, -94), (10, -88), (50, -91), (64, -86), (68, -76), (68, -58), (58, -46), (44, -50), (10, -44), (-28, -46), (-48, -56), (-62, -62)]
    outline = L(body + head)
    out.append(painted(D, outline, pal, seed, sdir=(-0.3, 0.8), sk=0.22, angle=-6, n=50, inkw=1.4, inkc="#140C06", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(outline)}"/>')
    fur = []
    for k in range(120):
        px, py = rnd.uniform(-118, 68), rnd.uniform(-120, -44)
        X, Y = L([(px, py)])[0]
        a = math.radians(rnd.uniform(60, 80))
        ln = rnd.uniform(5, 10) * s
        fur.append(f'<path d="M {X:.1f} {Y:.1f} l {math.cos(a) * ln:.1f} {math.sin(a) * ln:.1f}" stroke="{rnd.choice([pal[0], pal[2], pal[1]])}" stroke-width="{rnd.uniform(1, 1.8) * s:.1f}" stroke-linecap="round" opacity="0.5"/>')
    # darker saddle along the back, pale belly and throat
    fur.append(f'<path d="{smooth_closed(L([(-50, -96), (-20, -96), (20, -90), (60, -94), (60, -80), (20, -78), (-20, -82), (-50, -84)]))}" fill="{pal[2]}" opacity="0.35"/>')
    fur.append(f'<path d="{smooth_closed(L([(-50, -58), (-20, -48), (20, -46), (50, -50), (40, -58), (0, -54), (-40, -64)]))}" fill="#F2E6D6" opacity="0.4"/>')
    fur.append(f'<path d="{smooth_closed(L(Hd([(-112, -71), (-96, -70), (-80, -68), (-66, -62), (-58, -64), (-74, -72), (-96, -76)])))}" fill="#F2E6D6" opacity="0.55"/>')
    # shoulder and haunch masses
    fur.append(pline(L([(-38, -90), (-30, -74), (-34, -56)]), pal[2], 1.8 * s, seed, 0.5, 1))
    fur.append(pline(L([(40, -86), (30, -70), (38, -52)]), pal[2], 1.8 * s, seed + 1, 0.5, 1))
    out.append(f'<g {cid}>{"".join(fur)}</g>')
    # near legs: foreleg straight, hind leg with its hock
    for pts in (((-42, -70), (-43, -44), (-45, -12), (-50, -1)), ((50, -66), (38, -40), (58, -20), (54, -1))):
        out.append(taper(catmull(L(list(pts)), 6), 15 * s, 8 * s, pal[1]))
        out.append(taper(catmull(L([(px - 2, py) for px, py in pts]), 6), 4 * s, 2 * s, pal[0], 0.5))
        fx_, fy_ = L([pts[-1]])[0]
        out.append(f'<path d="{blob(fx_ - 3 * s, fy_ - 2 * s, 7 * s, 3.4 * s, int(fx_), 0.1, 8)}" fill="{pal[2]}"/>')
    # eye, nose, mouth line, inner ear
    ex, ey = L(Hd([(-92, -88)]))[0]
    out.append(f'<path d="{blob(ex, ey, 3.4 * s, 1.8 * s, seed, 0.05, 8, head_ang - 8)}" fill="#E8B84A"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.3 * s:.1f}" fill="#1A0A04"/>')
    nx_, ny_ = L(Hd([(-118, -77)]))[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{3 * s:.1f}" fill="#140A06"/>')
    out.append(pline(L(Hd([(-114, -72), (-100, -71), (-92, -72)])), "#140A06", 1.2 * s, seed, 0.7, 1))
    out.append(poly(L(Hd([(-70, -102), (-74, -116), (-78, -102)])), pal[2], 0.8))
    if rim:
        out.append(ink(smooth_open(L(Hd([(-80, -102), (-74, -122), (-66, -100), (-62, -98)]) + [(-48, -94), (-28, -94), (10, -88), (50, -91), (64, -86)])), rim, 2.2 * s, seed, 1, 0.85))
        out.append(ink(smooth_open(tail[:10]), rim, 1.6 * s, seed + 1, 1, 0.6))
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
    out.append(she_wolf(D, 352, 488, 1.32, 8, rim="#FFD8A0"))
    out.append(baby_in_basket(D, 222, 474, 1.12, 9))
    # lettering
    out.append(multi(300, 108, [("Romulus ", "#2A1A3A"), ("&", "#A8302A"), (" Remus", "#2A1A3A")], DMS, 62, max_w=440, shadow="#FFF2D8", sdy=2.5))
    out.append(tx(300, 140, "ROMAN · THE SHE-WOLF OF THE TIBER", CINZEL, 17, "#2A1A3A", ls=2.5, max_w=440))
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


def selkie_woman(D, x, base, s, seed):
    """The seal wife standing on the rock, seen from behind, looking out to sea: a long pale gown lifting in the
    wind, her long dark hair streaming toward the water, silvered by the moon. ~150*s tall."""
    def L(pts):
        return T(pts, x, base, s)
    rnd = random.Random(seed)
    out = []
    dress = L([(-7, -128), (-15, -122), (-16, -112), (-12, -96), (-10, -86), (-14, -70), (-18, -40), (-22, -10), (-24, 0), (10, 2), (36, 0), (48, -6),
               (34, -14), (24, -40), (16, -70), (12, -86), (14, -96), (16, -112), (15, -122), (7, -128)])
    out.append(painted(D, dress, ("#C8D0EA", "#7A84AA", "#2A3050"), seed, sdir=(-0.6, 0.3), sk=0.25, angle=-80, n=30, inkw=1.4, inkc="#0A0C1A", hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(dress)}"/>')
    folds = "".join(pline(L([(-6 + k * 8, -70), (-4 + k * 10, -36), (k * 12, -2)]), "#3A4266", 1.4 * s, seed + k, 0.5, 1) for k in range(4))
    out.append(f'<g {cid}>{folds}</g>')
    for (pts, w0) in ((((-15, -118), (-19, -96), (-17, -76)), 6), (((15, -118), (19, -96), (18, -78)), 6)):
        out.append(taper(catmull(L(list(pts)), 5), w0 * s, 4.4 * s, "#6A7498"))
    hx, hy = L([(0, -138)])[0]
    out.append(f'<path d="{blob(hx, hy, 8.6 * s, 10 * s, seed, 0.05, 12)}" fill="#14182A"/>')
    hair = L([(-9, -142), (-11, -124), (-9, -104), (-2, -90), (10, -92), (28, -100), (54, -104), (40, -110), (22, -118), (10, -134), (2, -148), (-6, -147)])
    out.append(painted(D, hair, ("#3A4060", "#14182A", "#05060E"), seed + 2, sdir=(-0.5, 0.5), sk=0.2, angle=-60, n=20, inkw=1.2, inkc="#05060E", hi=0.3))
    for k in range(9):
        t = rnd.uniform(0, 1)
        out.append(pline(L([(-6 + 4 * t, -140 + 10 * t), (4 + 10 * t, -116 + 6 * t), (24 + 24 * t, -104 - 4 * t)]), "#C8D4F0", 1.1 * s, seed + k, 0.55, 1))
    out.append(ink(smooth_open(L([(2, -148), (10, -134), (22, -118), (40, -110), (54, -104)])), "#E8F0FF", 1.8 * s, seed, 1, 0.9))
    out.append(ink(smooth_open(L([(16, -112), (14, -96), (12, -86), (16, -70), (24, -40), (34, -14), (48, -6)])), "#F2F6FF", 2 * s, seed + 1, 1, 0.85))
    return "".join(out)


def seal_lying(D, x, y, s, seed, flip=False, pal=("#B8C4D4", "#6A7488", "#1E2432")):
    """A grey seal hauled out on a rock, lying on its belly with head raised (facing left). (x, y) = belly."""
    def L(pts):
        return T(pts, x, y, s, flip)
    body = L([(-62, -40), (-70, -46), (-80, -44), (-86, -38), (-82, -32), (-70, -30), (-56, -22), (-30, -24), (0, -22), (30, -16), (54, -10), (64, -6),
              (60, 0), (30, 2), (0, 4), (-30, 2), (-50, -2), (-58, -10), (-54, -30)])
    out = [cast(D, x, y + 3 * s, 70 * s, 6 * s, "#000000", 0.45, seed)]
    out.append(painted(D, body, pal, seed, sdir=(-0.4, 0.8), sk=0.24, angle=-4, n=30, inkw=1.4, inkc="#0A0C14", hi=0.55))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    spots = [f'<path d="{blob(*L([(rnd.uniform(-60, 50), rnd.uniform(-24, 0))])[0], rnd.uniform(1.5, 3.6) * s, rnd.uniform(1, 2.4) * s, k, 0.2, 8)}" fill="{pal[2]}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>' for k in range(30)]
    spots.append(f'<path d="{smooth_closed(L([(-50, -2), (-20, 0), (20, 0), (50, -4), (20, -8), (-20, -8)]))}" fill="#E8EEF6" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(spots)}</g>')
    # moonlit back, hind flippers, a fore flipper, the face
    out.append(ink(smooth_open(L([(-84, -40), (-74, -46), (-62, -40), (-54, -26), (-30, -24), (0, -22), (30, -16), (54, -10)])), "#E8F0FF", 2 * s, seed, 1, 0.8))
    for sg in (-1, 1):
        fl = L([(58, -6), (76, -10 + sg * 8), (80, -4 + sg * 10), (66, 0)])
        out.append(poly(fl, pal[2]))
    out.append(poly(L([(-36, -2), (-30, 6), (-18, 8), (-22, -2)]), pal[2]))
    ex, ey = L([(-74, -40)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#05060A"/><circle cx="{ex - 0.6:.1f}" cy="{ey - 0.8:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    nx_, ny_ = L([(-85, -38)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{1.8 * s:.1f}" fill="#05060A"/>')
    for k in range(3):
        a0 = L([(-82, -35 + k * 1.5)])[0]
        out.append(f'<path d="M {a0[0]:.1f} {a0[1]:.1f} l {-8 * s if not flip else 8 * s:.1f} {(k - 1) * 2 * s:.1f}" stroke="#E8EEF6" stroke-width="0.8" opacity="0.7"/>')
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
    out.append(seal_lying(D, 478, 500, 0.92, 10))
    out.append(cast(D, 130, 452, 40, 5, "#000000", 0.5, 3))
    out.append(selkie_woman(D, 124, 454, 0.98, 15))
    # lettering
    out.append(letters(D, 300, 114, "The Selkie", SERIF_IT, 72, "#F2F6FF", ["#FFFFFF", "#DCE6FF", "#C8D8F8"], 13, max_w=380,
                       shadow="#000010", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 146, "SCOTTISH & IRISH · THE SEAL WIFE", CINZEL, 17, "#DCE6FF", ls=2, max_w=440))
    out.append(tx(301.5, 545.5, "The sea will always call her home.", SERIF_IT, 26, "#000000", max_w=420, op=0.6))
    out.append(tx(300, 544, "The sea will always call her home.", SERIF_IT, 26, "#F2F6FF", max_w=420))
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
    out.append(tx(300, 134, "JAPANESE · THE SUN COMES BACK", CINZEL, 17, "#FFF2D0", ls=2, max_w=440))
    out.append(tx(301.5, 539.5, "Light always finds its way out.", SERIF_IT, 27, "#1A0A04", max_w=420, op=0.6))
    out.append(tx(300, 538, "Light always finds its way out.", SERIF_IT, 27, "#FFF6E0", max_w=420))
    return fin(D, out, 33)


# ================================================================ 21. kitsune — the nine-tailed fox under the moon
def foxfire(D, x, y, r, seed, col="#8AF0E0"):
    out = [soft_glow(D, x, y, r * 4, col, 0.7)]
    out.append(poly([(x - r, y + r * 0.4), (x - r * 0.6, y - r), (x, y - r * 2.4), (x + r * 0.4, y - r * 1.2), (x + r, y + r * 0.2), (x, y + r)], col, 0.85))
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def fox_tail(D, root, ang, L, W, seed, pal=("#FFFFFF", "#ECE8F2", "#A8A4C0"), tip="#FFFFFF", curl=0.25):
    """One bushy fox brush springing from root at angle ang (deg), length L, max width W: full in the middle,
    a soft S-curve, fur strokes along it and a pale tip."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    spine = []
    for i in range(13):
        t = i / 12
        off = math.sin(t * math.pi * 1.2) * curl * L * 0.3
        spine.append((root[0] + ux * L * t + nx * off, root[1] + uy * L * t + ny * off))
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        t = i / 12
        w = W * (0.3 + 0.7 * math.sin(math.pi * min(1, t * 0.8 + 0.08)) ** 0.5) * (1 - 0.45 * t ** 4)
        j = rnd.uniform(0.92, 1.08)
        left.append((x + nx * w / 2 * j, y + ny * w / 2 * j))
        right.append((x - nx * w / 2 * j, y - ny * w / 2 * j))
    pts = left + [(spine[-1][0] + ux * W * 0.22 + nx * W * 0.12, spine[-1][1] + uy * W * 0.22 + ny * W * 0.12), (spine[-1][0] + ux * W * 0.3, spine[-1][1] + uy * W * 0.3),
                  (spine[-1][0] + ux * W * 0.22 - nx * W * 0.12, spine[-1][1] + uy * W * 0.22 - ny * W * 0.12)] + right[::-1]
    out = [painted(D, pts, pal, seed, sdir=(-ux * 0.3 + 0.2, -uy * 0.3 + 0.5), sk=0.2, angle=ang, n=24, inkw=1.4, inkc="#3A3A5A", hi=0.5)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    fur = []
    for k in range(70):
        t = rnd.uniform(0.05, 0.95)
        i = int(t * 12)
        x, y = spine[i]
        o = rnd.uniform(-W * 0.4, W * 0.4)
        x, y = x + nx * o, y + ny * o
        ln = rnd.uniform(8, 16)
        fur.append(f'<path d="M {x:.1f} {y:.1f} q {ux * ln * 0.5 + nx * 2:.1f} {uy * ln * 0.5 + ny * 2:.1f} {ux * ln:.1f} {uy * ln:.1f}" stroke="{rnd.choice([pal[2], "#FFFFFF", pal[1]])}" stroke-width="{rnd.uniform(1, 1.8):.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    # the glowing tip
    tx_, ty_ = spine[-2]
    g = D.lin([(0, tip, 0), (0.6, tip, 0.7), (1, tip, 1)], spine[7][0], spine[7][1], spine[-1][0], spine[-1][1], "userSpaceOnUse")
    fur.append(f'<path d="{smooth_closed(pts)}" fill="{g}"/>')
    out.append(f'<g {cid}>{"".join(fur)}</g>')
    return "".join(out), spine[-1]


def sitting_fox(D, x, base, s, seed, pal=("#FFFFFF", "#F2EEF6", "#A8A4C0"), rim="#FFFFFF"):
    """A fox sitting upright in profile, facing left, ears up, brush of tails drawn separately. ~178*s tall."""
    def L(pts):
        return T(pts, x, base, s)
    out = []
    far_ear = L([(-8, -150), (-12, -176), (2, -152)])
    out.append(poly(far_ear, pal[2]))
    out.append(poly(L([(-6, -153), (-10, -170), (-1, -154)]), "#E8A8B0", 0.7))
    # far foreleg
    out.append(taper(catmull(L([(-30, -70), (-31, -34), (-33, -4)]), 6), 11 * s, 8 * s, mix(pal[1], pal[2], 0.5)))
    body = L([(-70, -127), (-62, -120), (-50, -117), (-46, -110), (-49, -98), (-44, -84), (-41, -60), (-41, -22), (-42, -8), (-50, -2), (-48, 0), (-26, 0),
              (-27, -28), (-18, -40), (-14, -14), (-24, -6), (-26, 0), (18, 0), (34, -6), (40, -24), (38, -46), (28, -70), (16, -96), (6, -118),
              (0, -134), (-6, -146), (-12, -152), (-23, -174), (-30, -150), (-36, -146), (-44, -140), (-58, -133)])
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.5), sk=0.18, angle=-80, n=50, inkw=1.6, inkc="#2A2A48", hi=0.5))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    f = []
    for k in range(70):
        px, py = rnd.uniform(-50, 40), rnd.uniform(-150, -4)
        X, Y = L([(px, py)])[0]
        f.append(f'<path d="M {X:.1f} {Y:.1f} l {1.5 * s:.1f} {6 * s:.1f}" stroke="{rnd.choice([pal[2], "#FFFFFF"])}" stroke-width="{1.2 * s:.1f}" stroke-linecap="round" opacity="0.55"/>')
    # haunch and foreleg folds, the inner ear, the shrine-fox markings in vermilion
    f.append(pline(L([(-18, -40), (0, -60), (24, -60), (38, -46)]), pal[2], 1.8 * s, seed, 0.7, 1))
    f.append(pline(L([(-27, -28), (-27, -60), (-32, -80)]), pal[2], 1.6 * s, seed + 1, 0.6, 1))
    out.append(f'<g {cid}>{"".join(f)}</g>')
    out.append(poly(L([(-17, -153), (-23, -168), (-27, -152)]), "#E8A8B0", 0.8))
    # the cheek ruff that frames the face, and the throat fur
    out.append(pline(L([(-14, -146), (-14, -132), (-22, -122), (-30, -116), (-42, -112)]), "#8A84A8", 1.8 * s, seed + 7, 0.8, 1))
    for (ax, ay) in ((-16, -128), (-24, -119), (-34, -114)):
        out.append(pline(L([(ax, ay), (ax + 3, ay + 6)]), "#8A84A8", 1.4 * s, seed + int(ax), 0.7, 1))
    out.append(pline(L([(-46, -104), (-42, -96), (-46, -90)]), "#8A84A8", 1.4 * s, seed + 8, 0.6, 1))
    for (a, b) in (((-40, -140), (-32, -146)), ((-36, -132), (-26, -136))):
        p0, p1 = L([a, b])
        out.append(taper([p0, p1], 3 * s, 1.2 * s, "#D8302A"))
    ex, ey = L([(-44, -134)])[0]
    out.append(f'<path d="M {ex - 5 * s:.1f} {ey + 1 * s:.1f} q {5 * s:.1f} {-4 * s:.1f} {9 * s:.1f} {-2 * s:.1f}" stroke="#2A2A48" stroke-width="{2 * s:.1f}" fill="none" stroke-linecap="round"/>')
    nx_, ny_ = L([(-69, -127)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{2.6 * s:.1f}" fill="#2A2A48"/>')
    out.append(pline(L([(-66, -122), (-54, -121)]), "#2A2A48", 1.2 * s, seed, 0.7, 1))
    if rim:
        out.append(ink(smooth_open(L([(-6, -146), (0, -134), (6, -118), (16, -96), (28, -70), (38, -46), (40, -24)])), "#FFE8A0", 2.2 * s, seed, 1, 0.8))
    return "".join(out)


@design("kitsune")
def kitsune():
    D = Doc2("my-ks")
    out = [sky(D, [(0, "#060A24"), (0.5, "#141E4A"), (0.85, "#2A3466"), (1, "#3A3E70")], 1, 600, ["#1E2A5A", "#060A24", "#3A4A7A"], 60)]
    out.append(stars_field(4, (0, 0, 600, 360), 110))
    mx, my = 392, 262
    out.append(moon(D, mx, my, 104, 5, pal=("#FFF6D6", "#F6DE9A", "#D8B868"), glow="#FFE8A8", gs=0.5))
    # far hills, a vermilion torii on the left rise, pines
    far = ridge([(-20, 412), (90, 384), (200, 404), (330, 392), (460, 404), (620, 388)], 6, 8)
    out.append(hill(D, far, 620, ("#3A3E6A", "#22264A", "#0E1028"), 6, inkw=0))
    tx_, tb = 104, 392
    for dx in (-15, 15):
        out.append(taper([(tx_ + dx, tb), (tx_ + dx * 0.9, tb - 44)], 4.5, 3.6, "#D8402A"))
    out.append(taper([(tx_ - 28, tb - 46), (tx_, tb - 44), (tx_ + 28, tb - 46)], 5.5, 5.5, "#D8402A"))
    out.append(taper([(tx_ - 22, tb - 35), (tx_ + 22, tb - 35)], 3.4, 3.4, "#D8402A"))
    out.append(taper([(tx_ - 31, tb - 51), (tx_, tb - 49), (tx_ + 31, tb - 51)], 3.4, 3.4, "#1A0A0A"))
    for k in range(6):
        out.append(conifer(150 + k * 26 + (k % 2) * 6, 398 + (k % 2) * 4, 34 + (k % 3) * 10, "#0E1230", k, width=0.3))
    for k in range(4):
        out.append(conifer(520 + k * 24, 398, 30 + (k % 2) * 12, "#0E1230", k + 9, width=0.3))
    out.append(mist(D, 410, 40, 3, "#8A90C0", 0.4))
    # the meadow, susuki grass
    near = [(-20, 468), (140, 452), (300, 458), (460, 450), (620, 466)]
    out.append(hill(D, near, 620, ("#3A4A5A", "#1E2A34", "#0A1016"), 8, inkw=0))
    rnd = random.Random(8)
    # nine tails fanned behind her like a halo, each tipped with light
    fx, fb, fs = 236, 486, 1.32
    root = T([(36, -30)], fx, fb, fs)[0]
    out.append(soft_glow(D, root[0] + 60, root[1] - 90, 200, "#FFFFFF", 0.25))
    tips = []
    for k, ang in enumerate((-8, -26, -44, -62, -80, -98, -116, -134, -150)):
        L_ = 150 + 26 * math.sin(math.pi * k / 8)
        svg, tip = fox_tail(D, root, ang, L_, 58, 30 + k, pal=("#FFFFFF", "#F2ECF2", "#B0A4C0"), tip="#FFFFFF", curl=0.3 if k % 2 else -0.24)
        out.append(svg)
        tips.append(tip)
    out.append(cast(D, fx - 4, fb + 2, 90, 9, "#000000", 0.45, 2))
    out.append(sitting_fox(D, fx, fb, fs, 9, rim=None))
    # foxfire: kitsunebi drifting at the tail tips and over the grass
    def foxfire_(x, y, r, sd):
        o = [soft_glow(D, x, y, r * 5, "#7AF0E0", 0.6)]
        o.append(poly([(x - r, y + r * 0.5), (x - r * 0.7, y - r), (x - r * 0.1, y - r * 2.6), (x + r * 0.5, y - r * 1.1), (x + r, y + r * 0.3), (x, y + r * 1.1)], "#AFFFF0", 0.9))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="#FFFFFF"/>')
        return "".join(o)
    for k in (0, 2, 4, 6):
        out.append(foxfire_(tips[k][0], tips[k][1] - 6, 5, k))
    for (xx, yy) in ((78, 440), (150, 300), (520, 470), (468, 420)):
        out.append(foxfire_(xx, yy, 5, int(xx)))
    for k in range(60):
        x = rnd.uniform(-10, 610)
        if 150 < x < 330:
            continue
        base = rnd.uniform(470, 620)
        h = rnd.uniform(50, 110)
        lean = rnd.uniform(-0.4, 0.1)
        p = [(x, base), (x + lean * h * 0.4, base - h * 0.6), (x + lean * h, base - h)]
        out.append(taper(p, 2, 0.8, "#1A2A30"))
        if k % 2:
            pass
    # tall susuki at the corners, as in the old prints: silver plumes of fine strands bowing in the night air
    for (bx_, by_, h_, lean_) in ((34, 600, 200, 0.18), (62, 600, 170, 0.1), (86, 600, 140, 0.22), (566, 600, 190, -0.2), (540, 600, 160, -0.1), (516, 600, 130, -0.24)):
        tip = (bx_ + lean_ * h_, by_ - h_)
        out.append(taper(catmull([(bx_, by_), (bx_ + lean_ * h_ * 0.4, by_ - h_ * 0.6), tip], 6), 3, 1.2, "#2A3A30"))
        for j in range(8):
            a_ = math.radians((90 + (j - 3.5) * 9) if lean_ < 0 else (90 - (j - 3.5) * 9))
            ln = rnd.uniform(26, 40)
            st = catmull([tip, (tip[0] + math.cos(a_) * ln * 0.3 + lean_ * 20, tip[1] + 4), (tip[0] + math.cos(a_) * ln * 0.6 + lean_ * 40, tip[1] + ln * 0.5), (tip[0] + math.cos(a_) * ln * 0.7 + lean_ * 50, tip[1] + ln)], 5)
            out.append(taper(st, 2.4, 0.8, rnd.choice(["#E8E0D0", "#D8CCB8", "#F6F0E6"]), 0.8))
    # lettering
    out.append(letters(D, 300, 112, "Kitsune", SERIF_IT, 80, "#FFFFFF", ["#FFFFFF", "#FFE8E0", "#E8F0FF"], 14, max_w=360,
                       shadow="#060A24", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 144, "JAPANESE · THE NINE-TAILED FOX", CINZEL, 17, "#E8F0FF", ls=2.5, max_w=440))
    out.append(tx(301.5, 545.5, "A tail for every hundred years of wisdom", SERIF_IT, 24, "#000000", max_w=440, op=0.6))
    out.append(tx(300, 544, "A tail for every hundred years of wisdom", SERIF_IT, 24, "#F2F6FF", max_w=440))
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


def long_dragon(D, spine_pts, w, seed, pal=("#FFE8A0", "#E89A28", "#7A3A08"), belly="#F6E6B0", fin_col="#C8302A", back=-1):
    """A Chinese long: serpentine body along spine_pts (tail first), overlapping scales, a cream belly of
    ventral plates, flame-like dorsal fins along the back, four legs with eagle claws and flame tufts.
    back = which edge (+1 left / -1 right of travel) carries the dorsal fins. Returns (svg, head point, angle)."""
    path = catmull(spine_pts, 10)
    n = len(path)
    widths = [w * (0.22 + 0.78 * math.sin(math.pi * min(1, (i / (n - 1)) * 1.05 + 0.05)) ** 0.6) for i in range(n)]
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
    bk, bl = (left, right) if back > 0 else (right, left)
    sg = 1 if back > 0 else -1
    out = []
    rnd = random.Random(seed)
    # dorsal fins: flame-shaped, sweeping back toward the tail
    for i in range(3, n - 4, 2):
        x, y = bk[i]
        nx, ny = norms[i]
        nx, ny = nx * sg, ny * sg
        h = widths[i] * rnd.uniform(0.45, 0.65)
        px, py = path[max(0, i - 3)]
        tx_, ty_ = x + nx * h + (px - path[i][0]) * 0.5, y + ny * h + (py - path[i][1]) * 0.5
        fin = [(x - (px - path[i][0]) * 0.2, y - (py - path[i][1]) * 0.2), ((x + tx_) / 2 + nx * 3, (y + ty_) / 2 + ny * 3), (tx_, ty_), (x + (px - path[i][0]) * 0.3, y + (py - path[i][1]) * 0.3)]
        out.append(f'<path d="{smooth_closed(fin)}" fill="{fin_col if i % 4 == 1 else "#E8582A"}"/>')
    body = left + right[::-1]
    out.append(painted(D, body, pal, seed, sdir=(0.3, 0.8), sk=0.2, angle=-20, n=70, inkw=1.6, inkc="#3A1A04", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    sc = []
    # overlapping scales in staggered rows, each with a dark lower edge and a lit rim
    for i in range(2, n - 2, 2):
        x, y = path[i]
        nx, ny = norms[i]
        ww = widths[i]
        ux, uy = ny, -nx
        k0 = (i // 2) % 2
        for j in range(5):
            t = -0.36 + j * 0.18 + k0 * 0.09
            if t * -sg > 0.2:
                continue
            sx, sy = x + nx * ww * t, y + ny * ww * t
            r = ww * 0.13
            sc.append(f'<path d="M {sx - nx * r:.1f} {sy - ny * r:.1f} Q {sx - ux * r * 1.5:.1f} {sy - uy * r * 1.5:.1f} {sx + nx * r:.1f} {sy + ny * r:.1f}" stroke="{pal[2]}" stroke-width="1.3" fill="none" opacity="0.6"/>')
            sc.append(f'<path d="M {sx - nx * r * 0.6:.1f} {sy - ny * r * 0.6:.1f} Q {sx - ux * r * 0.6:.1f} {sy - uy * r * 0.6:.1f} {sx + nx * r * 0.6:.1f} {sy + ny * r * 0.6:.1f}" stroke="{pal[0]}" stroke-width="1" fill="none" opacity="0.6"/>')
    # the belly: a cream band of ventral plates along the lower edge
    inner = [(bl[i][0] + norms[i][0] * sg * widths[i] * 0.3, bl[i][1] + norms[i][1] * sg * widths[i] * 0.3) for i in range(n)]
    sc.append(f'<path d="{smooth_closed(bl + inner[::-1])}" fill="{belly}"/>')
    for i in range(1, n - 1):
        x, y = bl[i]
        nx, ny = norms[i]
        sc.append(f'<path d="M {x:.1f} {y:.1f} l {nx * sg * widths[i] * 0.3:.1f} {ny * sg * widths[i] * 0.3:.1f}" stroke="#B8862A" stroke-width="1.2" opacity="0.75"/>')
    sc.append(taper(inner, 1.6, 1.6, "#B8862A", 0.7))
    # a darker ridge down the spine
    sc.append(taper([(bk[i][0] - norms[i][0] * sg * widths[i] * 0.12, bk[i][1] - norms[i][1] * sg * widths[i] * 0.12) for i in range(n)], 3, 3, pal[2], 0.45))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # legs: a muscled upper limb, flame tufts at the elbow, four spread talons
    for t, side in ((0.3, 1), (0.4, -1), (0.66, 1), (0.76, -1)):
        i = int(t * (n - 1))
        x, y = path[i]
        nx, ny = norms[i]
        s2 = -sg * side if False else -sg
        kx = x + nx * s2 * widths[i] * 0.8 + (path[i + 3][0] - x) * 0.9
        ky = y + ny * s2 * widths[i] * 0.8 + (path[i + 3][1] - y) * 0.9
        fx = kx + nx * s2 * widths[i] * 0.55 + (path[i - 2][0] - x) * 0.3
        fy = ky + ny * s2 * widths[i] * 0.55 + (path[i - 2][1] - y) * 0.3
        out.append(taper(catmull([(x, y), (kx, ky), (fx, fy)], 6), widths[i] * 0.5, widths[i] * 0.24, pal[1]))
        out.append(taper(catmull([(x, y), (kx, ky), (fx, fy)], 6), widths[i] * 0.16, widths[i] * 0.06, pal[0], 0.6))
        for c in range(3):
            ta = math.atan2(ky - y, kx - x) + math.pi + (c - 1) * 0.35
            out.append(taper([(kx, ky), (kx + math.cos(ta) * 14, ky + math.sin(ta) * 14)], 4, 1, fin_col))
        base_a = math.atan2(fy - ky, fx - kx)
        for c in range(4):
            a = base_a + (c - 1.5) * 0.5
            p0 = (fx + math.cos(a) * 4, fy + math.sin(a) * 4)
            p1 = (fx + math.cos(a) * 12, fy + math.sin(a) * 12)
            p2 = (fx + math.cos(a + 0.7) * 17, fy + math.sin(a + 0.7) * 17)
            out.append(taper([p0, p1], 5, 3.4, pal[1]))
            out.append(taper([p1, p2], 3.2, 0.8, "#FFF6D8"))
    # the flame-tufted tip of the tail
    tx0, ty0 = path[0]
    ta = math.atan2(path[0][1] - path[3][1], path[0][0] - path[3][0])
    for c in range(7):
        a = ta + (c - 3) * 0.28
        L2 = 30 + 10 * math.cos((c - 3) * 0.5)
        out.append(taper(catmull([(tx0, ty0), (tx0 + math.cos(a) * L2 * 0.5, ty0 + math.sin(a) * L2 * 0.5), (tx0 + math.cos(a + 0.3) * L2, ty0 + math.sin(a + 0.3) * L2)], 5), 7, 1, (fin_col, "#E8582A", "#F6A030")[c % 3]))
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
    out.append(f'<path d="{blob(ex, ey, 4.4 * s, 3 * s, seed, 0.05, 10, ang)}" fill="#FFE04A" stroke="#3A1A04" stroke-width="1.4"/><circle cx="{ex + 0.6:.1f}" cy="{ey:.1f}" r="{1.5 * s:.1f}" fill="#1A0A04"/>')
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
    spine = [(500, 500), (470, 456), (400, 440), (300, 476), (190, 452), (130, 360), (180, 268), (290, 262), (350, 304)]
    svg, (hx, hy), ha = long_dragon(D, spine, 50, 5, back=-1)
    out.append(svg)
    out.append(long_head(D, hx - 4, hy - 6, 1.35, ha - 42, 6))
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
    out.append(tx(300, 134, "CHINESE · THE PEARL OF WISDOM", CINZEL, 17, "#E8F6F0", ls=2, max_w=440))
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
    out.append(tx(300, 538, "CHINESE · THE ELIXIR OF LIFE", CINZEL, 17, "#F2E8D8", ls=2.5, max_w=440))
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
    out = [sky(D, [(0, "#0E1A4A"), (0.35, "#2A3A7A"), (0.62, "#C87A8A"), (0.8, "#F6C08A"), (0.9, "#FFE6B8")], 1, 440, ["#3A4A8A", "#0E1A4A", "#F2B08A"], 60)]
    out.append(stars_field(3, (0, 0, 600, 220), 80))
    out.append(soft_glow(D, 300, 420, 320, "#FFF0C8", 0.6))
    for (x, y, w, sd) in ((470, 246, 190, 3), (150, 330, 130, 4)):
        out.append(puff_cloud(D, x, y, w, sd, ("#FFE8E0", "#E0A0B0", "#7A5A8A"), op=0.85))
    # the moon, first of the treasures, newly risen from the milk
    out.append(soft_glow(D, 150, 196, 70, "#FFFFFF", 0.7))
    out.append(f'<path d="M 165 174 A 30 30 0 1 0 165 226 A 34 34 0 0 1 165 174 Z" fill="#FFFDF0"/>')
    # the ocean of milk, ivory with cool shadows in the troughs
    out.append(sea(D, 410, 620, [(0, "#FFF8EA"), (0.4, "#F2E6DA"), (1, "#C8BCD0")], 5, ["#FFFFFF", "#C8C0D8", "#FFF2DC"], 90))
    cx, top, base = 300, 168, 446

    def hw(y):
        return 8 + 124 * (y - top) / (base - top)
    vp = ("#7AA8E0", "#2A4A9A", "#0E1E4A")
    coils = [(252, 0), (318, 1), (384, 2)]
    # the far halves of Vasuki's coils pass behind the mountain
    for (y, k) in coils:
        rx = hw(y) + 16
        pts = [(cx + rx * math.cos(math.radians(a)), y + rx * 0.24 * math.sin(math.radians(a)) - 8 * math.cos(math.radians(a))) for a in range(180, 361, 15)]
        out.append(taper(catmull(pts, 4), 20, 20, dk(vp[1], 0.35)))
    # Kurma, the great tortoise, bearing the mountain on its shell
    out.append(turtle_shell(D, cx, base + 4, 150, 30, 6))
    hx_, hy_ = cx + 160, base + 6
    out.append(painted(D, [(hx_ - 14, hy_ - 4), (hx_ + 6, hy_ - 14), (hx_ + 26, hy_ - 12), (hx_ + 30, hy_ - 2), (hx_ + 10, hy_ + 6)], ("#9AB08A", "#4A6A4A", "#1A2A1A"), 7, sk=0.2, n=6, inkw=1.4, inkc="#0A140A", hi=0.4))
    out.append(f'<circle cx="{hx_ + 18}" cy="{hy_ - 7}" r="2.2" fill="#0A140A"/>')
    # Mount Mandara, the churning rod: forested lower slopes, bare rock above, lit from the moon's side
    left = ridge([(cx - hw(base), base), (cx - hw(380), 380), (cx - hw(300), 300), (cx - hw(220), 220), (cx - 6, top + 6), (cx, top)], 4, 6)
    right = ridge([(cx, top), (cx + 8, top + 8), (cx + hw(230), 230), (cx + hw(310), 310), (cx + hw(390), 390), (cx + hw(base), base)], 5, 6)
    mt = left + right[1:]
    out.append(painted(D, mt, ("#C8B8A0", "#7A6A70", "#2A2234"), 8, sdir=(0.7, 0.2), sk=0.25, angle=-80, n=90, inkw=1.6, inkc="#140A1E", hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(mt)}"/>')
    rnd = random.Random(9)
    tex = []
    for k in range(40):
        y = rnd.uniform(top + 20, base - 20)
        x = cx + rnd.uniform(-hw(y), hw(y)) * 0.9
        tex.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-8, 8):.1f} {rnd.uniform(10, 22):.1f}" stroke="{rnd.choice(["#FFF0D8", "#2A2234"])}" stroke-width="{rnd.uniform(1.2, 2.2):.1f}" opacity="0.45"/>')
    for k in range(70):
        y = rnd.uniform(270, base)
        x = cx + rnd.uniform(-hw(y), hw(y))
        tex.append(f'<path d="{blob(x, y, rnd.uniform(5, 10), rnd.uniform(4, 7), k, 0.2, 8)}" fill="{rnd.choice(["#5A8A4A", "#3A6A3A", "#1E4A2A", "#8AAA5A"])}" opacity="0.9"/>')
    g = D.lin([(0, "#FFE8C8", 0.35), (0.45, "#FFE8C8", 0), (1, "#140A1E", 0.45)], 0, 0, 1, 0)
    tex.append(f'<path d="{smooth_closed(mt)}" fill="{g}"/>')
    out.append(f'<g {cid}>{"".join(tex)}</g>')
    out.append(ink(smooth_open(left[-6:]), "#FFF0D8", 2.6, 3, 1, 0.7))
    # the near halves of the coils, scaled and banded
    for (y, k) in coils:
        rx = hw(y) + 16
        pts = [(cx + rx * math.cos(math.radians(a)), y + rx * 0.24 * math.sin(math.radians(a)) - 8 * math.cos(math.radians(a))) for a in range(0, 181, 12)]
        out.append(snake(D, pts, 21, 21, vp, 10 + k, head=False))
    # the free ends, pulled taut toward the gods and the demons beyond the picture
    lx0, ly0 = cx - hw(384) - 16, 384 + 8
    out.append(snake(D, [(lx0, ly0), (lx0 - 50, 380), (140, 384), (104, 376), (92, 356)], 21, 18, vp, 13, head=False))
    rx0, ry0 = cx + hw(252) + 16, 252 - 8
    out.append(snake(D, [(rx0, ry0), (rx0 + 60, 262), (500, 274), (560, 270), (630, 252)], 20, 12, vp, 14, head=False))
    # Vasuki's head, the great cobra hood raised at the left
    hx, hy = 92, 318
    neck = [(hx - 9, hy + 44), (hx + 9, hy + 44)]
    hood = [(hx - 9, hy + 46), (hx - 22, hy + 22), (hx - 33, hy - 4), (hx - 31, hy - 28), (hx - 18, hy - 44), (hx, hy - 48),
            (hx + 18, hy - 44), (hx + 31, hy - 28), (hx + 33, hy - 4), (hx + 22, hy + 22), (hx + 9, hy + 46)]
    out.append(painted(D, hood, vp, 15, sdir=(0.4, 0.6), sk=0.2, n=24, inkw=1.6, inkc="#06102A", hi=0.45))
    out.append(painted(D, [(hx - 7, hy + 44), (hx - 12, hy + 10), (hx - 11, hy - 18), (hx, hy - 30), (hx + 11, hy - 18), (hx + 12, hy + 10), (hx + 7, hy + 44)],
                       ("#FFF6D8", "#F2DCA0", "#A8863A"), 16, sk=0.15, n=8, inkw=1.0, inkc="#6A4A10", hi=0.4))
    for k in range(7):
        y = hy + 36 - k * 9
        w_ = 6 + 4 * math.sin(math.pi * k / 7)
        out.append(f'<path d="M {hx - w_:.1f} {y:.1f} q {w_:.1f} 5 {2 * w_:.1f} 0" stroke="#A8863A" stroke-width="1.3" fill="none"/>')
    head = [(hx - 12, hy - 40), (hx - 14, hy - 54), (hx - 8, hy - 66), (hx, hy - 70), (hx + 8, hy - 66), (hx + 14, hy - 54), (hx + 12, hy - 40)]
    out.append(painted(D, head, vp, 17, sdir=(0.4, 0.6), sk=0.2, n=8, inkw=1.6, inkc="#06102A", hi=0.5))
    for sg in (-1, 1):
        out.append(f'<path d="{blob(hx + sg * 6, hy - 54, 2.6, 2, 4 + sg, 0.05, 8)}" fill="#FFE04A"/><circle cx="{hx + sg * 6:.1f}" cy="{hy - 54:.1f}" r="1" fill="#06102A"/>')
    out.append(soft_glow(D, hx, hy - 76, 16, "#FFE08A", 0.8))
    out.append(f'<path d="{blob(hx, hy - 76, 5, 6, 9, 0.05, 10)}" fill="#E8402A" stroke="#E8B84A" stroke-width="2"/>')
    # the milk churned into great foaming swirls about the mountain's foot
    for k in range(6):
        r = hw(base) + 20 + k * 24
        out.append(f'<path d="{smooth_open(ell_pts(cx, base + 8, r, r * 0.17, 8, 172, 20))}" fill="none" stroke="#FFFFFF" stroke-width="{4.5 - k * 0.6:.1f}" opacity="0.85"/>')
        out.append(f'<path d="{smooth_open(ell_pts(cx, base + 10, r + 6, (r + 6) * 0.17, 20, 160, 20))}" fill="none" stroke="#B8B0C8" stroke-width="1.4" opacity="0.5"/>')
    for k in range(70):
        out.append(f'<circle cx="{rnd.uniform(60, 540):.1f}" cy="{rnd.uniform(430, 500):.1f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    # the golden pot of amrita rising from the foam in a burst of light, a lotus floating near
    kx, ky = 476, 470
    out.append(soft_glow(D, kx, ky - 26, 110, "#FFE070", 0.85))
    out.append(ray_fan(kx, ky - 26, 30, 110, 18, "#FFF2B0", 0.35, seed=6))
    pot = [(kx - 22, ky - 30), (kx - 28, ky - 10), (kx - 18, ky + 6), (kx + 18, ky + 6), (kx + 28, ky - 10), (kx + 22, ky - 30), (kx + 10, ky - 40), (kx - 10, ky - 40)]
    out.append(painted(D, pot, GOLD, 12, sk=0.2, n=10, inkw=1.4, inkc="#5A3A08", hi=0.5))
    out.append(painted(D, [(kx - 10, ky - 40), (kx + 10, ky - 40), (kx + 15, ky - 50), (kx - 15, ky - 50)], GOLD, 13, sk=0.2, n=4, inkw=1.2, inkc="#5A3A08", hi=0.5))
    for k in range(5):
        a = math.radians(-150 + k * 30)
        out.append(f'<path d="{blob(kx + math.cos(a) * 10, ky - 56 + math.sin(a) * 8, 8, 3.6, k, 0.05, 8, math.degrees(a))}" fill="#4A8A4A"/>')
    out.append(f'<path d="M {kx - 26} {ky - 14} q 26 10 52 0" stroke="#C8302A" stroke-width="3" fill="none"/>')
    for k in range(12):
        out.append(sparkle(kx + rnd.uniform(-50, 50), ky - 40 + rnd.uniform(-50, 30), rnd.uniform(2, 4.4), "#FFFFFF", 0.95))
    lx, ly = 150, 486
    for k in range(8):
        a = math.radians(-180 + k * 25.7)
        out.append(f'<path d="{blob(lx + math.cos(a) * 14, ly - 8 + math.sin(a) * 12, 14, 5.4, k, 0.05, 10, math.degrees(a))}" fill="{("#F6A8C0", "#FFD0DC")[k % 2]}" stroke="#C8607A" stroke-width="0.8"/>')
    out.append(f'<circle cx="{lx}" cy="{ly - 10}" r="5" fill="#F6C84A"/>')
    out.append(f'<path d="{blob(lx + 30, ly + 6, 22, 6, 3, 0.05, 12)}" fill="#5A8A5A" opacity="0.9"/>')
    # lettering
    out.append(gilt(D, 300, 98, "The Churning of the Ocean", SERIF_IT, 48, max_w=460, seed=15, deboss="#000010", dop=0.8))
    out.append(tx(300, 128, "HINDU · SAMUDRA MANTHAN", CINZEL, 17, "#F2ECFF", ls=2, max_w=440))
    out.append(tx(300, 546, "From the churning came the nectar of life", SERIF_IT, 24, "#4A2A5A", max_w=440))
    return fin(D, out, 37)


# ================================================================ 25. fenrir — the great wolf bound by Gleipnir
def howling_wolf(D, x, base, s, seed, col="#0C1224", rim="#DCE8FF", fur="#2A3450"):
    """A great wolf sitting on its haunches, head thrown back, howling (facing right). (x, base) = ground under
    the chest; about 285*s tall. Painted dark against the moonlight with a cold rim light and fur strokes."""
    def L(pts):
        return T(pts, x, base, s)
    # head in its own frame: u along the muzzle (pointing up-right), v toward the throat
    C, th = (22, -236), math.radians(-50)
    du, dv = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))

    def H(pts):
        return [(C[0] + 1.18 * (u * du[0] + v * dv[0]), C[1] + 1.18 * (u * du[1] + v * dv[1])) for u, v in pts]
    head = H([(-20, 18), (-26, 6), (-25, -8), (-22, -16), (-8, -22), (8, -19), (30, -13), (52, -9), (60, -6), (63, -2), (60, 3), (40, 6),
              (18, 10), (46, 14), (44, 19), (28, 23), (8, 23), (-6, 24)])
    ear_far = H([(-4, -18), (-2, -50), (8, -20)])
    ear = H([(-18, -16), (-16, -52), (-2, -22)])
    body = [(3, -212), (-12, -196), (-30, -168), (-48, -128), (-66, -96), (-82, -66), (-88, -40), (-82, -16), (-66, -3), (-50, 0),
            (10, 0), (13, -6), (6, -11), (-14, -14), (-6, -40), (8, -66), (22, -84), (24, -56), (26, -20), (24, 0), (58, 0),
            (60, -7), (50, -14), (48, -46), (48, -80), (54, -108), (50, -128), (58, -146), (48, -152), (56, -170), (44, -174),
            (50, -192), (38, -196), (34, -212)]
    sil = L(body)
    out = []
    # far foreleg, a shade lighter so the pair reads
    out.append(taper(catmull(L([(30, -110), (36, -60), (40, -16), (44, 0)]), 6), 18 * s, 12 * s, mix(col, "#3A4668", 0.35)))
    out.append(poly(L(ear_far), mix(col, "#3A4668", 0.3)))
    out.append(poly(sil, col))
    out.append(poly(L(head), col))
    out.append(poly(L(ear), col))
    # the bushy tail curled along the ground round the feet
    tail = catmull(L([(-82, -30), (-74, -8), (-46, 3), (-10, 4), (14, -3), (24, -12)]), 8)
    out.append(taper(tail, 30 * s, 10 * s, col))
    rnd = random.Random(seed)
    allp = smooth_closed(sil) + " " + smooth_closed(L(head))
    cid = D.clip(f'<path d="{allp}"/>')
    f = []
    g = D.lin([(0, "#7A8AB8", 0.6), (0.4, "#2A3450", 0.18), (1, col, 0)], 1, 0, 0.15, 0.7)
    f.append(f'<path d="{allp}" fill="{g}"/>')
    for k in range(300):
        px, py = rnd.uniform(-90, 66), rnd.uniform(-290, 0)
        X, Y = L([(px, py)])[0]
        ang = math.radians(105 + rnd.uniform(-20, 20)) if py > -190 else math.radians(140 + rnd.uniform(-25, 25))
        ln = rnd.uniform(6, 13) * s
        f.append(f'<path d="M {X:.1f} {Y:.1f} q {math.cos(ang) * ln * 0.5 + 1.5:.1f} {math.sin(ang) * ln * 0.5:.1f} {math.cos(ang) * ln:.1f} {math.sin(ang) * ln:.1f}" '
                 f'stroke="{rnd.choice([fur, "#3A4668", "#05070E", "#4A5878"])}" stroke-width="{rnd.uniform(1.1, 2.0):.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    # folds: the near foreleg against the chest, the haunch, the hock
    f.append(pline(L([(22, -84), (24, -56), (26, -20)]), "#04060C", 2.6 * s, seed, 0.7, 1))
    f.append(pline(L([(-74, -60), (-56, -92), (-28, -104), (-2, -96)]), "#04060C", 2.6 * s, seed + 1, 0.55, 1))
    f.append(pline(L([(-78, -36), (-60, -14), (-30, -12)]), "#04060C", 2.2 * s, seed + 2, 0.5, 1))
    f.append(pline(L(H([(40, 6), (18, 10), (46, 14)])), "#04060C", 2.0 * s, seed + 3, 0.9, 1))
    out.append(f'<g {cid}>{"".join(f)}</g>')
    # cold rim light along the moon side: brow, muzzle, jaw, throat ruff, chest, foreleg
    out.append(ink(smooth_open(L(H([(-8, -22), (8, -19), (30, -13), (52, -9), (60, -6), (63, -2)]))), rim, 2.6 * s, seed, 1, 0.95))
    out.append(ink(smooth_open(L(H([(46, 14), (44, 19), (28, 23), (8, 23)]))), rim, 1.8 * s, seed + 6, 1, 0.7))
    out.append(ink(smooth_open(L([(34, -212), (38, -196), (50, -192), (44, -174), (56, -170), (48, -152), (58, -146), (50, -128), (54, -108), (48, -80), (48, -46), (50, -14)])),
                   rim, 2.2 * s, seed + 3, 1, 0.8))
    out.append(ink(smooth_open(L([ear[1], ear[2]])), rim, 1.8 * s, seed + 4, 1, 0.85))
    out.append(ink(smooth_open(tail[-14:]), rim, 1.6 * s, seed + 5, 1, 0.5))
    # the eye shut tight in the howl
    ex, ey = L(H([(4, -9)]))[0]
    out.append(pline([(ex - 5 * s, ey + 2 * s), (ex, ey - 0.5 * s), (ex + 5 * s, ey - 3 * s)], "#9AA8C8", 1.6 * s, seed, 0.9, 1))
    nx_, ny_ = L(H([(60, -2)]))[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{3.4 * s:.1f}" fill="#020306"/>')
    return "".join(out)


def gleipnir(D, pts, seed, w=4.0):
    """The silken fetter: a thin glowing ribbon that catches the light, with a few sparkles along it."""
    path = catmull(pts, 8)
    out = [taper(path, w * 3.2, w * 3.2, "#FFE8B0", 0.18)]
    out.append(taper(path, w, w * 0.9, "#FFF2C8", 0.95))
    out.append(taper([(px, py - w * 0.25) for px, py in path], w * 0.4, w * 0.3, "#FFFFFF", 0.9))
    rnd = random.Random(seed)
    for k in range(0, len(path), 5):
        px, py = path[k]
        out.append(sparkle(px + rnd.uniform(-4, 4), py + rnd.uniform(-6, 6), rnd.uniform(2, 4), "#FFFFFF", 0.9))
    return "".join(out)


@design("fenrir")
def fenrir():
    D = Doc2("my-fn")
    out = [sky(D, [(0, "#050A1E"), (0.45, "#0E1E3E"), (0.75, "#1E3A5A"), (1, "#2A4A66")], 1, 600, ["#14284A", "#050A1E", "#2A4A6A"], 60)]
    out.append(stars_field(5, (0, 0, 600, 360), 140))
    out.append(aurora(D, 6, 150, 330, ("#5AE0B0", "#3AB8C8", "#7AF0C8")))
    mx, my = 446, 228
    out.append(moon(D, mx, my, 74, 7, pal=("#FFFFFF", "#F2F4F8", "#B8C0D0"), glow="#E8F0FF", gs=0.6, glow_r=3.4))
    # far mountains of the lake shore, a wall of firs, the black lake with the moon's road
    far = ridge([(-20, 372), (70, 330), (150, 356), (240, 300), (320, 350), (400, 326), (480, 352), (560, 318), (620, 340)], 3, 8)
    out.append(hill(D, far, 620, ("#4A5E80", "#2A3A5A", "#121C34"), 3, inkw=0, lit="#8AA0C8"))
    for k in range(28):
        xx = -10 + k * 23 + (k * 7) % 11
        out.append(conifer(xx, 400 + (k % 3) * 3, 28 + (k * 13) % 22, "#0A1428", k, width=0.34))
    out.append(sea(D, 396, 620, [(0, "#2A4060"), (0.4, "#14223C"), (1, "#060A18")], 8, ["#4A6A90", "#060A18", "#8AA8D0"], 70))
    rnd = random.Random(9)
    out.append(soft_glow(D, mx, 420, 80, "#C8D8FF", 0.3))
    for k in range(70):
        y = 400 + (k / 70) ** 1.2 * 110
        w = 30 + (y - 396) * 0.9
        xx = mx + rnd.gauss(0, w * 0.3)
        ln = rnd.uniform(4, 14)
        out.append(taper([(xx - ln, y), (xx, y - 1.2), (xx + ln, y)], 0.6, rnd.uniform(1.2, 2.6), "#F2F6FF", rnd.uniform(0.3, 0.85)))
    # the island of Lyngvi: a dark rock with frost on its lip
    isle = [(-20, 620), (-20, 470), (40, 452), (120, 444), (220, 440), (330, 450), (400, 470), (440, 500), (470, 540), (480, 620)]
    out.append(painted(D, isle, ("#3A4660", "#1A2236", "#060A12"), 10, sdir=(-0.6, 0.5), sk=0.18, angle=-12, n=60, inkw=1.4, inkc="#020408", hi=0.0))
    out.append(ink(smooth_open(isle[2:8]), "#C8D8F0", 2.4, 4, 1, 0.65))
    for k in range(26):
        sx = rnd.uniform(20, 440)
        out.append(taper([(sx, 452 + rnd.uniform(0, 70)), (sx + rnd.uniform(10, 28), 452 + rnd.uniform(0, 70))], 1, 2, "#8AA0C8", rnd.uniform(0.2, 0.5)))
    # the rock Thviti, driven deep, where the fetter is fastened
    th = [(364, 506), (370, 452), (380, 426), (392, 422), (400, 446), (406, 506)]
    out.append(painted(D, th, ("#6A7A98", "#2A3450", "#0A0E1A"), 11, sdir=(-0.6, 0.4), sk=0.25, angle=-80, n=10, inkw=1.4, inkc="#04060C", hi=0.3))
    out.append(ink(smooth_open(th[1:5]), "#DCE8FF", 2, 5, 1, 0.8))
    # the wolf, and Gleipnir: from the rock, round his forelegs, trailing on the stone
    wx, wb = 196, 474
    out.append(cast(D, wx - 10, wb + 4, 150, 12, "#000000", 0.5, 3))
    out.append(soft_glow(D, wx + 40, wb - 200, 200, "#AFC8FF", 0.25))
    out.append(howling_wolf(D, wx, wb, 1.08, 12))
    ws = 1.08
    lx0, lx1 = wx + 20 * ws, wx + 66 * ws
    for k, yy in enumerate((wb - 34 * ws, wb - 22 * ws)):
        out.append(gleipnir(D, [(lx0, yy - 4), ((lx0 + lx1) / 2, yy + 7), (lx1, yy - 2)], 13 + k, 3.4))
    out.append(gleipnir(D, [(lx1, wb - 24 * ws), (lx1 + 16, wb - 6), (lx1 + 46, wb + 4), (320, wb + 2), (366, wb - 8), (386, 452)], 15, 3.6))
    out.append(soft_glow(D, (lx0 + lx1) / 2, wb - 28, 60, "#FFE8B0", 0.45))
    # lettering
    out.append(gilt(D, 300, 100, "FENRIR", CINZEL, 66, ls=14, max_w=380, seed=15, pal="silver", deboss="#000000", dop=0.85))
    out.append(tx(300, 132, "NORSE · BOUND BY A SILKEN RIBBON", CINZEL, 17, "#DCE8FF", ls=2, max_w=440))
    out.append(tx(301.5, 541.5, "Woven of a cat’s footfall and a mountain’s roots", SERIF_IT, 23, "#000000", max_w=450, op=0.6))
    out.append(tx(300, 540, "Woven of a cat’s footfall and a mountain’s roots", SERIF_IT, 23, "#F2F6FF", max_w=450))
    return fin(D, out, 38)


# ================================================================ 26. gilgamesh — into the cedar forest
def cedar(D, x, base, h, w, seed, pal=("#5A8A6A", "#24503E", "#0A2018"), trunk=("#8A6A4A", "#4A3424", "#1A100A"), lit=1, rim=None,
          tiers=6, spread=1.0, haze=None):
    """A cedar of Lebanon: a massive trunk and flat, layered tiers of foliage held out on near-horizontal limbs,
    lit from the `lit` side. haze = (colour, opacity) lays atmosphere over the whole tree."""
    rnd = random.Random(seed)
    out = []
    top = base - h
    tr = [(x - w * 0.5, base + 4), (x - w * 0.36, base - h * 0.4), (x - w * 0.16, top + h * 0.12), (x, top), (x + w * 0.16, top + h * 0.12),
          (x + w * 0.36, base - h * 0.4), (x + w * 0.5, base + 4)]
    out.append(painted(D, tr, trunk, seed, sdir=(-lit * 0.6, 0.3), sk=0.25, angle=-90, n=int(h / 4), inkw=0, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(tr)}"/>')
    bark = "".join(f'<path d="M {x + rnd.uniform(-w, w) * 0.4:.1f} {rnd.uniform(top, base):.1f} l {rnd.uniform(-2, 2):.1f} {rnd.uniform(14, 40):.1f}" stroke="{trunk[2]}" stroke-width="{rnd.uniform(1.2, 2.4):.1f}" opacity="0.5"/>' for _ in range(int(h / 5)))
    out.append(f'<g {cid}>{bark}</g>')
    if rim:
        out.append(ink(smooth_open(tr[4:] if lit > 0 else tr[:4]), rim, 2.4, seed, 1, 0.7))
    pads = []
    for i in range(tiers):
        t = i / max(1, tiers - 1)
        y = base - h * (0.32 + 0.66 * t)
        reach = (h * 0.55 * (1 - t) ** 0.8 + h * 0.08) * spread
        for side in (-1, 1):
            if rnd.random() < 0.15 and 0 < i < tiers - 1:
                continue
            ex = x + side * reach * rnd.uniform(0.75, 1.05)
            ey = y - rnd.uniform(4, 16)
            out.append(taper(catmull([(x + side * w * 0.12, y + 10), ((x + ex) / 2, y - 4), (ex, ey)], 6), max(4, w * 0.22 * (1 - t * 0.6)), 3, trunk[1]))
            pads.append((ex - side * reach * 0.25, ey, reach * 0.62, h * 0.045 + 6))
        pads.append((x, y - 6, reach * 0.28, h * 0.04 + 6))
    pads.append((x, top + 6, h * 0.08, h * 0.03 + 5))
    shapes = []
    for (cx, cy, rx, ry) in pads:
        # each tier is a flat-bottomed cloud of needle clumps: a lumpy lit top, a straight shadowed underside
        pts = []
        nb = max(3, int(rx / (ry * 1.1)))
        for k in range(nb + 1):
            t = k / nb
            px = cx - rx + 2 * rx * t
            bump = ry * (0.7 + 0.5 * math.sin(math.pi * t)) * rnd.uniform(0.75, 1.15)
            pts.append((px, cy - bump))
            if k < nb:
                pts.append((px + rx / nb, cy - bump * rnd.uniform(0.82, 0.95)))
        pts += [(cx + rx * 1.02, cy - ry * 0.1), (cx + rx * 0.9, cy + ry * 0.45), (cx + rx * 0.3, cy + ry * 0.6), (cx - rx * 0.3, cy + ry * 0.62), (cx - rx * 0.92, cy + ry * 0.45), (cx - rx * 1.02, cy - ry * 0.1)]
        shapes.append(pts)
        out.append(painted(D, pts, pal, int(cx + cy), sdir=(-lit * 0.25, 0.95), sk=0.3, angle=0 + rnd.uniform(-8, 8), n=int(rx * ry / 8) + 10,
                           slen=(rx * 0.08, rx * 0.28), inkw=0, hi=0.5, hik=0.12))
        cid2 = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        tex = []
        for k in range(int(rx * ry / 14)):
            fx, fy = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry * 1.2, ry * 0.6)
            tex.append(f'<path d="M {fx:.1f} {fy:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-1.5, 1.5):.1f}" stroke="{rnd.choice([pal[0], pal[2], pal[2]])}" stroke-width="{rnd.uniform(1, 2):.1f}" opacity="{rnd.uniform(0.3, 0.7):.2f}" stroke-linecap="round"/>')
        tex.append(f'<path d="M {cx - rx * 1.1:.1f} {cy + ry * 0.15:.1f} L {cx + rx * 1.1:.1f} {cy + ry * 0.15:.1f} L {cx + rx * 1.1:.1f} {cy + ry:.1f} L {cx - rx * 1.1:.1f} {cy + ry:.1f} Z" fill="{pal[2]}" opacity="0.45"/>')
        out.append(f'<g {cid2}>{"".join(tex)}</g>')
        for k in range(int(rx / 3)):
            i = rnd.randint(0, len(pts) - 7)
            fx, fy = pts[i]
            out.append(f'<path d="M {fx + rnd.uniform(-3, 3):.1f} {fy + 2:.1f} l {rnd.uniform(-3, 3):.1f} {-rnd.uniform(2, 5):.1f}" stroke="{pal[0]}" stroke-width="1.4" opacity="0.75"/>')
    if haze:
        col, op = haze
        allp = smooth_closed(tr) + "".join(" " + smooth_closed(pp) for pp in shapes)
        out.append(f'<path d="{allp}" fill="{col}" opacity="{op}"/>')
    return "".join(out)


def walker_back(x, base, s, col, rim=None, flip=False, stride=1.0, kilt=None):
    """A tall heroic figure walking away from us (about 150*s tall): broad shoulders, narrow waist, a fringed
    knee-length kilt, long striding legs, the left arm swinging. The right arm is left to the caller."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = []
    # legs: the near (right) leg planted, the left one lifting at the heel as it strides
    out.append(taper(catmull(L([(-7, -50), (-9 - 2 * stride, -24), (-12 - 3 * stride, -6)]), 6), 12 * s, 6 * s, col))
    out.append(poly(L([(-20 - 3 * stride, -2), (-6 - 3 * stride, -2), (-8 - 3 * stride, -9), (-17 - 3 * stride, -9)]), col))
    out.append(taper(catmull(L([(7, -50), (10 + 2 * stride, -26), (13 + 3 * stride, -10)]), 6), 12 * s, 6 * s, col))
    out.append(poly(L([(9 + 3 * stride, -14), (19 + 3 * stride, -9), (17 + 3 * stride, -4), (8 + 3 * stride, -9)]), col))
    torso = L([(-6, -128), (-16, -126), (-24, -122), (-27, -114), (-24, -102), (-18, -90), (-15, -78), (15, -78), (18, -90), (24, -102), (27, -114), (24, -122), (16, -126), (6, -128)])
    out.append(poly(torso, col))
    kc = kilt or col
    out.append(poly(L([(-16, -82), (16, -82), (19, -60), (21, -44), (8, -42), (-6, -44), (-21, -42), (-19, -62)]), kc))
    out.append(poly(L([(-5, -134), (-5, -124), (5, -124), (5, -134)]), col))
    hx, hy = L([(0, -142)])[0]
    out.append(f'<path d="{blob(hx, hy, 8.4 * s, 9.6 * s, 4, 0.06, 12)}" fill="{col}"/>')
    # the left arm swinging back
    out.append(taper(catmull(L([(-23, -120), (-29, -100), (-31, -82), (-29, -68)]), 6), 8 * s, 5.4 * s, col))
    if kilt:
        rnd = random.Random(int(x))
        for k in range(10):
            a, b = L([(-20 + k * 4.2, -45), (-20 + k * 4.2 + rnd.uniform(-1, 1), -39)])
            out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{kc}" stroke-width="{1.4 * s:.1f}"/>')
    if rim:
        out.append(ink(smooth_open(L([(4, -150), (8, -144), (8, -134), (16, -126), (25, -121), (27, -112), (24, -102), (18, -90)])), rim, 1.8, 3, 1, 0.85))
        out.append(ink(smooth_open(L([(19, -62), (21, -44)])), rim, 1.4, 4, 1, 0.6))
        out.append(ink(smooth_open(L([(10 + 2 * stride, -36), (13 + 3 * stride, -12)])), rim, 1.4, 5, 1, 0.6))
    return "".join(out)


def hero_with_axe(D, x, base, s, col, rim, flip=False, hair=False):
    """A hero from behind (walker_back) with a bronze axe carried on the outer shoulder; hair=True gives Enkidu's
    wild mane, otherwise Gilgamesh's long hair bound in a knot at the nape."""
    out = [walker_back(x, base, s, col, rim, flip, 1.0, kilt="#2A1810")]

    def L(pts):
        return T(pts, x, base, s, flip)
    # the right arm bent up to the shoulder, holding the haft
    out.append(taper(catmull(L([(23, -120), (30, -104), (26, -92), (20, -100)]), 6), 8 * s, 6 * s, col))
    h0, h1 = L([(14, -84), (40, -168)])
    out.append(taper([h0, h1], 3.4 * s, 3 * s, "#3A2414"))
    blade = L([(34, -158), (54, -174), (64, -160), (62, -140), (40, -146)])
    out.append(poly(blade, "#C8862A"))
    out.append(ink(smooth_open(blade[1:4]), "#FFE6A0", 2.2 * s, 3, 1, 0.95))
    if hair:
        out.append(poly(L([(-10, -150), (-14, -136), (-18, -114), (-8, -120), (0, -112), (8, -120), (17, -114), (13, -136), (10, -150), (0, -153)]), col))
    else:
        out.append(f'<path d="{blob(*L([(0, -128)])[0], 7 * s, 6 * s, 2, 0.1, 10)}" fill="{col}"/>')
        out.append(poly(L([(-9, -150), (-6, -155), (6, -155), (9, -150)]), col))
    return "".join(out)


def cuneiform_rows(D, x0, x1, y0, y1, rows, seed, col="#5A3A22", op=0.55, s=1.0):
    """Rows of wedge impressions pressed into clay (decorative, not a real text)."""
    rnd = random.Random(seed)
    out = []
    h = (y1 - y0) / rows
    for r in range(rows):
        y = y0 + h * (r + 0.5)
        out.append(f'<path d="M {x0:.1f} {y + h * 0.5:.1f} L {x1:.1f} {y + h * 0.5 + rnd.uniform(-0.6, 0.6):.1f}" stroke="{col}" stroke-width="0.9" opacity="{op * 0.6:.2f}"/>')
        x = x0 + rnd.uniform(0, 6)
        while x < x1 - 8:
            kind = rnd.random()
            if kind < 0.45:
                out.append(f'<path d="M {x:.1f} {y - 4 * s:.1f} l {5 * s:.1f} {2 * s:.1f} l {-5 * s:.1f} {2 * s:.1f} Z M {x + 4 * s:.1f} {y:.1f} l {6 * s:.1f} 0" stroke="{col}" stroke-width="{1.1 * s:.1f}" fill="{col}" opacity="{op:.2f}"/>')
            elif kind < 0.8:
                out.append(f'<path d="M {x - 2.5 * s:.1f} {y - 5 * s:.1f} l {5 * s:.1f} 0 l {-2.5 * s:.1f} {4 * s:.1f} Z M {x:.1f} {y - 1 * s:.1f} l 0 {6 * s:.1f}" stroke="{col}" stroke-width="{1.1 * s:.1f}" fill="{col}" opacity="{op:.2f}"/>')
            else:
                out.append(f'<path d="M {x + 4 * s:.1f} {y - 4 * s:.1f} l {-5 * s:.1f} {3 * s:.1f} l {5 * s:.1f} {2 * s:.1f}" stroke="{col}" stroke-width="{1.4 * s:.1f}" fill="none" opacity="{op:.2f}"/>')
            x += rnd.uniform(9, 15) * s
            if rnd.random() < 0.12:
                x += 10 * s
    return "".join(out)


@design("gilgamesh")
def gilgamesh():
    D = Doc2("my-gg")
    out = [sky(D, [(0, "#3A2A3A"), (0.35, "#A8705A"), (0.62, "#F2C27A"), (0.8, "#FCE6B0")], 1, 520, ["#7A4A4A", "#FFE0A0", "#D89A6A"], 60)]
    # the Cedar Mountain, dwelling of the gods, glowing at the end of the forest road
    sx, sy = 316, 300
    out.append(soft_glow(D, sx, sy, 300, "#FFF2C8", 0.75))
    mt = ridge([(150, 420), (220, 330), (270, 268), (310, 232), (350, 262), (400, 300), (470, 420)], 4, 6)
    out.append(hill(D, mt, 620, ("#F6D8B8", "#D8A890", "#A87A70"), 4, inkw=0, lit="#FFF6E0"))
    out.append(ray_fan(sx, sy, 30, 520, 26, "#FFF6D8", 0.16, a0=60, a1=120, w=0.035, seed=4))
    # receding ranks of cedars, paler and bluer with distance
    for k, (cx_, hh, ww) in enumerate(((150, 210, 12), (470, 230, 14), (210, 170, 10), (420, 180, 10))):
        out.append(cedar(D, cx_, 430, hh, ww, 40 + k, pal=("#C8B8A0", "#A08A84", "#7A6A70"), trunk=("#B89A88", "#9A8078", "#7A6468"), lit=1 if cx_ < 300 else -1,
                         tiers=5, spread=0.9, haze=("#F2D2B0", 0.35)))
    out.append(mist(D, 430, 60, 3, "#FFE8C8", 0.6))
    for k, (cx_, hh, ww) in enumerate(((96, 290, 18), (520, 300, 18))):
        out.append(cedar(D, cx_, 470, hh, ww, 50 + k, pal=("#8AA08A", "#5A7466", "#34483E"), trunk=("#9A7A66", "#6A5244", "#3A2A24"), lit=1 if cx_ < 300 else -1,
                         tiers=6, spread=0.72, haze=("#F2D2A8", 0.26)))
    # shafts of evening light slanting through the gap, motes of dust in them
    for k, (x0_, w0_) in enumerate(((236, 26), (290, 40), (350, 22))):
        g = D.lin([(0, "#FFF2C8", 0.0), (0.35, "#FFF2C8", 0.1), (1, "#FFF2C8", 0)], 0, 0, 0, 1)
        for e in (0, 8, 16):
            out.append(f'<path d="M {x0_ - e:.1f} 250 L {x0_ + w0_ + e:.1f} 250 L {x0_ + w0_ * 3 + (k - 1) * 60 + e * 2:.1f} 470 L {x0_ - w0_ + (k - 1) * 60 - e * 2:.1f} 470 Z" fill="{g}"/>')
    out.append(specks(5, (200, 300, 420, 460), ["#FFF6D8", "#FFE8A0"], 40, (0.8, 1.8), (0.4, 0.9)))
    out.append(bird_v(400, 210, 11, "#5A3A3A", 0.8) + bird_v(426, 224, 8, "#5A3A3A", 0.7))
    # the forest floor and the road the heroes take, lit down the middle
    gnd = [(-20, 470), (140, 456), (300, 448), (460, 456), (620, 470)]
    out.append(hill(D, gnd, 620, ("#C89A6A", "#8A6A44", "#3A2A1A"), 7, inkw=0))
    road = [(250, 452), (350, 452), (440, 620), (160, 620)]
    g = D.lin([(0, "#FFE8B0", 0.7), (1, "#E8B878", 0.2)])
    out.append(f'<path d="{smooth_closed(road)}" fill="{g}"/>')
    out.append(grass(8, (0, 460, 600, 520), ["#7A8A4A", "#3A4A22", "#A8A060"], 120, (6, 16), 1.4))
    # the two nearest cedars, colossal, framing the plate; their trunks run off the top
    fg = ("#7A9A86", "#3E5E52", "#162A24")
    for (x0_, x1_) in ((-30, 50), (550, 630)):
        out.append(painted(D, [(x0_, 600), (x0_ + 6, -10), (x1_ - 6, -10), (x1_, 600)], ("#A87A58", "#5A3A26", "#1E120A"), x0_ + 99, sk=0.25, angle=-90, n=30, inkw=0, hi=0.3))
    out.append(cedar(D, 14, 560, 400, 70, 61, pal=fg, trunk=("#A87A58", "#5A3A26", "#1E120A"), lit=1, rim="#FFD890", tiers=5, spread=0.62))
    out.append(cedar(D, 592, 560, 420, 64, 62, pal=fg, trunk=("#A87A58", "#5A3A26", "#1E120A"), lit=-1, rim="#FFD890", tiers=5, spread=0.6))
    # Gilgamesh and Enkidu walking into the forest, axes on their shoulders
    out.append(cast(D, 300, 470, 70, 6, "#2A1A0A", 0.5, 2))
    out.append(hero_with_axe(D, 334, 468, 0.62, "#1E140E", "#FFE0A0"))
    out.append(hero_with_axe(D, 268, 472, 0.64, "#1E140E", "#FFE0A0", flip=True, hair=True))
    # the clay tablet at the foot of the plate
    tab = [(-20, 620), (-20, 492), (60, 486), (140, 492), (220, 488), (300, 494), (380, 488), (460, 492), (540, 486), (620, 490), (620, 620)]
    out.append(painted(D, tab, ("#F2D8B0", "#D8B080", "#8A6A44"), 70, sdir=(0.2, 0.8), sk=0.06, angle=0, n=60, inkw=1.6, inkc="#5A3A22", hi=0.4))
    out.append(cuneiform_rows(D, 52, 548, 496, 520, 2, 71, s=0.9))
    out.append(cuneiform_rows(D, 52, 548, 554, 576, 2, 72, s=0.9))
    out.append(tx(300, 546, "The oldest story ever written", SERIF_IT, 26, "#4A2A14", max_w=430))
    # lettering
    out.append(gilt(D, 300, 100, "GILGAMESH", CINZEL, 58, ls=10, max_w=420, seed=16, deboss="#2A1008", dop=0.8))
    out.append(tx(300, 130, "MESOPOTAMIAN · INTO THE CEDARS", CINZEL, 17, "#3A1E14", ls=2, max_w=440))
    return fin(D, out, 39)


# ================================================================ 27. quetzalcoatl — the feathered serpent at dawn
def quetzal_feather(cx, cy, L, W, ang, seed, pal=("#8AF0B0", "#1EA868", "#0A4A3A"), tip="#1E6AC8"):
    """One long quetzal tail plume: tapered vane with a darker rachis and an iridescent blue-green tip."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    bend = rnd.uniform(-0.12, 0.12)
    pts = []
    for i in range(9):
        t = i / 8
        w = W * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 - 0.25 * t)
        c = (cx + ux * L * t + nx * L * bend * t * t, cy + uy * L * t + ny * L * bend * t * t)
        pts.append(((c[0] + nx * w), (c[1] + ny * w), (c[0] - nx * w), (c[1] - ny * w)))
    left = [(p[0], p[1]) for p in pts]
    right = [(p[2], p[3]) for p in pts][::-1]
    out = [poly(left + right, pal[1])]
    out.append(poly(left[:6] + [((left[6][0] + right[2][0]) / 2, (left[6][1] + right[2][1]) / 2)] + right[-6:], pal[2], 0.35))
    out.append(poly(left[5:] + right[:4], tip, 0.55))
    mid = [((p[0] + p[2]) / 2, (p[1] + p[3]) / 2) for p in pts]
    out.append(taper(mid[:-1], 1.6, 0.6, pal[2], 0.8))
    out.append(taper([(x - nx * W * 0.35, y - ny * W * 0.35) for x, y in mid[1:-2]], 1.4, 0.4, pal[0], 0.7))
    return "".join(out)


def feathered_serpent(D, spine_pts, w, seed, pal=("#9AE0C0", "#2A9A86", "#0A3A3A"), belly=("#FFF2B0", "#E8B84A", "#8A5A14")):
    """The body of the plumed serpent along spine_pts (tail first): jade scales, gold belly scutes, a rattle at
    the tail, and long quetzal plumes streaming back from the spine. Returns (svg, head point, head angle)."""
    path = catmull(spine_pts, 10)
    n = len(path)
    widths = [w * (0.18 + 0.82 * min(1, (i / (n - 1)) * 1.6) ** 0.8) for i in range(n)]
    left, right, norms = [], [], []
    for i, (x, y) in enumerate(path):
        a = path[max(0, i - 1)]
        b = path[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / L_, dx / L_
        norms.append((nx, ny, dx / L_, dy / L_))
        left.append((x + nx * widths[i] / 2, y + ny * widths[i] / 2))
        right.append((x - nx * widths[i] / 2, y - ny * widths[i] / 2))
    rnd = random.Random(seed)
    out = []
    # plumes behind the body: streaming backward from the back (the 'left' edge)
    for i in range(n - 6, 3, -3):
        x, y = left[i]
        nx, ny, ux, uy = norms[i]
        ang = math.degrees(math.atan2(ny * 0.8 - uy * 0.9, nx * 0.8 - ux * 0.9))
        L = widths[i] * rnd.uniform(1.6, 2.4)
        out.append(quetzal_feather(x, y, L, widths[i] * 0.2, ang + rnd.uniform(-10, 10), seed + i,
                                   pal=rnd.choice([("#8AF0B0", "#1EA868", "#0A4A3A"), ("#B8F0A0", "#4AB84A", "#1A5A2A"), ("#7AE0D0", "#14988A", "#0A3A44")])))
    # the rattle
    tx_, ty_ = path[0]
    nx, ny, ux, uy = norms[0]
    for k in range(4):
        cx_, cy_ = tx_ - ux * (k * 7 + 4), ty_ - uy * (k * 7 + 4)
        out.append(f'<path d="{blob(cx_, cy_, 6 - k, 5 - k * 0.8, seed + k, 0.05, 10, math.degrees(math.atan2(uy, ux)))}" fill="#E8C88A" stroke="#6A4A1A" stroke-width="1.2"/>')
    body = left + right[::-1]
    out.append(painted(D, body, pal, seed, sdir=(0.3, 0.8), sk=0.22, angle=-20, n=80, inkw=1.8, inkc="#06201E", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    sc = []
    # belly scutes in gold along the lower edge
    bel = []
    for i in range(n):
        x, y = right[i]
        nx, ny, ux, uy = norms[i]
        bel.append((x + nx * widths[i] * 0.3, y + ny * widths[i] * 0.3))
    sc.append(f'<path d="{smooth_closed(right + bel[::-1])}" fill="{belly[1]}"/>')
    for i in range(1, n - 1):
        x, y = right[i]
        nx, ny, ux, uy = norms[i]
        sc.append(f'<path d="M {x:.1f} {y:.1f} l {nx * widths[i] * 0.32:.1f} {ny * widths[i] * 0.32:.1f}" stroke="{belly[2]}" stroke-width="1.2" opacity="0.7"/>')
    sc.append(taper([(x + norms[i][0] * widths[i] * 0.08, y + norms[i][1] * widths[i] * 0.08) for i, (x, y) in enumerate(right)], 2, 4, belly[0], 0.6))
    # jade scales in rows, a diamond chain down the back
    for i in range(2, n - 1, 2):
        x, y = path[i]
        nx, ny, ux, uy = norms[i]
        ww = widths[i]
        for j in (-0.32, -0.12, 0.08):
            sx, sy = x + nx * ww * j, y + ny * ww * j
            r = ww * 0.12
            sc.append(f'<path d="M {sx - nx * r:.1f} {sy - ny * r:.1f} Q {sx - ux * r * 1.4:.1f} {sy - uy * r * 1.4:.1f} {sx + nx * r:.1f} {sy + ny * r:.1f}" stroke="{pal[2]}" stroke-width="1.1" fill="none" opacity="0.6"/>')
        if i % 6 == 0:
            dx_, dy_ = x + nx * ww * 0.22, y + ny * ww * 0.22
            d = ww * 0.13
            sc.append(f'<path d="M {dx_ - ux * d * 1.6:.1f} {dy_ - uy * d * 1.6:.1f} L {dx_ + nx * d:.1f} {dy_ + ny * d:.1f} L {dx_ + ux * d * 1.6:.1f} {dy_ + uy * d * 1.6:.1f} L {dx_ - nx * d:.1f} {dy_ - ny * d:.1f} Z" fill="#E8C84A" opacity="0.75" stroke="#0A3A3A" stroke-width="1"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(ink(smooth_open(left[4:]), "#E8FFF0", 2, seed, 1, 0.5))
    hx, hy = path[-1]
    ha = math.degrees(math.atan2(path[-1][1] - path[-4][1], path[-1][0] - path[-4][0]))
    return "".join(out), (hx, hy), ha


def serpent_head(D, x, y, s, ang, seed, flip=False, pal=("#9AE0C0", "#2A9A86", "#0A3A3A")):
    """The plumed serpent's head in profile along +x: jaws open, curling fangs, forked tongue, a heavy scrolled
    brow over the eye, a crest of plumes and a ruff of feathers round the neck."""
    def L(pts):
        return T(pts, x, y, s, flip, ang)
    out = []
    rnd = random.Random(seed)
    # neck ruff: a corona of feathers fanned behind the head
    for k in range(13):
        a = -200 + k * 26 + rnd.uniform(-6, 6)
        px, py = L([(-14, 0)])[0]
        aa = a + (ang if not flip else 180 - ang)
        out.append(quetzal_feather(px, py, 74 * s * rnd.uniform(0.85, 1.1), 9 * s, aa, seed + k,
                                   pal=[("#8AF0B0", "#1EA868", "#0A4A3A"), ("#FFE08A", "#E8A030", "#8A4A10"), ("#7AE0D0", "#14988A", "#0A3A44")][k % 3],
                                   tip=["#1E6AC8", "#C8302A", "#1E6AC8"][k % 3]))
    # crest plumes sweeping back from the brow
    for k in range(5):
        px, py = L([(14 - k * 4, -26)])[0]
        aa = (-150 - k * 9) if not flip else (-30 + k * 9)
        aa += ang if not flip else -ang
        out.append(quetzal_feather(px, py, 90 * s, 7 * s, aa, seed + 30 + k))
    lower = L([(-6, 8), (20, 14), (50, 26), (74, 30), (78, 24), (56, 16), (30, 6)])
    out.append(painted(D, lower, pal, seed + 1, sk=0.2, n=8, inkw=1.6, inkc="#06201E", hi=0.4))
    out.append(poly(L([(16, 4), (72, 22), (70, 12), (22, -2)]), "#8A1A2A"))
    upper = L([(-20, 10), (-24, -12), (-10, -28), (14, -32), (40, -26), (66, -18), (84, -10), (88, -2), (80, 6), (60, 6), (34, 2), (8, 6)])
    out.append(painted(D, upper, pal, seed, sk=0.2, n=14, inkw=1.6, inkc="#06201E", hi=0.5))
    # fangs
    for (a0, a1) in (((70, 6), (66, 22)), ((56, 6), (54, 16))):
        out.append(taper(L([a0, ((a0[0] + a1[0]) / 2 + 1, (a0[1] + a1[1]) / 2), a1]), 4.4 * s, 0.8 * s, "#FFFDF0"))
    # forked tongue
    t0 = L([(74, 14), (100, 18), (114, 10)])
    out.append(taper(catmull(t0, 5), 3 * s, 1.6 * s, "#C8202A"))
    out.append(taper(L([(114, 10), (124, 2)]), 1.8 * s, 0.8 * s, "#C8202A"))
    out.append(taper(L([(114, 10), (126, 14)]), 1.8 * s, 0.8 * s, "#C8202A"))
    # scrolled brow plate, the eye under it, nostril curl, scale rows
    out.append(painted(D, L([(-2, -30), (18, -40), (40, -34), (44, -24), (30, -22), (12, -20)]), ("#FFF2B0", "#E8B84A", "#8A5A14"), seed + 2, sk=0.2, n=6, inkw=1.4, inkc="#4A2A08", hi=0.5))
    sp = [L([(40 - 10 * t * math.cos(t * 5), -30 + 8 * t * math.sin(t * 5))])[0] for t in [i / 10 for i in range(11)]]
    out.append(pline(sp, "#6A3A08", 1.6 * s, seed, 0.9, 1))
    ex, ey = L([(22, -16)])[0]
    out.append(f'<path d="{blob(ex, ey, 6.6 * s, 5 * s, seed, 0.04, 12, ang)}" fill="#FFE04A" stroke="#06201E" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(ex + 1, ey, 1.6 * s, 4.2 * s, seed + 1, 0.02, 8, ang)}" fill="#06100E"/>')
    out.append(f'<circle cx="{ex - 2 * s:.1f}" cy="{ey - 2 * s:.1f}" r="{1.3 * s:.1f}" fill="#FFFFFF"/>')
    nx_, ny_ = L([(78, -10)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{2.4 * s:.1f}" fill="#06201E"/>')
    cid = D.clip(f'<path d="{smooth_closed(upper)}"/>')
    sc = []
    for r in range(3):
        for c in range(8):
            px, py = L([(-14 + c * 11 + r * 5, -2 + r * -8)])[0]
            sc.append(f'<path d="{blob(px, py, 3.6 * s, 3 * s, r * 10 + c, 0.1, 8)}" fill="none" stroke="{pal[2]}" stroke-width="1" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    return "".join(out)


def stepped_fret(x0, x1, y, h, col, bg=None, w=2.6):
    """Xicalcoliuhqui: the Mesoamerican stepped fret, a band of step-and-spiral motifs."""
    out = []
    if bg:
        out.append(f'<rect x="{x0}" y="{y - h / 2:.1f}" width="{x1 - x0}" height="{h:.1f}" fill="{bg}"/>')
    u = h * 1.6
    x = x0
    k = 0
    while x < x1:
        a, b = y - h * 0.38, y + h * 0.38
        st = h * 0.19
        # steps rising to the right, then a hooked spiral
        d = (f"M {x:.1f} {b:.1f} L {x:.1f} {b - st:.1f} L {x + st:.1f} {b - st:.1f} L {x + st:.1f} {b - 2 * st:.1f} L {x + 2 * st:.1f} {b - 2 * st:.1f} "
             f"L {x + 2 * st:.1f} {a:.1f} L {x + u * 0.9:.1f} {a:.1f} L {x + u * 0.9:.1f} {y + st * 0.6:.1f} L {x + u * 0.6:.1f} {y + st * 0.6:.1f} L {x + u * 0.6:.1f} {y - st * 0.6:.1f}")
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="miter"/>')
        out.append(f'<path d="M {x:.1f} {b:.1f} L {x + u:.1f} {b:.1f}" stroke="{col}" stroke-width="{w}"/>')
        x += u
        k += 1
    return "".join(out)


def step_pyramid(D, cx, base, w, h, seed, tiers=7, lit=("#F6D0A0", "#D8A070", "#8A5A3A"), shade=("#A87A6A", "#7A5048", "#3A2220")):
    """A stepped temple-pyramid seen from the front with a little of its shaded right flank: terraces with lit
    treads and shadowed risers, the central stair with its balustrades, and the temple on the summit."""
    out = []
    th = h * 0.8 / tiers
    top_w = w * 0.34
    for i in range(tiers):
        t0, t1 = i / tiers, (i + 1) / tiers
        y0, y1 = base - h * 0.8 * t0, base - h * 0.8 * t1
        w0, w1 = w - (w - top_w) * t0, w - (w - top_w) * t1
        face = [(cx - w0 / 2, y0), (cx - w1 / 2 + 3, y1 + th * 0.18), (cx + w1 / 2 - 3, y1 + th * 0.18), (cx + w0 / 2, y0)]
        out.append(sharp(face, lit[1]))
        g = D.lin([(0, lit[0], 0.6), (0.5, lit[1], 0), (1, shade[1], 0.85)], 0, 0, 1, 0)
        out.append(sharp(face, g))
        out.append(f'<path d="M {cx - w1 / 2 + 3:.1f} {y1 + th * 0.18:.1f} L {cx + w1 / 2 - 3:.1f} {y1 + th * 0.18:.1f}" stroke="{lit[0]}" stroke-width="2.4" opacity="0.8"/>')
        out.append(f'<path d="M {cx - w0 / 2:.1f} {y0:.1f} L {cx + w0 / 2:.1f} {y0:.1f}" stroke="{shade[2]}" stroke-width="1.4" opacity="0.6"/>')
        # the shaded right flank
        out.append(sharp([(cx + w0 / 2, y0), (cx + w1 / 2 - 3, y1 + th * 0.18), (cx + w1 / 2 + 8, y1 + th * 0.12), (cx + w0 / 2 + 12, y0 - 2)], shade[2], 0.8))
        out.append(stone_blocks(D, pd(face), (cx - w0 / 2, y1, cx + w0 / 2, y0), seed + i, shade[2], rows=2, op=0.25, w=1))
    # the central stair and balustrades
    sw0, sw1 = w * 0.18, top_w * 0.4
    ytop = base - h * 0.8
    stair = [(cx - sw0 / 2, base), (cx - sw1 / 2, ytop), (cx + sw1 / 2, ytop), (cx + sw0 / 2, base)]
    out.append(sharp(stair, lit[1]))
    out.append(sharp(stair, D.lin([(0, "#FFFFFF", 0.25), (1, shade[1], 0.4)], 0, 0, 1, 0)))
    n = 30
    for k in range(n):
        t = k / n
        yy = base - (base - ytop) * t
        ww = sw0 + (sw1 - sw0) * t
        out.append(f'<path d="M {cx - ww / 2:.1f} {yy:.1f} L {cx + ww / 2:.1f} {yy:.1f}" stroke="{shade[2]}" stroke-width="1" opacity="0.5"/>')
    for sg in (-1, 1):
        out.append(taper([(cx + sg * sw0 / 2, base), (cx + sg * sw1 / 2, ytop)], 7, 4, shade[1] if sg > 0 else lit[0]))
    # the temple on the summit
    tw, tt = top_w * 0.78, h * 0.2
    temple = [(cx - tw / 2, ytop), (cx - tw / 2, ytop - tt * 0.7), (cx + tw / 2, ytop - tt * 0.7), (cx + tw / 2, ytop)]
    out.append(sharp(temple, lit[1]))
    out.append(sharp(temple, D.lin([(0, lit[0], 0.5), (1, shade[1], 0.8)], 0, 0, 1, 0)))
    out.append(sharp([(cx - tw / 2 - 4, ytop - tt * 0.7), (cx + tw / 2 + 4, ytop - tt * 0.7), (cx + tw / 2, ytop - tt), (cx - tw / 2, ytop - tt)], shade[1]))
    for dx in (-tw * 0.22, 0, tw * 0.22):
        out.append(f'<path d="M {cx + dx - tw * 0.07:.1f} {ytop:.1f} L {cx + dx - tw * 0.07:.1f} {ytop - tt * 0.5:.1f} L {cx + dx + tw * 0.07:.1f} {ytop - tt * 0.5:.1f} L {cx + dx + tw * 0.07:.1f} {ytop:.1f} Z" fill="#2A1410"/>')
    out.append(soft_glow(D, cx, ytop - tt * 0.25, tw * 0.5, "#FFB040", 0.5))
    return "".join(out)


@design("quetzalcoatl")
def quetzalcoatl():
    D = Doc2("my-qz")
    out = [sky(D, [(0, "#0A2A3E"), (0.32, "#1E5A6A"), (0.58, "#E89A6A"), (0.74, "#FCD48A"), (0.82, "#FFF0C0")], 1, 470, ["#2A6A7A", "#0A2A3E", "#F6B87A"], 60)]
    out.append(stars_field(6, (0, 0, 600, 200), 50))
    # the morning star: Venus, the serpent's own light
    vx, vy = 112, 196
    out.append(soft_glow(D, vx, vy, 70, "#FFFFFF", 0.7))
    out.append(star4(vx, vy, 16, "#FFFFFF") + star4(vx, vy, 7, "#FFFFFF"))
    out.append(soft_glow(D, 300, 470, 340, "#FFE6A0", 0.55))
    for (x, y, w_, sd) in ((480, 300, 170, 3), (150, 330, 150, 4)):
        out.append(puff_cloud(D, x, y, w_, sd, ("#FFE0C0", "#E8A08A", "#8A5A6A"), op=0.85))
    # far hills and the jungle, mist in the hollows, the pyramid rising from the trees
    far = ridge([(-20, 430), (100, 400), (220, 420), (330, 396), (460, 418), (620, 400)], 5, 6)
    out.append(hill(D, far, 620, ("#9AA08A", "#6A7A6A", "#3A4A44"), 5, inkw=0))
    out.append(step_pyramid(D, 360, 474, 260, 210, 6))
    out.append(mist(D, 450, 40, 4, "#FFF0D0", 0.65))
    for k in range(16):
        x = -20 + k * 42
        out.append(dab_crown(D, x, 486 + (k % 3) * 8, 46, 30, [("#8AB060", "#3A6A3A", "#143018"), ("#A8B860", "#5A7A3A", "#1E3A1A")], 80 + k, n=40, size=(6, 12), light=(-0.6, -0.8), inkw=0))
    for k in range(4):
        out.append(palm(D, (40 + k * 160 + (k % 2) * 30, 560), (30 + k * 160 + (k % 2) * 40, 440 + (k % 2) * 20), 90 + k, L=50, width=8,
                        leaf_cols=["#2A5A3A", "#3A7A4A", "#1A3A24"], trunk=("#7A6A4A", "#4A3A2A", "#2A2016"), nuts=False, rings=False))
    out.append(painted(D, [(-20, 620), (-20, 520), (150, 506), (300, 516), (450, 506), (620, 520), (620, 620)], ("#3A6A3A", "#1E4A2A", "#0A2414"), 99, sk=0.1, angle=0, n=40, inkw=0, hi=0.3))
    # the feathered serpent sweeping across the dawn
    spine = [(640, 420), (560, 330), (450, 290), (350, 320), (250, 360), (170, 330), (150, 270), (190, 226), (250, 214)]
    svg, (hx, hy), ha = feathered_serpent(D, spine, 46, 7)
    out.append(svg)
    out.append(serpent_head(D, hx - 8, hy + 2, 1.12, ha - 12, 8))
    # the stepped-fret borders, top and foot
    out.append(f'<rect x="0" y="0" width="600" height="26" fill="#6A2A1A"/>')
    out.append(stepped_fret(-6, 610, 13, 18, "#E8B84A", w=2.2))
    out.append(f'<rect x="0" y="574" width="600" height="26" fill="#6A2A1A"/>')
    out.append(stepped_fret(-6, 610, 587, 18, "#E8B84A", w=2.2))
    # lettering
    out.append(gilt(D, 300, 100, "Quetzalcoatl", DMS, 64, max_w=440, seed=17, deboss="#04141E", dop=0.85))
    out.append(tx(300, 130, "AZTEC · THE FEATHERED SERPENT", CINZEL, 17, "#E8FFF6", ls=2.5, max_w=440))
    out.append(tx(301.5, 545.5, "He brought maize, books and the calendar", SERIF_IT, 24, "#000000", max_w=440, op=0.6))
    out.append(tx(300, 544, "He brought maize, books and the calendar", SERIF_IT, 24, "#FFF6E0", max_w=440))
    return fin(D, out, 40)


# ================================================================ 28. baba yaga's hut — the izba on chicken legs
def chicken_leg(D, hip, hock, foot, s, seed, lift=0.0, flip=False):
    """A great hen's leg: a feathered drumstick from the hip, a scaly yellow shank bending at the hock, three
    clawed toes forward and one behind. lift curls the toes as the foot rises."""
    out = []
    rnd = random.Random(seed)
    # feathered thigh
    th = catmull([hip, ((hip[0] + hock[0]) / 2 + (8 if not flip else -8) * s, (hip[1] + hock[1]) / 2), hock], 6)
    out.append(taper(th, 46 * s, 20 * s, "#8A5A3A"))
    for k in range(18):
        t = rnd.uniform(0.05, 0.85)
        i = int(t * (len(th) - 1))
        x, y = th[i]
        w = (46 - 26 * t) * s * 0.42
        fx = x + rnd.uniform(-w, w)
        out.append(f'<path d="M {fx:.1f} {y - 4 * s:.1f} q {rnd.uniform(-4, 4) * s:.1f} {8 * s:.1f} {rnd.uniform(-2, 2) * s:.1f} {14 * s:.1f}" stroke="{rnd.choice(["#C8905A", "#5A3420", "#E8B87A"])}" stroke-width="{2.2 * s:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    # scaly shank
    sh = [hock, foot]
    out.append(taper(sh, 15 * s, 11 * s, "#E8A83A"))
    out.append(taper([(hock[0] - 3 * s, hock[1]), (foot[0] - 3 * s, foot[1])], 4 * s, 3 * s, "#FFE08A", 0.7))
    L_ = math.hypot(foot[0] - hock[0], foot[1] - hock[1])
    for k in range(1, int(L_ / (6 * s))):
        t = k * 6 * s / L_
        x, y = hock[0] + (foot[0] - hock[0]) * t, hock[1] + (foot[1] - hock[1]) * t
        out.append(f'<path d="M {x - 6 * s:.1f} {y:.1f} q {6 * s:.1f} {3 * s:.1f} {12 * s:.1f} 0" stroke="#8A5A14" stroke-width="{1.2 * s:.1f}" fill="none" opacity="0.7"/>')
    out.append(f'<path d="{blob(hock[0], hock[1], 12 * s, 10 * s, seed, 0.1, 10)}" fill="#C8863A"/>')
    # toes splayed on the ground: out to each side and one toward us; they curl as the foot lifts
    fx, fy = foot
    for (dx, dy, ln) in ((-1, 0.18, 30), (1, 0.18, 30), (0.12, 1, 16), (-0.5, 0.5, 18)):
        dy2 = dy + lift * 0.9
        p = [(fx, fy), (fx + dx * ln * 0.5 * s, fy + (dy2 * ln * 0.5 - 2) * s), (fx + dx * ln * s, fy + dy2 * ln * s)]
        out.append(taper(catmull(p, 4), 9 * s, 5 * s, "#E8A83A"))
        cx_, cy_ = p[-1]
        out.append(taper([(cx_, cy_), (cx_ + dx * 8 * s, cy_ + (3 + dy2 * 6) * s)], 4.4 * s, 0.8 * s, "#2A1A10"))
    out.append(f'<path d="{blob(fx, fy, 9 * s, 6 * s, seed + 3, 0.1, 10)}" fill="#E8A83A"/>')
    return "".join(out)


def izba(D, cx, floor, w, seed):
    """The hut: a log izba with a steep shingled roof seen gable-on, carved white bargeboards and window frame,
    blue shutters, a lamp-lit window, moss on the roof and a crooked chimney."""
    rnd = random.Random(seed)
    out = []
    x0, x1 = cx - w / 2, cx + w / 2
    wall_top = floor - w * 0.62
    apex = wall_top - w * 0.62
    # the roof planes behind the gable, shingled and mossy
    roof = poly_pts([(cx, apex - 12), (x1 + w * 0.16, wall_top + 18), (x0 - w * 0.16, wall_top + 18)], 6, seed, 0.6)
    out.append(painted(D, roof, ("#A8907A", "#6A5444", "#2A1E18"), seed, sdir=(0.4, 0.6), sk=0.2, angle=-60, n=40, inkw=1.6, inkc="#0A0606", hi=0.3))
    cid = D.clip(f'<path d="{pd(roof)}"/>')
    sh = []
    for r in range(14):
        y = apex + r * (wall_top + 18 - apex) / 13
        sh.append(f'<path d="M {x0 - w * 0.2:.1f} {y:.1f} L {x1 + w * 0.2:.1f} {y + rnd.uniform(-1, 1):.1f}" stroke="#1A1412" stroke-width="1.2" opacity="0.5"/>')
        xx = x0 - w * 0.2 + (r % 2) * 7
        while xx < x1 + w * 0.2:
            sh.append(f'<path d="M {xx:.1f} {y:.1f} l 0 {(wall_top + 18 - apex) / 13:.1f}" stroke="#1A1412" stroke-width="1" opacity="0.4"/>')
            xx += rnd.uniform(9, 15)
    for k in range(10):
        sh.append(f'<path d="{blob(rnd.uniform(x0 - w * 0.15, x1 + w * 0.15), rnd.uniform(apex + 30, wall_top + 14), rnd.uniform(8, 20), rnd.uniform(4, 8), k, 0.3, 10)}" fill="{rnd.choice(["#5A7A3A", "#7A9A4A", "#3A5A2A"])}" opacity="0.75"/>')
    out.append(f'<g {cid}>{"".join(sh)}</g>')
    # chimney
    chx = cx + w * 0.32
    ch = [(chx - 9, wall_top - w * 0.12), (chx - 8, wall_top - w * 0.42), (chx + 10, wall_top - w * 0.44), (chx + 11, wall_top - w * 0.18)]
    out.append(painted(D, ch, ("#B89A80", "#7A6050", "#3A2A20"), seed + 1, sk=0.2, n=6, inkw=1.4, inkc="#1A0E08", hi=0.3))
    # log walls
    logs = 9
    lh = (floor - wall_top) / logs
    for i in range(logs):
        y = wall_top + i * lh
        lg_ = [(x0 - 6, y + 1), (x1 + 6, y), (x1 + 6, y + lh), (x0 - 6, y + lh + 1)]
        out.append(painted(D, lg_, ("#C8946A", "#8A5A3A", "#3A2216"), seed + 10 + i, sdir=(0, 1), sk=0.3, angle=0, n=10, inkw=1.2, inkc="#1E1008", hi=0.5, hik=0.2))
        for ex_ in (x0 - 8, x1 + 8):
            out.append(f'<circle cx="{ex_:.1f}" cy="{y + lh / 2:.1f}" r="{lh * 0.55:.1f}" fill="#D8A878" stroke="#3A2216" stroke-width="1.4"/>')
            out.append(f'<circle cx="{ex_:.1f}" cy="{y + lh / 2:.1f}" r="{lh * 0.28:.1f}" fill="none" stroke="#8A5A3A" stroke-width="1"/>')
    # the gable: vertical boards and a little round window
    gab = poly_pts([(x0 + 4, wall_top + 2), (cx, apex + 6), (x1 - 4, wall_top + 2)], 6, seed + 1, 0.4)
    out.append(painted(D, gab, ("#B88A60", "#7A5034", "#3A2216"), seed + 2, sk=0.2, angle=-90, n=16, inkw=0, hi=0.4))
    cid = D.clip(f'<path d="{pd(gab)}"/>')
    out.append(f'<g {cid}>' + "".join(f'<path d="M {x:.1f} {apex:.1f} L {x:.1f} {wall_top + 4:.1f}" stroke="#3A2216" stroke-width="1.2" opacity="0.55"/>' for x in range(int(x0), int(x1), 9)) + '</g>')
    out.append(f'<circle cx="{cx}" cy="{wall_top - w * 0.2:.1f}" r="{w * 0.06:.1f}" fill="#FFD068" stroke="#F2EADA" stroke-width="3"/>')
    # carved bargeboards with scalloped edges and a horse-head ridge finial
    for sg in (-1, 1):
        a = (cx, apex - 4)
        b = (cx + sg * (w / 2 + w * 0.16), wall_top + 22)
        out.append(taper([a, b], 11, 11, "#F2EADA"))
        n = 9
        for k in range(1, n):
            t = k / n
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            out.append(f'<circle cx="{px - sg * 2:.1f}" cy="{py + 7:.1f}" r="4" fill="#F2EADA"/>')
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="#7A3A2A"/>')
        out.append(ink(smooth_open([a, b]), "#5A4A40", 1.2, seed + sg, 1, 0.7))
    hx, hy = cx, apex - 8
    out.append(poly([(hx - 3, hy + 4), (hx - 4, hy - 10), (hx + 2, hy - 20), (hx + 14, hy - 18), (hx + 16, hy - 12), (hx + 6, hy - 10), (hx + 4, hy + 4)], "#F2EADA"))
    # the window with its carved frame (nalichnik), blue shutters and the lamp inside
    wy0, wy1 = wall_top + lh * 1.6, wall_top + lh * 5.4
    ww = w * 0.24
    out.append(soft_glow(D, cx, (wy0 + wy1) / 2, w * 0.5, "#FFC060", 0.55))
    win = [(cx - ww / 2, wy1), (cx - ww / 2, wy0 + 6), (cx + ww / 2, wy0 + 6), (cx + ww / 2, wy1)]
    out.append(glow_window(D, win, seed + 3, frame="#3A2216"))
    out.append(sharp([(cx - ww / 2 - 8, wy0 + 6), (cx, wy0 - 22), (cx + ww / 2 + 8, wy0 + 6)], "#F2EADA"))
    out.append(sharp([(cx - ww / 2 + 2, wy0 + 2), (cx, wy0 - 14), (cx + ww / 2 - 2, wy0 + 2)], "#2A6A9A"))
    out.append(f'<circle cx="{cx}" cy="{wy0 - 5:.1f}" r="3" fill="#C8402A"/>')
    out.append(f'<rect x="{cx - ww / 2 - 10:.1f}" y="{wy1:.1f}" width="{ww + 20:.1f}" height="7" fill="#F2EADA" stroke="#5A4A40" stroke-width="1"/>')
    for sg in (-1, 1):
        shp = [(cx + sg * (ww / 2 + 3), wy0 + 6), (cx + sg * (ww / 2 + 3 + ww * 0.42), wy0 + 10), (cx + sg * (ww / 2 + 3 + ww * 0.42), wy1 - 2), (cx + sg * (ww / 2 + 3), wy1)]
        out.append(painted(D, shp, ("#6AA8D8", "#2A6A9A", "#123A5A"), seed + 4 + sg, sk=0.15, angle=-90, n=6, inkw=1.2, inkc="#0A1E30", hi=0.4))
        fx_, fy_ = cx + sg * (ww / 2 + 3 + ww * 0.21), (wy0 + wy1) / 2 + 3
        for k in range(5):
            a = math.radians(k * 72)
            out.append(f'<circle cx="{fx_ + math.cos(a) * 3.4:.1f}" cy="{fy_ + math.sin(a) * 3.4:.1f}" r="2.2" fill="#F2EADA"/>')
        out.append(f'<circle cx="{fx_:.1f}" cy="{fy_:.1f}" r="1.6" fill="#E8B84A"/>')
    # floor beam
    out.append(painted(D, [(x0 - 14, floor - 2), (x1 + 14, floor - 2), (x1 + 10, floor + 10), (x0 - 10, floor + 10)], ("#8A6A4A", "#4A3424", "#1A100A"), seed + 5, sk=0.2, angle=0, n=8, inkw=1.4, inkc="#0A0604", hi=0.3))
    return "".join(out), (chx, wall_top - w * 0.44)


@design("baba-yagas-hut")
def baba_yagas_hut():
    D = Doc2("my-by")
    out = [sky(D, [(0, "#0E1430"), (0.4, "#2A2A54"), (0.72, "#6A4A6A"), (0.88, "#A8707A")], 1, 520, ["#2A3A6A", "#0E1430", "#7A5A7A"], 60)]
    out.append(stars_field(8, (0, 0, 600, 300), 110))
    mx, my = 462, 226
    out.append(moon(D, mx, my, 58, 9, pal=("#FFFBEA", "#F6EACA", "#D2C29A"), glow="#FFF0D0", gs=0.5))
    # Baba Yaga herself, far off, flying across the moon in her mortar, sweeping her tracks with a broom
    bx, by = mx - 4, my + 8
    sil = "#14101E"
    out.append(poly([(bx - 16, by - 6), (bx + 16, by - 6), (bx + 11, by + 16), (bx - 11, by + 16)], sil))
    out.append(f'<path d="M {bx - 17} {by - 7} L {bx + 17} {by - 7}" stroke="{sil}" stroke-width="4" stroke-linecap="round"/>')
    out.append(poly([(bx - 9, by - 6), (bx - 11, by - 18), (bx - 6, by - 26), (bx + 2, by - 28), (bx + 8, by - 22), (bx + 9, by - 12), (bx + 7, by - 6)], sil))
    out.append(poly([(bx - 9, by - 22), (bx - 4, by - 34), (bx + 6, by - 33), (bx + 10, by - 24), (bx + 14, by - 16), (bx + 6, by - 20)], sil))
    out.append(sharp([(bx + 6, by - 30), (bx + 13, by - 29), (bx + 7, by - 26)], sil))
    out.append(taper([(bx + 2, by - 18), (bx + 20, by - 30), (bx + 30, by - 44)], 3, 2.4, sil))
    out.append(f'<path d="{blob(bx + 31, by - 46, 4.6, 3, 2, 0.1, 8, -50)}" fill="{sil}"/>')
    out.append(taper([(bx - 10, by + 4), (bx - 26, by + 16), (bx - 38, by + 22)], 2.4, 2, sil))
    out.append(poly([(bx - 36, by + 16), (bx - 56, by + 16), (bx - 54, by + 30), (bx - 38, by + 26)], sil))
    for k in range(6):
        out.append(f'<circle cx="{bx - 62 - k * 9:.1f}" cy="{by + 26 + k * 2.5:.1f}" r="{3.2 - k * 0.4:.1f}" fill="#FFF6E0" opacity="{0.6 - k * 0.09:.2f}"/>')
    # the forest: dark firs and pale birches
    for k in range(18):
        xx = -10 + k * 36 + (k * 13) % 17
        out.append(conifer(xx, 470, 120 + (k * 37) % 90, "#141A30" if k % 2 else "#1A2238", k, width=0.32))
    rnd = random.Random(10)
    for (bx_, bw, lean) in ((34, 16, 0.01), (86, 11, -0.03), (520, 12, 0.02), (570, 17, -0.01)):
        tr = [(bx_ - bw / 2, 520), (bx_ - bw * 0.4 + lean * 530, -10), (bx_ + bw * 0.4 + lean * 530, -10), (bx_ + bw / 2, 520)]
        out.append(painted(D, tr, ("#FFFFFF", "#E8E2DA", "#9A928A"), int(bx_), sk=0.2, angle=-90, n=10, inkw=0, hi=0.3))
        for j in range(22):
            yy = rnd.uniform(0, 500)
            xx_ = bx_ + lean * (520 - yy) * 1.08
            out.append(f'<path d="M {xx_ - bw * 0.4:.1f} {yy:.1f} l {bw * rnd.uniform(0.3, 0.7):.1f} {rnd.uniform(-1, 1):.1f}" stroke="#1A1418" stroke-width="{rnd.uniform(1.6, 3.2):.1f}" stroke-linecap="round"/>')
    out.append(mist(D, 470, 50, 5, "#B8A0C0", 0.5))
    # the clearing
    gnd = [(-20, 478), (120, 470), (300, 476), (480, 468), (620, 480)]
    out.append(hill(D, gnd, 620, ("#4A5A4A", "#26302A", "#0C120E"), 11, inkw=0))
    out.append(grass(12, (0, 474, 600, 600), ["#4A6A4A", "#1A2A1E", "#6A7A5A"], 200, (6, 18), 1.5))
    out.append(soft_glow(D, 300, 330, 230, "#FFC070", 0.35))
    # the hut, mid-step on its legs
    out.append(cast(D, 300, 492, 130, 10, "#000000", 0.5, 3))
    hut, (smx, smy) = izba(D, 300, 372, 170, 13)
    out.append(chicken_leg(D, (338, 370), (380, 420), (356, 462), 1.0, 14, lift=0.6, flip=True))
    out.append(chicken_leg(D, (262, 370), (226, 430), (252, 488), 1.05, 15))
    out.append(hut)
    out.append(smoke(D, [(smx + 1, smy), (smx + 10, smy - 20), (smx + 34, smy - 30), (smx + 60, smy - 26)], 4, 16, 6, "#C8B8D8", 0.55))
    # the palisade with lanterns glowing on its posts
    for (px, h_) in ((60, 86), (104, 74), (496, 76), (540, 88)):
        post = [(px - 7, 512), (px - 6, 512 - h_), (px, 506 - h_ - 8), (px + 6, 512 - h_), (px + 7, 512)]
        out.append(painted(D, post, ("#8A7A6A", "#4A3E34", "#1A1410"), px, sk=0.25, angle=-90, n=8, inkw=1.4, inkc="#0A0604", hi=0.3))
        ly = 512 - h_ - 18
        out.append(soft_glow(D, px, ly, 46, "#FFB040", 0.7))
        out.append(painted(D, blob_pts(px, ly, 9, 10, px, 0.04, 14), ("#FFF2B0", "#FFC040", "#C8701A"), px + 1, sk=0.15, n=4, inkw=1.2, inkc="#3A1A08", hi=0.6))
        out.append(f'<rect x="{px - 6}" y="{ly - 14}" width="12" height="4" fill="#2A1A10"/>')
    for (xa, xb, y_) in ((60, 104, 480), (496, 540, 478)):
        out.append(taper([(xa, y_), (xb, y_ + 3)], 6, 6, "#3A2E26"))
    # lettering
    out.append(letters(D, 300, 100, "Baba Yaga’s Hut", DMS, 62, "#FFF2D8", ["#FFFFFF", "#FFE0B0", "#F2D0C0"], 18, max_w=430,
                       shadow="#0A0818", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(tx(300, 132, "SLAVIC · THE HUT ON HEN’S LEGS", CINZEL, 17, "#F2E0E8", ls=2, max_w=440))
    out.append(tx(301.5, 545.5, "“Turn your back to the woods, your face to me.”", SERIF_IT, 23, "#000000", max_w=450, op=0.6))
    out.append(tx(300, 544, "“Turn your back to the woods, your face to me.”", SERIF_IT, 23, "#FFF2D8", max_w=450))
    return fin(D, out, 41)


# ================================================================ 29. maui's fishhook — fishing up the islands
def figure_hauling(x, base, s, col, rim=None):
    """A man in a canoe seen from the side (facing right), braced on one leg and leaning back, both arms
    out before him hauling on a line. About 150*s tall. Returns (svg, hands point)."""
    def L(pts):
        return T(pts, x, base, s)
    out = []
    out.append(taper(catmull(L([(-4, -62), (-18, -34), (-26, -2)]), 6), 14 * s, 8 * s, col))
    out.append(poly(L([(-34, 0), (-16, 0), (-18, -6), (-30, -6)]), col))
    out.append(taper(catmull(L([(4, -62), (26, -46), (40, -22)]), 6), 14 * s, 8 * s, col))
    out.append(poly(L([(36, -18), (52, -20), (50, -26), (38, -26)]), col))
    torso = L([(-10, -60), (12, -62), (10, -84), (4, -104), (-6, -122), (-22, -126), (-30, -116), (-26, -96), (-18, -76)])
    out.append(poly(torso, col))
    out.append(poly(L([(-14, -66), (14, -66), (16, -54), (6, -46), (-10, -50)]), col))
    out.append(poly(L([(-16, -124), (-12, -130), (-20, -132), (-24, -126)]), col))
    hx, hy = L([(-16, -140)])[0]
    out.append(f'<path d="{blob(hx, hy, 9 * s, 10 * s, 4, 0.06, 12, -15)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-22, -152)])[0], 5 * s, 5 * s, 5, 0.1, 10)}" fill="{col}"/>')
    hands = L([(40, -104)])[0]
    for (sh, el) in (((-8, -118), (14, -108)), ((-16, -114), (8, -100))):
        out.append(taper(catmull(L([sh, el, (40, -104)]), 6), 10 * s, 7 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(-8, -150), (-6, -142), (-8, -132), (-4, -120), (6, -106), (10, -86), (12, -64)])), rim, 2.0 * s, 3, 1, 0.9))
        out.append(ink(smooth_open(L([(-6, -118), (14, -110), (38, -106)])), rim, 1.6 * s, 4, 1, 0.8))
        out.append(ink(smooth_open(L([(8, -60), (28, -46), (42, -24)])), rim, 1.6 * s, 5, 1, 0.7))
    return "".join(out), hands


def paddler(x, base, s, col, rim=None, flip=False):
    """A seated paddler, side view, paddle dipped."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-14, 0), (16, 0), (12, -30), (4, -52), (-10, -52), (-16, -30)]), col)]
    hx, hy = L([(-2, -62)])[0]
    out.append(f'<path d="{blob(hx, hy, 8 * s, 9 * s, 3, 0.06, 12)}" fill="{col}"/>')
    p0, p1 = L([(20, -60), (40, 26)])
    out.append(taper([p0, p1], 3 * s, 3 * s, col))
    out.append(f'<path d="{blob(*L([(38, 18)])[0], 5 * s, 12 * s, 2, 0.05, 10, -14 if not flip else 14)}" fill="{col}"/>')
    out.append(taper(catmull(L([(2, -46), (18, -40), (24, -50)]), 5), 6 * s, 5 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(4, -70), (6, -60), (4, -52), (12, -30)])), rim, 1.6 * s, 6, 1, 0.8))
    return "".join(out)


def paddler_g(D, x, wl, h, seed, pal, L, rim, phase=0.0):
    """A kneeling paddler seen in profile (facing +x): torso leaning into the stroke, both hands on the paddle,
    blade in the water. Only what shows above the gunwale."""
    reach = 0.6 + 0.5 * math.sin(phase)
    J = pose("side", head=(1.25 + reach * 0.4, -6.85), neck=(0.95 + reach * 0.35, -6.3), sR=(0.85 + reach * 0.3, -5.85), sL=(0.75 + reach * 0.3, -5.85),
             hR=(0.0, -3.95), hL=(0.0, -3.95), eR=(1.5 + reach * 0.4, -5.2), wR=(1.6 + reach * 0.5, -5.9), eL=(1.4 + reach * 0.4, -4.5), wL=(1.9 + reach * 0.5, -4.1))
    B, M = human(D, x, wl + h * 0.48, h, J, pal, seed, L=L, rim=rim, rim_d=1.6, legs=False, fur_n=0.2)
    hc = J["head"]
    B.mass(M([(hc[0] - 0.4, hc[1] + 0.1), (hc[0] - 0.36, hc[1] - 0.48), (hc[0], hc[1] - 0.62), (hc[0] + 0.24, hc[1] - 0.5), (hc[0] - 0.05, hc[1] - 0.2),
              (hc[0] - 0.2, hc[1] + 0.3)]), flow=180, fur=0.6, shade=0.3)
    B.mass(M([(hc[0] - 0.2, hc[1] - 0.62), (hc[0] - 0.05, hc[1] - 0.95), (hc[0] + 0.18, hc[1] - 0.66)]), flow=-90, fur=0.3)
    out = [B.render()]
    a, b = M([J["wR"], (J["wL"][0] + 0.4, J["wL"][1] + 2.4)])
    out.append(taper([a, b], h * 0.03, h * 0.03, pal[2]))
    out.append(f'<path d="{blob(b[0], b[1] + h * 0.05, h * 0.05, h * 0.12, seed, 0.1, 10, -15)}" fill="{pal[2]}"/>')
    return "".join(out)


def bone_hook(D, cx, cy, s, seed, ang=0, water=None, sea_col="#1E4A6A"):
    """Manaiakalani: a great hook carved from bone, with a notched shank, a barbed point and lashing at the head."""
    def L(pts):
        return T(pts, cx, cy, s, False, ang)
    path = L([(0, -60), (2, -20), (0, 10), (12, 30), (32, 32), (44, 16), (42, -6)])
    out = [soft_glow(D, *L([(20, 0)])[0], 90 * s, "#FFF6D0", 0.7)]
    pp = catmull(path, 8)
    out.append(taper(pp, 15 * s, 7 * s, "#5A4630"))
    out.append(taper(pp, 12 * s, 5 * s, "#F6EEDA"))
    out.append(taper([(px - 2 * s, py - 1 * s) for px, py in pp[:len(pp) // 2]], 4 * s, 2 * s, "#FFFFFF", 0.8))
    bx, by = L([(42, -6)])[0]
    out.append(sharp(L([(42, -6), (32, -14), (40, -22), (46, -12)]), "#F6EEDA"))
    out.append(ink(smooth_open(pp), "#5A4630", 1.4 * s, seed, 1, 0.6))
    for k in range(5):
        a, b = L([(-6, -54 + k * 6), (6, -54 + k * 6)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#8A4A2A" stroke-width="{2 * s:.1f}"/>')
    for k in range(4):
        a, b = L([(-3, -32 + k * 9), (3, -30 + k * 9)])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#8A6A4A" stroke-width="{1.4 * s:.1f}" opacity="0.8"/>')
    for k in range(5):
        a = math.radians(-140 + k * 25)
        p0 = L([(4, -62)])[0]
        out.append(taper([p0, (p0[0] + math.cos(a) * 16 * s, p0[1] + math.sin(a) * 16 * s)], 3 * s, 1 * s, "#C8402A"))
    if water is not None:
        g = D.lin([(0, sea_col, 0), (0.08, sea_col, 0.3), (1, sea_col, 0.7)], 0, water, 0, water + 110 * s, "userSpaceOnUse")
        out.append(taper(pp, 15.5 * s, 7.5 * s, g))
        out.append(f'<path d="{smooth_closed(L([(42, -6), (32, -14), (40, -22), (46, -12)]))}" fill="{g}"/>')
    return "".join(out)


def waka(D, x0, x1, wl, seed, col="#2A140C", rim="#FFC080"):
    """A Polynesian canoe in side view: long dark hull with a painted band, a carved upswept stern post,
    a lower prow, and an outrigger float with its booms."""
    L_ = x1 - x0
    hull = [(x0 - 10, wl - 30), (x0 + L_ * 0.1, wl - 10), (x0 + L_ * 0.5, wl - 6), (x1 - L_ * 0.08, wl - 12), (x1 + 6, wl - 26), (x1, wl - 4), (x1 - L_ * 0.1, wl + 8),
            (x0 + L_ * 0.5, wl + 12), (x0 + L_ * 0.12, wl + 8), (x0 - 2, wl - 6)]
    out = [painted(D, hull, ("#8A4A2A", "#4A2414", col), seed, sdir=(0.5, 0.8), sk=0.2, angle=0, n=30, inkw=1.6, inkc="#0A0402", hi=0.3)]
    band = catmull([(x0 + 4, wl - 10), (x0 + L_ * 0.5, wl - 2), (x1 - 8, wl - 8)], 6)
    out.append(taper(band, 4, 4, "#E8C88A", 0.8))
    for k in range(10):
        t = (k + 0.5) / 10
        px, py = band[int(t * (len(band) - 1))]
        out.append(sharp([(px - 4, py + 2), (px, py - 3), (px + 4, py + 2)], "#C8402A"))
    # carved stern post curling up at the left end, a short prow piece at the right
    out.append(taper(catmull([(x0 - 6, wl - 26), (x0 - 18, wl - 60), (x0 - 10, wl - 96), (x0 + 4, wl - 104)], 8), 12, 5, col))
    for k in range(5):
        px, py = catmull([(x0 - 6, wl - 26), (x0 - 18, wl - 60), (x0 - 10, wl - 96), (x0 + 4, wl - 104)], 4)[2 + k * 2]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#E8C88A" opacity="0.8"/>')
    out.append(taper(catmull([(x1 + 2, wl - 24), (x1 + 16, wl - 40), (x1 + 26, wl - 42)], 6), 8, 3, col))
    out.append(ink(smooth_open(hull[:6]), rim, 2, seed, 1, 0.6))
    # outrigger float on the far side
    for bx in (x0 + L_ * 0.3, x0 + L_ * 0.66):
        out.append(taper([(bx, wl - 10), (bx + 10, wl - 26), (bx + 18, wl - 30)], 4, 3, col))
    return "".join(out)


def rising_island(D, cx, wl, w, h, seed):
    """An island heaved up from the deep: a green volcanic peak, terraces of forest, water and foam pouring
    off its shoulders, a few palms on the new shore."""
    rnd = random.Random(seed)
    out = []
    peak = ridge([(cx - w / 2, wl), (cx - w * 0.3, wl - h * 0.35), (cx - w * 0.12, wl - h * 0.8), (cx, wl - h), (cx + w * 0.1, wl - h * 0.86), (cx + w * 0.28, wl - h * 0.45),
                  (cx + w / 2, wl)], seed, 8)
    body = peak + [(cx + w / 2, wl + 10), (cx - w / 2, wl + 10)]
    out.append(painted(D, body, ("#9AC870", "#3A7A4A", "#123A2A"), seed, sdir=(0.6, 0.4), sk=0.22, angle=-70, n=80, inkw=1.6, inkc="#06180E", hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    tex = []
    # rock faces near the summit, forest dabs lower down, sunlit left flank
    tex.append(f'<path d="{blob(cx - w * 0.02, wl - h * 0.86, w * 0.1, h * 0.14, seed, 0.2, 12)}" fill="#6A5A4A" opacity="0.8"/>')
    for k in range(120):
        px, py = rnd.uniform(cx - w / 2, cx + w / 2), rnd.uniform(wl - h * 0.7, wl)
        tex.append(f'<path d="{blob(px, py, rnd.uniform(4, 9), rnd.uniform(3, 6), k, 0.2, 8)}" fill="{rnd.choice(["#5A9A4A", "#2A6A3A", "#B8D880", "#1A4A2A"])}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    g = D.lin([(0, "#FFD890", 0.5), (0.5, "#FFD890", 0), (1, "#06180E", 0.4)], 0, 0, 1, 0)
    tex.append(f'<path d="{smooth_closed(body)}" fill="{g}"/>')
    # waterfalls streaming from the heights
    for k in range(9):
        sx = cx + rnd.uniform(-w * 0.38, w * 0.38)
        sy = wl - h * rnd.uniform(0.35, 0.7)
        tex.append(taper(catmull([(sx, sy), (sx + rnd.uniform(-5, 5), sy + (wl - sy) * 0.35), (sx + rnd.uniform(-5, 5), sy + (wl - sy) * 0.7), (sx + rnd.uniform(-8, 8), wl + 4)], 6), rnd.uniform(1.2, 2.2), rnd.uniform(3, 6), "#F2FAFF", rnd.uniform(0.45, 0.75)))
    out.append(f'<g {cid}>{"".join(tex)}</g>')
    for k in range(4):
        px = cx - w * 0.36 + k * w * 0.14 + rnd.uniform(-6, 6)
        out.append(palm(D, (px, wl - 4), (px + rnd.uniform(-10, 10), wl - 44 - rnd.uniform(0, 12)), seed + k, L=24, width=4,
                        leaf_cols=["#2A5A3A", "#4A8A4A", "#1A3A24"], trunk=("#7A6A4A", "#4A3A2A", "#2A2016"), nuts=False, rings=False))
    # the sea boiling white where it breaks free
    for k in range(40):
        fx = cx + rnd.uniform(-w * 0.58, w * 0.58)
        out.append(f'<path d="{blob(fx, wl + rnd.uniform(-2, 8), rnd.uniform(8, 20), rnd.uniform(3, 6), k, 0.3, 10)}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    return "".join(out)


@design("mauis-fishhook")
def mauis_fishhook():
    D = Doc2("my-mh")
    out = [sky(D, [(0, "#14284A"), (0.35, "#3A5A8A"), (0.62, "#E89A7A"), (0.78, "#FCCC7A"), (0.86, "#FFF0C0")], 1, 470, ["#3A5A8A", "#14284A", "#F6B88A"], 60)]
    # the hook's own stars: Scorpius, the fishhook of Maui, fading in the dawn
    hook_stars = [(76, 168), (96, 186), (112, 204), (122, 226), (120, 250), (106, 266), (88, 266), (78, 254)]
    out.append(pline(hook_stars, "#E8F0FF", 1.2, 3, 0.35, 1))
    for k, (sx, sy) in enumerate(hook_stars):
        out.append(soft_glow(D, sx, sy, 10, "#FFFFFF", 0.6) + star4(sx, sy, 4.5 if k % 3 else 6, "#FFFFFF"))
    out.append(soft_glow(D, 60, 152, 14, "#FF8A6A", 0.8) + f'<circle cx="60" cy="152" r="3" fill="#FFB090"/>')
    out.append(stars_field(9, (0, 0, 600, 200), 40))
    # dawn: the sun on the rim of the sea
    sx_, sy_ = 290, 404
    out.append(soft_glow(D, sx_, sy_, 300, "#FFE6A0", 0.75))
    out.append(ray_fan(sx_, sy_, 40, 480, 22, "#FFF6D0", 0.14, a0=190, a1=350, w=0.04, seed=3))
    out.append(f'<circle cx="{sx_}" cy="{sy_}" r="38" fill="#FFF4C8"/>')
    for (x, y, w_, sd) in ((150, 330, 160, 3), (470, 250, 150, 4)):
        out.append(puff_cloud(D, x, y, w_, sd, ("#FFE8D0", "#F2A890", "#9A6A8A"), op=0.8))
    out.append(sea(D, 400, 620, [(0, "#F6C88A"), (0.25, "#5A7A9A"), (1, "#0E2440")], 6, ["#FFE0A8", "#0E2440", "#8AA8C8"], 90))
    rnd = random.Random(7)
    for k in range(40):
        y = 406 + (k / 40) ** 1.3 * 110
        w = 10 + (y - 400) * 0.9
        xx = sx_ + rnd.uniform(-w, w) * 0.5
        out.append(taper([(xx - w * 0.3, y), (xx, y - 1.4), (xx + w * 0.3, y)], 0.8, rnd.uniform(1.4, 3), "#FFF6D8", rnd.uniform(0.4, 0.9)))
    # the island coming up out of the sea on the line
    ix, iwl = 470, 410
    out.append(rising_island(D, ix, iwl, 250, 190, 8))
    # the swell and the canoe
    out.append(swell(D, 470, 8, 120, 1.0, ("#3A6A8A", "#1A3A5A", "#0A1A30"), 9))
    cnv = waka(D, 70, 300, 474, 10)
    fig, (hx, hy) = figure_hauling(160, 466, 0.82, "#140A08", rim="#FFD090")
    out.append(paddler(250, 470, 0.7, "#140A08", rim="#FFD090"))
    out.append(fig)
    out.append(cnv)
    out.append(swell(D, 500, 7, 90, 2.4, ("#2A5A7A", "#14304A", "#06122A"), 11))
    # the line, taut, from his hands down into the sea, where the bone hook glows under the island's root
    hk = (382, 418)
    line = catmull([(hx, hy), ((hx + hk[0]) / 2, (hy + hk[1]) / 2 - 14), hk], 10)
    out.append(taper(line, 2.6, 2.0, "#2A1A10"))
    out.append(taper([(px, py - 1) for px, py in line], 1, 0.8, "#FFE8B0", 0.8))
    out.append(soft_glow(D, hk[0] + 16, 476, 60, "#FFF6D0", 0.4))
    out.append(bone_hook(D, hk[0], hk[1] + 54, 0.9, 12, ang=-8, water=hk[1] + 2))
    out.append(wave_lines(13, (340, 424, 440, 500), ["#8AB8D8", "#FFF2D0"], 12, (10, 22), 1.4, 2, (0.3, 0.6)))
    for k in range(10):
        out.append(f'<path d="{blob(hk[0] + rnd.uniform(-14, 14), hk[1] + rnd.uniform(-2, 4), rnd.uniform(5, 10), rnd.uniform(2, 3.5), k, 0.3, 8)}" fill="#FFFFFF" opacity="0.85"/>')
    # birds wheeling over the new land
    for (bx, by, bs) in ((450, 192, 10), (476, 180, 8), (500, 200, 9), (430, 212, 7)):
        out.append(bird_v(bx, by, bs, "#3A2A3A", 0.8))
    # lettering
    out.append(gilt(D, 300, 104, "MAUI’S FISHHOOK", BEBAS, 76, ls=5, max_w=430, seed=18, deboss="#0A142A", dop=0.85))
    out.append(tx(300, 134, "POLYNESIAN · FISHER OF ISLANDS", CINZEL, 17, "#FFF2DC", ls=2, max_w=440))
    out.append(tx(301.5, 545.5, "Its hook still hangs among the stars", SERIF_IT, 25, "#000000", max_w=440, op=0.6))
    out.append(tx(300, 544, "Its hook still hangs among the stars", SERIF_IT, 25, "#FFF6E0", max_w=440))
    return fin(D, out, 42)


# ================================================================ 30. the simurgh — a Persian miniature
def tchi_cloud(pts, w, col, edge, seed):
    """A Persian 'tchi' cloud ribbon: a long tapering scarf of cloud that curls into a scroll at each end."""
    path = catmull(pts, 8)
    out = [taper(path, w * 0.4, w * 0.4, edge)]
    out.append(taper(path, w, w * 0.6, col))
    out.append(taper([(x, y - w * 0.2) for x, y in path], w * 0.3, w * 0.15, "#FFFFFF", 0.7))
    for end, sgn in ((path[0], -1), (path[-1], 1)):
        sp = []
        for i in range(14):
            t = i / 13
            a = math.radians(90 * sgn + t * 360 * sgn)
            r = w * 1.1 * (1 - t * 0.75)
            sp.append((end[0] + math.cos(a) * r, end[1] - w * 0.9 + math.sin(a) * r))
        out.append(taper(sp, w * 0.55, w * 0.2, col))
        out.append(pline(sp, edge, 1.2, seed, 0.7, 1))
    out.append(ink(smooth_open(path), edge, 1.2, seed, 1, 0.6))
    return "".join(out)


def sponge_rock(D, cx, cy, rx, ry, pal, seed):
    """The soft, cauliflower-like rocks of Persian painting: a lumpy mass with curling crease lines."""
    rnd = random.Random(seed)
    pts = []
    n = 14
    for k in range(n):
        a = math.pi * 2 * k / n
        r = 1 + (0.16 if k % 2 == 0 else -0.02) * rnd.uniform(0.5, 1.2)
        yy = math.sin(a)
        pts.append((cx + math.cos(a) * rx * r, cy + yy * ry * r * (1.0 if yy < 0 else 0.7)))
    out = [painted(D, pts, pal, seed, sdir=(0.4, 0.7), sk=0.25, angle=-60, n=16, inkw=1.6, inkc=dk(pal[2], 0.3), hi=0.55, hik=0.12)]
    for k in range(4):
        x = cx + rnd.uniform(-rx * 0.6, rx * 0.6)
        y = cy + rnd.uniform(-ry * 0.5, ry * 0.2)
        r = rnd.uniform(rx * 0.12, rx * 0.25)
        sp = [(x + math.cos(math.radians(200 + t * 220)) * r * (1 - t * 0.5), y + math.sin(math.radians(200 + t * 220)) * r * 0.7 * (1 - t * 0.5)) for t in [i / 8 for i in range(9)]]
        out.append(pline(sp, dk(pal[2], 0.2), 1.3, seed + k, 0.6, 1))
    return "".join(out)


def ribbon_plume(D, pts, w0, w1, pal, seed, eye=None):
    """A long feathered tail plume: a quill along pts with soft barbs sweeping back on both sides, banded in
    the plume's colours, and a peacock eye at the tip."""
    path = catmull(pts, 12)
    n = len(path)
    rnd = random.Random(seed)
    out = [taper(path, w0 * 0.55, w1 * 0.5, pal[2], 0.9)]
    for i in range(1, n - 1):
        (xa, ya), (xb, yb) = path[i - 1], path[i + 1]
        a = math.atan2(yb - ya, xb - xa)
        t = i / (n - 1)
        if i % 2:
            continue
        w = (w0 + (w1 - w0) * t) * (0.7 + 0.35 * t)
        col = pal[1] if (i // 6) % 3 else pal[0]
        x, y = path[i]
        for sg in (-1, 1):
            ba = a + sg * math.radians(118)
            ex, ey = x + math.cos(ba) * w, y + math.sin(ba) * w
            out.append(f'<path d="M {x:.1f} {y:.1f} Q {x + math.cos(ba - sg * 0.4) * w * 0.6:.1f} {y + math.sin(ba - sg * 0.4) * w * 0.6:.1f} {ex:.1f} {ey:.1f}" '
                       f'stroke="{col}" stroke-width="{max(1.6, w * 0.3):.1f}" stroke-linecap="round" fill="none" opacity="{rnd.uniform(0.8, 1):.2f}"/>')
            if i % 4 == 0:
                out.append(f'<path d="M {x:.1f} {y:.1f} L {ex:.1f} {ey:.1f}" stroke="{pal[2]}" stroke-width="0.8" opacity="0.5"/>')
    out.append(taper(path, 2.2, 1.0, pal[0], 0.95))
    if eye:
        ex, ey = path[-1]
        r = max(w0, w1) * 0.62
        out.append(f'<path d="{blob(ex, ey, r * 1.3, r * 1.05, seed, 0.05, 12)}" fill="{pal[1]}" stroke="{dk(pal[2], 0.2)}" stroke-width="1"/>')
        out.append(f'<path d="{blob(ex, ey, r * 0.85, r * 0.7, seed + 1, 0.05, 12)}" fill="{eye[0]}"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r * 0.38:.1f}" fill="{eye[1]}"/>')
    return "".join(out)


def simurgh(D, x, y, s, seed):
    """The Simurgh in flight as in Persian manuscripts: a slender crested bird with jewel-coloured wings raised,
    a hooked beak, and a tail of long curling ribbon plumes."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    LAP = ("#7A9AE0", "#2A4AA8", "#0E1E5A")
    RED = ("#F28A7A", "#C8302A", "#6A0E0E")
    TUR = ("#9AE8E0", "#2AA8A0", "#0E4E52")
    GLD = ("#FFF0A8", "#E8B84A", "#8A5A14")
    ROS = ("#FFC8D8", "#E8789A", "#7A2A44")
    # tail plumes, curling behind
    tails = [
        ([(-40, 8), (-90, 4), (-140, -26), (-186, -10), (-196, 30), (-172, 52)], RED),
        ([(-40, 10), (-96, 22), (-150, 18), (-200, 50), (-206, 96), (-180, 112)], LAP),
        ([(-40, 12), (-90, 36), (-130, 64), (-150, 110), (-136, 142), (-110, 140)], TUR),
        ([(-40, 14), (-80, 50), (-96, 96), (-82, 132), (-56, 140)], ROS),
        ([(-40, 6), (-110, -6), (-170, -50), (-210, -40), (-218, -6)], GLD),
    ]
    for k, (pp, pal) in enumerate(tails):
        out.append(ribbon_plume(D, L(pp), 22 * s, 14 * s, pal, seed + k, eye=(GLD[0], LAP[1]) if k % 2 == 0 else (TUR[0], RED[1])))
    # far wing
    def wing(sh, el, wr, prim_angles, prim_len, sec_angle, pals, sd, front):
        arm = catmull(L([sh, el, wr]), 8)
        o = []
        for i in range(len(arm) - 1, 0, -1):
            t = i / (len(arm) - 1)
            o.append(feather_fan(D, arm[i], [sec_angle + 20 * (1 - t)], [70 * s - 10 * t * s], 13 * s, pals, sd + i))
        o.append(feather_fan(D, arm[-1], prim_angles, [l * s for l in prim_len], 12 * s, pals, sd + 40))
        cov = arm + [(x_ + 20 * s * math.cos(math.radians(sec_angle)), y_ + 20 * s * math.sin(math.radians(sec_angle))) for x_, y_ in arm[::-1]]
        o.append(painted(D, cov, GLD, sd + 60, sk=0.15, angle=sec_angle, n=12, inkw=1.2, inkc="#5A3A08", hi=0.5))
        for i in range(1, len(arm), 2):
            o.append(feather_fan(D, arm[i], [sec_angle + 10], [26 * s], 8 * s, [TUR, GLD], sd + 80 + i))
        o.append(ink(smooth_open(arm), "#FFF6D0", 2, sd, 1, 0.8))
        return "".join(o)
    out.append(wing((-4, -10), (-30, -56), (-30, -104), [-110, -125, -140, -155, -170, -185], [96, 100, 98, 92, 84, 74], 160, [LAP, TUR, RED], seed + 100, False))
    body = L([(-46, 6), (-30, -6), (-4, -14), (22, -16), (34, -10), (34, 4), (18, 14), (-12, 18), (-38, 16)])
    out.append(painted(D, body, TUR, seed + 1, sdir=(0.3, 0.7), sk=0.2, angle=0, n=14, inkw=1.4, inkc="#06303A", hi=0.5))
    out.append(bird_feathers(D, body, [GLD[1], "#FFFFFF", TUR[2]], seed + 2, n=40, size=(3, 5), angle=0, op=(0.4, 0.8)))
    neck = L([(18, -12), (28, -30), (34, -48), (42, -64), (52, -72), (62, -68), (58, -56), (48, -42), (42, -24), (34, -4)])
    out.append(painted(D, neck, GLD, seed + 3, sdir=(0.4, 0.6), sk=0.15, n=10, inkw=1.4, inkc="#5A3A08", hi=0.5))
    out.append(bird_feathers(D, neck, [RED[1], LAP[1], GLD[0]], seed + 4, n=20, size=(2.5, 4), angle=60, op=(0.5, 0.9)))
    # crest plumes streaming back from the crown
    for k, (pts, pal) in enumerate((([(54, -76), (40, -98), (18, -108), (2, -100)], RED), ([(52, -74), (32, -88), (12, -88)], LAP), ([(56, -78), (52, -102), (40, -118)], TUR))):
        out.append(ribbon_plume(D, L(pts), 9 * s, 6 * s, pal, seed + 10 + k, eye=(GLD[0], RED[1])))
    head = L([(48, -66), (52, -76), (62, -78), (68, -72), (66, -62), (56, -60)])
    out.append(painted(D, head, GLD, seed + 5, sk=0.15, n=4, inkw=1.4, inkc="#5A3A08", hi=0.5))
    beak = L([(66, -74), (82, -72), (86, -64), (80, -60), (78, -64), (66, -64)])
    out.append(painted(D, beak, ("#FFFFFF", "#F2E2C0", "#8A7A5A"), seed + 6, sk=0.1, n=4, inkw=1.2, inkc="#3A2A10", hi=0.3))
    ex, ey = L([(60, -70)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3 * s:.1f}" fill="#FFFFFF" stroke="#2A1A08" stroke-width="1.2"/><circle cx="{ex + 0.8:.1f}" cy="{ey:.1f}" r="{1.6 * s:.1f}" fill="#1A0A04"/>')
    # a beard of small feathers under the beak, as the painters gave her
    for k in range(4):
        out.append(taper(catmull(L([(60 + k * 3, -60), (58 + k * 3, -50), (54 + k * 4, -42)]), 4), 3 * s, 1 * s, (RED[1], LAP[1])[k % 2]))
    # legs tucked, talons gold
    out.append(taper(catmull(L([(0, 14), (-10, 30), (-24, 34)]), 5), 6 * s, 3 * s, "#C8862A"))
    out.append(wing((10, -10), (34, -58), (30, -112), [-70, -84, -98, -112, -126, -140], [100, 106, 104, 98, 90, 80], 200, [RED, LAP, TUR], seed + 200, True))
    return "".join(out)


def vine_scroll(x0, y0, x1, y1, col, leaf, seed, amp=8, step=34):
    """A gold arabesque: a sinuous stem with curling tendrils and small leaves/buds, along a straight run."""
    rnd = random.Random(seed)
    L_ = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L_, (y1 - y0) / L_
    nx, ny = -uy, ux
    pts = []
    n = int(L_ / 6)
    for i in range(n + 1):
        t = i / n
        o = amp * math.sin(t * L_ / step * math.pi)
        pts.append((x0 + ux * L_ * t + nx * o, y0 + uy * L_ * t + ny * o))
    out = [pline(pts, col, 1.8, seed, 0.95, 1)]
    k = 0
    d = step / 2
    while d < L_:
        t = d / L_
        sg = 1 if k % 2 == 0 else -1
        bx, by = x0 + ux * d + nx * amp * sg, y0 + uy * d + ny * amp * sg
        sp = [(bx + (ux * math.cos(a) + nx * math.sin(a) * sg) * r, by + (uy * math.cos(a) + ny * math.sin(a) * sg) * r)
              for a, r in [(math.radians(0 + j * 50), 7 * (1 - j / 9)) for j in range(8)]]
        out.append(pline(sp, col, 1.4, seed + k, 0.9, 1))
        out.append(f'<path d="{blob(bx - nx * sg * 3, by - ny * sg * 3, 3.6, 2, k, 0.05, 8, math.degrees(math.atan2(uy, ux)) + 40 * sg)}" fill="{leaf}"/>')
        d += step
        k += 1
    return "".join(out)


@design("the-simurgh")
def the_simurgh():
    D = Doc2("my-sm")
    LAPIS_BG = "#16307A"
    out = [f'<rect width="600" height="600" fill="{LAPIS_BG}"/>']
    # the picture: a gold sky with tchi clouds, the pastel peaks of Mount Qaf, a cypress and a tree in flower
    x0, y0, x1, y1 = 54, 54, 546, 546
    cid = D.clip(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
    pic = [sky(D, [(0, "#F6DC8A"), (0.6, "#ECC062"), (1, "#E2A84A")], 3, 600, ["#FFF0B0", "#D89A3A", "#F6D27A"], 50)]
    pic.append(specks(4, (54, 54, 546, 420), ["#FFFFFF", "#B8862A"], 60, (0.8, 1.8), (0.3, 0.7)))
    pic.append(tchi_cloud([(80, 214), (130, 200), (190, 214), (240, 204)], 9, "#FFFFFF", "#2A4AA8", 3))
    pic.append(tchi_cloud([(400, 170), (450, 158), (500, 170), (530, 160)], 8, "#FFFFFF", "#2A4AA8", 4))
    pic.append(tchi_cloud([(420, 300), (470, 290), (520, 304)], 7, "#DCE6FF", "#2A4AA8", 5))
    rocks = [
        (110, 420, 70, 60, ("#F8C8C8", "#E09A9A", "#8A4A5A")), (200, 450, 60, 44, ("#D8C8F0", "#A898D0", "#4A3A7A")),
        (60, 470, 60, 54, ("#F2E0A8", "#D8B86A", "#7A5A2A")), (480, 440, 76, 58, ("#D8C8F0", "#A898D0", "#4A3A7A")),
        (390, 470, 64, 44, ("#F8C8C8", "#E09A9A", "#8A4A5A")), (540, 480, 60, 50, ("#C8E0C0", "#8AB088", "#3A5A3A")),
        (300, 490, 80, 40, ("#F2E0A8", "#D8B86A", "#7A5A2A")), (130, 510, 90, 40, ("#C8E0C0", "#8AB088", "#3A5A3A")),
        (470, 520, 90, 40, ("#F8C8C8", "#E09A9A", "#8A4A5A")),
    ]
    # a cypress and a flowering almond growing from the rocks
    pic.append(f'<path d="{blob(88, 330, 14, 62, 6, 0.05, 16)}" fill="#2A5A3A" stroke="#0E2A1A" stroke-width="1.4"/>')
    pic.append(strokes(D.nid(), blob(88, 330, 14, 62, 6, 0.05, 16), (70, 260, 110, 400), ["#4A8A5A", "#14341E"], 7, n=20, angle=-90, length=(10, 24), width=(1.5, 3)))
    pic.append(taper(catmull([(520, 400), (512, 340), (526, 300)], 6), 8, 4, "#5A3A2A"))
    for (a, l) in ((-140, 40), (-60, 44), (-100, 30)):
        pic.append(taper(catmull([(518, 340), (518 + math.cos(math.radians(a)) * l * 0.6, 340 + math.sin(math.radians(a)) * l * 0.6), (518 + math.cos(math.radians(a)) * l, 336 + math.sin(math.radians(a)) * l)], 5), 4, 1.5, "#5A3A2A"))
    rnd = random.Random(8)
    for k in range(70):
        bx, by = 518 + rnd.gauss(0, 26), 314 + rnd.gauss(0, 18)
        pic.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{rnd.uniform(1.8, 3.4):.1f}" fill="{rnd.choice(["#FFFFFF", "#FFD8E4", "#F8A8C0"])}" stroke="#C86A8A" stroke-width="0.6"/>')
    for (cx, cy, rx, ry, pal) in rocks:
        pic.append(sponge_rock(D, cx, cy, rx, ry, pal, int(cx + cy)))
    # a silver stream threading down between the rocks, tufts of flowers
    pic.append(taper(catmull([(250, 430), (280, 460), (262, 490), (300, 520), (290, 560)], 8), 4, 12, "#DCE6F2"))
    pic.append(pline(catmull([(250, 430), (280, 460), (262, 490), (300, 520), (290, 560)], 8), "#6A7A9A", 1.2, 5, 0.6, 1))
    for (fx, fy) in ((170, 400), (420, 420), (350, 452), (66, 418), (560, 432)):
        for j in range(5):
            pic.append(taper([(fx + j * 4 - 8, fy + 10), (fx + j * 5 - 10, fy - 6 - j % 2 * 4)], 2, 1, "#3A6A3A"))
            pic.append(f'<circle cx="{fx + j * 5 - 10:.1f}" cy="{fy - 8 - j % 2 * 4:.1f}" r="2.6" fill="{("#C8302A", "#FFFFFF", "#2A4AA8")[j % 3]}"/>')
    # the Simurgh herself
    pic.append(soft_glow(D, 330, 290, 170, "#FFFFFF", 0.35))
    pic.append(simurgh(D, 360, 316, 0.92, 9))
    out.append(f'<g {cid}>{"".join(pic)}</g>')
    # the illuminated border: lapis band with a gold arabesque, gold and red rules
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="#E8B84A" stroke-width="4"/>')
    out.append(f'<rect x="{x0 + 5}" y="{y0 + 5}" width="{x1 - x0 - 10}" height="{y1 - y0 - 10}" fill="none" stroke="#B8302A" stroke-width="1.6"/>')
    for (a, b, c, d_) in ((26, 27, 574, 27), (26, 573, 574, 573), (27, 26, 27, 574), (573, 26, 573, 574)):
        out.append(vine_scroll(a, b, c, d_, "#E8B84A", "#F2D27A", int(a + b), amp=7, step=30))
    for (cx, cy) in ((27, 27), (573, 27), (27, 573), (573, 573)):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#E8B84A"/><circle cx="{cx}" cy="{cy}" r="4" fill="#B8302A"/>')
    # the title cartouche and the line from Attar
    def cartouche(cx, cy, w, h, seed):
        pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 + h * 0.35, cy), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2 - h * 0.35, cy)]
        o = [f'<path d="{pd(pts)}" fill="#1A0A04" opacity="0.25" transform="translate(2 3)"/>']
        o.append(f'<path d="{pd(pts)}" fill="#FBF3DE"/>')
        o.append(f'<path d="{pd(pts)}" fill="none" stroke="#E8B84A" stroke-width="4"/>')
        inner = [(px + (cx - px) * 0.04, py + (cy - py) * 0.18) for px, py in pts]
        o.append(f'<path d="{pd(inner)}" fill="none" stroke="#2A4AA8" stroke-width="1.2"/>')
        for sg in (-1, 1):
            o.append(f'<circle cx="{cx + sg * (w / 2 + h * 0.35 + 8):.1f}" cy="{cy}" r="4" fill="#E8B84A"/>')
        return "".join(o)
    out.append(cartouche(300, 106, 330, 84, 1))
    out.append(tx(300, 114, "The Simurgh", DMS, 54, "#1E3A8A", max_w=300))
    out.append(tx(300, 138, "PERSIAN · QUEEN OF THE BIRDS", CINZEL, 17, "#9A2A22", ls=1.5, max_w=330))
    out.append(cartouche(300, 519, 360, 40, 2))
    out.append(tx(300, 526, "Thirty birds sought her, and found themselves", SERIF_IT, 21, "#1E3A8A", max_w=370))
    return fin(D, out, 43, op=0.35)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        body = fn()
        if slug in PF:
            body = painterly(body, prefix=f"mypf-{slug[:10]}-", **PF[slug])
        save(COL, slug, body)
    if not only:
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()



# =====================================================================================================================
# GALLERY EDITION (October 2026): every plate repainted to the standard of a museum-quality illustrated book of myths
# (Dore's drama, Dulac's jewelled night skies, Rackham's line, Waterhouse's mood, the craft of Egyptian tomb painting).
# Only NEW helpers live below; everything above stays as it was because other generators import from this file.
# A design registered again with @gallery(slug) replaces the earlier version of that slug, and gets the painterly
# finish (painterly.py) with its own seed and strength.
# =====================================================================================================================
from figures import tube as ftube, tube_side as ftube_side, _resample as fresample, _chain_frames as fframes
from painterly import painterly

PF = {}


def gallery(slug, **pf):
    def deco(fn):
        DESIGNS[slug] = fn
        PF[slug] = pf
        return fn
    return deco


def unit(x, y):
    d = math.hypot(x, y) or 1.0
    return x / d, y / d


def dir_grad(D, stops, L):
    """Linear gradient across an object's box from the side facing the light L (toward-light vector) to the far side."""
    lx, ly = unit(*L)
    return D.lin(stops, round(0.5 + 0.5 * lx, 3), round(0.5 + 0.5 * ly, 3), round(0.5 - 0.5 * lx, 3), round(0.5 - 0.5 * ly, 3))


def bstroke(x, y, ang, L, w, col, op, bend=0.0):
    """One tapered, slightly bent brush stroke starting at (x, y), angle in degrees."""
    a = math.radians(ang)
    dx, dy = L * math.cos(a), L * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    mx, my = x + dx / 2 + nx * bend * L, y + dy / 2 + ny * bend * L
    return (f'<path d="M {x:.1f} {y:.1f} Q {mx + nx * w:.1f} {my + ny * w:.1f} {x + dx:.1f} {y + dy:.1f} '
            f'Q {mx - nx * w:.1f} {my - ny * w:.1f} {x:.1f} {y:.1f} Z" fill="{col}" opacity="{op:.2f}"/>')


def flow_strokes(D, d, box, flow, cols, seed, n, length=(6, 16), width=(0.8, 2.2), op=(0.2, 0.55), bend=0.25, jit=10, clip=True):
    """Brush strokes whose direction follows `flow` (degrees, or a function (x, y) -> degrees), clipped to d."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(int(n)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = (flow(x, y) if callable(flow) else flow) + rnd.uniform(-jit, jit)
        L = rnd.uniform(*length)
        out.append(bstroke(x - L / 2 * math.cos(math.radians(a)), y - L / 2 * math.sin(math.radians(a)), a, L,
                           rnd.uniform(*width) / 2, rnd.choice(cols), rnd.uniform(*op), rnd.uniform(-bend, bend)))
    if not clip:
        return "".join(out)
    return f'<g {D.clip(f"<path d=\"{d}\"/>")}>{"".join(out)}</g>'


def chain_strokes(pts, ws, cols, seed, n, length=(6, 14), width=(0.8, 2.0), op=(0.2, 0.5), spread=0.85, jit=8, back=False):
    """Strokes laid along a limb / tail / serpent chain (fur, scales, folds following the form)."""
    rnd = random.Random(seed)
    P, W = fresample(pts, ws, 3.0)
    tans, norms = fframes(P)
    out = []
    for _ in range(int(n)):
        i = rnd.randrange(len(P))
        u = rnd.uniform(-spread / 2, spread / 2)
        x, y = P[i][0] + norms[i][0] * u * W[i], P[i][1] + norms[i][1] * u * W[i]
        a = math.degrees(math.atan2(tans[i][1], tans[i][0])) + (180 if back else 0) + rnd.uniform(-jit, jit)
        out.append(bstroke(x, y, a, rnd.uniform(*length), rnd.uniform(*width) / 2, rnd.choice(cols), rnd.uniform(*op), rnd.uniform(-0.2, 0.2)))
    return "".join(out)


def model(D, pts, pal, seed, L=(-0.6, -0.8), flow=None, n=None, slen=None, sw=None, sop=(0.14, 0.42), cols=None, core=1.0,
          refl=None, hi=0.3, edge=None, edge_w=1.6, rim=None, rim_w=2.2, d=None, smooth=True, grad=0.9, jit=10):
    """A form painted with a value structure: graded body colour from the light, a soft core shadow built from glazes,
    reflected light at the far edge, a lit plane, form-following strokes, and a lost-and-found edge (gone on the lit
    side, found on the shadow side) plus an optional rim light on the lit edge."""
    light, base, dark = pal
    d = d or (smooth_closed(pts) if smooth else pd(pts))
    x0, y0, x1, y1 = bbox(pts)
    W, H = max(1, x1 - x0), max(1, y1 - y0)
    lx, ly = unit(*L)
    out = [f'<path d="{d}" fill="{base}"/>']
    if grad:
        out.append(f'<path d="{d}" fill="{dir_grad(D, [(0, light, grad * 0.8), (0.42, base, 0), (0.75, dark, grad * 0.45), (1, dark, grad * 0.8)], L)}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    sm = smooth_closed if smooth else pd
    if core:
        for k, op in ((0.34, 0.16), (0.22, 0.16), (0.12, 0.14)):
            sp = shift(pts, lx * W * k, ly * H * k)
            inner.append(f'<path d="{d} {sm(sp)}" fill-rule="evenodd" fill="{dark}" opacity="{op * core:.2f}"/>')
    if refl:
        sp = shift(pts, lx * W * 0.05, ly * H * 0.05)
        inner.append(f'<path d="{d} {sm(sp)}" fill-rule="evenodd" fill="{refl}" opacity="0.32"/>')
    if hi:
        for k, op in ((0.16, 0.5), (0.08, 0.6)):
            sp = shift(pts, -lx * W * k, -ly * H * k)
            inner.append(f'<path d="{d} {sm(sp)}" fill-rule="evenodd" fill="{light}" opacity="{hi * op:.2f}"/>')
    if flow is not None:
        m = min(W, H)
        n = n if n is not None else int(max(8, min(260, W * H / 70)))
        slen = slen or (max(4, m * 0.12), max(8, m * 0.45))
        sw = sw or (max(0.7, m * 0.02), max(1.4, m * 0.05))
        inner.append(flow_strokes(D, d, (x0, y0, x1, y1), flow, cols or [light, base, dark, light], seed, n, slen, sw, sop, jit=jit, clip=False))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if edge:
        g = dir_grad(D, [(0, edge, 0), (0.45, edge, 0.15), (1, edge, 0.85)], L)
        out.append(f'<path d="{d}" fill="none" stroke="{g}" stroke-width="{edge_w}" stroke-linejoin="round"/>')
    if rim:
        g = dir_grad(D, [(0, rim, 0.95), (0.35, rim, 0.25), (0.55, rim, 0)], L)
        out.append(f'<path d="{d}" fill="none" stroke="{g}" stroke-width="{rim_w}" stroke-linejoin="round"/>')
    return "".join(out)


def rim_mask(D, ds, L, dist, col, op=0.9, src=None):
    """Rim light along the lit edge of a union of shapes: the part of the union that would leave it if pushed
    toward the light by `dist`. src=(x, y, r): the rim is strong near a light source there and fades out with
    distance (lost-and-found), instead of a uniform line."""
    lx, ly = unit(*L)
    mid = D.nid()
    sh = "".join(f'<path d="{d}"/>' for d in ds)
    D.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="700" height="700">'
                  f'<g fill="#FFFFFF">{sh}</g><g fill="#000000" transform="translate({-lx * dist:.2f} {-ly * dist:.2f})">{sh}</g></mask>')
    fill = col
    if src:
        sx, sy, sr = src
        fill = D.rad([(0, col, 1), (0.45, col, 0.6), (1, col, 0)], cx=sx, cy=sy, r=sr, units="userSpaceOnUse")
    return f'<g mask="url(#{mid})"><rect x="-50" y="-50" width="700" height="700" fill="{fill}" opacity="{op}"/></g>'


def edge_mask(D, ds, L, dist, col, op=0.5):
    """Dark accent along the shadow-side edge of a union of shapes (the 'found' edge)."""
    return rim_mask(D, ds, (-L[0], -L[1]), dist, col, op)


class Beast:
    """A body (animal, figure, drapery) painted as ONE modelled mass built from overlapping parts: limbs are tapered
    tubes, masses are closed outlines. All parts share a colour so the silhouette reads as one; each part then gets
    its own form shading and strokes that follow it (fur along the limb, hair over the barrel), a rim light runs along
    the lit edge of the whole union and an occlusion edge along the shadow side."""

    def __init__(self, D, pal, seed, L=(-0.6, -0.8), fur=None, rim=None, rim_d=2.2, rim_op=0.85, edge="#000000", edge_d=1.6,
                 edge_op=0.45, fur_n=1.0, fur_len=(4, 11), fur_w=(0.8, 1.8), fur_op=(0.18, 0.5), shade=0.42, lit=0.28, glob=0.75):
        self.D, self.pal, self.seed, self.L = D, pal, seed, unit(*L)
        self.fur = fur or [pal[0], pal[1], pal[2], mix(pal[1], pal[0], 0.5)]
        self.rim, self.rim_d, self.rim_op = rim, rim_d, rim_op
        self.edge, self.edge_d, self.edge_op = edge, edge_d, edge_op
        self.fur_n, self.fur_len, self.fur_w, self.fur_op = fur_n, fur_len, fur_w, fur_op
        self.shade, self.lit, self.glob = shade, lit, glob
        self.parts = []
        self.after = []

    def limb(self, pts, ws, cap0=True, cap1=True, fur=1.0, pal=None, shade=None, flen=None, back=False):
        P = [tuple(p) for p in pts]
        o = ftube(P, list(ws), cap0, cap1)
        self.parts.append(dict(kind="tube", pts=o, axis=P, ws=list(ws), fur=fur, pal=pal, shade=shade, flen=flen, back=back, cap1=cap1))
        return o

    def mass(self, pts, flow=-90, fur=1.0, pal=None, shade=None, flen=None, smooth=True, core=None):
        self.parts.append(dict(kind="mass", pts=list(pts), flow=flow, fur=fur, pal=pal, shade=shade, flen=flen, smooth=smooth, core=core))
        return pts

    def overlay(self, s):
        """Extra painting (markings, eyes, folds) drawn inside the union, above the shading, below the rim."""
        self.after.append(s)

    def ds(self):
        return [smooth_closed(p["pts"]) if p.get("smooth", True) else pd(p["pts"]) for p in self.parts]

    def render(self):
        D, L = self.D, self.L
        rnd = random.Random(self.seed)
        ds = self.ds()
        allp = [q for p in self.parts for q in p["pts"]]
        x0, y0, x1, y1 = bbox(allp)
        out = []
        cid = D.clip("".join(f'<path d="{d}"/>' for d in ds))
        inner = out
        for k, (p, d) in enumerate(zip(self.parts, ds)):
            out.append(f'<path d="{d}" fill="{(p["pal"] or self.pal)[1]}"/>')
            pal = p["pal"] or self.pal
            sh = self.shade if p["shade"] is None else p["shade"]
            flen = p["flen"] or self.fur_len
            if p["kind"] == "tube":
                if sh:
                    inner.append(f'<path d="{smooth_closed(ftube_side(p["axis"], p["ws"], L, 0.5, cap1=p["cap1"]))}" fill="{pal[2]}" opacity="{sh * 0.6:.2f}"/>')
                    inner.append(f'<path d="{smooth_closed(ftube_side(p["axis"], p["ws"], L, 0.22, cap1=p["cap1"]))}" fill="{pal[2]}" opacity="{sh * 0.5:.2f}"/>')
                if self.lit:
                    inner.append(f'<path d="{smooth_closed(ftube_side(p["axis"], p["ws"], L, 0.2, lit=True, cap1=p["cap1"]))}" fill="{pal[0]}" opacity="{self.lit:.2f}"/>')
                if p["fur"]:
                    Ls = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p["axis"], p["axis"][1:]))
                    n = Ls * (sum(p["ws"]) / len(p["ws"])) / 14 * self.fur_n * p["fur"]
                    cols = [pal[0], pal[1], pal[2], mix(pal[1], pal[0], 0.5)] if p["pal"] else self.fur
                    inner.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>' + chain_strokes(p["axis"], p["ws"], cols, self.seed + k, n, flen, self.fur_w,
                                                                                    self.fur_op, 0.95, back=p["back"]) + "</g>")
            else:
                pts = p["pts"]
                bx0, by0, bx1, by1 = bbox(pts)
                W, H = bx1 - bx0, by1 - by0
                sm = smooth_closed if p["smooth"] else pd
                if sh:
                    for kk, op in ((0.3, 0.45), (0.18, 0.35), (0.09, 0.3)):
                        sp = shift(pts, L[0] * W * kk, L[1] * H * kk)
                        inner.append(f'<path d="{d} {sm(sp)}" fill-rule="evenodd" fill="{pal[2]}" opacity="{sh * op:.2f}" {D.clip(f"<path d=\"{d}\"/>")}/>')
                if self.lit:
                    sp = shift(pts, -L[0] * W * 0.12, -L[1] * H * 0.12)
                    inner.append(f'<path d="{d} {sm(sp)}" fill-rule="evenodd" fill="{pal[0]}" opacity="{self.lit:.2f}" {D.clip(f"<path d=\"{d}\"/>")}/>')
                if p["fur"]:
                    n = W * H / 60 * self.fur_n * p["fur"]
                    cols = [pal[0], pal[1], pal[2], mix(pal[1], pal[0], 0.5)] if p["pal"] else self.fur
                    inner.append(flow_strokes(D, d, (bx0, by0, bx1, by1), p["flow"], cols, self.seed + k, n, flen, self.fur_w, self.fur_op))
        top = []
        if self.glob:
            g = dir_grad(D, [(0, self.pal[0], 0.55 * self.glob), (0.45, self.pal[1], 0), (1, self.pal[2], 0.7 * self.glob)], L)
            top.append(f'<rect x="{x0 - 2:.1f}" y="{y0 - 2:.1f}" width="{x1 - x0 + 4:.1f}" height="{y1 - y0 + 4:.1f}" fill="{g}"/>')
        top.extend(self.after)
        out.append(f'<g {cid}>{"".join(top)}</g>')
        if self.edge and self.edge_d:
            out.append(edge_mask(D, ds, L, self.edge_d, self.edge, self.edge_op))
        if self.rim:
            out.append(rim_mask(D, ds, L, self.rim_d, self.rim, self.rim_op))
        return "".join(out)


def leg_chain(root, angs, lens):
    """Joint positions of a limb hanging from root; angles in degrees from straight down, positive = toward +x."""
    pts = [root]
    x, y = root
    for a, l in zip(angs, lens):
        x, y = x + math.sin(math.radians(a)) * l, y + math.cos(math.radians(a)) * l
        pts.append((x, y))
    return pts



# ---------------------------------------------------------------- a horse with real anatomy
STAND = dict(fn=(4, 1, 24), ff=(-4, 0, 22), hn=(-24, 4, 24), hf=(-16, 2, 22), neck=0, head=56, tail=(-150, 0.5))
GALLOP = dict(fn=(48, 62, 76), ff=(22, -62, -40), hn=(-46, -62, -72), hf=(14, -18, 18), neck=10, head=40, tail=(-170, 0.9))


def horse_hoof(D, p, ang, w, col="#1E1612"):
    """Hoof at the end of a pastern: a short wedge, flat sole."""
    a = math.radians(ang)
    dx, dy = math.sin(a), math.cos(a)
    nx, ny = -dy, dx
    h = w * 1.0
    p0 = (p[0] - nx * w * 0.5, p[1] - ny * w * 0.5)
    p1 = (p[0] + nx * w * 0.55, p[1] + ny * w * 0.55)
    p2 = (p1[0] + dx * h + nx * w * 0.2, p1[1] + dy * h + ny * w * 0.2)
    p3 = (p0[0] + dx * h * 1.05 - nx * w * 0.1, p0[1] + dy * h * 1.05 - ny * w * 0.1)
    return [p0, p1, p2, p3]


def steed(D, x, y, s, seed, pal=("#F4F2EE", "#C8C6C4", "#5A5A62"), pose=None, flip=False, L=(-0.5, -0.85), rim=None,
          mane=("#FFFFFF", "#D8D8E0", "#7A7A88"), far=None, dapple=True, legs8=False, wind=0.0, socks=None, hoof="#2A221E",
          edge="#0A0A10", eye_col="#0A0808"):
    """A horse in profile with true anatomy: deep chest, arched neck, wedge head with a round jaw, a powerful
    hindquarter, legs with forearm, knee, cannon, fetlock, pastern and hoof, hocks angled back, a flowing mane
    and tail. Local units: withers height = 100, ground at 0, facing +x (flip to face left). Returns svg."""
    P = dict(STAND)
    P.update(pose or {})
    Lw = (-L[0], L[1]) if flip else L

    def M(pts):
        return T(pts, x, y, s, flip)
    rnd = random.Random(seed)
    farpal = far or (mix(pal[0], pal[2], 0.45), mix(pal[1], pal[2], 0.45), mix(pal[2], "#000000", 0.35))
    out = []

    def leg_parts(B, kind, angs, dx=0.0, dang=0.0):
        a = [v + dang for v in angs]
        if kind == "f":
            root = (81 + dx, -62)
            j = leg_chain(root, a, (34, 20, 8))
            mid = ((j[0][0] + j[1][0]) / 2, (j[0][1] + j[1][1]) / 2)
            pts = [root, mid, j[1], ((j[1][0] + j[2][0]) / 2, (j[1][1] + j[2][1]) / 2), j[2], j[3]]
            ws5 = (21, 13, 9.6, 6.8, 8.6, 6.4)
        else:
            root = (16 + dx, -58)
            j = leg_chain(root, a, (28, 24, 8))
            mid = ((j[0][0] + j[1][0]) / 2, (j[0][1] + j[1][1]) / 2)
            pts = [root, mid, j[1], ((j[1][0] + j[2][0]) / 2, (j[1][1] + j[2][1]) / 2), j[2], j[3]]
            ws5 = (24, 14, 10.5, 6.8, 8.6, 6.4)
        B.limb(M(pts), [w * s for w in ws5], fur=0.7)
        if kind == "h":
            # point of hock
            hx, hy = j[1]
            ang = math.radians(a[0])
            B.mass(M([(hx - 2, hy - 5), (hx - 6 * math.cos(ang) - 3, hy + 1), (hx - 1, hy + 6), (hx + 3, hy)]), flow=90, fur=0.3)
        hp = horse_hoof(D, None or j[3], a[2] * (-1 if flip else 1) * 0 + a[2], 7.4)
        return j, hp

    def hoof_draw(hp, col):
        return f'<path d="{pd(M(hp))}" fill="{col}"/>'

    # ---- far legs (behind the body), darker
    Bf = Beast(D, farpal, seed + 1, Lw, rim=None, edge=edge, edge_d=1.2, edge_op=0.4, fur_n=0.6, shade=0.35, lit=0.12, glob=0.5)
    hoofs_far = []
    for kind, key in (("f", "ff"), ("h", "hf")):
        reps = ((0, 0), (5, 14)) if legs8 else ((0, 0),)
        for dx, dang in reps:
            j, hp = leg_parts(Bf, kind, P[key], dx - 3, dang)
            hoofs_far.append(hp)
    out.append(Bf.render())
    out.extend(hoof_draw(h, mix(hoof, "#000000", 0.3)) for h in hoofs_far)

    # ---- body
    B = Beast(D, pal, seed, Lw, rim=rim, rim_d=2.4 * s / 1.3, edge=edge, edge_d=1.8, edge_op=0.55, fur_n=0.9, fur_len=(4 * s, 10 * s),
              fur_w=(0.7, 1.6), shade=0.45, lit=0.3, glob=0.8)
    # barrel with a deep chest, slight tuck up at the flank
    barrel = [(70, -102), (50, -95), (32, -96), (16, -99), (4, -92), (4, -74), (14, -60), (30, -54), (50, -51), (66, -49), (80, -52),
              (94, -60), (102, -72), (102, -84), (90, -98)]
    B.mass(M(barrel), flow=180 if not flip else 0, fur=1.0)
    # hindquarter: round croup, hamstring down the back of the thigh into the gaskin
    hq = [(24, -101), (10, -101), (-1, -95), (-7, -84), (-6, -70), (-2, -58), (4, -48), (10, -42), (20, -44), (28, -54), (32, -70), (32, -90)]
    B.mass(M(hq), flow=lambda X, Y: 100 if not flip else 80, fur=0.9, shade=0.22)
    # shoulder and the forearm's top
    sh = [(70, -100), (84, -94), (100, -84), (104, -72), (99, -60), (89, -53), (78, -55), (72, -70), (68, -88)]
    B.mass(M(sh), flow=60 if not flip else 120, fur=0.8, shade=0.18)
    near_hoofs = []
    for kind, key in (("f", "fn"), ("h", "hn")):
        reps = ((0, 0), (6, -12)) if legs8 else ((0, 0),)
        for dx, dang in reps[::-1]:
            j, hp = leg_parts(B, kind, P[key], dx, dang)
            near_hoofs.append(hp)
    # neck: arched crest from the withers to the poll, throat underneath
    na = math.radians(P["neck"])
    piv = (84, -86)

    def rn(pts):
        c, s_ = math.cos(-na), math.sin(-na)
        return [(piv[0] + (px - piv[0]) * c - (py - piv[1]) * s_, piv[1] + (px - piv[0]) * s_ + (py - piv[1]) * c) for px, py in pts]
    poll = rn([(113, -141)])[0]
    ha = math.radians(P["head"] - P["neck"])

    def hd(pts):
        c, s_ = math.cos(ha), math.sin(ha)
        return [(poll[0] + px * c - py * s_, poll[1] + px * s_ + py * c) for px, py in pts]
    crest = rn([(64, -101), (78, -114), (92, -128), (104, -138), (110, -142)])
    throat = hd([(1, 10)]) + rn([(110, -114), (106, -98), (104, -84), (100, -74)])
    neck = [(60, -96)] + crest + hd([(-1, -6), (-2, 2)]) + throat + [(88, -78), (74, -80)]
    B.mass(M(neck), flow=lambda X, Y: (-60 if not flip else -120), fur=0.9)
    head = hd([(-3, -5), (5, -8), (14, -8.6), (24, -7.2), (33, -6.0), (39.5, -4.6), (43, -1.6), (43.6, 2.0), (42, 4.6), (38.5, 6.0), (34.5, 5.6),
               (29, 6.6), (22, 9.4), (15, 12.8), (8, 14.0), (2.5, 11.6), (-1.5, 6.5)])
    B.mass(M(head), flow=lambda X, Y: math.degrees(ha) * (1 if not flip else -1) + (0 if not flip else 180), fur=0.5, shade=0.35)
    # ears
    for e, dxe in ((0, 0), (1, 3.5)):
        ear = hd([(-1 + dxe, -6), (-8 + dxe, -15), (-10.5 + dxe, -19.5), (-6 + dxe, -16), (3 + dxe, -7.5)])
        B.mass(M(ear), flow=-90, fur=0.2, pal=pal if e else farpal)
    # anatomy overlays: shoulder blade, elbow crease, the flank fold, the jaw, hip point
    def ov(pts, col, w, op):
        return ink(smooth_open(M(pts)), col, w * s, seed + len(B.after), 1, op)
    dk_ = mix(pal[2], "#000000", 0.2)
    B.overlay(ov([(70, -98), (80, -84), (92, -70), (99, -63)], dk_, 2.6, 0.32))
    B.overlay(ov([(76, -60), (78, -66), (84, -70)], dk_, 2.2, 0.35))
    B.overlay(ov([(30, -96), (32, -80), (28, -62), (20, -54)], dk_, 3.2, 0.25))
    B.overlay(ov([(12, -96), (10, -82)], pal[0], 3.0, 0.3))
    B.overlay(ov(hd([(3, 11), (10, 6), (16, 0), (20, 4), (24, 8)]), dk_, 1.8, 0.4))
    B.overlay(ov(hd([(17, -4), (26, -3.5), (35, -2.5)]), pal[0], 2.4, 0.35))
    if dapple:
        dd = []
        for _ in range(46):
            cx_, cy_ = rnd.uniform(4, 96), rnd.uniform(-98, -62)
            if cx_ > 70 and cy_ > -70:
                continue
            r = rnd.uniform(2.0, 4.0)
            (px, py), = M([(cx_, cy_)])
            dd.append(f'<path d="{blob(px, py, r * s, r * s * 0.85, rnd.randint(0, 999), 0.2, 9)}" fill="{pal[0]}" opacity="{rnd.uniform(0.18, 0.4):.2f}"/>')
        dd.insert(0, f'<path d="{smooth_closed(M([(10, -94), (40, -92), (64, -90), (66, -66), (40, -60), (12, -66)]))}" fill="{dk_}" opacity="0.16"/>')
        B.overlay("".join(dd))
    if socks:
        for kind in ("fn", "hn"):
            pass
    body = B.render()
    out.append(body)
    out.extend(hoof_draw(h, hoof) for h in near_hoofs)
    # eye, nostril, mouth
    (ex, ey), = M(hd([(12.5, -3)]))
    out.append(f'<path d="{blob(ex, ey, 2.6 * s, 1.8 * s, seed + 3, 0.05, 10, math.degrees(ha))}" fill="{eye_col}"/>')
    out.append(f'<circle cx="{ex - 0.6 * s:.1f}" cy="{ey - 0.6 * s:.1f}" r="{0.7 * s:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(ink(smooth_open(M(hd([(9.5, -5.4), (12.5, -6.2), (15.5, -5)]))), dk_, 1.0 * s, seed, 1, 0.5))
    out.append(ink(smooth_open(M(hd([(37.5, -2.6), (39.5, -1.0), (40.5, 1.2)]))), mix(pal[2], "#000000", 0.4), 1.6 * s, seed, 1, 0.8))
    out.append(ink(smooth_open(M(hd([(35.5, 4.4), (39, 3.6), (42.5, 3.4)]))), mix(pal[2], "#000000", 0.4), 1.0 * s, seed, 1, 0.6))
    # mane: locks falling from the crest, blown back by the wind
    mn = []
    cpts = catmull(rn([(66, -102), (78, -115), (92, -129), (104, -139), (111, -143)]), 6)
    for k in range(int(70 * max(0.6, s))):
        t = rnd.random()
        bx_, by_ = cpts[int(t * (len(cpts) - 1))]
        L_ = rnd.uniform(10, 26) * (1 - 0.5 * t)
        a = 150 + wind * 30 + rnd.uniform(-20, 20) - P["neck"] * 0.6
        ex_, ey_ = bx_ + math.cos(math.radians(a)) * L_ * -1, by_ + math.sin(math.radians(a)) * L_ * -1
        ex_, ey_ = bx_ - L_ * (0.9 + wind * 0.3), by_ + L_ * (0.5 - wind * 0.45)
        mid = ((bx_ + ex_) / 2 + rnd.uniform(-3, 3), (by_ + ey_) / 2 + rnd.uniform(-2, 4))
        mn.append(taper(M([(bx_, by_), mid, (ex_, ey_)]), rnd.uniform(2.5, 4.5) * s, 0.4, rnd.choice(mane), rnd.uniform(0.5, 0.95)))
    # forelock
    for k in range(10):
        b = hd([(rnd.uniform(-2, 3), rnd.uniform(-7, -4))])[0]
        e = hd([(rnd.uniform(6, 12), rnd.uniform(-10, -3))])[0]
        mn.append(taper(M([b, ((b[0] + e[0]) / 2, (b[1] + e[1]) / 2 - 2), e]), 2.6 * s, 0.4, rnd.choice(mane), 0.85))
    out.append("".join(mn))
    # tail: from the dock, a long bundle of hair
    ta, lift = P["tail"]
    tr = (2, -96)
    tl = []
    for k in range(int(60 * max(0.6, s))):
        L_ = rnd.uniform(40, 70)
        a = math.radians(ta + rnd.uniform(-14, 14))
        mid = (tr[0] + math.cos(a) * L_ * 0.35, tr[1] + math.sin(a) * L_ * 0.35 - lift * 6 + 10)
        end = (tr[0] + math.cos(a) * L_, tr[1] + math.sin(a) * L_ + (1 - lift) * L_ * 0.8 + rnd.uniform(-6, 6))
        tl.append(taper(M([(tr[0] + rnd.uniform(-2, 2), tr[1] + rnd.uniform(-2, 3)), mid, end]), rnd.uniform(3, 6) * s, 0.4, rnd.choice(mane), rnd.uniform(0.45, 0.9)))
    out.insert(0 if not legs8 else 0, "")
    out.append("".join(tl))
    return "".join(out)



# ---------------------------------------------------------------- human figures with real proportion (8 heads tall)
def pose(view="back", **kw):
    """Joint positions in head units (1 = head height, feet at y = 0, crown at y = -8). view 'back' (seen from behind,
    x = viewer's right) or 'side' (profile facing +x). Override any joint by keyword (tuples)."""
    if view == "back":
        J = dict(head=(0, -7.45), neck=(0, -6.75), sR=(0.88, -6.2), sL=(-0.88, -6.2), eR=(1.18, -4.95), eL=(-1.18, -4.95),
                 wR=(1.22, -3.7), wL=(-1.22, -3.7), hR=(0.52, -4.0), hL=(-0.52, -4.0), kR=(0.48, -2.1), kL=(-0.48, -2.1),
                 aR=(0.42, -0.28), aL=(-0.42, -0.28), tR=(0.48, 0), tL=(-0.48, 0), waist=-4.75, tilt=0.0)
    else:
        J = dict(head=(0.12, -7.45), neck=(0.0, -6.75), sR=(0.0, -6.3), sL=(-0.05, -6.3), eR=(0.1, -4.9), eL=(-0.12, -4.9),
                 wR=(0.25, -3.65), wL=(-0.2, -3.65), hR=(0.0, -4.0), hL=(-0.04, -4.0), kR=(0.12, -2.1), kL=(-0.1, -2.1),
                 aR=(0.0, -0.3), aL=(-0.08, -0.3), tR=(0.75, 0), tL=(0.68, 0), waist=-4.75, tilt=10.0)
    J.update(kw)
    J["view"] = view
    return J


def human(D, x, base, h, J, pal, seed, L=(-0.6, -0.8), rim=None, flip=False, rim_d=1.8, form="m", fur_n=0.5, edge="#000000",
          shade=0.42, lit=0.25, hands=True, head=True, legs=True, arms=("L", "R"), fur_len=None):
    """Return (Beast, M) for a human body posed by J, with anatomical contours: a torso drawn along the curve of the
    spine (chest, shoulder blades, the lumbar hollow, buttock), arms with deltoid, biceps and forearm bellies, legs
    with the long thigh taper, a calf bulge set behind the shin, real hands and feet. Callers add drapery to the same
    Beast before B.render(). M maps head units to pixels."""
    k = h / 8.0

    def M(pts):
        return T(pts, x, base, k, flip)
    Lw = (-L[0], L[1]) if flip else L
    B = Beast(D, pal, seed, Lw, rim=rim, rim_d=rim_d, edge=edge, edge_d=max(0.8, k * 0.04), edge_op=0.5, fur_n=fur_n,
              fur_len=fur_len or (k * 0.25, k * 0.7), fur_w=(0.6, max(1.0, k * 0.05)), fur_op=(0.12, 0.35), shade=shade, lit=lit, glob=0.7)
    v = J["view"]
    fem = form == "f"
    sw = 0.86 if fem else 1.0
    nb = J["neck"]
    hR, hL = J["hR"], J["hL"]
    hy = (hR[1] + hL[1]) / 2
    hx = (hR[0] + hL[0]) / 2
    sy = (J["sR"][1] + J["sL"][1]) / 2
    wy = J["waist"]
    back_dir = -1.0 if v == "side" else 0.0      # side view faces +x, the back of the leg is toward -x

    def leg(side):
        hp, kn, an, to = J["h" + side], J["k" + side], J["a" + side], J["t" + side]
        th = [hp, _lerp(hp, kn, 0.3), _lerp(hp, kn, 0.7), kn]
        B.limb(M(th), [k * w * (1.0 if not fem else 1.02) for w in (0.98, 0.88, 0.66, 0.46)], cap0=True)
        u, n, d = _frame(kn, an)
        off = 0.07 * back_dir * (1 if n[0] < 0 else -1)
        c1 = (_lerp(kn, an, 0.28)[0] + n[0] * off, _lerp(kn, an, 0.28)[1] + n[1] * off)
        B.limb(M([kn, c1, _lerp(kn, an, 0.62), an]), [k * w for w in (0.44, 0.54, 0.36, 0.22)])
        if v == "side":
            B.mass(M(foot_pts(an, to)), flow=0, fur=0.2, shade=0.3)
        else:
            B.limb(M([an, to]), [k * 0.26, k * 0.2], fur=0.2)
    if legs:
        for side in ("L", "R"):
            leg(side)
    # torso
    if v == "back":
        def side_pts(sg):
            s_ = J["sR"] if sg > 0 else J["sL"]
            hp = J["hR"] if sg > 0 else J["hL"]
            return [(nb[0] + sg * 0.3, nb[1] + 0.1), (nb[0] + (s_[0] - nb[0]) * 0.6, s_[1] - 0.04), (s_[0] + sg * 0.16 * sw, s_[1] + 0.22),
                    (s_[0] + sg * 0.14 * sw, s_[1] + 0.6), (s_[0] * 0.9 * sw, s_[1] + 1.1), (sg * (0.7 if not fem else 0.56) + hx * 0.4, wy),
                    (hp[0] + sg * (0.3 if not fem else 0.46), hy + 0.05), (hp[0] + sg * 0.3, hy + 0.55), (hx + sg * 0.12, hy + 0.85)]
        tor = side_pts(1) + side_pts(-1)[::-1]
        B.mass(M(tor), flow=-90, fur=0.5)
        B.overlay(ink(smooth_open(M([(nb[0], nb[1] + 0.3), ((nb[0] + hx) / 2, (sy + wy) / 2), (hx, hy)])), pal[2], k * 0.07, seed, 1, 0.35))
        for sg in (-1, 1):
            B.overlay(ink(smooth_open(M([(sg * 0.25, sy + 0.25), (sg * 0.62, sy + 0.55), (sg * 0.45, sy + 1.25)])), pal[2], k * 0.06, seed + sg, 1, 0.3))
    else:
        # profile torso drawn in a frame that follows the spine from the pelvis to the base of the neck
        P0 = (hx, hy)
        u, n, d = _frame(P0, nb)          # u points up the spine; n is the forward normal when facing +x
        if n[0] < 0:
            n = (-n[0], -n[1])
        sc = d / 2.75

        def S(px, py):                       # px forward, py along the spine (0 pelvis .. -2.75 neck)
            return (P0[0] + n[0] * px + u[0] * (-py) * sc, P0[1] + n[1] * px + u[1] * (-py) * sc)
        chest = 0.64 if not fem else 0.66
        prof = [(-0.26, -2.8), (-0.5, -2.5), (-0.6, -2.0), (-0.52, -1.4), (-0.4, -0.85), (-0.48, -0.3), (-0.6, 0.15), (-0.44, 0.58),
                (0.12, 0.52), (0.36, 0.1), (0.46, -0.35), (0.44, -0.82), (0.52, -1.3), (chest - 0.06, -1.68), (chest, -1.98), (0.46, -2.44), (0.24, -2.8)]
        B.mass(M([S(a, b) for a, b in prof]), flow=-90, fur=0.5)
        B.overlay(ink(smooth_open(M([S(0.46, -2.0), S(0.36, -1.66), S(0.1, -1.62)])), pal[2], k * 0.05, seed, 1, 0.35))
        B.overlay(ink(smooth_open(M([S(-0.36, -2.3), S(-0.2, -1.9), S(-0.3, -1.55)])), pal[2], k * 0.045, seed + 1, 1, 0.3))
    # neck and head
    if head:
        hc = J["head"]
        B.limb(M([(nb[0] - (0.06 if v == "side" else 0), nb[1] + 0.25), _lerp(nb, hc, 0.62)]), [k * 0.66, k * 0.5], fur=0.2)
        ang = J.get("head_tilt", 0)
        if v == "back":
            hp_ = blob_pts(hc[0], hc[1] - 0.02, 0.38, 0.52, seed + 5, 0.02, 18, ang)
        else:
            hp_ = [(hc[0] + px, hc[1] + py) for px, py in ((-0.42, -0.06), (-0.34, -0.4), (-0.05, -0.56), (0.25, -0.46), (0.38, -0.22),
                                                            (0.4, -0.08), (0.5, 0.1), (0.42, 0.16), (0.44, 0.26), (0.38, 0.38), (0.3, 0.5), (0.1, 0.5),
                                                            (-0.08, 0.36), (-0.3, 0.28))]
            hp_ = [(hc[0] + (px - hc[0]) * math.cos(math.radians(ang)) - (py - hc[1]) * math.sin(math.radians(ang)),
                    hc[1] + (px - hc[0]) * math.sin(math.radians(ang)) + (py - hc[1]) * math.cos(math.radians(ang))) for px, py in hp_]
        B.mass(M(hp_), flow=-90, fur=0.2, shade=0.35)
    # arms: deltoid and biceps on the upper arm, the forearm's muscle belly near the elbow, a real hand
    for side in arms:
        s_, e_, w_ = J["s" + side], J["e" + side], J["w" + side]
        ua = [s_, _lerp(s_, e_, 0.25), _lerp(s_, e_, 0.55), _lerp(s_, e_, 0.8), e_]
        B.limb(M(ua), [k * w * (1 if not fem else 0.8) for w in (0.7, 0.6, 0.5, 0.42, 0.34)])
        B.mass(M(blob_pts(s_[0], s_[1] + 0.15, 0.34 * (1 if not fem else 0.8), 0.42, seed + 9, 0.04, 14)), flow=-90, fur=0.3, shade=0.3)
        B.limb(M([e_, _lerp(e_, w_, 0.25), _lerp(e_, w_, 0.62), w_]), [k * w * (1 if not fem else 0.85) for w in (0.36, 0.42, 0.32, 0.23)])
        if hands:
            dx, dy = w_[0] - e_[0], w_[1] - e_[1]
            d_ = math.hypot(dx, dy) or 1
            hand_end = J.get("hand" + side, (w_[0] + dx / d_ * 0.7, w_[1] + dy / d_ * 0.7))
            B.mass(M(hand_pts(w_, hand_end, side=1 if side == "R" else -1)), flow=math.degrees(math.atan2(dy, dx)), fur=0.1, shade=0.3)
    return B, M


def drape(B, M, pts, flow=-90, pal=None, fur=0.6, shade=0.5):
    """Cloth on a figure (cloak, chiton, himation): a mass with folds painted along `flow`."""
    B.mass(M(pts), flow=flow, fur=fur, pal=pal, shade=shade)


def folds(D, M, lines, col, w, seed, op=0.4):
    """Fold lines (in head units) drawn as tapered brush marks."""
    return "".join(taper(M(l), w, w * 0.2, col, op) for l in lines)



# ---------------------------------------------------------------- scene painting helpers
def cloud_mass(D, pts, pal, seed, L=(-0.5, -0.8), n=40, puff=(18, 40), lit_edge=None, op=1.0):
    """A heavy cloud bank: many overlapping soft puffs inside an outline, lit side lighter, underside dark,
    with brushy strokes and a lit rim where the light catches it."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = bbox(pts)
    d = smooth_closed(pts)
    lx, ly = unit(*L)
    out = [f'<g opacity="{op}">', f'<path d="{d}" fill="{pal[1]}" opacity="0.92"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{d}" fill="{dir_grad(D, [(0, pal[0], 0.7), (0.5, pal[1], 0), (1, pal[2], 0.85)], L)}"/>']
    for i in range(n):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(*puff)
        t = ((cx - (x0 + x1) / 2) * lx / max(1, (x1 - x0) / 2) + (cy - (y0 + y1) / 2) * ly / max(1, (y1 - y0) / 2))
        col = pal[0] if t > 0.25 else (pal[2] if t < -0.3 else pal[1])
        pp = blob(cx, cy, r, r * 0.8, rnd.randint(0, 9999), 0.12, 14)
        inner.append(f'<path d="{pp}" fill="{col}" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>')
        # the lit top of each puff
        inner.append(f'<path d="{blob(cx + lx * r * 0.3, cy + ly * r * 0.3, r * 0.7, r * 0.5, rnd.randint(0, 9999), 0.15, 12)}" fill="{pal[0]}" opacity="{rnd.uniform(0.1, 0.3):.2f}"/>')
    inner.append(flow_strokes(D, d, (x0, y0, x1, y1), -8, [pal[0], pal[1], pal[2]], seed + 5, (x1 - x0) * (y1 - y0) / 300, (20, 60), (3, 9), (0.08, 0.22), clip=False))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if lit_edge:
        out.append(rim_mask(D, [d], L, 3, lit_edge, 0.7))
    out.append("</g>")
    return "".join(out)


def fire(D, x, y, h, seed, lean=0.0, pal=("#FFFBE0", "#FFD25A", "#FF8A1E", "#C8380E"), glow=True, n=9, w=0.42):
    """A living flame: a white-hot core low down, licking S-curved tongues (soft halo + body for each), hottest
    colours inside, deep red at the tips, sparks rising and a big warm glow."""
    rnd = random.Random(seed)
    out = []
    if glow:
        out.append(soft_glow(D, x, y - h * 0.45, h * 3.2, "#FF9A3A", 0.42))
        out.append(soft_glow(D, x, y - h * 0.4, h * 1.4, "#FFD27A", 0.6))
    core = D.rad([(0, pal[0], 1), (0.45, pal[1], 0.85), (1, pal[2], 0)])
    out.append(f'<ellipse cx="{x + lean * h * 0.2:.1f}" cy="{y - h * 0.3:.1f}" rx="{h * w * 0.9:.1f}" ry="{h * 0.5:.1f}" fill="{core}"/>')
    for layer, (col, sc, op) in enumerate(((pal[3], 1.0, 0.55), (pal[2], 0.88, 0.7), (pal[1], 0.7, 0.85), (pal[0], 0.46, 0.95))):
        k = n if layer < 2 else max(3, n // 2 + 1)
        for i in range(k):
            off = (i / max(1, k - 1) - 0.5) * 2 * h * w * sc * 0.55 + rnd.uniform(-2, 2)
            hh = h * sc * rnd.uniform(0.6, 1.08) * (1 - abs(off) / (h * w * 1.4))
            bx = x + off
            curl = rnd.uniform(-0.22, 0.22) + lean
            wig = rnd.uniform(0.08, 0.16) * rnd.choice((-1, 1))
            pts = [(bx, y), (bx + (curl * 0.3 + wig) * hh, y - hh * 0.3), (bx + (curl * 0.6 - wig) * hh, y - hh * 0.6),
                   (bx + (curl * 0.9 + wig * 0.6) * hh, y - hh * 0.84), (bx + (curl * 1.1) * hh + rnd.uniform(-2, 2), y - hh)]
            c = catmull(pts, 5)
            bw = h * w * sc * rnd.uniform(0.32, 0.55)
            out.append(taper(c, bw * 1.7, 1.0, col, op * 0.3))
            out.append(taper(c, bw, 0.5, col, op))
    for i in range(16):
        sx = x + rnd.uniform(-h * 0.5, h * 0.5) + lean * h
        sy = y - h * rnd.uniform(0.9, 2.3)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rnd.uniform(0.8, 2.0):.1f}" fill="{rnd.choice(pal[:3])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    return "".join(out)


def crag(D, pts, pal, seed, L=(-0.5, -0.8), lit=None, facets=14, cracks=8, edge="#000000", op_lit=0.6):
    """A rock mass painted in planes: graded body, angular lit facets, dark cracks, rough strokes, lit top edge."""
    rnd = random.Random(seed)
    out = [model(D, pts, pal, seed, L, flow=lambda X, Y: rnd.uniform(-100, -60), sop=(0.1, 0.32), core=0.8, hi=0.25, edge=edge, edge_w=2)]
    x0, y0, x1, y1 = bbox(pts)
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for i in range(facets):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        w, h = rnd.uniform(14, 50), rnd.uniform(10, 34)
        a = rnd.uniform(-30, 30)
        poly_ = [(cx, cy), (cx + w * 0.6, cy - h * 0.4), (cx + w, cy + h * 0.1), (cx + w * 0.4, cy + h * 0.5)]
        poly_ = _rot(poly_, cx, cy, a)
        inner.append(f'<path d="{pd(poly_)}" fill="{rnd.choice([pal[0], pal[2]])}" opacity="{rnd.uniform(0.08, 0.22):.2f}"/>')
    for i in range(cracks):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        c = [(cx, cy)]
        for j in range(4):
            cx += rnd.uniform(-10, 10)
            cy += rnd.uniform(6, 16)
            c.append((cx, cy))
        inner.append(taper(c, 2.4, 0.4, mix(pal[2], "#000000", 0.4), 0.55))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if lit:
        out.append(rim_mask(D, [d], L, 3.2, lit, op_lit))
    return "".join(out)


def _rot(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (px - cx) * c - (py - cy) * s, cy + (px - cx) * s + (py - cy) * c) for px, py in pts]


def bolt(x0, y0, x1, y1, seed, col="#F2F0FF", w=3.0, glow="#B8C0FF"):
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    n = 8
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-14, 14), y0 + (y1 - y0) * t + rnd.uniform(-4, 4)))
    pts.append((x1, y1))
    d = "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    br = pts[3]
    d2 = f"M {br[0]:.1f} {br[1]:.1f} l {rnd.uniform(-30, -14):.1f} {rnd.uniform(14, 24):.1f} l {rnd.uniform(-8, 4):.1f} {rnd.uniform(12, 20):.1f}"
    return (f'<path d="{d} {d2}" stroke="{glow}" stroke-width="{w * 4}" fill="none" opacity="0.18" stroke-linejoin="round"/>'
            f'<path d="{d} {d2}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round"/>')


def soft_cloud(D, puffs, pal, seed, L=(0, -1), op=1.0, key=None):
    """Volumetric cloud / smoke from soft-edged puffs (radial gradients): shadow puffs first, then body, then lit
    caps offset toward the light. puffs = [(x, y, r), ...]."""
    rnd = random.Random(seed)
    lx, ly = unit(*L)
    gd = D.rad([(0, pal[2], 0.9), (0.6, pal[2], 0.5), (1, pal[2], 0)])
    gb = D.rad([(0, pal[1], 0.95), (0.55, pal[1], 0.6), (1, pal[1], 0)])
    gl = D.rad([(0, pal[0], 0.9), (0.5, pal[0], 0.4), (1, pal[0], 0)])
    out = [f'<g opacity="{op}">']
    for x, y, r in puffs:
        out.append(f'<path d="{blob(x - lx * r * 0.25, y - ly * r * 0.25, r * 1.1, r * 0.9, rnd.randint(0, 9999), 0.12, 14)}" fill="{gd}"/>')
    for x, y, r in puffs:
        out.append(f'<path d="{blob(x, y, r, r * 0.85, rnd.randint(0, 9999), 0.14, 14)}" fill="{gb}"/>')
    for x, y, r in puffs:
        out.append(f'<path d="{blob(x + lx * r * 0.3, y + ly * r * 0.3, r * 0.62, r * 0.5, rnd.randint(0, 9999), 0.16, 12)}" fill="{gl}"/>')
    out.append("</g>")
    return "".join(out)


def vignette(D, cx, cy, r0, col="#000000", op=0.6, r1=1.0):
    """Chiaroscuro: darken everything away from the focal point (cx, cy)."""
    g = D.rad([(0, col, 0), (r0, col, 0), (r1, col, op)], cx=round(cx / 600, 3), cy=round(cy / 600, 3), r=0.75)
    return f'<rect x="-10" y="-10" width="620" height="620" fill="{g}"/>'


def light_pool(D, cx, cy, r, col, op=0.5):
    """Warm light thrown on everything near a source (a soft additive-looking glaze)."""
    g = D.rad([(0, col, op), (0.5, col, op * 0.4), (1, col, 0)])
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


# ================================================================ G1. prometheus: the fire carried down from Olympus
@gallery("prometheus", seed=21, edge=3.0, bristle=0.5, grain=0.2)
def prometheus_g():
    D = Doc2("myg-pr")
    rnd = random.Random(7)
    out = [sky(D, [(0, "#07060F"), (0.3, "#150F26"), (0.6, "#2E1A34"), (0.8, "#4A2430"), (1, "#120A12")], 3, 600,
               ["#2A1A3A", "#0A0814", "#4A2A3A"], 80, sop=(0.08, 0.2))]
    # Olympus far off on the right, its summit in the storm
    out.append(hill(D, ridge([(300, 330), (400, 250), (470, 196), (520, 220), (640, 300)], 3, 10, 4), 620, ("#3A2A44", "#22182E", "#0E0A16"), 2, inkw=0, sop=(0.06, 0.16)))
    out.append(soft_cloud(D, [(x, 150 + 40 * math.sin(x / 70) + rnd.uniform(-20, 20), rnd.uniform(50, 80)) for x in range(-40, 680, 50)],
                          ("#6A4A6A", "#2A1E36", "#0A0812"), 4, L=(0.2, 1), op=0.95))
    out.append(soft_cloud(D, [(x, 90 + rnd.uniform(-30, 30), rnd.uniform(50, 90)) for x in range(-40, 680, 60)], ("#4A3A5A", "#1C1428", "#05040A"), 5, op=0.9))
    out.append(soft_glow(D, 505, 180, 150, "#A8A0FF", 0.35))
    out.append(bolt(512, 160, 470, 300, 3, w=2.4))
    # the plain of men far below: dark land, mist, and the first hearth fires
    out.append(hill(D, ridge([(-20, 400), (120, 388), (260, 404), (380, 394), (620, 410)], 7, 6, 3), 620, ("#3A2430", "#1E1220", "#0A060C"), 8, inkw=0, sop=(0.06, 0.16)))
    out.append(mist(D, 404, 46, 5, "#7A4A5A", 0.35))
    for (hx, hy, s_) in ((60, 446, 1.0), (104, 466, 0.8), (150, 440, 0.7), (196, 470, 0.9), (34, 486, 0.8), (240, 448, 0.6), (130, 498, 1.1), (280, 476, 0.7)):
        out.append(smoke(D, [(hx, hy - 2), (hx + 5, hy - 18), (hx - 3, hy - 34), (hx + 8, hy - 52)], 2, 8, int(hx), "#8A5A6A", 0.22))
        out.append(soft_glow(D, hx, hy, 22 * s_, "#FF9A40", 0.75))
        out.append(fire(D, hx, hy + 2, 7 * s_, int(hx), glow=False, n=4))
    # the crag: a tall pinnacle on the right, the path cut along its shoulder
    rock = [(236, 620), (268, 540), (318, 500), (364, 484), (402, 474), (436, 452), (468, 404), (492, 340), (520, 300), (560, 270), (620, 250), (630, 620)]
    out.append(cliff(D, rock, ("#8A5248", "#2E1C22", "#0A0608"), 5, L=(-0.3, -1), lit="#FFB070", faces=26, strata=12, op_lit=0.95, src=(420, 260, 330)))
    out.append(cliff(D, [(-30, 620), (-30, 556), (60, 536), (160, 548), (240, 574), (290, 620)], ("#4A2A2E", "#180E12", "#050304"), 6, L=(0.6, -0.8), lit="#8A4A4A", faces=8, strata=4))
    out.append(grass(5, (300, 490, 470, 500), ["#2A1810", "#4A2A1A"], 20, (4, 9)))
    # Prometheus striding down, the fennel stalk raised high, the chlamys streaming back in the storm wind
    fx, fb, H = 398, 482, 212
    J = pose("side", head=(0.22, -7.42), neck=(0.06, -6.72), sR=(0.1, -6.22), sL=(-0.06, -6.22),
             eR=(0.5, -7.3), wR=(0.72, -8.45), handR=(0.8, -9.0), eL=(-0.38, -4.95), wL=(-0.5, -3.85),
             hR=(0.02, -4.0), hL=(-0.06, -4.0), kR=(0.66, -2.2), aR=(0.86, -0.14), tR=(1.5, 0.08), kL=(-0.3, -2.05), aL=(-0.98, -0.52), tL=(-0.42, -0.32))
    Lf = (0.45, -0.9)
    B, M_ = human(D, fx, fb, H, J, ("#6A3A2C", "#22120E", "#050202"), 17, L=Lf, rim="#FFD08A", flip=True, rim_d=3.0, fur_n=0.3)
    drape(B, M_, [(-0.5, -6.3), (0.48, -6.15), (0.52, -5.2), (0.44, -4.6), (0.62, -3.7), (1.0, -2.95), (0.42, -2.8), (-0.1, -2.9), (-0.72, -3.05),
                  (-0.62, -3.8), (-0.52, -4.7)], flow=-80, pal=("#B0684A", "#5A2A1E", "#160806"), shade=0.45)
    cloak = [(-0.2, -6.55), (-0.6, -6.35), (-1.3, -6.05), (-2.1, -5.7), (-2.9, -5.45), (-3.6, -5.7), (-3.25, -5.0), (-3.7, -4.35), (-3.0, -4.0),
             (-2.4, -3.45), (-1.55, -3.65), (-0.85, -4.2), (-0.52, -5.2)]
    drape(B, M_, cloak, flow=-170, pal=("#D85A40", "#7A1E16", "#200606"), shade=0.55, fur=0.8)
    B.overlay(folds(D, M_, [[(-0.6, -6.1), (-1.6, -5.35), (-2.8, -4.75)], [(-0.7, -5.6), (-1.5, -4.65), (-2.4, -4.05)], [(-1.0, -6.0), (-2.2, -5.45), (-3.2, -5.05)]],
                    "#FFA070", H * 0.014, 3, 0.45))
    B.overlay(folds(D, M_, [[(0.1, -4.5), (0.35, -3.3), (0.6, -3.0)], [(-0.2, -4.4), (-0.25, -3.2)], [(-0.45, -4.3), (-0.6, -3.1)]], "#000000", H * 0.012, 4, 0.45))
    hc = J["head"]
    B.mass(M_([(hc[0] - 0.44, hc[1] - 0.02), (hc[0] - 0.34, hc[1] - 0.46), (hc[0] + 0.04, hc[1] - 0.6), (hc[0] + 0.34, hc[1] - 0.46), (hc[0] + 0.24, hc[1] - 0.26),
                (hc[0] - 0.08, hc[1] - 0.18), (hc[0] - 0.18, hc[1] + 0.22), (hc[0] - 0.38, hc[1] + 0.34)]), flow=170, pal=("#6A4030", "#22140C", "#050302"), fur=0.6)
    B.mass(M_([(hc[0] + 0.08, hc[1] + 0.18), (hc[0] + 0.44, hc[1] + 0.2), (hc[0] + 0.38, hc[1] + 0.64), (hc[0] + 0.12, hc[1] + 0.74), (hc[0] - 0.04, hc[1] + 0.4)]),
           flow=90, pal=("#6A4030", "#22140C", "#050302"), fur=0.5)
    out.append(cast(D, fx - 10, fb + 2, 70, 8, "#000000", 0.5, 3))
    (tx_, ty_), = M_([(J["handR"][0] + 0.5, J["handR"][1] - 1.6)])
    out.append(light_pool(D, tx_, ty_, 300, "#FF9A40", 0.34))
    out.append(B.render())
    # the fennel stalk (narthex) with the stolen fire smouldering in its pith
    (hx_, hy_), = M_([J["handR"]])
    top = (hx_ + 12, hy_ - 50)
    bot = (hx_ - 14, hy_ + 32)
    out.append(taper([bot, (hx_, hy_), top], 8, 6, "#3A3418"))
    out.append(ink(smooth_open([(bot[0] + 2.5, bot[1]), (hx_ + 2.5, hy_), (top[0] + 2.5, top[1])]), "#FFC870", 1.6, 3, 1, 0.7))
    for t in (0.2, 0.5, 0.78):
        nx_, ny_ = bot[0] + (top[0] - bot[0]) * t, bot[1] + (top[1] - bot[1]) * t
        out.append(f'<path d="M {nx_ - 4:.1f} {ny_ + 1:.1f} l 9 -2" stroke="#1E2410" stroke-width="2.4"/>')
    hand = M_([(J["handR"][0] - 0.22, J["handR"][1] + 0.3), (J["handR"][0] + 0.16, J["handR"][1] + 0.34), (J["handR"][0] + 0.22, J["handR"][1] - 0.12),
               (J["handR"][0] - 0.14, J["handR"][1] - 0.18)])
    out.append(model(D, hand, ("#E89A60", "#4A2214", "#120604"), 3, L=(0.3, -1), hi=0.5, edge="#000000"))
    for kk in range(3):
        a_ = M_([(J["handR"][0] - 0.12 + kk * 0.1, J["handR"][1] + 0.0), (J["handR"][0] - 0.1 + kk * 0.1, J["handR"][1] + 0.22)])
        out.append(ink(smooth_open(a_), "#120604", 1.0, kk, 1, 0.6))
    out.append(fire(D, top[0], top[1] + 6, 74, 8, lean=-0.3))
    for i in range(46):
        t = rnd.random()
        ex = top[0] - t * 380 + rnd.uniform(-24, 24)
        ey = top[1] - 30 + t * 260 + rnd.uniform(-34, 34) - math.sin(t * 3) * 60
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{rnd.uniform(0.8, 2.1) * (1 - t * 0.5):.1f}" fill="{rnd.choice(["#FFE8A0", "#FFB050", "#FF7A2A"])}" opacity="{rnd.uniform(0.4, 0.95) * (1 - t * 0.55):.2f}"/>')
    out.append(vignette(D, top[0], top[1] + 80, 0.25, "#05030A", 0.75))
    # lettering
    out.append(gilt(D, 300, 100, "PROMETHEUS", CINZEL, 58, ls=10, max_w=440, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 130, "GREEK · HE STOLE FIRE FOR US", CINZEL, 17, "#F2D8C8", ls=2.5, max_w=440))
    out.append(tx(206, 548, "Every hearth began with him.", SERIF_IT, 28, "#FFE6C8", max_w=300))
    return fin(D, out, 14, op=0.45)


def cliff(D, pts, pal, seed, L=(-0.5, -0.8), lit=None, strata=10, faces=16, edge="#000000", op_lit=0.75, vertical=True, src=None):
    """A cliff / crag painted the way Dore cut his rocks: graded mass, tall vertical faces alternately catching and
    losing the light, horizontal strata and cracks, rough dry-brush, a lit lip along the top edge."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = bbox(pts)
    d = smooth_closed(pts)
    out = [model(D, pts, pal, seed, L, flow=-88 if vertical else -10, sop=(0.08, 0.26), core=0.7, hi=0.2, edge=edge, edge_w=2.2, n=int((x1 - x0) * (y1 - y0) / 140))]
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for i in range(faces):
        fx = rnd.uniform(x0, x1)
        fw = rnd.uniform(10, 34)
        top_y = y0 + rnd.uniform(0, (y1 - y0) * 0.5)
        hgt = rnd.uniform(60, 220)
        skew = rnd.uniform(-10, 10)
        face = [(fx, top_y), (fx + fw, top_y + rnd.uniform(-8, 8)), (fx + fw + skew, top_y + hgt), (fx + skew * 0.6, top_y + hgt * rnd.uniform(0.8, 1.1))]
        lit_face = rnd.random() < 0.45
        inner.append(f'<path d="{pd(face)}" fill="{pal[0] if lit_face else pal[2]}" opacity="{rnd.uniform(0.1, 0.24):.2f}"/>')
        inner.append(taper([face[0], ((face[0][0] + face[3][0]) / 2 + rnd.uniform(-2, 2), (face[0][1] + face[3][1]) / 2), face[3]], 2.2, 0.4,
                           mix(pal[2], "#000000", 0.5), 0.45))
    for i in range(strata):
        sx, sy = rnd.uniform(x0, x1), rnd.uniform(y0 + 10, y1)
        c = [(sx, sy)]
        for j in range(5):
            sx += rnd.uniform(10, 22)
            sy += rnd.uniform(-5, 5)
            c.append((sx, sy))
        inner.append(taper(c, 2.0, 0.5, mix(pal[2], "#000000", 0.4), 0.5))
        inner.append(taper([(a, b - 2) for a, b in c], 1.4, 0.4, pal[0], 0.25))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if lit:
        out.append(rim_mask(D, [d], L, 3.4, lit, op_lit, src))
    return "".join(out)


def light_shafts(D, ox, oy, spec, col, seed):
    """God-rays falling from an opening: spec = [(angle_deg, spread_deg, length, opacity), ...]."""
    out = []
    for a, sp, Ln, op in spec:
        a0, a1 = math.radians(a - sp / 2), math.radians(a + sp / 2)
        g = D.lin([(0, col, op), (0.7, col, op * 0.3), (1, col, 0)], ox, oy, ox + math.cos(math.radians(a)) * Ln, oy + math.sin(math.radians(a)) * Ln, "userSpaceOnUse")
        out.append(f'<path d="M {ox:.1f} {oy:.1f} L {ox + math.cos(a0) * Ln:.1f} {oy + math.sin(a0) * Ln:.1f} L {ox + math.cos(a1) * Ln:.1f} {oy + math.sin(a1) * Ln:.1f} Z" fill="{g}"/>')
    return "".join(out)


# ================================================================ G2. orpheus: the climb out of the dark, not looking back
@gallery("orpheus", seed=23, edge=2.8, bristle=0.45, grain=0.2)
def orpheus_g():
    D = Doc2("myg-or")
    rnd = random.Random(11)
    out = [f'<rect width="600" height="600" fill="#0A0712"/>']
    # the way out: a ragged mouth at the top of the climb, the dawn world beyond it
    mouth = [(452, 334), (440, 280), (446, 226), (468, 186), (500, 168), (540, 166), (572, 180), (600, 200), (640, 230), (640, 380), (560, 372), (500, 360)]
    md = smooth_closed(mouth)
    cid = D.clip(f'<path d="{md}"/>')
    out.append(f'<g {cid}><rect x="430" y="150" width="220" height="240" fill="{D.lin([(0, "#FFF6DA"), (0.5, "#FFE6B0"), (1, "#F6C890")])}"/>'
               f'{hill(D, ridge([(430, 330), (500, 316), (560, 324), (650, 310)], 4, 6, 3), 400, ("#E8D0B0", "#C8AE94", "#9A8478"), 3, inkw=0, sop=(0.05, 0.12))}'
               f'{puff_cloud(D, 540, 240, 120, 5, pal=("#FFFFFF", "#FFF4E2", "#F2D4BA"), op=0.6)}</g>')
    out.append(soft_glow(D, 520, 270, 280, "#FFE6B0", 0.6))
    out.append(light_shafts(D, 500, 260, [(160, 12, 520, 0.3), (172, 8, 480, 0.22), (148, 9, 440, 0.2), (184, 6, 420, 0.14), (138, 6, 400, 0.12)], "#FFF0C8", 3))
    # the tunnel: a vault of rock overhead, the rock floor climbing to the light
    ceil = [(-30, -30), (640, -30), (640, 200), (600, 196), (560, 160), (500, 150), (452, 176), (420, 230), (360, 236), (280, 214), (190, 222), (100, 252), (-30, 270)]
    out.append(cliff(D, ceil, ("#4A3A4C", "#1A1220", "#05030A"), 3, L=(0.9, 0.4), lit="#FFD8A0", faces=30, strata=12, op_lit=0.9, src=(500, 250, 300)))
    floor_ = [(-30, 640), (-30, 520), (80, 506), (170, 482), (250, 460), (330, 420), (400, 380), (450, 350), (500, 334), (560, 330), (640, 340), (640, 640)]
    # the far wall of the passage, dim stone catching a little of the daylight
    back = [(-30, 250), (100, 246), (200, 226), (300, 222), (420, 236), (460, 330), (300, 430), (100, 500), (-30, 520)]
    out.append(cliff(D, back, ("#3A3044", "#1E1828", "#0A0810"), 8, L=(1, -0.2), faces=26, strata=14, op_lit=0.0, edge=None))
    out.append(light_shafts(D, 500, 260, [(166, 10, 520, 0.18), (156, 6, 480, 0.14)], "#FFF0C8", 4))
    out.append(cliff(D, floor_, ("#6A5868", "#2A2030", "#0A060C"), 6, L=(0.7, -0.8), lit="#FFE6C0", faces=0, strata=22, vertical=False, op_lit=0.9, src=(500, 300, 420)))
    out.append(light_pool(D, 480, 340, 220, "#FFD8A0", 0.3))
    # rough steps up the slope
    for i, (sx, sy) in enumerate(((120, 498), (190, 478), (262, 452), (330, 418), (392, 384), (446, 352))):
        out.append(taper([(sx - 26, sy + 4), (sx, sy + 1), (sx + 24, sy + 3)], 2.4, 1.0, "#FFE6C0", 0.45))
        out.append(taper([(sx - 24, sy + 7), (sx, sy + 5), (sx + 22, sy + 7)], 3.0, 1.0, "#05030A", 0.5))
    for (ax, ab, ah) in ((40, 560, 52), (80, 590, 64), (16, 600, 44), (300, 456, 26), (360, 420, 22), (230, 486, 28), (520, 600, 46), (560, 580, 40)):
        out.append(asphodel(D, ax, ab, ah, ax, "#E8E2F2"))
    # Orpheus near the top, lyre on his arm, eyes on the light
    B, M_, J = robed_walker(D, 392, 392, 178, 9, ("#6A5060", "#22161E", "#060306"), robe_pal=("#7A6A88", "#2A2236", "#08060C"), L=(1, -0.5),
                            rim="#FFE6B8", rim_d=2.2, kind="orpheus")
    out.append(B.render())
    (lx, ly), = M_([(1.12, -4.5)])
    out.append(chelys_lyre(D, lx, ly + 24, 0.34, 5, glow=False, strings="#FFF0C8"))
    # the near hand across the lyre
    (hx_, hy_), = M_([J["handR"]])
    hc = J["head"]
    for k in range(9):
        t = k / 8
        a = math.radians(190 + t * 150)
        px_, py_ = M_([(hc[0] + math.cos(a) * 0.42, hc[1] - 0.22 + math.sin(a) * 0.3)])[0]
        out.append(f'<path d="{blob(px_, py_, 2.0, 1.1, k, 0.1, 8, math.degrees(a) + 90)}" fill="#D8C070"/>')
    # Eurydice following, still a shade, pale and half transparent, her hand reaching toward him
    BE, ME, JE = robed_walker(D, 176, 488, 172, 13, ("#F2F0FF", "#B8C0E0", "#5A6488"), robe_pal=("#FFFFFF", "#C8D0EA", "#6A7498"), L=(1, -0.5),
                              rim="#FFFFFF", rim_d=2.0, kind="eurydice", edge="#2A3050", shade=0.35, lit=0.35)
    eur = BE.render()
    out.append(soft_glow(D, 200, 400, 140, "#C8D4FF", 0.3))
    out.append(f'<g opacity="0.78">{eur}</g>')
    for i in range(34):
        px, py = 196 + rnd.uniform(-80, 50), 484 - rnd.uniform(0, 158)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#E8F0FF" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    out.append(mist(D, 520, 70, 9, "#8A84A8", 0.3))
    out.append(vignette(D, 470, 300, 0.3, "#030206", 0.65))
    out.append(gilt(D, 300, 100, "ORPHEUS", CINZEL, 64, ls=14, max_w=420, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 130, "GREEK · AT THE GATES OF HADES", CINZEL, 17, "#E8E0F2", ls=2.5, max_w=440))
    out.append(f'<rect x="0" y="500" width="600" height="100" fill="{D.lin([(0, "#05030A", 0), (0.5, "#05030A", 0.5), (1, "#05030A", 0.7)])}"/>')
    out.append(tx(300, 552, "Don’t look back.", SERIF_IT, 50, "#FFF2DC", max_w=440))
    return fin(D, out, 15, op=0.45)


def robed_walker(D, x, base, h, seed, pal, robe_pal=None, L=(1, -0.4), rim=None, flip=False, rim_d=2.0, kind="orpheus", edge="#000000",
                 shade=0.45, lit=0.25, hair=("#5A4030", "#1E140C", "#050302")):
    """A robed figure in profile walking up a slope (facing +x before flip), leaning into the climb: the cloth is
    pulled tight over the forward thigh and knee and falls straight from the knee, the hem trails behind the back
    leg. kind 'orpheus' (long chiton + himation, the lyre arm bent at the chest) or 'eurydice' (peplos with an
    overfold, a veil falling down her back and trailing, one arm reaching forward). Returns (Beast, M, J)."""
    fem = kind == "eurydice"
    J = pose("side", head=(0.5, -7.36), neck=(0.32, -6.7), sR=(0.24, -6.2), sL=(0.16, -6.2), hR=(0.1, -3.95), hL=(0.04, -3.95),
             kR=(1.08, -2.62), aR=(1.2, -0.8), tR=(1.78, -0.62), kL=(-0.16, -2.0), aL=(-0.72, -0.4), tL=(-0.2, -0.04),
             eL=(-0.12, -4.9), wL=(0.0, -3.8), head_tilt=8, tilt=12)
    if fem:
        J.update(eR=(0.85, -5.35), wR=(1.6, -5.25), handR=(2.08, -5.36))
    else:
        J.update(eR=(0.36, -4.85), wR=(0.98, -5.32), handR=(1.22, -5.62))
    B, M = human(D, x, base, h, J, pal, seed, L=L, rim=rim, flip=flip, rim_d=rim_d, fur_n=0.2, legs=True, arms=("L",), edge=edge,
                 shade=shade, lit=lit, form="f" if fem else "m")
    rp = robe_pal or pal
    if fem:
        robe = [(0.28, -6.72), (0.58, -6.3), (0.72, -5.8), (0.66, -5.3), (0.5, -4.85), (0.62, -4.25), (0.86, -3.62), (1.18, -2.7), (1.28, -1.9),
                (1.33, -1.1), (1.42, -0.62), (1.2, -0.5), (0.8, -0.38), (0.3, -0.2), (-0.3, -0.05), (-0.9, 0.04), (-1.5, 0.06), (-1.62, -0.04),
                (-1.2, -0.4), (-0.85, -1.1), (-0.6, -2.0), (-0.42, -3.0), (-0.36, -3.8), (-0.22, -4.7), (-0.16, -5.6), (-0.06, -6.3), (0.12, -6.7)]
        over = [(-0.1, -6.25), (0.62, -6.15), (0.76, -5.4), (0.86, -4.6), (0.98, -4.05), (0.5, -3.92), (-0.05, -4.0), (-0.42, -3.9), (-0.3, -4.9)]
        veil = [(0.42, -8.02), (0.72, -7.96), (0.86, -7.68), (0.7, -7.6), (0.5, -7.5), (0.26, -7.2), (0.12, -6.7), (0.0, -6.1), (-0.14, -5.3),
                (-0.3, -4.5), (-0.6, -3.7), (-1.1, -3.0), (-1.7, -2.5), (-2.3, -2.25), (-1.85, -2.7), (-1.35, -3.3), (-0.95, -4.1), (-0.64, -5.0),
                (-0.4, -6.0), (-0.12, -7.0), (0.1, -7.7)]
    else:
        robe = [(0.3, -6.74), (0.62, -6.1), (0.66, -5.4), (0.54, -4.75), (0.64, -4.2), (0.9, -3.6), (1.22, -2.75), (1.3, -1.9), (1.34, -1.1),
                (1.38, -0.78), (1.0, -0.64), (0.6, -0.5), (0.1, -0.3), (-0.4, -0.14), (-0.88, -0.04), (-1.08, -0.12), (-0.96, -0.72),
                (-0.76, -1.6), (-0.56, -2.6), (-0.4, -3.6), (-0.28, -4.6), (-0.2, -5.5), (-0.1, -6.2), (0.1, -6.7)]
        over = [(-0.2, -6.0), (-0.05, -6.5), (0.36, -6.62), (0.62, -6.0), (0.7, -5.0), (0.8, -4.3), (1.02, -3.62), (0.6, -3.3), (0.1, -3.5),
                (-0.42, -3.62), (-0.32, -4.6)]
        veil = None
    drape(B, M, robe, flow=-92, pal=rp, shade=0.5, fur=0.9)
    drape(B, M, over, flow=-60, pal=(mix(rp[0], "#FFFFFF", 0.1), mix(rp[1], rp[0], 0.15), rp[2]), shade=0.5, fur=0.7)
    fl = [[(0.62, -3.95), (0.95, -3.05), (1.12, -2.5)], [(0.4, -3.7), (0.8, -2.6), (0.95, -2.3)], [(1.12, -2.4), (1.18, -1.4), (1.22, -0.75)],
          [(0.86, -2.3), (0.9, -1.2), (0.86, -0.6)], [(0.2, -3.6), (0.15, -2.0), (0.1, -0.4)], [(-0.2, -3.4), (-0.42, -1.8), (-0.6, -0.2)],
          [(-0.3, -2.6), (-0.7, -1.0), (-0.9, -0.12)]]
    if fem:
        fl += [[(0.2, -6.0), (0.45, -5.0)], [(0.0, -5.6), (0.4, -4.1)], [(0.55, -5.9), (0.8, -4.3)], [(-0.4, -1.0), (-1.2, -0.1)]]
    else:
        fl += [[(-0.05, -6.3), (0.4, -5.0), (0.85, -3.7)], [(-0.18, -5.6), (0.25, -4.4), (0.6, -3.5)]]
    B.overlay(folds(D, M, fl, rp[2], h * 0.014, seed, 0.55))
    B.overlay(folds(D, M, [[(p[0] + 0.07, p[1]) for p in f] for f in fl[:5]], rp[0], h * 0.008, seed + 1, 0.45))
    hc = J["head"]
    if fem:
        drape(B, M, veil, flow=120, pal=(mix(rp[0], "#FFFFFF", 0.2), rp[1], rp[2]), shade=0.35, fur=0.8)
        B.overlay(folds(D, M, [[(0.3, -7.4), (0.05, -6.0), (-0.3, -4.6), (-1.0, -3.3)], [(-0.1, -5.8), (-0.6, -4.2), (-1.4, -3.0)]], rp[2], h * 0.01, seed + 2, 0.4))
    else:
        B.mass(M([(hc[0] - 0.44, hc[1] + 0.05), (hc[0] - 0.38, hc[1] - 0.42), (hc[0] - 0.02, hc[1] - 0.6), (hc[0] + 0.32, hc[1] - 0.5), (hc[0] + 0.36, hc[1] - 0.28),
                   (hc[0] + 0.05, hc[1] - 0.24), (hc[0] - 0.12, hc[1] + 0.12), (hc[0] - 0.14, hc[1] + 0.5), (hc[0] - 0.38, hc[1] + 0.5)]), flow=110, pal=hair, fur=1.0)
        B.mass(M([(hc[0] + 0.12, hc[1] + 0.22), (hc[0] + 0.42, hc[1] + 0.26), (hc[0] + 0.36, hc[1] + 0.56), (hc[0] + 0.14, hc[1] + 0.62), (hc[0] - 0.04, hc[1] + 0.36)]),
               flow=90, pal=hair, fur=0.5)
    s_, e_, w_ = J["sR"], J["eR"], J["wR"]
    B.limb(M([s_, ((s_[0] + e_[0]) / 2, (s_[1] + e_[1]) / 2), e_]), [h / 8 * w for w in ((0.5 if fem else 0.6), 0.44, 0.36)], pal=rp)
    B.limb(M([e_, (e_[0] * 0.6 + w_[0] * 0.4, e_[1] * 0.6 + w_[1] * 0.4), w_]), [h / 8 * w for w in (0.34, 0.32, 0.22)])
    hn = J["handR"]
    B.limb(M([w_, ((w_[0] + hn[0]) / 2, (w_[1] + hn[1]) / 2), hn]), [h / 8 * 0.2, h / 8 * 0.22, h / 8 * 0.12], fur=0.1)
    return B, M, J


def serpent(D, pts, w0, w1, pal, seed, L=(-0.5, -0.8), head=True, eye="#E8F27A", tongue="#C8282A", mouth=0.0, rim=None, belly=None, scales=1.0):
    """A painted snake along pts: a tapering modelled body (lit back, dark flank, a paler belly line), scales laid
    along the body, rim light, and a wedge head with a brow ridge, a gleaming eye, optional open jaws and tongue."""
    rnd = random.Random(seed)
    P = catmull(pts, 6)
    n = len(P)
    ws = [w0 + (w1 - w0) * (i / (n - 1)) ** 1.2 for i in range(n)]
    B = Beast(D, pal, seed, L, rim=rim, rim_d=max(1.0, w0 * 0.12), edge="#000000", edge_d=max(0.8, w0 * 0.08), edge_op=0.6,
              fur_n=0, shade=0.55, lit=0.35, glob=0.4)
    B.limb(P, ws, cap0=True, cap1=not head, fur=0)
    # scales: small overlapping lenses along the body
    sc = []
    Pr, Wr = fresample(P, ws, max(1.5, w0 * 0.22))
    tans, norms = fframes(Pr)
    for i in range(0, len(Pr), 1):
        for u in (-0.3, 0.0, 0.3):
            if rnd.random() > 0.8 * scales:
                continue
            x, y = Pr[i][0] + norms[i][0] * u * Wr[i], Pr[i][1] + norms[i][1] * u * Wr[i]
            a = math.degrees(math.atan2(tans[i][1], tans[i][0]))
            r = Wr[i] * 0.16
            sc.append(f'<path d="{blob(x, y, r * 1.2, r * 0.8, rnd.randint(0, 999), 0.05, 8, a)}" fill="none" stroke="{rnd.choice([pal[2], pal[0]])}" '
                      f'stroke-width="{max(0.5, r * 0.3):.1f}" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>')
    B.overlay("".join(sc))
    if belly:
        side = ftube_side(P, ws, (-L[0], -L[1]), 0.18, lit=False, cap1=not head)
        B.overlay(f'<path d="{smooth_closed(side)}" fill="{belly}" opacity="0.45"/>')
    out = [B.render()]
    if head:
        (x, y), (px, py) = P[-1], P[-3]
        a = math.atan2(y - py, x - px)
        hw = w1 * 1.7
        hl = w1 * 2.6

        def H(u, v):
            return (x + math.cos(a) * u - math.sin(a) * v, y + math.sin(a) * u + math.cos(a) * v)
        if mouth:
            up = [H(-hl * 0.2, -hw * 0.5), H(hl * 0.35, -hw * 0.62), H(hl * 0.85, -hw * 0.45 - mouth * hw * 0.5), H(hl * 1.05, -hw * 0.2 - mouth * hw * 0.9),
                  H(hl * 0.45, -hw * 0.05), H(-hl * 0.1, hw * 0.1)]
            lo = [H(-hl * 0.1, -hw * 0.05), H(hl * 0.45, hw * 0.1), H(hl * 0.95, hw * 0.25 + mouth * hw * 0.8), H(hl * 0.7, hw * 0.5), H(hl * 0.1, hw * 0.55),
                  H(-hl * 0.25, hw * 0.4)]
            out.append(f'<path d="{smooth_closed([H(hl * 0.2, 0), H(hl * 1.0, -mouth * hw * 0.8), H(hl * 0.95, mouth * hw * 0.7)])}" fill="#3A0A0A"/>')
            out.append(model(D, lo, pal, seed + 3, L, hi=0.3, edge="#000000", edge_w=1))
            out.append(model(D, up, pal, seed + 4, L, hi=0.4, edge="#000000", edge_w=1, rim=rim, rim_w=1.4))
            if tongue:
                t0 = H(hl * 0.5, 0)
                t1 = H(hl * 1.5, mouth * hw * 0.2)
                out.append(f'<path d="M {t0[0]:.1f} {t0[1]:.1f} L {t1[0]:.1f} {t1[1]:.1f} l {math.cos(a - 0.5) * hw * 0.4:.1f} {math.sin(a - 0.5) * hw * 0.4:.1f} '
                           f'M {t1[0]:.1f} {t1[1]:.1f} l {math.cos(a + 0.5) * hw * 0.4:.1f} {math.sin(a + 0.5) * hw * 0.4:.1f}" stroke="{tongue}" stroke-width="{max(0.8, w1 * 0.18):.1f}" fill="none"/>')
            ep = H(hl * 0.28, -hw * 0.3)
        else:
            hd_ = [H(-hl * 0.25, -hw * 0.45), H(hl * 0.3, -hw * 0.55), H(hl * 0.8, -hw * 0.36), H(hl * 1.05, 0), H(hl * 0.8, hw * 0.36), H(hl * 0.3, hw * 0.55), H(-hl * 0.25, hw * 0.45)]
            out.append(model(D, hd_, pal, seed + 3, L, hi=0.4, edge="#000000", edge_w=1, rim=rim, rim_w=1.4))
            ep = H(hl * 0.35, -hw * 0.25)
            if tongue:
                t0 = H(hl * 1.0, 0)
                t1 = H(hl * 1.6, 0)
                out.append(f'<path d="M {t0[0]:.1f} {t0[1]:.1f} L {t1[0]:.1f} {t1[1]:.1f} l {math.cos(a - 0.5) * hw * 0.4:.1f} {math.sin(a - 0.5) * hw * 0.4:.1f} '
                           f'M {t1[0]:.1f} {t1[1]:.1f} l {math.cos(a + 0.5) * hw * 0.4:.1f} {math.sin(a + 0.5) * hw * 0.4:.1f}" stroke="{tongue}" stroke-width="{max(0.8, w1 * 0.18):.1f}" fill="none"/>')
        out.append(soft_glow(D, ep[0], ep[1], hw * 0.7, eye, 0.5))
        out.append(f'<circle cx="{ep[0]:.1f}" cy="{ep[1]:.1f}" r="{max(0.9, hw * 0.16):.1f}" fill="{eye}"/>')
        out.append(f'<path d="M {ep[0]:.1f} {ep[1] - hw * 0.12:.1f} L {ep[0]:.1f} {ep[1] + hw * 0.12:.1f}" stroke="#000000" stroke-width="{max(0.5, hw * 0.06):.1f}"/>')
    return "".join(out)


def corinthian_helmet(D, cx, cy, s, seed, L=(-0.7, -0.6), glint="#D8F2B8", rim="#FFE0A0"):
    """A bronze Corinthian helmet seen from behind and to the right, the wearer looking up-left: the domed skull,
    the flared neck guard, the edge of the right cheek-piece, a raised border, and a tall horsehair crest on its
    stilt falling down the back. Metal painted with dark mirror reflections and bright speculars. s = dome radius."""
    rnd = random.Random(seed)

    def H(pts):
        return [(cx + px * s, cy + py * s) for px, py in pts]
    out = []
    helm = H([(-0.55, -0.92), (-0.05, -1.04), (0.45, -0.9), (0.82, -0.55), (0.98, -0.05), (1.02, 0.35), (1.14, 0.66), (1.0, 0.86), (0.6, 0.86),
              (0.2, 0.8), (-0.2, 0.84), (-0.52, 0.98), (-0.82, 0.84), (-0.9, 0.44), (-0.98, 0.0), (-0.92, -0.5)])
    d = smooth_closed(helm)
    g = D.lin([(0, "#F6D088"), (0.25, "#B07A30"), (0.5, "#5A3410"), (0.7, "#2A1806"), (1, "#7A5020")], 0.2, 0, 0.8, 1)
    out.append(f'<path d="{d}" fill="{g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # environment reflections: the green light of the shield on the left of the dome, the dark cave elsewhere
    inner.append(f'<path d="{smooth_closed(H([(-0.9, -0.3), (-0.6, -0.85), (-0.2, -0.95), (-0.35, -0.5), (-0.55, 0.1), (-0.8, 0.5)]))}" fill="{glint}" opacity="0.35"/>')
    inner.append(f'<path d="{smooth_closed(H([(0.2, -0.6), (0.7, -0.3), (0.8, 0.3), (0.5, 0.6), (0.15, 0.3)]))}" fill="#0E0802" opacity="0.6"/>')
    inner.append(flow_strokes(D, d, (cx - s, cy - s, cx + s * 1.2, cy + s), lambda X, Y: math.degrees(math.atan2(Y - cy, X - cx)) + 90,
                              ["#FFE6A8", "#3A2008", "#C8903A", "#1A0E04"], seed, 70, (s * 0.15, s * 0.5), (s * 0.02, s * 0.06), (0.15, 0.4), clip=False))
    # speculars: a long bright streak along the curve of the dome, a sharp spot
    inner.append(taper(catmull(H([(-0.7, -0.4), (-0.45, -0.78), (-0.05, -0.92), (0.3, -0.84)]), 6), s * 0.09, s * 0.02, "#FFF6D8", 0.85))
    inner.append(f'<path d="{blob(*H([(-0.48, -0.62)])[0], s * 0.08, s * 0.05, seed, 0.1, 10, -30)}" fill="#FFFFFF"/>')
    # neck guard flare catching the light, the raised border
    inner.append(taper(catmull(H([(0.98, 0.42), (1.08, 0.66), (0.95, 0.82)]), 6), s * 0.06, s * 0.02, "#FFE6A8", 0.7))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    border = H([(-0.82, 0.8), (-0.5, 0.92), (-0.2, 0.78), (0.2, 0.74), (0.6, 0.8), (0.98, 0.8), (1.08, 0.64)])
    out.append(ink(smooth_open(border), "#2A1404", s * 0.07, seed, 1, 0.8))
    out.append(ink(smooth_open([(px, py - s * 0.05) for px, py in border]), "#F2C878", s * 0.03, seed + 1, 1, 0.7))
    out.append(ink(smooth_open(H([(-0.88, 0.45), (-0.96, 0.0), (-0.9, -0.5)])), "#F2C878", s * 0.03, seed + 2, 1, 0.6))
    out.append(ink(d, "#0A0602", s * 0.035, seed + 3, 1, 0.8))
    # crest holder and the crest: red horsehair standing up in a fan, falling down the back
    out.append(f'<path d="{pd(H([(-0.12, -1.0), (-0.06, -1.22), (0.1, -1.22), (0.14, -0.98)]))}" fill="#3A2008"/>')
    crest = H([(-0.32, -1.18), (-0.2, -1.62), (0.1, -1.78), (0.5, -1.6), (0.86, -1.2), (1.1, -0.6), (1.22, 0.1), (1.12, 0.5), (0.98, 0.0),
               (0.82, -0.6), (0.52, -1.0), (0.2, -1.2)])
    out.append(model(D, crest, ("#F2785A", "#9A1E14", "#2A0404"), seed + 5, L, flow=lambda X, Y: math.degrees(math.atan2(Y - (cy - 1.1 * s), X - cx)),
                     n=160, slen=(s * 0.2, s * 0.6), sw=(s * 0.02, s * 0.05), sop=(0.25, 0.7), edge="#000000", edge_w=1.5, rim=rim, rim_w=2.5, hi=0.4))
    hairs = []
    for i in range(60):
        t = rnd.random()
        a0 = -2.2 + t * 2.0
        r0 = s * rnd.uniform(0.5, 0.7)
        bx, by = cx + 0.12 * s + math.cos(a0) * r0, cy - 1.0 * s + math.sin(a0) * r0 * 0.9
        L_ = s * rnd.uniform(0.25, 0.6)
        a1 = a0 + rnd.uniform(0.3, 0.7)
        hairs.append(taper([(bx, by), (bx + math.cos(a1) * L_ * 0.5, by + math.sin(a1) * L_ * 0.5), (bx + math.cos(a1 + 0.3) * L_, by + math.sin(a1 + 0.3) * L_)],
                           s * 0.03, 0.3, rnd.choice(["#FF9A78", "#7A0E08", "#D8402A", "#3A0404"]), rnd.uniform(0.4, 0.85)))
    out.append("".join(hairs))
    return "".join(out)


def medusa_face(D, cx, cy, s, seed, L=(0.0, 1.0)):
    """Medusa as the shield shows her: a grave, beautiful oval face mostly in shadow, lit from below by the green
    light, eyes burning, a crown of living serpents. Painted with planes of light rather than lines."""
    rnd = random.Random(seed)
    out = []
    # serpents behind the head
    specs = []
    for k in range(22):
        a0 = math.radians(-205 + k * (230 / 21) + rnd.uniform(-6, 6))
        specs.append((a0, rnd.uniform(0.7, 1.25), rnd.choice((-1, 1)), k))
    def snake_path(a0, r, curl, k):
        pts = []
        for j in range(7):
            t = j / 6
            a = a0 + curl * math.sin(t * math.pi * 1.4) * 0.5
            rr = 0.42 + r * t
            pts.append((cx + math.cos(a) * rr * s + math.cos(a + 1.57) * 0.12 * s * math.sin(t * 7 + k), cy - 0.25 * s + math.sin(a) * rr * s * 0.95))
        return pts
    for layer in (0, 1):
        for a0, r, curl, k in specs:
            if k % 2 != layer:
                continue
            pal = rnd.choice([("#A8C87A", "#4A6A30", "#0A1A08"), ("#C8C07A", "#6A6A2A", "#1A1A06"), ("#8AB89A", "#2E5A44", "#06140C")]) if layer else ("#5A7A4A", "#1E3A1A", "#040A04")
            out.append(serpent(D, snake_path(a0, r, curl, k), s * 0.21, s * 0.09, pal, seed + k, L=(0, 1), rim="#D8FFB0" if layer else None,
                               mouth=0.7 if k % 5 == 1 else 0.0, belly="#E8E8A0"))
        if layer == 0:
            # shoulders and neck in a dark peplos, then the face
            sh = [(cx - 1.1 * s, cy + 1.9 * s), (cx - 0.95 * s, cy + 1.2 * s), (cx - 0.5 * s, cy + 0.95 * s), (cx - 0.18 * s, cy + 0.62 * s), (cx + 0.18 * s, cy + 0.62 * s),
                  (cx + 0.5 * s, cy + 0.95 * s), (cx + 0.95 * s, cy + 1.2 * s), (cx + 1.1 * s, cy + 1.9 * s)]
            out.append(model(D, sh, ("#5A7A5A", "#1A2A1C", "#040806"), seed + 40, L, flow=-80, sop=(0.1, 0.3), edge="#000000", rim="#B8E8A0", rim_w=2))
            face = [(cx, cy - 0.62 * s), (cx + 0.36 * s, cy - 0.5 * s), (cx + 0.46 * s, cy - 0.1 * s), (cx + 0.4 * s, cy + 0.3 * s), (cx + 0.22 * s, cy + 0.58 * s),
                    (cx, cy + 0.68 * s), (cx - 0.22 * s, cy + 0.58 * s), (cx - 0.4 * s, cy + 0.3 * s), (cx - 0.46 * s, cy - 0.1 * s), (cx - 0.36 * s, cy - 0.5 * s)]
            out.append(model(D, face, ("#B8D0A0", "#4A6248", "#0E1A10"), seed + 41, L, core=1.2, hi=0.0, edge="#000000"))
            cid = D.clip(f'<path d="{smooth_closed(face)}"/>')
            planes = [
                [(cx - 0.05 * s, cy - 0.2 * s), (cx + 0.05 * s, cy - 0.2 * s), (cx + 0.08 * s, cy + 0.2 * s), (cx - 0.07 * s, cy + 0.22 * s)],
                [(cx - 0.4 * s, cy + 0.1 * s), (cx - 0.2 * s, cy + 0.12 * s), (cx - 0.16 * s, cy + 0.42 * s), (cx - 0.32 * s, cy + 0.38 * s)],
                [(cx + 0.4 * s, cy + 0.1 * s), (cx + 0.2 * s, cy + 0.12 * s), (cx + 0.16 * s, cy + 0.42 * s), (cx + 0.32 * s, cy + 0.38 * s)],
                [(cx - 0.14 * s, cy + 0.52 * s), (cx + 0.14 * s, cy + 0.52 * s), (cx + 0.08 * s, cy + 0.64 * s), (cx - 0.08 * s, cy + 0.64 * s)]]
            pl = "".join(f'<path d="{smooth_closed(p)}" fill="#D8F0B8" opacity="0.42"/>' for p in planes)
            # brows in shadow, the eyes burning
            pl += f'<path d="{smooth_closed([(cx - 0.42 * s, cy - 0.16 * s), (cx + 0.42 * s, cy - 0.16 * s), (cx + 0.4 * s, cy - 0.02 * s), (cx - 0.4 * s, cy - 0.02 * s)])}" fill="#050A04" opacity="0.6"/>'
            out.append(f'<g {cid}>{pl}</g>')
            for sg in (-1, 1):
                ex, ey = cx + sg * 0.19 * s, cy - 0.06 * s
                out.append(soft_glow(D, ex, ey, s * 0.22, "#F2FF8A", 0.7))
                out.append(f'<path d="{blob(ex, ey, s * 0.085, s * 0.04, seed + sg, 0.05, 10, sg * -8)}" fill="#F6FFB0"/>')
                out.append(f'<path d="M {ex:.1f} {ey - s * 0.035:.1f} L {ex:.1f} {ey + s * 0.035:.1f}" stroke="#0A1404" stroke-width="{max(0.8, s * 0.02):.1f}"/>')
            # the mouth, closed and grave
            out.append(taper([(cx - 0.12 * s, cy + 0.43 * s), (cx, cy + 0.41 * s), (cx + 0.12 * s, cy + 0.43 * s)], s * 0.035, s * 0.01, "#2A0A0A", 0.85))
            out.append(taper([(cx - 0.08 * s, cy + 0.46 * s), (cx + 0.08 * s, cy + 0.46 * s)], s * 0.03, s * 0.01, "#8A3A3A", 0.6))
    return "".join(out)


def stone_warrior(D, x, base, h, seed, flip=False, col=("#C8CCBE", "#8A8E82", "#3A3E36")):
    """A warrior turned to stone, shield raised and sword drawn back, frozen in grey."""
    J = pose("side", head=(0.3, -7.3), eR=(0.75, -5.6), wR=(1.1, -6.3), eL=(-0.6, -5.6), wL=(-1.1, -6.5), handL=(-1.4, -7.0),
             kR=(0.6, -2.1), aR=(0.9, -0.2), tR=(1.5, 0), kL=(-0.4, -2.0), aL=(-1.0, -0.3), tL=(-0.5, 0))
    B, M = human(D, x, base, h, J, col, seed, L=(0.6, -0.8), flip=flip, fur_n=0.3, edge="#1A1E18")
    drape(B, M, [(-0.5, -6.2), (0.5, -6.2), (0.55, -4.2), (0.8, -3.2), (-0.6, -3.1), (-0.5, -4.4)], flow=-90, shade=0.4)
    sh = [(0.9, -7.2), (1.6, -6.9), (1.75, -5.8), (1.6, -4.8), (0.9, -4.6), (0.75, -5.9)]
    B.mass(M(sh), flow=-90, shade=0.5)
    hc = J["head"]
    B.mass(M([(hc[0] - 0.4, hc[1] + 0.2), (hc[0] - 0.4, hc[1] - 0.4), (hc[0] + 0.1, hc[1] - 0.66), (hc[0] + 0.45, hc[1] - 0.3), (hc[0] + 0.4, hc[1] + 0.3),
               (hc[0] - 0.1, hc[1] - 0.6), (hc[0] - 0.6, hc[1] - 1.0), (hc[0] - 0.9, hc[1] - 0.8)]), flow=180, shade=0.4)
    out = [B.render()]
    a, b = M([J["handL"], (J["handL"][0] - 1.3, J["handL"][1] - 1.2)])
    out.append(taper([a, b], h * 0.03, h * 0.012, col[1]))
    return "".join(out)


# ================================================================ G3. medusa: seen only in the bronze shield
@gallery("medusa", seed=25, edge=2.6, bristle=0.45, grain=0.2)
def medusa_g():
    D = Doc2("myg-md")
    rnd = random.Random(3)
    out = [sky(D, [(0, "#06100C"), (0.5, "#0E2018"), (1, "#040806")], 1, 600, ["#1A3A2A", "#020604", "#24402E"], 70)]
    out.append(light_shafts(D, 40, -20, [(62, 14, 760, 0.2), (56, 6, 700, 0.12)], "#E8F2C8", 2))
    walls_l = [(-30, -30), (110, -30), (84, 120), (56, 260), (74, 420), (40, 640), (-30, 640)]
    walls_r = [(630, -30), (520, -30), (552, 120), (572, 240), (610, 330), (630, 330)]
    out.append(cliff(D, walls_l, ("#3A5244", "#14241C", "#040A06"), 4, L=(1, 0.2), lit="#A8D8A0", faces=18, strata=10, op_lit=0.6, src=(250, 300, 300)))
    out.append(cliff(D, walls_r, ("#3A5244", "#14241C", "#040A06"), 5, L=(-1, 0.2), lit="#A8D8A0", faces=12, strata=8, op_lit=0.5, src=(250, 300, 300)))
    floor_ = [(-30, 640), (-30, 520), (120, 506), (300, 500), (480, 508), (630, 500), (630, 640)]
    out.append(cliff(D, floor_, ("#3A5244", "#14241C", "#040A06"), 6, L=(-0.3, -1), lit="#B8E8A8", faces=0, strata=16, vertical=False, op_lit=0.5, src=(250, 420, 300)))
    for (bx, by, br) in ((90, 530, 18), (150, 552, 12), (60, 566, 13), (190, 534, 9), (520, 540, 14), (560, 560, 10)):
        out.append(model(D, blob_pts(bx, by, br, br * 0.7, int(bx), 0.15, 12), ("#9AA89A", "#5A665C", "#1A221C"), int(bx), (-0.4, -1), hi=0.4, edge="#000000", edge_w=1.4))
    for k in range(40):
        t = rnd.random()
        out.append(f'<circle cx="{40 + t * 360 + rnd.uniform(-30, 30):.1f}" cy="{t * 600 + rnd.uniform(-20, 20):.1f}" r="{rnd.uniform(0.5, 1.4):.1f}" fill="#F2FFE0" opacity="{rnd.uniform(0.2, 0.6):.2f}"/>')
    # Perseus, from behind: helmet, chlamys, the harpe low in his right hand, wings on his sandals
    fx, fb, H = 446, 584, 300
    J = pose("back", head=(-0.06, -7.42), head_tilt=-8, eL=(-1.5, -5.7), wL=(-2.1, -6.5), handL=(-2.4, -6.8), eR=(1.2, -4.9), wR=(1.35, -3.8), handR=(1.42, -3.3),
             kL=(-0.5, -2.1), aL=(-0.5, -0.3), tL=(-0.55, 0), kR=(0.58, -2.05), aR=(0.68, -0.28), tR=(0.78, 0.02))
    Lp = (-0.9, -0.4)
    B, M_ = human(D, fx, fb, H, J, ("#7A6050", "#2A1E18", "#080604"), 21, L=Lp, rim="#C8F0B0", rim_d=2.6, fur_n=0.3)
    drape(B, M_, [(-0.95, -6.3), (0.95, -6.3), (1.0, -4.8), (0.95, -3.2), (0.7, -2.9), (0.0, -3.0), (-0.7, -2.95), (-0.98, -3.2), (-1.0, -4.8)],
          flow=-90, pal=("#6A5A4A", "#2A2018", "#080604"), shade=0.45)
    cloak = [(-0.6, -6.6), (-0.3, -6.8), (0.3, -6.8), (0.95, -6.45), (1.12, -5.6), (1.1, -4.6), (1.22, -3.5), (1.34, -2.75), (1.0, -2.6), (0.62, -2.82),
             (0.2, -2.6), (-0.2, -2.86), (-0.55, -2.7), (-0.82, -2.95), (-0.86, -3.9), (-0.8, -4.9), (-0.86, -5.7)]
    drape(B, M_, cloak, flow=-92, pal=("#B8483A", "#5A1A12", "#140404"), shade=0.5, fur=0.8)
    B.overlay(folds(D, M_, [[(-0.6, -6.2), (-0.7, -4.4), (-0.8, -2.7)], [(0.0, -6.4), (0.05, -4.4), (0.1, -2.5)], [(0.6, -6.2), (0.75, -4.2), (0.95, -2.6)],
                            [(-0.3, -5.6), (-0.35, -3.0)], [(0.35, -5.6), (0.42, -3.0)]], "#140404", H * 0.016, 7, 0.55))
    B.overlay(folds(D, M_, [[(-0.75, -6.1), (-0.85, -4.6)], [(-0.12, -6.3), (-0.12, -4.6)]], "#C8F0B0", H * 0.008, 8, 0.4))
    # the kibisis, the bag that waits for her head, slung at his hip
    B.mass(M_([(0.7, -4.2), (1.25, -4.3), (1.4, -3.6), (1.2, -3.2), (0.8, -3.25), (0.65, -3.7)]), flow=-80, pal=("#8A6A3A", "#3A2A14", "#0E0804"), shade=0.5)
    # helmet seen from behind: dome and flared neck guard, the crest standing on top
    hc = J["head"]
    B.mass(M_([(hc[0] - 0.5, hc[1] + 0.5), (hc[0] - 0.52, hc[1] - 0.1), (hc[0] - 0.36, hc[1] - 0.5), (hc[0], hc[1] - 0.62), (hc[0] + 0.36, hc[1] - 0.5),
               (hc[0] + 0.52, hc[1] - 0.1), (hc[0] + 0.5, hc[1] + 0.5), (hc[0] + 0.6, hc[1] + 0.72), (hc[0], hc[1] + 0.66), (hc[0] - 0.6, hc[1] + 0.72)]),
           flow=lambda X, Y: 0, pal=("#E8B860", "#8A5A1E", "#2A1606"), shade=0.45, fur=0.4)
    fig = B.render()
    # far arm raised to the shield (behind the shield edge), drawn before the shield
    Ba = Beast(D, ("#7A6050", "#2A1E18", "#080604"), 22, L=Lp, rim="#C8F0B0", rim_d=2.4, fur_n=0.3)
    Ba.limb(M_([J["sL"], J["eL"], J["wL"], J["handL"]]), [H / 8 * w for w in (0.62, 0.5, 0.36, 0.3)])
    out.append(Ba.render())
    # the shield, polished like a mirror
    cx, cy, R = 232, 292, 150
    out.append(soft_glow(D, cx, cy, R * 1.8, "#B8F0A0", 0.3))
    out.append(cast(D, cx + 26, cy + 36, R * 1.05, R * 1.0, "#000000", 0.6, 2))
    g = D.lin([(0, "#FFE7A0"), (0.25, "#C8903A"), (0.5, "#5A3612"), (0.75, "#A87028"), (1, "#2A1606")], 0, 0, 1, 1)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{g}"/>')
    ring = smooth_closed(ell_pts(cx, cy, R, R, 0, 360, 60)[:-1])
    out.append(flow_strokes(D, ring, (cx - R, cy - R, cx + R, cy + R), lambda X, Y: math.degrees(math.atan2(Y - cy, X - cx)) + 90,
                            ["#FFE8A8", "#5A3410", "#E8B860", "#2A1604"], 5, 220, (12, 34), (1, 3), (0.15, 0.45)))
    for k in range(40):
        a = 2 * math.pi * k / 40
        r1, r2 = R - 6, R - 16
        a2 = a + 2 * math.pi / 80
        out.append(f'<path d="M {cx + math.cos(a) * r1:.1f} {cy + math.sin(a) * r1:.1f} L {cx + math.cos(a) * r2:.1f} {cy + math.sin(a) * r2:.1f} L {cx + math.cos(a2) * r2:.1f} {cy + math.sin(a2) * r2:.1f} L {cx + math.cos(a2) * (r1 - 4):.1f} {cy + math.sin(a2) * (r1 - 4):.1f}" stroke="#3A2006" stroke-width="1.8" fill="none" opacity="0.7"/>')
    out.append(f'<path d="{smooth_open(ell_pts(cx, cy, R - 3, R - 3, 190, 280, 16))}" stroke="#FFF2C8" stroke-width="3" fill="none" opacity="0.7" stroke-linecap="round"/>')
    Ri = R - 22
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri + 3}" fill="#1A0E04"/>')
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{Ri}"/>')
    sc = [f'<rect x="{cx - Ri}" y="{cy - Ri}" width="{2 * Ri}" height="{2 * Ri}" fill="{D.rad([(0, "#E8F2C0"), (0.4, "#7A9A68"), (1, "#14281A")], cx=0.5, cy=0.4, r=0.65)}"/>']
    sc.append(soft_cloud(D, [(cx - 60, cy - 60, 54), (cx + 50, cy - 70, 60), (cx, cy - 100, 46)], ("#F2FAD8", "#A8C890", "#3A5A3A"), 3, op=0.6))
    sc.append(stone_warrior(D, cx - 86, cy + 130, 136, 3, flip=False))
    sc.append(stone_warrior(D, cx + 90, cy + 136, 128, 4, flip=True))
    sc.append(f'<rect x="{cx - Ri}" y="{cy + 90}" width="{2 * Ri}" height="80" fill="{D.lin([(0, "#14281A", 0), (1, "#0A140C", 0.9)])}"/>')
    sc.append(medusa_face(D, cx, cy + 8, 56, 11))
    sc.append(f'<path d="{smooth_open(ell_pts(cx - 14, cy - 12, Ri * 0.9, Ri * 0.88, 196, 256, 12))}" stroke="#FFFFFF" stroke-width="11" fill="none" opacity="0.15" stroke-linecap="round"/>')
    sc.append(f'<path d="{smooth_open(ell_pts(cx - 14, cy - 12, Ri * 0.78, Ri * 0.76, 204, 236, 8))}" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.36" stroke-linecap="round"/>')
    sc.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri}" fill="{D.rad([(0, "#000000", 0), (0.72, "#000000", 0), (1, "#1A0E04", 0.7)])}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri}" fill="none" stroke="#FFE7A0" stroke-width="2" opacity="0.55"/>')
    out.append(ink(ring, "#120A02", 2.6, 6, 2, 0.8))
    out.append(light_pool(D, fx - 40, fb - 200, 220, "#A8E890", 0.18))
    out.append(cast(D, fx, fb + 2, 90, 10, "#000000", 0.55, 3))
    out.append(fig)
    # the crest: red horsehair standing up from front to back, fanned toward us
    (ccx, ccy), = M_([(hc[0], hc[1] - 0.62)])
    k_ = H / 8
    crest = [(ccx - k_ * 0.16, ccy + 4), (ccx - k_ * 0.3, ccy - k_ * 0.5), (ccx - k_ * 0.1, ccy - k_ * 1.0), (ccx + k_ * 0.3, ccy - k_ * 1.15),
             (ccx + k_ * 0.6, ccy - k_ * 0.9), (ccx + k_ * 0.66, ccy - k_ * 0.4), (ccx + k_ * 0.5, ccy + k_ * 0.2), (ccx + k_ * 0.28, ccy + k_ * 0.5),
             (ccx + k_ * 0.16, ccy + 4)]
    out.append(model(D, crest, ("#F2785A", "#9A1E14", "#2A0404"), 31, Lp, flow=lambda X, Y: math.degrees(math.atan2(Y - ccy - 10, X - ccx)), n=140,
                     slen=(4, 12), sw=(0.6, 1.6), sop=(0.25, 0.7), edge="#000000", edge_w=1.4, rim="#E8FFC8", rim_w=2.2, hi=0.35))
    for i in range(40):
        a0 = math.radians(rnd.uniform(-200, 20))
        bx_, by_ = ccx + k_ * 0.18 + math.cos(a0) * k_ * 0.62, ccy - k_ * 0.35 + math.sin(a0) * k_ * 0.6
        a1 = a0 + rnd.uniform(-0.3, 0.6)
        L_ = rnd.uniform(5, 12)
        out.append(taper([(bx_, by_), (bx_ + math.cos(a1) * L_, by_ + math.sin(a1) * L_)], 1.6, 0.3, rnd.choice(["#FF9A78", "#7A0E08", "#D8402A"]), rnd.uniform(0.4, 0.85)))
    # bronze glints on the helmet, the harpe, the winged sandals
    (hx_, hy_), = M_([(hc[0] - 0.3, hc[1] - 0.3)])
    out.append(taper([(hx_ - 4, hy_ + 10), (hx_, hy_), (hx_ + 12, hy_ - 8)], 3.2, 0.6, "#FFF2C8", 0.8))
    (rx_, ry_), = M_([J["handR"]])
    out.append(harpe(D, rx_, ry_, 62, 70, 5))
    for side, fl in (("L", True), ("R", False)):
        (ax_, ay_), = M_([J["a" + side]])
        out.append(talaria_wing(D, ax_ + (-6 if fl else 6), ay_ - 2, 26, flip=fl))
    out.append(vignette(D, cx + 40, cy + 40, 0.38, "#010402", 0.62))
    out.append(gilt(D, 300, 100, "MEDUSA", CINZEL, 66, ls=16, max_w=420, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 134, "GREEK · SEEN ONLY IN THE SHIELD", CINZEL, 17, "#DCEAD0", ls=2.5, max_w=440))
    return fin(D, out, 14, op=0.4)


def corinthian_profile(D, x, y, s, seed, ang=-12, L=(-0.8, -0.5), glint="#D8F2B8", rim="#E8F8C8", crest=("#F2785A", "#9A1E14", "#2A0404")):
    """A bronze Corinthian helmet in left-facing profile (the wearer looking at something on the left): rounded
    skull, the almond eye-slit under a heavy brow, the long nose guard, the cheek piece sweeping down to the chin,
    the notch under the ear and the flared neck guard; a raised border chased around the edge; a tall arched
    horsehair crest on its holder, hanging down at the back. (x, y) = top of the dome, s = helmet height."""
    rnd = random.Random(seed)

    def H(pts):
        return T(pts, x, y, s, False, ang)
    out = []
    shell = [(0, 0), (0.2, 0.02), (0.36, 0.12), (0.46, 0.3), (0.5, 0.52), (0.54, 0.7), (0.62, 0.86), (0.54, 0.92), (0.36, 0.88), (0.24, 0.82),
             (0.18, 0.7), (0.12, 0.8), (0.0, 0.94), (-0.22, 1.02), (-0.34, 0.98), (-0.38, 0.84), (-0.34, 0.68), (-0.4, 0.6), (-0.46, 0.5),
             (-0.48, 0.4), (-0.47, 0.3), (-0.4, 0.16), (-0.24, 0.04)]
    P = H(shell)
    d = smooth_closed(P)
    g = D.lin([(0, "#F2C878"), (0.3, "#A8702A"), (0.55, "#4A2A0C"), (0.8, "#1E1004"), (1, "#5A3A14")], 0.1, 0, 0.9, 1)
    out.append(f'<path d="{d}" fill="{g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # the green light of the shield reflected down the front and the brow, the dark cave on the back
    # mirror-like bronze: the bright cave light on the crown, a dark horizon band, green ground-light below
    inner.append(f'<path d="{smooth_closed(H([(-0.5, 0.22), (-0.3, 0.06), (0.0, 0.0), (0.3, 0.06), (0.48, 0.24), (0.3, 0.2), (0.0, 0.17), (-0.3, 0.22)]))}" fill="#FFE8B0" opacity="0.5"/>')
    inner.append(f'<path d="{smooth_closed(H([(-0.5, 0.3), (-0.2, 0.25), (0.1, 0.24), (0.5, 0.34), (0.5, 0.5), (0.2, 0.42), (-0.1, 0.45), (-0.5, 0.48)]))}" fill="#140A02" opacity="0.75"/>')
    inner.append(f'<path d="{smooth_closed(H([(-0.5, 0.55), (-0.2, 0.5), (0.1, 0.52), (0.45, 0.6), (0.62, 0.9), (0.0, 1.05), (-0.45, 1.0)]))}" fill="{glint}" opacity="0.28"/>')
    inner.append(f'<path d="{smooth_closed(H([(-0.5, 0.2), (-0.36, 0.08), (-0.24, 0.12), (-0.34, 0.3), (-0.36, 0.6), (-0.4, 0.95), (-0.5, 0.9)]))}" fill="{glint}" opacity="0.35"/>')
    bx, by = H([(0.0, 0.45)])[0]
    inner.append(flow_strokes(D, d, bbox(P), lambda X, Y: math.degrees(math.atan2(Y - by, X - bx)) + 90, ["#FFE6A8", "#3A2008", "#C8903A", "#1A0E04"],
                              seed, 120, (s * 0.06, s * 0.2), (s * 0.006, s * 0.02), (0.12, 0.35), clip=False))
    # speculars along the skull and the brow, a hot spot
    inner.append(taper(catmull(H([(-0.36, 0.14), (-0.18, 0.05), (0.06, 0.03), (0.26, 0.09)]), 6), s * 0.035, s * 0.008, "#FFF6D8", 0.9))
    inner.append(taper(catmull(H([(-0.44, 0.33), (-0.3, 0.29), (-0.14, 0.31)]), 6), s * 0.02, s * 0.006, "#FFF0C8", 0.75))
    inner.append(f'<path d="{blob(*H([(-0.14, 0.07)])[0], s * 0.03, s * 0.016, seed, 0.1, 10, ang)}" fill="#FFFFFF"/>')
    inner.append(taper(catmull(H([(0.5, 0.62), (0.56, 0.76), (0.6, 0.86)]), 6), s * 0.02, s * 0.006, "#FFE6A8", 0.7))
    # the cheek piece and the neck guard are separate planes: a shadow line between them, under the ear
    inner.append(taper(catmull(H([(0.18, 0.7), (0.22, 0.56), (0.3, 0.48), (0.44, 0.46)]), 6), s * 0.022, s * 0.006, "#120802", 0.7))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # the eye slit and the gap between the cheek pieces (dark), with a lit lower lip
    eye = H([(-0.47, 0.34), (-0.36, 0.3), (-0.22, 0.32), (-0.12, 0.39), (-0.22, 0.44), (-0.4, 0.44)])
    out.append(f'<path d="{smooth_closed(eye)}" fill="#050302"/>')
    out.append(ink(smooth_open(H([(-0.4, 0.44), (-0.26, 0.44), (-0.15, 0.42)])), "#FFE0A0", s * 0.008, seed, 1, 0.7))
    out.append(ink(smooth_open(H([(-0.4, 0.6), (-0.37, 0.72), (-0.36, 0.84)])), "#050302", s * 0.016, seed, 1, 0.8))
    # raised, chased border round the edge
    border = H([(0.6, 0.84), (0.52, 0.89), (0.36, 0.85), (0.24, 0.79), (0.18, 0.68), (0.11, 0.78), (0.0, 0.91), (-0.22, 0.99), (-0.33, 0.95),
                (-0.36, 0.84), (-0.33, 0.68), (-0.39, 0.6), (-0.45, 0.5), (-0.46, 0.4)])
    out.append(ink(smooth_open(border), "#2A1404", s * 0.022, seed, 1, 0.85))
    out.append(ink(smooth_open([(px + s * 0.008, py - s * 0.012) for px, py in border]), "#F2C878", s * 0.008, seed + 1, 1, 0.75))
    out.append(ink(d, "#0A0602", s * 0.012, seed + 3, 1, 0.8))
    out.append(rim_mask(D, [d], L, max(1.5, s * 0.012), rim, 0.8))
    # crest holder and the arched horsehair crest
    out.append(f'<path d="{smooth_closed(H([(-0.3, 0.06), (-0.16, -0.02), (0.1, -0.04), (0.34, 0.04), (0.36, 0.1), (0.1, 0.03), (-0.16, 0.05)]))}" fill="#3A2008"/>')
    cr = H([(-0.36, 0.04), (-0.4, -0.12), (-0.26, -0.3), (0.0, -0.4), (0.3, -0.38), (0.56, -0.24), (0.72, -0.02), (0.8, 0.26), (0.82, 0.6), (0.74, 0.74),
            (0.64, 0.44), (0.52, 0.2), (0.36, 0.06), (0.1, -0.01), (-0.16, 0.0)])
    cx_, cy_ = H([(0.12, 0.1)])[0]
    out.append(model(D, cr, crest, seed + 5, L, flow=lambda X, Y: math.degrees(math.atan2(Y - cy_, X - cx_)) + 70, n=200,
                     slen=(s * 0.05, s * 0.16), sw=(s * 0.005, s * 0.016), sop=(0.25, 0.7), edge="#000000", edge_w=1.4, rim=rim, rim_w=2.2, hi=0.4))
    hairs = []
    for i in range(70):
        t = rnd.random()
        a0 = math.radians(-160 + t * 230)
        bx_, by_ = cx_ + math.cos(a0) * s * 0.46, cy_ + math.sin(a0) * s * 0.44
        a1 = a0 + rnd.uniform(0.5, 1.0)
        L_ = s * rnd.uniform(0.06, 0.16)
        hairs.append(taper([(bx_, by_), (bx_ + math.cos(a1) * L_, by_ + math.sin(a1) * L_), (bx_ + math.cos(a1 + 0.4) * L_ * 1.6, by_ + math.sin(a1 + 0.4) * L_ * 1.6)],
                           s * 0.012, 0.3, rnd.choice([crest[0], crest[1], crest[2], "#D8402A"]), rnd.uniform(0.4, 0.85)))
    out.append("".join(hairs))
    return "".join(out)


def harpe(D, x, y, s, ang, seed, col=("#F2F6F0", "#A8B0B8", "#3A4048")):
    """Perseus' harpe: a short sword with a sickle hook on the back of the blade."""
    def H(pts):
        return T(pts, x, y, s, False, ang)
    blade = H([(0, -0.05), (0.7, -0.07), (0.95, -0.2), (1.02, -0.42), (0.92, -0.58), (0.94, -0.4), (0.85, -0.22), (0.7, 0.06), (0, 0.06)])
    out = [model(D, blade, col, seed, (-0.6, -0.8), hi=0.6, edge="#000000", edge_w=1, rim="#E8FFD0", rim_w=1.5)]
    out.append(taper(H([(-0.36, 0), (0, 0)]), s * 0.09, s * 0.08, "#3A2210"))
    out.append(taper(H([(0, -0.14), (0, 0.14)]), s * 0.05, s * 0.05, "#C8963A"))
    return "".join(out)


def talaria_wing(D, x, y, s, flip=False, col=("#FFFFFF", "#D8D8C8", "#6A6A5A")):
    """A small wing on Perseus' sandal: three layered rows of feathers sweeping back."""
    out = []
    for k, (L_, a) in enumerate(((1.0, -30), (0.82, -16), (0.62, -4))):
        f = T([(0, 0), (0.3 * L_, -0.16), (0.8 * L_, -0.22), (1.0 * L_, -0.1), (0.6 * L_, 0.02)], x, y + k * s * 0.05, s, flip, a)
        out.append(model(D, f, col, k, (0, -1), hi=0.5, edge="#1A1A10", edge_w=0.8))
    return "".join(out)


def cedar_g(D, x, base, h, seed, pal=("#8AB08A", "#3A6A50", "#10281C"), trunk=("#9A7A5A", "#4A3424", "#140C06"), L=(0.6, -0.8), haze=0.0,
            hazec="#C8D8C8", tiers=None, spread=1.0, detail=1.0, rim=None, sil=False):
    """A cedar of Lebanon: a massive trunk forking into near-horizontal limbs that carry flat, layered plates of
    needles, lit on top and dark beneath (the tree's unmistakable tiered silhouette). haze 0..1 pushes it back into
    the atmosphere; sil paints it as a flat silhouette against the light."""
    rnd = random.Random(seed)
    if haze:
        pal = tuple(mix(c, hazec, haze) for c in pal)
        trunk = tuple(mix(c, hazec, haze) for c in trunk)
    out = []
    tw = h * 0.06
    tr = [(x - tw * 1.4, base), (x - tw * 0.8, base - h * 0.08), (x - tw * 0.6, base - h * 0.45), (x - tw * 0.35, base - h * 0.85), (x + tw * 0.25, base - h * 0.85),
          (x + tw * 0.6, base - h * 0.45), (x + tw * 0.8, base - h * 0.08), (x + tw * 1.5, base)]
    if sil:
        out.append(f'<path d="{smooth_closed(tr)}" fill="{trunk[1]}"/>')
    else:
        out.append(model(D, tr, trunk, seed, L, flow=-90, sop=(0.15, 0.4), edge=None if haze > 0.4 else "#000000", hi=0.3, rim=rim))
    tiers = tiers or [(0.3, 1.0), (0.45, 0.92), (0.58, 0.8), (0.7, 0.64), (0.81, 0.48), (0.9, 0.32), (0.97, 0.16)]
    for i, (t, wf) in enumerate(tiers):
        y = base - h * t
        for side in (-1, 1):
            if rnd.random() < 0.2 and 0 < i < len(tiers) - 1:
                continue
            Lw = h * 0.4 * wf * spread * rnd.uniform(0.7, 1.15)
            cx = x + side * Lw * 0.48 + rnd.uniform(-h * 0.02, h * 0.02)
            out.append(taper([(x, y + h * 0.03), (x + side * Lw * 0.35, y + h * 0.012), (x + side * Lw * 0.8, y + h * 0.004)], tw * 0.45 * wf + 1, 1.0,
                             trunk[2] if not sil else trunk[1], 0.95))
            out.append(needle_plate(D, cx, y, Lw * 0.6, h * 0.04 * (0.8 + wf * 0.4), seed * 31 + i * 2 + side, pal, L, detail, sil))
    return "".join(out)


def hero_back(D, x, base, h, seed, pal, L, rim, kilt=("#C8A060", "#6A4A22", "#1A1006"), hair=("#3A2818", "#140C06", "#030201"), axe=True,
              wild=False, stride=1.0, flip=False):
    """A Mesopotamian hero seen from behind walking away, against the light: broad back, a fringed kilt, long
    curled hair (or Enkidu's wild mane), a great axe on the shoulder. Built on real proportion, painted dark with
    a rim of light."""
    J = pose("back", head=(0.02, -7.45), eR=(1.3, -6.25), wR=(0.95, -7.05), handR=(0.7, -7.35), eL=(-1.12, -5.0), wL=(-1.22, -3.85),
             kL=(-0.46, -2.15), aL=(-0.44, -0.55 * stride), tL=(-0.44, -0.2 * stride), kR=(0.5, -2.0), aR=(0.46, -0.2), tR=(0.5, 0.05))
    B, M = human(D, x, base, h, J, pal, seed, L=L, rim=rim, flip=flip, rim_d=max(1.4, h * 0.014), fur_n=0.2, shade=0.3, lit=0.15)
    k = [(-0.95, -4.25), (0.95, -4.25), (1.02, -3.4), (1.12, -2.5), (0.6, -2.42), (0.0, -2.5), (-0.6, -2.42), (-1.1, -2.5), (-1.02, -3.4)]
    drape(B, M, k, flow=-90, pal=kilt, shade=0.4)
    B.overlay(folds(D, M, [[(fx_, -3.9), (fx_ * 1.06, -2.5)] for fx_ in (-0.7, -0.35, 0.0, 0.35, 0.7)], kilt[2], h * 0.01, seed, 0.5))
    hc = J["head"]
    if wild:
        hr = [(hc[0] - 0.62, hc[1] + 0.9), (hc[0] - 0.72, hc[1] + 0.1), (hc[0] - 0.5, hc[1] - 0.52), (hc[0], hc[1] - 0.72), (hc[0] + 0.5, hc[1] - 0.52),
              (hc[0] + 0.74, hc[1] + 0.1), (hc[0] + 0.66, hc[1] + 0.95), (hc[0] + 0.3, hc[1] + 1.25), (hc[0] - 0.3, hc[1] + 1.3)]
    else:
        hr = [(hc[0] - 0.46, hc[1] + 0.7), (hc[0] - 0.5, hc[1] - 0.1), (hc[0] - 0.36, hc[1] - 0.5), (hc[0], hc[1] - 0.6), (hc[0] + 0.36, hc[1] - 0.5),
              (hc[0] + 0.5, hc[1] - 0.1), (hc[0] + 0.46, hc[1] + 0.7), (hc[0] + 0.26, hc[1] + 1.05), (hc[0] - 0.26, hc[1] + 1.05)]
    B.mass(M(hr), flow=90, pal=hair, fur=1.2, shade=0.4)
    out = [cast(D, x, base + 1, h * 0.3, h * 0.04, "#000000", 0.4, seed)]
    if axe:
        a, b = M([(0.32, -3.7), (0.62, -8.7)])
        out.append(taper([a, b], h * 0.028, h * 0.022, "#1A0E06"))
        bl = M([(0.45, -8.15), (1.25, -8.95), (1.6, -8.3), (1.35, -7.6), (0.62, -7.78)])
        out.append(model(D, bl, ("#E8E0D0", "#6A6A68", "#1A1A1E"), seed + 3, L, hi=0.4, edge="#000000", edge_w=1.2, rim=rim, rim_w=1.8))
    out.append(B.render())
    return "".join(out)


# ================================================================ G4. gilgamesh: into the cedar forest
@gallery("gilgamesh", seed=27, edge=2.6, bristle=0.5, grain=0.18)
def gilgamesh_g():
    D = Doc2("myg-gg")
    rnd = random.Random(5)
    out = [sky(D, [(0, "#FFF4D8"), (0.4, "#F6E2B4"), (0.7, "#D8C08A"), (1, "#8A7A50")], 3, 600, ["#FFF8E0", "#E8D0A0"], 40, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 300, 330, 230, "#FFFDF0", 0.95))
    # deep in the forest: cedars fading into the golden haze
    for (cx, b, h, hz, sd) in ((170, 400, 200, 0.82, 1), (250, 392, 150, 0.88, 2), (380, 394, 170, 0.86, 3), (450, 404, 210, 0.8, 4), (60, 410, 240, 0.74, 5), (560, 412, 250, 0.72, 6)):
        out.append(cedar_g(D, cx, b, h, sd, pal=("#5A6A50", "#4A5A44", "#3A4836"), trunk=("#5A5040", "#4A4034", "#3A3228"), haze=hz, hazec="#F2E2C0", sil=True))
    out.append(mist(D, 392, 80, 3, "#FFF6E0", 0.7))
    for (cx, b, h, hz, sd) in ((110, 470, 330, 0.5, 7), (500, 474, 340, 0.48, 8)):
        out.append(cedar_g(D, cx, b, h, sd, pal=("#4A5A40", "#34422E", "#24301E"), trunk=("#4A3E30", "#3A3024", "#2A2218"), haze=hz, hazec="#F2E2C0", sil=True))
    out.append(mist(D, 450, 60, 4, "#FFF0D0", 0.5))
    out.append(light_shafts(D, 300, 40, [(92, 9, 480, 0.3), (82, 7, 470, 0.22), (102, 6, 440, 0.2), (72, 5, 420, 0.14), (110, 4, 400, 0.14)], "#FFFAE8", 4))
    # the forest floor and the path toward the light
    out.append(hill(D, ridge([(-20, 470), (150, 462), (300, 458), (450, 464), (620, 470)], 5, 4, 3), 640, ("#7A6A40", "#3A3220", "#120E08"), 6, inkw=0, sop=(0.1, 0.25)))
    path = [(200, 640), (262, 540), (290, 486), (300, 462), (314, 462), (336, 486), (380, 540), (460, 640)]
    out.append(f'<path d="{smooth_closed(path)}" fill="{D.lin([(0, "#FFF0C8", 0.95), (0.5, "#E8C890", 0.7), (1, "#8A6A40", 0.5)])}"/>')
    out.append(grass(7, (-10, 466, 610, 600), ["#3A3A1C", "#2A2A14", "#5A5A2E", "#1A1A0A"], 260, (5, 14)))
    # vast near trunks framing the plate and a dark canopy overhead
    for (cx, sd, side) in ((30, 8, -1), (570, 9, 1)):
        tr = [(cx - 78, 640), (cx - 58, 420), (cx - 50, 200), (cx - 44, -20), (cx + 44, -20), (cx + 50, 200), (cx + 58, 420), (cx + 78, 640)]
        tr = [(cx - 96, 640), (cx - 70, 560), (cx - 58, 420), (cx - 50, 200), (cx - 44, -20), (cx + 44, -20), (cx + 50, 200), (cx + 58, 420), (cx + 70, 560), (cx + 96, 640)]
        out.append(model(D, tr, ("#6A5640", "#2A2016", "#0A0604"), sd, (-side, -0.3), flow=-90, sop=(0.12, 0.4), edge="#000000", n=220, slen=(20, 70), sw=(2, 5)))
        cid = D.clip(f'<path d="{smooth_closed(tr)}"/>')
        bark = []
        for k in range(26):
            bx = cx + rnd.uniform(-60, 60)
            y0 = rnd.uniform(-20, 560)
            seg = [(bx, y0)]
            for j in range(5):
                seg.append((seg[-1][0] + rnd.uniform(-4, 4), seg[-1][1] + rnd.uniform(14, 30)))
            bark.append(taper(seg, rnd.uniform(2, 4.5), 0.6, "#050302", rnd.uniform(0.4, 0.75)))
            bark.append(taper([(a_ + 2.5 * side * -1, b_) for a_, b_ in seg], rnd.uniform(1, 2.2), 0.4, "#C8A878", rnd.uniform(0.15, 0.35)))
        out.append(f'<g {cid}>{"".join(bark)}</g>')
        out.append(rim_mask(D, [smooth_closed(tr)], (-side, -0.2), 3.5, "#FFE8B0", 0.85, src=(300, 330, 330)))
    for (cx, y, rx, ry, sd) in ((60, 30, 200, 40, 10), (540, 24, 210, 40, 11), (300, -14, 260, 34, 12), (40, 170, 120, 22, 13), (580, 190, 110, 22, 14)):
        out.append(needle_plate(D, cx, y, rx, ry, sd, ("#3A4428", "#1A2212", "#0A1006"), detail=1.0, sil=True))
    # Gilgamesh and Enkidu walking in, axes on their shoulders, black against the light
    out.append(hero_back(D, 274, 520, 98, 21, ("#3A2A20", "#140C08", "#040202"), (0.0, -1), "#FFF0C8", wild=True,
                         kilt=("#4A3A24", "#1E160C", "#060402"), hair=("#2A1E14", "#0E0806", "#020101")))
    out.append(hero_back(D, 334, 526, 104, 22, ("#3A2A20", "#140C08", "#040202"), (0.0, -1), "#FFF0C8",
                         kilt=("#5A4426", "#241A0C", "#060402"), hair=("#2A1E14", "#0E0806", "#020101")))
    # the clay tablet the story was written on, with the line pressed into it
    tab = [(-20, 640), (-20, 520), (150, 512), (300, 516), (450, 510), (620, 520), (620, 640)]
    out.append(model(D, tab, ("#E8C89A", "#B8865A", "#6A4426"), 14, (0, -1), flow=0, sop=(0.08, 0.2), core=0.4, hi=0.4, edge="#3A2010", edge_w=2))
    out.append(cuneiform_rows(D, 70, 530, 526, 538, 1, 3, col="#6A4426", op=0.65, s=0.9))
    out.append(cuneiform_rows(D, 70, 530, 564, 576, 1, 4, col="#6A4426", op=0.65, s=0.9))
    out.append(tx(300, 557, "The oldest story ever written", SERIF_IT, 27, "#4A2A14", max_w=420))
    out.append(gilt(D, 300, 104, "GILGAMESH", CINZEL, 58, ls=10, max_w=440, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 134, "MESOPOTAMIAN · INTO THE CEDARS", CINZEL, 17, "#3A2A14", ls=2.5, max_w=440))
    return fin(D, out, 14, op=0.35)


def needle_plate(D, cx, y, rx, ry, seed, pal, L=(0, -1), detail=1.0, sil=False):
    """One flat tier of cedar foliage built from many small tufts: ragged needle edges, lit tufts on top, dark
    tufts underneath. sil=True paints it as a silhouette against the light (one value, ragged edge)."""
    rnd = random.Random(seed)
    out = []
    n = int(max(14, rx * ry / 9 * detail))
    tufts = []
    for i in range(n):
        u = rnd.uniform(-1, 1)
        x = cx + u * rx
        top = ry * math.sqrt(max(0.0, 1 - u * u)) * rnd.uniform(0.5, 1.1)
        yy = y - rnd.uniform(-0.3, 1.0) * top
        r = rnd.uniform(0.5, 1.0) * ry * 0.75
        lt = (y - yy) / max(1, ry)
        tufts.append((lt, x, yy, r))
    tufts.sort()
    for lt, x, yy, r in tufts:
        if sil:
            col = pal[1]
        else:
            col = pal[0] if lt > 0.55 else (pal[2] if lt < 0.0 else pal[1])
        d = blob(x, yy, r * 1.3, r * 0.75, rnd.randint(0, 99999), 0.3, 10, rnd.uniform(-15, 15))
        out.append(f'<path d="{d}" fill="{col}" opacity="{rnd.uniform(0.8, 1):.2f}"/>')
        if not sil and lt > 0.3 and rnd.random() < 0.5:
            out.append(taper([(x - r, yy - r * 0.4), (x, yy - r * 0.7), (x + r, yy - r * 0.45)], 1.4, 0.4, mix(pal[0], "#FFF6D0", 0.4), 0.6))
    # needle fringe along the bottom edge
    for i in range(int(rx / 2.5)):
        x = cx + rnd.uniform(-rx * 0.9, rx * 0.9)
        out.append(taper([(x, y + ry * 0.1), (x + rnd.uniform(-2, 2), y + ry * rnd.uniform(0.35, 0.6))], 1.6, 0.3, pal[2] if not sil else pal[1], 0.8))
    return "".join(out)


def sea_g(D, y0, y1, stops, seed, sun_x=None, glint="#FFE8B0", crest="#FFFFFF", trough="#000000", swell=14, n=160, cols=None, glit_w=60):
    """Painted open sea: graded water, long horizontal brush strokes, rows of swells (dark trough, lit crest)
    getting larger and further apart toward us, and a glitter path under a low sun."""
    rnd = random.Random(seed)
    g = D.lin(stops, 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="-10" y="{y0}" width="620" height="{y1 - y0 + 10}" fill="{g}"/>']
    d = f"M -10 {y0} L 610 {y0} L 610 {y1 + 10} L -10 {y1 + 10} Z"
    out.append(flow_strokes(D, d, (-60, y0, 640, y1), 0, cols or [stops[0][1], stops[-1][1], crest], seed, n, (40, 140), (1.5, 5), (0.08, 0.25), jit=2, clip=False))
    y = y0 + 4
    k = 0
    while y < y1:
        t = (y - y0) / max(1, y1 - y0)
        gap = 3 + t * swell
        for i in range(int(8 + 10 * (1 - t))):
            x = rnd.uniform(-40, 640)
            L_ = rnd.uniform(20, 60) * (0.6 + t * 1.6)
            out.append(taper([(x, y + 1.5 + t * 3), (x + L_ * 0.5, y + 2.5 + t * 4), (x + L_, y + 1.5 + t * 3)], 1 + t * 3.5, 0.5, trough, rnd.uniform(0.15, 0.35)))
            out.append(taper([(x + L_ * 0.1, y), (x + L_ * 0.5, y - 1 - t * 2), (x + L_ * 0.9, y)], 0.8 + t * 2, 0.4, crest, rnd.uniform(0.15, 0.45)))
        y += gap
        k += 1
    if sun_x is not None:
        y = y0 + 2
        while y < y1:
            t = (y - y0) / max(1, y1 - y0)
            for i in range(int(3 + 4 * (1 - t))):
                x = sun_x + rnd.gauss(0, glit_w * (0.4 + t))
                L_ = rnd.uniform(4, 16) * (0.5 + t * 1.5)
                out.append(taper([(x - L_ / 2, y), (x + L_ / 2, y + rnd.uniform(-0.6, 0.6))], 1 + t * 2.5, 0.5, glint, rnd.uniform(0.45, 0.95)))
            y += 2 + t * 7
    return "".join(out)


def waka_g(D, x0, x1, wl, seed, pal=("#8A5A3A", "#3A2016", "#0C0604"), rim="#FFC890", L=(-1, -0.3)):
    """A Maori waka in side view against the light: long low hull, the carved prow (tauihu) pierced with spirals at
    the right, the tall carved sternpost (taurapa) at the left, a lashed washstrake, paddlers' thwarts."""
    rnd = random.Random(seed)
    Lh = x1 - x0
    hull = [(x0, wl - 22), (x0 + Lh * 0.15, wl - 14), (x0 + Lh * 0.5, wl - 11), (x1 - Lh * 0.12, wl - 14), (x1, wl - 24), (x1 + 4, wl - 14),
            (x1 - Lh * 0.08, wl + 6), (x0 + Lh * 0.5, wl + 9), (x0 + Lh * 0.1, wl + 5), (x0 - 6, wl - 8)]
    out = [model(D, hull, pal, seed, L, flow=0, sop=(0.15, 0.4), edge="#000000", rim=rim, rim_w=2.4, hi=0.3)]
    band = catmull([(x0 + 6, wl - 15), (x0 + Lh * 0.5, wl - 6), (x1 - 10, wl - 13)], 6)
    out.append(taper(band, 3, 3, "#E8B880", 0.55))
    for k in range(14):
        px, py = band[int((k + 0.5) / 14 * (len(band) - 1))]
        out.append(f'<path d="M {px - 3:.1f} {py + 3:.1f} L {px:.1f} {py - 2:.1f} L {px + 3:.1f} {py + 3:.1f}" stroke="#8A2A1A" stroke-width="1.4" fill="none" opacity="0.8"/>')
    # taurapa: tall sternpost with a fretted spine
    sp = catmull([(x0 + 4, wl - 18), (x0 - 10, wl - 50), (x0 - 12, wl - 90), (x0 - 2, wl - 122), (x0 + 6, wl - 130)], 6)
    out.append(taper(sp, 14, 6, pal[2]))
    out.append(taper([(px + 3, py) for px, py in sp], 3, 1.5, rim, 0.7))
    for k in range(2, len(sp) - 2, 3):
        px, py = sp[k]
        out.append(f'<circle cx="{px - 1:.1f}" cy="{py:.1f}" r="2.6" fill="none" stroke="{rim}" stroke-width="1.2" opacity="0.6"/>')
    for k in range(6):
        px, py = sp[3 + k * 3] if 3 + k * 3 < len(sp) else sp[-1]
        out.append(taper([(px - 6, py), (px - 16, py - 4)], 2.4, 0.6, pal[2]))
    # tauihu: the prow, a carved figure with pierced spirals
    pr = [(x1 - 4, wl - 22), (x1 + 20, wl - 34), (x1 + 34, wl - 30), (x1 + 38, wl - 20), (x1 + 26, wl - 12), (x1 + 4, wl - 10)]
    out.append(model(D, pr, pal, seed + 2, L, edge="#000000", rim=rim, rim_w=2))
    for (sx, sy, r) in ((x1 + 16, wl - 24, 5), (x1 + 28, wl - 22, 4)):
        out.append(f'<path d="M {sx + r:.1f} {sy:.1f} A {r} {r} 0 1 0 {sx:.1f} {sy + r:.1f} A {r * 0.6:.1f} {r * 0.6:.1f} 0 1 0 {sx + r * 0.5:.1f} {sy:.1f}" stroke="{rim}" stroke-width="1.3" fill="none" opacity="0.8"/>')
    return "".join(out)


# ================================================================ G5. maui's fishhook: hauling up the land
@gallery("mauis-fishhook", seed=29, edge=2.6, bristle=0.5, grain=0.2)
def mauis_fishhook_g():
    D = Doc2("myg-mh")
    rnd = random.Random(9)
    sx, sy = 168, 368
    out = [sky(D, [(0, "#0A1030"), (0.25, "#1E2450"), (0.45, "#5A3A6A"), (0.58, "#C8606A"), (0.66, "#F2A060"), (0.7, "#FFD890")], 3, 372,
               ["#2A3060", "#8A4A6A", "#FFB070"], 70, sop=(0.06, 0.16))]
    out.append(stars_field(5, (0, 150, 600, 250), 50, r=(0.5, 1.3), op=(0.3, 0.9)))
    # Te Matau a Maui: the fishhook in the stars (the tail of Scorpius), low in the dawn
    hook = [(362, 168), (380, 180), (390, 198), (386, 218), (372, 228), (354, 226), (344, 212), (348, 198)]
    for i, (hx, hy) in enumerate(hook):
        out.append(soft_glow(D, hx, hy, 9, "#DCE8FF", 0.5))
        out.append(star4(hx, hy, 3.6 if i in (0, 4, 7) else 2.6, "#FFFFFF"))
    out.append(f'<path d="{smooth_open(hook)}" fill="none" stroke="#DCE8FF" stroke-width="1" opacity="0.25" stroke-dasharray="2 4"/>')
    out.append(soft_glow(D, sx, sy, 300, "#FFC870", 0.7))
    out.append(f'<path d="{blob(sx, sy + 4, 30, 30, 3, 0.02, 20)}" fill="{D.rad([(0, "#FFFDF0"), (0.7, "#FFE6A0"), (1, "#FFC870")])}"/>')
    out.append(stratus(D, 300, -40, 640, 16, ("#FFE6B0", "#C86A7A", "#4A2E5A"), 3, 34))
    out.append(stratus(D, 336, -40, 640, 10, ("#FFF0C8", "#E89A80", "#7A4A6A"), 4, 26))
    out.append(stratus(D, 250, 180, 640, 12, ("#F2B0A0", "#7A4A7A", "#2A2050"), 5, 18, op=0.8))
    out.append(sea_g(D, 370, 600, [(0, "#C88A7A"), (0.15, "#5A4A6A"), (0.5, "#1E2A4A"), (1, "#0A1024")], 4, sun_x=sx, swell=16))
    # the land rising from the deep, water pouring off it, birds already wheeling over it
    isl = ridge([(318, 386), (352, 350), (384, 310), (410, 300), (436, 262), (462, 226), (476, 210), (492, 222), (512, 250), (536, 244), (560, 270),
                 (590, 296), (640, 310)], 6, 8, 4) + [(640, 400), (318, 400)]
    out.append(mountain_isle(D, isl, 7, L=(-1, -0.25), src=(200, 340, 420)))
    out.append(smoke(D, [(476, 210), (486, 186), (478, 166), (494, 146)], 4, 16, 3, "#F2D8D0", 0.35))
    out.append(soft_cloud(D, [(x, 384 + rnd.uniform(-4, 4), rnd.uniform(14, 26)) for x in range(330, 640, 20)], ("#FFFFFF", "#E8E0F0", "#8A8AA8"), 8, op=0.85))
    for (bx, by, bs) in ((420, 200, 1.0), (440, 186, 0.8), (520, 210, 0.9), (395, 222, 0.7)):
        out.append(bird_v(bx, by, bs * 1.4, "#2A2030", 0.85))
    # the line, taut from Maui's hands down into the sea
    Mx, Mb, MH = 206, 454, 150
    J = pose("side", head=(-2.0, -6.95), neck=(-1.78, -6.3), sR=(-1.6, -5.85), sL=(-1.7, -5.85), hR=(-0.55, -3.55), hL=(-0.6, -3.55),
             eR=(-0.7, -5.45), wR=(0.08, -5.25), handR=(0.62, -5.2), eL=(-0.82, -5.25), wL=(-0.04, -5.05), handL=(0.5, -5.0),
             kR=(0.5, -2.05), aR=(1.4, -0.4), tR=(2.2, -0.34), kL=(-0.25, -1.75), aL=(-1.15, -0.2), tL=(-0.35, -0.02))
    B, M_ = human(D, Mx, Mb, MH, J, ("#4A2C20", "#1A0E0A", "#040202"), 11, L=(-1, -0.2), rim="#FFD49A", rim_d=2.4, fur_n=0.3)
    drape(B, M_, [(-1.0, -4.0), (-0.1, -3.9), (0.0, -3.5), (-0.05, -2.9), (-0.25, -2.8), (-0.4, -3.25), (-0.9, -3.3), (-1.15, -3.6)], flow=-60,
          pal=("#6A3A2A", "#2A120C", "#080302"), shade=0.4)
    hc = J["head"]
    B.mass(M_([(hc[0] - 0.42, hc[1] + 0.1), (hc[0] - 0.4, hc[1] - 0.45), (hc[0] - 0.05, hc[1] - 0.6), (hc[0] + 0.28, hc[1] - 0.48), (hc[0] - 0.02, hc[1] - 0.2),
               (hc[0] - 0.2, hc[1] + 0.3)]), flow=180, fur=0.6, shade=0.3)
    B.mass(M_([(hc[0] - 0.28, hc[1] - 0.5), (hc[0] - 0.2, hc[1] - 0.95), (hc[0] + 0.05, hc[1] - 1.0), (hc[0] + 0.1, hc[1] - 0.58)]), flow=-90, fur=0.3)
    (hx_, hy_), = M_([J["handR"]])
    line_end = (452, 404)
    out.append(f'<path d="M {hx_ - 30:.1f} {hy_ + 14:.1f} Q {hx_ - 10:.1f} {hy_ + 4:.1f} {hx_:.1f} {hy_:.1f} L {line_end[0]} {line_end[1]}" stroke="#FFE6B0" stroke-width="1.8" fill="none" opacity="0.9"/>')
    out.append(f'<path d="M {hx_:.1f} {hy_:.1f} L {line_end[0]} {line_end[1]}" stroke="#FFFFFF" stroke-width="5" fill="none" opacity="0.12"/>')
    out.append(soft_glow(D, line_end[0], line_end[1], 26, "#FFFFFF", 0.6))
    # the waka and the brothers, black against the sunrise
    wl = 470
    for i, px in enumerate((118, 150, 262)):
        out.append(paddler_g(D, px, wl - 8, 92, 30 + i, ("#3A2418", "#140A06", "#030101"), (-1, -0.2), "#FFD49A", phase=i * 1.7))
    out.append(B.render())
    out.append(waka_g(D, 80, 320, wl, 5))
    out.append(sea_g(D, 474, 600, [(0, "#2A2A4A"), (1, "#0A1024")], 6, sun_x=sx, swell=10, n=60))
    for k in range(30):
        fx = rnd.uniform(70, 340)
        out.append(f'<path d="{blob(fx, wl + rnd.uniform(4, 12), rnd.uniform(6, 14), rnd.uniform(2, 4), k, 0.3, 10)}" fill="#F2E6E0" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(gilt(D, 300, 104, "MAUI’S FISHHOOK", BEBAS, 66, ls=4, max_w=440, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 134, "POLYNESIAN · FISHER OF ISLANDS", CINZEL, 17, "#E8E4FF", ls=2.5, max_w=440))
    out.append(f'<rect x="0" y="512" width="600" height="88" fill="{D.lin([(0, "#05081A", 0), (0.5, "#05081A", 0.45), (1, "#05081A", 0.7)])}"/>')
    out.append(tx(300, 550, "Its hook still hangs among the stars", SERIF_IT, 27, "#FFF0DC", max_w=440))
    return fin(D, out, 14, op=0.4)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _frame(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1.0
    return (dx / d, dy / d), (-dy / d, dx / d), d


def hand_pts(w, e, k=1.0, side=1):
    """A hand as a mitten with a thumb: wrist w toward fingertips e (head units)."""
    u, n, d = _frame(w, e)
    n = (n[0] * side, n[1] * side)

    def P(a, b):
        return (w[0] + u[0] * a + n[0] * b, w[1] + u[1] * a + n[1] * b)
    return [P(0, 0.12), P(0.3, 0.15), P(0.58, 0.12), P(0.7, 0.05), P(0.72, -0.04), P(0.6, -0.1), P(0.42, -0.12), P(0.4, -0.2),
            P(0.3, -0.24), P(0.18, -0.16), P(0, -0.12)]


def foot_pts(a, t, sole=None):
    """A foot in profile from the ankle a toward the toe t (head units): heel, arch, instep, toes."""
    u, n, d = _frame(a, t)
    if n[1] < 0:
        n = (-n[0], -n[1])         # n points down, toward the sole

    def P(x, y):
        return (a[0] + u[0] * x * d + n[0] * y, a[1] + u[1] * x * d + n[1] * y)
    return [P(-0.24, 0.08), P(-0.2, -0.12), P(0.0, -0.16), P(0.18, -0.12), P(0.5, -0.05), P(0.86, 0.04), P(1.0, 0.12), P(0.96, 0.2),
            P(0.6, 0.2), P(0.25, 0.16), P(-0.1, 0.22), P(-0.22, 0.2)]


def cumulus(D, cx, cy, w, seed, pal=("#FFF2E0", "#E8A8A0", "#6A4A6A"), L=(0, -1), op=1.0, rows=3, flat=0.3):
    """A painted cumulus: puffs with definite (but soft) edges built from a body wash, a shadowed underside,
    lit caps facing the light with a bright dry-brush rim, and wisps."""
    rnd = random.Random(seed)
    lx, ly = unit(*L)
    puffs = []
    for r_ in range(rows):
        n = 7 - r_ * 2
        for i in range(n):
            t = (i + 0.5) / n
            px = cx + (t - 0.5) * w * (1 - r_ * 0.28) + rnd.uniform(-w, w) * 0.03
            rr = w * (0.1 + 0.08 * math.sin(math.pi * t)) * rnd.uniform(0.85, 1.2) * (1 - r_ * 0.08)
            py = cy - r_ * w * 0.11 - rr * 0.5 + rnd.uniform(-3, 3)
            puffs.append((px, py, rr))
    shapes = [blob(px, py, rr, rr * 0.86, rnd.randint(0, 9999), 0.08, 14) for px, py, rr in puffs]
    base = smooth_closed([(cx - w * 0.52, cy), (cx - w * 0.3, cy + w * flat * 0.1), (cx + w * 0.3, cy + w * flat * 0.1), (cx + w * 0.52, cy),
                          (cx + w * 0.3, cy - w * 0.08), (cx - w * 0.3, cy - w * 0.08)])
    allp = " ".join(shapes) + " " + base
    out = [f'<g opacity="{op}">', f'<path d="{allp}" fill="{pal[1]}"/>']
    cid = D.clip(f'<path d="{allp}"/>')
    inner = [f'<rect x="{cx - w}" y="{cy - w}" width="{2 * w}" height="{w * 1.3}" fill="{dir_grad(D, [(0, pal[0], 0.7), (0.5, pal[1], 0), (1, pal[2], 0.8)], L)}"/>']
    for (px, py, rr) in puffs:
        inner.append(f'<path d="{blob(px + lx * rr * 0.25, py + ly * rr * 0.25, rr * 0.8, rr * 0.62, rnd.randint(0, 9999), 0.12, 12)}" fill="{pal[0]}" opacity="0.45"/>')
        inner.append(f'<path d="{blob(px - lx * rr * 0.45, py - ly * rr * 0.45 + rr * 0.3, rr * 0.9, rr * 0.45, rnd.randint(0, 9999), 0.12, 12)}" fill="{pal[2]}" opacity="0.3"/>')
    inner.append(f'<rect x="{cx - w}" y="{cy - w * 0.08}" width="{2 * w}" height="{w * 0.3}" fill="{pal[2]}" opacity="0.35"/>')
    inner.append(flow_strokes(D, allp, (cx - w * 0.6, cy - w * 0.5, cx + w * 0.6, cy + w * 0.1), -5, [pal[0], pal[1], pal[2]], seed, w * 1.2, (8, 26), (1.5, 4), (0.1, 0.3), clip=False))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(rim_mask(D, [allp], L, max(1.5, w * 0.012), mix(pal[0], "#FFFFFF", 0.4), 0.8))
    out.append("</g>")
    return "".join(out)


def stratus(D, y, x0, x1, th, pal, seed, n=30, lit_below=True, op=1.0):
    """A band of long, thin dawn/dusk clouds: overlapping tapered horizontal streaks, a darker body and a bright
    edge on the side facing the low sun."""
    rnd = random.Random(seed)
    out = [f'<g opacity="{op}">']
    for i in range(n):
        cx = rnd.uniform(x0, x1)
        L_ = rnd.uniform(40, 160)
        yy = y + rnd.gauss(0, th * 0.4)
        w = rnd.uniform(th * 0.25, th * 0.7)
        sag = rnd.uniform(-2, 2)
        pts = [(cx - L_ / 2, yy), (cx - L_ * 0.2, yy - w * 0.1 + sag), (cx + L_ * 0.2, yy + sag), (cx + L_ / 2, yy + rnd.uniform(-1, 1))]
        out.append(taper(catmull(pts, 4), w, 0.5, pal[1], rnd.uniform(0.5, 0.9)))
        e = 1 if lit_below else -1
        out.append(taper(catmull([(px, py + e * w * 0.32) for px, py in pts], 4), w * 0.35, 0.3, pal[0], rnd.uniform(0.5, 0.95)))
        out.append(taper(catmull([(px, py - e * w * 0.3) for px, py in pts], 4), w * 0.4, 0.3, pal[2], rnd.uniform(0.25, 0.5)))
    out.append("</g>")
    return "".join(out)


def mountain_isle(D, pts, seed, L=(-1, -0.3), pal=("#C8B880", "#2E4A3A", "#08140E"), rim="#FFC890", ridges=7, src=None):
    """A rugged volcanic island: the mass graded from the lit flank to the shadow side, ridges running down from
    the summits (lit on one side, dark on the other), forest dabs, cascades pouring down to a foaming shore."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = bbox(pts)
    d = smooth_closed(pts)
    out = [model(D, pts, pal, seed, L, flow=-80, sop=(0.12, 0.4), n=int((x1 - x0) * (y1 - y0) / 60), edge="#000000",
                 cols=[pal[0], pal[1], pal[2], mix(pal[0], pal[1], 0.5)], core=1.2)]
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    tops = sorted(pts[:-2], key=lambda p: p[1])[:4]
    for i in range(ridges):
        tx_, ty_ = rnd.choice(tops)
        tx_ += rnd.uniform(-20, 20)
        ty_ += rnd.uniform(0, 30)
        dx = rnd.uniform(-1, 1)
        rp = [(tx_, ty_)]
        for j in range(5):
            rp.append((rp[-1][0] + dx * 18 + rnd.uniform(-8, 8), rp[-1][1] + rnd.uniform(16, 26)))
        lit_side = 1 if L[0] < 0 else -1
        inner.append(taper([(px - lit_side * 3, py) for px, py in rp], rnd.uniform(5, 9), 1, pal[0], 0.35))
        inner.append(taper([(px + lit_side * 4, py) for px, py in rp], rnd.uniform(6, 11), 1, pal[2], 0.45))
    for k in range(int((x1 - x0) * (y1 - y0) / 160)):
        px, py = rnd.uniform(x0, x1), rnd.uniform(y0 + (y1 - y0) * 0.25, y1)
        inner.append(f'<path d="{blob(px, py, rnd.uniform(3, 7), rnd.uniform(2, 4.5), k, 0.25, 8)}" fill="{rnd.choice([pal[1], pal[2], mix(pal[0], pal[1], 0.4)])}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    for k in range(10):
        wx = rnd.uniform(x0 + 20, x1 - 10)
        wy = rnd.uniform(y0 + (y1 - y0) * 0.3, y0 + (y1 - y0) * 0.6)
        inner.append(taper(catmull([(wx, wy), (wx + rnd.uniform(-4, 4), (wy + y1) / 2), (wx + rnd.uniform(-6, 6), y1 + 4)], 6),
                           rnd.uniform(0.8, 1.6), rnd.uniform(2.5, 5), "#F2F6FF", rnd.uniform(0.3, 0.6)))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(rim_mask(D, [d], L, 3.0, rim, 0.85, src))
    return "".join(out)


def siren_bird(D, x, y, s, seed, flip=False, pal=("#7A5A4A", "#2A1A16", "#080404"), rim="#FFD49A", wings="folded", L=(-1, -0.3),
               hair=("#5A3A24", "#1E120A", "#050302")):
    """A Siren as the Greeks painted her: the body of a great bird of prey perched on a rock, with a woman's head
    and long hair. (x, y) = where the talons grip, s = size (about the bird's height). wings 'folded' or 'raised'."""
    rnd = random.Random(seed)

    def M(pts):
        return T(pts, x, y, s, flip)
    Lw = (-L[0], L[1]) if flip else L
    B = Beast(D, pal, seed, Lw, rim=rim, rim_d=max(1.4, s * 0.02), edge="#000000", edge_d=1.2, edge_op=0.5, fur_n=1.2, fur_len=(s * 0.03, s * 0.08),
              fur_w=(0.6, 1.4), shade=0.4, lit=0.25)
    # tail feathers falling behind the perch
    B.mass(M([(-0.18, -0.32), (-0.42, -0.1), (-0.62, 0.22), (-0.5, 0.26), (-0.3, 0.08), (-0.08, -0.12)]), flow=120, fur=0.6)
    # the body: breast forward, back sloping to the tail
    body = [(0.12, -0.92), (0.3, -0.8), (0.36, -0.58), (0.3, -0.34), (0.16, -0.18), (-0.06, -0.12), (-0.3, -0.2), (-0.4, -0.38), (-0.3, -0.62), (-0.1, -0.84)]
    B.mass(M(body), flow=100, fur=1.0)
    # legs and talons
    for dx in (-0.02, 0.1):
        B.limb(M([(dx, -0.22), (dx + 0.02, -0.06), (dx + 0.03, 0.0)]), [s * 0.07, s * 0.045, s * 0.035], fur=0.3)
    # wing
    if wings == "raised":
        wg = [(-0.05, -0.8), (-0.3, -1.15), (-0.6, -1.5), (-0.95, -1.62), (-0.82, -1.38), (-1.0, -1.32), (-0.78, -1.12), (-0.92, -1.0), (-0.66, -0.88),
              (-0.7, -0.74), (-0.4, -0.62), (-0.2, -0.6)]
    else:
        wg = [(0.12, -0.78), (0.05, -0.86), (-0.22, -0.74), (-0.42, -0.5), (-0.62, -0.1), (-0.5, -0.06), (-0.32, -0.26), (-0.1, -0.36), (0.12, -0.5)]
    B.mass(M(wg), flow=lambda X, Y: 130 if not flip else 50, fur=1.2, pal=(mix(pal[0], "#FFFFFF", 0.05), pal[1], pal[2]))
    feathers = []
    for k in range(4):
        t = k / 3
        if wings == "raised":
            a, b = M([(-0.22 - t * 0.5, -0.7 - t * 0.5), (-0.5 - t * 0.5, -0.9 - t * 0.55)])
        else:
            a, b = M([(0.0 - t * 0.12, -0.6 + t * 0.06), (-0.42 - t * 0.12, -0.22 + t * 0.06)])
        feathers.append(taper([a, b], s * 0.025, s * 0.006, pal[2], 0.55))
        feathers.append(taper([(a[0], a[1] - s * 0.012), (b[0], b[1] - s * 0.012)], s * 0.012, s * 0.004, pal[0], 0.4))
    B.overlay("".join(feathers))
    # the woman's neck and head in profile, hair down her back
    B.limb(M([(0.18, -0.85), (0.22, -0.98)]), [s * 0.13, s * 0.1], fur=0.2)
    hd = [(0.12, -1.18), (0.2, -1.24), (0.3, -1.2), (0.34, -1.12), (0.37, -1.07), (0.34, -1.05), (0.35, -1.01), (0.32, -0.98), (0.26, -0.96), (0.2, -1.0), (0.12, -1.04)]
    B.mass(M(hd), flow=-90, fur=0.1, shade=0.35)
    hr = [(0.12, -1.06), (0.08, -1.18), (0.18, -1.27), (0.3, -1.24), (0.28, -1.18), (0.18, -1.14), (0.12, -1.0), (0.04, -0.8), (-0.06, -0.7), (-0.04, -0.86)]
    B.mass(M(hr), flow=110, fur=1.0, pal=hair)
    return B.render()


def galley_g(D, x0, x1, wl, seed, pal=("#6A4A3A", "#22140E", "#060302"), rim="#FFD49A", L=(-1, -0.3), oars=12):
    """A Greek galley in profile (bow to the right): long low black hull, the bronze ram at the waterline, a painted
    eye on the bow, the stern sweeping up and over, oars dipping in a row, a mast with its yard and furled sail."""
    rnd = random.Random(seed)
    Lh = x1 - x0
    hull = [(x0 - 8, wl - 40), (x0 + 10, wl - 26), (x0 + Lh * 0.2, wl - 18), (x0 + Lh * 0.6, wl - 17), (x1 - 30, wl - 22), (x1 - 10, wl - 34),
            (x1 + 4, wl - 40), (x1 + 2, wl - 30), (x1 - 6, wl - 12), (x1 + 22, wl - 2), (x1 - 4, wl + 6), (x0 + Lh * 0.5, wl + 8), (x0 + 16, wl + 2),
            (x0 - 2, wl - 10), (x0 - 18, wl - 30)]
    out = []
    # oars below the gunwale, dipping in
    for i in range(oars):
        ox = x0 + 30 + i * (Lh - 70) / max(1, oars - 1)
        a = math.radians(118 + 6 * math.sin(i * 1.3))
        out.append(f'<path d="M {ox:.1f} {wl - 16:.1f} L {ox + math.cos(a) * 40:.1f} {wl - 16 + math.sin(a) * 40:.1f}" stroke="{pal[2]}" stroke-width="2.2"/>')
        out.append(f'<path d="{blob(ox + math.cos(a) * 40, wl - 14 + math.sin(a) * 40, 5, 1.6, i, 0.2, 8)}" fill="#F2E6E0" opacity="0.6"/>')
    out.append(model(D, hull, pal, seed, L, flow=0, sop=(0.15, 0.4), edge="#000000", rim=rim, rim_w=2.4, hi=0.3))
    # the stern ornament curling back over the steersman
    st = catmull([(x0 - 14, wl - 34), (x0 - 26, wl - 60), (x0 - 18, wl - 84), (x0 - 2, wl - 88), (x0 + 4, wl - 76)], 6)
    out.append(taper(st, 9, 3, pal[2]))
    out.append(taper([(px + 2, py - 1) for px, py in st], 2, 1, rim, 0.7))
    # the eye on the bow, red band along the wale, the ram
    ex, ey = x1 - 16, wl - 24
    out.append(f'<path d="{blob(ex, ey, 6, 3.4, seed, 0.05, 10)}" fill="#F2E8D8"/><circle cx="{ex + 1:.1f}" cy="{ey:.1f}" r="2.2" fill="#140A06"/>')
    out.append(taper(catmull([(x0, wl - 20), (x0 + Lh * 0.5, wl - 13), (x1 - 20, wl - 18)], 6), 2.6, 2.6, "#A8301E", 0.8))
    out.append(model(D, [(x1 - 4, wl - 4), (x1 + 26, wl - 1), (x1 - 2, wl + 4)], ("#F2C878", "#A8742A", "#3A2008"), seed + 1, L, hi=0.5))
    # rowers' heads along the gunwale
    for i in range(oars // 2):
        rx = x0 + 40 + i * (Lh - 90) / max(1, oars // 2 - 1)
        out.append(f'<path d="{blob(rx, wl - 26, 4.2, 5, seed + i, 0.1, 10)}" fill="{pal[2]}"/>')
        out.append(f'<path d="{blob(rx - 1, wl - 31, 3.4, 3.6, seed + i + 50, 0.1, 10)}" fill="{pal[2]}"/>')
    return "".join(out)


# ================================================================ G6. the sirens: Odysseus bound to the mast
@gallery("the-sirens", seed=31, edge=2.6, bristle=0.5, grain=0.2)
def the_sirens_g():
    D = Doc2("myg-sr")
    rnd = random.Random(13)
    sx, sy = 236, 352
    out = [sky(D, [(0, "#2A2050"), (0.3, "#6A3A6A"), (0.5, "#C86A6A"), (0.6, "#F2A868"), (0.62, "#FFD890")], 3, 360, ["#4A3060", "#C8706A", "#FFB070"], 70, sop=(0.06, 0.16))]
    out.append(soft_glow(D, sx, sy, 280, "#FFD890", 0.7))
    out.append(f'<path d="{blob(sx, sy + 6, 26, 26, 3, 0.02, 20)}" fill="{D.rad([(0, "#FFFDF0"), (0.7, "#FFE6A0"), (1, "#FFC870")])}"/>')
    out.append(stratus(D, 270, -40, 640, 14, ("#FFE6B0", "#B85A6A", "#4A2A5A"), 3, 32))
    out.append(stratus(D, 316, -40, 640, 9, ("#FFF0C8", "#E8907A", "#7A4A6A"), 4, 24))
    out.append(stratus(D, 220, -40, 640, 12, ("#F2A0A0", "#6A3A6A", "#2A1A44"), 5, 16, op=0.7))
    out.append(sea_g(D, 356, 600, [(0, "#E8A07A"), (0.12, "#8A5A6A"), (0.5, "#3A2A4A"), (1, "#120E22")], 4, sun_x=sx, swell=15))
    # the Sirens' rock, with the bones of sailors who listened
    rock = [(400, 470), (420, 420), (440, 380), (452, 330), (478, 300), (500, 268), (528, 250), (560, 262), (600, 284), (640, 300), (640, 480)]
    out.append(cliff(D, rock, ("#7A5A5A", "#2E1E24", "#0A0608"), 7, L=(-1, -0.3), lit="#FFC890", faces=18, strata=10, op_lit=0.9, src=(sx, sy, 460)))
    for k in range(8):
        bx, by = rnd.uniform(430, 600), rnd.uniform(380, 450)
        out.append(taper([(bx, by), (bx + rnd.uniform(8, 14), by + rnd.uniform(-3, 3))], 2.6, 2.2, "#E8DCC8", 0.75))
    for k in range(30):
        fx = rnd.uniform(390, 640)
        out.append(f'<path d="{blob(fx, 470 + rnd.uniform(-4, 8), rnd.uniform(8, 18), rnd.uniform(2, 4), k, 0.3, 10)}" fill="#F6E6E0" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(siren_bird(D, 470, 334, 96, 3, flip=True, wings="folded"))
    out.append(siren_bird(D, 530, 256, 104, 4, flip=True, wings="raised"))
    out.append(siren_bird(D, 584, 290, 90, 5, flip=True, wings="folded"))
    # their song drifting over the water
    for i in range(3):
        pts = [(450 - i * 6, 300 + i * 18), (390, 280 + i * 22), (330, 300 + i * 16), (280, 296 + i * 20)]
        out.append(f'<path d="{smooth_open(pts)}" stroke="#FFF0D0" stroke-width="1.4" fill="none" opacity="0.35" stroke-dasharray="1 6" stroke-linecap="round"/>')
    # the galley, Odysseus lashed to the mast
    wl = 468
    mx = 214
    out.append(f'<path d="M {mx} {wl - 22} L {mx + 2} {wl - 230}" stroke="#140A06" stroke-width="6"/>')
    out.append(f'<path d="M {mx + 3} {wl - 22} L {mx + 5} {wl - 228}" stroke="#FFD49A" stroke-width="1.6" opacity="0.6"/>')
    out.append(taper(catmull([(mx - 90, wl - 214), (mx, wl - 222), (mx + 90, wl - 214)], 6), 5, 5, "#140A06"))
    out.append(model(D, [(mx - 84, wl - 216), (mx, wl - 224), (mx + 84, wl - 216), (mx + 70, wl - 204), (mx, wl - 208), (mx - 70, wl - 204)],
                     ("#F2E0C0", "#B89A7A", "#4A3A30"), 6, (-1, -0.3), flow=0, edge="#000000", hi=0.4))
    for k in (-60, -20, 20, 60):
        out.append(f'<path d="M {mx + k} {wl - 210} L {mx + k * 1.2} {wl - 26}" stroke="#140A06" stroke-width="1" opacity="0.6"/>')
    # Odysseus straining at the ropes toward the song
    J = pose("side", head=(0.55, -7.3), neck=(0.35, -6.65), sR=(0.25, -6.18), sL=(0.15, -6.18), hR=(0.05, -3.95), hL=(0.0, -3.95),
             eR=(-0.25, -5.0), wR=(-0.35, -4.0), eL=(-0.3, -5.1), wL=(-0.4, -4.2), kR=(0.45, -2.1), aR=(0.5, -0.2), tR=(1.2, -0.1),
             kL=(-0.2, -2.05), aL=(-0.35, -0.2), tL=(0.35, -0.1))
    B, M_ = human(D, mx + 14, wl - 22, 122, J, ("#5A3A2C", "#1E120C", "#050302"), 9, L=(-1, -0.3), rim="#FFD49A", rim_d=2, fur_n=0.2)
    drape(B, M_, [(-0.45, -6.2), (0.55, -6.1), (0.6, -4.8), (0.62, -3.3), (0.0, -2.9), (-0.55, -3.0), (-0.5, -4.6)], flow=-90,
          pal=("#6A4A3A", "#24160E", "#060302"), shade=0.4)
    hc = J["head"]
    B.mass(M_([(hc[0] - 0.42, hc[1] + 0.1), (hc[0] - 0.36, hc[1] - 0.46), (hc[0], hc[1] - 0.58), (hc[0] + 0.3, hc[1] - 0.44), (hc[0], hc[1] - 0.2),
               (hc[0] - 0.16, hc[1] + 0.3)]), flow=180, fur=0.6, shade=0.3)
    B.mass(M_([(hc[0] + 0.1, hc[1] + 0.2), (hc[0] + 0.44, hc[1] + 0.22), (hc[0] + 0.36, hc[1] + 0.66), (hc[0] + 0.1, hc[1] + 0.72), (hc[0] - 0.04, hc[1] + 0.4)]),
           flow=90, fur=0.5)
    out.append(B.render())
    for yy in (-5.6, -4.6, -3.4):
        a_, b_ = M_([(-0.65, yy), (0.65, yy + 0.25)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#E8C890" stroke-width="2" opacity="0.85"/>')
    out.append(galley_g(D, 70, 380, wl, 5))
    out.append(sea_g(D, 474, 600, [(0, "#3A2A4A"), (1, "#120E22")], 6, sun_x=sx, swell=10, n=60))
    out.append(gilt(D, 300, 100, "The Sirens", DMS, 66, ls=1, max_w=420, seed=13, deboss="#000000", dop=0.8))
    out.append(tx(300, 132, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#F2E4F2", ls=2.5, max_w=440))
    out.append(f'<rect x="0" y="508" width="600" height="92" fill="{D.lin([(0, "#0A0816", 0), (0.5, "#0A0816", 0.45), (1, "#0A0816", 0.7)])}"/>')
    out.append(tx(300, 550, "“Bind me fast to the mast.”", SERIF_IT, 30, "#FFF0DC", max_w=440))
    return fin(D, out, 14, op=0.4)



# =====================================================================================================================
# GALLERY EDITION II: the plates painted with paint_mythology_kit (hand-drawn contours, soft modelling inside each
# silhouette, rim light, blurred atmosphere, a brush finish over the art while the lettering stays crisp).
# A slug registered with @plate replaces any earlier version of that slug.
# =====================================================================================================================
import paint_mythology_kit as K
from paint_mythology_kit import Plate, sp, lp, place, ellipse, ribbon, form, clip_to, soft, soft_line, rim, glow, screen


def plate(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        PF.pop(slug, None)
        return fn
    return deco


# ================================================================ athena's owl — the little owl on the olive, Acropolis by moonlight
def olive_bough(P, axis, ws, seed, L=(-0.7, -0.7), bark=("#A8A294", "#4E483E", "#141210"), rim_col="#DDE8FF"):
    """A gnarled olive limb: twisted, knotted, fissured grey bark, lit along the top."""
    rnd = random.Random(seed)
    pts = ribbon(K.catmull(axis, 6), _interp_ws(axis, ws, 6))
    d = sp(pts)
    x0, y0, x1, y1 = K.bbox(pts)
    fis = []
    ax = K.catmull(axis, 6)
    for k in range(5):
        off = rnd.uniform(-0.3, 0.3)
        line = []
        for i, (x, y) in enumerate(ax):
            a, b = ax[max(i - 1, 0)], ax[min(i + 1, len(ax) - 1)]
            tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
            line.append((x - ty_ * off * 14 + rnd.uniform(-1.2, 1.2), y + tx_ * off * 14 + rnd.uniform(-1.2, 1.2)))
        fis.append(K.stroke_line(line, bark[2], rnd.uniform(1.2, 2.4), rnd.uniform(0.35, 0.6)))
        fis.append(K.stroke_line([(x + 1.2, y - 1.4) for x, y in line], bark[0], 0.9, 0.35))
    knots = []
    for k in range(4):
        i = rnd.randrange(3, len(ax) - 3)
        x, y = ax[i]
        knots.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(4, 7):.1f}" ry="{rnd.uniform(2.5, 4):.1f}" fill="{bark[2]}" opacity="0.55"/>')
        knots.append(f'<ellipse cx="{x - 1:.1f}" cy="{y - 1.5:.1f}" rx="{rnd.uniform(3, 5):.1f}" ry="1.4" fill="{bark[0]}" opacity="0.4"/>')
    return form(P, d, bark, L, (x0, y0, x1, y1), core=0.6, lit=0.5, edge="#000000", edge_op=0.5, rim_col=rim_col, rim_d=1.8, rim_op=0.8,
                extra=fis + knots)


def _interp_ws(axis, ws, n):
    out = []
    for i in range(len(axis) - 1):
        for k in range(n):
            out.append(ws[i] + (ws[i + 1] - ws[i]) * k / n)
    out.append(ws[-1])
    return out


def olive_leaf(P, x, y, L_, ang, seed, top=True, pal=None, op=1.0):
    """A narrow lanceolate olive leaf: dark grey-green above, silvery beneath, a pale midrib."""
    pal = pal or (("#9AAA88", "#56684A", "#1E2A1A") if top else ("#DCE4D8", "#A8B4A8", "#5A665A"))
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    W = L_ * 0.13
    loc = [(0, 0, 1), (L_ * 0.2, -W * 0.9), (L_ * 0.55, -W), (L_ * 0.85, -W * 0.55), (L_, 0, 1), (L_ * 0.85, W * 0.5), (L_ * 0.55, W * 0.95), (L_ * 0.2, W * 0.8)]
    pts = [(x + px * c - py * s, y + px * s + py * c) + tuple(p[2:]) for p in loc for px, py in [p[:2]]]
    d = sp(pts)
    out = [K.path(d, pal[1], op)]
    out.append(K.path(d, K.dir_grad(P, [(0, pal[0], 0.7), (0.5, pal[1], 0), (1, pal[2], 0.6)], (-0.7, -0.7)), op))
    out.append(f'<path d="M {x + c * L_ * 0.05:.1f} {y + s * L_ * 0.05:.1f} L {x + c * L_ * 0.9:.1f} {y + s * L_ * 0.9:.1f}" stroke="{pal[0]}" stroke-width="0.8" opacity="{0.6 * op:.2f}"/>')
    return "".join(out)


def olive_spray(P, seed, stem, n_leaves, L_=(18, 30), olives=0, side_bias=0, op=1.0):
    """A twig with leaves in opposite pairs along it, some showing their silver undersides, a few black olives."""
    rnd = random.Random(seed)
    out = [K.taper(stem, 3.2, 1.0, "#3A3228", op)]
    ax = K.resample(stem, 6)
    for i in range(1, len(ax)):
        if rnd.random() > n_leaves / len(ax):
            continue
        x, y = ax[i]
        a, b = ax[i - 1], ax[min(i + 1, len(ax) - 1)]
        base_ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        for sg in (-1, 1):
            out.append(olive_leaf(P, x, y, rnd.uniform(*L_), base_ang + sg * rnd.uniform(28, 55) + side_bias, seed + i * 3 + sg, top=rnd.random() < 0.62, op=op))
    rnd2 = random.Random(seed + 99)
    for k in range(olives):
        x, y = ax[rnd2.randrange(1, len(ax))]
        ox, oy = x + rnd2.uniform(-6, 6), y + rnd2.uniform(4, 9)
        out.append(f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="4.2" ry="5.4" fill="#1A1424" opacity="{op}"/>')
        out.append(f'<ellipse cx="{ox - 1.4:.1f}" cy="{oy - 2:.1f}" rx="1.4" ry="1.8" fill="#B8C0E8" opacity="{0.7 * op:.2f}"/>')
    return "".join(out)


def little_owl_g(P, ox, oy, s, seed, L=(-0.75, -0.65), turn=7):
    """Athene noctua, painted: flat broad head, pale brows drawn down in a stern V, lemon eyes under heavy lids,
    white moustache and collar, chocolate upperparts spotted white, a cream breast with broken brown streaks,
    feathered legs, grey claws. (ox, oy) = where the feet grip; the bird is about 236 * s tall."""
    rnd = random.Random(seed)
    lx, ly = K.unit(*L)

    def Q(pts):
        return place(pts, ox, oy, s)

    def Q1(x, y):
        return place([(x, y)], ox, oy, s)[0]
    out = []
    fluff = P.rough(3.2 * s, 0.11, seed)
    # short tail, behind
    tail = Q([(-18, -12), (18, -12), (16, 18), (4, 24, 0.5), (-4, 24, 0.5), (-16, 18)])
    out.append(form(P, sp(tail), ("#8A6A50", "#4A3220", "#1A0E06"), L, K.bbox(tail), core=0.6, lit=0.2))
    sil_l = [(0, -236), (28, -235), (50, -228), (63, -212), (68, -192), (66, -172), (59, -158, 0.4), (66, -147), (74, -126), (78, -100),
             (77, -70), (69, -42), (57, -20), (42, -7), (26, -1), (0, 1), (-26, -1), (-42, -7), (-56, -19), (-67, -40), (-74, -68),
             (-76, -98), (-72, -124), (-64, -146), (-57, -157, 0.4), (-63, -171), (-65, -191), (-60, -211), (-47, -227), (-26, -234)]
    sil = Q(sil_l)
    d = sp(sil)
    box = K.bbox(sil)
    inside = K.inside_poly(sil_l)
    inner = []
    # big soft modelling of the whole bird first (the round volume of head and body)
    inner.append(soft(P, sp(Q(ellipse(40, -92, 50, 90, 20))), "#140804", 0.7, 14 * s))
    inner.append(soft(P, sp(Q(ellipse(30, -192, 40, 34, 20))), "#140804", 0.4, 10 * s))
    inner.append(soft(P, sp(Q(ellipse(-26, -214, 30, 16, 16))), "#FFF0DC", 0.35, 8 * s))
    # cream breast with broken brown streaks
    breast = [(0, -152), (30, -148), (44, -122), (47, -82), (41, -42), (27, -13), (0, -6), (-27, -13), (-41, -42), (-47, -82), (-44, -122), (-30, -148)]
    inner.append(f'<path d="{sp(Q(breast))}" fill="#E2CCA8" {P.rough_blur(5 * s, 0.09, 1.6, seed + 3)}/>')
    inner.append(soft(P, sp(Q(ellipse(-12, -86, 30, 56, 16))), "#FFF8EA", 0.55, 8 * s))
    inner.append(soft(P, sp(Q(ellipse(30, -70, 26, 60, 16))), "#3A2414", 0.45, 10 * s))
    st = []
    ib = K.inside_poly(breast)
    for k in range(90):
        x, y = rnd.uniform(-44, 44), rnd.uniform(-140, -16)
        if not ib(x, y):
            continue
        L_ = rnd.uniform(6, 15)
        lean = x * 0.12
        a_ = Q1(x, y)
        b_ = Q1(x + lean * L_ / 10 + rnd.uniform(-1, 1), y + L_)
        m_ = Q1(x + lean * L_ / 20 + rnd.uniform(-1.5, 1.5), y + L_ / 2)
        w = rnd.uniform(2.6, 5.4) * s
        st.append(K.taper([a_, m_, b_], w * 0.4, w * 0.3, rnd.choice(["#5E3A1E", "#74502C", "#4A2C14", "#8A6038"]), rnd.uniform(0.55, 0.9), mid=w))
    inner.append(f'<g {P.blur(0.45)}>{"".join(st)}</g>')
    inner.append(K.scallops(seed + 5, K.bbox(Q(breast)), 70, 90, ["#FFF6E6", "#C8AA80"], (2.2 * s, 4 * s), (0.25, 0.55), (0.6, 1.1),
                            inside=K.inside_poly(Q(breast))))
    # folded wings over the flanks: chocolate, rows of white spots, barred primaries at the tip
    for sg in (-1, 1):
        wl = [(sg * 46, -150), (sg * 70, -134), (sg * 78, -100), (sg * 75, -62), (sg * 63, -30), (sg * 47, -6), (sg * 33, 6, 1),
              (sg * 38, -30), (sg * 43, -70), (sg * 45, -110), (sg * 41, -140)]
        wing = Q(wl)
        wd = sp(wing)
        spots = [K.scallops(seed + 10 + sg, K.bbox(wing), 50, 90, ["#C8A078", "#2A160A"], (2.4 * s, 4.2 * s), (0.3, 0.6), (0.7, 1.2), inside=K.inside_poly(wing))]
        for row in range(7):
            for j in range(3):
                if rnd.random() < 0.3:
                    continue
                x = sg * (49 + j * 8 + row * 1.0) + rnd.uniform(-3, 3)
                y = -136 + row * 13 + j * 5 + rnd.uniform(-3, 3)
                if abs(x) > 74 or not inside(x, y):
                    continue
                c = Q1(x, y)
                rr = rnd.uniform(1.4, 2.8) * s
                spots.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rr:.1f}" ry="{rr * rnd.uniform(0.6, 0.9):.1f}" fill="#F4E8D4" opacity="{rnd.uniform(0.45, 0.9):.2f}" transform="rotate({rnd.uniform(-30, 30):.0f} {c[0]:.1f} {c[1]:.1f})"/>')
        for k in range(5):
            a_, b_ = Q1(sg * (40 + k * 3), -42 + k * 8), Q1(sg * (60 - k * 2), -36 + k * 8)
            spots.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#E8D8C0" stroke-width="{2.0 * s:.1f}" opacity="0.5" stroke-linecap="round"/>')
        shade = 0.75 if sg > 0 else 0.35
        inner.append(form(P, wd, ("#B48A64", "#6A4428", "#24140A"), L, K.bbox(wing), core=shade, lit=0.4 if sg < 0 else 0.15, extra=spots,
                          edge="#140A04", edge_op=0.7))
    # head: crown finely spotted white, facial disc paler with radiating lines
    t = turn
    disc = [(t, -152), (t - 36, -157), (t - 54, -172), (t - 56, -194), (t - 45, -211), (t - 24, -217), (t, -211), (t + 22, -216), (t + 42, -210),
            (t + 52, -193), (t + 50, -172), (t + 34, -157)]
    inner.append(soft(P, sp(Q(disc)), "#B89A78", 0.8, 2.6 * s))
    inner.append(soft(P, sp(Q(ellipse(t + 30, -184, 22, 24, 14))), "#2A1808", 0.35, 6 * s))
    for k in range(80):
        x, y = rnd.uniform(-60, 62), rnd.uniform(-233, -200)
        if (x / 64) ** 2 + ((y + 192) / 44) ** 2 > 1 or not inside(x, y):
            continue
        c = Q1(x, y)
        inner.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rnd.uniform(0.9, 1.7) * s:.1f}" ry="{rnd.uniform(0.7, 1.2) * s:.1f}" fill="#F8EEDC" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
    for sg in (-1, 1):
        ex = t + sg * (22 if sg < 0 else 20)
        for k in range(11):
            a = math.radians(205 - k * 21) if sg < 0 else math.radians(-25 + k * 21)
            p0 = Q1(ex + math.cos(a) * 16, -184 + math.sin(a) * 16)
            p1 = Q1(ex + math.cos(a) * rnd.uniform(26, 32), -184 + math.sin(a) * rnd.uniform(24, 29))
            inner.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice(["#4A2C14", "#E8D8C0"])}" stroke-width="{0.9 * s:.1f}" opacity="0.45"/>')
    # the head's shadow falling on the upper breast
    inner.append(soft(P, sp(Q(ellipse(t + 8, -140, 46, 10, 16))), "#1A0C04", 0.45, 4 * s))
    # white throat collar and moustache
    inner.append(K.taper(Q([(t - 32, -151), (t - 15, -144), (t, -142), (t + 15, -144), (t + 30, -151)]), 5 * s, 5 * s, "#FBF4E6", 0.95, mid=11 * s))
    for sg in (-1, 1):
        inner.append(K.taper(Q([(t + sg * 4, -165), (t + sg * 15, -160), (t + sg * 28, -163)]), 5 * s, 1.5 * s, "#FFF8EC", 0.92))
    out.append(f'<g {fluff}>' + form(P, d, ("#B48A62", "#6E4A2C", "#2A180C"), L, box, core=0.7, lit=0.45, extra=inner,
                                     edge="#0A0602", edge_op=0.6, rim_col="#EEF4FF", rim_d=2.2 * s, rim_op=0.9,
                                     rim_src=(box[0], box[1] + 40 * s, 230 * s)) + "</g>")
    # eyes: lemon iris, black pupil, heavy lids that give the stern look, moonlight catchlight
    for sg in (-1, 1):
        ex = t + sg * (22 if sg < 0 else 20)
        cx_, cy_ = Q1(ex, -183)
        r = 12.5 * s * (1.0 if sg < 0 else 0.94)
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r + 2.0 * s:.1f}" fill="#120804"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r:.1f}" fill="{P.rad([(0, "#FFF6B0"), (0.5, "#F6D232"), (0.88, "#E39A12"), (1, "#7A4A06")])}"/>')
        out.append(f'<circle cx="{cx_ + 1.0 * s:.1f}" cy="{cy_ + 0.6 * s:.1f}" r="{6.6 * s:.1f}" fill="#040202"/>')
        # the lid: a feathered hood cutting the top of the eye, sloping down toward the bill
        inner_x = cx_ - sg * r
        lid = [(cx_ - r * 1.3, cy_ - r * 1.4), (cx_ + r * 1.3, cy_ - r * 1.4), (cx_ + r * 1.25, cy_ - r * (0.35 if sg < 0 else 0.62)),
               (cx_, cy_ - r * 0.5), (cx_ - r * 1.25, cy_ - r * (0.62 if sg < 0 else 0.35))]
        out.append(K.path(sp(lid), "#3A2412", 0.92))
        out.append(K.path(sp(lid), "#B89A78", 0.5))
        out.append(K.stroke_line([lid[4], lid[3], lid[2]], "#0A0402", 1.8 * s, 0.9))
        out.append(f'<ellipse cx="{cx_ - 4.2 * s:.1f}" cy="{cy_ - 2.8 * s:.1f}" rx="{2.4 * s:.1f}" ry="{1.8 * s:.1f}" fill="#FFFFFF" opacity="0.95"/>')
        out.append(f'<circle cx="{cx_ + 4 * s:.1f}" cy="{cy_ + 5 * s:.1f}" r="{1.0 * s:.1f}" fill="#FFFFFF" opacity="0.4"/>')
    # the pale brows, drawn down to the bill in a V
    for sg in (-1, 1):
        out.append(f'<g {fluff}>' + K.taper(Q([(t + sg * 3, -170), (t + sg * 10, -190), (t + sg * 22, -199), (t + sg * 38, -199), (t + sg * 52, -192)]),
                                            4 * s, 1.6 * s, "#FFF6E6", 0.95, mid=7 * s) + "</g>")
    # beak: small, hooked, horn-yellow
    bk = Q([(t - 5.5, -177), (t + 5.5, -177), (t + 4.5, -167), (t + 1, -158, 1), (t - 4.5, -167)])
    out.append(form(P, sp(bk), ("#F2EAC0", "#C0B078", "#5A4A28"), L, K.bbox(bk), core=0.55, lit=0.55, sd=1.4))
    # feathered legs and grey toes gripping the bough
    for sg in (-1, 1):
        leg = Q([(sg * 12, -12), (sg * 27, -12), (sg * 28, -2), (sg * 23, 4), (sg * 12, 3)])
        out.append(f'<g {fluff}>' + form(P, sp(leg), ("#E8DCC8", "#B8A488", "#5A4A36"), L, K.bbox(leg), core=0.6 if sg > 0 else 0.35, lit=0.2, sd=2) + "</g>")
        for k, (tx_, ty_) in enumerate(((sg * 6, 11), (sg * 18, 14), (sg * 31, 11))):
            a_, b_ = Q1(sg * 20, 2), Q1(tx_, ty_)
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} Q {b_[0]:.1f} {a_[1]:.1f} {b_[0]:.1f} {b_[1]:.1f}" stroke="#4A4442" stroke-width="{3.6 * s:.1f}" fill="none" stroke-linecap="round"/>')
            out.append(f'<path d="M {b_[0]:.1f} {b_[1]:.1f} q {sg * 0.5 * s:.1f} {3 * s:.1f} {sg * 2 * s:.1f} {5 * s:.1f}" stroke="#100C0C" stroke-width="{2.2 * s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def parthenon_g(P, cx, base, w, seed, lit="#F2EEE6", shade="#7A7894", L=(-0.8, -0.5)):
    """The Parthenon seen from the north-west, small and far: west front with 8 columns in light, the long north flank
    with its colonnade receding in shadow, the pediment, the broken roof line (it is a ruin), stylobate steps."""
    s = w / 120
    out = []
    # stylobate (steps), front face and receding side
    fx0, fx1 = cx - 46 * s, cx + 4 * s
    sx1 = cx + 74 * s
    h = 30 * s
    top = base - 6 * s
    out.append(K.path(lp([(fx0 - 3 * s, base), (fx1 + 2 * s, base), (sx1 + 3 * s, base - 4 * s), (sx1 + 3 * s, base - 8 * s), (fx1, top - 1 * s), (fx0 - 3 * s, top)]), shade))
    out.append(K.path(lp([(fx0 - 3 * s, top), (fx1, top - 1 * s), (fx1, base), (fx0 - 3 * s, base)]), lit, 0.85))
    # entablature + pediment on the front
    ent = top - h
    out.append(K.path(lp([(fx0 - 2 * s, ent), (fx1 + 1 * s, ent), (fx1 + 1 * s, ent - 6 * s), (fx0 - 2 * s, ent - 6 * s)]), lit))
    out.append(K.path(lp([(fx0 - 3 * s, ent - 6 * s), (fx1 + 2 * s, ent - 6 * s), ((fx0 + fx1) / 2, ent - 15 * s)]), mix(lit, shade, 0.15)))
    # side entablature receding, broken in the middle (the 1687 explosion)
    out.append(K.path(lp([(fx1 + 1 * s, ent), (cx + 22 * s, ent + 1 * s), (cx + 26 * s, ent - 4 * s), (fx1 + 1 * s, ent - 6 * s)]), shade))
    out.append(K.path(lp([(cx + 50 * s, ent + 2 * s), (sx1 + 1 * s, ent + 3 * s), (sx1 + 1 * s, ent - 2 * s), (cx + 52 * s, ent - 2 * s)]), shade))
    # columns: front 8 lit with a shade side; side colonnade darker, perspective-spaced
    for i in range(8):
        x = fx0 + (fx1 - fx0) * (i + 0.5) / 8
        cw = 4.4 * s
        out.append(f'<rect x="{x - cw / 2:.1f}" y="{ent:.1f}" width="{cw:.1f}" height="{top - ent:.1f}" fill="{lit}"/>')
        out.append(f'<rect x="{x + cw * 0.1:.1f}" y="{ent:.1f}" width="{cw * 0.4:.1f}" height="{top - ent:.1f}" fill="{shade}" opacity="0.55"/>')
    for i in range(13):
        if 6 <= i <= 8:
            continue
        t = i / 12
        x = fx1 + 4 * s + (sx1 - fx1 - 6 * s) * t
        cw = 3.2 * s
        yb = top - 1 * s - 3 * s * t
        out.append(f'<rect x="{x - cw / 2:.1f}" y="{ent + 1 * s * t:.1f}" width="{cw:.1f}" height="{yb - ent - 1 * s * t:.1f}" fill="{mix(lit, shade, 0.55)}"/>')
    # inner shadow between the columns (the cella wall)
    return f'<g>{"".join(out)}</g>'


def moon_disc(P, mx, my, r, seed, glow_col="#9AB4F0"):
    rnd = random.Random(seed)
    out = [glow(P, mx, my, r * 4.4, glow_col, 0.42), glow(P, mx, my, r * 2.1, "#E8F0FF", 0.45)]
    md = sp(ellipse(mx, my, r, r, 40))
    out.append(K.path(md, P.rad([(0, "#FFFFFF"), (0.65, "#F6F4EC"), (1, "#D6D4CC")], cx=0.42, cy=0.4, r=0.62)))
    # the maria as they really sit: Imbrium and Serenitatis upper left, Tranquillitatis right of centre, Procellarum west
    maria = [(-0.38, -0.3, 0.3, 0.22), (-0.02, -0.38, 0.2, 0.16), (0.22, -0.08, 0.2, 0.2), (-0.55, 0.1, 0.22, 0.35), (0.42, 0.2, 0.12, 0.12),
             (0.05, 0.25, 0.14, 0.1), (-0.15, 0.45, 0.1, 0.08)]
    sh = [f'<ellipse cx="{mx + x * r:.1f}" cy="{my + y * r:.1f}" rx="{a * r:.1f}" ry="{b * r:.1f}" fill="#8A8C9C" opacity="{rnd.uniform(0.22, 0.34):.2f}"/>' for x, y, a, b in maria]
    out.append(clip_to(P, md, f'<g {P.blur(r * 0.06)}>{"".join(sh)}</g>'))
    return "".join(out)


@plate("athenas-owl")
def athenas_owl_p():
    P = Plate("myp-ow")
    L = (-0.75, -0.62)
    art = [K.sky_grad(P, [(0, "#050A20"), (0.4, "#12224C"), (0.72, "#26386A"), (1, "#3A3E66")])]
    art.append(K.sky_wash(P, 3, ["#3A5A9A", "#1A2858", "#5A6AA0", "#0A1230"], 16, (-40, -40, 640, 480), (80, 180), (0.12, 0.28), 34))
    art.append(K.sky_strokes(P, 4, ["#5A70B0", "#0A1434", "#3A4C88"], 70, (-20, -20, 620, 420), op=(0.05, 0.14)))
    mx, my = 150, 168
    art.append(K.stars(5, (0, 0, 600, 360), 130, avoid=lambda x, y: math.hypot(x - mx, y - my) < 110))
    art.append(moon_disc(P, mx, my, 54, 3))
    # moonlit cloud streaks
    art.append(K.strata(P, 7, 252, -40, 520, 18, ("#D8E2FF", "#3E4E80", "#18204A"), L=(-0.9, -0.6), n=6, op=0.95))
    art.append(K.strata(P, 9, 112, 220, 640, 12, ("#C8D4F8", "#2E3C70", "#121A40"), L=(-1, 0.1), n=4, op=0.8))
    # the Acropolis: a flat-topped limestone rock with sheer sides, the Parthenon on top; Athens glittering below
    rock = [(-20, 600), (-20, 400), (14, 392), (40, 376), (52, 346), (62, 336), (230, 334), (246, 342), (258, 366), (282, 384), (330, 400), (420, 414), (620, 424), (620, 600)]
    art.append(form(P, sp(rock), ("#8A8AB0", "#3C3C62", "#14142E"), (-0.8, -0.5), K.bbox(rock), core=0.45, lit=0.35, sd=10))
    rnd = random.Random(4)
    cl = []
    for k in range(40):
        x = rnd.uniform(52, 262)
        y0 = 340 + rnd.uniform(0, 6)
        cl.append(K.bstroke(x, y0, 90 + rnd.uniform(-8, 8), rnd.uniform(10, 34), rnd.uniform(0.8, 2.2),
                            rnd.choice(["#B8B8D8", "#22224A", "#9090B8", "#4A4A74"]), rnd.uniform(0.25, 0.6)))
    art.append(clip_to(P, sp(rock), [f'<g {P.rough(2, 0.08, 4)}>{"".join(cl)}</g>']))
    art.append(glow(P, 150, 318, 80, "#F2F0FF", 0.16))
    art.append(parthenon_g(P, 152, 338, 112, 4))
    art.append(K.haze(P, 350, 470, "#22244A", 0, 0.55))
    lights = []
    for k in range(190):
        x, y = rnd.uniform(-10, 610), rnd.uniform(400, 600)
        if y < 404 + x * 0.04:
            continue
        lights.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2.0):.1f}" fill="{rnd.choice(["#FFD27A", "#FFE8B0", "#FFB050"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    art.append(f'<g {P.blur(1.6)}>{"".join(lights)}</g>' + "".join(lights[::3]))
    art.append(K.haze(P, 430, 600, "#B07A48", 0, 0.16))
    # out-of-focus olive leaves at the far left (depth of field)
    art.append(f'<g {P.blur(3.4)}>{olive_spray(P, 21, [(-20, 470), (30, 440), (70, 420), (110, 416)], 7, (38, 56), 0, op=0.95)}</g>')
    # the gnarled olive bough the owl stands on, coming in from the right
    axis = [(650, 446), (580, 430), (500, 422), (430, 422), (360, 426), (300, 440), (240, 462), (200, 480)]
    art.append(olive_bough(P, axis, [44, 40, 36, 32, 28, 23, 16, 10], 6))
    art.append(olive_spray(P, 31, [(250, 458), (218, 436), (190, 426), (160, 430)], 6, (24, 34), 2))
    art.append(olive_spray(P, 32, [(560, 428), (580, 398), (598, 378), (626, 368)], 6, (24, 36), 3))
    art.append(K.cast_shadow(P, 396, 412, 50, 5, "#000000", 0.55))
    art.append(glow(P, 470, 260, 160, "#000010", 0.35))
    art.append(little_owl_g(P, 394, 410, 1.3, 11, L))
    # moonlight falling across the owl from the left, the far side sinking into the night
    art.append(screen(glow(P, 300, 230, 150, "#8AA0D8", 0.22)))
    art.append(olive_spray(P, 33, [(470, 426), (452, 450), (430, 466)], 4, (24, 32), 2))
    art.append(K.vignette(P, "#02040E", 0.5, 0.55))
    art.append(K.text_scrim(P, 430, 600, "#03050F", 0.85))
    text = [gilt(P, 300, 504, "Athena’s Owl", SERIF_IT, 62, ls=0.5, max_w=420, seed=12, deboss="#000000", dop=0.85),
            tx(300, 534, "GREEK · WISDOM SEES IN THE DARK", CINZEL, 17, "#DCE4F8", ls=2.5, max_w=440)]
    return P.render(art, text, seed=41, edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ prometheus — the fire carried down from Olympus (plate)
def crag(P, pts, pal, seed, L=(-0.5, -0.8), lit=None, src=None, faces=18, strata=8, rough=(5, 0.05)):
    """A rock mass painted like Dore's crags: graded mass, tall faces alternately catching and losing the light,
    strata and cracks, a torn dry-brush edge and a lit lip along the edge facing the light."""
    rnd = random.Random(seed)
    light, base, dark = pal
    d = sp(pts)
    x0, y0, x1, y1 = K.bbox(pts)
    ins = K.inside_poly(pts)
    ex = []
    for _ in range(faces):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        if not ins(x, y):
            continue
        w = rnd.uniform(8, 30)
        h = rnd.uniform(20, 80)
        k = rnd.random()
        col = light if k < 0.4 else (dark if k > 0.7 else base)
        face = [(x, y), (x + w * 0.5, y - h * 0.1), (x + w, y + h * 0.15), (x + w * 0.85, y + h), (x + w * 0.1, y + h * 0.9)]
        ex.append(f'<path d="{lp(face)}" fill="{col}" opacity="{rnd.uniform(0.18, 0.4):.2f}" {P.blur(1.2)}/>')
    for _ in range(strata):
        y = rnd.uniform(y0, y1)
        xa = rnd.uniform(x0, x1)
        line = [(xa + i * 14, y + rnd.uniform(-3, 3) + i * rnd.uniform(-1, 1)) for i in range(rnd.randint(3, 8))]
        ex.append(K.stroke_line(line, dark, rnd.uniform(1, 2.2), rnd.uniform(0.3, 0.6)))
        ex.append(K.stroke_line([(x, y_ - 1.6) for x, y_ in line], light, 0.9, rnd.uniform(0.15, 0.35)))
    for _ in range(strata):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        line = [(x, y), (x + rnd.uniform(-4, 4), y + rnd.uniform(10, 20)), (x + rnd.uniform(-6, 6), y + rnd.uniform(24, 46))]
        ex.append(K.stroke_line(line, dark, rnd.uniform(1, 2), rnd.uniform(0.3, 0.55)))
    body = form(P, d, pal, L, (x0, y0, x1, y1), core=0.5, lit=0.35, extra=ex, edge="#000000", edge_op=0.4,
                rim_col=lit, rim_d=2.4, rim_op=0.95, rim_src=src)
    return f'<g {P.rough(rough[0], rough[1], seed)}>{body}</g>'


def prometheus_figure(P, ox, oy, s, torch, seed):
    """Prometheus striding down the mountain toward men, the fennel stalk with the stolen fire raised high in his
    right hand, the left hand open and reaching forward and down, the chlamys streaming back in the storm wind.
    Real anatomy (8 heads tall: 100 units a head), mostly in shadow, lit warm from the fire above and cool from the
    lightning behind. (ox, oy) = ground under the front foot; local units, y up negative."""
    def Q(pts):
        return place(pts, ox, oy, s)
    k = s / 0.3
    tx_, ty_ = torch
    skin = ("#FFC890", "#5A3222", "#0E0604")
    tunic = ("#F2D0A0", "#4A3A2C", "#0C0806")
    cloak = ("#FF9A60", "#7A1C12", "#1A0504")
    hair = ("#B07A4A", "#2A1810", "#060302")
    Lw = K.unit(tx_ - (ox + 20 * s), ty_ - (oy - 600 * s))
    B = K.Body(P, Lw)
    sl = lambda pts, col, w, op: K.stroke_line(Q(pts), col, w * k, op)

    def lb(axis, wl, wr, pal, core=0.5, lit=0.5, extra=(), sh=0.75):
        wl = [w * 1.12 for w in wl]
        wr = [w * 1.12 for w in wr]
        ex = [soft(P, sp(Q(K.limb_shade(axis, wl, wr, (Lw[0], Lw[1])))), pal[2], sh, 2.2 * k)] + list(extra)
        return B.add(Q(K.limb(axis, wl, wr)), pal, core=core * 0.5, lit=lit, extra=ex)
    # the cloak, behind everything, streaming right in the wind off the mountain
    ck = Q([(-44, -668), (0, -692), (70, -710), (150, -708), (232, -692), (300, -668), (356, -646, 1), (320, -620), (348, -588), (308, -560),
            (336, -518, 1), (278, -504), (238, -474), (196, -456), (156, -472), (120, -512), (92, -566), (66, -618)])
    B.add(ck, cloak, core=0.55, lit=0.5, extra=[sl([(0, -684), (120, -644), (250, -604)], cloak[0], 3.2, 0.4),
                                               sl([(30, -664), (130, -594), (230, -544)], cloak[2], 6, 0.5),
                                               sl([(70, -644), (160, -544), (210, -484)], cloak[2], 5, 0.5),
                                               sl([(20, -694), (160, -676), (300, -654)], cloak[0], 2.5, 0.45)])
    # far (right) leg: stretched behind and up the slope, heel lifted, pushing off
    lb([(26, -402), (50, -345), (74, -295), (98, -250), (106, -205), (114, -165), (126, -122)],
       [44, 44, 38, 25, 22, 19, 12], [50, 42, 34, 25, 34, 26, 13], skin, core=0.8, lit=0.25, sh=0.85)
    B.add(Q([(112, -134), (136, -130), (158, -110), (180, -94), (183, -86, 1), (150, -82), (122, -98), (108, -116)]), ("#C89A70", "#3A2616", "#0A0604"), core=0.6, lit=0.3)
    # far (right) arm raised: the stalk above the head
    lb([(58, -640), (64, -676), (70, -716), (72, -768), (66, -806), (56, -844), (42, -880)], [31, 27, 22, 17, 20, 17, 12],
       [31, 27, 23, 17, 19, 16, 12], skin, core=0.4, lit=0.75, extra=[sl([(60, -690), (70, -740)], skin[0], 3, 0.35)])
    B.add(Q([(22, -874), (38, -902), (60, -898), (68, -874), (58, -852), (34, -852)]), skin, core=0.35, lit=0.8)
    # torso in the exomis, leaning forward into the descent, belted, the hem fluttering back
    torso = Q([(-88, -640), (-48, -674), (4, -684), (60, -660), (88, -632), (78, -590), (66, -528), (50, -476), (58, -428), (90, -372), (112, -336, 1),
               (66, -346), (22, -338), (-22, -342), (-64, -352), (-100, -364, 1), (-80, -420), (-66, -472), (-74, -520), (-86, -566), (-98, -604)])
    B.add(torso, tunic, core=0.65, lit=0.6, extra=[
        sl([(-30, -470), (-22, -400), (-30, -350)], tunic[2], 4, 0.55), sl([(10, -468), (30, -400), (60, -352)], tunic[2], 4, 0.5),
        sl([(30, -470), (64, -420), (96, -352)], tunic[0], 2.5, 0.35), sl([(-60, -640), (-20, -560), (40, -480)], tunic[2], 3, 0.4),
        sl([(-70, -472), (-6, -478), (52, -474)], "#2A1408", 9, 0.9), sl([(-70, -476), (-6, -482), (52, -478)], "#C89A60", 1.5, 0.5),
        K.path(sp(Q([(-8, -682), (60, -660), (88, -632), (74, -592), (36, -598), (8, -628)])), skin[1], 0.95),
        soft(P, sp(Q([(10, -676), (60, -660), (84, -636), (50, -640)])), skin[0], 0.5, 3 * k)])
    # neck, head in profile looking down toward the plain of men, curling hair, a full beard
    B.add(Q([(-54, -702), (-14, -708), (-4, -668), (-50, -658)]), skin, core=0.6, lit=0.5)
    head = Q([(-26, -802), (-62, -792), (-84, -770), (-90, -752), (-98, -744), (-106, -731, 1), (-96, -725), (-97, -717), (-92, -709),
              (-90, -694), (-76, -676), (-54, -668), (-26, -686), (-10, -706), (8, -726), (16, -752), (8, -782)])
    B.add(head, skin, core=0.5, lit=0.7, extra=[soft(P, sp(Q(ellipse(-76, -752, 9, 6, 10))), "#000000", 0.55, 2 * k),
                                               sl([(-96, -722), (-84, -720)], "#1A0A04", 1.4, 0.6)])
    hairm = Q([(-30, -808), (-68, -798), (-88, -774), (-76, -770), (-60, -782), (-40, -774), (-24, -752), (-12, -728), (4, -712), (20, -726),
               (24, -758), (14, -790)])
    B.add(hairm, hair, core=0.5, lit=0.7, extra=[K.scallops(seed, K.bbox(hairm), 34, 0, [hair[0], hair[2]], (1.4 * k, 2.8 * k), (0.4, 0.7), (0.7, 1.1))])
    beard = Q([(-92, -708), (-97, -694), (-90, -676), (-76, -662), (-54, -660), (-34, -676), (-26, -700), (-44, -704), (-62, -712), (-78, -716)])
    B.add(beard, hair, core=0.5, lit=0.55, extra=[K.scallops(seed + 1, K.bbox(beard), 26, 90, [hair[0], hair[2]], (1.3 * k, 2.4 * k), (0.4, 0.7), (0.7, 1.1))])
    # near (left) leg: stepping down-forward, the weight coming onto it
    lb([(-30, -404), (-48, -350), (-66, -292), (-90, -222), (-104, -175), (-120, -110), (-140, -40)],
       [44, 46, 40, 26, 24, 20, 12], [52, 44, 36, 26, 36, 30, 13], skin, core=0.6, lit=0.5,
       extra=[soft(P, sp(Q(ellipse(-96, -224, 12, 14, 10))), skin[0], 0.45, 3 * k), sl([(-60, -330), (-84, -250)], skin[2], 3, 0.35),
                 sl([(-88, -200), (-110, -120)], skin[0], 2, 0.3)])
    B.add(Q([(-126, -46), (-150, -38), (-178, -22), (-202, -10), (-206, 0, 1), (-128, 0), (-116, -16)]), ("#C89A70", "#4A3424", "#0E0804"), core=0.5, lit=0.5)
    # near (left) arm reaching forward and down, the hand open over the plain
    lb([(-84, -628), (-100, -606), (-118, -584), (-146, -546), (-166, -522), (-188, -494), (-206, -470)],
       [32, 28, 24, 17, 20, 18, 12], [32, 30, 26, 18, 22, 17, 12], skin, core=0.5, lit=0.6)
    hand = Q([(-198, -482), (-216, -480), (-230, -466), (-246, -448), (-252, -438, 1), (-241, -440), (-234, -434), (-238, -420, 1), (-228, -424),
              (-222, -440), (-216, -430), (-212, -416, 1), (-204, -428), (-200, -446), (-194, -464)])
    B.add(hand, skin, core=0.4, lit=0.6)
    over = [soft(P, sp(Q(ellipse(60, -480, 110, 180, 16))), "#000000", 0.3, 30 * s),
            K.falloff(P, tx_, ty_, 330 * k, "#0A0306", 0.88, 0.22)]
    rims = [dict(L=Lw, col="#FFE0A0", d=2.6, op=1.0, src=(tx_, ty_, 420 * k)),
            dict(L=(1, -0.1), col="#C8D4FF", d=1.8, op=0.75, src=(ox + 320 * s, oy - 640 * s, 260 * k))]
    return B.render(rims=rims, edge_op=0.7, over=over)


@plate("prometheus")
def prometheus_p():
    P = Plate("myp-pr")
    rnd = random.Random(7)
    ox, oy, s = 330, 452, 0.3
    torch = (ox + 22 * s, oy - 1010 * s)
    art = [K.sky_grad(P, [(0, "#040309"), (0.3, "#0E0A1A"), (0.58, "#1E1226"), (0.8, "#341824"), (1, "#0E060A")])]
    art.append(K.sky_wash(P, 3, ["#2A1A40", "#4A2034", "#05040A", "#1E1234"], 16, (-40, -40, 640, 480), (90, 200), (0.15, 0.3), 36))
    # Olympus in the storm, far right, lightning splitting the cloud above it
    olym = [(250, 620), (300, 380), (360, 330), (420, 270), (470, 228), (500, 214), (540, 236), (600, 270), (640, 300), (640, 620)]
    art.append(form(P, sp(olym), ("#5A4466", "#2A1E3A", "#0E0A18"), (0.6, -0.8), K.bbox(olym), core=0.4, lit=0.3, sd=12))
    art.append(K.haze(P, 220, 420, "#2A1E3A", 0.2, 0.7))
    art.append(glow(P, 500, 150, 200, "#B8B0FF", 0.38))
    art.append(K.strata(P, 4, 150, -60, 660, 40, ("#7A6AA8", "#1E1630", "#06040A"), L=(0.4, 1), n=8, op=0.95, sd=3, rough_=(18, 0.02)))
    art.append(K.strata(P, 5, 70, -60, 660, 36, ("#3A2E58", "#0E0A18", "#020104"), L=(0.5, 1), n=7, op=0.95, sd=3, rough_=(18, 0.02)))
    bolt = [(520, 120), (508, 160), (522, 168), (496, 214), (506, 220), (478, 268)]
    art.append(screen(K.stroke_line(bolt, "#B8C0FF", 9, 0.5, smooth=False, extra=f' {P.blur(4)}')))
    art.append(K.stroke_line(bolt, "#F4F2FF", 2.4, 0.95, smooth=False))
    art.append(K.stroke_line([(506, 220), (530, 246), (526, 262)], "#F4F2FF", 1.2, 0.7, smooth=False))
    # the plain of men far below on the left: dark land, mist, and the first hearth fires with their smoke
    plain = K.ridge(8, -20, 380, 380, 352, 14, 10, 0.4, bottom=620)
    art.append(form(P, sp(plain), ("#4A2A3A", "#1E1222", "#08050C"), (0.6, -0.8), K.bbox(plain), core=0.3, lit=0.2, sd=10))
    art.append(K.haze(P, 350, 420, "#6A3A4A", 0.45, 0))
    for (hx, hy, s_) in ((50, 392, 0.8), (96, 410, 0.7), (142, 384, 0.6), (190, 404, 0.7), (30, 430, 0.9), (236, 380, 0.5), (122, 440, 1.0), (276, 392, 0.55), (70, 462, 1.1), (200, 444, 0.8)):
        art.append(f'<path d="{sp([(hx, hy), (hx + 5, hy - 18), (hx - 3, hy - 34), (hx + 8, hy - 52)], closed=False)}" stroke="#8A5A6A" stroke-width="{6 * s_:.1f}" fill="none" opacity="0.3" {P.blur(3)}/>')
        art.append(screen(glow(P, hx, hy, 24 * s_, "#FF9A40", 0.8)))
        art.append(K.flame(P, hx, hy + 2, 9 * s_, int(hx), n=3, sd=0.5))
    # the crag Prometheus descends: a ridge falling from the right toward the plain
    rock = [(120, 620), (170, 540), (240, 490), (300, 462), (334, 454), (370, 441), (392, 430), (430, 406), (470, 382), (520, 358), (570, 346), (640, 342), (640, 620)]
    art.append(crag(P, rock, ("#9A6050", "#3A2228", "#0C0608"), 5, L=(-0.2, -1), lit="#FFB070", src=(torch[0], torch[1] + 140, 260)))
    art.append(K.cast_shadow(P, ox + 10, oy + 2, 60, 6, "#000000", 0.6))
    # the warm pool of firelight and the figure
    art.append(screen(glow(P, torch[0], torch[1] + 120, 260, "#FF8A30", 0.3)))
    art.append(prometheus_figure(P, ox, oy, s, torch, 9))
    # the fennel stalk (narthex), the fire smouldering in its pith
    hx_, hy_ = ox + 45 * s, oy - 880 * s
    top = (torch[0], torch[1] + 6)
    bot = (hx_ + 18 * s, hy_ + 90 * s)
    art.append(K.taper([bot, (hx_, hy_), top], 8, 6, "#4A4420"))
    art.append(K.stroke_line([(bot[0] + 2, bot[1]), (hx_ + 2, hy_), (top[0] + 2, top[1])], "#FFD890", 1.4, 0.7))
    for t in (0.25, 0.6):
        nx_, ny_ = K.lerp2(bot, top, t)
        art.append(f'<path d="M {nx_ - 4:.1f} {ny_ + 1:.1f} l 9 -2" stroke="#1E2410" stroke-width="2.4"/>')
    art.append(screen(glow(P, top[0], top[1] - 30, 120, "#FFB040", 0.7)))
    art.append(K.flame(P, top[0], top[1] + 4, 82, 8, lean=0.35, n=8, w=0.36, sd=1.4))
    art.append(K.embers(11, top[0] + 30, top[1] - 40, 40, 160, 50))
    art.append(K.vignette(P, "#05030A", 0.6, 0.5, cx=0.6, cy=0.45))
    art.append(K.text_scrim(P, 440, 600, "#05030A", 0.8))
    text = [gilt(P, 300, 502, "PROMETHEUS", CINZEL, 58, ls=10, max_w=440, seed=13, deboss="#000000", dop=0.8),
            tx(300, 532, "GREEK · HE STOLE FIRE FOR US", CINZEL, 17, "#F2D8C8", ls=2.5, max_w=440),
            tx(70, 98, "Every hearth", SERIF_IT, 30, "#FFE6C8", max_w=240, anchor="start"),
            tx(70, 132, "began with him.", SERIF_IT, 30, "#FFE6C8", max_w=240, anchor="start")]
    return P.render(art, text, seed=21, edge=2.6, bristle=0.5, grain=0.2)


# ================================================================ kitsune — foxfires at the old enoki tree (plate, after Hiroshige)
def keyline(pts, col, w, seed, closed=True, var=0.45, seg=5):
    """A woodblock keyline: the outline cut as a carved, slightly swelling and thinning line (not a uniform stroke)."""
    rnd = random.Random(seed)
    P_ = K.catmull(list(pts) + ([pts[0], pts[1]] if closed else []), 5)
    out = []
    step = max(4, len(P_) // max(1, len(P_) // (seg * 5)))
    i = 0
    while i < len(P_) - 2:
        j = min(len(P_) - 1, i + rnd.randint(seg * 3, seg * 6))
        chunk = P_[i:j + 1]
        if len(chunk) >= 3:
            out.append(K.taper(chunk, w * rnd.uniform(0.3, 0.6), w * rnd.uniform(0.3, 0.6), col, 0.95, mid=w * rnd.uniform(1 - var, 1 + var * 0.6)))
        i = j - 1
    return "".join(out)


def kitsune_fox(P, ox, oy, s, seed, ink="#1E2440", L=(0.5, -0.8)):
    """A seated white fox (byakko), painted from life: tall black-backed ears, long narrow muzzle, a deep chest ruff,
    slim straight forelegs, the rounded haunch with the hind foot tucked forward, nine bushy tails rising behind
    like flames. Faces left. Lit cold from the foxfires and the sky. (ox, oy) = ground under the forefeet."""
    rnd = random.Random(seed)

    def Q(pts):
        return place(pts, ox, oy, s)
    out = []
    white = ("#FFFFFF", "#E6E6F2", "#5A5E92")
    # nine tails: each springs from the rump, sweeps back and up, the tip curling over
    root = (78, -40)
    tails = []
    for i in range(9):
        a0 = -44 - i * 6.8
        c = 1
        L_ = [236, 272, 250, 300, 262, 288, 244, 270, 226][i]
        W = 60 - abs(i - 4) * 2
        p0 = root
        dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (a0 - 6, a0 + c * 10, a0 + c * 58)]
        p1 = (p0[0] + dirs[0][0] * L_ * 0.38, p0[1] + dirs[0][1] * L_ * 0.38)
        p2 = (p1[0] + dirs[1][0] * L_ * 0.36, p1[1] + dirs[1][1] * L_ * 0.36)
        p3 = (p2[0] + dirs[2][0] * L_ * 0.28, p2[1] + dirs[2][1] * L_ * 0.28)
        spine = K.bez(p0, p1, p2, p3, 12)
        tails.append((i, spine, W))
    for i, spine, W in sorted(tails, key=lambda t: -abs(t[0] - 4)):
        pts = Q(K.plume(spine, W, (0.32, 0.58, 0.84, 0.98, 1.0, 0.92, 0.74, 0.46, 0.12)))
        flow_pts = Q(spine)

        def flow(x, y, fp=flow_pts):
            j = min(range(len(fp) - 1), key=lambda k: (fp[k][0] - x) ** 2 + (fp[k][1] - y) ** 2)
            return math.degrees(math.atan2(fp[j + 1][1] - fp[j][1], fp[j + 1][0] - fp[j][0]))
        tip0, tip1 = flow_pts[8], flow_pts[-1]
        gr = P.lin([(0, "#FFFFFF", 0), (1, "#F0FFFC", 1)], tip0[0], tip0[1], tip1[0], tip1[1], "userSpaceOnUse")
        out.append(K.furry(P, pts, white, L, seed + i * 7, flow, n=170, flen=(8 * s, 20 * s), fw=(0.7, 1.6), fop=(0.35, 0.7),
                           rough=(3.4 * s, 0.1), core=0.5, lit=0.6, edge="#0A0C24", edge_op=0.7,
                           extra=[f'<path d="{sp(pts)}" fill="{gr}"/>',
                                  soft(P, sp(Q(K.limb(spine[:6], [W * 0.05] * 6, [W * 0.5] * 6, 3))), "#2A2E5A", 0.6, 4 * s)]))
    # body (neck, chest ruff, forelegs, haunch, hind foot), then the head over it
    body_l = [(2, -212), (30, -172), (56, -132), (82, -98), (100, -62), (98, -26), (86, -7), (66, 0), (-6, 0), (-20, -4), (-34, -2), (-62, 0, 1),
              (-58, -8), (-54, -50), (-54, -96), (-62, -118), (-74, -136), (-68, -146), (-77, -154), (-66, -162), (-72, -172), (-50, -182),
              (-12, -194)]
    body = Q(body_l)

    def bflow(x, y):
        lx_ = (x - ox) / s
        if lx_ > 10:
            return 100 - min(40, (lx_ - 10) * 0.5)
        return 92
    over = [soft(P, sp(Q([(30, -200), (104, -90), (108, -10), (40, -10), (20, -120)])), "#262A56", 0.6, 10 * s),
            soft(P, sp(Q([(-56, -116), (-30, -110), (-30, -8), (-56, -8)])), "#4A4E84", 0.45, 4 * s),
            soft(P, sp(Q([(-70, -170), (-30, -186), (-10, -130), (-50, -112)])), "#FFFFFF", 0.7, 6 * s)]
    out.append(K.furry(P, body, white, L, seed + 50, bflow, n=340, flen=(5 * s, 13 * s), fw=(0.6, 1.3), fop=(0.3, 0.6), rough=(2.6 * s, 0.11),
                       core=0.5, lit=0.55, edge="#0A0C24", edge_op=0.65, pre=over, rim_col="#D8FFF8", rim_d=2.0))
    # ears (far ear first)
    far_ear = Q([(-14, -228), (-8, -274, 1), (4, -222)])
    out.append(K.furry(P, far_ear, ("#C8CCE0", "#7A7EA8", "#2A2E50"), L, seed + 60, -80, n=20, rough=None, core=0.4, lit=0.3, edge="#0A0C24", edge_op=0.6))
    head_l = [(-112, -199, 0.6), (-106, -205), (-80, -211), (-58, -220), (-46, -228), (-28, -232), (-8, -225), (2, -210), (-8, -193),
              (-18, -184), (-26, -179, 1), (-38, -182), (-50, -180), (-80, -185), (-98, -191)]
    head = Q(head_l)
    hover = [soft(P, sp(Q([(-100, -204), (-40, -230), (-10, -220), (-50, -200)])), "#FFFFFF", 0.7, 4 * s),
             soft(P, sp(Q([(-90, -188), (-50, -182), (-20, -186), (-60, -194)])), "#3A3E70", 0.45, 3 * s)]
    out.append(K.furry(P, head, white, L, seed + 61, lambda x, y: 185, n=120, flen=(4 * s, 9 * s), fw=(0.5, 1.1), fop=(0.3, 0.6), rough=(1.6 * s, 0.12),
                       core=0.35, lit=0.6, edge="#0A0C24", edge_op=0.7, pre=hover, rim_col="#D8FFF8", rim_d=1.6))
    near_ear = Q([(-38, -228), (-30, -246), (-25, -280, 1), (-16, -250), (-8, -226)])
    out.append(K.furry(P, near_ear, white, L, seed + 62, -80, n=30, rough=None, core=0.35, lit=0.6, edge="#0A0C24", edge_op=0.7))
    # ears: pink insides, black backs
    out.append(soft(P, sp(Q([(-31, -236), (-25, -266, 1), (-17, -238)])), "#D89098", 0.6, 1.2))
    out.append(K.path(sp(Q([(-25, -280, 1), (-19, -262), (-14, -250), (-22, -262)])), "#14161E", 0.85))
    out.append(K.path(sp(Q([(-8, -274, 1), (-3, -256), (0, -244), (-6, -258)])), "#14161E", 0.8))
    # vermilion markings of a divine fox along the brow
    out.append(K.taper(Q([(-62, -214), (-50, -220), (-38, -226), (-30, -231)]), 0.8, 1.4, "#D8302A", 0.9, mid=3.2 * s))
    # eye: narrow almond, amber, the lid line inked
    e1 = Q([(-58, -212), (-51, -215.5), (-44, -213), (-51, -209.5)])
    out.append(K.path(sp(e1), "#E8A020"))
    out.append(K.path(sp(Q([(-53, -215), (-49.5, -215), (-49, -210.5), (-52.5, -210.5)])), "#0A0A10"))
    out.append(K.stroke_line(Q([(-61, -210), (-51, -217), (-41, -213)]), "#0A0C1E", 1.5, 0.95))
    nose = Q([(-111, -200)])[0]
    out.append(f'<ellipse cx="{nose[0] + 1.5 * s:.1f}" cy="{nose[1] + 0.5 * s:.1f}" rx="{4 * s:.1f}" ry="{3 * s:.1f}" fill="#14161E"/>')
    out.append(K.stroke_line(Q([(-106, -194), (-92, -190), (-80, -189)]), "#20244A", 1.2, 0.8))
    for k in range(3):
        a_, b_ = Q([(-92 + k * 3, -197 + k * 2), (-130 + k * 4, -186 + k * 8)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#FFFFFF" stroke-width="0.7" opacity="0.6"/>')
    # the line of the near foreleg against the chest, the haunch and the tucked hind foot
    out.append(K.stroke_line(Q([(-34, -104), (-34, -60), (-36, -4)]), "#3A3E6A", 1.6, 0.6))
    out.append(K.stroke_line(Q([(74, -96), (44, -66), (20, -24), (6, -6)]), "#3A3E6A", 1.8, 0.55))
    for x0 in (-62, -38):
        for k in range(3):
            a_, b_ = Q([(x0 + 6 + k * 6, -1), (x0 + 6 + k * 6, -7)])
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#3A3E6A" stroke-width="1.1" opacity="0.6"/>')
    return "".join(out), [Q([sp_[-1]])[0] for _, sp_, _ in tails]


def kitsunebi(P, x, y, r, seed):
    """Foxfire: a small cold flame floating in the air, blue-white with a soft halo (as Hiroshige printed it)."""
    rnd = random.Random(seed)
    lean = rnd.uniform(-0.3, 0.3)
    pts = [(x - r, y + r * 0.2), (x - r * 0.85, y - r * 0.7), (x - r * 0.2 + lean * r, y - r * 1.6), (x + lean * r * 2.2, y - r * 3.0, 1),
           (x + r * 0.4 + lean * r, y - r * 1.4), (x + r, y - r * 0.4), (x + r * 0.8, y + r * 0.5), (x, y + r * 0.9)]
    return (screen(glow(P, x, y - r, r * 7, "#6AE8E0", 0.55)) + K.path(sp(pts), "#C8FFF6", 0.92)
            + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.55:.1f}" fill="#FFFFFF"/>')


def small_fox(P, x, y, s, flip, col="#E8E4DC", ink="#1E2440"):
    """A distant fox trotting through the field, in profile (a few strokes, as in the print's background)."""
    pts = [(-30, -14), (-20, -20), (10, -20), (22, -26), (30, -36, 1), (32, -26), (40, -22, 1), (30, -18), (24, -10), (20, 0, 1), (16, -6),
           (8, -8), (0, 0, 1), (-4, -8), (-16, -8), (-20, 0, 1), (-24, -8), (-30, -10), (-50, -18), (-58, -12, 1), (-44, -10)]
    q = place(pts, x, y, s, flip)
    return K.path(sp(q), col) + K.stroke_line(q + [q[0]], ink, 0.9, 0.8)


@plate("kitsune")
def kitsune_p():
    P = Plate("myp-ki")
    rnd = random.Random(5)
    ink = "#1A2040"
    # night sky in bokashi: Prussian blue darkening to the top, a band of pale indigo at the horizon
    art = [K.sky_grad(P, [(0, "#060A1C"), (0.35, "#0E1A3E"), (0.62, "#1E3466"), (0.74, "#3A5486"), (0.78, "#24345A"), (1, "#141A2E")])]
    art.append(K.stars(3, (0, 0, 600, 330), 120, cols=("#FFFFFF", "#F2F0D8"), r=(0.6, 1.5), op=(0.5, 1)))
    # distant woods and the roofs of Oji village on the horizon, flat and dark
    far = K.ridge(4, -20, 640, 470, 452, 10, 18, 0.5, bottom=620)
    art.append(K.path(sp(far), "#1A2440"))
    for k in range(26):
        x = rnd.uniform(-10, 610)
        art.append(K.path(sp(ellipse(x, 448 + rnd.uniform(-4, 4), rnd.uniform(10, 22), rnd.uniform(8, 16), 10)), "#141C34", 0.95))
    for x in (60, 96, 122, 200):
        art.append(K.path(lp([(x - 16, 452), (x, 440), (x + 16, 452)]), "#10162A"))
    # the field: dark fallow ground with bokashi, a path across it
    art.append(K.sky_grad(P, [(0, "#1E2A3E"), (0.4, "#16203A"), (1, "#0C1222")], 456, 600))
    art.append(K.path(sp([(-20, 470), (200, 462), (420, 470), (640, 466), (640, 476), (420, 480), (200, 474), (-20, 482)]), "#2E3A52", 0.6))
    # the procession of foxes coming across the fields, each with its own fire
    for k, (x, y) in enumerate(((40, 468), (72, 464), (104, 469), (136, 465), (168, 470), (196, 466))):
        art.append(small_fox(P, x, y, 0.32, True))
        art.append(kitsunebi(P, x + 16, y - 16, 2.4, k))
    # the great enoki tree on the right: twisted trunk, dark foliage masses with lit edges (as in the print)
    trunk = [(590, 620), (570, 520), (562, 440), (566, 380), (544, 320), (510, 270), (480, 240), (496, 236), (530, 262), (550, 286), (560, 250),
             (548, 200), (560, 196), (574, 250), (588, 300), (610, 340), (620, 360), (620, 620)]
    art.append(form(P, sp(trunk), ("#6A5A50", "#2E241E", "#0E0A08"), (-0.8, -0.6), K.bbox(trunk), core=0.6, lit=0.3,
                    extra=[K.brush(7, K.bbox(trunk), 60, 80, ["#4A3A30", "#14100C", "#7A6A5A"], (10, 30), (1.5, 3), (0.3, 0.6))]))
    art.append(keyline(trunk, ink, 2.2, 8))
    for (cx, cy, rx, ry) in ((580, 150, 110, 80), (470, 196, 80, 50), (620, 260, 70, 60), (500, 110, 90, 56)):
        art.append(f'<g {P.rough(9, 0.06, int(cx))}>' + K.foliage(P, int(cx + cy), cx, cy, rx, ry, ("#4A6A5A", "#1A2E2A", "#08120E"), L=(-0.6, -0.8), n=26, leaf=(5, 10), dabs=180, sd=1.6) + "</g>")
    # tall susuki grass at the lower left, silver plumes bowing
    for (bx_, by_, h_, lean_) in ((34, 600, 210, 0.22), (60, 600, 170, 0.12), (82, 600, 130, 0.28), (8, 600, 150, 0.08)):
        tip = (bx_ + lean_ * h_, by_ - h_)
        art.append(K.taper(K.catmull([(bx_, by_), (bx_ + lean_ * h_ * 0.4, by_ - h_ * 0.6), tip], 6), 3, 1.2, "#22303A"))
        for j in range(9):
            a_ = math.radians(90 + (j - 4) * 9)
            ln = rnd.uniform(26, 44)
            stx = K.catmull([tip, (tip[0] + math.cos(a_) * ln * 0.3 + lean_ * 20, tip[1] + 4), (tip[0] + math.cos(a_) * ln * 0.6 + lean_ * 40, tip[1] + ln * 0.5),
                             (tip[0] + math.cos(a_) * ln * 0.7 + lean_ * 50, tip[1] + ln)], 5)
            art.append(K.taper(stx, 2.2, 0.6, rnd.choice(["#E8E0D0", "#D8CCB8", "#F6F0E6"]), 0.85))
    # the nine-tailed fox in the foreground, its foxfires
    art.append(K.cast_shadow(P, 330, 528, 130, 9, "#000000", 0.55))
    art.append(screen(glow(P, 330, 400, 240, "#4AC8D0", 0.22)))
    art.append(screen(glow(P, 230, 380, 120, "#E8FFFF", 0.18)))
    fox, tips = kitsune_fox(P, 236, 526, 0.98, 9, ink)
    art.append(fox)
    for k, (x, y) in enumerate(tips):
        if k % 2 == 0:
            art.append(kitsunebi(P, x + 4, y - 4, 4.0, 20 + k))
    for (x, y, r) in ((150, 410, 4.5), (230, 300, 3.5), (430, 236, 3.5), (120, 500, 5)):
        art.append(kitsunebi(P, x, y, r, int(x)))
    # the cartouche: a vermilion title slip, as on a print
    art.append(K.path(lp([(62, 62), (292, 62), (292, 140), (62, 140)]), "#C8382A"))
    art.append(K.path(lp([(68, 68), (286, 68), (286, 134), (68, 134)]), "#F2E6CC"))
    art.append(K.stroke_line([(73, 73), (281, 73), (281, 129), (73, 129), (73, 73)], "#C8382A", 1.2, 0.8, smooth=False))
    art.append(K.text_scrim(P, 500, 600, "#05081A", 0.6))
    text = [tx(177, 120, "Kitsune", SERIF_IT, 56, "#1A2040", max_w=190),
            tx(64, 168, "JAPANESE · THE NINE-TAILED FOX", CINZEL, 16, "#F2E6CC", ls=1.6, max_w=330, anchor="start"),
            tx(300, 534, "A tail for every hundred years of wisdom", SERIF_IT, 24, "#F2F6FF", max_w=440)]
    return P.render(art, text, seed=34, edge=1.6, bristle=0.4, grain=0.2, streak=(0.012, 0.5))


# ================================================================ the moon rabbit — the jade hare pounding the elixir (plate, gongbi manner)
def jade_hare(P, ox, oy, s, seed, L=(-0.6, -0.8)):
    """The jade hare of the moon, upright on its hind legs, both forepaws on the pestle, about to strike the mortar.
    Painted in the gongbi manner: fine ink contour, layered washes, every hair laid with the brush. Faces right.
    (ox, oy) = ground under the hind feet; ears tip ~300 * s above."""
    def Q(pts):
        return place(pts, ox, oy, s)
    fur = ("#FFFFFF", "#E6E2DE", "#6A6878")
    line = "#2A2622"
    out = []
    # far ear (behind), laid back
    far_ear = Q([(-4, -226), (-30, -262), (-62, -290), (-82, -300, 1), (-70, -284), (-40, -250), (-14, -218)])
    out.append(K.furry(P, far_ear, ("#E8E0DC", "#A8A0A0", "#4A4448"), L, seed, 230, n=40, rough=None, core=0.5, lit=0.3, edge=line, edge_op=0.6))
    # far forearm (behind the pestle)
    far_arm = Q(K.limb([(4, -168), (24, -180), (44, -192), (56, -200)], [11, 9, 7, 6], [11, 9, 7, 6]))
    out.append(K.furry(P, far_arm, ("#D8D4D0", "#9A96A0", "#3A3840"), L, seed + 1, 20, n=30, rough=None, core=0.5, lit=0.2, edge=line, edge_op=0.7))
    body_l = [(-44, -2), (-62, -12), (-74, -34), (-78, -58), (-72, -84), (-64, -100, 0.3), (-58, -124), (-50, -152), (-40, -180), (-24, -206),
              (-18, -218), (-4, -232), (12, -234), (26, -226), (40, -212), (45, -206, 0.5), (42, -200), (34, -195), (22, -191), (12, -178),
              (18, -158), (22, -138), (18, -110), (14, -92), (12, -80, 0.3), (24, -66), (32, -46), (32, -24), (40, -12), (60, -2, 1)]
    body = Q(body_l)

    def flow(x, y):
        lx, ly = (x - ox) / s, (y - oy) / s
        if ly < -190:
            return 200
        return 100 - lx * 0.3
    over = [soft(P, sp(Q([(-60, -200), (-20, -220), (0, -120), (-40, -110)])), "#FFFFFF", 0.55, 10 * s),
            soft(P, sp(Q([(0, -170), (24, -150), (22, -90), (6, -100)])), "#4A4858", 0.4, 7 * s),
            soft(P, sp(Q([(-20, -228), (20, -230), (30, -212), (-10, -205)])), "#FFFFFF", 0.6, 4 * s)]
    out.append(K.furry(P, body, fur, L, seed + 2, flow, n=520, flen=(4 * s, 10 * s), fw=(0.45, 1.0), fop=(0.3, 0.65), rough=(1.8 * s, 0.14),
                       core=0.45, lit=0.55, edge=line, edge_op=0.85, pre=over, rim_col="#FFF8E0", rim_d=2.0, sd=8 * s))
    # the haunch: the great folded thigh of the hind leg, a separate rounded mass
    thigh = Q([(-70, -88), (-40, -104), (-6, -96), (18, -76), (28, -52), (26, -28), (6, -16), (-30, -14), (-60, -24), (-76, -50)])

    def tflow(x, y):
        lx, ly = (x - ox) / s, (y - oy) / s
        return math.degrees(math.atan2(ly + 56, lx + 26)) + 90
    out.append(K.furry(P, thigh, fur, L, seed + 5, tflow, n=200, flen=(4 * s, 9 * s), fw=(0.45, 1.0), fop=(0.3, 0.6), rough=(1.6 * s, 0.14),
                       core=0.55, lit=0.6, edge=line, edge_op=0.6, sd=10 * s,
                       pre=[soft(P, sp(Q(ellipse(-36, -70, 26, 22, 12))), "#FFFFFF", 0.55, 6 * s)]))
    # the long hind foot flat on the ground
    foot = Q([(-44, -2), (-20, -12), (20, -10), (50, -6), (62, -1, 1), (40, 2), (-30, 2)])
    out.append(K.furry(P, foot, fur, L, seed + 3, 0, n=40, rough=None, core=0.4, lit=0.4, edge=line, edge_op=0.8))
    # near ear, laid back along the head, pink inside
    ear = Q([(-2, -232), (-24, -268), (-52, -300), (-70, -314, 1), (-64, -296), (-40, -262), (-20, -226)])
    out.append(K.furry(P, ear, fur, L, seed + 4, 235, n=50, rough=None, core=0.35, lit=0.5, edge=line, edge_op=0.85))
    out.append(soft(P, sp(Q([(-12, -236), (-34, -266), (-56, -294), (-48, -270), (-26, -240)])), "#E8A8A0", 0.55, 1.4 * s))
    # eye: large, dark, a ring of lighter fur, the catchlight of the moon; nose and split lip
    ex, ey = Q([(22, -214)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{6.2 * s:.1f}" ry="{6.8 * s:.1f}" fill="#F2EEE8"/>')
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{4.8 * s:.1f}" ry="{5.4 * s:.1f}" fill="{P.rad([(0, "#5A2A1A"), (0.6, "#2A120A"), (1, "#0A0402")])}"/>')
    out.append(f'<circle cx="{ex - 1.6 * s:.1f}" cy="{ey - 2 * s:.1f}" r="{1.4 * s:.1f}" fill="#FFFFFF"/>')
    out.append(K.stroke_line(Q([(15, -217), (22, -221), (29, -217)]), line, 1.2, 0.8))
    out.append(K.path(sp(Q([(42, -208), (46, -205, 1), (42, -202)])), "#C88A8A"))
    out.append(K.stroke_line(Q([(44, -203), (42, -198), (38, -196)]), line, 1.0, 0.7))
    for k in range(4):
        a_, b_ = Q([(36, -204 + k * 2), (70 + k * 3, -214 + k * 8)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#FFFFFF" stroke-width="0.6" opacity="0.7"/>')
    return "".join(out)


def pestle_and_mortar(P, ox, oy, s, seed, hare_x, hare_y):
    """A turned wooden mortar (usu) with a jade-green bowl of the elixir, and the long pestle in the hare's paws."""
    def Q(pts):
        return place(pts, ox, oy, s)
    wood = ("#E8B88A", "#9A5A34", "#3A1C0C")
    out = []
    body = Q([(-46, 0), (-40, -24), (-44, -52), (-52, -66), (-50, -76), (50, -76), (52, -66), (44, -52), (40, -24), (46, 0)])
    rnd = random.Random(seed)
    grain = [K.stroke_line(Q([(x, -74), (x + rnd.uniform(-3, 3), -40), (x + rnd.uniform(-2, 2), 0)]), wood[2], 0.9, 0.35) for x in range(-40, 44, 7)]
    out.append(form(P, sp(body), wood, (-0.6, -0.8), K.bbox(body), core=0.6, lit=0.5, extra=grain, edge="#1A0C04", edge_op=0.8))
    out.append(K.path(sp(Q(ellipse(0, -76, 50, 9, 20))), "#5A3018"))
    out.append(K.path(sp(Q(ellipse(0, -75, 40, 6.5, 20))), P.rad([(0, "#E8FFF0"), (0.6, "#8AD8B0"), (1, "#2A7A5A")])))
    out.append(screen(glow(P, *Q([(0, -80)])[0], 60 * s, "#C8FFE0", 0.6)))
    return "".join(out)


def osmanthus(P, seed, axis, n_leaves=14, s=1.0):
    """A sprig of sweet osmanthus (the cassia of the moon): a dark twig, glossy oval leaves, clusters of tiny gold flowers."""
    rnd = random.Random(seed)
    out = [K.taper(axis, 6 * s, 1.5 * s, "#3A2A20")]
    ax = K.resample(axis, 12 * s)
    for i in range(1, len(ax) - 1):
        x, y = ax[i]
        a, b = ax[i - 1], ax[i + 1]
        base = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        for sg in (-1, 1):
            if rnd.random() < 0.35:
                continue
            ang = base + sg * rnd.uniform(35, 65)
            Ll = rnd.uniform(26, 40) * s
            c, si = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            loc = [(0, 0, 1), (Ll * 0.3, -Ll * 0.22), (Ll * 0.7, -Ll * 0.2), (Ll, 0, 1), (Ll * 0.7, Ll * 0.2), (Ll * 0.3, Ll * 0.22)]
            pts = [(x + px * c - py * si, y + px * si + py * c) + tuple(p[2:]) for p in loc for px, py in [p[:2]]]
            out.append(form(P, sp(pts), ("#7AA070", "#2A5034", "#0A1A10"), (-0.6, -0.8), K.bbox(pts), core=0.5, lit=0.5, sd=3 * s, edge="#0A1A10", edge_op=0.6))
            out.append(f'<path d="M {x:.1f} {y:.1f} L {x + c * Ll * 0.9:.1f} {y + si * Ll * 0.9:.1f}" stroke="#B8D0A0" stroke-width="0.8" opacity="0.6"/>')
        if rnd.random() < 0.7:
            for k in range(rnd.randint(4, 8)):
                fx, fy = x + rnd.uniform(-8, 8) * s, y + rnd.uniform(-6, 10) * s
                r = rnd.uniform(1.8, 2.8) * s
                out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r:.1f}" fill="#F2B030"/>')
                out.append(f'<circle cx="{fx - r * 0.3:.1f}" cy="{fy - r * 0.3:.1f}" r="{r * 0.45:.1f}" fill="#FFE8A0"/>')
    return "".join(out)


def xiangyun(P, cx, cy, w, seed, pal=("#FFFFFF", "#B4BCE6", "#4A52A0"), op=1.0):
    """An auspicious cloud (xiangyun) as painted in silk: a bank of scrolled, curling lobes with a trailing tail."""
    rnd = random.Random(seed)
    out = []
    lobes = []
    n = 5
    for i in range(n):
        t = i / (n - 1)
        x = cx - w / 2 + w * t
        r = w * (0.11 + 0.06 * math.sin(math.pi * t)) * rnd.uniform(0.9, 1.1)
        y = cy - math.sin(math.pi * t) * w * 0.07
        lobes.append((x, y, r))
    body = [(cx - w * 0.62, cy + w * 0.06)] + [(x, y - r * 0.9) for x, y, r in lobes] + [(cx + w * 0.55, cy + w * 0.04), (cx + w * 0.3, cy + w * 0.1), (cx - w * 0.3, cy + w * 0.1)]
    d = sp(body)
    out.append(form(P, d, pal, (-0.4, -0.9), K.bbox(body), core=0.4, lit=0.6, sd=w * 0.06, edge=pal[2], edge_op=0.5))
    for x, y, r in lobes:
        spiral = [(x + r * 0.9 * math.cos(a) * (1 - a / 14), y - r * 0.2 + r * 0.9 * math.sin(a) * (1 - a / 14)) for a in [k * 0.5 for k in range(16)]]
        out.append(K.stroke_line(spiral, pal[2], 1.3, 0.55))
        out.append(K.stroke_line([(px - 1, py - 1.5) for px, py in spiral[:8]], "#E8C870", 1.0, 0.7))
    tail = [(cx - w * 0.55, cy + w * 0.06), (cx - w * 0.8, cy + w * 0.02), (cx - w * 1.0, cy + w * 0.08), (cx - w * 1.15, cy + w * 0.03)]
    out.append(K.taper(tail, w * 0.06, 1, pal[1], 0.8 * op))
    return f'<g opacity="{op}">{"".join(out)}</g>'


@plate("the-moon-rabbit")
def the_moon_rabbit_p():
    P = Plate("myp-mr")
    rnd = random.Random(3)
    art = [K.sky_grad(P, [(0, "#0A0A24"), (0.5, "#1A1A44"), (1, "#0E0C26")])]
    art.append(K.sky_wash(P, 3, ["#2A2A6A", "#3A2A5A", "#0A0A20"], 14, (-40, -40, 640, 640), (100, 200), (0.12, 0.25), 40))
    art.append(K.stars(5, (0, 0, 600, 600), 110, avoid=lambda x, y: math.hypot(x - 300, y - 312) < 214))
    # the full moon, very large, the hare's realm
    mx, my, mr = 300, 312, 206
    art.append(glow(P, mx, my, mr * 1.6, "#C8C0FF", 0.35))
    md = sp(ellipse(mx, my, mr, mr, 48))
    art.append(K.path(md, P.rad([(0, "#FFFDF4"), (0.7, "#F6F0DA"), (0.92, "#E8DFC0"), (1, "#C8BC98")], cx=0.45, cy=0.42, r=0.6)))
    maria = [(-0.38, -0.3, 0.3, 0.22), (-0.02, -0.4, 0.2, 0.16), (0.24, -0.1, 0.2, 0.2), (-0.55, 0.1, 0.22, 0.35), (0.42, 0.22, 0.12, 0.12),
             (0.05, 0.28, 0.14, 0.1), (-0.15, 0.48, 0.1, 0.08)]
    art.append(clip_to(P, md, [f'<g {P.blur(14)}>' + "".join(f'<ellipse cx="{mx + x * mr:.1f}" cy="{my + y * mr:.1f}" rx="{a * mr:.1f}" ry="{b * mr:.1f}" fill="#B8AE90" opacity="0.32"/>' for x, y, a, b in maria) + "</g>",
                               K.brush(4, (mx - mr, my - mr, mx + mr, my + mr), 120, 0, ["#FFFFFF", "#E0D6B8"], (30, 90), (3, 8), (0.06, 0.16))]))
    # sweet osmanthus reaching in from the upper right (the cassia tree Wu Gang forever fells)
    art.append(osmanthus(P, 7, [(640, 160), (580, 182), (520, 212), (470, 236), (432, 248)], s=1.0))
    art.append(osmanthus(P, 8, [(640, 230), (600, 240), (566, 262)], s=0.9))
    # auspicious clouds drifting across the bottom of the moon, the hare stands on them
    art.append(xiangyun(P, 470, 470, 210, 4, op=0.95))
    art.append(xiangyun(P, 150, 430, 170, 5, op=0.85))
    art.append(K.cast_shadow(P, 276, 466, 120, 10, "#2A2A60", 0.5))
    art.append(xiangyun(P, 300, 476, 300, 6))
    hx, hy, hs = 256, 458, 0.92
    art.append(pestle_and_mortar(P, 340, 460, 1.0, 9, hx, hy))
    art.append(jade_hare(P, hx, hy, hs, 11))
    # the long pestle held in both forepaws, raised to strike
    top = place([(40, -262)], hx, hy, hs)[0]
    bot = (338, 384)
    art.append(K.taper([top, K.lerp2(top, bot, 0.5), bot], 7, 9, "#8A5A34"))
    art.append(K.stroke_line([(top[0] - 1.5, top[1]), (bot[0] - 2, bot[1])], "#E8C090", 1.4, 0.6))
    # near forearm and paws over the pestle
    paw = place(K.limb([(4, -166), (20, -174), (36, -188), (46, -200), (52, -206)], [11, 9, 6, 6, 5], [11, 10, 7, 7, 5]), hx, hy, hs)
    art.append(K.furry(P, place(ellipse(50, -204, 8, 7, 12), hx, hy, hs), ("#FFFFFF", "#E6E2DE", "#6A6878"), (-0.6, -0.8), 13, 30, n=20, rough=None,
                       core=0.35, lit=0.55, edge="#2A2622", edge_op=0.85))
    art.insert(-1, K.furry(P, paw, ("#FFFFFF", "#E6E2DE", "#6A6878"), (-0.6, -0.8), 12, 30, n=40, rough=None, core=0.35, lit=0.55, edge="#2A2622", edge_op=0.85))
    art.append(K.vignette(P, "#05051A", 0.5, 0.6))
    art.append(K.text_scrim(P, 490, 600, "#05051A", 0.6))
    text = [gilt(P, 300, 98, "The Moon Rabbit", SERIF_IT, 60, ls=0.5, max_w=440, seed=21, pal="pale", deboss="#000000", dop=0.8),
            tx(300, 534, "CHINESE · POUNDING THE ELIXIR OF LIFE", CINZEL, 17, "#E8E4FF", ls=2.4, max_w=440)]
    return P.render(art, text, seed=52, edge=1.8, bristle=0.4, grain=0.18)


# ================================================================ huginn and muninn — Odin's ravens at the rune stone (plate)
RAVEN_PAL = ("#6A7090", "#14161E", "#020204")


def raven_perched_g(P, ox, oy, s, seed, L=(-0.8, -0.5), rim_col="#FFD8A0", rim_src=None, flip=False):
    """A common raven perched, in profile (drawn in centimetres of a real bird, ~60 cm long): the heavy arched bill
    with its nasal bristles, flat crown, shaggy throat hackles, the long folded wing reaching toward the wedge tail,
    thick scaled legs gripping. Black, with a blue-violet sheen where the light strikes. (ox, oy) = feet; faces left."""
    def Q(pts):
        return place(pts, ox, oy, s, flip)
    out = []
    body = Q([(-26, -30, 1), (-23, -32), (-20, -33.6), (-17.5, -34.4), (-15.5, -36.2), (-12, -38), (-8, -38.2), (-5, -37), (-3, -35.4), (1, -33),
              (6, -29.5), (11, -25), (15, -20.5), (20, -15), (26, -9), (33, -3, 1), (29.5, -2), (24, -5.5), (17, -9.5), (11, -9), (6, -8.4), (1, -8),
              (-4, -8.6), (-9, -11), (-12.5, -14.5), (-14.6, -19), (-15.8, -22.6, 0.6), (-14.8, -23.2), (-16.8, -25.5, 0.6), (-15.4, -26), (-17.4, -27.6, 0.6), (-16, -28),
              (-18, -29), (-21, -29.4)])
    sheen = [soft(P, sp(Q([(-15, -37), (-4, -37), (4, -31), (-8, -33)])), "#8A94C8", 0.6, 1.2 * s),
             soft(P, sp(Q([(-14, -22), (-10, -14), (-6, -12), (-10, -20)])), "#5A6090", 0.35, 1.2 * s)]
    out.append(K.furry(P, body, RAVEN_PAL, L, seed, 25 if not flip else 155, n=180, flen=(1.2 * s, 2.8 * s), fw=(0.6, 1.2),
                       fop=(0.2, 0.5), rough=(0.35 * s, 0.14), core=0.6, lit=0.45, edge="#000000", edge_op=0.6, pre=sheen,
                       rim_col=rim_col, rim_d=1.8, rim_src=rim_src))
    # the folded wing: lesser and greater coverts in rows, then the long primaries, edges catching the light
    wing = Q([(-9, -30), (0, -31.5), (8, -27), (15, -21), (22, -13, 1), (16, -12.5), (8, -13), (0, -15), (-6, -19), (-10, -24)])
    feathers = []
    for k in range(5):
        t = k / 4
        feathers.append(K.stroke_line(Q([(-6 + t * 4, -27 + t * 6), (4 + t * 8, -24 + t * 7), (14 + t * 7, -18 + t * 5)]), "#000000", 0.45 * s, 0.6))
        feathers.append(K.stroke_line(Q([(-6 + t * 4, -27.4 + t * 6), (4 + t * 8, -24.4 + t * 7), (14 + t * 7, -18.4 + t * 5)]), "#8A92C0", 0.3 * s, 0.45))
    for k in range(6):
        x0 = -7 + k * 2.4
        feathers.append(K.scallops(seed + k, (x0, -30, x0 + 3, -22), 0, 0, ["#000000"]))
    feathers.append(K.scallops(seed + 30, K.bbox(wing[:6]), 26, 110, ["#6A72A0", "#000000"], (0.9 * s, 1.6 * s), (0.3, 0.6), (0.6, 1.0),
                               inside=K.inside_poly(Q([(-9, -30), (0, -31.5), (6, -28), (2, -22), (-6, -21)]))))
    out.append(form(P, sp(wing), ("#5A6088", "#101218", "#020203"), L, K.bbox(wing), core=0.5, lit=0.45, extra=feathers, edge="#000000", edge_op=0.5))
    # legs and toes, scaled
    for lx in (-2.2, 0.8):
        out.append(K.taper(Q([(lx, -8), (lx - 0.3, -3), (lx - 0.5, 0)]), 1.5 * s, 1.1 * s, "#0A0A0E"))
    for tx_, ty_ in ((-5.4, 0.8), (-3.6, 1.2), (3.2, 0.6)):
        out.append(K.taper(Q([(-0.6, 0), (tx_, ty_)]), 0.9 * s, 0.5 * s, "#0A0A0E"))
    # the bill: heavy, arched, glint along the culmen; nasal bristles; the eye with its glint
    bill = Q([(-26, -30, 1), (-23, -32), (-20, -33.6), (-17.5, -34.4), (-16.5, -31.5), (-18, -29.2), (-21, -29.4)])
    out.append(form(P, sp(bill), ("#6A6E80", "#141618", "#020203"), L, K.bbox(bill), core=0.4, lit=0.55, sd=0.8 * s))
    out.append(K.stroke_line(Q([(-25, -30.6), (-21.5, -32.8), (-18, -34)]), "#D0D8F0", 0.35 * s, 0.7))
    out.append(K.stroke_line(Q([(-25.6, -30), (-21, -30.6), (-17.6, -31.2)]), "#000000", 0.3 * s, 0.9))
    out.append(K.scallops(seed + 40, K.bbox(Q([(-19, -34.5), (-15, -31)])), 10, 200, ["#2A2C38", "#000000"], (0.5 * s, 0.9 * s), (0.5, 0.8), (0.5, 0.8)))
    ex, ey = Q([(-13.4, -34.6)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{0.95 * s:.1f}" fill="#1A1410"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{0.7 * s:.1f}" fill="#3A2A20"/>')
    out.append(f'<circle cx="{ex - 0.25 * s:.1f}" cy="{ey - 0.3 * s:.1f}" r="{0.28 * s:.1f}" fill="#FFF2D8"/>')
    return "".join(out)


def raven_flying_g(P, ox, oy, s, seed, ang=-20, squash=0.92, L=(-0.8, -0.5), rim_col="#FFD8A0", rim_src=None, flip=False):
    """A raven gliding overhead, seen from below as it crosses the sky: the long broad wings spread straight out,
    five primaries fingered at each tip and lit through from behind, the wedge-shaped tail, the head and heavy bill
    thrust forward. Drawn in cm (wingspan ~120), axis pointing left, rotated `ang` deg, wings foreshortened by squash."""
    def Q(pts):
        q = [(p[0], p[1] * squash) + tuple(p[2:]) for p in pts]
        return place(q, ox, oy, s, flip, ang)
    out = []

    def wing(sg):
        pts = [(-14, -4), (-16, -14), (-17, -26), (-15.5, -36), (-13, -46), (-11, -54), (-10, -60, 1), (-6, -52), (-4, -63, 1), (-0.5, -53),
               (3, -64, 1), (5, -53), (9.5, -61, 1), (10.5, -51), (15, -55, 1), (15.5, -46), (16, -34), (15, -24), (14, -14), (10, -5)]
        return [(x, y * sg) + tuple(p[2:]) for p in pts for x, y in [p[:2]]]
    sil = []
    near = Q(wing(-1))
    far = Q(wing(1))
    bodyp = Q([(-35, 0, 1), (-31, -1.8), (-27.5, -3.0), (-24, -4.4), (-20, -4.2), (-16, -4.6), (-8, -6.2), (2, -6.2), (10, -5.2), (15, -6.4),
               (22, -6.6), (30, -7.2, 0.5), (36, -3.6), (39, 0, 1), (36, 3.6), (30, 7.2, 0.5), (22, 6.6), (15, 6.4), (10, 5.2), (2, 6.2), (-8, 6.2),
               (-16, 4.6), (-20, 4.2), (-24, 4.4), (-27.5, 3.0), (-31, 1.8)])
    for pts_, k in ((far, 0), (near, 1)):
        # flight feathers lit through from behind: paler toward the trailing edge and the fingers
        sep = []
        for j, (fx, fy) in enumerate(((-10, -60), (-4, -63), (3, -64), (9.5, -61), (15, -55))):
            sg = -1 if k == 1 else 1
            sep.append(K.stroke_line(Q([(-12 + j * 4, -40 * sg), (fx - 0.4, (fy + 3) * sg)]), "#000000", 0.35 * s, 0.6))
        for j in range(7):
            sg = -1 if k == 1 else 1
            sep.append(K.stroke_line(Q([(-6 + j * 3, -14 * sg), (-4 + j * 3.2, -40 * sg)]), "#000000", 0.3 * s, 0.4))
        sg = -1 if k == 1 else 1
        trans = soft(P, sp(Q([(4, -8 * sg), (16, -10 * sg), (16, -48 * sg), (8, -58 * sg), (0, -40 * sg)])), "#6A6478", 0.65, 2.5 * s)
        out.append(form(P, sp(pts_), ("#5A5A70", "#121218", "#020204"), L, K.bbox(pts_), core=0.4, lit=0.3, extra=[trans] + sep,
                        edge="#000000", edge_op=0.5))
    out.append(K.furry(P, bodyp, RAVEN_PAL, L, seed + 3, ang + 180, n=60, flen=(1.2 * s, 2.6 * s), rough=None, core=0.5, lit=0.4, edge="#000000", edge_op=0.6))
    out.append(K.stroke_line(Q([(-33, 0), (-29, 0.2), (-25.6, 0.4)]), "#4A4E60", 0.3 * s, 0.8))
    out.append(K.rim(P, [sp(near), sp(far), sp(bodyp)], L, 1.6, rim_col, 0.85, sd=0.5, src=rim_src))
    return "".join(out)


def rune_stone(P, cx, base, w, h, seed, L=(-0.8, -0.5), rim_col="#FFC890", src=None):
    """A Viking-age rune stone of grey granite: a tall rounded slab, its face carved with a serpent band that loops
    round the edge, runes cut inside the band (traces of red paint in the grooves), lichen in orange and sage."""
    rnd = random.Random(seed)
    pts = [(cx - w * 0.5, base + 10), (cx - w * 0.52, base - h * 0.5), (cx - w * 0.44, base - h * 0.84), (cx - w * 0.22, base - h * 0.99),
           (cx + w * 0.06, base - h), (cx + w * 0.32, base - h * 0.93), (cx + w * 0.48, base - h * 0.7), (cx + w * 0.52, base - h * 0.3), (cx + w * 0.5, base + 10)]
    d = sp(pts)
    ex = [K.brush(seed, K.bbox(pts), 160, lambda x, y: rnd.uniform(0, 180), ["#B8B4A8", "#5A5650", "#8A867C", "#2A2824"], (3, 9), (1, 2.6), (0.2, 0.5))]
    # the serpent band (urnes-style loop) following the edge of the stone
    band = [(cx - w * 0.36, base - 4), (cx - w * 0.4, base - h * 0.5), (cx - w * 0.3, base - h * 0.8), (cx - w * 0.08, base - h * 0.88),
            (cx + w * 0.18, base - h * 0.84), (cx + w * 0.34, base - h * 0.66), (cx + w * 0.38, base - h * 0.36), (cx + w * 0.32, base - h * 0.1),
            (cx + w * 0.1, base - h * 0.04)]
    ex.append(K.stroke_line(band, "#2A2824", 17, 0.45))
    ex.append(K.stroke_line(band, "#B8B0A0", 13, 0.75))
    ex.append(K.stroke_line(band, "#A0402A", 13, 0.3))
    ex.append(K.stroke_line([(x + 6.5, y - 0.5) for x, y in band], "#1A1814", 1.3, 0.6))
    ex.append(K.stroke_line([(x - 6.5, y + 0.5) for x, y in band], "#1A1814", 1.3, 0.6))
    # runes inside the band (Younger Futhark staves cut as single strokes)
    pts_b = K.resample(K.catmull(band, 6), 13)
    for i, (x, y) in enumerate(pts_b[1:-1]):
        a, b = pts_b[i], pts_b[i + 2]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        stv = [(x - nx * 4.5, y - ny * 4.5), (x + nx * 4.5, y + ny * 4.5)]
        kind = rnd.randrange(4)
        ex.append(K.stroke_line(stv, "#2A1A14", 1.3, 0.85))
        tx_, ty_ = math.cos(ang) * 3, math.sin(ang) * 3
        if kind == 0:
            ex.append(K.stroke_line([(x - nx * 4, y - ny * 4), (x - nx * 1 + tx_, y - ny * 1 + ty_)], "#2A1A14", 1.1, 0.8))
        elif kind == 1:
            ex.append(K.stroke_line([(x, y), (x + tx_ - nx * 3, y + ty_ - ny * 3)], "#2A1A14", 1.1, 0.8))
        elif kind == 2:
            ex.append(K.stroke_line([(x - tx_ + nx * 2, y - ty_ + ny * 2), (x + tx_ - nx * 2, y + ty_ - ny * 2)], "#2A1A14", 1.1, 0.8))
    # the serpent's head biting its own tail at the bottom
    hx, hy = band[0]
    ex.append(K.path(sp([(hx - 10, hy - 4), (hx + 2, hy - 12), (hx + 14, hy - 6), (hx + 6, hy + 2)]), "#8A3A2A", 0.7))
    # lichen
    for k in range(18):
        x, y = rnd.uniform(cx - w * 0.5, cx + w * 0.5), rnd.uniform(base - h, base)
        r = rnd.uniform(3, 10)
        col = rnd.choice(["#D88A2A", "#C8B860", "#A8B898", "#E8A040"])
        ex.append(f'<path d="{K.sp(K.wobble(ellipse(x, y, r, r * 0.8, 9), k, r * 0.25))}" fill="{col}" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    body = form(P, d, ("#C8C4B8", "#6E6A62", "#1E1C1A"), L, K.bbox(pts), core=0.6, lit=0.5, extra=ex, edge="#000000", edge_op=0.5,
                rim_col=rim_col, rim_d=2.2, rim_op=0.9, rim_src=src)
    return f'<g {P.rough(2.4, 0.06, seed)}>{body}</g>'


@plate("huginn-and-muninn")
def huginn_and_muninn_p():
    P = Plate("myp-hm")
    rnd = random.Random(4)
    sx, sy = 176, 326
    L = (-0.85, -0.3)
    art = [K.sky_grad(P, [(0, "#1E1E3E"), (0.28, "#4A3A64"), (0.46, "#A06A78"), (0.53, "#F0A070"), (0.56, "#FFD890")], 0, 340)]
    art.append(K.sky_wash(P, 3, ["#7A5A80", "#2A2A58", "#E8A080"], 12, (-40, -40, 640, 300), (80, 160), (0.12, 0.25), 30))
    art.append(screen(glow(P, sx, sy, 300, "#FFC880", 0.6)))
    art.append(screen(glow(P, sx, sy, 60, "#FFF6D8", 0.9)))
    art.append(K.strata(P, 5, 262, -40, 640, 10, ("#FFE0B0", "#B06A70", "#5A3A5A"), L=(-0.6, 1), n=7, op=0.9))
    art.append(K.strata(P, 6, 176, 60, 640, 12, ("#F2B0A0", "#5A4A78", "#241E44"), L=(-0.8, 1), n=6, op=0.85))
    # fjord walls, layered: far (pale, warm with haze), mid (violet), near (dark) - the sun setting between them
    far = [(160, 340), (220, 304), (280, 290), (330, 300), (380, 280), (440, 270), (500, 286), (560, 270), (640, 280), (640, 340)]
    art.append(K.path(sp(far), "#9A6A80"))
    art.append(K.haze(P, 270, 340, "#F0B090", 0.1, 0.55))
    left = [(-20, 340), (-20, 230), (20, 226), (60, 252), (90, 290), (110, 324), (118, 340)]
    art.append(form(P, sp(left), ("#7A5A78", "#3A2C50", "#14102A"), (0.9, -0.4), K.bbox(left), core=0.4, lit=0.3, sd=8))
    art.append(K.water(P, 7, 338, 600, [(0, "#F0B080"), (0.15, "#9A6A80"), (0.6, "#3A2E50"), (1, "#1A1630")], ["#FFE0B0", "#3A2E50", "#B08090"], n=180, sun_x=sx, glint_w=24))
    art.append(K.haze(P, 334, 370, "#FFE0C0", 0.55, 0))
    near_r = [(250, 600), (290, 430), (330, 370), (380, 330), (440, 300), (500, 282), (560, 270), (640, 262), (640, 600)]
    art.append(crag(P, near_r, ("#8A6A70", "#2A2028", "#0A0810"), 8, L=L, lit="#FFC890", src=(sx, sy, 560), faces=30, strata=14))
    # the headland in the foreground: heather and grass, the rune stone standing on it
    ground = [(-20, 600), (-20, 486), (80, 476), (200, 470), (300, 474), (420, 482), (520, 478), (640, 472), (640, 600)]
    art.append(form(P, sp(ground), ("#8A7A5A", "#3A3020", "#100C08"), L, K.bbox(ground), core=0.4, lit=0.3, sd=10))
    art.append(K.grass(5, -10, 610, 468, 600, ["#4A4A2A", "#6A5A3A", "#2A2818", "#8A6A5A", "#7A4A6A", "#C89A70"], 460, (6, 16)))
    art.append(K.cast_shadow(P, 470, 482, 80, 7, "#000000", 0.5))
    art.append(rune_stone(P, 452, 484, 132, 204, 9, L=L, src=(sx, sy, 560)))
    # Huginn on the stone, Muninn coming in low over the water
    art.append(raven_perched_g(P, 446, 284, 3.3, 11, L=L, rim_src=(sx, sy, 520)))
    art.append(raven_flying_g(P, 226, 268, 2.15, 12, ang=-16, L=L, rim_src=(sx, sy, 380)))
    art.append(K.vignette(P, "#0A0812", 0.45, 0.6))
    art.append(K.text_scrim(P, 470, 600, "#0A0812", 0.75))
    text = [multi(300, 100, [("Huginn ", "#FFF2E4"), ("&", "#F2B060"), (" Muninn", "#FFF2E4")], DMS, 58, max_w=440, shadow="#000000", sdy=2.5),
            tx(300, 130, "NORSE · THOUGHT AND MEMORY", CINZEL, 17, "#F2E0D8", ls=2.5, max_w=440),
            tx(300, 532, "“Every day they fly over the wide world.”", SERIF_IT, 24, "#FFF0DC", max_w=440)]
    return P.render(art, text, seed=61, edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ the phoenix — rising from the pyre of myrrh (plate)
def feather(P, root, ang, L_, W, pal, seed, tip_round=0.5, curve=0.08, L=(0, -1), rachis="#FFF2C0", lit=0.45, core=0.45, edge="#3A0A04"):
    """One flight feather: a long vane, broader on the trailing side, rounded or pointed tip, a pale rachis, barb
    lines, coloured along its length (pal = base -> tip list of 3) and modelled across its width."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    n = 8
    for i in range(n + 1):
        t = i / n
        bend = math.sin(t * math.pi) * curve * L_
        cx, cy = root[0] + ux * L_ * t + nx * bend, root[1] + uy * L_ * t + ny * bend
        w = W * (0.35 + 0.65 * math.sin(min(1, t * 1.25) * math.pi / 2)) * (1 - max(0, t - 0.75) / 0.25 * (1 - tip_round) if t > 0.75 else 1)
        pts.append((cx, cy, w))
    left = [(x + nx * w * 0.42, y + ny * w * 0.42) for x, y, w in pts]
    right = [(x - nx * w * 0.58, y - ny * w * 0.58) for x, y, w in pts]
    tip = (pts[-1][0] + ux * W * 0.25 * tip_round, pts[-1][1] + uy * W * 0.25 * tip_round)
    outline = left + [tip] + right[::-1]
    d = sp(outline)
    gr = P.lin([(0, pal[0]), (0.55, pal[1]), (1, pal[2])], root[0], root[1], tip[0], tip[1], "userSpaceOnUse")
    ex = [f'<path d="{d}" fill="{gr}"/>']
    ex.append(soft(P, sp(right + [(x - nx * 1.5, y - ny * 1.5) for x, y, w in pts][::-1]), "#2A0402", 0.45, max(1, W * 0.12)))
    for k in range(int(L_ / 12)):
        t = rnd.uniform(0.1, 0.95)
        i = min(n - 1, int(t * n))
        x, y, w = pts[i]
        sgn = rnd.choice((-1, 1))
        ex.append(f'<path d="M {x:.1f} {y:.1f} l {nx * w * 0.5 * sgn + ux * w * 0.3:.1f} {ny * w * 0.5 * sgn + uy * w * 0.3:.1f}" stroke="{rnd.choice([pal[2], "#FFF2B0"])}" '
                  f'stroke-width="0.6" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    ex.append(K.stroke_line([(x, y) for x, y, w in pts], rachis, max(0.8, W * 0.06), 0.8))
    base = pal[1]
    return form(P, d, (pal[0], base, pal[2]), L, K.bbox(outline), core=core, lit=lit, extra=ex, edge=edge, edge_op=0.6, sd=max(1.2, W * 0.25))


def phoenix_wing(P, sg, cx, cy, s, seed):
    """A raised wing: primaries fanned from the hand, secondaries hanging from the forearm, two rows of coverts."""
    rnd = random.Random(seed)

    def Q(x, y):
        return (cx + sg * x * s, cy + y * s)
    out = []
    S, E, W_, H = (34, -34), (96, -96), (132, -170), (150, -196)
    prim = [("#FFE070", "#FF8A20", "#B8160C"), ("#FFD860", "#F8701A", "#9A0E08")]
    # primaries from the hand: up and outward
    for i in range(11):
        t = i / 10
        bx, by = W_[0] + (H[0] - W_[0]) * t, W_[1] + (H[1] - W_[1]) * t
        ang = -100 + t * 82 if sg > 0 else -80 - t * 82
        L_ = (150 + 40 * math.sin(t * math.pi * 0.8)) * s
        out.append(feather(P, Q(bx, by), ang, L_, 26 * s, prim[i % 2], seed + i, tip_round=0.6, curve=0.05 * sg, L=(-0.3 * sg, -1)))
    # secondaries along the forearm: outward and down
    for i in range(10):
        t = i / 9
        bx, by = E[0] + (W_[0] - E[0]) * t, E[1] + (W_[1] - E[1]) * t
        ang = (14 - t * 60) if sg > 0 else (166 + t * 60)
        out.append(feather(P, Q(bx, by), ang, (128 - t * 10) * s, 28 * s, ("#FFE68A", "#FFA030", "#C8301A"), seed + 20 + i, tip_round=0.8, L=(-0.3 * sg, -1)))
    # greater and lesser coverts: shorter, rounder, gold, scalloped rows over the bone
    for row, (Lc, Wc, off) in enumerate(((70, 26, 0), (44, 22, 0.15))):
        for i in range(12):
            t = i / 11
            p = K.lerp2(S, E, t * 2) if t < 0.5 else K.lerp2(E, W_, (t - 0.5) * 2)
            ang = ((30 - t * 90) if sg > 0 else (150 + t * 90))
            out.append(feather(P, Q(p[0] - 4 * row, p[1] + 6 * row), ang, Lc * s, Wc * s, ("#FFF4B0", "#FFC848", "#E06A1A"), seed + 40 + row * 20 + i,
                               tip_round=1.0, L=(-0.3 * sg, -1), lit=0.55))
    return "".join(out)


@plate("the-phoenix")
def the_phoenix_p():
    P = Plate("myp-ph")
    rnd = random.Random(8)
    cx, cy, s = 300, 344, 0.7
    art = [K.sky_grad(P, [(0, "#14060E"), (0.4, "#3A0E16"), (0.7, "#7A2412"), (1, "#C8501A")])]
    art.append(K.sky_wash(P, 3, ["#5A1018", "#A83A14", "#1E0610"], 14, (-40, -40, 640, 640), (100, 200), (0.15, 0.3), 40))
    art.append(screen(glow(P, cx, cy + 40, 340, "#FF9A30", 0.55)))
    art.append(screen(glow(P, cx, cy - 20, 170, "#FFE6A0", 0.45)))
    # rays of the reborn sun-bird
    art.append(K.rays(P, cx, cy, [-170 + i * 12 for i in range(30)], 420, [30, 14, 22], "#FFD890", 0.22, 6))
    # the pyre of myrrh and cinnamon twigs, and the fire that remakes it
    for k in range(16):
        x0 = cx - 120 + rnd.uniform(0, 240)
        a = rnd.uniform(-30, 30)
        L_ = rnd.uniform(60, 120)
        x1 = x0 + math.cos(math.radians(a)) * L_ * rnd.choice((-1, 1))
        y0 = 500 + rnd.uniform(-10, 14)
        art.append(K.taper([(x0, y0), (x1, y0 + math.sin(math.radians(a)) * L_ * 0.3)], 7, 5, rnd.choice(["#3A1A0A", "#5A2A10", "#2A0E06"])))
    art.append(screen(glow(P, cx, 470, 200, "#FF8A20", 0.6)))
    for k, (fx, fh) in enumerate(((cx - 100, 90), (cx - 60, 130), (cx - 20, 170), (cx + 20, 160), (cx + 64, 120), (cx + 104, 86), (cx, 120))):
        art.append(K.flame(P, fx, 512, fh, 70 + k, lean=rnd.uniform(-0.15, 0.15), n=6, w=0.42, sd=1.6))
    # the tail: long streaming plumes falling into the fire
    for i in range(7):
        t = (i - 3) / 3
        p0 = (cx + t * 8, cy + 60)
        p3 = (cx + t * 150 + rnd.uniform(-10, 10), cy + 190)
        spine = K.bez(p0, (p0[0] + t * 10, p0[1] + 60), (p3[0] - t * 40, p3[1] - 60), p3, 12)
        pts = K.plume(spine, 30 - abs(t) * 6, (0.2, 0.5, 0.8, 1, 1, 0.9, 0.7, 0.4, 0.1))
        gr = P.lin([(0, "#FFE070"), (0.5, "#FF7A1A"), (1, "#8A0A08")], p0[0], p0[1], p3[0], p3[1], "userSpaceOnUse")
        art.append(form(P, sp(pts), ("#FFE070", "#FF7A1A", "#7A0806"), (0, -1), K.bbox(pts), core=0.4, lit=0.5,
                        extra=[f'<path d="{sp(pts)}" fill="{gr}"/>', K.stroke_line(spine, "#FFF2B0", 1.2, 0.7),
                               K.along(30 + i, spine, [20] * len(spine), 40, ["#FFE070", "#C8200C", "#FFB040"], (6, 14), (0.6, 1.2), (0.3, 0.6))]))
        # an eye-spot at the end of the plume, as on the old mosaics
        ex, ey = spine[-3]
        art.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="7" ry="9" fill="#2A0A3A" opacity="0.8"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="4" ry="5.5" fill="#3AB8C8"/>')
    # wings
    art.append(phoenix_wing(P, -1, cx, cy, s, 10))
    art.append(phoenix_wing(P, 1, cx, cy, s, 30))
    # body: a deep eagle's breast, shoulders broad where the wings join, narrowing to the feathered thighs
    def B(pts):
        return [(cx + x * s, cy + y * s) + tuple(p[2:]) for p in pts for x, y in [p[:2]]]
    body = B([(18, -240), (44, -242), (60, -232), (68, -222), (56, -212), (40, -210), (28, -198), (24, -176), (30, -148), (46, -112), (58, -68),
              (60, -24), (52, 22), (40, 60), (28, 90), (12, 104), (-4, 106), (-20, 100), (-34, 84), (-46, 54), (-56, 14), (-60, -30), (-54, -76),
              (-40, -112), (-28, -140), (-26, -170), (-20, -200), (-4, -228)])
    art.append(K.furry(P, body, ("#FFF2A0", "#F2A030", "#8A2A0A"), (0.2, -1), 41, 90, n=0, rough=(1.2, 0.12), core=0.5, lit=0.55,
                       pre=[soft(P, sp(B(ellipse(-6, -40, 34, 56, 16))), "#FFF6C8", 0.7, 12 * s),
                            soft(P, sp(B(ellipse(30, 20, 24, 60, 16))), "#7A1A06", 0.4, 12 * s)],
                       extra=[K.scallops(42, K.bbox(body), 300, 90, ["#FFF6C0", "#C84A10", "#FFD060"], (3.2 * s, 5.6 * s), (0.4, 0.8), (0.8, 1.4), inside=K.inside_poly(body))],
                       rim_col="#FFF6C8", rim_d=2))
    beak = B([(58, -236), (76, -232), (88, -220), (90, -206, 1), (82, -214), (70, -216), (62, -218)])
    art.append(form(P, sp(beak), ("#FFF6D0", "#E8B040", "#6A3A0A"), (0, -1), K.bbox(beak), core=0.4, lit=0.6, sd=2, edge="#3A1A04", edge_op=0.7))
    ex, ey = B([(44, -228)])[0]
    art.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="#2A0A04"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.9" fill="#FFB020"/>'
               f'<circle cx="{ex + 0.4:.1f}" cy="{ey:.1f}" r="1.4" fill="#1A0402"/><circle cx="{ex - 0.8:.1f}" cy="{ey - 1.2:.1f}" r="0.8" fill="#FFFFFF"/>')
    art.append(K.taper(B([(40, -228), (26, -224), (12, -230)]), 2.4, 0.8, "#8A1A08", 0.8))
    # the crest: fine shafts tipped with flame-red feathers
    for k in range(6):
        a = math.radians(-160 + k * 15)
        base_ = B([(12 + k * 4, -238)])[0]
        tip = (base_[0] + math.cos(a) * 40 * s, base_[1] + math.sin(a) * 40 * s)
        mid = (base_[0] + math.cos(a) * 22 * s - 5 * s, base_[1] + math.sin(a) * 22 * s)
        art.append(K.taper([base_, mid, tip], 2.0, 0.8, "#FFC040", 0.9))
        art.append(f'<ellipse cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" rx="3.2" ry="4.4" fill="#E8301A" transform="rotate({math.degrees(a) + 90:.0f} {tip[0]:.1f} {tip[1]:.1f})"/>')
    for k, (fx, fh) in enumerate(((cx - 70, 60), (cx - 24, 84), (cx + 30, 76), (cx + 80, 56))):
        art.append(K.flame(P, fx, 516, fh, 170 + k, lean=rnd.uniform(-0.15, 0.15), n=5, w=0.4, sd=1.4))
    art.append(screen(glow(P, cx, cy - 30, 120, "#FFF6D8", 0.45)))
    art.append(K.embers(9, cx, 420, 160, 320, 120))
    art.append(K.vignette(P, "#0A0206", 0.55, 0.55))
    art.append(K.text_scrim(P, 490, 600, "#0A0206", 0.6))
    text = [gilt(P, 300, 104, "THE PHOENIX", CINZEL, 56, ls=8, max_w=440, seed=13, deboss="#000000", dop=0.85),
            tx(300, 534, "GREEK & EGYPTIAN · REBORN IN FIRE", CINZEL, 17, "#FFE8C8", ls=2.5, max_w=440)]
    return P.render(art, text, seed=71, edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ bastet — the bronze cat in the temple at sunset (plate)
def bronze_cat_g(P, ox, oy, s, seed, L=(-0.9, -0.35)):
    """A temple bronze of Bastet's cat (after the Late Period votive statues): seated upright, forelegs straight and
    together, a long neck, small head with tall ears, the tail laid along the ground round the forefeet. Cast bronze
    with a dark patina, verdigris in the hollows, gold earring and nose ring, a scarab on the brow, a silver wedjat
    pendant on an incised collar. In profile, facing left. (ox, oy) = ground under the forefeet."""
    def Q(pts):
        return place(pts, ox, oy, s)
    rnd = random.Random(seed)
    bronze = ("#E8C27A", "#3E2E18", "#0C0804")
    out = []
    # the far forefoot and hind foot
    out.append(form(P, sp(Q([(-10, 0), (-12, -60), (-4, -100), (6, -100), (6, -40), (8, 0)])), ("#B89058", "#3A2A16", "#0C0804"), L,
                    K.bbox(Q([(-12, -100), (8, 0)])), core=0.6, lit=0.3, edge="#000000", edge_op=0.5))
    far_ear = Q([(-20, -258), (-8, -298, 1), (0, -254)])
    out.append(form(P, sp(far_ear), ("#B89058", "#3A2A16", "#0C0804"), L, K.bbox(far_ear), core=0.5, lit=0.3, edge="#000000", edge_op=0.5, rim_col="#FFE6A8", rim_d=1.6))
    body = Q([(-46, 0), (-44, -40), (-44, -90), (-46, -128), (-50, -158), (-50, -184), (-48, -204), (-58, -212), (-67, -221), (-71, -230, 0.6),
              (-67, -238), (-58, -248), (-48, -256), (-36, -260), (-30, -302, 1), (-16, -264), (-6, -258), (2, -244), (6, -226), (12, -200),
              (18, -176), (32, -146), (50, -108), (66, -78), (76, -44), (72, -14), (62, 0)])
    rims = []
    ex = [
        # muscles and planes the founder chased into the bronze: shoulder, the haunch, the long neck
        soft(P, sp(Q(ellipse(-20, -150, 26, 40, 14))), bronze[0], 0.35, 8 * s),
        soft(P, sp(Q(ellipse(40, -60, 34, 48, 14))), bronze[2], 0.45, 10 * s),
        soft(P, sp(Q(ellipse(20, -70, 22, 34, 14))), bronze[0], 0.3, 8 * s),
        K.stroke_line(Q([(30, -120), (10, -90), (6, -40), (12, -4)]), bronze[2], 2.2 * s, 0.6),
        K.stroke_line(Q([(-44, -110), (-30, -112), (-14, -108)]), bronze[2], 1.4 * s, 0.4),
        # verdigris in the hollows
        f'<g {P.rough(4, 0.08, seed)}>' + "".join(f'<path d="{sp(Q(K.wobble(ellipse(x, y, r, r * 0.7, 9), k, r * 0.3)))}" fill="#4A9A84" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>'
                                                for k, (x, y, r) in enumerate(((20, -20, 14), (-34, -40, 8), (-2, -190, 7), (54, -100, 9), (-40, -140, 6), (62, -30, 7)))) + "</g>",
        # the incised collar with its wedjat pendant
        K.stroke_line(Q([(-48, -176), (-24, -170), (0, -176), (10, -188)]), "#E8D0A0", 1.6 * s, 0.8),
        K.stroke_line(Q([(-49, -168), (-24, -162), (2, -168), (14, -180)]), "#E8D0A0", 1.6 * s, 0.8),
        K.stroke_line(Q([(-49, -172), (-24, -166), (1, -172), (12, -184)]), "#1A1006", 1.2 * s, 0.7),
    ]
    out.append(form(P, sp(body), bronze, L, K.bbox(body), core=0.55, lit=0.45, extra=ex, edge="#000000", edge_op=0.55,
                    rim_col="#FFE6A8", rim_d=2.6, rim_op=1.0))
    out.append(K.rim(P, sp(body), (0.4, -1), 2.2, "#FFD890", 0.8, sd=0.6))
    # tail laid along the ground round the forefeet, its tip curling up
    tail = Q(K.limb([(68, -6), (30, -4), (-10, -4), (-50, -6), (-66, -14), (-70, -28)], [7, 7, 7, 6.5, 5, 3.5], [7, 7, 7, 6.5, 5, 3.5]))
    out.append(form(P, sp(tail), bronze, L, K.bbox(tail), core=0.5, lit=0.5, edge="#000000", edge_op=0.6, rim_col="#FFE6A8", rim_d=1.6))
    # head details: almond eye inlaid in glass and gold, the scarab on the brow, earring, nose ring, whisker pits
    eye = Q([(-56, -240), (-48, -245), (-40, -242), (-48, -238)])
    out.append(K.path(sp(eye), "#2A1A08"))
    out.append(K.path(sp(Q([(-54, -241), (-48, -244), (-42, -242), (-48, -239.5)])), "#C8E8D8"))
    out.append(K.path(sp(Q([(-49.5, -243.5), (-47.5, -243.5), (-47.5, -239.5), (-49.5, -239.5)])), "#0A0A0A"))
    out.append(K.stroke_line(Q([(-58, -239), (-48, -246), (-38, -242), (-32, -244)]), "#E8C878", 1.2 * s, 0.8))
    sc = Q(ellipse(-36, -254, 6, 4, 10))
    out.append(form(P, sp(sc), ("#FFF2B0", "#C89A30", "#5A3A08"), L, K.bbox(sc), core=0.4, lit=0.6, sd=1.5))
    ear_ring = Q(ellipse(-18, -266, 4.5, 6.5, 14))
    out.append(K.stroke_line(ear_ring + [ear_ring[0]], "#FFD860", 1.8 * s, 0.95))
    out.append(K.stroke_line(Q(ellipse(-69, -226, 2.6, 3.6, 10)), "#FFD860", 1.4 * s, 0.9))
    out.append(K.path(sp(Q([(-33, -264), (-29, -294, 1), (-20, -266)])), "#1A1006", 0.6))
    for k in range(3):
        out.append(f'<circle cx="{Q([(-62 + k * 3, -224 + k)])[0][0]:.1f}" cy="{Q([(-62 + k * 3, -224 + k)])[0][1]:.1f}" r="{0.8 * s:.1f}" fill="#1A1006" opacity="0.7"/>')
    # wedjat pendant in silver
    wx, wy = Q([(-40, -160)])[0]
    out.append(f'<ellipse cx="{wx:.1f}" cy="{wy:.1f}" rx="{7 * s:.1f}" ry="{6 * s:.1f}" fill="#D8DCE0"/>')
    out.append(K.stroke_line([(wx - 5 * s, wy), (wx, wy - 2.5 * s), (wx + 5 * s, wy)], "#2A2A2A", 1.2 * s, 0.9))
    out.append(f'<circle cx="{wx:.1f}" cy="{wy - 0.3 * s:.1f}" r="{1.6 * s:.1f}" fill="#1A1A1A"/>')
    out.append(K.stroke_line([(wx - 1 * s, wy + 1.6 * s), (wx - 1.5 * s, wy + 5 * s), (wx + 1 * s, wy + 6 * s)], "#2A2A2A", 1.0 * s, 0.9))
    # specular glints on the most lit planes
    for (x, y, r) in ((-56, -250, 6), (-46, -140, 10), (-44, -60, 8), (52, -94, 7)):
        gx, gy = Q([(x, y)])[0]
        out.append(screen(glow(P, gx, gy, r * s * 1.6, "#FFF2C8", 0.55)))
    return "".join(out)


def lotus_column(P, x, top, base, w, seed, lit_side=-1, L=(-0.9, -0.35), light="#FFC880"):
    """A papyrus-bundle column with an open papyrus capital, painted bands and incised reliefs, in deep shadow with a
    warm edge of sunset on the side facing the light."""
    rnd = random.Random(seed)
    shaft = [(x - w / 2, base), (x - w * 0.48, top + w * 0.9), (x - w * 0.42, top + w * 0.6), (x + w * 0.42, top + w * 0.6), (x + w * 0.48, top + w * 0.9), (x + w / 2, base)]
    cap = [(x - w * 0.42, top + w * 0.62), (x - w * 0.9, top + w * 0.1), (x - w * 0.95, top), (x + w * 0.95, top), (x + w * 0.9, top + w * 0.1), (x + w * 0.42, top + w * 0.62)]
    ex = []
    for k in range(5):
        xx = x - w * 0.4 + k * w * 0.2
        ex.append(K.stroke_line([(xx, top + w * 0.7), (xx, base)], "#000000", 1.4, 0.35))
    for yy in (top + w * 0.9, top + w * 1.05, top + w * 1.2):
        ex.append(K.stroke_line([(x - w / 2, yy), (x + w / 2, yy)], rnd.choice(["#2A6A8A", "#8A2A1A", "#C8A040"]), 3, 0.55))
    for k in range(10):
        gy = rnd.uniform(top + w * 1.4, base - 20)
        ex.append(f'<path d="M {x - w * 0.3:.1f} {gy:.1f} h {rnd.uniform(4, 10):.1f} v {rnd.uniform(4, 10):.1f}" stroke="#000000" stroke-width="1" fill="none" opacity="0.35"/>')
    out = [form(P, lp(shaft), ("#C89A6A", "#4A3424", "#0E0806"), L, K.bbox(shaft), core=0.7, lit=0.35, extra=ex, edge="#000000", edge_op=0.5,
                rim_col=light, rim_d=2.0, rim_op=0.8)]
    out.append(form(P, sp(cap), ("#C8A070", "#4A3828", "#0E0A06"), L, K.bbox(cap), core=0.6, lit=0.35,
                    extra=[K.stroke_line([(x + k * w * 0.18, top + w * 0.6), (x + k * w * 0.3, top + w * 0.05)], "#1E5A6A", 2.2, 0.6) for k in range(-3, 4)],
                    edge="#000000", edge_op=0.5, rim_col=light, rim_d=1.8, rim_op=0.8))
    return "".join(out)


@plate("bastet")
def bastet_p():
    P = Plate("myp-bs")
    rnd = random.Random(6)
    L = (-0.9, -0.35)
    # the temple court at sunset: a warm doorway of light behind, the hall in shadow
    art = [K.sky_grad(P, [(0, "#1A0E0A"), (0.4, "#3A2014"), (1, "#140A06")])]
    # the gateway opening onto the west: a glowing sky, palms and the Nile
    gate = [(150, 448), (150, 150), (450, 150), (450, 448)]
    art.append(f'<g {P.clip(f"<path d=\"{lp(gate)}\"/>")}>' + K.sky_grad(P, [(0, "#E8885A"), (0.45, "#FFC07A"), (0.7, "#FFE6A8"), (1, "#C88A50")], 150, 448)
               + glow(P, 230, 380, 120, "#FFF6D8", 0.8)
               + K.path(sp([(150, 400), (220, 392), (300, 396), (380, 388), (450, 394), (450, 448), (150, 448)]), "#6A4A3A")
               + K.path(lp([(150, 410), (450, 410), (450, 426), (150, 426)]), "#F2C890", 0.5)
               + "".join(f'<g transform="translate({px} {py})">{K.taper([(0, 0), (2, -40), (0, -70)], 4, 2, "#3A2418")}'
                         + "".join(K.taper([(0, -70), (math.cos(math.radians(a)) * 28, -70 + math.sin(math.radians(a)) * 16 + 10)], 5, 1, "#3A2A18") for a in range(-170, 10, 30)) + "</g>"
                         for px, py in ((180, 404), (206, 398), (402, 400), (428, 406)))
               + "</g>")
    art.append(K.path(lp([(140, 150), (460, 150), (460, 160), (140, 160)]), "#3A2214"))
    # the light from the gate spilling over the floor
    art.append(K.rays(P, 300, 300, [70 + i * 6 for i in range(7)], 340, [50, 30, 40], "#FFC070", 0.18, 10))
    # floor: polished stone catching the light
    floor = [(-20, 448), (620, 448), (620, 620), (-20, 620)]
    art.append(K.path(lp(floor), P.lin([(0, "#6A4428"), (0.3, "#3A2414"), (1, "#140A06")], 0, 448, 0, 600, "userSpaceOnUse")))
    art.append(screen(glow(P, 300, 456, 180, "#FFC07A", 0.35, ry=36)))
    # columns framing the gate, the lintel with the winged sun above
    art.append(lotus_column(P, 82, 108, 456, 84, 3, L=(0.9, -0.3)))
    art.append(lotus_column(P, 518, 108, 456, 84, 4, L=(-0.9, -0.3)))
    lintel = [(-20, 30), (620, 30), (620, 110), (-20, 110)]
    art.append(form(P, lp(lintel), ("#C89A6A", "#4A3424", "#140A06"), (0, 1), K.bbox(lintel), core=0.6, lit=0.3, grad=True))
    wing = []
    for sg in (-1, 1):
        for k in range(6):
            y = 70 + k * 4
            wing.append(K.taper([(300 + sg * 22, y), (300 + sg * (60 + k * 18), y - 6 + k), (300 + sg * (110 + k * 14), y + k * 2)], 6 - k * 0.6, 1.5,
                                ["#2A7AA8", "#C8A040", "#A83A20"][k % 3], 0.85))
    art.append("".join(wing))
    art.append(f'<circle cx="300" cy="72" r="13" fill="#C83A20"/><circle cx="296" cy="68" r="4" fill="#F2A070" opacity="0.6"/>')
    for sg in (-1, 1):
        art.append(K.taper([(300 + sg * 12, 84), (300 + sg * 18, 74), (300 + sg * 16, 62)], 4, 2, "#2A7A4A", 0.9))
    # the plinth and the statue
    plinth = [(204, 468), (208, 418), (392, 418), (396, 468)]
    art.append(form(P, lp(plinth), ("#C8A070", "#4A3424", "#140A06"), L, K.bbox(plinth), core=0.5, lit=0.5, edge="#000000", edge_op=0.6,
                    extra=[K.stroke_line([(214, 428), (386, 428)], "#E8C890", 1.2, 0.5)] +
                          [f'<path d="M {x} {442 + (k % 2) * 4} h 7 m -3 -3 v 9" stroke="#1A0E06" stroke-width="1.4" opacity="0.6"/>' for k, x in enumerate(range(222, 380, 16))],
                    rim_col="#FFD890", rim_d=1.8))
    art.append(K.cast_shadow(P, 336, 420, 84, 7, "#000000", 0.6))
    art.append(bronze_cat_g(P, 292, 418, 0.9, 9, L))
    # an offering lamp on the plinth's foot and a blue lotus laid before the goddess
    lamp = [(214, 418), (220, 410), (236, 408), (248, 412), (244, 418)]
    art.append(form(P, sp(lamp), ("#F2C890", "#8A5A30", "#2A1408"), (0, -1), K.bbox(lamp), core=0.4, lit=0.5, sd=2))
    art.append(screen(glow(P, 222, 400, 90, "#FFB850", 0.5)))
    art.append(K.flame(P, 220, 408, 16, 3, lean=0.1, n=3, w=0.3, sd=0.6))
    art.append(K.taper([(352, 418), (372, 416), (392, 418)], 2, 1, "#2A5A3A"))
    for k in range(5):
        a = math.radians(-150 + k * 25)
        art.append(K.path(sp([(350, 416), (350 + math.cos(a) * 14 - 3, 416 + math.sin(a) * 14), (350 + math.cos(a) * 18, 416 + math.sin(a) * 18, 1),
                              (350 + math.cos(a) * 14 + 3, 416 + math.sin(a) * 14)]), "#6A8AE8", 0.9))
    art.append(K.embers(5, 300, 300, 160, 260, 40, cols=("#FFE8C0", "#FFD8A0"), r=(0.5, 1.2)))
    art.append(K.vignette(P, "#0A0402", 0.6, 0.5))
    art.append(K.text_scrim(P, 480, 600, "#0A0402", 0.7))
    text = [gilt(P, 300, 510, "BASTET", CINZEL, 54, ls=12, max_w=400, seed=5, deboss="#000000", dop=0.85),
            tx(300, 538, "EGYPTIAN · GUARDIAN OF THE HOME", CINZEL, 17, "#F2DCC0", ls=2.5, max_w=440)]
    return P.render(art, text, seed=81, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ the sphinx — Giza at sunrise, Khafre's pyramid behind (plate)
def pyramid_g(P, apex, base_l, base_r, front_x, seed, lit=("#FFD8A0", "#E8A868", "#9A6038"), shade=("#C88A60", "#8A5434", "#3A2014"),
              cap=None, haze=0.0):
    """A pyramid seen from the south-east: the sunlit east face (left) and the shaded south face, courses of blocks
    as broken horizontal strokes, the weathered edges, an optional remnant of the smooth limestone casing at the top."""
    rnd = random.Random(seed)
    ax, ay = apex
    by = base_l[1]
    left = [apex, base_l, (front_x, by + 6)]
    right = [apex, (front_x, by + 6), base_r]
    out = [form(P, lp(left), lit, (-1, -0.2), K.bbox(left), core=0.25, lit=0.4, grad=True),
           form(P, lp(right), shade, (-1, -0.2), K.bbox(right), core=0.35, lit=0.15, grad=True)]
    courses = []
    for k in range(1, 40):
        t = k / 40
        y = ay + (by - ay) * t
        xl = ax + (base_l[0] - ax) * t
        xm = ax + (front_x - ax) * t
        xr = ax + (base_r[0] - ax) * t
        courses.append(K.stroke_line([(xl + 2, y), (xm - 1, y + 6 * t)], "#8A5434", 0.9, rnd.uniform(0.2, 0.45), smooth=False))
        courses.append(K.stroke_line([(xm + 1, y + 6 * t), (xr - 2, y)], "#2A1408", 0.9, rnd.uniform(0.2, 0.4), smooth=False))
    out.append(f'<g {P.rough(1.6, 0.2, seed)}>{"".join(courses)}</g>')
    if cap:
        t = cap
        cl = [apex, (ax + (base_l[0] - ax) * t, ay + (by - ay) * t), (ax + (front_x - ax) * t, ay + (by - ay) * t + 6 * t)]
        cr = [apex, (ax + (front_x - ax) * t, ay + (by - ay) * t + 6 * t), (ax + (base_r[0] - ax) * t, ay + (by - ay) * t)]
        out.append(K.path(lp(cl), "#FFF0D0", 0.85))
        out.append(K.path(lp(cr), "#C8A088", 0.85))
    out.append(K.stroke_line([apex, (front_x, by + 6)], "#FFE8C0", 1.2, 0.6, smooth=False))
    if haze:
        out.append(K.path(lp([apex, base_l, (front_x, by + 6), base_r]), "#F2C8A8", haze))
    return "".join(out)


def great_sphinx(P, ox, oy, s, seed, L=(-1, -0.25)):
    """The Great Sphinx in profile, facing the sunrise (left): the long couchant lion body cut from the bedrock, its
    eroded layers in bands, forepaws stretched out, the head in the striped nemes with its lappets, the face worn,
    the nose gone. (ox, oy) = ground at the tips of the forepaws; drawn ~440 * s long."""
    def Q(pts):
        return place(pts, ox, oy, s)
    rnd = random.Random(seed)
    stone = ("#FFD49A", "#9A6440", "#2E160A")
    out = []
    body = Q([(0, 0), (-2, -16), (6, -24), (40, -26), (70, -27), (88, -30), (92, -44), (96, -62), (102, -72), (110, -76), (176, -78), (198, -80), (230, -76), (292, -73),
              (350, -68), (398, -60), (428, -46), (440, -26), (442, 0)])
    ex = []
    # the eroded strata: alternating hard and soft layers of the Mokattam limestone
    for k, (y, w, col, op) in enumerate(((-10, 6, "#4A2814", 0.5), (-26, 8, "#C8925E", 0.4), (-38, 5, "#3A1C0C", 0.55), (-50, 9, "#D8A068", 0.35),
                                         (-62, 6, "#4A2814", 0.5), (-70, 4, "#E8B880", 0.45))):
        line = [(x, y + math.sin(x * 0.07 + k) * 1.6 + rnd.uniform(-1, 1)) for x in range(80, 446, 12)]
        ex.append(f'<g {P.rough(3, 0.06, seed + k)}>' + K.stroke_line(Q(line), col, w * s, op) + "</g>")
    ex.append(soft(P, sp(Q(ellipse(392, -34, 44, 26, 16))), stone[0], 0.35, 8 * s))
    ex.append(soft(P, sp(Q(ellipse(396, -26, 30, 20, 16))), stone[2], 0.45, 8 * s))
    # restoration blocks along the base
    for x in range(100, 430, 14):
        ex.append(K.path(lp(Q([(x, -2), (x + 13, -2), (x + 13, -12), (x, -12)])), rnd.choice(["#D8A878", "#B88458", "#E8B888"]), 0.55))
    # the paws: toes and the gap between them
    ex.append(K.stroke_line(Q([(2, -12), (80, -14)]), "#3A2010", 1.6 * s, 0.55))
    ex.append(soft(P, sp(Q([(0, -24), (80, -28), (80, -16), (0, -14)])), "#FFE8C0", 0.45, 3 * s))
    for k in range(3):
        ex.append(K.stroke_line(Q([(5 + k * 5, -22), (7 + k * 5, -2)]), "#3A2010", 1.2 * s, 0.5))
    out.append(form(P, sp(body), stone, L, K.bbox(body), core=0.65, lit=0.22, extra=ex, edge="#1A0A04", edge_op=0.6, rim_col="#FFE8C0", rim_d=2.4))
    # the head: nemes headdress with its stripes and lappets, worn face, ear
    nemes = Q([(100, -112), (106, -128), (122, -136), (142, -134), (156, -124), (166, -104), (174, -84), (178, -74), (150, -70), (136, -78),
               (126, -86), (112, -96), (104, -104)])
    stripes = [K.stroke_line(Q([(112 + k * 7, -130 + k * 0.5), (140 + k * 5, -76 + k)]), "#6A3A1C", 3 * s, 0.4) for k in range(7)]
    out.append(form(P, sp(nemes), ("#FFDCA8", "#A87048", "#3A1E0E"), L, K.bbox(nemes), core=0.5, lit=0.55, extra=stripes, edge="#2A1408",
                    edge_op=0.5, rim_col="#FFE8C0", rim_d=2))
    face = Q([(100, -112), (95, -108), (93, -100), (90, -94), (91, -90), (94, -86), (93, -82), (97, -78), (104, -74), (116, -74), (124, -82),
              (126, -96), (118, -108)])
    fex = [soft(P, sp(Q(ellipse(103, -101, 6.5, 3.4, 10))), "#2A1408", 0.75, 1.0 * s),          # the eye in its deep socket
           soft(P, sp(Q([(96, -108), (110, -108), (108, -104), (97, -105)])), "#FFF0D0", 0.6, 1.0 * s),  # the brow catching the sun
           K.path(sp(Q([(91, -96), (95, -97), (97, -90), (93, -88)])), "#4A2814", 0.6),          # the broken nose
           K.stroke_line(Q([(93, -84), (99, -83.5), (102, -85)]), "#3A2010", 1.3 * s, 0.7),       # the mouth, a faint smile
           soft(P, sp(Q([(104, -96), (112, -94), (110, -84), (102, -86)])), "#FFF0D0", 0.35, 2 * s),  # the cheek plane
           soft(P, sp(Q([(112, -100), (124, -98), (122, -78), (110, -78)])), "#5A321A", 0.5, 3 * s)]
    out.append(form(P, sp(face), ("#FFE2B0", "#C08A58", "#4A2814"), L, K.bbox(face), core=0.4, lit=0.6, extra=fex, edge="#2A1408", edge_op=0.4,
                    rim_col="#FFF0D0", rim_d=1.8))
    ear = Q([(118, -102), (124, -106), (128, -98), (124, -90), (118, -92)])
    out.append(form(P, sp(ear), ("#FFE2B0", "#C08A58", "#4A2A16"), L, K.bbox(ear), core=0.5, lit=0.4, sd=2))
    # the uraeus scar on the brow
    out.append(K.stroke_line(Q([(100, -114), (104, -120)]), "#3A2010", 1.6 * s, 0.6))
    return "".join(out)


@plate("the-sphinx")
def the_sphinx_p():
    P = Plate("myp-sx")
    rnd = random.Random(5)
    sx, sy = 70, 300
    art = [K.sky_grad(P, [(0, "#3A4A7A"), (0.3, "#8A7A9A"), (0.5, "#E8A88A"), (0.62, "#FFD8A0"), (0.7, "#FFE8C0")], 0, 420)]
    art.append(K.sky_wash(P, 3, ["#C88A9A", "#5A6A9A", "#FFC890"], 12, (-40, -40, 640, 380), (90, 180), (0.12, 0.25), 34))
    art.append(screen(glow(P, sx, sy, 320, "#FFD890", 0.6)))
    art.append(screen(glow(P, sx, sy, 50, "#FFFBEA", 0.95)))
    art.append(K.strata(P, 4, 236, -40, 640, 8, ("#FFE8C8", "#D89A90", "#8A6A88"), L=(-1, 0.2), n=6, op=0.8))
    # the pyramids: Khufu's far right, Khafre's behind the Sphinx (with its casing cap), Menkaure small far left
    art.append(pyramid_g(P, (148, 300), (78, 380), (232, 380), 120, 4, haze=0.45))
    art.append(pyramid_g(P, (560, 150), (330, 400), (720, 400), 470, 5, haze=0.25))
    art.append(pyramid_g(P, (390, 168), (196, 404), (600, 404), 330, 6, cap=0.16, haze=0.3))
    art.append(K.haze(P, 260, 420, "#FFD8B0", 0.0, 0.6))
    # the desert floor: dunes and the plateau, long morning shadows to the right
    sand = [(-20, 600), (-20, 404), (120, 398), (260, 404), (420, 396), (620, 402), (620, 600)]
    art.append(form(P, sp(sand), ("#FFE0B0", "#D8A070", "#7A4A28"), (-1, -0.4), K.bbox(sand), core=0.3, lit=0.4, sd=20))
    ripples = [K.stroke_line([(x, y), (x + rnd.uniform(30, 70), y + rnd.uniform(-2, 2))], rnd.choice(["#FFF0D0", "#B87A48"]), rnd.uniform(1, 2.2), rnd.uniform(0.3, 0.6))
               for x, y in [(rnd.uniform(-20, 600), rnd.uniform(470, 600)) for _ in range(60)]]
    art.append(f'<g {P.blur(0.6)}>{"".join(ripples)}</g>')
    # a camel caravan crossing far off
    for k, x in enumerate((230, 252, 274)):
        art.append(K.path(sp([(x - 9, 410), (x - 8, 402), (x - 4, 398), (x, 401), (x + 4, 397), (x + 7, 400), (x + 10, 394), (x + 12, 396), (x + 9, 402), (x + 8, 410),
                              (x + 6, 410), (x + 5, 404), (x - 5, 404), (x - 6, 410)]), "#4A2A20", 0.85))
    # the Sphinx and its long shadow
    art.append(f'<path d="{sp([(150, 470), (420, 476), (640, 482), (640, 500), (420, 494), (150, 484)])}" fill="#5A3020" opacity="0.4" {P.blur(4)}/>')
    art.append(great_sphinx(P, 52, 478, 1.36, 7))
    art.append(K.vignette(P, "#1A0A06", 0.4, 0.6))
    art.append(K.text_scrim(P, 490, 600, "#1A0A06", 0.55))
    text = [gilt(P, 300, 100, "The Sphinx", SERIF_IT, 64, ls=0.5, max_w=420, seed=8, deboss="#000000", dop=0.7),
            tx(300, 130, "EGYPTIAN · GUARDIAN OF THE HORIZON", CINZEL, 17, "#FFF2E4", ls=2.4, max_w=440),
            tx(300, 534, "He has watched the sun rise for 4,500 years.", SERIF_IT, 22, "#FFF4E4", max_w=440)]
    return P.render(art, text, seed=91, edge=2.0, bristle=0.4, grain=0.2)


# ================================================================ egyptian canon figures (shared by the boat of ra and the weighing of the heart)
EGY_LINE = "#2A120A"


def egy_paint(P, pts, fill, line=EGY_LINE, w=1.3, op=1.0, shade=0.12, seed=1):
    """Flat mineral colour as the tomb painters laid it: an even fill with a faint uneven density (it was brushed onto
    plaster), and a fine, sure dark outline."""
    d = sp(pts)
    out = [K.path(d, fill, op)]
    if shade:
        out.append(clip_to(P, d, [f'<path d="{d}" fill="#000000" opacity="{shade}" {P.mottle(0.05, 0.6, seed)}/>']))
    out.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{w}" stroke-linejoin="round" opacity="0.92"/>')
    return "".join(out)


def egy_figure(P, x, base, g, head="jackal", arms=None, kneel=False, flip=False, skin="#1A1614", seed=1, spear=None, crown=None):
    """A figure drawn on the Egyptian canon (19 squares from soles to crown, g = one square): legs and head in profile,
    shoulders and eye frontal, the white linen shendyt kilt with its pleats, a broad collar (wesekh) in bands of blue,
    green, red and gold, armlets and bracelets, a tripartite wig. Faces right (flip -> left).
    arms: dict(near=(shoulder, elbow, wrist), far=(...)) in squares; kneel: one knee down, the other raised."""
    def Q(pts):
        return place(pts, x, base, g, flip)
    out = []
    line_w = max(1.0, g * 0.09)
    skin_l = mix(skin, "#FFFFFF", 0.0)
    if kneel:
        # far (back) leg: knee on the ground, shin flat along it, toes bent
        out.append(egy_paint(P, Q(K.limb([(-0.6, -6.6), (-1.6, -3.2), (-1.8, -0.5)], [1.1, 0.7, 0.45], [1.2, 0.7, 0.45])), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q([(-1.8, -1.0), (-3.8, -0.6), (-4.6, -0.2), (-4.8, 0, 1), (-1.4, 0), (-1.2, -0.6)]), skin, w=line_w, seed=seed))
        # near leg: knee raised, foot flat
        out.append(egy_paint(P, Q(K.limb([(0.6, -6.8), (2.8, -6.4), (3.0, -3.4), (3.0, -0.6)], [1.0, 0.7, 0.75, 0.4], [1.1, 0.7, 0.55, 0.4])), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q([(2.5, -0.9), (3.4, -0.9), (4.4, -0.4), (5.2, 0, 1), (2.4, 0), (2.4, -0.5)]), skin, w=line_w, seed=seed))
        hip = -6.8
    else:
        out.append(egy_paint(P, Q(K.limb([(-0.3, -9.2), (-1.0, -5.2), (-1.9, -0.7)], [1.1, 0.62, 0.36], [1.15, 0.68, 0.36])), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q([(-2.4, -0.9), (-1.5, -0.9), (-0.5, -0.4), (0.2, 0, 1), (-2.6, 0), (-2.6, -0.5)]), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q(K.limb([(0.7, -9.2), (1.6, -5.2), (2.5, -0.7)], [1.1, 0.62, 0.36], [1.15, 0.68, 0.36])), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q([(2.0, -0.9), (2.9, -0.9), (3.9, -0.4), (4.7, 0, 1), (1.9, 0), (1.9, -0.5)]), skin, w=line_w, seed=seed))
        hip = -9.2
    dy = 0 if not kneel else 2.4
    # far arm (behind the torso)
    if arms and arms.get("far"):
        sh, el, wr = arms["far"]
        out.append(egy_paint(P, Q(K.limb([sh, el, wr], [0.62, 0.45, 0.32], [0.62, 0.45, 0.32])), skin, w=line_w, seed=seed))
        out.append(egy_paint(P, Q(ellipse(wr[0] + 0.25, wr[1] + 0.05, 0.42, 0.32, 10)), skin, w=line_w, seed=seed))
    # kilt
    kilt = [(-1.6, -11.2 + dy), (1.8, -11.2 + dy), (2.2, -9.5 + dy), (3.4, -6.6 + dy, 1), (-1.9, -6.6 + dy), (-1.8, -9.5 + dy)]
    out.append(egy_paint(P, Q(kilt), "#F6F0E0", w=line_w, shade=0.06, seed=seed))
    for k in range(6):
        out.append(K.stroke_line(Q([(0.2 + k * 0.4, -10.9 + dy), (0.6 + k * 0.5, -6.8 + dy)]), "#B8A888", max(0.6, g * 0.05), 0.7))
    out.append(K.stroke_line(Q([(-1.6, -11.0 + dy), (1.8, -11.0 + dy)]), "#C8A040", max(1, g * 0.18), 0.9))
    # torso, frontal shoulders
    torso = [(-1.3, -11.2 + dy), (-1.5, -12.5 + dy), (-2.4, -14.2 + dy), (-3.0, -15.6 + dy), (-2.6, -16.2 + dy), (-0.7, -16.4 + dy), (0.7, -16.4 + dy),
             (2.6, -16.2 + dy), (3.0, -15.6 + dy), (2.6, -14.4 + dy), (2.0, -13.6 + dy), (1.6, -12.5 + dy), (1.5, -11.2 + dy)]
    out.append(egy_paint(P, Q(torso), skin, w=line_w, seed=seed))
    # broad collar
    for k, col in enumerate(("#C8A040", "#2A6AA8", "#3A9A6A", "#C83A2A", "#C8A040")):
        r = 0.7 + k * 0.32
        arc = [(0.3 + math.cos(math.radians(a)) * r * 1.35, -16.3 + dy + math.sin(math.radians(a)) * r * 0.9) for a in range(15, 166, 10)]
        out.append(K.stroke_line(Q(arc), col, max(1.0, g * 0.3), 0.95))
    # near arm
    if arms and arms.get("near"):
        sh, el, wr = arms["near"]
        sh, el, wr = (sh[0], sh[1] + dy), (el[0], el[1] + dy), (wr[0], wr[1] + dy)
        out.append(egy_paint(P, Q(K.limb([sh, el, wr], [0.62, 0.45, 0.32], [0.62, 0.45, 0.32])), skin, w=line_w, seed=seed))
        for t, col in ((0.25, "#C8A040"), (0.88, "#2A6AA8")):
            p = K.lerp2(sh, el, t) if t < 0.5 else K.lerp2(el, wr, t)
            out.append(f'<circle cx="{Q([p])[0][0]:.1f}" cy="{Q([p])[0][1]:.1f}" r="{0.42 * g:.1f}" fill="{col}" stroke="{EGY_LINE}" stroke-width="{line_w * 0.6:.1f}"/>')
        out.append(egy_paint(P, Q(ellipse(wr[0] + 0.25, wr[1] + 0.05, 0.42, 0.32, 10)), skin, w=line_w, seed=seed))
    # head
    hy = dy
    if head == "jackal":
        wig = [(-0.9, -16.0 + hy), (-1.0, -17.6 + hy), (-0.6, -18.9 + hy), (0.6, -19.1 + hy), (1.2, -18.6 + hy), (1.2, -15.0 + hy), (0.3, -14.8 + hy), (0.0, -16.2 + hy)]
        out.append(egy_paint(P, Q(wig), "#1E2A5A", w=line_w, seed=seed))
        for k in range(5):
            out.append(K.stroke_line(Q([(0.35, -18.0 + k * 0.7 + hy), (1.15, -18.0 + k * 0.7 + hy)]), "#C8A040", max(0.8, g * 0.08), 0.85))
        h = [(-0.6, -16.4 + hy), (-0.8, -17.6 + hy), (-0.6, -18.7 + hy), (-0.3, -19.0 + hy), (0.1, -21.6 + hy, 1), (0.8, -19.2 + hy), (1.3, -18.9 + hy), (3.1, -18.2 + hy),
             (3.4, -17.9 + hy, 0.5), (3.0, -17.5 + hy), (1.4, -17.1 + hy), (0.6, -16.5 + hy)]
        out.append(egy_paint(P, Q(h), skin, w=line_w, seed=seed))
        out.append(K.path(sp(Q([(-0.1, -19.2 + hy), (0.1, -21.0 + hy, 1), (0.5, -19.3 + hy)])), "#C8A040", 0.5))
        ex_, ey_ = Q([(1.5, -18.4 + hy)])[0]
        out.append(K.path(sp(Q([(1.1, -18.45 + hy), (1.55, -18.65 + hy), (2.0, -18.45 + hy), (1.55, -18.25 + hy)])), "#F6F0E0"))
        out.append(f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{0.13 * g:.1f}" fill="#0A0604"/>')
        out.append(K.stroke_line(Q([(2.9, -17.6 + hy), (2.0, -17.45 + hy)]), "#C83A2A", max(0.8, g * 0.08), 0.8))
    elif head == "set":
        h = [(-0.6, -16.4 + hy), (-0.8, -17.6 + hy), (-0.5, -18.6 + hy), (-0.4, -20.8 + hy), (-0.6, -21.2 + hy, 1), (0.2, -21.2 + hy, 1), (0.1, -19.3 + hy),
             (0.6, -19.4 + hy), (0.7, -21.0 + hy), (0.6, -21.4 + hy, 1), (1.4, -21.4 + hy, 1), (1.1, -19.1 + hy), (2.2, -18.7 + hy), (3.2, -18.0 + hy), (3.6, -17.4 + hy, 0.5),
             (3.2, -17.3 + hy), (2.0, -17.2 + hy), (0.8, -16.8 + hy)]
        out.append(egy_paint(P, Q(h), skin, w=line_w, seed=seed))
        ex_, ey_ = Q([(1.2, -18.4 + hy)])[0]
        out.append(K.path(sp(Q([(0.8, -18.45 + hy), (1.25, -18.65 + hy), (1.7, -18.45 + hy), (1.25, -18.25 + hy)])), "#F6F0E0"))
        out.append(f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{0.13 * g:.1f}" fill="#0A0604"/>')
    elif head == "falcon":
        wig = [(-1.0, -15.6 + hy), (-1.1, -17.6 + hy), (-0.6, -19.0 + hy), (0.8, -19.3 + hy), (1.4, -18.6 + hy), (1.3, -15.0 + hy), (0.3, -14.8 + hy), (0.0, -16.2 + hy)]
        out.append(egy_paint(P, Q(wig), "#1E2A5A", w=line_w, seed=seed))
        for k in range(5):
            out.append(K.stroke_line(Q([(0.35, -18.0 + k * 0.7 + hy), (1.25, -18.0 + k * 0.7 + hy)]), "#C8A040", max(0.8, g * 0.08), 0.85))
        h = [(-0.4, -17.0 + hy), (-0.5, -18.3 + hy), (0.2, -19.1 + hy), (1.2, -19.0 + hy), (1.9, -18.5 + hy), (2.4, -18.0 + hy), (2.5, -17.4 + hy, 1), (2.1, -17.6 + hy),
             (1.9, -17.4 + hy), (1.2, -17.3 + hy), (0.6, -16.9 + hy)]
        out.append(egy_paint(P, Q(h), "#3A6A4A", w=line_w, seed=seed))
        out.append(K.path(sp(Q([(1.0, -18.1 + hy), (1.3, -17.4 + hy), (1.0, -16.9 + hy), (0.8, -17.6 + hy)])), "#1A1410", 0.9))
        ex_, ey_ = Q([(1.2, -18.4 + hy)])[0]
        out.append(f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{0.28 * g:.1f}" fill="#F6F0E0" stroke="{EGY_LINE}" stroke-width="{line_w * 0.6:.1f}"/>'
                   f'<circle cx="{ex_ + 0.05 * g:.1f}" cy="{ey_:.1f}" r="{0.15 * g:.1f}" fill="#0A0604"/>')
    if crown == "sun":
        cx_, cy_ = Q([(0.6, -20.6 + hy)])[0]
        out.append(screen(glow(P, cx_, cy_, 3.6 * g, "#FFB040", 0.5)))
        out.append(egy_paint(P, ellipse(cx_, cy_, 1.6 * g, 1.6 * g, 28), "#D8402A", w=line_w, seed=seed, shade=0.05))
        out.append(K.stroke_line(Q([(1.6, -19.4 + hy), (1.8, -20.4 + hy), (1.4, -21.0 + hy)]), "#C8A040", max(1.2, g * 0.25), 0.95))
    if spear:
        a_, b_ = Q([spear[0]]), Q([spear[1]])
        out.append(K.stroke_line([a_[0], b_[0]], "#5A3A1A", max(1.4, g * 0.22), 1.0, smooth=False))
        out.append(K.stroke_line([a_[0], b_[0]], "#C8A060", max(0.6, g * 0.07), 0.8, smooth=False))
    return "".join(out)


def papyrus_umbel(P, x, y, s, ang, col=("#3A8A5A", "#C8A040")):
    """The flared papyrus-umbel finial of a sacred barque's prow or stern."""
    pts = place([(0, 0), (-10, -18), (-16, -30), (0, -26), (16, -30), (10, -18)], x, y, s, False, ang)
    out = [egy_paint(P, pts, col[0], w=1.2, seed=3)]
    for k in range(-2, 3):
        a_, b_ = place([(0, -2), (k * 6, -27)], x, y, s, False, ang)
        out.append(K.stroke_line([a_, b_], col[1], 1.0, 0.8))
    return "".join(out)


# ================================================================ the boat of ra — the sun's night voyage, as painted in a royal tomb (plate)
def tomb_star(x, y, r, col="#F2C850"):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return K.path(lp(pts), col, 0.95)


def apophis(P, seed, spine, w, col=("#E8C070", "#9A6A2A", "#2A1A08")):
    """Apep, the chaos serpent, rising from the waters of the night in great loops, spotted, with knives in its back
    as the funerary books show it."""
    pts = K.limb(K.catmull(spine, 6), [w * (0.4 + 0.6 * min(1, i / 8)) for i in range(len(K.catmull(spine, 6)))],
                 [w * (0.4 + 0.6 * min(1, i / 8)) for i in range(len(K.catmull(spine, 6)))], n=1)
    out = [egy_paint(P, pts, col[1], w=1.4, seed=seed)]
    ax = K.resample(K.catmull(spine, 6), 9)
    rnd = random.Random(seed)
    for i, (x, y) in enumerate(ax[2:-2]):
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w * 0.18:.1f}" ry="{w * 0.12:.1f}" fill="{col[2]}" opacity="0.7"/>')
    # knives
    for t in (0.35, 0.6, 0.82):
        i = int(t * (len(ax) - 1))
        x, y = ax[i]
        out.append(K.path(lp([(x - 2, y - w * 0.4), (x + 2, y - w * 0.4), (x + 1, y - w * 1.6), (x - 3, y - w * 1.2)]), "#D8DCE0"))
        out.append(K.stroke_line([(x - 3, y - w * 0.4), (x + 3, y - w * 0.4)], "#5A3A1A", 2.4, 1))
    # head at the end of the spine
    hx, hy = spine[-1]
    a, b = spine[-2], spine[-1]
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    head = place([(0, -w * 0.55), (w * 0.9, -w * 0.5), (w * 1.6, -w * 0.15), (w * 1.7, w * 0.15, 0.5), (w * 0.9, w * 0.45), (0, w * 0.5)], hx, hy, 1, False, ang)
    out.append(egy_paint(P, head, col[1], w=1.4, seed=seed))
    ex, ey = place([(w * 0.8, -w * 0.2)], hx, hy, 1, False, ang)[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{w * 0.12:.1f}" fill="#F6F0E0"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{w * 0.06:.1f}" fill="#000"/>')
    tq = place([(w * 1.7, w * 0.1), (w * 2.2, w * 0.05), (w * 2.4, -w * 0.1), (w * 2.25, w * 0.12), (w * 2.45, w * 0.3)], hx, hy, 1, False, ang)
    out.append(K.stroke_line(tq, "#C83A2A", 1.4, 0.9))
    return "".join(out)


@plate("the-boat-of-ra")
def the_boat_of_ra_p():
    P = Plate("myp-ra")
    rnd = random.Random(2)
    # the tomb ceiling: Egyptian blue night, rows of yellow stars, the plaster showing through
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#14286A")]
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#3A5AB0" opacity="0.5" {P.mottle(0.012, 0.7, 5, (0.0, 0.0, 0.05))}/>')
    for r_ in range(7):
        for c_ in range(11):
            x = 30 + c_ * 56 + (28 if r_ % 2 else 0)
            y = 40 + r_ * 44
            art.append(tomb_star(x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2), 9))
    # the frieze above (khekher) and the borders in red, blue and yellow
    for k in range(16):
        x = -8 + k * 40
        art.append(egy_paint(P, [(x, 34, 1), (x + 4, 12), (x + 6, 6), (x + 13, 3), (x + 20, 6), (x + 22, 12), (x + 26, 34, 1)], ["#C83A2A", "#2A8A6A", "#C8A040"][k % 3], w=1, seed=k, shade=0.05))
    art.append(K.path(lp([(-10, 34), (610, 34), (610, 42), (-10, 42)]), "#C8A040"))
    # the waters of the night: zigzag bands
    art.append(K.path(lp([(-10, 384), (610, 384), (610, 610), (-10, 610)]), "#0E1E50"))
    for r_ in range(7):
        y = 396 + r_ * 16
        zz = [(x, y + (5 if (x // 12) % 2 else -5)) for x in range(-12, 624, 12)]
        art.append(K.stroke_line(zz, "#5A8AD8" if r_ % 2 else "#2A4A98", 2.2, 0.85, smooth=False))
    # Apep rising before the prow
    art.append(apophis(P, 7, [(600, 520), (560, 470), (520, 500), (490, 440), (520, 400), (510, 360), (474, 352)], 20))
    # the sacred barque: a papyrus-bundle hull curving up at both ends, lashed bindings, the cabin-shrine amidships
    hull = [(70, 300), (96, 344), (140, 372), (300, 384), (450, 372), (494, 346), (512, 306), (504, 304), (486, 340), (440, 360), (300, 368), (150, 358),
            (108, 336), (82, 298)]
    art.append(egy_paint(P, hull, "#C89A40", w=1.6, seed=3))
    for k in range(22):
        x = 120 + k * 16
        art.append(K.stroke_line([(x, 360 + abs(x - 300) * 0.02), (x - 2, 382 - abs(x - 300) * 0.04)], "#6A4A1A", 1.6, 0.8))
    art.append(K.stroke_line([(96, 344), (140, 370), (300, 382), (450, 370), (494, 346)], "#2A6AA8", 3, 0.9))
    art.append(papyrus_umbel(P, 76, 300, 1.2, -40))
    art.append(papyrus_umbel(P, 508, 306, 1.2, 36))
    # the steering oars at the stern
    art.append(K.stroke_line([(120, 300), (96, 400)], "#6A4A1A", 4, 1, smooth=False))
    art.append(egy_paint(P, [(90, 380, 1), (100, 380, 1), (98, 420), (92, 420)], "#C8A040", w=1, seed=4))
    # the shrine: a kiosk with a cavetto cornice, the god inside
    shrine = [(236, 366, 1), (236, 216, 1), (360, 216, 1), (360, 366, 1)]
    art.append(egy_paint(P, shrine, "#F2E2B8", w=1.6, seed=5, shade=0.08))
    art.append(egy_paint(P, [(228, 216, 1), (368, 216, 1), (374, 200, 1), (222, 200, 1)], "#2A6AA8", w=1.4, seed=6))
    for k in range(10):
        art.append(K.path(lp([(232 + k * 14, 202), (238 + k * 14, 202), (238 + k * 14, 214), (232 + k * 14, 214)]), ["#C83A2A", "#C8A040"][k % 2]))
    art.append(screen(glow(P, 300, 260, 150, "#FFB040", 0.35)))
    # Ra, falcon-headed, the sun disk on his head, holding the was-sceptre
    art.append(egy_figure(P, 290, 364, 7.0, head="falcon", skin="#B0522E", crown="sun",
                          arms=dict(near=((2.4, -15.8), (3.6, -12.8), (5.4, -12.4)), far=((-2.4, -15.8), (-0.6, -12.6), (1.2, -11.6)))))
    a_, b_ = place([(5.6, -19.0)], 290, 364, 7.0)[0], place([(5.6, -0.4)], 290, 364, 7.0)[0]
    art.append(K.stroke_line([a_, b_], "#2A1A0A", 2.4, 1, smooth=False))
    art.append(K.stroke_line([(a_[0], a_[1]), (a_[0] + 6, a_[1] - 4)], "#2A1A0A", 2.4, 1, smooth=False))
    # Set at the prow, spearing Apep
    sp_ = ((-1.5, -17.5), (12.5, 0.5))

    def on(t):
        return (sp_[0][0] + (sp_[1][0] - sp_[0][0]) * t, sp_[0][1] + (sp_[1][1] - sp_[0][1]) * t)
    art.append(egy_figure(P, 410, 364, 6.6, head="set", skin="#B0522E", arms=dict(near=((2.4, -15.8), (3.9, -13.4), on(0.38)), far=((-2.4, -15.8), (-1.0, -13.4), on(0.22))),
                          spear=sp_))
    # the register line and the title band
    art.append(K.path(lp([(-10, 470), (610, 470), (610, 610), (-10, 610)]), "#1A0E08", 0.0))
    band = [(40, 474, 1), (560, 474, 1), (560, 548, 1), (40, 548, 1)]
    art.append(egy_paint(P, band, "#1E1410", w=1.6, seed=8, shade=0.0))
    art.append(K.stroke_line([(46, 480), (554, 480), (554, 542), (46, 542), (46, 480)], "#C8A040", 1.6, 0.9, smooth=False))
    for k in range(26):
        x = 50 + k * 20
        art.append(K.path(lp([(x, 474), (x + 10, 474), (x + 10, 470), (x, 470)]), ["#C83A2A", "#2A8A6A", "#C8A040"][k % 3]))
    # the wall itself: faded, flaked plaster
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#F2E2B8" opacity="0.12" {P.mottle(0.03, 0.8, 9, (0.95, 0.88, 0.72))}/>')
    flakes = "".join(f'<path d="{sp(K.wobble(ellipse(x, y, r, r * 0.6, 8), int(x), r * 0.3))}" fill="#E8D8B0" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>'
                     for x, y, r in [(rnd.uniform(0, 600), rnd.uniform(0, 600), rnd.uniform(1, 4)) for _ in range(40)] if not (40 < x < 560 and 474 < y < 548))
    art.append(flakes)
    text = [gilt(P, 300, 514, "THE BOAT OF RA", CINZEL, 40, ls=6, max_w=480, seed=5, deboss="#000000", dop=0.8),
            tx(300, 538, "EGYPTIAN · SAILING THE NIGHT", CINZEL, 16, "#F2DCC0", ls=2.5, max_w=440)]
    return P.render(art, text, seed=101, edge=1.4, bristle=0.35, grain=0.22)


# ================================================================ the weighing of the heart — a vignette from a Book of the Dead (plate)
def papyrus_sheet(P, seed, x0=-10, y0=-10, x1=610, y1=610):
    """A papyrus sheet: warm cream with the crossed layers of pith strips showing as faint fibres, darker joins, the
    edges browned with age."""
    rnd = random.Random(seed)
    out = [K.path(lp([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), "#EAD7A8")]
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#C8A060" opacity="0.5" {P.mottle(0.015, 0.75, seed, (0.55, 0.38, 0.16))}/>')
    fib = []
    for k in range(110):
        y = rnd.uniform(y0, y1)
        fib.append(K.stroke_line([(x0, y), (x1, y + rnd.uniform(-3, 3))], rnd.choice(["#B89058", "#F6E8C0"]), rnd.uniform(0.6, 1.6), rnd.uniform(0.12, 0.3), smooth=False))
    for k in range(60):
        x = rnd.uniform(x0, x1)
        fib.append(K.stroke_line([(x, y0), (x + rnd.uniform(-3, 3), y1)], rnd.choice(["#B89058", "#F6E8C0"]), rnd.uniform(0.6, 1.4), rnd.uniform(0.08, 0.2), smooth=False))
    for x in (150, 340, 520):
        fib.append(K.stroke_line([(x, y0), (x + 2, y1)], "#A87A40", 5, 0.12, smooth=False))
    out.append(f'<g {P.blur(0.4)}>{"".join(fib)}</g>')
    out.append(K.vignette(P, "#6A4018", 0.55, 0.62))
    return "".join(out)


def glyph_g(kind, x, y, s, col):
    """A few hieratic-hand hieroglyphs as a scribe brushed them (reed leaf, water, loaf, mouth, quail chick, eye, ankh,
    owl, seated man). Drawn small, in black or red ink."""
    def L(pts):
        return [(x + px * s, y + py * s) + tuple(p[2:]) for p in pts for px, py in [p[:2]]]
    if kind == "reed":
        return K.path(sp(L([(0, 8), (-2, 0), (0, -9, 1), (2, 0)])), col)
    if kind == "water":
        return K.stroke_line(L([(-7, 0), (-5, -2), (-3, 0), (-1, -2), (1, 0), (3, -2), (5, 0), (7, -2)]), col, 1.4 * s, 1, smooth=False)
    if kind == "loaf":
        return K.path(sp(L([(-6, 2, 1), (-5, -2), (0, -4), (5, -2), (6, 2, 1)])), col)
    if kind == "mouth":
        return K.path(sp(L(ellipse(0, 0, 6, 2.6, 12))), col)
    if kind == "chick":
        return K.path(sp(L([(-5, 6, 1), (-4, -1), (-1, -5), (2, -7), (5, -6, 1), (3, -4), (4, 0), (2, 4), (1, 7, 1), (-2, 4)])), col)
    if kind == "eye":
        return K.path(sp(L([(-7, 0, 1), (-2, -3), (4, -2), (7, 0, 1), (2, 2), (-3, 2)])), col) + K.path(sp(L(ellipse(0, -0.4, 1.6, 1.6, 8))), "#EAD7A8")
    if kind == "ankh":
        return (K.stroke_line(L(ellipse(0, -5, 3, 4, 12)) + [L([(3, -5)])[0]], col, 1.3 * s, 1) + K.stroke_line(L([(-5, 0), (5, 0)]), col, 1.4 * s, 1, smooth=False)
                + K.stroke_line(L([(0, -1), (0, 8)]), col, 1.4 * s, 1, smooth=False))
    if kind == "owl":
        return K.path(sp(L([(-4, 8, 1), (-5, 0), (-4, -6), (-1, -8), (2, -7), (3, -3), (5, 2), (6, 8, 1)])), col)
    if kind == "man":
        return K.path(sp(L([(-2, -8), (1, -8), (1, -5), (3, -3), (2, 2), (5, 7, 1), (-5, 7, 1), (-3, 2), (-2, -4)])), col)
    return ""


def hiero_column(seed, x, y0, y1, s, red_every=0):
    rnd = random.Random(seed)
    kinds = ["reed", "water", "loaf", "mouth", "chick", "eye", "ankh", "owl", "man", "reed", "water"]
    out = []
    y = y0
    i = 0
    while y < y1:
        k = rnd.choice(kinds)
        col = "#9A2A1A" if (red_every and i % red_every == 0) else "#1E140C"
        if k in ("water", "loaf", "mouth"):
            out.append(glyph_g(k, x, y, s, col))
            y += 7 * s
        else:
            out.append(glyph_g(k, x, y + 5 * s, s, col))
            y += 17 * s
        i += 1
    return "".join(out)


def ammit(P, x, base, s, seed):
    """Ammit, the Devourer of the Dead: crocodile head, lion's mane and forelegs, a hippopotamus's hindquarters,
    crouched and eager, facing the scale (left)."""
    def Q(pts):
        return place(pts, x, base, s)
    out = []
    hind = Q([(4, -60), (36, -66), (56, -54), (62, -30), (58, -4), (50, 0, 1), (28, 0, 1), (26, -14), (10, -18), (0, -30)])
    out.append(egy_paint(P, hind, "#B05A3A", seed=seed))
    fore = Q([(-14, -64), (8, -70), (12, -40), (4, -20), (-2, -4), (-4, 0, 1), (-24, 0, 1), (-22, -6), (-18, -36), (-20, -56)])
    out.append(egy_paint(P, fore, "#D8A848", seed=seed + 1))
    for k in range(3):
        a_, b_ = Q([(-20 + k * 4, -2), (-21 + k * 4, 0)])
    mane = Q([(-28, -66), (-20, -92), (0, -100), (16, -88), (18, -66), (6, -54), (-16, -50)])
    out.append(egy_paint(P, mane, "#C88A30", seed=seed + 2))
    for k in range(6):
        out.append(K.stroke_line(Q([(-18 + k * 6, -94 + k), (-16 + k * 5, -58)]), "#2A6AA8", 1.4 * s, 0.8))
    head = Q([(-70, -84, 1), (-40, -92), (-24, -96), (-16, -98), (-10, -90), (-14, -80), (-30, -76), (-50, -74), (-68, -78)])
    out.append(egy_paint(P, head, "#4A8A5A", seed=seed + 3))
    for k in range(7):
        a_ = Q([(-64 + k * 6, -80)])[0]
        out.append(K.path(lp([(a_[0], a_[1]), (a_[0] + 2 * s, a_[1]), (a_[0] + 1 * s, a_[1] + 3 * s)]), "#F6F0E0"))
    ex, ey = Q([(-22, -91)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="#F6F0E0" stroke="{EGY_LINE}" stroke-width="0.8"/><circle cx="{ex - 0.5:.1f}" cy="{ey:.1f}" r="{1.2 * s:.1f}" fill="#000"/>')
    return "".join(out)


def baboon_thoth(P, x, base, s, seed):
    """The baboon of Thoth squatting on the top of the balance, as on the papyri."""
    def Q(pts):
        return place(pts, x, base, s)
    body = Q([(-10, 0, 1), (-12, -10), (-10, -20), (-4, -28), (4, -30), (12, -26), (16, -18), (18, -8), (16, 0, 1)])
    head = Q([(-16, -30), (-14, -40), (-4, -46), (6, -42), (8, -34), (2, -28), (-8, -26)])
    out = [egy_paint(P, body, "#7AA88A", seed=seed), egy_paint(P, head, "#9AC0A8", seed=seed + 1)]
    out.append(egy_paint(P, Q([(-22, -34), (-14, -40), (-10, -32), (-18, -28)]), "#C8A080", seed=seed + 2))
    out.append(f'<circle cx="{Q([(-10, -37)])[0][0]:.1f}" cy="{Q([(-10, -37)])[0][1]:.1f}" r="{1.2 * s:.1f}" fill="#000"/>')
    out.append(K.stroke_line(Q([(-6, -16), (-14, -12), (-16, -6)]), EGY_LINE, 1.0, 0.8))
    return "".join(out)


@plate("the-weighing-of-the-heart")
def the_weighing_of_the_heart_p():
    P = Plate("myp-wh")
    rnd = random.Random(3)
    art = [papyrus_sheet(P, 4)]
    # border bands top and bottom: red, blue, green and the black register lines
    for y in (54, 446):
        art.append(K.stroke_line([(40, y), (560, y)], "#1E140C", 1.6, 0.9, smooth=False))
    for k in range(26):
        x = 44 + k * 20
        art.append(K.path(lp([(x, 44), (x + 9, 44), (x + 9, 52), (x, 52)]), ["#9A2A1A", "#2A5A9A", "#3A7A5A"][k % 3], 0.85))
    # columns of text above the scene, as in the papyrus of Hunefer
    for i, x in enumerate(range(62, 548, 22)):
        art.append(K.stroke_line([(x + 11, 62), (x + 11, 150)], "#1E140C", 0.6, 0.6, smooth=False))
        art.append(hiero_column(10 + i, x, 66, 148, 0.86, red_every=5 if i % 4 == 0 else 0))
    art.append(K.stroke_line([(40, 154), (560, 154)], "#1E140C", 1.2, 0.8, smooth=False))
    # the balance: post with lotus top, crossbeam, cords, pans; the baboon of Thoth on top
    post_x = 312
    art.append(egy_paint(P, [(post_x - 5, 440, 1), (post_x - 4, 196), (post_x + 4, 196), (post_x + 5, 440, 1)], "#2A6A9A", w=1.2, seed=2))
    for y in range(206, 436, 14):
        art.append(K.stroke_line([(post_x - 4, y), (post_x + 4, y)], "#C8A040", 2, 0.9, smooth=False))
    art.append(egy_paint(P, [(post_x - 26, 446, 1), (post_x - 18, 432, 1), (post_x + 18, 432, 1), (post_x + 26, 446, 1)], "#C8A040", w=1.2, seed=3))
    beam_y = 214
    art.append(egy_paint(P, [(post_x - 104, beam_y - 3, 1), (post_x + 104, beam_y - 3, 1), (post_x + 104, beam_y + 3, 1), (post_x - 104, beam_y + 3, 1)], "#C8A040", w=1.0, seed=4))
    art.append(baboon_thoth(P, post_x + 2, beam_y - 4, 1.1, 5))
    for sg in (-1, 1):
        px = post_x + sg * 96
        for dx in (-22, 22):
            art.append(K.stroke_line([(px, beam_y + 3), (px + dx, 316)], "#1E140C", 1.0, 0.85, smooth=False))
        art.append(egy_paint(P, [(px - 30, 316), (px + 30, 316), (px + 22, 326), (px - 22, 326)], "#C8A040", w=1.2, seed=6 + sg))
    # the heart (ib, a little jar) on the left pan, the feather of Ma'at on the right
    hx = post_x - 96
    art.append(egy_paint(P, [(hx - 9, 314), (hx - 11, 300), (hx - 7, 290), (hx - 10, 286), (hx - 4, 282), (hx + 4, 282), (hx + 10, 286), (hx + 7, 290), (hx + 11, 300), (hx + 9, 314)],
                         "#A83A2A", seed=7))
    fx = post_x + 96
    feather = [(fx - 2, 314), (fx - 6, 290), (fx - 8, 266), (fx - 4, 250), (fx + 6, 246), (fx + 8, 256), (fx + 2, 262), (fx + 2, 290), (fx + 2, 314)]
    art.append(egy_paint(P, feather, "#F6F0E0", seed=8))
    art.append(K.stroke_line([(fx, 314), (fx - 2, 262), (fx + 2, 250)], "#1E140C", 0.8, 0.8))
    # the plumb line Anubis watches
    art.append(K.stroke_line([(post_x, beam_y + 3), (post_x, 300)], "#1E140C", 0.9, 0.9, smooth=False))
    art.append(egy_paint(P, [(post_x - 4, 300), (post_x + 4, 300), (post_x, 312)], "#C8A040", w=0.8, seed=9))
    # Anubis at the scale, steadying the plummet
    art.append(egy_figure(P, 96, 440, 10.6, head="jackal", skin="#16120E",
                          arms=dict(near=((2.4, -15.8), (5.6, -13.6), (8.6, -15.6)), far=((-2.4, -15.8), (0.8, -12.8), (4.0, -11.6))), seed=11))
    # Ammit on her pedestal, waiting
    art.append(egy_paint(P, [(442, 446, 1), (442, 404, 1), (546, 404, 1), (546, 446, 1)], "#2A6A9A", w=1.2, seed=12))
    for k in range(7):
        art.append(K.stroke_line([(446 + k * 15, 404), (446 + k * 15, 446)], "#C8A040", 1.4, 0.7, smooth=False))
    art.append(ammit(P, 504, 404, 1.12, 13))
    text = [tx(300, 500, "The Weighing of the Heart", DMS, 40, "#1E140C", max_w=470),
            tx(300, 530, "EGYPTIAN · AS LIGHT AS A FEATHER", CINZEL, 17, "#9A2A1A", ls=2.5, max_w=440)]
    return P.render(art, text, seed=111, edge=1.2, bristle=0.3, grain=0.24)


# ================================================================ the labyrinth — Daedalus's maze on Crete at dusk, Ariadne's thread (plate)
class Cam3:
    """A simple pinhole camera looking north and down at the ground plane (x east, y north, z up)."""

    def __init__(self, dist, height, pitch_deg, focal, cx, cy):
        self.D, self.H, self.F, self.cx, self.cy = dist, height, focal, cx, cy
        p = math.radians(pitch_deg)
        self.f = (0, math.cos(p), -math.sin(p))
        self.u = (0, math.sin(p), math.cos(p))

    def __call__(self, x, y, z=0.0):
        d = (x, y + self.D, z - self.H)
        depth = d[1] * self.f[1] + d[2] * self.f[2]
        sx = d[0] / depth * self.F
        sy = -(d[1] * self.u[1] + d[2] * self.u[2]) / depth * self.F
        return (self.cx + sx, self.cy + sy)

    def depth(self, x, y, z=0.0):
        return (y + self.D) * self.f[1] + (z - self.H) * self.f[2]


@plate("the-labyrinth")
def the_labyrinth_p():
    P = Plate("myp-lb")
    rnd = random.Random(5)
    nx_, ny_ = 9, 9
    open_, W, H = make_maze(nx_, ny_, 21, court=(3, 3, 5, 5))
    cam = Cam3(dist=19.9, height=8.2, pitch_deg=30, focal=520, cx=300, cy=470)
    s = 1.0
    ox, oy = -W / 2, -H / 2
    wall_h = 0.6
    sun = (-1.0, 0.25, 0.42)       # toward the low western sun
    # sky at dusk, the sea and the mountains of Crete on the horizon
    hy = cam(0, 2000, 0)[1]
    art = [K.sky_grad(P, [(0, "#1E2448"), (0.45, "#6A4A6A"), (0.75, "#E8906A"), (1, "#FFD49A")], 0, hy + 6)]
    art.append(K.sky_wash(P, 3, ["#8A5A7A", "#3A3A68", "#F2A070"], 10, (-40, -40, 640, hy), (80, 160), (0.12, 0.25), 30))
    art.append(screen(glow(P, 40, hy - 6, 240, "#FFD890", 0.6)))
    art.append(K.strata(P, 4, hy - 50, -40, 640, 8, ("#FFD8B0", "#B06A78", "#5A3A60"), L=(-1, 0.3), n=6, op=0.85))
    ida = K.ridge(6, -20, 640, hy - 8, hy - 40, 26, 16, 0.5, peaks=[(430, hy - 66, 170)])
    art.append(form(P, sp(ida), ("#B08AA0", "#6A5078", "#2E2448"), (-1, -0.3), K.bbox(ida), core=0.3, lit=0.4, sd=8))
    art.append(K.haze(P, hy - 70, hy + 6, "#F2B890", 0.0, 0.6))
    # the sea of Crete in a thin bright line under the mountains, the sun's path on it
    art.append(K.path(lp([(-20, hy - 10), (620, hy - 10), (620, hy + 4), (-20, hy + 4)]), "#F2B888"))
    art.append(screen(glow(P, 60, hy - 4, 120, "#FFE8B0", 0.6, ry=10)))
    # the ground of the plain: golden grass in the last light, falling into shadow toward the viewer
    ground = [(-20, hy + 2), (620, hy + 2), (620, 620), (-20, 620)]
    art.append(K.path(lp(ground), P.lin([(0, "#D8A868"), (0.2, "#A87A48"), (0.6, "#6A4A2A"), (1, "#2A1A10")], 0, hy, 0, 600, "userSpaceOnUse")))
    art.append(f'<rect x="-20" y="{hy}" width="640" height="{620 - hy}" fill="#3A2010" opacity="0.25" {P.mottle(0.02, 0.6, 11)}/>')
    # the palace of Minos at Knossos far off on its low hill: terraces, red columns, horns of consecration
    kx, ky = 470, hy + 26
    art.append(K.path(sp([(kx - 90, ky + 16), (kx - 60, ky - 4), (kx + 60, ky - 6), (kx + 96, ky + 16)]), "#8A6A4A"))
    for k, (x0, w, h) in enumerate(((kx - 60, 50, 14), (kx - 10, 60, 20), (kx + 50, 34, 12), (kx - 40, 40, 8))):
        art.append(K.path(lp([(x0, ky), (x0 + w, ky), (x0 + w, ky - h), (x0, ky - h)]), "#E8C8A0" if k % 2 else "#D8B088"))
        art.append(K.path(lp([(x0, ky - h), (x0 + w, ky - h), (x0 + w, ky - h + 2), (x0, ky - h + 2)]), "#6A3A2A"))
        for c in range(int(w / 9)):
            art.append(K.path(lp([(x0 + 4 + c * 9, ky - h + 3), (x0 + 6 + c * 9, ky - h + 3), (x0 + 6 + c * 9, ky - 1), (x0 + 4 + c * 9, ky - 1)]), "#A8302A"))
    art.append(K.haze(P, hy - 20, hy + 40, "#F2B890", 0.5, 0.0))
    # olive groves on the plain: rows of round grey-green crowns with long shadows
    for row in range(5):
        wy = 22 - row * 2.6
        for k in range(14):
            wx = -16 + k * 2.6 + (1.3 if row % 2 else 0) + rnd.uniform(-0.4, 0.4)
            if abs(wx) < 11.5 and wy < 11:
                continue
            bx, by = cam(wx, wy, 0)
            tx_, ty_ = cam(wx, wy, 1.0)
            r = (by - ty_) * 0.5 * rnd.uniform(0.8, 1.2)
            if r < 1:
                continue
            art.append(f'<ellipse cx="{bx + r * 1.2:.1f}" cy="{by:.1f}" rx="{r * 1.5:.1f}" ry="{r * 0.35:.1f}" fill="#2A1A10" opacity="0.4"/>')
            art.append(K.path(sp(K.wobble(ellipse(bx, by - r * 0.9, r * 1.1, r * 0.85, 10), k + row * 20, r * 0.18)), "#4A5236"))
            art.append(K.path(sp(K.wobble(ellipse(bx - r * 0.35, by - r * 1.15, r * 0.6, r * 0.45, 8), k + row * 30, r * 0.1)), "#B8B080", 0.75))
    # cypresses dotting the plain
    for (wx, wy) in ((-9, 9), (9.5, 10), (-11, -2), (11.5, 3), (-6, 14), (7, 16)):
        bx, by = cam(wx, wy, 0)
        tx_, ty_ = cam(wx, wy, 3.2)
        h = by - ty_
        pts = [(bx - h * 0.08, by), (bx - h * 0.12, by - h * 0.4), (bx - h * 0.06, by - h * 0.85), (tx_, ty_, 1), (bx + h * 0.06, by - h * 0.85),
               (bx + h * 0.12, by - h * 0.4), (bx + h * 0.08, by)]
        art.append(K.cast_shadow(P, bx + h * 0.5, by + 2, h * 0.5, h * 0.06, "#1A0E06", 0.45))
        art.append(form(P, sp(pts), ("#7A8A50", "#24341E", "#0A1008"), (-1, -0.2), K.bbox(pts), core=0.6, lit=0.4, rim_col="#FFC880", rim_d=1.6))
    # the maze floor: beaten earth
    corners = [cam(ox - 0.6, oy - 0.6), cam(ox + W + 0.6, oy - 0.6), cam(ox + W + 0.6, oy + H + 0.6), cam(ox - 0.6, oy + H + 0.6)]
    art.append(K.path(lp(corners), "#C89A68"))
    art.append(f'<path d="{lp(corners)}" fill="#6A4A2A" opacity="0.5" {P.mottle(0.03, 0.6, 3)}/>')
    open_.add((1, H - 1))

    def wpos(gx, gy):
        return ox + gx, oy + (H - 1 - gy)
    walls = set((gx, gy) for gx in range(W) for gy in range(H) if (gx, gy) not in open_)
    # long dusk shadows cast by the walls across the floor (eastward)
    shadows = []
    for gx, gy in walls:
        x0, y0 = wpos(gx, gy)
        k = wall_h / sun[2]
        dx, dy = -sun[0] * k, -sun[1] * k
        base = [(x0, y0), (x0 + 1, y0), (x0 + 1, y0 + 1), (x0, y0 + 1)]
        top = [(x + dx, y + dy) for x, y in base]
        hull = [base[0], base[1], top[1], top[2], base[2], base[3]] if dx > 0 else [base[0], top[0], top[1], base[1], base[2], top[2], top[3], base[3]]
        pts = [base[0], base[3], top[3], top[2], top[1], base[1]]
        shadows.append(f'<path d="{lp([cam(x, y, 0) for x, y in pts])}"/>')
    art.append(f'<g fill="#2A1428" opacity="0.45" {P.blur(0.8)}>{"".join(shadows)}</g>')
    # Ariadne's thread, from the gate to the heart of the maze
    gate = (1, H - 1)
    goal = (2 * 4 + 1, 2 * 4 + 1)
    path_ = maze_path(open_, gate, goal)
    thread = [cam(wpos(gx, gy)[0] + 0.5 + rnd.uniform(-0.12, 0.12), wpos(gx, gy)[1] + 0.5 + rnd.uniform(-0.12, 0.12), 0.03) for gx, gy in path_]
    thread = [cam(ox + 1.5, oy - 1.6, 0.03), cam(ox + 1.4, oy - 0.6, 0.03)] + thread
    # NOTE maze rows: lattice gy counts from the far side; flip so the gate faces the viewer
    # the walls, painted back to front: lit tops, west faces in the sun, south faces in shade
    blocks = sorted(walls, key=lambda c: (-wpos(*c)[1], abs(wpos(*c)[0] + 0.5)))
    faces = []
    for gx, gy in blocks:
        x0, y0 = wpos(gx, gy)
        b = [(x0, y0), (x0 + 1, y0), (x0 + 1, y0 + 1), (x0, y0 + 1)]
        top = [cam(x, y, wall_h) for x, y in b]
        bot = [cam(x, y, 0) for x, y in b]
        # south face (toward viewer)
        tint = rnd.uniform(-0.08, 0.08)
        def tc(c):
            return mix(c, "#FFFFFF", tint) if tint > 0 else mix(c, "#000000", -tint)
        if (gx, gy + 1) not in walls:
            faces.append(f'<path d="{lp([bot[0], bot[1], top[1], top[0]])}" fill="{tc("#4E3024")}"/>')
            for k in (0.33, 0.66):
                a_, b_ = K.lerp2(bot[0], top[0], k), K.lerp2(bot[1], top[1], k)
                faces.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#2A1810" stroke-width="0.8" opacity="0.6"/>')
        if x0 > 0.0 and (gx - 1, gy) not in walls:
            faces.append(f'<path d="{lp([bot[0], bot[3], top[3], top[0]])}" fill="{tc("#F2A462")}"/>')
            for k in (0.33, 0.66):
                a_, b_ = K.lerp2(bot[0], top[0], k), K.lerp2(bot[3], top[3], k)
                faces.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#8A5030" stroke-width="0.8" opacity="0.6"/>')
        if x0 + 1 < 0.0 and (gx + 1, gy) not in walls:
            faces.append(f'<path d="{lp([bot[1], bot[2], top[2], top[1]])}" fill="{tc("#4A2E2C")}"/>')
        faces.append(f'<path d="{lp(top)}" fill="{tc("#F8D49C")}"/>')
    # draw the thread under the walls that stand in front of it: simplest is thread first, then walls
    art.append(K.stroke_line(thread, "#5A0606", 4.4, 0.9, smooth=False))
    art.append(K.stroke_line(thread, "#F0302A", 2.6, 1.0, smooth=False))
    art.append(screen(K.stroke_line(thread, "#FF6A4A", 8, 0.45, smooth=False, extra=f' {P.blur(3)}')))
    art.append(f'<g {P.rough(2.2, 0.09, 3)}>{"".join(faces)}</g>')
    # stone courses on the sunlit faces and some texture over the whole maze
    art.append(f'<path d="{lp(corners)}" fill="#3A2010" opacity="0.18" {P.mottle(0.08, 0.7, 7)}/>')
    # the heart of the maze: a torch-lit court, a horned shadow on the far wall
    cx_, cy_ = cam(ox + 9.5 - W / 2 + W / 2, oy + H / 2, 0)
    cxx, cyy = cam(0, 0, 0.2)
    art.append(screen(glow(P, cxx, cyy, 70, "#FFA040", 0.7)))
    art.append(K.flame(P, cxx - 14, cyy + 2, 12, 4, n=3, w=0.3, sd=0.6))
    art.append(K.flame(P, cxx + 14, cyy + 2, 12, 5, n=3, w=0.3, sd=0.6))
    art.append(K.vignette(P, "#0A0610", 0.55, 0.55))
    art.append(K.text_scrim(P, 30, 150, "#140A1A", 0.55, up=False))
    text = [gilt(P, 300, 98, "The Labyrinth", SERIF_IT, 62, ls=0.5, max_w=420, seed=9, deboss="#000000", dop=0.8),
            tx(300, 128, "GREEK · FOLLOW ARIADNE’S THREAD", CINZEL, 17, "#FFF0E0", ls=2.5, max_w=440)]
    return P.render(art, text, seed=121, edge=1.8, bristle=0.4, grain=0.2)


# ================================================================ the golden fleece — on the oak in the grove of Ares, the sleepless dragon (plate)
def golden_fleece(P, cx, top, s, seed):
    """The fleece of the golden ram hung by the head from a branch: the curled horns, the long pelt falling in heavy
    locks with the legs hanging at the corners, every lock of wool catching the light."""
    rnd = random.Random(seed)

    def Q(pts):
        return place(pts, cx, top, s)
    out = [screen(glow(P, cx, top + 90 * s, 170 * s, "#FFD060", 0.55))]
    pelt_l = [(-16, 12), (-34, 28), (-62, 34), (-84, 46, 0.6), (-66, 52), (-56, 76), (-62, 112), (-68, 150), (-60, 184), (-74, 214), (-70, 236, 0.6),
              (-54, 216), (-36, 212), (-20, 226), (-4, 218), (6, 240, 0.6), (16, 216), (34, 214), (52, 220), (66, 238, 0.6), (64, 206), (60, 180),
              (68, 146), (64, 108), (56, 76), (64, 52), (86, 42, 0.6), (64, 32), (34, 26), (16, 12)]
    pelt = Q(pelt_l)
    ins = K.inside_poly(pelt_l)
    locks = []
    for k in range(320):
        x, y = rnd.uniform(-80, 80), rnd.uniform(20, 236)
        if not ins(x, y):
            continue
        r = rnd.uniform(3.5, 7)
        c = Q([(x, y)])[0]
        spiral = [(c[0] + math.cos(a) * r * s * (1 - a / 12), c[1] + math.sin(a) * r * s * 0.8 * (1 - a / 12)) for a in [i * 0.6 for i in range(14)]]
        locks.append(K.stroke_line(spiral, rnd.choice(["#FFF6C0", "#B8801A", "#FFE070"]), rnd.uniform(1.2, 2.2) * s, rnd.uniform(0.5, 0.9)))
    sheen = [soft(P, sp(Q(ellipse(-20, 100, 26, 70, 14))), "#FFF8D0", 0.6, 12 * s), soft(P, sp(Q(ellipse(40, 150, 30, 60, 14))), "#5A2A04", 0.5, 14 * s)]
    out.append(f'<g {P.rough(5 * s, 0.09, seed)}>' + form(P, sp(pelt), ("#FFF2A0", "#D89A28", "#5A2A04"), (-0.6, -0.8), K.bbox(pelt), core=0.55, lit=0.6,
                                                         extra=sheen + locks, edge="#2A1004", edge_op=0.7, rim_col="#FFF8D0", rim_d=2) + "</g>")
    # the ram's head at the top, hanging muzzle-down, the horns spiralling forward round the ears
    head = Q([(-13, -16), (13, -16), (15, -2), (11, 14), (8, 28), (0, 34), (-8, 28), (-11, 14), (-15, -2)])
    out.append(form(P, sp(head), ("#FFF2A0", "#C88A28", "#4A2604"), (-0.6, -0.8), K.bbox(head), core=0.55, lit=0.6, edge="#2A1004", edge_op=0.7,
                    extra=[soft(P, sp(Q(ellipse(-4, 0, 6, 14, 10))), "#FFF8D0", 0.6, 3 * s)]))
    for sg in (-1, 1):
        ex, ey = Q([(sg * 10, 4)])[0]
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{1.8 * s:.1f}" ry="{1.2 * s:.1f}" fill="#2A1004"/>')
        nx_, ny_ = Q([(sg * 3, 30)])[0]
        out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="{1.4 * s:.1f}" ry="{1.0 * s:.1f}" fill="#3A1A04" opacity="0.8"/>')
        spiral = [(sg * (12 + 16 * math.cos(a) * (1 - a / 14)), -6 + 16 * math.sin(a) * (1 - a / 14) * 0.95) for a in [-2.2 + i * 0.45 for i in range(16)]]
        sp_ = Q(spiral if sg > 0 else [(x, y) for x, y in spiral])
        out.append(K.taper(sp_, 10 * s, 3 * s, "#B07A22"))
        out.append(K.stroke_line(sp_[:10], "#FFF2C0", 1.6 * s, 0.6))
        for k in range(1, len(sp_) - 2, 2):
            out.append(f'<circle cx="{sp_[k][0]:.1f}" cy="{sp_[k][1]:.1f}" r="{(5 - k * 0.25) * s:.1f}" fill="none" stroke="#5A3008" stroke-width="0.8" opacity="0.5"/>')
    out.append(K.embers(seed, cx, top + 110 * s, 80 * s, 150 * s, 30, cols=("#FFF6C0", "#FFE070"), r=(0.6, 1.6)))
    return "".join(out)


def serpent_coil(P, spine, ws, seed, pal=("#7AB088", "#1E4A34", "#04120A"), belly="#C8B878", crest="#C8302A", rim_col=None, rim_src=None):
    """A section of the dragon's body: scaled, with a pale ventral band and a crest of spines along the back."""
    pts = K.limb(spine, ws, ws, n=5)
    d = sp(pts)
    A = K.catmull(spine, 5)
    W = K.interp_list(ws, 5)
    rnd = random.Random(seed)
    sc = []
    for i in range(1, len(A) - 1, 2):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        for j in (-0.5, 0, 0.5):
            cx, cy = x - ty_ * W[i] * j, y + tx_ * W[i] * j
            r = W[i] * 0.3
            sc.append(f'<path d="M {cx - ty_ * r:.1f} {cy + tx_ * r:.1f} Q {cx + tx_ * r * 1.2:.1f} {cy + ty_ * r * 1.2:.1f} {cx + ty_ * r:.1f} {cy - tx_ * r:.1f}" '
                      f'stroke="{rnd.choice([pal[0], pal[2]])}" stroke-width="0.9" fill="none" opacity="0.6"/>')
    bel = K.limb(spine, [-w * 0.4 for w in ws], [w * 0.9 for w in ws], n=5)
    ex = [soft(P, sp(bel), belly, 0.55, 2)] + sc
    for i in range(len(bel) // 2):
        pass
    return form(P, d, pal, (-0.5, -0.8), K.bbox(pts), core=0.55, lit=0.5, extra=ex, edge="#000000", edge_op=0.6, rim_col=rim_col, rim_d=2, rim_src=rim_src)


@plate("the-golden-fleece")
def the_golden_fleece_p():
    P = Plate("myp-gf")
    rnd = random.Random(9)
    # the grove: deep green dark, a gap of evening light behind where the river runs and the Argo waits
    art = [K.sky_grad(P, [(0, "#0A140E"), (0.5, "#1A2A1C"), (1, "#0A100A")])]
    gap = [(330, 200), (420, 180), (520, 190), (600, 200), (600, 420), (330, 420)]
    art.append(f'<g {P.clip(f"<path d=\"{sp(gap)}\"/>")}>' + K.sky_grad(P, [(0, "#C8B888"), (0.5, "#F2C880"), (1, "#8A7A50")], 180, 420)
               + screen(glow(P, 470, 300, 160, "#FFE8B0", 0.6)) + "</g>")
    art.append(K.path(lp([(330, 330), (620, 330), (620, 350), (330, 350)]), "#E8D0A0", 0.6))
    # the Argo's sail and mast, far off on the Phasis
    art.append(K.path(lp([(486, 326), (530, 326), (524, 334), (492, 334)]), "#2A1A10", 0.8))
    art.append(K.stroke_line([(508, 326), (508, 290)], "#2A1A10", 1.6, 0.8))
    art.append(K.path(sp([(496, 296), (520, 296), (522, 316), (494, 316)]), "#E8C8A0", 0.8))
    # far trunks in the haze
    for x in (360, 400, 560, 590):
        art.append(K.path(lp([(x - 6, 420), (x - 4, 180), (x + 4, 180), (x + 6, 420)]), "#3A4A30", 0.6))
    art.append(K.haze(P, 160, 440, "#C8B888", 0.0, 0.25))
    # the canopy: dark masses of oak foliage, edges catching the evening light
    for (cx, cy, rx, ry, sd_) in ((100, 80, 180, 110, 1), (420, 60, 220, 100, 2), (560, 160, 120, 90, 3), (40, 230, 100, 80, 4)):
        art.append(f'<g {P.rough(14, 0.05, sd_)}>' + K.foliage(P, sd_ * 7, cx, cy, rx, ry, ("#4A6A3A", "#16261A", "#040804"), L=(0.7, 0.6), n=40, leaf=(6, 12), dabs=320, sd=2.6) + "</g>")
    # the ground: roots, ferns, the fallen leaves
    ground = [(-20, 600), (-20, 470), (140, 452), (300, 444), (460, 452), (620, 440), (620, 600)]
    art.append(form(P, sp(ground), ("#6A5A30", "#2A2414", "#0A0804"), (0.6, -0.8), K.bbox(ground), core=0.4, lit=0.3, sd=10))
    art.append(K.grass(4, -10, 610, 446, 600, ["#3A4A20", "#6A6A30", "#2A2A10", "#8A7A3A"], 300, (6, 18)))
    # the great oak: a twisted trunk, buttress roots, a bough reaching right where the fleece hangs
    trunk = [(120, 600), (130, 520), (150, 470), (156, 400), (150, 330), (160, 260), (170, 200), (150, 150), (120, 110), (180, 130), (210, 170),
             (250, 176), (330, 150), (380, 140), (430, 146), (434, 160), (380, 162), (320, 182), (270, 208), (236, 230), (226, 300), (230, 380),
             (242, 450), (270, 500), (300, 540), (280, 600)]
    bark = [K.stroke_line([(x + rnd.uniform(-3, 3), y) for x, y in [(140 + k * 9 + rnd.uniform(-4, 4), yy) for yy in range(210, 590, 40)]], "#0A0604", 2, 0.4)
            for k in range(10)]
    art.append(form(P, sp(trunk), ("#8A7A60", "#3A2E22", "#0C0A06"), (0.8, -0.6), K.bbox(trunk), core=0.6, lit=0.4, extra=bark,
                    edge="#000000", edge_op=0.6, rim_col="#FFD890", rim_d=2.2, rim_src=(470, 300, 360)))
    # the dragon coiled about the trunk: coils behind first...
    # ...then the coils wrapping the trunk: each band crosses the front of the trunk and vanishes behind it
    rnd2 = random.Random(5)
    for k, (yl, yr, w) in enumerate(((548, 520, 30), (470, 446, 27), (392, 370, 24), (318, 300, 21))):
        xl = 128 + k * 6
        xr = 250 - k * 4
        mx_ = (xl + xr) / 2
        band = [(xl - 4, yl - 10), (xl + 8, yl + 2), (mx_ - 20, yl + 8), (mx_ + 20, (yl + yr) / 2 + 6), (xr - 8, yr), (xr + 4, yr - 12)]
        ws_ = [w * 0.5, w * 0.85, w, w, w * 0.85, w * 0.5]
        art.append(serpent_coil(P, band, ws_, 3 + k, rim_col="#FFD890", rim_src=(470, 300, 380)))
    # the neck rising from the top coil and curving out toward the fleece
    neck = [(238, 300), (250, 270), (240, 236), (252, 208), (282, 196), (300, 204)]
    art.append(serpent_coil(P, neck, [21, 19, 17, 16, 15, 14], 9, rim_col="#FFD890", rim_src=(470, 300, 380)))
    # head of the drakon: a long jaw, a crest, the eye that never closes
    hx, hy = 298, 206
    head = place([(0, -10), (18, -16), (36, -14), (54, -8), (62, -2, 1), (52, 2), (40, 6), (54, 10, 1), (36, 12), (16, 12), (0, 10)], hx, hy, 1.15, False, -12)
    art.append(form(P, sp(head), ("#8AC098", "#1E4A34", "#04120A"), (-0.5, -0.8), K.bbox(head), core=0.5, lit=0.5, edge="#000000", edge_op=0.6,
                    rim_col="#FFD890", rim_d=1.8))
    for k in range(6):
        b_ = place([(4 + k * 6, -12)], hx, hy, 1.15, False, -12)[0]
        t_ = place([(0 + k * 6, -24 - (6 - k) * 1.2)], hx, hy, 1.15, False, -12)[0]
        art.append(K.path(lp([(b_[0] - 3, b_[1]), t_, (b_[0] + 3, b_[1])]), "#C8302A", 0.9))
    ex, ey = place([(26, -6)], hx, hy, 1.15, False, -12)[0]
    art.append(screen(glow(P, ex, ey, 14, "#FFE040", 0.8)))
    art.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="3.6" ry="2.6" fill="#FFE040"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="1" ry="2.4" fill="#000"/>')
    for k in range(4):
        a_ = place([(38 + k * 4, 6)], hx, hy, 1.15, False, -12)[0]
        art.append(K.path(lp([(a_[0], a_[1]), (a_[0] + 2, a_[1]), (a_[0] + 1, a_[1] + 4)]), "#F6F0E0"))
    # the fleece, hung from the bough, lit by the last of the day
    art.append(K.stroke_line([(382, 150), (382, 170)], "#2A1A10", 2, 0.9))
    art.append(golden_fleece(P, 382, 182, 0.92, 7))
    art.append(K.vignette(P, "#020402", 0.55, 0.55))
    art.append(K.text_scrim(P, 470, 600, "#020402", 0.75))
    text = [gilt(P, 300, 508, "The Golden Fleece", SERIF_IT, 54, ls=0.5, max_w=460, seed=4, deboss="#000000", dop=0.85),
            tx(300, 536, "GREEK · GUARDED BY A SLEEPLESS DRAGON", CINZEL, 17, "#F2E8C8", ls=2, max_w=460)]
    return P.render(art, text, seed=131, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ a galloping horse with real anatomy (shared by sleipnir and the sea-horses)
HORSE_BODY_L = [(-150, -46, 0.5), (-144, -58), (-122, -82), (-102, -98), (-92, -104), (-88, -110), (-84, -121, 1), (-76, -106), (-66, -100),
                (-46, -86), (-26, -66), (-6, -50), (12, -44), (28, -40), (50, -38), (72, -40), (92, -45), (106, -38), (112, -26), (116, -8), (114, 14),
                (110, 34), (106, 52), (96, 62), (84, 56), (76, 44), (64, 42), (40, 44), (12, 44), (-14, 42), (-30, 38), (-38, 44), (-50, 46), (-52, 30),
                (-56, 2), (-62, -16), (-68, -34), (-80, -52), (-90, -62),
                (-100, -62), (-110, -56), (-124, -44), (-136, -38), (-145, -40)]
GALLOP_LEGS = {
    "fore_near": ([(-44, 36), (-64, 46), (-84, 54), (-106, 58), (-118, 60), (-130, 68)], [17, 13, 8, 7, 8.5, 6], [17, 12, 8, 7, 8.5, 6]),
    "fore_far": ([(-48, 30), (-70, 36), (-92, 40), (-112, 38), (-124, 40), (-136, 46)], [16, 12, 7.5, 6.5, 8, 5.5], [16, 11, 7.5, 6.5, 8, 5.5]),
    "hind_near": ([(98, 52), (114, 62), (130, 70), (146, 74), (160, 78), (172, 84)], [14, 10, 8, 7, 8.5, 6], [16, 11, 8.5, 7, 8.5, 6]),
    "hind_far": ([(88, 48), (106, 56), (122, 62), (138, 64), (152, 66), (164, 70)], [13, 10, 7.5, 6.5, 8, 5.5], [15, 10, 8, 6.5, 8, 5.5]),
}


def horse_g(P, ox, oy, s, seed, pal=("#FFFFFF", "#C8CAD0", "#3A3C48"), mane=("#FFFFFF", "#D8DAE2", "#6A6E80"), L=(-0.4, -0.9), legs=None,
            rim_col=None, rim_src=None, dapple=False, flip=False, extra_legs=(), tail=True, hoof="#2A2422"):
    """A horse in the flying gallop (the pose of the old masters' cavalry pictures): head and neck stretched forward,
    forelegs reaching, hind legs thrown back. Built from an anatomical contour (poll, crest, withers, back, croup,
    buttock, stifle, girth, elbow, point of shoulder, throatlatch, jowl) and jointed legs (forearm, knee, cannon,
    fetlock, pastern, hoof / gaskin, hock). Faces left. (ox, oy) = centre of the barrel; ~330 * s long."""
    def Q(pts):
        return place(pts, ox, oy, s, flip)
    rnd = random.Random(seed)
    lx, ly = K.unit(*L)
    legs = legs or GALLOP_LEGS
    out = []
    dark_leg = (mix(pal[0], pal[1], 0.5), mix(pal[1], pal[2], 0.35), pal[2])

    def leg(axis, wl, wr, far):
        q = Q(K.limb(axis, wl, wr, n=5))
        lp_ = dark_leg if far else pal
        shade = soft(P, sp(Q(K.limb_shade(axis, wl, wr, (lx, ly)))), pal[2], 0.6, 2 * s)
        body = form(P, sp(q), lp_, L, K.bbox(q), core=0.3, lit=0.4 if not far else 0.15, extra=[shade], edge="#000000", edge_op=0.5)
        hx, hy = axis[-1]
        a, b = axis[-2], axis[-1]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        hf = Q(place([(-2, -6), (8, -7), (12, 6, 1), (-4, 6, 1)], hx, hy, 1, False, ang - 90 + 90))
        return body + K.path(sp(hf), hoof)
    # tail streaming back
    if tail:
        for k in range(9):
            sp0 = (110, -26)
            ctrl = [(sp0[0] + 20, sp0[1] - 6 + k), (sp0[0] + 60, sp0[1] - 10 + k * 3), (sp0[0] + 100 + rnd.uniform(-8, 8), sp0[1] - 4 + k * 5 + rnd.uniform(-6, 6))]
            out.append(K.taper(Q(K.catmull([sp0] + ctrl, 5)), 6 * s, 0.6, rnd.choice(mane), 0.85))
    for name in ("fore_far", "hind_far"):
        out.append(leg(*legs[name], True))
    for ax_, wl_, wr_ in extra_legs:
        out.append(leg(ax_, wl_, wr_, True))
    body = Q(HORSE_BODY_L)
    ex = [soft(P, sp(Q(ellipse(-20, -4, 34, 26, 14))), pal[0], 0.5, 8 * s),          # shoulder catching the light
          soft(P, sp(Q(ellipse(86, -8, 24, 28, 14))), pal[0], 0.45, 8 * s),          # the round of the haunch
          soft(P, sp(Q([(0, 34), (84, 34), (84, 46), (0, 46)])), pal[2], 0.6, 6 * s),    # belly in shadow
          soft(P, sp(Q(ellipse(-100, -72, 14, 10, 12))), pal[0], 0.4, 4 * s),
          K.stroke_line(Q([(-40, -10), (-24, 8), (-36, 24)]), pal[2], 1.6 * s, 0.35),   # line of the shoulder
          K.stroke_line(Q([(70, -26), (82, 4), (78, 28)]), pal[2], 1.6 * s, 0.3),        # stifle and thigh
          K.stroke_line(Q([(-100, -86), (-110, -70), (-104, -60)]), pal[2], 1.2 * s, 0.35)]  # cheekbone
    if dapple:
        for k in range(36):
            x, y = rnd.uniform(-40, 140), rnd.uniform(-34, 30)
            ex.append(f'<circle cx="{Q([(x, y)])[0][0]:.1f}" cy="{Q([(x, y)])[0][1]:.1f}" r="{rnd.uniform(3, 6) * s:.1f}" fill="{pal[0]}" opacity="0.35"/>')
    out.append(form(P, sp(body), pal, L, K.bbox(body), core=0.5, lit=0.5, extra=ex, edge="#000000", edge_op=0.5,
                    rim_col=rim_col, rim_d=2.2, rim_src=rim_src))
    for name in ("fore_near", "hind_near"):
        out.append(leg(*legs[name], False))
    # mane along the crest, blowing back; forelock
    for k in range(14):
        t = k / 13
        root = K.lerp2((-84, -106), (-8, -52), t)
        tip = (root[0] + 26 + rnd.uniform(-4, 8), root[1] - 14 + rnd.uniform(-6, 6) + t * 6)
        mid = ((root[0] + tip[0]) / 2 + 2, (root[1] + tip[1]) / 2 - 6)
        out.append(K.taper(Q([root, mid, tip]), 7 * s, 0.8, rnd.choice(mane), 0.9))
    out.append(K.taper(Q([(-92, -104), (-102, -100), (-110, -92)]), 5 * s, 1, mane[1], 0.9))
    # eye, nostril, mouth
    ex_, ey_ = Q([(-102, -84)])[0]
    out.append(f'<ellipse cx="{ex_:.1f}" cy="{ey_:.1f}" rx="{3.2 * s:.1f}" ry="{2.4 * s:.1f}" fill="#120E0E"/><circle cx="{ex_ - 0.8 * s:.1f}" cy="{ey_ - 0.8 * s:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    out.append(K.path(sp(Q([(-144, -52), (-139, -57), (-137, -50), (-141, -48)])), "#2A2226", 0.85))
    out.append(K.stroke_line(Q([(-147, -41), (-135, -40)]), "#2A2226", 1.2 * s, 0.7))
    return "".join(out)


# ================================================================ sleipnir — Odin's eight-legged horse over the clouds (plate)
def odin_rider(P, ox, oy, s, seed, L, rim_col, rim_src):
    """Odin on horseback, seen against the moon: the wide-brimmed hat, the long grey beard, the cloak streaming
    back in the wind of the gallop, Gungnir levelled forward. Seated at (ox, oy) = the saddle, in horse units."""
    def Q(pts):
        return place(pts, ox, oy, s)
    B = K.Body(P, L)
    cloak = Q([(-10, -60), (10, -66), (40, -64), (80, -56), (120, -50), (150, -36, 1), (122, -30), (140, -14), (104, -12), (118, 4, 1), (78, 0), (40, 4),
               (14, 0), (-6, -24)])
    B.add(cloak, ("#3A4A72", "#10162A", "#03050A"), core=0.5, lit=0.4,
          extra=[K.stroke_line(Q([(0, -56), (60, -44), (120, -34)]), "#000000", 2 * s, 0.5), K.stroke_line(Q([(4, -40), (60, -24), (110, -12)]), "#000000", 2 * s, 0.45)])
    torso = Q([(-14, -2), (-20, -30), (-18, -56), (-10, -66), (4, -66), (12, -54), (12, -28), (10, -2)])
    B.add(torso, ("#5A6A8A", "#1E2638", "#06080E"), core=0.5, lit=0.4)
    leg = Q(K.limb([(0, -4), (-14, 10), (-16, 34), (-22, 48)], [8, 7, 5, 4], [9, 8, 6, 4]))
    B.add(leg, ("#4A4A5A", "#1A1A22", "#060608"), core=0.5, lit=0.3)
    arm = Q(K.limb([(-8, -58), (-24, -44), (-42, -40)], [6, 5, 4], [6, 5, 4]))
    B.add(arm, ("#5A6A8A", "#1E2638", "#06080E"), core=0.4, lit=0.4)
    head = Q([(-12, -66), (-18, -74), (-16, -84), (-8, -88), (2, -84), (4, -72), (0, -64)])
    B.add(head, ("#C8B8A8", "#5A4A40", "#140C08"), core=0.5, lit=0.5)
    beard = Q([(-18, -72), (-24, -62), (-20, -48), (-12, -44), (-8, -56), (-6, -66)])
    B.add(beard, ("#F2F2F6", "#A8AAB8", "#3A3C48"), core=0.4, lit=0.5)
    hat = Q([(-34, -84), (-16, -88), (-12, -104), (-2, -112, 1), (6, -100), (8, -88), (26, -84), (24, -80), (-32, -80)])
    B.add(hat, ("#5A6A8A", "#1A2238", "#05070E"), core=0.4, lit=0.4)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=2.0, op=0.95, src=rim_src)], edge_op=0.6)]
    # Gungnir, levelled forward over the horse's head
    a_, b_ = Q([(30, -46)])[0], Q([(-150, -60)])[0]
    out.append(K.stroke_line([a_, b_], "#2A2018", 2.6 * s, 1, smooth=False))
    out.append(K.stroke_line([a_, b_], rim_col, 0.8 * s, 0.6, smooth=False))
    tip = Q([(-150, -64), (-170, -60, 1), (-150, -56)])
    out.append(K.path(sp(tip), "#E8ECF4"))
    return "".join(out)


@plate("sleipnir")
def sleipnir_p():
    P = Plate("myp-sl")
    rnd = random.Random(3)
    mx, my, mr = 330, 262, 150
    L = (0.7, -0.7)
    art = [K.sky_grad(P, [(0, "#040814"), (0.35, "#0A1630"), (0.7, "#14284A"), (1, "#1E3050")])]
    art.append(K.stars(4, (0, 0, 600, 420), 160, avoid=lambda x, y: math.hypot(x - mx, y - my) < 90))
    # the aurora: curtains of green and violet light
    for k in range(5):
        x0 = -40 + k * 60
        band = [(x0, 60 + k * 10), (x0 + 120, 40 + k * 14), (x0 + 260, 90 + k * 8), (x0 + 420, 70 + k * 12), (x0 + 640, 120)]
        pts = K.catmull(band, 8)
        rays_ = "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-6, 6):.1f} {rnd.uniform(60, 140):.1f}" stroke="{rnd.choice(["#4AF0A0", "#2AD8A8", "#8A6AE8"])}" '
                        f'stroke-width="{rnd.uniform(3, 8):.1f}" opacity="{rnd.uniform(0.08, 0.22):.2f}"/>' for x, y in pts[::2])
        art.append(screen(f'<g {P.blur(4)}>{rays_}</g>'))
    art.append(glow(P, mx, my, mr * 2.4, "#8AB0E8", 0.4))
    art.append(moon_disc(P, mx, my, mr, 6, glow_col="#9AB8F0"))
    # a sea of moonlit cloud below, torn and drifting, the far mountains of Midgard glimpsed between
    art.append(K.strata(P, 4, 420, -40, 640, 22, ("#E8F0FF", "#4A5A88", "#14203E"), L=(0.3, -1), n=8, op=0.95, sd=2.4, rough_=(16, 0.02)))
    art.append(K.strata(P, 5, 470, -40, 640, 26, ("#C8D4F2", "#2E3A66", "#0C1430"), L=(0.3, -1), n=9, op=1.0, sd=2.8, rough_=(18, 0.02)))
    art.append(K.strata(P, 6, 330, -40, 640, 10, ("#F2F6FF", "#6A7AA8", "#2A3458"), L=(0.3, -1), n=5, op=0.6, sd=1.6))
    # Sleipnir, with Odin on his back, racing left across the sky; eight legs, the far four in shade
    hx, hy, hs = 296, 286, 1.0
    # eight legs in different phases of the stride, so that every one of them reads
    legs = {"fore_near": ([(-44, 36), (-64, 46), (-84, 54), (-106, 58), (-118, 60), (-130, 68)], [17, 13, 8, 7, 8.5, 6], [17, 12, 8, 7, 8.5, 6]),
            "fore_far": ([(-48, 30), (-70, 36), (-92, 40), (-112, 38), (-124, 40), (-136, 46)], [16, 12, 7.5, 6.5, 8, 5.5], [16, 11, 7.5, 6.5, 8, 5.5]),
            "hind_near": ([(98, 52), (114, 62), (130, 70), (146, 74), (160, 78), (172, 84)], [14, 10, 8, 7, 8.5, 6], [16, 11, 8.5, 7, 8.5, 6]),
            "hind_far": ([(88, 48), (106, 56), (122, 62), (138, 64), (152, 66), (164, 70)], [13, 10, 7.5, 6.5, 8, 5.5], [15, 10, 8, 6.5, 8, 5.5])}
    extra = [([(-40, 38), (-52, 54), (-62, 72), (-54, 88), (-48, 100), (-40, 110)], [16, 12, 7.5, 6.5, 8, 5.5], [16, 11, 7.5, 6.5, 8, 5.5]),
             ([(-34, 38), (-38, 58), (-44, 80), (-43, 98), (-42, 112), (-48, 124)], [16, 12, 7.5, 6.5, 8, 5.5], [16, 11, 7.5, 6.5, 8, 5.5]),
             ([(90, 54), (94, 72), (96, 90), (82, 100), (70, 108), (60, 114)], [13, 10, 7.5, 6.5, 8, 5.5], [15, 10, 8, 6.5, 8, 5.5]),
             ([(96, 54), (104, 72), (110, 88), (108, 104), (104, 118), (98, 128)], [13, 10, 7.5, 6.5, 8, 5.5], [15, 10, 8, 6.5, 8, 5.5])]
    src = (mx, my, 420)
    art.append(horse_g(P, hx, hy, hs, 5, pal=("#5A6280", "#161A26", "#030406"), mane=("#FFFFFF", "#C8CCD8", "#6A6E80"), L=L,
                       rim_col="#E8F0FF", rim_src=src, dapple=False, extra_legs=extra, legs=legs))
    art.append(odin_rider(P, hx + 6 * hs, hy - 38 * hs, hs, 7, L, "#E8F0FF", src))
    art.append(K.vignette(P, "#02040A", 0.5, 0.6))
    art.append(K.text_scrim(P, 470, 600, "#02040A", 0.7))
    text = [gilt(P, 300, 512, "Sleipnir", DMS, 64, ls=1, max_w=420, seed=3, pal="silver", deboss="#000000", dop=0.85),
            tx(300, 540, "NORSE · ODIN’S EIGHT-LEGGED STEED", CINZEL, 16, "#DCE6FF", ls=2.2, max_w=440)]
    return P.render(art, text, seed=141, edge=2.0, bristle=0.45, grain=0.18)


# ================================================================ thor's goats — the thunder-chariot across the storm (plate)
GOAT_BODY_L = [(-104, -54, 0.5), (-100, -62), (-86, -76), (-76, -86), (-70, -92), (-62, -88), (-50, -70), (-30, -54), (0, -50), (30, -52), (52, -55),
               (56, -66, 1), (62, -56), (68, -42), (66, -20), (60, -2), (52, 8), (40, 4), (20, 6), (-10, 8), (-34, 4), (-40, 10), (-52, -4), (-58, -22),
               (-64, -40), (-74, -48), (-80, -46), (-88, -26, 1), (-92, -40), (-98, -50)]
GOAT_LEGS = [([(-40, 4), (-60, 14), (-80, 22), (-96, 22), (-104, 26)], [9, 6, 4.5, 4.5, 3.5], [9, 6, 4.5, 4.5, 3.5]),          # fore near, reaching
             ([(-44, 2), (-58, 22), (-68, 36), (-60, 48), (-56, 54)], [8, 5.5, 4, 4, 3.2], [8, 5.5, 4, 4, 3.2]),              # fore far, tucked
             ([(50, 4), (68, 18), (86, 24), (102, 30), (112, 34)], [11, 7, 4.5, 4.5, 3.5], [12, 7, 4.5, 4.5, 3.5]),          # hind near, thrown back
             ([(44, 4), (58, 22), (66, 38), (78, 46), (86, 50)], [10, 6.5, 4, 4, 3.2], [11, 6.5, 4, 4, 3.2])]                # hind far


def goat_g(P, ox, oy, s, seed, pal=("#8A8090", "#2A2430", "#08060A"), L=(0.6, -0.8), rim_col=None, rim_src=None, horn="#D8C8A8"):
    """One of Thor's goats leaping: a lean goat body, short upright tail, shaggy beard, long ridged horns sweeping
    back over the neck; shaggy coat along the belly and thighs. Faces left; (ox, oy) = barrel centre (~210 * s long)."""
    def Q(pts):
        return place(pts, ox, oy, s)
    rnd = random.Random(seed)
    out = []
    dark = (mix(pal[0], pal[1], 0.5), mix(pal[1], pal[2], 0.4), pal[2])
    for i, (ax, wl, wr) in enumerate(GOAT_LEGS):
        far = i in (1, 3)
        q = Q(K.limb(ax, wl, wr, n=5))
        out_ = form(P, sp(q), dark if far else pal, L, K.bbox(q), core=0.4, lit=0.25 if far else 0.4, edge="#000000", edge_op=0.6)
        hx, hy = ax[-1]
        hf = Q([(hx - 3, hy - 2), (hx + 3, hy - 2), (hx + 4, hy + 4, 1), (hx - 4, hy + 4, 1)])
        (out.insert(0, out_ + K.path(sp(hf), "#1A1410")) if far else out.append(out_ + K.path(sp(hf), "#1A1410")))
    body = Q(GOAT_BODY_L)
    shag = K.brush(seed, K.bbox(body), 160, 100, [pal[0], pal[2], mix(pal[1], pal[0], 0.4)], (4 * s, 10 * s), (0.8, 1.6), (0.3, 0.6),
                   inside=K.inside_poly(body))
    out.insert(2, f'<g {P.rough(2.6 * s, 0.12, seed)}>' + form(P, sp(body), pal, L, K.bbox(body), core=0.5, lit=0.45, edge="#000000", edge_op=0.6,
                                                             extra=[shag, soft(P, sp(Q(ellipse(-30, -24, 20, 18, 12))), pal[0], 0.4, 5 * s)],
                                                             rim_col=rim_col, rim_d=2.0, rim_src=rim_src) + "</g>")
    # horns: long, ridged, sweeping back
    for k, off in enumerate((0, 6)):
        spine = K.bez((-70 + off, -92), (-60 + off, -120), (-30 + off, -128), (-10 + off, -112), 10)
        hp = Q(spine)
        out.append(K.taper(hp, (9 - k * 2) * s, 2 * s, horn if k == 0 else mix(horn, "#000000", 0.4)))
        if k == 0:
            for j in range(1, 9):
                a_, b_ = hp[j - 1], hp[j + 1]
                tx_, ty_ = K.unit(b_[0] - a_[0], b_[1] - a_[1])
                w = (9 - j * 0.7) * s * 0.5
                out.append(f'<path d="M {hp[j][0] - ty_ * w:.1f} {hp[j][1] + tx_ * w:.1f} L {hp[j][0] + ty_ * w:.1f} {hp[j][1] - tx_ * w:.1f}" stroke="#5A4A3A" stroke-width="0.9" opacity="0.7"/>')
    ex, ey = Q([(-78, -74)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{2.4 * s:.1f}" ry="{1.4 * s:.1f}" fill="#E8C040"/><rect x="{ex - 1.6 * s:.1f}" y="{ey - 0.4 * s:.1f}" width="{3.2 * s:.1f}" height="{0.8 * s:.1f}" fill="#000"/>')
    return "".join(out)


def thor_figure(P, ox, oy, s, seed, L, rim_col, rim_src):
    """Thor standing braced in the chariot (seen from the hips up above the rail), Mjolnir raised high in his right
    hand, the reins in his left, face in profile toward the goats, red hair and beard blown back, a cloak streaming.
    Faces left; drawn ~8 heads tall (head = 26 units)."""
    def Q(pts):
        return place(pts, ox, oy, s)
    skin = ("#F2B890", "#7A4430", "#1A0A06")
    red = ("#FF9A50", "#A83A14", "#2A0804")
    tunic = ("#7A8AB0", "#26304A", "#080A12")
    B = K.Body(P, L)
    cloak = Q([(-6, -156), (24, -162), (70, -156), (130, -140), (178, -114, 1), (142, -106), (166, -82), (122, -80), (132, -58, 1), (82, -62), (34, -56), (14, -90)])
    B.add(cloak, ("#E8604A", "#7A1810", "#1A0402"), core=0.55, lit=0.4,
          extra=[K.stroke_line(Q([(10, -150), (80, -134), (150, -112)]), "#1A0402", 2.2 * s, 0.5), K.stroke_line(Q([(20, -124), (80, -100), (140, -84)]), "#1A0402", 2.2 * s, 0.45)])
    # the raised (far, right) arm
    B.add(Q(K.limb([(20, -150), (28, -172), (34, -194), (30, -214), (24, -230)], [11, 10, 7, 8, 6], [12, 10, 7, 7.5, 6])), skin, core=0.4, lit=0.5)
    B.add(Q(ellipse(23, -234, 8, 7, 10)), skin, core=0.4, lit=0.5)
    # torso in a belted tunic
    torso = Q([(-34, -152), (-42, -136), (-40, -112), (-33, -96), (-36, -60), (26, -60), (28, -96), (30, -128), (26, -150), (10, -162), (-14, -161)])
    B.add(torso, tunic, core=0.5, lit=0.4, extra=[K.stroke_line(Q([(-36, -94), (28, -96)]), "#C8A040", 5 * s, 0.95),
                                                  K.stroke_line(Q([(-30, -146), (-10, -120), (10, -100)]), "#000000", 1.6 * s, 0.4),
                                                  soft(P, sp(Q(ellipse(-24, -128, 14, 20, 10))), tunic[0], 0.4, 4 * s)])
    # neck and head in profile
    B.add(Q([(-18, -164), (-2, -168), (4, -156), (-16, -152)]), skin, core=0.5, lit=0.4)
    head = Q([(-6, -208), (-18, -204), (-24, -194), (-26, -188), (-31, -180, 0.6), (-26, -176), (-25, -171), (-18, -166), (-2, -168), (6, -180), (8, -196)])
    B.add(head, skin, core=0.4, lit=0.55, extra=[soft(P, sp(Q(ellipse(-16, -188, 3.6, 2.4, 8))), "#000000", 0.6, 0.8)])
    hair = Q([(-8, -212), (-22, -204), (-12, -200), (2, -200), (6, -186), (10, -174), (30, -178), (56, -186, 1), (38, -194), (60, -204, 1), (32, -208),
              (44, -220, 1), (14, -216)])
    B.add(hair, red, core=0.4, lit=0.55)
    beard = Q([(-27, -172), (-30, -160), (-26, -140, 0.6), (-16, -146), (-6, -156), (-2, -168), (-16, -168)])
    B.add(beard, red, core=0.4, lit=0.5, extra=[K.scallops(seed, K.bbox(beard), 14, 100, [red[0], red[2]], (1.2 * s, 2.4 * s), (0.4, 0.7), (0.6, 1))])
    # the near (left) arm forward with the reins
    B.add(Q(K.limb([(-30, -150), (-44, -138), (-56, -124), (-70, -118), (-84, -116)], [12, 10, 7, 8, 6], [12, 10, 7, 7.5, 6])), skin, core=0.45, lit=0.45)
    B.add(Q(ellipse(-88, -116, 7, 6, 10)), skin, core=0.4, lit=0.45)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=2.2, op=0.95, src=rim_src)], edge_op=0.6)]
    # Mjolnir: the short-hafted hammer, its head blazing with the lightning it calls
    hd = Q([(0, -262), (48, -262), (50, -240), (-2, -240)])
    out.append(K.stroke_line([Q([(23, -226)])[0], Q([(24, -246)])[0]], "#3A2414", 5 * s, 1))
    out.append(form(P, lp(hd), ("#E8ECF2", "#6A7080", "#1A1C24"), L, K.bbox(hd), core=0.4, lit=0.6, edge="#000000", edge_op=0.6,
                    extra=[K.stroke_line(Q([(4, -252), (44, -252)]), "#2A2C34", 1.2 * s, 0.6)]))
    out.append(screen(glow(P, *K.lerp2(hd[0], hd[2], 0.5), 60 * s, "#C8D8FF", 0.6)))
    return "".join(out)


@plate("thors-goats")
def thors_goats_p():
    P = Plate("myp-tg")
    rnd = random.Random(4)
    L = (0.5, -0.9)
    fx, fy = 520, 170
    art = [K.sky_grad(P, [(0, "#0C0E1C"), (0.4, "#1E2234"), (0.7, "#2E3040"), (1, "#14141E")])]
    art.append(screen(glow(P, fx, fy, 300, "#9AA8E8", 0.45)))
    # storm clouds in heavy masses, lit from within by the lightning
    art.append(K.sky_wash(P, 3, ["#3A3E58", "#0C0E18", "#5A6080"], 18, (-40, -40, 640, 460), (90, 200), (0.25, 0.45), 26, flat=0.5))
    for k, (cy, th, op) in enumerate(((60, 40, 0.95), (150, 34, 0.9), (230, 30, 0.85), (310, 26, 0.85))):
        art.append(K.strata(P, 30 + k, cy, -60, 660, th, ("#C8D0F2", "#3A3E58", "#0A0C16"), L=(0.5, -1), n=9, op=op, sd=3.4, rough_=(24, 0.018)))
    # the lightning bolt itself, forking down to the left
    bolt = [(fx, 150), (fx - 10, 190), (fx + 6, 202), (fx - 18, 250), (fx - 6, 258), (fx - 30, 310)]
    art.append(screen(K.stroke_line(bolt, "#B8C4FF", 12, 0.5, smooth=False, extra=f' {P.blur(5)}')))
    art.append(K.stroke_line(bolt, "#FFFFFF", 2.6, 1, smooth=False))
    art.append(K.stroke_line([(fx + 6, 202), (fx + 30, 230), (fx + 26, 260)], "#FFFFFF", 1.4, 0.8, smooth=False))
    # rain slanting
    rain = "".join(f'<path d="M {x:.1f} {y:.1f} l -10 26" stroke="#C8D0F0" stroke-width="0.8" opacity="{rnd.uniform(0.1, 0.3):.2f}"/>'
                   for x, y in [(rnd.uniform(-20, 640), rnd.uniform(0, 600)) for _ in range(140)])
    art.append(rain)
    # the chariot: a light car with a spoked wheel, sparks where it runs on the cloud
    src = (fx, fy, 520)
    cx_, cy_ = 400, 370
    car = [(cx_ - 50, cy_ - 50), (cx_ + 50, cy_ - 56), (cx_ + 60, cy_ - 10), (cx_ + 40, cy_ + 6), (cx_ - 50, cy_ + 6)]
    art.append(thor_figure(P, cx_ + 4, cy_ - 8, 0.78, 5, L, "#E8F0FF", src))
    art.append(form(P, sp(car), ("#C89A60", "#5A3A1C", "#140A04"), L, K.bbox(car), core=0.5, lit=0.4, edge="#000000", edge_op=0.6, rim_col="#E8F0FF", rim_d=2, rim_src=src,
                    extra=[K.stroke_line([(cx_ - 46, cy_ - 30), (cx_ + 54, cy_ - 34)], "#E8C070", 2, 0.7)]))
    wx, wy, wr = cx_ + 4, cy_ + 4, 40
    art.append(K.stroke_line(ellipse(wx, wy, wr, wr, 36) + [ellipse(wx, wy, wr, wr, 36)[0]], "#2A1A0C", 6, 1))
    art.append(K.stroke_line(ellipse(wx, wy, wr, wr, 36, a0=200, a1=320), "#E8F0FF", 2, 0.7))
    for k in range(8):
        a = math.radians(k * 22.5 + 8)
        art.append(K.stroke_line([(wx, wy), (wx + math.cos(a) * wr, wy + math.sin(a) * wr)], "#2A1A0C", 2.4, 0.95, smooth=False))
    art.append(f'<circle cx="{wx}" cy="{wy}" r="6" fill="#C8A040"/>')
    art.append(K.embers(5, wx, wy + wr, 30, 40, 30, cols=("#FFFFFF", "#C8D8FF", "#FFE8A0")))
    # the traces and the two goats racing ahead
    art.append(K.stroke_line([(cx_ - 50, cy_ - 20), (300, 336), (230, 330)], "#1A1008", 3, 0.9))
    art.append(goat_g(P, 254, 330, 0.92, 7, L=L, rim_col="#E8F0FF", rim_src=src, pal=("#8A8078", "#2E2824", "#080606")))
    art.append(goat_g(P, 176, 362, 1.0, 8, L=L, rim_col="#E8F0FF", rim_src=src, pal=("#A8A098", "#3A3430", "#0A0808")))
    art.append(K.stroke_line([(cx_ - 52, cy_ - 16), (300, 350), (196, 352)], "#1A1008", 3, 0.9))
    # cloud they run upon
    art.append(K.strata(P, 41, 440, -40, 640, 30, ("#B8C0E0", "#2E3248", "#0A0C14"), L=(0.4, -1), n=9, op=1.0, sd=3, rough_=(18, 0.02)))
    art.append(K.vignette(P, "#020206", 0.5, 0.6))
    art.append(K.text_scrim(P, 450, 600, "#020206", 0.75))
    text = [gilt(P, 300, 100, "Thor’s Goats", SERIF_IT, 64, ls=0.5, max_w=420, seed=6, pal="silver", deboss="#000000", dop=0.85),
            tx(300, 130, "NORSE · TANNGRISNIR & TANNGNJÓSTR", CINZEL, 16, "#DCE4F8", ls=2, max_w=440),
            tx(300, 532, "When it thunders, Thor is riding.", SERIF_IT, 28, "#F2F4FF", max_w=440)]
    return P.render(art, text, seed=151, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ fenrir — the great wolf bound by Gleipnir on the isle of Lyngvi (plate)
def howling_wolf_g(P, ox, oy, s, seed, pal=("#8A94B0", "#232838", "#05060A"), L=(-0.6, -0.8), rim_col="#E8F0FF", rim_src=None):
    """A great grey wolf sitting back on its haunches, head thrown up to howl: long muzzle, ears laid back, a heavy
    ruff of fur at the neck and chest, straight forelegs, the bushy tail curled round the feet. Faces left, ~290 * s
    tall. (ox, oy) = ground under the forefeet."""
    def Q(pts):
        return place(pts, ox, oy, s)
    rnd = random.Random(seed)
    out = []
    far_leg = Q(K.limb([(-10, -120), (-14, -76), (-14, -40), (-12, -10), (-20, 0)], [13, 10, 7, 6.5, 8], [14, 10, 7.5, 6.5, 8]))
    out.append(K.furry(P, far_leg, (mix(pal[0], pal[1], 0.5), pal[1], pal[2]), L, seed, 95, n=40, rough=(2 * s, 0.12), core=0.5, lit=0.2))
    body_l = [(-80, -268, 0.6), (-66, -276), (-52, -264), (-42, -258), (-34, -254), (-20, -286, 1), (-12, -250), (-4, -238), (6, -220), (14, -202),
              (24, -172), (40, -142), (56, -106), (72, -82), (86, -52), (88, -24), (80, -6), (60, 0), (16, 0), (0, -4), (-12, -2), (-40, 0, 1), (-38, -6),
              (-34, -60), (-34, -110), (-40, -138), (-52, -150, 0.6), (-46, -156), (-58, -166, 0.6), (-52, -172), (-62, -186, 0.6), (-58, -194),
              (-66, -212), (-72, -236), (-76, -252), (-72, -258), (-80, -262)]
    body = Q(body_l)

    def flow(x, y):
        lx_, ly_ = (x - ox) / s, (y - oy) / s
        if ly_ < -200:
            return 60          # head and neck fur runs back from the muzzle
        if lx_ > 30:
            return 110
        return 95
    over = [soft(P, sp(Q([(30, -170), (90, -60), (90, -10), (40, -20), (20, -100)])), pal[2], 0.6, 10 * s),
            soft(P, sp(Q([(-60, -200), (-40, -240), (-10, -230), (-20, -170)])), pal[0], 0.55, 8 * s),
            soft(P, sp(Q(ellipse(52, -50, 30, 36, 14))), pal[0], 0.3, 8 * s)]
    out.append(K.furry(P, body, pal, L, seed + 1, flow, n=520, flen=(5 * s, 14 * s), fw=(0.6, 1.4), fop=(0.3, 0.6), rough=(3 * s, 0.1),
                       core=0.5, lit=0.45, edge="#000000", edge_op=0.6, pre=over, rim_col=rim_col, rim_d=2.4, rim_src=rim_src))
    # bushy tail curled round in front
    tail = Q(K.plume([(84, -8), (60, 6), (20, 10), (-10, 10), (-36, 6)], 30, (0.5, 0.8, 1.0, 0.9, 0.6, 0.2)))
    out.append(K.furry(P, tail, (mix(pal[0], pal[1], 0.6), pal[1], pal[2]), L, seed + 2, 180, n=90, flen=(5 * s, 12 * s), rough=(3 * s, 0.1), core=0.55,
                       lit=0.25, edge="#000000", edge_op=0.6, extra=[soft(P, sp(Q(ellipse(-30, 6, 12, 8, 10))), "#000000", 0.7, 3 * s)]))
    # the near foreleg read inside the mass: its back edge in shadow against the belly, a lit front edge; the thigh line
    out.append(f'<g {P.rough(2 * s, 0.12, seed)}>' + K.stroke_line(Q([(-12, -124), (-16, -80), (-18, -40), (-16, -8)]), "#000000", 2.6 * s, 0.55)
               + K.stroke_line(Q([(-34, -112), (-34, -60), (-36, -12)]), rim_col, 1.2 * s, 0.4)
               + K.stroke_line(Q([(30, -120), (12, -80), (10, -40), (20, -6)]), "#000000", 2.2 * s, 0.45) + "</g>")
    for k in range(4):
        tx_ = -38 + k * 5
        out.append(K.stroke_line(Q([(tx_, -6), (tx_ - 1, 0)]), "#000000", 1.2 * s, 0.6))
    # face: the eye shut tight in the howl, the dark lips, nose
    out.append(K.stroke_line(Q([(-52, -250), (-46, -248), (-40, -250)]), "#000000", 1.6 * s, 0.85))
    out.append(K.stroke_line(Q([(-76, -256), (-68, -248), (-60, -246)]), "#000000", 1.6 * s, 0.7))
    nx_, ny_ = Q([(-78, -268)])[0]
    out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="{4 * s:.1f}" ry="{3 * s:.1f}" fill="#050508" transform="rotate(-50 {nx_:.1f} {ny_:.1f})"/>')
    return "".join(out)


def gleipnir_g(P, pts, seed, w=2.2):
    """Gleipnir: a ribbon soft and smooth as silk, woven of impossible things, shimmering faintly where it binds."""
    return (screen(K.stroke_line(pts, "#A8F0E8", w * 3, 0.22, extra=f' {P.blur(2)}')) + K.stroke_line(pts, "#C8E8F0", w, 0.85)
            + K.stroke_line([(x, y - w * 0.3) for x, y in pts], "#FFFFFF", w * 0.35, 0.7))


@plate("fenrir")
def fenrir_p():
    P = Plate("myp-fe")
    rnd = random.Random(6)
    mx, my, mr = 196, 236, 104
    L = (-0.7, -0.6)
    art = [K.sky_grad(P, [(0, "#04060E"), (0.4, "#0A1428"), (0.7, "#142440"), (1, "#0A1020")])]
    art.append(K.stars(5, (0, 0, 600, 400), 140, avoid=lambda x, y: math.hypot(x - mx, y - my) < 130))
    for k in range(6):
        x0 = -60 + k * 50
        band = [(x0, 70 + k * 6), (x0 + 160, 50 + k * 8), (x0 + 340, 100 + k * 6), (x0 + 520, 60 + k * 8), (x0 + 700, 110)]
        pts = K.catmull(band, 8)
        rays_ = "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(70, 160):.1f}" stroke="{rnd.choice(["#4AF0A0", "#2AD8A8", "#6AE0C0", "#9A7AF0"])}" '
                        f'stroke-width="{rnd.uniform(3, 9):.1f}" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>' for x, y in pts[::2])
        art.append(screen(f'<g {P.blur(5)}>{rays_}</g>'))
    art.append(moon_disc(P, mx, my, mr, 9, glow_col="#9AB8F0"))
    # the sea and the dark islands
    art.append(K.water(P, 8, 380, 600, [(0, "#2A3A5A"), (0.4, "#121C34"), (1, "#060A16")], ["#9AB0D8", "#0A1428", "#4A5A80"], n=150, sun_x=mx, glint="#E8F0FF", glint_w=40))
    far = K.ridge(5, -20, 640, 384, 360, 12, 14, 0.5, peaks=[(520, 330, 80)])
    art.append(K.path(sp(far), "#0C1424"))
    # the rock of Lyngvi in the foreground
    rock = [(150, 620), (190, 520), (240, 478), (300, 462), (380, 456), (460, 466), (520, 490), (580, 520), (640, 560), (640, 620)]
    art.append(crag(P, rock, ("#5A6480", "#1A2030", "#05070C"), 7, L=L, lit="#C8D8FF", src=(mx, my, 520), faces=26, strata=10))
    # the boulder Gviol to which the fetter is made fast, the chain Gelgja
    art.append(form(P, lp([(468, 476), (474, 446), (496, 430), (528, 434), (544, 454), (548, 478)]), ("#5A6480", "#1E2434", "#05060A"), L, (468, 430, 548, 478),
                    core=0.5, lit=0.4, edge="#000000", edge_op=0.6, rim_col="#C8D8FF", rim_d=1.6))
    # the wolf
    wx, wy, ws = 330, 478, 1.12
    art.append(howling_wolf_g(P, wx, wy, ws, 11, L=L, rim_src=(mx, my, 440)))
    # Gleipnir about the neck and the forelegs, running down to the boulder
    neck = [place([(x, y)], wx, wy, ws)[0] for x, y in ((-60, -184), (-30, -176), (0, -184), (14, -196))]
    art.append(gleipnir_g(P, neck, 1))
    legs = [place([(x, y)], wx, wy, ws)[0] for x, y in ((-42, -40), (-26, -36), (-12, -38))]
    art.append(gleipnir_g(P, legs, 2))
    trail = [neck[0], place([(-70, -150)], wx, wy, ws)[0], place([(-60, -80)], wx, wy, ws)[0], legs[0]]
    art.append(gleipnir_g(P, trail, 3, 2.2))
    chain = [legs[-1], (420, 470), (470, 468), (494, 456)]
    art.append(gleipnir_g(P, chain, 4, 2.2))
    art.append(K.vignette(P, "#010206", 0.5, 0.6))
    art.append(K.text_scrim(P, 470, 600, "#010206", 0.75))
    text = [gilt(P, 300, 100, "FENRIR", CINZEL, 62, ls=14, max_w=400, seed=3, pal="silver", deboss="#000000", dop=0.85),
            tx(300, 130, "NORSE · BOUND BY A SILKEN RIBBON", CINZEL, 17, "#DCE6FF", ls=2.4, max_w=440),
            tx(300, 532, "Woven of a cat’s footfall and a mountain’s roots", SERIF_IT, 22, "#E8F0FF", max_w=440)]
    return P.render(art, text, seed=161, edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ romulus and remus — the she-wolf at the Tiber, under the fig tree (plate)
def lying_wolf_g(P, ox, oy, s, seed, pal=("#D8B890", "#6A5440", "#140E08"), L=(-0.8, -0.5), rim_col="#FFD8A0", rim_src=None):
    """A she-wolf lying down with her forelegs stretched before her and her head lowered over the basket of the twins,
    ears soft, the tail curled round her flank. Faces left; (ox, oy) = ground at the middle of the body, ~270 * s long."""
    def Q(pts):
        return place(pts, ox, oy, s)
    body_l = [(-150, -32, 0.6), (-138, -44), (-118, -56), (-106, -64), (-100, -68), (-92, -92, 1), (-82, -70), (-72, -66), (-54, -68), (-30, -76),
              (0, -68), (30, -62), (60, -64), (86, -70), (106, -58), (116, -36), (114, -12), (98, 0), (40, 2), (-40, 2), (-62, -4), (-86, -8), (-118, -6),
              (-132, -2, 0.6), (-128, -12), (-96, -16), (-70, -22), (-66, -30), (-74, -36), (-100, -38), (-132, -30), (-146, -28)]
    body = Q(body_l)

    def flow(x, y):
        lx_, ly_ = (x - ox) / s, (y - oy) / s
        if lx_ < -70:
            return 10
        return 15 + (ly_ + 30) * 0.6
    over = [soft(P, sp(Q([(-60, -64), (60, -58), (80, -40), (-40, -40)])), pal[0], 0.55, 8 * s),
            soft(P, sp(Q([(-40, -20), (100, -16), (100, 0), (-40, 0)])), pal[2], 0.6, 6 * s),
            soft(P, sp(Q(ellipse(84, -30, 26, 22, 12))), pal[0], 0.35, 6 * s),
            soft(P, sp(Q([(-118, -58), (-96, -66), (-84, -56), (-110, -46)])), pal[0], 0.5, 3 * s),
            K.stroke_line(Q([(64, -54), (78, -30), (70, -6)]), pal[2], 2 * s, 0.4),
            K.stroke_line(Q([(-56, -58), (-50, -40), (-58, -24)]), pal[2], 1.8 * s, 0.35)]
    out = [K.furry(P, body, pal, L, seed, flow, n=460, flen=(5 * s, 12 * s), fw=(0.6, 1.3), fop=(0.3, 0.6), rough=(2.4 * s, 0.11), core=0.5, lit=0.5,
                   edge="#000000", edge_op=0.55, pre=over, rim_col=rim_col, rim_d=2.2, rim_src=rim_src)]
    tail = Q(K.plume([(110, -14), (120, 4), (90, 14), (40, 14), (10, 10)], 24, (0.5, 0.9, 1.0, 0.7, 0.2)))
    out.append(K.furry(P, tail, pal, L, seed + 1, 180, n=60, rough=(2 * s, 0.11), core=0.5, lit=0.4, edge="#000000", edge_op=0.6))
    # face: the eye half-closed and gentle, the black nose, the line of the mouth
    ex, ey = Q([(-112, -54)])[0]
    out.append(K.stroke_line(Q([(-118, -54), (-112, -56), (-106, -54)]), "#140A04", 1.6 * s, 0.9))
    out.append(f'<ellipse cx="{Q([(-147, -34)])[0][0]:.1f}" cy="{Q([(-147, -34)])[0][1]:.1f}" rx="{4 * s:.1f}" ry="{3 * s:.1f}" fill="#100A06"/>')
    out.append(K.stroke_line(Q([(-144, -28), (-126, -30), (-114, -36)]), "#140A04", 1.3 * s, 0.7))
    out.append(K.path(sp(Q([(-96, -70), (-90, -86, 1), (-86, -70)])), "#3A2414", 0.5))
    return "".join(out)


def twins_basket(P, cx, cy, s, seed):
    """A shallow basket of woven reeds with the two infants asleep in it, wrapped in linen, one small hand free."""
    def Q(pts):
        return place(pts, cx, cy, s)
    rnd = random.Random(seed)
    out = [K.cast_shadow(P, cx, cy + 12 * s, 56 * s, 7 * s, "#1A0E06", 0.5)]
    back = Q([(-54, -8), (-48, -20), (48, -20), (54, -8)])
    out.append(K.path(sp(back), "#6A4A22"))
    # the babies: swaddled bodies, round heads, closed eyes, rosy cheeks
    for k, (bx, by, ang) in enumerate(((-18, -20, -8), (18, -18, 10))):
        sw = Q([(bx - 18, by + 6), (bx - 14, by - 6), (bx + 14, by - 8), (bx + 20, by + 4), (bx + 10, by + 12), (bx - 12, by + 12)])
        out.append(form(P, sp(sw), ("#FFFFFF", "#E8E0D0", "#8A7A68"), (-0.6, -0.8), K.bbox(sw), core=0.4, lit=0.5, edge="#5A4A3A", edge_op=0.5,
                        extra=[K.stroke_line(Q([(bx - 10, by - 4), (bx + 4, by + 8)]), "#B8A890", 1, 0.6), K.stroke_line(Q([(bx, by - 6), (bx + 12, by + 6)]), "#B8A890", 1, 0.6)]))
        hx_, hy_ = Q([(bx - 16 if k == 0 else bx + 18, by - 8)])[0]
        hd = ellipse(hx_, hy_, 9 * s, 8.5 * s, 16)
        out.append(form(P, sp(hd), ("#FFE8D8", "#E8B898", "#8A5A40"), (-0.6, -0.8), K.bbox(hd), core=0.35, lit=0.6, edge="#6A3A2A", edge_op=0.5, sd=3 * s,
                        extra=[soft(P, sp(ellipse(hx_ + 3 * s, hy_ + 2 * s, 2.6 * s, 2 * s, 8)), "#F28A80", 0.5, 1.2 * s)]))
        for sg in (-1, 1):
            out.append(K.stroke_line([(hx_ + sg * 3.6 * s - 1.6 * s, hy_ - 0.6 * s), (hx_ + sg * 3.6 * s, hy_ + 0.4 * s), (hx_ + sg * 3.6 * s + 1.6 * s, hy_ - 0.6 * s)],
                                     "#4A2A1A", 0.9, 0.85))
        out.append(K.path(sp(ellipse(hx_, hy_ - 6 * s, 7 * s, 3.4 * s, 10)), "#8A5A30", 0.7))
    hand = Q(ellipse(-2, -26, 4, 3.4, 10))
    out.append(form(P, sp(hand), ("#FFE8D8", "#E8B898", "#8A5A40"), (-0.6, -0.8), K.bbox(hand), core=0.3, lit=0.6, sd=1.5))
    front = Q([(-58, -10), (58, -10), (50, 10), (-50, 10)])
    weave = [K.stroke_line(Q([(-56 + k * 8, -10), (-50 + k * 8, 10)]), "#3A2410", 1.2, 0.5) for k in range(14)]
    weave += [K.stroke_line(Q([(-56, -10 + k * 5), (56, -10 + k * 5)]), "#E8C080", 1.0, 0.45) for k in range(5)]
    out.append(form(P, sp(front), ("#E8C080", "#9A6A30", "#3A2410"), (-0.6, -0.8), K.bbox(front), core=0.45, lit=0.5, extra=weave, edge="#2A1806", edge_op=0.6))
    return "".join(out)


def woodpecker(P, x, y, s, seed):
    """Picus, the woodpecker sacred to Mars, who brought the twins food: black and white barred, a red crown."""
    def Q(pts):
        return place(pts, x, y, s)
    body = Q([(-6, -20), (2, -24), (8, -16), (8, 6), (4, 18), (2, 30, 1), (-2, 18), (-6, 4)])
    out = [form(P, sp(body), ("#F2F2F2", "#2A2A2A", "#050505"), (-0.6, -0.8), K.bbox(body), core=0.4, lit=0.4, sd=2,
                extra=[K.stroke_line(Q([(-4, -6 + k * 5), (6, -4 + k * 5)]), "#F2F2F2", 1.2, 0.8) for k in range(4)])]
    head = Q([(-8, -22), (-2, -30), (6, -28), (8, -20), (0, -18)])
    out.append(K.path(sp(head), "#1A1A1A"))
    out.append(K.path(sp(Q([(-4, -28), (2, -32), (8, -28), (2, -26)])), "#D8302A"))
    out.append(K.path(lp(Q([(-8, -24), (-20, -23), (-8, -21)])), "#3A3A3A"))
    out.append(f'<circle cx="{Q([(-3, -24)])[0][0]:.1f}" cy="{Q([(-3, -24)])[0][1]:.1f}" r="{1 * s:.1f}" fill="#FFF"/>')
    return "".join(out)


@plate("romulus-and-remus")
def romulus_and_remus_p():
    P = Plate("myp-rr")
    rnd = random.Random(7)
    sx, sy = 120, 300
    L = (-0.85, -0.45)
    art = [K.sky_grad(P, [(0, "#3A3A6A"), (0.35, "#8A6A8A"), (0.6, "#E8A078"), (0.72, "#FFD8A0")], 0, 360)]
    art.append(K.sky_wash(P, 3, ["#B07A90", "#5A5A8A", "#FFC890"], 12, (-40, -40, 640, 340), (80, 160), (0.12, 0.25), 30))
    art.append(screen(glow(P, sx, sy, 300, "#FFD890", 0.55)))
    art.append(K.strata(P, 4, 200, -40, 640, 10, ("#FFE0C0", "#B07A88", "#5A4A70"), L=(-1, 0.3), n=6, op=0.8))
    # the seven hills: the Palatine with its huts far off, umbrella pines
    hills = K.ridge(3, -20, 640, 360, 318, 18, 14, 0.4, peaks=[(420, 300, 120)])
    art.append(form(P, sp(hills), ("#9A7A8A", "#5A4A6A", "#2A2240"), L, K.bbox(hills), core=0.3, lit=0.3, sd=8))
    for (px, py, r) in ((380, 300, 18), (430, 296, 22), (500, 306, 16)):
        art.append(K.stroke_line([(px, py + 18), (px + 2, py)], "#2A2030", 2.4, 0.9))
        art.append(K.path(sp(ellipse(px + 2, py - 4, r, r * 0.42, 14)), "#3A3048"))
    for (hx, hy) in ((320, 318), (340, 316), (356, 320)):
        art.append(K.path(sp([(hx - 6, hy + 4), (hx - 6, hy - 2), (hx, hy - 8, 1), (hx + 6, hy - 2), (hx + 6, hy + 4)]), "#4A3A50"))
    art.append(K.haze(P, 290, 370, "#F2C0A0", 0.0, 0.55))
    # the Tiber, wide and slow, gold with the evening
    art.append(K.water(P, 5, 360, 470, [(0, "#E8B088"), (0.5, "#8A6A78"), (1, "#3A3048")], ["#FFE0B0", "#4A3A50", "#C89080"], n=130, sun_x=sx, glint_w=30))
    # the near bank: reeds, grass, the roots of the fig tree
    bank = [(-20, 620), (-20, 440), (80, 452), (200, 446), (330, 454), (460, 446), (640, 436), (640, 620)]
    art.append(form(P, sp(bank), ("#9A8A4A", "#3A3418", "#100E06"), L, K.bbox(bank), core=0.4, lit=0.35, sd=12))
    art.append(K.grass(5, -10, 610, 440, 600, ["#6A6A2A", "#A89A50", "#3A3818", "#C8A860"], 380, (6, 16)))
    for k in range(30):
        x = rnd.uniform(-10, 160) if k < 20 else rnd.uniform(500, 610)
        h = rnd.uniform(40, 90)
        art.append(K.taper([(x, 470), (x + rnd.uniform(-6, 6), 470 - h * 0.6), (x + rnd.uniform(-10, 10), 470 - h)], 2.4, 0.6, rnd.choice(["#4A4A20", "#6A6A30", "#2A2A10"])))
        if k % 4 == 0:
            art.append(K.path(sp(ellipse(x, 470 - h + 6, 2.6, 9, 10)), "#4A3418"))
    # the Ficus Ruminalis: a fig tree leaning over the bank, its broad lobed leaves catching the light
    trunk = [(560, 620), (548, 520), (532, 440), (500, 360), (460, 300), (420, 260), (436, 252), (474, 284), (520, 330), (560, 380), (590, 460), (610, 540), (620, 620)]
    art.append(form(P, sp(trunk), ("#B8A890", "#5A4A3A", "#140E08"), L, K.bbox(trunk), core=0.6, lit=0.4, edge="#000000", edge_op=0.5, rim_col="#FFD8A0", rim_d=2,
                    rim_src=(sx, sy, 600)))
    for (cx, cy, rx, ry) in ((440, 200, 120, 70), (560, 240, 90, 70), (340, 230, 70, 40)):
        art.append(f'<g {P.rough(10, 0.05, int(cx))}>' + K.foliage(P, int(cx), cx, cy, rx, ry, ("#9AAA60", "#3A5228", "#0E1808"), L=L, n=30, leaf=(8, 16), dabs=180, sd=2) + "</g>")
    art.append(woodpecker(P, 470, 300, 0.55, 3))
    # the she-wolf and the twins
    art.append(K.cast_shadow(P, 310, 492, 160, 10, "#1A0E06", 0.55))
    art.append(twins_basket(P, 176, 482, 1.12, 4))
    art.append(lying_wolf_g(P, 340, 494, 1.16, 9, L=L, rim_src=(sx, sy, 520)))
    art.append(K.vignette(P, "#0A0610", 0.45, 0.6))
    art.append(K.text_scrim(P, 480, 600, "#0A0610", 0.7))
    text = [multi(300, 100, [("Romulus ", "#FFF4E8"), ("&", "#F2A060"), (" Remus", "#FFF4E8")], DMS, 58, max_w=440, shadow="#000000", sdy=2.5),
            tx(300, 130, "ROMAN · THE SHE-WOLF OF THE TIBER", CINZEL, 17, "#FFF0E0", ls=2.5, max_w=440),
            tx(300, 534, "Rome began with a mother’s kindness.", SERIF_IT, 26, "#FFF4E4", max_w=440)]
    return P.render(art, text, seed=171, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ the dragon's pearl — a long dragon in the clouds (plate, after the Song ink masters)
INK_ = "#15130F"


def ink_cloud(P, seed, cx, cy, w, h, dark=0.55):
    """A cloud as the ink painters made it: a pale wet wash that blooms and pools darker at its curling edges."""
    rnd = random.Random(seed)
    out = []
    for k in range(7):
        x, y = cx + rnd.uniform(-w / 2, w / 2), cy + rnd.uniform(-h / 2, h / 2)
        r = rnd.uniform(0.3, 0.55) * w * 0.5
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * rnd.uniform(0.4, 0.7):.1f}" fill="{INK_}" opacity="{rnd.uniform(0.08, 0.18) * dark / 0.55:.2f}"/>')
    body = f'<g {P.rough_blur(18, 0.02, 6, seed)}>{"".join(out)}</g>'
    curls = []
    for k in range(2):
        x, y = cx + rnd.uniform(-w / 2.5, w / 2.5), cy + rnd.uniform(-h / 3, h / 3)
        r = rnd.uniform(18, 30)
        spiral = [(x + math.cos(a) * r * (1 - a / 12), y + math.sin(a) * r * 0.7 * (1 - a / 12)) for a in [i * 0.5 for i in range(20)]]
        curls.append(K.stroke_line(spiral, INK_, rnd.uniform(1.2, 2.4), rnd.uniform(0.25, 0.5)))
    return body + f'<g {P.rough(2, 0.1, seed)}>{"".join(curls)}</g>'


def long_dragon_ink(P, spine, w0, seed, hidden=()):
    """The body of the long (lung): a serpent body swelling and tapering, a dorsal crest of flame-like spines, belly
    scutes, scales laid as overlapping ink crescents, ink-wash modelling; segments in `hidden` (index ranges) are lost
    in cloud. Returns the art."""
    A = K.catmull(spine, 8)
    n = len(A)
    ws = [w0 * (0.55 + 0.45 * math.sin(math.pi * min(1, 0.15 + i / n * 0.95))) * (1 - 0.7 * max(0, i / n - 0.8) / 0.2) for i in range(n)]
    pts = K.limb(A, [w / 2 for w in ws], [w / 2 for w in ws], n=1)
    d = sp(pts)
    rnd = random.Random(seed)
    sc = []
    for i in range(2, n - 2, 2):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        for j in (-0.32, 0.0, 0.32):
            cx, cy = x - ty_ * ws[i] * j, y + tx_ * ws[i] * j
            r = ws[i] * 0.18
            sc.append(f'<path d="M {cx - ty_ * r:.1f} {cy + tx_ * r:.1f} Q {cx - tx_ * r * 1.3:.1f} {cy - ty_ * r * 1.3:.1f} {cx + ty_ * r:.1f} {cy - tx_ * r:.1f}" '
                      f'stroke="{INK_}" stroke-width="{rnd.uniform(0.8, 1.4):.1f}" fill="none" opacity="{rnd.uniform(0.45, 0.8):.2f}"/>')
    belly = K.limb(A, [-w * 0.25 for w in ws], [w * 0.5 for w in ws], n=1)
    scutes = []
    for i in range(2, n - 2, 2):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        p0 = (x + ty_ * ws[i] * 0.25, y - tx_ * ws[i] * 0.25)
        p1 = (x + ty_ * ws[i] * 0.5, y - tx_ * ws[i] * 0.5)
        scutes.append(K.stroke_line([p0, p1], INK_, 1.0, 0.5))
    crest = []
    for i in range(3, n - 3, 3):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        base_ = (x - ty_ * ws[i] * 0.5, y + tx_ * ws[i] * 0.5)
        tip = (base_[0] - ty_ * ws[i] * 0.55 - tx_ * ws[i] * 0.3, base_[1] + tx_ * ws[i] * 0.55 - ty_ * ws[i] * 0.3)
        crest.append(K.path(sp([(base_[0] - tx_ * 5, base_[1] - ty_ * 5), tip + (1,), (base_[0] + tx_ * 6, base_[1] + ty_ * 6)]), INK_, 0.85))
    body = form(P, d, ("#E8E0C8", "#8A8270", "#2A2620"), (-0.5, -0.8), K.bbox(pts), core=0.55, lit=0.4,
                extra=[K.path(sp(belly), "#D8CCA8", 0.55)] + sc + scutes, edge=INK_, edge_op=0.8)
    return "".join(crest) + body


def dragon_head_ink(P, x, y, s, ang, seed, flip=False):
    """The head of a Chinese dragon: camel's head, deer's antlers, a long snout with flaring nostrils, open jaws,
    the long whiskers (feelers) and the beard, a mane streaming back. Faces left; (x, y) = the back of the skull."""
    def Q(pts):
        return place(pts, x, y, s, flip, ang)
    out = []
    mane = Q([(-4, -18), (20, -30), (46, -22), (60, -6), (44, 0), (60, 12), (36, 14), (40, 30), (14, 18), (0, 16)])
    out.append(K.path(sp(mane), INK_, 0.75))
    for k in range(8):
        a_ = Q([(4 + k * 6, -14 + k * 3)])[0]
        b_ = Q([(30 + k * 5, -24 + k * 6)])[0]
        out.append(K.stroke_line([a_, b_], "#5A5244", 1.2, 0.6))
    upper = Q([(0, -16), (-22, -20), (-44, -16), (-62, -16), (-72, -12), (-74, -4, 1), (-60, -2), (-40, 0), (-20, 2), (0, 4)])
    lower = Q([(0, 6), (-18, 8), (-38, 14), (-56, 20), (-64, 26, 1), (-50, 24), (-30, 20), (-10, 18), (2, 12)])
    out.append(form(P, sp(lower), ("#E8E0C8", "#8A8270", "#2A2620"), (-0.5, -0.8), K.bbox(lower), core=0.5, lit=0.4, edge=INK_, edge_op=0.85))
    out.append(K.path(sp(Q([(-8, 4), (-40, 4), (-60, 0), (-56, 14), (-34, 12), (-10, 10)])), "#8A2A20", 0.8))
    for k in range(6):
        a_ = Q([(-58 + k * 8, -2)])[0]
        out.append(K.path(lp([a_, (a_[0] + 2.5 * s, a_[1] + 5 * s), (a_[0] + 5 * s, a_[1])]), "#F6F0E0", 0.95))
    out.append(form(P, sp(upper), ("#E8E0C8", "#8A8270", "#2A2620"), (-0.5, -0.8), K.bbox(upper), core=0.5, lit=0.45, edge=INK_, edge_op=0.85,
                    extra=[K.stroke_line(Q([(-30, -16), (-24, -10), (-14, -12)]), INK_, 1.4, 0.8)]))
    # brow ridge and the eye, fierce
    ex, ey = Q([(-20, -12)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{5 * s:.1f}" ry="{3.6 * s:.1f}" fill="#F2D060" stroke="{INK_}" stroke-width="1.2"/>'
               f'<circle cx="{ex - 0.5:.1f}" cy="{ey:.1f}" r="{1.8 * s:.1f}" fill="{INK_}"/>')
    out.append(K.stroke_line(Q([(-30, -20), (-20, -24), (-8, -20)]), INK_, 2.2, 0.85))
    # antlers
    for off in (0, 7):
        base_ = (-6 + off, -20)
        main = Q([base_, (2 + off, -40), (14 + off, -54), (28 + off, -60)])
        out.append(K.taper(main, 5 * s, 1.6 * s, "#4A4236"))
        for bt in ((2 + off, -40, -6, -54), (14 + off, -54, 10 + off, -70)):
            out.append(K.taper(Q([(bt[0], bt[1]), (bt[2], bt[3])]), 3.4 * s, 1 * s, "#4A4236"))
    # whiskers: two long feelers flowing back from the snout, and the beard
    for k, (dx, dy) in enumerate(((-70, -10), (-66, -6))):
        wh = Q([(dx, dy), (dx - 20, dy - 20 - k * 10), (dx + 10, dy - 50 - k * 6), (dx + 60, dy - 52 - k * 10), (dx + 110, dy - 30 - k * 14)])
        out.append(K.taper(K.catmull(wh, 6), 2.4 * s, 0.6, INK_, 0.85))
    beard = Q([(-30, 18), (-28, 34), (-20, 44, 1), (-14, 32), (-6, 40, 1), (-4, 22)])
    out.append(K.path(sp(beard), INK_, 0.7))
    return "".join(out)


def flaming_pearl(P, x, y, r, seed):
    """The flaming pearl of wisdom: a luminous orb ringed with tongues of red-gold flame."""
    rnd = random.Random(seed)
    out = [screen(glow(P, x, y, r * 5, "#FFD890", 0.55))]
    for k in range(9):
        a = math.radians(k * 40 + rnd.uniform(-8, 8))
        tip = (x + math.cos(a) * r * 2.3, y + math.sin(a) * r * 2.3)
        b1 = (x + math.cos(a - 0.35) * r * 1.05, y + math.sin(a - 0.35) * r * 1.05)
        b2 = (x + math.cos(a + 0.35) * r * 1.05, y + math.sin(a + 0.35) * r * 1.05)
        mid = (x + math.cos(a + 0.25) * r * 1.7, y + math.sin(a + 0.25) * r * 1.7)
        out.append(K.path(sp([b1, mid, tip + (1,), b2]), rnd.choice(["#D8402A", "#E8702A"]), 0.85))
    out.append(K.path(sp(ellipse(x, y, r, r, 24)), P.rad([(0, "#FFFFFF"), (0.5, "#F6F2FF"), (0.85, "#C8D0F0"), (1, "#8A90C0")], cx=0.38, cy=0.36, r=0.66)))
    out.append(f'<ellipse cx="{x - r * 0.35:.1f}" cy="{y - r * 0.38:.1f}" rx="{r * 0.25:.1f}" ry="{r * 0.18:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def claw(P, x, y, s, ang, seed):
    """A dragon's foreleg ending in an eagle's claw, five talons spread (the imperial five-clawed dragon)."""
    def Q(pts):
        return place(pts, x, y, s, False, ang)
    leg = Q(K.limb([(0, 0), (14, 16), (30, 26)], [8, 6, 5], [8, 6, 5]))
    out = [form(P, sp(leg), ("#E8E0C8", "#8A8270", "#2A2620"), (-0.5, -0.8), K.bbox(leg), core=0.5, lit=0.4, edge=INK_, edge_op=0.85)]
    for k in range(5):
        a = math.radians(-50 + k * 25)
        base_ = (30, 26)
        tip = (30 + math.cos(a) * 18, 26 + math.sin(a) * 18)
        mid = (30 + math.cos(a - 0.3) * 12, 26 + math.sin(a - 0.3) * 12)
        out.append(K.taper(Q([base_, mid, tip]), 4.4 * s, 0.8, INK_, 0.9))
    return "".join(out)


@plate("the-dragons-pearl")
def the_dragons_pearl_p():
    P = Plate("myp-dp")
    rnd = random.Random(8)
    # aged silk: warm grey with the weave and stains of age
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#D6CAA8")]
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#8A7A58" opacity="0.5" {P.mottle(0.01, 0.6, 3, (0.4, 0.34, 0.22))}/>')
    art.append(K.vignette(P, "#5A4A30", 0.45, 0.6))
    # ink-wash storm clouds the dragon swims through
    for k, (cx, cy, w, h) in enumerate(((140, 160, 300, 120), (460, 120, 260, 100), (300, 300, 380, 140), (100, 420, 280, 120), (480, 430, 300, 120))):
        art.append(ink_cloud(P, 10 + k, cx, cy, w, h, 0.6))
    # the pearl, high right
    px, py = 446, 262
    art.append(flaming_pearl(P, px, py, 22, 3))
    # the dragon: body coiling up out of the lower clouds, the far coil lost in mist
    spine = [(214, 272), (170, 306), (160, 360), (210, 400), (300, 406), (370, 440), (350, 490), (250, 500), (140, 486), (70, 496)]
    art.append(long_dragon_ink(P, spine, 50, 5))
    art.append(claw(P, 176, 350, 1.1, 120, 1))
    art.append(claw(P, 330, 420, 1.0, 40, 2))
    # mist veiling part of the body (lost and found)
    art.append(f'<g {P.blur(12)}><ellipse cx="300" cy="500" rx="110" ry="30" fill="#E8DEC0" opacity="0.65"/><ellipse cx="190" cy="370" rx="60" ry="24" fill="#E8DEC0" opacity="0.5"/></g>')
    art.append(dragon_head_ink(P, 220, 274, 1.3, 8, 7, flip=True))
    # the artist's red seal
    art.append(K.path(lp([(498, 470), (530, 470), (530, 502), (498, 502)]), "#B8302A", 0.9))
    art.append(K.stroke_line([(504, 478), (524, 478)], "#F2D8C8", 1.6, 0.8, smooth=False))
    art.append(K.stroke_line([(514, 474), (514, 498)], "#F2D8C8", 1.6, 0.8, smooth=False))
    art.append(K.stroke_line([(504, 492), (524, 492)], "#F2D8C8", 1.6, 0.8, smooth=False))
    text = [tx(300, 98, "The Dragon’s Pearl", SERIF_IT, 56, INK_, max_w=440),
            tx(300, 128, "CHINESE · THE PEARL OF WISDOM", CINZEL, 17, "#8A2A20", ls=2.5, max_w=440),
            tx(300, 540, "Chase wisdom like the dragon chases the pearl", SERIF_IT, 21, INK_, max_w=430)]
    return P.render(art, text, seed=181, edge=1.6, bristle=0.35, grain=0.22)


# ================================================================ amaterasu — the sun goddess comes out of the rock cave (plate, woodblock manner)
def rooster_g(P, x, y, s, seed, flip=False, L=(1, -0.3)):
    """A long-tailed rooster (onagadori, the 'long-crowing bird' of the myth) standing on the perch, head up to crow:
    an upright carriage, full breast, red comb and wattles, golden hackles flowing down the neck and saddle, white
    body, dark sickle feathers arching up and falling in long ribbons. Faces right (flip -> left); feet at (x, y)."""
    def Q(pts):
        return place(pts, x, y, s, flip)
    rnd = random.Random(seed)
    out = []
    for k in range(7):
        p0 = (-32, -50)
        up = (-52 - k * 3, -96 + k * 6)
        over = (-84 - k * 6, -70 + k * 4)
        tip = (-92 - k * 8 + rnd.uniform(-4, 4), 10 + k * 14)
        out.append(K.taper(Q(K.catmull([p0, up, over, tip], 6)), 5.5 * s, 0.6, rnd.choice(["#1A2440", "#24345A", "#2A4A44", "#101830"]), 0.95))
        out.append(K.stroke_line(Q(K.catmull([p0, up, over], 5)), "#6A8AB8", 0.8, 0.45))
    body = Q([(18, -72, 1), (6, -70), (12, -60), (16, -46), (14, -30), (6, -20), (-8, -16), (-24, -22), (-34, -34), (-38, -48), (-30, -52), (-18, -48),
              (-10, -56), (-6, -70), (-2, -80), (8, -82)])
    out.append(form(P, sp(body), ("#FFFFFF", "#ECE6DA", "#7A7068"), L, K.bbox(body), core=0.4, lit=0.5, edge="#1E2440", edge_op=0.8, sd=4 * s,
                    extra=[K.scallops(seed, K.bbox(body), 40, 100, ["#B8B0A0", "#FFFFFF"], (1.4 * s, 2.6 * s), (0.35, 0.6), (0.6, 1.0), inside=K.inside_poly(body))]))
    hackle = Q([(-4, -80), (2, -74), (4, -58), (-2, -44), (-14, -40), (-26, -44), (-14, -54), (-8, -68)])
    out.append(form(P, sp(hackle), ("#FFE8A0", "#E8A030", "#7A3A08"), L, K.bbox(hackle), core=0.35, lit=0.5, edge="#1E2440", edge_op=0.7, sd=3 * s,
                    extra=[K.stroke_line(Q([(-2 - k * 3, -76 + k * 2), (-6 - k * 4, -48 + k)]), "#7A3A08", 0.9, 0.55) for k in range(5)]))
    out.append(K.path(sp(Q([(-2, -82), (0, -90, 1), (4, -84), (6, -92, 1), (9, -85), (12, -91, 1), (13, -82), (6, -80)])), "#D8302A"))
    out.append(K.path(sp(Q([(10, -70), (14, -60), (8, -62)])), "#D8302A"))
    out.append(K.path(lp(Q([(14, -76), (24, -74), (14, -71)])), "#E8B040"))
    out.append(f'<circle cx="{Q([(8, -76)])[0][0]:.1f}" cy="{Q([(8, -76)])[0][1]:.1f}" r="{1.4 * s:.1f}" fill="#1A1410"/>')
    for lx in (-10, 0):
        out.append(K.taper(Q([(lx, -18), (lx + 1, -2), (lx + 1, 0)]), 2.6 * s, 2 * s, "#E8B040"))
        out.append(K.taper(Q([(lx + 1, 0), (lx + 8, 1)]), 1.6 * s, 1 * s, "#E8B040"))
    return "".join(out)


def sacred_mirror(P, cx, cy, r, seed):
    """The Yata no Kagami: a round bronze mirror, its polished face blazing with the light from the cave."""
    out = [screen(glow(P, cx, cy, r * 4, "#FFE8A0", 0.6))]
    out.append(K.path(sp(ellipse(cx, cy, r, r, 28)), "#8A6A2A"))
    out.append(K.path(sp(ellipse(cx, cy, r * 0.86, r * 0.86, 28)), P.rad([(0, "#FFFFFF"), (0.4, "#FFF4C8"), (0.8, "#F2C860"), (1, "#C8902A")], cx=0.4, cy=0.38, r=0.7)))
    out.append(K.stroke_line(ellipse(cx, cy, r, r, 28) + [ellipse(cx, cy, r, r, 28)[0]], "#2A1A08", 1.6, 0.9))
    return "".join(out)


def magatama_g(cx, cy, r, ang, col):
    pts = place([(0, -r), (r * 0.9, -r * 0.4), (r, r * 0.3), (r * 0.6, r * 0.9), (-r * 0.2, r * 1.1), (-r * 0.9, r * 1.6, 1), (-r * 0.7, r * 0.6), (-r * 0.9, -r * 0.2)],
                cx, cy, 1, False, ang)
    return K.path(sp(pts), col) + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.25:.1f}" fill="#1A1410" opacity="0.6"/>'


@plate("amaterasu")
def amaterasu_p():
    P = Plate("myp-am")
    rnd = random.Random(4)
    ink = "#1A2040"
    gx, gy = 410, 330          # the crack of light at the cave mouth
    # the world in darkness: Prussian blue bokashi, a scatter of stars
    art = [K.sky_grad(P, [(0, "#05081A"), (0.4, "#0E1A40"), (0.75, "#1E3266"), (1, "#0A1024")])]
    art.append(K.stars(3, (0, 0, 600, 320), 90, cols=("#FFFFFF", "#F2F0D8"), r=(0.6, 1.4)))
    hills = K.ridge(5, -20, 640, 420, 380, 20, 12, 0.4, peaks=[(120, 360, 120)])
    art.append(K.path(sp(hills), "#141C3A"))
    # rays of the returning sun: straight, ruled, gold as on a print
    art.append(K.rays(P, gx, gy, [150 + i * 9 for i in range(14)] + [-150 + i * 9 for i in range(10)], 560, [26, 10, 18], "#FFE080", 0.5, 2))
    art.append(screen(glow(P, gx, gy, 260, "#FFC860", 0.6)))
    # the rock cave: great boulders, the stone door rolled half aside
    cliff_ = [(330, 620), (330, 380), (350, 300), (380, 220), (430, 170), (500, 150), (640, 140), (640, 620)]
    art.append(form(P, sp(cliff_), ("#8A8070", "#3A3430", "#0E0C0A"), (-0.9, -0.3), K.bbox(cliff_), core=0.6, lit=0.4,
                    extra=[K.brush(3, K.bbox(cliff_), 120, lambda x, y: rnd.uniform(60, 120), ["#5A5048", "#14100C", "#8A8070"], (10, 30), (2, 4), (0.3, 0.6))],
                    edge=ink, edge_op=0.8, rim_col="#FFE0A0", rim_d=2.6, rim_src=(gx, gy, 300)))
    mouth = [(376, 470), (372, 380), (386, 310), (414, 274), (446, 290), (460, 360), (462, 470)]
    art.append(K.path(sp(mouth), P.rad([(0, "#FFFFFF"), (0.35, "#FFF6C8"), (0.7, "#FFD060"), (1, "#E89A30")], cx=0.5, cy=0.55, r=0.6)))
    for k, (bx, by, br) in enumerate(((560, 160, 50), (470, 190, 40), (612, 230, 44), (360, 300, 30), (600, 420, 50))):
        b_ = K.wobble(ellipse(bx, by, br, br * 0.8, 10), k, br * 0.15)
        art.append(form(P, sp(b_), ("#9A9080", "#3A342E", "#0E0C0A"), (-0.9, -0.3), K.bbox(b_), core=0.6, lit=0.35, edge=ink, edge_op=0.8,
                        rim_col="#FFE0A0", rim_d=2, rim_src=(gx, gy, 280)))
    door = [(444, 482), (440, 300, 1), (470, 268), (530, 262), (566, 280, 1), (572, 486, 1)]
    art.append(form(P, sp(door), ("#9A9080", "#4A443C", "#141210"), (-1, -0.2), K.bbox(door), core=0.55, lit=0.5, edge=ink, edge_op=0.85,
                    rim_col="#FFF0C0", rim_d=3, rim_src=(gx, gy, 200),
                    extra=[K.path(sp(K.wobble(ellipse(x, y, r_, r_ * 0.7, 9), int(x), 3)), "#4A6A3A", 0.6) for x, y, r_ in ((470, 330, 14), (520, 320, 10), (548, 380, 12))]))
    # ground before the cave
    ground = [(-20, 620), (-20, 470), (200, 462), (400, 470), (640, 466), (640, 620)]
    art.append(K.path(sp(ground), P.lin([(0, "#3A3A30"), (1, "#0E0E0C")], 0, 460, 0, 600, "userSpaceOnUse")))
    art.append(screen(glow(P, gx, 480, 200, "#FFC860", 0.35, ry=40)))
    # the sakaki tree with the mirror, the jewels and the paper streamers hung on it
    trunk = [(170, 480), (176, 400), (172, 320), (180, 250), (196, 200), (204, 204), (192, 260), (188, 330), (192, 410), (196, 480)]
    art.append(form(P, sp(trunk), ("#8A6A4A", "#3A2818", "#0E0804"), (0.9, -0.3), K.bbox(trunk), core=0.5, lit=0.4, edge=ink, edge_op=0.8))
    for (cx, cy, rx, ry) in ((150, 200, 80, 50), (230, 230, 70, 40), (120, 280, 60, 36), (200, 160, 60, 34)):
        art.append(f'<g {P.rough(8, 0.06, int(cx))}>' + K.foliage(P, int(cx + cy), cx, cy, rx, ry, ("#5A8A4A", "#1E3A22", "#081208"), L=(0.9, -0.3), n=20, leaf=(6, 10), dabs=120, sd=1.6) + "</g>")
    art.append(K.stroke_line([(186, 236), (186, 252)], "#C8A040", 1.4, 0.9))
    art.append(sacred_mirror(P, 186, 272, 22, 3))
    for k, (x0, y0) in enumerate(((124, 300), (236, 290))):
        art.append(K.stroke_line([(x0, y0), (x0 + 2, y0 + 70)], "#C8A040", 1.0, 0.8))
        for j in range(6):
            art.append(magatama_g(x0 + 2, y0 + 10 + j * 12, 4.2, 20 if k else -20, ["#3AB87A", "#E8402A", "#2A6AC8", "#F2C040"][j % 4]))
    for x0 in (156, 208):
        strip = [(x0, 298), (x0 + 8, 298), (x0 + 8, 312), (x0 + 2, 312), (x0 + 2, 326), (x0 + 10, 326), (x0 + 10, 342), (x0 + 4, 342), (x0 + 4, 356),
                 (x0 - 2, 356), (x0 - 2, 340), (x0 + 4, 340), (x0 + 4, 328), (x0 - 4, 328), (x0 - 4, 314), (x0, 314)]
        art.append(K.path(lp(strip), "#FFFFFF", 0.95))
        art.append(K.stroke_line(strip + [strip[0]], ink, 0.7, 0.7, smooth=False))
    # the perch of the long-crowing birds (from which the torii is said to come) and the roosters
    art.append(K.stroke_line([(40, 400), (310, 400)], "#C8302A", 7, 1, smooth=False))
    art.append(K.stroke_line([(30, 392), (320, 392)], "#1A1410", 5, 1, smooth=False))
    for x in (70, 280):
        art.append(K.stroke_line([(x, 392), (x, 480)], "#C8302A", 8, 1, smooth=False))
    art.append(rooster_g(P, 120, 392, 1.0, 5))
    art.append(rooster_g(P, 262, 392, 0.92, 6))
    # cartouche, as on the print
    art.append(K.path(lp([(62, 62), (292, 62), (292, 140), (62, 140)]), "#C8382A"))
    art.append(K.path(lp([(68, 68), (286, 68), (286, 134), (68, 134)]), "#F2E6CC"))
    art.append(K.stroke_line([(73, 73), (281, 73), (281, 129), (73, 129), (73, 73)], "#C8382A", 1.2, 0.8, smooth=False))
    art.append(K.text_scrim(P, 490, 600, "#05081A", 0.7))
    text = [tx(177, 120, "Amaterasu", SERIF_IT, 46, "#1A2040", max_w=200),
            tx(64, 168, "JAPANESE · THE SUN COMES BACK", CINZEL, 16, "#F2E6CC", ls=1.0, max_w=340, anchor="start"),
            tx(300, 534, "Light always finds its way out.", SERIF_IT, 28, "#FFF6E0", max_w=440)]
    return P.render(art, text, seed=191, edge=1.6, bristle=0.4, grain=0.2, streak=(0.012, 0.5))


# ================================================================ the churning of the ocean — samudra manthan (plate, Pahari miniature manner)
def puller(P, x, y, s, seed, flip=False, kind="deva"):
    """A figure hauling on the serpent-rope, braced and leaning back with the whole weight: front leg bent, back leg
    straight, arms reaching forward to the rope, in a short dhoti with a sash. Devas fair-blue and crowned; asuras
    dark with horned crowns. Faces left (flip -> right); (x, y) = between the feet; ~100 * s tall."""
    def Q(pts):
        return place(pts, x, y, s, flip)
    rnd = random.Random(seed)
    if kind == "deva":
        skin = ("#B8D0F0", "#5A80C0", "#1A2A50")
        cloth = ("#FFE070", "#E8A020", "#7A4A08")
    else:
        skin = ("#8A9A70", "#3A4A2A", "#0E140A")
        cloth = ("#F08060", "#B82A1A", "#4A0A04")
    line = "#2A1408"
    B = K.Body(P, (-0.5, -0.8))
    B.add(Q(K.limb([(6, -48), (12, -26), (20, -4)], [6, 4.5, 3.2], [7, 5.5, 3.2])), skin, core=0.4, lit=0.4)          # back leg, braced
    B.add(Q([(14, -6), (28, -2), (30, 1, 1), (14, 1)]), skin, core=0.3, lit=0.3)
    B.add(Q(K.limb([(10, -84), (-2, -78), (-14, -72), (-24, -70)], [4.5, 4, 3.4, 3], [4.5, 4, 3.4, 3])), skin, core=0.4, lit=0.4)  # far arm
    B.add(Q([(-8, -54), (12, -56), (18, -40), (22, -30, 1), (6, -34), (-14, -30, 1), (-10, -44)]), cloth, core=0.4, lit=0.5,
          extra=[K.stroke_line(Q([(0, -52), (-2, -34)]), cloth[2], 0.8, 0.6)])                                        # dhoti
    B.add(Q([(-6, -52), (-4, -70), (4, -84), (16, -90), (22, -84), (18, -66), (10, -54)]), skin, core=0.35, lit=0.45)  # torso leaning back
    B.add(Q(K.limb([(0, -48), (-10, -38), (-18, -22), (-26, -4)], [6.5, 5.5, 4, 3.2], [7, 6, 5, 3.2])), skin, core=0.35, lit=0.45)   # front leg
    B.add(Q([(-22, -6), (-36, -2), (-38, 1, 1), (-22, 1)]), skin, core=0.3, lit=0.3)
    B.add(Q(ellipse(18, -98, 7, 7.5, 12)), skin, core=0.35, lit=0.5)                                                       # head
    B.add(Q(K.limb([(14, -86), (2, -80), (-10, -74), (-22, -72)], [4.5, 4, 3.4, 3], [4.5, 4, 3.4, 3])), skin, core=0.3, lit=0.5)    # near arm
    out = [B.render(edge_col=line, edge_op=0.9)]
    if kind == "deva":
        out.append(K.path(lp(Q([(12, -104), (14, -116), (17, -108), (20, -118), (23, -108), (25, -116), (25, -104)])), "#F2C040"))
    else:
        out.append(K.path(sp(Q([(12, -104), (8, -114), (6, -122, 1), (14, -110), (22, -110), (30, -122, 1), (28, -112), (25, -104)])), "#E8D8B8"))
    out.append(f'<circle cx="{Q([(14, -99)])[0][0]:.1f}" cy="{Q([(14, -99)])[0][1]:.1f}" r="{1.0 * s:.1f}" fill="{line}"/>')
    sash = Q([(14, -84), (24, -70), (30, -54), (40, -46)])
    out.append(K.taper(sash, 2.6 * s, 1, cloth[0], 0.9))
    return "".join(out)


def milk_ocean(P, y0, y1, seed):
    """The ocean of milk as the miniaturists painted water: a cream ground, and wave-crests drawn as rows of little
    curling scallops, with a pale blue wash in the troughs."""
    rnd = random.Random(seed)
    out = [K.sky_grad(P, [(0, "#E8E8D8"), (1, "#C8D0C8")], y0, y1)]
    rows = []
    y = y0 + 6
    k = 0
    while y < y1:
        step = 10 + (y - y0) * 0.04
        for x in range(-20 + (k % 2) * 9, 620, 18):
            rows.append(f'<path d="M {x} {y:.1f} q 6 -7 12 0 q -3 -1 -6 2" stroke="#7A8AA8" stroke-width="1.1" fill="none" opacity="0.55"/>')
        y += step
        k += 1
    out.append("".join(rows))
    return "".join(out)


@plate("the-churning-of-the-ocean")
def the_churning_of_the_ocean_p():
    P = Plate("myp-ch")
    rnd = random.Random(3)
    # the painted page: a gold-flecked border in red, an inner field of night and dawn
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#A8281E")]
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#6A0A08" opacity="0.4" {P.mottle(0.02, 0.6, 4)}/>')
    for k in range(48):
        x = 20 + (k % 24) * 24
        y = 26 if k < 24 else 574
        art.append(K.path(sp([(x, y - 6), (x + 5, y), (x, y + 6), (x - 5, y)]), "#F2C040", 0.85))
    field = [(40, 44, 1), (560, 44, 1), (560, 556, 1), (40, 556, 1)]
    art.append(K.path(sp(field), "#1A1A3A"))
    fd = sp(field)
    inner = [K.sky_grad(P, [(0, "#1A1A4A"), (0.5, "#4A3A6A"), (0.8, "#E89A6A"), (1, "#FFD8A0")], 44, 330)]
    inner.append(K.stars(5, (40, 44, 560, 260), 70, cols=("#FFF2C8", "#FFFFFF")))
    # the moon, first of the treasures, rising from the churn
    inner.append(screen(glow(P, 150, 150, 60, "#FFF6D8", 0.6)))
    cres = ellipse(150, 150, 20, 20, 24, a0=60, a1=300) + [(150 + 20 * math.cos(math.radians(a)) * 0.45 - 4, 150 + 20 * math.sin(math.radians(a))) for a in range(300, 59, -20)]
    inner.append(K.path(sp(cres), "#FFF6E0"))
    inner.append(milk_ocean(P, 330, 560, 3))
    # Mount Mandara: a tall peak built of rounded rock masses in the miniaturists' way, trees clinging to its ledges
    mtn = [(220, 420), (236, 360), (250, 300), (266, 236), (282, 190), (300, 164), (318, 190), (334, 236), (350, 300), (364, 360), (380, 420)]
    inner.append(form(P, sp(mtn), ("#D8B88A", "#8A6A48", "#2A1A0E"), (-0.6, -0.8), K.bbox(mtn), core=0.5, lit=0.5, edge="#2A1408", edge_op=0.8))
    lumps = []
    for k in range(34):
        y = rnd.uniform(180, 410)
        hw = (y - 164) * 0.32
        x = 300 + rnd.uniform(-hw, hw) * 0.85
        r = rnd.uniform(9, 16)
        lumps.append((y, x, r))
    for y, x, r in sorted(lumps):
        lump = K.wobble(ellipse(x, y, r, r * 0.8, 12), int(x * y) % 97, r * 0.12)
        inner.append(form(P, sp(lump), ("#F2D8A8", "#A8845A", "#3A2412"), (-0.6, -0.8), K.bbox(lump), core=0.5, lit=0.55, edge="#3A2412", edge_op=0.7, sd=r * 0.4))
    for k in range(14):
        y = rnd.uniform(200, 400)
        hw = (y - 164) * 0.3
        x = 300 + rnd.uniform(-hw, hw) * 0.9
        inner.append(K.stroke_line([(x, y), (x, y - 10)], "#3A2412", 1.6, 0.9))
        inner.append(K.path(sp(K.wobble(ellipse(x, y - 14, 7, 6, 10), k, 1)), rnd.choice(["#2A5A2A", "#3A7A3A", "#1E4A2A"])))
        inner.append(K.path(sp(ellipse(x - 2, y - 16, 3, 2.4, 8)), "#8AB86A", 0.8))
    # Kurma's shell under the mountain
    shell = ellipse(300, 432, 120, 30, 32, a0=180, a1=360)
    inner.append(form(P, sp(shell + [(420, 440), (180, 440)]), ("#B8C890", "#5A7A4A", "#1E2A14"), (-0.6, -0.8), (180, 400, 420, 440), core=0.4, lit=0.5,
                      edge="#2A1408", edge_op=0.8, extra=[K.stroke_line(ellipse(300, 432, 120 - k * 26, 30 - k * 6.5, 24, a0=190, a1=350), "#2A3A18", 1.2, 0.6) for k in range(4)]))
    inner.append(K.path(sp([(176, 436), (160, 428), (150, 436), (164, 444)]), "#8AA070"))
    # Vasuki: wound three times round the mountain, the tail to the gods, the hoods to the asuras
    coils = []
    for k, y in enumerate((236, 300, 364)):
        hw = (y - 168) * 0.32 + 10
        coils.append([(300 - hw, y + 4), (300, y + 16), (300 + hw, y + 4)])
    for c in coils:
        inner.append(serpent_coil(P, c, [12, 13, 12], 3, pal=("#7AB8D8", "#1E5A8A", "#06182A"), belly="#F2E8B0"))
    rope_l = [(300 - 60, 368), (210, 380), (150, 380), (96, 384), (72, 380)]
    rope_r = [(300 + 60, 368), (400, 380), (460, 382), (520, 384), (548, 380)]
    inner.append(serpent_coil(P, rope_l, [9, 8.5, 8.5, 8, 8], 4, pal=("#7AB8D8", "#1E5A8A", "#06182A"), belly="#F2E8B0"))
    inner.append(serpent_coil(P, rope_r, [9, 8.5, 8, 6, 3], 5, pal=("#7AB8D8", "#1E5A8A", "#06182A"), belly="#F2E8B0"))
    # the hooded heads of Vasuki at the asuras' end
    hood = [(72, 380), (60, 362), (48, 358), (40, 370), (46, 384), (60, 392)]
    inner.append(form(P, sp(hood), ("#7AB8D8", "#1E5A8A", "#06182A"), (-0.6, -0.8), K.bbox(hood), core=0.4, lit=0.5, edge="#06182A", edge_op=0.8))
    inner.append(f'<circle cx="52" cy="370" r="1.6" fill="#F2D040"/>')
    # the asuras haul from the left, the devas from the right
    for k, x in enumerate((96, 136, 176)):
        inner.append(puller(P, x - 30, 402 + k * 2, 0.62, k, flip=True, kind="asura"))
    for k, x in enumerate((424, 466, 508)):
        inner.append(puller(P, x + 34, 402 + k * 2, 0.62, k + 5, flip=False, kind="deva"))
    # the pot of amrita rising from the milk, glowing
    inner.append(screen(glow(P, 300, 488, 90, "#FFE080", 0.85)))
    inner.append(K.rays(P, 300, 490, [-90 + i * 18 for i in range(-4, 5)], 90, [10, 6], "#FFF2B0", 0.35, 3))
    pot = [(284, 512), (278, 496), (282, 482), (292, 476), (290, 468), (310, 468), (308, 476), (318, 482), (322, 496), (316, 512)]
    inner.append(form(P, sp(pot), ("#FFF2B0", "#E0A030", "#6A3A08"), (-0.6, -0.8), K.bbox(pot), core=0.4, lit=0.6, edge="#3A1A04", edge_op=0.8))
    inner.append(K.path(sp(ellipse(300, 466, 12, 4, 14)), "#FFF8D0"))
    for k in range(5):
        inner.append(K.path(sp([(300 + (k - 2) * 5, 466), (300 + (k - 2) * 7, 452), (300 + (k - 2) * 5 + 2, 466)]), "#4A8A3A", 0.9))
    art.append(f'<g {P.clip(f"<path d=\"{fd}\"/>")}>{"".join(inner)}</g>')
    art.append(K.stroke_line([(40, 44), (560, 44), (560, 556), (40, 556), (40, 44)], "#F2C040", 3, 0.95, smooth=False))
    art.append(K.stroke_line([(34, 38), (566, 38), (566, 562), (34, 562), (34, 38)], "#1A0806", 1.2, 0.8, smooth=False))
    text = [tx(300, 100, "The Churning of the Ocean", SERIF_IT, 40, "#FFF4E0", max_w=460),
            tx(300, 128, "HINDU · SAMUDRA MANTHAN", CINZEL, 16, "#F2D8A8", ls=2.5, max_w=440),
            tx(300, 540, "From the churning came the nectar of life", SERIF_IT, 21, "#3A1A10", max_w=440)]
    return P.render(art, text, seed=201, edge=1.4, bristle=0.35, grain=0.22)


# ================================================================ the simurgh — a Persian miniature from a book of kings (plate)
def qaf_rock(P, pts, pal, seed):
    """The sponge-like rocks of the miniaturists: soft pastel masses with scalloped, outlined edges and inner contours."""
    d = sp(pts)
    rnd = random.Random(seed)
    x0, y0, x1, y1 = K.bbox(pts)
    inner = []
    for k in range(5):
        cx, cy = rnd.uniform(x0 + 10, x1 - 10), rnd.uniform(y0 + 8, y1 - 8)
        r = rnd.uniform(8, 20)
        inner.append(K.stroke_line(ellipse(cx, cy, r, r * 0.7, 10, a0=200, a1=340), pal[2], 1.1, 0.6))
    return form(P, d, pal, (-0.5, -0.8), (x0, y0, x1, y1), core=0.35, lit=0.5, extra=inner, edge="#2A1A30", edge_op=0.9)


def simurgh_g(P, cx, cy, s, seed):
    """The Simurgh in flight, as the Safavid painters drew her: a crested raptor's head, a long arched neck, wings
    raised with rows of scale-like coverts and long fingered primaries, and the tail of long ribbon plumes that loop
    and curl behind her. Faces left; (cx, cy) = the body."""
    def Q(pts):
        return place(pts, cx, cy, s)
    rnd = random.Random(seed)
    out = []
    # tail streamers: long ribbons looping back and down to the right
    cols = [("#3AA8C8", "#1E5A8A"), ("#E8B040", "#8A5A10"), ("#D84A3A", "#7A1A10"), ("#5AB86A", "#1E5A2A"), ("#8A5AB8", "#3A1A5A")]
    for k in range(5):
        p0 = (30, 6)
        sp_ = K.bez(p0, (90, -30 + k * 14), (150, 60 + k * 10), (200 + k * 8, 10 + k * 24), 14)
        pts = Q(K.plume(sp_, 18 - k, (0.4, 0.8, 1.0, 1.0, 0.9, 0.8, 0.6, 0.3)))
        c = cols[k]
        out.append(form(P, sp(pts), (mix(c[0], "#FFFFFF", 0.3), c[0], c[1]), (-0.5, -0.8), K.bbox(pts), core=0.3, lit=0.5, edge="#2A1A10", edge_op=0.85,
                        extra=[K.stroke_line(Q(sp_), "#F2D080", 1.0, 0.8)]))
        ex, ey = Q([sp_[-2]])[0]
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{7 * s:.1f}" ry="{5 * s:.1f}" fill="#F2C040" stroke="#2A1A10" stroke-width="0.8"/>'
                   f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{3.4 * s:.1f}" ry="{2.6 * s:.1f}" fill="#1E3A8A"/>')
    # far wing (behind)
    for k in range(9):
        t = k / 8
        out.append(feather(P, Q([(10 + t * 30, -20 - t * 12)])[0], -60 - t * 50, (90 - abs(t - 0.5) * 30) * s, 16 * s,
                           ("#3AA8C8", "#1E6A9A", "#0A2A4A"), seed + k, tip_round=0.5, L=(-0.5, -0.8), rachis="#F2D080", edge="#0A1A2A"))
    # body
    body = Q([(-30, -8), (-20, -20), (0, -24), (24, -18), (36, -2), (30, 12), (6, 16), (-20, 12)])
    out.append(form(P, sp(body), ("#FFE8A0", "#E0A030", "#7A4A10"), (-0.5, -0.8), K.bbox(body), core=0.35, lit=0.5, edge="#2A1A10", edge_op=0.85,
                    extra=[K.scallops(seed, K.bbox(body), 50, 90, ["#7A4A10", "#FFF2C0"], (2.4 * s, 4 * s), (0.5, 0.8), (0.7, 1.1), inside=K.inside_poly(body))]))
    # near wing raised: coverts in scale rows, primaries spread
    for k in range(11):
        t = k / 10
        out.append(feather(P, Q([(-6 + t * 36, -18 - t * 30)])[0], -110 + t * 70, (110 - abs(t - 0.4) * 40) * s, 18 * s,
                           [("#5AB86A", "#1E7A4A", "#0A2A1A"), ("#E8B040", "#C87A20", "#5A2A08"), ("#D84A3A", "#9A2A1A", "#3A0A04")][k % 3], seed + 20 + k,
                           tip_round=0.6, L=(-0.5, -0.8), rachis="#FFF2C0", edge="#2A1A10"))
    cov = Q([(-14, -20), (6, -46), (30, -66), (40, -50), (30, -26), (10, -16)])
    out.append(form(P, sp(cov), ("#8AD8E8", "#2A8AB8", "#0A2A4A"), (-0.5, -0.8), K.bbox(cov), core=0.3, lit=0.5, edge="#0A1A2A", edge_op=0.85,
                    extra=[K.scallops(seed + 3, K.bbox(cov), 60, 70, ["#F2D080", "#0A2A4A"], (2.6 * s, 4.4 * s), (0.6, 0.9), (0.8, 1.2), inside=K.inside_poly(cov))]))
    # neck, head with crest, hooked beak
    neck = Q([(-24, -12), (-40, -30), (-50, -52), (-62, -64), (-76, -66), (-84, -60), (-76, -54), (-64, -50), (-52, -34), (-34, -6)])
    out.append(form(P, sp(neck), ("#FFE8A0", "#E0A030", "#7A4A10"), (-0.5, -0.8), K.bbox(neck), core=0.35, lit=0.5, edge="#2A1A10", edge_op=0.85,
                    extra=[K.scallops(seed + 4, K.bbox(neck), 40, 120, ["#7A4A10", "#FFF2C0"], (2 * s, 3.4 * s), (0.5, 0.8), (0.6, 1.0), inside=K.inside_poly(neck))]))
    beak = Q([(-82, -64), (-96, -62), (-100, -56, 1), (-92, -58), (-82, -56)])
    out.append(K.path(sp(beak), "#F2D060"))
    out.append(K.stroke_line(beak + [beak[0]], "#2A1A10", 0.9, 0.9))
    ex, ey = Q([(-74, -62)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.2 * s:.1f}" fill="#FFFFFF" stroke="#2A1A10" stroke-width="0.8"/><circle cx="{ex - 0.4:.1f}" cy="{ey:.1f}" r="{1.1 * s:.1f}" fill="#000"/>')
    for k in range(5):
        base_ = Q([(-70 + k * 4, -66)])[0]
        tip = Q([(-60 + k * 10, -96 - k * 2)])[0]
        mid = Q([(-70 + k * 6, -84)])[0]
        out.append(K.taper([base_, mid, tip], 2.2 * s, 0.8, "#D84A3A", 0.95))
        out.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="{2.2 * s:.1f}" fill="#F2C040"/>')
    return "".join(out)


@plate("the-simurgh")
def the_simurgh_p():
    P = Plate("myp-sm")
    rnd = random.Random(5)
    # lapis border with gold illumination, a fine gold rule, the gold-leaf sky of the painting
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#1A2E7A")]
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#0A1440" opacity="0.4" {P.mottle(0.02, 0.6, 7)}/>')
    for k in range(40):
        t = k / 40 * 4
        side = int(t)
        u = t - side
        x, y = [(20 + u * 560, 22), (578, 20 + u * 560), (580 - u * 560, 578), (22, 580 - u * 560)][side]
        art.append(K.path(sp([(x, y - 5), (x + 5, y), (x, y + 5), (x - 5, y)]), "#E8C050", 0.9))
        art.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#D84A3A"/>')
    field = [(42, 42, 1), (558, 42, 1), (558, 558, 1), (42, 558, 1)]
    fd = sp(field)
    inner = [K.path(fd, P.lin([(0, "#F2D890"), (0.6, "#E8C068"), (1, "#C89A48")], 0, 42, 0, 558, "userSpaceOnUse"))]
    inner.append(f'<rect x="42" y="42" width="516" height="516" fill="#A87A28" opacity="0.35" {P.mottle(0.03, 0.6, 9, (0.6, 0.45, 0.16))}/>')
    # chinese-style cloud bands (tchi) in white and blue across the gold
    for k, (x0, y0, w) in enumerate(((60, 180, 160), (380, 150, 170), (250, 240, 120))):
        band = [(x0, y0), (x0 + w * 0.3, y0 - 10), (x0 + w * 0.6, y0 + 4), (x0 + w, y0 - 6)]
        inner.append(K.taper(K.catmull(band, 6), 10, 3, "#FFFFFF", 0.95, mid=14))
        inner.append(K.stroke_line(K.catmull(band, 6), "#3A6AB8", 1.2, 0.8))
        for j in range(3):
            cx_, cy_ = band[j + 1]
            inner.append(K.stroke_line([(cx_ + 6 * math.cos(a), cy_ + 6 * math.sin(a) * 0.7) for a in [i * 0.6 for i in range(12)]], "#3A6AB8", 1.0, 0.8))
    # Mount Qaf: pastel rocks rising in tiers on both sides, a stream between
    for k, (pts, pal) in enumerate((
            ([(42, 560), (42, 420), (70, 390), (110, 384), (150, 400), (180, 430), (200, 470), (210, 560)], ("#F2C8D8", "#C88AA8", "#6A3A5A")),
            ([(42, 450), (60, 470), (110, 470), (150, 500), (170, 560), (42, 560)], ("#C8E0F0", "#7AA8C8", "#2A4A6A")),
            ([(380, 560), (400, 480), (440, 440), (500, 420), (558, 412), (558, 560)], ("#D8E8B8", "#98B87A", "#3A5A2A")),
            ([(460, 560), (490, 500), (540, 486), (558, 490), (558, 560)], ("#F2D8B0", "#D0A070", "#6A4A20")))):
        inner.append(qaf_rock(P, pts, pal, k))
    stream = [(210, 560), (240, 520), (300, 500), (340, 520), (380, 560)]
    inner.append(K.path(sp(stream + [(360, 560), (230, 560)]), "#9AB8D8"))
    inner.append(K.stroke_line([(240, 528), (300, 510), (340, 528)], "#FFFFFF", 1.2, 0.8))
    # a cypress and a flowering almond, the painters' trees
    inner.append(K.path(sp([(492, 420), (480, 360), (488, 300), (496, 260, 1), (504, 300), (512, 360), (500, 420)]), "#2A5A3A"))
    inner.append(K.stroke_line([(496, 270), (496, 416)], "#4A8A5A", 1, 0.6))
    trunk = [(100, 392), (98, 330), (90, 290), (108, 300), (112, 330), (114, 392)]
    inner.append(K.path(sp(trunk), "#6A4A30"))
    for k in range(60):
        a = rnd.uniform(0, 2 * math.pi)
        r_ = rnd.random() ** 0.5 * 50
        x, y = 100 + math.cos(a) * r_, 280 + math.sin(a) * r_ * 0.6
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.6, 3):.1f}" fill="{rnd.choice(["#FFFFFF", "#F2B8C8", "#E890A8"])}" stroke="#8A4A5A" stroke-width="0.4"/>')
    # small birds who came seeking her
    for (bx, by) in ((150, 120), (176, 108), (420, 330), (446, 318), (300, 120)):
        inner.append(K.path(sp([(bx - 6, by), (bx - 2, by - 4), (bx + 4, by - 2), (bx + 8, by - 6, 1), (bx + 6, by), (bx + 2, by + 3)]), "#3A2A20", 0.85))
    inner.append(simurgh_g(P, 290, 330, 1.25, 7))
    art.append(f'<g {P.clip(f"<path d=\"{fd}\"/>")}>{"".join(inner)}</g>')
    art.append(K.stroke_line([(42, 42), (558, 42), (558, 558), (42, 558), (42, 42)], "#E8C050", 2.4, 0.95, smooth=False))
    # the title cartouche
    cart = [(118, 58, 1), (482, 58, 1), (504, 100), (482, 142, 1), (118, 142, 1), (96, 100)]
    art.append(K.path(sp(cart), "#F6EEDA"))
    art.append(K.stroke_line(cart + [cart[0]], "#1A2E7A", 2, 0.95, smooth=False))
    art.append(K.text_scrim(P, 500, 560, "#000000", 0.0))
    text = [tx(300, 106, "The Simurgh", DMS, 46, "#1A2E7A", max_w=340),
            tx(300, 130, "PERSIAN · QUEEN OF THE BIRDS", CINZEL, 16, "#A8281E", ls=1.6, max_w=360)]
    return P.render(art, text, seed=211, edge=1.2, bristle=0.3, grain=0.2)


# ================================================================ baba yaga's hut — the izba on hen's legs in the dark wood (plate, after Bilibin)
def hen_leg(P, hip, hock, foot, s, seed, lift=0.0, L=(0.6, -0.8)):
    """A giant hen's leg: a feathered drumstick under the floor, the bare scaled shank bending at the hock, the foot
    with three long front toes and a hind toe, horn-black claws."""
    rnd = random.Random(seed)
    out = []
    thigh = K.limb([hip, K.lerp2(hip, hock, 0.45), hock], [30 * s, 34 * s, 13 * s], [32 * s, 36 * s, 13 * s])
    out.append(K.furry(P, thigh, ("#C8A880", "#6A4A30", "#1E1208"), L, seed, lambda x, y: 100, n=90, flen=(5 * s, 12 * s), rough=(3 * s, 0.1),
                       core=0.5, lit=0.4, edge="#0A0604", edge_op=0.6))
    fx, fy = foot
    fy -= lift
    shank = K.limb([hock, K.lerp2(hock, (fx, fy), 0.5), (fx, fy)], [12 * s, 10 * s, 9 * s], [12 * s, 10 * s, 9 * s])
    scales = []
    for k in range(12):
        p = K.lerp2(hock, (fx, fy), k / 12)
        scales.append(K.stroke_line([(p[0] - 9 * s, p[1]), (p[0], p[1] + 3 * s), (p[0] + 9 * s, p[1])], "#5A3A10", 1.1, 0.7))
    out.append(form(P, sp(shank), ("#FFD878", "#C88A28", "#5A3008"), L, K.bbox(shank), core=0.5, lit=0.5, extra=scales, edge="#2A1404", edge_op=0.7))
    for k, (ang, ln) in enumerate(((-160, 58), (-130, 64), (-100, 56), (20, 34))):
        a = math.radians(ang + (lift * 0.4 if k < 3 else 0))
        tip = (fx + math.cos(a) * ln * s, fy + math.sin(a) * ln * s * 0.35 + (ln * s * 0.25 if lift else 0))
        toe = K.limb([(fx, fy), K.lerp2((fx, fy), tip, 0.5), tip], [8 * s, 6 * s, 4 * s], [8 * s, 6 * s, 4 * s])
        out.append(form(P, sp(toe), ("#FFD878", "#C88A28", "#5A3008"), L, K.bbox(toe), core=0.5, lit=0.5, edge="#2A1404", edge_op=0.7))
        cl = (tip[0] + math.cos(a) * 12 * s, tip[1] + math.sin(a) * 4 * s + 6 * s)
        out.append(K.taper([tip, cl], 5 * s, 0.6, "#140A04"))
    return "".join(out)


def izba_g(P, cx, floor, w, seed, L=(0.6, -0.8), win_glow="#FFC860"):
    """A Russian log izba: notched log walls with round ends, a steep plank roof with carved bargeboards and a
    horse-head finial, a small window with painted shutters and carved frame glowing from within, moss on the roof."""
    rnd = random.Random(seed)
    s = w / 200
    out = []
    x0, x1 = cx - w / 2, cx + w / 2
    wall_top = floor - 120 * s
    # logs
    logs = []
    for k in range(9):
        y = floor - k * 13.5 * s
        log = [(x0 - 8 * s, y), (x1 + 8 * s, y), (x1 + 8 * s, y - 13 * s), (x0 - 8 * s, y - 13 * s)]
        logs.append(form(P, sp(log), ("#C89A6A", "#6A4428", "#1E1008"), L, K.bbox(log), core=0.45, lit=0.4, sd=4 * s, edge="#140A04", edge_op=0.6,
                         extra=[K.stroke_line([(x0, y - 6 * s + rnd.uniform(-2, 2)), (x1, y - 6 * s + rnd.uniform(-2, 2))], "#3A2010", 0.8, 0.5)]))
        for ex_ in (x0 - 8 * s, x1 + 8 * s):
            logs.append(f'<ellipse cx="{ex_:.1f}" cy="{y - 6.5 * s:.1f}" rx="{6 * s:.1f}" ry="{6.5 * s:.1f}" fill="#B88A5A" stroke="#2A1408" stroke-width="1"/>'
                        f'<ellipse cx="{ex_:.1f}" cy="{y - 6.5 * s:.1f}" rx="{3 * s:.1f}" ry="{3.2 * s:.1f}" fill="none" stroke="#6A4428" stroke-width="0.8"/>')
    out.append("".join(logs))
    # the window: carved frame (nalichnik) with a pointed pediment, shutters, warm light
    wx, wy, ww, wh = cx, floor - 64 * s, 46 * s, 50 * s
    out.append(screen(glow(P, wx, wy, 90 * s, win_glow, 0.55)))
    out.append(K.path(lp([(wx - ww / 2, wy - wh / 2), (wx + ww / 2, wy - wh / 2), (wx + ww / 2, wy + wh / 2), (wx - ww / 2, wy + wh / 2)]),
                      P.rad([(0, "#FFF2C0"), (0.6, "#FFC860"), (1, "#C86A20")])))
    out.append(K.stroke_line([(wx, wy - wh / 2), (wx, wy + wh / 2)], "#2A1408", 2.4 * s, 1, smooth=False))
    out.append(K.stroke_line([(wx - ww / 2, wy), (wx + ww / 2, wy)], "#2A1408", 2.4 * s, 1, smooth=False))
    frame = [(wx - ww / 2 - 8 * s, wy + wh / 2 + 6 * s), (wx - ww / 2 - 8 * s, wy - wh / 2 - 4 * s), (wx, wy - wh / 2 - 24 * s, 1),
             (wx + ww / 2 + 8 * s, wy - wh / 2 - 4 * s), (wx + ww / 2 + 8 * s, wy + wh / 2 + 6 * s)]
    out.append(K.stroke_line(frame, "#F2E2C0", 5 * s, 0.95, smooth=False))
    out.append(K.stroke_line(frame, "#2A6A8A", 1.6 * s, 0.9, smooth=False))
    for sg in (-1, 1):
        sh = [(wx + sg * ww / 2, wy - wh / 2), (wx + sg * (ww / 2 + 20 * s), wy - wh / 2), (wx + sg * (ww / 2 + 20 * s), wy + wh / 2), (wx + sg * ww / 2, wy + wh / 2)]
        out.append(form(P, lp(sh), ("#5AA0C8", "#2A5A8A", "#0A1A3A"), L, K.bbox(sh), core=0.4, lit=0.4, edge="#0A1A2A", edge_op=0.7,
                        extra=[K.path(sp(ellipse(wx + sg * (ww / 2 + 10 * s), wy, 5 * s, 9 * s, 12)), "#E8C050", 0.9)]))
    # roof: steep, plank, carved bargeboards, moss
    ridge_y = wall_top - 76 * s
    roof = [(x0 - 24 * s, wall_top + 6 * s), (cx, ridge_y), (x1 + 24 * s, wall_top + 6 * s)]
    planks = [K.stroke_line([(cx, ridge_y), (x0 - 24 * s + k * (w + 48 * s) / 10, wall_top + 6 * s)], "#1A0E06", 1.0, 0.5) for k in range(11)]
    moss = [K.path(sp(K.wobble(ellipse(rnd.uniform(x0, x1), rnd.uniform(ridge_y + 40 * s, wall_top), rnd.uniform(8, 18) * s, rnd.uniform(4, 8) * s, 10), k, 2)),
                   rnd.choice(["#4A6A2A", "#6A8A3A", "#2A4A1A"]), 0.8) for k in range(10)]
    out.append(form(P, lp(roof), ("#8A7A60", "#3A2E22", "#0E0A06"), L, K.bbox(roof), core=0.5, lit=0.4, extra=planks + moss, edge="#0A0604", edge_op=0.7))
    for sg in (-1, 1):
        board = [(cx, ridge_y - 4 * s), (cx + sg * (w / 2 + 28 * s), wall_top + 10 * s)]
        out.append(K.stroke_line(board, "#E8D8B8", 7 * s, 0.95, smooth=False))
        for k in range(10):
            p = K.lerp2(board[0], board[1], (k + 0.5) / 10)
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1] + 6 * s:.1f}" r="{3 * s:.1f}" fill="#E8D8B8"/>')
    out.append(K.path(sp([(cx - 4 * s, ridge_y), (cx - 8 * s, ridge_y - 18 * s), (cx + 4 * s, ridge_y - 30 * s), (cx + 18 * s, ridge_y - 26 * s, 1), (cx + 8 * s, ridge_y - 18 * s), (cx + 6 * s, ridge_y)]),
                      "#E8D8B8"))
    return "".join(out)


def skull_stake(P, x, base, h, seed, glow_col="#FFB030"):
    """A fence stake topped with a skull, its eye sockets burning (as in the tale, the skulls light up at dusk)."""
    out = [K.stroke_line([(x, base), (x + 1, base - h)], "#2A1A10", 6, 1, smooth=False),
           K.stroke_line([(x - 1.5, base), (x - 0.5, base - h)], "#8A6A4A", 1.4, 0.6, smooth=False)]
    sx, sy = x, base - h - 12
    out.append(screen(glow(P, sx, sy, 34, glow_col, 0.5)))
    skull = [(sx - 10, sy + 2), (sx - 11, sy - 8), (sx - 4, sy - 14), (sx + 6, sy - 13), (sx + 11, sy - 6), (sx + 10, sy + 4), (sx + 6, sy + 10), (sx - 6, sy + 10)]
    out.append(form(P, sp(skull), ("#FFF8E8", "#D8C8A8", "#5A4A30"), (0.6, -0.8), K.bbox(skull), core=0.4, lit=0.5, edge="#1A1008", edge_op=0.7, sd=2))
    for ex in (-4.5, 4.5):
        out.append(f'<ellipse cx="{sx + ex:.1f}" cy="{sy:.1f}" rx="3" ry="3.4" fill="{glow_col}"/><ellipse cx="{sx + ex:.1f}" cy="{sy:.1f}" rx="1.4" ry="1.8" fill="#FFF8D0"/>')
    out.append(K.path(sp([(sx - 1.5, sy + 4), (sx, sy + 7, 1), (sx + 1.5, sy + 4)]), "#1A1008"))
    return "".join(out)


@plate("baba-yagas-hut")
def baba_yagas_hut_p():
    P = Plate("myp-by")
    rnd = random.Random(8)
    mx, my = 498, 200
    L = (0.6, -0.8)
    art = [K.sky_grad(P, [(0, "#0A0A1A"), (0.45, "#1E1E3A"), (0.75, "#3A3050"), (1, "#141420")])]
    art.append(K.stars(3, (0, 0, 600, 300), 60))
    art.append(moon_disc(P, mx, my, 40, 4, glow_col="#C8C0E8"))
    # rows of spruces and birches, far to near, in mist
    for row, (yb, col, hmin, hmax, op) in enumerate(((380, "#2A2A44", 120, 200, 0.9), (420, "#1A1A2E", 150, 240, 0.95), (460, "#0E0E1A", 180, 280, 1.0))):
        for k in range(16):
            x = rnd.uniform(-20, 620)
            if row == 2 and 160 < x < 440:
                continue
            h = rnd.uniform(hmin, hmax)
            tree = [(x - h * 0.16, yb), (x, yb - h, 1), (x + h * 0.16, yb)]
            pts = []
            for j in range(9):
                t = j / 8
                yy = yb - h * t
                ww = h * 0.18 * (1 - t) + 2
                pts.append((x - ww * (1.2 if j % 2 else 0.8), yy))
            pts += [(x, yb - h - 4, 1)] + [(x + (x - px), py) for px, py in pts[::-1]]
            art.append(K.path(lp(pts), col, op))
        art.append(K.haze(P, yb - 140, yb + 10, "#5A5070", 0.0, 0.35 - row * 0.1))
    for x in (40, 96, 520, 566):
        art.append(K.path(lp([(x - 5, 600), (x - 4, 160), (x + 4, 160), (x + 5, 600)]), "#E8E4DC"))
        for k in range(12):
            y = rnd.uniform(170, 590)
            art.append(K.stroke_line([(x - 5, y), (x + rnd.uniform(-2, 5), y + 1)], "#1A1A1A", rnd.uniform(1.2, 2.4), 0.9, smooth=False))
    # the clearing: trampled snow-grey ground, mist
    ground = [(-20, 620), (-20, 470), (200, 462), (400, 466), (640, 460), (640, 620)]
    art.append(K.path(sp(ground), P.lin([(0, "#4A4658"), (1, "#14121C")], 0, 460, 0, 600, "userSpaceOnUse")))
    art.append(K.grass(5, -10, 610, 462, 600, ["#3A3A2A", "#5A5A3A", "#2A2A1A"], 260, (5, 12)))
    # the fence of stakes with their skulls
    for k, x in enumerate((70, 120, 470, 520)):
        art.append(skull_stake(P, x, 500, 100 + (k % 2) * 10, k))
    # the hut, turning on its hen's legs (one foot lifted)
    hx, floor = 300, 336
    art.append(K.cast_shadow(P, 300, 488, 120, 10, "#000000", 0.6))
    art.append(screen(glow(P, 300, 250, 150, "#FFB040", 0.18)))
    art.append(hen_leg(P, (266, floor + 6), (248, 404), (256, 488), 0.92, 3))
    art.append(izba_g(P, hx, floor + 10, 186, 5))
    art.append(hen_leg(P, (334, floor + 6), (360, 400), (352, 478), 0.92, 4, lift=16))
    art.append(K.vignette(P, "#05050A", 0.5, 0.6))
    art.append(K.text_scrim(P, 490, 600, "#05050A", 0.7))
    art.append(K.text_scrim(P, 40, 150, "#05050A", 0.6, up=False))
    text = [gilt(P, 300, 98, "Baba Yaga’s Hut", SERIF_IT, 56, ls=0.5, max_w=440, seed=4, deboss="#000000", dop=0.85),
            tx(300, 128, "SLAVIC · THE HUT ON HEN’S LEGS", CINZEL, 17, "#E8E0F2", ls=2.5, max_w=440),
            tx(300, 534, "“Turn your back to the woods, your face to me.”", SERIF_IT, 21, "#F2ECFF", max_w=450)]
    return P.render(art, text, seed=221, edge=2.0, bristle=0.45, grain=0.2)


# ================================================================ quetzalcoatl — the feathered serpent over Teotihuacan at dawn (plate)
def feathered_body(P, spine, w0, seed, L=(-0.6, -0.8)):
    """The serpent's body clothed in feathers: overlapping rows of quetzal-green feather scales shading to turquoise,
    a pale scaled belly, long emerald plumes springing from the back and streaming in the wind."""
    rnd = random.Random(seed)
    A = K.catmull(spine, 8)
    n = len(A)
    ws = [w0 * (0.6 + 0.4 * math.sin(math.pi * min(1, 0.1 + i / n))) * (1 - 0.75 * max(0, i / n - 0.82) / 0.18) for i in range(n)]
    out = []
    # plumes from the back (drawn first, behind the body)
    for i in range(4, n - 6, 5):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        base_ = (x + ty_ * ws[i] * 0.45, y - tx_ * ws[i] * 0.45)
        L_ = rnd.uniform(50, 80)
        ang = math.atan2(-tx_, ty_) + rnd.uniform(-0.3, 0.3)
        back_ = (-tx_, -ty_)
        p1 = (base_[0] + math.cos(ang) * L_ * 0.4 + back_[0] * L_ * 0.2, base_[1] + math.sin(ang) * L_ * 0.4 + back_[1] * L_ * 0.2)
        p2 = (base_[0] + math.cos(ang) * L_ * 0.7 + back_[0] * L_ * 0.6, base_[1] + math.sin(ang) * L_ * 0.7 + back_[1] * L_ * 0.6)
        sp_ = K.bez(base_, p1, p2, (p2[0] + back_[0] * 20, p2[1] + back_[1] * 20 + 6), 8)
        pl = K.plume(sp_, 12, (0.3, 0.8, 1.0, 0.9, 0.7, 0.4, 0.1))
        out.append(form(P, sp(pl), ("#9AF0B8", "#1EA868", "#063A2A"), L, K.bbox(pl), core=0.4, lit=0.5, edge="#062A1A", edge_op=0.6,
                        extra=[K.stroke_line(sp_, "#C8FFD8", 0.8, 0.6)]))
    pts = K.limb(A, [w / 2 for w in ws], [w / 2 for w in ws], n=1)
    d = sp(pts)
    sc = []
    for i in range(1, n - 1):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        for j in (-0.38, -0.05, 0.3):
            cx, cy = x - ty_ * ws[i] * j, y + tx_ * ws[i] * j
            r = ws[i] * 0.22
            col = rnd.choice(["#2AC88A", "#1E8A6A", "#5AE8C8", "#0E6A5A"])
            sc.append(f'<path d="M {cx - ty_ * r:.1f} {cy + tx_ * r:.1f} Q {cx + tx_ * r * 1.6:.1f} {cy + ty_ * r * 1.6:.1f} {cx + ty_ * r:.1f} {cy - tx_ * r:.1f} Z" '
                      f'fill="{col}" opacity="0.75" stroke="#063A2A" stroke-width="0.5"/>')
    belly = K.limb(A, [w * 0.5 for w in ws], [-w * 0.2 for w in ws], n=1)
    bel = [K.path(sp(belly), "#F2E8A0", 0.7)]
    for i in range(2, n - 2, 2):
        x, y = A[i]
        a, b = A[i - 1], A[i + 1]
        tx_, ty_ = K.unit(b[0] - a[0], b[1] - a[1])
        bel.append(K.stroke_line([(x - ty_ * ws[i] * 0.22, y + tx_ * ws[i] * 0.22), (x - ty_ * ws[i] * 0.5, y + tx_ * ws[i] * 0.5)], "#8A6A20", 1, 0.6))
    out.append(form(P, d, ("#7AE8B8", "#1E8A6A", "#052A22"), L, K.bbox(pts), core=0.5, lit=0.5, extra=sc + bel, edge="#031A12", edge_op=0.7,
                    rim_col="#FFE8B0", rim_d=2.2))
    return "".join(out), A, ws


def serpent_head_q(P, x, y, s, ang, seed, flip=False, L=(-0.6, -0.8)):
    """The head of the feathered serpent as the Teotihuacan masons carved it: wide open jaws with curved fangs and a
    forked tongue, a heavy brow over the eye, the face framed by a great collar of feathers."""
    def Q(pts):
        return place(pts, x, y, s, flip, ang)
    rnd = random.Random(seed)
    out = []
    # the feather ruff
    for k in range(14):
        a = math.radians(100 + k * 12)
        base_ = Q([(10, 0)])[0]
        tip = Q([(10 + math.cos(a) * 46, math.sin(a) * 46)])[0]
        mid = Q([(10 + math.cos(a + 0.12) * 26, math.sin(a + 0.12) * 26)])[0]
        pl = K.plume([base_, mid, tip], 14 * s, (0.4, 1, 0.9, 0.3))
        out.append(form(P, sp(pl), ("#9AF0B8", "#2AA870", "#063A2A") if k % 2 else ("#FFE08A", "#E8A030", "#6A3A08"), L, K.bbox(pl), core=0.4, lit=0.5,
                        edge="#062A1A", edge_op=0.6))
    upper = Q([(14, -14), (-6, -20), (-30, -20), (-50, -14), (-58, -6, 1), (-44, -4), (-24, -6), (0, -2), (14, 0)])
    lower = Q([(12, 4), (-8, 8), (-30, 18), (-48, 26, 1), (-34, 18), (-14, 14), (6, 12)])
    out.append(form(P, sp(lower), ("#7AE8B8", "#1E8A6A", "#052A22"), L, K.bbox(lower), core=0.5, lit=0.4, edge="#031A12", edge_op=0.8))
    out.append(K.path(sp(Q([(10, 0), (-30, 0), (-46, -2), (-40, 14), (-16, 10)])), "#8A1A20"))
    for k, (fx, fy, dy) in enumerate(((-50, -6, 10), (-26, -5, 8), (-44, 22, -8))):
        b_ = Q([(fx, fy)])[0]
        t_ = Q([(fx + 3, fy + dy)])[0]
        out.append(K.path(sp([b_, (t_[0], t_[1], 1), (b_[0] + 4 * s, b_[1])]), "#FFF8E8"))
    tq = Q([(-30, 4), (-56, 6), (-72, 0), (-66, 6), (-74, 12)])
    out.append(K.stroke_line(tq, "#D8302A", 2 * s, 0.95))
    out.append(form(P, sp(upper), ("#8AF0C0", "#1E8A6A", "#052A22"), L, K.bbox(upper), core=0.5, lit=0.5, edge="#031A12", edge_op=0.8,
                    extra=[K.scallops(seed, K.bbox(upper), 30, 180, ["#063A2A", "#9AF0C8"], (2 * s, 3.6 * s), (0.5, 0.8), (0.6, 1.0), inside=K.inside_poly(upper))]))
    brow = Q([(-6, -20), (-26, -24), (-34, -16), (-14, -14)])
    out.append(K.path(sp(brow), "#E8A030"))
    ex, ey = Q([(-18, -12)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.2 * s:.1f}" fill="#F2D040" stroke="#031A12" stroke-width="1"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{1.2 * s:.1f}" ry="{3.4 * s:.1f}" fill="#000"/>')
    return "".join(out)


def stepped_pyramid_sun(P, cx, base, w, h, seed, L=(-0.8, -0.5)):
    """The Pyramid of the Sun: five talus tiers, the great western stair, lit by the low sun from the left."""
    out = []
    tiers = 5
    for k in range(tiers):
        t0, t1 = k / tiers, (k + 1) / tiers
        w0, w1 = w * (1 - t0 * 0.72), w * (1 - t1 * 0.72)
        y0, y1 = base - h * t0, base - h * t1
        face = [(cx - w0 / 2, y0), (cx - w1 / 2, y1 + h * 0.03), (cx + w1 / 2, y1 + h * 0.03), (cx + w0 / 2, y0)]
        out.append(form(P, lp(face), ("#F2C890", "#A87A50", "#3A2414"), L, K.bbox(face), core=0.4, lit=0.5, edge="#2A1408", edge_op=0.5, grad=True))
        ledge = [(cx - w1 / 2 - 4, y1 + h * 0.03), (cx + w1 / 2 + 4, y1 + h * 0.03), (cx + w1 / 2, y1), (cx - w1 / 2, y1)]
        out.append(K.path(lp(ledge), "#FFE0B0", 0.85))
    stair = [(cx - w * 0.08, base), (cx - w * 0.04, base - h), (cx + w * 0.04, base - h), (cx + w * 0.08, base)]
    out.append(K.path(lp(stair), "#C89A6A"))
    for k in range(24):
        y = base - h * k / 24
        out.append(K.stroke_line([(cx - w * (0.08 - 0.04 * k / 24), y), (cx + w * (0.08 - 0.04 * k / 24), y)], "#6A4A2A", 0.8, 0.6, smooth=False))
    temple = [(cx - w * 0.07, base - h), (cx - w * 0.07, base - h - 14), (cx + w * 0.07, base - h - 14), (cx + w * 0.07, base - h)]
    out.append(K.path(lp(temple), "#D8A070"))
    return "".join(out)


@plate("quetzalcoatl")
def quetzalcoatl_p():
    P = Plate("myp-qz")
    rnd = random.Random(5)
    sx, sy = 90, 330
    L = (-0.85, -0.5)
    art = [K.sky_grad(P, [(0, "#0E1E3A"), (0.35, "#2A4A6A"), (0.6, "#C88A6A"), (0.72, "#FFC88A"), (0.8, "#FFE8B0")], 0, 400)]
    art.append(K.sky_wash(P, 3, ["#4A6A8A", "#E8A080", "#2A3A5A"], 12, (-40, -40, 640, 360), (80, 160), (0.12, 0.25), 30))
    art.append(screen(glow(P, sx, sy, 300, "#FFD890", 0.6)))
    art.append(K.twinkle(70, 120, 9, "#FFFFFF", 0.95))
    art.append(screen(glow(P, 70, 120, 26, "#FFFFFF", 0.6)))
    art.append(K.strata(P, 4, 250, -40, 640, 10, ("#FFE0C0", "#B07A80", "#4A4A70"), L=(-1, 0.3), n=6, op=0.8))
    # Cerro Gordo and the valley
    mtn = K.ridge(5, -20, 640, 400, 330, 30, 14, 0.4, peaks=[(470, 300, 160)])
    art.append(form(P, sp(mtn), ("#8A7A8A", "#4A4A62", "#1E2238"), L, K.bbox(mtn), core=0.3, lit=0.3, sd=10))
    art.append(K.haze(P, 300, 420, "#F2C8A0", 0.0, 0.55))
    # the Pyramid of the Moon far up the avenue, the Pyramid of the Sun nearer
    art.append(stepped_pyramid_sun(P, 470, 410, 120, 50, 3))
    art.append(K.haze(P, 360, 420, "#F2C8A0", 0.2, 0.3))
    ground = [(-20, 620), (-20, 420), (640, 416), (640, 620)]
    art.append(K.path(lp(ground), P.lin([(0, "#C89A6A"), (0.4, "#7A5A3A"), (1, "#2A1A10")], 0, 416, 0, 600, "userSpaceOnUse")))
    art.append(K.grass(5, -10, 610, 420, 600, ["#7A6A3A", "#A88A50", "#4A3A20"], 260, (4, 12)))
    art.append(stepped_pyramid_sun(P, 250, 468, 300, 110, 4))
    # the feathered serpent arcing over the city
    spine = [(560, 480), (586, 396), (540, 320), (440, 270), (330, 252), (230, 262), (166, 236), (156, 198)]
    body, A, ws = feathered_body(P, spine[::-1], 54, 7, L)
    art.append(body)
    hx, hy = 158, 202
    art.append(serpent_head_q(P, hx, hy, 1.45, -40, 9))
    art.append(K.vignette(P, "#0A0610", 0.45, 0.6))
    art.append(K.text_scrim(P, 480, 600, "#0A0610", 0.7))
    text = [gilt(P, 300, 98, "Quetzalcoatl", SERIF_IT, 60, ls=0.5, max_w=430, seed=5, deboss="#000000", dop=0.85),
            tx(300, 128, "AZTEC · THE FEATHERED SERPENT", CINZEL, 17, "#FFF2E4", ls=2.5, max_w=440),
            tx(300, 534, "He brought maize, books and the calendar", SERIF_IT, 24, "#FFF4E4", max_w=440)]
    return P.render(art, text, seed=231, edge=2.0, bristle=0.45, grain=0.2)


# ================================================================ poseidon — the horses of the sea (plate, after Walter Crane's 'Neptune's Horses')
def foam(P, seed, pts, op=1.0, scale=10, flow=-12):
    """Breaking foam: a torn white mass laced with streaks that run back with the wave, a cool blue-green shadow
    underneath, spray flicked off its leading edge."""
    rnd = random.Random(seed)
    d = sp(pts)
    x0, y0, x1, y1 = K.bbox(pts)
    streaks = K.brush(seed, (x0, y0, x1, y1), int((x1 - x0) * (y1 - y0) / 90), flow, ["#FFFFFF", "#C8E0E4", "#7AA0A8", "#FFFFFF"], (14, 40), (1.2, 3.4), (0.35, 0.8),
                      jit=10, bend=0.15, inside=K.inside_poly(pts))
    body = form(P, d, ("#FFFFFF", "#CFE2E6", "#4A7A84"), (-0.5, -0.9), (x0, y0, x1, y1), core=0.55, lit=0.5, extra=[streaks])
    out = [f'<g {P.rough(scale, 0.07, seed)}>' + body + "</g>"]
    spray = "".join(f'<circle cx="{rnd.uniform(x0 - 10, x1):.1f}" cy="{rnd.uniform(y0 - 24, y0 + 16):.1f}" r="{rnd.uniform(0.6, 2.2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>'
                    for _ in range(int((x1 - x0) / 3)))
    out.append(spray)
    out.append(f'<g {P.blur(2.5)}>' + "".join(K.bstroke(rnd.uniform(x0, x1), rnd.uniform(y0 - 10, y0 + 10), rnd.uniform(-170, -150), rnd.uniform(20, 50), 2, "#FFFFFF", 0.35)
                                                for _ in range(10)) + "</g>")
    return f'<g opacity="{op}">{"".join(out)}</g>'


@plate("poseidon")
def poseidon_p():
    P = Plate("myp-po")
    rnd = random.Random(6)
    L = (-0.5, -0.9)
    art = [K.sky_grad(P, [(0, "#1E2E3A"), (0.4, "#4A6A72"), (0.7, "#A8B8AA"), (1, "#DCE0C8")], 0, 360)]
    art.append(K.sky_wash(P, 3, ["#6A8A8A", "#2A3A48", "#C8D0B8"], 14, (-40, -40, 640, 340), (90, 180), (0.15, 0.3), 30))
    art.append(K.rays(P, 160, -40, [60 + i * 8 for i in range(6)], 520, [40, 22, 30], "#FFF8D8", 0.25, 8))
    art.append(K.strata(P, 4, 130, -40, 640, 26, ("#E8ECE0", "#5A7078", "#1E2A34"), L=(-0.4, -1), n=8, op=0.9, sd=3, rough_=(18, 0.02)))
    # the open sea: long dark swells running to the horizon
    art.append(K.water(P, 5, 330, 600, [(0, "#8AA8A0"), (0.2, "#2A5A62"), (0.6, "#123A44"), (1, "#06202A")], ["#C8E0D8", "#0A2A34", "#4A7A80"], n=180))
    # the great wave rising from the right, its face translucent green, curling over to the left
    face = [(640, 600), (640, 200), (600, 180), (540, 196), (480, 236), (420, 290), (360, 330), (300, 360), (220, 390), (120, 410), (-20, 420), (-20, 600)]
    art.append(form(P, sp(face), ("#8AE0C8", "#1E7A78", "#062A34"), (-0.3, -1), K.bbox(face), core=0.5, lit=0.5,
                    extra=[K.brush(7, (0, 180, 640, 600), 220, lambda x, y: -20 + (x - 300) * 0.05, ["#4AB8A8", "#0A3A44", "#9AF0D8"], (20, 60), (2, 5), (0.15, 0.4)),
                           soft(P, sp([(640, 200), (560, 210), (480, 260), (560, 330), (640, 320)]), "#B8FFE8", 0.45, 20)]))
    # the horses bursting from the crest, galloping left; the foam of the crest covers their hindquarters
    horses = ((402, 300, 0.62, 3), (300, 348, 0.78, 5), (176, 392, 0.9, 7))
    for k, (hx, hy, hs, sd_) in enumerate(horses):
        art.append(horse_g(P, hx, hy, hs, sd_, pal=("#FFFFFF", "#D0DCE0", "#4A5A68"), mane=("#FFFFFF", "#E8F2F4", "#A8C0C8"), L=L,
                           rim_col="#FFFFFF", tail=False))
        # spray manes flying back from the crest of each neck
        for j in range(16):
            t = j / 15
            root = place([K.lerp2((-84, -106), (-8, -52), t)], hx, hy, hs)[0]
            tip = (root[0] + rnd.uniform(40, 90) * hs, root[1] - rnd.uniform(0, 30) * hs)
            art.append(K.taper([root, ((root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2 - 8), tip], 6 * hs, 0.6, "#FFFFFF", 0.7))
        art.append(foam(P, 20 + k, [(hx - 10 * hs, hy + 30 * hs), (hx + 30 * hs, hy - 10 * hs), (hx + 90 * hs, hy - 40 * hs), (hx + 170 * hs, hy - 30 * hs),
                                    (hx + 220 * hs, hy + 10 * hs), (hx + 200 * hs, hy + 80 * hs), (hx + 20 * hs, hy + 90 * hs)], scale=14))
    # the curling lip of the wave above the last horse, the trident thrust from the sea at the right
    art.append(foam(P, 31, [(470, 250), (520, 200), (580, 176), (640, 170), (640, 240), (560, 250)], scale=16))
    tx_, ty_ = 520, 150
    art.append(screen(glow(P, tx_, ty_ + 30, 70, "#FFE8A0", 0.5)))
    art.append(K.stroke_line([(tx_, ty_ + 120), (tx_, ty_ - 6)], "#8A6A20", 5, 1, smooth=False))
    art.append(K.stroke_line([(tx_ - 1.5, ty_ + 120), (tx_ - 1.5, ty_ - 6)], "#FFE8A0", 1.4, 0.8, smooth=False))
    for sg in (-1, 0, 1):
        prong = [(tx_ + sg * 16, ty_ + 4), (tx_ + sg * 16, ty_ - 30), (tx_ + sg * 16 + 4 * (sg or 1), ty_ - 22)]
        if sg:
            art.append(K.stroke_line([(tx_, ty_ + 6), (tx_ + sg * 16, ty_ + 4)], "#C89A30", 5, 1))
        art.append(K.stroke_line(prong[:2], "#C89A30", 4.4, 1, smooth=False))
        art.append(K.path(lp([(tx_ + sg * 16 - 5, ty_ - 28), (tx_ + sg * 16, ty_ - 44), (tx_ + sg * 16 + 5, ty_ - 28)]), "#E8C060"))
    art.append(foam(P, 32, [(-20, 470), (100, 440), (240, 446), (400, 430), (560, 440), (640, 430), (640, 520), (-20, 520)], op=0.85, scale=18))
    art.append(K.vignette(P, "#02141A", 0.45, 0.6))
    art.append(K.text_scrim(P, 490, 600, "#02141A", 0.7))
    text = [gilt(P, 300, 96, "POSEIDON", CINZEL, 58, ls=12, max_w=420, seed=7, deboss="#000000", dop=0.8),
            tx(300, 532, "GREEK · LORD OF THE SEA", CINZEL, 18, "#F2FFF8", ls=3, max_w=440)]
    return P.render(art, text, seed=241, edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ gilgamesh — Gilgamesh and Enkidu at the edge of the Cedar Forest (plate)
def cedar_lebanon(P, x, base, h, seed, L=(0.6, -0.8), haze=0.0, haze_col="#E8D8B0", pal=("#8AA878", "#2E4A34", "#0A1610"), trunk_pal=("#A8907A", "#4A3A2E", "#120C08")):
    """A cedar of Lebanon: a massive trunk dividing into great limbs, the foliage held in broad flat tiers like
    shelves, each lit along its top and dark beneath, the crown spreading wider than tall in old age."""
    rnd = random.Random(seed)
    out = []
    tw = h * 0.07
    trunk = [(x - tw, base), (x - tw * 0.8, base - h * 0.3), (x - tw * 0.6, base - h * 0.62), (x - tw * 0.3, base - h * 0.9), (x + tw * 0.3, base - h * 0.9),
             (x + tw * 0.6, base - h * 0.62), (x + tw * 0.8, base - h * 0.3), (x + tw, base)]
    limbs = []
    tiers = []
    for k in range(6):
        t = 0.32 + k * 0.12
        y = base - h * t
        span = h * (0.62 - k * 0.07) * rnd.uniform(0.85, 1.1)
        for sg in (-1, 1):
            if rnd.random() < 0.15:
                continue
            ex = x + sg * span * rnd.uniform(0.6, 1.0)
            ey = y - h * rnd.uniform(0.02, 0.06)
            limbs.append(K.taper([(x, y + h * 0.02), (x + sg * span * 0.3, y - h * 0.01), (ex, ey)], tw * 0.5, tw * 0.15, trunk_pal[1]))
            tiers.append((ex - sg * span * 0.25, ey - h * 0.015, span * 0.55, h * 0.045))
    tiers.append((x, base - h * 0.96, h * 0.16, h * 0.04))
    out.append(form(P, sp(trunk), trunk_pal, L, K.bbox(trunk), core=0.6, lit=0.4, edge="#000000", edge_op=0.5,
                    extra=[K.brush(seed, K.bbox(trunk), 60, 90, [trunk_pal[0], trunk_pal[2]], (10, 30), (1.5, 3), (0.3, 0.6))]))
    out.extend(limbs)
    for k, (cx, cy, rx, ry) in enumerate(sorted(tiers, key=lambda t: t[1])):
        plate_ = K.wobble(ellipse(cx, cy, rx, ry, 18), seed * 7 + k, ry * 0.4)
        flat = [(px, py if py < cy else cy + (py - cy) * 0.5) for px, py in plate_]
        out.append(f'<g {P.rough(6, 0.07, seed + k)}>' + form(P, sp(flat), pal, L, K.bbox(flat), core=0.6, lit=0.6, edge="#000000", edge_op=0.35, sd=ry * 0.8,
                                                            extra=[K.brush(seed + k, K.bbox(flat), int(rx / 5), 0, [pal[0], pal[2], pal[1]], (4, 10), (1, 2), (0.3, 0.7),
                                                                           inside=K.inside_poly(flat))]) + "</g>")
    res = "".join(out)
    if haze:
        allpts = trunk + [(cx + rx, cy) for cx, cy, rx, ry in tiers] + [(cx - rx, cy) for cx, cy, rx, ry in tiers]
        x0, y0, x1, y1 = K.bbox(allpts)
        res = f'<g>{res}<rect x="{x0 - 40:.1f}" y="{y0 - 30:.1f}" width="{x1 - x0 + 80:.1f}" height="{y1 - y0 + 40:.1f}" fill="{haze_col}" opacity="0"/></g>'
        res = f'<g opacity="{1 - haze * 0.6:.2f}">{res}</g>'
    return res


def walker_back_g(P, x, base, s, seed, L, rim_col, rim_src=None, axe=True, hair="long", flip=False, kilt=("#C8A060", "#6A4A22", "#1A1006")):
    """A man seen from behind walking away into the forest: weight on the forward foot, the back heel lifting, a
    tufted kilt and bare back, a long axe on the shoulder. 8 heads tall (head = 24 units); (x, base) = feet."""
    def Q(pts):
        return place(pts, x, base, s, flip)
    skin = ("#C8906A", "#4A2A1A", "#0E0604")
    B = K.Body(P, L)
    B.add(Q(K.limb([(6, -92), (8, -60), (10, -30), (12, -4)], [9, 7.5, 5.5, 4], [9, 8, 6, 4])), skin, core=0.6, lit=0.3)          # far leg
    B.add(Q(K.limb([(-6, -92), (-8, -62), (-4, -34), (-2, -10)], [9, 7.5, 6.5, 4], [9, 8, 5.5, 4])), skin, core=0.5, lit=0.35)   # near leg, heel up
    B.add(Q([(-4, -12), (2, -12), (4, -2, 1), (-6, -2, 1)]), skin, core=0.4, lit=0.3)
    B.add(Q([(-17, -100), (17, -100), (19, -84), (22, -70, 1), (-22, -70, 1), (-19, -84)]), kilt, core=0.45, lit=0.4,
          extra=[K.stroke_line(Q([(-18 + k * 6, -82), (-20 + k * 7, -71)]), kilt[2], 1, 0.5) for k in range(7)])
    torso = Q([(-16, -100), (-18, -124), (-24, -146), (-26, -156), (-12, -162), (12, -162), (26, -156), (24, -146), (18, -124), (16, -100)])
    B.add(torso, skin, core=0.5, lit=0.4, extra=[K.stroke_line(Q([(0, -158), (0, -108)]), skin[2], 1.4, 0.45)])
    B.add(Q(K.limb([(22, -154), (26, -132), (28, -112), (26, -96)], [6, 5, 4.5, 4], [6, 5, 4.5, 4])), skin, core=0.5, lit=0.4)    # right arm hanging
    B.add(Q(K.limb([(-22, -154), (-30, -170), (-22, -184)], [6, 5, 4.5], [6, 5, 4.5])), skin, core=0.5, lit=0.4)                   # left arm up to the axe
    B.add(Q([(-6, -162), (6, -162), (5, -170), (-5, -170)]), skin, core=0.5, lit=0.4)
    B.add(Q(ellipse(0, -180, 9, 11, 14)), ("#2A1A10", "#140C06", "#040201"), core=0.3, lit=0.3)                               # head (hair)
    if hair == "long":
        B.add(Q([(-8, -186), (8, -186), (12, -164), (6, -154), (-6, -154), (-12, -164)]), ("#2A1A10", "#140C06", "#040201"), core=0.3, lit=0.3)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=1.6, op=0.9, src=rim_src)], edge_op=0.6)]
    if axe:
        a_, b_ = Q([(-36, -150)])[0], Q([(-6, -214)])[0]
        out.append(K.stroke_line([a_, b_], "#3A2414", 3.2 * s, 1, smooth=False))
        head = Q([(-12, -214), (6, -220), (12, -206), (0, -202)])
        out.append(K.path(sp(head), "#C8C0B0"))
    return "".join(out)


@plate("gilgamesh")
def gilgamesh_p():
    P = Plate("myp-gi")
    rnd = random.Random(4)
    L = (0.5, -0.85)
    # the Cedar Mountain: a gold-green gloom, shafts of morning light through the canopy
    art = [K.sky_grad(P, [(0, "#3A4A3A"), (0.4, "#8A8A60"), (0.7, "#D8C890"), (1, "#E8D8A8")])]
    art.append(screen(glow(P, 330, 200, 260, "#FFF2C8", 0.6)))
    # far cedars, pale in the mist, then middle ones, then the giants framing the scene
    for k in range(7):
        x = 40 + k * 90 + rnd.uniform(-20, 20)
        art.append(f'<g opacity="0.35">{cedar_lebanon(P, x, 420, rnd.uniform(160, 220), 40 + k, L, pal=("#C8C8A0", "#8A9070", "#5A6450"), trunk_pal=("#B8A890", "#8A8070", "#5A5448"))}</g>')
    art.append(K.haze(P, 160, 440, "#E8E0B8", 0.2, 0.5))
    for k, x in enumerate((90, 520)):
        art.append(f'<g opacity="0.7">{cedar_lebanon(P, x, 460, 300, 60 + k, L, pal=("#9AAA80", "#4A5A40", "#1E2A1A"), trunk_pal=("#A89880", "#5A4A3A", "#2A2018"))}</g>')
    art.append(K.rays(P, 330, 60, [70 + i * 9 for i in range(7)], 520, [40, 24, 30], "#FFF6D0", 0.35, 8))
    art.append(K.haze(P, 300, 470, "#F2E8C0", 0.0, 0.35))
    # the forest floor: needles, ferns, a path running in
    ground = [(-20, 620), (-20, 450), (200, 440), (400, 446), (640, 436), (640, 620)]
    art.append(K.path(sp(ground), P.lin([(0, "#8A7A50"), (0.4, "#4A3E26"), (1, "#14100A")], 0, 440, 0, 600, "userSpaceOnUse")))
    art.append(K.path(sp([(250, 620), (290, 470), (320, 446), (350, 446), (380, 470), (440, 620)]), "#C8B080", 0.45))
    art.append(K.grass(5, -10, 610, 446, 600, ["#5A5A30", "#8A8040", "#2A2814", "#A89A60"], 300, (6, 18)))
    # the two giants framing the view, nearest and darkest
    art.append(cedar_lebanon(P, -30, 620, 520, 81, L, pal=("#6A8A5A", "#1E3220", "#060C06"), trunk_pal=("#8A7A6A", "#2E241C", "#0A0806")))
    art.append(cedar_lebanon(P, 640, 620, 500, 82, L, pal=("#6A8A5A", "#1E3220", "#060C06"), trunk_pal=("#8A7A6A", "#2E241C", "#0A0806")))
    # Gilgamesh and Enkidu walking in, small against the great trees
    art.append(K.cast_shadow(P, 296, 474, 40, 4, "#000000", 0.45))
    art.append(walker_back_g(P, 286, 472, 0.56, 3, L, "#FFF0C0", (330, 200, 400)))
    art.append(walker_back_g(P, 326, 468, 0.6, 4, L, "#FFF0C0", (330, 200, 400), hair="long", flip=True))
    art.append(K.vignette(P, "#0A0804", 0.5, 0.55))
    art.append(K.text_scrim(P, 480, 600, "#0A0804", 0.7))
    text = [gilt(P, 300, 98, "GILGAMESH", CINZEL, 54, ls=8, max_w=430, seed=3, deboss="#000000", dop=0.85),
            tx(300, 128, "MESOPOTAMIAN · INTO THE CEDARS", CINZEL, 17, "#2A2010", ls=2.4, max_w=440),
            tx(300, 534, "The oldest story ever written", SERIF_IT, 28, "#FFF4E0", max_w=440)]
    return P.render(art, text, seed=251, edge=2.0, bristle=0.45, grain=0.2)


# ================================================================ maui's fishhook — hauling the great fish-island out of the sea (plate)
def hauler(P, x, y, s, seed, L, rim_col, rim_src, flip=False, ang=-16):
    """Maui standing braced in the stern, leaning back with all his weight against the line, arms straight, the front
    knee bent and the back leg driving; hair tied up in a topknot. Faces right; (x, y) = feet; ~190 * s tall."""
    def Q(pts):
        return place(pts, x, y, s, flip, ang)
    skin = ("#C88A60", "#3A2014", "#0A0402")
    B = K.Body(P, L)
    B.add(Q(K.limb([(-8, -92), (-24, -50), (-36, -6)], [10, 8, 5], [11, 9, 5])), skin, core=0.6, lit=0.3)                       # back leg, straight, driving
    B.add(Q([(-42, -8), (-30, -8), (-26, 0, 1), (-46, 0, 1)]), skin, core=0.5, lit=0.3)
    B.add(Q(K.limb([(14, -150), (32, -136), (52, -122), (68, -112)], [7, 6, 5, 4], [7, 6, 5, 4])), skin, core=0.5, lit=0.4)    # far arm
    B.add(Q([(-14, -100), (12, -100), (16, -84), (20, -72, 1), (-18, -72, 1), (-16, -84)]), ("#E8D8B0", "#8A6A40", "#2A1A08"), core=0.4, lit=0.4,
          extra=[K.stroke_line(Q([(-12 + k * 5, -96), (-14 + k * 6, -74)]), "#2A1A08", 0.8, 0.5) for k in range(7)])          # flax kilt
    torso = Q([(-12, -100), (-14, -124), (-12, -148), (-4, -162), (12, -164), (22, -150), (16, -124), (14, -100)])
    B.add(torso, skin, core=0.5, lit=0.4)
    B.add(Q(K.limb([(4, -98), (24, -62), (12, -34), (16, -6)], [11, 8, 6, 5], [11, 9, 7, 5])), skin, core=0.4, lit=0.4)        # front leg, bent
    B.add(Q([(12, -8), (26, -6), (30, 0, 1), (10, 0, 1)]), skin, core=0.4, lit=0.3)
    B.add(Q(ellipse(0, -176, 9.5, 11, 14)), skin, core=0.4, lit=0.45)
    B.add(Q([(-8, -182), (0, -190), (8, -186), (4, -196), (-4, -200), (-12, -192)]), ("#2A1A10", "#100804", "#000000"), core=0.3, lit=0.3)   # hair, topknot
    B.add(Q(K.limb([(10, -152), (30, -138), (50, -124), (66, -114)], [7, 6, 5, 4], [7, 6, 5, 4])), skin, core=0.4, lit=0.45)   # near arm
    return B.render(rims=[dict(L=L, col=rim_col, d=2.0, op=0.95, src=rim_src)], edge_op=0.6)


def paddler_g(P, x, y, s, seed, L, rim_col, rim_src, phase=0.0):
    """A brother kneeling in the canoe, leaning into the stroke: back bent forward, head up, both hands on the
    paddle shaft, the blade driving through the water (only the upper body shows above the hull)."""
    def Q(pts):
        return place(pts, x, y, s, False, 22 + phase * 8)
    skin = ("#B8805A", "#34200F", "#080402")
    B = K.Body(P, L)
    torso = Q([(-12, 0), (-14, -20), (-10, -38), (0, -46), (10, -42), (12, -24), (10, 0)])
    B.add(torso, skin, core=0.5, lit=0.4)
    B.add(Q(ellipse(6, -56, 7, 8, 12)), skin, core=0.4, lit=0.45)
    B.add(Q([(0, -62), (10, -66), (12, -58), (4, -64)]), ("#2A1A10", "#100804", "#000000"), core=0.3, lit=0.3)
    hand_hi = (22, -40)
    hand_lo = (30, -10)
    B.add(Q(K.limb([(-4, -40), (10, -42), hand_hi], [4.5, 4, 3.4], [4.5, 4, 3.4])), skin, core=0.4, lit=0.4)
    B.add(Q(K.limb([(6, -38), (20, -22), hand_lo], [4.5, 4, 3.4], [4.5, 4, 3.4])), skin, core=0.4, lit=0.4)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=1.6, op=0.9, src=rim_src)], edge_op=0.6)]
    a_, b_ = Q([(hand_hi[0] - 6, hand_hi[1] - 12)])[0], Q([(hand_lo[0] + 10, hand_lo[1] + 44)])[0]
    out.append(K.stroke_line([a_, b_], "#2A1408", 2.4 * s, 1, smooth=False))
    blade = Q([(hand_lo[0] + 6, hand_lo[1] + 30), (hand_lo[0] + 16, hand_lo[1] + 32), (hand_lo[0] + 14, hand_lo[1] + 54, 1), (hand_lo[0] + 6, hand_lo[1] + 48)])
    out.append(K.path(sp(blade), "#2A1408"))
    return "".join(out)


def waka_hull(P, x0, x1, wl, seed, L, rim_col, rim_src):
    """A Maori waka: a long hull with a tall carved sternpost (taurapa) and a carved prow (tauihu), red ochre with
    black and white scroll carving along the top strake."""
    rnd = random.Random(seed)
    out = []
    hull = [(x0, wl - 30), (x0 + 30, wl - 18), (x1 - 40, wl - 18), (x1, wl - 24), (x1 - 10, wl + 4), (x1 - 50, wl + 10), (x0 + 40, wl + 10), (x0 + 6, wl - 2)]
    scroll = []
    for k in range(int((x1 - x0) / 22)):
        cx = x0 + 40 + k * 22
        scroll.append(K.stroke_line([(cx + 6 * math.cos(a) * (1 - a / 12), wl - 12 + 4 * math.sin(a) * (1 - a / 12)) for a in [i * 0.6 for i in range(14)]], "#F2E8D0", 1.0, 0.7))
    out.append(form(P, sp(hull), ("#E8805A", "#8A2A18", "#2A0804"), L, K.bbox(hull), core=0.5, lit=0.45, extra=scroll + [K.stroke_line([(x0 + 20, wl - 8), (x1 - 30, wl - 8)], "#140604", 2, 0.8)],
                    edge="#000000", edge_op=0.6, rim_col=rim_col, rim_d=2, rim_src=rim_src))
    # taurapa (stern post), tall, pierced spirals
    post = [(x0 - 4, wl - 26), (x0 - 18, wl - 70), (x0 - 24, wl - 120), (x0 - 14, wl - 128), (x0 - 2, wl - 80), (x0 + 10, wl - 30)]
    out.append(form(P, sp(post), ("#E8805A", "#8A2A18", "#2A0804"), L, K.bbox(post), core=0.5, lit=0.45, edge="#000000", edge_op=0.6, rim_col=rim_col, rim_d=1.6, rim_src=rim_src))
    for k in range(3):
        cx, cy = x0 - 12, wl - 50 - k * 24
        out.append(K.stroke_line([(cx + 5 * math.cos(a) * (1 - a / 12), cy + 7 * math.sin(a) * (1 - a / 12)) for a in [i * 0.6 for i in range(14)]], "#F2E8D0", 1, 0.8))
    prow = [(x1 - 6, wl - 26), (x1 + 20, wl - 40), (x1 + 30, wl - 34), (x1 + 16, wl - 18), (x1 - 2, wl - 4)]
    out.append(form(P, sp(prow), ("#E8805A", "#8A2A18", "#2A0804"), L, K.bbox(prow), core=0.5, lit=0.45, edge="#000000", edge_op=0.6))
    return "".join(out)


@plate("mauis-fishhook")
def mauis_fishhook_p():
    P = Plate("myp-ma")
    rnd = random.Random(5)
    sx, sy = 120, 318
    L = (-0.9, -0.35)
    art = [K.sky_grad(P, [(0, "#0E1030"), (0.3, "#3A2A5A"), (0.55, "#C8607A"), (0.68, "#FFA870"), (0.75, "#FFE0A0")], 0, 330)]
    art.append(K.sky_wash(P, 3, ["#5A3A7A", "#E87A80", "#2A2050"], 12, (-40, -40, 640, 300), (80, 160), (0.12, 0.25), 30))
    # the hook of Maui still in the sky: the curve of Scorpius fading in the dawn
    hook_stars = [(x + 30, y + 86) for x, y in [(470, 70), (488, 82), (500, 98), (506, 118), (500, 138), (486, 150), (470, 152), (458, 142)]]
    for (x, y) in hook_stars:
        art.append(screen(glow(P, x, y, 9, "#FFFFFF", 0.7)))
        art.append(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#FFFFFF"/>')
    art.append(K.stroke_line(hook_stars, "#FFFFFF", 0.6, 0.25))
    art.append(screen(glow(P, sx, sy, 280, "#FFD08A", 0.6)))
    art.append(screen(glow(P, sx, sy + 6, 40, "#FFF8E0", 0.95)))
    art.append(K.strata(P, 4, 250, -40, 640, 10, ("#FFD8B8", "#B05A78", "#4A2A60"), L=(-1, 0.3), n=7, op=0.85))
    # the sea at dawn
    art.append(K.water(P, 6, 324, 600, [(0, "#F2A880"), (0.12, "#8A5A80"), (0.5, "#2A2A5A"), (1, "#0A0A24")], ["#FFE0B0", "#2A2A5A", "#C88090"], n=200, sun_x=sx, glint_w=34))
    # the island rising out of the sea, water pouring from its new slopes, a cloud of birds above it
    isl = [(330, 336), (370, 306), (406, 270), (436, 246), (460, 240), (492, 252), (536, 280), (580, 306), (620, 330), (640, 336)]
    art.append(crag(P, isl + [(640, 340), (330, 340)], ("#6A8A60", "#2A3A2A", "#0A100A"), 7, L=L, lit="#FFC890", src=(sx, sy, 520), faces=24, strata=12))
    for k in range(10):
        x = rnd.uniform(380, 600)
        art.append(f'<path d="M {x:.1f} {300 - (x - 470) ** 2 * 0.0008 + rnd.uniform(-10, 20):.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(30, 70):.1f}" stroke="#E8F0FF" stroke-width="{rnd.uniform(1, 2.4):.1f}" opacity="0.6" {P.blur(0.8)}/>')
    art.append(foam(P, 41, [(320, 344), (420, 326), (520, 330), (640, 330), (640, 356), (320, 356)], op=0.9, scale=10, flow=180))
    for k in range(14):
        bx, by = rnd.uniform(360, 460), rnd.uniform(200, 236)
        art.append(K.stroke_line([(bx - 4, by), (bx, by - 2), (bx + 4, by)], "#1A1424", 1.2, 0.8))
    # the waka, the brothers paddling, Maui hauling in the stern
    wl = 450
    art.append(waka_hull(P, 70, 330, wl, 3, L, "#FFD8A0", (sx, sy, 520)))
    for k, x in enumerate((150, 196, 242, 288)):
        art.append(paddler_g(P, x, wl - 18, 0.9, k, L, "#FFD8A0", (sx, sy, 520), phase=(k % 2) * 0.6))
    art.append(hauler(P, 104, wl - 18, 0.62, 5, L, "#FFD8A0", (sx, sy, 520)))
    # the line, drawn tight from his hands down into the sea toward the island
    hand = place([(66, -116)], 104, wl - 18, 0.62, False, -16)[0]
    art.append(K.stroke_line([hand, (240, 384), (360, 352)], "#F2E8D0", 1.4, 0.9))
    art.append(foam(P, 42, [(60, 458), (180, 452), (330, 454), (350, 466), (60, 470)], op=0.8, scale=8, flow=180))
    art.append(K.vignette(P, "#05051A", 0.45, 0.6))
    art.append(K.text_scrim(P, 470, 600, "#05051A", 0.7))
    text = [gilt(P, 300, 100, "MAUI’S FISHHOOK", BEBAS, 66, ls=4, max_w=440, seed=13, deboss="#000000", dop=0.8),
            tx(300, 130, "POLYNESIAN · FISHER OF ISLANDS", CINZEL, 17, "#E8E4FF", ls=2.5, max_w=440),
            tx(300, 534, "Its hook still hangs among the stars", SERIF_IT, 27, "#FFF0DC", max_w=440)]
    return P.render(art, text, seed=261, edge=2.0, bristle=0.45, grain=0.18)


# ================================================================ the sirens — Odysseus bound to the mast (plate)
def siren_g(P, x, y, s, seed, flip=False, L=(-1, -0.3), rim_col="#FFD49A", rim_src=None, wings="folded"):
    """A Siren as the Greek vase-painters showed her: the body of a great bird (folded or half-raised wings, a fanned
    tail, talons on the rock) with a woman's head and long dark hair. Faces left (flip -> right); (x, y) = the talons."""
    def Q(pts):
        return place(pts, x, y, s, flip)
    out = []
    pal = ("#C8A890", "#5A3A2E", "#140A08")
    tail = Q([(18, -14), (44, -6), (52, 4, 1), (40, 6), (30, 2), (14, -4)])
    out.append(form(P, sp(tail), pal, L, K.bbox(tail), core=0.5, lit=0.4, edge="#000000", edge_op=0.6))
    body = Q([(-16, -34), (-12, -46), (0, -50), (16, -44), (26, -30), (24, -14), (12, -4), (-4, -4), (-14, -14), (-18, -26)])
    out.append(K.furry(P, body, pal, L, seed, 30, n=60, flen=(2 * s, 5 * s), rough=None, core=0.5, lit=0.45, edge="#000000", edge_op=0.6,
                       extra=[K.scallops(seed, K.bbox(body), 30, 90, ["#E8D0B8", "#2A1A14"], (1.6 * s, 3 * s), (0.4, 0.7), (0.6, 1.0), inside=K.inside_poly(body))],
                       rim_col=rim_col, rim_d=1.6, rim_src=rim_src))
    if wings == "raised":
        wing = Q([(0, -40), (10, -70), (24, -96), (34, -104, 1), (30, -88), (40, -96, 1), (34, -80), (42, -84, 1), (34, -66), (28, -44), (16, -34)])
    else:
        wing = Q([(-6, -42), (14, -46), (34, -30), (52, -12, 1), (34, -16), (14, -18), (0, -24)])
    out.append(form(P, sp(wing), ("#B89880", "#4A2E24", "#0E0806"), L, K.bbox(wing), core=0.5, lit=0.45, edge="#000000", edge_op=0.6,
                    extra=[K.stroke_line(Q([(4, -36), (30, -24)]), "#E8D0B8", 0.8, 0.5)], rim_col=rim_col, rim_d=1.4, rim_src=rim_src))
    for tx_ in (-6, 4):
        out.append(K.taper(Q([(tx_, -6), (tx_ - 1, 0)]), 2 * s, 1.6 * s, "#2A1A10"))
        out.append(K.taper(Q([(tx_ - 1, 0), (tx_ - 5, 2)]), 1.4 * s, 0.6, "#2A1A10"))
    # the woman's head and neck: profile, long hair down the back
    hair = Q([(-14, -66), (-6, -72), (4, -70), (8, -58), (10, -40), (2, -36), (-4, -48), (-10, -54)])
    out.append(form(P, sp(hair), ("#6A4A30", "#24140A", "#060302"), L, K.bbox(hair), core=0.4, lit=0.4, edge="#000000", edge_op=0.6))
    face = Q([(-12, -46), (-14, -54), (-16, -58), (-18, -62, 0.6), (-16, -64), (-14, -68), (-8, -70), (-4, -64), (-4, -52), (-8, -44)])
    out.append(form(P, sp(face), ("#FFE0C8", "#C88A70", "#4A2A20"), L, K.bbox(face), core=0.4, lit=0.6, edge="#2A1008", edge_op=0.6, sd=1.5,
                    rim_col=rim_col, rim_d=1.2, rim_src=rim_src))
    out.append(K.path(sp(Q([(-14, -70), (-8, -74), (0, -72), (2, -66), (-6, -68)])), "#24140A"))
    out.append(f'<circle cx="{Q([(-12, -61)])[0][0]:.1f}" cy="{Q([(-12, -61)])[0][1]:.1f}" r="{0.7 * s:.1f}" fill="#1A0A04"/>')
    out.append(K.stroke_line(Q([(-17, -56), (-14, -55)]), "#8A2A20", 0.8 * s, 0.9))
    return "".join(out)


def galley_ship(P, x0, x1, wl, seed, L, rim_col, rim_src, oars=14):
    """A Homeric black ship: a long low hull with the ram at the prow and the painted eye, the stern curling up,
    oars in a row, the mast stepped amidships with the yard and furled sail."""
    rnd = random.Random(seed)
    out = []
    hull = [(x0, wl - 36), (x0 + 10, wl - 22), (x0 + 30, wl - 12), (x1 - 40, wl - 12), (x1 - 8, wl - 16), (x1 + 16, wl - 6, 1), (x1 - 6, wl + 2),
            (x1 - 30, wl + 8), (x0 + 40, wl + 8), (x0 + 14, wl)]
    stern = [(x0, wl - 36), (x0 - 12, wl - 58), (x0 - 2, wl - 72), (x0 + 8, wl - 64), (x0 + 2, wl - 52), (x0 + 12, wl - 26)]
    out.append(form(P, sp(stern), ("#6A5040", "#1E140E", "#050302"), L, K.bbox(stern), core=0.5, lit=0.4, edge="#000000", edge_op=0.6, rim_col=rim_col, rim_d=1.6, rim_src=rim_src))
    # oars (far side first)
    for k in range(oars):
        ox_ = x0 + 50 + k * (x1 - x0 - 90) / oars
        out.append(K.stroke_line([(ox_, wl - 14), (ox_ - 22, wl + 22)], "#2A1A10", 1.8, 0.9, smooth=False))
    out.append(form(P, sp(hull), ("#6A5040", "#1E140E", "#050302"), L, K.bbox(hull), core=0.5, lit=0.45, edge="#000000", edge_op=0.6, rim_col=rim_col, rim_d=2, rim_src=rim_src,
                    extra=[K.stroke_line([(x0 + 20, wl - 6), (x1 - 20, wl - 6)], "#A8402A", 2.4, 0.8)]))
    ex, ey = x1 - 20, wl - 8
    out.append(f'<ellipse cx="{ex}" cy="{ey}" rx="5" ry="3" fill="#F2E8D8"/><circle cx="{ex - 1}" cy="{ey}" r="1.6" fill="#000"/>')
    for k in range(oars):
        ox_ = x0 + 56 + k * (x1 - x0 - 90) / oars
        out.append(K.stroke_line([(ox_, wl - 8), (ox_ - 26, wl + 24)], "#3A2416", 2, 1, smooth=False))
        out.append(f'<ellipse cx="{ox_ - 26:.1f}" cy="{wl + 25:.1f}" rx="5" ry="1.6" fill="#FFFFFF" opacity="0.5"/>')
    # oarsmen's heads and shoulders, their ears stopped with wax, bent to the stroke
    for k in range(oars // 2):
        hx = x0 + 60 + k * (x1 - x0 - 100) / (oars // 2)
        out.append(K.path(sp([(hx - 6, wl - 12), (hx - 4, wl - 22), (hx + 4, wl - 24), (hx + 8, wl - 16), (hx + 6, wl - 12)]), "#1A100A"))
        out.append(f'<circle cx="{hx + 6:.1f}" cy="{wl - 26:.1f}" r="3.4" fill="#1A100A"/>')
    return "".join(out)


def bound_hero(P, x, y, s, L, rim_col, rim_src):
    """Odysseus lashed upright to the mast, straining toward the song: head turned, chest thrust forward against
    the ropes, hands bound behind. Faces left (toward the Sirens); (x, y) = feet."""
    def Q(pts):
        return place(pts, x, y, s)
    skin = ("#C88A60", "#3A2014", "#0A0402")
    B = K.Body(P, L)
    B.add(Q(K.limb([(4, -92), (6, -48), (6, -6)], [9, 7, 5], [9, 7.5, 5])), skin, core=0.6, lit=0.3)
    B.add(Q(K.limb([(-4, -92), (-8, -50), (-6, -6)], [9, 7, 5], [9, 7.5, 5])), skin, core=0.5, lit=0.4)
    B.add(Q([(-14, -100), (14, -100), (16, -82), (18, -70, 1), (-16, -70, 1), (-16, -82)]), ("#E8D8B0", "#8A6A40", "#2A1A08"), core=0.4, lit=0.4)
    torso = Q([(-14, -100), (-18, -126), (-22, -150), (-14, -162), (8, -164), (18, -150), (16, -124), (14, -100)])
    B.add(torso, skin, core=0.5, lit=0.45)
    B.add(Q(ellipse(-6, -178, 9, 11, 14)), skin, core=0.4, lit=0.5)
    B.add(Q([(-2, -188), (-12, -188), (-16, -176), (-12, -168), (-4, -164), (4, -170), (6, -182)]), ("#3A2A1A", "#140C06", "#000000"), core=0.3, lit=0.3)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=1.8, op=0.9, src=rim_src)], edge_op=0.6)]
    for yy in (-150, -126, -90, -40):
        a_, b_ = Q([(-20, yy), (20, yy + 4)])
        out.append(K.stroke_line([a_, b_], "#E8C890", 2.2 * s, 0.95, smooth=False))
    return "".join(out)


@plate("the-sirens")
def the_sirens_p():
    P = Plate("myp-sr")
    rnd = random.Random(13)
    sx, sy = 250, 344
    L = (-1, -0.3)
    src = (sx, sy, 520)
    art = [K.sky_grad(P, [(0, "#2A2050"), (0.3, "#6A3A6A"), (0.5, "#C86A6A"), (0.58, "#F2A868"), (0.62, "#FFD890")], 0, 360)]
    art.append(K.sky_wash(P, 3, ["#8A4A70", "#3A2A5A", "#F2A070"], 12, (-40, -40, 640, 340), (80, 160), (0.12, 0.25), 30))
    art.append(screen(glow(P, sx, sy, 300, "#FFD890", 0.6)))
    art.append(screen(glow(P, sx, sy + 4, 30, "#FFFDF0", 0.95)))
    art.append(K.strata(P, 3, 268, -40, 640, 12, ("#FFE6B0", "#B85A6A", "#4A2A5A"), L=(-0.6, 1), n=7, op=0.9))
    art.append(K.strata(P, 4, 196, -40, 640, 12, ("#F2A0A0", "#6A3A6A", "#2A1A44"), L=(-0.8, 1), n=6, op=0.75))
    art.append(K.water(P, 5, 352, 600, [(0, "#E8A07A"), (0.14, "#8A5A6A"), (0.5, "#3A2A4A"), (1, "#120E22")], ["#FFE0B0", "#3A2A4A", "#C88080"], n=200, sun_x=sx, glint_w=30))
    # the Sirens' rock on the right, the bones of sailors who listened bleaching on it
    rock = [(390, 600), (400, 470), (420, 410), (440, 370), (462, 330), (492, 300), (528, 280), (566, 286), (600, 300), (640, 320), (640, 600)]
    art.append(crag(P, rock, ("#9A6A6A", "#3A2228", "#0A0608"), 7, L=L, lit="#FFC890", src=(sx, sy, 520), faces=26, strata=12))
    for k in range(10):
        bx, by = rnd.uniform(420, 600), rnd.uniform(400, 470)
        art.append(K.taper([(bx, by), (bx + rnd.uniform(8, 14), by + rnd.uniform(-3, 3))], 2.6, 2.2, "#E8DCC8", 0.8))
    art.append(foam(P, 51, [(380, 476), (460, 466), (560, 470), (640, 464), (640, 494), (380, 494)], op=0.85, scale=8, flow=180))
    art.append(siren_g(P, 470, 330, 1.25, 3, L=L, rim_src=src))
    art.append(siren_g(P, 548, 284, 1.35, 4, L=L, rim_src=src, wings="raised"))
    art.append(siren_g(P, 596, 304, 1.1, 5, L=L, rim_src=src))
    # their song drifting over the water
    for i in range(3):
        pts = [(450 - i * 6, 300 + i * 16), (390, 284 + i * 20), (330, 300 + i * 14), (270, 296 + i * 18)]
        art.append(f'<path d="{sp(pts, closed=False)}" stroke="#FFF0D0" stroke-width="1.4" fill="none" opacity="0.4" stroke-dasharray="1 6" stroke-linecap="round"/>')
    # the black ship, Odysseus lashed to the mast
    wl = 450
    mx = 214
    art.append(K.stroke_line([(mx, wl - 14), (mx + 2, wl - 230)], "#140A06", 6, 1, smooth=False))
    art.append(K.stroke_line([(mx + 3, wl - 14), (mx + 5, wl - 228)], "#FFD49A", 1.4, 0.6, smooth=False))
    art.append(K.taper([(mx - 90, wl - 214), (mx, wl - 222), (mx + 90, wl - 214)], 5, 5, "#140A06"))
    sail = [(mx - 84, wl - 216), (mx, wl - 224), (mx + 84, wl - 216), (mx + 70, wl - 204), (mx, wl - 208), (mx - 70, wl - 204)]
    art.append(form(P, sp(sail), ("#F2E0C0", "#B89A7A", "#4A3A30"), L, K.bbox(sail), core=0.4, lit=0.5, edge="#000000", edge_op=0.5))
    for k in (-60, -20, 20, 60):
        art.append(K.stroke_line([(mx + k, wl - 210), (mx + k * 1.2, wl - 20)], "#140A06", 1, 0.5, smooth=False))
    art.append(bound_hero(P, mx + 2, wl - 14, 0.7, L, "#FFD49A", src))
    art.append(galley_ship(P, 70, 360, wl, 5, L, "#FFD49A", src))
    art.append(K.vignette(P, "#0A0816", 0.45, 0.6))
    art.append(K.text_scrim(P, 480, 600, "#0A0816", 0.7))
    text = [gilt(P, 300, 100, "The Sirens", DMS, 66, ls=1, max_w=420, seed=13, deboss="#000000", dop=0.8),
            tx(300, 130, "GREEK · HOMER, THE ODYSSEY", CINZEL, 17, "#F2E4F2", ls=2.5, max_w=440),
            tx(300, 534, "“Bind me fast to the mast.”", SERIF_IT, 30, "#FFF0DC", max_w=440)]
    return P.render(art, text, seed=271, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ the selkie — the seal wife returns to the sea (plate)
def selkie_woman_g(P, x, y, s, seed, L, rim_col, rim_src):
    """The selkie seen from behind on the rock at the tide's edge, looking out to her kin: a long linen shift blown
    against her by the sea wind, long dark hair streaming, the sealskin over her arm trailing to the stone.
    8 heads tall (head = 22 units); (x, y) = feet."""
    def Q(pts):
        return place(pts, x, y, s)
    rnd = random.Random(seed)
    out = []
    B = K.Body(P, L)
    dress = Q([(-18, -150), (-24, -120), (-24, -96), (-26, -60), (-30, -20), (-32, -2), (-14, 0), (4, -2), (24, 2), (40, -4, 1), (32, -12), (44, -18, 1),
               (30, -30), (26, -70), (22, -100), (22, -124), (18, -150), (0, -154)])
    B.add(dress, ("#D8DCE8", "#5A6278", "#12141E"), core=0.55, lit=0.45,
          extra=[K.stroke_line(Q([(-10, -120), (-14, -60), (-18, -6)]), "#0A0C14", 2 * s, 0.4), K.stroke_line(Q([(6, -116), (12, -60), (22, -8)]), "#0A0C14", 2 * s, 0.4),
                 K.stroke_line(Q([(-2, -100), (0, -50), (4, -4)]), "#E8ECF8", 1.4 * s, 0.3)])
    B.add(Q(K.limb([(20, -146), (26, -124), (28, -104), (30, -90)], [5, 4.4, 3.8, 3.4], [5, 4.4, 3.8, 3.4])), ("#E8D0C0", "#6A5048", "#14100E"), core=0.5, lit=0.4)
    B.add(Q(K.limb([(-18, -146), (-28, -126), (-36, -110), (-44, -100)], [5, 4.4, 3.8, 3.4], [5, 4.4, 3.8, 3.4])), ("#E8D0C0", "#6A5048", "#14100E"), core=0.5, lit=0.4)
    B.add(Q([(-6, -154), (6, -154), (5, -162), (-5, -162)]), ("#E8D0C0", "#6A5048", "#14100E"), core=0.5, lit=0.4)
    B.add(Q(ellipse(0, -172, 9, 11, 14)), ("#3A2A2A", "#120A0A", "#020101"), core=0.3, lit=0.3)
    hair = Q([(-10, -178), (0, -184), (10, -178), (14, -160), (18, -140), (26, -120), (40, -104, 1), (24, -108), (30, -96, 1), (14, -104), (4, -112), (-6, -116),
              (-14, -128), (-14, -150)])
    B.add(hair, ("#5A4038", "#1A100E", "#040202"), core=0.4, lit=0.4,
          extra=[K.stroke_line(Q([(-6 + k * 4, -176), (-2 + k * 6, -140), (8 + k * 7, -112)]), "#8A6A58", 0.8, 0.5) for k in range(4)])
    out.append(B.render(rims=[dict(L=L, col=rim_col, d=2.0, op=0.95, src=rim_src)], edge_op=0.6))
    # the sealskin over her left forearm, falling to the rock: silver-grey, dappled, the flippers hanging
    skin = Q([(-50, -104), (-38, -100), (-34, -84), (-38, -56), (-44, -30), (-40, -10), (-48, 2), (-62, 4), (-70, -4, 1), (-60, -14), (-64, -40), (-62, -70),
              (-58, -94)])
    spots = [f'<ellipse cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{rnd.uniform(1.4, 3) * s:.1f}" ry="{rnd.uniform(1, 2.2) * s:.1f}" fill="#2A3038" opacity="0.7"/>'
             for p in Q([(rnd.uniform(-60, -40), rnd.uniform(-96, -10)) for _ in range(26)])]
    out.append(K.furry(P, skin, ("#D8E0E8", "#7A8494", "#1E2430"), L, seed + 3, 95, n=50, flen=(3 * s, 7 * s), rough=(1.2 * s, 0.12), core=0.5, lit=0.5,
                       edge="#000000", edge_op=0.6, extra=spots, rim_col=rim_col, rim_d=1.6, rim_src=rim_src))
    return "".join(out)


def seal_head_g(P, x, y, s, seed, L, rim_col, rim_src, turn=1):
    """A grey seal's head above the water: rounded crown, big dark eyes, whiskered muzzle, the ripple ring around."""
    def Q(pts):
        return place(pts, x, y, s, turn < 0)
    out = [K.stroke_line(ellipse(x, y + 2 * s, 18 * s, 4 * s, 20) + [ellipse(x, y + 2 * s, 18 * s, 4 * s, 20)[0]], "#E8F0FF", 1.0, 0.45)]
    head = Q([(-12, 2), (-14, -6), (-8, -14), (2, -17), (10, -14), (16, -10), (21, -7, 0.6), (19, -4), (13, -2), (4, 2)])
    out.append(form(P, sp(head), ("#9AA8BC", "#323C4E", "#080A10"), L, K.bbox(head), core=0.55, lit=0.5, edge="#000000", edge_op=0.6, sd=3 * s,
                    rim_col=rim_col, rim_d=1.4, rim_src=rim_src))
    c = Q([(6, -11)])[0]
    out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{1.5 * s:.1f}" fill="#05070A"/><circle cx="{c[0] - 0.3 * s:.1f}" cy="{c[1] - 0.4 * s:.1f}" r="{0.45 * s:.1f}" fill="#FFF"/>')
    n_ = Q([(20, -6)])[0]
    out.append(f'<circle cx="{n_[0]:.1f}" cy="{n_[1]:.1f}" r="{1 * s:.1f}" fill="#05070A"/>')
    for k in range(3):
        a_, b_ = Q([(15, -5 + k), (26, -8 + k * 3)])
        out.append(K.stroke_line([a_, b_], "#E8F0FF", 0.5, 0.6))
    return "".join(out)


@plate("the-selkie")
def the_selkie_p():
    P = Plate("myp-se")
    rnd = random.Random(9)
    mx, my, mr = 330, 196, 62
    L = (0.2, -1)
    src = (mx, my, 520)
    art = [K.sky_grad(P, [(0, "#060A1C"), (0.45, "#14224A"), (0.8, "#2A3A66"), (1, "#3A4A72")], 0, 330)]
    art.append(K.stars(5, (0, 0, 600, 300), 120, avoid=lambda x, y: math.hypot(x - mx, y - my) < 90))
    art.append(K.strata(P, 4, 250, -40, 640, 12, ("#C8D4F2", "#3A4A78", "#141C40"), L=(0, -1), n=6, op=0.8))
    art.append(moon_disc(P, mx, my, mr, 6))
    # far headland with the croft where she kept house, its window lit
    head_ = [(-20, 330), (-20, 290), (40, 280), (100, 292), (150, 316), (180, 330)]
    art.append(K.path(sp(head_), "#0C1226"))
    art.append(K.path(lp([(70, 286), (96, 286), (96, 272), (83, 264), (70, 272)]), "#0A0E1E"))
    art.append(screen(glow(P, 84, 280, 14, "#FFC060", 0.8)))
    art.append(f'<rect x="80" y="277" width="6" height="5" fill="#FFD890"/>')
    # the sea under the moon, the seals waiting in the moon-glade
    art.append(K.water(P, 5, 326, 600, [(0, "#3A4A78"), (0.3, "#1A2448"), (1, "#060A1A")], ["#C8D8FF", "#0A1028", "#5A6A98"], n=200, sun_x=mx, glint="#E8F0FF", glint_w=40))
    for k, (x, y, sc) in enumerate(((300, 370, 1.0), (372, 382, 1.1), (444, 360, 0.85), (246, 398, 1.2))):
        art.append(seal_head_g(P, x, y, sc, k, L, "#E8F0FF", src, turn=-1 if x > 340 else 1))
    # the rocks of the shore, wet and shining
    rocks = [(-20, 620), (-20, 470), (40, 440), (110, 430), (180, 446), (230, 470), (300, 486), (360, 480), (420, 500), (520, 492), (640, 500), (640, 620)]
    art.append(crag(P, rocks, ("#7A86A8", "#222A40", "#06080E"), 5, L=L, lit="#E8F0FF", src=src, faces=24, strata=10))
    art.append(foam(P, 61, [(200, 480), (300, 474), (420, 488), (540, 480), (640, 486), (640, 500), (200, 500)], op=0.7, scale=8, flow=180))
    # the selkie
    art.append(selkie_woman_g(P, 120, 436, 1.12, 4, L, "#E8F0FF", src))
    art.append(K.vignette(P, "#02040C", 0.5, 0.6))
    art.append(K.text_scrim(P, 480, 600, "#02040C", 0.7))
    text = [gilt(P, 300, 98, "The Selkie", SERIF_IT, 66, ls=0.5, max_w=420, seed=5, pal="silver", deboss="#000000", dop=0.85),
            tx(300, 128, "SCOTTISH & IRISH · THE SEAL WIFE", CINZEL, 17, "#DCE6FF", ls=2.4, max_w=440),
            tx(300, 534, "The sea will always call her home.", SERIF_IT, 27, "#E8F0FF", max_w=440)]
    return P.render(art, text, seed=281, edge=2.0, bristle=0.45, grain=0.18)


# ================================================================ bifrost — the burning rainbow bridge to Asgard (plate)
def heimdall_g(P, x, y, s, seed, L, rim_col, rim_src):
    """Heimdall, watchman of the gods, standing at the bridgehead: a long cloak, a helmet, the great curved
    Gjallarhorn raised to his lips. Faces right, up the bridge; (x, y) = feet; ~180 * s tall."""
    def Q(pts):
        return place(pts, x, y, s)
    B = K.Body(P, L)
    cloak = Q([(-14, -150), (8, -156), (14, -120), (16, -70), (22, -20), (14, 0), (-20, 0), (-36, -6, 1), (-30, -30), (-34, -70), (-30, -110), (-22, -140)])
    B.add(cloak, ("#6A7AA0", "#1E2638", "#05070C"), core=0.5, lit=0.4, extra=[K.stroke_line(Q([(-20, -120), (-24, -60), (-26, -10)]), "#000000", 1.6 * s, 0.4)])
    B.add(Q(K.limb([(6, -92), (8, -50), (10, -4)], [7, 6, 4.5], [7, 6.5, 4.5])), ("#5A5A6A", "#1A1A22", "#050508"), core=0.5, lit=0.4)
    B.add(Q([(4, -6), (18, -4), (20, 0, 1), (4, 0, 1)]), ("#5A5A6A", "#1A1A22", "#050508"), core=0.5, lit=0.4)
    B.add(Q(ellipse(0, -166, 9, 11, 14)), ("#D8B8A0", "#5A4038", "#140C0A"), core=0.4, lit=0.5)
    B.add(Q([(-9, -168), (-8, -178), (0, -182), (9, -178), (10, -168)]), ("#E8ECF4", "#8A90A0", "#2A2E38"), core=0.4, lit=0.6)   # helmet
    B.add(Q([(-4, -160), (-10, -150), (-6, -140), (4, -142), (6, -154)]), ("#F2E8D8", "#A8988A", "#3A3028"), core=0.4, lit=0.5)   # beard
    B.add(Q(K.limb([(8, -150), (20, -150), (24, -164)], [5, 4.4, 3.6], [5, 4.4, 3.6])), ("#6A7AA0", "#1E2638", "#05070C"), core=0.4, lit=0.5)
    out = [B.render(rims=[dict(L=L, col=rim_col, d=1.8, op=0.95, src=rim_src)], edge_op=0.6)]
    horn = Q(K.plume(K.bez((6, -168), (24, -176), (46, -194), (52, -222), 8), 14, (0.25, 0.4, 0.55, 0.7, 0.85, 1.0)))
    out.append(form(P, sp(horn), ("#FFF6D8", "#D8B87A", "#5A4020"), L, K.bbox(horn), core=0.4, lit=0.6, edge="#2A1A08", edge_op=0.7))
    out.append(K.path(sp(Q(ellipse(52, -224, 7, 4, 12, rot=-70))), "#3A2A10"))
    for k in range(3):
        a_ = Q([(60 + k * 8, -230 - k * 10)])[0]
        out.append(K.stroke_line([(a_[0], a_[1]), (a_[0] + 8, a_[1] - 6), (a_[0] + 4, a_[1] - 14)], "#FFF6D8", 1.2, 0.5 - k * 0.12))
    return "".join(out)


def golden_hall(P, cx, base, w, seed, L):
    """A hall of Asgard: a long timber hall with steep golden-shingled roofs, crossed gable boards carved as dragon
    heads, a lower wing, smoke and light — Valhalla with its roof of shields."""
    rnd = random.Random(seed)
    s = w / 160
    out = [screen(glow(P, cx, base - 40 * s, 160 * s, "#FFE0A0", 0.5))]
    for k, (ox, ww, hh, rh) in enumerate(((-56, 70, 26, 34), (30, 60, 22, 28), (-10, 90, 34, 46))):
        x0, x1 = cx + ox * s - ww * s / 2, cx + ox * s + ww * s / 2
        wall = [(x0, base), (x0, base - hh * s), (x1, base - hh * s), (x1, base)]
        out.append(K.path(lp(wall), "#6A4A2A"))
        for j in range(int(ww / 10)):
            out.append(f'<rect x="{x0 + 4 * s + j * 10 * s:.1f}" y="{base - hh * s * 0.6:.1f}" width="{3 * s:.1f}" height="{5 * s:.1f}" fill="#FFE8A0"/>')
        roof = [(x0 - 6 * s, base - hh * s + 2 * s), ((x0 + x1) / 2, base - (hh + rh) * s), (x1 + 6 * s, base - hh * s + 2 * s)]
        out.append(form(P, lp(roof), ("#FFF0B0", "#D8A030", "#6A3A08"), L, K.bbox(roof), core=0.4, lit=0.6, edge="#2A1404", edge_op=0.6,
                        extra=[K.scallops(seed + k, K.bbox(roof), 40, 90, ["#8A5A10", "#FFF2C0"], (2 * s, 3.4 * s), (0.5, 0.8), (0.6, 1.0), inside=K.inside_poly(roof))]))
        top = ((x0 + x1) / 2, base - (hh + rh) * s)
        for sg in (-1, 1):
            out.append(K.stroke_line([top, (top[0] + sg * 10 * s, top[1] - 12 * s), (top[0] + sg * 16 * s, top[1] - 10 * s)], "#C88A20", 2 * s, 0.95))
    return "".join(out)


@plate("bifrost")
def bifrost_p():
    P = Plate("myp-bf")
    rnd = random.Random(4)
    L = (0.6, -0.8)
    art = [K.sky_grad(P, [(0, "#0A0E24"), (0.35, "#22305A"), (0.62, "#6A6A9A"), (0.8, "#E8B0A0"), (1, "#FFD8B0")], 0, 420)]
    art.append(K.stars(3, (0, 0, 600, 240), 90))
    for k in range(5):
        x0 = -60 + k * 50
        band = [(x0, 60 + k * 8), (x0 + 160, 40 + k * 8), (x0 + 340, 90 + k * 6), (x0 + 520, 50 + k * 8), (x0 + 700, 100)]
        pts = K.catmull(band, 8)
        rays_ = "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(60, 130):.1f}" stroke="{rnd.choice(["#4AF0A0", "#2AD8A8", "#9A7AF0"])}" '
                        f'stroke-width="{rnd.uniform(3, 8):.1f}" opacity="{rnd.uniform(0.07, 0.18):.2f}"/>' for x, y in pts[::2])
        art.append(screen(f'<g {P.blur(5)}>{rays_}</g>'))
    # Asgard on its sky-mountain, high on the right, bathed in light
    peak = [(330, 330), (380, 290), (420, 252), (460, 236), (520, 236), (560, 250), (600, 280), (640, 300), (640, 340), (330, 340)]
    art.append(form(P, sp(peak), ("#E8D8C8", "#8A7A90", "#2A2440"), L, K.bbox(peak), core=0.4, lit=0.5, sd=8, rim_col="#FFE8C0", rim_d=2))
    art.append(golden_hall(P, 500, 240, 150, 3, L))
    art.append(K.strata(P, 4, 330, 280, 660, 18, ("#FFF0E0", "#A890B0", "#4A4068"), L=(0.2, -1), n=7, op=0.95, sd=2.4))
    # Midgard below: fjord and dark mountains
    mtn = K.ridge(6, -20, 640, 450, 380, 40, 14, 0.4, peaks=[(80, 340, 140), (300, 380, 120)])
    art.append(form(P, sp(mtn), ("#6A6A8A", "#2A2C48", "#0C0E1E"), L, K.bbox(mtn), core=0.4, lit=0.35, sd=10))
    art.append(K.haze(P, 360, 470, "#E8B8A8", 0.0, 0.45))
    art.append(K.water(P, 5, 462, 600, [(0, "#C89AA0"), (0.3, "#3A3A5A"), (1, "#0A0C1A")], ["#FFE0D0", "#1A1C30", "#8A7A98"], n=140))
    # the bridge itself: a rainbow of three burning colours sweeping up from the shore to the gods
    p0, p1, p2, p3 = (110, 470), (150, 250), (320, 190), (452, 238)
    for k, (col, w_, op) in enumerate((("#E8402A", 12, 0.95), ("#F2A030", 8, 0.9), ("#F8E070", 7, 0.85), ("#5AC88A", 7, 0.8), ("#4A7AE8", 7, 0.8), ("#8A5AD8", 7, 0.75))):
        off = (k - 2.5) * 7
        pts = K.bez((p0[0] + off, p0[1]), (p1[0] + off, p1[1] + off), (p2[0], p2[1] + off), (p3[0], p3[1] + off), 30)
        art.append(screen(K.stroke_line(pts, col, w_ * 2.4, op * 0.4, extra=f' {P.blur(6)}')))
        art.append(K.stroke_line(pts, col, w_, op))
    # flames licking along the red band (the fire that keeps the giants off)
    red = K.bez((p0[0] - 18, p0[1]), (p1[0] - 18, p1[1] - 18), (p2[0], p2[1] - 18), (p3[0], p3[1] - 18), 24)
    for k, (fx, fy) in enumerate(red[2:-2:2]):
        art.append(K.flame(P, fx, fy + 2, rnd.uniform(14, 24), 30 + k, lean=0.2, n=3, w=0.35, sd=0.8))
    # the bridgehead rock and Heimdall
    rock = [(-20, 620), (-20, 470), (40, 456), (110, 452), (170, 470), (210, 500), (230, 620)]
    art.append(crag(P, rock, ("#7A7A98", "#26283C", "#08080E"), 7, L=L, lit="#FFC8A0", src=(160, 400, 300), faces=20, strata=8))
    art.append(heimdall_g(P, 92, 456, 0.62, 3, (0.8, -0.6), "#FFD8B0", (220, 330, 260)))
    art.append(K.vignette(P, "#04050E", 0.45, 0.6))
    art.append(K.text_scrim(P, 480, 600, "#04050E", 0.7))
    text = [gilt(P, 300, 504, "Bifröst", SERIF_IT, 64, ls=0.5, max_w=420, seed=5, deboss="#000000", dop=0.85),
            tx(300, 536, "NORSE · THE BRIDGE TO ASGARD", CINZEL, 17, "#F2E8FF", ls=2.5, max_w=440)]
    return P.render(art, text, seed=291, edge=2.0, bristle=0.45, grain=0.18)


# ================================================================ orpheus — the climb out of the underworld, not looking back (plate)
def orpheus_g(P, x, y, s, seed, L, rim_col, rim_src):
    """Orpheus climbing the last steps toward the daylight, seen from behind and a little to the side: a long
    chiton, a cloak over one shoulder, the lyre held against his side, his head bowed, resolutely not turning.
    8 heads tall (head = 22 units); (x, y) = the forward foot, a step higher than the back one."""
    def Q(pts):
        return place(pts, x, y, s)
    B = K.Body(P, L)
    robe = ("#8A8CA8", "#262838", "#06070C")
    B.add(Q(K.limb([(-6, -84), (-14, -46), (-20, -8), (-22, 14)], [8, 7, 5, 4], [8, 7.5, 5, 4])), ("#C89A80", "#4A3028", "#100806"), core=0.6, lit=0.3)   # back leg, lower step
    chiton = Q([(-16, -144), (16, -146), (20, -110), (22, -70), (26, -40, 1), (8, -36), (-10, -34), (-26, -38, 1), (-22, -80), (-20, -116)])
    B.add(chiton, robe, core=0.5, lit=0.45, extra=[K.stroke_line(Q([(-8, -130), (-12, -80), (-14, -40)]), "#000000", 1.4 * s, 0.4),
                                                   K.stroke_line(Q([(6, -132), (10, -80), (12, -40)]), "#000000", 1.4 * s, 0.4)])
    B.add(Q(K.limb([(6, -80), (14, -44), (16, -4)], [8, 7, 5], [8, 7.5, 5])), ("#C89A80", "#4A3028", "#100806"), core=0.5, lit=0.4)   # forward leg on the upper step
    cloak = Q([(-18, -146), (-4, -152), (10, -148), (2, -120), (-8, -80), (-24, -44), (-34, -40, 1), (-30, -80), (-26, -120)])
    B.add(cloak, ("#A84A3A", "#4A1410", "#120404"), core=0.5, lit=0.45)
    B.add(Q(K.limb([(16, -140), (24, -116), (26, -96)], [5, 4.4, 3.8], [5, 4.4, 3.8])), ("#C89A80", "#4A3028", "#100806"), core=0.4, lit=0.5)
    B.add(Q([(-5, -150), (5, -150), (5, -158), (-5, -158)]), ("#C89A80", "#4A3028", "#100806"), core=0.5, lit=0.4)
    B.add(Q(ellipse(2, -168, 8.5, 10, 14)), ("#3A2A1A", "#140C06", "#030201"), core=0.3, lit=0.3)                       # head from behind, curls
    B.add(Q([(-8, -172), (0, -180), (10, -176), (12, -164), (4, -158), (-6, -160)]), ("#5A3A20", "#24140A", "#060302"), core=0.3, lit=0.4,
          extra=[K.scallops(seed, K.bbox(Q([(-8, -180), (12, -158)])), 14, 90, ["#8A6A40", "#000000"], (1.2 * s, 2.2 * s), (0.4, 0.7), (0.5, 0.9))])
    out = [B.render(rims=[dict(L=L, col=rim_col, d=2.2, op=1.0, src=rim_src)], edge_op=0.6)]
    # the lyre at his side: tortoiseshell sound box, two curving arms, the crossbar and strings catching the light
    lx, ly = Q([(30, -100)])[0]
    box = ellipse(lx, ly + 8 * s, 9 * s, 7 * s, 14)
    out.append(form(P, sp(box), ("#C8A070", "#5A3A1A", "#140A04"), L, K.bbox(box), core=0.4, lit=0.5, sd=2))
    for sg in (-1, 1):
        out.append(K.taper([(lx + sg * 6 * s, ly + 4 * s), (lx + sg * 10 * s, ly - 10 * s), (lx + sg * 7 * s, ly - 22 * s)], 2.6 * s, 1.4 * s, "#E8C890"))
    out.append(K.stroke_line([(lx - 8 * s, ly - 20 * s), (lx + 8 * s, ly - 20 * s)], "#E8C890", 1.8 * s, 1, smooth=False))
    for k in range(5):
        xx = lx - 4 * s + k * 2 * s
        out.append(K.stroke_line([(xx, ly - 20 * s), (xx, ly + 8 * s)], "#FFF6D8", 0.6, 0.9, smooth=False))
    return "".join(out)


def eurydice_g(P, x, y, s, seed):
    """Eurydice following, still a shade: a pale veiled figure of mist, her drapery trailing back into the dark,
    one hand reaching toward him; drawn translucent, with soft lost edges."""
    def Q(pts):
        return place(pts, x, y, s)
    fig = Q([(0, -184), (10, -178), (12, -164), (8, -152), (18, -140), (22, -118), (40, -110, 0.6), (38, -104), (22, -104), (20, -80), (24, -40),
             (34, -4), (60, 10), (90, 20, 1), (40, 14), (0, 6), (-30, 10), (-60, 20, 1), (-30, 0), (-22, -40), (-18, -90), (-16, -130), (-10, -150),
             (-10, -168)])
    d = sp(fig)
    out = [f'<path d="{d}" fill="#E8F0FF" opacity="0.28" {P.blur(3)}/>',
           f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.5" {P.blur(1)}/>']
    for k in range(5):
        out.append(K.stroke_line(Q([(-10 + k * 6, -140), (-12 + k * 8, -80), (-20 + k * 16, 0)]), "#FFFFFF", 1.0, 0.25))
    out.append(screen(glow(P, *Q([(0, -100)])[0], 120 * s, "#C8D8FF", 0.3)))
    return "".join(out)


@plate("orpheus")
def orpheus_p():
    P = Plate("myp-or")
    rnd = random.Random(5)
    gx, gy = 450, 210          # the mouth of the cave and the daylight
    L = K.unit(1, -1)
    src = (gx, gy, 380)
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#0C0A12")]
    # the cave: rock walls closing in, lit only by the daylight ahead
    art.append(screen(glow(P, gx, gy, 380, "#FFE8B0", 0.45)))
    walls = [[(-20, -20), (640, -20), (640, 120), (560, 150), (520, 130), (470, 140), (400, 170), (330, 230), (260, 300), (180, 380), (100, 450), (-20, 520)],
             [(640, 620), (640, 320), (600, 300), (560, 280), (520, 300), (480, 340), (420, 390), (360, 430), (280, 480), (200, 520), (120, 560), (60, 620)]]
    for k, w in enumerate(walls):
        art.append(crag(P, w, ("#8A7A70", "#2A2228", "#08060A"), 10 + k, L=L, lit="#FFE0A0", src=src, faces=30, strata=14))
    # the opening itself: blinding white-gold daylight, the world above
    mouth = [(380, 300), (390, 240), (420, 190), (470, 166), (520, 176), (550, 220), (556, 290), (520, 300), (440, 306)]
    art.append(K.path(sp(mouth), P.rad([(0, "#FFFFFF"), (0.4, "#FFF6D8"), (0.8, "#FFD890"), (1, "#E8A860")], cx=0.55, cy=0.45, r=0.6)))
    art.append(K.rays(P, gx, gy, [120 + i * 10 for i in range(8)], 520, [40, 24, 30], "#FFF0C0", 0.35, 8))
    # the rough stair cut in the rock, climbing toward it: lit treads, dark risers, the worn edges catching the light
    stair = []
    for k in range(9):
        t = k / 8
        x0, y0 = 120 + t * 290, 528 - t * 224
        stepw = 140 - t * 70
        h = 26 - t * 12
        tread = [(x0 - stepw / 2, y0), (x0 + stepw / 2, y0 - 4), (x0 + stepw / 2 + 6, y0 + 6), (x0 - stepw / 2 - 6, y0 + 10)]
        riser = [(x0 - stepw / 2 - 6, y0 + 10), (x0 + stepw / 2 + 6, y0 + 6), (x0 + stepw / 2 + 8, y0 + 6 + h), (x0 - stepw / 2 - 8, y0 + 10 + h)]
        stair.append((riser, tread))
    for riser, tread in stair:
        art.append(form(P, lp(riser), ("#6A5A54", "#241C1C", "#060404"), L, K.bbox(riser), core=0.5, lit=0.3, edge="#000000", edge_op=0.5))
        art.append(form(P, lp(tread), ("#E8D0B0", "#7A6A5A", "#201814"), L, K.bbox(tread), core=0.4, lit=0.6, edge="#000000", edge_op=0.4,
                        rim_col="#FFE8B0", rim_d=1.6, rim_src=src))
    # asphodel, the flowers of the underworld, pale along the way
    for k in range(18):
        x, y = rnd.uniform(60, 360), rnd.uniform(420, 560)
        art.append(K.stroke_line([(x, y), (x + rnd.uniform(-3, 3), y - rnd.uniform(14, 26))], "#4A5A4A", 1.2, 0.8))
        for j in range(4):
            art.append(f'<circle cx="{x + rnd.uniform(-4, 4):.1f}" cy="{y - rnd.uniform(14, 28):.1f}" r="{rnd.uniform(1.6, 2.6):.1f}" fill="#F2ECF8" opacity="0.9"/>')
    # Eurydice, a shade, following below; Orpheus near the light, not looking back
    art.append(eurydice_g(P, 200, 470, 0.86, 3))
    art.append(orpheus_g(P, 352, 344, 0.86, 4, L, "#FFF0C8", src))
    art.append(K.vignette(P, "#030206", 0.55, 0.55, cx=0.6, cy=0.4))
    art.append(K.text_scrim(P, 470, 600, "#030206", 0.75))
    text = [gilt(P, 300, 100, "ORPHEUS", CINZEL, 60, ls=12, max_w=420, seed=5, deboss="#000000", dop=0.85),
            tx(300, 130, "GREEK · AT THE GATES OF HADES", CINZEL, 17, "#F2E8E0", ls=2.4, max_w=440),
            tx(300, 534, "Don’t look back.", SERIF_IT, 40, "#FFF4E4", max_w=440)]
    return P.render(art, text, seed=301, edge=2.2, bristle=0.45, grain=0.2)


# ================================================================ medusa — seen only in the bronze shield (plate)
def gorgon_reflection(P, cx, cy, r, seed):
    """What the polished shield shows: the mouth of the cave glowing a sick green, and against it the Gorgon's head
    and shoulders in silhouette, the serpents of her hair writhing out in every direction, her eyes burning."""
    rnd = random.Random(seed)
    out = [K.path(sp(ellipse(cx, cy, r, r, 40)), P.rad([(0, "#C8F0C0"), (0.35, "#6AA878"), (0.75, "#1E4030"), (1, "#081810")], cx=0.5, cy=0.42, r=0.62))]
    # the reflected cave arch
    arch = [(cx - r * 0.7, cy + r), (cx - r * 0.6, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.62), (cx + r * 0.3, cy - r * 0.62), (cx + r * 0.6, cy - r * 0.2), (cx + r * 0.7, cy + r)]
    out.append(f'<path d="{sp(arch)} M {cx - r - 10} {cy - r - 10} L {cx + r + 10} {cy - r - 10} L {cx + r + 10} {cy + r + 10} L {cx - r - 10} {cy + r + 10} Z" '
               f'fill="#06120C" fill-rule="evenodd" opacity="0.8"/>')
    # her silhouette
    hx, hy = cx, cy + r * 0.12
    sil = [(hx - r * 0.5, cy + r), (hx - r * 0.42, hy + r * 0.5), (hx - r * 0.2, hy + r * 0.34), (hx - r * 0.16, hy + r * 0.18), (hx - r * 0.2, hy - r * 0.05),
           (hx - r * 0.16, hy - r * 0.24), (hx, hy - r * 0.32), (hx + r * 0.16, hy - r * 0.24), (hx + r * 0.2, hy - r * 0.05), (hx + r * 0.16, hy + r * 0.18),
           (hx + r * 0.2, hy + r * 0.34), (hx + r * 0.42, hy + r * 0.5), (hx + r * 0.5, cy + r)]
    snakes = []
    for k in range(17):
        a = math.radians(-200 + k * (220 / 16))
        base_ = (hx + math.cos(a) * r * 0.16, hy - r * 0.04 + math.sin(a) * r * 0.22)
        L_ = r * rnd.uniform(0.32, 0.5)
        pts = []
        for j in range(8):
            t = j / 7
            wig = math.sin(t * math.pi * 2.2 + k) * r * 0.05
            pts.append((base_[0] + math.cos(a) * L_ * t - math.sin(a) * wig, base_[1] + math.sin(a) * L_ * t + math.cos(a) * wig))
        snakes.append(K.taper(pts, r * 0.07, r * 0.03, "#020604"))
        hd = pts[-1]
        snakes.append(f'<ellipse cx="{hd[0]:.1f}" cy="{hd[1]:.1f}" rx="{r * 0.035:.1f}" ry="{r * 0.024:.1f}" fill="#020604" transform="rotate({math.degrees(a):.0f} {hd[0]:.1f} {hd[1]:.1f})"/>')
    out.append("".join(snakes))
    out.append(K.path(sp(sil), "#020604"))
    for sg in (-1, 1):
        ex, ey = hx + sg * r * 0.075, hy - r * 0.06
        out.append(screen(glow(P, ex, ey, r * 0.1, "#8AFF9A", 0.9)))
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{r * 0.03:.1f}" ry="{r * 0.018:.1f}" fill="#E8FFD8"/>')
    # the mirror's sheen: a diagonal glare and a darker rim of polish
    out.append(f'<path d="M {cx - r} {cy - r * 0.2} L {cx - r * 0.2} {cy - r} L {cx + r * 0.1} {cy - r} L {cx - r} {cy + r * 0.1} Z" fill="#FFFFFF" opacity="0.12" {P.blur(r * 0.06)}/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000000" stroke-width="{r * 0.12:.1f}" opacity="0.35" {P.blur(r * 0.05)}/>')
    return clip_to(P, sp(ellipse(cx, cy, r, r, 40)), out)


def stone_warrior_g(P, x, y, s, seed, L, flip=False):
    """A warrior turned to stone the instant he looked: a hoplite flinching back behind his raised shield, his spear
    dropped; grey limestone, cracked, lichen in the folds."""
    def Q(pts):
        return place(pts, x, y, s, flip)
    stone = ("#C8CCC0", "#6A6E66", "#1A1C18")
    B = K.Body(P, L)
    B.add(Q(K.limb([(6, -92), (16, -48), (24, -6)], [9, 7, 5], [9, 7.5, 5])), stone, core=0.6, lit=0.35)
    B.add(Q(K.limb([(-6, -92), (-16, -50), (-12, -6)], [9, 7, 5], [9, 7.5, 5])), stone, core=0.5, lit=0.4)
    B.add(Q([(-16, -100), (14, -100), (18, -78), (-20, -78)]), stone, core=0.5, lit=0.4)
    B.add(Q([(-16, -100), (-22, -130), (-18, -156), (4, -164), (18, -150), (14, -120), (14, -100)]), stone, core=0.5, lit=0.45)
    B.add(Q(ellipse(-2, -176, 10, 12, 14)), stone, core=0.45, lit=0.5)
    B.add(Q([(-10, -180), (0, -196), (12, -196), (14, -180), (4, -172)]), stone, core=0.4, lit=0.5)                     # crested helmet
    B.add(Q(K.limb([(-16, -150), (-34, -146), (-44, -164)], [6, 5, 4], [6, 5, 4])), stone, core=0.45, lit=0.45)
    shield = Q(ellipse(-48, -150, 26, 30, 24))
    B.add(shield, stone, core=0.5, lit=0.5)
    out = [B.render(rims=[dict(L=L, col="#C8F0C8", d=1.6, op=0.7)], edge_op=0.6)]
    rnd = random.Random(seed)
    for k in range(6):
        p0 = Q([(rnd.uniform(-20, 20), rnd.uniform(-160, -20))])[0]
        out.append(K.stroke_line([p0, (p0[0] + rnd.uniform(-8, 8), p0[1] + rnd.uniform(6, 16)), (p0[0] + rnd.uniform(-8, 8), p0[1] + rnd.uniform(16, 26))], "#1A1C18", 0.9, 0.6, smooth=False))
    return "".join(out)


@plate("medusa")
def medusa_p():
    P = Plate("myp-me")
    rnd = random.Random(3)
    L = (0.6, -0.8)
    art = [K.path(lp([(-10, -10), (610, -10), (610, 610), (-10, 610)]), "#060C0A")]
    art.append(screen(glow(P, 300, 300, 360, "#2A5A40", 0.6)))
    # the cave of the Gorgons: rock walls, a far glow of daylight behind the viewer catching the edges
    for k, w in enumerate(([(-20, -20), (240, -20), (200, 80), (120, 160), (60, 300), (40, 460), (-20, 520)],
                           [(640, -20), (400, -20), (440, 90), (520, 180), (560, 320), (600, 470), (640, 520)])):
        art.append(crag(P, w + ([(-20, 520)] if k == 0 else [(640, 520)]), ("#5A7A68", "#16241E", "#040806"), 20 + k, L=L, lit="#9AD8B0", faces=30, strata=12))
    floor = [(-20, 620), (-20, 470), (200, 450), (400, 456), (640, 446), (640, 620)]
    art.append(form(P, sp(floor), ("#4A5A50", "#16201A", "#040806"), L, K.bbox(floor), core=0.4, lit=0.3, sd=12))
    for k in range(14):
        x, y = rnd.uniform(20, 580), rnd.uniform(470, 580)
        art.append(K.taper([(x, y), (x + rnd.uniform(8, 18), y + rnd.uniform(-4, 4))], 3, 2, "#C8C8B8", 0.6))
    # what is left of those who looked: a stone hand reaching up from the rubble, a toppled helmeted head
    for k, (bx, by, br) in enumerate(((90, 470, 30), (130, 486, 22), (520, 470, 28), (480, 488, 20), (560, 490, 18))):
        b_ = K.wobble(ellipse(bx, by, br, br * 0.6, 10), k, br * 0.15)
        art.append(form(P, sp(b_), ("#A8B0A0", "#4A524A", "#101410"), L, K.bbox(b_), core=0.5, lit=0.45, edge="#000000", edge_op=0.6, rim_col="#B8E8C0", rim_d=1.4))
    sh = [(80, 456), (78, 410), (74, 384), (68, 360, 1), (76, 362), (80, 380), (84, 352, 1), (90, 354), (90, 380), (96, 358, 1), (102, 362), (98, 388),
          (104, 372, 1), (110, 378), (102, 410), (98, 456)]
    art.append(form(P, sp(sh), ("#C8CCC0", "#6A6E66", "#1A1C18"), L, K.bbox(sh), core=0.5, lit=0.5, edge="#000000", edge_op=0.6, rim_col="#C8F0C8", rim_d=1.4,
                    extra=[K.stroke_line([(84, 440), (88, 420), (86, 404)], "#1A1C18", 0.9, 0.6)]))
    hd = [(512, 462), (500, 448), (502, 430), (516, 420), (534, 424), (544, 438), (540, 456), (526, 464)]
    art.append(form(P, sp(hd), ("#C8CCC0", "#6A6E66", "#1A1C18"), L, K.bbox(hd), core=0.5, lit=0.5, edge="#000000", edge_op=0.6, rim_col="#C8F0C8", rim_d=1.4,
                    extra=[K.path(sp([(504, 434), (514, 412), (530, 402), (546, 410), (536, 420), (520, 422)]), "#8A8E86"),
                           K.stroke_line([(502, 444), (508, 452), (504, 458)], "#1A1C18", 1.2, 0.6)]))
    art.append(K.haze(P, 300, 520, "#2A4A38", 0.0, 0.4))
    # the shield of Perseus, held up as a mirror; his hand gripping the rim
    cx, cy, r = 300, 314, 150
    art.append(K.cast_shadow(P, cx + 10, cy + 20, r * 1.02, r * 1.02, "#000000", 0.6, sd=20))
    rim_ = sp(ellipse(cx, cy, r + 16, r + 16, 48))
    art.append(form(P, rim_, ("#FFE8A8", "#B8862A", "#3A2408"), (-0.6, -0.8), (cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16), core=0.5, lit=0.6,
                    edge="#000000", edge_op=0.6))
    # a meander (Greek key) band chased round the rim
    mk = []
    for k in range(40):
        a0 = math.radians(k * 9)
        a1 = math.radians(k * 9 + 6)
        rr0, rr1 = r + 4, r + 12
        p = [(cx + math.cos(a0) * rr0, cy + math.sin(a0) * rr0), (cx + math.cos(a0) * rr1, cy + math.sin(a0) * rr1),
             (cx + math.cos(a1) * rr1, cy + math.sin(a1) * rr1), (cx + math.cos(a1) * (rr0 + 4), cy + math.sin(a1) * (rr0 + 4))]
        mk.append(K.stroke_line(p, "#3A2408", 1.4, 0.75, smooth=False))
    art.append("".join(mk))
    art.append(gorgon_reflection(P, cx, cy, r, 5))
    # the harpe, the hooked sword Hermes lent him, held low at the left, catching the green light
    blade = [(160, 474), (168, 440), (180, 404), (194, 372, 1), (200, 378), (190, 410), (178, 446), (170, 478)]
    hook = [(186, 414), (176, 398), (172, 384), (176, 372, 1), (182, 388), (190, 402)]
    for sh_ in (blade, hook):
        art.append(form(P, sp(sh_), ("#F2FFF2", "#9AA8A0", "#2A3430"), (-0.6, -0.8), K.bbox(sh_), core=0.4, lit=0.6, edge="#000000", edge_op=0.6))
    art.append(K.stroke_line([(184, 380), (172, 440)], "#FFFFFF", 0.9, 0.7))
    art.append(K.stroke_line([(156, 476), (176, 480)], "#C8A040", 4, 1))
    art.append(K.stroke_line([(166, 480), (156, 512)], "#5A3A1A", 6, 1))
    art.append(K.vignette(P, "#010302", 0.5, 0.55))
    art.append(K.text_scrim(P, 480, 600, "#010302", 0.75))
    text = [gilt(P, 300, 98, "MEDUSA", CINZEL, 60, ls=14, max_w=420, seed=8, deboss="#000000", dop=0.85),
            tx(300, 128, "GREEK · SEEN ONLY IN THE SHIELD", CINZEL, 17, "#E0F2E4", ls=2.5, max_w=440),
            tx(300, 534, "Never meet her eyes.", SERIF_IT, 30, "#E8F8EC", max_w=440)]
    return P.render(art, text, seed=311, edge=2.0, bristle=0.45, grain=0.2)


# @@PLATES@@


if __name__ == "__main__":
    build(sys.argv[1:] or None)
