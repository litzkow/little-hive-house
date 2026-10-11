"""Philippines, hand-painted (gouache / storybook) edition: 30 magnets for Filipino-American families, balikbayans
and everyone who loves the Philippines.

Same idiom as the Brasil and Korea sets: warm paper ground, layered washes with pooled edges, brush strokes that
follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Hero words are in
Filipino / Tagalog (a little Taglish where people really talk that way), lightly glossed in English where needed.
Colour story: the flag's sun yellow, blue and red used with restraint, banana-leaf and rice-paddy greens, ube purple,
mango gold, capiz-shell pearl, nipa and rattan tans, narra wood, and the candy colours of fiesta banderitas.

Run from tools/designs:  python3 philippines_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps, qpts)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import (rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, banana_leaf, palm, sea, seagull,
                            hibiscus)
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, leaf_simple, wood_planks, heart_d, steam,
                            finish_b, bird_v, p_heart, branch)
from japan_painted import densify, round_poly, clipped
import holidays_gouache as hg
import figures

COL = "philippines"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
ARAW = ("#FFE88A", "#F6C51E", "#B88A08")        # the flag's sun
BUGHAW = ("#5A86D8", "#1E4AA0", "#0C2460")      # flag blue
PULA = ("#F2766A", "#CE2A2A", "#7A0E10")        # flag red
UBE = ("#B88AD8", "#6E3A9E", "#36164E")
MANGGA = ("#FFE27A", "#F5B623", "#B0700A")
SAGING = ("#9ED870", "#3E9A3A", "#1A5A22")      # banana leaf
PALAY = ("#D8E890", "#9AC04A", "#4E7A1E")       # young rice
NIPA = ("#E8C88A", "#C09A58", "#7A5A2A")        # nipa thatch
RATTAN = ("#F0CE8E", "#CC9A54", "#7E5424")
NARRA = ("#C88A5A", "#8A4E2A", "#4A2410")       # narra wood
PALAYOK = ("#E8946A", "#B8582E", "#62280E")     # clay pot
CAPIZ = ("#FFFCF2", "#F2EAD8", "#C4B49A")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
STEEL = ("#F4F6F8", "#C8CED6", "#7A8494")
RICE = ("#FFFFFF", "#F7F3EA", "#B8B2A8")
TEAL = ("#6AC8C0", "#1E8A86", "#0C4A4A")
PINK = ("#FFB0C8", "#EE6A98", "#A82A5A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


lt, dk = hg.lt, hg.dk


# ================================================================ philippines toolkit
def ellipse_d(cx, cy, rx, ry, n=36):
    return smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, n)[:-1])


def banig(D, d, seed, cell=16, base="#E8CC94", bands=("#C8285A", "#2E8A5A", "#F2B21E", "#6A3A9E"), rot_=45, op=0.9):
    """Woven pandan / buri mat (banig): over-under checker of natural strips crossed by coloured bands."""
    c = cell
    rnd = random.Random(seed)
    W = c * 12
    tile = [f'<rect width="{W}" height="{W}" fill="{base}"/>']
    # coloured warp/weft bands at fixed positions in the tile
    band_rows = {2: bands[0], 3: bands[0], 7: bands[1], 9: bands[2]}
    band_cols = {1: bands[3], 5: bands[0], 6: bands[0], 10: bands[1]}
    for i in range(12):
        for j in range(12):
            x, y = i * c, j * c
            over = (i + j) % 2 == 0
            col = band_cols.get(i) if over else band_rows.get(j)
            if col is None:
                col = mix(base, "#FFFFFF" if over else "#8A6A3A", 0.12 if over else 0.18)
            tile.append(f'<rect x="{x + 0.6:.1f}" y="{y + 0.6:.1f}" width="{c - 1.2:.1f}" height="{c - 1.2:.1f}" rx="2" fill="{col}"/>')
            if over:
                tile.append(f'<path d="M {x + 2:.1f} {y + 3:.1f} L {x + c - 2:.1f} {y + 3:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.35"/>')
                tile.append(f'<path d="M {x + 2:.1f} {y + c - 2:.1f} L {x + c - 2:.1f} {y + c - 2:.1f}" stroke="#5A3A18" stroke-width="1" opacity="0.3"/>')
            else:
                tile.append(f'<path d="M {x + 3:.1f} {y + 2:.1f} L {x + 3:.1f} {y + c - 2:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.3"/>')
                tile.append(f'<path d="M {x + c - 2:.1f} {y + 2:.1f} L {x + c - 2:.1f} {y + c - 2:.1f}" stroke="#5A3A18" stroke-width="1" opacity="0.3"/>')
    pat = D.pattern(W, W, "".join(tile), transform=f"rotate({rot_})" if rot_ else "")
    return f'<path d="{d}" fill="{pat}" opacity="{op}"/>'


def palayok(D, cx, rim_y, rx, h, seed, ry=None, belly=1.14, pal=PALAYOK, soot=0.55):
    """Clay pot (palayok): thick rolled lip, round belly wider than the mouth, soot-darkened bottom, clay grit."""
    ry = ry or rx * 0.32
    bot = rim_y + h
    R = rx * belly
    body = [(cx + rx + 6, rim_y + 4), (cx + R, rim_y + h * 0.36), (cx + R * 0.96, rim_y + h * 0.6), (cx + R * 0.78, rim_y + h * 0.86),
            (cx + R * 0.42, bot), (cx - R * 0.42, bot), (cx - R * 0.78, rim_y + h * 0.86), (cx - R * 0.96, rim_y + h * 0.6),
            (cx - R, rim_y + h * 0.36), (cx - rx - 6, rim_y + 4)]
    body += ell_pts(cx, rim_y, rx + 8, ry + 5, 180, 360, 18)[1:-1]
    d = smooth_closed(body)
    out = [cast(D, cx + 16, bot - 4, R * 1.05, h * 0.16, strength=0.45, seed=seed)]
    out.append(painted(D, body, pal, seed, sdir=(0.85, 0.35), sk=0.18, angle=-75, n=70, slen=(12, 34), sw=(1.2, 3.4),
                       cols=[pal[0], pal[2], lt(pal[0], 0.2), pal[1]], inkw=2.2, inkop=0.7, hi=0.4, hik=0.06))
    inner = [f'<path d="{d}" fill="{D.lin([(0, "#1A0E0A", 0), (0.55, "#1A0E0A", 0), (1, "#1A0E0A", soot)])}"/>',
             specks(seed + 1, (cx - R, rim_y, cx + R, bot), ["#F2B08A", "#4A1A08", "#FFD8B8"], int(R * 1.2), (0.6, 1.5), (0.25, 0.6))]
    # a lighter girdle line where the two halves were paddled together, and burnished highlight
    inner.append(pline(ell_pts(cx, rim_y + h * 0.36, R, ry * 0.9, 10, 170, 18), lt(pal[0], 0.25), 2.2, seed + 2, 0.5, 1))
    inner.append(pline(ell_pts(cx, rim_y + h * 0.36 + 3, R, ry * 0.9, 10, 170, 18), pal[2], 1.4, seed + 3, 0.45, 1))
    inner.append(taper([(cx - R * 0.78, rim_y + h * 0.22), (cx - R * 0.86, rim_y + h * 0.42), (cx - R * 0.72, rim_y + h * 0.68)], 10, 2, "#FFE0C8", 0.4))
    inner.append(taper([(cx - R * 0.72, rim_y + h * 0.26), (cx - R * 0.78, rim_y + h * 0.42)], 4, 1, "#FFFFFF", 0.55))
    out.append(clipped(D, d, inner))
    # rolled lip
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx + 8, ry + 5)}" fill="{pal[1]}"/>')
    out.append(taper(ell_pts(cx, rim_y, rx + 5, ry + 3, 160, 340, 20), 6, 4, pal[0], 0.85))
    out.append(taper(ell_pts(cx, rim_y + 2, rx + 7, ry + 4, 10, 170, 20), 4, 3, pal[2], 0.6))
    out.append(ink(ellipse_d(cx, rim_y, rx + 8, ry + 5), INK, 1.8, seed, 1, 0.7))
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx, ry)}" fill="{dk(pal[2], 0.3)}"/>')
    return "".join(out)


def bay_leaf(D, x, y, L, ang, seed, pal=("#B8B070", "#7E7A3A", "#46441C")):
    return leaf_simple(D, x, y, L, L * 0.2, ang, pal, seed, vein=True, inkw=1.0)


def peppercorns(seed, box, n, avoid=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(2.4, 3.6)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#2A1A12"/><circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.35:.1f}" fill="#8A7A6A" opacity="0.8"/>')
    return "".join(out)


def garlic_clove(D, cx, cy, s, ang, seed, pal=("#FFF6DE", "#F0DCB0", "#B89A62"), toasted=0.0):
    pts = rot([(cx - s, cy + s * 0.2), (cx - s * 0.6, cy - s * 0.45), (cx + s * 0.2, cy - s * 0.55), (cx + s * 0.9, cy - s * 0.15),
               (cx + s * 0.95, cy + s * 0.2), (cx + s * 0.1, cy + s * 0.42), (cx - s * 0.6, cy + s * 0.42)], cx, cy, ang)
    if toasted:
        pal = (mix(pal[0], "#F2C070", toasted), mix(pal[1], "#D8902E", toasted), mix(pal[2], "#7A4410", toasted))
    out = [painted(D, pts, pal, seed, sdir=(0.4, 0.9), sk=0.2, angle=ang, n=5, inkw=1.0, inkop=0.55, hi=0.5)]
    a = math.radians(ang)
    out.append(pline([(cx - math.cos(a) * s * 0.7, cy - math.sin(a) * s * 0.7 - 1), (cx + math.cos(a) * s * 0.7, cy + math.sin(a) * s * 0.7 - 2)], pal[2], 0.9, seed, 0.45, 1))
    return "".join(out)


def garlic_bulb(D, cx, cy, r, seed):
    out = [cast(D, cx + 6, cy + r * 0.85, r * 1.05, r * 0.25, strength=0.4, seed=seed)]
    lobes = [(-0.45, 0.06, 0.55), (0.45, 0.06, 0.55), (-0.18, 0.0, 0.62), (0.2, 0.0, 0.62), (0, 0.04, 0.6)]
    for k, (dx, dy, w) in enumerate(lobes):
        pts = [(cx + dx * r, cy - r * 1.05), (cx + dx * r + w * r * 0.9, cy - r * 0.2 + dy * r), (cx + dx * r + w * r * 0.6, cy + r * 0.62),
               (cx + dx * r, cy + r * 0.78), (cx + dx * r - w * r * 0.6, cy + r * 0.62), (cx + dx * r - w * r * 0.9, cy - r * 0.2 + dy * r)]
        pal = ("#FFFDF4", "#F2E6D0", "#BFA88A") if k > 1 else ("#F8EEE0", "#E6D4BA", "#A88E6E")
        out.append(painted(D, pts, pal, seed + k, sdir=(0.7, 0.6), sk=0.2, angle=-90, n=8, inkw=1.1, inkop=0.55, hi=0.5))
        out.append(pline([(cx + dx * r, cy - r * 0.95), (cx + dx * r * 1.15, cy), (cx + dx * r, cy + r * 0.7)], "#C8A0B0", 1.2, seed + k, 0.5, 1))
    out.append(taper([(cx, cy - r * 1.0), (cx + 2, cy - r * 1.35), (cx + 6, cy - r * 1.55)], 7, 3, "#D8C4A0"))
    for k in range(6):
        out.append(f'<path d="M {cx - r * 0.3 + k * r * 0.12:.1f} {cy + r * 0.78:.1f} l {-2 + k:.1f} 5" stroke="#B8A080" stroke-width="1.1"/>')
    return "".join(out)


def rice_bowl_side(D, cx, rim_y, rx, h, seed, glaze=WHITE, band=BUGHAW, mound=0.55):
    """A plain enamel/porcelain bowl from the side, heaped with steaming rice."""
    ry = rx * 0.26
    body = [(cx + rx, rim_y), (cx + rx * 0.92, rim_y + h * 0.55), (cx + rx * 0.55, rim_y + h), (cx - rx * 0.55, rim_y + h),
            (cx - rx * 0.92, rim_y + h * 0.55), (cx - rx, rim_y)] + ell_pts(cx, rim_y, rx, ry, 180, 360, 14)[1:-1]
    out = [cast(D, cx + 8, rim_y + h + 2, rx * 0.95, 8, strength=0.4, seed=seed)]
    # rice heap behind the front rim
    heap = ell_pts(cx, rim_y, rx - 2, ry, 180, 360, 16)
    heap = [(x, y - mound * rx * 0.55 * math.sin(math.pi * (x - cx + rx) / (2 * rx)) ** 0.8) for x, y in heap]
    hp = heap + ell_pts(cx, rim_y, rx - 2, ry, 0, 180, 12)[1:-1]
    out.append(painted(D, hp, RICE, seed + 1, sdir=(0.6, 0.8), sk=0.15, angle=-30, n=10, inkw=1.2, inkop=0.45, hi=0.5))
    out.append(rice_grains(seed + 2, hp, int(rx * 1.1)))
    out.append(painted(D, body, glaze, seed + 3, sdir=(0.9, 0.3), sk=0.18, angle=-85, n=16, inkw=1.8, hi=0.5, hik=0.06))
    out.append(pline(ell_pts(cx, rim_y + h * 0.18, rx * 0.97, ry * 0.95, 8, 172, 16), band[1], 2.6, seed + 4, 0.85, 1))
    out.append(pline(ell_pts(cx, rim_y + h * 0.27, rx * 0.94, ry * 0.9, 10, 170, 16), band[1], 1.3, seed + 5, 0.7, 1))
    out.append(taper([(cx - rx * 0.78, rim_y + h * 0.3), (cx - rx * 0.66, rim_y + h * 0.75)], 4, 1, "#FFFFFF", 0.85))
    return "".join(out)


def rice_grains(seed, pts, n, col="#FFFFFF", shade="#C8C0B0"):
    """Little grain marks inside an area (approximate: within its bbox, kept near the centre)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = bbox(pts)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for _ in range(n):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.88
        x, y = cx + math.cos(a) * (x1 - x0) / 2 * r, cy + math.sin(a) * (y1 - y0) / 2 * r
        t = rnd.uniform(0, 3.14)
        L = rnd.uniform(3, 5)
        out.append(f'<path d="M {x - math.cos(t) * L / 2:.1f} {y - math.sin(t) * L / 2:.1f} l {math.cos(t) * L:.1f} {math.sin(t) * L:.1f}" stroke="{rnd.choice([col, col, shade])}" stroke-width="2.2" stroke-linecap="round" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    return "".join(out)


def rice_mound_top(D, cx, cy, rx, ry, seed):
    """A mound of steamed rice seen from above."""
    pts = blob_pts(cx, cy, rx, ry, seed, 0.08, 18)
    out = [cast(D, cx + 6, cy + 6, rx * 1.05, ry * 1.05, strength=0.35, seed=seed)]
    out.append(painted(D, pts, RICE, seed, sdir=(0.6, 0.8), sk=0.2, angle=-30, n=10, inkw=1.2, inkop=0.4, hi=0.5))
    out.append(rice_grains(seed + 1, pts, int(rx * ry * 0.09)))
    return "".join(out)


def sandok(D, x0, y0, x1, y1, seed, pal=NARRA, bowl_r=18):
    """Wooden ladle / rice paddle (sandok) lying on the table: handle from (x0,y0) to the bowl at (x1,y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    L = math.hypot(x1 - x0, y1 - y0)
    out = [cast(D, (x0 + x1) / 2 + 6, (y0 + y1) / 2 + 8, L * 0.5, 10, strength=0.35, seed=seed)]
    hpts = [(x0 + nx * 5, y0 + ny * 5), (x1 - math.cos(a) * bowl_r + nx * 4, y1 - math.sin(a) * bowl_r + ny * 4),
            (x1 - math.cos(a) * bowl_r - nx * 4, y1 - math.sin(a) * bowl_r - ny * 4), (x0 - nx * 5, y0 - ny * 5)]
    out.append(painted(D, poly_pts(hpts, 14, seed, 0.3), pal, seed, sdir=(nx, ny), sk=0.25, angle=math.degrees(a), n=10, inkw=1.4, hi=0.4))
    bw = rot(blob_pts(x1, y1, bowl_r * 1.2, bowl_r, seed + 1, 0.05, 14), x1, y1, math.degrees(a))
    out.append(painted(D, bw, pal, seed + 1, sdir=(0.6, 0.8), sk=0.25, angle=math.degrees(a), n=8, inkw=1.4, hi=0.45))
    out.append(f'<path d="{blob(x1 + 2, y1 + 1, bowl_r * 0.8, bowl_r * 0.62, seed + 2, 0.08, 12, math.degrees(a))}" fill="{pal[2]}" opacity="0.45"/>')
    return "".join(out)


def calamansi(D, cx, cy, r, seed, cut=False):
    if not cut:
        out = [painted(D, blob_pts(cx, cy, r, r * 0.95, seed, 0.05, 12), ("#B8E07A", "#4E9A2E", "#1E5A1A"), seed, sdir=(0.6, 0.8), sk=0.22, n=4, inkw=1.0, hi=0.45)]
        out.append(f'<circle cx="{cx - r * 0.3:.1f}" cy="{cy - r * 0.35:.1f}" r="{r * 0.2:.1f}" fill="#FFFFFF" opacity="0.5"/>')
        return "".join(out)
    out = [f'<path d="{blob(cx, cy, r, r * 0.95, seed, 0.04, 14)}" fill="#3E8A2A"/>',
           f'<path d="{blob(cx, cy, r * 0.84, r * 0.8, seed + 1, 0.04, 14)}" fill="#FFF4B8"/>',
           f'<path d="{blob(cx, cy, r * 0.74, r * 0.7, seed + 2, 0.04, 14)}" fill="#F8C840"/>']
    for k in range(8):
        a = math.radians(k * 45 + 10)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * r * 0.72:.1f} {cy + math.sin(a) * r * 0.7:.1f}" stroke="#FFF4C8" stroke-width="1.4"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.1:.1f}" fill="#FFF4C8"/>')
    out.append(ink(blob(cx, cy, r, r * 0.95, seed, 0.04, 14), INK, 1.0, seed, 1, 0.5))
    return "".join(out)


def sili(D, x, y, L, ang, seed, pal=("#FF7A5A", "#D8241E", "#7A0A08")):
    """A small red chili (siling labuyo) with a green cap."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for i in range(9):
        t = i / 8
        w = L * 0.16 * (1 - t ** 1.6)
        bend = L * 0.12 * t * t
        pts.append((x + ux * L * t + nx * (w + bend), y + uy * L * t + ny * (w + bend)))
    for i in range(8, -1, -1):
        t = i / 8
        w = L * 0.16 * (1 - t ** 1.6)
        bend = L * 0.12 * t * t
        pts.append((x + ux * L * t + nx * (bend - w), y + uy * L * t + ny * (bend - w)))
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.2, angle=ang, n=4, inkw=1.0, hi=0.5)]
    out.append(taper([(x - ux * 2, y - uy * 2), (x - ux * L * 0.2 + nx * 3, y - uy * L * 0.2 + ny * 3)], 5, 2, "#3E7A2A"))
    out.append(taper([(x + ux * L * 0.2 - nx * L * 0.06, y + uy * L * 0.2 - ny * L * 0.06), (x + ux * L * 0.6 - nx * L * 0.02, y + uy * L * 0.6 - ny * L * 0.02)], 2, 1, "#FFFFFF", 0.6))
    return "".join(out)


def sawsawan(D, cx, cy, r, seed, sauce="#3A1A0A", glaze=WHITE, rim=BUGHAW, bits="soy"):
    """Small dipping-sauce saucer seen from above: soy-calamansi with chili, or spiced vinegar."""
    out = [cast(D, cx + 5, cy + 6, r * 1.05, r * 0.95, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.94, seed, 0.02, 20), glaze, seed, sdir=(0.6, 0.8), sk=0.12, n=6, inkw=1.4, hi=0.4))
    out.append(ink(blob(cx, cy, r * 0.86, r * 0.8, seed + 1, 0.02, 20), rim[1], 1.8, seed + 1, 1, 0.8))
    sd = blob(cx, cy, r * 0.68, r * 0.62, seed + 2, 0.03, 16)
    inner = [f'<path d="{sd}" fill="{sauce}"/>',
             f'<path d="{blob(cx - r * 0.2, cy - r * 0.2, r * 0.3, r * 0.14, seed + 3, 0.1, 10, -20)}" fill="#FFFFFF" opacity="0.35"/>']
    rnd = random.Random(seed)
    if bits == "soy":
        for _ in range(5):
            x, y = cx + rnd.uniform(-r, r) * 0.45, cy + rnd.uniform(-r, r) * 0.4
            inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.1:.1f}" ry="{r * 0.07:.1f}" fill="#D8281E" stroke="#7A0A06" stroke-width="0.8"/>')
    else:
        for _ in range(8):
            x, y = cx + rnd.uniform(-r, r) * 0.45, cy + rnd.uniform(-r, r) * 0.4
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 2.6):.1f}" fill="{rnd.choice(["#F2E2B0", "#D8281E", "#2A1A12"])}"/>')
    out.append(clipped(D, sd, inner))
    return "".join(out)


def wall(D, top, bot, seed, cols, h=600, angle=-80):
    return sky(D, [(0, top), (1, bot)], seed, h, cols, 110, angle=angle, sop=(0.06, 0.18))


def table_edge(y, col="#2A1408", op=0.55):
    return f'<rect y="{y - 4}" width="600" height="8" fill="{col}" opacity="{op}"/>'


# ================================================================ 1. adobo — the clay pot on a banig, everything around it
def chicken_piece(D, cx, cy, s, ang, seed, kind="thigh"):
    """A piece of adobo chicken: glossy soy-brown, darker crevices, shiny highlights; drumsticks show a bone knob."""
    pal = ("#C07A3A", "#7A3A16", "#2E1206")
    if kind == "drum":
        pts = rot([(cx - s, cy - s * 0.32), (cx - s * 0.2, cy - s * 0.48), (cx + s * 0.5, cy - s * 0.22), (cx + s * 0.95, cy - s * 0.1),
                   (cx + s * 0.95, cy + s * 0.12), (cx + s * 0.5, cy + s * 0.22), (cx - s * 0.2, cy + s * 0.5), (cx - s, cy + s * 0.3)], cx, cy, ang)
    else:
        pts = rot(blob_pts(cx, cy, s, s * 0.72, seed, 0.14, 14), cx, cy, ang)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.24, angle=ang - 30, n=12, sw=(1, 2.6), inkw=1.3, inkc="#1A0802", inkop=0.6, hi=0.45, hik=0.1)]
    d = smooth_closed(pts)
    rnd = random.Random(seed)
    inner = []
    for _ in range(4):
        x, y = cx + rnd.uniform(-s, s) * 0.5, cy + rnd.uniform(-s, s) * 0.3
        inner.append(taper([(x - s * 0.2, y), (x, y + 2), (x + s * 0.18, y - 1)], 3, 1, "#2A0E04", 0.5))
    for _ in range(5):
        x, y = cx + rnd.uniform(-s, s) * 0.55 - s * 0.15, cy + rnd.uniform(-s, 0) * 0.4
        inner.append(f'<path d="{blob(x, y, s * rnd.uniform(0.08, 0.16), s * 0.05, rnd.randint(0, 999), 0.2, 8, ang - 20)}" fill="#FFF0D8" opacity="{rnd.uniform(0.5, 0.85):.2f}"/>')
    out.append(clipped(D, d, inner))
    if kind == "drum":
        a = math.radians(ang)
        bx, by = cx + math.cos(a) * s * 1.08, cy + math.sin(a) * s * 1.08
        out.append(f'<path d="{blob(bx, by, s * 0.2, s * 0.16, seed + 9, 0.1, 10)}" fill="#F2E2C2" stroke="{INK}" stroke-width="1.1"/>')
        out.append(f'<circle cx="{bx - s * 0.05:.1f}" cy="{by - s * 0.05:.1f}" r="{s * 0.06:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("adobo")
def adobo():
    D = Doc2("ph-ad")
    # warm mustard wall, light from the upper left
    out = [wall(D, "#EDB85A", "#D8963A", 11, ["#F6CC78", "#C8822A", "#F2C068"])]
    out.append(soft_glow(D, 150, 160, 380, "#FFF0C0", 0.45))
    out.append(blooms(12, ["#F6CC78", "#C07A26"], 7, (0, 0, 600, 420), (90, 170), (0.08, 0.14)))
    # narra table
    out.append(wood_planks(D, 418, 600, 13, NARRA, 3))
    out.append(table_edge(418, "#2A1006"))
    # banig placemat in perspective
    mat = [(70, 446), (530, 446), (590, 600), (10, 600)]
    md = pd(mat)
    out.append(cast(D, 300, 452, 250, 14, strength=0.3, seed=14))
    out.append(banig(D, md, 15, cell=10, rot_=45))
    out.append(clipped(D, md, [f'<path d="{md}" fill="{D.lin([(0, "#3A1A06", 0.05), (1, "#3A1A06", 0.35)])}"/>']))
    out.append(ink(md, INK, 1.8, 16, 1, 0.6))
    # fringe at the front edge
    rnd = random.Random(17)
    for k in range(40):
        x = 20 + k * 14.5
        out.append(pline([(x, 597), (x + rnd.uniform(-3, 3), 604)], "#B89050", 2, k, 0.8, 1))
    # the pot
    cx, rim_y, rx = 318, 340, 132
    out.append(palayok(D, cx, rim_y, rx, 180, 18, ry=56))
    sd = ellipse_d(cx, rim_y + 2, rx - 4, 52)
    inner = [f'<path d="{sd}" fill="#3A1606"/>',
             f'<path d="{sd}" fill="{D.rad([(0, "#A85A22", 0.85), (0.6, "#6A2A0C", 0.6), (1, "#2A0C02", 0.8)], 0.4, 0.4, 0.7)}"/>']
    for _ in range(18):
        x, y = cx + rnd.uniform(-rx, rx) * 0.85, rim_y + rnd.uniform(-44, 44) * 0.8
        inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(4, 10):.1f}" ry="{rnd.uniform(1.5, 3):.1f}" fill="#E8A040" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out.append(clipped(D, sd, inner))
    pieces = [("thigh", -74, -16, 36, -12), ("drum", 50, -26, 42, 160), ("thigh", 2, -10, 38, 8), ("thigh", 96, 6, 32, 20),
              ("drum", -36, 22, 40, -20), ("thigh", -100, 16, 28, 30), ("thigh", 42, 26, 34, -10)]
    pc = []
    for kind, dx, dy, s, ang in pieces:
        pc.append(chicken_piece(D, cx + dx, rim_y + dy, s, ang, 30 + dx + dy, kind))
    for k, (dx, dy, ang) in enumerate(((-14, 30, 30), (78, -4, -40), (-92, -4, 70), (112, -14, 10), (16, -36, -10), (-60, 40, 20))):
        pc.append(garlic_clove(D, cx + dx, rim_y + dy, 9, ang, 60 + k, toasted=0.55))
    for k, (dx, dy, ang) in enumerate(((-30, -34, -20), (88, 4, 200), (-118, -8, 160), (6, 30, 15))):
        pc.append(bay_leaf(D, cx + dx, rim_y + dy, 42, ang, 70 + k, pal=("#A8A060", "#6E6A2E", "#3A3814")))
    pc.append(peppercorns(80, (cx - rx * 0.7, rim_y - 32, cx + rx * 0.7, rim_y + 32), 20))
    out.append(clipped(D, sd, pc))
    out.append(taper(ell_pts(cx, rim_y + 2, rx - 4, 52, 200, 340, 16), 3, 2, "#1A0802", 0.5))
    # steam
    out.append(steam(cx, rim_y - 40, 76, 81, "#FFFFFF", 3, 42, 9, 0.45))
    # rice bowl, garlic, bay leaves, ladle
    out.append(rice_bowl_side(D, 122, 456, 56, 62, 82, mound=1.0))
    out.append(steam(122, 396, 46, 83, "#FFFFFF", 2, 20, 5, 0.5))
    out.append(garlic_bulb(D, 500, 520, 26, 84))
    for k, (x, y) in enumerate(((452, 556), (480, 566))):
        out.append(garlic_clove(D, x, y, 11, -15 + k * 40, 85 + k))
    out.append(bay_leaf(D, 150, 560, 54, -10, 86))
    out.append(bay_leaf(D, 196, 548, 46, 25, 87, pal=("#C8C080", "#8E8A44", "#4E4C1E")))
    out.append(peppercorns(88, (240, 548, 300, 572), 7))
    out.append(sandok(D, 572, 412, 470, 470, 89))
    # lettering
    out.append(letters(D, 300, 160, "adobo", SERIF_IT, 136, "#4A1E0A", ["#6A2E12", "#2A0E04", "#8A4A22"], 90, max_w=400,
                       shadow="#FFF0C8", soff=(0.018, 0.03), angle=-40, hi="#C8865A"))
    out.append(ruled(300, 206, "WALANG TATALO", "#7A2E0E", font=JOS, size=22, ls=8, line_w=40, gap=14))
    return finish_b(D, out, 91)


# ================================================================ 2. halo-halo — the tall glass, every layer showing
def halo_glass_pts(cx, rim_y, bot_y, rx_top, rx_bot):
    return [(cx - rx_top, rim_y), (cx - rx_top * 0.97, rim_y + (bot_y - rim_y) * 0.4), (cx - rx_bot * 1.08, bot_y - 18), (cx - rx_bot * 0.8, bot_y),
            (cx + rx_bot * 0.8, bot_y), (cx + rx_bot * 1.08, bot_y - 18), (cx + rx_top * 0.97, rim_y + (bot_y - rim_y) * 0.4), (cx + rx_top, rim_y)]


def nata_cube(x, y, s, seed, col=("#FFFFFF", "#E8F0F0", "#A8C0C0")):
    rnd = random.Random(seed)
    a = rnd.uniform(-20, 20)
    pts = rot([(x - s, y - s), (x + s, y - s * 0.9), (x + s * 0.95, y + s), (x - s * 0.9, y + s * 0.95)], x, y, a)
    return (f'<path d="{smooth_closed(round_poly(pts, s * 0.3, 2))}" fill="{col[1]}" opacity="0.92" stroke="{col[2]}" stroke-width="1"/>'
            f'<path d="M {x - s * 0.5:.1f} {y - s * 0.4:.1f} l {s * 0.6:.1f} {-s * 0.1:.1f}" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>')


def oilcloth(D, y0, seed, base="#FFFDF6", check="#8AC8E8"):
    """Printed plastic tablecloth of a carinderia: pale check with little painted fruits."""
    rnd = random.Random(seed)
    c = 30
    tile = [f'<rect width="{2 * c}" height="{2 * c}" fill="{base}"/>',
            f'<rect width="{c}" height="{2 * c}" fill="{check}" opacity="0.35"/>',
            f'<rect width="{2 * c}" height="{c}" fill="{check}" opacity="0.35"/>']
    # a cherry pair and a little mango in each tile
    tile.append(f'<path d="M 12 8 q 4 -6 10 -6 M 17 10 q 2 -6 5 -8" stroke="#3E7A2A" stroke-width="1.4" fill="none"/>'
                f'<circle cx="11" cy="12" r="4.2" fill="#E0302A"/><circle cx="18" cy="13" r="4.2" fill="#C8241E"/>'
                f'<circle cx="10" cy="10.5" r="1.2" fill="#FFFFFF" opacity="0.8"/>')
    tile.append(f'<path d="M 40 40 q 8 -8 14 0 q 2 10 -8 12 q -8 0 -6 -12 Z" fill="#F6B623"/><path d="M 46 36 q 2 -4 6 -4" stroke="#3E7A2A" stroke-width="1.6" fill="none"/>'
                f'<path d="M 43 41 q 2 -3 5 -3" stroke="#FFF2B0" stroke-width="1.4" fill="none"/>')
    pat = D.pattern(2 * c, 2 * c, "".join(tile), transform="rotate(-6)")
    d = f"M -10 {y0} L 610 {y0} L 610 610 L -10 610 Z"
    out = [f'<path d="{d}" fill="{pat}"/>',
           f'<path d="{d}" fill="{D.lin([(0, "#2A3A5A", 0.18), (1, "#2A3A5A", 0)], 0, y0, 0, 600, "userSpaceOnUse")}"/>',
           strokes(D.nid(), d, (-40, y0, 600, 600), ["#FFFFFF", "#A8C8D8"], seed, n=30, angle=-2, length=(40, 120), width=(2, 5), opacity=(0.12, 0.3)),
           f'<path d="M -10 {y0} L 610 {y0}" stroke="#4A6A8A" stroke-width="3" opacity="0.6"/>']
    return "".join(out)


@design("halo-halo")
def halo_halo():
    D = Doc2("ph-hh")
    # sunny pastel stripes radiating behind the glass
    out = [paper(D.nid(), "#FCE8E4", "#8A5A6A", 21)]
    rays = []
    for k in range(24):
        a0, a1 = math.radians(k * 15), math.radians(k * 15 + 7.5)
        rays.append(f'<path d="M 300 380 L {300 + 700 * math.cos(a0):.1f} {380 + 700 * math.sin(a0):.1f} L {300 + 700 * math.cos(a1):.1f} {380 + 700 * math.sin(a1):.1f} Z" fill="#F6C8D8" opacity="0.55"/>')
    out.append("".join(rays))
    out.append(soft_glow(D, 300, 370, 300, "#FFFFFF", 0.75))
    out.append(blooms(22, ["#E8A8C8", "#B8A8E8", "#FFE0B0"], 7, (0, 0, 600, 600), (90, 170), (0.06, 0.12)))
    out.append(oilcloth(D, 494, 23))
    # the glass
    cx, rim_y, bot_y = 300, 330, 524
    H = bot_y - rim_y
    gp = halo_glass_pts(cx, rim_y, bot_y, 88, 64)
    gd = smooth_closed(densify(gp, 10))
    out.append(cast(D, cx + 16, bot_y + 2, 86, 11, strength=0.5, seed=24))
    rnd = random.Random(25)
    lay = []
    y_beans, y_nata, y_langka, y_ice = rim_y + H * 0.74, rim_y + H * 0.5, rim_y + H * 0.38, rim_y - 4
    # bottom: sweet red beans and white beans
    lay.append(f'<rect x="200" y="{y_beans:.0f}" width="200" height="80" fill="#8A2A1E"/>')
    for _ in range(40):
        x, y = rnd.uniform(220, 380), rnd.uniform(y_beans + 6, bot_y - 4)
        c = rnd.choice(["#A8382A", "#7A1E14", "#C04A30", "#F2E4C8"])
        lay.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6" ry="4.2" transform="rotate({rnd.uniform(-40, 40):.0f} {x:.1f} {y:.1f})" fill="{c}" stroke="#4A0E08" stroke-width="0.8"/>')
    # kaong (palm fruit, green and red), nata de coco cubes and sago in light syrup
    lay.append(f'<rect x="200" y="{y_nata:.0f}" width="200" height="{y_beans - y_nata + 2:.0f}" fill="#F4E6C8"/>')
    for _ in range(8):
        lay.append(nata_cube(rnd.uniform(228, 372), rnd.uniform(y_nata + 8, y_beans - 6), rnd.uniform(7, 9), rnd.randint(0, 999)))
    for _ in range(8):
        x, y = rnd.uniform(228, 372), rnd.uniform(y_nata + 8, y_beans - 6)
        c = rnd.choice([("#8AE07A", "#3EA83A"), ("#FF8A9A", "#D8304A")])
        lay.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="8" ry="5" fill="{c[0]}" opacity="0.92" stroke="{c[1]}" stroke-width="1.2"/><ellipse cx="{x - 2:.1f}" cy="{y - 2:.1f}" rx="3" ry="1.4" fill="#FFFFFF" opacity="0.8"/>')
    for _ in range(14):
        x, y = rnd.uniform(228, 372), rnd.uniform(y_nata + 6, y_beans - 4)
        lay.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="#FFFFFF" opacity="0.75" stroke="#C8B8A0" stroke-width="0.8"/>')
    # langka (jackfruit) strips
    lay.append(f'<rect x="200" y="{y_langka:.0f}" width="200" height="{y_nata - y_langka + 2:.0f}" fill="#F6C84A"/>')
    for k in range(8):
        x = 226 + k * 21 + rnd.uniform(-4, 4)
        lay.append(f'<path d="{blob(x, (y_langka + y_nata) / 2, 12, 7, 30 + k, 0.2, 10, rnd.uniform(-30, 30))}" fill="{rnd.choice(["#FFD860", "#F2B020"])}" stroke="#B87A0A" stroke-width="1"/>')
    # ube swirled into milky shaved ice
    lay.append(f'<rect x="200" y="{y_ice:.0f}" width="200" height="{y_langka - y_ice + 2:.0f}" fill="#F6F0F8"/>')
    lay.append(taper([(214, y_langka - 12), (250, y_langka - 30), (300, y_langka - 14), (350, y_langka - 36), (392, y_langka - 20)], 16, 9, "#9A6AC8", 0.75))
    lay.append(taper([(216, rim_y + 20), (266, rim_y + 12), (330, rim_y + 26), (388, rim_y + 12)], 10, 5, "#B48AD8", 0.6))
    for _ in range(36):
        x, y = rnd.uniform(214, 386), rnd.uniform(rim_y + 2, y_langka - 4)
        lay.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" opacity="0.8"/>')
    # condensation drops and glass tint
    for _ in range(18):
        x, y = rnd.uniform(222, 380), rnd.uniform(rim_y + 30, bot_y - 20)
        r = rnd.uniform(1.6, 3.2)
        lay.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.3:.1f}" fill="#FFFFFF" opacity="0.45"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.35:.1f}" fill="#FFFFFF" opacity="0.9"/>')
    lay.append(f'<path d="{gd}" fill="{D.lin([(0, "#FFFFFF", 0.38), (0.22, "#FFFFFF", 0), (0.78, "#5A6A8A", 0), (1, "#3A4A6A", 0.28)], 0, 0, 1, 0)}"/>')
    out.append(clipped(D, gd, lay))
    out.append(ink(gd, "#5A6A7A", 2.2, 26, 2, 0.75))
    out.append(taper([(cx - 70, rim_y + 18), (cx - 66, rim_y + 90), (cx - 50, bot_y - 22)], 7, 2, "#FFFFFF", 0.75))
    out.append(taper([(cx + 62, rim_y + 26), (cx + 58, rim_y + 80)], 4, 1, "#FFFFFF", 0.6))
    out.append(pline(ell_pts(cx, rim_y, 84, 9, 0, 180, 16), "#FFFFFF", 2, 27, 0.6, 1))
    # shaved-ice dome heaped above the rim
    dome = [(cx - 90, rim_y + 4), (cx - 86, rim_y - 22), (cx - 62, rim_y - 52), (cx - 26, rim_y - 68), (cx + 18, rim_y - 70), (cx + 58, rim_y - 56),
            (cx + 84, rim_y - 28), (cx + 92, rim_y + 4), (cx, rim_y + 14)]
    out.append(painted(D, dome, ("#FFFFFF", "#F2EEF8", "#B8B0D0"), 27, sdir=(0.6, 0.6), sk=0.15, angle=-60, n=40, slen=(6, 16), sw=(1, 3), inkw=1.4, inkop=0.45, hi=0.6))
    for i in range(70):
        a, r = rnd.uniform(3.4, 6.0), rnd.uniform(0.2, 0.92)
        x, y = cx + math.cos(a) * 84 * r, rim_y - 2 + math.sin(a) * 64 * r
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#FFFFFF", "#D8D0E8"])}" stroke-width="2" stroke-linecap="round" opacity="0.85"/>')
    # evaporated milk soaking down the ice and over the rim
    for x, L in ((cx - 74, 24), (cx - 28, 16), (cx + 56, 28)):
        out.append(taper([(x, rim_y - 4), (x + 1, rim_y + L * 0.5), (x, rim_y + L)], 8, 6, "#FFFDF4", 0.9))
    # leche flan slice, ube halaya, ube ice cream scoop, pinipig
    flan = [(cx + 10, rim_y - 64), (cx + 80, rim_y - 46), (cx + 76, rim_y - 22), (cx + 6, rim_y - 40)]
    out.append(painted(D, poly_pts(flan, 10, 28, 0.4), ("#FFE89A", "#F2BE3A", "#B87A0A"), 28, sdir=(0.3, 1), sk=0.25, angle=10, n=8, inkw=1.4, hi=0.5))
    cara = [(cx + 10, rim_y - 64), (cx + 80, rim_y - 46), (cx + 82, rim_y - 52), (cx + 12, rim_y - 72)]
    out.append(painted(D, poly_pts(cara, 10, 29, 0.4), ("#C8782A", "#8A420E", "#4A1E04"), 29, sdir=(0.3, 1), sk=0.2, angle=10, n=4, inkw=1.2, hi=0.5))
    out.append(taper([(cx + 22, rim_y - 56), (cx + 66, rim_y - 44)], 3, 1.5, "#FFF6C8", 0.8))
    out.append(painted(D, blob_pts(cx - 50, rim_y - 44, 28, 16, 31, 0.15, 12), UBE, 31, sdir=(0.5, 0.8), sk=0.25, angle=-30, n=10, inkw=1.4, hi=0.4))
    sy = rim_y - 94
    sc = blob_pts(cx - 8, sy, 40, 35, 32, 0.06, 18)
    sc = [(x, min(y, sy + 26 + 4 * math.sin(x / 5))) for x, y in sc]
    out.append(painted(D, sc, ("#D8B0F0", "#9A62D0", "#5A2A8A"), 32, sdir=(0.6, 0.7), sk=0.2, angle=-50, n=20, sw=(1.5, 3.5), inkw=1.6, hi=0.5, hik=0.1))
    for k in range(8):
        x = cx - 44 + k * 11
        out.append(f'<path d="{blob(x, sy + 26 + rnd.uniform(-2, 3), 7, 5, 40 + k, 0.2, 8)}" fill="#9A62D0"/>')
    out.append(taper([(cx - 32, sy - 18), (cx - 20, sy - 27), (cx - 2, sy - 30)], 2, 6, "#F4E6FF", 0.8))
    for i in range(30):
        a, r = rnd.uniform(3.5, 5.9), rnd.uniform(0.3, 0.95)
        x, y = cx + math.cos(a) * 80 * r, rim_y - 10 + math.sin(a) * 60 * r
        if math.hypot(x - cx + 8, y - sy) < 40:
            continue
        out.append(f'<path d="{blob(x, y, 3.2, 2.2, 50 + i, 0.25, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(["#8AA040", "#C8A050", "#A8B860"])}" stroke="#5A4A1A" stroke-width="0.6"/>')
    # the long spoon
    out.append(taper([(cx + 34, rim_y - 50), (cx + 120, rim_y - 146)], 7, 5, "#C8CED6"))
    out.append(taper([(cx + 36, rim_y - 55), (cx + 118, rim_y - 146)], 2, 1.4, "#FFFFFF", 0.9))
    out.append(ink(f"M {cx + 30:.1f} {rim_y - 48:.1f} L {cx + 116:.1f} {rim_y - 148:.1f} L {cx + 123:.1f} {rim_y - 143:.1f} L {cx + 38:.1f} {rim_y - 46:.1f}", "#5A6A7A", 1.2, 33, 1, 0.6))
    # toppings waiting on the side: a jar of ube halaya and a tin of leche flan
    jx, jb = 128, 520
    out.append(cast(D, jx + 10, jb, 52, 8, strength=0.4, seed=60))
    jar = [(jx - 40, jb - 74), (jx - 42, jb - 30), (jx - 36, jb), (jx + 36, jb), (jx + 42, jb - 30), (jx + 40, jb - 74)]
    out.append(painted(D, jar, ("#C8A0E8", "#7A48B0", "#3E1A66"), 61, sdir=(0.9, 0.3), sk=0.18, angle=-85, n=16, inkw=1.8, inkc="#3A2A4A", hi=0.35))
    out.append(clipped(D, smooth_closed(jar), [f'<path d="{smooth_closed(jar)}" fill="{D.lin([(0, "#FFFFFF", 0.4), (0.25, "#FFFFFF", 0), (1, "#2A1A3A", 0.2)], 0, 0, 1, 0)}"/>']))
    out.append(taper([(jx - 30, jb - 66), (jx - 32, jb - 14)], 5, 2, "#FFFFFF", 0.7))
    lbl = rect_pts(jx - 30, jb - 52, jx + 30, jb - 22, 10, 62, 0.4)
    out.append(painted(D, lbl, ("#FFFDF4", "#F6EAD0", "#C8B48A"), 62, sk=0.1, angle=0, n=4, inkw=1.1, hi=0.3))
    out.append(label(jx, jb - 32, "UBE", JOS, 15, "#5A2A86", ls=2))
    out.append(painted(D, rect_pts(jx - 44, jb - 92, jx + 44, jb - 72, 10, 63, 0.4), ("#F6D27A", "#D8A030", "#8A5A10"), 63, sdir=(0, 1), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.45))
    for k in range(9):
        out.append(pline([(jx - 38 + k * 9.5, jb - 90), (jx - 38 + k * 9.5, jb - 74)], "#8A5A10", 1.1, 64 + k, 0.5, 1))
    tx, ty = 474, 506
    out.append(cast(D, tx + 8, ty + 14, 74, 12, strength=0.4, seed=65))
    tin = ell_pts(tx, ty, 70, 22, 0, 360, 30)[:-1]
    out.append(painted(D, tin, STEEL, 66, sdir=(0.5, 0.9), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.5))
    fl = ell_pts(tx, ty - 6, 58, 16, 0, 360, 28)[:-1]
    out.append(painted(D, fl, ("#E8A050", "#B8641E", "#6A320A"), 67, sdir=(0.4, 0.9), sk=0.2, angle=0, n=10, inkw=1.2, hi=0.5))
    out.append(f'<path d="{blob(tx - 16, ty - 10, 22, 5, 68, 0.2, 10)}" fill="#FFD890" opacity="0.6"/>')
    cut = [(tx + 6, ty - 10), (tx + 52, ty - 12), (tx + 50, ty + 2), (tx + 6, ty + 4)]
    out.append(f'<path d="{smooth_closed(cut)}" fill="#C8CED6"/>')
    out.append(painted(D, poly_pts([(tx + 10, ty - 30), (tx + 58, ty - 34), (tx + 60, ty - 20), (tx + 12, ty - 16)], 8, 69, 0.3), ("#FFE89A", "#F2BE3A", "#B87A0A"), 69, sdir=(0.3, 1), sk=0.25, angle=0, n=5, inkw=1.2, hi=0.5))
    out.append(painted(D, poly_pts([(tx + 10, ty - 30), (tx + 58, ty - 34), (tx + 58, ty - 38), (tx + 10, ty - 35)], 8, 70, 0.3), ("#C8782A", "#8A420E", "#4A1E04"), 70, sk=0.1, angle=0, n=2, inkw=1, hi=0.4))
    for x, y, s in ((96, 300, 12), (512, 250, 10), (500, 410, 9), (88, 404, 8)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 128, "halo-halo", SERIF_IT, 124, "#5A2A86", ["#7A42A8", "#3A145E", "#9A62C8"], 41, max_w=440,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#E0C0F8"))
    out.append(ruled(300, 172, "HALUIN BAGO KAININ", "#C8306A", font=JOS, size=20, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 42, "#5A2A4A")


# ================================================================ 3. kain na! — a boodle fight laid out on banana leaves
def leaf_runner(D, y0, y1, seed, x0=-30, x1=630, pal=SAGING, tear=True):
    """A strip of banana leaf seen from above: midrib along one edge, fine parallel veins across, torn ends."""
    rnd = random.Random(seed)
    top = [(x0 + (x1 - x0) * i / 24, y0 + rnd.uniform(-4, 4)) for i in range(25)]
    bot = [(x0 + (x1 - x0) * i / 24, y1 + rnd.uniform(-5, 5)) for i in range(25)][::-1]
    pts = top + bot
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    inner = [f'<path d="{d}" fill="{D.lin([(0, pal[0], 0.45), (0.5, pal[1], 0), (1, pal[2], 0.45)], 0, y0, 0, y1, "userSpaceOnUse")}"/>']
    x = x0
    while x < x1:
        x += rnd.uniform(5, 9)
        sk = rnd.uniform(-4, 4)
        inner.append(f'<path d="M {x:.1f} {y0 - 6} L {x + sk:.1f} {y1 + 6}" stroke="{rnd.choice([pal[0], pal[2], lt(pal[0], 0.2)])}" stroke-width="{rnd.uniform(0.8, 1.8):.1f}" opacity="{rnd.uniform(0.18, 0.45):.2f}"/>')
    inner.append(strokes(D.nid(), d, (x0, y0, x1, y1), [pal[0], pal[2]], seed, n=int((x1 - x0) / 10), angle=-88, length=(10, 30), width=(1, 3), opacity=(0.1, 0.3)))
    # waxy sheen
    for _ in range(4):
        sx = rnd.uniform(x0 + 40, x1 - 40)
        inner.append(f'<path d="{blob(sx, (y0 + y1) / 2, rnd.uniform(40, 90), (y1 - y0) * 0.28, rnd.randint(0, 999), 0.2, 12)}" fill="#FFFFFF" opacity="0.07"/>')
    out.append(clipped(D, d, inner))
    # midrib along the top edge
    out.append(taper([(x0, y0 + 5), ((x0 + x1) / 2, y0 + 7), (x1, y0 + 4)], 7, 7, lt(pal[0], 0.35), 0.85))
    out.append(pline([(x0, y0 + 9), ((x0 + x1) / 2, y0 + 11), (x1, y0 + 8)], pal[2], 1.2, seed, 0.5, 1))
    if tear:
        for _ in range(3):
            tx = rnd.uniform(x0 + 60, x1 - 60)
            out.append(taper([(tx, y1 + 4), (tx + rnd.uniform(-3, 3), y1 - (y1 - y0) * rnd.uniform(0.25, 0.5))], 4, 0.5, "#2A1A0E", 0.6))
    out.append(ink(d, "#1E3A14", 1.4, seed, 1, 0.5))
    return "".join(out)


def grilled_fish(D, cx, cy, L, ang, seed, pal=("#C8B898", "#8A7A5E", "#3E3426")):
    """Whole grilled fish (inihaw) from above: charred skin, grill stripes, tail fan, cooked white eye, stuffing at the belly."""
    pts = []
    for i in range(15):
        t = i / 14
        w = L * 0.2 * math.sin(math.pi * min(1, t * 1.15)) ** 0.75 * (1 - 0.3 * t)
        pts.append((cx - L * 0.5 + L * 0.8 * t, cy - w))
    for i in range(14, -1, -1):
        t = i / 14
        w = L * 0.2 * math.sin(math.pi * min(1, t * 1.15)) ** 0.75 * (1 - 0.3 * t)
        pts.append((cx - L * 0.5 + L * 0.8 * t, cy + w))
    pts = rot(pts, cx, cy, ang)
    tail = rot([(cx + L * 0.28, cy), (cx + L * 0.5, cy - L * 0.14), (cx + L * 0.46, cy), (cx + L * 0.5, cy + L * 0.14)], cx, cy, ang)
    out = [cast(D, cx + 6, cy + 8, L * 0.55, L * 0.2, strength=0.4, seed=seed)]
    out.append(painted(D, tail, ("#9A7A4A", "#5A3E1E", "#2A1A0A"), seed + 1, sk=0.2, n=6, inkw=1.4, hi=0.3))
    out.append(painted(D, pts, pal, seed, sdir=(0.4, 0.9), sk=0.22, angle=ang, n=20, inkw=1.8, hi=0.4))
    d = smooth_closed(pts)
    inner = []
    a = math.radians(ang)
    for k in range(-3, 4):
        bx, by = cx + math.cos(a) * k * L * 0.11, cy + math.sin(a) * k * L * 0.11
        inner.append(taper(rot([(bx - L * 0.06, by - L * 0.22), (bx + L * 0.06, by + L * 0.22)], bx, by, ang), 6, 4, "#1E1208", 0.75))
    inner.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.25), (0.5, "#FFFFFF", 0), (1, "#000000", 0.3)])}"/>')
    rnd = random.Random(seed)
    for _ in range(14):
        x, y = cx + rnd.uniform(-L, L) * 0.35, cy + rnd.uniform(-L, L) * 0.1
        inner.append(f'<path d="{blob(x, y, rnd.uniform(3, 8), rnd.uniform(1.5, 3), rnd.randint(0, 999), 0.3, 8)}" fill="#1A0E06" opacity="0.5"/>')
    out.append(clipped(D, d, inner))
    # gill line, eye, stuffing of tomato and onion at the belly slit
    hx, hy = cx - math.cos(a) * L * 0.3, cy - math.sin(a) * L * 0.3
    out.append(pline(rot([(hx, hy - L * 0.14), (hx + L * 0.04, hy), (hx, hy + L * 0.14)], hx, hy, ang), "#2A1A0A", 2, seed, 0.8, 1))
    ex, ey = cx - math.cos(a) * L * 0.38 - math.sin(a) * L * 0.05, cy - math.sin(a) * L * 0.38 + math.cos(a) * L * 0.05
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{L * 0.035:.1f}" fill="#F4EEE0" stroke="#2A1A0A" stroke-width="1.2"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{L * 0.014:.1f}" fill="#4A3A2A"/>')
    for k in range(4):
        sx, sy = cx + math.cos(a) * (-0.1 + k * 0.08) * L + math.sin(a) * L * 0.17, cy + math.sin(a) * (-0.1 + k * 0.08) * L - math.cos(a) * L * 0.17
        out.append(f'<path d="{blob(sx, sy, 6, 4, seed + 10 + k, 0.2, 8)}" fill="{["#E0402A", "#F2E2F0", "#C8302A", "#E8D0E8"][k]}" stroke="#5A1A0A" stroke-width="0.8"/>')
    return "".join(out)


def lechon_chunk(D, x, y, w, h, seed, ang=0):
    """A chunk of lechon kawali: blistered crackling on top, a layer of fat, juicy meat below (3/4 from above)."""
    sk = rot(round_poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2 + 2), (x + w / 2 + 1, y), (x - w / 2 - 1, y + 1)], 6, 3), x, y, ang)
    fat = rot(rect_pts(x - w / 2, y - h * 0.02, x + w / 2, y + h * 0.12, 8, seed + 1, 0.5), x, y, ang)
    meat = rot(round_poly([(x - w / 2, y + h * 0.1), (x + w / 2, y + h * 0.1), (x + w / 2 - 2, y + h / 2), (x - w / 2 + 2, y + h / 2)], 4, 3), x, y, ang)
    out = [cast(D, x + 4, y + h * 0.5, w * 0.6, h * 0.18, strength=0.4, seed=seed)]
    out.append(painted(D, meat, ("#D89A6A", "#A8643A", "#5A2A12"), seed + 2, sk=0.25, angle=-80, n=8, inkw=1.1, hi=0.3))
    out.append(painted(D, fat, ("#FFF6E0", "#F2DCB4", "#C8A878"), seed + 1, sk=0.15, angle=0, n=4, inkw=1.0, hi=0.4))
    out.append(painted(D, sk, ("#F0B060", "#C0702A", "#6A300A"), seed, sk=0.25, angle=0, n=8, inkw=1.3, inkc="#4A1A04", hi=0.5))
    rnd = random.Random(seed)
    bub = []
    for _ in range(int(w * 0.5)):
        bx, by = x + rnd.uniform(-w, w) * 0.45, y - h * 0.3 + rnd.uniform(-h, h) * 0.17
        r = rnd.uniform(1.4, 3.2)
        bub.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="#FFE8A8" opacity="0.8"/><circle cx="{bx + r * 0.4:.1f}" cy="{by + r * 0.4:.1f}" r="{r * 0.6:.1f}" fill="#A8580E" opacity="0.5"/>')
    out.append(clipped(D, smooth_closed(sk), bub))
    return "".join(out)


def prawn(D, cx, cy, s, ang, seed, pal=("#FFA070", "#E8502A", "#8A1E0A")):
    """Grilled prawn from above: curled body of shell segments, fanned tail, head with long feelers."""
    out = []
    segs = 6
    for k in range(segs):
        t = k / (segs - 1)
        a = math.radians(ang - 70 + t * 150)
        R = s * 0.6
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
        r = s * (0.3 - 0.12 * t)
        out.append(painted(D, rot(blob_pts(x, y, r * 1.1, r * 0.8, seed + k, 0.06, 10), x, y, math.degrees(a) + 90), pal, seed + k, sk=0.25, n=3, inkw=1.0, inkop=0.6, hi=0.5))
        out.append(f'<circle cx="{x + r * 0.2:.1f}" cy="{y:.1f}" r="{r * 0.25:.1f}" fill="#2A0E04" opacity="0.4"/>')
    a = math.radians(ang + 80)
    tx, ty = cx + math.cos(a) * s * 0.66, cy + math.sin(a) * s * 0.66
    for k in (-1, 0, 1):
        tp = rot([(tx, ty), (tx + s * 0.22, ty + k * s * 0.12 - s * 0.06), (tx + s * 0.3, ty + k * s * 0.16), (tx + s * 0.2, ty + k * s * 0.12 + s * 0.06)], tx, ty, math.degrees(a))
        out.append(f'<path d="{smooth_closed(tp)}" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1"/>')
    a = math.radians(ang - 80)
    hx, hy = cx + math.cos(a) * s * 0.6, cy + math.sin(a) * s * 0.6
    out.append(painted(D, rot(blob_pts(hx, hy, s * 0.36, s * 0.24, seed + 9, 0.08, 12), hx, hy, math.degrees(a)), ("#FF9A60", "#D8401E", "#7A1606"), seed + 9, sk=0.25, n=4, inkw=1.1, hi=0.45))
    for k in (-1, 1):
        out.append(pline([(hx, hy), (hx + math.cos(a + k * 0.5) * s * 0.8, hy + math.sin(a + k * 0.5) * s * 0.8), (hx + math.cos(a + k * 0.3) * s * 1.4, hy + math.sin(a + k * 0.3) * s * 1.4)], pal[2], 1.2, seed + k, 0.8, 1))
    out.append(f'<circle cx="{hx + math.cos(a) * s * 0.2:.1f}" cy="{hy + math.sin(a) * s * 0.2:.1f}" r="2.2" fill="#1A0804"/>')
    # char dabs
    rnd = random.Random(seed)
    for _ in range(5):
        aa = math.radians(ang - 60 + rnd.uniform(0, 130))
        out.append(f'<path d="{blob(cx + math.cos(aa) * s * 0.6, cy + math.sin(aa) * s * 0.6, 3, 1.6, rnd.randint(0, 99), 0.3, 6)}" fill="#2A0E04" opacity="0.55"/>')
    return "".join(out)


def salted_egg(D, cx, cy, r, seed, ang=0):
    """Half a red salted duck egg (itlog na maalat): red-dyed shell rim, white, deep orange yolk."""
    out = [cast(D, cx + 4, cy + 5, r * 1.1, r * 0.8, strength=0.35, seed=seed)]
    shell = rot(blob_pts(cx, cy, r * 1.1, r * 0.8, seed, 0.04, 16), cx, cy, ang)
    out.append(painted(D, shell, ("#F2706A", "#C8283A", "#7A0E1A"), seed, sk=0.2, n=4, inkw=1.2, hi=0.3))
    out.append(f'<path d="{smooth_closed(rot(blob_pts(cx, cy, r * 0.95, r * 0.68, seed + 1, 0.04, 16), cx, cy, ang))}" fill="#FBF6EC"/>')
    out.append(painted(D, rot(blob_pts(cx + r * 0.05, cy, r * 0.52, r * 0.42, seed + 2, 0.08, 14), cx, cy, ang), ("#FFB04A", "#E8701A", "#A83E06"), seed + 2, sk=0.25, n=4, inkw=0.8, inkop=0.4, hi=0.5))
    out.append(f'<circle cx="{cx - r * 0.12:.1f}" cy="{cy - r * 0.12:.1f}" r="{r * 0.12:.1f}" fill="#FFE0A0" opacity="0.7"/>')
    return "".join(out)


def tomato_wedge(D, cx, cy, s, ang, seed):
    pts = rot([(cx - s, cy), (cx - s * 0.6, cy - s * 0.55), (cx + s * 0.4, cy - s * 0.6), (cx + s, cy - s * 0.1), (cx + s * 0.2, cy + s * 0.25)], cx, cy, ang)
    out = [painted(D, pts, ("#FF8A6A", "#E0302A", "#8A100A"), seed, sk=0.2, n=4, inkw=1.0, hi=0.45)]
    inner = rot(blob_pts(cx, cy - s * 0.25, s * 0.55, s * 0.22, seed + 1, 0.1, 10), cx, cy, ang)
    out.append(f'<path d="{smooth_closed(inner)}" fill="#F8A070" opacity="0.8"/>')
    rnd = random.Random(seed)
    for _ in range(4):
        x, y = cx + rnd.uniform(-s, s) * 0.4, cy - s * 0.25 + rnd.uniform(-3, 3)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.2" ry="1.4" fill="#FFF0B0"/>')
    return "".join(out)


def bbq_stick(D, x0, y0, x1, y1, seed, n=5):
    """Pork barbecue on a bamboo stick: glazed, charred-edged pieces."""
    out = [cast(D, (x0 + x1) / 2 + 5, (y0 + y1) / 2 + 8, math.hypot(x1 - x0, y1 - y0) * 0.5, 12, strength=0.35, seed=seed)]
    out.append(taper([(x0, y0), (x1, y1)], 4, 3, "#D8B070"))
    out.append(pline([(x0, y0), (x1, y1)], "#8A6A30", 1, seed, 0.6, 1))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    for k in range(n):
        t = 0.2 + 0.74 * k / (n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        pts = rot(blob_pts(x, y, 13, 16, seed + k, 0.12, 12), x, y, ang)
        out.append(painted(D, pts, ("#D86A3A", "#9A2E14", "#4A0E04"), seed + k, sdir=(0.5, 0.8), sk=0.28, angle=ang + 90, n=6, inkw=1.2, inkc="#2A0804", hi=0.5, hik=0.12))
        out.append(f'<path d="{blob(x - 4, y - 5, 4, 2, seed + k + 30, 0.2, 6)}" fill="#FFE0C0" opacity="0.7"/>')
        out.append(f'<path d="{blob(x + 6, y + 6, 4, 2.5, seed + k + 40, 0.3, 6)}" fill="#1A0402" opacity="0.6"/>')
    return "".join(out)


def mango_cheek(D, cx, cy, s, ang, seed, scored=True):
    pts = rot(blob_pts(cx, cy, s, s * 0.62, seed, 0.06, 16), cx, cy, ang)
    out = [cast(D, cx + 4, cy + 6, s, s * 0.6, strength=0.3, seed=seed)]
    out.append(painted(D, pts, ("#FFE98A", "#F5B623", "#C07A0A"), seed, sdir=(0.5, 0.8), sk=0.2, angle=ang, n=8, inkw=1.4, inkc="#7A4A0A", hi=0.5))
    if scored:
        lines = []
        for k in range(-3, 4):
            lines.append(pline(rot([(cx + k * s * 0.24 - s * 0.4, cy - s * 0.7), (cx + k * s * 0.24 + s * 0.4, cy + s * 0.7)], cx, cy, ang), "#D88A10", 1.4, seed + k, 0.6, 1))
            lines.append(pline(rot([(cx + k * s * 0.24 + s * 0.4, cy - s * 0.7), (cx + k * s * 0.24 - s * 0.4, cy + s * 0.7)], cx, cy, ang), "#D88A10", 1.4, seed + k + 9, 0.6, 1))
        out.append(clipped(D, smooth_closed(pts), lines))
    return "".join(out)


def eggplant_half(D, cx, cy, L, ang, seed):
    """Grilled eggplant split open (for ensaladang talong): charred purple skin, smoky flesh, a tomato-onion topping."""
    pts = []
    for i in range(13):
        t = i / 12
        w = L * 0.14 * math.sin(math.pi * t) ** 0.6 * (0.7 + 0.3 * t)
        pts.append((cx - L / 2 + L * t, cy - w))
    for i in range(12, -1, -1):
        t = i / 12
        w = L * 0.14 * math.sin(math.pi * t) ** 0.6 * (0.7 + 0.3 * t)
        pts.append((cx - L / 2 + L * t, cy + w))
    pts = rot(pts, cx, cy, ang)
    out = [cast(D, cx + 5, cy + 8, L * 0.5, L * 0.12, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#8A5A8A", "#4A2250", "#1E0A22"), seed, sk=0.2, angle=ang, n=8, inkw=1.4, hi=0.35))
    fl = rot(blob_pts(cx + L * 0.04, cy, L * 0.4, L * 0.09, seed + 1, 0.12, 14), cx, cy, ang)
    out.append(painted(D, fl, ("#E8D8A0", "#B8A060", "#6A5A2A"), seed + 1, sk=0.2, angle=ang, n=10, inkw=0.8, inkop=0.4, hi=0.4))
    rnd = random.Random(seed)
    for _ in range(10):
        x, y = cx + rnd.uniform(-L, L) * 0.32, cy + rnd.uniform(-L, L) * 0.05
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 5), rnd.uniform(2, 3), rnd.randint(0, 999), 0.3, 6)}" fill="{rnd.choice(["#E0402A", "#F2E2F0", "#E8C8E0"])}" stroke="#5A1A0A" stroke-width="0.6"/>')
    a = math.radians(ang)
    sx, sy = cx - math.cos(a) * L * 0.5, cy - math.sin(a) * L * 0.5
    out.append(painted(D, rot(blob_pts(sx - 6, sy, 12, 9, seed + 2, 0.1, 10), sx, sy, ang), ("#9AC070", "#4E7A2E", "#22401A"), seed + 2, sk=0.2, n=3, inkw=1, hi=0.4))
    return "".join(out)


def kawali_chunk(D, cx, cy, r, seed):
    """Lechon kawali from above: a chunky cube of pork with blistered, glassy golden crackling and a sliver of
    juicy meat showing on the cut side."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.86, seed, 0.12, 9)
    out = [cast(D, cx + 4, cy + 6, r * 1.05, r * 0.9, strength=0.4, seed=seed)]
    side = [(x, y + r * 0.32) for x, y in pts]
    out.append(painted(D, side, ("#D89A6A", "#A8643A", "#5A2A12"), seed + 1, sk=0.25, n=5, inkw=1.2, inkc="#3A1206", hi=0.3))
    out.append(clipped(D, smooth_closed(side), [f'<path d="{smooth_closed([(x, y + r * 0.12) for x, y in pts])}" fill="#FBEAD0"/>']))
    out.append(painted(D, pts, ("#FFD488", "#D8862E", "#7A3A0A"), seed, sdir=(0.5, 0.8), sk=0.22, n=8, inkw=1.4, inkc="#4A1A04", hi=0.5))
    bub = []
    for _ in range(int(r * 1.4)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.85
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.86
        b = rnd.uniform(1.4, 3.4)
        bub.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{b:.1f}" fill="#FFF0B8" opacity="0.85"/><circle cx="{x + b * 0.35:.1f}" cy="{y + b * 0.35:.1f}" r="{b * 0.55:.1f}" fill="#A85410" opacity="0.55"/>')
    out.append(clipped(D, smooth_closed(pts), bub))
    return "".join(out)


def liempo_slice(D, cx, cy, L, w, seed, ang):
    """A slice of grilled pork belly (inihaw na liempo): striped meat and fat, charred edges and grill marks."""
    a = math.radians(ang)
    pts = rot(round_poly([(cx - L / 2, cy - w / 2), (cx + L / 2, cy - w / 2 + 2), (cx + L / 2 - 2, cy + w / 2), (cx - L / 2 + 3, cy + w / 2 - 1)], 6, 3), cx, cy, ang)
    d = smooth_closed(pts)
    out = [cast(D, cx + 5, cy + 6, L * 0.5, w * 0.7, strength=0.35, seed=seed), f'<path d="{d}" fill="#B8643A"/>']
    rnd = random.Random(seed)
    lay = []
    for k, (o, th, col) in enumerate(((-0.4, 0.22, "#7A2E0E"), (-0.18, 0.16, "#FBE8C8"), (0.04, 0.26, "#D07848"), (0.26, 0.12, "#F6DEB8"), (0.42, 0.18, "#B8582A"))):
        y0 = cy + o * w
        band = rot([(cx - L, y0 - th * w / 2), (cx + L, y0 - th * w / 2 + rnd.uniform(-1, 1)), (cx + L, y0 + th * w / 2), (cx - L, y0 + th * w / 2)], cx, cy, ang)
        lay.append(f'<path d="{smooth_closed(band)}" fill="{col}"/>')
    for k in range(-3, 4):
        bx, by = cx + math.cos(a) * k * L * 0.14, cy + math.sin(a) * k * L * 0.14
        lay.append(taper(rot([(bx - 6, by - w * 0.6), (bx + 6, by + w * 0.6)], bx, by, ang), 4, 3, "#2A0E04", 0.65))
    lay.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.25), (0.5, "#FFFFFF", 0), (1, "#000000", 0.25)])}"/>')
    out.append(clipped(D, d, lay))
    out.append(ink(d, "#3A1206", 1.3, seed, 1, 0.7))
    return "".join(out)


@design("kain-na")
def kain_na():
    D = Doc2("ph-kn")
    out = [wood_planks(D, 0, 600, 101, ("#8A5A36", "#5A341A", "#2A1408"), 6)]
    out.append(soft_glow(D, 300, 130, 300, "#FFD890", 0.25))
    # three overlapping strips of banana leaf down the table
    out.append(leaf_runner(D, 228, 360, 102, pal=("#A8DC7A", "#4EA040", "#22602A")))
    out.append(leaf_runner(D, 340, 480, 103, pal=("#9AD070", "#3E9436", "#1A5822")))
    out.append(leaf_runner(D, 462, 640, 104, pal=("#A8DC7A", "#48A03E", "#1E5E26")))
    # the long ridge of rice down the middle
    rnd = random.Random(105)
    out.append(cast(D, 300, 430, 270, 20, strength=0.35, seed=106))
    for k in range(9):
        x = 74 + k * 56 + rnd.uniform(-4, 4)
        out.append(rice_mound_top(D, x, 404 + rnd.uniform(-5, 5), 40, 32, 107 + k))
    # top row: grilled fish, lechon kawali, grilled prawns
    out.append(grilled_fish(D, 160, 300, 210, -4, 110))
    for k, (x, y, r) in enumerate(((316, 270, 24), (360, 282, 26), (300, 318, 25), (346, 328, 24), (398, 262, 22), (404, 312, 24), (380, 352, 20))):
        out.append(kawali_chunk(D, x, y, r, 120 + k))
    for k, (x, y, a) in enumerate(((470, 280, 20), (510, 318, -10), (452, 336, 40))):
        out.append(prawn(D, x, y, 30, a, 130 + k))
    # bottom row: salted eggs and tomatoes, barbecue sticks, grilled eggplant, mango cheeks; calamansi everywhere
    for k, (x, y, a) in enumerate(((98, 482, -10), (146, 508, 20))):
        out.append(salted_egg(D, x, y, 28, 140 + k, a))
    for k, (x, y, a) in enumerate(((104, 528, 30), (186, 472, -40), (196, 528, 80), (150, 460, 10))):
        out.append(tomato_wedge(D, x, y, 17, a, 150 + k))
    out.append(eggplant_half(D, 300, 470, 120, -8, 159))
    out.append(bbq_stick(D, 232, 540, 384, 494, 160))
    out.append(bbq_stick(D, 252, 556, 400, 516, 161))
    out.append(mango_cheek(D, 456, 478, 40, -20, 170))
    out.append(mango_cheek(D, 498, 524, 36, 15, 171))
    for k, (x, y) in enumerate(((240, 444), (424, 446), (532, 452), (82, 360), (418, 548), (544, 372), (224, 352))):
        out.append(calamansi(D, x, y, 10, 180 + k, cut=k % 2 == 0))
    out.append(sawsawan(D, 536, 248, 28, 190, bits="soy"))
    out.append(sili(D, 66, 244, 30, 20, 191))
    out.append(sili(D, 78, 260, 26, -10, 192))
    # lettering on the wood
    out.append(letters(D, 300, 140, "Kain na!", SERIF_IT, 138, "#FFF2D8", ["#FFFFFF", "#F8DCB0", "#FFE8C8"], 193, max_w=440,
                       shadow="#1A0A04", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 190, "TARA, SALO-SALO TAYO", "#F6C84A", font=JOS, size=20, ls=5, line_w=30, gap=12))
    return finish_b(D, out, 194)


# ================================================================ 4. maligayang pasko — a capiz parol glowing over the town
def parol(D, cx, cy, R, seed, body=PULA, inner=ARAW, accent=("#7AD08A", "#2E9A4E", "#145A2A"), tails=True, ring=True, glow=True):
    """Star lantern (parol): five-point bamboo-framed star of translucent paper / capiz, glowing from within,
    a hoop with little star tips, and two fringed tails."""
    out = []
    if glow:
        out.append(soft_glow(D, cx, cy, R * 2.6, "#FFD27A", 0.55))
        out.append(soft_glow(D, cx, cy, R * 1.4, "#FFF2C0", 0.5))
    if tails:
        for sg in (-1, 1):
            a = math.radians(90 + sg * 36)
            sx, sy = cx + math.cos(a) * R * 0.62, cy + math.sin(a) * R * 0.62
            path = [(sx, sy), (sx + sg * R * 0.18, sy + R * 0.5), (sx + sg * R * 0.05, sy + R * 0.95), (sx + sg * R * 0.22, sy + R * 1.35)]
            cp = catmull(path, 6)
            for k in range(len(cp) - 1):
                (x0, y0), (x1, y1) = cp[k], cp[k + 1]
                c = [body[1], inner[1], "#FFFFFF"][k % 3]
                out.append(taper([(x0, y0), (x1, y1)], R * 0.16 * (1 - k / len(cp) * 0.5), R * 0.14 * (1 - k / len(cp) * 0.5), c, 0.95))
                for j in (-1, 1):
                    out.append(f'<path d="M {x0:.1f} {y0:.1f} l {j * R * 0.12:.1f} {R * 0.03:.1f}" stroke="{c}" stroke-width="1.6" opacity="0.8"/>')
            out.append(pline(cp, INK, 1, seed + sg, 0.4, 1))
    if ring:
        rr = R * 1.18
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{body[2]}" stroke-width="{R * 0.07:.1f}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{inner[0]}" stroke-width="{R * 0.035:.1f}" stroke-dasharray="{R * 0.08:.1f} {R * 0.06:.1f}"/>')
        for k in range(10):
            a = math.radians(-90 + 18 + k * 36)
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            out.append(painted(D, [(x + math.cos(a) * R * 0.14, y + math.sin(a) * R * 0.14), (x + math.cos(a + 1.6) * R * 0.06, y + math.sin(a + 1.6) * R * 0.06),
                                   (x - math.cos(a) * R * 0.05, y - math.sin(a) * R * 0.05), (x + math.cos(a - 1.6) * R * 0.06, y + math.sin(a - 1.6) * R * 0.06)],
                               inner, seed + k, sk=0.1, n=2, inkw=0.8, hi=0.5))
    # the star: outer points, then layered inner star and a sun-flower centre
    def star(r_out, r_in, rot_=-90):
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot_ + i * 36)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts
    outer = star(R, R * 0.48)
    od = smooth_closed(round_poly(outer, R * 0.04, 2))
    out.append(f'<path d="{od}" fill="{body[1]}"/>')
    inn = [f'<path d="{od}" fill="{D.rad([(0, "#FFF6C8", 1), (0.35, body[0], 0.85), (1, body[2], 0.6)], 0.5, 0.5, 0.6)}"/>']
    # frame ribs from the centre to each point
    for i in range(10):
        a = math.radians(-90 + i * 36)
        r = R if i % 2 == 0 else R * 0.48
        inn.append(f'<path d="M {cx} {cy} L {cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}" stroke="{body[2]}" stroke-width="{R * 0.02:.1f}" opacity="0.55"/>')
    out.append(clipped(D, od, inn))
    out.append(ink(od, "#4A0A06", max(1.6, R * 0.025), seed, 2, 0.8))
    mid = star(R * 0.7, R * 0.34)
    md = smooth_closed(round_poly(mid, R * 0.03, 2))
    out.append(f'<path d="{md}" fill="{D.rad([(0, "#FFFFFF", 1), (0.4, inner[0], 1), (1, inner[1], 1)], 0.5, 0.5, 0.6)}"/>')
    out.append(ink(md, inner[2], max(1.2, R * 0.018), seed + 1, 1, 0.7))
    # capiz petals around the centre
    for k in range(5):
        a = math.radians(-90 + k * 72)
        x, y = cx + math.cos(a) * R * 0.3, cy + math.sin(a) * R * 0.3
        out.append(painted(D, rot(blob_pts(x, y, R * 0.16, R * 0.08, seed + 20 + k, 0.05, 12), x, y, math.degrees(a)), accent, seed + 20 + k, sk=0.15, n=3, inkw=1, hi=0.5))
        a2 = math.radians(-54 + k * 72)
        x2, y2 = cx + math.cos(a2) * R * 0.26, cy + math.sin(a2) * R * 0.26
        out.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="{R * 0.05:.1f}" fill="{body[1]}" stroke="{body[2]}" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.14:.1f}" fill="{D.rad([(0, "#FFFFFF", 1), (0.6, "#FFF2A0", 1), (1, inner[1], 1)])}" stroke="{inner[2]}" stroke-width="1.4"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.07:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def parol_small(D, cx, cy, R, seed, body, inner=ARAW):
    return parol(D, cx, cy, R, seed, body=body, inner=inner, accent=("#FFFFFF", "#F2EAD8", "#C4B49A"), tails=R > 14, ring=False, glow=True)


@design("maligayang-pasko")
def maligayang_pasko():
    D = Doc2("ph-mp")
    out = [sky(D, [(0, "#0E1640"), (0.6, "#1E2A6A"), (1, "#3A3A86")], 201, 600, ["#1E2A6A", "#0A1030", "#2E3A7A"], 80, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(202)
    for _ in range(50):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 380)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>')
    for x, y, s in ((90, 70, 7), (520, 120, 6), (470, 40, 5), (130, 300, 5)):
        out.append(sparkle(x, y, s, "#FFF6D8", 0.9))
    # rooftops of the barrio, each window with its own parol
    roofs = [(-20, 352, 110), (80, 334, 100), (170, 362, 90), (250, 344, 120), (360, 358, 92), (440, 336, 110), (540, 354, 90)]
    for k, (x, top, w) in enumerate(roofs):
        wall_c = mix("#2A2A5A", "#4A3A6A", (k % 3) / 3)
        body = [(x, top + 26), (x + w, top + 26), (x + w, 440), (x, 440)]
        out.append(f'<path d="{pd(body)}" fill="{wall_c}"/>')
        out.append(f'<path d="{pd([(x - 10, top + 30), (x + w / 2, top), (x + w + 10, top + 30)])}" fill="#1A1A3A"/>')
        out.append(pline([(x - 10, top + 30), (x + w / 2, top), (x + w + 10, top + 30)], "#5A5A9A", 1.6, k, 0.5, 1))
        wx = x + w * 0.3
        out.append(f'<path d="{hg.org_rect(wx, top + 40, w * 0.4, 30, 210 + k, 0.4, 8, 1)}" fill="#FFD88A"/>')
        out.append(soft_glow(D, wx + w * 0.2, top + 55, 34, "#FFC860", 0.6))
        out.append(f'<path d="M {wx + w * 0.2:.1f} {top + 40} L {wx + w * 0.2:.1f} {top + 70} M {wx:.1f} {top + 55} L {wx + w * 0.4:.1f} {top + 55}" stroke="#5A3A2A" stroke-width="1.6"/>')
        cols = [PULA, ("#7AE0A0", "#1E9A5A", "#0A4A2A"), ("#FFB0D8", "#E8509A", "#8A1A5A"), BUGHAW, ("#FFE08A", "#F2A81E", "#8A5A0A")]
        out.append(parol_small(D, x + w * 0.5, top + 14 if k % 2 else top + 18, 11, 220 + k, cols[k % 5]))
    out.append(f'<path d="M -10 420 L 610 420 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#16163E"), (1, "#0A0A20")])}"/>')
    # windows of the near street glowing faintly on the dark ground
    for k in range(9):
        x = 20 + k * 70 + rnd.uniform(-10, 10)
        out.append(f'<path d="{blob(x, 432, 22, 4, 240 + k, 0.2, 10)}" fill="#FFC860" opacity="0.18"/>')
    # string of coloured bulbs swagging across the street
    lights = []
    for seg, (x0, y0, x1, y1, sag) in enumerate(((-10, 300, 300, 318, 36), (300, 318, 610, 292, 40))):
        pts = [(x0 + (x1 - x0) * t / 20, y0 + (y1 - y0) * t / 20 + sag * 4 * (t / 20) * (1 - t / 20)) for t in range(21)]
        lights.append(pline(pts, "#0A0A1A", 1.6, seg, 0.9, 1))
        for i in range(1, 20, 2):
            x, y = pts[i]
            c = ["#FF5A5A", "#FFD84A", "#5AE08A", "#5AB0FF", "#FF8AD8"][(i // 2 + seg) % 5]
            lights.append(soft_glow(D, x, y + 6, 14, c, 0.6))
            lights.append(f'<ellipse cx="{x:.1f}" cy="{y + 6:.1f}" rx="3.4" ry="5" fill="{c}"/><circle cx="{x - 1:.1f}" cy="{y + 4:.1f}" r="1.3" fill="#FFFFFF" opacity="0.9"/>')
    out.append("".join(lights))
    # the big parol, hanging from its cord
    pcx, pcy, R = 300, 196, 92
    out.append(pline([(300, -5), (301, 60), (300, pcy - R * 1.18)], "#0A0A1A", 2.4, 230, 0.95, 1))
    out.append(parol(D, pcx, pcy, R, 231))
    # lettering at the foot
    out.append(letters(D, 300, 484, "Maligayang Pasko", SERIF_IT, 76, "#FFE7A8", ["#FFFFFF", "#FFD878", "#FFF0C0"], 232, max_w=460,
                       shadow="#05051A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 524, "SIMULA SETYEMBRE", "#F2A8C8", font=JOS, size=18, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 233, "#0A0A2A", 0.6)


# ================================================================ 5. ingat! — a jeepney heading home at dusk
def chrome(D, pts, seed, inkw=1.2, vertical=False):
    d = smooth_closed(pts)
    g = D.lin([(0, "#FFFFFF"), (0.35, "#C8D0DA"), (0.55, "#6A7484"), (0.75, "#E8EEF4"), (1, "#8A94A4")], 0, 0, 1 if vertical else 0, 0 if vertical else 1)
    return f'<path d="{d}" fill="{g}"/>' + (ink(d, "#2A2E38", inkw, seed, 1, 0.7) if inkw else "")


def jeepney(D, X, Y, s, seed, body=("#FFFDF0", "#F2EAD2", "#B8A884"), sign="TRABAHO - BAHAY", name="Pamilya"):
    """Side view of a jeepney facing right; (X, Y) = ground under the rear bumper, s = scale (1 => ~470 px long)."""
    P = lambda x, y: (X + x * s, Y + y * s)
    PP = lambda pts: [P(x, y) for x, y in pts]
    out = [cast(D, X + 240 * s, Y + 2, 250 * s, 12 * s, strength=0.55, seed=seed)]
    # rear entrance (dark interior) and passenger body
    body_pts = PP([(0, -52), (322, -52), (322, -178), (0, -178)])
    out.append(painted(D, rect_pts(*P(0, -178), *P(322, -52), 16, seed, 0.4), body, seed, sdir=(0.3, 1), sk=0.12, angle=0, n=30, inkw=1.8, hi=0.3))
    # window band: dark interior, passengers, chrome posts
    win = rect_pts(*P(22, -170), *P(318, -138), 12, seed + 1, 0.3)
    out.append(f'<path d="{smooth_closed(win)}" fill="#2A2230"/>')
    rnd = random.Random(seed)
    heads = []
    for k in range(7):
        hx = 44 + k * 38 + rnd.uniform(-6, 6)
        if k == 3:
            continue
        hc = rnd.choice(["#3A2A2A", "#4A3428", "#2A1E1E"])
        heads.append(f'<path d="{blob(*P(hx, -150), 9 * s, 10 * s, seed + k, 0.08, 10)}" fill="{hc}"/>')
        heads.append(f'<path d="{blob(*P(hx, -136), 16 * s, 8 * s, seed + k + 20, 0.08, 10)}" fill="{rnd.choice(["#C8503A", "#3A6AA8", "#E8B83A", "#6A8A4A", "#F2F0E8"])}"/>')
        heads.append(f'<path d="{blob(*P(hx + 3, -152), 4 * s, 5 * s, seed + k + 40, 0.1, 8)}" fill="#E8B080" opacity="0.5"/>')
    out.append(clipped(D, smooth_closed(win), heads + [f'<rect x="{P(0, -172)[0]:.1f}" y="{P(0, -172)[1]:.1f}" width="{330 * s:.1f}" height="{8 * s:.1f}" fill="#000000" opacity="0.35"/>']))
    for k in range(8):
        x = 22 + k * 42
        out.append(chrome(D, rect_pts(*P(x - 2.5, -172), *P(x + 2.5, -136), 8, seed + k, 0.2), seed + k, 0.8, vertical=True))
    out.append(f'<path d="{smooth_closed(rect_pts(*P(0, -178), *P(24, -52), 10, seed + 2, 0.3))}" fill="#1E1820"/>')
    out.append(chrome(D, rect_pts(*P(20, -176), *P(26, -54), 8, seed + 3, 0.2), seed + 3, 0.8, vertical=True))
    # painted side panel: stripes, flourishes, the jeep's name
    stripes = [(-128, -122, PULA[1]), (-119, -115, ARAW[1]), (-112, -108, BUGHAW[1])]
    for y0, y1, c in stripes:
        out.append(f'<path d="{smooth_closed(rect_pts(*P(26, y0), *P(320, y1), 14, seed + int(y0), 0.3))}" fill="{c}"/>')
    for y0, y1, c in ((-74, -66, BUGHAW[1]), (-63, -58, PULA[1])):
        out.append(f'<path d="{smooth_closed(rect_pts(*P(26, y0), *P(320, y1), 14, seed + int(y0), 0.3))}" fill="{c}"/>')
    for k, cxp in enumerate((70, 278)):
        cx_, cy_ = P(cxp, -90)
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<path d="{blob(cx_ + math.cos(a) * 7 * s, cy_ + math.sin(a) * 7 * s, 6 * s, 3.6 * s, seed + j + k * 9, 0.1, 8, math.degrees(a))}" fill="{[PULA[1], "#E8509A"][k]}"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{3.6 * s:.1f}" fill="{ARAW[1]}"/>')
        for sg in (-1, 1):
            out.append(pline([P(cxp + sg * 14, -90), P(cxp + sg * 26, -100), P(cxp + sg * 40, -92), P(cxp + sg * 46, -84)], "#2E8A4A", 2.2 * s, seed + sg + k, 0.9, 1))
    nx, ny = P(174, -80)
    out.append(f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" {SERIF_IT} font-size="{fit_size(name, SERIF_IT, 34 * s, 150 * s):.1f}" fill="{PULA[2]}">{esc(name)}</text>')
    out.append(f'<text x="{nx - 1:.1f}" y="{ny - 1.5:.1f}" text-anchor="middle" {SERIF_IT} font-size="{fit_size(name, SERIF_IT, 34 * s, 150 * s):.1f}" fill="{PULA[1]}">{esc(name)}</text>')
    # roof with route board and a chrome rack
    roof = rect_pts(*P(-6, -198), *P(332, -176), 14, seed + 4, 0.3)
    out.append(painted(D, roof, ("#5A86D8", "#1E4AA0", "#0C2460"), seed + 4, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    bx, by = P(166, -183)
    out.append(f'<text x="{bx:.1f}" y="{by + 1:.1f}" text-anchor="middle" {ANTON} font-size="{fit_size(sign, ANTON, 15 * s, 240 * s, 2):.1f}" letter-spacing="2" fill="#FFF6D8">{esc(sign)}</text>')
    for k in range(9):
        x = 10 + k * 38
        out.append(chrome(D, rect_pts(*P(x - 2, -210), *P(x + 2, -198), 6, seed + 50 + k, 0.2), seed, 0.6, vertical=True))
    out.append(chrome(D, rect_pts(*P(4, -213), *P(326, -208), 14, seed + 60, 0.2), seed, 0.8))
    # cab: open side, driver, windshield, visor
    cab = PP([(322, -52), (372, -52), (372, -118), (366, -178), (322, -178)])
    out.append(painted(D, [P(x, y) for x, y in densify([(322, -52), (372, -52), (372, -118), (364, -178), (322, -178)], 10)], body, seed + 5, sk=0.12, angle=-90, n=10, inkw=1.6, hi=0.3))
    door = densify([(330, -150), (360, -150), (362, -100), (330, -100)], 8)
    out.append(f'<path d="{smooth_closed(PP(door))}" fill="#2A2230"/>')
    out.append(f'<path d="{blob(*P(346, -136), 8 * s, 9 * s, seed + 6, 0.08, 10)}" fill="#2A1E1E"/>')
    out.append(f'<path d="{blob(*P(346, -112), 14 * s, 10 * s, seed + 7, 0.08, 10)}" fill="#F2F0E8"/>')
    out.append(chrome(D, densify(PP([(364, -180), (382, -180), (384, -172), (366, -170)]), 6), seed + 8, 0.8))
    out.append(chrome(D, densify(PP([(368, -170), (372, -170), (380, -120), (376, -120)]), 6), seed + 9, 0.8, vertical=True))
    out.append(f'<path d="{smooth_closed(densify(PP([(372, -168), (378, -122), (373, -122), (369, -168)]), 6))}" fill="#9AC8E8" opacity="0.7"/>')
    # side mirror
    out.append(pline([P(372, -132), P(392, -146)], "#4A505A", 2 * s, seed, 0.9, 1))
    out.append(f'<path d="{blob(*P(394, -150), 6 * s, 8 * s, seed + 10, 0.05, 10)}" fill="#C8D0DA" stroke="#2A2E38" stroke-width="1.2"/>')
    # hood with chrome trim, little chrome horses and streamers
    hood = [(368, -52), (462, -52), (466, -66), (464, -112), (440, -120), (372, -122)]
    out.append(painted(D, [P(x, y) for x, y in densify(hood, 10)], ("#F27A6A", "#CE2A2A", "#7A0E10"), seed + 11, sdir=(0.2, 1), sk=0.15, angle=0, n=20, inkw=1.8, hi=0.45))
    out.append(chrome(D, densify(PP([(372, -96), (462, -96), (462, -90), (372, -90)]), 10), seed + 12, 0.8))
    for k in range(4):
        x = 392 + k * 14
        out.append(pline([P(x, -84), P(x, -64)], "#7A0E10", 2.2 * s, seed + k, 0.7, 1))
    for k, hx in enumerate((428, 446)):
        hpts = PP([(hx - 8, -120), (hx - 4, -132), (hx + 2, -140), (hx + 8, -136), (hx + 6, -128), (hx + 2, -124), (hx + 4, -120)])
        out.append(chrome(D, hpts, seed + 13 + k, 0.8))
    for k, (ax, col) in enumerate(((380, "#F6C51E"), (456, "#1E4AA0"))):
        out.append(pline([P(ax, -120), P(ax + 2, -190)], "#4A505A", 1.6 * s, seed + k, 0.9, 1))
        out.append(taper([P(ax + 2, -188), P(ax - 14, -184), P(ax - 30, -188)], 5 * s, 1, col, 0.95))
        out.append(taper([P(ax + 2, -180), P(ax - 12, -176), P(ax - 24, -179)], 4 * s, 1, PULA[1], 0.95))
    # grille, headlight, bumper
    out.append(chrome(D, densify(PP([(460, -116), (474, -114), (476, -58), (462, -56)]), 8), seed + 15, 1.0, vertical=True))
    for k in range(5):
        out.append(pline([P(463, -108 + k * 11), P(474, -108 + k * 11)], "#4A505A", 1.2, seed + k, 0.6, 1))
    out.append(f'<path d="{blob(*P(470, -100), 7 * s, 11 * s, seed + 16, 0.05, 10)}" fill="#FFF6C8" stroke="#4A505A" stroke-width="1.4"/>')
    out.append(soft_glow(D, *P(482, -100), 40 * s, "#FFE8A0", 0.6))
    out.append(chrome(D, densify(PP([(-10, -56), (24, -56), (24, -46), (-10, -46)]), 8), seed + 17, 1.0))
    out.append(chrome(D, densify(PP([(440, -58), (484, -58), (486, -46), (440, -46)]), 8), seed + 18, 1.0))
    # wheels with chrome fender arches
    for k, wx in enumerate((104, 404)):
        cxw, cyw = P(wx, -34)
        well = PP([(wx - 44, -52)] + [(wx + 44 * math.cos(math.radians(a)), -52 - 34 * math.sin(math.radians(a))) for a in range(180, -1, -15)])
        out.append(f'<path d="{smooth_closed(well)}" fill="#1E1820"/>')
        out.append(f'<circle cx="{cxw:.1f}" cy="{cyw:.1f}" r="{34 * s:.1f}" fill="#1E1A1E"/>')
        out.append(f'<circle cx="{cxw:.1f}" cy="{cyw:.1f}" r="{34 * s:.1f}" fill="none" stroke="#3A3438" stroke-width="{4 * s:.1f}" stroke-dasharray="{5 * s:.1f} {4 * s:.1f}"/>')
        out.append(f'<circle cx="{cxw:.1f}" cy="{cyw:.1f}" r="{19 * s:.1f}" fill="{D.rad([(0, "#FFFFFF"), (0.5, "#C8D0DA"), (1, "#6A7484")], 0.4, 0.4, 0.7)}" stroke="#2A2E38" stroke-width="1.4"/>')
        for j in range(6):
            a = math.radians(j * 60 + k * 20)
            out.append(f'<circle cx="{cxw + math.cos(a) * 11 * s:.1f}" cy="{cyw + math.sin(a) * 11 * s:.1f}" r="{2 * s:.1f}" fill="#4A505A"/>')
        out.append(f'<circle cx="{cxw:.1f}" cy="{cyw:.1f}" r="{5 * s:.1f}" fill="#E8EEF4" stroke="#4A505A" stroke-width="1"/>')
        arc = PP([(wx + 50 * math.cos(math.radians(a)), -50 - 40 * math.sin(math.radians(a))) for a in range(180, -1, -12)])
        out.append(taper(arc, 7 * s, 7 * s, "#6A7484"))
        out.append(taper(arc, 3.5 * s, 3.5 * s, "#F4F8FC", 0.9))
    # mud flaps
    for k, mx in enumerate((150, 452)):
        out.append(f'<path d="{smooth_closed(densify(PP([(mx, -52), (mx + 8, -52), (mx + 8, -14), (mx, -14)]), 6))}" fill="#C8241E" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def power_pole(D, x, base, top, seed, col="#3A2A3A"):
    out = [taper([(x, base), (x + 1, top)], 7, 5, col)]
    for k, w in enumerate((40, 30)):
        y = top + 14 + k * 16
        out.append(taper([(x - w, y), (x + w, y)], 4, 4, col))
        for sg in (-1, 1):
            out.append(f'<rect x="{x + sg * w * 0.8 - 2:.1f}" y="{y - 7:.1f}" width="4" height="7" fill="{col}"/>')
    out.append(f'<rect x="{x + 6:.1f}" y="{top + 44:.1f}" width="16" height="22" rx="3" fill="{col}"/>')
    return "".join(out)


@design("ingat")
def ingat():
    D = Doc2("ph-in")
    out = [sky(D, [(0, "#4A3A86"), (0.35, "#C8689A"), (0.62, "#F6A06A"), (0.8, "#FFD890")], 301, 600, ["#6A4A9A", "#F28A8A", "#FFC890"], 80, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 420, 360, 220, "#FFE8A8", 0.7))
    out.append(f'<circle cx="420" cy="372" r="38" fill="#FFE9A8" opacity="0.9"/>')
    out.append(puff_cloud(D, 120, 286, 140, 302, pal=("#FFD8C8", "#F2A8B0", "#B86A8A"), op=0.8))
    out.append(puff_cloud(D, 540, 250, 110, 303, pal=("#FFD8C8", "#F2A8B0", "#B86A8A"), op=0.7))
    # town silhouettes: a bell tower, shophouses, palms
    sil = "#5A3A6A"
    sil2 = "#3E2A52"
    town = []
    town.append(f'<path d="{pd([(-10, 420), (60, 420), (60, 360), (120, 360), (120, 392), (180, 392), (180, 350), (236, 350), (236, 400), (610, 400), (610, 460), (-10, 460)])}" fill="{sil}"/>')
    town.append(f'<path d="{pd([(470, 400), (470, 300), (478, 292), (478, 270), (490, 256), (502, 270), (502, 292), (510, 300), (510, 400)])}" fill="{sil}"/>')
    town.append(f'<path d="{pd([(486, 256), (490, 236), (494, 256)])}" fill="{sil}"/><path d="M 490 236 L 490 222 M 484 228 L 496 228" stroke="{sil}" stroke-width="3"/>')
    town.append(f'<path d="{blob(490, 320, 6, 9, 304, 0.05, 10)}" fill="#FFD890" opacity="0.8"/>')
    for k, (x, y) in enumerate(((76, 380), (96, 380), (136, 404), (196, 368), (216, 368))):
        town.append(f'<rect x="{x}" y="{y}" width="10" height="12" fill="#FFD890" opacity="{0.6 + 0.1 * (k % 3):.1f}"/>')
    out.append("".join(town))
    for k, (bx, ty, lean) in enumerate(((268, 300, 8), (558, 316, -10))):
        out.append(palm(D, (bx, 420), (bx + lean, ty), 305 + k, sil=sil2, L=70, width=12, nuts=False, leaf_cols=[sil2]))
    out.append(power_pole(D, 330, 470, 286, 307, sil2))
    wires = []
    for k, (y0, y1, sag) in enumerate(((300, 312, 22), (316, 330, 26), (334, 348, 18))):
        for (xa, xb, ya, yb) in ((-10, 330, y0 + 8, y0), (330, 610, y0, y1)):
            pts = [(xa + (xb - xa) * t / 16, ya + (yb - ya) * t / 16 + sag * 4 * (t / 16) * (1 - t / 16)) for t in range(17)]
            wires.append(pline(pts, sil2, 1.4, k, 0.85, 1))
    out.append("".join(wires))
    # road and sidewalk
    out.append(f'<path d="M -10 452 L 610 452 L 610 470 L -10 470 Z" fill="#8A6A7A"/>')
    out.append(f'<path d="M -10 468 L 610 468 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#5A4A5A"), (1, "#3A2E3A")])}"/>')
    out.append(strokes(D.nid(), "M -10 468 L 610 468 L 610 610 L -10 610 Z", (-40, 468, 600, 600), ["#7A6A7A", "#2A1E2A", "#F2A07A"], 308, n=50, angle=-1, length=(40, 140), width=(2, 5), opacity=(0.1, 0.3)))
    for k in range(5):
        x = -20 + k * 140
        out.append(f'<path d="{hg.org_rect(x, 552, 70, 7, 309 + k, 0.4, 10, 2)}" fill="#F2E2B0" opacity="0.8"/>')
    # sunset glow reflected on the road
    out.append(f'<path d="{blob(430, 500, 160, 18, 310, 0.1, 14)}" fill="#F6B07A" opacity="0.25"/>')
    # motion lines behind the jeep
    for k, (y, L) in enumerate(((410, 50), (436, 36), (470, 44))):
        out.append(taper([(52 - L, y), (52, y)], 1, 4, "#FFF2D8", 0.75))
    out.append(jeepney(D, 66, 520, 0.98, 311))
    # lettering
    out.append(letters(D, 300, 160, "Ingat!", SERIF_IT, 138, "#FFF2DC", ["#FFFFFF", "#FFE0C0", "#F8D0B8"], 312, max_w=400,
                       shadow="#2E1E4E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 212, "TEXT MO AKO PAG NAKAUWI KA NA", "#FFF0C8", font=JOS, size=18, ls=3, line_w=18, gap=10, max_w=420))
    return finish_b(D, out, 313, "#2A1A3A", 0.6)


# ================================================================ 6. lola — her tumba-tumba by the capiz window
def solihiya(D, d, seed, cane=("#F6DCA0", "#D8B070", "#8A6A30"), hole="#4A2E14", cell=13, rot_=0):
    """Solihiya cane weave: crossing strands with the little octagonal sunburst holes."""
    c = cell
    t = [f'<rect width="{c}" height="{c}" fill="{cane[1]}"/>',
         f'<path d="M 0 {c / 2} L {c} {c / 2} M {c / 2} 0 L {c / 2} {c} M 0 0 L {c} {c} M {c} 0 L 0 {c}" stroke="{cane[0]}" stroke-width="1.8"/>',
         f'<path d="M 0 {c / 2 + 1.2} L {c} {c / 2 + 1.2} M {c / 2 + 1.2} 0 L {c / 2 + 1.2} {c}" stroke="{cane[2]}" stroke-width="0.8" opacity="0.6"/>',
         f'<circle cx="0" cy="0" r="{c * 0.24:.1f}" fill="{hole}"/><circle cx="{c}" cy="0" r="{c * 0.24:.1f}" fill="{hole}"/>'
         f'<circle cx="0" cy="{c}" r="{c * 0.24:.1f}" fill="{hole}"/><circle cx="{c}" cy="{c}" r="{c * 0.24:.1f}" fill="{hole}"/>']
    pat = D.pattern(c, c, "".join(t), transform=f"rotate({rot_})" if rot_ else "")
    return f'<path d="{d}" fill="{pat}"/>'


def capiz_window(D, x0, y0, x1, y1, seed, cols=4, rows=6, frame=NARRA, glow="#FFF6E0", open_=0.0):
    """Sliding capiz-shell window: a wooden grid of small translucent pearly squares."""
    out = [painted(D, rect_pts(x0 - 10, y0 - 10, x1 + 10, y1 + 10, 16, seed, 0.4), frame, seed, sdir=(0.6, 0.8), sk=0.15, angle=-90, n=20, inkw=1.8, hi=0.35)]
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    rnd = random.Random(seed)
    for i in range(cols):
        for j in range(rows):
            x, y = x0 + i * cw + 2.5, y0 + j * ch + 2.5
            c = mix(glow, rnd.choice(["#F2D8C8", "#E8E0F0", "#FFF2D0", "#E8F0E8"]), rnd.uniform(0.2, 0.6))
            out.append(f'<path d="{hg.org_rect(x, y, cw - 5, ch - 5, seed + i * 17 + j, 0.4, 8, 1.5)}" fill="{c}"/>')
            out.append(f'<path d="M {x + 2:.1f} {y + ch - 9:.1f} Q {x + cw * 0.4:.1f} {y + ch * 0.3:.1f} {x + cw - 8:.1f} {y + 3:.1f}" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.6"/>')
            out.append(f'<path d="M {x + 3:.1f} {y + ch * 0.6:.1f} q {cw * 0.3:.1f} {-ch * 0.2:.1f} {cw * 0.6:.1f} {-ch * 0.1:.1f}" stroke="#D8C8D8" stroke-width="1" fill="none" opacity="0.5"/>')
    for i in range(cols + 1):
        out.append(taper([(x0 + i * cw, y0 - 2), (x0 + i * cw, y1 + 2)], 5, 5, frame[1]))
    for j in range(rows + 1):
        out.append(taper([(x0 - 2, y0 + j * ch), (x1 + 2, y0 + j * ch)], 5, 5, frame[1]))
    out.append(ink(smooth_closed(rect_pts(x0 - 10, y0 - 10, x1 + 10, y1 + 10, 16, seed, 0.4)), INK, 1.6, seed, 1, 0.7))
    return "".join(out)


def abaniko(D, cx, cy, R, ang, seed, pal=("#FFB0C8", "#E8508A", "#9A1A4A"), spread=150):
    """Folding hand fan (abaniko), opened: pleated painted leaf on fine ribs, a sampaguita sprig painted on it."""
    out = [cast(D, cx + 6, cy + 6, R * 0.8, R * 0.25, strength=0.3, seed=seed)]
    n = 14
    a0 = ang - spread / 2
    for k in range(n):
        a = math.radians(a0 + spread * k / n)
        b = math.radians(a0 + spread * (k + 1) / n)
        pts = [(cx + math.cos(a) * R * 0.3, cy + math.sin(a) * R * 0.3), (cx + math.cos(a) * R, cy + math.sin(a) * R),
               (cx + math.cos(b) * R, cy + math.sin(b) * R), (cx + math.cos(b) * R * 0.3, cy + math.sin(b) * R * 0.3)]
        col = pal[0] if k % 2 else mix(pal[0], pal[1], 0.35)
        out.append(f'<path d="{pd(pts)}" fill="{col}"/>')
    for k in range(n + 1):
        a = math.radians(a0 + spread * k / n)
        out.append(pline([(cx, cy), (cx + math.cos(a) * R, cy + math.sin(a) * R)], "#7A4A2A", 1.2, seed + k, 0.6, 1))
    edge = [(cx + math.cos(math.radians(a0 + spread * t / 30)) * R, cy + math.sin(math.radians(a0 + spread * t / 30)) * R) for t in range(31)]
    out.append(pline(edge, pal[2], 2.2, seed, 0.8, 1))
    inner = [(cx + math.cos(math.radians(a0 + spread * t / 30)) * R * 0.3, cy + math.sin(math.radians(a0 + spread * t / 30)) * R * 0.3) for t in range(31)]
    out.append(pline(inner, "#7A4A2A", 1.6, seed, 0.7, 1))
    # painted sprig
    am = math.radians(ang)
    fx, fy = cx + math.cos(am) * R * 0.66, cy + math.sin(am) * R * 0.66
    for j in range(3):
        aa = am + (j - 1) * 0.35
        px, py = cx + math.cos(aa) * R * 0.68, cy + math.sin(aa) * R * 0.68
        out.append(sampaguita_flower(D, px, py, R * 0.09, seed + j))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.05:.1f}" fill="#C8A040" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def sampaguita_flower(D, cx, cy, r, seed, rot_=0, pal=("#FFFFFF", "#F6F2E8", "#B8B0A0"), center="#F2E8A0", layers=1):
    """Sampaguita (Arabian jasmine): small white star of rounded petals, sometimes double."""
    out = []
    for L in range(layers):
        n = 7 if L == 0 else 6
        rr = r * (1 - 0.3 * L)
        for k in range(n):
            a = math.radians(rot_ + k * 360 / n + L * 25)
            x, y = cx + math.cos(a) * rr * 0.55, cy + math.sin(a) * rr * 0.55
            out.append(f'<path d="{blob(x, y, rr * 0.55, rr * 0.28, seed + k + L * 9, 0.1, 8, math.degrees(a))}" fill="{pal[0] if L else pal[1]}" stroke="{pal[2]}" stroke-width="{max(0.6, r * 0.06):.1f}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.16:.1f}" fill="{center}"/>')
    return "".join(out)


def rosary(D, cx, cy, r, seed, bead="#6A2E2A", cross="#C8A040"):
    rnd = random.Random(seed)
    out = []
    pts = [(cx + math.cos(math.radians(a)) * r * (1 + 0.08 * math.sin(a / 20)), cy + math.sin(math.radians(a)) * r * 0.55) for a in range(0, 360, 12)]
    for x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{bead}" stroke="#2A0A08" stroke-width="0.8"/><circle cx="{x - 1:.1f}" cy="{y - 1:.1f}" r="1.1" fill="#FFFFFF" opacity="0.7"/>')
    tail = [(cx + r * 0.2, cy + r * 0.55), (cx + r * 0.35, cy + r * 0.85), (cx + r * 0.42, cy + r * 1.1)]
    for x, y in catmull(tail, 3)[::2]:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{bead}" stroke="#2A0A08" stroke-width="0.8"/>')
    x, y = cx + r * 0.46, cy + r * 1.3
    out.append(f'<path d="M {x - 2:.1f} {y - 8:.1f} h 4 v 6 h 5 v 4 h -5 v 12 h -4 v -12 h -5 v -4 h 5 Z" fill="{cross}" stroke="#6A4A10" stroke-width="0.8"/>')
    return "".join(out)


def tumba(D, X, Y, s, seed, frame=("#9A5A30", "#5E3018", "#2A1206")):
    """Tumba-tumba (rattan rocking chair) in 3/4 view facing left-front; (X, Y) = floor under the middle of the rockers."""
    def P(u, v, h):
        return (X + (-u * 0.86 + v * 0.62) * s, Y + (-h + u * 0.16 + v * 0.3) * s)

    def rocker_pts(v):
        return [P(u, v, 14 * ((u - 40) / 110) ** 2) for u in range(-80, 161, 12)]

    out = [cast(D, X - 10 * s, Y + 22 * s, 150 * s, 20 * s, strength=0.4, seed=seed)]
    far, near = 112, 0
    dark = tuple(dk(c, 0.25) for c in frame)
    # far side: rocker, legs, back post, armrest
    out.append(taper(rocker_pts(far), 9 * s, 9 * s, dark[1]))
    for u in (0, 104):
        out.append(taper([P(u, far, 6), P(u, far, 100)], 8 * s, 7 * s, dark[1]))
    out.append(taper([P(0, far, 100), P(-12, far, 200), P(-26, far, 290)], 9 * s, 8 * s, dark[1]))
    out.append(taper([P(-14, far, 190), P(40, far, 192), P(90, far, 176), P(114, far, 168)], 8 * s, 9 * s, dark[1]))
    out.append(taper([P(104, far, 100), P(110, far, 168)], 7 * s, 7 * s, dark[1]))
    # back panel (woven)
    bp = [P(-2, near + 8, 116), P(-2, far - 8, 116), P(-24, far - 8, 278), P(-28, (near + far) / 2, 296), P(-24, near + 8, 278)]
    bd = smooth_closed(densify(bp, 10))
    out.append(solihiya(D, bd, seed + 1, cell=12 * s))
    out.append(clipped(D, bd, [f'<path d="{bd}" fill="{D.lin([(0, "#2A1206", 0.0), (1, "#2A1206", 0.35)], 0, 0, 1, 0)}"/>']))
    out.append(ink(bd, frame[2], 1.4, seed, 1, 0.6))
    out.append(taper([P(-2, near + 6, 116), P(-2, far - 6, 116)], 7 * s, 7 * s, frame[1]))
    out.append(taper([P(-24, near + 6, 278), P(-29, (near + far) / 2, 298), P(-24, far - 6, 278)], 10 * s, 10 * s, frame[1]))
    out.append(taper([P(-22, near + 8, 274), P(-27, (near + far) / 2, 292), P(-22, far - 8, 274)], 2.5 * s, 2.5 * s, frame[0], 0.8))
    # seat (woven)
    sp = [P(0, near, 100), P(104, near, 98), P(104, far, 98), P(0, far, 100)]
    sd = smooth_closed(densify(sp, 10))
    out.append(solihiya(D, sd, seed + 2, cell=11 * s, rot_=20))
    out.append(clipped(D, sd, [f'<path d="{sd}" fill="{D.lin([(0, "#2A1206", 0.3), (1, "#2A1206", 0.0)], 0, 0, 1, 0)}"/>']))
    out.append(taper([P(0, near, 98), P(104, near, 96)], 8 * s, 8 * s, frame[1]))
    out.append(taper([P(104, near, 96), P(104, far, 96)], 8 * s, 8 * s, frame[1]))
    # near side: rocker, legs, back post, curving armrest with a scroll
    out.append(taper(rocker_pts(near), 10 * s, 10 * s, frame[1]))
    out.append(taper([p for p in rocker_pts(near)], 3 * s, 3 * s, frame[0], 0.7))
    for u in (0, 104):
        out.append(taper([P(u, near, 6), P(u, near, 100)], 9 * s, 8 * s, frame[1]))
        out.append(taper([P(u + 3, near, 10), P(u + 3, near, 96)], 2.4 * s, 2 * s, frame[0], 0.7))
    out.append(taper([P(0, near, 100), P(-12, near, 200), P(-26, near, 290)], 10 * s, 9 * s, frame[1]))
    out.append(taper([P(2, near, 104), P(-10, near, 200), P(-23, near, 284)], 3 * s, 2.4 * s, frame[0], 0.7))
    arm = [P(-14, near, 190), P(40, near, 194), P(90, near, 178), P(116, near, 168), P(124, near, 156), P(114, near, 150)]
    out.append(taper([P(104, near, 100), P(110, near, 166)], 8 * s, 8 * s, frame[1]))
    out.append(taper(arm, 10 * s, 11 * s, frame[1]))
    out.append(taper(arm[:4], 3 * s, 3 * s, frame[0], 0.75))
    # little turned finials on the back posts
    for v in (near, far):
        x, y = P(-27, v, 296)
        out.append(f'<path d="{blob(x, y, 6 * s, 7 * s, seed + v, 0.05, 10)}" fill="{frame[1] if v == near else dark[1]}" stroke="{frame[2]}" stroke-width="1"/>')
    return "".join(out), P


@design("lola")
def lola():
    D = Doc2("ph-lo")
    out = [wall(D, "#F6DCC4", "#EBC4A4", 401, ["#FFE8D4", "#D8A888", "#F8D4BC"])]
    # a band of wainscot and the polished narra floor
    out.append(f'<path d="M -10 380 L 610 380 L 610 450 L -10 450 Z" fill="#B87A4E"/>')
    out.append(wood_planks(D, 380, 450, 402, ("#D8986A", "#A86A3E", "#5E3418"), 1, vertical=True, x0=-10, x1=610) if False else "")
    for k in range(13):
        out.append(pline([(k * 50 - 4, 382), (k * 50 - 4, 448)], "#6A3A1A", 1.6, k, 0.5, 1))
    out.append(taper([(-10, 382), (610, 382)], 8, 8, "#8A5230"))
    out.append(taper([(-10, 380), (610, 380)], 2.4, 2.4, "#E8B88A", 0.8))
    floor = "M -10 450 L 610 450 L 610 610 L -10 610 Z"
    out.append(f'<path d="{floor}" fill="{D.lin([(0, "#8A4E2A"), (1, "#5E3018")])}"/>')
    fl = []
    for k in range(14):
        x = -60 + k * 56
        fl.append(pline([(300 + (x - 300) * 0.55, 450), (x, 600)], "#3A1A08", 1.6, k, 0.45, 1))
    out.append("".join(fl))
    out.append(strokes(D.nid(), floor, (-40, 450, 600, 600), ["#B8784A", "#3A1A08", "#D8986A"], 403, n=60, angle=-80, length=(20, 60), width=(2, 5), opacity=(0.1, 0.3)))
    # capiz window, sunlight falling across the floor
    out.append(capiz_window(D, 396, 222, 520, 368, 404, cols=4, rows=5))
    out.append(f'<path d="M 396 368 L 520 368 L 470 600 L 210 600 Z" fill="#FFF2D0" opacity="0.16"/>')
    out.append(soft_glow(D, 456, 280, 160, "#FFF6DC", 0.45))
    # a framed picture: the old home province (no faces)
    out.append(painted(D, rect_pts(96, 222, 186, 292, 12, 405, 0.4), ("#E8C888", "#B8904A", "#6A4A1A"), 405, sk=0.15, angle=0, n=8, inkw=1.6, hi=0.4))
    pic = smooth_closed(rect_pts(106, 232, 176, 282, 10, 406, 0.3))
    out.append(clipped(D, pic, [f'<rect x="100" y="227" width="80" height="60" fill="#A8D0E8"/>',
                                 f'<path d="M 100 270 Q 130 252 150 262 T 182 258 L 182 284 L 100 284 Z" fill="#6AA04A"/>',
                                 f'<path d="M 118 270 L 132 258 L 146 270 Z" fill="#C8A060"/><rect x="122" y="270" width="20" height="10" fill="#8A6A3A"/>',
                                 f'<circle cx="164" cy="244" r="6" fill="#FFE08A"/>']))
    out.append(ink(pic, INK, 1.2, 407, 1, 0.6))
    # sampaguita garland hung on the frame corner
    gl = [(100, 290), (112, 314), (141, 326), (170, 314), (182, 290)]
    out.append(pline(gl, "#3E7A2A", 1.6, 409, 0.8, 1))
    for k, (x, y) in enumerate(catmull(gl, 3)):
        if k % 2:
            out.append(leaf_simple(D, x, y, 10, 3, 120 + k * 20, ("#8AC870", "#3E8A3A", "#1E5A22"), 410 + k, vein=False, inkw=0))
        out.append(sampaguita_flower(D, x, y, 7.5, 412 + k, rot_=k * 20))
    out.append(taper([(141, 326), (138, 342), (142, 356)], 3, 1, "#C8304A"))
    # a banig rug under the chair
    rug = [(110, 470), (370, 470), (410, 560), (60, 560)]
    rd = smooth_closed(densify(rug, 12))
    out.append(banig(D, rd, 415, cell=8, base="#E2C48A", bands=("#B8285A", "#2E7A5A", "#E8A81E", "#5A2A8A"), rot_=45))
    out.append(clipped(D, rd, [f'<path d="{rd}" fill="{D.lin([(0, "#3A1A06", 0.2), (1, "#3A1A06", 0.0)])}"/>']))
    out.append(ink(rd, INK, 1.4, 416, 1, 0.5))
    # the rocking chair
    chair, P = tumba(D, 246, 526, 0.9, 420)
    out.append(chair)
    # her abaniko left open on the seat
    out.append(abaniko(D, *P(54, 50, 104), 42, -100, 423))
    # side table with her rosary, her glasses and a cup of salabat
    tx, ttop = 458, 452
    out.append(cast(D, tx + 8, 538, 64, 10, strength=0.4, seed=430))
    for lx in (tx - 36, tx + 34):
        out.append(taper([(lx, ttop + 6), (lx + (4 if lx > tx else -4), 534)], 7, 6, "#5E3018"))
    out.append(taper([(tx, ttop + 6), (tx, 528)], 6, 6, "#4A2410"))
    out.append(painted(D, ell_pts(tx, ttop, 60, 15, 0, 360, 24)[:-1], NARRA, 431, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{pd([(tx - 60, ttop), (tx + 60, ttop), (tx + 58, ttop + 8), (tx - 58, ttop + 8)])}" fill="#5E3018"/>')
    out.append(rosary(D, tx - 18, ttop - 2, 18, 432))
    cup = [(tx + 14, ttop - 34), (tx + 16, ttop - 4), (tx + 42, ttop - 4), (tx + 44, ttop - 34)]
    out.append(painted(D, densify(cup, 6), WHITE, 433, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=6, inkw=1.4, hi=0.5))
    out.append(f'<path d="{ellipse_d(tx + 29, ttop - 34, 15, 4)}" fill="#C8904A" stroke="{INK}" stroke-width="1"/>')
    out.append(pline([(tx + 44, ttop - 28), (tx + 52, ttop - 24), (tx + 50, ttop - 14), (tx + 43, ttop - 12)], WHITE[2], 2.2, 434, 0.9, 1))
    out.append(pline([(tx + 16, ttop - 26), (tx + 42, ttop - 26)], BUGHAW[1], 1.8, 435, 0.8, 1))
    out.append(steam(tx + 29, ttop - 42, 30, 436, "#FFFFFF", 2, 10, 4, 0.7))
    # lettering
    out.append(letters(D, 300, 158, "Lola", SERIF_IT, 132, "#8A2E3A", ["#A8404A", "#5A1420", "#C0606A"], 440, max_w=360,
                       shadow="#FFF4E8", soff=(0.018, 0.03), angle=-40, hi="#F2A8A8"))
    out.append(ruled(300, 198, "ANG PINAKAMAMAHAL NAMIN", "#7A4A2A", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 441)


# ================================================================ 7. sinigang — the kaldero on a bamboo table, sour and steaming
def bamboo_table(D, y0, y1, seed, n=6, pal=("#F2DC9A", "#D2B062", "#8A6A2A")):
    """Table top of split-round bamboo poles running across, each with nodes and a lit upper edge."""
    h = (y1 - y0) / n
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = y0 + i * h
        d = pd([(-10, a), (610, a), (610, a + h), (-10, a + h)])
        c = mix(pal[1], rnd.choice([pal[0], pal[2]]), rnd.uniform(0.05, 0.25))
        out.append(f'<path d="{d}" fill="{c}"/>')
        out.append(f'<path d="{d}" fill="{D.lin([(0, pal[0], 0.7), (0.4, pal[1], 0), (1, pal[2], 0.7)], 0, a, 0, a + h, "userSpaceOnUse")}"/>')
        out.append(strokes(D.nid(), d, (-40, a, 600, a + h), [pal[0], pal[2]], seed + i, n=14, angle=0, length=(40, 120), width=(0.8, 2), opacity=(0.2, 0.45), curve=0.03))
        x = rnd.uniform(-40, 40)
        while x < 620:
            out.append(f'<path d="M {x:.1f} {a + 1:.1f} Q {x + 3:.1f} {a + h / 2:.1f} {x:.1f} {a + h - 1:.1f}" stroke="{pal[2]}" stroke-width="2.4" fill="none" opacity="0.75"/>')
            out.append(f'<path d="M {x + 3:.1f} {a + 2:.1f} Q {x + 6:.1f} {a + h / 2:.1f} {x + 3:.1f} {a + h - 2:.1f}" stroke="{pal[0]}" stroke-width="1.2" fill="none" opacity="0.6"/>')
            x += rnd.uniform(120, 190)
        out.append(pline([(-10, a + h - 0.5), (610, a + h - 0.5)], "#4A3410", 1.4, seed + i, 0.6, 1))
    return "".join(out)


def kaldero(D, cx, rim_y, rx, h, seed, ry=None):
    """Dented aluminium cooking pot with two loop handles; soot at the bottom, bright rolled rim."""
    ry = ry or rx * 0.36
    bot = rim_y + h
    body = [(cx + rx, rim_y), (cx + rx * 0.98, rim_y + h * 0.6), (cx + rx * 0.9, bot - 8), (cx + rx * 0.7, bot), (cx - rx * 0.7, bot), (cx - rx * 0.9, bot - 8),
            (cx - rx * 0.98, rim_y + h * 0.6), (cx - rx, rim_y)] + ell_pts(cx, rim_y, rx, ry, 180, 360, 18)[1:-1]
    d = smooth_closed(body)
    out = [cast(D, cx + 14, bot, rx * 1.05, h * 0.14, strength=0.5, seed=seed)]
    for sg in (-1, 1):
        hp = [(cx + sg * rx * 0.96, rim_y + h * 0.16), (cx + sg * (rx + 30), rim_y + h * 0.1), (cx + sg * (rx + 36), rim_y + h * 0.3), (cx + sg * (rx + 22), rim_y + h * 0.42), (cx + sg * rx * 0.98, rim_y + h * 0.38)]
        out.append(ink(smooth_open(hp), "#4A505A", 11, seed + sg, 1, 1))
        out.append(ink(smooth_open(hp), "#C8D0DA", 6, seed + sg, 1, 1))
        out.append(ink(smooth_open(hp[:3]), "#FFFFFF", 2, seed + sg, 1, 0.8))
    out.append(painted(D, body, STEEL, seed, sdir=(0.85, 0.35), sk=0.2, angle=-85, n=50, slen=(14, 40), sw=(1.2, 3), cols=["#FFFFFF", "#8A94A4", "#E8ECF0", "#AAB2BE"], inkw=2.2, inkc="#2A2E38", inkop=0.7, hi=0.5, hik=0.06))
    inner = [f'<path d="{d}" fill="{D.lin([(0, "#14141A", 0), (0.6, "#14141A", 0), (1, "#14141A", 0.55)])}"/>',
             f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.0), (0.2, "#FFFFFF", 0.55), (0.32, "#FFFFFF", 0.0), (0.75, "#FFFFFF", 0), (0.86, "#FFFFFF", 0.3), (1, "#FFFFFF", 0)], 0, 0, 1, 0)}"/>']
    rnd = random.Random(seed)
    for _ in range(3):
        x, y = cx + rnd.uniform(-rx, rx) * 0.6, rim_y + h * rnd.uniform(0.3, 0.7)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(10, 16), rnd.uniform(6, 9), rnd.randint(0, 999), 0.2, 10)}" fill="#6A7484" opacity="0.25"/>')
        inner.append(taper([(x - 8, y - 5), (x + 2, y - 8), (x + 10, y - 4)], 2.5, 1, "#FFFFFF", 0.6))
    out.append(clipped(D, d, inner))
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx + 4, ry + 3)}" fill="#E8ECF0"/>')
    out.append(taper(ell_pts(cx, rim_y, rx + 2, ry + 1.5, 160, 340, 20), 3, 2, "#FFFFFF", 0.9))
    out.append(ink(ellipse_d(cx, rim_y, rx + 4, ry + 3), "#2A2E38", 1.6, seed, 1, 0.7))
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx - 2, ry - 2)}" fill="#6A7484"/>')
    return "".join(out)


def kangkong_leaf(D, x, y, L, ang, seed):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = [(x, y), (x + ux * L * 0.3 + nx * L * 0.28, y + uy * L * 0.3 + ny * L * 0.28), (x + ux * L, y + uy * L),
           (x + ux * L * 0.3 - nx * L * 0.28, y + uy * L * 0.3 - ny * L * 0.28), (x - ux * L * 0.05 - nx * L * 0.14, y - uy * L * 0.05 - ny * L * 0.14),
           (x - ux * L * 0.05 + nx * L * 0.14, y - uy * L * 0.05 + ny * L * 0.14)]
    out = [painted(D, pts, ("#6AB04A", "#2E7A2A", "#124A16"), seed, sdir=(nx, ny), sk=0.2, angle=ang, n=5, inkw=1.0, inkc="#0E3A10", hi=0.35)]
    out.append(pline([(x, y), (x + ux * L * 0.9, y + uy * L * 0.9)], "#A8D880", 1.2, seed, 0.7, 1))
    return "".join(out)


def radish_slice(x, y, r, seed):
    return (f'<path d="{blob(x, y, r, r * 0.8, seed, 0.06, 12)}" fill="#F8F6EE" stroke="#C8C4B4" stroke-width="1.2" opacity="0.95"/>'
            f'<path d="{blob(x, y, r * 0.7, r * 0.55, seed + 1, 0.06, 12)}" fill="none" stroke="#E0DCD0" stroke-width="1"/>'
            f'<circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.25:.1f}" r="{r * 0.2:.1f}" fill="#FFFFFF" opacity="0.8"/>')


def pork_rib(D, x, y, s, ang, seed):
    pts = rot(blob_pts(x, y, s, s * 0.5, seed, 0.14, 12), x, y, ang)
    out = [painted(D, pts, ("#F2C8A8", "#C88E6A", "#7A4A2E"), seed, sdir=(0.5, 0.8), sk=0.22, angle=ang, n=6, inkw=1.1, inkop=0.55, hi=0.45)]
    a = math.radians(ang)
    bx, by = x + math.cos(a) * s * 0.95, y + math.sin(a) * s * 0.95
    out.append(f'<path d="{blob(bx, by, s * 0.24, s * 0.18, seed + 3, 0.1, 8, ang)}" fill="#F6ECD8" stroke="{INK}" stroke-width="1"/>')
    out.append(taper([(x - math.cos(a) * s * 0.5, y - math.sin(a) * s * 0.5 - 3), (x + math.cos(a) * s * 0.5, y + math.sin(a) * s * 0.5 - 4)], 4, 2, "#FFF2E8", 0.6))
    return "".join(out)


def tamarind_pod(D, x, y, L, ang, seed, open_=False):
    """Sampalok pod: knobbly curved brown pod; an opened one shows the sticky pulp and dark seeds."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    top, bot = [], []
    for i in range(13):
        t = i / 12
        w = L * 0.09 * (1 + 0.25 * math.sin(t * math.pi * 4)) * (0.6 + 0.4 * math.sin(math.pi * t) ** 0.3)
        bend = L * 0.12 * math.sin(math.pi * t)
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        top.append((px + nx * w, py + ny * w))
        bot.append((px - nx * w, py - ny * w))
    pts = top + bot[::-1]
    pal = ("#C8925A", "#8A5A2E", "#4A2A12") if not open_ else ("#B87A4A", "#7A4A22", "#3A1E0A")
    out = [cast(D, x + ux * L / 2 + 4, y + uy * L / 2 + 8, L * 0.5, L * 0.1, strength=0.35, seed=seed)]
    out.append(painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.2, angle=ang, n=8, inkw=1.3, hi=0.4))
    if open_:
        pulp = [(px * 0.7 + qx * 0.3, py * 0.7 + qy * 0.3) for (px, py), (qx, qy) in zip(top[2:11], bot[2:11])]
        pulp += [(px * 0.3 + qx * 0.7, py * 0.3 + qy * 0.7) for (px, py), (qx, qy) in zip(top[2:11], bot[2:11])][::-1]
        out.append(f'<path d="{smooth_closed(pulp)}" fill="#A8602A"/>')
        for i in (3, 5, 7, 9):
            px, py = (top[i][0] + bot[i][0]) / 2, (top[i][1] + bot[i][1]) / 2
            out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{L * 0.04:.1f}" ry="{L * 0.03:.1f}" fill="#3A1A08"/><circle cx="{px - 1:.1f}" cy="{py - 1:.1f}" r="1.2" fill="#FFFFFF" opacity="0.6"/>')
        for i in range(2, 11, 2):
            out.append(pline([top[i], (top[i][0] - nx * 3, top[i][1] - ny * 3)], "#E8C890", 1, seed + i, 0.6, 1))
    else:
        for i in (3, 6, 9):
            out.append(pline([top[i], bot[i]], pal[2], 1, seed + i, 0.4, 1))
    return "".join(out)


def long_chili(D, x, y, L, ang, seed, pal=("#A8E07A", "#4E9A2E", "#1E5A14")):
    return sili(D, x, y, L, ang, seed, pal=pal)


@design("sinigang")
def sinigang():
    D = Doc2("ph-sg")
    out = [wall(D, "#A8D4C4", "#7AB4A2", 501, ["#C0E2D6", "#5E9A88", "#B8DCCE"])]
    out.append(soft_glow(D, 300, 260, 340, "#FFFFFF", 0.4))
    out.append(blooms(502, ["#C8E8DC", "#5E9A88"], 7, (0, 0, 600, 430), (90, 170), (0.06, 0.12)))
    out.append(bamboo_table(D, 420, 610, 503, n=6))
    out.append(table_edge(420, "#3A3410", 0.45))
    cx, rim_y, rx = 300, 338, 166
    out.append(kaldero(D, cx, rim_y, rx, 176, 504, ry=62))
    sd = ellipse_d(cx, rim_y + 2, rx - 6, 56)
    rnd = random.Random(505)
    inner = [f'<path d="{sd}" fill="#D89A6A"/>',
             f'<path d="{sd}" fill="{D.rad([(0, "#F6D2A8", 0.9), (0.6, "#E0A878", 0.5), (1, "#A8643A", 0.7)], 0.42, 0.4, 0.7)}"/>']
    for _ in range(22):
        x, y = cx + rnd.uniform(-rx, rx) * 0.85, rim_y + rnd.uniform(-46, 46)
        inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3, 8):.1f}" ry="{rnd.uniform(1.4, 3):.1f}" fill="#FFE8B8" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    pcs = []
    for k, (dx, dy, a) in enumerate(((-70, -18, 20), (40, -26, -30), (-10, 18, 10), (80, 14, 40), (-100, 22, -20))):
        pcs.append(pork_rib(D, cx + dx, rim_y + dy, 24, a, 510 + k))
    for k, (dx, dy) in enumerate(((-36, -30), (10, -6), (98, -18), (-120, -4), (54, 30), (-52, 34))):
        pcs.append(radish_slice(cx + dx, rim_y + dy, 13, 520 + k))
    for k, (dx, dy, a) in enumerate(((-90, -30, -150), (-20, -40, -80), (60, -4, -30), (110, -30, -100), (-60, 10, 160), (30, 38, -10), (-130, 18, 120), (120, 30, 20))):
        pcs.append(kangkong_leaf(D, cx + dx, rim_y + dy, 40, a, 530 + k))
    for k, (dx, dy) in enumerate(((0, -36), (-80, 36), (92, 36), (24, 4))):
        pcs.append(f'<circle cx="{cx + dx:.1f}" cy="{rim_y + dy:.1f}" r="5.5" fill="#B8E08A" stroke="#3E7A2A" stroke-width="2"/><circle cx="{cx + dx:.1f}" cy="{rim_y + dy:.1f}" r="2.4" fill="#E8F4D0"/>')
    for k, (dx, dy, a) in enumerate(((-30, 30, 30), (118, 0, -30), (-110, -26, 10))):
        pcs.append(tomato_wedge(D, cx + dx, rim_y + dy, 15, a, 540 + k))
    for k, (dx, dy, a) in enumerate(((-6, -16, -20), (70, 24, 15))):
        pcs.append(long_chili(D, cx + dx, rim_y + dy, 52, a, 550 + k))
    for k, (dx, dy, a) in enumerate(((44, -40, 70), (-56, -6, 20), (100, 40, -40))):
        x, y = cx + dx, rim_y + dy
        pcs.append(taper([(x - math.cos(math.radians(a)) * 14, y - math.sin(math.radians(a)) * 14), (x + math.cos(math.radians(a)) * 14, y + math.sin(math.radians(a)) * 14)], 9, 9, "#5EA83A"))
        pcs.append(taper([(x - math.cos(math.radians(a)) * 12, y - math.sin(math.radians(a)) * 12 - 2), (x + math.cos(math.radians(a)) * 12, y + math.sin(math.radians(a)) * 12 - 2)], 2.5, 2.5, "#B8E890", 0.8))
    for _ in range(14):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * (rx - 10) * r, rim_y + math.sin(a) * 48 * r
        pcs.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 4):.1f}" fill="none" stroke="#FFF2D8" stroke-width="1.2" opacity="0.8"/>')
    out.append(clipped(D, sd, inner + pcs))
    # ladle resting in the pot
    out.append(taper([(cx + 96, rim_y + 6), (cx + 170, rim_y - 120)], 9, 7, "#8A94A4"))
    out.append(taper([(cx + 98, rim_y + 2), (cx + 168, rim_y - 120)], 3, 2, "#FFFFFF", 0.9))
    out.append(steam(cx - 20, rim_y - 50, 100, 506, "#FFFFFF", 3, 46, 10, 0.5))
    # sampalok pods and a dish of patis with chili on the table
    out.append(tamarind_pod(D, 76, 500, 92, -12, 560))
    out.append(tamarind_pod(D, 96, 530, 84, 6, 561, open_=True))
    out.append(sawsawan(D, 500, 506, 30, 562, sauce="#8A4A1A", bits="vinegar"))
    for k in range(3):
        out.append(sili(D, 486 + k * 9, 504 + (k % 2) * 6, 20, -60 + k * 30, 563 + k))
    out.append(long_chili(D, 200, 528, 60, -8, 566))
    # lettering
    out.append(letters(D, 300, 136, "sinigang", SERIF_IT, 136, "#1E5A4A", ["#2E7A62", "#0E3A2E", "#4A9A80"], 570, max_w=430,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#A8E0C8"))
    out.append(ruled(300, 182, "PAHINGI NG SABAW", "#B8402A", font=JOS, size=21, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 571)


# ================================================================ 8. lumpia — the party tray, already half gone
def lumpia_roll(D, x0, y0, x1, y1, w, seed, cut_left=False, cut_right=False):
    """One lumpiang shanghai: a thin, golden, blistered roll; cut ends show the pink-brown filling."""
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    L = math.hypot(x1 - x0, y1 - y0)
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((x0 + (x1 - x0) * t + nx * w / 2 * (1 + 0.04 * math.sin(i * 2.3 + seed)), y0 + (y1 - y0) * t + ny * w / 2))
    for i in range(8, -1, -1):
        t = i / 8
        pts.append((x0 + (x1 - x0) * t - nx * w / 2, y0 + (y1 - y0) * t - ny * w / 2 * (1 + 0.04 * math.cos(i * 1.7 + seed))))
    d = smooth_closed(pts)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    rnd0 = random.Random(seed)
    base = mix("#D8862A", rnd0.choice(["#E8A040", "#B8661A"]), rnd0.uniform(0, 0.5))
    g = D.lin([(0, "#FFE6A8", 0.75), (0.3, base, 0), (0.62, base, 0), (1, "#5A2606", 0.75)], mx - nx * w / 2, my - ny * w / 2, mx + nx * w / 2, my + ny * w / 2, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{base}"/>', f'<path d="{d}" fill="{g}"/>',
           strokes(D.nid(), d, bbox(pts), ["#FFE0A0", "#8A4410", "#F2B860"], seed, n=int(L / 5) + 4, angle=math.degrees(a), length=(6, 16), width=(0.8, 2), opacity=(0.2, 0.5))]
    d = smooth_closed(pts)
    rnd = random.Random(seed)
    bl = []
    for _ in range(int(L / 4)):
        t = rnd.uniform(0.05, 0.95)
        o = rnd.uniform(-0.4, 0.3)
        x, y = x0 + (x1 - x0) * t + nx * w * o, y0 + (y1 - y0) * t + ny * w * o
        r = rnd.uniform(1, 2.4)
        bl.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#FFE8A8", "#A85A14"])}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    # spiral seam of the wrapper
    for k in range(int(L / 26)):
        t = (k + 0.5) / max(1, int(L / 26))
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        bl.append(pline([(x - nx * w * 0.5 - math.cos(a) * 6, y - ny * w * 0.5 - math.sin(a) * 6), (x + nx * w * 0.5 + math.cos(a) * 6, y + ny * w * 0.5 + math.sin(a) * 6)], "#A85A14", 1.1, seed + k, 0.45, 1))
    out.append(clipped(D, d, bl))
    out.append(taper([(x0 + math.cos(a) * 4 + nx * w * 0.22, y0 + math.sin(a) * 4 - ny * w * 0.28), (x1 - math.cos(a) * 4 + nx * w * 0.22, y1 - math.sin(a) * 4 - ny * w * 0.28)], 2.4, 1.6, "#FFF2C8", 0.7))
    out.append(ink(d, "#5A2A08", 1.2, seed + 2, 2, 0.6))
    for cut, (cx_, cy_) in ((cut_left, (x0, y0)), (cut_right, (x1, y1))):
        if cut:
            end = rot(blob_pts(cx_, cy_, w * 0.22, w * 0.5, seed + 7, 0.06, 12), cx_, cy_, math.degrees(a))
            out.append(f'<path d="{smooth_closed(end)}" fill="#E8B060" stroke="#8A4410" stroke-width="1.2"/>')
            out.append(f'<path d="{blob(cx_, cy_, w * 0.16, w * 0.38, seed + 8, 0.12, 10, math.degrees(a))}" fill="#B8785A"/>')
            for j in range(4):
                out.append(f'<circle cx="{cx_ + rnd.uniform(-2, 2):.1f}" cy="{cy_ + rnd.uniform(-w * 0.3, w * 0.3):.1f}" r="1.3" fill="{rnd.choice(["#F2802A", "#6AA84A", "#F6E8D0"])}"/>')
    return "".join(out)


@design("lumpia")
def lumpia():
    D = Doc2("ph-lu")
    out = [paper(D.nid(), "#FCE6B8", "#8A6A3A", 601)]
    rnd = random.Random(602)
    dots = "".join(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 600):.1f}" r="{rnd.uniform(3, 6):.1f}" fill="{rnd.choice(["#F2766A", "#5A86D8", "#F6C51E", "#7AC08A", "#EE6A98"])}" opacity="0.5"/>' for _ in range(70))
    out.append(dots)
    out.append(soft_glow(D, 300, 380, 300, "#FFF8E8", 0.7))
    out.append(blooms(603, ["#F6C878", "#F2A890"], 6, (0, 0, 600, 600), (90, 170), (0.06, 0.12)))
    # foil catering tray in perspective
    tl, tr, br, bl = (124, 262), (476, 262), (538, 520), (62, 520)
    rim = [tl, tr, br, bl]
    out.append(cast(D, 312, 528, 260, 22, strength=0.45, seed=604))
    outer = poly_pts([(tl[0] - 10, tl[1] - 8), (tr[0] + 10, tr[1] - 8), (br[0] + 12, br[1] + 10), (bl[0] - 12, bl[1] + 10)], 14, 605, 0.6)
    foil = ("#FFFFFF", "#D8DEE6", "#7A8494")
    out.append(painted(D, outer, foil, 605, sdir=(0.6, 0.8), sk=0.12, angle=-30, n=60, slen=(6, 18), sw=(0.8, 2), cols=["#FFFFFF", "#9AA4B4", "#E8EEF4"], inkw=1.6, inkc="#3A404A", hi=0.5))
    inner_pts = poly_pts([(tl[0] + 12, tl[1] + 10), (tr[0] - 12, tr[1] + 10), (br[0] - 14, br[1] - 10), (bl[0] + 14, bl[1] - 10)], 14, 606, 0.5)
    idd = smooth_closed(inner_pts)
    inner = [f'<path d="{idd}" fill="#C8D0DA"/>']
    for _ in range(40):
        x, y = rnd.uniform(70, 530), rnd.uniform(270, 512)
        inner.append(pline([(x, y), (x + rnd.uniform(-14, 14), y + rnd.uniform(-8, 8)), (x + rnd.uniform(-20, 20), y + rnd.uniform(-10, 10))], rnd.choice(["#FFFFFF", "#8A94A4"]), 1.2, rnd.randint(0, 99), 0.5, 1))
    for _ in range(5):
        x, y = rnd.uniform(380, 500), rnd.uniform(420, 500)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(10, 20), rnd.uniform(5, 9), rnd.randint(0, 99), 0.2, 10)}" fill="#E8B060" opacity="0.4"/>')
    # rows of rolls (back to front); the front-right corner is already emptied
    rows = 8
    for j in range(rows):
        t = (j + 0.5) / rows
        y = tl[1] + 22 + (br[1] - tl[1] - 40) * t
        xl = tl[0] + (bl[0] - tl[0]) * t + 22
        xr = tr[0] + (br[0] - tr[0]) * t - 22
        w = 24 + 9 * t
        pieces = 3
        seg = (xr - xl) / pieces
        for k in range(pieces):
            if (j >= 5 and k == 2) or (j >= 6 and k == 1):
                for _ in range(5):
                    inner.append(f'<circle cx="{xl + seg * (k + rnd.random()):.1f}" cy="{y + rnd.uniform(-6, 6):.1f}" r="{rnd.uniform(1, 2.2):.1f}" fill="#C8802A" opacity="0.8"/>')
                continue
            a = xl + seg * k + 3
            b = xl + seg * (k + 1) - 3
            tilt = rnd.uniform(-3, 3)
            inner.append(lumpia_roll(D, a + rnd.uniform(-2, 2), y - tilt, b + rnd.uniform(-2, 2), y + tilt, w * rnd.uniform(0.92, 1.05), 610 + j * 5 + k, cut_left=k > 0, cut_right=k < pieces - 1))
    out.append(clipped(D, idd, inner))
    out.append(ink(idd, "#5A6270", 1.4, 607, 1, 0.6))
    # masking-tape label on the rim
    tape = rot(rect_pts(176, 500, 336, 532, 12, 608, 0.6), 256, 516, -3)
    out.append(painted(D, tape, ("#FFF8E0", "#F2E2B4", "#B8A270"), 608, sk=0.1, angle=0, n=8, inkw=1.2, hi=0.3))
    out.append(f'<text x="256" y="524" text-anchor="middle" {MONO} font-size="{fit_size("PARA SA PARTY", MONO, 18, 146)}" fill="#3A3A8A" transform="rotate(-3 256 516)">PARA SA PARTY</text>')
    # sweet chili dip with one roll dunked
    dx, dy = 470, 236
    out.append(sawsawan(D, dx, dy, 42, 620, sauce="#E0502A", bits="vinegar"))
    out.append(lumpia_roll(D, dx - 4, dy - 2, dx + 66, dy - 52, 22, 621, cut_left=True))
    out.append(f'<path d="{blob(dx + 6, dy - 8, 10, 7, 622, 0.2, 8)}" fill="#E0502A" opacity="0.85"/>')
    # one hand-me-down napkin
    nap = rot(rect_pts(70, 206, 166, 262, 14, 623, 0.8), 118, 234, -10)
    out.append(painted(D, nap, ("#FFFFFF", "#F6F0F4", "#C8B8C8"), 623, sk=0.15, angle=20, n=8, inkw=1.2, hi=0.4))
    out.append(lumpia_roll(D, 90, 236, 150, 222, 22, 624, cut_right=True))
    # lettering
    out.append(letters(D, 300, 146, "lumpia", SERIF_IT, 136, "#B0281E", ["#D0402A", "#7A100A", "#E8603A"], 630, max_w=380,
                       shadow="#FFF4D8", soff=(0.018, 0.03), angle=-40, hi="#F8A880"))
    out.append(ruled(300, 190, "LAGING KULANG", "#2E4A9A", font=JOS, size=22, ls=8, line_w=38, gap=14))
    return finish_b(D, out, 631)


# ================================================================ 9. pancit — birthday noodles on a banana-leaf bilao
def bilao(D, cx, cy, R, seed, ry=None):
    """Round woven bamboo tray (bilao) seen from above, rim bound with rattan."""
    ry = ry or R
    d = ellipse_d(cx, cy, R, ry, 48)
    out = [cast(D, cx + 12, cy + 16, R * 1.04, ry * 1.02, strength=0.45, seed=seed)]
    c = 9
    t = [f'<rect width="{2 * c}" height="{2 * c}" fill="#D8B070"/>',
         f'<rect x="0.5" y="0.5" width="{c - 1}" height="{2 * c - 1}" rx="2" fill="#E8C888"/>',
         f'<rect x="{c + 0.5}" y="0.5" width="{c - 1}" height="{2 * c - 1}" rx="2" fill="#C89A58"/>',
         f'<path d="M 0 {c} L {2 * c} {c}" stroke="#8A6A30" stroke-width="0.8" opacity="0.6"/>']
    pat = D.pattern(2 * c, 2 * c, "".join(t), transform="rotate(45)")
    out.append(f'<path d="{d}" fill="{pat}"/>')
    out.append(clipped(D, d, [f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0.0), (0.7, "#3A2408", 0.05), (1, "#3A2408", 0.35)])}"/>']))
    out.append(ink(d, "#6A4A1A", 2, seed, 1, 0.7))
    rim = ell_pts(cx, cy, R - 4, ry - 4, 0, 360, 72)
    out.append(taper(rim, 13, 13, "#B8884A"))
    for i in range(0, 72, 2):
        x, y = rim[i]
        out.append(f'<path d="{blob(x, y, 6, 3.4, seed + i, 0.1, 8, i * 5 + 45)}" fill="#E8C080" opacity="0.9"/>')
    out.append(ink(ellipse_d(cx, cy, R - 11, ry - 11, 48), "#6A4A1A", 1.4, seed + 1, 1, 0.6))
    return "".join(out)


def leaf_disc(D, cx, cy, R, seed, pal=SAGING):
    """Circle of banana leaf lining a tray: a few overlapping pieces with radiating veins."""
    out = []
    rnd = random.Random(seed)
    for k in range(4):
        a0 = k * 90 + rnd.uniform(-10, 10)
        pts = [(cx, cy)] + [(cx + math.cos(math.radians(a)) * R * rnd.uniform(0.98, 1.02), cy + math.sin(math.radians(a)) * R * rnd.uniform(0.98, 1.02)) for a in range(int(a0 - 8), int(a0 + 104), 8)]
        d = smooth_closed(pts)
        col = mix(pal[1], rnd.choice([pal[0], pal[2]]), rnd.uniform(0.1, 0.3))
        lines = [f'<path d="{d}" fill="{col}"/>']
        am = math.radians(a0 + 45)
        for j in range(-30, 31, 3):
            off = j * 4
            lines.append(f'<path d="M {cx + math.cos(am + 1.57) * off:.1f} {cy + math.sin(am + 1.57) * off:.1f} l {math.cos(am) * R * 1.2:.1f} {math.sin(am) * R * 1.2:.1f}" stroke="{rnd.choice([pal[0], pal[2]])}" stroke-width="1.2" opacity="0.35"/>')
        out.append(clipped(D, d, lines))
        out.append(ink(d, "#1E4A16", 1.2, seed + k, 1, 0.5))
    return "".join(out)


def noodle_pile(seed, cx, cy, rx, ry, n=260, cols=("#F2D488", "#DDB058", "#C8923A", "#FBE8B0"), w=2.4):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.95
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        L = rnd.uniform(20, 60)
        t = rnd.uniform(0, 6.28)
        pts = [(x, y)]
        for k in range(4):
            t += rnd.uniform(-1.2, 1.2)
            x, y = x + math.cos(t) * L / 4, y + math.sin(t) * L / 4
            pts.append((x, y))
        out.append(f'<path d="{smooth_open(pts)}" stroke="{rnd.choice(cols)}" stroke-width="{w * rnd.uniform(0.8, 1.2):.1f}" fill="none" stroke-linecap="round" opacity="0.95"/>')
    return "".join(out)


def carrot_strip(x, y, L, ang, col="#F2802A"):
    a = math.radians(ang)
    return (f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * L:.1f} {math.sin(a) * L:.1f}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M {x:.1f} {y - 1:.1f} l {math.cos(a) * L * 0.8:.1f} {math.sin(a) * L * 0.8:.1f}" stroke="#FFC890" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>')


def snow_pea(D, x, y, L, ang, seed):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = [(x, y), (x + ux * L * 0.5 + nx * L * 0.2, y + uy * L * 0.5 + ny * L * 0.2), (x + ux * L, y + uy * L), (x + ux * L * 0.5 - nx * L * 0.12, y + uy * L * 0.5 - ny * L * 0.12)]
    return painted(D, pts, ("#B8E890", "#5EAE3E", "#2A6A1A"), seed, sk=0.2, angle=ang, n=3, inkw=1, hi=0.4)


def shrimp_top(D, x, y, s, ang, seed):
    out = []
    for k in range(5):
        t = k / 4
        a = math.radians(ang + t * 200)
        px, py = x + math.cos(a) * s * 0.5, y + math.sin(a) * s * 0.5
        r = s * (0.28 - 0.1 * t)
        out.append(f'<path d="{blob(px, py, r, r * 0.8, seed + k, 0.08, 8)}" fill="{["#FF9A7A", "#F27A5A"][k % 2]}" stroke="#B8401E" stroke-width="1"/>')
    out.append(f'<path d="{blob(x + math.cos(math.radians(ang)) * s * 0.5, y + math.sin(math.radians(ang)) * s * 0.5, s * 0.12, s * 0.08, seed + 9, 0.1, 6)}" fill="#FFF0E0" opacity="0.8"/>')
    return "".join(out)


def egg_half_top(D, x, y, r, seed, ang=0):
    out = [painted(D, rot(blob_pts(x, y, r * 1.2, r * 0.85, seed, 0.04, 14), x, y, ang), ("#FFFFFF", "#F8F4EC", "#C8C0B0"), seed, sk=0.15, n=3, inkw=1.0, hi=0.4)]
    out.append(painted(D, blob_pts(x + 1, y, r * 0.55, r * 0.5, seed + 1, 0.05, 12), ("#FFE89A", "#F6C030", "#B8800A"), seed + 1, sk=0.2, n=3, inkw=0.8, inkop=0.4, hi=0.4))
    return "".join(out)


@design("pancit")
def pancit():
    D = Doc2("ph-pc")
    # festive red tablecloth seen from above
    out = [paper(D.nid(), "#C8302A", "#5A0A08", 701, 0.6)]
    rnd = random.Random(702)
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-40, -10, 600, 600), ["#E04A3A", "#8A1410", "#D8382E"], 703, n=140, angle=-4, length=(60, 180), width=(4, 12), opacity=(0.08, 0.2)))
    for k in range(-2, 14):
        out.append(f'<path d="M {k * 52:.0f} -10 L {k * 52 - 80:.0f} 610" stroke="#F6C84A" stroke-width="2" opacity="0.18"/>')
    out.append(soft_glow(D, 300, 380, 300, "#FFB070", 0.35))
    cx, cy, R = 300, 382, 168
    out.append(bilao(D, cx, cy, R, 704))
    out.append(leaf_disc(D, cx, cy, R - 16, 705))
    # the noodles: a generous golden mound
    mound = blob(cx, cy + 4, 124, 120, 706, 0.06, 20)
    out.append(cast(D, cx + 8, cy + 14, 130, 124, strength=0.35, seed=706))
    out.append(f'<path d="{mound}" fill="#D8A850"/>')
    out.append(clipped(D, mound, [noodle_pile(707, cx, cy + 4, 128, 124, 420),
                                   f'<path d="{mound}" fill="{D.rad([(0, "#FFFFFF", 0.0), (0.6, "#5A3A0A", 0.05), (1, "#5A3A0A", 0.35)], 0.45, 0.42, 0.6)}"/>']))
    out.append(ink(mound, "#8A5A1A", 1.4, 708, 1, 0.5))
    # toppings
    tp = []
    for _ in range(26):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 105
        tp.append(carrot_strip(cx + math.cos(a) * r, cy + math.sin(a) * r, rnd.uniform(14, 24), rnd.uniform(0, 180)))
    for _ in range(18):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 105
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        tp.append(f'<path d="{blob(x, y, rnd.uniform(8, 14), rnd.uniform(3, 5), rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8F4C8", "#C8E098", "#F4F8E0"])}" stroke="#8AB060" stroke-width="0.8"/>')
    for k in range(9):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 100
        tp.append(snow_pea(D, cx + math.cos(a) * r, cy + math.sin(a) * r, 26, rnd.uniform(0, 360), 710 + k))
    for k in range(10):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 96
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        tp.append(painted(D, rot(blob_pts(x, y, 13, 7, 720 + k, 0.15, 10), x, y, rnd.uniform(0, 180)), ("#F8E8D0", "#E0C098", "#9A7A4A"), 720 + k, sk=0.2, n=3, inkw=0.9, hi=0.4))
    for k in range(7):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 90
        tp.append(shrimp_top(D, cx + math.cos(a) * r, cy + math.sin(a) * r, 26, rnd.uniform(0, 360), 730 + k))
    for _ in range(30):
        x, y = cx + rnd.uniform(-100, 100), cy + rnd.uniform(-100, 100)
        if math.hypot(x - cx, y - cy) < 110:
            tp.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="none" stroke="#3E9A2E" stroke-width="1.8"/>')
    for k, (dx, dy, a) in enumerate(((-30, -40, 20), (34, -20, -30), (-6, 30, 60))):
        tp.append(egg_half_top(D, cx + dx, cy + dy, 16, 740 + k, a))
    out.append("".join(tp))
    # calamansi halves around the rim
    for k in range(9):
        a = math.radians(-60 + k * 40)
        out.append(calamansi(D, cx + math.cos(a) * 142, cy + math.sin(a) * 142, 13, 750 + k, cut=True))
    # a fork lifting one long, long noodle
    fx, fy = 486, 268
    strand = [(cx + 40, cy - 40), (cx + 70, cy - 90), (cx + 120, cy - 130), (fx - 6, fy + 10)]
    for k in range(4):
        out.append(ink(smooth_open([(x + k * 3 - 4, y + k * 1.5) for x, y in strand]), ["#F2D488", "#DDB058", "#FBE8B0", "#C8923A"][k], 3, 760 + k, 1, 1))
    out.append(cast(D, fx + 30, fy + 40, 40, 10, strength=0.3, seed=765))
    tine = [(fx - 14, fy + 8), (fx + 14, fy - 4), (fx + 22, fy - 30), (fx - 6, fy - 22)]
    out.append(chrome(D, densify(tine, 6), 766, 1))
    for k in range(4):
        out.append(pline([(fx - 10 + k * 7, fy + 4 - k * 3), (fx - 18 + k * 7, fy + 24 - k * 3)], "#8A94A4", 2.4, 767 + k, 0.9, 1))
    out.append(taper([(fx + 8, fy - 26), (fx + 30, fy - 76), (fx + 40, fy - 100)], 8, 10, "#C8CED6"))
    out.append(taper([(fx + 10, fy - 30), (fx + 31, fy - 78)], 2, 2, "#FFFFFF", 0.9))
    for k in range(3):
        out.append(ink(smooth_open([(fx - 8 + k * 6, fy + 8), (fx - 12 + k * 6, fy + 30), (fx - 6 + k * 7, fy + 46)]), "#F2D488", 3, 770 + k, 1, 1))
    # lettering
    out.append(letters(D, 290, 144, "pancit", SERIF_IT, 120, "#FFF0D0", ["#FFFFFF", "#FFE0A8", "#FFF4D8"], 780, max_w=360,
                       shadow="#5A0A08", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(290, 192, "PAMPAHABA NG BUHAY", "#FFD25A", font=JOS, size=20, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 781, "#3A0A08", 0.7)


# ================================================================ 10. lechon — the fiesta table under the banderitas
def banderitas(D, x0, y0, x1, y1, sag, n, seed, size=26, cols=None):
    """Fiesta banderitas: little cut-paper / plastic squares strung on a line, every one a different colour."""
    cols = cols or ["#E8304A", "#F6C51E", "#1E9AD8", "#2EB05A", "#EE6A98", "#F28A2A", "#8A5AD0", "#FFFFFF"]
    rnd = random.Random(seed)

    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)

    out = [pline([pt(i / 30) for i in range(31)], "#4A3A2A", 1.6, seed, 0.9, 1)]
    for i in range(n):
        t = (i + 0.5) / n
        x, y = pt(t)
        a = math.atan2(pt(t + 0.01)[1] - pt(t - 0.01)[1], 0.02 * (x1 - x0))
        h = size * rnd.uniform(0.95, 1.15)
        w = size * 0.8
        sway = rnd.uniform(-6, 6)
        pts = rot([(x - w / 2, y), (x + w / 2, y), (x + w / 2 + sway * 0.3, y + h), (x - w / 2 + sway * 0.3, y + h)], x, y, math.degrees(a) + sway)
        col = cols[(i + rnd.randint(0, 1)) % len(cols)]
        dd = hg.org_poly(pts, seed + i, 0.4, 8, 1.2)
        out.append(f'<path d="{dd}" fill="{col}" opacity="0.92"/>')
        # cut-paper pattern: a little scalloped hole and fold line
        cx_, cy_ = (pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2
        out.append(f'<path d="{blob(cx_, cy_ + 1, w * 0.18, h * 0.16, seed + i, 0.25, 8)}" fill="{lt(col, 0.6) if col != "#FFFFFF" else "#E8E0D0"}" opacity="0.9"/>')
        out.append(f'<path d="M {pts[0][0]:.1f} {pts[0][1] + 3:.1f} L {pts[1][0]:.1f} {pts[1][1] + 3:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.5"/>')
        out.append(ink(dd, INK, 0.9, seed + i, 1, 0.45))
    return "".join(out)


LECHON_HIND = [(-150, 18), (-196, 30), (-232, 40), (-246, 50), (-236, 60), (-196, 56), (-150, 48)]
LECHON_FORE = [(86, 28), (132, 42), (166, 44), (182, 54), (170, 62), (122, 58), (80, 50)]


def lechon_pig(D, X, Y, s, seed):
    """Whole roast pig on its bamboo spit, side view facing right: lacquered amber crackling, folded legs, closed eye."""
    P = lambda x, y: (X + x * s, Y + y * s)
    PP = lambda pts: [P(x, y) for x, y in pts]
    out = [cast(D, X + 10 * s, Y + 64 * s, 230 * s, 20 * s, strength=0.5, seed=seed)]
    skin = ("#F2A050", "#C0581E", "#5E1E06")
    # bamboo spit poking out at both ends
    out.append(taper([P(-250, 2), P(-196, 4)], 14 * s, 14 * s, "#D8C07A"))
    out.append(taper([P(212, -8), P(262, -10)], 14 * s, 14 * s, "#D8C07A"))
    for x0, y0 in ((-250, 2), (262, -10)):
        out.append(f'<path d="{ellipse_d(*P(x0, y0), 4 * s, 7 * s, 12)}" fill="#F2E2A8" stroke="#8A6A2A" stroke-width="1.2"/>')
    out.append(pline([P(-240, 8), P(-200, 9)], "#8A6A2A", 1.2, seed, 0.6, 1))
    # far legs (darker, behind the body)
    for leg in (LECHON_HIND, LECHON_FORE):
        out.append(painted(D, PP([(x + 14, y - 6) for x, y in leg]), tuple(dk(c, 0.25) for c in skin), seed + 3, sk=0.25, n=6, inkw=1.4, inkc="#3A1004", hi=0.3))
    # body
    body = PP([(-208, 6), (-196, -40), (-150, -74), (-60, -92), (40, -94), (120, -82), (170, -60), (196, -30), (204, 6), (190, 38), (120, 54), (0, 58), (-120, 54), (-186, 40)])
    out.append(painted(D, body, skin, seed, sdir=(0.3, 1), sk=0.2, angle=-10, n=60, slen=(14, 40), sw=(1.5, 4), cols=["#FFC070", "#8A2E08", "#E07A2A", "#FFD898"], inkw=2.2, inkc="#3A1004", hi=0.5, hik=0.08))
    bd = smooth_closed(body)
    rnd = random.Random(seed)
    gl = [f'<path d="{bd}" fill="{D.lin([(0, "#FFE0A0", 0.35), (0.35, "#C0581E", 0), (1, "#2A0A02", 0.55)])}"/>']
    # crackle blisters and long lacquer reflections
    for _ in range(140):
        x, y = rnd.uniform(-200, 200), rnd.uniform(-90, 50)
        r = rnd.uniform(1, 2.6) * s
        gl.append(f'<circle cx="{P(x, y)[0]:.1f}" cy="{P(x, y)[1]:.1f}" r="{r:.1f}" fill="{rnd.choice(["#FFE0A0", "#7A2A06", "#FFC070"])}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    gl.append(taper(PP([(-170, -50), (-100, -78), (0, -88), (100, -78), (160, -56)]), 4 * s, 3 * s, "#FFF4D8", 0.75))
    gl.append(taper(PP([(-150, -38), (-60, -62), (30, -66)]), 2 * s, 1.5 * s, "#FFFFFF", 0.6))
    for k in range(5):
        x = -140 + k * 60
        gl.append(taper(PP([(x, -60), (x + 6, -20), (x + 2, 30)]), 3 * s, 1, "#7A2A06", 0.35))
    out.append(clipped(D, bd, gl))
    # near legs: hind legs stretched back, fore legs folded under the chest
    for k, leg in enumerate((LECHON_HIND, LECHON_FORE)):
        out.append(painted(D, PP(leg), skin, seed + 7 + k, sdir=(0.3, 1), sk=0.25, n=8, inkw=1.6, inkc="#3A1004", hi=0.45))
        hx, hy = P(*leg[3])
        out.append(f'<path d="{blob(hx, hy, 7 * s, 6 * s, seed + 9 + k, 0.1, 8)}" fill="#3A1A0A"/>')
    # head: long snout, flopped ear, closed eye
    head = PP([(140, -72), (182, -82), (214, -70), (240, -50), (264, -36), (280, -24), (282, -4), (272, 8), (246, 14), (212, 22), (178, 26), (150, 2)])
    out.append(painted(D, head, skin, seed + 5, sdir=(0.3, 1), sk=0.2, angle=-10, n=20, inkw=2, inkc="#3A1004", hi=0.5))
    out.append(clipped(D, smooth_closed(head), [f'<path d="{smooth_closed(head)}" fill="{D.lin([(0, "#FFE0A0", 0.3), (0.4, "#C0581E", 0), (1, "#2A0A02", 0.5)])}"/>']))
    out.append(f'<path d="{ellipse_d(*P(281, -14), 6 * s, 12 * s, 14)}" fill="#8A3410" stroke="#3A1004" stroke-width="1.4"/>')
    for dy in (-18, -9):
        out.append(f'<ellipse cx="{P(282, dy)[0]:.1f}" cy="{P(282, dy)[1]:.1f}" rx="{1.5 * s:.1f}" ry="{2.4 * s:.1f}" fill="#2A0802"/>')
    out.append(pline(PP([(206, -46), (215, -42), (224, -46)]), "#2A0802", 2.2 * s, seed, 0.9, 1))
    for k in range(3):
        out.append(pline(PP([(208 + k * 6, -44), (206 + k * 6, -38)]), "#2A0802", 1.2, seed + k, 0.7, 1))
    out.append(pline(PP([(244, 10), (258, 8), (270, 2)]), "#2A0802", 1.8 * s, seed + 3, 0.8, 1))
    ear = PP([(178, -70), (196, -104), (226, -96), (238, -70), (214, -64)])
    out.append(painted(D, ear, tuple(dk(c, 0.1) for c in skin), seed + 6, sdir=(0.3, 1), sk=0.25, n=6, inkw=1.6, inkc="#3A1004", hi=0.5))
    out.append(taper(PP([(178, -56), (236, -52), (266, -30)]), 2.5 * s, 1.5, "#FFF0C8", 0.75))
    return "".join(out)


@design("lechon")
def lechon():
    D = Doc2("ph-lc")
    out = [sky(D, [(0, "#5AA8E8"), (0.6, "#A8DCF4"), (1, "#E8F6F8")], 801, 600, ["#7ABCEE", "#E8F6FF", "#5A9ADA"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 470, 260, 180, 802, pal=("#FFFFFF", "#F4FAFF", "#C8DCF0")))
    out.append(puff_cloud(D, 110, 236, 140, 803, pal=("#FFFFFF", "#F4FAFF", "#C8DCF0")))
    # mango trees behind the yard
    for k, (x, y, rx_, ry_) in enumerate(((60, 380, 120, 90), (230, 396, 110, 70), (420, 384, 130, 84), (580, 392, 100, 80))):
        out.append(dab_crown(D, x, y, rx_, ry_, [("#8AC86A", "#3E8A3A", "#1A4A1E"), ("#A8D878", "#5AA048", "#2A5A22")], 804 + k, n=120, size=(8, 16), inkw=0))
    out.append(f'<path d="M -10 420 L 610 420 L 610 470 L -10 470 Z" fill="#7AB05A"/>')
    # fiesta table with a white cloth and a scalloped lace edge
    out.append(f'<path d="M -10 446 L 610 446 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FFFFFF"), (1, "#E8E2D8")])}"/>')
    out.append(strokes(D.nid(), "M -10 446 L 610 446 L 610 610 L -10 610 Z", (-40, 446, 600, 600), ["#FFFFFF", "#C8C0B4"], 805, n=40, angle=-2, length=(40, 120), width=(2, 5), opacity=(0.15, 0.35)))
    lace = []
    for k in range(-1, 26):
        x = k * 25
        lace.append(f'<path d="M {x} 566 q 12 18 25 0" fill="#FFFFFF" stroke="#C8C0B4" stroke-width="1.2"/><circle cx="{x + 12.5:.1f}" cy="{574}" r="3" fill="none" stroke="#C8C0B4" stroke-width="1"/>')
    out.append(f'<path d="M -10 566 L 610 566 L 610 610 L -10 610 Z" fill="#E8DCC8"/>')
    out.append("".join(lace))
    # banana leaves under the pig
    for k, (ang, L) in enumerate(((182, 270), (-4, 270), (196, 220), (-16, 220))):
        out.append(banana_leaf(D, 300, 500, ang, L, 44, 806 + k, pal=SAGING))
    out.append(lechon_pig(D, 290, 440, 0.86, 810))
    # sarsa (liver sauce) bowl and lemongrass
    out.append(sawsawan(D, 122, 528, 36, 811, sauce="#7A4A1E", bits="vinegar"))
    for k in range(3):
        out.append(taper([(430 + k * 10, 540), (520 + k * 6, 520 - k * 4)], 6, 3, ["#C8E098", "#A8C870", "#E0EEB0"][k]))
    out.append(banderitas(D, -20, 196, 620, 208, 50, 17, 812, size=26))
    out.append(banderitas(D, -20, 232, 620, 222, 40, 15, 813, size=24))
    # lettering
    out.append(letters(D, 300, 146, "lechon", SERIF_IT, 124, "#8A2A0A", ["#A83E14", "#5A1404", "#C85A22"], 820, max_w=380,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#F8B080"))
    out.append(ruled(300, 180, "MALUTONG ANG BALAT", "#1E4AA0", font=JOS, size=20, ls=6, line_w=28, gap=12))
    return finish_b(D, out, 821)


# ================================================================ 11. ube — the purple yam, cut open, and a tin of halaya
def ube_tuber(D, cx, cy, L, W, ang, seed, cut=False):
    """Purple yam: knobbly elongated tuber with rough grey-brown-violet skin and root hairs; cut=True shows the
    vivid violet flesh with paler rings and white flecks (the tuber then ends at the cut)."""
    rnd = random.Random(seed)
    top, bot = [], []
    for i in range(15):
        t = i / 14
        w = W * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.1)) ** 0.6) * (1 + rnd.uniform(-0.08, 0.08))
        if cut:
            w = W * (0.35 + 0.65 * math.sin(math.pi * (0.5 + t * 0.5)) ** 0.5) * (1 + rnd.uniform(-0.05, 0.05))
        top.append((cx - L / 2 + L * t, cy - w / 2))
        bot.append((cx - L / 2 + L * t, cy + w / 2))
    pts = rot(top + bot[::-1], cx, cy, ang)
    out = [cast(D, cx + 8, cy + W * 0.5, L * 0.55, W * 0.25, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#D0A8B8", "#9A6488", "#4E2A44"), seed, sdir=(0.4, 0.9), sk=0.22, angle=ang + 80, n=30, sw=(1, 2.6),
                       cols=["#E0B8C8", "#6A3A5A", "#B07AA0", "#5A3828"], inkw=1.6, inkc="#2A1420", hi=0.4))
    d = smooth_closed(pts)
    tex = []
    for _ in range(int(L * 0.5)):
        x, y = cx + rnd.uniform(-L, L) * 0.5, cy + rnd.uniform(-W, W) * 0.5
        tex.append(f'<path d="{blob(x, y, rnd.uniform(2, 4), rnd.uniform(1, 2), rnd.randint(0, 999), 0.3, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(["#3A2230", "#D8B8C0", "#5A3A28"])}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out.append(clipped(D, d, tex))
    for _ in range(14):
        i = rnd.randint(1, 13)
        x, y = rot([bot[i] if rnd.random() < 0.6 else top[i]], cx, cy, ang)[0]
        a = rnd.uniform(0, 6.28)
        out.append(pline([(x, y), (x + math.cos(a) * 8, y + math.sin(a) * 8 + 3), (x + math.cos(a) * 14, y + math.sin(a) * 14 + 6)], "#6A4A3A", 1, rnd.randint(0, 99), 0.7, 1))
    if cut:
        ex, ey = rot([(cx + L / 2, cy)], cx, cy, ang)[0]
        face = rot(blob_pts(ex, ey, W * 0.36, W * 0.52, seed + 3, 0.04, 16), ex, ey, ang)
        fd = smooth_closed(face)
        out.append(f'<path d="{fd}" fill="#6E2EA8"/>')
        rings = [f'<path d="{fd}" fill="{D.rad([(0, "#B880F0", 0.9), (0.55, "#8A48C8", 0.4), (1, "#4A1478", 0.6)])}"/>']
        for k in (0.75, 0.5):
            rings.append(f'<path d="{smooth_closed(rot(blob_pts(ex, ey, W * 0.36 * k, W * 0.52 * k, seed + 4, 0.05, 14), ex, ey, ang))}" fill="none" stroke="#C8A0F0" stroke-width="1.2" opacity="0.7"/>')
        for _ in range(30):
            rings.append(f'<circle cx="{ex + rnd.uniform(-W * 0.3, W * 0.3):.1f}" cy="{ey + rnd.uniform(-W * 0.45, W * 0.45):.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#F4E8FF" opacity="0.8"/>')
        out.append(clipped(D, fd, rings))
        out.append(f'<path d="{fd}" fill="none" stroke="#E8D8F0" stroke-width="2.4"/>')
        out.append(ink(fd, "#2A0A40", 1.2, seed + 5, 1, 0.7))
    return "".join(out)


def ube_leaf(D, x, y, s, ang, seed):
    """Heart-shaped leaf of the ube vine, with its purple-tinged stem."""
    pts = rot([(x + px * s / 16, y + py * s / 16) for px, py in heart_d(0, 0, 16)], x, y, ang + 180)
    out = [painted(D, pts, ("#9ACB7A", "#4E8A3E", "#244E1E"), seed, sdir=(0.5, 0.8), sk=0.15, angle=ang, n=6, inkw=1.2, inkc="#1E3A16", hi=0.35)]
    out.append(pline([(x, y), (x + math.cos(math.radians(ang)) * s * 0.9, y + math.sin(math.radians(ang)) * s * 0.9)], "#8A5A9A", 1.4, seed, 0.8, 1))
    return "".join(out)


def crinkle(D, cx, cy, r, seed):
    """Ube crinkle cookie: domed purple cookie with cracks full of powdered sugar."""
    out = [cast(D, cx + 4, cy + r * 0.5, r, r * 0.3, strength=0.35, seed=seed)]
    pts = blob_pts(cx, cy, r, r * 0.8, seed, 0.06, 14)
    out.append(painted(D, pts, ("#B890E0", "#7A48B0", "#3E1A66"), seed, sk=0.25, n=6, inkw=1.2, hi=0.4))
    rnd = random.Random(seed)
    cr = []
    for _ in range(9):
        x, y = cx + rnd.uniform(-r, r) * 0.7, cy + rnd.uniform(-r, r) * 0.55
        cr.append(f'<path d="{blob(x, y, rnd.uniform(3, 7), rnd.uniform(2, 4), rnd.randint(0, 999), 0.35, 8, rnd.uniform(0, 180))}" fill="#FFFFFF" opacity="0.92"/>')
    out.append(clipped(D, smooth_closed(pts), cr))
    return "".join(out)


@design("ube")
def ube():
    D = Doc2("ph-ub")
    out = [paper(D.nid(), "#EEE2F4", "#6A4A7A", 901)]
    out.append(blooms(902, ["#C8A8E8", "#9A72C8", "#E8D0F8"], 9, (0, 0, 600, 600), (90, 200), (0.1, 0.18)))
    out.append(soft_glow(D, 300, 360, 280, "#FFFFFF", 0.6))
    # chopping board
    board = poly_pts([(70, 420), (540, 420), (560, 560), (50, 560)], 18, 903, 0.8)
    out.append(cast(D, 312, 566, 270, 16, strength=0.4, seed=904))
    out.append(painted(D, board, ("#F2D4A8", "#D4A870", "#8A6236"), 905, sdir=(0.3, 1), sk=0.12, angle=0, n=60, slen=(40, 120), sw=(1, 2.4), inkw=2, hi=0.4))
    out.append(f'<path d="{pd([(50, 560), (560, 560), (556, 574), (54, 574)])}" fill="#8A6236"/>')
    # whole tuber and the cut half
    out.append(ube_tuber(D, 176, 456, 210, 70, -8, 906))
    out.append(ube_tuber(D, 366, 502, 150, 76, 6, 907, cut=True))
    # a slice
    sx, sy = 496, 470
    sl = blob_pts(sx, sy, 34, 22, 908, 0.05, 16)
    out.append(cast(D, sx + 4, sy + 10, 36, 10, strength=0.35, seed=908))
    out.append(f'<path d="{smooth_closed(shift(sl, 0, 7))}" fill="#4A1478"/>')
    out.append(f'<path d="{smooth_closed(sl)}" fill="#7A3AB8" stroke="#5A3448" stroke-width="3"/>')
    out.append(f'<path d="{blob(sx, sy, 22, 13, 909, 0.05, 14)}" fill="none" stroke="#C8A0F0" stroke-width="1.2"/>')
    out.append(f'<path d="{blob(sx - 10, sy - 6, 12, 5, 910, 0.1, 10)}" fill="#E8D0FF" opacity="0.5"/>')
    # oval llanera of ube halaya with a swirl pattern, a spoon taken out
    hx, hy = 330, 340
    out.append(cast(D, hx + 10, hy + 40, 150, 24, strength=0.4, seed=911))
    tin = ell_pts(hx, hy + 14, 148, 46, 0, 360, 36)[:-1]
    out.append(painted(D, tin, STEEL, 912, sdir=(0.5, 0.9), sk=0.2, angle=0, n=14, inkw=1.8, inkc="#2A2E38", hi=0.5))
    out.append(f'<path d="{ellipse_d(hx, hy, 146, 44)}" fill="#E8ECF0" stroke="#5A6270" stroke-width="1.6"/>')
    hd = ellipse_d(hx, hy + 2, 134, 38)
    rnd = random.Random(913)
    sw = [f'<path d="{hd}" fill="#7A3AB0"/>',
          f'<path d="{hd}" fill="{D.rad([(0, "#B880E8", 0.8), (0.6, "#8A48C0", 0.3), (1, "#3A0A60", 0.6)], 0.4, 0.4, 0.7)}"/>']
    for k in range(9):
        r = 12 + k * 15
        sw.append(f'<path d="{smooth_open(ell_pts(hx + 4, hy + 2, r, r * 0.29, 200 + k * 10, 520 + k * 10, 26))}" fill="none" stroke="#5A2088" stroke-width="3" opacity="0.6"/>')
        sw.append(f'<path d="{smooth_open(ell_pts(hx + 4, hy, r, r * 0.29, 200 + k * 10, 330 + k * 10, 16))}" fill="none" stroke="#D0A8F8" stroke-width="1.6" opacity="0.6"/>')
    sw.append(f'<path d="{blob(hx + 58, hy + 4, 30, 12, 914, 0.15, 12)}" fill="#4A1478" opacity="0.7"/>')
    for _ in range(18):
        x, y = hx + rnd.uniform(-110, 110), hy + rnd.uniform(-30, 30)
        sw.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(4, 9):.1f} {rnd.uniform(-2, 2):.1f}" stroke="#FFF6E0" stroke-width="2.4" stroke-linecap="round" opacity="0.6"/>')
    out.append(clipped(D, hd, sw))
    out.append(taper([(hx - 96, hy - 22), (hx - 30, hy - 32), (hx + 30, hy - 30)], 3, 1, "#FFFFFF", 0.7))
    # spoon resting with a scoop on it
    out.append(taper([(hx + 120, hy - 8), (hx + 210, hy - 60)], 7, 6, "#C8CED6"))
    out.append(taper([(hx + 122, hy - 12), (hx + 208, hy - 62)], 2, 2, "#FFFFFF", 0.9))
    sp = blob_pts(hx + 100, hy + 2, 26, 15, 915, 0.05, 14)
    out.append(painted(D, rot(sp, hx + 100, hy + 2, -28), STEEL, 915, sk=0.25, n=4, inkw=1.4, inkc="#2A2E38", hi=0.6))
    out.append(painted(D, rot(blob_pts(hx + 100, hy - 2, 18, 11, 916, 0.15, 12), hx + 100, hy - 2, -28), UBE, 916, sk=0.25, n=4, inkw=1.2, hi=0.45))
    for sg, x0 in ((-1, -10), (1, 610)):
        vine = [(x0, 40), (x0 - sg * 60, 70), (x0 - sg * 90, 130), (x0 - sg * 70, 200), (x0 - sg * 96, 260)]
        cp = catmull(vine, 5)
        out.append(pline(cp, "#5A3A6A", 2.4, 930 + sg, 0.9, 1))
        for i, (x, y) in enumerate(cp[2::3]):
            out.append(ube_leaf(D, x, y, 18 + (i % 2) * 5, (40 if sg < 0 else 140) + (i % 3) * 30 * sg, 932 + i * 3 + sg))
    for k, (x, y) in enumerate(((112, 368), (150, 390), (90, 400))):
        out.append(crinkle(D, x, y, 22, 940 + k))
    for x, y, s in ((520, 300, 10), (480, 250, 7), (540, 380, 8)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 174, "ube", SERIF_IT, 152, "#5A2186", ["#7A3AB0", "#3A0E5E", "#9A5AD0"], 920, max_w=300,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#E0C0FF"))
    out.append(ruled(300, 218, "OO, PURPLE TALAGA", "#B8306A", font=JOS, size=21, ls=6, line_w=30, gap=14))
    return finish_b(D, out, 921, "#3A1A4A")


# ================================================================ 12. tahooo! — the vendor's buckets at the gate, early morning
def bougainvillea(D, cx, cy, rx, ry, seed, n=90, pal=(("#FF8AC8", "#E0308A", "#8A0E4A"), ("#FFA8D8", "#EE5AA8", "#A01E62"))):
    rnd = random.Random(seed)
    out = [dab_crown(D, cx, cy, rx, ry, [("#8AC86A", "#3E8A3A", "#1A4A1E")], seed, n=int(n * 0.5), size=(5, 10), inkw=0, base=False)]
    for _ in range(n):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        p = rnd.choice(pal)
        for j in range(3):
            aa = rnd.uniform(0, 6.28) + j * 2.1
            out.append(f'<path d="{blob(x + math.cos(aa) * 4, y + math.sin(aa) * 4, 5.5, 4.2, rnd.randint(0, 9999), 0.18, 8, math.degrees(aa))}" fill="{p[rnd.randint(0, 1)]}" opacity="0.95"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.2" fill="#FFF6D8"/>')
    return "".join(out)


def iron_gate(D, x0, y0, x1, y1, seed, col="#2E3A4A"):
    out = []
    for k in range(int((x1 - x0) / 22) + 1):
        x = x0 + k * 22
        out.append(taper([(x, y0), (x, y1)], 4, 4, col))
        out.append(f'<path d="M {x - 4:.1f} {y0 - 2} L {x:.1f} {y0 - 14} L {x + 4:.1f} {y0 - 2} Z" fill="{col}"/>')
    for y in (y0 + 14, (y0 + y1) / 2, y1 - 14):
        out.append(taper([(x0 - 4, y), (x1 + 4, y)], 5, 5, col))
    for k in range(int((x1 - x0) / 44)):
        x = x0 + 11 + k * 44
        ym = y0 + 40
        out.append(f'<path d="M {x:.1f} {ym:.1f} q 11 -18 22 0 q -11 18 -22 0 Z" fill="none" stroke="{col}" stroke-width="3"/>')
    return "".join(out)


def taho_bucket(D, cx, base, w, h, seed, lid=True):
    """Aluminium taho bucket (balde): ribbed body, a domed lid with a knob, and a wire bail handle."""
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    body = [(l + w * 0.05, top), (l, base - 6), (l + 6, base), (r - 6, base), (r, base - 6), (r - w * 0.05, top)]
    out = [cast(D, cx + 10, base, w * 0.65, 9, strength=0.45, seed=seed)]
    out.append(painted(D, densify(body, 10), STEEL, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=30, cols=["#FFFFFF", "#8A94A4", "#E8ECF0"], inkw=1.8, inkc="#2A2E38", hi=0.5, hik=0.06))
    d = smooth_closed(densify(body, 10))
    out.append(clipped(D, d, [f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.0), (0.18, "#FFFFFF", 0.6), (0.3, "#FFFFFF", 0), (0.85, "#14141A", 0.25), (1, "#14141A", 0.4)], 0, 0, 1, 0)}"/>']
                                 + [pline([(l, top + h * t), (r, top + h * t)], "#6A7484", 2, seed + int(t * 10), 0.6, 1) for t in (0.18, 0.8)]))
    out.append(f'<path d="{ellipse_d(cx, top, w / 2 - w * 0.04, w * 0.1)}" fill="#E8ECF0" stroke="#2A2E38" stroke-width="1.4"/>')
    if lid:
        dome = ell_pts(cx, top, w / 2 - w * 0.04, w * 0.24, 180, 360, 18)
        out.append(painted(D, dome, STEEL, seed + 1, sdir=(0.7, 0.7), sk=0.2, angle=-20, n=10, inkw=1.6, inkc="#2A2E38", hi=0.6))
        out.append(f'<path d="{ellipse_d(cx, top - w * 0.24, 8, 4)}" fill="#C8CED6" stroke="#2A2E38" stroke-width="1.2"/>')
        out.append(taper([(cx - w * 0.3, top - 4), (cx - w * 0.15, top - w * 0.18)], 3, 1, "#FFFFFF", 0.8))
    # bail handle to the pole
    out.append(pline([(l + 4, top + 10), (l - 6, top - h * 0.4), (cx, top - h * 0.62)], "#4A505A", 2.2, seed, 0.9, 1))
    out.append(pline([(r - 4, top + 10), (r + 6, top - h * 0.4), (cx, top - h * 0.62)], "#4A505A", 2.2, seed + 1, 0.9, 1))
    return "".join(out)


def taho_cup(D, cx, base, h, seed):
    """Clear plastic cup of taho: silken tofu, amber arnibal syrup swirling down, chewy sago pearls; a little spoon."""
    w_top, w_bot = h * 0.62, h * 0.46
    top = base - h
    cup = [(cx - w_top / 2, top), (cx - w_bot / 2, base), (cx + w_bot / 2, base), (cx + w_top / 2, top)]
    d = smooth_closed(densify(cup, 8))
    out = [cast(D, cx + 10, base + 2, w_bot * 0.8, 8, strength=0.45, seed=seed)]
    rnd = random.Random(seed)
    lay = [f'<rect x="{cx - w_top:.1f}" y="{top:.1f}" width="{2 * w_top:.1f}" height="{h + 4:.1f}" fill="#FBF4E4"/>']
    for k in range(5):
        y = top + h * (0.15 + 0.17 * k)
        lay.append(taper([(cx - w_top / 2, y), (cx - w_top * 0.1, y + 8), (cx + w_top * 0.2, y - 4), (cx + w_top / 2, y + 6)], 10 - k, 5, "#C8862A", 0.55))
    lay.append(f'<rect x="{cx - w_top:.1f}" y="{base - h * 0.16:.1f}" width="{2 * w_top:.1f}" height="{h * 0.2:.1f}" fill="#B8702A" opacity="0.8"/>')
    for _ in range(26):
        x, y = cx + rnd.uniform(-w_top, w_top) * 0.45, top + h * rnd.uniform(0.05, 0.95)
        r = rnd.uniform(4, 6.5)
        lay.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#9A5A2A" opacity="0.85"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.3:.1f}" fill="#FFE8C8" opacity="0.8"/>')
    lay.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.45), (0.2, "#FFFFFF", 0), (0.85, "#7A6A5A", 0), (1, "#5A4A3A", 0.25)], 0, 0, 1, 0)}"/>')
    out.append(clipped(D, d, lay))
    out.append(ink(d, "#8A8070", 1.8, seed, 2, 0.7))
    out.append(f'<path d="{ellipse_d(cx, top, w_top / 2, w_top * 0.12)}" fill="#F4E6CC" stroke="#8A8070" stroke-width="1.6"/>')
    out.append(f'<path d="{ellipse_d(cx, top + 1, w_top / 2 - 6, w_top * 0.09)}" fill="#E0B070"/>')
    for _ in range(5):
        out.append(f'<circle cx="{cx + rnd.uniform(-w_top, w_top) * 0.3:.1f}" cy="{top + rnd.uniform(-4, 4):.1f}" r="4" fill="#9A5A2A"/>')
    out.append(taper([(cx - w_top * 0.36, top + 12), (cx - w_bot * 0.38, base - 10)], 5, 2, "#FFFFFF", 0.75))
    # little plastic spoon
    out.append(taper([(cx + 10, top - 2), (cx + 44, top - 62)], 6, 5, "#F6F0E8"))
    out.append(pline([(cx + 8, top), (cx + 42, top - 64)], "#B8B0A0", 1, seed, 0.6, 1))
    return "".join(out)


@design("taho")
def taho():
    D = Doc2("ph-th")
    out = [sky(D, [(0, "#F6C8A0"), (0.55, "#FFE4C0"), (1, "#FFF2DC")], 1001, 600, ["#FFD8B0", "#F2B890", "#FFF0D8"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 150, 250, 260, "#FFF6D0", 0.7))
    # concrete wall with a gate, bougainvillea spilling over
    wallp = "M -10 272 L 610 272 L 610 470 L -10 470 Z"
    out.append(f'<path d="{wallp}" fill="#E8D8C0"/>')
    out.append(strokes(D.nid(), wallp, (-40, 272, 600, 470), ["#F6EAD8", "#C8B498", "#D8C4A8"], 1002, n=60, angle=-80, length=(20, 60), width=(3, 8), opacity=(0.12, 0.3)))
    out.append(f'<path d="M -10 272 L 610 272 L 610 284 L -10 284 Z" fill="#C8B498"/>')
    out.append(f'<path d="{pd([(300, 284), (560, 284), (560, 470), (300, 470)])}" fill="#3A3A48" opacity="0.25"/>')
    out.append(iron_gate(D, 312, 300, 548, 470, 1003))
    out.append(bougainvillea(D, 150, 276, 190, 40, 1004, n=110))
    out.append(bougainvillea(D, 470, 282, 130, 30, 1005, n=70))
    for _ in range(6):
        rnd = random.Random(1006 + _)
        out.append(f'<path d="{blob(rnd.uniform(60, 560), rnd.uniform(470, 560), 5, 3.6, rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="#EE5AA8" opacity="0.85"/>')
    # sidewalk
    gp = "M -10 470 L 610 470 L 610 610 L -10 610 Z"
    out.append(f'<path d="{gp}" fill="{D.lin([(0, "#C8BCA8"), (1, "#A89A84")])}"/>')
    out.append(strokes(D.nid(), gp, (-40, 470, 600, 600), ["#DCD0BC", "#8A7E6A"], 1007, n=40, angle=-2, length=(40, 120), width=(2, 5), opacity=(0.12, 0.3)))
    for k in range(5):
        out.append(pline([(k * 150 - 20, 470), (k * 150 - 70, 600)], "#8A7E6A", 1.4, k, 0.4, 1))
    # the vendor's pole resting on two buckets
    out.append(taho_bucket(D, 128, 516, 112, 104, 1010))
    out.append(taho_bucket(D, 300, 508, 86, 76, 1011, lid=True))
    out.append(taper([(36, 350), (214, 368), (380, 386)], 12, 12, "#D8C07A"))
    out.append(taper([(36, 346), (214, 364), (380, 382)], 3, 3, "#F6E8B0", 0.9))
    # the cup, front and centre
    out.append(taho_cup(D, 448, 540, 176, 1012))
    out.append(steam(448, 356, 40, 1013, "#FFFFFF", 2, 18, 5, 0.6))
    # lettering
    out.append(letters(D, 300, 160, "TAHOOO!", BEBAS, 140, "#8A4A12", ["#A8601E", "#5A2A06", "#C87A2A"], 1020, max_w=420, ls=6, wob=0.6,
                       shadow="#FFF6E8", soff=(0.018, 0.03), angle=-40, hi="#F8C080"))
    out.append(ruled(300, 198, "ANG TAWAG TUWING UMAGA", "#C8306A", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 1021)


# ================================================================ 13. magandang umaga — pandesal and coffee at the window, a rooster outside
def pandesal(D, cx, cy, r, seed, ang=0, split=False):
    """Pandesal roll: oval dome, golden-brown top dusted with breadcrumbs."""
    pts = rot(blob_pts(cx, cy, r * 1.15, r * 0.82, seed, 0.05, 16), cx, cy, ang)
    out = [cast(D, cx + 4, cy + r * 0.6, r * 1.05, r * 0.25, strength=0.35, seed=seed)]
    out.append(painted(D, pts, ("#F8D898", "#D8A050", "#8A5A1E"), seed, sdir=(0.5, 0.85), sk=0.22, angle=ang - 20, n=10, inkw=1.4, inkc="#5A3410", hi=0.45))
    rnd = random.Random(seed)
    crumbs = []
    for _ in range(int(r * 2.2)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.95
        crumbs.append(f'<circle cx="{cx + math.cos(a) * rr * 1.1:.1f}" cy="{cy + math.sin(a) * rr * 0.75:.1f}" r="{rnd.uniform(0.7, 1.6):.1f}" fill="{rnd.choice(["#FFF0C8", "#B87A2E", "#F2D090"])}" opacity="0.85"/>')
    out.append(clipped(D, smooth_closed(pts), crumbs))
    if split:
        out.append(taper(rot([(cx - r * 0.7, cy - 2), (cx, cy + 2), (cx + r * 0.7, cy - 1)], cx, cy, ang), 5, 3, "#FFF6E0", 0.95))
    return "".join(out)


def rooster(D, x, base, s, seed, col="#3A2A3A", rim="#FFD890"):
    """Rooster silhouette crowing on a fence post (backlit by sunrise)."""
    P = lambda a, b: (x + a * s, base + b * s)
    body = [P(-30, -10), P(-20, -36), P(4, -44), P(18, -62), P(26, -80), P(36, -84), P(44, -78), P(40, -66), P(30, -52), P(32, -30), P(20, -8), P(0, 0), P(-20, -2)]
    out = [f'<path d="{smooth_closed(body)}" fill="{col}"/>']
    tail = [P(-26, -20), P(-50, -60), P(-64, -70), P(-56, -46), P(-70, -50), P(-58, -24), P(-40, -6)]
    out.append(f'<path d="{smooth_closed(tail)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed([P(28, -84), P(30, -94), P(36, -90), P(40, -96), P(42, -86)])}" fill="#C8241E"/>')
    out.append(f'<path d="M {P(44, -78)[0]:.1f} {P(44, -78)[1]:.1f} L {P(54, -78)[0]:.1f} {P(54, -78)[1]:.1f} L {P(44, -74)[0]:.1f} {P(44, -74)[1]:.1f} Z" fill="#E8A030"/>')
    out.append(f'<path d="{blob(*P(40, -68), 3 * s, 5 * s, seed, 0.1, 8)}" fill="#C8241E"/>')
    out.append(pline([P(-6, 0), P(-8, 14)], col, 2.4 * s, seed, 1, 1) + pline([P(8, -2), P(10, 14)], col, 2.4 * s, seed + 1, 1, 1))
    out.append(taper([P(-18, -34), P(4, -42), P(18, -58)], 2 * s, 1, rim, 0.8))
    return "".join(out)


@design("magandang-umaga")
def magandang_umaga():
    D = Doc2("ph-mu")
    out = [wall(D, "#FBE6C8", "#F2CFA2", 1101, ["#FFF0D8", "#E8B888", "#FFE4C0"])]
    # the window: sunrise over paddies and coconut palms
    wx0, wy0, wx1, wy1 = 120, 196, 480, 400
    view = smooth_closed(rect_pts(wx0, wy0, wx1, wy1, 20, 1102, 0.3))
    v = [sky(D, [(0, "#8AC0E8"), (0.45, "#FFD8A8"), (0.75, "#FFB878")], 1103, wy1 + 10, ["#FFE8C8", "#F8B888"], 30, angle=-3, sop=(0.06, 0.16), y0=wy0 - 10)]
    v.append(soft_glow(D, 300, 344, 120, "#FFF6C0", 0.9))
    v.append(f'<circle cx="300" cy="352" r="30" fill="#FFF2B8"/>')
    v.append(hill(D, ridge([(100, 336), (200, 318), (300, 332), (420, 312), (500, 330)], 1104, 5, 3), 420, ("#B8B8D8", "#9090B8", "#6A6A98"), 1105, inkw=0))
    v.append(f'<path d="M 100 352 L 500 352 L 500 420 L 100 420 Z" fill="#8AB04A"/>')
    for k in range(6):
        v.append(pline([(100, 356 + k * 9), (500, 354 + k * 9.5)], "#C8E080" if k % 2 else "#5A8A2A", 1.6, k, 0.6, 1))
    for k in range(5):
        v.append(f'<path d="M {100 + k * 90:.0f} 352 L {60 + k * 110:.0f} 420" stroke="#6A9A3A" stroke-width="1.4" opacity="0.6"/>')
    for k, (bx, ty, lean) in enumerate(((160, 280, -10), (196, 296, 8), (430, 286, 10))):
        v.append(palm(D, (bx, 362), (bx + lean, ty), 1106 + k, sil="#4A3A4A", L=44, width=7, nuts=False, leaf_cols=["#4A3A4A"]))
    # bamboo fence and the rooster
    v.append(f'<path d="M 100 380 L 500 380" stroke="#8A6A3A" stroke-width="4"/>')
    for k in range(10):
        x = 112 + k * 42
        v.append(taper([(x, 404), (x, 366)], 6, 6, "#A8844A"))
    v.append(rooster(D, 380, 366, 0.62, 1109))
    v.append(seagull(270, 250, 8, "#6A5A6A") if False else bird_v(258, 250, 7, "#6A5A6A") + bird_v(280, 262, 5, "#6A5A6A"))
    out.append(clipped(D, view, v))
    # window frame with open capiz shutters folded aside
    out.append(ink(view, INK, 2, 1110, 1, 0.8))
    for sg, x0 in ((-1, wx0 - 70), (1, wx1 + 4)):
        out.append(capiz_window(D, x0 + 6, wy0 + 2, x0 + 60, wy1 - 2, 1111 + sg, cols=2, rows=6))
    out.append(painted(D, rect_pts(wx0 - 14, wy0 - 18, wx1 + 14, wy0, 16, 1113, 0.4), NARRA, 1113, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    # sill / table with the paper bag of pandesal and a mug of coffee
    out.append(painted(D, rect_pts(-10, 400, 610, 430, 20, 1114, 0.5), NARRA, 1114, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.45))
    out.append(wood_planks(D, 430, 600, 1115, ("#E8B88A", "#C08A58", "#7A4E2A"), 3))
    out.append(soft_glow(D, 300, 470, 260, "#FFE8B8", 0.4))
    bx, bb = 196, 548
    bag = [(bx - 72, bb), (bx - 66, bb - 108), (bx - 70, bb - 140), (bx + 60, bb - 150), (bx + 62, bb - 110), (bx + 70, bb)]
    out.append(cast(D, bx + 14, bb + 2, 90, 10, strength=0.4, seed=1116))
    for k, (x, y, a) in enumerate(((bx - 34, bb - 148, -10), (bx + 10, bb - 158, 8), (bx + 40, bb - 142, 18))):
        out.append(pandesal(D, x, y, 26, 1117 + k, a))
    out.append(painted(D, densify(bag, 12), ("#E8C898", "#C89A60", "#7A5A2E"), 1120, sdir=(0.8, 0.4), sk=0.18, angle=-88, n=40, inkw=1.8, hi=0.35))
    out.append(clipped(D, smooth_closed(densify(bag, 12)), [pline([(bx - 70, bb - 132 + k * 8), (bx + 60, bb - 140 + k * 8)], "#8A6A3A", 1, 1121 + k, 0.4, 1) for k in range(2)]
                       + [taper([(bx - 20, bb - 120), (bx - 26, bb - 60), (bx - 14, bb - 8)], 3, 2, "#8A6A3A", 0.4), taper([(bx + 30, bb - 120), (bx + 36, bb - 40)], 3, 2, "#8A6A3A", 0.35)]))
    out.append(pandesal(D, 304, 524, 26, 1124, -6, split=False))
    out.append(pandesal(D, 92, 524, 22, 1125, 10))
    # enamel mug of coffee
    out.append(enamel_mug(D, 412, 556, 92, 1126))
    out.append(steam(412, 446, 60, 1127, "#FFFFFF", 2, 24, 7, 0.65))
    # lettering
    out.append(letters(D, 300, 116, "Magandang umaga", SERIF_IT, 82, "#A0401E", ["#C0582A", "#6A220A", "#D87A3A"], 1130, max_w=470,
                       shadow="#FFF6E8", soff=(0.018, 0.03), angle=-40, hi="#F8B880"))
    out.append(ruled(300, 160, "PANDESAL AT KAPE", "#2E5AA0", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 1131)


def enamel_mug(D, cx, base, w, seed, body=("#FFFFFF", "#F4F0E8", "#B8B0A6"), rim=BUGHAW):
    h = w * 0.9
    top = base - h
    l, r = cx - w / 2, cx + w / 2
    out = [cast(D, cx + 10, base, w * 0.6, 8, strength=0.45, seed=seed)]
    hp = [(r - 2, top + h * 0.2), (r + w * 0.3, top + h * 0.22), (r + w * 0.32, top + h * 0.6), (r - 2, top + h * 0.72)]
    out.append(ink(smooth_open(hp), rim[2], 11, seed, 1, 1))
    out.append(ink(smooth_open(hp), body[1], 6, seed + 1, 1, 1))
    pts = densify([(l, top), (l + 2, base - 8), (l + 10, base), (r - 10, base), (r - 2, base - 8), (r, top)], 10)
    out.append(painted(D, pts, body, seed + 2, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=16, inkw=1.8, hi=0.5))
    out.append(f'<path d="{ellipse_d(cx, top, w / 2, w * 0.1)}" fill="{rim[1]}" stroke="{INK}" stroke-width="1.4"/>')
    out.append(f'<path d="{ellipse_d(cx, top + 2, w / 2 - 5, w * 0.075)}" fill="#3A1A0A"/>')
    out.append(f'<path d="{blob(cx - 8, top + 1, w * 0.15, w * 0.025, seed, 0.1, 8)}" fill="#C8905A" opacity="0.7"/>')
    out.append(pline([(l + 2, base - 6), (cx, base - 2), (r - 2, base - 6)], rim[1], 3.5, seed + 3, 0.9, 1))
    # a painted rooster-red flower on the enamel, and one chip
    for j in range(5):
        a = math.radians(j * 72)
        out.append(f'<path d="{blob(cx + math.cos(a) * 7, top + h * 0.5 + math.sin(a) * 7, 6, 4, seed + j, 0.1, 8, math.degrees(a))}" fill="{PULA[1]}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{top + h * 0.5:.1f}" r="3.4" fill="{ARAW[1]}"/>')
    out.append(leaf_simple(D, cx + 10, top + h * 0.58, 16, 4, 30, ("#8ACB8A", "#3E8A4E", "#1E5A2E"), seed + 9, vein=False, inkw=0))
    out.append(f'<path d="{blob(l + 10, base - 14, 4, 3, seed + 11, 0.25, 8)}" fill="#1E1E28"/>')
    out.append(taper([(l + 8, top + 12), (l + 9, base - 22)], 4, 1, "#FFFFFF", 0.85))
    return "".join(out)


# ================================================================ 14. salamat po — a bayong full of pasalubong, with a tag
def mango_whole(D, cx, cy, s, ang, seed, ripe=1.0):
    """Philippine (carabao) mango: long, kidney-shaped, golden yellow with a blush of green at the stem."""
    top, bot = [], []
    for i in range(17):
        u = -1 + 2 * i / 16
        k = max(0.0, 1 - u * u)
        top.append((cx + u * s, cy - s * 0.44 * k ** 0.55 * (1 + 0.18 * u) - s * 0.06 * u))
        bot.append((cx + u * s, cy + s * 0.46 * k ** 0.5 * (1 - 0.1 * u) + s * 0.1 * u * u))
    pts = top + bot[::-1][1:-1]
    pts = rot(pts, cx, cy, ang)
    pal = (mix("#C8E080", "#FFE98A", ripe), mix("#8AB040", "#F5B623", ripe), mix("#4A6A1A", "#B0700A", ripe))
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.85), sk=0.22, angle=ang + 10, n=12, inkw=1.5, inkc="#6A4A0A", hi=0.55, hik=0.12)]
    a = math.radians(ang)
    sx, sy = cx - math.cos(a) * s * 0.92, cy - math.sin(a) * s * 0.92
    out.append(clipped(D, smooth_closed(pts), [f'<path d="{blob(sx, sy, s * 0.4, s * 0.3, seed + 1, 0.2, 10)}" fill="#8AB040" opacity="0.45"/>']))
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{max(2, s * 0.05):.1f}" fill="#5A3A1A"/>')
    out.append(taper(rot([(cx - s * 0.5, cy - s * 0.26), (cx, cy - s * 0.36), (cx + s * 0.4, cy - s * 0.3)], cx, cy, ang), 4, 1.5, "#FFFBE0", 0.7))
    return "".join(out)


def suman(D, cx, cy, L, ang, seed):
    """Suman: sticky rice wrapped in banana leaf, tied with strips."""
    a = math.radians(ang)
    pts = rot(rect_pts(cx - L / 2, cy - L * 0.15, cx + L / 2, cy + L * 0.15, 10, seed, 0.5), cx, cy, ang)
    out = [painted(D, pts, ("#B8D890", "#6A9A4A", "#2E5A22"), seed, sk=0.25, angle=ang, n=8, inkw=1.3, hi=0.4)]
    for t in (-0.25, 0.25):
        x, y = cx + math.cos(a) * L * t, cy + math.sin(a) * L * t
        out.append(taper(rot([(x, y - L * 0.17), (x + 2, y + L * 0.17)], x, y, ang), 4, 4, "#D8C890"))
    out.append(pline(rot([(cx - L / 2, cy - L * 0.04), (cx + L / 2, cy - L * 0.06)], cx, cy, ang), "#2E5A22", 1, seed, 0.4, 1))
    return "".join(out)


def saging(D, cx, cy, s, ang, seed, n=4):
    """A small hand of lakatan bananas."""
    out = []
    for k in range(n):
        off = (k - (n - 1) / 2) * s * 0.26
        a = math.radians(ang)
        bx, by = cx - math.sin(a) * off, cy + math.cos(a) * off
        curve = [(bx - math.cos(a) * s * 0.5, by - math.sin(a) * s * 0.5), (bx + math.sin(a) * s * 0.18, by - math.cos(a) * s * 0.18),
                 (bx + math.cos(a) * s * 0.5, by + math.sin(a) * s * 0.5)]
        cp = catmull(curve, 6)
        top = [(x - math.sin(a) * s * 0.11 * math.sin(math.pi * i / (len(cp) - 1)) ** 0.6, y + math.cos(a) * s * 0.11 * math.sin(math.pi * i / (len(cp) - 1)) ** 0.6 - s * 0.11) for i, (x, y) in enumerate(cp)]
        bot = [(x + math.sin(a) * s * 0.02, y + s * 0.02) for x, y in cp]
        pts = top + bot[::-1]
        out.append(painted(D, pts, ("#FFF29A", "#F2CC2A", "#A8820A"), seed + k, sk=0.25, angle=ang, n=6, inkw=1.2, inkc="#6A4A0A", hi=0.5))
        out.append(f'<circle cx="{cp[-1][0]:.1f}" cy="{cp[-1][1] - s * 0.05:.1f}" r="2.4" fill="#3A2A0A"/>')
    a = math.radians(ang)
    x0, y0 = cx - math.cos(a) * s * 0.5, cy - math.sin(a) * s * 0.5
    out.append(taper([(x0, y0 - s * 0.05), (x0 - math.cos(a) * s * 0.16, y0 - math.sin(a) * s * 0.16 - s * 0.04)], 10, 7, "#8A9A3A"))
    return "".join(out)


def bayong(D, cx, base, w_top, w_bot, h, seed):
    """Bayong: woven buri / pandan market bag with coloured bands and twisted rattan handles. Returns (back, front)."""
    top = base - h
    l_t, r_t, l_b, r_b = cx - w_top / 2, cx + w_top / 2, cx - w_bot / 2, cx + w_bot / 2
    body = densify([(l_t, top), (r_t, top), (r_b, base), (l_b, base)], 10)
    d = smooth_closed(body)
    back = [f'<path d="{ellipse_d(cx, top, w_top / 2, 18)}" fill="#7A5A2A"/>']
    c = 10
    t = [f'<rect width="{2 * c}" height="{2 * c}" fill="#D8B878"/>',
         f'<rect x="0.5" y="0.5" width="{c - 1}" height="{c - 1}" rx="2" fill="#ECCE94"/><rect x="{c + 0.5}" y="{c + 0.5}" width="{c - 1}" height="{c - 1}" rx="2" fill="#ECCE94"/>',
         f'<rect x="{c + 0.5}" y="0.5" width="{c - 1}" height="{c - 1}" rx="2" fill="#C8A060"/><rect x="0.5" y="{c + 0.5}" width="{c - 1}" height="{c - 1}" rx="2" fill="#C8A060"/>']
    pat = D.pattern(2 * c, 2 * c, "".join(t), transform="rotate(45)")
    front = [f'<path d="{d}" fill="{pat}"/>']
    bands = []
    for k, (t0, t1, col) in enumerate(((0.22, 0.32, "#C8285A"), (0.36, 0.42, "#2E8A5A"), (0.62, 0.72, "#C8285A"), (0.76, 0.8, "#E8A81E"))):
        y0, y1 = top + h * t0, top + h * t1
        bands.append(f'<rect x="{cx - w_bot:.1f}" y="{y0:.1f}" width="{2 * w_bot:.1f}" height="{y1 - y0:.1f}" fill="{col}" opacity="0.85"/>')
        for x in range(int(cx - w_bot), int(cx + w_bot), 14):
            bands.append(f'<path d="M {x} {y0:.1f} L {x + 7} {y1:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.35"/>')
    bands.append(f'<path d="{d}" fill="{D.lin([(0, "#3A2408", 0.0), (0.6, "#3A2408", 0.05), (1, "#3A2408", 0.45)], 0, 0, 1, 0)}"/>')
    bands.append(f'<path d="{d}" fill="{D.lin([(0, "#3A2408", 0.25), (0.2, "#3A2408", 0.0)], 0, 0, 0, 1)}"/>')
    front.append(clipped(D, d, bands))
    front.append(ink(d, INK, 2, seed, 2, 0.75))
    front.append(taper([(l_t - 2, top + 2), (r_t + 2, top + 2)], 9, 9, "#B8884A"))
    for x in range(int(l_t), int(r_t), 9):
        front.append(f'<path d="{blob(x + 4, top + 2, 5, 3, seed + x, 0.1, 8, 40)}" fill="#E8C080"/>')
    # handles
    for sg in (-1, 1):
        hx0, hx1 = cx + sg * w_top * 0.12, cx + sg * w_top * 0.36
        hp = [(hx0, top + 4), (hx0 + sg * 6, top - h * 0.36), ((hx0 + hx1) / 2, top - h * 0.48), (hx1 - sg * 4, top - h * 0.36), (hx1, top + 4)]
        back.append(ink(smooth_open(hp), "#6A4A1A", 8, seed + sg, 1, 1))
        back.append(ink(smooth_open(hp), "#C8985A", 4, seed + sg + 3, 1, 1))
        for i in range(0, 13, 2):
            x, y = catmull(hp, 3)[i]
            back.append(pline([(x - 3, y - 3), (x + 3, y + 3)], "#6A4A1A", 1.2, seed + i, 0.6, 1))
    return "".join(back), "".join(front)


def lanzones(D, cx, cy, seed, n=14):
    """A bunch of lanzones: small round straw-yellow fruits with tiny brown freckles on a woody stalk."""
    rnd = random.Random(seed)
    out = [taper([(cx - 10, cy - 40), (cx, cy - 10), (cx + 6, cy + 24)], 5, 3, "#7A5A3A")]
    pos = []
    for k in range(n):
        t = k / (n - 1)
        pos.append((cx + rnd.uniform(-20, 20) * (0.6 + t), cy - 30 + t * 64 + rnd.uniform(-6, 6), rnd.uniform(11, 14)))
    for x, y, r in sorted(pos, key=lambda p: p[1]):
        out.append(painted(D, blob_pts(x, y, r, r * 0.95, rnd.randint(0, 999), 0.05, 12), ("#FFF2B8", "#E8C870", "#9A7A2A"), rnd.randint(0, 999), sdir=(0.5, 0.8), sk=0.25, n=3, inkw=1.0, inkc="#6A4A1A", hi=0.5))
        for _ in range(4):
            out.append(f'<circle cx="{x + rnd.uniform(-r, r) * 0.6:.1f}" cy="{y + rnd.uniform(-r, r) * 0.6:.1f}" r="0.9" fill="#8A5A2A" opacity="0.7"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y - r + 2:.1f}" r="1.6" fill="#6A4A2A"/>')
    return "".join(out)


@design("salamat-po")
def salamat_po():
    D = Doc2("ph-sp")
    out = [wall(D, "#F6E2BE", "#EBC896", 1201, ["#FFF0D4", "#D8A868", "#F8DCAA"])]
    out.append(soft_glow(D, 300, 360, 300, "#FFFFFF", 0.5))
    out.append(blooms(1202, ["#F2C88A", "#C8E0A8"], 6, (0, 0, 600, 600), (90, 170), (0.06, 0.12)))
    # a narra bench top
    out.append(wood_planks(D, 456, 600, 1203, NARRA, 2))
    out.append(table_edge(456, "#2A1006"))
    cx, base = 300, 540
    back, front = bayong(D, cx, base, 280, 236, 200, 1204)
    out.append(cast(D, cx + 16, base + 2, 140, 14, strength=0.5, seed=1205))
    out.append(back)
    # the pasalubong inside, peeking over the rim
    top = base - 196
    out.append(banana_leaf(D, cx - 30, top + 10, -118, 120, 30, 1206, pal=SAGING))
    out.append(banana_leaf(D, cx + 50, top + 10, -64, 110, 28, 1207, pal=SAGING))
    out.append(lanzones(D, cx - 96, top - 30, 1208))
    out.append(suman(D, cx + 92, top - 50, 84, -58, 1212))
    out.append(suman(D, cx + 70, top - 44, 80, -72, 1213))
    out.append(mango_whole(D, cx - 50, top - 30, 56, -24, 1209))
    out.append(mango_whole(D, cx + 14, top - 40, 60, 14, 1210))
    out.append(mango_whole(D, cx + 70, top - 14, 50, -8, 1211, ripe=0.8))
    out.append(front)
    # mangoes beside the bag
    out.append(mango_whole(D, 106, 524, 46, 6, 1214))
    out.append(mango_whole(D, 498, 528, 42, 172, 1215, ripe=0.9))
    # kraft tag tied to the handle
    tx, ty = 472, 330
    out.append(pline([(cx + 84, top - 70), (tx - 40, ty - 34), (tx - 30, ty - 20)], "#8A6A3A", 1.6, 1216, 0.9, 1))
    tag = rot([(tx - 40, ty - 26), (tx + 46, ty - 26), (tx + 46, ty + 26), (tx - 40, ty + 26), (tx - 58, ty)], tx, ty, 12)
    out.append(painted(D, densify(tag, 10), ("#F2D8A8", "#D8B07A", "#8A6A3A"), 1216, sk=0.15, angle=12, n=10, inkw=1.4, hi=0.35))
    hx, hy = rot([(tx - 44, ty)], tx, ty, 12)[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="4" fill="#F6EAD8" stroke="#8A6A3A" stroke-width="1.2"/>')
    out.append(f'<text x="{tx + 4}" y="{ty + 7}" text-anchor="middle" {SERIF_IT} font-size="{fit_size("Para sa inyo", SERIF_IT, 21, 82)}" fill="#7A2E1E" transform="rotate(12 {tx} {ty})">Para sa inyo</text>')
    out.append(p_heart(D, tx + 30, ty + 18, 7, PULA, 1217, rot_=12, inkw=0.8) if False else "")
    # lettering
    out.append(letters(D, 300, 132, "Salamat po", SERIF_IT, 116, "#2E6A3A", ["#3E8A4A", "#1A4A22", "#5AA866"], 1220, max_w=460,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#B8E0B0"))
    out.append(ruled(300, 176, "THANK YOU, WITH RESPECT", "#B8462A", font=JOS, size=19, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 1221)


# ================================================================ 15. mahal kita — harana: a guitar under the lit capiz window
def guitar(D, cx, cy, s, ang, seed, body=("#F2C278", "#D08A3A", "#7A4410")):
    """Acoustic guitar (local, center = sound hole): figure-eight body, rosette, bridge, neck with frets and headstock."""
    def T(pts):
        return rot([(cx + x * s, cy + y * s) for x, y in pts], cx, cy, ang)
    lower = [(math.cos(math.radians(a)) * 64, 40 + math.sin(math.radians(a)) * 58) for a in range(0, 360, 15)]
    upper = [(math.cos(math.radians(a)) * 50, -44 + math.sin(math.radians(a)) * 44) for a in range(0, 360, 15)]
    out = [cast(D, cx + 20 * s, cy + 110 * s, 70 * s, 12 * s, strength=0.4, seed=seed)]
    # neck and headstock (behind body top)
    neck = T([(-9, -80), (9, -80), (8, -250), (-8, -250)])
    out.append(painted(D, densify(neck, 8), ("#8A5A3A", "#5A3418", "#2A1206"), seed, sk=0.2, angle=ang - 90, n=8, inkw=1.4, hi=0.4))
    for k in range(10):
        y = -96 - k * 15
        out.append(pline(T([(-8, y), (8, y)]), "#E8E0D0", 1.4, seed + k, 0.9, 1))
    head = T([(-12, -250), (12, -250), (14, -300), (-14, -300)])
    out.append(painted(D, densify(head, 8), ("#8A5A3A", "#5A3418", "#2A1206"), seed + 1, sk=0.2, n=4, inkw=1.4, hi=0.4))
    for k in range(3):
        for sg in (-1, 1):
            px, py = T([(sg * 18, -262 - k * 13)])[0]
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{3.6 * s:.1f}" fill="#E8E0D0" stroke="#5A4A3A" stroke-width="1"/>')
    # body
    bodyp = T(upper[:13] + lower[12:] + lower[:1]) if False else None
    for part in (upper, lower):
        out.append(painted(D, T(part), body, seed + 2, sdir=(0.6, 0.8), sk=0.15, angle=ang - 90, n=20, inkw=0, hi=0.4))
    waist = T([(-44, -14), (44, -14), (50, 10), (-50, 10)])
    out.append(f'<path d="{smooth_closed(waist)}" fill="{body[1]}"/>')
    out.append(ink(smooth_closed(T(upper)), "#3A1A06", 2, seed + 3, 1, 0.7) + ink(smooth_closed(T(lower)), "#3A1A06", 2, seed + 4, 1, 0.7))
    out.append(f'<path d="{smooth_closed(T(upper))}" fill="none" stroke="#2A1206" stroke-width="{3 * s:.1f}" opacity="0.3"/>')
    hx, hy = cx, cy
    for r, col in ((22, "#2A1206"), (20, "#E8C890"), (17, "#7A4410"), (15, "#1A0A04")):
        out.append(f'<path d="{ellipse_d(*T([(0, 0)])[0], r * s, r * s, 24)}" fill="{col}"/>')
    for k in range(6):
        out.append(pline(T([(-4 + k * 1.6, -70), (-4 + k * 1.6, 70)]), "#F2F0E8", 0.8, seed + k, 0.8, 1))
    out.append(painted(D, densify(T([(-24, 66), (24, 66), (24, 76), (-24, 76)]), 6), ("#6A4428", "#3A2010", "#1A0A04"), seed + 5, sk=0.1, n=2, inkw=1, hi=0.3))
    out.append(taper(T([(-40, 20), (-50, 50), (-40, 80)]), 4 * s, 1, "#FFF2D0", 0.5))
    return "".join(out)


def fireflies(seed, n, box, col="#FFF2A0"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(5, 9):.1f}" fill="{col}" opacity="0.18"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 2.4):.1f}" fill="{col}"/>')
    return "".join(out)


@design("mahal-kita")
def mahal_kita():
    D = Doc2("ph-mk")
    out = [sky(D, [(0, "#121A44"), (0.6, "#24306A"), (1, "#3A3A78")], 1301, 600, ["#1E2A5A", "#0A1030", "#2E3A7A"], 70, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(1302)
    for _ in range(40):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 260):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(soft_glow(D, 110, 280, 100, "#FFF6D0", 0.5))
    out.append(f'<circle cx="110" cy="280" r="30" fill="#FFF4D0"/>')
    out.append(f'<circle cx="102" cy="274" r="5" fill="#E8DCB0" opacity="0.6"/><circle cx="118" cy="292" r="4" fill="#E8DCB0" opacity="0.6"/>')
    # stone wall of the bahay na bato (ground floor) with the wooden upper storey
    out.append('<g transform="translate(0 50)">')
    stone = "M 250 330 L 610 330 L 610 520 L 250 520 Z"
    out.append(f'<path d="{stone}" fill="#6A6478"/>')
    st = []
    for j in range(8):
        y = 330 + j * 24
        for i in range(-1, 9):
            x = 250 + i * 46 + (j % 2) * 23
            st.append(f'<path d="{hg.org_rect(x + 2, y + 2, 42, 20, 1303 + i * 13 + j, 0.6, 8, 3)}" fill="{rnd.choice(["#7A7488", "#5E586C", "#888096"])}"/>')
    out.append(clipped(D, stone, st))
    out.append(f'<path d="{stone}" fill="{D.lin([(0, "#0A0A20", 0.5), (1, "#0A0A20", 0.1)], 0, 0, 1, 0)}"/>')
    upper = "M 236 120 L 610 120 L 610 332 L 236 332 Z"
    out.append(f'<path d="{upper}" fill="#4A3A4A"/>')
    out.append(strokes(D.nid(), upper, (236, 120, 610, 332), ["#5A4A5A", "#2A1E2A"], 1304, n=40, angle=-90, length=(30, 80), width=(3, 7), opacity=(0.2, 0.45)))
    for k in range(9):
        out.append(pline([(240 + k * 44, 120), (240 + k * 44, 330)], "#2A1E2A", 1.4, k, 0.5, 1))
    out.append(f'<path d="{pd([(224, 112), (610, 112), (610, 126), (224, 126)])}" fill="#2A1E2A"/>')
    out.append(f'<path d="{pd([(226, 330), (610, 330), (610, 344), (226, 344)])}" fill="#2A1E2A"/>')
    # the window, glowing, capiz shutters half open, a ventanilla balustrade below
    out.append(soft_glow(D, 420, 226, 200, "#FFC860", 0.6))
    out.append(f'<path d="{pd([(330, 156), (510, 156), (510, 300), (330, 300)])}" fill="{D.lin([(0, "#FFF2C8"), (1, "#FFC870")])}"/>')
    out.append(f'<path d="{blob(420, 250, 40, 34, 1305, 0.1, 12)}" fill="#FFE8A0" opacity="0.6"/>')
    out.append(capiz_window(D, 330, 156, 384, 300, 1306, cols=2, rows=6, glow="#FFE8B0"))
    out.append(capiz_window(D, 456, 156, 510, 300, 1307, cols=2, rows=6, glow="#FFE8B0"))
    for k in range(9):
        x = 334 + k * 22
        out.append(taper([(x, 302), (x, 326)], 5, 5, "#5E3018"))
    out.append(taper([(326, 302), (514, 302)], 6, 6, "#7A4422"))
    out.append(taper([(326, 326), (514, 326)], 6, 6, "#7A4422"))
    # a potted sampaguita on the sill
    out.append(dab_crown(D, 420, 290, 30, 16, [("#6AA05A", "#2E6A2E", "#143A16")], 1308, n=40, size=(3, 6), inkw=0))
    for k in range(7):
        out.append(sampaguita_flower(D, 400 + k * 7, 284 + (k % 3) * 4, 4.5, 1309 + k))
    out.append('</g>')
    # ground, a bench, and the guitar leaning on it
    gp = "M -10 470 L 610 470 L 610 610 L -10 610 Z"
    out.append(f'<path d="{gp}" fill="{D.lin([(0, "#2A2A4A"), (1, "#14142A")])}"/>')
    out.append(f'<path d="{blob(420, 476, 170, 22, 1310, 0.1, 14)}" fill="#FFC860" opacity="0.12"/>')
    out.append(painted(D, rect_pts(250, 432, 500, 452, 14, 1311, 0.5), NARRA, 1311, sdir=(0, 1), sk=0.25, angle=0, n=14, inkw=1.6, hi=0.35))
    for x in (270, 476):
        out.append(taper([(x, 452), (x, 512)], 10, 10, "#4A2410"))
    # sampaguita bush at left
    out.append(dab_crown(D, 110, 470, 110, 70, [("#5A8A4A", "#2A5A2A", "#102A12")], 1312, n=140, size=(6, 12), inkw=0))
    for k in range(26):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        out.append(sampaguita_flower(D, 110 + math.cos(a) * 96 * r, 470 + math.sin(a) * 56 * r, rnd.uniform(5, 7), 1320 + k, rot_=rnd.uniform(0, 60)))
    out.append(guitar(D, 330, 470, 0.86, 18, 1330))
    out.append(fireflies(1340, 14, (40, 360, 560, 560)))
    out.append(p_heart(D, 228, 380, 10, PULA, 1341, rot_=-12, inkw=1))
    out.append(p_heart(D, 254, 352, 7, ("#FFB0C8", "#EE6A98", "#A82A5A"), 1342, rot_=10, inkw=0.8))
    # lettering
    out.append(letters(D, 300, 124, "Mahal kita", SERIF_IT, 114, "#FFE4C0", ["#FFFFFF", "#FFD8B0", "#F8C8A8"], 1350, max_w=470,
                       shadow="#0A0A2A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 162, "I LOVE YOU", "#F2A8C8", font=JOS, size=19, ls=8, line_w=30, gap=12))
    return finish_b(D, out, 1351, "#0A0A2A", 0.6)


# ================================================================ 16. bahala na — a bangka heads out at sunrise
def bangka(D, cx, wl, s, seed, hull=("#FFFFFF", "#F2EEE6", "#A8A49C"), stripe=BUGHAW, trim=PULA, sil=None, boatman=True):
    """Outrigger canoe (bangka) in side view, bow to the right: slim upswept hull, curved bamboo cross-arms (tarik)
    and the outrigger floats (katig) on the near side."""
    P = lambda x, y: (cx + x * s, wl + y * s)
    out = []
    if not sil:
        out.append(f'<path d="{blob(cx, wl + 6 * s, 210 * s, 10 * s, seed, 0.1, 16)}" fill="#1A2A4A" opacity="0.35"/>')
    # far outrigger float and arms
    far = "#4A3A3A" if not sil else sil
    out.append(taper([P(-170, -16), P(170, -18)], 5 * s, 5 * s, far))
    for x in (-110, 60):
        out.append(taper([P(x - 4, -40), P(x + 30, -30), P(x + 60, -18)], 4 * s, 3 * s, far))
    hullp = [P(-200, -40), P(-176, -22), P(-130, -6), (P(0, 0)), P(130, -6), P(180, -24), P(214, -58), P(206, -60), P(172, -42), P(100, -40), P(-100, -40), P(-170, -42), P(-196, -54)]
    if sil:
        out.append(f'<path d="{smooth_closed(hullp)}" fill="{sil}"/>')
    else:
        out.append(painted(D, hullp, hull, seed, sdir=(0.2, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
        hd = smooth_closed(hullp)
        bands = [taper([P(-190, -38), P(-100, -30), P(0, -28), P(100, -30), P(200, -50)], 6 * s, 6 * s, stripe[1]),
                 taper([P(-180, -26), P(-100, -18), P(0, -16), P(100, -18), P(176, -32)], 3 * s, 3 * s, trim[1]),
                 f'<path d="{hd}" fill="{D.lin([(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0), (1, "#1A1A3A", 0.4)])}"/>']
        out.append(clipped(D, hd, bands))
        # the painted eye at the bow
        ex, ey = P(170, -40)
        out.append(f'<path d="{blob(ex, ey, 6 * s, 4 * s, seed, 0.1, 8)}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/><circle cx="{ex + s:.1f}" cy="{ey:.1f}" r="{2 * s:.1f}" fill="{INK}"/>')
    # boatman, standing at the stern with a long pole
    bm = "#2A1E2A" if not sil else sil
    if not boatman:
        bm = None
    if bm:
        out.append(f'<path d="{blob(*P(-128, -96), 7 * s, 8 * s, seed + 3, 0.05, 10)}" fill="{bm}"/>')
        out.append(f'<path d="{smooth_closed([P(-138, -86), P(-118, -86), P(-114, -60), P(-122, -42), P(-132, -42), P(-140, -60)])}" fill="{bm}"/>')
        out.append(taper([P(-140, -108), P(-128, -104), P(-116, -108)], 3 * s, 3 * s, bm))
        out.append(pline([P(-150, -150), P(-100, -10)], bm, 2.6 * s, seed, 1, 1))
        out.append(pline([P(-132, -80), P(-140, -110)], bm, 2.6 * s, seed + 1, 1, 1))
    # near arms and outrigger float
    near = "#C8A86A" if not sil else sil
    for x in (-110, 60):
        out.append(taper([P(x - 4, -40), P(x + 20, -46), P(x + 50, -26), P(x + 70, 4)], 5 * s, 4 * s, near))
    out.append(taper([P(-180, 6), P(-60, 10), P(60, 10), P(176, 4)], 7 * s, 6 * s, near))
    if not sil:
        out.append(taper([P(-170, 4), P(170, 2)], 2 * s, 2 * s, "#F6E8B0", 0.8))
        for x in (-180, 176):
            out.append(f'<path d="{blob(*P(x, 4), 5 * s, 3 * s, seed + x, 0.1, 8)}" fill="#A8884A"/>')
    return "".join(out)


@design("bahala-na")
def bahala_na():
    D = Doc2("ph-bn")
    out = [sky(D, [(0, "#1E2A6A"), (0.32, "#6A5A9A"), (0.52, "#F29A7A"), (0.62, "#FFD08A")], 1401, 360, ["#3A4A8A", "#F2A88A", "#FFE0A8"], 60, angle=-3, sop=(0.06, 0.16))]
    rnd = random.Random(1402)
    for _ in range(26):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 150):.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    out.append(soft_glow(D, 300, 336, 260, "#FFE8A0", 0.8))
    out.append(f'<path d="M 252 340 A 48 48 0 0 1 348 340 Z" fill="#FFF2B0"/>')
    for k, (y, w) in enumerate(((262, 220), (284, 160))):
        out.append(f'<path d="{blob(300 + (k - 0.5) * 120, y, w * 0.5, 8, 1403 + k, 0.2, 12)}" fill="#F6B07A" opacity="0.6"/>')
    # islands with palms on either side
    il = ridge([(-20, 340), (20, 300), (70, 286), (130, 304), (180, 340)], 1404, 4, 3)
    out.append(hill(D, il, 342, ("#6A4A6A", "#4A3452", "#2A1E36"), 1405, inkw=0))
    ir = ridge([(420, 340), (480, 310), (540, 296), (620, 320)], 1406, 4, 3)
    out.append(hill(D, ir, 342, ("#7A5A7A", "#5A405E", "#36263E"), 1407, inkw=0))
    for k, (bx, by, tx, ty) in enumerate(((40, 298, 30, 236), (88, 292, 104, 240), (510, 306, 520, 252))):
        out.append(palm(D, (bx, by), (tx, ty), 1408 + k, sil="#2A1E36", L=40, width=6, nuts=False, leaf_cols=["#2A1E36"]))
    # the sea with the sun's path
    out.append(sea(D, 340, 610, [(0, "#E8906A"), (0.3, "#8A6A9A"), (1, "#1E2A5A")], 1410, ["#F2B08A", "#4A4A8A", "#FFD8A8"], n=90))
    path = []
    for k in range(40):
        y = 346 + k * 6
        w = 20 + k * 3.5
        x = 300 + rnd.uniform(-w, w) * 0.6
        path.append(taper([(x - w * rnd.uniform(0.2, 0.5), y), (x + w * rnd.uniform(0.2, 0.5), y + 1)], 3, 2, rnd.choice(["#FFE8A8", "#FFD080", "#FFF6D0"]), rnd.uniform(0.5, 0.9)))
    out.append("".join(path))
    out.append(seagull(150, 220, 14, "#3A2A4A") if False else bird_v(150, 214, 12, "#3A2A4A") + bird_v(176, 230, 8, "#3A2A4A") + bird_v(452, 196, 10, "#3A2A4A"))
    # wake behind the boat
    for k in range(5):
        y = 470 + k * 9
        out.append(taper([(60 + k * 10, y + 10), (150, y + 2), (230, y - 4)], 1, 3, "#FFE8C8", 0.6 - k * 0.08))
    out.append(bangka(D, 316, 466, 1.12, 1420))
    # reflection of the boat
    out.append(f'<g opacity="0.25" transform="translate(0 932) scale(1 -1)">{bangka(D, 316, 466, 1.12, 1421, sil="#1A1A3A")}</g>')
    # lettering
    out.append(letters(D, 300, 128, "Bahala na", SERIF_IT, 130, "#FFF0D8", ["#FFFFFF", "#FFE0C0", "#F8D0B8"], 1430, max_w=460,
                       shadow="#0E1238", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 174, "COME WHAT MAY", "#FFD08A", font=JOS, size=21, ls=9, line_w=34, gap=14))
    return finish_b(D, out, 1431, "#1A1A3A", 0.6)


# ================================================================ 17. hay naku! — the washing is out and here comes the rain
def garment(D, kind, x, y, w, seed, pal, sway=0):
    """A piece of laundry hanging from the line at its top edge (x, y) to (x + w, y)."""
    rnd = random.Random(seed)
    s = w / 100
    def T(pts):
        return [(x + px * s + sway * (py / 100) * s, y + py * s) for px, py in pts]
    if kind == "shirt":
        pts = T([(0, 0), (30, 4), (50, 10), (70, 4), (100, 0), (118, 26), (100, 40), (92, 32), (92, 110), (8, 110), (8, 32), (0, 40), (-18, 26)])
    elif kind == "dress":
        pts = T([(20, 0), (40, 6), (60, 6), (80, 0), (86, 30), (96, 70), (112, 140), (-12, 140), (4, 70), (14, 30)])
    elif kind == "towel":
        pts = T([(0, 0), (100, 0), (100, 150), (0, 150)])
    elif kind == "shorts":
        pts = T([(0, 0), (100, 0), (106, 80), (60, 82), (50, 40), (40, 82), (-6, 80)])
    else:  # sock
        pts = T([(0, 0), (30, 0), (30, 70), (52, 90), (40, 104), (10, 86), (0, 70)])
    pts = densify(pts, 10)
    out = [painted(D, pts, pal, seed, sdir=(0.7, 0.6), sk=0.15, angle=-80, n=int(w * 0.25) + 4, inkw=1.4, hi=0.35)]
    d = smooth_closed(pts)
    deco = []
    if kind == "dress":
        for _ in range(16):
            px, py = x + rnd.uniform(0, w), y + rnd.uniform(10, 140 * s)
            deco.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(3, 5):.1f}" fill="#FFFFFF" opacity="0.8"/><circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="#F6C51E"/>')
    if kind == "towel":
        for t in (0.12, 0.18, 0.84, 0.9):
            deco.append(f'<rect x="{x - 20:.1f}" y="{y + 150 * s * t:.1f}" width="{w + 40:.1f}" height="{4 * s + 2:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    if kind == "shirt":
        deco.append(f'<path d="M {x + 36 * s:.1f} {y + 6 * s:.1f} Q {x + 50 * s:.1f} {y + 22 * s:.1f} {x + 64 * s:.1f} {y + 6 * s:.1f}" fill="none" stroke="{pal[2]}" stroke-width="2"/>')
        deco.append(f'<rect x="{x - 10:.1f}" y="{y + 58 * s:.1f}" width="{w + 30:.1f}" height="{12 * s:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    deco.append(f'<path d="{d}" fill="{D.lin([(0, "#000000", 0.0), (0.7, "#000000", 0.0), (1, "#000000", 0.25)], 0, 0, 1, 0)}"/>')
    out.append(clipped(D, d, deco))
    # clothespins
    for px in (x + w * 0.12, x + w * 0.88):
        out.append(f'<path d="{hg.org_rect(px - 3, y - 8, 6, 18, seed + int(px), 0.3, 6, 1.5)}" fill="{rnd.choice(["#E8304A", "#1E9AD8", "#2EB05A", "#F6C51E"])}" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def rain(seed, n, box, col="#D8E8F8", op=(0.35, 0.75), ang=105, L=(14, 30)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        l = rnd.uniform(*L)
        a = math.radians(ang)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * l:.1f} {math.sin(a) * l:.1f}" stroke="{col}" stroke-width="{rnd.uniform(1.4, 2.4):.1f}" stroke-linecap="round" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


@design("hay-naku")
def hay_naku():
    D = Doc2("ph-hn")
    out = [sky(D, [(0, "#5A6A84"), (0.5, "#8A9AB0"), (1, "#C8D4DC")], 1501, 600, ["#6A7A94", "#A8B8C8", "#4A5A74"], 70, angle=-3, sop=(0.08, 0.2))]
    # a patch of sun still on the right
    out.append(soft_glow(D, 540, 230, 200, "#FFF2C8", 0.55))
    # heavy rain clouds rolling in from the left
    for k, (x, y, w) in enumerate(((60, 250, 260), (230, 226, 220), (-20, 300, 220), (380, 210, 160))):
        out.append(puff_cloud(D, x, y, w, 1502 + k, pal=("#A8B4C4", "#7A8698", "#4A5468"), op=0.95))
    out.append(rain(1506, 70, (-20, 230, 360, 600)))
    # the house: wooden wall, window with grille, corrugated roof edge
    hx = 430
    wallp = f"M {hx} 250 L 610 250 L 610 520 L {hx} 520 Z"
    out.append(f'<path d="{wallp}" fill="#C89A6A"/>')
    planks = [pline([(hx, 270 + k * 22), (610, 270 + k * 22)], "#8A5E36", 1.6, k, 0.6, 1) for k in range(12)]
    out.append(clipped(D, wallp, planks + [strokes(D.nid(), wallp, (hx, 250, 610, 520), ["#E0B888", "#8A5E36"], 1507, n=40, angle=0, length=(30, 80), width=(2, 5), opacity=(0.15, 0.35))]))
    out.append(f'<path d="{pd([(hx - 30, 252), (620, 252), (620, 232), (hx - 20, 222)])}" fill="#A8B0B8"/>')
    for k in range(10):
        out.append(pline([(hx - 26 + k * 20, 224 + k * 0.5), (hx - 26 + k * 20, 252)], "#7A848E", 2, k, 0.7, 1))
    out.append(f'<path d="{pd([(470, 300), (560, 300), (560, 396), (470, 396)])}" fill="#3A4A5A"/>')
    out.append(f'<path d="{pd([(470, 300), (560, 300), (560, 396), (470, 396)])}" fill="#FFE8A8" opacity="0.25"/>')
    for k in range(5):
        out.append(pline([(470 + k * 22.5, 300), (470 + k * 22.5, 396)], "#2A2A34", 2.4, k, 0.9, 1))
    out.append(pline([(470, 348), (560, 348)], "#2A2A34", 2.4, 9, 0.9, 1))
    out.append(ink(pd([(470, 300), (560, 300), (560, 396), (470, 396)]), "#5E3A1E", 3, 1508, 1, 0.9))
    # yard: concrete and a strip of grass
    gp = "M -10 470 L 610 470 L 610 610 L -10 610 Z"
    out.append(f'<path d="{gp}" fill="{D.lin([(0, "#8AA070"), (0.25, "#9AA890"), (1, "#7A8A74")])}"/>')
    out.append(grass(1509, (-10, 470, 430, 500), ["#5A8A3A", "#7AAA4A", "#3E6A2A"], n=120, h=(8, 18)))
    for _ in range(14):
        rnd = random.Random(1510 + _)
        x, y = rnd.uniform(20, 400), rnd.uniform(500, 590)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(6, 14):.1f}" ry="{rnd.uniform(1.5, 3):.1f}" fill="none" stroke="#D8E8F0" stroke-width="1.2" opacity="0.7"/>')
    # bamboo pole and the sagging line
    out.append(taper([(76, 520), (72, 262)], 10, 8, "#C8A86A"))
    for y in (300, 360, 420, 480):
        out.append(pline([(68, y), (82, y + 2)], "#7A5A2A", 2, y, 0.8, 1))
    line = [(74, 268), (200, 302), (320, 306), (450, 280)]
    out.append(pline(catmull(line, 6), "#3A3A44", 1.8, 1511, 0.9, 1))
    items = [("towel", 92, 284, 74, ("#8AD0E8", "#2E9AC8", "#14587A"), 6), ("shirt", 180, 300, 76, ("#FFA8A0", "#E8504A", "#8A1E1A"), 10),
             ("dress", 268, 306, 76, ("#F8B8E0", "#E060A8", "#8A205A"), 14), ("shorts", 358, 300, 58, ("#9AB8F0", "#3A6AC8", "#1A3A7A"), 10),
             ("sock", 424, 286, 26, ("#FFF2A0", "#F2C82A", "#A8820A"), 8)]
    for k, (kind, x, y, w, pal, sw) in enumerate(items):
        out.append(garment(D, kind, x, y, w, 1512 + k, pal, sway=sw))
    out.append(rain(1520, 30, (-20, 260, 260, 600), col="#E8F2FF", op=(0.5, 0.9)))
    # batya (wash basin) with the rest of the laundry, and a tabo floating
    bx, by = 470, 548
    out.append(cast(D, bx + 10, by + 6, 86, 10, strength=0.45, seed=1521))
    basin = [(bx - 84, by - 44), (bx - 70, by), (bx + 70, by), (bx + 84, by - 44)]
    out.append(painted(D, densify(basin, 10), ("#7AC8F0", "#1E8AC8", "#0E4A7A"), 1522, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=12, inkw=1.8, hi=0.45))
    out.append(f'<path d="{ellipse_d(bx, by - 44, 84, 16)}" fill="#3AA0D8" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<path d="{ellipse_d(bx, by - 42, 76, 12)}" fill="#E8F2F8"/>')
    for k, (dx, col) in enumerate(((-40, "#F2766A"), (-6, "#F6C51E"), (26, "#7AC08A"), (52, "#B88AD8"))):
        out.append(f'<path d="{blob(bx + dx, by - 48, 22, 9, 1523 + k, 0.25, 10)}" fill="{col}" stroke="{INK}" stroke-width="1"/>')
    # lettering
    out.append(letters(D, 300, 128, "Hay naku!", SERIF_IT, 136, "#FFF4E0", ["#FFFFFF", "#E8EEF4", "#FFF0D8"], 1530, max_w=460,
                       shadow="#2A3448", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 174, "UMULAN NA NAMAN", "#FFE6A8", font=JOS, size=21, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 1531, "#2A3040", 0.6)


# ================================================================ 18. kilig — a love letter, and the butterflies get out
def butterfly(D, cx, cy, s, ang, seed, pal=("#FFC8E0", "#EE5AA0", "#8A1A5A"), spot="#FFFFFF", flap=1.0):
    """Painted butterfly seen from above: rounded fore- and hindwings with a dark border and white spots, slim body."""
    def T(pts):
        return rot([(cx + x * s, cy + y * s * 1.0) for x, y in pts], cx, cy, ang)
    out = []
    for sg in (-1, 1):
        fw = T([(0, -2), (sg * 34 * flap, -30), (sg * 46 * flap, -18), (sg * 40 * flap, 0), (sg * 10, 4)])
        hw = T([(0, 2), (sg * 30 * flap, 8), (sg * 32 * flap, 26), (sg * 14 * flap, 34), (sg * 4, 16)])
        for k, w in enumerate((fw, hw)):
            d = smooth_closed(w)
            out.append(f'<path d="{d}" fill="{pal[1]}"/>')
            out.append(clipped(D, d, [f'<path d="{d}" fill="none" stroke="{pal[2]}" stroke-width="{7 * s:.1f}"/>',
                                       f'<path d="{d}" fill="{D.rad([(0, pal[0], 0.9), (1, pal[0], 0)], 0.3 if sg < 0 else 0.7, 0.6, 0.6)}"/>']))
            for j in range(3):
                px, py = w[2][0] * 0.82 + w[1][0] * 0.18, w[2][1] * 0.8 + w[1][1] * 0.2
                out.append(f'<circle cx="{px + (j - 1) * 3 * s:.1f}" cy="{py + j * 3 * s:.1f}" r="{1.6 * s:.1f}" fill="{spot}"/>')
            out.append(ink(d, "#2A0A1A", 1.0, seed + k + sg, 1, 0.6))
    body = T([(0, -10), (2.4, 0), (0, 24), (-2.4, 0)])
    out.append(f'<path d="{smooth_closed(body)}" fill="#2A1A1A"/>')
    hx, hy = T([(0, -12)])[0]
    for sg in (-1, 1):
        tx, ty = T([(sg * 10, -30)])[0]
        out.append(pline([(hx, hy), ((hx + tx) / 2 + sg * 2, (hy + ty) / 2), (tx, ty)], "#2A1A1A", 1.1, seed, 0.9, 1))
        out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="1.6" fill="#2A1A1A"/>')
    return "".join(out)


@design("kilig")
def kilig():
    D = Doc2("ph-kl")
    out = [paper(D.nid(), "#FBE0E4", "#8A4A5A", 1601)]
    out.append(blooms(1602, ["#F8B8C8", "#E8A0C0", "#FFE0E8"], 9, (0, 0, 600, 600), (90, 200), (0.1, 0.18)))
    out.append(soft_glow(D, 300, 420, 260, "#FFFFFF", 0.6))
    # little pink hearts drifting
    rnd = random.Random(1603)
    # the opened envelope and a letter sliding out
    ex, ey, ew, eh = 300, 470, 260, 150
    out.append(cast(D, ex + 14, ey + eh / 2 + 6, ew * 0.55, 14, strength=0.4, seed=1604))
    env_back = [(ex - ew / 2, ey - eh / 2), (ex + ew / 2, ey - eh / 2), (ex + ew / 2, ey + eh / 2), (ex - ew / 2, ey + eh / 2)]
    out.append(painted(D, densify(env_back, 12), ("#FFF6EE", "#F4E2D4", "#C8A898"), 1605, sk=0.12, angle=0, n=10, inkw=1.6, hi=0.3))
    # opened flap up
    flap = [(ex - ew / 2, ey - eh / 2), (ex, ey - eh / 2 - 92), (ex + ew / 2, ey - eh / 2)]
    out.append(painted(D, densify(flap, 12), ("#FFFFFF", "#F0DCCC", "#C8A898"), 1606, sk=0.12, angle=0, n=8, inkw=1.6, hi=0.3))
    # letter
    let = rot(rect_pts(ex - 100, ey - eh / 2 - 70, ex + 100, ey + 20, 14, 1607, 0.5), ex, ey - 30, -4)
    out.append(painted(D, let, ("#FFFFFF", "#FFFCF4", "#D8D0C0"), 1607, sk=0.1, angle=0, n=6, inkw=1.3, hi=0.3))
    lines = []
    for k in range(5):
        y = ey - eh / 2 - 48 + k * 16
        x0, x1 = ex - 82, ex + 82 - (40 if k == 4 else rnd.uniform(0, 30))
        pts = [(x0, y)]
        x = x0
        while x < x1:
            x += rnd.uniform(6, 12)
            pts.append((x, y + rnd.uniform(-3, 2)))
        lines.append(pline(rot(pts, ex, ey - 30, -4), "#4A5AA8", 1.4, 1608 + k, 0.7, 1))
    out.append("".join(lines))
    # front pocket of the envelope
    front = [(ex - ew / 2, ey - eh / 2 + 4), (ex, ey + 16), (ex + ew / 2, ey - eh / 2 + 4), (ex + ew / 2, ey + eh / 2), (ex - ew / 2, ey + eh / 2)]
    out.append(painted(D, densify(front, 12), ("#FFF6EE", "#F6E6DA", "#C8A898"), 1609, sk=0.12, angle=0, n=10, inkw=1.6, hi=0.3))
    out.append(pline([(ex - ew / 2 + 4, ey + eh / 2 - 4), (ex - 30, ey + 24)], "#D8C0B0", 1.4, 1610, 0.7, 1))
    out.append(pline([(ex + ew / 2 - 4, ey + eh / 2 - 4), (ex + 30, ey + 24)], "#D8C0B0", 1.4, 1611, 0.7, 1))
    out.append(p_heart(D, ex, ey + 22, 18, PULA, 1612, inkw=1.2))
    out.append(sampaguita_flower(D, ex - 90, ey + 50, 12, 1613, layers=2))
    out.append(sampaguita_flower(D, ex - 66, ey + 60, 9, 1614))
    out.append(leaf_simple(D, ex - 80, ey + 62, 30, 8, 150, ("#8AC870", "#3E8A3A", "#1E5A22"), 1615, inkw=1))
    # the butterflies rising out of the letter
    pals = [(("#FFC8E0", "#EE5AA0", "#8A1A5A"), "#FFFFFF"), (("#FFE8A0", "#F6B41E", "#7A4A0A"), "#FFFFFF"),
            (("#A8E0F8", "#2E9AD8", "#0E3A6A"), "#FFF6D8"), (("#D8B8F8", "#8A5AD0", "#3A1A6A"), "#FFFFFF"), (("#FFB8A0", "#F2643A", "#7A1E0A"), "#FFF6D8")]
    path = [(300, 330), (250, 300), (196, 262), (170, 222), (220, 200), (300, 214), (380, 230), (430, 266), (470, 300)]
    for k, (x, y) in enumerate([(282, 340), (214, 298), (142, 262), (388, 306), (462, 262), (330, 274), (116, 340), (500, 346)]):
        pal, spot = pals[k % len(pals)]
        out.append(butterfly(D, x, y, 0.9 - 0.08 * (k % 3), rnd.uniform(-40, 40), 1620 + k, pal, spot, flap=rnd.uniform(0.75, 1.0)))
    for k in range(10):
        x, y = rnd.uniform(90, 510), rnd.uniform(244, 366)
        out.append(p_heart(D, x, y, rnd.uniform(4, 7), ("#FFC8D8", "#F27AA0", "#A82A5A"), 1640 + k, rot_=rnd.uniform(-20, 20), inkw=0.6))
    for x, y, s in ((92, 420, 9), (520, 420, 10), (456, 196, 8), (140, 180, 7)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 162, "kilig", SERIF_IT, 140, "#C02A5A", ["#E0407A", "#8A0E3A", "#F06A98"], 1650, max_w=340,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFC0D8"))
    out.append(ruled(300, 214, "KILIG TO THE BONES", "#5A3A8A", font=JOS, size=20, ls=6, line_w=28, gap=12))
    return finish_b(D, out, 1651, "#5A2A3A")


# ================================================================ 19. gigil — an aspin puppy too cute not to squeeze
def aspin_puppy(D, cx, cy, s, seed, coat=("#F2C88A", "#D89A52", "#8A5A26"), white=("#FFFFFF", "#F8F2E8", "#C8B8A0")):
    """A chubby little aspin (asong Pinoy) puppy sitting, front view: big head, floppy ears, squinty happy eyes."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    out = [cast(D, cx + 6 * s, cy + 128 * s, 110 * s, 16 * s, strength=0.45, seed=seed)]
    # tail wagging behind
    out.append(taper([P(60, 100), P(96, 80), P(110, 50)], 16 * s, 8 * s, coat[1]))
    # body
    body = [P(-74, 120), P(-80, 70), P(-56, 20), P(0, 6), P(56, 20), P(80, 70), P(74, 120), P(0, 128)]
    out.append(painted(D, body, coat, seed, sdir=(0.6, 0.8), sk=0.2, angle=-80, n=40, sw=(1.2, 3), inkw=2, hi=0.4))
    chest = [P(-34, 40), P(0, 30), P(34, 40), P(30, 100), P(0, 120), P(-30, 100)]
    out.append(painted(D, chest, white, seed + 1, sk=0.15, angle=-90, n=14, inkw=0, hi=0.4))
    # front paws
    for sg in (-1, 1):
        paw = blob_pts(*P(sg * 30, 120), 22 * s, 14 * s, seed + 2 + sg, 0.06, 12)
        out.append(painted(D, paw, white, seed + 2 + sg, sk=0.2, n=4, inkw=1.6, hi=0.4))
        for j in (-1, 0, 1):
            out.append(pline([P(sg * 30 + j * 7, 116), P(sg * 30 + j * 7, 126)], white[2], 1.4, seed + j, 0.7, 1))
    # chubby legs (haunches)
    for sg in (-1, 1):
        hp = blob_pts(*P(sg * 62, 104), 26 * s, 26 * s, seed + 5 + sg, 0.06, 12)
        out.append(painted(D, hp, coat, seed + 5 + sg, sk=0.2, n=8, inkw=1.6, hi=0.35))
    # head
    head = blob_pts(*P(0, -40), 84 * s, 70 * s, seed + 8, 0.03, 22)
    out.append(painted(D, head, coat, seed + 8, sdir=(0.6, 0.8), sk=0.15, angle=-60, n=50, sw=(1.2, 3), inkw=2.2, hi=0.45, hik=0.08))
    muzzle = blob_pts(*P(0, -8), 44 * s, 32 * s, seed + 9, 0.05, 16)
    out.append(painted(D, muzzle, white, seed + 9, sk=0.15, n=10, inkw=1.2, inkop=0.4, hi=0.4))
    out.append(painted(D, [P(-12, -106), P(12, -106), P(16, -40), P(-16, -40)], white, seed + 10, sk=0.1, n=4, inkw=0, hi=0.3))
    # ears flopping
    for sg in (-1, 1):
        ear = [P(sg * 50, -96), P(sg * 92, -96), P(sg * 104, -56), P(sg * 92, -30), P(sg * 72, -54)]
        out.append(painted(D, ear, tuple(dk(c, 0.18) for c in coat), seed + 11 + sg, sdir=(0.5, 0.8), sk=0.2, angle=-90, n=10, inkw=1.8, hi=0.3))
    # happy squinting eyes, nose, smile, tongue, blush
    for sg in (-1, 1):
        out.append(pline([P(sg * 40, -46), P(sg * 30, -56), P(sg * 18, -48)], "#2A1408", 4 * s, seed + sg, 1, 1))
        out.append(f'<path d="{blob(*P(sg * 50, -24), 14 * s, 8 * s, seed + 20 + sg, 0.1, 10)}" fill="#F28AA0" opacity="0.55"/>')
    out.append(f'<path d="{smooth_closed([P(-12, -28), P(12, -28), P(8, -18), P(0, -14), P(-8, -18)])}" fill="#2A1408"/>')
    out.append(f'<path d="{blob(*P(-4, -25), 4 * s, 2 * s, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(pline([P(0, -14), P(0, -6)], "#2A1408", 2.4 * s, seed, 1, 1))
    out.append(pline([P(-18, -6), P(-8, 0), P(0, -6), P(8, 0), P(18, -6)], "#2A1408", 2.4 * s, seed + 1, 1, 1))
    tongue = [P(-8, -2), P(8, -2), P(9, 12), P(0, 18), P(-9, 12)]
    out.append(painted(D, tongue, ("#FFB0C0", "#F2708A", "#A8304A"), seed + 30, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(pline([P(0, 0), P(0, 12)], "#A8304A", 1.2, seed + 31, 0.7, 1))
    # collar with a little bell
    out.append(taper([P(-52, 18), P(0, 30), P(52, 18)], 9 * s, 9 * s, PULA[1]))
    out.append(f'<circle cx="{P(0, 34)[0]:.1f}" cy="{P(0, 34)[1]:.1f}" r="{8 * s:.1f}" fill="#F6C51E" stroke="#8A5A0A" stroke-width="1.4"/>')
    out.append(f'<path d="M {P(-5, 36)[0]:.1f} {P(-5, 36)[1]:.1f} L {P(5, 36)[0]:.1f} {P(5, 36)[1]:.1f}" stroke="#8A5A0A" stroke-width="1.4"/>')
    return "".join(out)


@design("gigil")
def gigil():
    D = Doc2("ph-gg")
    out = [paper(D.nid(), "#DDF0E4", "#4A7A5A", 1701)]
    out.append(blooms(1702, ["#B8E0C8", "#A8D8E8", "#E8F8EC"], 9, (0, 0, 600, 600), (90, 200), (0.1, 0.18)))
    out.append(soft_glow(D, 300, 400, 260, "#FFFFFF", 0.7))
    # a banig cushion on the floor
    rug = [(110, 470), (490, 470), (530, 560), (70, 560)]
    rd = smooth_closed(densify(rug, 12))
    out.append(cast(D, 300, 560, 240, 14, strength=0.35, seed=1703))
    out.append(banig(D, rd, 1704, cell=9, base="#E8D0A0", bands=("#E8508A", "#2E9A7A", "#F2B21E", "#6A4AB0"), rot_=45))
    out.append(clipped(D, rd, [f'<path d="{rd}" fill="{D.lin([(0, "#3A1A06", 0.15), (1, "#3A1A06", 0.0)])}"/>']))
    out.append(ink(rd, INK, 1.4, 1705, 1, 0.5))
    out.append(aspin_puppy(D, 300, 392, 1.25, 1706))
    # squeeze lines and hearts around the cheeks
    for sg in (-1, 1):
        for k in range(3):
            a = math.radians(-30 + k * 30)
            x0, y0 = 300 + sg * (128 + math.cos(a) * 10), 330 + math.sin(a) * 40
            out.append(taper([(x0, y0), (x0 + sg * 22 * math.cos(a), y0 + 22 * math.sin(a))], 4, 1.4, "#E8508A", 0.85))
    rnd = random.Random(1707)
    for k, (x, y, sz) in enumerate(((112, 260, 12), (486, 252, 14), (460, 420, 9), (138, 420, 10), (520, 340, 8))):
        out.append(p_heart(D, x, y, sz, ("#FFB8CC", "#F2648E", "#A82A5A"), 1708 + k, rot_=rnd.uniform(-20, 20), inkw=1))
    for x, y, s in ((84, 330, 9), (530, 200, 8), (420, 214, 7)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 156, "gigil!", SERIF_IT, 128, "#1E6A4A", ["#2E8A62", "#0E4A30", "#4AAA80"], 1720, max_w=340,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#B8F0D0"))
    out.append(ruled(300, 206, "THAT URGE TO SQUEEZE SOMETHING CUTE", "#C83A6A", font=JOS, size=16, ls=3, line_w=16, gap=10, max_w=430))
    return finish_b(D, out, 1721)


# ================================================================ 20. simbang gabi — dawn mass, and bibingka at the church steps
def stone_church(D, cx, base, w, h, seed, haze=0.0):
    """A Filipino colonial stone church: broad facade with a pediment, arched doorway glowing, a squat bell tower."""
    hz = (lambda c: mix(c, "#5A6A9A", haze)) if haze else (lambda c: c)
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    out = []
    # bell tower at the right
    tx0, tx1 = r - 6, r + w * 0.3
    for k, (y0, y1, inset) in enumerate(((top - h * 0.15, base, 0), (top - h * 0.48, top - h * 0.15, 8), (top - h * 0.7, top - h * 0.48, 16))):
        pts = rect_pts(tx0 + inset, y0, tx1 - inset, y1, 14, seed + k, 0.5)
        out.append(painted(D, pts, (hz("#D8B890"), hz("#A88660"), hz("#5A4230")), seed + k, sdir=(0.9, 0.3), sk=0.15, angle=-90, n=20, inkw=1.4, inkop=0.5, hi=0.3))
        ax = (tx0 + tx1) / 2
        ay = (y0 + y1) / 2
        out.append(f'<path d="M {ax - 9:.1f} {ay + 14:.1f} L {ax - 9:.1f} {ay - 4:.1f} Q {ax:.1f} {ay - 18:.1f} {ax + 9:.1f} {ay - 4:.1f} L {ax + 9:.1f} {ay + 14:.1f} Z" fill="{hz("#2A2238")}"/>')
    tx = (tx0 + tx1) / 2
    out.append(f'<path d="{pd([(tx0 + 14, top - h * 0.7), (tx, top - h * 0.86), (tx1 - 14, top - h * 0.7)])}" fill="{hz("#7A6A5E")}"/>')
    out.append(f'<path d="M {tx:.1f} {top - h * 0.86:.1f} l 0 -14 M {tx - 5:.1f} {top - h * 0.86 - 9:.1f} l 10 0" stroke="{hz("#5A4E44")}" stroke-width="2.4"/>')
    # facade with pediment and scroll shoulders
    fac = [(l, base), (l, top + h * 0.1), (l + w * 0.12, top + h * 0.05), (l + w * 0.2, top - h * 0.08), (cx, top - h * 0.3), (r - w * 0.2, top - h * 0.08), (r - w * 0.12, top + h * 0.05), (r, top + h * 0.1), (r, base)]
    out.append(painted(D, densify(fac, 14), (hz("#ECC89A"), hz("#C49A6C"), hz("#6A4A30")), seed + 5, sdir=(0.6, 0.6), sk=0.12, angle=-90, n=50, inkw=1.6, inkop=0.6, hi=0.3))
    fd = smooth_closed(densify(fac, 14))
    rnd = random.Random(seed)
    blocks = []
    for j in range(int(h / 14) + 6):
        y = top - h * 0.3 + j * 14
        blocks.append(pline([(l, y), (r, y + rnd.uniform(-1, 1))], hz("#8A7A68"), 0.9, seed + j, 0.35, 1))
    blocks.append(f'<path d="{fd}" fill="{D.lin([(0, "#FFE8B0", 0.0), (0.7, "#FFE8B0", 0), (1, "#FFC870", 0.25)], 0, 0, 0, 1)}"/>')
    out.append(clipped(D, fd, blocks))
    for x in (l + w * 0.22, r - w * 0.22, l + w * 0.06, r - w * 0.06):
        out.append(taper([(x, base), (x, top + h * 0.14)], 7, 7, hz("#C8B89E"), 0.9))
        out.append(taper([(x + 3, base), (x + 3, top + h * 0.14)], 2, 2, hz("#6A5A48"), 0.6))
    out.append(taper([(l + 2, top + h * 0.42), (r - 2, top + h * 0.42)], 6, 6, hz("#C8B89E"), 0.9))
    # rose window, niches
    out.append(f'<circle cx="{cx:.1f}" cy="{top + h * 0.02:.1f}" r="{w * 0.07:.1f}" fill="{hz("#FFD880")}" stroke="{hz("#5A4E44")}" stroke-width="2"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M {cx:.1f} {top + h * 0.02:.1f} l {math.cos(a) * w * 0.07:.1f} {math.sin(a) * w * 0.07:.1f}" stroke="{hz("#8A5A2A")}" stroke-width="1.2"/>')
    for sg in (-1, 1):
        nx_ = cx + sg * w * 0.36
        out.append(f'<path d="M {nx_ - 8:.1f} {top + h * 0.34:.1f} L {nx_ - 8:.1f} {top + h * 0.2:.1f} Q {nx_:.1f} {top + h * 0.12:.1f} {nx_ + 8:.1f} {top + h * 0.2:.1f} L {nx_ + 8:.1f} {top + h * 0.34:.1f} Z" fill="{hz("#FFD070")}" opacity="0.85"/>')
    # the great arched door, open and glowing
    dw, dh = w * 0.2, h * 0.46
    door = f"M {cx - dw / 2:.1f} {base} L {cx - dw / 2:.1f} {base - dh + dw / 2:.1f} A {dw / 2:.1f} {dw / 2:.1f} 0 0 1 {cx + dw / 2:.1f} {base - dh + dw / 2:.1f} L {cx + dw / 2:.1f} {base} Z"
    out.append(soft_glow(D, cx, base - dh * 0.4, dw * 2.4, "#FFC860", 0.7))
    out.append(f'<path d="{door}" fill="{D.lin([(0, "#FFF2C0"), (1, "#FFB848")])}"/>')
    out.append(f'<path d="{door}" fill="none" stroke="{hz("#5A4E44")}" stroke-width="3"/>')
    return "".join(out)


def bibingka(D, cx, cy, r, seed):
    """Bibingka seen from above on its banana-leaf liner: golden, browned top, a slice of salted egg and cheese, butter melting."""
    out = [cast(D, cx + 5, cy + 6, r * 1.2, r * 0.5, strength=0.35, seed=seed)]
    leaf = ell_pts(cx, cy, r * 1.22, r * 0.5, 0, 360, 28)[:-1]
    out.append(painted(D, leaf, SAGING, seed, sk=0.2, angle=0, n=10, inkw=1.2, hi=0.3))
    top = ell_pts(cx, cy - 4, r, r * 0.4, 0, 360, 28)[:-1]
    out.append(painted(D, top, ("#FFE29A", "#E8A848", "#9A5A1A"), seed + 1, sdir=(0.4, 0.9), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.45))
    rnd = random.Random(seed)
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.8
        out.append(f'<path d="{blob(cx + math.cos(a) * r * rr, cy - 4 + math.sin(a) * r * 0.4 * rr, rnd.uniform(4, 9), rnd.uniform(2, 3), rnd.randint(0, 999), 0.3, 8)}" fill="#A85A14" opacity="0.5"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy - 6, r * 0.22, r * 0.12, seed + 2, 0.1, 10)}" fill="#FBF6EC" stroke="#C83A3A" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy - 6, r * 0.11, r * 0.07, seed + 3, 0.1, 10)}" fill="#F2802A"/>')
    out.append(f'<path d="{blob(cx + r * 0.3, cy - 8, r * 0.2, r * 0.1, seed + 4, 0.15, 10, 15)}" fill="#FFF2B0" stroke="#C8A040" stroke-width="1"/>')
    out.append(f'<path d="{blob(cx + 2, cy - 2, r * 0.16, r * 0.07, seed + 5, 0.25, 10)}" fill="#FFF6C8" opacity="0.85"/>')
    return "".join(out)


def puto_bumbong(D, x, y, L, ang, seed):
    """One length of puto bumbong: purple sticky-rice log with butter, grated coconut and muscovado on top."""
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)
    x1, y1 = x + math.cos(a) * L, y + math.sin(a) * L
    pts = [(x + nx * 9, y + ny * 9), (x1 + nx * 9, y1 + ny * 9), (x1 - nx * 9, y1 - ny * 9), (x - nx * 9, y - ny * 9)]
    out = [painted(D, densify(pts, 8), ("#B888E0", "#7A3AB0", "#3A1060"), seed, sdir=(nx, ny), sk=0.25, angle=ang, n=8, inkw=1.2, hi=0.5)]
    rnd = random.Random(seed)
    for _ in range(int(L / 3)):
        t = rnd.uniform(0.05, 0.95)
        px, py = x + (x1 - x) * t + nx * rnd.uniform(-6, 4), y + (y1 - y) * t + ny * rnd.uniform(-6, 4)
        out.append(f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#FFFFFF", "#FFFFFF", "#A8642A"])}" stroke-width="1.8" stroke-linecap="round"/>')
    return "".join(out)


@design("simbang-gabi")
def simbang_gabi():
    D = Doc2("ph-sb")
    out = [sky(D, [(0, "#0E1440"), (0.55, "#2A3474"), (0.85, "#6A5A9A")], 1801, 600, ["#1E2A5A", "#3A3A7A"], 60, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(1802)
    for _ in range(40):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 300):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(sparkle(500, 100, 9, "#FFF6D8", 0.95))
    # plaza and church
    out.append(f'<path d="M -10 400 L 610 400 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#3A3858"), (1, "#1E1E36")])}"/>')
    out.append(stone_church(D, 270, 404, 260, 124, 1803, haze=0.12))
    for k, (x, col) in enumerate(((84, PULA), (168, ("#7AE0A0", "#1E9A5A", "#0A4A2A")), (510, ("#FFB0D8", "#E8509A", "#8A1A5A")))):
        out.append(pline([(x, 200), (x, 222)], "#0A0A1A", 1.4, k, 0.9, 1))
        out.append(parol(D, x, 248, 22, 1804 + k, body=col, accent=("#FFFFFF", "#F2EAD8", "#C4B49A"), ring=False))
    # people walking to mass (small silhouettes)
    for k, (x, f) in enumerate(((170, 1), (196, 1), (380, -1), (404, -1), (430, -1))):
        out.append(figures.person(x, 412 + k % 2 * 3, 30, "walk", f, "silhouette:#1A1830", seed=1810 + k))
    # the bibingka stall up front: a table with banana leaves, clay oven with coals on its lid
    out.append(soft_glow(D, 300, 470, 300, "#FFB860", 0.45))
    out.append(painted(D, rect_pts(-10, 450, 610, 476, 20, 1820, 0.6), NARRA, 1820, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(f'<path d="M -10 476 L 610 476 L 610 610 L -10 610 Z" fill="#5E3018"/>')
    out.append(strokes(D.nid(), "M -10 476 L 610 476 L 610 610 L -10 610 Z", (-40, 476, 600, 600), ["#8A4E2A", "#3A1A08"], 1821, n=40, angle=-90, length=(30, 80), width=(3, 8), opacity=(0.2, 0.4)))
    for k in range(7):
        out.append(pline([(k * 92 + 20, 478), (k * 92 + 22, 600)], "#2A1006", 1.6, k, 0.6, 1))
    # clay oven (palayok with embers on the lid)
    ox, oy = 470, 452
    out.append(palayok(D, ox, oy - 64, 54, 66, 1822, ry=14, soot=0.4))
    out.append(f'<path d="{blob(ox, oy - 66, 62, 12, 1823, 0.1, 14)}" fill="#4A3A34"/>')
    for k in range(12):
        x, y = ox + rnd.uniform(-48, 48), oy - 70 + rnd.uniform(-6, 6)
        out.append(f'<path d="{blob(x, y, rnd.uniform(5, 8), rnd.uniform(3, 5), 1824 + k, 0.2, 8)}" fill="{rnd.choice(["#FF6A2A", "#FFB040", "#C83A1A", "#2A1A1A"])}"/>')
    out.append(soft_glow(D, ox, oy - 74, 70, "#FF8A3A", 0.6))
    out.append(steam(ox, oy - 86, 50, 1825, "#FFFFFF", 2, 24, 6, 0.4))
    # bibingka and puto bumbong on the table
    out.append(banana_leaf(D, 60, 512, -6, 330, 46, 1826, pal=SAGING))
    out.append(bibingka(D, 140, 500, 58, 1827))
    out.append(bibingka(D, 270, 518, 52, 1828))
    for k in range(3):
        out.append(puto_bumbong(D, 352 + k * 6, 520 + k * 16, 110, -10, 1829 + k))
    out.append(steam(150, 470, 50, 1832, "#FFFFFF", 2, 24, 6, 0.45))
    # lettering
    out.append(letters(D, 300, 116, "Simbang Gabi", SERIF_IT, 112, "#FFE6B0", ["#FFFFFF", "#FFD890", "#FFF0C8"], 1840, max_w=460,
                       shadow="#05051A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 160, "BIBINGKA AT PUTO BUMBONG", "#F2A8C8", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 1841, "#0A0A2A", 0.6)


# ================================================================ 21. banaue — the rice terraces in morning mist
def terraces(D, seed, y_top, y_bot, n=14, bowl=90, cx=300, pal_dry=("#B8D878", "#7AA83A", "#3E6A1E"), water_every=3, spur=0.0, spur_x=400, flooded=None):
    """Contour rice terraces filling a valley: each level a curved band with a dark mud wall, a lit lip, and
    some flooded paddies mirroring the sky."""
    rnd = random.Random(seed)
    out = []
    ys = []
    t = 0
    for i in range(n + 1):
        f = i / n
        ys.append(y_top + (y_bot - y_top) * (f ** 1.35))
    for i in range(n):
        y0, y1 = ys[i], ys[i + 1]
        depth = (i + 1) / n
        b = bowl * (1 - 0.6 * depth)
        def curve(y, ph):
            return [(x, y - b * (1 - ((x - cx) / 330) ** 2) - spur * (1 - 0.5 * depth) * math.exp(-((x - spur_x) / 80) ** 2)
                     + 4 * math.sin(x / (40 + 30 * depth) + ph)) for x in range(-20, 641, 16)]
        top_c = curve(y0, i * 1.3)
        bot_c = curve(y1, (i + 1) * 1.3)
        d = smooth_open(top_c) + " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in bot_c[::-1]) + " Z"
        haze = max(0.0, 0.55 - depth * 0.7)
        is_flooded = (i in flooded) if flooded is not None else (i % water_every == 1)
        if is_flooded:
            g = D.lin([(0, mix("#C8E0F0", "#E8F0F4", haze)), (1, mix("#8AB8D8", "#D8E8F0", haze))], 0, 0, 0, 1)
            out.append(f'<path d="{d}" fill="{g}"/>')
            for _ in range(int(6 + depth * 8)):
                x = rnd.uniform(0, 600)
                yy = y0 + (y1 - y0) * rnd.uniform(0.3, 0.9) - b * (1 - ((x - cx) / 330) ** 2)
                out.append(f'<path d="M {x:.1f} {yy:.1f} l {rnd.uniform(10, 30):.1f} 0" stroke="#FFFFFF" stroke-width="1.4" opacity="0.6"/>')
                if rnd.random() < 0.5:
                    out.append(f'<path d="M {x + 4:.1f} {yy - 2:.1f} l 0 -4 M {x + 8:.1f} {yy - 1:.1f} l 1 -4" stroke="{mix("#5A9A3A", "#C8D8E0", haze)}" stroke-width="1.2"/>')
        else:
            c = mix(rnd.choice([pal_dry[0], pal_dry[1], mix(pal_dry[0], pal_dry[1], 0.5)]), "#C8D8E0", haze)
            out.append(f'<path d="{d}" fill="{c}"/>')
            out.append(strokes(D.nid(), d, (-20, y0 - bowl, 620, y1), [mix(pal_dry[0], "#FFFFFF", 0.2), mix(pal_dry[2], "#C8D8E0", haze)], seed + i, n=int(30 + depth * 50),
                               angle=-90, length=(3 + depth * 6, 6 + depth * 10), width=(0.8, 1.6 + depth), opacity=(0.3, 0.7), curve=0.1))
        # mud / stone wall face below the lip
        wall_h = 4 + depth * 13
        wall = smooth_open(bot_c) + " L " + " L ".join(f"{x:.1f} {y - wall_h:.1f}" for x, y in bot_c[::-1]) + " Z"
        out.append(f'<path d="{wall}" fill="{mix("#6E6A3A", "#B8C8D0", haze)}" opacity="0.8"/>')
        out.append(ink(smooth_open([(x, y - wall_h) for x, y in bot_c]), mix("#E8F0B0", "#E8F0F4", haze), 1.2, seed + i, 1, 0.45))
    return "".join(out), ys


def ifugao_hut(D, x, base, s, seed, haze=0.0):
    """Ifugao house (bale): a steep pyramid thatch roof on four posts, with the rat guards on the posts."""
    hz = (lambda c: mix(c, "#C8D8E0", haze)) if haze else (lambda c: c)
    out = []
    for dx in (-14, 14):
        out.append(taper([(x + dx * s, base), (x + dx * s, base - 22 * s)], 3 * s, 3 * s, hz("#4A3420")))
        out.append(f'<ellipse cx="{x + dx * s:.1f}" cy="{base - 14 * s:.1f}" rx="{4 * s:.1f}" ry="{2 * s:.1f}" fill="{hz("#6A5038")}"/>')
    out.append(painted(D, rect_pts(x - 18 * s, base - 34 * s, x + 18 * s, base - 22 * s, 8, seed, 0.3), (hz("#9A7A5A"), hz("#6A4A2E"), hz("#3A2614")), seed, sk=0.2, n=3, inkw=1, hi=0.3))
    roof = [(x - 28 * s, base - 30 * s), (x, base - 74 * s), (x + 28 * s, base - 30 * s), (x, base - 26 * s)]
    out.append(painted(D, densify(roof, 6), (hz("#D8B880"), hz("#A8844A"), hz("#5A4220")), seed + 1, sdir=(0.9, 0.3), sk=0.2, angle=-60, n=10, inkw=1.2, hi=0.35))
    return "".join(out)


@design("banaue")
def banaue():
    D = Doc2("ph-ba")
    out = [sky(D, [(0, "#8AB8E0"), (0.5, "#D8E8F0"), (1, "#F8F0E0")], 1901, 600, ["#A8C8E8", "#FFFFFF"], 60, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 200, 200, "#FFF4D0", 0.7))
    # far mountains, layered blue
    for k, (pts, pal) in enumerate((([(-20, 250), (80, 196), (170, 222), (260, 180), (360, 214), (460, 176), (620, 230)], ("#B8C8E0", "#9AAED0", "#7A90B8")),
                                    ([(-20, 270), (100, 236), (200, 258), (330, 226), (440, 250), (620, 236)], ("#9AB0C8", "#7A98B4", "#5A7898")))):
        out.append(hill(D, ridge(pts, 1902 + k, 6, 3), 400, pal, 1904 + k, inkw=0))
    out.append(dab_crown(D, 60, 286, 120, 30, [("#7A9A8A", "#5A7A6A", "#3A5A4A")], 1906, n=60, size=(5, 9), inkw=0))
    out.append(dab_crown(D, 540, 280, 120, 30, [("#7A9A8A", "#5A7A6A", "#3A5A4A")], 1907, n=60, size=(5, 9), inkw=0))
    tr, ys = terraces(D, 1908, 336, 720, n=12, bowl=96, spur=56, spur_x=420, flooded=(1, 4))
    out.append(tr)
    # mist drifting across the upper terraces
    for k, (y, op) in enumerate(((290, 0.6), (330, 0.4))):
        out.append(f'<path d="{blob(300 + (k - 0.5) * 120, y, 360, 18, 1909 + k, 0.2, 16)}" fill="#FFFFFF" opacity="{op}"/>')
    # huts on a terrace, a farmer with a carabao, an egret
    for k, (x, b, s_) in enumerate(((150, 344, 0.7), (186, 348, 0.8), (446, 340, 0.75))):
        out.append(ifugao_hut(D, x, b, s_, 1910 + k, haze=0.3))
    out.append(figures.person(268, 470, 30, "walk", 1, {"top": "#C8302A", "bottom": "#2A2A3A", "hat_kind": "sunhat", "hat": "#D8B870", "skin": "#B8784A"}, seed=1914))
    out.append(carabao(D, 330, 476, 0.42, 1915))
    out.append(egret(D, 412, 540, 0.8, 1916))
    # lettering
    out.append(letters(D, 300, 130, "Banaue", DMS, 120, "#2E5A2A", ["#3E7A3A", "#1A3A1A", "#5A9A4A"], 1920, max_w=380,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8E8B0"))
    out.append(ruled(300, 170, "HAGDAN-HAGDANG PALAYAN · IFUGAO", "#5A4A2A", font=JOS, size=17, ls=4, line_w=18, gap=10, max_w=420))
    return finish_b(D, out, 1921)


def carabao(D, cx, base, s, seed, flip=1, pal=("#8A8490", "#4E4854", "#22202A")):
    """Water buffalo (kalabaw) in side view: heavy grey body, sweeping crescent horns, head held low."""
    P = lambda x, y: (cx + x * s * flip, base + y * s)
    out = [cast(D, cx, base + 4 * s, 130 * s, 10 * s, strength=0.4, seed=seed)]
    legs = [(-80, 0), (-50, 0), (58, 0), (84, 0)]
    for k, (lx, _) in enumerate(legs):
        dark = k in (1, 2)
        c = pal[2] if dark else pal[1]
        out.append(taper([P(lx, -60), P(lx + 2, -24), P(lx, 0)], 18 * s, 12 * s, c))
        out.append(f'<path d="{blob(*P(lx, 2), 8 * s, 4 * s, seed + k, 0.1, 8)}" fill="#1A1820"/>')
    body = [P(-118, -96), P(-60, -126), P(30, -130), P(96, -118), P(118, -86), P(110, -52), P(60, -44), P(-30, -46), P(-104, -52), P(-124, -74)]
    out.append(painted(D, body, pal, seed, sdir=(0.3, 1), sk=0.2, angle=-10, n=30, inkw=2, inkc="#14121A", hi=0.35))
    out.append(taper([P(-112, -86), P(-128, -60), P(-126, -30)], 4 * s, 2 * s, pal[2]))
    head = [P(100, -112), P(140, -116), P(170, -96), P(184, -64), P(176, -50), P(150, -56), P(118, -76)]
    out.append(painted(D, head, pal, seed + 1, sdir=(0.3, 1), sk=0.2, n=10, inkw=1.8, inkc="#14121A", hi=0.35))
    horn = [P(136, -114), P(110, -132), P(84, -136), P(70, -126), P(90, -126), P(112, -118), P(128, -104)]
    out.append(painted(D, horn, ("#D8D0C0", "#A89A88", "#5A5048"), seed + 2, sk=0.2, n=6, inkw=1.4, hi=0.5))
    out.append(f'<circle cx="{P(160, -86)[0]:.1f}" cy="{P(160, -86)[1]:.1f}" r="{3 * s:.1f}" fill="#0A0A10"/>')
    out.append(pline([P(-60, -120), P(20, -126), P(90, -114)], "#B8B0C0", 3 * s, seed, 0.5, 1))
    return "".join(out)


def egret(D, x, base, s, seed):
    """Cattle egret: small white heron with a yellow bill, standing on long dark legs."""
    P = lambda a, b: (x + a * s, base + b * s)
    out = [pline([P(-4, -30), P(-6, 0)], "#3A3A30", 1.8 * s, seed, 1, 1), pline([P(4, -30), P(6, 0)], "#3A3A30", 1.8 * s, seed + 1, 1, 1)]
    body = [P(-22, -44), P(-6, -56), P(14, -52), P(22, -40), P(10, -28), P(-12, -28)]
    out.append(painted(D, body, ("#FFFFFF", "#F2F0EA", "#B8B4A8"), seed, sk=0.2, n=4, inkw=1.2, hi=0.4))
    out.append(taper([P(14, -50), P(22, -64), P(24, -76)], 7 * s, 5 * s, "#F6F4EE"))
    out.append(f'<path d="{blob(*P(26, -78), 6 * s, 5 * s, seed + 2, 0.05, 8)}" fill="#F6F4EE" stroke="#B8B4A8" stroke-width="1"/>')
    out.append(f'<path d="{pd([P(30, -80), P(44, -77), P(30, -75)])}" fill="#F2C24A"/>')
    out.append(f'<circle cx="{P(28, -79)[0]:.1f}" cy="{P(28, -79)[1]:.1f}" r="1.3" fill="#1A1A10"/>')
    return "".join(out)


# ================================================================ 22. el nido — limestone cliffs, a lagoon, bangkas on turquoise
def karst(D, pts, seed, pal=("#B8B8A8", "#8A8C80", "#4A4E48"), haze=0.0, veg=True):
    """A limestone karst island: jagged grey cliff with vertical streaks, ledges of jungle green on top and in cracks."""
    hz = (lambda c: mix(c, "#B8D8E0", haze)) if haze else (lambda c: c)
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    out = [f'<path d="{d}" fill="{hz(pal[1])}"/>']
    rnd = random.Random(seed)
    inner = [f'<path d="{d}" fill="{D.lin([(0, hz(pal[0]), 0.6), (0.55, hz(pal[1]), 0), (1, hz(pal[2]), 0.6)], 0, 0, 1, 0)}"/>']
    for _ in range(int((x1 - x0) / 3)):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1 - 20)
        L = rnd.uniform(20, 80)
        inner.append(taper([(x, y), (x + rnd.uniform(-4, 4), y + L)], rnd.uniform(1.5, 4), 0.6, hz(rnd.choice([pal[2], pal[0], "#6A6A5E"])), rnd.uniform(0.3, 0.6)))
    if veg:
        for _ in range(int((x1 - x0) / 5)):
            x = rnd.uniform(x0, x1)
            y = rnd.uniform(y0, y1 - 30)
            inner.append(f'<path d="{blob(x, y, rnd.uniform(5, 14), rnd.uniform(3, 8), rnd.randint(0, 999), 0.3, 8)}" fill="{hz(rnd.choice(["#3E7A3A", "#5A9A4A", "#2A5A2A"]))}" opacity="0.9"/>')
    out.append(clipped(D, d, inner))
    if veg:
        top = sorted(pts, key=lambda p: p[1])[: max(3, len(pts) // 3)]
        for x, y in top:
            out.append(dab_crown(D, x, y + 4, rnd.uniform(14, 26), rnd.uniform(6, 10), [(hz("#7AB05A"), hz("#3E7A3A"), hz("#1E4A22"))], rnd.randint(0, 999), n=14, size=(3, 6), inkw=0, base=False))
    out.append(ink(d, hz("#2A2E28"), 1.2, seed, 1, 0.45))
    return "".join(out)


@design("el-nido")
def el_nido():
    D = Doc2("ph-en")
    out = [sky(D, [(0, "#4AA0E0"), (0.6, "#9AD4F0"), (1, "#E0F4F8")], 2001, 380, ["#6AB4EA", "#E8F8FF"], 50, angle=-3, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 470, 236, 160, 2002, pal=("#FFFFFF", "#F4FAFF", "#C8DCF0")))
    out.append(puff_cloud(D, 120, 270, 110, 2003, pal=("#FFFFFF", "#F4FAFF", "#C8DCF0"), op=0.85))
    # distant karst islets in haze
    out.append(karst(D, [(200, 352), (214, 300), (236, 284), (256, 300), (270, 352)], 2004, haze=0.55, veg=False))
    out.append(karst(D, [(330, 352), (344, 316), (366, 302), (392, 320), (404, 352)], 2005, haze=0.5, veg=False))
    # lagoon water
    wp = "M -10 350 L 610 350 L 610 610 L -10 610 Z"
    out.append(f'<path d="{wp}" fill="{D.lin([(0, "#2E8AB8"), (0.35, "#2EB8C0"), (0.7, "#6AD8C8"), (1, "#C8F0D8")], 0, 350, 0, 600, "userSpaceOnUse")}"/>')
    out.append(strokes(D.nid(), wp, (-40, 350, 600, 600), ["#FFFFFF", "#1E7AA8", "#8AE8E0"], 2006, n=80, angle=0, length=(30, 100), width=(1.5, 4), opacity=(0.12, 0.35)))
    # sand showing through shallows, then the beach
    out.append(f'<path d="{blob(300, 590, 380, 70, 2007, 0.1, 18)}" fill="#E8F0C8" opacity="0.55"/>')
    sand = "M -10 560 Q 150 540 300 548 T 610 544 L 610 610 L -10 610 Z"
    out.append(f'<path d="{sand}" fill="#F6EAC8"/>')
    out.append(strokes(D.nid(), sand, (-40, 540, 600, 610), ["#FFFFFF", "#D8C8A0"], 2008, n=30, angle=0, length=(20, 60), width=(2, 4), opacity=(0.2, 0.4)))
    out.append(pline([(-10, 560), (150, 541), (300, 549), (450, 551), (610, 544)], "#FFFFFF", 3, 2009, 0.8, 1))
    # the big cliffs on both sides
    left = [(-30, 360), (-20, 180), (20, 140), (44, 168), (70, 120), (104, 150), (130, 240), (150, 300), (176, 362)]
    out.append(karst(D, left, 2010))
    right = [(420, 364), (440, 290), (468, 220), (500, 196), (522, 150), (552, 170), (590, 130), (630, 160), (630, 364)]
    out.append(karst(D, right, 2011))
    # reflections of the cliffs
    for pts, sd in ((left, 2012), (right, 2013)):
        refl = [(x, 360 + (360 - y) * 0.35) for x, y in pts]
        out.append(f'<path d="{smooth_closed(refl)}" fill="#1E5A6A" opacity="0.25"/>')
    # bangkas moored on the turquoise water
    out.append(bangka(D, 300, 430, 0.62, 2014, hull=("#FFFFFF", "#F2EEE6", "#A8A49C"), stripe=("#6AC8C0", "#1E8A86", "#0C4A4A"), trim=PULA, boatman=False))
    out.append(bangka(D, 180, 486, 0.5, 2015, stripe=("#F2766A", "#CE2A2A", "#7A0E10"), trim=ARAW, boatman=False))
    out.append(seagull(240, 210, 10, "#3A4A5A") if False else bird_v(240, 210, 9, "#3A4A5A") + bird_v(262, 222, 6, "#3A4A5A"))
    # lettering
    out.append(letters(D, 300, 130, "El Nido", DMS, 112, "#FFFFFF", ["#FFFFFF", "#E8F8FF", "#D8F0FF"], 2020, max_w=380,
                       shadow="#1E5A8A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 166, "PALAWAN", "#FFF6C8", font=JOS, size=22, ls=12, line_w=40, gap=14))
    return finish_b(D, out, 2021, "#1A3A4A", 0.5)


# ================================================================ 23. sari-sari store — the little corner shop window
def candy_jar(D, cx, base, w, h, seed, fill_cols, lid=PULA):
    """Round-shouldered glass jar of sweets with a coloured screw lid."""
    top = base - h
    pts = densify([(cx - w * 0.3, top + 6), (cx - w / 2, top + h * 0.22), (cx - w / 2, base - 6), (cx - w * 0.44, base), (cx + w * 0.44, base),
                   (cx + w / 2, base - 6), (cx + w / 2, top + h * 0.22), (cx + w * 0.3, top + 6)], 8)
    d = smooth_closed(pts)
    rnd = random.Random(seed)
    inner = [f'<path d="{d}" fill="#E8F0F0" opacity="0.5"/>']
    for _ in range(int(w * h / 50)):
        x, y = cx + rnd.uniform(-w, w) * 0.45, rnd.uniform(top + h * 0.3, base - 3)
        c = rnd.choice(fill_cols)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(4, 6), rnd.uniform(3, 4), rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{c}" stroke="{dk(c, 0.3)}" stroke-width="0.6"/>')
    inner.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.5), (0.25, "#FFFFFF", 0), (0.8, "#2A3A4A", 0), (1, "#2A3A4A", 0.25)], 0, 0, 1, 0)}"/>')
    out = [clipped(D, d, inner), ink(d, "#5A6A70", 1.4, seed, 1, 0.7)]
    out.append(taper([(cx - w * 0.36, top + h * 0.3), (cx - w * 0.38, base - 10)], 3, 1, "#FFFFFF", 0.85))
    out.append(painted(D, rect_pts(cx - w * 0.34, top - 4, cx + w * 0.34, top + 8, 8, seed + 1, 0.3), lid, seed + 1, sk=0.2, angle=0, n=4, inkw=1.2, hi=0.45))
    return "".join(out)


def sachet_strip(x, top, n, w, h, seed, col):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        y = top + k * (h + 1)
        sway = math.sin(k * 0.6 + seed) * 1.5
        out.append(f'<path d="{hg.org_rect(x + sway, y, w, h, seed + k, 0.3, 6, 1.5)}" fill="{col}" stroke="{dk(col, 0.35)}" stroke-width="0.8"/>')
        out.append(f'<path d="M {x + sway + 3:.1f} {y + 3:.1f} l {w - 6:.1f} 0" stroke="#FFFFFF" stroke-width="1.6" opacity="0.6"/>')
        out.append(f'<circle cx="{x + sway + w / 2:.1f}" cy="{y + h * 0.6:.1f}" r="{min(w, h) * 0.18:.1f}" fill="{rnd.choice(["#FFFFFF", "#F6C51E", "#2A2A3A"])}" opacity="0.8"/>')
    return "".join(out)


@design("sari-sari-store")
def sari_sari_store():
    D = Doc2("ph-ss")
    # painted mint plywood front
    out = [wall(D, "#9AD8C0", "#6ABCA4", 2101, ["#B8E8D4", "#4A9A84", "#A8E0C8"])]
    for k in range(5):
        out.append(pline([(k * 128 + 30, 0), (k * 128 + 32, 600)], "#3E8A74", 1.6, k, 0.45, 1))
    # corrugated roof eave across the very top
    eave = "M -10 -10 L 610 -10 L 610 40 L -10 40 Z"
    out.append(f'<path d="{eave}" fill="#B8C0C8"/>')
    for k in range(32):
        out.append(f'<path d="M {k * 20 - 6} -10 L {k * 20 - 6} 40" stroke="{["#E8EEF4", "#7A848E"][k % 2]}" stroke-width="6" opacity="0.6"/>')
    out.append(f'<path d="{pd([(-10, 40), (610, 40), (610, 48), (-10, 48)])}" fill="#4A545E" opacity="0.5"/>')
    # hand-painted signboard
    sb = rect_pts(52, 64, 548, 172, 16, 2103, 0.6)
    out.append(cast(D, 306, 176, 250, 10, strength=0.35, seed=2103))
    out.append(painted(D, sb, ("#FFF8E4", "#F6EACC", "#C8B48A"), 2104, sk=0.1, angle=0, n=30, inkw=2, hi=0.3))
    out.append(ink(smooth_closed(rect_pts(62, 74, 538, 162, 16, 2105, 0.6)), "#1E4AA0", 2.4, 2105, 1, 0.8))
    out.append(letters(D, 300, 140, "Sari-Sari Store", DMS, 72, "#C8241E", ["#E0402A", "#8A100A", "#F0603A"], 2106, max_w=440,
                       shadow="#1E4AA0", soff=(0.025, 0.04), angle=-40, hi="#FFB090"))
    for x in (78, 522):
        out.append(f'<circle cx="{x}" cy="118" r="4" fill="#8A8A90" stroke="#3A3A40" stroke-width="1"/>')
    # the window: shelves of everything behind a diamond wire screen
    wx0, wy0, wx1, wy1 = 70, 208, 530, 454
    win = smooth_closed(rect_pts(wx0, wy0, wx1, wy1, 20, 2107, 0.4))
    inside = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="#4A3A30"/>',
              soft_glow(D, 300, 300, 260, "#FFD890", 0.45)]
    for y in (296, 376):
        inside.append(painted(D, rect_pts(wx0, y, wx1, y + 10, 20, y, 0.3), NARRA, y, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1, hi=0.4))
    rnd = random.Random(2108)
    # top shelf: candy jars
    for k, x in enumerate(range(110, 520, 70)):
        cols = [["#E8304A", "#F6C51E", "#FFFFFF"], ["#2EB05A", "#FFFFFF", "#F28A2A"], ["#8A5AD0", "#EE6A98"], ["#F6C51E", "#C8641E"], ["#1E9AD8", "#FFFFFF", "#E8304A"], ["#F28A2A", "#5A3A1A"]][k % 6]
        inside.append(candy_jar(D, x, 296, 54, 70, 2110 + k, cols, lid=[PULA, BUGHAW, ARAW, ("#7AD08A", "#2E9A4E", "#145A2A")][k % 4]))
    # middle shelf: bottles, canned goods, a tray of eggs
    for k in range(6):
        x = 100 + k * 26
        c = rnd.choice(["#3A1A0A", "#E8A030", "#C8302A", "#2E7A3A"])
        inside.append(painted(D, densify([(x - 8, 376), (x - 8, 336), (x - 4, 326), (x - 3, 314), (x + 3, 314), (x + 4, 326), (x + 8, 336), (x + 8, 376)], 6),
                              (lt(c, 0.3), c, dk(c, 0.4)), 2120 + k, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=3, inkw=1, hi=0.5))
        inside.append(f'<rect x="{x - 8:.1f}" y="344" width="16" height="12" fill="#FFFFFF" opacity="0.8"/>')
    for k in range(5):
        x = 290 + k * 24
        c = rnd.choice(["#C8302A", "#1E6AC8", "#F2B21E", "#2E8A4A"])
        inside.append(painted(D, rect_pts(x - 10, 342, x + 10, 376, 6, 2130 + k, 0.3), (lt(c, 0.3), c, dk(c, 0.4)), 2130 + k, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=3, inkw=1, hi=0.4))
        inside.append(f'<path d="M {x - 10:.1f} 346 L {x + 10:.1f} 346 M {x - 10:.1f} 372 L {x + 10:.1f} 372" stroke="#C8CED6" stroke-width="2"/>')
    for k in range(5):
        x = 420 + k * 20
        inside.append(f'<path d="{blob(x, 364, 9, 11, 2140 + k, 0.03, 10)}" fill="#F6E8D0" stroke="#B8A080" stroke-width="1"/>')
    inside.append(f'<path d="{pd([(406, 372), (516, 372), (512, 378), (410, 378)])}" fill="#C8B08A"/>')
    # bottom: loaves of bread in plastic bags, chichirya bags
    for k in range(4):
        x = 110 + k * 50
        inside.append(painted(D, rect_pts(x - 20, 396, x + 20, 446, 8, 2150 + k, 0.6), ("#FFFFFF", "#EEF2F6", "#B8C0C8"), 2150 + k, sk=0.15, n=4, inkw=1, hi=0.5))
        inside.append(f'<path d="{blob(x, 426, 14, 12, 2155 + k, 0.08, 10)}" fill="#E0A858"/>')
    for k in range(4):
        x = 350 + k * 44
        c = ["#E8304A", "#F6C51E", "#1E9AD8", "#2EB05A"][k]
        inside.append(painted(D, densify([(x - 18, 446), (x - 20, 400), (x + 20, 400), (x + 18, 446)], 6), (lt(c, 0.35), c, dk(c, 0.35)), 2160 + k, sk=0.2, n=5, inkw=1.1, hi=0.5))
        inside.append(f'<path d="M {x - 18:.1f} 404 l 4 -4 l 4 4 l 4 -4 l 4 4 l 4 -4 l 4 4 l 4 -4 l 4 4 l 4 -4" stroke="{dk(c, 0.3)}" stroke-width="1.2" fill="none"/>')
        inside.append(f'<circle cx="{x:.1f}" cy="424" r="8" fill="#FFFFFF" opacity="0.75"/>')
    # sachets hanging in strips from the top
    for k, x in enumerate((84, 150, 446, 500)):
        inside.append(sachet_strip(x, 212, 5, 22, 14, 2170 + k, ["#E8304A", "#1E9AD8", "#F6C51E", "#2EB05A"][k]))
    out.append(clipped(D, win, inside))
    # diamond wire screen and the serving hole
    mesh = []
    for k in range(-20, 40):
        x = wx0 + k * 18
        mesh.append(f'<path d="M {x} {wy0} L {x + (wy1 - wy0)} {wy1}" stroke="#3A3A44" stroke-width="1.4" opacity="0.55"/>')
        mesh.append(f'<path d="M {x} {wy1} L {x + (wy1 - wy0)} {wy0}" stroke="#3A3A44" stroke-width="1.4" opacity="0.55"/>')
    hole = f"M 242 404 L 358 404 L 358 454 L 242 454 Z"
    out.append(f'<g {D.clip(f"<path d=\"{win}\"/>")}><g {D.clip(f"<path d=\"M 0 0 L 600 0 L 600 600 L 0 600 Z {hole}\" clip-rule=\"evenodd\"/>")}>{"".join(mesh)}</g></g>')
    out.append(ink(hole, "#3A2414", 2.2, 2180, 1, 0.8))
    out.append(painted(D, rect_pts(wx0 - 14, wy0 - 14, wx1 + 14, wy0, 16, 2181, 0.4), NARRA, 2181, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    for x in (wx0 - 14, wx1):
        out.append(painted(D, rect_pts(x, wy0 - 14, x + 14, wy1 + 4, 16, 2182 + x, 0.4), NARRA, 2182 + x, sdir=(1, 0), sk=0.2, angle=-90, n=14, inkw=1.6, hi=0.4))
    # counter ledge with a candy jar and a little cardboard sign
    out.append(painted(D, rect_pts(40, 454, 560, 476, 20, 2184, 0.5), NARRA, 2184, sdir=(0, 1), sk=0.2, angle=0, n=24, inkw=1.6, hi=0.45))
    out.append(cast(D, 300, 480, 280, 8, strength=0.4, seed=2185))
    out.append(candy_jar(D, 430, 454, 50, 60, 2186, ["#F6C51E", "#E8304A", "#FFFFFF"], lid=BUGHAW))
    sign = rot(rect_pts(110, 392, 214, 448, 10, 2187, 0.6), 162, 420, -6)
    out.append(painted(D, sign, ("#E8C898", "#C89A60", "#7A5A2E"), 2187, sk=0.1, angle=0, n=8, inkw=1.4, hi=0.3))
    out.append(f'<text x="162" y="430" text-anchor="middle" {BEBAS} font-size="{fit_size("BUKAS PO", BEBAS, 30, 90, 2)}" letter-spacing="2" fill="#C8241E" transform="rotate(-6 162 420)">BUKAS PO</text>')
    out.append(pline([(126, 394), (162, 372), (198, 390)], "#5A4A3A", 1.4, 2188, 0.9, 1))
    # wall below: a bench and plants in old cans
    out.append(painted(D, rect_pts(70, 520, 300, 534, 14, 2189, 0.4), NARRA, 2189, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    for x in (90, 280):
        out.append(taper([(x, 534), (x, 600)], 8, 8, "#4A2410"))
    for k, x in enumerate((420, 480)):
        out.append(painted(D, rect_pts(x - 22, 530, x + 22, 580, 8, 2190 + k, 0.3), STEEL, 2190 + k, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.5))
        out.append(dab_crown(D, x, 520, 34, 24, [("#8AD06A", "#3E9A3A", "#1A5A1E")], 2192 + k, n=40, size=(4, 8), inkw=0))
    out.append(cat_loaf(D, 200, 516, 0.8, 2195))
    out.append(ruled(300, 197, "PABILI PO!", "#FFFFFF", font=JOS, size=19, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 2196)


def cat_loaf(D, cx, base, s, seed, pal=("#F2F0EA", "#D8D0C4", "#8A8070"), patch=("#F2B060", "#D8862E", "#8A4A10")):
    """A calico puspin (Filipino street cat) curled on the bench."""
    P = lambda x, y: (cx + x * s, base + y * s)
    out = [cast(D, cx, base + 2, 40 * s, 5 * s, strength=0.35, seed=seed)]
    body = [P(-40, 0), P(-38, -22), P(-14, -36), P(20, -34), P(40, -16), P(42, 0)]
    out.append(painted(D, body, pal, seed, sk=0.2, n=8, inkw=1.4, hi=0.4))
    out.append(clipped(D, smooth_closed(body), [f'<path d="{blob(*P(-10, -26), 18 * s, 10 * s, seed + 1, 0.2, 10)}" fill="{patch[1]}"/>', f'<path d="{blob(*P(20, -10), 10 * s, 8 * s, seed + 2, 0.2, 10)}" fill="#3A3A3A"/>']))
    head = blob_pts(*P(-34, -24), 16 * s, 14 * s, seed + 3, 0.05, 12)
    out.append(painted(D, head, pal, seed + 3, sk=0.2, n=4, inkw=1.4, hi=0.4))
    for sg in (-1, 1):
        ex = -34 + sg * 9
        out.append(f'<path d="{pd([P(ex - 5, -34), P(ex + sg * 2, -46), P(ex + 5, -34)])}" fill="{patch[1] if sg < 0 else pal[1]}" stroke="{INK}" stroke-width="1"/>')
        out.append(pline([P(-34 + sg * 6 - 3, -24), P(-34 + sg * 6, -22), P(-34 + sg * 6 + 3, -24)], INK, 1.4, seed + sg, 0.9, 1))
    out.append(taper([P(40, -6), P(30, 4), P(0, 6), P(-20, 4)], 7 * s, 4 * s, patch[1]))
    return "".join(out)


# ================================================================ 24. tarsier — a field-guide card from Bohol
def tarsier_d(D, cx, cy, s, seed, fur=("#C8B098", "#9A8068", "#5A4634")):
    """Philippine tarsier clinging to an upright branch: huge amber eyes, thin bat-like ears, long fingers with pads."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    out = []
    # long thin tail hanging down along the branch
    out.append(taper([P(10, 70), P(22, 140), P(18, 210), P(24, 260)], 6 * s, 3 * s, fur[1]))
    out.append(f'<path d="{blob(*P(24, 268), 7 * s, 14 * s, seed, 0.2, 10)}" fill="{fur[1]}"/>')
    # hind legs: long, frog-like, gripping
    for sg in (-1, 1):
        leg = [P(sg * 20, 40), P(sg * 44, 54), P(sg * 50, 86), P(sg * 30, 100), P(sg * 12, 80)]
        out.append(painted(D, leg, fur, seed + 1 + sg, sk=0.2, n=10, inkw=1.4, hi=0.35))
        for j in range(3):
            out.append(taper([P(sg * 30, 98), P(sg * (16 - j * 4), 104 + j * 6)], 4 * s, 3 * s, fur[1]))
            out.append(f'<circle cx="{P(sg * (16 - j * 4), 104 + j * 6)[0]:.1f}" cy="{P(sg * (16 - j * 4), 104 + j * 6)[1]:.1f}" r="{3.4 * s:.1f}" fill="{fur[0]}" stroke="{fur[2]}" stroke-width="0.8"/>')
    # body
    body = blob_pts(*P(0, 30), 36 * s, 50 * s, seed + 3, 0.05, 16)
    out.append(painted(D, body, fur, seed + 3, sdir=(0.6, 0.8), sk=0.2, angle=-90, n=30, sw=(0.8, 2), inkw=1.6, hi=0.4))
    rnd = random.Random(seed)
    fz = []
    for _ in range(70):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = P(math.cos(a) * 32 * r, 30 + math.sin(a) * 46 * r)
        t = rnd.uniform(-1.9, -1.2)
        fz.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(t) * 5 * s:.1f} {math.sin(t) * 5 * s:.1f}" stroke="{rnd.choice([fur[0], fur[2]])}" stroke-width="1" opacity="0.6"/>')
    out.append(clipped(D, smooth_closed(body), fz))
    # arms reaching to the branch, long fingers with round pads
    for sg in (-1, 1):
        arm = [P(sg * 22, 4), P(sg * 40, -6), P(sg * 46, 6), P(sg * 30, 20)]
        out.append(painted(D, arm, fur, seed + 5 + sg, sk=0.2, n=6, inkw=1.2, hi=0.35))
        for j in range(4):
            fx, fy = P(sg * (38 - j * 4), -10 + j * 6)
            tx, ty = P(sg * (24 - j * 2), -16 + j * 8)
            out.append(taper([(fx, fy), (tx, ty)], 3.4 * s, 2.4 * s, fur[1]))
            out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{3.2 * s:.1f}" fill="{fur[0]}" stroke="{fur[2]}" stroke-width="0.8"/>')
    # head
    head = blob_pts(*P(0, -50), 46 * s, 40 * s, seed + 8, 0.03, 18)
    for sg in (-1, 1):
        ear = [P(sg * 26, -76), P(sg * 44, -108), P(sg * 62, -100), P(sg * 52, -70), P(sg * 38, -64)]
        out.append(painted(D, ear, ("#E8C8B8", "#C8A090", "#7A5A4A"), seed + 9 + sg, sk=0.2, n=6, inkw=1.3, hi=0.4))
        out.append(f'<path d="{smooth_closed([P(sg * 32, -76), P(sg * 44, -98), P(sg * 54, -94), P(sg * 46, -74)])}" fill="#F2B8B0" opacity="0.6"/>')
    out.append(painted(D, head, fur, seed + 8, sdir=(0.6, 0.8), sk=0.15, angle=-60, n=24, inkw=1.8, hi=0.45))
    # the eyes: huge discs with amber irises
    for sg in (-1, 1):
        ex, ey = P(sg * 19, -54)
        r = 17 * s
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r + 3 * s:.1f}" fill="{fur[2]}" opacity="0.6"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r:.1f}" fill="{D.rad([(0, "#FFE08A"), (0.55, "#E8A030"), (1, "#8A4A10")], 0.45, 0.45, 0.6)}" stroke="#2A1A0A" stroke-width="1.6"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r * 0.6:.1f}" fill="#120A04"/>')
        out.append(f'<circle cx="{ex - r * 0.3:.1f}" cy="{ey - r * 0.32:.1f}" r="{r * 0.22:.1f}" fill="#FFFFFF"/>')
        out.append(f'<circle cx="{ex + r * 0.25:.1f}" cy="{ey + r * 0.2:.1f}" r="{r * 0.08:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(f'<path d="{blob(*P(0, -32), 4 * s, 3 * s, seed + 12, 0.1, 8)}" fill="#5A3A2A"/>')
    out.append(pline([P(-6, -24), P(0, -22), P(6, -24)], "#4A2A1A", 1.4, seed, 0.8, 1))
    return "".join(out)


@design("tarsier")
def tarsier():
    D = Doc2("ph-ts")
    out = [paper(D.nid(), "#F6EEDC", FLECK, 2201)]
    # card frame
    out.append(ink(smooth_closed(rect_pts(56, 56, 544, 544, 20, 2202, 0.4)), "#2E5A3A", 2.4, 2202, 1, 0.85))
    out.append(ink(smooth_closed(rect_pts(66, 66, 534, 534, 20, 2203, 0.4)), "#2E5A3A", 1.2, 2203, 1, 0.7))
    out.append(ruled(300, 98, "BOHOL · PILIPINAS · Nº 3", "#2E5A3A", font=JOS, size=15, ls=4, line_w=40, gap=12))
    # an oval vignette of jungle behind
    vd = ellipse_d(300, 282, 190, 160, 40)
    v = [f'<path d="{vd}" fill="{D.lin([(0, "#CDE4C0"), (1, "#8AB880")])}"/>',
         dab_crown(D, 300, 420, 260, 80, [("#7AB05A", "#3E7A3A", "#1E4A22")], 2204, n=120, size=(8, 16), inkw=0),
         dab_crown(D, 120, 220, 90, 120, [("#9AC878", "#5A9A4A", "#2E5A2A")], 2205, n=80, size=(8, 14), inkw=0),
         dab_crown(D, 480, 240, 90, 120, [("#9AC878", "#5A9A4A", "#2E5A2A")], 2206, n=80, size=(8, 14), inkw=0),
         soft_glow(D, 300, 260, 180, "#FFFBE0", 0.6)]
    # the upright branch the tarsier clings to
    br = [(352, 520), (340, 420), (346, 320), (336, 200), (346, 100)]
    v.append(taper(br, 26, 18, "#7A5A3E"))
    v.append(taper([(x - 6, y) for x, y in br], 6, 4, "#B8946A", 0.8))
    v.append(taper([(x + 7, y) for x, y in br], 5, 3, "#3E2A1A", 0.6))
    v.append(leaf_simple(D, 346, 190, 70, 18, -30, ("#9AD07A", "#4E9A3A", "#1E5A1E"), 2208, inkw=1.2))
    v.append(leaf_simple(D, 340, 236, 60, 16, -150, ("#9AD07A", "#4E9A3A", "#1E5A1E"), 2209, inkw=1.2))
    v.append(leaf_simple(D, 348, 400, 64, 16, 20, ("#9AD07A", "#4E9A3A", "#1E5A1E"), 2210, inkw=1.2))
    v.append(tarsier_d(D, 314, 282, 1.08, 2211))
    out.append(clipped(D, vd, v))
    out.append(ink(vd, "#2E5A3A", 1.8, 2207, 1, 0.7))
    # lettering at the foot of the card
    out.append(letters(D, 300, 498, "tarsier", SERIF_IT, 76, "#2E5A3A", ["#3E7A4A", "#1A3A22", "#5A9A62"], 2220, max_w=300,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8E8C0"))
    out.append(label(300, 526, "CARLITO SYRICHTA", CINZEL, 16, "#7A5A3A", ls=3))
    return finish_b(D, out, 2221)


# ================================================================ 25. isa pang kanta! — family karaoke night
def microphone(D, x, y, L, ang, seed, body=("#5A5E6A", "#2A2E38", "#0E1016"), cord=True):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    hx, hy = x + ux * L, y + uy * L
    handle = [(x + nx * 6, y + ny * 6), (hx + nx * 9, hy + ny * 9), (hx - nx * 9, hy - ny * 9), (x - nx * 6, y - ny * 6)]
    out = [painted(D, densify(handle, 8), body, seed, sdir=(nx, ny), sk=0.25, angle=ang, n=6, inkw=1.4, hi=0.5)]
    gx, gy = hx + ux * 16, hy + uy * 16
    out.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="19" fill="{D.rad([(0, "#F4F6F8"), (0.6, "#A8B0BC"), (1, "#5A6270")], 0.35, 0.35, 0.7)}" stroke="#2A2E38" stroke-width="1.6"/>')
    mesh = []
    for k in range(-3, 4):
        mesh.append(f'<path d="M {gx - 18:.1f} {gy + k * 5:.1f} L {gx + 18:.1f} {gy + k * 5:.1f} M {gx + k * 5:.1f} {gy - 18:.1f} L {gx + k * 5:.1f} {gy + 18:.1f}" stroke="#5A6270" stroke-width="0.8" opacity="0.6"/>')
    out.append(clipped(D, f"M {gx - 19:.1f} {gy:.1f} a 19 19 0 1 0 38 0 a 19 19 0 1 0 -38 0", mesh))
    out.append(f'<circle cx="{gx - 6:.1f}" cy="{gy - 7:.1f}" r="5" fill="#FFFFFF" opacity="0.8"/>')
    out.append(taper([(hx + nx * 9, hy + ny * 9), (hx - nx * 9, hy - ny * 9)], 4, 4, "#C8CED6"))
    if cord:
        out.append(pline([(x, y), (x - ux * 30 + nx * 20, y - uy * 30 + ny * 20), (x - ux * 60 - nx * 10, y - uy * 60 + 40)], "#1A1A22", 2.4, seed, 0.9, 1))
    return "".join(out)


@design("isa-pang-kanta")
def isa_pang_kanta():
    D = Doc2("ph-ka")
    out = [wall(D, "#3A2A5A", "#22183A", 2301, ["#4A3A6A", "#1A1030", "#5A3A7A"])]
    # disco glow blobs
    for k, (x, y, c) in enumerate(((100, 250, "#FF5AA8"), (500, 230, "#5AC8FF"), (300, 200, "#FFD84A"), (160, 420, "#7AE08A"), (460, 430, "#B88AFF"))):
        out.append(soft_glow(D, x, y, 160, c, 0.35))
    # string lights across
    lights = []
    for seg, (x0, y0, x1, y1, sag) in enumerate(((-10, 196, 300, 206, 30), (300, 206, 610, 192, 30))):
        ps = [(x0 + (x1 - x0) * t / 20, y0 + (y1 - y0) * t / 20 + sag * 4 * (t / 20) * (1 - t / 20)) for t in range(21)]
        lights.append(pline(ps, "#0A0A14", 1.6, seg, 0.9, 1))
        for i in range(1, 20, 2):
            x, y = ps[i]
            c = ["#FF5A5A", "#FFD84A", "#5AE08A", "#5AB0FF", "#FF8AD8"][(i // 2 + seg) % 5]
            lights.append(soft_glow(D, x, y + 6, 12, c, 0.6))
            lights.append(f'<ellipse cx="{x:.1f}" cy="{y + 6:.1f}" rx="3.4" ry="5" fill="{c}"/>')
    out.append("".join(lights))
    # floor
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#5A3A2A"), (1, "#2A1A12")])}"/>')
    # cabinet with the karaoke screen
    out.append(painted(D, rect_pts(110, 404, 490, 474, 16, 2302, 0.5), NARRA, 2302, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
    for x in (230, 370):
        out.append(pline([(x, 410), (x, 468)], "#2A1006", 1.6, x, 0.7, 1))
        out.append(f'<circle cx="{x - 14}" cy="440" r="3" fill="#E8C070"/><circle cx="{x + 14}" cy="440" r="3" fill="#E8C070"/>')
    out.append(cast(D, 300, 404, 190, 8, strength=0.5, seed=2303))
    scr = rect_pts(150, 232, 450, 400, 16, 2304, 0.3)
    out.append(painted(D, rect_pts(140, 222, 460, 404, 16, 2305, 0.3), ("#4A4A54", "#24242C", "#0A0A10"), 2305, sk=0.1, angle=0, n=10, inkw=1.6, hi=0.3))
    sd = smooth_closed(scr)
    rnd = random.Random(2306)
    sc = [f'<path d="{sd}" fill="{D.lin([(0, "#3A8AD8"), (0.5, "#6A5AC8"), (1, "#C84A9A")], 0, 0, 1, 1)}"/>',
          f'<path d="{blob(220, 300, 80, 50, 2307, 0.2, 12)}" fill="#FFFFFF" opacity="0.1"/>',
          f'<path d="{blob(390, 260, 60, 40, 2308, 0.2, 12)}" fill="#FFE8A0" opacity="0.15"/>']
    for k in range(9):
        sc.append(f'<circle cx="{rnd.uniform(160, 440):.1f}" cy="{rnd.uniform(240, 300):.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    # score badge (no lyrics, just the famous perfect score)
    sc.append(f'<text x="300" y="352" text-anchor="middle" {ANTON} font-size="86" fill="#1A0A3A" opacity="0.4" transform="translate(4 4)">100</text>')
    sc.append(f'<text x="300" y="352" text-anchor="middle" {ANTON} font-size="86" fill="#FFE04A">100</text>')
    sc.append(f'<text x="300" y="380" text-anchor="middle" {JOS} font-size="15" letter-spacing="4" fill="#FFFFFF">PERFECT!</text>')
    out.append(clipped(D, sd, sc))
    out.append(taper([(160, 240), (230, 238)], 3, 1, "#FFFFFF", 0.4))
    for x, y, s in ((200, 300, 8), (412, 316, 10), (380, 250, 6)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.9))
    # speakers either side
    for k, x in enumerate((58, 472)):
        out.append(painted(D, rect_pts(x, 300, x + 70, 474, 14, 2310 + k, 0.4), ("#4A4A54", "#24242C", "#0A0A10"), 2310 + k, sk=0.15, angle=-90, n=10, inkw=1.6, hi=0.3))
        for cy_, r in ((340, 18), (414, 26)):
            out.append(f'<circle cx="{x + 35}" cy="{cy_}" r="{r}" fill="#14141A" stroke="#5A5A64" stroke-width="2"/><circle cx="{x + 35}" cy="{cy_}" r="{r * 0.35:.1f}" fill="#3A3A44"/>')
        for j in range(3):
            out.append(f'<path d="M {x + (78 if k else -8) + (j * 8 if k else -j * 8):.1f} {370 - j * 10:.1f} q {6 if k else -6} 20 0 40" stroke="#FFD84A" stroke-width="2" fill="none" opacity="{0.8 - j * 0.2:.1f}"/>')
    # music notes floating up
    for k, (x, y, c) in enumerate(((120, 280, "#FF8AD8"), (480, 270, "#5AE0FF"), (520, 330, "#FFD84A"), (86, 360, "#7AE08A"))):
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="7" ry="5" fill="{c}" transform="rotate(-20 {x} {y})"/><path d="M {x + 6:.1f} {y - 2:.1f} l 0 -26 q 8 4 12 12" stroke="{c}" stroke-width="2.4" fill="none"/>')
    # two mics on the floor rug, ready for the next singer
    rug = ellipse_d(300, 540, 240, 44)
    out.append(banig(D, rug, 2320, cell=9, base="#E0C890", bands=("#E8508A", "#2E9A7A", "#F2B21E", "#6A4AB0"), rot_=45))
    out.append(ink(rug, INK, 1.4, 2321, 1, 0.5))
    out.append(microphone(D, 210, 540, 70, -20, 2322))
    out.append(microphone(D, 400, 548, 70, -160, 2323, body=("#F28AB0", "#D8407A", "#7A1A3A")))
    # lettering
    out.append(letters(D, 300, 128, "Isa pang kanta!", SERIF_IT, 96, "#FFE6F2", ["#FFFFFF", "#FFC8E0", "#FFE0F0"], 2330, max_w=470,
                       shadow="#120A2A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "FAMILY KARAOKE NIGHT", "#FFD84A", font=JOS, size=19, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 2331, "#0A0A1A", 0.6)


# ================================================================ 26. nanay — ilaw ng tahanan: the capiz lamp, and food kept warm for you
def capiz_lamp(D, cx, top, R, seed):
    """Hanging capiz-shell chandelier: strands of overlapping translucent shell discs falling from a ring in a bell
    shape around a glowing bulb."""
    out = [pline([(cx, -10), (cx, top)], "#3A2A1A", 2, seed, 0.9, 1)]
    out.append(soft_glow(D, cx, top + R * 0.9, R * 3.2, "#FFD27A", 0.6))
    rnd = random.Random(seed)
    strands = []
    n = 13
    for j in range(n):
        u = -1 + 2 * j / (n - 1)
        x = cx + u * R
        L = R * (1.7 - 0.55 * u * u)
        depth = math.sqrt(max(0, 1 - u * u))
        strands.append((depth, x, L, u))
    # back strands first (they glow through), then the front row
    for front in (False, True):
        for depth, x, L, u in sorted(strands):
            xx = x if front else cx - (x - cx) * 0.86
            yy0 = top + (6 if front else 2)
            k = 0
            y = yy0
            while y < top + L:
                r = R * 0.12
                c = mix("#FFF6E0", rnd.choice(["#F2D8C8", "#E8E0F0", "#FFE8C0"]), rnd.uniform(0.2, 0.6))
                if not front:
                    c = mix(c, "#FFC870", 0.35)
                out.append(f'<path d="{blob(xx, y, r, r * 1.05, seed + int(x) + k, 0.06, 10)}" fill="{c}" opacity="{0.95 if front else 0.75}" stroke="#C8A878" stroke-width="0.8"/>')
                if front:
                    out.append(f'<path d="M {xx - r * 0.45:.1f} {y + r * 0.2:.1f} q {r * 0.4:.1f} {-r * 0.7:.1f} {r * 0.85:.1f} {-r * 0.45:.1f}" stroke="#FFFFFF" stroke-width="1" fill="none" opacity="0.75"/>')
                y += r * 1.35
                k += 1
        if not front:
            out.append(soft_glow(D, cx, top + R * 0.9, R * 1.1, "#FFF6D0", 0.85))
    out.append(f'<path d="{ellipse_d(cx, top + 3, R + 4, 7)}" fill="#8A6A3A" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<path d="{ellipse_d(cx, top, R * 0.3, 5)}" fill="#6A4A2A"/>')
    return "".join(out)


def food_cover(D, cx, base, R, seed, col=("#FFB8D0", "#EE6A98", "#A82A5A")):
    """The folding mesh food cover (takip) every Filipino kitchen has, keeping a plate warm for whoever comes home late."""
    out = [cast(D, cx + 8, base + 2, R * 1.05, R * 0.16, strength=0.45, seed=seed)]
    dome = ell_pts(cx, base, R, R * 0.78, 180, 360, 24)
    d = smooth_closed(dome + [(cx + R, base + 2), (cx - R, base + 2)])
    mesh = [f'<path d="{d}" fill="{col[0]}" opacity="0.45"/>']
    for k in range(-14, 15):
        mesh.append(f'<path d="M {cx + k * 8:.1f} {base - R} L {cx + k * 8 + R * 0.4:.1f} {base}" stroke="{col[1]}" stroke-width="0.9" opacity="0.6"/>')
        mesh.append(f'<path d="M {cx + k * 8:.1f} {base - R} L {cx + k * 8 - R * 0.4:.1f} {base}" stroke="{col[1]}" stroke-width="0.9" opacity="0.6"/>')
    out.append(clipped(D, d, mesh))
    for k in range(7):
        a = math.radians(180 + k * 30)
        out.append(pline(ell_pts(cx, base, R * abs(math.cos(a)) + 0.1, R * 0.78, 180, 360, 14), col[2], 1.8, seed + k, 0.85, 1))
    out.append(pline([(cx - R, base), (cx + R, base)], col[2], 2.4, seed, 0.9, 1))
    out.append(f'<circle cx="{cx}" cy="{base - R * 0.78 - 4:.1f}" r="6" fill="{col[1]}" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


@design("nanay")
def nanay():
    D = Doc2("ph-ny")
    out = [wall(D, "#3A2E4A", "#2A2034", 2401, ["#4A3A5A", "#1E1428", "#5A4A6A"])]
    out.append(capiz_lamp(D, 300, 226, 82, 2402))
    # warm pool of light on the table
    out.append(f'<path d="M -10 420 L 610 420 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#8A5A3A"), (1, "#4A2A16")])}"/>')
    out.append(wood_planks(D, 420, 600, 2403, ("#C8905A", "#8A5432", "#4A2410"), 3))
    out.append(f'<path d="{blob(300, 478, 280, 70, 2404, 0.1, 16)}" fill="#FFD890" opacity="0.28"/>')
    # a crocheted table runner, the covered plate, the rice pot, a glass of water and a note
    out.append(f'<path d="{blob(300, 474, 210, 30, 2405, 0.05, 20)}" fill="#FFFBF2" opacity="0.92"/>')
    for k in range(26):
        x = 100 + k * 16
        out.append(f'<circle cx="{x}" cy="{474 + 26 * math.sin(k * 0.3) * 0:.0f}" r="3" fill="none" stroke="#D8C8A8" stroke-width="1"/>')
    out.append(painted(D, ell_pts(300, 476, 96, 20, 0, 360, 28)[:-1], WHITE, 2406, sk=0.15, angle=0, n=8, inkw=1.4, hi=0.4))
    out.append(pline(ell_pts(300, 476, 84, 16, 0, 360, 28), BUGHAW[1], 1.6, 2407, 0.7, 1))
    out.append(food_cover(D, 300, 474, 86, 2408))
    out.append(rice_bowl_side(D, 120, 442, 44, 50, 2409, glaze=WHITE, band=PULA, mound=0.9))
    gx, gb = 476, 488
    out.append(cast(D, gx + 6, gb, 26, 5, strength=0.4, seed=2410))
    gl = densify([(gx - 20, gb - 70), (gx - 16, gb), (gx + 16, gb), (gx + 20, gb - 70)], 8)
    out.append(f'<path d="{smooth_closed(gl)}" fill="#E8F2F8" opacity="0.55" stroke="#8A9AA8" stroke-width="1.6"/>')
    out.append(f'<path d="{smooth_closed(densify([(gx - 19, gb - 50), (gx - 16, gb - 2), (gx + 16, gb - 2), (gx + 19, gb - 50)], 8))}" fill="#C8E0F0" opacity="0.6"/>')
    out.append(taper([(gx - 12, gb - 64), (gx - 10, gb - 10)], 3, 1, "#FFFFFF", 0.85))
    note = rot(rect_pts(370, 498, 470, 540, 10, 2411, 0.6), 420, 519, -6)
    out.append(painted(D, note, ("#FFFFFF", "#FFF8E0", "#D8C8A0"), 2411, sk=0.1, angle=0, n=4, inkw=1.2, hi=0.3))
    out.append(f'<text x="420" y="525" text-anchor="middle" {SERIF_IT} font-size="{fit_size("Kain ka na, anak", SERIF_IT, 17, 92)}" fill="#3A3A8A" transform="rotate(-6 420 519)">Kain ka na, anak</text>')
    out.append(p_heart(D, 452, 532, 5, PULA, 2412, rot_=-6, inkw=0.6))
    # lettering
    out.append(letters(D, 300, 140, "Nanay", SERIF_IT, 118, "#FFE6C0", ["#FFFFFF", "#FFD8A0", "#FFF0D0"], 2420, max_w=380,
                       shadow="#120A1E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 184, "ILAW NG TAHANAN", "#F6C870", font=JOS, size=21, ls=8, line_w=32, gap=14))
    return finish_b(D, out, 2421, "#0A0A1A", 0.6)


# ================================================================ 27. tatay — haligi ng tahanan: the bahay kubo on its sturdy posts
def sawali(D, d, seed, cell=12, pal=("#F2DCA0", "#D8B870", "#8A6A30")):
    """Sawali: split-bamboo wall panel woven in a herringbone / twill."""
    c = cell
    t = [f'<rect width="{2 * c}" height="{2 * c}" fill="{pal[1]}"/>',
         f'<rect x="0.6" y="0.6" width="{2 * c - 1.2}" height="{c / 2 - 1:.1f}" rx="1.5" fill="{pal[0]}"/>',
         f'<rect x="0.6" y="{c + 0.6}" width="{c / 2 - 1:.1f}" height="{c - 1.2}" rx="1.5" fill="{pal[0]}"/>',
         f'<rect x="{c + 0.6}" y="{c / 2 + 0.6:.1f}" width="{c - 1.2}" height="{c / 2 - 1:.1f}" rx="1.5" fill="{lt(pal[0], 0.2)}"/>',
         f'<path d="M 0 {c} L {2 * c} {c}" stroke="{pal[2]}" stroke-width="0.8" opacity="0.6"/>']
    pat = D.pattern(2 * c, 2 * c, "".join(t), transform="rotate(45)")
    return f'<path d="{d}" fill="{pat}"/>'


def salakot(D, cx, cy, R, seed, ang=0):
    """Salakot: the wide, shallow conical farmer's hat, woven, with a knob at the crown."""
    pts = rot([(cx - R, cy + R * 0.08), (cx - R * 0.6, cy - R * 0.2), (cx, cy - R * 0.5), (cx + R * 0.6, cy - R * 0.2), (cx + R, cy + R * 0.08), (cx, cy + R * 0.18)], cx, cy, ang)
    out = [painted(D, pts, ("#F2D898", "#C8A058", "#7A5A26"), seed, sdir=(0.6, 0.8), sk=0.2, angle=ang, n=16, inkw=1.6, hi=0.45)]
    for k in range(1, 4):
        out.append(pline(rot(ell_pts(cx, cy - R * 0.5 + R * 0.15 * k, R * 0.28 * k, R * 0.07 * k, 10, 170, 10), cx, cy, ang), "#8A6A30", 1.2, seed + k, 0.6, 1))
    for k in range(-4, 5):
        out.append(pline(rot([(cx, cy - R * 0.48), (cx + k * R * 0.24, cy + R * 0.1)], cx, cy, ang), "#8A6A30", 0.9, seed + k, 0.45, 1))
    kx, ky = rot([(cx, cy - R * 0.52)], cx, cy, ang)[0]
    out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{R * 0.07:.1f}" fill="#8A5A2A" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def bahay_kubo(D, cx, base, w, seed, floor_h=70, wall_h=96):
    """Bahay kubo on bamboo stilts: raised floor, sawali walls, a propped window, a steep nipa roof, bamboo ladder."""
    l, r = cx - w / 2, cx + w / 2
    fy = base - floor_h
    out = [cast(D, cx + 10, base + 2, w * 0.62, 12, strength=0.45, seed=seed)]
    # stilts (haligi): the corner posts are thick hardwood
    for k, x in enumerate((l + 8, cx, r - 8)):
        thick = 18 if k != 1 else 12
        out.append(painted(D, rect_pts(x - thick / 2, fy - 4, x + thick / 2, base, 10, seed + k, 0.3), NARRA, seed + k, sdir=(1, 0), sk=0.3, angle=-90, n=6, inkw=1.4, hi=0.4))
    for x in (l + 50, r - 50):
        out.append(taper([(x, fy), (x, base)], 9, 9, "#C8A86A"))
        for j in range(3):
            out.append(pline([(x - 4, fy + 14 + j * 18), (x + 4, fy + 15 + j * 18)], "#7A5A2A", 1.4, j, 0.8, 1))
    out.append(f'<path d="{pd([(l, fy - 8), (r, fy - 8), (r, fy + 6), (l, fy + 6)])}" fill="#3A2A12" opacity="0.4"/>')
    # floor beam
    out.append(painted(D, rect_pts(l - 10, fy - 12, r + 10, fy + 2, 14, seed + 5, 0.4), ("#E8C88A", "#B8945A", "#6A4A22"), seed + 5, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.4, hi=0.4))
    # walls of sawali
    wl = densify([(l + 4, fy - 12), (r - 4, fy - 12), (r - 4, fy - 12 - wall_h), (l + 4, fy - 12 - wall_h)], 12)
    wd = smooth_closed(wl)
    out.append(sawali(D, wd, seed + 6))
    out.append(clipped(D, wd, [f'<path d="{wd}" fill="{D.lin([(0, "#3A2408", 0.25), (0.4, "#3A2408", 0), (1, "#3A2408", 0.2)], 0, 0, 1, 0)}"/>']))
    out.append(ink(wd, INK, 1.6, seed + 6, 1, 0.7))
    for x in (l + 4, r - 4, cx):
        out.append(taper([(x, fy - 12), (x, fy - 12 - wall_h)], 8, 8, "#C8A86A"))
    # window with a propped awning
    wx0, wx1 = cx + 24, cx + 92
    wy0, wy1 = fy - 12 - wall_h + 22, fy - 40
    out.append(f'<path d="{pd([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])}" fill="#3A2A1A"/>')
    out.append(f'<path d="{pd([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])}" fill="#FFD890" opacity="0.35"/>')
    aw = [(wx0 - 8, wy0 + 2), (wx1 + 8, wy0 + 2), (wx1 + 16, wy0 - 26), (wx0 - 2, wy0 - 30)]
    out.append(painted(D, densify(aw, 8), ("#E8C88A", "#B8945A", "#6A4A22"), seed + 7, sk=0.2, angle=0, n=6, inkw=1.3, hi=0.4))
    out.append(pline([(wx1 + 4, wy1), (wx1 + 14, wy0 - 24)], "#7A5A2A", 2.4, seed, 0.9, 1))
    # door and bamboo ladder
    dx0, dx1 = l + 34, l + 86
    out.append(f'<path d="{pd([(dx0, fy - 12), (dx1, fy - 12), (dx1, fy - 12 - wall_h + 14), (dx0, fy - 12 - wall_h + 14)])}" fill="#2A1E12"/>')
    out.append(soft_glow(D, (dx0 + dx1) / 2, fy - 50, 40, "#FFC870", 0.4))
    for x in (dx0 - 10, dx1 + 6):
        out.append(taper([(x, fy - 8), (x - 26 if x < dx1 else x - 14, base)], 6, 6, "#C8A86A"))
    for j in range(4):
        t = (j + 1) / 5
        out.append(taper([(dx0 - 10 - 26 * t, fy - 8 + floor_h * t), (dx1 + 6 - 14 * t, fy - 8 + floor_h * t)], 5, 5, "#B8945A"))
    # nipa roof
    rt = fy - 12 - wall_h
    roof = [(l - 36, rt + 16), (cx, rt - w * 0.5), (r + 36, rt + 16), (r + 26, rt + 26), (cx, rt + 12), (l - 26, rt + 26)]
    out.append(painted(D, roof, NIPA, seed + 8, sdir=(0.7, 0.6), sk=0.15, angle=-70, n=60, slen=(10, 30), sw=(1, 2.4), inkw=1.8, hi=0.45))
    rd = smooth_closed(roof)
    rnd = random.Random(seed)
    thatch = []
    for j in range(7):
        t = (j + 1) / 8
        y = rt - w * 0.5 + (w * 0.5 + 18) * t
        hw = (w / 2 + 36) * t
        thatch.append(pline([(cx - hw, y + 4), (cx, y - 2), (cx + hw, y + 4)], "#8A6A30", 1.4, seed + j, 0.5, 1))
    for _ in range(80):
        x = rnd.uniform(l - 30, r + 30)
        thatch.append(f'<path d="M {x:.1f} {rt + 22:.1f} l {rnd.uniform(-2, 2):.1f} {rnd.uniform(6, 12):.1f}" stroke="{rnd.choice(["#C8A058", "#8A6A30"])}" stroke-width="1.4"/>')
    out.append(clipped(D, rd + f" M {l - 40} {rt + 20} L {r + 40} {rt + 20} L {r + 40} {rt + 40} L {l - 40} {rt + 40} Z", thatch))
    out.append(taper([(cx - 8, rt - w * 0.5 + 4), (cx, rt - w * 0.5 - 6), (cx + 8, rt - w * 0.5 + 4)], 8, 8, "#8A6A30"))
    return "".join(out), (l + 8, fy)


def chicken(D, x, base, s, seed, flip=1, pal=("#E8A050", "#B8642A", "#6A320E")):
    P = lambda a, b: (x + a * s * flip, base + b * s)
    out = [cast(D, x, base + 2, 14 * s, 3 * s, strength=0.3, seed=seed)]
    body = [P(-16, -10), P(-6, -22), P(10, -24), P(18, -16), P(14, -6), P(-4, -4)]
    out.append(painted(D, body, pal, seed, sk=0.2, n=4, inkw=1.1, hi=0.4))
    out.append(painted(D, [P(-16, -10), P(-26, -26), P(-22, -8)], ("#3A4A3A", "#1E2A22", "#0A120E"), seed + 1, sk=0.1, n=2, inkw=0.8, hi=0.3))
    out.append(f'<path d="{blob(*P(16, -26), 5 * s, 5 * s, seed + 2, 0.05, 8)}" fill="{pal[1]}"/>')
    out.append(f'<path d="{pd([P(14, -32), P(17, -36), P(19, -31)])}" fill="#D8241E"/>')
    out.append(f'<path d="{pd([P(20, -27), P(25, -25), P(20, -24)])}" fill="#F2B21E"/>')
    out.append(pline([P(0, -4), P(0, 4)], "#C8902A", 1.2 * s, seed, 1, 1) + pline([P(6, -4), P(7, 4)], "#C8902A", 1.2 * s, seed + 1, 1, 1))
    return "".join(out)


@design("tatay")
def tatay():
    D = Doc2("ph-ty")
    out = [sky(D, [(0, "#6AA8D8"), (0.5, "#F2C890"), (0.75, "#FFB070")], 2501, 600, ["#8AB8E0", "#FFD8A8", "#F8A878"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 330, 180, "#FFE8A8", 0.7))
    out.append(hill(D, ridge([(-20, 380), (120, 350), (260, 366), (420, 340), (620, 370)], 2502, 5, 3), 460, ("#A8B898", "#8A9A80", "#6A7A62"), 2503, inkw=0))
    # banana plants and coconut palms around the house
    for k, (bx, ty, lean) in enumerate(((84, 240, -14), (530, 250, 12))):
        out.append(palm(D, (bx, 470), (bx + lean, ty), 2504 + k, L=80, width=12, nuts=True))
    for k, (x, ang) in enumerate(((70, -120), (96, -60), (520, -110), (546, -70))):
        out.append(banana_leaf(D, x, 452, ang, 90, 22, 2506 + k, pal=SAGING))
    # ground
    gp = "M -10 440 L 610 440 L 610 610 L -10 610 Z"
    out.append(f'<path d="{gp}" fill="{D.lin([(0, "#9AB860"), (1, "#6A8A3A")])}"/>')
    out.append(grass(2510, (-10, 440, 610, 600), ["#5A8A2A", "#8AB84A", "#3E6A1E", "#A8C860"], n=260, h=(8, 20)))
    kubo, (px, py) = bahay_kubo(D, 300, 526, 236, 2511, floor_h=80, wall_h=96)
    out.append(kubo)
    # Tatay's salakot hung on the corner post, the chickens underneath
    out.append(salakot(D, px + 2, py + 40, 40, 2512, ang=-6))
    out.append(chicken(D, 330, 532, 1.1, 2513))
    out.append(chicken(D, 384, 536, 0.9, 2514, flip=-1, pal=("#F6F0E4", "#D8CCB8", "#8A7A68")))
    for k in range(5):
        rnd = random.Random(2515 + k)
        out.append(f'<circle cx="{rnd.uniform(320, 420):.1f}" cy="{rnd.uniform(528, 540):.1f}" r="1.6" fill="#F2D898"/>')
    # lettering
    out.append(letters(D, 300, 154, "Tatay", SERIF_IT, 120, "#2E4A8A", ["#3E5AA8", "#1A2A5A", "#5A7AC8"], 2520, max_w=360,
                       shadow="#FFF6E8", soff=(0.018, 0.03), angle=-40, hi="#C8D8F8"))
    out.append(ruled(300, 196, "HALIGI NG TAHANAN", "#8A3A1E", font=JOS, size=21, ls=7, line_w=32, gap=14))
    return finish_b(D, out, 2521)


# ================================================================ 28. balikbayan box — packed full, taped, tied, on its way home
def corned_can(D, cx, base, w, h, seed, col=PULA):
    out = [painted(D, densify([(cx - w / 2, base), (cx - w / 2 * 0.86, base - h), (cx + w / 2 * 0.86, base - h), (cx + w / 2, base)], 6), col, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=5, inkw=1.2, hi=0.5)]
    out.append(f'<path d="{ellipse_d(cx, base - h, w / 2 * 0.86, w * 0.12)}" fill="#D8DEE6" stroke="#5A6270" stroke-width="1"/>')
    out.append(f'<rect x="{cx - w * 0.3:.1f}" y="{base - h * 0.6:.1f}" width="{w * 0.6:.1f}" height="{h * 0.26:.1f}" rx="2" fill="#F6E8C8" opacity="0.9"/>')
    return "".join(out)


@design("balikbayan-box")
def balikbayan_box():
    D = Doc2("ph-bb")
    out = [paper(D.nid(), "#E4EEF4", "#4A6A8A", 2601)]
    out.append(blooms(2602, ["#B8D4E8", "#F2D8C0", "#D8E8F0"], 8, (0, 0, 600, 600), (90, 200), (0.1, 0.16)))
    # dotted flight path over the Pacific, plane and a heart at home
    path = [(70, 240), (150, 196), (250, 226), (330, 270), (430, 236), (520, 196)]
    cp = catmull(path, 10)
    for i in range(0, len(cp) - 1, 3):
        out.append(pline([cp[i], cp[i + 1]], "#C8462A", 2.4, i, 0.8, 1))
    px, py = 470, 214
    plane = rot([(px - 22, py), (px + 22, py), (px + 26, py + 2), (px + 22, py + 4), (px - 22, py + 4)], px, py, -20)
    out.append(f'<path d="{smooth_closed(plane)}" fill="#3A4A6A"/>')
    out.append(f'<path d="{smooth_closed(rot([(px - 4, py + 2), (px + 6, py - 18), (px + 12, py - 18), (px + 6, py + 2)], px, py, -20))}" fill="#3A4A6A"/>')
    out.append(f'<path d="{smooth_closed(rot([(px - 4, py + 2), (px + 6, py + 18), (px + 12, py + 18), (px + 6, py + 2)], px, py, -20))}" fill="#2A3A5A"/>')
    out.append(f'<path d="{smooth_closed(rot([(px - 20, py + 2), (px - 26, py - 8), (px - 22, py - 8), (px - 14, py + 2)], px, py, -20))}" fill="#3A4A6A"/>')
    out.append(p_heart(D, 66, 246, 12, PULA, 2603, inkw=1))
    out.append(p_heart(D, 534, 190, 9, PULA, 2604, inkw=1))
    # the box in 3/4 view
    fx0, fx1, ftop, fbot = 120, 380, 330, 540
    dx, dy = 110, -60
    front = [(fx0, ftop), (fx1, ftop), (fx1, fbot), (fx0, fbot)]
    side = [(fx1, ftop), (fx1 + dx, ftop + dy), (fx1 + dx, fbot + dy), (fx1, fbot)]
    top = [(fx0, ftop), (fx0 + dx, ftop + dy), (fx1 + dx, ftop + dy), (fx1, ftop)]
    card = ("#E8C08A", "#C8945A", "#7A5228")
    out.append(cast(D, 300, 546, 220, 16, strength=0.5, seed=2605))
    # items heaped in the open top (drawn first, the flaps and front go over them)
    inner = [f'<path d="{pd(top)}" fill="#5A3A1A"/>']
    out.append("".join(inner))
    items = []
    items.append(corned_can(D, 214, ftop - 30, 36, 44, 2606))
    items.append(corned_can(D, 256, ftop - 40, 36, 44, 2607, col=("#7AB8F0", "#1E6AC8", "#0E3A7A")))
    items.append(painted(D, rot(rect_pts(296, ftop - 96, 340, ftop - 20, 8, 2608, 0.4), 318, ftop - 58, 10), ("#C8A0E8", "#7A48B0", "#3E1A66"), 2608, sk=0.2, n=5, inkw=1.3, hi=0.4))
    items.append(painted(D, rot(rect_pts(150, ftop - 76, 200, ftop - 10, 8, 2609, 0.4), 176, ftop - 44, -12), ("#FFF2C8", "#F6D27A", "#B88A2A"), 2609, sk=0.2, n=5, inkw=1.3, hi=0.4))
    # a teddy bear peeking
    bx, by = 384, ftop - 84
    items.append(painted(D, blob_pts(bx, by, 26, 24, 2610, 0.04, 14), ("#D8A878", "#A8744A", "#5A3A1E"), 2610, sk=0.2, n=8, inkw=1.4, hi=0.4))
    for sg in (-1, 1):
        items.append(painted(D, blob_pts(bx + sg * 20, by - 20, 9, 9, 2611 + sg, 0.05, 10), ("#D8A878", "#A8744A", "#5A3A1E"), 2611 + sg, sk=0.2, n=3, inkw=1.2, hi=0.4))
    items.append(f'<path d="{blob(bx, by + 6, 11, 8, 2614, 0.05, 10)}" fill="#F2D8B0"/><circle cx="{bx}" cy="{by + 2}" r="3" fill="#2A1A0A"/>')
    items.append(f'<circle cx="{bx - 9}" cy="{by - 6}" r="2.6" fill="#1A0A04"/><circle cx="{bx + 9}" cy="{by - 6}" r="2.6" fill="#1A0A04"/>')
    items.append(taper([(bx - 26, by + 22), (bx, by + 28), (bx + 26, by + 22)], 6, 6, PULA[1]))
    # a rolled towel and a pair of sneakers
    items.append(painted(D, blob_pts(440, ftop - 54, 30, 16, 2615, 0.05, 12), ("#FFFFFF", "#E8F0F8", "#A8B8C8"), 2615, sk=0.2, n=6, inkw=1.2, hi=0.4))
    items.append(pline(ell_pts(440, ftop - 54, 18, 9, 0, 300, 12), "#A8B8C8", 1.4, 2616, 0.8, 1))
    out.append(clipped(D, smooth_closed(top) + " M 100 120 L 520 120 L 520 " + str(ftop) + " L 100 " + str(ftop) + " Z", items))
    # flaps folded open
    for flap in ([(fx0, ftop), (fx1, ftop), (fx1 - 20, ftop - 60), (fx0 - 30, ftop - 54)],
                 [(fx1, ftop), (fx1 + dx, ftop + dy), (fx1 + dx + 52, ftop + dy - 28), (fx1 + 50, ftop - 18)]):
        out.append(painted(D, densify(flap, 10), card, 2617 + int(flap[2][0]), sdir=(0.5, 0.8), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.35))
    # box faces
    out.append(painted(D, densify(side, 12), tuple(dk(c, 0.15) for c in card), 2620, sdir=(0.9, 0.3), sk=0.15, angle=-90, n=20, inkw=1.8, hi=0.25))
    out.append(painted(D, densify(front, 12), card, 2621, sdir=(0.6, 0.6), sk=0.12, angle=-90, n=30, inkw=2, hi=0.3))
    fd = pd(front)
    deco = []
    # tape strips
    deco.append(f'<rect x="{fx0 - 10}" y="{ftop + 92}" width="{fx1 - fx0 + 20}" height="22" fill="#D8B070" opacity="0.8"/>')
    deco.append(f'<rect x="{(fx0 + fx1) / 2 - 12:.0f}" y="{ftop - 10}" width="24" height="{fbot - ftop + 20}" fill="#D8B070" opacity="0.8"/>')
    out.append(clipped(D, fd, deco))
    # handwritten address in marker
    out.append(f'<text x="{(fx0 + fx1) / 2 - 40:.0f}" y="{ftop + 60}" text-anchor="middle" {SERIF_IT} font-size="{fit_size("Para sa pamilya", SERIF_IT, 28, 150)}" fill="#1E2A5A" transform="rotate(-3 200 {ftop + 60})">Para sa pamilya</text>')
    out.append(f'<text x="{(fx0 + fx1) / 2 + 60:.0f}" y="{ftop + 182}" text-anchor="middle" {BEBAS} font-size="28" letter-spacing="2" fill="#C8241E" transform="rotate(-4 310 {ftop + 182})">FRAGILE</text>')
    out.append(p_heart(D, 168, ftop + 176, 13, PULA, 2622, inkw=0.8))
    # "this side up" arrows on the side face
    for k in range(2):
        ax, ay = fx1 + 34 + k * 30, ftop + 70 - k * 16
        out.append(f'<path d="M {ax:.1f} {ay + 26:.1f} L {ax:.1f} {ay:.1f} M {ax - 7:.1f} {ay + 8:.1f} L {ax:.1f} {ay:.1f} L {ax + 7:.1f} {ay + 8:.1f}" stroke="#1E2A5A" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # yellow plastic strap tied around
    for y0 in (ftop + 128,):
        out.append(f'<path d="{pd([(fx0 - 2, y0 - 5), (fx1, y0 - 5), (fx1 + dx, y0 - 5 + dy), (fx1 + dx, y0 + 5 + dy), (fx1, y0 + 5), (fx0 - 2, y0 + 5)])}" fill="#F6C51E" stroke="#A87A0A" stroke-width="1"/>')
        out.append(pline([(fx0, y0 - 2), (fx1, y0 - 2), (fx1 + dx, y0 - 2 + dy)], "#FFF2A0", 1.4, 2623, 0.8, 1))
    # lettering
    out.append(letters(D, 300, 124, "BALIKBAYAN BOX", BEBAS, 88, "#1E3A7A", ["#2E5AA8", "#0E1E4A", "#4A7AC8"], 2630, max_w=460, ls=4, wob=0.5,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8D8F8"))
    out.append(ruled(300, 162, "PUNO NG PAGMAMAHAL", "#C8462A", font=JOS, size=20, ls=6, line_w=28, gap=12))
    return finish_b(D, out, 2631, "#2A3A4A")


# ================================================================ 29. tuloy po kayo — tsinelas lined up at the open door
@design("tuloy-po-kayo")
def tuloy_po_kayo():
    D = Doc2("ph-tp")
    from summer_gouache import flipflop
    out = [wall(D, "#F6DC9A", "#E8C070", 2701, ["#FFEAB8", "#D8A850", "#F8E0A8"])]
    # the doorway, open, with warm light inside
    dx0, dx1, dtop, dbot = 190, 410, 210, 440
    out.append(painted(D, rect_pts(dx0 - 24, dtop - 24, dx1 + 24, dbot, 16, 2702, 0.4), NARRA, 2702, sdir=(0.6, 0.8), sk=0.15, angle=-90, n=30, inkw=1.8, hi=0.4))
    inside = smooth_closed(rect_pts(dx0, dtop, dx1, dbot, 16, 2703, 0.3))
    ins = [f'<rect x="{dx0}" y="{dtop}" width="{dx1 - dx0}" height="{dbot - dtop}" fill="{D.lin([(0, "#FFE6B0"), (1, "#F2B868")])}"/>',
           f'<path d="M {dx0} {dbot - 60} L {dx1} {dbot - 60} L {dx1} {dbot} L {dx0} {dbot} Z" fill="#C88A52"/>',
           capiz_window(D, 252, 236, 348, 314, 2704, cols=3, rows=3, glow="#FFF4D8"),
           f'<path d="{ellipse_d(300, 376, 56, 12)}" fill="#8A4E2A" stroke="{INK}" stroke-width="1.2"/>',
           taper([(262, 380), (258, 428)], 5, 5, "#5E3018"), taper([(338, 380), (342, 428)], 5, 5, "#5E3018"),
           painted(D, densify([(286, 374), (284, 346), (292, 336), (308, 336), (316, 346), (314, 374)], 6), ("#C8E0F0", "#7AA8D0", "#3A5A8A"), 2705, sk=0.2, n=4, inkw=1.2, hi=0.5)]
    for j in range(6):
        ins.append(sampaguita_flower(D, 288 + (j % 3) * 12, 326 - (j // 3) * 12, 6, 2706 + j))
    out.append(clipped(D, inside, ins))
    out.append(soft_glow(D, 300, 360, 200, "#FFE8A0", 0.45))
    # both door leaves swung open (seen edge-on, carved panels)
    for sg, x in ((-1, dx0), (1, dx1)):
        leaf = [(x, dtop), (x + sg * 44, dtop + 16), (x + sg * 44, dbot + 10), (x, dbot)]
        out.append(painted(D, densify(leaf, 10), ("#B8784A", "#8A4E2A", "#4A2410"), 2707 + sg, sdir=(0.9 * sg, 0.3), sk=0.2, angle=-90, n=14, inkw=1.8, hi=0.35))
        for j in range(3):
            y0 = dtop + 30 + j * 78
            out.append(ink(smooth_closed(densify([(x + sg * 8, y0 + 3), (x + sg * 36, y0 + 10), (x + sg * 36, y0 + 60), (x + sg * 8, y0 + 56)], 6)), "#4A2410", 1.4, 2709 + j, 1, 0.7))
    # steps of red tile
    out.append(painted(D, rect_pts(150, 440, 450, 464, 16, 2712, 0.4), ("#E88A6A", "#C0583A", "#7A2A14"), 2712, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.45))
    out.append(painted(D, rect_pts(110, 464, 490, 490, 16, 2713, 0.4), ("#E88A6A", "#C0583A", "#7A2A14"), 2713, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.6, hi=0.45))
    for k in range(9):
        out.append(pline([(150 + k * 37.5, 440), (150 + k * 37.5, 464)], "#7A2A14", 1.2, k, 0.5, 1))
    out.append(f'<path d="M -10 490 L 610 490 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#C8B8A0"), (1, "#A89880")])}"/>')
    # potted plants either side
    for k, (x, pal) in enumerate(((96, ("#F8C860", "#E07A2A", "#8A3A10")), (504, ("#8AD06A", "#2E8A3A", "#14501E")))):
        out.append(painted(D, densify([(x - 34, 410), (x - 26, 490), (x + 26, 490), (x + 34, 410)], 8), PALAYOK, 2714 + k, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.4))
        if k == 0:
            for j in range(9):
                a = -150 + j * 15
                out.append(leaf_simple(D, x, 410, 60, 14, a, [("#F8E070", "#D8A020", "#7A5A0A"), ("#F28A5A", "#C8402A", "#7A1A0A"), ("#9AD06A", "#3E8A2A", "#1A4A14")][j % 3], 2716 + j, inkw=1))
        else:
            for j in range(7):
                a = -125 + j * 12
                out.append(leaf_simple(D, x - 10 + j * 3, 414, 110, 9, a, pal, 2730 + j, inkw=1))
    # the tsinelas, lined up neatly on the steps: Tatay, Nanay, Lola, Kuya, bunso
    pairs = [(132, 66, ("#7AB0F0", "#1E5AC8", "#0E2A6A"), ("#2A2A3A", "#1A1A22", "#000000")), (216, 58, ("#FFB8D0", "#EE6A98", "#A82A5A"), ("#FFFFFF", "#F2EEE8", "#B8B0A6")),
             (298, 58, ("#B8E0A8", "#5EAE5A", "#2A6A2A"), ("#F2D898", "#C8A058", "#7A5A26")), (382, 62, ("#FFE08A", "#F2B21E", "#A87A0A"), ("#E8304A", "#C8241E", "#7A0E10")),
             (462, 44, ("#C8A8F0", "#8A5AD0", "#4A2A8A"), ("#FFFFFF", "#F2EEE8", "#B8B0A6"))]
    for k, (x, L, sole, strap) in enumerate(pairs):
        for j, sg in enumerate((-1, 1)):
            fx = x + sg * L * 0.17
            out.append(f'<g transform="translate({fx:.1f} 514) scale(1 0.5) translate({-fx:.1f} -514)">{flipflop(D, fx, 514, L * 1.45, 2740 + k * 2 + j, sole=sole, strap=strap, flip=sg)}</g>')
    # lettering
    out.append(letters(D, 300, 124, "Tuloy po kayo", SERIF_IT, 104, "#7A2E14", ["#9A3E1E", "#4A1408", "#B85A2A"], 2760, max_w=460,
                       shadow="#FFF6E0", soff=(0.018, 0.03), angle=-40, hi="#F8B080"))
    out.append(ruled(300, 166, "WELCOME TO OUR HOME", "#1E4AA0", font=JOS, size=19, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 2761)


# ================================================================ 30. mabuhay! — the eight-rayed sun rising, three stars above
@design("mabuhay")
def mabuhay():
    D = Doc2("ph-mb")
    out = [sky(D, [(0, "#0E2A7A"), (0.5, "#2A4AA8"), (0.78, "#E87A6A"), (0.9, "#F6B07A")], 2801, 420, ["#1E3A8A", "#3A5AB8", "#F29A7A"], 60, angle=-3, sop=(0.06, 0.16))]
    cx, cy = 300, 400
    out.append(soft_glow(D, cx, cy, 300, "#FFE08A", 0.6))
    # eight principal rays, each a long gold blade flanked by two thinner ones, as on the flag
    rays = []
    for k in range(8):
        a = math.radians(-180 + (k + 0.5) * 180 / 8)
        for off, L, w in ((0, 214, 20), (-0.085, 176, 7), (0.085, 176, 7)):
            aa = a + off
            tip = (cx + math.cos(aa) * L, cy + math.sin(aa) * L)
            b0 = (cx + math.cos(aa + 1.5708) * w, cy + math.sin(aa + 1.5708) * w)
            b1 = (cx + math.cos(aa - 1.5708) * w, cy + math.sin(aa - 1.5708) * w)
            rays.append(f'<path d="{pd([b0, tip, b1])}" fill="{ARAW[1]}" opacity="{0.5 if off else 0.62}"/>')
    out.append("".join(rays))
    out.append(f'<path d="M {cx - 92} {cy} A 92 92 0 0 1 {cx + 92} {cy} Z" fill="{D.rad([(0, "#FFF8D0"), (0.6, ARAW[0]), (1, ARAW[1])], 0.5, 0.9, 0.9)}"/>')
    out.append(strokes(D.nid(), f"M {cx - 92} {cy} A 92 92 0 0 1 {cx + 92} {cy} Z", (cx - 100, cy - 100, cx + 100, cy), ["#FFFFFF", ARAW[1]], 2802, n=30, angle=-30, length=(10, 30), width=(2, 4), opacity=(0.2, 0.45)))
    # three five-point stars
    for k, (x, y, r) in enumerate(((150, 262, 22), (300, 222, 26), (450, 262, 22))):
        pts = [(x + (r if i % 2 == 0 else r * 0.42) * math.cos(math.radians(-90 + i * 36)), y + (r if i % 2 == 0 else r * 0.42) * math.sin(math.radians(-90 + i * 36))) for i in range(10)]
        out.append(soft_glow(D, x, y, r * 2.4, "#FFE08A", 0.45))
        out.append(painted(D, round_poly(pts, 2, 2), ARAW, 2803 + k, sk=0.15, n=6, inkw=1.4, inkc="#8A5A08", hi=0.5))
    # the sea, catching the red of sunrise
    out.append(sea(D, 400, 610, [(0, "#E86A5A"), (0.4, "#C8343A"), (1, "#7A1424")], 2806, ["#F28A7A", "#8A1424", "#FFC890"], n=90))
    rnd = random.Random(2807)
    for k in range(30):
        y = 406 + k * 5
        w = 70 - k * 1.2
        x = cx + rnd.uniform(-w, w) * 0.5
        out.append(taper([(x - w * rnd.uniform(0.2, 0.5), y), (x + w * rnd.uniform(0.2, 0.5), y + 1)], 3, 2, rnd.choice(["#FFE8A8", "#FFD080"]), rnd.uniform(0.5, 0.9)))
    # islands far off on the horizon
    for pts, sd in (([(-20, 402), (40, 384), (110, 392), (160, 402)], 2808), ([(440, 402), (500, 380), (560, 388), (620, 402)], 2809)):
        out.append(f'<path d="{smooth_closed(ridge(pts, sd, 3, 2) + [(620, 404), (-20, 404)])}" fill="#3A1A3A" opacity="0.8"/>')
    # a garland of sampaguita across the foot, a welcome lei
    gl = [(60, 474), (150, 504), (300, 516), (450, 504), (540, 474)]
    cp = catmull(gl, 6)
    out.append(pline(cp, "#3E7A2A", 2, 2810, 0.9, 1))
    for i, (x, y) in enumerate(cp):
        if i % 2:
            out.append(leaf_simple(D, x, y, 14, 4, 90 + (i % 4) * 40, ("#8AC870", "#3E8A3A", "#1E5A22"), 2811 + i, vein=False, inkw=0))
        out.append(sampaguita_flower(D, x, y - 2, 9, 2830 + i, rot_=i * 13, layers=1 + (i % 3 == 0)))
    out.append(taper([(300, 520), (296, 546), (304, 566)], 6, 3, PULA[1]))
    # lettering
    out.append(letters(D, 300, 140, "MABUHAY!", BEBAS, 128, "#FFE08A", ["#FFF2C0", "#F6C51E", "#FFE8A8"], 2840, max_w=440, ls=8, wob=0.5,
                       shadow="#0A1A4A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 180, "PILIPINAS", "#FFF2D0", font=JOS, size=22, ls=12, line_w=40, gap=14))
    return finish_b(D, out, 2841, "#0A0A2A", 0.6)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
