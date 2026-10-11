"""India, hand-painted (gouache / storybook) edition: 30 magnets for Indian-American families and anyone who loves India.

Same idiom as the Brasil, Korea and Ireland sets: warm paper, layered washes with pooled edges, brush strokes that
follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Hero words are
romanized Hindi (and a little Tamil-English, Gujarati and plain English), because the site fonts carry no Devanagari;
the one Devanagari word (माँ, "Maa") is painted stroke by stroke as brush calligraphy, never set in a font.
Colour story: marigold saffron, turmeric yellow, sindoor vermilion, rani pink, peacock blue-green, indigo, mango,
leaf green, terracotta clay and bright stainless steel, on warm cream paper.

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
import figures

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


def ground(D, base=PAPER, seed=1, tints=None, n=7):
    out = [paper(D.nid(), base, FLECK, seed)]
    if tints:
        out.append(blooms(seed + 1, tints, n, (20, 20, 580, 580), (90, 190), (0.08, 0.16)))
    return "".join(out)


def metal(D, d, x0, x1, pal=STEEL, op=0.85, dark_edge=0.75):
    """Polished-metal banding across a cylinder (stainless steel / brass): dark edges, a bright stripe, a reflection."""
    light, base, dark = pal
    g = D.lin([(0, dark, dark_edge), (0.1, base, 0.2), (0.24, light, op), (0.3, "#FFFFFF", op), (0.38, base, 0.1),
               (0.62, dark, 0.35), (0.72, base, 0.1), (0.86, light, 0.55), (1, dark, dark_edge)], x0, 0, x1, 0, "userSpaceOnUse")
    return f'<path d="{d}" fill="{g}"/>'


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
    for ring, (rr, cnt, col, sz) in enumerate(((0.86, 18, base, 0.34), (0.62, 13, mix(base, light, 0.35), 0.32), (0.38, 9, light, 0.3), (0.14, 4, mix(light, "#FFFFFF", 0.3), 0.24))):
        for i in range(cnt):
            a = 2 * math.pi * i / cnt + rnd.uniform(-0.2, 0.2) + ring * 0.4
            px, py = cx + math.cos(a) * r * rr, cy + math.sin(a) * r * rr * tilt
            c = col if rnd.random() < 0.7 else rnd.choice([dark, light, base])
            out.append(f'<path d="{blob(px, py, r * sz, r * sz * 0.8, rnd.randint(0, 9999), 0.3, 8, math.degrees(a))}" fill="{c}"/>')
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
            out.append(leaf_simple(D, x, y, r * 1.5, r * 0.45, a, LEAF, seed + i, vein=False, inkw=0.8))
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


def tile_wall(D, y0, y1, seed, base="#F6F2EA", grout="#C8C0B4", size=50, x0=0, x1=600, tint=None):
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{base}"/>']
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            c = mix(base, tint or "#FFFFFF", rnd.uniform(0, 0.4))
            out.append(f'<path d="{hg.org_rect(x + 2, y + 2, size - 4, size - 4, rnd.randint(0, 9999), 0.4, 12, 3)}" fill="{c}"/>')
            out.append(f'<path d="M {x + 6} {y + 8} l {size * 0.3:.0f} 0" stroke="#FFFFFF" stroke-width="2" opacity="0.6" stroke-linecap="round"/>')
            x += size
        y += size
    lines = []
    y = y0
    while y <= y1:
        lines.append(f'<path d="M {x0} {y} L {x1} {y}" stroke="{grout}" stroke-width="2.4"/>')
        y += size
    x = x0
    while x <= x1:
        lines.append(f'<path d="M {x} {y0} L {x} {y1}" stroke="{grout}" stroke-width="2.4"/>')
        x += size
    out.append("".join(lines))
    return "".join(out)


def sunburst(cx, cy, n, c1, c2, R=900, phase=0.0):
    out = []
    for i in range(n):
        a0 = 2 * math.pi * i / n + phase
        a1 = 2 * math.pi * (i + 1) / n + phase
        out.append(f'<path d="M {cx} {cy} L {cx + R * math.cos(a0):.1f} {cy + R * math.sin(a0):.1f} L {cx + R * math.cos(a1):.1f} {cy + R * math.sin(a1):.1f} Z" fill="{c1 if i % 2 else c2}"/>')
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


def wire_carrier(D, cx, base, cols, rows_y, gap, ring_w, seed, handle_top):
    """Steel-wire chai carrier: a ring for each glass at mid height, a base tray of wire and a tall loop handle."""
    out = []
    x0 = cx - gap * (cols - 1) / 2
    c = "#8A929C"
    # handle: two uprights in the middle, joined by a loop on top
    hx = cx
    out.append(taper([(hx - 7, base - 4), (hx - 7, handle_top + 18)], 4, 4, c))
    out.append(taper([(hx + 7, base - 4), (hx + 7, handle_top + 18)], 4, 4, c))
    loop = [(hx - 7, handle_top + 20), (hx - 26, handle_top + 6), (hx - 18, handle_top - 12), (hx, handle_top - 16), (hx + 18, handle_top - 12), (hx + 26, handle_top + 6), (hx + 7, handle_top + 20)]
    out.append(ink(smooth_open(loop), c, 5, seed, 1, 1))
    out.append(ink(smooth_open(loop), "#E8ECF0", 1.8, seed + 1, 1, 0.9))
    out.append(ink(f"M {hx - 5} {base - 4} L {hx - 5} {handle_top + 18}", "#F4F6F8", 1.4, seed + 2, 1, 0.8))
    return "".join(out)


@design("chai")
def chai():
    D = Doc2("in-ch")
    # a sun-warmed ochre wall with leaf shadows, morning light from the left
    out = [sky(D, [(0, "#F4C27A"), (0.6, "#EAA45E"), (1, "#D8884A")], 11, 600, ["#FFD898", "#C8743A", "#F6B870"], 120, angle=-82, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 140, 160, 420, "#FFF0C0", 0.5))
    out.append(leaf_shadows(D, 12, (330, 120, 640, 400), "#7A3A10", 30, (0.07, 0.14), (14, 30)))
    out.append(blooms(13, ["#C8743A", "#FFE0A8"], 6, (0, 0, 600, 450), (90, 170), (0.08, 0.15)))
    # the stall counter
    out.append(wood_planks(D, 474, 600, 14, WOOD, 3))
    out.append(f'<path d="M -10 470 L 610 470 L 610 482 L -10 482 Z" fill="#E8B87A"/>')
    out.append(f'<rect y="482" width="600" height="6" fill="#2A1408" opacity="0.4"/>')
    # brass kettle at the back right, steaming from its spout
    kx, kb = 470, 478
    kb_pts = [(kx - 70, kb), (kx - 80, kb - 46), (kx - 66, kb - 104), (kx - 44, kb - 126), (kx + 44, kb - 126), (kx + 66, kb - 104), (kx + 80, kb - 46), (kx + 70, kb)]
    out.append(cast(D, kx + 10, kb + 2, 90, 10, strength=0.45, seed=17))
    spout = [(kx - 72, kb - 70), (kx - 110, kb - 94), (kx - 130, kb - 140)]
    out.append(ink(smooth_open(spout), BRASS[2], 15, 18, 1, 1))
    out.append(ink(smooth_open(spout), BRASS[1], 10, 18, 1, 1))
    out.append(ink(smooth_open([(x - 2, y - 2) for x, y in spout]), BRASS[0], 3.4, 19, 1, 0.9))
    d = smooth_closed(kb_pts)
    out.append(f'<path d="{d}" fill="{BRASS[1]}"/>')
    out.append(metal(D, d, kx - 80, kx + 80, BRASS, 0.8, 0.7))
    out.append(strokes(D.nid(), d, (kx - 80, kb - 126, kx + 80, kb), ["#FFF0C0", "#8A5A14"], 20, n=36, angle=-90, length=(10, 40), width=(1, 3), opacity=(0.1, 0.3)))
    out.append(f'<path d="{ellipse_d(kx, kb - 40, 76, 8)}" fill="none" stroke="{BRASS[2]}" stroke-width="2" opacity="0.5"/>')
    out.append(ink(d, INK, 1.8, 21, 2, 0.6))
    out.append(painted(D, ell_pts(kx, kb - 126, 46, 10, 0, 360, 16), BRASS, 22, sk=0.1, n=4, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(kx, kb - 138, 11, 9, 23, 0.05, 10), ("#5A4A40", "#2A1E18", "#100A08"), 23, sk=0.1, n=3, inkw=1.2, hi=0.4))
    out.append(ink(smooth_open([(kx - 40, kb - 124), (kx - 36, kb - 190), (kx + 36, kb - 190), (kx + 40, kb - 124)]), "#3A3030", 5, 24, 1, 0.95))
    out.append(ink(smooth_open([(kx - 38, kb - 128), (kx - 34, kb - 186), (kx + 2, kb - 188)]), "#8A8080", 1.6, 24, 1, 0.8))
    out.append(steam(kx - 134, kb - 150, 76, 25, "#FFFFFF", 2, 16, 6, 0.6))
    # the wire carrier with its glasses: back row, wire frame, front row, front rail
    cx = 214
    gw, gh = 80, 104
    out.append(cast(D, cx + 14, 548, 186, 16, strength=0.5, seed=26))
    hb = 520
    for k, x in enumerate((cx - 44, cx + 44)):
        out.append(cutting_glass(D, x, hb, gw * 0.92, gh * 0.92, 30 + k, fill=0.78))
    c = "#7E8690"
    top = 300
    for sx in (-8, 8):
        out.append(taper([(cx + sx, 540), (cx + sx, top + 26)], 4.6, 4.6, c))
        out.append(taper([(cx + sx - 1.5, 540), (cx + sx - 1.5, top + 26)], 1.4, 1.4, "#F4F6F8", 0.8))
    loop = [(cx - 8, top + 28), (cx - 30, top + 10), (cx - 22, top - 12), (cx, top - 18), (cx + 22, top - 12), (cx + 30, top + 10), (cx + 8, top + 28)]
    out.append(ink(smooth_open(loop), c, 5.4, 34, 1, 1))
    out.append(ink(smooth_open(loop[:4]), "#F4F6F8", 1.8, 35, 1, 0.9))
    out.append(ink(smooth_open([(cx - 130, hb - gh * 0.42 + 8), (cx, hb - gh * 0.42 + 14), (cx + 130, hb - gh * 0.42 + 8)]), c, 3, 36, 1, 0.8))
    for k, x in enumerate((cx - 88, cx, cx + 88)):
        out.append(cutting_glass(D, x, 548, gw, gh, 40 + k, fill=0.8 if k != 2 else 0.6))
    tray = [(cx - 140, 542), (cx + 140, 542), (cx + 132, 552), (cx - 132, 552)]
    out.append(f'<path d="{pd(tray)}" fill="none" stroke="{c}" stroke-width="3.6" stroke-linejoin="round"/>')
    rail_y = 548 - gh * 0.44
    out.append(ink(smooth_open([(cx - 138, rail_y), (cx, rail_y + 7), (cx + 138, rail_y)]), c, 3.8, 37, 1, 1))
    out.append(ink(smooth_open([(cx - 138, rail_y - 1.4), (cx, rail_y + 5.6), (cx + 138, rail_y - 1.4)]), "#F4F6F8", 1.3, 38, 1, 0.9))
    for x in (cx - 88, cx, cx + 88):
        out.append(f'<path d="{ellipse_d(x, rail_y + 4 - abs(x - cx) * 0.02, gw * 0.44, 6)}" fill="none" stroke="{c}" stroke-width="2.6" opacity="0.9"/>')
    out.append(steam(cx - 88, 548 - gh - 10, 72, 39, "#FFFFFF", 2, 18, 6, 0.65))
    out.append(steam(cx + 44, hb - gh * 0.92 - 10, 60, 40, "#FFFFFF", 2, 16, 5, 0.5))
    # rusks on a scrap of paper, cardamom pods and a knob of ginger on the counter
    out.append(cast(D, 476, 552, 76, 10, strength=0.35, seed=50))
    out.append(painted(D, poly_pts([(400, 534), (540, 520), (556, 556), (414, 566)], 8, 51, 0.5), ("#FFFFFF", "#F2EADA", "#C8B8A0"), 51, sk=0.1, angle=0, n=6, inkw=1.2, hi=0.3))
    for k, (x, y, a) in enumerate(((438, 540, -8), (478, 534, -4), (518, 528, -10))):
        r = rect_pts(x - 22, y - 11, x + 22, y + 11, 8, 52 + k, 0.6)
        out.append(painted(D, rot(r, x, y, a), ("#F8D28A", "#D8984A", "#8A5418"), 52 + k, sk=0.22, angle=a, n=10, inkw=1.2, hi=0.4))
        out.append(specks(53 + k, (x - 17, y - 7, x + 17, y + 7), ["#FFF0C8", "#8A4A10"], 9, (0.6, 1.3), (0.5, 0.9)))
    for k, (x, y) in enumerate(((330, 560), (348, 568), (316, 572))):
        out.append(cardamom(D, x, y, 10, 20 * k, 60 + k))
    # lettering
    out.append(letters(D, 300, 160, "Chai?", SERIF_IT, 168, "#8A2A10", ["#B8401A", "#5A1406", "#D8602A"], 70, max_w=360,
                       shadow="#FFE8C0", soff=(0.02, 0.03), angle=-40, hi="#FFB880"))
    out.append(sub(300, 206, "THE ANSWER IS ALWAYS YES", "#4A1E08", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 71)


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
    """A little steel katori seen from directly above: rolled rim, shading inside, spice filling."""
    out = [f'<path d="{ellipse_d(cx + 3, cy + 4, r + 6, r + 6)}" fill="#2A3038" opacity="0.35"/>']
    out.append(f'<path d="{ellipse_d(cx, cy, r + 6, r + 6)}" fill="#E8ECF0"/>')
    g = D.lin([(0, "#FFFFFF", 1), (0.5, "#B8C0C8", 1), (1, "#6E7884", 1)], 0, 0, 1, 1)
    out.append(f'<path d="{ellipse_d(cx, cy, r + 6, r + 6)}" fill="{g}"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, r + 1, r + 1)}" fill="#5E6874"/>')
    out.append(spice_mound(D, cx, cy, r - 1, kind, seed))
    out.append(f'<path d="{ellipse_d(cx, cy, r + 6, r + 6)}" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
    out.append(f'<path d="M {cx - r * 0.7:.1f} {cy - r * 0.86:.1f} A {r + 3:.1f} {r + 3:.1f} 0 0 1 {cx + r * 0.2:.1f} {cy - r - 3:.1f}" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="0.9" stroke-linecap="round"/>')
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
    out = [sky(D, [(0, "#3E3A40"), (1, "#24222A")], 101, 600, ["#4A4650", "#1A1820", "#5A5460"], 140, angle=-30, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 180, 220, 420, "#FFE8C0", 0.18))
    out.append(specks(102, (0, 0, 600, 600), ["#6A6670", "#14121A"], 140, (0.8, 2.2), (0.3, 0.7)))
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
    out.append(letters(D, 236, 116, "masala dabba", SERIF_IT, 84, "#FFC24A", ["#FFD870", "#E89A1A", "#FFE6A0"], 140, max_w=400,
                       shadow="#0E0A10", soff=(0.02, 0.035), angle=-40, hi="#FFF0B0"))
    out.append(sub(236, 156, "NO RECIPE, JUST ANDAAZ", "#F2E6D0", font=JOS, size=19, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 141, "#FFFFFF", 0.5)


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
        for _ in range(int(w * h / 230)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            rr = rnd.uniform(1.4, 3.8)
            bl.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="#FFF4CC" opacity="0.5"/>'
                      f'<path d="M {x - rr:.1f} {y + rr * 0.2:.1f} A {rr:.1f} {rr:.1f} 0 0 0 {x + rr:.1f} {y + rr * 0.2:.1f}" stroke="#8A4A10" stroke-width="0.9" fill="none" opacity="0.55"/>')
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
    """Pattal: a plate stitched from dried sal leaves."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 10, cy + 14, rx * 1.04, ry * 1.04, strength=0.5, seed=seed)]
    rim = blob(cx, cy, rx, ry, seed, 0.04, 30)
    out.append(f'<path d="{rim}" fill="#8E9A44"/>')
    pals = [("#D8D088", "#9EA650", "#5A6A24"), ("#C8C870", "#8E9A44", "#4A5A1E"), ("#DCD890", "#A8A858", "#62622A")]
    for i in range(16):
        a = 2 * math.pi * i / 16 + rnd.uniform(-0.08, 0.08)
        ang = math.degrees(math.atan2(math.sin(a) * ry, math.cos(a) * rx))
        out.append(leaf_simple(D, cx + math.cos(a) * rx * 0.12, cy + math.sin(a) * ry * 0.12, rx * 0.88, rx * 0.2, ang, pals[i % 3], seed + i, inkw=0.9))
    out.append(leaf_simple(D, cx - rx * 0.3, cy + 4, rx * 0.62, rx * 0.2, -8, pals[0], seed + 40, inkw=0.9))
    for i in range(16):
        a = 2 * math.pi * (i + 0.5) / 16
        x, y = cx + math.cos(a) * rx * 0.5, cy + math.sin(a) * ry * 0.5
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a + 1.6) * 6:.1f} {math.sin(a + 1.6) * 3:.1f}" stroke="#F2E8B8" stroke-width="2" stroke-linecap="round" opacity="0.9"/>')
    out.append(ink(rim, INK, 1.6, seed, 1, 0.45))
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
    out.append(soft_glow(D, 300, 400, 320, "#FFB070", 0.32))
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
    # lettering
    out.append(letters(D, 300, 156, "Samosa", SERIF_IT, 140, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 220, max_w=420,
                       shadow="#4A0614", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 202, "WITH BOTH CHUTNEYS, PLEASE", "#FFE6C8", font=JOS, size=19, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 221, "#2A0A0A", 0.6)


# ================================================================ 4. teen seeti — the pressure cooker's third whistle
def gas_stove(D, x0, x1, top, seed):
    out = [cast(D, (x0 + x1) / 2, top + 66, (x1 - x0) * 0.55, 10, strength=0.5, seed=seed)]
    body = poly_pts([(x0, top), (x1, top), (x1 + 6, top + 62), (x0 - 6, top + 62)], 8, seed, 0.4)
    out.append(painted(D, body, ("#5A5E68", "#2E323A", "#121418"), seed, sdir=(0, 1), sk=0.12, angle=0, n=14, inkw=1.8, hi=0.25))
    out.append(f'<path d="{pd([(x0 - 2, top - 2), (x1 + 2, top - 2), (x1 + 3, top + 7), (x0 - 3, top + 7)])}" fill="#D8DDE2"/>')
    out.append(f'<path d="{pd([(x0 - 2, top + 5), (x1 + 2, top + 5), (x1 + 3, top + 8), (x0 - 3, top + 8)])}" fill="#6E7884"/>')
    for k, kx in enumerate((x0 + (x1 - x0) * 0.18, x0 + (x1 - x0) * 0.82)):
        out.append(f'<circle cx="{kx:.1f}" cy="{top + 36}" r="13" fill="#E8E4DC"/><circle cx="{kx:.1f}" cy="{top + 36}" r="13" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0.6"/>')
        out.append(f'<path d="M {kx:.1f} {top + 26} L {kx:.1f} {top + 38}" stroke="#2A2E36" stroke-width="3.4" stroke-linecap="round" transform="rotate({-50 + 100 * k} {kx:.1f} {top + 36})"/>')
    return "".join(out)


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


def pressure_cooker(D, cx, base, w, h, seed):
    """Aluminium pressure cooker in 3/4 view: pot, lid with the long black handle, the weight whistle on top."""
    out = []
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    ry = w * 0.16
    body = [(l, top), (l + 2, base - ry * 0.3)] + [(cx + (w / 2 - 2) * math.cos(math.radians(a)), base - ry * 0.3 + ry * math.sin(math.radians(a))) for a in range(175, 0, -15)] + [(r - 2, base - ry * 0.3), (r, top)]
    d = pd(body)
    out.append(f'<path d="{d}" fill="#C8CCD2"/>')
    out.append(metal(D, d, l, r, ("#FFFFFF", "#C0C6CE", "#5E6670"), 0.85, 0.8))
    out.append(strokes(D.nid(), d, (l, top, r, base + ry), ["#FFFFFF", "#7A828C"], seed, n=40, angle=-90, length=(20, 60), width=(1, 2.4), opacity=(0.1, 0.25)))
    out.append(f'<path d="{smooth_open(ell_pts(cx, base - ry * 0.3, w / 2 - 2, ry, 180, 0, 16))}" fill="none" stroke="#3A3E44" stroke-width="3" opacity="0.4"/>')
    out.append(ink(d, INK, 2, seed, 2, 0.65))
    # little helper handle on the left
    out.append(painted(D, poly_pts([(l - 34, top + 18), (l + 4, top + 16), (l + 4, top + 36), (l - 34, top + 38)], 6, seed + 1, 0.3), ("#5A5250", "#2A2422", "#0E0A0A"), seed + 1, sk=0.15, n=4, inkw=1.4, hi=0.4))
    # lid
    lid = ellipse_d(cx, top, w / 2 + 4, ry)
    out.append(f'<path d="{lid}" fill="#B8BEC6"/>')
    out.append(metal(D, lid, l, r, ("#FFFFFF", "#B8BEC6", "#5E6670"), 0.7, 0.6))
    out.append(f'<path d="{ellipse_d(cx, top - 3, w * 0.32, ry * 0.62)}" fill="#D8DDE2"/>')
    out.append(ink(ellipse_d(cx, top - 3, w * 0.32, ry * 0.62), INK, 1.2, seed + 2, 1, 0.4))
    out.append(ink(lid, INK, 1.8, seed + 3, 1, 0.65))
    # long handle: lid bar riding on the body bar, sticking out to the right
    hb2 = poly_pts([(r - 8, top + 8), (r + w * 0.46, top + 0), (r + w * 0.48, top + 14), (r - 6, top + 22)], 6, seed + 5, 0.3)
    out.append(painted(D, hb2, ("#4A4440", "#1E1A18", "#0A0808"), seed + 5, sdir=(0, 1), sk=0.2, angle=-8, n=8, inkw=1.4, hi=0.25))
    hb = poly_pts([(cx + w * 0.14, top - 9), (r + w * 0.48, top - 16), (r + w * 0.5, top - 2), (cx + w * 0.18, top + 8)], 6, seed + 4, 0.3)
    out.append(painted(D, hb, ("#6A6460", "#2E2A28", "#0A0808"), seed + 4, sdir=(0, 1), sk=0.2, angle=-8, n=10, inkw=1.6, hi=0.35))
    out.append(taper([(r + w * 0.02, top - 9), (r + w * 0.42, top - 14)], 2.4, 1.4, "#FFFFFF", 0.4))
    # vent pipe and the weight, lifted and hissing
    vx, vy = cx - w * 0.06, top - ry * 0.2
    out.append(f'<rect x="{vx - 4:.1f}" y="{vy - 12:.1f}" width="8" height="12" fill="#8A929C"/>')
    wt = [(vx - 13, vy - 16), (vx - 10, vy - 36), (vx - 5, vy - 46), (vx + 5, vy - 46), (vx + 10, vy - 36), (vx + 13, vy - 16)]
    out.append(painted(D, rot(wt, vx, vy - 16, 10), ("#5A5250", "#2A2422", "#0E0A0A"), seed + 6, sk=0.2, n=4, inkw=1.4, hi=0.45))
    return "".join(out), (vx, vy - 20)


def steam_puff(D, cx, cy, r, seed, op=0.95):
    """A round billow of steam: a cluster of soft painted puffs with a bluish shade side."""
    rnd = random.Random(seed)
    puffs = [(cx, cy, r)] + [(cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.5, r * rnd.uniform(0.48, 0.66)) for a in [rnd.uniform(0, 6.28) + k * 1.05 for k in range(6)]]
    shapes = " ".join(blob(x, y, rr, rr * 0.9, seed + i, 0.08, 14) for i, (x, y, rr) in enumerate(puffs))
    out = [f'<g opacity="{op}"><path d="{shapes}" fill="#C8D6DC" stroke="#9AAAB4" stroke-width="2.4" stroke-opacity="0.35"/>']
    inner = []
    for i, (x, y, rr) in enumerate(puffs):
        inner.append(f'<path d="{blob(x - rr * 0.18, y - rr * 0.22, rr * 0.82, rr * 0.7, seed + 30 + i, 0.1, 12)}" fill="#F6FAFA"/>')
        inner.append(f'<path d="{blob(x - rr * 0.32, y - rr * 0.36, rr * 0.4, rr * 0.3, seed + 60 + i, 0.15, 10)}" fill="#FFFFFF"/>')
    out.append(clipped(D, shapes, inner))
    out.append("</g>")
    return "".join(out)


@design("teen-seeti")
def teen_seeti():
    D = Doc2("in-ts")
    # white kitchen tiles with a teal-and-turmeric border band, warm window light from the left
    out = [tile_wall(D, 0, 470, 301, "#F2F4F0", "#C2CCC8", 60, -20, 620, "#D8F0EC")]
    out.append(f'<path d="{hg.org_rect(-10, 384, 620, 24, 302, 0.5, 14, 1)}" fill="#12808A"/>')
    for x in range(10, 600, 40):
        out.append(f'<path d="{blob(x, 396, 6, 6, x, 0.2, 8)}" fill="#F4C21A" opacity="0.95"/>')
    out.append(soft_glow(D, 40, 120, 420, "#FFE6B0", 0.5))
    out.append(f'<rect width="600" height="470" fill="{D.lin([(0, "#000000", 0), (1, "#1A2A2A", 0.16)], 0, 0, 1, 0)}"/>')
    # granite counter
    out.append(f'<path d="M -10 466 L 610 466 L 610 610 L -10 610 Z" fill="#3A3A3E"/>')
    out.append(specks(303, (0, 466, 600, 600), ["#8A8A90", "#1A1A1E", "#C8C0B0"], 240, (0.8, 2.2), (0.4, 0.9)))
    out.append(f'<path d="M -10 466 L 610 466" stroke="#6A6A70" stroke-width="5"/>')
    # stove, flame, cooker
    out.append(gas_stove(D, 70, 470, 478, 304))
    out.append(blue_flame(D, 220, 482, 56, 305))
    ck, (wx, wy) = pressure_cooker(D, 220, 486, 196, 148, 306)
    out.append(ck)
    # a steel tumbler and a little steel katori of dal waiting on the counter
    out.append(cast(D, 530, 548, 30, 6, strength=0.45, seed=307))
    tb = [(506, 470), (554, 470), (548, 546), (512, 546)]
    out.append(f'<path d="{pd(tb)}" fill="#C8CED6"/>' + metal(D, pd(tb), 506, 554) + ink(pd(tb), INK, 1.6, 308, 1, 0.6))
    out.append(f'<path d="{ellipse_d(530, 470, 24, 5)}" fill="#6E7884"/>')
    # three whistles: three billows of steam climbing, numbered
    for k, (sx, sy, s) in enumerate(((wx + 44, wy - 30, 0.66), (wx + 146, wy - 62, 0.84), (wx + 266, wy - 78, 1.0))):
        out.append(steam_puff(D, sx, sy, 58 * s, 310 + k))
        out.append(label(sx, sy + 16 * s, str(k + 1), DMS, int(50 * s), "#12808A"))
    out.append(taper([(wx, wy), (wx + 6, wy - 14), (wx + 18, wy - 30)], 5, 16, "#FFFFFF", 0.85))
    for a in (-70, -30, 10):
        rr = math.radians(a - 90)
        out.append(pline([(wx + math.cos(rr) * 22, wy + math.sin(rr) * 22), (wx + math.cos(rr) * 36, wy + math.sin(rr) * 36)], "#C8281E", 3, 312 + a, 0.9, 1))
    # lettering
    out.append(letters(D, 300, 122, "teen seeti", SERIF_IT, 118, "#B8281E", ["#D8402A", "#7A0E0A", "#F06A4A"], 320, max_w=440,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB0A0"))
    out.append(sub(300, 166, "THREE WHISTLES & THE DAL IS DONE", "#12606A", font=JOS, size=18, ls=4, line_w=16, gap=10))
    return finish_b(D, out, 321)


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


@design("shubh-deepavali")
def shubh_deepavali():
    D = Doc2("in-sd")
    out = [sky(D, [(0, "#2A1450"), (0.55, "#4A1E5A"), (1, "#2A0E2A")], 401, 600, ["#3A1A60", "#1A0A30", "#5A2A6A"], 120, angle=-4, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 420, 360, "#FF9A3A", 0.35))
    # a string of tiny lights draped across the top, and a marigold toran
    lights = [(-10, 30), (150, 64), (300, 50), (450, 66), (610, 28)]
    cp = catmull(lights, 10)
    out.append(pline(lights, "#1A0A20", 1.6, 402, 0.9, 1))
    for i, (x, y) in enumerate(cp[::5]):
        c = ["#FFE27A", "#FF8A5A", "#FFFFFF", "#8AE0D8"][i % 4]
        out.append(soft_glow(D, x, y + 6, 20, c, 0.55))
        out.append(f'<circle cx="{x:.1f}" cy="{y + 6:.1f}" r="3.6" fill="{c}"/>')
    # the floor: dark stone, the rangoli on it in perspective
    out.append(f'<path d="M -10 330 L 610 330 L 610 610 L -10 610 Z" fill="#3A2028"/>')
    out.append(f'<path d="M -10 330 L 610 330 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#1A0A12", 0.6), (1, "#5A3030", 0.3)])}"/>')
    out.append(strokes(D.nid(), pd([(-10, 330), (610, 330), (610, 610), (-10, 610)]), (-40, 330, 610, 600), ["#5A3A40", "#1A0A10"], 403, n=80, angle=0, length=(40, 140), width=(2, 6), opacity=(0.1, 0.25)))
    out.append(soft_glow(D, 300, 470, 300, "#FFB050", 0.35))
    out.append(rangoli(D, 300, 468, 200, 404, 0.42))
    # diyas around the rangoli (back ones smaller), with scattered marigold petals
    rnd = random.Random(405)
    ring = []
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.3
        x, y = 300 + math.cos(a) * 236, 468 + math.sin(a) * 236 * 0.42
        ring.append((y, x, a))
    for y, x, a in sorted(ring):
        s = 22 + (y - 368) * 0.1
        out.append(diya(D, x - s * 0.1, y, s, 406 + int(x)))
    for k in range(28):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(1.05, 1.35)
        x, y = 300 + math.cos(a) * 200 * rr, 468 + math.sin(a) * 84 * rr
        if y < 350 or y > 588 or x < 30 or x > 570:
            continue
        out.append(f'<path d="{blob(x, y, 5, 3, k + 410, 0.25, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2901E", "#F4C21A", "#D6342A"])}"/>')
    # lettering
    out.append(letters(D, 300, 182, "Shubh Deepavali", SERIF_IT, 76, "#FFD06A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 420, max_w=470,
                       shadow="#12061E", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 226, "MAY YOUR HOME BE FULL OF LIGHT", "#FFC8A0", font=JOS, size=18, ls=4, line_w=20, gap=10))
    return finish_b(D, out, 421, "#FFFFFF", 0.45)


# ================================================================ 6. chalo! — the auto-rickshaw at the corner
def wheel(D, cx, cy, r, seed):
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#1A1A1E"/>',
           f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.62:.1f}" fill="#3A3A40"/>',
           f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.5:.1f}" fill="#C8CED6"/>',
           metal(D, ellipse_d(cx, cy, r * 0.5, r * 0.5), cx - r * 0.5, cx + r * 0.5),
           f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.16:.1f}" fill="#3A3A40"/>']
    for k in range(5):
        a = math.radians(k * 72 + seed)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.32:.1f}" cy="{cy + math.sin(a) * r * 0.32:.1f}" r="{r * 0.05:.1f}" fill="#3A3A40"/>')
    out.append(f'<path d="M {cx - r * 0.7:.1f} {cy - r * 0.5:.1f} A {r * 0.86:.1f} {r * 0.86:.1f} 0 0 1 {cx + r * 0.2:.1f} {cy - r * 0.84:.1f}" stroke="#6A6A72" stroke-width="2" fill="none"/>')
    return "".join(out)


def auto_rickshaw(D, x, base, s, seed):
    """Side view of a generic auto-rickshaw facing left: black body, yellow canvas hood, open passenger bay."""
    def P(pts):
        return [(x + px * s, base + py * s) for px, py in pts]

    def box(pts, step=6, j=0.35, sd=None):
        return poly_pts(P(pts), step, sd or seed, j)

    yl = ("#FFE680", "#F6C21C", "#A87A06")
    blk = ("#62626A", "#26262C", "#0A0A0E")
    out = [cast(D, x + 160 * s, base + 2, 196 * s, 13 * s, strength=0.55, seed=seed)]
    # open bay (dark interior) behind everything
    out.append(f'<path d="{pd(P([(96, -208), (290, -208), (290, -50), (96, -50)]))}" fill="#1E181C"/>')
    out.append(f'<path d="{pd(P([(96, -208), (290, -208), (290, -50), (96, -50)]))}" fill="{D.lin([(0, "#4A3A40", 0.7), (1, "#000000", 0.1)], 0, 0, 1, 0)}"/>')
    # passenger bench and backrest, grab rail
    out.append(painted(D, box([(262, -196), (288, -196), (288, -104), (262, -104)], sd=seed + 1), ("#F07A6A", "#C02C22", "#6A0E0A"), seed + 1, sdir=(1, 0.3), sk=0.2, angle=-90, n=8, inkw=1.3, hi=0.35))
    out.append(painted(D, box([(186, -112), (288, -112), (288, -86), (186, -86)], sd=seed + 2), ("#F07A6A", "#C02C22", "#6A0E0A"), seed + 2, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.3, hi=0.4))
    out.append(ink(smooth_open(P([(124, -156), (196, -156)])), "#E8ECF0", 3.2 * s, seed + 3, 1, 1))
    out.append(ink(smooth_open(P([(196, -156), (196, -112)])), "#E8ECF0", 3 * s, seed + 4, 1, 1))
    # driver's seat and the handlebar
    out.append(painted(D, box([(104, -124), (140, -124), (140, -108), (104, -108)], sd=seed + 5), blk, seed + 5, sk=0.2, n=4, inkw=1.2, hi=0.3))
    out.append(ink(smooth_open(P([(70, -150), (94, -160), (108, -152)])), "#C8CED6", 3.4 * s, seed + 6, 1, 1))
    # rear body over the engine, lower body and footboard
    rear = box([(186, -86), (300, -86), (306, -70), (306, -40), (186, -40)], sd=seed + 7)
    out.append(painted(D, rear, blk, seed + 7, sdir=(0.3, 1), sk=0.14, angle=0, n=14, inkw=1.7, hi=0.25))
    floor = box([(80, -56), (190, -56), (190, -40), (80, -40)], sd=seed + 8)
    out.append(painted(D, floor, blk, seed + 8, sdir=(0, 1), sk=0.1, angle=0, n=6, inkw=1.4, hi=0.2))
    skirt = box([(30, -40), (306, -40), (302, -24), (34, -24)], sd=seed + 9)
    out.append(painted(D, skirt, ("#FFE680", "#F2BC18", "#A87A06"), seed + 9, sdir=(0, 1), sk=0.15, angle=0, n=14, inkw=1.4, hi=0.4))
    for k in range(13):
        out.append(f'<circle cx="{x + (70 + k * 18) * s:.1f}" cy="{base - 32 * s:.1f}" r="{2 * s:.1f}" fill="#1E1E24" opacity="0.85"/>')
    # front cowl (the nose) with headlamp and a painted stripe
    nose = box([(16, -24), (10, -60), (8, -104), (18, -136), (40, -152), (70, -156), (92, -146), (94, -64), (100, -56), (80, -40), (40, -24)], 7, 0.3, seed + 10)
    out.append(painted(D, nose, blk, seed + 10, sdir=(0.6, 0.6), sk=0.16, angle=-75, n=16, inkw=1.8, hi=0.35, hik=0.07))
    out.append(taper(P([(12, -70), (40, -76), (90, -80)]), 6 * s, 4 * s, "#F6C21C", 0.95))
    lamp = P([(16, -118)])[0]
    out.append(soft_glow(D, lamp[0] - 10 * s, lamp[1], 30 * s, "#FFF2B0", 0.5))
    out.append(f'<circle cx="{lamp[0]:.1f}" cy="{lamp[1]:.1f}" r="{10 * s:.1f}" fill="#FFF8D8" stroke="#A8B0BA" stroke-width="{3 * s:.1f}"/>')
    out.append(f'<circle cx="{lamp[0] - 3 * s:.1f}" cy="{lamp[1] - 3 * s:.1f}" r="{3 * s:.1f}" fill="#FFFFFF"/>')
    # windscreen pillar and glass
    out.append(f'<path d="{pd(P([(62, -152), (76, -210), (98, -210), (88, -150)]))}" fill="#CFE8F0" opacity="0.5"/>')
    out.append(taper(P([(60, -152), (74, -214)]), 5 * s, 4 * s, "#26262C"))
    out.append(taper(P([(66, -160), (76, -204)]), 1.6 * s, 1.2 * s, "#FFFFFF", 0.6))
    # the yellow canvas hood
    hood = box([(68, -206), (72, -230), (90, -248), (268, -254), (294, -242), (304, -214), (306, -86), (290, -86), (288, -202), (100, -206)], 7, 0.3, seed + 11)
    out.append(painted(D, hood, yl, seed + 11, sdir=(0.2, 1), sk=0.14, angle=0, n=28, inkw=1.8, hi=0.45, hik=0.06))
    out.append(f'<path d="{pd(P([(290, -206), (306, -214), (306, -86), (290, -86)]))}" fill="{yl[2]}" opacity="0.45"/>')
    for k in range(4):
        xx = 120 + k * 46
        out.append(pline(P([(xx, -252), (xx + 1, -208)]), yl[2], 2 * s, seed + 12 + k, 0.55, 1))
    out.append(taper(P([(96, -244), (180, -248), (262, -250)]), 3 * s, 2 * s, "#FFFFFF", 0.55))
    # a marigold garland strung under the hood's front edge
    out.append(garland(D, P([(80, -206), (94, -186), (110, -204)]), 6 * s, seed + 20, leaves=False))
    # mud flap, tail lamp, wheels
    out.append(f'<path d="{pd(P([(284, -24), (298, -24), (298, 0), (284, 0)]))}" fill="#1A1A1E"/>')
    out.append(f'<path d="{pd(P([(300, -82), (308, -82), (308, -64), (300, -64)]))}" fill="#E8302A"/>')
    out.append(wheel(D, x + 54 * s, base - 18 * s, 22 * s, 3))
    out.append(wheel(D, x + 244 * s, base - 18 * s, 24 * s, 21))
    return "".join(out)


@design("chalo")
def chalo():
    D = Doc2("in-cl")
    # dusty-pink wall in late-afternoon sun, a bougainvillea spilling over it
    out = [sky(D, [(0, "#F6C4B0"), (1, "#E8987E")], 501, 600, ["#FFD8C8", "#D8806A", "#F8B8A0"], 110, angle=-82, sop=(0.06, 0.16))]
    out.append(blooms(502, ["#C8705A", "#FFE0D0"], 7, (0, 0, 600, 440), (90, 170), (0.08, 0.15)))
    # a painted blue door at the right edge
    door = hg.org_rect(456, 176, 180, 290, 503, 0.6, 14, 2)
    out.append(f'<path d="{door}" fill="#2E6E9A"/>')
    out.append(f'<path d="{hg.org_rect(474, 194, 150, 272, 504, 0.6, 14, 2)}" fill="#1E4A6E"/>')
    out.append(strokes(D.nid(), door, (456, 176, 636, 466), ["#5A9AC8", "#0E2A4A"], 505, n=40, angle=-90, length=(30, 90), width=(1.5, 4), opacity=(0.15, 0.35)))
    for y in (250, 340):
        out.append(f'<path d="{hg.org_rect(490, y, 110, 60, y, 0.5, 10, 2)}" fill="none" stroke="#5A9AC8" stroke-width="3" opacity="0.6"/>')
    out.append(leaf_shadows(D, 506, (0, 250, 450, 440), "#7A2A1A", 20, (0.06, 0.12), (14, 28)))
    # bougainvillea cascading over the top of the door
    rnd = random.Random(507)
    vine = [(620, 140), (560, 170), (500, 168), (452, 196), (432, 250)]
    cv = catmull(vine, 6)
    out.append(pline(vine, "#5A3A1A", 3, 508, 0.8, 1))
    for k in range(110):
        p = cv[rnd.randint(0, len(cv) - 1)]
        x, y = p[0] + rnd.uniform(-34, 34), p[1] + rnd.uniform(-26, 40)
        if x < 412 or y < 128:
            continue
        if rnd.random() < 0.3:
            out.append(leaf_simple(D, x, y, 18, 6, rnd.uniform(0, 360), LEAF, k + 509, vein=False, inkw=0.8))
        else:
            c = rnd.choice([RANI, ("#FF9AC8", "#E8448A", "#9A1A50")])
            out.append(f'<path d="{blob(x, y, 9, 8, k + 600, 0.25, 8)}" fill="{c[1]}"/><path d="{blob(x - 2, y - 2, 4, 3, k + 700, 0.2, 6)}" fill="{c[0]}" opacity="0.8"/>')
    for k in range(6):
        x, y = rnd.uniform(380, 560), rnd.uniform(420, 470)
        out.append(f'<path d="{blob(x, y, 5, 4, k + 800, 0.25, 8, rnd.uniform(0, 90))}" fill="#E8448A" opacity="0.85"/>')
    # street and kerb
    out.append(f'<path d="M -10 466 L 610 466 L 610 610 L -10 610 Z" fill="#B8A890"/>')
    out.append(f'<path d="M -10 466 L 610 466 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#7A6A58", 0.5), (1, "#E8D8C0", 0.2)])}"/>')
    out.append(strokes(D.nid(), pd([(-10, 466), (610, 466), (610, 610), (-10, 610)]), (-40, 466, 610, 600), ["#8A7A68", "#E8DCC8", "#6A5A48"], 510, n=80, angle=0, length=(30, 120), width=(2, 5), opacity=(0.12, 0.3)))
    for x in range(-10, 610, 40):
        out.append(f'<path d="{hg.org_rect(x, 452, 40, 16, x + 999, 0.4, 10, 1)}" fill="{"#2A2A2A" if (x // 40) % 2 else "#F2EEE6"}"/>')
    out.append(f'<rect y="466" width="600" height="4" fill="#3A2A1A" opacity="0.3"/>')
    # the auto
    out.append(auto_rickshaw(D, 96, 556, 1.2, 512))
    # dust and speed strokes behind it
    out.append(puff_cloud(D, 520, 552, 76, 513, pal=("#F4E8D8", "#E8D8C0", "#B8A890"), inkw=0, op=0.75))
    for k, y in enumerate((330, 372, 414)):
        out.append(taper([(484, y), (556, y - 2)], 3.4, 0.6, "#FFFFFF", 0.75))
    # lettering
    out.append(letters(D, 250, 140, "Chalo!", SERIF_IT, 156, "#1E4A6E", ["#2E6A9A", "#0E2A4A", "#4A8AC0"], 520, max_w=380,
                       shadow="#FFF0E6", soff=(0.022, 0.035), angle=-40, hi="#A8D0F0"))
    out.append(sub(250, 188, "KAHAN JAANA HAI?", "#7A1E3A", font=JOS, size=21, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 521)


# ================================================================ 7. dosa — a masala dosa on a banana leaf, sambar and chutneys
def banana_sheet(D, pts, seed, vein_dir=-90, pal=("#8AD06A", "#3E9A3A", "#1E5A1E")):
    """A cut piece of banana leaf: glossy green, fine parallel veins at right angles to the midrib, a split or two."""
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    g = D.lin([(0, pal[0], 0.55), (0.5, pal[1], 0), (1, pal[2], 0.45)], 0, 0, 1, 1)
    out.append(f'<path d="{d}" fill="{g}"/>')
    x0, y0, x1, y1 = bbox(pts)
    inner = []
    rnd = random.Random(seed)
    a = math.radians(vein_dir)
    ux, uy = math.cos(a), math.sin(a)
    for k in range(-60, 60):
        off = k * 7
        cx, cy = (x0 + x1) / 2 + -uy * off, (y0 + y1) / 2 + ux * off
        inner.append(f'<path d="M {cx - ux * 600:.1f} {cy - uy * 600:.1f} L {cx + ux * 600:.1f} {cy + uy * 600:.1f}" stroke="{pal[2] if k % 3 else pal[0]}" stroke-width="{1.2 if k % 3 else 1.6}" opacity="{0.25 if k % 3 else 0.4}"/>')
    inner.append(strokes(D.nid(), d, (x0, y0, x1, y1), [pal[0], pal[2]], seed, n=60, angle=vein_dir, length=(30, 90), width=(2, 5), opacity=(0.08, 0.2), curve=0.05))
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#1E4A1A", 1.6, seed, 1, 0.5))
    return "".join(out)


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
    out.append(soft_glow(D, 160, 120, 460, "#FFE0A8", 0.28))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#000000", 0), (1, "#000000", 0.3)], 0, 0, 1, 1)}"/>')
    # the banana leaf
    leaf = poly_pts([(-20, 262), (620, 236), (620, 600), (-20, 616)], 30, 702, 2)
    out.append(banana_sheet(D, leaf, 703, vein_dir=-80))
    out.append(clipped(D, smooth_closed(leaf), [blooms(704, ["#B8F08A", "#1A5A1A", "#6AC04A"], 9, (0, 260, 600, 600), (70, 150), (0.12, 0.22))]))
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
    # lettering
    out.append(letters(D, 300, 168, "Dosa", SERIF_IT, 168, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 720, max_w=360,
                       shadow="#1A0A04", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 214, "EXTRA SAMBAR, AMMA!", "#FFE6C8", font=JOS, size=21, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 721, "#1A0A04", 0.6)


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
    # a halwai's stall at dusk: warm marigold wall, string of bulbs
    out = [sky(D, [(0, "#F6B23A"), (0.7, "#EE8A2A"), (1, "#D8641E")], 801, 600, ["#FFD070", "#C8541A", "#FFC060"], 120, angle=-84, sop=(0.06, 0.16))]
    out.append(blooms(802, ["#FFE08A", "#C8501A"], 7, (0, 0, 600, 420), (90, 170), (0.08, 0.16)))
    out.append(soft_glow(D, 300, 380, 300, "#FFF0B0", 0.45))
    # a great black kadai of bubbling oil behind, jalebis frying in it
    kx, ky = 300, 352
    out.append(f'<path d="{ellipse_d(kx, ky + 46, 250, 60)}" fill="#1A1210"/>')
    out.append(painted(D, ell_pts(kx, ky + 20, 250, 70, 0, 180, 24), ("#5A5048", "#2A221E", "#0E0A08"), 803, sdir=(0, 1), sk=0.12, angle=0, n=30, inkw=2, hi=0.3))
    out.append(f'<path d="{ellipse_d(kx, ky, 250, 42)}" fill="#3A2E28"/>')
    out.append(f'<path d="{ellipse_d(kx, ky + 3, 236, 36)}" fill="#C88A1A"/>')
    out.append(f'<path d="{ellipse_d(kx, ky + 3, 236, 36)}" fill="{D.lin([(0, "#FFE07A", 0.6), (1, "#7A4A0A", 0.6)])}"/>')
    rnd = random.Random(804)
    for k in range(5):
        out.append(jalebi(D, kx - 170 + k * 84, ky + 4, 34, 805 + k, sq=0.3, turns=2.1, w=7))
    for k in range(40):
        x, y = kx + rnd.uniform(-220, 220), ky + rnd.uniform(-26, 30)
        if ((x - kx) / 230) ** 2 + ((y - ky - 3) / 34) ** 2 > 1:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 3.6):.1f}" fill="none" stroke="#FFF2B0" stroke-width="1.2" opacity="0.8"/>')
    out.append(ink(ellipse_d(kx, ky, 250, 42), INK, 2, 806, 1, 0.6))
    out.append(steam(kx - 60, ky - 30, 80, 807, "#FFFFFF", 3, 60, 7, 0.4))
    # the steel plate in front, heaped with fresh jalebis
    px, py = 300, 498
    out.append(cast(D, px + 10, py + 30, 230, 34, strength=0.55, seed=808))
    plate = ellipse_d(px, py, 224, 66)
    out.append(f'<path d="{plate}" fill="#B8C0C8"/>')
    out.append(metal(D, plate, px - 224, px + 224))
    out.append(f'<path d="{ellipse_d(px, py + 4, 196, 52)}" fill="#D8DEE4"/>')
    out.append(f'<path d="{ellipse_d(px, py + 4, 196, 52)}" fill="{D.lin([(0, "#6E7884", 0.5), (1, "#FFFFFF", 0.5)])}"/>')
    out.append(ink(plate, INK, 1.8, 809, 1, 0.6))
    out.append(f'<path d="{blob(px + 40, py + 20, 120, 18, 810, 0.2, 14)}" fill="#E8901A" opacity="0.35"/>')
    spots = [(196, 494, 48), (296, 510, 52), (398, 494, 48), (246, 470, 46), (350, 468, 46), (300, 446, 44)]
    for k, (x, y, R) in enumerate(spots):
        out.append(jalebi(D, x, y, R, 811 + k))
    for x, y, r in ((520, 560, 9), (86, 448, 7), (540, 420, 6)):
        out.append(sparkle(x, y, r, "#FFFFFF", 0.85))
    # lettering
    out.append(letters(D, 300, 148, "Jalebi", SERIF_IT, 150, "#8A1A0A", ["#B8301A", "#5A0A04", "#D8502A"], 820, max_w=400,
                       shadow="#FFE8B0", soff=(0.022, 0.035), angle=-40, hi="#FFA070"))
    out.append(sub(300, 194, "GARAM GARAM, FROM THE KADAI", "#5A1406", font=JOS, size=19, ls=5, line_w=20, gap=12))
    return finish_b(D, out, 821)


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
    out.append(f'<path d="{blob(cx, rim_y - 16, rx * 0.96, ry + 22, 905, 0.06, 20)}" fill="#F6EED8"/>')
    rnd = random.Random(906)
    grains = []
    for _ in range(520):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rr * rx * 0.94, rim_y - 16 + math.sin(a) * rr * (ry + 18)
        c = rnd.choices(["#FFFDF4", "#F8EED0", "#F6C24A", "#F2A01E", "#E8E0C8", "#E8701A"], [5, 3, 3, 2.4, 2, 0.8])[0]
        ang = rnd.uniform(-40, 40)
        grains.append(f'<path d="{blob(x, y, 4.6, 1.5, rnd.randint(0, 9999), 0.1, 6, ang)}" fill="{c}"/>')
    grains.append(f'<path d="{blob(cx + 30, rim_y - 20, 60, 14, 907, 0.3, 12)}" fill="#F2A01E" opacity="0.35"/>')
    grains.append(f'<path d="{blob(cx - 70, rim_y - 8, 40, 10, 908, 0.3, 12)}" fill="#F6C24A" opacity="0.3"/>')
    out.append(clipped(D, blob(cx, rim_y - 16, rx * 0.96, ry + 22, 905, 0.06, 20), grains))
    # crisp fried onions, mint, a boiled egg, whole spices
    for k in range(26):
        x, y = cx + rnd.uniform(-110, 110), rim_y - 16 + rnd.uniform(-26, 26)
        out.append(taper([(x, y), (x + rnd.uniform(-8, 8), y + rnd.uniform(-5, 5)), (x + rnd.uniform(-10, 10), y + rnd.uniform(-5, 5))], 3, 1.2, rnd.choice(["#8A4A14", "#A8601E", "#6A3410"]), 0.9))
    for k in range(7):
        x, y = cx + rnd.uniform(-100, 100), rim_y - 18 + rnd.uniform(-22, 18)
        out.append(leaf_simple(D, x, y, 16, 6, rnd.uniform(0, 360), ("#8AD06A", "#3E9A3A", "#1A5A1A"), 910 + k, vein=False, inkw=0.7))
    ex, ey = cx + 40, rim_y - 22
    out.append(painted(D, blob_pts(ex, ey, 24, 17, 920, 0.04, 14), WHITE, 920, sk=0.2, n=6, inkw=1.3, hi=0.4))
    out.append(f'<path d="{blob(ex + 2, ey + 1, 11, 9, 921, 0.08, 10)}" fill="#F6C21C"/><path d="{blob(ex, ey - 1, 5, 4, 922, 0.1, 8)}" fill="#FFE47A"/>')
    out.append(star_anise(D, cx - 70, rim_y - 26, 12, 923, 20))
    out.append(dried_chilli(D, cx - 20, rim_y - 34, 40, 20, 924))
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
    out.append(steam(cx - 20, rim_y - 50, 100, 931, "#FFFFFF", 3, 50, 9, 0.4))
    # lettering
    out.append(letters(D, 300, 150, "Biryani", SERIF_IT, 140, "#FFC86A", ["#FFE0A0", "#E89A2A", "#FFF0C8"], 940, max_w=420,
                       shadow="#061A1C", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 196, "WORTH EVERY MINUTE OF DUM", "#9AE0D8", font=JOS, size=19, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 941, "#FFFFFF", 0.4)


# ================================================================ 10. mango season — a crate of Alphonsos in straw
@design("mango-season")
def mango_season():
    D = Doc2("in-mg")
    out = [ground(D, "#FBEBD0", 1001, ["#F6C46A", "#F2A07A", "#FFE6A8"])]
    out.append(soft_glow(D, 300, 330, 320, "#FFE08A", 0.4))
    # a few mango leaves bleeding in from the top corners
    for k, (x, y, a, L) in enumerate(((-10, 230, -20, 170), (20, 270, 10, 140), (610, 250, 200, 160), (590, 290, 175, 130))):
        out.append(leaf_simple(D, x, y, L, L * 0.17, a, ("#7ABA5A", "#2E7A34", "#124A1E"), 1002 + k, inkw=1.2))
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
    out.append(label(300, top + 89, "RATNAGIRI · GRADE A", JOS, 21, "#8A3A12", ls=4, max_w=300, extra=' opacity="0.75"'))
    # a whole mango with its leaf, and a katori of aamras with two puffed puris
    out.append(mango(D, 498, 546, 42, -150, 1050, leaf=True))
    out.append(leaf_simple(D, 60, 540, 70, 14, -20, ("#7ABA5A", "#2E7A34", "#124A1E"), 1051, inkw=1.1))
    aam = (f'<path d="{ellipse_d(116, 513, 42, 12)}" fill="#F6A21E"/>'
           f'<path d="{blob(108, 510, 18, 4, 1057, 0.2, 8)}" fill="#FFD86A" opacity="0.85"/>'
           f'<path d="M 128 512 q 6 -2 10 1" stroke="#C8600A" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(steel_bowl(D, 116, 510, 48, 30, 1058, fill=aam))
    # lettering
    out.append(letters(D, 300, 132, "mango season", SERIF_IT, 104, "#D8641A", ["#F28A2A", "#A8400A", "#FFA84A"], 1070, max_w=460,
                       shadow="#FFF6E0", soff=(0.022, 0.035), angle=-40, hi="#FFD0A0"))
    out.append(sub(300, 176, "AAM KA MAUSAM · BY THE DOZEN", "#2E6A2A", font=JOS, size=18, ls=4, line_w=18, gap=10))
    return finish_b(D, out, 1071)


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
    out = [ground(D, "#F8E8D0", 1101, ["#F2C89A", "#E8B0A0", "#FFE0B0"])]
    # a kitchen window behind: lime-washed blue frame, morning outside
    out.append(f'<path d="{hg.org_rect(70, 250, 460, 230, 1102, 0.8, 14, 2)}" fill="#2E6E9A"/>')
    out.append(f'<path d="{hg.org_rect(86, 264, 428, 202, 1103, 0.8, 14, 2)}" fill="#CFE6EE"/>')
    out.append(soft_glow(D, 300, 360, 220, "#FFFFFF", 0.6))
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
    out.append(painted(D, poly_pts([(296, 486), (520, 486), (526, 556), (290, 556)], 8, 1107, 0.3), ("#5A5E68", "#2E323A", "#121418"), 1107, sdir=(0, 1), sk=0.12, angle=0, n=10, inkw=1.6, hi=0.25))
    out.append(f'<path d="{pd([(294, 482), (522, 482), (523, 492), (293, 492)])}" fill="#D8DDE2"/>')
    out.append(f'<path d="{ellipse_d(bx, 482, 52, 10)}" fill="#1A1A1E"/>')
    out.append(soft_glow(D, bx, 440, 120, "#FFB040", 0.55))
    out.append(blue_flame(D, bx, 480, 46, 1108))
    for k in range(4):
        a_ = math.radians(k * 90 + 45)
        out.append(f'<path d="M {bx + math.cos(a_) * 30:.1f} {480 + math.sin(a_) * 6:.1f} L {bx + math.cos(a_) * 70:.1f} {478 + math.sin(a_) * 12:.1f}" stroke="#3A3A40" stroke-width="5" stroke-linecap="round"/>')
    out.append(roti(D, bx, 430, 92, 26, 1109, puffed=0.85))
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
    out.append(letters(D, 300, 92, "Bas,", SERIF_IT, 74, "#2E6E9A", ["#4A8AC0", "#1E4A6E", "#6AA8D8"], 1130, max_w=200,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8E0F0"))
    out.append(letters(D, 300, 182, "one more roti", SERIF_IT, 96, "#B8401A", ["#D85A2A", "#7A1E0A", "#F07A4A"], 1131, max_w=470,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFC0A0"))
    out.append(sub(300, 224, "MUMMY, EVERY SINGLE MEAL", "#7A4A2A", font=JOS, size=17, ls=4, line_w=18, gap=10))
    return finish_b(D, out, 1132)


# ================================================================ 12. filter kaapi — davara and tumbler, frothing over
def tumbler(D, cx, base, w, h, seed, pal=STEEL, flare=0.12):
    """Tall South Indian steel tumbler with a rolled lip, slightly tapered."""
    l0, r0 = cx - w / 2, cx + w / 2
    l1, r1 = cx - w * (0.5 - flare), cx + w * (0.5 - flare)
    top = base - h
    ry = w * 0.14
    body = [(l0, top)] + [(l1, base - ry * 0.5)] + [(cx + (w * (0.5 - flare)) * math.cos(math.radians(a)), base - ry * 0.5 + ry * 0.8 * math.sin(math.radians(a))) for a in range(170, 0, -20)] + [(r1, base - ry * 0.5), (r0, top)]
    d = pd(body)
    out = [f'<path d="{d}" fill="{pal[1]}"/>', metal(D, d, l0, r0, pal, 0.9, 0.8)]
    for k in (0.22, 0.85):
        y = top + h * k
        out.append(f'<path d="M {l0 + (l1 - l0) * k:.1f} {y:.1f} Q {cx:.1f} {y + ry * 0.8:.1f} {r0 + (r1 - r0) * k:.1f} {y:.1f}" stroke="#6E7884" stroke-width="1.8" fill="none" opacity="0.6"/>')
    out.append(ink(d, INK, 1.7, seed, 1, 0.6))
    out.append(f'<path d="{ellipse_d(cx, top, w / 2 + 2, ry)}" fill="#E8ECF0"/>')
    return "".join(out), (cx, top, w / 2, ry)


@design("filter-kaapi")
def filter_kaapi():
    D = Doc2("in-fk")
    # red-oxide floor and a kolam drawn in rice flour; a brass lamp-glow
    out = [sky(D, [(0, "#B8442A"), (1, "#7A2414")], 1201, 600, ["#C85A3A", "#5A1408", "#D8704A"], 110, angle=-6, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 300, 360, "#FFB070", 0.28))
    # kolam: a grid of dots threaded by looping lines
    kol = []
    cxk, cyk = 300, 420
    pts = [(cxk + i * 34, cyk + j * 34) for i in range(-6, 7) for j in range(-6, 6) if abs(i) + abs(j) <= 7]
    for x, y in pts:
        kol.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFF6E8" opacity="0.6"/>')
    for i in range(-6, 7):
        for j in range(-6, 6):
            if abs(i) + abs(j) <= 6 and (i + j) % 2 == 0:
                x, y = cxk + i * 34 + 17, cyk + j * 34 + 17
                kol.append(f'<path d="M {x - 17} {y} Q {x} {y - 26} {x + 17} {y} Q {x} {y + 26} {x - 17} {y} Z" fill="none" stroke="#FFF6E8" stroke-width="2.4" opacity="0.4"/>')
    out.append("".join(kol))
    # the davara (wide bowl) with the tumbler standing in it
    dcx, drim = 300, 468
    out.append(cast(D, dcx + 14, drim + 72, 170, 20, strength=0.55, seed=1202))
    dav_fill = (f'<path d="{ellipse_d(dcx, drim + 3, 140, 30)}" fill="#C88A54"/>'
                f'<path d="{blob(dcx - 30, drim, 70, 12, 1203, 0.2, 12)}" fill="#E8C49A" opacity="0.8"/>')
    out.append(steel_bowl(D, dcx, drim, 152, 70, 1204, fill=dav_fill, ry=40))
    t_, (tx, ttop, trx, tr_y) = tumbler(D, dcx + 6, drim + 22, 116, 206, 1205)
    out.append(t_)
    # froth heaped above the rim, a drip running down
    foam = blob_pts(tx, ttop - 6, trx + 4, 22, 1206, 0.12, 18)
    out.append(painted(D, foam, ("#FFF8EC", "#F2DCC0", "#C8A07A"), 1206, sdir=(0.5, 0.8), sk=0.18, angle=-20, n=16, inkw=1.4, hi=0.5))
    rnd = random.Random(1207)
    for k in range(26):
        x, y = tx + rnd.uniform(-trx * 0.8, trx * 0.8), ttop - 6 + rnd.uniform(-12, 10)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.2, 3.2):.1f}" fill="none" stroke="#C8A07A" stroke-width="1" opacity="0.6"/>')
    out.append(taper([(tx + trx - 6, ttop + 6), (tx + trx - 4, ttop + 40), (tx + trx - 7, ttop + 62)], 7, 3, "#D8B08A", 0.95))
    out.append(steam(tx, ttop - 26, 56, 1208, "#FFFFFF", 3, 26, 7, 0.55))
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
    out.append(letters(D, 300, 140, "filter kaapi", SERIF_IT, 116, "#FFE6B8", ["#FFFFFF", "#F2C890", "#FFF2D8"], 1240, max_w=460,
                       shadow="#4A0E04", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 184, "DECOCTION FIRST, THEN THE WORLD", "#FFD8A8", font=JOS, size=18, ls=4, line_w=18, gap=10))
    return finish_b(D, out, 1241, "#2A0A04", 0.6)


# ================================================================ 13. it's not ice cream — the tub in the freezer is dal
def tub(D, cx, base, w, h, seed, body=("#FFFDF6", "#F4EAD6", "#C8B494"), band="#E8607A", scoop=True, tape=None, lid=True, open_=False):
    """A round ice-cream tub in 3/4 view; `tape` = a masking-tape label with a handwritten word."""
    ry = w * 0.2
    top = base - h
    l, r = cx - w / 2, cx + w / 2
    out = [cast(D, cx + 8, base + 4, w * 0.58, ry * 0.5, strength=0.4, seed=seed)]
    bl, br = cx - w * 0.44, cx + w * 0.44
    pts = [(l, top), (bl, base)] + [(cx + w * 0.44 * math.cos(math.radians(a)), base + ry * 0.85 * math.sin(math.radians(a))) for a in range(170, 0, -20)] + [(br, base), (r, top)]
    d = pd(pts)
    out.append(f'<path d="{d}" fill="{body[1]}"/>')
    out.append(metal(D, d, l, r, body, 0.5, 0.35))
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="M {l - 10:.1f} {base - h * 0.25:.1f} Q {cx:.1f} {base - h * 0.25 + ry:.1f} {r + 10:.1f} {base - h * 0.25:.1f} L {r + 10:.1f} {base - h * 0.12:.1f} Q {cx:.1f} {base - h * 0.12 + ry:.1f} {l - 10:.1f} {base - h * 0.12:.1f} Z" fill="{band}"/>']
    if scoop:
        sx, sy = cx - w * 0.2, top + h * 0.4
        inner.append(f'<path d="M {sx - 26:.1f} {sy + 8:.1f} L {sx:.1f} {sy + 52:.1f} L {sx + 26:.1f} {sy + 8:.1f} Z" fill="#E8A85A"/>')
        for k in range(4):
            inner.append(f'<path d="M {sx - 20 + k * 10:.1f} {sy + 10:.1f} l 8 14" stroke="#B8742A" stroke-width="1.4"/>')
        inner.append(f'<path d="{blob(sx, sy, 28, 20, seed, 0.15, 12)}" fill="#FFF0D8"/><path d="{blob(sx + 4, sy + 4, 22, 13, seed + 1, 0.15, 10)}" fill="#F2D8B0" opacity="0.6"/>')
        inner.append(f'<circle cx="{sx + 6:.1f}" cy="{sy - 20:.1f}" r="7" fill="#D6243A"/><path d="M {sx + 6:.1f} {sy - 26:.1f} q 4 -10 12 -12" stroke="#3E6A2A" stroke-width="1.6" fill="none"/>')
        inner.append(f'<text x="{cx + w * 0.16:.1f}" y="{top + h * 0.5:.1f}" text-anchor="middle" {SERIF_IT} font-size="{w * 0.12:.0f}" fill="{band}" transform="rotate(-6 {cx + w * 0.16:.1f} {top + h * 0.5:.1f})">Vanilla</text>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{d}" fill="{D.lin([(0, "#E8F4FA", 0.0), (0.8, "#E8F4FA", 0.0), (1, "#FFFFFF", 0.0)])}"/>')
    out.append(ink(d, INK, 1.7, seed, 1, 0.6))
    if tape:
        tw = w * 0.62
        out.append(f'<path d="{hg.org_rect(cx - tw / 2, top + h * 0.32, tw, h * 0.26, seed + 3, 0.6, 8, 1)}" fill="#F2E2B0" transform="rotate(-3 {cx} {top + h * 0.4})"/>')
        out.append(label(cx, top + h * 0.52, tape, MONO, int(h * 0.18), "#2A2A6A", max_w=tw - 10, extra=f' transform="rotate(-3 {cx} {top + h * 0.4})"'))
    if lid and not open_:
        lp = ellipse_d(cx, top, w / 2 + 4, ry)
        out.append(f'<path d="M {l - 4:.1f} {top:.1f} L {l - 4:.1f} {top - 12:.1f} L {r + 4:.1f} {top - 12:.1f} L {r + 4:.1f} {top:.1f} Z" fill="{band}"/>')
        out.append(f'<path d="{ellipse_d(cx, top - 12, w / 2 + 4, ry)}" fill="{lt(band, 0.25)}"/>')
        out.append(f'<path d="{ellipse_d(cx, top + 0, w / 2 + 4, ry)}" fill="none" stroke="{dk(band, 0.3)}" stroke-width="1.4" opacity="0.4"/>')
        out.append(ink(ellipse_d(cx, top - 12, w / 2 + 4, ry), INK, 1.4, seed + 4, 1, 0.5))
    return "".join(out), (cx, top, w / 2, ry)


def frost(seed, box, n=60):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(3, 7)
        out.append(f'<path d="M {x - r:.1f} {y:.1f} L {x + r:.1f} {y:.1f} M {x:.1f} {y - r:.1f} L {x:.1f} {y + r:.1f} M {x - r * 0.7:.1f} {y - r * 0.7:.1f} L {x + r * 0.7:.1f} {y + r * 0.7:.1f} M {x - r * 0.7:.1f} {y + r * 0.7:.1f} L {x + r * 0.7:.1f} {y - r * 0.7:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    return "".join(out)


@design("its-not-ice-cream")
def its_not_ice_cream():
    D = Doc2("in-ic")
    # the inside of the freezer: icy blue, frosted walls, a wire shelf
    out = [sky(D, [(0, "#DDEFF6"), (1, "#A8CCDC")], 1301, 600, ["#FFFFFF", "#8AB8CC", "#E8F6FA"], 120, angle=-86, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 40, 380, "#FFFFFF", 0.7))
    out.append(frost(1303, (20, 230, 580, 580), 50))
    shelf_y = 488
    out.append(f'<path d="M -10 {shelf_y} L 610 {shelf_y} L 610 610 L -10 610 Z" fill="#C8DEE8"/>')
    out.append(f'<path d="M -10 {shelf_y} L 610 {shelf_y} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FFFFFF", 0.6), (1, "#6A98AE", 0.3)])}"/>')
    for x in range(-40, 640, 26):
        out.append(f'<path d="M {300 + (x - 300) * 0.82:.1f} {shelf_y} L {x:.1f} 600" stroke="#8AA8B8" stroke-width="2.4" opacity="0.6"/>')
    out.append(f'<path d="M -10 {shelf_y} L 610 {shelf_y}" stroke="#E8F4FA" stroke-width="5"/>')
    # the stack at the back: re-used tubs with masking-tape labels
    t1, _ = tub(D, 116, 472, 142, 100, 1304, band="#5AA0D8", scoop=False, tape="RAJMA")
    t2, _ = tub(D, 116, 362, 130, 92, 1305, band="#7AC08A", scoop=False, tape="SAMBAR")
    t3, _ = tub(D, 484, 472, 150, 104, 1306, band="#F2A24A", scoop=False, tape="CHHOLE")
    out += [t1, t2, t3]
    # the hero tub, front and centre, lid off: dal
    t, (cx, top, rx, ry) = tub(D, 300, 540, 204, 146, 1307, band="#E8607A", open_=True)
    out.append(t)
    out.append(f'<path d="{ellipse_d(cx, top, rx + 3, ry + 1)}" fill="#E8ECEC"/>')
    out.append(f'<path d="{ellipse_d(cx, top + 2, rx - 4, ry - 4)}" fill="#E8A21E"/>')
    rnd = random.Random(1308)
    dal = [f'<path d="{blob(cx - 20, top - 2, rx * 0.6, ry * 0.4, 1309, 0.2, 12)}" fill="#F6C84A" opacity="0.8"/>']
    for k in range(40):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * rr * (rx - 6), top + 2 + math.sin(a) * rr * (ry - 6)
        c = rnd.choice(["#7A3A10", "#5A2A0A", "#C8281E", "#3E8A2A", "#FFE08A"])
        dal.append(f'<path d="{blob(x, y, rnd.uniform(1.4, 3.4), rnd.uniform(1, 2.2), rnd.randint(0, 999), 0.2, 6, rnd.uniform(0, 180))}" fill="{c}"/>')
    dal.append(frost(1310, (cx - rx, top - ry, cx + rx, top + ry), 10))
    out.append(clipped(D, ellipse_d(cx, top + 2, rx - 4, ry - 4), dal))
    out.append(ink(ellipse_d(cx, top, rx + 3, ry + 1), INK, 1.5, 1311, 1, 0.55))
    # its lid, propped against the tub
    lx, ly = 502, 548
    out.append(cast(D, lx + 6, ly + 8, 90, 12, strength=0.35, seed=1312))
    out.append(f'<path d="{ellipse_d(lx, ly + 6, 88, 18)}" fill="#C8485E"/><path d="{ellipse_d(lx, ly, 88, 18)}" fill="#F27A90"/>'
               f'<path d="{ellipse_d(lx, ly - 2, 76, 13)}" fill="#E8607A"/>{ink(ellipse_d(lx, ly, 88, 18), INK, 1.5, 1313, 1, 0.55)}')
    for x, y, r in ((cx - 70, top - 30, 9), (cx + 64, top - 40, 11), (cx + 6, top - 56, 7)):
        out.append(sparkle(x, y, r, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 126, "It's not ice cream", SERIF_IT, 76, "#1E4A7A", ["#2E6AA8", "#0E2A4A", "#4A8AC8"], 1320, max_w=470,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8E0F8"))
    out.append(sub(300, 172, "IT'S DAL. IT'S ALWAYS DAL.", "#C8304A", font=JOS, size=22, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 1321, "#2A4A6A", 0.5)


# ================================================================ 14. thoda adjust karo — the suitcase going home to India
def gift_box(D, x, y, w, h, col, seed, ribbon="#F6C21C", ang=0, pattern=None):
    pts = rot(poly_pts([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 8, seed, 0.4), x + w / 2, y + h / 2, ang)
    out = [painted(D, pts, col, seed, sdir=(0.5, 0.8), sk=0.15, angle=ang, n=8, inkw=1.4, hi=0.35)]
    rib = rot([(x + w * 0.46, y), (x + w * 0.56, y), (x + w * 0.56, y + h), (x + w * 0.46, y + h)], x + w / 2, y + h / 2, ang)
    out.append(f'<path d="{pd(rib)}" fill="{ribbon}"/>')
    if pattern == "dots":
        rnd = random.Random(seed)
        out.append(clipped(D, smooth_closed(pts), [f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, h):.1f}" r="2.4" fill="#FFFFFF" opacity="0.7"/>' for _ in range(int(w * h / 90))]))
    return "".join(out)


@design("thoda-adjust-karo")
def thoda_adjust_karo():
    D = Doc2("in-ta")
    # a block-printed bedspread behind (the packing always happens on the bed)
    out = [f'<rect width="600" height="600" fill="#F4E6CC"/>']
    pat = []
    for j in range(-1, 9):
        for i in range(-1, 9):
            x, y = i * 74 + (37 if j % 2 else 0), j * 74
            for k in range(8):
                a = math.radians(k * 45)
                pat.append(f'<path d="{blob(x + math.cos(a) * 11, y + math.sin(a) * 11, 7, 4, k + i * 9, 0.2, 8, k * 45)}" fill="#C8463A" opacity="0.45"/>')
            pat.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#2A3A6A" opacity="0.5"/>')
            pat.append(f'<path d="{blob(x + 37, y + 37, 6, 3, j * 7 + i, 0.2, 8, 45)}" fill="#3E6A3A" opacity="0.4"/>')
    out.append("".join(pat))
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#FFFFFF", "#8A5A3A"], 1402, n=90, angle=-8, length=(60, 160), width=(3, 9), opacity=(0.05, 0.12)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF8E8", 0.55), (1, "#FFF8E8", 0)], 0.45, 0.55, 0.6)}"/>')
    # the suitcase, upright and bulging, a sleeve and a ribbon squeezing out of the zip
    x0, x1, y0, y1 = 120, 392, 292, 522
    cx = (x0 + x1) / 2
    out.append(cast(D, cx + 20, y1 + 6, 170, 14, strength=0.5, seed=1404))
    body = []
    for k in range(48):
        t = k / 48 * 2 * math.pi
        cs, sn = math.cos(t), math.sin(t)
        px = cx + (x1 - x0) / 2 * (abs(cs) ** 0.3) * (1 if cs >= 0 else -1) * (1 + 0.03 * (1 - abs(sn)))
        py = (y0 + y1) / 2 + (y1 - y0) / 2 * (abs(sn) ** 0.3) * (1 if sn >= 0 else -1)
        body.append((px, py))
    out.append(painted(D, body, ("#4A9AD8", "#1E64B0", "#0E2E62"), 1405, sdir=(0.7, 0.4), sk=0.14, angle=-90, n=40, inkw=2.2, hi=0.4, hik=0.06))
    rid = [f'<path d="M {x:.1f} {y0 + 10} Q {x + (x - cx) * 0.06:.1f} {(y0 + y1) / 2:.1f} {x:.1f} {y1 - 10}" stroke="{c}" stroke-width="{w}" fill="none" opacity="{o}"/>'
           for x in (cx - 90, cx - 30, cx + 30, cx + 90) for c, w, o in (("#0E2E62", 5, 0.35), ("#8AC0F0", 2, 0.5))]
    out.append(clipped(D, smooth_closed(body), rid))
    out.append(ink(smooth_closed([(x * 0.94 + cx * 0.06, y * 0.95 + (y0 + y1) / 2 * 0.05) for x, y in body]), "#0A1E44", 1.6, 1406, 1, 0.55))
    # corners and wheels
    for wx in (x0 + 26, x1 - 26):
        out.append(f'<path d="{hg.org_rect(wx - 16, y1 - 8, 32, 14, wx, 0.3, 6, 4)}" fill="#1A1A22"/><circle cx="{wx}" cy="{y1 + 10}" r="10" fill="#2A2A32"/><circle cx="{wx}" cy="{y1 + 10}" r="4" fill="#8A8A94"/>')
    # things escaping the zip on the right edge: a red sleeve, a gift ribbon, a teddy's ear; a box corner on the left
    out.append(painted(D, [(x1 - 4, 380), (x1 + 34, 396), (x1 + 50, 440), (x1 + 40, 482), (x1 + 20, 480), (x1 + 26, 444), (x1 + 6, 418), (x1 - 6, 404)],
                       ("#F28A8A", "#D8404A", "#8A1424"), 1407, sdir=(0.6, 0.4), sk=0.2, angle=-80, n=14, inkw=1.6, hi=0.35))
    for k in range(4):
        out.append(f'<path d="M {x1 + 20 + k * 1} {466 + k * 4} l 22 -1" stroke="#8A1424" stroke-width="2" opacity="0.6"/>')
    out.append(taper([(x1 - 2, 340), (x1 + 20, 336), (x1 + 34, 354), (x1 + 28, 370)], 7, 3, "#F6C21C", 0.95))
    out.append(painted(D, blob_pts(x1 + 2, 316, 13, 11, 1408, 0.1, 10), ("#E8B880", "#B8783A", "#6A3E14"), 1408, sk=0.2, n=4, inkw=1.3, hi=0.35))
    out.append(f'<path d="{blob(x1 + 4, 316, 6, 5, 1409, 0.1, 8)}" fill="#F4DAB0"/>')
    out.append(painted(D, poly_pts([(x0 - 20, 410), (x0 + 6, 396), (x0 + 10, 440), (x0 - 16, 446)], 6, 1410, 0.3), ("#FFE48A", "#E8B020", "#8A6A06"), 1410, sk=0.2, n=4, inkw=1.3, hi=0.4))
    out.append(f'<path d="M {x0 - 18} 426 L {x0 + 8} 418" stroke="#D6246E" stroke-width="4"/>')
    # two luggage belts pulled tight, with buckles
    for k, y in enumerate((362, 456)):
        belt = [(x0 - 6, y + 4), (cx, y - 6), (x1 + 6, y + 4)]
        out.append(taper(belt, 20, 20, ["#E8346E", "#F2901E"][k]))
        out.append(taper([(px, py - 6) for px, py in belt], 3, 3, "#FFFFFF", 0.35))
        bx = cx - 20 + k * 30
        out.append(f'<path d="{hg.org_rect(bx - 16, y - 18, 32, 26, bx, 0.3, 6, 3)}" fill="none" stroke="#2A2A32" stroke-width="5"/>')
        out.append(f'<path d="M {bx} {y - 18} L {bx} {y + 8}" stroke="#2A2A32" stroke-width="3"/>')
    # carry handle with an identifying red ribbon, and the luggage scale clipped on it reading 23.0
    out.append(f'<path d="M {cx - 34} {y0 + 6} q 34 -34 68 0" stroke="#1A1A22" stroke-width="10" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{smooth_closed([(cx + 24, y0 - 10), (cx + 46, y0 - 26), (cx + 40, y0 - 4)])}" fill="#D6342A"/>')
    out.append(f'<path d="{smooth_closed([(cx + 24, y0 - 10), (cx + 30, y0 + 22), (cx + 40, y0 + 18)])}" fill="#B8241A"/>')
    hx, hy = cx, y0 - 22
    out.append(pline([(hx, y0 - 12), (hx, hy - 6)], "#1A1A22", 4, 1417, 1, 1))
    sc = poly_pts([(hx - 54, hy - 74), (hx + 54, hy - 74), (hx + 54, hy - 6), (hx - 54, hy - 6)], 8, 1418, 0.3)
    out.append(painted(D, sc, ("#5A5E68", "#2E323A", "#121418"), 1418, sk=0.15, n=8, inkw=1.6, hi=0.3))
    out.append(f'<path d="{hg.org_rect(hx - 42, hy - 64, 84, 42, 1420, 0.3, 8, 3)}" fill="#BCE0A0"/>')
    out.append(f'<text x="{hx}" y="{hy - 31}" text-anchor="middle" {MONO} font-size="31" fill="#1E3A1E">23.0</text>')
    out.append(f'<circle cx="{hx + 46}" cy="{hy - 14}" r="3.4" fill="#E8302A"/>')
    # the cardboard box tied with blue nylon rope, the other half of every trip
    bx0, by0 = 404, 408
    out.append(cast(D, 488, 532, 96, 10, strength=0.5, seed=1421))
    front = poly_pts([(bx0, by0 + 22), (bx0 + 126, by0 + 22), (bx0 + 126, 528), (bx0, 528)], 8, 1422, 0.4)
    side = poly_pts([(bx0 + 126, by0 + 22), (bx0 + 158, by0), (bx0 + 158, 508), (bx0 + 126, 528)], 8, 1423, 0.4)
    topf = poly_pts([(bx0, by0 + 22), (bx0 + 32, by0), (bx0 + 158, by0), (bx0 + 126, by0 + 22)], 8, 1424, 0.4)
    out.append(painted(D, front, ("#E2B47A", "#C08A50", "#7A5230"), 1422, sk=0.12, angle=0, n=12, inkw=1.6, hi=0.3))
    out.append(painted(D, side, ("#C8965A", "#9A6A3A", "#5A3A1A"), 1423, sk=0.12, angle=-90, n=8, inkw=1.6, hi=0.2))
    out.append(painted(D, topf, ("#F2CC92", "#D8A868", "#8A6A3A"), 1424, sk=0.1, angle=0, n=8, inkw=1.4, hi=0.3))
    out.append(f'<path d="M {bx0 + 16} {by0 + 11} L {bx0 + 142} {by0 + 11}" stroke="#C8A070" stroke-width="5" opacity="0.8"/>')
    for pts_ in ([(bx0 + 62, by0 + 22), (bx0 + 62, 528)], [(bx0, 470), (bx0 + 126, 470), (bx0 + 158, 450)], [(bx0 + 62, by0 + 22), (bx0 + 94, by0)], [(bx0 + 16, by0 + 11), (bx0 + 142, by0 + 11)]):
        out.append(pline(pts_, "#1E6AC8", 4, 1425, 1, 1))
    out.append(f'<path d="M {bx0 + 30} 510 L {bx0 + 30} 482 M {bx0 + 22} 492 L {bx0 + 30} 482 L {bx0 + 38} 492 M {bx0 + 96} 510 L {bx0 + 96} 482 M {bx0 + 88} 492 L {bx0 + 96} 482 L {bx0 + 104} 492" stroke="#2A2A3A" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    out.append(label(bx0 + 63, by0 + 56, "FRAGILE", JOS, 19, "#C8201E", ls=2, max_w=118))
    # lettering
    out.append(letters(D, 300, 104, "Thoda adjust karo", SERIF_IT, 72, "#1E3A7A", ["#2E5AA8", "#0E1E4A", "#4A7AC8"], 1430, max_w=470,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8D8F8"))
    out.append(sub(300, 146, "23 KILOS, NOT ONE GRAM MORE", "#8A1E2A", font=JOS, size=19, ls=4, line_w=20, gap=12))
    return finish_b(D, out, 1431)


# ================================================================ 15. jugaad — the remote: wrapped in plastic, held with a rubber band
@design("jugaad")
def jugaad():
    D = Doc2("in-jg")
    # a crochet doily on a dark wooden side table, a warm lamp glow
    out = [wood_planks(D, 0, 600, 1501, ("#B07A4A", "#7A4A26", "#3E2210"), 4)]
    out.append(soft_glow(D, 120, 140, 400, "#FFD890", 0.35))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#000000", 0), (1, "#000000", 0.25)], 0, 0, 1, 1)}"/>')
    # doily: rings of crochet loops
    cx, cy = 300, 390
    out.append(cast(D, cx + 10, cy + 12, 250, 180, strength=0.3, seed=1502))
    for k, rr in enumerate((228, 196, 160, 120, 80, 40)):
        n = int(rr / 7)
        loops = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.72
            loops.append(f'<path d="{blob(x, y, 11 if k == 0 else 8, 8 if k == 0 else 6, i + k * 50, 0.1, 8, math.degrees(a))}" fill="none" stroke="#FFFBF0" stroke-width="2.6"/>')
        out.append(f'<path d="{ellipse_d(cx, cy, rr - 6, (rr - 6) * 0.72)}" fill="#FFF8EA" opacity="{0.35 if k % 2 else 0.6}"/>')
        out.append("".join(loops))
    for i in range(24):
        a = 2 * math.pi * i / 24
        out.append(f'<path d="M {cx + math.cos(a) * 44:.1f} {cy + math.sin(a) * 32:.1f} L {cx + math.cos(a) * 190:.1f} {cy + math.sin(a) * 137:.1f}" stroke="#FFFBF0" stroke-width="2" opacity="0.55"/>')
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
    # lettering
    out.append(letters(D, 300, 140, "Jugaad", SERIF_IT, 150, "#FFD27A", ["#FFE6A0", "#F2A83A", "#FFF2C8"], 1520, max_w=380,
                       shadow="#1A0A04", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 186, "ONE RUBBER BAND FROM FIXED", "#FFE6C8", font=JOS, size=19, ls=5, line_w=20, gap=12))
    return finish_b(D, out, 1521, "#1A0A04", 0.6)


# ================================================================ 16. kai po che! — Uttarayan, kites over the rooftops
def kite(D, cx, cy, s, ang, seed, cols=("#D6246E", "#F6C21C"), tail=True, split="diag"):
    """Patang: a square kite flown on its point, two-tone paper, a bamboo spine and bow, a little tail."""
    pts = [(cx, cy - s), (cx + s * 0.92, cy), (cx, cy + s), (cx - s * 0.92, cy)]
    P_ = rot(pts, cx, cy, ang)
    out = [f'<path d="{pd(P_)}" fill="{cols[0]}"/>']
    if split == "diag":
        half = rot([(cx, cy - s), (cx + s * 0.92, cy), (cx, cy + s)], cx, cy, ang)
        out.append(f'<path d="{pd(half)}" fill="{cols[1]}"/>')
    else:
        top = rot([(cx - s * 0.46, cy - s * 0.5), (cx, cy - s), (cx + s * 0.46, cy - s * 0.5)], cx, cy, ang)
        out.append(f'<path d="{pd(top)}" fill="{cols[1]}"/>')
        mid = rot([(cx, cy - s * 0.3), (cx + s * 0.28, cy), (cx, cy + s * 0.3), (cx - s * 0.28, cy)], cx, cy, ang)
        out.append(f'<path d="{pd(mid)}" fill="{cols[1]}"/>')
    out.append(f'<path d="{pd(P_)}" fill="{D.lin([(0, "#FFFFFF", 0.35), (0.5, "#FFFFFF", 0), (1, "#000000", 0.2)])}"/>')
    spine = rot([(cx, cy - s), (cx, cy + s)], cx, cy, ang)
    bow = rot([(cx - s * 0.92, cy), (cx, cy - s * 0.4), (cx + s * 0.92, cy)], cx, cy, ang)
    out.append(ink(pd(spine, False), "#8A6A3A", max(1.2, s * 0.04), seed, 1, 0.9))
    out.append(ink(smooth_open(bow), "#8A6A3A", max(1.2, s * 0.04), seed + 1, 1, 0.9))
    out.append(ink(pd(P_), INK, max(1, s * 0.035), seed + 2, 1, 0.6))
    if tail:
        b = P_[2]
        tl = rot([(cx, cy + s), (cx - s * 0.12, cy + s * 1.3), (cx + s * 0.08, cy + s * 1.5)], cx, cy, ang)
        out.append(f'<path d="{smooth_closed([b, tl[1], tl[2], (b[0] + 2, b[1])])}" fill="{cols[1]}"/>')
    return "".join(out)


def rooftop_row(D, base, seed, n, hmin, hmax, haze, pal_cols):
    rnd = random.Random(seed)
    out = []
    x = -20
    while x < 620:
        w = rnd.uniform(60, 110)
        h = rnd.uniform(hmin, hmax)
        c = mix(rnd.choice(pal_cols), "#E8D8E8", haze)
        out.append(f'<path d="{hg.org_rect(x, base - h, w, h + 200, rnd.randint(0, 999), 0.5, 12, 1)}" fill="{c}"/>')
        out.append(f'<path d="{hg.org_rect(x - 2, base - h - 6, w + 4, 8, rnd.randint(0, 999), 0.4, 12, 1)}" fill="{mix(dk(c, 0.15), "#E8D8E8", haze * 0.5)}"/>')
        if rnd.random() < 0.5:
            tx = x + rnd.uniform(10, w - 30)
            out.append(f'<path d="{hg.org_rect(tx, base - h - 26, 22, 22, rnd.randint(0, 999), 0.4, 8, 3)}" fill="{mix("#2A2A30", "#E8D8E8", haze)}"/>')
        for k in range(rnd.randint(1, 3)):
            wx = x + 10 + k * 26
            if wx + 12 < x + w:
                out.append(f'<rect x="{wx:.1f}" y="{base - h + 16:.1f}" width="12" height="16" fill="{mix("#5A6A8A", "#E8D8E8", haze)}"/>')
        x += w - 2
    return "".join(out)


@design("kai-po-che")
def kai_po_che():
    D = Doc2("in-kp")
    out = [sky(D, [(0, "#6AB8E8"), (0.65, "#BCE4F4"), (1, "#FFF2D8")], 1601, 600, ["#FFFFFF", "#8AC8F0"], 80, angle=-4, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 120, 200, "#FFFFFF", 0.6))
    # many far kites, small and pale
    rnd = random.Random(1602)
    pal = [("#D6246E", "#F6C21C"), ("#2A3A90", "#F2901E"), ("#3E8A3A", "#FFFFFF"), ("#F2901E", "#D6342A"), ("#12808A", "#F6C21C"), ("#FFFFFF", "#D6246E")]
    for k in range(18):
        x, y = rnd.uniform(40, 560), rnd.uniform(220, 400)
        s = rnd.uniform(7, 13)
        c = pal[k % len(pal)]
        out.append(f'<g opacity="0.75">{kite(D, x, y, s, rnd.uniform(-20, 20), 1603 + k, (mix(c[0], "#BCE4F4", 0.35), mix(c[1], "#BCE4F4", 0.35)), tail=False)}</g>')
    # rooftops: far (hazy), near
    out.append(rooftop_row(D, 452, 1610, 8, 30, 80, 0.55, ["#E8B88A", "#F2D8A8", "#D8A8A0", "#C8D0D8"]))
    out.append(rooftop_row(D, 506, 1611, 8, 20, 60, 0.12, ["#E8986A", "#F2C88A", "#D88A8A", "#B8C8D0", "#F4E0C0"]))
    # a kite flyer on the next roof, a friend beside him holding the spool
    out.append(figures.person(462, 448, 52, "point", -1, {"top": "#F6C21C", "top_kind": "tee", "bottom": "#2A3A6A", "form": "m", "hair_style": "short", "hat_kind": None}, seed=1640, light=-1))
    out.append(figures.person(500, 448, 44, "stand_34", -1, {"top": "#D6246E", "top_kind": "long", "bottom": "#F2E6D0", "form": "f", "hair_style": "ponytail", "hat_kind": None}, seed=1641, light=-1))
    out.append(f'<path d="{hg.org_rect(418, 446, 120, 8, 1642, 0.4, 10, 1)}" fill="#C8A888"/>')
    # the near parapet with a big firki (spool) of manja resting on it
    out.append(f'<path d="{hg.org_rect(-10, 512, 620, 110, 1612, 0.6, 14, 1)}" fill="#F2E0C8"/>')
    out.append(strokes(D.nid(), hg.org_rect(-10, 512, 620, 110, 1612, 0.6, 14, 1), (-10, 512, 610, 620), ["#FFFFFF", "#C8A888"], 1613, n=50, angle=0, length=(30, 100), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(f'<path d="M -10 512 L 610 512" stroke="#C8A888" stroke-width="5"/>')
    fx, fy = 124, 490
    out.append(cast(D, fx + 8, fy + 34, 74, 10, strength=0.45, seed=1614))
    out.append(f'<path d="M {fx - 64} {fy + 26} L {fx + 64} {fy + 26}" stroke="#6A4A2A" stroke-width="9" stroke-linecap="round"/>')
    out.append(f'<path d="{ellipse_d(fx, fy, 44, 40)}" fill="#D6342A"/>')
    for k in range(9):
        out.append(f'<path d="{ellipse_d(fx, fy, 40 - k * 3, 36 - k * 3)}" fill="none" stroke="{["#FF9AB8", "#F6C21C", "#FFFFFF"][k % 3]}" stroke-width="2.2" opacity="0.85"/>')
    out.append(f'<path d="{ellipse_d(fx, fy, 44, 40)}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, "#000000", 0.3)], 0, 0, 1, 1)}"/>')
    out.append(ink(ellipse_d(fx, fy, 44, 40), INK, 1.6, 1615, 1, 0.6))
    out.append(f'<path d="M {fx - 70} {fy} L {fx + 70} {fy}" stroke="#A8804A" stroke-width="8" stroke-linecap="round"/>')
    out.append(f'<path d="M {fx - 70} {fy - 2} L {fx + 70} {fy - 2}" stroke="#E8C88A" stroke-width="2.4" stroke-linecap="round"/>')
    # spare kites stacked against the parapet, ready for the next round
    for k, (x, y, a_, c) in enumerate(((506, 478, -12, ("#3E8A3A", "#FFFFFF")), (530, 486, 8, ("#F2901E", "#D6342A")), (488, 490, 18, ("#12808A", "#F6C21C")))):
        out.append(kite(D, x, y, 34, a_, 1650 + k, c, tail=False))
    # the dogfight: the pink kite sails on, the blue one has just been cut and tumbles away
    k1 = (372, 286)
    out.append(pline([(448, 408), (420, 350), k1], "#D6246E", 1.6, 1616, 0.85, 1))
    out.append(kite(D, k1[0], k1[1], 56, 8, 1617, ("#D6246E", "#F6C21C")))
    k2 = (170, 330)
    out.append(kite(D, k2[0], k2[1], 46, -52, 1618, ("#2A3A90", "#F2901E"), split="band"))
    out.append(pline([(k2[0] + 20, k2[1] + 26), (214, 370), (190, 404), (222, 440), (206, 470)], "#2A3A90", 1.4, 1619, 0.7, 1))
    for a in (-40, -10, 20):
        rr = math.radians(a)
        out.append(taper([(k2[0] + 54 + math.cos(rr) * 10, k2[1] - 30 + math.sin(rr) * 26), (k2[0] + 76 + math.cos(rr) * 18, k2[1] - 40 + math.sin(rr) * 34)], 3, 1, "#2A3A90", 0.6))
    # birds
    for x, y, s in ((96, 210, 9), (122, 196, 7), (520, 230, 8)):
        out.append(bird_v(x, y, s, "#3A3048", 0.8))
    # lettering
    out.append(letters(D, 300, 132, "Kai po che!", SERIF_IT, 116, "#B8183A", ["#D8304A", "#7A0A1A", "#F05A6A"], 1630, max_w=450,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB0B8"))
    out.append(sub(300, 176, "UTTARAYAN · KITES ON EVERY ROOF", "#1E3A6A", font=JOS, size=18, ls=4, line_w=18, gap=10))
    return finish_b(D, out, 1631)


# ================================================================ 17. ekdum filmy — a hand-painted cinema hoarding
def block_letters(D, x, y, s, font, size, fill, side, outline, depth=10, max_w=470, ls=0, rot_=0):
    """Hoarding lettering: a stacked extrusion in `side`, a thick `outline`, then the face with a painted gradient."""
    fs = fit_size(s, font, size, max_w, ls)
    t = f'<text x="{x}" y="{y}" text-anchor="middle" {font} font-size="{fs}" letter-spacing="{ls}">{esc(s)}</text>'
    out = [f'<g transform="rotate({rot_} {x} {y})">']
    for k in range(depth, 0, -1):
        out.append(f'<g transform="translate({k * 0.6:.1f} {k:.1f})" fill="{side}" stroke="{side}" stroke-width="{fs * 0.06:.1f}" stroke-linejoin="round">{t}</g>')
    out.append(f'<g fill="{outline}" stroke="{outline}" stroke-width="{fs * 0.12:.1f}" stroke-linejoin="round">{t}</g>')
    g = D.lin([(0, lt(fill, 0.5), 1), (0.5, fill, 1), (1, dk(fill, 0.25), 1)])
    out.append(f'<g fill="{g}">{t}</g>')
    out.append("</g>")
    return "".join(out), fs


@design("ekdum-filmy")
def ekdum_filmy():
    D = Doc2("in-ef")
    out = [f'<rect width="600" height="600" fill="#2A0E3A"/>']
    out.append(sunburst(300, 330, 28, "#E8246E", "#C81A5E"))
    out.append(soft_glow(D, 300, 330, 300, "#FFD06A", 0.45))
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#FFFFFF", "#6A0A3A"], 1701, n=90, angle=-70, length=(40, 140), width=(3, 9), opacity=(0.05, 0.12)))
    # marquee border of bulbs
    rnd = random.Random(1702)
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
        on = rnd.random() < 0.8
        if on:
            out.append(soft_glow(D, x, y, 16, "#FFE27A", 0.6))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.4" fill="{"#FFF6C8" if on else "#8A6A3A"}" stroke="#5A3A10" stroke-width="1.2"/>')
    # stars and sparkles
    for x, y, r in ((120, 250, 14), (486, 230, 16), (90, 420, 9), (520, 420, 11), (300, 470, 8)):
        out.append(f'<polygon points="{hg.star_pts(x, y, r, r * 0.45) if hasattr(hg, "star_pts") else ""}" fill="#FFE27A"/>' if False else sparkle(x, y, r, "#FFF2B0", 0.95))
    # hero lettering, stacked on a tilt
    a, _ = block_letters(D, 300, 226, "EKDUM", ANTON, 128, "#FFE27A", "#8A1A0A", "#2A0A1A", depth=12, max_w=420, ls=4, rot_=-6)
    b, _ = block_letters(D, 300, 360, "FILMY!", ANTON, 150, "#FF8A3A", "#6A0A1A", "#2A0A1A", depth=14, max_w=440, ls=4, rot_=-6)
    out += [a, b]
    # ribbon banner and a ticket stub
    rb = [(110, 410), (490, 390), (500, 444), (120, 464)]
    out.append(painted(D, poly_pts(rb, 10, 1703, 0.5), ("#FFFFFF", "#F4EAD6", "#C8B494"), 1703, sk=0.12, angle=-3, n=14, inkw=1.6, hi=0.3))
    for side in (-1, 1):
        ex, ey = (110, 437) if side < 0 else (495, 417)
        out.append(f'<path d="{pd([(ex, ey - 22), (ex + side * 46, ey - 26), (ex + side * 34, ey), (ex + side * 46, ey + 24), (ex, ey + 22)])}" fill="#C8B494"/>')
    out.append(label(305, 437, "3 HOURS · WITH INTERVAL", JOS, 19, "#6A0A2A", ls=3, max_w=360, extra=' transform="rotate(-3 305 430)"'))
    tk = rot(poly_pts([(330, 476), (500, 476), (500, 536), (330, 536)], 8, 1704, 0.3), 415, 506, 8)
    out.append(cast(D, 420, 540, 90, 10, strength=0.4, seed=1705))
    out.append(painted(D, tk, ("#FFF4A0", "#F6D83A", "#A89A0A"), 1704, sk=0.1, n=8, inkw=1.4, hi=0.3))
    out.append(f'<path d="M 372 478 L 366 536" stroke="#A89A0A" stroke-width="2" stroke-dasharray="4 4" transform="rotate(8 415 506)"/>')
    out.append(label(436, 504, "BALCONY", JOS, 18, "#6A0A2A", ls=3, max_w=110, extra=' transform="rotate(8 436 498)"'))
    out.append(label(436, 528, "ROW F · 14", MONO, 16, "#6A0A2A", max_w=140, extra=' transform="rotate(8 436 518)"'))
    # a paper cone of roasted peanuts
    px, py = 166, 500
    cone = [(px - 46, py - 36), (px + 46, py - 36), (px + 6, py + 50), (px - 4, py + 50)]
    rnd2 = random.Random(1706)
    for k in range(10):
        out.append(painted(D, blob_pts(px + rnd2.uniform(-36, 36), py - 40 + rnd2.uniform(-10, 4), 8, 5, 1707 + k, 0.1, 10, rot=rnd2.uniform(0, 180)), ("#F2C88A", "#C8904A", "#7A4A1A"), 1707 + k, sk=0.2, n=2, inkw=0.9, hi=0.4))
    out.append(painted(D, poly_pts(cone, 8, 1720, 0.4), ("#F4ECE0", "#E2D4C0", "#9A8A70"), 1720, sk=0.2, angle=-80, n=10, inkw=1.4, hi=0.3))
    for k in range(5):
        out.append(f'<path d="M {px - 36 + k * 9} {py - 26 + k * 8} l {50 - k * 9} 0" stroke="#6A6A70" stroke-width="1.4" opacity="0.5"/>')
    out.append(sub(300, 84, "NOW SHOWING · HOUSE FULL", "#FFE27A", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 1721, "#FFFFFF", 0.4)


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
        for y in (360, 470):
            out.append(f'<path d="{hg.org_rect(x - 50, y - 40, 100, 80, x + y, 0.5, 10, 3)}" fill="none" stroke="#2A8A90" stroke-width="3"/>')
            out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{BRASS[1]}" stroke="{INK}" stroke-width="1.2"/><circle cx="{x - 3}" cy="{y - 3}" r="3" fill="#FFF0C0"/>')
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
    out.append(letters(D, 300, 132, "Nazar na lage", SERIF_IT, 94, "#FFF2D8", ["#FFFFFF", "#F2D8A8", "#FFF6E8"], 1830, max_w=450,
                       shadow="#12245A", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 178, "NO EVIL EYE ON THIS HOME", "#FFE08A", font=JOS, size=20, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 1831, "#0A1A3A", 0.5)


# ================================================================ 19. taj mahal — Agra at first light, across the long pool
def onion_dome(cx, base_y, w, h, neck=0.8):
    """Onion dome outline points: from the drum (width w*neck) swelling to w, closing to a pointed tip."""
    pts = []
    for i in range(25):
        t = i / 24
        y = base_y - h * t
        if t < 0.08:
            r = w / 2 * (neck + (1 - neck) * t / 0.08 * 0.5)
        elif t < 0.45:
            u = (t - 0.08) / 0.37
            r = w / 2 * (neck + (1 - neck) * 0.5 + (1 - neck) * 0.5 * math.sin(u * math.pi / 2))
        else:
            u = (t - 0.45) / 0.55
            r = w / 2 * math.cos(u * math.pi / 2) ** 0.85 * (1 - 0.25 * u)
        pts.append((r, y))
    right = [(cx + r, y) for r, y in pts]
    left = [(cx - r, y) for r, y in pts[::-1]]
    return right + left[1:]


def arch_pts(cx, base, w, h, n=10):
    """A pointed (Mughal) arch opening: straight sides then two arcs meeting at a point."""
    sp = base - h * 0.62
    pts = [(cx - w / 2, base), (cx - w / 2, sp)]
    for i in range(1, n + 1):
        t = i / n
        pts.append((cx - w / 2 + w / 2 * math.sin(t * math.pi / 2) ** 1.2, sp - (h * 0.38) * (1 - math.cos(t * math.pi / 2))))
    for i in range(n - 1, 0, -1):
        t = i / n
        pts.append((cx + w / 2 - w / 2 * math.sin(t * math.pi / 2) ** 1.2, sp - (h * 0.38) * (1 - math.cos(t * math.pi / 2))))
    pts += [(cx + w / 2, sp), (cx + w / 2, base)]
    return pts


def taj(D, cx, plinth_y, s, seed, lit="#FFF0E8", mid="#F2DCD8", shade="#C8B4CC", line="#9A86A8", haze=0.0):
    """The Taj Mahal, front elevation: plinth, chamfered main hall with the great iwan, drum and onion dome,
    four chhatris, four minarets. s = scale (1 = 190 px wide hall)."""
    hz = (lambda c: mix(c, "#F6E0E0", haze)) if haze else (lambda c: c)
    L, M, S, N = hz(lit), hz(mid), hz(shade), hz(line)
    out = []

    def X(v):
        return cx + v * s

    def Y(v):
        return plinth_y - v * s

    # minarets (behind the plinth front)
    for side in (-1, 1):
        mx = X(side * 196)
        pts = [(mx - 9 * s, Y(0)), (mx - 7 * s, Y(170)), (mx + 7 * s, Y(170)), (mx + 9 * s, Y(0))]
        out.append(f'<path d="{pd(pts)}" fill="{M}"/>')
        out.append(f'<path d="{pd([(mx + 1 * s, Y(0)), (mx + 1 * s, Y(170)), (mx + 7 * s, Y(170)), (mx + 9 * s, Y(0))])}" fill="{S}" opacity="0.7"/>')
        for b in (52, 104, 152):
            out.append(f'<path d="{pd([(mx - 13 * s, Y(b)), (mx + 13 * s, Y(b)), (mx + 11 * s, Y(b - 4)), (mx - 11 * s, Y(b - 4))])}" fill="{L}" stroke="{N}" stroke-width="0.8"/>')
        out.append(f'<path d="{pd([(mx - 10 * s, Y(170)), (mx + 10 * s, Y(170)), (mx + 10 * s, Y(176)), (mx - 10 * s, Y(176))])}" fill="{L}"/>')
        for k in (-7, 0, 7):
            out.append(f'<path d="M {mx + k * s:.1f} {Y(176):.1f} L {mx + k * s:.1f} {Y(186):.1f}" stroke="{M}" stroke-width="{1.4 * s:.1f}"/>')
        out.append(f'<path d="{smooth_closed(onion_dome(mx, Y(186), 22 * s, 18 * s, 0.9))}" fill="{L}"/>')
        out.append(f'<path d="M {mx:.1f} {Y(204):.1f} L {mx:.1f} {Y(212):.1f}" stroke="{N}" stroke-width="1.2"/>')
    # plinth
    out.append(f'<path d="{pd([(X(-214), Y(0)), (X(214), Y(0)), (X(214), Y(-16)), (X(-214), Y(-16))])}" fill="{M}"/>')
    out.append(f'<path d="{pd([(X(-214), Y(-10)), (X(214), Y(-10)), (X(214), Y(-16)), (X(-214), Y(-16))])}" fill="{S}" opacity="0.6"/>')
    for k in range(-13, 14):
        out.append(f'<path d="{smooth_closed(arch_pts(X(k * 16), Y(-14), 9 * s, 10 * s, 4))}" fill="{S}" opacity="0.6"/>')
    # main hall: centre block with chamfered corners
    hall = [(X(-96), Y(0)), (X(-96), Y(96)), (X(96), Y(96)), (X(96), Y(0))]
    out.append(f'<path d="{pd(hall)}" fill="{L}"/>')
    for side in (-1, 1):
        out.append(f'<path d="{pd([(X(side * 96), Y(0)), (X(side * 96), Y(96)), (X(side * 80), Y(96)), (X(side * 80), Y(0))])}" fill="{S if side > 0 else M}" opacity="0.8"/>')
        # two storeys of small arches on each wing
        for st in (0, 1):
            ax = X(side * 52)
            out.append(f'<path d="{smooth_closed(arch_pts(ax, Y(6 + st * 44), 22 * s, 36 * s))}" fill="{S}"/>')
            out.append(f'<path d="{smooth_closed(arch_pts(ax, Y(6 + st * 44), 14 * s, 26 * s))}" fill="{N}" opacity="0.6"/>')
            cxw = X(side * 88)
            out.append(f'<path d="{smooth_closed(arch_pts(cxw, Y(6 + st * 44), 9 * s, 30 * s, 6))}" fill="{S}" opacity="0.9"/>')
    # the great iwan: a framed portal with a deep pointed arch
    out.append(f'<path d="{pd([(X(-34), Y(0)), (X(-34), Y(112)), (X(34), Y(112)), (X(34), Y(0))])}" fill="{L}"/>')
    out.append(f'<path d="{pd([(X(-34), Y(112)), (X(34), Y(112)), (X(34), Y(108)), (X(-34), Y(108))])}" fill="{M}"/>')
    out.append(f'<path d="{smooth_closed(arch_pts(X(0), Y(0), 46 * s, 96 * s))}" fill="{S}"/>')
    out.append(f'<path d="{smooth_closed(arch_pts(X(4), Y(0), 30 * s, 74 * s))}" fill="{N}" opacity="0.65"/>')
    out.append(f'<path d="{smooth_closed(arch_pts(X(0), Y(0), 46 * s, 96 * s))}" fill="none" stroke="{N}" stroke-width="1.2" opacity="0.8"/>')
    out.append(f'<path d="{pd([(X(-30), Y(104)), (X(30), Y(104))], False)}" stroke="{N}" stroke-width="0.9" opacity="0.6"/>')
    # roof parapet, chhatris, drum and the dome
    for side in (-1, 1):
        hx = X(side * 66)
        out.append(f'<path d="{pd([(hx - 16 * s, Y(96)), (hx + 16 * s, Y(96)), (hx + 16 * s, Y(110)), (hx - 16 * s, Y(110))])}" fill="{M}"/>')
        for k in (-12, 0, 12):
            out.append(f'<path d="M {hx + k * s:.1f} {Y(110):.1f} L {hx + k * s:.1f} {Y(122):.1f}" stroke="{M}" stroke-width="{2 * s:.1f}"/>')
        out.append(f'<path d="{pd([(hx - 18 * s, Y(122)), (hx + 18 * s, Y(122)), (hx + 16 * s, Y(126)), (hx - 16 * s, Y(126))])}" fill="{L}"/>')
        out.append(f'<path d="{smooth_closed(onion_dome(hx, Y(126), 34 * s, 26 * s, 0.85))}" fill="{L}"/>')
        out.append(f'<path d="{smooth_closed(onion_dome(hx + 5 * s, Y(126), 18 * s, 22 * s, 0.85))}" fill="{S}" opacity="0.45"/>')
        out.append(f'<path d="M {hx:.1f} {Y(152):.1f} L {hx:.1f} {Y(160):.1f}" stroke="{N}" stroke-width="1.2"/>')
    out.append(f'<path d="{pd([(X(-50), Y(112)), (X(50), Y(112)), (X(50), Y(134)), (X(-50), Y(134))])}" fill="{M}"/>')
    out.append(f'<path d="{pd([(X(20), Y(112)), (X(50), Y(112)), (X(50), Y(134)), (X(20), Y(134))])}" fill="{S}" opacity="0.5"/>')
    dome = onion_dome(X(0), Y(134), 124 * s, 118 * s, 0.8)
    out.append(f'<path d="{smooth_closed(dome)}" fill="{L}"/>')
    g = D.lin([(0, "#FFFFFF", 0.5), (0.4, L, 0), (1, S, 0.75)], X(-62), 0, X(62), 0, "userSpaceOnUse")
    out.append(f'<path d="{smooth_closed(dome)}" fill="{g}"/>')
    out.append(f'<path d="{smooth_closed(dome)}" fill="none" stroke="{N}" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<path d="M {X(0):.1f} {Y(250):.1f} L {X(0):.1f} {Y(276):.1f}" stroke="{hz("#D8B060")}" stroke-width="{2.6 * s:.1f}"/>')
    out.append(f'<path d="{smooth_closed(onion_dome(X(0), Y(258), 8 * s, 8 * s, 0.8))}" fill="{hz("#D8B060")}"/>')
    out.append(f'<path d="{pd(hall)}" fill="none" stroke="{N}" stroke-width="1.2" opacity="0.6"/>')
    return "".join(out)


def cypress_row(D, pts, seed, col="#1E4A3A", light="#3E7A5A", hmul=1.0):
    out = []
    rnd = random.Random(seed)
    for x, base, h in pts:
        h *= hmul
        w = h * 0.22
        p = [(x, base - h), (x + w * 0.5, base - h * 0.6), (x + w * 0.55, base - h * 0.2), (x, base), (x - w * 0.55, base - h * 0.2), (x - w * 0.5, base - h * 0.6)]
        out.append(f'<path d="{smooth_closed(p)}" fill="{col}"/>')
        out.append(f'<path d="{smooth_closed([(x, base - h), (x - w * 0.5, base - h * 0.6), (x - w * 0.55, base - h * 0.2), (x - w * 0.1, base)])}" fill="{light}" opacity="0.6"/>')
    return "".join(out)


@design("taj-mahal")
def taj_mahal():
    D = Doc2("in-tj")
    out = [sky(D, [(0, "#7E8CC8"), (0.45, "#D8B0C0"), (0.75, "#F8D0B0"), (1, "#FCE6C8")], 1901, 600, ["#FFFFFF", "#F6C0B0", "#A8A0D0"], 70, angle=-3, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 470, 380, 230, "#FFE8B8", 0.7))
    out.append(soft_glow(D, 470, 380, 70, "#FFFFFF", 0.7))
    for cx_, cy_, w_ in ((130, 250, 120), (480, 210, 90)):
        out.append(puff_cloud(D, cx_, cy_, w_, 1902 + cx_, pal=("#FFF0F0", "#F6D6D8", "#C8A8C8"), op=0.75))
    # far garden trees in haze, the Taj, the near cypress avenues
    out.append(f'<path d="M -10 410 L 610 410 L 610 440 L -10 440 Z" fill="#B8A8C0"/>')
    out.append(dab_crown(D, 60, 404, 90, 22, [("#C8B8D0", "#A898B8", "#8A7AA0")], 1903, n=60, size=(6, 12), inkw=0))
    out.append(dab_crown(D, 540, 404, 90, 22, [("#C8B8D0", "#A898B8", "#8A7AA0")], 1904, n=60, size=(6, 12), inkw=0))
    out.append(taj(D, 300, 424, 0.9, 1905, haze=0.05))
    # forecourt and the long pool, the reflection broken by ripples
    out.append(f'<path d="M -10 434 L 610 434 L 610 610 L -10 610 Z" fill="#E8D8D0"/>')
    pool = [(236, 434), (364, 434), (420, 610), (180, 610)]
    out.append(f'<path d="{pd(pool)}" fill="#9AA8D0"/>')
    refl = taj(D, 0, 0, 0.9, 1907, haze=0.35)
    out.append(clipped(D, pd(pool), [f'<g transform="translate(300 450) scale(1 -0.6)" opacity="0.6">{refl}</g>',
                                      f'<path d="{pd(pool)}" fill="{D.lin([(0, "#F6D8C8", 0.1), (1, "#5A6AA8", 0.45)])}"/>',
                                      wave_lines(1908, (180, 440, 420, 600), ["#FFFFFF", "#C8D0F0"], 50, (14, 40), 1.6, 1, (0.3, 0.7))]))
    out.append(ink(pd(pool), "#8A7A90", 1.4, 1909, 1, 0.6))
    # cypress avenues converging toward the Taj, flower beds between
    left = [(228 - k * 40, 438 + k * 24, 28 + k * 17) for k in range(5)]
    right = [(372 + k * 40, 438 + k * 24, 28 + k * 17) for k in range(5)]
    out.append(f'<path d="{pd([(-10, 466), (190, 434), (230, 434), (170, 610), (-10, 610)])}" fill="#6A9A5A"/>')
    out.append(f'<path d="{pd([(610, 466), (410, 434), (370, 434), (430, 610), (610, 610)])}" fill="#6A9A5A"/>')
    out.append(grass(1910, (0, 470, 160, 600), ["#8AB86A", "#4A7A3A"], 80, (6, 14)))
    out.append(grass(1911, (440, 470, 600, 600), ["#8AB86A", "#4A7A3A"], 80, (6, 14)))
    out.append(cypress_row(D, left[::-1], 1912))
    out.append(cypress_row(D, right[::-1], 1913))
    for x, y, s in ((120, 300, 7), (148, 290, 6), (420, 268, 7)):
        out.append(bird_v(x, y, s, "#5A4A6A", 0.8))
    # lettering
    out.append(label(300, 108, "TAJ MAHAL", CINZEL, 66, "#4A2E5A", ls=6, max_w=460))
    out.append(sub(300, 144, "AGRA · AT FIRST LIGHT", "#8A4A5A", font=JOS, size=19, ls=6, line_w=30, gap=14))
    return finish_b(D, out, 1914)


# ================================================================ 20. kerala — a kettuvallam on the backwaters at golden hour
def coconut_palm(D, x, base, h, lean, seed, col="#2E4A2A", light="#6A8A3A"):
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    trunk = [(x, base), (x + lean * h * 0.35, base - h * 0.45), top]
    out = [taper(trunk, 9, 5, "#6A5038"), taper([(px - 2, py) for px, py in trunk], 3, 1.6, "#A88A60", 0.6)]
    for k in range(9):
        a = math.radians(-180 + k * 22 + rnd.uniform(-8, 8))
        L = h * rnd.uniform(0.32, 0.42)
        tip = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.6 + L * 0.35)
        mid = (top[0] + math.cos(a) * L * 0.5, top[1] + math.sin(a) * L * 0.5 - 6)
        out.append(taper([top, mid, tip], 7, 1, col))
        for j in range(8):
            t = 0.2 + j * 0.1
            px, py = top[0] + (tip[0] - top[0]) * t, top[1] + (mid[1] - top[1]) * 2 * t * (1 - t) + (tip[1] - top[1]) * t * t
            out.append(f'<path d="M {px:.1f} {py:.1f} l {math.cos(a + 1.2) * 12:.1f} {abs(math.sin(a + 1.2)) * 12 + 4:.1f} M {px:.1f} {py:.1f} l {math.cos(a - 1.2) * 12:.1f} {abs(math.sin(a - 1.2)) * 12 + 4:.1f}" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')
    for k in range(3):
        out.append(f'<circle cx="{top[0] + (k - 1) * 6:.1f}" cy="{top[1] + 6:.1f}" r="5" fill="#5A6A2A"/>')
    return "".join(out)


def houseboat(D, x, wl, s, seed):
    """Kettuvallam: a long curved wooden hull, a vaulted roof of woven palm thatch on bamboo, open windows."""
    def P(pts):
        return [(x + px * s, wl + py * s) for px, py in pts]

    out = []
    hull = P([(-10, -30), (20, -22), (300, -22), (330, -34), (318, -8), (290, 6), (30, 6), (4, -6)])
    out.append(painted(D, hull, ("#A8703A", "#6E4220", "#3A200C"), seed, sdir=(0, 1), sk=0.2, angle=0, n=18, inkw=1.6, hi=0.3))
    for k in range(3):
        out.append(pline(P([(14, -16 + k * 7), (160, -12 + k * 6), (314, -18 + k * 7)]), "#3A200C", 1.2, seed + k, 0.6, 1))
    # cabin: posts and open windows, then the thatched barrel roof
    out.append(f'<path d="{pd(P([(40, -24), (280, -24), (280, -70), (40, -70)]))}" fill="#3A2A1A"/>')
    for k in range(7):
        wx = 50 + k * 33
        out.append(f'<path d="{pd(P([(wx, -30), (wx + 24, -30), (wx + 24, -60), (wx, -60)]))}" fill="#FFD890" opacity="0.85"/>')
        out.append(f'<path d="M {x + (wx - 4) * s:.1f} {wl - 24 * s:.1f} L {x + (wx - 4) * s:.1f} {wl - 72 * s:.1f}" stroke="#E8C890" stroke-width="{2.4 * s:.1f}"/>')
    roof = P([(28, -66), (34, -92), (60, -110), (160, -118), (262, -110), (288, -92), (292, -66)])
    out.append(painted(D, roof, ("#E8C88A", "#B88A4A", "#6A4A1E"), seed + 5, sdir=(0, 1), sk=0.2, angle=-90, n=30, inkw=1.6, hi=0.4,
                       cols=["#F6DCA0", "#8A6A30", "#D8B070"]))
    for k in range(12):
        rx_ = 40 + k * 21
        out.append(pline(P([(rx_, -68), (rx_ + 2, -96 - 10 * math.sin(math.pi * k / 11)), (rx_ + 4, -112 + 4 * abs(k - 5.5) / 5.5)]), "#8A6A30", 1.2, seed + 10 + k, 0.5, 1))
    out.append(f'<path d="{pd(P([(290, -70), (322, -60), (318, -50), (288, -58)]))}" fill="#C8A060"/>')
    return "".join(out)


@design("kerala")
def kerala():
    D = Doc2("in-kl")
    out = [sky(D, [(0, "#F6A86A"), (0.5, "#FCD49A"), (1, "#FFEBC0")], 2001, 420, ["#FFFFFF", "#F28A5A"], 50, angle=-3, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 380, 330, 200, "#FFF2C0", 0.8))
    out.append(f'<circle cx="380" cy="330" r="34" fill="#FFF6D8"/>')
    # far bank: a low line of palms, misty
    out.append(f'<path d="M -10 372 L 610 372 L 610 392 L -10 392 Z" fill="#8A9A6A" opacity="0.8"/>')
    rnd = random.Random(2002)
    for k in range(26):
        x = -10 + k * 25 + rnd.uniform(-8, 8)
        out.append(coconut_palm(D, x, 382, rnd.uniform(40, 70), rnd.uniform(-0.2, 0.2), 2003 + k, col="#6A8A5A", light="#8AA06A"))
    out.append(mist(D, 368, 30, 2004, "#FFF2D8", 0.5))
    # water
    out.append(f'<path d="M -10 388 L 610 388 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#F6C88A", 1), (0.5, "#7AA8A0", 1), (1, "#3E6A70", 1)])}"/>')
    out.append(f'<path d="{blob(380, 430, 30, 110, 2005, 0.2, 14)}" fill="#FFF0C0" opacity="0.45"/>')
    out.append(wave_lines(2006, (0, 392, 600, 600), ["#FFFFFF", "#FFE0A0", "#2E5A60"], 90, (14, 50), 1.8, 1.2, (0.3, 0.75)))
    # the houseboat and its reflection
    hb = houseboat(D, 130, 470, 1.0, 2007)
    out.append(clipped(D, "M -10 470 L 610 470 L 610 610 L -10 610 Z", [f'<g transform="translate(0 940) scale(1 -1)" opacity="0.25">{houseboat(D, 130, 470, 1.0, 2007)}</g>']))
    out.append(hb)
    out.append(wave_lines(2008, (110, 474, 480, 500), ["#FFFFFF", "#FFE8C0"], 16, (20, 50), 1.8, 1.2, (0.5, 0.9)))
    # a leaning palm in the foreground left and a fisherman in his canoe on the right
    out.append(coconut_palm(D, 30, 600, 330, 0.34, 2009, col="#1E3A22", light="#3E6A3A"))
    cx_, cy_ = 470, 540
    out.append(f'<path d="{smooth_closed([(cx_ - 70, cy_ - 6), (cx_ + 70, cy_ - 8), (cx_ + 54, cy_ + 6), (cx_ - 56, cy_ + 6)])}" fill="#3A2414"/>')
    out.append(figures.person(cx_ - 10, cy_ - 6, 52, "paddle", 1, "silhouette:#2A1A12", seed=2010, light=-1))
    out.append(wave_lines(2011, (cx_ - 80, cy_ + 4, cx_ + 80, cy_ + 16), ["#FFFFFF"], 8, (20, 40), 1.6, 1, (0.5, 0.9)))
    for x, y, s in ((200, 250, 9), (226, 236, 7), (520, 210, 8)):
        out.append(bird_v(x, y, s, "#6A3A2A", 0.85))
    # lettering
    out.append(letters(D, 300, 140, "Kerala", SERIF_IT, 150, "#1E4A3A", ["#2E6A4A", "#0E2A1E", "#4A8A6A"], 2020, max_w=400,
                       shadow="#FFF2D8", soff=(0.022, 0.035), angle=-40, hi="#A8D8B8"))
    out.append(sub(300, 186, "BACKWATERS · SLOW, GOLDEN DAYS", "#8A3A1A", font=JOS, size=19, ls=4, line_w=20, gap=12))
    return finish_b(D, out, 2021)


# ================================================================ 21. jaipur — a jharokha in the pink city
def jaali(D, d, box, seed, col="#F6E0D0", cell=16):
    x0, y0, x1, y1 = box
    out = []
    y = y0
    j = 0
    while y < y1 + cell:
        x = x0 + (cell / 2 if j % 2 else 0)
        while x < x1 + cell:
            out.append(f'<path d="M {x:.1f} {y - cell * 0.5:.1f} L {x + cell * 0.5:.1f} {y:.1f} L {x:.1f} {y + cell * 0.5:.1f} L {x - cell * 0.5:.1f} {y:.1f} Z" fill="none" stroke="{col}" stroke-width="3"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{col}"/>')
            x += cell
        y += cell / 2
        j += 1
    return clipped(D, d, out)


def scallop_arch(cx, base, w, h, lobes=7):
    """Cusped (multifoil) arch outline: straight jambs and a scalloped head."""
    sp = base - h * 0.55
    pts = [(cx - w / 2, base), (cx - w / 2, sp)]
    for i in range(lobes * 6 + 1):
        t = i / (lobes * 6)
        a = math.pi * (1 - t)
        rx, ry = w / 2, h * 0.45
        bx, by = cx + math.cos(a) * rx, sp - math.sin(a) * ry
        bump = abs(math.sin(t * lobes * math.pi)) * w * 0.03
        pts.append((bx - math.cos(a) * bump * -1, by - math.sin(a) * bump * -1))
    pts += [(cx + w / 2, sp), (cx + w / 2, base)]
    return pts


@design("jaipur")
def jaipur():
    D = Doc2("in-jp")
    # the pink sandstone wall with white painted borders
    out = [sky(D, [(0, "#E8908A"), (1, "#D06A66")], 2101, 600, ["#F8B0A8", "#B85050", "#F2A098"], 130, angle=-84, sop=(0.08, 0.18))]
    out.append(blooms(2102, ["#F8C0B8", "#A84848"], 8, (0, 0, 600, 600), (90, 180), (0.08, 0.16)))
    out.append(soft_glow(D, 140, 200, 360, "#FFE6C8", 0.35))
    rnd = random.Random(2103)
    border = []
    for x in range(0, 620, 34):
        for y in (232, 566):
            border.append(f'<path d="{blob(x, y, 8, 8, x + y, 0.1, 10)}" fill="none" stroke="#FFF6EC" stroke-width="2.6"/>')
            border.append(f'<circle cx="{x + 17}" cy="{y}" r="2.6" fill="#FFF6EC"/>')
    out.append("".join(border))
    out.append(f'<path d="M -10 218 L 610 218 M -10 246 L 610 246 M -10 552 L 610 552" stroke="#FFF6EC" stroke-width="3"/>')
    # the jharokha: bracketed balcony, three cusped openings with jaali, a curved bangaldar roof, small domes
    out.append('<g transform="translate(42 72) scale(0.86)">')
    cx = 300
    sh = cast(D, cx + 20, 520, 210, 22, strength=0.4, seed=2104)
    out.append(sh)
    # brackets under the balcony
    for k, bx in enumerate((cx - 150, cx - 50, cx + 50, cx + 150)):
        br = [(bx - 14, 470), (bx + 14, 470), (bx + 10, 500), (bx, 528), (bx - 10, 500)]
        out.append(painted(D, br, ("#F6B8A8", "#D8807A", "#8A3A3A"), 2105 + k, sk=0.2, n=4, inkw=1.4, hi=0.35))
    base = poly_pts([(cx - 186, 450), (cx + 186, 450), (cx + 180, 474), (cx - 180, 474)], 10, 2109, 0.4)
    out.append(painted(D, base, ("#FFE8DC", "#F2C0B0", "#A8706A"), 2109, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    for k in range(13):
        out.append(f'<path d="{blob(cx - 168 + k * 28, 462, 6, 5, 2110 + k, 0.1, 8)}" fill="#D8807A"/>')
    # pillars and openings
    for k, ox in enumerate((cx - 116, cx, cx + 116)):
        op = scallop_arch(ox, 450, 92, 196, 7)
        d = smooth_closed(op)
        out.append(f'<path d="{d}" fill="#3A1E2A"/>')
        out.append(jaali(D, d, (ox - 46, 250, ox + 46, 452), 2112 + k, "#F8D8C8", 18))
        out.append(f'<path d="{d}" fill="{D.lin([(0, "#000000", 0.35), (1, "#000000", 0)])}"/>')
        out.append(ink(d, "#FFF6EC", 4, 2115 + k, 1, 0.9))
        out.append(ink(d, INK, 1.4, 2118 + k, 1, 0.5))
    for k, px in enumerate((cx - 174, cx - 58, cx + 58, cx + 174)):
        pl = poly_pts([(px - 10, 252), (px + 10, 252), (px + 10, 450), (px - 10, 450)], 8, 2120 + k, 0.3)
        out.append(painted(D, pl, ("#FFE0D4", "#F0B0A0", "#A8605A"), 2120 + k, sdir=(1, 0), sk=0.25, angle=-90, n=6, inkw=1.3, hi=0.4))
        for y in (300, 380):
            out.append(f'<path d="M {px - 10} {y} L {px + 10} {y}" stroke="#FFF6EC" stroke-width="2.4"/>')
    # the curved (bangaldar) roof and cupolas
    roof = [(cx - 200, 254), (cx - 180, 226), (cx, 206), (cx + 180, 226), (cx + 200, 254), (cx, 236)]
    out.append(painted(D, roof, ("#FFE8DC", "#F2B8A8", "#A8605A"), 2124, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.6, hi=0.45))
    for k, (dx, w, h) in enumerate(((-140, 52, 46), (0, 70, 60), (140, 52, 46))):
        dy = 214 if dx else 206
        out.append(f'<path d="{pd([(cx + dx - w * 0.5, dy + 6), (cx + dx + w * 0.5, dy + 6), (cx + dx + w * 0.42, dy - 4), (cx + dx - w * 0.42, dy - 4)])}" fill="#F2C0B0"/>')
        dm = onion_dome(cx + dx, dy - 4, w * 0.9, h, 0.9)
        out.append(painted(D, dm, ("#FFF0E8", "#F6CABC", "#B07068"), 2125 + k, sdir=(0.8, 0.3), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.45))
        out.append(f'<path d="M {cx + dx:.1f} {dy - 4 - h:.1f} l 0 -12" stroke="#D8A040" stroke-width="2.4"/><circle cx="{cx + dx}" cy="{dy - 4 - h - 13}" r="3" fill="#D8A040"/>')
    # a pigeon on the ledge, a string of marigolds hung in the middle opening
    out.append(garland(D, [(cx - 30, 300), (cx, 330), (cx + 30, 300)], 8, 2130, leaves=False))
    out.append(pline([(cx, 330), (cx + 1, 370)], "#8A3A1A", 1.4, 2131, 0.8, 1))
    out.append(marigold(D, cx + 1, 376, 8, 2132))
    # two clay pots of marigolds on the balcony ledge
    for k, px_ in enumerate((cx - 156, cx + 156)):
        pot = [(px_ - 22, 422), (px_ + 22, 422), (px_ + 16, 450), (px_ - 16, 450)]
        out.append(painted(D, poly_pts(pot, 6, 2133 + k, 0.3), CLAY, 2133 + k, sk=0.2, angle=-90, n=5, inkw=1.3, hi=0.35))
        out.append(f'<path d="{ellipse_d(px_, 422, 24, 5)}" fill="#8A3A1A"/>')
        for j_, (dx, dy, r) in enumerate(((-12, 410, 10), (10, 408, 11), (0, 396, 10))):
            out.append(leaf_simple(D, px_ + dx, dy + 8, 16, 5, -60 - j_ * 40, LEAF, 2135 + k * 5 + j_, vein=False, inkw=0.6))
            out.append(marigold(D, px_ + dx, dy, r, 2140 + k * 5 + j_, SAFFRON if j_ != 1 else HALDI))
    out.append('</g>')
    # lettering
    out.append(letters(D, 300, 134, "Jaipur", SERIF_IT, 140, "#FFF6EC", ["#FFFFFF", "#F8D8C8", "#FFEDE4"], 2140, max_w=400,
                       shadow="#7A2A34", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 180, "THE PINK CITY", "#5A1424", font=JOS, size=22, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 2141, "#5A1424", 0.6)


# ================================================================ 22. mor — the peacock dances when the monsoon comes
def eyespot(cx, cy, r, ang, k):
    a = math.degrees(ang)
    return (f'<g transform="rotate({a:.1f} {cx:.1f} {cy:.1f})">'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 1.25:.1f}" ry="{r:.1f}" fill="#C8A040"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 1.0:.1f}" ry="{r * 0.8:.1f}" fill="#2AA08A"/>'
            f'<ellipse cx="{cx - r * 0.1:.1f}" cy="{cy:.1f}" rx="{r * 0.7:.1f}" ry="{r * 0.6:.1f}" fill="#8A5A2A"/>'
            f'<ellipse cx="{cx - r * 0.18:.1f}" cy="{cy:.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.46:.1f}" fill="#1E2A8A"/>'
            f'<ellipse cx="{cx - r * 0.28:.1f}" cy="{cy - r * 0.1:.1f}" rx="{r * 0.14:.1f}" ry="{r * 0.12:.1f}" fill="#FFFFFF" opacity="0.6"/></g>')


@design("mor")
def mor():
    D = Doc2("in-mr")
    # monsoon sky: heavy slate clouds, a break of light, slanting rain
    out = [sky(D, [(0, "#3A4A5E"), (0.6, "#6A7E8A"), (1, "#A8B8A8")], 2201, 600, ["#8A9AAA", "#2A3A4E", "#B8C8C8"], 120, angle=-4, sop=(0.08, 0.2))]
    for cx_, cy_, w_ in ((120, 120, 240), (420, 90, 280), (300, 200, 300)):
        out.append(puff_cloud(D, cx_, cy_, w_, 2202 + cx_, pal=("#9AAAB8", "#6A7A8A", "#3A4A5A"), op=0.85))
    out.append(soft_glow(D, 300, 330, 300, "#E8F0D8", 0.4))
    # green ground and grass
    out.append(hill(D, ridge([(-20, 470), (300, 456), (620, 474)], 2203, 6, 3), 620, ("#8AB86A", "#4A8A3A", "#1E4A1E"), 2203, inkw=0))
    out.append(grass(2204, (0, 470, 600, 600), ["#6AA84A", "#2E6A2A", "#A8D07A"], 160, (10, 26)))
    # the fan: rows of feathers radiating from the body, each with an eye
    cx, cy = 300, 432
    fan_r = 238
    rays = []
    for i in range(46):
        a = math.radians(-172 + 164 * i / 45)
        rays.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * fan_r:.1f} {cy + math.sin(a) * fan_r:.1f}" stroke="#2E6A3A" stroke-width="2"/>')
    fan = [(cx + math.cos(math.radians(-174 + 168 * i / 40)) * fan_r * 1.04, cy + math.sin(math.radians(-174 + 168 * i / 40)) * fan_r * 1.04) for i in range(41)] + [(cx, cy + 10)]
    out.append(f'<path d="{smooth_closed(fan)}" fill="#1E5A3A"/>')
    out.append(f'<path d="{smooth_closed(fan)}" fill="{D.rad([(0, "#0E3A2A", 1), (0.7, "#2E7A4A", 1), (1, "#4A9A5A", 1)], 0.5, 1.0, 1.0)}"/>')
    out.append("".join(rays))
    rnd = random.Random(2205)
    for row, (rr, n, r) in enumerate(((0.95, 26, 13), (0.78, 21, 12), (0.6, 16, 10.5), (0.43, 11, 9))):
        for i in range(n):
            a = math.radians(-168 + 156 * (i + 0.5 * (row % 2)) / (n - 0.5 * (row % 2) if row % 2 else n - 1))
            out.append(eyespot(cx + math.cos(a) * fan_r * rr, cy + math.sin(a) * fan_r * rr, r, a, row))
    for _ in range(140):
        a = rnd.uniform(-3.0, -0.14)
        rr = rnd.uniform(0.3, 1.0) * fan_r
        out.append(f'<path d="M {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f} l {math.cos(a + 1.3) * 6:.1f} {math.sin(a + 1.3) * 6:.1f}" stroke="{rnd.choice(["#8AD07A", "#C8E08A", "#3E8A4A"])}" stroke-width="1.4" opacity="0.6"/>')
    out.append(ink(smooth_closed(fan), "#0E2A1A", 2, 2206, 1, 0.5))
    # the bird: wings, iridescent blue neck and breast, crest
    wing = [(cx - 40, cy - 6), (cx - 16, cy - 50), (cx + 16, cy - 50), (cx + 40, cy - 6), (cx + 30, cy + 40), (cx - 30, cy + 40)]
    out.append(painted(D, wing, ("#A8885A", "#6A4E2A", "#2A1E0E"), 2207, sk=0.2, angle=-90, n=14, inkw=1.6, hi=0.3))
    for k in range(6):
        out.append(f'<path d="M {cx - 30 + k * 12} {cy - 30} q 2 30 -2 64" stroke="#5A4020" stroke-width="1.6" fill="none" opacity="0.6"/>')
    body = [(cx - 20, cy + 30), (cx - 24, cy - 30), (cx - 14, cy - 92), (cx - 8, cy - 128), (cx + 6, cy - 132), (cx + 14, cy - 120), (cx + 8, cy - 92), (cx + 22, cy - 30), (cx + 20, cy + 30)]
    out.append(painted(D, body, ("#4A8AE8", "#1E4AB8", "#0E1E6A"), 2208, sdir=(0.6, 0.3), sk=0.18, angle=-90, n=16, inkw=1.6, hi=0.45))
    for _ in range(40):
        x, y = cx + rnd.uniform(-16, 16), cy + rnd.uniform(-110, 20)
        out.append(f'<path d="M {x:.1f} {y:.1f} q 3 3 6 0" stroke="#5AC8E8" stroke-width="1.2" fill="none" opacity="0.5"/>')
    hx, hy = cx + 2, cy - 136
    out.append(painted(D, blob_pts(hx, hy, 11, 10, 2209, 0.06, 12), ("#4A8AE8", "#1E4AB8", "#0E1E6A"), 2209, sk=0.15, n=4, inkw=1.4, hi=0.4))
    out.append(f'<path d="M {hx + 8} {hy - 1} L {hx + 20} {hy + 3} L {hx + 8} {hy + 5} Z" fill="#D8C8A8" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<path d="M {hx - 6} {hy - 4} q 8 -4 12 2" stroke="#FFFFFF" stroke-width="2.2" fill="none"/><circle cx="{hx + 3}" cy="{hy - 1}" r="2" fill="#1A1A1A"/>')
    out.append(f'<path d="M {hx - 4} {hy + 4} q 6 3 12 0" stroke="#FFFFFF" stroke-width="1.6" fill="none"/>')
    for k in range(6):
        a = math.radians(-120 + k * 12)
        tx, ty = hx + math.cos(a) * 26, hy - 8 + math.sin(a) * 26
        out.append(f'<path d="M {hx:.1f} {hy - 8:.1f} L {tx:.1f} {ty:.1f}" stroke="#1E2A6A" stroke-width="1.2"/><circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.2" fill="#1E4AB8"/>')
    # legs
    for dx in (-8, 8):
        out.append(f'<path d="M {cx + dx} {cy + 30} L {cx + dx * 1.4} {cy + 64} M {cx + dx * 1.4 - 6} {cy + 66} l 12 0" stroke="#8A7A6A" stroke-width="3" stroke-linecap="round"/>')
    # rain
    rn = []
    for _ in range(170):
        x, y = rnd.uniform(-20, 620), rnd.uniform(-20, 600)
        L = rnd.uniform(14, 30)
        rn.append(f'<path d="M {x:.1f} {y:.1f} l {-L * 0.25:.1f} {L:.1f}" stroke="#E8F0F8" stroke-width="1.4" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    out.append("".join(rn))
    # lettering
    out.append(letters(D, 300, 116, "Mor", SERIF_IT, 120, "#F2F8E8", ["#FFFFFF", "#D8E8C8", "#F0F8E8"], 2220, max_w=300,
                       shadow="#1E2A3A", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 156, "WHEN THE RAINS COME, HE DANCES", "#FFE8A0", font=JOS, size=18, ls=4, line_w=16, gap=10))
    return finish_b(D, out, 2221, "#FFFFFF", 0.4)


# ================================================================ 23. holi hai! — gulal clouds and brass plates of colour
def powder_cloud(D, cx, cy, r, col, seed, op=0.85):
    rnd = random.Random(seed)
    out = []
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        rr = r * math.sqrt(rnd.random()) * 0.7
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8
        s = r * rnd.uniform(0.35, 0.6)
        out.append(f'<path d="{blob(x, y, s, s * 0.85, rnd.randint(0, 9999), 0.2, 12)}" fill="{col}" opacity="{op * rnd.uniform(0.35, 0.7):.2f}"/>')
    out.append(specks(seed, (cx - r * 1.4, cy - r * 1.2, cx + r * 1.4, cy + r * 1.2), [col, lt(col, 0.4)], int(r * 1.2), (0.8, 2.6), (0.4, 0.9)))
    return "".join(out)


def gulal_plate(D, cx, cy, r, col, seed):
    out = [cast(D, cx + 6, cy + 10, r * 1.05, r * 0.3, strength=0.4, seed=seed)]
    rim = ellipse_d(cx, cy, r, r * 0.34)
    out.append(f'<path d="{rim}" fill="{BRASS[1]}"/>' + metal(D, rim, cx - r, cx + r, BRASS, 0.8, 0.8))
    out.append(f'<path d="{ellipse_d(cx, cy + 2, r * 0.82, r * 0.26)}" fill="{BRASS[2]}" opacity="0.6"/>')
    mound = [(cx - r * 0.72, cy + 2), (cx - r * 0.4, cy - r * 0.3), (cx, cy - r * 0.42), (cx + r * 0.4, cy - r * 0.3), (cx + r * 0.72, cy + 2), (cx, cy + r * 0.2)]
    out.append(painted(D, mound, (lt(col, 0.35), col, dk(col, 0.3)), seed, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=12, inkw=0, hi=0.45))
    out.append(specks(seed + 1, (cx - r * 0.7, cy - r * 0.4, cx + r * 0.7, cy + r * 0.1), [lt(col, 0.5), dk(col, 0.2)], int(r), (0.6, 1.6), (0.4, 0.9)))
    out.append(ink(rim, INK, 1.4, seed + 2, 1, 0.5))
    return "".join(out)


@design("holi-hai")
def holi_hai():
    D = Doc2("in-hh")
    out = [ground(D, "#FBF4EA", 2301)]
    # gulal thrown into the air: big soft clouds of pink, yellow, green, blue, orange
    for k, (x, y, r, c) in enumerate(((150, 300, 130, "#E8246E"), (450, 290, 130, "#F6C21C"), (300, 360, 120, "#1EA0D8"),
                                       (110, 470, 100, "#3EB84A"), (500, 470, 100, "#F2701E"), (300, 250, 90, "#A83AC8"))):
        out.append(powder_cloud(D, x, y, r, c, 2302 + k))
    # splashes and droplets
    rnd = random.Random(2310)
    for k in range(40):
        x, y = rnd.uniform(60, 540), rnd.uniform(220, 560)
        c = rnd.choice(["#E8246E", "#F6C21C", "#1EA0D8", "#3EB84A", "#F2701E", "#A83AC8"])
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 8), rnd.uniform(3, 7), k, 0.3, 8)}" fill="{c}" opacity="0.85"/>')
    # brass plates of gulal on the ground, a brass pichkari
    out.append(gulal_plate(D, 150, 512, 80, "#E8246E", 2311))
    out.append(gulal_plate(D, 300, 534, 84, "#3EB84A", 2312))
    out.append(gulal_plate(D, 452, 512, 80, "#F6C21C", 2313))
    # a brass pichkari: barrel, a tapering nozzle, finger rings, the plunger rod and its T-handle
    pc, pa = (452, 424), -16
    R = lambda pts: rot(pts, pc[0], pc[1], pa)
    out.append(cast(D, 456, 470, 110, 9, strength=0.35, seed=2313))
    out.append(taper(R([(500, 424), (584, 424)]), 7, 7, "#8A929C"))
    out.append(taper(R([(500, 422), (584, 422)]), 2, 2, "#F4F6F8", 0.8))
    out.append(painted(D, poly_pts(R([(578, 404), (590, 404), (590, 444), (578, 444)]), 5, 2319, 0.2), ("#E86A5A", "#C8301E", "#6A0E0A"), 2319, sk=0.2, n=3, inkw=1.3, hi=0.4))
    bar = poly_pts(R([(380, 408), (508, 408), (508, 440), (380, 440)]), 8, 2314, 0.3)
    out.append(painted(D, bar, BRASS, 2314, sdir=(0, 1), sk=0.25, angle=pa, n=10, inkw=1.6, hi=0.55, hik=0.14))
    for x in (396, 420, 470, 494):
        a_, b_ = R([(x, 409), (x, 439)])
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{BRASS[2]}" stroke-width="2.4" opacity="0.7"/>')
    for sgn in (-1, 1):
        rc = R([(500, 424 + sgn * 26)])[0]
        out.append(f'<circle cx="{rc[0]:.1f}" cy="{rc[1]:.1f}" r="9" fill="none" stroke="{BRASS[1]}" stroke-width="5"/><circle cx="{rc[0]:.1f}" cy="{rc[1]:.1f}" r="9" fill="none" stroke="{INK}" stroke-width="1" opacity="0.5"/>')
    nz = R([(380, 410), (340, 420), (330, 422), (330, 426), (340, 428), (380, 438)])
    out.append(painted(D, nz, BRASS, 2315, sk=0.2, n=4, inkw=1.3, hi=0.5))
    # its stream of pink colour arcing out, breaking into drops
    tip = R([(328, 424)])[0]
    stream = [tip, (tip[0] - 40, tip[1] - 34), (tip[0] - 96, tip[1] - 46), (tip[0] - 150, tip[1] - 30)]
    out.append(taper(stream, 7, 3, "#E8246E", 0.85))
    out.append(taper([(x, y - 2) for x, y in stream], 2, 1, "#FFB0D0", 0.8))
    for k in range(7):
        out.append(f'<path d="{blob(stream[-1][0] - 12 - k * 13, stream[-1][1] + 8 + k * 9 + rnd.uniform(-4, 4), 5 - k * 0.3, 4, 2320 + k, 0.2, 8)}" fill="#E8246E" opacity="{0.9 - k * 0.08:.2f}"/>')
    # lettering
    out.append(letters(D, 300, 150, "Holi hai!", SERIF_IT, 140, "#D6246E", ["#F04A8A", "#8A0E40", "#FF7AB0"], 2330, max_w=420,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFC0D8"))
    out.append(sub(300, 196, "BURA NA MANO, HOLI HAI", "#2A3A90", font=JOS, size=20, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 2331)


# ================================================================ 24. howzat! — gully cricket between the houses
@design("howzat")
def howzat():
    D = Doc2("in-hz")
    # a lane wall in turmeric yellow with peeling plaster, the wicket chalked on it
    out = [sky(D, [(0, "#F2C85A"), (1, "#E0A23A")], 2401, 600, ["#FFE08A", "#C8801A", "#F6D070"], 130, angle=-86, sop=(0.08, 0.18))]
    out.append(blooms(2402, ["#FFF0B0", "#A8641A"], 8, (0, 0, 600, 480), (80, 170), (0.08, 0.16)))
    rnd = random.Random(2403)
    for k in range(6):
        x, y = rnd.uniform(40, 560), rnd.uniform(240, 440)
        d = blob(x, y, rnd.uniform(20, 40), rnd.uniform(12, 24), 2404 + k, 0.3, 12)
        out.append(f'<path d="{d}" fill="#D8C8B0"/>')
        for j in range(4):
            out.append(f'<path d="M {x - 20} {y - 8 + j * 6} l {rnd.uniform(14, 34):.0f} 0" stroke="#B8603A" stroke-width="2.2" opacity="0.4"/>')
        out.append(ink(d, "#8A5A20", 1.2, 2405 + k, 1, 0.5))
    # a blue window with a grille, a potted tulsi-free money plant on the ledge
    out.append(f'<path d="{hg.org_rect(408, 236, 130, 120, 2410, 0.6, 12, 2)}" fill="#2E6E9A"/>')
    out.append(f'<path d="{hg.org_rect(420, 248, 106, 96, 2411, 0.6, 12, 2)}" fill="#1A3A4A"/>')
    for k in range(5):
        out.append(f'<path d="M {430 + k * 22} 250 L {430 + k * 22} 342" stroke="#5A9AC8" stroke-width="3"/>')
    out.append(f'<path d="M 420 296 L 526 296" stroke="#5A9AC8" stroke-width="3"/>')
    # ground: a dusty lane with a gutter edge
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="#C8A884"/>')
    out.append(strokes(D.nid(), pd([(-10, 470), (610, 470), (610, 610), (-10, 610)]), (-40, 470, 610, 600), ["#A8886A", "#E8D0B0", "#8A6A4A"], 2412, n=90, angle=0, length=(30, 110), width=(2, 5), opacity=(0.12, 0.32)))
    out.append(f'<path d="M -10 470 L 610 470" stroke="#7A5A3A" stroke-width="4"/>')
    # the chalk wicket on the wall: three stumps and bails, a little tally of runs
    wx = 196
    for k in (-26, 0, 26):
        out.append(taper([(wx + k, 466), (wx + k + 1, 330)], 7, 6, "#FFFFFF", 0.9))
    out.append(taper([(wx - 32, 326), (wx + 2, 324)], 6, 6, "#FFFFFF", 0.9))
    out.append(taper([(wx + 2, 324), (wx + 34, 326)], 6, 6, "#FFFFFF", 0.9))
    out.append(f'<text x="70" y="290" {JOS} font-size="24" fill="#FFFFFF" opacity="0.85">RUNS</text>')
    for k in range(4):
        out.append(taper([(76 + k * 12, 304), (78 + k * 12, 340)], 4, 3, "#FFFFFF", 0.85))
    out.append(taper([(70, 336), (130, 308)], 4, 3, "#FFFFFF", 0.85))
    out.append(taper([(76 + 5 * 12, 304), (78 + 5 * 12, 340)], 4, 3, "#FFFFFF", 0.85))
    # a bat leaning on the wall, a tape-wrapped tennis ball, a brick and a chappal marking the crease
    bat = [(300, 470), (318, 470), (336, 330), (352, 300), (338, 296), (322, 326)]
    bp_ = rot(poly_pts([(288, 300), (330, 300), (330, 470), (288, 470)], 8, 2413, 0.4), 309, 385, 12)
    out.append(cast(D, 330, 476, 40, 6, strength=0.4, seed=2414))
    out.append(painted(D, bp_, ("#F6DCA8", "#E2B87A", "#9A7440"), 2413, sdir=(1, 0.2), sk=0.25, angle=-80, n=18, inkw=1.6, hi=0.4))
    hd = rot([(301, 296), (317, 296), (317, 214), (301, 214)], 309, 385, 12)
    out.append(painted(D, poly_pts(hd, 6, 2415, 0.3), ("#4A4A6A", "#1E2A4A", "#0A0E1E"), 2415, sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.3))
    for k in range(8):
        y = 222 + k * 9
        a_, b_ = rot([(301, y), (317, y + 4)], 309, 385, 12)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#5A6A9A" stroke-width="2"/>')
    bx, by = 440, 520
    out.append(cast(D, bx + 4, by + 22, 28, 6, strength=0.45, seed=2416))
    out.append(painted(D, blob_pts(bx, by, 24, 24, 2417, 0.03, 16), ("#E8F080", "#C8D83A", "#7A8A1A"), 2417, sk=0.2, n=8, inkw=1.4, hi=0.45))
    for k, a in enumerate((-30, 20)):
        band = rot([(bx - 26, by - 6 + k * 14), (bx + 26, by - 6 + k * 14), (bx + 26, by + 2 + k * 14), (bx - 26, by + 2 + k * 14)], bx, by, a)
        out.append(clipped(D, ellipse_d(bx, by, 24, 24), [f'<path d="{pd(band)}" fill="#C8281E"/>']))
    out.append(f'<path d="M {bx - 18} {by - 4} q 18 12 36 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.7"/>')
    br = poly_pts([(70, 500), (150, 494), (152, 528), (72, 534)], 8, 2418, 0.4)
    out.append(painted(D, br, ("#E8906A", "#B8583A", "#6A2A18"), 2418, sk=0.2, angle=0, n=10, inkw=1.4, hi=0.3))
    ch = [(510, 548), (520, 520), (548, 512), (566, 524), (560, 552), (530, 562)]
    out.append(painted(D, ch, ("#6A8AC8", "#2E4A9A", "#122A5A"), 2419, sk=0.2, n=6, inkw=1.3, hi=0.3))
    out.append(f'<path d="M 524 528 q 14 -10 30 0" stroke="#F6C21C" stroke-width="3" fill="none"/>')
    # lettering
    out.append(letters(D, 300, 140, "Howzat!", SERIF_IT, 150, "#1E3A7A", ["#2E5AA8", "#0E1E4A", "#4A7AC8"], 2430, max_w=420,
                       shadow="#FFF4D8", soff=(0.022, 0.035), angle=-40, hi="#C8D8F8"))
    out.append(sub(300, 186, "GULLY CRICKET · ONE TIP, ONE HAND", "#7A2A10", font=JOS, size=18, ls=4, line_w=16, gap=10))
    return finish_b(D, out, 2431)


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
    for y, c in ((256, "#C8281E"), (266, "#F2901E"), (276, "#C8281E")):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="{c}" stroke-width="6" opacity="0.9"/>')
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
    pk = blob_pts(cx + 88, cy + 78, 24, 16, 2516, 0.15, 12)
    out.append(painted(D, pk, ("#E8603A", "#B8301E", "#6A0E0A"), 2516, sk=0.2, n=6, inkw=1.2, hi=0.4))
    for k in range(6):
        out.append(f'<path d="{blob(cx + 88 + rnd.uniform(-16, 16), cy + 78 + rnd.uniform(-9, 9), 5, 4, 2517 + k, 0.3, 8)}" fill="#F2A01E" opacity="0.8"/>')
    out.append(onion_ring(D, cx + 112, cy + 26, 16, 2520, 10))
    out.append(lemon_wedge(D, cx + 130, cy + 46, 18, 2521, 30))
    for k in range(3):
        out.append(f'<path d="{blob(cx + 122 + k * 11, cy + 2 - k * 6, 8, 3, 2522 + k, 0.2, 8, 40)}" fill="#7AC04A"/>')
    pp = blob_pts(cx - 20, cy + 110, 46, 24, 2525, 0.06, 18)
    out.append(painted(D, pp, ("#FFF4C8", "#F2D890", "#B89A50"), 2525, sk=0.12, n=6, inkw=1.2, hi=0.4))
    out.append(specks(2526, (cx - 58, cy + 94, cx + 18, cy + 126), ["#2A1A10", "#C89A40", "#FFFFFF"], 30, (0.7, 1.6), (0.5, 0.9)))
    out.append(steam(cx - 50, cy - 132, 36, 2527, "#FFFFFF", 2, 18, 4, 0.5))
    # lettering: माँ painted in the brush, then the rest of the phrase
    out.append(maa_devanagari(D, 110, 58, 132, "#B8201E", 2530, shadow="#F2C8A8", paper_c="#FBF1DE"))
    out.append(letters(D, 390, 132, "ke haath", SERIF_IT, 58, "#7A2410", ["#A83A1A", "#5A1406", "#C8502A"], 2531, max_w=260,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40))
    out.append(letters(D, 390, 186, "ka khana", SERIF_IT, 58, "#7A2410", ["#A83A1A", "#5A1406", "#C8502A"], 2532, max_w=260,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40))
    out.append(sub(300, 228, "MAA · MOM'S HOME COOKING", "#5A3A1A", font=JOS, size=19, ls=5, line_w=22, gap=12))
    return finish_b(D, out, 2533)


# ================================================================ 26. nani's kitchen — the steel rack, the achaar jar in the sun
def plate_on_edge(D, cx, base, r, seed):
    """A steel plate standing on its rim in a rack, seen slightly from the side: a tall narrow ellipse."""
    d = ellipse_d(cx, base - r, r * 0.28, r)
    out = [f'<path d="{d}" fill="#C8CED6"/>', metal(D, d, cx - r * 0.28, cx + r * 0.28, STEEL, 0.9, 0.8)]
    out.append(f'<path d="{ellipse_d(cx + r * 0.04, base - r, r * 0.2, r * 0.86)}" fill="none" stroke="#6E7884" stroke-width="1.4" opacity="0.6"/>')
    out.append(ink(d, INK, 1.2, seed, 1, 0.5))
    return "".join(out)


def achaar_jar(D, cx, base, w, h, seed, cloth_c="#D6342A"):
    """Ceramic barni: cream glazed belly with a brown glazed shoulder, a muslin cloth tied over the mouth."""
    top = base - h
    body = [(cx - w * 0.3, top + h * 0.12), (cx - w * 0.5, top + h * 0.4), (cx - w * 0.48, top + h * 0.8), (cx - w * 0.36, base), (cx + w * 0.36, base),
            (cx + w * 0.48, top + h * 0.8), (cx + w * 0.5, top + h * 0.4), (cx + w * 0.3, top + h * 0.12)]
    out = [cast(D, cx + 8, base + 4, w * 0.6, 8, strength=0.45, seed=seed)]
    out.append(painted(D, body, ("#FFF6E0", "#EEDDBA", "#A8906A"), seed, sdir=(0.7, 0.3), sk=0.2, angle=-90, n=16, inkw=1.6, hi=0.5))
    sh = [(cx - w * 0.3, top + h * 0.12), (cx - w * 0.47, top + h * 0.36), (cx + w * 0.47, top + h * 0.36), (cx + w * 0.3, top + h * 0.12)]
    out.append(clipped(D, smooth_closed(body), [f'<path d="{smooth_closed(sh + [(cx, top + h * 0.42)])}" fill="#8A4A1E"/>',
                                                f'<path d="M {cx - w:.1f} {top + h * 0.38:.1f} Q {cx:.1f} {top + h * 0.48:.1f} {cx + w:.1f} {top + h * 0.38:.1f}" stroke="#6A3010" stroke-width="3" fill="none" opacity="0.5"/>']))
    # through the glaze: oil and mango pieces glimpsed? no, ceramic is opaque — a painted band instead
    out.append(clipped(D, smooth_closed(body), [f'<path d="M {cx - w:.1f} {top + h * 0.66:.1f} Q {cx:.1f} {top + h * 0.74:.1f} {cx + w:.1f} {top + h * 0.66:.1f}" stroke="#2E6AA8" stroke-width="3" fill="none" opacity="0.7"/>']))
    cl = [(cx - w * 0.36, top + h * 0.16), (cx - w * 0.3, top - h * 0.06), (cx, top - h * 0.12), (cx + w * 0.3, top - h * 0.06), (cx + w * 0.36, top + h * 0.16),
          (cx + w * 0.42, top + h * 0.3), (cx + w * 0.28, top + h * 0.22), (cx, top + h * 0.2), (cx - w * 0.28, top + h * 0.22), (cx - w * 0.42, top + h * 0.3)]
    out.append(painted(D, cl, (lt(cloth_c, 0.4), cloth_c, dk(cloth_c, 0.35)), seed + 1, sk=0.2, angle=-60, n=10, inkw=1.4, hi=0.35))
    out.append(taper([(cx - w * 0.33, top + h * 0.12), (cx, top + h * 0.16), (cx + w * 0.33, top + h * 0.12)], 3, 3, "#F4E6C8"))
    return "".join(out)


@design("nanis-kitchen")
def nanis_kitchen():
    D = Doc2("in-nk")
    # a pistachio-green kitchen wall, the morning sun through a window
    out = [sky(D, [(0, "#BCE0C0"), (1, "#8CC4A0")], 2601, 600, ["#D8F0D8", "#6AA884", "#C8E8C8"], 120, angle=-84, sop=(0.06, 0.16))]
    out.append(blooms(2602, ["#E8F8E0", "#5A9A7A"], 8, (0, 0, 600, 600), (90, 180), (0.08, 0.16)))
    out.append(f'<path d="M 360 230 L 600 230 L 640 600 L 470 600 Z" fill="#FFF6D0" opacity="0.35"/>')
    # the steel rack: a wire frame with plates on edge, glasses hung upside down, katoris stacked
    rx0, rx1, ry0 = 76, 344, 228
    out.append(cast(D, 214, 400, 150, 12, strength=0.3, seed=2603))
    for x in (rx0, rx1):
        out.append(taper([(x, ry0), (x, 392)], 4, 4, "#8A929C"))
    for y in (ry0, 304, 392):
        out.append(taper([(rx0 - 4, y), (rx1 + 4, y)], 4, 4, "#8A929C"))
        out.append(taper([(rx0 - 4, y - 1.5), (rx1 + 4, y - 1.5)], 1.2, 1.2, "#FFFFFF", 0.8))
    for k in range(7):
        out.append(plate_on_edge(D, 106 + k * 18, 302, 36, 2604 + k))
    for k in range(4):
        gx = 252 + k * 24
        g = [(gx - 10, 232), (gx + 10, 232), (gx + 8, 290), (gx - 8, 290)]
        out.append(f'<path d="{pd(g)}" fill="#C8CED6"/>' + metal(D, pd(g), gx - 10, gx + 10))
        out.append(ink(pd(g), INK, 1, 2612 + k, 1, 0.5))
    for k in range(4):
        out.append(steel_bowl(D, 130, 384 - k * 14, 44, 18, 2620 + k, ry=10, inkw=1.0))
    for k in range(3):
        out.append(steel_bowl(D, 250, 384 - k * 16, 54, 22, 2625 + k, ry=12, inkw=1.0))
    out.append(steel_bowl(D, 318, 380, 30, 20, 2628, ry=8, inkw=1.0))
    # ladles and a jhara hanging from hooks under the rack
    for k, (hx, L, kind) in enumerate(((206, 24, "ladle"), (232, 30, "jhara"), (288, 22, "ladle"), (318, 34, "tongs"))):
        out.append(f'<path d="M {hx} 392 q 4 6 0 10" stroke="#8A929C" stroke-width="2.4" fill="none"/>')
        if kind == "tongs":
            out.append(taper([(hx, 402), (hx - 6, 402 + L)], 3.4, 3, "#8A929C") + taper([(hx, 402), (hx + 6, 402 + L)], 3.4, 3, "#6E7884"))
            continue
        out.append(taper([(hx, 402), (hx, 402 + L)], 4, 3.4, "#9AA2AC") + taper([(hx - 1, 402), (hx - 1, 402 + L)], 1.2, 1, "#FFFFFF", 0.8))
        bd = ellipse_d(hx, 402 + L + 10, 13, 11)
        out.append(f'<path d="{bd}" fill="#C8CED6"/>' + metal(D, bd, hx - 13, hx + 13) + ink(bd, INK, 1, 2645 + k, 1, 0.5))
        if kind == "jhara":
            out.append("".join(f'<circle cx="{hx - 7 + (i % 4) * 4.6:.1f}" cy="{402 + L + 4 + (i // 4) * 4.4:.1f}" r="1.2" fill="#4A525C"/>' for i in range(12)))
    # the window ledge: an achaar jar warming in the sun, a sprig of curry leaves in a glass
    out.append(soft_glow(D, 470, 300, 140, "#FFFFFF", 0.4))
    win = hg.org_rect(372, 226, 210, 220, 2630, 0.6, 12, 2)
    out.append(f'<path d="{win}" fill="{D.lin([(0, "#BFE2F2", 1), (1, "#FFF6D8", 1)])}"/>')
    rnd0 = random.Random(2631)
    twig = [(600, 250), (540, 270), (470, 262), (420, 290)]
    br_ = [pline(twig, "#6A4A2A", 3, 2631, 0.9, 1)]
    for k, (x, y) in enumerate(catmull(twig, 4)):
        for sgn in (-1, 1):
            br_.append(leaf_simple(D, x, y, rnd0.uniform(20, 30), 6, (rnd0.uniform(40, 80) if sgn > 0 else rnd0.uniform(200, 250)), ("#A8D86A", "#5A9A3A", "#2E5A1E"), 2640 + k * 2 + (sgn > 0), vein=False, inkw=0.6))
    out.append(clipped(D, win, br_))
    out.append(bird_v(430, 380, 9, "#3A3048", 0.8))
    for x in (372, 582):
        out.append(f'<path d="M {x} 226 L {x} 446" stroke="#2E6E9A" stroke-width="10"/>')
    out.append(f'<path d="M 372 226 L 582 226" stroke="#2E6E9A" stroke-width="10"/>')
    out.append(f'<path d="M 477 226 L 477 446 M 372 336 L 582 336" stroke="#2E6E9A" stroke-width="5"/>')
    out.append(f'<path d="{hg.org_rect(356, 440, 240, 18, 2632, 0.5, 12, 2)}" fill="#E8E0D0"/>')
    # counter
    out.append(f'<path d="M -10 456 L 610 456 L 610 610 L -10 610 Z" fill="#5A5A60"/>')
    out.append(specks(2633, (0, 456, 600, 600), ["#9A9AA0", "#2A2A30", "#D8D0C0"], 220, (0.8, 2.2), (0.4, 0.9)))
    out.append(f'<path d="M -10 456 L 610 456" stroke="#8A8A90" stroke-width="5"/>')
    out.append(achaar_jar(D, 452, 446, 98, 110, 2634))
    out.append(achaar_jar(D, 534, 446, 66, 76, 2635, cloth_c="#F2901E"))
    # chakla-belan (board and rolling pin) with a ball of dough, a brass lota
    out.append(cast(D, 190, 548, 120, 14, strength=0.5, seed=2636))
    out.append(f'<path d="{ellipse_d(186, 534, 112, 30)}" fill="#8A5A2E"/>')
    out.append(painted(D, ell_pts(186, 524, 112, 30, 0, 360, 28), ("#E8C08A", "#C8945A", "#7A4A1E"), 2637, sk=0.1, angle=0, n=14, inkw=1.6, hi=0.4))
    out.append(painted(D, blob_pts(170, 514, 32, 18, 2638, 0.08, 14), ("#FFF6E0", "#F2E2C0", "#B8A07A"), 2638, sk=0.2, n=6, inkw=1.3, hi=0.5))
    out.append(specks(2639, (140, 500, 200, 528), ["#FFFFFF"], 16, (0.8, 1.6), (0.5, 0.9)))
    out.append(taper([(80, 560), (300, 506)], 18, 18, "#D8A86A"))
    out.append(taper([(80, 559), (300, 505)], 6, 6, "#F2D8A8", 0.7))
    for ex in ((70, 563, 52, 568), (300, 506, 320, 501)):
        out.append(taper([(ex[0], ex[1]), (ex[2], ex[3])], 9, 7, "#A8743A"))
    # a cane basket of red onions and garlic
    bx, bb = 520, 548
    out.append(cast(D, bx + 6, bb + 2, 60, 9, strength=0.45, seed=2642))
    for k, (ox, oy, r) in enumerate(((-30, -40, 20), (0, -46, 22), (28, -38, 19), (-12, -58, 18), (16, -60, 17))):
        out.append(painted(D, blob_pts(bx + ox, bb + oy, r, r * 0.9, 2643 + k, 0.08, 12), ("#E87AA0", "#A8305A", "#5A0E2A") if k != 3 else ("#FFFDF0", "#F0E8D8", "#B8A890"), 2643 + k, sk=0.2, angle=-90, n=5, inkw=1.1, hi=0.45))
        out.append(taper([(bx + ox, bb + oy - r * 0.8), (bx + ox + 2, bb + oy - r * 1.3)], 3, 1, "#8A5A2A"))
    bk = [(bx - 52, bb - 40), (bx + 52, bb - 40), (bx + 44, bb), (bx - 44, bb)]
    out.append(painted(D, poly_pts(bk, 8, 2648, 0.3), ("#E8C88A", "#C8A060", "#7A5A2A"), 2648, sk=0.2, angle=0, n=10, inkw=1.4, hi=0.3))
    for k in range(4):
        out.append(f'<path d="M {bx - 50 + k * 2} {bb - 32 + k * 9} L {bx + 50 - k * 2} {bb - 32 + k * 9}" stroke="#8A6A3A" stroke-width="1.6" opacity="0.7"/>')
    lx, lb = 420, 552
    out.append(cast(D, lx + 6, lb + 2, 40, 7, strength=0.45, seed=2640))
    lota = [(lx - 14, lb - 74), (lx + 14, lb - 74), (lx + 10, lb - 62), (lx + 34, lb - 40), (lx + 30, lb - 10), (lx + 16, lb), (lx - 16, lb), (lx - 30, lb - 10), (lx - 34, lb - 40), (lx - 10, lb - 62)]
    out.append(painted(D, lota, BRASS, 2641, sdir=(0.8, 0.3), sk=0.25, angle=-90, n=10, inkw=1.5, hi=0.6))
    out.append(f'<path d="{ellipse_d(lx, lb - 74, 16, 4)}" fill="{BRASS[2]}"/>')
    # lettering
    out.append(letters(D, 300, 132, "Nani's kitchen", SERIF_IT, 96, "#1E5A3A", ["#2E7A4A", "#0E3A1E", "#4A9A6A"], 2650, max_w=460,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8F0D0"))
    out.append(sub(300, 176, "BEST FOOD IN THE WHOLE WORLD", "#8A2A1A", font=JOS, size=19, ls=4, line_w=18, gap=10))
    return finish_b(D, out, 2651)


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
    out = [sky(D, [(0, "#F6A21E"), (1, "#E2701A")], 2701, 600, ["#FFC860", "#C8500E", "#FFB040"], 140, angle=-30, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 380, 300, "#FFF0B0", 0.45))
    for y in (556, 572):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#FFE08A" stroke-width="3" opacity="0.8"/>')
    for x in range(0, 620, 24):
        out.append(f'<path d="{blob(x, 564, 6, 4, x, 0.2, 8)}" fill="#C8201E" opacity="0.8"/>')
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
    # lettering
    out.append(letters(D, 300, 150, "Rakhi", SERIF_IT, 156, "#8A0E1E", ["#B8201E", "#5A0410", "#D8402A"], 2720, max_w=360,
                       shadow="#FFE6A0", soff=(0.022, 0.035), angle=-40, hi="#FFA080"))
    out.append(sub(300, 198, "A THREAD AND A PROMISE", "#5A1406", font=JOS, size=20, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 2721)


# ================================================================ 28. namaste — shoes off at the door, the whole family's pile
def chappal(D, cx, cy, L, ang, seed, sole=("#C8945A", "#8A5A2E", "#4A2A10"), strap="#D6342A"):
    pts = rot([(cx - L * 0.5, cy), (cx - L * 0.42, cy - L * 0.17), (cx - L * 0.1, cy - L * 0.2), (cx + L * 0.3, cy - L * 0.16), (cx + L * 0.5, cy - L * 0.04),
               (cx + L * 0.46, cy + L * 0.12), (cx + L * 0.1, cy + L * 0.16), (cx - L * 0.36, cy + L * 0.16)], cx, cy, ang)
    out = [f'<path d="{smooth_closed(shift(pts, 3, 5))}" fill="#3A2410" opacity="0.3"/>']
    out.append(painted(D, pts, sole, seed, sk=0.15, angle=ang, n=6, inkw=1.3, hi=0.4))
    st = rot([(cx + L * 0.22, cy - L * 0.17), (cx + L * 0.06, cy), (cx + L * 0.22, cy + L * 0.15)], cx, cy, ang)
    out.append(ink(smooth_open(st), strap, max(3, L * 0.07), seed, 1, 1))
    toe = rot([(cx + L * 0.34, cy - L * 0.01)], cx, cy, ang)[0]
    out.append(ink(smooth_open([st[1], toe]), strap, max(2.4, L * 0.05), seed + 1, 1, 1))
    return "".join(out)


def sneaker(D, cx, cy, L, ang, seed, upper=("#8AC0F0", "#2E7AC8", "#0E3A6A"), sole_c="#FFFFFF"):
    pts = rot([(cx - L * 0.5, cy), (cx - L * 0.44, cy - L * 0.2), (cx - L * 0.1, cy - L * 0.24), (cx + L * 0.3, cy - L * 0.2), (cx + L * 0.5, cy - L * 0.06),
               (cx + L * 0.48, cy + L * 0.14), (cx + L * 0.1, cy + L * 0.2), (cx - L * 0.4, cy + L * 0.18)], cx, cy, ang)
    out = [f'<path d="{smooth_closed(shift(pts, 3, 5))}" fill="#3A2410" opacity="0.3"/>']
    out.append(f'<path d="{smooth_closed(pts)}" fill="{sole_c}" stroke="{INK}" stroke-width="1.4" stroke-opacity="0.6"/>')
    inner = rot([(cx - L * 0.44, cy), (cx - L * 0.38, cy - L * 0.15), (cx - L * 0.1, cy - L * 0.18), (cx + L * 0.28, cy - L * 0.14), (cx + L * 0.44, cy - L * 0.04),
                 (cx + L * 0.42, cy + L * 0.1), (cx + L * 0.1, cy + L * 0.15), (cx - L * 0.36, cy + L * 0.13)], cx, cy, ang)
    out.append(painted(D, inner, upper, seed, sk=0.15, angle=ang, n=6, inkw=1.0, hi=0.4))
    op = rot([(cx - L * 0.36, cy), (cx - L * 0.3, cy - L * 0.08), (cx - L * 0.12, cy - L * 0.08), (cx - L * 0.06, cy), (cx - L * 0.12, cy + L * 0.07), (cx - L * 0.3, cy + L * 0.07)], cx, cy, ang)
    out.append(f'<path d="{smooth_closed(op)}" fill="#2A2A30"/>')
    for k in range(4):
        a_, b_ = rot([(cx - L * 0.02 + k * L * 0.08, cy - L * 0.09), (cx - L * 0.02 + k * L * 0.08, cy + L * 0.09)], cx, cy, ang)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#FFFFFF" stroke-width="2.2"/>')
    return "".join(out)


@design("namaste")
def namaste():
    D = Doc2("in-nm")
    # seen from above: the marble-tiled entryway and a cotton dhurrie doormat
    out = [f'<rect width="600" height="600" fill="#EDE6DA"/>']
    for x in range(0, 600, 150):
        for y in range(0, 600, 150):
            out.append(f'<path d="{hg.org_rect(x + 2, y + 2, 146, 146, x + y, 0.4, 14, 2)}" fill="{["#F4EEE4", "#E8E0D2"][(x + y) // 150 % 2]}"/>')
    rnd = random.Random(2801)
    for _ in range(18):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(pline([(x, y), (x + rnd.uniform(10, 40), y + rnd.uniform(-10, 30)), (x + rnd.uniform(30, 80), y + rnd.uniform(0, 40))], "#B8A890", 1, rnd.randint(0, 99), 0.35, 1))
    mat = poly_pts([(96, 222), (504, 214), (512, 530), (90, 536)], 12, 2802, 0.8)
    out.append(cast(D, 302, 386, 230, 170, strength=0.2, seed=2803))
    out.append(f'<path d="{smooth_closed(mat)}" fill="#2A3A7A"/>')
    stripes = []
    for k, (y, c, w) in enumerate(((236, "#F2901E", 14), (262, "#FFFFFF", 6), (290, "#D6342A", 18), (320, "#F6C21C", 8), (440, "#F6C21C", 8), (470, "#D6342A", 18), (498, "#FFFFFF", 6), (520, "#F2901E", 14))):
        stripes.append(f'<path d="M 60 {y} L 540 {y - 4}" stroke="{c}" stroke-width="{w}"/>')
    for k in range(9):
        x = 130 + k * 42
        stripes.append(f'<path d="M {x} 352 l 14 24 l -14 24 l -14 -24 Z" fill="{["#F2901E", "#FFFFFF", "#F6C21C"][k % 3]}"/>')
    stripes.append(strokes(D.nid(), smooth_closed(mat), (90, 214, 512, 536), ["#FFFFFF", "#0E1A4A"], 2804, n=90, angle=0, length=(20, 60), width=(1, 3), opacity=(0.1, 0.25)))
    out.append(clipped(D, smooth_closed(mat), stripes))
    for x in range(96, 510, 12):
        out.append(f'<path d="M {x} 222 l -2 -12 M {x} 536 l 2 12" stroke="#E8E0D0" stroke-width="2.4"/>')
    out.append(ink(smooth_closed(mat), INK, 1.6, 2805, 1, 0.5))
    # the shoe pile: chappals, kolhapuris, school sneakers, a pair of tiny kids' sandals, heels for the party
    out.append(chappal(D, 150, 300, 110, -20, 2806))
    out.append(chappal(D, 176, 336, 110, -8, 2807))
    out.append(sneaker(D, 410, 300, 130, 24, 2808))
    out.append(sneaker(D, 440, 350, 130, 8, 2809))
    out.append(chappal(D, 300, 468, 120, 170, 2810, sole=("#E8C08A", "#B8864A", "#6A4418"), strap="#8A4A1A"))
    out.append(chappal(D, 316, 500, 120, 190, 2811, sole=("#E8C08A", "#B8864A", "#6A4418"), strap="#8A4A1A"))
    out.append(chappal(D, 126, 470, 70, 40, 2812, sole=("#FFB8D0", "#E85A8A", "#8A1A4A"), strap="#F6C21C"))
    out.append(chappal(D, 150, 486, 70, 60, 2813, sole=("#FFB8D0", "#E85A8A", "#8A1A4A"), strap="#F6C21C"))
    out.append(chappal(D, 474, 470, 96, -150, 2814, sole=("#F2D8A8", "#C8A060", "#6A4A1A"), strap="#12808A"))
    out.append(chappal(D, 290, 330, 104, 100, 2815, sole=("#5A5A6A", "#2A2A36", "#0E0E14"), strap="#2E7AC8"))
    # lettering
    out.append(letters(D, 300, 140, "Namaste", SERIF_IT, 140, "#2A3A7A", ["#3E5AA8", "#121E4A", "#5A7AC8"], 2820, max_w=420,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#C8D8F8"))
    out.append(sub(300, 186, "SHOES OFF, COME ON IN", "#B8401A", font=JOS, size=21, ls=6, line_w=24, gap=12))
    return finish_b(D, out, 2821)


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
    for k, (x, w, h) in enumerate(((20, 120, 200), (150, 90, 150), (380, 140, 230), (520, 100, 170))):
        out.append(f'<path d="{hg.org_rect(x, 420 - h, w, h + 40, k + 2902, 0.8, 14, 2)}" fill="#7A8EA2" opacity="0.6"/>')
        for j in range(int(h / 30)):
            for i in range(int(w / 30)):
                if (i + j + k) % 3:
                    out.append(f'<rect x="{x + 10 + i * 30}" y="{420 - h + 12 + j * 30}" width="12" height="14" fill="{"#FFE6A0" if (i * j + k) % 5 == 0 else "#5A6E82"}" opacity="0.6"/>')
    for k, (x, h, ln) in enumerate(((150, 250, 0.12), (230, 200, -0.08), (470, 230, 0.1))):
        out.append(f'<g opacity="0.75">{coconut_palm(D, x, 420, h, ln, 2906 + k, col="#4A6070", light="#6A8090")}</g>')
    out.append(mist(D, 330, 60, 2907, "#C8D8E4", 0.5))
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
    out.append(steam(444, 448, 54, 2923, "#FFFFFF", 2, 16, 5, 0.6))
    out.append(steam(516, 444, 48, 2924, "#FFFFFF", 2, 14, 5, 0.5))
    out.append(steam(250, 470, 40, 2925, "#FFFFFF", 3, 26, 5, 0.45))
    # lettering
    out.append(letters(D, 300, 140, "Baarish", SERIF_IT, 150, "#FFF6E8", ["#FFFFFF", "#D8E4EE", "#F0F6FA"], 2930, max_w=420,
                       shadow="#2A3A4E", soff=(0.022, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(sub(300, 186, "CHAI, PAKORE & THE FIRST RAIN", "#FFE08A", font=JOS, size=19, ls=4, line_w=20, gap=12))
    return finish_b(D, out, 2931, "#1A2A3A", 0.5)


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
    out.append(letters(D, 300, 132, "Dadi ke laddoo", SERIF_IT, 96, "#8A2A10", ["#B8401A", "#5A1406", "#D8602A"], 3030, max_w=460,
                       shadow="#FFFFFF", soff=(0.022, 0.035), angle=-40, hi="#FFB880"))
    out.append(sub(300, 176, "EXTRA GHEE, EXTRA LOVE", "#2E5A8A", font=JOS, size=21, ls=6, line_w=24, gap=12))
    return finish_b(D, out, 3031)


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
