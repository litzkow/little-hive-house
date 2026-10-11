"""India, hand-painted (gouache / storybook) edition: 30 magnets for Indian-American families and anyone who loves India.

Same idiom as the Brasil, Korea and Ireland sets: warm paper, layered washes with pooled edges, brush strokes that
follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Hero words are
romanized Hindi (and a little Tamil-English, Gujarati and plain English), because the site fonts carry no Devanagari;
the one Devanagari word (माँ, "Maa") is painted stroke by stroke as brush calligraphy, never set in a font.
Colour story: marigold saffron, turmeric yellow, sindoor vermilion, rani pink, peacock blue-green, indigo, mango,
leaf green, terracotta clay and bright stainless steel, on warm cream paper.

Gallery upgrade (paint_india_kit.py): every piece is painted as a scene with a light source, cast shadows, haze and a
value structure, then finished inside an SVG brush filter (broken edges, bristle texture, pigment grain) while the
lettering stays crisp on top.  Vehicles, rooms and lanes are drawn through a small perspective camera; people appear
only as small, properly proportioned silhouettes; the peacock, the Taj and the Hawa Mahal are built from their
real anatomy / massing.

Run from tools/designs:  python3 india_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (mist, blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, banana_leaf, stripes_in
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, leaf_simple, branch, wood_planks, heart_d,
                            steam, finish_b, bird_v, p_heart)
from japan_painted import densify, round_poly, clipped
import holidays_gouache as hg
import brasil_painted as bp
import paint_india_kit as pk
from paint_india_kit import finish_art, modelled, glaze, vignette, haze_band, dabs, Cam3, figure, lit_line, pdl, coco_palm

COL = "india"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
SAFFRON = ("#FFC46A", "#F2901E", "#A8520A")       # marigold / kesari
HALDI = ("#FFE88A", "#F4C21A", "#B08008")         # turmeric
SINDOOR = ("#F57A5E", "#D6342A", "#8A1210")       # vermilion
RANI = ("#FF8AB8", "#D6246E", "#8A0E40")          # rani pink
PEACOCK = ("#5EC0C0", "#12808A", "#084650")       # peacock blue-green
INDIGO = ("#6A7AD0", "#2A3A90", "#121C52")
MANGO = ("#FFD46A", "#F6A21E", "#B8600A")
LEAF = ("#9ACB6A", "#3E8A3A", "#1A4A1E")
CLAY = ("#E8986A", "#B85E34", "#6A2A12")
STEEL = ("#FFFFFF", "#CDD3DA", "#6E7884")
BRASS = ("#FFE6A0", "#D8A84A", "#7A5414")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
DARKWOOD = ("#9A6A44", "#5E3820", "#2A160A")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
GOLDFRY = ("#FCE0A0", "#E2A64A", "#9A5A16")       # fried golden pastry
PAPER = "#F6ECDA"

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


lt, dk = hg.lt, hg.dk


# ================================================================ india toolkit
def ellipse_d(cx, cy, rx, ry, n=36):
    return smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, n)[:-1])


def leaf_lite(D, x, y, L, W, ang, pal, seed, vein=True, inkw=1.0):
    """A painted leaf at a fraction of leaf_simple's weight: one graded fill lit from the upper left, a handful of
    strokes along the blade, a pale midrib and a light ink edge."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(9):
        t = i / 8
        w = W * math.sin(math.pi * t) ** 0.85 * (1 - 0.3 * t)
        bend = 0.08 * L * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    g = D.lin([(0, pal[0]), (0.5, pal[1]), (1, pal[2])], x0, y0, x1, y1, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{g}"/>']
    rnd = random.Random(seed)
    for k in range(min(8, int(L / 8) + 2)):
        t0 = rnd.uniform(0.1, 0.7)
        s0 = rnd.uniform(-0.6, 0.6) * W * 0.6
        p0 = (x + ux * L * t0 + nx * s0, y + uy * L * t0 + ny * s0)
        p1 = (p0[0] + ux * L * 0.25, p0[1] + uy * L * 0.25)
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice([pal[0], pal[2]])}" stroke-width="{max(0.8, W * 0.12):.1f}" opacity="0.3" stroke-linecap="round"/>')
    if vein:
        out.append(f'<path d="M {x:.1f} {y:.1f} Q {x + ux * L * 0.5 + nx * 0.02 * L:.1f} {y + uy * L * 0.5 + ny * 0.02 * L:.1f} {x + ux * L * 0.92 + nx * 0.07 * L:.1f} {y + uy * L * 0.92 + ny * 0.07 * L:.1f}" stroke="{lt(pal[0], 0.35)}" stroke-width="{max(0.8, W * 0.08):.1f}" fill="none" opacity="0.7"/>')
    if inkw:
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{inkw}" opacity="0.45"/>')
    return "".join(out)


def metal(D, d, x0, x1, pal=STEEL, op=0.85, dark_edge=0.75):
    """Polished metal painted, not airbrushed: soft bands of light and dark across the form, broken by vertical
    brush strokes in the band colours, a warm bounce at the shadow edge and one crisp dry-brush highlight."""
    light, base, dark = pal
    g = D.lin([(0, dark, dark_edge), (0.1, base, 0.2), (0.24, light, op), (0.3, "#FFFFFF", op * 0.9), (0.38, base, 0.1),
               (0.62, dark, 0.35), (0.72, base, 0.1), (0.86, light, 0.5), (1, dark, dark_edge)], x0, 0, x1, 0, "userSpaceOnUse")
    w = max(4, x1 - x0)
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(int(x0 * 13 + x1 * 7))
    st = []
    for _ in range(int(w / 3.5)):
        x = rnd.uniform(x0, x1)
        t = (x - x0) / w
        c = light if (0.2 < t < 0.34 or 0.82 < t < 0.9) else (dark if (0.55 < t < 0.7 or t > 0.94 or t < 0.06) else base)
        st.append(f'<path d="M {x:.1f} -1000 L {x + rnd.uniform(-1.5, 1.5):.1f} 1000" stroke="{c}" stroke-width="{rnd.uniform(0.8, 2.6):.1f}" opacity="{rnd.uniform(0.08, 0.25):.2f}"/>')
    hx = x0 + w * 0.27
    st.append(f'<path d="M {hx:.1f} -1000 L {hx:.1f} 1000" stroke="#FFFFFF" stroke-width="{max(1.2, w * 0.025):.1f}" opacity="0.55"/>')
    st.append(f'<rect x="{x0 + w * 0.88:.1f}" y="-1000" width="{w * 0.12:.1f}" height="2000" fill="#E8B880" opacity="0.12"/>')
    return f'<path d="{d}" fill="{g}"/><g {cid}>{"".join(st)}</g>'


def steel_bowl(D, cx, rim_y, rx, h, seed, fill=None, ry=None, pal=STEEL, inkw=1.6):
    """Katori: a stainless steel bowl in 3/4 view; `fill` = (pal, kind) painted inside the rim."""
    ry = ry or rx * 0.32
    out = [cast(D, cx + rx * 0.12, rim_y + h + 2, rx * 0.95, ry * 0.5, strength=0.4, seed=seed)]
    body = ell_pts(cx, rim_y, rx, ry, 0, 180, 18) + [(cx - rx * 0.78, rim_y + h * 0.75), (cx - rx * 0.5, rim_y + h), (cx + rx * 0.5, rim_y + h), (cx + rx * 0.78, rim_y + h * 0.75)][::-1][::-1]
    body = [(cx + rx, rim_y)] + [(cx + rx * 0.86, rim_y + h * 0.6), (cx + rx * 0.55, rim_y + h), (cx - rx * 0.55, rim_y + h), (cx - rx * 0.86, rim_y + h * 0.6)] + [(cx - rx, rim_y)]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{pal[1]}"/>')
    out.append(metal(D, d, cx - rx, cx + rx, pal))
    out.append(ink(d, INK, inkw, seed, 1, 0.6))
    rim = ellipse_d(cx, rim_y, rx, ry)
    out.append(f'<path d="{rim}" fill="{pal[2]}"/>')
    inner = ellipse_d(cx, rim_y + 1, rx * 0.93, ry * 0.86)
    g = D.lin([(0, pal[2], 1), (0.5, pal[1], 1), (1, pal[0], 1)], 0, 0, 0, 1)
    out.append(f'<path d="{inner}" fill="{g}"/>')
    if fill:
        out.append(fill)
    out.append(ink(rim, INK, inkw * 0.8, seed + 1, 1, 0.55))
    out.append(taper([(cx - rx * 0.62, rim_y + h * 0.25), (cx - rx * 0.56, rim_y + h * 0.6)], 3, 1, "#FFFFFF", 0.9))
    return "".join(out)


def marigold(D, cx, cy, r, seed, pal=SAFFRON, tilt=1.0, inkw=0.0):
    """A genda (marigold) head: ruffled rings of little petal dabs, darker at the heart."""
    rnd = random.Random(seed)
    light, base, dark = pal
    out = [f'<path d="{blob(cx, cy + r * 0.12, r * 1.02, r * 0.98 * tilt, seed, 0.12, 16)}" fill="{dark}"/>']
    rings = ((0.86, 18, base, 0.34), (0.62, 13, mix(base, light, 0.35), 0.32), (0.38, 9, light, 0.3), (0.14, 4, mix(light, "#FFFFFF", 0.3), 0.24))
    if r < 14:
        rings = ((0.8, 9, base, 0.44), (0.45, 6, mix(base, light, 0.4), 0.4), (0.12, 2, light, 0.32))
    for ring, (rr, cnt, col, sz) in enumerate(rings):
        for i in range(cnt):
            a = 2 * math.pi * i / cnt + rnd.uniform(-0.2, 0.2) + ring * 0.4
            px, py = cx + math.cos(a) * r * rr, cy + math.sin(a) * r * rr * tilt
            c = col if rnd.random() < 0.7 else rnd.choice([dark, light, base])
            out.append(f'<path d="{blob(px, py, r * sz, r * sz * 0.8, rnd.randint(0, 9999), 0.3, 8, math.degrees(a))}" fill="{c}"/>')
            if r >= 14:
                out.append(f'<path d="M {px - math.cos(a) * r * sz * 0.6:.1f} {py - math.sin(a) * r * sz * 0.5 * tilt:.1f} l {math.cos(a) * r * sz * 0.9:.1f} {math.sin(a) * r * sz * 0.9 * tilt:.1f}" stroke="{dark}" stroke-width="{max(0.6, r * 0.04):.1f}" opacity="0.35"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.35 * tilt, r * 0.3, r * 0.18, seed + 5, 0.2, 8)}" fill="#FFFFFF" opacity="0.25"/>')
    if inkw:
        out.append(ink(blob(cx, cy, r * 1.0, r * 0.96 * tilt, seed + 3, 0.12, 16), INK, inkw, seed, 1, 0.4))
    return "".join(out)


def garland(D, pts, r, seed, pals=(SAFFRON, HALDI), leaves=True, every=1.0, jasmine=False):
    """String of marigolds along a polyline (centre points spaced ~1.5 r apart)."""
    cp = catmull(pts, 12)
    # resample along the curve
    acc, out_pts = 0.0, [cp[0]]
    step = r * 1.45 * every
    for a, b in zip(cp, cp[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        acc += seg
        while acc >= step:
            acc -= step
            t = 1 - acc / seg if seg else 0
            out_pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    out = [pline(pts, "#6A4A2A", 1.6, seed, 0.8, 1)]
    rnd = random.Random(seed)
    for i, (x, y) in enumerate(out_pts):
        if leaves and i % 3 == 1:
            a = rnd.uniform(0, 360)
            out.append(leaf_lite(D, x, y, r * 1.5, r * 0.45, a, LEAF, seed + i, vein=False, inkw=0.8))
        if jasmine and i % 4 == 2:
            for k in range(3):
                out.append(f'<path d="{blob(x + rnd.uniform(-r, r) * 0.6, y + rnd.uniform(-r, r) * 0.6, r * 0.36, r * 0.3, seed + i * 9 + k, 0.2, 8)}" fill="#FFFDF0"/>')
            continue
        out.append(marigold(D, x, y, r * rnd.uniform(0.9, 1.08), seed + i * 7, pals[i % len(pals)]))
    return "".join(out)


def diya(D, cx, cy, s, seed, lit=True, pal=CLAY, painted_rim=True, glow=True, flame_h=1.0):
    """Clay oil lamp (diya): shallow bowl pinched to a spout at the right, a cotton wick and a flame with a halo."""
    out = []
    if lit and glow:
        out.append(soft_glow(D, cx + s * 0.55, cy - s * 0.55, s * 2.6, "#FFB040", 0.55))
        out.append(soft_glow(D, cx + s * 0.55, cy - s * 0.6, s * 1.1, "#FFE6A0", 0.6))
    out.append(cast(D, cx, cy + s * 0.38, s * 1.1, s * 0.16, strength=0.45, seed=seed))
    body = [(cx - s, cy - s * 0.12), (cx - s * 0.85, cy + s * 0.22), (cx - s * 0.4, cy + s * 0.4), (cx + s * 0.2, cy + s * 0.38),
            (cx + s * 0.7, cy + s * 0.18), (cx + s * 1.12, cy - s * 0.22), (cx + s * 0.6, cy - s * 0.14), (cx, cy - s * 0.1)]
    out.append(painted(D, body, pal, seed, sdir=(0.4, 1), sk=0.22, angle=0, n=10, inkw=max(1, s * 0.035), hi=0.35))
    # the open top: an oil pool inside the rim
    top = [(cx - s, cy - s * 0.12), (cx - s * 0.5, cy - s * 0.32), (cx + s * 0.3, cy - s * 0.32), (cx + s * 0.8, cy - s * 0.26), (cx + s * 1.12, cy - s * 0.22),
           (cx + s * 0.6, cy - s * 0.1), (cx, cy - s * 0.04), (cx - s * 0.6, cy - s * 0.04)]
    out.append(f'<path d="{smooth_closed(top)}" fill="{pal[2]}"/>')
    out.append(f'<path d="{smooth_closed(shift([(x * 0.86 + cx * 0.14, y) for x, y in top], 0, 1.5))}" fill="#C88A2A" opacity="0.85"/>')
    if painted_rim:
        out.append(pline([(cx - s * 0.9, cy + s * 0.02), (cx - s * 0.3, cy + s * 0.16), (cx + s * 0.4, cy + s * 0.12), (cx + s * 0.9, cy - s * 0.08)], "#FFE6B0", max(1.2, s * 0.05), seed + 3, 0.8, 1))
        rnd = random.Random(seed)
        for k in range(6):
            t = (k + 0.5) / 6
            x = cx - s * 0.85 + s * 1.7 * t
            y = cy + s * 0.2 - s * 0.06 + math.sin(t * 3.1) * s * 0.06
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.2, s * 0.045):.1f}" fill="{rnd.choice(["#FFFFFF", "#F6C21C", "#D6342A"])}" opacity="0.9"/>')
    out.append(ink(smooth_closed(top), INK, max(1, s * 0.03), seed + 4, 1, 0.5))
    if lit:
        fx, fy = cx + s * 0.86, cy - s * 0.26
        out.append(taper([(fx - s * 0.2, fy + s * 0.04), (fx, fy)], s * 0.08, s * 0.05, "#F4EAD6"))
        fh = s * 0.95 * flame_h
        fl = [(fx, fy - fh), (fx + s * 0.16, fy - fh * 0.45), (fx + s * 0.13, fy - fh * 0.1), (fx, fy + s * 0.02), (fx - s * 0.13, fy - fh * 0.1), (fx - s * 0.15, fy - fh * 0.45)]
        out.append(f'<path d="{smooth_closed(fl)}" fill="#FF9A1E"/>')
        fl2 = [(fx, fy - fh * 0.78), (fx + s * 0.09, fy - fh * 0.38), (fx + s * 0.07, fy - fh * 0.08), (fx, fy - s * 0.02), (fx - s * 0.07, fy - fh * 0.08), (fx - s * 0.08, fy - fh * 0.38)]
        out.append(f'<path d="{smooth_closed(fl2)}" fill="#FFE27A"/>')
        out.append(f'<path d="{blob(fx, fy - fh * 0.12, s * 0.035, s * 0.07, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def mango(D, cx, cy, r, ang, seed, pal=MANGO, blush=True, leaf=False, light=(-0.6, -0.8)):
    """Alphonso mango: a plump oblique oval with a little beak, golden skin flushed orange toward the stem end,
    a hint of green at the stem. ang = direction from centre to the stem end (degrees)."""
    pts = []
    for i in range(26):
        a = 2 * math.pi * i / 26
        x = math.cos(a) * r * 1.18
        y = math.sin(a) * r * 0.86 * (1 + 0.1 * math.cos(a))
        if math.sin(a) > 0 and math.cos(a) < 0:        # the beak, low on the far end
            k = max(0, math.sin(a) * -math.cos(a)) * 2
            x -= k * r * 0.1
            y += k * r * 0.06
        pts.append((x, y))
    pts = rot([(cx + x, cy + y) for x, y in pts], cx, cy, ang)
    out = [painted(D, pts, ("#FFE680", "#F6B82A", "#C2660A"), seed, sdir=(-light[0], -light[1]), sk=0.2, angle=ang - 70, n=int(r * 0.9) + 8,
                   cols=["#FFE98A", "#E8861A", "#FFD45A", "#F29A2A"], inkw=max(1.2, r * 0.04), hi=0.5, hik=0.1, curve=0.4)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    sa = math.radians(ang)
    sx, sy = cx + math.cos(sa) * r * 1.12, cy + math.sin(sa) * r * 1.12
    if blush:
        inner.append(f'<path d="{blob(cx + math.cos(sa) * r * 0.55, cy + math.sin(sa) * r * 0.55, r * 0.75, r * 0.6, seed + 3, 0.2, 12)}" fill="#E8501E" opacity="0.32"/>')
        inner.append(f'<path d="{blob(cx + math.cos(sa) * r * 0.7, cy + math.sin(sa) * r * 0.7, r * 0.42, r * 0.36, seed + 4, 0.2, 12)}" fill="#D8361A" opacity="0.22"/>')
    inner.append(f'<path d="{blob(sx, sy, r * 0.28, r * 0.24, seed + 2, 0.2, 10)}" fill="#8AA83A" opacity="0.4"/>')
    rnd = random.Random(seed)
    for _ in range(int(r * 0.4)):
        inner.append(f'<circle cx="{cx + rnd.uniform(-r, r):.1f}" cy="{cy + rnd.uniform(-r, r) * 0.8:.1f}" r="{rnd.uniform(0.5, 1.1):.1f}" fill="#8A5A1A" opacity="0.3"/>')
    inner.append(f'<path d="{blob(cx - r * 0.42, cy - r * 0.4, r * 0.34, r * 0.13, seed + 5, 0.2, 10, -20)}" fill="#FFFFFF" opacity="0.55"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{blob(sx, sy, r * 0.09, r * 0.07, seed + 6, 0.2, 8)}" fill="#5A4020"/>')
    out.append(taper([(sx, sy), (sx + math.cos(sa - 0.5) * r * 0.22, sy + math.sin(sa - 0.5) * r * 0.22)], max(2.5, r * 0.07), max(1.5, r * 0.045), "#5A4020"))
    if leaf:
        lx, ly = sx + math.cos(sa - 0.5) * r * 0.2, sy + math.sin(sa - 0.5) * r * 0.2
        out.append(leaf_simple(D, lx, ly, r * 1.7, r * 0.34, ang - 50, ("#7ABA5A", "#2E7A34", "#124A1E"), seed + 9, inkw=1.1))
    return "".join(out)


def jasmine(D, x, y, r, seed):
    """A small mogra bud-and-bloom: five soft white petals, a creamy eye."""
    rnd = random.Random(seed)
    out = []
    a0 = rnd.uniform(0, 72)
    for k in range(5):
        a = math.radians(a0 + k * 72)
        out.append(f'<path d="{blob(x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.5, r * 0.5, r * 0.34, seed + k, 0.15, 8, math.degrees(a))}" fill="#FFFDF4" stroke="#C8C0A8" stroke-width="0.8"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.22:.1f}" fill="#F2E2A0"/>')
    return "".join(out)


def paisley_pts(cx, cy, s, ang=0, n=30):
    """Paisley (keri / mango motif) outline: round body tapering to a curled tip."""
    pts = []
    for i in range(n):
        t = i / n * 2 * math.pi
        r = 1 - 0.2 * math.cos(t)
        x = math.cos(t) * 0.55 * r
        y = math.sin(t) * 0.5 * r
        pts.append((x, y))
    # pull the top-right into a tip curling to the left
    out = []
    for x, y in pts:
        k = max(0, -y) * max(0, x + 0.2)
        out.append((x - k * 1.6, y - k * 1.9))
    return rot([(cx + x * s, cy + y * s) for x, y in out], cx, cy, ang)


def leaf_shadows(D, seed, box, col="#3A1A08", n=40, op=(0.06, 0.13), size=(16, 34)):
    """Dappled leaf shadows thrown across a sunlit wall."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        s = rnd.uniform(*size)
        out.append(f'<path d="{blob(x, y, s, s * 0.42, rnd.randint(0, 9999), 0.2, 10, rnd.uniform(-60, 60))}" fill="{col}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def sub(x, y, s, fill, font=JOS, size=19, ls=5, line_w=24, gap=12, line=None, seed=3, max_w=None):
    """ruled() subtitle that never prints below 17 px: tightens letter-spacing, then the side rules, before shrinking."""
    for lw, gp in ((line_w, gap), (min(line_w, 16), min(gap, 10)), (10, 8)):
        for l2 in range(ls, 1, -1):
            room = 480 - 2 * (gp + lw)
            fs = fit_size(s, font, size, room, l2)
            if fs >= 17 or (lw == 10 and l2 == 2):
                return ruled(x, y, s, fill, font=font, size=fs, ls=l2, line_w=lw, gap=gp, line=line, seed=seed, max_w=room)
    return ruled(x, y, s, fill, font=font, size=size, ls=ls, line_w=line_w, gap=gap, line=line, seed=seed, max_w=max_w or 380)


# ================================================================ 1. chai? — cutting chai at the stall, in the wire carrier
def cutting_glass(D, cx, base, w, h, seed, fill=0.78, tea="#C8884A", foam="#E8C8A0", tilt=0.22):
    """Small fluted glass of cutting chai: wider at the top, vertical facets, milky tea, a pale skin of froth."""
    top = base - h
    rx_t, rx_b = w / 2, w * 0.36
    ry_t, ry_b = w * tilt / 2, w * 0.36 * tilt
    out = [cast(D, cx + w * 0.15, base + 2, w * 0.6, w * 0.1, strength=0.35, seed=seed)]
    body = [(cx - rx_t, top)] + [(cx - rx_b, base)] + ell_pts(cx, base, rx_b, ry_b, 180, 0, 10)[1:-1][::-1][::-1] + [(cx + rx_b, base), (cx + rx_t, top)]
    body = [(cx - rx_t, top), (cx - rx_b, base)] + ell_pts(cx, base, rx_b, ry_b, 180, 0, 10)[::-1][::-1] + [(cx + rx_b, base), (cx + rx_t, top)]
    body = [(cx - rx_t, top), (cx - rx_b, base)] + [(cx + rx_b * math.cos(math.radians(a)), base + ry_b * math.sin(math.radians(a))) for a in range(170, 0, -20)] + [(cx + rx_b, base), (cx + rx_t, top)]
    d = pd(body)
    out.append(f'<path d="{d}" fill="#F4ECE0" opacity="0.55"/>')
    # tea inside
    ty = base - h * fill
    tr = rx_b + (rx_t - rx_b) * fill
    tea_d = pd([(cx - tr, ty), (cx - rx_b + 1.5, base - 1)] + [(cx + (rx_b - 1.5) * math.cos(math.radians(a)), base - 1 + ry_b * math.sin(math.radians(a))) for a in range(170, 0, -20)] + [(cx + rx_b - 1.5, base - 1), (cx + tr, ty)])
    out.append(f'<path d="{tea_d}" fill="{tea}"/>')
    g = D.lin([(0, "#5A2A0A", 0.45), (0.35, tea, 0), (0.7, "#FFE0B0", 0.25), (1, "#5A2A0A", 0.5)], cx - tr, 0, cx + tr, 0, "userSpaceOnUse")
    out.append(f'<path d="{tea_d}" fill="{g}"/>')
    out.append(f'<path d="{ellipse_d(cx, ty, tr, tr * tilt)}" fill="{foam}"/>')
    out.append(f'<path d="{blob(cx - tr * 0.2, ty - 0.5, tr * 0.5, tr * tilt * 0.4, seed, 0.2, 10)}" fill="#FFF2DC" opacity="0.7"/>')
    # facets
    for k in range(-3, 4):
        u = k / 3.6
        out.append(f'<path d="M {cx + rx_t * u:.1f} {top + 3:.1f} L {cx + rx_b * u:.1f} {base - 1:.1f}" stroke="#FFFFFF" stroke-width="{max(1, w * 0.035):.1f}" opacity="{0.55 if k < 0 else 0.3:.2f}"/>')
        out.append(f'<path d="M {cx + rx_t * u + w * 0.05:.1f} {top + 3:.1f} L {cx + rx_b * u + w * 0.035:.1f} {base - 1:.1f}" stroke="#6A4020" stroke-width="{max(0.8, w * 0.02):.1f}" opacity="0.18"/>')
    out.append(f'<path d="{pd([(cx - rx_t, top), (cx - rx_b, base), (cx - rx_b + w * 0.07, base), (cx - rx_t + w * 0.1, top)])}" fill="#FFFFFF" opacity="0.35"/>')
    out.append(ink(d, "#6A5040", max(1.1, w * 0.035), seed, 1, 0.7))
    out.append(f'<path d="{ellipse_d(cx, top, rx_t, ry_t)}" fill="none" stroke="#FFFFFF" stroke-width="{max(1.2, w * 0.04):.1f}" opacity="0.8"/>')
    out.append(ink(ellipse_d(cx, top, rx_t, ry_t), "#6A5040", max(1, w * 0.025), seed + 1, 1, 0.6))
    return "".join(out)


def glass_jar(D, cx, base, w, h, seed, fill_kind="rusk"):
    """A tea-stall glass jar with a round lid, its biscuits seen through the glass."""
    rnd = random.Random(seed)
    top = base - h
    body = pk.dens2([(cx - w / 2, base), (cx + w / 2, base), (cx + w / 2, top + h * 0.12), (cx + w * 0.38, top), (cx - w * 0.38, top), (cx - w / 2, top + h * 0.12)], 8)
    d = smooth_closed(body)
    out = [f'<path d="{blob(cx + w * 0.2, base + 3, w * 0.6, 5, seed, 0.1, 12)}" fill="#1A0E08" opacity="0.4"/>']
    inner = []
    if fill_kind == "rusk":
        for k in range(10):
            y = base - 8 - k * (h * 0.075)
            inner.append(f'<path d="{blob(cx + rnd.uniform(-6, 6), y, w * 0.42, h * 0.04, rnd.randint(0, 999), 0.1, 12, rnd.uniform(-8, 8))}" fill="{rnd.choice(["#D8984A", "#E8B060", "#C8803A"])}"/>')
            inner.append(f'<path d="M {cx - w * 0.38:.1f} {y - h * 0.02:.1f} L {cx + w * 0.38:.1f} {y - h * 0.025:.1f}" stroke="#F8D898" stroke-width="1.4" opacity="0.7"/>')
    else:
        for k in range(16):
            x, y = cx + rnd.uniform(-w * 0.35, w * 0.35), base - 10 - rnd.uniform(0, h * 0.7)
            inner.append(f'<path d="{blob(x, y, w * 0.16, w * 0.08, rnd.randint(0, 999), 0.2, 10, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2D08A", "#E8B868", "#FFE6A8"])}"/>')
    out.append(f'<path d="{d}" fill="#E8E0C8" opacity="0.35"/>')
    out.append(clipped(D, d, inner + [f'<rect x="{cx - w}" y="{top}" width="{2 * w}" height="{h}" fill="{D.lin([(0, "#FFFFFF", 0.35), (0.3, "#FFFFFF", 0), (0.8, "#2A3A3A", 0.15), (1, "#FFFFFF", 0.3)], 0, 0, 1, 0)}"/>']))
    out.append(taper([(cx - w * 0.36, top + h * 0.16), (cx - w * 0.38, base - h * 0.1)], max(2, w * 0.06), max(1, w * 0.03), "#FFFFFF", 0.7))
    out.append(f'<path d="{d}" fill="none" stroke="#5A6A60" stroke-width="1.4" opacity="0.7"/>')
    lid = pk.dens2([(cx - w * 0.42, top + 2), (cx + w * 0.42, top + 2), (cx + w * 0.4, top - h * 0.1), (cx - w * 0.4, top - h * 0.1)], 6)
    out.append(modelled(D, lid, ("#F28A6A", "#C8402A", "#6A1A0A"), seed + 1, light=(-0.6, -0.8), angle=0, n=8, inkw=1.0, hi=0.4))
    return "".join(out)


@design("chai")
def chai():
    D = Doc2("in-ch")
    art = []
    # dawn on the street behind the stall: warm mist, soft buildings, a street lamp still lit
    art.append(sky(D, [(0, "#E8C49A"), (0.45, "#F2D2A8"), (1, "#E0A878")], 11, 600, ["#FFE6C0", "#D8A070", "#FFF0D8"], 100, angle=-6, sop=(0.05, 0.14)))
    art.append(soft_glow(D, 120, 250, 260, "#FFF2D0", 0.8))
    rnd0 = random.Random(9)
    for k, (x, w, h) in enumerate(((-20, 130, 200), (100, 90, 170), (180, 120, 230), (300, 100, 180), (390, 140, 220), (520, 110, 170))):
        c = mix(["#B88A7A", "#A88078", "#C49480", "#9A7A7A", "#B4887A", "#A07A70"][k], "#F2D2A8", 0.62)
        bp = jitter(pk.dens2([(x, 430 - h), (x + w, 430 - h + rnd0.uniform(-6, 6)), (x + w, 440), (x, 440)], 12), k, 1.2)
        art.append(f'<path d="{smooth_closed(bp)}" fill="{c}"/>')
        art.append(strokes(D.nid(), smooth_closed(bp), (x, 430 - h, x + w, 440), [lt(c, 0.15), dk(c, 0.1)], 10 + k, n=12, angle=-90, length=(20, 60), width=(3, 8), opacity=(0.15, 0.3)))
        for j in range(2):
            for i in range(2):
                if rnd0.random() < 0.6:
                    wx, wy = x + 16 + i * (w * 0.45), 430 - h + 30 + j * 60
                    art.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{w * 0.18:.1f}" height="20" fill="{mix("#7A5A5A", "#F2D2A8", 0.6)}" opacity="0.8"/>')

    art.append(f'<path d="M 470 440 L 474 230" stroke="{mix("#5A4A4A", "#F2D2A8", 0.4)}" stroke-width="4"/>')
    art.append(soft_glow(D, 478, 232, 40, "#FFE8A0", 0.8))
    art.append(haze_band(D, 400, 140, "#F8E2C0", 0.7))
    # the stall's own shadowed back corner behind the stove, a tin awning edge above
    bk = jitter(pk.dens2([(372, 232), (620, 222), (620, 450), (372, 450)], 12), 9, 1.0)
    art.append(f'<path d="{smooth_closed(bk)}" fill="{D.lin([(0, "#4A2E22"), (1, "#2A1810")])}"/>')
    art.append(strokes(D.nid(), smooth_closed(bk), (372, 222, 620, 450), ["#5A3A2A", "#1A0E08", "#6A4632"], 8, n=40, angle=-90, length=(20, 70), width=(3, 8), opacity=(0.2, 0.45)))
    art.append(f'<path d="{pdl([(360, 214), (620, 200), (620, 228), (360, 240)])}" fill="#8A9098"/>')
    for k in range(9):
        x = 368 + k * 30
        art.append(f'<path d="M {x} {238 - k * 1.6:.1f} L {x} {212 - k * 1.6:.1f}" stroke="#5A6068" stroke-width="2" opacity="0.6"/>')
    # the stall's counter: old planks, a strip of tin at the edge
    art.append(wood_planks(D, 448, 620, 14, WOOD, 3))
    art.append(f'<path d="{pdl([(-10, 444), (610, 444), (610, 458), (-10, 458)])}" fill="#C8B8A0"/>')
    art.append(f'<path d="M -10 458 L 610 458" stroke="#2A1408" stroke-width="2" opacity="0.5"/>')
    art.append(pk.dabs(12, (0, 470, 600, 600), ["#6A3A1A", "#C88A4A"], 50, (2, 6), (0.15, 0.35)))
    # jars of rusk and khari at the back left
    art.append(glass_jar(D, 70, 452, 74, 112, 13, "rusk"))
    art.append(glass_jar(D, 150, 452, 62, 92, 14, "khari"))
    # the stove at right: a dented aluminium patila of chai at a rolling boil, froth climbing the sides
    sx, sb = 470, 452
    stv = pk.dens2([(sx - 80, sb - 2), (sx + 80, sb - 2), (sx + 70, sb - 40), (sx - 70, sb - 40)], 8)
    art.append(modelled(D, stv, ("#6A6E76", "#2E3036", "#0C0D10"), 15, light=(-0.6, -0.8), angle=0, n=16, inkw=1.2, hi=0.3))
    art.append(soft_glow(D, sx, sb - 44, 70, "#5AA0FF", 0.45))
    for k in range(10):
        x = sx - 50 + k * 11
        art.append(f'<path d="M {x - 3:.1f} {sb - 40:.1f} Q {x - 1:.1f} {sb - 48:.1f} {x:.1f} {sb - 54:.1f} Q {x + 2:.1f} {sb - 47:.1f} {x + 3:.1f} {sb - 40:.1f} Z" fill="#4A8AF0" opacity="0.85"/>')
    pb, _ = pk.metal_cyl(D, sx, sb - 140, sb - 46, 76, 18, 16, pal=("#F2F4F6", "#AEB4BC", "#4E545C"), env=("#F8E8D0", "#6A9AF0"), light=-1, gloss=0.55)
    art.append(pb)
    for k, (dx, dy) in enumerate(((-40, -100), (20, -80), (50, -116))):
        art.append(f'<path d="{blob(sx + dx, sb + dy, 7, 4, 17 + k, 0.2, 8)}" fill="#8A929C" opacity="0.6"/>')
    rim = blob(sx, sb - 140, 76, 18, 18, 0.004, 30)
    art.append(f'<path d="{rim}" fill="#C8CED6"/>')
    tea = blob(sx, sb - 138, 70, 15, 19, 0.01, 30)
    art.append(f'<path d="{tea}" fill="{D.rad([(0, "#F2D2A0"), (0.6, "#D8A060"), (1, "#8A5428")], 0.45, 0.45, 0.6)}"/>')
    froth = []
    rnd = random.Random(20)
    for k in range(40):
        a_ = rnd.uniform(0, 6.28)
        r_ = math.sqrt(rnd.random()) * 0.9
        froth.append(f'<circle cx="{sx + math.cos(a_) * 66 * r_:.1f}" cy="{sb - 138 + math.sin(a_) * 13 * r_:.1f}" r="{rnd.uniform(1.5, 5):.1f}" fill="#FFF4E0" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    art.append(clipped(D, tea, froth))
    art.append(f'<path d="{smooth_closed([(sx - 74, sb - 142), (sx - 60, sb - 160), (sx - 30, sb - 152), (sx, sb - 166), (sx + 30, sb - 152), (sx + 64, sb - 160), (sx + 76, sb - 140), (sx, sb - 128)])}" fill="#FBF0DC" opacity="0.9"/>')
    art.append(pk.metal_ellipse(D, sx, sb - 140, 76, 18, 21, rim_w=3, inner_pal=None) if False else "")
    art.append(f'<path d="{rim}" fill="none" stroke="#5A6068" stroke-width="2" opacity="0.6"/>')
    # steam rolling off the boil
    art.append(pk.steam_plume(D, [(sx + 8, sb - 164), (sx - 12, sb - 204), (sx + 18, sb - 244), (sx - 22, sb - 284), (sx - 2, sb - 314)], 40, 80, 21, "#9A8A80", 0.35, puffs=False))
    art.append(pk.steam_plume(D, [(sx, sb - 170), (sx - 20, sb - 210), (sx + 10, sb - 250), (sx - 30, sb - 290), (sx - 10, sb - 320)], 40, 80, 22, "#FFFFFF", 0.8))
    # tongs (pakkad) resting on the counter, a strainer, a knob of ginger, cardamom
    art.append(taper([(340, 520), (420, 500)], 5, 4, "#7A8088"))
    art.append(taper([(340, 528), (424, 512)], 5, 4, "#9AA0A8"))
    art.append(f'<path d="{blob(552, 520, 22, 18, 23, 0.04, 14)}" fill="#3A3A40"/><path d="{blob(552, 520, 18, 14, 24, 0.04, 14)}" fill="#C8B490" opacity="0.8"/>')
    art.append(taper([(574, 520), (612, 512)], 4, 3, "#2A2A30"))
    gn = [(372, 566), (392, 556), (414, 562), (428, 554), (440, 566), (420, 578), (392, 578)]
    art.append(modelled(D, gn, ("#E8C890", "#C89A5A", "#6A4A20"), 25, light=(-0.6, -0.7), angle=0, n=8, inkw=1.0, hi=0.4))
    for k, (x, y) in enumerate(((330, 572), (346, 580), (318, 584))):
        art.append(cardamom(D, x, y, 9, 20 * k, 26 + k))
    # the wire carrier with six cutting glasses, the hero, front and centre
    cx = 250
    gw, gh = 70, 92
    art.append(f'<path d="{blob(cx + 20, 556, 170, 14, 27, 0.1, 16)}" fill="#1A0E08" opacity="0.45"/>')
    hb = 512
    for k, x in enumerate((cx - 80, cx, cx + 80)):
        art.append(cutting_glass(D, x, hb, gw * 0.92, gh * 0.92, 30 + k, fill=0.8))
    c = "#7E8690"
    top = 330
    for sx_ in (-8, 8):
        art.append(taper([(cx + sx_, 548), (cx + sx_, top + 26)], 4.6, 4.6, c))
        art.append(taper([(cx + sx_ - 1.5, 548), (cx + sx_ - 1.5, top + 26)], 1.4, 1.4, "#F4F6F8", 0.8))
    loop = [(cx - 8, top + 28), (cx - 30, top + 10), (cx - 22, top - 12), (cx, top - 18), (cx + 22, top - 12), (cx + 30, top + 10), (cx + 8, top + 28)]
    art.append(ink(smooth_open(loop), c, 5.4, 34, 1, 1))
    art.append(ink(smooth_open(loop[:4]), "#F4F6F8", 1.8, 35, 1, 0.9))
    for k, x in enumerate((cx - 120, cx - 40, cx + 40, cx + 120)):
        art.append(cutting_glass(D, x, 556, gw, gh, 40 + k, fill=0.82 if k != 2 else 0.62))
    rail_y = 556 - gh * 0.44
    art.append(ink(smooth_open([(cx - 166, rail_y), (cx, rail_y + 7), (cx + 166, rail_y)]), c, 3.8, 37, 1, 1))
    art.append(ink(smooth_open([(cx - 166, rail_y - 1.4), (cx, rail_y + 5.6), (cx + 166, rail_y - 1.4)]), "#F4F6F8", 1.3, 38, 1, 0.9))
    art.append(f'<path d="{pd([(cx - 170, 550), (cx + 170, 550), (cx + 162, 560), (cx - 162, 560)])}" fill="none" stroke="{c}" stroke-width="3.6" stroke-linejoin="round"/>')
    art.append(pk.steam_plume(D, [(cx - 120, 452), (cx - 130, 420), (cx - 110, 390)], 12, 22, 39, "#FFFFFF", 0.55, puffs=False))
    art.append(pk.steam_plume(D, [(cx + 40, 452), (cx + 50, 420), (cx + 30, 390)], 12, 22, 40, "#FFFFFF", 0.5, puffs=False))
    art.append(glaze(D, [(0, "#FFF0C8", 0.15), (0.6, "#FFF0C8", 0), (1, "#3A1A08", 0.25)]))
    art.append(vignette(D, "#2A1408", 0.32, 0.8))
    txt = [letters(D, 300, 152, "Chai?", SERIF_IT, 164, "#8A2A10", ["#B8401A", "#5A1406", "#D8602A"], 70, max_w=360,
                   shadow="#FFF0D0", soff=(0.02, 0.03), angle=-40, hi="#FFB880"),
           sub(300, 198, "THE ANSWER IS ALWAYS YES", "#4A1E08", font=JOS, size=19, ls=5, line_w=24, gap=12)]
    return finish_art(D, art, txt, 71, under="#E8C49A", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 2. masala dabba — the steel spice box, from above
def spice_mound(D, cx, cy, r, kind, seed):
    rnd = random.Random(seed)
    out = []
    pals = {"haldi": ("#FFE45A", "#F2B40E", "#B87A06"), "mirch": ("#F25A3A", "#C21E12", "#6A0A06"),
            "dhania": ("#D8C27A", "#A8904A", "#6A5A28"), "garam": ("#A8704A", "#6E3E22", "#3A1E0E"),
            "jeera": ("#C8A06A", "#8A6A3A", "#4A3418"), "rai": ("#5A4038", "#2A1A16", "#100806"),
            "methi": ("#F2C86A", "#C8902A", "#7A5410")}
    pal = pals[kind]
    if kind in ("haldi", "mirch", "dhania", "garam"):
        # soft powder heap with a spoon scoop mark and a dusty rim
        out.append(f'<path d="{ellipse_d(cx, cy, r, r)}" fill="{pal[1]}"/>')
        g = D.rad([(0, pal[0], 0.9), (0.55, pal[1], 0.2), (1, pal[2], 0.85)], 0.42, 0.4, 0.62)
        out.append(f'<path d="{ellipse_d(cx, cy, r, r)}" fill="{g}"/>')
        out.append(specks(seed, (cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8), [pal[0], pal[2], "#FFFFFF"], int(r * 1.6), (0.5, 1.4), (0.3, 0.8)))
        out.append(f'<path d="{blob(cx + r * 0.18, cy + r * 0.12, r * 0.34, r * 0.22, seed, 0.15, 10, 30)}" fill="{pal[2]}" opacity="0.4"/>')
        out.append(f'<path d="{blob(cx + r * 0.14, cy + r * 0.06, r * 0.3, r * 0.16, seed + 1, 0.15, 10, 30)}" fill="{pal[0]}" opacity="0.5"/>')
    else:
        out.append(f'<path d="{ellipse_d(cx, cy, r, r)}" fill="{pal[2]}"/>')
        n = {"jeera": int(r * 3.2), "rai": int(r * 6), "methi": int(r * 4)}[kind]
        items = []
        for _ in range(n):
            a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.94
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            lit = (x - cx) * -0.6 + (y - cy) * -0.8
            if kind == "jeera":
                ang = rnd.uniform(0, 180)
                L = r * 0.13
                c = pal[0] if lit > r * 0.2 else rnd.choice(pal)
                items.append(f'<path d="{blob(x, y, L, L * 0.32, rnd.randint(0, 9999), 0.1, 8, ang)}" fill="{c}"/>')
                items.append(f'<path d="M {x - math.cos(math.radians(ang)) * L * 0.7:.1f} {y - math.sin(math.radians(ang)) * L * 0.7:.1f} l {math.cos(math.radians(ang)) * L * 1.4:.1f} {math.sin(math.radians(ang)) * L * 1.4:.1f}" stroke="#3A2410" stroke-width="0.7" opacity="0.5"/>')
            elif kind == "rai":
                rr2 = r * 0.055
                items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr2:.1f}" fill="{rnd.choice(pal)}"/><circle cx="{x - rr2 * 0.35:.1f}" cy="{y - rr2 * 0.35:.1f}" r="{rr2 * 0.35:.1f}" fill="#B8A098" opacity="0.7"/>')
            else:
                s = r * 0.07
                items.append(f'<path d="{hg.org_rect(x - s, y - s * 0.7, s * 2, s * 1.4, rnd.randint(0, 999), 0.3, 6, 1)}" fill="{rnd.choice(pal)}" transform="rotate({rnd.uniform(0, 90):.0f} {x:.1f} {y:.1f})"/>')
        out.append(clipped(D, ellipse_d(cx, cy, r, r), items))
        g = D.rad([(0, "#FFFFFF", 0), (0.7, "#000000", 0), (1, "#000000", 0.45)])
        out.append(f'<path d="{ellipse_d(cx, cy, r, r)}" fill="{g}"/>')
    return "".join(out)


def katori_top(D, cx, cy, r, kind, seed):
    """A little steel katori seen from directly above: rolled rim catching the light, the inner wall in shade on
    the lit side (the light comes from the upper left), spice heaped inside, a cast shadow to the lower right."""
    out = [f'<path d="{blob(cx + 5, cy + 6, r + 7, r + 6, seed, 0.03, 20)}" fill="#0A080C" opacity="0.45"/>']
    rim = ellipse_d(cx, cy, r + 6, r + 6)
    g = D.lin([(0, "#FFFFFF"), (0.35, "#C8D0D8"), (0.7, "#7A848E"), (1, "#3E4650")], 0, 0, 1, 1)
    out.append(f'<path d="{rim}" fill="{g}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, r + 1, r + 1)}" fill="{D.lin([(0, "#3E4650"), (0.55, "#7A848E"), (1, "#D8DEE4")], 0, 0, 1, 1)}"/>')
    out.append(spice_mound(D, cx, cy, r - 1, kind, seed))
    # the inner wall's shadow falling across the spice on the lit side
    out.append(clipped(D, ellipse_d(cx, cy, r - 1, r - 1), [f'<path d="{blob(cx - r * 0.25, cy - r * 0.25, r * 0.95, r * 0.95, seed + 3, 0.02, 20)} {blob(cx + r * 0.1, cy + r * 0.1, r * 1.0, r * 1.0, seed + 4, 0.02, 20)}" fill-rule="evenodd" fill="#1A1410" opacity="0.35"/>']))
    out.append(f'<path d="{rim}" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.5"/>')
    out.append(f'<path d="M {cx - r * 0.72:.1f} {cy - r * 0.88:.1f} A {r + 3:.1f} {r + 3:.1f} 0 0 1 {cx + r * 0.25:.1f} {cy - r - 3:.1f}" stroke="#FFFFFF" stroke-width="2.6" fill="none" opacity="0.95" stroke-linecap="round"/>')
    out.append(f'<path d="M {cx + r * 0.6:.1f} {cy + r * 0.92:.1f} A {r + 4:.1f} {r + 4:.1f} 0 0 0 {cx + r * 0.98:.1f} {cy + r * 0.3:.1f}" stroke="#E8B880" stroke-width="2" fill="none" opacity="0.5" stroke-linecap="round"/>')
    return "".join(out)


def dried_chilli(D, x, y, L, ang, seed, pal=SINDOOR):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    right, left = [], []
    for i in range(11):
        t = i / 10
        w = L * 0.11 * (math.sin(math.pi * min(1, t * 1.3 + 0.08)) ** 0.6) * (1 - 0.75 * t)
        bend = L * 0.12 * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, ("#E8503A", "#A8160E", "#5A0604"), seed, sdir=(nx, ny), sk=0.2, angle=ang, n=6, inkw=1.1, hi=0.35, hik=0.12)]
    out.append(taper([(x - ux * 2, y - uy * 2), (x - ux * L * 0.14 + nx * 3, y - uy * L * 0.14 + ny * 3)], L * 0.07, L * 0.04, "#5A6A2A"))
    out.append(taper([(x + ux * L * 0.15 + nx * L * 0.03, y + uy * L * 0.15 + ny * L * 0.03), (x + ux * L * 0.6 + nx * L * 0.05, y + uy * L * 0.6 + ny * L * 0.05)], L * 0.03, L * 0.01, "#FFB0A0", 0.6))
    return "".join(out)


def cardamom(D, x, y, s, ang, seed):
    return painted(D, blob_pts(x, y, s, s * 0.55, seed, 0.08, 12, rot=ang), ("#C8E09A", "#88A858", "#4A6A2A"), seed, sk=0.22, n=3, inkw=1, hi=0.45)


def star_anise(D, cx, cy, r, seed, ang=0):
    out = []
    for i in range(8):
        a = math.radians(ang + i * 45)
        tip = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        sd = (math.cos(a + 1.5) * r * 0.2, math.sin(a + 1.5) * r * 0.2)
        pts = [(cx + sd[0] * 0.4, cy + sd[1] * 0.4), (cx + math.cos(a) * r * 0.55 + sd[0], cy + math.sin(a) * r * 0.55 + sd[1]), tip,
               (cx + math.cos(a) * r * 0.55 - sd[0], cy + math.sin(a) * r * 0.55 - sd[1]), (cx - sd[0] * 0.4, cy - sd[1] * 0.4)]
        out.append(f'<path d="{smooth_closed(pts)}" fill="#7A3E1E"/>')
        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, r * 0.1, r * 0.07, seed + i, 0.1, 8)}" fill="#C88A3A"/>')
        out.append(ink(smooth_closed(pts), "#2A1008", 0.9, seed + i, 1, 0.6))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.14:.1f}" fill="#4A2010"/>')
    return "".join(out)


def cinnamon(D, x0, y0, x1, y1, w, seed):
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    pts = [(x0 + nx * w / 2, y0 + ny * w / 2), (x1 + nx * w / 2, y1 + ny * w / 2), (x1 - nx * w / 2, y1 - ny * w / 2), (x0 - nx * w / 2, y0 - ny * w / 2)]
    out = [painted(D, pts, ("#D8905A", "#A85A2A", "#5A2A0E"), seed, sdir=(nx, ny), sk=0.25, angle=math.degrees(a), n=10, inkw=1.2, hi=0.3)]
    out.append(f'<path d="{ellipse_d(x1, y1, w * 0.18, w / 2)}" fill="#6A3010" transform="rotate({math.degrees(a):.0f} {x1:.1f} {y1:.1f})"/>')
    out.append(f'<path d="M {x1:.1f} {y1:.1f} m {nx * w * 0.3:.1f} {ny * w * 0.3:.1f} q {-math.cos(a) * 3 - nx * 8:.1f} {-math.sin(a) * 3 - ny * 8:.1f} {-nx * w * 0.3:.1f} {-ny * w * 0.6:.1f}" stroke="#D8905A" stroke-width="1.4" fill="none" transform="rotate(0)"/>')
    return "".join(out)


def bay_leaf(D, x, y, L, ang, seed):
    return leaf_simple(D, x, y, L, L * 0.2, ang, ("#B8B07A", "#7E7A44", "#46441E"), seed, inkw=1.0)


@design("masala-dabba")
def masala_dabba():
    D = Doc2("in-md")
    # dark slate counter, light from the upper left
    out = [sky(D, [(0, "#3E3A40"), (1, "#1E1C22")], 101, 600, ["#4A4650", "#141218", "#5A5460", "#2A262E"], 220, angle=-30, sop=(0.08, 0.24))]
    out.append(blooms(103, ["#5A5660", "#0E0C12"], 10, (0, 0, 600, 600), (60, 140), (0.08, 0.18)))
    out.append(soft_glow(D, 170, 200, 460, "#FFE2B0", 0.3))
    out.append(specks(102, (0, 0, 600, 600), ["#6A6670", "#14121A", "#8A8278"], 220, (0.8, 2.2), (0.3, 0.7)))
    # an indigo dabu-print cotton cloth folded under one side of the tin
    cl = [(-40, 330), (300, 610), (-40, 640)]
    clp = smooth_closed(jitter(pk.dens2([(-40, 300), (340, 640), (-40, 640)], 14), 104, 1.2))
    out.append(f'<path d="{clp}" fill="#22305A"/>')
    pat = []
    rr = random.Random(105)
    for j in range(12):
        for i in range(12):
            x, y = -40 + i * 34 + (17 if j % 2 else 0), 300 + j * 30
            pat.append(f'<path d="{blob(x, y, 7, 5, i * 13 + j, 0.25, 8, 30)}" fill="#E8E2D2" opacity="0.75"/>')
            pat.append(f'<circle cx="{x + 17:.1f}" cy="{y + 12:.1f}" r="2" fill="#E8E2D2" opacity="0.7"/>')
    pat.append(strokes(D.nid(), clp, (-40, 300, 340, 640), ["#3A4A7A", "#121A38"], 106, n=60, angle=-45, length=(20, 60), width=(2, 6), opacity=(0.15, 0.35)))
    pat.append(f'<path d="M -40 300 L 340 640" stroke="#0A0E20" stroke-width="10" opacity="0.35"/>')
    out.append(clipped(D, clp, pat))
    out.append(f'<path d="{smooth_open([(-40, 302), (120, 446), (338, 640)])}" fill="none" stroke="#E8E2D2" stroke-width="2" opacity="0.5" stroke-dasharray="4 3"/>')
    cx, cy, R = 300, 368, 170
    # the lid, leaning off to the upper right (seen at a slight angle) — drawn first, under the box
    lx, ly = 470, 226
    out.append(f'<path d="{ellipse_d(lx + 10, ly + 12, 128, 60)}" fill="#0A080C" opacity="0.4" transform="rotate(-24 {lx} {ly})"/>')
    lid = ellipse_d(lx, ly, 128, 56)
    out.append(f'<g transform="rotate(-24 {lx} {ly})"><path d="{lid}" fill="{STEEL[1]}"/>{metal(D, lid, lx - 128, lx + 128, STEEL, 0.9)}'
               f'<path d="{ellipse_d(lx, ly, 108, 46)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>'
               f'<path d="{ellipse_d(lx, ly, 88, 37)}" fill="none" stroke="#6E7884" stroke-width="1.6" opacity="0.6"/>'
               f'{ink(lid, INK, 1.8, 103, 1, 0.6)}</g>')
    # the round tin
    out.append(f'<path d="{ellipse_d(cx + 12, cy + 16, R + 10, R + 10)}" fill="#0A080C" opacity="0.5"/>')
    tin = ellipse_d(cx, cy, R, R)
    out.append(f'<path d="{tin}" fill="#C8CED6"/>')
    g = D.lin([(0, "#FFFFFF", 1), (0.45, "#B8C0CA", 1), (1, "#5E6874", 1)], 0, 0, 1, 1)
    out.append(f'<path d="{tin}" fill="{g}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, R - 9, R - 9)}" fill="#7E8894"/>')
    g2 = D.lin([(0, "#4E5864", 1), (0.6, "#9AA2AC", 1), (1, "#D8DEE4", 1)], 0, 0, 1, 1)
    out.append(f'<path d="{ellipse_d(cx, cy, R - 12, R - 12)}" fill="{g2}"/>')
    out.append(f'<path d="M {cx - R * 0.78:.1f} {cy - R * 0.55:.1f} A {R - 3} {R - 3} 0 0 1 {cx + R * 0.1:.1f} {cy - R + 3:.1f}" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.85" stroke-linecap="round"/>')
    out.append(ink(tin, INK, 2.2, 104, 2, 0.7))
    # seven katoris: one in the middle, six around it
    kinds = ["haldi", "mirch", "jeera", "dhania", "garam", "methi"]
    r = 47
    for i, k in enumerate(kinds):
        a = math.radians(-90 + 60 * i + 8)
        out.append(katori_top(D, cx + math.cos(a) * 104, cy + math.sin(a) * 104, r, k, 110 + i))
    out.append(katori_top(D, cx, cy, r, "rai", 120))
    # a tiny steel spoon resting in the turmeric
    a = math.radians(-90 + 8)
    sx, sy = cx + math.cos(a) * 104, cy + math.sin(a) * 104
    out.append(taper([(sx + 8, sy + 2), (sx + 60, sy - 34), (sx + 96, sy - 60)], 5, 3.5, "#9AA2AC"))
    out.append(taper([(sx + 8, sy + 1), (sx + 60, sy - 35), (sx + 96, sy - 61)], 1.6, 1.0, "#FFFFFF", 0.9))
    out.append(f'<path d="{ellipse_d(sx + 2, sy + 6, 13, 9)}" fill="#F4C21A" transform="rotate(-35 {sx + 2} {sy + 6})"/>')
    out.append(f'<path d="{ellipse_d(sx + 2, sy + 6, 13, 9)}" fill="none" stroke="#6E7884" stroke-width="2" transform="rotate(-35 {sx + 2} {sy + 6})"/>')
    # whole spices scattered on the slate
    out.append(dried_chilli(D, 66, 470, 92, 18, 130))
    out.append(dried_chilli(D, 470, 560, 84, -164, 131))
    out.append(cinnamon(D, 56, 560, 150, 532, 16, 132))
    out.append(star_anise(D, 536, 470, 24, 133, 10))
    out.append(cardamom(D, 92, 404, 10, 30, 134))
    out.append(cardamom(D, 112, 418, 9, -10, 135))
    out.append(cardamom(D, 520, 524, 9, 60, 136))
    out.append(bay_leaf(D, 470, 380, 70, 70, 137))
    out.append(specks(138, (60, 380, 160, 600), ["#C21E12", "#F2B40E"], 16, (0.8, 1.8), (0.5, 0.9)))
    # lettering
    out.append(vignette(D, "#060408", 0.4, 0.8))
    txt = [letters(D, 236, 116, "masala dabba", SERIF_IT, 84, "#FFC24A", ["#FFD870", "#E89A1A", "#FFE6A0"], 140, max_w=400,
                   shadow="#0E0A10", soff=(0.02, 0.035), angle=-40, hi="#FFF0B0"),
           sub(236, 156, "NO RECIPE, JUST ANDAAZ", "#F2E6D0", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, out, txt, 141, under="#2A262E", edge=2.4, bristle=0.45, grain=0.2)


# ================================================================ 3. samosa — on a leaf plate, with both chutneys
def qcurve(p, q, bulge, n=8):
    """Points along a gently bowed edge p->q (bulge > 0 bows to the left of the direction of travel)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = dy / L, -dx / L
    c = ((p[0] + q[0]) / 2 + nx * bulge * L, (p[1] + q[1]) / 2 + ny * bulge * L)
    return [((1 - t) ** 2 * p[0] + 2 * (1 - t) * t * c[0] + t * t * q[0], (1 - t) ** 2 * p[1] + 2 * (1 - t) * t * c[1] + t * t * q[1])
            for t in (i / n for i in range(n))]


def samosa(D, cx, base, w, h, seed, turn=1):
    """A samosa standing on its base: two puffed faces of a cone meeting at a pinched front seam, blistered pastry."""
    rnd = random.Random(seed)
    A = (cx + turn * w * 0.05, base - h)
    M = (cx + turn * w * 0.1, base + h * 0.05)
    Lc, Rc = (cx - w * 0.5, base - h * 0.12), (cx + w * 0.5, base - h * 0.1)
    out = [cast(D, cx + 8, base + 6, w * 0.62, h * 0.09, strength=0.55, seed=seed)]
    left = qcurve(Lc, M, -0.1) + qcurve(M, A, -0.08) + qcurve(A, Lc, -0.15)
    right = qcurve(M, Rc, -0.1) + qcurve(Rc, A, -0.15) + qcurve(A, M, -0.08)
    lit, shd = (left, right) if turn > 0 else (right, left)
    for k, (pts, pal, sd) in enumerate(((lit, ("#FFE6A8", "#ECB45A", "#A8641A"), (0.7, 0.5)), (shd, ("#E8B060", "#C47E2C", "#6E3A0E"), (0.9, 0.2)))):
        out.append(painted(D, pts, pal, seed + k, sdir=sd, sk=0.2, angle=-60 - 30 * k, n=int(w * h / 110) + 12,
                           cols=["#FFF0C0", "#B8701E", "#F6C870", "#9A5410"], inkw=1.7, hi=0.4, hik=0.08, curve=0.45))
        x0, y0, x1, y1 = bbox(pts)
        bl = []
        for _ in range(int(w * h / 520)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            rr = rnd.uniform(1.8, 4.2)
            bl.append(f'<path d="{blob(x, y, rr, rr * 0.8, rnd.randint(0, 999), 0.25, 8)}" fill="#FCE2A0" opacity="0.32"/>'
                      f'<path d="M {x - rr:.1f} {y + rr * 0.3:.1f} A {rr:.1f} {rr:.1f} 0 0 0 {x + rr:.1f} {y + rr * 0.3:.1f}" stroke="#8A4A10" stroke-width="0.8" fill="none" opacity="0.4"/>')
        bl.append(ink(smooth_closed(pts), "#8A4A10", 7, seed + 9, 1, 0.25))
        out.append(clipped(D, smooth_closed(pts), bl))
    # the pinched seam: a flat lip of pastry with fork crimps
    seam = qcurve(M, A, -0.06, 12) + [A]
    out.append(taper(seam, 9, 4, "#F6CC78", 0.95))
    out.append(taper([(x + 2.5 * turn, y) for x, y in seam], 3, 1.5, "#9A5410", 0.5))
    for i in range(1, 11):
        x, y = seam[i]
        out.append(f'<path d="M {x - 4:.1f} {y + 1:.1f} l 7 -4" stroke="#8A4A10" stroke-width="1.6" opacity="0.65" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(A[0], A[1] + 3, 5, 4, seed, 0.2, 8)}" fill="#C47E2C"/>')
    return "".join(out)


def leaf_plate(D, cx, cy, rx, ry, seed):
    """Pattal: a round plate stitched from dried sal leaves with slivers of twig, seen at a slant: a scalloped
    rim of overlapping leaves laid tangentially, a centre of flatter leaves, the stitches showing."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx + 12, cy + 16, rx * 1.04, ry * 1.06, seed, 0.03, 30)}" fill="#1A0206" opacity="0.45"/>']
    rim = blob(cx, cy, rx, ry, seed, 0.03, 30)
    out.append(f'<path d="{rim}" fill="#7A8A3A"/>')
    pals = [("#D8D088", "#A8A858", "#5A6A24"), ("#C8C870", "#8E9A44", "#4A5A1E"), ("#E0D894", "#B0AA5C", "#66662A")]
    n = 18
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        px, py = cx + math.cos(a) * rx * 0.78, cy + math.sin(a) * ry * 0.78
        ang = math.degrees(math.atan2(math.cos(a) * ry, -math.sin(a) * rx)) + rnd.uniform(-10, 10)
        out.append(leaf_lite(D, px, py, rx * 0.5, rx * 0.17, ang, pals[i % 3], seed + i, inkw=0.8))
    for i in range(7):
        a = 2 * math.pi * i / 7 + 0.3
        px, py = cx + math.cos(a) * rx * 0.36, cy + math.sin(a) * ry * 0.36
        out.append(leaf_lite(D, px, py, rx * 0.55, rx * 0.2, math.degrees(a) + 90, pals[(i + 1) % 3], seed + 40 + i, inkw=0.8))
    out.append(f'<path d="{blob(cx, cy, rx * 0.5, ry * 0.5, seed + 60, 0.08, 18)}" fill="#B8B064" opacity="0.6"/>')
    for i in range(22):
        a = 2 * math.pi * (i + 0.5) / 22
        x, y = cx + math.cos(a) * rx * 0.6, cy + math.sin(a) * ry * 0.6
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a + 1.6) * 7:.1f} {math.sin(a + 1.6) * 3.5:.1f}" stroke="#E8DCB0" stroke-width="1.8" stroke-linecap="round" opacity="0.85"/>')
    out.append(f'<path d="{rim}" fill="none" stroke="#3A4214" stroke-width="1.4" opacity="0.5"/>')
    out.append(f'<path d="{rim}" fill="{D.lin([(0, "#FFF0C0", 0.25), (0.5, "#FFF0C0", 0), (1, "#1A2008", 0.3)], 0, 0, 1, 1)}"/>')
    return "".join(out)


def onion_ring(D, cx, cy, r, seed, ang=0):
    out = []
    for k, rr in enumerate((1.0, 0.72, 0.46)):
        out.append(f'<path d="{ellipse_d(cx, cy, r * rr, r * rr * 0.55)}" fill="none" stroke="#B8306A" stroke-width="{max(2, r * 0.13):.1f}" transform="rotate({ang} {cx} {cy})" opacity="0.9"/>')
        out.append(f'<path d="{ellipse_d(cx, cy, r * rr - r * 0.06, r * rr * 0.55 - r * 0.04)}" fill="none" stroke="#FCE8F0" stroke-width="{max(1.2, r * 0.06):.1f}" transform="rotate({ang} {cx} {cy})"/>')
    return "".join(out)


def lemon_wedge(D, cx, cy, r, seed, ang=0):
    pts = rot([(cx - r, cy), (cx - r * 0.7, cy - r * 0.5), (cx, cy - r * 0.62), (cx + r * 0.7, cy - r * 0.5), (cx + r, cy), (cx, cy + r * 0.1)], cx, cy, ang)
    out = [painted(D, pts, ("#FFF4A0", "#F6D83A", "#A89A0A"), seed, sk=0.15, n=6, inkw=1.2, hi=0.4)]
    inner = rot([(cx - r * 0.8, cy - r * 0.04), (cx, cy - r * 0.46), (cx + r * 0.8, cy - r * 0.04), (cx, cy + r * 0.02)], cx, cy, ang)
    out.append(f'<path d="{smooth_closed(inner)}" fill="#FFF8C8"/>')
    for k in range(5):
        a = math.radians(-160 + k * 35)
        ex, ey = rot([(cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.4)], cx, cy, ang)[0]
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {ex:.1f} {ey:.1f}" stroke="#F2D84A" stroke-width="1.4"/>')
    return "".join(out)


@design("samosa")
def samosa_d():
    D = Doc2("in-sm")
    # deep rani-red ground with a faint paisley block-print
    out = [sky(D, [(0, "#B8243A"), (1, "#7A1226")], 201, 600, ["#C8344A", "#6A0A1E", "#D84A5A"], 120, angle=-80, sop=(0.06, 0.16))]
    pat = []
    for j in range(8):
        for i in range(8):
            x, y = i * 92 + (46 if j % 2 else 0) - 20, j * 92 - 10
            pp = paisley_pts(x, y, 44, 30 + (j % 2) * 180)
            pat.append(f'<path d="{smooth_closed(pp)}" fill="none" stroke="#F2A0A8" stroke-width="2" opacity="0.18"/>')
            pat.append(f'<circle cx="{x - 4:.1f}" cy="{y + 4:.1f}" r="5" fill="#F2A0A8" opacity="0.16"/>')
            pat.append(f'<circle cx="{x + 46:.1f}" cy="{y + 46:.1f}" r="3" fill="#FFD0A0" opacity="0.2"/>')
    out.append("".join(pat))
    out.append(blooms(202, ["#5A0614", "#E84A5A"], 10, (0, 0, 600, 600), (60, 140), (0.08, 0.16)))
    out.append(soft_glow(D, 260, 380, 360, "#FFB070", 0.38))
    out.append(vignette(D, "#2A0208", 0.55, 0.75))
    # the leaf plate, the samosas, two chutneys, onion rings, lemon and a fried chilli
    out.append(leaf_plate(D, 300, 452, 236, 104, 203))
    out.append(steel_bowl(D, 488, 404, 50, 34, 204, fill=f'<path d="{ellipse_d(488, 406, 44, 13)}" fill="#3E8A2A"/>'
                          f'<path d="{blob(480, 403, 16, 4, 205, 0.2, 8)}" fill="#9AD06A" opacity="0.7"/>'))
    out.append(samosa(D, 210, 478, 190, 160, 206, turn=1))
    out.append(samosa(D, 372, 498, 196, 170, 207, turn=-1))
    out.append(steel_bowl(D, 104, 512, 50, 34, 208, fill=f'<path d="{ellipse_d(104, 514, 44, 13)}" fill="#6A2A12"/>'
                          f'<path d="{blob(96, 511, 16, 4, 209, 0.2, 8)}" fill="#B86A3A" opacity="0.7"/>'))
    out.append(onion_ring(D, 488, 488, 22, 210, -10))
    out.append(onion_ring(D, 514, 470, 18, 211, 20))
    out.append(lemon_wedge(D, 462, 512, 24, 212, -15))
    out.append(dried_chilli(D, 130, 556, 74, -14, 214, ("#9AD06A", "#3E8A2A", "#1E4A12")))
    out.append(pk.steam_plume(D, [(214, 316), (204, 280), (222, 246), (206, 214)], 12, 26, 215, "#FFFFFF", 0.45, puffs=False))
    out.append(pk.steam_plume(D, [(378, 326), (388, 290), (370, 256)], 12, 24, 216, "#FFFFFF", 0.4, puffs=False))
    out.append(glaze(D, [(0, "#FFE0B0", 0.12), (0.5, "#FFE0B0", 0), (1, "#3A0410", 0.2)], 0, 0, 1, 1))
    # lettering
    txt = [letters(D, 300, 156, "Samosa", SERIF_IT, 140, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 220, max_w=420,
                   shadow="#4A0614", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 202, "WITH BOTH CHUTNEYS, PLEASE", "#FFE6C8", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, out, txt, 221, under="#8A1226", edge=2.6, bristle=0.45, grain=0.2)


# ================================================================ 4. teen seeti — the pressure cooker's third whistle
def blue_flame(D, cx, y, rx, seed):
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, y, rx * 1.3, "#5AA0FF", 0.35)]
    for i in range(14):
        t = (i + 0.5) / 14
        x = cx - rx + 2 * rx * t
        h = rnd.uniform(12, 20) * (0.7 + 0.3 * math.sin(math.pi * t))
        out.append(f'<path d="M {x - 4:.1f} {y:.1f} Q {x - 2:.1f} {y - h * 0.6:.1f} {x + rnd.uniform(-2, 2):.1f} {y - h:.1f} Q {x + 3:.1f} {y - h * 0.5:.1f} {x + 4:.1f} {y:.1f} Z" fill="#3A7AF0" opacity="0.85"/>')
        out.append(f'<path d="M {x - 2:.1f} {y:.1f} Q {x:.1f} {y - h * 0.4:.1f} {x:.1f} {y - h * 0.55:.1f} Q {x + 1:.1f} {y - h * 0.3:.1f} {x + 2:.1f} {y:.1f} Z" fill="#B8E0FF" opacity="0.9"/>')
    return "".join(out)


def tile_wall_p(D, x0, y0, x1, y1, seed, size=46, base="#D6E2DE", grout="#B0BCB8", tint="#C2D4D0"):
    """Glazed white kitchen tiles, hand-painted: each tile its own slightly different wash with a sheen stroke,
    soft grout lines that wander a little."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{grout}"/>']
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            c = mix(base, tint, rnd.uniform(0, 0.5))
            t = jitter(pk.dens2([(x + 2, y + 2), (x + size - 2, y + 2), (x + size - 2, y + size - 2), (x + 2, y + size - 2)], 21), rnd.randint(0, 9999), 0.6)
            out.append(f'<path d="{smooth_closed(t)}" fill="{c}"/>')
            out.append(f'<path d="M {x + 7:.1f} {y + 9:.1f} q {size * 0.2:.1f} -3 {size * 0.45:.1f} -1" stroke="#FFFFFF" stroke-width="2.4" opacity="{rnd.uniform(0.4, 0.8):.2f}" fill="none" stroke-linecap="round"/>')
            x += size
        y += size
    return "".join(out)


@design("teen-seeti")
def teen_seeti():
    D = Doc2("in-ts")
    art = []
    # the kitchen wall: glazed tiles, a band of hand-painted border tiles, morning light from a window at the left
    art.append(tile_wall_p(D, -20, -20, 620, 470, 301))
    art.append(glaze(D, [(0, "#FFF8E8", 0.25), (0.45, "#FFF8E8", 0), (1, "#2A3A44", 0.35)], 0, 0, 1, 0))
    band = []
    for k in range(-1, 15):
        x = k * 46
        band.append(f'<path d="{smooth_closed(jitter(pk.dens2([(x + 2, 378), (x + 44, 378), (x + 44, 418), (x + 2, 418)], 10), k, 0.5))}" fill="#1E6E7A"/>')
        band.append(f'<path d="{blob(x + 23, 398, 9, 9, k + 40, 0.15, 10)}" fill="#F4C21A"/>')
        for a_ in range(4):
            r_ = math.radians(45 + a_ * 90)
            band.append(f'<path d="{blob(x + 23 + math.cos(r_) * 14, 398 + math.sin(r_) * 14, 4, 2.4, k * 9 + a_, 0.2, 8, math.degrees(r_))}" fill="#FFF4E0"/>')
    art.append("".join(band))
    # the window, its frame and a curry-leaf plant in a tin on the sill
    win = pk.dens2([(-20, 40), (150, 40), (150, 300), (-20, 300)], 12)
    art.append(f'<path d="{smooth_closed(win)}" fill="{D.lin([(0, "#BEE0F0"), (1, "#FFF6E0")])}"/>')
    art.append(soft_glow(D, 60, 160, 160, "#FFFFFF", 0.7))
    for x_ in (64,):
        art.append(f'<path d="M {x_} 40 L {x_} 300" stroke="#6A8A9A" stroke-width="6"/>')
    art.append(f'<path d="M -20 170 L 150 170" stroke="#6A8A9A" stroke-width="5"/>')
    art.append(f'<path d="{smooth_closed(win)}" fill="none" stroke="#5A7A8A" stroke-width="9"/>')
    art.append(f'<path d="M -20 306 L 168 306 L 168 318 L -20 318 Z" fill="#E8E2D6"/>')
    art.append(pk.light_shaft(D, 140, 120, 260, 520, 470, "#FFF8E0", 0.22))
    pot_ = [(70, 304), (118, 304), (112, 270), (76, 270)]
    art.append(modelled(D, pk.dens2(pot_, 6), ("#E8E8E0", "#A8B0B0", "#5A6066"), 302, light=(-0.8, -0.4), angle=-90, n=10, inkw=1, hi=0.4))
    rnd = random.Random(303)
    for k in range(9):
        a_ = -90 + rnd.uniform(-50, 50)
        L_ = rnd.uniform(40, 70)
        bx, by = 94 + rnd.uniform(-8, 8), 270
        tip = (bx + math.cos(math.radians(a_)) * L_, by + math.sin(math.radians(a_)) * L_)
        art.append(f'<path d="M {bx:.1f} {by:.1f} Q {(bx + tip[0]) / 2 + rnd.uniform(-8, 8):.1f} {(by + tip[1]) / 2:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="#3A5A2A" stroke-width="1.4" fill="none"/>')
        for j in range(6):
            t = 0.25 + j * 0.13
            px, py = bx + (tip[0] - bx) * t, by + (tip[1] - by) * t
            for sg in (-1, 1):
                art.append(leaf_lite(D, px + sg * 5, py, 11, 4, a_ + sg * 60, LEAF, k * 20 + j * 2 + (sg > 0), vein=False, inkw=0.5))
    # granite counter, lit at its front edge
    ctr = pk.dens2([(-20, 470), (620, 470), (620, 620), (-20, 620)], 14)
    art.append(f'<path d="{smooth_closed(ctr)}" fill="#2E2C30"/>')
    art.append(pk.dabs(304, (-20, 470, 620, 620), ["#7A7470", "#141216", "#B8AC9A", "#4A4448"], 170, (0.6, 2.2), (0.4, 0.9)))
    art.append(f'<path d="M -20 470 L 620 470" stroke="#8A8680" stroke-width="3"/>')
    # the gas stove: a dark steel top, black pan-support, knobs on the front lip
    stv = pk.dens2([(40, 486), (470, 486), (490, 540), (20, 540)], 10)
    art.append(modelled(D, stv, ("#6A6E76", "#2A2C32", "#0C0D10"), 305, light=(-0.6, -0.8), angle=0, n=40, inkw=1.2, hi=0.3))
    lip = pk.dens2([(20, 540), (490, 540), (490, 566), (20, 566)], 10)
    art.append(modelled(D, lip, ("#C8CCD2", "#8A9098", "#3E444C"), 306, light=(-0.6, -0.8), angle=0, n=30, inkw=1.0, hi=0.4))
    for k, kx in enumerate((92, 160, 380)):
        art.append(f'<path d="{blob(kx, 553, 12, 9, 307 + k, 0.03, 14)}" fill="#1A1A1E"/>')
        art.append(f'<path d="M {kx - 7} {551} L {kx + 7} {555}" stroke="#E8E8E8" stroke-width="2"/>')
    # the blue flame licking round the cooker's base
    for k in range(18):
        t = k / 17
        x = 150 + 200 * t
        h_ = 14 + 8 * math.sin(math.pi * t)
        art.append(f'<path d="M {x - 4:.1f} 500 Q {x - 2:.1f} {500 - h_ * 0.6:.1f} {x + rnd.uniform(-2, 2):.1f} {500 - h_:.1f} Q {x + 3:.1f} {500 - h_ * 0.5:.1f} {x + 4:.1f} 500 Z" fill="#3A7AF0" opacity="0.85"/>')
        art.append(f'<path d="M {x - 2:.1f} 500 Q {x:.1f} {500 - h_ * 0.4:.1f} {x:.1f} {500 - h_ * 0.55:.1f} Q {x + 1:.1f} {500 - h_ * 0.3:.1f} {x + 2:.1f} 500 Z" fill="#C8E8FF" opacity="0.9"/>')
    art.append(soft_glow(D, 250, 496, 130, "#5AA0FF", 0.3))
    art.append(f'<path d="M 110 494 L 390 494" stroke="#141418" stroke-width="7" stroke-linecap="round"/>')
    # the pressure cooker: satin aluminium body, the lid set inside the rim, two long black handles, the weight
    cx, top, bot, rx, ry = 250, 330, 486, 120, 30
    art.append(f'<path d="{blob(cx + 40, 492, 150, 14, 308, 0.1, 16)}" fill="#000000" opacity="0.4"/>')
    # helper handle on the far left
    art.append(modelled(D, pk.dens2([(cx - rx - 46, 356), (cx - rx + 6, 352), (cx - rx + 6, 374), (cx - rx - 46, 378)], 6), ("#5A5654", "#22201E", "#080706"), 309, light=(-0.7, -0.7), angle=0, n=8, inkw=1.2, hi=0.35))
    body, bd = pk.metal_cyl(D, cx, top, bot, rx, ry, 310, pal=("#F4F6F8", "#B4BAC2", "#565C66"), env=("#D8EAF4", "#7AA0F0"), light=-1, bulge=0.04, gloss=0.6)
    art.append(body)
    # the rim, the lid sunk inside it, its raised centre
    art.append(pk.metal_ellipse(D, cx, top, rx, ry, 311, pal=("#FFFFFF", "#C4CAD2", "#6A7078"), inner_pal=("#B8BEC6", "#8A9098", "#4A5058"), rim_w=7))
    lid = blob(cx, top + 4, rx - 14, ry - 6, 312, 0.004, 30)
    art.append(f'<path d="{lid}" fill="{D.lin([(0, "#E8ECF0"), (0.5, "#AEB4BC"), (1, "#6A7078")], 0, 0, 1, 1)}"/>')
    art.append(f'<path d="{blob(cx - 6, top + 2, rx * 0.36, ry * 0.4, 313, 0.01, 24)}" fill="#D8DCE2"/>')
    art.append(f'<path d="{blob(cx - 6, top + 2, rx * 0.36, ry * 0.4, 313, 0.01, 24)}" fill="none" stroke="#5A6068" stroke-width="1.2" opacity="0.6"/>')
    # long handles: the body handle below, the lid handle riding on it
    hb1 = pk.dens2([(cx + rx - 10, top + 8), (cx + rx + 150, top - 4), (cx + rx + 156, top + 14), (cx + rx - 8, top + 28)], 8)
    art.append(modelled(D, hb1, ("#4A4644", "#1A1816", "#060505"), 314, light=(-0.4, -1), angle=-5, n=16, inkw=1.3, hi=0.3))
    hb2 = pk.dens2([(cx + 30, top - 8), (cx + rx + 156, top - 12), (cx + rx + 160, top + 6), (cx + 34, top + 10)], 8)
    art.append(modelled(D, hb2, ("#6A6460", "#26221F", "#080706"), 315, light=(-0.4, -1), angle=-3, n=20, inkw=1.4, hi=0.45))
    art.append(taper([(cx + 60, top - 6), (cx + rx + 140, top - 10)], 2.6, 1.2, "#FFFFFF", 0.35))
    art.append(f'<path d="{blob(cx + rx - 2, top + 2, 12, 10, 316, 0.05, 10)}" fill="#C8CCD2"/>')
    # the vent pipe and the weight, lifted and hissing
    vx, vy = cx - 8, top - 2
    art.append(f'<path d="M {vx - 4} {vy} L {vx - 4} {vy - 14} L {vx + 4} {vy - 14} L {vx + 4} {vy} Z" fill="#9AA0A8"/>')
    wt = [(vx - 13, vy - 18), (vx - 11, vy - 38), (vx - 6, vy - 48), (vx + 6, vy - 48), (vx + 11, vy - 38), (vx + 13, vy - 18)]
    art.append(modelled(D, rot(wt, vx, vy - 18, 12), ("#7A7470", "#2E2A28", "#0E0C0C"), 317, light=(-0.7, -0.7), angle=-90, n=8, inkw=1.2, hi=0.45))
    # the jet of steam: three billows climbing, one per whistle
    art.append(taper([(vx + 6, vy - 22), (vx + 22, vy - 40), (vx + 44, vy - 62)], 4, 18, "#FFFFFF", 0.85))
    plume = [(vx + 40, vy - 60), (vx + 70, vy - 90), (vx + 116, vy - 110), (vx + 166, vy - 120), (vx + 212, vy - 128), (vx + 250, vy - 134)]
    art.append(pk.steam_plume(D, plume, 22, 60, 318, "#FFFFFF", 0.9))
    for k, (sx_, sy_, r_) in enumerate(((vx + 64, vy - 86, 28), (vx + 148, vy - 118, 36), (vx + 246, vy - 132, 42))):
        rr_ = random.Random(319 + k)
        lobes = [(sx_ + rr_.uniform(-0.5, 0.5) * r_, sy_ + rr_.uniform(-0.4, 0.4) * r_, r_ * rr_.uniform(0.45, 0.7)) for _ in range(7)]
        for lx, ly, lr in lobes:
            art.append(f'<path d="{blob(lx + lr * 0.25, ly + lr * 0.3, lr, lr * 0.85, rr_.randint(0, 999), 0.12, 12)}" fill="{D.rad([(0, "#7A90A0", 0.35), (1, "#7A90A0", 0)])}"/>')
        for lx, ly, lr in lobes:
            art.append(f'<path d="{blob(lx, ly, lr, lr * 0.85, rr_.randint(0, 999), 0.12, 12)}" fill="{D.rad([(0, "#FFFFFF", 0.95), (0.6, "#FFFFFF", 0.7), (1, "#FFFFFF", 0)], 0.42, 0.4, 0.6)}"/>')
    for a_ in (-60, -25, 10):
        rr = math.radians(a_ - 90)
        art.append(pline([(vx + math.cos(rr) * 22, vy - 34 + math.sin(rr) * 22), (vx + math.cos(rr) * 34, vy - 34 + math.sin(rr) * 34)], "#C8281E", 2.6, 322 + a_, 0.9, 1))
    # a steel tumbler of water and a katori of dal waiting on the counter
    tb, _ = pk.metal_cyl(D, 538, 472, 548, 25, 6, 330, light=-1, taper_=0.12, gloss=0.8)
    art.append(f'<path d="{blob(548, 550, 30, 5, 331, 0.1, 12)}" fill="#000000" opacity="0.35"/>')
    art.append(tb)
    art.append(pk.metal_ellipse(D, 538, 472, 25, 6, 332, rim_w=2.2))
    art.append(glaze(D, [(0, "#FFF4E0", 0.18), (0.55, "#FFF4E0", 0), (1, "#2A2A3A", 0.22)], 0, 0, 1, 0.3))
    art.append(vignette(D, "#1A1A22", 0.32, 0.8))
    txt = [letters(D, 300, 122, "teen seeti", SERIF_IT, 118, "#B8281E", ["#D8402A", "#7A0E0A", "#F06A4A"], 340, max_w=440,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB0A0"),
           sub(300, 166, "THREE WHISTLES & THE DAL IS DONE", "#12606A", font=JOS, size=18, ls=4, line_w=16, gap=10)]
    return finish_art(D, art, txt, 341, under="#E8E6E0", edge=2.4, bristle=0.4, grain=0.16)


# ================================================================ 5. shubh deepavali — diyas around a rangoli on the threshold
def rangoli(D, cx, cy, R, seed, sy=0.5):
    """Coloured-powder rangoli seen at a slant: rings, a lotus of petals, dotted white outlines."""
    rnd = random.Random(seed)
    out = []

    def E(rr):
        return ellipse_d(cx, cy, rr, rr * sy, 48)

    rings = [(1.0, "#F2901E"), (0.92, "#D6246E"), (0.8, "#FFFFFF"), (0.77, "#2A3A90"), (0.62, "#F4C21A"), (0.5, "#3E8A3A"), (0.36, "#D6342A"), (0.2, "#F4C21A")]
    for rr, c in rings:
        out.append(f'<path d="{E(R * rr)}" fill="{c}"/>')
    # petals of the lotus ring
    for ring, (rr, n, c, cin) in enumerate(((0.9, 16, "#D6246E", "#FF8AB8"), (0.68, 12, "#F2901E", "#FFE08A"), (0.46, 8, "#12808A", "#8AE0D8"))):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * ring) / n
            px, py = cx + math.cos(a) * R * rr * 0.86, cy + math.sin(a) * R * rr * 0.86 * sy
            L = R * rr * 0.32
            pts = [(cx + math.cos(a) * R * (rr - 0.16), cy + math.sin(a) * R * (rr - 0.16) * sy),
                   (px + math.cos(a + 1.57) * L * 0.5, py + math.sin(a + 1.57) * L * 0.5 * sy),
                   (cx + math.cos(a) * R * (rr + 0.06), cy + math.sin(a) * R * (rr + 0.06) * sy),
                   (px - math.cos(a + 1.57) * L * 0.5, py - math.sin(a + 1.57) * L * 0.5 * sy)]
            out.append(f'<path d="{smooth_closed(pts)}" fill="{c}"/>')
            inner = [(x * 0.55 + px * 0.45, y * 0.55 + py * 0.45) for x, y in pts]
            out.append(f'<path d="{smooth_closed(inner)}" fill="{cin}"/>')
    # dotted white rice-flour outlines
    for rr in (1.0, 0.8, 0.58, 0.36):
        n = int(R * rr * 0.32)
        for i in range(n):
            a = 2 * math.pi * i / n
            out.append(f'<circle cx="{cx + math.cos(a) * R * rr:.1f}" cy="{cy + math.sin(a) * R * rr * sy:.1f}" r="{max(1.4, R * 0.012):.1f}" fill="#FFFFFF" opacity="0.95"/>')
    # powdery grain
    out.append(specks(seed, (cx - R, cy - R * sy, cx + R, cy + R * sy), ["#FFFFFF", "#000000"], int(R * 1.2), (0.5, 1.2), (0.15, 0.35)))
    out.append(f'<path d="{E(R * 1.03)}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.4" stroke-dasharray="2 4"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.07:.1f}" fill="#FFFFFF" transform="translate(0 0) scale(1 1)"/>')
    return "".join(out)


def kandil(D, cx, cy, s, seed, col="#F2701E", col2="#F6C21C"):
    """Akash kandil: a star-shaped paper lantern glowing from within, paper tassels hanging below."""
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, cy, s * 2.4, "#FFB050", 0.6)]
    pts = []
    for i in range(10):
        r = s if i % 2 == 0 else s * 0.5
        a = math.radians(-90 + i * 36)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.9))
    out.append(f'<path d="{pdl(pts)}" fill="{col}"/>')
    out.append(f'<path d="{pdl(pts)}" fill="{D.rad([(0, "#FFF6C8", 0.95), (0.5, col2, 0.6), (1, col, 0)])}"/>')
    out.append(f'<path d="{pdl([(x * 0.55 + cx * 0.45, y * 0.55 + cy * 0.45) for x, y in pts])}" fill="none" stroke="#FFF0C0" stroke-width="1.4" opacity="0.8"/>')
    out.append(f'<path d="{pdl(pts)}" fill="none" stroke="#7A2A08" stroke-width="1.2" opacity="0.6"/>')
    for k in range(7):
        x = cx - s * 0.4 + k * s * 0.13
        out.append(f'<path d="M {x:.1f} {cy + s * 0.5:.1f} q {rnd.uniform(-3, 3):.1f} {s * 0.5:.1f} {rnd.uniform(-4, 4):.1f} {s * rnd.uniform(0.9, 1.3):.1f}" stroke="{rnd.choice([col, col2, "#D6246E"])}" stroke-width="2.2" fill="none"/>')
    return "".join(out)


def firework(cx, cy, r, seed, col="#FFE08A", op=0.7):
    rnd = random.Random(seed)
    out = []
    for k in range(26):
        a = 2 * math.pi * k / 26 + rnd.uniform(-0.05, 0.05)
        r0, r1 = r * rnd.uniform(0.15, 0.3), r * rnd.uniform(0.75, 1.0)
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        x1, y1 = cx + math.cos(a) * r1, cy + math.sin(a) * r1 + r * 0.08
        out.append(taper([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - r * 0.02), (x1, y1)], 0.4, 2.4, col, op))
        out.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="1.6" fill="#FFFFFF" opacity="{op:.2f}"/>')
    return "".join(out)


@design("shubh-deepavali")
def shubh_deepavali():
    D = Doc2("in-sd")
    art = [sky(D, [(0, "#1A0E3A"), (0.5, "#36184E"), (1, "#2A0E2A")], 401, 600, ["#3A1A60", "#120828", "#5A2A6A"], 140, angle=-4, sop=(0.06, 0.16))]
    art.append(firework(110, 90, 70, 430, "#FFD86A", 0.45))
    art.append(firework(500, 70, 60, 431, "#FF8AB8", 0.4))
    art.append(firework(440, 150, 34, 432, "#8AE0D8", 0.35))
    # the house front: a lime-washed wall in lamplight, the open door blazing, diyas on every ledge
    wall = pk.dens2([(-20, 240), (620, 240), (620, 352), (-20, 352)], 14)
    art.append(f'<path d="{smooth_closed(wall)}" fill="#6A3A4A"/>')
    art.append(f'<path d="{smooth_closed(wall)}" fill="{D.rad([(0, "#F2A060", 0.55), (0.5, "#C86A50", 0.2), (1, "#3A1A2A", 0)], 0.5, 1.0, 0.7)}"/>')
    art.append(strokes(D.nid(), smooth_closed(wall), (-40, 240, 620, 352), ["#8A5060", "#4A2030", "#C88070"], 402, n=60, angle=-86, length=(20, 60), width=(3, 8), opacity=(0.12, 0.3)))
    door = pk.dens2([(244, 352), (356, 352), (356, 262), (244, 262)], 8)
    art.append(f'<path d="{smooth_closed(door)}" fill="{D.lin([(0, "#FFE8A0"), (1, "#F2902A")])}"/>')
    art.append(soft_glow(D, 300, 320, 140, "#FFD070", 0.6))
    art.append(f'<path d="{smooth_closed(door)}" fill="none" stroke="#3A1A10" stroke-width="7"/>')
    art.append(garland(D, [(236, 262), (300, 278), (364, 262)], 6.4, 403, leaves=True))
    for x in range(10, 600, 46):
        if 230 < x < 370:
            continue
        art.append(diya(D, x, 244, 9, 404 + x, glow=True, flame_h=1.1))
    # string lights swagged across the wall top
    lights = [(-10, 236), (150, 262), (300, 250), (450, 264), (610, 234)]
    cp = catmull(lights, 10)
    art.append(pline(lights, "#1A0A20", 1.4, 405, 0.9, 1))
    for i, (x, y) in enumerate(cp[::4]):
        c = ["#FFE27A", "#FF8A5A", "#FFFFFF", "#8AE0D8"][i % 4]
        art.append(soft_glow(D, x, y + 5, 16, c, 0.6))
        art.append(f'<circle cx="{x:.1f}" cy="{y + 5:.1f}" r="3" fill="{c}"/>')
    # paper lanterns hanging either side
    for x_, y_, c1, c2, sd in ((84, 300, "#F2701E", "#F6C21C", 406), (516, 304, "#D6246E", "#FF9AC8", 407)):
        art.append(f'<path d="M {x_} 236 L {x_} {y_ - 24}" stroke="#2A1A10" stroke-width="1.2"/>')
        art.append(kandil(D, x_, y_, 26, sd, c1, c2))
    # the courtyard floor, stone and warm reflections, the rangoli in perspective
    fl = [(-10, 352), (610, 352), (610, 610), (-10, 610)]
    art.append(f'<path d="{pdl(fl)}" fill="#3A2028"/>')
    art.append(f'<path d="{pdl(fl)}" fill="{D.lin([(0, "#8A4A40", 0.6), (0.4, "#3A2028", 0.2), (1, "#1A0A12", 0.5)])}"/>')
    art.append(strokes(D.nid(), pdl(fl), (-40, 352, 610, 610), ["#5A3A40", "#1A0A10", "#7A4A40"], 408, n=100, angle=0, length=(40, 140), width=(2, 6), opacity=(0.1, 0.28)))
    art.append(f'<path d="{pdl([(244, 352), (356, 352), (420, 420), (180, 420)])}" fill="#FFC870" opacity="0.18"/>')
    art.append(soft_glow(D, 300, 470, 300, "#FFB050", 0.38))
    art.append(rangoli(D, 300, 478, 196, 404, 0.42))
    art.append(clipped(D, ellipse_d(300, 478, 196, 196 * 0.42, 48), [pk.dabs(409, (100, 390, 500, 570), ["#FFFFFF", "#1A0A10", "#FFE8A0"], 300, (0.5, 1.4), (0.2, 0.5))]))
    rnd = random.Random(410)
    ring = []
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.3
        x, y = 300 + math.cos(a) * 232, 478 + math.sin(a) * 232 * 0.42
        ring.append((y, x, a))
    for y, x, a in sorted(ring):
        s_ = 22 + (y - 378) * 0.1
        art.append(f'<ellipse cx="{x:.1f}" cy="{y + s_ * 0.5:.1f}" rx="{s_ * 1.8:.1f}" ry="{s_ * 0.5:.1f}" fill="{D.rad([(0, "#FFC860", 0.5), (1, "#FFC860", 0)])}"/>')
        art.append(diya(D, x - s_ * 0.1, y, s_, 411 + int(x)))
    for k in range(30):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(1.05, 1.35)
        x, y = 300 + math.cos(a) * 200 * rr, 478 + math.sin(a) * 84 * rr
        if y < 368 or y > 592 or x < 30 or x > 570:
            continue
        art.append(f'<path d="{blob(x, y, 5, 3, k + 440, 0.25, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2901E", "#F4C21A", "#D6342A"])}"/>')
    art.append(vignette(D, "#08020E", 0.45, 0.8))
    txt = [letters(D, 300, 166, "Shubh Deepavali", SERIF_IT, 76, "#FFD06A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 420, max_w=470,
                   shadow="#12061E", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 208, "MAY YOUR HOME BE FULL OF LIGHT", "#FFC8A0", font=JOS, size=18, ls=4, line_w=20, gap=10)]
    return finish_art(D, art, txt, 421, under="#2A0E2A", edge=2.2, bristle=0.4, grain=0.18)


# ================================================================ 6. chalo! — the auto-rickshaw at the corner
@design("chalo")
def chalo():
    D = Doc2("in-cl")
    cam = Cam3((720, 520, 200), (-20, 0, 85), f=1450, cx=300, cy=392)
    L3 = (0.35, 0.75, 0.55)
    art = []
    Y = -330                                        # the shop-house facade across the lane

    def F(x, z):
        return cam((x, Y, z))

    def fpoly(pts):
        return [F(x, z) for x, z in pts]
    # sky above the roofline (only a sliver shows) and the warm ochre wall in late sun
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#F2C48A"/>')
    wall = fpoly([(-900, 0), (700, 0), (700, 700), (-900, 700)])
    wd = pdl(wall)
    art.append(f'<path d="{wd}" fill="#E6A85A"/>')
    gw = D.lin([(0, "#F8D290", 0.9), (0.55, "#E6A85A", 0), (1, "#B8702E", 0.6)], 0, 0, 1, 0)
    art.append(f'<path d="{wd}" fill="{gw}"/>')
    art.append(strokes(D.nid(), wd, (-40, -40, 640, 640), ["#F6C27A", "#C8803A", "#F2B868", "#D89048"], 501, n=170, angle=-86, length=(20, 80), width=(3, 9), opacity=(0.12, 0.3), curve=0.3))
    art.append(blooms(502, ["#B8682A", "#FFE0A8", "#9A5A2A"], 9, (0, 0, 600, 470), (40, 110), (0.08, 0.16)))
    # peeled plaster showing brick
    for k, (px, pz, w, h) in enumerate(((-1150, 120, 60, 34),)):
        pp = fpoly([(px, pz), (px + w, pz + 6), (px + w * 0.9, pz - h), (px + 6, pz - h * 0.8)])
        d = smooth_closed(pp)
        art.append(f'<path d="{d}" fill="#B86A44"/>')
        cid = D.clip(f'<path d="{d}"/>')
        br = []
        for j in range(10):
            q0, q1 = F(px - 10, pz - j * 7), F(px + w + 10, pz - j * 7 + 1)
            br.append(f'<path d="M {q0[0]:.1f} {q0[1]:.1f} L {q1[0]:.1f} {q1[1]:.1f}" stroke="#F2C8A0" stroke-width="1.2" opacity="0.7"/>')
        art.append(f'<g {cid}>{"".join(br)}</g>')
        art.append(f'<path d="{d}" fill="none" stroke="#FFF0D0" stroke-width="1.6" opacity="0.7"/>')
    # rain stains running down from the parapet
    art.append(clipped(D, wd, [strokes(D.nid(), wd, (-40, -40, 640, 200), ["#A8682A", "#8A5A2A"], 509, n=40, angle=-92, length=(30, 120), width=(2, 6), opacity=(0.08, 0.18))]))
    # a blue wooden door down the lane, with its stone step and a painted shop sign beside it
    door = fpoly(pk.dens2([(-1010, 15), (-880, 15), (-880, 235), (-1010, 235)], 8))
    art.append(f'<path d="{pdl(fpoly([(-1030, 15), (-860, 15), (-860, 255), (-1030, 255)]))}" fill="#8A6A4A"/>')
    art.append(modelled(D, door, ("#5A9AD8", "#2A5E9E", "#0E2A50"), 503, light=(-0.6, -0.5), angle=-90, n=40, inkw=1.2, hi=0.3))
    for z0 in (40, 140):
        pnl = fpoly([(-995, z0), (-895, z0), (-895, z0 + 80), (-995, z0 + 80)])
        art.append(f'<path d="{pdl(pnl)}" fill="none" stroke="#0E2A50" stroke-width="2" opacity="0.6"/>')
    sg = fpoly(pk.dens2([(-1280, 150), (-1120, 150), (-1120, 230), (-1280, 230)], 8))
    art.append(modelled(D, sg, ("#FFFFFF", "#F4EEE2", "#B8AE9E"), 504, light=(-0.6, -0.5), angle=0, n=12, inkw=1.0, hi=0.2))
    for k, z in enumerate((212, 192, 172)):
        q0, q1 = F(-1265, z), F(-1135 - k * 12, z)
        art.append(taper([q0, q1], 4.5 - k, 3 - k * 0.6, ("#C8302A", "#1E4E8A", "#C8302A")[k], 0.85))
    # bougainvillea spilling over the parapet at the top right
    rnd = random.Random(505)
    for k in range(150):
        x = rnd.uniform(470, 640)
        y = rnd.uniform(-10, 70) + (x - 470) * 0.35 + (rnd.random() ** 2) * 60
        if rnd.random() < 0.28:
            art.append(leaf_lite(D, x, y, 14, 5, rnd.uniform(0, 360), LEAF, k + 506, vein=False, inkw=0.6))
        else:
            c = rnd.choice([RANI, ("#FF9AC8", "#E8448A", "#9A1A50"), ("#FFB0D8", "#F05A9A", "#A8205A")])
            art.append(f'<path d="{blob(x, y, 7, 6, k + 600, 0.25, 8)}" fill="{c[1]}"/><path d="{blob(x - 2, y - 2, 3.4, 2.6, k + 700, 0.2, 6)}" fill="{c[0]}" opacity="0.8"/>')
    for k in range(9):
        x, y = rnd.uniform(380, 590), rnd.uniform(400, 470)
        art.append(f'<path d="{blob(x, y, 4, 3, k + 800, 0.25, 8, rnd.uniform(0, 90))}" fill="#E8448A" opacity="0.85"/>')
    # overhead wires sagging across the lane
    for k, (y0, y1, sag) in enumerate(((22, 60, 30), (40, 92, 26))):
        art.append(pline([(-20, y0), (300, y0 + sag + (y1 - y0) / 2), (620, y1)], "#2A1E18", 1.6, 510 + k, 0.8, 1))
    # sidewalk and kerb, the asphalt lane
    sw = [cam((x, y, 15)) for x, y in ((-900, Y), (700, Y), (700, -250), (-900, -250))]
    art.append(f'<path d="{pdl(sw)}" fill="#C8B49A"/>')
    kerb = [cam(p) for p in ((-900, -250, 15), (700, -250, 15), (700, -250, 0), (-900, -250, 0))]
    art.append(f'<path d="{pdl(kerb)}" fill="#8A7A68"/>')
    for x in range(-900, 700, 60):
        q = [cam(p) for p in ((x, -250, 15), (x + 30, -250, 15), (x + 30, -250, 0), (x, -250, 0))]
        art.append(f'<path d="{pdl(q)}" fill="#F2EEE6" opacity="0.85"/>')
    road = [cam(p) for p in ((-900, -250, 0), (700, -250, 0), (700, 380, 0), (-900, 380, 0))]
    rd = pdl(road)
    art.append(f'<path d="{rd}" fill="#9A8C7E"/>')
    art.append(f'<path d="{rd}" fill="{D.lin([(0, "#6A5E54", 0.6), (0.6, "#B8A890", 0.1), (1, "#D8C8B0", 0.3)])}"/>')
    art.append(strokes(D.nid(), rd, (-40, 380, 640, 640), ["#7A6E62", "#C8B8A2", "#5A5048", "#D8CCB8"], 507, n=160, angle=-8, length=(20, 90), width=(1.5, 5), opacity=(0.15, 0.35)))
    art.append(pk.dabs(508, (0, 470, 600, 600), ["#5A4E44", "#E8DCC8"], 90, (0.8, 2.2), (0.3, 0.7)))
    # the shadow of the house across the lane climbing the lower wall, and a tree's leaf shadows
    shp = [F(-1500, 0), F(-1500, 60), F(-700, 140), F(-150, 260), F(100, 300), F(100, 0)]
    art.append(f'<path d="{smooth_closed(shp)}" fill="#5A2A3A" opacity="0.32"/>')
    art.append(leaf_shadows(D, 509, (330, 180, 640, 420), "#6A2A0A", 26, (0.06, 0.12), (12, 26)))
    art.append(haze_band(D, 300, 260, "#FFE8B0", 0.12))
    # the auto's cast shadow on the road (projected along the sun)
    def sh_pt(p):
        x, y, z = p
        return cam((x - L3[0] / L3[2] * z, y - L3[1] / L3[2] * z, 0))
    corners = [(x, y, z) for x in (112, 100, -148) for y in (66, -66) for z in (0, 170)] + [(-148, y, 80) for y in (66, -66)]
    hullp = pk._hull([sh_pt(p) for p in corners])
    art.append(f'<path d="{smooth_closed(hullp)}" fill="#3A2030" opacity="0.38"/>')
    under = pk._hull([cam((x, y, 0)) for x in (125, -150) for y in (70, -70)])
    art.append(f'<path d="{smooth_closed(under)}" fill="#1A0E0A" opacity="0.5"/>')
    # the auto itself
    av, _ = pk.auto_rickshaw(D, cam, 512, light=L3)
    art.append(av)
    # marigold garland across the top of the windscreen and a nimbu-mirchi charm under the nose
    gl = [cam((94, y, 146 - 8 * (1 - (y / 50) ** 2))) for y in range(-48, 50, 8)]
    art.append(garland(D, gl, 4.2, 513, leaves=False))
    np_ = cam((102, 0, 44))
    art.append(f'<path d="M {np_[0]:.1f} {np_[1]:.1f} l 0 22" stroke="#FFFFFF" stroke-width="1"/>')
    art.append(lemon(D, np_[0], np_[1] + 26, 5.5, 514))
    for k, ang in enumerate((80, 95, 110)):
        art.append(green_chilli(D, np_[0], np_[1] + 30, 15, ang, 515 + k))
    # warm low sun washing in from the left, a cool shadow at the right
    art.append(glaze(D, [(0, "#FFE0A0", 0.22), (0.55, "#FFE0A0", 0), (1, "#3A2A5A", 0.18)], 0, 0, 1, 0))
    art.append(pk.dabs(530, (60, 200, 560, 470), ["#FFF2C8", "#FFFFFF"], 26, (0.8, 1.8), (0.25, 0.6)))
    art.append(vignette(D, "#3A1A0A", 0.3, 0.8))
    txt = [letters(D, 300, 140, "Chalo!", SERIF_IT, 156, "#1E3E6A", ["#2E5A9A", "#0E2240", "#4A7AB8"], 520, max_w=380,
                   shadow="#FFF0D8", soff=(0.022, 0.035), angle=-40, hi="#A8C8F0"),
           sub(300, 188, "KAHAN JAANA HAI?", "#7A1E2A", font=JOS, size=21, ls=5, line_w=24, gap=12)]
    return finish_art(D, art, txt, 521, under="#E6A85A", edge=2.6, bristle=0.5, grain=0.2)


# ================================================================ 7. dosa — a masala dosa on a banana leaf, sambar and chutneys
def dosa_roll(D, p0, p1, r0, r1, seed):
    """Masala dosa rolled into a long tapering tube: lacy golden-brown crisp skin, an open end showing the spiral and filling."""
    rnd = random.Random(seed)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    top, bot = [], []
    for i in range(21):
        t = i / 20
        r = r0 + (r1 - r0) * t
        x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        sag = math.sin(math.pi * t) * 4
        top.append((x - nx * r, y - ny * r + sag))
        bot.append((x + nx * r, y + ny * r + sag))
    pts = top + bot[::-1]
    out = [cast(D, (p0[0] + p1[0]) / 2 + 10, (p0[1] + p1[1]) / 2 + r0 * 0.9, math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 0.52, r0 * 0.5, strength=0.5, seed=seed)]
    out.append(painted(D, pts, ("#F8CC70", "#D88A2E", "#8A4A10"), seed, sdir=(nx, ny), sk=0.25, angle=math.degrees(a), n=90,
                       cols=["#FFF0C0", "#B86A1E", "#F6C46A", "#8A4A10"], inkw=1.8, hi=0.45, hik=0.12, curve=0.3))
    d = smooth_closed(pts)
    lace = []
    for _ in range(170):
        t = rnd.random()
        r = r0 + (r1 - r0) * t
        v = rnd.uniform(-1, 1)
        x = p0[0] + (p1[0] - p0[0]) * t + nx * r * v
        y = p0[1] + (p1[1] - p0[1]) * t + ny * r * v + math.sin(math.pi * t) * 4
        rr = rnd.uniform(1.5, 4.5)
        lace.append(f'<path d="{blob(x, y, rr, rr * 0.7, rnd.randint(0, 9999), 0.3, 7, math.degrees(a))}" fill="{rnd.choice(["#A85A14", "#8A4210", "#C8782A"])}" opacity="{rnd.uniform(0.35, 0.75):.2f}"/>')
    for k in range(9):
        t = (k + 0.5) / 9
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        r = r0 + (r1 - r0) * t
        lace.append(f'<path d="M {x - nx * r * 0.8:.1f} {y - ny * r * 0.8:.1f} q {ux * 10 + nx * r * 0.4:.1f} {uy * 10 + ny * r * 0.4:.1f} {nx * r * 1.6:.1f} {ny * r * 1.6:.1f}" stroke="#FFF0C8" stroke-width="2" fill="none" opacity="0.35"/>')
    lace.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.0), (0.3, "#FFF6D8", 0.35), (0.45, "#FFFFFF", 0), (1, "#5A2A08", 0.4)], 0, 0, 0, 1)}"/>')
    out.append(clipped(D, d, lace))
    # open end at p0: crisp spiral lip and the potato masala peeking out
    ex, ey = p0
    out.append(f'<path d="{ellipse_d(ex, ey, r0 * 0.42, r0 * 1.0)}" fill="#F2C24A" transform="rotate({math.degrees(a):.1f} {ex:.1f} {ey:.1f})"/>')
    for k in range(10):
        px, py = ex + rnd.uniform(-r0 * 0.3, r0 * 0.3), ey + rnd.uniform(-r0 * 0.7, r0 * 0.7)
        out.append(f'<path d="{blob(px, py, rnd.uniform(3, 6), rnd.uniform(2.5, 4.5), rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#FFE07A", "#E8B030", "#F6D060"])}"/>')
    for k in range(4):
        px, py = ex + rnd.uniform(-r0 * 0.25, r0 * 0.25), ey + rnd.uniform(-r0 * 0.6, r0 * 0.6)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="#2A1A10"/>')
    out.append(f'<path d="{smooth_open(ell_pts(ex, ey, r0 * 0.46, r0 * 1.04, 90, 300, 14))}" fill="none" stroke="#C8782A" stroke-width="5" transform="rotate({math.degrees(a):.1f} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<path d="{smooth_open(ell_pts(ex, ey, r0 * 0.3, r0 * 0.66, 120, 330, 12))}" fill="none" stroke="#E8A848" stroke-width="3" transform="rotate({math.degrees(a):.1f} {ex:.1f} {ey:.1f})"/>')
    return "".join(out)


def curry_leaf(D, x, y, L, ang, seed):
    return leaf_simple(D, x, y, L, L * 0.26, ang, ("#5EA84A", "#2E6A2A", "#123A12"), seed, inkw=0.8)


@design("dosa")
def dosa():
    D = Doc2("in-ds")
    # a dark teak table in morning light
    out = [wood_planks(D, 0, 600, 701, DARKWOOD, 5, vertical=True)]
    out.append(soft_glow(D, 160, 120, 460, "#FFE0A8", 0.34))
    out.append(leaf_shadows(D, 700, (300, 0, 640, 300), "#000000", 24, (0.08, 0.16), (16, 34)))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#000000", 0), (1, "#000000", 0.3)], 0, 0, 1, 1)}"/>')
    # the banana leaf: torn edge, splits along the veins, a glossy sheen
    rl = random.Random(702)
    edge = []
    for k in range(31):
        x = -20 + k * 640 / 30
        y = 600 + rl.uniform(-6, 10) + (24 if 8 < k < 11 else 0)
        edge.append((x, y))
    leaf = [(-20, 262), (620, 236)] + [(620, 600)] + edge[::-1][1:]
    out.append(f'<path d="{smooth_closed(shift(leaf, 8, 12))}" fill="#000000" opacity="0.4"/>')
    ld = smooth_closed(leaf)
    out.append(f'<path d="{ld}" fill="#3E8A34"/>')
    out.append(f'<path d="{ld}" fill="{D.lin([(0, "#C8E890", 0.9), (0.12, "#8CC860", 0.6), (0.5, "#3E8A34", 0.1), (1, "#143A14", 0.75)], 0, 0, 0.06, 1)}"/>')
    rv = random.Random(705)
    veins = []
    for k in range(-40, 120):
        x0_ = k * 6.5
        c_ = "#B8E088" if k % 4 == 0 else ("#1E5A1E" if k % 4 == 2 else "#5EA84A")
        veins.append(f'<path d="M {x0_:.1f} 290 L {x0_ - 60:.1f} 640" stroke="{c_}" stroke-width="{1.4 if k % 4 == 0 else 0.9}" opacity="{0.35 if k % 4 == 0 else 0.22}"/>')
    for k in range(9):
        x0_ = rv.uniform(-20, 600)
        w_ = rv.uniform(20, 60)
        veins.append(f'<path d="M {x0_:.1f} 290 L {x0_ + w_:.1f} 290 L {x0_ + w_ - 60:.1f} 640 L {x0_ - 60:.1f} 640 Z" fill="#F4FFE0" opacity="{rv.uniform(0.06, 0.14):.2f}"/>')
    for k in range(5):
        x0_ = rv.uniform(40, 560)
        h_ = rv.uniform(60, 140)
        veins.append(f'<path d="M {x0_:.1f} 640 L {x0_ + h_ * 60 / 350:.1f} {640 - h_:.1f} L {x0_ + 4:.1f} 640 Z" fill="#0E2A0E" opacity="0.7"/>')
    out.append(clipped(D, ld, veins))
    out.append(ink(ld, "#1E4A1A", 1.6, 706, 1, 0.5))
    out.append(taper([(-20, 304), (300, 292), (620, 280)], 9, 7, "#2E7A2A", 0.5))
    out.append(taper([(-20, 300), (300, 288), (620, 276)], 4, 3, "#C8F0A0", 0.6))
    # steel bowls: sambar (big), coconut chutney, red chutney
    sam = (f'<path d="{ellipse_d(474, 352, 84, 25)}" fill="#C85A1E"/>'
           f'<path d="{blob(458, 348, 40, 9, 705, 0.2, 10)}" fill="#E8843A" opacity="0.7"/>')
    rnd = random.Random(706)
    for k in range(10):
        x, y = 474 + rnd.uniform(-64, 64), 352 + rnd.uniform(-15, 15)
        sam += f'<path d="{blob(x, y, rnd.uniform(4, 8), rnd.uniform(3, 5), k, 0.2, 8)}" fill="{rnd.choice(["#F2A65A", "#FFE08A", "#7AA03A", "#E86A2A"])}"/>'
    sam += f'<path d="{hg.org_rect(440, 340, 50, 8, 707, 0.4, 8, 3)}" fill="#6A8A2A" transform="rotate(-14 465 344)"/>'
    out.append(steel_bowl(D, 474, 350, 92, 52, 708, fill=sam))
    out.append(curry_leaf(D, 500, 344, 26, -30, 709))
    coco = (f'<path d="{ellipse_d(116, 520, 60, 18)}" fill="#F6F2E6"/>'
            f'<path d="{blob(104, 517, 26, 6, 710, 0.2, 10)}" fill="#FFFFFF"/>')
    for k in range(12):
        x, y = 116 + rnd.uniform(-46, 46), 520 + rnd.uniform(-11, 11)
        coco += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="#2A1A10"/>'
    out.append(steel_bowl(D, 116, 518, 66, 40, 711, fill=coco))
    out.append(curry_leaf(D, 130, 516, 24, 200, 712))
    out.append(curry_leaf(D, 104, 522, 20, -20, 713))
    red = f'<path d="{ellipse_d(254, 556, 50, 15)}" fill="#C8301E"/><path d="{blob(244, 553, 20, 5, 714, 0.2, 10)}" fill="#F06A4A" opacity="0.7"/>'
    out.append(steel_bowl(D, 254, 554, 56, 34, 715, fill=red))
    # the dosa, rolled, running corner to corner
    out.append(dosa_roll(D, (92, 404), (566, 474), 54, 34, 716))
    out.append(curry_leaf(D, 392, 506, 30, 10, 717))
    out.append(pk.steam_plume(D, [(140, 380), (128, 340), (150, 300)], 12, 26, 718, "#FFFFFF", 0.4, puffs=False))
    out.append(pk.steam_plume(D, [(474, 318), (486, 280), (468, 248)], 14, 26, 719, "#FFFFFF", 0.45, puffs=False))
    out.append(vignette(D, "#0A0402", 0.4, 0.8))
    # lettering
    txt = [letters(D, 300, 168, "Dosa", SERIF_IT, 168, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 720, max_w=360,
                   shadow="#1A0A04", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 214, "EXTRA SAMBAR, AMMA!", "#FFE6C8", font=JOS, size=21, ls=6, line_w=26, gap=12)]
    return finish_art(D, out, txt, 721, under="#3A2010", edge=2.4, bristle=0.45, grain=0.2)


# ================================================================ 8. jalebi — garam garam, out of the kadai
def spiral_pts(cx, cy, r0, r1, turns, ang0=0, n=60, sq=1.0):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = ang0 + 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * sq))
    return pts


def jalebi(D, cx, cy, R, seed, sq=0.62, turns=2.3, w=None):
    """One jalebi: a crisp tube of batter piped in loops, glossy with syrup."""
    rnd = random.Random(seed)
    w = w or R * 0.3
    pts = spiral_pts(cx, cy, R * 0.12, R, turns, rnd.uniform(0, 6.28), int(40 * turns), sq)
    # a closing loop back across the spiral, the way they are piped
    pts += [(cx + R * 0.2, cy + R * 0.85 * sq), (cx - R * 0.6, cy + R * 0.5 * sq)]
    out = [taper(pts, w * 1.15, w * 1.0, "#7A2A06", 0.9)]
    out.append(taper(pts, w, w * 0.9, "#E8701A"))
    out.append(taper([(x - w * 0.12, y - w * 0.18) for x, y in pts], w * 0.55, w * 0.5, "#F8A030", 0.95))
    out.append(taper([(x - w * 0.2, y - w * 0.28) for x, y in pts], w * 0.16, w * 0.12, "#FFF2C8", 0.75))
    # ridges and syrup beads
    for i in range(0, len(pts) - 2, 3):
        x, y = pts[i]
        out.append(f'<circle cx="{x + rnd.uniform(-2, 2):.1f}" cy="{y + w * 0.2:.1f}" r="{w * 0.12:.1f}" fill="#B8420A" opacity="0.5"/>')
        if rnd.random() < 0.25:
            out.append(f'<circle cx="{x - w * 0.15:.1f}" cy="{y - w * 0.25:.1f}" r="{w * 0.1:.1f}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


@design("jalebi")
def jalebi_d():
    D = Doc2("in-jl")
    art = []
    # the halwai's stall at night: deep warm dark, bokeh of street lamps and string lights
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#1E120E"/>')
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.rad([(0, "#6A2A10", 0.9), (0.6, "#3A160A", 0.5), (1, "#120806", 0)], 0.55, 0.62, 0.7)}"/>')
    rnd = random.Random(801)
    for k in range(26):
        x, y, r = rnd.uniform(-20, 620), rnd.uniform(160, 330), rnd.uniform(8, 26)
        c = rnd.choice(["#FFC860", "#FF9A40", "#FFE8A0", "#F26A3A", "#8AC8F0"])
        art.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{D.rad([(0, c, 0.5), (0.7, c, 0.25), (1, c, 0)])}"/>')
    # the stall's counter of old wood
    art.append(f'<path d="{pdl([(-20, 420), (620, 420), (620, 620), (-20, 620)])}" fill="#3A2214"/>')
    art.append(strokes(D.nid(), pdl([(-20, 420), (620, 420), (620, 620), (-20, 620)]), (-40, 420, 620, 620), ["#5A3A24", "#1E120A", "#7A5034"], 802, n=90, angle=-3, length=(40, 140), width=(2, 6), opacity=(0.15, 0.4)))
    # the fire under the kadai, the black iron belly glowing at its rim
    KX, KY, RX, RY = 340, 372, 214, 74
    art.append(soft_glow(D, KX, KY + 110, 260, "#FF7A1E", 0.75))
    belly = [(KX - RX, KY)] + [(KX + RX * math.cos(math.radians(a)), KY + RY * 0.6 * math.sin(math.radians(a)) + 92 * math.sin(math.radians(a)) ** 2) for a in range(175, 4, -10)] + [(KX + RX, KY)]
    belly = [(KX + RX * math.cos(math.radians(a)), KY + (RY + 70) * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    art.append(modelled(D, belly, ("#5A4A44", "#1E1816", "#060404"), 803, light=(0.0, 1.0), angle=0, n=40, inkw=1.2, hi=0.0, core=0.2, cols=["#3A2E2A", "#0A0808", "#6A3A20"]))
    art.append(clipped(D, smooth_closed(belly), [f'<rect x="{KX - RX}" y="{KY}" width="{2 * RX}" height="160" fill="{D.lin([(0, "#FF8A2A", 0), (0.6, "#FF6A1A", 0.15), (1, "#FFB040", 0.6)])}"/>']))
    art.append(f'<ellipse cx="{KX}" cy="{KY + RY + 66}" rx="{RX * 0.7:.0f}" ry="16" fill="{D.rad([(0, "#FFE080", 0.9), (0.5, "#FF8A2A", 0.6), (1, "#FF6A1A", 0)])}"/>')
    # the rim and the pool of hot ghee, bubbling around the frying spirals
    rim = blob(KX, KY, RX, RY, 804, 0.004, 40)
    art.append(f'<path d="{rim}" fill="#2A2220"/>')
    art.append(f'<path d="{blob(KX, KY - 3, RX - 4, RY - 4, 805, 0.004, 40)}" fill="#5A4A40"/>')
    pool = blob(KX, KY + 4, RX - 18, RY - 14, 806, 0.004, 40)
    g = D.rad([(0, "#FFE48A"), (0.5, "#F2B83A"), (0.85, "#B8701A"), (1, "#5A3008")], 0.45, 0.4, 0.62)
    inner = [f'<path d="{pool}" fill="{g}"/>']
    # ripples and bubbles, the light's reflection
    for k in range(70):
        a_ = rnd.uniform(0, 6.28)
        r_ = math.sqrt(rnd.random()) * 0.92
        x, y = KX + math.cos(a_) * (RX - 20) * r_, KY + 4 + math.sin(a_) * (RY - 16) * r_
        br = rnd.uniform(1.4, 4.2)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{br:.1f}" fill="none" stroke="#FFF6C8" stroke-width="0.9" opacity="0.75"/>')
    for k, (jx, jy, jr) in enumerate(((KX - 110, KY + 6, 34), (KX - 40, KY - 20, 32), (KX + 34, KY + 14, 36), (KX - 80, KY + 30, 26), (KX + 112, KY - 4, 30))):
        inner.append(f'<path d="{blob(jx, jy + 3, jr * 1.1, jr * 0.62, 807 + k, 0.1, 14)}" fill="#8A4A10" opacity="0.4"/>')
        inner.append(jalebi(D, jx, jy, jr, 810 + k, sq=0.55, w=jr * 0.24))
        for b_ in range(8):
            a_ = rnd.uniform(0, 6.28)
            inner.append(f'<circle cx="{jx + math.cos(a_) * jr * 1.15:.1f}" cy="{jy + math.sin(a_) * jr * 0.65:.1f}" r="{rnd.uniform(1.2, 3):.1f}" fill="#FFF8D8" opacity="0.8"/>')
    inner.append(f'<path d="{blob(KX - 60, KY - 30, 70, 10, 816, 0.2, 12, -6)}" fill="#FFFFFF" opacity="0.35"/>')
    art.append(clipped(D, pool, inner))
    art.append(f'<path d="M {KX - RX + 10:.1f} {KY - 14:.1f} Q {KX - 80:.1f} {KY - RY - 2:.1f} {KX + 40:.1f} {KY - RY + 2:.1f}" stroke="#C8B8A8" stroke-width="2.4" fill="none" opacity="0.6"/>')
    # the batter cone hanging in from above: muslin bag, a brass nozzle, a thin stream laying down a new spiral
    cone = [(470, 196), (540, 200), (514, 258), (496, 278), (484, 266)]
    art.append(modelled(D, cone, ("#FFF8E8", "#E8DCC4", "#9A8A70"), 817, light=(-0.6, -0.6), angle=-70, n=16, inkw=1.2, hi=0.4))
    for k in range(4):
        art.append(f'<path d="M {478 + k * 14} {202 + k * 2} q 6 26 12 58" stroke="#B8A888" stroke-width="1" fill="none" opacity="0.6"/>')
    art.append(f'<path d="{smooth_closed([(488, 274), (500, 268), (500, 284), (494, 290), (488, 284)])}" fill="#D8A848"/>')
    st_ = [(494, 290), (488, 316), (474, 342), (460, 362)]
    art.append(taper(st_, 3.2, 2.4, "#FFF0D0", 0.95))
    art.append(clipped(D, pool, [taper(spiral_pts(458, 368, 3, 18, 1.4, 0, 40, 0.5), 5, 5, "#FFE0A0", 0.9)]))
    # steam and smoke curling up through the light
    art.append(pk.steam_plume(D, [(260, 330), (250, 290), (270, 250), (240, 210), (260, 170)], 30, 60, 818, "#FFE8C8", 0.3))
    art.append(pk.steam_plume(D, [(380, 330), (390, 290), (370, 250), (400, 210)], 26, 50, 819, "#FFE8C8", 0.25))
    # the finished jalebis piled on a steel tray in front, dripping syrup
    TX, TY = 170, 548
    art.append(f'<path d="{blob(TX + 20, TY + 20, 170, 22, 820, 0.1, 16)}" fill="#000000" opacity="0.45"/>')
    art.append(pk.metal_ellipse(D, TX, TY, 156, 46, 821, pal=("#F8F0E0", "#B8A898", "#4A3A30"), inner_pal=("#C8B8A8", "#8A7868", "#3A2A20"), rim_w=8))
    piles = [(TX - 70, TY + 2, 30), (TX + 10, TY + 8, 32), (TX + 84, TY, 28), (TX - 30, TY - 18, 30), (TX + 50, TY - 22, 30), (TX + 4, TY - 40, 28), (TX - 90, TY - 16, 24)]
    for k, (jx, jy, jr) in enumerate(sorted(piles, key=lambda q: q[1])):
        art.append(f'<path d="{blob(jx + 4, jy + jr * 0.4, jr * 1.1, jr * 0.4, 822 + k, 0.1, 12)}" fill="#3A1A08" opacity="0.4"/>')
        art.append(jalebi(D, jx, jy, jr, 830 + k, sq=0.62, w=jr * 0.26))
    for k in range(10):
        x = TX - 120 + rnd.uniform(0, 240)
        art.append(f'<circle cx="{x:.1f}" cy="{TY + rnd.uniform(-10, 20):.1f}" r="{rnd.uniform(1.5, 3.5):.1f}" fill="#FFB040" opacity="0.8"/>')
    # a slotted jhara resting on the tray's edge
    art.append(taper([(322, 520), (470, 470)], 5, 4, "#8A8A90"))
    art.append(pk.metal_ellipse(D, 330, 530, 36, 14, 840, rim_w=3))
    for k in range(9):
        art.append(f'<circle cx="{316 + (k % 3) * 12:.1f}" cy="{526 + (k // 3) * 5:.1f}" r="1.8" fill="#2A2420"/>')
    art.append(glaze(D, [(0, "#FFB060", 0.0), (0.6, "#FFB060", 0.0), (1, "#FF8A2A", 0.12)]))
    art.append(vignette(D, "#0A0402", 0.5, 0.78))
    txt = [letters(D, 300, 128, "Jalebi", SERIF_IT, 146, "#FFB43A", ["#FFD070", "#E8801A", "#FFE6A0"], 850, max_w=380,
                   shadow="#3A0E04", soff=(0.022, 0.035), angle=-40, hi="#FFF0C0"),
           sub(300, 174, "GARAM GARAM, FROM THE KADAI", "#FFE6C0", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, art, txt, 851, under="#1E120E", edge=2.4, bristle=0.4, grain=0.18)


# ================================================================ 9. biryani — the handi opened after the dum
def handi(D, cx, rim_y, rx, h, seed, pal=("#F2A06A", "#B85A2A", "#5A2410")):
    """Copper handi: a wide-bellied pot with a flared rim, hammered texture, a reflection of the light."""
    ry = rx * 0.28
    belly = rx * 1.12
    body = [(cx - rx, rim_y), (cx - belly, rim_y + h * 0.35), (cx - belly * 0.92, rim_y + h * 0.7), (cx - rx * 0.6, rim_y + h), (cx + rx * 0.6, rim_y + h),
            (cx + belly * 0.92, rim_y + h * 0.7), (cx + belly, rim_y + h * 0.35), (cx + rx, rim_y)]
    out = [cast(D, cx + 16, rim_y + h + 4, belly * 1.05, 18, strength=0.55, seed=seed)]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{pal[1]}"/>')
    out.append(metal(D, d, cx - belly, cx + belly, pal, 0.6, 0.85))
    rnd = random.Random(seed)
    ham = []
    for _ in range(140):
        x, y = rnd.uniform(cx - belly, cx + belly), rnd.uniform(rim_y + 10, rim_y + h)
        ham.append(f'<path d="{blob(x, y, 3.4, 2.6, rnd.randint(0, 9999), 0.2, 7)}" fill="{rnd.choice([pal[0], pal[0], pal[2]])}" opacity="{rnd.uniform(0.06, 0.14):.2f}"/>')
    out.append(clipped(D, d, ham))
    out.append(ink(d, INK, 2.2, seed, 2, 0.7))
    # rolled brass rim band
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx + 10, ry + 6)}" fill="{BRASS[1]}"/>')
    out.append(metal(D, ellipse_d(cx, rim_y, rx + 10, ry + 6), cx - rx - 10, cx + rx + 10, BRASS, 0.8))
    out.append(ink(ellipse_d(cx, rim_y, rx + 10, ry + 6), INK, 1.6, seed + 1, 1, 0.6))
    return "".join(out), ry


@design("biryani")
def biryani():
    D = Doc2("in-br")
    # deep teal wall, a candle-warm light from the right
    out = [sky(D, [(0, "#1E5A5E"), (1, "#0E3438")], 901, 600, ["#2A6E72", "#0A2A2E", "#3A8084"], 120, angle=-82, sop=(0.06, 0.16))]
    out.append(blooms(902, ["#2E7A7E", "#082226"], 6, (0, 0, 600, 420), (90, 170), (0.08, 0.16)))
    out.append(soft_glow(D, 330, 360, 340, "#FFC070", 0.32))
    out.append(wood_planks(D, 470, 600, 903, DARKWOOD, 3))
    out.append(f'<rect y="466" width="600" height="8" fill="#0A0604" opacity="0.5"/>')
    # the handi and the rice heaped inside
    cx, rim_y, rx = 286, 352, 150
    pot, ry = handi(D, cx, rim_y, rx, 140, 904)
    out.append(pot)
    rice_top = ellipse_d(cx, rim_y + 2, rx + 2, ry + 2)
    opening = blob(cx, rim_y + 2, rx * 0.97, ry * 0.92, 904, 0.004, 32)
    out.append(f'<path d="{opening}" fill="#C8CCD2"/>')
    out.append(f'<path d="{opening}" fill="{D.lin([(0, "#5A6068"), (0.45, "#B8BEC6"), (1, "#E8ECF0")], 0, 0, 0, 1)}"/>')
    rice_d = blob(cx, rim_y + 8, rx * 0.9, ry * 0.72, 905, 0.02, 30)
    out.append(f'<path d="{rice_d}" fill="#F6EED8"/>')
    rnd = random.Random(906)
    grains = []
    for _ in range(520):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rr * rx * 0.9, rim_y + 8 + math.sin(a) * rr * ry * 0.72
        c = rnd.choices(["#FFFDF4", "#F8EED0", "#F6C24A", "#F2A01E", "#E8E0C8", "#E8701A"], [5, 3, 3, 2.4, 2, 0.8])[0]
        ang = rnd.uniform(-40, 40)
        grains.append(f'<path d="{blob(x, y, 4.6, 1.5, rnd.randint(0, 9999), 0.1, 6, ang)}" fill="{c}"/>')
    grains.append(f'<path d="{blob(cx + 30, rim_y + 6, 60, 10, 907, 0.3, 12)}" fill="#F2A01E" opacity="0.35"/>')
    grains.append(f'<path d="{blob(cx - 70, rim_y + 12, 40, 8, 908, 0.3, 12)}" fill="#F6C24A" opacity="0.3"/>')
    grains.append(f'<path d="{blob(cx, rim_y - ry * 0.4, rx * 0.95, ry * 0.5, 909, 0.02, 20)}" fill="#3A2A20" opacity="0.35"/>')
    out.append(clipped(D, rice_d, grains))
    # crisp fried onions, mint, a boiled egg, whole spices
    for k in range(26):
        x, y = cx + rnd.uniform(-110, 110), rim_y + 8 + rnd.uniform(-20, 20)
        out.append(taper([(x, y), (x + rnd.uniform(-8, 8), y + rnd.uniform(-5, 5)), (x + rnd.uniform(-10, 10), y + rnd.uniform(-5, 5))], 3, 1.2, rnd.choice(["#8A4A14", "#A8601E", "#6A3410"]), 0.9))
    for k in range(7):
        x, y = cx + rnd.uniform(-100, 100), rim_y + 6 + rnd.uniform(-18, 16)
        out.append(leaf_simple(D, x, y, 16, 6, rnd.uniform(0, 360), ("#8AD06A", "#3E9A3A", "#1A5A1A"), 910 + k, vein=False, inkw=0.7))
    ex, ey = cx + 40, rim_y + 2
    out.append(painted(D, blob_pts(ex, ey, 24, 17, 920, 0.04, 14), WHITE, 920, sk=0.2, n=6, inkw=1.3, hi=0.4))
    out.append(f'<path d="{blob(ex + 2, ey + 1, 11, 9, 921, 0.08, 10)}" fill="#F6C21C"/><path d="{blob(ex, ey - 1, 5, 4, 922, 0.1, 8)}" fill="#FFE47A"/>')
    out.append(star_anise(D, cx - 70, rim_y + 2, 12, 923, 20))
    out.append(dried_chilli(D, cx - 20, rim_y - 6, 40, 20, 924))
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx + 10, ry + 6)}" fill="none" stroke="#E8ECF0" stroke-width="3" opacity="0.8"/>')
    out.append(ink(rice_top, INK, 0.1, 925, 1, 0))
    # the dough seal torn away and the lid set aside, leaning on the pot
    lid_cx, lid_cy = 486, 418
    lid = ellipse_d(lid_cx, lid_cy, 92, 104)
    out.append(cast(D, lid_cx + 30, 474, 70, 10, strength=0.4, seed=926))
    out.append(f'<path d="{lid}" fill="#B85A2A" transform="rotate(14 {lid_cx} {lid_cy})"/>')
    out.append(f'<g transform="rotate(14 {lid_cx} {lid_cy})">{metal(D, lid, lid_cx - 92, lid_cx + 92, ("#F2A06A", "#B85A2A", "#5A2410"), 0.6, 0.85)}'
               f'<path d="{ellipse_d(lid_cx, lid_cy, 92, 104)}" fill="none" stroke="#F2D8A8" stroke-width="14" opacity="0.95"/>'
               f'<path d="{ellipse_d(lid_cx, lid_cy, 92, 104)}" fill="none" stroke="#C8A06A" stroke-width="3" stroke-dasharray="6 9" opacity="0.6"/>'
               f'{ink(lid, INK, 1.8, 927, 1, 0.6)}<circle cx="{lid_cx}" cy="{lid_cy}" r="14" fill="{BRASS[1]}"/><circle cx="{lid_cx - 4}" cy="{lid_cy - 4}" r="4" fill="#FFF0C0"/></g>')
    for k in range(6):
        a = rnd.uniform(0, 6.28)
        x, y = cx + math.cos(a) * (rx + 18), rim_y + math.sin(a) * (ry + 8)
        out.append(f'<path d="{blob(x, y, 7, 4, 930 + k, 0.3, 8, rnd.uniform(0, 90))}" fill="#F2D8A8"/>')
    out.append(pk.steam_plume(D, [(cx - 30, rim_y - 10), (cx - 50, rim_y - 60), (cx - 10, rim_y - 110), (cx - 60, rim_y - 160)], 40, 70, 931, "#E8F0EC", 0.5))
    out.append(pk.steam_plume(D, [(cx + 50, rim_y - 6), (cx + 70, rim_y - 50), (cx + 40, rim_y - 100)], 30, 50, 932, "#E8F0EC", 0.45))
    out.append(glaze(D, [(0, "#0A2024", 0.25), (0.5, "#0A2024", 0), (1, "#FFC070", 0.12)], 0, 0, 1, 0))
    out.append(vignette(D, "#041012", 0.45, 0.8))
    # lettering
    txt = [letters(D, 300, 150, "Biryani", SERIF_IT, 140, "#FFC86A", ["#FFE0A0", "#E89A2A", "#FFF0C8"], 940, max_w=420,
                   shadow="#061A1C", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 196, "WORTH EVERY MINUTE OF DUM", "#9AE0D8", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, out, txt, 941, under="#0E3438", edge=2.4, bristle=0.45, grain=0.2)


# ================================================================ 10. mango season — a crate of Alphonsos in straw
@design("mango-season")
def mango_season():
    D = Doc2("in-mg")
    out = [sky(D, [(0, "#FBE6C0"), (0.6, "#F6D49A"), (1, "#E8B878")], 1001, 600, ["#FFF0D0", "#E8B070", "#FFE6B0"], 140, angle=-84, sop=(0.06, 0.16))]
    out.append(blooms(1003, ["#E8A860", "#FFF2D8"], 8, (0, 0, 600, 460), (60, 140), (0.08, 0.16)))
    out.append(soft_glow(D, 300, 330, 320, "#FFE08A", 0.4))
    out.append(leaf_shadows(D, 1004, (-20, 160, 620, 440), "#8A4A10", 40, (0.06, 0.13), (18, 40)))
    # the floor: old newspaper spread out to ripen the fruit on
    paper_ = jitter(pk.dens2([(-30, 500), (630, 470), (640, 640), (-30, 640)], 20), 1005, 1.5)
    out.append(f'<path d="{smooth_closed(paper_)}" fill="#E8E0CC"/>')
    np_ = []
    rr = random.Random(1006)
    for k in range(14):
        y = 486 + k * 10
        for c_ in range(4):
            x0_ = -20 + c_ * 165
            np_.append(f'<path d="M {x0_:.1f} {y - c_ * 7:.1f} L {x0_ + rr.uniform(110, 150):.1f} {y - c_ * 7 - 4:.1f}" stroke="#8A8478" stroke-width="2" opacity="0.4"/>')
    np_.append(f'<path d="M -20 486 L 620 456" stroke="#4A4440" stroke-width="5" opacity="0.4"/>')
    out.append(clipped(D, smooth_closed(paper_), np_))
    # a mango branch reaching in from the top right, heavy with fruit
    br_ = [(640, 236), (590, 250), (540, 262), (500, 262)]
    out.append(taper(br_, 9, 4, "#4A3020"))
    rl_ = random.Random(1007)
    for k in range(13):
        t = k / 12
        px, py = 640 - 140 * t, 236 + 26 * t
        a_ = rl_.uniform(110, 190) if k % 2 else rl_.uniform(-40, 30)
        pal_ = ("#9A6A4A", "#7A3A2A", "#3A1A10") if k in (3, 9) else ("#7ABA5A", "#2E7A34", "#124A1E")
        out.append(leaf_simple(D, px, py, rl_.uniform(58, 80), rl_.uniform(11, 15), a_, pal_, 1008 + k, inkw=1.0))
    for k, (hx, hy, L_) in enumerate(((560, 258, 40),)):
        out.append(f'<path d="M {hx} {hy} q 4 {L_ * 0.5:.0f} -2 {L_}" stroke="#4A3020" stroke-width="2" fill="none"/>')
        out.append(mango(D, hx - 4, hy + L_ + 30, 30, -90, 1015 + k))
    # the wooden crate in 3/4, straw spilling out
    x0, x1, top, bot = 108, 492, 360, 520
    out.append(cast(D, 300, bot + 6, 230, 18, strength=0.5, seed=1010))
    back = poly_pts([(x0 + 20, top - 34), (x1 - 20, top - 34), (x1, top), (x0, top)], 10, 1011, 0.4)
    out.append(painted(D, back, ("#C8945A", "#9A6430", "#5A3412"), 1011, sk=0.1, angle=0, n=10, inkw=1.4, hi=0.2))
    rnd = random.Random(1012)
    straw = []
    for _ in range(220):
        x, y = rnd.uniform(x0, x1), rnd.uniform(top - 40, top + 14)
        L = rnd.uniform(10, 26)
        a = rnd.uniform(-0.8, 0.8)
        straw.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * L:.1f} {math.sin(a) * L:.1f}" stroke="{rnd.choice(["#F6DA8A", "#E2B85A", "#C8963A", "#FFF0B8"])}" stroke-width="{rnd.uniform(1.2, 2.4):.1f}" stroke-linecap="round"/>')
    out.append("".join(straw))
    # mangoes nestled in the straw (back row, then front row)
    for k, (x, y, r, a) in enumerate(((176, 316, 46, -20), (272, 306, 50, 10), (372, 310, 48, -8), (446, 322, 40, 25),
                                       (220, 350, 50, 15), (328, 352, 52, -15), (420, 356, 44, 30))):
        out.append(mango(D, x, y, r, a, 1020 + k))
    for _ in range(50):
        x, y = rnd.uniform(x0, x1), rnd.uniform(top - 6, top + 10)
        a = rnd.uniform(-0.6, 0.6)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * 18:.1f} {math.sin(a) * 18:.1f}" stroke="{rnd.choice(["#F6DA8A", "#E2B85A"])}" stroke-width="1.8" stroke-linecap="round"/>')
    # the front slats with a stencilled stamp
    for k in range(3):
        y0 = top + 4 + k * 54
        sl = poly_pts([(x0, y0), (x1, y0), (x1 - 2, y0 + 46), (x0 + 2, y0 + 46)], 10, 1030 + k, 0.5)
        out.append(painted(D, sl, ("#E8B47A", "#C08850", "#6E4A22"), 1030 + k, sdir=(0, 1), sk=0.15, angle=0, n=20, inkw=1.6, hi=0.35))
        for nx in (x0 + 14, x1 - 14):
            out.append(f'<circle cx="{nx}" cy="{y0 + 23}" r="2.6" fill="#4A3020"/>')
    out.append(label(300, top + 89, "RATNAGIRI · GRADE A", JOS, 21, "#7A2A0A", ls=4, max_w=300, extra=' opacity="0.8"'))
    # a whole mango with its leaf, and a katori of aamras with two puffed puris
    out.append(mango(D, 498, 546, 42, -150, 1050, leaf=True))
    out.append(leaf_simple(D, 60, 540, 70, 14, -20, ("#7ABA5A", "#2E7A34", "#124A1E"), 1051, inkw=1.1))
    aam = (f'<path d="{ellipse_d(116, 513, 42, 12)}" fill="#F6A21E"/>'
           f'<path d="{blob(108, 510, 18, 4, 1057, 0.2, 8)}" fill="#FFD86A" opacity="0.85"/>'
           f'<path d="M 128 512 q 6 -2 10 1" stroke="#C8600A" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(steel_bowl(D, 116, 510, 48, 30, 1058, fill=aam))
    out.append(glaze(D, [(0, "#FFF0C8", 0.15), (0.6, "#FFF0C8", 0), (1, "#5A2A08", 0.18)], 0, 0, 1, 1))
    out.append(vignette(D, "#4A2408", 0.3, 0.8))
    txt = [letters(D, 300, 132, "mango season", SERIF_IT, 104, "#D8641A", ["#F28A2A", "#A8400A", "#FFA84A"], 1070, max_w=460,
                   shadow="#FFF6E0", soff=(0.022, 0.035), angle=-40, hi="#FFD0A0"),
           sub(300, 176, "AAM KA MAUSAM · BY THE DOZEN", "#2E6A2A", font=JOS, size=18, ls=4, line_w=18, gap=10)]
    return finish_art(D, out, txt, 1071, under="#F6D49A", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 11. bas, one more roti — the phulka puffing on the flame
def roti(D, cx, cy, rx, ry, seed, puffed=0.0, ghee=False):
    """A round wheat roti: golden-cream, scattered brown char spots; puffed > 0 swells it into a balloon."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, rx, ry, seed, 0.03, 22)
    if puffed:
        pts = [(x, y - puffed * ry * 2.2 * max(0, 1 - ((x - cx) / rx) ** 2) ** 0.6 if y < cy + ry * 0.2 else y) for x, y in pts]
    out = [painted(D, pts, ("#FCEBC0", "#E8C78A", "#A8783A"), seed, sdir=(0.5, 0.8), sk=0.15, angle=-10, n=int(rx * 0.8) + 8,
                   cols=["#FFF6DA", "#C89A5A", "#F2D8A0"], inkw=1.6, hi=0.4)]
    x0, y0, x1, y1 = bbox(pts)
    spots = []
    for _ in range(int(rx * 0.55)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        rr = rnd.uniform(2, 7)
        spots.append(f'<path d="{blob(x, y, rr, rr * 0.7, rnd.randint(0, 9999), 0.3, 8)}" fill="{rnd.choice(["#8A4A14", "#A8601E", "#6A3410"])}" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
        if rnd.random() < 0.3:
            spots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr * 0.4:.1f}" fill="#2A1408" opacity="0.6"/>')
    if ghee:
        spots.append(f'<path d="{blob(cx - rx * 0.1, cy - ry * 0.1, rx * 0.5, ry * 0.4, seed + 5, 0.3, 12)}" fill="#FFF2B0" opacity="0.45"/>')
        spots.append(f'<path d="{blob(cx - rx * 0.25, cy - ry * 0.25, rx * 0.16, ry * 0.08, seed + 6, 0.3, 8)}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(clipped(D, smooth_closed(pts), spots))
    return "".join(out)


@design("bas-one-more-roti")
def bas_one_more_roti():
    D = Doc2("in-rt")
    out = [sky(D, [(0, "#F6DCB0"), (0.6, "#EEC890"), (1, "#D8A870")], 1101, 600, ["#FFF0D0", "#D8A068", "#F8E0B8"], 150, angle=-84, sop=(0.06, 0.16))]
    out.append(blooms(1101, ["#C88A50", "#FFF2D8"], 8, (0, 0, 600, 460), (60, 140), (0.08, 0.16)))
    # a kitchen window behind: lime-washed blue frame, morning outside
    out.append(f'<path d="{hg.org_rect(70, 250, 460, 230, 1102, 0.8, 14, 2)}" fill="#2E6E9A"/>')
    out.append(strokes(D.nid(), hg.org_rect(70, 250, 460, 230, 1102, 0.8, 14, 2), (70, 250, 530, 480), ["#5A9AC8", "#1E4A6E"], 1102, n=40, angle=0, length=(20, 80), width=(2, 5), opacity=(0.15, 0.35)))
    wd_ = hg.org_rect(86, 264, 428, 202, 1103, 0.8, 14, 2)
    out.append(f'<path d="{wd_}" fill="{D.lin([(0, "#BFE0F0"), (0.55, "#FFF4D8"), (1, "#F8DCA8")])}"/>')
    view = [f'<path d="M 86 380 L 200 372 L 200 300 L 260 296 L 262 380 L 330 384 L 330 330 L 420 326 L 422 470 L 86 470 Z" fill="#E8C8A8" opacity="0.8"/>',
            f'<path d="M 330 330 L 420 326 L 422 470 L 330 470 Z" fill="#C89A80" opacity="0.6"/>',
            dab_crown(D, 470, 330, 70, 60, [("#A8C878", "#6A9A4A", "#3A6A2A")], 1140, n=70, size=(5, 10), inkw=0),
            soft_glow(D, 180, 300, 160, "#FFFFFF", 0.8)]
    for k in range(4):
        view.append(f'<rect x="{214 + k * 0}" y="{312 + k * 16}" width="12" height="9" fill="#8A6A5A" opacity="0.5"/>')
    out.append(clipped(D, wd_, view))
    out.append(f'<path d="M 300 264 L 300 466 M 86 360 L 514 360" stroke="#2E6E9A" stroke-width="7"/>')
    rnd0 = random.Random(1104)
    twig = [(86, 300), (160, 312), (230, 300), (290, 318)]
    out.append(clipped(D, hg.org_rect(86, 264, 428, 202, 1103, 0.8, 14, 2), [pline(twig, "#6A4A2A", 3, 1104, 0.8, 1)] +
                       [leaf_simple(D, x + rnd0.uniform(-6, 6), y, rnd0.uniform(22, 34), 5, rnd0.choice([60, 75, 100, 120, 240, 260, 280]), ("#A8D86A", "#5A9A3A", "#2E5A1E"), 1105 + k, vein=False, inkw=0.6)
                        for k, (x, y) in enumerate(catmull(twig, 4)[::1])]))
    # counter
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="#E8D8C0"/>')
    out.append(strokes(D.nid(), pd([(-10, 470), (610, 470), (610, 610), (-10, 610)]), (-40, 470, 610, 600), ["#C8B8A0", "#FFFFFF"], 1106, n=60, angle=0, length=(40, 140), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(f'<path d="M -10 470 L 610 470" stroke="#B8A890" stroke-width="4"/>')
    # gas burner on the right with the phulka ballooning over the flame, held in tongs
    bx, by = 400, 520
    out.append(modelled(D, poly_pts([(296, 486), (520, 486), (526, 556), (290, 556)], 8, 1107, 0.3), ("#6A6E78", "#2E323A", "#0E1014"), 1107, light=(-0.6, -0.8), angle=0, n=30, inkw=1.4, hi=0.35))
    out.append(f'<path d="M 300 552 L 520 552" stroke="#C8CCD2" stroke-width="4" opacity="0.7"/>')
    for k, kx in enumerate((330, 486)):
        out.append(f'<path d="{blob(kx, 540, 9, 7, 1150 + k, 0.03, 12)}" fill="#E8E4DC"/><path d="M {kx - 5} 538 L {kx + 5} 542" stroke="#2A2A2E" stroke-width="2"/>')
    out.append(f'<path d="{pd([(294, 482), (522, 482), (523, 492), (293, 492)])}" fill="#D8DDE2"/>')
    out.append(f'<path d="{ellipse_d(bx, 482, 52, 10)}" fill="#1A1A1E"/>')
    out.append(soft_glow(D, bx, 440, 120, "#FFB040", 0.55))
    out.append(blue_flame(D, bx, 480, 46, 1108))
    for k in range(4):
        a_ = math.radians(k * 90 + 45)
        out.append(f'<path d="M {bx + math.cos(a_) * 30:.1f} {480 + math.sin(a_) * 6:.1f} L {bx + math.cos(a_) * 70:.1f} {478 + math.sin(a_) * 12:.1f}" stroke="#3A3A40" stroke-width="5" stroke-linecap="round"/>')
    out.append(roti(D, bx, 430, 92, 26, 1109, puffed=0.85))
    out.append(f'<path d="{blob(bx - 30, 400, 40, 16, 1109, 0.2, 12)}" fill="#FFFFFF" opacity="0.28"/>')
    out.append(pk.steam_plume(D, [(bx - 10, 380), (bx - 30, 340), (bx, 300), (bx - 20, 266)], 16, 34, 1112, "#FFFFFF", 0.55, puffs=False))
    # chimta (tongs) gripping the roti from the right: two flat steel blades joined at a ring
    for k, (y0, y1, c) in enumerate(((426, 392, "#9AA2AC"), (440, 402, "#7A828C"))):
        blade = [(bx + 76, y0), (bx + 120, y0 - 12), (566, y1)]
        out.append(taper(blade, 7, 8, INK, 0.6))
        out.append(taper(blade, 5.4, 6.4, c))
        out.append(taper([(x, y - 1.6) for x, y in blade], 1.4, 1.6, "#FFFFFF", 0.8))
    out.append(f'<circle cx="572" cy="396" r="9" fill="none" stroke="#8A929C" stroke-width="4.4"/><circle cx="572" cy="396" r="9" fill="none" stroke="{INK}" stroke-width="1" opacity="0.5"/>')
    # the roti dabba: steel casserole lined with a checked cloth, a stack glistening with ghee
    cx, rim = 168, 470
    cloth = [(cx - 112, rim - 6), (cx - 130, rim - 40), (cx - 90, rim - 30), (cx - 40, rim - 48), (cx + 20, rim - 30), (cx + 80, rim - 50), (cx + 124, rim - 30), (cx + 112, rim - 6)]
    out.append(steel_bowl(D, cx, rim, 120, 70, 1110))
    for k in range(4):
        out.append(roti(D, cx - 4 + k * 2, rim - 6 - k * 7, 104, 24, 1111 + k, ghee=(k == 3)))
    out.append(bp.cloth(D, [(cx - 118, rim - 2), (cx - 146, rim - 30), (cx - 128, rim - 66), (cx - 100, rim - 44), (cx - 96, rim + 4)], "#D6342A", 1120, cell=9, rot_=20, inkw=1.4))
    out.append(bp.cloth(D, [(cx + 116, rim - 2), (cx + 92, rim - 40), (cx + 120, rim - 58), (cx + 150, rim - 26), (cx + 120, rim + 8)], "#D6342A", 1121, cell=9, rot_=-20, inkw=1.4))
    # a tiny katori of ghee with a spoon
    out.append(steel_bowl(D, 282, 540, 34, 22, 1121, fill=f'<path d="{ellipse_d(282, 541, 29, 8)}" fill="#F8D870"/>'))
    out.append(taper([(282, 538), (318, 506), (330, 494)], 4, 3, "#9AA2AC"))
    # lettering: a small "Bas," then the big line
    out.append(glaze(D, [(0, "#FFF4D8", 0.12), (0.6, "#FFF4D8", 0), (1, "#4A2410", 0.2)], 0, 0, 1, 1))
    out.append(vignette(D, "#3A1E0A", 0.3, 0.8))
    txt = [letters(D, 300, 92, "Bas,", SERIF_IT, 74, "#2E6E9A", ["#4A8AC0", "#1E4A6E", "#6AA8D8"], 1130, max_w=200,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8E0F0"),
           letters(D, 300, 182, "one more roti", SERIF_IT, 96, "#B8401A", ["#D85A2A", "#7A1E0A", "#F07A4A"], 1131, max_w=470,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFC0A0"),
           sub(300, 224, "MUMMY, EVERY SINGLE MEAL", "#6A3A1A", font=JOS, size=17, ls=4, line_w=18, gap=10)]
    return finish_art(D, out, txt, 1132, under="#EEC890", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 12. filter kaapi — davara and tumbler, frothing over
@design("filter-kaapi")
def filter_kaapi():
    D = Doc2("in-fk")
    # red-oxide floor and a kolam drawn in rice flour; a brass lamp-glow
    out = [sky(D, [(0, "#A8402A"), (0.6, "#8A2E1C"), (1, "#5A1A0E")], 1201, 600, ["#C85A3A", "#4A1006", "#D8704A", "#7A2414"], 180, angle=-6, sop=(0.08, 0.2))]
    out.append(blooms(1201, ["#D8704A", "#3A0A04"], 10, (0, 0, 600, 600), (60, 140), (0.08, 0.16)))
    # morning sun through a window grille, thrown across the polished red-oxide floor
    for k in range(5):
        x0_ = -80 + k * 120
        out.append(f'<path d="M {x0_} -20 L {x0_ + 70} -20 L {x0_ + 300} 640 L {x0_ + 230} 640 Z" fill="#FFD8A0" opacity="0.14"/>')
    out.append(f'<path d="M -20 230 L 640 160 L 640 178 L -20 248 Z" fill="#3A0A04" opacity="0.18"/>')
    out.append(soft_glow(D, 300, 330, 360, "#FFB070", 0.3))

    # the davara (wide bowl) with the tumbler standing in it
    dcx, drim = 300, 468
    out.append(cast(D, dcx + 14, drim + 72, 170, 20, strength=0.55, seed=1202))
    dav_fill = (f'<path d="{ellipse_d(dcx, drim + 3, 140, 30)}" fill="#C88A54"/>'
                f'<path d="{blob(dcx - 30, drim, 70, 12, 1203, 0.2, 12)}" fill="#E8C49A" opacity="0.8"/>')
    out.append(steel_bowl(D, dcx, drim, 152, 70, 1204, fill=dav_fill, ry=40))
    tx, trx = dcx + 6, 58
    ttop = drim + 22 - 206
    t_, _ = pk.metal_cyl(D, tx, ttop, drim + 22, trx, trx * 0.26, 1205, light=-1, taper_=0.2, gloss=1.0, env=("#F8E0C8", "#E87A4A"))
    out.append(t_)
    for k in (0.22, 0.85):
        y = ttop + 206 * k
        w_ = trx * (1 - 0.2 * k)
        out.append(f'<path d="M {tx - w_:.1f} {y:.1f} Q {tx:.1f} {y + 12:.1f} {tx + w_:.1f} {y:.1f}" stroke="#5E6670" stroke-width="1.6" fill="none" opacity="0.55"/>')
    out.append(pk.metal_ellipse(D, tx, ttop, trx, trx * 0.26, 1215, rim_w=3))
    # froth heaped above the rim, a drip running down
    foam = blob_pts(tx, ttop - 6, trx + 4, 22, 1206, 0.12, 18)
    out.append(painted(D, foam, ("#FFF8EC", "#F2DCC0", "#C8A07A"), 1206, sdir=(0.5, 0.8), sk=0.18, angle=-20, n=16, inkw=1.4, hi=0.5))
    rnd = random.Random(1207)
    for k in range(26):
        x, y = tx + rnd.uniform(-trx * 0.8, trx * 0.8), ttop - 6 + rnd.uniform(-12, 10)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.2, 3.2):.1f}" fill="none" stroke="#C8A07A" stroke-width="1" opacity="0.6"/>')
    out.append(taper([(tx + trx - 6, ttop + 6), (tx + trx - 4, ttop + 40), (tx + trx - 7, ttop + 62)], 7, 3, "#D8B08A", 0.95))
    out.append(pk.steam_plume(D, [(tx, ttop - 20), (tx - 16, ttop - 60), (tx + 6, ttop - 96)], 16, 30, 1208, "#FFFFFF", 0.6, puffs=False))
    # the two-tier brass filter at the left, and a string of jasmine on the right
    fx, fb = 120, 508
    out.append(cast(D, fx + 10, fb + 4, 56, 9, strength=0.45, seed=1209))
    for k, (y0, y1, w) in enumerate(((fb - 74, fb, 84), (fb - 150, fb - 70, 80))):
        p = poly_pts([(fx - w / 2, y0), (fx + w / 2, y0), (fx + w / 2, y1), (fx - w / 2, y1)], 8, 1210 + k, 0.3)
        out.append(f'<path d="{smooth_closed(p)}" fill="{BRASS[1]}"/>' + metal(D, smooth_closed(p), fx - w / 2, fx + w / 2, BRASS, 0.8, 0.8) + ink(smooth_closed(p), INK, 1.6, 1212 + k, 1, 0.6))
        out.append(f'<path d="{ellipse_d(fx, y0, w / 2, 8)}" fill="{BRASS[2]}" opacity="0.7"/>')
    out.append(painted(D, ell_pts(fx, fb - 154, 40, 10, 0, 360, 16), BRASS, 1214, sk=0.1, n=4, inkw=1.4, hi=0.4))
    out.append(f'<circle cx="{fx}" cy="{fb - 166}" r="8" fill="{BRASS[1]}" stroke="{INK}" stroke-width="1.2"/>')
    jas = [(430, 560), (470, 540), (510, 548), (548, 528)]
    out.append(pline(jas, "#3E6A2A", 1.6, 1215, 0.8, 1))
    for i, (x, y) in enumerate(catmull(jas, 4)[::2]):
        for k in range(2):
            px, py = x + rnd.uniform(-5, 5), y + rnd.uniform(-5, 5)
            out.append(jasmine(D, px, py, 9, 1216 + i * 3 + k))
        if i % 2:
            out.append(f'<path d="{blob(x, y - 8, 4, 7, 1230 + i, 0.2, 8)}" fill="#F6E8F0"/>')
    # lettering
    out.append(vignette(D, "#1A0402", 0.45, 0.8))
    txt = [letters(D, 300, 140, "filter kaapi", SERIF_IT, 116, "#FFE6B8", ["#FFFFFF", "#F2C890", "#FFF2D8"], 1240, max_w=460,
                   shadow="#4A0E04", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 184, "DECOCTION FIRST, THEN THE WORLD", "#FFD8A8", font=JOS, size=18, ls=4, line_w=18, gap=10)]
    return finish_art(D, out, txt, 1241, under="#8A2E1C", edge=2.4, bristle=0.45, grain=0.2)


# ================================================================ 13. it's not ice cream — the tub in the freezer is dal
def frost(seed, box, n=60):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(3, 7)
        out.append(f'<path d="M {x - r:.1f} {y:.1f} L {x + r:.1f} {y:.1f} M {x:.1f} {y - r:.1f} L {x:.1f} {y + r:.1f} M {x - r * 0.7:.1f} {y - r * 0.7:.1f} L {x + r * 0.7:.1f} {y + r * 0.7:.1f} M {x - r * 0.7:.1f} {y + r * 0.7:.1f} L {x + r * 0.7:.1f} {y - r * 0.7:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    return "".join(out)


def plastic_tub(D, cx, base, w, h, seed, band="#E8607A", lid=("#F8B8C8", "#E8607A", "#9A2A40"), tape=None, open_=False, fill=None, frost=0.0, light=-1):
    """A reused ice-cream tub: slightly tapered cream plastic with a coloured band, its lid on (or off), a strip of
    masking tape with a marker label, and frost on the shoulders."""
    rx, ry = w / 2, w * 0.13
    out = [f'<path d="{blob(cx + w * 0.12, base + 2, w * 0.6, ry * 0.8, seed, 0.1, 14)}" fill="#3A5A7A" opacity="0.35"/>']
    body, bd = pk.metal_cyl(D, cx, base - h, base, rx, ry, seed, pal=("#FFFFFF", "#F2EAD8", "#B8AC98"), env=("#E8F4FF", "#C8D8E8"), light=light,
                            taper_=0.1, gloss=0.35, inkw=1.2)
    out.append(body)
    cid = D.clip(f'<path d="{bd}"/>')
    bt = base - h * 0.32
    out.append(f'<g {cid}><path d="M {cx - w:.1f} {bt:.1f} Q {cx:.1f} {bt + ry * 1.6:.1f} {cx + w:.1f} {bt:.1f} L {cx + w:.1f} {bt + h * 0.12:.1f} Q {cx:.1f} {bt + h * 0.12 + ry * 1.6:.1f} {cx - w:.1f} {bt + h * 0.12:.1f} Z" fill="{band}" opacity="0.9"/></g>')
    if tape:
        ty = base - h * 0.66
        tp = [(cx - w * 0.3, ty - 9), (cx + w * 0.32, ty - 8), (cx + w * 0.3, ty + 10), (cx - w * 0.32, ty + 9)]
        out.append(f'<path d="{smooth_closed(jitter(pk.dens2(tp, 6), seed, 0.6))}" fill="#F4E4B0" opacity="0.95"/>')
        out.append(f'<text x="{cx:.1f}" y="{ty + 6:.1f}" text-anchor="middle" {JOS} font-size="{fit_size(tape, JOS, 17, w * 0.58)}" fill="#1E2A4A" transform="rotate(-2 {cx:.1f} {ty:.1f})">{tape}</text>')
    if open_:
        out.append(pk.metal_ellipse(D, cx, base - h, rx, ry, seed + 3, pal=("#FFFFFF", "#F2EAD8", "#A89C88"), inner_pal=("#F8F0E0", "#E8DCC8", "#B8A890"), rim_w=3))
        if fill:
            out.append(fill)
    else:
        lidp = [(cx - rx - 3, base - h + 2)] + [(cx + (rx + 3) * math.cos(math.radians(a)), base - h - 4 + ry * math.sin(math.radians(a))) for a in range(180, 361, 15)] + [(cx + rx + 3, base - h + 2)]
        lidp = [(cx + (rx + 3) * math.cos(math.radians(a)), base - h - 4 + (ry + 1) * math.sin(math.radians(a))) for a in range(0, 360, 12)]
        out.append(f'<path d="{smooth_closed([(x, y + 7) for x, y in lidp])}" fill="{lid[2]}"/>')
        out.append(modelled(D, lidp, lid, seed + 4, light=(-0.6, -0.8), angle=0, n=10, inkw=1.0, hi=0.4))
    if frost:
        rnd = random.Random(seed + 9)
        fr = []
        for _ in range(int(30 * frost)):
            a = rnd.uniform(math.pi, 2 * math.pi)
            fr.append(f'<circle cx="{cx + math.cos(a) * rx * rnd.uniform(0.6, 1):.1f}" cy="{base - h - 3 + math.sin(a) * ry * 1.1 + rnd.uniform(-2, 4):.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
        out.append("".join(fr))
    return "".join(out)


@design("its-not-ice-cream")
def its_not_ice_cream():
    D = Doc2("in-ic")
    art = []
    # inside the freezer: icy back wall and side walls in perspective, cold blue light from the top
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#C8DCEC"/>')
    back = [(110, 170), (490, 170), (490, 470), (110, 470)]
    lw = [(-20, -20), (110, 170), (110, 470), (-20, 640)]
    rw = [(620, -20), (490, 170), (490, 470), (620, 640)]
    top_ = [(-20, -20), (620, -20), (490, 170), (110, 170)]
    flr = [(110, 470), (490, 470), (620, 640), (-20, 640)]
    for poly, cols in ((back, [(0, "#A8C2D8"), (1, "#7E9AB4")]), (lw, [(0, "#7A98B4"), (1, "#B8D0E4")]), (rw, [(0, "#6A88A6"), (1, "#A8C2D8")]),
                       (top_, [(0, "#E8F2FA"), (1, "#C8DCEC")]), (flr, [(0, "#9AB4CC"), (1, "#D8E8F4")])):
        art.append(f'<path d="{pdl(poly)}" fill="{D.lin(cols)}"/>')
        x0, y0, x1, y1 = bbox(poly)
        art.append(strokes(D.nid(), pdl(poly), (x0, y0, x1, y1), ["#FFFFFF", "#9AB4CC", "#E8F4FF"], int(x0 + y0 + 900), n=50, angle=-90 if poly is not flr else 0, length=(20, 80), width=(2, 6), opacity=(0.1, 0.3)))
    art.append(soft_glow(D, 300, 186, 240, "#FFFFFF", 0.75))
    art.append(soft_glow(D, 300, 186, 60, "#FFFFFF", 0.9))
    # frost crusted along the edges, crystals feathering the corners
    rnd = random.Random(1301)
    fr = []
    for edge in ((-20, -20, 110, 170), (620, -20, 490, 170), (110, 170, 490, 170), (110, 470, -20, 640), (490, 470, 620, 640)):
        x0, y0, x1, y1 = edge
        for k in range(60):
            t = rnd.random()
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            fr.append(f'<path d="{blob(x + rnd.uniform(-8, 8), y + rnd.uniform(-8, 8), rnd.uniform(3, 9), rnd.uniform(2, 6), rnd.randint(0, 9999), 0.3, 8)}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    for k in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(180, 600)
        L_ = rnd.uniform(3, 7)
        fr.append(f'<path d="M {x - L_:.1f} {y:.1f} L {x + L_:.1f} {y:.1f} M {x:.1f} {y - L_:.1f} L {x:.1f} {y + L_:.1f} M {x - L_ * 0.7:.1f} {y - L_ * 0.7:.1f} L {x + L_ * 0.7:.1f} {y + L_ * 0.7:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    art.append("".join(fr))
    # the wire shelf
    for k in range(9):
        x = 110 + k * 47.5
        xb = -20 + k * 80
        art.append(f'<path d="M {x:.1f} 360 L {xb:.1f} 470" stroke="#8AA0B4" stroke-width="2" opacity="0.7"/>')
    art.append(f'<path d="M 60 410 L 540 410" stroke="#8AA0B4" stroke-width="2.4" opacity="0.7"/>')
    # the back row of tubs, labelled in marker on masking tape
    art.append(plastic_tub(D, 186, 372, 136, 104, 1302, band="#5A9A5A", lid=("#C8E8B8", "#6AAA6A", "#2A5A2A"), tape="SAMBAR", frost=1.0))
    art.append(plastic_tub(D, 186, 262, 128, 92, 1303, band="#4A7AC8", lid=("#B8D0F8", "#4A7AC8", "#1A3A7A"), tape="RAJMA", frost=1.0))
    art.append(plastic_tub(D, 428, 372, 136, 104, 1304, band="#E89A3A", lid=("#FFD8A0", "#E89A3A", "#8A4A10"), tape="CHHOLE", frost=1.0))
    # the open "vanilla" tub in front: it is dal, frozen solid, tadka and coriander suspended in it
    dal = (f'<path d="{blob(302, 404, 70, 18, 1305, 0.02, 24)}" fill="#E8B830"/>'
           f'<path d="{blob(296, 400, 56, 12, 1306, 0.1, 20)}" fill="#F6D060" opacity="0.8"/>')
    rr = random.Random(1307)
    for k in range(30):
        a_ = rr.uniform(0, 6.28)
        r_ = rr.uniform(0, 0.9)
        x, y = 302 + math.cos(a_) * 66 * r_, 404 + math.sin(a_) * 15 * r_
        c = rr.choice(["#C83A1A", "#3E8A2A", "#4A2A10", "#FFFFFF", "#8A5A10"])
        dabs_ = f'<path d="{blob(x, y, rr.uniform(1.4, 3), rr.uniform(1, 2), rr.randint(0, 999), 0.3, 6)}" fill="{c}" opacity="0.9"/>'
        dal += dabs_
    dal += f'<path d="{blob(302, 404, 70, 18, 1308, 0.02, 24)}" fill="#E8F4FF" opacity="0.28"/>'
    art.append(plastic_tub(D, 302, 520, 160, 112, 1309, band="#E8607A", open_=True, fill=dal, frost=0.5))
    # its printed label (a cone and the word)
    art.append(f'<text x="318" y="484" text-anchor="middle" {SERIF_IT} font-size="28" fill="#C83A5A">Vanilla</text>')
    cone = [(248, 466), (268, 466), (258, 494)]
    art.append(f'<path d="{smooth_closed(cone)}" fill="#E8B060"/><path d="{blob(258, 462, 11, 8, 1310, 0.15, 10)}" fill="#FFF4E8"/>')
    # its lid propped against it, a spoon left in the frost
    lid_ = blob(462, 540, 74, 22, 1311, 0.01, 30, -12)
    art.append(f'<path d="{blob(470, 548, 76, 22, 1312, 0.01, 30, -12)}" fill="#9A2A40"/>')
    art.append(f'<path d="{lid_}" fill="{D.lin([(0, "#F8B8C8"), (1, "#C84A64")])}"/>')
    art.append(f'<path d="{blob(462, 540, 56, 15, 1313, 0.01, 30, -12)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
    # cold breath spilling out of the freezer
    art.append(haze_band(D, 600, 120, "#FFFFFF", 0.5))
    art.append(pk.steam_plume(D, [(80, 590), (140, 570), (220, 586), (330, 575), (450, 588), (560, 572)], 40, 50, 1314, "#FFFFFF", 0.45, puffs=True))
    art.append(vignette(D, "#3A5A7A", 0.3, 0.8))
    txt = [letters(D, 300, 100, "It's not ice cream", SERIF_IT, 76, "#1E3A6A", ["#2E4E8A", "#0E1E40", "#4A6AA8"], 1320, max_w=470,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8D8F0"),
           sub(300, 138, "IT'S DAL. IT'S ALWAYS DAL.", "#B83A4A", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, art, txt, 1321, under="#C8DCEC", edge=2.0, bristle=0.35, grain=0.14)


# ================================================================ 14. thoda adjust karo — the suitcase going home to India
@design("thoda-adjust-karo")
def thoda_adjust_karo():
    D = Doc2("in-ta")
    cam = Cam3((60, 210, 130), (-8, 0, 38), f=860, cx=300, cy=372)
    L3 = (0.35, 0.6, 0.72)
    art = []
    # the bedroom at night: a warm plaster wall lit by the bedside lamp on the right
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#C88A5E"/>')
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.rad([(0, "#FFE2B0", 0.95), (0.45, "#E8A870", 0.45), (1, "#5A2A18", 0.55)], 0.86, 0.42, 0.85)}"/>')
    art.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-40, -10, 620, 610), ["#F2C890", "#A8683E", "#FFE0B8"], 1401, n=150, angle=-80, length=(30, 90), width=(3, 9), opacity=(0.07, 0.18)))
    # a framed photo of the family above the headboard
    fr = [(412, 170), (490, 164), (492, 234), (414, 240)]
    art.append(f'<path d="{smooth_closed(shift(fr, 4, 6))}" fill="#3A1A0A" opacity="0.35"/>')
    art.append(modelled(D, pk.dens2(fr, 8), ("#C8946A", "#7A4A26", "#3A1A0A"), 1402, light=(0.6, -0.6), angle=0, n=10, inkw=1.2, hi=0.3))
    inner_ = [(420, 176), (482, 171), (484, 228), (422, 233)]
    art.append(f'<path d="{smooth_closed(inner_)}" fill="{D.lin([(0, "#F4E0C0"), (1, "#C89A70")])}"/>')
    art.append(clipped(D, smooth_closed(inner_), [f'<path d="M 420 214 L 444 190 L 462 206 L 474 196 L 486 214 L 486 240 L 420 240 Z" fill="#6A8A6A"/>',
                                                   f'<circle cx="466" cy="186" r="6" fill="#FFF0C0"/>',
                                                   f'<path d="M 420 224 Q 452 216 486 226 L 486 240 L 420 240 Z" fill="#3E6A4A"/>']))
    # the headboard and the bed, its block-printed sheet in perspective
    hb = [cam(p_) for p_ in ((-260, -62, 0), (260, -62, 0), (260, -62, 30), (-260, -62, 30))]
    art.append(modelled(D, pk.dens2(hb, 10), ("#A86A3E", "#6A3A1C", "#2A140A"), 1404, light=(0.7, -0.5), angle=0, n=40, inkw=1.4, hi=0.3))
    bed = [cam(p_) for p_ in ((-260, -60, 0), (260, -60, 0), (260, 120, 0), (-260, 120, 0))]
    bd = pdl(bed)
    art.append(f'<path d="{bd}" fill="#F6ECD8"/>')
    motifs = []
    rr = random.Random(1405)
    for i in range(-13, 14):
        for j in range(-3, 9):
            x, y = i * 20 + (10 if j % 2 else 0), j * 20
            c = cam((x, y, 0.2))
            sc_ = cam.f / cam.depth((x, y, 0)) * 0.9
            col = "#C8342A" if (i + j) % 2 else "#2A3A7A"
            for k in range(5):
                a_ = math.radians(k * 72)
                motifs.append(f'<ellipse cx="{c[0] + math.cos(a_) * 3.2 * sc_:.1f}" cy="{c[1] + math.sin(a_) * 1.8 * sc_:.1f}" rx="{2.2 * sc_:.1f}" ry="{1.3 * sc_:.1f}" fill="{col}" opacity="0.75"/>')
            motifs.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{1.0 * sc_:.1f}" fill="#E8A21E"/>')
    motifs.append(f'<path d="{bd}" fill="{D.lin([(0, "#3A1A0A", 0.25), (0.5, "#FFF0D0", 0.1), (1, "#3A1A0A", 0.25)], 0, 0, 1, 0)}"/>')
    for k in range(5):
        y0_ = 10 + k * 26
        f0, f1 = cam((-260, y0_, 0)), cam((260, y0_ + 10, 0))
        motifs.append(f'<path d="M {f0[0]:.1f} {f0[1]:.1f} Q {(f0[0] + f1[0]) / 2:.1f} {(f0[1] + f1[1]) / 2 + 6:.1f} {f1[0]:.1f} {f1[1]:.1f}" stroke="#5A3A2A" stroke-width="{3 + k}" fill="none" opacity="0.08"/>')
    art.append(clipped(D, bd, motifs))
    # the suitcase's shadow on the sheet, cast away from the lamp
    sh = [cam(p_) for p_ in ((24, -13, 0), (-24, -13, 0), (-70, -40, 0), (-60, 20, 0), (-24, 14, 0))]
    art.append(f'<path d="{smooth_closed(sh)}" fill="#3A1A10" opacity="0.32"/>')
    # piles waiting their turn: folded saris on the left, a mithai box, snack packets, a steel tiffin
    for k, (c1, c2) in enumerate((("#2A4A9A", "#F2E6D0"), ("#F2701E", "#7A2A8A"), ("#2E7A5A", "#E8C060"), ("#D6246E", "#F6C21C"))):
        bx_ = pk.box3(D, cam, (60, 16, k * 6), (36, 28, 6), 1406 + k, (lt(c1, 0.3), c1, dk(c1, 0.4)), light=L3, inkw=0.8, tex=False)
        art.append(bx_)
        e0, e1 = cam((42, 30.5, k * 6 + 3)), cam((78, 30.5, k * 6 + 3))
        art.append(f'<path d="M {e0[0]:.1f} {e0[1]:.1f} L {e1[0]:.1f} {e1[1]:.1f}" stroke="{c2}" stroke-width="2" opacity="0.9"/>')
    mb = {}
    art.append(pk.box3(D, cam, (-52, 20, 0), (28, 22, 8), 1412, ("#FFE8A0", "#F2C24A", "#8A6010"), light=L3, faces_out=mb, inkw=1.0, tex=False))
    if "top" in mb:
        tp_ = mb["top"][1]
        x0_, y0_, x1_, y1_ = bbox(tp_)
        art.append(f'<path d="{blob((x0_ + x1_) / 2, (y0_ + y1_) / 2, (x1_ - x0_) * 0.22, (y1_ - y0_) * 0.25, 1413, 0.1, 12)}" fill="#C8302A" opacity="0.8"/>')
    # a three-tier steel tiffin carrier waiting to be packed
    tb_ = cam((-66, 52, 0))
    tw_ = cam.f / cam.depth((-66, 52, 0)) * 9
    for k in range(3):
        yb_ = tb_[1] - k * tw_ * 0.95
        body_, _ = pk.metal_cyl(D, tb_[0], yb_ - tw_ * 0.9, yb_, tw_, tw_ * 0.3, 1430 + k, light=1, gloss=0.8, inkw=1.0)
        art.append(body_)
    art.append(pk.metal_ellipse(D, tb_[0], tb_[1] - tw_ * 2.85 - tw_ * 0.9, tw_, tw_ * 0.3, 1433, rim_w=2))
    art.append(f'<path d="M {tb_[0] - tw_ * 1.05:.1f} {tb_[1] - tw_ * 0.4:.1f} L {tb_[0] - tw_ * 1.05:.1f} {tb_[1] - tw_ * 4.4:.1f} Q {tb_[0]:.1f} {tb_[1] - tw_ * 5.4:.1f} {tb_[0] + tw_ * 1.05:.1f} {tb_[1] - tw_ * 4.4:.1f} L {tb_[0] + tw_ * 1.05:.1f} {tb_[1] - tw_ * 0.4:.1f}" stroke="#8A929C" stroke-width="3" fill="none"/>')
    # the suitcase: cobalt hard shell, ribbed, bulging, an orange strap, spinner wheels
    fo = {}
    sc = (0, 0, 4)
    for wx, wy in ((-21, 11), (21, 11), (-21, -11), (21, -11)):
        wp = cam((wx, wy, 2))
        art.append(f'<circle cx="{wp[0]:.1f}" cy="{wp[1]:.1f}" r="5.5" fill="#1A1A1E"/><circle cx="{wp[0] - 1.4:.1f}" cy="{wp[1] - 1.4:.1f}" r="1.8" fill="#6A6A70"/>')
    art.append(pk.box3(D, cam, sc, (48, 26, 72), 1415, ("#6A9AF0", "#1E4AB8", "#0A1A50"), light=L3, faces_out=fo, round_=1, inkw=1.4))
    if "front" in fo:
        _, _, P3 = fo["front"]
        for k in range(1, 5):
            t = k / 5
            a_ = cam((P3[0][0] + (P3[1][0] - P3[0][0]) * t, 13.4, 8))
            b_ = cam((P3[0][0] + (P3[1][0] - P3[0][0]) * t, 13.4, 72))
            art.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#0A1A50" stroke-width="2.2" opacity="0.45"/>')
            art.append(f'<path d="M {a_[0] - 2:.1f} {a_[1]:.1f} L {b_[0] - 2:.1f} {b_[1]:.1f}" stroke="#8AB0F8" stroke-width="1.2" opacity="0.55"/>')
        bul = cam((0, 14, 40))
        art.append(f'<path d="{blob(bul[0] + 14, bul[1] - 20, 40, 90, 1416, 0.1, 16, -4)}" fill="{D.rad([(0, "#C8DCFF", 0.35), (1, "#C8DCFF", 0)])}"/>')
    zip_ = [cam((24, 0, z)) for z in range(6, 76, 6)] + [cam((x, 0, 76)) for x in range(24, -25, -6)]
    art.append(f'<path d="{smooth_open(zip_)}" fill="none" stroke="#0A1030" stroke-width="2.4"/>')
    art.append(f'<path d="{smooth_open(zip_)}" fill="none" stroke="#C8C8D0" stroke-width="0.8" stroke-dasharray="2 2"/>')
    # a sari pallu and a sock escaping the zip
    zp = cam((24.5, 0, 30))
    art.append(f'<path d="{smooth_closed([(zp[0], zp[1] - 8), (zp[0] - 30, zp[1] + 6), (zp[0] - 34, zp[1] + 30), (zp[0] - 20, zp[1] + 26), (zp[0] - 6, zp[1] + 10)])}" fill="#D6246E"/>')
    art.append(f'<path d="M {zp[0] - 30:.1f} {zp[1] + 10:.1f} L {zp[0] - 32:.1f} {zp[1] + 28:.1f}" stroke="#F6C21C" stroke-width="2.4"/>')
    zp2 = cam((24.5, 0, 60))
    art.append(f'<path d="{smooth_closed([(zp2[0], zp2[1] - 4), (zp2[0] - 18, zp2[1] + 2), (zp2[0] - 22, zp2[1] + 14), (zp2[0] - 4, zp2[1] + 8)])}" fill="#F2F0E8" stroke="{INK}" stroke-width="0.8"/>')
    st = [cam((24.4, -13, 38)), cam((24.4, 13.4, 38)), cam((-24.4, 13.4, 38))]
    st2 = [cam((24.4, -13, 44)), cam((24.4, 13.4, 44)), cam((-24.4, 13.4, 44))]
    art.append(f'<path d="{pdl(st + st2[::-1])}" fill="#F2701E"/>')
    art.append(f'<path d="M {st[1][0]:.1f} {st[1][1]:.1f} L {st[2][0]:.1f} {st[2][1]:.1f}" stroke="#A84010" stroke-width="1.4"/>')
    bk = cam((-4, 13.6, 41))
    art.append(f'<rect x="{bk[0] - 8:.1f}" y="{bk[1] - 9:.1f}" width="16" height="18" rx="2" fill="none" stroke="#1A1A1E" stroke-width="3"/>')
    # a luggage tag on a loop of string
    tg = cam((-20, 13, 70))
    art.append(f'<path d="M {tg[0]:.1f} {tg[1]:.1f} q -10 14 -26 18" stroke="#6A4A2A" stroke-width="1.4" fill="none"/>')
    tag = [(tg[0] - 26, tg[1] + 14), (tg[0] - 70, tg[1] + 26), (tg[0] - 62, tg[1] + 54), (tg[0] - 18, tg[1] + 42)]
    art.append(modelled(D, pk.dens2(tag, 6), ("#FFF6E0", "#F2E2C0", "#A8946A"), 1417, light=(0.6, -0.6), angle=-15, n=6, inkw=1.0, hi=0.3))
    for k in range(3):
        y_ = tg[1] + 30 + k * 6
        art.append(f'<path d="M {tg[0] - 60:.1f} {y_ + 3:.1f} L {tg[0] - 28:.1f} {y_ - 6:.1f}" stroke="#2A3A7A" stroke-width="1.6" opacity="0.7"/>')
    # top handle and the luggage scale dangling down the front, reading the verdict
    h0, h1 = cam((-8, 0, 76)), cam((8, 0, 76))
    art.append(f'<path d="M {h0[0]:.1f} {h0[1]:.1f} Q {(h0[0] + h1[0]) / 2:.1f} {(h0[1] + h1[1]) / 2 - 14:.1f} {h1[0]:.1f} {h1[1]:.1f}" stroke="#1A1A1E" stroke-width="5" fill="none" stroke-linecap="round"/>')
    tp = cam((0, 13, 77))
    art.append(f'<path d="M {tp[0]:.1f} {tp[1] - 12:.1f} L {tp[0] + 2:.1f} {tp[1] + 30:.1f}" stroke="#2A2A30" stroke-width="3.4"/>')
    sx_, sy_ = tp[0] + 2, tp[1] + 56
    scl = [(sx_ - 34, sy_ - 20), (sx_ + 34, sy_ - 20), (sx_ + 38, sy_ + 24), (sx_ - 38, sy_ + 24)]
    art.append(f'<path d="{blob(sx_ + 8, sy_ + 30, 36, 6, 1418, 0.1, 10)}" fill="#0A1030" opacity="0.3"/>')
    art.append(modelled(D, pk.dens2(scl, 8), ("#F0F0F4", "#A8AAB2", "#4A4C54"), 1419, light=(0.6, -0.8), angle=0, n=10, inkw=1.4, hi=0.5))
    lcd = [(sx_ - 24, sy_ - 10), (sx_ + 24, sy_ - 10), (sx_ + 24, sy_ + 12), (sx_ - 24, sy_ + 12)]
    art.append(f'<path d="{pdl(lcd)}" fill="#B8D8A0"/>')
    art.append(f'<text x="{sx_:.1f}" y="{sy_ + 9:.1f}" text-anchor="middle" {MONO} font-size="19" fill="#1A2A10">23.0</text>')
    # the bedside lamp glow spilling in from the right
    art.append(soft_glow(D, 600, 300, 260, "#FFD890", 0.35))
    art.append(glaze(D, [(0, "#2A140A", 0.3), (0.45, "#2A140A", 0), (1, "#FFE8B0", 0.1)], 0, 0, 1, 0))
    art.append(vignette(D, "#1A0A04", 0.38, 0.8))
    txt = [letters(D, 300, 96, "Thoda adjust karo", SERIF_IT, 70, "#1E2A6A", ["#2E3E9A", "#0E1440", "#4A5AB8"], 1420, max_w=470,
                   shadow="#FFF0D8", soff=(0.022, 0.035), angle=-40, hi="#C0C8F0"),
           sub(300, 132, "23 KILOS, NOT ONE GRAM MORE", "#5A1A08", font=JOS, size=18, ls=4, line_w=16, gap=10)]
    return finish_art(D, art, txt, 1421, under="#C88A5E", edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ 15. jugaad — the remote: wrapped in plastic, held with a rubber band
@design("jugaad")
def jugaad():
    D = Doc2("in-jg")
    # a crochet doily on a dark wooden side table, a warm lamp glow
    out = [wood_planks(D, 0, 600, 1501, ("#B07A4A", "#7A4A26", "#3E2210"), 4)]
    out.append(soft_glow(D, 120, 140, 400, "#FFD890", 0.35))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#000000", 0), (1, "#000000", 0.25)], 0, 0, 1, 1)}"/>')
    # doily: crochet lace in rings - a rosette, a ring of petals, mesh, a scalloped edge with picots - each
    # thread casting a hairline shadow on the wood
    cx, cy = 300, 390
    sq = 0.72

    def ring_path(rr, n, amp, ph=0.0):
        pts_ = [(cx + math.cos(2 * math.pi * i / (n * 6)) * (rr + amp * math.cos(n * 2 * math.pi * i / (n * 6) + ph)),
                 cy + math.sin(2 * math.pi * i / (n * 6)) * (rr + amp * math.cos(n * 2 * math.pi * i / (n * 6) + ph)) * sq) for i in range(n * 6)]
        return smooth_closed(pts_)
    lace = []
    for dx, dy, col, op in ((5, 7, "#2A1408", 0.35), (0, 0, "#FFF8EC", 1.0)):
        g = f'<g transform="translate({dx} {dy})" opacity="{op}">'
        g += f'<path d="{ring_path(232, 26, 10)}" fill="none" stroke="{col}" stroke-width="3.2"/>'
        for i in range(52):
            a_ = 2 * math.pi * i / 52
            g += f'<circle cx="{cx + math.cos(a_) * 244:.1f}" cy="{cy + math.sin(a_) * 244 * sq:.1f}" r="2.6" fill="{col}"/>'
        for rr in (206, 182):
            g += f'<path d="{ring_path(rr, 30, 5, rr * 0.1)}" fill="none" stroke="{col}" stroke-width="2"/>'
        for i in range(48):
            a_ = 2 * math.pi * i / 48
            g += f'<path d="M {cx + math.cos(a_) * 120:.1f} {cy + math.sin(a_) * 120 * sq:.1f} L {cx + math.cos(a_) * 206:.1f} {cy + math.sin(a_) * 206 * sq:.1f}" stroke="{col}" stroke-width="1.4"/>'
        for i in range(12):
            a_ = 2 * math.pi * i / 12
            px_, py_ = cx + math.cos(a_) * 92, cy + math.sin(a_) * 92 * sq
            g += f'<path d="{blob(px_, py_, 30, 16, 1540 + i, 0.05, 12, math.degrees(math.atan2(math.sin(a_) * sq, math.cos(a_))))}" fill="none" stroke="{col}" stroke-width="2.6"/>'
            g += f'<path d="{blob(px_, py_, 16, 7, 1560 + i, 0.05, 10, math.degrees(math.atan2(math.sin(a_) * sq, math.cos(a_))))}" fill="none" stroke="{col}" stroke-width="1.4"/>'
        g += f'<path d="{ring_path(122, 12, 6)}" fill="none" stroke="{col}" stroke-width="2.4"/>'
        g += f'<path d="{blob(cx, cy, 52, 52 * sq, 1580, 0.02, 20)}" fill="none" stroke="{col}" stroke-width="2.4"/>'
        for k in range(3):
            g += f'<path d="{blob(cx, cy, 40 - k * 12, (40 - k * 12) * sq, 1581 + k, 0.03, 16)}" fill="none" stroke="{col}" stroke-width="2"/>'
        g += "</g>"
        lace.append(g)
    out.append(f'<path d="{blob(cx, cy, 236, 236 * sq, 1539, 0.01, 40)}" fill="#FFF6E6" opacity="0.18"/>')
    out.append("".join(lace))
    # the remote: dark plastic, soft rubber buttons, wrapped in crinkly cling film
    a = -24
    rx0, ry0, rw, rh = cx - 64, cy - 168, 128, 330
    body = rot(round_poly([(rx0, ry0), (rx0 + rw, ry0), (rx0 + rw - 6, ry0 + rh), (rx0 + 6, ry0 + rh)], 22, 5), cx, cy, a)
    out.append(cast(D, cx + 24, cy + 20, 110, 170, strength=0.35, seed=1503))
    out.append(painted(D, body, ("#5A5E68", "#2A2C34", "#0E0E12"), 1504, sdir=(0.6, 0.4), sk=0.12, angle=a - 90, n=30, inkw=2, hi=0.35))
    btn = []

    def B(x, y, w, h, col, txt=None, rnd_=False):
        pts = rot(round_poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], min(w, h) / 2 if rnd_ else 5, 4), cx, cy, a)
        s = f'<path d="{smooth_closed(pts)}" fill="{col}"/><path d="{smooth_closed(shift(pts, -1, -1.5))}" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.35"/>'
        if txt:
            px, py = rot([(x, y + 5)], cx, cy, a)[0]
            s += f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" {JOS} font-size="16" fill="#F4F4F4" transform="rotate({a} {px:.1f} {py:.1f})">{txt}</text>'
        return s

    btn.append(B(cx - 38, ry0 + 34, 26, 26, "#D6342A", rnd_=True))
    for i in range(3):
        for j in range(4):
            btn.append(B(cx - 34 + i * 34, ry0 + 150 + j * 34, 26, 22, "#4A4E58", str(1 + i + j * 3) if j < 3 else ["", "0", ""][i]))
    btn.append(B(cx, ry0 + 92, 64, 44, "#3A3E48", rnd_=True))
    btn.append(B(cx, ry0 + 92, 22, 22, "#6A6E78", rnd_=True))
    for i, col in enumerate(("#D6342A", "#3E9A3A", "#F2BE2A", "#2E6AC8")):
        btn.append(B(cx - 42 + i * 28, ry0 + 296, 20, 10, col))
    out.append("".join(btn))
    # cling film: pale sheen, crinkles, a twisted end
    film = rot(round_poly([(rx0 - 12, ry0 - 14), (rx0 + rw + 12, ry0 - 14), (rx0 + rw + 6, ry0 + rh + 14), (rx0 - 6, ry0 + rh + 14)], 26, 5), cx, cy, a)
    out.append(f'<path d="{smooth_closed(film)}" fill="#E8F4FA" opacity="0.22"/>')
    rnd = random.Random(1505)
    cr = []
    for _ in range(26):
        x, y = rnd.uniform(rx0 - 10, rx0 + rw + 10), rnd.uniform(ry0 - 10, ry0 + rh + 10)
        p = rot([(x, y), (x + rnd.uniform(-20, 20), y + rnd.uniform(10, 40)), (x + rnd.uniform(-10, 10), y + rnd.uniform(40, 70))], cx, cy, a)
        cr.append(taper(p, rnd.uniform(1, 3), 0.5, "#FFFFFF", rnd.uniform(0.35, 0.75)))
    out.append(clipped(D, smooth_closed(film), cr))
    out.append(ink(smooth_closed(film), "#C8E0EC", 1.6, 1506, 1, 0.7))
    tw = rot([(cx - 10, ry0 + rh + 12), (cx - 24, ry0 + rh + 40), (cx + 4, ry0 + rh + 52), (cx + 20, ry0 + rh + 36), (cx + 10, ry0 + rh + 12)], cx, cy, a)
    out.append(f'<path d="{smooth_closed(tw)}" fill="#E8F4FA" opacity="0.5"/>' + ink(smooth_closed(tw), "#C8E0EC", 1.4, 1507, 1, 0.7))
    # the rubber band holding the battery cover on
    for k, yy in enumerate((ry0 + 236, ry0 + 250)):
        band = rot([(rx0 - 14, yy - 4), (cx, yy + 4), (rx0 + rw + 14, yy - 2)], cx, cy, a)
        out.append(ink(smooth_open(band), "#E8A21E", 5, 1508 + k, 1, 1))
        out.append(ink(smooth_open(shift(band, -0.8, -1.4)), "#FFE08A", 1.6, 1510 + k, 1, 0.8))
    # Papa's reading glasses folded on the table, the evening chai going cold beside them
    gx, gy = 486, 540
    out.append(f'<path d="{blob(gx + 8, gy + 8, 64, 10, 1530, 0.1, 12)}" fill="#000000" opacity="0.35"/>')
    for dx in (-30, 30):
        out.append(f'<path d="{ellipse_d(gx + dx, gy, 26, 18)}" fill="#E8F2F8" opacity="0.3"/>')
        out.append(f'<path d="{ellipse_d(gx + dx, gy, 26, 18)}" fill="none" stroke="#4A3018" stroke-width="3.6"/>')
        out.append(f'<path d="M {gx + dx - 14} {gy - 8} q 8 -4 14 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.8"/>')
    out.append(f'<path d="M {gx - 4} {gy - 4} q 4 -6 8 0" stroke="#4A3018" stroke-width="3" fill="none"/>')
    out.append(f'<path d="M {gx - 56} {gy - 6} L {gx - 100} {gy - 30}" stroke="#4A3018" stroke-width="3"/>')
    cg = cutting_glass(D, 90, 590, 64, 84, 1531, fill=0.6)
    out.append(cg)
    out.append(glaze(D, [(0, "#FFE8B0", 0.14), (0.5, "#FFE8B0", 0), (1, "#1A0A04", 0.3)], 0, 0, 1, 1))
    out.append(vignette(D, "#0A0402", 0.45, 0.78))
    txt = [letters(D, 300, 140, "Jugaad", SERIF_IT, 150, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 1520, max_w=380,
                   shadow="#1A0A04", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 186, "ONE RUBBER BAND FROM FIXED", "#FFE6C8", font=JOS, size=19, ls=5, line_w=20, gap=12)]
    return finish_art(D, out, txt, 1521, under="#5A3418", edge=2.2, bristle=0.45, grain=0.18)


# ================================================================ 16. kai po che! — Uttarayan, kites over the rooftops
def patang(D, cx, cy, s, ang, seed, cols=("#D6246E", "#F6C21C"), backlit=0.0, haze=0.0, haze_c="#F4D8B0", tail=True, bend=0.0):
    """Indian fighter kite (patang) on its point: tissue paper in two colours, a bamboo spine and a bow bent
    up across the upper third, a small triangular tail flap.  backlit 0..1 makes the paper glow with the
    spine and bow showing through as shadows; haze pushes it into the distance."""
    c0, c1 = (mix(c, haze_c, haze) for c in cols)
    pts = [(cx, cy - s), (cx + s * 0.95, cy - s * 0.05 + bend * s), (cx, cy + s), (cx - s * 0.95, cy - s * 0.05 - bend * s)]
    P_ = rot(pts, cx, cy, ang)
    ink_c = mix("#4A2A14", haze_c, haze)
    out = [f'<path d="{pd(P_)}" fill="{c0}"/>']
    half = rot([(cx, cy - s), (cx + s * 0.95, cy - s * 0.05 + bend * s), (cx, cy + s)], cx, cy, ang)
    out.append(f'<path d="{pd(half)}" fill="{c1}"/>')
    if backlit:
        g = D.rad([(0, "#FFF6D8", 0.55 * backlit), (1, "#FFF6D8", 0)], 0.35, 0.4, 0.7)
        out.append(f'<path d="{pd(P_)}" fill="{g}"/>')
    else:
        out.append(f'<path d="{pd(P_)}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, "#000000", 0.18)])}"/>')
    spine = rot([(cx, cy - s), (cx, cy + s)], cx, cy, ang)
    bow = rot([(cx - s * 0.95, cy - s * 0.05 - bend * s), (cx, cy - s * 0.45), (cx + s * 0.95, cy - s * 0.05 + bend * s)], cx, cy, ang)
    sw = max(0.7, s * 0.045)
    sc = mix("#6A4A2A", haze_c, haze) if not backlit else mix("#5A3A20", c0, 0.35)
    out.append(f'<path d="{pd(spine, False)}" stroke="{sc}" stroke-width="{sw:.2f}" fill="none" opacity="0.85"/>')
    out.append(f'<path d="{smooth_open(bow)}" stroke="{sc}" stroke-width="{sw:.2f}" fill="none" opacity="0.85"/>')
    out.append(f'<path d="{pd(P_)}" fill="none" stroke="{ink_c}" stroke-width="{max(0.6, s * 0.03):.2f}" opacity="0.6"/>')
    if tail:
        tl = rot([(cx, cy + s * 0.88), (cx - s * 0.2, cy + s * 1.3), (cx + s * 0.2, cy + s * 1.3)], cx, cy, ang)
        out.append(f'<path d="{pd(tl)}" fill="{c1}"/>')
    return "".join(out)


def firki(D, cx, cy, r, ang, seed, thread="#E8407A"):
    """The spool of manja: two wooden end wheels on a hub, the glass-coated thread wound fat between them."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    hw = r * 0.7
    out = []
    e1 = (cx - ux * hw, cy - uy * hw)
    e2 = (cx + ux * hw, cy + uy * hw)
    out.append(taper([(e1[0] - ux * r * 0.7, e1[1] - uy * r * 0.7), (e2[0] + ux * r * 0.7, e2[1] + uy * r * 0.7)], r * 0.16, r * 0.16, "#7A5230"))
    out.append(f'<path d="{blob(e1[0], e1[1], r * 0.3, r, seed, 0.03, 16, ang)}" fill="#B8864A" stroke="#4A2A14" stroke-width="1.2"/>')
    body = rot([(cx - hw, cy - r * 0.78), (cx + hw, cy - r * 0.78), (cx + hw, cy + r * 0.78), (cx - hw, cy + r * 0.78)], cx, cy, ang)
    out.append(modelled(D, body, (lt(thread, 0.35), thread, dk(thread, 0.4)), seed + 1, light=(-0.6, -0.6), angle=ang + 90, n=30, inkw=1.0, hi=0.4,
                        cols=[lt(thread, 0.5), dk(thread, 0.3), "#FFFFFF"], sop=(0.2, 0.5)))
    out.append(f'<path d="{blob(e2[0], e2[1], r * 0.3, r, seed + 2, 0.03, 16, ang)}" fill="#D8A060" stroke="#4A2A14" stroke-width="1.2"/>')
    out.append(f'<path d="{blob(e2[0], e2[1], r * 0.1, r * 0.3, seed + 3, 0.03, 10, ang)}" fill="#6A4220"/>')
    return "".join(out)


def pol_rooftops(D, base, seed, haze, haze_c, pal_cols, hmin, hmax, tanks=0.5, people=0.0, people_c="#5A3A40"):
    """A row of old-city (pol) houses seen across the roofs: flat roofs with parapets, stair huts, water tanks,
    the odd carved balcony, washing lines, and tiny kite-flyers."""
    rnd = random.Random(seed)
    out = []
    x = -30
    while x < 630:
        w = rnd.uniform(46, 96)
        h = rnd.uniform(hmin, hmax)
        c = mix(rnd.choice(pal_cols), haze_c, haze)
        top = base - h
        body = pk.dens2([(x, top), (x + w, top), (x + w, base + 200), (x, base + 200)], 10)
        out.append(f'<path d="{smooth_closed(jitter(body, rnd.randint(0, 999), 0.6))}" fill="{c}"/>')
        out.append(f'<path d="{pdl([(x + w * 0.62, top), (x + w, top), (x + w, base + 200), (x + w * 0.62, base + 200)])}" fill="{mix(dk(c, 0.18), haze_c, haze * 0.6)}" opacity="0.6"/>')
        out.append(f'<path d="{pdl([(x - 2, top - 5), (x + w + 2, top - 5), (x + w + 2, top + 2), (x - 2, top + 2)])}" fill="{mix(lt(c, 0.2), haze_c, haze * 0.5)}"/>')
        if rnd.random() < 0.35:
            hx = x + rnd.uniform(4, w * 0.5)
            out.append(f'<path d="{pdl([(hx, top - 22), (hx + 26, top - 22), (hx + 26, top), (hx, top)])}" fill="{mix(dk(c, 0.08), haze_c, haze)}"/>')
            out.append(f'<path d="{pdl([(hx - 2, top - 25), (hx + 28, top - 25), (hx + 28, top - 21), (hx - 2, top - 21)])}" fill="{mix(lt(c, 0.25), haze_c, haze)}"/>')
        if rnd.random() < tanks:
            tx = x + rnd.uniform(8, w - 24)
            out.append(f'<path d="{pdl([(tx, top - 20), (tx + 18, top - 20), (tx + 18, top), (tx, top)])}" fill="{mix("#2A2A30", haze_c, haze)}"/>')
            out.append(f'<ellipse cx="{tx + 9:.1f}" cy="{top - 20:.1f}" rx="9" ry="2.4" fill="{mix("#4A4A50", haze_c, haze)}"/>')
        for k in range(rnd.randint(1, 3)):
            wx = x + 8 + k * 22
            if wx + 10 < x + w:
                out.append(f'<rect x="{wx:.1f}" y="{top + 16:.1f}" width="10" height="15" fill="{mix("#4A3A4A", haze_c, haze)}"/>')
                if rnd.random() < 0.3:
                    out.append(f'<rect x="{wx - 3:.1f}" y="{top + 30:.1f}" width="16" height="3" fill="{mix("#6A4A2A", haze_c, haze)}"/>')
        if people and rnd.random() < people:
            px = x + rnd.uniform(10, w - 10)
            ph = rnd.uniform(14, 22) * (1 - haze * 0.4)
            pose = rnd.choice([dict(ua_l=-70, fa_l=-90, ua_r=60, fa_r=10), dict(ua_l=-40, fa_l=-80, ua_r=-60, fa_r=-85), dict()])
            out.append(figure(px, top + 1, ph, pose, mix(people_c, haze_c, haze * 0.7), facing=rnd.choice([1, -1]),
                              cloth=rnd.choice([None, "kurta", "sari"]), female=rnd.random() < 0.4)[0])
        x += w - 1
    return "".join(out)


@design("kai-po-che")
def kai_po_che():
    D = Doc2("in-kp")
    art = []
    # golden-hour sky over the old city: dusty blue overhead, apricot at the horizon, the low sun on the left
    art.append(sky(D, [(0, "#6E9CC4"), (0.4, "#A8C4D4"), (0.72, "#F2D4A8"), (1, "#F6B878")], 1601, 600,
                   ["#FFFFFF", "#8AB0D0", "#F8DCB0", "#FFE8C8"], 120, angle=-6, sop=(0.06, 0.16)))
    art.append(soft_glow(D, 70, 420, 330, "#FFF0C0", 0.75))
    art.append(soft_glow(D, 70, 430, 90, "#FFFFFF", 0.8))
    art.append(pk.sky_brush(D, 1602, [(190, 360, ["#FFE8C0", "#F8D0A0", "#FFFFFF"], 30, (2, 6), (60, 160), (0.12, 0.3))], angle=-4))
    # dozens of far kites, small and hazy, each on a faint string
    rnd = random.Random(1603)
    pal = [("#D6246E", "#F6C21C"), ("#2A3A90", "#F2901E"), ("#3E8A3A", "#FFFFFF"), ("#F2901E", "#D6342A"), ("#12808A", "#F6C21C"), ("#FFFFFF", "#D6246E"), ("#7A2A8A", "#F6C21C")]
    far = []
    for k in range(34):
        x, y = rnd.uniform(20, 580), rnd.uniform(200, 420)
        if 130 < x < 470 and y < 215:
            continue
        sz = 3 + (y - 200) / 220 * -1.5 + rnd.uniform(2, 6)
        far.append((y, x, sz, k))
    for y, x, sz, k in sorted(far):
        hz = 0.5 - (y - 200) / 600
        art.append(f'<path d="M {x:.1f} {y + sz:.1f} q {rnd.uniform(-20, 20):.1f} {rnd.uniform(30, 60):.1f} {rnd.uniform(-40, 40):.1f} {rnd.uniform(80, 160):.1f}" stroke="{mix("#6A5A6A", "#F2D8B8", 0.5)}" stroke-width="0.6" fill="none" opacity="0.5"/>')
        art.append(patang(D, x, y, sz, rnd.uniform(-25, 25), 1604 + k, pal[k % len(pal)], haze=0.45 + hz * 0.3, tail=sz > 5))
    # three rows of pol rooftops stepping toward us, hazier with distance, with kite-flyers on the roofs
    art.append(pol_rooftops(D, 440, 1610, 0.68, "#F2D2B4", ["#E8A890", "#D8B8A0", "#C8B0B8", "#E8C8A0"], 18, 60, people=0.45))
    art.append(haze_band(D, 440, 50, "#F8E0C0", 0.6))
    art.append(pol_rooftops(D, 486, 1611, 0.4, "#F0C8A8", ["#E8986A", "#F2C88A", "#D88A8A", "#B8A8C0", "#F4E0C0"], 20, 70, people=0.4))
    art.append(haze_band(D, 488, 40, "#F8D8B8", 0.4))
    art.append(pol_rooftops(D, 540, 1612, 0.15, "#E8B898", ["#D8784A", "#E8B070", "#C86A6A", "#8A98B0", "#E8D0B0"], 24, 80, tanks=0.7, people=0.2))
    # the neighbours' roof across the gap: a whitewashed slab with a low parapet, a stair hut, washing on a line
    nr = pk.dens2([(318, 472), (640, 466), (640, 560), (318, 560)], 10)
    art.append(modelled(D, nr, ("#FFE8D0", "#E8C8A8", "#A07A60"), 1640, light=(-0.9, -0.3), angle=-90, n=60, inkw=0, hi=0.25, core=0.2))
    art.append(f'<path d="{pdl([(316, 466), (640, 460), (640, 474), (316, 478)])}" fill="#F8E6D0"/>')
    hut = pk.dens2([(560, 404), (640, 400), (640, 470), (560, 472)], 10)
    art.append(modelled(D, hut, ("#F8D8B8", "#D8A888", "#8A6050"), 1641, light=(-0.9, -0.3), angle=-90, n=30, inkw=0, hi=0.3))
    art.append(f'<path d="{pdl([(572, 424), (598, 423), (598, 470), (572, 471)])}" fill="#5A3A3A"/>')
    art.append(pline([(330, 430), (420, 446), (560, 428)], "#6A5A5A", 1.0, 1642, 0.7, 1))
    for k, (x, c) in enumerate(((346, "#D6342A"), (362, "#F6C21C"), (514, "#2A6AB0"), (530, "#FFFFFF"))):
        y = 432 + (x - 330) * 0.17 if x < 420 else 446 - (x - 420) * 0.13
        art.append(f'<path d="{smooth_closed([(x - 6, y), (x + 6, y), (x + 7, y + 20), (x - 7, y + 21)])}" fill="{c}" opacity="0.9"/>')
    # the kite-flyers on that roof against the low sun: a man hauling in his line, his wife with the firki
    man_pose = dict(torso=-99, head=-26, ua_l=-68, fa_l=-82, hand_l=-86, ua_r=30, fa_r=-20, hand_r=-20, th_l=76, sh_l=96, th_r=106, sh_r=92, ft_r=8)
    msvg, mj = figure(430, 470, 132, man_pose, "#3A2420", rim="#FFE2A8", rim_side=-1, facing=1, cloth="kurta", build=0.95, rim_w=1.0)
    wom_pose = dict(torso=-92, head=-16, ua_l=78, fa_l=-62, hand_l=-40, ua_r=86, fa_r=-50, hand_r=-30, th_l=90, sh_l=90, th_r=92, sh_r=90)
    wsvg, wj = figure(494, 471, 120, wom_pose, "#4A2A2C", rim="#FFE2A8", rim_side=-1, facing=-1, cloth="sari", female=True, hair="bun", rim_w=1.0)
    art.append(wsvg)
    art.append(msvg)
    hw = wj["arm_l"][2]
    art.append(firki(D, 494 - hw[0] - 3, 471 + hw[1] - 1, 7, -8, 1620))
    art.append(f'<path d="{blob(462, 473, 70, 4, 1643, 0.1, 12)}" fill="#6A4A40" opacity="0.35"/>')
    # the near roof: parapet wall in warm whitewash, light raking from the left
    par = pk.dens2([(-20, 528), (620, 522), (620, 640), (-20, 640)], 12)
    art.append(modelled(D, par, ("#FFF2DC", "#E8D4B4", "#A88A6A"), 1613, light=(-0.9, -0.3), angle=0, n=90, inkw=0, hi=0.3, core=0.2))
    art.append(f'<path d="{pdl([(-20, 518), (620, 512), (620, 530), (-20, 536)])}" fill="#F6E6CC"/>')
    art.append(f'<path d="M -20 536 L 620 530" stroke="#8A6A4A" stroke-width="2" opacity="0.5"/>')
    # his line up to the winning kite, and the cut kite tumbling away on the left
    hand = (430 + mj["arm_l"][3][0], 470 + mj["arm_l"][3][1])
    k1 = (486, 248)
    art.append(f'<path d="M {hand[0]:.1f} {hand[1]:.1f} Q {(hand[0] + k1[0]) / 2 + 10:.1f} {(hand[1] + k1[1] + 52) / 2 + 8:.1f} {k1[0] - 4:.1f} {k1[1] + 50:.1f}" stroke="#E8407A" stroke-width="1.0" fill="none" opacity="0.9"/>')
    art.append(patang(D, k1[0], k1[1], 52, 12, 1621, ("#D6246E", "#F6C21C"), backlit=0.8, bend=0.04))
    k2 = (176, 296)
    art.append(patang(D, k2[0], k2[1], 40, -58, 1622, ("#2A3A90", "#F2901E"), backlit=0.6, bend=-0.08))
    art.append(pline([(k2[0] + 22, k2[1] + 28), (224, 344), (196, 380), (228, 416), (210, 446), (236, 470)], "#2A3A90", 1.1, 1623, 0.75, 1))
    for a_ in (-40, -10, 20):
        rr = math.radians(a_)
        art.append(taper([(k2[0] + 50 + math.cos(rr) * 10, k2[1] - 34 + math.sin(rr) * 22), (k2[0] + 66 + math.cos(rr) * 16, k2[1] - 44 + math.sin(rr) * 30)], 2.4, 0.8, "#FFFFFF", 0.7))
    # pigeons wheeling, spare kites leaning on the parapet
    for x, y, sz in ((100, 210, 9), (124, 198, 7), (82, 232, 6), (530, 300, 7)):
        art.append(bird_v(x, y, sz, "#4A3A48", 0.75))
    for k, (x, y, a_, c) in enumerate(((84, 520, -14, ("#3E8A3A", "#FFFFFF")), (112, 528, 10, ("#F2901E", "#D6342A")))):
        art.append(patang(D, x, y, 30, a_, 1650 + k, c, tail=False))
    art.append(firki(D, 190, 548, 18, -12, 1660, "#F6C21C"))
    art.append(glaze(D, [(0, "#FFE8B0", 0.2), (0.5, "#FFE8B0", 0), (1, "#6A3A5A", 0.18)], 0, 0, 1, 0))
    art.append(vignette(D, "#4A2A20", 0.28, 0.8))
    txt = [letters(D, 300, 132, "Kai po che!", SERIF_IT, 116, "#B8183A", ["#D8304A", "#7A0A1A", "#F05A6A"], 1630, max_w=450,
                   shadow="#FFF4E0", soff=(0.022, 0.035), angle=-40, hi="#FFB0B8"),
           sub(300, 176, "UTTARAYAN · KITES ON EVERY ROOF", "#1E3A6A", font=JOS, size=18, ls=4, line_w=18, gap=10)]
    return finish_art(D, art, txt, 1631, under="#F2D2B4", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 17. ekdum filmy — a hand-painted cinema hoarding
def sign_letters(D, x, y, s, font, size, face, side, outline, seed, depth=10, max_w=470, ls=0, rot_=0, shine="#FFFFFF"):
    """Cinema-hoarding lettering the way sign painters did it: a deep extrusion, a fat dark outline, a face painted
    in a two-tone gradient with visible strokes, and quick white 'shine' ticks on every letter."""
    fs = fit_size(s, font, size, max_w, ls)
    t = f'<text x="{x}" y="{y}" text-anchor="middle" {font} font-size="{fs}" letter-spacing="{ls}">{esc(s)}</text>'
    out = [f'<g transform="rotate({rot_} {x} {y})">']
    for k in range(depth, 0, -1):
        c = mix(side, "#000000", 0.25 * k / depth)
        out.append(f'<g transform="translate({k * 0.7:.1f} {k:.1f})" fill="{c}" stroke="{c}" stroke-width="{fs * 0.06:.1f}" stroke-linejoin="round">{t}</g>')
    out.append(f'<g fill="{outline}" stroke="{outline}" stroke-width="{fs * 0.13:.1f}" stroke-linejoin="round">{t}</g>')
    g = D.lin([(0, lt(face, 0.55)), (0.45, face), (0.55, dk(face, 0.12)), (1, dk(face, 0.35))])
    out.append(f'<g fill="{g}">{t}</g>')
    w = measure(s, font, fs, ls)
    uid = D.nid()
    rnd = random.Random(seed)
    st = []
    for _ in range(int(w / 4)):
        px, py = rnd.uniform(x - w / 2, x + w / 2), rnd.uniform(y - fs * 0.9, y)
        L = rnd.uniform(fs * 0.15, fs * 0.4)
        st.append(f'<path d="M {px:.1f} {py:.1f} l {L:.1f} {L * 0.12:.1f}" stroke="{rnd.choice([lt(face, 0.6), lt(face, 0.3), dk(face, 0.08)])}" stroke-width="{rnd.uniform(2, 5):.1f}" opacity="{rnd.uniform(0.15, 0.35):.2f}" stroke-linecap="round"/>')
    gx = x - w / 2
    for ch in s:
        adv = measure(ch, font, fs) + ls
        if ch.strip():
            px, py = gx + adv * 0.3, y - fs * 0.78
            st.append(f'<path d="M {px:.1f} {py + fs * 0.16:.1f} Q {px + fs * 0.01:.1f} {py + fs * 0.02:.1f} {px + fs * 0.12:.1f} {py:.1f}" stroke="{shine}" stroke-width="{max(2, fs * 0.035):.1f}" fill="none" opacity="0.9" stroke-linecap="round"/>')
        gx += adv
    out.append(f'<clipPath id="{uid}">{t}</clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    out.append("</g>")
    return "".join(out), fs


@design("ekdum-filmy")
def ekdum_filmy():
    D = Doc2("in-ef")
    art = []
    # the hoarding board: planks painted rani pink, a painted sunburst, spotlights crossing behind the title
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#B8185A"/>')
    rays = []
    for i in range(30):
        a0 = 2 * math.pi * i / 30
        a1 = 2 * math.pi * (i + 1) / 30
        c = "#D8246A" if i % 2 else "#A8124E"
        d = f"M 300 320 L {300 + 900 * math.cos(a0):.1f} {320 + 900 * math.sin(a0):.1f} L {300 + 900 * math.cos(a1):.1f} {320 + 900 * math.sin(a1):.1f} Z"
        rays.append(f'<path d="{d}" fill="{c}"/>')
        rays.append(strokes(D.nid(), d, (-40, -40, 640, 640), [lt(c, 0.25), dk(c, 0.2)], 1701 + i, n=14, angle=math.degrees((a0 + a1) / 2), length=(40, 160), width=(3, 9), opacity=(0.1, 0.3)))
    art.append("".join(rays))
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.rad([(0, "#FFE08A", 0.6), (0.45, "#FF8A4A", 0.15), (1, "#2A0420", 0.45)], 0.5, 0.53, 0.72)}"/>')
    for k, (x0, x1) in enumerate(((-40, 220), (640, 380))):
        art.append(f'<path d="M {x0} 640 L {x1 - 40} -20 L {x1 + 40} -20 Z" fill="{D.lin([(0, "#FFF6D0", 0.0), (1, "#FFF6D0", 0.18)], 0, 1, 0, 0)}"/>')
    for y in (148, 300, 452):
        art.append(f'<path d="M -10 {y} L 610 {y + 2}" stroke="#5A0A2A" stroke-width="2" opacity="0.45"/>')
        art.append(f'<path d="M -10 {y + 2} L 610 {y + 4}" stroke="#FF9AC0" stroke-width="1" opacity="0.3"/>')
    rnd = random.Random(1702)
    for k in range(14):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        art.append(f'<path d="{blob(x, y, rnd.uniform(4, 12), rnd.uniform(2, 6), rnd.randint(0, 999), 0.4, 8)}" fill="#C8A47A" opacity="0.55"/>')
    # marquee border of bulbs, a few blown
    for k in range(64):
        t = k / 64
        if t < 0.25:
            x, y = 40 + 520 * t / 0.25, 40
        elif t < 0.5:
            x, y = 560, 40 + 520 * (t - 0.25) / 0.25
        elif t < 0.75:
            x, y = 560 - 520 * (t - 0.5) / 0.25, 560
        else:
            x, y = 40, 560 - 520 * (t - 0.75) / 0.25
        on = rnd.random() < 0.85
        if on:
            art.append(soft_glow(D, x, y, 18, "#FFE27A", 0.65))
        art.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.6" fill="{"#FFF6C8" if on else "#7A5A3A"}" stroke="#4A2A10" stroke-width="1.2"/>')
        if on:
            art.append(f'<circle cx="{x - 1.6:.1f}" cy="{y - 1.6:.1f}" r="1.8" fill="#FFFFFF"/>')
    for x, y, r in ((116, 240, 15), (490, 226, 17), (92, 400, 10), (520, 404, 12), (300, 466, 8)):
        art.append(sparkle(x, y, r, "#FFF2B0", 0.95))
    # the title painted big on the board
    a_, _ = sign_letters(D, 300, 226, "EKDUM", ANTON, 128, "#FFEA6A", "#8A1A0A", "#2A0A1A", 1710, depth=12, max_w=420, ls=4, rot_=-6)
    b_, _ = sign_letters(D, 300, 360, "FILMY!", ANTON, 150, "#FF9A30", "#6A0A1A", "#2A0A1A", 1711, depth=14, max_w=440, ls=4, rot_=-6)
    art += [a_, b_]
    # ribbon banner, a ticket stub, a paper cone of hot peanuts
    rb = [(110, 410), (490, 390), (500, 444), (120, 464)]
    for side in (-1, 1):
        ex, ey = (112, 437) if side < 0 else (497, 417)
        art.append(f'<path d="{pd([(ex, ey - 22), (ex + side * 46, ey - 26), (ex + side * 34, ey), (ex + side * 46, ey + 24), (ex, ey + 22)])}" fill="#B8A484"/>')
    art.append(modelled(D, poly_pts(rb, 10, 1703, 0.5), ("#FFFFFF", "#F4EAD6", "#C8B494"), 1703, light=(-0.4, -1), angle=-3, n=20, inkw=1.6, hi=0.3))
    tk = rot(poly_pts([(330, 476), (500, 476), (500, 536), (330, 536)], 8, 1704, 0.3), 415, 506, 8)
    art.append(cast(D, 420, 540, 90, 10, strength=0.4, seed=1705))
    art.append(modelled(D, tk, ("#FFF4A0", "#F6D83A", "#A89A0A"), 1704, light=(-0.4, -1), angle=8, n=12, inkw=1.4, hi=0.3))
    art.append(f'<path d="M 372 478 L 366 536" stroke="#A89A0A" stroke-width="2" stroke-dasharray="4 4" transform="rotate(8 415 506)"/>')
    px, py = 166, 500
    cone = [(px - 46, py - 36), (px + 46, py - 36), (px + 6, py + 50), (px - 4, py + 50)]
    rnd2 = random.Random(1706)
    for k in range(12):
        art.append(modelled(D, blob_pts(px + rnd2.uniform(-36, 36), py - 40 + rnd2.uniform(-12, 4), 8, 5, 1707 + k, 0.1, 10, rot=rnd2.uniform(0, 180)), ("#F2C88A", "#C8904A", "#7A4A1A"), 1707 + k, n=3, inkw=0.9, hi=0.4))
    art.append(modelled(D, poly_pts(cone, 8, 1720, 0.4), ("#F4ECE0", "#E2D4C0", "#9A8A70"), 1720, light=(-0.6, -0.6), angle=-80, n=14, inkw=1.4, hi=0.3))
    for k in range(5):
        art.append(f'<path d="M {px - 36 + k * 9} {py - 26 + k * 8} l {50 - k * 9} 0" stroke="#6A6A70" stroke-width="1.4" opacity="0.5"/>')
    art.append(pk.steam_plume(D, [(160, 452), (150, 420), (168, 392)], 10, 16, 1722, "#FFFFFF", 0.4, puffs=False))
    art.append(vignette(D, "#1A0410", 0.22, 0.85))
    txt = [label(305, 437, "3 HOURS · WITH INTERVAL", JOS, 19, "#6A0A2A", ls=3, max_w=360, extra=' transform="rotate(-3 305 430)"'),
           label(436, 504, "BALCONY", JOS, 18, "#6A0A2A", ls=3, max_w=110, extra=' transform="rotate(8 436 498)"'),
           label(436, 528, "ROW F · 14", MONO, 16, "#6A0A2A", max_w=140, extra=' transform="rotate(8 436 518)"'),
           sub(300, 84, "NOW SHOWING · HOUSE FULL", "#FFE27A", font=JOS, size=19, ls=5, line_w=24, gap=12)]
    return finish_art(D, art, txt, 1721, under="#B8185A", edge=2.2, bristle=0.5, grain=0.2)


# ================================================================ 18. nazar na lage — nimbu-mirchi on the door
def lemon(D, cx, cy, r, seed, ang=0):
    pts = rot([(cx - r * 1.2, cy), (cx - r * 0.9, cy - r * 0.62), (cx, cy - r * 0.86), (cx + r * 0.9, cy - r * 0.62), (cx + r * 1.2, cy),
               (cx + r * 0.9, cy + r * 0.62), (cx, cy + r * 0.86), (cx - r * 0.9, cy + r * 0.62)], cx, cy, ang)
    out = [painted(D, pts, ("#FFF6A0", "#F6D82A", "#A8920A"), seed, sk=0.2, angle=ang, n=int(r) + 6, cols=["#FFFAC0", "#C8B01A", "#FFF080"], inkw=max(1.2, r * 0.05), hi=0.5)]
    for sgn in (-1, 1):
        nx, ny = rot([(cx + sgn * r * 1.22, cy)], cx, cy, ang)[0]
        out.append(f'<path d="{blob(nx, ny, r * 0.12, r * 0.09, seed + sgn, 0.1, 8)}" fill="#C8B01A"/>')
    rnd = random.Random(seed)
    out.append(clipped(D, smooth_closed(pts), [f'<circle cx="{cx + rnd.uniform(-r, r):.1f}" cy="{cy + rnd.uniform(-r, r) * 0.7:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#A8920A" opacity="0.4"/>' for _ in range(int(r * 1.2))]))
    return "".join(out)


def green_chilli(D, x, y, L, ang, seed, curl=0.18):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    right, left = [], []
    for i in range(13):
        t = i / 12
        w = L * 0.12 * (math.sin(math.pi * min(1, t * 1.2 + 0.1)) ** 0.5) * (1 - 0.8 * t)
        bend = L * curl * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, ("#9AE05A", "#3E9A2A", "#1A5A12"), seed, sdir=(nx, ny), sk=0.22, angle=ang, n=6, inkw=1.2, hi=0.45, hik=0.12)]
    out.append(taper([(x + ux * L * 0.12 - nx * L * 0.02, y + uy * L * 0.12 - ny * L * 0.02), (x + ux * L * 0.55 - nx * L * 0.04 + nx * L * curl * 0.3, y + uy * L * 0.55 - ny * L * 0.04 + ny * L * curl * 0.3)], L * 0.035, L * 0.01, "#E8FFC0", 0.7))
    out.append(taper([(x, y), (x - ux * L * 0.12 - nx * L * 0.04, y - uy * L * 0.12 - ny * L * 0.04)], L * 0.06, L * 0.035, "#4A6A1A"))
    return "".join(out)


@design("nazar-na-lage")
def nazar_na_lage():
    D = Doc2("in-nz")
    # lime-washed indigo wall (the blue of Jodhpur), a carved wooden door lintel
    out = [sky(D, [(0, "#5A8AD0"), (1, "#3A64B0")], 1801, 600, ["#7AA8E8", "#2A4A90", "#8AB8F0"], 120, angle=-84, sop=(0.08, 0.18))]
    out.append(blooms(1802, ["#A8C8F8", "#1E3A80"], 8, (0, 0, 600, 600), (90, 180), (0.08, 0.16)))
    out.append(soft_glow(D, 120, 120, 380, "#FFF0D0", 0.25))
    # door frame (top part) with carved rosettes, door leaves below in deep teal
    out.append(f'<path d="{hg.org_rect(92, 236, 416, 400, 1803, 0.6, 14, 2)}" fill="#7A4A26"/>')
    out.append(f'<path d="{hg.org_rect(124, 290, 352, 360, 1804, 0.6, 14, 2)}" fill="#12606A"/>')
    out.append(strokes(D.nid(), hg.org_rect(124, 290, 352, 360, 1804, 0.6, 14, 2), (124, 290, 476, 650), ["#2A8A90", "#063A40"], 1805, n=60, angle=-90, length=(40, 120), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(f'<path d="M 300 290 L 300 610" stroke="#06343A" stroke-width="5"/>')
    for x in (190, 410):
        for y in (360, 470, 580):
            pn = pk.dens2([(x - 56, y - 44), (x + 56, y - 44), (x + 56, y + 44), (x - 56, y + 44)], 8)
            out.append(modelled(D, pn, ("#3AA0A0", "#16707A", "#063A40"), x + y, light=(-0.7, -0.7), angle=-90, n=20, inkw=1.4, hi=0.45, core=0.3))
            out.append(f'<path d="{pdl([(x - 56, y + 44), (x + 56, y + 44), (x + 50, y + 38), (x - 50, y + 38)])}" fill="#042A30" opacity="0.6"/>')
            out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{BRASS[1]}" stroke="{INK}" stroke-width="1.2"/><circle cx="{x - 3}" cy="{y - 3}" r="3" fill="#FFF0C0"/>')
    for x in (136, 464):
        for y in range(310, 600, 40):
            out.append(f'<circle cx="{x}" cy="{y}" r="4.4" fill="{BRASS[1]}"/><circle cx="{x - 1.4}" cy="{y - 1.4}" r="1.6" fill="#FFF0C0"/>')
    lint = poly_pts([(80, 236), (520, 236), (520, 290), (80, 290)], 10, 1806, 0.4)
    out.append(painted(D, lint, ("#C88A54", "#8A5A30", "#4A2A10"), 1806, sdir=(0, 1), sk=0.15, angle=0, n=24, inkw=1.8, hi=0.35))
    for k in range(9):
        x = 108 + k * 48
        out.append(f'<path d="{blob(x, 263, 14, 14, 1807 + k, 0.08, 12)}" fill="#6A3E1A"/>')
        for j in range(6):
            a = math.radians(j * 60)
            out.append(f'<path d="{blob(x + math.cos(a) * 7, 263 + math.sin(a) * 7, 5, 3, k * 9 + j, 0.1, 8, j * 60)}" fill="#D8A06A"/>')
        out.append(f'<circle cx="{x}" cy="263" r="3" fill="#4A2A10"/>')
    out.append(cast(D, 300, 300, 230, 12, strength=0.4, seed=1808))
    # a marigold-and-mango-leaf toran along the lintel
    out.append(garland(D, [(86, 296), (190, 316), (300, 300), (410, 316), (514, 296)], 12, 1809))
    for k, x in enumerate(range(120, 500, 52)):
        out.append(leaf_simple(D, x, 306 + (8 if k % 2 else 0), 34, 9, 92 + (k % 3 - 1) * 6, ("#7ABA5A", "#2E7A34", "#124A1E"), 1810 + k, inkw=0.9))
    # the charm's shadow thrown on the door by the low sun from the left
    out.append(f'<g transform="translate(22 10)" opacity="0.32"><path d="M 300 288 L 301 500" stroke="#021A20" stroke-width="3"/>'
               f'<path d="{blob(301, 498, 40, 34, 1823, 0.05, 16)}" fill="#021A20"/>'
               f'<path d="{blob(301, 400, 36, 52, 1824, 0.1, 16)}" fill="#021A20"/></g>')
    # the nimbu-mirchi hanging from a nail on the lintel: a thread, a charcoal bead, seven chillies, a lemon
    ty = 300
    out.append(f'<circle cx="300" cy="{ty - 18}" r="4" fill="#3A3A40"/>')
    out.append(pline([(300, ty - 16), (301, 500)], "#F4F0E6", 2.4, 1811, 1, 1))
    out.append(f'<path d="{blob(301, 338, 13, 11, 1820, 0.15, 10)}" fill="#2A2A2E"/><path d="{blob(297, 334, 4, 3, 1821, 0.2, 8)}" fill="#8A8A90"/>')
    fan = [(-38, 0.12), (38, -0.12), (-26, 0.1), (26, -0.1), (-14, 0.1), (14, -0.08), (0, 0.06)]
    for k, (da, cu) in enumerate(fan):
        y = 352 + (k // 2) * 20
        out.append(green_chilli(D, 301, y, 92, 90 + da, 1813 + k, curl=cu))
    out.append(cast(D, 301, 548, 40, 6, strength=0.25, seed=1822))
    out.append(lemon(D, 301, 498, 40, 1812, 90))
    # lettering
    out.append(glaze(D, [(0, "#FFF0C8", 0.16), (0.5, "#FFF0C8", 0), (1, "#0A1A3A", 0.3)], 0, 0, 1, 0.5))
    out.append(vignette(D, "#0A1430", 0.35, 0.8))
    txt = [letters(D, 300, 132, "Nazar na lage", SERIF_IT, 94, "#FFF2D8", ["#FFFFFF", "#F2D8A8", "#FFF6E8"], 1830, max_w=450,
                   shadow="#12245A", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 178, "NO EVIL EYE ON THIS HOME", "#FFE08A", font=JOS, size=20, ls=5, line_w=22, gap=12)]
    return finish_art(D, out, txt, 1831, under="#3A64B0", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 19. taj mahal — Agra at first light, across the long pool
def cypress(D, x, base, h, seed, col=("#5A7A5A", "#2E4A3A", "#142A20"), haze=0.0, haze_c="#E8D8E0", light=-1):
    """A garden cypress: a slim flame of dark foliage built from upward dabs, lit on one side."""
    rnd = random.Random(seed)
    c0, c1, c2 = (mix(c, haze_c, haze) for c in col)
    w = h * 0.1
    pts = []
    for i in range(16):
        t = i / 15
        r = w * (0.75 + 0.25 * math.sin(math.pi * min(1, t * 2.2))) * (1 - t ** 1.8) ** 0.8 if t > 0.02 else w * 0.5
        pts.append((x + r * (1 + rnd.uniform(-0.12, 0.12)), base - h * t))
    pts = pts + [(2 * x - px + rnd.uniform(-1, 1) * w * 0.1, py) for px, py in pts[::-1]]
    out = [f'<path d="{smooth_closed(pts)}" fill="{c1}"/>']
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = [strokes(D.nid(), smooth_closed(pts), (x - w * 1.2, base - h, x + w * 1.2, base), [c0, c2, c1], seed, n=int(h * 0.9), angle=-95,
                     length=(h * 0.06, h * 0.18), width=(w * 0.08, w * 0.25), opacity=(0.3, 0.7), curve=0.4)]
    g = D.lin([(0, c0, 0.55), (0.45, c0, 0), (1, c2, 0.6)], x - w, 0, x + w, 0, "userSpaceOnUse") if light < 0 else \
        D.lin([(0, c2, 0.6), (0.55, c0, 0), (1, c0, 0.55)], x - w, 0, x + w, 0, "userSpaceOnUse")
    inner.append(f'<rect x="{x - w * 1.3:.1f}" y="{base - h:.1f}" width="{w * 2.6:.1f}" height="{h:.1f}" fill="{g}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


@design("taj-mahal")
def taj_mahal():
    D = Doc2("in-tj")
    art = []
    G = 412                                   # garden level at the foot of the plinth
    # dawn sky: lavender above, rose and apricot at the horizon, a pale sun rising behind the left minarets
    art.append(sky(D, [(0, "#8A90C4"), (0.35, "#BBA8C8"), (0.62, "#EAC0C0"), (0.82, "#F8D6B8"), (1, "#FBE6CC")], 1901, 600,
                   ["#FFFFFF", "#F6C8C0", "#A8A0D0", "#FFE8D0"], 110, angle=-3, sop=(0.05, 0.14)))
    art.append(pk.sky_brush(D, 1902, [(150, 330, ["#F8D8D0", "#E8B8C0", "#FFFFFF"], 40, (2, 7), (60, 180), (0.12, 0.3))], angle=-3))
    art.append(soft_glow(D, 120, 360, 260, "#FFE8C0", 0.7))
    art.append(soft_glow(D, 120, 366, 40, "#FFFFFF", 0.85))
    # the far tree line along the Yamuna, lost in mist
    tl = ridge([(-20, 404), (100, 396), (200, 400), (400, 398), (520, 392), (620, 400)], 1903, 5, 3)
    art.append(hill(D, tl, 430, ("#C8B8CC", "#B0A0BC", "#9A8AAA"), 1903, inkw=0, sop=(0.1, 0.25)))
    art.append(haze_band(D, 404, 44, "#F4DCDC", 0.7))
    # the Taj, and a breath of river mist at its feet
    art.append(pk.taj_mahal_painting(D, 300, G, 3.22, 1905, lit="#FFEADC", mid="#F0D6D2", shade="#B4A2C0", deep="#7E6E98"))
    art.append(haze_band(D, G - 6, 26, "#FBE8E8", 0.55))
    # garden: lawns, marble walkways, the long canal leading to the tomb
    lawn = [(-20, G), (620, G), (620, 620), (-20, 620)]
    art.append(f'<path d="{pdl(lawn)}" fill="#6E8A62"/>')
    art.append(f'<path d="{pdl(lawn)}" fill="{D.lin([(0, "#D8C8C8", 0.85), (0.25, "#9AA888", 0.3), (1, "#3E5A40", 0.45)])}"/>')
    art.append(strokes(D.nid(), pdl(lawn), (-40, G, 620, 620), ["#9AB884", "#5A7A4A", "#B8C8A0"], 1906, n=120, angle=-4, length=(20, 80), width=(2, 6), opacity=(0.15, 0.35)))
    walk = [(268, G), (332, G), (468, 620), (132, 620)]
    art.append(f'<path d="{pdl(walk)}" fill="#E8D8D4"/>')
    art.append(f'<path d="{pdl(walk)}" fill="{D.lin([(0, "#F6E8E0", 0.6), (1, "#B8A0A8", 0.5)])}"/>')
    pool = [(287, G + 1), (313, G + 1), (378, 620), (222, 620)]
    pdp = pdl(pool)
    art.append(f'<path d="{pdp}" fill="#9AA6CC"/>')
    # the reflection: the whole tomb inverted in the still water, softened, with ripples
    refl = pk.taj_mahal_painting(D, 300, 0, 3.22, 1907, haze=0.3, haze_c="#C8C8E0")
    rp = [f'<path d="{pdp}" fill="{D.lin([(0, "#F2D8D8"), (0.5, "#B8B4D8"), (1, "#7A84B8")])}"/>',
          f'<g transform="translate(0 {G + 4}) scale(1 -1.0)" opacity="0.62">{refl}</g>',
          f'<path d="{pdp}" fill="{D.lin([(0, "#F6E0E0", 0.2), (1, "#4A5A98", 0.45)])}"/>']
    rnd = random.Random(1908)
    for k in range(70):
        y = rnd.uniform(G + 6, 610)
        t = (y - G) / (620 - G)
        hw = 13 + 65 * t
        x = 300 + rnd.uniform(-hw, hw)
        L_ = rnd.uniform(6, 22) * (0.4 + t)
        rp.append(f'<path d="M {x - L_ / 2:.1f} {y:.1f} L {x + L_ / 2:.1f} {y:.1f}" stroke="{rnd.choice(["#FFFFFF", "#E8E0F0", "#6A74A8"])}" stroke-width="{0.6 + t * 1.2:.1f}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    art.append(clipped(D, pdp, rp))
    art.append(f'<path d="{pdp}" fill="none" stroke="#F6EEEA" stroke-width="2" opacity="0.8"/>')
    # cypress avenues converging on the tomb, nearest ones tall at the edges
    for side in (-1, 1):
        rows = []
        for k in range(7):
            t = k / 6
            y = G + 6 + (620 - G) * t ** 1.6
            x = 300 + side * (52 + 260 * t ** 1.5)
            h = 26 + 300 * t ** 1.7
            rows.append((y, x, h, k))
        for y, x, h, k in rows:
            art.append(f'<path d="{blob(x + h * 0.45, y - 2, h * 0.48, max(2, h * 0.035), 1930 + k, 0.1, 12, -4)}" fill="#2A3A3A" opacity="0.32"/>')
            if k > 1:
                art.append(pk.dabs(1940 + k + side, (x - h * 0.3 + side * 20, y - 4, x + h * 0.3 + side * 40, y + 6), ["#E86A8A", "#F6C26A", "#FFFFFF", "#D84A5A"], int(h * 0.25), (0.8, 2.4), (0.5, 0.9)))
        for y, x, h, k in rows:
            art.append(cypress(D, x, y, h, 1910 + side * 10 + k, haze=max(0, 0.55 - k * 0.1), light=-1))
    for x, y, sz in ((96, 232, 7), (118, 222, 6), (470, 246, 6), (488, 238, 5)):
        art.append(bird_v(x, y, sz, "#6A5A7A", 0.75))
    art.append(glaze(D, [(0, "#FFE8D8", 0.18), (0.5, "#FFE8D8", 0), (1, "#3A3A6A", 0.18)]))
    art.append(vignette(D, "#3A2A4A", 0.3, 0.8))
    txt = [label(300, 104, "TAJ MAHAL", CINZEL, 64, "#3E2A52", ls=6, max_w=460),
           sub(300, 140, "AGRA · AT FIRST LIGHT", "#7A3A4E", font=JOS, size=19, ls=6, line_w=30, gap=14)]
    return finish_art(D, art, txt, 1914, under="#E8D0D0", edge=2.0, bristle=0.4, grain=0.16)


# ================================================================ 20. kerala — a kettuvallam on the backwaters at golden hour
def kettuvallam(D, x0, x1, wl, seed, haze=0.0, haze_c="#F8D8A8", lit_side=1):
    """A Kerala houseboat in near side view: a long jackfruit-wood hull rising to a curled prow and stern, a long
    barrel vault of woven bamboo-and-coir thatch, windows glowing with lamplight, an open front deck."""
    def H(c):
        return mix(c, haze_c, haze)
    L = x1 - x0
    out = []
    hull = [(x0 - L * 0.02, wl - L * 0.1), (x0 + L * 0.05, wl - L * 0.055), (x0 + L * 0.5, wl - L * 0.05), (x1 - L * 0.04, wl - L * 0.06),
            (x1 + L * 0.03, wl - L * 0.12), (x1 - L * 0.01, wl - L * 0.02), (x1 - L * 0.08, wl + L * 0.012), (x0 + L * 0.1, wl + L * 0.012), (x0 + L * 0.01, wl - L * 0.03)]
    out.append(modelled(D, hull, (H("#B8784A"), H("#6E3E1E"), H("#2A1408")), seed, light=(0.3, -1), angle=0, n=40, inkw=1.2, hi=0.35, core=0.3))
    for k in range(4):
        y = wl - L * 0.045 + k * L * 0.013
        out.append(f'<path d="M {x0 + L * 0.03:.1f} {y - L * 0.01:.1f} Q {x0 + L * 0.5:.1f} {y + L * 0.008:.1f} {x1 - L * 0.03:.1f} {y - L * 0.012:.1f}" stroke="{H("#2A1408")}" stroke-width="1" fill="none" opacity="0.6"/>')
    out.append(f'<path d="M {x0 + L * 0.04:.1f} {wl - L * 0.056:.1f} Q {x0 + L * 0.5:.1f} {wl - L * 0.045:.1f} {x1 - L * 0.04:.1f} {wl - L * 0.06:.1f}" stroke="{H("#F2C890")}" stroke-width="1.6" fill="none" opacity="0.7"/>')
    # the thatched vault
    r0, r1 = x0 + L * 0.22, x1 - L * 0.08
    rh = L * 0.13
    deck = wl - L * 0.052
    vault = [(r0, deck - rh * 0.05)] + [(r0 + (r1 - r0) * t, deck - rh * (0.82 + 0.18 * math.sin(math.pi * t)) - (rh * 0.12 if 0.02 < t < 0.98 else 0)) for t in [i / 16 for i in range(17)]] + [(r1, deck - rh * 0.05)]
    roof = [(r0 - L * 0.012, deck - rh * 0.55)] + [(r0 + (r1 - r0) * t, deck - rh * (1.0 + 0.16 * math.sin(math.pi * t))) for t in [i / 16 for i in range(17)]] + [(r1 + L * 0.012, deck - rh * 0.55), (r1, deck - rh * 0.62), (r0, deck - rh * 0.62)]
    # walls under the roof: dark interior with lit windows and wooden posts
    wall = [(r0 + L * 0.01, deck), (r1 - L * 0.005, deck), (r1 - L * 0.005, deck - rh * 0.62), (r0 + L * 0.01, deck - rh * 0.62)]
    out.append(f'<path d="{pdl(wall)}" fill="{H("#3A2010")}"/>')
    nwin = 7
    for k in range(nwin):
        t0 = (k + 0.18) / nwin
        t1 = (k + 0.82) / nwin
        wx0, wx1 = r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1
        wy0, wy1 = deck - rh * 0.52, deck - rh * 0.16
        g = D.lin([(0, H("#FFE8A0")), (1, H("#E8902A"))], 0, 0, 0, 1)
        out.append(f'<path d="{pdl([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])}" fill="{g}"/>')
        out.append(f'<path d="{pdl([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])}" fill="none" stroke="{H("#5A3418")}" stroke-width="1.4"/>')
        out.append(f'<path d="M {(wx0 + wx1) / 2:.1f} {wy0:.1f} L {(wx0 + wx1) / 2:.1f} {wy1:.1f}" stroke="{H("#5A3418")}" stroke-width="1"/>')
    for k in range(nwin + 1):
        px = r0 + (r1 - r0) * k / nwin
        out.append(f'<path d="M {px:.1f} {deck:.1f} L {px:.1f} {deck - rh * 0.62:.1f}" stroke="{H("#7A4A22")}" stroke-width="2.2"/>')
    rd = smooth_closed(roof)
    out.append(modelled(D, roof, (H("#F2D08A"), H("#C8964A"), H("#6A4A1E")), seed + 1, light=(-0.2 * lit_side, -1), angle=-90, n=80, inkw=1.2, hi=0.45, core=0.35,
                        cols=[H("#FFE6A8"), H("#9A6A2A"), H("#E8B868"), H("#7A5222")], sop=(0.2, 0.5), slen=(4, 14), sw=(0.8, 2.0)))
    cid = D.clip(f'<path d="{rd}"/>')
    ribs = []
    for k in range(26):
        t = k / 25
        px = r0 + (r1 - r0) * t
        ribs.append(f'<path d="M {px:.1f} {deck - rh * (1.0 + 0.16 * math.sin(math.pi * t)):.1f} L {px + 1.5:.1f} {deck - rh * 0.6:.1f}" stroke="{H("#7A5222")}" stroke-width="1" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(ribs)}</g>')
    # the open front deck with a cane chair and lamp glow
    out.append(f'<path d="M {x0 + L * 0.07:.1f} {deck:.1f} L {r0:.1f} {deck:.1f}" stroke="{H("#5A3418")}" stroke-width="2"/>')
    out.append(soft_glow(D, x0 + L * 0.16, deck - L * 0.03, L * 0.08, H("#FFD080"), 0.6))
    return "".join(out)


@design("kerala")
def kerala():
    D = Doc2("in-kl")
    art = []
    HZ = 352
    # golden-hour sky: apricot over lilac, the sun low on the right behind the far palms
    art.append(sky(D, [(0, "#7E92B8"), (0.35, "#C8A8B8"), (0.6, "#F2C090"), (0.85, "#F8D8A0"), (1, "#FBE6B8")], 2001, 600,
                   ["#FFE8C0", "#F2B890", "#FFFFFF"], 100, angle=-3, sop=(0.05, 0.14), y0=0))
    art.append(pk.sky_brush(D, 2002, [(150, 300, ["#F8D0A0", "#E8A890", "#FFF0D0"], 40, (2, 6), (70, 180), (0.12, 0.3))], angle=-2))
    art.append(soft_glow(D, 470, 338, 240, "#FFE6A0", 0.85))
    art.append(soft_glow(D, 470, 342, 30, "#FFFFFF", 0.95))
    # the far bank: a long line of palms and paddy, misty
    fb = ridge([(-20, HZ - 6), (160, HZ - 12), (330, HZ - 8), (480, HZ - 14), (620, HZ - 8)], 2003, 4, 3)
    art.append(hill(D, fb, HZ + 4, ("#A88A8A", "#8A7080", "#6A5A6A"), 2003, inkw=0, sop=(0.1, 0.25)))
    rnd = random.Random(2004)
    for k in range(26):
        x = rnd.uniform(-10, 610)
        art.append(coco_palm_far(x, HZ - 8, rnd.uniform(26, 46), rnd.uniform(-0.3, 0.3), 2010 + k, mix("#5A4A5A", "#F2C8A0", 0.35 + rnd.uniform(0, 0.15))))
    art.append(haze_band(D, HZ - 6, 26, "#F8D8B0", 0.55))
    # the backwater: sky reflected, the sun's road of gold, slow ripples
    water = [(-20, HZ), (620, HZ), (620, 620), (-20, 620)]
    art.append(f'<path d="{pdl(water)}" fill="{D.lin([(0, "#F6D2A0"), (0.3, "#D8A890"), (0.7, "#7E7EA0"), (1, "#3E4A6A")])}"/>')
    art.append(f'<ellipse cx="470" cy="{HZ + 60}" rx="70" ry="70" fill="{D.rad([(0, "#FFF0C0", 0.6), (1, "#FFF0C0", 0)])}" transform="scale(1 1)"/>')
    rl = []
    for k in range(260):
        y = rnd.uniform(HZ + 2, 610)
        t = (y - HZ) / (620 - HZ)
        x = rnd.uniform(-20, 620) if k % 2 else 470 + 30 * t + rnd.uniform(-1, 1) * (30 + 90 * t)
        Lr = rnd.uniform(8, 30) * (0.4 + t * 1.4)
        col = rnd.choice(["#FFF4D8", "#FFE0A0", "#FFF8E8", "#F6C890"]) if abs(x - (470 + 30 * t)) < 30 + 90 * t else rnd.choice(["#A8A0C0", "#5A5A80", "#F2D0B0"])
        rl.append(f'<path d="M {x - Lr / 2:.1f} {y:.1f} L {x + Lr / 2:.1f} {y:.1f}" stroke="{col}" stroke-width="{0.6 + t * 1.6:.1f}" opacity="{rnd.uniform(0.3, 0.75):.2f}" stroke-linecap="round"/>')
    art.append("".join(rl))
    # the houseboat gliding across the middle distance, its reflection below
    hb = kettuvallam(D, 230, 520, HZ + 52, 2020, haze=0.12)
    art.append(f'<g transform="translate(0 {2 * (HZ + 52) + 2}) scale(1 -1)" opacity="0.38">{kettuvallam(D, 230, 520, HZ + 52, 2021, haze=0.4, haze_c="#9A90B0")}</g>')
    art.append(hb)
    art.append(f'<path d="M 214 {HZ + 54} Q 380 {HZ + 60} 540 {HZ + 54}" stroke="#FFF2D8" stroke-width="1.6" fill="none" opacity="0.6"/>')
    # near bank on the left: palms leaning out over the water, against the light
    nb = [(-20, 440), (60, 448), (120, 470), (160, 520), (150, 620), (-20, 620)]
    art.append(f'<path d="{smooth_closed(nb)}" fill="#2A2420"/>')
    art.append(grass(2030, (-20, 430, 150, 470), ["#3A3A28", "#5A5030", "#2A2418"], 60, (8, 22)))
    art.append(coco_palm(D, -6, 452, 250, 0.25, 2033, rim=0.6, scale=0.85))
    art.append(coco_palm(D, 40, 470, 260, 0.6, 2031, rim=0.8))
    art.append(coco_palm(D, 100, 482, 200, 0.85, 2032, rim=0.8, scale=0.85))
    # a fisherman poling his vallam home in the foreground water
    cx_, wl_ = 380, 500
    canoe = [(cx_ - 78, wl_ - 10), (cx_ - 60, wl_ - 3), (cx_ + 50, wl_ - 3), (cx_ + 76, wl_ - 12), (cx_ + 64, wl_ + 4), (cx_ - 64, wl_ + 4)]
    art.append(f'<path d="{smooth_closed(canoe)}" fill="#1E1612"/>')
    art.append(f'<path d="M {cx_ - 62} {wl_ - 4} Q {cx_} {wl_ - 1} {cx_ + 54} {wl_ - 4}" stroke="#E8B870" stroke-width="1.2" fill="none" opacity="0.7"/>')
    fig, fj = figure(cx_ + 34, wl_ - 3, 84, dict(torso=-78, head=8, ua_l=58, fa_l=72, hand_l=80, ua_r=40, fa_r=20, hand_r=30, th_l=80, sh_l=100, th_r=104, sh_r=88),
                     "#1E1612", rim="#F2C070", rim_side=1, facing=-1, cloth="lungi", rim_w=1.0)
    art.append(fig)
    hd = fj["arm_l"][2]
    hx, hy = cx_ + 34 - hd[0], wl_ - 3 + hd[1]
    art.append(f'<path d="M {hx + 40:.1f} {hy - 50:.1f} L {hx - 34:.1f} {wl_ + 40:.1f}" stroke="#2A1E14" stroke-width="2.2"/>')
    art.append(f'<path d="{smooth_closed([(cx_ - 70, wl_ + 6), (cx_ + 70, wl_ + 6), (cx_ + 60, wl_ + 14), (cx_ - 60, wl_ + 14)])}" fill="#1E1612" opacity="0.4"/>')
    for k in range(3):
        art.append(f'<path d="M {cx_ - 60 - k * 20} {wl_ + 8 + k * 6} q 20 3 40 0" stroke="#FFF0C8" stroke-width="1.2" fill="none" opacity="{0.6 - k * 0.15:.2f}"/>')
    # water hyacinth drifting, an egret on a stake
    for k, (x, y) in enumerate(((180, 540), (230, 556), (520, 570), (90, 586))):
        art.append(pk.dabs(2040 + k, (x - 22, y - 6, x + 22, y + 6), ["#2E4A2A", "#4A6A3A", "#1E2E1A"], 16, (2, 5), (0.7, 1)))
        art.append(f'<circle cx="{x + 4}" cy="{y - 5}" r="2.2" fill="#B89AD8"/>')
    for x, y, sz in ((330, 230, 7), (352, 238, 6), (150, 260, 6)):
        art.append(bird_v(x, y, sz, "#5A4A5A", 0.75))
    art.append(glaze(D, [(0, "#FFE8B0", 0.12), (1, "#3A2A4A", 0.2)]))
    art.append(vignette(D, "#2A1A20", 0.32, 0.8))
    txt = [letters(D, 300, 140, "Kerala", SERIF_IT, 150, "#1E4A3A", ["#2E6A4A", "#0E2A1E", "#4A8A6A"], 2050, max_w=400,
                   shadow="#FFF0D0", soff=(0.022, 0.035), angle=-40, hi="#A8E0C0"),
           sub(300, 184, "BACKWATERS · SLOW, GOLDEN DAYS", "#6A2A1A", font=JOS, size=18, ls=4, line_w=18, gap=10)]
    return finish_art(D, art, txt, 2051, under="#F2C8A0", edge=2.4, bristle=0.45, grain=0.18)


def coco_palm_far(x, base, h, lean, seed, col):
    """A far palm: a thin curved stroke and a small starburst of drooping fronds."""
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    out = [taper([(x, base), (x + lean * h * 0.4, base - h * 0.5), top], 2.2, 1.2, col)]
    for k in range(8):
        a = math.radians(-180 + k * 25 + rnd.uniform(-8, 8))
        L = h * rnd.uniform(0.3, 0.42)
        tip = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.4 + L * 0.45)
        mid = (top[0] + math.cos(a) * L * 0.5, top[1] + math.sin(a) * L * 0.5 - 2)
        out.append(taper([top, mid, tip], 2.6, 0.5, col))
    return "".join(out)


# ================================================================ 21. jaipur — a jharokha in the pink city
def hawa_bay(D, cx, z0, w, h, seed, top=None, pal=("#F8B8A0", "#E08A74", "#9A4A48"), white="#FFF4EC", sun=(-0.4, -0.9)):
    """One storey of a jharokha bay on the Hawa Mahal: a semi-octagonal projection (lit front, angled sides),
    an arched opening filled with jaali, a white painted border, a chhajja ledge below.  z0 = bottom (px)."""
    lt_, base, dk_ = pal
    out = []
    fw = w * 0.56
    sw_ = (w - fw) / 2
    x0, x1 = cx - w / 2, cx + w / 2
    f0, f1 = cx - fw / 2, cx + fw / 2
    y1 = z0 - h
    left = [(x0, z0), (f0, z0 + h * 0.06), (f0, y1 + h * 0.06), (x0, y1)]
    right = [(f1, z0 + h * 0.06), (x1, z0), (x1, y1), (f1, y1 + h * 0.06)]
    front = [(f0, z0 + h * 0.06), (f1, z0 + h * 0.06), (f1, y1 + h * 0.06), (f0, y1 + h * 0.06)]
    rj = random.Random(seed * 7)
    J = lambda pts: smooth_closed(jitter(pk.dens2(pts, 6), rj.randint(0, 999), 0.5))
    out.append(f'<path d="{J(left)}" fill="{mix(lt_, "#FFE8D0", 0.3)}"/>')
    out.append(f'<path d="{J(right)}" fill="{mix(dk_, "#6A3A5A", 0.3)}"/>')
    g = D.lin([(0, lt_), (0.55, base), (1, mix(base, dk_, 0.3))], 0, 0, 1, 1)
    out.append(f'<path d="{J(front)}" fill="{g}"/>')
    out.append(strokes(D.nid(), J(front), (f0 - 2, y1, f1 + 2, z0 + 4), [lt_, dk_, "#FFF0E0"], seed + 9, n=10, angle=-90, length=(6, h * 0.5), width=(0.8, 2.4), opacity=(0.15, 0.35)))
    # arched opening with jaali
    aw = fw * 0.62
    ah = h * 0.62
    ab = z0 - h * 0.14
    arch = [(cx - aw / 2, ab), (cx - aw / 2, ab - ah * 0.55), (cx - aw * 0.36, ab - ah * 0.86), (cx, ab - ah), (cx + aw * 0.36, ab - ah * 0.86), (cx + aw / 2, ab - ah * 0.55), (cx + aw / 2, ab)]
    ad = smooth_closed(arch)
    out.append(f'<path d="{ad}" fill="{mix(dk_, "#3A1A2A", 0.4)}"/>')
    rnd = random.Random(seed)
    jl = []
    step = max(2.2, aw / 4)
    yy = ab - ah
    while yy < ab:
        xx = cx - aw / 2
        while xx < cx + aw / 2:
            jl.append(f'<circle cx="{xx + step / 2:.1f}" cy="{yy + step / 2:.1f}" r="{step * 0.22:.1f}" fill="{mix(lt_, base, 0.5)}" opacity="0.75"/>')
            xx += step
        yy += step
    out.append(clipped(D, ad, jl))
    out.append(f'<path d="{ad}" fill="none" stroke="{white}" stroke-width="{max(0.8, w * 0.045):.1f}" opacity="0.9"/>')
    # white border lines on the bay faces
    for pts in (front,):
        q = [(px + (cx - px) * 0.1, py + (z0 - h / 2 - py) * 0.08) for px, py in pts]
        out.append(f'<path d="{pdl(q)}" fill="none" stroke="{white}" stroke-width="{max(0.6, w * 0.025):.1f}" opacity="0.75"/>')
    # chhajja ledge with brackets under the bay
    led = [(x0 - w * 0.06, z0 - h * 0.02), (x1 + w * 0.06, z0 - h * 0.02), (x1, z0 + h * 0.08), (x0, z0 + h * 0.08)]
    out.append(f'<path d="{pdl(led)}" fill="{mix(base, dk_, 0.25)}"/>')
    out.append(f'<path d="M {x0 - w * 0.06:.1f} {z0 - h * 0.02:.1f} L {x1 + w * 0.06:.1f} {z0 - h * 0.02:.1f}" stroke="{white}" stroke-width="{max(0.6, w * 0.03):.1f}" opacity="0.85"/>')
    for bx in (cx - w * 0.3, cx, cx + w * 0.3):
        out.append(f'<path d="M {bx:.1f} {z0 + h * 0.08:.1f} q {w * 0.04:.1f} {h * 0.1:.1f} 0 {h * 0.14:.1f}" stroke="{dk_}" stroke-width="{max(0.8, w * 0.05):.1f}" fill="none" opacity="0.6"/>')
    out.append(f'<path d="{pdl(right)}" fill="#3A1A30" opacity="0.18"/>')
    # the top of the column: a domed cupola with a finial, or a curved bangaldar roof
    if top == "dome":
        dw = w * 0.86
        dm = [(cx - dw / 2, y1), (cx - dw * 0.48, y1 - h * 0.18), (cx - dw * 0.3, y1 - h * 0.38), (cx, y1 - h * 0.48), (cx + dw * 0.3, y1 - h * 0.38), (cx + dw * 0.48, y1 - h * 0.18), (cx + dw / 2, y1)]
        out.append(modelled(D, dm, (lt_, base, dk_), seed + 3, light=sun, angle=-90, n=12, inkw=0.8, hi=0.4))
        out.append(f'<path d="M {cx:.1f} {y1 - h * 0.48:.1f} L {cx:.1f} {y1 - h * 0.66:.1f}" stroke="#C89A4A" stroke-width="{max(0.8, w * 0.05):.1f}"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{y1 - h * 0.58:.1f}" r="{max(0.8, w * 0.05):.1f}" fill="#E8B850"/>')
        out.append(f'<path d="M {cx - dw / 2:.1f} {y1:.1f} L {cx + dw / 2:.1f} {y1:.1f}" stroke="{white}" stroke-width="{max(0.6, w * 0.035):.1f}"/>')
    elif top == "bangla":
        rf = [(x0 - w * 0.05, y1 + h * 0.02), (cx - w * 0.25, y1 - h * 0.2), (cx, y1 - h * 0.26), (cx + w * 0.25, y1 - h * 0.2), (x1 + w * 0.05, y1 + h * 0.02), (cx, y1 - h * 0.08)]
        out.append(modelled(D, rf, (lt_, base, dk_), seed + 4, light=sun, angle=0, n=10, inkw=0.8, hi=0.4))
        for k in (-1, 0, 1):
            out.append(f'<path d="M {cx + k * w * 0.3:.1f} {y1 - h * 0.24 + abs(k) * h * 0.05:.1f} l 0 {-h * 0.1:.1f}" stroke="#C89A4A" stroke-width="{max(0.8, w * 0.04):.1f}"/>')
    return "".join(out)


@design("jaipur")
def jaipur():
    D = Doc2("in-jp")
    art = []
    # a clear desert-morning sky, the sun full on the facade
    art.append(sky(D, [(0, "#4E8EC8"), (0.45, "#8EC0E0"), (0.8, "#E8E4D0"), (1, "#F8E0C0")], 2101, 600, ["#FFFFFF", "#7AAAD8", "#F8E8D0"], 90, angle=-4, sop=(0.05, 0.16)))
    art.append(soft_glow(D, 40, 300, 300, "#FFF2D0", 0.5))
    art.append(pk.sky_brush(D, 2102, [(200, 340, ["#FFFFFF", "#D8E8F4"], 26, (2, 6), (60, 160), (0.12, 0.3))], angle=-3))
    # the honeycomb facade: columns of jharokha bays stepping up to the crest
    ncol = 13
    W = 560
    cw = W / ncol
    sh = 60.0                       # storey height
    base_y = 520
    storeys = [3, 3, 4, 4, 4, 5, 5, 5, 4, 4, 4, 3, 3]
    # the wall plane behind the bays
    wall = []
    for i, n in enumerate(storeys):
        x0 = 300 - W / 2 + i * cw
        wall += [(x0, base_y - n * sh - 6), (x0 + cw, base_y - n * sh - 6)]
    wall = [(300 - W / 2, base_y)] + wall + [(300 + W / 2, base_y)]
    art.append(f'<path d="{pdl(wall)}" fill="#C8706A"/>')
    rnd = random.Random(2105)
    for i, n in enumerate(storeys):
        cx = 300 - W / 2 + (i + 0.5) * cw
        # the shadow each projecting column throws to its right across the wall
        x1 = cx + cw * 0.46
        shp = [(x1, base_y), (x1 + cw * 0.16, base_y + 4), (x1 + cw * 0.16, base_y - n * sh + 10), (x1, base_y - n * sh)]
        art.append(f'<path d="{pdl(shp)}" fill="#4A2244" opacity="0.42"/>')
        for k in range(n):
            z0 = base_y - k * sh
            top = None
            if k == n - 1:
                top = "bangla" if (i % 4 == 1 and n >= 4) else "dome"
            v = rnd.uniform(-0.12, 0.12)
            pal = (mix("#FFC8A8", "#FFE4D0", max(0, v) * 2), mix("#EE9A80", "#D27470", max(0, -v) * 3), "#8E4256")
            art.append(hawa_bay(D, cx, z0, cw * 0.92, sh * 0.9, 2110 + i * 10 + k, top=top, pal=pal))
            if rnd.random() < 0.5:
                art.append(taper([(cx + rnd.uniform(-8, 8), z0 + 6), (cx + rnd.uniform(-8, 8), z0 + rnd.uniform(18, 36))], 4, 1, "#7A3A40", 0.18))
    # the arcade of shops at street level: deep arches in shade, bolts of cloth and brass catching light
    arc_ = pk.dens2([(-20, 520), (620, 520), (620, 620), (-20, 620)], 14)
    art.append(modelled(D, arc_, ("#F2B0A0", "#D07A6E", "#8A3A44"), 2190, light=(0, -1), angle=0, n=60, inkw=0, hi=0.25))
    for k in range(9):
        x = -10 + k * 72
        ar = [(x + 8, 610), (x + 8, 556), (x + 22, 541), (x + 36, 536), (x + 50, 541), (x + 64, 556), (x + 64, 610)]
        art.append(f'<path d="{smooth_closed(ar)}" fill="{D.lin([(0, "#4A2030"), (1, "#7A4040")])}"/>')
        rr = random.Random(2191 + k)
        for j in range(6):
            bx = x + 14 + j * 8
            art.append(f'<path d="M {bx:.1f} {600 - rr.uniform(0, 8):.1f} L {bx:.1f} {566 + rr.uniform(0, 10):.1f}" stroke="{rr.choice(["#F6C21C", "#D6342A", "#2A6AB0", "#E86AA0", "#3EA86A"])}" stroke-width="5" opacity="0.8" stroke-linecap="round"/>')
        art.append(f'<path d="{smooth_open(ar)}" fill="none" stroke="#FFF0E8" stroke-width="2" opacity="0.85"/>')
    art.append(f'<path d="M -20 522 L 620 522" stroke="#FFF0E8" stroke-width="3"/>')
    art.append(f'<path d="M -20 528 L 620 528" stroke="#7A3A44" stroke-width="2" opacity="0.4"/>')
    # paper kites over the crest (Jaipur flies them all January)
    art.append(patang(D, 102, 236, 13, -14, 2181, ("#F6C21C", "#D6246E"), haze=0.2, haze_c="#A8CCE8"))
    art.append(f'<path d="M 104 250 q 30 60 80 110" stroke="#5A4A5A" stroke-width="0.7" fill="none" opacity="0.6"/>')
    art.append(patang(D, 532, 196, 10, 12, 2182, ("#2A6AB0", "#FFFFFF"), haze=0.3, haze_c="#A8CCE8"))
    # pigeons wheeling past the crest, one on a ledge
    for x, y, sz in ((470, 236, 9), (500, 222, 8), (92, 300, 7), (520, 260, 7), (120, 286, 6)):
        art.append(bird_v(x, y, sz, "#5A4A5A", 0.8))
    art.append(haze_band(D, 520, 40, "#FFE8D0", 0.35))
    art.append(glaze(D, [(0, "#FFF0D8", 0.18), (0.5, "#FFF0D8", 0), (1, "#4A2244", 0.25)], 0, 0, 1, 0.4))
    art.append(vignette(D, "#3A1A24", 0.3, 0.82))
    txt = [letters(D, 300, 132, "Jaipur", SERIF_IT, 140, "#FFF6EC", ["#FFFFFF", "#F8D8C8", "#FFEDE4"], 2140, max_w=400,
                   shadow="#7A2A34", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 176, "THE PINK CITY", "#3A1A4A", font=JOS, size=22, ls=8, line_w=34, gap=14)]
    return finish_art(D, art, txt, 2141, under="#C8706A", edge=2.0, bristle=0.4, grain=0.16)


# ================================================================ 22. mor — the peacock dances when the monsoon comes
def egret(x, y, s, phase, col="#FFFFFF", shade="#B8C4CC", flip=1):
    """A great egret in flight, side view: neck folded back into an S (a bulge under the chin), dagger bill,
    black legs trailing far behind, broad wings with fingered tips at `phase` (1 = raised, -1 = down)."""
    def P(px, py):
        return (x + flip * px * s, y + py * s)

    def W(pts, ph):
        return [P(px, py * ph if py < -0.04 else py) for px, py in pts]
    wing = [(0.16, -0.05), (0.13, -0.28), (0.05, -0.48), (-0.1, -0.66), (-0.3, -0.78), (-0.42, -0.8), (-0.36, -0.68), (-0.33, -0.58),
            (-0.3, -0.48), (-0.25, -0.32), (-0.2, -0.16), (-0.12, -0.04)]
    body = [(-0.38, 0.0), (-0.2, -0.07), (0.1, -0.08), (0.26, -0.05), (0.34, 0.02), (0.22, 0.07), (-0.1, 0.07), (-0.3, 0.04)]
    neck = [(0.22, -0.02), (0.32, 0.06), (0.38, 0.03), (0.38, -0.05), (0.42, -0.08)]
    far = W([(px * 0.9 + 0.03, py * 0.8) for px, py in wing], phase * 0.85)
    out = [f'<path d="{smooth_closed(far)}" fill="{shade}"/>',
           taper([P(-0.18, 0.05), P(-0.55, 0.08), P(-0.92, 0.1)], s * 0.035, s * 0.022, "#1E1E22", 0.9),
           f'<path d="{smooth_closed([P(*q) for q in body])}" fill="{col}"/>',
           taper([P(*q) for q in neck], s * 0.12, s * 0.09, col),
           f'<path d="{blob(*P(0.44, -0.085), s * 0.06, s * 0.045, 3, 0.05, 8)}" fill="{col}"/>',
           taper([P(0.47, -0.09), P(0.62, -0.075), P(0.76, -0.06)], s * 0.035, s * 0.006, "#E8B030"),
           f'<path d="{smooth_closed(W(wing, phase))}" fill="{col}"/>']
    # shading on the near wing's trailing edge and the belly
    tr = W([(-0.42, -0.8), (-0.33, -0.58), (-0.25, -0.32), (-0.12, -0.04)], phase)
    out.append(f'<path d="{smooth_open(tr)}" fill="none" stroke="{shade}" stroke-width="{max(0.8, s * 0.03):.1f}" opacity="0.8"/>')
    out.append(f'<path d="{smooth_open([P(-0.3, 0.04), P(0.0, 0.075), P(0.26, 0.05)])}" fill="none" stroke="{shade}" stroke-width="{max(0.8, s * 0.04):.1f}" opacity="0.7"/>')
    return "".join(out)


@design("mor")
def mor():
    D = Doc2("in-mr")
    art = []
    # the monsoon sky: indigo above, a sea-green break of light low on the left, the warm glow of rain-light
    art.append(sky(D, [(0, "#1E2640"), (0.35, "#34405E"), (0.62, "#5E7A7E"), (0.8, "#A8B49A"), (1, "#C8C49A")], 2201, 600,
                   ["#46506E", "#1A2036", "#7A8AA0", "#A8B8A8"], 160, angle=-6, sop=(0.06, 0.18)))
    art.append(pk.soft_glow(D, 90, 420, 330, "#F6E8B0", 0.45) if hasattr(pk, "soft_glow") else soft_glow(D, 90, 420, 330, "#F6E8B0", 0.45))
    art.append(pk.sky_brush(D, 2210, [
        (-40, 260, ["#1A2036", "#262E4A", "#30395A"], 140, (8, 22), (60, 180), (0.35, 0.8)),
        (60, 330, ["#3A4666", "#46506E", "#2A3250"], 110, (6, 16), (50, 150), (0.25, 0.6)),
        (180, 420, ["#7A8C90", "#9AAAA0", "#5E6E80"], 90, (4, 12), (40, 130), (0.18, 0.45)),
        (120, 300, ["#C8B890", "#E0D0A0", "#8A90A0"], 40, (1.5, 4), (30, 110), (0.15, 0.4)),
        (-40, 120, ["#121628", "#1E2440"], 70, (10, 26), (80, 200), (0.3, 0.7))], angle=-10))
    # a skein of egrets crossing the storm (the balaka of the monsoon poems)
    for k, (x, y, s, ph) in enumerate(((468, 250, 52, 0.85), (520, 284, 46, -0.55), (414, 222, 42, 0.3), (552, 322, 38, 0.95))):
        art.append(egret(x, y, s, ph, flip=-1))
    # distant land: a low ridge, a sandstone chhatri, trees in rain haze
    art.append(hill(D, ridge([(-20, 452), (120, 438), (260, 450), (420, 432), (620, 446)], 2203, 6, 3), 620, ("#7A9A7A", "#4A6E5A", "#2A4436"), 2203, inkw=0))
    art.append(haze_band(D, 446, 60, "#C8D0B8", 0.5))
    # the train and the bird (focal point), lit from the break of light at the left
    cx, cy, R = 312, 446, 248
    art.append(soft_glow(D, 300, 330, 300, "#F2F0C0", 0.5))
    tr_svg, fan = pk.peacock_train(D, cx, cy, R, 2230, a0=-197, a1=17, rows=5, squash=0.96)
    art.append(tr_svg)
    # wet ground, puddle reflecting the blue of the neck, the grass in front
    gl = ridge([(-20, 520), (200, 512), (420, 520), (620, 510)], 2204, 4, 3)
    art.append(hill(D, gl, 620, ("#7AA85A", "#3E7A36", "#16401C"), 2204, inkw=0, sop=(0.15, 0.4)))
    art.append(grass(2207, (-10, 515, 610, 600), ["#5A9A3A", "#2E6A2A", "#9AC86A", "#1E4A1E"], 320, (8, 22), w=1.2))
    art.append(pk.peacock_body(D, cx - 2, 556, 2.5, 2240))
    art.append(grass(2208, (-10, 548, 610, 610), ["#4A8A36", "#245A22", "#8AB85A"], 160, (12, 30), w=1.4))
    # rain: fine slanting strokes, some catching the light
    rnd = random.Random(2250)
    rn = []
    for _ in range(260):
        x, y = rnd.uniform(-20, 640), rnd.uniform(-20, 600)
        L = rnd.uniform(12, 34)
        rn.append(f'<path d="M {x:.1f} {y:.1f} l {-L * 0.28:.1f} {L:.1f}" stroke="{rnd.choice(["#E8F0F4", "#C8D4E0", "#FFF6D8"])}" stroke-width="{rnd.uniform(0.8, 1.6):.1f}" opacity="{rnd.uniform(0.18, 0.5):.2f}" stroke-linecap="round"/>')
    art.append("".join(rn))
    art.append(vignette(D, "#0E1424", 0.45, 0.78))
    txt = [letters(D, 300, 126, "Mor", SERIF_IT, 132, "#FFF4D8", ["#FFFFFF", "#F2E2B8", "#FFE8A8"], 2260, max_w=300,
                   shadow="#0E1428", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 168, "WHEN THE RAINS COME, HE DANCES", "#FFE29A", font=JOS, size=18, ls=4, line_w=16, gap=10)]
    return finish_art(D, art, txt, 2261, under="#2A3450", edge=2.6, bristle=0.45, grain=0.18)


# ================================================================ 23. holi hai! — gulal clouds and brass plates of colour
def gulal_cloud(D, cx, cy, r, col, seed, op=0.8, specks_n=None):
    """A thrown cloud of gulal hanging in sunlit air: a soft radial core, billowing lobes, and a spray of grains."""
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, cy, r * 1.25, col, op * 0.8)]
    for k in range(9):
        a_ = rnd.uniform(0, 6.28)
        rr = r * math.sqrt(rnd.random()) * 0.65
        x, y = cx + math.cos(a_) * rr, cy + math.sin(a_) * rr * 0.75
        sz = r * rnd.uniform(0.3, 0.55)
        g = D.rad([(0, lt(col, 0.15), op * 0.55), (0.7, col, op * 0.25), (1, col, 0)])
        out.append(f'<path d="{blob(x, y, sz, sz * 0.85, rnd.randint(0, 9999), 0.18, 12)}" fill="{g}"/>')
    out.append(pk.dabs(seed + 1, (cx - r * 1.2, cy - r, cx + r * 1.2, cy + r), [col, lt(col, 0.4), dk(col, 0.15)], specks_n or int(r * 0.9), (0.6, 2.2), (0.35, 0.85)))
    return "".join(out)


def gulal_thali(D, cx, cy, r, col, seed):
    """A brass thali seen at a low angle, heaped with a soft cone of gulal."""
    out = [f'<path d="{blob(cx + r * 0.1, cy + r * 0.2, r * 1.05, r * 0.3, seed, 0.05, 16)}" fill="#2A1408" opacity="0.4"/>']
    rim = ellipse_d(cx, cy, r, r * 0.3)
    out.append(f'<path d="{rim}" fill="#9A6A1E"/>')
    out.append(f'<path d="{rim}" fill="{D.lin([(0, "#FFF0B0", 0.9), (0.3, "#E8B84A", 0.3), (0.65, "#8A5A14", 0.6), (1, "#FFE08A", 0.7)], 0, 0, 1, 0)}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy - 1, r * 0.86, r * 0.24)}" fill="#C8902A"/>')
    out.append(f'<path d="{ellipse_d(cx, cy - 1, r * 0.86, r * 0.24)}" fill="{D.lin([(0, "#7A4A10", 0.7), (1, "#FFE6A0", 0.6)])}"/>')
    h = r * 0.62
    mound = [(cx - r * 0.74, cy + r * 0.02), (cx - r * 0.5, cy - h * 0.45), (cx - r * 0.14, cy - h * 0.95), (cx + r * 0.08, cy - h), (cx + r * 0.42, cy - h * 0.55),
             (cx + r * 0.74, cy + r * 0.02), (cx + r * 0.3, cy + r * 0.14), (cx - r * 0.3, cy + r * 0.14)]
    out.append(modelled(D, mound, (lt(col, 0.42), col, dk(col, 0.35)), seed + 1, light=(-0.7, -0.6), angle=-60, n=50, inkw=0, hi=0.5, core=0.4,
                        cols=[lt(col, 0.5), dk(col, 0.25), col, "#FFFFFF"], sop=(0.15, 0.4)))
    out.append(pk.dabs(seed + 2, (cx - r * 0.7, cy - h, cx + r * 0.7, cy + r * 0.1), [lt(col, 0.55), dk(col, 0.2)], int(r * 1.4), (0.5, 1.4), (0.4, 0.9)))
    out.append(pk.dabs(seed + 3, (cx - r * 1.2, cy - r * 0.1, cx + r * 1.2, cy + r * 0.5), [col, lt(col, 0.3)], int(r * 0.5), (0.6, 1.8), (0.4, 0.9)))
    out.append(f'<path d="{ellipse_d(cx, cy, r, r * 0.3)}" fill="none" stroke="#4A2A08" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<path d="M {cx - r * 0.9:.1f} {cy - r * 0.05:.1f} Q {cx - r * 0.5:.1f} {cy - r * 0.2:.1f} {cx - r * 0.1:.1f} {cy - r * 0.27:.1f}" stroke="#FFF6D0" stroke-width="2" fill="none" opacity="0.8" stroke-linecap="round"/>')
    return "".join(out)


@design("holi-hai")
def holi_hai():
    D = Doc2("in-hh")
    art = []
    VP = (300, 330)
    # sunlit haze at the end of the lane
    art.append(sky(D, [(0, "#F8E2C8"), (0.5, "#FCEAD0"), (1, "#F2C8A8")], 2301, 600, ["#FFFFFF", "#F6D8C0"], 40, angle=-4, sop=(0.05, 0.12)))
    # the lane: two rows of old houses converging on a gateway, washed in old colour
    def wall(side, seed, cols):
        rnd = random.Random(seed)
        out = []
        x_edge = -40 if side < 0 else 640
        xs = [0.0, 0.18, 0.36, 0.52, 0.66, 0.78, 0.88]
        for i, (t0, t1) in enumerate(zip(xs, xs[1:])):
            def W(t, h):            # t along the wall toward the VP (0 near .. 1 at VP), h = height factor (0 ground .. 1 roof)
                x = x_edge + (VP[0] - x_edge) * t
                yb = 640 + (VP[1] + 40 - 640) * t
                yt = -80 + (VP[1] - 70 + 80) * t
                return (x, yb + (yt - yb) * h)
            top_h = rnd.uniform(0.85, 1.0)
            c = rnd.choice(cols)
            poly = [W(t0, 0), W(t1, 0), W(t1, top_h), W(t0, top_h)]
            haze = t0 * 0.75
            out.append(f'<path d="{pdl(poly)}" fill="{mix(c, "#FCEAD0", haze)}"/>')
            out.append(f'<path d="{pdl(poly)}" fill="#4A2A3A" opacity="{max(0, 0.42 - t0 * 0.6):.2f}"/>')
            out.append(strokes(D.nid(), pdl(poly), (min(p[0] for p in poly) - 5, min(p[1] for p in poly), max(p[0] for p in poly) + 5, max(p[1] for p in poly)),
                               [mix(lt(c, 0.2), "#FCEAD0", haze), mix(dk(c, 0.15), "#FCEAD0", haze)], seed + i, n=24, angle=-90, length=(20, 70), width=(2, 6), opacity=(0.15, 0.35)))
            # a door and a window with a little balcony
            dw = [W(t0 + (t1 - t0) * 0.25, 0.02), W(t0 + (t1 - t0) * 0.6, 0.02), W(t0 + (t1 - t0) * 0.6, 0.36), W(t0 + (t1 - t0) * 0.25, 0.36)]
            out.append(f'<path d="{pdl(dw)}" fill="{mix(rnd.choice(["#2A5A8A", "#1E6A5A", "#7A2A2A"]), "#FCEAD0", haze)}"/>')
            ww_ = [W(t0 + (t1 - t0) * 0.3, 0.55), W(t0 + (t1 - t0) * 0.62, 0.55), W(t0 + (t1 - t0) * 0.62, 0.72), W(t0 + (t1 - t0) * 0.3, 0.72)]
            out.append(f'<path d="{pdl(ww_)}" fill="{mix("#3A2430", "#FCEAD0", haze)}"/>')
            bl = [W(t0 + (t1 - t0) * 0.22, 0.52), W(t0 + (t1 - t0) * 0.7, 0.52)]
            out.append(f'<path d="M {bl[0][0]:.1f} {bl[0][1]:.1f} L {bl[1][0]:.1f} {bl[1][1]:.1f}" stroke="{mix("#4A2A1A", "#FCEAD0", haze)}" stroke-width="{3 * (1 - t0):.1f}"/>')
            # splashes and handprints of colour on the plaster
            for _ in range(6):
                tt, hh = rnd.uniform(t0, t1), rnd.uniform(0.05, 0.5)
                px, py = W(tt, hh)
                sz = 18 * (1 - tt)
                out.append(f'<path d="{blob(px, py, sz, sz * 0.7, rnd.randint(0, 999), 0.35, 10)}" fill="{mix(rnd.choice(["#E8246E", "#F6C21C", "#2EB84A", "#8A3AC8", "#1EA0D8"]), "#FCEAD0", haze)}" opacity="0.55"/>')
        return "".join(out)
    art.append(wall(-1, 2302, ["#E0A878", "#C8889A", "#8AA8A0", "#E8B878"]))
    art.append(wall(1, 2303, ["#E09880", "#A898C8", "#E8C080", "#C88870"]))
    # the gateway at the end, blazing with sun
    gate = [(256, 372), (256, 300), (270, 280), (300, 268), (330, 280), (344, 300), (344, 372)]
    art.append(f'<path d="{smooth_closed(gate)}" fill="#FFF8E8"/>')
    art.append(soft_glow(D, 300, 320, 150, "#FFFFFF", 0.85))
    # the street floor, wet with coloured water, receding
    fl = [(-40, 640), (640, 640), (VP[0] + 50, VP[1] + 42), (VP[0] - 50, VP[1] + 42)]
    art.append(f'<path d="{pdl(fl)}" fill="#D8B8A8"/>')
    art.append(f'<path d="{pdl(fl)}" fill="{D.lin([(0, "#FFF0E0", 0.7), (1, "#A87A8A", 0.4)])}"/>')
    art.append(clipped(D, pdl(fl), [pk.dabs(2304, (0, 380, 600, 600), ["#E8246E", "#2EB84A", "#F6C21C", "#8A3AC8"], 120, (2, 9), (0.25, 0.6), (0.3, 0.5))]))
    # light shafts down the lane from the gateway
    for k, (x1a, x1b) in enumerate(((60, 160), (420, 520), (230, 300))):
        art.append(pk.light_shaft(D, 300, 300, x1a, x1b, 640, "#FFF6D8", 0.22))
    # the crowd in the haze: small backlit figures throwing colour, deeper ones paler
    rnd = random.Random(2310)
    crowd = []
    for k in range(13):
        depth = rnd.uniform(0.15, 1.0)
        y = VP[1] + 40 + (640 - VP[1] - 40) * (depth ** 2) * 0.42
        x = VP[0] + rnd.uniform(-1, 1) * (40 + 200 * depth ** 2)
        h = 18 + 70 * depth ** 2
        crowd.append((y, x, h, depth, k))
    for y, x, h, depth, k in sorted(crowd):
        pose = rnd.choice([dict(ua_l=-75, fa_l=-95, ua_r=-110, fa_r=-90, head=-10), dict(ua_l=-30, fa_l=-60, ua_r=70, fa_r=40),
                           dict(ua_l=-60, fa_l=-80, ua_r=-60, fa_r=-80, torso=-95), dict(ua_l=10, fa_l=-40, ua_r=100, fa_r=90, torso=-86)])
        tint = rnd.choice(["#8A3A6A", "#5A3A6A", "#7A4A3A", "#3A4A6A"])
        c = mix(tint, "#F8DCD0", 0.75 - depth * 0.55)
        art.append(figure(x, y, h, pose, c, facing=rnd.choice([1, -1]), cloth=rnd.choice(["kurta", "kurta", "sari", None]), female=rnd.random() < 0.4,
                          hair=rnd.choice(["short", "bun"]), rim="#FFF2D8" if depth > 0.5 else None, rim_side=1)[0])
    # clouds of gulal hanging in the sunlit air
    for k, (x, y, r, c) in enumerate(((150, 300, 120, "#E8246E"), (452, 286, 120, "#F6C21C"), (310, 236, 96, "#8A3AC8"), (90, 430, 90, "#2EB84A"),
                                       (520, 430, 96, "#F2701E"), (360, 380, 70, "#1EA0D8"), (230, 400, 64, "#F6C21C"))):
        art.append(gulal_cloud(D, x, y, r, c, 2320 + k, op=0.78))
    # foreground: the stone step with three brass thalis of gulal and loose rose petals
    st = pk.dens2([(-20, 520), (620, 520), (620, 640), (-20, 640)], 14)
    art.append(modelled(D, st, ("#F2DCC8", "#C8A890", "#7A5A4A"), 2330, light=(0.0, -1.0), angle=0, n=70, inkw=0, hi=0.3, core=0.25))
    art.append(f'<path d="M -20 520 L 620 520" stroke="#FFF2E0" stroke-width="3" opacity="0.8"/>')
    art.append(gulal_thali(D, 146, 548, 74, "#E8246E", 2331))
    art.append(gulal_thali(D, 454, 548, 74, "#F6C21C", 2332))
    art.append(gulal_thali(D, 300, 566, 80, "#2EB84A", 2333))
    for k in range(26):
        x, y = rnd.uniform(20, 580), rnd.uniform(580, 600)
        art.append(f'<path d="{blob(x, y, 4, 2.6, k + 2340, 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#D6244A", "#F04A6A", "#F6A21C"])}" opacity="0.85"/>')
    art.append(glaze(D, [(0, "#FFF0D8", 0.18), (1, "#8A3A6A", 0.12)]))
    art.append(vignette(D, "#5A2A40", 0.3, 0.8))
    txt = [letters(D, 300, 140, "Holi hai!", SERIF_IT, 140, "#C8185E", ["#E83A7E", "#7A0A38", "#FF6AA0"], 2350, max_w=420,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFC0D8"),
           sub(300, 186, "BURA NA MANO, HOLI HAI", "#2A2A80", font=JOS, size=20, ls=5, line_w=22, gap=12)]
    return finish_art(D, art, txt, 2351, under="#F2D8C8", edge=2.6, bristle=0.4, grain=0.16)


# ================================================================ 24. howzat! — gully cricket between the houses
def brick3(D, cam, c, size, yaw, roll, seed, pal=("#E8946A", "#B8583A", "#6A2A18"), light=(0.6, -0.3, 0.75)):
    """A brick (size = (l, w, h) cm) centred at c, turned by yaw (about z) and roll (about its long axis),
    drawn as its visible faces with paint texture."""
    l, w, h = size
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))

    def T(p):
        x, y, z = p
        y, z = y * cr - z * sr, y * sr + z * cr
        x, y = x * cy_ - y * sy_, x * sy_ + y * cy_
        return (c[0] + x, c[1] + y, c[2] + z)
    V = [T((sx * l / 2, sy * w / 2, sz * h / 2)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)]
    out = []
    vis = []
    for f in faces:
        pts3 = [V[i] for i in f]
        ctr = [sum(p[i] for p in pts3) / 4 for i in range(3)]
        cc = [sum(V[j][i] for j in range(8)) / 8 for i in range(3)]
        n = [ctr[i] - cc[i] for i in range(3)]
        to_cam = [cam.pos[i] - ctr[i] for i in range(3)]
        if sum(n[i] * to_cam[i] for i in range(3)) > 0:
            L = math.sqrt(sum(q * q for q in n)) or 1
            br = max(0, sum(n[i] / L * light[i] for i in range(3)))
            vis.append((cam.depth(ctr), pts3, br))
    for _, pts3, br in sorted(vis, reverse=True):
        pts = [cam(p) for p in pts3]
        col = mix(pal[2], pal[1], min(1, 0.35 + br)) if br < 0.65 else mix(pal[1], pal[0], (br - 0.65) / 0.35)
        d = pdl(pts)
        x0, y0, x1, y1 = bbox(pts)
        out.append(f'<path d="{d}" fill="{col}"/>')
        out.append(strokes(D.nid(), d, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), [mix(col, pal[0], 0.4), mix(col, pal[2], 0.4), "#D8B8A0"], seed, n=10, angle=-20,
                           length=(4, max(6, (x1 - x0) * 0.6)), width=(1, 3), opacity=(0.2, 0.5)))
        out.append(pk.dabs(seed + 1, (x0, y0, x1, y1), ["#5A2010", "#F2C8A0"], int(max(3, (x1 - x0) * (y1 - y0) / 60)), (0.5, 1.2), (0.3, 0.7), clip=D.clip(f'<path d="{d}"/>')))
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round" opacity="0.55"/>')
        seed += 3
    return "".join(out)


def tennis_ball(D, cx, cy, r, seed, tape="#C8281E", ang=20):
    """The gully ball: a tennis ball wound with electrical tape, fuzz on the bare felt."""
    out = [modelled(D, blob_pts(cx, cy, r, r, seed, 0.02, 18), ("#F0F890", "#C8D83A", "#6A7A12"), seed, light=(0.5, -0.7), angle=ang, n=20, inkw=1.1, hi=0.5)]
    bands = []
    for k in (-0.35, 0.3):
        band = rot([(cx - r * 1.2, cy + k * r - r * 0.16), (cx + r * 1.2, cy + k * r - r * 0.16), (cx + r * 1.2, cy + k * r + r * 0.16), (cx - r * 1.2, cy + k * r + r * 0.16)], cx, cy, ang)
        bands.append(f'<path d="{pdl(band)}" fill="{tape}"/>')
        hl = rot([(cx - r * 1.2, cy + k * r - r * 0.1), (cx + r * 1.2, cy + k * r - r * 0.1)], cx, cy, ang)
        bands.append(f'<path d="M {hl[0][0]:.1f} {hl[0][1]:.1f} L {hl[1][0]:.1f} {hl[1][1]:.1f}" stroke="#FF8A7A" stroke-width="{max(0.8, r * 0.06):.1f}" opacity="0.7"/>')
    out.append(clipped(D, ellipse_d(cx, cy, r, r), bands))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.38, r * 0.25, r * 0.16, seed + 3, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.55"/>')
    return "".join(out)


@design("howzat")
def howzat():
    D = Doc2("in-hz")
    cam = Cam3((-120, -20, 70), (900, 0, 160), f=500, cx=300, cy=410)
    art = []
    Wl, Wr = 190, -190                     # lane walls (y), the lane runs away along +x
    # golden sky in the slot between the roofs
    art.append(sky(D, [(0, "#F6D8A0"), (0.5, "#FBE8C0"), (1, "#FFF4D8")], 2401, 600, ["#FFFFFF", "#F8D8A8"], 40, angle=-4, sop=(0.06, 0.14)))
    art.append(soft_glow(D, 360, 360, 260, "#FFF8E0", 0.9))

    def side(yw, seed, cols, lit):
        rnd = random.Random(seed)
        out = []
        x = -40
        while x < 2600:
            w = rnd.uniform(240, 420)
            h = rnd.uniform(520, 760)
            c = rnd.choice(cols)
            dist = (x + w / 2) / 2600
            hz = min(0.7, dist ** 1.4 * 1.1)
            col = mix(c, "#FBE8C8", hz)
            face = [cam((x, yw, 0)), cam((x + w, yw, 0)), cam((x + w, yw, h)), cam((x, yw, h))]
            out.append(f'<path d="{pdl(face)}" fill="{col}"/>')
            if not lit:
                out.append(f'<path d="{pdl(face)}" fill="#2A1830" opacity="{0.62 * (1 - hz) ** 1.5:.2f}"/>')
            else:
                out.append(f'<path d="{pdl(face)}" fill="{D.lin([(0, "#FFE0A0", 0.35), (1, "#5A2A20", 0.35)], 0, 0, 0, 1)}" opacity="{(1 - hz):.2f}"/>')
                out.append(f'<path d="{pdl(face)}" fill="#3A1A10" opacity="{0.35 * (1 - dist * 2.5 if dist < 0.4 else 0):.2f}"/>')
            x0, y0, x1, y1 = bbox(face)
            x0, y0, x1, y1 = max(-20, x0), max(-20, y0), min(620, x1), min(620, y1)
            if x1 <= x0 or y1 <= y0:
                x += w
                continue
            out.append(strokes(D.nid(), pdl(face), (x0 - 4, y0, x1 + 4, y1), [mix(lt(c, 0.2), "#FBE8C8", hz), mix(dk(c, 0.2), "#FBE8C8", hz)], seed + int(x), n=int(min(60, max(6, (x1 - x0) * (y1 - y0) / 400))),
                               angle=-90, length=(10, 60), width=(1.5, 5), opacity=(0.15, 0.35)))
            # parapet lip, a door, a window with a balcony slab
            lip = [cam((x, yw, h)), cam((x + w, yw, h)), cam((x + w, yw - (12 if yw > 0 else -12), h + 14)), cam((x, yw - (12 if yw > 0 else -12), h + 14))]
            out.append(f'<path d="{pdl(lip)}" fill="{mix(lt(c, 0.3), "#FBE8C8", hz)}"/>')
            dx0 = x + w * rnd.uniform(0.15, 0.3)
            door = [cam((dx0, yw, 0)), cam((dx0 + 95, yw, 0)), cam((dx0 + 95, yw, 215)), cam((dx0, yw, 215))]
            out.append(f'<path d="{pdl(door)}" fill="{mix(rnd.choice(["#2E6E9A", "#1E6A5A", "#7A2A22", "#5A3A2A"]), "#FBE8C8", hz)}"/>')
            wx0 = x + w * rnd.uniform(0.45, 0.6)
            win = [cam((wx0, yw, 330)), cam((wx0 + 110, yw, 330)), cam((wx0 + 110, yw, 450)), cam((wx0, yw, 450))]
            out.append(f'<path d="{pdl(win)}" fill="{mix("#2A1E26", "#FBE8C8", hz)}"/>')
            for gx in range(1, 5):
                g0, g1 = cam((wx0 + gx * 22, yw, 330)), cam((wx0 + gx * 22, yw, 450))
                out.append(f'<path d="M {g0[0]:.1f} {g0[1]:.1f} L {g1[0]:.1f} {g1[1]:.1f}" stroke="{mix("#4A7AA0", "#FBE8C8", hz)}" stroke-width="{max(0.6, 2.5 * (1 - dist)):.1f}"/>')
            bal = [cam((wx0 - 20, yw, 318)), cam((wx0 + 130, yw, 318)), cam((wx0 + 130, yw - (60 if yw > 0 else -60), 318)), cam((wx0 - 20, yw - (60 if yw > 0 else -60), 318))]
            out.append(f'<path d="{pdl(bal)}" fill="{mix(dk(c, 0.3), "#FBE8C8", hz)}"/>')
            x += w
        return "".join(out)
    art.append(side(Wr, 2402, ["#E8A048", "#D8806A", "#B8B080", "#E8B870", "#8A9AC8"], lit=True))
    art.append(side(Wl, 2403, ["#C88A58", "#B8707A", "#7AA090", "#D8A070", "#7A88B8"], lit=False))
    # washing lines across the lane
    for k, (x, z) in enumerate(((640, 330), (1100, 420))):
        p0, p1 = cam((x, Wl, z)), cam((x + 60, Wr, z))
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 26 - k * 12)
        art.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} Q {mid[0]:.1f} {mid[1]:.1f} {p1[0]:.1f} {p1[1]:.1f}" stroke="#4A3A3A" stroke-width="1" fill="none" opacity="0.7"/>')
        rnd = random.Random(2404 + k)
        for j in range(5):
            t = (j + 1) / 6
            px = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mid[0] + t * t * p1[0]
            py = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * mid[1] + t * t * p1[1]
            sz = 9 - k * 4
            art.append(f'<path d="{smooth_closed([(px - sz * 0.6, py), (px + sz * 0.6, py), (px + sz * 0.7, py + sz * 1.6), (px - sz * 0.7, py + sz * 1.7)])}" fill="{mix(rnd.choice(["#D6342A", "#F6C21C", "#2A6AB0", "#FFFFFF", "#D6246E"]), "#FBE8C8", 0.2 + k * 0.3)}"/>')
    # the score chalked on the shady wall: RUNS and a tally
    def wl(x, z):
        return cam((x, Wl, z))
    ch = []
    for k in range(5):
        ch.append(taper([wl(400 + k * 18, 170), wl(403 + k * 18, 110)], 2.6, 2.0, "#F4F0E6", 0.85))
    ch.append(taper([wl(392, 116), wl(492, 164)], 2.6, 2.0, "#F4F0E6", 0.85))
    for k in range(3):
        ch.append(taper([wl(520 + k * 18, 170), wl(523 + k * 18, 110)], 2.6, 2.0, "#F4F0E6", 0.85))
    art.append("".join(ch))
    # the lane floor: packed earth and old paving, long shadows toward us
    fl = [cam((-30, Wl, 0)), cam((-30, Wr, 0)), cam((3000, Wr, 0)), cam((3000, Wl, 0))]
    art.append(f'<path d="{pdl(fl)}" fill="#C8A47A"/>')
    art.append(f'<path d="{pdl(fl)}" fill="{D.lin([(0, "#FFF0D0", 0.6), (0.4, "#C8A47A", 0), (1, "#7A5A3A", 0.5)])}"/>')
    art.append(clipped(D, pdl(fl), [strokes(D.nid(), pdl(fl), (-40, 380, 640, 640), ["#A8845A", "#E8D0A8", "#8A6A48", "#F2DCB8"], 2405, n=140, angle=-4, length=(20, 90), width=(2, 6), opacity=(0.15, 0.35))]))
    # sunlit strip down the middle of the lane, the shade of the left houses on the ground
    sh = [cam((-30, Wl, 0)), cam((3000, Wl, 0)), cam((3000, 40, 0)), cam((-30, -20, 0))]
    art.append(f'<path d="{pdl(sh)}" fill="#3A2440" opacity="0.32"/>')
    lit_ = [cam((-30, -20, 0)), cam((3000, 40, 0)), cam((3000, Wr, 0)), cam((-30, Wr, 0))]
    art.append(f'<path d="{pdl(lit_)}" fill="#FFE8B0" opacity="0.25"/>')
    # a charpai stood on its end against the sunny wall
    cp = [cam((520, Wr + 14, 4)), cam((700, Wr + 14, 4)), cam((700, Wr + 4, 120)), cam((520, Wr + 4, 120))]
    art.append(f'<path d="{pdl(cp)}" fill="#E8D0A0" opacity="0.5"/>')
    for k in range(9):
        t = k / 8
        a0 = (cp[0][0] + (cp[1][0] - cp[0][0]) * t, cp[0][1] + (cp[1][1] - cp[0][1]) * t)
        a1 = (cp[3][0] + (cp[2][0] - cp[3][0]) * t, cp[3][1] + (cp[2][1] - cp[3][1]) * t)
        art.append(f'<path d="M {a0[0]:.1f} {a0[1]:.1f} L {a1[0]:.1f} {a1[1]:.1f}" stroke="#C8A060" stroke-width="1"/>')
        b0 = (cp[0][0] + (cp[3][0] - cp[0][0]) * t, cp[0][1] + (cp[3][1] - cp[0][1]) * t)
        b1 = (cp[1][0] + (cp[2][0] - cp[1][0]) * t, cp[1][1] + (cp[2][1] - cp[1][1]) * t)
        art.append(f'<path d="M {b0[0]:.1f} {b0[1]:.1f} L {b1[0]:.1f} {b1[1]:.1f}" stroke="#C8A060" stroke-width="1"/>')
    art.append(f'<path d="{pdl(cp)}" fill="none" stroke="#6A4020" stroke-width="3"/>')
    # the bowler at the far end, leaping in his appeal; two fielders and a kid on a balcony
    bw = cam((1350, 10, 0))
    bwh = 170 * cam.f / cam.depth((1350, 10, 0))
    art.append(figure(bw[0], bw[1] - bwh * 0.12, bwh, dict(torso=-94, head=-18, ua_l=-74, fa_l=-96, hand_l=-100, ua_r=-108, fa_r=-86, hand_r=-80, th_l=60, sh_l=120, th_r=110, sh_r=60, ft_l=30),
                      "#3A2430", rim="#FFF0C8", rim_side=1, facing=-1, cloth=None, rim_w=1.0)[0])
    art.append(f'<path d="{blob(bw[0], bw[1], 22, 3, 2407, 0.1, 10)}" fill="#3A2440" opacity="0.35"/>')
    for k, (fx, fy, hh, pose) in enumerate(((1900, 90, 1, dict(ua_l=-60, fa_l=-90, ua_r=-120, fa_r=-90)),)):
        p = cam((fx, fy, 0))
        hpx = 168 * cam.f / cam.depth((fx, fy, 0))
        art.append(figure(p[0], p[1], hpx, pose, mix("#3A2430", "#FBE8C8", 0.35), facing=1, cloth="shorts")[0])
    # the wicket: bricks stacked in the dust, the top one knocked flying as the ball crashes in
    WX = 230
    for k in range(3):
        art.append(brick3(D, cam, (WX, 0, 3.5 + k * 7), (23, 11, 7), 90 + (k - 1) * 3, 0, 2410 + k * 5))
    art.append(brick3(D, cam, (WX - 6, 10, 34), (23, 11, 7), 60, 35, 2420))
    dc = cam((WX, 0, 26))
    art.append(soft_glow(D, dc[0] + 6, dc[1] - 6, 50, "#F8E8C8", 0.6))
    art.append(pk.dabs(2430, (dc[0] - 40, dc[1] - 40, dc[0] + 50, dc[1] + 24), ["#E8C8A0", "#B8583A", "#FFF0D8"], 40, (0.6, 2.2), (0.4, 0.9)))
    for k in range(7):
        a_ = math.radians(-160 + k * 22)
        p0 = (dc[0] + math.cos(a_) * 22, dc[1] + math.sin(a_) * 18)
        p1 = (dc[0] + math.cos(a_) * 38, dc[1] + math.sin(a_) * 30)
        art.append(taper([p0, p1], 1.8, 0.4, "#FFF4E0", 0.75))
    # the ball, just bounced off the bricks, and its motion trail from the bowler
    art.append(taper([(bw[0] - 4, bw[1] - 30), (dc[0] + 50, dc[1] - 40), (dc[0] + 26, dc[1] - 18)], 0.6, 8, "#FFFFFF", 0.35))
    art.append(tennis_ball(D, dc[0] + 22, dc[1] - 20, 11, 2431))
    # the bat flung down in the foreground, the chalk crease
    bat = [(118, 590), (330, 540), (336, 556), (124, 612)]
    art.append(f'<path d="{blob(150, 590, 96, 8, 2432, 0.1, 14, -18)}" fill="#3A2418" opacity="0.35"/>')
    art.append(modelled(D, pk.dens2([(40, 600), (196, 552), (202, 568), (48, 618)], 10), ("#FBE6B8", "#E2B87A", "#8A6438"), 2433, light=(-0.3, -1), angle=-18, n=40, inkw=1.4, hi=0.45))
    art.append(modelled(D, pk.dens2([(196, 556), (262, 536), (266, 546), (200, 565)], 8), ("#5A6A9A", "#2A3A6A", "#0E1630"), 2434, light=(-0.3, -1), angle=-18, n=12, inkw=1.2, hi=0.3))
    for k in range(5):
        x = 206 + k * 11
        art.append(f'<path d="M {x:.1f} {556 - k * 3.4:.1f} l 3 8" stroke="#8A9AC8" stroke-width="1.5"/>')
    art.append(taper([cam((150, 160, 0)), cam((150, -160, 0))], 3, 3, "#FFFFFF", 0.6))
    art.append(glaze(D, [(0, "#2A1A30", 0.45), (0.22, "#2A1A30", 0), (0.78, "#3A2010", 0), (1, "#3A2010", 0.35)], 0, 0, 1, 0))
    art.append(glaze(D, [(0, "#FFE8B0", 0.15), (0.6, "#FFE8B0", 0), (1, "#4A2A40", 0.2)]))
    art.append(vignette(D, "#3A1E10", 0.32, 0.8))
    art.append(f'<ellipse cx="300" cy="150" rx="300" ry="80" fill="{D.rad([(0, "#FBEBD0", 0.85), (0.6, "#FBEBD0", 0.55), (1, "#FBEBD0", 0)])}"/>')
    txt = [letters(D, 300, 140, "Howzat!", SERIF_IT, 150, "#1E3A7A", ["#2E5AA8", "#0E1E4A", "#4A7AC8"], 2440, max_w=420,
                   shadow="#FFF4D8", soff=(0.022, 0.035), angle=-40, hi="#C8D8F8"),
           sub(300, 186, "GULLY CRICKET · ONE TIP, ONE HAND", "#7A2A10", font=JOS, size=18, ls=4, line_w=16, gap=10)]
    return finish_art(D, art, txt, 2441, under="#E8C890", edge=2.6, bristle=0.45, grain=0.18)


# ================================================================ 25. maa ke haath ka khana — the thali, and माँ painted in brush
def _bpoly(pts, w, taper_end=0.6):
    """Outline of a brush stroke along pts: pressed start, lean middle, lifted end."""
    cp = catmull(pts, 8) if len(pts) > 2 else [(pts[0][0] + (pts[1][0] - pts[0][0]) * t / 12, pts[0][1] + (pts[1][1] - pts[0][1]) * t / 12) for t in range(13)]
    n = len(cp)
    left, right = [], []
    for i, (x, y) in enumerate(cp):
        a, b = cp[max(i - 1, 0)], cp[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ls = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ls, dx / Ls
        t = i / max(1, n - 1)
        k = (1.1 if t < 0.08 else 1.0 - 0.12 * math.sin(math.pi * t)) * (1 - (1 - taper_end) * max(0, (t - 0.85) / 0.15))
        ww = w * k / 2
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    return left + right[::-1], cp


def maa_devanagari(D, x, y, h, color, seed, shadow=None, paper_c="#FFFFFF"):
    """माँ painted stroke by stroke (no font). (x, y) = top-left of the glyph box; h = height from the chandrabindu
    to the foot of the stems. Shape checked against a Devanagari reference rendering: shirorekha across the top,
    म = left stroke with its foot-knob + mid crossbar + full stem, ा = second full stem, ँ = crescent and dot
    above the ा."""
    s = h / 370
    w = 30 * s
    rnd = random.Random(seed)

    def P(pts):
        return [(x + px * s + rnd.uniform(-0.6, 0.6), y + py * s + rnd.uniform(-0.6, 0.6)) for px, py in pts]

    strokes_ = [
        (P([(6, 124), (220, 126), (424, 124)]), w * 1.02, 0.85),        # shirorekha
        (P([(60, 138), (61, 210), (60, 272)]), w, 0.9),                  # म left stroke
        (P([(62, 243), (130, 245), (190, 243)]), w * 0.9, 0.9),          # म crossbar
        (P([(190, 136), (191, 260), (190, 366)]), w, 0.5),               # म stem
        (P([(316, 136), (317, 260), (316, 366)]), w, 0.5),               # ा stem
        (P([(250, 10), (268, 42), (308, 62), (350, 54), (372, 30), (364, 10)]), w * 0.62, 0.7),   # ँ crescent
    ]
    polys = [_bpoly(p, ww, te) for p, ww, te in strokes_]
    knob = blob(x + 40 * s, y + 268 * s, 26 * s, 18 * s, seed, 0.12, 12, -24)
    dot = smooth_closed(P([(313, 8), (330, 26), (313, 44), (296, 26)]))
    out = []
    if shadow:
        out.append(f'<g transform="translate({h * 0.02:.1f} {h * 0.025:.1f})" fill="{shadow}">' + "".join(f'<path d="{smooth_closed(p)}"/>' for p, _ in polys) + f'<path d="{knob}"/><path d="{dot}"/></g>')
    for p, cp in polys:
        d = smooth_closed(p)
        out.append(f'<path d="{d}" fill="{color}"/>')
        ex, ey = cp[0]
        out.append(f'<path d="{blob(ex, ey, w * 0.58, w * 0.5, seed + int(ex), 0.12, 10)}" fill="{color}"/>')
        st = []
        for _ in range(3):
            off = rnd.uniform(-0.3, 0.3) * w
            a0 = rnd.randint(len(cp) // 2, max(len(cp) // 2, len(cp) - 3))
            seg = cp[a0:]
            if len(seg) < 2:
                continue
            dx, dy = seg[-1][0] - seg[0][0], seg[-1][1] - seg[0][1]
            Ls = math.hypot(dx, dy) or 1
            nx, ny = -dy / Ls, dx / Ls
            st.append(taper([(px + nx * off, py + ny * off) for px, py in seg], 0.5, rnd.uniform(1.2, 2.6), paper_c, rnd.uniform(0.35, 0.65)))
        out.append(clipped(D, d, st))
    out.append(f'<path d="{knob}" fill="{color}"/><path d="{dot}" fill="{color}"/>')
    return "".join(out)


def bowl_food(D, cx, cy, r, kind, seed):
    rnd = random.Random(seed)
    E = ellipse_d(cx, cy, r, r)
    if kind == "dal":
        base, hi_, bits = "#F2B21E", "#FFD45A", [("#7A3A10", 18, 1.6), ("#C8281E", 6, 2.2), ("#3E8A2A", 8, 2.6)]
    elif kind == "palak":
        base, hi_, bits = "#3E7A2A", "#6AA84A", [("#FFF4D8", 8, 4), ("#E8D8B0", 6, 3)]
    elif kind == "raita":
        base, hi_, bits = "#F6F2E6", "#FFFFFF", [("#8A5A2A", 16, 1.4), ("#C8301E", 6, 1.2), ("#5AA03A", 8, 2.2)]
    elif kind == "kheer":
        base, hi_, bits = "#F4E2C0", "#FFF6E0", [("#E8901A", 10, 1.2), ("#7AB04A", 6, 2.6), ("#C89A5A", 6, 3)]
    else:  # chhole
        base, hi_, bits = "#8A4A1E", "#B8702E", [("#D8A06A", 22, 4.6), ("#3E8A2A", 6, 2.4), ("#F2E6C0", 5, 3)]
    out = [f'<path d="{E}" fill="{base}"/>']
    inner = [f'<path d="{blob(cx - r * 0.25, cy - r * 0.25, r * 0.5, r * 0.32, seed, 0.2, 10)}" fill="{hi_}" opacity="0.7"/>']
    for col, n, sz in bits:
        for _ in range(n):
            a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.85
            px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            inner.append(f'<path d="{blob(px, py, sz, sz * 0.75, rnd.randint(0, 9999), 0.2, 7, rnd.uniform(0, 180))}" fill="{col}"/>')
    inner.append(f'<path d="{E}" fill="{D.rad([(0, "#FFFFFF", 0), (0.75, "#000000", 0), (1, "#000000", 0.4)])}"/>')
    out.append(clipped(D, E, inner))
    return "".join(out)


def katori_food(D, cx, cy, r, kind, seed):
    out = [f'<path d="{ellipse_d(cx + 4, cy + 6, r + 7, r + 7)}" fill="#2A3038" opacity="0.3"/>']
    out.append(f'<path d="{ellipse_d(cx, cy, r + 7, r + 7)}" fill="#E8ECF0"/>')
    g = D.lin([(0, "#FFFFFF", 1), (0.5, "#B8C0C8", 1), (1, "#6E7884", 1)], 0, 0, 1, 1)
    out.append(f'<path d="{ellipse_d(cx, cy, r + 7, r + 7)}" fill="{g}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, r + 1, r + 1)}" fill="#5E6874"/>')
    out.append(bowl_food(D, cx, cy, r - 1, kind, seed))
    out.append(f'<path d="{ellipse_d(cx, cy, r + 7, r + 7)}" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.5"/>')
    out.append(f'<path d="M {cx - r * 0.7:.1f} {cy - r * 0.86:.1f} A {r + 4:.1f} {r + 4:.1f} 0 0 1 {cx + r * 0.2:.1f} {cy - r - 4:.1f}" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="0.9" stroke-linecap="round"/>')
    return "".join(out)


def roti_fold(D, cx, cy, r, ang, seed):
    """A roti folded into a quarter: a fan shape with a curved edge, char spots and a ghee sheen."""
    a0 = math.radians(ang)
    pts = [(cx, cy)] + [(cx + math.cos(a0 + t * math.pi / 2) * r, cy + math.sin(a0 + t * math.pi / 2) * r) for t in [i / 10 for i in range(11)]]
    out = [painted(D, pts, ("#FCEBC0", "#E8C78A", "#A8783A"), seed, sk=0.15, angle=ang + 45, n=10, cols=["#FFF6DA", "#C89A5A"], inkw=1.4, hi=0.4)]
    rnd = random.Random(seed)
    sp = []
    for _ in range(14):
        t, rr = rnd.random(), rnd.uniform(0.25, 0.9) * r
        x, y = cx + math.cos(a0 + t * math.pi / 2) * rr, cy + math.sin(a0 + t * math.pi / 2) * rr
        sp.append(f'<path d="{blob(x, y, rnd.uniform(2, 5), rnd.uniform(1.5, 3.5), rnd.randint(0, 999), 0.3, 7)}" fill="#8A4A14" opacity="0.6"/>')
    sp.append(f'<path d="{blob(cx + math.cos(a0 + 0.8) * r * 0.5, cy + math.sin(a0 + 0.8) * r * 0.5, r * 0.25, r * 0.12, seed, 0.3, 8)}" fill="#FFF6C8" opacity="0.5"/>')
    out.append(clipped(D, smooth_closed(pts), sp))
    return "".join(out)


@design("maa-ke-haath-ka-khana")
def maa_ke_haath():
    D = Doc2("in-mk")
    # a woven straw mat with a red-and-saffron border, a warm afternoon light
    out = [f'<rect width="600" height="600" fill="#E2B878"/>']
    weave = []
    for y in range(0, 620, 10):
        for x in range(0, 620, 20):
            xx = x + (10 if (y // 10) % 2 else 0)
            weave.append(f'<path d="M {xx} {y + 5} l 16 0" stroke="{["#C8964E", "#F0CC8C"][(x // 20 + y // 10) % 2]}" stroke-width="6" stroke-linecap="round" opacity="0.7"/>')
    out.append("".join(weave))
    out.append(strokes(D.nid(), "M -10 250 L 610 250 L 610 610 L -10 610 Z", (-40, 250, 620, 610), ["#B8843E", "#F6D498", "#8A5A24"], 2540, n=220, angle=-4, length=(20, 70), width=(2, 5), opacity=(0.12, 0.3)))
    out.append(f'<rect x="-10" y="250" width="620" height="360" fill="{D.rad([(0, "#FFF0C8", 0.35), (0.6, "#FFF0C8", 0), (1, "#3A1A08", 0.4)], 0.5, 0.45, 0.7)}"/>')
    for y, c in ((256, "#C8281E"), (266, "#F2901E"), (276, "#C8281E")):
        out.append(f'<path d="{smooth_open(jitter([(x, y) for x in range(-10, 620, 40)], y, 1.0))}" stroke="{c}" stroke-width="6" opacity="0.9" fill="none"/>')
    out.append(f'<path d="M -10 0 L 610 0 L 610 250 L -10 250 Z" fill="#FBF1DE"/>')
    out.append(paper(D.nid(), "#FBF1DE", FLECK, 2501).replace('<rect width="600" height="600" fill="#FBF1DE"/>', '').replace('height="600" fill="url', 'height="250" fill="url'))
    out.append(f'<rect y="246" width="600" height="6" fill="#8A5A2A" opacity="0.35"/>')
    out.append(soft_glow(D, 300, 430, 280, "#FFF0C8", 0.35))
    # the steel thali
    cx, cy, R = 300, 424, 172
    out.append(f'<path d="{ellipse_d(cx + 10, cy + 14, R + 4, R + 4)}" fill="#3A2410" opacity="0.35"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, R, R)}" fill="#C8CED6"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, R, R)}" fill="{D.lin([(0, "#FFFFFF", 1), (0.5, "#BCC4CC", 1), (1, "#6E7884", 1)], 0, 0, 1, 1)}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, R - 16, R - 16)}" fill="#9AA2AC"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, R - 18, R - 18)}" fill="{D.lin([(0, "#8A929C", 1), (0.55, "#D8DEE4", 1), (1, "#F4F6F8", 1)], 0, 0, 1, 1)}"/>')
    out.append(f'<path d="M {cx - R * 0.8:.1f} {cy - R * 0.5:.1f} A {R - 6} {R - 6} 0 0 1 {cx + R * 0.05:.1f} {cy - R + 6:.1f}" stroke="#FFFFFF" stroke-width="3.4" fill="none" opacity="0.9" stroke-linecap="round"/>')
    out.append(ink(ellipse_d(cx, cy, R, R), INK, 2, 2502, 1, 0.6))
    # katoris along the top arc, rice in the middle, rotis, salad, pickle and papad below
    for k, (a, kind) in enumerate(((-158, "chhole"), (-120, "dal"), (-82, "palak"), (-44, "raita"), (-8, "kheer"))):
        rr = math.radians(a)
        out.append(katori_food(D, cx + math.cos(rr) * 112, cy + math.sin(rr) * 112, 32, kind, 2503 + k))
    rice = blob_pts(cx + 4, cy + 14, 52, 40, 2510, 0.08, 16)
    out.append(painted(D, rice, ("#FFFFFF", "#F6F0E2", "#C8BCA8"), 2510, sk=0.15, n=6, inkw=1.2, hi=0.5))
    rnd = random.Random(2511)
    out.append(clipped(D, smooth_closed(rice), [f'<path d="{blob(cx + 4 + rnd.uniform(-46, 46), cy + 14 + rnd.uniform(-34, 34), 4, 1.4, rnd.randint(0, 999), 0.1, 6, rnd.uniform(-40, 40))}" fill="{rnd.choice(["#FFFFFF", "#E8E0D0", "#D8CCB8"])}"/>' for _ in range(120)]))
    out.append(f'<path d="{blob(cx + 2, cy + 6, 14, 8, 2512, 0.2, 10)}" fill="#F6D86A" opacity="0.8"/>')
    out.append(leaf_simple(D, cx + 24, cy - 6, 18, 6, -30, ("#8AD06A", "#3E9A3A", "#1A5A1A"), 2513, vein=False, inkw=0.7))
    out.append(roti_fold(D, cx - 128, cy + 30, 72, -10, 2514))
    out.append(roti_fold(D, cx - 116, cy + 44, 72, -2, 2515))
    pkl = blob_pts(cx + 88, cy + 78, 24, 16, 2516, 0.15, 12)
    out.append(painted(D, pkl, ("#E8603A", "#B8301E", "#6A0E0A"), 2516, sk=0.2, n=6, inkw=1.2, hi=0.4))
    for k in range(6):
        out.append(f'<path d="{blob(cx + 88 + rnd.uniform(-16, 16), cy + 78 + rnd.uniform(-9, 9), 5, 4, 2517 + k, 0.3, 8)}" fill="#F2A01E" opacity="0.8"/>')
    out.append(onion_ring(D, cx + 112, cy + 26, 16, 2520, 10))
    out.append(lemon_wedge(D, cx + 130, cy + 46, 18, 2521, 30))
    for k in range(3):
        out.append(f'<path d="{blob(cx + 122 + k * 11, cy + 2 - k * 6, 8, 3, 2522 + k, 0.2, 8, 40)}" fill="#7AC04A"/>')
    pp = blob_pts(cx - 20, cy + 110, 46, 24, 2525, 0.06, 18)
    out.append(painted(D, pp, ("#FFF4C8", "#F2D890", "#B89A50"), 2525, sk=0.12, n=6, inkw=1.2, hi=0.4))
    out.append(specks(2526, (cx - 58, cy + 94, cx + 18, cy + 126), ["#2A1A10", "#C89A40", "#FFFFFF"], 30, (0.7, 1.6), (0.5, 0.9)))
    out.append(pk.steam_plume(D, [(cx - 70, cy - 120), (cx - 84, cy - 150), (cx - 66, cy - 176)], 10, 18, 2527, "#FFFFFF", 0.55, puffs=False))
    out.append(pk.steam_plume(D, [(cx + 16, cy - 2), (cx + 4, cy - 40), (cx + 20, cy - 74)], 10, 20, 2528, "#FFFFFF", 0.5, puffs=False))
    out.append(glaze(D, [(0, "#FFF0D0", 0.1), (0.6, "#FFF0D0", 0), (1, "#3A1A08", 0.18)], 0, 0, 1, 1))
    # lettering: माँ painted in the brush, then the rest of the phrase
    txt = [maa_devanagari(D, 110, 58, 132, "#B8201E", 2530, shadow="#F2C8A8", paper_c="#FBF1DE"),
           letters(D, 390, 132, "ke haath", SERIF_IT, 58, "#7A2410", ["#A83A1A", "#5A1406", "#C8502A"], 2531, max_w=260,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40),
           letters(D, 390, 186, "ka khana", SERIF_IT, 58, "#7A2410", ["#A83A1A", "#5A1406", "#C8502A"], 2532, max_w=260,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40),
           sub(300, 228, "MAA · MOM'S HOME COOKING", "#5A3A1A", font=JOS, size=19, ls=5, line_w=22, gap=12)]
    return finish_art(D, out, txt, 2533, under="#E2B878", edge=2.2, bristle=0.4, grain=0.16)


# ================================================================ 26. nani's kitchen — the steel rack, the achaar jar in the sun
def plate_on_edge(D, cx, base, r, seed, sq=0.26, light=-1):
    """A steel thali standing on its rim in a rack, seen nearly edge-on: a tall narrow ellipse with a bright
    rolled rim, a dark reflection of the room in its well and a hot highlight."""
    d = blob(cx, base - r, r * sq, r, seed, 0.005, 28)
    g = D.lin([(0, "#FFFFFF"), (0.25, "#C8D0D8"), (0.5, "#7A848E"), (0.75, "#D8DEE4"), (1, "#5A626C")], cx - r * sq, 0, cx + r * sq, 0, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{g}"/>']
    out.append(f'<path d="{blob(cx + r * sq * 0.18, base - r, r * sq * 0.62, r * 0.84, seed + 1, 0.005, 24)}" fill="{D.lin([(0, "#4A525C"), (0.5, "#A8B0BA"), (1, "#E8ECF0")], 0, 0, 0, 1)}" opacity="0.8"/>')
    out.append(taper([(cx - r * sq * 0.5, base - r * 1.7), (cx - r * sq * 0.6, base - r), (cx - r * sq * 0.45, base - r * 0.35)], max(1.2, r * 0.05), max(0.6, r * 0.02), "#FFFFFF", 0.85))
    out.append(f'<path d="{d}" fill="none" stroke="#3A3E46" stroke-width="1" opacity="0.55"/>')
    return "".join(out)


def achaar_jar(D, cx, base, w, h, seed, cloth_c="#D6342A", glaze=("#FFF6E0", "#EEDDBA", "#A8906A"), shoulder="#8A4A1E", lit=1.0):
    """Ceramic barni: cream glazed belly, a brown glazed shoulder, muslin tied over the mouth with string."""
    top = base - h
    body = [(cx - w * 0.3, top + h * 0.12), (cx - w * 0.5, top + h * 0.4), (cx - w * 0.48, top + h * 0.8), (cx - w * 0.36, base), (cx + w * 0.36, base),
            (cx + w * 0.48, top + h * 0.8), (cx + w * 0.5, top + h * 0.4), (cx + w * 0.3, top + h * 0.12)]
    out = [f'<path d="{blob(cx + w * 0.3, base + 3, w * 0.7, 6, seed, 0.1, 12)}" fill="#1A0E08" opacity="0.35"/>']
    out.append(modelled(D, body, glaze, seed, light=(-0.7, -0.5), angle=-90, n=24, inkw=1.4, hi=0.55 * lit, core=0.45))
    sh = [(cx - w * 0.3, top + h * 0.12), (cx - w * 0.47, top + h * 0.36), (cx + w * 0.47, top + h * 0.36), (cx + w * 0.3, top + h * 0.12)]
    out.append(clipped(D, smooth_closed(body), [f'<path d="{smooth_closed(sh + [(cx, top + h * 0.42)])}" fill="{shoulder}"/>',
                                                f'<path d="{smooth_closed(sh + [(cx, top + h * 0.42)])}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, "#000000", 0.3)], 0, 0, 1, 0)}"/>',
                                                f'<path d="M {cx - w:.1f} {top + h * 0.38:.1f} Q {cx:.1f} {top + h * 0.48:.1f} {cx + w:.1f} {top + h * 0.38:.1f}" stroke="#4A2008" stroke-width="2" fill="none" opacity="0.5"/>']))
    out.append(taper([(cx - w * 0.32, top + h * 0.45), (cx - w * 0.38, top + h * 0.7)], max(2, w * 0.08), max(1, w * 0.03), "#FFFFFF", 0.7 * lit))
    cl = [(cx - w * 0.36, top + h * 0.16), (cx - w * 0.3, top - h * 0.06), (cx, top - h * 0.12), (cx + w * 0.3, top - h * 0.06), (cx + w * 0.36, top + h * 0.16),
          (cx + w * 0.42, top + h * 0.3), (cx + w * 0.28, top + h * 0.22), (cx, top + h * 0.2), (cx - w * 0.28, top + h * 0.22), (cx - w * 0.42, top + h * 0.3)]
    out.append(modelled(D, cl, (lt(cloth_c, 0.4), cloth_c, dk(cloth_c, 0.35)), seed + 1, light=(-0.6, -0.7), angle=-60, n=10, inkw=1.2, hi=0.35))
    out.append(taper([(cx - w * 0.33, top + h * 0.12), (cx, top + h * 0.16), (cx + w * 0.33, top + h * 0.12)], 2.6, 2.6, "#F4E6C8"))
    return "".join(out)


@design("nanis-kitchen")
def nanis_kitchen():
    D = Doc2("in-nk")
    art = []
    # an old kitchen wall in faded duck-egg green, sunlight raking in from a window at the left
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#8EBCAA"/>')
    art.append(sky(D, [(0, "#7AAE9C"), (0.6, "#9CC8B4"), (1, "#7AA894")], 2701, 470, ["#B8DCC8", "#5A8A78", "#A8D0BC"], 140, angle=-84, sop=(0.08, 0.2)))
    art.append(blooms(2702, ["#5A8A78", "#D8F0E0", "#C8A880"], 10, (0, 0, 600, 460), (40, 110), (0.08, 0.18)))
    # the window: morning blaze, iron bars, a curry-leaf branch outside
    win = pk.dens2([(-20, 170), (150, 170), (150, 380), (-20, 380)], 12)
    art.append(f'<path d="{smooth_closed(win)}" fill="{D.lin([(0, "#FFFBEA"), (1, "#F8E8B8")])}"/>')
    for x_ in (16, 52, 88, 124):
        art.append(f'<path d="M {x_} 170 L {x_} 380" stroke="#3A4A44" stroke-width="3.4"/>')
    art.append(f'<path d="{smooth_closed(win)}" fill="none" stroke="#5A6A5A" stroke-width="10"/>')
    art.append(f'<path d="M -20 386 L 170 386 L 170 398 L -20 398 Z" fill="#C8B49A"/>')
    # the sunbeam slanting across the room, and its pool on the far wall
    art.append(f'<rect x="-10" y="-10" width="620" height="470" fill="{D.lin([(0, "#000000", 0), (0.4, "#0A2A20", 0.1), (1, "#0A2A20", 0.32)], 0, 0, 1, 0)}"/>')
    for k, (y0_, y1_) in enumerate(((176, 236), (250, 310), (322, 376))):
        art.append(f'<path d="M 150 {y0_} L 150 {y1_} L 620 {y1_ + 230} L 620 {y0_ + 170} Z" fill="{D.lin([(0, "#FFF8D8", 0.32), (1, "#FFF8D8", 0)], 150, 0, 620, 0, "userSpaceOnUse")}"/>')
    art.append(soft_glow(D, 470, 400, 120, "#FFF2C8", 0.35))
    art.append(pk.dabs(2703, (160, 200, 560, 520), ["#FFFFFF", "#FFF4C8"], 60, (0.6, 1.4), (0.4, 0.9)))
    # the plate rack: a wooden shelf with steel thalis on edge, tumblers turned upside down, katoris
    sh_ = pk.dens2([(196, 300), (560, 300), (560, 314), (196, 314)], 10)
    art.append(modelled(D, sh_, ("#C8946A", "#8A5A34", "#3A2410"), 2704, light=(-0.6, -0.8), angle=0, n=16, inkw=1.2, hi=0.4))
    art.append(f'<path d="M 196 230 L 560 230" stroke="#6A4424" stroke-width="3"/>')
    for k in range(8):
        art.append(plate_on_edge(D, 214 + k * 18, 300, 50 - abs(k - 3.5) * 1.2, 2705 + k))

    for k in range(3):
        tb, _ = pk.metal_cyl(D, 404 + k * 34, 248, 298, 14, 4, 2720 + k, light=-1, taper_=-0.15, gloss=0.8, inkw=1.0)
        art.append(tb)
        art.append(f'<path d="{blob(404 + k * 34, 248, 12, 3.5, 2723 + k, 0.01, 16)}" fill="#E8ECF0"/>')
    for k in range(3):
        cx_ = 506 + k * 0 
    art.append(f'<path d="{blob(520, 296, 30, 6, 2726, 0.02, 16)}" fill="#8A929C"/>')
    for k in range(3):
        kb, _ = pk.metal_cyl(D, 520, 284 - k * 12, 296 - k * 12, 28 - k * 2, 6, 2727 + k, light=-1, taper_=0.25, gloss=0.6, inkw=0.9)
        art.append(kb)
    # brass lota and a copper pot catching the beam on the top shelf
    art.append(f'<path d="{blob(236, 454, 40, 5, 2735, 0.1, 12)}" fill="#000000" opacity="0.35"/>')
    lota = [(204, 454), (250, 454), (262, 426), (246, 406), (240, 388), (222, 388), (216, 406), (196, 426)]
    art.append(modelled(D, lota, ("#FFE8A0", "#D8A048", "#7A5014"), 2730, light=(-0.8, -0.5), angle=-90, n=14, inkw=1.2, hi=0.6, core=0.5))
    art.append(f'<path d="{blob(456, 454, 50, 6, 2736, 0.1, 12)}" fill="#000000" opacity="0.35"/>')
    cop = [(408, 454), (478, 454), (492, 424), (474, 400), (414, 400), (396, 424)]
    art.append(modelled(D, cop, ("#F8B080", "#C8643A", "#5A2010"), 2731, light=(-0.8, -0.5), angle=-90, n=14, inkw=1.2, hi=0.55, core=0.5))
    art.append(f'<path d="{blob(444, 400, 32, 6, 2732, 0.01, 16)}" fill="#7A3014"/>')
    # the stone counter, jars in the sun, the rolling board with a roti half-rolled
    ctr = pk.dens2([(-20, 450), (620, 450), (620, 620), (-20, 620)], 14)
    art.append(f'<path d="{smooth_closed(ctr)}" fill="#3A3634"/>')
    art.append(f'<path d="{smooth_closed(ctr)}" fill="{D.lin([(0, "#6A625A", 0.6), (1, "#1A1614", 0.4)])}"/>')
    art.append(pk.dabs(2733, (-20, 450, 620, 620), ["#8A8278", "#1A1816", "#B8AC98"], 260, (0.6, 2), (0.3, 0.8)))
    art.append(f'<path d="M -20 452 L 620 452" stroke="#A89C8C" stroke-width="3"/>')
    art.append(f'<path d="M 150 452 L 600 560 L 620 620 L 300 620 Z" fill="#FFF0C8" opacity="0.08"/>')
    art.append(achaar_jar(D, 68, 470, 70, 96, 2740, "#D6342A"))
    art.append(achaar_jar(D, 136, 470, 52, 72, 2741, "#F2A21E", glaze=("#FFF2DC", "#E2C8A0", "#9A7A54"), shoulder="#5A3418"))
    art.append(achaar_jar(D, 534, 466, 48, 64, 2742, "#2E6AA8", lit=0.6))
    cb = (330, 540)
    art.append(f'<path d="{blob(cb[0] + 14, cb[1] + 20, 120, 14, 2743, 0.1, 16)}" fill="#000000" opacity="0.35"/>')
    board = [(cb[0] + 104 * math.cos(math.radians(a)), cb[1] + 40 * math.sin(math.radians(a))) for a in range(0, 360, 15)]
    art.append(f'<path d="{smooth_closed([(x, y + 10) for x, y in board])}" fill="#6A4424"/>')
    art.append(modelled(D, board, ("#F2D0A0", "#C89A64", "#7A5430"), 2744, light=(-0.7, -0.6), angle=0, n=30, inkw=1.2, hi=0.45))
    art.append(roti(D, cb[0] - 8, cb[1] - 4, 70, 26, 2745))
    art.append(pk.dabs(2746, (cb[0] - 90, cb[1] - 30, cb[0] + 90, cb[1] + 30), ["#FFFFFF", "#F4ECD8"], 40, (0.6, 1.6), (0.4, 0.9)))
    pin = [(170, 600), (190, 586), (480, 498), (494, 506), (476, 520), (186, 610)]
    art.append(modelled(D, pk.dens2([(186, 592), (474, 506), (482, 518), (194, 606)], 10), ("#F6DCA8", "#D2A468", "#7A5428"), 2747, light=(-0.6, -0.8), angle=-17, n=20, inkw=1.2, hi=0.5))
    for x0_, y0_, x1_, y1_ in ((150, 606, 188, 596), (478, 510, 516, 500)):
        art.append(taper([(x0_, y0_), (x1_, y1_)], 9, 7, "#A8743A"))
    # a steel katori of atta and a flutter of flour
    kt, _ = pk.metal_cyl(D, 520, 520, 548, 38, 10, 2748, light=-1, taper_=0.3, gloss=0.7)
    art.append(f'<path d="{blob(536, 552, 44, 6, 2749, 0.1, 12)}" fill="#000000" opacity="0.35"/>')
    art.append(kt)
    art.append(pk.metal_ellipse(D, 520, 520, 38, 10, 2750, inner_pal=("#FFFFFF", "#F2EAD8", "#C8BCA4"), rim_w=3))
    art.append(f'<path d="{blob(520, 518, 26, 6, 2751, 0.15, 12)}" fill="#FBF6EC"/>')
    art.append(glaze(D, [(0, "#FFF4D8", 0.18), (0.5, "#FFF4D8", 0), (1, "#1A2A2A", 0.25)], 0, 0, 1, 0.6))
    art.append(vignette(D, "#1A2420", 0.35, 0.8))
    txt = [letters(D, 300, 104, "Nani's kitchen", SERIF_IT, 92, "#1E4A3A", ["#2E6A4A", "#0E2A1E", "#4A8A6A"], 2760, max_w=460,
                   shadow="#F4FFF4", soff=(0.022, 0.035), angle=-40, hi="#C8F0D8"),
           sub(300, 146, "BEST FOOD IN THE WHOLE WORLD", "#6A2410", font=JOS, size=19, ls=5, line_w=18, gap=10)]
    return finish_art(D, art, txt, 2761, under="#8EBCAA", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 27. rakhi — the thread, the plate, the promise
def rakhi_charm(D, cx, cy, r, seed, ang=0):
    """A rakhi: a red-and-gold twisted thread with a big centre rosette (gota petals, beads, a stone) and tassels."""
    rnd = random.Random(seed)
    out = []
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    for side in (-1, 1):
        pts = [(cx + side * ux * r * 0.8, cy + side * uy * r * 0.8), (cx + side * ux * r * 2.2 - uy * r * 0.3, cy + side * uy * r * 2.2 + ux * r * 0.3),
               (cx + side * ux * r * 3.4 + uy * r * 0.2 * side, cy + side * uy * r * 3.4 + r * 0.6)]
        out.append(taper(pts, r * 0.16, r * 0.12, "#C8201E"))
        cp = catmull(pts, 10)
        for i in range(0, len(cp) - 1, 2):
            x, y = cp[i]
            out.append(f'<path d="M {x - r * 0.06:.1f} {y - r * 0.06:.1f} l {r * 0.1:.1f} {r * 0.1:.1f}" stroke="#F6C21C" stroke-width="{max(1.2, r * 0.035):.1f}"/>')
        ex, ey = pts[-1]
        for k in range(5):
            out.append(taper([(ex, ey), (ex + (k - 2) * r * 0.06, ey + r * 0.5)], r * 0.05, r * 0.03, ["#C8201E", "#F6C21C"][k % 2]))
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r * 0.1:.1f}" fill="#F6C21C"/>')
    # rosette: two rings of petals, a ring of pearls, a central stone
    for ring, (rr, n, col) in enumerate(((0.98, 16, ("#FFE48A", "#E8A81E", "#8A5A06")), (0.7, 12, ("#FF8AB8", "#D6246E", "#8A0E40")))):
        for i in range(n):
            t = 2 * math.pi * i / n + ring * 0.2
            out.append(painted(D, blob_pts(cx + math.cos(t) * r * rr * 0.62, cy + math.sin(t) * r * rr * 0.62, r * 0.26 * (1.2 - ring * 0.3), r * 0.16, seed + i + ring * 20, 0.1, 10, rot=math.degrees(t)),
                               col, seed + i + ring * 20, sk=0.2, n=2, inkw=0.9, hi=0.5))
    for i in range(14):
        t = 2 * math.pi * i / 14
        out.append(f'<circle cx="{cx + math.cos(t) * r * 0.36:.1f}" cy="{cy + math.sin(t) * r * 0.36:.1f}" r="{r * 0.07:.1f}" fill="#FFFDF4" stroke="#C8B8A0" stroke-width="0.8"/>')
    out.append(painted(D, blob_pts(cx, cy, r * 0.24, r * 0.24, seed + 50, 0.04, 14), ("#7AE0D8", "#12808A", "#084650"), seed + 50, sk=0.2, n=3, inkw=1.2, hi=0.5))
    out.append(f'<path d="{blob(cx - r * 0.08, cy - r * 0.08, r * 0.08, r * 0.05, seed, 0.2, 8)}" fill="#FFFFFF"/>')
    for k in range(10):
        t = rnd.uniform(0, 6.28)
        out.append(sparkle(cx + math.cos(t) * r * rnd.uniform(0.9, 1.3), cy + math.sin(t) * r * rnd.uniform(0.9, 1.3), r * 0.07, "#FFF6C8", 0.9))
    return "".join(out)


def kaju_katli(D, cx, cy, s, seed, ang=0):
    pts = rot([(cx, cy - s * 0.6), (cx + s, cy), (cx, cy + s * 0.6), (cx - s, cy)], cx, cy, ang)
    out = [f'<path d="{pd(shift(pts, 0, s * 0.18))}" fill="#C8B488"/>']
    out.append(painted(D, pts, ("#FFF8EA", "#F2E6CC", "#B8A47A"), seed, sk=0.12, n=3, inkw=1, hi=0.4))
    out.append(f'<path d="{blob(cx - s * 0.1, cy - s * 0.05, s * 0.45, s * 0.22, seed, 0.3, 10, ang)}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(specks(seed, (cx - s * 0.5, cy - s * 0.3, cx + s * 0.5, cy + s * 0.3), ["#E8ECF0", "#FFFFFF", "#B8C0C8"], 10, (0.6, 1.4), (0.6, 1)))
    return "".join(out)


@design("rakhi")
def rakhi():
    D = Doc2("in-rk")
    # a deep marigold silk ground with a woven gold border
    # a bandhani silk dupatta spread under the plate: tie-dye dots in rings on deep red, soft folds
    out = [sky(D, [(0, "#C8202A"), (1, "#8A0E1A")], 2701, 600, ["#E8404A", "#6A0612", "#D82A3A"], 160, angle=-30, sop=(0.08, 0.2))]
    rr = random.Random(2711)
    dots = []
    for j in range(-1, 14):
        for i in range(-1, 14):
            x, y = i * 48 + (24 if j % 2 else 0), j * 46
            for k in range(8):
                a_ = math.radians(k * 45)
                dots.append(f'<circle cx="{x + math.cos(a_) * 9:.1f}" cy="{y + math.sin(a_) * 9:.1f}" r="2" fill="#FFE8A0" opacity="0.75"/>')
            dots.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#FFFFFF" opacity="0.8"/>')
            dots.append(f'<circle cx="{x + 24}" cy="{y + 23}" r="1.6" fill="#2A8A3A" opacity="0.7"/>')
    out.append("".join(dots))
    for k, (x0_, x1_) in enumerate(((-40, 160), (260, 470), (520, 680))):
        out.append(f'<path d="M {x0_} -20 Q {(x0_ + x1_) / 2 + 40} 300 {x0_ + 30} 640 L {x1_} 640 Q {(x0_ + x1_) / 2 + 80} 300 {x1_ - 20} -20 Z" fill="{D.lin([(0, "#3A0408", 0.0), (0.5, "#3A0408", 0.28), (1, "#3A0408", 0.0)], 0, 0, 1, 0)}"/>')
    out.append(soft_glow(D, 300, 400, 320, "#FFD890", 0.4))
    # the brass plate with roli, rice, a diya, kaju katli and the rakhi
    cx, cy = 300, 424
    out.append(f'<path d="{ellipse_d(cx + 10, cy + 16, 228, 104)}" fill="#5A2A06" opacity="0.35"/>')
    pl = ellipse_d(cx, cy, 226, 100)
    out.append(f'<path d="{pl}" fill="{BRASS[1]}"/>' + metal(D, pl, cx - 226, cx + 226, BRASS, 0.8, 0.7))
    out.append(f'<path d="{ellipse_d(cx, cy + 4, 196, 82)}" fill="#C8963A"/>')
    out.append(f'<path d="{ellipse_d(cx, cy + 4, 196, 82)}" fill="{D.lin([(0, "#8A5A14", 0.5), (1, "#FFE6A0", 0.4)])}"/>')
    for i in range(32):
        a = 2 * math.pi * i / 32
        out.append(f'<circle cx="{cx + math.cos(a) * 212:.1f}" cy="{cy + math.sin(a) * 92:.1f}" r="2.6" fill="#FFF0C0" opacity="0.8"/>')
    out.append(ink(pl, INK, 1.8, 2702, 1, 0.55))
    # roli (vermilion) and rice in two little katoris
    out.append(steel_bowl(D, 150, 396, 36, 22, 2703, fill=f'<path d="{ellipse_d(150, 398, 31, 9)}" fill="#D6201E"/>', pal=BRASS))
    rice = f'<path d="{ellipse_d(232, 372, 31, 9)}" fill="#FFFDF0"/>' + "".join(f'<path d="{blob(232 + random.Random(k).uniform(-24, 24), 372 + random.Random(k + 99).uniform(-6, 6), 3, 1.2, k, 0.1, 6, k * 23)}" fill="#E8E0C8"/>' for k in range(20))
    out.append(steel_bowl(D, 232, 370, 36, 22, 2704, fill=rice, pal=BRASS))
    out.append(diya(D, 430, 392, 30, 2705))
    for k, (x, y, a) in enumerate(((410, 474, 10), (450, 490, -12), (482, 462, 20))):
        out.append(kaju_katli(D, x, y, 22, 2706 + k, a))
    rnd = random.Random(2709)
    for _ in range(14):
        x, y = cx + rnd.uniform(-170, 170), cy + rnd.uniform(-50, 70)
        out.append(f'<path d="{blob(x, y, 3, 1.2, rnd.randint(0, 999), 0.1, 6, rnd.uniform(0, 180))}" fill="#FFFDF0"/>')
    out.append(rakhi_charm(D, 286, 444, 62, 2710, ang=-6))
    for k in range(18):
        x, y = rnd.uniform(40, 560), rnd.uniform(520, 590)
        out.append(f'<path d="{blob(x, y, 5, 3, k + 2730, 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2901E", "#F6C21C", "#FFB040"])}" opacity="0.9"/>')
    out.append(vignette(D, "#2A0206", 0.45, 0.8))
    # lettering
    txt = [letters(D, 300, 150, "Rakhi", SERIF_IT, 156, "#FFD86A", ["#FFE8A0", "#F2A83A", "#FFF2C8"], 2720, max_w=360,
                   shadow="#3A0408", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 198, "A THREAD AND A PROMISE", "#FFE6C0", font=JOS, size=20, ls=5, line_w=24, gap=12)]
    return finish_art(D, out, txt, 2721, under="#A8142A", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 28. namaste — shoes off at the door, the whole family's pile
def _shoe_pts(cx, cy, L, ang, sq, toe=0.5, heel=0.36, w=0.2, curl=0.0):
    """Footprint outline of a shoe/sandal seen from above at a slant (sq squashes y)."""
    pts = [(-0.5, 0.0), (-0.46, -heel * w * 2.2), (-0.2, -w * 0.95), (0.18, -w * 1.1), (0.42, -w * 0.75), (0.5 + curl, -w * 0.15), (0.48, w * 0.45),
           (0.22, w * 0.95), (-0.12, w * 0.8), (-0.42, w * 0.7)]
    pts = [(x * L, y * L) for x, y in pts]
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + x * c - y * s_, cy + (x * s_ + y * c) * sq) for x, y in pts]


def shoe(D, kind, cx, cy, L, ang, seed, sq=0.62, col=None):
    """Painted footwear seen from above at a slant: 'kolhapuri', 'chappal', 'jutti', 'sneaker', 'sandal'."""
    out = []
    P = _shoe_pts(cx, cy, L, ang, sq, curl=0.08 if kind == "jutti" else 0.0)
    out.append(f'<path d="{smooth_closed(shift(P, L * 0.04, L * 0.07))}" fill="#1A0E08" opacity="0.35"/>')
    c_, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def R(x, y):
        return (cx + (x * c_ - y * s_) * L, cy + (x * s_ + y * c_) * L * sq)
    if kind in ("kolhapuri", "chappal", "sandal"):
        sole = {"kolhapuri": ("#E8B070", "#B87A3A", "#5A3414"), "chappal": col or ("#8AB8E8", "#2E6AB0", "#0E2A5A"), "sandal": ("#F2D0A0", "#C89A5A", "#6A4A20")}[kind]
        side = [(x, y + L * 0.035) for x, y in P]
        out.append(f'<path d="{smooth_closed(side)}" fill="{sole[2]}"/>')
        out.append(modelled(D, P, sole, seed, light=(-0.6, -0.7), angle=ang, n=12, inkw=1.0, hi=0.4, core=0.2))
        if kind == "kolhapuri":
            st = [R(-0.02, -0.24), R(0.08, -0.26), R(0.12, 0.26), R(0.0, 0.26)]
            out.append(modelled(D, st, ("#D89A5A", "#9A5A24", "#4A2408"), seed + 1, light=(-0.6, -0.7), angle=ang + 90, n=8, inkw=1.0, hi=0.3))
            for k in range(5):
                a_, b_ = R(0.0 + k * 0.025, -0.22), R(0.0 + k * 0.025, 0.22)
                out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#F2C890" stroke-width="0.9" opacity="0.7" stroke-dasharray="2 1.5"/>')
            t0, t1 = R(0.3, 0.0), R(0.08, 0.0)
            out.append(taper([t0, t1], L * 0.05, L * 0.04, "#7A3A14"))
            out.append(f'<circle cx="{t0[0]:.1f}" cy="{t0[1]:.1f}" r="{L * 0.04:.1f}" fill="#D6342A"/>')
            edge = [(x + (cx - x) * 0.1, y + (cy - y) * 0.1) for x, y in P]
            out.append(f'<path d="{smooth_closed(edge)}" fill="none" stroke="#F2D0A0" stroke-width="0.9" stroke-dasharray="2.4 2" opacity="0.8"/>')
        elif kind == "chappal":
            for a_, b_ in ((R(0.18, -0.2), R(0.3, 0.0)), (R(0.18, 0.2), R(0.3, 0.0))):
                out.append(taper([a_, b_], L * 0.06, L * 0.05, "#FFFFFF"))
                out.append(taper([a_, b_], L * 0.025, L * 0.02, "#C8D8E8", 0.8))
        else:
            for yy in (-0.22, 0.22):
                out.append(taper([R(0.05, yy), R(0.22, 0.0)], L * 0.05, L * 0.04, "#C89A3A"))
            out.append(f'<path d="{blob(*R(0.22, 0.0), L * 0.05, L * 0.04, seed, 0.1, 8)}" fill="#F6C21C"/>')
    elif kind == "jutti":
        sole = ("#3A2010", "#2A1408", "#100604")
        out.append(f'<path d="{smooth_closed([(x, y + L * 0.03) for x, y in P])}" fill="{sole[1]}"/>')
        vel = col or ("#E86A7A", "#B8183A", "#5A0418")
        out.append(modelled(D, P, vel, seed, light=(-0.6, -0.7), angle=ang, n=14, inkw=1.0, hi=0.4))
        op_ = [R(-0.45, 0.0), R(-0.38, -0.15), R(-0.1, -0.16), R(0.0, 0.0), R(-0.1, 0.15), R(-0.38, 0.14)]
        out.append(f'<path d="{smooth_closed(op_)}" fill="#3A1008"/>')
        out.append(pk.dabs(seed + 2, bbox([R(0.0, -0.18), R(0.45, 0.18)]), ["#F6D060", "#FFF0B0", "#E8B030"], int(L * 0.6), (0.6, 1.4), (0.7, 1.0),
                           clip=D.clip(f'<path d="{smooth_closed(P)}"/>')))
    elif kind == "sneaker":
        up = col or ("#F2F2F0", "#C8CCD0", "#6A707A")
        out.append(f'<path d="{smooth_closed([(x, y + L * 0.06) for x, y in P])}" fill="#E8E4DC"/>')
        out.append(modelled(D, P, up, seed, light=(-0.6, -0.7), angle=ang, n=12, inkw=1.0, hi=0.4))
        op_ = [R(-0.42, 0.0), R(-0.34, -0.13), R(-0.12, -0.13), R(-0.05, 0.0), R(-0.12, 0.12), R(-0.34, 0.12)]
        out.append(f'<path d="{smooth_closed(op_)}" fill="#2A2A30"/>')
        for k in range(4):
            a_, b_ = R(-0.0 + k * 0.08, -0.1), R(-0.0 + k * 0.08, 0.1)
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#FFFFFF" stroke-width="{max(1.2, L * 0.025):.1f}"/>')
        sw_ = [R(-0.2, 0.17), R(0.1, 0.12), R(0.3, 0.16)]
        out.append(taper(sw_, L * 0.04, L * 0.02, "#D6342A"))
    return "".join(out)


def kolam(D, cx, cy, R, seed, sq=0.5, col="#FFFFFF"):
    """A rice-flour kolam drawn on the threshold: a dot grid with a continuous looping line around the dots,
    petals at the cardinal points, seen at a slant."""
    rnd = random.Random(seed)
    out = []
    n = 5
    step = R * 2 / (n + 1)
    dots = []
    for i in range(n):
        for j in range(n):
            if abs(i - n // 2) + abs(j - n // 2) <= n // 2 + 0:
                x, y = cx + (i - n // 2) * step, cy + (j - n // 2) * step * sq
                dots.append((x, y))
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.4, R * 0.025):.1f}" fill="{col}"/>')
    # loops around each dot (sikku style approximation)
    for x, y in dots:
        rr = step * 0.42
        lp = [(x + math.cos(t) * rr, y + math.sin(t) * rr * sq) for t in [k * math.pi / 6 for k in range(12)]]
        out.append(f'<path d="{smooth_closed(jitter(lp, rnd.randint(0, 999), 0.4))}" fill="none" stroke="{col}" stroke-width="{max(1.2, R * 0.022):.1f}" opacity="0.92"/>')
    for a in range(0, 360, 45):
        r_ = math.radians(a)
        px, py = cx + math.cos(r_) * R * 1.02, cy + math.sin(r_) * R * 1.02 * sq
        pet = [(cx + math.cos(r_) * R * 0.86, cy + math.sin(r_) * R * 0.86 * sq), (px + math.cos(r_ + 1.6) * R * 0.08, py + math.sin(r_ + 1.6) * R * 0.08 * sq),
               (cx + math.cos(r_) * R * 1.2, cy + math.sin(r_) * R * 1.2 * sq), (px + math.cos(r_ - 1.6) * R * 0.08, py + math.sin(r_ - 1.6) * R * 0.08 * sq)]
        out.append(f'<path d="{smooth_closed(pet)}" fill="none" stroke="{col}" stroke-width="{max(1.2, R * 0.022):.1f}"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(1.6, R * 0.03):.1f}" fill="#E8346A"/>')
    out.append(f'<path d="{blob(cx, cy, R * 1.25, R * 1.25 * sq, seed, 0.02, 24)}" fill="none" stroke="{col}" stroke-width="{max(1.2, R * 0.02):.1f}" stroke-dasharray="3 3" opacity="0.8"/>')
    return "".join(out)


@design("namaste")
def namaste():
    D = Doc2("in-nm")
    art = []
    # dusk outside: a cool lime-washed wall, an ochre dado, the teak door frame
    art.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#4E6EA8"/>')
    art.append(sky(D, [(0, "#3E5A94"), (0.6, "#5A7AB4"), (1, "#6A88B8")], 2801, 480, ["#7A98C8", "#2E4A80", "#8AA8D8"], 140, angle=-84, sop=(0.08, 0.2)))
    art.append(blooms(2809, ["#2A4078", "#8AA8D8"], 8, (0, 0, 600, 420), (50, 120), (0.08, 0.16)))
    art.append(f'<path d="{pdl([(-10, 380), (610, 380), (610, 472), (-10, 472)])}" fill="#C88A40"/>')
    art.append(strokes(D.nid(), pdl([(-10, 380), (610, 380), (610, 472), (-10, 472)]), (-40, 380, 620, 472), ["#E0A858", "#A86A2A"], 2802, n=60, angle=-4, length=(30, 90), width=(3, 7), opacity=(0.12, 0.3)))
    art.append(f'<path d="M -10 380 L 610 380" stroke="#F2E6D0" stroke-width="3"/>')
    # the open doorway with warm lamplight within
    X0, X1, Y0, Y1 = 204, 396, 238, 452
    frame = pk.dens2([(X0 - 30, Y0 - 34), (X1 + 30, Y0 - 34), (X1 + 30, Y1 + 4), (X0 - 30, Y1 + 4)], 10)
    art.append(modelled(D, frame, ("#B87A4A", "#7A4420", "#3A1C08"), 2803, light=(-0.6, -0.6), angle=-90, n=60, inkw=1.6, hi=0.35))
    for k in range(9):
        y = Y0 - 20 + k * 34
        for x in (X0 - 16, X1 + 16):
            art.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#E8C060"/><circle cx="{x - 1}" cy="{y - 1}" r="1.4" fill="#FFF6D0"/>')
    for k in range(7):
        x = X0 - 10 + k * (X1 - X0 + 20) / 6
        art.append(f'<path d="{blob(x, Y0 - 22, 9, 6, 2804 + k, 0.2, 10)}" fill="#5A2A0E" opacity="0.6"/>')
    inside = pk.dens2([(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)], 10)
    idp = smooth_closed(inside)
    art.append(f'<path d="{idp}" fill="{D.lin([(0, "#F8C870"), (0.6, "#E8984A"), (1, "#B8642A")])}"/>')
    inn = [soft_glow(D, 300, 320, 150, "#FFF0B0", 0.8),
           f'<path d="{pdl([(X0, 404), (X1, 404), (X1, Y1), (X0, Y1)])}" fill="#A8582A" opacity="0.6"/>']
    for k in range(5):
        y = 404 + k * 11
        inn.append(f'<path d="M {X0} {y} L {X1} {y}" stroke="#7A3A18" stroke-width="1" opacity="0.5"/>')
    inn.append(f'<path d="{pdl([(256, 334), (344, 334), (344, 344), (256, 344)])}" fill="#6A3414"/>')
    inn.append(diya(D, 300, 330, 12, 2805, glow=True))
    inn.append(f'<path d="{pdl([(266, 264), (334, 264), (334, 316), (266, 316)])}" fill="#5A3414"/>')
    inn.append(f'<path d="{pdl([(272, 270), (328, 270), (328, 310), (272, 310)])}" fill="{D.lin([(0, "#F2D8A8"), (1, "#C8946A")])}"/>')
    inn.append(f'<circle cx="300" cy="286" r="9" fill="#B8784A" opacity="0.6"/>')
    inn.append(garland(D, [(266, 268), (300, 284), (334, 268)], 3.4, 2806, leaves=False))
    # the door leaf swung inward at the right, catching the lamplight
    leaf_ = [(X1 - 4, Y0 + 2), (X1 - 54, Y0 + 18), (X1 - 54, Y1 - 10), (X1 - 4, Y1)]
    inn.append(modelled(D, leaf_, ("#C88A4A", "#8A4E22", "#3A1C08"), 2807, light=(-1, -0.2), angle=-90, n=24, inkw=1.2, hi=0.3))
    for y in (Y0 + 60, Y0 + 160, Y0 + 250):
        inn.append(f'<circle cx="{X1 - 30}" cy="{y}" r="3" fill="#E8C060"/>')
    art.append(clipped(D, idp, inn))
    # mandana: white lime-paint borders and dots framing the door, a lamp niche on the right, tulsi on the left
    for off, w_ in ((54, 2.6), (66, 1.6)):
        fr_ = [(X0 - off, Y1 + 4), (X0 - off, Y0 - off), (X1 + off, Y0 - off), (X1 + off, Y1 + 4)]
        art.append(f'<path d="{smooth_open(jitter(pk.dens2(fr_, 14)[:-1], 2870 + off, 0.8))}" fill="none" stroke="#F4F0E6" stroke-width="{w_}" opacity="0.85"/>')
    rnd2 = random.Random(2871)
    for k in range(26):
        t = k / 25
        for xx in (X0 - 60, X1 + 60):
            y_ = Y0 - 58 + (Y1 - Y0 + 60) * t
            art.append(f'<circle cx="{xx + rnd2.uniform(-1, 1):.1f}" cy="{y_:.1f}" r="2.2" fill="#F4F0E6" opacity="0.85"/>')
    for k in range(5):
        y_ = Y0 - 64 - 4
        art.append(f'<path d="{blob(X0 - 60 + k * (X1 - X0 + 120) / 4, y_, 7, 4, 2872 + k, 0.2, 8)}" fill="#F4F0E6" opacity="0.85"/>')
    nx_, ny_ = 516, 300
    niche = [(nx_ - 26, ny_ + 30), (nx_ - 26, ny_ - 10), (nx_ - 14, ny_ - 30), (nx_, ny_ - 38), (nx_ + 14, ny_ - 30), (nx_ + 26, ny_ - 10), (nx_ + 26, ny_ + 30)]
    art.append(f'<path d="{smooth_closed(niche)}" fill="#1E2A4A"/>')
    art.append(soft_glow(D, nx_, ny_ + 8, 60, "#FFC860", 0.5))
    art.append(diya(D, nx_ - 4, ny_ + 26, 13, 2873, glow=False))
    art.append(f'<path d="{smooth_open(niche)}" fill="none" stroke="#F4F0E6" stroke-width="2"/>')
    pot = [(70, 380), (130, 380), (122, 340), (78, 340)]
    art.append(modelled(D, pk.dens2(pot, 6), ("#E8A070", "#B8603A", "#5A2410"), 2874, light=(-0.6, -0.6), angle=-90, n=14, inkw=1.2, hi=0.35))
    for k in range(5):
        art.append(f'<path d="M {82 + k * 9} 344 L {80 + k * 9} 348" stroke="#F4F0E6" stroke-width="2"/>')
    art.append(dab_crown(D, 100, 310, 34, 34, [("#8AC060", "#3E8A3A", "#1A4A1E")], 2875, n=50, size=(3, 6), inkw=0))
    # the toran: mango leaves and marigolds strung across the top of the frame
    pts = [(X0 - 34, Y0 - 30), (300, Y0 - 12), (X1 + 34, Y0 - 30)]
    rnd = random.Random(2808)
    for k in range(13):
        t = k / 12
        x = X0 - 30 + (X1 - X0 + 60) * t
        y = Y0 - 30 + 18 * math.sin(math.pi * t)
        art.append(leaf_simple(D, x + rnd.uniform(-3, 3), y + 20, rnd.uniform(32, 40), rnd.uniform(9, 12), 90 + rnd.uniform(-12, 12), rnd.choice([("#8AC060", "#3A8A2A", "#1A4A14"), ("#A8C870", "#5A9A3A", "#2A5A1A"), ("#7AA850", "#2E7024", "#123A10")]), 2809 + k, inkw=0.9))
    art.append(garland(D, pts, 7, 2830, leaves=False))
    # the threshold step, the stone floor outside in the door's spill of light
    stp = pk.dens2([(X0 - 40, Y1), (X1 + 40, Y1), (X1 + 54, Y1 + 22), (X0 - 54, Y1 + 22)], 10)
    art.append(modelled(D, stp, ("#E8D8C0", "#B8A890", "#6A5A48"), 2840, light=(0, -1), angle=0, n=20, inkw=1.2, hi=0.35))
    art.append(f'<path d="M {X0 - 40} {Y1 + 2} L {X1 + 40} {Y1 + 2}" stroke="#D6342A" stroke-width="3" opacity="0.8"/>')
    fl = [(-10, Y1 + 22), (610, Y1 + 22), (610, 620), (-10, 620)]
    art.append(f'<path d="{pdl(fl)}" fill="#8A8278"/>')
    art.append(f'<path d="{pdl(fl)}" fill="{D.rad([(0, "#F8C878", 0.75), (0.6, "#E8A860", 0.25), (1, "#3A3440", 0.2)], 0.5, 0.0, 0.75)}"/>')
    art.append(strokes(D.nid(), pdl(fl), (-40, Y1 + 22, 620, 620), ["#A89A88", "#6A6268", "#D8C8B0"], 2841, n=90, angle=-4, length=(20, 80), width=(2, 6), opacity=(0.12, 0.3)))
    art.append(kolam(D, 300, 538, 72, 2842, sq=0.42))
    # the family's footwear, kicked off in two drifts either side of the kolam
    left = [("kolhapuri", 104, 504, 78, -22, None), ("kolhapuri", 140, 528, 78, -6, None), ("jutti", 84, 560, 64, 26, None), ("jutti", 172, 574, 64, -40, None),
            ("chappal", 202, 500, 56, 64, (("#F2A0C0", "#D6246E", "#7A0E3A"))), ("chappal", 216, 528, 54, 96, (("#F2A0C0", "#D6246E", "#7A0E3A")))]
    right = [("sneaker", 412, 512, 70, 200, None), ("sneaker", 448, 536, 70, 174, None), ("chappal", 500, 500, 74, 158, None), ("chappal", 526, 532, 74, 194, None),
             ("sandal", 404, 574, 46, 212, None), ("sandal", 436, 582, 44, 168, None)]
    for kind, x, y, L_, a_, c_ in sorted(left + right, key=lambda q: q[2]):
        art.append(shoe(D, kind, x, y, L_, a_, 2850 + int(x), col=c_))
    art.append(glaze(D, [(0, "#3A4A6A", 0.25), (0.5, "#3A4A6A", 0), (1, "#3A4A6A", 0.25)], 0, 0, 1, 0))
    art.append(vignette(D, "#1A1A2A", 0.35, 0.8))
    txt = [letters(D, 300, 116, "Namaste", SERIF_IT, 128, "#FFF2DC", ["#FFFFFF", "#F8E2C0", "#FFE8C8"], 2860, max_w=400,
                   shadow="#1A2448", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 160, "SHOES OFF, COME ON IN", "#FFD890", font=JOS, size=20, ls=6, line_w=24, gap=12)]
    return finish_art(D, art, txt, 2861, under="#C8C8C0", edge=2.4, bristle=0.4, grain=0.16)


# ================================================================ 29. baarish — monsoon on the balcony, chai and pakore
def railing(D, y0, y1, seed, col="#1E2A3A"):
    out = [taper([(-10, y0), (610, y0)], 8, 8, col), taper([(-10, y1), (610, y1)], 6, 6, col)]
    for x in range(0, 620, 44):
        out.append(taper([(x, y0), (x, y1)], 4, 4, col))
        cx, cy = x + 22, (y0 + y1) / 2
        out.append(f'<path d="M {cx - 14} {cy} C {cx - 14} {cy - 18}, {cx + 4} {cy - 18}, {cx + 2} {cy - 6} C {cx} {cy + 2}, {cx - 8} {cy}, {cx - 6} {cy - 6}" stroke="{col}" stroke-width="3" fill="none"/>')
        out.append(f'<path d="M {cx + 14} {cy} C {cx + 14} {cy + 18}, {cx - 4} {cy + 18}, {cx - 2} {cy + 6} C {cx} {cy - 2}, {cx + 8} {cy}, {cx + 6} {cy + 6}" stroke="{col}" stroke-width="3" fill="none"/>')
    out.append(taper([(-10, y0 - 3), (610, y0 - 3)], 2, 2, "#8AA8C8", 0.6))
    return "".join(out)


def pakora(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.72, seed, 0.25, 18)
    out = [painted(D, pts, ("#F2C060", "#C8822A", "#7A4410"), seed, sk=0.25, angle=-40, n=8, cols=["#FFE08A", "#8A4A10", "#E8A040"], inkw=1.3, hi=0.45)]
    for _ in range(int(r * 0.6)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.2, 0.9) * r
        out.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.7, rnd.uniform(1.5, 3.5), rnd.uniform(1, 2.5), rnd.randint(0, 999), 0.3, 6)}" fill="{rnd.choice(["#8A4A10", "#FFE8A0", "#3E7A2A"])}" opacity="0.75"/>')
    return "".join(out)


@design("baarish")
def baarish():
    D = Doc2("in-bs")
    # the rain beyond the balcony: grey-blue, a blur of wet trees and buildings
    out = [sky(D, [(0, "#5A6E86"), (0.7, "#8AA0B4"), (1, "#A8BCC8")], 2901, 600, ["#9AB0C4", "#3E5268", "#B8C8D4"], 110, angle=-84, sop=(0.06, 0.16))]
    out.append(pk.sky_brush(D, 2902, [(-40, 300, ["#4A5E76", "#6A8098", "#3A4C62"], 90, (6, 16), (60, 180), (0.2, 0.45)),
                                      (200, 420, ["#9AAEC0", "#7A8EA4", "#B8C8D4"], 60, (4, 10), (50, 140), (0.15, 0.35))], angle=-80))
    rb = random.Random(2903)
    for k, (x, w, h) in enumerate(((10, 130, 210), (150, 90, 160), (380, 150, 240), (530, 100, 180))):
        bp_ = jitter(pk.dens2([(x, 420 - h), (x + w, 420 - h + rb.uniform(-8, 8)), (x + w, 460), (x, 460)], 14), k, 1.6)
        out.append(f'<path d="{smooth_closed(bp_)}" fill="#6E8298" opacity="0.6"/>')
        for j in range(int(h / 40)):
            for i in range(int(w / 40)):
                if rb.random() < 0.35:
                    wx_, wy_ = x + 14 + i * 40, 420 - h + 18 + j * 40
                    c_ = "#FFE6A0" if rb.random() < 0.4 else "#4E6278"
                    out.append(f'<path d="{blob(wx_, wy_, 6, 8, rb.randint(0, 999), 0.2, 8)}" fill="{c_}" opacity="0.55"/>')
                    if c_ == "#FFE6A0":
                        out.append(soft_glow(D, wx_, wy_, 16, "#FFE6A0", 0.35))
    for k, (x, h, ln) in enumerate(((150, 260, 0.35), (236, 210, 0.42), (470, 240, 0.3))):
        out.append(f'<g opacity="0.7">{coco_palm(D, x, 430, h, ln, 2906 + k, col="#3E5262", lit="#8AA0B0", trunk_c="#3E4E5C", scale=0.9, rim=0.2)}</g>')
    out.append(mist(D, 330, 70, 2907, "#C8D8E4", 0.55))
    # rain: long slanted streaks and splashes on the rail
    rnd = random.Random(2908)
    rn = []
    for _ in range(220):
        x, y = rnd.uniform(-40, 640), rnd.uniform(-20, 470)
        L = rnd.uniform(18, 40)
        rn.append(f'<path d="M {x:.1f} {y:.1f} l {-L * 0.22:.1f} {L:.1f}" stroke="#E8F2FA" stroke-width="{rnd.uniform(1, 1.8):.1f}" opacity="{rnd.uniform(0.25, 0.65):.2f}"/>')
    out.append("".join(rn))
    # the wrought-iron railing, a potted hibiscus-free tulsi-free money plant in a clay pot, drops hanging off the rail
    out.append(railing(D, 380, 452, 2909))
    for x in range(20, 600, 34):
        out.append(f'<path d="{blob(x, 390, 2.4, 3.6, x, 0.1, 6)}" fill="#E8F4FC" opacity="0.85"/>')
    # a little table in front with a steel plate of pakore, two glasses of chai, a bowl of green chutney
    out.append(f'<path d="M -10 450 L 610 450 L 610 610 L -10 610 Z" fill="#6A4A3A"/>')
    out.append(f'<path d="M -10 450 L 610 450 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#2A1A12", 0.5), (1, "#8A6A50", 0.2)])}"/>')
    out.append(strokes(D.nid(), pd([(-10, 450), (610, 450), (610, 610), (-10, 610)]), (-40, 450, 610, 600), ["#8A6A50", "#3A2418"], 2910, n=60, angle=0, length=(40, 140), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(soft_glow(D, 300, 500, 260, "#FFC880", 0.35))
    px, py = 250, 510
    pl = ellipse_d(px, py, 150, 44)
    out.append(f'<path d="{ellipse_d(px + 8, py + 10, 150, 44)}" fill="#1A0E08" opacity="0.4"/>')
    out.append(f'<path d="{pl}" fill="#C8CED6"/>' + metal(D, pl, px - 150, px + 150) + f'<path d="{ellipse_d(px, py + 3, 128, 34)}" fill="#DDE2E8"/>' + ink(pl, INK, 1.6, 2911, 1, 0.6))
    for k, (x, y, r) in enumerate(((190, 500, 30), (240, 512, 32), (296, 502, 30), (214, 482, 28), (270, 480, 28), (330, 516, 26), (160, 520, 24))):
        out.append(pakora(D, x, y, r, 2912 + k))
    out.append(steel_bowl(D, 104, 480, 34, 22, 2920, fill=f'<path d="{ellipse_d(104, 482, 29, 8)}" fill="#3E8A2A"/>'))
    out.append(cutting_glass(D, 444, 540, 64, 84, 2921, fill=0.8))
    out.append(cutting_glass(D, 516, 530, 60, 80, 2922, fill=0.7))
    out.append(pk.steam_plume(D, [(444, 452), (436, 420), (452, 390)], 10, 20, 2923, "#FFFFFF", 0.55, puffs=False))
    out.append(pk.steam_plume(D, [(516, 448), (524, 416), (508, 388)], 10, 18, 2924, "#FFFFFF", 0.5, puffs=False))
    out.append(pk.steam_plume(D, [(250, 476), (236, 440), (256, 406)], 14, 26, 2925, "#FFFFFF", 0.45, puffs=False))
    # lettering
    out.append(glaze(D, [(0, "#2A3A50", 0.18), (0.6, "#2A3A50", 0), (1, "#FFB060", 0.1)]))
    out.append(vignette(D, "#0E1620", 0.4, 0.8))
    txt = [letters(D, 300, 140, "Baarish", SERIF_IT, 150, "#FFF6E8", ["#FFFFFF", "#D8E4EE", "#F0F6FA"], 2930, max_w=420,
                   shadow="#2A3A4E", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"),
           sub(300, 186, "CHAI, PAKORE & THE FIRST RAIN", "#FFE08A", font=JOS, size=19, ls=4, line_w=20, gap=12)]
    return finish_art(D, out, txt, 2931, under="#5A6E86", edge=2.4, bristle=0.45, grain=0.18)


# ================================================================ 30. dadi ke laddoo — the steel dabba, the glasses, the shawl
def laddoo(D, cx, cy, r, seed, kind="motichoor", light=(-0.6, -0.8)):
    rnd = random.Random(seed)
    if kind == "motichoor":
        pal = ("#FFC060", "#F28A1E", "#A8500A")
    else:
        pal = ("#F8D88A", "#E0A848", "#8A5A18")
    pts = blob_pts(cx, cy, r, r * 0.96, seed, 0.04, 18)
    out = [painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-40, n=int(r * 0.6) + 4, inkw=max(1, r * 0.04), hi=0.45, hik=0.1)]
    d = smooth_closed(pts)
    inner = []
    if kind == "motichoor":
        for _ in range(int(r * r * 0.22)):
            a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            lit = -(math.cos(a) * light[0] + math.sin(a) * light[1]) * rr / r
            c = pal[0] if lit > 0.3 else (pal[2] if lit < -0.35 else rnd.choice(pal))
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.6, 2.6):.1f}" fill="{c}" opacity="0.85"/>')
    else:
        for _ in range(int(r * 0.8)):
            a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
            inner.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#8A5A18" opacity="0.4"/>')
    inner.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.38, r * 0.3, r * 0.2, seed + 2, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.45"/>')
    out.append(clipped(D, d, inner))
    if kind != "motichoor":
        out.append(painted(D, blob_pts(cx + r * 0.1, cy - r * 0.55, r * 0.32, r * 0.16, seed + 3, 0.1, 10, rot=-20), ("#FFF6E0", "#F0DCB0", "#A88A5A"), seed + 3, sk=0.2, n=2, inkw=0.8, hi=0.5))
    else:
        for k in range(3):
            out.append(f'<path d="{blob(cx + rnd.uniform(-r, r) * 0.4, cy - r * 0.6 + rnd.uniform(-3, 3), r * 0.12, r * 0.05, seed + k, 0.2, 6, rnd.uniform(-40, 40))}" fill="#7AB04A"/>')
    return "".join(out)


@design("dadi-ke-laddoo")
def dadi_ke_laddoo():
    D = Doc2("in-dl")
    # a cotton saree-blue table cover with a woven border, soft window light
    out = [sky(D, [(0, "#F4E6D0"), (1, "#E8D2B4")], 3001, 600, ["#FFFFFF", "#C8A880"], 90, angle=-6, sop=(0.05, 0.12))]
    out.append(blooms(3002, ["#FFF6E8", "#C8A07A"], 7, (0, 0, 600, 600), (90, 180), (0.06, 0.12)))
    out.append(f'<path d="M -10 268 L 610 268 L 610 610 L -10 610 Z" fill="#2E5A8A"/>')
    out.append(strokes(D.nid(), pd([(-10, 300), (610, 300), (610, 610), (-10, 610)]), (-40, 268, 610, 600), ["#4A7AAA", "#1A3A5E"], 3003, n=100, angle=-2, length=(40, 140), width=(2, 6), opacity=(0.15, 0.35)))
    for y, c, w in ((280, "#F6C21C", 6), (292, "#D6342A", 10), (304, "#F6C21C", 6)):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="{c}" stroke-width="{w}"/>')
    for x in range(0, 620, 22):
        out.append(f'<path d="{blob(x, 292, 4, 3, x, 0.2, 6)}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(f'<rect x="-10" y="268" width="620" height="342" fill="{D.rad([(0, "#FFF0D0", 0.3), (0.6, "#FFF0D0", 0), (1, "#0A1A30", 0.45)], 0.45, 0.4, 0.75)}"/>')
    out.append(leaf_shadows(D, 3040, (-20, 0, 260, 260), "#6A4A2A", 20, (0.05, 0.1), (16, 30)))
    # Dadi's paisley shawl folded at the back right, her prayer beads on it
    sh_ = [(420, 300), (620, 290), (620, 380), (560, 372), (470, 360), (410, 340)]
    out.append(f'<path d="{smooth_closed(shift(sh_, 6, 10))}" fill="#0A1A30" opacity="0.4"/>')
    out.append(modelled(D, sh_, ("#C86A5A", "#8A2A2A", "#3A0A0E"), 3041, light=(-0.6, -0.7), angle=-10, n=30, inkw=1.2, hi=0.3))
    shd = smooth_closed(sh_)
    pz = []
    rp = random.Random(3042)
    for k in range(9):
        x, y = 430 + k * 22 + rp.uniform(-4, 4), 318 + (k % 2) * 22
        pz.append(f'<path d="{smooth_closed(paisley_pts(x, y, 14, 20 + k * 30))}" fill="#E8B84A" opacity="0.75"/>')
        pz.append(f'<circle cx="{x - 2:.1f}" cy="{y + 2:.1f}" r="2" fill="#2A6A5A"/>')
    pz.append(f'<path d="M 410 342 Q 500 368 620 382" stroke="#E8B84A" stroke-width="3" fill="none" opacity="0.8"/>')
    out.append(clipped(D, shd, pz))
    for k in range(22):
        a_ = 2 * math.pi * k / 22
        out.append(f'<circle cx="{520 + math.cos(a_) * 28:.1f}" cy="{330 + math.sin(a_) * 10:.1f}" r="3" fill="#8A4A1E"/><circle cx="{519 + math.cos(a_) * 28:.1f}" cy="{329 + math.sin(a_) * 10:.1f}" r="1" fill="#F2C890"/>')
    # the round steel dabba, lid leaning behind, heaped with laddoos
    cx, rim = 262, 404
    out.append(cast(D, cx + 16, 512, 170, 18, strength=0.5, seed=3004))
    lid = ellipse_d(cx + 150, 352, 104, 112)
    out.append(cast(D, cx + 170, 460, 100, 14, strength=0.35, seed=3005))
    out.append(f'<path d="{lid}" fill="#C8CED6"/>' + metal(D, lid, cx + 46, cx + 254) + f'<path d="{ellipse_d(cx + 150, 352, 88, 96)}" fill="none" stroke="#FFFFFF" stroke-width="2.4" opacity="0.7"/>'
               + f'<path d="{ellipse_d(cx + 150, 352, 70, 78)}" fill="none" stroke="#6E7884" stroke-width="1.6" opacity="0.5"/>' + ink(lid, INK, 1.6, 3006, 1, 0.55))
    out.append(steel_bowl(D, cx, rim, 150, 104, 3006, ry=40))
    items = [(-96, 0, 34, "m"), (-30, 6, 36, "m"), (36, 2, 36, "m"), (100, -2, 33, "m"), (-64, -30, 34, "m"), (2, -32, 36, "b"), (68, -30, 34, "m"), (-30, -60, 33, "m"), (36, -60, 33, "m")]
    for k, (dx, dy, r, kd) in enumerate(sorted(items, key=lambda t: t[1])):
        out.append(laddoo(D, cx + dx, rim + dy - 4, r, 3010 + k, "motichoor" if kd == "m" else "besan"))
    # a front rim lip over the bottom row
    out.append(f'<path d="{smooth_open(ell_pts(cx, rim, 150, 40, 10, 170, 20))}" fill="none" stroke="#DDE2E8" stroke-width="7"/>')
    out.append(f'<path d="{smooth_open(ell_pts(cx, rim, 150, 40, 10, 170, 20))}" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.5"/>')
    # two laddoos on a small plate, one broken open; Dadi's spectacles beside it
    out.append(steel_bowl(D, 488, 514, 66, 14, 3020, ry=18))
    out.append(laddoo(D, 466, 500, 26, 3021))
    out.append(laddoo(D, 512, 498, 24, 3022, "besan"))
    gx, gy = 120, 520
    for dx in (-30, 30):
        out.append(f'<path d="{ellipse_d(gx + dx, gy, 26, 18)}" fill="#E8F2F8" opacity="0.35"/>')
        out.append(ink(ellipse_d(gx + dx, gy, 26, 18), "#5A3A1A", 3.4, 3023 + dx, 1, 0.95))
        out.append(f'<path d="M {gx + dx - 12} {gy - 8} q 8 -4 14 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.8"/>')
    out.append(ink(f"M {gx - 4} {gy - 4} q 4 -6 8 0", "#5A3A1A", 3, 3025, 1, 0.95))
    out.append(ink(f"M {gx - 56} {gy - 6} L {gx - 96} {gy - 30}", "#5A3A1A", 3, 3026, 1, 0.9))
    out.append(ink(f"M {gx + 56} {gy - 6} L {gx + 88} {gy - 34}", "#5A3A1A", 3, 3027, 1, 0.9))
    # lettering
    out.append(vignette(D, "#2A1A10", 0.32, 0.8))
    txt = [letters(D, 300, 132, "Dadi ke laddoo", SERIF_IT, 96, "#8A2A10", ["#B8401A", "#5A1406", "#D8602A"], 3030, max_w=460,
                   shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB880"),
           sub(300, 176, "EXTRA GHEE, EXTRA LOVE", "#2E5A8A", font=JOS, size=21, ls=6, line_w=24, gap=12)]
    return finish_art(D, out, txt, 3031, under="#E8D2B4", edge=2.2, bristle=0.4, grain=0.16)


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
