"""Italia, hand-painted (gouache / storybook) edition: 30 magnets for Italian-American families, Italians abroad and
anyone who loves Italy.

Same painted idiom as the Brasil set (brasil_painted.py): warm paper, layered washes with pooled edges, brush strokes
that follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Colour story:
tomato red, basil green, Amalfi lemon yellow, majolica cobalt and turquoise, terracotta, Siena ochre, olive silver and
Venetian dusk pinks. Italian first (with the right accents), English only as a small supporting line.

Run from tools/designs:  python3 italia_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, qpts, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, stripes_in, sea, seagull
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, gingham, cloth, leaf_simple, bird_v, heart_d,
                            p_heart, steam, wood_planks, cup_saucer, stamp, branch)
import holidays_gouache as hg
import figures

COL = "italia"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
ROSSO = ("#F48A72", "#D8322A", "#7E1410")
POMO = ("#FF9A72", "#E23A26", "#8E140C")
BASIL = ("#94D46E", "#3E9A3A", "#17541E")
VERDE = ("#7CC88A", "#1E8A4C", "#0E4E2C")
OLIVA = ("#C6CEA2", "#8A9858", "#46522A")
LIMONE = ("#FFF39A", "#F8D42A", "#BE940A")
LEAFL = ("#8ACB6A", "#3A8A3A", "#1A4E1E")
COBALTO = ("#5A86D8", "#1F4BA8", "#0C2462")
TURCH = ("#8ADCD8", "#1E9CA8", "#0C5A64")
TERRA = ("#EEA27A", "#C8643C", "#7A3218")
OCRA = ("#F6CE7E", "#E0A048", "#9A6420")
SIENA = ("#E8A070", "#B8622E", "#6A3010")
CREMA = ("#FFFDF4", "#F4EAD4", "#C8B490")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
NOCE = ("#B07A4E", "#7A4A28", "#3E220E")
ALU = ("#F6F8FC", "#B4BAC4", "#5E6470")
COPPER = ("#F8BC8A", "#CA743E", "#7A3816")
PISTA = ("#C8E07A", "#8AB040", "#4A6A1A")
CHOC = ("#7A4A30", "#4A2614", "#24100A")
PINK = ("#FFC2B8", "#F08A86", "#B04A4E")
NAVY = ("#4A6A9A", "#22406E", "#0E1E3E")

lt, dk = hg.lt, hg.dk

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def finish_i(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


def pal3(c, a=0.35, b=0.35):
    return (lt(c, a), c, dk(c, b))


# ================================================================ italia toolkit
def tomato(D, cx, cy, r, seed, pal=POMO, calyx=True, rot_=0, squash=0.86):
    """A ripe tomato: soft lobes, glossy highlight, darker shoulder, a green star calyx with a short stem."""
    rnd = random.Random(seed)
    pts = []
    for i in range(30):
        a = 2 * math.pi * i / 30
        k = 1 + 0.035 * math.cos(5 * a + seed) + rnd.uniform(-0.01, 0.01)
        pts.append((cx + r * k * math.cos(a), cy + r * squash * k * math.sin(a)))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.6, 0.75), sk=0.2, angle=-40, n=int(r * 1.2), slen=(r * 0.2, r * 0.6), sw=(r * 0.03, r * 0.08),
                   cols=[pal[0], pal[2], "#FF6A4A", pal[0]], inkw=max(1.3, r * 0.045), inkop=0.7, hi=0.4, hik=0.08, curve=0.5)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k in range(5):
        a = math.radians(k * 72 + seed * 13 + rot_)
        inner.append(taper([(cx + math.cos(a) * r * 0.12, cy - r * 0.55 + math.sin(a) * r * 0.06),
                            (cx + math.cos(a) * r * 0.55, cy - r * 0.2 + math.sin(a) * r * 0.25)], max(2, r * 0.08), 1, pal[2], 0.25))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.32, r * 0.2, r * 0.11, seed + 3, 0.15, 10, -35)}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(f'<circle cx="{cx - r * 0.12:.1f}" cy="{cy - r * 0.48:.1f}" r="{max(1.2, r * 0.05):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    if calyx:
        top = (cx + math.sin(math.radians(rot_)) * r * 0.62, cy - math.cos(math.radians(rot_)) * r * squash * 0.72)
        for k in range(5):
            a = math.radians(-90 + k * 72 + rnd.uniform(-12, 12) + rot_)
            L = r * rnd.uniform(0.32, 0.46)
            tip = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.55 + L * 0.12)
            out.append(taper([top, ((top[0] + tip[0]) / 2, (top[1] + tip[1]) / 2 - 1.5), tip], max(3, r * 0.14), 0.8, "#3E7A2A"))
            out.append(taper([top, tip], max(1, r * 0.04), 0.4, "#8AC060", 0.7))
        out.append(taper([top, (top[0] + r * 0.05, top[1] - r * 0.14), (top[0] + r * 0.14, top[1] - r * 0.22)], max(3, r * 0.1), max(2, r * 0.07), "#4A6A22"))
    return "".join(out)


def basil_leaf(D, x, y, L, ang, seed, pal=BASIL, inkw=1.2, cup=0.3):
    """Sweet-basil leaf from its stalk point (x, y): ovate, cupped, glossy, with a pale midrib and side veins."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    W = L * 0.36
    right, left = [], []
    for i in range(15):
        t = i / 14
        w = W * (math.sin(math.pi * t ** 0.8) ** 0.9) * (1 - 0.15 * t)
        bend = cup * L * 0.12 * math.sin(math.pi * t)
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w * 0.92, py - ny * w * 0.92))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.16, angle=ang + 30, n=int(L * 0.5) + 6, slen=(W * 0.4, W * 1.2),
                   sw=(0.8, max(1.2, W * 0.12)), cols=[pal[0], pal[2], lt(pal[0], 0.3)], inkw=inkw, inkop=0.55, hi=0.35, hik=0.1)]
    mid = [(x + ux * L * t + nx * cup * L * 0.12 * math.sin(math.pi * t), y + uy * L * t + ny * cup * L * 0.12 * math.sin(math.pi * t)) for t in (0.02, 0.35, 0.7, 0.95)]
    out.append(taper(mid, max(1.6, L * 0.035), 0.6, lt(pal[0], 0.45), 0.85))
    for t in (0.25, 0.45, 0.65):
        px, py = mid[0][0] + ux * L * t, mid[0][1] + uy * L * t
        for sg in (-1, 1):
            w = W * math.sin(math.pi * t ** 0.8) * 0.75
            out.append(taper([(px, py), (px + ux * L * 0.12 + nx * sg * w, py + uy * L * 0.12 + ny * sg * w)], max(1, L * 0.02), 0.4, lt(pal[0], 0.35), 0.6))
    # gloss
    gx, gy = x + ux * L * 0.4 - nx * W * 0.35, y + uy * L * 0.4 - ny * W * 0.35
    out.append(taper([(gx - ux * L * 0.12, gy - uy * L * 0.12), (gx + ux * L * 0.15, gy + uy * L * 0.15)], max(1.5, W * 0.18), 0.5, "#FFFFFF", 0.45))
    return "".join(out)


def basil_sprig(D, x, y, ang, L, seed, pal=BASIL, scale=1.0):
    """A sprig of basil: a tender stem with opposite pairs of leaves, a crown of small leaves at the tip."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    stem = [(x + ux * L * t + nx * L * 0.06 * math.sin(math.pi * t), y + uy * L * t + ny * L * 0.06 * math.sin(math.pi * t)) for t in (0, 0.33, 0.66, 1)]
    out = [taper(catmull(stem, 5), max(3, 5 * scale), max(1.5, 2.4 * scale), "#5A8A3A")]
    leaves = []
    for k, t in enumerate((0.22, 0.5, 0.76)):
        px, py = x + ux * L * t + nx * L * 0.06 * math.sin(math.pi * t), y + uy * L * t + ny * L * 0.06 * math.sin(math.pi * t)
        s = (1.0 - 0.25 * t) * L * 0.62
        for sg in (-1, 1):
            leaves.append((px, py, s * rnd.uniform(0.85, 1.05), ang + sg * rnd.uniform(48, 64), seed + k * 3 + sg))
    tx, ty = stem[-1]
    for j, da in enumerate((-30, 0, 30)):
        leaves.append((tx, ty, L * 0.32, ang + da, seed + 40 + j))
    for px, py, s, aa, sd in leaves:
        out.append(basil_leaf(D, px, py, s, aa, sd, pal, inkw=1.1))
    return "".join(out)


def garlic(D, cx, cy, r, seed, rot_=0):
    """A head of garlic: plump cloves bulging under papery skin, purple-pink streaks, a dry neck and root tuft."""
    rnd = random.Random(seed)
    out = [cast(D, cx + r * 0.2, cy + r * 0.85, r * 1.1, r * 0.25, strength=0.35, seed=seed)]
    out.append(f'<g transform="rotate({rot_} {cx} {cy})">')
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        k = 1 + 0.06 * math.cos(6 * a)
        y = math.sin(a)
        yy = cy + r * 0.82 * y * (1.12 if y < 0 else 0.92)
        pts.append((cx + r * k * math.cos(a) * (0.86 if y < -0.3 else 1), yy))
    neck = [(cx - r * 0.18, cy - r * 0.86), (cx - r * 0.06, cy - r * 1.32), (cx + r * 0.02, cy - r * 1.42), (cx + r * 0.12, cy - r * 1.3), (cx + r * 0.16, cy - r * 0.86)]
    out.append(painted(D, neck, ("#FFF8EC", "#EADCC4", "#B09A78"), seed + 5, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.2, hi=0.4))
    out.append(painted(D, pts, ("#FFFDF6", "#F2E8DA", "#C2AE98"), seed, sdir=(0.7, 0.6), sk=0.16, angle=-90, n=int(r), inkw=max(1.3, r * 0.05), hi=0.5))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k in (-0.62, -0.25, 0.12, 0.5):
        x0 = cx + k * r
        inner.append(taper([(x0 + r * 0.02, cy - r * 0.8), (x0 + r * (0.18 if k < 0 else 0.1) - abs(k) * r * 0.25 * (1 if k < 0 else -1), cy), (x0 + r * 0.04, cy + r * 0.78)],
                           max(1.4, r * 0.06), 0.6, "#B8A088", 0.55))
    for _ in range(6):
        x0 = cx + rnd.uniform(-0.6, 0.6) * r
        inner.append(taper([(x0, cy - r * 0.6), (x0 + rnd.uniform(-3, 3), cy + r * 0.1), (x0 + rnd.uniform(-4, 4), cy + r * 0.6)], max(1.5, r * 0.07), 0.5,
                           rnd.choice(["#C890A8", "#B07890", "#D8A8B8"]), 0.35))
    inner.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.2, r * 0.18, r * 0.42, seed + 9, 0.1, 10, 10)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for k in range(9):
        a = math.radians(70 + k * 5)
        out.append(pline([(cx + rnd.uniform(-r * 0.15, r * 0.15), cy + r * 0.74), (cx + math.cos(a) * r * 0.3 + rnd.uniform(-3, 3), cy + r * 0.74 + r * 0.22)], "#A08A6A", 1.1, seed + k, 0.75, 1))
    out.append("</g>")
    return "".join(out)


def garlic_clove(D, cx, cy, s, seed, rot_=0):
    pts = rot([(cx - s * 0.5, cy + s * 0.3), (cx - s * 0.45, cy - s * 0.15), (cx - s * 0.1, cy - s * 0.55), (cx + s * 0.1, cy - s * 0.62),
               (cx + s * 0.35, cy - s * 0.2), (cx + s * 0.48, cy + s * 0.3), (cx, cy + s * 0.42)], cx, cy, rot_)
    return (cast(D, cx + 3, cy + s * 0.45, s * 0.6, s * 0.12, strength=0.3, seed=seed) +
            painted(D, pts, ("#FFFDF4", "#F0E4CC", "#BEA27E"), seed, sdir=(0.8, 0.5), sk=0.18, angle=-80, n=6, inkw=1.2, hi=0.45))


def olive(cx, cy, r, ang, col=("#B8B060", "#7A7A2A", "#3E3E12"), ink_c=INK):
    """A single olive: glossy ellipse with a highlight."""
    d = blob(cx, cy, r, r * 0.72, int(cx * 7 + cy), 0.03, 12, ang)
    return (f'<path d="{d}" fill="{col[1]}"/>'
            f'<path d="{blob(cx + r * 0.18, cy + r * 0.16, r * 0.8, r * 0.5, int(cx + cy), 0.05, 10, ang)}" fill="{col[2]}" opacity="0.5"/>'
            f'<path d="{blob(cx - r * 0.3, cy - r * 0.25, r * 0.32, r * 0.16, int(cx), 0.1, 8, ang - 20)}" fill="#FFFFFF" opacity="0.65"/>'
            + ink(d, ink_c, max(0.9, r * 0.1), int(cy), 1, 0.55))


def olive_leaf(D, x, y, L, ang, seed, pal=OLIVA, inkw=0.9):
    """Slender lanceolate olive leaf: grey-green top, silvery underside showing at one edge."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    W = L * 0.13
    right, left = [], []
    for i in range(11):
        t = i / 10
        w = W * math.sin(math.pi * t) ** 0.7
        right.append((x + ux * L * t + nx * w, y + uy * L * t + ny * w))
        left.append((x + ux * L * t - nx * w, y + uy * L * t - ny * w))
    pts = right + left[::-1][1:-1]
    out = [f'<path d="{smooth_closed(pts)}" fill="{pal[1]}"/>',
           f'<path d="{smooth_closed(right + [(x + ux * L * t, y + uy * L * t) for t in (1, 0.5, 0)])}" fill="{pal[0]}" opacity="0.75"/>',
           taper([(x, y), (x + ux * L * 0.9, y + uy * L * 0.9)], max(0.8, W * 0.25), 0.3, lt(pal[0], 0.4), 0.7)]
    if inkw:
        out.append(ink(smooth_closed(pts), pal[2], inkw, seed, 1, 0.55))
    return "".join(out)


def olive_branch(D, pts, seed, olives=(), w=4.5, leaves=16, pal=OLIVA, bark=("#9A8A6A", "#6A5A3E", "#3A2E1E"), L=(30, 44)):
    """Olive twig along pts, with alternate slender leaves and optional olives [(t, side, colour), ...]."""
    rnd = random.Random(seed)
    path = catmull(pts, 6)
    out = [taper(path, w, max(1.2, w * 0.35), bark[1])]
    n = len(path)
    for k in range(leaves):
        t = 0.08 + 0.9 * k / max(1, leaves - 1)
        i = min(n - 2, int(t * (n - 1)))
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        base = math.degrees(math.atan2(y1 - y0, x1 - x0))
        sg = 1 if k % 2 else -1
        out.append(olive_leaf(D, x0, y0, rnd.uniform(*L) * (1 - 0.3 * t), base + sg * rnd.uniform(28, 50), seed + k, pal))
    for (t, sg, col) in olives:
        i = min(n - 2, int(t * (n - 1)))
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        base = math.atan2(y1 - y0, x1 - x0) + sg * 1.2
        ox, oy = x0 + math.cos(base) * 12, y0 + math.sin(base) * 12 + 6
        out.append(pline([(x0, y0), (ox, oy - 6)], bark[2], 1.3, seed, 0.8, 1))
        out.append(olive(ox, oy, 8.5, math.degrees(base) + 90, col))
    return "".join(out)


def lemon_it(D, cx, cy, r, seed, rot_=0, leaf=True, pal=LIMONE):
    """An Amalfi sfusato lemon: long, bumpy, pointed nipple at each end, pores, a waxy highlight."""
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        c = math.cos(a)
        k = 1 + 0.24 * abs(c) ** 10 + 0.025 * math.sin(7 * a + seed)
        pts.append((cx + r * 1.32 * c * k, cy + r * math.sin(a) * (1 - 0.08 * abs(c))))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=-25 + rot_, n=int(r * 1.3), slen=(r * 0.3, r * 0.8), sw=(r * 0.03, r * 0.08),
                   cols=[pal[0], "#E8B812", "#FFF8C8", pal[2]], inkw=max(1.3, r * 0.05), inkop=0.65, hi=0.45, hik=0.08, curve=0.5)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    pores = "".join(f'<circle cx="{cx + rnd.uniform(-1.4, 1.4) * r:.1f}" cy="{cy + rnd.uniform(-1, 1) * r:.1f}" r="{rnd.uniform(0.5, 1.2):.1f}" fill="{rnd.choice([pal[2], "#FFFBE0"])}" opacity="0.45"/>' for _ in range(int(r * 2.5)))
    green = f'<path d="{blob(*rot([(cx + r * 1.15, cy + r * 0.1)], cx, cy, rot_)[0], r * 0.5, r * 0.6, seed + 4, 0.1, 10)}" fill="#A8B02A" opacity="0.28"/>'
    out.append(f'<g {cid}>{pores}{green}</g>')
    out.append(taper(rot([(cx - r * 0.85, cy - r * 0.05), (cx - r * 0.55, cy - r * 0.55), (cx - r * 0.05, cy - r * 0.68)], cx, cy, rot_), max(2.5, r * 0.14), 1, "#FFFDE8", 0.75))
    return "".join(out)


def citrus_leaf(D, x, y, L, ang, seed, pal=LEAFL, inkw=1.3):
    return leaf_simple(D, x, y, L, L * 0.24, ang, pal, seed, vein=True, inkw=inkw)


def majolica_tile(D, x, y, s, seed, kind=0, ground="#FBF4E2"):
    """Hand-painted southern-Italian majolica tile: cream tin glaze, cobalt corner arcs that link across tiles,
    turquoise half-moons on the edges, and a centre motif (0 = lemon with leaves, 1 = sunflower rosette)."""
    rnd = random.Random(seed)
    cx, cy = x + s / 2, y + s / 2
    g = mix(ground, rnd.choice(["#FFFFFF", "#F2E6C8"]), rnd.uniform(0.1, 0.5))
    out = [f'<path d="{hg.org_rect(x + 1, y + 1, s - 2, s - 2, seed, 0.4, 10, 2)}" fill="{g}"/>']
    b = mix(COBALTO[1], rnd.choice([COBALTO[0], COBALTO[2]]), rnd.uniform(0, 0.25))
    for (qx, qy, a0) in ((x, y, 0), (x + s, y, 90), (x + s, y + s, 180), (x, y + s, 270)):
        pts = [(qx + s * 0.3 * math.cos(math.radians(a0 + 90 * i / 8)), qy + s * 0.3 * math.sin(math.radians(a0 + 90 * i / 8))) for i in range(9)]
        out.append(taper(jitter(pts, seed + a0, s * 0.006), max(2, s * 0.05), max(2, s * 0.05), b, 0.92))
        pts2 = [(qx + s * 0.16 * math.cos(math.radians(a0 + 90 * i / 6)), qy + s * 0.16 * math.sin(math.radians(a0 + 90 * i / 6))) for i in range(7)]
        out.append(f'<path d="{pd([(qx, qy)] + pts2)}" fill="#F2A21E" opacity="0.9"/>')
    for (mx, my, a0) in ((cx, y, 0), (x + s, cy, 90), (cx, y + s, 180), (x, cy, 270)):
        pts = [(mx + s * 0.1 * math.cos(math.radians(a0 + 180 * i / 8)), my + s * 0.1 * math.sin(math.radians(a0 + 180 * i / 8))) for i in range(9)]
        out.append(f'<path d="{pd(pts)}" fill="{TURCH[1]}" opacity="0.9"/>')
    if kind == 0:
        for sg in (-1, 1):
            a = math.radians(-90 + sg * 60)
            lx, ly = cx + math.cos(a) * s * 0.06, cy - s * 0.08 + math.sin(a) * s * 0.06
            d = blob(lx + math.cos(a) * s * 0.12, ly + math.sin(a) * s * 0.12, s * 0.13, s * 0.055, seed + sg, 0.08, 10, math.degrees(a))
            out.append(f'<path d="{d}" fill="#3E8A3A"/>')
            out.append(taper([(lx, ly), (lx + math.cos(a) * s * 0.22, ly + math.sin(a) * s * 0.22)], max(1, s * 0.012), 0.4, "#A8D880", 0.8))
        lp = []
        for i in range(20):
            a = 2 * math.pi * i / 20
            c = math.cos(a)
            k = 1 + 0.25 * abs(c) ** 8
            lp.append((cx + s * 0.17 * c * k, cy + s * 0.04 + s * 0.13 * math.sin(a)))
        out.append(f'<path d="{smooth_closed(lp)}" fill="#F6C81E"/>')
        out.append(f'<path d="{blob(cx + s * 0.04, cy + s * 0.08, s * 0.14, s * 0.07, seed + 5, 0.1, 10)}" fill="#E0901A" opacity="0.6"/>')
        out.append(f'<path d="{blob(cx - s * 0.06, cy - s * 0.01, s * 0.06, s * 0.025, seed + 6, 0.1, 8, -15)}" fill="#FFF6C8" opacity="0.9"/>')
        out.append(ink(smooth_closed(lp), "#9A5A10", max(1, s * 0.012), seed, 1, 0.7))
    else:
        for k in range(8):
            a = math.radians(k * 45)
            out.append(f'<path d="{blob(cx + math.cos(a) * s * 0.13, cy + math.sin(a) * s * 0.13, s * 0.1, s * 0.045, seed + k, 0.1, 8, k * 45)}" fill="{b}"/>')
        for k in range(8):
            a = math.radians(k * 45 + 22.5)
            out.append(f'<path d="{blob(cx + math.cos(a) * s * 0.1, cy + math.sin(a) * s * 0.1, s * 0.07, s * 0.03, seed + 9 + k, 0.1, 8, k * 45 + 22.5)}" fill="#3E8A3A"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.075:.1f}" fill="#F2A21E"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.035:.1f}" fill="{dk("#F2A21E", 0.35)}"/>')
    out.append(f'<path d="{blob(x + s * 0.3, y + s * 0.24, s * 0.22, s * 0.06, seed + 50, 0.2, 10, -35)}" fill="#FFFFFF" opacity="{rnd.uniform(0.18, 0.35):.2f}"/>')
    return "".join(out)


def tile_wall(D, x0, y0, x1, y1, s, seed, kinds=(0, 1), grout="#D8CDB4", shade=True):
    out = []
    j = 0
    y = y0
    while y < y1:
        i = 0
        x = x0
        while x < x1:
            out.append(majolica_tile(D, x, y, s, seed + j * 31 + i * 7, kinds[(i + j) % len(kinds)]))
            x += s
            i += 1
        y += s
        j += 1
    for k in range(int((x1 - x0) / s) + 2):
        out.append(f'<path d="M {x0 + k * s:.1f} {y0} L {x0 + k * s + 0.6:.1f} {y1}" stroke="{grout}" stroke-width="1.8" opacity="0.85"/>')
    for k in range(int((y1 - y0) / s) + 2):
        out.append(f'<path d="M {x0} {y0 + k * s:.1f} L {x1} {y0 + k * s + 0.5:.1f}" stroke="{grout}" stroke-width="1.8" opacity="0.85"/>')
    return "".join(out)


def facet_body(D, rows, seed, cols=("#F2F4F8", "#C2C8D0", "#7E8490"), inkw=2.0):
    """An octagonal metal body (moka pot) seen face-on. rows = [(y, half_width), ...] top to bottom.
    Three visible facets: lit left, mid front, dark right; vertical brush strokes and a specular streak."""
    left = [(-hw, y) for y, hw in rows]
    right = [(hw, y) for y, hw in rows]
    out = []
    f = 0.414
    facets = [(-1, -f, cols[0]), (-f, f, cols[1]), (f, 1, cols[2])]
    outline = [(x, y) for x, y in left] + [(x, y) for x, y in right[::-1]]
    for a, b, c in facets:
        poly = [(a * hw, y) for y, hw in rows] + [(b * hw, y) for y, hw in rows[::-1]]
        out.append((poly, c))
    return outline, out


def moka(D, cx, base, h, seed, flame_glow=True):
    """Stovetop moka pot: octagonal aluminium boiler and collector, screw waist, faceted lid with a black knob,
    a pointed pour spout, an angular black handle and a little brass safety valve. base = bottom of the boiler."""
    w = h * 0.5
    out = [cast(D, cx + 12, base + 6, w * 0.75, 10, strength=0.5, seed=seed)]
    yb, yw = base, base - h * 0.4
    yc = yw - h * 0.065
    yt = base - h * 0.86
    ylid = yt - h * 0.04
    # handle behind body, right
    hp = [(cx + w * 0.44, yt + h * 0.04), (cx + w * 0.62, yt + h * 0.02), (cx + w * 0.7, yt + h * 0.08), (cx + w * 0.66, yt + h * 0.3),
          (cx + w * 0.52, yc - h * 0.04), (cx + w * 0.38, yc - h * 0.02), (cx + w * 0.4, yc - h * 0.1), (cx + w * 0.52, yc - h * 0.12),
          (cx + w * 0.56, yt + h * 0.24), (cx + w * 0.58, yt + h * 0.1), (cx + w * 0.44, yt + h * 0.12)]
    out.append(painted(D, hp, ("#4A4650", "#1E1C22", "#060608"), seed + 1, sdir=(1, 0.3), sk=0.15, angle=-80, n=14, inkw=1.8, inkc="#060608", hi=0.35))
    out.append(taper([(cx + w * 0.62, yt + h * 0.06), (cx + w * 0.64, yt + h * 0.2), (cx + w * 0.56, yc - h * 0.08)], 3, 1, "#8A8894", 0.7))
    # spout, left
    sp = [(cx - w * 0.4, yt + h * 0.015), (cx - w * 0.66, yt - h * 0.035), (cx - w * 0.6, yt + h * 0.0), (cx - w * 0.42, yt + h * 0.13)]
    out.append(painted(D, sp, ALU, seed + 2, sdir=(0.3, 1), sk=0.2, angle=-20, n=8, inkw=1.8, hi=0.5))
    out.append(pline([(cx - w * 0.64, yt - h * 0.03), (cx - w * 0.45, yt + h * 0.06)], "#FFFFFF", 1.6, seed, 0.8, 1))

    def chamber(rows, sd):
        outline, facets = facet_body(D, rows, sd)
        res = []
        sh = [(cx + x, y) for x, y in outline]
        d = smooth_closed(sh) if False else pd(sh)
        cid = D.clip(f'<path d="{d}"/>')
        inner = []
        for poly, c in facets:
            inner.append(f'<path d="{pd([(cx + x, y) for x, y in poly])}" fill="{c}"/>')
        y0, y1 = rows[0][0], rows[-1][0]
        inner.append(strokes(D.nid(), d, (cx - w, y0, cx + w, y1), ["#FFFFFF", "#9AA0AC", "#DDE2EA", "#6A707C"], sd, n=int(h * 0.35), angle=-90,
                             length=((y1 - y0) * 0.2, (y1 - y0) * 0.6), width=(0.8, 2.4), opacity=(0.15, 0.4), curve=0.03))
        mid_hw = rows[len(rows) // 2][1]
        inner.append(taper([(cx - mid_hw * 0.7, y0 + 4), (cx - mid_hw * 0.72, (y0 + y1) / 2), (cx - mid_hw * 0.66, y1 - 4)], max(3, w * 0.06), max(2, w * 0.03), "#FFFFFF", 0.85))
        inner.append(taper([(cx + mid_hw * 0.2, y0 + 6), (cx + mid_hw * 0.22, y1 - 6)], max(2, w * 0.03), 1, "#FFFFFF", 0.4))
        if flame_glow and y1 >= base - 2:
            inner.append(f'<rect x="{cx - w}" y="{y1 - h * 0.12:.1f}" width="{2 * w}" height="{h * 0.12:.1f}" fill="{D.lin([(0, "#4A8AF0", 0), (1, "#4A8AF0", 0.45)])}"/>')
        res.append(f'<g {cid}>{"".join(inner)}</g>')
        for a in (-0.414, 0.414):
            res.append(pline([(cx + a * rows[0][1], rows[0][0]), (cx + a * rows[-1][1], rows[-1][0])], "#5A606C", 1.2, sd, 0.55, 1))
        res.append(ink(d, INK, 2, sd, 2, 0.75))
        return "".join(res)
    # boiler: slight foot flare, then tapering to the waist
    out.append(chamber([(yw, w * 0.33), (yb - h * 0.06, w * 0.48), (yb - h * 0.015, w * 0.5), (yb, w * 0.48)], seed + 3))
    # valve on the boiler
    vx, vy = cx - w * 0.36, base - h * 0.17
    out.append(painted(D, rect_pts(vx - 9, vy - 6, vx + 2, vy + 6, 5, seed, 0.3), ("#F6DC8A", "#C8A040", "#7A5A14"), seed + 4, sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(f'<circle cx="{vx - 9:.1f}" cy="{vy:.1f}" r="3.4" fill="#A88830" stroke="{INK}" stroke-width="1"/>')
    # collector: collar then widening upward
    out.append(chamber([(yt, w * 0.47), (yc - h * 0.02, w * 0.36), (yc, w * 0.36)], seed + 5))
    out.append(chamber([(yc, w * 0.38), (yw, w * 0.37)], seed + 6))
    out.append(pline([(cx - w * 0.36, yc + h * 0.02), (cx + w * 0.36, yc + h * 0.022)], "#5A606C", 1.2, seed, 0.5, 1))
    out.append(pline([(cx - w * 0.36, yc + h * 0.04), (cx + w * 0.36, yc + h * 0.042)], "#5A606C", 1.2, seed + 1, 0.5, 1))
    # lid
    lid = [(cx - w * 0.49, yt + 2), (cx - w * 0.44, ylid), (cx - w * 0.2, ylid - h * 0.025), (cx + w * 0.2, ylid - h * 0.025), (cx + w * 0.44, ylid), (cx + w * 0.49, yt + 2)]
    out.append(painted(D, lid, ALU, seed + 7, sdir=(0.8, 0.5), sk=0.18, angle=0, n=10, inkw=1.8, hi=0.55))
    out.append(pline([(cx - w * 0.49, yt + 2), (cx + w * 0.49, yt + 3)], "#5A606C", 1.6, seed, 0.6, 1))
    kn = [(cx - w * 0.09, ylid - h * 0.02), (cx - w * 0.07, ylid - h * 0.07), (cx - w * 0.03, ylid - h * 0.085), (cx + w * 0.03, ylid - h * 0.085),
          (cx + w * 0.07, ylid - h * 0.07), (cx + w * 0.09, ylid - h * 0.02)]
    out.append(painted(D, kn, ("#5A5660", "#1E1C22", "#060608"), seed + 8, sdir=(1, 0.3), sk=0.2, angle=-90, n=5, inkw=1.4, inkc="#060608", hi=0.4))
    return "".join(out)


def gas_flames(D, cx, cy, rx, ry, seed, front=True, h=(10, 16)):
    """A ring of little blue gas flames on a burner seen slightly from above (front or back half)."""
    rnd = random.Random(seed)
    out = []
    a0, a1 = (10, 170) if front else (190, 350)
    for k in range(13):
        a = math.radians(a0 + (a1 - a0) * k / 12)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        hh = rnd.uniform(*h)
        lean = math.cos(a) * 3
        d = smooth_closed([(x - 3.2, y), (x - 2.4, y - hh * 0.5), (x + lean, y - hh), (x + 2.4, y - hh * 0.5), (x + 3.2, y)])
        out.append(f'<path d="{d}" fill="#3A7AF0" opacity="0.8"/>')
        out.append(f'<path d="{smooth_closed([(x - 1.6, y), (x - 1, y - hh * 0.35), (x + lean * 0.4, y - hh * 0.6), (x + 1, y - hh * 0.35), (x + 1.6, y)])}" fill="#BFE2FF" opacity="0.9"/>')
    return "".join(out)


def burner(D, cx, cy, rx, seed, lit=True):
    """Gas hob burner seen from slightly above: dark cast cap, the ring, a four-arm iron grate."""
    ry = rx * 0.28
    out = []
    if lit:
        out.append(D.glow(cx, cy - 4, rx * 1.6, "#6AA8FF", 0.45, ry=rx * 0.6))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 3, rx * 1.12, ry * 1.2, 0, 360, 24))}" fill="#2A2A30" opacity="0.35"/>')
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 24), ("#5A5A64", "#2A2A32", "#0E0E12"), seed, sdir=(0.3, 1), sk=0.2, angle=0, n=8, inkw=1.2, inkc="#0E0E12", hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy - 2, rx * 0.62, ry * 0.6, 0, 360, 20))}" fill="#16161A"/>')
    out.append(f'<path d="{smooth_open(ell_pts(cx, cy - 2, rx * 0.62, ry * 0.6, 200, 340, 10))}" stroke="#8A8A96" stroke-width="1.4" fill="none" opacity="0.7"/>')
    if lit:
        out.append(gas_flames(D, cx, cy - 2, rx * 0.66, ry * 0.62, seed, front=False))
    return "".join(out)


def grate_arms(D, cx, cy, rx, seed, front=True):
    ry = rx * 0.28
    out = []
    angs = (30, 150) if front else (210, 330)
    for a in angs:
        r = math.radians(a)
        x0, y0 = cx + math.cos(r) * rx * 0.45, cy + math.sin(r) * ry * 0.45 - 8
        x1, y1 = cx + math.cos(r) * rx * 1.25, cy + math.sin(r) * ry * 1.25
        out.append(taper([(x0, y0), (x1, y1 - 6), (x1, y1 + 4)], 6, 6, "#1A1A1E"))
        out.append(taper([(x0, y0 - 1.5), (x1, y1 - 7.5)], 1.6, 1.2, "#7A7A86", 0.8))
    return "".join(out)


def cypress(D, x, base, h, seed, pal=("#5E8A4A", "#2E5232", "#14281A"), light=1, w=None, rim=None):
    """Italian cypress: a tall flame of dense foliage painted with upward dabs, lit on one side."""
    rnd = random.Random(seed)
    w = w or h * 0.17
    pts = []
    for i in range(17):
        t = i / 16
        prof = math.sin(math.pi * min(1, (t * 0.95 + 0.05))) ** 0.6 * (1 - t) ** 0.35
        hw = w / 2 * (0.55 + 0.6 * prof) * (1 - t ** 1.6) + 0.6
        pts.append((x + hw * rnd.uniform(0.9, 1.08), base - h * t))
    pts = pts + [(x - (px - x) * rnd.uniform(0.9, 1.08), py) for px, py in pts[::-1][1:]]
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for _ in range(int(h * 0.9)):
        t = rnd.random() ** 0.9
        y = base - h * t
        side = rnd.uniform(-1, 1)
        xx = x + side * w * 0.5
        lit = side * light
        c = pal[0] if lit > 0.25 else (pal[2] if lit < -0.25 else pal[1])
        if rim and lit > 0.65 and rnd.random() < 0.5:
            c = rim
        L = rnd.uniform(h * 0.03, h * 0.07)
        inner.append(taper([(xx, y + L), (xx + rnd.uniform(-1.5, 1.5), y)], max(1.4, w * 0.12), 0.6, c, rnd.uniform(0.6, 0.95)))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, pal[2], max(0.8, w * 0.04), seed, 1, 0.45))
    return "".join(out)


def facade(D, x0, x1, top, base, seed, wall, shutters="#2E6A4A", rows=3, cols=3, arch=False, lit=0.0, roof=True, haze=0.0,
           balcony=None, door=True, sill="#F4ECDC", ink_w=1.4):
    """An Italian house front: painted plaster wall, rows of windows with louvred shutters (persiane), stone sills,
    optional arched (Venetian) windows lit from inside, a clay-tile eave and a door."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D2E2", haze)) if haze else (lambda c: c)
    w, h = x1 - x0, base - top
    out = [painted(D, rect_pts(x0, top, x1, base, 18, seed, 0.6), (hz(lt(wall, 0.25)), hz(wall), hz(dk(wall, 0.25))), seed, sdir=(1, 0.3), sk=0.06,
                   angle=-80, n=max(8, int(w * h / 160)), inkw=ink_w, inkop=0.5, hi=0.2)]
    if roof:
        out.append(f'<path d="{hg.org_rect(x0 - 5, top - 7, w + 10, 9, seed + 1, 0.4, 10, 1)}" fill="{hz("#A8462A")}"/>')
        out.append(f'<path d="M {x0 - 5} {top + 2} L {x1 + 5} {top + 2.5}" stroke="{hz("#5A2010")}" stroke-width="1.6" opacity="0.6"/>')
    gh = h * (0.82 if door else 0.94) / rows
    gw = w / cols
    for j in range(rows):
        for i in range(cols):
            wx = x0 + gw * (i + 0.5)
            wy = top + h * 0.06 + gh * (j + 0.5)
            ww_, wh_ = gw * 0.34, gh * 0.56
            on = rnd.random() < lit
            glass = hz("#FFD27A") if on else hz(rnd.choice(["#2E3440", "#3A3A48", "#2A3038"]))
            if arch:
                wp = [(wx - ww_ / 2, wy + wh_ / 2), (wx - ww_ / 2, wy - wh_ * 0.15)] + \
                     [(wx + ww_ / 2 * math.cos(math.radians(180 - 180 * k / 8)), wy - wh_ * 0.15 - ww_ / 2 * math.sin(math.radians(180 - 180 * k / 8)) * 1.1) for k in range(1, 8)] + \
                     [(wx + ww_ / 2, wy - wh_ * 0.15), (wx + ww_ / 2, wy + wh_ / 2)]
                out.append(f'<path d="{smooth_closed(jitter(wp, seed + i * 7 + j, 0.3))}" fill="{hz("#F4ECDC")}" transform="translate(0 0)" stroke="{hz("#F4ECDC")}" stroke-width="5"/>')
                out.append(f'<path d="{smooth_closed(jitter(wp, seed + i * 7 + j, 0.3))}" fill="{glass}"/>')
                if on:
                    out.append(D.glow(wx, wy, ww_ * 1.4, "#FFC860", 0.35))
                out.append(pline([(wx, wy - wh_ * 0.5), (wx, wy + wh_ / 2)], hz("#4A3A2A"), 1.2, seed, 0.7, 1))
            else:
                out.append(f'<rect x="{wx - ww_ / 2:.1f}" y="{wy - wh_ / 2:.1f}" width="{ww_:.1f}" height="{wh_:.1f}" fill="{glass}"/>')
                if on:
                    out.append(D.glow(wx, wy, ww_ * 1.3, "#FFC860", 0.3))
                # louvred shutters, one or both open
                for sg in (-1, 1):
                    if rnd.random() < 0.18:
                        continue
                    sx = wx + sg * (ww_ / 2 + ww_ * 0.26)
                    sp = rect_pts(sx - ww_ * 0.25, wy - wh_ / 2, sx + ww_ * 0.25, wy + wh_ / 2, 8, seed + i + j * 5 + sg, 0.25)
                    out.append(f'<path d="{smooth_closed(sp)}" fill="{hz(shutters)}"/>')
                    for k in range(1, int(wh_ / 4)):
                        yy = wy - wh_ / 2 + k * 4
                        out.append(f'<path d="M {sx - ww_ * 0.22:.1f} {yy:.1f} L {sx + ww_ * 0.22:.1f} {yy:.1f}" stroke="{hz(dk(shutters, 0.35))}" stroke-width="0.9"/>')
                    out.append(ink(smooth_closed(sp), hz(dk(shutters, 0.5)), 0.9, seed, 1, 0.6))
            out.append(f'<path d="{hg.org_rect(wx - ww_ / 2 - 3, wy + wh_ / 2, ww_ + 6, 3.4, seed + i, 0.2, 6, 0.5)}" fill="{hz(sill)}"/>')
            if balcony and j == 0 and i == cols // 2:
                out.append(f'<path d="M {wx - ww_ * 0.9:.1f} {wy + wh_ / 2 + 3:.1f} L {wx + ww_ * 0.9:.1f} {wy + wh_ / 2 + 3:.1f}" stroke="{hz("#2A2A2A")}" stroke-width="2"/>')
                for k in range(9):
                    bx = wx - ww_ * 0.9 + k * ww_ * 1.8 / 8
                    out.append(f'<path d="M {bx:.1f} {wy + wh_ / 2 + 3:.1f} l 0 {-gh * 0.25:.1f}" stroke="{hz("#2A2A2A")}" stroke-width="1.2"/>')
                out.append(f'<path d="M {wx - ww_ * 0.9:.1f} {wy + wh_ / 2 + 3 - gh * 0.25:.1f} L {wx + ww_ * 0.9:.1f} {wy + wh_ / 2 + 3 - gh * 0.25:.1f}" stroke="{hz("#2A2A2A")}" stroke-width="1.6"/>')
                for k in range(5):
                    out.append(f'<circle cx="{wx - ww_ * 0.8 + k * ww_ * 0.4:.1f}" cy="{wy + wh_ / 2 - gh * 0.2:.1f}" r="{max(2, gw * 0.05):.1f}" fill="{hz(balcony)}"/>')
    if door:
        dx = x0 + w * rnd.uniform(0.3, 0.55)
        dw, dh = min(gw * 0.42, 22), h * 0.16
        out.append(f'<path d="{hg.org_rect(dx, base - dh, dw, dh, seed + 30, 0.3, 6, 1)}" fill="{hz(rnd.choice(["#5A3A22", "#2E4A3A", "#3A2A1E"]))}"/>')
    return "".join(out)


def string_lights(D, x0, y0, x1, y1, sag, n, seed, col="#FFE29A", wire="#3A2A1E", r=4.2):
    """Festoon of warm bulbs with soft glows along a sagging wire."""
    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
    out = [ink(smooth_open([pt(i / 30) for i in range(31)]), wire, 1.6, seed, 1, 0.9)]
    for i in range(n):
        x, y = pt((i + 0.5) / n)
        out.append(D.glow(x, y + r * 1.4, r * 5, col, 0.45))
        out.append(f'<rect x="{x - r * 0.45:.1f}" y="{y - 1:.1f}" width="{r * 0.9:.1f}" height="{r * 0.7:.1f}" fill="{wire}"/>')
        out.append(f'<path d="{blob(x, y + r * 1.3, r * 0.85, r * 1.05, seed + i, 0.05, 10)}" fill="{col}"/>')
        out.append(f'<circle cx="{x - r * 0.25:.1f}" cy="{y + r:.1f}" r="{r * 0.35:.1f}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def checks_band(D, d, col, base="#FFFDF6", cell=14, rot_=0, op=0.62):
    return gingham(D, d, col, base, cell, rot_, op)


# ================================================================ 1. la moka — the pot on the flame, two cups waiting
@design("la-moka")
def la_moka():
    D = Doc2("itmk")
    out = [sky(D, [(0, "#FBF0DA"), (1, "#F2DEBA")], 3, 600, ["#FFFFFF", "#E8CDA0", "#FFF6E2"], 90, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(11, ["#E8C890", "#FFFFFF", "#F2D2A8"], 6, (0, 0, 600, 240), (90, 160), (0.06, 0.12)))
    # majolica splash-back
    out.append(tile_wall(D, -24, 236, 624, 424, 64, 101))
    out.append(f'<rect x="0" y="236" width="600" height="188" fill="{D.lin([(0, "#1A0E04", 0), (0.7, "#1A0E04", 0.05), (1, "#1A0E04", 0.25)])}"/>')
    out.append(painted(D, rect_pts(-10, 226, 610, 238, 30, 102, 0.5), ("#E88A5A", "#C0582E", "#7A2E14"), 102, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.4, hi=0.3))
    out.append(soft_glow(D, 180, 260, 260, "#FFF2C8", 0.35))
    # white enamel stove top with a chrome back edge
    out.append(f'<path d="M -10 424 L 610 424 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#F4F0E8"), (0.6, "#E6E0D4"), (1, "#C8C0B2")])}"/>')
    out.append(strokes(D.nid(), "M -10 424 L 610 424 L 610 610 L -10 610 Z", (-40, 424, 610, 600), ["#FFFFFF", "#D8D0C0", "#C8BEAE"], 103, n=70,
                       angle=0, length=(60, 180), width=(2, 6), opacity=(0.12, 0.3), curve=0.05))
    out.append(painted(D, rect_pts(-10, 418, 610, 432, 30, 104, 0.4), ("#FFFFFF", "#C8CCD4", "#6A707C"), 104, sdir=(0, 1), sk=0.25, angle=0, n=30, inkw=1.4, hi=0.6))
    # reflections of the pot and window light on the enamel
    out.append(f'<path d="{blob(196, 540, 90, 12, 105, 0.1, 14)}" fill="#FFFFFF" opacity="0.4"/>')
    # burner
    out.append(burner(D, 196, 508, 100, 106, lit=True))
    out.append(grate_arms(D, 196, 508, 100, 107, front=False))
    # the moka
    out.append(moka(D, 196, 498, 292, 111))
    out.append(gas_flames(D, 196, 506, 66, 19, 112, front=True, h=(9, 15)))
    out.append(grate_arms(D, 196, 508, 100, 113, front=True))
    # coffee rising: steam curling from the spout
    out.append(steam(124, 236, 60, 114, "#FFFFFF", 2, 18, 6, 0.75))
    # two espresso cups and a little plate of cantucci on the right
    out.append(cast(D, 474, 452, 70, 12, strength=0.35, seed=120))
    out.append(painted(D, ell_pts(472, 444, 66, 17, 0, 360, 28), WHITE, 121, sdir=(0.4, 1), sk=0.15, angle=0, n=12, inkw=1.6, hi=0.4))
    out.append(ink(smooth_open(ell_pts(472, 445, 58, 13, 15, 165, 14)), ROSSO[1], 2.2, 122, 1, 0.85))
    for k, (x, y, a) in enumerate(((444, 434, -12), (480, 428, 8), (504, 440, -4))):
        pts = rot([(x - 24, y + 6), (x - 20, y - 6), (x + 20, y - 8), (x + 26, y + 4), (x, y + 10)], x, y, a)
        out.append(painted(D, pts, ("#F6D8A0", "#DCA65A", "#8A5A22"), 123 + k, sdir=(0.4, 1), sk=0.2, angle=a, n=8, inkw=1.3, hi=0.45))
        rr = random.Random(130 + k)
        for j in range(5):
            out.append(f'<path d="{blob(x + rr.uniform(-16, 16), y + rr.uniform(-4, 5), 2.6, 2, j + k * 9, 0.2, 6)}" fill="#C8A070" stroke="#8A5A2A" stroke-width="0.8"/>')
    out.append(cup_saucer(D, 384, 540, 80, 115, rim=COBALTO))
    out.append(cup_saucer(D, 496, 520, 72, 116, rim=ROSSO, handle=-1))
    out.append(steam(384, 468, 44, 117, "#FFFFFF", 2, 20, 5, 0.65))
    out.append(steam(496, 454, 36, 118, "#FFFFFF", 2, 18, 5, 0.6))
    out.append(taper([(420, 540), (440, 533), (466, 522)], 3.6, 2, "#8A8E98"))
    out.append(taper([(420, 539), (466, 521)], 1, 0.6, "#FFFFFF", 0.8))
    out.append(painted(D, rect_pts(326, 530, 340, 544, 4, 119, 0.4), ("#FFFFFF", "#F4F0EA", "#B8B0A6"), 119, sk=0.25, n=2, inkw=1, hi=0.5))
    # lettering
    out.append(letters(D, 318, 146, "la moka", SERIF_IT, 122, "#8A2E16", ["#B0461E", "#6A1E0C", "#C8582A"], 120, max_w=400,
                       shadow="#F2C890", soff=(0.02, 0.035), angle=-40, hi="#F2A878"))
    out.append(ruled(330, 193, "PRIMA IL CAFFÈ", "#1F4BA8", font=JOS, size=24, ls=6, line_w=30, gap=14, max_w=280))
    return finish_i(D, out, 121)


# ================================================================ 2. il sugo della domenica — the pot, the spoon, the steam
def meatball(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    out = [painted(D, blob_pts(cx, cy, r, r * 0.9, seed, 0.08, 14), ("#B07050", "#7A3E26", "#3E1A0C"), seed, sdir=(0.6, 0.8), sk=0.22, angle=-40,
                   n=int(r), inkw=1.2, inkop=0.6, hi=0.35)]
    for _ in range(int(r * 0.8)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.8)
        out.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr * 0.9:.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="{rnd.choice(["#C89070", "#4A200E", "#5A8A3A"])}" opacity="0.7"/>')
    return "".join(out)


def stock_pot(D, cx, rim_y, rx, ry, depth, seed, body=ALU, contents=None):
    """A big pot in 3/4 view: rim ellipse at rim_y, straight sides, two loop handles; `contents(d)` paints the
    surface inside the rim (receives the inner-ellipse path)."""
    out = [cast(D, cx + 14, rim_y + depth + 6, rx * 1.12, ry * 0.7, strength=0.5, seed=seed)]
    for sg in (-1, 1):
        hx = cx + sg * rx
        hp = f"M {hx:.1f} {rim_y + depth * 0.12:.1f} q {sg * 34:.1f} {-2:.1f} {sg * 34:.1f} {depth * 0.16:.1f} q 0 {depth * 0.14:.1f} {-sg * 34:.1f} {depth * 0.14:.1f}"
        out.append(ink(hp, body[2], 11, seed + sg, 1, 1) + ink(hp, body[1], 6, seed + sg, 1, 1) + ink(hp, body[0], 2, seed + sg, 1, 0.8))
    side = [(cx - rx, rim_y)] + ell_pts(cx, rim_y + depth, rx, ry, 180, 0, 20) + [(cx + rx, rim_y)]
    side = [(cx - rx, rim_y)] + [(x, y) for x, y in ell_pts(cx, rim_y + depth, rx, ry, 180, 0, 20)][::-1][::-1] + [(cx + rx, rim_y)]
    sp = [(cx + rx, rim_y)] + ell_pts(cx, rim_y + depth, rx, ry, 0, 180, 20) + [(cx - rx, rim_y)] + ell_pts(cx, rim_y, rx, ry, 180, 360, 20)[1:-1]
    d = smooth_closed(sp)
    out.append(f'<path d="{d}" fill="{body[1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<rect x="{cx - rx}" y="{rim_y - ry}" width="{2 * rx}" height="{depth + 2 * ry}" fill="{D.lin([(0, body[0]), (0.25, body[1]), (0.7, dk(body[1], 0.25)), (1, body[2])], 0, 0, 1, 0)}"/>',
             strokes(D.nid(), d, (cx - rx, rim_y, cx + rx, rim_y + depth + ry), [body[0], dk(body[1], 0.15)], seed, n=int(rx * 0.25), angle=-90,
                     length=(depth * 0.5, depth * 1.0), width=(1, 2.4), opacity=(0.08, 0.2), curve=0.01),
             f'<rect x="{cx + rx * 0.25:.1f}" y="{rim_y}" width="{rx * 0.12:.1f}" height="{depth + ry}" fill="#FFFFFF" opacity="0.25"/>',
             f'<rect x="{cx - rx * 0.92:.1f}" y="{rim_y}" width="{rx * 0.08:.1f}" height="{depth + ry}" fill="{body[2]}" opacity="0.18"/>',
             taper([(cx - rx * 0.62, rim_y + 10), (cx - rx * 0.64, rim_y + depth * 0.6), (cx - rx * 0.6, rim_y + depth + ry * 0.6)], 8, 3, "#FFFFFF", 0.55),
             f'<path d="{smooth_open(ell_pts(cx, rim_y + depth * 0.3, rx + 2, ry, 0, 180, 20))}" stroke="{body[2]}" stroke-width="1.6" fill="none" opacity="0.4"/>']
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, INK, 2.2, seed, 2, 0.75))
    # rim and inside
    outer = ell_pts(cx, rim_y, rx, ry, 0, 360, 36)
    out.append(f'<path d="{smooth_closed(outer)}" fill="{body[0]}"/>')
    inn = ell_pts(cx, rim_y + 2, rx - 7, ry - 5, 0, 360, 36)
    di = smooth_closed(inn)
    out.append(f'<path d="{di}" fill="{body[2]}"/>')
    if contents:
        out.append(contents(cx, rim_y + 2, rx - 7, ry - 5, di))
    out.append(ink(smooth_closed(outer), INK, 1.8, seed + 2, 1, 0.7))
    out.append(taper(ell_pts(cx, rim_y, rx - 2, ry - 1.5, 200, 340, 14), 2.2, 2.2, "#FFFFFF", 0.8))
    return "".join(out)


def wooden_spoon(D, x0, y0, x1, y1, seed, bowl=True, w=11):
    """Olive-wood spoon from handle end (x0, y0) to bowl (x1, y1)."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    out = [f'<g transform="translate({x0} {y0}) rotate({ang:.1f})">']
    handle = [(0, -w * 0.45), (L * 0.75, -w * 0.32), (L * 0.75, w * 0.32), (0, w * 0.45), (-w * 0.4, 0)]
    out.append(painted(D, handle, ("#F2CC92", "#C8904E", "#7A4E22"), seed, sdir=(0, 1), sk=0.25, angle=0, n=14, slen=(20, 60), sw=(0.6, 1.6), inkw=1.6, hi=0.45))
    if bowl:
        b = blob_pts(L * 0.88, 0, L * 0.15, w * 1.5, seed + 1, 0.04, 16)
        out.append(painted(D, b, ("#F2CC92", "#C8904E", "#7A4E22"), seed + 1, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append("</g>")
    return "".join(out)


@design("il-sugo-della-domenica")
def il_sugo():
    D = Doc2("itsg")
    # warm terracotta-rose kitchen wall, light from the upper left
    out = [sky(D, [(0, "#F4D2B4"), (1, "#E8B48E")], 5, 600, ["#FFE6CC", "#D89870", "#F8DCC0"], 100, angle=-75, sop=(0.06, 0.16))]
    out.append(blooms(13, ["#D88A60", "#FFF0DC", "#E8A07A"], 7, (0, 0, 600, 420), (90, 170), (0.06, 0.12)))
    out.append(soft_glow(D, 140, 140, 320, "#FFF4D8", 0.45))
    # marble counter
    cnt = "M -10 404 L 610 404 L 610 610 L -10 610 Z"
    out.append(f'<path d="{cnt}" fill="{D.lin([(0, "#F6F2EA"), (1, "#DCD4C6")])}"/>')
    rnd = random.Random(7)
    for k in range(9):
        y = 410 + rnd.uniform(0, 190)
        x = rnd.uniform(-40, 560)
        out.append(pline([(x, y), (x + 60, y + rnd.uniform(-14, 14)), (x + 120, y + rnd.uniform(-20, 20)), (x + 200, y + rnd.uniform(-20, 20))], rnd.choice(["#B8B0A8", "#A8A098", "#C8C0B6"]), rnd.uniform(0.8, 1.8), k, 0.55, 1))
    out.append(painted(D, rect_pts(-10, 398, 610, 412, 30, 130, 0.4), ("#FFFFFF", "#ECE6DA", "#B0A898"), 130, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.2, hi=0.5))
    # folded checked cloth under the pot
    out.append(cloth(D, [(120, 436), (470, 424), (500, 470), (488, 560), (140, 572), (104, 510)], "#D8322A", 131, cell=13, rot_=-4,
                     folds=[((200, 440), (210, 500), (196, 566)), ((400, 430), (418, 500), (410, 560))]))

    def sauce(cx, cy, rx, ry, di):
        res = [f'<path d="{di}" fill="#A8180E"/>']
        cid = D.clip(f'<path d="{di}"/>')
        r2 = random.Random(9)
        inner = [f'<path d="{blob(cx - rx * 0.1, cy - ry * 0.05, rx * 0.8, ry * 0.7, 3, 0.1, 16)}" fill="#C8281A"/>',
                 strokes(D.nid(), di, (cx - rx, cy - ry, cx + rx, cy + ry), ["#E04A2A", "#8A0E08", "#D8381E"], 11, n=90, angle=-8,
                         length=(10, 34), width=(1.5, 4), opacity=(0.25, 0.6), curve=0.6)]
        # meatballs and a couple of sausage pieces poking through
        for k, (mx, my, r) in enumerate(((-0.45, -0.05, 22), (-0.1, 0.25, 24), (0.32, -0.12, 21), (0.12, -0.42, 18), (0.58, 0.28, 19))):
            inner.append(f'<path d="{blob(cx + mx * rx + 3, cy + my * ry + 5, r * 1.05, r * 0.5, k, 0.1, 12)}" fill="#6A0A06" opacity="0.6"/>')
            inner.append(meatball(D, cx + mx * rx, cy + my * ry - r * 0.25, r, 140 + k))
            inner.append(f'<path d="{blob(cx + mx * rx, cy + my * ry + r * 0.35, r * 1.05, r * 0.35, k + 9, 0.12, 12)}" fill="#B81E12"/>')
        for k, (sx, sy) in enumerate(((-0.62, 0.32), (0.4, 0.5))):
            inner.append(painted(D, blob_pts(cx + sx * rx, cy + sy * ry, 18, 9, 150 + k, 0.08, 12, 20), ("#C87050", "#8A3A22", "#4A1A0A"), 150 + k, sk=0.2, n=4, inkw=1, hi=0.4))
        # bubbles and glossy oil
        for k in range(16):
            bx, by = cx + r2.uniform(-0.8, 0.8) * rx, cy + r2.uniform(-0.7, 0.7) * ry
            br = r2.uniform(2.5, 6)
            inner.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{br:.1f}" ry="{br * 0.6:.1f}" fill="#7A0806" opacity="0.6"/>'
                         f'<path d="M {bx - br * 0.7:.1f} {by - br * 0.1:.1f} q {br * 0.7:.1f} {-br * 0.8:.1f} {br * 1.4:.1f} 0" stroke="#FF8A5A" stroke-width="1.3" fill="none" opacity="0.8"/>')
        for k in range(10):
            bx, by = cx + r2.uniform(-0.8, 0.8) * rx, cy + r2.uniform(-0.7, 0.7) * ry
            inner.append(f'<path d="{blob(bx, by, r2.uniform(3, 7), r2.uniform(1.4, 3), k + 30, 0.2, 8)}" fill="#FFB060" opacity="0.55"/>')
        inner.append(basil_leaf(D, cx + rx * 0.05, cy + ry * 0.02, 34, -20, 160))
        inner.append(basil_leaf(D, cx - rx * 0.25, cy + ry * 0.45, 26, 200, 161))
        inner.append(f'<path d="{blob(cx, cy - ry * 0.95, rx * 1.1, ry * 0.35, 5, 0.05, 16)}" fill="#3A0604" opacity="0.45"/>')
        res.append(f'<g {cid}>{"".join(inner)}</g>')
        return "".join(res)
    out.append(stock_pot(D, 300, 352, 172, 52, 132, 132, contents=sauce))
    out.append(wooden_spoon(D, 492, 236, 350, 352, 133, bowl=False, w=17))
    out.append(steam(290, 300, 80, 134, "#FFFFFF", 3, 44, 8, 0.6))
    # around the pot: tomatoes on the vine, garlic, basil
    out.append(pline([(70, 470), (92, 452), (118, 448), (142, 456)], "#4A7A2A", 3.2, 135, 1, 1))
    for k, (tx, ty, r) in enumerate(((90, 496, 30), (134, 510, 26), (100, 526, 21))):
        out.append(cast(D, tx + 8, ty + r * 0.75, r, r * 0.25, strength=0.35, seed=136 + k))
        out.append(tomato(D, tx, ty, r, 137 + k, rot_=[-14, 10, 4][k]))
    out.append(garlic(D, 500, 506, 26, 140, rot_=8))
    out.append(garlic_clove(D, 456, 532, 16, 141, rot_=-30))
    out.append(basil_sprig(D, 534, 470, 160, 60, 142))
    # lettering
    out.append(letters(D, 300, 152, "il sugo", SERIF_IT, 114, "#9A1A10", ["#C8281A", "#6E0E08", "#D8402A"], 143, max_w=400,
                       shadow="#FFF0DC", soff=(0.02, 0.035), angle=-40, hi="#FF9A7A"))
    out.append(ruled(300, 198, "DELLA DOMENICA", "#1E6A3A", font=JOS, size=24, ls=6, line_w=36, gap=14, max_w=320))
    return finish_i(D, out, 144)


# ================================================================ 3. cannoli — on a majolica-framed panel
def cannolo(D, cx, cy, L, r, ang, seed, ends=("pista", "choc")):
    """One cannolo seen from the side: a fried, blistered golden shell tube with slightly flared ends, and creamy
    ricotta bulging out of each end, studded with pistachio crumbs, chocolate chips or a candied cherry."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({ang} {cx} {cy})">']
    out.append(cast(D, cx + 6, cy + r * 1.1, L * 0.58, r * 0.32, strength=0.4, seed=seed))
    shell_pal = ("#FCE2AA", "#E2A85E", "#9A5A22")
    x0, x1 = cx - L / 2, cx + L / 2
    # ricotta mounds first (the shell rim overlaps their base)
    for sg, kind in ((-1, ends[0]), (1, ends[1])):
        ex = cx + sg * (L / 2 - r * 0.2)
        mound = [(ex, cy - r * 0.92)] + [(ex + sg * r * 1.05 * math.sin(math.radians(t)), cy - r * 0.92 * math.cos(math.radians(t)) * (1 - 0.06 * math.sin(math.radians(t * 3))))
                                         for t in range(20, 180, 20)] + [(ex, cy + r * 0.9)]
        md = smooth_closed(mound)
        out.append(painted(D, mound, ("#FFFFFF", "#FBF4E4", "#D2C2A2"), seed + 3 + sg, sdir=(0.2, 1), sk=0.2, angle=-60, n=14, inkw=1.4, hi=0.5))
        mcid = D.clip(f'<path d="{md}"/>')
        tp = []
        for _ in range(16):
            px, py = ex + sg * rnd.uniform(0.1, 0.8) * r, cy + rnd.uniform(-0.8, 0.8) * r
            tp.append(f'<path d="{blob(px, py, rnd.uniform(2, 4), rnd.uniform(1.4, 2.6), rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#FFFFFF", "#E8DCC4"])}" opacity="0.8"/>')
        for _ in range(34 if kind in ("pista", "choc") else 10):
            px, py = ex + sg * rnd.uniform(0.2, 1.0) * r, cy + rnd.uniform(-0.85, 0.85) * r
            if kind == "pista" or kind == "cherry":
                tp.append(f'<path d="{blob(px, py, rnd.uniform(1.8, 3.6), rnd.uniform(1.4, 2.6), rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#8AB040", "#A8C858", "#5A8A2A", "#C8D870"])}"/>')
            else:
                tp.append(f'<path d="{blob(px, py, rnd.uniform(2, 3.4), rnd.uniform(1.6, 2.6), rnd.randint(1, 999), 0.25, 6)}" fill="{rnd.choice(["#3A1A0A", "#5A2A12", "#24100A"])}"/>')
        out.append(f'<g {mcid}>{"".join(tp)}</g>')
        if kind == "cherry":
            out.append(painted(D, blob_pts(ex + sg * r * 0.62, cy - r * 0.1, r * 0.3, r * 0.28, seed + 7, 0.05, 10), ("#FF8A8A", "#D8142A", "#7A0412"), seed + 7, sk=0.2, n=3, inkw=1.1, hi=0.6))
            out.append(f'<circle cx="{ex + sg * r * 0.55:.1f}" cy="{cy - r * 0.22:.1f}" r="{r * 0.08:.1f}" fill="#FFFFFF" opacity="0.85"/>')
    # cylinder shell: straight sides, rounded ends, vertical gradient (lit from above)
    k = r * 0.32
    shell = [(x0 + k, cy - r)] + [(x0 + k - k * math.sin(math.radians(t)), cy - r * math.cos(math.radians(t))) for t in range(15, 180, 15)] + \
            [(x0 + k, cy + r), (x1 - k, cy + r)] + [(x1 - k + k * math.sin(math.radians(t)), cy + r * math.cos(math.radians(t))) for t in range(15, 180, 15)] + [(x1 - k, cy - r)]
    d = pd(shell)
    out.append(f'<path d="{d}" fill="{D.lin([(0, "#FCDC9A"), (0.3, "#F0B25E"), (0.7, "#CC8238"), (1, "#7E4416")])}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [strokes(D.nid(), d, (x0 - 10, cy - r, x1, cy + r), ["#FFEFC8", "#C0803E", "#E8B470"], seed, n=int(L * 0.35), angle=0,
                     length=(L * 0.08, L * 0.25), width=(1, 2.6), opacity=(0.15, 0.4), curve=0.05)]
    for _ in range(int(L * r / 18)):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(cy - r, cy + r)
        br = rnd.uniform(1.6, 4.4)
        lit = (cy - by) / r
        c = "#FFF2D2" if lit > 0.3 else (rnd.choice(["#F2C680", "#EAB66C"]) if lit > -0.4 else "#C08040")
        inner.append(f'<path d="{blob(bx, by, br, br * 0.7, rnd.randint(1, 9999), 0.2, 8)}" fill="{c}" opacity="0.9"/>'
                     f'<path d="M {bx - br * 0.7:.1f} {by + br * 0.4:.1f} q {br * 0.7:.1f} {br * 0.55:.1f} {br * 1.4:.1f} 0" stroke="#9A5A22" stroke-width="0.9" fill="none" opacity="0.45"/>')
    for _ in range(int(L * 0.1)):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(cy, cy + r)
        inner.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="#7A3A12" opacity="0.45"/>')
    inner.append(taper([(x0 + r * 0.4, cy - r * 0.62), (cx, cy - r * 0.68), (x1 - r * 0.4, cy - r * 0.62)], max(3, r * 0.16), max(2, r * 0.08), "#FFF8E4", 0.7))
    for _ in range(int(L * 1.1)):
        bx, by = rnd.uniform(x0, x1), cy - r + abs(rnd.gauss(0, r * 0.3))
        inner.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{rnd.uniform(0.5, 1.3):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#6A3A14", 1.8, seed, 2, 0.75))
    # the crisp shell lips at each end
    for sg in (-1, 1):
        ex = cx + sg * (L / 2 - k * 0.9)
        out.append(pline([(ex - sg * k * 0.2, cy - r * 0.96), (ex + sg * k * 0.55, cy), (ex - sg * k * 0.2, cy + r * 0.96)], "#A8682A", 2, seed + sg, 0.7, 1))
    out.append("</g>")
    return "".join(out)


@design("cannoli")
def cannoli():
    D = Doc2("itcn")
    out = [paper(D.nid(), "#FBF2DE", FLECK, 151)]
    # majolica frame bleeding off the edge
    s = 60
    for i in range(10):
        for (x, y) in ((i * s, 0), (i * s, 540)):
            out.append(majolica_tile(D, x, y, s, 152 + i * 3 + y, (i + y // s) % 2))
    for j in range(1, 9):
        for x in (0, 540):
            out.append(majolica_tile(D, x, j * s, s, 190 + j * 5 + x, (j + x // s) % 2))
    out.append(f'<path d="M 60 60 L 540 60 L 540 540 L 60 540 Z" fill="none" stroke="#1F4BA8" stroke-width="4"/>')
    out.append(f'<path d="M 66 66 L 534 66 L 534 534 L 66 534 Z" fill="none" stroke="#F2A21E" stroke-width="2"/>')
    out.append(f'<path d="M 66 66 L 534 66 L 534 534 L 66 534 Z" fill="{D.rad([(0, "#FFFFFF", 0.5), (1, "#FFFFFF", 0)], r=0.6)}"/>')
    out.append(blooms(14, ["#F2D8A8", "#FFFFFF"], 4, (100, 100, 500, 500), (80, 140), (0.08, 0.14)))
    # plate, seen from a little above, scalloped with a yellow/cobalt rim
    cx, cy, rx, ry = 300, 392, 196, 92
    out.append(cast(D, cx + 10, cy + 24, rx + 6, ry * 0.9, strength=0.35, seed=153))
    sc = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        k = 1 + 0.025 * math.cos(a * 18)
        sc.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    out.append(painted(D, sc, ("#FFFFFF", "#F8F2E6", "#C8C0B2"), 154, sdir=(0.5, 1), sk=0.08, angle=0, n=40, inkw=1.8, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, cy - 2, rx - 14, ry - 8, 0, 360, 40)), "#1F4BA8", 4, 155, 1, 0.9))
    for i in range(24):
        a = 2 * math.pi * i / 24
        px, py = cx + (rx - 6) * math.cos(a), cy + (ry - 3) * math.sin(a)
        out.append(f'<path d="{blob(px, py, 6, 3.2, 156 + i, 0.15, 8, math.degrees(a) + 90)}" fill="#F2A21E" opacity="0.9"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 2, rx - 30, ry - 22, 0, 360, 40))}" fill="#F2ECE0"/>')
    # dusting of sugar on the plate
    out.append(specks(157, (cx - rx * 0.7, cy - ry * 0.5, cx + rx * 0.7, cy + ry * 0.6), ["#FFFFFF"], 120, (0.6, 1.6), (0.5, 0.95)))
    # three cannoli: two below, one on top
    out.append(cannolo(D, 226, 414, 150, 36, -14, 158, ("pista", "choc")))
    out.append(cannolo(D, 376, 420, 150, 36, 12, 159, ("choc", "cherry")))
    out.append(cannolo(D, 300, 352, 160, 38, -4, 160, ("pista", "pista")))
    # a few pistachios and chips scattered
    rnd = random.Random(161)
    for k in range(9):
        x, y = rnd.uniform(110, 490), rnd.uniform(470, 520)
        if abs(x - 300) < 60 and y < 490:
            continue
        out.append(f'<path d="{blob(x, y, 4, 2.8, k, 0.3, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(["#8AB040", "#5A8A2A", "#3A1A0A"])}"/>')
    # lettering
    out.append(letters(D, 300, 196, "cannoli", SERIF_IT, 128, "#1F4BA8", ["#2E62C8", "#0C2462", "#4A7AD8"], 162, max_w=400,
                       shadow="#F2C870", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 246, "SICILIA · CON AMORE", "#B8461E", font=JOS, size=21, ls=5, line_w=24, gap=12, max_w=320))
    return finish_i(D, out, 163)


# ================================================================ 4. limoncello — a lemon branch over the Amalfi sea
def bottle(D, cx, base, h, seed, liquid=("#FFF27A", "#F2D21A", "#B89A08"), glass="#E8F4E8"):
    """Tall clear bottle with a cork, liquid inside, a hand-tied paper tag and string, highlights."""
    w = h * 0.3
    neck_w = w * 0.3
    out = [cast(D, cx + 10, base + 2, w * 0.8, 8, strength=0.45, seed=seed)]
    body = [(cx - w / 2, base - 6), (cx - w / 2, base - h * 0.55), (cx - w * 0.42, base - h * 0.64), (cx - neck_w / 2, base - h * 0.74),
            (cx - neck_w / 2, base - h * 0.93), (cx + neck_w / 2, base - h * 0.93), (cx + neck_w / 2, base - h * 0.74), (cx + w * 0.42, base - h * 0.64),
            (cx + w / 2, base - h * 0.55), (cx + w / 2, base - 6), (cx + w * 0.4, base), (cx - w * 0.4, base)]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{glass}" opacity="0.55"/>')
    cid = D.clip(f'<path d="{d}"/>')
    ly = base - h * 0.6
    liq = f"M {cx - w}  {ly} Q {cx} {ly + 4} {cx + w} {ly} L {cx + w} {base + 4} L {cx - w} {base + 4} Z"
    inner = [f'<path d="{liq}" fill="{liquid[1]}" opacity="0.92"/>',
             f'<rect x="{cx - w}" y="{ly - 4}" width="{2 * w}" height="{h}" fill="{D.lin([(0, liquid[0], 0.6), (0.3, liquid[0], 0), (0.75, liquid[2], 0.25), (1, liquid[2], 0.6)], 0, 0, 1, 0)}"/>',
             f'<path d="M {cx - w} {ly} Q {cx} {ly + 4} {cx + w} {ly}" stroke="#FFFBD8" stroke-width="2.4" fill="none"/>',
             taper([(cx - w * 0.32, base - h * 0.08), (cx - w * 0.34, base - h * 0.5), (cx - w * 0.1, base - h * 0.72), (cx - neck_w * 0.2, base - h * 0.9)], 6, 2, "#FFFFFF", 0.75),
             taper([(cx + w * 0.34, base - h * 0.1), (cx + w * 0.36, base - h * 0.5)], 3, 1, "#FFFFFF", 0.45)]
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#4A5A4A", 1.8, seed, 2, 0.7))
    cork = rect_pts(cx - neck_w * 0.46, base - h * 1.0, cx + neck_w * 0.46, base - h * 0.9, 5, seed, 0.3)
    out.append(painted(D, cork, ("#E8C08A", "#B8864E", "#6A4420"), seed + 1, sk=0.2, n=6, inkw=1.4, hi=0.4))
    out.append(specks(seed, (cx - neck_w * 0.4, base - h * 0.99, cx + neck_w * 0.4, base - h * 0.91), ["#6A4420"], 8, (0.6, 1.2), (0.5, 0.9)))
    # string and paper tag
    out.append(pline([(cx - neck_w / 2, base - h * 0.86), (cx, base - h * 0.84), (cx + neck_w / 2, base - h * 0.86)], "#C8B48A", 1.6, seed, 1, 1))
    tag = rot(rect_pts(cx + neck_w * 0.2, base - h * 0.8, cx + w * 0.62, base - h * 0.66, 6, seed, 0.4), cx + neck_w * 0.4, base - h * 0.84, 18)
    out.append(pline([(cx + neck_w * 0.4, base - h * 0.85), (cx + w * 0.3, base - h * 0.8)], "#C8B48A", 1.3, seed, 1, 1))
    out.append(painted(D, tag, ("#FFFDF0", "#F2E6C8", "#B8A27A"), seed + 2, sk=0.15, n=4, inkw=1.1, hi=0.4))
    tx, ty = bbox(tag)[0] + 8, (bbox(tag)[1] + bbox(tag)[3]) / 2
    out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.4" fill="none" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def frosty_glass(D, cx, base, h, seed, liquid=("#FFF27A", "#F2D21A", "#B89A08")):
    """Small chilled stemmed glass, frosted at the top, with limoncello."""
    w = h * 0.62
    out = [cast(D, cx + 6, base + 1, w * 0.6, 5, strength=0.4, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 2, w * 0.38, 4, 0, 360, 16))}" fill="#E8F2EC" stroke="#6A7A6A" stroke-width="1.2"/>')
    out.append(f'<path d="M {cx - 2} {base - 3} L {cx - 2.5} {base - h * 0.32} L {cx + 2.5} {base - h * 0.32} L {cx + 2} {base - 3} Z" fill="#E8F2EC" stroke="#6A7A6A" stroke-width="1.1"/>')
    cup = [(cx - w / 2, base - h), (cx - w * 0.44, base - h * 0.62), (cx - w * 0.2, base - h * 0.36), (cx, base - h * 0.32), (cx + w * 0.2, base - h * 0.36),
           (cx + w * 0.44, base - h * 0.62), (cx + w / 2, base - h)]
    d = smooth_closed(cup)
    out.append(f'<path d="{d}" fill="#EEF6F0" opacity="0.6"/>')
    cid = D.clip(f'<path d="{d}"/>')
    ly = base - h * 0.84
    rnd = random.Random(seed)
    frost = "".join(f'<circle cx="{cx + rnd.uniform(-w / 2, w / 2):.1f}" cy="{rnd.uniform(base - h, base - h * 0.5):.1f}" r="{rnd.uniform(0.5, 1.4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(int(w * 1.5)))
    out.append(f'<g {cid}><rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{liquid[1]}"/>'
               f'<rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{D.lin([(0, liquid[0], 0.6), (0.4, liquid[0], 0), (1, liquid[2], 0.5)], 0, 0, 1, 0)}"/>'
               f'<path d="M {cx - w} {ly} L {cx + w} {ly}" stroke="#FFFBD8" stroke-width="2"/>{frost}'
               f'{taper([(cx - w * 0.3, base - h * 0.95), (cx - w * 0.28, base - h * 0.55)], 4, 1.5, "#FFFFFF", 0.7)}</g>')
    out.append(ink(d, "#5A6A5A", 1.5, seed, 2, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w / 2, 4, 0, 360, 16))}" fill="none" stroke="#5A6A5A" stroke-width="1.3" opacity="0.8"/>')
    return "".join(out)


def stacked_town(D, x0, x1, base, top, seed, cols, haze=0.4, n=26):
    """A cliff village (Positano / Amalfi): little pastel cubes stacked up a slope, tiny dark windows."""
    rnd = random.Random(seed)
    out = []
    items = []
    for k in range(n):
        x = rnd.uniform(x0, x1)
        t = (x - x0) / max(1, x1 - x0)
        ytop = base - (base - top) * (1 - abs(t - 0.4) * 1.4) * rnd.uniform(0.3, 1.0)
        w, h = rnd.uniform(10, 18), rnd.uniform(9, 14)
        items.append((ytop, x, w, h))
    for ytop, x, w, h in sorted(items):
        c = mix(rnd.choice(cols), "#C8D8E8", haze)
        out.append(f'<path d="{hg.org_rect(x, ytop, w, h, rnd.randint(1, 999), 0.3, 6, 1)}" fill="{c}"/>')
        out.append(f'<path d="M {x + w:.1f} {ytop:.1f} l 3 -1.5 l 0 {h:.1f} l -3 1.5 Z" fill="{dk(c, 0.2)}"/>')
        if rnd.random() < 0.8:
            out.append(f'<rect x="{x + w * 0.3:.1f}" y="{ytop + h * 0.35:.1f}" width="2.2" height="3" fill="{mix("#3A3A4A", "#C8D8E8", haze * 0.6)}"/>')
        if rnd.random() < 0.5:
            out.append(f'<rect x="{x + w * 0.65:.1f}" y="{ytop + h * 0.35:.1f}" width="2.2" height="3" fill="{mix("#3A3A4A", "#C8D8E8", haze * 0.6)}"/>')
    return "".join(out)


@design("limoncello")
def limoncello():
    D = Doc2("itlc")
    out = [sky(D, [(0, "#9ED2EE"), (0.55, "#D6EEF4"), (1, "#FFF2D6")], 3, 330, ["#FFFFFF", "#B8E0F2", "#E6F6FA"], 70, angle=-3, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 120, 120, 200, "#FFFBE0", 0.6))
    # coast: a headland at left with a stacked village, the sea, distant cape
    out.append(hill(D, ridge([(-20, 300), (120, 250), (240, 266), (330, 296)], 171, 12, 4) + [(340, 312)], 340, ("#A8B8C8", "#8A9CB4", "#6A7A98"), 172, inkw=0, n=40))
    out.append(hill(D, ridge([(380, 300), (500, 282), (620, 270)], 173, 8, 3), 330, ("#B8C4D2", "#9EAAC0", "#8090AA"), 174, inkw=0, n=20))
    out.append(stacked_town(D, 20, 230, 312, 252, 175, ["#F6D8A0", "#F2B8A0", "#FFFFFF", "#F6E8C8", "#E8A8A0", "#F8E0A8"], haze=0.25, n=34))
    out.append(sea(D, 306, 470, [(0, "#3A9ACB"), (0.5, "#1E6EAA"), (1, "#16508A")], 176, ["#6AC0E8", "#0E3E70", "#FFFFFF"], 90, ticks=["#FFFFFF", "#A8E0F6"]))
    # tiny boat with a wake
    out.append(painted(D, [(390, 356), (430, 356), (424, 364), (396, 364)], WHITE, 177, sk=0.2, n=3, inkw=1, hi=0.5))
    out.append(taper([(388, 362), (350, 366), (300, 368)], 3, 1, "#FFFFFF", 0.7))
    # whitewashed terrace wall in front, with a strip of majolica tiles
    out.append(painted(D, rect_pts(-10, 444, 610, 610, 30, 178, 0.6), ("#FFFFFF", "#F2EDE4", "#C8C0B4"), 178, sdir=(0.3, 1), sk=0.06, angle=0, n=60, inkw=0, hi=0.3))
    for j in range(2):
        for i in range(11):
            out.append(majolica_tile(D, -20 + i * 58, 486 + j * 58, 58, 179 + i + j * 13, (i + j) % 2))
    for y in (486, 544, 602):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#D8CDB4" stroke-width="2"/>')
    for i in range(12):
        out.append(f'<path d="M {-20 + i * 58} 486 L {-20 + i * 58} 610" stroke="#D8CDB4" stroke-width="2"/>')
    out.append(f'<rect x="0" y="486" width="600" height="124" fill="{D.lin([(0, "#3A2A1A", 0.22), (0.25, "#3A2A1A", 0), (1, "#3A2A1A", 0.1)])}"/>')
    out.append(painted(D, rect_pts(-10, 432, 610, 452, 30, 180, 0.5), ("#FFFFFF", "#EEE8DE", "#B8B0A2"), 180, sdir=(0, 1), sk=0.3, angle=0, n=20, inkw=1.6, hi=0.6))
    out.append(f'<rect x="-10" y="452" width="620" height="10" fill="#6A5A48" opacity="0.18"/>')
    # bottle and glass on the ledge, one lemon resting by them
    out.append(bottle(D, 178, 444, 252, 181))
    out.append(frosty_glass(D, 270, 444, 80, 182))
    out.append(lemon_it(D, 350, 420, 25, 183, rot_=-8))
    out.append(lemon_it(D, 106, 428, 18, 187, rot_=14))
    out.append(citrus_leaf(D, 372, 398, 44, -30, 184))
    # lemon branch arching in from the top right
    bp = catmull([(640, 30), (560, 60), (500, 108), (452, 170), (432, 230)], 6)
    out.append(branch(D, bp, 12, 5, 185, ("#9A8A62", "#6A5A3A", "#3A3020")))
    for k, (x, y, L, a) in enumerate(((600, 40, 66, 150), (560, 60, 70, -40), (520, 92, 64, 200), (500, 108, 62, -10), (470, 150, 60, 210),
                                      (456, 170, 58, 20), (440, 214, 52, 160), (578, 50, 56, 100), (480, 130, 50, 260))):
        out.append(citrus_leaf(D, x, y, L, a, 186 + k))
    for k, (x, y, r, ang) in enumerate(((528, 168, 34, 78), (462, 262, 31, 90), (580, 128, 28, 70))):
        out.append(pline([(x + 6, y - r * 1.2), (x + 2, y - r * 0.9)], "#5A6A2A", 2.4, k, 1, 1))
        out.append(lemon_it(D, x, y, r, 190 + k, rot_=ang))
    out.append(citrus_leaf(D, 520, 128, 44, 110, 194))
    # blossoms
    for k, (x, y) in enumerate(((430, 226), (510, 96))):
        for j in range(5):
            a = math.radians(j * 72 + k * 20)
            out.append(f'<path d="{blob(x + math.cos(a) * 5, y + math.sin(a) * 5, 5, 3.2, 195 + k * 7 + j, 0.1, 8, math.degrees(a))}" fill="#FFFFFF" stroke="#C8B8A8" stroke-width="0.8"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#F2C21C"/>')
    # lettering
    out.append(letters(D, 236, 128, "limoncello", SERIF_IT, 104, "#F6CC1C", ["#FFE46A", "#E0A808", "#FFF2A0"], 196, max_w=360,
                       shadow="#1E5A8A", soff=(0.018, 0.032), angle=-40, hi="#FFFBE0"))
    out.append(ruled(236, 170, "COSTIERA AMALFITANA", "#1E4E8A", font=JOS, size=18, ls=4, line_w=20, gap=10, max_w=330))
    return finish_i(D, out, 197)


# ================================================================ 5. toscana — cypress road to the farmhouse at golden hour
def casale(D, x, base, w, h, seed, tower=True):
    """A Tuscan farmhouse: warm stone walls in 3/4 view, low terracotta roofs, a little dovecote tower."""
    out = []
    stone = ("#F2D0A0", "#D8A870", "#9A6A3A")
    sw_ = w * 0.4
    side = [(x + w, base - h), (x + w + sw_, base - h - sw_ * 0.2), (x + w + sw_, base - sw_ * 0.2), (x + w, base)]
    out.append(f'<path d="{pd(side)}" fill="#B07A48"/>')
    out.append(painted(D, rect_pts(x, base - h, x + w, base, 8, seed, 0.3), stone, seed, sdir=(-1, 0.3), sk=0.1, angle=-80, n=10, inkw=1.1, inkop=0.6, hi=0.4))
    roof = [(x - 3, base - h + 1), (x + w * 0.5, base - h - w * 0.18), (x + w + 3, base - h + 1)]
    out.append(f'<path d="{pd(roof)}" fill="#C8582E"/>')
    out.append(f'<path d="{pd([(x + w + 3, base - h + 1), (x + w * 0.5, base - h - w * 0.18), (x + w * 0.5 + sw_, base - h - w * 0.18 - sw_ * 0.2), (x + w + sw_ + 3, base - h - sw_ * 0.2 + 1)])}" fill="#A8462A"/>')
    for k in range(3):
        wx = x + w * (0.18 + 0.3 * k)
        out.append(f'<rect x="{wx:.1f}" y="{base - h * 0.62:.1f}" width="3.2" height="4.4" fill="#4A3020"/>')
    if tower:
        tx, tw = x + w * 0.62, w * 0.3
        out.append(painted(D, rect_pts(tx, base - h - h * 0.75, tx + tw, base - h + 2, 6, seed + 1, 0.3), stone, seed + 1, sdir=(-1, 0.3), sk=0.1, n=6, inkw=1.0, inkop=0.6, hi=0.4))
        out.append(f'<path d="{pd([(tx - 2, base - h - h * 0.75), (tx + tw / 2, base - h - h * 0.95), (tx + tw + 2, base - h - h * 0.75)])}" fill="#C8582E"/>')
        out.append(f'<rect x="{tx + tw * 0.35:.1f}" y="{base - h - h * 0.55:.1f}" width="3" height="4" fill="#4A3020"/>')
    return "".join(out)


@design("toscana")
def toscana():
    D = Doc2("itts")
    out = [sky(D, [(0, "#F4B97E"), (0.45, "#FAD8A0"), (1, "#FFF0C8")], 3, 330, ["#FFE8B8", "#F2A870", "#FFF4D8"], 60, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 460, 250, 280, "#FFF6C8", 0.75))
    out.append(f'<circle cx="460" cy="252" r="30" fill="#FFF8DA" opacity="0.95"/>')
    for k, (x, y, w) in enumerate(((150, 210, 160), (370, 180, 110))):
        out.append(puff_cloud(D, x, y, w, 200 + k, pal=("#FFF4E0", "#FCDCB4", "#E8A888"), op=0.75, rows=1))
    # distant hazy hills, layered, paler and bluer with distance
    out.append(hill(D, ridge([(-20, 282), (120, 262), (260, 276), (400, 256), (620, 270)], 201, 8, 4), 340, ("#E8C8C0", "#D8B0B0", "#B89098"), 202, inkw=0, n=20))
    out.append(hill(D, ridge([(-20, 300), (140, 290), (300, 300), (460, 284), (620, 296)], 203, 8, 4), 360, ("#D8C0A0", "#C0A888", "#9A8268"), 204, inkw=0, n=20))
    # far cypress fringes
    rnd = random.Random(205)
    for k in range(14):
        x = rnd.uniform(0, 600)
        out.append(cypress(D, x, 300 + rnd.uniform(-4, 6), rnd.uniform(14, 22), 206 + k, pal=("#B0A078", "#8A8060", "#6A6048"), w=4))
    # mid hill with the farmhouse on its crown
    mid = ridge([(-20, 336), (120, 318), (250, 290), (330, 286), (430, 306), (620, 330)], 207, 6, 3)
    out.append(hill(D, mid, 420, ("#D8C878", "#B8A858", "#7A7A38"), 208, inkw=1.2, n=60, lit="#FFF0A8"))
    # field patches on the mid hill (wheat, green, ploughed)
    for k, (pts, c) in enumerate((([(30, 350), (180, 330), (200, 370), (40, 392)], "#E8C870"), ([(200, 328), (300, 306), (330, 340), (220, 366)], "#9AAA58"),
                                  ([(340, 316), (470, 324), (480, 360), (350, 352)], "#C89A60"), ([(470, 328), (620, 340), (620, 380), (490, 370)], "#B8C068"))):
        fd = smooth_closed(jitter(poly_pts(pts, 14, 209 + k, 1.5), 209 + k, 2))
        out.append(f'<path d="{fd}" fill="{c}" opacity="0.7"/>')
        x0, y0, x1, y1 = bbox(pts)
        out.append(strokes(D.nid(), fd, (x0 - 30, y0, x1, y1), [lt(c, 0.3), dk(c, 0.25)], 210 + k, n=40, angle=-6, length=(16, 44), width=(0.8, 1.8), opacity=(0.35, 0.7)))
    out.append(casale(D, 268, 296, 44, 22, 212))
    for k, (x, h) in enumerate(((256, 44), (330, 50), (342, 38))):
        out.append(cypress(D, x, 300 + k, h, 213 + k, light=1, rim="#C8D088"))
    # winding road from the bottom up to the house, lined with cypresses
    road_c = catmull([(250, 610), (300, 520), (380, 470), (330, 410), (250, 370), (290, 320), (300, 300)], 8)
    widths = []
    for i, (x, y) in enumerate(road_c):
        widths.append(max(3, (y - 290) * 0.2))
    left = []
    right = []
    for i, (x, y) in enumerate(road_c):
        a = road_c[max(0, i - 1)]
        b = road_c[min(len(road_c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((x + nx * widths[i] / 2, y + ny * widths[i] / 2))
        right.append((x - nx * widths[i] / 2, y - ny * widths[i] / 2))
    # front hills (green, lit) with vineyard rows
    front = ridge([(-20, 400), (160, 380), (320, 396), (460, 372), (620, 384)], 214, 6, 3)
    out.append(hill(D, front, 610, ("#B8C870", "#8AA048", "#4E6A2A"), 215, inkw=1.4, n=120, lit="#F2F0A0"))
    road = smooth_closed(left + right[::-1])
    out.append(f'<path d="{road}" fill="#E8C898"/>')
    out.append(strokes(D.nid(), road, (180, 290, 420, 610), ["#F6DCB0", "#C8A070", "#FFF0D0"], 216, n=50, angle=-80, length=(10, 30), width=(1, 3), opacity=(0.3, 0.6)))
    out.append(ink(smooth_open(left), "#9A7A50", 1.2, 217, 1, 0.5) + ink(smooth_open(right), "#9A7A50", 1.2, 218, 1, 0.5))
    # vineyard rows converging on the right hill
    for k in range(9):
        y0 = 420 + k * 22
        pts = [(400 + k * 4, y0 - 30 + k * 3), (500, y0 - 14 + k * 2), (620, y0 + k * 3)]
        out.append(taper(catmull(pts, 4), 3 + k * 0.8, 6 + k * 1.2, "#3E5A22", 0.85))
        rr = random.Random(220 + k)
        for j in range(int(12 + k * 2)):
            t = rr.random()
            x = pts[0][0] + (pts[-1][0] - pts[0][0]) * t
            y = pts[0][1] + (pts[-1][1] - pts[0][1]) * t - 2 - k * 0.5
            s = 2.4 + k * 0.6
            out.append(f'<path d="{blob(x, y, s, s * 0.7, rr.randint(1, 999), 0.2, 8)}" fill="{rr.choice(["#6E8A34", "#A8B850", "#4E6A2A", "#C8C860"])}"/>')
    # left: wheat field with round hay bales, and a poppy patch in front
    out.append(f'<path d="{smooth_closed([(-10, 436), (120, 420), (236, 440), (226, 610), (-10, 610)])}" fill="#E2C070" opacity="0.6"/>')
    for k, (x, y, r) in enumerate(((60, 446, 13), (118, 452, 15), (176, 440, 11))):
        out.append(f'<path d="{blob(x - r * 0.6, y + r * 0.85, r * 1.3, r * 0.22, k, 0.1, 10)}" fill="#5A4A1A" opacity="0.35"/>')
        out.append(painted(D, blob_pts(x, y, r, r * 0.92, 227 + k, 0.04, 14), ("#FBE2A0", "#DDB060", "#9A7030"), 227 + k, sdir=(-1, 0.3), sk=0.2, angle=-90, n=10, inkw=1.2, hi=0.5))
        out.append(f'<path d="{blob(x + r * 0.3, y, r * 0.5, r * 0.55, k + 4, 0.05, 10)}" fill="none" stroke="#B88A40" stroke-width="1.2" opacity="0.8"/>')
        out.append(f'<path d="{blob(x + r * 0.3, y, r * 0.25, r * 0.28, k + 5, 0.05, 10)}" fill="none" stroke="#B88A40" stroke-width="1" opacity="0.8"/>')
    out.append(grass(225, (-10, 470, 230, 610), ["#E8C870", "#F2D890", "#C8A050"], n=220, h=(10, 24), w=1.8))
    rr = random.Random(226)
    for k in range(40):
        x, y = rr.uniform(10, 200), rr.uniform(500, 600)
        s = 2.4 + (y - 500) * 0.04
        out.append(f'<path d="{blob(x, y, s, s * 0.8, k, 0.2, 8)}" fill="{rr.choice(["#E0281A", "#F04A2A", "#C8180E"])}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{s * 0.25:.1f}" fill="#2A1A10"/>')
    # cypress avenue: pairs shrinking with distance, long shadows to the left
    for k, (t, h) in enumerate(((0.16, 140), (0.27, 100), (0.38, 74), (0.5, 56), (0.6, 44), (0.7, 34), (0.8, 28))):
        i = int(t * (len(road_c) - 1))
        x, y = road_c[i]
        off = widths[i] * 0.5 + h * 0.08
        for sg in (-1, 1):
            out.append(f'<path d="{blob(x + sg * off - h * 0.35, y + 2, h * 0.38, h * 0.03 + 1, k, 0.1, 10)}" fill="#3A4A1A" opacity="0.35"/>')
            out.append(cypress(D, x + sg * off, y + 2, h, 230 + k * 2 + (sg > 0), light=1, rim="#D8D890"))
    # lettering
    out.append(letters(D, 300, 154, "Toscana", SERIF_IT, 124, "#7A2E14", ["#A8461E", "#5A1E0A", "#C8602E"], 240, max_w=420,
                       shadow="#FFF0C8", soff=(0.02, 0.035), angle=-40, hi="#F2A870"))
    out.append(ruled(300, 198, "COLLINE · CIPRESSI · VINO", "#5A3A1A", font=JOS, size=18, ls=4, line_w=22, gap=10, max_w=360))
    return finish_i(D, out, 241)


# ================================================================ 6. venezia — a moored gondola, the bridge, lamps at dusk
def venetian_chimney(D, x, top, s, col):
    """The funnel-topped Venetian chimney (camino a imbuto)."""
    return (f'<path d="M {x - s * 0.18:.1f} {top + s:.1f} L {x - s * 0.15:.1f} {top + s * 0.35:.1f} L {x - s * 0.42:.1f} {top:.1f} L {x + s * 0.42:.1f} {top:.1f} '
            f'L {x + s * 0.15:.1f} {top + s * 0.35:.1f} L {x + s * 0.18:.1f} {top + s:.1f} Z" fill="{col}"/>'
            f'<path d="M {x - s * 0.44:.1f} {top:.1f} L {x + s * 0.44:.1f} {top:.1f}" stroke="{dk(col, 0.3)}" stroke-width="2"/>')


def gondola(D, x0, x1, wl, seed, s=1.0):
    """A gondola moored at the waterline wl: long black asymmetric hull, rising stern and prow, the iron ferro
    at the prow, gold trim, a red cushioned seat; reflection below."""
    L = x1 - x0
    out = []
    top = [(x0 - 6, wl - 34 * s), (x0 + L * 0.08, wl - 16 * s), (x0 + L * 0.3, wl - 9 * s), (x0 + L * 0.6, wl - 9 * s), (x0 + L * 0.86, wl - 16 * s), (x1, wl - 40 * s)]
    bot = [(x1 - 6, wl - 30 * s), (x0 + L * 0.84, wl - 2 * s), (x0 + L * 0.5, wl + 3 * s), (x0 + L * 0.14, wl - 2 * s), (x0, wl - 26 * s)]
    hull = catmull(top, 6) + catmull(bot, 6)
    # reflection
    refl = [(x, wl + (wl - y) * 0.9) for x, y in hull]
    out.append(f'<path d="{smooth_closed(refl)}" fill="#0E0E1A" opacity="0.4"/>')
    out.append(painted(D, hull, ("#3A3A4A", "#14121A", "#020204"), seed, sdir=(0, 1), sk=0.1, angle=0, n=40, slen=(20, 60), sw=(1, 2.4),
                       cols=["#4A4A5E", "#0A0A10", "#2A2A3A"], inkw=1.6, inkc="#000000", hi=0.4, hik=0.12))
    out.append(taper(catmull(top, 6)[2:-2], 2.4, 2.4, "#E8B848", 0.95))
    out.append(taper([(x0 + L * 0.12, wl - 10 * s), (x0 + L * 0.5, wl - 4 * s), (x0 + L * 0.82, wl - 10 * s)], 2.2, 1, "#7A7A9A", 0.55))
    # seat and cushions
    sx = x0 + L * 0.55
    back = [(sx - 36 * s, wl - 12 * s), (sx - 40 * s, wl - 34 * s), (sx - 30 * s, wl - 44 * s), (sx - 18 * s, wl - 40 * s), (sx - 18 * s, wl - 14 * s)]
    out.append(painted(D, back, ("#F2685A", "#B8182A", "#5A0610"), seed + 2, sdir=(1, 0.3), sk=0.2, n=6, inkw=1.2, hi=0.45))
    out.append(ink(smooth_open(back[:4]), "#E8B848", 2.2, seed, 1, 0.95))
    cush = [(sx - 24 * s, wl - 12 * s), (sx - 22 * s, wl - 24 * s), (sx + 24 * s, wl - 24 * s), (sx + 28 * s, wl - 12 * s)]
    out.append(painted(D, cush, ("#F2685A", "#B8182A", "#5A0610"), seed + 1, sdir=(0.3, 1), sk=0.2, n=8, inkw=1.2, hi=0.45))
    for k in range(4):
        out.append(f'<circle cx="{sx - 14 * s + k * 12 * s:.1f}" cy="{wl - 19 * s:.1f}" r="{1.6 * s:.1f}" fill="#E8B848"/>')
    out.append(taper([(sx - 22 * s, wl - 24 * s), (sx + 24 * s, wl - 24 * s)], 2, 2, "#E8B848", 0.9))
    # the forcola (carved oarlock) near the stern
    fx0 = x0 + L * 0.2
    out.append(painted(D, [(fx0 - 4 * s, wl - 12 * s), (fx0 - 6 * s, wl - 30 * s), (fx0 + 2 * s, wl - 38 * s), (fx0 + 6 * s, wl - 30 * s), (fx0 + 2 * s, wl - 24 * s), (fx0 + 5 * s, wl - 12 * s)],
                       ("#E8B880", "#A8703A", "#5A3414"), seed + 5, sk=0.2, n=4, inkw=1.2, hi=0.4))
    # ferro: the iron prow comb (generic: an S-neck blade with six teeth)
    fx, fy = x1 - 2, wl - 40 * s
    blade = [(fx - 4 * s, fy + 6 * s), (fx - 2 * s, fy - 10 * s), (fx + 4 * s, fy - 26 * s), (fx + 2 * s, fy - 34 * s), (fx + 12 * s, fy - 36 * s),
             (fx + 14 * s, fy - 30 * s), (fx + 10 * s, fy - 24 * s), (fx + 8 * s, fy - 6 * s), (fx + 6 * s, fy + 6 * s)]
    out.append(f'<path d="{smooth_closed(blade)}" fill="#D8D8E0" stroke="#5A5A6A" stroke-width="1.2"/>')
    for k in range(6):
        ty = fy - 2 * s - k * 4 * s
        out.append(f'<path d="M {fx + 6 * s:.1f} {ty:.1f} l {9 * s:.1f} {-1 * s:.1f}" stroke="#D8D8E0" stroke-width="{2.4 * s:.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="M {fx - 1 * s:.1f} {fy - 6 * s:.1f} l {-8 * s:.1f} {3 * s:.1f}" stroke="#D8D8E0" stroke-width="{2.6 * s:.1f}" stroke-linecap="round"/>')
    # stern post
    out.append(f'<path d="M {x0 + 2:.1f} {wl - 26 * s:.1f} q -4 -12 -2 -16" stroke="#14121A" stroke-width="{4 * s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def palina(D, x, top, wl, seed, cols=("#1F4BA8", "#FFFFFF"), w=10, cap=True):
    """Striped mooring pole with a painted cap, and its wobbly reflection."""
    out = []
    d = hg.org_rect(x - w / 2, top, w, wl - top + 6, seed, 0.3, 10, 2)
    out.append(f'<path d="{d}" fill="{cols[1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    st = []
    y = top + 12
    while y < wl + 10:
        st.append(f'<path d="M {x - w:.1f} {y:.1f} L {x + w:.1f} {y - 6:.1f} L {x + w:.1f} {y + 4:.1f} L {x - w:.1f} {y + 10:.1f} Z" fill="{cols[0]}"/>')
        y += 22
    st.append(f'<rect x="{x - w / 2:.1f}" y="{top}" width="{w * 0.35:.1f}" height="{wl - top + 6:.1f}" fill="#FFFFFF" opacity="0.25"/>')
    st.append(f'<rect x="{x + w * 0.15:.1f}" y="{top}" width="{w * 0.35:.1f}" height="{wl - top + 6:.1f}" fill="#000000" opacity="0.22"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(ink(d, "#1A1A2A", 1.2, seed, 1, 0.7))
    if cap:
        out.append(painted(D, blob_pts(x, top - 2, w * 0.7, 6, seed, 0.05, 10), ("#F2C860", "#C8902A", "#7A5410"), seed, sk=0.2, n=3, inkw=1, hi=0.5))
    for k in range(6):
        yy = wl + 6 + k * 9
        out.append(f'<path d="M {x - w / 2 + math.sin(k) * 3:.1f} {yy:.1f} l {w:.1f} 0" stroke="{cols[k % 2]}" stroke-width="5" opacity="{0.55 - k * 0.07:.2f}"/>')
    return "".join(out)


@design("venezia")
def venezia():
    D = Doc2("itvz")
    out = [sky(D, [(0, "#3A3A7A"), (0.35, "#8A5A9A"), (0.7, "#F09A8A"), (1, "#FFD2A0")], 3, 440, ["#B88AB8", "#5A4A8A", "#FFC8A8"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 340, 220, "#FFE2B0", 0.6))
    out.append(hg.flakes(301, 22, (40, 40, 560, 160), (0.8, 1.6), "#FFF6E8", (0.4, 0.9)))
    # far: the campanile and a dome silhouetted in the gap, hazy
    far = "#B48AA8"
    out.append(f'<path d="M 252 352 L 252 248 L 258 240 L 262 222 L 266 240 L 272 248 L 272 352 Z" fill="{far}"/>')
    out.append(f'<path d="M 300 352 L 300 300 Q 300 268 330 262 Q 360 268 360 300 L 360 352 Z" fill="{far}"/><path d="M 328 262 l 2 -14 l 2 14 Z" fill="{far}"/>')
    out.append(f'<path d="M 200 352 L 200 318 L 400 318 L 400 352 Z" fill="#A87A98"/>')
    # palazzi either side (left darker, right catching the sunset)
    out.append(facade(D, -20, 120, 214, 470, 302, "#C87A62", shutters="#3A5A4A", rows=4, cols=2, arch=True, lit=0.55, roof=True, haze=0.2))
    out.append(facade(D, 118, 200, 266, 470, 303, "#E8B07A", shutters="#3A5A4A", rows=3, cols=2, arch=True, lit=0.5, haze=0.25))
    out.append(facade(D, 404, 488, 258, 470, 304, "#D88A7A", shutters="#2E4A3A", rows=3, cols=2, arch=True, lit=0.5, haze=0.2))
    out.append(facade(D, 486, 620, 206, 470, 305, "#F2C894", shutters="#2E4A3A", rows=4, cols=2, arch=True, lit=0.6, haze=0.1, balcony="#E8504A"))
    for x, top, c in ((40, 186, "#A85A48"), (90, 190, "#A85A48"), (150, 240, "#B87A58"), (440, 232, "#B06A5A"), (530, 180, "#C89A6A")):
        out.append(venetian_chimney(D, x, top, 26, c))
    # shade toward the canal on the facades
    out.append(f'<rect x="-10" y="360" width="620" height="112" fill="{D.lin([(0, "#2A1A3A", 0), (1, "#2A1A3A", 0.45)])}"/>')
    # canal water
    out.append(sea(D, 468, 610, [(0, "#6A5A8A"), (0.4, "#3A3A6A"), (1, "#1E2248")], 306, ["#8A7AAA", "#14183A", "#F2B8A0"], 110, ticks=["#FFD8B0", "#B8A8D8"]))
    for x, c in ((60, "#FFD27A"), (160, "#FFD27A"), (450, "#FFD27A"), (540, "#FFD27A"), (300, "#FFE2B0")):
        out.append(wave_lines(307 + x, (x - 20, 474, x + 20, 600), [c], 14, (8, 22), 2.4, 2, (0.4, 0.8)))
    # quays (fondamenta) under the palazzi
    for x0, x1 in ((-10, 196), (404, 610)):
        out.append(painted(D, rect_pts(x0, 460, x1, 476, 20, x0 + 400, 0.4), ("#F2E8DA", "#C8B8A6", "#7A6A5A"), 318 + x0, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.2, hi=0.5))
    # reflections of the lit facades, broken by ripples
    for x0, x1, c in ((-10, 120, "#C87A62"), (118, 200, "#E8B07A"), (404, 488, "#D88A7A"), (486, 610, "#F2C894")):
        rr = random.Random(int(x0) + 900)
        for k in range(26):
            y = 482 + k * 4.6 + rr.uniform(-1, 1)
            xa = x0 + rr.uniform(0, 14)
            xb = x1 - rr.uniform(0, 14)
            out.append(taper([(xa, y), ((xa + xb) / 2, y + rr.uniform(-1.2, 1.2)), (xb, y)], 0.6, rr.uniform(2, 3.4), mix(c, "#2A2448", 0.35 + k * 0.02), 0.55 - k * 0.012))
    # stone bridge: a single arch, deck rising to the crown
    deck = catmull([(116, 474), (156, 446), (300, 376), (444, 446), (484, 474)], 6)
    arch_pts = [(300 + 118 * math.cos(math.radians(180 * k / 24)), 478 - 72 * math.sin(math.radians(180 * k / 24))) for k in range(25)]
    body = deck + arch_pts
    out.append(painted(D, body, ("#FBF4EA", "#E2D4C2", "#9A8A7A"), 308, sdir=(0, 1), sk=0.08, angle=0, n=50, slen=(10, 40), sw=(1, 3), inkw=1.8, hi=0.3))
    bcid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    courses = []
    for k in range(1, 6):
        y = 380 + k * 18
        courses.append(f'<path d="M 100 {y} L 500 {y}" stroke="#B8A898" stroke-width="1" opacity="0.5"/>')
    courses.append(f'<rect x="100" y="360" width="400" height="120" fill="{D.lin([(0, "#FFE2B8", 0.35), (0.5, "#FFE2B8", 0), (1, "#3A2A4A", 0.35)])}"/>')
    out.append(f'<g {bcid}>{"".join(courses)}</g>')
    for k in range(0, 25, 2):
        a_ = math.radians(180 * k / 24)
        out.append(pline([(300 + 118 * math.cos(a_), 478 - 72 * math.sin(a_)), (300 + 134 * math.cos(a_), 478 - 86 * math.sin(a_))], "#9A8A7A", 1.3, k, 0.7, 1))
    out.append(pline([(300 + 134 * math.cos(math.radians(180 * k / 24)), 478 - 86 * math.sin(math.radians(180 * k / 24))) for k in range(25)], "#9A8A7A", 1.2, 309, 0.6, 1))
    out.append(f'<path d="{smooth_closed(arch_pts)}" fill="#1E1834"/>')
    out.append(f'<path d="{smooth_closed(arch_pts)}" fill="{D.lin([(0, "#F2A880", 0.0), (1, "#F2A880", 0.35)])}"/>')
    refl = [(x, 478 + (478 - y) * 0.8) for x, y in arch_pts]
    out.append(f'<path d="{smooth_open(refl)}" stroke="#D8C8D0" stroke-width="7" fill="none" opacity="0.3"/>')
    # balustrade along the deck
    top = [(x, y - 14) for x, y in deck]
    out.append(taper(top, 4, 4, "#F6EEE2"))
    for k in range(3, len(deck) - 3, 2):
        x, y = deck[k]
        out.append(f'<path d="M {x:.1f} {y - 13:.1f} L {x:.1f} {y:.1f}" stroke="#E6DACA" stroke-width="3"/>')
    by = 400
    # lamps on the bridge
    for x, y in ((172, 428), (428, 428)):
        out.append(D.glow(x, y - 10, 34, "#FFD27A", 0.75))
        out.append(f'<path d="M {x} {y + 14} L {x} {y - 4}" stroke="#2A2230" stroke-width="2.4"/>')
        out.append(f'<path d="{hg.org_rect(x - 5, y - 16, 10, 12, x, 0.2, 6, 1)}" fill="#FFE8A0" stroke="#2A2230" stroke-width="1.6"/>')
    # two figures crossing the bridge
    out.append(figures.person(270, 384, 30, "walk", 1, seed=310, tint=("#8A5A9A", 0.35)))
    out.append(figures.person(326, 384, 28, "walk", -1, seed=311, tint=("#8A5A9A", 0.35)))
    # foreground: mooring poles and the gondola
    out.append(palina(D, 66, 418, 528, 312))
    out.append(palina(D, 92, 444, 528, 313, cols=("#C8281A", "#FFFFFF"), w=8))
    out.append(gondola(D, 104, 516, 536, 314, 1.3))
    out.append(palina(D, 548, 430, 532, 315))
    # lettering
    out.append(letters(D, 300, 146, "Venezia", SERIF_IT, 120, "#FFF2DA", ["#FFFFFF", "#F6D8C0", "#FFE8D0"], 316, max_w=400,
                       shadow="#3A2A5A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 188, "LA SERENISSIMA", "#FFE2B0", font=JOS, size=20, ls=6, line_w=30, gap=12, max_w=300))
    return finish_i(D, out, 317, "#2A1A3A", 0.8)


# ================================================================ 7. pasta fatta in casa — the flour well, eggs, the rolling pin
def flour_drift(D, cx, cy, rx, ry, seed, op=0.85):
    """Loose dusting of flour: a pale irregular patch with grainy edges."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy, rx, ry, seed, 0.18, 20)}" fill="#FFFCF2" opacity="{op * 0.55:.2f}"/>',
           f'<path d="{blob(cx + rx * 0.1, cy - ry * 0.05, rx * 0.7, ry * 0.65, seed + 1, 0.2, 16)}" fill="#FFFFFF" opacity="{op * 0.5:.2f}"/>']
    for _ in range(int(rx * ry / 40)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.6, 1.25)
        out.append(f'<circle cx="{cx + math.cos(a) * rx * rr:.1f}" cy="{cy + math.sin(a) * ry * rr:.1f}" r="{rnd.uniform(0.5, 1.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9) * op:.2f}"/>')
    return "".join(out)


def nest(D, cx, cy, r, seed, pal=("#FFF0A8", "#F2CC5A", "#B88A24")):
    """A nest of fresh tagliatelle seen from above: flat golden ribbons coiled loosely, floured."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + 8, r * 1.1, r * 1.0, strength=0.4, seed=seed)]
    out.append(f'<path d="{blob(cx, cy, r * 0.95, r * 0.88, seed, 0.1, 16)}" fill="{pal[2]}" opacity="0.55"/>')
    for k in range(18):
        a0 = rnd.uniform(0, 6.28)
        rr = r * rnd.uniform(0.35, 0.92)
        span = rnd.uniform(2.8, 4.8)
        pts = []
        for i in range(14):
            t = i / 13
            a = a0 + span * t
            rad = rr * (1 + 0.12 * math.sin(t * 5 + k))
            pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad * 0.92))
        w = r * rnd.uniform(0.14, 0.19)
        c = rnd.choice([pal[1], pal[0], lt(pal[1], 0.15), mix(pal[1], pal[2], 0.2)])
        out.append(taper(pts, w * 0.8, w, dk(c, 0.35), 0.5))
        out.append(taper([(x - 0.8, y - 0.8) for x, y in pts], w * 0.75, w * 0.9, c, 0.95))
        out.append(taper([(x - w * 0.25, y - w * 0.25) for x, y in pts[2:-2]], w * 0.15, w * 0.2, "#FFFBE0", 0.6))
    out.append(specks(seed, (cx - r, cy - r, cx + r, cy + r), ["#FFFFFF"], int(r * 2), (0.6, 1.5), (0.5, 0.9)))
    return "".join(out)


def rolling_pin(D, x0, y0, x1, y1, w, seed):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    pal = ("#F6D6A2", "#D6A262", "#8A5A2A")
    out = [f'<g transform="translate({x0} {y0}) rotate({ang:.1f})">']
    out.append(f'<path d="{blob(L / 2 + 8, w * 0.9, L * 0.52, w * 0.35, seed, 0.03, 16)}" fill="#3A2010" opacity="0.25"/>')
    body = rect_pts(0, -w / 2, L, w / 2, 20, seed, 0.3)
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{D.lin([(0, pal[0]), (0.45, pal[1]), (1, pal[2])])}"/>')
    out.append(strokes(D.nid(), d, (-10, -w / 2, L, w / 2), [pal[0], pal[2], "#FFF0D0"], seed, n=int(L * 0.25), angle=0, length=(30, 90), width=(0.6, 1.6), opacity=(0.2, 0.5), curve=0.02))
    out.append(taper([(6, -w * 0.25), (L - 6, -w * 0.22)], w * 0.12, w * 0.08, "#FFF6E0", 0.7))
    rnd = random.Random(seed)
    out.append(specks(seed, (10, -w / 2, L - 10, w / 2), ["#FFFFFF"], int(L * 0.3), (0.6, 1.6), (0.5, 0.9)))
    out.append(ink(d, INK, 1.8, seed, 2, 0.75))
    out.append("</g>")
    return "".join(out)


def fork(D, x0, y0, x1, y1, w, seed, metal=ALU):
    """Table fork from handle end (x0, y0) to the tine tips (x1, y1)."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    out = [f'<g transform="translate({x0} {y0}) rotate({ang:.1f})">']
    handle = [(0, -w * 0.5), (L * 0.62, -w * 0.22), (L * 0.66, -w * 0.3), (L * 0.66, w * 0.3), (L * 0.62, w * 0.22), (0, w * 0.5), (-w * 0.3, 0)]
    out.append(painted(D, handle, metal, seed, sdir=(0, 1), sk=0.25, angle=0, n=8, inkw=1.4, hi=0.6))
    head = [(L * 0.64, -w * 0.32), (L * 0.78, -w * 0.62), (L * 0.78, w * 0.62), (L * 0.64, w * 0.32)]
    out.append(painted(D, head, metal, seed + 1, sdir=(0, 1), sk=0.25, angle=0, n=4, inkw=1.4, hi=0.6))
    for k in range(4):
        y = -w * 0.5 + k * w / 3
        out.append(taper([(L * 0.77, y), (L, y * 1.05)], w * 0.2, w * 0.12, metal[1]))
        out.append(taper([(L * 0.77, y - w * 0.05), (L * 0.98, y * 1.05 - w * 0.05)], w * 0.06, w * 0.03, "#FFFFFF", 0.8))
    out.append("</g>")
    return "".join(out)


@design("pasta-fatta-in-casa")
def pasta_fatta_in_casa():
    D = Doc2("itpf")
    out = [wood_planks(D, 0, 600, 401, ("#E2B07A", "#C08A52", "#7A522A"), 5, vertical=True)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF2D8", 0.25), (1, "#3A2010", 0.3)], cx=0.45, cy=0.45, r=0.75)}"/>')
    # flour dusted everywhere
    for k, (x, y, rx, ry) in enumerate(((236, 372, 176, 140), (440, 300, 80, 46), (160, 520, 90, 40), (470, 560, 60, 30))):
        out.append(flour_drift(D, x, y, rx, ry, 402 + k, 0.55 if k else 0.7))
    # the flour well with eggs (fontana)
    cx, cy = 236, 372
    ring = blob_pts(cx, cy, 128, 112, 410, 0.07, 26)
    out.append(cast(D, cx + 10, cy + 14, 132, 116, strength=0.25, seed=411))
    out.append(painted(D, ring, ("#FFFFFF", "#F8F2E4", "#D8CCB4"), 412, sdir=(0.6, 0.8), sk=0.1, angle=-30, n=60, slen=(10, 30), sw=(1, 3), inkw=1.2, inkop=0.35, hi=0.6))
    rnd = random.Random(413)
    for _ in range(140):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.5, 1.0)
        out.append(f'<circle cx="{cx + math.cos(a) * 120 * rr:.1f}" cy="{cy + math.sin(a) * 104 * rr:.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="{rnd.choice(["#E8DCC4", "#FFFFFF", "#D8C8A8"])}" opacity="0.8"/>')
    well = blob_pts(cx + 4, cy + 2, 66, 56, 414, 0.08, 18)
    out.append(f'<path d="{smooth_closed(well)}" fill="#E8DCC4"/>')
    out.append(f'<path d="{smooth_closed(shift(well, -6, -6))} {smooth_closed(well)}" fill-rule="evenodd" fill="#BBA888" opacity="0.5"/>')
    # egg white pool and three yolks
    out.append(f'<path d="{blob(cx + 6, cy + 4, 50, 40, 415, 0.1, 16)}" fill="#F8F4E0" opacity="0.9"/>')
    out.append(f'<path d="{blob(cx + 6, cy + 4, 50, 40, 415, 0.1, 16)}" fill="none" stroke="#E0D4B0" stroke-width="2"/>')
    for k, (x, y, r) in enumerate(((cx - 12, cy - 6, 17), (cx + 22, cy - 2, 16), (cx + 4, cy + 22, 16))):
        out.append(painted(D, blob_pts(x, y, r, r * 0.95, 416 + k, 0.03, 14), ("#FFD24A", "#F49A12", "#B85A06"), 416 + k, sdir=(0.6, 0.7), sk=0.2, angle=-40, n=6, inkw=1.2, inkc="#9A4A06", hi=0.5))
        out.append(f'<path d="{blob(x - r * 0.35, y - r * 0.38, r * 0.3, r * 0.16, 420 + k, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
    # a fork resting in the well, ready to beat
    out.append(fork(D, 430, 300, 262, 360, 19, 424))
    # cracked egg shells
    for k, (x, y, a) in enumerate(((438, 372, -20), (470, 396, 30))):
        sh = rot([(x - 22, y), (x - 20, y - 12), (x - 10, y - 18), (x - 4, y - 10), (x + 2, y - 18), (x + 10, y - 12), (x + 16, y - 18), (x + 22, y - 6), (x + 20, y + 6),
                  (x, y + 14), (x - 16, y + 10)], x, y, a)
        out.append(cast(D, x + 4, y + 14, 24, 6, strength=0.3, seed=430 + k))
        out.append(painted(D, sh, ("#FFF4E4", "#F2DCC0", "#C8A47E"), 431 + k, sdir=(0.5, 0.8), sk=0.2, angle=-40, n=6, inkw=1.3, hi=0.4))
        out.append(f'<path d="{blob(x + 2, y + 2, 13, 7, 432 + k, 0.12, 10, a)}" fill="#FFFFFF" opacity="0.9"/>')
    # nests of tagliatelle
    out.append(nest(D, 128, 486, 52, 440))
    out.append(nest(D, 240, 506, 42, 441))
    # rolled sheet with a few cut ribbons
    sheet = [(392, 452), (552, 430), (562, 528), (402, 546)]
    out.append(cast(D, 486, 520, 92, 62, strength=0.3, seed=442))
    out.append(painted(D, poly_pts(sheet, 18, 443, 1.2), ("#FFF2B8", "#F6D676", "#C8A048"), 443, sdir=(0.4, 1), sk=0.08, angle=-8, n=30, inkw=1.4, hi=0.4))
    for k in range(5):
        x = 420 + k * 26
        out.append(pline([(x, 466 - k * 4), (x + 4, 520 - k * 2), (x + 8, 572 - k * 2)], "#C8A048", 1.4, 444 + k, 0.7, 1))
    out.append(specks(445, (400, 450, 560, 570), ["#FFFFFF"], 80, (0.6, 1.5), (0.5, 0.9)))
    out.append(rolling_pin(D, 360, 236, 576, 390, 32, 446))
    # lettering
    out.append(label(300, 92, "PASTA FRESCA", JOS, 26, "#FFF6E0", ls=10, max_w=320, extra=' stroke="#5A3418" stroke-width="5" paint-order="stroke"'))
    out.append(letters(D, 300, 196, "fatta in casa", SERIF_IT, 104, "#FFF8E8", ["#FFFFFF", "#F2E2C2", "#FFF2D8"], 447, max_w=450,
                       shadow="#5A3418", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    return finish_i(D, out, 448)


# ================================================================ 8. mangia! — spaghetti and meatballs, one forkful twirled
def plate_34(D, cx, cy, rx, ry, seed, glaze=WHITE, rim=None, rim2=None):
    """A round plate seen from a little above: rim, well, a painted band."""
    out = [cast(D, cx + 10, cy + ry * 0.35, rx * 1.05, ry * 0.9, strength=0.4, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 40), glaze, seed, sdir=(0.4, 1), sk=0.08, angle=0, n=30, inkw=1.8, hi=0.45))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + ry * 0.04, rx * 0.72, ry * 0.68, 0, 360, 36))}" fill="{dk(glaze[1], 0.04)}"/>')
    out.append(ink(smooth_open(ell_pts(cx, cy + ry * 0.04, rx * 0.72, ry * 0.68, 190, 350, 20)), glaze[2], 1.6, seed, 1, 0.6))
    if rim:
        out.append(ink(smooth_closed(ell_pts(cx, cy, rx * 0.88, ry * 0.86, 0, 360, 40)), rim, 3.2, seed + 1, 1, 0.9))
    if rim2:
        out.append(ink(smooth_closed(ell_pts(cx, cy, rx * 0.95, ry * 0.94, 0, 360, 40)), rim2, 1.6, seed + 2, 1, 0.9))
    return "".join(out)


def spaghetti_mound(D, cx, cy, rx, ry, seed, pal=("#FFEBA8", "#EEC864", "#B8902E")):
    """A tangle of spaghetti: many thin golden strands in loose loops, light on top, a few shadowed."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy, rx, ry, seed, 0.06, 20)}" fill="{pal[1]}"/>']
    cid = D.clip(f'<path d="{blob(cx, cy, rx * 1.02, ry * 1.04, seed, 0.06, 20)}"/>')
    inner = []
    for k in range(80):
        x, y = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        a0 = rnd.uniform(0, 6.28)
        R = rnd.uniform(10, 34)
        pts = [(x + math.cos(a0 + t * 0.4) * R * (1 + t * 0.05), y + math.sin(a0 + t * 0.4) * R * 0.55) for t in range(rnd.randint(6, 12))]
        lit = (cy - y) / ry
        c = pal[0] if lit > 0.25 else (pal[2] if lit < -0.4 else rnd.choice([pal[1], pal[0]]))
        inner.append(ink(smooth_open([(px, py + 1.2) for px, py in pts]), dk(pal[2], 0.2), 3.4, k, 1, 0.35))
        inner.append(ink(smooth_open(pts), c, 2.6, k, 1, 0.95))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


@design("mangia")
def mangia():
    D = Doc2("itmg")
    # trattoria: deep green wainscot wall, red check tablecloth
    out = [sky(D, [(0, "#2E5A44"), (1, "#1E4232")], 501, 600, ["#3E7A5A", "#16302A", "#4A8A64"], 110, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 120, 300, "#FFE6A8", 0.3))
    for x in range(-20, 620, 64):
        out.append(f'<path d="M {x} 220 L {x} 300" stroke="#16302A" stroke-width="3" opacity="0.5"/><path d="M {x + 3} 220 L {x + 3} 300" stroke="#5A9A70" stroke-width="1.4" opacity="0.4"/>')
    out.append(painted(D, rect_pts(-10, 208, 610, 222, 30, 502, 0.4), ("#C89A5A", "#8A5A2A", "#4A2A10"), 502, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.4))
    tc = [(-20, 300), (620, 300), (620, 620), (-20, 620)]
    out.append(cloth(D, tc, "#D0281E", 503, cell=22, light=(0.0, 0.0, 0.0, 1.0), inkw=0,
                     folds=[((60, 300), (70, 450), (50, 610)), ((540, 300), (530, 450), (550, 610))]))
    out.append(f'<rect x="-10" y="296" width="620" height="10" fill="#2A0A06" opacity="0.25"/>')
    # plate of spaghetti and meatballs
    cx, cy = 300, 436
    out.append(plate_34(D, cx, cy, 192, 100, 504, rim="#1E6A3A", rim2="#D0281E"))
    out.append(spaghetti_mound(D, cx, cy - 10, 132, 64, 505))
    # sauce over the top, glossy
    sauce = blob_pts(cx - 4, cy - 28, 96, 40, 506, 0.18, 22)
    out.append(painted(D, sauce, ("#F0583A", "#C82214", "#6A0A06"), 506, sdir=(0.5, 0.8), sk=0.15, angle=-20, n=30, inkw=1.2, inkop=0.5, hi=0.4))
    rnd = random.Random(507)
    for k in range(10):
        a = rnd.uniform(0, 6.28)
        x, y = cx - 4 + math.cos(a) * 90, cy - 28 + math.sin(a) * 36
        out.append(taper([(x, y), (x + math.cos(a) * 10, y + 12 + rnd.uniform(0, 8))], 7, 2, "#C82214", 0.95))
    for k, (x, y, r) in enumerate(((cx - 54, cy - 40, 30), (cx + 36, cy - 46, 32), (cx - 6, cy - 14, 31), (cx + 74, cy - 14, 26))):
        out.append(f'<path d="{blob(x + 6, y + r * 0.7, r * 1.1, r * 0.35, k, 0.1, 10)}" fill="#5A0806" opacity="0.4"/>')
        out.append(meatball(D, x, y, r, 508 + k))
        out.append(f'<path d="{blob(x - 2, y - r * 0.55, r * 0.7, r * 0.28, 512 + k, 0.2, 10)}" fill="#C82214" opacity="0.9"/>')
        out.append(f'<path d="{blob(x - r * 0.3, y - r * 0.45, r * 0.2, r * 0.1, 516 + k, 0.2, 8, -20)}" fill="#FFFFFF" opacity="0.55"/>')
    # parmigiano snow and basil
    out.append(specks(520, (cx - 90, cy - 70, cx + 100, cy + 10), ["#FFF8E0", "#FFFFFF", "#F2E2B0"], 160, (0.8, 2.2), (0.75, 1)))
    out.append(basil_leaf(D, cx + 10, cy - 64, 38, -60, 521))
    out.append(basil_leaf(D, cx + 10, cy - 64, 30, -120, 522))
    # fork twirling a forkful, held above, strands falling
    fx, fy = 452, 296
    out.append(fork(D, 586, 196, fx, fy, 20, 523))
    tw = []
    out.append(f'<path d="{blob(fx - 4, fy + 8, 26, 17, 539, 0.1, 14)}" fill="#C8A040"/>')
    for k in range(14):
        a0 = k * 0.55
        pts = [(fx - 4 + math.cos(a0 + t * 0.8) * (24 - t * 0.8), fy + 8 + math.sin(a0 + t * 0.8) * 15 + t * 0.8) for t in range(12)]
        tw.append(ink(smooth_open(pts), "#EEC864" if k % 2 else "#FFE29A", 3, 524 + k, 1, 1))
    out.append("".join(tw))
    for k, dx in enumerate((-18, -8, 2, 12, 20)):
        pts = [(fx + dx, fy + 22), (fx + dx + 6 * math.sin(k), fy + 70), (fx + dx - 6, fy + 108 + k * 8)]
        out.append(ink(smooth_open(pts), "#B8902E", 3.4, 530 + k, 1, 0.4) + ink(smooth_open(pts), "#F2D070", 2.6, 534 + k, 1, 1))
    out.append(painted(D, blob_pts(fx - 8, fy + 2, 18, 10, 538, 0.15, 12), ("#F0583A", "#C82214", "#6A0A06"), 538, sk=0.2, n=4, inkw=1, hi=0.4))
    # a chunk of parmigiano and a little bowl of grated cheese
    pg = [(70, 534), (82, 488), (150, 476), (164, 522), (140, 544)]
    out.append(cast(D, 120, 546, 56, 10, strength=0.4, seed=540))
    out.append(painted(D, pg, ("#FFF0B8", "#F2D480", "#B89A48"), 541, sdir=(0.7, 0.6), sk=0.2, angle=-60, n=10, inkw=1.6, hi=0.4))
    out.append(painted(D, [(70, 534), (82, 488), (92, 482), (84, 530)], ("#E8B860", "#B8862E", "#7A5214"), 542, sk=0.2, n=4, inkw=1.2, hi=0.3))
    out.append(specks(543, (90, 488, 158, 540), ["#C8A050", "#FFFBE0"], 24, (0.8, 1.6), (0.5, 0.9)))
    # lettering
    out.append(letters(D, 300, 148, "Mangia!", SERIF_IT, 132, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 544, max_w=420,
                       shadow="#0E2418", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 196, "MANGIA, CHE TI FA BENE", "#F6C870", font=JOS, size=20, ls=4, line_w=24, gap=12, max_w=360))
    return finish_i(D, out, 545)


# ================================================================ 9. la dolce vita — two spritz on a Roman terrace at sunset
def spritz_glass(D, cx, base, h, seed, drink=("#FFB060", "#F2641A", "#A8360A"), olive_=True, straw=None):
    """Big balloon wine glass with an orange spritz, ice, a slice of orange and a green olive on a pick."""
    w = h * 0.62
    out = [cast(D, cx + 8, base + 1, w * 0.55, 5, strength=0.4, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 2, w * 0.36, 4.5, 0, 360, 16))}" fill="#F2F4F0" stroke="#6A7A7A" stroke-width="1.2"/>')
    out.append(f'<path d="M {cx - 2.2} {base - 3} L {cx - 2.6} {base - h * 0.38} L {cx + 2.6} {base - h * 0.38} L {cx + 2.2} {base - 3} Z" fill="#F2F4F0" stroke="#6A7A7A" stroke-width="1.1"/>')
    bowl = [(cx - w * 0.42, base - h), (cx - w * 0.5, base - h * 0.7), (cx - w * 0.36, base - h * 0.46), (cx, base - h * 0.37),
            (cx + w * 0.36, base - h * 0.46), (cx + w * 0.5, base - h * 0.7), (cx + w * 0.42, base - h)]
    d = smooth_closed(bowl)
    out.append(f'<path d="{d}" fill="#F2F6F4" opacity="0.45"/>')
    cid = D.clip(f'<path d="{d}"/>')
    ly = base - h * 0.86
    rnd = random.Random(seed)
    inner = [f'<rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{drink[1]}" opacity="0.92"/>',
             f'<rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{D.lin([(0, drink[0], 0.7), (0.4, drink[0], 0), (1, drink[2], 0.6)], 0, 0, 1, 0)}"/>']
    for k in range(4):
        ix, iy = cx + rnd.uniform(-w * 0.28, w * 0.28), ly + rnd.uniform(6, h * 0.3)
        inner.append(f'<path d="{hg.org_rect(ix - 9, iy - 8, 18, 16, seed + k, 0.6, 8, 4)}" fill="#FFE0C0" opacity="0.5" stroke="#FFFFFF" stroke-width="1.2" transform="rotate({rnd.uniform(-30, 30):.0f} {ix:.1f} {iy:.1f})"/>')
    for k in range(14):
        inner.append(f'<circle cx="{cx + rnd.uniform(-w * 0.35, w * 0.35):.1f}" cy="{rnd.uniform(ly + 6, base - h * 0.42):.1f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFE8C8" opacity="0.85"/>')
    # orange slice inside
    sx, sy = cx - w * 0.12, ly + h * 0.2
    inner.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{w * 0.2:.1f}" fill="#FF9A2A" stroke="#E8701A" stroke-width="2.4"/>')
    for k in range(8):
        a = math.radians(k * 45)
        inner.append(f'<path d="M {sx:.1f} {sy:.1f} L {sx + math.cos(a) * w * 0.17:.1f} {sy + math.sin(a) * w * 0.17:.1f}" stroke="#FFD08A" stroke-width="1.4"/>')
    inner.append(f'<path d="M {cx - w} {ly} L {cx + w} {ly}" stroke="#FFD8A8" stroke-width="2.6"/>')
    inner.append(taper([(cx - w * 0.38, base - h * 0.95), (cx - w * 0.42, base - h * 0.7), (cx - w * 0.3, base - h * 0.5)], 5, 1.5, "#FFFFFF", 0.7))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#5A6A6A", 1.6, seed, 2, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w * 0.42, 4.5, 0, 360, 16))}" fill="none" stroke="#5A6A6A" stroke-width="1.3" opacity="0.8"/>')
    if olive_:
        out.append(pline([(cx + w * 0.1, base - h * 0.62), (cx + w * 0.42, base - h * 1.12)], "#D8C8A0", 2, seed, 1, 1))
        out.append(olive(cx + w * 0.3, base - h * 0.96, 7, -58, ("#B8C060", "#7A8A2A", "#3E4A12")))
    return "".join(out)


def umbrella_pine(D, x, base, h, seed, pal=("#6A8A5A", "#3E5E3A", "#1E3220"), trunk="#5A3A2A", light=1, rim=None):
    """Roman stone pine: slim leaning trunk forking high, a flat wide parasol crown of dabs."""
    rnd = random.Random(seed)
    out = []
    top = (x + h * 0.06 * light, base - h * 0.78)
    out.append(taper(catmull([(x, base), (x + h * 0.02, base - h * 0.4), top], 4), max(3, h * 0.05), max(2, h * 0.025), trunk))
    for sg in (-1, 1):
        out.append(taper([top, (top[0] + sg * h * 0.16, top[1] - h * 0.08)], max(2, h * 0.025), 1.2, trunk))
    cx, cy = top[0], top[1] - h * 0.1
    rx, ry = h * 0.42, h * 0.13
    out.append(f'<path d="{blob(cx, cy, rx, ry, seed, 0.12, 20)}" fill="{pal[2]}"/>')
    for i in range(int(h * 1.4)):
        a = rnd.uniform(math.pi, 2 * math.pi) if rnd.random() < 0.6 else rnd.uniform(0, math.pi)
        rr = math.sqrt(rnd.random())
        px, py = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        lit = (px - cx) / rx * light * 0.6 - (py - cy) / ry * 0.6
        c = (rim if rim and lit > 0.55 else pal[0]) if lit > 0.3 else (pal[2] if lit < -0.3 else pal[1])
        out.append(f'<path d="{blob(px, py, rnd.uniform(3, 6) * h / 120, rnd.uniform(2, 4) * h / 120, rnd.randint(1, 9999), 0.25, 8)}" fill="{c}"/>')
    return "".join(out)


def dome(D, cx, base, w, seed, col="#C8A898", lit="#F2C8A8", haze=0.0):
    """A generic baroque church: drum with windows, ribbed dome, lantern and cross, flanking roofs."""
    hz = (lambda c: mix(c, "#E8C8C8", haze)) if haze else (lambda c: c)
    out = []
    out.append(f'<path d="{hg.org_rect(cx - w * 0.9, base - w * 0.32, w * 1.8, w * 0.34, seed, 0.3, 10, 1)}" fill="{hz(dk(col, 0.1))}"/>')
    out.append(f'<path d="{hg.org_rect(cx - w * 0.45, base - w * 0.72, w * 0.9, w * 0.42, seed + 1, 0.3, 10, 1)}" fill="{hz(col)}"/>')
    for k in range(5):
        wx = cx - w * 0.36 + k * w * 0.18
        out.append(f'<path d="M {wx:.1f} {base - w * 0.38:.1f} l 0 {-w * 0.18:.1f} q {w * 0.035:.1f} {-w * 0.05:.1f} {w * 0.07:.1f} 0 l 0 {w * 0.18:.1f} Z" fill="{hz(dk(col, 0.4))}"/>')
    dp = [(cx - w * 0.48, base - w * 0.7)] + [(cx - w * 0.48 * math.cos(math.radians(t)), base - w * 0.7 - w * 0.62 * math.sin(math.radians(t))) for t in range(10, 171, 10)] + [(cx + w * 0.48, base - w * 0.7)]
    out.append(f'<path d="{pd(dp)}" fill="{hz(col)}"/>')
    lp = [(cx - w * 0.48, base - w * 0.7)] + [(cx - w * 0.48 * math.cos(math.radians(t)), base - w * 0.7 - w * 0.62 * math.sin(math.radians(t))) for t in range(10, 91, 10)] + [(cx, base - w * 0.7)]
    out.append(f'<path d="{pd(lp)}" fill="{hz(lit)}" opacity="0.5"/>')
    for k in (-0.6, -0.3, 0, 0.3, 0.6):
        out.append(f'<path d="M {cx + k * w * 0.48:.1f} {base - w * 0.7:.1f} Q {cx + k * w * 0.36:.1f} {base - w * 1.2:.1f} {cx:.1f} {base - w * 1.32:.1f}" stroke="{hz(dk(col, 0.25))}" stroke-width="1.6" fill="none"/>')
    out.append(f'<path d="{hg.org_rect(cx - w * 0.07, base - w * 1.52, w * 0.14, w * 0.22, seed + 2, 0.2, 6, 1)}" fill="{hz(col)}"/>')
    out.append(f'<path d="M {cx:.1f} {base - w * 1.52:.1f} l 0 {-w * 0.14:.1f} M {cx - w * 0.04:.1f} {base - w * 1.6:.1f} l {w * 0.08:.1f} 0" stroke="{hz(dk(col, 0.3))}" stroke-width="2"/>')
    return "".join(out)


@design("la-dolce-vita")
def la_dolce_vita():
    D = Doc2("itdv")
    out = [sky(D, [(0, "#F2A07A"), (0.45, "#F8C890"), (0.8, "#FCE2B0"), (1, "#FFF0CC")], 601, 420, ["#FFD8A8", "#F28A6A", "#FFF2D8"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 420, 330, 260, "#FFF2C0", 0.7))
    for k, (x, y, w) in enumerate(((120, 230, 170), (470, 210, 140))):
        out.append(puff_cloud(D, x, y, w, 602 + k, pal=("#FFE8D0", "#F8C0A0", "#D88A8A"), op=0.7, rows=1))
    # Roman skyline: far dome, bell tower, rooftops, stone pines
    out.append(dome(D, 474, 424, 104, 603, col="#C89A8A", lit="#FFD8B0", haze=0.2))
    out.append(f'<path d="{hg.org_rect(186, 300, 24, 110, 604, 0.3, 8, 1)}" fill="#C8A090"/><path d="M 182 302 L 198 282 L 214 302 Z" fill="#B8786A"/>')
    for k in range(2):
        out.append(f'<path d="M {190 + k * 9} 324 l 0 -12 q 3 -4 6 0 l 0 12 Z" fill="#8A5A50"/>')
    roofs = [(-20, 440, 120, 372), (100, 440, 230, 384), (210, 440, 330, 394), (300, 440, 420, 380), (520, 440, 620, 370)]
    for k, (x0, b, x1, t) in enumerate(roofs):
        c = ["#D8907A", "#E8A880", "#C88068", "#E0A088", "#D89478"][k]
        out.append(painted(D, rect_pts(x0, t, x1, b, 16, 605 + k, 0.5), (lt(c, 0.25), c, dk(c, 0.25)), 605 + k, sdir=(-1, 0.2), sk=0.06, angle=-80, n=12, inkw=0, hi=0.2))
        out.append(f'<path d="{hg.org_rect(x0 - 4, t - 6, x1 - x0 + 8, 8, 610 + k, 0.3, 10, 1)}" fill="#A8503A"/>')
        rr = random.Random(611 + k)
        for j in range(int((x1 - x0) / 26)):
            wx = x0 + 10 + j * 26 + rr.uniform(-3, 3)
            out.append(f'<rect x="{wx:.1f}" y="{t + 12:.1f}" width="7" height="12" fill="{rr.choice(["#6A3A30", "#FFD88A", "#6A3A30"])}"/>')
            out.append(f'<path d="M {wx - 3:.1f} {t + 12:.1f} l 4 -2 l 0 16 l -4 1 Z M {wx + 10:.1f} {t + 12:.1f} l -4 -2 l 0 16 l 4 1 Z" fill="#3E6A4A" opacity="0.8"/>')
    out.append(umbrella_pine(D, 70, 400, 190, 620, light=1, rim="#C8B870"))
    out.append(umbrella_pine(D, 300, 392, 110, 622, pal=("#8A9A70", "#5E7050", "#3E4A34")))
    out.append(f'<rect x="-10" y="330" width="620" height="140" fill="{D.lin([(0, "#F8C890", 0), (1, "#F8C890", 0.35)])}"/>')
    # stone balustrade: rail, vase-shaped balusters, plinth
    out.append(painted(D, rect_pts(-10, 470, 610, 610, 30, 623, 0.6), ("#E8D2B0", "#C8A880", "#8A6A48"), 623, sdir=(0.2, 1), sk=0.08, angle=0, n=40, inkw=0, hi=0.2))
    out.append(f'<rect x="-10" y="470" width="620" height="140" fill="#5A3A20" opacity="0.35"/>')
    for k in range(13):
        x = -6 + k * 50
        prof = [(0, 0), (11, 4), (9, 14), (16, 40), (17, 58), (10, 76), (13, 84), (14, 96), (0, 96)]
        L = [(x - px, 478 + py) for px, py in prof]
        R = [(x + px, 478 + py) for px, py in prof[::-1]]
        out.append(painted(D, L + R, ("#FFF2DC", "#E8D2B0", "#9A7A58"), 626 + k, sdir=(1, 0.2), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.55))
    out.append(painted(D, rect_pts(-10, 572, 610, 610, 30, 640, 0.5), ("#FFF2DC", "#EAD6B8", "#A8906E"), 640, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.6, hi=0.5))
    out.append(painted(D, rect_pts(-10, 446, 610, 478, 30, 624, 0.5), ("#FFF6E6", "#EEDCC0", "#A8906E"), 624, sdir=(0, 1), sk=0.3, angle=0, n=30, inkw=1.8, hi=0.6))
    for k, (x, y) in enumerate(((150, 240), (178, 226), (520, 120), (206, 248))):
        out.append(bird_v(x, y, 9, "#5A2A2A", 0.8))
    # two spritz, a bowl of olives, a little dish of chips
    out.append(spritz_glass(D, 236, 452, 196, 626))
    out.append(spritz_glass(D, 352, 452, 182, 627, olive_=True))
    out.append(cast(D, 470, 454, 56, 8, strength=0.35, seed=628))
    out.append(painted(D, ell_pts(466, 440, 54, 16, 0, 360, 24), ("#FFFFFF", "#F2EAE0", "#B8AEA2"), 629, sdir=(0.3, 1), sk=0.15, n=8, inkw=1.4, hi=0.4))
    for k in range(10):
        out.append(olive(440 + (k % 5) * 12, 432 + (k // 5) * 8 + (k % 2) * 2, 7.5, (k * 37) % 180))
    out.append(f'<path d="{smooth_open(ell_pts(466, 440, 54, 16, 0, 180, 14))}" stroke="#1F4BA8" stroke-width="2.4" fill="none"/>')
    out.append(cast(D, 120, 454, 50, 8, strength=0.35, seed=632))
    out.append(painted(D, ell_pts(120, 442, 48, 14, 0, 360, 22), WHITE, 630, sdir=(0.3, 1), sk=0.15, n=6, inkw=1.4, hi=0.4))
    for k in range(8):
        out.append(f'<path d="{blob(92 + k * 8, 432 + (k % 3) * 2, 9, 5.5, 631 + k, 0.2, 8, k * 30)}" fill="#F6D27A" stroke="#C89A3A" stroke-width="0.8"/>')
    # lettering
    out.append(letters(D, 300, 140, "la dolce vita", SERIF_IT, 112, "#8A2A3A", ["#B03A4A", "#5A1424", "#C85A62"], 640, max_w=460,
                       shadow="#FFE8C8", soff=(0.02, 0.035), angle=-40, hi="#F2A0A0"))
    out.append(ruled(300, 186, "ROMA · AL TRAMONTO", "#7A3A2A", font=JOS, size=19, ls=5, line_w=26, gap=12, max_w=340))
    return finish_i(D, out, 641)


# ================================================================ 10. piano piano — a snail on the garden wall
def snail(D, x, base, s, seed, shell=("#E8B47A", "#B0703A", "#5E3214")):
    """A garden snail, side view, crawling right: soft grey-beige foot with a wet sheen, two eye stalks,
    a spiral shell with banded stripes."""
    rnd = random.Random(seed)
    out = [cast(D, x + 10 * s, base + 2, 110 * s, 8 * s, strength=0.35, seed=seed)]
    body = [(x - 70 * s, base), (x - 60 * s, base - 14 * s), (x - 10 * s, base - 22 * s), (x + 40 * s, base - 26 * s), (x + 62 * s, base - 40 * s),
            (x + 72 * s, base - 62 * s), (x + 86 * s, base - 64 * s), (x + 94 * s, base - 46 * s), (x + 92 * s, base - 22 * s), (x + 80 * s, base - 4 * s), (x + 40 * s, base + 2 * s)]
    bpal = ("#E8DCC8", "#BCA88E", "#6E5A44")
    out.append(painted(D, body, bpal, seed, sdir=(0.2, 1), sk=0.2, angle=-10, n=30, inkw=1.8, hi=0.5, hik=0.12))
    bcid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    tex = "".join(f'<path d="{blob(x + rnd.uniform(-60, 90) * s, base - rnd.uniform(4, 40) * s, rnd.uniform(2, 4) * s, rnd.uniform(1.4, 2.4) * s, rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#9A8670", "#D8CCB8"])}" opacity="0.6"/>' for _ in range(40))
    out.append(f'<g {bcid}>{tex}</g>')
    out.append(taper([(x - 56 * s, base - 10 * s), (x, base - 18 * s), (x + 50 * s, base - 22 * s)], 3 * s, 1.5 * s, "#FFFFFF", 0.65))
    # eye stalks
    for k, (dx, dy, L) in enumerate(((80, -60, 40), (90, -58, 34))):
        tip = (x + (dx + 14) * s, base + (dy - L) * s)
        out.append(taper([(x + dx * s, base + dy * s), ((x + dx * s + tip[0]) / 2 + 3 * s, (base + dy * s + tip[1]) / 2), tip], 6 * s, 3 * s, bpal[1 + k % 2 * 0]))
        out.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="{4.4 * s:.1f}" fill="#5A4836"/><circle cx="{tip[0] - 1.2 * s:.1f}" cy="{tip[1] - 1.4 * s:.1f}" r="{1.4 * s:.1f}" fill="#FFFFFF"/>')
    out.append(taper([(x + 94 * s, base - 30 * s), (x + 104 * s, base - 22 * s)], 3 * s, 1.5 * s, bpal[1]))
    # shell
    scx, scy, R = x + 4 * s, base - 70 * s, 54 * s
    sp = blob_pts(scx, scy, R, R * 0.92, seed + 1, 0.03, 24)
    out.append(painted(D, sp, shell, seed + 1, sdir=(0.6, 0.8), sk=0.2, angle=-40, n=40, inkw=2, hi=0.45))
    scid = D.clip(f'<path d="{smooth_closed(sp)}"/>')
    sw = []
    turns = 3.2
    pts = []
    for i in range(140):
        t = i / 139
        a = -math.pi / 2 + t * turns * 2 * math.pi
        r = R * (1 - t) ** 0.9
        pts.append((scx + 6 * s + r * math.cos(a) * 0.95, scy + 4 * s + r * math.sin(a) * 0.88))
    for k, (w, c, op) in enumerate(((10 * s, shell[2], 0.35), (5 * s, "#FFE8C0", 0.45), (2.4 * s, shell[2], 0.8))):
        sw.append(ink(smooth_open(shift(pts, k * 1.2 * s, k * 1.2 * s)), c, w, seed + k, 1, op))
    for i in range(0, 130, 5):
        x0, y0 = pts[i]
        x1, y1 = pts[min(139, i + 3)]
        a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        L = R * (1 - i / 139) * 0.22
        sw.append(f'<path d="M {x0:.1f} {y0:.1f} l {math.cos(a) * L:.1f} {math.sin(a) * L:.1f}" stroke="{shell[2]}" stroke-width="{max(1, 1.6 * s):.1f}" opacity="0.35"/>')
    sw.append(shade_over(D, smooth_closed(sp), "#2A1206", 0.4, 0, 0, 1, 1, 0.45))
    out.append(f'<g {scid}>{"".join(sw)}</g>')
    out.append(f'<path d="{blob(scx - R * 0.4, scy - R * 0.45, R * 0.22, R * 0.1, seed + 3, 0.2, 10, -40)}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


@design("piano-piano")
def piano_piano():
    D = Doc2("itpp")
    # sun-warmed ochre garden wall with ivy, a stone coping, a terracotta pot of basil
    out = [sky(D, [(0, "#F6DCA8"), (1, "#EAC07E")], 701, 600, ["#FFF0C8", "#D8A060", "#F8E0B0"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(702, ["#D89A50", "#FFF2D0", "#C88A48"], 8, (0, 0, 600, 440), (90, 170), (0.06, 0.12)))
    rnd = random.Random(703)
    for k in range(10):
        x, y = rnd.uniform(0, 600), rnd.uniform(220, 440)
        out.append(f'<path d="{blob(x, y, rnd.uniform(20, 50), rnd.uniform(8, 16), k, 0.2, 10)}" fill="#C88A48" opacity="0.12"/>')
    # ivy trailing down from the top right
    iv = catmull([(620, 40), (560, 90), (530, 170), (548, 260), (520, 330)], 6)
    out.append(pline(iv, "#5A4A2A", 2.4, 704, 0.9, 1))
    for k in range(0, len(iv), 2):
        x, y = iv[k]
        for sg in (-1, 1):
            out.append(leaf_simple(D, x, y, rnd.uniform(18, 28), rnd.uniform(10, 16), 90 + sg * rnd.uniform(30, 70), rnd.choice([VERDE, BASIL]), 705 + k * 2 + sg, vein=True, inkw=1))
    # stone coping and the wall face below (rough ashlar)
    cy0 = 404
    out.append(painted(D, rect_pts(-10, cy0 + 34, 610, 610, 30, 707, 0.6), ("#E8C890", "#D2A868", "#8A6A3A"), 707, sdir=(0.2, 1), sk=0.06, angle=-80, n=50, inkw=0, hi=0.2))
    rr = random.Random(7071)
    for j, y in enumerate(range(cy0 + 34, 610, 44)):
        x = -40 + (j % 2) * 46
        while x < 610:
            w = rr.uniform(70, 100)
            st = hg.org_rect(x + 3, y + 3, w - 6, 38, int(x * 3 + y), 1.2, 10, 6)
            c = mix("#D8B078", rr.choice(["#E8C890", "#C8985A", "#F2D8A8"]), rr.uniform(0.2, 0.6))
            out.append(f'<path d="{st}" fill="{c}"/>')
            out.append(strokes(D.nid(), st, (x, y, x + w, y + 44), [lt(c, 0.2), dk(c, 0.2)], int(x + y), n=6, angle=-5, length=(10, 30), width=(1, 3), opacity=(0.2, 0.45)))
            out.append(ink(st, "#8A6A3A", 1.2, int(x + y), 1, 0.45))
            x += w
    out.append(f'<rect x="-10" y="{cy0 + 34}" width="620" height="40" fill="{D.lin([(0, "#3A2410", 0.35), (1, "#3A2410", 0)])}"/>')
    out.append(painted(D, rect_pts(-10, cy0, 610, cy0 + 36, 30, 706, 0.6), ("#EEE4D2", "#C8B8A0", "#8A7A62"), 706, sdir=(0, 1), sk=0.25, angle=0, n=40, inkw=1.8, hi=0.55))
    # moss and tiny flowers on the coping
    out.append(grass(708, (-10, cy0 - 4, 610, cy0 + 6), ["#7A9A3A", "#9AB050", "#5A7A2A"], n=90, h=(4, 11), w=1.4))
    for x in (40, 70, 530, 556):
        out.append(f'<circle cx="{x}" cy="{cy0 - 2}" r="3.4" fill="#FFFFFF"/><circle cx="{x}" cy="{cy0 - 2}" r="1.3" fill="#F2C21C"/>')
    # the terracotta pot of basil on the left
    px, pb = 124, cy0 + 4
    pot = [(px - 62, pb - 112), (px + 62, pb - 112), (px + 48, pb), (px - 48, pb)]
    out.append(cast(D, px + 18, pb + 2, 70, 9, strength=0.45, seed=709))
    for k, (x, y, L, a) in enumerate(((124, pb - 122, 72, -100), (110, pb - 122, 64, -140), (138, pb - 122, 64, -45), (98, pb - 136, 54, -168),
                                      (150, pb - 136, 54, -12), (124, pb - 170, 46, -90), (112, pb - 160, 40, -128), (138, pb - 160, 40, -55))):
        out.append(basil_leaf(D, x, y, L, a, 710 + k))
    out.append(painted(D, poly_pts(pot, 18, 716, 0.6), TERRA, 716, sdir=(1, 0.3), sk=0.2, angle=-90, n=28, inkw=2, hi=0.45))
    out.append(painted(D, rect_pts(px - 70, pb - 130, px + 70, pb - 106, 14, 717, 0.5), TERRA, 717, sdir=(0.6, 1), sk=0.25, angle=0, n=12, inkw=2, hi=0.5))
    # the snail and its silvery trail
    trail = catmull([(186, cy0 + 4), (250, cy0 + 6), (300, cy0 + 4)], 6)
    out.append(taper(trail, 2, 12, "#FFFFFF", 0.5))
    for k in range(5):
        x, y = trail[min(len(trail) - 1, 1 + k * 2)]
        out.append(sparkle(x, y - 2, 4 + k * 0.6, "#FFFFFF", 0.85))
    out.append(snail(D, 372, cy0 + 2, 1.5, 718))
    out.append(hg.ladybug(D, 532, cy0 - 4, 8, 719, rot=20))
    # lettering
    out.append(letters(D, 300, 142, "piano piano", SERIF_IT, 116, "#2E5A2A", ["#3E7A3A", "#1A3E1A", "#4E8A44"], 720, max_w=440,
                       shadow="#FFF2CC", soff=(0.02, 0.035), angle=-40, hi="#A8D07A"))
    out.append(ruled(300, 190, "SI VA LONTANO", "#9A3A1E", font=JOS, size=22, ls=6, line_w=30, gap=14, max_w=300))
    return finish_i(D, out, 721)


# ================================================================ 11. che bello! — a window, open shutters, geraniums
def geranium(D, cx, cy, r, seed, col=("#FF7A6A", "#E0281E", "#8A0A0A")):
    """A round head of geranium: a dome of five-petalled florets, lit from the top left, a few buds."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy, r * 0.95, r * 0.85, seed, 0.12, 14)}" fill="{col[2]}"/>']
    items = []
    for k in range(int(r * 0.55) + 6):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.8
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85
        lit = -(math.cos(a) * 0.5 + math.sin(a) * 0.8) * rr / r
        items.append((-math.sin(a) * rr, x, y, lit))
    for _, x, y, lit in sorted(items):
        c = col[0] if lit > 0.25 else (dk(col[1], 0.2) if lit < -0.35 else col[1])
        fr = r * rnd.uniform(0.2, 0.26)
        rotf = rnd.uniform(0, 72)
        for j in range(5):
            b = math.radians(j * 72 + rotf)
            out.append(f'<path d="{blob(x + math.cos(b) * fr * 0.55, y + math.sin(b) * fr * 0.55, fr * 0.6, fr * 0.45, rnd.randint(1, 999), 0.12, 8, math.degrees(b))}" fill="{c}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{fr * 0.18:.1f}" fill="{lt(col[0], 0.6)}"/>')
        out.append(ink(blob(x, y, fr * 1.05, fr * 0.95, rnd.randint(1, 999), 0.2, 10), col[2], 0.7, 1, 1, 0.35))
    return "".join(out)


def geranium_leaf(D, x, y, r, seed, col=("#8AC060", "#4A8A34", "#24501A")):
    d = blob(x, y, r, r * 0.86, seed, 0.12, 14)
    out = [f'<path d="{d}" fill="{col[1]}"/>', f'<path d="{blob(x, y, r * 0.6, r * 0.5, seed + 1, 0.15, 12)}" fill="none" stroke="{col[2]}" stroke-width="{max(1.2, r * 0.12):.1f}" opacity="0.45"/>',
           f'<path d="{blob(x - r * 0.3, y - r * 0.3, r * 0.4, r * 0.25, seed + 2, 0.2, 10)}" fill="{col[0]}" opacity="0.6"/>', ink(d, col[2], 1, seed, 1, 0.5)]
    return "".join(out)


@design("che-bello")
def che_bello():
    D = Doc2("itcb")
    wall = ("#F6C88A", "#E8A860", "#A86A2A")
    out = [sky(D, [(0, "#F8D29A"), (1, "#EEB070")], 801, 600, ["#FFE8C0", "#D8904A", "#FFF0D0"], 140, angle=-80, sop=(0.06, 0.18))]
    out.append(blooms(802, ["#D88A40", "#FFF2D0", "#E89A58"], 10, (0, 0, 600, 600), (80, 170), (0.06, 0.12)))
    rnd = random.Random(803)
    for k, (bx_, by_) in enumerate(((84, 540), (530, 548))):
        patch = blob(bx_, by_, 44, 26, 860 + k, 0.25, 14)
        out.append(f'<path d="{patch}" fill="#C8784A"/>')
        pc = D.clip(f'<path d="{patch}"/>')
        br = "".join(f'<path d="{hg.org_rect(bx_ - 60 + i * 22 + (j % 2) * 11, by_ - 30 + j * 10, 20, 8, i * 7 + j, 0.4, 6, 1)}" fill="{rnd.choice(["#D88A5A", "#B8603A", "#E09A6A"])}"/>' for i in range(6) for j in range(7))
        out.append(f'<g {pc}>{br}</g>' + ink(patch, "#9A5A2A", 1.4, 862 + k, 1, 0.5))
    for k in range(6):
        x, y = rnd.uniform(0, 600), rnd.uniform(240, 560)
        out.append(f'<path d="{blob(x, y, rnd.uniform(16, 34), rnd.uniform(8, 14), k, 0.2, 10)}" fill="#F8E2C0" opacity="0.5"/>')
        out.append(f'<path d="{blob(x, y, rnd.uniform(16, 34), rnd.uniform(8, 14), k, 0.2, 10)}" fill="none" stroke="#C8884A" stroke-width="1" opacity="0.35"/>')
    # window: stone frame, glass with a lace curtain, open green shutters
    wx0, wx1, wy0, wy1 = 196, 404, 232, 456
    out.append(f'<path d="{hg.org_rect(wx0 - 18, wy0 - 18, wx1 - wx0 + 36, wy1 - wy0 + 26, 804, 0.5, 12, 2)}" fill="#F4EAD8"/>')
    out.append(ink(hg.org_rect(wx0 - 18, wy0 - 18, wx1 - wx0 + 36, wy1 - wy0 + 26, 804, 0.5, 12, 2), INK, 1.6, 804, 1, 0.5))
    glass = rect_pts(wx0, wy0, wx1, wy1, 16, 805, 0.3)
    out.append(f'<path d="{smooth_closed(glass)}" fill="{D.lin([(0, "#3A4A5A"), (1, "#1E2A36")])}"/>')
    # lace curtain half drawn
    lace = [(wx0, wy0), (wx0 + 96, wy0), (wx0 + 80, wy0 + 100), (wx0 + 54, wy1), (wx0, wy1)]
    out.append(f'<path d="{smooth_closed(lace)}" fill="#FFFFFF" opacity="0.82"/>')
    lcid = D.clip(f'<path d="{smooth_closed(lace)}"/>')
    lp = "".join(f'<circle cx="{wx0 + (i % 8) * 13 + (i // 8 % 2) * 6:.1f}" cy="{wy0 + (i // 8) * 13:.1f}" r="3.6" fill="none" stroke="#C8C0B8" stroke-width="1"/>' for i in range(8 * 18))
    out.append(f'<g {lcid}>{lp}{"".join(pline([(wx0 + 14 + k * 18, wy0), (wx0 + 10 + k * 14, wy1)], "#D8D0C8", 2, k, 0.6, 1) for k in range(5))}</g>')
    out.append(pline([(300, wy0), (300, wy1)], "#F4EAD8", 6, 806, 1, 1) + pline([(wx0, 330), (wx1, 330)], "#F4EAD8", 5, 807, 1, 1))
    out.append(taper([(330, wy0 + 10), (380, wy0 + 70)], 8, 3, "#FFFFFF", 0.25))
    # shutters (persiane), swung open
    for sg in (-1, 1):
        x0 = wx0 - 18 if sg < 0 else wx1 + 18
        x1 = x0 + sg * 96
        sp = poly_pts([(x0, wy0 - 14), (x1, wy0 - 6), (x1, wy1 + 2), (x0, wy1 + 8)], 14, 808 + sg, 0.5)
        out.append(cast(D, x1 + sg * 6, (wy0 + wy1) / 2, 14, 120, strength=0.25, seed=809))
        out.append(painted(D, sp, ("#5AA078", "#2E7050", "#163E2A"), 810 + sg, sdir=(sg * 0.6, 0.6), sk=0.12, angle=-90, n=20, inkw=1.8, hi=0.35))
        for k in range(1, 30):
            y = wy0 - 10 + k * 8
            out.append(pline([(x0 + sg * 8, y), (x1 - sg * 8, y + 1 + sg)], "#163E2A", 1.6, k, 0.55, 1))
            out.append(pline([(x0 + sg * 8, y + 2), (x1 - sg * 8, y + 3 + sg)], "#7AC098", 1, k, 0.45, 1))
        out.append(pline([(x0 + sg * 48, wy0 - 10), (x0 + sg * 48, wy1 + 4)], "#163E2A", 2.2, 811, 0.6, 1))
        out.append(f'<circle cx="{x0 + sg * 4:.1f}" cy="{wy0 + 20}" r="3" fill="#2A2A2A"/><circle cx="{x0 + sg * 4:.1f}" cy="{wy1 - 20}" r="3" fill="#2A2A2A"/>')
    # sill and window box
    out.append(painted(D, rect_pts(wx0 - 30, wy1 + 6, wx1 + 30, wy1 + 22, 14, 812, 0.4), ("#FFFFFF", "#EEE4D2", "#A89A82"), 812, sdir=(0, 1), sk=0.3, angle=0, n=10, inkw=1.6, hi=0.6))
    bx = [(wx0 - 14, wy1 + 22), (wx1 + 14, wy1 + 22), (wx1 + 6, wy1 + 72), (wx0 - 6, wy1 + 72)]
    out.append(painted(D, poly_pts(bx, 16, 813, 0.5), TERRA, 813, sdir=(0.6, 1), sk=0.15, angle=0, n=20, inkw=1.8, hi=0.4))
    for k in range(6):
        out.append(f'<path d="M {wx0 + 4 + k * 38} {wy1 + 34} q 10 8 20 0" stroke="#F6D8B8" stroke-width="2.2" fill="none" opacity="0.8"/>')
    # geraniums: a mound of round zonal leaves, trailing stems, big red and pink heads
    for k in range(9):
        x = wx0 - 6 + k * 27 + rnd.uniform(-4, 4)
        out.append(geranium_leaf(D, x, wy1 + 16 + rnd.uniform(-8, 4), rnd.uniform(18, 24), 814 + k))
    for sg, x0 in ((-1, wx0 - 8), (1, wx1 + 8)):
        tr = catmull([(x0, wy1 + 30), (x0 + sg * 20, wy1 + 50), (x0 + sg * 22, wy1 + 66), (x0 + sg * 14, wy1 + 74)], 4)
        out.append(pline(tr, "#4A7A2A", 2.4, 830 + sg, 0.9, 1))
        for j in (3, 6, 9, 12):
            if j < len(tr):
                out.append(geranium_leaf(D, tr[j][0] + sg * 8, tr[j][1], 13 - j * 0.4, 832 + j + sg))
        out.append(geranium(D, tr[-1][0], tr[-1][1] + 6, 17, 838 + sg, PINK))
    for k, (x, y, r) in enumerate(((wx0 + 14, wy1 - 6, 30), (wx0 + 76, wy1 - 20, 33), (wx0 + 140, wy1 - 8, 30), (wx1 - 12, wy1 - 18, 31))):
        out.append(pline([(x, y + r * 0.8), (x + 3, y + r + 18)], "#4A7A2A", 2.6, k, 0.9, 1))
        out.append(geranium(D, x, y, r, 842 + k, ROSSO if k % 2 == 0 else ("#FF8AA0", "#E8406A", "#9A1A40")))
    # a swallow resting on the open shutter
    out.append(hg.songbird(D, wx1 + 66, wy0 - 30, 30, 849, body="#2A3450", belly="#F6E8D8", flip=-1, beak="#3A2A2A"))
    # lettering
    out.append(letters(D, 300, 140, "che bello!", SERIF_IT, 124, "#1E5A3E", ["#2E7A52", "#0E3A26", "#3E8A60"], 852, max_w=430,
                       shadow="#FFF2D0", soff=(0.02, 0.035), angle=-40, hi="#9AD0A8"))
    out.append(ruled(300, 186, "CHE BELLA GIORNATA", "#A8401E", font=JOS, size=20, ls=5, line_w=26, gap=12, max_w=340))
    return finish_i(D, out, 853)


# ================================================================ 12. a tavola! — the long table under the pergola
def vine_leaf(D, x, y, r, rot_, seed, pal=("#A8C860", "#5E8A34", "#2E4E1A")):
    """Grapevine leaf: five rounded lobes with toothed edge, palmate veins."""
    pts = []
    for i in range(50):
        a = 2 * math.pi * i / 50
        lobe = 1 + 0.22 * math.cos(5 * a) - 0.12 * (1 if math.cos(a - math.pi / 2) > 0.92 else 0)
        tooth = 1 + 0.04 * math.sin(30 * a)
        pts.append((x + r * lobe * tooth * math.cos(a), y + r * lobe * tooth * math.sin(a) * 0.95))
    pts = rot(pts, x, y, rot_)
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>', f'<path d="{blob(x - r * 0.25, y - r * 0.25, r * 0.55, r * 0.4, seed, 0.2, 10)}" fill="{pal[0]}" opacity="0.55"/>']
    for k in range(5):
        a = math.radians(-90 + k * 72 + rot_ + 36)
        out.append(taper([(x, y), (x + math.cos(a) * r * 0.85, y + math.sin(a) * r * 0.85)], max(1, r * 0.06), 0.4, pal[0], 0.7))
    out.append(ink(d, pal[2], max(0.8, r * 0.04), seed, 1, 0.55))
    return "".join(out)


def grape_bunch(D, x, y, s, seed, pal=("#9A6AB0", "#5A2A6A", "#2A0E36")):
    rnd = random.Random(seed)
    out = []
    rows = [5, 5, 4, 4, 3, 2, 1]
    berries = []
    for j, n in enumerate(rows):
        for i in range(n):
            bx = x + (i - (n - 1) / 2) * s * 1.6 + rnd.uniform(-1, 1)
            by = y + j * s * 1.4 + rnd.uniform(-1, 1)
            berries.append((bx, by))
    for bx, by in berries:
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{s:.1f}" fill="{pal[1]}"/><circle cx="{bx + s * 0.25:.1f}" cy="{by + s * 0.25:.1f}" r="{s * 0.75:.1f}" fill="{pal[2]}" opacity="0.5"/>'
                   f'<circle cx="{bx - s * 0.35:.1f}" cy="{by - s * 0.35:.1f}" r="{s * 0.3:.1f}" fill="{pal[0]}" opacity="0.9"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="{s:.1f}" fill="none" stroke="{pal[2]}" stroke-width="0.8" opacity="0.6"/>')
    out.append(pline([(x, y - s * 1.2), (x + 2, y - s * 2.6)], "#6A5A2A", 2, seed, 1, 1))
    return "".join(out)


@design("a-tavola")
def a_tavola():
    D = Doc2("itat")
    # summer evening sky over the garden
    out = [sky(D, [(0, "#3A4A7A"), (0.45, "#8A6A9A"), (0.8, "#F2A88A"), (1, "#FFD8A8")], 901, 380, ["#5A5A8A", "#C88AA0", "#FFC8A8"], 60, angle=-3, sop=(0.06, 0.16))]
    out.append(hg.flakes(902, 14, (60, 50, 540, 140), (0.8, 1.6), "#FFF6E8", (0.5, 0.9)))
    out.append(hill(D, ridge([(-20, 330), (160, 312), (330, 326), (480, 306), (620, 320)], 903, 8, 3), 400, ("#7A7A8A", "#5A5A72", "#3E3E56"), 904, inkw=0, n=20))
    rr = random.Random(905)
    for k in range(9):
        out.append(cypress(D, rr.uniform(20, 580), 326 + rr.uniform(-4, 6), rr.uniform(26, 44), 906 + k, pal=("#5A6A6A", "#3A4A4A", "#24302E"), w=7))
    # garden floor
    out.append(f'<path d="M -10 340 L 610 340 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#5A6A3E"), (1, "#3A4A2A")])}"/>')
    out.append(grass(915, (-10, 344, 610, 610), ["#6A7A44", "#4A5A2E", "#8A9A54"], n=260, h=(8, 20), w=1.6))
    # the table in perspective (vanishing point near 300, 300)
    vx, vy = 300, 292
    near_y, far_y = 600, 352

    def lerp_x(x_near, y):
        t = (y - vy) / (near_y - vy)
        return vx + (x_near - vx) * t
    tl, tr = 92, 508
    top = [(lerp_x(tl, far_y), far_y), (lerp_x(tr, far_y), far_y), (tr + 40, near_y + 30), (tl - 40, near_y + 30)]
    # pergola posts and the string lights
    for k, y in enumerate((356, 400, 470, 590)):
        for sg in (-1, 1):
            x = lerp_x(300 + sg * 290, y)
            h = (y - vy) * 3.1
            out.append(painted(D, rect_pts(x - h * 0.016, y - h, x + h * 0.016, y, 20, 920 + k * 2 + sg, 0.4), WOOD, 920 + k * 2 + sg, sdir=(-sg, 0.2), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.4))
    # table cloth: white with a red runner, falling over the near edge
    out.append(painted(D, top, ("#FFFFFF", "#F4EEE4", "#C8BCAC"), 930, sdir=(0, 1), sk=0.04, angle=0, n=40, inkw=1.6, hi=0.4))
    run = [(lerp_x(272, far_y), far_y), (lerp_x(328, far_y), far_y), (370, near_y + 30), (230, near_y + 30)]
    out.append(checks_band(D, smooth_closed(run), "#D0281E", cell=10, op=0.7))
    # long wooden benches either side
    for sg in (-1, 1):
        bench = [(lerp_x(300 + sg * 236, far_y + 6), far_y + 6), (lerp_x(300 + sg * 262, far_y + 6), far_y + 6), (300 + sg * 400, near_y + 30), (300 + sg * 352, near_y + 30)]
        out.append(painted(D, bench, ("#E8B86A", "#B07A3A", "#5A3A14"), 940 + sg, sdir=(-sg, 0.3), sk=0.15, angle=-80, n=20, inkw=1.4, hi=0.4))
        for k, y in enumerate((380, 420, 480, 560)):
            x = lerp_x(300 + sg * 250, y)
            out.append(pline([(x, y), (x, y + (y - vy) * 0.12)], "#5A3A14", max(1.5, (y - vy) * 0.03), 945 + k, 0.8, 1))
    # dishes along the table: bowls of pasta, bread, wine, candles (diminishing)
    for k, y in enumerate((372, 396, 430, 480, 548)):
        sc = (y - vy) / (near_y - vy)
        for sg in (-1, 1):
            x = lerp_x(300 + sg * 140, y)
            out.append(painted(D, ell_pts(x, y, 40 * sc, 11 * sc, 0, 360, 18), WHITE, 960 + k * 2 + sg, sk=0.15, n=4, inkw=max(0.8, 1.4 * sc), hi=0.4))
            out.append(f'<path d="{blob(x, y - 3 * sc, 24 * sc, 8 * sc, 970 + k, 0.2, 10)}" fill="#EEC864"/><path d="{blob(x - 3 * sc, y - 5 * sc, 12 * sc, 4 * sc, 975 + k, 0.2, 8)}" fill="#D0281E"/>')
            gx = lerp_x(300 + sg * 205, y)
            out.append(f'<path d="M {gx:.1f} {y:.1f} l 0 {-14 * sc:.1f}" stroke="#E8E8E8" stroke-width="{max(1, 1.6 * sc):.1f}"/>'
                       f'<path d="{blob(gx, y - 20 * sc, 7 * sc, 8 * sc, 980 + k, 0.05, 10)}" fill="#8A1A2A" opacity="0.85" stroke="#F2F2F2" stroke-width="{max(0.8, 1.2 * sc):.1f}"/>')
        if k in (1, 3):
            cx_ = lerp_x(300, y)
            out.append(D.glow(cx_, y - 30 * sc, 60 * sc, "#FFD27A", 0.55))
            out.append(f'<rect x="{cx_ - 3 * sc:.1f}" y="{y - 28 * sc:.1f}" width="{6 * sc:.1f}" height="{24 * sc:.1f}" fill="#FFF6E0"/>'
                       f'<path d="{blob(cx_, y - 33 * sc, 3 * sc, 6 * sc, 990 + k, 0.1, 8)}" fill="#FFC040"/>')
        if k in (2, 4):
            bx_ = lerp_x(300 + (40 if k == 2 else -46), y)
            out.append(painted(D, rect_pts(bx_ - 6 * sc, y - 56 * sc, bx_ + 6 * sc, y, 6, 992 + k, 0.3), ("#4A7A4A", "#1E4A2A", "#0A2414"), 992 + k, sk=0.2, n=4, inkw=1, hi=0.5))
            out.append(painted(D, rect_pts(bx_ - 2.6 * sc, y - 76 * sc, bx_ + 2.6 * sc, y - 54 * sc, 6, 995 + k, 0.3), ("#4A7A4A", "#1E4A2A", "#0A2414"), 995 + k, sk=0.2, n=2, inkw=1, hi=0.5))
    # a big bread loaf and a jug of flowers up front
    out.append(cast(D, 300, 540, 90, 16, strength=0.35, seed=996))
    out.append(painted(D, ell_pts(300, 522, 84, 24, 0, 360, 28), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 996, sdir=(0.3, 1), sk=0.12, n=10, inkw=1.6, hi=0.4))
    out.append(ink(smooth_open(ell_pts(300, 524, 76, 19, 10, 170, 14)), "#1F4BA8", 2.4, 996, 1, 0.9))
    out.append(spaghetti_mound(D, 300, 514, 62, 20, 997))
    out.append(painted(D, blob_pts(300, 506, 34, 10, 998, 0.2, 14), ("#F0583A", "#C82214", "#6A0A06"), 998, sk=0.15, n=6, inkw=1, hi=0.4))
    out.append(basil_leaf(D, 300, 502, 22, -70, 999))
    out.append(painted(D, blob_pts(176, 512, 40, 15, 994, 0.06, 16), ("#F2C27A", "#C8843A", "#7A4416"), 994, sdir=(0.4, 1), sk=0.2, angle=-10, n=10, inkw=1.6, hi=0.45))
    for k in range(4):
        out.append(pline([(154 + k * 14, 504), (160 + k * 14, 518)], "#7A4416", 1.6, 990 + k, 0.7, 1))
    # a jug of wildflowers
    jx, jb = 424, 522
    out.append(painted(D, [(jx - 18, jb), (jx - 22, jb - 26), (jx - 14, jb - 44), (jx + 14, jb - 44), (jx + 22, jb - 26), (jx + 18, jb)], ("#FFF6E8", "#F2E2C8", "#B8A07A"), 993,
                       sdir=(0.8, 0.4), sk=0.2, n=8, inkw=1.4, hi=0.5))
    out.append(pline([(jx - 20, jb - 24), (jx, jb - 20), (jx + 20, jb - 24)], "#1F4BA8", 2, 993, 0.9, 1))
    rf = random.Random(992)
    for k in range(9):
        a_ = math.radians(-90 + rf.uniform(-50, 50))
        L = rf.uniform(24, 46)
        fx_, fy_ = jx + math.cos(a_) * L, jb - 44 + math.sin(a_) * L
        out.append(pline([(jx + rf.uniform(-6, 6), jb - 42), (fx_, fy_)], "#5A7A2A", 1.4, k, 0.9, 1))
        col = rf.choice(["#FFFFFF", "#F2C21C", "#E8506A", "#8A6AD0"])
        for j in range(5):
            b_ = math.radians(j * 72)
            out.append(f'<circle cx="{fx_ + math.cos(b_) * 3.2:.1f}" cy="{fy_ + math.sin(b_) * 3.2:.1f}" r="2.6" fill="{col}"/>')
        out.append(f'<circle cx="{fx_:.1f}" cy="{fy_:.1f}" r="1.6" fill="#F2A21E"/>')
    # string lights across under the vine beams
    out.append(string_lights(D, -10, 222, 610, 232, 70, 13, 999))
    out.append(string_lights(D, 40, 300, 560, 300, 26, 9, 1000, r=3))
    # vine canopy across the top with hanging grapes
    for k in range(26):
        x = -20 + k * 26 + rr.uniform(-6, 6)
        y = 22 + rr.uniform(-14, 14) + (24 if k % 5 == 0 else 0)
        out.append(vine_leaf(D, x, y, rr.uniform(20, 30), rr.uniform(-40, 40), 1001 + k))
    for x, y in ((80, 44), (520, 40), (300, 30)):
        out.append(grape_bunch(D, x, y, 5.5, int(x)))
    # lettering
    out.append(letters(D, 300, 156, "a tavola!", SERIF_IT, 124, "#FFF2DA", ["#FFFFFF", "#F6D8C0", "#FFE8D0"], 1030, max_w=420,
                       shadow="#2A2448", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 198, "È PRONTO!", "#FFD8A8", font=JOS, size=22, ls=8, line_w=34, gap=14, max_w=300))
    return finish_i(D, out, 1031)


# ================================================================ 13. basilico — a majolica pot of basil and the pesto mortar
def majolica_pot(D, cx, base, w, h, seed, ground="#FBF4E2"):
    """A Sicilian majolica planter: rounded belly, rolled rim, glossy cream glaze painted with cobalt scrolls,
    a yellow-and-green lemon garland and an orange band."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 14, base + 2, w * 0.62, 10, strength=0.5, seed=seed)]
    prof = []
    for i in range(21):
        t = i / 20
        y = base - h * t
        k = 0.36 + 0.16 * math.sin(math.pi * (0.1 + t * 0.85)) + 0.04 * t
        prof.append((cx + w * k, y))
    pts = prof + [(cx - (x - cx), y) for x, y in prof[::-1]]
    d = smooth_closed(pts)
    out.append(painted(D, pts, (ground, mix(ground, "#E8D8B8", 0.4), "#B8A47E"), seed, sdir=(0.9, 0.3), sk=0.12, angle=-90, n=30, inkw=2, hi=0.5, hik=0.06))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # bands
    for yy, c, th in ((base - h * 0.12, COBALTO[1], 7), (base - h * 0.2, "#F2A21E", 4), (base - h * 0.82, "#F2A21E", 4), (base - h * 0.9, COBALTO[1], 7)):
        inner.append(taper([(cx - w, yy + 3), (cx, yy - 2), (cx + w, yy + 3)], th, th, c, 0.95))
    # cobalt scroll waves
    for k in range(7):
        x = cx - w * 0.6 + k * w * 0.2
        inner.append(pline([(x, base - h * 0.28), (x + w * 0.05, base - h * 0.34), (x + w * 0.1, base - h * 0.3), (x + w * 0.08, base - h * 0.26)], COBALTO[1], 3, seed + k, 0.9, 1))
        inner.append(pline([(x + 2, base - h * 0.76), (x + w * 0.06, base - h * 0.72), (x + w * 0.1, base - h * 0.76)], TURCH[1], 3, seed + k + 9, 0.9, 1))
    # lemon garland in the middle
    for k in range(4):
        lx = cx - w * 0.33 + k * w * 0.22
        ly = base - h * 0.52 + (k % 2) * 8
        for sg in (-1, 1):
            inner.append(f'<path d="{blob(lx + sg * 14, ly - 6, 12, 5, seed + k * 5 + sg, 0.1, 10, sg * 30)}" fill="#3E8A3A"/>')
        lp = [(lx + 16 * math.cos(a) * (1 + 0.25 * abs(math.cos(a)) ** 8), ly + 6 + 11 * math.sin(a)) for a in [2 * math.pi * i / 18 for i in range(18)]]
        inner.append(f'<path d="{smooth_closed(lp)}" fill="#F6C81E"/><path d="{blob(lx + 3, ly + 10, 11, 5, seed + k, 0.1, 8)}" fill="#E0901A" opacity="0.6"/>')
        inner.append(f'<path d="{blob(lx - 5, ly + 2, 5, 2.4, seed + k + 3, 0.1, 8, -15)}" fill="#FFF6C8" opacity="0.9"/>')
        inner.append(ink(smooth_closed(lp), "#9A5A10", 1.1, seed + k, 1, 0.7))
        for j in range(3):
            inner.append(f'<circle cx="{lx + 26:.1f}" cy="{ly - 12 + j * 9:.1f}" r="2.2" fill="{COBALTO[1]}"/>')
    inner.append(shade_over(D, d, "#2A1A06", 0.45, 0, 0, 1, 0, 0.5))
    inner.append(taper([(cx - w * 0.32, base - h * 0.84), (cx - w * 0.38, base - h * 0.5), (cx - w * 0.3, base - h * 0.2)], 9, 3, "#FFFFFF", 0.7))
    inner.append(taper([(cx - w * 0.2, base - h * 0.8), (cx - w * 0.22, base - h * 0.6)], 3, 1, "#FFFFFF", 0.9))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # rolled rim with soil
    rim = ell_pts(cx, base - h, w * 0.5, h * 0.07, 0, 360, 30)
    out.append(painted(D, rim, (ground, mix(ground, "#E8D8B8", 0.4), "#B8A47E"), seed + 1, sdir=(0.5, 1), sk=0.2, n=10, inkw=1.8, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h + 1, w * 0.44, h * 0.05, 0, 360, 28))}" fill="#4A2E1A"/>')
    out.append(specks(seed, (cx - w * 0.4, base - h - 3, cx + w * 0.4, base - h + 4), ["#6A4A2A", "#2A1A0A"], 30, (0.8, 1.8), (0.6, 1)))
    out.append(ink(smooth_open(ell_pts(cx, base - h, w * 0.5, h * 0.07, 10, 170, 14)), COBALTO[1], 3, seed, 1, 0.9))
    return "".join(out)


def basil_plant(D, cx, top_y, w, seed):
    """A lush basil plant: several stems, layered leaves (darker inside, glossy outside), flower spikes."""
    rnd = random.Random(seed)
    out = []
    stems = []
    for k in range(7):
        a = -90 + (k - 3) * 19 + rnd.uniform(-5, 5)
        L = w * rnd.uniform(0.5, 0.68) * (1 - abs(k - 3) * 0.05)
        stems.append((a, L))
    leaves = []
    for k, (a, L) in enumerate(stems):
        ra = math.radians(a)
        pts = [(cx + math.cos(ra) * L * t + rnd.uniform(-2, 2), top_y + math.sin(ra) * L * t) for t in (0, 0.4, 0.75, 1)]
        out.append(taper(catmull(pts, 4), 6, 3, "#5A8A3A"))
        for j, t in enumerate((0.3, 0.55, 0.78, 0.98)):
            px, py = cx + math.cos(ra) * L * t, top_y + math.sin(ra) * L * t
            s = w * (0.36 - 0.08 * t) * rnd.uniform(0.85, 1.1)
            for sg in (-1, 1):
                leaves.append((t + rnd.uniform(0, 0.1), px, py, s, a + sg * rnd.uniform(40, 75), rnd.randint(1, 9999), j))
    for t, px, py, s, aa, sd, j in sorted(leaves, key=lambda q: q[0]):
        pal = BASIL if t > 0.5 else (lt(BASIL[0], 0.0), dk(BASIL[1], 0.15), BASIL[2])
        out.append(basil_leaf(D, px, py, s, aa, sd, pal, inkw=1.0))
    # two little white flower spikes
    for k, (a, L) in enumerate(()):
        ra = math.radians(a)
        x, y = cx + math.cos(ra) * L * 1.08, top_y + math.sin(ra) * L * 1.08
        for j in range(6):
            out.append(f'<path d="{blob(x + rnd.uniform(-3, 3), y - j * 6, 3.4, 2.4, k * 9 + j, 0.2, 8)}" fill="#FFFFFF" stroke="#C8B8C8" stroke-width="0.8"/>')
    return "".join(out)


def mortar(D, cx, base, w, seed):
    """A marble mortar (mortaio) full of bright pesto with a wooden pestle."""
    h = w * 0.55
    out = [cast(D, cx + 8, base + 2, w * 0.62, 8, strength=0.45, seed=seed)]
    body = [(cx - w / 2, base - h), (cx - w * 0.48, base - h * 0.5), (cx - w * 0.36, base - h * 0.08), (cx - w * 0.3, base), (cx + w * 0.3, base),
            (cx + w * 0.36, base - h * 0.08), (cx + w * 0.48, base - h * 0.5), (cx + w / 2, base - h)]
    out.append(painted(D, body, ("#FFFFFF", "#E8E4DC", "#A8A098"), seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=16, inkw=1.8, hi=0.5))
    for k in range(4):
        out.append(pline([(cx - w * 0.4 + k * 20, base - h * 0.9), (cx - w * 0.35 + k * 22, base - h * 0.5), (cx - w * 0.3 + k * 18, base - h * 0.1)], "#B8B0C0", 1, seed + k, 0.5, 1))
    out.append(painted(D, ell_pts(cx, base - h, w / 2, h * 0.2, 0, 360, 24), ("#FFFFFF", "#E8E4DC", "#A8A098"), seed + 1, sk=0.2, n=6, inkw=1.6, hi=0.5))
    out.append(painted(D, ell_pts(cx, base - h + 2, w * 0.42, h * 0.14, 0, 360, 24), ("#A8D870", "#5A9A2A", "#2A5A12"), seed + 2, sdir=(0.3, 1), sk=0.2, n=10, inkw=0, hi=0.4))
    out.append(specks(seed, (cx - w * 0.36, base - h - 6, cx + w * 0.36, base - h + 8), ["#2A5A12", "#E8E0A0", "#8AC060"], 30, (0.8, 1.8), (0.6, 1)))
    out.append(wooden_spoon(D, cx + w * 0.7, base - h * 2.2, cx + w * 0.05, base - h * 0.95, seed + 3, bowl=False, w=w * 0.16))
    return "".join(out)


@design("basilico")
def basilico():
    D = Doc2("itbs")
    out = [sky(D, [(0, "#CFE8E2"), (1, "#A8D4CC")], 1101, 600, ["#E8F6F2", "#8AC4BA", "#D8F0EA"], 110, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(1102, ["#8AC4BA", "#FFFFFF", "#B8DED6"], 8, (0, 0, 600, 460), (90, 170), (0.06, 0.12)))
    out.append(soft_glow(D, 200, 300, 300, "#FFFBE8", 0.5))
    # wooden sill
    out.append(wood_planks(D, 470, 600, 1103, WOOD, 2))
    out.append(painted(D, rect_pts(-10, 456, 610, 476, 30, 1104, 0.5), ("#E8B880", "#B88048", "#6A421E"), 1104, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.6, hi=0.5))
    out.append(f'<rect x="-10" y="476" width="620" height="16" fill="#3A2010" opacity="0.3"/>')
    # the pot and the plant
    out.append(basil_plant(D, 250, 328, 150, 1105))
    out.append(majolica_pot(D, 250, 492, 200, 172, 1106))
    # mortar with pesto, pine nuts, garlic and a wedge of cheese to the right
    out.append(mortar(D, 440, 486, 112, 1107))
    rnd = random.Random(1108)
    for k in range(9):
        x, y = rnd.uniform(380, 520), rnd.uniform(500, 530)
        out.append(f'<path d="{blob(x, y, 4.4, 2.6, k, 0.2, 8, rnd.uniform(0, 180))}" fill="#F2DCA0" stroke="#B8985A" stroke-width="0.8"/>')
    out.append(garlic_clove(D, 400, 532, 18, 1109, rot_=20))
    out.append(basil_leaf(D, 500, 530, 36, -160, 1110))
    out.append(basil_leaf(D, 108, 524, 34, -20, 1111))
    out.append(basil_leaf(D, 120, 530, 28, 30, 1112))
    # lettering
    out.append(letters(D, 300, 146, "basilico", SERIF_IT, 112, "#1E6A34", ["#2E8A44", "#0E4A22", "#4AA058"], 1113, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8E0A8"))
    out.append(ruled(300, 190, "PROFUMO DI CASA", "#1F4BA8", font=JOS, size=22, ls=6, line_w=30, gap=14, max_w=300))
    return finish_i(D, out, 1114)


# ================================================================ 14. al mercato — the market stall under the striped awning
def artichoke(D, cx, cy, r, seed):
    """Carciofo: layered pointed bracts in green-violet, tips tinged purple, a cut stem."""
    rnd = random.Random(seed)
    out = [taper([(cx + 2, cy + r * 0.8), (cx + 4, cy + r * 1.4)], r * 0.3, r * 0.22, "#8A9A5A")]
    for ring, (rr, n) in enumerate(((1.0, 9), (0.78, 8), (0.55, 6), (0.32, 4))):
        for k in range(n):
            a = math.radians(-90 + (k - (n - 1) / 2) * (300 / n) + ring * 10)
            bx, by = cx + math.cos(a) * r * rr * 0.55, cy + math.sin(a) * r * rr * 0.6 + r * 0.15
            br = [(bx - r * 0.2, by + r * 0.15), (bx - r * 0.18, by - r * 0.2), (bx, by - r * 0.38), (bx + r * 0.18, by - r * 0.2), (bx + r * 0.2, by + r * 0.15)]
            br = rot(br, bx, by, math.degrees(a) + 90)
            out.append(painted(D, br, ("#B8C890", "#7A9A5A", "#3E5A2A"), seed + ring * 20 + k, sdir=(0.5, 0.8), sk=0.2, angle=-90, n=3, inkw=0.9, hi=0.4))
            tip = br[2]
            out.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="{r * 0.08:.1f}" fill="#7A3A6A" opacity="0.7"/>')
    return "".join(out)


def crate(D, x, y, w, h, seed, fill_fn=None):
    """Wooden market crate (cassetta) seen from the front, slightly from above."""
    out = [cast(D, x + w / 2 + 6, y + h + 2, w * 0.58, 8, strength=0.4, seed=seed)]
    pal = ("#F2D29A", "#D2A262", "#7A5228")
    back = rect_pts(x + 4, y - h * 0.25, x + w - 4, y + 2, 10, seed, 0.3)
    out.append(painted(D, back, (dk(pal[0], 0.2), dk(pal[1], 0.25), pal[2]), seed + 1, sdir=(0, 1), sk=0.15, angle=0, n=6, inkw=1.2, hi=0.2))
    if fill_fn:
        out.append(fill_fn(x, y, w))
    for k in range(3):
        sl = rect_pts(x, y + k * h / 3 + 1, x + w, y + (k + 1) * h / 3 - 2, 12, seed + k, 0.3)
        out.append(painted(D, sl, pal, seed + 5 + k, sdir=(0, 1), sk=0.15, angle=0, n=8, slen=(10, 30), sw=(0.6, 1.4), inkw=1.3, hi=0.4))
    for sx in (x + 4, x + w - 10):
        out.append(painted(D, rect_pts(sx, y - 2, sx + 6, y + h, 8, seed + int(sx), 0.2), pal, seed + int(sx), sk=0.2, n=3, inkw=1.1, hi=0.3))
    return "".join(out)


def oil_bottle(D, cx, base, h, seed):
    """Square-shouldered glass bottle of green-gold olive oil with a cork and a paper label with an olive sprig."""
    w = h * 0.28
    out = [cast(D, cx + 6, base + 1, w * 0.7, 5, strength=0.4, seed=seed)]
    body = [(cx - w / 2, base), (cx - w / 2, base - h * 0.62), (cx - w * 0.3, base - h * 0.72), (cx - w * 0.17, base - h * 0.76), (cx - w * 0.17, base - h * 0.94),
            (cx + w * 0.17, base - h * 0.94), (cx + w * 0.17, base - h * 0.76), (cx + w * 0.3, base - h * 0.72), (cx + w / 2, base - h * 0.62), (cx + w / 2, base)]
    out.append(painted(D, body, ("#E8E070", "#A8A020", "#4A5008"), seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.5, hik=0.15))
    out.append(taper([(cx - w * 0.3, base - h * 0.08), (cx - w * 0.32, base - h * 0.6)], w * 0.12, w * 0.06, "#FFFBD8", 0.7))
    out.append(painted(D, rect_pts(cx - w * 0.15, base - h * 1.02, cx + w * 0.15, base - h * 0.93, 4, seed, 0.2), ("#E8C08A", "#B8864E", "#6A4420"), seed + 1, sk=0.2, n=3, inkw=1.1, hi=0.4))
    lab = rect_pts(cx - w * 0.42, base - h * 0.48, cx + w * 0.42, base - h * 0.18, 6, seed, 0.3)
    out.append(painted(D, lab, ("#FFFDF0", "#F2E6C8", "#B8A27A"), seed + 2, sk=0.15, n=4, inkw=1.1, hi=0.3))
    lx, ly = cx, base - h * 0.33
    out.append(pline([(lx - w * 0.25, ly + 4), (lx + w * 0.25, ly - 4)], "#5A6A2A", 1.4, seed, 0.9, 1))
    for k in range(3):
        out.append(f'<path d="{blob(lx - w * 0.12 + k * w * 0.14, ly + 1 - k * 2.4, w * 0.08, w * 0.03, seed + k, 0.1, 8, -30 + k * 40)}" fill="#7A8A4A"/>')
    out.append(olive(lx + w * 0.05, ly + 5, w * 0.05, 20, ("#7A6A8A", "#3A2A4A", "#1A0E22")))
    return "".join(out)


@design("al-mercato")
def al_mercato():
    D = Doc2("itam")
    out = [sky(D, [(0, "#F6E6C8"), (1, "#E8CFA4")], 1201, 600, ["#FFF6E0", "#D8B47E", "#F8E8C8"], 100, angle=-80, sop=(0.06, 0.14))]
    out.append(blooms(1202, ["#D8B47E", "#FFFFFF"], 6, (0, 0, 600, 600), (90, 170), (0.06, 0.12)))
    # striped awning with a scalloped valance across the top
    aw = "M -10 -10 L 610 -10 L 610 66 L -10 66 Z"
    out.append(stripes_in(D, aw, (-10, -10, 610, 66), 0, [40, 40], ["#D8322A", "#FFF8EC"], 1203))
    sc = [(-10, 66)]
    for k in range(16):
        x = -10 + k * 40
        sc += [(x + 20 * (1 - math.cos(math.radians(t))) , 66 + 22 * math.sin(math.radians(t))) for t in range(0, 181, 30)]
    sc += [(630, 66), (630, 50), (-10, 50)]
    vd = pd(sc)
    out.append(stripes_in(D, vd, (-10, 50, 630, 90), 0, [40, 40], ["#D8322A", "#FFF8EC"], 1204))
    out.append(ink(smooth_open(sc[:-3]), "#7A1A10", 1.6, 1205, 1, 0.7))
    out.append(f'<rect x="-10" y="-10" width="620" height="100" fill="{D.lin([(0, "#3A1A0A", 0), (0.7, "#3A1A0A", 0), (1, "#3A1A0A", 0.15)])}"/>')
    out.append(f'<path d="{vd}" fill="{D.lin([(0, "#FFFFFF", 0.2), (1, "#5A1A0A", 0.25)])}"/>')
    # chalkboard sign hanging on two strings
    for x in (196, 404):
        out.append(pline([(x, 80), (x + (300 - x) * 0.05, 112)], "#5A4A3A", 1.8, x, 1, 1))
    bd = rect_pts(150, 108, 450, 242, 20, 1206, 0.6)
    out.append(cast(D, 308, 248, 160, 12, strength=0.3, seed=1206))
    out.append(painted(D, bd, ("#C89A62", "#9A6A38", "#5A3A18"), 1207, sdir=(0.5, 1), sk=0.12, angle=0, n=20, inkw=2, hi=0.4))
    inner_b = rect_pts(162, 120, 438, 230, 20, 1208, 0.5)
    out.append(painted(D, inner_b, ("#3E4A44", "#26302C", "#121816"), 1208, sdir=(0.5, 1), sk=0.06, angle=-20, n=40, inkw=0, hi=0.1))
    out.append(strokes(D.nid(), smooth_closed(inner_b), (160, 118, 440, 232), ["#FFFFFF"], 1209, n=40, angle=-15, length=(20, 60), width=(2, 6), opacity=(0.03, 0.08)))
    out.append(hg.chalk_text(D, 300, 196, "al mercato", SERIF_IT, 70, "#FFFDF4", 1210, max_w=250))
    out.append(label(300, 222, "FRUTTA · VERDURA · OLIO", JOS, 15, "#F6D27A", ls=2, max_w=250))
    # the counter: crates of tomatoes, lemons and artichokes, bowls of olives, oil bottles
    out.append(painted(D, rect_pts(-10, 500, 610, 610, 30, 1211, 0.5), NOCE, 1211, sdir=(0, 1), sk=0.1, angle=0, n=40, inkw=1.6, hi=0.3))
    out.append(stripes_in(D, "M -10 500 L 610 500 L 610 610 L -10 610 Z", (-10, 500, 610, 610), 0, [24, 24], [None, "#5A3418"], 1212, op=0.25))

    def tomatoes(x, y, w):
        o = []
        for j, (dx, dy, r) in enumerate(((0.2, -14, 22), (0.5, -18, 24), (0.8, -12, 22), (0.34, -34, 21), (0.66, -36, 22), (0.5, -52, 20))):
            o.append(tomato(D, x + w * dx, y + dy, r, 1220 + j + int(x)))
        return "".join(o)

    def lemons(x, y, w):
        o = []
        for j, (dx, dy, r, a) in enumerate(((0.25, -12, 17, 10), (0.6, -14, 17, -12), (0.85, -10, 15, 30), (0.42, -32, 16, -20), (0.72, -34, 16, 14))):
            o.append(lemon_it(D, x + w * dx, y + dy, r, 1230 + j + int(x), rot_=a))
        o.append(citrus_leaf(D, x + w * 0.1, y - 30, 34, -60, 1236))
        return "".join(o)

    def artichokes(x, y, w):
        o = []
        for j, (dx, dy, r) in enumerate(((0.25, -26, 26), (0.72, -24, 26), (0.5, -44, 25))):
            o.append(artichoke(D, x + w * dx, y + dy, r, 1240 + j * 9))
        return "".join(o)
    out.append(painted(D, rect_pts(-10, 380, 610, 400, 30, 1253, 0.5), NOCE, 1253, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.4, hi=0.4))
    out.append(f'<rect x="-10" y="400" width="620" height="100" fill="{D.lin([(0, "#5A3418", 0.45), (1, "#5A3418", 0.15)])}"/>')
    out.append(crate(D, 96, 312, 176, 72, 1250, tomatoes))
    out.append(crate(D, 328, 312, 176, 72, 1251, artichokes))
    out.append(crate(D, 196, 420, 208, 76, 1252, lemons))
    # olive bowls and the oil
    for k, (x, col) in enumerate(((112, ("#B8C060", "#7A8A2A", "#3E4A12")), (488, ("#7A6A8A", "#3A2A4A", "#1A0E22")))):
        out.append(cast(D, x + 4, 542, 54, 9, strength=0.4, seed=1260 + k))
        out.append(painted(D, ell_pts(x, 522, 52, 15, 0, 360, 24), ("#F6E2C2", "#E0B888", "#8A6A42"), 1261 + k, sdir=(0.3, 1), sk=0.15, n=8, inkw=1.4, hi=0.4))
        out.append(painted(D, [(x - 52, 522), (x - 40, 544), (x + 40, 544), (x + 52, 522)], TERRA, 1262 + k, sdir=(0.5, 1), sk=0.2, n=8, inkw=1.6, hi=0.4))
        for j in range(13):
            out.append(olive(x - 38 + (j % 7) * 12.5, 514 + (j // 7) * 9 + (j % 2) * 2, 7.5, (j * 41) % 180, col))
    out.append(oil_bottle(D, 404, 534, 112, 1265))
    out.append(oil_bottle(D, 192, 536, 96, 1266))
    # garlic braid hanging from the awning on the left, peppers on the right
    for k in range(5):
        out.append(garlic(D, 60 + (k % 2) * 10, 130 + k * 34, 15, 1270 + k, rot_=(k % 2) * 16 - 8))
    for k in range(6):
        x, y = 536 + (k % 2) * 12, 120 + k * 30
        out.append(painted(D, rot([(x - 6, y), (x + 6, y), (x + 4, y + 26), (x, y + 34), (x - 4, y + 26)], x, y, (k % 2) * 20 - 10), ("#FF7A5A", "#D8221A", "#7A0A06"), 1280 + k, sk=0.2, n=4, inkw=1.1, hi=0.5))
        out.append(f'<path d="M {x} {y} l 0 -6" stroke="#3E6A2A" stroke-width="3"/>')
    out.append(pline([(66, 92), (66, 300)], "#B89A60", 2, 1290, 0.8, 1) + pline([(540, 92), (542, 300)], "#B89A60", 2, 1291, 0.8, 1))
    return finish_i(D, out, 1292)


# ================================================================ 15. buon natale — panettone, a slice, and the Christmas lights
def panettone(D, cx, base, w, h, seed):
    """Tall domed panettone in its brown-gold paper case: cracked glossy top with a cross cut, a ribbon."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 10, base + 4, w * 0.62, 12, strength=0.5, seed=seed)]
    # paper case (fluted)
    case = [(cx - w / 2, base - h * 0.62), (cx + w / 2, base - h * 0.62), (cx + w * 0.48, base - 4), (cx + w * 0.4, base), (cx - w * 0.4, base), (cx - w * 0.48, base - 4)]
    out.append(painted(D, case, ("#F6E2B0", "#D8B070", "#8A6428"), seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=14, inkw=2, hi=0.45))
    ccid = D.clip(f'<path d="{smooth_closed(case)}"/>')
    fl = []
    for k in range(34):
        x = cx - w * 0.5 + k * w / 33
        fl.append(f'<path d="M {x:.1f} {base - h * 0.62:.1f} L {x * 0.985 + cx * 0.015:.1f} {base:.1f}" stroke="{"#FFF6DC" if k % 2 else "#A8803A"}" stroke-width="{2.2 if k % 2 else 1.2}" opacity="{0.55 if k % 2 else 0.5}"/>')
    # printed pattern on the paper: little gold stars and dots
    for j in range(3):
        for k in range(7):
            x = cx - w * 0.4 + k * w * 0.133 + (j % 2) * w * 0.066
            y = base - h * 0.5 + j * h * 0.15
            if abs(y - (base - h * 0.32)) < h * 0.07:
                continue
            fl.append(f'<path d="{pd(hg.star_pts(x, y, 6, 2.6))}" fill="#B8862A" opacity="0.8"/>')
    fl.append(shade_over(D, smooth_closed(case), "#3A2006", 0.45, 0, 0, 1, 0, 0.45))
    out.append(f'<g {ccid}>{"".join(fl)}</g>')
    # gold paper rim and red ribbon with a bow
    out.append(painted(D, rect_pts(cx - w / 2 - 2, base - h * 0.66, cx + w / 2 + 2, base - h * 0.58, 10, seed, 0.3), ("#FFE89A", "#E2B240", "#9A6A10"), seed + 1, sdir=(0, 1), sk=0.25, n=8, inkw=1.4, hi=0.6))
    out.append(painted(D, rect_pts(cx - w / 2 - 1, base - h * 0.36, cx + w / 2 + 1, base - h * 0.27, 10, seed + 2, 0.3), ROSSO, seed + 2, sdir=(0, 1), sk=0.25, n=8, inkw=1.4, hi=0.5))
    bx, by = cx + w * 0.12, base - h * 0.32
    for sg in (-1, 1):
        lp = [(bx, by), (bx + sg * 30, by - 22), (bx + sg * 40, by - 8), (bx + sg * 32, by + 10)]
        out.append(painted(D, lp, ROSSO, seed + 3 + sg, sk=0.25, n=4, inkw=1.4, hi=0.5))
        out.append(painted(D, [(bx, by), (bx + sg * 12, by + 34), (bx + sg * 22, by + 30)], ROSSO, seed + 5 + sg, sk=0.25, n=3, inkw=1.2, hi=0.4))
    out.append(painted(D, blob_pts(bx, by, 9, 8, seed + 8, 0.05, 10), ROSSO, seed + 8, sk=0.2, n=3, inkw=1.2, hi=0.5))
    # dome: glossy dark crust, mushrooming over the case, a cross-shaped cut
    dome = [(cx - w * 0.54, base - h * 0.64), (cx - w * 0.56, base - h * 0.78)] + [(cx - w * 0.54 * math.cos(math.radians(t)), base - h * 0.78 - h * 0.24 * math.sin(math.radians(t))) for t in range(15, 166, 15)] + \
           [(cx + w * 0.56, base - h * 0.78), (cx + w * 0.54, base - h * 0.64), (cx, base - h * 0.62)]
    out.append(painted(D, dome, ("#C8783A", "#8A4416", "#3E1A06"), seed + 9, sdir=(0.6, 0.8), sk=0.15, angle=-20, n=30, inkw=2, hi=0.55, hik=0.12))
    dcid = D.clip(f'<path d="{smooth_closed(dome)}"/>')
    di = []
    for k in range(14):
        x = cx + rnd.uniform(-0.45, 0.45) * w
        y = base - h * rnd.uniform(0.7, 0.95)
        di.append(pline([(x, y), (x + rnd.uniform(-10, 10), y + rnd.uniform(-4, 4)), (x + rnd.uniform(-16, 16), y + rnd.uniform(-5, 5))], "#E8B070", 1.6, k, 0.6, 1))
    di.append(taper([(cx - w * 0.36, base - h * 0.84), (cx - w * 0.18, base - h * 0.96), (cx + w * 0.04, base - h * 1.0)], 7, 2, "#F8C890", 0.6))
    out.append(f'<g {dcid}>{"".join(di)}</g>')
    # cross cut, opened and paler
    for a, b in (((cx - w * 0.22, base - h * 0.86), (cx + w * 0.22, base - h * 0.86)), ((cx, base - h * 0.78), (cx + 2, base - h * 0.98))):
        out.append(taper([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 2), b], 8, 8, "#F2C878", 0.95))
        out.append(taper([a, b], 2, 2, "#8A4416", 0.6))
    # pearl sugar
    for _ in range(18):
        out.append(f'<circle cx="{cx + rnd.uniform(-0.4, 0.4) * w:.1f}" cy="{base - h * rnd.uniform(0.74, 0.98):.1f}" r="{rnd.uniform(1.2, 2.2):.1f}" fill="#FFFDF4"/>')
    return "".join(out)


def panettone_slice(D, x, base, s, seed):
    """A tall wedge cut from the panettone: airy yellow crumb dotted with raisins and candied orange cubes."""
    rnd = random.Random(seed)
    face = [(x, base), (x + s, base - 2), (x + s * 0.98, base - s * 0.8), (x + s * 0.55, base - s * 1.04), (x + s * 0.05, base - s * 0.86)]
    out = [cast(D, x + s * 0.55, base + 2, s * 0.7, 7, strength=0.45, seed=seed)]
    out.append(painted(D, face, ("#FFF2B0", "#F6D26A", "#C8A040"), seed, sdir=(0.6, 0.8), sk=0.12, angle=-90, n=14, inkw=1.6, hi=0.3))
    fc = D.clip(f'<path d="{smooth_closed(face)}"/>')
    inner = []
    for _ in range(40):
        inner.append(f'<path d="{blob(x + rnd.uniform(0.05, 0.95) * s, base - rnd.uniform(0.05, 0.95) * s, rnd.uniform(1, 3), rnd.uniform(1.4, 4), rnd.randint(1, 999), 0.3, 6)}" fill="#C8A040" opacity="0.6"/>')
    for _ in range(14):
        inner.append(f'<path d="{blob(x + rnd.uniform(0.1, 0.9) * s, base - rnd.uniform(0.1, 0.85) * s, rnd.uniform(3, 4.5), rnd.uniform(2.4, 3.6), rnd.randint(1, 999), 0.2, 8)}" fill="#4A1A16"/>')
    for _ in range(9):
        cx_, cy_ = x + rnd.uniform(0.1, 0.9) * s, base - rnd.uniform(0.1, 0.85) * s
        inner.append(f'<path d="{hg.org_rect(cx_ - 4, cy_ - 4, 8, 7, rnd.randint(1, 999), 0.5, 6, 1.5)}" fill="{rnd.choice(["#F2861A", "#E8A01A", "#5AA040"])}" opacity="0.95"/>')
    inner.append(taper([(x + s * 0.06, base - s * 0.86), (x + s * 0.55, base - s * 1.04), (x + s * 0.98, base - s * 0.8)], 10, 10, "#8A4416", 1))
    out.append(f'<g {fc}>{"".join(inner)}</g>')
    out.append(taper([(x + 1, base - 1), (x + s, base - 3)], 6, 6, "#B87A3A", 0.9))
    return "".join(out)


@design("buon-natale")
def buon_natale():
    D = Doc2("itbn")
    out = [sky(D, [(0, "#1E4A36"), (1, "#123426")], 1301, 600, ["#2E6A4A", "#0A2418", "#3E7A5A"], 120, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 330, 300, "#FFD88A", 0.32))
    # warm bokeh lights behind
    rnd = random.Random(1302)
    for k in range(26):
        x, y = rnd.uniform(0, 600), rnd.uniform(200, 440)
        r = rnd.uniform(8, 22)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#FFD27A", "#FFB060", "#FFF0C0"])}" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>')
    out.append(string_lights(D, -10, 222, 610, 214, 46, 12, 1303))
    # wooden board on a red table runner
    out.append(painted(D, rect_pts(-10, 470, 610, 610, 30, 1304, 0.5), ("#C8302A", "#9A1A16", "#5A0A08"), 1304, sdir=(0, 1), sk=0.1, angle=0, n=40, inkw=0, hi=0.2))
    for k in range(12):
        out.append(f'<path d="M {k * 54 - 10} 474 l 30 0" stroke="#F6D27A" stroke-width="3" opacity="0.6"/>')
    out.append(cast(D, 300, 520, 230, 18, strength=0.45, seed=1305))
    out.append(painted(D, ell_pts(300, 500, 214, 30, 0, 360, 36), ("#E8B880", "#B88048", "#6A421E"), 1306, sdir=(0.3, 1), sk=0.15, angle=0, n=30, inkw=1.8, hi=0.4))
    # pine sprigs and a few red berries on the board edges
    for k, (x0, y0, x1, y1) in enumerate(((60, 494, 150, 470), (82, 506, 170, 512), (540, 494, 452, 474), (520, 508, 430, 514))):
        out.append(hg.pine_sprig(D, x0, y0, x1, y1, 1307 + k))
    for x, y in ((150, 496), (160, 488), (442, 494), (452, 486), (446, 502)):
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#D8221A"/><circle cx="{x - 1.6}" cy="{y - 1.6}" r="1.6" fill="#FFFFFF" opacity="0.8"/>')
    out.append(panettone(D, 262, 500, 190, 250, 1310))
    out.append(panettone_slice(D, 362, 516, 84, 1311))
    # a small star ornament hanging and a sparkle
    out.append(hg.star_painted(D, 480, 300, 18, 1312))
    out.append(pline([(480, 214), (480, 284)], "#E2B240", 1.4, 1313, 0.9, 1))
    for x, y, r in ((520, 380, 7), (90, 330, 6), (130, 420, 5)):
        out.append(sparkle(x, y, r, "#FFF2C0", 0.85))
    # lettering
    out.append(letters(D, 300, 142, "Buon Natale", SERIF_IT, 118, "#FFE8B0", ["#FFF6D8", "#F2C860", "#FFE8A0"], 1314, max_w=440,
                       shadow="#08180E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 188, "CON TUTTA LA FAMIGLIA", "#F2C860", font=JOS, size=19, ls=5, line_w=26, gap=12, max_w=340))
    return finish_i(D, out, 1315, "#08180E", 0.7)


# ================================================================ 16. gelato — the gelateria counter and a cone to go
def gelato_tub(D, x, y, w, d, flavour, seed):
    """A steel gelato tub seen from above at an angle, heaped with sculpted waves, garnished on top."""
    col, garn = flavour
    rnd = random.Random(seed)
    out = []
    tub = rect_pts(x, y, x + w, y + d, 10, seed, 0.3)
    out.append(painted(D, tub, ALU, seed, sdir=(0, 1), sk=0.15, n=6, inkw=1.4, hi=0.5))
    heap = [(x + 4, y + d - 2)]
    for k in range(9):
        t = k / 8
        heap.append((x + 4 + (w - 8) * t, y + d * 0.2 - math.sin(math.pi * t) * d * 0.55 - rnd.uniform(0, d * 0.15)))
    heap.append((x + w - 4, y + d - 2))
    out.append(painted(D, heap, (lt(col, 0.35), col, dk(col, 0.3)), seed + 1, sdir=(0.3, 1), sk=0.18, angle=-20, n=14, inkw=1.4, hi=0.45))
    for k in range(4):
        xx = x + 12 + k * (w - 24) / 3
        out.append(pline([(xx, y + d * 0.6), (xx + 8, y + d * 0.1 - k % 2 * 4), (xx + 16, y + d * 0.5)], dk(col, 0.25), 1.6, seed + k, 0.6, 1))
        out.append(pline([(xx + 2, y + d * 0.5), (xx + 8, y + d * 0.05 - k % 2 * 4)], lt(col, 0.5), 1.4, seed + k + 9, 0.7, 1))
    out.append(garn(x + w / 2, y + d * 0.05 - d * 0.35, w))
    return "".join(out)


@design("gelato")
def gelato():
    D = Doc2("itgl")
    out = [paper(D.nid(), "#FCE8E4", "#8A4A4A", 1401)]
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-10, -10, 610, 610), 0, [30, 30], [None, "#F8D2CC"], 1402, op=0.6))
    # pink awning valance at top
    aw = "M -10 -10 L 610 -10 L 610 52 L -10 52 Z"
    out.append(stripes_in(D, aw, (-10, -10, 610, 52), 0, [36, 36], ["#E8607A", "#FFF8F0"], 1403))
    sc = [(-10, 52)]
    for k in range(18):
        x = -10 + k * 36
        sc += [(x + 18 * (1 - math.cos(math.radians(t))), 52 + 18 * math.sin(math.radians(t))) for t in range(0, 181, 30)]
    sc += [(640, 52), (640, 40), (-10, 40)]
    out.append(stripes_in(D, pd(sc), (-10, 40, 640, 72), 0, [36, 36], ["#E8607A", "#FFF8F0"], 1404))
    out.append(ink(smooth_open(sc[:-3]), "#9A2A4A", 1.4, 1405, 1, 0.6))
    # the gelateria counter behind: a row of heaped tubs under the glass
    ty = 316
    out.append(painted(D, rect_pts(-10, ty + 60, 610, 610, 30, 1406, 0.5), ("#8ADCD0", "#3AA8A0", "#1A6A64"), 1406, sdir=(0, 1), sk=0.1, angle=0, n=40, inkw=1.6, hi=0.3))
    for k in range(9):
        out.append(f'<path d="M {k * 70 - 10} {ty + 70} L {k * 70 - 10} 610" stroke="#1A6A64" stroke-width="2" opacity="0.4"/>')
    out.append(painted(D, rect_pts(-10, ty + 46, 610, ty + 66, 30, 1407, 0.4), ("#FFFFFF", "#ECECEE", "#A8A8B0"), 1407, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.6, hi=0.5))
    flav = [
        ("#A8C858", lambda x, y, w: "".join(f'<path d="{blob(x + (k - 2) * 9, y + (k % 2) * 4, 4, 3, k, 0.3, 6)}" fill="#6A9A2A" stroke="#3E5A12" stroke-width="0.8"/>' for k in range(5))),
        ("#F2A0B0", lambda x, y, w: tomato(D, x, y + 2, 10, 1410, pal=("#FF8A8A", "#E02A3A", "#8A0A1A"), calyx=True)),
        ("#FFF0A0", lambda x, y, w: lemon_it(D, x, y + 2, 9, 1411, rot_=-10, leaf=False)),
        ("#7A4A30", lambda x, y, w: "".join(f'<path d="M {x - 16 + k * 8} {y + (k % 2) * 4} l 5 -4" stroke="#2A1408" stroke-width="3" stroke-linecap="round"/>' for k in range(5))),
    ]
    names = ["PISTACCHIO", "FRAGOLA", "LIMONE", "CIOCCOLATO"]
    for i in range(4):
        x = 22 + i * 144 + (60 if i >= 2 else 0) - (0 if i < 2 else 60)
        x = [60, 176, 306, 422][i]
        out.append(gelato_tub(D, x, ty + 10, 118, 40, flav[i], 1420 + i))
        out.append(label(x + 59, ty + 92, names[i], MONO, 13, "#FFFFFF", ls=1, max_w=116))
    out.append(f'<path d="M 0 {ty - 26} L 600 {ty - 26} L 610 {ty + 50} L -10 {ty + 50} Z" fill="#E8FFFC" opacity="0.2"/>')
    out.append(pline([(0, ty - 26), (600, ty - 26)], "#FFFFFF", 3, 1430, 0.8, 1))
    out.append(taper([(40, ty - 20), (70, ty + 40)], 10, 4, "#FFFFFF", 0.3))
    # the hero cone: pistachio, fragola, cioccolato, a wafer and a little spoon
    ccx = 300
    out.append(cast(D, ccx + 30, 540, 90, 10, strength=0.25, seed=1438))
    out.append(summer_cone(D, ccx, 408, 104, 130, 1431))
    out.append(scoop_it(D, ccx - 2, 398, 62, ("#D8EC8A", "#9EC04E", "#5A7A1E"), 1432))
    out.append(specks(1439, (ccx - 50, 350, ccx + 50, 400), ["#5A8A2A", "#3E6A12"], 18, (1.2, 2.4), (0.7, 1)))
    out.append(scoop_it(D, ccx + 8, 340, 54, ("#FFC8D2", "#F28AA2", "#B0405E"), 1433))
    out.append(scoop_it(D, ccx - 4, 290, 46, ("#A8785A", "#6A3E22", "#2E140A"), 1440))
    out.append(painted(D, rot(rect_pts(ccx + 26, 226, ccx + 44, 300, 10, 1441, 0.4), ccx + 35, 263, 18), ("#FFE2A8", "#E0AC5A", "#9A6A24"), 1441, sdir=(1, 0.2), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.5))
    for k in range(4):
        out.append(pline(rot([(ccx + 27, 236 + k * 18), (ccx + 43, 236 + k * 18)], ccx + 35, 263, 18), "#B8823A", 1.2, k, 0.7, 1))
    out.append(painted(D, rot([(ccx - 44, 282), (ccx - 38, 282), (ccx - 36, 236), (ccx - 46, 236)], ccx - 41, 260, -24), ("#FF9AB0", "#F05A80", "#A82450"), 1442, sk=0.2, n=3, inkw=1.2, hi=0.5))
    out.append(painted(D, blob_pts(ccx - 54, 226, 9, 6, 1443, 0.05, 10, -24), ("#FF9AB0", "#F05A80", "#A82450"), 1443, sk=0.2, n=3, inkw=1.2, hi=0.5))
    # lettering
    out.append(letters(D, 300, 172, "gelato", SERIF_IT, 128, "#C8305A", ["#E8507A", "#8A1A3A", "#F27A98"], 1436, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC0D0"))
    out.append(ruled(300, 214, "UN GELATO AL GIORNO", "#1A6A64", font=JOS, size=20, ls=5, line_w=24, gap=12, max_w=320))
    return finish_i(D, out, 1437, "#5A2A3A", 0.8)


def summer_cone(D, cx, top, w, h, seed):
    from summer_gouache import waffle_cone
    return waffle_cone(D, cx, top, w, h, seed)


def scoop_it(D, cx, cy, r, pal, seed):
    from summer_gouache import scoop
    return scoop(D, cx, cy, r, pal, seed, drips=2)


# ================================================================ 17. pizza margherita — out of the wood-fired oven
def fire(D, cx, base, w, h, seed):
    """Wood fire: split logs, layered tongues of flame (red, orange, yellow, white core), sparks."""
    rnd = random.Random(seed)
    out = [D.glow(cx, base - h * 0.3, w * 1.1, "#FF9A2A", 0.75)]
    for k, (dx, a) in enumerate(((-0.3, -10), (0.05, 8), (0.3, -4))):
        lx = cx + dx * w
        out.append(painted(D, rot(rect_pts(lx - w * 0.28, base - 10, lx + w * 0.28, base, 8, seed + k, 0.4), lx, base - 5, a), ("#8A5A3A", "#4A2A16", "#1A0A04"), seed + k, sk=0.2, n=6, inkw=1.2, hi=0.3))
        out.append(f'<circle cx="{lx + w * 0.28 * math.cos(math.radians(a)):.1f}" cy="{base - 5 + w * 0.28 * math.sin(math.radians(a)):.1f}" r="5" fill="#F2A04A" stroke="#4A2A16" stroke-width="1.2"/>')
    for layer, (col, sc) in enumerate((("#C8281A", 1.0), ("#F2641A", 0.82), ("#FFB02A", 0.6), ("#FFF0A0", 0.34))):
        for k in range(5):
            x = cx + (k - 2) * w * 0.18 * sc + rnd.uniform(-4, 4)
            hh = h * sc * rnd.uniform(0.6, 1.0) * (1 - abs(k - 2) * 0.18)
            ww = w * 0.16 * sc + 4
            lean = rnd.uniform(-0.25, 0.25) * hh
            pts = [(x - ww, base - 6), (x - ww * 0.8, base - hh * 0.4), (x + lean - ww * 0.1, base - hh * 0.8), (x + lean, base - hh), (x + lean * 0.6 + ww * 0.3, base - hh * 0.6), (x + ww, base - hh * 0.25), (x + ww * 0.9, base - 6)]
            out.append(f'<path d="{smooth_closed(pts)}" fill="{col}" opacity="0.92"/>')
    for k in range(12):
        out.append(f'<circle cx="{cx + rnd.uniform(-w * 0.6, w * 0.6):.1f}" cy="{base - rnd.uniform(h * 0.6, h * 1.3):.1f}" r="{rnd.uniform(1, 2.2):.1f}" fill="#FFD27A" opacity="0.9"/>')
    return "".join(out)


def pizza_top(D, cx, cy, rx, ry, seed):
    """Neapolitan margherita seen from a little above: puffy leopard-spotted cornicione, tomato, pools of
    melted mozzarella, basil leaves, a thread of olive oil."""
    rnd = random.Random(seed)
    out = []
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 40), ("#FBE2A8", "#E8B66A", "#A8702E"), seed, sdir=(0.3, 1), sk=0.12, angle=0, n=40, inkw=1.8, hi=0.5))
    # leopard spots on the crust
    for k in range(46):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.86, 0.98)
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 5), rnd.uniform(1.4, 3), k, 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#3A1A0A", "#5A2A10", "#2A1006"])}" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    inner = ell_pts(cx, cy + ry * 0.04, rx * 0.8, ry * 0.76, 0, 360, 36)
    out.append(f'<path d="{smooth_closed(jitter(inner, seed, 2))}" fill="#C8281A"/>')
    icid = D.clip(f'<path d="{smooth_closed(jitter(inner, seed, 2))}"/>')
    ii = [strokes(D.nid(), smooth_closed(inner), (cx - rx, cy - ry, cx + rx, cy + ry), ["#E8482A", "#9A1810", "#F26A3A"], seed, n=60, angle=-5, length=(10, 30), width=(2, 4), opacity=(0.3, 0.6), curve=0.5)]
    for k in range(7):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.1, 0.6)
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        mz = blob(x, y, rnd.uniform(20, 30), rnd.uniform(9, 13), seed + k, 0.25, 12)
        ii.append(f'<path d="{mz}" fill="#FFF8E8"/><path d="{blob(x + 3, y + 3, 16, 7, seed + k + 20, 0.25, 10)}" fill="#E8D8B8" opacity="0.6"/>'
                  f'<path d="{blob(x - 6, y - 3, 8, 3, seed + k + 40, 0.2, 8)}" fill="#FFFFFF"/>')
        ii.append(f'<path d="{blob(x + 10, y + 1, 6, 3, seed + k + 60, 0.2, 8)}" fill="#C8902A" opacity="0.5"/>')
    out.append(f'<g {icid}>{"".join(ii)}</g>')
    for k, (dx, dy, a) in enumerate(((-0.3, -0.2, -30), (0.25, -0.3, 40), (0.05, 0.25, 160), (0.42, 0.18, -100), (-0.45, 0.2, 120))):
        out.append(basil_leaf(D, cx + dx * rx, cy + dy * ry, 30, a, seed + 70 + k, inkw=0.9))
    out.append(pline([(cx - rx * 0.5, cy - ry * 0.1), (cx - rx * 0.1, cy + ry * 0.05), (cx + rx * 0.3, cy - ry * 0.15)], "#F2D23A", 2, seed, 0.55, 1))
    return "".join(out)


@design("pizza-margherita")
def pizza_margherita():
    D = Doc2("itpz")
    out = [sky(D, [(0, "#3A2A22"), (1, "#2A1C16")], 1501, 600, ["#4A3A30", "#1A100A", "#5A4636"], 120, angle=-80, sop=(0.06, 0.16))]
    # the oven: a brick dome face with a mosaic band, the mouth glowing
    ox, oy = 300, 396
    face = [(-10, 600), (-10, 300), (60, 236), (180, 212), (300, 206), (420, 212), (540, 236), (610, 300), (610, 600)]
    out.append(f'<path d="{smooth_closed(face)}" fill="#9A4A2A"/>')
    fcid = D.clip(f'<path d="{smooth_closed(face)}"/>')
    rnd = random.Random(1502)
    br = []
    for j in range(16):
        y = 210 + j * 18
        for i in range(-1, 14):
            x = i * 48 + (j % 2) * 24
            c = mix("#B85A32", rnd.choice(["#D8784A", "#8A3A1E", "#C8683A", "#A04A28"]), rnd.uniform(0.2, 0.6))
            br.append(f'<path d="{hg.org_rect(x + 2, y + 2, 44, 14, i * 31 + j, 0.6, 8, 2)}" fill="{c}"/>')
    br.append(f'<rect x="0" y="200" width="600" height="400" fill="{D.rad([(0, "#FF9A3A", 0.45), (0.5, "#FF9A3A", 0.12), (1, "#1A0A04", 0.45)], cx=0.5, cy=0.45, r=0.6)}"/>')
    out.append(f'<g {fcid}>{"".join(br)}</g>')
    out.append(ink(smooth_open(face[1:-1]), "#3A1A0A", 2.2, 1503, 2, 0.7))
    # mosaic band around the mouth (gold and cobalt tesserae)
    for ring, col in ((0, "#E8B840"), (1, "#1F4BA8"), (2, "#E8B840")):
        R = 156 + ring * 12
        for k in range(46):
            a = math.radians(180 + 180 * (k + 0.5) / 46)
            x, y = ox + math.cos(a) * R, oy + math.sin(a) * R * 0.8
            out.append(f'<path d="{hg.org_rect(x - 5, y - 5, 10, 10, k + ring * 50, 0.4, 6, 1.5)}" fill="{mix(col, "#FFFFFF", rnd.uniform(0, 0.25))}" transform="rotate({math.degrees(a) + 90:.0f} {x:.1f} {y:.1f})"/>')
    mouth = [(ox - 150, oy + 80)] + [(ox + 150 * math.cos(math.radians(180 + 180 * k / 20)), oy + 120 * math.sin(math.radians(180 + 180 * k / 20))) for k in range(21)] + [(ox + 150, oy + 80)]
    out.append(f'<path d="{pd(mouth)}" fill="#1A0804"/>')
    mcid = D.clip(f'<path d="{pd(mouth)}"/>')
    out.append(f'<g {mcid}><rect x="140" y="270" width="320" height="220" fill="{D.rad([(0, "#FF8A2A", 0.6), (1, "#3A0A04", 0)], cx=0.35, cy=0.65, r=0.6)}"/>'
               f'{fire(D, ox - 64, oy + 70, 120, 120, 1504)}'
               f'<path d="M 140 {oy + 70} L 460 {oy + 70} L 460 {oy + 90} L 140 {oy + 90} Z" fill="#2A1008"/>'
               f'{specks(1505, (150, oy + 60, 450, oy + 76), ["#FF8A2A", "#FFD27A", "#C8281A"], 50, (1, 2.4), (0.6, 1))}</g>')
    # counter (marble) in front
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#F2EEE6"), (1, "#C8C0B4")])}"/>')
    for k in range(6):
        y = 480 + rnd.uniform(0, 120)
        x = rnd.uniform(-40, 520)
        out.append(pline([(x, y), (x + 60, y + rnd.uniform(-10, 10)), (x + 140, y + rnd.uniform(-14, 14))], "#A8A098", 1.2, k, 0.5, 1))
    out.append(painted(D, rect_pts(-10, 462, 610, 476, 30, 1506, 0.4), ("#FFFFFF", "#ECE6DA", "#B0A898"), 1506, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    out.append(flour_drift(D, 470, 540, 90, 30, 1507, 0.6))
    # the peel with the pizza
    out.append(painted(D, rot(rect_pts(430, 488, 640, 512, 20, 1508, 0.4), 430, 500, 14), ("#F2CC92", "#C8904E", "#7A4E22"), 1508, sdir=(0, 1), sk=0.25, angle=14, n=14, inkw=1.6, hi=0.45))
    out.append(cast(D, 296, 496, 186, 30, strength=0.35, seed=1509))
    out.append(painted(D, ell_pts(290, 472, 186, 66, 0, 360, 40), ("#F2CC92", "#C8904E", "#7A4E22"), 1510, sdir=(0.3, 1), sk=0.15, angle=0, n=40, slen=(30, 90), sw=(0.8, 2), inkw=1.8, hi=0.45))
    out.append(pizza_top(D, 290, 464, 164, 56, 1511))
    out.append(steam(250, 420, 50, 1512, "#FFFFFF", 3, 30, 6, 0.45))
    # basil pot on the counter at left
    out.append(basil_leaf(D, 86, 500, 34, -80, 1513) + basil_leaf(D, 86, 500, 30, -130, 1514) + basil_leaf(D, 86, 500, 30, -30, 1515))
    out.append(painted(D, [(58, 494), (114, 494), (108, 540), (64, 540)], TERRA, 1516, sdir=(1, 0.3), sk=0.2, n=8, inkw=1.6, hi=0.45))
    # lettering
    out.append(letters(D, 300, 152, "pizza", SERIF_IT, 120, "#FFF2D8", ["#FFFFFF", "#F6D8B0", "#FFE8C8"], 1517, max_w=360,
                       shadow="#C8281A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 196, "MARGHERITA", "#F6C860", font=JOS, size=24, ls=10, line_w=36, gap=14, max_w=300))
    return finish_i(D, out, 1518)


# ================================================================ 19. caprese — verde, bianco e rosso on a plate
def tomato_slice(D, cx, cy, r, seed, rot_=0):
    """A round tomato slice seen from above: glossy skin rim, pale flesh walls, jelly-filled seed chambers."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx + 3, cy + 4, r, r * 0.98, seed, 0.03, 18)}" fill="#3A0A04" opacity="0.25"/>']
    out.append(f'<path d="{blob(cx, cy, r, r * 0.98, seed, 0.03, 18)}" fill="#C81E12"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.88, r * 0.86, seed + 1, 0.04, 18)}" fill="#E8483A"/>')
    n = 5
    for k in range(n):
        a = math.radians(rot_ + k * 360 / n + 36)
        lx, ly = cx + math.cos(a) * r * 0.48, cy + math.sin(a) * r * 0.48
        out.append(f'<path d="{blob(lx, ly, r * 0.3, r * 0.2, seed + 3 + k, 0.1, 12, math.degrees(a))}" fill="#F27A5A"/>')
        out.append(f'<path d="{blob(lx, ly, r * 0.25, r * 0.15, seed + 9 + k, 0.1, 12, math.degrees(a))}" fill="#FF9A6A" opacity="0.8"/>')
        for j in range(4):
            sx, sy = lx + rnd.uniform(-r * 0.14, r * 0.14), ly + rnd.uniform(-r * 0.08, r * 0.08)
            out.append(f'<path d="{blob(sx, sy, r * 0.05, r * 0.03, seed + k * 7 + j, 0.1, 6, math.degrees(a))}" fill="#F6E2A0"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.16, r * 0.16, seed + 20, 0.1, 10)}" fill="#F48A6A"/>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.4, r * 0.2, r * 0.07, seed + 21, 0.2, 8, -35)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(ink(blob(cx, cy, r, r * 0.98, seed, 0.03, 18), "#7A0E08", 1.4, seed, 1, 0.6))
    return "".join(out)


def mozzarella_slice(D, cx, cy, r, seed):
    out = [f'<path d="{blob(cx + 3, cy + 4, r, r * 0.96, seed, 0.06, 16)}" fill="#3A2A1A" opacity="0.2"/>']
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.96, seed, 0.06, 16), ("#FFFFFF", "#FBF6EC", "#D8CCB4"), seed, sdir=(0.6, 0.8), sk=0.14, angle=-30, n=8, inkw=1.2, inkop=0.45, hi=0.6))
    out.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.3, r * 0.25, r * 0.12, seed + 1, 0.2, 8, -30)}" fill="#FFFFFF"/>')
    return "".join(out)


@design("caprese")
def caprese():
    D = Doc2("itcp")
    out = [paper(D.nid(), "#F2EEE4", "#7A7A8A", 1701)]
    # linen with a thin blue stripe
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-10, -10, 610, 610), 0, [56, 4, 6, 4], [None, "#7A9AD0", None, "#7A9AD0"], 1702, op=0.35))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-40, 0, 610, 600), ["#FFFFFF", "#D8D4CA"], 1703, n=120, angle=-90, length=(40, 120), width=(1, 3), opacity=(0.1, 0.3)))
    # the plate
    cx, cy, R = 300, 372, 170
    out.append(cast(D, cx + 12, cy + 16, R + 8, R, strength=0.3, seed=1704))
    out.append(painted(D, blob_pts(cx, cy, R, R, 1705, 0.01, 40), ("#FFFFFF", "#F8F6F0", "#C8C4BC"), 1705, sdir=(0.6, 0.8), sk=0.06, angle=-30, n=40, inkw=1.8, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R - 14, R - 14, 0, 360, 48)), "#1F4BA8", 3.4, 1706, 1, 0.9))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R - 22, R - 22, 0, 360, 48)), "#1F4BA8", 1.4, 1707, 1, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx + 4, cy + 4, R - 40, R - 40, 0, 360, 40))}" fill="#EAE6DE" opacity="0.6"/>')
    # ring of overlapping slices, alternating, basil tucked between
    n = 10
    items = []
    for k in range(n):
        a = math.radians(-90 + k * 360 / n)
        x, y = cx + math.cos(a) * 98, cy + math.sin(a) * 98
        items.append((k, x, y, a))
    for k, x, y, a in items:
        if k % 2 == 0:
            out.append(tomato_slice(D, x, y, 41, 1710 + k, rot_=k * 20))
        else:
            out.append(mozzarella_slice(D, x, y, 39, 1710 + k))
        bx, by = cx + math.cos(a + 0.31) * 106, cy + math.sin(a + 0.31) * 106
        out.append(basil_leaf(D, bx - math.cos(a + 0.31) * 20, by - math.sin(a + 0.31) * 20, 40, math.degrees(a + 0.31), 1730 + k, inkw=0.9))
    # centre: a ball of burrata-like mozzarella torn open? keep it simple: a basil crown
    out.append(mozzarella_slice(D, cx, cy, 40, 1750))
    for k in range(5):
        out.append(basil_leaf(D, cx, cy + 4, 34, -90 + k * 72, 1751 + k, inkw=0.9))
    # oil, salt and pepper
    rnd = random.Random(1760)
    out.append(pline([(cx - 120, cy - 40), (cx - 40, cy + 20), (cx + 60, cy - 30), (cx + 130, cy + 30)], "#E8D23A", 3, 1761, 0.55, 1))
    for _ in range(26):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, 150)
        out.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="#2A1A10"/>')
    for _ in range(18):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, 150)
        out.append(f'<rect x="{cx + math.cos(a) * rr:.1f}" y="{cy + math.sin(a) * rr:.1f}" width="2.4" height="2.4" fill="#FFFFFF" transform="rotate(30 {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f})"/>')
    # lettering
    out.append(letters(D, 300, 134, "caprese", SERIF_IT, 116, "#C81E12", ["#E8483A", "#8A0E08", "#F26A4A"], 1770, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB0A0"))
    out.append(ruled(300, 178, "VERDE, BIANCO E ROSSO", "#1E7A3E", font=JOS, size=19, ls=5, line_w=24, gap=12, max_w=340))
    return finish_i(D, out, 1771, "#3A3A4A", 0.8)


# ================================================================ 20. un caffè — at the bar counter, first thing in the morning
def lever_machine(D, x0, x1, base, top, seed):
    """A generic chrome lever espresso machine on the back bar: domed boiler, two group heads with tall levers."""
    w = x1 - x0
    cx = (x0 + x1) / 2
    out = []
    body = rect_pts(x0, top + (base - top) * 0.35, x1, base, 18, seed, 0.4)
    out.append(painted(D, body, ("#FFFFFF", "#C8CCD4", "#6A707C"), seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=20, inkw=1.8, hi=0.6))
    out.append(painted(D, rect_pts(x0 + 4, top + (base - top) * 0.55, x1 - 4, top + (base - top) * 0.68, 18, seed + 1, 0.3), ("#F2604A", "#C8281A", "#6A0A06"), seed + 1, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.5))
    dome_ = [(x0 + w * 0.1, top + (base - top) * 0.36)] + [(cx - w * 0.4 * math.cos(math.radians(t)), top + (base - top) * 0.36 - (base - top) * 0.3 * math.sin(math.radians(t))) for t in range(15, 166, 15)] + [(x1 - w * 0.1, top + (base - top) * 0.36)]
    out.append(painted(D, dome_, ("#FFFFFF", "#C8CCD4", "#6A707C"), seed + 2, sdir=(1, 0.4), sk=0.2, angle=-60, n=12, inkw=1.6, hi=0.6))
    out.append(painted(D, blob_pts(cx, top + (base - top) * 0.03, 8, 7, seed + 3, 0.05, 10), ("#E8C860", "#B8902A", "#6A5010"), seed + 3, sk=0.2, n=3, inkw=1.2, hi=0.6))
    for k, gx in enumerate((x0 + w * 0.28, x1 - w * 0.28)):
        gy = top + (base - top) * 0.74
        out.append(painted(D, rect_pts(gx - 14, gy, gx + 14, gy + 18, 6, seed + 4 + k, 0.2), ("#FFFFFF", "#B8BCC4", "#5A606C"), seed + 4 + k, sk=0.2, n=3, inkw=1.2, hi=0.6))
        out.append(taper([(gx, gy), (gx + 14, gy - (base - top) * 0.5), (gx + 22, gy - (base - top) * 0.8)], 8, 6, "#5A606C"))
        out.append(taper([(gx - 1, gy), (gx + 12, gy - (base - top) * 0.5), (gx + 20, gy - (base - top) * 0.8)], 2.4, 2, "#FFFFFF", 0.7))
        out.append(painted(D, blob_pts(gx + 22, gy - (base - top) * 0.86, 13, 10, seed + 6 + k, 0.05, 10), ("#5A5660", "#1E1C22", "#060608"), seed + 6 + k, sk=0.2, n=3, inkw=1, hi=0.5))
        out.append(taper([(gx - 6, gy + 18), (gx - 4, gy + 26), (gx + 6, gy + 26), (gx + 6, gy + 18)], 3, 3, "#3A3A44"))
    return "".join(out)


def cornetto(D, cx, cy, w, seed, rot_=0):
    """A glazed cornetto: a plump crescent rolled in visible bands, golden glaze, pointed curled ends."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + w * 0.2, w * 0.55, w * 0.1, strength=0.35, seed=seed)]
    outer = [(cx + w * 0.5 * math.cos(math.radians(t)), cy + w * 0.08 - w * 0.34 * math.sin(math.radians(t))) for t in range(0, 181, 10)]
    inner = [(cx + w * 0.3 * math.cos(math.radians(t)), cy + w * 0.14 - w * 0.12 * math.sin(math.radians(t))) for t in range(180, -1, -10)]
    tipL, tipR = (cx - w * 0.56, cy + w * 0.2), (cx + w * 0.56, cy + w * 0.2)
    pts = rot([tipR] + outer + [tipL] + inner, cx, cy, rot_)
    out.append(painted(D, pts, ("#FCD48A", "#E0962E", "#8A4A12"), seed, sdir=(0.3, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.55, hik=0.12))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inn = []
    for k, t in enumerate((-0.62, -0.32, 0, 0.32, 0.62)):
        a0 = math.radians(90 + t * 80)
        p0 = (cx + w * 0.3 * math.cos(a0), cy + w * 0.14 - w * 0.12 * math.sin(a0))
        p1 = (cx + w * 0.5 * math.cos(a0) * 1.04, cy + w * 0.08 - w * 0.34 * math.sin(a0) * 1.04)
        mid = ((p0[0] + p1[0]) / 2 + w * 0.05 * (1 if t >= 0 else -1), (p0[1] + p1[1]) / 2)
        seg = rot([p0, mid, p1], cx, cy, rot_)
        inn.append(ink(smooth_open(seg), "#8A4A12", 2.4, seed + k, 1, 0.6))
        inn.append(ink(smooth_open([(x + 3, y) for x, y in seg]), "#FFE2A8", 1.6, seed + k, 1, 0.6))
    for _ in range(50):
        a = rnd.uniform(0.2, 2.9)
        rr = rnd.uniform(0.32, 0.48)
        x, y = rot([(cx + w * rr * math.cos(a), cy + w * 0.1 - w * 0.3 * (rr / 0.5) * math.sin(a))], cx, cy, rot_)[0]
        inn.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    out.append(f'<g {cid}>{"".join(inn)}</g>')
    return "".join(out)


@design("un-caffe")
def un_caffe():
    D = Doc2("ituc")
    # back bar: warm wood panelling, a mirror strip, the machine and stacked cups
    out = [sky(D, [(0, "#6A3E22"), (1, "#4A2A16")], 1801, 600, ["#8A5A36", "#3A1E0E", "#9A6A44"], 110, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 120, 300, "#FFE2A8", 0.35))
    out.append(painted(D, rect_pts(-10, 214, 610, 228, 30, 1802, 0.4), ("#E8C890", "#B88A4A", "#6A4A20"), 1802, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    out.append(f'<rect x="-10" y="228" width="620" height="160" fill="{D.lin([(0, "#E8DCC8"), (1, "#B8A88A")])}" opacity="0.35"/>')
    for k in range(9):
        out.append(taper([(k * 80 - 30, 380), (k * 80 + 40, 236)], 14, 14, "#FFFFFF", 0.08))
    out.append(lever_machine(D, 330, 560, 384, 214, 1803))
    # stacked cups on the machine's warmer and a shelf of bottles (no labels)
    for k in range(4):
        x = 360 + k * 38 + (14 if k > 1 else 0)
        out.append(painted(D, [(x - 12, 254), (x + 12, 254), (x + 9, 272), (x - 9, 272)], WHITE, 1804 + k, sk=0.2, n=3, inkw=1.1, hi=0.4))
    for k in range(6):
        x = 40 + k * 40
        col = ["#2E6A3A", "#8A2A1A", "#C8902A", "#2E4A7A", "#6A2A4A", "#3E6A2A"][k]
        out.append(painted(D, [(x - 10, 384), (x - 10, 318), (x - 4, 306), (x - 4, 280), (x + 4, 280), (x + 4, 306), (x + 10, 318), (x + 10, 384)], pal3(col, 0.4, 0.4), 1810 + k, sdir=(1, 0.2), sk=0.25, angle=-90, n=4, inkw=1.2, hi=0.55))
    # marble counter with a brass rail
    out.append(f'<path d="M -10 384 L 610 384 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FBF8F2"), (1, "#D8D0C4")])}"/>')
    rnd = random.Random(1820)
    for k in range(8):
        y = 396 + rnd.uniform(0, 200)
        x = rnd.uniform(-40, 520)
        out.append(pline([(x, y), (x + 70, y + rnd.uniform(-10, 10)), (x + 150, y + rnd.uniform(-18, 18)), (x + 240, y + rnd.uniform(-14, 14))], rnd.choice(["#B8B0A8", "#A8A098", "#C8C0B6"]), rnd.uniform(0.8, 1.8), k, 0.5, 1))
    out.append(painted(D, rect_pts(-10, 380, 610, 392, 30, 1821, 0.4), ("#FFFFFF", "#ECE6DA", "#B0A898"), 1821, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    # the espresso: a thick white bar cup on its saucer, crema, a spoon, a sugar sachet
    out.append(cup_saucer(D, 236, 520, 104, 1822, rim=("#E8C860", "#C8902A", "#6A5010")))
    out.append(steam(236, 432, 60, 1823, "#FFFFFF", 2, 26, 6, 0.6))
    out.append(taper([(290, 512), (318, 504), (350, 494)], 4.4, 2.6, "#B8BCC4"))
    out.append(taper([(290, 511), (350, 493)], 1.2, 0.6, "#FFFFFF", 0.8))
    sach = rot(rect_pts(120, 508, 176, 530, 8, 1824, 0.3), 148, 519, -12)
    out.append(painted(D, sach, ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 1824, sk=0.15, n=4, inkw=1.2, hi=0.4))
    out.append(pline(rot([(126, 514), (170, 514)], 148, 519, -12), "#C8281A", 2.4, 1825, 0.8, 1) + pline(rot([(126, 524), (170, 524)], 148, 519, -12), "#1E8A4C", 2.4, 1826, 0.8, 1))
    # glass of water and a cornetto on a little plate
    gx, gb = 362, 470
    out.append(cast(D, gx + 6, gb + 2, 26, 5, strength=0.35, seed=1827))
    gl = [(gx - 22, gb - 92), (gx + 22, gb - 92), (gx + 18, gb), (gx - 18, gb)]
    out.append(f'<path d="{smooth_closed(gl)}" fill="#E8F4F6" opacity="0.6"/>')
    out.append(f'<path d="M {gx - 20} {gb - 64} L {gx + 20} {gb - 64} L {gx + 17} {gb - 2} L {gx - 17} {gb - 2} Z" fill="#BFE2EC" opacity="0.6"/>')
    out.append(taper([(gx - 14, gb - 86), (gx - 12, gb - 10)], 4, 2, "#FFFFFF", 0.8))
    out.append(ink(smooth_closed(gl), "#6A8A92", 1.4, 1828, 2, 0.7))
    out.append(cast(D, 470, 500, 76, 12, strength=0.3, seed=1829))
    out.append(painted(D, ell_pts(468, 488, 74, 20, 0, 360, 28), WHITE, 1830, sdir=(0.3, 1), sk=0.15, n=10, inkw=1.4, hi=0.4))
    out.append(cornetto(D, 468, 470, 120, 1831, rot_=-6))
    # lettering
    out.append(letters(D, 300, 154, "un caffè", SERIF_IT, 110, "#FFF2DA", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 1832, max_w=420,
                       shadow="#2A1408", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 196, "AL BANCO, PER FAVORE", "#F2C860", font=JOS, size=19, ls=5, line_w=24, gap=12, max_w=340))
    return finish_i(D, out, 1833)


# ================================================================ 21. cin cin! — two glasses of red, the straw fiasco, a board
def wine_glass(D, cx, base, h, seed, rot_=0, fill=0.45, wine=("#C83A4A", "#7A0E1E", "#3A0410")):
    w = h * 0.5
    out = [f'<g transform="rotate({rot_} {cx} {base})">']
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 2, w * 0.4, 4.5, 0, 360, 16))}" fill="#F2F4F0" stroke="#6A6A72" stroke-width="1.2"/>')
    out.append(f'<path d="M {cx - 2.2} {base - 3} L {cx - 2.6} {base - h * 0.42} L {cx + 2.6} {base - h * 0.42} L {cx + 2.2} {base - 3} Z" fill="#F2F4F0" stroke="#6A6A72" stroke-width="1.1"/>')
    bowl = [(cx - w * 0.38, base - h), (cx - w * 0.5, base - h * 0.72), (cx - w * 0.36, base - h * 0.48), (cx, base - h * 0.41),
            (cx + w * 0.36, base - h * 0.48), (cx + w * 0.5, base - h * 0.72), (cx + w * 0.38, base - h)]
    d = smooth_closed(bowl)
    out.append(f'<path d="{d}" fill="#F2F6F4" opacity="0.4"/>')
    cid = D.clip(f'<path d="{d}"/>')
    ly = base - h * (0.41 + fill * 0.5)
    out.append(f'<g {cid}><g transform="rotate({-rot_} {cx} {ly})"><rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{wine[1]}"/>'
               f'<rect x="{cx - w}" y="{ly}" width="{2 * w}" height="{h}" fill="{D.lin([(0, wine[0], 0.6), (0.4, wine[0], 0), (1, wine[2], 0.7)], 0, 0, 1, 0)}"/>'
               f'<path d="M {cx - w} {ly} L {cx + w} {ly}" stroke="{wine[0]}" stroke-width="3"/></g>'
               f'{taper([(cx - w * 0.32, base - h * 0.96), (cx - w * 0.42, base - h * 0.72), (cx - w * 0.3, base - h * 0.52)], 6, 1.5, "#FFFFFF", 0.7)}</g>')
    out.append(ink(d, "#5A5A62", 1.6, seed, 2, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w * 0.38, 4, 0, 360, 16))}" fill="none" stroke="#5A5A62" stroke-width="1.2" opacity="0.8"/>')
    out.append("</g>")
    return "".join(out)


def fiasco(D, cx, base, h, seed):
    """The straw-wrapped Chianti-style flask: round green-glass belly in a woven straw jacket, long neck, cork."""
    r = h * 0.33
    by = base - r
    out = [cast(D, cx + 10, base + 2, r * 1.0, 8, strength=0.45, seed=seed)]
    neck = [(cx - r * 0.18, by - r * 0.8), (cx - r * 0.12, by - h * 0.92), (cx + r * 0.12, by - h * 0.92), (cx + r * 0.18, by - r * 0.8)]
    out.append(painted(D, neck, ("#7AB070", "#2E6A3A", "#0E3418"), seed, sdir=(1, 0.2), sk=0.25, angle=-90, n=6, inkw=1.4, hi=0.6, hik=0.15))
    out.append(painted(D, rect_pts(cx - r * 0.14, by - h * 1.0, cx + r * 0.14, by - h * 0.9, 4, seed, 0.2), ("#C8302A", "#9A1A16", "#5A0A08"), seed + 1, sk=0.2, n=3, inkw=1.1, hi=0.5))
    belly = blob_pts(cx, by, r, r, seed + 2, 0.02, 24)
    out.append(painted(D, belly, ("#7AB070", "#2E6A3A", "#0E3418"), seed + 2, sdir=(0.8, 0.4), sk=0.2, n=10, inkw=1.6, hi=0.5))
    # straw jacket on the lower two thirds
    jac = [(cx - r * 1.02, by - r * 0.2)] + [(cx + r * 1.02 * math.cos(math.radians(t)), by + r * 1.02 * math.sin(math.radians(t))) for t in range(180, -1, -15)][::-1][::-1]
    jac = [(cx + r * 1.02 * math.cos(math.radians(t)), by + r * 1.02 * math.sin(math.radians(t))) for t in range(-18, 199, 12)]
    jd = smooth_closed(jac)
    out.append(f'<path d="{jd}" fill="#E8C878"/>')
    jcid = D.clip(f'<path d="{jd}"/>')
    rnd = random.Random(seed)
    wv = []
    for i in range(-14, 15):
        x = cx + i * r * 0.075
        sx_ = cx + i * r * 0.03
        c = rnd.choice(["#F6DC90", "#D8B060", "#E8C878", "#C89A48"])
        wv.append(taper([(x, by - r * 0.3), (x * 1.0 + (x - cx) * 0.25, by + r * 0.4), (sx_, by + r * 1.05)], 3.2, 1.6, c, 0.95))
    for j in range(5):
        y = by + j * r * 0.18
        wv.append(pline([(cx - r * 1.1, y - 2), (cx, y + 3), (cx + r * 1.1, y - 2)], "#B88A40", 1.6, j, 0.6, 1))
    wv.append(shade_over(D, jd, "#5A3A0A", 0.55, 0, 0, 1, 0.6, 0.4))
    out.append(f'<g {jcid}>{"".join(wv)}</g>')
    out.append(ink(jd, "#7A5418", 1.6, seed, 2, 0.75))
    out.append(taper([(cx - r * 1.0, by - r * 0.16), (cx, by - r * 0.26), (cx + r * 1.0, by - r * 0.16)], 7, 7, "#C8302A", 0.95))
    out.append(taper([(cx - r * 0.55, by - r * 0.62), (cx - r * 0.66, by - r * 0.4)], 5, 2, "#FFFFFF", 0.7))
    return "".join(out)


@design("cin-cin")
def cin_cin():
    D = Doc2("itcc")
    out = [sky(D, [(0, "#6A1E26"), (1, "#3A0E14")], 1901, 600, ["#8A2A34", "#2A060C", "#9A3A40"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 280, 260, "#FFC88A", 0.45))
    rnd = random.Random(1902)
    for k in range(14):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(220, 420):.1f}" r="{rnd.uniform(8, 20):.1f}" fill="#FFD27A" opacity="{rnd.uniform(0.06, 0.15):.2f}"/>')
    # rustic table
    out.append(wood_planks(D, 430, 600, 1903, NOCE, 3))
    out.append(f'<rect y="426" width="600" height="8" fill="#1A0804" opacity="0.5"/>')
    # cheese board: pecorino wedge, salami slices, grapes
    out.append(cast(D, 400, 520, 150, 20, strength=0.45, seed=1904))
    out.append(painted(D, rect_pts(250, 470, 560, 520, 24, 1905, 0.5), ("#F2CC92", "#C8904E", "#7A4E22"), 1905, sdir=(0, 1), sk=0.15, angle=0, n=20, inkw=1.6, hi=0.45))
    out.append(painted(D, [(270, 476), (360, 448), (380, 484), (300, 498)], ("#FFF6D8", "#F2E2B0", "#B8A070"), 1906, sdir=(0.5, 1), sk=0.2, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, [(270, 476), (300, 498), (300, 504), (270, 484)], ("#E8B860", "#B8862E", "#6A4A14"), 1907, sk=0.2, n=3, inkw=1.2, hi=0.3))
    for k in range(5):
        x, y = 410 + k * 22, 486 - (k % 2) * 6
        out.append(painted(D, blob_pts(x, y, 15, 13, 1908 + k, 0.04, 14), ("#E8706A", "#B8303A", "#6A0E18"), 1908 + k, sk=0.15, n=4, inkw=1.2, hi=0.4))
        for j in range(6):
            out.append(f'<circle cx="{x + rnd.uniform(-9, 9):.1f}" cy="{y + rnd.uniform(-8, 8):.1f}" r="{rnd.uniform(1.4, 2.6):.1f}" fill="#FFE8E0" opacity="0.9"/>')
    out.append(grape_bunch(D, 520, 446, 6, 1913))
    # the fiasco
    out.append(fiasco(D, 140, 512, 250, 1914))
    # two glasses clinking, a little splash and sparkles at the touch
    out.append(wine_glass(D, 262, 430, 176, 1915, rot_=12))
    out.append(wine_glass(D, 382, 430, 176, 1916, rot_=-12))
    sx, sy = 322, 272
    for k in range(4):
        a = math.radians(-140 + k * 33)
        out.append(f'<path d="{smooth_closed(drop_pts(sx + math.cos(a) * 30, sy + math.sin(a) * 24, 3.6, a))}" fill="#B81E2E"/>')
    for x, y, r in ((sx, sy - 40, 12), (sx - 40, sy - 24, 7), (sx + 42, sy - 26, 8)):
        out.append(sparkle(x, y, r, "#FFF2C8", 0.95))
    # lettering
    out.append(letters(D, 300, 150, "cin cin!", SERIF_IT, 128, "#FFE8C8", ["#FFFFFF", "#F6D2A8", "#FFE2B8"], 1917, max_w=400,
                       shadow="#1A0408", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 194, "ALLA SALUTE!", "#F2B860", font=JOS, size=21, ls=8, line_w=32, gap=14, max_w=300))
    return finish_i(D, out, 1918, "#1A0408", 0.7)


def drop_pts(cx, cy, r, ang):
    """A droplet flying outward along ang (radians): round tail at (cx, cy), point leading."""
    pts = [(cx + math.cos(ang) * r * 2.4, cy + math.sin(ang) * r * 2.4)]
    for k in range(9):
        a = ang + math.pi / 2 + math.pi * k / 8
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


# ================================================================ 22. tiramisù — a slice, the cocoa, the espresso
@design("tiramisu")
def tiramisu():
    D = Doc2("ittm")
    out = [paper(D.nid(), "#F2E2CC", FLECK, 2001)]
    out.append(blooms(2002, ["#C8A07A", "#FFFFFF", "#D8B890"], 6, (0, 0, 600, 600), (90, 170), (0.08, 0.14)))
    # linen napkin and a small sieve
    out.append(cloth(D, [(380, 380), (590, 360), (600, 560), (400, 590)], "#C8A07A", 2003, base="#FBF4E6", cell=10, rot_=-6))
    # the plate
    cx, cy = 280, 450
    out.append(plate_34(D, cx, cy + 6, 206, 78, 2004, glaze=("#FFFFFF", "#F6F2EA", "#C0B8AC"), rim="#8A5A3A"))
    # a square slice in 3/4 view: top (cocoa), front face (layers), side face
    x0, x1, yt, yb = 168, 368, 336, 462
    dx, dy = 52, -30
    front = [(x0, yt), (x1, yt), (x1, yb), (x0, yb)]
    side = [(x1, yt), (x1 + dx, yt + dy), (x1 + dx, yb + dy), (x1, yb)]
    top = [(x0, yt), (x0 + dx, yt + dy), (x1 + dx, yt + dy), (x1, yt)]
    out.append(cast(D, cx + 40, yb + 6, 130, 16, strength=0.45, seed=2005))
    # layers on the front: cream / soaked biscuit / cream / soaked biscuit / cream
    layers = [(0, 0.14, "#3E2010"), (0.14, 0.34, "#FBF2DC"), (0.34, 0.5, "#8A5426"), (0.5, 0.72, "#FBF2DC"), (0.72, 0.88, "#7A4620"), (0.88, 1, "#F2E2C2")]
    for a, b, c in layers:
        ya, yb2 = yt + (yb - yt) * a, yt + (yb - yt) * b
        out.append(f'<path d="{hg.org_poly([(x0, ya), (x1, ya), (x1, yb2), (x0, yb2)], int(ya), 0.8, 12, 0.5)}" fill="{c}"/>')
        if c in ("#8A5426", "#7A4620"):
            rr = random.Random(int(ya))
            for k in range(18):
                px = rr.uniform(x0 + 4, x1 - 4)
                out.append(f'<circle cx="{px:.1f}" cy="{rr.uniform(ya + 2, yb2 - 2):.1f}" r="{rr.uniform(1, 2.2):.1f}" fill="{rr.choice(["#5A3014", "#A86A3A"])}" opacity="0.8"/>')
            for k in range(4):
                bx = x0 + 6 + k * (x1 - x0) / 4
                out.append(pline([(bx, ya + 2), (bx + 1, yb2 - 2)], "#5A3014", 1.2, k, 0.5, 1))
        else:
            out.append(strokes(D.nid(), pd([(x0, ya), (x1, ya), (x1, yb2), (x0, yb2)]), (x0, ya, x1, yb2), ["#FFFFFF", "#E8D8B8"], int(ya), n=12, angle=0, length=(16, 40), width=(1, 2.4), opacity=(0.3, 0.6)))
    out.append(f'<path d="{pd(side)}" fill="#C8A47A"/>')
    for a, b, c in layers:
        out.append(f'<path d="{pd([(x1, yt + (yb - yt) * a), (x1 + dx, yt + (yb - yt) * a + dy), (x1 + dx, yt + (yb - yt) * b + dy), (x1, yt + (yb - yt) * b)])}" fill="{dk(c, 0.25)}"/>')
    out.append(f'<path d="{pd(top)}" fill="#5A3018"/>')
    tcid = D.clip(f'<path d="{pd(top)}"/>')
    rnd = random.Random(2006)
    cocoa = "".join(f'<circle cx="{rnd.uniform(x0, x1 + dx):.1f}" cy="{rnd.uniform(yt + dy, yt):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="{rnd.choice(["#7A4A2A", "#3A1A0A", "#8A5A36"])}"/>' for _ in range(260))
    out.append(f'<g {tcid}>{cocoa}</g>')
    out.append(ink(pd(front), INK, 1.6, 2007, 2, 0.7) + ink(pd(side), INK, 1.4, 2008, 1, 0.6) + ink(pd(top), INK, 1.4, 2009, 1, 0.6))
    out.append(specks(2010, (150, 380, 420, 500), ["#5A3018", "#7A4A2A"], 70, (0.6, 1.6), (0.5, 0.9)))
    # a fork, coffee beans, the espresso cup
    out.append(fork(D, 470, 500, 360, 486, 13, 2011, metal=ALU))
    for k, (x, y, a) in enumerate(((110, 520, 20), (126, 532, -30), (96, 540, 60), (470, 330, 10), (486, 342, -40))):
        bean = blob(x, y, 7, 5, 2012 + k, 0.05, 10, a)
        out.append(f'<path d="{bean}" fill="#4A2410"/><path d="M {x - 5 * math.cos(math.radians(a)):.1f} {y - 5 * math.sin(math.radians(a)):.1f} Q {x:.1f} {y + 1.5:.1f} {x + 5 * math.cos(math.radians(a)):.1f} {y + 5 * math.sin(math.radians(a)):.1f}" stroke="#1A0804" stroke-width="1.4" fill="none"/>'
                   f'<path d="{blob(x - 2, y - 2, 2.4, 1.2, k, 0.2, 6, a)}" fill="#FFFFFF" opacity="0.5"/>')
    out.append(cup_saucer(D, 482, 300, 70, 2017, rim=("#C8A07A", "#8A5A3A", "#4A2A14")))
    out.append(steam(482, 240, 40, 2018, "#FFFFFF", 2, 18, 5, 0.65))
    # lettering
    out.append(letters(D, 270, 142, "tiramisù", SERIF_IT, 118, "#5A2A12", ["#7A3E1E", "#3A1608", "#8A5030"], 2019, max_w=380,
                       shadow="#FFF2DC", soff=(0.02, 0.035), angle=-40, hi="#C8906A"))
    out.append(ruled(270, 188, "UN CUCCHIAIO DI FELICITÀ", "#8A5A2A", font=JOS, size=18, ls=4, line_w=20, gap=10, max_w=330))
    return finish_i(D, out, 2020)


# ================================================================ 23. sicilia — prickly pears, blood oranges, a majolica sun
def cactus_pad(D, x, y, w, h, ang, seed, pal=("#A8C870", "#6A9A48", "#2E5A22")):
    """A prickly-pear pad (cladode): flat oval, dotted areoles with tiny spines, lit edge."""
    rnd = random.Random(seed)
    pts = rot(blob_pts(x, y, w / 2, h / 2, seed, 0.05, 20), x, y, ang)
    out = [painted(D, pts, pal, seed, sdir=(0.7, 0.5), sk=0.18, angle=ang - 90, n=int(w * h / 300) + 6, inkw=1.6, hi=0.4)]
    for j in range(5):
        for i in range(4):
            u = -0.32 + i * 0.21 + (j % 2) * 0.1
            v = -0.36 + j * 0.18
            if u * u / 0.16 + v * v / 0.18 > 1:
                continue
            px, py = rot([(x + u * w, y + v * h)], x, y, ang)[0]
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#5A7A3A"/><circle cx="{px:.1f}" cy="{py:.1f}" r="1.1" fill="#F2ECC0"/>'
                       f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(-6, -3):.1f}" stroke="#F6F0D8" stroke-width="0.9"/>')
    return "".join(out)


def prickly_fruit(D, x, y, r, ang, seed, pal=("#FFB060", "#F0601E", "#9A2A0A")):
    pts = rot([(x - r * 0.7, y + r * 0.4), (x - r * 0.8, y - r * 0.4), (x - r * 0.4, y - r * 1.1), (x + r * 0.4, y - r * 1.1), (x + r * 0.8, y - r * 0.4), (x + r * 0.7, y + r * 0.4), (x, y + r * 0.7)], x, y, ang)
    out = [painted(D, pts, pal, seed, sdir=(0.6, 0.7), sk=0.2, angle=ang - 90, n=6, inkw=1.3, hi=0.45)]
    rnd = random.Random(seed)
    for _ in range(9):
        px, py = rot([(x + rnd.uniform(-0.5, 0.5) * r, y + rnd.uniform(-0.8, 0.3) * r)], x, y, ang)[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.2" fill="#FFE8A0"/>')
    tx, ty = rot([(x, y - r * 1.1)], x, y, ang)[0]
    out.append(f'<path d="{blob(tx, ty, r * 0.35, r * 0.12, seed + 1, 0.1, 8, ang)}" fill="{pal[2]}"/>')
    return "".join(out)


def blood_orange_half(D, cx, cy, r, seed):
    """A blood orange cut in half: thick rind, white pith, ruby segments with juice sacs, a pale centre."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + r * 0.3, r * 1.05, r * 0.4, strength=0.35, seed=seed)]
    out.append(f'<path d="{blob(cx, cy, r, r * 0.62, seed, 0.03, 20)}" fill="#E8701A"/>')
    out.append(f'<path d="{blob(cx, cy - 2, r * 0.93, r * 0.56, seed + 1, 0.03, 20)}" fill="#FFF0D8"/>')
    out.append(f'<path d="{blob(cx, cy - 2, r * 0.84, r * 0.5, seed + 2, 0.03, 20)}" fill="#8A0E1E"/>')
    for k in range(10):
        a0 = math.radians(k * 36 + 4)
        a1 = math.radians(k * 36 + 32)
        seg = [(cx, cy - 2)] + [(cx + r * 0.8 * math.cos(a0 + (a1 - a0) * t / 5), cy - 2 + r * 0.47 * math.sin(a0 + (a1 - a0) * t / 5)) for t in range(6)]
        c = rnd.choice(["#C8182E", "#A8102A", "#D83A3A", "#B0202E"])
        out.append(f'<path d="{smooth_closed(seg)}" fill="{c}"/>')
        mx, my = cx + r * 0.5 * math.cos((a0 + a1) / 2), cy - 2 + r * 0.3 * math.sin((a0 + a1) / 2)
        out.append(f'<path d="{blob(mx, my, r * 0.12, r * 0.04, seed + k, 0.2, 6, math.degrees((a0 + a1) / 2))}" fill="#FF8A7A" opacity="0.6"/>')
    out.append(f'<path d="{blob(cx, cy - 2, r * 0.12, r * 0.07, seed + 30, 0.1, 8)}" fill="#FFE8D8"/>')
    out.append(ink(blob(cx, cy, r, r * 0.62, seed, 0.03, 20), "#9A3A0A", 1.6, seed, 1, 0.7))
    return "".join(out)


def ceramic_sun(D, cx, cy, R, seed):
    """A majolica sun medallion (no face): wavy and straight rays in yellow and orange, cobalt outlines, a
    spiral and dotted rings in the disc, a glossy glaze highlight."""
    out = []
    for k in range(16):
        a = math.radians(k * 22.5)
        L = R * (1.0 if k % 2 == 0 else 0.82)
        w = 0.14 if k % 2 == 0 else 0.1
        p0 = (cx + math.cos(a - w) * R * 0.5, cy + math.sin(a - w) * R * 0.5)
        p1 = (cx + math.cos(a + w) * R * 0.5, cy + math.sin(a + w) * R * 0.5)
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        c = "#F6C21C" if k % 2 == 0 else "#F2861A"
        if k % 2 == 0:
            mid = (cx + math.cos(a + 0.08) * L * 0.75, cy + math.sin(a + 0.08) * L * 0.75)
            pts = [p0, mid, tip, (cx + math.cos(a - 0.04) * L * 0.75, cy + math.sin(a - 0.04) * L * 0.75), p1]
        else:
            pts = [p0, tip, p1]
        out.append(f'<path d="{smooth_closed(pts) if k % 2 == 0 else pd(pts)}" fill="{c}"/>')
        out.append(ink(smooth_closed(pts) if k % 2 == 0 else pd(pts), COBALTO[1], 2, seed + k, 1, 0.85))
    out.append(painted(D, blob_pts(cx, cy, R * 0.55, R * 0.55, seed, 0.02, 24), ("#FFF2A0", "#F6C21C", "#C88A0A"), seed, sk=0.15, n=20, inkw=2.4, inkc=COBALTO[1], hi=0.5))
    for k in range(24):
        a = math.radians(k * 15)
        out.append(f'<circle cx="{cx + math.cos(a) * R * 0.46:.1f}" cy="{cy + math.sin(a) * R * 0.46:.1f}" r="{R * 0.025:.1f}" fill="{COBALTO[1]}"/>')
    sp = [(cx + R * 0.36 * (1 - t / 60) * math.cos(t * 0.25), cy + R * 0.36 * (1 - t / 60) * math.sin(t * 0.25)) for t in range(60)]
    out.append(ink(smooth_open(sp), "#F2861A", 4, seed, 1, 0.9))
    out.append(f'<path d="{blob(cx - R * 0.2, cy - R * 0.25, R * 0.18, R * 0.07, seed + 3, 0.2, 10, -35)}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


@design("sicilia")
def sicilia():
    D = Doc2("itsc")
    out = [sky(D, [(0, "#2A5AB0"), (1, "#163E86")], 2101, 600, ["#3A6AC0", "#0E2A6A", "#4A7ACC"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 360, 330, 280, "#FFE29A", 0.35))
    out.append(ceramic_sun(D, 440, 270, 96, 2102))
    # terracotta ledge
    out.append(painted(D, rect_pts(-10, 476, 610, 610, 30, 2103, 0.5), TERRA, 2103, sdir=(0, 1), sk=0.08, angle=0, n=50, inkw=0, hi=0.2))
    out.append(painted(D, rect_pts(-10, 464, 610, 484, 30, 2104, 0.4), ("#F2B48A", "#D2784A", "#8A3A18"), 2104, sdir=(0, 1), sk=0.3, angle=0, n=20, inkw=1.6, hi=0.5))
    for k in range(11):
        out.append(f'<path d="M {k * 60 - 10} 484 L {k * 60 - 12} 610" stroke="#8A3A18" stroke-width="1.6" opacity="0.4"/>')
    # prickly pear rising on the left
    pads = [(150, 420, 118, 150, -6), (96, 318, 88, 114, -28), (206, 314, 92, 116, 22), (140, 242, 70, 88, -12), (256, 244, 62, 80, 34)]
    for k, (x, y, w, h, a) in enumerate(pads):
        out.append(cactus_pad(D, x, y, w, h, a, 2105 + k))
    for k, (x, y, r, a, pal) in enumerate(((122, 204, 14, -20, ("#FFB060", "#F0601E", "#9A2A0A")), (148, 198, 13, 4, ("#FF8A6A", "#D8282A", "#7A0A0A")),
                                           (172, 206, 14, 22, ("#FFD86A", "#F2A21E", "#9A5A0A")), (252, 206, 13, 10, ("#FF8A6A", "#D8282A", "#7A0A0A")),
                                           (274, 216, 12, 40, ("#FFB060", "#F0601E", "#9A2A0A")), (68, 268, 13, -40, ("#FFD86A", "#F2A21E", "#9A5A0A")), (236, 260, 13, 30, ("#FFB060", "#F0601E", "#9A2A0A")))):
        out.append(prickly_fruit(D, x, y, r, a, 2110 + k, pal))
    # basket of blood oranges and lemons on the ledge, one orange cut
    bx = 430
    out.append(cast(D, bx + 10, 486, 130, 12, strength=0.4, seed=2120))
    for k, (x, y, r) in enumerate(((bx - 70, 432, 30), (bx - 18, 422, 32), (bx + 38, 428, 30), (bx + 84, 440, 27), (bx - 44, 398, 28), (bx + 12, 392, 29), (bx + 62, 404, 26))):
        if k in (2, 5):
            out.append(lemon_it(D, x, y, r * 0.8, 2121 + k, rot_=k * 15 - 30))
        else:
            out.append(tomato(D, x, y, r, 2121 + k, pal=("#FFA868", "#E8601A", "#8A2A0A"), calyx=False, squash=0.95))
            out.append(f'<circle cx="{x + r * 0.1:.1f}" cy="{y - r * 0.5:.1f}" r="{r * 0.08:.1f}" fill="#6A5A1A"/>')
    out.append(wicker_front(D, bx, 438, 150, 44, 2130))
    out.append(blood_orange_half(D, 292, 482, 42, 2131))
    out.append(citrus_leaf(D, 330, 462, 40, -20, 2132))
    # lettering
    out.append(letters(D, 300, 150, "Sicilia", SERIF_IT, 116, "#FFE27A", ["#FFF2B0", "#F2B81C", "#FFE89A"], 2133, max_w=380,
                       shadow="#0E2462", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 536, "TERRA DEL SOLE", "#FFF2D8", font=JOS, size=22, ls=8, line_w=30, gap=14, max_w=300))
    return finish_i(D, out, 2134)


def wicker_front(D, cx, top, w, h, seed):
    """Front of a low wicker basket (rows of woven strands), rim on top."""
    pts = [(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.42, top + h), (cx - w * 0.42, top + h)]
    d = smooth_closed(poly_pts(pts, 14, seed, 0.5))
    out = [f'<path d="{d}" fill="#B07A3E"/>']
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    wv = []
    for j in range(int(h / 9) + 1):
        y = top + 5 + j * 9
        for i in range(-1, int(w / 18) + 2):
            x = cx - w / 2 + i * 18 + (j % 2) * 9
            wv.append(f'<path d="{blob(x + 9, y, 10, 4.2, i * 13 + j, 0.12, 10)}" fill="{rnd.choice(["#E2B06A", "#D49E58", "#ECC07A"])}"/>')
    wv.append(shade_over(D, d, "#3A1A06", 0.5, 0, 0, 1, 0.6, 0.3))
    out.append(f'<g {cid}>{"".join(wv)}</g>')
    out.append(ink(d, INK, 1.8, seed, 2, 0.7))
    out.append(taper([(cx - w / 2 - 4, top), (cx, top + 3), (cx + w / 2 + 4, top)], 9, 9, "#9A6830"))
    out.append(taper([(cx - w / 2 - 2, top - 2), (cx, top + 1), (cx + w / 2 + 2, top - 2)], 3, 3, "#E8BA74", 0.8))
    return "".join(out)


# ================================================================ 24. erbe aromatiche — a field-guide plate of the kitchen herbs
def rosemary(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    out = [taper([(x, y), (x + ux * L, y + uy * L)], 4, 1.6, "#7A6A4A")]
    for k in range(int(L / 4)):
        t = 0.05 + 0.95 * k / (L / 4)
        px, py = x + ux * L * t, y + uy * L * t
        for sg in (-1, 1):
            b = a + sg * rnd.uniform(0.6, 1.0) - 0.2 * sg * t
            l = 18 * (1 - 0.5 * t) * rnd.uniform(0.8, 1.1)
            out.append(taper([(px, py), (px + math.cos(b) * l, py + math.sin(b) * l)], 3.4, 1, rnd.choice(["#4A6A4A", "#5E7E58", "#3A563C"])))
            out.append(taper([(px, py), (px + math.cos(b) * l * 0.8, py + math.sin(b) * l * 0.8)], 1, 0.4, "#A8C0A0", 0.7))
    for k in range(3):
        t = 0.3 + k * 0.2
        out.append(f'<path d="{blob(x + ux * L * t + 8, y + uy * L * t, 4, 3, seed + k, 0.2, 8)}" fill="#8AA8E0"/>')
    return "".join(out)


def sage_sprig(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    out = [taper([(x, y), (x + ux * L, y + uy * L)], 4, 2, "#7A8A62")]
    for k, t in enumerate((0.25, 0.5, 0.72, 0.95)):
        px, py = x + ux * L * t, y + uy * L * t
        for sg in ((-1, 1) if t < 0.9 else (0,)):
            b = ang + sg * rnd.uniform(45, 60)
            s = L * (0.42 - 0.12 * t)
            out.append(leaf_simple(D, px, py, s, s * 0.32, b, ("#C8D0B4", "#8A9A7A", "#4A5A40"), seed + k * 3 + sg, vein=True, inkw=1.1))
    rr = random.Random(seed)
    return "".join(out)


def oregano(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    out = [taper([(x, y), (x + ux * L, y + uy * L)], 3, 1.4, "#7A4A3A")]
    for k in range(7):
        t = 0.12 + k * 0.13
        px, py = x + ux * L * t, y + uy * L * t
        for sg in (-1, 1):
            b = a + sg * 1.1
            out.append(f'<path d="{blob(px + math.cos(b) * 8, py + math.sin(b) * 8, 7, 5, seed + k * 2 + sg, 0.08, 10, math.degrees(b))}" fill="{rnd.choice(["#6A9A4A", "#5A8A3E", "#7AA858"])}" stroke="#2E5A22" stroke-width="0.9"/>')
    tx, ty = x + ux * L, y + uy * L
    for k in range(9):
        out.append(f'<circle cx="{tx + rnd.uniform(-9, 9):.1f}" cy="{ty + rnd.uniform(-9, 5):.1f}" r="{rnd.uniform(2, 3):.1f}" fill="{rnd.choice(["#E8A0C8", "#D07AA8", "#F2C0D8"])}"/>')
    return "".join(out)


def parsley(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    out = []
    for k, da in enumerate((-22, 0, 22)):
        a = math.radians(ang + da)
        ux, uy = math.cos(a), math.sin(a)
        l = L * (1 - abs(da) / 80)
        tx, ty = x + ux * l, y + uy * l
        out.append(taper([(x, y), (tx, ty)], 3, 1.4, "#6A9A3A"))
        for j, db in enumerate((-40, 0, 40)):
            b = math.radians(ang + da + db)
            lx, ly = tx + math.cos(b) * 10, ty + math.sin(b) * 10
            pts = []
            for i in range(14):
                t = 2 * math.pi * i / 14
                k2 = 1 + 0.22 * math.cos(3 * t)
                pts.append((lx + 12 * k2 * math.cos(t), ly + 9 * k2 * math.sin(t)))
            pts = rot(pts, lx, ly, math.degrees(b))
            out.append(f'<path d="{smooth_closed(pts)}" fill="{rnd.choice(["#3E8A3A", "#4A9A40", "#2E7A2E"])}"/>')
            out.append(ink(smooth_closed(pts), "#1A4A1A", 0.9, seed + k + j, 1, 0.6))
            out.append(taper([(tx, ty), (lx + math.cos(b) * 8, ly + math.sin(b) * 8)], 1, 0.4, "#A8D880", 0.8))
    return "".join(out)


def bay_sprig(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    out = [taper([(x, y), (x + ux * L, y + uy * L)], 4, 2, "#6A5A3A")]
    for k, t in enumerate((0.2, 0.42, 0.62, 0.82, 1.0)):
        px, py = x + ux * L * t, y + uy * L * t
        sg = 1 if k % 2 else -1
        if t == 1.0:
            sg = 0
        b = ang + sg * rnd.uniform(30, 45)
        out.append(leaf_simple(D, px, py, L * 0.5, L * 0.12, b, ("#6AA05A", "#2E6A34", "#123E1A"), seed + k, vein=True, inkw=1.1))
        out.append(taper([(px + math.cos(math.radians(b)) * L * 0.1, py + math.sin(math.radians(b)) * L * 0.1), (px + math.cos(math.radians(b)) * L * 0.3, py + math.sin(math.radians(b)) * L * 0.3)], 3, 1, "#FFFFFF", 0.35))
    return "".join(out)


@design("erbe-aromatiche")
def erbe_aromatiche():
    D = Doc2("itea")
    out = [paper(D.nid(), "#F3ECDA", FLECK, 2201)]
    out.append(blooms(2202, ["#C8D8B0", "#E8D8A8", "#B8D0C0"], 6, (100, 120, 500, 500), (110, 180), (0.1, 0.18)))
    out.append(f'<rect x="50" y="50" width="500" height="500" fill="none" stroke="#3E5A2E" stroke-width="2.2"/>')
    out.append(f'<rect x="58" y="58" width="484" height="484" fill="none" stroke="#3E5A2E" stroke-width="1.2" opacity="0.7"/>')
    for x, y in ((50, 50), (550, 50), (50, 550), (550, 550)):
        out.append(f'<path d="{blob(x, y, 7, 7, x + y, 0.1, 8)}" fill="#C8603A"/>')
    out.append(ruled(300, 92, "L'ORTO DI CASA · TAV. III", "#3E5A2E", font=MONO, size=16, ls=4, line_w=24, gap=10, max_w=360))
    out.append(letters(D, 300, 156, "Erbe aromatiche", SERIF_IT, 64, "#2E4A22", ["#3E6A2E", "#1A2E12"], 2203, max_w=420, angle=-40, wob=0.6))
    # six cells
    cells = [("BASILICO", basil_sprig, 0), ("ROSMARINO", rosemary, 1), ("SALVIA", sage_sprig, 2), ("ORIGANO", oregano, 3), ("PREZZEMOLO", parsley, 4), ("ALLORO", bay_sprig, 5)]
    for k, (name, fn, _) in enumerate(cells):
        i, j = k % 3, k // 3
        cx, cyb = 140 + i * 160, 326 + j * 180
        if fn is basil_sprig:
            out.append(basil_sprig(D, cx + 4, cyb - 6, -90, 96, 2210 + k))
        elif fn is parsley:
            out.append(parsley(D, cx, cyb - 6, 92, -90, 2210 + k))
        else:
            out.append(fn(D, cx + (8 if fn is rosemary else 0), cyb - 6, {rosemary: 112, sage_sprig: 104, oregano: 104, bay_sprig: 100}[fn], -90 + (8 if fn is rosemary else 0), 2210 + k))
        out.append(label(cx, cyb + 22, name, JOS, 16, "#7A3218", ls=2, max_w=140))
    out.append(pline([(80, 362), (300, 363), (520, 362)], "#3E5A2E", 1, 2230, 0.35, 1))
    return finish_i(D, out, 2231)


# ================================================================ 25. ti voglio bene — a postcard home
@design("ti-voglio-bene")
def ti_voglio_bene():
    D = Doc2("ittv")
    out = [wood_planks(D, 0, 600, 2301, ("#C89A6A", "#9A6A40", "#5A3A1E"), 5)]
    # the postcard, slightly turned, bleeding past the edges
    card = rot(rect_pts(28, 34, 572, 566, 30, 2302, 0.6), 300, 300, -2.5)
    out.append(f'<path d="{smooth_closed(shift(card, 8, 10))}" fill="#2A1408" opacity="0.35"/>')
    out.append(painted(D, card, ("#FFFDF4", "#F6EEDC", "#C8B898"), 2303, sdir=(0.5, 1), sk=0.04, angle=-20, n=60, inkw=1.4, hi=0.3))
    out.append('<g transform="rotate(-2.5 300 300)">')
    out.append(ruled(300, 88, "CARTOLINA POSTALE", "#8A3A1E", font=CINZEL, size=24, ls=6, line_w=34, gap=14, max_w=380))
    # vignette on the left: Positano-like coast in a deckled frame
    vx0, vy0, vx1, vy1 = 64, 122, 300, 352
    fr = rect_pts(vx0, vy0, vx1, vy1, 6, 2304, 1.2)
    out.append(f'<path d="{smooth_closed(fr)}" fill="#FFFFFF"/>')
    vcid = D.clip(f'<rect x="{vx0 + 8}" y="{vy0 + 8}" width="{vx1 - vx0 - 16}" height="{vy1 - vy0 - 16}"/>')
    v = [sky(D, [(0, "#8AC8EE"), (1, "#FFF0D8")], 2305, 360, ["#FFFFFF", "#B8E0F2"], 30, angle=-3, sop=(0.08, 0.2), y0=120)]
    v.append(sea(D, 268, 360, [(0, "#3A9ACB"), (1, "#1E5A9A")], 2306, ["#6AC0E8", "#0E3E70", "#FFFFFF"], 30, ticks=["#FFFFFF"]))
    v.append(hill(D, ridge([(60, 200), (130, 160), (200, 190), (300, 230)], 2307, 8, 3) + [(310, 272)], 300, ("#9AB070", "#6A8A4A", "#3E5A2A"), 2308, inkw=0, n=20))
    v.append(stacked_town(D, 80, 250, 270, 186, 2309, ["#F6D8A0", "#F2B8A0", "#FFFFFF", "#F6E8C8", "#E8A8A0", "#F8E0A8"], haze=0.05, n=40))
    v.append(dome(D, 150, 236, 26, 2310, col="#E8E0D0", lit="#FFFFFF"))
    v.append(f'<path d="{blob(150, 214, 12, 10, 2311, 0.05, 10)}" fill="#3EA89A"/>')
    for x, y in ((236, 300), (180, 320)):
        v.append(painted(D, [(x - 12, y), (x + 12, y), (x + 9, y + 5), (x - 9, y + 5)], WHITE, int(x), sk=0.2, n=2, inkw=0.9, hi=0.5))
    out.append(f'<g {vcid}>{"".join(v)}</g>')
    out.append(f'<rect x="{vx0 + 8}" y="{vy0 + 8}" width="{vx1 - vx0 - 16}" height="{vy1 - vy0 - 16}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.5"/>')
    out.append(label(182, 378, "Saluti dall'Italia", SERIF_IT, 22, "#8A3A1E", max_w=230))
    # divider line and the address side
    out.append(pline([(322, 124), (323, 400)], "#B8A890", 1.6, 2312, 0.8, 1))
    for y in (300, 336, 372):
        out.append(pline([(344, y), (450, y + 1), (536, y)], "#B8A890", 1.6, y, 0.8, 1))
    # the stamp: a painted lemon on a tile, perforated
    def lem_art(x0, y0, x1, y1):
        a = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#2E62C8"/>']
        a.append(f'<circle cx="{(x0 + x1) / 2}" cy="{(y0 + y1) / 2}" r="{(x1 - x0) * 0.42:.1f}" fill="#FFF6DC"/>')
        a.append(lemon_it(D, (x0 + x1) / 2, (y0 + y1) / 2 + 4, 15, 2313, rot_=-20))
        a.append(citrus_leaf(D, (x0 + x1) / 2 + 6, (y0 + y1) / 2 - 12, 22, -60, 2314, inkw=0.9))
        return "".join(a)
    out.append('<g transform="rotate(5 484 172)">' + stamp(D, 440, 126, 88, 100, 2315, lem_art) + "</g>")
    out.append(label(484, 248, "ITALIA", CINZEL, 16, "#2E62C8", ls=3))
    pm = [f'<circle cx="420" cy="214" r="34" fill="none" stroke="#2A3A6A" stroke-width="2.2" opacity="0.55"/>',
          f'<circle cx="420" cy="214" r="26" fill="none" stroke="#2A3A6A" stroke-width="1.3" opacity="0.55"/>',
          f'<path d="{smooth_closed(heart_d(420, 216, 10))}" fill="#2A3A6A" opacity="0.5"/>']
    for k2 in range(3):
        y = 192 + k2 * 14
        pm.append(f'<path d="M 340 {y} q 10 -6 20 0 t 20 0 t 20 0" stroke="#2A3A6A" stroke-width="2" fill="none" opacity="0.45"/>')
    out.append("".join(pm))
    # the handwritten message across the bottom
    out.append(letters(D, 300, 468, "ti voglio bene", SERIF_IT, 92, "#B8221E", ["#D8382E", "#8A1410", "#E85A4A"], 2316, max_w=470,
                       shadow="#F2D8C0", soff=(0.015, 0.03), angle=-40, hi="#FFA898", rot=-3))
    out.append(p_heart(D, 520, 512, 16, ROSSO, 2317, rot_=12))
    out.append(label(300, 518, "UN BACIO DA LONTANO", JOS, 17, "#5A3A1E", ls=4, max_w=300))
    out.append("</g>")
    return finish_i(D, out, 2318)


# ================================================================ 26. napoli — the bay, Vesuvius, a stone pine and a gozzo
def gozzo(D, cx, wl, L, seed, hull=("#5A9AE0", "#1E5AB0", "#0C2E6A"), band="#FFFFFF", trim="#D8282A"):
    """A Neapolitan gozzo: small wooden fishing boat, painted hull, raised stem post, a white band, oars."""
    out = []
    pts = [(cx - L / 2, wl - L * 0.12), (cx - L * 0.4, wl + L * 0.02), (cx, wl + L * 0.05), (cx + L * 0.4, wl + L * 0.02), (cx + L / 2, wl - L * 0.16),
           (cx + L * 0.52, wl - L * 0.26), (cx + L * 0.44, wl - L * 0.18), (cx, wl - L * 0.12), (cx - L * 0.46, wl - L * 0.16), (cx - L * 0.52, wl - L * 0.22)]
    out.append(f'<path d="{smooth_closed([(x, wl + (wl - y) * 0.8) for x, y in pts])}" fill="{hull[2]}" opacity="0.35"/>')
    out.append(painted(D, pts, hull, seed, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    out.append(taper([(cx - L * 0.48, wl - L * 0.15), (cx, wl - L * 0.1), (cx + L * 0.47, wl - L * 0.18)], L * 0.035, L * 0.035, band))
    out.append(taper([(cx - L * 0.5, wl - L * 0.19), (cx, wl - L * 0.13), (cx + L * 0.5, wl - L * 0.22)], L * 0.02, L * 0.02, trim))
    out.append(pline([(cx - L * 0.2, wl - L * 0.14), (cx - L * 0.1, wl - L * 0.3), (cx - L * 0.04, wl - L * 0.4)], "#C8A060", 2.4, seed, 1, 1))
    out.append(pline([(cx + L * 0.1, wl - L * 0.13), (cx + L * 0.24, wl - L * 0.28)], "#C8A060", 2.4, seed + 1, 1, 1))
    return "".join(out)


@design("napoli")
def napoli():
    D = Doc2("itnp")
    out = [sky(D, [(0, "#7AB4E0"), (0.5, "#C8DCE8"), (1, "#FFE8C8")], 2401, 360, ["#FFFFFF", "#A8D0EC", "#FFF0E0"], 60, angle=-3, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 470, 250, 220, "#FFF4D8", 0.6))
    for k, (x, y, w) in enumerate(((140, 220, 150), (430, 196, 110))):
        out.append(puff_cloud(D, x, y, w, 2402 + k, pal=("#FFFFFF", "#F6F2F0", "#C8C8D8"), op=0.85, rows=1))
    # Vesuvius: the Somma ridge and the cone, hazy violet-blue, a wisp
    ves = [(-20, 322), (80, 304), (170, 270), (230, 248), (262, 252), (296, 236), (330, 214), (346, 204), (372, 206), (392, 218), (440, 252), (520, 290), (620, 310)]
    out.append(hill(D, ves, 360, ("#9A9AC0", "#7A7AA8", "#5A5A88"), 2404, inkw=0, n=40, lit="#C8C8E0"))
    out.append(f'<path d="{smooth_open([(232, 250), (262, 256), (300, 240)])}" stroke="#5A5A88" stroke-width="2" fill="none" opacity="0.5"/>')
    out.append(steam(360, 204, 40, 2405, "#FFFFFF", 1, 10, 8, 0.5))
    out.append(f'<rect x="-10" y="280" width="620" height="80" fill="{D.lin([(0, "#FFF0E0", 0), (1, "#FFF0E0", 0.5)])}"/>')
    # the far shore with a scatter of white towns
    out.append(hill(D, ridge([(-20, 328), (200, 320), (420, 324), (620, 318)], 2406, 4, 3), 344, ("#C8B8A0", "#A89A88", "#8A7A6A"), 2407, inkw=0, n=10))
    out.append(stacked_town(D, 20, 600, 334, 320, 2408, ["#FFFFFF", "#F6E2C8", "#F2C8A8"], haze=0.35, n=60))
    out.append(sea(D, 336, 610, [(0, "#4AA0D0"), (0.5, "#1E6EAA"), (1, "#124A86")], 2409, ["#7AC8EC", "#0E3E70", "#FFFFFF"], 120, ticks=["#FFFFFF", "#A8E0F6"]))
    out.append(wave_lines(2410, (380, 340, 600, 380), ["#FFF6D8"], 30, (10, 30), 2, 2, (0.5, 0.9)))
    # a sailboat far out and a gozzo close in
    out.append(painted(D, [(470, 360), (470, 322), (492, 360)], WHITE, 2411, sk=0.2, n=3, inkw=1, hi=0.4))
    out.append(painted(D, [(460, 362), (500, 362), (494, 368), (466, 368)], ("#8A6A4A", "#5A3A22", "#2A1A0A"), 2412, sk=0.2, n=2, inkw=0.8, hi=0.3))
    out.append(gozzo(D, 360, 486, 190, 2413))
    out.append(gozzo(D, 494, 420, 86, 2414, hull=("#FFFFFF", "#F2EEE6", "#A8A098"), band="#2E8A4C", trim="#F2C21C"))
    # foreground rocks and the stone pine framing the left
    out.append(hill(D, ridge([(-20, 470), (60, 450), (140, 470), (200, 520), (240, 610)], 2415, 10, 3), 610, ("#C8B090", "#8A7458", "#4A3A28"), 2416, inkw=1.6, n=40, lit="#FFF0C8"))
    out.append(umbrella_pine(D, 90, 470, 250, 2417, light=1, rim="#C8D088"))
    out.append(grass(2418, (-10, 450, 200, 600), ["#8A9A4A", "#B8A860", "#6A7A3A"], n=80, h=(8, 18), w=1.6))
    # lettering
    out.append(letters(D, 300, 150, "Napoli", SERIF_IT, 116, "#1E3E86", ["#2E5AB8", "#0C2462", "#3E6AC8"], 2419, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 192, "BELLA NAPOLI", "#B8461E", font=JOS, size=22, ls=8, line_w=30, gap=14, max_w=300))
    return finish_i(D, out, 2420)


# ================================================================ 27. roma — a scooter parked by a fountain in the piazza
def scooter(D, x, base, s, seed, body=("#B8E8D8", "#6AC0A8", "#2E7A68")):
    """A generic vintage scooter (side view, facing left): small wheels, a curved leg shield, flat floor, a
    single saddle, a rounded tail cowl over the engine, chrome bars and a round headlamp. No marks."""
    def P(px, py):
        return (x + px * s, base + py * s)

    def L(pts):
        return [P(px, py) for px, py in pts]
    out = [cast(D, x + 10 * s, base + 2, 120 * s, 8 * s, strength=0.5, seed=seed)]
    # wheels
    for wx in (-82, 78):
        cx, cy = P(wx, -26)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{26 * s:.1f}" fill="#1E1C22"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{14 * s:.1f}" fill="#C8CCD4"/>'
                   f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{5 * s:.1f}" fill="#5A606C"/><path d="M {cx - 10 * s:.1f} {cy - 6 * s:.1f} a {12 * s:.1f} {12 * s:.1f} 0 0 1 {12 * s:.1f} {-6 * s:.1f}" stroke="#FFFFFF" stroke-width="{2 * s:.1f}" fill="none"/>')
    # front fork + mudguard
    out.append(painted(D, L([(-112, -40), (-104, -62), (-82, -70), (-60, -62), (-54, -44), (-70, -46), (-82, -52), (-98, -48)]), body, seed + 1, sdir=(0.5, 1), sk=0.2, n=6, inkw=1.6, hi=0.5))
    # floorboard and leg shield
    out.append(painted(D, L([(-70, -46), (30, -42), (34, -30), (-64, -32)]), ("#5A5A64", "#2E2E36", "#121218"), seed + 2, sk=0.2, n=4, inkw=1.4, hi=0.3))
    shield = L([(-76, -40), (-90, -100), (-96, -150), (-84, -160), (-68, -150), (-56, -100), (-50, -44)])
    out.append(painted(D, shield, body, seed + 3, sdir=(1, 0.3), sk=0.22, angle=-80, n=12, inkw=1.8, hi=0.5))
    # steering column, handlebar and headlamp
    out.append(taper(L([(-84, -158), (-86, -186)]), 8 * s, 7 * s, body[2]))
    out.append(painted(D, L([(-112, -196), (-60, -196), (-54, -186), (-118, -186)]), body, seed + 4, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(taper(L([(-118, -192), (-130, -190)]), 5 * s, 5 * s, "#1E1C22") + taper(L([(-56, -192), (-44, -190)]), 5 * s, 5 * s, "#1E1C22"))
    hx, hy = P(-112, -184)
    out.append(painted(D, blob_pts(hx, hy, 10 * s, 11 * s, seed + 5, 0.03, 12), ("#FFFFFF", "#C8CCD4", "#5A606C"), seed + 5, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(f'<circle cx="{hx - 2 * s:.1f}" cy="{hy:.1f}" r="{6 * s:.1f}" fill="#FFF6D8"/>')
    # rear body cowl
    cowl = L([(14, -42), (6, -80), (26, -112), (70, -118), (112, -100), (122, -60), (110, -40), (86, -36), (78, -50), (60, -52), (44, -40)])
    out.append(painted(D, cowl, body, seed + 6, sdir=(0.6, 0.8), sk=0.2, angle=-30, n=20, inkw=1.8, hi=0.55, hik=0.12))
    out.append(pline(L([(40, -92), (74, -98), (100, -86)]), body[2], 1.6 * s, seed, 0.5, 1))
    # saddle and rack
    out.append(painted(D, L([(10, -112), (24, -132), (92, -130), (106, -116), (60, -110)]), ("#A8704A", "#7A4A2A", "#3A1E0E"), seed + 7, sk=0.2, n=6, inkw=1.5, hi=0.45))
    out.append(pline(L([(100, -122), (132, -122), (134, -108)]), "#B8BCC4", 3 * s, seed, 1, 1))
    tl = P(122, -76)
    out.append(f'<path d="{blob(tl[0], tl[1], 4 * s, 5 * s, seed + 8, 0.05, 8)}" fill="#E8382A"/>')
    return "".join(out)


def fountain(D, cx, base, w, seed):
    """A Roman piazza fountain: low travertine basin, a fluted pedestal with a shell bowl, arcs of water."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, base + 2, w * 0.6, 10, strength=0.45, seed=seed)]
    # pedestal and upper bowl
    out.append(painted(D, rect_pts(cx - w * 0.06, base - w * 0.5, cx + w * 0.06, base - w * 0.12, 8, seed, 0.3), ("#FFF6E6", "#E2D4BC", "#9A8A70"), seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.5))
    bowl = [(cx - w * 0.24, base - w * 0.5), (cx + w * 0.24, base - w * 0.5), (cx + w * 0.16, base - w * 0.42), (cx - w * 0.16, base - w * 0.42)]
    out.append(painted(D, bowl, ("#FFF6E6", "#E2D4BC", "#9A8A70"), seed + 1, sdir=(0.5, 1), sk=0.2, n=6, inkw=1.4, hi=0.5))
    for k in range(7):
        x = cx - w * 0.2 + k * w * 0.067
        out.append(pline([(x, base - w * 0.5), (x + (x - cx) * 0.2, base - w * 0.44)], "#9A8A70", 1.1, k, 0.6, 1))
    # water: a jet up and arcs falling into the basin
    out.append(taper([(cx, base - w * 0.5), (cx, base - w * 0.66)], 4, 1.5, "#E8F8FF", 0.95))
    for sg in (-1, 1):
        for k in range(3):
            r = w * (0.2 + k * 0.06)
            pts = [(cx + sg * w * 0.2 + sg * r * math.sin(t / 8 * math.pi / 2), base - w * 0.48 + r * 1.2 * (1 - math.cos(t / 8 * math.pi / 2))) for t in range(9)]
            out.append(taper(pts, 3, 2, "#DFF6FF", 0.8))
    # basin
    basin = [(cx - w / 2, base - w * 0.2), (cx + w / 2, base - w * 0.2), (cx + w / 2, base), (cx - w / 2, base)]
    out.append(painted(D, poly_pts(basin, 14, seed + 2, 0.5), ("#FFF6E6", "#E2D4BC", "#9A8A70"), seed + 2, sdir=(0.6, 1), sk=0.15, angle=0, n=14, inkw=1.6, hi=0.5))
    out.append(painted(D, rect_pts(cx - w / 2 - 4, base - w * 0.24, cx + w / 2 + 4, base - w * 0.18, 10, seed + 3, 0.3), ("#FFFFFF", "#ECE2D0", "#A89A80"), seed + 3, sdir=(0, 1), sk=0.25, n=6, inkw=1.4, hi=0.6))
    for k in range(10):
        out.append(f'<circle cx="{cx + rnd.uniform(-w * 0.4, w * 0.4):.1f}" cy="{base - w * 0.21 + rnd.uniform(-3, 2):.1f}" r="{rnd.uniform(1.6, 3):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


@design("roma")
def roma():
    D = Doc2("itrm")
    out = [sky(D, [(0, "#8AC0E8"), (1, "#F6E8D0")], 2501, 300, ["#FFFFFF", "#B0D4EE"], 40, angle=-3, sop=(0.08, 0.2))]
    # palazzi around the piazza: ochre, rust and cream, green shutters
    out.append(facade(D, -20, 150, 160, 430, 2502, "#E8A24A", shutters="#3E6A4A", rows=4, cols=2, balcony="#D8322A"))
    out.append(facade(D, 148, 302, 196, 430, 2503, "#D2683A", shutters="#3E6A4A", rows=3, cols=3))
    out.append(facade(D, 300, 452, 186, 430, 2504, "#F2D29A", shutters="#2E5A3E", rows=3, cols=3, balcony="#E8507A"))
    out.append(facade(D, 450, 620, 154, 430, 2505, "#C8783A", shutters="#2E5A3E", rows=4, cols=2))
    out.append(f'<rect x="-10" y="150" width="620" height="290" fill="{D.lin([(0, "#FFF2D8", 0.0), (0.7, "#3A2A2A", 0.05), (1, "#3A2A2A", 0.3)])}"/>')
    # sampietrini cobbles
    out.append(f'<path d="M -10 430 L 610 430 L 610 610 L -10 610 Z" fill="#8A8278"/>')
    rnd = random.Random(2506)
    for j in range(16):
        y = 432 + j * (6 + j * 0.9)
        h = 5 + j * 0.85
        for i in range(-2, int(620 / (8 + j * 1.6)) + 2):
            ww = 8 + j * 1.6
            x = -10 + i * ww + (j % 2) * ww / 2
            c = mix("#9A9288", rnd.choice(["#B8B0A4", "#7A7268", "#A8A094", "#6A645C"]), rnd.uniform(0.2, 0.7))
            out.append(f'<path d="{hg.org_rect(x + 1, y + 1, ww - 2, h - 1.5, i * 37 + j, 0.4, 6, h * 0.35)}" fill="{c}"/>')
    out.append(f'<rect x="-10" y="430" width="620" height="180" fill="{D.lin([(0, "#3A3028", 0.35), (0.5, "#3A3028", 0.0), (1, "#3A3028", 0.15)])}"/>')
    # the fountain at left, the scooter at right, a street lamp
    out.append(fountain(D, 180, 498, 230, 2507))
    out.append(taper([(476, 498), (478, 260)], 7, 5, "#2A2A30"))
    out.append(taper([(478, 262), (500, 246), (520, 252)], 4, 3, "#2A2A30"))
    out.append(painted(D, [(510, 252), (530, 252), (534, 276), (506, 276)], ("#FFF2C0", "#F6D27A", "#A88A3A"), 2508, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(scooter(D, 408, 540, 0.95, 2509))
    # pigeons
    for k, (x, y, f) in enumerate(((300, 520, 1), (330, 530, -1))):
        out.append(hg.songbird(D, x, y, 12, 2510 + k, body="#8A8AA0", belly="#C8C8D8", flip=f, beak="#3A3A3A"))
    # lettering
    out.append(letters(D, 300, 134, "ROMA", CINZEL, 112, "#8A2A16", ["#B03A1A", "#5A1A08", "#C8582A"], 2511, ls=14, max_w=380,
                       shadow="#FFF2D8", soff=(0.02, 0.035), angle=-40, hi="#F2A070", wob=0.4))
    out.append(ruled(300, 176, "LA CITTÀ ETERNA", "#1E4A86", font=JOS, size=20, ls=6, line_w=30, gap=12, max_w=300))
    return finish_i(D, out, 2512)


# ================================================================ 28. burano — the island of colours
def burano_house(D, x0, x1, top, base, seed, wall, door="#2E4A6A"):
    """A narrow Burano house: saturated plaster, white-framed windows with green shutters, a chimney,
    a flower pot on a sill, a door at the fondamenta."""
    rnd = random.Random(seed)
    w = x1 - x0
    out = [painted(D, rect_pts(x0, top, x1, base, 16, seed, 0.5), (lt(wall, 0.25), wall, dk(wall, 0.25)), seed, sdir=(1, 0.3), sk=0.06, angle=-80, n=int(w * (base - top) / 160), inkw=1.4, inkop=0.5, hi=0.25)]
    out.append(f'<path d="{hg.org_rect(x0 - 3, top - 6, w + 6, 8, seed + 1, 0.3, 8, 1)}" fill="#F4EEE4"/>')
    if rnd.random() < 0.7:
        cx = x0 + w * rnd.uniform(0.2, 0.8)
        out.append(venetian_chimney(D, cx, top - 30, 24, mix(wall, "#FFFFFF", 0.3)))
    rows = int((base - top - 40) / 52)
    for j in range(rows):
        y = top + 18 + j * 52
        nw = 2 if w > 70 else 1
        for i in range(nw):
            wx = x0 + w * ((i + 0.5) / nw) - 10
            out.append(f'<path d="{hg.org_rect(wx - 4, y - 4, 28, 36, seed + j * 7 + i, 0.3, 6, 1)}" fill="#FFFFFF"/>')
            out.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="20" height="28" fill="#2A3442"/>')
            out.append(f'<path d="M {wx + 10:.1f} {y:.1f} l 0 28 M {wx:.1f} {y + 12:.1f} l 20 0" stroke="#FFFFFF" stroke-width="1.6"/>')
            for sg in (-1, 1):
                sx = wx + 10 + sg * 18
                out.append(f'<path d="{hg.org_rect(sx - 5, y - 2, 10, 32, seed + j + i + sg, 0.2, 6, 0.5)}" fill="#2E6A4A"/>')
            if rnd.random() < 0.35:
                for k in range(4):
                    out.append(f'<circle cx="{wx + 3 + k * 5:.1f}" cy="{y + 30:.1f}" r="3" fill="{rnd.choice(["#E8282A", "#FF6A8A", "#FFFFFF"])}"/>')
                out.append(f'<rect x="{wx - 1:.1f}" y="{y + 31:.1f}" width="22" height="5" fill="#B8603A"/>')
    dx = x0 + w * 0.5 - 12
    out.append(f'<path d="{hg.org_rect(dx, base - 46, 24, 46, seed + 40, 0.3, 6, 1)}" fill="{door}"/>')
    out.append(f'<path d="{hg.org_rect(dx - 3, base - 50, 30, 5, seed + 41, 0.3, 6, 1)}" fill="#FFFFFF"/>')
    return "".join(out)


def sandolo(D, cx, wl, L, seed, hull=("#F2F2F0", "#D8D8D4", "#8A8A88"), stripe="#1E8A4C"):
    out = []
    pts = [(cx - L / 2, wl - 10), (cx - L * 0.4, wl + 4), (cx + L * 0.4, wl + 4), (cx + L / 2, wl - 14), (cx + L * 0.44, wl - 10), (cx - L * 0.44, wl - 8)]
    out.append(f'<path d="{smooth_closed([(x, wl + (wl - y) * 0.8 + 6) for x, y in pts])}" fill="#0E2A3A" opacity="0.3"/>')
    out.append(painted(D, pts, hull, seed, sdir=(0, 1), sk=0.2, n=8, inkw=1.4, hi=0.4))
    out.append(taper([(cx - L * 0.46, wl - 8), (cx, wl - 5), (cx + L * 0.46, wl - 11)], 3, 3, stripe))
    return "".join(out)


@design("burano")
def burano():
    D = Doc2("itbr")
    out = [sky(D, [(0, "#7EC0EC"), (1, "#DDF0F8")], 2601, 260, ["#FFFFFF", "#A8D8F2"], 40, angle=-3, sop=(0.08, 0.2))]
    for k, (x, y, w) in enumerate(((120, 210, 130), (470, 196, 150))):
        out.append(puff_cloud(D, x, y, w, 2602 + k, op=0.9, rows=1))
    houses = [(-20, 70, 214, "#E8507A"), (68, 168, 236, "#F6C81E"), (166, 238, 196, "#2E7AC8"), (236, 338, 228, "#E8452A"),
              (336, 410, 206, "#5AB86A"), (408, 504, 230, "#9A5AC8"), (502, 620, 210, "#F28A1E")]
    for k, (x0, x1, top, c) in enumerate(houses):
        out.append(burano_house(D, x0, x1, top, 446, 2610 + k * 13, c, door=["#2E4A6A", "#5A3A22", "#1E6A3A", "#2E4A6A", "#8A2A1A", "#2E4A6A", "#5A3A22"][k]))
    # laundry line between two windows
    out.append(pline([(80, 300), (160, 316), (232, 298)], "#5A4A3A", 1.4, 2620, 0.9, 1))
    for k, (x, c, w, h) in enumerate(((104, "#FFFFFF", 18, 26), (130, "#F2B8C8", 20, 20), (182, "#8AC8F0", 16, 30), (206, "#FFE27A", 14, 18))):
        y = 300 + 16 * math.sin(math.pi * (x - 80) / 152) * 0.9
        out.append(painted(D, rect_pts(x - w / 2, y, x + w / 2, y + h, 6, 2621 + k, 0.5), pal3(c, 0.2, 0.25), 2621 + k, sk=0.2, n=3, inkw=1.1, hi=0.4))
    # fondamenta edge and canal with mirrored colour
    out.append(painted(D, rect_pts(-10, 444, 610, 458, 30, 2630, 0.4), ("#F6F0E6", "#D8D0C2", "#8A8274"), 2630, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    out.append(sea(D, 458, 610, [(0, "#3AA0B0"), (1, "#1E6A80")], 2631, ["#6AC8D0", "#0E4A5A", "#FFFFFF"], 80))
    for x0, x1, top, c in houses:
        rr = random.Random(int(x0) + 70)
        for k in range(22):
            y = 464 + k * 6 + rr.uniform(-1, 1)
            xa, xb = x0 + rr.uniform(2, 10), x1 - rr.uniform(2, 10)
            out.append(taper([(xa, y), ((xa + xb) / 2, y + rr.uniform(-1.5, 1.5)), (xb, y)], 0.6, rr.uniform(2.4, 4), mix(c, "#1E6A80", 0.25 + k * 0.025), 0.75 - k * 0.02))
    out.append(wave_lines(2632, (0, 470, 600, 600), ["#FFFFFF", "#BFF0F0"], 50, (10, 30), 2, 2, (0.4, 0.8)))
    out.append(sandolo(D, 170, 508, 150, 2633))
    out.append(sandolo(D, 420, 530, 170, 2634, hull=("#5A9AE0", "#1E5AB0", "#0C2E6A"), stripe="#F6C81E"))
    for x in (96, 520):
        out.append(palina(D, x, 470, 540, 2635 + x, cols=("#E8452A", "#FFFFFF"), w=8))
    # lettering
    out.append(letters(D, 300, 140, "Burano", SERIF_IT, 128, "#FFFFFF", ["#FFFFFF", "#F2F6FA", "#E0ECF6"], 2640, max_w=380,
                       shadow="#1E4A86", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "L'ISOLA DEI COLORI", "#1E4A86", font=JOS, size=20, ls=6, line_w=28, gap=12, max_w=320))
    return finish_i(D, out, 2641)


# ================================================================ 29. famiglia — the old olive tree, deep roots
def olive_tree(D, cx, base, h, seed):
    """An ancient olive: a twisted, hollowed, multi-stemmed trunk, flaring roots, and a silver-green crown
    of dabs and slender leaves catching the light."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 20, base + 4, h * 0.6, 14, strength=0.45, seed=seed)]
    bark = ("#B8A07A", "#7A6448", "#3A2E1E")
    # trunk: two twisting stems and a hollow
    for k, (pts, w0, w1) in enumerate(((catmull([(cx - 50, base), (cx - 60, base - h * 0.2), (cx - 30, base - h * 0.42), (cx - 70, base - h * 0.62)], 6), 54, 18),
                                       (catmull([(cx + 40, base), (cx + 58, base - h * 0.18), (cx + 26, base - h * 0.4), (cx + 60, base - h * 0.64)], 6), 50, 16),
                                       (catmull([(cx - 4, base - h * 0.2), (cx + 6, base - h * 0.42), (cx - 10, base - h * 0.66)], 6), 26, 10))):
        out.append(taper(pts, w0, w1, bark[1]))
        out.append(taper([(x - w0 * 0.2, y) for x, y in pts], w0 * 0.3, w1 * 0.3, bark[0], 0.7))
        out.append(taper([(x + w0 * 0.25, y) for x, y in pts], w0 * 0.25, w1 * 0.25, bark[2], 0.55))
        for j in range(5):
            i = rnd.randint(1, len(pts) - 2)
            x, y = pts[i]
            out.append(pline([(x - 8, y - 6), (x, y + 4), (x + 6, y - 2)], bark[2], 1.4, k * 9 + j, 0.6, 1))
    out.append(f'<path d="{blob(cx - 6, base - h * 0.14, 11, 22, seed, 0.2, 12)}" fill="#4A3A26"/>')
    out.append(f'<path d="{blob(cx - 4, base - h * 0.13, 7, 16, seed + 1, 0.2, 10)}" fill="#2A1E12"/>')
    # roots
    for sg, L in ((-1, 70), (1, 64), (-1, 40), (1, 36)):
        pts = catmull([(cx + sg * 30, base - 10), (cx + sg * (30 + L * 0.5), base - 2), (cx + sg * (30 + L), base + 4)], 4)
        out.append(taper(pts, 16, 3, bark[1]))
    # branches up into the crown
    for k, (a, b) in enumerate((((cx - 70, base - h * 0.62), (cx - 150, base - h * 0.82)), ((cx - 70, base - h * 0.62), (cx - 40, base - h * 0.92)),
                                ((cx + 60, base - h * 0.64), (cx + 150, base - h * 0.84)), ((cx + 60, base - h * 0.64), (cx + 40, base - h * 0.94)), ((cx - 10, base - h * 0.66), (cx, base - h)))):
        out.append(taper([a, ((a[0] + b[0]) / 2 + 8, (a[1] + b[1]) / 2), b], 14, 4, bark[1]))
    # crown: masses of olive green with silvery light, then individual leaf strokes
    pals = [("#C8D0A8", "#8A9A62", "#4E5A34"), ("#B8C498", "#7A8A52", "#3E4A28")]
    for k, (x, y, rx, ry) in enumerate(((cx - 140, base - h * 0.86, 100, 62), (cx + 140, base - h * 0.88, 104, 64), (cx, base - h * 0.98, 130, 74),
                                        (cx - 60, base - h * 1.08, 90, 56), (cx + 70, base - h * 1.06, 92, 58))):
        out.append(dab_crown(D, x, y, rx, ry, pals, seed + k, n=180, size=(6, 12), light=(-0.5, -0.85), inkw=1.2, inkc="#3E4A28"))
    for k in range(120):
        a = rnd.uniform(0, 6.28)
        rr = math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * 230 * rr, base - h * 0.96 + math.sin(a) * 90 * rr
        if abs(x - cx) > 260:
            continue
        b = rnd.uniform(0, 360)
        out.append(olive_leaf(D, x, y, rnd.uniform(14, 22), b, seed + k, pal=("#E0E6C8", "#9AA870", "#4E5A34"), inkw=0))
    for k in range(10):
        x, y = cx + rnd.uniform(-200, 200), base - h * rnd.uniform(0.8, 1.0)
        out.append(olive(x, y, 5, rnd.uniform(0, 180), ("#7A6A8A", "#3A2A4A", "#1A0E22")))
    return "".join(out)


@design("famiglia")
def famiglia():
    D = Doc2("itfm")
    out = [sky(D, [(0, "#F8D8A0"), (0.6, "#FCE8C0"), (1, "#FFF4DC")], 2701, 420, ["#FFF0D0", "#F2C890", "#FFFBEA"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 300, 260, "#FFF6D0", 0.6))
    out.append(hill(D, ridge([(-20, 400), (160, 380), (340, 394), (480, 376), (620, 390)], 2702, 6, 3), 450, ("#D8C8A0", "#B8A880", "#8A7A5A"), 2703, inkw=0, n=20))
    rr = random.Random(2704)
    for k in range(8):
        out.append(cypress(D, rr.uniform(20, 580), 392 + rr.uniform(-4, 6), rr.uniform(20, 34), 2705 + k, pal=("#A8A880", "#7A8060", "#5A6048"), w=6))
    # golden meadow
    out.append(hill(D, ridge([(-20, 452), (200, 440), (400, 452), (620, 440)], 2715, 6, 3), 610, ("#E8D07A", "#C8A850", "#8A7030"), 2716, inkw=1.2, n=80, lit="#FFF2B0"))
    out.append(grass(2717, (-10, 450, 610, 610), ["#D8B860", "#F2D890", "#B8983A", "#9AA04A"], n=260, h=(10, 24), w=1.8))
    # the old olive tree
    out.append(olive_tree(D, 300, 492, 280, 2718))
    # a long bench under it with a folded checked cloth and a basket
    out.append('<g transform="translate(0 -16)">')
    out.append(painted(D, rect_pts(176, 488, 424, 500, 20, 2719, 0.4), ("#E8B86A", "#B07A3A", "#5A3A14"), 2719, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.45))
    for x in (190, 410):
        out.append(painted(D, rect_pts(x - 5, 500, x + 5, 528, 6, 2720 + x, 0.3), ("#C8904E", "#8A5A2A", "#4A2A10"), 2720 + x, sk=0.2, n=3, inkw=1.2, hi=0.3))
    out.append(cloth(D, [(212, 476), (276, 474), (282, 490), (208, 492)], "#D8322A", 2721, cell=7))
    out.append(wicker_front(D, 362, 470, 60, 20, 2722))
    out.append(lemon_it(D, 352, 466, 9, 2723, rot_=-10) + lemon_it(D, 372, 464, 9, 2724, rot_=14))
    out.append('</g>')
    # lettering
    out.append(letters(D, 300, 144, "famiglia", SERIF_IT, 118, "#5A3A1A", ["#7A522A", "#3A220E", "#8A6A3A"], 2725, max_w=400,
                       shadow="#FFF6E0", soff=(0.02, 0.035), angle=-40, hi="#D8B888"))
    out.append(ruled(300, 534, "LA FAMIGLIA È TUTTO", "#5A3A1A", font=JOS, size=20, ls=5, line_w=26, gap=12, max_w=340))
    return finish_i(D, out, 2726)


# ================================================================ 30. la cucina della nonna — shelves, copper and the Sunday dough
def copper_pan(D, cx, top, r, seed, handle_len=60):
    """A hanging copper saucepan seen side-on: polished body, a long brass handle up to a hook."""
    out = [taper([(cx, top), (cx + 2, top - handle_len)], 6, 5, "#B88A3A")]
    out.append(f'<circle cx="{cx + 2:.1f}" cy="{top - handle_len - 4:.1f}" r="5" fill="none" stroke="#5A4A3A" stroke-width="2"/>')
    pts = [(cx - r, top), (cx + r, top), (cx + r * 0.96, top + r * 1.3), (cx + r * 0.7, top + r * 1.45), (cx - r * 0.7, top + r * 1.45), (cx - r * 0.96, top + r * 1.3)]
    out.append(painted(D, pts, COPPER, seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.5, hik=0.15))
    out.append(taper([(cx - r * 0.55, top + 4), (cx - r * 0.6, top + r * 1.3)], r * 0.14, r * 0.08, "#FFE0C0", 0.7))
    out.append(taper([(cx - r * 1.04, top), (cx + r * 1.04, top)], 4, 4, "#E8A060"))
    return "".join(out)


def preserve_jar(D, cx, base, w, h, seed, fill=("#F27A5A", "#C8281A", "#6A0A06"), lid="#E8C860", cloth_top=None):
    out = [cast(D, cx + 4, base + 1, w * 0.6, 4, strength=0.35, seed=seed)]
    body = rect_pts(cx - w / 2, base - h, cx + w / 2, base, 8, seed, 0.3)
    out.append(painted(D, body, fill, seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=6, inkw=1.3, hi=0.4))
    out.append(taper([(cx - w * 0.28, base - h * 0.85), (cx - w * 0.3, base - h * 0.15)], 3, 1.5, "#FFFFFF", 0.6))
    if cloth_top:
        cl = [(cx - w * 0.62, base - h - 2), (cx, base - h - 8), (cx + w * 0.62, base - h - 2), (cx + w * 0.55, base - h + 8), (cx - w * 0.55, base - h + 8)]
        out.append(gingham(D, smooth_closed(cl), cloth_top, "#FFFDF6", 5, 0, 0.6) + ink(smooth_closed(cl), INK, 1, seed, 1, 0.5))
        out.append(pline([(cx - w * 0.5, base - h + 6), (cx + w * 0.5, base - h + 6)], "#C8A060", 1.4, seed, 0.9, 1))
    else:
        out.append(painted(D, rect_pts(cx - w * 0.52, base - h - 7, cx + w * 0.52, base - h + 2, 6, seed + 1, 0.2), (lt(lid, 0.3), lid, dk(lid, 0.35)), seed + 1, sk=0.2, n=3, inkw=1.1, hi=0.5))
    out.append(painted(D, rect_pts(cx - w * 0.34, base - h * 0.62, cx + w * 0.34, base - h * 0.3, 6, seed + 2, 0.3), ("#FFFDF0", "#F2E6C8", "#B8A27A"), seed + 2, sk=0.15, n=2, inkw=0.9, hi=0.3))
    out.append(pline([(cx - w * 0.22, base - h * 0.47), (cx + w * 0.2, base - h * 0.46)], "#5A3A1E", 1.2, seed, 0.8, 1))
    return "".join(out)


@design("la-cucina-della-nonna")
def la_cucina_della_nonna():
    D = Doc2("itcn2")
    out = [sky(D, [(0, "#F6EAD0"), (1, "#EAD6B0")], 2801, 600, ["#FFFFFF", "#E0C898", "#FFF6E2"], 100, angle=-80, sop=(0.06, 0.16))]
    out.append(blooms(2802, ["#E0C898", "#FFFFFF"], 6, (0, 0, 600, 460), (90, 170), (0.06, 0.12)))
    # majolica band at the back of the counter
    out.append(tile_wall(D, -24, 384, 624, 448, 64, 2803))
    out.append(f'<rect x="0" y="384" width="600" height="64" fill="{D.lin([(0, "#1A0E04", 0.25), (1, "#1A0E04", 0.05)])}"/>')
    # the shelf with jars of passata, peppers sott'olio, apricot jam
    out.append(painted(D, rect_pts(-10, 300, 610, 314, 30, 2804, 0.4), WOOD, 2804, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.45))
    for x in (60, 540):
        out.append(painted(D, [(x - 8, 314), (x + 8, 314), (x + 2, 340), (x - 2, 340)], WOOD, 2805 + x, sk=0.2, n=3, inkw=1.2, hi=0.3))
    jars = [(110, 34, 66, ("#F27A5A", "#C8281A", "#6A0A06"), None, "#D8322A"), (156, 30, 54, ("#FFC86A", "#F29A1E", "#9A5A0A"), "#E8C860", None),
            (198, 32, 62, ("#B8C860", "#7A9A2A", "#3E5A12"), None, "#1E8A4C"), (414, 34, 70, ("#F27A5A", "#C8281A", "#6A0A06"), "#E8C860", None),
            (458, 30, 56, ("#F2A0A0", "#C8405A", "#6A0A1E"), None, "#D8322A"), (500, 30, 62, ("#F27A5A", "#C8281A", "#6A0A06"), "#E8C860", None)]
    for k, (x, w, h, f, lid, ct) in enumerate(jars):
        out.append(preserve_jar(D, x, 300, w, h, 2810 + k, f, lid or "#E8C860", ct))
    # copper pans hanging from a rail, a garlic braid and a string of chillies
    out.append(pline([(220, 236), (380, 236)], "#5A4A3A", 3, 2820, 1, 1))
    for k, (x, r) in enumerate(((246, 22), (300, 28), (354, 20))):
        out.append(copper_pan(D, x, 262 + (28 - r), r, 2821 + k, handle_len=26 + (28 - r)))
    for k in range(4):
        out.append(garlic(D, 40 + (k % 2) * 8, 330 + k * 28, 14, 2830 + k, rot_=(k % 2) * 16 - 8))
    for k in range(6):
        x, y = 566 - (k % 2) * 8, 324 + k * 22
        out.append(painted(D, rot([(x - 5, y), (x + 5, y), (x + 3, y + 22), (x, y + 28), (x - 3, y + 22)], x, y, (k % 2) * 20 - 10), ("#FF7A5A", "#D8221A", "#7A0A06"), 2840 + k, sk=0.2, n=3, inkw=1, hi=0.5))
    # the table: flour, the dough ball, rolling pin, a bowl of eggs, the wooden spoon
    out.append(wood_planks(D, 448, 600, 2850, WOOD, 3))
    out.append(f'<rect y="446" width="600" height="8" fill="#3A2010" opacity="0.45"/>')
    out.append(flour_drift(D, 260, 516, 150, 40, 2851, 0.75))
    out.append(cast(D, 250, 520, 70, 12, strength=0.35, seed=2852))
    out.append(painted(D, blob_pts(244, 496, 66, 34, 2853, 0.05, 18), ("#FFF8E8", "#F6E6C2", "#C8B080"), 2853, sdir=(0.5, 0.9), sk=0.2, angle=-20, n=16, inkw=1.6, hi=0.55))
    out.append(specks(2854, (190, 470, 300, 520), ["#FFFFFF"], 40, (0.6, 1.4), (0.6, 0.95)))
    out.append(rolling_pin(D, 316, 540, 520, 494, 24, 2855))
    out.append(cast(D, 104, 526, 54, 10, strength=0.35, seed=2856))
    out.append(painted(D, [(54, 486), (154, 486), (140, 524), (68, 524)], ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 2857, sdir=(0.8, 0.4), sk=0.2, n=8, inkw=1.6, hi=0.4))
    out.append(ink(smooth_open([(58, 494), (104, 498), (150, 494)]), COBALTO[1], 2.4, 2857, 1, 0.9))
    for k, (x, y) in enumerate(((84, 480), (108, 474), (128, 482))):
        out.append(painted(D, blob_pts(x, y, 13, 16, 2858 + k, 0.03, 12), ("#FFF2DE", "#F2D8B4", "#B8946A"), 2858 + k, sdir=(0.6, 0.8), sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(wooden_spoon(D, 520, 452, 420, 470, 2862, bowl=True, w=10))
    # lettering
    out.append(ruled(300, 92, "LA CUCINA DELLA", "#1F4BA8", font=JOS, size=24, ls=8, line_w=30, gap=14, max_w=360))
    out.append(letters(D, 300, 196, "nonna", SERIF_IT, 136, "#9A2A16", ["#C83A1E", "#6A1A0A", "#D85A3A"], 2863, max_w=360,
                       shadow="#FFE8C8", soff=(0.02, 0.035), angle=-40, hi="#F2A078"))
    return finish_i(D, out, 2864)


# ================================================================ 31. la vendemmia — September in the vineyard
@design("la-vendemmia")
def la_vendemmia():
    D = Doc2("itvd")
    out = [sky(D, [(0, "#F6C888"), (0.5, "#FCE0B0"), (1, "#FFF2D8")], 2901, 330, ["#FFE8C0", "#F2B880", "#FFF6E0"], 60, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 140, 250, 240, "#FFF6D0", 0.7))
    out.append(hill(D, ridge([(-20, 280), (120, 262), (300, 276), (460, 254), (620, 270)], 2902, 8, 3), 340, ("#D8B8A8", "#B89890", "#987878"), 2903, inkw=0, n=20))
    # hill town
    out.append(stacked_town(D, 380, 520, 272, 244, 2904, ["#F6D8A0", "#E8C090", "#F2E0C0"], haze=0.35, n=26))
    out.append(f'<path d="{hg.org_rect(452, 222, 12, 40, 2905, 0.2, 6, 1)}" fill="#C8A88A"/><path d="M 450 224 L 458 212 L 466 224 Z" fill="#B87A60"/>')
    # vineyard: rows sweeping toward the viewer in autumn colours
    out.append(hill(D, ridge([(-20, 300), (200, 290), (400, 304), (620, 292)], 2906, 6, 3), 610, ("#C8B868", "#9A8A40", "#5A5022"), 2907, inkw=1.2, n=60, lit="#FFF0A8"))
    vx, vy = 300, 286
    for k in range(-9, 10):
        xb = 300 + k * 104
        pts = catmull([(vx + k * 6, vy + 14), (vx + k * 30, vy + 110), (xb, 640)], 10)
        # the trodden earth between rows
        out.append(taper([(x + 0.5 * 52 * (y - vy) / 354, y) for x, y in pts], 1, 30, "#B8945A", 0.35))
        rr = random.Random(2910 + k)
        # posts and wire
        out.append(taper(pts, 0.8, 2.2, "#5A4A2A", 0.7))
        for j in range(0, len(pts), 3):
            x, y = pts[j]
            t = (y - vy) / (640 - vy)
            out.append(f'<path d="M {x:.1f} {y:.1f} l 0 {-6 - t * 40:.1f}" stroke="#6A5232" stroke-width="{1 + t * 3:.1f}"/>')
        # foliage along the row: leaves thicken toward us
        for j in range(len(pts) * 3):
            i = rr.randint(0, len(pts) - 1)
            x, y = pts[i]
            t = (y - vy) / (640 - vy)
            sz = 2.4 + t * 12
            out.append(f'<path d="{blob(x + rr.uniform(-sz, sz), y - sz * 1.4 + rr.uniform(-sz * 0.5, sz * 0.4), sz, sz * 0.75, rr.randint(1, 999), 0.2, 8)}" fill="{rr.choice(["#C8A030", "#A8B040", "#D8782A", "#8A9A30", "#B8502A", "#E8B840", "#7A8A2A"])}" opacity="0.95"/>')
            if t > 0.3 and rr.random() < 0.035:
                out.append(grape_bunch(D, x + rr.uniform(-sz, sz), y - sz * 0.4, 1.2 + t * 2.6, rr.randint(1, 999)))
    out.append(f'<rect x="-10" y="280" width="620" height="60" fill="{D.lin([(0, "#FFF0D0", 0.55), (1, "#FFF0D0", 0)])}"/>')
    # foreground: the harvest basket heaped with grapes, shears, vine leaves
    bx, by = 300, 450
    out.append(cast(D, bx + 14, by + 74, 170, 18, strength=0.5, seed=2930))
    for k, (x, y, s, pal) in enumerate(((bx - 90, by - 20, 8, ("#9A6AB0", "#5A2A6A", "#2A0E36")), (bx - 30, by - 40, 9, ("#9A6AB0", "#5A2A6A", "#2A0E36")),
                                        (bx + 40, by - 34, 8.5, ("#C8D870", "#8AA840", "#4A6A1A")), (bx + 100, by - 18, 8, ("#9A6AB0", "#5A2A6A", "#2A0E36")),
                                        (bx - 60, by - 6, 8, ("#B07AC0", "#6A3A7A", "#341444")), (bx + 70, by - 4, 8, ("#9A6AB0", "#5A2A6A", "#2A0E36")))):
        out.append(grape_bunch(D, x, y, s, 2931 + k, pal))
    out.append(wicker_front(D, bx, by, 300, 84, 2940))
    for k, (x, y, r, a) in enumerate(((bx - 160, by + 50, 34, -30), (bx + 168, by + 40, 32, 20), (bx - 130, by - 20, 28, -60))):
        out.append(vine_leaf(D, x, y, r, a, 2941 + k, pal=[("#F2C860", "#D8902A", "#7A4A10"), ("#E87A4A", "#B8402A", "#6A1A0A"), ("#C8C860", "#8A9A30", "#4A5A1A")][k]))
    # pruning shears on the ground
    sx, sy = 476, 526
    out.append(painted(D, rot([(sx - 40, sy - 4), (sx, sy - 6), (sx + 4, sy + 2), (sx - 40, sy + 6)], sx, sy, -14), ("#F2685A", "#C8281A", "#6A0A06"), 2950, sk=0.2, n=4, inkw=1.3, hi=0.5))
    out.append(painted(D, rot([(sx - 40, sy + 10), (sx, sy + 2), (sx + 4, sy + 10), (sx - 36, sy + 18)], sx, sy, -14), ("#F2685A", "#C8281A", "#6A0A06"), 2951, sk=0.2, n=4, inkw=1.3, hi=0.5))
    out.append(painted(D, rot([(sx + 2, sy - 4), (sx + 34, sy - 10), (sx + 40, sy - 4), (sx + 4, sy + 6)], sx, sy, -14), ALU, 2952, sk=0.2, n=3, inkw=1.2, hi=0.6))
    # lettering
    out.append(letters(D, 300, 140, "la vendemmia", SERIF_IT, 110, "#6A1E3A", ["#8A2A4A", "#4A0E24", "#A84A62"], 2953, max_w=460,
                       shadow="#FFF2D8", soff=(0.02, 0.035), angle=-40, hi="#E8A0B0"))
    out.append(ruled(300, 184, "SETTEMBRE IN VIGNA", "#7A4A10", font=JOS, size=20, ls=6, line_w=28, gap=12, max_w=320))
    return finish_i(D, out, 2954)


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
