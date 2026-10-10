"""Home Notes, hand-painted (gouache / storybook) edition: warm sayings about home and family for the fridge.

Thirty pieces, each its own little painting - cottages and porches, front doors and mailboxes, teacups,
quilts, birds and wildflowers - in a cozy palette of cream paper, rose, terracotta, sage, mustard and dusty blue,
with brush-textured lettering. Repaints the six original Home Notes slugs (same words) and adds twenty-four.

Run from tools/designs:  python3 home_notes_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open
from fall_gouache_b import (brush, dabs, form, glow, shadow, bg, vignette, btext, plain, hand_rule, sparkle, heart_path,
                            lgrad, wobble_line, hill, fruit_tree, steam, painted_heart)
from bee_kind_painted import (stem, leaf_shape, green_leaf, daisy, lavender, cosmos, bluebell, poppy, grass, ribbon, rose,
                              round_tree, poplar, puff_cloud, cloud2, blossom, twig, teacup, saucer, bow, picket_fence, soft_poly,
                              poly_d, mixc, gingham, ruled_c, fur, cr_sample, rays, peony_bud)
from paint import conifer

COL = "home-notes"

# ---------------------------------------------------------------- palette  (base, dark, light)
INK = "#3A2418"
PAPER = "#F7EEDF"
FLECK = "#8A6A4A"
CREAM = ("#FBF3E4", "#DCCCB0", "#FFFFFF")
ROSE = ("#E3897F", "#B4554F", "#F6BDB2")
BLUSH = ("#F2C4BA", "#D08E84", "#FCE2DA")
BERRY = ("#C8464A", "#8A2228", "#EE7E78")
TERRA = ("#CC6A44", "#8E3A22", "#EC9A70")
SAGE = ("#9EAE88", "#66784E", "#CBD6B4")
LEAF = ("#7E9450", "#4E6232", "#AFC27A")
DEEP = ("#55704A", "#34482C", "#7E9A68")
MUST = ("#E8B04A", "#B47A1E", "#F8D486")
BLUE = ("#86A4BE", "#55728E", "#BCD0E0")
TEAL = ("#4E7C7A", "#2E5250", "#7EAAA4")
WOOD = ("#C08A56", "#7E5230", "#E0B282")
DARKWOOD = ("#8A5A36", "#5A3620", "#B4845A")
LAVC = ("#A898CC", "#6E5E9A", "#D4CAEC")


def _f(v):
    return f"{v:.1f}"


class Ids:
    """Unique, slug-prefixed ids (pages inline many SVGs)."""

    def __init__(self, slug):
        self.p, self.n = "hnp-" + slug, 0

    def __call__(self, tag="i"):
        self.n += 1
        return f"{self.p}-{tag}{self.n}"


def finish(u, color=INK, op=0.6, seed=9):
    return grain(u("gr"), color, seed, op)


DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ shared painted pieces
def sky(u, stops, y1=600, seed=1, tints=None, n=160, angle=-4):
    """Graded sky with horizontal brush texture."""
    g = u("sky")
    o = [f'<defs>{lgrad(g, stops)}</defs><rect x="-10" y="-10" width="620" height="{y1 + 10}" fill="url(#{g})"/>']
    if tints:
        o.append(brush((-40, -20, 640, y1), tints, seed, n, angle, (60, 180), (4, 12), (0.06, 0.16), 0.1, 4))
    return "".join(o)


def rect_d(x0, y0, x1, y1):
    return f"M {_f(x0)} {_f(y0)} L {_f(x1)} {_f(y0)} L {_f(x1)} {_f(y1)} L {_f(x0)} {_f(y1)} Z"


def org_rect(x0, y0, x1, y1, seed, amt=0.8, k=0.08):
    return soft_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], seed, amt, k)


def smoke(x, y, h, seed, col="#FFFFFF", op=0.55):
    """A soft curl of chimney smoke: stacked puffs drifting right."""
    rnd = random.Random(seed)
    o = []
    for i in range(6):
        t = i / 5
        r = 6 + 9 * t
        o.append(f'<path d="{blob(x + 30 * t * t + rnd.uniform(-2, 2), y - h * t, r, r * 0.8, seed + i, 0.12, 10)}" fill="{col}" opacity="{op * (1 - t * 0.6):.2f}"/>')
    return "".join(o)


def songbird(u, cx, cy, s, seed, pal=BLUE, belly=("#F4C8A0", "#C8885A", "#FFE4C8"), flip=False, rot=0, beak_open=False, wing_up=False):
    """A round little storybook songbird (bluebird / robin), head to the left; s ~ body half-length."""
    k = s / 30
    tr = f"translate({_f(cx)} {_f(cy)}) rotate({rot}) scale({'-' if flip else ''}{k:.3f} {k:.3f})"
    o = [f'<g transform="{tr}">']
    # tail
    tail = smooth_closed([(18, -2), (52, -16), (58, -8), (50, 4), (20, 10)])
    o.append(form(u, tail, (16, -18, 60, 12), pal[1], mixc(pal[1], "#000000", 0.3), pal[0], seed, -10, n=10, shade=None, ink_w=2.2, ink_col=INK))
    # legs
    o.append(f'<path d="M -6 22 l -3 14 m 3 -14 l 4 13 M 6 22 l -1 14 m 1 -14 l 6 12" stroke="#7A4A2A" stroke-width="2.6" stroke-linecap="round" fill="none"/>')
    body = blob(0, 0, 30, 24, seed + 1, 0.03, 16)
    bel = f'<path d="{blob(-6, 12, 22, 14, seed + 2, 0.06, 12)}" fill="{belly[0]}"/><path d="{blob(-10, 16, 12, 6, seed + 3, 0.1, 10)}" fill="{belly[2]}" opacity="0.6"/>'
    o.append(form(u, body, (-30, -26, 32, 26), pal[0], pal[1], pal[2], seed + 4, -30, n=60, shade=(4, 6), shade_op=0.45, hi=(-12, -14, 10, 6),
                  ink_w=2.4, ink_col=INK, length=(4, 12), width=(0.8, 2), extra_in=bel))
    # head
    hd = blob(-24, -14, 16, 15, seed + 5, 0.03, 14)
    o.append(form(u, hd, (-40, -30, -8, 2), pal[0], pal[1], pal[2], seed + 6, -40, n=24, shade=(2, 3), shade_op=0.35, ink_w=2.2, ink_col=INK,
                  length=(3, 8), width=(0.8, 1.6)))
    # wing
    if wing_up:
        wg = smooth_closed([(-6, -8), (8, -40), (26, -46), (28, -30), (16, -6)])
        o.append(form(u, wg, (-8, -48, 30, -4), pal[1], mixc(pal[1], "#000000", 0.3), pal[0], seed + 7, -70, n=14, shade=None, ink_w=2.2, ink_col=INK,
                      extra_in='<path d="M 4 -20 l 16 -14 M 8 -12 l 16 -12" stroke="#FFFFFF" stroke-width="1.6" opacity="0.4"/>'))
    else:
        wg = smooth_closed([(-12, -6), (10, -12), (34, -4), (24, 8), (0, 8)])
        o.append(form(u, wg, (-14, -14, 36, 10), pal[1], mixc(pal[1], "#000000", 0.3), pal[0], seed + 7, 10, n=14, shade=None, ink_w=2.2, ink_col=INK,
                      extra_in='<path d="M 8 -4 q 10 2 20 0 M 6 2 q 10 2 18 1" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.45"/>'))
    # beak, eye, cheek
    if beak_open:
        o.append('<path d="M -38 -17 L -52 -22 L -40 -13 L -52 -8 L -38 -10 Z" fill="#E8A23A" stroke="#7A4A10" stroke-width="1.4" stroke-linejoin="round"/>')
    else:
        o.append('<path d="M -38 -18 L -51 -13 L -38 -9 Z" fill="#E8A23A" stroke="#7A4A10" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append('<circle cx="-29" cy="-17" r="3.6" fill="#2A1A10"/><circle cx="-30.2" cy="-18.4" r="1.3" fill="#FFFFFF"/>'
             '<ellipse cx="-24" cy="-7" rx="4.5" ry="3" fill="#F0907A" opacity="0.55"/>')
    o.append("</g>")
    return "".join(o)


def pot(u, cx, base, w, h, seed, pal=TERRA, rim=True):
    """A terracotta flower pot with a rolled rim."""
    rh = h * 0.24 if rim else 0
    body = soft_poly([(cx - w * 0.45, base - h + rh - 2), (cx + w * 0.45, base - h + rh - 2), (cx + w * 0.35, base), (cx - w * 0.35, base)], seed + 7, 0.5, 0.12)
    o = [shadow(u, cx + 4, base, w * 0.6, 6, 0.3),
         form(u, body, (cx - w / 2, base - h, cx + w / 2, base), pal[0], pal[1], pal[2], seed, -90, n=w * h / 40, shade=(w * 0.14, 0), shade_op=0.5,
              hi=(cx - w * 0.22, base - h * 0.5, w * 0.06, h * 0.25), ink_w=2.0, length=(h * 0.2, h * 0.5), width=(1, 2.4))]
    if rim:
        rd = org_rect(cx - w / 2, base - h, cx + w / 2, base - h + rh, seed + 1, 0.6, 0.25)
        o.append(form(u, rd, (cx - w / 2, base - h, cx + w / 2, base - h + rh), pal[0], pal[1], pal[2], seed + 2, 0, n=w * rh / 30, shade=(w * 0.1, rh * 0.2),
                      shade_op=0.45, ink_w=2.0, length=(w * 0.1, w * 0.3), width=(1, 2)))
    return "".join(o)


def stripes_fill(box, col, w, gap, ang=0, op=0.5):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = max(x1 - x0, y1 - y0) * 1.5
    s = []
    x = -L
    while x < L:
        s.append(f"M {_f(cx + x)} {_f(cy - L)} L {_f(cx + x)} {_f(cy + L)}")
        x += gap
    return f'<path d="{" ".join(s)}" stroke="{col}" stroke-width="{w}" opacity="{op}" transform="rotate({ang} {_f(cx)} {_f(cy)})"/>'


def stone_path(u, pts, seed, pal=("#E2D6BE", "#B0A084", "#FFF8E8")):
    o = []
    for i, (x, y, r) in enumerate(pts):
        o.append(form(u, blob(x, y, r, r * 0.42, seed + i, 0.12, 12), (x - r, y - r * 0.5, x + r, y + r * 0.5), pal[0], pal[1], pal[2], seed + i, 0,
                      n=max(6, r * 0.6), shade=(0, -r * 0.12), ink_w=1.6, ink_col="#7A6A50"))
    return "".join(o)


def flower_cluster(u, x, y, seed, r=10, pal=BERRY, n=5, spread=18, kind="blossom"):
    rnd = random.Random(seed)
    o = []
    for i in range(n):
        fx, fy = x + rnd.uniform(-spread, spread), y + rnd.uniform(-spread * 0.5, spread * 0.5)
        rr = r * rnd.uniform(0.8, 1.15)
        if kind == "blossom":
            o.append(blossom(u, fx, fy, rr, seed + i, pal=pal, rot=rnd.uniform(0, 70)))
        else:
            o.append(f'<path d="{blob(fx, fy, rr, rr * 0.9, seed + i, 0.12, 10)}" fill="{pal[0]}"/>'
                     f'<path d="{blob(fx - rr * 0.3, fy - rr * 0.3, rr * 0.4, rr * 0.3, seed + i + 50, 0.15, 8)}" fill="{pal[2]}" opacity="0.8"/>'
                     + ink(blob(fx, fy, rr, rr * 0.9, seed + i, 0.12, 10), pal[1], 1.5, seed, 1, 0.6))
    return "".join(o)


def leafy_bush(u, cx, base, w, h, seed, pal=DEEP, flowers=None, fpal=ROSE, fr=9, ink_c="#2A3A20"):
    """A rounded shrub painted from several blobs, with optional flowers dotted through it."""
    rnd = random.Random(seed)
    d = " ".join(blob(cx + rnd.uniform(-w * 0.32, w * 0.32), base - h * rnd.uniform(0.35, 0.62), w * rnd.uniform(0.25, 0.36), h * rnd.uniform(0.3, 0.42),
                      seed + i, 0.08, 12) for i in range(6))
    d += " " + blob(cx, base - h * 0.32, w * 0.5, h * 0.34, seed + 9, 0.05, 14)
    o = [f'<path d="{d}" fill="none" stroke="{ink_c}" stroke-width="3" opacity="0.75" stroke-linejoin="round"/>',
         form(u, d, (cx - w * 0.6, base - h, cx + w * 0.6, base), pal[0], pal[1], pal[2], seed, lambda x, y: math.degrees(math.atan2(y - base + h * 0.5, x - cx)) + 90,
              n=w * h / 30, shade=(w * 0.08, h * 0.12), shade_op=0.55, hi=(cx - w * 0.18, base - h * 0.7, w * 0.14, h * 0.1), hi_op=0.35, ink_w=0,
              length=(w * 0.05, w * 0.16), width=(0.8, 2.2), curve=0.5,
              extra_in=dabs((cx - w * 0.5, base - h, cx + w * 0.5, base), [pal[1], pal[2]], seed + 5, w * h / 160, (1.5, 3.5), (0.3, 0.6), 0.5))]
    if flowers:
        for i in range(flowers):
            a = rnd.uniform(0, 2 * math.pi)
            rr = math.sqrt(rnd.random()) * 0.85
            fx, fy = cx + math.cos(a) * w * 0.42 * rr, base - h * 0.5 + math.sin(a) * h * 0.36 * rr
            o.append(blossom(u, fx, fy, fr * rnd.uniform(0.8, 1.1), seed + 20 + i, pal=fpal, rot=rnd.uniform(0, 70)))
    return "".join(o)


def window(u, cx, cy, w, h, seed, glass=("#BCD6E2", "#7E9EB4", "#EAF4F8"), frame="#FBF6EC", lit=False, shutters=None, box=None, arch=False, panes=(2, 2)):
    """A painted cottage window: frame, mullions, sky reflection or warm light, optional shutters and a flower box."""
    o = []
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if shutters:
        for s in (-1, 1):
            sx0 = cx + s * (w / 2 + 3) if s > 0 else cx - w / 2 - 3 - w * 0.42
            sd = org_rect(sx0, y0 - 2, sx0 + w * 0.42, y1 + 2, seed + s, 0.5, 0.06)
            slats = "".join(f'<path d="M {_f(sx0 + 3)} {_f(y0 + t * (h + 4))} l {_f(w * 0.42 - 6)} 0" stroke="{shutters[1]}" stroke-width="1.6" opacity="0.6"/>'
                            for t in [i / 7 for i in range(1, 7)])
            o.append(form(u, sd, (sx0, y0, sx0 + w * 0.42, y1), shutters[0], shutters[1], shutters[2], seed + 3 + s, -90, n=w * h / 70, shade=(2, 0),
                          ink_w=1.6, extra_in=slats))
    fd = org_rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4, seed + 5, 0.5, 0.05)
    o.append(f'<path d="{fd}" fill="{frame}"/>' + ink(fd, INK, 1.8, seed, 1, 0.7))
    gd = org_rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, seed + 6, 0.4, 0.04)
    if lit:
        o.append(glow(u, cx, cy, w * 1.1, "#FFC860", 0.45))
        o.append(form(u, gd, (x0, y0, x1, y1), "#FFD27A", "#E8A040", "#FFF0C0", seed + 7, -90, n=w * h / 50, shade=(0, -h * 0.2), shade_op=0.35, ink_w=0))
    else:
        o.append(form(u, gd, (x0, y0, x1, y1), glass[0], glass[1], glass[2], seed + 7, -50, n=w * h / 50, shade=(-w * 0.1, -h * 0.15), shade_op=0.4, ink_w=0,
                      extra_in=f'<path d="M {_f(x0 + w * 0.15)} {_f(y1)} L {_f(x0 + w * 0.65)} {_f(y0)} L {_f(x0 + w * 0.82)} {_f(y0)} L {_f(x0 + w * 0.32)} {_f(y1)} Z" fill="#FFFFFF" opacity="0.35"/>'))
    mx = "".join(f'<path d="M {_f(x0 + (x1 - x0) * i / panes[0])} {_f(y0)} L {_f(x0 + (x1 - x0) * i / panes[0])} {_f(y1)}"/>' for i in range(1, panes[0]))
    my = "".join(f'<path d="M {_f(x0)} {_f(y0 + (y1 - y0) * i / panes[1])} L {_f(x1)} {_f(y0 + (y1 - y0) * i / panes[1])}"/>' for i in range(1, panes[1]))
    o.append(f'<g stroke="{frame}" stroke-width="{max(2.5, w * 0.06):.1f}">{mx}{my}</g>')
    o.append(f'<g stroke="{INK}" stroke-width="1" opacity="0.4">{mx}{my}</g>')
    if box:
        bd = org_rect(x0 - 8, y1 + 2, x1 + 8, y1 + 2 + h * 0.22, seed + 9, 0.5, 0.1)
        o.append(flower_cluster(u, cx, y1 - 2, seed + 11, r=w * 0.11, pal=box, n=6, spread=w * 0.48))
        for i in range(5):
            o.append(green_leaf(u, x0 + i * w / 4, y1 + 2, w * 0.18, w * 0.06, -90 + (i - 2) * 30, seed + 30 + i, pal=LEAF, vein=False))
        o.append(form(u, bd, (x0 - 8, y1, x1 + 8, y1 + h * 0.25), WOOD[0], WOOD[1], WOOD[2], seed + 10, 0, n=w * h / 80, shade=(0, -3), ink_w=1.8))
        # trailing ivy over the box
        for i, xx in enumerate((x0 - 2, x1 - 6)):
            o.append(ink(smooth_open([(xx, y1 + 6), (xx - 4, y1 + h * 0.35), (xx + 2, y1 + h * 0.55)]), LEAF[1], 1.8, seed + 40 + i, 1, 0.9))
            for j in range(3):
                o.append(f'<path d="{blob(xx - 2 + (j % 2) * 5, y1 + h * 0.2 + j * h * 0.13, 3.6, 2.6, seed + 50 + i * 5 + j, 0.1, 8)}" fill="{LEAF[0]}" stroke="{LEAF[1]}" stroke-width="1"/>')
    return "".join(o)


# ================================================================ there's no place like home
def cottage_house(u, cx, base, w, h, seed, wall=CREAM, roof=TERRA, door=TEAL, shutters=SAGE, box=BERRY, chimney=True):
    """A storybook cottage, front gable: clapboard walls, shingled roof, attic window, shuttered windows with flower boxes,
    a round-topped door with a little wreath, a porch lamp and a chimney."""
    o = []
    x0, x1, top = cx - w / 2, cx + w / 2, base - h
    peak = top - w * 0.42
    o.append(shadow(u, cx + 10, base + 2, w * 0.66, 12, 0.3))
    if chimney:
        chx = cx + w * 0.26
        cd = org_rect(chx - 13, top - w * 0.42, chx + 13, top, seed + 1, 0.5, 0.06)
        bricks = "".join(f'<path d="M {_f(chx - 13)} {_f(top - w * 0.42 + 9 * i)} l 26 0" stroke="#7A3A22" stroke-width="1.4" opacity="0.6"/>' for i in range(1, 6))
        o.append(form(u, cd, (chx - 13, top - w * 0.42, chx + 13, top), "#B05A3E", "#7A3420", "#D8846A", seed + 2, -90, n=20, shade=(5, 0), ink_w=1.8, extra_in=bricks))
        o.append(f'<path d="{org_rect(chx - 16, top - w * 0.42 - 6, chx + 16, top - w * 0.42 + 2, seed + 3)}" fill="#8A4028" stroke="{INK}" stroke-width="1.6"/>')
        o.append(smoke(chx + 2, top - w * 0.42 - 12, 70, seed + 4, "#FFFFFF", 0.7))
    # walls with clapboard lines
    wd = soft_poly([(x0, base), (x0, top), (cx, peak + 8), (x1, top), (x1, base)], seed + 5, 0.6, 0.02)
    boards = "".join(f'<path d="M {_f(x0)} {_f(y)} L {_f(x1)} {_f(y + 0.6)}" stroke="{wall[1]}" stroke-width="1.6" opacity="0.7"/>'
                     for y in [peak + 30 + i * 12 for i in range(int((base - peak - 30) / 12) + 1)])
    o.append(form(u, wd, (x0, peak, x1, base), wall[0], wall[1], wall[2], seed + 6, -90, n=w * h / 40, shade=(w * 0.1, 0), shade_op=0.45,
                  ink_w=2.2, extra_in=boards))
    # roof: two slopes with eaves, scalloped shingles
    ov = w * 0.09
    rf = soft_poly([(x0 - ov, top + 6), (cx, peak - 6), (x1 + ov, top + 6), (x1 + ov - 6, top + 18), (cx, peak + 14), (x0 - ov + 6, top + 18)], seed + 7, 0.6, 0.05)
    sh = []
    rnd = random.Random(seed + 70)
    y = peak + 4
    row = 0
    while y < top + 22:
        xs = x0 - ov - 12 + (6 if row % 2 else 0)
        while xs < x1 + ov + 12:
            sh.append(f"M {_f(xs)} {_f(y)} q 6 {_f(7 + rnd.uniform(-1, 1))} 12 0")
            xs += 12
        y += 9
        row += 1
    shingles = f'<path d="{" ".join(sh)}" stroke="{roof[1]}" stroke-width="1.6" fill="none" opacity="0.65"/>'
    o.append(form(u, rf, (x0 - ov, peak - 6, x1 + ov, top + 18), roof[0], roof[1], roof[2], seed + 8, 35, n=w * 0.8, shade=(0, -8), shade_op=0.5,
                  ink_w=2.4, length=(8, 24), width=(1, 3), extra_in=shingles))
    # attic round window
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(top - w * 0.16)}" r="{_f(w * 0.07)}" fill="#FBF6EC" stroke="{INK}" stroke-width="1.8"/>'
             f'<circle cx="{_f(cx)}" cy="{_f(top - w * 0.16)}" r="{_f(w * 0.05)}" fill="#FFD27A"/>'
             f'<path d="M {_f(cx - w * 0.05)} {_f(top - w * 0.16)} L {_f(cx + w * 0.05)} {_f(top - w * 0.16)} M {_f(cx)} {_f(top - w * 0.21)} L {_f(cx)} {_f(top - w * 0.11)}" stroke="#FBF6EC" stroke-width="2.4"/>')
    # windows
    for s in (-1, 1):
        o.append(window(u, cx + s * w * 0.29, top + h * 0.4, w * 0.17, h * 0.34, seed + 20 + s, shutters=shutters, box=box, lit=False))
    # door with arch, panels, knob, wreath; porch lamp; step
    dw, dh = w * 0.2, h * 0.62
    dd = (f"M {_f(cx - dw / 2)} {_f(base)} L {_f(cx - dw / 2)} {_f(base - dh + dw / 2)} A {_f(dw / 2)} {_f(dw / 2)} 0 0 1 {_f(cx + dw / 2)} {_f(base - dh + dw / 2)} "
          f"L {_f(cx + dw / 2)} {_f(base)} Z")
    panel = (f'<path d="{org_rect(cx - dw * 0.32, base - dh * 0.55, cx + dw * 0.32, base - dh * 0.2, seed + 30)}" fill="none" stroke="{door[1]}" stroke-width="2"/>')
    o.append(f'<path d="{dd}" fill="#FBF6EC" transform="translate(0 0) scale(1)" stroke="#FBF6EC" stroke-width="8" stroke-linejoin="round"/>')
    o.append(form(u, dd, (cx - dw / 2, base - dh, cx + dw / 2, base), door[0], door[1], door[2], seed + 31, -90, n=dw * dh / 30, shade=(dw * 0.15, 0),
                  ink_w=2.0, extra_in=panel))
    o.append(f'<circle cx="{_f(cx + dw * 0.28)}" cy="{_f(base - dh * 0.4)}" r="2.6" fill="#E8C060" stroke="{INK}" stroke-width="1"/>')
    wr = dw * 0.26
    for i in range(10):
        a = 2 * math.pi * i / 10
        o.append(f'<path d="{blob(cx + math.cos(a) * wr, base - dh * 0.7 + math.sin(a) * wr, 4.5, 3, seed + 40 + i, 0.1, 8, math.degrees(a) + 90)}" fill="{LEAF[0] if i % 2 else DEEP[0]}"/>')
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(base - dh * 0.7 + wr)}" r="3" fill="{BERRY[0]}"/>')
    o.append(f'<path d="{org_rect(cx - dw * 0.7, base - 2, cx + dw * 0.7, base + 8, seed + 50, 0.5, 0.2)}" fill="#C8BCA4" stroke="{INK}" stroke-width="1.6"/>')
    lx = cx - dw * 0.85
    o.append(glow(u, lx, base - dh * 0.72, 22, "#FFD070", 0.7))
    o.append(f'<path d="M {_f(lx - 5)} {_f(base - dh * 0.8)} L {_f(lx + 5)} {_f(base - dh * 0.8)} L {_f(lx + 4)} {_f(base - dh * 0.64)} L {_f(lx - 4)} {_f(base - dh * 0.64)} Z" fill="#FFE29A" stroke="{INK}" stroke-width="1.6"/>'
             f'<path d="M {_f(lx - 7)} {_f(base - dh * 0.8)} L {_f(lx)} {_f(base - dh * 0.88)} L {_f(lx + 7)} {_f(base - dh * 0.8)} Z" fill="{INK}"/>')
    return "".join(o)


@design("theres-no-place-like-home")
def no_place_like_home():
    u = Ids("theres-no-place-like-home")
    o = [bg(u, PAPER, ["#F2E6D2", "#FBF4E8"], 11)]
    o.append(sky(u, [(0, "#B8D2DE"), (0.5, "#DDE8E2"), (0.78, "#F6EBD4")], 470, 12, ["#CFE0E6", "#FFFFFF", "#B0C8D6"]))
    o.append(glow(u, 470, 300, 220, "#FFF2CC", 0.55))
    o.append(puff_cloud(u, 96, 262, 120, 40, 13) + puff_cloud(u, 512, 236, 104, 34, 14))
    o.append(hill(u, [(-20, 390), (100, 366), (220, 380), (360, 358), (480, 372), (620, 352)], 640, "#B4C6A6", "#94AA88", "#D4E0C6", 15))
    o.append(hill(u, [(-20, 418), (140, 404), (300, 412), (460, 398), (620, 410)], 640, "#9AB27A", "#7A9460", "#BED09C", 16))
    o.append(fruit_tree(u, 96, 470, 70, 17, greens=("#7E9A58", "#56703A", "#A8C27A"), fruit=16, fruitc=("#E8705A", "#FFE0C8")))
    o.append(poplar(u, 520, 470, 170, 18, pal=("#6E8A4E", "#4A6232", "#9AB070")) + poplar(u, 552, 476, 140, 19, pal=("#7E9A5A", "#56703A", "#A8C27A")))
    o.append(cottage_house(u, 300, 470, 210, 124, 20))
    o.append(leafy_bush(u, 172, 474, 64, 46, 21, flowers=7, fpal=BLUSH, fr=7) + leafy_bush(u, 428, 474, 64, 46, 22, flowers=7, fpal=BLUSH, fr=7))
    o.append(hill(u, [(-20, 472), (150, 466), (300, 470), (450, 464), (620, 470)], 640, "#8EA466", "#6E8A44", "#B4C67E", 23))
    o.append(grass(24, (-20, 472, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 160, (8, 20), 2.0))
    # winding path from the door to us
    path = smooth_closed([(286, 474), (314, 474), (330, 520), (362, 572), (378, 610), (252, 610), (276, 560), (282, 516)])
    o.append(form(u, path, (250, 470, 380, 610), "#E8D8B8", "#C0A87E", "#FBF0DA", 25, -90, n=120, shade=(10, 0), shade_op=0.35, ink_w=1.6, ink_col="#8A7050"))
    o.append(stone_path(u, [(300, 490, 13), (308, 518, 16), (318, 552, 19), (308, 590, 22)], 26))
    # picket fence with the gate open at the path
    fence_l = picket_fence(u, 552, 27, x0=-10, x1=230, h=58, gap=28)
    fence_r = picket_fence(u, 552, 28, x0=394, x1=610, h=58, gap=28)
    o.append(fence_l + fence_r)
    # foreground garden: cosmos, daisies and lavender at the corners
    o.append(lavender(u, 70, 610, 120, 29, ang=-98, buds=9) + lavender(u, 92, 612, 104, 30, ang=-84, buds=8) + lavender(u, 46, 612, 96, 31, ang=-108, buds=8))
    o.append(cosmos(u, 150, 560, 22, 32, pal=ROSE) + daisy(u, 196, 584, 18, 33, tilt=0.85) + daisy(u, 120, 590, 15, 34, tilt=0.85))
    o.append(cosmos(u, 470, 566, 20, 35, pal=BLUSH) + cosmos(u, 512, 540, 24, 36, pal=ROSE) + daisy(u, 430, 588, 17, 37, tilt=0.85) + daisy(u, 548, 590, 15, 38, tilt=0.85))
    o.append(green_leaf(u, 150, 600, 40, 11, -120, 39) + green_leaf(u, 500, 600, 40, 11, -60, 40))
    o.append(songbird(u, 236, 506, 12, 41, pal=BLUE, flip=True))
    # lettering
    o.append(ruled_c(u, 104, "THERE'S NO PLACE", JOST, 28, "#7A4636", 42, ls=6, line_w=34, line="#B4554F"))
    t, _, _ = btext(u, 300, 196, "like home", SERIF_IT, 116, "#A2423A", ["#C0564A", "#86302C", "#D8705E"], 43, max_w=470, angle=-35,
                    shadow="#FFF6E6", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ our happy place
def adirondack(u, cx, base, s, seed, pal):
    """An Adirondack chair seen from behind: a fan of back slats, wide arms, legs on the deck."""
    k = s / 100
    o = [shadow(u, cx + 6 * k, base, 58 * k, 8 * k, 0.35)]
    X = lambda v: cx + v * k
    Y = lambda v: base - v * k
    # legs
    for lx in (-40, 40):
        o.append(f'<path d="{org_rect(X(lx - 5), Y(48), X(lx + 5), Y(0), seed + lx)}" fill="{pal[1]}" stroke="{INK}" stroke-width="1.6"/>')
    # arms (flat boards seen from behind, slightly from above)
    for sg in (-1, 1):
        ad = soft_poly([(X(sg * 26), Y(52)), (X(sg * 62), Y(56)), (X(sg * 64), Y(46)), (X(sg * 26), Y(42))], seed + sg, 0.5, 0.15)
        o.append(form(u, ad, (X(-66), Y(58), X(66), Y(40)), pal[0], pal[1], pal[2], seed + 3 + sg, 0, n=8, shade=(0, 2), ink_w=1.6))
    # back slats fanning out, rounded tops
    slats = []
    for i in range(5):
        a = (i - 2) * 6
        bx = cx + (i - 2) * 12 * k
        topx = bx + math.sin(math.radians(a)) * 90 * k
        topy = Y(44) - math.cos(math.radians(a)) * (92 - abs(i - 2) * 7) * k
        w = 5.4 * k
        sd = smooth_closed([(bx - w, Y(40)), (topx - w, topy + 6 * k), (topx, topy), (topx + w, topy + 6 * k), (bx + w, Y(40))])
        slats.append(form(u, sd, (min(bx, topx) - w, topy, max(bx, topx) + w, Y(40)), pal[0], pal[1], pal[2], seed + 10 + i, -90, n=10,
                          shade=(w * 0.5, 0), shade_op=0.4, ink_w=1.6, length=(10 * k, 30 * k), width=(0.8, 1.6)))
    o.append("".join(slats))
    # cross braces
    for yy in (62, 84):
        bd = org_rect(X(-34), Y(yy + 5), X(34), Y(yy - 2), seed + yy, 0.4, 0.2)
        o.append(f'<path d="{bd}" fill="{pal[1]}" stroke="{INK}" stroke-width="1.6"/>')
    # rim light from the sunset on the slat tops
    o.append(f'<path d="M {_f(X(-30))} {_f(Y(118))} Q {_f(cx)} {_f(Y(140))} {_f(X(30))} {_f(Y(118))}" stroke="#FFD8A8" stroke-width="2.2" fill="none" opacity="0.6"/>')
    return "".join(o)


@design("our-happy-place")
def our_happy_place():
    u = Ids("our-happy-place")
    hz = 372
    o = [paper(u("pp"), "#F2D6C4", FLECK, 51, 1.0)]
    o.append(sky(u, [(0, "#6E78AC"), (0.42, "#B48CB4"), (0.78, "#EFA08E"), (1, "#F8CE96")], hz, 52, ["#C8A0C0", "#F6B8A0", "#8E86B8"], 200))
    o.append(glow(u, 334, hz - 14, 300, "#FFD9A0", 0.75, 200))
    sun = blob(334, hz - 18, 40, 40, 53, 0.02, 20)
    o.append(form(u, sun, (294, hz - 58, 374, hz + 22), "#FFE6B4", "#F6B878", "#FFF8E0", 54, 0, n=40, shade=None, ink_w=0))
    o.append(puff_cloud(u, 120, 246, 120, 26, 55, pal=("#F6C2B4", "#B48CB4", "#FFE2D0")) + puff_cloud(u, 488, 278, 130, 24, 56, pal=("#F8C8A8", "#C08AA8", "#FFE8D4")))
    for x, y, s in ((404, 248, 9), (426, 236, 7), (386, 232, 6)):
        o.append(f'<path d="M {x - s} {y} q {s / 2} -5 {s} 0 q {s / 2} -5 {s} 0" stroke="#4A3A5E" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    # far hills (hazy lavender), then the tree line
    o.append(hill(u, [(-20, 352), (80, 334), (200, 348), (300, 356), (420, 340), (520, 330), (620, 344)], hz + 4, "#A88AAE", "#8E74A0", "#C8AACA", 57, sop=(0.1, 0.25)))
    rnd = random.Random(58)
    trees = []
    for x in list(range(-10, 250, 9)) + list(range(400, 620, 9)):
        h = rnd.uniform(18, 44) * (1.4 if x > 480 else 1)
        trees.append(conifer(x + rnd.uniform(-3, 3), hz + 2, h, "#5E5280", rnd.random(), width=0.36))
    o.append("".join(trees))
    o.append(f'<path d="M -20 {hz} L 620 {hz} L 620 {hz + 6} L -20 {hz + 6} Z" fill="#5E5280"/>')
    # the lake
    wg = u("wt")
    o.append(f'<defs>{lgrad(wg, [(0, "#F4BC96"), (0.3, "#C898AE"), (1, "#5A6094")])}</defs><rect x="-10" y="{hz + 2}" width="620" height="{620 - hz}" fill="url(#{wg})"/>')
    # reflections of the tree line (mirrored, soft)
    o.append(f'<g transform="translate(0 {2 * hz + 8}) scale(1 -1)" opacity="0.32">{"".join(trees)}</g>')
    o.append(brush((-20, hz + 6, 620, 600), ["#FFE2C0", "#8E7AAE", "#F6C8A8", "#6E6EA0"], 59, 260, 0, (20, 70), (1, 3), (0.2, 0.5), 0.05, 2))
    # sun path on the water
    sp = []
    for i in range(22):
        y = hz + 8 + i * 9 + (i * i) * 0.12
        w = 46 - i * 1.2 + rnd.uniform(-8, 8)
        sp.append(f'<path d="M {_f(334 - w / 2 + rnd.uniform(-8, 8))} {_f(y)} q {_f(w / 2)} -2 {_f(w)} 0" stroke="{rnd.choice(["#FFE6B4", "#FFF4D8", "#F8C890"])}" '
                  f'stroke-width="{max(1.6, 4 - i * 0.12):.1f}" stroke-linecap="round" opacity="{0.9 - i * 0.03:.2f}"/>')
    o.append("".join(sp))
    # the near shore on the right with a little cabin and tall pines
    shore = smooth_closed([(380, 412), (440, 398), (520, 392), (640, 386), (640, 432), (520, 430), (420, 424)])
    o.append(form(u, shore, (380, 386, 640, 432), "#4E4468", "#36304E", "#6E6488", 60, 0, n=40, shade=None, ink_w=0))
    cab = []
    cx, base, w = 466, 404, 64
    cab.append(form(u, org_rect(cx - w / 2, base - 34, cx + w / 2, base, 61), (cx - w / 2, base - 34, cx + w / 2, base), "#7A4E44", "#4E3030", "#A8705E", 62, 0, n=20, shade=None, ink_w=1.6,
                    extra_in="".join(f'<path d="M {cx - w / 2} {base - 34 + 6 * i} l {w} 0" stroke="#4E3030" stroke-width="1.4" opacity="0.6"/>' for i in range(1, 6))))
    cab.append(f'<path d="{soft_poly([(cx - w / 2 - 8, base - 32), (cx, base - 62), (cx + w / 2 + 8, base - 32)], 63, 0.4, 0.1)}" fill="#3E2E3A" stroke="{INK}" stroke-width="1.6"/>')
    cab.append(glow(u, cx - 12, base - 18, 30, "#FFC860", 0.8))
    cab.append(f'<rect x="{cx - 20}" y="{base - 26}" width="16" height="13" fill="#FFD27A" stroke="{INK}" stroke-width="1.4"/><path d="M {cx - 12} {base - 26} l 0 13 M {cx - 20} {base - 19.5} l 16 0" stroke="#7A4E44" stroke-width="1.2"/>')
    cab.append(f'<rect x="{cx + 6}" y="{base - 28}" width="14" height="28" fill="#4E3030" stroke="{INK}" stroke-width="1.4"/>')
    cab.append(smoke(cx + 18, base - 66, 40, 64, "#E8C8D8", 0.5))
    cab.append(f'<rect x="{cx + 12}" y="{base - 66}" width="9" height="16" fill="#3E2E3A"/>')
    o.append("".join(cab))
    for i, (x, h) in enumerate(((410, 62), (530, 120), (566, 150), (602, 132), (504, 84))):
        o.append(conifer(x, 408 if x < 500 else 400, h, "#2E2A44", 65 + i, width=0.34))
    o.append(f'<g opacity="0.14" transform="translate(0 {2 * 412}) scale(1 -1)">' + "".join(conifer(x, 408, h, "#2E2A44", 65 + i, width=0.34) for i, (x, h) in enumerate(((530, 120), (566, 150), (602, 132)))) + "</g>")
    # the dock running out into the water, two chairs facing the sunset
    near_y, far_y = 612, 470
    nl, nr, fl, fr_ = 0, 300, 148, 240
    dock = poly_d([(nl, near_y), (fl, far_y), (fr_, far_y), (nr, near_y)])
    boards = []
    for i in range(1, 14):
        t = (i / 14) ** 1.6
        y = far_y + (near_y - far_y) * t
        xl, xr = fl + (nl - fl) * t, fr_ + (nr - fr_) * t
        boards.append(f"M {_f(xl)} {_f(y)} L {_f(xr)} {_f(y + 0.5)}")
    o.append(f'<path d="{poly_d([(nl - 14, near_y), (fl - 6, far_y + 4), (fl, far_y), (nl, near_y)])}" fill="#4A2E26"/>')
    for i, (px, py, ph) in enumerate(((fl - 3, far_y, 26), (fr_ - 1, far_y, 24), (fl - 3 + (nl - fl) * 0.45, far_y + (near_y - far_y) * 0.45, 40))):
        o.append(f'<path d="{org_rect(px - 4, py - 10, px + 4, py + ph, 66 + i)}" fill="#4A2E26" stroke="{INK}" stroke-width="1.4"/>')
    o.append(form(u, dock, (nl, far_y, nr, near_y), "#A8704A", "#6E4430", "#D29A6A", 67, -60, n=120, shade=(-10, 0), shade_op=0.4, ink_w=2.0,
                  length=(20, 60), width=(1, 3), extra_in=f'<path d="{" ".join(boards)}" stroke="#5A3424" stroke-width="2" opacity="0.6"/>'
                  f'<path d="M {fl} {far_y} L {nl} {near_y}" stroke="#F6C08A" stroke-width="4" opacity="0.45"/>'))
    o.append(adirondack(u, 104, 566, 72, 68, TERRA))
    o.append(adirondack(u, 210, 556, 66, 69, TEAL))
    o.append(f'<path d="{blob(160, 520, 10, 4, 70, 0.1, 10)}" fill="#3A2418" opacity="0.3"/>')
    # lettering in the sky
    t, _, _ = btext(u, 300, 112, "our", SERIF_IT, 64, "#FFF3E2", ["#FFFFFF", "#F6DCC8"], 71, angle=-30, shadow="#4E3A6A", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 202, "happy place", SERIF_IT, 106, "#FFF3E2", ["#FFFFFF", "#F8DCC6", "#FFE8D0"], 72, max_w=470, angle=-30,
                    shadow="#4E3A6A", soff=(0.02, 0.04))
    o.append(t)
    o.append(finish(u, "#2A1A30", 0.5))
    return "".join(o)


# ================================================================ family is everything
@design("family-is-everything")
def family_is_everything():
    u = Ids("family-is-everything")
    o = [bg(u, "#F6EDDD", ["#EFE2CC", "#FBF4E6", "#E8DCC4"], 81, angle=-20)]
    o.append(glow(u, 300, 210, 280, "#F8E0B0", 0.6))
    # a painted ground mound
    mound = smooth_closed([(60, 392), (180, 360), (300, 352), (420, 360), (540, 392), (420, 404), (300, 408), (180, 404)])
    o.append(form(u, mound, (60, 350, 540, 410), "#9AB27A", "#6E8A50", "#C0D49C", 82, -4, n=120, shade=(0, -8), ink_w=1.8, ink_col="#4E6232"))
    o.append(grass(83, (90, 356, 510, 400), ["#6E8A44", "#A8BC70", "#5E7A3A"], 90, (6, 14), 1.8))
    # trunk and branches
    tr = smooth_closed([(272, 384), (282, 330), (284, 290), (250, 250), (222, 232), (232, 224), (268, 248), (292, 268), (300, 230), (296, 200), (308, 200),
                        (314, 236), (316, 266), (346, 238), (380, 224), (388, 234), (356, 254), (322, 292), (322, 336), (334, 384)])
    o.append(form(u, tr, (220, 196, 390, 386), "#8A5A36", "#5A3620", "#B4845A", 84, -90, n=120, shade=(10, 0), shade_op=0.5, ink_w=2.4,
                  length=(10, 30), width=(1, 2.4), extra_in='<path d="M 300 380 q -4 -40 2 -80 M 312 360 q 2 -20 -2 -40" stroke="#5A3620" stroke-width="1.6" fill="none" opacity="0.6"/>'))
    # canopy of many leafy puffs
    rnd = random.Random(85)
    puffs = [(300, 150, 120, 84), (180, 196, 88, 66), (420, 196, 90, 66), (226, 120, 76, 56), (376, 118, 78, 56), (128, 240, 54, 40), (472, 240, 56, 40),
             (300, 236, 110, 50), (300, 90, 70, 38)]
    d = " ".join(blob(x, y, rx, ry, 86 + i, 0.07, 16) for i, (x, y, rx, ry) in enumerate(puffs))
    o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.2" opacity="0.7" stroke-linejoin="round"/>')
    leaves = dabs((74, 56, 530, 286), [DEEP[1], LEAF[2], "#A8C27A"], 87, 240, (2.5, 5), (0.3, 0.6), 0.5)
    o.append(form(u, d, (70, 50, 530, 290), DEEP[0], DEEP[1], LEAF[0], 88, lambda x, y: math.degrees(math.atan2(y - 170, x - 300)) + 90, n=900,
                  shade=(12, 16), shade_op=0.55, hi=(240, 110, 70, 36), hi_op=0.35, ink_w=0, length=(8, 22), width=(1.2, 3.4), curve=0.5, extra_in=leaves))
    # branches peeking through
    o.append(ink("M 292 268 Q 280 250 262 248 M 316 266 Q 330 250 352 246", "#5A3620", 4, 89, 1, 0.9))
    # hearts growing like fruit
    hearts = [(300, 120, 15, BERRY, -6), (214, 170, 13, ROSE, 10), (388, 160, 14, BERRY, -10), (156, 226, 11, BLUSH, 4), (452, 222, 12, ROSE, 8),
              (254, 236, 12, ROSE, -8), (346, 212, 13, BLUSH, 6), (232, 108, 11, BLUSH, -12), (372, 96, 11, ROSE, 12), (300, 196, 12, ROSE, 0),
              (110, 250, 9, BERRY, -4), (494, 254, 10, BERRY, 6), (420, 268, 9, BLUSH, 0), (176, 270, 9, BERRY, 0)]
    for i, (x, y, s, pal, r) in enumerate(hearts):
        o.append(f'<path d="M {x} {y - s * 0.8} l 0 -6" stroke="#5A3620" stroke-width="1.8"/>')
        o.append(f'<g transform="rotate({r} {x} {y})">' + painted_heart(u, x, y, s, pal, 90 + i) + "</g>")
    # one heart drifting down, one already on the grass
    o.append(f'<g transform="rotate(-24 150 330)">' + painted_heart(u, 150, 330, 10, ROSE, 110) + "</g>")
    o.append(f'<g transform="rotate(70 214 384)">' + painted_heart(u, 214, 384, 9, BERRY, 111) + "</g>")
    # the swing
    for x in (392, 440):
        o.append(ink(f"M {x - 6} 262 L {x} 344", "#7A5A3A", 2.6, 112 + x, 2, 0.95))
    seat = org_rect(376, 342, 456, 352, 113, 0.5, 0.2)
    o.append(form(u, seat, (376, 340, 456, 354), WOOD[0], WOOD[1], WOOD[2], 114, 0, n=10, shade=(0, -2), ink_w=1.8))
    o.append(songbird(u, 418, 328, 11, 115, pal=ROSE, belly=CREAM, flip=True))
    o.append(daisy(u, 134, 394, 13, 116, tilt=0.8) + daisy(u, 470, 392, 12, 117, tilt=0.8) + daisy(u, 492, 384, 9, 118, tilt=0.8) + daisy(u, 112, 386, 9, 119, tilt=0.8))
    # lettering
    t, _, _ = btext(u, 300, 488, "family", SERIF_IT, 120, "#5A2A24", ["#7A3A30", "#3E1A14", "#8E4A3A"], 120, max_w=420, angle=-35, shadow="#F2C8B4",
                    soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 536, "IS EVERYTHING", JOST, 30, "#8A3A30", 121, ls=8, line_w=38, line="#B4554F"))
    o.append(finish(u))
    return "".join(o)


# ================================================================ welcome home
def lantern(u, x, y, seed):
    o = [glow(u, x, y + 10, 70, "#FFC860", 0.55)]
    o.append(f'<path d="M {x - 26} {y - 40} L {x - 8} {y - 40} L {x - 8} {y - 30}" stroke="#2A2420" stroke-width="4" fill="none"/>')
    body = poly_d([(x - 14, y - 22), (x + 14, y - 22), (x + 12, y + 30), (x - 12, y + 30)])
    o.append(f'<path d="{body}" fill="#FFD68A"/>')
    o.append(glow(u, x, y + 8, 18, "#FFFFFF", 0.8))
    o.append(f'<path d="M {x - 3} {y + 22} L {x - 3} {y + 6} Q {x} {y - 6} {x + 3} {y + 6} L {x + 3} {y + 22} Z" fill="#FFF6E0"/>'
             f'<path d="{blob(x, y + 2, 2.6, 5, seed, 0.1, 8)}" fill="#F2A33A"/>')
    o.append(f'<path d="{body}" fill="none" stroke="#2A2420" stroke-width="3"/><path d="M {x} {y - 22} L {x} {y + 30} M {x - 13} {y + 4} L {x + 13} {y + 4}" stroke="#2A2420" stroke-width="2"/>')
    o.append(f'<path d="M {x - 20} {y - 22} L {x} {y - 40} L {x + 20} {y - 22} Z" fill="#2A2420"/><path d="M {x - 16} {y + 30} L {x + 16} {y + 30} L {x + 10} {y + 38} L {x - 10} {y + 38} Z" fill="#2A2420"/>'
             f'<circle cx="{x}" cy="{y - 44}" r="4" fill="none" stroke="#2A2420" stroke-width="2.4"/>')
    return "".join(o)


def wreath(u, cx, cy, r, seed, flowers=True, bow_pal=BLUSH):
    """A full door wreath: greenery and eucalyptus round a ring, blush roses and berries, a satin bow."""
    rnd = random.Random(seed)
    o = [shadow(u, cx + 6, cy + 8, r * 1.15, r * 1.15, 0.25)]
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#6E5236" stroke-width="{r * 0.2:.1f}"/>')
    for i in range(46):
        a = 2 * math.pi * i / 46 + rnd.uniform(-0.05, 0.05)
        rr = r * rnd.uniform(0.86, 1.12)
        px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        ang = math.degrees(a) + 90 + rnd.choice((-40, 40)) + rnd.uniform(-12, 12)
        pal = rnd.choice((DEEP, LEAF, DEEP, SAGE))
        o.append(green_leaf(u, px, py, r * rnd.uniform(0.42, 0.6), r * 0.15, ang, seed + i, pal=pal, vein=True))
    for i in range(14):
        a = 2 * math.pi * i / 14 + 0.12
        px, py = cx + math.cos(a) * r * rnd.uniform(0.85, 1.15), cy + math.sin(a) * r * rnd.uniform(0.85, 1.15)
        o.append(f'<path d="{blob(px, py, r * 0.1, r * 0.09, seed + 40 + i, 0.06, 10)}" fill="{SAGE[0]}" stroke="{SAGE[1]}" stroke-width="1.4"/>'
                 f'<path d="{blob(px - 1.5, py - 1.5, r * 0.04, r * 0.03, seed + 60 + i, 0.06, 8)}" fill="{SAGE[2]}" opacity="0.8"/>')
    if flowers:
        for i, (a, rr, pal) in enumerate(((140, 0.17, BLUSH), (165, 0.2, ROSE), (118, 0.14, CREAM), (20, 0.13, BLUSH), (-60, 0.12, ROSE))):
            ar = math.radians(a)
            o.append(rose(u, cx + math.cos(ar) * r, cy + math.sin(ar) * r, r * rr, seed + 80 + i, pal=pal))
        for i in range(9):
            a = math.radians(rnd.uniform(100, 200) if i < 6 else rnd.uniform(-80, 20))
            px, py = cx + math.cos(a) * r * rnd.uniform(0.75, 1.25), cy + math.sin(a) * r * rnd.uniform(0.75, 1.25)
            o.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="{r * 0.045 + 1.6:.1f}" fill="{BERRY[0]}" stroke="{BERRY[1]}" stroke-width="1"/>'
                     f'<circle cx="{_f(px - 1)}" cy="{_f(py - 1)}" r="1" fill="#FFFFFF" opacity="0.8"/>')
    o.append(bow(u, cx, cy + r * 1.0, r * 0.32, seed + 99, pal=bow_pal))
    return "".join(o)


@design("welcome-home")
def welcome_home():
    u = Ids("welcome-home")
    o = [paper(u("pp"), "#ECE6DA", FLECK, 131, 1.0)]
    # painted clapboard siding
    boards = []
    for i, y in enumerate(range(0, 620, 30)):
        boards.append(f'<path d="M -10 {y + 28} L 610 {y + 29}" stroke="#B8B0A0" stroke-width="3" opacity="0.7"/>'
                      f'<path d="M -10 {y + 31} L 610 {y + 32}" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
    o.append(brush((-20, -20, 620, 620), ["#F6F2EA", "#D8D0C0", "#FFFFFF"], 132, 260, 0, (40, 140), (2, 6), (0.12, 0.3), 0.05, 2))
    o.append("".join(boards))
    o.append(vignette(u, "#6E6454", 0.35, 0.55))
    # door surround: pilasters, crown, transom
    o.append(shadow(u, 308, 410, 150, 220, 0.25))
    trim = soft_poly([(186, 600), (186, 214), (414, 214), (414, 600)], 133, 0.5, 0.01)
    o.append(form(u, trim, (186, 214, 414, 600), "#FBF7EE", "#D4CCBC", "#FFFFFF", 134, -90, n=160, shade=(14, 0), shade_op=0.4, ink_w=2.0))
    crown = soft_poly([(172, 214), (176, 196), (424, 196), (428, 214)], 135, 0.4, 0.05)
    o.append(form(u, crown, (172, 192, 428, 216), "#FBF7EE", "#D4CCBC", "#FFFFFF", 136, 0, n=30, shade=(0, -4), ink_w=2.0))
    o.append(glow(u, 300, 246, 110, "#FFC860", 0.4, 40))
    tw = org_rect(212, 226, 388, 264, 137, 0.4, 0.05)
    o.append(form(u, tw, (212, 226, 388, 264), "#FFD27A", "#E8A040", "#FFF0C0", 138, -90, n=40, shade=(0, -6), ink_w=2.0,
                  extra_in="".join(f'<path d="M {212 + 176 * i / 5:.0f} 226 L {212 + 176 * i / 5:.0f} 264" stroke="#FBF7EE" stroke-width="4"/>' for i in range(1, 5))))
    # the door
    door = org_rect(222, 274, 378, 566, 139, 0.4, 0.01)
    panels = ""
    for (x0, y0, x1, y1) in ((238, 292, 294, 400), (306, 292, 362, 400), (238, 420, 294, 540), (306, 420, 362, 540)):
        panels += (f'<path d="{org_rect(x0, y0, x1, y1, x0 + y0, 0.3, 0.03)}" fill="{TEAL[1]}" opacity="0.35"/>'
                   f'<path d="M {x0} {y1} L {x0} {y0} L {x1} {y0}" stroke="{TEAL[2]}" stroke-width="2.4" fill="none" opacity="0.8"/>'
                   f'<path d="M {x1} {y0} L {x1} {y1} L {x0} {y1}" stroke="#1E3A38" stroke-width="2.4" fill="none" opacity="0.7"/>')
    o.append(form(u, door, (222, 274, 378, 566), TEAL[0], TEAL[1], TEAL[2], 140, -90, n=300, shade=(18, 0), shade_op=0.45, ink_w=2.4,
                  length=(20, 60), width=(1.2, 3), extra_in=panels))
    o.append(f'<circle cx="360" cy="440" r="7" fill="#D8AE4E" stroke="{INK}" stroke-width="1.6"/><circle cx="358" cy="438" r="2.4" fill="#FFF0B8"/>'
             f'<path d="{org_rect(352, 450, 366, 476, 141, 0.3, 0.2)}" fill="#C89A3E" stroke="{INK}" stroke-width="1.4"/>')
    o.append(f'<path d="{org_rect(226, 538, 374, 562, 142, 0.4, 0.05)}" fill="#C89A3E" stroke="{INK}" stroke-width="1.6" opacity="0.9"/>'
             f'<path d="M 232 544 L 368 544" stroke="#FFE6A0" stroke-width="2" opacity="0.7"/>')
    # wreath hung on a ribbon
    o.append(f'<path d="M 300 274 L 300 288" stroke="{BLUSH[1]}" stroke-width="5"/>')
    o.append(wreath(u, 300, 350, 54, 143))
    # lanterns
    o.append(lantern(u, 140, 330, 144) + lantern(u, 460, 330, 145))
    # stone step and doormat
    step = soft_poly([(120, 566), (480, 566), (492, 610), (108, 610)], 146, 0.6, 0.03)
    o.append(form(u, step, (108, 562, 492, 610), "#C8C0B0", "#9A9284", "#E8E2D6", 147, 0, n=120, shade=(0, -6), ink_w=2.0))
    mat = soft_poly([(226, 572), (374, 572), (386, 604), (214, 604)], 148, 0.5, 0.05)
    o.append(form(u, mat, (214, 570, 386, 606), "#C8A06A", "#8E6A3E", "#E2C08A", 149, -90, n=80, shade=None, ink_w=1.8, length=(3, 8), width=(0.8, 1.6),
                  extra_in='<path d="M 232 578 L 368 578 L 378 598 L 222 598 Z" fill="none" stroke="#5A3A20" stroke-width="2.4" opacity="0.6"/>'))
    # potted topiaries either side
    for x, sd in ((148, 150), (452, 160)):
        o.append(pot(u, x, 568, 80, 70, sd, pal=TERRA))
        o.append(f'<path d="M {x} 504 L {x} 470" stroke="#5A3A20" stroke-width="4"/>')
        o.append(leafy_bush(u, x, 486, 96, 92, sd + 1, pal=DEEP, flowers=0))
        for j, sg in enumerate((-1, 1)):
            vx = x + sg * 30
            o.append(ink(smooth_open([(vx, 500), (vx + sg * 8, 524), (vx + sg * 4, 552)]), LEAF[1], 2, sd + 5 + j, 1, 0.9))
            for k in range(4):
                o.append(green_leaf(u, vx + sg * (6 + (k % 2) * 4), 506 + k * 12, 12, 5, 90 + sg * (50 - k * 8), sd + 10 + j * 4 + k, pal=LEAF, vein=False))
    # lettering
    t, _, _ = btext(u, 300, 142, "welcome", SERIF_IT, 106, "#2E5250", ["#3E6A68", "#1E3A38", "#4E7C7A"], 151, max_w=460, angle=-35,
                    shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 184, "HOME", JOST, 30, "#B4554F", 152, ls=12, line_w=60, gap=18, line="#B4554F"))
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ love lives here
@design("love-lives-here")
def love_lives_here():
    u = Ids("love-lives-here")
    o = [bg(u, "#F8E6CE", ["#F4DCC0", "#FCF0E0", "#F0D2B4"], 161, fleck="#9A6A5A", angle=-20)]
    o.append(glow(u, 300, 330, 260, "#FFF2E6", 0.7))
    # a soft garden behind: a rolling hedge line, a blossom tree and a bit of picket fence
    o.append(hill(u, [(-20, 470), (100, 448), (220, 462), (360, 444), (480, 458), (620, 440)], 640, "#C4D0AE", "#A4B48C", "#DCE4C8", 1601, sop=(0.1, 0.3)))
    o.append(fruit_tree(u, 112, 486, 62, 1602, greens=("#9AB27A", "#6E8A50", "#C0D49C"), fruit=18, fruitc=("#F4B8C4", "#FFFFFF")))
    o.append(fruit_tree(u, 512, 478, 48, 1603, greens=("#A8BC88", "#7E9460", "#C8D8A8"), fruit=12, fruitc=("#F4B8C4", "#FFFFFF"), detail=False))
    o.append(picket_fence(u, 528, 1604, x0=380, x1=610, h=50, gap=26))
    o.append(picket_fence(u, 528, 1605, x0=-10, x1=250, h=50, gap=26))
    # ground
    gd = smooth_closed([(-20, 540), (150, 520), (300, 528), (450, 516), (620, 530), (620, 640), (-20, 640)])
    o.append(form(u, gd, (-20, 512, 620, 640), "#9AB27A", "#6E8A50", "#C0D49C", 162, -4, n=160, shade=(0, -6), ink_w=1.6, ink_col="#4E6232"))
    o.append(grass(163, (-20, 516, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 160, (8, 20), 2.0))
    # the post
    post = org_rect(318, 352, 350, 560, 164, 0.6, 0.02)
    o.append(form(u, post, (318, 352, 350, 560), WOOD[0], WOOD[1], WOOD[2], 165, -90, n=60, shade=(8, 0), ink_w=2.2,
                  extra_in='<path d="M 330 380 q 2 60 -1 120 M 340 420 q 1 40 -1 80" stroke="#7E5230" stroke-width="1.4" fill="none" opacity="0.6"/>'))
    o.append(shadow(u, 340, 560, 50, 8, 0.3))
    # the mailbox in three-quarter view: arched front, long side, open door
    fx0, fx1, ftop, fbot = 186, 256, 252, 352
    side = smooth_closed([(222, ftop), (402, ftop - 6), (424, ftop + 8), (432, ftop + 40), (432, fbot - 6), (252, fbot), (256, fbot - 40), (250, ftop + 14)])
    side = (f"M 221 {ftop} L 400 {ftop - 6} Q 432 {ftop - 4} 434 {ftop + 34} L 434 {fbot - 8} L 254 {fbot} L 256 {ftop + 34} Q 254 {ftop} 221 {ftop} Z")
    ribs = "".join(f'<path d="M {x} {ftop - 4 + (x - 256) * -0.03:.1f} Q {x + 6} {ftop + 30} {x + 2} {fbot - 2 - (x - 256) * 0.045:.1f}" stroke="{SAGE[1]}" stroke-width="2" fill="none" opacity="0.4"/>' for x in (300, 350, 400))
    o.append(form(u, side, (220, ftop - 8, 436, fbot + 2), SAGE[0], SAGE[1], SAGE[2], 166, 0, n=200, shade=(0, -16), shade_op=0.45, ink_w=2.6,
                  length=(20, 60), width=(1.2, 3),
                  extra_in=ribs + f'<path d="M 236 {ftop + 8} L 410 {ftop + 2}" stroke="#FFFFFF" stroke-width="6" opacity="0.4" stroke-linecap="round"/>'))
    # a painted heart on the side
    o.append(f'<g transform="rotate(-4 346 318)">' + painted_heart(u, 346, 312, 15, BERRY, 167) + "</g>")
    # the flag, raised
    o.append(f'<path d="{org_rect(406, 236, 414, 318, 168, 0.3, 0.2)}" fill="{BERRY[1]}" stroke="{INK}" stroke-width="1.6"/>')
    fl = soft_poly([(404, 220), (440, 222), (440, 248), (404, 250)], 169, 0.4, 0.1)
    o.append(form(u, fl, (404, 218, 442, 252), BERRY[0], BERRY[1], BERRY[2], 170, 0, n=16, shade=(0, 3), ink_w=1.8))
    o.append(f'<circle cx="410" cy="310" r="4" fill="#5A4A3A"/>')
    # opening (dark inside) and the letters peeking out
    front = f"M {fx0} {fbot} L {fx0} {ftop + 34} Q {fx0} {ftop} {(fx0 + fx1) / 2} {ftop} Q {fx1} {ftop} {fx1} {ftop + 34} L {fx1} {fbot} Z"
    o.append(f'<path d="{front}" fill="#4A4A3A"/><path d="{front}" fill="none" stroke="{SAGE[1]}" stroke-width="7"/>' + ink(front, INK, 2.4, 171, 1, 0.8))
    o.append(f'<path d="{blob(222, 318, 26, 30, 172, 0.05, 12)}" fill="#2E2A22" opacity="0.6"/>')
    for i, (x, y, r, pal) in enumerate(((196, 290, -28, CREAM), (220, 278, -12, ("#F6E2D0", "#D8B8A0", "#FFF8EE")), (206, 304, -40, ("#FBEFE4", "#D8C4B0", "#FFFFFF")))):
        env = org_rect(x - 36, y - 22, x + 36, y + 22, 173 + i, 0.5, 0.05)
        o.append(f'<g transform="rotate({r} {x} {y})">' + form(u, env, (x - 36, y - 22, x + 36, y + 22), pal[0], pal[1], pal[2], 174 + i, 0, n=20, shade=(0, -4),
                                                                ink_w=1.8, extra_in=f'<path d="M {x - 36} {y - 22} L {x} {y + 4} L {x + 36} {y - 22}" stroke="{pal[1]}" stroke-width="2" fill="none"/>')
                 + f'<path d="{heart_path(x, y + 2, 7)}" fill="{BERRY[0]}" stroke="{BERRY[1]}" stroke-width="1.2"/></g>')
    # the door, dropped open on its hinge (we see its inside face)
    door = (f"M {fx0 - 2} {fbot + 2} L {fx1 - 2} {fbot + 2} L {fx1 - 10} {fbot + 44} Q {fx1 - 12} {fbot + 66} {(fx0 + fx1) / 2 - 6} {fbot + 68} "
            f"Q {fx0 - 2} {fbot + 66} {fx0 - 2} {fbot + 44} Z")
    o.append(form(u, door, (fx0 - 6, fbot, fx1, fbot + 70), "#B8C4A0", SAGE[1], "#DCE4C8", 175, -90, n=30, shade=(-6, 0), ink_w=2.2,
                  extra_in=f'<path d="M {fx0 + 6} {fbot + 8} L {fx1 - 10} {fbot + 8}" stroke="{SAGE[1]}" stroke-width="3" opacity="0.6"/>'))
    o.append(f'<path d="M {(fx0 + fx1) / 2 - 12} {fbot + 56} l 8 0" stroke="#5A4A3A" stroke-width="4" stroke-linecap="round"/>')
    # hearts floating up out of the mailbox
    for i, (x, y, s, r, pal) in enumerate(((150, 252, 12, -16, BERRY), (112, 236, 9, -26, ROSE), (176, 228, 7, 10, BLUSH), (100, 284, 7, -8, ROSE))):
        o.append(f'<g transform="rotate({r} {x} {y})">' + painted_heart(u, x, y, s, pal, 176 + i) + "</g>")
    o.append(songbird(u, 330, 236, 15, 212, pal=BLUE, flip=True))
    # climbing rose vine twining up the post
    vine = [(312, 560), (356, 520), (314, 480), (356, 440), (316, 400), (350, 366)]
    o.append(ink(smooth_open(vine), DEEP[1], 3, 180, 1, 1))
    rnd = random.Random(181)
    for i, (x, y) in enumerate(vine[1:]):
        o.append(green_leaf(u, x, y, 22, 7, rnd.choice((-30, -150, 20, 200)), 182 + i, pal=DEEP))
        o.append(green_leaf(u, x, y + 10, 18, 6, rnd.choice((-60, -120)), 190 + i, pal=LEAF, vein=False))
    for i, (x, y, r, pal) in enumerate(((356, 520, 15, BERRY), (314, 480, 13, BLUSH), (356, 440, 14, ROSE), (316, 402, 11, BERRY), (300, 540, 12, ROSE))):
        o.append(rose(u, x, y, r, 196 + i, pal=pal))
    # flowers round the foot of the post
    o.append(lavender(u, 470, 600, 110, 201, ang=-96, buds=9) + lavender(u, 494, 600, 96, 202, ang=-82, buds=8) + lavender(u, 448, 600, 90, 203, ang=-106, buds=7))
    o.append(daisy(u, 210, 560, 17, 204, tilt=0.85) + daisy(u, 172, 586, 15, 205, tilt=0.85) + daisy(u, 246, 588, 13, 206, tilt=0.85) + daisy(u, 412, 580, 15, 207, tilt=0.85))
    o.append(cosmos(u, 112, 552, 20, 208, pal=ROSE) + cosmos(u, 540, 552, 18, 209, pal=BLUSH))
    # lettering
    t, _, _ = btext(u, 300, 162, "love", SERIF_IT, 128, "#A8343A", ["#C04A4A", "#86222A", "#D4645C"], 210, max_w=420, angle=-35,
                    shadow="#FFF4EC", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 210, "LIVES HERE", JOST, 30, "#5E3A2E", 211, ls=10, line_w=40, line="#B4554F"))
    o.append(finish(u))
    return "".join(o)


# ================================================================ you are my sunshine
def happy_sun(u, cx, cy, r, seed, rays_n=14, face=True):
    rnd = random.Random(seed)
    o = [glow(u, cx, cy, r * 3.0, "#FFE08A", 0.85), glow(u, cx, cy, r * 1.7, "#FFF4C8", 0.9)]
    rd = []
    for i in range(rays_n):
        a = 2 * math.pi * i / rays_n
        L = r * (1.55 if i % 2 == 0 else 1.32)
        w = 0.17 if i % 2 == 0 else 0.13
        pts = [(cx + math.cos(a - w) * r * 0.95, cy + math.sin(a - w) * r * 0.95), (cx + math.cos(a) * L, cy + math.sin(a) * L),
               (cx + math.cos(a + w) * r * 0.95, cy + math.sin(a + w) * r * 0.95)]
        rd.append(smooth_closed(jitter(pts + [(cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], seed + i, 0.8)))
    rays_d = " ".join(rd)
    o.append(form(u, rays_d, (cx - r * 1.6, cy - r * 1.6, cx + r * 1.6, cy + r * 1.6), "#F6B83A", "#D4881E", "#FFDC7A", seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)),
                  n=r * 4, shade=None, ink_w=2.0, ink_col="#A8601A", length=(r * 0.2, r * 0.4), width=(1, 2.4)))
    disc = blob(cx, cy, r, r, seed + 1, 0.02, 18)
    o.append(form(u, disc, (cx - r, cy - r, cx + r, cy + r), "#FFD25A", "#E8A030", "#FFF0A8", seed + 2, -40, n=r * 5, shade=(r * 0.14, r * 0.16), shade_op=0.4,
                  hi=(cx - r * 0.35, cy - r * 0.4, r * 0.3, r * 0.2), hi_op=0.6, ink_w=2.4, ink_col="#A8601A", length=(r * 0.2, r * 0.5), width=(1, 3)))
    if face:
        for s in (-1, 1):
            o.append(ink(f"M {_f(cx + s * r * 0.36 - r * 0.13)} {_f(cy - r * 0.08)} q {_f(r * 0.13)} {_f(-r * 0.14)} {_f(r * 0.26)} 0", "#7A3A12", max(2.2, r * 0.06), seed + 3 + s, 1, 1))
            o.append(f'<ellipse cx="{_f(cx + s * r * 0.5)}" cy="{_f(cy + r * 0.2)}" rx="{_f(r * 0.14)}" ry="{_f(r * 0.09)}" fill="#F0806A" opacity="0.6"/>')
        o.append(ink(f"M {_f(cx - r * 0.24)} {_f(cy + r * 0.24)} q {_f(r * 0.24)} {_f(r * 0.24)} {_f(r * 0.48)} 0", "#7A3A12", max(2.4, r * 0.065), seed + 6, 1, 1))
    return "".join(o)


@design("you-are-my-sunshine")
def you_are_my_sunshine():
    u = Ids("you-are-my-sunshine")
    o = [bg(u, "#8EA6BC", ["#9AB2C6", "#7E96AE", "#A8BED0", "#6E88A2"], 221, fleck="#2A3A4A", angle=-25)]
    o.append(vignette(u, "#3E5068", 0.55, 0.5))
    o.append(glow(u, 300, 320, 300, "#FFE6A8", 0.55))
    # wooden shelf / table
    tb = smooth_closed([(-20, 436), (300, 430), (620, 436), (620, 640), (-20, 640)])
    o.append(form(u, tb, (-20, 428, 620, 640), "#9A6A44", "#62402A", "#C08A5E", 222, -2, n=260, shade=None, ink_w=0, length=(40, 140), width=(1.5, 4),
                  extra_in='<path d="M -20 500 Q 300 494 620 500 M -20 566 Q 300 572 620 566" stroke="#4E3020" stroke-width="2.4" fill="none" opacity="0.5"/>'))
    o.append('<path d="M -10 436 Q 300 428 610 436" stroke="#E8BC8A" stroke-width="3" fill="none" opacity="0.7"/>')
    o.append(glow(u, 300, 456, 200, "#FFD27A", 0.6, 34))
    o.append(shadow(u, 312, 456, 120, 12, 0.35))
    # the jar
    jx0, jx1, jtop, jbot = 196, 404, 214, 456
    body = (f"M {jx0 + 30} {jtop} L {jx1 - 30} {jtop} Q {jx1} {jtop + 4} {jx1} {jtop + 40} L {jx1} {jbot - 26} Q {jx1} {jbot} {jx1 - 26} {jbot} "
            f"L {jx0 + 26} {jbot} Q {jx0} {jbot} {jx0} {jbot - 26} L {jx0} {jtop + 40} Q {jx0} {jtop + 4} {jx0 + 30} {jtop} Z")
    neck = org_rect(232, 178, 368, 216, 223, 0.4, 0.1)
    o.append(f'<path d="{body}" fill="#DCEAF0" opacity="0.28"/><path d="{neck}" fill="#DCEAF0" opacity="0.3"/>')
    o.append(f'<ellipse cx="300" cy="{jbot - 6}" rx="98" ry="12" fill="#FFF2C8" opacity="0.35"/>')
    o.append(happy_sun(u, 300, 336, 54, 224))
    for x, y, s in ((236, 262, 7), (366, 276, 6), (244, 412, 5), (372, 404, 7), (300, 246, 4), (214, 330, 4), (388, 340, 4)):
        o.append(sparkle(x, y, s, "#FFFBE6", 0.95))
    # glass highlights and edges
    o.append(f'<path d="M {jx0 + 16} {jtop + 40} Q {jx0 + 12} {jtop + 130} {jx0 + 18} {jbot - 30}" stroke="#FFFFFF" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.55"/>'
             f'<path d="M {jx0 + 34} {jtop + 60} L {jx0 + 34} {jtop + 110}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.5"/>'
             f'<path d="M {jx1 - 18} {jtop + 50} Q {jx1 - 14} {jtop + 140} {jx1 - 20} {jbot - 40}" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.4"/>'
             f'<path d="M {jx0 + 6} {jbot - 14} Q 300 {jbot + 4} {jx1 - 6} {jbot - 14}" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.5"/>')
    o.append(ink(body, "#2E4050", 2.6, 225, 2, 0.75) + ink(neck, "#2E4050", 2.2, 226, 1, 0.7))
    o.append(f'<path d="M {jx0 + 8} {jtop + 22} Q 300 {jtop + 30} {jx1 - 8} {jtop + 22}" stroke="#2E4050" stroke-width="1.8" fill="none" opacity="0.4"/>')
    # lid band with threads
    lid = org_rect(222, 150, 378, 184, 227, 0.4, 0.15)
    threads = "".join(f'<path d="M 222 {y} Q 300 {y + 3} 378 {y}" stroke="#8A6A24" stroke-width="1.6" fill="none" opacity="0.6"/>' for y in (160, 168, 176))
    o.append(form(u, lid, (222, 150, 378, 184), "#D8B058", "#9A7428", "#F6DC92", 228, 0, n=40, shade=(0, -6), shade_op=0.5, ink_w=2.2, extra_in=threads))
    o.append(f'<path d="M 230 155 L 370 155" stroke="#FFF4C8" stroke-width="3" opacity="0.7"/>')
    # twine bow and a kraft tag
    o.append(f'<path d="M 230 196 Q 300 204 370 196" stroke="#C8A070" stroke-width="5" fill="none"/><path d="M 230 202 Q 300 210 370 202" stroke="#A88050" stroke-width="3" fill="none"/>')
    o.append(ink("M 250 200 q -24 -22 -34 -2 q 10 14 34 2 q -18 18 -38 34 M 250 200 q -10 24 -2 40", "#A88050", 3.2, 229, 1, 1))
    o.append(ink("M 360 202 q 30 20 58 38", "#A88050", 2.4, 230, 1, 1))
    tag = soft_poly([(404, 230), (428, 222), (468, 300), (436, 314)], 231, 0.4, 0.12)
    o.append(f'<g transform="rotate(-6 436 268)">' + form(u, tag, (404, 222, 470, 316), "#D8B486", "#A88050", "#F2D6AC", 232, -60, n=20, shade=(3, 0), ink_w=1.8)
             + f'<circle cx="420" cy="236" r="4" fill="none" stroke="#7A5A34" stroke-width="2"/>'
             + f'<path d="{heart_path(442, 278, 9)}" fill="{BERRY[0]}" stroke="{BERRY[1]}" stroke-width="1.2" transform="rotate(26 442 278)"/></g>')
    # lettering
    o.append(ruled_c(u, 102, "YOU ARE MY", JOST, 34, "#FFF4DE", 233, ls=10, line_w=44, line="#FFE08A"))
    t, _, _ = btext(u, 300, 534, "sunshine", SERIF_IT, 110, "#F8C64A", ["#FFE08A", "#E8A030", "#FFF0B0"], 234, max_w=460, angle=-35,
                    shadow="#3E2414", soff=(0.02, 0.04), hi="#FFF8D8")
    o.append(t)
    o.append(finish(u, "#1E2A38", 0.55))
    return "".join(o)


# ================================================================ all because two people fell in love
def open_sample(pts, per=10):
    """Dense points along an open Catmull-Rom curve through pts."""
    n = len(pts)
    out = []
    for i in range(n - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 +
                                    (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def soft_steam(pts, w0=3, w1=8, col="#FFFFFF", op=0.9, seed=1, glow_c=None):
    """A wisp of steam: a tapered, softly fading brush line (thin where it leaves the cup, fuller as it rises)."""
    rnd = random.Random(seed)
    sm = open_sample(pts, 8)
    n = len(sm)
    o = []
    if glow_c:
        o.append(f'<path d="{smooth_open(pts)}" stroke="{glow_c}" stroke-width="{w1 * 2.2:.1f}" fill="none" stroke-linecap="round" opacity="0.22"/>')
    for i in range(n - 1):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * math.sin(min(1, t * 1.6) * math.pi / 2)
        a = op * min(1, t * 6 + 0.25) * (0.85 + 0.15 * rnd.random())
        (x0, y0), (x1, y1) = sm[i], sm[i + 1]
        o.append(f'<path d="M {_f(x0)} {_f(y0)} L {_f(x1)} {_f(y1)}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round" opacity="{a:.2f}"/>')
    return "".join(o)


def stoneware_mug(u, cx, top, w, h, seed, glaze, side=1, drink=("#8A5432", "#5A3018", "#B47A50"), heart_c=None, dip=None):
    """A speckled stoneware mug: glazed body, unglazed foot, handle on `side`, coffee inside."""
    o = [shadow(u, cx + 8, top + h + 2, w * 0.66, 8, 0.35)]
    hx = cx + side * w * 0.48
    hd = f"M {_f(hx - side * 4)} {_f(top + h * 0.2)} q {_f(side * w * 0.42)} {_f(-h * 0.06)} {_f(side * w * 0.34)} {_f(h * 0.36)} q {_f(-side * w * 0.04)} {_f(h * 0.24)} {_f(-side * w * 0.34)} {_f(h * 0.22)}"
    o.append(f'<path d="{hd}" stroke="{INK}" stroke-width="{w * 0.15 + 3:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>'
             f'<path d="{hd}" stroke="{glaze[0]}" stroke-width="{w * 0.15:.1f}" fill="none" stroke-linecap="round"/>'
             f'<path d="{hd}" stroke="{glaze[2]}" stroke-width="{w * 0.04:.1f}" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(-1 -2)"/>')
    body = smooth_closed([(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.49, top + h * 0.7), (cx + w * 0.42, top + h), (cx - w * 0.42, top + h), (cx - w * 0.49, top + h * 0.7)])
    rnd = random.Random(seed)
    spk = "".join(f'<circle cx="{_f(rnd.uniform(cx - w / 2, cx + w / 2))}" cy="{_f(rnd.uniform(top, top + h))}" r="{rnd.uniform(0.7, 1.6):.1f}" fill="{rnd.choice([glaze[1], "#3A2418"])}" opacity="0.55"/>' for _ in range(int(w * h / 90)))
    foot = f'<path d="M {_f(cx - w)} {_f(top + h * 0.84)} L {_f(cx + w)} {_f(top + h * 0.84)} L {_f(cx + w)} {_f(top + h + 5)} L {_f(cx - w)} {_f(top + h + 5)} Z" fill="#E8D6B8"/>'
    if dip:
        foot = f'<path d="M {_f(cx - w)} {_f(top + h * dip)} Q {_f(cx)} {_f(top + h * dip + 8)} {_f(cx + w)} {_f(top + h * dip)} L {_f(cx + w)} {_f(top + h + 5)} L {_f(cx - w)} {_f(top + h + 5)} Z" fill="#E8D6B8"/>' + foot
    hrt = ""
    if heart_c:
        hrt = painted_heart(u, cx - side * w * 0.04, top + h * 0.5, w * 0.12, heart_c, seed + 9)
    o.append(form(u, body, (cx - w / 2, top, cx + w / 2, top + h), glaze[0], glaze[1], glaze[2], seed, -90, n=w * h / 30, shade=(side * -w * 0.0 + w * 0.14, 0), shade_op=0.45,
                  hi=(cx - w * 0.28, top + h * 0.45, w * 0.06, h * 0.26), hi_op=0.5, ink_w=2.2, length=(h * 0.15, h * 0.5), width=(1, 2.6), extra_in=spk + foot + hrt))
    o.append(f'<ellipse cx="{_f(cx)}" cy="{_f(top + 1)}" rx="{_f(w / 2 - 1)}" ry="{_f(w * 0.12)}" fill="{glaze[1]}"/>'
             f'<ellipse cx="{_f(cx)}" cy="{_f(top + 3)}" rx="{_f(w / 2 - 6)}" ry="{_f(w * 0.085)}" fill="{drink[0]}"/>'
             f'<ellipse cx="{_f(cx - w * 0.1)}" cy="{_f(top + 2)}" rx="{_f(w * 0.2)}" ry="{_f(w * 0.03)}" fill="{drink[2]}" opacity="0.6"/>'
             f'<ellipse cx="{_f(cx)}" cy="{_f(top + 1)}" rx="{_f(w / 2 - 1)}" ry="{_f(w * 0.12)}" fill="none" stroke="{INK}" stroke-width="2" opacity="0.75"/>')
    return "".join(o)


@design("all-because-two-people-fell-in-love")
def all_because():
    u = Ids("all-because-two-people-fell-in-love")
    o = [bg(u, "#F8E8DC", ["#F2DCCC", "#FCF2EA", "#EED2C2"], 301, fleck="#9A6A5A", angle=-20)]
    o.append(glow(u, 300, 300, 240, "#FFF6EA", 0.8))
    # a gingham tablecloth
    tc = smooth_closed([(-20, 468), (300, 460), (620, 468), (620, 640), (-20, 640)])
    gid, gdef = gingham(u, "#D07A74", "#FBEDE4", 22, 0, 0.42)
    o.append(gdef)
    o.append(form(u, tc, (-20, 456, 620, 640), "#FBEDE4", "#D8B0A4", "#FFFFFF", 302, -2, n=80, shade=(0, -10), shade_op=0.35, ink_w=0, length=(40, 120), width=(2, 5),
                  sop=(0.08, 0.2), extra_in=f'<path d="{tc}" fill="url(#{gid})"/>' + brush((-20, 456, 620, 640), ["#FFFFFF", "#B85A54"], 303, 120, 0, (30, 90), (2, 5), (0.06, 0.16), 0.1)))
    o.append('<path d="M -10 468 Q 300 460 610 468" stroke="#B85A54" stroke-width="2" fill="none" opacity="0.5"/>')
    # two mugs, handles turned outward
    o.append(stoneware_mug(u, 222, 382, 112, 104, 304, TERRA, side=-1, heart_c=CREAM, dip=0.62))
    o.append(stoneware_mug(u, 378, 382, 112, 104, 305, SAGE, side=1, heart_c=BLUSH, dip=0.62))
    # their steam rises, crosses, and each wisp draws one half of a single heart
    k, hcx, hcy = 3.3, 300, 300
    hp = [(hcx + k * 16 * math.sin(t) ** 3, hcy - k * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
          for t in [2 * math.pi * i / 40 for i in range(41)]]
    right_half = hp[0:21][::-1]     # tip -> up the right lobe -> top dip
    left_half = hp[20:41]           # tip -> up the left lobe -> top dip
    lpts = [(222, 376), (230, 364), (252, 356), (282, 352)] + right_half[1:]
    rpts = [(378, 376), (370, 364), (348, 356), (318, 352)] + left_half[1:]
    o.append(soft_steam(lpts, 2.5, 8, "#FFFFFF", 0.9, 306, glow_c="#E8B0A8"))
    o.append(soft_steam(rpts, 2.5, 8, "#FFFFFF", 0.9, 307, glow_c="#E8B0A8"))
    o.append(sparkle(300, 258, 7, "#FFFFFF", 0.95) + sparkle(370, 268, 5, "#FFFFFF", 0.85) + sparkle(232, 282, 5, "#FFFFFF", 0.85))
    # a sprig of lavender and two spoons on the cloth
    o.append(lavender(u, 500, 540, 100, 308, ang=-160, buds=9) + lavender(u, 508, 552, 90, 309, ang=-150, buds=8))
    for i, (x, y, r) in enumerate(((96, 532, -20), (128, 544, -10))):
        o.append(f'<g transform="rotate({r} {x} {y})"><path d="M {x - 50} {y} L {x + 10} {y}" stroke="#A8A49C" stroke-width="5" stroke-linecap="round"/>'
                 f'<ellipse cx="{x + 24}" cy="{y}" rx="16" ry="9" fill="#C8C4BC" stroke="{INK}" stroke-width="1.6"/>'
                 f'<ellipse cx="{x + 20}" cy="{y - 3}" rx="6" ry="2.4" fill="#FFFFFF" opacity="0.8"/></g>')
    # lettering
    o.append(ruled_c(u, 98, "ALL BECAUSE", JOST, 28, "#8A3A30", 310, ls=8, line_w=40, line="#B4554F"))
    t, _, _ = btext(u, 300, 166, "two people", SERIF_IT, 80, "#4E2A22", ["#6E3A2C", "#3A1E16"], 311, max_w=440, angle=-35, shadow="#FFF6EE", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 236, "fell in love", SERIF_IT, 80, "#A8343A", ["#C04A4A", "#86222A", "#D4645C"], 312, max_w=440, angle=-35, shadow="#FFF6EE", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ kindness is free
def mason_jar(u, cx, base, w, h, seed, water=True):
    """A small clear mason jar for flowers (drawn after the stems so they show through)."""
    x0, x1, top = cx - w / 2, cx + w / 2, base - h
    body = (f"M {_f(x0 + 6)} {_f(top + 12)} L {_f(x1 - 6)} {_f(top + 12)} Q {_f(x1)} {_f(top + 16)} {_f(x1)} {_f(top + 30)} L {_f(x1)} {_f(base - 10)} "
            f"Q {_f(x1)} {_f(base)} {_f(x1 - 10)} {_f(base)} L {_f(x0 + 10)} {_f(base)} Q {_f(x0)} {_f(base)} {_f(x0)} {_f(base - 10)} L {_f(x0)} {_f(top + 30)} "
            f"Q {_f(x0)} {_f(top + 16)} {_f(x0 + 6)} {_f(top + 12)} Z")
    o = [shadow(u, cx + 4, base, w * 0.62, 5, 0.3)]
    if water:
        o.append(f'<path d="M {_f(x0 + 2)} {_f(top + h * 0.45)} Q {_f(cx)} {_f(top + h * 0.45 + 4)} {_f(x1 - 2)} {_f(top + h * 0.45)} L {_f(x1 - 1)} {_f(base - 8)} '
                 f'Q {_f(x1 - 2)} {_f(base - 1)} {_f(x1 - 10)} {_f(base - 1)} L {_f(x0 + 10)} {_f(base - 1)} Q {_f(x0 + 2)} {_f(base - 1)} {_f(x0 + 1)} {_f(base - 8)} Z" fill="#A8C8D0" opacity="0.4"/>')
    o.append(f'<path d="{body}" fill="#E4F0F2" opacity="0.25"/>')
    o.append(f'<path d="M {_f(x0 + 7)} {_f(top + 34)} L {_f(x0 + 7)} {_f(base - 12)}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
             f'<path d="M {_f(x1 - 7)} {_f(top + 40)} L {_f(x1 - 7)} {_f(top + 60)}" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" opacity="0.6"/>')
    o.append(ink(body, "#3E5058", 2.0, seed, 1, 0.75))
    rim = org_rect(x0 + 4, top, x1 - 4, top + 13, seed + 1, 0.3, 0.3)
    o.append(f'<path d="{rim}" fill="#E4F0F2" opacity="0.5"/>' + ink(rim, "#3E5058", 1.8, seed + 1, 1, 0.75) +
             f'<path d="M {_f(x0 + 6)} {_f(top + 6)} L {_f(x1 - 6)} {_f(top + 6)}" stroke="#3E5058" stroke-width="1.2" opacity="0.4"/>')
    return "".join(o)


def bouquet_stems(pts_from, pts_to, seed, col=DEEP[1]):
    return "".join(ink(smooth_open([a, ((a[0] + b[0]) / 2 + 2, (a[1] + b[1]) / 2), b]), col, 2.6, seed + i, 1, 1) for i, (a, b) in enumerate(zip(pts_from, pts_to)))


@design("kindness-is-free")
def kindness_is_free():
    u = Ids("kindness-is-free")
    o = [bg(u, "#E2EAD8", ["#D8E2CC", "#ECF2E4", "#CCD8BE"], 321, fleck="#5E6E4A", angle=-20)]
    o.append(glow(u, 300, 300, 260, "#FFF8E8", 0.7))
    # grass at the bottom
    gd = smooth_closed([(-20, 548), (300, 540), (620, 548), (620, 640), (-20, 640)])
    o.append(form(u, gd, (-20, 536, 620, 640), "#9AB27A", "#6E8A50", "#C0D49C", 322, -4, n=100, shade=(0, -6), ink_w=1.6, ink_col="#4E6232"))
    o.append(grass(323, (-20, 540, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 140, (8, 22), 2.0))
    # the stand: legs, crate body, top board
    for x in (150, 450):
        o.append(f'<path d="{org_rect(x - 9, 470, x + 9, 576, 324 + x)}" fill="{WOOD[1]}" stroke="{INK}" stroke-width="1.8"/>')
    o.append(shadow(u, 300, 576, 200, 10, 0.3))
    top_board = org_rect(118, 368, 482, 386, 325, 0.5, 0.1)
    # jars of flowers on the top board
    # left jar: daisies
    o.append(bouquet_stems([(196, 360), (206, 360), (216, 360), (190, 360)], [(160, 250), (206, 236), (246, 262), (180, 296)], 326))
    o.append(daisy(u, 160, 250, 24, 327) + daisy(u, 206, 232, 26, 328) + daisy(u, 248, 262, 20, 329) + daisy(u, 178, 296, 18, 330))
    o.append(green_leaf(u, 196, 330, 34, 9, -150, 331) + green_leaf(u, 214, 326, 34, 9, -30, 332))
    o.append(mason_jar(u, 204, 370, 64, 92, 333))
    # middle: cosmos and lavender in a tall jar
    o.append(bouquet_stems([(296, 350), (304, 350), (300, 350)], [(268, 196), (334, 206), (300, 236)], 334))
    o.append(lavender(u, 292, 340, 170, 335, ang=-100, buds=10) + lavender(u, 310, 340, 156, 336, ang=-78, buds=9))
    o.append(cosmos(u, 266, 196, 26, 337, pal=ROSE) + cosmos(u, 336, 206, 24, 338, pal=BLUSH) + cosmos(u, 300, 238, 22, 339, pal=BERRY))
    o.append(mason_jar(u, 300, 370, 70, 118, 340))
    # right: roses and a bud
    o.append(bouquet_stems([(396, 360), (404, 360), (410, 360)], [(372, 270), (414, 248), (438, 290)], 341))
    o.append(green_leaf(u, 392, 320, 34, 10, -140, 342) + green_leaf(u, 414, 318, 34, 10, -40, 343))
    o.append(rose(u, 372, 270, 26, 344, pal=ROSE) + rose(u, 416, 246, 24, 345, pal=BLUSH) + peony_bud(u, 440, 290, 14, 346, pal=("#E88A9A", "#B04A62", "#FAC4CC")))
    o.append(mason_jar(u, 404, 370, 64, 92, 347))
    o.append(form(u, top_board, (118, 366, 482, 388), WOOD[0], WOOD[1], WOOD[2], 348, 0, n=60, shade=(0, -4), ink_w=2.0, length=(30, 80), width=(1, 2.4)))
    # crate front, painted cream, with the hand-lettered sign
    front = org_rect(130, 386, 470, 500, 349, 0.5, 0.03)
    planks = "".join(f'<path d="M 130 {y} L 470 {y + 0.6}" stroke="#B8A888" stroke-width="2.2" opacity="0.7"/>' for y in (424, 462))
    o.append(form(u, front, (130, 386, 470, 500), "#F6EEDC", "#D2C2A2", "#FFFFFF", 350, 0, n=120, shade=(0, -10), shade_op=0.35, ink_w=2.4,
                  length=(30, 90), width=(1.2, 3), extra_in=planks))
    for x in (144, 456):
        for y in (398, 488):
            o.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#6A5A48"/>')
    t, sz, w = btext(u, 300, 470, "IS FREE", BEBAS, 84, "#B4483E", ["#C85A4A", "#963226", "#D8705E"], 351, max_w=300, ls=6, angle=-80, shadow="#E2CCAE",
                     soff=(0.02, 0.03))
    o.append(t)
    # a few loose flowers and a little tag
    o.append(daisy(u, 140, 362, 12, 352, tilt=0.6) + blossom(u, 462, 360, 9, 353, pal=BLUSH))
    tag = soft_poly([(470, 392), (520, 400), (514, 436), (464, 428)], 354, 0.4, 0.12)
    o.append(f'<path d="M 470 390 Q 466 380 460 372" stroke="#A88050" stroke-width="2" fill="none"/>' +
             form(u, tag, (462, 390, 522, 438), "#D8B486", "#A88050", "#F2D6AC", 355, -10, n=14, shade=(2, 0), ink_w=1.6) +
             plain(492, 422, "take one", SERIF_IT, 17, "#5A3418", max_w=46, extra=' transform="rotate(8 492 418)"'))
    o.append(butterfly(u, 470, 236, 14, 361, pal=MUST, rot=16) + butterfly(u, 128, 320, 11, 362, pal=BLUE, rot=-12))
    # flowers in the grass
    o.append(daisy(u, 92, 560, 16, 356, tilt=0.8) + daisy(u, 520, 566, 15, 357, tilt=0.8) + cosmos(u, 546, 540, 18, 358, pal=ROSE) + cosmos(u, 66, 540, 16, 359, pal=BLUSH))
    # lettering
    t, _, _ = btext(u, 300, 152, "kindness", SERIF_IT, 118, "#3E5A3A", ["#56744E", "#2A3E28", "#6E8A60"], 360, max_w=470, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ be still
def cattail(u, x, base, h, seed, lean=0.0, col="#3E4A3E"):
    top = (x + lean * h, base - h)
    o = [ink(smooth_open([(x, base), (x + lean * h * 0.4, base - h * 0.5), top]), col, 2.6, seed, 1, 1)]
    hx, hy = x + lean * h * 0.8, base - h * 0.8
    o.append(f'<path d="{blob(hx, hy, 6, 18, seed, 0.05, 10, math.degrees(math.atan(lean)))}" fill="#6A4A34" stroke="#3A2418" stroke-width="1.4"/>')
    o.append(f'<path d="{blob(hx - 2, hy - 6, 1.6, 8, seed + 1, 0.05, 8)}" fill="#A8806A" opacity="0.6"/>')
    return "".join(o)


def reed(x, base, h, seed, col, lean):
    return ink(smooth_open([(x, base), (x + lean * h * 0.3, base - h * 0.5), (x + lean * h, base - h)]), col, 2.2, seed, 1, 0.9)


def heron(u, x, base, s, seed, flat=False):
    """A grey heron standing in the shallows, facing left: S-curved neck, dagger beak, crest plume, long legs."""
    X = lambda v: x + v * s
    Y = lambda v: base + v * s
    body = smooth_closed([(X(-14), Y(-62)), (X(6), Y(-74)), (X(30), Y(-70)), (X(46), Y(-54)), (X(56), Y(-40)), (X(34), Y(-42)), (X(8), Y(-44)), (X(-12), Y(-50))])
    neck = (f"M {_f(X(-10))} {_f(Y(-58))} C {_f(X(-26))} {_f(Y(-70))} {_f(X(-4))} {_f(Y(-88))} {_f(X(-14))} {_f(Y(-104))} "
            f"C {_f(X(-20))} {_f(Y(-114))} {_f(X(-10))} {_f(Y(-124))} {_f(X(0))} {_f(Y(-120))} C {_f(X(6))} {_f(Y(-114))} {_f(X(2))} {_f(Y(-104))} {_f(X(4))} {_f(Y(-96))} "
            f"C {_f(X(8))} {_f(Y(-84))} {_f(X(4))} {_f(Y(-70))} {_f(X(10))} {_f(Y(-62))} Z")
    if flat:
        return f'<path d="{body}" fill="#5E6A80"/><path d="{neck}" fill="#5E6A80"/><path d="M {_f(X(14))} {_f(Y(-44))} L {_f(X(12))} {_f(Y(0))} M {_f(X(24))} {_f(Y(-44))} L {_f(X(28))} {_f(Y(0))}" stroke="#5E6A80" stroke-width="2.4"/>'
    o = [f'<path d="M {_f(X(14))} {_f(Y(-44))} L {_f(X(12))} {_f(Y(0))} M {_f(X(24))} {_f(Y(-44))} L {_f(X(28))} {_f(Y(0))}" stroke="#4E4A50" stroke-width="2.6" stroke-linecap="round"/>']
    o.append(form(u, body, (X(-16), Y(-76), X(58), Y(-38)), "#9AA4B6", "#5E6A80", "#C8D0DC", seed, -10, n=30, shade=(0, 5), shade_op=0.5, ink_w=2.0, ink_col="#2E3A4E",
                  extra_in=f'<path d="M {_f(X(8))} {_f(Y(-62))} Q {_f(X(30))} {_f(Y(-58))} {_f(X(54))} {_f(Y(-42))}" stroke="#4E5A70" stroke-width="2.4" fill="none" opacity="0.7"/>'))
    o.append(form(u, neck, (X(-26), Y(-126), X(12), Y(-56)), "#E4E8EE", "#A8B0C0", "#FFFFFF", seed + 1, -90, n=16, shade=(3, 0), ink_w=2.0, ink_col="#2E3A4E",
                  extra_in=f'<path d="M {_f(X(-6))} {_f(Y(-96))} L {_f(X(-8))} {_f(Y(-70))}" stroke="#5E6A80" stroke-width="2" stroke-dasharray="3 4"/>'))
    o.append(f'<path d="M {_f(X(-14))} {_f(Y(-118))} L {_f(X(-44))} {_f(Y(-112))} L {_f(X(-14))} {_f(Y(-110))} Z" fill="#E2A83A" stroke="#6A4A10" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(ink(f"M {_f(X(-4))} {_f(Y(-121))} Q {_f(X(12))} {_f(Y(-124))} {_f(X(22))} {_f(Y(-116))}", "#2A2A36", 2.4, seed + 2, 1, 1))
    o.append(f'<path d="M {_f(X(-12))} {_f(Y(-121))} L {_f(X(2))} {_f(Y(-121))}" stroke="#2A2A36" stroke-width="3" stroke-linecap="round"/>'
             f'<circle cx="{_f(X(-8))}" cy="{_f(Y(-116))}" r="1.8" fill="#2A1A10"/>')
    return "".join(o)


@design("be-still")
def be_still():
    u = Ids("be-still")
    hz = 384
    o = [paper(u("pp"), "#EEE6DC", FLECK, 371, 1.0)]
    o.append(sky(u, [(0, "#A8BCD0"), (0.5, "#D8D6DA"), (0.85, "#F4DCC8"), (1, "#F8E2C8")], hz, 372, ["#C0D0DE", "#FFFFFF", "#F2D6C6"], 200))
    o.append(glow(u, 380, hz - 20, 260, "#FFEBCB", 0.85, 130))
    # far mountains in haze, then a mid ridge
    o.append(hill(u, [(-20, 300), (60, 268), (130, 290), (210, 252), (290, 286), (380, 300), (460, 272), (540, 236), (620, 262)], hz + 2, "#B8C2D4", "#A0AEC4", "#D4DCE6", 373, sop=(0.1, 0.25)))
    o.append(f'<path d="{blob(300, 300, 360, 26, 374, 0.1, 20)}" fill="#FFFFFF" opacity="0.35"/>')
    o.append(hill(u, [(-20, 340), (80, 318), (170, 334), (260, 344), (360, 352), (460, 330), (540, 314), (620, 324)], hz + 2, "#94A4BA", "#7E90A8", "#B4C2D2", 375, sop=(0.1, 0.25)))
    rnd = random.Random(376)
    trees = []
    for x in list(range(-10, 230, 8)) + list(range(420, 620, 8)):
        edge = 1.0 - (min(abs(x - 230), abs(x - 420)) < 40 and (230 < x < 420)) * 0.5
        h = rnd.uniform(16, 38) * (1.6 if x < 90 or x > 520 else 1)
        trees.append(conifer(x + rnd.uniform(-3, 3), hz + 2, h, "#5E7086", rnd.random(), width=0.36))
    o.append("".join(trees))
    o.append(f'<path d="M -20 {hz - 2} L 620 {hz - 2} L 620 {hz + 4} L -20 {hz + 4} Z" fill="#5E7086"/>')
    # mist lying on the water
    for i, (x, y, rx, ry, op) in enumerate(((140, hz - 4, 200, 16, 0.55), (470, hz - 2, 220, 14, 0.5), (300, hz + 6, 300, 12, 0.45))):
        o.append(f'<path d="{blob(x, y, rx, ry, 377 + i, 0.12, 18)}" fill="#FFFFFF" opacity="{op}"/>')
    # still water with a mirror image
    wg = u("wt")
    o.append(f'<defs>{lgrad(wg, [(0, "#F2DECC"), (0.35, "#C8CCD8"), (1, "#7E92AC")])}</defs><rect x="-10" y="{hz + 4}" width="620" height="{620 - hz}" fill="url(#{wg})"/>')
    o.append(f'<g transform="translate(0 {2 * hz + 8}) scale(1 -1)" opacity="0.28">{"".join(trees)}</g>')
    o.append(brush((-20, hz + 8, 620, 600), ["#FFFFFF", "#9AAAC0", "#F6E2CE"], 378, 160, 0, (30, 110), (1, 2.4), (0.25, 0.55), 0.03, 1))
    o.append(f'<path d="{blob(380, hz + 22, 70, 5, 379, 0.1, 12)}" fill="#FFF4E0" opacity="0.7"/>')
    # a lone canoe drifting, its reflection and soft ripples
    cx, cy = 352, 470
    hull = f"M {cx - 70} {cy - 8} Q {cx - 64} {cy + 8} {cx} {cy + 10} Q {cx + 64} {cy + 8} {cx + 72} {cy - 10} Q {cx} {cy - 2} {cx - 70} {cy - 8} Z"
    o.append(f'<path d="{hull}" fill="#8E3A2A" opacity="0.3" transform="translate(0 {2 * cy + 18}) scale(1 -1) translate(0 0)"/>')
    for k, (rx, op) in enumerate(((96, 0.6), (130, 0.4), (170, 0.25))):
        o.append(f'<ellipse cx="{cx}" cy="{cy + 12}" rx="{rx}" ry="{rx * 0.08:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="{op}"/>')
    o.append(form(u, hull, (cx - 72, cy - 12, cx + 72, cy + 12), "#C0563E", "#8E3A2A", "#E68A66", 380, 0, n=30, shade=(0, -4), ink_w=2.0))
    o.append(f'<path d="M {cx - 66} {cy - 7} Q {cx} {cy - 1} {cx + 68} {cy - 9}" stroke="#F2C49A" stroke-width="2.4" fill="none"/>'
             f'<path d="M {cx - 20} {cy - 4} L {cx - 20} {cy + 6} M {cx + 22} {cy - 4} L {cx + 22} {cy + 6}" stroke="#6A2A1E" stroke-width="2.4"/>')
    o.append(ink(f"M {cx - 30} {cy - 18} L {cx + 40} {cy + 4}", "#7A5A3A", 3, 381, 1, 1) + f'<path d="{blob(cx + 46, cy + 6, 10, 4, 382, 0.1, 8, 18)}" fill="#7A5A3A"/>')
    # a heron standing in the shallows, and reeds in front
    hx, hb = 134, 522
    o.append(heron(u, hx, hb, 1.0, 383))
    o.append(f'<g transform="translate(0 {2 * hb + 4}) scale(1 -1)" opacity="0.18">' + heron(u, hx, hb, 1.0, 383, flat=True) + "</g>")
    for k, rx in enumerate((22, 36)):
        o.append(f'<ellipse cx="{hx + 6}" cy="{hb + 2}" rx="{rx}" ry="{rx * 0.12:.1f}" fill="none" stroke="#FFFFFF" stroke-width="1.8" opacity="{0.6 - k * 0.25:.2f}"/>')
    for i, (x, h, l) in enumerate(((40, 120, 0.1), (56, 150, -0.05), (74, 100, 0.15), (520, 130, -0.1), (540, 160, 0.05), (562, 110, -0.2), (500, 90, 0.2))):
        o.append(reed(x, 612, h, 384 + i, "#4E5E4A", l))
    o.append(cattail(u, 64, 612, 140, 391, 0.06) + cattail(u, 548, 612, 150, 392, -0.05) + cattail(u, 530, 612, 120, 393, 0.1))
    # lettering
    t, _, _ = btext(u, 300, 190, "be still", SERIF_IT, 150, "#3A4A62", ["#4E607A", "#2A364A", "#5E708A"], 394, max_w=470, angle=-30,
                    shadow="#FFF6EC", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u, "#2A3040", 0.5))
    return "".join(o)


# ================================================================ one day at a time
def snail(u, cx, cy, s, seed):
    """A storybook snail heading left: soft body, eye stalks, a spiral shell with a daisy growing on top."""
    k = s / 100
    o = [shadow(u, cx - 10 * k, cy + 52 * k, 150 * k, 12 * k, 0.3)]
    X = lambda v: cx + v * k
    Y = lambda v: cy + v * k
    body = smooth_closed([(X(-150), Y(48)), (X(-150), Y(30)), (X(-130), Y(-10)), (X(-118), Y(-56)), (X(-96), Y(-74)), (X(-74), Y(-66)), (X(-70), Y(-30)),
                          (X(-40), Y(20)), (X(60), Y(28)), (X(120), Y(36)), (X(136), Y(50)), (X(40), Y(56))])
    o.append(form(u, body, (X(-152), Y(-76), X(140), Y(58)), "#E6D2B4", "#B49A78", "#FBEEDA", seed, -10, n=120, shade=(0, 8 * k), shade_op=0.45,
                  hi=(X(-110), Y(-40), 10 * k, 20 * k), hi_op=0.6, ink_w=2.4, length=(8, 24), width=(1, 2.4),
                  extra_in=dabs((X(-150), Y(-70), X(130), Y(56)), ["#C8A882", "#FFFFFF"], seed + 1, 40, (1, 2.4), (0.3, 0.6))))
    # eye stalks
    for i, (bx, by, ex, ey) in enumerate(((-108, -64, -126, -112), (-90, -68, -86, -118))):
        o.append(ink(f"M {_f(X(bx))} {_f(Y(by))} Q {_f(X((bx + ex) / 2 - 4))} {_f(Y((by + ey) / 2))} {_f(X(ex))} {_f(Y(ey))}", "#B49A78", 5 * k + 2, seed + i, 1, 1))
        o.append(f'<circle cx="{_f(X(ex))}" cy="{_f(Y(ey))}" r="{_f(8 * k)}" fill="#E6D2B4" stroke="{INK}" stroke-width="2"/>'
                 f'<circle cx="{_f(X(ex - 2))}" cy="{_f(Y(ey + 1))}" r="{_f(4.2 * k)}" fill="#2A1A10"/><circle cx="{_f(X(ex - 3.5))}" cy="{_f(Y(ey - 1))}" r="{_f(1.6 * k)}" fill="#FFFFFF"/>')
    o.append(ink(f"M {_f(X(-142))} {_f(Y(-4))} q {_f(8 * k)} {_f(9 * k)} {_f(18 * k)} {_f(2 * k)}", INK, 2.4, seed + 3, 1, 0.9))
    o.append(f'<ellipse cx="{_f(X(-120))}" cy="{_f(Y(8))}" rx="{_f(9 * k)}" ry="{_f(5 * k)}" fill="#F0907A" opacity="0.55"/>')
    # spiral shell
    sx, sy, R = X(10), Y(-50), 92 * k
    shell = blob(sx, sy, R, R * 0.94, seed + 4, 0.02, 20)
    spiral = []
    for i in range(160):
        t = i / 160 * 3.1 * 2 * math.pi
        r = R * 0.92 * (1 - i / 175)
        spiral.append((sx + math.cos(t + 2.2) * r * 0.96 + (1 - i / 160) * 4, sy + math.sin(t + 2.2) * r * 0.92))
    bands = ""
    for j, col in enumerate(("#E8B04A", "#CC6A44", "#F2D486")):
        bands += f'<path d="{smooth_open(spiral[j * 6::3])}" stroke="{col}" stroke-width="{10 * k + 3:.1f}" fill="none" opacity="0.35" stroke-linecap="round"/>'
    o.append(form(u, shell, (sx - R, sy - R, sx + R, sy + R), "#D8844E", "#9A4A26", "#F2B47A", seed + 5, lambda x, y: math.degrees(math.atan2(y - sy, x - sx)) + 90,
                  n=R * R / 12, shade=(R * 0.14, R * 0.16), shade_op=0.5, hi=(sx - R * 0.4, sy - R * 0.45, R * 0.24, R * 0.14), hi_op=0.5, ink_w=2.8,
                  length=(R * 0.1, R * 0.3), width=(1.2, 3), curve=0.4, extra_in=bands))
    o.append(ink(smooth_open(spiral[::2]), "#6A2E14", 3.2, seed + 6, 2, 0.85))
    # a little daisy growing on top of the shell
    o.append(ink(f"M {_f(sx + 6 * k)} {_f(sy - R + 6)} q {_f(-4 * k)} {_f(-24 * k)} {_f(6 * k)} {_f(-46 * k)}", DEEP[1], 3, seed + 7, 1, 1))
    o.append(green_leaf(u, sx + 4 * k, sy - R - 10 * k, 22 * k, 7 * k, -150, seed + 8, pal=LEAF))
    o.append(daisy(u, sx + 12 * k, sy - R - 50 * k, 20 * k, seed + 9))
    return "".join(o)


@design("one-day-at-a-time")
def one_day_at_a_time():
    u = Ids("one-day-at-a-time")
    o = [bg(u, "#F4ECD8", ["#EEE2CA", "#FAF4E6", "#E6D8BC"], 401, angle=-20)]
    o.append(glow(u, 300, 380, 280, "#FFF2D0", 0.6))
    # mossy ground with clover
    gd = smooth_closed([(-20, 474), (150, 462), (300, 468), (450, 458), (620, 470), (620, 640), (-20, 640)])
    o.append(form(u, gd, (-20, 456, 620, 640), "#A8B880", "#76884E", "#CAD6A2", 402, -4, n=160, shade=(0, -8), ink_w=1.8, ink_col="#4E6232",
                  extra_in=dabs((-20, 470, 620, 640), ["#8EA060", "#C8D49A", "#6E8048"], 403, 300, (1.5, 4), (0.3, 0.7))))
    o.append(grass(404, (-20, 462, 620, 520), ["#6E8A44", "#A8BC70"], 70, (6, 14), 1.8))
    # a glistening trail behind the snail
    o.append(f'<path d="M 470 548 Q 540 552 600 540" stroke="#FFFFFF" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.55"/>')
    for x, y, s in ((500, 546, 6), (556, 544, 5), (586, 538, 4)):
        o.append(sparkle(x, y - 10, s, "#FFFFFF", 0.9))
    # mushrooms on the left
    for i, (x, b, w, h, cap) in enumerate(((96, 520, 46, 54, TERRA), (140, 528, 30, 36, MUST), (66, 530, 24, 28, TERRA))):
        stem_d = smooth_closed([(x - w * 0.18, b), (x - w * 0.14, b - h * 0.7), (x + w * 0.14, b - h * 0.7), (x + w * 0.18, b)])
        o.append(form(u, stem_d, (x - w * 0.2, b - h * 0.7, x + w * 0.2, b), "#F4E8D2", "#C8B494", "#FFFFFF", 405 + i, -90, n=8, shade=(3, 0), ink_w=1.6))
        cd = f"M {_f(x - w / 2)} {_f(b - h * 0.62)} Q {_f(x - w / 2)} {_f(b - h * 1.05)} {_f(x)} {_f(b - h * 1.05)} Q {_f(x + w / 2)} {_f(b - h * 1.05)} {_f(x + w / 2)} {_f(b - h * 0.62)} Q {_f(x)} {_f(b - h * 0.52)} {_f(x - w / 2)} {_f(b - h * 0.62)} Z"
        spots = "".join(f'<circle cx="{_f(x + dx * w)}" cy="{_f(b - h * dy)}" r="{_f(w * 0.06)}" fill="#FFF6E6"/>' for dx, dy in ((-0.2, 0.86), (0.12, 0.94), (0.24, 0.76), (-0.02, 0.74)))
        o.append(form(u, cd, (x - w / 2, b - h * 1.05, x + w / 2, b - h * 0.52), cap[0], cap[1], cap[2], 408 + i, -60, n=12, shade=(w * 0.1, 2), ink_w=1.8, extra_in=spots))
    # clover leaves and a fallen leaf
    for i, (x, y, s) in enumerate(((210, 548, 10), (420, 560, 9), (480, 512, 8), (36, 556, 9), (260, 586, 8))):
        for a in (-90, 30, 150):
            ar = math.radians(a)
            o.append(f'<path d="{heart_path(x + math.cos(ar) * s * 0.7, y + math.sin(ar) * s * 0.7, s * 0.5)}" fill="{LEAF[0]}" stroke="{LEAF[1]}" stroke-width="1.2" '
                     f'transform="rotate({a + 90} {_f(x + math.cos(ar) * s * 0.7)} {_f(y + math.sin(ar) * s * 0.7)})"/>')
    o.append(snail(u, 318, 456, 100, 411))
    # a ladybug on a blade of grass
    o.append(green_leaf(u, 520, 520, 60, 12, -110, 412, pal=LEAF))
    lx, ly = 508, 478
    o.append(f'<g transform="rotate(-30 {lx} {ly})"><ellipse cx="{lx}" cy="{ly}" rx="10" ry="8" fill="#C8382E" stroke="{INK}" stroke-width="1.6"/>'
             f'<path d="M {lx} {ly - 8} L {lx} {ly + 8}" stroke="{INK}" stroke-width="1.4"/><circle cx="{lx - 10}" cy="{ly}" r="4.4" fill="{INK}"/>'
             f'<circle cx="{lx - 4}" cy="{ly - 3}" r="1.8" fill="{INK}"/><circle cx="{lx + 4}" cy="{ly + 3}" r="1.8" fill="{INK}"/><circle cx="{lx + 4}" cy="{ly - 4}" r="1.6" fill="{INK}"/>'
             f'<ellipse cx="{lx + 2}" cy="{ly - 4}" rx="3" ry="1.6" fill="#FFFFFF" opacity="0.6"/></g>')
    # lettering
    t, _, _ = btext(u, 300, 168, "ONE DAY", BEBAS, 140, "#C0603E", ["#D8784E", "#9A4026", "#E89A70"], 413, max_w=440, ls=6, angle=-80,
                    shadow="#4E2A1A", soff=(0.02, 0.035), hi="#F8C8A0")
    o.append(t)
    o.append(ruled_c(u, 228, "at a time", SERIF_IT, 56, "#4E3A22", 414, ls=0, line_w=48, gap=16, line="#C0603E"))
    o.append(finish(u))
    return "".join(o)


# ================================================================ thank you for being you
def tulip(u, x, y, s, seed, pal, rot=0):
    """A cupped tulip head (three overlapping petals) centred on (x, y)."""
    o = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    back = smooth_closed([(x - s * 0.55, y - s * 0.2), (x - s * 0.3, y - s * 0.95), (x, y - s * 0.6), (x + s * 0.3, y - s * 0.95), (x + s * 0.55, y - s * 0.2), (x + s * 0.4, y + s * 0.5), (x - s * 0.4, y + s * 0.5)])
    o.append(form(u, back, (x - s * 0.6, y - s, x + s * 0.6, y + s * 0.55), mixc(pal[0], pal[1], 0.4), pal[1], pal[0], seed, -90, n=s * 2, shade=None, ink_w=1.6, ink_col=pal[1]))
    for i, sg in enumerate((-1, 1)):
        pet = smooth_closed([(x, y + s * 0.5), (x + sg * s * 0.5, y + s * 0.2), (x + sg * s * 0.46, y - s * 0.5), (x + sg * s * 0.12, y - s * 0.86), (x - sg * s * 0.1, y - s * 0.3), (x - sg * s * 0.06, y + s * 0.3)])
        o.append(form(u, pet, (x - s * 0.6, y - s * 0.9, x + s * 0.6, y + s * 0.55), pal[0], pal[1], pal[2], seed + 1 + i, -90, n=s * 2.4, shade=(sg * s * 0.1, 0), shade_op=0.45,
                      ink_w=1.8, ink_col=pal[1], length=(s * 0.2, s * 0.6), width=(0.8, max(1.2, s * 0.06))))
    mid = smooth_closed([(x, y + s * 0.5), (x - s * 0.24, y), (x, y - s * 0.72), (x + s * 0.24, y)])
    o.append(form(u, mid, (x - s * 0.3, y - s * 0.75, x + s * 0.3, y + s * 0.5), pal[2], pal[0], "#FFFFFF", seed + 4, -90, n=s, shade=None, ink_w=1.4, ink_col=pal[1]))
    o.append("</g>")
    return "".join(o)


@design("thank-you-for-being-you")
def thank_you_for_being_you():
    u = Ids("thank-you-for-being-you")
    o = [bg(u, "#F8EACA", ["#F4E2BC", "#FCF4E0", "#F0D8AA"], 421, angle=-20)]
    o.append(glow(u, 300, 330, 250, "#FFF8E6", 0.7))
    rot = -8
    o.append(f'<g transform="translate(36 58) scale(0.88) rotate({rot} 300 340)">')
    # back of the kraft wrap
    back = smooth_closed([(160, 240), (236, 206), (300, 224), (372, 200), (446, 236), (330, 460), (300, 476), (272, 460)])
    o.append(form(u, back, (170, 186, 440, 486), "#B8925E", "#8A6A3E", "#D2AE7A", 422, -80, n=120, shade=None, ink_w=2.0))
    # stems & leaves
    for i, (tx, ty) in enumerate(((200, 214), (246, 166), (300, 140), (354, 166), (402, 210), (300, 220), (224, 250), (378, 250))):
        o.append(ink(smooth_open([(300, 440), ((300 + tx) / 2, (440 + ty) / 2 + 10), (tx, ty + 24)]), DEEP[1], 3, 423 + i, 1, 1))
    for i, (x, y, L, a, pal) in enumerate(((236, 300, 140, -132, DEEP), (364, 300, 140, -48, DEEP), (280, 284, 120, -104, LEAF), (322, 286, 116, -76, LEAF),
                                            (256, 280, 100, -150, LEAF), (346, 282, 100, -30, LEAF))):
        o.append(green_leaf(u, x, y, L, 17, a, 430 + i, pal=pal))
    # eucalyptus sprigs
    for i, (x0, y0, x1, y1) in enumerate(((250, 300, 146, 196), (352, 300, 458, 200), (300, 290, 300, 160))):
        o.append(ink(smooth_open([(x0, y0), ((x0 + x1) / 2 - 4, (y0 + y1) / 2 - 6), (x1, y1)]), SAGE[1], 2.2, 436 + i, 1, 1))
        for j in range(6):
            t = (j + 1) / 7
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - 6 * math.sin(math.pi * t)
            o.append(f'<path d="{blob(px + (7 if j % 2 else -7), py, 8, 7, 438 + i * 10 + j, 0.06, 10)}" fill="{SAGE[0]}" stroke="{SAGE[1]}" stroke-width="1.2"/>'
                     f'<path d="{blob(px + (7 if j % 2 else -7) - 2, py - 2, 3.4, 2.4, 460 + i * 10 + j, 0.06, 8)}" fill="{SAGE[2]}" opacity="0.8"/>')
    # tulips, daisies and baby's breath
    o.append(tulip(u, 200, 214, 40, 476, MUST, -30) + tulip(u, 402, 210, 40, 477, ROSE, 28))
    o.append(tulip(u, 246, 168, 48, 473, ROSE, -16) + tulip(u, 354, 168, 48, 474, BERRY, 16) + tulip(u, 300, 142, 52, 475, BLUSH, 0))
    o.append(daisy(u, 214, 262, 22, 470) + daisy(u, 388, 260, 21, 471) + daisy(u, 300, 230, 19, 472) + daisy(u, 262, 226, 15, 478) + daisy(u, 340, 228, 15, 479))
    rnd = random.Random(486)
    bb = []
    for _ in range(40):
        x, y = rnd.uniform(180, 420), rnd.uniform(180, 290)
        if abs(x - 300) < 140 - (y - 180) * 0.3:
            bb.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(2.2, 3.4):.1f}" fill="#FFFFFF" stroke="#C8BCA8" stroke-width="0.8"/>')
    o.append("".join(bb))
    # front of the wrap: two folded sheets of kraft paper
    f1 = smooth_closed([(170, 270), (250, 288), (300, 306), (314, 470), (292, 476)])
    f2 = smooth_closed([(434, 266), (352, 290), (300, 306), (286, 470), (310, 476)])
    o.append(form(u, f1, (176, 258, 318, 494), "#D4AE78", "#A8824E", "#ECCE9A", 478, -70, n=120, shade=(-10, 0), shade_op=0.4, ink_w=2.2,
                  extra_in='<path d="M 196 270 L 300 470 M 222 276 L 302 440" stroke="#A8824E" stroke-width="1.6" opacity="0.4"/>'))
    o.append(form(u, f2, (282, 254, 430, 494), "#E2BE88", "#B08A56", "#F6DCAA", 479, -110, n=120, shade=(10, 0), shade_op=0.35, ink_w=2.2,
                  extra_in='<path d="M 408 266 L 302 470" stroke="#B08A56" stroke-width="1.6" opacity="0.4"/>'))
    # twine bow and tag
    o.append(f'<path d="M 268 380 Q 300 392 334 378" stroke="#7A5A34" stroke-width="5" fill="none"/>')
    o.append(ink("M 300 386 q -30 -24 -40 -4 q 12 16 40 4 q 30 -24 40 -4 q -12 16 -40 4 M 300 386 q -10 30 -24 50 M 300 386 q 8 30 22 46", "#7A5A34", 3, 480, 1, 1))
    o.append("</g>")
    tag = soft_poly([(360, 448), (432, 436), (440, 482), (368, 494)], 481, 0.4, 0.14)
    o.append(ink("M 330 424 Q 350 440 366 460", "#7A5A34", 2, 482, 1, 1))
    o.append(form(u, tag, (358, 434, 442, 496), "#FBF3E4", "#D8C8AC", "#FFFFFF", 483, -10, n=16, shade=(2, 0), ink_w=1.8) +
             f'<circle cx="372" cy="464" r="4" fill="none" stroke="#7A5A34" stroke-width="2"/>' +
             f'<path d="{heart_path(408, 466, 10)}" fill="{BERRY[0]}" stroke="{BERRY[1]}" stroke-width="1.2" transform="rotate(-8 408 466)"/>')
    # lettering
    t, _, _ = btext(u, 300, 134, "thank you", SERIF_IT, 94, "#9A3A3A", ["#B44A48", "#7A2A2A", "#C8605A"], 484, max_w=460, angle=-35, shadow="#FFF8EC", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 540, "FOR BEING YOU", JOST, 32, "#5E3A2E", 485, ls=8, line_w=36, line="#9A3A3A"))
    o.append(finish(u))
    return "".join(o)


# ================================================================ you've got this
@design("youve-got-this")
def youve_got_this():
    u = Ids("youve-got-this")
    o = [bg(u, "#DCE8E0", ["#D2E0D6", "#E8F0EA", "#C6D6CC"], 501, fleck="#4A6A5A", angle=-20)]
    # sunburst behind the pot
    cx, cy = 300, 470
    rs = []
    for i in range(18):
        a0 = math.pi + math.pi * i / 18
        a1 = a0 + math.pi / 36
        rs.append(f"M {cx} {cy} L {_f(cx + math.cos(a0) * 700)} {_f(cy + math.sin(a0) * 700)} L {_f(cx + math.cos(a1) * 700)} {_f(cy + math.sin(a1) * 700)} Z")
    o.append(f'<path d="{" ".join(rs)}" fill="#F6E2A4" opacity="0.55"/>')
    o.append(glow(u, cx, cy - 40, 260, "#FFF2C8", 0.8))
    # little ground line
    o.append(shadow(u, 300, 548, 140, 12, 0.3))
    # the sprout: strong stem, two big leaves, a new leaf unfurling
    stem_d = smooth_open([(300, 446), (296, 408), (306, 360), (300, 314), (292, 290)])
    o.append(ink(stem_d, "#4E6A32", 9, 502, 1, 1) + ink(stem_d, "#8EAE5A", 4, 503, 1, 0.9))
    for i, (x, y, L, wd, a, pal) in enumerate(((300, 396, 132, 36, -160, LEAF), (304, 360, 130, 34, -22, DEEP), (296, 304, 62, 18, -128, LEAF))):
        d, tip = leaf_shape(x, y, L, wd, a, 504 + i)
        o.append(form(u, d, (min(x, tip[0]) - wd, min(y, tip[1]) - wd, max(x, tip[0]) + wd, max(y, tip[1]) + wd), pal[0], pal[1], pal[2], 505 + i, a, n=L * wd / 14,
                      shade=(0, wd * 0.3), shade_op=0.45, ink_w=2.4, ink_col="#34461E", length=(L * 0.15, L * 0.4), width=(1, 3),
                      hi=(x + (tip[0] - x) * 0.45, y + (tip[1] - y) * 0.45 - wd * 0.2, L * 0.16, wd * 0.18), hi_op=0.4))
        o.append(f'<path d="M {_f(x)} {_f(y)} Q {_f((x + tip[0]) / 2)} {_f((y + tip[1]) / 2 - wd * 0.15)} {_f(x + (tip[0] - x) * 0.9)} {_f(y + (tip[1] - y) * 0.9)}" stroke="#DCE8B0" stroke-width="2.6" fill="none" opacity="0.8"/>')
    # curled new leaf at the very top
    o.append(f'<path d="M 292 290 q -10 -24 8 -32 q 16 -4 14 12 q -2 10 -12 6" stroke="#4E6A32" stroke-width="5" fill="#9AB860" stroke-linecap="round"/>')
    # a ladybug climbing the big leaf
    lx, ly = 220, 372
    o.append(f'<g transform="rotate(-40 {lx} {ly})"><ellipse cx="{lx}" cy="{ly}" rx="12" ry="9.5" fill="#C8382E" stroke="{INK}" stroke-width="1.8"/>'
             f'<path d="M {lx} {ly - 9} L {lx} {ly + 9}" stroke="{INK}" stroke-width="1.6"/><circle cx="{lx - 12}" cy="{ly}" r="5" fill="{INK}"/>'
             f'<circle cx="{lx - 5}" cy="{ly - 4}" r="2.2" fill="{INK}"/><circle cx="{lx + 5}" cy="{ly + 3}" r="2.2" fill="{INK}"/><circle cx="{lx + 4}" cy="{ly - 5}" r="1.8" fill="{INK}"/>'
             f'<ellipse cx="{lx + 2}" cy="{ly - 5}" rx="3.6" ry="2" fill="#FFFFFF" opacity="0.6"/></g>')
    # the pot with soil
    o.append(f'<path d="{blob(300, 446, 66, 10, 510, 0.05, 14)}" fill="#5A3A24"/>')
    o.append(dabs((240, 438, 360, 452), ["#7A5034", "#3E2414"], 511, 30, (1.5, 3), (0.6, 0.9)))
    o.append(pot(u, 300, 548, 160, 112, 512, pal=TERRA))
    o.append(f'<g transform="rotate(-6 300 502)">' + painted_heart(u, 300, 504, 16, CREAM, 513) + "</g>")
    for x, y, s in ((180, 300, 10), (420, 280, 12), (448, 360, 7), (152, 390, 7), (376, 236, 6)):
        o.append(sparkle(x, y, s, "#E8A82A", 0.9))
    # lettering
    t, _, _ = btext(u, 300, 118, "you've", SERIF_IT, 78, "#3E5A48", ["#56745E", "#2A3E30"], 514, max_w=300, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 226, "GOT THIS", BEBAS, 120, "#C0603E", ["#D8784E", "#9A4026", "#E89A70"], 515, max_w=460, ls=8, angle=-80,
                    shadow="#3E2A1E", soff=(0.02, 0.035), hi="#F8C8A0")
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ make yourself at home
def sprig_wallpaper(u, seed, col, col2, box=(-10, -10, 610, 610), step=64):
    """Tiny painted sprigs scattered like a vintage wallpaper print."""
    rnd = random.Random(seed)
    o = []
    x0, y0, x1, y1 = box
    row = 0
    y = y0 + 20
    while y < y1:
        x = x0 + (step / 2 if row % 2 else 0)
        while x < x1:
            jx, jy = x + rnd.uniform(-5, 5), y + rnd.uniform(-5, 5)
            a = rnd.uniform(-40, 40)
            o.append(f'<g transform="rotate({a:.0f} {_f(jx)} {_f(jy)})"><path d="M {_f(jx)} {_f(jy + 9)} L {_f(jx)} {_f(jy - 7)}" stroke="{col}" stroke-width="1.6"/>'
                     f'<ellipse cx="{_f(jx - 4)}" cy="{_f(jy)}" rx="4" ry="2" fill="{col}" transform="rotate(-30 {_f(jx - 4)} {_f(jy)})"/>'
                     f'<ellipse cx="{_f(jx + 4)}" cy="{_f(jy - 3)}" rx="4" ry="2" fill="{col}" transform="rotate(30 {_f(jx + 4)} {_f(jy - 3)})"/>'
                     f'<circle cx="{_f(jx)}" cy="{_f(jy - 9)}" r="2.6" fill="{col2}"/></g>')
            x += step
        y += step * 0.8
        row += 1
    return "".join(o)


def knit(box, color, dx=9, dy=8, op=0.5, sw=1.6):
    x0, y0, x1, y1 = box
    d = []
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            d.append(f"M{_f(x)} {_f(y)}l{dx / 2:.1f} {dy:.1f}l{dx / 2:.1f} {-dy:.1f}")
            x += dx
        y += dy
    return f'<path d="{"".join(d)}" stroke="{color}" stroke-width="{sw}" fill="none" opacity="{op}"/>'


def sleeping_cat(u, cx, cy, s, seed, pal=("#E8A25A", "#B46A2E", "#F8CC8E")):
    """A cat curled up asleep, tail wrapped round, stripes and a pink ear."""
    k = s / 100
    X = lambda v: cx + v * k
    Y = lambda v: cy + v * k
    o = [shadow(u, cx, Y(30), 104 * k, 12 * k, 0.3)]
    body = smooth_closed([(X(-92), Y(20)), (X(-86), Y(-18)), (X(-40), Y(-44)), (X(20), Y(-46)), (X(74), Y(-26)), (X(96), Y(4)), (X(80), Y(30)), (X(0), Y(36)), (X(-70), Y(32))])
    stripes = "".join(f'<path d="M {_f(X(x))} {_f(Y(-46))} q {_f(6 * k)} {_f(30 * k)} {_f(-2 * k)} {_f(56 * k)}" stroke="{pal[1]}" stroke-width="{max(2.4, 7 * k):.1f}" fill="none" opacity="0.6" stroke-linecap="round"/>' for x in (-20, 8, 36, 62))
    o.append(form(u, body, (X(-96), Y(-48), X(98), Y(38)), pal[0], pal[1], pal[2], seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=110,
                  shade=(0, 10 * k), shade_op=0.45, hi=(X(10), Y(-30), 30 * k, 8 * k), hi_op=0.5, ink_w=2.4, length=(6, 16), width=(1, 2.2), extra_in=stripes))
    # tail wrapping round the front
    tail = f"M {_f(X(86))} {_f(Y(14))} Q {_f(X(60))} {_f(Y(44))} {_f(X(-10))} {_f(Y(40))} Q {_f(X(-60))} {_f(Y(38))} {_f(X(-74))} {_f(Y(26))}"
    o.append(f'<path d="{tail}" stroke="{INK}" stroke-width="{18 * k + 4:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>'
             f'<path d="{tail}" stroke="{pal[0]}" stroke-width="{18 * k:.1f}" fill="none" stroke-linecap="round"/>'
             f'<path d="M {_f(X(-60))} {_f(Y(36))} L {_f(X(-74))} {_f(Y(26))}" stroke="{pal[1]}" stroke-width="{18 * k:.1f}" stroke-linecap="round"/>')
    # head resting on the paws at the left
    hd = blob(X(-62), Y(-6), 36 * k, 30 * k, seed + 1, 0.04, 14)
    o.append(form(u, hd, (X(-100), Y(-40), X(-24), Y(26)), pal[0], pal[1], pal[2], seed + 2, -90, n=40, shade=(4 * k, 6 * k), shade_op=0.35, ink_w=2.2,
                  extra_in=f'<path d="M {_f(X(-64))} {_f(Y(-36))} l 0 {_f(12 * k)} M {_f(X(-54))} {_f(Y(-34))} l {_f(-2 * k)} {_f(12 * k)}" stroke="{pal[1]}" stroke-width="3" opacity="0.6"/>'))
    for sg, ex in ((-1, -84), (1, -46)):
        ear = poly_d([(X(ex - 12), Y(-24)), (X(ex - 2 + sg * 4), Y(-50)), (X(ex + 12), Y(-26))])
        o.append(f'<path d="{ear}" fill="{pal[0]}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                 f'<path d="{poly_d([(X(ex - 6), Y(-27)), (X(ex - 1 + sg * 3), Y(-42)), (X(ex + 6), Y(-28))])}" fill="#F2A0A0"/>')
    for ex in (-76, -50):
        o.append(ink(f"M {_f(X(ex - 7))} {_f(Y(-4))} q {_f(7 * k)} {_f(6 * k)} {_f(14 * k)} 0", INK, 2.2, seed + ex, 1, 1))
    o.append(f'<path d="{heart_path(X(-63), Y(4), 3.4 * k + 1)}" fill="#D87070"/>'
             f'<path d="M {_f(X(-90))} {_f(Y(6))} l {_f(-18 * k)} {_f(-3 * k)} M {_f(X(-90))} {_f(Y(10))} l {_f(-18 * k)} {_f(3 * k)} M {_f(X(-36))} {_f(Y(6))} l {_f(18 * k)} {_f(-3 * k)} M {_f(X(-36))} {_f(Y(10))} l {_f(18 * k)} {_f(3 * k)}" stroke="{INK}" stroke-width="1.2" opacity="0.6"/>')
    # paws in front of the face
    for px in (-70, -48):
        o.append(f'<path d="{blob(X(px), Y(24), 11 * k, 7 * k, seed + px, 0.05, 10)}" fill="{pal[2]}" stroke="{INK}" stroke-width="1.8"/>')
    o.append(f'<text x="{_f(X(-10))}" y="{_f(Y(-60))}" {SERIF_IT} font-size="{max(18, 26 * k):.0f}" fill="#7A5A44" opacity="0.8">z</text>'
             f'<text x="{_f(X(8))}" y="{_f(Y(-84))}" {SERIF_IT} font-size="{max(20, 34 * k):.0f}" fill="#7A5A44" opacity="0.8">z</text>')
    return "".join(o)


@design("make-yourself-at-home")
def make_yourself_at_home():
    u = Ids("make-yourself-at-home")
    o = [paper(u("pp"), "#D6E0E2", "#4A5A6A", 521, 1.0)]
    o.append(brush((-20, -20, 620, 470), ["#E2EAEC", "#C6D4D8", "#F0F4F4"], 522, 200, -80, (60, 160), (6, 14), (0.08, 0.2), 0.1))
    o.append(sprig_wallpaper(u, 523, "#9AB0B8", "#E8B8AC", (-10, -10, 610, 450), 70))
    o.append(glow(u, 140, 280, 220, "#FFE2A8", 0.7))
    # wooden floor
    fl = smooth_closed([(-20, 452), (300, 448), (620, 452), (620, 640), (-20, 640)])
    boards = "".join(f'<path d="M {x} 452 L {x * 1.6 - 180:.0f} 640" stroke="#6E4A2E" stroke-width="2" opacity="0.45"/>' for x in range(-60, 700, 70))
    o.append(form(u, fl, (-20, 444, 620, 640), "#B8885A", "#7E5432", "#D8AA78", 524, -2, n=200, shade=None, ink_w=0, length=(40, 120), width=(1.5, 4), extra_in=boards))
    o.append(f'<path d="{org_rect(-20, 438, 620, 454, 525, 0.4, 0.1)}" fill="#F4F0E8" stroke="{INK}" stroke-width="1.8"/>')
    # a braided round rug
    for i, (rx, ry, col) in enumerate(((258, 56, "#C86A54"), (232, 48, "#E8C69A"), (204, 41, "#8EA0B4"), (174, 34, "#E8A08A"), (142, 27, "#F4E6CC"), (108, 20, "#C86A54"), (70, 13, "#E8C69A"))):
        o.append(f'<ellipse cx="300" cy="530" rx="{rx}" ry="{ry}" fill="{col}"/>')
        o.append(f'<ellipse cx="300" cy="530" rx="{rx}" ry="{ry}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="5 4" opacity="0.4"/>')
    o.append(ink("M 42 530 A 258 56 0 0 0 558 530 A 258 56 0 0 0 42 530", "#5A3424", 2, 526, 1, 0.5))
    # side table with a lamp, books and a cup of tea
    o.append(shadow(u, 120, 500, 60, 8, 0.35))
    for x in (82, 158):
        o.append(f'<path d="{org_rect(x - 4, 388, x + 4, 498, 527 + x)}" fill="{DARKWOOD[1]}" stroke="{INK}" stroke-width="1.6"/>')
    tt = org_rect(70, 380, 170, 394, 528, 0.4, 0.3)
    o.append(form(u, tt, (70, 378, 170, 396), DARKWOOD[0], DARKWOOD[1], DARKWOOD[2], 529, 0, n=14, shade=(0, -3), ink_w=1.8))
    o.append(f'<path d="{org_rect(76, 440, 164, 448, 530, 0.3, 0.3)}" fill="{DARKWOOD[1]}" stroke="{INK}" stroke-width="1.4"/>')
    for i, (y, c, w) in enumerate(((432, "#8E5A6E", 70), (424, "#5E7A8E", 62))):
        o.append(f'<path d="{org_rect(120 - w / 2, y - 8, 120 + w / 2, y, 531 + i, 0.3, 0.2)}" fill="{c}" stroke="{INK}" stroke-width="1.4"/>'
                 f'<path d="M {120 - w / 2 + 6} {y - 4} l {w - 14} 0" stroke="#F4E6CC" stroke-width="1.4"/>')
    lamp_base = smooth_closed([(96, 380), (100, 356), (90, 340), (100, 322), (114, 322), (124, 340), (114, 356), (118, 380)])
    o.append(form(u, lamp_base, (88, 320, 126, 382), "#E6D2B4", "#B49A78", "#FBEEDA", 533, -90, n=10, shade=(5, 0), ink_w=1.8))
    o.append(f'<path d="M 107 322 L 107 298" stroke="#6A5A44" stroke-width="3"/>')
    o.append(glow(u, 107, 300, 130, "#FFD27A", 0.6))
    shade_d = soft_poly([(76, 304), (138, 304), (126, 246), (88, 246)], 534, 0.4, 0.1)
    o.append(form(u, shade_d, (76, 244, 138, 306), "#FFE6B0", "#E8B868", "#FFF8E0", 535, -90, n=20, shade=(6, 0), shade_op=0.3, ink_w=2.0,
                  extra_in='<path d="M 80 296 L 134 296" stroke="#E8A040" stroke-width="3" opacity="0.6"/>'))
    o.append(stoneware_mug(u, 150, 352, 30, 28, 536, BLUSH, side=1))
    o.append(soft_steam([(146, 348), (140, 334), (150, 322), (144, 306)], 1.6, 4, "#FFFFFF", 0.85, 537))
    # potted plant on the right
    o.append(pot(u, 508, 500, 74, 64, 538, pal=CREAM))
    for i, (a, L) in enumerate(((-120, 110), (-96, 130), (-70, 112), (-140, 80), (-46, 86), (-84, 70))):
        ar = math.radians(a)
        bx, by = 508, 440
        tx, ty = bx + math.cos(ar) * L, by + math.sin(ar) * L
        o.append(ink(f"M {bx} {by} Q {_f((bx + tx) / 2 + 6)} {_f((by + ty) / 2)} {_f(tx)} {_f(ty)}", DEEP[1], 2.4, 539 + i, 1, 1))
        o.append(green_leaf(u, tx - math.cos(ar) * 6, ty - math.sin(ar) * 6, 50, 20, a + (20 if a > -90 else -20), 545 + i, pal=DEEP if i % 2 else LEAF))
    # the armchair
    cx = 300
    o.append(shadow(u, cx + 10, 498, 160, 14, 0.4))
    for x in (206, 394):
        o.append(f'<path d="{soft_poly([(x - 7, 470), (x + 7, 470), (x + 4, 506), (x - 4, 506)], 550 + x, 0.3, 0.2)}" fill="{DARKWOOD[1]}" stroke="{INK}" stroke-width="1.6"/>')
    back = smooth_closed([(214, 420), (208, 300), (216, 248), (256, 224), (300, 218), (344, 224), (384, 248), (392, 300), (386, 420)])
    tufts = "".join(f'<path d="M {x} 236 Q {x + (x - 300) * 0.06:.0f} 320 {x} 400" stroke="{MUST[1]}" stroke-width="2.4" fill="none" opacity="0.55"/>' for x in (246, 274, 300, 326, 354))
    buttons = "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="{MUST[1]}"/>' for x in (260, 287, 313, 340) for y in (276, 330))
    o.append(form(u, back, (206, 216, 394, 422), MUST[0], MUST[1], MUST[2], 551, -90, n=260, shade=(16, 0), shade_op=0.45, hi=(256, 260, 22, 40), hi_op=0.4,
                  ink_w=2.6, length=(14, 40), width=(1.2, 3), extra_in=tufts + buttons))
    seat = smooth_closed([(214, 404), (300, 396), (386, 404), (392, 438), (300, 444), (208, 438)])
    o.append(form(u, seat, (206, 394, 394, 446), MUST[0], MUST[1], MUST[2], 552, 0, n=80, shade=(0, 8), shade_op=0.45, ink_w=2.4))
    skirt = soft_poly([(196, 436), (404, 436), (408, 476), (192, 476)], 553, 0.5, 0.12)
    o.append(form(u, skirt, (190, 434, 410, 478), "#D89A36", MUST[1], MUST[0], 554, 0, n=80, shade=(0, -6), ink_w=2.4,
                  extra_in='<path d="M 196 470 Q 300 476 404 470" stroke="#B47A1E" stroke-width="3" fill="none" opacity="0.5"/>'))
    for sg in (-1, 1):
        ax = cx + sg * 104
        arm = smooth_closed([(ax - 30, 476), (ax - 32, 352), (ax - 22, 326), (ax, 318), (ax + 22, 326), (ax + 32, 352), (ax + 30, 476)])
        o.append(form(u, arm, (ax - 34, 316, ax + 34, 478), MUST[0], MUST[1], MUST[2], 555 + sg, -90, n=90, shade=(sg * 10, 0), shade_op=0.45,
                      hi=(ax - 8, 336, 10, 8), hi_op=0.5, ink_w=2.4, extra_in=f'<path d="{blob(ax, 334, 18, 12, 557 + sg, 0.05, 12)}" fill="none" stroke="{MUST[1]}" stroke-width="2.4" opacity="0.6"/>'))
    # cushion with an embroidered heart
    cu = blob(250, 372, 40, 30, 558, 0.06, 14, rot=-10)
    o.append(form(u, cu, (208, 340, 292, 404), SAGE[0], SAGE[1], SAGE[2], 559, -20, n=40, shade=(6, 6), ink_w=2.2,
                  extra_in=f'<path d="{heart_path(250, 372, 10)}" fill="none" stroke="#B4554F" stroke-width="2.4" stroke-dasharray="3 2"/>'))
    # knitted throw over the right arm
    throw = smooth_closed([(352, 316), (394, 308), (428, 326), (436, 400), (430, 478), (404, 470), (396, 404), (368, 360), (344, 350)])
    o.append(form(u, throw, (342, 306, 438, 480), ROSE[0], ROSE[1], ROSE[2], 560, -90, n=60, shade=(8, 0), shade_op=0.45, ink_w=2.2,
                  extra_in=knit((340, 300, 440, 482), ROSE[1], 9, 8, 0.45, 1.8)))
    o.append("".join(f'<path d="M {x} {476 - (x - 404) * 0.3:.0f} l 0 12" stroke="{ROSE[1]}" stroke-width="2.4" stroke-linecap="round"/>' for x in range(406, 432, 5)))
    o.append(sleeping_cat(u, 318, 392, 72, 561, pal=("#9A9A9E", "#6A6A70", "#C8C8CC")))
    # lettering
    o.append(ruled_c(u, 98, "MAKE YOURSELF", JOST, 30, "#3E5A62", 562, ls=8, line_w=34, line="#B4554F"))
    t, _, _ = btext(u, 300, 190, "at home", SERIF_IT, 104, "#B4483E", ["#C85A4A", "#963226", "#D8705E"], 563, max_w=440, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ friends welcome, family always
def plank(u, x0, y0, x1, y1, seed, pal=DARKWOOD):
    rnd = random.Random(seed)
    d = org_rect(x0, y0, x1, y1, seed, 0.8, 0.04)
    h = y1 - y0
    grain_ = "".join(f'<path d="{wobble_line([(x0, y0 + h * t), ((x0 + x1) / 2, y0 + h * t + rnd.uniform(-4, 4)), (x1, y0 + h * t + rnd.uniform(-2, 2))], seed + k, 1.4)}" '
                     f'stroke="{pal[1]}" stroke-width="1.6" fill="none" opacity="0.45"/>' for k, t in enumerate((0.14, 0.3, 0.5, 0.7, 0.86)))
    knots = "".join(f'<ellipse cx="{_f(rnd.uniform(x0 + 30, x1 - 30))}" cy="{_f(y0 + h * rnd.uniform(0.2, 0.8))}" rx="9" ry="4" fill="none" stroke="{pal[1]}" stroke-width="1.6" opacity="0.6"/>' for _ in range(2))
    return (shadow(u, (x0 + x1) / 2 + 8, y1 + 6, (x1 - x0) * 0.52, 10, 0.3) +
            form(u, d, (x0, y0, x1, y1), pal[0], pal[1], pal[2], seed + 1, -2, n=(x1 - x0) * h / 40, shade=(0, h * 0.12), shade_op=0.45, length=(30, 90),
                 width=(1, 3), ink_w=2.6, extra_in=grain_ + knots +
                 f'<path d="M {x0 + 4} {y0 + 4} L {x1 - 4} {y0 + 4}" stroke="{pal[2]}" stroke-width="2.4" opacity="0.6"/>'))


@design("friends-welcome-family-always")
def friends_welcome_family_always():
    u = Ids("friends-welcome-family-always")
    o = [paper(u("pp"), "#E4E8DA", "#5E6E4A", 601, 1.0)]
    # whitewashed board-and-batten wall
    o.append(brush((-20, -20, 620, 620), ["#EEF0E6", "#D4DACA", "#F8F8F2"], 602, 240, -90, (60, 160), (4, 10), (0.12, 0.3), 0.05, 3))
    for x in range(30, 620, 90):
        o.append(f'<path d="{org_rect(x - 7, -10, x + 7, 610, 603 + x, 0.4, 0.02)}" fill="#F6F6EE"/><path d="M {x + 7} -10 L {x + 7} 610" stroke="#B8BEAA" stroke-width="2.4" opacity="0.7"/>')
    o.append(vignette(u, "#5E6A50", 0.3, 0.55))
    # nail, rope and two hanging planks
    o.append(f'<path d="M 300 76 L 150 150 M 300 76 L 450 150" stroke="#7A5A34" stroke-width="4" stroke-linecap="round"/>'
             f'<path d="M 300 76 L 150 150 M 300 76 L 450 150" stroke="#C8A070" stroke-width="2" stroke-linecap="round" stroke-dasharray="4 3"/>'
             f'<circle cx="300" cy="74" r="6" fill="#5A4A3A" stroke="{INK}" stroke-width="1.6"/><circle cx="298" cy="72" r="2" fill="#D8C8B0"/>')
    o.append(plank(u, 88, 140, 512, 312, 604))
    for x in (150, 450):
        o.append(f'<path d="M {x} 306 L {x} 346" stroke="#7A5A34" stroke-width="4"/><path d="M {x} 306 L {x} 346" stroke="#C8A070" stroke-width="2" stroke-dasharray="4 3"/>'
                 f'<circle cx="{x}" cy="306" r="5" fill="none" stroke="#5A4A3A" stroke-width="2.4"/><circle cx="{x}" cy="346" r="5" fill="none" stroke="#5A4A3A" stroke-width="2.4"/>')
    o.append(plank(u, 88, 340, 512, 500, 605, pal=("#9A6A42", "#64422A", "#C49268")))
    # painted lettering on the wood
    t, _, _ = btext(u, 300, 248, "friends", SERIF_IT, 92, "#FBF3E4", ["#FFFFFF", "#E8DCC8"], 606, max_w=380, angle=-30, shadow="#3A2014", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 292, "WELCOME", JOST, 30, "#F2C870", 607, ls=12, line_w=46, gap=16, line="#F2C870"))
    t, _, _ = btext(u, 300, 428, "family", SERIF_IT, 92, "#FBF3E4", ["#FFFFFF", "#E8DCC8"], 608, max_w=380, angle=-30, shadow="#3A2014", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 476, "ALWAYS", JOST, 30, "#F2C870", 609, ls=12, line_w=46, gap=16, line="#F2C870"))
    # a garland of greenery and roses draped across the top plank
    gl = [(80, 136), (150, 150), (220, 144), (300, 152), (380, 144), (450, 150), (520, 136)]
    o.append(ink(smooth_open(gl), DEEP[1], 3, 610, 1, 1))
    rnd = random.Random(611)
    for i in range(26):
        t = i / 25
        j = min(int(t * 6), 5)
        tt = t * 6 - j
        x = gl[j][0] + (gl[j + 1][0] - gl[j][0]) * tt
        y = gl[j][1] + (gl[j + 1][1] - gl[j][1]) * tt
        a = rnd.choice((-150, -30, -120, -60, 160, 20))
        o.append(green_leaf(u, x, y, rnd.uniform(18, 26), 7, a, 612 + i, pal=rnd.choice((DEEP, LEAF, SAGE)), vein=False))
    for i, (x, y, r, pal) in enumerate(((100, 142, 15, BLUSH), (196, 150, 13, ROSE), (300, 154, 16, BLUSH), (404, 150, 13, ROSE), (500, 142, 15, BLUSH))):
        o.append(rose(u, x, y, r, 640 + i, pal=pal))
    for x, y in ((150, 146), (250, 152), (350, 152), (452, 146)):
        o.append(flower_cluster(u, x, y, 650 + x, r=4, pal=CREAM, n=3, spread=8, kind="dot"))
    # trailing ivy from the lower plank
    for i, (x, sg) in enumerate(((104, -1), (496, 1))):
        pts = [(x, 496), (x + sg * 6, 524), (x - sg * 2, 550), (x + sg * 6, 574)]
        o.append(ink(smooth_open(pts), DEEP[1], 2, 660 + i, 1, 1))
        for k, (px, py) in enumerate(pts[1:]):
            o.append(green_leaf(u, px, py, 18, 7, 90 + sg * 40 - k * 20 * sg, 662 + i * 5 + k, pal=LEAF, vein=False))
    o.append(songbird(u, 474, 116, 13, 670, pal=BLUE, flip=True))
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ the best things in life are the people we love
def fabric(u, x0, y0, x1, y1, kind, base, accent, seed):
    """One quilt patch: a painted fabric square with a printed pattern."""
    d = org_rect(x0, y0, x1, y1, seed, 0.6, 0.02)
    w, h = x1 - x0, y1 - y0
    rnd = random.Random(seed)
    if kind == "gingham":
        gid, gdef = gingham(u, accent, base, 20, 0, 0.45)
        pat = gdef + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{gid})"/>'
    elif kind == "dots":
        pat = "".join(f'<circle cx="{x0 + 10 + i * 22 + (11 if j % 2 else 0)}" cy="{y0 + 10 + j * 20}" r="4" fill="{accent}" opacity="0.8"/>' for i in range(int(w / 22) + 1) for j in range(int(h / 20) + 1))
    elif kind == "stripes":
        pat = stripes_fill((x0, y0, x1, y1), accent, 7, 18, 0, 0.55)
    elif kind == "floral":
        pat = "".join(f'<circle cx="{_f(x0 + rnd.uniform(0, w))}" cy="{_f(y0 + rnd.uniform(0, h))}" r="4.5" fill="{accent}"/>' for _ in range(int(w * h / 500)))
        pat += "".join(f'<ellipse cx="{_f(x0 + rnd.uniform(0, w))}" cy="{_f(y0 + rnd.uniform(0, h))}" rx="5" ry="2.4" fill="#7E9450" opacity="0.7" transform="rotate({rnd.uniform(0, 180):.0f} {x0 + w / 2} {y0 + h / 2})"/>' for _ in range(int(w * h / 600)))
    elif kind == "heart":
        pat = painted_heart(u, (x0 + x1) / 2, (y0 + y1) / 2 + 4, min(w, h) * 0.22, (accent, mixc(accent, "#000000", 0.3), mixc(accent, "#FFFFFF", 0.4)), seed + 3)
        pat += f'<path d="{heart_path((x0 + x1) / 2, (y0 + y1) / 2 + 4, min(w, h) * 0.28)}" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="4 3"/>'
    else:
        pat = ""
    return form(u, d, (x0, y0, x1, y1), base, mixc(base, "#000000", 0.15), mixc(base, "#FFFFFF", 0.4), seed, -45, n=w * h / 140, shade=None, ink_w=0,
                length=(12, 30), width=(1.5, 4), sop=(0.08, 0.2), extra_in=pat)


@design("the-best-things-in-life-are-the-people-we-love")
def best_things_in_life():
    u = Ids("the-best-things-in-life-are-the-people-we-love")
    o = [paper(u("pp"), PAPER, FLECK, 701, 1.0)]
    kinds = [("gingham", "#FBEDE4", "#D07A74"), ("floral", "#DCE6EE", "#E88A9A"), ("dots", "#F4E2B8", "#C8843A"), ("heart", "#EEF0E2", "#C8464A"),
             ("stripes", "#F8E6DC", "#9EAE88"), ("dots", "#E8EEE0", "#7E9450"), ("floral", "#F8E8D0", "#86A4BE"), ("gingham", "#EEF2F4", "#86A4BE"),
             ("stripes", "#EAF0F2", "#E8A08A"), ("heart", "#FBEDE4", "#86A4BE")]
    rnd = random.Random(702)
    cells = []
    S = 130
    k = 0
    for j in range(5):
        for i in range(5):
            x0, y0 = -25 + i * S, -25 + j * S
            kind, base, acc = kinds[(i * 3 + j * 7 + k) % len(kinds)]
            cells.append(fabric(u, x0, y0, x0 + S, y0 + S, kind, base, acc, 703 + i * 10 + j))
    o.append("".join(cells))
    # seams and running stitches
    seams = "".join(f'<path d="M {-25 + i * S} -10 L {-25 + i * S} 610" stroke="#8A6A4A" stroke-width="2" opacity="0.5"/>'
                    f'<path d="M -10 {-25 + i * S} L 610 {-25 + i * S}" stroke="#8A6A4A" stroke-width="2" opacity="0.5"/>' for i in range(1, 5))
    stitches = "".join(f'<path d="M {-25 + i * S + 7} -10 L {-25 + i * S + 7} 610 M {-25 + i * S - 7} -10 L {-25 + i * S - 7} 610 '
                       f'M -10 {-25 + i * S + 7} L 610 {-25 + i * S + 7} M -10 {-25 + i * S - 7} L 610 {-25 + i * S - 7}" '
                       f'stroke="#FFFFFF" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>' for i in range(1, 5))
    o.append(seams + stitches)
    o.append(brush((-20, -20, 620, 620), ["#FFFFFF", "#8A6A4A"], 704, 160, -45, (30, 80), (2, 5), (0.04, 0.1), 0.2))
    # the appliqued centre panel, scalloped and stitched down
    pts = []
    x0, y0, x1, y1 = 96, 128, 504, 478
    for i in range(14):
        pts += [(x0 + (x1 - x0) * i / 14, y0), (x0 + (x1 - x0) * (i + 0.5) / 14, y0 - 7)]
    for i in range(12):
        pts += [(x1, y0 + (y1 - y0) * i / 12), (x1 + 7, y0 + (y1 - y0) * (i + 0.5) / 12)]
    for i in range(14):
        pts += [(x1 - (x1 - x0) * i / 14, y1), (x1 - (x1 - x0) * (i + 0.5) / 14, y1 + 7)]
    for i in range(12):
        pts += [(x0, y1 - (y1 - y0) * i / 12), (x0 - 7, y1 - (y1 - y0) * (i + 0.5) / 12)]
    panel = smooth_closed(pts)
    o.append(f'<path d="{panel}" fill="#3A2418" opacity="0.25" transform="translate(6 8)"/>')
    o.append(form(u, panel, (x0 - 8, y0 - 8, x1 + 8, y1 + 8), "#FBF5EA", "#E2D4BC", "#FFFFFF", 705, -10, n=200, shade=(0, -8), shade_op=0.25, ink_w=2.2, ink_col="#8A6A4A",
                  sop=(0.08, 0.2), extra_in=f'<rect x="{x0 + 14}" y="{y0 + 14}" width="{x1 - x0 - 28}" height="{y1 - y0 - 28}" rx="10" fill="none" stroke="#C8464A" stroke-width="2.4" stroke-dasharray="7 5" opacity="0.8"/>'))
    # lettering
    t, _, _ = btext(u, 300, 206, "the best things in life", SERIF_IT, 52, "#4E2A22", ["#6E3A2C", "#3A1E16"], 706, max_w=360, angle=-35)
    o.append(t)
    o.append(ruled_c(u, 250, "ARE THE", JOST, 26, "#7A5A44", 707, ls=8, line_w=44, gap=14, line="#C8464A"))
    t, _, _ = btext(u, 300, 362, "PEOPLE", BEBAS, 124, "#C0463E", ["#D45A4A", "#962E28", "#E07A64"], 708, max_w=350, ls=8, angle=-80, shadow="#E8D2BE", soff=(0.02, 0.03))
    o.append(t)
    t, _, _ = btext(u, 300, 430, "we love", SERIF_IT, 66, "#4E2A22", ["#6E3A2C", "#3A1E16"], 709, max_w=340, angle=-35)
    o.append(t)
    o.append(f'<g transform="rotate(-8 450 410)">' + painted_heart(u, 450, 412, 11, BERRY, 710) + "</g>")
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ grandpa's workshop
def hammer(u, x, y, s, seed, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    hd = soft_poly([(x - 34 * s, y - 10 * s), (x + 26 * s, y - 12 * s), (x + 30 * s, y + 8 * s), (x - 34 * s, y + 6 * s)], seed, 0.4, 0.15)
    o.append(f'<path d="{org_rect(x - 6 * s, y + 4 * s, x + 6 * s, y + 120 * s, seed + 1, 0.4, 0.3)}" fill="{WOOD[0]}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M {_f(x - 2 * s)} {_f(y + 12 * s)} L {_f(x - 2 * s)} {_f(y + 116 * s)}" stroke="{WOOD[2]}" stroke-width="2"/>')
    o.append(form(u, hd, (x - 36 * s, y - 14 * s, x + 32 * s, y + 10 * s), "#8E98A4", "#5A6270", "#C8D0D8", seed + 2, 0, n=14, shade=(0, 4), ink_w=2.2,
                  extra_in=f'<path d="M {_f(x + 26 * s)} {_f(y - 12 * s)} Q {_f(x + 40 * s)} {_f(y - 20 * s)} {_f(x + 44 * s)} {_f(y - 6 * s)}" stroke="#5A6270" stroke-width="5" fill="none"/>'))
    o.append(f'<path d="M {_f(x + 26 * s)} {_f(y - 12 * s)} Q {_f(x + 42 * s)} {_f(y - 22 * s)} {_f(x + 48 * s)} {_f(y - 4 * s)} L {_f(x + 40 * s)} {_f(y - 4 * s)} Q {_f(x + 36 * s)} {_f(y - 12 * s)} {_f(x + 28 * s)} {_f(y - 4 * s)} Z" fill="#7A8490" stroke="{INK}" stroke-width="2"/>')
    o.append("</g>")
    return "".join(o)


def saw(u, x, y, s, seed, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    blade = poly_d([(x - 20 * s, y), (x + 20 * s, y), (x + 14 * s, y + 160 * s), (x - 2 * s, y + 160 * s)])
    teeth = "".join(f'<path d="M {_f(x - 20 * s + i * 1.15 * s - (i * 0.11 * s))} {_f(y + i * 8 * s)} l {-5 * s:.1f} {4 * s:.1f} l {4.6 * s:.1f} {4 * s:.1f}" fill="none" stroke="{INK}" stroke-width="1.4"/>' for i in range(20))
    o.append(form(u, blade, (x - 22 * s, y, x + 22 * s, y + 160 * s), "#B8C0C8", "#7A848E", "#E8EEF2", seed, -90, n=30, shade=(6, 0), ink_w=2.0,
                  extra_in=f'<path d="M {_f(x + 6 * s)} {_f(y + 10 * s)} L {_f(x + 4 * s)} {_f(y + 150 * s)}" stroke="#FFFFFF" stroke-width="3" opacity="0.6"/>'))
    o.append(teeth)
    hd = smooth_closed([(x - 26 * s, y + 10 * s), (x - 30 * s, y - 40 * s), (x, y - 56 * s), (x + 30 * s, y - 40 * s), (x + 26 * s, y + 10 * s)])
    o.append(form(u, hd, (x - 32 * s, y - 58 * s, x + 32 * s, y + 12 * s), WOOD[0], WOOD[1], WOOD[2], seed + 1, -90, n=20, shade=(5, 0), ink_w=2.2,
                  extra_in=f'<path d="{blob(x, y - 26 * s, 13 * s, 9 * s, seed + 2, 0.05, 10)}" fill="#5A3A24"/>'))
    for dy in (-6, 2):
        o.append(f'<circle cx="{_f(x + 14 * s)}" cy="{_f(y + dy * s)}" r="2.4" fill="#C8B070" stroke="{INK}" stroke-width="1"/>')
    o.append("</g>")
    return "".join(o)


def wrench(u, x, y, s, seed, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    d = (f"M {_f(x - 6 * s)} {_f(y)} L {_f(x - 7 * s)} {_f(y + 110 * s)} L {_f(x + 7 * s)} {_f(y + 110 * s)} L {_f(x + 6 * s)} {_f(y)} Z")
    o.append(form(u, d, (x - 8 * s, y, x + 8 * s, y + 110 * s), "#9AA4AE", "#5A6270", "#D8DEE4", seed, -90, n=10, shade=(3, 0), ink_w=2.0))
    for yy, open_up in ((y - 8 * s, True), (y + 118 * s, False)):
        jaw = blob(x, yy, 15 * s, 14 * s, seed + int(yy), 0.03, 14)
        o.append(form(u, jaw, (x - 16 * s, yy - 15 * s, x + 16 * s, yy + 15 * s), "#9AA4AE", "#5A6270", "#D8DEE4", seed + 3, -40, n=10, shade=(3, 2), ink_w=2.0))
        o.append(f'<path d="M {_f(x - 6 * s)} {_f(yy + (-16 if open_up else 16) * s)} L {_f(x - 5 * s)} {_f(yy)} L {_f(x + 5 * s)} {_f(yy)} L {_f(x + 6 * s)} {_f(yy + (-16 if open_up else 16) * s)} Z" fill="#C8A274"/>')
    o.append("</g>")
    return "".join(o)


def screwdriver(u, x, y, s, seed, col=BERRY, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    o.append(f'<path d="M {_f(x)} {_f(y + 40 * s)} L {_f(x)} {_f(y + 110 * s)}" stroke="#7A848E" stroke-width="{5 * s:.1f}"/><path d="M {_f(x - 1)} {_f(y + 40 * s)} L {_f(x - 1)} {_f(y + 104 * s)}" stroke="#E8EEF2" stroke-width="1.4"/>'
             f'<path d="M {_f(x - 3 * s)} {_f(y + 110 * s)} L {_f(x + 3 * s)} {_f(y + 110 * s)} L {_f(x + 1)} {_f(y + 118 * s)} L {_f(x - 1)} {_f(y + 118 * s)} Z" fill="#5A6270"/>')
    hd = smooth_closed([(x - 9 * s, y + 42 * s), (x - 10 * s, y + 6 * s), (x, y - 2 * s), (x + 10 * s, y + 6 * s), (x + 9 * s, y + 42 * s)])
    o.append(form(u, hd, (x - 11 * s, y - 3 * s, x + 11 * s, y + 43 * s), col[0], col[1], col[2], seed, -90, n=10, shade=(3, 0), ink_w=2.0,
                  extra_in=f'<path d="M {_f(x - 3 * s)} {_f(y + 8 * s)} L {_f(x - 3 * s)} {_f(y + 36 * s)} M {_f(x + 3 * s)} {_f(y + 8 * s)} L {_f(x + 3 * s)} {_f(y + 36 * s)}" stroke="{col[1]}" stroke-width="1.6"/>'))
    o.append("</g>")
    return "".join(o)


def peg(x, y):
    return f'<path d="M {x} {y} l 0 -12" stroke="#7A848E" stroke-width="3.4" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="2.6" fill="#5A6270"/>'


@design("grandpas-workshop")
def grandpas_workshop():
    u = Ids("grandpas-workshop")
    o = [paper(u("pp"), "#C8A274", "#5A3A20", 801, 1.2)]
    o.append(brush((-20, -20, 620, 620), ["#D4B084", "#B88E60", "#DCBA90"], 802, 220, -4, (60, 160), (4, 12), (0.1, 0.25), 0.05, 3))
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="3.4" fill="#6E4A2A" opacity="0.75"/><circle cx="{x + 0.8}" cy="{y + 1}" r="2" fill="#3A2418" opacity="0.6"/>'
                    for x in range(15, 600, 30) for y in range(15, 600, 30))
    o.append(holes)
    o.append(vignette(u, "#3A2418", 0.45, 0.55))
    o.append(glow(u, 300, 320, 260, "#FFE6B8", 0.35))
    # the sign
    for x in (150, 450):
        o.append(peg(x, 96))
    o.append(plank(u, 84, 92, 516, 236, 803, pal=DARKWOOD))
    t, _, _ = btext(u, 300, 156, "Grandpa's", SERIF_IT, 70, "#FBF3E4", ["#FFFFFF", "#E8DCC8"], 804, max_w=380, angle=-30, shadow="#2A160C", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 220, "WORKSHOP", BEBAS, 76, "#F2C25A", ["#F8D888", "#D49A2A", "#FFE8A8"], 805, max_w=380, ls=10, angle=-80, shadow="#2A160C", soff=(0.02, 0.03))
    o.append(t)
    # tools hanging on the pegboard
    for x, y in ((120, 270), (205, 270), (300, 270), (348, 270), (420, 270), (488, 270)):
        o.append(peg(x, y))
    o.append(saw(u, 120, 300, 0.8, 806, rot=0))
    o.append(hammer(u, 205, 290, 0.9, 807, rot=0))
    o.append(wrench(u, 300, 290, 0.9, 808))
    o.append(screwdriver(u, 348, 278, 1.0, 809, col=BERRY) + screwdriver(u, 374, 278, 0.9, 810, col=MUST))
    # a coil of rope / tape measure
    o.append(f'<circle cx="452" cy="318" r="34" fill="{MUST[0]}" stroke="{INK}" stroke-width="2.4"/><circle cx="452" cy="318" r="22" fill="none" stroke="{MUST[1]}" stroke-width="3"/>'
             f'<circle cx="452" cy="318" r="8" fill="#5A4A3A"/><path d="M 486 324 L 512 326 L 512 336 L 484 334 Z" fill="#F2E2A4" stroke="{INK}" stroke-width="1.6"/>'
             f'<path d="M 440 296 q 8 -6 20 -2" stroke="#FFF2C0" stroke-width="3" fill="none" opacity="0.8"/>')
    o.append(peg(452, 278) + f'<path d="M 452 278 L 452 284" stroke="{INK}" stroke-width="2"/>')
    # workbench
    bench = smooth_closed([(-20, 432), (300, 428), (620, 432), (620, 640), (-20, 640)])
    o.append(shadow(u, 300, 432, 340, 14, 0.4))
    o.append(form(u, bench, (-20, 426, 620, 640), "#B07A4A", "#7A4A26", "#D29E6A", 811, -2, n=240, shade=None, ink_w=2.4, length=(40, 140), width=(1.5, 4),
                  extra_in='<path d="M -20 446 Q 300 442 620 446" stroke="#E2B888" stroke-width="3" fill="none" opacity="0.7"/>'
                           '<path d="M -20 508 Q 300 512 620 508" stroke="#5A3420" stroke-width="2.4" fill="none" opacity="0.5"/>'))
    # a little birdhouse being built
    bx, bb = 250, 492
    bw = smooth_closed([(bx - 46, bb), (bx - 46, bb - 74), (bx, bb - 114), (bx + 46, bb - 74), (bx + 46, bb)])
    bw = soft_poly([(bx - 46, bb), (bx - 46, bb - 74), (bx, bb - 112), (bx + 46, bb - 74), (bx + 46, bb)], 812, 0.4, 0.05)
    o.append(form(u, bw, (bx - 48, bb - 114, bx + 48, bb), BLUE[0], BLUE[1], BLUE[2], 813, -90, n=50, shade=(10, 0), ink_w=2.2,
                  extra_in=f'<circle cx="{bx}" cy="{bb - 64}" r="15" fill="#3A2418"/><circle cx="{bx}" cy="{bb - 34}" r="5" fill="{WOOD[0]}" stroke="{INK}" stroke-width="1.6"/><circle cx="{bx - 1.5}" cy="{bb - 35.5}" r="1.6" fill="{WOOD[2]}"/>'))
    roof = soft_poly([(bx - 60, bb - 70), (bx, bb - 124), (bx + 60, bb - 70), (bx + 52, bb - 62), (bx, bb - 110), (bx - 52, bb - 62)], 814, 0.4, 0.05)
    o.append(form(u, roof, (bx - 62, bb - 126, bx + 62, bb - 60), TERRA[0], TERRA[1], TERRA[2], 815, 40, n=30, shade=(0, -3), ink_w=2.2))
    # paint can with brush, pencil, shavings and a mug
    px, pb = 378, 494
    can = org_rect(px - 30, pb - 56, px + 30, pb, 816, 0.4, 0.1)
    o.append(form(u, can, (px - 30, pb - 56, px + 30, pb), "#C8CCD0", "#8A9098", "#EEF0F2", 817, -90, n=20, shade=(8, 0), ink_w=2.2,
                  extra_in=f'<path d="{org_rect(px - 30, pb - 40, px + 30, pb - 16, 818, 0.3, 0.1)}" fill="{BLUE[0]}"/>'))
    o.append(f'<ellipse cx="{px}" cy="{pb - 56}" rx="30" ry="7" fill="{BLUE[1]}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M {px - 30} {pb - 56} q 4 14 2 22" stroke="{BLUE[0]}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    o.append(f'<g transform="rotate(24 {px + 6} {pb - 70})"><path d="{org_rect(px + 1, pb - 130, px + 11, pb - 70, 819, 0.3, 0.3)}" fill="{WOOD[0]}" stroke="{INK}" stroke-width="1.8"/>'
             f'<path d="{org_rect(px - 2, pb - 74, px + 14, pb - 60, 820, 0.3, 0.2)}" fill="#B8C0C8" stroke="{INK}" stroke-width="1.6"/>'
             f'<path d="M {px - 2} {pb - 60} L {px + 14} {pb - 60} L {px + 12} {pb - 46} L {px} {pb - 46} Z" fill="{BLUE[1]}" stroke="{INK}" stroke-width="1.6"/></g>')
    o.append(stoneware_mug(u, 486, 438, 60, 56, 821, CREAM, side=1, heart_c=BERRY))
    o.append(soft_steam([(480, 432), (474, 414), (484, 398), (478, 378)], 1.6, 5, "#FFFFFF", 0.8, 822))
    o.append(f'<g transform="rotate(-8 120 490)"><path d="M 60 484 L 168 484 L 180 490 L 168 496 L 60 496 Z" fill="{MUST[0]}" stroke="{INK}" stroke-width="1.8"/>'
             f'<path d="M 168 484 L 180 490 L 168 496 Z" fill="#F2DCB8"/><path d="M 176 488 L 180 490 L 176 492 Z" fill="#3A2418"/><path d="M 60 484 L 52 484 L 52 496 L 60 496" fill="#E89A8E" stroke="{INK}" stroke-width="1.8"/></g>')
    rnd = random.Random(823)
    for _ in range(9):
        x, y = rnd.uniform(70, 540), rnd.uniform(462, 484)
        if 50 < x < 200 or 180 < x < 430:
            continue
        o.append(ink(f"M {_f(x)} {_f(y)} q 8 -10 16 -2 q 6 8 -4 10 q -8 0 -6 -6", "#E8C08A", 3, rnd.randint(0, 999), 1, 1))
    o.append(ruled_c(u, 536, "IF GRANDPA CAN'T FIX IT, NO ONE CAN", JOST, 20, "#FBEAD0", 824, ls=2, line_w=10, gap=8, line="#FBEAD0", max_w=470))
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ mom knows best
def duck(u, x, y, s, seed, kerchief=BLUE):
    """A white farm duck walking to the right, with an orange bill and a polka-dot kerchief."""
    k = s / 100
    X = lambda v: x + v * k
    Y = lambda v: y + v * k
    o = [shadow(u, X(6), Y(44), 80 * k, 9 * k, 0.3)]
    # feet
    for fx, fy in ((-4, 34), (22, 36)):
        o.append(f'<path d="M {_f(X(fx))} {_f(Y(fy - 6))} L {_f(X(fx))} {_f(Y(fy))} M {_f(X(fx - 8))} {_f(Y(fy + 6))} L {_f(X(fx))} {_f(Y(fy))} L {_f(X(fx + 14))} {_f(Y(fy + 5))} L {_f(X(fx + 4))} {_f(Y(fy + 9))} Z" '
                 f'fill="#E8902E" stroke="#8A4A10" stroke-width="1.6" stroke-linejoin="round"/>')
    body = smooth_closed([(X(-84), Y(-36)), (X(-60), Y(-12)), (X(-34), Y(-24)), (X(8), Y(-24)), (X(40), Y(-16)), (X(58), Y(4)), (X(48), Y(26)), (X(8), Y(36)), (X(-42), Y(30)), (X(-72), Y(8))])
    o.append(form(u, body, (X(-86), Y(-38), X(60), Y(38)), "#FBF6EC", "#C8BCA8", "#FFFFFF", seed, -10, n=80, shade=(0, 10 * k), shade_op=0.5, ink_w=2.4,
                  length=(8, 22), width=(1, 2.4)))
    wing = smooth_closed([(X(-46), Y(-8)), (X(-6), Y(-18)), (X(34), Y(-6)), (X(20), Y(14)), (X(-26), Y(14))])
    o.append(form(u, wing, (X(-48), Y(-20), X(36), Y(16)), "#F2ECE0", "#BCB09A", "#FFFFFF", seed + 1, 0, n=20, shade=(0, 4), ink_w=2.0,
                  extra_in=f'<path d="M {_f(X(-30))} {_f(Y(4))} q {_f(14 * k)} {_f(-6 * k)} {_f(30 * k)} {_f(-4 * k)} M {_f(X(-36))} {_f(Y(10))} q {_f(16 * k)} {_f(-4 * k)} {_f(34 * k)} 0" stroke="#BCB09A" stroke-width="1.8" fill="none"/>'))
    neck = smooth_closed([(X(24), Y(-16)), (X(30), Y(-50)), (X(36), Y(-78)), (X(62), Y(-90)), (X(80), Y(-74)), (X(64), Y(-50)), (X(56), Y(-12))])
    o.append(form(u, neck, (X(22), Y(-92), X(82), Y(-10)), "#FBF6EC", "#C8BCA8", "#FFFFFF", seed + 2, -90, n=30, shade=(6 * k, 0), shade_op=0.35, ink_w=2.4))
    # bill & eye
    bill = smooth_closed([(X(74), Y(-80)), (X(102), Y(-78)), (X(108), Y(-70)), (X(96), Y(-66)), (X(74), Y(-68))])
    o.append(form(u, bill, (X(72), Y(-82), X(110), Y(-64)), "#F2A03A", "#C0701E", "#FFC870", seed + 3, 0, n=8, shade=(0, 2), ink_w=1.8, ink_col="#7A4010"))
    o.append(f'<circle cx="{_f(X(62))}" cy="{_f(Y(-80))}" r="{_f(4 * k + 1)}" fill="#2A1A10"/><circle cx="{_f(X(61))}" cy="{_f(Y(-81.5))}" r="{_f(1.4 * k + 0.4)}" fill="#FFFFFF"/>'
             f'<ellipse cx="{_f(X(66))}" cy="{_f(Y(-68))}" rx="{_f(6 * k)}" ry="{_f(3.6 * k)}" fill="#F0907A" opacity="0.5"/>')
    # polka-dot kerchief
    kd = soft_poly([(X(24), Y(-40)), (X(70), Y(-46)), (X(48), Y(-8))], seed + 4, 0.4, 0.2)
    dots = "".join(f'<circle cx="{_f(X(dx))}" cy="{_f(Y(dy))}" r="{_f(2.6 * k + 0.6)}" fill="#FFFFFF"/>' for dx, dy in ((36, -36), (52, -38), (44, -26), (60, -42), (48, -16)))
    o.append(form(u, kd, (X(22), Y(-48), X(72), Y(-6)), kerchief[0], kerchief[1], kerchief[2], seed + 5, -30, n=12, shade=(0, 3), ink_w=2.0, extra_in=dots))
    return "".join(o)


def duckling(u, x, y, s, seed, flip=False, look_up=False):
    k = s / 30
    sx = -1 if flip else 1
    o = [shadow(u, x, y + 18 * k, 24 * k, 4 * k, 0.3)]
    o.append(f'<g transform="translate({_f(x)} {_f(y)}) scale({sx} 1)">')
    for fx in (-5, 6):
        o.append(f'<path d="M {_f(fx * k)} {_f(12 * k)} l 0 {_f(5 * k)} l {_f(6 * k)} {_f(2 * k)} l {_f(-7 * k)} {_f(1 * k)} Z" fill="#E8902E" stroke="#8A4A10" stroke-width="1.2" stroke-linejoin="round"/>')
    body = blob(0, 0, 22 * k, 16 * k, seed, 0.05, 14)
    o.append(form(u, body, (-24 * k, -18 * k, 24 * k, 18 * k), "#F8D45A", "#D8A42A", "#FFF0A0", seed, -90, n=30, shade=(2 * k, 4 * k), shade_op=0.4, ink_w=2.0, ink_col="#7A5A10",
                  length=(3, 8), width=(0.8, 1.6)))
    o.append(f'<path d="{blob(-4 * k, -2 * k, 9 * k, 6 * k, seed + 1, 0.1, 10, -10)}" fill="#E8B83A" stroke="#7A5A10" stroke-width="1.4"/>')
    hy = -24 * k if not look_up else -26 * k
    hx = 14 * k
    hd = blob(hx, hy, 13 * k, 12 * k, seed + 2, 0.05, 12)
    o.append(form(u, hd, (hx - 14 * k, hy - 13 * k, hx + 14 * k, hy + 13 * k), "#F8D45A", "#D8A42A", "#FFF0A0", seed + 3, -90, n=14, shade=(1, 3), shade_op=0.3, ink_w=2.0, ink_col="#7A5A10"))
    o.append(f'<path d="M {_f(hx - 2 * k)} {_f(hy - 12 * k)} q {_f(-2 * k)} {_f(-6 * k)} {_f(3 * k)} {_f(-8 * k)} M {_f(hx + 1 * k)} {_f(hy - 12 * k)} q {_f(2 * k)} {_f(-5 * k)} {_f(6 * k)} {_f(-5 * k)}" stroke="#D8A42A" stroke-width="2" fill="none" stroke-linecap="round"/>')
    if look_up:
        o.append(f'<path d="M {_f(hx + 8 * k)} {_f(hy - 4 * k)} L {_f(hx + 20 * k)} {_f(hy - 12 * k)} L {_f(hx + 12 * k)} {_f(hy + 1 * k)} Z" fill="#F2A03A" stroke="#7A4010" stroke-width="1.2" stroke-linejoin="round"/>')
        o.append(f'<circle cx="{_f(hx + 4 * k)}" cy="{_f(hy - 5 * k)}" r="{_f(2.4 * k + 0.4)}" fill="#2A1A10"/><circle cx="{_f(hx + 4.6 * k)}" cy="{_f(hy - 6 * k)}" r="0.9" fill="#FFFFFF"/>')
    else:
        o.append(f'<path d="M {_f(hx + 10 * k)} {_f(hy - 1 * k)} L {_f(hx + 22 * k)} {_f(hy + 1 * k)} L {_f(hx + 10 * k)} {_f(hy + 4 * k)} Z" fill="#F2A03A" stroke="#7A4010" stroke-width="1.2" stroke-linejoin="round"/>')
        o.append(f'<circle cx="{_f(hx + 4 * k)}" cy="{_f(hy - 3 * k)}" r="{_f(2.4 * k + 0.4)}" fill="#2A1A10"/><circle cx="{_f(hx + 4.6 * k)}" cy="{_f(hy - 4 * k)}" r="0.9" fill="#FFFFFF"/>')
    o.append(f'<ellipse cx="{_f(hx + 2 * k)}" cy="{_f(hy + 4 * k)}" rx="{_f(3 * k)}" ry="{_f(2 * k)}" fill="#F0907A" opacity="0.6"/>')
    o.append("</g>")
    return "".join(o)


def butterfly(u, x, y, s, seed, pal=BLUE, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    for sg in (-1, 1):
        up = blob(x + sg * s * 0.55, y - s * 0.35, s * 0.55, s * 0.45, seed + sg, 0.08, 10, sg * 30)
        lo = blob(x + sg * s * 0.4, y + s * 0.32, s * 0.36, s * 0.3, seed + sg + 5, 0.08, 10, sg * -20)
        o.append(form(u, up + " " + lo, (x - s * 1.2, y - s, x + s * 1.2, y + s * 0.7), pal[0], pal[1], pal[2], seed + 3, -60, n=10, shade=None, ink_w=1.8, ink_col=INK,
                      extra_in=f'<circle cx="{_f(x + sg * s * 0.7)}" cy="{_f(y - s * 0.42)}" r="{_f(s * 0.14)}" fill="#FFFFFF" opacity="0.8"/>'))
    o.append(f'<path d="M {x} {_f(y - s * 0.5)} L {x} {_f(y + s * 0.5)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
             f'<path d="M {x} {_f(y - s * 0.5)} q -4 -10 -10 -12 M {x} {_f(y - s * 0.5)} q 4 -10 10 -12" stroke="{INK}" stroke-width="1.6" fill="none"/>')
    o.append("</g>")
    return "".join(o)


@design("mom-knows-best")
def mom_knows_best():
    u = Ids("mom-knows-best")
    o = [paper(u("pp"), "#EEF2E6", FLECK, 901, 1.0)]
    o.append(sky(u, [(0, "#C8DCE6"), (0.55, "#E8EEE4"), (1, "#F6F0DE")], 380, 902, ["#D8E6EC", "#FFFFFF"], 120))
    o.append(puff_cloud(u, 470, 300, 110, 30, 903) + puff_cloud(u, 112, 318, 90, 24, 904))
    o.append(hill(u, [(-20, 372), (110, 350), (240, 364), (380, 344), (500, 356), (620, 340)], 640, "#B4C6A6", "#94AA88", "#D4E0C6", 905))
    o.append(fruit_tree(u, 540, 382, 44, 906, greens=("#7E9A58", "#56703A", "#A8C27A"), fruit=10, fruitc=("#F4B8C4", "#FFFFFF"), detail=False))
    o.append(hill(u, [(-20, 396), (160, 384), (320, 392), (480, 380), (620, 390)], 640, "#9AB27A", "#7A9460", "#BED09C", 907))
    # pond on the left with reeds
    pond = blob(110, 430, 150, 26, 908, 0.05, 18)
    o.append(form(u, pond, (-40, 400, 260, 460), "#A8C8D8", "#7EA0B8", "#D8EAF2", 909, 0, n=60, shade=(0, -4), ink_w=1.8, ink_col="#5E7A8E",
                  extra_in='<path d="M 20 430 q 40 -4 80 0 M 120 440 q 40 -4 80 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.7"/>'))
    for i, (x, h, l) in enumerate(((30, 60, -0.1), (44, 74, 0.05), (232, 56, 0.1), (246, 44, 0.2))):
        o.append(reed(x, 424, h, 910 + i, "#5E7A3A", l))
    o.append(cattail(u, 38, 426, 70, 915, -0.05))
    # the path the family is walking
    gd = smooth_closed([(-20, 450), (200, 448), (420, 440), (620, 444), (620, 640), (-20, 640)])
    o.append(form(u, gd, (-20, 436, 620, 640), "#8EA466", "#6E8A44", "#B4C67E", 916, -4, n=140, shade=(0, -6), ink_w=0))
    o.append(grass(917, (-20, 444, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 170, (8, 22), 2.0))
    trail_d = smooth_closed([(-20, 516), (200, 500), (420, 506), (620, 492), (620, 540), (420, 552), (200, 548), (-20, 560)])
    o.append(form(u, trail_d, (-20, 490, 620, 562), "#E2D2AE", "#B8A47E", "#F4EAD2", 918, 0, n=80, shade=(0, -4), ink_w=0))
    # mama leading the ducklings, the last one distracted by a butterfly
    o.append(duck(u, 398, 466, 132, 919))
    o.append(duckling(u, 284, 512, 30, 920))
    o.append(duckling(u, 212, 516, 28, 921))
    o.append(duckling(u, 142, 520, 29, 922))
    o.append(duckling(u, 76, 524, 27, 923, flip=True, look_up=True))
    o.append(butterfly(u, 104, 430, 16, 924, pal=BLUSH, rot=-14))
    o.append(daisy(u, 560, 560, 16, 925, tilt=0.8) + daisy(u, 520, 586, 13, 926, tilt=0.8) + daisy(u, 40, 590, 14, 927, tilt=0.8) + cosmos(u, 584, 524, 16, 928, pal=ROSE))
    # lettering
    t, _, _ = btext(u, 300, 178, "mom", SERIF_IT, 160, "#A8343A", ["#C04A4A", "#86222A", "#D4645C"], 929, max_w=420, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 238, "KNOWS BEST", JOST, 34, "#3E5A48", 930, ls=10, line_w=40, line="#A8343A"))
    o.append(finish(u))
    return "".join(o)


# ================================================================ dad jokes loading
@design("dad-jokes-loading")
def dad_jokes_loading():
    u = Ids("dad-jokes-loading")
    o = [bg(u, "#2E4A52", ["#36565E", "#26404A", "#3E6068", "#1E363E"], 951, fleck="#E8DCC0", angle=-25)]
    o.append(vignette(u, "#0E1C22", 0.5, 0.55))
    o.append(glow(u, 300, 190, 220, "#F6C870", 0.25))
    # bushy eyebrows, specs and a magnificent mustache
    cx, cy = 300, 170
    for sg in (-1, 1):
        br = smooth_closed([(cx + sg * 26, cy - 54), (cx + sg * 62, cy - 70), (cx + sg * 100, cy - 62), (cx + sg * 96, cy - 54), (cx + sg * 60, cy - 58), (cx + sg * 28, cy - 46)])
        o.append(form(u, br, (cx - 110, cy - 70, cx + 110, cy - 36), "#7A4E30", "#4A2E1C", "#A8784E", 952 + sg, -10 * sg, n=40, shade=None, ink_w=2.0, ink_col="#2A160C",
                      length=(6, 14), width=(1, 2)))
    for sg in (-1, 1):
        lx = cx + sg * 62
        lens = blob(lx, cy - 4, 46, 38, 954 + sg, 0.02, 18)
        o.append(f'<path d="{lens}" fill="#BCD6E0" opacity="0.85"/>'
                 f'<path d="M {_f(lx - 26)} {_f(cy + 10)} L {_f(lx + 6)} {_f(cy - 30)}" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.6"/>'
                 f'<path d="M {_f(lx - 10)} {_f(cy + 18)} L {_f(lx + 16)} {_f(cy - 14)}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.5"/>')
        o.append(f'<path d="{lens}" fill="none" stroke="#2A160C" stroke-width="15"/><path d="{lens}" fill="none" stroke="#7A4A26" stroke-width="11"/>')
        o.append(dabs((lx - 50, cy - 44, lx + 50, cy + 36), ["#C8843A", "#4A2814", "#E0A050"], 956 + sg, 70, (1.5, 3.5), (0.5, 0.9),
                      clip=lambda x, y, lx=lx: 38 < math.hypot((x - lx) * 0.83, y - cy + 4) < 46))
        o.append(f'<path d="M {_f(lx + sg * 46)} {_f(cy - 10)} l {sg * 26} -6" stroke="#5A3418" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<path d="M {cx - 16} {cy - 8} Q {cx} {cy - 22} {cx + 16} {cy - 8}" stroke="#2A160C" stroke-width="12" fill="none"/>'
             f'<path d="M {cx - 16} {cy - 8} Q {cx} {cy - 22} {cx + 16} {cy - 8}" stroke="#7A4A26" stroke-width="8" fill="none"/>')
    must = (f"M {cx} {cy + 54} C {cx - 20} {cy + 40} {cx - 60} {cy + 42} {cx - 92} {cy + 70} C {cx - 108} {cy + 84} {cx - 124} {cy + 76} {cx - 126} {cy + 62} "
            f"C {cx - 120} {cy + 74} {cx - 104} {cy + 72} {cx - 96} {cy + 60} C {cx - 70} {cy + 96} {cx - 24} {cy + 92} {cx} {cy + 76} "
            f"C {cx + 24} {cy + 92} {cx + 70} {cy + 96} {cx + 96} {cy + 60} C {cx + 104} {cy + 72} {cx + 120} {cy + 74} {cx + 126} {cy + 62} "
            f"C {cx + 124} {cy + 76} {cx + 108} {cy + 84} {cx + 92} {cy + 70} C {cx + 60} {cy + 42} {cx + 20} {cy + 40} {cx} {cy + 54} Z")
    o.append(form(u, must, (cx - 128, cy + 38, cx + 128, cy + 98), "#8A5634", "#4E2E1A", "#B88050", 958, lambda x, y: 90 + (x - cx) * 0.5, n=140, shade=(0, 6), shade_op=0.4,
                  hi=(cx - 40, cy + 54, 24, 6), hi_op=0.45, ink_w=2.4, ink_col="#2A160C", length=(10, 24), width=(0.8, 2)))
    # a big DAD JOKES
    t, _, _ = btext(u, 300, 380, "DAD JOKES", BEBAS, 136, "#FBEBD2", ["#FFF6E6", "#E8D2B4", "#F6E0C0"], 959, max_w=460, ls=6, angle=-78, shadow="#0E1A1E", soff=(0.025, 0.04))
    o.append(t)
    # the progress bar, painted, about 87% of the way
    bx0, bx1, by0, by1 = 96, 504, 410, 458
    shell = org_rect(bx0, by0, bx1, by1, 960, 0.6, 0.5)
    o.append(f'<path d="{shell}" fill="#1E3036"/>')
    fill_x = bx0 + 8 + (bx1 - bx0 - 16) * 0.87
    fd = org_rect(bx0 + 8, by0 + 8, fill_x, by1 - 8, 961, 0.5, 0.45)
    stripes = "".join(f'<path d="M {x} {by1} L {x + 24} {by0}" stroke="#F8D888" stroke-width="9" opacity="0.5"/>' for x in range(bx0 - 20, int(fill_x) + 20, 26))
    o.append(form(u, fd, (bx0 + 8, by0 + 8, fill_x, by1 - 8), "#E8A23A", "#B4701E", "#F8C860", 962, 0, n=60, shade=(0, -6), shade_op=0.35, ink_w=0, extra_in=stripes))
    o.append(ink(shell, "#FBEBD2", 4, 963, 2, 0.95))
    o.append(sparkle(fill_x - 4, by0 + 2, 9, "#FFF6D8", 0.95))
    # loading... with blinking dots
    t, sz, w = btext(u, 286, 528, "loading", SERIF_IT, 66, "#F2A88E", ["#F6C0AA", "#E08E72"], 964, max_w=300, angle=-35)
    o.append(t)
    for i in range(3):
        o.append(f'<circle cx="{_f(286 + w / 2 + 16 + i * 18)}" cy="520" r="5.4" fill="#F2A88E" opacity="{1 - i * 0.3:.1f}"/>')
    o.append(finish(u, "#F6E6C8", 0.45))
    return "".join(o)


# ================================================================ life is better on the porch
def rocker(u, x, base, s, seed, face=1, pal=CREAM, cushion=ROSE, throw=None):
    """A painted porch rocking chair in profile (facing +x when face=1)."""
    k = s / 100
    X = lambda v: x + face * v * k
    Y = lambda v: base - v * k
    o = [shadow(u, x, base + 2, 70 * k, 7 * k, 0.35)]
    rock = f"M {_f(X(-66))} {_f(Y(14))} Q {_f(X(-10))} {_f(Y(-6))} {_f(X(64))} {_f(Y(6))}"
    o.append(f'<path d="{rock}" stroke="{INK}" stroke-width="{9 * k + 3:.1f}" fill="none" stroke-linecap="round"/><path d="{rock}" stroke="{pal[0]}" stroke-width="{9 * k:.1f}" fill="none" stroke-linecap="round"/>')
    for a, b in (((-38, 4), (-34, 72)), ((34, 2), (32, 72))):
        d = f"M {_f(X(a[0]))} {_f(Y(a[1]))} L {_f(X(b[0]))} {_f(Y(b[1]))}"
        o.append(f'<path d="{d}" stroke="{INK}" stroke-width="{8 * k + 3:.1f}" stroke-linecap="round"/><path d="{d}" stroke="{pal[0]}" stroke-width="{8 * k:.1f}" stroke-linecap="round"/>')
    # back: two posts with spindles leaning back
    for d in (f"M {_f(X(-36))} {_f(Y(70))} L {_f(X(-58))} {_f(Y(176))}",):
        o.append(f'<path d="{d}" stroke="{INK}" stroke-width="{9 * k + 3:.1f}" stroke-linecap="round"/><path d="{d}" stroke="{pal[0]}" stroke-width="{9 * k:.1f}" stroke-linecap="round"/>')
    crest = f"M {_f(X(-60))} {_f(Y(170))} Q {_f(X(-48))} {_f(Y(184))} {_f(X(-36))} {_f(Y(168))}"
    sp = "".join(f'<path d="M {_f(X(-36 - t * 22 + 6))} {_f(Y(76 + t * 92))} L {_f(X(-36 - t * 22 - 2))} {_f(Y(80 + t * 92))}" stroke="{pal[1]}" stroke-width="2"/>' for t in (0.25, 0.5, 0.75))
    o.append(f'<path d="{crest}" stroke="{INK}" stroke-width="{12 * k + 3:.1f}" stroke-linecap="round" fill="none"/><path d="{crest}" stroke="{pal[0]}" stroke-width="{12 * k:.1f}" stroke-linecap="round" fill="none"/>')
    # back cushion
    bc = smooth_closed([(X(-36), Y(84)), (X(-54), Y(160)), (X(-40), Y(164)), (X(-22), Y(90))])
    o.append(form(u, bc, (min(X(-56), X(-20)), Y(166), max(X(-56), X(-20)), Y(82)), cushion[0], cushion[1], cushion[2], seed, -70, n=16, shade=(face * 3, 0), ink_w=2.0))
    if throw:
        tr = smooth_closed([(X(-58), Y(168)), (X(-40), Y(170)), (X(-30), Y(120)), (X(-26), Y(74)), (X(-44), Y(70)), (X(-46), Y(120))])
        o.append(form(u, tr, (min(X(-60), X(-24)), Y(172), max(X(-60), X(-24)), Y(68)), throw[0], throw[1], throw[2], seed + 9, -80, n=20, shade=(face * 3, 0), ink_w=2.0,
                      extra_in=knit((min(X(-60), X(-24)), Y(172), max(X(-60), X(-24)), Y(68)), throw[1], 7, 6, 0.5, 1.4)))
    # seat with a cushion
    seat = soft_poly([(X(-42), Y(78)), (X(40), Y(78)), (X(40), Y(68)), (X(-42), Y(68))], seed + 1, 0.4, 0.3)
    o.append(f'<path d="{seat}" fill="{pal[0]}" stroke="{INK}" stroke-width="2"/>')
    sc = smooth_closed([(X(-40), Y(80)), (X(-20), Y(92)), (X(38), Y(90)), (X(42), Y(80))])
    o.append(form(u, sc, (min(X(-42), X(44)), Y(94), max(X(-42), X(44)), Y(78)), cushion[0], cushion[1], cushion[2], seed + 2, 0, n=14, shade=(0, 3), ink_w=2.0))
    # arm and its support
    arm = f"M {_f(X(-44))} {_f(Y(118))} L {_f(X(40))} {_f(Y(112))}"
    o.append(f'<path d="{arm}" stroke="{INK}" stroke-width="{8 * k + 3:.1f}" stroke-linecap="round"/><path d="{arm}" stroke="{pal[0]}" stroke-width="{8 * k:.1f}" stroke-linecap="round"/>'
             f'<path d="M {_f(X(32))} {_f(Y(110))} L {_f(X(30))} {_f(Y(80))}" stroke="{INK}" stroke-width="{6 * k + 3:.1f}" stroke-linecap="round"/><path d="M {_f(X(32))} {_f(Y(110))} L {_f(X(30))} {_f(Y(80))}" stroke="{pal[0]}" stroke-width="{6 * k:.1f}" stroke-linecap="round"/>')
    o.append(sp)
    return "".join(o)


def fern_basket(u, x, y, s, seed):
    """A hanging basket of Boston fern: chains, a woven basket, arching fronds spilling down."""
    k = s / 100
    rnd = random.Random(seed)
    o = [f'<path d="M {_f(x)} {_f(y - 110 * k)} L {_f(x - 40 * k)} {_f(y)} M {_f(x)} {_f(y - 110 * k)} L {_f(x + 40 * k)} {_f(y)}" stroke="#5A4A3A" stroke-width="2" stroke-dasharray="4 2"/>']
    fronds = []
    for i in range(26):
        t = i / 25
        dirx = -1 + 2 * t + rnd.uniform(-0.1, 0.1)
        L = 100 * k * rnd.uniform(0.75, 1.1) * (0.75 + 0.35 * abs(dirx))
        bx, by = x + dirx * 30 * k, y - 4 * k
        mx, my = bx + dirx * L * 0.55, by - L * (0.35 - 0.2 * abs(dirx)) * rnd.uniform(0.6, 1.1)
        tx, ty = bx + dirx * L * 0.85, by + L * (0.55 - 0.45 * (1 - abs(dirx))) + rnd.uniform(-8, 8) * k
        fronds.append((bx, by, mx, my, tx, ty))
    rnd.shuffle(fronds)
    for j, (bx, by, mx, my, tx, ty) in enumerate(fronds):
        col = rnd.choice([LEAF, DEEP, LEAF])
        o.append(ink(smooth_open([(bx, by), (mx, my), (tx, ty)]), col[1], 1.8, seed + j, 1, 1))
        for t in [i / 11 for i in range(1, 11)]:
            px = (1 - t) ** 2 * bx + 2 * t * (1 - t) * mx + t * t * tx
            py = (1 - t) ** 2 * by + 2 * t * (1 - t) * my + t * t * ty
            dx_ = 2 * (1 - t) * (mx - bx) + 2 * t * (tx - mx)
            dy_ = 2 * (1 - t) * (my - by) + 2 * t * (ty - my)
            base_a = math.degrees(math.atan2(dy_, dx_))
            ln = 9 * k * (1 - t * 0.55) + 1.5
            for sg in (-1, 1):
                o.append(f'<ellipse cx="{_f(px)}" cy="{_f(py)}" rx="{_f(ln)}" ry="{_f(2.6 * k + 0.9)}" fill="{rnd.choice([col[0], col[2], col[0]])}" stroke="{col[1]}" stroke-width="0.8" '
                         f'transform="rotate({base_a + sg * 58:.0f} {_f(px)} {_f(py)}) translate({_f(ln * 0.8)} 0)"/>')
    bk = smooth_closed([(x - 42 * k, y - 4 * k), (x + 42 * k, y - 4 * k), (x + 34 * k, y + 30 * k), (x, y + 38 * k), (x - 34 * k, y + 30 * k)])
    weave = "".join(f'<path d="M {_f(x - 44 * k)} {_f(y + t * k)} Q {_f(x)} {_f(y + (t + 6) * k)} {_f(x + 44 * k)} {_f(y + t * k)}" stroke="#7A5A34" stroke-width="1.6" fill="none" opacity="0.6"/>' for t in (6, 14, 22))
    o.append(form(u, bk, (x - 44 * k, y - 6 * k, x + 44 * k, y + 40 * k), "#C8A070", "#8A6438", "#E8C890", seed + 50, -90, n=20, shade=(6 * k, 0), ink_w=2.0, extra_in=weave))
    return "".join(o)


@design("life-is-better-on-the-porch")
def porch():
    u = Ids("life-is-better-on-the-porch")
    o = [paper(u("pp"), "#F2ECE0", FLECK, 1001, 1.0)]
    # the view beyond the porch: summer sky, lawn, trees
    o.append(sky(u, [(0, "#B8D4E2"), (0.6, "#E2ECE6"), (1, "#F6EEDA")], 420, 1002, ["#CFE0E6", "#FFFFFF"], 120))
    o.append(puff_cloud(u, 300, 250, 160, 30, 1003))
    o.append(hill(u, [(-20, 350), (140, 330), (300, 342), (460, 326), (620, 340)], 640, "#A8BE94", "#88A276", "#CADAB6", 1004))
    o.append(round_tree(u, 170, 352, 46, 1005, pal=("#6E8A4E", "#4A6232", "#9AB070")) + round_tree(u, 430, 348, 52, 1006, pal=("#7E9A5A", "#56703A", "#A8C27A")))
    o.append(hill(u, [(-20, 376), (200, 366), (400, 370), (620, 362)], 640, "#9AB27A", "#7A9460", "#BED09C", 1007))
    # porch railing
    rail_top, rail_bot = 352, 436
    o.append(f'<path d="{org_rect(-10, rail_top - 8, 610, rail_top + 6, 1008, 0.5, 0.1)}" fill="#FBF7EE" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<path d="{org_rect(-10, rail_bot - 6, 610, rail_bot + 6, 1009, 0.5, 0.1)}" fill="#EEE8DC" stroke="{INK}" stroke-width="2"/>')
    bal = []
    for x in range(10, 600, 26):
        bal.append(f'<path d="{org_rect(x - 5, rail_top + 6, x + 5, rail_bot - 6, 1010 + x, 0.3, 0.1)}" fill="#FBF7EE" stroke="{INK}" stroke-width="1.6"/>'
                   f'<path d="M {x + 3} {rail_top + 8} L {x + 3} {rail_bot - 8}" stroke="#D4CCBC" stroke-width="2.4"/>')
    o.append("".join(bal))
    # porch floor in perspective
    fl = poly_d([(-10, 436), (610, 436), (610, 610), (-10, 610)])
    boards = "".join(f'<path d="M {300 + (x - 300) * 0.35:.0f} 436 L {x} 610" stroke="#7A5A3A" stroke-width="2" opacity="0.5"/>' for x in range(-400, 1000, 60))
    o.append(form(u, fl, (-10, 436, 610, 610), "#B8946A", "#86643E", "#D8B88A", 1011, -90, n=120, shade=None, ink_w=0, length=(30, 80), width=(1.2, 3), extra_in=boards))
    o.append(f'<path d="M -10 438 L 610 438" stroke="#5A3A20" stroke-width="3" opacity="0.6"/>')
    # columns at both sides and the beam with scalloped trim
    for x0 in (-10, 548):
        o.append(form(u, org_rect(x0, -10, x0 + 62, 610, 1012 + x0, 0.4, 0.01), (x0, -10, x0 + 62, 610), "#FBF7EE", "#D4CCBC", "#FFFFFF", 1013 + x0, -90, n=80,
                      shade=(14, 0), shade_op=0.4, ink_w=2.4))
    o.append(form(u, org_rect(-10, -10, 610, 40, 1014, 0.4, 0.02), (-10, -10, 610, 40), "#FBF7EE", "#D4CCBC", "#FFFFFF", 1015, 0, n=60, shade=(0, -6), ink_w=2.4))
    sc = "".join(f'<path d="M {x} 40 q 15 22 30 0" fill="#FBF7EE" stroke="{INK}" stroke-width="2"/><circle cx="{x + 15}" cy="48" r="3" fill="#D4CCBC"/>' for x in range(52, 548, 30))
    o.append(sc)
    # hanging ferns in the corners
    o.append(fern_basket(u, 108, 262, 84, 1016) + fern_basket(u, 492, 262, 84, 1017))
    # two rockers facing each other and a little table with lemonade
    o.append(rocker(u, 172, 560, 100, 1018, face=1, pal=CREAM, cushion=SAGE, throw=ROSE))
    o.append(rocker(u, 428, 560, 100, 1019, face=-1, pal=CREAM, cushion=SAGE))
    tx, ttop = 300, 476
    o.append(shadow(u, tx, 562, 46, 6, 0.3))
    o.append(f'<path d="M {tx - 30} {ttop + 6} L {tx - 34} 560 M {tx + 30} {ttop + 6} L {tx + 34} 560" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
             f'<path d="M {tx - 30} {ttop + 6} L {tx - 34} 560 M {tx + 30} {ttop + 6} L {tx + 34} 560" stroke="{WOOD[0]}" stroke-width="4" stroke-linecap="round"/>')
    o.append(form(u, org_rect(tx - 46, ttop, tx + 46, ttop + 10, 1020, 0.3, 0.3), (tx - 46, ttop, tx + 46, ttop + 10), WOOD[0], WOOD[1], WOOD[2], 1021, 0, n=8, shade=(0, -2), ink_w=1.8))
    # pitcher
    pb = ttop
    pd = smooth_closed([(tx - 16, pb - 64), (tx + 12, pb - 64), (tx + 20, pb - 30), (tx + 16, pb - 2), (tx - 18, pb - 2), (tx - 22, pb - 30)])
    o.append(f'<path d="M {tx + 14} {pb - 54} q 18 2 14 22 q -2 12 -14 12" stroke="#C8D8DC" stroke-width="5" fill="none"/>')
    o.append(f'<path d="{pd}" fill="#F6E27A" opacity="0.85"/>')
    o.append(f'<path d="M {tx - 20} {pb - 46} L {tx + 18} {pb - 46}" stroke="#FFF6C0" stroke-width="2"/>')
    for i, (lx, ly) in enumerate(((tx - 6, pb - 30), (tx + 8, pb - 18))):
        o.append(f'<circle cx="{lx}" cy="{ly}" r="6" fill="#F8E890" stroke="#E2B83A" stroke-width="2"/><path d="M {lx - 4} {ly} L {lx + 4} {ly} M {lx} {ly - 4} L {lx} {ly + 4}" stroke="#E2B83A" stroke-width="1"/>')
    o.append(f'<path d="M {tx - 12} {pb - 60} L {tx - 12} {pb - 8}" stroke="#FFFFFF" stroke-width="3" opacity="0.7" stroke-linecap="round"/>' + ink(pd, "#4E6A70", 1.8, 1022, 1, 0.75))
    o.append(f'<path d="M {tx - 16} {pb - 64} L {tx - 24} {pb - 70}" stroke="#4E6A70" stroke-width="2"/>')
    for gx in (tx - 36, tx + 36):
        gd = soft_poly([(gx - 8, pb - 30), (gx + 8, pb - 30), (gx + 6, pb - 1), (gx - 6, pb - 1)], gx, 0.2, 0.2)
        o.append(f'<path d="{gd}" fill="#F6E27A" opacity="0.85"/>' + ink(gd, "#4E6A70", 1.6, gx, 1, 0.7) + f'<path d="M {gx - 4} {pb - 26} L {gx - 4} {pb - 6}" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>')
    o.append(f'<path d="M {tx + 40} {pb - 28} L {tx + 30} {pb - 50}" stroke="#E8607A" stroke-width="2.4"/>')
    # lettering in the sky between the ferns
    t, _, _ = btext(u, 300, 124, "life is better", SERIF_IT, 62, "#3E5A48", ["#56745E", "#2A3E30"], 1023, max_w=300, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 206, "on the porch", SERIF_IT, 70, "#B4483E", ["#C85A4A", "#963226", "#D8705E"], 1024, max_w=300, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ our little nest
def nest(u, cx, cy, w, h, seed):
    """A woven twig nest: a bowl of many crossing painted twigs, darker inside."""
    rnd = random.Random(seed)
    o = [shadow(u, cx + 6, cy + h * 0.5, w * 0.55, h * 0.2, 0.3)]
    bowl = f"M {_f(cx - w / 2)} {_f(cy)} Q {_f(cx - w * 0.48)} {_f(cy + h * 0.9)} {_f(cx)} {_f(cy + h)} Q {_f(cx + w * 0.48)} {_f(cy + h * 0.9)} {_f(cx + w / 2)} {_f(cy)} Q {_f(cx)} {_f(cy + h * 0.25)} {_f(cx - w / 2)} {_f(cy)} Z"
    o.append(form(u, bowl, (cx - w / 2, cy - 4, cx + w / 2, cy + h), "#A8784A", "#6E4A2A", "#C8985E", seed, 0, n=40, shade=(0, -h * 0.2), ink_w=0))
    tw = []
    for _ in range(70):
        t = rnd.uniform(0.05, 0.95)
        y = cy + h * rnd.uniform(0.0, 0.85)
        half = w / 2 * math.sqrt(max(0.05, 1 - ((y - cy) / h) ** 1.4))
        x0, x1 = cx - half * rnd.uniform(0.6, 1.05), cx + half * rnd.uniform(0.6, 1.05)
        if rnd.random() < 0.5:
            x0, x1 = x1, x0
        tw.append(f'<path d="M {_f(x0)} {_f(y + rnd.uniform(-6, 6))} Q {_f(cx)} {_f(y + rnd.uniform(4, 12))} {_f(x1)} {_f(y + rnd.uniform(-6, 6))}" stroke="{rnd.choice(["#6E4A2A", "#C8985E", "#8A6038", "#E2B880"])}" '
                  f'stroke-width="{rnd.uniform(1.6, 3.2):.1f}" fill="none" stroke-linecap="round" opacity="0.9"/>')
    o.append("".join(tw))
    for _ in range(10):
        x, y = cx + rnd.choice((-1, 1)) * w * rnd.uniform(0.4, 0.56), cy + rnd.uniform(-4, h * 0.4)
        o.append(f'<path d="M {_f(x)} {_f(y)} l {_f(rnd.uniform(-14, 14))} {_f(rnd.uniform(-10, 4))}" stroke="#8A6038" stroke-width="2" stroke-linecap="round"/>')
    return bowl, "".join(o)


def chick(u, x, y, s, seed, rot=0):
    """A fluffy baby bird peeking out of the nest, beak open wide."""
    k = s / 30
    o = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    hd = blob(x, y, 22 * k, 20 * k, seed, 0.05, 14)
    o.append(form(u, hd, (x - 24 * k, y - 22 * k, x + 24 * k, y + 22 * k), "#B8B0A8", "#7E766E", "#E2DCD4", seed, -90, n=20, shade=(2, 4), shade_op=0.35, ink_w=2.0))
    o.append(f'<path d="M {_f(x - 4 * k)} {_f(y - 19 * k)} q {_f(-4 * k)} {_f(-10 * k)} {_f(2 * k)} {_f(-12 * k)} M {_f(x + 2 * k)} {_f(y - 19 * k)} q {_f(4 * k)} {_f(-8 * k)} {_f(10 * k)} {_f(-6 * k)}" stroke="#9A928A" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M {_f(x - 13 * k)} {_f(y + 2 * k)} L {_f(x)} {_f(y - 22 * k)} L {_f(x + 13 * k)} {_f(y + 2 * k)} L {_f(x)} {_f(y - 4 * k)} Z" fill="#F6C23A" stroke="#9A6A10" stroke-width="1.6" stroke-linejoin="round" transform="translate(0 {_f(-8 * k)})"/>'
             f'<path d="M {_f(x - 8 * k)} {_f(y - 4 * k)} L {_f(x)} {_f(y - 18 * k)} L {_f(x + 8 * k)} {_f(y - 4 * k)} Z" fill="#E8604A" transform="translate(0 {_f(-8 * k)})"/>')
    for sg in (-1, 1):
        o.append(f'<circle cx="{_f(x + sg * 10 * k)}" cy="{_f(y + 4 * k)}" r="{_f(3 * k + 0.4)}" fill="#2A1A10"/><circle cx="{_f(x + sg * 10 * k - 1)}" cy="{_f(y + 3 * k)}" r="1" fill="#FFFFFF"/>')
    o.append("</g>")
    return "".join(o)


@design("our-little-nest")
def our_little_nest():
    u = Ids("our-little-nest")
    o = [bg(u, "#E2ECEE", ["#D6E4E8", "#EEF4F4", "#CCDCE0"], 1101, fleck="#4A6070", angle=-20)]
    o.append(glow(u, 300, 380, 280, "#FFF6E8", 0.7))
    # a blossoming branch across the picture
    br = [(-20, 460), (110, 462), (230, 452), (340, 436), (460, 412), (620, 372)]
    o.append(f'<path d="{blob(300, 400, 190, 150, 1149, 0.06, 18)}" fill="#FBE8DC" opacity="0.7"/>')
    o.append(twig(u, br, 26, 12, 1102))
    o.append(twig(u, [(150, 450), (120, 400), (96, 346), (60, 320)], 9, 4, 1103))
    o.append(twig(u, [(470, 410), (500, 470), (530, 520)], 8, 4, 1104))
    o.append(twig(u, [(380, 424), (420, 366), (432, 320)], 7, 3, 1105))
    rnd = random.Random(1106)
    for i, (x, y) in enumerate(((96, 346), (60, 320), (120, 396), (432, 320), (424, 356), (530, 520), (502, 470), (40, 456), (580, 384), (200, 452))):
        o.append(green_leaf(u, x, y, 30, 10, rnd.uniform(-170, -10), 1107 + i, pal=LEAF))
    for i, (x, y, r) in enumerate(((70, 316, 15), (100, 344, 13), (128, 390, 12), (430, 316, 14), (452, 344, 12), (528, 516, 13), (512, 482, 11), (40, 444, 13),
                                    (566, 372, 14), (596, 396, 11), (196, 434, 11), (174, 462, 10))):
        o.append(blossom(u, x, y, r, 1120 + i, rot=rnd.uniform(0, 70)))
    # petals drifting
    for x, y, r in ((160, 300, 30), (520, 280, 120), (250, 540, -40), (380, 536, 60)):
        o.append(f'<path d="{blob(x, y, 7, 4, x + y, 0.1, 8, r)}" fill="#F6C4CC" stroke="#D8889A" stroke-width="1.2"/>')
    # the nest with three hungry chicks
    bowl, nest_o = nest(u, 270, 398, 236, 92, 1140)
    o.append(f'<path d="{blob(270, 406, 106, 18, 1141, 0.05, 14)}" fill="#3E2614"/>')
    o.append(chick(u, 210, 384, 40, 1142, -16) + chick(u, 272, 368, 46, 1143, 0) + chick(u, 334, 384, 39, 1144, 16))
    o.append(nest_o)
    # mama bird arriving with a worm
    o.append(songbird(u, 474, 362, 40, 1145, pal=BLUE, flip=False, wing_up=True))
    o.append(ink("M 434 346 q -10 8 -5 16 q 8 8 -3 16 q -10 5 -5 13", "#E8807A", 5, 1146, 1, 1))
    # lettering
    o.append(ruled_c(u, 102, "OUR LITTLE", JOST, 34, "#4A6070", 1147, ls=10, line_w=40, line="#B4554F"))
    t, _, _ = btext(u, 300, 230, "nest", SERIF_IT, 160, "#8E5A3A", ["#A86E48", "#6E4028", "#C08A5E"], 1148, max_w=420, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ the laundry can wait
@design("the-laundry-can-wait")
def the_laundry_can_wait():
    u = Ids("the-laundry-can-wait")
    o = [paper(u("pp"), "#EEF2E4", FLECK, 1201, 1.0)]
    o.append(sky(u, [(0, "#BFD8E4"), (0.7, "#E8F0E6"), (1, "#F4F0DC")], 430, 1202, ["#D2E4EA", "#FFFFFF"], 120))
    o.append(glow(u, 300, 120, 260, "#FFF6DC", 0.6))
    o.append(hill(u, [(-20, 404), (150, 386), (300, 396), (450, 382), (620, 394)], 640, "#A8BE94", "#88A276", "#CADAB6", 1203))
    o.append(poplar(u, 330, 404, 90, 1204, pal=("#8EA668", "#66804A", "#B4C88C")) + poplar(u, 352, 406, 70, 1205, pal=("#9AB070", "#6E8A4E", "#BCD098")))
    # lawn
    gd = smooth_closed([(-20, 440), (300, 430), (620, 440), (620, 640), (-20, 640)])
    o.append(form(u, gd, (-20, 426, 620, 640), "#8EA466", "#6E8A44", "#B4C67E", 1206, -4, n=160, shade=(0, -8), ink_w=0))
    o.append(grass(1207, (-20, 436, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 190, (8, 22), 2.0))
    # two trees holding the hammock, leaves spilling in from the corners
    for x, sg in ((70, -1), (530, 1)):
        trunk = soft_poly([(x - 16, 470), (x - 12, 200), (x - 6, 120), (x + 6, 120), (x + 12, 200), (x + 16, 470)], 1208 + x, 0.6, 0.1)
        o.append(form(u, trunk, (x - 18, 110, x + 18, 472), DARKWOOD[0], DARKWOOD[1], DARKWOOD[2], 1209 + x, -90, n=60, shade=(sg * -8, 0), ink_w=2.2,
                      extra_in=f'<path d="M {x - 4} 440 q 4 -60 -2 -120 M {x + 6} 380 q 2 -40 -2 -80" stroke="{DARKWOOD[1]}" stroke-width="1.6" fill="none" opacity="0.6"/>'))
    canopy = " ".join(blob(x, y, rx, ry, 1210 + i, 0.08, 14) for i, (x, y, rx, ry) in enumerate(((20, 40, 120, 90), (110, 0, 110, 70), (-20, 160, 80, 70),
                                                                                             (580, 40, 120, 90), (490, 0, 110, 70), (620, 160, 80, 70))))
    o.append(f'<path d="{canopy}" fill="none" stroke="{INK}" stroke-width="3" opacity="0.7"/>')
    o.append(form(u, canopy, (-100, -70, 700, 230), DEEP[0], DEEP[1], LEAF[0], 1211, -60, n=500, shade=(0, 12), shade_op=0.5, ink_w=0, length=(8, 22), width=(1.2, 3.4), curve=0.5,
                  extra_in=dabs((-100, -70, 700, 230), [DEEP[1], LEAF[2]], 1212, 200, (2.5, 5), (0.3, 0.6), 0.5)))
    # the hammock: ropes, a striped sling sagging between the trees
    hl, hr, hy, sag = (86, 300), (514, 300), 300, 120
    o.append(f'<path d="M 86 296 L 150 330 M 514 296 L 450 330" stroke="#8A6A44" stroke-width="3"/>')
    for i in range(6):
        o.append(f'<path d="M 150 330 L {178 + i * 6} {356 + i * 6}" stroke="#C8A878" stroke-width="1.6"/><path d="M 450 330 L {422 - i * 6} {356 + i * 6}" stroke="#C8A878" stroke-width="1.6"/>')
    sling = "M 176 352 Q 300 470 424 352 L 432 384 Q 300 500 168 384 Z"
    sling_cl = u("sl")
    stripes = "".join(f'<path d="M 120 {y} Q 300 {y + 120} 480 {y}" stroke="{c}" stroke-width="12" fill="none"/>' for y, c in ((330, "#E8A08A"), (354, "#F6E6CC"), (378, "#86A4BE"), (402, "#F6E6CC")))
    o.append(shadow(u, 300, 520, 140, 12, 0.3))
    o.append(form(u, sling, (166, 350, 434, 470), "#F6E6CC", "#C8B494", "#FFFFFF", 1213, 0, n=60, shade=(0, -10), shade_op=0.35, ink_w=2.4, extra_in=stripes))
    # a sun hat and a book left in the hammock, lemonade on the grass
    o.append(f'<path d="{blob(262, 404, 46, 12, 1214, 0.05, 14, -6)}" fill="#E8C886" stroke="{INK}" stroke-width="2"/>'
             f'<path d="{blob(262, 394, 24, 16, 1215, 0.05, 12, -6)}" fill="#F2D898" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M 240 398 Q 262 406 284 396" stroke="{ROSE[0]}" stroke-width="6" fill="none"/>')
    o.append(f'<g transform="rotate(10 348 408)"><path d="M 314 412 L 346 398 L 382 410 L 348 424 Z" fill="{BLUE[1]}" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M 346 398 L 348 424" stroke="{INK}" stroke-width="1.6"/></g>')
    # the abandoned laundry basket, overflowing, one sock escaping
    bx, bb = 452, 560
    o.append(shadow(u, bx + 6, bb, 76, 10, 0.35))
    clothes = [(bx - 40, bb - 92, 30, 18, ROSE), (bx, bb - 98, 34, 20, BLUE), (bx + 40, bb - 90, 28, 16, MUST), (bx - 14, bb - 108, 26, 16, CREAM), (bx + 22, bb - 110, 22, 14, SAGE)]
    for i, (x, y, rx, ry, pal) in enumerate(clothes):
        o.append(form(u, blob(x, y, rx, ry, 1216 + i, 0.15, 12), (x - rx, y - ry, x + rx, y + ry), pal[0], pal[1], pal[2], 1217 + i, -30, n=10, shade=(0, 4), ink_w=1.8))
    o.append(f'<path d="M {bx - 60} {bb - 84} q -16 30 -4 60" stroke="{BLUE[0]}" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M {bx - 60} {bb - 84} q -16 30 -4 60" stroke="{INK}" stroke-width="2" fill="none"/>')
    bsk = soft_poly([(bx - 70, bb - 84), (bx + 70, bb - 84), (bx + 56, bb), (bx - 56, bb)], 1222, 0.5, 0.12)
    weave = "".join(f'<path d="M {bx - 72} {y} L {bx + 72} {y}" stroke="#7A5A34" stroke-width="2" opacity="0.6"/>' for y in range(bb - 72, bb, 12))
    weave += "".join(f'<path d="M {x} {bb - 84} L {x + (x - bx) * -0.1:.0f} {bb}" stroke="#7A5A34" stroke-width="1.6" opacity="0.5"/>' for x in range(bx - 60, bx + 61, 15))
    o.append(form(u, bsk, (bx - 72, bb - 86, bx + 72, bb), "#D8B07A", "#9A7444", "#F2D29A", 1223, -90, n=40, shade=(10, 0), ink_w=2.4, extra_in=weave))
    o.append(f'<path d="{org_rect(bx - 74, bb - 90, bx + 74, bb - 78, 1224, 0.4, 0.4)}" fill="#C8A070" stroke="{INK}" stroke-width="2"/>')
    sock = f"M 540 540 L 548 512 L 562 512 L 558 538 Q 570 544 566 556 L 540 556 Z"
    o.append(form(u, sock, (538, 510, 572, 558), "#F6E6CC", "#C8B494", "#FFFFFF", 1225, -90, n=8, shade=(2, 0), ink_w=1.8,
                  extra_in='<path d="M 546 520 L 562 520 M 545 526 L 560 526" stroke="#C86A54" stroke-width="3"/>'))
    gx, gb = 150, 548
    o.append(shadow(u, gx, gb, 16, 4, 0.3) + f'<path d="{soft_poly([(gx - 13, gb - 44), (gx + 13, gb - 44), (gx + 10, gb), (gx - 10, gb)], 1226, 0.2, 0.2)}" fill="#F6E27A" opacity="0.85"/>'
             + ink(soft_poly([(gx - 13, gb - 44), (gx + 13, gb - 44), (gx + 10, gb), (gx - 10, gb)], 1226, 0.2, 0.2), "#4E6A70", 1.6, 1227, 1, 0.75)
             + f'<circle cx="{gx + 12}" cy="{gb - 44}" r="10" fill="#F8E890" stroke="#E2B83A" stroke-width="2"/><path d="M {gx - 4} {gb - 40} L {gx - 4} {gb - 6}" stroke="#FFFFFF" stroke-width="3" opacity="0.7"/>'
             + f'<path d="M {gx + 2} {gb - 42} L {gx - 8} {gb - 68}" stroke="#E8607A" stroke-width="3"/>')
    o.append(daisy(u, 92, 566, 15, 1228, tilt=0.8) + daisy(u, 236, 584, 13, 1229, tilt=0.8) + daisy(u, 330, 560, 12, 1230, tilt=0.8))
    # lettering
    o.append(ruled_c(u, 116, "THE LAUNDRY", JOST, 34, "#3E5A62", 1231, ls=10, line_w=36, line="#B4483E", max_w=420))
    t, _, _ = btext(u, 300, 214, "can wait", SERIF_IT, 110, "#B4483E", ["#C85A4A", "#963226", "#D8705E"], 1232, max_w=400, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ you are loved
def teddy(u, cx, cy, s, seed, fur_pal=("#C8925E", "#8E5E34", "#E6B888"), muzzle=("#F2D6B0", "#C8A47A", "#FFF0D8")):
    """A plush teddy bear sitting and hugging a big red heart."""
    k = s / 100
    X = lambda v: cx + v * k
    Y = lambda v: cy + v * k
    ang = lambda px, py, ox, oy: math.degrees(math.atan2(py - oy, px - ox)) + 90
    o = [shadow(u, cx, Y(150), 130 * k, 14 * k, 0.35)]

    def part(d, box, origin, sd, hi=None, shade=(6, 8)):
        return form(u, d, box, fur_pal[0], fur_pal[1], fur_pal[2], sd, lambda px, py: ang(px, py, *origin), n=(box[2] - box[0]) * (box[3] - box[1]) / 40,
                    shade=(shade[0] * k, shade[1] * k), shade_op=0.5, hi=hi, hi_op=0.4, ink_w=2.6, ink_col="#4A2A14", length=(4, 10), width=(0.8, 2), curve=0.4)
    # legs, out in front
    for sg in (-1, 1):
        lg = blob(X(sg * 62), Y(120), 40 * k, 30 * k, seed + sg, 0.04, 14)
        o.append(part(lg, (X(sg * 62) - 42 * k, Y(88), X(sg * 62) + 42 * k, Y(152)), (X(sg * 62), Y(120)), seed + 2 + sg))
        pad = blob(X(sg * 70), Y(126), 18 * k, 20 * k, seed + 5 + sg, 0.05, 12)
        o.append(form(u, pad, (X(sg * 70) - 20 * k, Y(104), X(sg * 70) + 20 * k, Y(148)), muzzle[0], muzzle[1], muzzle[2], seed + 7 + sg, -90, n=10, shade=None, ink_w=2.0, ink_col="#4A2A14",
                      extra_in=f'<path d="{heart_path(X(sg * 70), Y(124), 7 * k)}" fill="{BERRY[0]}" opacity="0.8"/>'))
    # body
    body = blob(cx, Y(60), 84 * k, 92 * k, seed + 10, 0.03, 18)
    o.append(part(body, (X(-86), Y(-34), X(86), Y(154)), (cx, Y(60)), seed + 11, hi=(X(-40), Y(10), 20 * k, 30 * k)))
    tummy = blob(cx, Y(80), 52 * k, 58 * k, seed + 12, 0.04, 16)
    o.append(form(u, tummy, (X(-54), Y(20), X(54), Y(140)), muzzle[0], muzzle[1], muzzle[2], seed + 13, -90, n=40, shade=None, ink_w=0, length=(4, 10), width=(0.8, 2)))
    # ears
    for sg in (-1, 1):
        ear = blob(X(sg * 70), Y(-150), 30 * k, 28 * k, seed + 20 + sg, 0.04, 12)
        o.append(part(ear, (X(sg * 70) - 32 * k, Y(-180), X(sg * 70) + 32 * k, Y(-120)), (X(sg * 70), Y(-150)), seed + 22 + sg))
        o.append(f'<path d="{blob(X(sg * 70), Y(-148), 16 * k, 15 * k, seed + 24 + sg, 0.05, 10)}" fill="{muzzle[1]}"/>')
    # head
    head = blob(cx, Y(-90), 92 * k, 80 * k, seed + 30, 0.03, 20)
    o.append(part(head, (X(-94), Y(-172), X(94), Y(-8)), (cx, Y(-90)), seed + 31, hi=(X(-40), Y(-130), 26 * k, 14 * k)))
    mz = blob(cx, Y(-58), 38 * k, 28 * k, seed + 32, 0.04, 14)
    o.append(form(u, mz, (X(-40), Y(-88), X(40), Y(-28)), muzzle[0], muzzle[1], muzzle[2], seed + 33, -90, n=20, shade=(0, 4 * k), shade_op=0.35, ink_w=2.2, ink_col="#4A2A14"))
    o.append(f'<path d="{blob(cx, Y(-70), 14 * k, 10 * k, seed + 34, 0.05, 10)}" fill="#3A2016"/><ellipse cx="{_f(X(-4))}" cy="{_f(Y(-73))}" rx="{_f(4 * k)}" ry="{_f(2.4 * k)}" fill="#FFFFFF" opacity="0.6"/>')
    o.append(ink(f"M {_f(cx)} {_f(Y(-60))} L {_f(cx)} {_f(Y(-50))} M {_f(X(-14))} {_f(Y(-48))} Q {_f(X(-6))} {_f(Y(-40))} {_f(cx)} {_f(Y(-50))} Q {_f(X(6))} {_f(Y(-40))} {_f(X(14))} {_f(Y(-48))}", "#3A2016", 2.6, seed + 35, 1, 1))
    for sg in (-1, 1):
        o.append(f'<circle cx="{_f(X(sg * 34))}" cy="{_f(Y(-98))}" r="{_f(8 * k)}" fill="#2A1A10"/><circle cx="{_f(X(sg * 34 - 3))}" cy="{_f(Y(-101))}" r="{_f(2.6 * k)}" fill="#FFFFFF"/>'
                 f'<ellipse cx="{_f(X(sg * 56))}" cy="{_f(Y(-68))}" rx="{_f(12 * k)}" ry="{_f(7 * k)}" fill="#F0806A" opacity="0.45"/>')
    # stitched seam down the head
    o.append(f'<path d="M {_f(cx)} {_f(Y(-170))} L {_f(cx)} {_f(Y(-130))}" stroke="#7A4E28" stroke-width="2" stroke-dasharray="4 3" opacity="0.7"/>')
    # a satin bow at the neck
    o.append(bow(u, cx, Y(-6), 22 * k, seed + 40, pal=BLUSH, tails=False))
    # the heart, hugged by both arms
    hd = heart_path(cx, Y(56), 46 * k)
    o.append(form(u, hd, (X(-76), Y(-4), X(76), Y(120)), BERRY[0], BERRY[1], BERRY[2], seed + 41, -60, n=160, shade=(8 * k, 8 * k), shade_op=0.5,
                  hi=(X(-34), Y(30), 16 * k, 10 * k), hi_op=0.55, ink_w=2.6, ink_col="#6A1418", length=(8, 24), width=(1, 3)))
    o.append(f'<path d="{heart_path(cx, Y(56), 38 * k)}" fill="none" stroke="#FBE2DA" stroke-width="2" stroke-dasharray="5 4" opacity="0.8"/>')
    for sg in (-1, 1):
        arm = smooth_closed([(X(sg * 76), Y(4)), (X(sg * 92), Y(40)), (X(sg * 70), Y(84)), (X(sg * 30), Y(96)), (X(sg * 20), Y(78)), (X(sg * 50), Y(56)), (X(sg * 60), Y(20))])
        o.append(part(arm, (min(X(sg * 94), X(sg * 18)), Y(0), max(X(sg * 94), X(sg * 18)), Y(98)), (X(sg * 60), Y(50)), seed + 42 + sg, shade=(3, 4)))
    return "".join(o)


@design("you-are-loved")
def you_are_loved():
    u = Ids("you-are-loved")
    o = [bg(u, "#F8E4DC", ["#F2D6CA", "#FCF0EA", "#EECABC"], 1301, fleck="#9A6A5A", angle=-20)]
    o.append(glow(u, 300, 320, 260, "#FFF6F0", 0.85))
    rnd = random.Random(1302)
    for i in range(16):
        x, y = rnd.uniform(70, 530), rnd.uniform(130, 470)
        if 150 < x < 450 and 150 < y < 470:
            continue
        o.append(f'<g transform="rotate({rnd.uniform(-25, 25):.0f} {_f(x)} {_f(y)})">' + painted_heart(u, x, y, rnd.uniform(5, 9), rnd.choice((ROSE, BLUSH, BERRY)), 1303 + i) + "</g>")
    o.append(teddy(u, 300, 290, 94, 1320))
    o.append(ruled_c(u, 100, "YOU ARE", JOST, 36, "#7A3A3A", 1330, ls=12, line_w=50, gap=16, line="#C8464A"))
    t, _, _ = btext(u, 300, 534, "loved", SERIF_IT, 112, "#A8343A", ["#C04A4A", "#86222A", "#D4645C"], 1331, max_w=420, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ love you more (repaint)
@design("love-you-more")
def love_you_more():
    u = Ids("love-you-more")
    o = [bg(u, "#F4D6CE", ["#EECAC0", "#FAE6E0", "#E8BEB2"], 1401, fleck="#9A5A4A", angle=-20)]
    o.append(glow(u, 300, 300, 260, "#FFF2EC", 0.8))
    rnd = random.Random(1402)
    for i, (x, y, s_, r) in enumerate(((92, 210, 9, -20), (510, 196, 11, 16), (528, 420, 8, 10), (74, 400, 7, -12), (150, 160, 6, 8), (462, 150, 6, -8))):
        o.append(f'<g transform="rotate({r} {x} {y})">' + painted_heart(u, x, y, s_, rnd.choice((ROSE, BLUSH, BERRY)), 1403 + i) + "</g>")
    ex0, ey0, ex1, ey1 = 158, 206, 442, 396
    cx, cy = (ex0 + ex1) / 2, (ey0 + ey1) / 2
    o.append(f'<g transform="rotate(-5 {cx} {cy})">')
    # a rose tucked behind the envelope
    o.append(ink("M 300 330 Q 380 280 446 236", DEEP[1], 4, 1404, 1, 1))
    o.append(green_leaf(u, 420, 252, 46, 14, -70, 1405, pal=DEEP) + green_leaf(u, 436, 244, 40, 12, 20, 1406, pal=LEAF))
    o.append(rose(u, 462, 220, 34, 1407, pal=BERRY))
    o.append(shadow(u, cx + 10, ey1 + 6, (ex1 - ex0) * 0.52, 12, 0.35))
    env = org_rect(ex0, ey0, ex1, ey1, 1408, 0.6, 0.02)
    o.append(form(u, env, (ex0, ey0, ex1, ey1), "#FBF3E6", "#D8C6AC", "#FFFFFF", 1409, -10, n=160, shade=(0, -10), shade_op=0.3, ink_w=2.6, sop=(0.1, 0.25)))
    # side and bottom folds
    o.append(form(u, poly_d([(ex0, ey1), (cx, cy + 20), (ex1, ey1)]), (ex0, cy, ex1, ey1), "#F4E8D6", "#D2BEA2", "#FFFFFF", 1410, -90, n=40, shade=None, ink_w=2.0))
    o.append(f'<path d="M {ex0} {ey0} L {cx - 30} {cy + 4} M {ex1} {ey0} L {cx + 30} {cy + 4}" stroke="#C8B496" stroke-width="2" opacity="0.7"/>')
    # top flap folded down
    flap = poly_d([(ex0 + 2, ey0 + 2), (ex1 - 2, ey0 + 2), (cx, cy + 22)])
    o.append(f'<path d="{flap}" fill="#3A2418" opacity="0.15" transform="translate(0 6)"/>')
    o.append(form(u, flap, (ex0, ey0, ex1, cy + 24), "#FFF8EE", "#DCCAAE", "#FFFFFF", 1411, -80, n=60, shade=(0, -6), shade_op=0.3, ink_w=2.4))
    # a heart-shaped wax seal
    sx, sy = cx, cy + 12
    drip = blob(sx, sy + 4, 38, 33, 1412, 0.12, 14)
    o.append(f'<path d="{drip}" fill="{BERRY[1]}"/>')
    o.append(form(u, heart_path(sx, sy + 2, 26), (sx - 40, sy - 34, sx + 40, sy + 34), BERRY[0], BERRY[1], BERRY[2], 1413, -60, n=40, shade=(4, 4), shade_op=0.5,
                  hi=(sx - 12, sy - 12, 8, 5), hi_op=0.6, ink_w=2.2, ink_col="#5A1014"))
    o.append(f'<path d="{heart_path(sx, sy + 2, 18)}" fill="none" stroke="#6A1418" stroke-width="2" opacity="0.6"/>')
    # a little sprig of baby's breath at the left corner
    o.append(ink("M 170 390 Q 140 350 120 316 M 150 360 Q 168 330 166 300", SAGE[1], 2.2, 1414, 1, 1))
    for x, y in ((120, 314), (126, 306), (114, 322), (166, 298), (172, 306), (160, 302), (132, 336), (176, 318)):
        o.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#FFFFFF" stroke="#C8BCA8" stroke-width="1"/>')
    o.append("</g>")
    # lettering
    t, _, _ = btext(u, 300, 140, "love you", SERIF_IT, 104, "#7A2A34", ["#963A44", "#5A1A22", "#A84A50"], 1415, max_w=440, angle=-35, shadow="#FFF4EE", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 534, "MORE", BEBAS, 150, "#C8464A", ["#D85A5A", "#9A2A30", "#E8807A"], 1416, max_w=360, ls=14, angle=-80, shadow="#6A1A22", soff=(0.02, 0.035), hi="#F8B0A8")
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ blessed (repaint)
@design("blessed")
def blessed():
    u = Ids("blessed")
    o = [bg(u, "#DEE4D2", ["#D4DCC6", "#E8ECDE", "#CCD6BC"], 1501, fleck="#5E6E4A", angle=-20)]
    o.append(glow(u, 300, 300, 240, "#FFFBEE", 0.8))
    rnd = random.Random(1502)
    cx, cy, R = 300, 300, 206

    def pt(a, r=R):
        return cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r
    # two branches sweeping up from the bottom, open at the top
    for side, angs in ((-1, list(range(96, 244, 8))), (1, list(range(84, -64, -8)))):
        path = [pt(a) for a in angs]
        o.append(ink(smooth_open(path), "#6E5236", 4.4, 1503 + side, 1, 1))
        for i, a in enumerate(angs):
            px, py = pt(a)
            tang = a + 90 * (1 if side < 0 else -1)
            for sg in (-1, 1):
                la = tang + sg * 42 + rnd.uniform(-10, 10)
                o.append(green_leaf(u, px, py, rnd.uniform(36, 50), 10, la, 1510 + i * 3 + sg + (side + 1) * 50,
                                    pal=rnd.choice((SAGE, ("#8E9E7A", "#5E6E4A", "#B8C4A0"), DEEP)), vein=True))
        for j, a in enumerate(angs[1::2]):
            px, py = pt(a, R + rnd.choice((-1, 1)) * rnd.uniform(14, 22))
            o.append(f'<path d="{blob(px, py, 11, 10, 1600 + j + side * 40, 0.05, 10)}" fill="{SAGE[0]}" stroke="{SAGE[1]}" stroke-width="1.4"/>'
                     f'<path d="{blob(px - 3, py - 3, 4, 3, 1700 + j + side * 40, 0.05, 8)}" fill="{SAGE[2]}" opacity="0.8"/>')
    for i in range(30):
        a = rnd.uniform(100, 240) if i % 2 else rnd.uniform(-60, 80)
        px, py = pt(a, R + rnd.uniform(-26, 26))
        o.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="4" fill="{TERRA[0]}" stroke="{TERRA[1]}" stroke-width="1"/><circle cx="{_f(px - 1)}" cy="{_f(py - 1)}" r="1.3" fill="#FFFFFF" opacity="0.7"/>')
    flowers = [(150, 1.0, 30), (196, 1.0, 26), (30, 1.0, 30), (-16, 1.0, 26), (118, 1.03, 22), (62, 1.03, 22), (234, 0.99, 20), (-54, 0.99, 20)]
    for i, (a, rr, r) in enumerate(flowers):
        px, py = pt(a, R * rr)
        o.append(cosmos(u, px, py, r, 1620 + i, pal=CREAM, center=("#4A3A3A", "#2A1E1E", "#7A6A6A"), rot=rnd.uniform(0, 60)))
    for i, (a, r) in enumerate(((172, 17), (8, 17), (98, 15), (82, 14), (216, 13), (-36, 13), (134, 12), (46, 12))):
        px, py = pt(a, R * rnd.uniform(0.96, 1.04))
        o.append(rose(u, px, py, r, 1640 + i, pal=BLUSH if i % 2 else ROSE))
    # linen bow where the branches meet
    o.append(bow(u, cx, cy + R - 2, 30, 1660, pal=("#EEE4D2", "#BCA884", "#FFFFFF")))
    # lettering
    t, _, _ = btext(u, 300, 304, "blessed", SERIF_IT, 116, "#3E5238", ["#56704E", "#2A3A26", "#6E8A60"], 1661, max_w=300, angle=-35, shadow="#FFFFFF", soff=(0.02, 0.035))
    o.append(t)
    o.append(hand_rule(236, 284, 338, "#B49A6A", 2.2, 1662) + hand_rule(316, 364, 338, "#B49A6A", 2.2, 1663))
    o.append(f'<g transform="rotate(-6 300 336)">' + painted_heart(u, 300, 336, 9, ROSE, 1664) + "</g>")
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ family (repaint)
def boot(u, x, base, h, seed, pal, flip=False, dots=None):
    """A glossy rain boot in profile: tall shaft flaring a little at the top, rounded toe, heel and a dark sole; toe toward +x."""
    sx = -1 if flip else 1
    w = h * 0.4
    foot = h * 0.36
    X = lambda v: x + sx * v
    pts = [(X(-2), base - h), (X(w + 3), base - h), (X(w), base - h * 0.6), (X(w + 1), base - h * 0.34), (X(w + foot * 0.4), base - h * 0.27),
           (X(w + foot * 0.82), base - h * 0.2), (X(w + foot), base - h * 0.1), (X(w + foot - 3), base), (X(2), base), (X(-3), base - h * 0.12), (X(1), base - h * 0.55)]
    d = smooth_closed(pts)
    x_lo, x_hi = min(X(-6), X(w + foot + 4)), max(X(-6), X(w + foot + 4))
    extra = f'<path d="M {_f(x_lo)} {_f(base - h * 0.075)} L {_f(x_hi)} {_f(base - h * 0.075)} L {_f(x_hi)} {_f(base + 4)} L {_f(x_lo)} {_f(base + 4)} Z" fill="#3A2A24"/>'
    extra += f'<path d="M {_f(x_lo)} {_f(base - h * 0.88)} L {_f(x_hi)} {_f(base - h * 0.88)}" stroke="{pal[1]}" stroke-width="{h * 0.05:.1f}" opacity="0.55"/>'
    if dots:
        rnd = random.Random(seed)
        extra += "".join(f'<circle cx="{_f(X(rnd.uniform(5, w - 4)))}" cy="{_f(rnd.uniform(base - h * 0.84, base - h * 0.3))}" r="{h * 0.028 + 1:.1f}" fill="{dots}"/>' for _ in range(int(h / 7)))
        extra += "".join(f'<circle cx="{_f(X(w + rnd.uniform(4, foot * 0.7)))}" cy="{_f(rnd.uniform(base - h * 0.22, base - h * 0.12))}" r="{h * 0.028 + 1:.1f}" fill="{dots}"/>' for _ in range(3))
    extra += f'<path d="M {_f(X(w * 0.24))} {_f(base - h * 0.8)} L {_f(X(w * 0.24))} {_f(base - h * 0.3)}" stroke="#FFFFFF" stroke-width="{max(2.4, h * 0.035):.1f}" stroke-linecap="round" opacity="0.6"/>'
    extra += f'<path d="M {_f(X(w + foot * 0.3))} {_f(base - h * 0.22)} Q {_f(X(w + foot * 0.6))} {_f(base - h * 0.2)} {_f(X(w + foot * 0.8))} {_f(base - h * 0.15)}" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.5"/>'
    o = [form(u, d, (x_lo, base - h, x_hi, base), pal[0], pal[1], pal[2], seed + 1, -90, n=h * w / 40, shade=(sx * w * 0.2, 0), shade_op=0.45,
              ink_w=2.4, length=(h * 0.1, h * 0.3), width=(1, 2.6), extra_in=extra)]
    o.append(f'<ellipse cx="{_f(X(w / 2 + 0.5))}" cy="{_f(base - h)}" rx="{_f(w / 2 + 2.5)}" ry="{_f(h * 0.025 + 1.5)}" fill="{pal[1]}" stroke="{INK}" stroke-width="1.8"/>')
    o.append(f'<path d="M {_f(X(w * 0.5 - 6))} {_f(base - h - 1)} q 6 {_f(-h * 0.09)} 12 0" stroke="{pal[1]}" stroke-width="3.4" fill="none"/>')
    return "".join(o)


@design("family")
def family():
    u = Ids("family")
    o = [paper(u("pp"), "#D8E4EC", "#4A6070", 1701, 1.0)]
    o.append(brush((-20, -20, 620, 470), ["#E2ECF2", "#C8D8E2", "#F0F6F8"], 1702, 200, -80, (60, 160), (6, 14), (0.08, 0.2), 0.1))
    # a row of coat hooks with a scarf and an umbrella
    o.append(form(u, org_rect(-10, 256, 610, 278, 1703, 0.4, 0.1), (-10, 256, 610, 278), WOOD[0], WOOD[1], WOOD[2], 1704, 0, n=60, shade=(0, -4), ink_w=2.0))
    for x in (110, 230, 370, 490):
        o.append(f'<path d="M {x} 268 q 0 18 12 18" stroke="#5A4A3A" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="{x}" cy="268" r="5" fill="#6A5A4A"/>')
    # a striped scarf, a straw hat and the dog's leash on the hooks
    sc = smooth_closed([(218, 284), (242, 284), (250, 330), (256, 410), (238, 414), (232, 340), (224, 330), (220, 380), (204, 384), (208, 320)])
    o.append(form(u, sc, (200, 282, 258, 416), ROSE[0], ROSE[1], ROSE[2], 1705, -90, n=24, shade=(4, 0), ink_w=2.0,
                  extra_in="".join(f'<path d="M 190 {y} L 270 {y + 4}" stroke="#FBF3E4" stroke-width="6" opacity="0.85"/>' for y in (312, 340, 368, 396))))
    o.append("".join(f'<path d="M {x} {y} l 1 12" stroke="{ROSE[1]}" stroke-width="2.4" stroke-linecap="round"/>' for x, y in ((208, 382), (213, 383), (218, 382), (240, 412), (245, 413), (250, 412))))
    o.append(f'<path d="{blob(370, 306, 54, 12, 1706, 0.04, 16)}" fill="#E8C886" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M 340 304 Q 342 270 370 268 Q 398 270 400 304 Z" fill="#F2D898" stroke="{INK}" stroke-width="2"/>'
             f'<path d="M 342 296 Q 370 304 398 296" stroke="{BLUE[0]}" stroke-width="7" fill="none"/>'
             + brush((316, 266, 424, 318), ["#C8A060", "#FFF0C0"], 1707, 40, 0, (6, 16), (0.6, 1.4), (0.3, 0.6), 0.2))
    o.append(ink("M 490 278 q -22 30 -6 60 q 16 22 8 46 M 490 278 q 20 34 4 62", BERRY[0], 4, 1708, 1, 1))
    o.append(f'<path d="{org_rect(486, 382, 500, 398, 1709, 0.3, 0.3)}" fill="#B8C0C8" stroke="{INK}" stroke-width="1.6"/>')
    # floor and a woven doormat
    fl = smooth_closed([(-20, 440), (300, 436), (620, 440), (620, 640), (-20, 640)])
    o.append(form(u, fl, (-20, 432, 620, 640), "#C8A47A", "#96744E", "#E2C49A", 1708, -2, n=120, shade=None, ink_w=0, length=(40, 120), width=(1.5, 4),
                  extra_in="".join(f'<path d="M -20 {y} Q 300 {y - 4} 620 {y}" stroke="#86643E" stroke-width="2" fill="none" opacity="0.4"/>' for y in (480, 540))))
    o.append(f'<path d="{org_rect(-10, 432, 610, 446, 1709, 0.4, 0.1)}" fill="#F4F0E8" stroke="{INK}" stroke-width="1.8"/>')
    mat = soft_poly([(96, 488), (504, 488), (528, 548), (72, 548)], 1710, 0.5, 0.06)
    o.append(form(u, mat, (70, 486, 530, 550), "#C8A06A", "#8E6A3E", "#E2C08A", 1711, -90, n=200, shade=None, ink_w=2.0, length=(3, 8), width=(0.8, 1.6),
                  extra_in='<path d="M 110 496 L 490 496 L 510 540 L 90 540 Z" fill="none" stroke="#5A3A20" stroke-width="3" opacity="0.5"/>'))
    o.append(shadow(u, 300, 530, 220, 12, 0.35))
    # the boots, biggest to smallest
    o.append(boot(u, 112, 518, 166, 1712, ("#3E5672", "#26384E", "#6A86A4")) + boot(u, 88, 530, 166, 1713, ("#4E6A88", "#2E4460", "#7E9AB8")))
    o.append(boot(u, 246, 518, 140, 1714, BERRY, dots="#F6C0BA") + boot(u, 226, 530, 140, 1715, ("#D25A5C", "#9A2E34", "#F2908A"), dots="#F6C0BA"))
    o.append(boot(u, 360, 518, 104, 1716, MUST) + boot(u, 344, 530, 104, 1717, ("#F2BE58", "#C08A28", "#FFE09A")))
    o.append(boot(u, 444, 520, 68, 1718, BLUSH) + boot(u, 432, 530, 68, 1719, ("#F6CEC4", "#D49A90", "#FFE8E2")))
    # and the dog's ball
    o.append(form(u, blob(520, 520, 16, 16, 1720, 0.02, 14), (504, 504, 536, 536), "#D8E26A", "#A8B03A", "#F2F6A8", 1721, -40, n=10, shade=(3, 3), ink_w=2.0,
                  extra_in='<path d="M 506 512 Q 520 522 532 508 M 506 530 Q 520 520 534 532" stroke="#FFFFFF" stroke-width="2.4" fill="none"/>'))
    # lettering
    t, _, _ = btext(u, 300, 166, "FAMILY", BEBAS, 150, "#2E4A66", ["#3E5A78", "#1E3048", "#56728E"], 1722, max_w=440, ls=14, angle=-80, shadow="#FFFFFF", soff=(0.02, 0.03))
    o.append(t)
    t, _, _ = btext(u, 300, 230, "our favorite people", SERIF_IT, 50, "#B4483E", ["#C85A4A", "#963226"], 1723, max_w=420, angle=-35)
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ grandma's kitchen (repaint)
def cookie(u, x, y, r, seed, bite=False, rot=0):
    o = [f'<g transform="rotate({rot} {x} {y})">']
    d = blob(x, y, r, r * 0.92, seed, 0.06, 16)
    if bite:
        d = smooth_closed([p for p in blob_pts(x, y, r, r * 0.92, seed, 0.06, 18) if (p[0] - (x + r * 0.9)) ** 2 + (p[1] - (y - r * 0.5)) ** 2 > (r * 0.45) ** 2] +
                          [(x + r * 0.5, y - r * 0.4), (x + r * 0.6, y - r * 0.1), (x + r * 0.9, y)])
    rnd = random.Random(seed)
    chips = "".join(f'<path d="{blob(x + rnd.uniform(-0.6, 0.6) * r, y + rnd.uniform(-0.55, 0.55) * r, r * 0.12, r * 0.1, seed + i, 0.15, 8)}" fill="#4A2A18"/>' for i in range(7))
    o.append(form(u, d, (x - r, y - r, x + r, y + r), "#D8A060", "#A8702E", "#F2C888", seed + 1, -30, n=r * r / 20, shade=(r * 0.1, r * 0.12), shade_op=0.45, ink_w=2.0,
                  extra_in=chips + dabs((x - r, y - r, x + r, y + r), ["#F6D8A0", "#A8702E"], seed + 2, r, (0.8, 1.8), (0.4, 0.8))))
    o.append("</g>")
    return "".join(o)


@design("grandmas-kitchen")
def grandmas_kitchen():
    u = Ids("grandmas-kitchen")
    o = [paper(u("pp"), "#F6EAD0", FLECK, 1801, 1.0)]
    o.append(brush((-20, -20, 620, 440), ["#FAF0DC", "#EEDCBA", "#FFF8EA"], 1802, 200, -80, (60, 160), (6, 14), (0.08, 0.2), 0.1))
    # tile backsplash: little blue-and-white painted tiles
    tiles = []
    for j in range(5):
        for i in range(12):
            x0, y0 = -20 + i * 54, 236 + j * 44
            tiles.append(f'<path d="{org_rect(x0 + 2, y0 + 2, x0 + 52, y0 + 42, 1803 + i * 7 + j, 0.4, 0.08)}" fill="#FBF6EC" stroke="#C8BCA4" stroke-width="1.4"/>'
                         f'<path d="M {x0 + 27} {y0 + 12} l 6 10 l -6 10 l -6 -10 Z" fill="#9AB4CE" opacity="0.7"/><circle cx="{x0 + 27}" cy="{y0 + 22}" r="2.4" fill="#5E7EA0"/>')
    o.append("".join(tiles))
    o.append(glow(u, 300, 330, 230, "#FFF2D8", 0.6))
    # the counter with a gingham cloth runner
    ct = smooth_closed([(-20, 436), (300, 432), (620, 436), (620, 640), (-20, 640)])
    o.append(form(u, ct, (-20, 428, 620, 640), "#C8946A", "#8E5E3A", "#E2B48A", 1804, -2, n=160, shade=None, ink_w=2.0, length=(40, 120), width=(1.5, 4)))
    gid, gdef = gingham(u, "#C8464A", "#FBEDE4", 18, 0, 0.42)
    o.append(gdef)
    rn = smooth_closed([(-20, 452), (300, 446), (620, 452), (620, 506), (300, 512), (-20, 506)])
    o.append(form(u, rn, (-20, 444, 620, 514), "#FBEDE4", "#D8B0A4", "#FFFFFF", 1805, -2, n=60, shade=(0, -6), shade_op=0.3, ink_w=1.8, sop=(0.06, 0.16),
                  extra_in=f'<path d="{rn}" fill="url(#{gid})"/>'))
    # the cookie jar
    jx, jb, jw, jh = 270, 470, 190, 176
    o.append(shadow(u, jx + 10, jb, jw * 0.6, 10, 0.4))
    jar = smooth_closed([(jx - jw * 0.34, jb - jh), (jx + jw * 0.34, jb - jh), (jx + jw * 0.5, jb - jh * 0.72), (jx + jw * 0.5, jb - jh * 0.2), (jx + jw * 0.36, jb),
                         (jx - jw * 0.36, jb), (jx - jw * 0.5, jb - jh * 0.2), (jx - jw * 0.5, jb - jh * 0.72)])
    deco = (f'<path d="M {jx - jw} {jb - jh * 0.78} Q {jx} {jb - jh * 0.72} {jx + jw} {jb - jh * 0.78}" stroke="#5E7EA0" stroke-width="5" fill="none"/>'
            f'<path d="M {jx - jw} {jb - jh * 0.14} Q {jx} {jb - jh * 0.08} {jx + jw} {jb - jh * 0.14}" stroke="#5E7EA0" stroke-width="5" fill="none"/>')
    for i, (fx, fy) in enumerate(((jx - 62, jb - 96), (jx + 64, jb - 92), (jx - 50, jb - 46), (jx + 54, jb - 44))):
        for a in range(0, 360, 72):
            ar = math.radians(a + i * 10)
            deco += f'<ellipse cx="{_f(fx + math.cos(ar) * 7)}" cy="{_f(fy + math.sin(ar) * 7)}" rx="5.4" ry="3.6" fill="#7E9EC0" transform="rotate({a + i * 10} {_f(fx + math.cos(ar) * 7)} {_f(fy + math.sin(ar) * 7)})"/>'
        deco += f'<circle cx="{fx}" cy="{fy}" r="3" fill="#F2C24A"/>'
    o.append(form(u, jar, (jx - jw / 2, jb - jh, jx + jw / 2, jb), "#FBF5EA", "#D8CCB6", "#FFFFFF", 1806, -90, n=200, shade=(jw * 0.14, 0), shade_op=0.45,
                  hi=(jx - jw * 0.3, jb - jh * 0.55, jw * 0.05, jh * 0.2), hi_op=0.8, ink_w=2.6, ink_col="#5A4A3A", length=(14, 40), width=(1, 3), sop=(0.1, 0.25), extra_in=deco))
    t, _, _ = btext(u, jx, jb - 62, "cookies", SERIF_IT, 40, "#3E5E80", ["#4E6E90", "#2E4A6A"], 1807, max_w=118, angle=-35)
    o.append(t)
    # lid and knob
    lid = smooth_closed([(jx - jw * 0.38, jb - jh + 4), (jx - jw * 0.3, jb - jh - 18), (jx, jb - jh - 26), (jx + jw * 0.3, jb - jh - 18), (jx + jw * 0.38, jb - jh + 4)])
    o.append(form(u, lid, (jx - jw * 0.4, jb - jh - 28, jx + jw * 0.4, jb - jh + 6), "#FBF5EA", "#D8CCB6", "#FFFFFF", 1808, 0, n=30, shade=(8, 4), ink_w=2.4, ink_col="#5A4A3A",
                  extra_in=f'<path d="M {jx - jw} {jb - jh - 6} Q {jx} {jb - jh - 18} {jx + jw} {jb - jh - 6}" stroke="#5E7EA0" stroke-width="4" fill="none"/>'))
    knob = blob(jx, jb - jh - 36, 14, 12, 1809, 0.04, 12)
    o.append(form(u, knob, (jx - 14, jb - jh - 48, jx + 14, jb - jh - 24), "#7E9EC0", "#4E6E90", "#B8CCE0", 1810, -40, n=8, shade=(3, 3), ink_w=2.0, ink_col="#2E4A6A"))
    # a plate of cookies, one bitten, crumbs
    o.append(plate_simple(u, 446, 478, 84, 20, 1811))
    o.append(cookie(u, 418, 462, 30, 1812, rot=-10) + cookie(u, 470, 456, 28, 1813, rot=20) + cookie(u, 446, 438, 28, 1814, bite=True, rot=-30))
    o.append(dabs((480, 470, 540, 494), ["#D8A060", "#A8702E"], 1815, 8, (1.2, 2.4), (0.7, 1)))
    # rolling pin with flour
    o.append(f'<path d="{blob(150, 512, 90, 14, 1816, 0.2, 16)}" fill="#FFFFFF" opacity="0.7"/>')
    o.append(dabs((60, 494, 240, 530), ["#FFFFFF"], 1817, 30, (1, 2.6), (0.5, 0.9)))
    o.append(f'<g transform="rotate(-8 150 500)">'
             f'<path d="{org_rect(56, 494, 84, 506, 1818, 0.3, 0.4)}" fill="{WOOD[1]}" stroke="{INK}" stroke-width="1.8"/>'
             f'<path d="{org_rect(216, 494, 244, 506, 1819, 0.3, 0.4)}" fill="{WOOD[1]}" stroke="{INK}" stroke-width="1.8"/>'
             + form(u, org_rect(82, 484, 218, 516, 1820, 0.4, 0.4), (82, 484, 218, 516), WOOD[0], WOOD[1], WOOD[2], 1821, 0, n=30, shade=(0, -6), ink_w=2.2,
                    extra_in='<path d="M 90 490 L 210 490" stroke="#F2D2A8" stroke-width="3" opacity="0.8"/>') + "</g>")
    # lettering
    t, _, _ = btext(u, 300, 124, "Grandma's", SERIF_IT, 84, "#5A2E26", ["#7A3E30", "#3E1A14"], 1822, max_w=420, angle=-35, shadow="#FFF8EA", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 210, "KITCHEN", BEBAS, 100, "#B4483E", ["#C85A4A", "#963226", "#D8705E"], 1823, max_w=400, ls=12, angle=-80, shadow="#5A2E26", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled_c(u, 540, "MADE WITH LOVE", JOST, 24, "#5A2E26", 1824, ls=8, line_w=36, line="#B4483E"))
    o.append(finish(u))
    return "".join(o)


def plate_simple(u, cx, cy, rx, ry, seed):
    o = [shadow(u, cx + 6, cy + 8, rx * 1.05, ry * 1.1, 0.35)]
    d = blob(cx, cy, rx, ry, seed, 0.01, 30)
    o.append(form(u, d, (cx - rx, cy - ry, cx + rx, cy + ry), "#FBF5EA", "#D8CCB6", "#FFFFFF", seed + 1, 0, n=30, shade=(0, -ry * 0.2), shade_op=0.4, ink_w=2.0, ink_col="#6A5A44",
                  extra_in=f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.86:.1f}" ry="{ry * 0.8:.1f}" fill="none" stroke="#7E9EC0" stroke-width="3" opacity="0.8"/>'))
    return "".join(o)


# ================================================================ hello sunshine (repaint)
@design("hello-sunshine")
def hello_sunshine():
    u = Ids("hello-sunshine")
    o = [paper(u("pp"), "#F8E8B8", FLECK, 1901, 1.0)]
    o.append(brush((-20, -20, 620, 620), ["#FBF0C8", "#F0DCA0", "#FFF6DA"], 1902, 220, -80, (60, 160), (6, 14), (0.1, 0.22), 0.1))
    o.append(glow(u, 300, 380, 280, "#FFF6DE", 0.7))
    wx0, wy0, wx1, wy1 = 150, 264, 450, 500
    # the view: a morning sky, the sun rising over soft hills
    clip = u("wv")
    view = [f'<defs><clipPath id="{clip}"><rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/></clipPath></defs><g clip-path="url(#{clip})">']
    vg = u("vs")
    view.append(f'<defs>{lgrad(vg, [(0, "#9EC4DA"), (0.55, "#F6D8B0"), (1, "#FCE6B8")])}</defs><rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{vg})"/>')
    view.append(happy_sun(u, 300, 430, 44, 1903, rays_n=12, face=True))
    view.append(puff_cloud(u, 214, 328, 70, 20, 1904) + puff_cloud(u, 392, 304, 60, 18, 1905))
    view.append(hill(u, [(wx0 - 10, 440), (220, 424), (300, 434), (380, 420), (wx1 + 10, 434)], wy1 + 10, "#9AB27A", "#7A9460", "#BED09C", 1906))
    view.append(hill(u, [(wx0 - 10, 466), (240, 456), (360, 464), (wx1 + 10, 452)], wy1 + 10, "#7E9A58", "#56703A", "#A8C27A", 1907))
    view.append(poplar(u, 196, 460, 60, 1908) + poplar(u, 410, 456, 50, 1909))
    view.append("</g>")
    o.append("".join(view))
    # sash frame and mullions
    fr = f"M {wx0 - 18} {wy0 - 18} L {wx1 + 18} {wy0 - 18} L {wx1 + 18} {wy1 + 6} L {wx0 - 18} {wy1 + 6} Z M {wx0} {wy0} L {wx0} {wy1} L {wx1} {wy1} L {wx1} {wy0} Z"
    o.append(form(u, fr, (wx0 - 18, wy0 - 18, wx1 + 18, wy1 + 6), "#FBF7EE", "#D4CCBC", "#FFFFFF", 1910, -90, n=60, shade=(6, 6), shade_op=0.35, ink_w=2.4))
    o.append(f'<path d="M 300 {wy0} L 300 {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#FBF7EE" stroke-width="10"/>'
             f'<path d="M 300 {wy0} L 300 {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#D4CCBC" stroke-width="2" opacity="0.7" transform="translate(3 3)"/>')
    o.append(f'<path d="M {wx0 + 14} {wy0 + 100} L {wx0 + 60} {wy0 + 14} L {wx0 + 80} {wy0 + 14} L {wx0 + 34} {wy0 + 100} Z" fill="#FFFFFF" opacity="0.25"/>')
    # gingham curtains tied back
    gid, gdef = gingham(u, "#E8A22A", "#FFF6DA", 16, 0, 0.45)
    o.append(gdef)
    for sg in (-1, 1):
        ex = wx0 - 30 if sg < 0 else wx1 + 30
        inn = wx0 + 40 if sg < 0 else wx1 - 40
        cur = (f"M {ex} {wy0 - 34} L {inn} {wy0 - 34} Q {inn - sg * 6} {wy0 + 60} {ex + sg * 26} {wy0 + 150} Q {ex + sg * 40} {wy1 - 20} {ex + sg * 30} {wy1 + 30} L {ex - sg * 10} {wy1 + 30} Z")
        folds = "".join(f'<path d="M {ex + sg * f} {wy0 - 34} Q {ex + sg * f * 0.6} {wy0 + 140} {ex + sg * (f * 0.5 + 10)} {wy1 + 30}" stroke="#C8841E" stroke-width="3" fill="none" opacity="0.4"/>' for f in (16, 34, 52))
        o.append(form(u, cur, (min(ex, inn) - 12, wy0 - 36, max(ex, inn) + 12, wy1 + 32), "#FFF6DA", "#E2C88A", "#FFFFFF", 1911 + sg, -90, n=60, shade=(-sg * 6, 0), shade_op=0.3, ink_w=2.2,
                      extra_in=f'<path d="{cur}" fill="url(#{gid})"/>' + folds))
        tx = ex + sg * 34
        o.append(f'<path d="{blob(tx, wy0 + 156, 14, 8, 1914 + sg, 0.1, 10)}" fill="{BERRY[0]}" stroke="{INK}" stroke-width="1.8"/>')
    o.append(form(u, org_rect(wx0 - 60, wy0 - 46, wx1 + 60, wy0 - 32, 1916, 0.3, 0.4), (wx0 - 60, wy0 - 46, wx1 + 60, wy0 - 32), WOOD[0], WOOD[1], WOOD[2], 1917, 0, n=20, ink_w=2.0))
    # the sill with a geranium and a songbird singing good morning
    sill = org_rect(wx0 - 40, wy1 + 4, wx1 + 40, wy1 + 24, 1918, 0.4, 0.1)
    o.append(form(u, sill, (wx0 - 40, wy1 + 4, wx1 + 40, wy1 + 24), "#FBF7EE", "#D4CCBC", "#FFFFFF", 1919, 0, n=20, shade=(0, -4), ink_w=2.2))
    o.append(shadow(u, 300, wy1 + 30, 200, 10, 0.25))
    px, pb = 214, wy1 + 6
    for i, (a, L) in enumerate(((-130, 48), (-100, 58), (-70, 50), (-150, 34), (-36, 36))):
        ar = math.radians(a)
        o.append(green_leaf(u, px, pb - 40, L * 0.7, 16, a, 1920 + i, pal=LEAF))
    for i, (fx, fy) in enumerate(((px - 22, pb - 96), (px + 20, pb - 100), (px, pb - 116))):
        o.append(ink(f"M {px} {pb - 40} Q {_f((px + fx) / 2)} {_f(pb - 70)} {fx} {fy}", DEEP[1], 2.4, 1925 + i, 1, 1))
        o.append(flower_cluster(u, fx, fy, 1930 + i * 10, r=8, pal=BERRY, n=6, spread=12))
    o.append(pot(u, px, pb, 64, 52, 1940, pal=TERRA))
    o.append(songbird(u, 372, wy1 - 18, 22, 1941, pal=BLUE, flip=True, beak_open=True))
    for i, (nx, ny) in enumerate(((404, wy1 - 70), (424, wy1 - 92))):
        o.append(ink(f"M {nx} {ny} l 0 -18 l 10 -4 l 0 16", "#5A3A24", 2.4, 1942 + i, 1, 1) + f'<ellipse cx="{nx - 3}" cy="{ny}" rx="5" ry="3.6" fill="#5A3A24" transform="rotate(-20 {nx - 3} {ny})"/>'
                 f'<ellipse cx="{nx + 7}" cy="{ny - 4}" rx="5" ry="3.6" fill="#5A3A24" transform="rotate(-20 {nx + 7} {ny - 4})"/>')
    # lettering
    t, _, _ = btext(u, 300, 131, "hello", SERIF_IT, 88, "#5A3418", ["#7A4A24", "#3A2010"], 1944, max_w=300, angle=-35, shadow="#FFF8E6", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 190, "SUNSHINE", BEBAS, 78, "#D2702E", ["#E28A3E", "#A85020", "#F2A860"], 1945, max_w=420, ls=12, angle=-80, shadow="#5A3418", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ choose joy (repaint)
def balloon(u, x, y, r, seed, pal, string_to=None, rot=0):
    o = []
    if string_to:
        sx, sy = string_to
        o.append(ink(smooth_open([(x, y + r * 1.18), (x + (sx - x) * 0.3 + 10, y + r * 1.18 + (sy - y) * 0.35), (x + (sx - x) * 0.7 - 8, y + (sy - y) * 0.7), (sx, sy)]),
                     "#7A6A5A", 1.6, seed, 1, 0.9))
    d = smooth_closed([(x, y - r), (x + r * 0.85, y - r * 0.55), (x + r * 0.9, y + r * 0.2), (x + r * 0.4, y + r * 0.95), (x, y + r * 1.1), (x - r * 0.4, y + r * 0.95),
                       (x - r * 0.9, y + r * 0.2), (x - r * 0.85, y - r * 0.55)])
    o.append(f'<g transform="rotate({rot} {x} {y})">')
    o.append(form(u, d, (x - r, y - r, x + r, y + r * 1.1), pal[0], pal[1], pal[2], seed + 1, lambda px, py: math.degrees(math.atan2(py - y, px - x)) + 90, n=r * r / 10,
                  shade=(r * 0.16, r * 0.16), shade_op=0.5, ink_w=2.4, length=(r * 0.2, r * 0.5), width=(1, 3)))
    o.append(f'<path d="M {_f(x - r * 0.5)} {_f(y - r * 0.3)} Q {_f(x - r * 0.42)} {_f(y - r * 0.72)} {_f(x - r * 0.05)} {_f(y - r * 0.78)}" stroke="#FFFFFF" stroke-width="{r * 0.12:.1f}" fill="none" stroke-linecap="round" opacity="0.75"/>'
             f'<ellipse cx="{_f(x - r * 0.56)}" cy="{_f(y - r * 0.02)}" rx="{_f(r * 0.05)}" ry="{_f(r * 0.08)}" fill="#FFFFFF" opacity="0.6"/>')
    o.append(f'<path d="M {_f(x - r * 0.12)} {_f(y + r * 1.22)} L {_f(x)} {_f(y + r * 1.08)} L {_f(x + r * 0.12)} {_f(y + r * 1.22)} Z" fill="{pal[1]}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    o.append("</g>")
    return "".join(o)


@design("choose-joy")
def choose_joy():
    u = Ids("choose-joy")
    o = [bg(u, "#F6EAD6", ["#F2E0C6", "#FBF4E6", "#EED6B6"], 2001, angle=-20)]
    o.append(glow(u, 300, 240, 260, "#FFF8EA", 0.8))
    rnd = random.Random(2002)
    # confetti
    cols = [ROSE[0], MUST[0], SAGE[0], BLUE[0], TERRA[0], BLUSH[1]]
    for i in range(60):
        x, y = rnd.uniform(40, 560), rnd.uniform(40, 560)
        if 140 < x < 460 and 50 < y < 350 or 180 < x < 420 and 360 < y < 545:
            continue
        if rnd.random() < 0.5:
            o.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{rnd.uniform(6, 10):.1f}" height="{rnd.uniform(3, 5):.1f}" fill="{rnd.choice(cols)}" transform="rotate({rnd.uniform(0, 180):.0f} {_f(x)} {_f(y)})" opacity="0.85"/>')
        else:
            o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(2.4, 4.4):.1f}" fill="{rnd.choice(cols)}" opacity="0.85"/>')
    knot = (300, 332)
    balloons = [(242, 134, 46, BLUE, -8), (358, 126, 48, MUST, 8), (300, 96, 44, ROSE, 0), (198, 210, 40, SAGE, -14), (404, 206, 42, TERRA, 12),
                (300, 186, 46, BLUSH, 2), (252, 258, 33, MUST, -6), (352, 260, 34, BLUE, 6)]
    for i, (x, y, r, pal, rot) in enumerate(balloons):
        o.append(balloon(u, x, y, r, 2003 + i * 3, pal, string_to=knot, rot=rot))
    o.append(bow(u, knot[0], knot[1], 20, 2030, pal=BERRY, tails=False))
    for x, y, s_ in ((126, 104, 10), (480, 92, 12), (520, 300, 8), (88, 300, 8), (150, 370, 6), (456, 372, 7)):
        o.append(sparkle(x, y, s_, "#E8A82A", 0.9))
    # lettering
    t, _, _ = btext(u, 300, 414, "choose", SERIF_IT, 78, "#5A3418", ["#7A4A24", "#3A2010"], 2031, max_w=320, angle=-35)
    o.append(t)
    t, _, _ = btext(u, 300, 532, "JOY", BEBAS, 156, "#D2602E", ["#E2783E", "#A84420", "#F29A60"], 2032, max_w=300, ls=16, angle=-80, shadow="#5A2A18", soff=(0.025, 0.04), hi="#FFD0A0")
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ home is where the heart is
def lazy_daisy(x, y, r, col, seed, n=6, rot=0, center="#F2C24A"):
    """An embroidered lazy-daisy flower: looped chain-stitch petals around a French-knot centre."""
    o = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        bx, by = x + ca * r * 0.25, y + sa * r * 0.25
        tx, ty = x + ca * r, y + sa * r
        d = (f"M {_f(bx)} {_f(by)} Q {_f(bx + ca * r * 0.4 + nx * r * 0.38)} {_f(by + sa * r * 0.4 + ny * r * 0.38)} {_f(tx)} {_f(ty)} "
             f"Q {_f(bx + ca * r * 0.4 - nx * r * 0.38)} {_f(by + sa * r * 0.4 - ny * r * 0.38)} {_f(bx)} {_f(by)}")
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{max(2.2, r * 0.16):.1f}" stroke-linejoin="round"/>')
        o.append(f'<path d="M {_f(tx - ca * 2)} {_f(ty - sa * 2)} l {_f(ca * 3)} {_f(sa * 3)}" stroke="{col}" stroke-width="{max(2.2, r * 0.16):.1f}" stroke-linecap="round"/>')
    o.append(french_knots(x, y, r * 0.22, center, seed, 5))
    return "".join(o)


def french_knots(x, y, r, col, seed, n=5):
    rnd = random.Random(seed)
    o = []
    for _ in range(n):
        a, rr = rnd.uniform(0, 6.28), r * math.sqrt(rnd.random())
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        o.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="3.2" fill="{col}" stroke="{mixc(col, "#000000", 0.3)}" stroke-width="1"/><circle cx="{_f(px - 1)}" cy="{_f(py - 1)}" r="1" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(o)


def satin_fill(clip_id, d, box, col, ang, gap=3.2, w=2.6):
    """Satin stitch: tight parallel thread strokes clipped to a shape, with a soft sheen line."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = max(x1 - x0, y1 - y0)
    lines = []
    t = -L
    while t < L:
        lines.append(f"M {_f(cx + t)} {_f(cy - L)} L {_f(cx + t)} {_f(cy + L)}")
        t += gap
    return (f'<clipPath id="{clip_id}"><path d="{d}"/></clipPath><g clip-path="url(#{clip_id})"><path d="{d}" fill="{col}"/>'
            f'<path d="{" ".join(lines)}" stroke="{mixc(col, "#000000", 0.22)}" stroke-width="1.1" opacity="0.6" transform="rotate({ang} {_f(cx)} {_f(cy)})"/>'
            f'<path d="{" ".join(lines[::3])}" stroke="{mixc(col, "#FFFFFF", 0.35)}" stroke-width="{w * 0.5:.1f}" opacity="0.5" transform="rotate({ang} {_f(cx)} {_f(cy)}) translate(1 0)"/></g>'
            f'<path d="{d}" fill="none" stroke="{mixc(col, "#000000", 0.3)}" stroke-width="1.6"/>')


def stitch(d, col, w=3.2, dash="9 5", op=1.0):
    return (f'<path d="{d}" fill="none" stroke="{mixc(col, "#000000", 0.35)}" stroke-width="{w + 1.2:.1f}" stroke-dasharray="{dash}" stroke-linecap="round" opacity="{op * 0.35:.2f}" transform="translate(0.8 1)"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round" opacity="{op}"/>')


@design("home-is-where-the-heart-is")
def home_is_where_the_heart_is():
    u = Ids("home-is-where-the-heart-is")
    o = [bg(u, "#A8BCC8", ["#B4C6D0", "#9AB0BE", "#C0D0D8", "#8EA4B4"], 2101, fleck="#2A3A4A", angle=-25)]
    o.append(sprig_wallpaper(u, 2102, "#8EA4B4", "#C8D6DE", (-10, -10, 610, 610), 76))
    o.append(vignette(u, "#4E6274", 0.4, 0.55))
    cx, cy, R = 300, 318, 222
    # ribbon the hoop hangs from
    o.append(f'<path d="M 300 -10 L 300 74" stroke="{ROSE[1]}" stroke-width="10"/><path d="M 300 -10 L 300 74" stroke="{ROSE[0]}" stroke-width="6"/>')
    o.append(shadow(u, cx + 12, cy + 16, R + 18, R + 18, 0.35))
    # fabric with weave
    cid = u("fab")
    weave = "".join(f'<path d="M {cx - R} {y} L {cx + R} {y}" stroke="#D8CCB4" stroke-width="1" opacity="0.6"/>' for y in range(cy - R, cy + R, 5))
    weave += "".join(f'<path d="M {x} {cy - R} L {x} {cy + R}" stroke="#E8DECC" stroke-width="1" opacity="0.6"/>' for x in range(cx - R, cx + R, 5))
    o.append(f'<defs><clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{R - 8}"/></clipPath></defs>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="#F6EFE2"/><g clip-path="url(#{cid})">{weave}'
             + brush((cx - R, cy - R, cx + R, cy + R), ["#FFFFFF", "#D8CCB4"], 2103, 120, -30, (30, 90), (3, 8), (0.08, 0.2), 0.2)
             + f'<ellipse cx="{cx - 60}" cy="{cy - 80}" rx="160" ry="120" fill="#FFFFFF" opacity="0.25"/></g>')
    # the little stitched house with a heart
    hx, hb, hw, hh = 300, 268, 150, 86
    walls = poly_d([(hx - hw / 2, hb), (hx - hw / 2, hb - hh), (hx + hw / 2, hb - hh), (hx + hw / 2, hb)])
    o.append(f'<path d="{walls}" fill="#FBF4E6" opacity="0.6"/>')
    roof = poly_d([(hx - hw / 2 - 16, hb - hh + 4), (hx, hb - hh - 58), (hx + hw / 2 + 16, hb - hh + 4)])
    o.append(satin_fill(u("rf"), roof, (hx - hw / 2 - 16, hb - hh - 58, hx + hw / 2 + 16, hb - hh + 4), "#C8664A", 70))
    o.append(stitch(walls, "#5E7EA0", 3.4, "10 5"))
    door = f"M {hx - 13} {hb} L {hx - 13} {hb - 34} Q {hx} {hb - 46} {hx + 13} {hb - 34} L {hx + 13} {hb} Z"
    o.append(satin_fill(u("dr"), door, (hx - 14, hb - 46, hx + 14, hb), "#6E8A5E", 0))
    for wx in (hx - 38, hx + 38):
        win = poly_d([(wx - 12, hb - 52), (wx + 12, hb - 52), (wx + 12, hb - 28), (wx - 12, hb - 28)])
        o.append(satin_fill(u("wn"), win, (wx - 12, hb - 52, wx + 12, hb - 28), "#F2C860", 0) + stitch(f"M {wx} {hb - 52} L {wx} {hb - 28} M {wx - 12} {hb - 40} L {wx + 12} {hb - 40}", "#5E7EA0", 2, "5 3"))
    o.append(stitch(f"M {hx + 30} {hb - hh - 20} L {hx + 30} {hb - hh - 46} L {hx + 44} {hb - hh - 46} L {hx + 44} {hb - hh - 8}", "#8E5A3A", 3, "7 4"))
    hp = heart_path(hx, hb - hh - 24, 11)
    o.append(satin_fill(u("ht"), hp, (hx - 20, hb - hh - 44, hx + 20, hb - hh - 4), "#D24A4E", 30))
    o.append(stitch(f"M {hx - hw / 2 - 30} {hb + 2} Q {hx} {hb + 8} {hx + hw / 2 + 30} {hb + 2}", "#6E8A5E", 3, "8 5"))
    # vines and lazy-daisy flowers around the lower rim
    vine_l = f"M {cx - 176} {cy + 100} Q {cx - 150} {cy + 170} {cx - 40} {cy + 176}"
    vine_r = f"M {cx + 176} {cy + 100} Q {cx + 150} {cy + 170} {cx + 40} {cy + 176}"
    o.append(stitch(vine_l, "#6E8A5E", 3.4, "8 4") + stitch(vine_r, "#6E8A5E", 3.4, "8 4"))
    for i, (x, y, a) in enumerate(((cx - 162, cy + 132, -40), (cx - 120, cy + 164, -10), (cx + 162, cy + 132, 220), (cx + 120, cy + 164, 190),
                                   (cx - 70, cy + 176, 20), (cx + 70, cy + 176, 160))):
        lf, _ = leaf_shape(x, y, 22, 8, a, 2104 + i)
        o.append(satin_fill(u("lf"), lf, (x - 24, y - 24, x + 24, y + 24), "#7E9A68", a + 90))
    for i, (x, y, r, col) in enumerate(((cx - 150, cy + 104, 18, "#E8808A"), (cx + 150, cy + 104, 18, "#E8808A"), (cx - 98, cy + 158, 15, "#86A4C8"),
                                         (cx + 98, cy + 158, 15, "#86A4C8"), (cx, cy + 176, 21, "#F2A0A8"), (cx - 44, cy + 182, 11, "#F2C860"), (cx + 44, cy + 182, 11, "#F2C860"))):
        o.append(lazy_daisy(x, y, r, col, 2110 + i, rot=i * 13, center="#F2C24A" if col != "#F2C860" else "#C8664A"))
    o.append(french_knots(cx - 176, cy + 66, 10, "#B48AC8", 2120, 6) + french_knots(cx + 176, cy + 66, 10, "#B48AC8", 2121, 6))
    # lettering, stitched in thread colours
    o.append(plain(cx, 340, "HOME IS WHERE", JOST, 30, "#3E5E80", max_w=320, ls=6))
    o.append(stitch(f"M {cx - 110} 354 L {cx + 110} 354", "#3E5E80", 2.4, "6 4"))
    t, _, _ = btext(u, cx, 412, "the heart is", SERIF_IT, 70, "#C8404A", ["#D85A60", "#9A2A34", "#E8808A"], 2122, max_w=300, angle=-20, sop=(0.25, 0.6))
    o.append(t)
    # the wooden hoop and its brass screw
    hoop = f"M {cx - R} {cy} A {R} {R} 0 1 0 {cx + R} {cy} A {R} {R} 0 1 0 {cx - R} {cy} Z M {cx - R + 16} {cy} A {R - 16} {R - 16} 0 1 1 {cx + R - 16} {cy} A {R - 16} {R - 16} 0 1 1 {cx - R + 16} {cy} Z"
    o.append(form(u, hoop, (cx - R, cy - R, cx + R, cy + R), "#D8A86E", "#9A6A3A", "#F2CC98", 2123, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=200,
                  shade=None, ink_w=2.4, length=(20, 60), width=(1, 2.4), extra_in=f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="none" stroke="#9A6A3A" stroke-width="2" opacity="0.6"/>'
                  f'<path d="M {cx - R + 20} {cy - 60} A {R - 6} {R - 6} 0 0 1 {cx - 60} {cy - R + 20}" stroke="#FFF0D0" stroke-width="3" fill="none" opacity="0.7"/>'))
    o.append(form(u, org_rect(cx - 22, cy - R - 20, cx + 22, cy - R + 8, 2124, 0.3, 0.3), (cx - 22, cy - R - 20, cx + 22, cy - R + 8), "#D8B058", "#9A7428", "#F6DC92", 2125, 0, n=10, shade=(0, -3), ink_w=2.0))
    o.append(f'<path d="M {cx - 34} {cy - R - 8} L {cx + 34} {cy - R - 8}" stroke="#9A7428" stroke-width="7" stroke-linecap="round"/><circle cx="{cx + 34}" cy="{cy - R - 8}" r="7" fill="#D8B058" stroke="{INK}" stroke-width="1.8"/>')
    o.append(bow(u, cx, cy - R - 30, 22, 2126, pal=ROSE, tails=False))
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ breathe
def dandelion_head(u, cx, cy, r, seed, n=110, col="#FFFFFF"):
    """A dandelion clock: a seed-studded centre and many fine pappus stalks each ending in a little parachute."""
    rnd = random.Random(seed)
    o = [glow(u, cx, cy, r * 1.6, "#FFFFFF", 0.35)]
    stalks, chutes = [], []
    for i in range(n):
        # fibonacci-ish spread over a sphere, projected
        z = 1 - 2 * (i + 0.5) / n
        ph = i * 2.39996
        rr = math.sqrt(1 - z * z)
        dx, dy = math.cos(ph) * rr, math.sin(ph) * rr
        L = r * (0.75 + 0.25 * abs(rr))
        ex, ey = cx + dx * L, cy + dy * L
        sx, sy = cx + dx * r * 0.14, cy + dy * r * 0.14
        stalks.append(f"M {_f(sx)} {_f(sy)} L {_f(ex)} {_f(ey)}")
        a = math.atan2(dy, dx)
        for k in range(-3, 4):
            aa = a + k * 0.32
            chutes.append(f"M {_f(ex)} {_f(ey)} l {_f(math.cos(aa) * r * 0.16)} {_f(math.sin(aa) * r * 0.16)}")
    o.append(f'<path d="{" ".join(stalks)}" stroke="{col}" stroke-width="1.5" opacity="0.8"/>')
    o.append(f'<path d="{" ".join(chutes)}" stroke="{col}" stroke-width="1.3" opacity="0.75" stroke-linecap="round"/>')
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.16)}" fill="#C8A878" stroke="#7A5A3A" stroke-width="1.6"/>')
    o.append(dabs((cx - r * 0.14, cy - r * 0.14, cx + r * 0.14, cy + r * 0.14), ["#7A5A3A", "#E2C898"], seed + 1, 14, (1, 2), (0.6, 1)))
    return "".join(o)


def seed_chute(x, y, s, rot, col="#FFFFFF"):
    o = [f'<g transform="rotate({rot:.0f} {_f(x)} {_f(y)})">']
    o.append(f'<path d="M {_f(x)} {_f(y)} L {_f(x)} {_f(y + s * 1.6)}" stroke="{col}" stroke-width="1.6"/>')
    o.append(f'<path d="{blob(x, y + s * 1.8, s * 0.12, s * 0.3, int(x * 7 + y), 0.05, 8)}" fill="#8A6A44"/>')
    rays_ = " ".join(f"M {_f(x)} {_f(y)} l {_f(math.cos(math.radians(a)) * s)} {_f(math.sin(math.radians(a)) * s * 0.8)}" for a in range(-170, -9, 20))
    o.append(f'<path d="{rays_}" stroke="{col}" stroke-width="1.4" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


@design("breathe")
def breathe():
    u = Ids("breathe")
    o = [paper(u("pp"), "#DCE6D8", "#4A5E4A", 2201, 1.0)]
    o.append(sky(u, [(0, "#7E9A8E"), (0.5, "#A8BEB0"), (1, "#E2EADC")], 600, 2202, ["#94AE9E", "#C8D8CC", "#6E8A7E"], 220, angle=-8))
    o.append(glow(u, 420, 120, 260, "#FFF8E6", 0.5))
    # breeze lines
    for i, (y, x0, x1) in enumerate(((150, 260, 540), (196, 300, 560), (250, 340, 520))):
        o.append(f'<path d="M {x0} {y} Q {(x0 + x1) / 2} {y - 22} {x1} {y - 6}" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.45" stroke-dasharray="40 14"/>')
    # meadow grasses at the foot
    o.append(grass(2203, (-20, 520, 620, 610), ["#6E8A5E", "#94AE84", "#5A7650"], 220, (20, 60), 2.2))
    # the dandelion
    st = [(76, 610), (100, 520), (120, 420), (136, 330), (146, 266)]
    o.append(ink(smooth_open(st), "#6E8A4E", 5, 2204, 1, 1) + ink(smooth_open(st), "#A8C27A", 2, 2205, 1, 0.8))
    for i, (x, y, a, L) in enumerate(((92, 560, -120, 70), (102, 540, -60, 60), (86, 580, -150, 50))):
        d, tip = leaf_shape(x, y, L, 12, a, 2206 + i)
        o.append(form(u, d, (min(x, tip[0]) - 12, min(y, tip[1]) - 12, max(x, tip[0]) + 12, max(y, tip[1]) + 12), LEAF[0], LEAF[1], LEAF[2], 2207 + i, a, n=12, shade=None, ink_w=1.8, ink_col="#34461E"))
    o.append(f'<path d="{blob(146, 272, 12, 8, 2210, 0.1, 10)}" fill="#7E9A5A" stroke="#4E6232" stroke-width="1.6"/>')
    o.append(dandelion_head(u, 148, 218, 88, 2211))
    # seeds drifting away on the breeze
    rnd = random.Random(2212)
    path = [(250, 210), (316, 176), (380, 186), (444, 148), (506, 116)]
    for i in range(14):
        t = i / 13
        j = min(int(t * 4), 3)
        tt = t * 4 - j
        x = path[j][0] + (path[j + 1][0] - path[j][0]) * tt + rnd.uniform(-26, 26)
        y = path[j][1] + (path[j + 1][1] - path[j][1]) * tt + rnd.uniform(-40, 50)
        o.append(seed_chute(x, y, 10 + rnd.uniform(-2, 3), rnd.uniform(-30, 30)))
    # a few more drifting lower and further
    for x, y, r in ((420, 300, 20), (488, 260, -16), (366, 290, 8), (526, 210, 24)):
        o.append(seed_chute(x, y, 9, r))
    # lettering
    t, _, _ = btext(u, 346, 480, "breathe", SERIF_IT, 126, "#2E4A3A", ["#3E5E4A", "#1E3428", "#4E6E58"], 2213, max_w=370, angle=-30, shadow="#F2F6EC", soff=(0.02, 0.035))
    o.append(t)
    o.append(f'<path d="{blob(346, 526, 170, 22, 2215, 0.06, 16)}" fill="#EEF2E6" opacity="0.75"/>')
    o.append(ruled_c(u, 534, "INHALE · EXHALE", JOST, 26, "#1E3428", 2214, ls=8, line_w=30, line="#3E5E4A", cx=346, max_w=360))
    o.append(finish(u, "#1E3428", 0.45))
    return "".join(o)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
