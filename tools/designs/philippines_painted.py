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
                            bird_v, p_heart, branch)
from japan_painted import densify, round_poly, clipped
import holidays_gouache as hg
import figures
import fall_gouache_a as _fga
import brasil_painted as _brp
import summer_gouache as _smg
import japan_painted as _jpp
import paint_philippines_kit as K
from paint_philippines_kit import (TXT, Cam3, gouache_finish, soft_ink, dry_brush, brush_field, streak_reflection, sky_paint,
                                   color_at, tint, ripple_filter, soft_filter, vstreaks, cloud_bank, fur, fuzzy_edge, bokeh, rain_sheets)

# Gallery pass: the hard full pen outline becomes a broken, warm, lost-and-found line everywhere (shared helpers
# included, in this process only), and every design is finished by the paint filter (edges, pooled pigment,
# bristle texture, granulation) with its lettering kept crisp on top.
ink = K.install_soft_ink(_fga, _brp, _smg, _jpp, hg, color="#4A2E1E")
_letters, _ruled, _label = letters, ruled, label
_T0, _T1 = "<!--T0-->", "<!--T1-->"


def letters(*a, **k):
    return _T0 + _letters(*a, **k) + _T1


def ruled(*a, **k):
    return _T0 + _ruled(*a, **k) + _T1


def label(*a, **k):
    return _T0 + _label(*a, **k) + _T1


CURRENT = {"slug": "ph"}


def steam_wisps(cx, y, h, seed, col="#FFFFFF", n=3, gap=28, w=7, op=0.75):
    return K.soft_steam(cx, y, h, seed, col, n, gap * 0.8, w, min(0.7, op), uid=CURRENT["slug"])


def steam(cx, y, h, seed, col="#FFFFFF", n=3, gap=22, w=6, op=0.6):
    return K.soft_steam(cx, y, h, seed, col, n, gap * 0.8, w, min(0.7, op + 0.1), uid=CURRENT["slug"])
FILTER = {}          # per-slug overrides of the paint filter


def finish_b(D, out, seed, color="#3A2418", op=1.0):
    """Grain, then split the lettering off the art: art goes through the paint filter, words stay crisp on top."""
    import re
    body = _brp.finish_b(D, out, seed, color, op)
    texts = re.findall(re.escape(_T0) + r"(.*?)" + re.escape(_T1), body, flags=re.S)
    art = re.sub(re.escape(_T0) + r".*?" + re.escape(_T1), "", body, flags=re.S)
    slug = CURRENT["slug"]
    kw = dict(seed=seed % 997 + 1)
    kw.update(FILTER.get(slug, {}))
    return gouache_finish(slug, art + TXT + "".join(texts), **kw)

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


# ================================================================ shared painted rooms (gallery pass)
def room_bg(D, seed, wall, table_y, table=NARRA, light_from=-1, window=True, shelf=None, warm="#FFE6B0", wall_dark=None, planks=4):
    """A painted kitchen / sala corner: plaster wall worked in brush strokes, a window just out of frame throwing a
    soft slanted shaft of light across the wall and the table, a soft-focus shelf of jars in the back (optional),
    a wooden tabletop catching the light. Returns the parts list to start a design with."""
    rnd = random.Random(seed)
    wd = wall_dark or dk(wall, 0.35)
    out = [f'<rect x="-10" y="-10" width="620" height="{table_y + 10}" fill="{wall}"/>',
           clipped(D, f"M -10 -10 L 610 -10 L 610 {table_y} L -10 {table_y} Z",
                   [brush_field(seed, (-40, -10, 610, table_y), [lt(wall, 0.18), wd, mix(wall, warm, 0.3), dk(wall, 0.15)], 220, -88, (30, 100), (4, 10), (0.12, 0.3)),
                    streaks_down(seed + 1, (-10, -10, 610, table_y), wd, 30)]),
           f'<rect x="-10" y="-10" width="620" height="{table_y + 10}" fill="{D.lin([(0, wd, 0.0 if light_from < 0 else 0.45), (1, wd, 0.45 if light_from < 0 else 0.0)], 0, 0, 1, 0)}"/>']
    fid = D.nid()
    D.defs.append(soft_filter(fid, 9))
    if window:
        # the window's light falls on the wall as a slanted bright parallelogram, with the shadow of its mullions
        x0 = 40 if light_from < 0 else 330
        sh = [(x0, 120), (x0 + 220, 140), (x0 + 250, table_y - 10), (x0 + 30, table_y - 30)]
        if light_from > 0:
            sh = [(x0 + 30, 140), (x0 + 250, 120), (x0 + 220, table_y - 30), (x0, table_y - 10)]
        out.append(f'<g filter="url(#{fid})"><path d="{pd(sh)}" fill="{warm}" opacity="0.45"/>'
                   f'<path d="M {(sh[0][0] + sh[1][0]) / 2:.1f} {(sh[0][1] + sh[1][1]) / 2:.1f} L {(sh[2][0] + sh[3][0]) / 2:.1f} {(sh[2][1] + sh[3][1]) / 2:.1f}" stroke="{wd}" stroke-width="12" opacity="0.25"/></g>')
    if shelf:
        fid2 = D.nid()
        D.defs.append(soft_filter(fid2, 2.6))
        sy = shelf
        jars = [f'<path d="{pd([(-10, sy), (610, sy), (610, sy + 10), (-10, sy + 10)])}" fill="{dk(table[1], 0.2)}"/>']
        x = rnd.uniform(-20, 30)
        while x < 600:
            w = rnd.uniform(26, 44)
            h = rnd.uniform(36, 70)
            c = rnd.choice(["#C89A5A", "#E8D8B8", "#8A5A3A", "#D8C098", "#B86A3A", "#E8E0D0"])
            jars.append(f'<path d="{pd([(x, sy), (x + w, sy), (x + w, sy - h), (x, sy - h)])}" fill="{c}" opacity="0.9"/>'
                        f'<rect x="{x + w * 0.15:.1f}" y="{sy - h - 6:.1f}" width="{w * 0.7:.1f}" height="7" fill="{dk(c, 0.3)}"/>'
                        f'<rect x="{x + 4:.1f}" y="{sy - h + 4:.1f}" width="4" height="{h - 8:.1f}" fill="#FFFFFF" opacity="0.35"/>')
            x += w + rnd.uniform(8, 50)
        out.append(f'<g filter="url(#{fid2})" opacity="0.8">{"".join(jars)}</g>')
    out.append(wood_planks(D, table_y, 610, seed + 2, pal=table, n=planks))
    out.append(f'<path d="M -10 {table_y} L 610 {table_y} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FFF0C8", 0.0), (1, "#1A0A04", 0.35)], 0, table_y, 0, 610, "userSpaceOnUse")}"/>')
    out.append(f'<path d="M -10 {table_y} L 610 {table_y}" stroke="{lt(table[0], 0.3)}" stroke-width="2.4" opacity="0.7"/>')
    return out


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
    # a mustard kitchen wall with the morning sun slanting across it, jars on the shelf behind, the narra table
    out = room_bg(D, 11, "#D8A04A", 418, table=NARRA, light_from=-1, shelf=300, warm="#FFF0C0", planks=3)
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
    # a merienda stand on a hot afternoon, the street behind it out of focus
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#8AC4EE"), (0.45, "#CDE6F2"), (0.8, "#F6E8C8")])}"/>']
    fid = D.nid()
    D.defs.append(soft_filter(fid, 5))
    bg = [soft_glow(D, 470, 200, 280, "#FFFBE8", 0.85)]
    bg.append(f'<path d="{pd([(-10, 300), (180, 300), (180, 494), (-10, 494)])}" fill="#E8C8A0"/>')        # a pastel house front
    bg.append(f'<path d="{pd([(30, 330), (100, 330), (100, 420), (30, 420)])}" fill="#5A8A9A"/>')
    bg.append(f'<path d="{pd([(420, 290), (610, 290), (610, 494), (420, 494)])}" fill="#F2D8E0"/>')
    bg.append(f'<path d="{pd([(460, 330), (540, 330), (540, 420), (460, 420)])}" fill="#7A5A4A"/>')
    bg.append(dab_crown(D, 300, 300, 150, 70, [("#9AD070", "#4E9A3A", "#2A6A2A")], 21, n=90, size=(10, 20), inkw=0))
    bg.append(f'<path d="{pd([(-10, 420), (610, 420), (610, 494), (-10, 494)])}" fill="#C8B8A0"/>')
    bg.append(bokeh(D, 22, (0, 180, 600, 470), ["#FFFFFF", "#FFF2C8", "#F8D8E8"], 18, (8, 20), (0.25, 0.5), 2))
    out.append(f'<g filter="url(#{fid})">{"".join(bg)}</g>')
    # the stand's striped awning edge, crisp, across the top, scalloped
    aw = []
    for k in range(-1, 14):
        x = k * 46
        col = ["#E8506A", "#FFFFFF"][k % 2]
        aw.append(f'<path d="M {x} 186 L {x + 46} 186 L {x + 46} 206 Q {x + 23} 226 {x} 206 Z" fill="{col}"/>')
    out.append(f'<path d="M -10 -10 L 610 -10 L 610 190 L -10 190 Z" fill="none"/>')
    out.append("".join(aw))
    out.append(f'<path d="M -10 186 L 610 186" stroke="#B8304A" stroke-width="3"/>')
    out.append(f'<path d="{pd([(-10, 206), (610, 206), (610, 236), (-10, 236)])}" fill="{D.lin([(0, "#2A1A2A", 0.25), (1, "#2A1A2A", 0)])}"/>')
    out.append(oilcloth(D, 494, 23))
    # the glass
    cx, rim_y, bot_y = 300, 330, 524
    H = bot_y - rim_y
    gp = halo_glass_pts(cx, rim_y, bot_y, 88, 64)
    gd = smooth_closed(densify(gp, 10))
    out.append(f'<path d="{blob(cx - 60, bot_y + 6, 110, 16, 24, 0.1, 16)}" fill="#3A2A4A" opacity="0.35"/>')
    out.append(f'<path d="{blob(cx - 70, bot_y + 6, 50, 9, 241, 0.2, 14)}" fill="#E8B8F0" opacity="0.6"/><path d="{blob(cx - 92, bot_y + 6, 16, 4, 242, 0.2, 10)}" fill="#FFFFFF" opacity="0.7"/>')
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
    # lettering
    out.append(letters(D, 300, 112, "halo-halo", SERIF_IT, 120, "#5A2A86", ["#7A42A8", "#3A145E", "#9A62C8"], 41, max_w=440,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#E0C0F8"))
    out.append(ruled(300, 156, "HALUIN BAGO KAININ", "#B8205A", font=JOS, size=20, ls=6, line_w=30, gap=12))
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
    # the barrio street at night, receding to a vanishing point: wooden houses on stone ground floors, every
    # capiz window glowing and hung with its own parol; the wet road catching all of it
    VX, VY = 300, 392
    road = pd([(-10, 610), (610, 610), (VX + 14, VY), (VX - 14, VY)])
    out.append(f'<path d="M -10 {VY} L 610 {VY} L 610 610 L -10 610 Z" fill="#141432"/>')
    out.append(f'<path d="{road}" fill="{D.lin([(0, "#2A2A58"), (1, "#0E0E26")])}"/>')
    cols = [PULA, ("#7AE0A0", "#1E9A5A", "#0A4A2A"), ("#FFB0D8", "#E8509A", "#8A1A5A"), BUGHAW, ("#FFE08A", "#F2A81E", "#8A5A0A")]
    reflections = []
    for side in (-1, 1):
        # houses from far to near: each facade is a trapezoid between two depths
        edges = [0.04, 0.12, 0.24, 0.42, 0.7, 1.05]
        for k in range(len(edges) - 1):
            t0, t1 = edges[k], edges[k + 1]
            def X(t):
                return VX + side * (24 + 420 * t)
            def Yb(t):
                return VY + 240 * t
            def Yt(t, h):
                return VY - h * t
            h = 190 + 34 * ((k + side) % 3)
            x0, x1 = X(t0), X(t1)
            q = [(x0, Yt(t0, h)), (x1, Yt(t1, h)), (x1, Yb(t1)), (x0, Yb(t0))]
            wall = mix(["#3A2E52", "#4A3450", "#2E3456"][(k + (side > 0)) % 3], "#141432", 0.35 * (1 - t1))
            out.append(f'<path d="{pd(q)}" fill="{wall}"/>')
            # stone ground floor, wooden upper floor (planks), eave
            mid = lambda t: VY - 0.32 * h * t + 0.0
            gq = [(x0, mid(t0)), (x1, mid(t1)), (x1, Yb(t1)), (x0, Yb(t0))]
            out.append(f'<path d="{pd(gq)}" fill="#5A5068" opacity="0.55"/>')
            out.append(clipped(D, pd(q), brush_field(260 + k * 7 + side, (min(x0, x1), Yt(t1, h), max(x0, x1), Yb(t1)), ["#5A4A6A", "#1E1A34", "#6A5470"], 30, -90, (10, 40), (1.5, 4), (0.15, 0.35))))
            # a corrugated roof sloping up from the eave, seen from the street
            r0, r1 = Yt(t0, h), Yt(t1, h)
            roof = [(x0 - side * 6 * t0, r0 + 4 * t0), (x1 - side * 10 * t1, r1 + 8 * t1), (x1 + side * 40 * t1, r1 - 60 * t1), (x0 + side * 40 * t0, r0 - 60 * t0)]
            out.append(f'<path d="{pd(roof)}" fill="#22203E"/>')
            out.append(f'<path d="M {roof[0][0]:.1f} {roof[0][1]:.1f} L {roof[1][0]:.1f} {roof[1][1]:.1f}" stroke="#6A6A9A" stroke-width="{1 + 2 * t1:.1f}" opacity="0.6"/>')
            # two capiz windows upstairs, warm light, a parol in each
            for wi, (u0, u1) in enumerate(((0.18, 0.44), (0.56, 0.82))):
                xa, xb = x0 + (x1 - x0) * u0, x0 + (x1 - x0) * u1
                ta, tb = t0 + (t1 - t0) * u0, t0 + (t1 - t0) * u1
                wq = [(xa, VY - 0.86 * h * ta), (xb, VY - 0.86 * h * tb), (xb, VY - 0.48 * h * tb), (xa, VY - 0.48 * h * ta)]
                out.append(f'<path d="{pd(wq)}" fill="#FFCF7A"/>')
                out.append(f'<path d="{pd(wq)}" fill="{D.lin([(0, "#FFF0C8", 0.6), (1, "#E8903A", 0.5)])}"/>')
                cw = abs(xb - xa)
                for j in range(1, 4):
                    xx = xa + (xb - xa) * j / 4
                    out.append(f'<path d="M {xx:.1f} {VY - 0.86 * h * (ta + (tb - ta) * j / 4):.1f} L {xx:.1f} {VY - 0.48 * h * (ta + (tb - ta) * j / 4):.1f}" stroke="#6A4020" stroke-width="{max(0.8, cw * 0.05):.1f}" opacity="0.7"/>')
                wc = ((xa + xb) / 2, VY - 0.67 * h * (ta + tb) / 2)
                out.append(soft_glow(D, wc[0], wc[1], max(16, cw * 1.6), "#FFC060", 0.5))
                pr = max(4, cw * 0.32)
                out.append(parol_small(D, wc[0], wc[1] - pr * 0.1, pr, 300 + k * 10 + wi + (side > 0) * 50, cols[(k * 2 + wi + (side > 0)) % 5]))
                reflections.append((wc[0], cw, Yb((ta + tb) / 2)))
    # reflections of every lit window on the wet road
    for (x, cw, yb) in reflections:
        out.append(vstreaks(int(x), x - (x - VX) * 0.05, yb + 2, yb + 6 + cw * 2.2, max(1.5, cw * 0.16), "#FFC870", 0.45, 3, max(1.5, cw * 0.12)))
    fid = D.nid()
    D.defs.append(soft_filter(fid, 8))
    out.append(f'<path d="{blob(300, VY - 6, 300, 26, 251, 0.2, 18)}" fill="#8A8AC8" opacity="0.35" filter="url(#{fid})"/>')
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
    out.append(soft_glow(D, pcx, pcy, R * 2.6, "#FFE0A0", 0.45))
    rays = "".join(f"M{pcx:.1f} {pcy:.1f}L{pcx + math.cos(a) * R * 2.4:.1f} {pcy + math.sin(a) * R * 2.4:.1f}" for a in [i / 16 * math.pi * 2 + 0.1 for i in range(16)])
    fidr = D.nid()
    D.defs.append(soft_filter(fidr, 4))
    out.append(f'<path d="{rays}" stroke="#FFE8B0" stroke-width="6" opacity="0.18" filter="url(#{fidr})"/>')
    out.append(parol(D, pcx, pcy, R, 231))
    # lettering at the foot
    out.append(letters(D, 300, 484, "Maligayang Pasko", SERIF_IT, 76, "#FFE7A8", ["#FFFFFF", "#FFD878", "#FFF0C0"], 232, max_w=460,
                       shadow="#05051A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 524, "SIMULA SETYEMBRE", "#F2A8C8", font=JOS, size=18, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 233, "#0A0A2A", 0.6)


def chrome(D, pts, seed, inkw=1.2, vertical=False):
    d = smooth_closed(pts)
    g = D.lin([(0, "#FFFFFF"), (0.35, "#C8D0DA"), (0.55, "#6A7484"), (0.75, "#E8EEF4"), (1, "#8A94A4")], 0, 0, 1 if vertical else 0, 0 if vertical else 1)
    return f'<path d="{d}" fill="{g}"/>' + (ink(d, "#2A2E38", inkw, seed, 1, 0.7) if inkw else "")



# ================================================================ 5. ingat! — a jeepney coming home at dusk, after the rain
DUSK_SKY = [(0, "#26245E"), (0.2, "#4A3478"), (0.38, "#8A4688"), (0.52, "#D0608A"), (0.6, "#F28E6E"), (0.655, "#FFC88E")]


def chrome_dusk(D, pts, seed, inkw=0.0, vertical=False, warm=1.0):
    """Chrome painted as the world it mirrors: violet sky on top, a hot sunset line, dark wet street below."""
    d = smooth_closed(pts) if len(pts) > 4 else pd(pts)
    hot = mix("#FFE6B0", "#C8B8D8", 1 - warm)
    if vertical:
        g = D.lin([(0, "#6A4E9A"), (0.3, "#E89AB0"), (0.46, hot), (0.5, "#FFFFFF"), (0.56, "#5A3A4A"), (0.8, "#2A1E2A"), (1, "#7A5A6A")], 0, 0, 1, 0)
    else:
        g = D.lin([(0, "#5A4A8A"), (0.32, "#D88AA8"), (0.46, hot), (0.52, "#FFFFFF"), (0.6, "#4A2E3E"), (0.85, "#24182A"), (1, "#8A6A6A")])
    out = f'<path d="{d}" fill="{g}"/>'
    if inkw:
        out += soft_ink(d, "#24182A", inkw, seed, 1, 0.6)
    return out


def _aff(C, X, Y, Z, ux=(1, 0, 0), vy=(0, -1, 0), unit=0.01):
    """SVG matrix that maps local centimetre coords (u along `ux`, v along `vy`) on a plane to the screen."""
    o = C(X, Y, Z)
    a = C(X + ux[0], Y + ux[1], Z + ux[2])
    b = C(X + vy[0], Y + vy[1], Z + vy[2])
    return (f"matrix({(a[0] - o[0]) * unit:.4f} {(a[1] - o[1]) * unit:.4f} {(b[0] - o[0]) * unit:.4f} {(b[1] - o[1]) * unit:.4f} "
            f"{o[0]:.2f} {o[1]:.2f})")


def _face(C, pts3):
    return [C(*p) for p in pts3]


def _paint_face(D, pts, base, seed, top=None, bottom=None, angle=0.0, cols=None, n=None, sw=(1.5, 4), sl=(14, 46), op=(0.12, 0.32)):
    d = pd(pts)
    out = [f'<path d="{d}" fill="{base}"/>']
    if top or bottom:
        out.append(f'<path d="{d}" fill="{D.lin([(0, top or base, 0.85 if top else 0), (0.55, base, 0), (1, bottom or base, 0.8 if bottom else 0)])}"/>')
    if cols:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        n = n or max(8, int((max(xs) - min(xs)) * (max(ys) - min(ys)) / 140))
        out.append(clipped(D, d, brush_field(seed, (min(xs) - 20, min(ys) - 4, max(xs) + 4, max(ys) + 4), cols, n, angle, sl, sw, op, 0.12, 6)))
    return "".join(out)


def jeep34(D, C, seed, mirror=False):
    """A passenger jeepney in 3/4 front view, painted against a sunset. C = Cam3 (world metres: X along the jeep
    from the open back (0) to the front bumper (6.25), Y up, Z across, near side at Z = -1)."""
    if mirror:
        C0 = C
        C = lambda X, Y, Z: C0(X, -Y, Z)
    rnd = random.Random(seed)
    out = []
    F = lambda pts3: _face(C, pts3)
    ang = math.degrees(math.atan2(C(4, 1, -1)[1] - C(0, 1, -1)[1], C(4, 1, -1)[0] - C(0, 1, -1)[0]))
    # ---- shadow under the jeep (on the wet street) and the dark chassis
    if not mirror:
        sh = F([(-0.3, 0, -1.25), (6.5, 0, -1.25), (6.5, 0, 1.2), (-0.3, 0, 1.2)])
        out.append(f'<path d="{smooth_closed(sh)}" fill="#120A16" opacity="0.55"/>')
    out.append(f'<path d="{pd(F([(0.1, 0.25, -0.95), (6.0, 0.25, -0.95), (6.0, 0.62, -0.95), (0.1, 0.62, -0.95)]))}" fill="#160E18"/>')
    # far wheels peeking under the body
    for wx in (1.05, 5.15):
        pts = [C(wx + 0.42 * math.cos(t / 12 * math.pi * 2), 0.42 + 0.42 * math.sin(t / 12 * math.pi * 2), 0.95) for t in range(12)]
        out.append(f'<path d="{smooth_closed(pts)}" fill="#0E080E"/>')
    # ---- passenger body, near side
    side = F([(0, 0.55, -1), (4.28, 0.55, -1), (4.28, 1.98, -1), (0, 1.98, -1)])
    cream = "#8E7E9C"
    out.append(_paint_face(D, side, cream, seed + 1, top="#E8B8B4", bottom="#2E2244", angle=ang,
                           cols=["#B8A0B0", "#6A5A84", "#A88AA0", "#54466E", "#D0A8A8"], sw=(1.2, 3.4), sl=(16, 60), n=260))
    # grime and road spray along the bottom of the body
    lowq = F([(0, 0.55, -1.003), (4.28, 0.55, -1.003), (4.28, 0.8, -1.003), (0, 0.8, -1.003)])
    out.append(clipped(D, pd(lowq), brush_field(seed + 2, (min(p[0] for p in lowq) - 10, min(p[1] for p in lowq), max(p[0] for p in lowq), max(p[1] for p in lowq) + 4),
                                                 ["#4A3A50", "#6A5060", "#3A2A40"], 70, ang - 90, (4, 14), (0.8, 2), (0.15, 0.4), 0.2, 20)))
    # wheel arch of the rear wheel cut into the skirt
    arch = [C(1.05 + 0.53 * math.cos(math.radians(a)), 0.43 + 0.5 * math.sin(math.radians(a)), -1.0) for a in range(0, 181, 15)]
    # window band (open windows): interior, far windows full of sunset, passengers against the light
    wb = F([(0.22, 1.27, -1), (4.12, 1.27, -1), (4.12, 1.78, -1), (0.22, 1.78, -1)])
    inner = [f'<path d="{pd(wb)}" fill="#2A1A2E"/>']
    far = F([(-0.8, 1.16, 1), (4.1, 1.16, 1), (4.1, 1.8, 1), (-0.8, 1.8, 1)])
    inner.append(f'<path d="{pd(far)}" fill="{D.lin([(0, "#E86A86"), (0.5, "#FFB27A"), (1, "#FFE0A0")])}"/>')
    inner.append(f'<path d="{pd(F([(-0.8, 1.66, 1), (4.1, 1.66, 1), (4.1, 1.8, 1), (-0.8, 1.8, 1)]))}" fill="#B8507A" opacity="0.7"/>')
    inner.append(f'<path d="{pd(F([(-0.8, 1.16, 1), (4.1, 1.16, 1), (4.1, 1.27, 1), (-0.8, 1.27, 1)]))}" fill="#3A2438"/>')
    # far-side posts
    for k in range(9):
        x = 0.3 + k * 0.475
        inner.append(f'<path d="{pd(F([(x - 0.03, 1.28, 1), (x + 0.03, 1.28, 1), (x + 0.03, 1.8, 1), (x - 0.03, 1.8, 1)]))}" fill="#3A2438"/>')
    # ceiling, with a strip of coloured interior lights
    inner.append(f'<path d="{pd(F([(0.22, 1.78, -1), (4.12, 1.78, -1), (4.12, 1.86, 1), (0.22, 1.86, 1)]))}" fill="#3A2440"/>')
    for k in range(14):
        x = 0.35 + k * 0.27
        col = ["#FF5A8A", "#5AD8FF", "#FFE05A", "#8AFF7A"][k % 4]
        p = C(x, 1.8, 0.0)
        inner.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.2" fill="{col}"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{col}" opacity="0.25"/>')
    # passengers on the bench along the far side, seen against the far windows (head, neck, shoulders)
    if not mirror:
        for k in range(8):
            x = 0.35 + k * 0.5 + rnd.uniform(-0.08, 0.08)
            if k in (2, 6):
                continue
            hy = 1.58 + rnd.uniform(-0.03, 0.04)
            z = 0.62
            hc = C(x, hy, z)
            sc = C(x, hy - 0.2, z)
            s_ = abs(C(x, hy + 0.1, z)[1] - hc[1])          # px per 10 cm
            hr = s_ * 1.0
            col = rnd.choice(["#2A1824", "#33202C", "#24162A"])
            sh_w = s_ * 2.3
            body = [(sc[0] - sh_w, sc[1] + s_ * 3), (sc[0] - sh_w, sc[1] + s_ * 0.6), (sc[0] - sh_w * 0.55, sc[1] - s_ * 0.2),
                    (hc[0] - hr * 0.4, hc[1] + hr * 1.3), (hc[0] + hr * 0.4, hc[1] + hr * 1.3), (sc[0] + sh_w * 0.55, sc[1] - s_ * 0.2),
                    (sc[0] + sh_w, sc[1] + s_ * 0.6), (sc[0] + sh_w, sc[1] + s_ * 3)]
            inner.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
            tilt = rnd.uniform(-12, 12)
            inner.append(f'<path d="{blob(hc[0], hc[1], hr * 0.82, hr, seed + 40 + k, 0.05, 12, tilt)}" fill="{col}"/>')
            if rnd.random() < 0.5:   # hair bun / cap / long hair variation
                inner.append(f'<path d="{blob(hc[0] - hr * 0.5, hc[1] - hr * 0.3, hr * 0.42, hr * 0.42, seed + 60 + k, 0.08, 10)}" fill="{col}"/>')
            inner.append(f'<path d="{blob(hc[0] - hr * 0.55, hc[1] - hr * 0.1, hr * 0.18, hr * 0.6, seed + 70 + k, 0.1, 8)}" fill="#FFB27A" opacity="0.55"/>')
    out.append(clipped(D, pd(wb), inner))
    # near-side window posts (chrome)
    for k in range(9):
        x = 0.25 + k * 0.48
        out.append(chrome_dusk(D, F([(x - 0.035, 1.26, -1.01), (x + 0.035, 1.26, -1.01), (x + 0.035, 1.8, -1.01), (x - 0.035, 1.8, -1.01)]), seed + k, vertical=True))
    # lower art panel: stripes, scrollwork, flowers and the jeep's name
    stripes = [(1.15, 1.2, "#C23040"), (1.1, 1.14, "#E8B83A"), (1.05, 1.09, "#2A4AA0"), (0.7, 0.74, "#2A4AA0"), (0.64, 0.68, "#C23040")]
    for y0, y1, c in stripes:
        q = F([(0.02, y0, -1.005), (4.26, y0, -1.005), (4.26, y1, -1.005), (0.02, y1, -1.005)])
        out.append(f'<path d="{pd(q)}" fill="{c}"/>')
    # top band of little painted stars between windows and roof
    for k in range(16):
        x = 0.2 + k * 0.26
        p = C(x, 1.885, -1.005)
        r = abs(C(x, 1.93, -1)[1] - p[1])
        out.append(f'<path d="M {p[0]:.1f} {p[1] - r:.1f} L {p[0] + r * 0.3:.1f} {p[1]:.1f} L {p[0]:.1f} {p[1] + r:.1f} L {p[0] - r * 0.3:.1f} {p[1]:.1f} Z" fill="{["#E8B83A", "#C23040", "#2A4AA0"][k % 3]}"/>')
    # scrollwork either side of the name
    for sx in (0.55, 3.55):
        for sg in (1, -1):
            pts = [C(sx + sg * t * 0.5, 0.9 + 0.08 * math.sin(t * 7) * (1 - t * 0.4), -1.006) for t in [i / 10 for i in range(11)]]
            out.append(f'<path d="{smooth_open(pts)}" fill="none" stroke="#2E7A4A" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>')
        fc = C(sx, 0.9, -1.006)
        fr = abs(C(sx, 0.98, -1)[1] - fc[1])
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<path d="{blob(fc[0] + math.cos(a) * fr * 0.7, fc[1] + math.sin(a) * fr * 0.7, fr * 0.55, fr * 0.38, seed + j, 0.1, 8, math.degrees(a))}" fill="#D8407A"/>')
        out.append(f'<circle cx="{fc[0]:.1f}" cy="{fc[1]:.1f}" r="{fr * 0.32:.1f}" fill="#F2C23A"/>')
    if not mirror:
        m = _aff(C, 2.05, 0.82, -1.006)
        out.append(f'<g transform="{m}"><text x="3" y="3" text-anchor="middle" {SERIF_IT} font-size="30" fill="#5A0E1A" opacity="0.7">Pamilya</text>'
                   f'<text x="0" y="0" text-anchor="middle" {SERIF_IT} font-size="30" fill="#C82A3A">Pamilya</text>'
                   f'<text x="-1" y="-1.5" text-anchor="middle" {SERIF_IT} font-size="30" fill="none" stroke="#FFE6A0" stroke-width="0.8" opacity="0.8">Pamilya</text></g>')
    # skirt: dark rubbing strip with chrome moulding, the open back's step
    out.append(chrome_dusk(D, F([(0, 0.55, -1.01), (4.28, 0.55, -1.01), (4.28, 0.62, -1.01), (0, 0.62, -1.01)]), seed + 30))
    out.append(f'<path d="{smooth_closed(arch + [arch[-1], arch[0]])}" fill="#130A14"/>')
    out.append(f'<path d="{smooth_open([C(1.05 + 0.56 * math.cos(math.radians(a)), 0.43 + 0.53 * math.sin(math.radians(a)), -1.015) for a in range(0, 181, 15)])}" '
               f'fill="none" stroke="{D.lin([(0, "#FFF0D0"), (0.5, "#C890B0"), (1, "#3A2A3A")], 0, 0, 0, 1)}" stroke-width="4.5" stroke-linecap="round"/>')
    # tail lamp on the back corner
    tl = C(0.02, 0.78, -0.98)
    out.append(f'<ellipse cx="{tl[0]:.1f}" cy="{tl[1]:.1f}" rx="3" ry="6" fill="#FF4A3A"/>')
    if not mirror:
        out.append(soft_glow(D, tl[0] - 2, tl[1], 26, "#FF4A3A", 0.5))
    # rim light: the sunset catches the top edge of the body
    if not mirror:
        out.append(dry_brush(seed + 5, [C(0.0, 1.97, -1.01), C(2.0, 1.97, -1.01), C(4.28, 1.97, -1.01)], 3, "#FFD8A8", 0.9, 4))
    # ---- roof: fascia with the route board, overhanging visor, chrome rack
    fas = F([(-0.12, 1.97, -1.06), (4.78, 1.97, -1.06), (4.78, 2.2, -1.06), (-0.12, 2.2, -1.06)])
    out.append(_paint_face(D, fas, "#22357A", seed + 6, top="#6A5AA8", bottom="#121A44", angle=ang, cols=["#3A5AB0", "#141C48"], sw=(1, 2.4)))
    if not mirror:
        m = _aff(C, 2.33, 2.03, -1.065)
        out.append(f'<g transform="{m}"><text x="0" y="0" text-anchor="middle" {ANTON} font-size="17" letter-spacing="3" fill="#FFF2D0">TRABAHO · BAHAY</text></g>')
    out.append(dry_brush(seed + 7, [C(-0.12, 2.2, -1.06), C(4.78, 2.2, -1.06)], 2.4, "#FFC890", 0.8, 3))
    vis = F([(4.78, 1.97, -1.06), (4.78, 1.97, 1.06), (4.78, 2.2, 1.06), (4.78, 2.2, -1.06)])
    out.append(_paint_face(D, vis, "#1A2A64", seed + 8, top="#3A3A80", bottom="#0E1434"))
    if not mirror:
        m = _aff(C, 4.785, 2.035, 0.0, ux=(0, 0, 1))
        out.append(f'<g transform="{m}"><text x="0" y="0" text-anchor="middle" {SERIF_IT} font-size="15" fill="#FFD46A">Ingat Lagi</text></g>')
    for k in range(11):
        x = -0.05 + k * 0.48
        out.append(chrome_dusk(D, F([(x - 0.02, 2.2, -1.0), (x + 0.02, 2.2, -1.0), (x + 0.02, 2.36, -1.0), (x - 0.02, 2.36, -1.0)]), seed, vertical=True))
    out.append(chrome_dusk(D, F([(-0.1, 2.33, -1.0), (4.75, 2.33, -1.0), (4.75, 2.38, -1.0), (-0.1, 2.38, -1.0)]), seed + 9))
    # ---- cab: open driver's side, the driver as a backlit shape, windshield full of sky
    cab = F([(4.28, 0.55, -1), (4.62, 0.55, -1), (4.62, 1.97, -1), (4.28, 1.97, -1)])
    out.append(_paint_face(D, cab, cream, seed + 10, top="#F2D6C8", bottom="#6A5A7A"))
    door = F([(4.32, 1.0, -1.002), (4.6, 1.0, -1.002), (4.6, 1.8, -1.002), (4.32, 1.8, -1.002)])
    out.append(f'<path d="{pd(door)}" fill="#24162A"/>')
    ws = F([(4.62, 1.26, -0.86), (4.62, 1.26, 0.86), (4.62, 1.94, 0.86), (4.62, 1.94, -0.86)])
    out.append(f'<path d="{pd(ws)}" fill="{D.lin([(0, "#8A5A9A"), (0.5, "#E88AA0"), (1, "#3A2A4A")], 0, 0, 0.4, 1)}"/>')
    out.append(f'<path d="{pd(F([(4.621, 1.26, -0.03), (4.621, 1.26, 0.03), (4.621, 1.94, 0.03), (4.621, 1.94, -0.03)]))}" fill="#2A1E2E"/>')
    if not mirror:
        # driver's silhouette behind the glass, and a hanging rosary
        dc = C(4.4, 1.6, -0.45)
        s_ = abs(C(4.4, 1.7, -0.45)[1] - dc[1])
        out.append(clipped(D, pd(ws), [f'<path d="{blob(dc[0], dc[1], s_ * 0.85, s_ * 1.0, seed + 11, 0.05, 12)}" fill="#2A1A2A"/>',
                                       f'<path d="{smooth_closed([(dc[0] - s_ * 2.4, dc[1] + s_ * 3), (dc[0] - s_ * 2.2, dc[1] + s_ * 1.2), (dc[0] - s_ * 0.5, dc[1] + s_ * 0.9), (dc[0] + s_ * 0.5, dc[1] + s_ * 0.9), (dc[0] + s_ * 2.2, dc[1] + s_ * 1.2), (dc[0] + s_ * 2.4, dc[1] + s_ * 3)])}" fill="#2A1A2A"/>',
                                       dry_brush(seed + 12, [C(4.63, 1.9, -0.8), C(4.63, 1.3, 0.2)], 6, "#FFFFFF", 0.35, 3)]))
        rp = C(4.6, 1.9, 0.2)
        out.append(f'<path d="M {rp[0]:.1f} {rp[1]:.1f} q -3 10 0 18" stroke="#E8C86A" stroke-width="1.2" fill="none"/>')
    for z in (-0.88, 0.88):
        out.append(chrome_dusk(D, F([(4.62, 1.24, z - 0.03), (4.62, 1.24, z + 0.03), (4.62, 1.97, z + 0.03), (4.62, 1.97, z - 0.03)]), seed, vertical=True))
    # ---- hood (long, flat) with chrome trim, fenders over the front wheels
    hood_side = F([(4.62, 0.74, -0.8), (6.0, 0.74, -0.8), (6.0, 1.16, -0.8), (4.62, 1.22, -0.8)])
    out.append(_paint_face(D, hood_side, "#B8243A", seed + 13, top="#F07A7A", bottom="#5A0E2A", angle=ang, cols=["#E85A6A", "#7A1030", "#FF9A8A"]))
    hood_top = F([(4.62, 1.22, -0.8), (6.0, 1.16, -0.8), (6.0, 1.16, 0.8), (4.62, 1.22, 0.8)])
    out.append(_paint_face(D, hood_top, "#E86A6A", seed + 14, top="#FFB08A", bottom="#B8304A", angle=ang, cols=["#FFC0A0", "#C8405A"]))
    out.append(chrome_dusk(D, F([(4.62, 1.215, -0.0), (6.0, 1.155, -0.0), (6.0, 1.155, 0.06), (4.62, 1.215, 0.06)]), seed + 15))
    out.append(chrome_dusk(D, F([(4.62, 0.98, -0.805), (6.0, 0.98, -0.805), (6.0, 1.03, -0.805), (4.62, 1.03, -0.805)]), seed + 16))
    for k in range(5):     # hood louvres
        x = 4.85 + k * 0.12
        out.append(f'<path d="{pd(F([(x, 0.8, -0.806), (x + 0.05, 0.8, -0.806), (x + 0.05, 0.94, -0.806), (x, 0.94, -0.806)]))}" fill="#5A0A20"/>')
    out.append(dry_brush(seed + 17, [C(4.62, 1.22, -0.8), C(6.0, 1.16, -0.8)], 2.4, "#FFD0A0", 0.9, 3))
    # near fender: flat top, side skirt and the front wheel arch
    fen_top = F([(4.5, 0.95, -1.0), (6.05, 0.95, -1.0), (6.05, 0.95, -0.78), (4.5, 0.95, -0.78)])
    fen_side = F([(4.5, 0.55, -1.0), (6.05, 0.55, -1.0), (6.05, 0.95, -1.0), (4.5, 0.95, -1.0)])
    out.append(_paint_face(D, fen_side, "#2A4AA0", seed + 18, top="#6A7ACC", bottom="#141E50"))
    out.append(f'<path d="{pd(fen_top)}" fill="#7A86D0"/>')
    farch = [C(5.15 + 0.53 * math.cos(math.radians(a)), 0.43 + 0.5 * math.sin(math.radians(a)), -1.002) for a in range(0, 181, 15)]
    out.append(f'<path d="{smooth_closed(farch + [farch[-1], farch[0]])}" fill="#120A14"/>')
    out.append(f'<path d="{smooth_open([C(5.15 + 0.56 * math.cos(math.radians(a)), 0.43 + 0.53 * math.sin(math.radians(a)), -1.01) for a in range(0, 181, 15)])}" '
               f'fill="none" stroke="{D.lin([(0, "#FFF0D0"), (0.5, "#C890B0"), (1, "#3A2A3A")], 0, 0, 0, 1)}" stroke-width="5" stroke-linecap="round"/>')
    out.append(dry_brush(seed + 19, [C(4.5, 0.95, -1.0), C(6.05, 0.95, -1.0)], 2, "#FFE0B0", 0.9, 3))
    # ---- wheels (near side): tyre, chrome hubcap mirroring the sunset, lug nuts
    for k, wx in enumerate((1.05, 5.15)):
        tyre = [C(wx + 0.43 * math.cos(t / 20 * math.pi * 2), 0.43 + 0.43 * math.sin(t / 20 * math.pi * 2), -0.98) for t in range(20)]
        tread = [C(wx + 0.43 * math.cos(t / 20 * math.pi * 2), 0.43 + 0.43 * math.sin(t / 20 * math.pi * 2), -0.72) for t in range(20)]
        out.append(f'<path d="{smooth_closed(tread)}" fill="#120C12"/>')
        out.append(f'<path d="{smooth_closed(tyre)}" fill="#1E161E"/>')
        out.append(f'<path d="{smooth_open([C(wx + 0.41 * math.cos(math.radians(a)), 0.43 + 0.41 * math.sin(math.radians(a)), -0.99) for a in range(100, 200, 10)])}" fill="none" stroke="#8A6A8A" stroke-width="2" opacity="0.7"/>')
        hub = [C(wx + 0.25 * math.cos(t / 18 * math.pi * 2), 0.43 + 0.25 * math.sin(t / 18 * math.pi * 2), -0.995) for t in range(18)]
        out.append(chrome_dusk(D, hub, seed + 20 + k))
        for j in range(6):
            a = j / 6 * math.pi * 2
            p = C(wx + 0.14 * math.cos(a), 0.43 + 0.14 * math.sin(a), -1.0)
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1.6" fill="#2A1E2A"/>')
        c0 = C(wx, 0.43, -1.0)
        out.append(f'<circle cx="{c0[0]:.1f}" cy="{c0[1]:.1f}" r="3.2" fill="#FFF0D8"/>')
    # mud flap with a painted star
    mf = F([(1.6, 0.12, -0.98), (1.72, 0.12, -0.98), (1.72, 0.58, -0.98), (1.6, 0.58, -0.98)])
    out.append(f'<path d="{pd(mf)}" fill="#8A1A2A"/>')
    # ---- front: grille, headlights (on), bumper with fog lamps
    gr = F([(6.0, 0.62, -0.62), (6.0, 0.62, 0.62), (6.0, 1.16, 0.62), (6.0, 1.16, -0.62)])
    out.append(f'<path d="{pd(gr)}" fill="#2A1A2A"/>')
    for k in range(9):
        z = -0.5 + k * 0.125
        out.append(chrome_dusk(D, F([(6.01, 0.66, z - 0.025), (6.01, 0.66, z + 0.025), (6.01, 1.12, z + 0.025), (6.01, 1.12, z - 0.025)]), seed + k, vertical=True))
    fface = F([(6.05, 0.55, -1.0), (6.05, 0.55, -0.62), (6.05, 0.95, -0.62), (6.05, 0.95, -1.0)])
    out.append(f'<path d="{pd(fface)}" fill="#1E2E6A"/>')
    lights = []
    for z in (-0.81, 0.81):
        c = C(6.06, 0.8, z)
        r = abs(C(6.06, 0.92, z)[1] - c[1])
        rx = abs(C(6.06, 0.8, z + 0.12)[0] - c[0])
        lights.append((c, r, rx))
        out.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx * 1.15:.1f}" ry="{r * 1.15:.1f}" fill="{D.lin([(0, "#FFFFFF"), (0.5, "#8A7A9A"), (1, "#2A1E2A")])}"/>')
        out.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx:.1f}" ry="{r:.1f}" fill="#FFF8DC"/>')
    bump = F([(6.05, 0.4, -1.08), (6.28, 0.4, -1.08), (6.28, 0.4, 1.08), (6.28, 0.6, 1.08), (6.28, 0.6, -1.08), (6.05, 0.6, -1.08)])
    out.append(chrome_dusk(D, F([(6.28, 0.4, -1.08), (6.28, 0.4, 1.08), (6.28, 0.6, 1.08), (6.28, 0.6, -1.08)]), seed + 31))
    out.append(chrome_dusk(D, F([(6.05, 0.4, -1.08), (6.28, 0.4, -1.08), (6.28, 0.6, -1.08), (6.05, 0.6, -1.08)]), seed + 32))
    for z in (-0.45, 0.45):
        c = C(6.3, 0.7, z)
        out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="5" fill="#FFE8A0"/>')
        lights.append((c, 4, 4))
    # ---- hood ornaments: a pair of chrome horses rearing, antennas with streamers, side mirror on its long arm
    for k, (hx, hz) in enumerate(((5.45, -0.3), (5.8, 0.25))):
        b = C(hx, 1.17, hz)
        s_ = abs(C(hx, 1.27, hz)[1] - b[1]) * 10 * 0.33 / 32 / 1.6
        horse = [(-7, 0), (-7.5, -6), (-6.5, -11), (-9, -14), (-13, -12), (-15, -9), (-14, -14), (-10, -18), (-5, -19), (0, -19),
                 (4, -22), (6, -28), (8.5, -33), (9.5, -36), (10.5, -33), (13.5, -31), (16, -27), (14.5, -25.5), (11, -27), (9, -22),
                 (9, -17), (13, -19), (16, -16), (14.5, -14), (11, -15.5), (7, -13.5), (2, -14), (-3, -13.5), (-4, -9), (-3, -4), (-2.2, 0)]
        out.append(chrome_dusk(D, [(b[0] + x * s_ * 1.6, b[1] + y * s_ * 1.6) for x, y in horse], seed + 33 + k, vertical=True))
    for k, (ax, az, col) in enumerate(((5.95, -0.9, "#F2C23A"), (4.7, -1.0, "#C23040"))):
        b = C(ax, 0.95 if k == 0 else 1.97, az)
        t = C(ax - 0.1, 3.3 if k == 0 else 3.2, az)
        out.append(f'<path d="M {b[0]:.1f} {b[1]:.1f} L {t[0]:.1f} {t[1]:.1f}" stroke="#3A2A3A" stroke-width="1.6"/>')
        out.append(taper([t, (t[0] - 14, t[1] + 4), (t[0] - 30, t[1] + 1)], 6, 1, col, 0.95))
        out.append(taper([(t[0], t[1] + 7), (t[0] - 12, t[1] + 12), (t[0] - 26, t[1] + 10)], 5, 1, "#2A4AA0" if k == 0 else "#F2C23A", 0.95))
    ma, mb = C(4.62, 1.55, -1.0), C(4.75, 1.75, -1.42)
    out.append(f'<path d="M {ma[0]:.1f} {ma[1]:.1f} L {mb[0]:.1f} {mb[1]:.1f}" stroke="#3A2A3A" stroke-width="2"/>')
    out.append(chrome_dusk(D, [(mb[0] - 5, mb[1] - 8), (mb[0] + 5, mb[1] - 9), (mb[0] + 6, mb[1] + 6), (mb[0] - 4, mb[1] + 7)], seed + 40, vertical=True))
    return out, lights


def town_row(D, seed, hz):
    """Far side of the street: shophouses, a church tower, palms and power lines against the sunset."""
    out = []
    far = "#5A3A6E"
    near = "#3E2A56"
    # distant church tower with its belfry (left, behind the jeep's tail) and a cross
    tw = [(118, hz), (118, 262), (124, 256), (124, 236), (132, 226), (132, 212), (140, 202), (148, 212), (148, 226), (156, 236), (156, 256), (162, 262), (162, hz)]
    out.append(f'<path d="{smooth_closed(jitter(tw, seed, 0.6))}" fill="{far}"/>')
    out.append(f'<path d="M 140 202 L 140 184 M 134 190 L 146 190" stroke="{far}" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(140, 244, 5, 8, seed, 0.05, 10)}" fill="#FFC88A" opacity="0.85"/>')
    out.append(f'<path d="M 118 262 L 162 262" stroke="#FFB890" stroke-width="2" opacity="0.6"/>')
    # rooflines of shophouses with lit windows
    xs = [-10, 40, 96, 170, 236, 300, 372, 452, 520, 610]
    rnd = random.Random(seed)
    for a, b in zip(xs, xs[1:]):
        top = hz - rnd.uniform(36, 70)
        pts = [(a, hz + 2), (a, top), (b, top), (b, hz + 2)]
        if rnd.random() < 0.5:
            pts = [(a, hz + 2), (a, top + 8), ((a + b) / 2, top - 10), (b, top + 8), (b, hz + 2)]
        out.append(f'<path d="{pd(pts)}" fill="{near}"/>')
        for j in range(rnd.randint(1, 3)):
            wx = rnd.uniform(a + 8, b - 18)
            wy = rnd.uniform(top + 12, hz - 18)
            out.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="9" height="11" fill="#FFCF7A" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
            out.append(soft_glow(D, wx + 4, wy + 5, 20, "#FFB060", 0.3))
    # a hand-painted store sign on the right
    out.append(f'<path d="{pd([(470, hz - 70), (560, hz - 70), (560, hz - 52), (470, hz - 52)])}" fill="#E8D8B8" opacity="0.85"/>')
    out.append(f'<text x="515" y="{hz - 56}" text-anchor="middle" {ANTON} font-size="13" letter-spacing="1" fill="#8A2A3A">SARI-SARI</text>')
    return "".join(out)


@design("ingat")
def ingat():
    D = Doc2("ph-in")
    hz = 392
    C = Cam3(f=760, cx=300, cy=hz, yaw=31, pitch=0, pos=(3.32, 1.5, -11.6))
    out = [sky_paint(D, DUSK_SKY, 301, hz)]
    rs = random.Random(300)
    for k in range(7):
        x, y = rs.uniform(30, 570), rs.uniform(20, 110)
        out.append(sparkle(x, y, rs.uniform(2.5, 4.5), "#FFF6E0", 0.8))
    # the sun has just gone down behind the town on the left: a broad hot glow on the horizon
    out.append(soft_glow(D, 150, hz - 6, 300, "#FFB46A", 0.75))
    out.append(soft_glow(D, 150, hz - 2, 120, "#FFF0C0", 0.8))
    # streaky dusk clouds lit from below
    rnd = random.Random(302)
    for k in range(9):
        y = 240 + k * 15 + rnd.uniform(-5, 5)
        x = rnd.uniform(-60, 520)
        w = rnd.uniform(140, 300)
        col = mix("#FFC8A0", "#C86A9A", k / 9)
        out.append(taper([(x, y), (x + w * 0.4, y - 3), (x + w, y + 2)], 1, rnd.uniform(4, 9), col, rnd.uniform(0.35, 0.6)))
        out.append(taper([(x + 10, y + 4), (x + w * 0.5, y + 3), (x + w * 0.9, y + 5)], 1, 2.4, "#FFE2B8", 0.4))
    out.append(town_row(D, 303, hz))
    out.append(f'<rect x="-10" y="{hz - 30}" width="620" height="34" fill="{D.lin([(0, "#F2A07A", 0), (1, "#F2A07A", 0.35)])}"/>')
    # palms and the power pole with its tangle of wires
    for k, (bx, ty, lean) in enumerate(((36, 236, 10), (566, 252, -12), (598, 286, -6))):
        out.append(palm(D, (bx, hz + 4), (bx + lean, ty), 305 + k, sil="#2E2048", L=74, width=11, nuts=False, leaf_cols=["#2E2048", "#3A2852"]))
    px = 520
    out.append(taper([(px, hz + 30), (px + 2, 228)], 8, 5, "#2A1E3E"))
    for k, w in enumerate((44, 32)):
        y = 240 + k * 16
        out.append(taper([(px - w, y), (px + w, y)], 4, 4, "#2A1E3E"))
    out.append(f'<rect x="{px + 6}" y="282" width="16" height="22" rx="3" fill="#2A1E3E"/>')
    wires = []
    for k, (y0, y1, sag) in enumerate(((242, 300, 30), (246, 330, 40), (258, 320, 24), (262, 350, 34), (240, 286, 18))):
        pts = [(px - 40 + 40 * (k % 2), y0)]
        for t in range(1, 17):
            u = t / 16
            pts.append((px - 40 - (px + 60) * u, y0 + (y1 - y0) * u + sag * 4 * u * (1 - u)))
        wires.append(f'<path d="{smooth_open(pts)}" fill="none" stroke="#2A1E3E" stroke-width="{1.3 + 0.3 * (k % 2):.1f}" opacity="0.85"/>')
        pts2 = [(px + 40, y0 + 2), (px + 70, y0 + 8), (610, y0 + 12)]
        wires.append(f'<path d="{smooth_open(pts2)}" fill="none" stroke="#2A1E3E" stroke-width="1.4" opacity="0.85"/>')
    out.append("".join(wires))
    # wet street: mirror of the sky, darker toward us, with a far lane line and puddles
    road = f"M -10 {hz} L 610 {hz} L 610 610 L -10 610 Z"
    out.append(f'<path d="{road}" fill="{D.lin([(0, "#F6B488"), (0.08, "#B8607A"), (0.35, "#4A2E52"), (1, "#1A1226")])}"/>')
    out.append(clipped(D, road, brush_field(304, (-60, hz, 600, 610), ["#2A1A30", "#6A4060", "#120A18", "#F2A07A"], 160, -6, (40, 160), (1.5, 5), (0.1, 0.35), 0.05, 3)))
    # the jeepney's reflection in the wet street, then the jeepney
    refl, _ = jeep34(D, C, 311, mirror=True)
    D.defs.append(ripple_filter("ph-in-rip", 7, 14, "0.006 0.09", 1.0))
    out.append(f'<g opacity="0.42" filter="url(#ph-in-rip)">{clipped(D, road, refl)}</g>')
    out.append(f'<path d="{road}" fill="{D.lin([(0, "#1A1226", 0), (0.4, "#1A1226", 0.25), (1, "#1A1226", 0.55)])}"/>')
    # puddle glints catching the sunset: small broken dashes, denser near the horizon
    for k in range(16):
        y = hz + 6 + (k / 16) ** 1.8 * 190
        x = rnd.uniform(-40, 560)
        L = rnd.uniform(14, 60) * (0.5 + (y - hz) / 220)
        out.append(taper([(x, y), (x + L * 0.5, y + 0.4), (x + L, y)], 0.6, rnd.uniform(1.2, 2.4), rnd.choice(["#FFC890", "#F28AA0", "#FFE0B0"]), rnd.uniform(0.25, 0.5)))
    jeep, lights = jeep34(D, C, 311)
    out.extend(jeep)
    # headlight glow, beams on the wet street and long reflections
    for (c, r, rx) in lights:
        out.append(soft_glow(D, c[0], c[1], max(r, rx) * 4.5, "#FFF0C0", 0.75))
        out.append(vstreaks(312 + int(c[0]), c[0], c[1] + 2 * (515 - c[1]) * 0.9 - 30, 612, max(rx, 3) * 0.9, "#FFE8B0", 0.8, 6, max(rx, 3) * 0.6))
    lx = (lights[0][0][0] + lights[1][0][0]) / 2
    out.append(f'<ellipse cx="{lx + 40:.1f}" cy="548" rx="150" ry="34" fill="{D.rad([(0, "#FFE8B0", 0.35), (0.6, "#FFC890", 0.12), (1, "#FFC890", 0)])}"/>')
    out.append(letters(D, 300, 150, "Ingat!", SERIF_IT, 138, "#FFF2DC", ["#FFFFFF", "#FFE0C0", "#F8D0B8"], 312, max_w=400,
                       shadow="#1E1640", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 204, "TEXT MO AKO PAG NAKAUWI KA NA", "#FFE6C0", font=JOS, size=18, ls=3, line_w=18, gap=10, max_w=420))
    return finish_b(D, out, 313, "#2A1A3A", 0.5)


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
    out = room_bg(D, 401, "#E8C8AE", 450, light_from=1, window=False, warm="#FFF2DC")
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
    fidb = D.nid()
    D.defs.append(soft_filter(fidb, 7))
    out.append(f'<g filter="url(#{fidb})"><path d="{pd([(396, 222), (520, 222), (360, 560), (150, 560)])}" fill="#FFF2D0" opacity="0.18"/>'
               f'<path d="{pd([(230, 470), (420, 470), (380, 560), (150, 560)])}" fill="#FFE8B8" opacity="0.35"/></g>')
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
    out = room_bg(D, 501, "#8EC0B0", 420, light_from=-1, shelf=302, warm="#FFF6E0")
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
    rnd = random.Random(602)
    # a birthday party: a pastel wall with balloons and banderitas out of focus, the buffet table under a white cloth
    out = room_bg(D, 601, "#F2CFA8", 236, light_from=-1, window=False, warm="#FFF6E0")
    fidp = D.nid()
    D.defs.append(soft_filter(fidp, 4))
    party = [banderitas(D, -20, 200, 620, 204, 18, 14, 6031, size=20)]
    for k, (x, y, c) in enumerate(((36, 196, "#E8506A"), (78, 208, "#F6C51E"), (528, 200, "#3A8AD0"), (570, 190, "#EE6A98"), (486, 212, "#7AC08A"))):
        party.append(f'<ellipse cx="{x}" cy="{y}" rx="26" ry="32" fill="{c}"/><ellipse cx="{x - 8}" cy="{y - 12}" rx="7" ry="10" fill="#FFFFFF" opacity="0.5"/>'
                     f'<path d="M {x} {y + 32} q 6 30 -4 60" stroke="#8A7A6A" stroke-width="1.4" fill="none"/>')
    out.append(f'<g filter="url(#{fidp})">{"".join(party)}</g>')
    cloth = "M -10 236 L 610 236 L 610 610 L -10 610 Z"
    out.append(f'<path d="{cloth}" fill="#F6F0E6"/>')
    out.append(clipped(D, cloth, [brush_field(6032, (-40, 236, 610, 610), ["#FFFFFF", "#D8D0C4", "#E8E0D4"], 90, 3, (40, 140), (2, 6), (0.2, 0.45), 0.05, 3),
                                  f'<path d="{cloth}" fill="{D.lin([(0, "#8A7A6A", 0.25), (0.3, "#8A7A6A", 0), (1, "#5A4A3A", 0.2)])}"/>']))
    out.append(f'<path d="M -10 236 L 610 236" stroke="#C8B8A8" stroke-width="2"/>')
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
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#FFE0B0", 0.22), (0.5, "#FFE0B0", 0), (1, "#2A0404", 0.35)], 0, 0, 1, 1)}"/>')
    # the rest of the handaan around the plate, cut by the frame: rice, a glass of iced gulaman, puto
    for k, (x, y, r) in enumerate(((44, 560, 70), (566, 548, 56))):
        out.append(f'<path d="{blob(x + 8, y + 10, r * 1.05, r * 1.0, 7001 + k, 0.05, 18)}" fill="#3A0604" opacity="0.4"/>')
    out.append(painted(D, ell_pts(44, 560, 70, 66, 0, 360, 30)[:-1], WHITE, 7003, sk=0.15, angle=0, n=10, inkw=0, hi=0.4))
    out.append(rice_mound_top(D, 44, 556, 52, 48, 7004))
    out.append(f'<circle cx="566" cy="548" r="56" fill="#E8F2F4" opacity="0.6"/><circle cx="566" cy="548" r="48" fill="#C8783A" opacity="0.85"/>')
    for k in range(6):
        x, y = 566 + random.Random(7005 + k).uniform(-30, 30), 548 + random.Random(7015 + k).uniform(-30, 30)
        out.append(f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" rx="4" fill="#FFFFFF" opacity="0.55" transform="rotate({k * 23} {x:.1f} {y:.1f})"/>')
    out.append(f'<circle cx="566" cy="548" r="56" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.7"/><path d="M 530 520 A 50 50 0 0 1 590 506" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.8"/>')
    cx, cy, R = 300, 382, 168
    out.append(f'<path d="{blob(cx + 14, cy + 16, R * 1.02, R * 1.0, 7020, 0.03, 24)}" fill="#3A0604" opacity="0.45"/>')
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


def lechon_pig2(D, X, Y, s, seed):
    """Whole roast pig lying on its belly, facing right, seen a little from above: shoulder and ham read as
    big rounded masses, legs tucked (fore legs forward under the chin, hind legs back), blistered lacquered skin."""
    P = lambda x, y: (X + x * s, Y + y * s)
    PP = lambda pts: [P(x, y) for x, y in pts]
    rnd = random.Random(seed)
    skin = ("#E88A3A", "#A84416", "#4A1204")
    out = [cast(D, X + 20 * s, Y + 58 * s, 280 * s, 24 * s, strength=0.55, seed=seed)]
    # the bamboo spit it was roasted on, through from tail to mouth
    out.append(taper([P(-262, -18), P(-180, -24)], 15 * s, 15 * s, "#C8A860"))
    out.append(taper([P(-262, -22), P(-180, -28)], 4 * s, 4 * s, "#F2E0A0", 0.8))
    out.append(f'<ellipse cx="{P(-262, -18)[0]:.1f}" cy="{P(-262, -18)[1]:.1f}" rx="{4 * s:.1f}" ry="{7.5 * s:.1f}" fill="#E8D8A0" stroke="#7A5A2A" stroke-width="1.2"/>')
    # far legs (behind), darker
    for leg in (((-140, 40), (-196, 48), (-236, 44)), ((140, 36), (190, 50), (230, 46))):
        out.append(taper(PP(leg), 30 * s, 14 * s, "#5A1A08"))
    body = PP([(-206, -2), (-198, -50), (-160, -92), (-80, -114), (0, -118), (80, -112), (136, -96), (172, -74), (190, -40), (186, 24),
               (140, 50), (50, 60), (-60, 60), (-146, 52), (-190, 32)])
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="{skin[1]}"/>')
    inner = [f'<path d="{bd}" fill="{D.lin([(0, "#FFD088", 0.95), (0.18, "#F0963E", 0.7), (0.45, "#B04A16", 0.1), (0.7, "#5A1606", 0.55), (1, "#1E0602", 0.9)], 0, 0, 0, 1)}"/>',
             f'<path d="{bd}" fill="{D.lin([(0, "#2A0802", 0.35), (0.12, "#2A0802", 0), (0.88, "#2A0802", 0), (1, "#2A0802", 0.3)], 0, 0, 1, 0)}"/>']
    # the two big masses: shoulder and ham, each a rounded glossy dome
    for (cx, cy, rx, ry) in ((-150, -40, 80, 76), (120, -44, 74, 70)):
        c = P(cx, cy)
        inner.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx * s:.1f}" ry="{ry * s:.1f}" fill="{D.rad([(0, "#FFC070", 0.4), (0.5, "#C2561C", 0.0), (1, "#C2561C", 0)], 0.4, 0.3, 0.6)}"/>')
    # blistered crackling: many tiny bubbles, light tops and dark undersides
    bub = {"#FFE2A8": [], "#7A2606": [], "#FFC070": []}
    for _ in range(520):
        x, y = rnd.uniform(-220, 200), rnd.uniform(-100, 50)
        r = rnd.uniform(0.9, 2.4) * s
        p = P(x, y)
        bub["#7A2606"].append(f"M{p[0] + r * 0.3:.1f} {p[1] + r * 0.5:.1f}a{r:.1f} {r * 0.7:.1f} 0 1 0 0.1 0Z")
        if y < 10:
            bub[rnd.choice(["#FFE2A8", "#FFC070"])].append(f"M{p[0] - r * 0.2:.1f} {p[1] - r * 0.3:.1f}a{r * 0.7:.1f} {r * 0.5:.1f} 0 1 0 0.1 0Z")
    for c, v in bub.items():
        inner.append(f'<path d="{"".join(v)}" fill="{c}" opacity="{0.55 if c == "#7A2606" else 0.6}"/>')
    # lacquer reflections: a long hot streak along the spine, softer ones on ham and shoulder
    inner.append(taper(PP([(-180, -60), (-130, -96), (-50, -112), (40, -114), (110, -102), (160, -80)]), 7 * s, 4 * s, "#FFF4DC", 0.8))
    inner.append(taper(PP([(-170, -44), (-120, -78), (-40, -92)]), 3 * s, 1.5 * s, "#FFFFFF", 0.7))
    inner.append(taper(PP([(96, -84), (140, -72), (166, -50)]), 4 * s, 1.5 * s, "#FFFFFF", 0.6))
    inner.append(taper(PP([(-200, -10), (-190, 20)]), 3 * s, 1, "#FFD8A0", 0.5))
    out.append(clipped(D, bd, inner))
    out.append(soft_ink(bd, "#3A0E04", 2.4, seed, 2, 0.7))
    # near legs: hind leg stretched back, fore leg folded forward under the chin, hooves dark
    for k, leg in enumerate((((-132, 38), (-194, 54), (-242, 48)), ((138, 34), (196, 56), (240, 50)))):
        lp = limb(P(*leg[0]), P(*leg[1]), P(*leg[2]), 34 * s, 24 * s, 15 * s)
        ld = smooth_closed(lp)
        out.append(f'<path d="{ld}" fill="{skin[1]}"/>')
        out.append(clipped(D, ld, [f'<path d="{ld}" fill="{D.lin([(0, "#FFC070", 0.6), (1, "#2A0802", 0.6)], 0, 0, 0, 1)}"/>',
                                   taper([P(leg[0][0], leg[0][1] - 8), P(leg[1][0], leg[1][1] - 8)], 3 * s, 2 * s, "#FFE8C0", 0.6)]))
        h = P(*leg[2])
        out.append(f'<path d="{blob(h[0] + (6 if k else -6) * s, h[1], 10 * s, 8 * s, seed + k, 0.1, 10)}" fill="#2A0E04"/>')
    # head: forehead, long snout with its flat disc, heavy jowl, closed eye, a crisp ear
    head = PP([(150, -92), (196, -96), (232, -80), (266, -54), (296, -40), (306, -20), (300, 2), (276, 14), (240, 32), (196, 36), (160, 20), (150, -30)])
    hd = smooth_closed(head)
    out.append(f'<path d="{hd}" fill="{skin[1]}"/>')
    hi = [f'<path d="{hd}" fill="{D.lin([(0, "#FFD088", 0.9), (0.3, "#F0963E", 0.4), (0.6, "#7A2008", 0.3), (1, "#1E0602", 0.85)], 0, 0, 0, 1)}"/>',
          f'<path d="{hd}" fill="{D.lin([(0, "#2A0802", 0), (0.8, "#2A0802", 0), (1, "#2A0802", 0.45)], 0, 0, 1, 0)}"/>',
          taper(PP([(166, -84), (220, -82), (262, -58), (296, -40)]), 5 * s, 2 * s, "#FFF4DC", 0.75),
          f'<ellipse cx="{P(214, 10)[0]:.1f}" cy="{P(214, 10)[1]:.1f}" rx="{40 * s:.1f}" ry="{22 * s:.1f}" fill="#2A0802" opacity="0.08"/>']
    for _ in range(110):
        x, y = rnd.uniform(156, 300), rnd.uniform(-90, 30)
        p = P(x, y)
        hi.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{rnd.uniform(0.8, 2) * s:.1f}" fill="{rnd.choice(["#FFE2A8", "#7A2606"])}" opacity="0.5"/>')
    out.append(clipped(D, hd, hi))
    out.append(soft_ink(hd, "#3A0E04", 2.2, seed + 1, 2, 0.7))
    out.append(taper([P(290, -8), P(340, -14)], 15 * s, 15 * s, "#C8A860"))
    out.append(taper([P(290, -12), P(340, -18)], 4 * s, 4 * s, "#F2E0A0", 0.8))
    out.append(f'<ellipse cx="{P(340, -14)[0]:.1f}" cy="{P(340, -14)[1]:.1f}" rx="{4 * s:.1f}" ry="{7.5 * s:.1f}" fill="#E8D8A0" stroke="#7A5A2A" stroke-width="1.2"/>')
    sn = P(303, -19)
    out.append(f'<ellipse cx="{sn[0]:.1f}" cy="{sn[1]:.1f}" rx="{7 * s:.1f}" ry="{15 * s:.1f}" fill="#8A3410"/>'
               f'<ellipse cx="{sn[0] + 1:.1f}" cy="{sn[1] - 5 * s:.1f}" rx="{1.8 * s:.1f}" ry="{3 * s:.1f}" fill="#2A0802"/>'
               f'<ellipse cx="{sn[0] + 1:.1f}" cy="{sn[1] + 5 * s:.1f}" rx="{1.8 * s:.1f}" ry="{3 * s:.1f}" fill="#2A0802"/>'
               f'<path d="M {sn[0] - 6 * s:.1f} {sn[1] - 12 * s:.1f} q {4 * s:.1f} {-2 * s:.1f} {8 * s:.1f} {2 * s:.1f}" stroke="#FFE0B0" stroke-width="2" fill="none" opacity="0.7"/>')
    e = P(222, -52)
    out.append(f'<path d="M {e[0] - 9 * s:.1f} {e[1]:.1f} q {9 * s:.1f} {5 * s:.1f} {18 * s:.1f} {-1 * s:.1f}" stroke="#2A0802" stroke-width="{2.4 * s:.1f}" fill="none" stroke-linecap="round"/>')
    for k in range(4):
        out.append(f'<path d="M {e[0] - 6 * s + k * 4 * s:.1f} {e[1] + 2 * s:.1f} l {-0.5 * s:.1f} {4 * s:.1f}" stroke="#2A0802" stroke-width="1.2" opacity="0.7"/>')
    m = P(270, 16)
    out.append(f'<path d="M {m[0] - 20 * s:.1f} {m[1] + 4 * s:.1f} Q {m[0]:.1f} {m[1] + 2 * s:.1f} {m[0] + 18 * s:.1f} {m[1] - 8 * s:.1f}" stroke="#2A0802" stroke-width="{2 * s:.1f}" fill="none"/>')
    for k, ear in enumerate((PP([(168, -92), (190, -128), (236, -120), (226, -100), (204, -88)]), PP([(184, -88), (214, -118), (256, -104), (240, -86), (214, -80)]))):
        out.append(f'<path d="{smooth_closed(ear)}" fill="{"#6A200A" if k == 0 else "#8A2E0C"}"/>')
        out.append(clipped(D, smooth_closed(ear), [f'<path d="{smooth_closed(ear)}" fill="{D.lin([(0, "#E8823A", 0.8), (1, "#3A0E04", 0.5)], 1, 0, 0, 1)}"/>']))
        out.append(taper([ear[1], ear[2]], 3 * s, 1.5 * s, "#FFE0A8", 0.7))
    return "".join(out)


@design("lechon")
def lechon():
    D = Doc2("ph-lc")
    rnd = random.Random(800)
    # a backyard fiesta in the late afternoon, out of focus behind the table
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#7AB8E0"), (0.45, "#F2D6A8"), (0.7, "#E8B070")])}"/>']
    fid = D.nid()
    D.defs.append(soft_filter(fid, 4.5))
    bg = [soft_glow(D, 470, 250, 260, "#FFE8B0", 0.8)]
    for k, (x, y, rx_, ry_) in enumerate(((40, 330, 150, 120), (250, 360, 140, 90), (470, 320, 160, 120), (620, 360, 120, 100))):
        bg.append(dab_crown(D, x, y, rx_, ry_, [("#9AC870", "#4E8A3A", "#25502A"), ("#B8D880", "#6AA048", "#3A6A2A")], 801 + k, n=100, size=(10, 20), inkw=0))
    bg.append(f'<path d="M -10 410 L 610 410 L 610 470 L -10 470 Z" fill="#8AA860"/>')
    for k in range(3):   # a tent pole and the bamboo arch of the fiesta
        x = [86, 330, 540][k]
        bg.append(taper([(x, 470), (x + 2, 250)], 9, 7, "#C8A868"))
    bg.append(banderitas(D, -20, 250, 620, 262, 40, 16, 812, size=24))
    bg.append(bokeh(D, 805, (0, 200, 600, 420), ["#FFF2C0", "#FFD890", "#FFFFFF"], 16, (6, 16), (0.25, 0.5), 2))
    out.append(f'<g filter="url(#{fid})">{"".join(bg)}</g>')
    # the crisp string of banderitas closest to us
    out.append(banderitas(D, -20, 206, 620, 214, 46, 15, 813, size=26))
    # the long table: banana leaves laid over it
    table = "M -10 444 L 610 444 L 610 610 L -10 610 Z"
    out.append(f'<path d="{table}" fill="#2E5A2A"/>')
    for k, (x, y, ang, L) in enumerate(((-20, 470, 4, 330), (300, 462, -3, 330), (-30, 540, -2, 340), (290, 548, 3, 340), (120, 600, 0, 360))):
        out.append(banana_leaf_lite(D, x, y, ang, L, 50, 806 + k, pal=SAGING))
    out.append(f'<path d="{table}" fill="{D.lin([(0, "#1A2A10", 0.35), (0.3, "#1A2A10", 0), (1, "#1A2A10", 0.3)])}"/>')
    out.append(f'<path d="M -10 444 L 610 444" stroke="#1A3010" stroke-width="3" opacity="0.6"/>')
    out.append(lechon_pig2(D, 268, 452, 0.98, 810))
    # the chopping board up front with crackling already cut (the best part), a bowl of lechon sauce, calamansi
    cb = rot(rect_pts(30, 520, 210, 580, 14, 814, 0.5), 120, 550, -6)
    out.append(cast(D, 126, 584, 100, 12, strength=0.45, seed=815))
    out.append(painted(D, cb, ("#E8C08A", "#C8945A", "#7A5230"), 816, sdir=(0.3, 1), sk=0.2, angle=-6, n=16, inkw=0, hi=0.4))
    for k in range(6):
        x, y = 60 + (k % 3) * 44 + rnd.uniform(-4, 4), 536 + (k // 3) * 22 + rnd.uniform(-3, 3)
        out.append(lechon_chunk(D, x, y, 34, 18, 817 + k, ang=rnd.uniform(-15, 15)))
    out.append(sawsawan(D, 486, 552, 40, 811, sauce="#7A4A1E", bits="vinegar"))
    for k, (x, y) in enumerate(((410, 584), (432, 572), (540, 590))):
        out.append(calamansi(D, x, y, 11, 830 + k, cut=k == 1))
    out.append(letters(D, 300, 140, "lechon", SERIF_IT, 124, "#8A2A0A", ["#A83E14", "#5A1404", "#C85A22"], 820, max_w=380,
                       shadow="#FFF6E8", soff=(0.018, 0.03), angle=-40, hi="#F8B080"))
    out.append(ruled(300, 176, "MALUTONG ANG BALAT", "#1E3A80", font=JOS, size=20, ls=6, line_w=28, gap=12))
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
    out = room_bg(D, 901, "#B8A8C8", 352, table=("#D8A878", "#A87448", "#5A3A1E"), light_from=-1, shelf=262, warm="#FFF0D8")
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
    for k, (x, y) in enumerate(((96, 392), (134, 404), (76, 412))):
        out.append(crinkle(D, x, y, 20, 940 + k))
    # lettering
    out.append(letters(D, 300, 164, "ube", SERIF_IT, 152, "#4A1676", ["#7A3AB0", "#3A0E5E", "#9A5AD0"], 920, max_w=300,
                       shadow="#FFF6FF", soff=(0.018, 0.03), angle=-40, hi="#E0C0FF"))
    out.append(ruled(300, 210, "OO, PURPLE TALAGA", "#8A1A4A", font=JOS, size=21, ls=6, line_w=30, gap=14))
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
    out = [sky_paint(D, [(0, "#9ABCE0"), (0.25, "#F2D2B8"), (0.45, "#FFE2B8")], 1001, 600, n=90)]
    out.append(soft_glow(D, 60, 250, 300, "#FFF6D0", 0.8))
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
    # low morning sun from the left: long soft shadows across the sidewalk, a warm wash over the wall
    out.append(f'<path d="M -10 272 L 610 272 L 610 470 L -10 470 Z" fill="{D.lin([(0, "#FFE0A8", 0.35), (0.6, "#FFE0A8", 0), (1, "#3A3048", 0.2)], 0, 0, 1, 0)}"/>')
    fids = D.nid()
    D.defs.append(soft_filter(fids, 4))
    out.append(f'<g filter="url(#{fids})" fill="#4A3A48" opacity="0.4">'
               f'<path d="{pd([(80, 516), (190, 516), (330, 556), (210, 562)])}"/><path d="{pd([(262, 508), (344, 508), (450, 540), (360, 546)])}"/>'
               f'<path d="{pd([(370, 540), (520, 540), (640, 590), (480, 600)])}"/></g>')
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
    """A rooster crowing on a fence post, backlit by the sunrise: deep chest, hackles, arching sickle feathers,
    comb and wattles, strong legs with spurs, beak open. Silhouette with a warm rim of light."""
    P = lambda a, b: (x + a * s, base + b * s)
    out = []
    # sickle feathers: long arcs sweeping up and over, then down
    for k, (h, L, w) in enumerate(((60, 66, 7), (52, 58, 6), (44, 50, 5), (36, 44, 4.5))):
        pts = [P(-22, -26), P(-40 - k * 2, -h - 6), P(-58 - k * 4, -h + 4), P(-66 - k * 3, -h + 26 + k * 4)]
        out.append(taper(pts, w * s, 1.2 * s, col))
    body = [P(-30, -16), P(-24, -40), P(-6, -48), P(10, -56), P(18, -74), P(24, -86), P(34, -90), P(42, -84), P(40, -72), P(34, -60),
            P(38, -44), P(34, -24), P(20, -8), P(2, -2), P(-18, -4)]
    out.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
    # hackle feathers falling over the shoulders
    for k in range(6):
        out.append(taper([P(14 + k * 2, -70 + k * 4), P(6 + k * 3, -50 + k * 3)], 3 * s, 0.8, mix(col, rim, 0.2)))
    out.append(f'<path d="{smooth_closed([P(26, -88), P(26, -98), P(31, -95), P(34, -102), P(38, -96), P(42, -100), P(43, -90), P(40, -86)])}" fill="#C8241E"/>')
    out.append(f'<path d="{pd([P(43, -84), P(54, -86), P(45, -81), P(53, -77), P(43, -78)])}" fill="#E8A030"/>')
    out.append(f'<path d="{blob(*P(41, -70), 3 * s, 5 * s, seed, 0.1, 8)}" fill="#C8241E"/>')
    out.append(f'<circle cx="{P(36, -84)[0]:.1f}" cy="{P(36, -84)[1]:.1f}" r="{1.2 * s:.1f}" fill="{rim}"/>')
    for (hx, fx) in ((-4, -8), (10, 12)):
        out.append(taper([P(hx, -6), P(hx + 1, 6), P(fx, 16)], 3.4 * s, 2.2 * s, "#C8902A" if False else col))
        out.append(taper([P(fx, 16), P(fx + 8, 17)], 2 * s, 1, col))
        out.append(taper([P(fx, 16), P(fx - 6, 17)], 2 * s, 1, col))
    # rim light along the back, neck and the top of the tail
    out.append(taper([P(-24, -40), P(-6, -48), P(10, -56), P(18, -74), P(24, -86)], 2.2 * s, 1, rim, 0.85))
    out.append(taper([P(-40, -66), P(-58, -56)], 1.6 * s, 0.8, rim, 0.7))
    return "".join(out)


@design("magandang-umaga")
def magandang_umaga():
    D = Doc2("ph-mu")
    out = room_bg(D, 1101, "#EED2AA", 430, light_from=1, window=False, warm="#FFF4DC")
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
    out = room_bg(D, 1201, "#E2C89A", 456, table=NARRA, light_from=1, warm="#FFF6E0", planks=2)
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
    out.append(guitar(D, 336, 484, 0.74, 16, 1330))
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


def paraw(D, cx, wl, s, seed, sil="#22183A", rim="#FFC27A", sail_lit=True):
    """A Visayan paraw (double-outrigger sailing banca) in side view, sailing right, backlit by a low sun:
    dark slender hull with upswept ends, bamboo floats and curved booms, a tall translucent sail glowing."""
    P = lambda x, y: (cx + x * s, wl + y * s)
    PP = lambda pts: [P(x, y) for x, y in pts]
    out = []
    # far float and booms (behind the hull)
    out.append(taper(PP([(-150, -4), (0, -6), (150, -4)]), 5 * s, 5 * s, mix(sil, "#6A5A8A", 0.3)))
    # sail: tall, leaning forward from a yard, patched cloth glowing with the sunset behind it
    mast = (8, -18)
    sail = PP([(-70, -30), (96, -26), (64, -150), (18, -236)])
    sd = pd(sail)
    out.append(f'<path d="{sd}" fill="{D.lin([(0, "#FFE6B8"), (0.5, "#F6B880"), (1, "#E88A6A")], 1, 0, 0, 1)}"/>')
    rnd = random.Random(seed)
    sc = [brush_field(seed, (min(p[0] for p in sail) - 10, min(p[1] for p in sail), max(p[0] for p in sail), max(p[1] for p in sail)),
                      ["#FFF2D0", "#F2A070", "#FFD8A0"], 40, -70, (10, 40), (2, 5), (0.15, 0.4))]
    for k in range(1, 6):   # cloth panels / seams
        t = k / 6
        a, b = sail[0], sail[3]
        c, d_ = sail[1], sail[2]
        p1 = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        p2 = (c[0] + (d_[0] - c[0]) * t, c[1] + (d_[1] - c[1]) * t)
        sc.append(f'<path d="M {p1[0]:.1f} {p1[1]:.1f} L {p2[0]:.1f} {p2[1]:.1f}" stroke="#C8704A" stroke-width="1.2" opacity="0.5"/>')
    sc.append(f'<path d="{pd([P(30, -110), P(60, -106), P(52, -78), P(24, -82)])}" fill="#E8A0A0" opacity="0.35"/>')
    sc.append(f'<path d="{sd}" fill="{D.lin([(0, "#2A1A3A", 0.0), (0.7, "#2A1A3A", 0), (1, "#2A1A3A", 0.35)], 0, 0, 0, 1)}"/>')
    out.append(clipped(D, sd, sc))
    out.append(soft_ink(sd, "#4A2A3A", 1.6, seed, 1, 0.6))
    out.append(taper([P(-74, -30), P(100, -26)], 4 * s, 4 * s, sil))          # boom
    out.append(taper([P(16, -240), P(-70, -30)], 3.5 * s, 3 * s, mix(sil, "#3A2A4A", 0.3)))   # yard along the leading edge
    out.append(taper([P(*mast), P(14, -170)], 4.5 * s, 3 * s, sil))          # mast
    for (a, b) in (((14, -170), (-120, -14)), ((14, -170), (136, -12)), ((60, -150), (128, -14))):
        out.append(f'<path d="M {P(*a)[0]:.1f} {P(*a)[1]:.1f} L {P(*b)[0]:.1f} {P(*b)[1]:.1f}" stroke="{sil}" stroke-width="1" opacity="0.8"/>')
    # hull: slender, ends swept up, a painted stripe catching the light
    hull = PP([(-140, -24), (-120, -14), (-60, -8), (60, -8), (124, -14), (150, -30), (140, -6), (100, 6), (-100, 6), (-136, -6)])
    hd = smooth_closed(hull)
    out.append(f'<path d="{hd}" fill="{sil}"/>')
    out.append(clipped(D, hd, [taper(PP([(-130, -12), (0, -4), (136, -14)]), 2.4 * s, 2.4 * s, "#3E5AA8", 0.8),
                               taper(PP([(-128, -8), (0, 0), (134, -10)]), 1.8 * s, 1.8 * s, "#C83A4A", 0.7)]))
    out.append(taper(PP([(-120, -15), (-60, -9), (60, -9), (122, -15), (148, -30)]), 2.4 * s, 1.5 * s, rim, 0.85))
    # booms arching from the hull out to the near float, the near float on the water
    for bx in (-70, 44):
        out.append(taper(PP([(bx, -12), (bx + 10, -26), (bx + 26, -12), (bx + 30, 10)]), 4 * s, 3 * s, sil))
        out.append(taper(PP([(bx + 2, -14), (bx + 12, -27), (bx + 26, -14)]), 1.4 * s, 1 * s, rim, 0.7))
    out.append(taper(PP([(-160, 12), (0, 14), (160, 12)]), 6 * s, 6 * s, sil))
    out.append(taper(PP([(-158, 10), (0, 12), (158, 10)]), 1.6 * s, 1.6 * s, rim, 0.6))
    return "".join(out)


@design("bahala-na")
def bahala_na():
    D = Doc2("ph-bn")
    hz = 372
    SKY = [(0, "#1C2260"), (0.2, "#3E3A7E"), (0.38, "#9A5A90"), (0.5, "#E8826E"), (0.58, "#FFB874"), (0.62, "#FFD898")]
    out = [sky_paint(D, SKY, 1401, hz + 2, n=110)]
    rnd = random.Random(1402)
    for _ in range(20):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 120):.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    SX, SY = 420, hz - 22
    out.append(soft_glow(D, SX, SY, 330, "#FFC880", 0.7))
    out.append(soft_glow(D, SX, SY, 90, "#FFF2C8", 0.9))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="30" fill="#FFF6D8"/>')
    # long clouds lit from below by the sun
    for k in range(10):
        y = 210 + k * 14 + rnd.uniform(-4, 4)
        x = rnd.uniform(-80, 480)
        w = rnd.uniform(160, 320)
        col = mix("#FFC890", "#B8608A", abs(x + w / 2 - SX) / 500)
        out.append(taper([(x, y), (x + w * 0.45, y - 4), (x + w, y + 2)], 1, rnd.uniform(5, 11), mix(col, "#6A4A8A", 0.35), rnd.uniform(0.5, 0.75)))
        out.append(taper([(x + 14, y + 5), (x + w * 0.5, y + 4), (x + w * 0.92, y + 6)], 1, 2.4, "#FFE6B8", 0.55))
    # far islands: limestone karsts, hazy violet
    for k, (pts, col) in enumerate((([(-20, hz + 2), (10, hz - 46), (40, hz - 58), (66, hz - 30), (96, hz - 40), (130, hz - 10), (150, hz + 2)], "#6A4E7A"),
                                    ([(520, hz + 2), (546, hz - 26), (576, hz - 34), (620, hz - 12), (620, hz + 2)], "#7A5A84"))):
        out.append(f'<path d="{smooth_closed(jitter(densify(pts, 10), 1403 + k, 2))}" fill="{col}"/>')
        out.append(f'<path d="{smooth_closed(jitter(densify(pts, 10), 1403 + k, 2))}" fill="{D.lin([(0, "#FFB890", 0.0), (1, "#FFB890", 0.3)], 0, 0, 1, 0)}"/>')
    # the sea: mirror of the sky, darkening toward us, a glitter road under the sun
    sea_d = f"M -10 {hz} L 610 {hz} L 610 610 L -10 610 Z"
    out.append(f'<path d="{sea_d}" fill="{D.lin([(0, "#F2A47A"), (0.12, "#B86A86"), (0.45, "#4A3A72"), (1, "#141A44")])}"/>')
    waves = []
    for k in range(240):
        y = hz + 3 + (k / 240) ** 1.5 * 236
        L = 8 + (y - hz) * 0.3
        x = rnd.uniform(-20, 600)
        waves.append(taper([(x, y), (x + L * 0.5, y - 0.6), (x + L, y)], 0.5, 1 + (y - hz) * 0.012, rnd.choice(["#6A5A9A", "#2A2A5E", "#C88AA0"]), rnd.uniform(0.3, 0.6)))
    out.append(clipped(D, sea_d, waves))
    glit = []
    for k in range(120):
        t = (k / 120) ** 1.3
        y = hz + 3 + t * 236
        w = 14 + t * 130
        x = SX + rnd.uniform(-w, w) * 0.55
        L = rnd.uniform(5, 18) * (0.6 + t)
        glit.append(taper([(x - L / 2, y), (x + L / 2, y + 0.4)], 1, 2 + t * 2.5, rnd.choice(["#FFF2C8", "#FFD890", "#FFFFFF"]), rnd.uniform(0.5, 0.95)))
    out.append("".join(glit))
    # the paraw, its reflection rippling under it, a small wake
    D.defs.append(ripple_filter("ph-bn-rip", 9, 10, "0.008 0.12", 0.8))
    bx, bw = 214, 456
    out.append(f'<g opacity="0.35" filter="url(#ph-bn-rip)" transform="translate(0 {2 * bw}) scale(1 -1)">{paraw(D, bx, bw, 1.05, 1421, sil="#1A1236")}</g>')
    for k in range(4):
        y = bw + 10 + k * 7
        out.append(taper([(bx - 230 + k * 20, y + 6), (bx - 160, y + 2), (bx - 100, y)], 0.6, 2.4, "#FFD8B0", 0.5 - k * 0.1))
    out.append(paraw(D, bx, bw, 1.05, 1420))
    for (x, y, sz) in ((132, 236, 11), (156, 250, 8), (486, 214, 9)):
        out.append(bird_v(x, y, sz, "#3A2A4A"))
    out.append(letters(D, 300, 120, "Bahala na", SERIF_IT, 128, "#FFF0D8", ["#FFFFFF", "#FFE0C0", "#F8D0B8"], 1430, max_w=460,
                       shadow="#0E1238", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 166, "COME WHAT MAY", "#FFD08A", font=JOS, size=21, ls=9, line_w=34, gap=14))
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
    SKY = [(0, "#3E4A62"), (0.3, "#5E6C84"), (0.6, "#8E9CB0"), (0.8, "#B8C4CC")]
    out = [sky_paint(D, SKY, 1501, 600, n=120, var=0.1)]
    # a patch of sun still on the right, the storm rolling in from the left
    out.append(soft_glow(D, 560, 240, 230, "#FFF2C8", 0.6))
    for k, (x, y, w, h) in enumerate(((120, 272, 360, 110), (-20, 316, 260, 90), (330, 236, 240, 70))):
        out.append(cloud_bank(D, x, y, w, h, 1502 + k, lit="#C8D0DC", mid="#7E8AA0", shade="#3A4458", light_dir=1, n=34, op=0.97))
    out.append(rain_sheets(D, 1506, (-40, 260, 380, 610), col="#D8E2EE", n=200))
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
    out.append(f'<path d="{wallp}" fill="{D.lin([(0, "#2A3040", 0.45), (0.4, "#2A3040", 0.15), (1, "#FFE8C0", 0.1)], 0, 0, 1, 0)}"/>')
    out.append(clipped(D, wallp, [streaks_down(1541, (hx, 250, 610, 520), "#5A3A1E", 30)]))
    # rain pouring off the roof edge in strings, splashing
    for k in range(9):
        x = hx - 22 + k * 20
        out.append(f'<path d="M {x:.1f} 254 L {x - 3:.1f} {300 + (k % 3) * 40:.1f}" stroke="#E8F2FF" stroke-width="1.6" opacity="0.55" stroke-dasharray="8 6"/>')
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
    out.append(rain_sheets(D, 1520, (-30, 250, 300, 610), col="#EEF4FF", n=90, op=(0.3, 0.7), curtains=2))
    # the wet ground mirrors the bright gap in the sky and the washing
    fidw = D.nid()
    D.defs.append(soft_filter(fidw, 3))
    out.append(f'<g filter="url(#{fidw})" opacity="0.35">'
               + "".join(f'<path d="{blob(x, 548, w * 0.4, 6, 1540 + i, 0.2, 10)}" fill="{c}"/>' for i, (x, w, c) in enumerate(((128, 74, "#2E9AC8"), (216, 76, "#E8504A"), (304, 76, "#E060A8"), (386, 58, "#3A6AC8"))))
               + '</g>')
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


def butterfly2(D, cx, cy, s, ang, seed, pal, flap=1.0, backlit=True, tilt=0.0):
    """A painted butterfly in flight: pointed forewings, rounded hindwings with a little tail, veins radiating from
    the body, dark borders with pale spots, wings glowing where the light comes through. flap < 1 folds the wings
    (seen at an angle); tilt squashes the far wing pair (3/4 view)."""
    light, base, dark = pal
    rnd = random.Random(seed)

    def T(pts, sg):
        k = flap * (1 - tilt * 0.5 if sg > 0 else 1)
        return rot([(cx + x * s * k * sg, cy + y * s) for x, y in pts], cx, cy, ang)
    out = []
    FW = [(1, -2), (14, -24), (34, -38), (46, -36), (44, -24), (34, -8), (12, 2)]
    HW = [(1, 2), (14, 4), (30, 12), (32, 26), (22, 38), (16, 50), (10, 36), (2, 18)]
    for sg in ((1, -1) if tilt else (-1, 1)):
        for k, W in enumerate((FW, HW)):
            w = T(W, sg)
            d = smooth_closed(w)
            g = D.rad([(0, light, 1), (0.55, base, 1), (1, dark, 1)], 0.5 + 0.1 * sg, 0.55, 0.75)
            inner = [f'<path d="{d}" fill="{g}"/>']
            root = T([(1, 0)], sg)[0]
            veins = "".join(f"M{root[0]:.1f} {root[1]:.1f}L{p[0]:.1f} {p[1]:.1f}" for p in w[1:-1])
            inner.append(f'<path d="{veins}" stroke="{dark}" stroke-width="0.8" opacity="0.5" fill="none"/>')
            inner.append(f'<path d="{d}" fill="none" stroke="{mix(dark, "#140810", 0.4)}" stroke-width="{6 * s:.1f}" opacity="0.85"/>')
            for j, t in enumerate((0.35, 0.55, 0.75)):
                a, b = w[2 + j % 2], w[3 + j % 2]
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.6 * s:.1f}" fill="#FFF6E0" opacity="0.9"/>')
            if backlit:
                inner.append(f'<path d="{d}" fill="{D.rad([(0, "#FFF6D8", 0.45), (1, "#FFF6D8", 0)], 0.5, 0.5, 0.5)}"/>')
            out.append(f'<g opacity="{0.94 if k == 0 else 0.9}">{clipped(D, d, inner)}</g>')
    body = rot([(cx, cy - 8 * s), (cx + 2.6 * s, cy), (cx, cy + 22 * s), (cx - 2.6 * s, cy)], cx, cy, ang)
    out.append(f'<path d="{smooth_closed(body)}" fill="#2A1A1A"/>')
    h = rot([(cx, cy - 10 * s)], cx, cy, ang)[0]
    for sg in (-1, 1):
        t_ = rot([(cx + sg * 9 * s, cy - 26 * s)], cx, cy, ang)[0]
        out.append(f'<path d="M {h[0]:.1f} {h[1]:.1f} Q {(h[0] + t_[0]) / 2 + sg * 2:.1f} {(h[1] + t_[1]) / 2:.1f} {t_[0]:.1f} {t_[1]:.1f}" stroke="#2A1A1A" stroke-width="1" fill="none"/>'
                   f'<circle cx="{t_[0]:.1f}" cy="{t_[1]:.1f}" r="1.3" fill="#2A1A1A"/>')
    return "".join(out)


@design("kilig")
def kilig():
    D = Doc2("ph-kl")
    rnd = random.Random(1600)
    # the room: a warm, shadowed plaster wall around an open window
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#6A3A4A"), (0.6, "#7A4650"), (1, "#4A2832")])}"/>']
    out.append(clipped(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", brush_field(1601, (-40, -10, 610, 610), ["#8A5460", "#5A303C", "#9A6068", "#4A2632"], 240, -88, (30, 90), (4, 10), (0.15, 0.35))))
    # the window: a dusk sky going pink, a mango tree and rooftops beyond
    wx0, wy0, wx1, wy1 = 128, 214, 472, 452
    win = pd([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])
    SKY = [(0, "#6A6AB0"), (0.4, "#C878A8"), (0.62, "#F6A08A"), (0.78, "#FFD0A0")]
    view = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(o, c) for o, c in SKY], 0, 0, 0, 1)}"/>',
            soft_glow(D, 380, 420, 160, "#FFE0B0", 0.8),
            cloud_bank(D, 230, 280, 160, 34, 1602, lit="#FFE8E0", mid="#F2C0C8", shade="#A87AA0", light_dir=1, op=0.85),
            f'<path d="{pd([(wx0, 430), (180, 404), (186, 392), (262, 386), (268, 410), (330, 412), (340, 396), (420, 392), (428, 418), (wx1, 420), (wx1, wy1), (wx0, wy1)])}" fill="#5A3A5E"/>',
            dab_crown(D, 182, 372, 70, 50, [("#6A4A6E", "#523656", "#3E2844")], 1603, n=60, size=(6, 12), inkw=0),
            f'<rect x="232" y="402" width="8" height="10" fill="#FFC870" opacity="0.8"/><rect x="372" y="404" width="8" height="10" fill="#FFC870" opacity="0.8"/>']
    out.append(clipped(D, win, view))
    # the capiz panels slid open to each side, glowing pearly in the evening light
    for side in (-1, 1):
        x0, x1 = (wx0 - 100, wx0 + 4) if side < 0 else (wx1 - 4, wx1 + 100)
        out.append(capiz_window(D, x0, wy0 + 4, x1, wy1 - 4, 1604 + side, cols=4, rows=7, frame=NARRA, glow="#FFE8D8"))
    out.append(painted(D, rect_pts(wx0 - 14, wy0 - 20, wx1 + 14, wy0, 16, 1606, 0.4), NARRA, 1606, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=0, hi=0.35))
    # the sill, and the evening light falling across it
    sill = pd([(60, 452), (540, 452), (560, 490), (40, 490)])
    out.append(painted(D, densify([(60, 452), (540, 452), (560, 490), (40, 490)], 10), ("#D8A070", "#A8683C", "#5A3018"), 1607, sdir=(0, 1), sk=0.2, angle=0, n=40, inkw=0, hi=0.45))
    out.append(f'<path d="{pd([(40, 506), (560, 506), (600, 600), (0, 600)])}" fill="#2A1018" opacity="0.35"/>')
    out.append(f'<path d="{pd([(40, 490), (560, 490), (560, 506), (40, 506)])}" fill="#4A2414"/>')
    out.append(f'<path d="{pd([(130, 452), (470, 452), (520, 490), (90, 490)])}" fill="#FFD8A8" opacity="0.3"/>')
    out.append(f'<path d="M 40 490 L 560 490" stroke="#FFD0A0" stroke-width="1.6" opacity="0.6"/>')
    # the love letter, unfolded, its envelope, a pressed gumamela
    out.append(cast(D, 300, 484, 140, 8, strength=0.35, seed=1608))
    env = rot([(320, 446), (440, 446), (446, 486), (314, 486)], 380, 466, 4)
    out.append(painted(D, densify(env, 10), ("#FFF6EE", "#F2DCCC", "#C0A090"), 1609, sk=0.12, angle=0, n=8, inkw=0, hi=0.3))
    out.append(f'<path d="{pd(rot([(320, 446), (380, 470), (440, 446)], 380, 466, 4))}" fill="none" stroke="#C8A898" stroke-width="1.4"/>')
    out.append(p_heart(D, 384, 472, 9, PULA, 1610, inkw=0))
    let = [(170, 440), (300, 436), (310, 486), (160, 488)]
    out.append(painted(D, densify(let, 10), ("#FFFFFF", "#FFF8EC", "#D8CCBC"), 1611, sk=0.1, angle=0, n=6, inkw=0, hi=0.3))
    out.append(f'<path d="M 166 462 L 304 460" stroke="#E0D4C4" stroke-width="1.2"/>')
    for k in range(4):
        y = 446 + k * 10
        pts = [(178 + k * 0.5, y)]
        x = pts[0][0]
        while x < 290 - (30 if k == 3 else 0):
            x += rnd.uniform(5, 9)
            pts.append((x, y + rnd.uniform(-1.5, 1)))
        out.append(f'<path d="{smooth_open(pts)}" stroke="#4A5AA8" stroke-width="1.1" fill="none" opacity="0.75"/>')
    out.append(gumamela(D, 150, 478, 20, 1612))
    # butterflies rising out of the letter toward the open window, lit from behind by the dusk
    pals = [("#FFD8E8", "#EE6AA8", "#7A1A4A"), ("#FFF0B0", "#F6B42E", "#7A4A0A"), ("#C8ECFF", "#3EA0E0", "#0E3A6A"),
            ("#E8D0FF", "#9A6AE0", "#3A1A6A"), ("#FFD0B8", "#F27A4A", "#7A2A0A")]
    spots = [(236, 410, 0.8, -20, 1.0), (196, 360, 0.9, 15, 0.7), (262, 330, 0.75, -35, 0.9), (330, 300, 0.85, 20, 0.55),
             (410, 266, 0.7, -10, 1.0), (300, 252, 0.6, 30, 0.8), (450, 340, 0.62, 25, 0.85)]
    for k, (x, y, sc, a, fl) in enumerate(spots):
        out.append(soft_glow(D, x, y, 40 * sc, "#FFF0D8", 0.35))
        out.append(butterfly2(D, x, y, sc, a, 1620 + k, pals[k % len(pals)], flap=fl, tilt=0.3 if k % 2 else 0.0))
    out.append(letters(D, 300, 140, "kilig", SERIF_IT, 140, "#FFD8E4", ["#FFFFFF", "#FFC0D8", "#FFE0EC"], 1650, max_w=340,
                       shadow="#2A0E1A", soff=(0.018, 0.03), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 186, "KILIG TO THE BONES", "#FFC8A0", font=JOS, size=20, ls=6, line_w=28, gap=12))
    return finish_b(D, out, 1651, "#5A2A3A")


def gumamela(D, cx, cy, r, seed, pal=("#FF8A7A", "#E02A3A", "#7A0A18")):
    """Hibiscus (gumamela): five broad ruffled petals, a dark throat, the long stamen column with pollen."""
    rnd = random.Random(seed)
    out = []
    for k in range(5):
        a = math.radians(k * 72 - 90 + rnd.uniform(-8, 8))
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        d = blob(px, py, r * 0.62, r * 0.48, seed + k, 0.12, 12, math.degrees(a))
        out.append(f'<path d="{d}" fill="{pal[1]}"/>')
        out.append(clipped(D, d, [f'<path d="{d}" fill="{D.rad([(0, pal[2], 0.8), (0.5, pal[1], 0), (1, pal[0], 0.7)], 0.5, 0.5, 0.6)}"/>']))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.2:.1f}" fill="{pal[2]}"/>')
    sx, sy = cx + r * 0.7, cy - r * 0.6
    out.append(f'<path d="M {cx:.1f} {cy:.1f} Q {cx + r * 0.4:.1f} {cy - r * 0.1:.1f} {sx:.1f} {sy:.1f}" stroke="#F2C0B0" stroke-width="2" fill="none"/>')
    for j in range(5):
        out.append(f'<circle cx="{sx + rnd.uniform(-3, 3):.1f}" cy="{sy + rnd.uniform(-3, 3):.1f}" r="1.4" fill="#F6C83A"/>')
    return "".join(out)


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


def furred(D, pts, base, cols, seed, flow, n, length=(5, 10), width=(0.7, 1.4), shade=None, edge=True, edge_cols=None):
    """A furry form: base fill, hair strokes following flow(x, y), an optional light->shade glaze, hairy outline."""
    d = smooth_closed(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    inner = [fur(seed, (min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4), cols, n, flow, length, width)]
    if shade:
        inner.append(f'<path d="{d}" fill="{shade}"/>')
    out = [f'<path d="{d}" fill="{base}"/>', clipped(D, d, inner)]
    if edge:
        out.append(fuzzy_edge(seed + 1, pts, edge_cols or [base] + cols[:2], 1.1, (length[0] * 0.45, length[1] * 0.55), (width[0] * 0.8, width[1] * 0.8)))
    return "".join(out)


@design("gigil")
def gigil():
    D = Doc2("ph-gg")
    rnd = random.Random(1700)
    # a sunny corner of the sala: lime-washed wall, window light falling across the floor
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#E8EEDA"), (0.6, "#D6E2C8"), (1, "#C2D0B0")])}"/>']
    out.append(clipped(D, "M -10 -10 L 610 -10 L 610 420 L -10 420 Z",
                       brush_field(1701, (-40, -10, 610, 420), ["#F2F4E4", "#C0CCB0", "#E0E8D0", "#B8C8A8"], 160, -88, (30, 90), (4, 10), (0.15, 0.35))))
    # a big patch of sunlight from the window (left), the floor of narra planks
    out.append(f'<path d="{pd([(60, 0), (300, 0), (420, 420), (150, 420)])}" fill="#FFF6D8" opacity="0.35"/>')
    floor = "M -10 420 L 610 420 L 610 610 L -10 610 Z"
    out.append(f'<path d="{floor}" fill="#B07848"/>')
    pl = []
    for k in range(9):
        y = 420 + (k / 9) ** 1.4 * 190
        pl.append(f"M-10 {y:.1f}L610 {y + rnd.uniform(-1, 1):.1f}")
    out.append(clipped(D, floor, [f'<path d="{"".join(pl)}" stroke="#6A3E1E" stroke-width="1.6" opacity="0.6" fill="none"/>',
                                  brush_field(1702, (-40, 420, 610, 610), ["#D09A62", "#8A5430", "#C88A50", "#E8B880"], 90, 0, (40, 140), (2, 5), (0.2, 0.45), 0.05, 3),
                                  f'<path d="{pd([(140, 420), (430, 420), (540, 610), (190, 610)])}" fill="#FFE8B0" opacity="0.28"/>']))
    out.append(f'<path d="M -10 420 L 610 420" stroke="#5A3A20" stroke-width="5" opacity="0.6"/>')
    # banig mat under the puppy, in perspective
    rug = [(150, 470), (470, 466), (530, 566), (96, 572)]
    rd = smooth_closed(densify(rug, 12))
    out.append(banig(D, rd, 1704, cell=9, base="#E8D0A0", bands=("#E8508A", "#2E9A7A", "#F2B21E", "#6A4AB0"), rot_=45))
    out.append(clipped(D, rd, [f'<path d="{rd}" fill="{D.lin([(0, "#3A1A06", 0.25), (1, "#3A1A06", 0.0)])}"/>']))
    # the chewed tsinelas he has been working on
    out.append(f'<path d="{blob(150, 540, 34, 12, 1705, 0.1, 14, -20)}" fill="#2E6AC8"/><path d="{blob(148, 537, 28, 8, 1706, 0.12, 14, -20)}" fill="#7AA8F0" opacity="0.6"/>'
               f'<path d="M 140 534 q 10 -12 22 -2" stroke="#1E3A8A" stroke-width="3" fill="none"/><path d="M 120 548 l 6 -4 l 4 6 l 5 -5" stroke="#1E3A8A" stroke-width="1.4" fill="none"/>')
    # ---------------- the puppy: a chubby aspin pup sitting, head tilted ----------------
    TAN = ("#E8B878", "#C88A48", "#7A4A1E")
    WH = ("#FFFCF4", "#F2E8DA", "#B8A890")
    P = []
    P.append(cast(D, 330, 520, 150, 20, strength=0.45, seed=1707))
    # tail curled over the back, right
    tail = limb((376, 468), (426, 430), (414, 392), 22, 16, 8)
    P.append(furred(D, tail, TAN[1], [TAN[0], TAN[2], "#F2CC90"], 1729, lambda x, y: -60, 200, (5, 9), (0.6, 1.1)))
    # body and haunches
    bodyp = blob_pts(300, 436, 92, 86, 1708, 0.03, 24)
    P.append(furred(D, bodyp, TAN[1], [TAN[0], TAN[2], TAN[1], "#F2CC90"], 1709, lambda x, y: 90 + (x - 300) * 0.3, 900, (6, 11),
                    shade=D.lin([(0, "#FFF4DC", 0.25), (0.45, "#FFF4DC", 0), (1, "#3A1A06", 0.35)], 0, 0, 1, 0.6)))
    for k, (hx, hy, rx, ry) in enumerate(((372, 478, 52, 42), (226, 482, 44, 38))):
        hp = blob_pts(hx, hy, rx, ry, 1710 + k, 0.04, 18)
        P.append(furred(D, hp, TAN[1], [TAN[0], TAN[2], "#F2CC90"], 1711 + k, lambda x, y, hx=hx: 120 if x > hx else 60, 300, (6, 10),
                        shade=D.lin([(0, "#FFF4DC", 0.2), (1, "#3A1A06", 0.3)], 0, 0, 1, 1)))
    # hind paws peeking out in front of the haunches
    for k, (px, py) in enumerate(((384, 516), (216, 518))):
        pp = blob_pts(px, py, 24, 11, 1712 + k, 0.05, 14)
        P.append(furred(D, pp, WH[1], [WH[0], WH[2]], 1713 + k, lambda x, y: 90, 120, (3, 6), edge_cols=[WH[1], WH[0]]))
    # white chest and the front legs
    chest = blob_pts(300, 408, 50, 62, 1714, 0.05, 18)
    P.append(furred(D, chest, WH[1], [WH[0], WH[2], "#FFFFFF"], 1715, lambda x, y: 90 + (x - 300) * 0.8, 500, (5, 10), edge_cols=[WH[1], WH[0]],
                    shade=D.lin([(0, "#FFFFFF", 0.2), (1, "#5A4A3A", 0.25)], 0, 0, 1, 1)))
    for k, (lx, sg) in enumerate(((270, -1), (332, 1))):
        leg = [(lx - 17, 420), (lx + 17, 420), (lx + 18 + sg * 2, 500), (lx - 16 + sg * 2, 502)]
        P.append(furred(D, densify(leg, 8), WH[1], [WH[0], WH[2]], 1716 + k, lambda x, y: 92, 220, (4, 8), edge_cols=[WH[1], WH[0]],
                        shade=D.lin([(0, "#FFFFFF", 0.0), (1, "#5A4A3A", 0.3)], 0, 0, 1, 0)))
        paw = blob_pts(lx + sg * 2, 506, 22, 13, 1718 + k, 0.05, 14)
        P.append(furred(D, paw, WH[1], [WH[0], WH[2]], 1719 + k, lambda x, y: 90, 120, (3, 6), edge_cols=[WH[1], WH[0]]))
        for t in (-0.4, 0.0, 0.4):
            P.append(f'<path d="M {lx + sg * 2 + t * 22:.1f} 512 l 0 6" stroke="#8A7A68" stroke-width="1.4" opacity="0.7"/>')
    # head, tilted, with floppy ears, a white blaze and muzzle
    HX, HY, TILT = 300, 300, -9
    def R(x, y):
        a = math.radians(TILT)
        dx, dy = x - HX, y - HY
        return (HX + dx * math.cos(a) - dy * math.sin(a), HY + dx * math.sin(a) + dy * math.cos(a))
    for k, (base_, mid, tip) in enumerate((((236, 262), (204, 292), (214, 340)), ((364, 262), (398, 290), (390, 338)))):
        sg = -1 if k == 0 else 1
        ear = [R(base_[0] - sg * 10, base_[1] - 14), R(mid[0], mid[1] - 10), R(tip[0] + sg * 6, tip[1]), R(tip[0] - sg * 12, tip[1] - 4),
               R(mid[0] - sg * 22, mid[1] + 10), R(base_[0] - sg * 26, base_[1] + 26)]
        P.append(furred(D, ear, TAN[2], ["#5A3216", TAN[1], "#3A1E0A"], 1720 + k, lambda x, y: 100, 260, (5, 9),
                        shade=D.lin([(0, "#3A1A06", 0.1), (1, "#3A1A06", 0.35)], 0, 0, 0, 1)))
    head = [R(x, y) for x, y in blob_pts(HX, HY, 82, 70, 1722, 0.03, 26)]
    P.append(furred(D, head, TAN[1], [TAN[0], TAN[2], "#F2CC90", TAN[1]], 1723,
                    lambda x, y: math.degrees(math.atan2(y - (HY + 30), x - HX)), 1300, (5, 9),
                    shade=D.lin([(0, "#FFF4DC", 0.35), (0.5, "#FFF4DC", 0), (1, "#3A1A06", 0.3)], 0, 0, 1, 1)))
    blaze = [R(x, y) for x, y in [(292, 238), (308, 238), (314, 290), (334, 312), (300, 322), (266, 312), (286, 290)]]
    P.append(furred(D, blaze, WH[1], [WH[0], WH[2], "#FFFFFF"], 1724, lambda x, y: -90, 220, (4, 8), edge_cols=[WH[1]]))
    muzzle = [R(x, y) for x, y in blob_pts(HX, HY + 38, 44, 30, 1725, 0.04, 18)]
    P.append(furred(D, muzzle, WH[1], [WH[0], WH[2], "#FFFFFF"], 1726, lambda x, y: math.degrees(math.atan2(y - (HY + 26), x - HX)), 500, (3, 7),
                    edge_cols=[WH[1], WH[0]], shade=D.lin([(0, "#FFFFFF", 0.0), (1, "#6A5A4A", 0.25)], 0, 0, 0, 1)))
    # cheeks begging to be squeezed: a warm rosy glaze in the fur
    for sg in (-1, 1):
        c = R(HX + sg * 48, HY + 30)
        P.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="18" ry="11" fill="#F28A7A" opacity="0.28"/>')
    # nose, mouth, a little pink tongue
    n = R(HX, HY + 22)
    P.append(f'<path d="{smooth_closed([(n[0] - 13, n[1] - 5), (n[0] + 13, n[1] - 6), (n[0] + 8, n[1] + 7), (n[0], n[1] + 10), (n[0] - 8, n[1] + 7)])}" fill="#1E1410"/>'
             f'<ellipse cx="{n[0] - 4:.1f}" cy="{n[1] - 3:.1f}" rx="4.5" ry="2.2" fill="#FFFFFF" opacity="0.55"/>')
    m1, m2, m3 = R(HX - 16, HY + 46), R(HX, HY + 40), R(HX + 16, HY + 46)
    P.append(f'<path d="M {m1[0]:.1f} {m1[1]:.1f} Q {(m1[0] + m2[0]) / 2:.1f} {m1[1] + 6:.1f} {m2[0]:.1f} {m2[1]:.1f} Q {(m2[0] + m3[0]) / 2:.1f} {m3[1] + 6:.1f} {m3[0]:.1f} {m3[1]:.1f}" stroke="#3A2418" stroke-width="2" fill="none"/>')
    t0 = R(HX + 2, HY + 48)
    P.append(f'<path d="{blob(t0[0], t0[1] + 3, 7, 8, 1727, 0.08, 10)}" fill="#E8607A"/><path d="M {t0[0]:.1f} {t0[1] - 2:.1f} l 0 8" stroke="#B8304A" stroke-width="1.2"/>')
    # eyes: dark, wet, a little wide — real puppy eyes, not cartoon
    for sg in (-1, 1):
        e = R(HX + sg * 32, HY - 6)
        P.append(f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="13" ry="12" fill="#2A1A10"/>'
                 f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="11" ry="10.5" fill="{D.rad([(0, "#6A3A1A"), (0.6, "#3A1E0E"), (1, "#140A06")], 0.5, 0.6, 0.6)}"/>'
                 f'<circle cx="{e[0] - 3:.1f}" cy="{e[1] - 4:.1f}" r="3.6" fill="#FFFFFF" opacity="0.92"/>'
                 f'<circle cx="{e[0] + 4:.1f}" cy="{e[1] + 4:.1f}" r="1.4" fill="#FFFFFF" opacity="0.5"/>'
                 f'<path d="M {e[0] - 14:.1f} {e[1] - 4:.1f} Q {e[0]:.1f} {e[1] - 17:.1f} {e[0] + 14:.1f} {e[1] - 5:.1f}" stroke="#5A3216" stroke-width="2" fill="none" opacity="0.6"/>')
        b = R(HX + sg * 30, HY - 26)
        P.append(f'<ellipse cx="{b[0]:.1f}" cy="{b[1]:.1f}" rx="8" ry="5" fill="#F2CC90" opacity="0.7"/>')
    # collar with a little brass bell
    P.append(taper([R(250, 352), R(300, 366), R(350, 350)], 9, 9, "#C8303A"))
    bc = R(302, 372)
    P.append(f'<circle cx="{bc[0]:.1f}" cy="{bc[1]:.1f}" r="7" fill="{D.rad([(0, "#FFF0A0"), (1, "#B8861E")], 0.35, 0.35, 0.7)}"/>')
    out.extend(P)
    # rim of window light on the puppy's left side
    out.append(f'<path d="{smooth_open([R(220, 290), R(222, 320), R(232, 350)])}" stroke="#FFF6D8" stroke-width="3" fill="none" opacity="0.5"/>')
    for k, (x, y, sz) in enumerate(((118, 262, 11), (488, 250, 13), (470, 380, 9))):
        out.append(p_heart(D, x, y, sz, ("#FFB8CC", "#F2648E", "#A82A5A"), 1730 + k, rot_=rnd.uniform(-20, 20), inkw=0))
    out.append(letters(D, 300, 150, "gigil!", SERIF_IT, 128, "#1E6A4A", ["#2E8A62", "#0E4A30", "#4AAA80"], 1740, max_w=340,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#B8F0D0"))
    out.append(ruled(300, 198, "THAT URGE TO SQUEEZE SOMETHING CUTE", "#C83A6A", font=JOS, size=16, ls=3, line_w=16, gap=10, max_w=430))
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


def stone_wall(D, d, box, seed, base, light, dark, course=11, lit_fn=None):
    """Old coral-stone masonry: a wash, uneven block courses, moss and rain stains, chipped highlights."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    inner = [f'<path d="{d}" fill="{base}"/>']
    inner.append(brush_field(seed, (x0 - 10, y0, x1, y1), [light, dark, base, mix(base, "#6A7A5A", 0.4)], int((x1 - x0) * (y1 - y0) / 160), -90, (8, 30), (2, 5), (0.15, 0.4)))
    y = y0
    lines = []
    while y < y1:
        h = course * rnd.uniform(0.8, 1.2)
        lines.append(f"M{x0} {y:.1f}L{x1} {y + rnd.uniform(-1, 1):.1f}")
        x = x0 + rnd.uniform(0, 20)
        while x < x1:
            w = course * rnd.uniform(1.6, 3.2)
            lines.append(f"M{x:.1f} {y:.1f}l{rnd.uniform(-0.5, 0.5):.1f} {h:.1f}")
            if rnd.random() < 0.25:
                inner.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{rnd.choice([light, dark])}" opacity="{rnd.uniform(0.1, 0.25):.2f}"/>')
            x += w
        y += h
    inner.append(f'<path d="{"".join(lines)}" stroke="{dark}" stroke-width="1" opacity="0.45" fill="none"/>')
    inner.append(streaks_down(seed + 1, (x0, y0, x1, y1), mix(dark, "#2A3A2A", 0.3), int((x1 - x0) / 6)))
    return clipped(D, d, inner)


@design("simbang-gabi")
def simbang_gabi():
    D = Doc2("ph-sb")
    rnd = random.Random(1802)
    SKY = [(0, "#0A1236"), (0.25, "#1A2A60"), (0.5, "#34407E"), (0.62, "#6A5A92"), (0.7, "#B87A8A")]
    out = [sky_paint(D, SKY, 1801, 430, n=90)]
    for _ in range(46):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 260):.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.3, 0.85):.2f}"/>')
    out.append(sparkle(538, 92, 8, "#FFF6D8", 0.95))
    # the church: earthquake-baroque facade with buttresses, a pediment, niches; a detached bell tower on the right
    base = 404
    l, r = 120, 380
    fac = [(l - 14, base), (l - 14, 262), (l + 30, 252), (l + 52, 226), (300 - 50, 214), (250, 196), (250, 180), (258, 178), (262, 182), (262, 196),
           (300 - 30, 214), (r - 52, 226), (r - 30, 252), (r + 14, 262), (r + 14, base)]
    fac = [(x + 10, y) for x, y in fac]
    fd = pd(fac)
    STONE = ("#D8B890", "#9A7E68", "#4E4048")
    out.append(stone_wall(D, fd, (l - 10, 170, r + 30, base), 1803, *STONE[1:2], STONE[0], STONE[2]))
    # night-blue glaze over the stone, the warm light of the doorway and the parols pushing back
    out.append(f'<path d="{fd}" fill="{D.lin([(0, "#1A2250", 0.55), (0.6, "#1A2250", 0.25), (1, "#1A2250", 0.1)])}"/>')
    out.append(clipped(D, fd, [soft_glow(D, 260, 380, 150, "#FFB860", 0.7), soft_glow(D, 260, 250, 120, "#FFD890", 0.25)]))
    # massive buttresses
    for bx in (l - 14 + 10, r - 10):
        bt = [(bx - 4, base), (bx - 4, 280), (bx + 6, 266), (bx + 30, 266), (bx + 34, 290), (bx + 40, base)]
        bt = [(x, y) for x, y in bt]
        out.append(stone_wall(D, pd(bt), (bx - 6, 260, bx + 42, base), 1804 + bx, "#8A7060", "#C8A880", "#3E3440", course=12))
        out.append(f'<path d="{pd(bt)}" fill="{D.lin([(0, "#14183E", 0.5), (1, "#14183E", 0.2)], 0, 0, 1, 0)}"/>')
        out.append(taper([(bx + 6, 268), (bx + 30, 268)], 2, 2, "#E8C8A0", 0.5))
    # cornices and pilasters
    for y in (300, 252):
        out.append(taper([(l, y), (r + 20, y)], 6, 6, "#5A4A50", 0.85))
        out.append(taper([(l, y - 3), (r + 20, y - 3)], 2, 2, "#F2D0A0", 0.5))
    for x in (l + 40, 200, 320, r - 18):
        out.append(taper([(x, base), (x, 300)], 9, 9, "#6A5A5E", 0.6))
        out.append(taper([(x - 3, base), (x - 3, 300)], 2.4, 2.4, "#F2C890", 0.45))
    # oculus and two saints' niches (empty, softly lit)
    out.append(f'<circle cx="260" cy="236" r="15" fill="#2A2238"/><circle cx="260" cy="236" r="11" fill="{D.rad([(0, "#FFE8A8"), (1, "#E89848")])}"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M 260 236 l {math.cos(a) * 11:.1f} {math.sin(a) * 11:.1f}" stroke="#7A4A28" stroke-width="1.2"/>')
    for nx_ in (172, 348):
        out.append(f'<path d="M {nx_ - 9} 290 L {nx_ - 9} 272 Q {nx_} 260 {nx_ + 9} 272 L {nx_ + 9} 290 Z" fill="#2A2034"/>')
        out.append(f'<path d="M {nx_ - 9} 290 L {nx_ - 9} 272 Q {nx_} 260 {nx_ + 9} 272 L {nx_ + 9} 290 Z" fill="#FFC870" opacity="0.35"/>')
    out.append(f'<path d="M 258 178 L 258 160 M 251 168 L 265 168" stroke="#3A3040" stroke-width="3" stroke-linecap="round"/>')
    # the great door, open: golden interior with the altar far inside
    dw, dtop = 64, 318
    door = f"M {260 - dw / 2} {base} L {260 - dw / 2} {dtop + dw / 2} A {dw / 2} {dw / 2} 0 0 1 {260 + dw / 2} {dtop + dw / 2} L {260 + dw / 2} {base} Z"
    out.append(soft_glow(D, 260, 370, 140, "#FFC060", 0.75))
    out.append(f'<path d="{door}" fill="{D.lin([(0, "#FFE6A8"), (0.6, "#FFC868"), (1, "#F2983A")])}"/>')
    out.append(clipped(D, door, [f'<path d="{pd([(246, 352), (274, 352), (276, 404), (244, 404)])}" fill="#E89038" opacity="0.6"/>',
                                 f'<path d="{blob(260, 344, 8, 10, 1805, 0.05, 10)}" fill="#FFFFFF" opacity="0.8"/>',
                                 soft_glow(D, 260, 346, 30, "#FFFFFF", 0.6)]))
    out.append(f'<path d="{door}" fill="none" stroke="#3A2A30" stroke-width="5"/>')
    for sg in (-1, 1):   # the heavy wooden door leaves swung open
        leaf = [(260 + sg * dw / 2, base), (260 + sg * dw / 2, dtop + dw / 2), (260 + sg * (dw / 2 + 12), dtop + dw / 2 + 6), (260 + sg * (dw / 2 + 12), base + 4)]
        out.append(f'<path d="{pd(leaf)}" fill="#3A2216"/>')
    # steps with light spilling down
    for k in range(3):
        y = base + k * 6
        out.append(f'<path d="{pd([(150 - k * 14, y), (370 + k * 14, y), (370 + k * 14, y + 6), (150 - k * 14, y + 6)])}" fill="{["#8A7A80", "#7A6A72", "#6A5A64"][k]}"/>')
    # bell tower on the right
    tx0, tx1 = 418, 478
    for k, (y0, y1, ins) in enumerate(((236, base, 0), (190, 236, 6), (156, 190, 12))):
        q = pd([(tx0 + ins, y1), (tx0 + ins, y0), (tx1 - ins, y0), (tx1 - ins, y1)])
        out.append(stone_wall(D, q, (tx0 + ins, y0, tx1 - ins, y1), 1806 + k, "#8A7064", "#C8A884", "#3E3442", course=10))
        out.append(f'<path d="{q}" fill="{D.lin([(0, "#1A2250", 0.35), (1, "#1A2250", 0.55)], 0, 0, 1, 0)}"/>')
        out.append(taper([(tx0 + ins - 3, y0), (tx1 - ins + 3, y0)], 5, 5, "#4E4048"))
        ax, ay = (tx0 + tx1) / 2, (y0 + y1) / 2 if k else 290
        out.append(f'<path d="M {ax - 9} {ay + 14} L {ax - 9} {ay - 2} Q {ax} {ay - 14} {ax + 9} {ay - 2} L {ax + 9} {ay + 14} Z" fill="#1A1630"/>')
        if k == 1:
            out.append(f'<path d="{blob(ax, ay + 4, 6, 7, 1809, 0.05, 10)}" fill="#C89A4A"/><path d="{blob(ax - 2, ay + 2, 2, 3, 1810, 0.1, 8)}" fill="#FFE0A0"/>')
    out.append(f'<path d="{pd([(tx0 + 10, 156), (448, 128), (tx1 - 10, 156)])}" fill="#5A4A54"/>')
    out.append(f'<path d="M 448 128 L 448 112 M 442 118 L 454 118" stroke="#3A3040" stroke-width="2.6" stroke-linecap="round"/>')
    # acacia tree on the far left, stars of parols strung across the plaza
    out.append(dab_crown(D, 40, 300, 90, 70, [("#2A3458", "#1E2648", "#141A36")], 1811, n=90, size=(8, 16), inkw=0))
    out.append(taper([(30, base + 10), (40, 320)], 12, 8, "#141A30"))
    # plaza: worn stone with the doorway's light and a few walking silhouettes
    plaza = f"M -10 {base} L 610 {base} L 610 610 L -10 610 Z"
    out.append(f'<path d="{plaza}" fill="{D.lin([(0, "#3A3654"), (1, "#1A1828")])}"/>')
    D.defs.append(soft_filter("ph-sb-spill", 6))
    out.append(f'<path d="{pd([(224, base + 14), (296, base + 14), (420, 520), (100, 520)])}" fill="{D.lin([(0, "#FFC068", 0.55), (1, "#FFC068", 0)])}" filter="url(#ph-sb-spill)"/>')
    out.append(clipped(D, plaza, brush_field(1812, (-40, base, 600, 610), ["#4A4664", "#24203A", "#8A7080"], 70, 0, (30, 100), (1.5, 4), (0.15, 0.35), 0.05, 3)))
    for k, (x, y, h_, pose, f) in enumerate(((214, 446, 40, "walk", 1), (232, 452, 36, "child_walk", 1), (300, 440, 42, "stand_back", 1),
                                              (330, 450, 44, "walk", -1), (176, 436, 34, "couple", 1), (378, 430, 30, "walk", -1))):
        out.append(figures.person(x, y, h_, pose, f, "silhouette:#16142A", seed=1813 + k, rim="#FFC068", light=1 if x < 260 else -1))
    # strings of parols overhead
    for seg, (x0, y0, x1, y1, sag) in enumerate(((-10, 176, 300, 170, 50), (300, 170, 610, 178, 46))):
        ps = [(x0 + (x1 - x0) * t / 16, y0 + (y1 - y0) * t / 16 + sag * 4 * (t / 16) * (1 - t / 16)) for t in range(17)]
        out.append(f'<path d="{smooth_open(ps)}" fill="none" stroke="#0A0A1A" stroke-width="1.4"/>')
        for i in (4, 8, 12):
            x, y = ps[i]
            col = [PULA, ("#7AE0A0", "#1E9A5A", "#0A4A2A"), ("#FFB0D8", "#E8509A", "#8A1A5A"), ARAW][(i // 4 + seg * 2) % 4]
            out.append(f'<path d="M {x:.1f} {y:.1f} l 0 10" stroke="#0A0A1A" stroke-width="1.2"/>')
            out.append(parol(D, x, y + 26, 15, 1820 + seg * 10 + i, body=col, accent=("#FFFFFF", "#F2EAD8", "#C4B49A"), ring=False))
    # foreground: the bibingka stall — a plank table, clay-pot ovens with coals on the lid, puto bumbong
    out.append(soft_glow(D, 470, 520, 220, "#FF9A48", 0.5))
    out.append(painted(D, rect_pts(-10, 506, 610, 526, 20, 1830, 0.5), NARRA, 1830, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=0, hi=0.45))
    out.append(f'<path d="M -10 506 L 610 506" stroke="#FFC890" stroke-width="2" opacity="0.6"/>')
    out.append(f'<path d="M -10 526 L 610 526 L 610 610 L -10 610 Z" fill="#3A1E12"/>')
    out.append(clipped(D, "M -10 526 L 610 526 L 610 610 L -10 610 Z", brush_field(1831, (-40, 526, 600, 610), ["#5A3420", "#24100A", "#8A5030"], 50, -90, (20, 60), (3, 7), (0.2, 0.4))))
    # clay oven with embers heaped on its lid, glowing
    ox, oy = 476, 506
    out.append(palayok(D, ox, oy - 62, 50, 60, 1832, ry=13, soot=0.45))
    out.append(f'<path d="{blob(ox, oy - 64, 58, 13, 1833, 0.1, 14)}" fill="#3A2A26"/>')
    for k in range(16):
        x, y = ox + rnd.uniform(-46, 46), oy - 68 + rnd.uniform(-5, 4)
        out.append(f'<path d="{blob(x, y, rnd.uniform(4.5, 7.5), rnd.uniform(3, 4.5), 1834 + k, 0.2, 8)}" fill="{rnd.choice(["#FF6A2A", "#FFB040", "#C83A1A", "#2A1A1A", "#FFE070"])}"/>')
    out.append(soft_glow(D, ox, oy - 72, 80, "#FF8A3A", 0.7))
    out.append(steam(ox - 10, oy - 82, 70, 1835, "#FFE8D8", 3, 22, 7, 0.45))
    # banana-leaf runner, bibingka in their leaf-lined pans, purple puto bumbong
    out.append(banana_leaf_lite(D, 14, 512, -4, 360, 34, 1836, pal=SAGING))
    out.append(bibingka(D, 104, 518, 50, 1837))
    out.append(bibingka(D, 222, 530, 46, 1838))
    for k in range(3):
        out.append(puto_bumbong(D, 290 + k * 7, 524 + k * 14, 96, -8, 1839 + k))
    out.append(steam(110, 488, 46, 1842, "#FFFFFF", 2, 22, 6, 0.4))
    out.append(letters(D, 300, 104, "Simbang Gabi", SERIF_IT, 106, "#FFE6B0", ["#FFFFFF", "#FFD890", "#FFF0C8"], 1840, max_w=460,
                       shadow="#05051A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 146, "BIBINGKA AT PUTO BUMBONG", "#F2A8C8", font=JOS, size=18, ls=5, line_w=22, gap=10))
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


def terrace_slope(D, seed, curves, sky_stops, light_from=-1, water=0.5, wall=("#8A9A52", "#5E6E36", "#2E3A1E"), rice=("#C8E07A", "#8AB444", "#4E7A24")):
    """Rice terraces carved into a sculpted slope, seen from across the valley. curves = terrace-edge polylines
    from the top (far) to the bottom (near), all with the same x samples. Each band is painted in vertical slices
    whose value follows the local slope of the contour (flanks facing the sun lit, the other flanks in shade), so the
    spurs and gullies of the mountain read; on top of each wall a paddy surface (water mirroring the sky, or young
    rice) widening toward us, with a bright lip where the light catches the dike."""
    rnd = random.Random(seed)
    out = []
    n = len(curves)
    for k in range(n - 1):
        top, bot = curves[k], curves[k + 1]
        depth = k / max(1, n - 2)
        haze = 0.38 * (1 - depth) ** 1.5
        hz = lambda c: mix(c, "#C8D4DE", haze)
        thick = 2.5 + depth ** 1.3 * 22
        flooded = rnd.random() < water
        for i in range(len(top) - 1):
            slope = (top[i + 1][1] - top[i][1]) / max(1e-6, top[i + 1][0] - top[i][0])
            lit = max(-1, min(1, -slope * light_from * 2.2))          # +1 facing the sun
            # wall slice (below the paddy band)
            q = [(top[i][0], top[i][1] + thick), (top[i + 1][0], top[i + 1][1] + thick), bot[i + 1], bot[i]]
            c = mix(wall[1], wall[0] if lit > 0 else wall[2], abs(lit) * 0.8)
            out.append(f'<path d="{pd(q)}" fill="{hz(c)}" stroke="{hz(c)}" stroke-width="0.6"/>')
            # paddy slice
            q2 = [top[i], top[i + 1], (top[i + 1][0], top[i + 1][1] + thick), (top[i][0], top[i][1] + thick)]
            if flooded:
                t = max(0.0, min(0.6, (760 - top[i][1]) / 600 * 0.5))
                c2 = mix(color_at(sky_stops, t), "#FFFFFF", 0.15 + 0.15 * max(0, lit))
            else:
                c2 = mix(rice[1], rice[0] if lit > 0 else rice[2], abs(lit) * 0.7)
            out.append(f'<path d="{pd(q2)}" fill="{hz(c2)}" stroke="{hz(c2)}" stroke-width="0.6"/>')
        band = top + list(reversed(bot))
        bd = pd(band)
        ys = [p[1] for p in band]
        out.append(clipped(D, bd, brush_field(seed + k, (top[0][0] - 10, min(ys), top[-1][0] + 10, max(ys)),
                                              [hz(wall[0]), hz(wall[2]), hz("#9AAA6A"), hz("#B8A87A")], int((top[-1][0] - top[0][0]) * (max(ys) - min(ys)) / 200) + 10,
                                              85, (3, 10), (0.8, 2.2), (0.2, 0.45), 0.2, 15)))
        if not flooded and depth > 0.3:
            pts_ = densify(top, 4 + (1 - depth) * 4, closed=False)
            tufts = "".join(f"M{x:.1f} {y + thick * rnd.uniform(0.3, 1.0):.1f}l{rnd.uniform(-1, 1):.1f} {-thick * rnd.uniform(0.3, 0.6):.1f}" for x, y in pts_)
            out.append(f'<path d="{tufts}" stroke="{hz(rice[2])}" stroke-width="1" fill="none" opacity="0.6"/>')
        if flooded and depth > 0.4:
            glints = "".join(f"M{x:.1f} {y + thick * rnd.uniform(0.3, 0.8):.1f}l{rnd.uniform(6, 18):.1f} 0" for x, y in densify(top, 30, closed=False))
            out.append(f'<path d="{glints}" stroke="#FFFFFF" stroke-width="1.2" fill="none" opacity="0.5"/>')
        out.append(f'<path d="{smooth_open(top)}" fill="none" stroke="{hz("#F6EEC0")}" stroke-width="{1 + depth * 1.6:.1f}" opacity="0.8"/>')
        out.append(f'<path d="{smooth_open([(x, y + thick) for x, y in top])}" fill="none" stroke="{hz("#2E3A1A")}" stroke-width="{0.8 + depth:.1f}" opacity="0.4"/>')
    return "".join(out)


def contour_set(seed, n, y_top, y_bot, x0, x1, shape, amp=4, power=1.25):
    """n terrace edges stacked from y_top (far) to y_bot (near). shape(x, t) -> vertical offset for a curve at
    depth t (0..1) at x (a bowl / spur profile). Small noise so they look hand-built."""
    rnd = random.Random(seed)
    curves = []
    for k in range(n):
        t = (k / (n - 1)) ** power
        y0 = y_top + (y_bot - y_top) * t
        pts = []
        steps = 26
        ph = rnd.uniform(0, 6)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i / steps
            y = y0 + shape(x, t) + math.sin(i * 0.7 + ph) * amp * (0.4 + t)
            pts.append((x, y))
        curves.append(pts)
    return curves


@design("banaue")
def banaue():
    D = Doc2("ph-ba")
    SKY = [(0, "#7AA6D6"), (0.25, "#B8CEE4"), (0.45, "#F2E2C8"), (0.55, "#FFE6B8")]
    out = [sky_paint(D, SKY, 1901, 420, n=80)]
    out.append(soft_glow(D, 80, 250, 280, "#FFF0C8", 0.7))
    out.append(cloud_bank(D, 440, 236, 200, 50, 1902, lit="#FFF6E0", mid="#EEF0F2", shade="#A8B4C8", light_dir=-1, op=0.8))
    # Cordillera ranges fading into the morning haze, mist pooled in the valleys
    for k, (pts, col) in enumerate((([(-20, 262), (60, 228), (150, 246), (240, 210), (330, 236), (430, 200), (520, 224), (620, 214)], "#A8B8D0"),
                                    ([(-20, 286), (90, 256), (180, 274), (300, 244), (400, 268), (500, 250), (620, 266)], "#8EA6B8"),
                                    ([(-20, 312), (120, 286), (240, 304), (360, 280), (480, 300), (620, 290)], "#76927E"))):
        out.append(hill(D, ridge(pts, 1903 + k, 6, 4), 470, (lt(col, 0.2), col, dk(col, 0.2)), 1906 + k, inkw=0, sop=(0.08, 0.22)))
        fid = D.nid()
        D.defs.append(soft_filter(fid, 6))
        out.append(f'<path d="{blob(300, pts[-1][1] + 30, 380, 16, 1909 + k, 0.25, 18)}" fill="#FFFFFF" opacity="0.55" filter="url(#{fid})"/>')
    # the far slope with its terraces (small, hazy), a tree-lined spur and a cluster of bale on the ridge
    far = contour_set(1910, 8, 304, 366, -20, 620, lambda x, t: -26 * ((x - 330) / 330) ** 2 * (1 - 0.5 * t) + 12 * t * math.exp(-((x - 200) / 70) ** 2), amp=2)
    out.append(terrace_slope(D, 1911, far, SKY, light_from=-1, water=0.6))
    for k, (x, b, s_) in enumerate(((392, 306, 0.6), (420, 302, 0.7), (446, 308, 0.62))):
        out.append(ifugao_hut(D, x, b, s_, 1912 + k, haze=0.35))
    out.append(dab_crown(D, 520, 300, 70, 20, [("#7A9A7A", "#5A7A62", "#3E5A4A")], 1915, n=50, size=(4, 8), inkw=0))
    # the near amphitheatre: big sweeping terraces filling the foreground, a bowl that dips in the middle
    def land(x, t):
        spurs = 46 * math.exp(-((x - 110) / 80) ** 2) + 58 * math.exp(-((x - 450) / 95) ** 2) - 30 * math.exp(-((x - 290) / 60) ** 2)
        return spurs * (0.25 + 0.95 * t) - 40 * ((x - 280) / 340) ** 2 * (1 - 0.4 * t)
    near = contour_set(1916, 12, 372, 650, -40, 640, land, amp=2.5, power=1.3)
    out.append(terrace_slope(D, 1917, near, SKY, light_from=-1, water=0.45))
    # clumps of trees on the spur crests
    for k, (x, y, rx_) in enumerate(((112, 446, 34), (452, 470, 40), (470, 404, 26))):
        out.append(dab_crown(D, x, y, rx_, rx_ * 0.6, [("#6A9A4A", "#3E6A2E", "#22401E")], 1925 + k, n=40, size=(4, 8), inkw=0))
    # morning mist drifting low across the middle terraces
    fid = D.nid()
    D.defs.append(soft_filter(fid, 9))
    out.append(f'<g filter="url(#{fid})"><path d="{blob(220, 398, 300, 14, 1920, 0.3, 18)}" fill="#FFFFFF" opacity="0.6"/>'
               f'<path d="{blob(500, 430, 180, 10, 1921, 0.3, 14)}" fill="#FFFFFF" opacity="0.45"/></g>')
    # an egret lifting off over the near paddies
    out.append(egret_flying(476, 500, 1.0, 1922))
    out.append(letters(D, 300, 126, "Banaue", DMS, 120, "#2E5A2A", ["#3E7A3A", "#1A3A1A", "#5A9A4A"], 1930, max_w=380,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8E8B0"))
    out.append(ruled(300, 166, "HAGDAN-HAGDANG PALAYAN · IFUGAO", "#5A4A2A", font=JOS, size=17, ls=4, line_w=18, gap=10, max_w=420))
    return finish_b(D, out, 1931)


def egret_flying(x, y, s, seed):
    """A white egret in flight: long neck folded into an S, legs trailing, broad wings mid-beat."""
    P = lambda a, b: (x + a * s, y + b * s)
    out = []
    wing_up = [P(-4, -2), P(-14, -22), P(-30, -36), P(-40, -40), P(-30, -26), P(-18, -10), P(0, -2)]
    wing_dn = [P(2, 0), P(16, -14), P(34, -20), P(46, -18), P(30, -8), P(14, 2)]
    body = [P(-16, 2), P(-4, -4), P(10, -2), P(18, 2), P(8, 6), P(-10, 6)]
    neck = [P(16, 0), P(24, -6), P(22, -12), P(28, -16), P(36, -14)]
    out.append(f'<path d="{smooth_closed(wing_up)}" fill="#E8EEF2"/><path d="{smooth_closed(wing_dn)}" fill="#F8FAFC"/>')
    out.append(f'<path d="{smooth_closed(body)}" fill="#FFFFFF"/>')
    out.append(taper(neck, 4 * s, 2.4 * s, "#FFFFFF"))
    out.append(taper([P(36, -14), P(46, -12)], 1.6 * s, 0.6, "#E8B83A"))
    out.append(taper([P(-14, 4), P(-34, 10)], 1.4 * s, 1 * s, "#2A2A2A"))
    out.append(f'<path d="{smooth_open(wing_up[1:5])}" stroke="#A8B4C0" stroke-width="1" fill="none" opacity="0.6"/>')
    return "".join(out)


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
    SKY = [(0, "#2E7ACA"), (0.3, "#6AAEE0"), (0.55, "#B8E0F0"), (0.62, "#E8F6F4")]
    out = [sky_paint(D, SKY, 2001, 380, n=90)]
    out.append(cloud_bank(D, 470, 250, 200, 70, 2002, lit="#FFFFFF", mid="#EEF6FC", shade="#9AB4D0", light_dir=-1, op=0.95))
    out.append(cloud_bank(D, 140, 286, 150, 44, 2003, lit="#FFFFFF", mid="#EEF6FC", shade="#9AB4D0", light_dir=-1, op=0.85))
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
    D.defs.append(ripple_filter("ph-en-rip", 5, 8, "0.006 0.1", 0.8))
    for pts, sd in ((left, 2012), (right, 2013)):
        refl = [(x, 360 + (360 - y) * 0.5) for x, y in pts]
        out.append(f'<path d="{smooth_closed(refl)}" fill="#14505E" opacity="0.32" filter="url(#ph-en-rip)"/>')
    # sun glitter and the clear water showing the coral and sand below in the shallows
    rg_ = random.Random(2016)
    for k in range(60):
        y = 366 + (k / 60) ** 1.4 * 170
        x = rg_.uniform(140, 520)
        L = rg_.uniform(6, 22) * (0.6 + (y - 366) / 200)
        out.append(taper([(x, y), (x + L, y + 0.4)], 0.6, 1.8, "#FFFFFF", rg_.uniform(0.35, 0.8)))
    for k in range(14):
        x, y = rg_.uniform(20, 580), rg_.uniform(500, 540)
        out.append(f'<path d="{blob(x, y, rg_.uniform(10, 24), rg_.uniform(3, 6), 2017 + k, 0.3, 10)}" fill="{rg_.choice(["#3AA8A0", "#8AD8C0", "#2A8A90"])}" opacity="0.35"/>')
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
    rnd = random.Random(2100)
    SKY = [(0, "#18204E"), (0.18, "#2E3A78"), (0.3, "#7A5A9A"), (0.38, "#E8867A"), (0.44, "#FFC48A")]
    out = [sky_paint(D, SKY, 2101, 300, n=80)]
    for k in range(6):
        out.append(sparkle(rnd.uniform(40, 560), rnd.uniform(20, 90), rnd.uniform(2, 3.5), "#FFF4E0", 0.8))
    # neighbours' rooflines and a mango tree in silhouette, a power pole with its wires
    out.append(f'<path d="{pd([(-10, 250), (-10, 196), (40, 170), (92, 196), (92, 250)])}" fill="#2A2850"/>')
    out.append(f'<rect x="20" y="210" width="12" height="14" fill="#FFC870" opacity="0.8"/>')
    out.append(dab_crown(D, 560, 200, 80, 60, [("#3A3A62", "#2A2A50", "#1E1E3E")], 2102, n=70, size=(8, 16), inkw=0))
    out.append(taper([(536, 300), (530, 120)], 7, 5, "#1E1C3A"))
    out.append(taper([(500, 132), (566, 132)], 4, 4, "#1E1C3A"))
    for k, (y0, sag) in enumerate(((134, 26), (140, 34), (150, 22))):
        pts = [(530 - 560 * t / 12, y0 + sag * 4 * (t / 12) * (1 - t / 12) + 18 * t / 12) for t in range(13)]
        out.append(f'<path d="{smooth_open(pts)}" fill="none" stroke="#1E1C3A" stroke-width="1.4" opacity="0.9"/>')
    # the store front: a mint-painted plywood wall under a corrugated roof edge
    wall_d = pd([(70, 214), (600, 214), (600, 520), (70, 520)])
    out.append(f'<path d="{wall_d}" fill="#7AB8A8"/>')
    out.append(clipped(D, wall_d, [brush_field(2103, (40, 214, 600, 520), ["#9AD0C0", "#5A9A8C", "#B8E0D0", "#4A8478"], 200, -88, (14, 50), (2, 6), (0.15, 0.4)),
                                   f'<path d="M 230 214 L 230 520 M 400 214 L 400 520" stroke="#3E7A6C" stroke-width="2" opacity="0.5"/>',
                                   streaks_down(2104, (70, 214, 600, 520), "#4A6A60")]))
    # warm light of the bulb on the wall, cool dusk at the edges
    out.append(f'<path d="{wall_d}" fill="{D.rad([(0, "#FFD898", 0.55), (0.45, "#FFC070", 0.18), (1, "#1E2850", 0.45)], 0.48, 0.32, 0.75)}"/>')
    # side wall of the store receding to the left (in shade)
    side = [(70, 214), (70, 520), (8, 548), (8, 230)]
    out.append(f'<path d="{pd(side)}" fill="#4E7A80"/>')
    out.append(f'<path d="{pd(side)}" fill="{D.lin([(0, "#1E2850", 0.55), (1, "#1E2850", 0.2)], 0, 0, 1, 0)}"/>')
    out.append(clipped(D, pd(side), brush_field(2105, (0, 210, 72, 550), ["#6A9A9A", "#2E4A58"], 30, -80, (14, 40), (2, 4), (0.15, 0.35))))
    # roof edge: corrugated GI sheets seen from below, rusty
    roof = [(0, 228), (60, 200), (610, 196), (610, 214), (70, 220), (8, 246)]
    out.append(f'<path d="{pd([(40, 196), (610, 190), (610, 216), (70, 222)])}" fill="#8A8E98"/>')
    rr = []
    for k in range(30):
        x = 70 + k * 19
        rr.append(f'<path d="M {x:.1f} 196 L {x + 2:.1f} 220" stroke="{["#C8CCD4", "#5A5E68"][k % 2]}" stroke-width="5" opacity="0.6"/>')
        if rnd.random() < 0.5:
            rr.append(f'<path d="M {x + rnd.uniform(-4, 4):.1f} 214 l 0 {rnd.uniform(6, 16):.1f}" stroke="#A8582A" stroke-width="{rnd.uniform(2, 4):.1f}" opacity="0.5" stroke-linecap="round"/>')
    out.append(clipped(D, pd([(40, 196), (610, 190), (610, 216), (70, 222)]), rr))
    out.append(f'<path d="M 70 222 L 610 216" stroke="#2A2A3A" stroke-width="3"/>')
    # the store window (recessed), shelves receding toward a vanishing point
    wx0, wy0, wx1, wy1 = 118, 286, 486, 468
    win = pd([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)])
    vp = (300, 360)
    back = (wx0 + 40, wy0 + 26, wx1 - 40, wy1 - 18)
    inside = [f'<path d="{win}" fill="#7A5236"/>',
              f'<path d="{pd([(back[0], back[1]), (back[2], back[1]), (back[2], back[3]), (back[0], back[3])])}" fill="#C89A64"/>',
              f'<path d="{pd([(wx0, wy0), (back[0], back[1]), (back[0], back[3]), (wx0, wy1)])}" fill="#4A2E1E"/>',
              f'<path d="{pd([(wx1, wy0), (back[2], back[1]), (back[2], back[3]), (wx1, wy1)])}" fill="#4A2E1E"/>',
              f'<path d="{pd([(wx0, wy0), (wx1, wy0), (back[2], back[1]), (back[0], back[1])])}" fill="#3A2416"/>',
              soft_glow(D, 300, 318, 260, "#FFE0A0", 0.8)]
    # three shelves: plank edge + receding top
    shelf_y = [348, 404, 452]
    for k, y in enumerate(shelf_y):
        by = back[1] + (y - wy0) * (back[3] - back[1]) / (wy1 - wy0)
        inside.append(f'<path d="{pd([(wx0, y), (wx1, y), (back[2], by), (back[0], by)])}" fill="#B07A48"/>')
        inside.append(f'<path d="{pd([(wx0, y), (wx1, y), (wx1, y + 7), (wx0, y + 7)])}" fill="#6A4022"/>')
        inside.append(f'<path d="M {wx0} {y} L {wx1} {y}" stroke="#FFD8A0" stroke-width="1.6" opacity="0.7"/>')
    # top shelf: glass candy jars with coloured lids
    jar_cols = [["#E8304A", "#F6C51E", "#FFFFFF"], ["#2EB05A", "#FFFFFF", "#F28A2A"], ["#8A5AD0", "#EE6A98", "#FFFFFF"], ["#F6C51E", "#C8641E"],
                ["#1E9AD8", "#FFFFFF", "#E8304A"], ["#F28A2A", "#5A3A1A", "#F6E0B0"]]
    for k, x in enumerate(range(150, 470, 54)):
        inside.append(candy_jar(D, x, shelf_y[0], 46, 54, 2110 + k, jar_cols[k % 6], lid=[PULA, BUGHAW, ARAW, ("#7AD08A", "#2E9A4E", "#145A2A")][k % 4]))
    # middle shelf: bottles of vinegar and soy sauce, cans, a tray of eggs
    for k in range(5):
        x = 140 + k * 20
        c = ["#3A1A0A", "#E8D8A0", "#3A1A0A", "#C8302A", "#E8D8A0"][k]
        bt = [(x - 7, 404), (x - 7, 372), (x - 3, 364), (x - 3, 354), (x + 3, 354), (x + 3, 364), (x + 7, 372), (x + 7, 404)]
        inside.append(f'<path d="{smooth_closed(bt)}" fill="{c}" opacity="0.92"/><path d="M {x - 4} 400 L {x - 4} 372" stroke="#FFFFFF" stroke-width="1.6" opacity="0.45"/>'
                      f'<rect x="{x - 7}" y="380" width="14" height="10" fill="#F2E8D0" opacity="0.85"/><rect x="{x - 3}" y="351" width="6" height="4" fill="#C8302A"/>')
    for k in range(6):
        x = 254 + k * 19
        c = ["#C8302A", "#1E6AC8", "#F2B21E", "#2E8A4A", "#C8302A", "#E8E0D0"][k]
        inside.append(f'<rect x="{x - 8}" y="380" width="16" height="24" fill="{c}"/><rect x="{x - 8}" y="380" width="16" height="3" fill="#D8DEE6"/>'
                      f'<rect x="{x - 8}" y="388" width="16" height="7" fill="#FFFFFF" opacity="0.6"/><path d="M {x - 6} 382 L {x - 6} 402" stroke="#FFFFFF" stroke-width="1.4" opacity="0.4"/>')
    inside.append(f'<path d="{pd([(378, 404), (466, 404), (462, 396), (382, 396)])}" fill="#C8A87A"/>')
    for k in range(8):
        x = 386 + (k % 4) * 20 + (k // 4) * 8
        y = 392 - (k // 4) * 6
        inside.append(f'<path d="{blob(x, y, 7.5, 9, 2140 + k, 0.03, 10)}" fill="#F6E4C8"/><path d="{blob(x - 2, y - 3, 2.5, 3.5, 2150 + k, 0.1, 8)}" fill="#FFFFFF" opacity="0.7"/>')
    # bottom shelf: pandesal in plastic bags, chips
    for k in range(5):
        x = 150 + k * 34
        inside.append(f'<path d="{blob(x, 438, 15, 13, 2155 + k, 0.08, 10)}" fill="#EEF2F6" opacity="0.7"/><path d="{blob(x, 440, 11, 9, 2160 + k, 0.1, 10)}" fill="#D89A50"/>'
                      f'<path d="{blob(x - 3, 436, 4, 3, 2165 + k, 0.1, 8)}" fill="#F2C890" opacity="0.8"/>')
    for k in range(4):
        x = 350 + k * 32
        c = ["#E8304A", "#F6C51E", "#1E9AD8", "#2EB05A"][k]
        inside.append(f'<path d="{smooth_closed([(x - 13, 452), (x - 14, 422), (x + 14, 422), (x + 13, 452)])}" fill="{c}"/>'
                      f'<circle cx="{x}" cy="437" r="6" fill="#FFFFFF" opacity="0.7"/><path d="M {x - 10} 426 L {x - 10} 448" stroke="#FFFFFF" stroke-width="2" opacity="0.4"/>')
    inside.append(f'<path d="{win}" fill="{D.rad([(0, "#FFE0A0", 0.12), (0.6, "#2A1408", 0.05), (1, "#1A0A04", 0.35)], 0.5, 0.3, 0.8)}"/>')
    out.append(clipped(D, win, inside))
    # the iron grille: vertical bars and a fine wire mesh, the little opening where you pay
    hole = (250, 420, 350, 468)
    grille = []
    for k in range(17):
        x = wx0 + 6 + k * (wx1 - wx0 - 12) / 16
        if hole[0] < x < hole[2]:
            grille.append(f'<path d="M {x:.1f} {wy0} L {x:.1f} {hole[1]}" stroke="#20202A" stroke-width="3.2"/><path d="M {x - 1:.1f} {wy0} L {x - 1:.1f} {hole[1]}" stroke="#FFD8A0" stroke-width="1" opacity="0.5"/>')
        else:
            grille.append(f'<path d="M {x:.1f} {wy0} L {x:.1f} {wy1}" stroke="#20202A" stroke-width="3.2"/><path d="M {x - 1:.1f} {wy0} L {x - 1:.1f} {wy1}" stroke="#FFD8A0" stroke-width="1" opacity="0.5"/>')
    for y in (wy0 + 4, 362, hole[1]):
        grille.append(f'<path d="M {wx0} {y} L {wx1} {y}" stroke="#20202A" stroke-width="4"/><path d="M {wx0} {y - 1.5} L {wx1} {y - 1.5}" stroke="#FFD8A0" stroke-width="1" opacity="0.5"/>')
    mesh = []
    for k in range(-30, 40):
        x = wx0 + k * 11
        mesh.append(f"M{x} {wy0}L{x + (wy1 - wy0)} {wy1}M{x} {wy1}L{x + (wy1 - wy0)} {wy0}")
    holed = f"M 0 0 L 600 0 L 600 600 L 0 600 Z M {hole[0]} {hole[1]} L {hole[2]} {hole[1]} L {hole[2]} {hole[3]} L {hole[0]} {hole[3]} Z"
    out.append(f'<g {D.clip(f"<path d=\"{win}\"/>")}><g {D.clip(f"<path d=\"{holed}\" clip-rule=\"evenodd\"/>")}>'
               f'<path d="{"".join(mesh)}" stroke="#2A2A34" stroke-width="0.9" opacity="0.5" fill="none"/>{"".join(grille)}</g></g>')
    # window frame and the counter ledge in front of the opening
    for (x0, y0, x1, y1) in ((wx0 - 14, wy0 - 12, wx1 + 14, wy0), (wx0 - 14, wy0 - 12, wx0, wy1 + 2), (wx1, wy0 - 12, wx1 + 14, wy1 + 2)):
        out.append(painted(D, rect_pts(x0, y0, x1, y1, 16, int(x0 + y0), 0.4), NARRA, int(x0 + y0), sdir=(0.3, 1), sk=0.2, angle=0 if y1 - y0 < 20 else -90, n=12, inkw=0, hi=0.35))
    out.append(painted(D, rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 16, 20, 2184, 0.5), NARRA, 2184, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=0, hi=0.45))
    out.append(f'<path d="M {wx0 - 30} {wy1} L {wx1 + 30} {wy1}" stroke="#FFD8A0" stroke-width="2" opacity="0.8"/>')
    out.append(cast(D, 300, wy1 + 22, 220, 8, strength=0.45, seed=2185))
    # on the ledge: a jar of sweets and the handwritten "pabili" price card
    out.append(candy_jar(D, 432, wy1, 40, 46, 2186, ["#F6C51E", "#E8304A", "#FFFFFF"], lid=BUGHAW))
    card = rot(rect_pts(136, wy1 - 34, 226, wy1 - 2, 10, 2187, 0.5), 181, wy1 - 18, -5)
    out.append(painted(D, card, ("#FFF4DC", "#F2E2C0", "#B8A07A"), 2187, sk=0.1, angle=0, n=6, inkw=0, hi=0.3))
    out.append(f'<text x="181" y="{wy1 - 12}" text-anchor="middle" {BEBAS} font-size="{fit_size("BAWAL UTANG", BEBAS, 19, 78, 1)}" letter-spacing="1" fill="#C8241E" transform="rotate(-5 181 {wy1 - 18})">BAWAL UTANG</text>')
    # the awning over the window: corrugated sheet on two brackets, seen from below, lit by the bulb
    aw_top = [(96, 262), (510, 262)]
    aw = [(88, 256), (518, 256), (540, 286), (66, 286)]
    out.append(f'<path d="{pd(aw)}" fill="#6A6E7A"/>')
    awr = []
    for k in range(26):
        x0 = 88 + k * 17
        x1 = 66 + k * 18.8
        awr.append(f'<path d="M {x0:.1f} 256 L {x1:.1f} 286" stroke="{["#B8BCC8", "#3E424E"][k % 2]}" stroke-width="5" opacity="0.6"/>')
    out.append(clipped(D, pd(aw), awr + [f'<path d="{pd(aw)}" fill="{D.lin([(0, "#2A2A3A", 0.5), (1, "#FFC070", 0.35)], 0, 0, 0, 1)}"/>']))
    out.append(f'<path d="M 66 286 L 540 286" stroke="#2A2A38" stroke-width="3"/>')
    for x in (110, 494):
        out.append(taper([(x, 256), (x + (8 if x < 300 else -8), 290)], 4, 4, "#3A2414"))
    # sachet strips and snack packs hanging from the awning, a bare bulb glowing
    for k, (x, col, n) in enumerate(((128, "#E8304A", 6), (150, "#1E9AD8", 5), (172, "#F6C51E", 7), (430, "#2EB05A", 6), (452, "#E8304A", 5), (474, "#7A4AC8", 6))):
        out.append(sachet_strip(x, 288, n, 19, 13, 2170 + k, col))
    for k, x in enumerate((200, 404)):
        c = ["#F28A2A", "#2E9AD8"][k]
        out.append(f'<path d="M {x} 286 L {x} 296" stroke="#3A3A3A" stroke-width="1.2"/>')
        out.append(f'<path d="{smooth_closed([(x - 13, 296), (x + 13, 296), (x + 15, 334), (x - 15, 334)])}" fill="{c}"/><circle cx="{x}" cy="316" r="6" fill="#FFFFFF" opacity="0.75"/>'
                   f'<path d="M {x - 11} 300 L {x - 12} 330" stroke="#FFFFFF" stroke-width="2" opacity="0.4"/>')
    out.append(f'<path d="M 300 286 L 300 300" stroke="#2A2A2A" stroke-width="1.6"/>')
    out.append(soft_glow(D, 300, 310, 120, "#FFE6A0", 0.55))
    out.append(f'<path d="{blob(300, 308, 7, 9, 2177, 0.04, 10)}" fill="#FFFBE6"/><rect x="296" y="298" width="8" height="5" fill="#8A8A8A"/>')
    # under the window: a wooden bench, plants in old cans, the ground in the store's warm light
    ground = "M -10 520 L 610 520 L 610 610 L -10 610 Z"
    out.append(f'<path d="{ground}" fill="#3A3A50"/>')
    out.append(f'<path d="{ground}" fill="{D.rad([(0, "#E8A868", 0.55), (1, "#E8A868", 0)], 0.5, 0.0, 0.6)}"/>')
    out.append(clipped(D, ground, brush_field(2188, (-40, 520, 600, 610), ["#5A5A70", "#2A2A3A", "#C89A70"], 60, 0, (30, 100), (1.5, 4), (0.15, 0.35), 0.05, 3)))
    out.append(f'<path d="{pd([(8, 548), (70, 520), (600, 520), (600, 526), (70, 526), (8, 554)])}" fill="#2A2A3A" opacity="0.5"/>')
    bench = [(330, 500), (560, 500), (560, 512), (330, 512)]
    out.append(cast(D, 450, 545, 140, 10, strength=0.4, seed=2189))
    out.append(painted(D, rect_pts(330, 496, 560, 510, 14, 2189, 0.4), NARRA, 2189, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=0, hi=0.45))
    for x in (346, 544):
        out.append(taper([(x, 510), (x - 2, 548)], 7, 7, "#3A1E0E"))
    # a cold soft drink in a plastic bag with a straw (how the store sells it), and a pair of tsinelas under the bench
    out.append(f'<path d="{smooth_closed([(470, 496), (466, 470), (472, 458), (488, 458), (494, 470), (490, 496)])}" fill="#F2F4F8" opacity="0.55"/>'
               f'<path d="{smooth_closed([(472, 494), (470, 474), (490, 474), (488, 494)])}" fill="#7A2A1A" opacity="0.9"/>'
               f'<path d="M 482 476 L 488 446" stroke="#E8304A" stroke-width="2.2"/><path d="M 471 460 q 9 -10 18 0" stroke="#F2F4F8" stroke-width="1.6" fill="none" opacity="0.7"/>')
    for k, x in enumerate((420, 440)):
        out.append(f'<path d="{blob(x, 552, 10, 3.4, 2190 + k, 0.08, 10, -5)}" fill="#E8508A"/><path d="{blob(x - 1, 551, 7, 2, 2192 + k, 0.08, 10, -5)}" fill="#FFB8D0" opacity="0.6"/>')
    for k, x in enumerate((96, 150, 196)):
        h_ = [42, 34, 46][k]
        out.append(painted(D, rect_pts(x - 18, 520 - h_ + 40, x + 18, 520 + 18, 8, 2194 + k, 0.3), STEEL, 2194 + k, sdir=(0.9, 0.3), sk=0.25, angle=-90, n=4, inkw=0, hi=0.5))
        out.append(f'<path d="M {x - 18} {520 - h_ + 48} L {x + 18} {520 - h_ + 48}" stroke="#C8302A" stroke-width="5" opacity="0.7"/>')
        out.append(croton(D, x, 520 - h_ + 44, 34, 2197 + k))
    out.append(letters(D, 300, 126, "Sari-Sari Store", DMS, 76, "#FFF0D8", ["#FFFFFF", "#FFE0B8", "#F8D0A8"], 2106, max_w=460,
                       shadow="#121838", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "PABILI PO!", "#FFD06A", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 2196)


def croton(D, cx, base, s, seed):
    """Croton (San Francisco) plant: glossy lance leaves splashed red, yellow and green, with pale veins."""
    rnd = random.Random(seed)
    out = []
    pals = [("#F6D84A", "#C8A020", "#7A5A0A"), ("#E85A3A", "#B82A1E", "#6A1008"), ("#7AC04A", "#3E8A2E", "#1A4A1A"), ("#F2A040", "#C86A1E", "#7A3A0A")]
    for k in range(11):
        a = math.radians(-90 + rnd.uniform(-70, 70))
        L = s * rnd.uniform(0.6, 1.0)
        W = L * 0.22
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        tip = (cx + ux * L, base + uy * L)
        pts = [(cx, base)] + [(cx + ux * L * t + nx * W * math.sin(math.pi * t) * (1 - 0.3 * t), base + uy * L * t + ny * W * math.sin(math.pi * t) * (1 - 0.3 * t)) for t in (0.2, 0.45, 0.7, 0.9)] + [tip] + \
              [(cx + ux * L * t - nx * W * math.sin(math.pi * t) * (1 - 0.3 * t), base + uy * L * t - ny * W * math.sin(math.pi * t) * (1 - 0.3 * t)) for t in (0.9, 0.7, 0.45, 0.2)]
        pal = rnd.choice(pals)
        d = smooth_closed(pts)
        out.append(f'<path d="{d}" fill="{pal[1]}"/>')
        out.append(f'<path d="{d}" fill="{D.lin([(0, pal[0], 0.8), (0.5, pal[0], 0), (1, pal[2], 0.5)], 0, 0, 1, 1)}"/>')
        out.append(f'<path d="M {cx:.1f} {base:.1f} L {tip[0]:.1f} {tip[1]:.1f}" stroke="#FFF0A0" stroke-width="1.1" opacity="0.7"/>')
        if rnd.random() < 0.5:
            for j in range(3):
                t = rnd.uniform(0.2, 0.8)
                out.append(f'<circle cx="{cx + ux * L * t + nx * W * rnd.uniform(-0.5, 0.5):.1f}" cy="{base + uy * L * t + ny * W * rnd.uniform(-0.5, 0.5):.1f}" r="1.4" fill="#FFE860" opacity="0.8"/>')
    return "".join(out)


def streaks_down(seed, box, col, n=40):
    """Rain-stain streaks running down a weathered wall."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y0 + (y1 - y0) * 0.4)
        L = rnd.uniform(20, 90)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-2, 2):.1f} {L / 2:.1f} {rnd.uniform(-3, 3):.1f} {L:.1f}" stroke="{col}" stroke-width="{rnd.uniform(1, 3):.1f}" opacity="{rnd.uniform(0.08, 0.2):.2f}" fill="none"/>')
    return "".join(out)


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


def limb(a, b, c, w0, w1, w2):
    """A tapered limb through three joints (shoulder/hip -> elbow/knee -> wrist/ankle) as a closed outline."""
    pts = catmull([a, b, c], 6)
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        p0 = pts[max(0, i - 1)]
        p1 = pts[min(n - 1, i + 1)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t * 2) if t < 0.5 else (w1 + (w2 - w1) * (t - 0.5) * 2)
        left.append((x - dy / L * w / 2, y + dx / L * w / 2))
        right.append((x + dy / L * w / 2, y - dx / L * w / 2))
    return left + right[::-1]


def grip(D, x, y, ang, s, seed, col, pad, light):
    """A tarsier hand / foot wrapped on a branch: long slender fingers ending in round sticky pads."""
    out = []
    rnd = random.Random(seed)
    for k in range(4):
        a = math.radians(ang + (k - 1.5) * 14)
        L = s * rnd.uniform(0.8, 1.05) * (0.85 if k in (0, 3) else 1)
        bx, by = x + math.cos(a) * 3, y + math.sin(a) * 3
        mx, my = bx + math.cos(a) * L * 0.55, by + math.sin(a) * L * 0.55 + 2
        ex, ey = bx + math.cos(a + 0.35) * L, by + math.sin(a + 0.35) * L
        out.append(taper([(bx, by), (mx, my), (ex, ey)], max(2.6, s * 0.2), max(1.6, s * 0.14), col))
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{s * 0.17:.1f}" ry="{s * 0.15:.1f}" fill="{pad}"/>'
                   f'<ellipse cx="{ex - s * 0.04:.1f}" cy="{ey - s * 0.05:.1f}" rx="{s * 0.07:.1f}" ry="{s * 0.05:.1f}" fill="{light}" opacity="0.7"/>')
    return "".join(out)


@design("tarsier")
def tarsier():
    D = Doc2("ph-ts")
    rnd = random.Random(2200)
    out = [paper(D.nid(), "#F4ECD8", FLECK, 2201)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0), (1, "#8A6A4A", 0.12)], 0.5, 0.5, 0.75)}"/>')
    # the painted study: a rectangle of Bohol forest at dusk, edges left loose like a gouache sketch on paper
    px0, py0, px1, py1 = 84, 112, 516, 462
    panel = pd(jitter(densify([(px0, py0), (px1, py0), (px1, py1), (px0, py1)], 14), 2201, 2.2))
    inner = [f'<path d="{panel}" fill="{D.lin([(0, "#2E4A3A"), (0.55, "#1E3A2E"), (1, "#122A22")])}"/>',
             soft_glow(D, 430, 150, 200, "#C8E0A0", 0.45),
             bokeh(D, 2202, (px0, py0, px1, py1), ["#B8D890", "#6A9A5A", "#E8F0C0", "#3E6A4A"], 22, (8, 26), (0.12, 0.35), 4)]
    # soft out-of-focus leaves behind
    fid = D.nid()
    D.defs.append(soft_filter(fid, 2.5))
    lv = []
    for k in range(14):
        x, y = rnd.uniform(px0, px1), rnd.uniform(py0, py1)
        lv.append(leaf_simple(D, x, y, rnd.uniform(40, 80), rnd.uniform(12, 20), rnd.uniform(0, 360),
                              rnd.choice([("#5A8A4A", "#3A6A3A", "#1E4A2A"), ("#4A7A4A", "#2E5A3A", "#163A26")]), 2203 + k, inkw=0))
    inner.append(f'<g filter="url(#{fid})" opacity="0.8">{"".join(lv)}</g>')
    # the trunk: a slim vertical sapling, bark painted with the light from the upper right
    br = [(228, 480), (236, 400), (240, 300), (234, 200), (242, 100)]
    inner.append(taper(br, 40, 32, "#5A4632"))
    inner.append(taper([(x + 10, y) for x, y in br], 11, 8, "#A88A64", 0.8))
    inner.append(taper([(x - 12, y) for x, y in br], 9, 7, "#2A2018", 0.7))
    bark = []
    for _ in range(80):
        t = rnd.random()
        y = 100 + t * 380
        x = 236 + math.sin(t * 3) * 4 + rnd.uniform(-14, 14)
        bark.append(f"M{x:.1f} {y:.1f}l{rnd.uniform(-1, 1):.1f} {rnd.uniform(4, 12):.1f}")
    inner.append(f'<path d="{"".join(bark)}" stroke="#2E241A" stroke-width="1.2" opacity="0.6" fill="none"/>')
    inner.append(dry_brush(2209, [(248, 110), (252, 300), (244, 470)], 4, "#D8C8A0", 0.55, 3))
    for k, (x, y, a) in enumerate(((246, 150, -30), (232, 176, 210), (244, 440, 25))):
        inner.append(leaf_simple(D, x, y, 66, 18, a, ("#8AC06A", "#3E7A3A", "#1A4A22"), 2210 + k, inkw=0))
    # ---------------- the tarsier: body in profile against the trunk, head turned to look at us ----------------
    FUR = ("#B8A08A", "#8A7462", "#5A4636", "#E2D2BE")     # light, base, dark, belly/highlight
    T = []
    # tail hanging down along the trunk
    T.append(taper([(330, 408), (340, 440), (352, 470), (356, 500)], 5.5, 3, "#7A6458"))
    # far arm (mostly hidden) reaching to the trunk
    T.append(taper([(282, 300), (268, 316), (254, 312)], 9, 7, FUR[2]))
    T.append(grip(D, 254, 312, 185, 15, 2226, "#6A5448", "#9A7C70", "#E8D0C0"))
    # body: an egg in profile, belly toward the trunk (left), back to the right
    torso = blob_pts(306, 352, 50, 70, 2220, 0.03, 22, rot=-12)
    td = smooth_closed(torso)
    T.append(f'<path d="{td}" fill="{FUR[1]}"/>')
    T.append(clipped(D, td, [f'<path d="{blob(268, 340, 14, 40, 2221, 0.06, 16, -12)}" fill="{FUR[3]}" opacity="0.55"/>',
                             fur(2222, (250, 280, 362, 430), [FUR[0], FUR[2], FUR[3], FUR[1]], 900, lambda x, y: 100 - (y - 352) * 0.1, (5, 10), (0.7, 1.4)),
                             f'<path d="{td}" fill="{D.lin([(0, "#1A120C", 0.0), (0.55, "#1A120C", 0.0), (1, "#1A120C", 0.4)], 0, 0, 1, 0.3)}"/>']))
    T.append(fuzzy_edge(2223, torso, [FUR[1], FUR[0], FUR[2]], 1.4, (3, 7)))
    # hind leg folded like a frog's: huge thigh up to the knee by the trunk, shin back down, then the long tarsus
    tarsus = limb((334, 418), (300, 440), (262, 448), 13, 9, 7)
    T.append(f'<path d="{smooth_closed(tarsus)}" fill="#7A6458"/>')
    T.append(clipped(D, smooth_closed(tarsus), [fur(2246, (250, 400, 345, 460), [FUR[0], FUR[2]], 160, lambda x, y: 160, (3, 5), (0.5, 1.0))]))
    T.append(f'<path d="M 330 424 Q 300 438 266 444" stroke="#C8A898" stroke-width="1.6" fill="none" opacity="0.55"/>')
    thigh = blob_pts(300, 390, 50, 30, 2224, 0.04, 20, rot=-28)
    tl = smooth_closed(thigh)
    T.append(f'<path d="{tl}" fill="{FUR[1]}"/>')
    T.append(clipped(D, tl, [fur(2224, (244, 350, 356, 432), [FUR[0], FUR[2], FUR[1], FUR[3]], 700, lambda x, y: 205, (5, 9), (0.7, 1.3)),
                             f'<path d="{tl}" fill="{D.lin([(0, "#FFF0D8", 0.3), (0.5, "#FFF0D8", 0), (1, "#1A120C", 0.4)], 0, 0, 0, 1)}"/>']))
    T.append(fuzzy_edge(2225, thigh, [FUR[1], FUR[0]], 1.3, (3, 6)))
    T.append(grip(D, 260, 448, 190, 18, 2227, "#8A7064", "#C8A898", "#FFE8D8"))
    # near arm: shoulder, elbow tucked, long fingers spread on the bark
    arm = limb((290, 312), (300, 336), (256, 334), 20, 14, 10)
    ad = smooth_closed(arm)
    T.append(f'<path d="{ad}" fill="{FUR[1]}"/>')
    T.append(clipped(D, ad, [fur(2228, (250, 300, 320, 350), [FUR[0], FUR[2], FUR[3]], 240, lambda x, y: 180, (4, 7), (0.6, 1.1))]))
    T.append(fuzzy_edge(2230, arm, [FUR[1], FUR[0]], 1.0, (2, 5)))
    T.append(grip(D, 256, 334, 175, 18, 2233, "#8A7064", "#C8A898", "#FFE8D8"))
    # ears: big, thin, rounded, the light shining through them
    HX, HY = 300, 236
    for k, (base_, tip, sg) in enumerate((((HX - 34, HY - 30), (HX - 74, HY - 96), -1), ((HX + 36, HY - 34), (HX + 80, HY - 98), 1))):
        bx, by = base_
        ex, ey = tip
        mx, my = (bx + ex) / 2, (by + ey) / 2
        nx, ny = -(ey - by), (ex - bx)
        L = math.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        W = 28
        ear = [(bx - nx * W * 0.6, by - ny * W * 0.6), (mx - nx * W, my - ny * W), (ex - nx * W * 0.45, ey - ny * W * 0.45), (ex, ey),
               (ex + nx * W * 0.5, ey + ny * W * 0.5), (mx + nx * W * 1.0, my + ny * W * 1.0), (bx + nx * W * 0.6, by + ny * W * 0.6)]
        ed = smooth_closed(ear)
        T.append(f'<path d="{ed}" fill="#A8887C"/>')
        T.append(clipped(D, ed, [f'<path d="{blob(mx + nx * 2, my + ny * 2, W * 0.62, L / 2.6, 2234 + k, 0.1, 12, math.degrees(math.atan2(ey - by, ex - bx)) + 90)}" fill="#E8B8A8" opacity="0.65"/>',
                                 f'<path d="M {bx:.1f} {by:.1f} Q {mx + nx * 6:.1f} {my + ny * 6:.1f} {ex:.1f} {ey:.1f} M {bx:.1f} {by:.1f} Q {mx - nx * 10:.1f} {my - ny * 10:.1f} {ex - nx * 8:.1f} {ey - ny * 8:.1f}" '
                                 f'stroke="#B86A6A" stroke-width="1.1" fill="none" opacity="0.6"/>',
                                 f'<path d="{ed}" fill="{D.lin([(0, "#FFE8D8", 0.5 if sg > 0 else 0.1), (1, "#3A2620", 0.3 if sg > 0 else 0.45)], 1, 0, 0, 1)}"/>']))
        T.append(f'<path d="{ed}" fill="none" stroke="#5A3E36" stroke-width="1.4" opacity="0.5"/>')
    # head: wide and round, fur radiating from the face, turned to look straight at us
    head = blob_pts(HX, HY, 66, 58, 2236, 0.03, 24)
    hd = smooth_closed(head)
    T.append(f'<path d="{hd}" fill="{FUR[1]}"/>')
    T.append(clipped(D, hd, [fur(2237, (HX - 70, HY - 62, HX + 70, HY + 62), [FUR[0], FUR[2], FUR[1], FUR[3]], 1200,
                                 lambda x, y: math.degrees(math.atan2(y - HY - 12, x - HX)), (4, 8), (0.6, 1.2)),
                             f'<path d="{blob(HX, HY + 38, 30, 18, 2238, 0.08, 14)}" fill="{FUR[3]}" opacity="0.75"/>',
                             f'<path d="{hd}" fill="{D.lin([(0, "#FFF0D8", 0.35), (0.5, "#FFF0D8", 0), (1, "#1A120C", 0.4)], 1, 0, 0, 1)}"/>']))
    T.append(fuzzy_edge(2239, head, [FUR[1], FUR[0], FUR[2]], 1.6, (3, 7)))
    # the enormous eyes, set in the fur: thin dark lids, amber-brown irises, wide pupils, wet highlights
    for k, ex in enumerate((HX - 28, HX + 28)):
        ey = HY
        T.append(f'<circle cx="{ex}" cy="{ey}" r="28" fill="#4A3628" opacity="0.8"/>')
        T.append(f'<circle cx="{ex}" cy="{ey}" r="26" fill="{D.rad([(0, "#E8B45A"), (0.5, "#B87A2E"), (0.85, "#6A3E16"), (1, "#3A220C")], 0.45, 0.42, 0.55)}"/>')
        rays = "".join(f"M{ex + math.cos(a) * 16:.1f} {ey + math.sin(a) * 16:.1f}L{ex + math.cos(a) * 25:.1f} {ey + math.sin(a) * 25:.1f}"
                       for a in [i / 40 * math.pi * 2 for i in range(40)])
        T.append(f'<path d="{rays}" stroke="#5A3010" stroke-width="0.9" opacity="0.45"/>')
        T.append(f'<circle cx="{ex + 1}" cy="{ey + 1}" r="15" fill="#0E0806"/>')
        T.append(f'<ellipse cx="{ex - 8}" cy="{ey - 9}" rx="6.5" ry="4.8" fill="#FFFFFF" opacity="0.9" transform="rotate(-30 {ex - 8} {ey - 9})"/>')
        T.append(f'<circle cx="{ex + 9}" cy="{ey + 9}" r="2.2" fill="#FFFFFF" opacity="0.5"/>')
        T.append(f'<path d="M {ex - 25} {ey - 6} A 26 26 0 0 1 {ex + 22} {ey - 12}" stroke="#2A1A12" stroke-width="2.4" fill="none" opacity="0.55"/>')
    T.append(f'<path d="M {HX - 5} {HY + 32} Q {HX} {HY + 28} {HX + 5} {HY + 32} Q {HX} {HY + 38} {HX - 5} {HY + 32} Z" fill="#3A2420"/>')
    T.append(f'<path d="M {HX - 12} {HY + 45} Q {HX} {HY + 50} {HX + 13} {HY + 44}" stroke="#3A2420" stroke-width="1.4" fill="none" opacity="0.8"/>')
    inner.append("".join(T))
    # rim light from the upper right on the fur edge
    inner.append(f'<path d="M 356 196 Q 370 226 362 262" stroke="#E8F0C8" stroke-width="2" fill="none" opacity="0.4"/>')
    out.append(clipped(D, panel, inner))
    out.append(f'<path d="{panel}" fill="none" stroke="#3A2A1A" stroke-width="1.6" opacity="0.4"/>')
    out.append(ruled(300, 92, "BOHOL · PILIPINAS", "#2E5A3A", font=JOS, size=15, ls=4, line_w=40, gap=12))
    out.append(letters(D, 300, 512, "tarsier", SERIF_IT, 64, "#2E5A3A", ["#3E7A4A", "#1A3A22", "#5A9A62"], 2240, max_w=300,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8E8C0"))
    out.append(label(300, 536, "CARLITO SYRICHTA", CINZEL, 16, "#7A5A3A", ls=3))
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


def monobloc(C, x, z, face_deg, seed, light_fn, mic=False, scale=1.0):
    """The one-piece white plastic chair of every Filipino party, in perspective. (x, z) = centre of the seat on the
    floor; face_deg = direction the sitter faces (0 = toward +Z / the screen, 180 = toward the camera).
    light_fn(normal) -> colour for a face. Faces are depth-sorted (painter's algorithm)."""
    rnd = random.Random(seed)
    a = math.radians(face_deg)
    fw = (math.sin(a), 0, math.cos(a))          # forward
    rt = (math.cos(a), 0, -math.sin(a))          # right
    up = (0, 1, 0)
    k = scale

    def W(u, v, w):
        return (x + (rt[0] * u + fw[0] * w) * k, v * k, z + (rt[2] * u + fw[2] * w) * k)

    def N(u, v, w):
        return (rt[0] * u + fw[0] * w, v, rt[2] * u + fw[2] * w)

    polys = []   # (pts3, normal, kind)
    # seat (slightly dished, rounded front)
    seat = [W(-0.23, 0.44, -0.2), W(0.23, 0.44, -0.2), W(0.24, 0.45, 0.14), W(0.18, 0.45, 0.22), W(-0.18, 0.45, 0.22), W(-0.24, 0.45, 0.14)]
    polys.append((seat, (0, 1, 0), "seat"))
    seat_front = [W(-0.24, 0.45, 0.14), W(-0.18, 0.45, 0.22), W(0.18, 0.45, 0.22), W(0.24, 0.45, 0.14), W(0.24, 0.38, 0.15), W(0.18, 0.38, 0.23), W(-0.18, 0.38, 0.23), W(-0.24, 0.38, 0.15)]
    polys.append((seat_front, N(0, 0, 1), "skirt"))
    # backrest tilted back, with horizontal slots
    bk = [W(-0.23, 0.46, -0.2), W(0.23, 0.46, -0.2), W(0.22, 0.88, -0.29), W(-0.22, 0.88, -0.29)]
    polys.append((bk, N(0, 0.2, 1), "back"))
    # armrests: from the backrest down to the front leg
    for s_ in (-1, 1):
        arm = [W(s_ * 0.23, 0.64, -0.24), W(s_ * 0.27, 0.64, -0.24), W(s_ * 0.28, 0.62, 0.12), W(s_ * 0.26, 0.4, 0.22), W(s_ * 0.23, 0.4, 0.21), W(s_ * 0.24, 0.6, 0.1)]
        polys.append((arm, N(s_, 0.4, 0), "arm"))
        side = [W(s_ * 0.24, 0.46, -0.2), W(s_ * 0.24, 0.64, -0.23), W(s_ * 0.24, 0.6, 0.1), W(s_ * 0.24, 0.45, 0.14)]
        polys.append((side, N(s_, 0, 0), "side"))
    # legs (front legs continue the armrests; back legs splay backward)
    for s_ in (-1, 1):
        fl = [W(s_ * 0.22, 0.4, 0.2), W(s_ * 0.27, 0.4, 0.21), W(s_ * 0.3, 0.0, 0.27), W(s_ * 0.25, 0.0, 0.26)]
        polys.append((fl, N(0, 0, 1), "leg"))
        bl = [W(s_ * 0.2, 0.42, -0.18), W(s_ * 0.25, 0.42, -0.19), W(s_ * 0.3, 0.0, -0.3), W(s_ * 0.25, 0.0, -0.29)]
        polys.append((bl, N(0, 0, -1), "leg"))
    out = []
    shadow = [C(*W(-0.34, 0, -0.34)), C(*W(0.34, 0, -0.34)), C(*W(0.36, 0, 0.32)), C(*W(-0.36, 0, 0.32))]
    out.append(f'<path d="{smooth_closed(shadow)}" fill="#0E0A16" opacity="0.5"/>')
    def depth(p3):
        return sum(C.depth(*p) for p in p3) / len(p3)
    ex, ey_, ez = C.eye_world()
    for pts3, nrm, kind in sorted(polys, key=lambda t: -depth(t[0])):
        pts = [C(*p) for p in pts3]
        cxp = sum(p[0] for p in pts3) / len(pts3)
        cyp = sum(p[1] for p in pts3) / len(pts3)
        czp = sum(p[2] for p in pts3) / len(pts3)
        if nrm[0] * (ex - cxp) + nrm[1] * (ey_ - cyp) + nrm[2] * (ez - czp) < 0:
            nrm = (-nrm[0], -nrm[1], -nrm[2])
        col = light_fn(nrm, kind)
        d = smooth_closed(pts) if kind in ("seat", "back") else pd(pts)
        out.append(f'<path d="{d}" fill="{col}"/>')
        if kind == "back":
            # slots, then a lit top edge
            for j in range(4):
                v0 = 0.56 + j * 0.075
                sl = [C(*W(-0.15, v0, -0.2 - (v0 - 0.46) * 0.21)), C(*W(0.15, v0, -0.2 - (v0 - 0.46) * 0.21)),
                      C(*W(0.15, v0 + 0.035, -0.2 - (v0 + 0.035 - 0.46) * 0.21)), C(*W(-0.15, v0 + 0.035, -0.2 - (v0 + 0.035 - 0.46) * 0.21))]
                out.append(f'<path d="{smooth_closed(sl)}" fill="#1A1A2E" opacity="0.75"/>')
            out.append(taper([C(*W(-0.22, 0.88, -0.29)), C(*W(0, 0.885, -0.29)), C(*W(0.22, 0.88, -0.29))], 2.4, 2.4, "#FFE6B8", 0.75))
            for s_ in (-1, 1):
                out.append(taper([C(*W(s_ * 0.225, 0.87, -0.29)), C(*W(s_ * 0.235, 0.66, -0.245))], 2.2, 1.0, "#BFE0FF", 0.7))
        if kind == "seat":
            out.append(taper([C(*W(-0.2, 0.45, 0.2)), C(*W(0.2, 0.45, 0.2))], 2, 2, "#FFFFFF", 0.5))
    if mic:
        p = C(*W(0.02, 0.46, 0.0))
        q = C(*W(0.1, 0.46, 0.12))
        out.append(taper([p, q], 5, 7, "#1E2028"))
        out.append(f'<circle cx="{q[0] + (q[0] - p[0]) * 0.35:.1f}" cy="{q[1] + (q[1] - p[1]) * 0.35:.1f}" r="7" fill="#9AA4B8"/>'
                   f'<circle cx="{q[0] + (q[0] - p[0]) * 0.35 - 2:.1f}" cy="{q[1] + (q[1] - p[1]) * 0.35 - 2.5:.1f}" r="2.4" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("isa-pang-kanta")
def isa_pang_kanta():
    D = Doc2("ph-ka")
    cy = 318
    C = Cam3(f=560, cx=300, cy=cy, yaw=-5, pitch=0, pos=(0.25, 1.22, -1.2))
    WALL_Z = 4.2
    out = []
    # night sky above the carport roof edge, then the back wall of the house
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#120E2A"), (0.5, "#1E1838"), (1, "#0E0A18")])}"/>')
    wall_q = [C(-4, 2.75, WALL_Z), C(4, 2.75, WALL_Z), C(4, 0, WALL_Z), C(-4, 0, WALL_Z)]
    out.append(f'<path d="{pd(wall_q)}" fill="#4E7A72"/>')
    # the screen's light spreading on the wall, warm bulbs above
    sc_c = C(0, 1.25, WALL_Z - 0.3)
    out.append(soft_glow(D, sc_c[0], sc_c[1], 260, "#7AB8FF", 0.65))
    out.append(clipped(D, pd(wall_q), brush_field(2301, (-20, wall_q[0][1], 620, wall_q[2][1]), ["#6A9A90", "#2E4A4E", "#8AC0C8", "#3A5A5A"], 140, -88, (12, 46), (2, 6), (0.12, 0.35))))
    out.append(f'<path d="{pd(wall_q)}" fill="{D.lin([(0, "#FFB060", 0.3), (0.3, "#FFB060", 0.0), (1, "#0E0A1E", 0.35)], 0, 0, 0, 1)}"/>')
    # a window with lace curtain (left) and a wall clock + family photos (right)
    win = [C(-2.6, 2.3, WALL_Z - 0.01), C(-1.5, 2.3, WALL_Z - 0.01), C(-1.5, 1.2, WALL_Z - 0.01), C(-2.6, 1.2, WALL_Z - 0.01)]
    out.append(f'<path d="{pd(win)}" fill="#FFC870"/>')
    out.append(f'<path d="{pd(win)}" fill="{D.lin([(0, "#FFE0A0", 0.6), (1, "#E8904A", 0.4)])}"/>')
    for j in range(7):
        t = j / 6
        a = (win[0][0] + (win[1][0] - win[0][0]) * t, win[0][1])
        b = (win[3][0] + (win[2][0] - win[3][0]) * t, win[3][1])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {a[0] + 3:.1f} {(a[1] + b[1]) / 2:.1f} {b[0]:.1f} {b[1]:.1f}" stroke="#FFF4E0" stroke-width="3" opacity="0.45"/>')
    out.append(soft_glow(D, (win[0][0] + win[2][0]) / 2, (win[0][1] + win[2][1]) / 2, 70, "#FFC060", 0.35))
    for (fx, fy, fw_, fh, col) in ((1.6, 2.1, 0.32, 0.4, "#C89A6A"), (2.05, 2.15, 0.26, 0.32, "#B87A5A"), (1.8, 1.6, 0.42, 0.3, "#D8B07A")):
        q = [C(fx, fy, WALL_Z - 0.01), C(fx + fw_, fy, WALL_Z - 0.01), C(fx + fw_, fy - fh, WALL_Z - 0.01), C(fx, fy - fh, WALL_Z - 0.01)]
        out.append(f'<path d="{pd(q)}" fill="{col}"/>')
        inner = [(q[0][0] + 3, q[0][1] + 3), (q[1][0] - 3, q[1][1] + 3), (q[2][0] - 3, q[2][1] - 3), (q[3][0] + 3, q[3][1] - 3)]
        out.append(f'<path d="{pd(inner)}" fill="{D.lin([(0, "#E8D8B8"), (1, "#8A7A6A")])}"/>')
        hc = ((inner[0][0] + inner[2][0]) / 2, (inner[0][1] + inner[2][1]) / 2)
        out.append(f'<path d="{blob(hc[0], hc[1] + 2, 5, 6, int(fx * 10), 0.1, 10)}" fill="#5A4A3A" opacity="0.7"/>')
    ck = C(1.1, 2.35, WALL_Z - 0.01)
    out.append(f'<circle cx="{ck[0]:.1f}" cy="{ck[1]:.1f}" r="11" fill="#F2EAD8" stroke="#3A2A1A" stroke-width="2"/><path d="M {ck[0]:.1f} {ck[1]:.1f} l 0 -7 M {ck[0]:.1f} {ck[1]:.1f} l 5 2" stroke="#3A2A1A" stroke-width="1.4"/>')
    # floor (polished concrete) catching the screen's glow
    floor_q = [C(-4, 0, WALL_Z), C(4, 0, WALL_Z), C(4, 0, -1.0), C(-4, 0, -1.0)]
    out.append(f'<path d="{pd(floor_q)}" fill="{D.lin([(0, "#3A3E52"), (1, "#16121E")])}"/>')
    fg = C(0, 0, WALL_Z - 0.6)
    out.append(f'<ellipse cx="{fg[0]:.1f}" cy="{fg[1] + 30:.1f}" rx="280" ry="90" fill="{D.rad([(0, "#9AD0FF", 0.6), (0.5, "#7AB8FF", 0.25), (1, "#7AB8FF", 0)])}"/>')
    out.append(clipped(D, pd(floor_q), brush_field(2302, (-20, floor_q[0][1], 620, 610), ["#4A5068", "#1A1626", "#6A7898"], 90, 0, (30, 110), (1.5, 4), (0.12, 0.3), 0.05, 3)))
    # cabinet, the tv screen showing a perfect score, speakers either side
    cab = [C(-0.85, 0.62, WALL_Z - 0.2), C(0.85, 0.62, WALL_Z - 0.2), C(0.85, 0.0, WALL_Z - 0.2), C(-0.85, 0.0, WALL_Z - 0.2)]
    cab_top = [C(-0.85, 0.62, WALL_Z - 0.2), C(0.85, 0.62, WALL_Z - 0.2), C(0.85, 0.62, WALL_Z), C(-0.85, 0.62, WALL_Z)]
    out.append(_paint_face(D, cab, "#5A321E", 2303, top="#7A4A2E", bottom="#24120A", angle=0, cols=["#8A5A36", "#3A1E10"]))
    out.append(f'<path d="{pd(cab_top)}" fill="#9A6A48"/>')
    for t in (0.33, 0.66):
        a, b = bil_pt(cab, t, 0.05), bil_pt(cab, t, 0.95)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#1E0E06" stroke-width="1.6" opacity="0.8"/>')
    for t in (0.28, 0.38, 0.62, 0.72):
        p = bil_pt(cab, t, 0.45)
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.2" fill="#E8C070"/>')
    bezel = [C(-0.78, 1.66, WALL_Z - 0.15), C(0.78, 1.66, WALL_Z - 0.15), C(0.78, 0.74, WALL_Z - 0.15), C(-0.78, 0.74, WALL_Z - 0.15)]
    out.append(f'<path d="{pd(bezel)}" fill="#14141C"/>')
    out.append(f'<path d="{pd([bezel[2], bezel[3], C(-0.1, 0.62, WALL_Z - 0.12), C(0.1, 0.62, WALL_Z - 0.12)])}" fill="#22222C"/>')
    scr = [bil_pt(bezel, 0.03, 0.04), bil_pt(bezel, 0.97, 0.04), bil_pt(bezel, 0.97, 0.94), bil_pt(bezel, 0.03, 0.94)]
    sd = pd(scr)
    rnd = random.Random(2304)
    sc = [f'<path d="{sd}" fill="{D.lin([(0, "#2E7AE0"), (0.55, "#5A4AC8"), (1, "#C84AA0")], 0, 0, 1, 1)}"/>',
          soft_glow(D, (scr[0][0] + scr[2][0]) / 2, (scr[0][1] + scr[2][1]) / 2, 90, "#FFFFFF", 0.35)]
    for _ in range(40):
        sx, sy = rnd.uniform(scr[0][0], scr[1][0]), rnd.uniform(scr[0][1], scr[2][1])
        sc.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{rnd.uniform(2, 5):.1f}" height="{rnd.uniform(1.5, 3):.1f}" fill="{rnd.choice(["#FFE04A", "#FF6AA8", "#6AE0FF", "#FFFFFF", "#8AF08A"])}" '
                  f'transform="rotate({rnd.uniform(0, 90):.0f} {sx:.1f} {sy:.1f})" opacity="0.9"/>')
    mcx = (scr[0][0] + scr[1][0]) / 2
    sh_ = scr[2][1] - scr[0][1]
    sc.append(f'<text x="{mcx + 2:.1f}" y="{scr[0][1] + sh_ * 0.68 + 2:.1f}" text-anchor="middle" {ANTON} font-size="{sh_ * 0.62:.1f}" fill="#1A0A3A" opacity="0.45">100</text>')
    sc.append(f'<text x="{mcx:.1f}" y="{scr[0][1] + sh_ * 0.68:.1f}" text-anchor="middle" {ANTON} font-size="{sh_ * 0.62:.1f}" fill="#FFE04A">100</text>')
    sc.append(f'<text x="{mcx:.1f}" y="{scr[0][1] + sh_ * 0.88:.1f}" text-anchor="middle" {JOS} font-size="{sh_ * 0.13:.1f}" letter-spacing="2" fill="#FFFFFF">PERFECT!</text>')
    out.append(clipped(D, sd, sc))
    out.append(taper([bil_pt(scr, 0.05, 0.08), bil_pt(scr, 0.45, 0.06)], 2.5, 0.5, "#FFFFFF", 0.4))
    for side in (-1, 1):
        x0 = 1.05 * side
        sp = [C(x0 - 0.22, 1.2, WALL_Z - 0.35), C(x0 + 0.22, 1.2, WALL_Z - 0.35), C(x0 + 0.22, 0, WALL_Z - 0.35), C(x0 - 0.22, 0, WALL_Z - 0.35)]
        sps = [C(x0 + 0.22 * side, 1.2, WALL_Z - 0.35), C(x0 + 0.22 * side, 1.2, WALL_Z - 0.05), C(x0 + 0.22 * side, 0, WALL_Z - 0.05), C(x0 + 0.22 * side, 0, WALL_Z - 0.35)]
        out.append(f'<path d="{pd(sps)}" fill="#0E0E14"/>')
        out.append(_paint_face(D, sp, "#24242E", 2305 + side, top="#3A3A4A", bottom="#0A0A10", angle=-90, cols=["#4A4A5A", "#101018"]))
        for (v, r) in ((0.25, 0.09), (0.62, 0.15)):
            c = bil_pt(sp, 0.5, v)
            rr = abs(bil_pt(sp, 0.5 + r, v)[0] - c[0])
            out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{rr:.1f}" fill="#0A0A10"/><circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{rr * 0.82:.1f}" fill="{D.rad([(0, "#5A5A6A"), (0.5, "#2A2A34"), (1, "#14141C")], 0.4, 0.35, 0.7)}"/>'
                       f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{rr * 0.28:.1f}" fill="#3A3A48"/>')
        out.append(taper([sp[0], sp[1]], 2, 2, "#9AB8FF" if side < 0 else "#FFD8A0", 0.6))
    # the carport ceiling: corrugated sheets on purlins, lit warm by the bulbs and cold by the screen
    ceil = [C(-4, 2.75, -1.0), C(4, 2.75, -1.0), C(4, 2.75, WALL_Z), C(-4, 2.75, WALL_Z)]
    out.append(f'<path d="{pd(ceil)}" fill="{D.lin([(0, "#1A1424"), (1, "#3A3446")], 0, 0, 0, 1)}"/>')
    cg = []
    for j in range(40):
        xx = -4 + j * 0.2
        a, b = C(xx, 2.75, -1.0), C(xx, 2.75, WALL_Z)
        cg.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{"#4A4256" if j % 2 else "#120E1A"}" stroke-width="{2.2 if j % 2 else 1.2}" opacity="0.7"/>')
    for zz in (0.4, 1.6, 2.9):
        a, b = C(-4, 2.7, zz), C(4, 2.7, zz)
        cg.append(taper([a, b], 700 / max(1, C.depth(0, 2.7, zz)) * 0.08, 700 / max(1, C.depth(0, 2.7, zz)) * 0.08, "#2A1E1A"))
    out.append(clipped(D, pd(ceil), cg))
    out.append(f'<path d="{pd(ceil)}" fill="{D.lin([(0, "#0A0610", 0.6), (0.7, "#0A0610", 0.1), (1, "#7AB8FF", 0.12)], 0, 0, 0, 1)}"/>')
    lights = [f'<rect x="-10" y="180" width="620" height="120" fill="{D.lin([(0, "#FFC070", 0.22), (1, "#FFC070", 0)])}"/>']
    for seg, (x0, y0, x1, y1, sag) in enumerate(((-10, 188, 210, 200, 34), (210, 200, 420, 192, 30), (420, 192, 610, 182, 30))):
        ps = [(x0 + (x1 - x0) * t / 16, y0 + (y1 - y0) * t / 16 + sag * 4 * (t / 16) * (1 - t / 16)) for t in range(17)]
        lights.append(f'<path d="{smooth_open(ps)}" fill="none" stroke="#0A0812" stroke-width="1.6"/>')
        for i in range(1, 16, 2):
            x, y = ps[i]
            c = ["#FF6A5A", "#FFD84A", "#6AE08A", "#6AB8FF", "#FF8AD8"][(i // 2 + seg) % 5]
            lights.append(soft_glow(D, x, y + 7, 22, c, 0.55))
            lights.append(f'<ellipse cx="{x:.1f}" cy="{y + 7:.1f}" rx="3.6" ry="5.4" fill="{c}"/><ellipse cx="{x - 1:.1f}" cy="{y + 5:.1f}" rx="1.3" ry="2" fill="#FFFFFF" opacity="0.8"/>')
    # chairs: three facing the screen, one turned toward us with the mic left on its seat
    def chair_light(nrm, kind):
        nx, ny, nz = nrm
        L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1
        nx, ny, nz = nx / L, ny / L, nz / L
        screen = max(0, nz) * 0.9           # faces toward the wall/screen get its cold light
        top = max(0, ny) * 0.6              # tops catch the warm bulbs
        base = "#7884A6"
        c = mix(base, "#E4F0FF", min(1, screen))
        c = mix(c, "#FFE2B8", min(0.7, top))
        if kind == "leg":
            c = mix(c, "#1A1A28", 0.25)
        return c
    out.append(monobloc(C, -1.2, 2.4, 10, 2310, chair_light))
    out.append(monobloc(C, 0.3, 2.9, -5, 2311, chair_light))
    out.append(monobloc(C, 1.5, 2.2, -25, 2312, chair_light))
    out.append(monobloc(C, 1.25, 1.35, 215, 2313, chair_light, mic=True))
    # mic cable snaking across the floor to the machine
    cab_p = [C(0.2, 0.0, WALL_Z - 0.25), C(0.0, 0, 3.0), C(0.9, 0, 2.2), C(1.0, 0, 1.6), C(1.27, 0.46, 1.36)]
    out.append(f'<path d="{smooth_open(cab_p)}" fill="none" stroke="#0A0A10" stroke-width="2.4"/>')
    out.append("".join(lights))
    # foreground: the corner of the food table (pancit tray, lumpia, juice) cut by the frame
    tbl = [(-10, 520), (180, 500), (210, 610), (-10, 610)]
    out.append(f'<path d="{pd(tbl)}" fill="#E8E0F0"/>')
    out.append(f'<path d="{pd(tbl)}" fill="{D.lin([(0, "#9AB0E0", 0.5), (1, "#3A3050", 0.55)], 0, 0, 1, 1)}"/>')
    for j in range(5):
        y = 520 + j * 18
        out.append(f'<path d="M -10 {y + 6} L 190 {y - 14 + j * 4}" stroke="#C8304A" stroke-width="3" opacity="0.35"/>')
    out.append(f'<ellipse cx="78" cy="548" rx="62" ry="20" fill="#C8B8A0"/><ellipse cx="78" cy="545" rx="54" ry="15" fill="#D8A84A"/>')
    nd = []
    for _ in range(70):
        x, y = rnd.uniform(30, 126), rnd.uniform(534, 556)
        nd.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-8, 8):.1f} {rnd.uniform(-4, 4):.1f} {rnd.uniform(-14, 14):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#F2D488", "#C8923A", "#FBE8B0"])}" stroke-width="1.6" fill="none"/>')
    out.append(clipped(D, ellipse_d(78, 545, 54, 15), nd + [f'<circle cx="{rnd.uniform(40, 120):.1f}" cy="{rnd.uniform(538, 552):.1f}" r="2.4" fill="{rnd.choice(["#3E9A3A", "#F2802A", "#E8502A"])}"/>' for _ in range(16)]))
    out.append(f'<path d="{pd([(150, 470), (186, 470), (182, 528), (154, 528)])}" fill="#E8902A" opacity="0.85"/>'
               f'<path d="{pd([(150, 470), (186, 470), (185, 482), (151, 482)])}" fill="#FFFFFF" opacity="0.35"/>'
               f'<ellipse cx="168" cy="470" rx="18" ry="5" fill="#F2F0F8" opacity="0.7"/>')
    out.append(letters(D, 300, 116, "Isa pang kanta!", SERIF_IT, 96, "#FFE6F2", ["#FFFFFF", "#FFC8E0", "#FFE0F0"], 2330, max_w=470,
                       shadow="#120A2A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 156, "FAMILY KARAOKE NIGHT", "#FFD84A", font=JOS, size=19, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 2331, "#0A0A1A", 0.6)


def bil_pt(q, u, v):
    a = (q[0][0] + (q[1][0] - q[0][0]) * u, q[0][1] + (q[1][1] - q[0][1]) * u)
    b = (q[3][0] + (q[2][0] - q[3][0]) * u, q[3][1] + (q[2][1] - q[3][1]) * u)
    return (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)


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


def plane_pt(C, o, U, V, u, v):
    return C(o[0] + U[0] * u + V[0] * v, o[1] + U[1] * u + V[1] * v, o[2] + U[2] * u + V[2] * v)


def plane_quad(C, o, U, V, u0=0.0, u1=1.0, v0=0.0, v1=1.0):
    return [plane_pt(C, o, U, V, u0, v0), plane_pt(C, o, U, V, u1, v0), plane_pt(C, o, U, V, u1, v1), plane_pt(C, o, U, V, u0, v1)]


def plane_matrix(C, o, U, V, su, sv):
    """Affine SVG matrix mapping local (x in 0..su, y in 0..sv, y down from the top edge) onto the plane quad."""
    p0 = plane_pt(C, o, U, V, 0, 0)
    pu = plane_pt(C, o, U, V, 1, 0)
    pv = plane_pt(C, o, U, V, 0, 1)
    return (f"matrix({(pu[0] - p0[0]) / su:.5f} {(pu[1] - p0[1]) / su:.5f} {(pv[0] - p0[0]) / sv:.5f} {(pv[1] - p0[1]) / sv:.5f} "
            f"{p0[0]:.2f} {p0[1]:.2f})")


def bamboo_pole(a, b, w, seed, pal=("#F2DC9A", "#C8A85A", "#7A5A26"), lit_side=1, nodes=4):
    """A bamboo pole between two screen points: tapered tube, lit stripe, nodes."""
    out = [taper([a, b], w, w * 0.9, pal[1])]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w * 0.25 * lit_side, dx / L * w * 0.25 * lit_side
    out.append(taper([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)], w * 0.35, w * 0.3, pal[0], 0.8))
    out.append(taper([(a[0] - nx * 1.4, a[1] - ny * 1.4), (b[0] - nx * 1.4, b[1] - ny * 1.4)], w * 0.25, w * 0.2, pal[2], 0.6))
    for k in range(1, nodes + 1):
        t = k / (nodes + 1)
        x, y = a[0] + dx * t, a[1] + dy * t
        out.append(f'<path d="M {x - dy / L * w * 0.55:.1f} {y + dx / L * w * 0.55:.1f} L {x + dy / L * w * 0.55:.1f} {y - dx / L * w * 0.55:.1f}" stroke="{pal[2]}" stroke-width="{max(1, w * 0.18):.1f}" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


def paddies(D, C, seed, x0, x1, z0, z1, sky_stops, hz, cell=(7.0, 5.0), skip=None):
    """Rice paddies on the ground plane (world-aligned grid, so it recedes in perspective): flooded ones mirror the
    sky with seedlings in rows, others are green with young rice; raised earthen dikes (pilapil) between them."""
    rnd = random.Random(seed)
    out = []
    xs = [x0]
    while xs[-1] < x1:
        xs.append(xs[-1] + cell[0] * rnd.uniform(0.7, 1.3))
    zs = [z0]
    while zs[-1] < z1:
        zs.append(zs[-1] + cell[1] * rnd.uniform(0.7, 1.3))
    cells = []
    for j in range(len(zs) - 1):
        for i in range(len(xs) - 1):
            cx_, cz_ = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            if skip and skip(cx_, cz_):
                continue
            cells.append((C.depth(cx_, 0, cz_), i, j))
    for dep, i, j in sorted(cells, reverse=True):
        if min(C.depth(xx, 0, zz) for xx in (xs[i], xs[i + 1]) for zz in (zs[j], zs[j + 1])) < 1.2:
            continue
        q = [C(xs[i], 0, zs[j]), C(xs[i + 1], 0, zs[j]), C(xs[i + 1], 0, zs[j + 1]), C(xs[i], 0, zs[j + 1])]
        if max(p[0] for p in q) < -20 or min(p[0] for p in q) > 620 or min(p[1] for p in q) > 620:
            continue
        d = pd(q)
        flooded = rnd.random() < 0.6 or dep < 26
        ys = [p[1] for p in q]
        sd = []
        px = 700 / dep          # pixels per metre at this distance
        if flooded:
            t0 = max(0.0, (2 * hz - max(ys)) / 600)
            t1 = max(0.0, (2 * hz - min(ys)) / 600)
            g = D.lin([(0, color_at(sky_stops, t1)), (1, color_at(sky_stops, t0))], 0, 0, 0, 1)
            out.append(f'<path d="{d}" fill="{g}"/>')
            out.append(f'<path d="{d}" fill="#2A5A6A" opacity="{0.1 + min(0.25, 6 / dep):.2f}"/>')
            cols_ = ["#4E8A2E", "#7AB04A", "#3A6A22", "#9AC85A"]
            paths = {c: [] for c in cols_}
            refl = []
            dens = 1.8 if dep < 22 else (1.1 if dep < 36 else 0.5)
            nr = max(1, int((zs[j + 1] - zs[j]) * dens))
            nc = max(1, int((xs[i + 1] - xs[i]) * dens))
            hh0 = 700 / dep * 0.24
            for r_ in range(nr):
                zz = zs[j] + (zs[j + 1] - zs[j]) * (r_ + 0.5) / nr
                for c_ in range(nc):
                    xx = xs[i] + (xs[i + 1] - xs[i]) * (c_ + 0.5) / nc + rnd.uniform(-0.06, 0.06)
                    dd = C.depth(xx, 0, zz)
                    if dd < 1:
                        continue
                    p = C(xx, 0, zz)
                    hh = 700 / dd * rnd.uniform(0.18, 0.3)
                    if hh < 1.2 or not (-15 < p[0] < 615 and p[1] < 615):
                        continue
                    nb = 1 if hh < 5 else 4
                    for b_ in range(nb):
                        a_ = math.radians(-90 + (rnd.uniform(-35, 35) if nb > 1 else rnd.uniform(-12, 12)))
                        L_ = hh * rnd.uniform(0.6, 1.1)
                        ex, ey = math.cos(a_) * L_, math.sin(a_) * L_
                        paths[rnd.choice(cols_)].append(f"M{p[0]:.1f} {p[1]:.1f}q{ex * 0.4:.1f} {ey * 0.55:.1f} {ex:.1f} {ey:.1f}")
                    refl.append(f"M{p[0]:.1f} {p[1] + 0.5:.1f}l0 {hh * 0.45:.1f}")
            sw_ = max(0.8, hh0 * 0.14)
            for c in cols_:
                if paths[c]:
                    sd.append(f'<path d="{"".join(paths[c])}" fill="none" stroke="{c}" stroke-width="{sw_:.1f}" stroke-linecap="round"/>')
            if refl:
                sd.append(f'<path d="{"".join(refl)}" fill="none" stroke="#2A4A3A" stroke-width="{sw_ * 0.8:.1f}" opacity="0.22"/>')
            out.append(clipped(D, d, sd))
            out.append(clipped(D, d, brush_field(seed + i * 31 + j, (min(p[0] for p in q) - 30, min(ys), max(p[0] for p in q), max(ys)),
                                                 ["#FFFFFF", "#FFE8C0", "#5A7A6A"], 6, 0, (20, 70), (0.6, 1.4), (0.2, 0.45))))
        else:
            base = rnd.choice(["#7AA83A", "#8AB84A", "#6A9A32", "#94B848"])
            out.append(f'<path d="{d}" fill="{base}"/>')
            out.append(f'<path d="{d}" fill="{D.lin([(0, "#F2E08A", 0.4), (1, "#2A4A1A", 0.3)], 0, 0, 1, 0)}"/>')
            sd = []
            nr = int((zs[j + 1] - zs[j]) * 2.5)
            for r_ in range(nr):
                zz = zs[j] + (zs[j + 1] - zs[j]) * (r_ + 0.5) / nr
                a, b = C(xs[i], 0, zz), C(xs[i + 1], 0, zz)
                dd = max(0.5, C.depth((xs[i] + xs[i + 1]) / 2, 0, zz))
                sd.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{rnd.choice(["#4E7A22", "#B8D070", "#5A8A2A"])}" stroke-width="{max(0.8, 700 / dd * 0.12):.1f}" stroke-dasharray="{max(1, 700 / dd * 0.08):.1f} {max(1, 700 / dd * 0.06):.1f}" opacity="0.75"/>')
            out.append(clipped(D, d, sd))
        # dikes on the near (low z) edge and the left (low x) edge
        for (a3, b3) in (((xs[i], zs[j]), (xs[i + 1], zs[j])), ((xs[i], zs[j]), (xs[i], zs[j + 1]))):
            tw = 0.22
            if a3[1] == b3[1]:
                poly = [C(a3[0], 0.16, a3[1] - tw), C(b3[0], 0.16, b3[1] - tw), C(b3[0], 0.16, b3[1] + tw), C(a3[0], 0.16, a3[1] + tw)]
                face = [C(a3[0], 0.16, a3[1] - tw), C(b3[0], 0.16, b3[1] - tw), C(b3[0], 0, b3[1] - tw - 0.2), C(a3[0], 0, a3[1] - tw - 0.2)]
            else:
                poly = [C(a3[0] - tw, 0.16, a3[1]), C(b3[0] - tw, 0.16, b3[1]), C(b3[0] + tw, 0.16, b3[1]), C(a3[0] + tw, 0.16, a3[1])]
                face = [C(a3[0] + tw, 0.16, a3[1]), C(b3[0] + tw, 0.16, b3[1]), C(b3[0] + tw + 0.2, 0, b3[1]), C(a3[0] + tw + 0.2, 0, a3[1])]
            out.append(f'<path d="{pd(face)}" fill="#6A6A3A"/><path d="{pd(poly)}" fill="#9A9A5A"/>')
            mid = C((a3[0] + b3[0]) / 2, 0.16, (a3[1] + b3[1]) / 2)
            dd = max(0.5, C.depth((a3[0] + b3[0]) / 2, 0, (a3[1] + b3[1]) / 2))
            gr = []
            for _ in range(min(60, int(abs(poly[1][0] - poly[0][0]) + abs(poly[1][1] - poly[0][1])) // 5 + 2)):
                t = rnd.random()
                pp = (poly[0][0] + (poly[1][0] - poly[0][0]) * t, poly[0][1] + (poly[1][1] - poly[0][1]) * t)
                gh = 700 / dd * rnd.uniform(0.1, 0.25)
                gr.append(f'<path d="M {pp[0]:.1f} {pp[1] + 1:.1f} l {rnd.uniform(-0.4, 0.4) * gh:.1f} {-gh:.1f}" stroke="{rnd.choice(["#6A8A3A", "#A8B860", "#4E6A2A"])}" stroke-width="{max(0.8, gh * 0.18):.1f}" stroke-linecap="round"/>')
            if dep < 40:
                out.append("".join(gr))
    return "".join(out)


def far_palm(x, base, h, col, seed, lean=0.0):
    """A distant coconut palm: a thin curved trunk and a crown of drooping fronds, few nodes."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    out = [taper([(x, base), (x + lean * h * 0.3, base - h * 0.5), (tx, ty)], max(1.2, h * 0.05), max(0.8, h * 0.03), col)]
    for k in range(8):
        a = math.radians(-180 + k * 26 + rnd.uniform(-8, 8))
        L = h * rnd.uniform(0.32, 0.45)
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.5 + L * 0.35
        mx, my = tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.5 - L * 0.08
        out.append(taper([(tx, ty), (mx, my), (ex, ey)], max(1.4, h * 0.07), 0.5, col))
    return "".join(out)


def banana_leaf_lite(D, bx, by, ang, L, W, seed, pal=SAGING):
    """Banana leaf, light on nodes: a painted blade, side veins in one stroke path, a pale midrib, a few wind tears."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    right, left, spine = [], [], []
    for i in range(15):
        t = i / 14
        bend = 0.14 * L * t * t
        px, py = bx + ux * L * t + nx * bend * (1 if ang < -90 else -1), by + uy * L * t + bend * 0.6
        w = W * math.sin(math.pi * min(1, t * 1.05)) ** 0.7 * (1 - 0.25 * t)
        spine.append((px, py))
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.12, angle=ang + 70, n=int(L * W / 260) + 8, slen=(W * 0.3, W * 0.9), sw=(1.2, 3), inkw=1.2, inkop=0.5, hi=0.3, hik=0.06)]
    v = []
    for i in range(2, 13):
        for edge in (right, left):
            sx, sy = spine[i]
            ex, ey = edge[min(14, i + 1)]
            v.append(f"M{sx:.1f} {sy:.1f}L{ex:.1f} {ey:.1f}")
    out.append(f'<path d="{"".join(v)}" stroke="{pal[2]}" stroke-width="0.9" opacity="0.35" fill="none"/>')
    for k in range(3):
        i = rnd.randint(4, 11)
        side = rnd.choice((right, left))
        sx, sy = spine[i]
        ex, ey = side[i + 1]
        out.append(f'<path d="M{sx + (ex - sx) * 0.3:.1f} {sy + (ey - sy) * 0.3:.1f}L{ex + (ex - sx) * 0.1:.1f} {ey + (ey - sy) * 0.1:.1f}" stroke="{pal[2]}" stroke-width="1.6" opacity="0.6"/>')
    out.append(taper(spine, max(2, W * 0.16), 1, pal[0], 0.85))
    return "".join(out)


def banana_plant(D, base, h, seed, lit=-1):
    """A banana plant: a few pale pseudostems and big arching, wind-torn leaves, lit from one side."""
    rnd = random.Random(seed)
    x, y = base
    out = []
    pals = [("#B8E080", "#5AA03A", "#1E5A22"), ("#A8D870", "#4E9232", "#1A4E1E"), ("#C8E890", "#6AAE44", "#2A6A2A")]
    for k in range(3):
        sx = x + (k - 1) * h * 0.06
        top = (sx + rnd.uniform(-6, 6), y - h * rnd.uniform(0.45, 0.62))
        out.append(taper([(sx, y), ((sx + top[0]) / 2, (y + top[1]) / 2), top], h * 0.09, h * 0.05, "#8AA858"))
        out.append(taper([(sx + lit * h * 0.02, y), (top[0] + lit * h * 0.015, top[1])], h * 0.03, h * 0.015, "#D8E8A0", 0.7))
    crown = (x, y - h * 0.58)
    angs = [-160, -130, -100, -75, -45, -20, -115, -60]
    for k, a in enumerate(angs):
        L = h * rnd.uniform(0.45, 0.62)
        pal = rnd.choice(pals)
        if (math.cos(math.radians(a)) > 0) == (lit > 0):
            pal = pals[2]
        out.append(banana_leaf_lite(D, crown[0] + rnd.uniform(-6, 6), crown[1] + rnd.uniform(-8, 8), a + rnd.uniform(-8, 8), L, L * 0.2, seed + k, pal=pal))
    return "".join(out)


def kubo34(D, C, seed):
    """Bahay kubo in 3/4, lit by a low sun from the left. World: floor 3.2 m (X) by 2.6 m (Z), front (door) at Z = -1.3."""
    rnd = random.Random(seed)
    out = []
    W, Dp = 1.6, 1.3
    fl, wt = 1.25, 3.05          # floor level, wall top
    ridge_y, ridge_half = 5.2, 0.7
    # cast shadow to the right/back on the ground (sun low on the left)
    sh = [C(-W, 0, -Dp), C(W + 3.4, 0, -Dp + 0.8), C(W + 3.6, 0, Dp + 1.4), C(-W, 0, Dp)]
    out.append(f'<path d="{smooth_closed(sh)}" fill="#1E2A2A" opacity="0.32"/>')
    # dark space under the floor
    out.append(f'<path d="{pd([C(-W, 0.02, -Dp), C(W, 0.02, -Dp), C(W, 0.02, Dp), C(W, fl - 0.1, Dp), C(-W, fl - 0.1, Dp)])}" fill="#2A2A22"/>')
    out.append(f'<path d="{pd([C(-W, 0.02, Dp), C(W, 0.02, Dp), C(W, fl - 0.1, Dp), C(-W, fl - 0.1, Dp)])}" fill="#3E4A2E"/>')
    # a clay banga and a woven basket in the shade underneath
    bp = C(-0.2, 0, 0.3)
    s = abs(C(-0.2, 0.5, 0.3)[1] - bp[1])
    out.append(f'<path d="{blob(bp[0], bp[1] - s * 0.45, s * 0.5, s * 0.46, seed, 0.04, 14)}" fill="#7A3A1E"/>'
               f'<path d="{blob(bp[0] - s * 0.15, bp[1] - s * 0.55, s * 0.15, s * 0.2, seed + 1, 0.1, 8)}" fill="#C87A4A" opacity="0.6"/>'
               f'<path d="{pd([(bp[0] - s * 0.22, bp[1] - s * 0.9), (bp[0] + s * 0.22, bp[1] - s * 0.9), (bp[0] + s * 0.18, bp[1] - s * 0.82), (bp[0] - s * 0.18, bp[1] - s * 0.82)])}" fill="#5A2410"/>')
    # posts (haligi): thick hardwood at the corners and middle, bamboo braces
    for (x, z) in ((W, Dp), (-W, -Dp), (0, -Dp), (W, -Dp), (W, 0)):
        a, b = C(x, 0, z), C(x, fl, z)
        w_ = abs(C(x + 0.13, 0, z)[0] - a[0]) * 1.6 + 3
        far = z > 0 and x > 0
        pal = ("#B87A4A", "#7A4626", "#3A1E10")
        out.append(taper([a, b], w_, w_ * 0.92, pal[2] if far else pal[1]))
        if not far:
            out.append(taper([(a[0] - w_ * 0.22, a[1]), (b[0] - w_ * 0.22, b[1])], w_ * 0.4, w_ * 0.36, "#E8A86A", 0.85))
            out.append(taper([(a[0] + w_ * 0.3, a[1]), (b[0] + w_ * 0.3, b[1])], w_ * 0.25, w_ * 0.22, "#2A140A", 0.6))
            out.append(dry_brush(seed + int(x * 10 + z), [(a[0] - w_ * 0.25, a[1] - 4), (b[0] - w_ * 0.25, b[1] + 4)], w_ * 0.3, "#FFD8A0", 0.6, 3))
    out.append(bamboo_pole(C(-W, 0.15, -Dp), C(0, fl - 0.15, -Dp), 4, seed, nodes=2))
    out.append(bamboo_pole(C(W, 0.15, -Dp), C(W, fl - 0.15, 0), 4, seed + 1, lit_side=-1, nodes=2))
    # floor beam (sahig edge): front lit, right side shaded
    fb_front = [C(-W - 0.1, fl - 0.12, -Dp - 0.08), C(W + 0.1, fl - 0.12, -Dp - 0.08), C(W + 0.1, fl + 0.06, -Dp - 0.08), C(-W - 0.1, fl + 0.06, -Dp - 0.08)]
    fb_side = [C(W + 0.1, fl - 0.12, -Dp - 0.08), C(W + 0.1, fl - 0.12, Dp + 0.08), C(W + 0.1, fl + 0.06, Dp + 0.08), C(W + 0.1, fl + 0.06, -Dp - 0.08)]
    out.append(f'<path d="{pd(fb_front)}" fill="#C8904E"/><path d="{pd(fb_side)}" fill="#6A4A2A"/>')
    out.append(dry_brush(seed + 3, [fb_front[3], fb_front[2]], 2, "#FFE0A8", 0.8, 2))
    # walls: sawali woven panels mapped onto each face, framed by bamboo
    faces = [
        ("front", (-W, wt, -Dp), (2 * W, 0, 0), (0, -(wt - fl - 0.06), 0), 1.0),
        ("side", (W, wt, -Dp), (0, 0, 2 * Dp), (0, -(wt - fl - 0.06), 0), -0.6),
    ]
    for name, o, U, V, lit in faces:
        q = plane_quad(C, o, U, V)
        d = pd(q)
        su, sv = (320, 175) if name == "front" else (260, 175)
        pal = ("#FFE6A8", "#E2BE78", "#9A7A3E") if lit > 0 else ("#B8A07A", "#8A7450", "#4A3A26")
        pat = D.pattern(14, 14, f'<rect width="14" height="14" fill="{pal[1]}"/>'
                        f'<rect x="0.5" y="0.5" width="13" height="3" rx="1" fill="{pal[0]}"/>'
                        f'<rect x="0.5" y="7.5" width="3" height="6" rx="1" fill="{pal[0]}"/>'
                        f'<rect x="7.5" y="4" width="6" height="3" rx="1" fill="{mix(pal[0], "#FFFFFF", 0.15)}"/>'
                        f'<path d="M 0 7 L 14 7 M 7 0 L 7 14" stroke="{pal[2]}" stroke-width="0.7" opacity="0.6"/>', transform="rotate(45)")
        m = plane_matrix(C, o, U, V, su, sv)
        out.append(f'<g transform="{m}"><rect x="0" y="0" width="{su}" height="{sv}" fill="{pat}"/></g>')
        if lit > 0:
            out.append(f'<path d="{d}" fill="{D.lin([(0, "#FFF0C0", 0.3), (0.6, "#FFF0C0", 0), (1, "#5A3A1A", 0.2)], 0, 0, 0, 1)}"/>')
        else:
            out.append(f'<path d="{d}" fill="{D.lin([(0, "#2A2A40", 0.35), (1, "#2A2A40", 0.15)], 0, 0, 1, 0)}"/>')
        out.append(clipped(D, d, brush_field(seed + len(name), (min(p[0] for p in q) - 10, min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q)),
                                             [pal[0], pal[2]], 40, -90, (8, 26), (1, 2.5), (0.12, 0.3))))
    # front: doorway (warm dark interior, a lamp inside), window on the side with a propped awning
    door = plane_quad(C, (-W, wt, -Dp), (2 * W, 0, 0), (0, -(wt - fl - 0.06), 0), 0.14, 0.42, 0.12, 1.0)
    out.append(f'<path d="{pd(door)}" fill="#2A1A12"/>')
    dc = ((door[0][0] + door[2][0]) / 2, (door[0][1] + door[2][1]) / 2)
    out.append(clipped(D, pd(door), [soft_glow(D, dc[0] + 4, dc[1] + 6, 40, "#FFB860", 0.55),
                                     f'<path d="{pd([door[0], door[1], (door[1][0], door[1][1] + 10), (door[0][0], door[0][1] + 12)])}" fill="#120A08" opacity="0.6"/>']))
    for k in (0, 1):
        out.append(bamboo_pole(door[k], door[3 - k], 4, seed + 10 + k, nodes=0))
    win = plane_quad(C, (W, wt, -Dp), (0, 0, 2 * Dp), (0, -(wt - fl - 0.06), 0), 0.3, 0.75, 0.2, 0.62)
    out.append(f'<path d="{pd(win)}" fill="#24180E"/>')
    out.append(clipped(D, pd(win), [soft_glow(D, (win[0][0] + win[2][0]) / 2, (win[0][1] + win[2][1]) / 2 + 6, 30, "#FFB050", 0.5)]))
    aw = [win[0], win[1], C(W + 0.75, wt - 0.05, -Dp + 2 * Dp * 0.75), C(W + 0.75, wt - 0.05, -Dp + 2 * Dp * 0.3)]
    out.append(f'<path d="{pd(aw)}" fill="#A88A58"/>')
    out.append(f'<path d="{pd(aw)}" fill="{D.lin([(0, "#E8C890", 0.6), (1, "#5A4428", 0.3)], 0, 1, 0, 0)}"/>')
    out.append(clipped(D, pd(aw), [f'<path d="M {aw[0][0] + (aw[1][0] - aw[0][0]) * t:.1f} {aw[0][1] + (aw[1][1] - aw[0][1]) * t:.1f} L {aw[3][0] + (aw[2][0] - aw[3][0]) * t:.1f} {aw[3][1] + (aw[2][1] - aw[3][1]) * t:.1f}" stroke="#6A5230" stroke-width="1" opacity="0.6"/>' for t in [i / 12 for i in range(1, 12)]]))
    out.append(bamboo_pole(C(W, fl + 0.3, -Dp + 2 * Dp * 0.55), C(W + 0.72, wt - 0.08, -Dp + 2 * Dp * 0.55), 2.6, seed + 12, nodes=1))
    # bamboo frame on the wall corners and the wall plate
    for (a3, b3, lit) in (((-W, fl, -Dp), (-W, wt, -Dp), 1), ((W, fl, -Dp), (W, wt, -Dp), 1), ((W, fl, Dp), (W, wt, Dp), -1)):
        out.append(bamboo_pole(C(*a3), C(*b3), 5, seed + 20, lit_side=lit, nodes=2))
    out.append(bamboo_pole(C(-W - 0.1, wt, -Dp - 0.02), C(W + 0.1, wt, -Dp - 0.02), 5, seed + 21, nodes=3))
    out.append(bamboo_pole(C(W + 0.02, wt, -Dp), C(W + 0.02, wt, Dp), 5, seed + 22, lit_side=-1, nodes=3))
    # nipa roof: hip end over the front (lit) and the long plane over the side (shade)
    ov = 0.75
    eL, eR = -W - ov, W + ov
    eF, eB = -Dp - ov, Dp + ov
    ey = wt - 0.25
    # long right-side roof plane: ridge point B, eave corners (eR,eF) & (eR,eB)
    out.append(_thatch_tri(D, C, (ridge_half, ridge_y, 0), (eR, ey, eF), (eR, ey, eB), seed + 30, ("#B89A68", "#86683E", "#4A3622"), lit=-0.5))
    # front plane (trapezoid): ridge A..B along the top, eave front edge (eL..eR at Z = eF)
    out.append(_thatch_trap(D, C, (-ridge_half, ridge_y, 0), (ridge_half, ridge_y, 0), (eR, ey, eF), (eL, ey, eF), seed + 31, ("#FFE29A", "#E0B464", "#8A6430"), lit=0.9))
    # ridge cap
    out.append(taper([C(-ridge_half - 0.1, ridge_y + 0.05, 0), C(ridge_half + 0.1, ridge_y + 0.05, 0)], 7, 7, "#6A4A26"))
    out.append(taper([C(-ridge_half - 0.1, ridge_y + 0.1, 0), C(ridge_half + 0.1, ridge_y + 0.1, 0)], 2.5, 2.5, "#E8C080", 0.8))
    # bamboo ladder from the doorway down to the ground, lit from the left
    l0, l1 = C(-W + 2 * W * 0.16, fl, -Dp - 0.05), C(-W + 2 * W * 0.40, fl, -Dp - 0.05)
    g0, g1 = C(-W + 2 * W * 0.1, 0, -Dp - 1.0), C(-W + 2 * W * 0.40, 0, -Dp - 1.0)
    for k in range(4):
        t = (k + 1) / 5
        a = (l0[0] + (g0[0] - l0[0]) * t, l0[1] + (g0[1] - l0[1]) * t)
        b = (l1[0] + (g1[0] - l1[0]) * t, l1[1] + (g1[1] - l1[1]) * t)
        out.append(bamboo_pole(a, b, 3.6, seed + 40 + k, nodes=0))
    out.append(bamboo_pole(l0, g0, 4.5, seed + 44, nodes=2))
    out.append(bamboo_pole(l1, g1, 4.5, seed + 45, nodes=2))
    # Tatay's salakot hung on the front post, his tsinelas at the foot of the ladder
    hp = C(W, fl + 0.55, -Dp - 0.05)
    out.append(salakot(D, hp[0] - 2, hp[1] + 4, 22, seed + 50, ang=-8))
    for k, dx in enumerate((-0.05, 0.22)):
        p = C(-W + 2 * W * 0.25 + dx, 0, -Dp - 1.25)
        out.append(f'<path d="{blob(p[0], p[1], 6.5, 2.4, seed + 60 + k, 0.08, 10, -8)}" fill="#3A5AA8"/><path d="{blob(p[0] - 1, p[1] - 0.6, 5, 1.4, seed + 62 + k, 0.08, 10, -8)}" fill="#8AA8E8" opacity="0.6"/>')
    return "".join(out)


def _thatch_tri(D, C, apex, a, b, seed, pal, lit):
    """Triangular roof plane: apex at the ridge end, a..b along the eave."""
    q = [C(*apex), C(*a), C(*b)]
    return _thatch_generic(D, C, q, lambda u, v: tuple(apex[i] + (a[i] + (b[i] - a[i]) * u - apex[i]) * v for i in range(3)), seed, pal, lit)


def _thatch_trap(D, C, r0, r1, e1, e0, seed, pal, lit):
    """Trapezoid roof plane: ridge r0..r1 on top, eave e0..e1 below (r0 above e0)."""
    q = [C(*r0), C(*r1), C(*e1), C(*e0)]

    def P(u, v):
        top = tuple(r0[i] + (r1[i] - r0[i]) * u for i in range(3))
        bot = tuple(e0[i] + (e1[i] - e0[i]) * u for i in range(3))
        return tuple(top[i] + (bot[i] - top[i]) * v for i in range(3))
    return _thatch_generic(D, C, q, P, seed, pal, lit)


def _thatch_generic(D, C, q, P, seed, pal, lit, courses=10):
    d = pd(q)
    light, base, dark = pal
    rnd = random.Random(seed)
    S = lambda u, v: C(*P(u, v))
    out = [f'<path d="{d}" fill="{base}"/>']
    inner = []
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    n = int((max(xs) - min(xs)) * (max(ys) - min(ys)) / 18) + 60
    for _ in range(n):
        u, v = rnd.uniform(-0.02, 1.02), rnd.uniform(0, 1.0)
        L = rnd.uniform(0.05, 0.13)
        a, b = S(u, v), S(u + rnd.uniform(-0.008, 0.008), min(1.03, v + L))
        col = rnd.choice([light, base, dark, mix(light, "#FFFFFF", 0.35)] if lit > 0 else [base, dark, light, mix(dark, "#20182A", 0.4)])
        inner.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{rnd.uniform(0.8, 2.2):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.3, 0.75):.2f}"/>')
    for k in range(1, courses + 1):
        v = k / (courses + 0.3)
        lo = [S(i / 30, v + rnd.uniform(-0.01, 0.01)) for i in range(31)]
        hi = [S(i / 30, v - 0.03) for i in range(31)]
        inner.append(f'<path d="{pd(hi + lo[::-1])}" fill="{dark}" opacity="{0.3 if lit > 0 else 0.42}"/>')
        inner.append(f'<path d="{smooth_open(lo)}" fill="none" stroke="{mix(light, "#FFFFFF", 0.3) if lit > 0 else light}" stroke-width="1.1" opacity="{0.55 if lit > 0 else 0.3}"/>')
    if lit > 0:
        inner.append(f'<path d="{d}" fill="{D.lin([(0, "#FFF0C0", 0.3), (1, "#FFF0C0", 0)], 0, 0, 0, 1)}"/>')
    else:
        inner.append(f'<path d="{d}" fill="{D.lin([(0, "#3A3050", 0.25), (1, "#3A3050", 0.45)], 0, 0, 0, 1)}"/>')
    out.append(clipped(D, d, inner))
    fr = []
    for i in range(70):
        a = S(i / 69, 1.0)
        L = rnd.uniform(4, 11)
        fr.append(f'<path d="M {a[0]:.1f} {a[1] - 3:.1f} l {rnd.uniform(-1.5, 1.5):.1f} {L:.1f}" stroke="{rnd.choice([base, dark, light])}" stroke-width="{rnd.uniform(1, 2.4):.1f}" stroke-linecap="round"/>')
    out.append("".join(fr))
    return "".join(out)


TATAY_SKY = [(0, "#5E8EC8"), (0.22, "#9AB8D8"), (0.4, "#F2D2A8"), (0.5, "#FFC27A"), (0.56, "#FFB066")]


@design("tatay")
def tatay():
    D = Doc2("ph-ty")
    hz = 356
    C = Cam3(f=700, cx=300, cy=hz, yaw=24, pitch=0, pos=(0.7, 1.7, -15.5))
    out = [sky_paint(D, TATAY_SKY, 2501, hz + 2, n=120)]
    # low sun just off the left edge: a broad golden glow
    out.append(soft_glow(D, -40, hz - 30, 420, "#FFD890", 0.75))
    out.append(soft_glow(D, -10, hz - 20, 160, "#FFF4D0", 0.7))
    # clouds: soft, lit gold on their left
    for k, (cx_, cy_, w_, h_) in enumerate(((130, 282, 190, 60), (470, 262, 230, 80), (330, 312, 140, 36))):
        out.append(cloud_bank(D, cx_, cy_, w_, h_, 2502 + k, lit="#FFF0D0", mid="#F4DCCC", shade="#A898B8", light_dir=-1, op=0.85))
    # far mountains, hazy
    out.append(hill(D, ridge([(-20, hz - 34), (90, hz - 58), (180, hz - 40), (300, hz - 70), (420, hz - 46), (520, hz - 62), (620, hz - 36)], 2503, 8, 4), hz + 4,
                    ("#B8B8CC", "#9EA2BC", "#8A8EA8"), 2504, inkw=0, sop=(0.08, 0.2)))
    out.append(hill(D, ridge([(-20, hz - 16), (120, hz - 26), (260, hz - 14), (400, hz - 24), (620, hz - 12)], 2505, 5, 4), hz + 4,
                    ("#8EA88A", "#76907A", "#5E7866"), 2506, inkw=0, sop=(0.08, 0.2)))
    # distant palms and tree line at the horizon
    rnd = random.Random(2507)
    for k in range(14):
        x = rnd.uniform(-10, 610)
        h_ = rnd.uniform(22, 44)
        out.append(far_palm(x, hz + 2, h_, rnd.choice(["#5E7466", "#6A8070"]), 2508 + k, rnd.uniform(-0.1, 0.1)))
    out.append(f'<path d="{blob(300, hz + 1, 340, 6, 2509, 0.2, 20)}" fill="#5E7466"/>')
    # ground beyond the paddies
    out.append(f'<path d="M -10 {hz} L 610 {hz} L 610 610 L -10 610 Z" fill="#7A9A4A"/>')
    out.append(paddies(D, C, 2510, -40, 40, -16, 70, TATAY_SKY, hz, cell=(6.5, 5.0), skip=lambda x, z: -5 < x < 7 and -5 < z < 5))
    # yard of packed earth around the kubo
    yard = [C(-4.2, 0, -4.6), C(6.0, 0, -4.2), C(6.6, 0, 3.6), C(-4.6, 0, 3.4)]
    out.append(f'<path d="{smooth_closed(yard)}" fill="#B89A62"/>')
    out.append(clipped(D, smooth_closed(yard), brush_field(2511, (min(p[0] for p in yard), min(p[1] for p in yard), max(p[0] for p in yard), max(p[1] for p in yard)),
                                                          ["#D8BC80", "#8A7044", "#A8905A", "#7A9A4A"], 90, 4, (10, 40), (1.5, 4), (0.2, 0.5))))
    yr = random.Random(2530)
    tufts = []
    for _ in range(140):
        x, z = yr.uniform(-4.5, 6.5), yr.uniform(-4.6, 3.6)
        if -2 < x < 2.2 and -1.6 < z < 1.6:
            continue
        p = C(x, 0, z)
        dd = max(1, C.depth(x, 0, z))
        hh = 700 / dd * yr.uniform(0.08, 0.2)
        tufts.append(f'<path d="M {p[0]:.1f} {p[1]:.1f} l {yr.uniform(-0.5, 0.5) * hh:.1f} {-hh:.1f}" stroke="{yr.choice(["#7A9A3A", "#A8B860", "#5A7A2A", "#C8B070"])}" stroke-width="1.2" stroke-linecap="round"/>')
    out.append(clipped(D, smooth_closed(yard), tufts))
    # a worn path from the dike to the ladder
    path_ = [C(-1.0, 0, -1.9), C(0.2, 0, -1.9), C(1.4, 0, -4.8), C(-0.6, 0, -4.8)]
    out.append(f'<path d="{smooth_closed(path_)}" fill="#D8C08A" opacity="0.55"/>')
    # banana plants and a coconut palm framing the house
    out.append(banana_plant(D, C(-3.3, 0, 1.8), 170, 2512, lit=-1))
    out.append(banana_plant(D, C(5.2, 0, 2.2), 150, 2514, lit=-1))
    pp = C(4.4, 0, 3.6)
    out.append(palm(D, (pp[0], pp[1]), (pp[0] + 30, pp[1] - 200), 2518, L=80, width=11, nuts=True))
    out.append(kubo34(D, C, 2520))
    out.append(letters(D, 300, 132, "Tatay", SERIF_IT, 120, "#24427E", ["#3E5AA8", "#1A2A5A", "#5A7AC8"], 2522, max_w=360,
                       shadow="#FFF4E0", soff=(0.018, 0.03), angle=-40, hi="#C8D8F8"))
    out.append(ruled(300, 176, "HALIGI NG TAHANAN", "#7A3418", font=JOS, size=21, ls=7, line_w=32, gap=14))
    return finish_b(D, out, 2523)


# ================================================================ 28. balikbayan box — packed full, taped, tied, on its way home
def corned_can(D, cx, base, w, h, seed, col=PULA):
    out = [painted(D, densify([(cx - w / 2, base), (cx - w / 2 * 0.86, base - h), (cx + w / 2 * 0.86, base - h), (cx + w / 2, base)], 6), col, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=5, inkw=1.2, hi=0.5)]
    out.append(f'<path d="{ellipse_d(cx, base - h, w / 2 * 0.86, w * 0.12)}" fill="#D8DEE6" stroke="#5A6270" stroke-width="1"/>')
    out.append(f'<rect x="{cx - w * 0.3:.1f}" y="{base - h * 0.6:.1f}" width="{w * 0.6:.1f}" height="{h * 0.26:.1f}" rx="2" fill="#F6E8C8" opacity="0.9"/>')
    return "".join(out)


@design("balikbayan-box")
def balikbayan_box():
    D = Doc2("ph-bb")
    rnd = random.Random(2600)
    cy = 92
    C = Cam3(f=540, cx=300, cy=cy, yaw=24, pitch=0, pos=(0.1, 1.5, -1.9))
    # the living room abroad at night: a warm wall, a window with snow-blue night outside, the lamp's pool of light
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#5A4A5E"), (0.55, "#6E5A64"), (1, "#3E3040")])}"/>']
    out.append(clipped(D, "M -10 -10 L 610 -10 L 610 380 L -10 380 Z", brush_field(2601, (-40, -10, 610, 380), ["#7A6470", "#4A3A4A", "#8A7078"], 160, -88, (30, 90), (4, 10), (0.15, 0.3))))
    out.append(soft_glow(D, 40, 300, 340, "#FFC878", 0.55))
    win = pd([(400, 196), (530, 196), (530, 300), (400, 300)])
    out.append(f'<path d="{win}" fill="{D.lin([(0, "#1E2A5A"), (1, "#3A4A7A")])}"/>')
    out.append(clipped(D, win, [f'<circle cx="{rnd.uniform(400, 530):.1f}" cy="{rnd.uniform(200, 280):.1f}" r="{rnd.uniform(1, 2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>' for _ in range(22)]
                         + [f'<path d="{pd([(400, 276), (430, 262), (470, 272), (510, 258), (530, 266), (530, 300), (400, 300)])}" fill="#2A2A4A"/>',
                            f'<rect x="440" y="276" width="5" height="7" fill="#FFD890"/><rect x="498" y="270" width="5" height="7" fill="#FFD890"/>',
                            f'<path d="{pd([(400, 290), (530, 284), (530, 300), (400, 300)])}" fill="#E8EEF8" opacity="0.8"/>']))
    for x in (397, 465, 533):
        out.append(taper([(x, 193), (x, 303)], 6, 6, "#E8E0D8"))
    for y in (193, 248, 303):
        out.append(taper([(395, y), (535, y)], 6, 6, "#E8E0D8"))
    # a wall calendar with the flight home circled
    cal = [(96, 196), (170, 199), (167, 290), (93, 287)]
    out.append(f'<path d="{pd(cal)}" fill="#F6F0E4"/><path d="{pd([(96, 196), (170, 199), (169, 218), (95, 215)])}" fill="#C8302A"/>')
    for i in range(5):
        for j in range(4):
            x, y = 101 + i * 13, 226 + j * 14
            out.append(f'<rect x="{x}" y="{y}" width="8" height="8" fill="#B8B0A0" opacity="0.6"/>')
    out.append(f'<path d="{blob(141, 254, 9, 8, 2602, 0.15, 10)}" fill="none" stroke="#E0303A" stroke-width="2.2"/>')
    out.append(f'<text x="132" y="212" text-anchor="middle" {BEBAS} font-size="13" letter-spacing="1" fill="#FFFFFF">DISYEMBRE</text>')
    out.append(f'<path d="M 132 190 L 132 197" stroke="#3A2A2A" stroke-width="1.6"/>')
    # floor and rug
    floor = [C(-4, 0, 6), C(4, 0, 6), C(4, 0, -2.5), C(-4, 0, -2.5)]
    fy = C(0, 0, 3.4)[1]
    out.append(f'<path d="{pd([(-10, fy), (610, fy), (610, 610), (-10, 610)])}" fill="#6A4630"/>')
    out.append(clipped(D, f"M -10 {fy:.1f} L 610 {fy:.1f} L 610 610 L -10 610 Z", brush_field(2603, (-40, fy, 610, 610), ["#8A5E40", "#4A2E1E", "#9A6E48"], 80, 4, (40, 120), (2, 5), (0.2, 0.4))))
    out.append(f'<path d="M -10 {fy:.1f} L 610 {fy:.1f}" stroke="#2A1A14" stroke-width="5" opacity="0.6"/>')
    rug = [C(-0.9, 0, -0.75), C(1.2, 0, -0.75), C(1.2, 0, 1.0), C(-0.9, 0, 1.0)]
    out.append(banig(D, smooth_closed(densify(rug, 20)), 2604, cell=8, base="#D8BC88", bands=("#C8285A", "#2E8A5A", "#F2B21E", "#3A5AB0"), rot_=40))
    out.append(f'<path d="{smooth_closed(densify(rug, 20))}" fill="{D.lin([(0, "#2A1408", 0.1), (1, "#2A1408", 0.4)], 1, 0, 0, 0)}"/>')
    # the box (X right, Z away, Y up), front face toward us at Z = -0.25
    W, Dd, H = 0.34, 0.25, 0.48
    v = lambda x, y, z: C(x, y, z)
    shadow = [v(-W - 0.05, 0, -Dd), v(W + 0.35, 0, -Dd - 0.05), v(W + 0.45, 0, Dd + 0.2), v(-W, 0, Dd)]
    out.append(f'<path d="{smooth_closed(shadow)}" fill="#1A0E08" opacity="0.45"/>')
    card = ("#E8C08A", "#C8945A", "#7A5228")
    front = [v(-W, H, -Dd), v(W, H, -Dd), v(W, 0, -Dd), v(-W, 0, -Dd)]
    side = [v(W, H, -Dd), v(W, H, Dd), v(W, 0, Dd), v(W, 0, -Dd)]
    top = [v(-W, H, -Dd), v(W, H, -Dd), v(W, H, Dd), v(-W, H, Dd)]
    # back and left flaps standing up behind the opening
    for fl in ([v(-W, H, Dd), v(W, H, Dd), v(W, H + 0.3, Dd + 0.12), v(-W, H + 0.3, Dd + 0.12)],
               [v(-W, H, -Dd), v(-W, H, Dd), v(-W - 0.12, H + 0.28, Dd), v(-W - 0.12, H + 0.28, -Dd)]):
        out.append(f'<path d="{pd(fl)}" fill="#B8864E"/>')
        out.append(f'<path d="{pd(fl)}" fill="{D.lin([(0, "#3A2010", 0.35), (1, "#FFE0A8", 0.2)], 0, 1, 0, 0)}"/>')
    # the opening and everything heaped inside it
    out.append(f'<path d="{pd(top)}" fill="#3A2412"/>')
    items = []
    o = v(0, H, 0)
    # tins of corned beef and sardines (no labels you could read), chocolates, a teddy bear, towels, shoes
    o = (o[0], o[1] + 22)
    for k, (x, y, w_, h_, col) in enumerate(((o[0] - 64, o[1] - 6, 30, 34, "#C8302A"), (o[0] - 34, o[1] - 14, 30, 36, "#1E5AB0"), (o[0] - 4, o[1] - 4, 30, 32, "#C8302A"))):
        items.append(f'<rect x="{x:.1f}" y="{y - h_:.1f}" width="{w_}" height="{h_}" fill="{col}"/><ellipse cx="{x + w_ / 2:.1f}" cy="{y - h_:.1f}" rx="{w_ / 2}" ry="5" fill="#D8DEE6"/>'
                     f'<rect x="{x:.1f}" y="{y - h_ * 0.6:.1f}" width="{w_}" height="{h_ * 0.3:.1f}" fill="#FFF2D8" opacity="0.75"/><rect x="{x + 3:.1f}" y="{y - h_:.1f}" width="4" height="{h_}" fill="#FFFFFF" opacity="0.35"/>')
    items.append(painted(D, densify(rot([(o[0] + 20, o[1] - 60), (o[0] + 64, o[1] - 60), (o[0] + 64, o[1] + 4), (o[0] + 20, o[1] + 4)], o[0] + 42, o[1] - 28, 12), 8),
                         ("#C8A0E8", "#7A48B0", "#3E1A66"), 2606, sk=0.2, n=5, inkw=0, hi=0.4))
    items.append(painted(D, densify(rot([(o[0] - 96, o[1] - 50), (o[0] - 60, o[1] - 50), (o[0] - 60, o[1] + 10), (o[0] - 96, o[1] + 10)], o[0] - 78, o[1] - 20, -14), 8),
                         ("#FFF2C8", "#F6D27A", "#B88A2A"), 2607, sk=0.2, n=5, inkw=0, hi=0.4))
    bx, by = o[0] + 76, o[1] - 48
    bear = ("#D8A878", "#A8744A", "#5A3A1E")
    for sg in (-1, 1):
        items.append(painted(D, blob_pts(bx + sg * 19, by - 19, 9, 9, 2611 + sg, 0.05, 10), bear, 2611 + sg, sk=0.25, n=3, inkw=0, hi=0.4))
        items.append(f'<circle cx="{bx + sg * 19}" cy="{by - 19}" r="4" fill="#F2D8B0" opacity="0.8"/>')
    items.append(painted(D, blob_pts(bx, by, 25, 23, 2610, 0.04, 14), bear, 2610, sk=0.25, n=8, inkw=0, hi=0.45))
    items.append(f'<path d="{blob(bx + 2, by + 7, 11, 8, 2614, 0.05, 10)}" fill="#F2D8B0"/><circle cx="{bx + 2}" cy="{by + 3}" r="3" fill="#2A1A0A"/>'
                 f'<circle cx="{bx - 7}" cy="{by - 5}" r="2.6" fill="#1A0A04"/><circle cx="{bx + 10}" cy="{by - 5}" r="2.6" fill="#1A0A04"/>'
                 f'<circle cx="{bx - 8}" cy="{by - 6}" r="0.9" fill="#FFFFFF"/><circle cx="{bx + 9}" cy="{by - 6}" r="0.9" fill="#FFFFFF"/>')
    items.append(taper([(bx - 24, by + 22), (bx + 2, by + 28), (bx + 26, by + 21)], 6, 6, PULA[1]))
    items.append(painted(D, blob_pts(o[0] - 20, o[1] - 40, 30, 14, 2615, 0.05, 12), ("#FFFFFF", "#E8F0F8", "#A8B8C8"), 2615, sk=0.25, n=6, inkw=0, hi=0.4))
    items.append(f'<path d="{smooth_open(ell_pts(o[0] - 20, o[1] - 40, 18, 8, 0, 300, 12))}" stroke="#A8B8C8" stroke-width="1.4" fill="none"/>')
    # folded clothes, a pair of sneakers and bottles of lotion filling the front of the box
    for k, (x, y, col) in enumerate(((o[0] - 62, o[1] + 2, "#E8506A"), (o[0] - 8, o[1] + 6, "#3A8AD0"), (o[0] + 44, o[1] + 2, "#F2E6D0"))):
        items.append(painted(D, densify([(x - 30, y - 16), (x + 30, y - 18), (x + 32, y + 12), (x - 28, y + 14)], 8), (lt(col, 0.3), col, dk(col, 0.35)), 2650 + k, sk=0.2, n=6, inkw=0, hi=0.4))
        items.append(f'<path d="M {x - 28:.1f} {y - 4:.1f} L {x + 30:.1f} {y - 6:.1f}" stroke="{dk(col, 0.3)}" stroke-width="1.2" opacity="0.6"/>')
    for k, (x, y) in enumerate(((o[0] + 96, o[1] - 14), (o[0] + 104, o[1] - 2))):
        items.append(f'<path d="{smooth_closed([(x - 24, y), (x - 20, y - 12), (x + 4, y - 14), (x + 22, y - 6), (x + 24, y + 4), (x - 22, y + 6)])}" fill="#F4F4F8"/>'
                     f'<path d="M {x - 22:.1f} {y + 3:.1f} L {x + 23:.1f} {y + 1:.1f}" stroke="#D8303A" stroke-width="3"/><path d="M {x - 6:.1f} {y - 10:.1f} l 8 4" stroke="#A8B0C0" stroke-width="1.4"/>')
    for k, (x, col) in enumerate(((o[0] - 100, "#F2B8C8"), (o[0] - 86, "#B8E0D0"))):
        items.append(f'<rect x="{x:.1f}" y="{o[1] - 30:.1f}" width="12" height="34" rx="3" fill="{col}"/><rect x="{x + 3:.1f}" y="{o[1] - 36:.1f}" width="6" height="7" fill="#FFFFFF"/>'
                     f'<rect x="{x + 2:.1f}" y="{o[1] - 26:.1f}" width="2.4" height="24" fill="#FFFFFF" opacity="0.5"/>')
    fl_, fr_ = top[0], top[1]
    out.append(clipped(D, pd([(-10, -10), (610, -10), (610, fr_[1]), fr_, fl_, (-10, fl_[1])]), items))
    # side face (in shade) and the lit front, cardboard grain, tape, strap, marker writing
    out.append(f'<path d="{pd(side)}" fill="{dk(card[1], 0.28)}"/>')
    out.append(clipped(D, pd(side), [brush_field(2620, (min(p[0] for p in side), min(p[1] for p in side), max(p[0] for p in side), max(p[1] for p in side)), [card[2], dk(card[1], 0.4)], 30, -90, (10, 30), (1, 3), (0.15, 0.35)),
                                     f'<path d="{pd(side)}" fill="{D.lin([(0, "#2A1E3A", 0.1), (1, "#2A1E3A", 0.35)], 0, 0, 1, 0)}"/>']))
    out.append(f'<path d="{pd(front)}" fill="{card[1]}"/>')
    fb = (min(p[0] for p in front), min(p[1] for p in front), max(p[0] for p in front), max(p[1] for p in front))
    out.append(clipped(D, pd(front), [brush_field(2621, fb, [card[0], card[2], "#F2D098"], 70, -90, (12, 40), (1.5, 4), (0.15, 0.4)),
                                      f'<path d="{pd(front)}" fill="{D.lin([(0, "#FFE8B8", 0.35), (1, "#3A2010", 0.25)], 0, 0, 1, 1)}"/>']))
    out.append(f'<path d="{pd([front[1], side[1], side[2], front[2]])}" fill="none"/>')
    out.append(f'<path d="M {front[1][0]:.1f} {front[1][1]:.1f} L {front[2][0]:.1f} {front[2][1]:.1f}" stroke="#FFE0B0" stroke-width="1.6" opacity="0.6"/>')
    # front flap folded down over the front, right flap open to the side
    ff = [v(-W, H, -Dd), v(W, H, -Dd), v(W, H - 0.1, -Dd - 0.2), v(-W, H - 0.1, -Dd - 0.2)]
    out.append(f'<path d="{pd(ff)}" fill="#D8A86A"/><path d="{pd(ff)}" fill="{D.lin([(0, "#FFF0C8", 0.4), (1, "#7A5228", 0.2)], 0, 0, 0, 1)}"/>')
    rf = [v(W, H, -Dd), v(W, H, Dd), v(W + 0.22, H - 0.08, Dd), v(W + 0.22, H - 0.08, -Dd)]
    out.append(f'<path d="{pd(rf)}" fill="#A8784A"/>')
    # brown tape down the middle of the front, the yellow plastic strap around
    tq = [v(-0.05, H, -Dd - 0.001), v(0.05, H, -Dd - 0.001), v(0.05, 0, -Dd - 0.001), v(-0.05, 0, -Dd - 0.001)]
    out.append(f'<path d="{pd(tq)}" fill="#C89A5A" opacity="0.85"/><path d="{pd(tq)}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, "#FFFFFF", 0.2)], 0, 0, 1, 0)}"/>')
    for y0 in (0.14,):
        st = [v(-W, y0 + 0.03, -Dd - 0.002), v(W, y0 + 0.03, -Dd - 0.002), v(W, y0 + 0.03, Dd), v(W, y0 - 0.02, Dd), v(W, y0 - 0.02, -Dd - 0.002), v(-W, y0 - 0.02, -Dd - 0.002)]
        out.append(f'<path d="{pd(st)}" fill="#F6C51E"/><path d="M {st[0][0]:.1f} {st[0][1]:.1f} L {st[1][0]:.1f} {st[1][1]:.1f} L {st[2][0]:.1f} {st[2][1]:.1f}" stroke="#FFF2A0" stroke-width="1.2" fill="none"/>')
    m = _aff(C, -W + 0.04, H - 0.12, -Dd - 0.003)
    out.append(f'<g transform="{m}"><text x="0" y="0" {SERIF_IT} font-size="7.4" fill="#1E2A5A" transform="rotate(-3)">Para sa pamilya</text></g>')
    m2 = _aff(C, -W + 0.06, 0.3, -Dd - 0.003)
    out.append(f'<g transform="{m2}"><text x="0" y="0" {BEBAS} font-size="7" letter-spacing="0.6" fill="#C8241E">FRAGILE</text>'
               f'<path d="M 34 -6 c -2 -3 -6 -2 -6 1 c 0 3 6 6 6 6 c 0 0 6 -3 6 -6 c 0 -3 -4 -4 -6 -1 z" fill="#D8303A"/></g>')
    m3 = _aff(C, W + 0.002, H - 0.1, -Dd + 0.08, ux=(0, 0, 1))
    out.append(f'<g transform="{m3}"><path d="M 4 12 L 4 2 M 1 5 L 4 2 L 7 5 M 14 12 L 14 2 M 11 5 L 14 2 L 17 5" stroke="#1E2A5A" stroke-width="1.4" fill="none" stroke-linecap="round"/></g>')
    # on the floor: the tape gun's roll, a marker, the packing list
    tp = C(-0.75, 0, -0.55)
    out.append(f'<ellipse cx="{tp[0]:.1f}" cy="{tp[1]:.1f}" rx="26" ry="12" fill="#B8864A"/><ellipse cx="{tp[0]:.1f}" cy="{tp[1] - 6:.1f}" rx="26" ry="12" fill="#D8A868"/>'
               f'<ellipse cx="{tp[0]:.1f}" cy="{tp[1] - 6:.1f}" rx="14" ry="6" fill="#6A4630"/><ellipse cx="{tp[0]:.1f}" cy="{tp[1] - 6:.1f}" rx="26" ry="12" fill="none" stroke="#FFF0C8" stroke-width="1.4" opacity="0.6"/>')
    mk = C(0.62, 0, -0.62)
    out.append(taper([(mk[0] - 30, mk[1] + 6), (mk[0] + 20, mk[1] - 4)], 7, 7, "#1A1A22") + taper([(mk[0] + 20, mk[1] - 4), (mk[0] + 30, mk[1] - 6)], 7, 4, "#E0E0E8"))
    lst = rot([(60, 500), (140, 494), (146, 556), (66, 562)], 103, 528, -8)
    out.append(painted(D, densify(lst, 8), ("#FFFFFF", "#F8F4EC", "#D0C8B8"), 2640, sk=0.1, n=4, inkw=0, hi=0.2))
    for k in range(5):
        a, b = rot([(74, 510 + k * 9), (130, 508 + k * 9)], 103, 528, -8)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0] - (k % 2) * 12:.1f} {b[1]:.1f}" stroke="#4A5AA8" stroke-width="1.2" opacity="0.7"/>')
    out.append(letters(D, 300, 116, "BALIKBAYAN BOX", BEBAS, 84, "#FFF0D8", ["#FFFFFF", "#FFE0B8", "#F8D0A0"], 2630, max_w=460, ls=4, wob=0.5,
                       shadow="#1E1424", soff=(0.018, 0.03), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 152, "PUNO NG PAGMAMAHAL", "#FFC880", font=JOS, size=20, ls=6, line_w=28, gap=12))
    return finish_b(D, out, 2631, "#2A3A4A")


# ================================================================ 29. tuloy po kayo — tsinelas lined up at the open door
@design("tuloy-po-kayo")
def tuloy_po_kayo():
    D = Doc2("ph-tp")
    from summer_gouache import flipflop
    out = room_bg(D, 2701, "#E8C47A", 470, table=("#C8B8A0", "#A89880", "#6A5A48"), light_from=-1, window=True, warm="#FFF6D8", planks=2)
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
    SKY = [(0, "#163A8A"), (0.25, "#3A5AA8"), (0.5, "#C88A9A"), (0.62, "#FFC890"), (0.7, "#FFE6B0")]
    out = [sky_paint(D, SKY, 2801, 430, n=100)]
    SX, SY = 452, 352
    # the sun coming up beside the volcano, eight soft rays fanning out (the flag's sun, seen in the sky)
    out.append(soft_glow(D, SX, SY, 360, "#FFD890", 0.7))
    fid = D.nid()
    D.defs.append(soft_filter(fid, 7))
    rays = []
    for k in range(8):
        a_ = math.radians(-180 + (k + 0.5) * 180 / 8)
        tip = (SX + math.cos(a_) * 520, SY + math.sin(a_) * 520)
        w = 0.07
        b0 = (SX + math.cos(a_ + w) * 520, SY + math.sin(a_ + w) * 520)
        rays.append(f'<path d="{pd([(SX, SY), b0, tip])}" fill="#FFF0C0" opacity="0.22"/>')
    out.append(f'<g filter="url(#{fid})">{"".join(rays)}</g>')
    out.append(soft_glow(D, SX, SY, 70, "#FFFBE8", 0.95))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="24" fill="#FFFCEE"/>')
    # three morning stars still shining
    for k, (x, y, r) in enumerate(((112, 226, 7), (300, 196, 8), (520, 214, 7))):
        out.append(soft_glow(D, x, y, r * 4, "#FFF0B0", 0.6))
        pts = [(x + (r if i % 2 == 0 else r * 0.4) * math.cos(math.radians(-90 + i * 36)), y + (r if i % 2 == 0 else r * 0.4) * math.sin(math.radians(-90 + i * 36))) for i in range(10)]
        out.append(f'<path d="{pd(pts)}" fill="#FFF2C0"/>')
    # clouds catching the first light
    for k in range(7):
        y = 280 + k * 12 + random.Random(2802 + k).uniform(-4, 4)
        x = random.Random(2810 + k).uniform(-40, 520)
        w = random.Random(2820 + k).uniform(120, 260)
        col = mix("#FFD8B0", "#B88AA8", min(1, abs(x + w / 2 - SX) / 420))
        out.append(taper([(x, y), (x + w * 0.45, y - 3), (x + w, y + 2)], 1, 7, col, 0.55))
    # Mayon: the perfect cone, lit on its right flank by the sun, gullies running from the summit, a plume of steam
    HX, HY, base = 250, 214, 418
    cone = [(-30, base + 6)] + [(HX - (HX + 30) * (t ** 1.55), HY + (base - HY) * t) for t in [i / 14 for i in range(14, 0, -1)]]
    cone += [(HX - 6, HY), (HX + 6, HY)] + [(HX + (560 - HX) * (t ** 1.55), HY + (base - HY) * t) for t in [i / 14 for i in range(1, 15)]] + [(610, base + 6)]
    cd = pd(cone)
    out.append(f'<path d="{cd}" fill="#5A5A8A"/>')
    inner = [f'<path d="{cd}" fill="{D.lin([(0, "#3E3E70", 0.9), (0.42, "#6A6A98", 0.4), (0.55, "#E8A890", 0.6), (1, "#FFC8A0", 0.75)], 0, 0, 1, 0)}"/>']
    rnd = random.Random(2830)
    gul = []
    for k in range(70):
        sgn = rnd.choice((-1, 1))
        t0 = rnd.uniform(0.02, 0.25)
        t1 = rnd.uniform(0.5, 1.0)
        spread = rnd.uniform(0.1, 1.0)
        def side_pt(t, f):
            y = HY + (base - HY) * t
            half = (HX + 30 if sgn < 0 else 560 - HX) * (t ** 1.55)
            return (HX + sgn * half * f, y)
        a0, a1 = side_pt(t0, spread), side_pt(t1, spread)
        col = rnd.choice(["#2E2E5A", "#4A4A7A"]) if sgn < 0 else rnd.choice(["#B87A7A", "#FFE0C0", "#8A5A6A"])
        gul.append(f'<path d="M {a0[0]:.1f} {a0[1]:.1f} L {a1[0]:.1f} {a1[1]:.1f}" stroke="{col}" stroke-width="{rnd.uniform(0.8, 2.2):.1f}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    inner.extend(gul)
    inner.append(f'<path d="{cd}" fill="{D.lin([(0, "#FFFFFF", 0), (0.7, "#C8C0D8", 0), (1, "#E8E0F0", 0.55)], 0, 0, 0, 1)}"/>')
    out.append(clipped(D, cd, inner))
    fidp = D.nid()
    D.defs.append(soft_filter(fidp, 3))
    out.append(f'<g filter="url(#{fidp})"><path d="{smooth_closed([(HX - 4, HY - 2), (HX + 10, HY - 26), (HX + 40, HY - 40), (HX + 90, HY - 44), (HX + 120, HY - 36), (HX + 80, HY - 30), (HX + 40, HY - 22), (HX + 10, HY - 6)])}" fill="#F2E0E0" opacity="0.75"/></g>')
    # the plain at its foot: mist, coconut palms, rice fields catching the light
    fidm = D.nid()
    D.defs.append(soft_filter(fidm, 8))
    out.append(f'<path d="{blob(300, base - 4, 380, 18, 2840, 0.2, 18)}" fill="#F8E8E0" opacity="0.6" filter="url(#{fidm})"/>')
    plain = f"M -10 {base} L 610 {base} L 610 610 L -10 610 Z"
    out.append(f'<path d="{plain}" fill="{D.lin([(0, "#7A8A5A"), (1, "#3A4A2A")])}"/>')
    out.append(clipped(D, plain, [brush_field(2841, (-40, base, 610, 610), ["#A8B060", "#5A6A3A", "#C8B878", "#FFD8A0"], 120, -2, (30, 110), (1.5, 4), (0.2, 0.45), 0.05, 3)]))
    for k in range(18):
        x = rnd.uniform(-10, 610)
        dy = rnd.uniform(0, 1) ** 2
        h_ = 22 + dy * 90
        out.append(far_palm(x, base + 2 + dy * 40, h_, mix("#2E3A2A", "#6A7A6A", 0.3 * (1 - dy)), 2850 + k, rnd.uniform(-0.12, 0.12)))
    # the sunrise glinting on wet fields
    out.append(f'<path d="{blob(SX - 40, base + 30, 200, 14, 2858, 0.3, 16)}" fill="#FFD8A8" opacity="0.35"/>')
    # a bamboo railing across the foreground, the welcome garland of sampaguita draped over it
    for x in (40, 300, 560):
        out.append(bamboo_pole((x, 610), (x + 2, 462), 12, 2860 + x, nodes=2))
    out.append(bamboo_pole((-10, 470), (610, 462), 11, 2863, nodes=6))
    out.append(f'<path d="M -10 476 L 610 468" stroke="#2A1A0A" stroke-width="3" opacity="0.35"/>')
    gl = [(40, 468), (150, 506), (300, 520), (450, 506), (560, 466)]
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
        CURRENT["slug"] = slug
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
