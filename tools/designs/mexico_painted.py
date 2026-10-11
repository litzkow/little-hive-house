"""México, hand-painted (gouache / storybook) edition: 30 magnets for Mexican families in the US and anyone who
loves Mexico. Spanish first, with correct accents.

Everything is painted in the house gouache idiom used by brasil_painted.py: warm paper, layered washes with pooled
edges, brush strokes that follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper
grain. Colour story: rosa mexicano, cempasúchil orange, talavera cobalt, turquoise, barro terracotta, agave green,
chile red and maize yellow.

Run from tools/designs:  python3 mexico_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, grass, hill, label, letters, mix, painted, pline, ridge,
                            ruled, shift, sky, soft_glow, specks, taper, catmull, cinnamon_stick, anise)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from paint import conifer
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, sparkle, hibiscus
import holidays_gouache as hg
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, cloth, leaf_simple, bird_v, heart_d, steam,
                            wood_planks, finish_b, tile_roof, branch)

COL = "mexico"
INK = "#3A2418"
FLECK = "#8A6A4A"
lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
ROSA = ("#FF9AC8", "#E6337A", "#9A1050")
MARI = ("#FFD27A", "#F5961E", "#B05A08")
AMAR = ("#FFE89A", "#F6C21C", "#B8860A")
COBALT = ("#5A7ED0", "#1E3F9A", "#0C2060")
TURQ = ("#8EE6DC", "#18A8A0", "#0A6060")
BARRO = ("#EBA676", "#BF6434", "#6E3014")
CHILE = ("#F4907A", "#D2352A", "#7A1010")
AGAVE = ("#A6D4C4", "#4E8E82", "#22504A")
NOPAL = ("#B4D884", "#5E9A3E", "#2A5A1A")
LIMA = ("#CCEB7E", "#7EBA36", "#3A6A12")
MAIZ = ("#FFEFA8", "#F2C640", "#B8861A")
MORADO = ("#C49AE8", "#7A42B8", "#3E1A6A")
VERDE = ("#7CCB7A", "#1F8A4C", "#0E5230")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
CHOC = ("#8A5A3A", "#5A3018", "#2A1408")
BREAD = ("#F6CE86", "#D9913E", "#8A4A16")
FIESTA = ["#E6337A", "#F5961E", "#F6C21C", "#18A8A0", "#7A42B8", "#2E9A4C", "#2E6AC8"]

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def pal_of(c, a=0.38, b=0.38):
    return (lt(c, a), c, dk(c, b))


# ================================================================ méxico toolkit
def papel_flag(D, w, h, col, seed, motif="flower", cut_letter=None, cutfill=None, font=ANTON, holes=True):
    """One papel picado flag in local coords: top-left (0, 0), w x h, a folded hem over the string, a zigzag fringe
    and cut-outs (evenodd holes, so whatever is behind shows through; islands inside holes stay paper)."""
    rnd = random.Random(seed)
    teeth = max(5, int(w / 11))
    outline = [(0, 0), (w, 0)]
    outline += [(w + rnd.uniform(-0.6, 0.6), h * t) for t in (0.3, 0.6)]
    outline.append((w, h))
    for i in range(teeth):
        x1 = w - (i + 0.5) * w / teeth
        x2 = w - (i + 1) * w / teeth
        outline += [(x1, h + h * 0.07), (x2, h)]
    outline += [(rnd.uniform(-0.6, 0.6), h * 0.6), (rnd.uniform(-0.6, 0.6), h * 0.3)]
    sub = [pd(outline)]
    if holes:
        # little diamonds along the hem and the sides
        n = max(4, int(w / 12))
        for i in range(n):
            x = (i + 0.5) * w / n
            sub.append(pd([(x, h * 0.1), (x + 2.6, h * 0.135), (x, h * 0.17), (x - 2.6, h * 0.135)]))
        for sx in (w * 0.09, w * 0.91):
            for j in range(4):
                y = h * (0.3 + j * 0.15)
                sub.append(pd([(sx, y - 3), (sx + 2.2, y), (sx, y + 3), (sx - 2.2, y)]))
        for i in range(teeth):
            x = w - (i + 0.5) * w / teeth
            sub.append(smooth_closed(ell_pts(x, h * 0.93, 1.8, 1.8, 0, 360, 8)[:-1]))
        cx, cy = w / 2, h * 0.56
        R = min(w, h) * 0.3
        if cut_letter:
            pass
        elif motif == "flower":
            sub.append(smooth_closed(ell_pts(cx, cy, R * 0.22, R * 0.22, 0, 360, 10)[:-1]))
            for k in range(8):
                a = math.radians(k * 45 + 22.5)
                px, py = cx + math.cos(a) * R * 0.62, cy + math.sin(a) * R * 0.62
                sub.append(smooth_closed(rot(ell_pts(px, py, R * 0.3, R * 0.13, 0, 360, 10)[:-1], px, py, k * 45 + 22.5)))
            for k in range(4):
                a = math.radians(k * 90 + 45)
                px, py = cx + math.cos(a) * R * 1.12, cy + math.sin(a) * R * 1.12
                sub.append(smooth_closed(ell_pts(px, py, R * 0.08, R * 0.08, 0, 360, 8)[:-1]))
        elif motif == "skull":
            sk = [(cx + R * 0.75 * x, cy + R * 0.85 * y) for x, y in
                  ((0, -1), (0.62, -0.88), (0.95, -0.4), (0.82, 0.18), (0.48, 0.42), (0.42, 0.85), (0, 0.92), (-0.42, 0.85), (-0.48, 0.42), (-0.82, 0.18), (-0.95, -0.4), (-0.62, -0.88))]
            sub.append(smooth_closed(sk))
            for sg in (-1, 1):
                sub.append(smooth_closed(ell_pts(cx + sg * R * 0.33, cy - R * 0.12, R * 0.22, R * 0.24, 0, 360, 10)[:-1]))
            sub.append(pd([(cx, cy + R * 0.12), (cx + R * 0.1, cy + R * 0.3), (cx - R * 0.1, cy + R * 0.3)]))
            for k in range(4):
                x = cx - R * 0.24 + k * R * 0.16
                sub.append(pd([(x - R * 0.05, cy + R * 0.5), (x + R * 0.05, cy + R * 0.5), (x + R * 0.05, cy + R * 0.66), (x - R * 0.05, cy + R * 0.66)]))
        elif motif == "heart":
            sub.append(smooth_closed(heart_d(cx, cy, R * 0.8)))
            for k in range(6):
                a = math.radians(k * 60 - 90)
                px, py = cx + math.cos(a) * R * 1.12, cy + math.sin(a) * R * 1.0
                sub.append(smooth_closed(ell_pts(px, py, R * 0.09, R * 0.09, 0, 360, 8)[:-1]))
        elif motif == "sun":
            sub.append(smooth_closed(ell_pts(cx, cy, R * 0.42, R * 0.42, 0, 360, 16)[:-1]))
            for k in range(12):
                a = math.radians(k * 30)
                p0 = (cx + math.cos(a - 0.12) * R * 0.58, cy + math.sin(a - 0.12) * R * 0.58)
                p1 = (cx + math.cos(a) * R * 1.05, cy + math.sin(a) * R * 1.05)
                p2 = (cx + math.cos(a + 0.12) * R * 0.58, cy + math.sin(a + 0.12) * R * 0.58)
                sub.append(pd([p0, p1, p2]))
        elif motif == "bird":
            b = [(cx - R * 0.9, cy + R * 0.1), (cx - R * 0.3, cy - R * 0.3), (cx + R * 0.2, cy - R * 0.25), (cx + R * 0.5, cy - R * 0.55),
                 (cx + R * 0.75, cy - R * 0.45), (cx + R * 0.95, cy - R * 0.4), (cx + R * 0.7, cy - R * 0.25), (cx + R * 0.5, cy + R * 0.2),
                 (cx, cy + R * 0.45), (cx - R * 0.5, cy + R * 0.4)]
            sub.append(smooth_closed(b))
            sub.append(smooth_closed(ell_pts(cx + R * 0.6, cy - R * 0.42, R * 0.06, R * 0.06, 0, 360, 6)[:-1]))
            sub.append(smooth_closed([(cx - R * 0.2, cy - R * 0.05), (cx + R * 0.25, cy - R * 0.1), (cx + R * 0.1, cy + R * 0.18)]))
    d = " ".join(sub)
    out = [f'<path d="{d}" fill-rule="evenodd" fill="{col}" opacity="0.96"/>']
    cid = D.clip(f'<path d="{d}" clip-rule="evenodd" fill-rule="evenodd"/>')
    out.append(f'<g {cid}>'
               + strokes(D.nid(), pd([(0, 0), (w, 0), (w, h * 1.1), (0, h * 1.1)]), (-4, -4, w + 4, h * 1.1), [lt(col, 0.35), dk(col, 0.15)], seed,
                         n=int(w * h / 160) + 6, angle=-84, length=(h * 0.2, h * 0.6), width=(1, 3), opacity=(0.15, 0.35), curve=0.1)
               + f'<path d="M {w * 0.5:.1f} 0 L {w * 0.52:.1f} {h * 1.1:.1f}" stroke="{dk(col, 0.25)}" stroke-width="1.2" opacity="0.3"/>'
               + f'<rect x="0" y="0" width="{w}" height="{h * 0.07:.1f}" fill="{dk(col, 0.25)}" opacity="0.45"/>'
               + "</g>")
    if cut_letter:
        fs = fit_size(cut_letter, font, int(h * 0.74), w * 0.74)
        out.append(f'<text x="{w / 2:.1f}" y="{h * 0.86:.1f}" text-anchor="middle" {font} font-size="{fs}" fill="{cutfill}">{esc(cut_letter)}</text>')
    out.append(ink(pd(outline), dk(col, 0.45), 1.0, seed, 1, 0.5))
    return "".join(out)


def papel_string(D, x0, y0, x1, y1, sag, specs, seed, w, h, rope="#5A4A3A", shadow=None, cutfill=None, font=ANTON, span=None):
    """A string of papel picado flags. specs: list of (colour, motif or None, letter or None)."""
    out = []
    n = len(specs)

    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)

    rnd = random.Random(seed)
    flags = []
    for i, (col, motif, letter) in enumerate(specs):
        t = (i + 0.5) / n if not span else span[0] + (span[1] - span[0]) * (i + 0.5) / n
        cx, cy = pt(t)
        a, b = pt(t - 0.02), pt(t + 0.02)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) * 0.8 + rnd.uniform(-2.5, 2.5)
        body = papel_flag(D, w, h, col, seed + i * 7, motif or "flower", letter, cutfill, font)
        if shadow:
            sh = f'<path d="{pd([(2, 2), (w + 2, 2), (w + 4, h + 6), (4, h + 6)])}" fill="{shadow}" opacity="0.18"/>'
        else:
            sh = ""
        flags.append(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang:.1f}) translate({-w / 2:.1f} -1)">{sh}{body}</g>')
    ext = 40 if not span else 400
    out.append(ink(smooth_open([pt(i / 40) for i in range(-ext // 40 * 4 - 1, 42 + ext // 40 * 4)]), rope, 1.8, seed, 2, 0.95))
    out += flags
    return "".join(out)


def cempa(D, cx, cy, r, seed, squash=0.88, pal=MARI, inkw=1.0):
    """Cempasúchil (Mexican marigold): a dense pom-pom of ruffled petals, darker in the creases, lit top-left."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy + r * 0.06, r * 1.02, r * squash, seed, 0.12, 18)}" fill="{pal[2]}"/>']
    for ring in range(5):
        rr = r * (1 - ring * 0.2)
        n = int(9 + rr * 0.45)
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.15, 0.15) + ring * 0.37
            px, py = cx + math.cos(a) * rr * 0.7, cy + math.sin(a) * rr * 0.7 * squash
            lit = -(math.cos(a) * 0.6 + math.sin(a) * 0.8) * (rr / r) + ring * 0.12
            c = pal[0] if lit > 0.35 else (dk(pal[1], 0.12) if lit < -0.25 else rnd.choice([pal[1], mix(pal[1], pal[0], 0.4)]))
            ps = r * 0.27 * (1 - ring * 0.08)
            p = blob(px, py, ps, ps * 0.78, seed * 97 + ring * 31 + i, 0.28, 9, math.degrees(a))
            out.append(f'<path d="{p}" fill="{c}"/>')
            out.append(f'<path d="M {px - math.cos(a) * ps * 0.5:.1f} {py - math.sin(a) * ps * 0.5:.1f} q {math.sin(a) * ps * 0.3:.1f} {-math.cos(a) * ps * 0.3:.1f} {math.cos(a) * ps * 0.7:.1f} {math.sin(a) * ps * 0.7:.1f}" '
                       f'stroke="{pal[2]}" stroke-width="{max(0.8, r * 0.035):.1f}" fill="none" opacity="0.55"/>')
    for _ in range(int(r * 0.25)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.14)
        out.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" r="{max(0.8, r * 0.04):.1f}" fill="{pal[2]}" opacity="0.7"/>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.4, r * 0.28, r * 0.14, seed + 3, 0.2, 10, -30)}" fill="#FFF4C8" opacity="0.35"/>')
    if inkw:
        out.append(ink(blob(cx, cy + r * 0.04, r * 0.98, r * squash * 0.98, seed + 1, 0.14, 18), dk(pal[2], 0.3), inkw, seed, 1, 0.45))
    return "".join(out)


def petals(seed, box, n=30, cols=("#F5961E", "#FFB02E", "#E8740E", "#FFD27A"), s=(3, 6), avoid=()):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in avoid):
            continue
        ss = rnd.uniform(*s)
        out.append(f'<path d="{blob(x, y, ss, ss * 0.6, rnd.randint(0, 9999), 0.25, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(0.75, 1):.2f}"/>')
    return "".join(out)


def flame(D, x, y, s, seed, glow=True, gr=None):
    """Candle flame: teardrop with hot core; (x, y) = base of the flame."""
    out = []
    if glow:
        out.append(D.glow(x, y - s * 0.8, gr or s * 5, "#FFC060", 0.55))
    f = [(x, y - s * 2.1), (x + s * 0.5, y - s * 1.1), (x + s * 0.55, y - s * 0.45), (x, y + s * 0.05), (x - s * 0.55, y - s * 0.45), (x - s * 0.5, y - s * 1.1)]
    out.append(f'<path d="{smooth_closed(f)}" fill="#FFB43A"/>')
    f2 = [(x, y - s * 1.6), (x + s * 0.3, y - s * 0.8), (x, y - s * 0.15), (x - s * 0.3, y - s * 0.8)]
    out.append(f'<path d="{smooth_closed(f2)}" fill="#FFF4C0"/>')
    out.append(f'<path d="M {x:.1f} {y + s * 0.1:.1f} l 0 {-s * 0.5:.1f}" stroke="#3A2010" stroke-width="{max(1, s * 0.12):.1f}" stroke-linecap="round"/>')
    return "".join(out)


def candle(D, x, base, w, h, seed, pal=CREAM, lit=True, drips=2, glow_r=None):
    rnd = random.Random(seed)
    top = base - h
    body = [(x - w / 2, top + 3), (x - w / 2 - 0.5, base - 2), (x - w / 2 + 2, base), (x + w / 2 - 2, base), (x + w / 2 + 0.5, base - 2), (x + w / 2, top + 3)]
    out = [cast(D, x + 3, base, w * 0.8, 4, strength=0.4, seed=seed)]
    out.append(painted(D, body, pal, seed, sdir=(0.9, 0.2), sk=0.2, angle=-90, n=max(4, int(h / 6)), inkw=1.2, hi=0.5, hik=0.12))
    out.append(f'<path d="{smooth_closed(ell_pts(x, top + 3, w / 2, w * 0.16, 0, 360, 14)[:-1])}" fill="{lt(pal[1], 0.6)}"/>')
    for k in range(drips):
        dx = x + rnd.uniform(-w * 0.35, w * 0.35)
        L = rnd.uniform(h * 0.15, h * 0.4)
        out.append(taper([(dx, top + 2), (dx + 0.5, top + L * 0.6), (dx, top + L)], max(2.5, w * 0.18), max(2.5, w * 0.16), lt(pal[0], 0.4), 0.95))
    if lit:
        out.append(flame(D, x, top, max(4, w * 0.32), seed, gr=glow_r))
    return "".join(out)


def talavera_tile(D, x, y, s, seed, blue=COBALT, accent=("#FFD27A", "#F2A41E", "#B8660A"), ground="#FBF6EA", kind=0):
    """One hand-painted Talavera tile: tin-white ground, cobalt rosette, ochre/yellow accents, corner quarter-motifs
    that join with the neighbours into a larger pattern."""
    rnd = random.Random(seed)
    cx, cy = x + s / 2, y + s / 2
    out = [f'<path d="{hg.org_rect(x + 0.6, y + 0.6, s - 1.2, s - 1.2, seed, 0.5, 10, 2)}" fill="{ground}"/>']
    if kind == 0:
        for k in range(4):
            a = k * 90 + 45
            px, py = cx + math.cos(math.radians(a)) * s * 0.2, cy + math.sin(math.radians(a)) * s * 0.2
            p = rot(blob_pts(px, py, s * 0.17, s * 0.1, seed + k, 0.1, 10), px, py, a)
            out.append(f'<path d="{smooth_closed(p)}" fill="{blue[1]}" opacity="0.92"/>')
            out.append(f'<path d="{smooth_closed(rot(blob_pts(px, py, s * 0.08, s * 0.04, seed + k + 9, 0.1, 8), px, py, a))}" fill="{blue[0]}" opacity="0.7"/>')
        for k in range(4):
            a = k * 90
            px, py = cx + math.cos(math.radians(a)) * s * 0.26, cy + math.sin(math.radians(a)) * s * 0.26
            out.append(f'<path d="{blob(px, py, s * 0.055, s * 0.055, seed + 20 + k, 0.15, 8)}" fill="{accent[1]}"/>')
        out.append(f'<path d="{blob(cx, cy, s * 0.1, s * 0.1, seed + 30, 0.1, 10)}" fill="{accent[1]}"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.04:.1f}" fill="{blue[2]}"/>')
        for (qx, qy) in ((x, y), (x + s, y), (x, y + s), (x + s, y + s)):
            a0 = math.degrees(math.atan2(cy - qy, cx - qx))
            pts = [(qx, qy)] + [(qx + math.cos(math.radians(a0 + d)) * s * 0.22, qy + math.sin(math.radians(a0 + d)) * s * 0.22) for d in range(-45, 46, 15)]
            out.append(f'<path d="{pd(pts)}" fill="{blue[1]}" opacity="0.9"/>')
            out.append(f'<path d="{pd([(qx, qy)] + [(qx + math.cos(math.radians(a0 + d)) * s * 0.12, qy + math.sin(math.radians(a0 + d)) * s * 0.12) for d in range(-45, 46, 15)])}" fill="{accent[1]}" opacity="0.9"/>')
    else:
        # star tile: an eight-point star, with leafy sprigs in the corners
        out.append(f'<path d="{smooth_closed(jitter([(cx + math.cos(math.radians(k * 22.5)) * s * (0.36 if k % 2 == 0 else 0.2), cy + math.sin(math.radians(k * 22.5)) * s * (0.36 if k % 2 == 0 else 0.2)) for k in range(16)], seed, 0.6))}" fill="{blue[1]}" opacity="0.92"/>')
        out.append(f'<path d="{blob(cx, cy, s * 0.13, s * 0.13, seed, 0.12, 10)}" fill="{accent[1]}"/>')
        out.append(f'<path d="{blob(cx, cy, s * 0.06, s * 0.06, seed + 1, 0.12, 8)}" fill="{ground}"/>')
        for (qx, qy) in ((x, y), (x + s, y), (x, y + s), (x + s, y + s)):
            out.append(f'<path d="{blob(qx, qy, s * 0.14, s * 0.14, seed + int(qx + qy), 0.1, 10)}" fill="{accent[1]}" opacity="0.9"/>')
            out.append(f'<path d="{blob(qx, qy, s * 0.07, s * 0.07, seed + int(qx), 0.1, 8)}" fill="{blue[1]}"/>')
    out.append(strokes(D.nid(), hg.org_rect(x, y, s, s, seed, 0.5, 10, 2), (x, y, x + s, y + s), ["#FFFFFF", blue[0]], seed, n=int(s * s / 300) + 3,
                       angle=-30, length=(s * 0.1, s * 0.3), width=(0.6, 1.6), opacity=(0.08, 0.2)))
    out.append(f'<path d="{blob(x + s * 0.3, y + s * 0.25, s * 0.18, s * 0.06, seed + 40, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.4"/>')
    return "".join(out)


def tile_wall(D, x0, y0, x1, y1, s, seed, grout="#D8CDB8", **kw):
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{grout}"/>']
    j = 0
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            out.append(talavera_tile(D, x, y, s, seed + j, **kw))
            x += s
            j += 1
        y += s
    return "".join(out)


def clay_pot(D, cx, base, w, h, seed, pal=BARRO, neck=0.55, lip=0.62, handles=True, deco="#FFF2DC", soot=True, inside="#2A1208", rim_y=None):
    """Olla de barro: round belly, narrow neck, flared lip, two loop handles, painted cream flourishes, a sooty base."""
    top = base - h
    bw = w / 2
    belly = top + h * 0.6
    pts = [(cx - bw * lip, top), (cx - bw * neck, top + h * 0.12), (cx - bw * 0.82, top + h * 0.32), (cx - bw, belly), (cx - bw * 0.88, base - h * 0.14),
           (cx - bw * 0.5, base), (cx + bw * 0.5, base), (cx + bw * 0.88, base - h * 0.14), (cx + bw, belly), (cx + bw * 0.82, top + h * 0.32),
           (cx + bw * neck, top + h * 0.12), (cx + bw * lip, top)]
    d = smooth_closed(pts)
    out = [cast(D, cx + w * 0.08, base, w * 0.62, h * 0.06, strength=0.45, seed=seed)]
    if handles:
        for sg in (-1, 1):
            hp = [(cx + sg * bw * 0.6, top + h * 0.13), (cx + sg * bw * 0.98, top + h * 0.12), (cx + sg * bw * 1.05, top + h * 0.28), (cx + sg * bw * 0.86, top + h * 0.36)]
            out.append(ink(smooth_open(hp), pal[2], max(5, w * 0.05), seed + sg, 1, 1))
            out.append(ink(smooth_open(hp), pal[1], max(3, w * 0.03), seed + sg + 2, 1, 1))
    out.append(painted(D, pts, pal, seed, sdir=(0.85, 0.35), sk=0.2, angle=-20, n=int(w * h / 110) + 10, slen=(w * 0.08, w * 0.25), sw=(1, 3.2), inkw=2, hi=0.45, hik=0.08, curve=0.4))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    if soot:
        g = D.lin([(0, "#1A0A04", 0), (0.65, "#1A0A04", 0), (1, "#1A0A04", 0.55)])
        inner.append(f'<rect x="{cx - bw - 5:.1f}" y="{top:.1f}" width="{w + 10:.1f}" height="{h + 4:.1f}" fill="{g}"/>')
    if deco:
        # painted band on the shoulder: dashes and dots, a little flower in front
        by = top + h * 0.3
        band = [(cx + bw * 0.86 * t, by + h * 0.05 * (1 - t * t)) for t in [i / 10 - 1 for i in range(21)]]
        inner.append(pline(band, deco, max(1.6, w * 0.012), seed + 5, 0.9, 1))
        inner.append(pline([(x, y + h * 0.08) for x, y in band], deco, max(1.6, w * 0.012), seed + 6, 0.9, 1))
        for i in range(-6, 7):
            x = cx + i * bw * 0.13
            y = by + h * 0.04 * (1 - (i / 7) ** 2) + h * 0.04
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.4, w * 0.011):.1f}" fill="{deco}" opacity="0.9"/>')
        fx, fy = cx - bw * 0.1, top + h * 0.6
        for k in range(5):
            a = math.radians(k * 72 - 90)
            inner.append(taper([(fx, fy), (fx + math.cos(a) * w * 0.07, fy + math.sin(a) * w * 0.07)], w * 0.035, 1, deco, 0.9))
        for sg in (-1, 1):
            inner.append(taper(catmull([(fx + sg * w * 0.05, fy + w * 0.03), (fx + sg * w * 0.14, fy + w * 0.06), (fx + sg * w * 0.2, fy + w * 0.02)], 4), w * 0.022, 1, deco, 0.85))
            inner.append(taper([(fx + sg * w * 0.12, fy + w * 0.05), (fx + sg * w * 0.15, fy + w * 0.0)], w * 0.03, 1, deco, 0.85))
    inner.append(shade_over(D, d, "#2A0E04", 0.35, 0, 0, 1, 0.2, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - bw * 0.72, top + h * 0.38), (cx - bw * 0.82, belly), (cx - bw * 0.7, base - h * 0.22)], max(3, w * 0.04), 1, lt(pal[0], 0.4), 0.55))
    # mouth
    ry = max(4, w * 0.06)
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, bw * lip, ry, 0, 360, 20)[:-1])}" fill="{pal[1]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1, bw * lip - 4, ry - 2.4, 0, 360, 20)[:-1])}" fill="{inside}"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top, bw * lip, ry, 0, 360, 20)[:-1]), INK, 1.6, seed + 9, 1, 0.75))
    return "".join(out)


def jarrito(D, cx, base, h, seed, pal=BARRO, drink="#3A1A0A", deco="#FFF2DC", handle=1, glaze=("#5A3A1A", "#3A2010")):
    """Jarrito de barro: a small clay mug, flared rim with a dark glaze band, cream painted flowers, loop handle."""
    w = h * 0.86
    top = base - h
    bw = w / 2
    pts = [(cx - bw * 0.95, top), (cx - bw * 0.8, top + h * 0.25), (cx - bw, top + h * 0.62), (cx - bw * 0.8, base - 2), (cx - bw * 0.4, base),
           (cx + bw * 0.4, base), (cx + bw * 0.8, base - 2), (cx + bw, top + h * 0.62), (cx + bw * 0.8, top + h * 0.25), (cx + bw * 0.95, top)]
    d = smooth_closed(pts)
    out = [cast(D, cx + w * 0.12, base, w * 0.7, h * 0.07, strength=0.45, seed=seed)]
    hx = cx + handle * bw * 0.85
    hp = [(hx, top + h * 0.2), (hx + handle * w * 0.42, top + h * 0.22), (hx + handle * w * 0.4, top + h * 0.6), (hx + handle * w * 0.05, top + h * 0.72)]
    out.append(ink(smooth_open(hp), pal[2], max(7, w * 0.11), seed, 1, 1))
    out.append(ink(smooth_open(hp), pal[1], max(4, w * 0.07), seed + 1, 1, 1))
    out.append(ink(smooth_open([(x - handle * 2, y - 2) for x, y in hp]), pal[0], 1.6, seed + 2, 1, 0.7))
    out.append(painted(D, pts, pal, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=int(w * h / 90) + 8, inkw=2, hi=0.45, hik=0.08, curve=0.3))
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{pd([(cx - bw - 4, top - 2), (cx + bw + 4, top - 2), (cx + bw + 4, top + h * 0.17), (cx - bw - 4, top + h * 0.21)])}" fill="{glaze[0]}" opacity="0.92"/>']
    inner.append(taper([(cx - bw, top + h * 0.19), (cx, top + h * 0.2), (cx + bw, top + h * 0.17)], 2.2, 2.2, glaze[1], 0.8))
    if deco:
        fx, fy = cx - bw * 0.1, top + h * 0.55
        for k in range(6):
            a = math.radians(k * 60)
            inner.append(f'<path d="{blob(fx + math.cos(a) * h * 0.07, fy + math.sin(a) * h * 0.07, h * 0.055, h * 0.035, seed + k, 0.15, 8, k * 60)}" fill="{deco}" opacity="0.92"/>')
        inner.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{h * 0.035:.1f}" fill="#F2B22E"/>')
        for sg in (-1, 1):
            lx = fx + sg * h * 0.2
            inner.append(taper(catmull([(fx + sg * h * 0.1, fy + h * 0.08), (lx, fy + h * 0.12), (lx + sg * h * 0.12, fy + h * 0.02)], 4), h * 0.025, 1, deco, 0.85))
        for i in range(-4, 5):
            inner.append(f'<circle cx="{cx + i * bw * 0.22:.1f}" cy="{base - h * 0.14 + abs(i) * -0.8:.1f}" r="{max(1.4, h * 0.016):.1f}" fill="{deco}" opacity="0.85"/>')
    inner.append(shade_over(D, d, "#2A0E04", 0.38, 0, 0, 1, 0.2, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - bw * 0.72, top + h * 0.3), (cx - bw * 0.82, top + h * 0.6), (cx - bw * 0.62, base - h * 0.16)], max(3, w * 0.05), 1, "#FFE8D0", 0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, bw * 0.95, h * 0.09, 0, 360, 20)[:-1])}" fill="{glaze[0]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1.2, bw * 0.95 - 4, h * 0.09 - 2.6, 0, 360, 20)[:-1])}" fill="{drink}"/>')
    out.append(f'<path d="{blob(cx - bw * 0.3, top + 1, bw * 0.3, h * 0.025, seed + 4, 0.1, 8)}" fill="#A8683A" opacity="0.6"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top, bw * 0.95, h * 0.09, 0, 360, 20)[:-1]), INK, 1.5, seed + 5, 1, 0.75))
    return "".join(out)


def monarch(D, cx, cy, s, ang, seed, open_=1.0, under=False, inkw=None):
    """Monarch butterfly from above: orange wings, heavy black veins, black borders with white dots.
    s = half wingspan; open_ squashes the wings toward the body (wing beat / perspective)."""
    rnd = random.Random(seed)
    org = ("#FFB24A", "#F07A12", "#A84A06") if not under else ("#FFD49A", "#F2A65A", "#B8702A")
    fore = [(0.04, -0.06), (0.2, -0.42), (0.45, -0.7), (0.75, -0.86), (0.98, -0.84), (1.03, -0.7), (0.94, -0.42), (0.78, -0.18), (0.5, -0.04), (0.1, 0.04)]
    hind = [(0.06, 0.04), (0.35, -0.02), (0.66, 0.06), (0.82, 0.26), (0.8, 0.48), (0.62, 0.66), (0.38, 0.74), (0.16, 0.66), (0.06, 0.38)]
    fv = [((0.06, -0.04), (0.6, -0.62), (0.9, -0.78)), ((0.06, -0.04), (0.5, -0.38), (0.98, -0.6)), ((0.06, -0.02), (0.5, -0.22), (0.9, -0.34)),
          ((0.3, -0.24), (0.62, -0.08), (0.78, -0.12))]
    hv = [((0.08, 0.06), (0.4, 0.12), (0.76, 0.3)), ((0.08, 0.08), (0.36, 0.3), (0.7, 0.56)), ((0.08, 0.1), (0.24, 0.42), (0.42, 0.72)),
          ((0.24, 0.16), (0.5, 0.28), (0.8, 0.44)), ((0.16, 0.18), (0.3, 0.5), (0.24, 0.7))]
    out = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({ang:.1f})">']
    sw = inkw or max(1.2, s * 0.035)
    for sg in (-1, 1):
        def P(pts, k=1.0):
            return [(sg * x * s * open_, y * s) for x, y in pts]
        for shape, veins, dk_ in ((hind, hv, 0.0), (fore, fv, 0.0)):
            o = P(shape)
            dd = smooth_closed(o)
            out.append(f'<path d="{dd}" fill="#1A1210"/>')
            ctr = (sum(p[0] for p in o) / len(o), sum(p[1] for p in o) / len(o))
            inset = [(ctr[0] + (x - ctr[0]) * 0.8, ctr[1] + (y - ctr[1]) * 0.8 - 0.02 * s) for x, y in o]
            inset = [((x + sg * 0.02 * s * open_), y) for x, y in inset]
            out.append(painted(D, inset, org, seed + int(sg * 3) + len(shape), sdir=(sg * 0.6, 0.6), sk=0.12, angle=-60, n=max(4, int(s * 0.4)),
                               inkw=0, hi=0.35, hik=0.08))
            for v in veins:
                out.append(taper([(sg * x * s * open_, y * s) for x, y in catmull(list(v), 3)], max(1.3, s * 0.05), max(1, s * 0.03), "#1A1210", 0.95))
            # white dots in the border
            for i in range(len(o)):
                (x1, y1), (x2, y2) = o[i], o[(i + 1) % len(o)]
                if abs(x1) < 0.15 * s * open_ and abs(x2) < 0.15 * s * open_:
                    continue
                for t in (0.3, 0.7):
                    px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                    px += (ctr[0] - px) * 0.08
                    py += (ctr[1] - py) * 0.08
                    if s > 18:
                        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(0.9, s * 0.025):.1f}" fill="#FFFFFF" opacity="0.9"/>')
        # orange apex spots on the forewing
        if s > 24:
            for (x, y) in ((0.78, -0.68), (0.86, -0.58), (0.7, -0.6)):
                out.append(f'<circle cx="{sg * x * s * open_:.1f}" cy="{y * s:.1f}" r="{s * 0.035:.1f}" fill="#FFC060"/>')
    # body
    out.append(f'<path d="{blob(0, s * 0.12, s * 0.06, s * 0.3, seed, 0.05, 10)}" fill="#1A1210"/>')
    out.append(f'<circle cx="0" cy="{-s * 0.16:.1f}" r="{s * 0.07:.1f}" fill="#1A1210"/>')
    for k in range(3):
        out.append(f'<circle cx="{s * 0.02:.1f}" cy="{s * (0.02 + k * 0.1):.1f}" r="{max(0.7, s * 0.015):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    for sg in (-1, 1):
        out.append(f'<path d="M {sg * s * 0.03:.1f} {-s * 0.2:.1f} q {sg * s * 0.06:.1f} {-s * 0.2:.1f} {sg * s * 0.16:.1f} {-s * 0.3:.1f}" stroke="#1A1210" stroke-width="{max(1, s * 0.02):.1f}" fill="none" stroke-linecap="round"/>')
        out.append(f'<circle cx="{sg * s * 0.16:.1f}" cy="{-s * 0.5:.1f}" r="{max(1, s * 0.025):.1f}" fill="#1A1210"/>')
    out.append("</g>")
    return "".join(out)


def bread_dome(D, cx, cy, rx, ry, seed, pal=BREAD, light=(-0.6, -0.8)):
    pts = blob_pts(cx, cy, rx, ry, seed, 0.04, 18)
    return painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-30, n=int(rx * ry / 40) + 8, slen=(rx * 0.15, rx * 0.4),
                   sw=(rx * 0.02, rx * 0.06), cols=[lt(pal[0], 0.2), pal[2], pal[0], "#C87A2A"], inkw=max(1.2, rx * 0.025), inkop=0.6, hi=0.4, hik=0.08, curve=0.5)


def concha(D, cx, cy, r, seed, top=("#FFFAF0", "#F4E6D0", "#C8B090")):
    """Concha: a golden bun under a sugar crust scored like a seashell (seen in 3/4 view)."""
    rnd = random.Random(seed)
    ry = r * 0.66
    out = [cast(D, cx + r * 0.12, cy + ry * 0.75, r * 1.05, ry * 0.32, strength=0.4, seed=seed)]
    out.append(bread_dome(D, cx, cy, r, ry, seed))
    # sugar crust: sits on the upper part of the dome
    cr = blob_pts(cx, cy - ry * 0.12, r * 0.94, ry * 0.8, seed + 1, 0.035, 22)
    cd = smooth_closed(cr)
    out.append(painted(D, cr, top, seed + 2, sdir=(0.6, 0.8), sk=0.14, angle=-20, n=int(r * 0.8), inkw=0, hi=0.45, hik=0.06))
    cid = D.clip(f'<path d="{cd}"/>')
    inner = []
    # shell scoring: grooves fanning out from the centre, each a crack showing bread
    gx, gy = cx - r * 0.05, cy - ry * 0.18
    n = 9
    for i in range(n):
        a = math.radians(-180 + 360 * i / n + rnd.uniform(-6, 6))
        pts = [(gx + math.cos(a + 0.35 * t) * r * 1.1 * t, gy + math.sin(a + 0.35 * t) * ry * 0.95 * t) for t in (0.12, 0.4, 0.7, 1.05)]
        inner.append(taper(pts, max(1.5, r * 0.06), max(3, r * 0.12), "#C8813A", 0.95))
        inner.append(taper([(x + 1, y + 1.2) for x, y in pts], max(1, r * 0.03), max(1.5, r * 0.05), "#8A4A16", 0.55))
    for k in range(3):
        rr = (k + 1) * 0.28
        arc = [(gx + math.cos(math.radians(a)) * r * rr, gy + math.sin(math.radians(a)) * ry * rr * 0.9) for a in range(0, 361, 20)]
        inner.append(ink(smooth_open(arc), "#C8813A", max(1, r * 0.035), seed + k, 1, 0.45))
    for _ in range(int(r * 1.2)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        inner.append(f'<circle cx="{cx + math.cos(a) * rr * r:.1f}" cy="{cy - ry * 0.12 + math.sin(a) * rr * ry * 0.8:.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="{rnd.choice(["#FFFFFF", top[2], lt(top[1], 0.4)])}" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    inner.append(shade_over(D, cd, dk(top[2], 0.5), 0.35, 0, 0, 1, 1, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(cd, dk(top[2], 0.4), max(1, r * 0.025), seed + 5, 1, 0.5))
    return "".join(out)


def cuerno(D, cx, cy, L, seed, ang=0):
    """Cuerno: a crescent roll of rolled pastry bands, glossy, seams shaded, a dusting of sugar."""
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">', cast(D, cx + 4, cy + L * 0.16, L * 0.52, L * 0.1, strength=0.38, seed=seed)]
    n = 24
    spine = [(cx + (i / n - 0.5) * L, cy + L * 0.06 - 0.22 * L * (1 - (2 * i / n - 1) ** 2)) for i in range(n + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        t = i / n
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ln, dx / Ln
        w = L * 0.17 * math.sin(math.pi * (0.04 + 0.92 * t)) ** 0.9 + 1.5
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    pts = left + right[::-1]
    d = smooth_closed(pts)
    out.append(painted(D, pts, BREAD, seed, sdir=(0.4, 0.9), sk=0.2, angle=-90, n=30, inkw=1.6, hi=0.45, hik=0.12))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k, t in enumerate((0.2, 0.32, 0.44, 0.56, 0.68, 0.8)):
        i = int(t * n)
        (lx, ly), (rx, ry) = left[i], right[i]
        mx, my = (lx + rx) / 2 + (t - 0.5) * L * 0.12, (ly + ry) / 2
        inner.append(taper([(rx, ry), (mx, my), (lx, ly)], 4, 4, "#8A4A16", 0.6))
        j = min(n, i + 1)
        (lx2, ly2), (rx2, ry2) = left[j], right[j]
        inner.append(taper([(rx2 + 2, ry2), ((lx2 + rx2) / 2 + (t - 0.5) * L * 0.12 + 2, (ly2 + ry2) / 2), (lx2 + 2, ly2)], 3, 3, "#FFE2A8", 0.55))
    inner.append(shade_over(D, d, "#4A1A04", 0.35, 0, 0, 0, 1, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(specks(seed, (cx - L * 0.4, cy - L * 0.24, cx + L * 0.4, cy), ["#FFFFFF", "#FFF4D8"], int(L * 0.4), (0.7, 1.5), (0.6, 0.95)))
    out.append("</g>")
    return "".join(out)


# ================================================================ 1. día de muertos — the family ofrenda
def pan_muerto(D, cx, cy, r, seed):
    """Pan de muerto: a sugared round loaf with dough 'bones' crossing on top and a little ball in the middle."""
    ry = r * 0.62
    out = [cast(D, cx + r * 0.1, cy + ry * 0.8, r * 1.0, ry * 0.3, strength=0.45, seed=seed), bread_dome(D, cx, cy, r, ry, seed)]
    for a in (25, -25, 90):
        aa = math.radians(a)
        pts = []
        for t in [i / 8 - 1 for i in range(17)]:
            x = cx + math.cos(aa) * r * 0.85 * t
            y = cy - ry * 0.25 + math.sin(aa) * ry * 0.5 * t - ry * 0.3 * (1 - t * t)
            pts.append((x, y))
        out.append(taper(pts, r * 0.16, r * 0.16, "#B8702A", 1))
        for k in range(len(pts)):
            if k % 3 == 1:
                x, y = pts[k]
                out.append(painted(D, blob_pts(x, y, r * 0.1, r * 0.085, seed + k + a, 0.1, 8), BREAD, seed + k + a, sk=0.2, n=2, inkw=0.9, hi=0.5, hik=0.15))
    out.append(painted(D, blob_pts(cx, cy - ry * 0.62, r * 0.15, r * 0.13, seed + 7, 0.05, 10), BREAD, seed + 7, sk=0.22, n=3, inkw=1, hi=0.5, hik=0.15))
    rnd = random.Random(seed)
    for _ in range(int(r * 2.2)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.95
        out.append(f'<circle cx="{cx + math.cos(a) * rr * r:.1f}" cy="{cy - ry * 0.1 + math.sin(a) * rr * ry * 0.85:.1f}" r="{rnd.uniform(0.7, 1.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    return "".join(out)


def mantel(D, x0, x1, y, h, seed, base="#FFFDF6", trim=ROSA[1]):
    """White embroidered altar cloth over a step: front panel with cut-work scallops and cross-stitch flowers."""
    rnd = random.Random(seed)
    sc = max(6, int((x1 - x0) / 26))
    pts = [(x0 - 4, y), (x1 + 4, y), (x1 + 6, y + h)]
    for i in range(sc):
        xa = x1 + 6 - (i + 0.5) * (x1 - x0 + 12) / sc
        xb = x1 + 6 - (i + 1) * (x1 - x0 + 12) / sc
        pts += [(xa, y + h + 9), (xb, y + h)]
    pts.append((x0 - 6, y + h))
    out = [painted(D, pts, ("#FFFFFF", base, "#C8BBAA"), seed, sdir=(0.3, 1), sk=0.12, angle=-88, n=int((x1 - x0) * h / 120) + 6, inkw=1.2, inkop=0.5, hi=0.3)]
    for i in range(sc):
        xm = x1 + 6 - (i + 0.5) * (x1 - x0 + 12) / sc
        out.append(f'<circle cx="{xm:.1f}" cy="{y + h + 2:.1f}" r="2.2" fill="{trim}" opacity="0.9"/>')
    yy = y + h * 0.5
    x = x0 + 18
    k = 0
    while x < x1 - 10:
        c = FIESTA[k % len(FIESTA)]
        for j in range(4):
            a = math.radians(j * 90 + 45)
            out.append(f'<path d="M {x:.1f} {yy:.1f} l {math.cos(a) * 5:.1f} {math.sin(a) * 5:.1f}" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="1.8" fill="{AMAR[1]}"/>')
        out.append(f'<path d="M {x + 9:.1f} {yy:.1f} l 8 0" stroke="{VERDE[1]}" stroke-width="2" stroke-dasharray="2.5 2" opacity="0.8"/>')
        x += 34
        k += 1
    out.append(f'<path d="M {x0 - 4} {y + 3} L {x1 + 4} {y + 3}" stroke="#B8A890" stroke-width="1.2" opacity="0.5"/>')
    return "".join(out)


def photo_frame(D, cx, cy, w, h, seed, frame=("#F2D06A", "#C8902A", "#7A4A10"), who="abuela"):
    """A framed sepia portrait on the ofrenda (painted softly, no likeness): head and shoulders against a studio wall."""
    x0, y0 = cx - w / 2, cy - h / 2
    out = [cast(D, cx + 5, cy + h / 2 + 2, w * 0.6, 5, strength=0.4, seed=seed)]
    out.append(painted(D, rect_pts(x0, y0, x0 + w, y0 + h, 10, seed, 0.5), frame, seed, sdir=(0.7, 0.7), sk=0.15, angle=-45, n=12, inkw=1.6, hi=0.5))
    ix0, iy0, ix1, iy1 = x0 + w * 0.14, y0 + h * 0.12, x0 + w * 0.86, y0 + h * 0.88
    cid = D.clip(f'<rect x="{ix0:.1f}" y="{iy0:.1f}" width="{ix1 - ix0:.1f}" height="{iy1 - iy0:.1f}" rx="{(ix1 - ix0) * 0.45:.1f}"/>')
    g = D.rad([(0, "#F2E2C2"), (1, "#B89A70")], cx=0.5, cy=0.4, r=0.7)
    pw, ph = ix1 - ix0, iy1 - iy0
    px = (ix0 + ix1) / 2
    body = [f'<rect x="{ix0:.1f}" y="{iy0:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{g}"/>']
    hair = "#4A3020" if who != "abuelo" else "#D8D0C0"
    body.append(f'<path d="{smooth_closed([(px - pw * 0.48, iy1 + 2), (px - pw * 0.4, iy1 - ph * 0.28), (px - pw * 0.15, iy1 - ph * 0.38), (px + pw * 0.15, iy1 - ph * 0.38), (px + pw * 0.4, iy1 - ph * 0.28), (px + pw * 0.48, iy1 + 2)])}" fill="#6A4A32"/>')
    body.append(f'<path d="{blob(px, iy1 - ph * 0.42, pw * 0.08, ph * 0.08, seed, 0.1, 8)}" fill="#C89A72"/>')
    body.append(f'<path d="{blob(px, iy0 + ph * 0.38, pw * 0.2, ph * 0.2, seed + 1, 0.05, 12)}" fill="#D4A880"/>')
    if who == "abuela":
        body.append(f'<path d="{smooth_closed([(px - pw * 0.23, iy0 + ph * 0.42), (px - pw * 0.24, iy0 + ph * 0.24), (px, iy0 + ph * 0.14), (px + pw * 0.24, iy0 + ph * 0.24), (px + pw * 0.23, iy0 + ph * 0.42), (px + pw * 0.16, iy0 + ph * 0.28), (px - pw * 0.16, iy0 + ph * 0.28)])}" fill="{hair}"/>')
        body.append(f'<path d="{blob(px, iy0 + ph * 0.15, pw * 0.1, ph * 0.06, seed + 2, 0.1, 8)}" fill="{hair}"/>')
        body.append(f'<path d="M {px - pw * 0.2:.1f} {iy1 - ph * 0.3:.1f} Q {px:.1f} {iy1 - ph * 0.12:.1f} {px + pw * 0.2:.1f} {iy1 - ph * 0.3:.1f}" stroke="#E8D8B8" stroke-width="{max(1.4, pw * 0.04):.1f}" fill="none" stroke-dasharray="2 2"/>')
    else:
        body.append(f'<path d="{smooth_closed([(px - pw * 0.22, iy0 + ph * 0.34), (px - pw * 0.18, iy0 + ph * 0.2), (px, iy0 + ph * 0.16), (px + pw * 0.18, iy0 + ph * 0.2), (px + pw * 0.22, iy0 + ph * 0.34), (px, iy0 + ph * 0.26)])}" fill="{hair}"/>')
        body.append(f'<path d="{pd([(px - pw * 0.06, iy1 - ph * 0.36), (px + pw * 0.06, iy1 - ph * 0.36), (px + pw * 0.03, iy1 - ph * 0.1), (px - pw * 0.03, iy1 - ph * 0.1)])}" fill="#3A2418"/>')
        body.append(f'<path d="{pd([(px - pw * 0.2, iy1 - ph * 0.38), (px, iy1 - ph * 0.3), (px + pw * 0.2, iy1 - ph * 0.38), (px + pw * 0.1, iy1 - ph * 0.2), (px - pw * 0.1, iy1 - ph * 0.2)])}" fill="#F2E8D8" opacity="0.8"/>')
    body.append(f'<rect x="{ix0:.1f}" y="{iy0:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#8A6A40" opacity="0.18"/>')
    out.append(f'<g {cid}>{"".join(body)}</g>')
    out.append(ink(f'M {ix0:.1f} {iy0 + ph / 2:.1f} a {pw / 2:.1f} {ph / 2:.1f} 0 1 0 {pw:.1f} 0 a {pw / 2:.1f} {ph / 2:.1f} 0 1 0 {-pw:.1f} 0', frame[2], 1.4, seed, 1, 0.8))
    return "".join(out)


def sugar_skull_small(D, cx, cy, s, seed, icing=(ROSA[1], TURQ[1], AMAR[1])):
    pts = [(cx + s * x, cy + s * y) for x, y in ((0, -1), (0.6, -0.92), (0.92, -0.5), (0.9, 0.0), (0.66, 0.3), (0.56, 0.7), (0.3, 0.88), (0, 0.9),
                                                    (-0.3, 0.88), (-0.56, 0.7), (-0.66, 0.3), (-0.9, 0.0), (-0.92, -0.5), (-0.6, -0.92))]
    out = [cast(D, cx + s * 0.15, cy + s * 0.95, s * 0.9, s * 0.2, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#FFFFFF", "#FBF4EC", "#C8B8C8"), seed, sdir=(0.6, 0.6), sk=0.18, angle=-60, n=8, inkw=1.2, hi=0.5))
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * s * 0.36, cy - s * 0.08, s * 0.24, s * 0.26, seed + sg, 0.06, 10)}" fill="{icing[1]}"/>')
        out.append(f'<circle cx="{cx + sg * s * 0.36:.1f}" cy="{cy - s * 0.08:.1f}" r="{s * 0.11:.1f}" fill="{AMAR[0]}"/>')
        out.append(f'<circle cx="{cx + sg * s * 0.33:.1f}" cy="{cy - s * 0.12:.1f}" r="{s * 0.04:.1f}" fill="#FFFFFF"/>')
    out.append(f'<path d="{smooth_closed(heart_d(cx, cy + s * 0.3, s * 0.13, 180))}" fill="{icing[0]}"/>')
    for k in range(5):
        out.append(f'<path d="M {cx - s * 0.3 + k * s * 0.15:.1f} {cy + s * 0.55:.1f} l 0 {s * 0.18:.1f}" stroke="#8A7A8A" stroke-width="1.2"/>')
    out.append(pline([(cx - s * 0.36, cy + s * 0.62), (cx, cy + s * 0.66), (cx + s * 0.36, cy + s * 0.62)], icing[0], 2, seed, 0.9, 1))
    for k in range(5):
        a = math.radians(k * 72 - 90)
        out.append(f'<circle cx="{cx + math.cos(a) * s * 0.12:.1f}" cy="{cy - s * 0.62 + math.sin(a) * s * 0.12:.1f}" r="{s * 0.08:.1f}" fill="{icing[k % 3]}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy - s * 0.62:.1f}" r="{s * 0.06:.1f}" fill="{AMAR[1]}"/>')
    return "".join(out)


def water_glass(D, cx, base, w, h, seed):
    top = base - h
    pts = [(cx - w / 2, top), (cx - w * 0.42, base), (cx + w * 0.42, base), (cx + w / 2, top)]
    out = [cast(D, cx + 3, base, w * 0.6, 3, strength=0.3, seed=seed)]
    out.append(f'<path d="{pd(pts)}" fill="#BFE6F0" opacity="0.45"/>')
    out.append(f'<path d="{pd([(cx - w * 0.47, top + h * 0.25), (cx - w * 0.42, base - 2), (cx + w * 0.42, base - 2), (cx + w * 0.47, top + h * 0.25)])}" fill="#7EC8E0" opacity="0.4"/>')
    out.append(f'<path d="M {cx - w * 0.3:.1f} {top + 4:.1f} L {cx - w * 0.26:.1f} {base - 4:.1f}" stroke="#FFFFFF" stroke-width="2.4" opacity="0.8"/>')
    out.append(ink(pd(pts), "#5A8AA0", 1.2, seed, 1, 0.7))
    out.append(ink(smooth_closed(ell_pts(cx, top, w / 2, 2.6, 0, 360, 12)[:-1]), "#5A8AA0", 1.1, seed + 1, 1, 0.7))
    return "".join(out)


def vase_flowers(D, cx, base, h, seed, pal=BARRO, n=5):
    """A small clay vase stuffed with cempasúchil."""
    out = []
    rnd = random.Random(seed)
    heads = []
    for k in range(n):
        a = math.radians(-90 + (k - (n - 1) / 2) * 26)
        L = h * rnd.uniform(0.75, 1.0)
        hx, hy = cx + math.cos(a) * L * 0.7, base - h * 0.6 + math.sin(a) * L * 0.75
        out.append(taper([(cx, base - h * 0.5), ((cx + hx) / 2, (base - h * 0.5 + hy) / 2 + 3), (hx, hy)], 3, 2, "#4A7A2A"))
        out.append(leaf_simple(D, (cx + hx) / 2, (base - h * 0.5 + hy) / 2, h * 0.22, h * 0.06, math.degrees(a) + rnd.choice([-50, 50]), NOPAL, seed + k, vein=False, inkw=0.8))
        heads.append((hx, hy, h * rnd.uniform(0.17, 0.21), seed + k * 5))
    for hx, hy, r, sd in sorted(heads, key=lambda q: q[1]):
        out.append(cempa(D, hx, hy, r, sd))
    out.append(clay_pot(D, cx, base, h * 0.62, h * 0.6, seed + 30, pal, neck=0.6, lip=0.72, handles=False, soot=False))
    return "".join(out)


def copal(D, cx, base, w, seed):
    """Sahumerio (clay incense burner) with copal smoke curling up."""
    out = [cast(D, cx + 3, base, w * 0.7, 4, strength=0.4, seed=seed)]
    out.append(painted(D, [(cx - w * 0.15, base), (cx - w * 0.1, base - w * 0.35), (cx + w * 0.1, base - w * 0.35), (cx + w * 0.15, base)], BARRO, seed, sk=0.2, n=3, inkw=1.2))
    cup = [(cx - w / 2, base - w * 0.62), (cx - w * 0.36, base - w * 0.34), (cx, base - w * 0.3), (cx + w * 0.36, base - w * 0.34), (cx + w / 2, base - w * 0.62)]
    out.append(painted(D, cup, BARRO, seed + 1, sk=0.2, n=5, inkw=1.4, hi=0.4))
    for k in range(7):
        x = cx - w * 0.36 + k * w * 0.12
        out.append(f'<path d="M {x:.1f} {base - w * 0.58:.1f} l {w * 0.04:.1f} {w * 0.12:.1f}" stroke="#FFF2DC" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<path d="{blob(cx, base - w * 0.62, w * 0.42, w * 0.08, seed + 2, 0.08, 12)}" fill="#3A1A0A"/>')
    out.append(f'<path d="{blob(cx, base - w * 0.64, w * 0.2, w * 0.05, seed + 3, 0.2, 10)}" fill="#FFE07A" opacity="0.85"/>')
    rnd = random.Random(seed)
    for k in range(3):
        x0 = cx + (k - 1) * w * 0.12
        pts = [(x0, base - w * 0.7)]
        for j in range(1, 7):
            pts.append((x0 + math.sin(j * 1.3 + k) * w * 0.25 * j / 6 + j * w * 0.05 * (k - 1), base - w * 0.7 - j * w * 0.32))
        out.append(taper(catmull(pts, 4), w * 0.12, w * 0.02, "#F6F0FA", 0.35 - k * 0.06))
    return "".join(out)


@design("dia-de-muertos")
def dia_de_muertos():
    D = Doc2("mxdm")
    out = [sky(D, [(0, "#2A1440"), (0.6, "#4A1E52"), (1, "#5A2440")], 3, 600, ["#5A2A6A", "#1E0E30", "#7A3A6A"], 110, angle=-84, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 380, 330, "#FFB050", 0.45))
    out.append(blooms(5, ["#7A3A7A", "#3A1A4A", "#A04A6A"], 7, (0, 0, 600, 600), (100, 180), (0.08, 0.14)))
    # papel picado across the top
    specs = [(ROSA[1], "skull", None), (MARI[1], "flower", None), (MORADO[1], "heart", None), (TURQ[1], "skull", None), (AMAR[1], "flower", None),
             ("#2E9A4C", "heart", None), (ROSA[1], "flower", None)]
    out.append(papel_string(D, -30, 26, 630, 26, 30, specs, 101, 82, 84, rope="#E8D8C0", shadow="#0A0410"))
    # lettering
    out.append(letters(D, 300, 214, "Día de Muertos", SERIF_IT, 84, "#FFB43A", ["#FFD27A", "#F5961E", "#FFE8A8"], 102, max_w=470,
                       shadow="#1A0820", soff=(0.025, 0.04), angle=-40, hi="#FFF4D0"))
    out.append(ruled(300, 254, "LOS RECORDAMOS CON AMOR", "#FFE8D0", font=JOS, size=19, ls=4, line_w=24, gap=10, line="#F5961E"))
    # the altar: three steps under embroidered cloths
    steps = [(206, 394, 340, 22), (138, 462, 412, 24), (78, 522, 484, 26)]
    for k, (x0, x1, y, h) in enumerate(steps):
        out.append(painted(D, rect_pts(x0, y, x1, y + 70, 20, 110 + k, 0.5), ("#8A4A2A", "#5A2A18", "#2A120A"), 110 + k, sk=0.1, n=10, inkw=0, hi=0.15))
    # top step: portraits and tall candles
    out.append(photo_frame(D, 266, 300, 58, 72, 120, who="abuela"))
    out.append(photo_frame(D, 338, 304, 50, 64, 121, frame=("#E8C8A0", "#A8784A", "#5A3A1A"), who="abuelo"))
    out.append(candle(D, 222, 342, 16, 52, 122, glow_r=60))
    out.append(candle(D, 380, 342, 16, 46, 123, glow_r=60))
    out.append(mantel(D, *steps[0][:3], steps[0][3], 124))
    # middle step: pan de muerto, sugar skulls, water, marigold vases
    out.append(vase_flowers(D, 168, 410, 92, 130))
    out.append(vase_flowers(D, 432, 410, 92, 131))
    out.append(pan_muerto(D, 300, 388, 52, 132))
    out.append(sugar_skull_small(D, 230, 396, 15, 133))
    out.append(sugar_skull_small(D, 370, 396, 15, 134, (TURQ[1], ROSA[1], MARI[1])))
    out.append(water_glass(D, 252, 410, 16, 26, 135))
    out.append(mantel(D, *steps[1][:3], steps[1][3], 136, trim=MARI[1]))
    # bottom step: a row of votive candles
    for k, x in enumerate((112, 150, 450, 488)):
        out.append(candle(D, x, 474, 15, 26 + (k % 2) * 8, 140 + k, pal=(("#FFF6E0", "#F4E2C0", "#C8A880") if k % 2 else ("#FFC8D8", "#F28AAE", "#B04A74")), drips=1, glow_r=40))
    out.append(copal(D, 300, 476, 40, 145))
    for k, x in enumerate((192, 236, 364, 408)):
        out.append(cempa(D, x, 466, 15, 146 + k))
    out.append(mantel(D, *steps[2][:3], steps[2][3], 150, trim=ROSA[1]))
    # floor: a path of marigold petals leading to the altar
    out.append(f'<rect y="560" width="600" height="40" fill="#2A120A" opacity="0.4"/>')
    out.append(petals(151, (60, 552, 540, 590), 120))
    out.append(petals(152, (220, 540, 380, 600), 40, s=(3, 5)))
    for k, (x, y) in enumerate(((52, 578), (548, 574))):
        out.append(cempa(D, x, y, 20, 155 + k))
    return finish_b(D, out, 159, "#FFE8D0", 0.6)


# ================================================================ 2. pan dulce — the panadería tray, conchas and cuernos
def tongs(D, x, y, L, ang, seed):
    out = [f'<g transform="rotate({ang:.1f} {x:.1f} {y:.1f})">']
    out.append(cast(D, x + L * 0.5, y + 10, L * 0.55, 6, strength=0.3, seed=seed))
    for sg, dy in ((-1, -1), (1, 1)):
        pts = [(x, y + sg * 3), (x + L * 0.3, y + sg * 6), (x + L * 0.75, y + sg * 12), (x + L, y + sg * 10)]
        out.append(taper(catmull(pts, 4), 7, 6, "#8A8E98"))
        out.append(taper(catmull([(px, py - 1.5) for px, py in pts], 4), 2, 2, "#F2F4F8", 0.9))
        for k in range(6):
            t = 0.8 + k * 0.035
            out.append(f'<path d="M {x + L * t:.1f} {y + sg * 8:.1f} l 0 {sg * 7:.1f}" stroke="#5A5E68" stroke-width="1.3"/>')
    out.append(f'<path d="{blob(x - 2, y, 7, 6, seed, 0.1, 10)}" fill="#E6337A"/>')
    out.append(ink(blob(x - 2, y, 7, 6, seed, 0.1, 10), INK, 1.2, seed, 1, 0.7))
    out.append("</g>")
    return "".join(out)


@design("pan-dulce")
def pan_dulce():
    D = Doc2("mxpd")
    out = [paper(D.nid(), "#F8E2D6", FLECK, 201)]
    rnd = random.Random(201)
    # papel-pink wall with a hand-painted scalloped awning stripe
    out.append(blooms(4, ["#F2A8C0", "#FFD0C0", "#E890B0"], 7, (0, 0, 600, 420), (120, 200), (0.12, 0.2)))
    for k in range(-1, 12):
        x = k * 56
        c = ROSA[1] if k % 2 else "#FFF6EE"
        out.append(f'<path d="{hg.org_poly([(x, -10), (x + 56, -10), (x + 56, 46), (x + 28, 64), (x, 46)], 200 + k, 0.6, 10, 1)}" fill="{c}"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 64 L -10 64 Z", (-40, -10, 610, 64), ["#FFFFFF", "#9A1050"], 202, n=60, angle=-88, length=(10, 40), width=(1, 3), opacity=(0.1, 0.25)))
    out.append(ink(smooth_open([(k * 28, 46 + (18 if k % 2 else 0)) for k in range(-1, 24)]), "#9A1050", 1.4, 203, 1, 0.5))
    # turquoise painted table
    out.append(wood_planks(D, 450, 600, 204, TURQ, 3))
    out.append(f'<rect y="444" width="600" height="8" fill="#0A4A4A" opacity="0.5"/>')
    out.append(soft_glow(D, 300, 380, 240, "#FFF2D0", 0.6))
    # the round metal tray, seen in 3/4
    cx, cy, rx, ry = 300, 418, 258, 124
    out.append(cast(D, cx + 16, cy + 26, rx + 6, ry, strength=0.4, seed=205))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40)[:-1])}" fill="#9AA0AA"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy - 4, rx - 10, ry - 8, 0, 360, 40)[:-1])}" fill="{D.lin([(0, "#E8ECF2"), (0.5, "#B8BEC8"), (1, "#D8DCE4")], 0, 0, 1, 1)}"/>')
    out.append(strokes(D.nid(), smooth_closed(ell_pts(cx, cy - 4, rx - 10, ry - 8, 0, 360, 40)[:-1]), (cx - rx, cy - ry, cx + rx, cy + ry), ["#FFFFFF", "#8A909A"], 206, n=60, angle=-8, length=(30, 90), width=(1, 3), opacity=(0.12, 0.3)))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40)[:-1]), "#4A4E58", 1.8, 207, 1, 0.8))
    out.append(ink(smooth_open(ell_pts(cx, cy, rx - 3, ry - 3, 200, 340, 20)), "#FFFFFF", 2.2, 208, 1, 0.8))
    # the bread: back row first
    pinks = ("#FFE4EC", "#F7A8C2", "#C0607E")
    vanilla = ("#FFFCF4", "#F6EAD2", "#C8B08A")
    chocs = ("#A87A5A", "#6E4028", "#3A1E10")
    yel = ("#FFF4C8", "#F6DC8A", "#C8A040")
    out.append(cuerno(D, 170, 374, 128, 210, -14))
    out.append(cuerno(D, 434, 372, 122, 212, 12))
    out.append(concha(D, 302, 350, 74, 211, chocs))
    out.append(concha(D, 200, 432, 76, 213, pinks))
    out.append(concha(D, 404, 434, 76, 214, vanilla))
    out.append(concha(D, 302, 478, 72, 215, yel))
    out.append(tongs(D, 430, 548, 140, -12, 216))
    # sugar crumbs on the table
    out.append(specks(217, (80, 480, 540, 570), ["#FFFFFF", "#F7A8C2", "#F6DC8A"], 40, (0.8, 2), (0.6, 0.95)))
    # lettering
    out.append(letters(D, 300, 180, "pan dulce", SERIF_IT, 116, "#9A2A4A", ["#C03A62", "#701434", "#D85A80"], 218, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#F8B8C8"))
    out.append(ruled(300, 224, "RECIÉN HORNEADO", "#8A4A16", font=JOS, size=22, ls=6, line_w=36, gap=14, line="#E6337A"))
    return finish_b(D, out, 219)


# ================================================================ 3. café de olla — clay pot, jarrito, canela, piloncillo
def piloncillo(D, cx, base, h, seed):
    w = h * 0.7
    pts = [(cx - w * 0.5, base), (cx - w * 0.38, base - h * 0.55), (cx - w * 0.12, base - h * 0.98), (cx + w * 0.12, base - h), (cx + w * 0.38, base - h * 0.55), (cx + w * 0.5, base)]
    out = [cast(D, cx + 6, base, w * 0.7, 6, strength=0.45, seed=seed)]
    out.append(painted(D, pts, ("#D8904A", "#9A5420", "#4A220A"), seed, sdir=(0.9, 0.2), sk=0.25, angle=-80, n=20, inkw=1.6, hi=0.45, hik=0.1))
    out.append(specks(seed, (cx - w * 0.4, base - h * 0.9, cx + w * 0.4, base - 4), ["#F2B86A", "#3A1A06", "#FFD8A0"], 26, (0.7, 1.6), (0.4, 0.9)))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 2, w * 0.5, w * 0.12, 0, 180, 10))}" fill="#6A3410" opacity="0.6"/>')
    return "".join(out)


@design("cafe-de-olla")
def cafe_de_olla():
    D = Doc2("mxco")
    # warm adobe wall, light from the upper left
    out = [sky(D, [(0, "#E89A6A"), (1, "#C86A44")], 301, 600, ["#F2B080", "#B85A36", "#F8C090"], 110, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 140, 120, 360, "#FFE6B0", 0.45))
    out.append(blooms(302, ["#F8C090", "#A84A2A", "#FFD8A8"], 7, (0, 0, 600, 300), (90, 170), (0.08, 0.14)))
    # talavera wainscot
    out.append(tile_wall(D, -12, 286, 612, 470, 46, 303))
    out.append(f'<path d="{hg.org_rect(-10, 278, 620, 10, 304, 0.5, 20, 1)}" fill="#1E3F9A"/>')
    out.append(f'<rect y="286" width="600" height="184" fill="{D.lin([(0, "#2A0E04", 0.2), (0.5, "#2A0E04", 0), (1, "#2A0E04", 0.35)])}"/>')
    # wooden table
    out.append(wood_planks(D, 470, 600, 305, WOOD, 3))
    out.append(f'<rect y="464" width="600" height="10" fill="#4A2A12" opacity="0.6"/>')
    # the olla on its little iron trivet, steam rising
    out.append(clay_pot(D, 196, 488, 236, 210, 306))
    out.append(steam(196, 270, 90, 307, "#FFFFFF", 3, 30, 8, 0.5))
    # cinnamon in the pot
    out.append(cinnamon_stick(D, 214, 268, 246, 226, 12, 308))
    # jarrito in front, right
    out.append(jarrito(D, 410, 552, 120, 309))
    out.append(steam(404, 422, 60, 310, "#FFFFFF", 2, 26, 6, 0.55))
    out.append(cinnamon_stick(D, 420, 438, 458, 402, 10, 311))
    # piloncillo, cinnamon and star anise on the table
    out.append(piloncillo(D, 528, 548, 76, 312))
    out.append(cinnamon_stick(D, 92, 556, 196, 540, 15, 313))
    out.append(cinnamon_stick(D, 102, 574, 214, 566, 13, 314))
    out.append(anise(D, 286, 560, 16, 20, 315))
    out.append(anise(D, 324, 576, 13, -10, 316))
    # lettering
    out.append(letters(D, 300, 140, "café de olla", SERIF_IT, 100, "#FFF4E0", ["#FFFFFF", "#F8DEC0", "#FFE8D0"], 317, max_w=450,
                       shadow="#6E2A10", soff=(0.022, 0.038), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 186, "CON CANELA Y PILONCILLO", "#4A1A06", font=JOS, size=20, ls=5, line_w=28, gap=12))
    return finish_b(D, out, 318)


def monarch_cluster(D, x, y, L, seed):
    """A hanging 'beard' of monarchs asleep with wings closed: tawny teardrops overlapping down a bough."""
    rnd = random.Random(seed)
    out = []
    items = []
    for i in range(int(L * 0.9)):
        t = rnd.random()
        px = x + rnd.uniform(-1, 1) * L * 0.28 * (1 - t * 0.6)
        py = y + t * L
        items.append((py, px, rnd.uniform(4.5, 7)))
    for py, px, s in sorted(items):
        a = rnd.uniform(-25, 25)
        p = rot([(px, py - s * 1.1), (px + s * 0.7, py - s * 0.2), (px + s * 0.45, py + s * 0.7), (px, py + s * 0.9), (px - s * 0.45, py + s * 0.7), (px - s * 0.7, py - s * 0.2)], px, py, a)
        c = rnd.choice(["#E8A060", "#D8883A", "#C87A3A", "#F2B070", "#B86A2A"])
        out.append(f'<path d="{smooth_closed(p)}" fill="{c}" stroke="#2A1810" stroke-width="1"/>')
        out.append(f'<path d="M {px:.1f} {py - s * 0.6:.1f} l {s * 0.3:.1f} {s * 1.1:.1f}" stroke="#2A1810" stroke-width="0.8" opacity="0.7" transform="rotate({a:.0f} {px:.1f} {py:.1f})"/>')
    return "".join(out)


# ================================================================ 4. mariposa monarca — the oyamel forest, coming home
@design("mariposa-monarca")
def mariposa_monarca():
    D = Doc2("mxmm")
    out = [sky(D, [(0, "#FFE6B0"), (0.45, "#F8D4A0"), (1, "#C8D8D0")], 401, 600, ["#FFF0C8", "#F2C890", "#D8E4D8"], 70, sop=(0.08, 0.18))]
    out.append(soft_glow(D, 140, 140, 300, "#FFF6D0", 0.7))
    # light shafts through the forest
    for k, x in enumerate((90, 170, 260)):
        out.append(f'<path d="M {x} -10 L {x + 60} -10 L {x + 260} 610 L {x + 150} 610 Z" fill="#FFF6D8" opacity="0.13"/>')
    rnd = random.Random(402)
    # far oyamel firs, hazy
    for layer, (col, hmin, hmax, base, op) in enumerate(((("#B8C8C0"), 160, 220, 470, 0.9), (("#8AA49A"), 200, 280, 520, 1), (("#5A7A6A"), 260, 340, 580, 1))):
        xs = sorted(rnd.uniform(-20, 620) for _ in range(9 - layer * 2))
        for x in xs:
            h = rnd.uniform(hmin, hmax)
            out.append(f'<rect x="{x - 3 - layer:.1f}" y="{base - h * 0.4:.1f}" width="{6 + layer * 2}" height="{h * 0.45:.1f}" fill="{dk(col, 0.25)}" opacity="{op}"/>')
            out.append(conifer(x, base - h * 0.05, h, col, rnd.randint(0, 9999), width=0.34))
            # monarch clusters cling to the boughs: orange dabs
            for _ in range(int(h * 0.25)):
                t = rnd.uniform(0.1, 0.8)
                yy = base - h * 0.05 - h * t
                ww = h * 0.17 * (1 - t)
                xx = x + rnd.uniform(-ww, ww)
                c = rnd.choice(["#E8892A", "#C86A1E", "#F2A04A", "#A85A20"]) if layer else rnd.choice(["#E8B080", "#D8A070"])
                out.append(f'<path d="{blob(xx, yy, rnd.uniform(1.6, 3.2) + layer, rnd.uniform(2.4, 4.4) + layer, rnd.randint(0, 9999), 0.2, 6)}" fill="{c}" opacity="{0.6 + layer * 0.15:.2f}"/>')
        out.append(f'<rect y="0" width="600" height="600" fill="#F8E8C8" opacity="{0.18 - layer * 0.05:.2f}"/>')
    # a near oyamel on the right, its boughs heavy with sleeping monarchs
    out.append(painted(D, [(500, 610), (508, 300), (516, -10), (548, -10), (556, 300), (566, 610)], ("#9A7A5A", "#6A4A30", "#2E1E12"), 403, sdir=(1, 0), sk=0.25, angle=-90, n=60, inkw=1.8, hi=0.3))
    for k, (y, L) in enumerate(((210, 120), (300, 160), (400, 130))):
        bough = catmull([(530, y), (480, y + 12), (430, y + 30), (530 - L, y + 46)], 4)
        out.append(taper(bough, 9, 2, "#3A2818"))
        for j in range(int(L / 9)):
            t = j / (L / 9)
            x = 530 - t * L + rnd.uniform(-4, 4)
            yy = y + 6 + t * 40 + rnd.uniform(-2, 4)
            out.append(f'<path d="{blob(x, yy - 4, 12 * (1 - t * 0.5), 5, rnd.randint(0, 999), 0.2, 8, -10)}" fill="#2E4A3A" opacity="0.9"/>')
        out.append(monarch_cluster(D, 470 - k * 6, y + 26, 34 + k * 6, 900 + k * 9))
        if k % 2:
            out.append(monarch_cluster(D, 420 - k * 4, y + 38, 26, 950 + k))
    # the ground: mossy forest floor in morning mist
    out.append(hill(D, ridge([(-20, 520), (200, 510), (420, 520), (620, 506)], 404, 4), 620, ("#7A9A5A", "#4A6A3A", "#22381A"), 404, inkw=0))
    out.append(f'<rect y="480" width="600" height="60" fill="{D.lin([(0, "#FFF6E0", 0), (0.5, "#FFF6E0", 0.35), (1, "#FFF6E0", 0)])}"/>')
    out.append(grass(409, (0, 530, 600, 600), ["#2E4A22", "#5A7A3A", "#8AA45A"], 120, (6, 14)))
    # flying monarchs, small to large
    for k in range(18):
        x, y = rnd.uniform(60, 540), rnd.uniform(220, 480)
        if 170 < x < 430 and 230 < y < 420:
            continue
        out.append(monarch(D, x, y, rnd.uniform(6, 12), rnd.uniform(-30, 30), 430 + k, open_=rnd.uniform(0.35, 1), inkw=0.8))
    out.append(monarch(D, 132, 446, 26, -18, 450, open_=0.7))
    out.append(monarch(D, 470, 400, 22, 24, 451, open_=0.45))
    # the hero monarch
    out.append(cast(D, 312, 480, 110, 10, strength=0.18, seed=405))
    out.append(monarch(D, 300, 330, 128, -6, 452))
    # lettering
    out.append(letters(D, 300, 132, "mariposa", SERIF_IT, 96, "#A8400A", ["#D86A1E", "#7A2A06", "#F08A3A"], 406, max_w=400,
                       shadow="#FFF6E0", soff=(0.02, 0.035), angle=-40, hi="#FFC890"))
    out.append(letters(D, 300, 186, "MONARCA", BEBAS, 50, "#2A1A10", ["#4A3020", "#1A0E06"], 407, ls=14, max_w=330, wob=0.4))
    out.append(f'<path d="{blob(300, 532, 220, 26, 410, 0.08, 16)}" fill="#22381A" opacity="0.55"/>')
    out.append(ruled(300, 540, "SIEMPRE REGRESA A CASA", "#FFF4D8", font=JOS, size=20, ls=5, line_w=26, gap=12, line="#FFC060"))
    return finish_b(D, out, 408)


# ================================================================ 5. ¡viva México! — papel picado over the plaza at dusk
def laurel_tree(D, x, base, s, seed, pals=None, haze=0.0):
    pals = pals or [("#7AB06A", "#3E7A44", "#1E4A2A"), ("#9AC07A", "#5A8A4A", "#2E5A2A")]
    if haze:
        pals = [tuple(mix(c, "#8A7AA8", haze) for c in p) for p in pals]
    out = [taper([(x, base), (x - 1, base - s * 0.5)], s * 0.12, s * 0.08, mix("#4A3220", "#8A7AA8", haze))]
    out.append(dab_crown(D, x, base - s * 0.95, s * 0.62, s * 0.52, pals, seed, n=int(s * 1.1), size=(s * 0.08, s * 0.16), inkw=0, base=True))
    return "".join(out)


def kiosco(D, cx, base, w, seed):
    """The plaza bandstand: a raised octagonal platform, slim iron columns, an onion-domed roof."""
    h = w * 0.95
    out = []
    plat = rect_pts(cx - w * 0.6, base - h * 0.2, cx + w * 0.6, base, 12, seed, 0.4)
    out.append(painted(D, plat, ("#F2E2C8", "#D8C0A0", "#8A7458"), seed, sk=0.15, angle=0, n=10, inkw=1.2, hi=0.3))
    for k in range(9):
        x = cx - w * 0.55 + k * w * 0.1375
        out.append(f'<path d="M {x:.1f} {base - h * 0.17:.1f} l 0 {h * 0.12:.1f}" stroke="#8A7458" stroke-width="2"/>')
    out.append(f'<path d="{pd([(cx - w * 0.55, base - h * 0.62), (cx + w * 0.55, base - h * 0.62), (cx + w * 0.55, base - h * 0.2), (cx - w * 0.55, base - h * 0.2)])}" fill="#FFE8A0" opacity="0.35"/>')
    out.append(D.glow(cx, base - h * 0.42, w * 0.8, "#FFD070", 0.45))
    for k in range(5):
        x = cx - w * 0.5 + k * w * 0.25
        out.append(f'<path d="M {x:.1f} {base - h * 0.2:.1f} L {x:.1f} {base - h * 0.62:.1f}" stroke="#2E5A3A" stroke-width="3.2"/>')
    for k in range(4):
        x = cx - w * 0.5 + k * w * 0.25
        out.append(f'<path d="M {x:.1f} {base - h * 0.58:.1f} Q {x + w * 0.125:.1f} {base - h * 0.5:.1f} {x + w * 0.25:.1f} {base - h * 0.58:.1f}" stroke="#2E5A3A" stroke-width="2" fill="none"/>')
    out.append(pline([(cx - w * 0.52, base - h * 0.3), (cx + w * 0.52, base - h * 0.3)], "#2E5A3A", 2, seed, 1, 1))
    roof = [(cx - w * 0.66, base - h * 0.62), (cx - w * 0.4, base - h * 0.78), (cx - w * 0.22, base - h * 0.92), (cx, base - h * 1.08), (cx + w * 0.22, base - h * 0.92), (cx + w * 0.4, base - h * 0.78), (cx + w * 0.66, base - h * 0.62)]
    out.append(painted(D, roof, ("#7ACBA0", "#2E8A6A", "#145A44"), seed + 1, sdir=(0.8, 0.3), sk=0.2, angle=-60, n=16, inkw=1.6, hi=0.4))
    for k in range(-3, 4):
        out.append(f'<path d="M {cx + k * w * 0.18:.1f} {base - h * 0.62:.1f} Q {cx + k * w * 0.08:.1f} {base - h * 0.85:.1f} {cx:.1f} {base - h * 1.06:.1f}" stroke="#145A44" stroke-width="1.2" fill="none" opacity="0.6"/>')
    out.append(f'<path d="M {cx:.1f} {base - h * 1.06:.1f} l 0 {-h * 0.12:.1f}" stroke="#2E5A3A" stroke-width="2"/><circle cx="{cx:.1f}" cy="{base - h * 1.18:.1f}" r="3" fill="#F2C640"/>')
    return "".join(out)


def parroquia(D, cx, base, w, seed, haze=0.3):
    """Town church: ochre façade, two bell towers with domes, a big doorway, warm light inside."""
    hz = lambda c: mix(c, "#9A7AA8", haze)
    h = w * 0.95
    out = []
    wall = (hz("#FFD8A0"), hz("#E8A860"), hz("#9A5A2A"))
    out.append(painted(D, rect_pts(cx - w * 0.3, base - h * 0.62, cx + w * 0.3, base, 14, seed, 0.5), wall, seed, sk=0.12, n=20, inkw=1.2, inkop=0.5, hi=0.3))
    gable = [(cx - w * 0.3, base - h * 0.62), (cx - w * 0.16, base - h * 0.7), (cx, base - h * 0.8), (cx + w * 0.16, base - h * 0.7), (cx + w * 0.3, base - h * 0.62)]
    out.append(painted(D, gable, wall, seed + 1, sk=0.12, n=8, inkw=1.2, inkop=0.5, hi=0.3))
    for sg in (-1, 1):
        tx = cx + sg * w * 0.38
        out.append(painted(D, rect_pts(tx - w * 0.1, base - h * 1.02, tx + w * 0.1, base, 14, seed + 2 + sg, 0.5), wall, seed + 2 + sg, sk=0.15, n=16, inkw=1.2, inkop=0.5, hi=0.3))
        out.append(f'<path d="{hg.org_rect(tx - w * 0.05, base - h * 0.95, w * 0.1, h * 0.14, seed + 5 + sg, 0.3, 6, 6)}" fill="{hz("#3A2030")}"/>')
        out.append(f'<path d="{blob(tx, base - h * 0.86, w * 0.03, w * 0.035, seed + sg, 0.1, 8)}" fill="{hz("#C8902A")}"/>')
        dome = [(tx - w * 0.1, base - h * 1.02), (tx - w * 0.08, base - h * 1.1), (tx, base - h * 1.16), (tx + w * 0.08, base - h * 1.1), (tx + w * 0.1, base - h * 1.02)]
        out.append(painted(D, dome, (hz("#F2C878"), hz("#C8903A"), hz("#7A4A14")), seed + 8 + sg, sk=0.15, n=4, inkw=1.1, inkop=0.5, hi=0.4))
        out.append(f'<path d="M {tx:.1f} {base - h * 1.16:.1f} l 0 {-h * 0.08:.1f} M {tx - 4:.1f} {base - h * 1.21:.1f} l 8 0" stroke="{hz("#5A3A1A")}" stroke-width="1.8"/>')
    out.append(f'<path d="M {cx - w * 0.09:.1f} {base:.1f} L {cx - w * 0.09:.1f} {base - h * 0.3:.1f} Q {cx:.1f} {base - h * 0.42:.1f} {cx + w * 0.09:.1f} {base - h * 0.3:.1f} L {cx + w * 0.09:.1f} {base:.1f} Z" fill="#FFC860"/>')
    out.append(D.glow(cx, base - h * 0.15, w * 0.3, "#FFC060", 0.5))
    out.append(f'<path d="{blob(cx, base - h * 0.5, w * 0.045, w * 0.045, seed + 11, 0.05, 10)}" fill="{hz("#5A3A2A")}"/>')
    return "".join(out)


def street_lamp(D, x, base, h, seed):
    out = [taper([(x, base), (x, base - h)], 3.2, 2.4, "#2A2030")]
    out.append(f'<path d="{pd([(x - 6, base - h - 2), (x + 6, base - h - 2), (x + 4, base - h - 16), (x - 4, base - h - 16)])}" fill="#FFE6A0"/>')
    out.append(D.glow(x, base - h - 9, 34, "#FFD070", 0.6))
    out.append(f'<path d="M {x - 7} {base - h - 16} L {x + 7} {base - h - 16} L {x} {base - h - 22} Z" fill="#2A2030"/>')
    return "".join(out)


@design("viva-mexico")
def viva_mexico():
    D = Doc2("mxvm")
    sky_stops = [(0, "#1E2A6A"), (0.38, "#5A3A8A"), (0.62, "#D8607A"), (0.8, "#F6A05A"), (1, "#F8C878")]
    skyg = D.lin(sky_stops, 0, 0, 0, 600, "userSpaceOnUse")
    out = [f'<rect width="600" height="600" fill="{skyg}"/>',
           strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), ["#FFFFFF", "#3A2A7A", "#F8B888"], 501, n=80, angle=-3, length=(80, 220), width=(5, 14), opacity=(0.04, 0.1), curve=0.1)]
    rnd = random.Random(502)
    for _ in range(26):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 200):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # the plaza: church, laurels, kiosco, lamps
    out.append(parroquia(D, 300, 470, 250, 503, haze=0.35))
    for k, x in enumerate((-10, 70, 520, 600)):
        out.append(laurel_tree(D, x, 500, 110 + (k % 2) * 20, 510 + k, haze=0.25))
    out.append(hill(D, [(-20, 470), (300, 468), (620, 470)], 620, ("#C8A088", "#8A6A70", "#4A3448"), 504, inkw=0, sop=(0.06, 0.14)))
    out.append(f'<ellipse cx="300" cy="520" rx="320" ry="80" fill="{D.rad([(0, "#FFC070", 0.4), (1, "#FFC070", 0)])}"/>')
    out.append(kiosco(D, 300, 512, 150, 505))
    for k, x in enumerate((150, 450)):
        out.append(laurel_tree(D, x, 540, 110, 520 + k))
    for x in (96, 504):
        out.append(street_lamp(D, x, 560, 80, 530))
    from figures import person
    for k, (x, pose, f) in enumerate(((196, "walk", 1), (222, "stand", -1), (404, "couple", 1), (470, "walk", -1), (250, "child_walk", 1))):
        out.append(person(x, 566 + (k % 2) * 4, 34 if pose != "child_walk" else 24, pose, f, None, 540 + k, rim="#FFC878", tint=("#7A4A7A", 0.18)))
    # cobbles in front
    out.append(f'<rect y="566" width="600" height="40" fill="#5A4050" opacity="0.4"/>')
    for k in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(572, 600)
        out.append(f'<path d="{blob(x, y, rnd.uniform(5, 9), rnd.uniform(2, 3), rnd.randint(0, 999), 0.2, 8)}" fill="#C8A0A0" opacity="0.25"/>')
    # papel picado: two strings, letters cut out so the sky shows through
    s1 = [(c, None, ch) for c, ch in zip((ROSA[1], MARI[1], TURQ[1], MORADO[1], "#2E9A4C"), "¡VIVA")]
    s2 = [(c, None, ch) for c, ch in zip((AMAR[1], ROSA[1], "#2E6AC8", MARI[1], "#2E9A4C", MORADO[1], TURQ[1]), "MÉXICO!")]
    out.append(papel_string(D, 30, 52, 570, 52, 22, s1, 550, 100, 122, rope="#FFF2D8", shadow="#1A1030", cutfill=skyg, span=(0.02, 0.98)))
    out.append(papel_string(D, 30, 206, 570, 206, 22, s2, 560, 74, 104, rope="#FFF2D8", shadow="#1A1030", cutfill=skyg, span=(0.0, 1.0)))
    return finish_b(D, out, 509, "#FFFFFF", 0.5)


# ================================================================ 6. calavera de azúcar — a sugar skull, iced by hand
def piped(pts, w, col, hi="#FFFFFF", op=1.0):
    """Royal icing piped in a line: a rounded bead with a little highlight running along the top."""
    return taper(pts, w, w * 0.8, col, op) + taper([(x - w * 0.15, y - w * 0.18) for x, y in pts], w * 0.3, w * 0.2, hi, 0.55)


def icing_dot(x, y, r, col):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>'
            f'<circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.35:.1f}" fill="#FFFFFF" opacity="0.6"/>')


@design("calavera-de-azucar")
def calavera_de_azucar():
    D = Doc2("mxca")
    out = [sky(D, [(0, "#3A0E3A"), (1, "#5A1440")], 601, 600, ["#6A1A5A", "#2A0828", "#8A2A6A"], 110, angle=-60, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 260, 300, "#FF7AB0", 0.32))
    out.append(soft_glow(D, 300, 260, 170, "#FFE0B0", 0.3))
    # a pattern of tiny stars and dots like a tin ornament
    rnd = random.Random(602)
    for _ in range(46):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        if 120 < x < 480 and 50 < y < 520:
            continue
        out.append(sparkle(x, y, rnd.uniform(3, 6), rnd.choice(["#FFD27A", "#FF9AC8", "#8EE6DC"]), 0.8))
    cx, cy, s = 300, 238, 150
    sk = [(cx + s * x, cy + s * y) for x, y in ((0, -1.06), (0.5, -1.0), (0.86, -0.74), (1.0, -0.3), (0.96, 0.08), (0.8, 0.3), (0.76, 0.52), (0.62, 0.62),
                                               (0.56, 0.86), (0.36, 1.0), (0, 1.04), (-0.36, 1.0), (-0.56, 0.86), (-0.62, 0.62), (-0.76, 0.52), (-0.8, 0.3),
                                               (-0.96, 0.08), (-1.0, -0.3), (-0.86, -0.74), (-0.5, -1.0))]
    skd = smooth_closed(sk)
    out.append(cast(D, cx + 14, cy + s * 1.08, s * 0.9, s * 0.12, strength=0.5, seed=603))
    out.append(painted(D, sk, ("#FFFFFF", "#FBF2EA", "#C8B4C8"), 604, sdir=(0.6, 0.7), sk=0.12, angle=-60, n=60, inkw=2.2, inkc="#5A2A4A", hi=0.5))
    cid = D.clip(f'<path d="{skd}"/>')
    sug = [specks(605, (cx - s, cy - s * 1.1, cx + s, cy + s * 1.1), ["#FFFFFF", "#E8D8E0", "#D8C8D8"], 500, (0.6, 1.4), (0.4, 0.9))]
    sug.append(shade_over(D, skd, "#5A2A6A", 0.35, 0, 0, 1, 1, 0.5))
    # cheek hollows and temple shading
    for sg in (-1, 1):
        sug.append(f'<path d="{blob(cx + sg * s * 0.74, cy + s * 0.42, s * 0.16, s * 0.2, 606 + sg, 0.1, 10)}" fill="#B8A0C0" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(sug)}</g>')
    # forehead: an iced flower with leaves and dot-swirls
    fx, fy = cx, cy - s * 0.62
    for k in range(8):
        a = math.radians(k * 45 - 90)
        px, py = fx + math.cos(a) * s * 0.14, fy + math.sin(a) * s * 0.11
        p = rot(blob_pts(px, py, s * 0.1, s * 0.06, 607 + k, 0.08, 10), px, py, k * 45 - 90)
        out.append(painted(D, p, ROSA, 607 + k, sk=0.2, n=3, inkw=1, inkc="#7A0A3A", hi=0.5, hik=0.15))
    out.append(icing_dot(fx, fy, s * 0.07, AMAR[1]))
    for sg in (-1, 1):
        for j, (dx, dy, a) in enumerate(((0.26, 0.04, 20), (0.36, -0.06, -20))):
            out.append(leaf_simple(D, fx + sg * s * 0.14, fy + s * 0.02, s * 0.24, s * 0.06, 90 - sg * 90 + sg * a - sg * 5, ("#9AE0A0", "#2E9A5A", "#145A30"), 608 + j + sg, vein=False, inkw=0.9))
        for j in range(6):
            t = j / 5
            ax = fx + sg * s * (0.48 + 0.08 * math.sin(t * 3))
            ay = fy - s * 0.24 + t * s * 0.4
            out.append(icing_dot(ax, ay, s * 0.022, TURQ[1] if j % 2 else MARI[1]))
    # piped scallop along the brow
    brow = [(cx + s * x, cy + s * y) for x, y in ((-0.86, -0.34), (-0.5, -0.4), (0, -0.36), (0.5, -0.4), (0.86, -0.34))]
    for i in range(14):
        t = i / 13
        x = cx - s * 0.84 + t * s * 1.68
        y = cy - s * 0.38 - 0.03 * s * math.sin(t * math.pi)
        out.append(f'<path d="M {x - s * 0.06:.1f} {y:.1f} q {s * 0.06:.1f} {-s * 0.07:.1f} {s * 0.12:.1f} 0" stroke="{MORADO[1]}" stroke-width="{s * 0.028:.1f}" fill="none" stroke-linecap="round"/>')
    # eyes: deep turquoise sockets ringed with piped petals, shiny foil centres
    for sg in (-1, 1):
        ex, ey = cx + sg * s * 0.4, cy - s * 0.04
        sock = blob_pts(ex, ey, s * 0.27, s * 0.25, 610 + sg, 0.05, 14, sg * 8)
        for k in range(12):
            a = math.radians(k * 30)
            px, py = ex + math.cos(a) * s * 0.3, ey + math.sin(a) * s * 0.28
            out.append(f'<path d="{blob(px, py, s * 0.07, s * 0.05, 611 + k, 0.1, 8, k * 30)}" fill="{ROSA[0] if k % 2 else MARI[0]}" stroke="#9A1050" stroke-width="1" />')
        out.append(painted(D, sock, TURQ, 612 + sg, sdir=(0.6, 0.7), sk=0.25, n=10, inkw=1.6, inkc="#0A3A3A", hi=0.3))
        g = D.rad([(0, "#FFF8D8"), (0.4, "#F2C640"), (0.8, "#B8860A"), (1, "#7A5A0A")], 0.4, 0.35, 0.6)
        out.append(f'<path d="{blob(ex, ey, s * 0.14, s * 0.13, 613 + sg, 0.05, 12)}" fill="{g}"/>')
        for k in range(8):
            a = math.radians(k * 45 + 10)
            out.append(f'<path d="M {ex:.1f} {ey:.1f} l {math.cos(a) * s * 0.13:.1f} {math.sin(a) * s * 0.12:.1f}" stroke="#FFF4C0" stroke-width="1.2" opacity="0.5"/>')
        out.append(f'<circle cx="{ex - s * 0.05:.1f}" cy="{ey - s * 0.05:.1f}" r="{s * 0.03:.1f}" fill="#FFFFFF"/>')
    # nose: an upside-down heart
    out.append(painted(D, heart_d(cx, cy + s * 0.3, s * 0.13, 180), CHILE, 614, sk=0.2, n=4, inkw=1.2, hi=0.5, hik=0.15))
    # cheek swirls
    for sg in (-1, 1):
        sw = [(cx + sg * s * (0.62 + 0.1 * math.cos(a)) , cy + s * (0.36 + 0.1 * math.sin(a)) ) for a in [t * 0.5 for t in range(14)]]
        sw = [(cx + sg * s * 0.66 + sg * s * 0.14 * (1 - i / 14) * math.cos(i * 0.55), cy + s * 0.36 + s * 0.12 * (1 - i / 14) * math.sin(i * 0.55)) for i in range(14)]
        out.append(piped(sw, s * 0.035, "#2E9A5A"))
    # mouth: teeth in a row, stitched, framed by piped icing
    mx, my = cx, cy + s * 0.68
    for k in range(-4, 5):
        x = mx + k * s * 0.075
        tp = hg.org_rect(x - s * 0.034, my - s * 0.07 - abs(k) * 0.6, s * 0.068, s * 0.15, 615 + k, 0.4, 6, 3)
        out.append(f'<path d="{tp}" fill="#FFFDF8" stroke="#A890A8" stroke-width="1.3"/>')
    out.append(piped([(mx - s * 0.36, my), (mx, my + s * 0.02), (mx + s * 0.36, my)], s * 0.03, MORADO[1]))
    for k in range(-4, 5):
        out.append(f'<path d="M {mx + k * s * 0.075:.1f} {my - s * 0.03:.1f} l 0 {s * 0.06:.1f}" stroke="#5A2A4A" stroke-width="1.6"/>')
    out.append(piped([(mx - s * 0.42, my - s * 0.1), (mx - s * 0.2, my - s * 0.15), (mx, my - s * 0.13), (mx + s * 0.2, my - s * 0.15), (mx + s * 0.42, my - s * 0.1)], s * 0.035, ROSA[1]))
    out.append(piped([(mx - s * 0.42, my + s * 0.12), (mx - s * 0.2, my + s * 0.17), (mx, my + s * 0.18), (mx + s * 0.2, my + s * 0.17), (mx + s * 0.42, my + s * 0.12)], s * 0.035, ROSA[1]))
    for k in range(-3, 4):
        out.append(icing_dot(mx + k * s * 0.11, my + s * 0.28 - abs(k) * 1.5, s * 0.025, [AMAR[1], TURQ[1], MARI[1]][k % 3]))
    # marigolds and petals at its base
    for k, (x, y, r) in enumerate(((128, 392, 30), (472, 392, 30), (82, 432, 20), (518, 432, 20), (180, 410, 20), (420, 410, 20))):
        out.append(cempa(D, x, y, r, 620 + k))
    out.append(petals(630, (90, 396, 510, 428), 24, avoid=((200, 380, 400, 430),)))
    # lettering
    out.append(letters(D, 300, 506, "calavera", SERIF_IT, 92, "#FFD27A", ["#FFE8A0", "#F5961E", "#FFF4C8"], 631, max_w=360,
                       shadow="#1A0418", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 540, "DE AZÚCAR", "#FF9AC8", font=JOS, size=20, ls=8, line_w=40, gap=14))
    return finish_b(D, out, 632, "#FFFFFF", 0.5)


# ================================================================ 7. tacos al pastor — the trompo glowing at the corner taquería
def rotulo(D, cx, cy, s, font, size, fill, outline, shadow, seed, ls=0, max_w=420, skew=0):
    """Hand-painted sign lettering (rótulo): flat fill, a contrasting keyline and a hard block shadow."""
    fs = fit_size(s, font, size, max_w, ls)
    xx = cx + ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    t = lambda dx, dy, extra: f'<text x="{xx + dx:.1f}" y="{cy + dy:.1f}" text-anchor="middle" {font} font-size="{fs}"{lsa} {extra}>{esc(s)}</text>'
    out = [f'<g transform="skewX({skew})">' if skew else "<g>"]
    for k in range(1, 6):
        out.append(t(k * 1.1, k * 1.1, f'fill="{shadow}"'))
    out.append(t(0, 0, f'fill="{fill}" stroke="{outline}" stroke-width="{max(2, fs * 0.07):.1f}" stroke-linejoin="round" paint-order="stroke"'))
    out.append(t(0, 0, f'fill="{fill}"'))
    uid = D.nid()
    rnd = random.Random(seed)
    W = measure(s, font, fs, ls)
    st = "".join(f'<path d="M {rnd.uniform(cx - W / 2, cx + W / 2):.1f} {cy - fs * rnd.uniform(0.1, 0.8):.1f} l {rnd.uniform(10, 30):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#FFFFFF", dk(fill, 0.2)])}" stroke-width="{rnd.uniform(1, 2.4):.1f}" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>' for _ in range(int(W / 4)))
    out.append(f'<clipPath id="{uid}">{t(0, 0, "")}</clipPath><g clip-path="url(#{uid})">{st}</g>')
    out.append("</g>")
    return "".join(out)


def trompo(D, cx, top, bot, w_top, w_bot, seed):
    """The al pastor spit, shaped like a spinning top: stacked achiote-red slabs with ragged charred edges,
    a shaved face, dripping fat, and a pineapple crowning the skewer."""
    rnd = random.Random(seed)
    out = []
    out.append(f'<rect x="{cx - 3}" y="{top - 60}" width="6" height="{bot - top + 90}" fill="#8A8E98"/>')
    out.append(f'<rect x="{cx - 1}" y="{top - 60}" width="2" height="{bot - top + 90}" fill="#E8ECF4" opacity="0.7"/>')
    n = 18
    pts_l, pts_r = [], []
    for i in range(n + 1):
        t = i / n
        y = top + (bot - top) * t
        w = (w_top + (w_bot - w_top) * t ** 1.4) / 2
        j = 5 if i % 2 else -2
        pts_l.append((cx - w - j + rnd.uniform(-2, 2), y))
        pts_r.append((cx + w + j + rnd.uniform(-2, 2), y))
    body = pts_l + pts_r[::-1]
    d = pd(body)
    out.append(painted(D, body, ("#F2884A", "#C23C1A", "#4A0E04"), seed, sdir=(0.8, 0.2), sk=0.24, angle=-5, n=110, slen=(20, 60), sw=(2, 5),
                       cols=["#F6A050", "#8A1E0A", "#E86A2A", "#3A0A02"], inkw=2, hi=0.45, hik=0.08, curve=0.3))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for i in range(1, n * 2):
        t = i / (n * 2)
        y = top + (bot - top) * t
        w = (w_top + (w_bot - w_top) * t ** 1.4) / 2 + 6
        wav = [(cx - w + j * w / 6, y + math.sin(j * 1.3 + i) * 2.4 + (j - 6) ** 2 * 0.08) for j in range(13)]
        inner.append(taper(wav, rnd.uniform(1.6, 3.6), rnd.uniform(1.2, 2.6), rnd.choice(["#3A0A02", "#6A1A08", "#5A1004"]), rnd.uniform(0.4, 0.75)))
        if i % 3 == 0:
            inner.append(taper([(x, y - 3) for x, y in wav], 1.4, 1, "#FFB070", 0.45))
    # shaved face: lighter, juicy cut meat in the middle-left
    for k in range(5):
        y = top + (bot - top) * (0.15 + k * 0.16)
        w = (w_top + (w_bot - w_top) * ((y - top) / (bot - top)) ** 1.4) / 2
        inner.append(f'<path d="{blob(cx - w * 0.2, y, w * 0.45, (bot - top) * 0.05, seed + k, 0.25, 10)}" fill="#F08A5A" opacity="0.55"/>')
    for _ in range(40):
        y = rnd.uniform(top, bot)
        side = rnd.choice([-1, 1])
        t = (y - top) / (bot - top)
        w = (w_top + (w_bot - w_top) * t ** 1.4) / 2
        inner.append(f'<path d="{blob(cx + side * w * 0.92, y, rnd.uniform(6, 12), rnd.uniform(2, 4), rnd.randint(0, 999), 0.3, 8)}" fill="#1E0400" opacity="0.75"/>')
    for _ in range(30):
        y = rnd.uniform(top + 6, bot - 6)
        x = cx + rnd.uniform(-w_top * 0.35, w_top * 0.15)
        inner.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(4, 10):.1f} 0" stroke="#FFE2B0" stroke-width="1.6" stroke-linecap="round" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    inner.append(shade_over(D, d, "#1A0400", 0.55, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for _ in range(5):
        x = cx + rnd.uniform(-w_bot * 0.4, w_bot * 0.4)
        out.append(taper([(x, bot - 2), (x + 0.5, bot + rnd.uniform(6, 14))], 3, 2, "#E87A3A", 0.8))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w_top / 2 + 3, 10, 0, 360, 20)[:-1])}" fill="#8A2A10"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top - 2, w_top / 2 - 8, 7, 0, 360, 20)[:-1])}" fill="#B8481E"/>')
    # pineapple crown on the skewer
    py = top - 30
    for k in range(9):
        a = -90 + (k - 4) * 17
        out.append(leaf_simple(D, cx, py - 18, 46 - abs(k - 4) * 5, 6.5, a, ("#9ACB7A", "#3E8A44", "#1E5A2A"), seed + 10 + k, vein=False, inkw=1))
    pin = blob_pts(cx, py, 28, 24, seed + 3, 0.05, 16)
    out.append(painted(D, pin, ("#FFE27A", "#F2B42A", "#A86A0A"), seed + 3, sdir=(0.8, 0.4), sk=0.2, angle=-60, n=16, inkw=1.6, hi=0.5))
    pc = D.clip(f'<path d="{smooth_closed(pin)}"/>')
    lat = "".join(f'<path d="M {cx + k * 10 - 30:.1f} {py - 30:.1f} l 40 60 M {cx + k * 10 + 30:.1f} {py - 30:.1f} l -40 60" stroke="#B8781A" stroke-width="1.4" opacity="0.6"/>' for k in range(-4, 5))
    out.append(f'<g {pc}>{lat}</g>')
    return "".join(out)


def taco(D, cx, cy, r, seed, rot_=0):
    """Street taco seen from above at an angle: doubled corn tortillas heaped with pastor, onion, cilantro, pineapple."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">']
    for k, (dx, dy) in enumerate(((5, 3), (0, 0))):
        tp = blob_pts(cx + dx, cy + dy, r, r * 0.62, seed + k, 0.04, 20)
        out.append(painted(D, tp, ("#FFF0B8", "#F2D68A", "#B89A4A"), seed + k, sdir=(0.6, 0.8), sk=0.12, angle=-20, n=10, inkw=1.4, hi=0.4))
    out.append(specks(seed, (cx - r * 0.9, cy - r * 0.55, cx + r * 0.9, cy + r * 0.55), ["#8A5A1A", "#C89A4A"], int(r * 0.6), (0.7, 1.6), (0.3, 0.7)))
    for _ in range(int(r * 0.42)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.68
        x, y = cx + math.cos(a) * rr * r, cy + math.sin(a) * rr * r * 0.6
        out.append(painted(D, blob_pts(x, y, rnd.uniform(5, 8), rnd.uniform(3.5, 5.5), rnd.randint(0, 999), 0.25, 8, rnd.uniform(0, 180)),
                           ("#F28A4A", "#C8401E", "#6A1406"), rnd.randint(0, 999), sk=0.3, n=2, inkw=0.8, inkop=0.5, hi=0.4))
    for _ in range(int(r * 0.35)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.6
        x, y = cx + math.cos(a) * rr * r, cy + math.sin(a) * rr * r * 0.6
        out.append(f'<path d="{hg.org_rect(x, y, rnd.uniform(3, 5), rnd.uniform(3, 5), rnd.randint(0, 999), 0.4, 6, 1)}" fill="#FFFDF4" stroke="#C8C0D8" stroke-width="0.6"/>')
    for _ in range(int(r * 0.4)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.66
        x, y = cx + math.cos(a) * rr * r, cy + math.sin(a) * rr * r * 0.6
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 3.6), rnd.uniform(1.6, 2.6), rnd.randint(0, 999), 0.3, 7, rnd.uniform(0, 180))}" fill="{rnd.choice(["#2E8A3A", "#4AAA4A", "#1E6A2A"])}"/>')
    for _ in range(3):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.45)
        x, y = cx + math.cos(a) * rr * r, cy + math.sin(a) * rr * r * 0.6
        out.append(painted(D, rect_pts(x - 5, y - 4, x + 5, y + 4, 4, rnd.randint(0, 999), 0.5), ("#FFF0A0", "#F6C83A", "#B8860A"), rnd.randint(0, 999), sk=0.2, n=2, inkw=0.8, hi=0.5))
    out.append("</g>")
    return "".join(out)


def lime_wedge(D, cx, cy, s, seed, rot_=0):
    pts = rot([(cx - s, cy), (cx - s * 0.6, cy - s * 0.55), (cx, cy - s * 0.72), (cx + s * 0.6, cy - s * 0.55), (cx + s, cy)], cx, cy, rot_)
    out = [painted(D, pts, ("#C8F07A", "#6EB82E", "#2E6A0E"), seed, sk=0.2, n=4, inkw=1.4, hi=0.4)]
    inner = rot([(cx - s * 0.8, cy - s * 0.06), (cx - s * 0.5, cy - s * 0.45), (cx, cy - s * 0.58), (cx + s * 0.5, cy - s * 0.45), (cx + s * 0.8, cy - s * 0.06)], cx, cy, rot_)
    out.append(f'<path d="{smooth_closed(inner)}" fill="#E8F8B0"/>')
    for k in range(5):
        a = math.radians(180 + 20 + k * 35)
        p0 = rot([(cx, cy - s * 0.04)], cx, cy, rot_)[0]
        p1 = rot([(cx + math.cos(a) * s * 0.66, cy - s * 0.04 + math.sin(a) * s * 0.5)], cx, cy, rot_)[0]
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="#A8D860" stroke-width="1.6"/>')
    return "".join(out)


@design("tacos-al-pastor")
def tacos_al_pastor():
    D = Doc2("mxtp")
    out = [sky(D, [(0, "#0E1838"), (0.6, "#1E2450"), (1, "#3A2440")], 701, 600, ["#2A3468", "#0A1028", "#4A3058"], 90, sop=(0.06, 0.16))]
    # the taquería: a white-tiled back wall glowing orange from the grill, the street dark around it
    out.append(f'<rect x="-10" y="150" width="620" height="290" fill="#F2E2CC"/>')
    tiles = "".join(f'<path d="M 0 0.5 L 22 0.5 M 0.5 0 L 0.5 22" stroke="#B8A890" stroke-width="1.2"/>' for _ in range(1))
    out.append(f'<rect x="-10" y="150" width="620" height="290" fill="{D.pattern(22, 22, tiles)}"/>')
    out.append(strokes(D.nid(), "M -10 150 L 610 150 L 610 440 L -10 440 Z", (-40, 150, 610, 440), ["#FFFFFF", "#C8A880"], 702, n=50, angle=-88, length=(20, 60), width=(2, 5), opacity=(0.08, 0.2)))
    out.append(f'<rect x="-10" y="150" width="620" height="290" fill="{D.rad([(0, "#FF8A2A", 0.45), (0.45, "#E85A1A", 0.25), (1, "#1A0E20", 0.75)], 0.5, 0.6, 0.62)}"/>')
    # the vertical gas grill behind the trompo
    out.append(painted(D, rect_pts(214, 206, 386, 436, 14, 703, 0.4), ("#6A6E78", "#3A3E48", "#1A1C22"), 703, sk=0.1, n=10, inkw=1.6, hi=0.2))
    for k in range(8):
        out.append(f'<path d="{hg.org_rect(228, 220 + k * 26, 144, 15, 704 + k, 0.4, 8, 3)}" fill="#FF5A14"/>')
        out.append(f'<path d="{hg.org_rect(240, 224 + k * 26, 120, 6, 714 + k, 0.4, 8, 2)}" fill="#FFD27A"/>')
    out.append(D.glow(300, 320, 190, "#FF7A2A", 0.6))
    out.append(trompo(D, 300, 236, 432, 170, 70, 705))
    # a bare bulb on a cord, swinging a little
    out.append(f'<path d="M 470 140 L 474 236" stroke="#1A1018" stroke-width="1.6"/>')
    out.append(D.glow(474, 246, 70, "#FFE0A0", 0.55))
    out.append(f'<path d="{blob(474, 246, 9, 11, 706, 0.05, 10)}" fill="#FFF6D0"/><path d="M 468 236 L 480 236 L 478 230 L 470 230 Z" fill="#3A3038"/>')
    # stainless counter
    out.append(painted(D, rect_pts(-10, 428, 610, 470, 30, 706, 0.4), ("#E8ECF2", "#A8B0BA", "#5A606A"), 706, sk=0.1, angle=0, n=30, inkw=1.4, hi=0.5))
    out.append(f'<rect x="-10" y="470" width="620" height="140" fill="{D.lin([(0, "#2A1E30"), (1, "#140E1A")])}"/>')
    out.append(f'<rect x="-10" y="470" width="620" height="16" fill="#E6337A" opacity="0.85"/>')
    for k in range(-1, 22):
        out.append(f'<path d="M {k * 30} 470 l 15 0 l 0 16 l -15 0 Z" fill="#FFFFFF" opacity="0.85"/>')
    # salsas and limes on the counter
    for k, (x, c) in enumerate(((96, ("#F07A5A", "#C0281A", "#6A0A06")), (504, ("#B8E07A", "#5EA03A", "#2A5A14")))):
        out.append(clay_pot(D, x, 452, 72, 34, 720 + k, BARRO, neck=0.98, lip=1.0, handles=False, deco=None, soot=False, inside=c[1]))
        out.append(specks(721 + k, (x - 28, 414, x + 28, 422), [c[2], c[0]], 14, (1, 2), (0.6, 1)))
    # the plate in front: three tacos and lime
    pcx, pcy = 300, 520
    out.append(cast(D, pcx + 12, pcy + 30, 200, 40, strength=0.5, seed=730))
    plate = ell_pts(pcx, pcy, 196, 70, 0, 360, 36)[:-1]
    out.append(painted(D, plate, ("#FFFFFF", "#F2EEE6", "#B8B0A8"), 731, sdir=(0.5, 1), sk=0.08, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(pcx, pcy - 2, 176, 58, 0, 360, 36)[:-1]), "#C8C0B8", 1.4, 732, 1, 0.6))
    for k in range(40):
        a = 2 * math.pi * k / 40
        out.append(f'<circle cx="{pcx + math.cos(a) * 187:.1f}" cy="{pcy + math.sin(a) * 64:.1f}" r="2.2" fill="#2E6AC8" opacity="0.7"/>')
    out.append(taco(D, 214, 516, 70, 733, -6))
    out.append(taco(D, 302, 506, 70, 734, 4))
    out.append(taco(D, 388, 518, 70, 735, 10))
    out.append(lime_wedge(D, 160, 558, 26, 736, -16))
    out.append(lime_wedge(D, 440, 558, 26, 737, 18))
    # string of bulbs under the sign
    lights = [(x, 168 + 14 * math.sin(x / 600 * math.pi)) for x in range(-20, 640, 20)]
    out.append(pline(lights, "#1A1018", 1.6, 738, 1, 1))
    for k, (x, y) in enumerate(lights[1::2]):
        out.append(D.glow(x, y + 8, 22, "#FFD070", 0.6))
        out.append(f'<path d="{blob(x, y + 8, 5, 6.5, 740 + k, 0.05, 8)}" fill="#FFF2B0"/>')
    # the sign board
    out.append(painted(D, rect_pts(56, 52, 544, 162, 30, 750, 0.6), ("#FFF2D0", "#F6D890", "#B8904A"), 750, sdir=(0.3, 1), sk=0.08, angle=0, n=50, inkw=2.4, hi=0.3))
    out.append(f'<path d="{hg.org_rect(66, 62, 468, 90, 751, 0.6, 20, 4)}" fill="none" stroke="#1E7A44" stroke-width="3"/>')
    for x in (74, 526):
        out.append(f'<circle cx="{x}" cy="70" r="3" fill="#5A3A1A"/><circle cx="{x}" cy="144" r="3" fill="#5A3A1A"/>')
    out.append(rotulo(D, 300, 120, "TACOS", ANTON, 64, "#D2352A", "#FFF6E0", "#2A1008", 752, ls=6, max_w=300))
    out.append(label(300, 146, "AL PASTOR · TAQUERÍA DE LA ESQUINA", JOS, 17, "#1E5A34", ls=2, max_w=430))
    for sg in (-1, 1):
        x = 300 + sg * 190
        for k in range(5):
            a = math.radians(k * 72 - 90)
            out.append(f'<path d="{blob(x + math.cos(a) * 9, 100 + math.sin(a) * 9, 7, 4.5, 753 + k + sg, 0.1, 8, k * 72 - 90)}" fill="#E6337A"/>')
        out.append(f'<circle cx="{x}" cy="100" r="4.5" fill="#F6C21C"/>')
    return finish_b(D, out, 759, "#FFFFFF", 0.5)


# ================================================================ 8. talavera — a talavera pot of geraniums against a sunlit pink wall
def geranium(D, cx, cy, r, seed, pal=CHILE):
    """A geranium head: a ball of five-petal florets with a few buds."""
    rnd = random.Random(seed)
    out = []
    for i in range(int(r * 0.7)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.82
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9
        lit = -(math.cos(a) * 0.6 + math.sin(a) * 0.8) * rr / r
        c = pal[0] if lit > 0.3 else (pal[2] if lit < -0.35 else pal[1])
        ps = r * 0.16
        for k in range(5):
            b = math.radians(k * 72 + rnd.uniform(0, 72))
            out.append(f'<path d="{blob(x + math.cos(b) * ps * 0.7, y + math.sin(b) * ps * 0.7, ps * 0.62, ps * 0.5, rnd.randint(0, 9999), 0.15, 8, math.degrees(b))}" fill="{c}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ps * 0.2:.1f}" fill="{dk(pal[2], 0.3)}" opacity="0.7"/>')
    return "".join(out)


def geranium_leaf(D, x, y, r, seed, pal=NOPAL):
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        rr = r * (1 + 0.12 * math.cos(a * 7))
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8))
    out = [painted(D, pts, pal, seed, sk=0.18, angle=-40, n=8, inkw=1.2, hi=0.35)]
    out.append(f'<path d="{blob(x, y, r * 0.6, r * 0.45, seed + 1, 0.15, 12)}" fill="none" stroke="{dk(pal[2], 0.2)}" stroke-width="{max(1.5, r * 0.14):.1f}" opacity="0.35"/>')
    for k in range(6):
        a = math.radians(k * 60)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * r * 0.8:.1f} {math.sin(a) * r * 0.64:.1f}" stroke="{pal[0]}" stroke-width="1" opacity="0.6"/>')
    return "".join(out)


def talavera_pot(D, cx, base, w, h, seed):
    """Talavera maceta: tin-white glaze, cobalt bands, a big painted flower with ochre and green, crackle of light."""
    top = base - h
    pts = [(cx - w * 0.56, top), (cx - w * 0.5, top + h * 0.12), (cx - w * 0.52, top + h * 0.4), (cx - w * 0.44, base - h * 0.1), (cx - w * 0.3, base),
           (cx + w * 0.3, base), (cx + w * 0.44, base - h * 0.1), (cx + w * 0.52, top + h * 0.4), (cx + w * 0.5, top + h * 0.12), (cx + w * 0.56, top)]
    d = smooth_closed(pts)
    out = [painted(D, pts, ("#FFFFFF", "#F8F2E4", "#C8BCA8"), seed, sdir=(0.9, 0.3), sk=0.16, angle=-90, n=30, inkw=2.2, hi=0.5, hik=0.06)]
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    B = COBALT
    # bands
    for y0, hh in ((top + h * 0.12, h * 0.07), (base - h * 0.16, h * 0.06)):
        inner.append(f'<path d="{hg.org_rect(cx - w, y0, w * 2, hh, seed + int(y0), 0.6, 14, 1)}" fill="{B[1]}"/>')
    for k in range(-6, 7):
        x = cx + k * w * 0.09
        inner.append(f'<path d="{blob(x, top + h * 0.24, w * 0.03, h * 0.035, seed + k, 0.15, 8)}" fill="#F2A41E"/>')
        inner.append(f'<path d="M {x + w * 0.045:.1f} {top + h * 0.2:.1f} q {w * 0.02:.1f} {h * 0.04:.1f} 0 {h * 0.08:.1f}" stroke="{B[1]}" stroke-width="2.2" fill="none"/>')
    # big central flower
    fx, fy = cx, top + h * 0.55
    R = h * 0.22
    for k in range(8):
        a = math.radians(k * 45 + 22)
        px, py = fx + math.cos(a) * R * 0.62, fy + math.sin(a) * R * 0.62
        p = rot(blob_pts(px, py, R * 0.5, R * 0.3, seed + 40 + k, 0.08, 12), px, py, k * 45 + 22)
        inner.append(f'<path d="{smooth_closed(p)}" fill="{B[1]}"/>')
        inner.append(f'<path d="{smooth_closed(rot(blob_pts(px + math.cos(a) * 2, py + math.sin(a) * 2, R * 0.26, R * 0.12, seed + 50 + k, 0.08, 10), px, py, k * 45 + 22))}" fill="{B[0]}" opacity="0.8"/>')
    inner.append(f'<path d="{blob(fx, fy, R * 0.34, R * 0.34, seed + 60, 0.08, 12)}" fill="#F2A41E"/>')
    inner.append(f'<path d="{blob(fx, fy, R * 0.16, R * 0.16, seed + 61, 0.08, 10)}" fill="#C8401E"/>')
    for sg in (-1, 1):
        lx = fx + sg * R * 1.6
        inner.append(leaf_simple(D, fx + sg * R * 0.9, fy + R * 0.5, R * 1.3, R * 0.32, 90 - sg * 70, ("#9AD07A", "#3E8A44", "#1E5A2A"), seed + 70 + sg, inkw=0))
        inner.append(f'<path d="{blob(lx, fy - R * 0.6, R * 0.22, R * 0.22, seed + 80 + sg, 0.1, 10)}" fill="{B[1]}"/>')
        inner.append(f'<path d="{blob(lx, fy - R * 0.6, R * 0.1, R * 0.1, seed + 82 + sg, 0.1, 8)}" fill="#F2A41E"/>')
        for j in range(5):
            inner.append(f'<circle cx="{lx + sg * R * 0.1 + math.cos(j) * R * 0.4:.1f}" cy="{fy + R * 0.4 + math.sin(j) * R * 0.3:.1f}" r="{R * 0.06:.1f}" fill="{B[1]}"/>')
    inner.append(strokes(D.nid(), d, (cx - w, top, cx + w, base), [B[0], "#FFFFFF"], seed + 90, n=40, angle=-80, length=(8, 24), width=(0.6, 1.6), opacity=(0.1, 0.25)))
    inner.append(shade_over(D, d, "#3A2A2A", 0.45, 0, 0, 1, 0, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - w * 0.38, top + h * 0.2), (cx - w * 0.44, top + h * 0.5), (cx - w * 0.36, base - h * 0.2)], 7, 2, "#FFFFFF", 0.7))
    # rim
    rim = ell_pts(cx, top, w * 0.56, h * 0.07, 0, 360, 24)[:-1]
    out.append(f'<path d="{smooth_closed(rim)}" fill="{B[1]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1, w * 0.5, h * 0.05, 0, 360, 24)[:-1])}" fill="#4A2A18"/>')
    out.append(ink(smooth_closed(rim), INK, 1.8, seed, 1, 0.7))
    return "".join(out)


@design("talavera")
def talavera():
    D = Doc2("mxtv")
    # two sunlit walls meeting: rosa mexicano on the left plane, warm yellow on the right, a hard diagonal shadow
    out = [painted(D, [(-10, -10), (360, -10), (360, 470), (-10, 470)], ("#FF8AB8", "#E6337A", "#9A1050"), 801, sk=0.0, angle=-88, n=120, inkw=0, hi=0)]
    out.append(painted(D, [(360, -10), (610, -10), (610, 470), (360, 470)], ("#FFE08A", "#F6B82A", "#B8760A"), 802, sk=0.0, angle=-88, n=80, inkw=0, hi=0))
    out.append(f'<path d="M 360 -10 L 610 -10 L 610 470 L 360 470 Z" fill="#7A3A0A" opacity="0.25"/>')
    out.append(f'<path d="M -10 -10 L 230 -10 L -10 300 Z" fill="#6A0A3A" opacity="0.22"/>')
    out.append(ink("M 360 -10 L 360 470", "#7A1A3A", 2, 803, 1, 0.5))
    # a niche window on the pink wall with light falling through
    # terracotta floor tiles in perspective
    floor = [(-10, 470), (610, 470), (610, 610), (-10, 610)]
    out.append(painted(D, floor, ("#E8A070", "#C0683A", "#7A3418"), 804, sk=0.0, angle=0, n=40, inkw=0, hi=0))
    for k in range(-8, 12):
        x0 = 300 + k * 60
        out.append(f'<path d="M {300 + k * 30:.1f} 470 L {x0 + (x0 - 300) * 0.6:.1f} 610" stroke="#8A4A24" stroke-width="2" opacity="0.6"/>')
    for y in (492, 522, 562):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#8A4A24" stroke-width="2" opacity="0.6"/>')
    out.append(f'<rect y="462" width="600" height="10" fill="#B83A6A" opacity="0.6"/>')
    # long cast shadow of the pot on the floor
    out.append(f'<path d="{blob(390, 548, 150, 26, 805, 0.08, 14, -6)}" fill="#3A1408" opacity="0.32"/>')
    # trailing ivy from the pot, geraniums, leaves
    cx, base, w, h = 290, 556, 250, 210
    for k in range(9):
        a = math.radians(-160 + k * 18)
        x, y = cx + math.cos(a) * 120, 340 + math.sin(a) * 90
        out.append(taper([(cx + (x - cx) * 0.3, 350), (x, y + 10)], 4, 2, "#3E6A2A"))
    for k, (x, y, r) in enumerate(((176, 318, 30), (226, 280, 32), (300, 300, 30), (376, 284, 30), (420, 326, 28), (150, 354, 26), (440, 360, 26), (262, 330, 26), (344, 336, 26))):
        out.append(geranium_leaf(D, x, y, r, 810 + k, NOPAL if k % 2 else ("#9ACB6A", "#4E8A34", "#24501A")))
    for k, (x, y, r, pal) in enumerate(((210, 220, 46, CHILE), (306, 200, 50, ("#FF9AB8", "#E6337A", "#9A1050")), (398, 226, 44, CHILE),
                                        (258, 250, 36, ("#FFB0A0", "#F2604A", "#A8281A")), (356, 256, 36, ("#FF9AB8", "#E6337A", "#9A1050")))):
        out.append(geranium(D, x, y, r, 820 + k, pal))
    for k, (x, y) in enumerate(((170, 270), (444, 268), (232, 168))):
        out.append(taper([(x, y + 30), (x + 4, y)], 2.4, 1.6, "#3E6A2A"))
        out.append(f'<path d="{blob(x + 4, y - 4, 6, 8, 830 + k, 0.1, 8)}" fill="{CHILE[1]}"/>')
    # ivy spilling over the rim
    for k, (sx, d_) in enumerate(((180, -1), (400, 1))):
        trail = catmull([(sx, 352), (sx + d_ * 20, 400), (sx + d_ * 10, 450), (sx + d_ * 30, 500)], 6)
        out.append(pline(trail, "#3E6A2A", 2.2, 840 + k, 1, 1))
        for j, (x, y) in enumerate(trail[2::4]):
            out.append(leaf_simple(D, x, y, 22, 8, 90 + d_ * 40 + (j % 2) * 60 - 30, NOPAL, 850 + k * 10 + j, vein=False, inkw=1))
    out.append(talavera_pot(D, cx, base, w, h, 860))
    for k, (sx, d_) in enumerate(((182, -1), (398, 1))):
        trail = catmull([(sx, 352), (sx + d_ * 14, 372), (sx + d_ * 22, 400)], 4)
        out.append(pline(trail, "#3E6A2A", 2, 870 + k, 1, 1))
        out.append(leaf_simple(D, sx + d_ * 18, 380, 24, 8, 90 + d_ * 30, NOPAL, 872 + k, vein=False, inkw=1))
    # a hummingbird visiting
    # lettering on the walls
    out.append(letters(D, 300, 116, "talavera", SERIF_IT, 96, "#FFFFFF", ["#FFFFFF", "#FFE2EE", "#FFF4D8"], 880, max_w=420,
                       shadow="#7A0A3A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 154, "HECHA A MANO EN PUEBLA", "#FFF4E0", font=JOS, size=19, ls=5, line_w=30, gap=12))
    return finish_b(D, out, 881)


# ================================================================ 9. colibrí — a naturalist's plate
def hummingbird(D, ox, oy, s, seed):
    """Broad-billed hummingbird hovering, facing left: emerald back, sapphire throat, coral bill tipped black,
    wings raised in a blur. (ox, oy) = the centre of the body; s = scale (1 ~ 200 px long)."""
    rnd = random.Random(seed)

    def P(x, y):
        return (ox + x * s, oy + y * s)

    out = []
    # far wing (behind), blurred
    fw = [P(10, -10), P(26, -44), P(48, -76), P(66, -86), P(64, -66), P(48, -30), P(30, -4)]
    out.append(f'<path d="{smooth_closed(fw)}" fill="#6A7A8A" opacity="0.35"/>')
    # tail
    tail = [P(40, 12), P(80, 30), P(110, 52), P(104, 60), P(84, 54), P(96, 70), P(86, 74), P(60, 52), P(36, 26)]
    out.append(painted(D, tail, ("#4A6A6A", "#1E3A3A", "#0A1A1A"), seed, sdir=(0.5, 0.8), sk=0.2, angle=30, n=10, inkw=1.4, hi=0.3))
    for k in range(4):
        out.append(f'<path d="M {P(48, 22)[0]:.1f} {P(48, 22)[1]:.1f} L {P(100 - k * 4, 54 + k * 5)[0]:.1f} {P(100 - k * 4, 54 + k * 5)[1]:.1f}" stroke="#0A1A1A" stroke-width="1" opacity="0.6"/>')
    # body
    body = [P(-40, -10), P(-30, -26), P(-6, -30), P(22, -22), P(44, -4), P(52, 14), P(36, 28), P(10, 30), P(-18, 22), P(-36, 8)]
    out.append(painted(D, body, ("#8AE0A0", "#1E9A5A", "#0A4A2A"), seed + 1, sdir=(0.5, 0.8), sk=0.2, angle=10, n=30, inkw=1.8, hi=0.4))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = []
    for _ in range(70):
        x, y = rnd.uniform(-40, 50), rnd.uniform(-30, 30)
        inner.append(f'<path d="{blob(*P(x, y), 3.2 * s, 2.2 * s, rnd.randint(0, 999), 0.2, 6, 20)}" fill="{rnd.choice(["#4ACB8A", "#2AAA6A", "#0E6A3A", "#9AF0B8", "#1E8A8A"])}" opacity="0.7"/>')
    # belly greyer, undertail white
    inner.append(f'<path d="{blob(*P(10, 24), 30 * s, 10 * s, seed, 0.1, 10)}" fill="#3A6A5A" opacity="0.5"/>')
    inner.append(shade_over(D, bd, "#041A10", 0.4, 0, 0, 0.4, 1, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{blob(*P(42, 24), 8 * s, 5 * s, seed + 2, 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    # head and throat
    head = blob_pts(*P(-38, -14), 20 * s, 18 * s, seed + 3, 0.04, 14)
    out.append(painted(D, head, ("#7AD0A0", "#1E8A5A", "#0A3A24"), seed + 3, sdir=(0.5, 0.8), sk=0.2, n=12, inkw=1.6, hi=0.4))
    gor = [P(-54, -8), P(-42, -2), P(-24, 2), P(-14, 10), P(-22, 18), P(-42, 12), P(-54, 2)]
    out.append(painted(D, gor, ("#8AB0FF", "#2A4ADA", "#101E7A"), seed + 4, sdir=(0.5, 0.8), sk=0.2, n=8, inkw=1.2, hi=0.5, hik=0.12))
    out.append(f'<path d="{blob(*P(-40, 2), 6 * s, 3 * s, seed + 5, 0.2, 8, -10)}" fill="#C8D8FF" opacity="0.8"/>')
    # eye with a white post-ocular spot, bill
    ex, ey = P(-44, -18)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4 * s:.1f}" fill="#0A0A0A"/><circle cx="{ex - 1.2 * s:.1f}" cy="{ey - 1.2 * s:.1f}" r="{1.3 * s:.1f}" fill="#FFFFFF"/>')
    out.append(f'<path d="{blob(*P(-34, -20), 3 * s, 1.8 * s, seed + 6, 0.2, 6)}" fill="#FFFFFF" opacity="0.9"/>')
    bill = [P(-56, -18), P(-110, -10), P(-112, -7), P(-56, -10)]
    out.append(f'<path d="{smooth_closed(bill)}" fill="#E8503A"/>')
    out.append(f'<path d="{pd([P(-88, -13), P(-112, -9), P(-111, -7), P(-88, -10)])}" fill="#1A0A06"/>')
    out.append(ink(smooth_closed(bill), "#5A1A0A", 1.2, seed + 7, 1, 0.8))
    # near wing raised, feathers fanned, a motion blur
    nw = [P(-4, -22), P(-14, -52), P(-8, -84), P(8, -102), P(20, -98), P(18, -70), P(16, -40), P(12, -18)]
    for k in range(3):
        out.append(f'<path d="{smooth_closed([(x + (k + 1) * 5 * s, y + (k + 1) * 5 * s) for x, y in nw])}" fill="#B8D0D8" opacity="{0.3 - k * 0.08:.2f}"/>')
    out.append('<g opacity="0.82">' + painted(D, nw, ("#D0E2E8", "#7A9AA6", "#3A4E58"), seed + 8, sdir=(0.5, 0.6), sk=0.15, angle=-75, n=14, inkw=1.3, hi=0.5) + '</g>')
    for k in range(6):
        t = k / 5
        a = P(4 + t * 8, -24 - t * 4)
        b = P(-8 + t * 26, -86 - t * 14)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2E3E48" stroke-width="1" opacity="0.5"/>')
    for k in range(3):
        out.append(f'<path d="M {P(30 + k * 6, -100 + k * 10)[0]:.1f} {P(30 + k * 6, -100 + k * 10)[1]:.1f} q {8 * s:.1f} {6 * s:.1f} {10 * s:.1f} {16 * s:.1f}" stroke="#7A9AA6" stroke-width="1.4" fill="none" opacity="0.5"/>')
    return "".join(out)


def fuchsia(D, x, y, s, seed, ang=0):
    """Hanging tubular flower (aretillo): coral sepals flared back, purple skirt, long stamens."""
    out = [f'<g transform="rotate({ang:.1f} {x:.1f} {y:.1f})">']
    out.append(taper([(x, y - s * 0.6), (x, y)], 2, 2, "#5A3A2A"))
    out.append(painted(D, [(x - s * 0.12, y), (x + s * 0.12, y), (x + s * 0.08, y + s * 0.5), (x - s * 0.08, y + s * 0.5)], CHILE, seed, sk=0.2, n=3, inkw=1, hi=0.4))
    for sg in (-1, 1):
        out.append(painted(D, [(x, y + s * 0.45), (x + sg * s * 0.5, y + s * 0.3), (x + sg * s * 0.62, y + s * 0.18), (x + sg * s * 0.3, y + s * 0.52)], CHILE, seed + sg, sk=0.2, n=3, inkw=1, hi=0.4))
    out.append(painted(D, [(x - s * 0.22, y + s * 0.5), (x + s * 0.22, y + s * 0.5), (x + s * 0.28, y + s * 0.85), (x + s * 0.1, y + s * 0.92), (x - s * 0.1, y + s * 0.92), (x - s * 0.28, y + s * 0.85)], MORADO, seed + 4, sk=0.2, n=4, inkw=1, hi=0.4))
    for k in (-1, 0, 1):
        out.append(f'<path d="M {x + k * 3:.1f} {y + s * 0.9:.1f} l {k * 2:.1f} {s * 0.35:.1f}" stroke="#C8304A" stroke-width="1.2"/><circle cx="{x + k * 3 + k * 2:.1f}" cy="{y + s * 1.26:.1f}" r="1.8" fill="#F6E07A"/>')
    out.append("</g>")
    return "".join(out)


@design("colibri")
def colibri():
    D = Doc2("mxcb")
    out = [paper(D.nid(), "#F4ECDA", FLECK, 901)]
    out.append(blooms(902, ["#F2C8D8", "#C8E2D2", "#F8E0B0"], 7, (90, 100, 510, 470), (110, 180), (0.12, 0.2)))
    # plate frame with talavera-blue corners
    out.append(f'<rect x="48" y="48" width="504" height="504" fill="none" stroke="#1E3F9A" stroke-width="2.4"/>')
    out.append(f'<rect x="56" y="56" width="488" height="488" fill="none" stroke="#1E3F9A" stroke-width="1.2" opacity="0.7"/>')
    for x, y in ((48, 48), (552, 48), (48, 552), (552, 552)):
        out.append(f'<path d="{blob(x, y, 9, 9, x + y, 0.1, 8)}" fill="#E6337A"/><circle cx="{x}" cy="{y}" r="3" fill="#FFF4E0"/>')
    out.append(ruled(300, 92, "AVES DE MÉXICO · Nº 3", "#1E3F9A", font=MONO, size=16, ls=4, line_w=26, gap=10))
    # flowering branch arching from the right
    br = catmull([(560, 210), (500, 236), (440, 250), (380, 262), (330, 290), (300, 330)], 5)
    out.append(branch(D, br, 9, 3, 903))
    for k, (x, y, L, a) in enumerate(((520, 226, 70, -120), (470, 246, 60, -60), (420, 256, 64, 160), (380, 264, 56, -110), (340, 284, 50, 120), (500, 236, 56, 60))):
        out.append(leaf_simple(D, x, y, L, 16, a, ("#9ACB7A", "#3E8A44", "#1E5A2A"), 904 + k, inkw=1.1))
    for k, (x, y, a) in enumerate(((456, 254, 8), (404, 262, -6), (352, 280, 12), (306, 328, -10), (490, 240, 0))):
        out.append(fuchsia(D, x, y, 46, 910 + k, a))
    # the hummingbird, hovering at the lowest flower
    out.append(hummingbird(D, 240, 340, 1.4, 920))
    # a second, smaller, far off
    out.append(hummingbird(D, 140, 196, 0.42, 921))
    # caption
    out.append(letters(D, 300, 498, "Colibrí", SERIF_IT, 70, "#1E5A3A", ["#2E7A4A", "#0E3A22"], 922, max_w=320, angle=-40, wob=0.6))
    out.append(label(300, 528, "CYNANTHUS LATIROSTRIS", MONO, 16, "#A8281A", ls=4))
    return finish_b(D, out, 923)


# ================================================================ 10. mi familia — an Otomí-style embroidered cloth
def satin(D, d, box, col, seed, angle=60, gap=2.6, w=2.0, outline=True):
    """Satin stitch: a shape filled with close parallel stitches, each thread catching the light a little differently."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + 4
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    cid = D.clip(f'<path d="{d}"/>')
    lines = []
    k = -R
    while k < R:
        px, py = cx + nx * k, cy + ny * k
        c = rnd.choice([col, col, lt(col, 0.22), dk(col, 0.12)])
        lines.append(f'<path d="M {px - ux * R:.1f} {py - uy * R:.1f} L {px + ux * R:.1f} {py + uy * R:.1f}" stroke="{c}" stroke-width="{w + rnd.uniform(-0.3, 0.3):.1f}"/>')
        lines.append(f'<path d="M {px - ux * R:.1f} {py - uy * R - 0.6:.1f} L {px + ux * R:.1f} {py + uy * R - 0.6:.1f}" stroke="#FFFFFF" stroke-width="0.5" opacity="0.25"/>')
        k += gap
    out = [f'<path d="{d}" fill="{dk(col, 0.25)}"/>', f'<g {cid}>{"".join(lines)}</g>']
    if outline:
        out.append(f'<path d="{d}" fill="none" stroke="{dk(col, 0.3)}" stroke-width="1.2" stroke-dasharray="2.2 1.2" opacity="0.7"/>')
    return "".join(out)


def otomi_bird(cx, cy, s, flip=1, chick=False):
    """Folk bird silhouette (big tail up, plump chest, crest) — Otomí tenango style."""
    pts = [(0, -0.5), (0.2, -0.62), (0.34, -0.55), (0.46, -0.48), (0.38, -0.36), (0.3, -0.18), (0.18, 0.2), (-0.1, 0.4), (-0.4, 0.38),
           (-0.62, 0.2), (-0.9, -0.2), (-1.05, -0.62), (-0.8, -0.5), (-0.62, -0.32), (-0.4, -0.18), (-0.18, -0.24), (-0.06, -0.42)]
    if chick:
        pts = [(0, -0.4), (0.26, -0.46), (0.4, -0.36), (0.3, -0.16), (0.3, 0.12), (0.08, 0.36), (-0.28, 0.36), (-0.5, 0.12), (-0.62, -0.12), (-0.42, -0.08), (-0.16, -0.2)]
    return [(cx + flip * x * s, cy + y * s) for x, y in pts]


def otomi_deer(cx, cy, s, flip=1):
    pts = [(0.8, -0.6), (0.64, -0.54), (0.5, -0.4), (0.42, -0.18), (0.62, 0.0), (0.86, 0.2), (0.82, 0.26), (0.56, 0.12), (0.34, 0.06), (-0.2, 0.08),
           (-0.44, 0.2), (-0.74, 0.4), (-0.78, 0.35), (-0.52, 0.12), (-0.58, -0.06), (-0.7, -0.18), (-0.52, -0.18), (-0.2, -0.22), (0.28, -0.3),
           (0.44, -0.56), (0.42, -0.78), (0.54, -0.68), (0.66, -0.7)]
    return [(cx + flip * x * s, cy + y * s) for x, y in pts]


def otomi_flower(D, cx, cy, r, col, seed, petals_n=8, center=None):
    out = []
    for k in range(petals_n):
        a = 2 * math.pi * k / petals_n
        px, py = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62
        p = rot(blob_pts(px, py, r * 0.42, r * 0.22, seed + k, 0.05, 12), px, py, math.degrees(a))
        out.append(satin(D, smooth_closed(p), bbox(p), col, seed + k, angle=math.degrees(a) + 90, gap=2.4, w=1.8))
    c = blob_pts(cx, cy, r * 0.3, r * 0.3, seed + 20, 0.05, 12)
    out.append(satin(D, smooth_closed(c), bbox(c), center or col, seed + 21, angle=20, gap=2.4, w=1.8))
    return "".join(out)


@design("mi-familia")
def mi_familia():
    D = Doc2("mxmf")
    # white manta cotton: weave texture
    out = [f'<rect width="600" height="600" fill="#FBF7EE"/>']
    weave = "".join(f'<path d="M 0 {y} L 8 {y}" stroke="#D8CDB8" stroke-width="0.8" opacity="0.5"/>' for y in (2, 6)) + "".join(f'<path d="M {x} 0 L {x} 8" stroke="#E8DECC" stroke-width="0.8" opacity="0.5"/>' for x in (2, 6))
    out.append(f'<rect width="600" height="600" fill="{D.pattern(8, 8, weave)}"/>')
    out.append(blooms(1001, ["#E8DEC8", "#F4ECDC"], 6, (0, 0, 600, 600), (120, 200), (0.2, 0.3)))
    # the motifs: a central tree of life, papá and mamá birds, three chicks, a deer, flowers and sprigs
    cols = {"rosa": "#E6337A", "turq": "#18A0A0", "nar": "#F5861E", "mor": "#7A42B8", "verde": "#2E9A4C", "azul": "#2E5AC8", "amar": "#F2B81C"}
    # tree of life: trunk and branches as stem stitches with satin leaves
    trunk = catmull([(300, 500), (296, 440), (302, 380), (300, 336)], 5)
    out.append(taper(trunk, 12, 7, "#2E9A4C"))
    for k in range(12):
        t = k / 11
        x, y = trunk[int(t * (len(trunk) - 1))]
        out.append(f'<path d="M {x - 5:.1f} {y:.1f} l 10 -3" stroke="#7ACB7A" stroke-width="1" opacity="0.7"/>')
    for sg in (-1, 1):
        br = catmull([(300, 420), (300 + sg * 40, 400), (300 + sg * 70, 362), (300 + sg * 76, 326)], 5)
        out.append(taper(br, 7, 3, "#2E9A4C"))
        for j, (x, y) in enumerate(br[3::4]):
            lf = leaf_shape_pts(x, y, 30, (-90 + sg * 60) + j * sg * 20)
            out.append(satin(D, smooth_closed(lf), bbox(lf), cols["verde"], 1010 + j + sg * 7, angle=(-90 + sg * 60) + 90, gap=2.4, w=1.8))
    out.append(otomi_flower(D, 300, 326, 30, cols["rosa"], 1020, 8, cols["amar"]))
    out.append(otomi_flower(D, 222, 322, 20, cols["nar"], 1030, 6, cols["mor"]))
    out.append(otomi_flower(D, 378, 322, 20, cols["turq"], 1040, 6, cols["rosa"]))
    for k, (x, y, col) in enumerate(((150, 540, cols["amar"]), (450, 540, cols["verde"]), (236, 560, cols["azul"]), (364, 560, cols["nar"]))):
        out.append(otomi_flower(D, x, y, 12, col, 1045 + k * 3, 6, cols["rosa"]))
    # papá and mamá birds facing each other
    for sg, col, sd in ((-1, cols["azul"], 1050), (1, cols["rosa"], 1060)):
        bp = otomi_bird(300 + sg * 138, 446, 100, flip=-sg)
        out.append(satin(D, smooth_closed(bp), bbox(bp), col, sd, angle=sg * 35 + 90, gap=2.6, w=2.0))
        wing = [(300 + sg * 138 + (-sg) * x * 100, 446 + y * 100) for x, y in ((-0.1, -0.16), (-0.5, -0.12), (-0.6, 0.02), (-0.3, 0.14), (0.0, 0.08))]
        out.append(satin(D, smooth_closed(wing), bbox(wing), cols["amar"] if sg < 0 else cols["turq"], sd + 1, angle=-sg * 30, gap=2.4, w=1.8))
        ex, ey = 300 + sg * 138 - sg * 0.22 * 100, 446 - 0.46 * 100
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="#FBF7EE"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.6" fill="#2A1A10"/>')
    # three chicks between them
    for k, (x, col) in enumerate(((256, cols["nar"]), (300, cols["mor"]), (344, cols["turq"]))):
        cp = otomi_bird(x, 516, 34, flip=1 if k == 0 else (-1 if k == 2 else 1), chick=True)
        out.append(satin(D, smooth_closed(cp), bbox(cp), col, 1070 + k, angle=60, gap=2.2, w=1.6))
        out.append(f'<circle cx="{x + (1 if k != 2 else -1) * 7:.1f}" cy="{516 - 10:.1f}" r="2.2" fill="#FBF7EE"/>')
    # ground line in running stitch
    out.append(f'<path d="M 130 544 Q 300 532 470 544" stroke="#2E9A4C" stroke-width="2.4" fill="none" stroke-dasharray="7 4"/>')
    # corner flowers and little rabbits
    for k, (x, y, col, c2) in enumerate(((92, 96, cols["turq"], cols["nar"]), (508, 96, cols["nar"], cols["mor"]), (88, 520, cols["mor"], cols["amar"]), (512, 520, cols["rosa"], cols["turq"]))):
        out.append(otomi_flower(D, x, y, 24, col, 1080 + k * 10, 8, c2))
    for sg in (-1, 1):
        dp = otomi_deer(300 + sg * 190, 312, 60, flip=-sg)
        out.append(satin(D, smooth_closed(dp), bbox(dp), cols["nar"] if sg < 0 else cols["azul"], 1120 + sg, angle=sg * 20, gap=2.4, w=1.8))
        ax, ay = 300 + sg * 190 - sg * 0.6 * 60, 312 - 0.7 * 60
        out.append(pline([(ax, ay), (ax - sg * 4, ay - 14), (ax - sg * 2, ay - 28)], "#7A4A2A", 2.4, 1125, 1, 1))
        for j, (tx, ty) in enumerate(((-4, -10), (-3, -20))):
            out.append(pline([(ax - sg * 4 + j, ay + ty + 4), (ax - sg * (12 + j * 2), ay + ty - 4)], "#7A4A2A", 2.2, 1126 + j, 1, 1))
        out.append(pline([(ax + sg * 2, ay - 4), (ax + sg * 10, ay - 18), (ax + sg * 8, ay - 28)], "#7A4A2A", 2.4, 1128, 1, 1))
    # stitched lettering
    T = '<text x="300" y="196" text-anchor="middle" ' + SERIF_IT + f' font-size="{fit_size("mi familia", SERIF_IT, 112, 420)}">mi familia</text>'
    cid = D.clip(T)
    rnd = random.Random(1130)
    st = []
    for i in range(240):
        x = 70 + i * 2.0
        c = rnd.choice(["#C8205A", "#E6337A", "#F05A90"])
        st.append(f'<path d="M {x:.1f} 70 L {x + 60:.1f} 220" stroke="{c}" stroke-width="1.9"/>')
    out.append(T.replace("<text", '<text fill="#9A1050" transform="translate(1.5 2)"'))
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(T.replace("<text", '<text fill="none" stroke="#7A0A3A" stroke-width="1" stroke-dasharray="2 1.4" opacity="0.6"'))
    out.append(ruled(300, 244, "HECHO CON AMOR, PUNTADA A PUNTADA", "#2E5AC8", font=JOS, size=16, ls=1.5, line_w=14, gap=8, max_w=440))
    # a little embroidery needle with its pink thread, tucked between the chicks and the corner
    out.append(f'<path d="M 404 584 L 486 566" stroke="#8A8E98" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<ellipse cx="480" cy="567" rx="3" ry="1.1" fill="#FBF7EE" transform="rotate(-12 480 567)"/>')
    out.append(pline(catmull([(480, 567), (500, 574), (492, 590), (470, 586)], 4), "#E6337A", 1.8, 1131, 1, 1))
    return finish_b(D, out, 1132, "#8A6A4A", 0.6)


def leaf_shape_pts(x, y, L, ang, w=0.36):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(9):
        t = i / 8
        ww = L * w * math.sin(math.pi * t) ** 0.9 * 0.5
        px, py = x + ux * L * t, y + uy * L * t
        right.append((px + nx * ww, py + ny * ww))
        left.append((px - nx * ww, py - ny * ww))
    return right + left[::-1][1:-1]


# ================================================================ 11. noche de tamales — Christmas Eve, the steamer and the window
def husk(D, cx, cy, w, h, seed, rot_=0, open_=False, filling="rojo"):
    """A tamal in its corn husk: pale straw husk with fine veins; open shows the masa and the chile-red filling."""
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">']
    out.append(cast(D, cx + 4, cy + h * 0.45, w * 0.7, h * 0.12, strength=0.35, seed=seed))
    H = ("#FFF2C8", "#EED79A", "#B89A5A")
    if open_:
        hp = [(cx - w * 0.75, cy - h * 0.3), (cx - w * 0.3, cy - h * 0.62), (cx, cy - h * 0.72), (cx + w * 0.3, cy - h * 0.62), (cx + w * 0.75, cy - h * 0.3),
              (cx + w * 0.6, cy + h * 0.3), (cx + w * 0.15, cy + h * 0.55), (cx, cy + h * 0.68), (cx - w * 0.15, cy + h * 0.55), (cx - w * 0.6, cy + h * 0.3)]
    else:
        hp = [(cx - w * 0.5, cy - h * 0.3), (cx - w * 0.2, cy - h * 0.5), (cx + w * 0.2, cy - h * 0.5), (cx + w * 0.5, cy - h * 0.3), (cx + w * 0.42, cy + h * 0.3),
              (cx + w * 0.12, cy + h * 0.6), (cx, cy + h * 0.72), (cx - w * 0.12, cy + h * 0.6), (cx - w * 0.42, cy + h * 0.3)]
    d = smooth_closed(hp)
    out.append(painted(D, hp, H, seed, sdir=(0.7, 0.5), sk=0.15, angle=-90, n=14, inkw=1.4, hi=0.4))
    cid = D.clip(f'<path d="{d}"/>')
    vv = []
    for k in range(-8, 9):
        x = cx + k * w * 0.09
        vv.append(f'<path d="M {x:.1f} {cy - h:.1f} Q {x - k * 1.4:.1f} {cy:.1f} {cx + k * w * 0.02:.1f} {cy + h * 0.75:.1f}" stroke="{H[2]}" stroke-width="1" fill="none" opacity="0.55"/>')
    out.append(f'<g {cid}>{"".join(vv)}</g>')
    if open_:
        m = [(cx - w * 0.42, cy - h * 0.34), (cx + w * 0.42, cy - h * 0.34), (cx + w * 0.44, cy + h * 0.26), (cx - w * 0.44, cy + h * 0.26)]
        out.append(painted(D, m, ("#FFF8DC", "#F4E2A8", "#C8A868"), seed + 1, sdir=(0.6, 0.8), sk=0.15, angle=-20, n=10, inkw=1.2, hi=0.5))
        out.append(f'<path d="{blob(cx, cy - h * 0.04, w * 0.24, h * 0.16, seed + 2, 0.15, 12)}" fill="{CHILE[1] if filling == "rojo" else "#4E9A3A"}" opacity="0.92"/>')
        out.append(specks(seed + 3, (cx - w * 0.2, cy - h * 0.16, cx + w * 0.2, cy + h * 0.08), ["#7A1010", "#F4907A", "#FFE2B0"], 16, (1, 2.4), (0.6, 1)))
        out.append(f'<path d="{blob(cx - w * 0.2, cy - h * 0.25, w * 0.12, h * 0.04, seed + 4, 0.2, 8)}" fill="#FFFFFF" opacity="0.6"/>')
    else:
        out.append(f'<path d="M {cx - w * 0.44:.1f} {cy + h * 0.1:.1f} Q {cx:.1f} {cy + h * 0.2:.1f} {cx + w * 0.44:.1f} {cy + h * 0.1:.1f}" stroke="#C8A868" stroke-width="5" fill="none"/>')
        out.append(f'<path d="M {cx - w * 0.44:.1f} {cy + h * 0.1:.1f} Q {cx:.1f} {cy + h * 0.2:.1f} {cx + w * 0.44:.1f} {cy + h * 0.1:.1f}" stroke="#FFF4D0" stroke-width="1.6" fill="none"/>')
    out.append("</g>")
    return "".join(out)


def poinsettia(D, cx, cy, r, seed, pal=CHILE):
    out = []
    for layer, (rr, n, off) in enumerate(((1.0, 6, 0), (0.7, 6, 30), (0.42, 5, 12))):
        for k in range(n):
            a = math.radians(k * 360 / n + off - 90)
            L = r * rr
            out.append(leaf_simple(D, cx, cy, L, L * 0.26, math.degrees(a), pal if layer < 2 else (lt(pal[0], 0.2), pal[0], pal[1]), seed + layer * 10 + k, vein=True, inkw=1.1, inkc=dk(pal[2], 0.3)))
    for k in range(7):
        a = math.radians(k * 51)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.08:.1f}" cy="{cy + math.sin(a) * r * 0.08:.1f}" r="{max(2, r * 0.05):.1f}" fill="#F2C640" stroke="#4A7A1A" stroke-width="1.2"/>')
    return "".join(out)


@design("noche-de-tamales")
def noche_de_tamales():
    D = Doc2("mxnt")
    # kitchen wall, deep green, warm lamplight
    out = [sky(D, [(0, "#1E4A3A"), (1, "#123426")], 1101, 600, ["#2E6A50", "#0A2418", "#3A7A5A"], 110, angle=-84, sop=(0.06, 0.18))]
    out.append(soft_glow(D, 300, 330, 320, "#FFC870", 0.42))
    # window with the Christmas night outside
    wx0, wy0, wx1, wy1 = 360, 66, 540, 270
    out.append(painted(D, rect_pts(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14, 20, 1102, 0.5), ("#FFF2D8", "#E8D2B0", "#A88A60"), 1102, sk=0.12, n=20, inkw=1.8, hi=0.3))
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#0E1440"), (1, "#3A3A7A")])}"/>')
    rnd = random.Random(1103)
    for _ in range(26):
        out.append(f'<circle cx="{rnd.uniform(wx0 + 4, wx1 - 4):.1f}" cy="{rnd.uniform(wy0 + 4, wy1 - 70):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append(sparkle(410, 96, 9, "#FFF6C8"))
    # neighbours' houses with lights
    for k, (x, w, h, c) in enumerate(((356, 50, 50, "#E8A0B8"), (404, 46, 66, "#F2C870"), (448, 56, 46, "#8AC8E0"), (500, 48, 60, "#F0A070"))):
        out.append(f'<path d="{hg.org_rect(x, wy1 - h, w, h, 1104 + k, 0.4, 8, 2)}" fill="{mix(c, "#2A2A5A", 0.45)}"/>')
        out.append(f'<rect x="{x + w * 0.3:.1f}" y="{wy1 - h * 0.7:.1f}" width="9" height="10" fill="#FFD070"/>')
    lights = [(x, wy1 - 72 + 6 * math.sin(x / 20)) for x in range(wx0, wx1 + 1, 12)]
    for k, (x, y) in enumerate(lights):
        out.append(f'<circle cx="{x}" cy="{y:.1f}" r="2.6" fill="{FIESTA[k % len(FIESTA)]}"/>')
    out.append(f'<path d="M {(wx0 + wx1) / 2} {wy0} L {(wx0 + wx1) / 2} {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#E8D2B0" stroke-width="7"/>')
    # papel picado garland across the window top, in Christmas colours
    specs = [(c, m, None) for c, m in ((CHILE[1], "sun"), ("#2E9A4C", "flower"), (AMAR[1], "heart"), (CHILE[1], "flower"), ("#FFFFFF", "sun"))]
    out.append(papel_string(D, 330, 54, 570, 54, 14, specs, 1105, 42, 46, rope="#E8D2B0", shadow="#0A1A10"))
    # tablecloth with embroidered border
    out.append(painted(D, [(-10, 430), (610, 430), (610, 610), (-10, 610)], ("#FFF8EC", "#F4E8D4", "#C8B494"), 1106, sk=0.06, angle=0, n=40, inkw=0, hi=0.2))
    for k in range(-1, 21):
        x = k * 32
        out.append(f'<path d="M {x} 440 l 8 -6 l 8 6 l 8 -6 l 8 6" stroke="{CHILE[1] if k % 2 else "#2E9A4C"}" stroke-width="2.4" fill="none"/>')
    # the vaporera (big steamer pot) in the back left, tamales standing inside
    vx, vb, vt, vw = 168, 478, 346, 104
    out.append(cast(D, vx + 14, vb, vw + 24, 14, strength=0.5, seed=1107))
    for k in range(5):
        out.append(husk(D, vx - 64 + k * 32, vt - 14 - (k % 2) * 10, 36, 96, 1110 + k, rot_=180 + (k - 2) * 7))
    pot = [(vx - vw, vt), (vx + vw, vt), (vx + vw - 6, vb - 6), (vx + vw - 16, vb), (vx - vw + 16, vb), (vx - vw + 6, vb - 6)]
    out.append(painted(D, pot, ("#F2F4F8", "#B8C0CA", "#5A626E"), 1108, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=50, inkw=2, hi=0.5, hik=0.06))
    pd_ = smooth_closed(pot)
    cid = D.clip(f'<path d="{pd_}"/>')
    out.append(f'<g {cid}>' + "".join(f'<path d="M {vx - vw - 4} {y} Q {vx} {y + 8} {vx + vw + 4} {y}" stroke="#8A929E" stroke-width="2.4" fill="none" opacity="0.55"/>' for y in (vt + 26, vb - 30)) + "</g>")
    out.append(taper([(vx - vw + 16, vt + 12), (vx - vw + 12, (vt + vb) / 2), (vx - vw + 18, vb - 16)], 8, 2, "#FFFFFF", 0.75))
    out.append(f'<path d="{smooth_closed(ell_pts(vx, vt, vw, 11, 0, 180, 16) + ell_pts(vx, vt, vw - 6, 7, 180, 0, 16))}" fill="#8A929E"/>')
    out.append(ink(smooth_open(ell_pts(vx, vt, vw, 11, 0, 180, 16)), "#3A424E", 1.8, 1111, 1, 0.8))
    for sg in (-1, 1):
        out.append(f'<path d="M {vx + sg * (vw - 2)} {vt + 22} q {sg * 22} 0 {sg * 22} 14 q 0 10 {-sg * 20} 10" stroke="#4A525E" stroke-width="5" fill="none"/>')
    out.append(steam(vx, vt - 70, 46, 1109, "#FFFFFF", 3, 40, 7, 0.4))
    # the plate in front: two open tamales and one wrapped, salsa verde
    pcx, pcy = 360, 520
    out.append(cast(D, pcx + 10, pcy + 24, 190, 40, strength=0.45, seed=1120))
    plate = ell_pts(pcx, pcy, 180, 60, 0, 360, 36)[:-1]
    out.append(painted(D, plate, ("#FFFFFF", "#F2EEE6", "#B8B0A8"), 1121, sdir=(0.5, 1), sk=0.08, angle=0, n=30, inkw=1.6, hi=0.4))
    for k in range(48):
        a = 2 * math.pi * k / 48
        out.append(f'<path d="{blob(pcx + math.cos(a) * 168, pcy + math.sin(a) * 55, 4, 2.4, 1122 + k, 0.2, 6, math.degrees(a) + 90)}" fill="{CHILE[1] if k % 2 else "#2E9A4C"}" opacity="0.85"/>')
    out.append(husk(D, 304, 516, 58, 128, 1123, rot_=-80, open_=True))
    out.append(husk(D, 418, 512, 58, 128, 1124, rot_=-100, open_=True, filling="verde"))
    out.append(steam(360, 470, 50, 1125, "#FFFFFF", 3, 30, 6, 0.5))
    # champurrado jarrito
    out.append(jarrito(D, 92, 568, 92, 1126, drink="#6A3A20"))
    out.append(steam(88, 466, 44, 1127, "#FFFFFF", 2, 18, 5, 0.55))
    # nochebuena in a clay pot on the sill
    out.append(clay_pot(D, 538, 446, 70, 50, 1128, BARRO, neck=0.95, lip=1.0, handles=False, soot=False, deco="#FFF2DC"))
    out.append(poinsettia(D, 538, 380, 48, 1129))
    # lettering
    out.append(letters(D, 200, 116, "noche de", SERIF_IT, 64, "#FFE6B0", ["#FFF2D0", "#F2C878"], 1130, max_w=250,
                       shadow="#0A1A10", soff=(0.02, 0.04), angle=-40, wob=0.6))
    out.append(letters(D, 200, 198, "tamales", SERIF_IT, 96, "#FFC24A", ["#FFE08A", "#F59A1E", "#FFF2C0"], 1131, max_w=270,
                       shadow="#0A1A10", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(200, 238, "NOCHEBUENA EN FAMILIA", "#F4E8D0", font=JOS, size=16, ls=2, line_w=12, gap=8, max_w=290, line="#E6337A"))
    return finish_b(D, out, 1132, "#FFFFFF", 0.5)


# ================================================================ 12. elote con todo — the street-cart elote, dressed
def elote(D, cx, cy, L, W, ang, seed):
    """An elote on a stick: plump kernels in rows round the cob, slathered in mayo, cotija, chile piquín,
    the stick wrapped in a paper napkin."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">']
    out.append(painted(D, rect_pts(cx - 8, cy + L * 0.4, cx + 8, cy + L * 0.98, 12, seed, 0.4), WOOD, seed, sdir=(1, 0), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))

    def half_w(t):
        top_ = math.sin(math.pi / 2 * min(1, (t + 0.02) / 0.3)) ** 0.55
        bot_ = math.sqrt(max(0.0, 1 - max(0, (t - 0.9) / 0.1) ** 2 * 0.55))
        return W / 2 * top_ * bot_ * (1 - 0.12 * t)
    cob = [(cx + half_w(i / 24), cy - L * 0.5 + L * i / 24) for i in range(25)]
    cob = cob + [(2 * cx - x, y) for x, y in cob[::-1]]
    d = smooth_closed(cob)
    out.append(f'<path d="{d}" fill="#A8700A"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    rows, per = 8, 15
    for r_ in range(rows):
        for j in range(per):
            t = (j + 0.5 + (0.5 if r_ % 2 else 0)) / (per + 0.5)
            y = cy - L * 0.5 + L * t
            w = half_w(t)
            u0 = (r_ / rows) * 2 - 1
            u1 = ((r_ + 1) / rows) * 2 - 1
            x0, x1 = cx + w * math.sin(u0 * math.pi / 2), cx + w * math.sin(u1 * math.pi / 2)
            kx, kw = (x0 + x1) / 2, (x1 - x0) * 0.46
            kh = L / per * 0.46
            um = (u0 + u1) / 2
            lit = -um * 0.8 + 0.15
            base = "#FFE27A" if lit > 0.45 else ("#D8960E" if lit < -0.35 else rnd.choice(["#F6C83A", "#F2BE2E", "#FAD24A"]))
            inner.append(f'<path d="{blob(kx, y, kw, kh, rnd.randint(0, 9999), 0.08, 10)}" fill="{base}"/>')
            inner.append(f'<path d="{blob(kx + kw * 0.2, y + kh * 0.25, kw * 0.7, kh * 0.6, rnd.randint(0, 9999), 0.1, 8)}" fill="#C8860A" opacity="0.35"/>')
            if lit > -0.1:
                inner.append(f'<path d="{blob(kx - kw * 0.3, y - kh * 0.35, kw * 0.32, kh * 0.25, rnd.randint(0, 9999), 0.15, 8)}" fill="#FFFBE0" opacity="0.85"/>')
    inner.append(shade_over(D, d, "#4A2000", 0.5, 0, 0, 1, 0, 0.55))
    # mayo: thick glossy ribbons, heavier on the lit side
    for k in range(8):
        y = cy - L * 0.44 + k * L * 0.115
        pts = [(cx - W * 0.46, y + rnd.uniform(-6, 6)), (cx - W * 0.15, y + rnd.uniform(-10, 4)), (cx + W * 0.15, y + rnd.uniform(-4, 10)), (cx + W * 0.46, y + rnd.uniform(-6, 6))]
        inner.append(taper(catmull(pts, 4), rnd.uniform(10, 16), rnd.uniform(6, 10), "#FFF6E2", 0.88))
        inner.append(taper(catmull([(x - 3, y - 3) for x, y in pts[:3]], 4), 3, 1.2, "#FFFFFF", 0.95))
    # cotija crumbs
    for _ in range(170):
        x, y = cx + rnd.uniform(-W * 0.5, W * 0.38), cy + rnd.uniform(-L * 0.48, L * 0.46)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(2.2, 4.6), rnd.uniform(1.8, 3.6), rnd.randint(0, 9999), 0.3, 7)}" fill="{rnd.choice(["#FFFFFF", "#FBF4E4", "#EDE4D0"])}" stroke="#C8B89A" stroke-width="0.5"/>')
    # chile piquín dusting, thicker in a band
    for _ in range(320):
        x, y = cx + rnd.uniform(-W * 0.5, W * 0.5), cy + rnd.uniform(-L * 0.48, L * 0.2) if rnd.random() < 0.7 else cy + rnd.uniform(-L * 0.48, L * 0.48)
        x = cx + rnd.uniform(-W * 0.5, W * 0.5)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.7, 2):.1f}" fill="{rnd.choice(["#C8281A", "#E8402A", "#8A1408", "#D8582A"])}" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#7A4A0A", 2.2, seed, 2, 0.75))
    # mayo drip over the edge
    out.append(taper([(cx + half_w(0.3) - 4, cy - L * 0.2), (cx + half_w(0.3) + 2, cy - L * 0.16), (cx + half_w(0.3) + 1, cy - L * 0.1)], 7, 5, "#FFF6E2", 0.95))
    # paper napkin wrapped round the stick
    nb = cy + L * 0.5
    nap = [(cx - W * 0.3, nb - 14), (cx, nb - 8), (cx + W * 0.3, nb - 16), (cx + W * 0.2, nb + 24), (cx + 14, nb + 50), (cx - 14, nb + 50), (cx - W * 0.2, nb + 24)]
    out.append(painted(D, nap, ("#FFFFFF", "#F6F2EC", "#C8C0B8"), seed + 3, sdir=(0.8, 0.4), sk=0.18, angle=-80, n=10, inkw=1.6, hi=0.4))
    for k in (-1, 0, 1):
        out.append(pline([(cx + k * W * 0.12, nb - 10), (cx + k * 7, nb + 46)], "#C8C0B8", 1.3, seed + k, 0.8, 1))
    out.append(taper([(cx - W * 0.26, nb + 2), (cx, nb + 7), (cx + W * 0.24, nb + 1)], 3, 3, "#E6337A", 0.8))
    out.append("</g>")
    return "".join(out)


@design("elote-con-todo")
def elote_con_todo():
    D = Doc2("mxel")
    # a turquoise colonial wall in late sun, an arched doorway in deep teal, warm light raking across
    out = [sky(D, [(0, "#3ABAB0"), (1, "#18908A")], 1201, 600, ["#6AD8CC", "#0E6A66", "#4AC8BC"], 110, angle=-84, sop=(0.08, 0.2))]
    out.append(f'<path d="M 360 610 L 360 320 Q 470 214 580 320 L 580 610 Z" fill="#0E5A5A"/>')
    out.append(painted(D, [(372, 610), (372, 326), (420, 270), (470, 256), (520, 270), (568, 326), (568, 610)], ("#2A4A6A", "#1A2E4A", "#0A1628"), 1202, sk=0.1, n=20, inkw=0, hi=0.1))
    out.append(f'<path d="M 360 610 L 360 320 Q 470 214 580 320 L 580 610" stroke="#F6C21C" stroke-width="7" fill="none"/>')
    out.append(f'<path d="M -10 -10 L 610 -10 L 610 260 L -10 520 Z" fill="#FFE2A0" opacity="0.18"/>')
    out.append(soft_glow(D, 160, 120, 300, "#FFF2C8", 0.45))
    # sidewalk
    out.append(painted(D, [(-10, 520), (610, 520), (610, 610), (-10, 610)], ("#E8C8A0", "#C8A07A", "#8A6A4A"), 1203, sk=0.06, angle=0, n=30, inkw=1.6, hi=0.2))
    out.append(f'<path d="M -10 520 L 610 520" stroke="#6A4A2A" stroke-width="2" opacity="0.6"/>')
    # papel picado strand
    specs = [(c, m, None) for c, m in zip(FIESTA, ("flower", "bird", "sun", "flower", "heart", "bird", "flower"))]
    out.append(papel_string(D, -40, 26, 640, 30, 24, specs, 1204, 76, 74, rope="#FFF2D8", shadow="#0A3A3A"))
    # the elote, big and diagonal
    out.append(cast(D, 236, 572, 120, 14, strength=0.35, seed=1205))
    out.append(elote(D, 220, 300, 320, 130, 14, 1206))
    # lime wedges and a little chile shaker (no label) on the sidewalk
    out.append(lime_wedge(D, 388, 556, 34, 1207, -20))
    out.append(lime_wedge(D, 440, 568, 30, 1208, 10))
    sx, sb = 512, 566
    out.append(cast(D, sx + 6, sb, 30, 6, strength=0.4, seed=1209))
    out.append(painted(D, rect_pts(sx - 20, sb - 64, sx + 20, sb, 10, 1210, 0.4), ("#FFFFFF", "#EAF2F4", "#9AB0B8"), 1210, sk=0.2, n=10, inkw=1.6, hi=0.5))
    out.append(f'<path d="{hg.org_rect(sx - 18, sb - 40, 36, 36, 1211, 0.4, 8, 2)}" fill="#C8281A" opacity="0.85"/>')
    out.append(specks(1212, (sx - 16, sb - 38, sx + 16, sb - 6), ["#8A1408", "#E8502A"], 20, (0.8, 1.8), (0.6, 1)))
    out.append(painted(D, rect_pts(sx - 21, sb - 78, sx + 21, sb - 62, 10, 1213, 0.4), ("#FFE27A", "#F2C21C", "#A8780A"), 1213, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(taper([(sx - 12, sb - 58), (sx - 12, sb - 10)], 3.5, 2, "#FFFFFF", 0.8))
    # lettering
    out.append(letters(D, 418, 200, "elote", SERIF_IT, 112, "#FFE27A", ["#FFF0A8", "#F6C21C", "#FFFFFF"], 1214, max_w=230,
                       shadow="#0A3A3A", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 424, 256, "CON TODO", BEBAS, 46, "#FFFFFF", ["#FFFFFF", "#D8F4F0"], 1215, ls=8, max_w=200, wob=0.4, shadow="#0A3A3A"))
    out.append(label(418, 290, "MAYO · QUESO · CHILE", JOS, 17, "#FFF2C8", ls=1, max_w=236))
    return finish_b(D, out, 1216, "#FFFFFF", 0.5)


# ================================================================ 13. Guanajuato — a hillside of coloured houses round the basílica
GTO = ["#F2A93A", "#E6337A", "#4A9AD8", "#F27A3A", "#7AC86A", "#C84A3A", "#F6D46A", "#8A5AC8", "#F4E8D8", "#18A8A0", "#F2B8C8"]


def casita(D, x, base, w, h, seed, wall, haze=0.0, detail=True):
    """A little colonial house of Guanajuato: flat roof behind a parapet with a cornice, tall shuttered windows with
    white frames, sometimes an iron balcony, a darker side wall turning away from the light."""
    rnd = random.Random(seed)
    hz = lambda c: mix(c, "#B8C8E8", haze) if haze else c
    out = []
    sw_ = w * 0.16
    out.append(f'<path d="{pd([(x + w, base - h), (x + w + sw_, base - h - sw_ * 0.3), (x + w + sw_, base - sw_ * 0.3), (x + w, base)])}" fill="{hz(dk(wall, 0.32))}"/>')
    front = rect_pts(x, base - h, x + w, base, 10, seed, 0.4)
    out.append(painted(D, front, (hz(lt(wall, 0.3)), hz(wall), hz(dk(wall, 0.25))), seed, sdir=(1, 0.3), sk=0.08, angle=-80, n=max(5, int(w * h / 110)),
                       inkw=1.0 if detail else 0, inkop=0.45, hi=0.25))
    out.append(f'<path d="{hg.org_rect(x - 1.5, base - h - 3, w + 3, 4, seed + 1, 0.3, 8, 1)}" fill="{hz(lt(wall, 0.45))}"/>')
    out.append(f'<path d="M {x:.1f} {base - h + 2:.1f} L {x + w:.1f} {base - h + 2:.1f}" stroke="{hz(dk(wall, 0.3))}" stroke-width="1.2" opacity="0.6"/>')
    floors = 2 if h > 34 else 1
    nwin = max(1, int(w / 16))
    frame = hz("#FFFFFF" if rnd.random() < 0.7 else "#F6D46A")
    for f in range(floors):
        fy = base - h + h * (0.18 + f * 0.46) if floors == 2 else base - h * 0.75
        wh = h * (0.24 if floors == 2 else 0.4)
        for k in range(nwin):
            wx = x + w * (k + 0.5) / nwin - w * 0.1 / nwin * 2
            ww_ = min(8, w / nwin * 0.42)
            out.append(f'<path d="{hg.org_rect(wx - 1.6, fy - 1.6, ww_ + 3.2, wh + 3.2, seed + 10 + k + f * 7, 0.3, 6, 1)}" fill="{frame}"/>')
            gl = hz("#FFE29A") if rnd.random() < 0.12 else hz(rnd.choice(["#2A3A4A", "#3A2A2A", "#2E4A5A"]))
            out.append(f'<rect x="{wx:.1f}" y="{fy:.1f}" width="{ww_:.1f}" height="{wh:.1f}" fill="{gl}"/>')
            if detail and f == 0 and floors == 2 and rnd.random() < 0.55:
                out.append(f'<path d="M {wx - 3:.1f} {fy + wh:.1f} l {ww_ + 6:.1f} 0 l 0 {-wh * 0.35:.1f} m {-ww_ - 6:.1f} 0 l 0 {wh * 0.35:.1f}" stroke="{hz("#2A2026")}" stroke-width="1.2" fill="none"/>')
                for j in range(4):
                    out.append(f'<path d="M {wx - 3 + j * (ww_ + 6) / 3:.1f} {fy + wh:.1f} l 0 {-wh * 0.35:.1f}" stroke="{hz("#2A2026")}" stroke-width="0.8"/>')
            if detail and rnd.random() < 0.35:
                for j in range(3):
                    out.append(f'<circle cx="{wx + j * ww_ / 2:.1f}" cy="{fy + wh + 2:.1f}" r="2" fill="{hz(rnd.choice(["#E6337A", "#F2383A", "#F6D46A"]))}"/>')
    return "".join(out)


def basilica(D, cx, base, s, seed, haze=0.1):
    """The yellow baroque basílica: a two-tier bell tower, a ribbed red dome with a lantern, carved doorway."""
    hz = lambda c: mix(c, "#B8C8E8", haze)
    wall = (hz("#FFE28A"), hz("#F2B42A"), hz("#9A6A0A"))
    out = []
    # nave and façade
    out.append(painted(D, rect_pts(cx - s * 0.5, base - s * 0.62, cx + s * 0.5, base, 14, seed, 0.4), wall, seed, sdir=(1, 0.3), sk=0.12, n=30, inkw=1.4, inkop=0.6, hi=0.3))
    out.append(painted(D, [(cx - s * 0.5, base - s * 0.62), (cx - s * 0.2, base - s * 0.74), (cx + s * 0.1, base - s * 0.8), (cx + s * 0.1, base - s * 0.62)], wall, seed + 1, sk=0.1, n=8, inkw=1.2, inkop=0.5, hi=0.3))
    # dome on a drum
    dx = cx + s * 0.22
    out.append(painted(D, rect_pts(dx - s * 0.2, base - s * 0.86, dx + s * 0.2, base - s * 0.6, 10, seed + 2, 0.4), wall, seed + 2, sk=0.15, n=8, inkw=1.2, hi=0.3))
    for k in range(4):
        out.append(f'<path d="{hg.org_rect(dx - s * 0.16 + k * s * 0.09, base - s * 0.82, s * 0.035, s * 0.12, seed + 3 + k, 0.2, 6, 4)}" fill="{hz("#5A3A1A")}"/>')
    dome = [(dx - s * 0.22, base - s * 0.86), (dx - s * 0.18, base - s * 1.02), (dx, base - s * 1.1), (dx + s * 0.18, base - s * 1.02), (dx + s * 0.22, base - s * 0.86)]
    out.append(painted(D, dome, (hz("#F08A6A"), hz("#C0402A"), hz("#6A1A0A")), seed + 4, sdir=(0.8, 0.3), sk=0.2, n=12, inkw=1.4, hi=0.45))
    for k in (-2, -1, 0, 1, 2):
        out.append(f'<path d="M {dx + k * s * 0.08:.1f} {base - s * 0.86:.1f} Q {dx + k * s * 0.05:.1f} {base - s * 1.0:.1f} {dx:.1f} {base - s * 1.09:.1f}" stroke="{hz("#FFE2B0")}" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(painted(D, rect_pts(dx - s * 0.04, base - s * 1.18, dx + s * 0.04, base - s * 1.08, 6, seed + 5, 0.3), wall, seed + 5, sk=0.2, n=3, inkw=1, hi=0.3))
    out.append(f'<path d="M {dx:.1f} {base - s * 1.18:.1f} l 0 {-s * 0.07:.1f} M {dx - 3:.1f} {base - s * 1.22:.1f} l 6 0" stroke="{hz("#5A3A1A")}" stroke-width="1.6"/>')
    # bell tower
    tx = cx - s * 0.32
    for k, (w0, h0, h1) in enumerate(((0.2, 0.62, 1.0), (0.15, 1.0, 1.24), (0.1, 1.24, 1.38))):
        out.append(painted(D, rect_pts(tx - s * w0, base - s * h1, tx + s * w0, base - s * h0 + 2, 8, seed + 10 + k, 0.3), wall, seed + 10 + k, sdir=(1, 0.3), sk=0.15, n=8, inkw=1.2, inkop=0.6, hi=0.3))
        out.append(f'<path d="{hg.org_rect(tx - s * w0 * 0.5, base - s * h1 + s * (h1 - h0) * 0.2, s * w0, s * (h1 - h0) * 0.55, seed + 13 + k, 0.2, 6, s * w0 * 0.5)}" fill="{hz("#3A2014")}"/>')
        out.append(f'<path d="M {tx - s * w0 - 2:.1f} {base - s * h1:.1f} L {tx + s * w0 + 2:.1f} {base - s * h1:.1f}" stroke="{hz("#FFF2C0")}" stroke-width="2.4"/>')
    out.append(painted(D, [(tx - s * 0.08, base - s * 1.38), (tx, base - s * 1.5), (tx + s * 0.08, base - s * 1.38)], (hz("#F08A6A"), hz("#C0402A"), hz("#6A1A0A")), seed + 16, sk=0.2, n=3, inkw=1.2, hi=0.4))
    out.append(f'<path d="M {tx:.1f} {base - s * 1.5:.1f} l 0 {-s * 0.07:.1f} M {tx - 3:.1f} {base - s * 1.54:.1f} l 6 0" stroke="{hz("#5A3A1A")}" stroke-width="1.6"/>')
    # doorway and the carved frame
    out.append(f'<path d="M {cx - s * 0.08:.1f} {base:.1f} L {cx - s * 0.08:.1f} {base - s * 0.24:.1f} Q {cx:.1f} {base - s * 0.34:.1f} {cx + s * 0.08:.1f} {base - s * 0.24:.1f} L {cx + s * 0.08:.1f} {base:.1f} Z" fill="{hz("#5A2A1A")}"/>')
    out.append(f'<path d="M {cx - s * 0.13:.1f} {base:.1f} L {cx - s * 0.13:.1f} {base - s * 0.42:.1f} L {cx + s * 0.13:.1f} {base - s * 0.42:.1f} L {cx + s * 0.13:.1f} {base:.1f}" stroke="{hz("#FFF2C0")}" stroke-width="2.4" fill="none"/>')
    out.append(f'<path d="{blob(cx, base - s * 0.5, s * 0.04, s * 0.04, seed + 20, 0.05, 10)}" fill="{hz("#5A3A1A")}"/>')
    return "".join(out)


def puff_cloud2(D, cx, cy, w, seed, top="#FFFFFF", shade="#C8D4EC", n=9):
    rnd = random.Random(seed)
    out = []
    puffs = []
    for i in range(n):
        x = cx + (i / (n - 1) - 0.5) * w
        r = w * (0.12 + 0.12 * math.sin(math.pi * i / (n - 1))) * rnd.uniform(0.85, 1.15)
        puffs.append((x, cy - r * 0.4, r))
    out.append(f'<path d="{blob(cx, cy + w * 0.06, w * 0.52, w * 0.1, seed, 0.05, 14)}" fill="{shade}"/>')
    for x, y, r in puffs:
        out.append(f'<path d="{blob(x, y + r * 0.2, r, r * 0.9, rnd.randint(0, 9999), 0.06, 12)}" fill="{shade}"/>')
    for x, y, r in puffs:
        out.append(f'<path d="{blob(x - r * 0.12, y, r * 0.9, r * 0.8, rnd.randint(0, 9999), 0.06, 12)}" fill="{top}"/>')
    return "".join(out)


@design("guanajuato")
def guanajuato():
    D = Doc2("mxgt")
    out = [sky(D, [(0, "#3A8AD8"), (0.5, "#7AB8E8"), (1, "#D8ECF4")], 1301, 600, ["#A8D0F0", "#2A72C0", "#E8F4FA"], 70, sop=(0.06, 0.16))]
    out.append(puff_cloud2(D, 110, 214, 150, 1302))
    out.append(puff_cloud2(D, 492, 190, 130, 1303))
    # the cerro behind, scrubby
    line = ridge([(-20, 300), (120, 250), (260, 266), (380, 236), (520, 262), (620, 250)], 1304, 6)
    out.append(hill(D, line, 620, ("#C8C08A", "#9A9A5A", "#5A6A3A"), 1304, inkw=1.4, inkop=0.4))
    rnd = random.Random(1305)
    for _ in range(40):
        x = rnd.uniform(0, 600)
        out.append(f'<path d="{blob(x, rnd.uniform(270, 320), rnd.uniform(4, 8), rnd.uniform(3, 6), rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#6A8A4A", "#7A9A54", "#4A6A34"])}"/>')
    # rows of houses, back to front; the basílica set among them
    rows = [(300, 30, 0.36, 0.7), (334, 34, 0.3, 0.75), (370, 40, 0.24, 0.8), (408, 46, 0.18, 0.85), (450, 52, 0.12, 0.9), (496, 58, 0.06, 0.95), (546, 64, 0.0, 1.0), (600, 70, 0.0, 1.0)]
    for ri, (base, hmax, haze, sc) in enumerate(rows):
        x = -30 + rnd.uniform(-20, 0)
        while x < 620:
            w = rnd.uniform(34, 62) * sc
            h = rnd.uniform(0.6, 1.0) * hmax
            if ri == 3 and 230 < x < 380:
                x = 380
                continue
            out.append(casita(D, x, base + rnd.uniform(-4, 4), w, h, rnd.randint(0, 99999), rnd.choice(GTO), haze, detail=ri > 1))
            x += w + rnd.uniform(-2, 4)
        if ri == 3:
            out.append(basilica(D, 300, base - 4, 150, 1306, haze=0.08))
        if ri == 5:
            for k in range(6):
                out.append(dab_crown(D, rnd.uniform(40, 560), base - rnd.uniform(36, 50), 14, 11, [("#9ACB6A", "#4E8A34", "#24501A")], rnd.randint(0, 999), n=16, size=(3, 6), inkw=0))
    # a callejón of stairs in the front, with a string of papel picado across
    specs = [(c, m, None) for c, m in zip(FIESTA, ("flower", "sun", "heart", "flower", "bird", "sun", "flower"))]
    out.append(papel_string(D, 30, 470, 570, 470, 24, specs, 1307, 46, 48, rope="#3A2A2A", shadow="#2A1A1A", span=(0.02, 0.98)))
    # lettering
    out.append(letters(D, 300, 132, "Guanajuato", SERIF_IT, 100, "#FFFFFF", ["#FFFFFF", "#E8F2FA", "#FFF6E0"], 1308, max_w=460,
                       shadow="#1E4A8A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "CIUDAD DE CALLEJONES", "#14366A", font=JOS, size=20, ls=6, line_w=28, gap=12, line="#E6337A"))
    return finish_b(D, out, 1309)


# ================================================================ 14. Xochimilco — the trajinera, bow on, with its painted arch
def ahuejote(D, x, base, h, seed, haze=0.0):
    pals = [("#9ACB6A", "#5A8A3A", "#2E5A22"), ("#B8D88A", "#6E9A44", "#3A6A2A")]
    if haze:
        pals = [tuple(mix(c, "#C8D8D0", haze) for c in p) for p in pals]
    out = [taper([(x, base), (x, base - h * 0.5)], h * 0.05, h * 0.03, mix("#5A4A32", "#C8D8D0", haze))]
    out.append(dab_crown(D, x, base - h * 0.55, h * 0.13, h * 0.45, pals, seed, n=int(h * 0.5), size=(h * 0.03, h * 0.06), inkw=0))
    return "".join(out)


@design("xochimilco")
def xochimilco():
    D = Doc2("mxxo")
    out = [sky(D, [(0, "#9AC8E8"), (0.6, "#F2E2C0"), (1, "#F8D8A8")], 1401, 600, ["#C8E0F0", "#7AA8D8", "#FFF0D0"], 60, sop=(0.06, 0.14))]
    out.append(soft_glow(D, 470, 230, 220, "#FFF2C8", 0.7))
    rnd = random.Random(1402)
    # far bank with ahuejotes and a chinampa garden
    out.append(hill(D, ridge([(-20, 300), (300, 296), (620, 302)], 1403, 2), 340, ("#A8C890", "#7AA06A", "#4A7044"), 1403, inkw=0))
    for k in range(14):
        x = -10 + k * 46 + rnd.uniform(-10, 10)
        out.append(ahuejote(D, x, 304, rnd.uniform(120, 170), 1404 + k, haze=0.35))
    # water
    wg = D.lin([(0, "#5A9A84"), (0.5, "#3A7A6A"), (1, "#2A5A50")])
    out.append(f'<rect y="300" width="600" height="300" fill="{wg}"/>')
    out.append(strokes(D.nid(), "M -10 300 L 610 300 L 610 610 L -10 610 Z", (-60, 300, 600, 600), ["#8AC8B0", "#1E4A40", "#C8E8D0"], 1405, n=140, angle=0, length=(20, 80), width=(1.2, 3), opacity=(0.2, 0.5), curve=0.05))
    for k in range(14):
        x = -10 + k * 46
        out.append(f'<path d="{blob(x, 330, 10, 26, 1406 + k, 0.2, 10)}" fill="#4A7A44" opacity="0.35"/>')
    # a second trajinera far off, side on
    out.append(painted(D, [(40, 318), (170, 318), (160, 330), (52, 330)], ("#E89A6A", "#C0502A", "#6A2414"), 1407, sk=0.1, n=4, inkw=1, hi=0.3))
    out.append(f'<path d="{hg.org_rect(56, 290, 104, 6, 1408, 0.3, 8, 2)}" fill="#E6337A"/>')
    for x in (60, 108, 156):
        out.append(f'<rect x="{x - 1}" y="294" width="2.4" height="24" fill="#5A3A2A"/>')
    out.append(f'<path d="{hg.org_rect(36, 286, 24, 34, 1409, 0.3, 6, 2)}" fill="#F6C21C"/>')
    # the trajinera, bow on
    out.append('<g transform="translate(300 330) scale(0.9) translate(-300 -330)">')
    cx = 300
    # hull: flat bow with painted bands, reflection
    hull = [(cx - 190, 470), (cx + 190, 470), (cx + 170, 520), (cx - 170, 520)]
    refl = [(cx - 170, 520), (cx + 170, 520), (cx + 190, 580), (cx - 190, 580)]
    out.append(f'<path d="{pd(refl)}" fill="#1E5A8A" opacity="0.35"/>')
    for k in range(12):
        y = 526 + k * 5
        out.append(f'<path d="M {cx - 180 + rnd.uniform(-10, 10):.1f} {y} l {rnd.uniform(60, 120):.1f} 0 m {rnd.uniform(40, 120):.1f} 0 l {rnd.uniform(60, 120):.1f} 0" stroke="{rnd.choice(["#F6C21C", "#E6337A", "#2E6AC8"])}" stroke-width="2.4" opacity="0.4"/>')
    out.append(painted(D, hull, ("#5A9AE8", "#1E5AAE", "#0A2A6A"), 1410, sdir=(0.3, 1), sk=0.1, angle=0, n=20, inkw=2, hi=0.3))
    for k, (y, c) in enumerate(((480, "#F6C21C"), (494, "#E6337A"), (506, "#FFFFFF"))):
        out.append(f'<path d="{hg.org_rect(cx - 184 + k * 4, y, 368 - k * 8, 6, 1411 + k, 0.4, 14, 2)}" fill="{c}"/>')
    # deck and the canopy receding behind the arch
    out.append(painted(D, [(cx - 168, 466), (cx + 168, 466), (cx + 120, 440), (cx - 120, 440)], WOOD, 1414, sk=0.1, angle=0, n=10, inkw=1.4, hi=0.3))
    out.append(painted(D, [(cx - 176, 260), (cx + 176, 260), (cx + 130, 236), (cx - 130, 236)], ("#FF9AC8", "#E6337A", "#9A1050"), 1415, sk=0.1, angle=0, n=10, inkw=1.6, hi=0.3))
    # shaded interior: the long table, chairs, posts
    out.append(f'<path d="{pd([(cx - 150, 268), (cx + 150, 268), (cx + 150, 466), (cx - 150, 466)])}" fill="#3A2A2A" opacity="0.38"/>')
    from figures import person
    for k, (x, f) in enumerate(((cx - 70, 1), (cx - 24, 1), (cx + 24, -1), (cx + 70, -1))):
        out.append(person(x, 392, 104, "sit_front", f, None, 1430 + k, rim="#FFE0A0", tint=("#5A3A3A", 0.12)))
    out.append(f'<path d="{pd([(cx - 96, 384), (cx + 96, 384), (cx + 66, 350), (cx - 66, 350)])}" fill="#F4E8D4"/>')
    out.append(f'<path d="{pd([(cx - 96, 384), (cx + 96, 384), (cx + 96, 392), (cx - 96, 392)])}" fill="#C8B8A0"/>')
    for k in range(-2, 3):
        out.append(f'<path d="{hg.org_rect(cx + k * 34 - 9, 384, 18, 28, 1416 + k, 0.3, 6, 2)}" fill="{["#F6C21C", "#18A8A0", "#E6337A", "#F5961E", "#2E9A4C"][k + 2]}"/>')
    out.append(f'<path d="{blob(cx - 30, 354, 12, 5, 1421, 0.1, 8)}" fill="#C8401E"/><path d="{blob(cx + 24, 356, 10, 4, 1422, 0.1, 8)}" fill="#7EBA36"/>')
    out.append(f'<rect x="{cx - 4}" y="330" width="8" height="18" fill="#F2C640" opacity="0.9"/>')
    out.append(D.glow(cx, 360, 80, "#FFE0A0", 0.4))
    # the portada: arch board painted with flowers and the boat's name
    ax0, ax1, atop, abot = cx - 200, cx + 200, 120, 300
    arch_out = [(ax0, abot), (ax0, atop + 70), (ax0 + 40, atop + 20), (cx, atop), (ax1 - 40, atop + 20), (ax1, atop + 70), (ax1, abot), (ax1 - 30, abot), (ax1 - 30, atop + 112), (cx, atop + 72), (ax0 + 30, atop + 112), (ax0 + 30, abot)]
    out.append(painted(D, arch_out, ("#FFF0A0", "#F6C21C", "#B8860A"), 1423, sdir=(0.5, 0.8), sk=0.1, angle=0, n=40, inkw=2.2, hi=0.3))
    inner_band = catmull([(ax0 + 15, abot), (ax0 + 15, atop + 86), (ax0 + 52, atop + 42), (cx, atop + 26), (ax1 - 52, atop + 42), (ax1 - 15, atop + 86), (ax1 - 15, abot)], 6)
    out.append(pline(inner_band, "#1E5AAE", 3, 1424, 1, 1))
    outer_band = catmull([(ax0 + 6, abot), (ax0 + 6, atop + 72), (ax0 + 44, atop + 26), (cx, atop + 8), (ax1 - 44, atop + 26), (ax1 - 6, atop + 72), (ax1 - 6, abot)], 6)
    out.append(pline(outer_band, "#E6337A", 2.4, 1425, 1, 1))
    for k, t in enumerate([i / 13 for i in range(14)]):
        x, y = inner_band[int(t * (len(inner_band) - 1))]
        if y > atop + 60 and abs(x - cx) < 120:
            continue
        c = ["#E6337A", "#F5961E", "#2E6AC8", "#7A42B8", "#D2352A"][k % 5]
        for j in range(5):
            a = math.radians(j * 72)
            out.append(f'<path d="{blob(x + math.cos(a) * 6, y + math.sin(a) * 6, 6, 4, 1426 + k * 5 + j, 0.15, 8, j * 72)}" fill="{c}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#FFF4C0"/>')
    for sg in (-1, 1):
        out.append(leaf_simple(D, cx + sg * 70, atop + 50, 34, 9, 90 - sg * 70, ("#9ACB6A", "#3E8A44", "#1E5A2A"), 1490 + sg, vein=False, inkw=1))
    out.append(rotulo(D, cx, atop + 66, "Lupita", SERIF_IT, 44, "#D2352A", "#FFF8D8", "#7A1A10", 1495, max_w=160))
    # posts down to the deck
    for x in (ax0 + 15, ax1 - 15):
        out.append(painted(D, rect_pts(x - 7, abot - 2, x + 7, 468, 6, 1496 + x, 0.3), ("#5A9AE8", "#1E5AAE", "#0A2A6A"), 1496 + x, sk=0.2, n=6, inkw=1.4, hi=0.3))
    # garlands of flowers looping between the posts
    gar = catmull([(ax0 + 22, 304), (cx - 90, 330), (cx, 312), (cx + 90, 330), (ax1 - 22, 304)], 6)
    out.append(pline(gar, "#3E7A3A", 2, 1497, 1, 1))
    for k, (x, y) in enumerate(gar[::3]):
        out.append(f'<circle cx="{x:.1f}" cy="{y + 3:.1f}" r="5" fill="{FIESTA[k % len(FIESTA)]}"/><circle cx="{x:.1f}" cy="{y + 3:.1f}" r="1.8" fill="#FFF4C0"/>')
    out.append("</g>")
    # cempasúchil and roses floating, a few lily pads
    for k in range(10):
        x, y = rnd.uniform(40, 560), rnd.uniform(536, 580)
        if 100 < x < 500 and y < 560:
            continue
        out.append(f'<path d="{blob(x, y, rnd.uniform(12, 18), rnd.uniform(4, 6), rnd.randint(0, 999), 0.1, 10)}" fill="#3E7A3A"/>')
    for k, (x, y) in enumerate(((64, 556), (532, 548), (112, 586))):
        out.append(cempa(D, x, y, 12, 1500 + k, squash=0.6))
    # lettering
    out.append(letters(D, 300, 106, "Xochimilco", SERIF_IT, 90, "#1E4A8A", ["#2E6AC8", "#0E2A62", "#4A8AE8"], 1510, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8C8F8"))
    out.append(f'<path d="{blob(300, 540, 190, 18, 1512, 0.08, 14)}" fill="#1E4A40" opacity="0.5"/>')
    out.append(label(300, 547, "UN PASEO EN TRAJINERA", JOS, 20, "#FFF4E0", ls=5))
    return finish_b(D, out, 1511)


# ================================================================ 15. jacarandas — a city street in spring under a purple canopy
JAC = [("#D8B8F8", "#9A6AD8", "#5A3A9A"), ("#C8A8F0", "#8A5AC8", "#4A2A8A"), ("#E8D0FA", "#B08AE0", "#6A4AAA")]


@design("jacarandas")
def jacarandas():
    D = Doc2("mxjc")
    out = [sky(D, [(0, "#B8D8F2"), (1, "#F2F4F8")], 1601, 600, ["#D8E8F8", "#9AC0E8"], 50, sop=(0.06, 0.14))]
    vx, vy = 300, 330
    rnd = random.Random(1602)
    # pastel façades receding on both sides
    cols = ["#F2D0A0", "#F8E2C8", "#C8E0D8", "#F4C8C8", "#F2E6B0", "#D8D0EC"]
    for sg in (-1, 1):
        for k in range(6):
            t0, t1 = k / 6, (k + 1) / 6
            f = lambda t: 1 - t * 0.85
            xa, xb = vx + sg * 300 * f(t0) * 1.0, vx + sg * 300 * f(t1)
            ya_top, yb_top = vy - 260 * f(t0), vy - 260 * f(t1)
            ya_bot, yb_bot = vy + 220 * f(t0), vy + 220 * f(t1)
            c = cols[(k + (sg > 0) * 3) % len(cols)]
            poly = [(xa, ya_top), (xb, yb_top), (xb, yb_bot), (xa, ya_bot)]
            out.append(f'<path d="{pd(poly)}" fill="{mix(c, "#B8C8E8", t0 * 0.5)}"/>')
            out.append(f'<path d="{pd(poly)}" fill="#3A2A4A" opacity="{0.06 + 0.08 * (sg > 0):.2f}"/>')
            for j in range(2):
                for i in range(2):
                    u0, u1 = 0.2 + i * 0.4, 0.42 + i * 0.4
                    v0, v1 = 0.18 + j * 0.34, 0.36 + j * 0.34
                    pts = []
                    for (u, v) in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                        x = xa + (xb - xa) * u
                        yt = ya_top + (yb_top - ya_top) * u
                        yb = ya_bot + (yb_bot - ya_bot) * u
                        pts.append((x, yt + (yb - yt) * v))
                    out.append(f'<path d="{pd(pts)}" fill="{mix("#3A4A6A", "#B8C8E8", t0 * 0.5)}"/>')
            out.append(f'<path d="M {xa:.1f} {ya_top:.1f} L {xb:.1f} {yb_top:.1f}" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
    # street and sidewalks
    out.append(f'<path d="{pd([(vx - 45, vy + 33), (vx + 45, vy + 33), (vx + 360, 610), (vx - 360, 610)])}" fill="#8A8A9A"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{pd([(vx + sg * 45, vy + 33), (vx + sg * 64, vy + 33), (vx + sg * 640, 610), (vx + sg * 360, 610)])}" fill="#D8CCC0"/>')
    out.append(f'<path d="M {vx} {vy + 36} L {vx} 610" stroke="#F6E8A0" stroke-width="3" stroke-dasharray="12 14" opacity="0.8"/>')
    # petals carpet
    out.append(petals(1603, (0, 400, 600, 600), 360, cols=("#B08AE0", "#9A6AD8", "#D8B8F8", "#8A5AC8"), s=(2, 5)))
    # trees: trunks lining both sides (receding), crowns meeting overhead
    trees = []
    for sg in (-1, 1):
        for k, t in enumerate((0.0, 0.3, 0.52, 0.68, 0.8)):
            f_ = 1 - t * 0.85
            x = vx + sg * 250 * f_
            base = vy + 230 * f_
            h = 330 * f_
            trees.append((t, x, base, h, sg, k))
    for t, x, base, h, sg, k in sorted(trees, key=lambda q: -q[0]):
        hz = t * 0.5
        out.append(taper(catmull([(x, base), (x - sg * h * 0.03, base - h * 0.4), (x - sg * h * 0.12, base - h * 0.7)], 4), h * 0.06, h * 0.025, mix("#4A3A3A", "#B8C8E8", hz)))
        out.append(taper(catmull([(x, base - h * 0.4), (x + sg * h * 0.08, base - h * 0.62)], 4), h * 0.03, h * 0.012, mix("#4A3A3A", "#B8C8E8", hz)))
        pals = [tuple(mix(c, "#E8E0F8", hz) for c in p) for p in JAC]
        out.append(dab_crown(D, x - sg * h * 0.12, base - h * 0.8, h * 0.5, h * 0.3, pals, 1610 + k + (sg > 0) * 10, n=int(h * 1.1), size=(h * 0.025 + 2, h * 0.05 + 3), inkw=0))
    # the near canopy overhead, bleeding off the top corners
    for sg in (-1, 1):
        out.append(dab_crown(D, 300 + sg * 250, 20, 170, 90, JAC, 1625 + sg, n=260, size=(8, 16), inkw=0))
        out.append(dab_crown(D, 300 + sg * 290, 150, 90, 80, JAC, 1627 + sg, n=120, size=(8, 15), inkw=0))
    # falling blossoms
    for k in range(60):
        x, y = rnd.uniform(40, 560), rnd.uniform(200, 540)
        out.append(f'<path d="{blob(x, y, rnd.uniform(2.4, 4.2), rnd.uniform(1.6, 2.6), rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#9A6AD8", "#B08AE0", "#C8A8F0"])}"/>')
    # a bicycle leaning against the near trunk, a basket of flowers
    bx, by = 132, 560
    for dx in (0, 70):
        out.append(f'<circle cx="{bx + dx}" cy="{by - 22}" r="22" fill="none" stroke="#2A2030" stroke-width="3"/>')
        out.append(f'<circle cx="{bx + dx}" cy="{by - 22}" r="3" fill="#2A2030"/>')
    out.append(pline([(bx, by - 22), (bx + 26, by - 54), (bx + 58, by - 54), (bx + 70, by - 22), (bx + 34, by - 22), (bx + 26, by - 54)], "#18A8A0", 4, 1620, 1, 1))
    out.append(pline([(bx + 34, by - 22), (bx + 58, by - 54), (bx + 62, by - 66)], "#18A8A0", 4, 1621, 1, 1))
    out.append(pline([(bx + 22, by - 60), (bx + 34, by - 60)], "#2A2030", 4, 1622, 1, 1))
    out.append(painted(D, rect_pts(bx + 56, by - 82, bx + 86, by - 64, 8, 1623, 0.4), WOOD, 1623, sk=0.2, n=4, inkw=1.2, hi=0.3))
    for k in range(6):
        out.append(f'<circle cx="{bx + 58 + k * 5:.1f}" cy="{by - 84 - (k % 2) * 3:.1f}" r="3.4" fill="{["#9A6AD8", "#F6C21C", "#E6337A"][k % 3]}"/>')
    # lettering in the sky gap
    out.append(f'<path d="{blob(300, 140, 210, 70, 1629, 0.1, 16)}" fill="#F4F2FA" opacity="0.7"/>')
    out.append(letters(D, 300, 140, "jacarandas", SERIF_IT, 96, "#5A2A9A", ["#7A42B8", "#3A1A6A", "#9A6AD8"], 1630, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#D8B8F8"))
    out.append(ruled(300, 182, "PRIMAVERA EN LA CIUDAD", "#3A2A6A", font=JOS, size=19, ls=5, line_w=24, gap=10, line="#9A6AD8"))
    return finish_b(D, out, 1631)


# ================================================================ 16. Jalisco — blue agave fields at sundown, a vintage poster
def agave(D, x, base, s, seed, pal=AGAVE, light=-1, inkw=1.0):
    """Blue agave rosette: long spear leaves fanning from the heart, a dark spine at each tip, toothed edges."""
    rnd = random.Random(seed)
    out = []
    leaves = []
    n = 13
    for i in range(n):
        a = -180 + 10 + i * (160 / (n - 1)) + rnd.uniform(-5, 5)
        L = s * (0.55 + 0.45 * math.sin(math.pi * i / (n - 1))) * rnd.uniform(0.85, 1.05)
        leaves.append((abs(a + 90), a, L))
    for _, a, L in sorted(leaves, key=lambda q: -q[0]):
        r = math.radians(a)
        ux, uy = math.cos(r), math.sin(r)
        nx, ny = -uy, ux
        W = s * 0.085
        pts = []
        for t in (0, 0.2, 0.5, 0.8, 1.0):
            w = W * (1 - t) ** 0.7
            pts.append((x + ux * L * t + nx * w, base + uy * L * t * 0.9 + ny * w))
        for t in (0.8, 0.5, 0.2, 0):
            w = W * (1 - t) ** 0.7
            pts.append((x + ux * L * t - nx * w, base + uy * L * t * 0.9 - ny * w))
        lit = (ux * light) > 0
        c = (mix(pal[0], "#FFD0B0", 0.3), mix(pal[1], pal[0], 0.35), pal[2]) if lit else (pal[1], dk(pal[1], 0.22), pal[2])
        out.append(f'<path d="{smooth_closed(pts)}" fill="{c[1]}"/>')
        out.append(f'<path d="M {x:.1f} {base:.1f} L {x + ux * L * 0.95:.1f} {base + uy * L * 0.95 * 0.9:.1f}" stroke="{c[0]}" stroke-width="{max(0.8, W * 0.35):.1f}" opacity="0.55"/>')
        if inkw:
            out.append(ink(smooth_closed(pts), pal[2], inkw, seed, 1, 0.5))
        out.append(f'<circle cx="{x + ux * L:.1f}" cy="{base + uy * L * 0.9:.1f}" r="{max(0.8, W * 0.22):.1f}" fill="#3A1A10"/>')
    return "".join(out)


@design("jalisco")
def jalisco():
    D = Doc2("mxjl")
    out = [sky(D, [(0, "#3A2A6A"), (0.35, "#C8507A"), (0.62, "#F2905A"), (0.8, "#FFD08A"), (1, "#FFE8B0")], 1701, 600, ["#E87A7A", "#FFC08A", "#7A4A8A"], 80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 380, 300, 200, "#FFF2C0", 0.9))
    out.append(f'<circle cx="380" cy="300" r="34" fill="#FFF4D0"/>')
    # thin streaks of cloud
    for k, (x, y, w) in enumerate(((140, 120, 220), (460, 160, 180), (220, 210, 260))):
        out.append(taper([(x - w / 2, y), (x, y - 4), (x + w / 2, y + 2)], 6, 2, "#FFB8A8", 0.55))
    # volcano silhouette and far ridges
    out.append(hill(D, [(-20, 300), (80, 290), (170, 236), (210, 216), (240, 222), (300, 270), (400, 296), (620, 300)], 620, ("#9A6A9A", "#6A4A7A", "#3A2A4A"), 1702, inkw=0, sop=(0.08, 0.18)))
    out.append(f'<rect y="200" width="600" height="110" fill="{D.lin([(0, "#FFC8A0", 0), (1, "#FFC8A0", 0.35)])}"/>')
    out.append(hill(D, ridge([(-20, 312), (300, 306), (620, 312)], 1703, 3), 620, ("#B8604A", "#8A3A2A", "#4A1A14"), 1703, inkw=0))
    # rows of agave converging to the horizon
    vpx, vpy = 300, 306
    band = 424
    for k in range(-7, 8):
        xb = vpx + k * 150
        out.append(f'<path d="M {vpx + k * 2:.1f} {vpy} L {xb - 30:.1f} {band} L {xb + 30:.1f} {band} Z" fill="#5A2014" opacity="0.4"/>')
        out.append(f'<path d="M {vpx + k * 2 + 1:.1f} {vpy} L {xb + 40:.1f} {band} L {xb + 52:.1f} {band} Z" fill="#E88A5A" opacity="0.25"/>')
    rnd = random.Random(1704)
    items = []
    for k in range(-7, 8):
        for t in [0.035 * (1.42 ** j) for j in range(14)]:
            if t > 1.0:
                break
            y = vpy + (band + 6 - vpy) * t
            x = vpx + (k * 150 + 75) * t + rnd.uniform(-4, 4) * t
            s = 5 + 104 * t ** 1.1
            if -40 < x < 640:
                items.append((y, x, s))
    for y, x, s in sorted(items):
        hz = max(0, 0.6 - (y - vpy) / 200)
        pal = tuple(mix(c, "#C8A0B0", hz) for c in ("#A8D8D0", "#4E9A92", "#1E4A4A"))
        out.append(agave(D, x, y, s, rnd.randint(0, 9999), pal, light=1, inkw=0.8 if s > 30 else 0))
    # poster band
    out.append(f'<rect y="{band}" width="600" height="{600 - band}" fill="#1E3A5A"/>')
    out.append(strokes(D.nid(), f"M -10 {band} L 610 {band} L 610 610 L -10 610 Z", (-60, band, 600, 600), ["#2E5A7A", "#0E2238"], 1705, n=40, angle=0, length=(60, 160), width=(3, 8), opacity=(0.15, 0.3)))
    out.append(f'<path d="M -10 {band + 2} L 610 {band + 2}" stroke="#F2B84A" stroke-width="4"/>')
    fs = fit_size("JALISCO", ANTON, 84, 460, 6)
    out.append(f'<text x="303" y="{band + 88}" text-anchor="middle" {ANTON} font-size="{fs}" letter-spacing="6" fill="#0A1A2A">JALISCO</text>')
    out.append(f'<text x="300" y="{band + 84}" text-anchor="middle" {ANTON} font-size="{fs}" letter-spacing="6" fill="#FFE8B8">JALISCO</text>')
    out.append(label(300, band + 118, "CAMPOS DE AGAVE AZUL", MONO, 18, "#F2B84A", ls=5))
    return finish_b(D, out, 1706, "#FFFFFF", 0.5)


# ================================================================ 17. ¡dale, dale, dale! — the star piñata over the backyard
def fringe_cone(D, bx, by, ang, L, W, cols, seed):
    """One piñata point: a cone wrapped in rows of fringed tissue paper, streamers at the tip."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (bx + ux * L, by + uy * L)
    cone = [(bx + nx * W / 2, by + ny * W / 2), tip, (bx - nx * W / 2, by - ny * W / 2)]
    out = [f'<path d="{pd(cone)}" fill="{cols[0]}"/>']
    rows = 6
    for r_ in range(rows, 0, -1):
        t = r_ / rows
        w = W / 2 * (1 - t) + 2
        px, py = bx + ux * L * t, by + uy * L * t
        c = cols[r_ % len(cols)]
        fr = []
        m = max(4, int(w / 3))
        for i in range(m + 1):
            s_ = -1 + 2 * i / m
            fx, fy = px + nx * w * s_, py + ny * w * s_
            fr.append((fx, fy))
            if i < m:
                s2 = -1 + 2 * (i + 0.5) / m
                fr.append((px + nx * w * s2 - ux * L / rows * 1.1, py + ny * w * s2 - uy * L / rows * 1.1))
        back = [(px + nx * w * 1.05 + ux * L / rows * 0.4, py + ny * w * 1.05 + uy * L / rows * 0.4), (px - nx * w * 1.05 + ux * L / rows * 0.4, py - ny * w * 1.05 + uy * L / rows * 0.4)]
        poly = fr + back[::-1][::-1]
        poly = fr + [back[1], back[0]]
        out.append(f'<path d="{pd(poly)}" fill="{c}"/>')
        out.append(f'<path d="{pd(fr, False)}" fill="none" stroke="{dk(c, 0.25)}" stroke-width="1" opacity="0.6"/>')
    # shade the far side
    out.append(f'<path d="{pd([cone[0], tip, (bx, by)])}" fill="#2A0A1A" opacity="0.18"/>')
    out.append(ink(pd(cone), INK, 1.6, seed, 1, 0.6))
    # streamers from the tip
    for k in range(3):
        c = cols[(k + 1) % len(cols)]
        pts = [tip]
        for j in range(1, 7):
            pts.append((tip[0] + math.sin(j * 1.2 + k) * 6 + (k - 1) * j * 2, tip[1] + j * 13))
        out.append(taper(catmull(pts, 3), 6, 4, c, 0.95))
    return "".join(out)


def candy(D, cx, cy, s, col, seed, ang=0):
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">']
    for sg in (-1, 1):
        out.append(f'<path d="{pd([(cx + sg * s * 0.5, cy), (cx + sg * s * 1.05, cy - s * 0.45), (cx + sg * s * 0.95, cy), (cx + sg * s * 1.05, cy + s * 0.45)])}" fill="{lt(col, 0.3)}" stroke="{dk(col, 0.3)}" stroke-width="1"/>')
    out.append(painted(D, blob_pts(cx, cy, s * 0.6, s * 0.42, seed, 0.04, 12), pal_of(col), seed, sk=0.25, n=3, inkw=1.2, hi=0.5, hik=0.15))
    out.append(f'<path d="M {cx - s * 0.3:.1f} {cy - s * 0.35:.1f} l {s * 0.2:.1f} {s * 0.7:.1f} M {cx + s * 0.05:.1f} {cy - s * 0.38:.1f} l {s * 0.2:.1f} {s * 0.7:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.7"/>')
    out.append("</g>")
    return "".join(out)


@design("dale-dale-dale")
def dale_dale_dale():
    D = Doc2("mxdd")
    out = [sky(D, [(0, "#2E8AD8"), (0.7, "#8AC8F0"), (1, "#D8F0F8")], 1801, 600, ["#A8D8F8", "#1E6AC0", "#E8F6FA"], 70, sop=(0.06, 0.16))]
    out.append(puff_cloud2(D, 470, 120, 170, 1802))
    out.append(puff_cloud2(D, 90, 360, 140, 1803))
    # tree branch top-left, rope down to the piñata
    out.append(taper(catmull([(-20, 40), (90, 52), (200, 60), (300, 58)], 5), 22, 8, "#5A3A22"))
    for k, (x, y, a) in enumerate(((60, 44, -140), (130, 52, -60), (190, 58, -150), (240, 60, -40), (280, 58, -120), (100, 50, 120), (220, 62, 70))):
        out.append(leaf_simple(D, x, y, 40, 11, a, ("#9ACB6A", "#4E8A34", "#24501A"), 1804 + k, inkw=1))
    cx, cy = 300, 262
    out.append(pline([(296, 58), (298, 120), (cx, cy - 64)], "#C8A060", 3, 1805, 1, 1))
    # the star: seven fringed points round a fringed ball
    pal = [(ROSA[1], AMAR[1], TURQ[1]), (MARI[1], ROSA[1], "#2E9A4C"), (TURQ[1], MORADO[1], AMAR[1]), (AMAR[1], "#2E9A4C", ROSA[1]),
           (MORADO[1], MARI[1], TURQ[1]), ("#2E9A4C", ROSA[1], AMAR[1]), (CHILE[1], AMAR[1], TURQ[1])]
    angs = [-90 + 360 / 7 * (i + 0.5) for i in range(7)]
    for k, a in sorted(enumerate(angs), key=lambda q: -math.sin(math.radians(q[1]))):
        out.append(fringe_cone(D, cx, cy, a, 136, 64, pal[k], 1810 + k))
    ball = blob_pts(cx, cy, 70, 66, 1820, 0.03, 20)
    out.append(painted(D, ball, ROSA, 1820, sdir=(0.6, 0.7), sk=0.2, n=10, inkw=2, hi=0.4))
    bc = D.clip(f'<path d="{smooth_closed(ball)}"/>')
    rows = []
    for j in range(9):
        y = cy - 66 + j * 16
        c = [ROSA[1], AMAR[1], TURQ[1], MARI[1], MORADO[1], "#2E9A4C"][j % 6]
        fr = [(cx - 80 + i * 8 + (4 if i % 2 else 0), y + (10 if i % 2 else 0)) for i in range(21)]
        rows.append(f'<path d="{pd(fr + [(cx + 90, y - 10), (cx - 90, y - 10)])}" fill="{c}"/>')
        rows.append(f'<path d="{pd(fr, False)}" fill="none" stroke="{dk(c, 0.3)}" stroke-width="1" opacity="0.6"/>')
    rows.append(shade_over(D, smooth_closed(ball), "#3A0A1A", 0.4, 0, 0, 1, 1, 0.45))
    rows.append(f'<path d="{blob(cx - 26, cy - 30, 22, 12, 1821, 0.2, 10, -30)}" fill="#FFFFFF" opacity="0.3"/>')
    out.append(f'<g {bc}>{"".join(rows)}</g>')
    out.append(ink(smooth_closed(ball), INK, 2, 1822, 1, 0.7))
    # candies and treats tumbling out
    rnd = random.Random(1823)
    for k in range(14):
        x, y = rnd.uniform(100, 500), rnd.uniform(384, 436)
        if k % 4 == 3:
            out.append(painted(D, blob_pts(x, y, 9, 6, 1830 + k, 0.1, 10, rnd.uniform(0, 180)), ("#E8C88A", "#C89A5A", "#7A5A2A"), 1830 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
        else:
            out.append(candy(D, x, y, 11, rnd.choice(FIESTA), 1840 + k, rnd.uniform(-60, 60)))
    for k in range(10):
        out.append(f'<path d="{blob(rnd.uniform(80, 520), rnd.uniform(370, 440), rnd.uniform(3, 6), rnd.uniform(2, 4), rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(FIESTA)}"/>')
    # the stick, ribbon-wrapped, swinging in from the right
    out.append('<g transform="translate(14 -96) rotate(-38 520 470)">')
    out.append(painted(D, rect_pts(512, 360, 528, 590, 10, 1850, 0.4), WOOD, 1850, sdir=(1, 0), sk=0.25, angle=-90, n=10, inkw=1.6, hi=0.4))
    for k in range(9):
        y = 372 + k * 24
        out.append(f'<path d="M 511 {y} L 529 {y + 12}" stroke="{FIESTA[k % len(FIESTA)]}" stroke-width="6"/>')
    out.append("</g>")
    # lettering
    out.append(letters(D, 300, 500, "¡dale, dale, dale!", SERIF_IT, 76, "#FFFFFF", ["#FFFFFF", "#FFE8F0", "#FFF6D8"], 1860, max_w=470,
                       shadow="#9A1050", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 538, "NO PIERDAS EL TINO", "#14366A", font=JOS, size=19, ls=5, line_w=30, gap=12, line="#E6337A"))
    return finish_b(D, out, 1861)


# ================================================================ 18. el mercado — the fruit stand under the pink tarp
def mango(D, cx, cy, r, seed, rot_=0):
    pts = rot(blob_pts(cx, cy, r, r * 0.74, seed, 0.05, 14), cx, cy, rot_)
    pts = [(x + (2 if y < cy else -1), y) for x, y in pts]
    out = [painted(D, pts, ("#FFE27A", "#F6B42A", "#B8700A"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-30, n=8, inkw=1.4, hi=0.5, hik=0.12)]
    out.append(f'<path d="{blob(cx + r * 0.25, cy - r * 0.25, r * 0.5, r * 0.4, seed + 1, 0.2, 10)}" fill="#E8502A" opacity="0.45"/>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.3, r * 0.22, r * 0.12, seed + 2, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.5"/>')
    return "".join(out)


def papaya_half(D, cx, cy, w, h, seed, rot_=0):
    outer = rot(blob_pts(cx, cy, w / 2, h / 2, seed, 0.03, 16), cx, cy, rot_)
    inner = rot(blob_pts(cx, cy, w / 2 - 6, h / 2 - 6, seed + 1, 0.03, 16), cx, cy, rot_)
    out = [painted(D, outer, ("#B8E07A", "#5E9A3E", "#2A5A1A"), seed, sk=0.2, n=6, inkw=1.6, hi=0.4)]
    out.append(painted(D, inner, ("#FFB07A", "#F26A2A", "#B03A0E"), seed + 1, sk=0.15, n=10, inkw=0, hi=0.5))
    cav = rot(blob_pts(cx, cy, w * 0.26, h * 0.13, seed + 2, 0.08, 12), cx, cy, rot_)
    out.append(f'<path d="{smooth_closed(cav)}" fill="#FFD8A8"/>')
    rnd = random.Random(seed)
    for _ in range(int(w * 0.5)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.85
        x, y = rot([(cx + math.cos(a) * w * 0.24 * rr, cy + math.sin(a) * h * 0.11 * rr)], cx, cy, rot_)[0]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.8, 2.8):.1f}" fill="#1A1210"/><circle cx="{x - 0.6:.1f}" cy="{y - 0.6:.1f}" r="0.7" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


def sandia_slice(D, cx, cy, r, seed, rot_=0):
    """A wedge of watermelon seen from the side: green rind, white band, red flesh, black seeds."""
    rp = rot([(cx - r, cy), (cx + r, cy)] + [(cx + r * math.cos(math.radians(a)), cy + r * 0.8 * math.sin(math.radians(a))) for a in range(0, 181, 15)][2:-1][::1], cx, cy, rot_)
    rind = rot([(cx - r, cy), (cx + r, cy)] + [(cx + r * math.cos(math.radians(a)), cy + r * 0.85 * math.sin(math.radians(a))) for a in range(15, 166, 15)][::-1][::-1], cx, cy, rot_)
    arc = lambda rr, k: [(cx + rr * math.cos(math.radians(a)), cy - rr * k * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    out = []
    o = rot(arc(r, 0.85), cx, cy, rot_)
    out.append(painted(D, o, ("#8ACB6A", "#2E7A3A", "#14401E"), seed, sk=0.1, n=6, inkw=1.6, hi=0.3))
    out.append(f'<path d="{smooth_closed(rot(arc(r - 6, 0.85), cx, cy, rot_))}" fill="#F4F8E0"/>')
    fl = rot(arc(r - 11, 0.83), cx, cy, rot_)
    out.append(painted(D, fl, ("#FF8A8A", "#E8303A", "#9A0E1A"), seed + 1, sk=0.12, angle=-90, n=12, inkw=0, hi=0.4))
    rnd = random.Random(seed)
    for _ in range(int(r * 0.25)):
        a, rr = rnd.uniform(20, 160), rnd.uniform(0.35, 0.75)
        x, y = rot([(cx + math.cos(math.radians(a)) * (r - 11) * rr, cy - math.sin(math.radians(a)) * (r - 11) * 0.83 * rr)], cx, cy, rot_)[0]
        out.append(f'<path d="{blob(x, y, 2, 3.2, rnd.randint(0, 999), 0.1, 8, a)}" fill="#1A1010"/>')
    return "".join(out)


def pitahaya(D, cx, cy, r, seed, rot_=0):
    pts = rot(blob_pts(cx, cy, r * 0.8, r, seed, 0.04, 14), cx, cy, rot_)
    out = [painted(D, pts, ("#FF9AC8", "#E6337A", "#9A1050"), seed, sk=0.2, n=8, inkw=1.4, hi=0.45)]
    for k in range(8):
        a = math.radians(k * 45 + 20)
        x, y = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.8
        out.append(leaf_simple(D, x, y, r * 0.55, r * 0.14, math.degrees(a) - 40, ("#D8F07A", "#7EBA36", "#3A6A12"), seed + k, vein=False, inkw=0.8))
    return "".join(out)


def lime_ball(D, cx, cy, r, seed):
    return painted(D, blob_pts(cx, cy, r, r * 0.9, seed, 0.04, 12), ("#C8F07A", "#5EA82E", "#2A5A0E"), seed, sk=0.25, n=3, inkw=1, hi=0.5, hik=0.15)


def huacal(D, x0, y0, x1, y1, seed):
    """A wooden crate (huacal): slatted front, darker gaps, nailed corners."""
    out = [f'<path d="{hg.org_rect(x0, y0, x1 - x0, y1 - y0, seed, 0.6, 14, 2)}" fill="#5A3A1E"/>']
    n = 3
    h = (y1 - y0) / n
    for k in range(n):
        out.append(painted(D, rect_pts(x0 + 2, y0 + k * h + 2, x1 - 2, y0 + (k + 1) * h - 3, 20, seed + k, 0.5), ("#F2D0A0", "#D8A870", "#8A6038"), seed + k, sk=0.15, angle=0, n=8, inkw=1, hi=0.3))
    for x in (x0 + 5, x1 - 5):
        out.append(painted(D, rect_pts(x - 4, y0 - 4, x + 4, y1, 6, seed + int(x), 0.4), ("#E8C090", "#C89860", "#7A5430"), seed + int(x), sk=0.2, n=3, inkw=1, hi=0.3))
    return "".join(out)


def price_tag(D, x, y, w, h, s, seed, rot_=0):
    out = [f'<g transform="rotate({rot_:.1f} {x:.1f} {y:.1f})">']
    out.append(f'<path d="{hg.org_rect(x - w / 2, y - h / 2, w, h, seed, 0.8, 10, 2)}" fill="#E8C898" stroke="#A88A5A" stroke-width="1"/>')
    out.append(label(x, y + 6, s, BEBAS, 20, "#1A1A2A", ls=1, max_w=w - 8))
    out.append("</g>")
    return "".join(out)


@design("el-mercado")
def el_mercado():
    D = Doc2("mxmc")
    out = [paper(D.nid(), "#F6E4D0", FLECK, 1901)]
    # the pink lona, glowing with light through it
    lona = [(-10, -10), (610, -10), (610, 170)] + [(610 - i * 31, 170 + (14 if i % 2 else 0) + 6 * math.sin(i)) for i in range(21)] + [(-10, 170)]
    out.append(f'<path d="{pd(lona)}" fill="#E6337A"/>')
    out.append(f'<path d="{pd(lona)}" fill="{D.rad([(0, "#FF9AC8", 0.7), (1, "#FF9AC8", 0)], 0.5, 0.3, 0.7)}"/>')
    out.append(strokes(D.nid(), pd(lona), (-40, -10, 610, 190), ["#FF7AB0", "#B01A5A", "#FFB0D0"], 1902, n=80, angle=-8, length=(40, 140), width=(2, 6), opacity=(0.12, 0.3)))
    for k in range(5):
        out.append(f'<path d="M {k * 140 - 20} -10 Q {k * 140 + 10} 90 {k * 140 - 6} 180" stroke="#9A1050" stroke-width="2" fill="none" opacity="0.3"/>')
    # under the tarp: rosy shade, back wall of stacked crates
    out.append(f'<rect y="170" width="600" height="300" fill="#C88A7A" opacity="0.3"/>')
    out.append(f'<rect y="170" width="600" height="40" fill="#9A1050" opacity="0.15"/>')
    rnd = random.Random(1903)
    # back tier: watermelons, a cut half; pitahayas
    out.append(huacal(D, 40, 300, 290, 352, 1904))
    out.append(huacal(D, 310, 300, 560, 352, 1905))
    for k, x in enumerate((76, 132, 188)):
        out.append(painted(D, blob_pts(x, 282, 36, 28, 1906 + k, 0.04, 14), ("#7ACB6A", "#2E7A3A", "#14401E"), 1906 + k, sk=0.2, n=6, inkw=1.6, hi=0.4))
        cid = D.clip(f'<path d="{blob(x, 282, 36, 28, 1906 + k, 0.04, 14)}"/>')
        out.append(f'<g {cid}>' + "".join(f'<path d="M {x + j * 12 - 30:.1f} 250 Q {x + j * 14 - 30:.1f} 282 {x + j * 12 - 30:.1f} 314" stroke="#14401E" stroke-width="4" fill="none" opacity="0.5"/>' for j in range(6)) + "</g>")
    out.append(sandia_slice(D, 248, 300, 46, 1910))
    for k, (x, y) in enumerate(((340, 290), (380, 282), (420, 292), (460, 284), (500, 292), (530, 286))):
        out.append(pitahaya(D, x, y, 20, 1911 + k * 3, rnd.uniform(-30, 30)))
    # front tier: mangoes, papaya halves, limes
    out.append(huacal(D, 20, 420, 300, 486, 1920))
    out.append(huacal(D, 300, 420, 580, 486, 1921))
    for k in range(13):
        x, y = 44 + (k % 7) * 38 + (19 if k >= 7 else 0), 404 - (k // 7) * 22
        out.append(mango(D, x, y, 22, 1922 + k, rnd.uniform(-30, 30)))
    out.append(papaya_half(D, 360, 398, 104, 54, 1940, -6))
    out.append(papaya_half(D, 448, 404, 100, 52, 1941, 8))
    for k in range(9):
        x, y = 494 + (k % 3) * 24, 392 + (k // 3) * 14 - 14
        out.append(lime_ball(D, x, y, 12, 1942 + k))
    # the counter: chiles in a bowl, a scale pan, a paper bag
    out.append(f'<rect y="486" width="600" height="124" fill="{D.lin([(0, "#6A3A20"), (1, "#3A1E10")])}"/>')
    out.append(wood_planks(D, 486, 600, 1950, WOOD, 3))
    bx = 150
    out.append(cast(D, bx + 6, 556, 70, 8, strength=0.4, seed=1951))
    out.append(painted(D, [(bx - 70, 520), (bx + 70, 520), (bx + 52, 556), (bx - 52, 556)], ("#8AE0D8", "#18A8A0", "#0A6060"), 1952, sk=0.2, n=8, inkw=1.8, hi=0.4))
    for k in range(12):
        x = bx - 56 + (k % 6) * 22
        y = 512 - (k // 6) * 10
        c = (("#F4907A", "#D2352A", "#7A1010") if k % 3 else ("#B8E07A", "#4E9A2E", "#2A5A14"))
        out.append(taper(catmull([(x - 12, y + 2), (x, y - 4), (x + 14, y + 4)], 3), 9, 2, c[1]))
        out.append(taper([(x - 12, y + 1), (x - 16, y - 3)], 2.4, 2, "#3E6A1A"))
        out.append(taper(catmull([(x - 8, y - 1), (x, y - 4), (x + 6, y - 1)], 3), 2, 1, "#FFFFFF", 0.6))
    out.append(price_tag(D, 160, 452, 84, 28, "MANGO", 1954, 4))
    out.append(price_tag(D, 404, 452, 94, 28, "PAPAYA", 1955, -4))
    out.append(price_tag(D, 434, 330, 104, 28, "PITAHAYA", 1956, 3))
    # paper bag with a mango peeking out, right
    gx, gb = 470, 590
    out.append(cast(D, gx + 6, gb - 4, 52, 8, strength=0.4, seed=1957))
    out.append(mango(D, gx + 4, gb - 86, 22, 1958, -40))
    out.append(painted(D, [(gx - 42, gb - 82), (gx + 42, gb - 86), (gx + 46, gb - 4), (gx - 46, gb - 4)], ("#F2D8A8", "#D8B07A", "#8A6A3A"), 1959, sdir=(0.9, 0.3), sk=0.2, angle=-88, n=14, inkw=1.6, hi=0.4))
    out.append(pline([(gx - 42, gb - 74), (gx, gb - 70), (gx + 42, gb - 76)], "#A8804A", 1.4, 1960, 0.8, 1))
    # lettering on the tarp
    out.append(letters(D, 300, 110, "el mercado", SERIF_IT, 96, "#FFFFFF", ["#FFFFFF", "#FFE2EE", "#FFF4D8"], 1961, max_w=440,
                       shadow="#7A0A3A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 152, "¿QUÉ VA A LLEVAR?", "#FFF4D8", font=JOS, size=21, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 1962)


# ================================================================ 19. salsa de molcajete — from above: the stone, the salsa, the ingredients
def tomato(D, cx, cy, r, seed, charred=False):
    out = [cast(D, cx + r * 0.25, cy + r * 0.3, r * 1.05, r * 0.95, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.05, 14), CHILE, seed, sdir=(0.6, 0.7), sk=0.22, angle=-40, n=8, inkw=1.4, hi=0.5, hik=0.12))
    rnd = random.Random(seed)
    if charred:
        for _ in range(7):
            a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.7)
            out.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(3, 7), rnd.uniform(2, 5), rnd.randint(0, 999), 0.3, 8)}" fill="#2A1008" opacity="0.8"/>')
        out.append(f'<path d="{blob(cx + r * 0.2, cy + r * 0.1, r * 0.4, r * 0.2, seed + 3, 0.3, 10)}" fill="#F8C8A0" opacity="0.4"/>')
    for k in range(5):
        a = math.radians(k * 72 + 10)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} q {math.cos(a) * r * 0.2:.1f} {math.sin(a) * r * 0.1:.1f} {math.cos(a) * r * 0.32:.1f} {math.sin(a) * r * 0.32:.1f}" stroke="#3E7A2A" stroke-width="{max(2, r * 0.1):.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.36, r * 0.22, r * 0.12, seed + 4, 0.2, 8, -35)}" fill="#FFFFFF" opacity="0.65"/>')
    return "".join(out)


def chile_pod(D, x, y, L, ang, seed, pal=(("#B8E07A", "#4E9A2E", "#1E5A14"))):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for t in (0, 0.15, 0.4, 0.7, 0.9, 1.0):
        w = L * 0.12 * (1 - t ** 2.2) + 1
        bend = L * 0.05 * math.sin(t * math.pi)
        pts.append((x + ux * L * t + nx * (w + bend), y + uy * L * t + ny * (w + bend)))
    for t in (1.0, 0.9, 0.7, 0.4, 0.15, 0):
        w = L * 0.12 * (1 - t ** 2.2) + 1
        bend = L * 0.05 * math.sin(t * math.pi)
        pts.append((x + ux * L * t - nx * (w - bend), y + uy * L * t - ny * (w - bend)))
    out = [cast(D, x + ux * L * 0.5 + 4, y + uy * L * 0.5 + 5, L * 0.5, L * 0.12, strength=0.3, seed=seed)]
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=ang, n=5, inkw=1.3, hi=0.5, hik=0.15))
    out.append(taper([(x - ux * 2, y - uy * 2), (x - ux * L * 0.18 + nx * 3, y - uy * L * 0.18 + ny * 3)], 4, 2, "#3E6A1A"))
    out.append(taper([(x + ux * L * 0.15 + nx * L * 0.04, y + uy * L * 0.15 + ny * L * 0.04), (x + ux * L * 0.6 + nx * L * 0.06, y + uy * L * 0.6 + ny * L * 0.06)], 2.4, 1, "#FFFFFF", 0.6))
    return "".join(out)


def garlic(D, cx, cy, r, seed):
    out = [cast(D, cx + 3, cy + 4, r, r * 0.8, strength=0.3, seed=seed)]
    for k in range(6):
        a = math.radians(k * 60 + 15)
        x, y = cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45
        out.append(painted(D, rot(blob_pts(x, y, r * 0.42, r * 0.3, seed + k, 0.08, 10), x, y, k * 60 + 15), ("#FFFFFF", "#F4ECE0", "#C8B8A8"), seed + k, sk=0.2, n=3, inkw=1, hi=0.5))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.18:.1f}" fill="#B8A890"/>')
    return "".join(out)


def onion_half(D, cx, cy, r, seed):
    out = [cast(D, cx + 4, cy + 5, r * 1.05, r, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.03, 16), ("#FFFFFF", "#F6EEF4", "#C8B0C8"), seed, sk=0.15, n=6, inkw=1.4, hi=0.4))
    for k in range(1, 6):
        out.append(f'<path d="{blob(cx + k * 0.6, cy + k * 0.4, r * (1 - k * 0.16), r * (1 - k * 0.16), seed + k, 0.03, 14)}" fill="none" stroke="#D8C0D8" stroke-width="1.6"/>')
    out.append(f'<path d="{blob(cx, cy, r * 1.0, r * 1.0, seed, 0.03, 16)}" fill="none" stroke="#A8789A" stroke-width="2.4" opacity="0.7"/>')
    return "".join(out)


def cilantro(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    out = []
    a = math.radians(ang)
    for k in range(5):
        da = math.radians(rnd.uniform(-22, 22))
        ex, ey = x + math.cos(a + da) * L, y + math.sin(a + da) * L
        out.append(pline([(x, y), ((x + ex) / 2 + rnd.uniform(-4, 4), (y + ey) / 2 + rnd.uniform(-4, 4)), (ex, ey)], "#5A9A3A", 1.6, seed + k, 1, 1))
        for j in range(3):
            lx, ly = ex + rnd.uniform(-8, 8), ey + rnd.uniform(-8, 8)
            for i in range(3):
                b = rnd.uniform(0, 6.28)
                out.append(f'<path d="{blob(lx + math.cos(b) * 3, ly + math.sin(b) * 3, 4.2, 3.2, rnd.randint(0, 999), 0.3, 7, math.degrees(b))}" fill="{rnd.choice(["#4E9A3A", "#6AB84A", "#2E7A2A"])}"/>')
    return "".join(out)


@design("salsa-de-molcajete")
def salsa_de_molcajete():
    D = Doc2("mxsm")
    out = [wood_planks(D, -10, 610, 2001, ("#C89A6A", "#9A6A3E", "#5A3A1E"), 5, vertical=True)]
    out.append(soft_glow(D, 220, 160, 360, "#FFF0D0", 0.35))
    # striped woven cloth under the stone, on the diagonal
    clothp = rot([(150, 200), (520, 200), (520, 570), (150, 570)], 335, 385, -12)
    stripes = "".join(f'<rect x="0" y="{i * 8}" width="24" height="8" fill="{c}"/>' for i, c in enumerate(["#FFF4E0", ROSA[1], "#FFF4E0", TURQ[1], "#FFF4E0", AMAR[1]]))
    pat = D.pattern(24, 48, stripes, transform="rotate(-12)")
    out.append(cast(D, 345, 400, 220, 210, strength=0.3, seed=2002))
    out.append(f'<path d="{hg.org_poly(clothp, 2003, 1, 14, 2)}" fill="{pat}"/>')
    out.append(strokes(D.nid(), hg.org_poly(clothp, 2003, 1, 14, 2), bbox(clothp), ["#FFFFFF", "#3A2010"], 2004, n=120, angle=-102, length=(8, 20), width=(0.6, 1.4), opacity=(0.1, 0.25)))
    for k in range(12):
        p0 = clothp[3]
        p1 = clothp[2]
        t = k / 11
        x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        out.append(f'<path d="M {x:.1f} {y:.1f} l {-3:.1f} 14" stroke="#F4E8D0" stroke-width="2.4" stroke-linecap="round"/>')
    # the molcajete from above
    cx, cy, R = 330, 372, 138
    out.append(cast(D, cx + 22, cy + 26, R + 8, R + 4, strength=0.55, seed=2005))
    for a in (40, 160, 280):
        lx, ly = cx + math.cos(math.radians(a)) * R * 0.92 + 14, cy + math.sin(math.radians(a)) * R * 0.92 + 18
        out.append(f'<path d="{blob(lx, ly, 22, 18, 2006 + a, 0.1, 10)}" fill="#2A2624"/>')
    stone = blob_pts(cx, cy, R, R * 0.98, 2007, 0.025, 28)
    out.append(painted(D, stone, ("#8A8480", "#5A5450", "#2A2624"), 2007, sdir=(0.6, 0.7), sk=0.12, angle=-40, n=60, inkw=2.2, hi=0.4))
    sc = D.clip(f'<path d="{smooth_closed(stone)}"/>')
    rnd = random.Random(2008)
    pores = []
    for _ in range(260):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * R
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        pr = rnd.uniform(0.8, 2.6)
        pores.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{pr:.1f}" fill="#1A1614" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
        if rnd.random() < 0.4:
            pores.append(f'<circle cx="{x - pr * 0.5:.1f}" cy="{y - pr * 0.5:.1f}" r="{pr * 0.5:.1f}" fill="#B8B0A8" opacity="0.5"/>')
    out.append(f'<g {sc}>{"".join(pores)}</g>')
    # inner wall and the salsa
    out.append(f'<path d="{blob(cx, cy, R * 0.84, R * 0.83, 2009, 0.02, 24)}" fill="#3A3432"/>')
    sal = blob_pts(cx + 2, cy + 3, R * 0.76, R * 0.75, 2010, 0.03, 24)
    out.append(painted(D, sal, ("#F05A3A", "#B8281A", "#6A0E06"), 2010, sdir=(0.6, 0.7), sk=0.15, angle=-30, n=50, inkw=1.6, inkc="#3A0A04", hi=0.3, curve=0.6))
    slc = D.clip(f'<path d="{smooth_closed(sal)}"/>')
    bits = []
    for _ in range(46):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * R * 0.72
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        bits.append(f'<path d="{blob(x, y, rnd.uniform(6, 12), rnd.uniform(4, 8), rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8402A", "#D23020", "#F26A4A", "#A01A10"])}"/>')
    for _ in range(60):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * R * 0.72
        bits.append(f'<ellipse cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" rx="2" ry="1.3" fill="#FFE8B0" transform="rotate({rnd.uniform(0, 180):.0f} {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f})"/>')
    for _ in range(30):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * R * 0.7
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        bits.append(f'<path d="{hg.org_rect(x, y, rnd.uniform(3, 6), rnd.uniform(3, 6), rnd.randint(0, 999), 0.4, 6, 1)}" fill="#FFFDF4" opacity="0.9"/>')
    for _ in range(40):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * R * 0.7
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        bits.append(f'<path d="{blob(x, y, 3.4, 2.4, rnd.randint(0, 999), 0.3, 7, rnd.uniform(0, 180))}" fill="{rnd.choice(["#3E8A2A", "#5AAA3A"])}"/>')
    bits.append(f'<path d="{blob(cx - R * 0.3, cy - R * 0.32, R * 0.22, R * 0.1, 2011, 0.3, 10, -35)}" fill="#FFFFFF" opacity="0.4"/>')
    bits.append(f'<path d="{blob(cx - R * 0.16, cy - R * 0.44, R * 0.08, R * 0.04, 2012, 0.3, 8, -35)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(f'<g {slc}>{"".join(bits)}</g>')
    # the tejolote resting on the rim
    tj = rot(blob_pts(cx + R * 0.72, cy - R * 0.62, 26, 62, 2013, 0.05, 14), cx + R * 0.72, cy - R * 0.62, 48)
    out.append(cast(D, cx + R * 0.72 + 16, cy - R * 0.62 + 18, 60, 30, strength=0.45, seed=2014))
    out.append(painted(D, tj, ("#8A8480", "#5A5450", "#2A2624"), 2013, sdir=(0.6, 0.7), sk=0.25, angle=48, n=12, inkw=2, hi=0.45))
    out.append(f'<path d="{blob(cx + R * 0.68, cy - R * 0.85, 12, 7, 2015, 0.2, 8, 48)}" fill="#C8281A" opacity="0.7"/>')
    # ingredients round about
    out.append(tomato(D, 112, 300, 34, 2020, charred=True))
    out.append(tomato(D, 128, 388, 30, 2021))
    out.append(tomato(D, 506, 536, 30, 2022, charred=True))
    out.append(chile_pod(D, 92, 470, 96, -18, 2023))
    out.append(chile_pod(D, 106, 504, 90, -4, 2024))
    out.append(chile_pod(D, 420, 548, 84, -170, 2025, (("#F4907A", "#C8281A", "#6A0A06"))))
    out.append(garlic(D, 196, 548, 26, 2026))
    out.append(onion_half(D, 526, 262, 38, 2027))
    out.append(cilantro(D, 540, 330, 50, 120, 2028))
    out.append(cilantro(D, 270, 560, 40, -150, 2029))
    out.append(lime_wedge(D, 534, 430, 30, 2030, 30))
    # lettering
    out.append('<g transform="rotate(-2 300 124)">')
    card = rect_pts(92, 52, 508, 200, 24, 2031, 0.6)
    out.append(cast(D, 306, 206, 220, 14, strength=0.4, seed=2035))
    out.append(painted(D, card, ("#FFFDF4", "#F6EEDC", "#C8B894"), 2031, sdir=(0.3, 1), sk=0.06, angle=0, n=30, inkw=1.6, hi=0.3))
    for y in (88, 128, 168):
        out.append(f'<path d="M 104 {y} L 496 {y}" stroke="#9AC0D8" stroke-width="1" opacity="0.6"/>')
    out.append(f'<path d="M 128 56 L 128 196" stroke="#E87A7A" stroke-width="1.2" opacity="0.6"/>')
    out.append(f'<path d="{hg.org_rect(270, 40, 60, 22, 2036, 0.5, 8, 1)}" fill="#F2E8C0" opacity="0.8"/>')
    out.append(letters(D, 300, 100, "salsa de", SERIF_IT, 46, "#5A2A14", ["#7A3A1E", "#3A1808"], 2032, max_w=200, wob=0.5))
    out.append(letters(D, 300, 160, "molcajete", SERIF_IT, 80, "#C8361E", ["#E8502A", "#8A1E0A", "#F07A4A"], 2033, max_w=380,
                       shadow="#F2D8C0", soff=(0.02, 0.035), angle=-40, hi="#FFC8A8"))
    out.append(label(300, 190, "PICA, PERO RICO", JOS, 18, "#1E6A44", ls=6))
    out.append("</g>")
    return finish_b(D, out, 2034, "#3A2418", 0.8)


# ================================================================ 20. tortillas hechas a mano — the comal, a tortilla puffing up
def chiquihuite(D, cx, base, w, h, seed):
    """A woven palm basket lined with an embroidered servilleta, tortillas stacked inside."""
    top = base - h
    out = [cast(D, cx + 10, base, w * 0.6, 10, strength=0.45, seed=seed)]
    # tortillas stacked, seen above the rim
    for k in range(4):
        out.append(painted(D, ell_pts(cx + k * 1.5, top - 6 - k * 4, w * 0.4, w * 0.11, 0, 360, 24)[:-1], ("#FFF2C0", "#EED690", "#B8964A"), seed + k, sk=0.15, n=6, inkw=1.2, hi=0.4))
    out.append(specks(seed, (cx - w * 0.3, top - 26, cx + w * 0.3, top - 12), ["#8A5A1A", "#C89A4A"], 20, (0.8, 2), (0.4, 0.8)))
    # the cloth, draped over the back and spilling forward
    cl = [(cx - w * 0.62, top + 6), (cx - w * 0.5, top - 30), (cx - w * 0.3, top - 10), (cx + w * 0.3, top - 10), (cx + w * 0.52, top - 34), (cx + w * 0.64, top + 6), (cx + w * 0.4, top + 70), (cx + w * 0.2, top + 44), (cx - w * 0.4, top + 56)]
    out.append(painted(D, cl, ("#FFFFFF", "#F8F2E8", "#C8B8A8"), seed + 10, sk=0.15, n=10, inkw=1.4, hi=0.3))
    for k in range(7):
        x = cx - w * 0.5 + k * w * 0.16
        y = top + 28 + 14 * math.sin(k)
        for j in range(4):
            a = math.radians(j * 90 + 45)
            out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * 5:.1f} {math.sin(a) * 5:.1f}" stroke="{[ROSA[1], TURQ[1], MARI[1], MORADO[1]][k % 4]}" stroke-width="2.4" stroke-linecap="round"/>')
    # basket body (front)
    body = [(cx - w / 2, top + 8), (cx + w / 2, top + 8), (cx + w * 0.42, base - 6), (cx + w * 0.3, base), (cx - w * 0.3, base), (cx - w * 0.42, base - 6)]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="#B88A4A"/>')
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    wv = []
    rows = int(h / 11) + 1
    for i in range(rows):
        y = top + 12 + i * 11
        x = cx - w / 2 - 10 + (i % 2) * 9
        while x < cx + w / 2 + 10:
            wv.append(f'<path d="{blob(x + 9, y, 9.5, 4.6, rnd.randint(0, 9999), 0.1, 8)}" fill="{rnd.choice(["#E8C080", "#D8AA66", "#F2CE90"])}"/>')
            wv.append(f'<path d="M {x:.1f} {y + 3:.1f} Q {x + 9:.1f} {y + 6:.1f} {x + 18:.1f} {y + 3:.1f}" stroke="#7A5020" stroke-width="1" fill="none" opacity="0.5"/>')
            x += 18
    for k in range(rows):
        y = top + 12 + k * 11
        if k % 4 == 2:
            wv.append(f'<rect x="{cx - w}" y="{y - 4}" width="{2 * w}" height="8" fill="{ROSA[1]}" opacity="0.75"/>')
    wv.append(shade_over(D, d, "#3A1A06", 0.5, 0, 0, 1, 0.3, 0.3))
    out.append(f'<g {cid}>{"".join(wv)}</g>')
    out.append(ink(d, INK, 2, seed, 2, 0.7))
    out.append(taper(ell_pts(cx, top + 8, w / 2, 8, -4, 184, 20), 9, 9, "#9A6A30"))
    return "".join(out)


def tortilla_flat(D, cx, cy, rx, ry, seed, puff=0.0):
    rnd = random.Random(seed)
    out = []
    pts = blob_pts(cx, cy, rx, ry, seed, 0.03, 22)
    if puff:
        pts = [(x, y - puff * max(0, 1 - ((x - cx) / rx) ** 2) * (1 if y < cy + ry * 0.2 else 0.2)) for x, y in pts]
        top = [(cx + rx * t, cy - puff * (1 - t * t) ** 0.8) for t in [i / 12 - 1 for i in range(25)]]
        dome = top + [(cx + rx, cy), (cx - rx, cy)]
        out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 24)[:-1], ("#FFF2C0", "#EED690", "#B8964A"), seed + 1, sk=0.1, n=8, inkw=1.2, hi=0.3))
        out.append(painted(D, top + ell_pts(cx, cy, rx, ry, 0, 180, 12)[1:-1], ("#FFF4C8", "#F2DA96", "#B89A4A"), seed, sdir=(0.6, 0.7), sk=0.22, angle=-20, n=12, inkw=1.6, hi=0.5, hik=0.12))
        for _ in range(16):
            x = cx + rnd.uniform(-rx * 0.8, rx * 0.8)
            y = cy - puff * (1 - ((x - cx) / rx) ** 2) ** 0.8 * rnd.uniform(0.2, 0.95) + rnd.uniform(0, ry * 0.3)
            out.append(f'<path d="{blob(x, y, rnd.uniform(3, 7), rnd.uniform(2, 4), rnd.randint(0, 999), 0.3, 8)}" fill="{rnd.choice(["#8A5A1A", "#A86A2A", "#6A3A10"])}" opacity="{rnd.uniform(0.5, 0.85):.2f}"/>')
        return "".join(out)
    out.append(painted(D, pts, ("#FFF2C0", "#EED690", "#B8964A"), seed, sk=0.12, n=10, inkw=1.4, hi=0.35))
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.85
        out.append(f'<path d="{blob(cx + math.cos(a) * rr * rx, cy + math.sin(a) * rr * ry, rnd.uniform(3, 7), rnd.uniform(1.5, 3), rnd.randint(0, 999), 0.3, 8)}" fill="{rnd.choice(["#8A5A1A", "#A86A2A"])}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    return "".join(out)


@design("tortillas-hechas-a-mano")
def tortillas_hechas_a_mano():
    D = Doc2("mxth")
    # an añil-blue kitchen wall, limewash texture, morning light from the left
    out = [sky(D, [(0, "#3A62B8"), (1, "#24448A")], 2101, 600, ["#5A82D0", "#1A3474", "#7A9AE0"], 120, angle=-84, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 110, 140, 320, "#FFF0D0", 0.4))
    out.append(blooms(2102, ["#6A8AD8", "#1A3474", "#8AA8E8"], 8, (0, 0, 600, 420), (80, 160), (0.1, 0.18)))
    # hanging clay jarritos on nails, a wooden shelf
    out.append(painted(D, rect_pts(330, 214, 572, 230, 20, 2103, 0.4), WOOD, 2103, sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    for k, x in enumerate((362, 414, 466, 518)):
        out.append(f'<circle cx="{x}" cy="240" r="2.6" fill="#3A2418"/>')
        out.append(f'<g transform="translate({x} 244) scale(0.72) translate({-x} -244)">' + jarrito(D, x, 322, 64, 2104 + k, handle=-1 if k % 2 else 1, drink="#3A1A0A") + "</g>")
    # a ristra of dried chiles hanging on the left
    out.append(pline([(80, 196), (82, 330)], "#C8A060", 2.2, 2140, 1, 1))
    rr = random.Random(2141)
    for k in range(13):
        y = 206 + k * 10
        for sg in (-1, 1):
            a = 90 + sg * rr.uniform(30, 60)
            out.append(chile_pod(D, 81, y, rr.uniform(34, 42), a, 2142 + k * 2 + sg, (("#E86A4A", "#A81E10", "#4A0804"))))
    # the fogón: an adobe stove with the fire glowing in its mouth
    out.append(painted(D, [(-10, 420), (610, 420), (610, 610), (-10, 610)], ("#E8B08A", "#C88A62", "#7A4A30"), 2105, sk=0.08, angle=0, n=40, inkw=1.6, hi=0.25))
    out.append(f'<path d="M -10 420 L 610 420" stroke="#5A3420" stroke-width="3"/>')
    out.append(f'<path d="M 180 610 L 180 520 Q 270 460 360 520 L 360 610 Z" fill="#2A1008"/>')
    out.append(D.glow(270, 560, 140, "#FF8A2A", 0.75))
    for k in range(5):
        x = 210 + k * 30
        out.append(f'<path d="{smooth_closed([(x, 600), (x + 10, 560 - k % 2 * 14), (x + 6, 540 - (k % 3) * 8), (x + 16, 566), (x + 22, 600)])}" fill="{["#FFB43A", "#FF7A1E", "#FFD27A"][k % 3]}"/>')
    # the comal
    ccx, ccy = 270, 412
    out.append(f'<path d="{smooth_closed(ell_pts(ccx, ccy + 6, 210, 44, 0, 360, 36)[:-1])}" fill="#140A08"/>')
    out.append(painted(D, ell_pts(ccx, ccy, 206, 40, 0, 360, 36)[:-1], ("#5A5250", "#2A2422", "#0A0806"), 2106, sdir=(0.3, 1), sk=0.08, angle=0, n=30, inkw=1.8, hi=0.25))
    out.append(ink(smooth_open(ell_pts(ccx, ccy, 204, 38, 190, 350, 18)), "#8A8480", 2, 2107, 1, 0.6))
    out.append(tortilla_flat(D, 176, 408, 70, 20, 2108))
    out.append(tortilla_flat(D, 330, 408, 82, 22, 2109, puff=44))
    out.append(steam(330, 350, 70, 2110, "#FFFFFF", 3, 26, 7, 0.55))
    # masa in a clay bowl, small balls ready
    out.append(clay_pot(D, 86, 412, 112, 40, 2111, BARRO, neck=0.98, lip=1.0, handles=False, deco=None, soot=False, inside="#F4E2A8"))
    for k, (x, y) in enumerate(((70, 368), (96, 364), (84, 352))):
        out.append(painted(D, blob_pts(x, y, 14, 11, 2112 + k, 0.05, 12), ("#FFF6D0", "#F2DCA0", "#B8A060"), 2112 + k, sk=0.25, n=3, inkw=1.2, hi=0.5))
    # the basket of tortillas, right
    out.append(chiquihuite(D, 478, 470, 150, 92, 2120))
    # lettering
    out.append(letters(D, 300, 126, "tortillas", SERIF_IT, 104, "#FFF2D8", ["#FFFFFF", "#F8DEB8", "#FFE8C8"], 2130, max_w=420,
                       shadow="#0E1E4A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "HECHAS A MANO", "#F6C21C", font=JOS, size=24, ls=8, line_w=40, gap=14))
    return finish_b(D, out, 2131, "#FFFFFF", 0.5)


# ================================================================ 21. mi casa es su casa — the front door, open-armed
def bugambilia(D, pts, seed, n=60, pal=ROSA, leaf=("#8ACB6A", "#3E8A3A", "#1E5A22")):
    """A cascade of bougainvillea along a path: papery magenta bracts in clusters, a few leaves, thin woody stems."""
    rnd = random.Random(seed)
    out = [pline(pts, "#6A4A2A", 2.4, seed, 0.9, 1)]
    items = []
    for i in range(n):
        x, y = pts[rnd.randrange(len(pts))]
        x += rnd.uniform(-26, 26)
        y += rnd.uniform(-18, 26)
        items.append((y, x))
    for y, x in sorted(items):
        if rnd.random() < 0.3:
            out.append(leaf_simple(D, x, y, rnd.uniform(14, 22), rnd.uniform(5, 7), rnd.uniform(0, 360), leaf, rnd.randint(0, 9999), vein=False, inkw=0.8))
        else:
            for k in range(3):
                a = rnd.uniform(0, 6.28) + k * 2.1
                px, py = x + math.cos(a) * 5, y + math.sin(a) * 5
                c = rnd.choice([pal[0], pal[1], pal[1], dk(pal[1], 0.15)])
                out.append(f'<path d="{blob(px, py, 7, 5.2, rnd.randint(0, 9999), 0.18, 8, math.degrees(a))}" fill="{c}"/>')
                out.append(f'<path d="M {x:.1f} {y:.1f} L {px + math.cos(a) * 4:.1f} {py + math.sin(a) * 4:.1f}" stroke="{dk(pal[1], 0.35)}" stroke-width="0.8" opacity="0.6"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#FFF4C0"/>')
    return "".join(out)


@design("mi-casa-es-su-casa")
def mi_casa_es_su_casa():
    D = Doc2("mxmc2")
    # warm ochre limewashed wall
    out = [sky(D, [(0, "#F2B45A"), (1, "#D88A3A")], 2201, 600, ["#F8C878", "#C0702A", "#FFD898"], 120, angle=-84, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 150, 140, 360, "#FFF0C8", 0.5))
    out.append(blooms(2202, ["#F8C878", "#B8601E"], 8, (0, 0, 600, 600), (80, 160), (0.08, 0.14)))
    # cantera stone frame with an arch, the wooden double door
    cx, top, base, W = 300, 250, 540, 200
    frame = [(cx - W / 2 - 30, base), (cx - W / 2 - 30, top + 40), (cx - W / 2, top - 10), (cx, top - 34), (cx + W / 2, top - 10), (cx + W / 2 + 30, top + 40), (cx + W / 2 + 30, base)]
    out.append(cast(D, cx + 16, base - 140, W * 0.7, 160, strength=0.18, seed=2203))
    out.append(painted(D, frame, ("#F8DCC8", "#E2B8A0", "#9A6A58"), 2204, sdir=(1, 0.3), sk=0.12, angle=-80, n=40, inkw=2, hi=0.3))
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        x0, y0 = cx + math.cos(a) * (W / 2 + 2), top + 30 + math.sin(a) * 60
        x1, y1 = cx + math.cos(a) * (W / 2 + 30), top + 30 + math.sin(a) * 86
        out.append(f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}" stroke="#9A6A58" stroke-width="1.6" opacity="0.7"/>')
    for y in range(int(top + 70), base, 36):
        for sg in (-1, 1):
            out.append(f'<path d="M {cx + sg * (W / 2):.1f} {y} l {sg * 30:.1f} 0" stroke="#9A6A58" stroke-width="1.6" opacity="0.7"/>')
    door = [(cx - W / 2, base), (cx - W / 2, top + 30), (cx - W / 2 + 20, top - 2), (cx, top - 14), (cx + W / 2 - 20, top - 2), (cx + W / 2, top + 30), (cx + W / 2, base)]
    out.append(painted(D, door, ("#B87A4A", "#7A4220", "#3A1A08"), 2205, sdir=(0.9, 0.2), sk=0.12, angle=-90, n=60, slen=(30, 90), sw=(1, 3), inkw=2, hi=0.3))
    dd = smooth_closed(door)
    cid = D.clip(f'<path d="{dd}"/>')
    inner = [f'<path d="M {cx} {top - 20} L {cx} {base}" stroke="#2A0E04" stroke-width="3"/>']
    for sg in (-1, 1):
        for (y0, y1) in ((top + 40, top + 150), (top + 172, base - 24)):
            x0 = cx + sg * 14
            x1 = cx + sg * (W / 2 - 16)
            inner.append(f'<path d="{hg.org_rect(min(x0, x1), y0, abs(x1 - x0), y1 - y0, 2206 + y0 + sg, 0.6, 12, 2)}" fill="#5A2E12" opacity="0.6"/>')
            inner.append(f'<path d="{hg.org_rect(min(x0, x1) + 6, y0 + 6, abs(x1 - x0) - 12, y1 - y0 - 12, 2207 + y0 + sg, 0.6, 12, 2)}" fill="#8A4E26" opacity="0.7"/>')
            for j in range(3):
                for i in range(2):
                    inner.append(f'<circle cx="{min(x0, x1) + (i + 0.5) * abs(x1 - x0) / 2:.1f}" cy="{y0 + (j + 0.5) * (y1 - y0) / 3:.1f}" r="3.4" fill="#2A1A10"/><circle cx="{min(x0, x1) + (i + 0.5) * abs(x1 - x0) / 2 - 1:.1f}" cy="{y0 + (j + 0.5) * (y1 - y0) / 3 - 1:.1f}" r="1.2" fill="#C8A878"/>')
    inner.append(shade_over(D, dd, "#1A0800", 0.45, 0, 0, 1, 0, 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for sg in (-1, 1):
        out.append(f'<circle cx="{cx + sg * 30}" cy="390" r="13" fill="none" stroke="#2A1A10" stroke-width="4"/><circle cx="{cx + sg * 30}" cy="376" r="5" fill="#2A1A10"/>')
    # talavera tile plaque above the door, a lantern, the step
    for k in range(3):
        out.append(talavera_tile(D, cx - 54 + k * 36, top - 72, 36, 2210 + k, kind=k % 2))
    out.append(f'<rect x="{cx - 54}" y="{top - 72}" width="108" height="36" fill="none" stroke="#1E3F9A" stroke-width="2"/>')
    out.append(painted(D, [(cx - W / 2 - 50, base), (cx + W / 2 + 50, base), (cx + W / 2 + 60, base + 22), (cx - W / 2 - 60, base + 22)], ("#E8D0C0", "#C8A898", "#7A5A4A"), 2213, sk=0.2, angle=0, n=10, inkw=1.6, hi=0.3))
    lx, ly = cx + W / 2 + 64, top + 30
    out.append(f'<path d="M {lx - 20} {ly - 10} L {lx} {ly - 10} L {lx} {ly}" stroke="#2A1A10" stroke-width="3" fill="none"/>')
    out.append(D.glow(lx, ly + 24, 50, "#FFE8A0", 0.6))
    out.append(painted(D, [(lx - 12, ly), (lx + 12, ly), (lx + 10, ly + 36), (lx - 10, ly + 36)], ("#FFF4C0", "#FFD870", "#C8902A"), 2214, sk=0.15, n=4, inkw=2, inkc="#2A1A10", hi=0.5))
    out.append(f'<path d="M {lx - 15} {ly} L {lx} {ly - 10} L {lx + 15} {ly} Z" fill="#2A1A10"/>')
    # pots each side: a tall agave on the left, geraniums on the right, and a woven doormat
    out.append(clay_pot(D, 120, 556, 100, 92, 2220, BARRO, neck=0.9, lip=0.95, handles=False, soot=False))
    out.append(agave(D, 120, 466, 96, 2221, AGAVE, light=-1))
    out.append(clay_pot(D, 482, 556, 96, 78, 2222, BARRO, neck=0.9, lip=0.95, handles=False, soot=False))
    for k, (x, y, r) in enumerate(((456, 470, 22), (500, 462, 24), (480, 444, 20))):
        out.append(geranium_leaf(D, x, y + 16, 18, 2223 + k))
    for k, (x, y, r) in enumerate(((452, 444, 20), (508, 436, 22), (482, 418, 20))):
        out.append(geranium(D, x, y, r, 2226 + k, CHILE))
    mat = [(cx - 90, 552), (cx + 90, 552), (cx + 100, 572), (cx - 100, 572)]
    out.append(painted(D, mat, ("#F2D8A8", "#D8B078", "#8A6A3A"), 2229, sk=0.15, angle=0, n=10, inkw=1.4, hi=0.3))
    for k, c in enumerate((ROSA[1], TURQ[1], ROSA[1])):
        out.append(f'<path d="M {cx - 92 + k * 2} {556 + k * 6} L {cx + 92 - k * 2} {556 + k * 6}" stroke="{c}" stroke-width="2.6"/>')
    # bougainvillea spilling over the top right and down the frame
    out.append(bugambilia(D, catmull([(620, 10), (540, 40), (470, 110), (430, 200), (420, 250)], 4), 2230, 120))
    out.append(bugambilia(D, catmull([(-20, 230), (40, 236), (100, 252), (150, 230)], 4), 2231, 40))
    # lettering
    out.append(letters(D, 236, 120, "mi casa", SERIF_IT, 94, "#FFFFFF", ["#FFFFFF", "#FFF2DC"], 2240, max_w=330,
                       shadow="#7A3A10", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 236, 164, "ES SU CASA", BEBAS, 40, "#1E3F9A", ["#2E5AC8", "#0C2060"], 2241, ls=10, max_w=300, wob=0.4))
    return finish_b(D, out, 2242)


# ================================================================ 22. ¡échale ganas! — a nopal on the windowsill, a new pad at sunrise
def nopal_pad(D, cx, cy, w, h, ang, seed, pal=NOPAL, young=False):
    pts = rot(blob_pts(cx, cy, w / 2, h / 2, seed, 0.05, 16), cx, cy, ang)
    if young:
        pal = ("#D8F0A0", "#9ACB5A", "#4E8A2A")
    out = [painted(D, pts, pal, seed, sdir=(0.6, 0.6), sk=0.18, angle=ang - 90, n=int(w * h / 180) + 6, inkw=1.6, hi=0.4)]
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    ar = []
    for i in range(int(w * h / 260)):
        u, v = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.85, 0.85)
        if u * u + v * v > 0.7:
            continue
        x, y = rot([(cx + u * w / 2, cy + v * h / 2)], cx, cy, ang)[0]
        ar.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{dk(pal[1], 0.3)}"/><circle cx="{x - 0.5:.1f}" cy="{y - 0.5:.1f}" r="0.9" fill="#FFF8D8"/>')
        if not young:
            for k in range(2):
                a = rnd.uniform(0, 6.28)
                ar.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * 5:.1f} {math.sin(a) * 5:.1f}" stroke="#FFF8E0" stroke-width="0.9" opacity="0.85"/>')
    out.append(f'<g {cid}>{"".join(ar)}</g>')
    return "".join(out)


@design("echale-ganas")
def echale_ganas():
    D = Doc2("mxeg")
    # pink wall, turquoise window frame, sunrise in the window
    out = [sky(D, [(0, "#F6A0B8"), (1, "#E8789A")], 2301, 600, ["#FFB8C8", "#D8587A", "#FFC8D8"], 110, angle=-84, sop=(0.08, 0.18))]
    wx0, wy0, wx1, wy1 = 120, 196, 480, 430
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#6A8AD8"), (0.5, "#F6A8A0"), (0.8, "#FFD08A"), (1, "#FFE8B0")])}"/>')
    out.append(soft_glow(D, 300, 400, 170, "#FFF2C0", 0.9))
    out.append(f'<circle cx="300" cy="404" r="36" fill="#FFF4C8"/>')
    for k in range(10):
        a = math.radians(-180 + k * 20)
        out.append(f'<path d="M {300 + math.cos(a) * 46:.1f} {404 + math.sin(a) * 46:.1f} L {300 + math.cos(a) * 150:.1f} {404 + math.sin(a) * 150:.1f}" stroke="#FFF4C8" stroke-width="4" opacity="0.35"/>')
    out.append(hill(D, ridge([(wx0, 404), (220, 390), (320, 400), (420, 384), (wx1, 396)], 2302, 4), wy1, ("#C88AA8", "#9A5A88", "#5A2A5A"), 2302, inkw=0))
    out.append(hill(D, ridge([(wx0, 418), (300, 410), (wx1, 420)], 2303, 3), wy1, ("#8A5A7A", "#5A3A5A", "#2A1A2A"), 2303, inkw=0))
    for k, (x, y) in enumerate(((180, 250), (210, 236), (420, 262))):
        out.append(bird_v(x, y, 7, "#5A3A6A", 0.8))
    # window frame and mullions
    fr = "#18A8A0"
    out.append(f'<path d="M {wx0 - 18} {wy0 - 18} L {wx1 + 18} {wy0 - 18} L {wx1 + 18} {wy1} L {wx0 - 18} {wy1} Z M {wx0} {wy0} L {wx0} {wy1} L {wx1} {wy1} L {wx1} {wy0} Z" fill="{fr}" fill-rule="evenodd"/>')
    out.append(f'<path d="M 300 {wy0} L 300 {wy1} M {wx0} 300 L {wx1} 300" stroke="{fr}" stroke-width="9"/>')
    out.append(ink(f"M {wx0 - 18} {wy0 - 18} L {wx1 + 18} {wy0 - 18} L {wx1 + 18} {wy1} L {wx0 - 18} {wy1} Z", "#0A5A5A", 2, 2304, 1, 0.7))
    out.append(f'<path d="M {wx0} {wy0} L {wx1} {wy0} L {wx1} {wy1} L {wx0} {wy1} Z" fill="none" stroke="#0A5A5A" stroke-width="2"/>')
    # light falling on the wall
    out.append(f'<path d="M {wx1 + 18} {wy1} L 610 520 L 610 610 L {wx0 + 60} 610 L {wx0} {wy1} Z" fill="#FFE8C0" opacity="0.18"/>')
    # sill
    out.append(painted(D, [(wx0 - 40, wy1), (wx1 + 40, wy1), (wx1 + 50, wy1 + 22), (wx0 - 50, wy1 + 22)], ("#FFFFFF", "#F2E8E0", "#B8A8A0"), 2305, sk=0.2, angle=0, n=10, inkw=1.8, hi=0.3))
    # the nopal in its pot: old pads, a fresh new pad, tunas and a flower
    pcx, pb = 300, wy1 + 2
    out.append(nopal_pad(D, 300, 352, 96, 132, -4, 2306))
    out.append(nopal_pad(D, 244, 272, 76, 104, -28, 2307))
    out.append(nopal_pad(D, 362, 262, 74, 102, 22, 2308))
    out.append(nopal_pad(D, 386, 186, 40, 58, 30, 2309, young=True))
    for k, (x, y, a) in enumerate(((214, 214, -20), (238, 210, 4), (266, 214, 18))):
        out.append(painted(D, rot(blob_pts(x, y, 11, 15, 2310 + k, 0.05, 12), x, y, a), ("#FF8AB0", "#D8205A", "#7A0A30"), 2310 + k, sk=0.2, n=3, inkw=1.2, hi=0.5, hik=0.15))
    fx, fy = 334, 206
    for k in range(8):
        a = math.radians(-90 + (k - 3.5) * 22)
        out.append(painted(D, rot(blob_pts(fx + math.cos(a) * 14, fy + math.sin(a) * 14, 12, 6, 2315 + k, 0.1, 10), fx + math.cos(a) * 14, fy + math.sin(a) * 14, math.degrees(a)), AMAR, 2315 + k, sk=0.15, n=2, inkw=1, hi=0.5))
    out.append(f'<circle cx="{fx}" cy="{fy}" r="6" fill="#9AB83A"/>')
    out.append(clay_pot(D, pcx, pb, 150, 110, 2320, BARRO, neck=0.9, lip=0.95, handles=False, soot=False))
    out.append(sparkle(410, 168, 9, "#FFFFFF", 0.9))
    out.append(sparkle(430, 196, 5, "#FFFFFF", 0.8))
    # lettering
    out.append(letters(D, 300, 126, "¡échale ganas!", SERIF_IT, 86, "#FFFFFF", ["#FFFFFF", "#FFF0F4", "#FFF8E0"], 2330, max_w=460,
                       shadow="#9A1050", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 520, "TÚ PUEDES", "#7A0A3A", font=JOS, size=26, ls=10, line_w=48, gap=16, line="#18A8A0"))
    return finish_b(D, out, 2331)


# ================================================================ 23. ahorita — the talavera wall clock that never quite says when
@design("ahorita")
def ahorita():
    D = Doc2("mxah")
    out = [sky(D, [(0, "#2AB0A6"), (1, "#14807A")], 2401, 600, ["#5AD0C4", "#0A5A56", "#3AC0B4"], 120, angle=-84, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 320, 280, "#FFF6D8", 0.35))
    out.append(blooms(2402, ["#5AD0C4", "#0A5A56"], 8, (0, 0, 600, 600), (80, 160), (0.08, 0.14)))
    cx, cy, R = 300, 318, 156
    # nail and cord
    out.append(f'<path d="M 300 150 L {cx - 40} {cy - R + 20} M 300 150 L {cx + 40} {cy - R + 20}" stroke="#3A2418" stroke-width="2"/>')
    out.append(f'<circle cx="300" cy="150" r="4" fill="#3A2418"/>')
    out.append(cast(D, cx + 18, cy + 22, R + 6, R + 6, strength=0.35, seed=2403))
    # scalloped talavera rim
    sc = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        rr = R * (1 + 0.035 * math.cos(a * 24))
        sc.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    out.append(painted(D, sc, ("#FFFFFF", "#F8F2E4", "#C8BCA8"), 2404, sk=0.08, angle=-30, n=40, inkw=2.2, hi=0.4))
    for i in range(24):
        a = 2 * math.pi * i / 24
        x, y = cx + R * 0.9 * math.cos(a), cy + R * 0.9 * math.sin(a)
        out.append(f'<path d="{blob(x, y, R * 0.07, R * 0.045, 2405 + i, 0.15, 8, math.degrees(a) + 90)}" fill="{COBALT[1] if i % 2 else "#F2A41E"}"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, R * 0.8, R * 0.8, 0, 360, 40)[:-1]), COBALT[1], 3, 2406, 1, 0.9))
    # face: cream with a painted flower medallion
    out.append(f'<path d="{blob(cx, cy, R * 0.77, R * 0.77, 2407, 0.01, 30)}" fill="#FFFBF0"/>')
    for k in range(8):
        a = math.radians(k * 45)
        px, py = cx + math.cos(a) * R * 0.2, cy + math.sin(a) * R * 0.2
        out.append(f'<path d="{smooth_closed(rot(blob_pts(px, py, R * 0.15, R * 0.07, 2408 + k, 0.08, 10), px, py, k * 45))}" fill="{COBALT[0]}" opacity="0.55"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.08:.1f}" fill="#F2A41E" opacity="0.7"/>')
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = R * (0.66 if i % 5 == 0 else 0.7)
        out.append(f'<path d="M {cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0:.1f} L {cx + math.cos(a) * R * 0.74:.1f} {cy + math.sin(a) * R * 0.74:.1f}" stroke="{COBALT[2]}" stroke-width="{2.6 if i % 5 == 0 else 1.2}"/>')
    for n_, a in (("12", -90), ("3", 0), ("6", 90), ("9", 180)):
        x, y = cx + math.cos(math.radians(a)) * R * 0.53, cy + math.sin(math.radians(a)) * R * 0.53 + 9
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {CINZEL} font-size="28" fill="{COBALT[1]}">{n_}</text>')
    # hands: the hour hand settled, the minute hand a blur of 'ahorita'
    for k in range(5):
        a = math.radians(-60 + k * 18)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * R * 0.6:.1f} {cy + math.sin(a) * R * 0.6:.1f}" stroke="#2A1A10" stroke-width="3" opacity="{0.08 + k * 0.05:.2f}"/>')
    arc = [(cx + math.cos(math.radians(a)) * R * 0.48, cy + math.sin(math.radians(a)) * R * 0.48) for a in range(-64, 20, 6)]
    out.append(taper(arc, 2, 5, "#E6337A", 0.7))
    ah = math.radians(20)
    out.append(taper([(cx - math.cos(ah) * 18, cy - math.sin(ah) * 18), (cx + math.cos(ah) * R * 0.62, cy + math.sin(ah) * R * 0.62)], 6, 2, "#2A1A10"))
    hh = math.radians(-150)
    out.append(taper([(cx - math.cos(hh) * 14, cy - math.sin(hh) * 14), (cx + math.cos(hh) * R * 0.38, cy + math.sin(hh) * R * 0.38)], 9, 3, "#2A1A10"))
    out.append(f'<circle cx="{cx + math.cos(hh) * R * 0.3:.1f}" cy="{cy + math.sin(hh) * R * 0.3:.1f}" r="7" fill="none" stroke="#2A1A10" stroke-width="3"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#2A1A10"/><circle cx="{cx - 2}" cy="{cy - 2}" r="2.4" fill="#C8A878"/>')
    out.append(f'<path d="{blob(cx - R * 0.45, cy - R * 0.5, R * 0.25, R * 0.1, 2409, 0.2, 10, -40)}" fill="#FFFFFF" opacity="0.5"/>')
    # bougainvillea curling in from the corners for colour
    out.append(bugambilia(D, catmull([(-20, 470), (40, 470), (90, 500), (110, 560), (150, 610)], 4), 2410, 50))
    out.append(bugambilia(D, catmull([(620, 440), (560, 470), (520, 530), (500, 610)], 4), 2411, 50))
    # lettering
    out.append(letters(D, 300, 128, "ahorita", SERIF_IT, 104, "#FFF6D8", ["#FFFFFF", "#FFE8B8", "#FFF2D0"], 2412, max_w=360,
                       shadow="#0A3A3A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(f'<path d="{blob(300, 528, 200, 24, 2413, 0.06, 16)}" fill="#0A4A48" opacity="0.6"/>')
    out.append(label(300, 535, "AHORA · AHORITA · AHORITITA", JOS, 19, "#FFF2C8", ls=3, max_w=380))
    return finish_b(D, out, 2414, "#FFFFFF", 0.5)


# ================================================================ 24. ¡qué padre! — three paletas de fruta against a sunburst
def paleta(D, cx, cy, w, h, ang, seed, body, chunks, coat=None, bite=False, specks_=None):
    """A fruit paleta: rounded bar on a wooden stick, frosty, fruit pieces frozen inside."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy + h * 0.55:.1f})">']
    out.append(painted(D, rect_pts(cx - w * 0.12, cy + h * 0.3, cx + w * 0.12, cy + h * 0.95, 8, seed, 0.3), ("#F2D8A8", "#D8B07A", "#8A6A3A"), seed, sdir=(1, 0), sk=0.25, angle=-90, n=5, inkw=1.4, hi=0.4))
    pts = []
    for t in range(0, 181, 15):
        a = math.radians(180 + t)
        pts.append((cx + math.cos(a) * w / 2, cy - h / 2 + w / 2 + math.sin(a) * w / 2))
    pts += [(cx + w / 2, cy + h * 0.44), (cx + w * 0.4, cy + h / 2), (cx - w * 0.4, cy + h / 2), (cx - w / 2, cy + h * 0.44)]
    if bite:
        bx, by, br = cx + w * 0.42, cy - h * 0.36, w * 0.3
        newp = []
        for x, y in pts:
            if math.hypot(x - bx, y - by) < br:
                a = math.atan2(y - by, x - bx)
                x, y = bx + math.cos(a) * br, by + math.sin(a) * br
            newp.append((x, y))
        pts = newp
    d = smooth_closed(pts)
    out.append(painted(D, pts, body, seed + 1, sdir=(0.6, 0.6), sk=0.18, angle=-90, n=30, inkw=2, hi=0.45, hik=0.08))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for _ in range(int(w * h / 500)):
        x, y = cx + rnd.uniform(-w * 0.4, w * 0.4), cy + rnd.uniform(-h * 0.4, h * 0.42)
        c = rnd.choice(chunks)
        inner.append(painted(D, blob_pts(x, y, rnd.uniform(5, 10), rnd.uniform(4, 8), rnd.randint(0, 9999), 0.25, 8, rnd.uniform(0, 180)), c, rnd.randint(0, 9999), sk=0.2, n=2, inkw=0.8, inkop=0.4, hi=0.5))
    if specks_:
        for _ in range(140):
            inner.append(f'<circle cx="{cx + rnd.uniform(-w / 2, w / 2):.1f}" cy="{cy + rnd.uniform(-h / 2, h * 0.1):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="{rnd.choice(specks_)}" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    if coat:
        drip = [(cx - w * 0.52, cy - h * 0.5)] + [(cx - w / 2 + i * w / 8, cy - h * 0.18 + (18 if i % 2 else 0) + rnd.uniform(-4, 4)) for i in range(9)] + [(cx + w * 0.52, cy - h * 0.5)]
        inner.append(painted(D, drip, coat, seed + 5, sk=0.2, n=10, inkw=0, hi=0.5))
    for _ in range(30):
        inner.append(f'<circle cx="{cx + rnd.uniform(-w / 2, w / 2):.1f}" cy="{cy + rnd.uniform(-h / 2, h / 2):.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    inner.append(taper([(cx - w * 0.3, cy - h * 0.3), (cx - w * 0.34, cy + h * 0.3)], 6, 2, "#FFFFFF", 0.55))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append("</g>")
    return "".join(out)


@design("que-padre")
def que_padre():
    D = Doc2("mxqp")
    out = [f'<rect width="600" height="600" fill="#F6A21E"/>']
    cx, cy = 300, 360
    for k in range(24):
        a0, a1 = math.radians(k * 15), math.radians(k * 15 + 7.5)
        out.append(f'<path d="M {cx} {cy} L {cx + math.cos(a0) * 700:.1f} {cy + math.sin(a0) * 700:.1f} L {cx + math.cos(a1) * 700:.1f} {cy + math.sin(a1) * 700:.1f} Z" fill="#E6337A" opacity="0.85"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), ["#FFFFFF", "#9A1050", "#FFD27A"], 2501, n=120, angle=-35, length=(40, 140), width=(3, 8), opacity=(0.05, 0.14)))
    out.append(soft_glow(D, cx, cy, 260, "#FFF2C0", 0.6))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="#FFF0C8" opacity="0.3"/>')
    out.append(hg.confetti(2502, 50, (40, 210, 560, 560), ["#FFFFFF", "#18A8A0", "#F6C21C", "#7A42B8"], avoid=((140, 200, 460, 560),), s=(5, 10)))
    out.append(cast(D, cx + 10, 560, 200, 16, strength=0.35, seed=2503))
    out.append(paleta(D, 196, 350, 108, 186, -22, 2504, ("#FFC07A", "#F6862A", "#A84A0A"), [("#FFE07A", "#F6B42A", "#B8780A")],
                      coat=("#E87A5A", "#B8281A", "#6A0A06"), bite=True, specks_=["#C8281A", "#8A1408"]))
    out.append(paleta(D, 404, 350, 108, 186, 22, 2505, ("#D8F4B8", "#9ADA7A", "#4E8A3A"), [("#E8FFC8", "#B8E890", "#6AA84A")], specks_=["#4E8A3A", "#2E6A2A"]))
    out.append(paleta(D, 300, 326, 116, 200, 0, 2506, ("#FFD0DC", "#F6A0B8", "#B8506A"), [("#FF8A9A", "#E8304A", "#9A1020"), ("#FFFFFF", "#FFF4F4", "#E8C8C8")]))
    # strawberry and lime slices at the base
    out.append(lime_wedge(D, 128, 520, 32, 2507, -10))
    for k, (x, y) in enumerate(((462, 520), (500, 530))):
        sp = [(x - 18, y - 12), (x + 18, y - 12), (x + 12, y + 8), (x, y + 20), (x - 12, y + 8)]
        out.append(painted(D, sp, ("#FF8A9A", "#E8304A", "#9A1020"), 2508 + k, sk=0.2, n=4, inkw=1.4, hi=0.5))
        out.append(specks(2510 + k, (x - 12, y - 8, x + 12, y + 12), ["#FFE07A"], 10, (0.9, 1.4), (0.9, 1)))
        for j in range(4):
            out.append(leaf_simple(D, x, y - 12, 12, 4, -150 + j * 40, ("#9ACB6A", "#3E8A44", "#1E5A2A"), 2512 + j + k * 4, vein=False, inkw=0.8))
    # lettering
    out.append(letters(D, 300, 140, "¡qué padre!", SERIF_IT, 108, "#FFFFFF", ["#FFFFFF", "#FFF0F4", "#FFF8E0"], 2520, max_w=460,
                       shadow="#7A0A3A", soff=(0.025, 0.045), angle=-40, hi="#FFFFFF"))
    out.append(f'<path d="{hg.org_rect(150, 164, 300, 38, 2521, 0.6, 14, 4)}" fill="#18A8A0"/>')
    out.append(label(300, 190, "PALETAS DE FRUTA", JOS, 20, "#FFFFFF", ls=4, max_w=272))
    return finish_b(D, out, 2522, "#FFFFFF", 0.5)


# ================================================================ 25. con cariño — a bouquet of crepe-paper flowers tied with a rebozo ribbon
def paper_flower(D, cx, cy, r, pal, seed, layers=4):
    """Crepe-paper flor: ruffled rings, crinkled with fine radial creases, darker towards the heart."""
    rnd = random.Random(seed)
    out = [cast(D, cx + r * 0.12, cy + r * 0.16, r * 1.02, r * 0.98, strength=0.3, seed=seed)]
    for L in range(layers):
        rr = r * (1 - L * 0.22)
        pts = []
        n = 44
        for i in range(n):
            a = 2 * math.pi * i / n
            k = 1 + 0.09 * math.sin(a * (7 + L)) + 0.05 * math.sin(a * 13 + L) + rnd.uniform(-0.03, 0.03)
            pts.append((cx + math.cos(a) * rr * k, cy + math.sin(a) * rr * k * 0.94))
        c = (lt(pal[1], 0.25 - L * 0.05), mix(pal[1], pal[2], L * 0.12), pal[2])
        out.append(painted(D, pts, c, seed + L, sdir=(0.6, 0.7), sk=0.14, angle=-40, n=int(rr * 0.6) + 4, inkw=1.0 if L == 0 else 0, inkop=0.4, hi=0.35, hik=0.06))
        for i in range(int(rr * 0.9)):
            a = rnd.uniform(0, 6.28)
            r0, r1 = rr * rnd.uniform(0.3, 0.6), rr * rnd.uniform(0.8, 1.02)
            out.append(f'<path d="M {cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0 * 0.94:.1f} L {cx + math.cos(a) * r1:.1f} {cy + math.sin(a) * r1 * 0.94:.1f}" stroke="{rnd.choice([dk(pal[1], 0.25), lt(pal[1], 0.4)])}" stroke-width="{rnd.uniform(0.7, 1.4):.1f}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.16, r * 0.15, seed + 9, 0.2, 10)}" fill="{dk(pal[2], 0.25)}"/>')
    out.append(specks(seed, (cx - r * 0.12, cy - r * 0.12, cx + r * 0.12, cy + r * 0.12), ["#FFE07A", "#FFF4C0"], 8, (1, 2), (0.8, 1)))
    return "".join(out)


def rebozo_band(D, pts, w, seed, cols=("#2A1A4A", "#E6337A", "#F6C21C", "#18A8A0")):
    """A rebozo-striped ribbon following pts: fine woven stripes and an ikat dash pattern."""
    out = []
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    d = smooth_closed(left + right[::-1])
    out.append(f'<path d="{d}" fill="{cols[0]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k, f in enumerate((-0.36, -0.2, 0.0, 0.2, 0.36)):
        line = [((l[0] + r_[0]) / 2 + (l[0] - r_[0]) * f, (l[1] + r_[1]) / 2 + (l[1] - r_[1]) * f) for l, r_ in zip(left, right)]
        inner.append(pline(line, cols[1 + k % 3], max(1.4, w * 0.08), seed + k, 0.95, 1))
    mid = [((l[0] + r_[0]) / 2, (l[1] + r_[1]) / 2) for l, r_ in zip(left, right)]
    inner.append(f'<path d="{smooth_open(mid)}" stroke="#FFFFFF" stroke-width="{w * 0.12:.1f}" stroke-dasharray="4 5" fill="none" opacity="0.85"/>')
    inner.append(shade_over(D, d, "#000000", 0.3, 0, 0, 0, 1, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, INK, 1.2, seed, 1, 0.6))
    return "".join(out)


@design("con-carino")
def con_carino():
    D = Doc2("mxcc")
    out = [paper(D.nid(), "#F8EADC", FLECK, 2601)]
    out.append(blooms(2602, ["#F8B8D0", "#FFD8A0", "#B8E8E0"], 8, (40, 160, 560, 560), (110, 190), (0.14, 0.24)))
    # the bouquet: stems in kraft paper, flowers fanned above
    out.append(cast(D, 310, 560, 120, 14, strength=0.35, seed=2603))
    for k in range(9):
        a = math.radians(-90 + (k - 4) * 9)
        out.append(taper([(300, 520), (300 + math.cos(a) * 200, 520 + math.sin(a) * 200)], 4, 3, "#4E8A34"))
    for k, (x, y, a) in enumerate(((176, 300, -150), (424, 300, -30), (150, 380, 170), (452, 384, 10), (220, 250, -120), (382, 250, -60))):
        out.append(leaf_simple(D, x, y, 70, 18, a, ("#9ACB6A", "#3E8A44", "#1E5A2A"), 2604 + k, inkw=1.2))
    flowers = [(300, 236, 64, ROSA), (196, 300, 56, MARI), (404, 300, 56, MORADO), (246, 360, 50, AMAR), (356, 362, 52, TURQ),
               (142, 360, 40, ("#FFC0C8", "#F26A7A", "#A82A3A")), (458, 360, 40, ROSA), (300, 318, 44, CHILE), (230, 200, 34, TURQ), (372, 196, 36, AMAR)]
    for k, (x, y, r, pal) in enumerate(sorted(flowers, key=lambda f: f[1])):
        out.append(paper_flower(D, x, y, r, pal, 2610 + k * 7))
    # kraft paper cone
    cone = poly_pts([(166, 372), (300, 396), (436, 372), (330, 560), (270, 560)], 16, 2680, 0.6)
    out.append(painted(D, cone, ("#F2D8A8", "#D8AE74", "#8A6236"), 2680, sdir=(0.9, 0.3), sk=0.12, angle=-70, n=30, inkw=2, hi=0.4))
    flap = poly_pts([(166, 372), (300, 396), (276, 560), (270, 560)], 16, 2681, 0.5)
    out.append(painted(D, flap, ("#E8C890", "#C89A60", "#7A522A"), 2681, sk=0.12, angle=-70, n=12, inkw=1.4, hi=0.3))
    out.append(pline([(166, 372), (232, 382), (300, 396)], "#FFF2D8", 2, 2679, 0.8, 1))
    for x0, x1 in ((236, 284), (340, 312), (396, 324)):
        out.append(pline([(x0, 396), (x1, 548)], "#A8804A", 1.3, x0, 0.6, 1))
    # rebozo ribbon bow
    out.append(rebozo_band(D, catmull([(214, 470), (300, 480), (386, 470)], 6), 22, 2682))
    for sg in (-1, 1):
        loop = catmull([(300, 476), (300 + sg * 40, 440), (300 + sg * 70, 456), (300 + sg * 46, 488), (300, 480)], 5)
        out.append(rebozo_band(D, loop, 18, 2683 + sg))
        tail = catmull([(300, 482), (300 + sg * 24, 520), (300 + sg * 40, 556)], 5)
        out.append(rebozo_band(D, tail, 16, 2685 + sg))
        for j in range(6):
            ex, ey = tail[-1]
            out.append(f'<path d="M {ex - 6 + j * 2.4:.1f} {ey + 4:.1f} l {sg * 1.5:.1f} 12" stroke="{["#E6337A", "#F6C21C", "#18A8A0"][j % 3]}" stroke-width="1.6"/>')
    out.append(painted(D, blob_pts(300, 478, 14, 12, 2687, 0.05, 10), ("#5A4A7A", "#2A1A4A", "#140A2A"), 2687, sk=0.2, n=3, inkw=1.2, hi=0.4))
    # a little paper tag on a string
    out.append(pline([(330, 480), (380, 500), (424, 504)], "#8A6A4A", 1.4, 2688, 1, 1))
    tag = rot([(424, 488), (500, 488), (510, 504), (500, 520), (424, 520)], 424, 504, 8)
    out.append(painted(D, tag, ("#FFFDF4", "#F6EEDC", "#C8B894"), 2689, sk=0.15, n=6, inkw=1.4, hi=0.3))
    out.append(p_heart_small(462, 506, 8, ROSA[1]))
    # lettering
    out.append(letters(D, 300, 120, "con cariño", SERIF_IT, 104, "#C8205A", ["#E6337A", "#8A0A3A", "#F05A90"], 2690, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB0CC"))
    out.append(ruled(300, 160, "FLORES DE PAPEL PARA TI", "#7A4A2A", font=JOS, size=18, ls=5, line_w=24, gap=10, line="#18A8A0"))
    return finish_b(D, out, 2691)


def p_heart_small(cx, cy, s, col):
    return f'<path d="{smooth_closed(heart_d(cx, cy, s))}" fill="{col}"/>'


# ================================================================ 26. la familia es primero — Sunday dinner in the backyard, string lights on
@design("la-familia-es-primero")
def la_familia_es_primero():
    D = Doc2("mxfp")
    out = [sky(D, [(0, "#4A3A8A"), (0.45, "#B8689A"), (0.8, "#F2A07A"), (1, "#F8C890")], 2701, 600, ["#7A5AAA", "#F2B08A", "#3A2A6A"], 70, sop=(0.06, 0.14))]
    rnd = random.Random(2702)
    for _ in range(20):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 140):.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # the house wall behind: a lit window and the back door
    out.append(painted(D, rect_pts(-10, 250, 610, 470, 30, 2703, 0.5), ("#F2B8A0", "#D8907A", "#8A4A3A"), 2703, sk=0.08, angle=-88, n=40, inkw=1.6, hi=0.2))
    out.append(tile_roof(D, [(-20, 238), (620, 238), (620, 262), (-20, 262)], 2704, rows=2, cols=24))
    for x in (90, 470):
        out.append(f'<path d="{hg.org_rect(x, 290, 70, 80, 2705 + x, 0.4, 10, 3)}" fill="#FFD27A"/>')
        out.append(D.glow(x + 35, 330, 90, "#FFD070", 0.5))
        out.append(f'<path d="M {x + 35} 290 L {x + 35} 370 M {x} 330 L {x + 70} 330" stroke="#5A3A2A" stroke-width="4"/>')
        out.append(f'<path d="{hg.org_rect(x - 6, 284, 82, 92, 2706 + x, 0.4, 10, 3)}" fill="none" stroke="#1E7A6A" stroke-width="6"/>')
    # lemon tree at the left edge
    out.append(taper([(36, 470), (40, 360)], 14, 8, "#5A3A22"))
    out.append(dab_crown(D, 46, 320, 80, 70, [("#9ACB6A", "#4E8A34", "#24501A"), ("#B8D88A", "#6E9A44", "#3A6A2A")], 2707, n=90, size=(6, 11), inkw=0))
    for k in range(9):
        out.append(painted(D, blob_pts(rnd.uniform(0, 110), rnd.uniform(270, 380), 6, 7, 2708 + k, 0.05, 10), ("#FFF2A0", "#F6D21C", "#A8860A"), 2708 + k, sk=0.2, n=2, inkw=0.8, hi=0.5))
    # string lights zigzagging over the yard
    for (x0, y0, x1, y1, sag) in ((-20, 180, 620, 200, 40), (-20, 230, 620, 214, 34)):
        pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)) for t in [i / 30 for i in range(31)]]
        out.append(pline(pts, "#2A1A2A", 1.4, int(y0), 1, 1))
        for k, (x, y) in enumerate(pts[1::2]):
            out.append(D.glow(x, y + 6, 18, "#FFE0A0", 0.55))
            out.append(f'<path d="{blob(x, y + 6, 3.6, 4.6, int(x + y), 0.05, 8)}" fill="#FFF4C8"/>')
    # the patio and the long table with an oilcloth
    out.append(f'<rect y="470" width="600" height="140" fill="{D.lin([(0, "#C88A6A"), (1, "#8A5A44")])}"/>')
    for k in range(-2, 12):
        out.append(f'<path d="M {k * 60} 470 L {k * 80 - 120} 610" stroke="#6A3A2A" stroke-width="1.6" opacity="0.4"/>')
    for y in (500, 540, 588):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#6A3A2A" stroke-width="1.6" opacity="0.4"/>')
    # the family seated behind the table
    from figures import person
    fam = [(150, 1, "f", 176, False), (222, 1, "m", 188, False), (292, 1, "f", 150, True), (356, -1, "m", 192, False), (426, -1, "f", 176, False), (490, -1, "m", 160, True)]
    for k, (x, f, form, h, ch) in enumerate(fam):
        pal = {"form": form, "season": "summer"}
        if k == 4:
            pal.update(hair="#D8D0C8", hair_style="bun")
        out.append(person(x, 506, h, "sit_front", f, pal, 2710 + k, rim="#FFD8A0", child=ch))
    # table (in front of them)
    out.append('<g transform="translate(0 40)">')
    top = [(110, 430), (500, 430), (528, 470), (82, 470)]
    pat = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/><circle cx="{x + 4}" cy="{y - 3}" r="3" fill="#2E9A4C"/>' for x, y, c in ((8, 8, "#E6337A"), (28, 22, "#F6C21C"), (12, 32, "#F5961E")))
    hule = D.pattern(40, 40, f'<rect width="40" height="40" fill="#FFF8EE"/>{pat}')
    out.append(f'<path d="{pd(top)}" fill="{hule}"/>')
    out.append(f'<path d="{pd([(82, 470), (528, 470), (532, 506), (78, 506)])}" fill="{hule}"/>')
    out.append(f'<path d="{pd([(82, 470), (528, 470), (532, 506), (78, 506)])}" fill="#3A1A10" opacity="0.18"/>')
    out.append(ink(pd(top), INK, 1.6, 2716, 1, 0.6))
    for x in (100, 510):
        out.append(f'<rect x="{x - 4}" y="506" width="8" height="40" fill="#5A3420"/>')
    # dishes: a cazuela, a tortillero, a pitcher of agua de jamaica, plates
    out.append(clay_pot(D, 222, 452, 70, 26, 2717, BARRO, neck=1, lip=1, handles=True, deco=None, soot=False, inside="#7A3A10"))
    out.append(steam(222, 420, 30, 2718, "#FFFFFF", 2, 16, 4, 0.55))
    out.append(painted(D, ell_pts(304, 446, 30, 10, 0, 360, 16)[:-1], ROSA, 2719, sk=0.2, n=4, inkw=1.2, hi=0.4))
    out.append(painted(D, ell_pts(304, 440, 22, 6, 0, 360, 14)[:-1], ("#FFF2C0", "#EED690", "#B8964A"), 2720, sk=0.15, n=3, inkw=1, hi=0.4))
    jx = 390
    out.append(f'<path d="{pd([(jx - 16, 404), (jx + 16, 404), (jx + 20, 450), (jx - 20, 450)])}" fill="#C81E3A" opacity="0.85"/>')
    out.append(f'<path d="{pd([(jx - 18, 398), (jx + 18, 398), (jx + 22, 452), (jx - 22, 452)])}" fill="#E8F4F8" opacity="0.35" stroke="#8AA8B8" stroke-width="1.4"/>')
    out.append(f'<path d="M {jx + 20} 410 q 14 4 10 20 q -2 8 -12 8" stroke="#8AA8B8" stroke-width="3" fill="none"/>')
    out.append(f'<path d="M {jx - 12} 406 L {jx - 10} 446" stroke="#FFFFFF" stroke-width="2.4" opacity="0.7"/>')
    for k, x in enumerate((150, 452)):
        out.append(f'<ellipse cx="{x}" cy="452" rx="24" ry="7" fill="#FFFFFF" stroke="#C8C0B8" stroke-width="1.2"/>')
    out.append("</g>")
    # a football waiting under the table
    out.append(painted(D, blob_pts(70, 552, 16, 15, 2721, 0.03, 12), WHITE, 2721, sk=0.25, n=4, inkw=1.4, hi=0.5))
    out.append(f'<path d="{blob(70, 552, 5, 5, 2722, 0.1, 6)}" fill="#2A2A30"/>')
    for k in range(5):
        a_ = math.radians(k * 72 - 90)
        out.append(f'<path d="{blob(70 + math.cos(a_) * 12, 552 + math.sin(a_) * 11, 3, 3, 2723 + k, 0.2, 6)}" fill="#2A2A30"/>')
    # lettering
    out.append(letters(D, 300, 112, "la familia", SERIF_IT, 94, "#FFF2D8", ["#FFFFFF", "#FFE2C0", "#FFF6E0"], 2730, max_w=420,
                       shadow="#2A1A4A", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 300, 158, "ES PRIMERO", BEBAS, 42, "#F6C21C", ["#FFE07A", "#D89A10"], 2731, ls=10, max_w=300, wob=0.4, shadow="#2A1A4A"))
    return finish_b(D, out, 2732, "#FFFFFF", 0.5)


# ================================================================ 27. la chancla — an original lotería-style card
def chancla(D, cx, cy, L, ang, seed, sole=("#FF9AC8", "#E6337A", "#9A1050"), strap=("#FFF0A0", "#F6C21C", "#B8860A")):
    """A rubber flip-flop seen from above: sole with a worn footprint, a Y strap and a toe post."""
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">']
    w = L * 0.36
    sp = [(cx, cy - L / 2), (cx + w * 0.5, cy - L * 0.44), (cx + w * 0.56, cy - L * 0.2), (cx + w * 0.4, cy + L * 0.06), (cx + w * 0.44, cy + L * 0.3),
          (cx + w * 0.36, cy + L * 0.48), (cx, cy + L * 0.52), (cx - w * 0.36, cy + L * 0.48), (cx - w * 0.42, cy + L * 0.3), (cx - w * 0.36, cy + L * 0.06),
          (cx - w * 0.5, cy - L * 0.2), (cx - w * 0.46, cy - L * 0.44)]
    out.append(f'<path d="{smooth_closed(shift(sp, 3, 6))}" fill="{dk(sole[2], 0.3)}"/>')
    out.append(painted(D, sp, sole, seed, sdir=(0.6, 0.6), sk=0.15, angle=-90, n=20, inkw=2, hi=0.4))
    out.append(f'<path d="{smooth_closed([(x + (cx - x) * 0.12, y + (cy - y) * 0.06) for x, y in sp])}" fill="none" stroke="{lt(sole[0], 0.3)}" stroke-width="2" opacity="0.7"/>')
    # worn footprint
    out.append(f'<path d="{blob(cx, cy + L * 0.28, w * 0.26, L * 0.13, seed + 1, 0.1, 10)}" fill="{sole[2]}" opacity="0.25"/>')
    out.append(f'<path d="{blob(cx + w * 0.04, cy - L * 0.2, w * 0.3, L * 0.16, seed + 2, 0.1, 10)}" fill="{sole[2]}" opacity="0.25"/>')
    # strap
    post = (cx + w * 0.02, cy - L * 0.3)
    for sg in (-1, 1):
        st = catmull([post, (cx + sg * w * 0.3, cy - L * 0.14), (cx + sg * w * 0.42, cy + L * 0.04)], 5)
        out.append(taper(st, w * 0.2, w * 0.24, strap[2]))
        out.append(taper([(x - 1, y - 1) for x, y in st], w * 0.16, w * 0.2, strap[1]))
        out.append(taper([(x - 2, y - 2) for x, y in st], w * 0.05, w * 0.06, strap[0], 0.8))
    out.append(f'<circle cx="{post[0]:.1f}" cy="{post[1]:.1f}" r="{w * 0.12:.1f}" fill="{strap[2]}"/><circle cx="{post[0] - 1:.1f}" cy="{post[1] - 1:.1f}" r="{w * 0.06:.1f}" fill="{strap[0]}"/>')
    out.append("</g>")
    return "".join(out)


def loteria_card(D, x0, y0, x1, y1, num, name, art, frame_col, seed, name_font=SERIF_IT, name_size=46):
    """An original lotería-style card: off-white stock, black keyline, a number in the corner, a framed picture
    and the name lettered in a panel underneath."""
    out = [cast(D, (x0 + x1) / 2 + 10, y1 + 2, (x1 - x0) * 0.52, 12, strength=0.4, seed=seed)]
    out.append(painted(D, rect_pts(x0, y0, x1, y1, 24, seed, 0.5), ("#FFFDF4", "#F8F0DE", "#C8B894"), seed, sdir=(0.3, 1), sk=0.04, angle=0, n=30, inkw=1.6, hi=0.2))
    ix0, iy0, ix1, iy1 = x0 + 16, y0 + 16, x1 - 16, y1 - 86
    out.append(f'<path d="{hg.org_rect(x0 + 8, y0 + 8, x1 - x0 - 16, y1 - y0 - 16, seed + 1, 0.5, 20, 2)}" fill="none" stroke="#1A1210" stroke-width="2.6"/>')
    cid = D.clip(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}"/>')
    out.append(f'<g {cid}>{art(ix0, iy0, ix1, iy1)}</g>')
    out.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="none" stroke="#1A1210" stroke-width="2.4"/>')
    # number badge
    out.append(f'<path d="{blob(ix0 + 26, iy0 + 26, 22, 22, seed + 2, 0.04, 12)}" fill="#FFFDF4" stroke="#1A1210" stroke-width="2.2"/>')
    out.append(label(ix0 + 26, iy0 + 35, num, CINZEL, 24, "#1A1210"))
    # name panel
    out.append(f'<path d="{hg.org_rect(ix0, iy1 + 10, ix1 - ix0, y1 - 26 - iy1 - 10, seed + 3, 0.5, 14, 2)}" fill="{frame_col}"/>')
    out.append(label((x0 + x1) / 2, y1 - 40, name, name_font, name_size, "#FFFDF4", max_w=ix1 - ix0 - 30, extra=' stroke="#1A1210" stroke-width="1.2" paint-order="stroke"'))
    return "".join(out)


@design("la-chancla")
def la_chancla():
    D = Doc2("mxlch")
    # background: a woven-plastic mercado-bag pattern in pink and white, bleeding off
    tile = "".join(f'<rect x="{i * 10}" y="0" width="5" height="40" fill="#FFFFFF" opacity="0.5"/>' for i in range(4)) + "".join(f'<rect x="0" y="{i * 10}" width="40" height="5" fill="#9A1050" opacity="0.25"/>' for i in range(4))
    out = [f'<rect width="600" height="600" fill="#E6337A"/>', f'<rect width="600" height="600" fill="{D.pattern(40, 40, tile)}"/>']
    out.append(soft_glow(D, 300, 300, 330, "#FFE8F0", 0.4))

    def art(x0, y0, x1, y1):
        a = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#8AD0F0"/>']
        cx, cy = (x0 + x1) / 2 + 20, (y0 + y1) / 2
        for k in range(18):
            a0, a1 = math.radians(k * 20), math.radians(k * 20 + 10)
            a.append(f'<path d="M {cx} {cy} L {cx + math.cos(a0) * 500:.1f} {cy + math.sin(a0) * 500:.1f} L {cx + math.cos(a1) * 500:.1f} {cy + math.sin(a1) * 500:.1f} Z" fill="#FFF4C0" opacity="0.5"/>')
        # speed lines and the curved flight path from the lower left
        path = catmull([(x0 - 20, y1 - 30), (x0 + 90, y1 - 100), (cx - 60, cy + 20)], 6)
        a.append(f'<path d="{smooth_open(path)}" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-dasharray="14 10" stroke-linecap="round" opacity="0.9"/>')
        for k in range(5):
            yy = cy + 50 + k * 16
            a.append(taper([(cx - 210 + k * 10, yy + 40), (cx - 70, yy - 10)], 1, 5, "#1A6A9A", 0.5))
        a.append(chancla(D, cx + 10, cy - 6, 220, 38, 2801))
        for k, (sx, sy, r) in enumerate(((cx + 110, cy - 110, 14), (cx + 140, cy - 60, 9), (cx - 120, cy - 120, 11), (cx + 120, cy + 60, 8))):
            a.append(sparkle(sx, sy, r, "#FFFFFF", 0.95))
        a.append(f'<text x="{cx + 92:.1f}" y="{cy - 124:.1f}" text-anchor="middle" {ANTON} font-size="34" fill="#D2352A" stroke="#FFFFFF" stroke-width="5" paint-order="stroke" transform="rotate(14 {cx + 92:.1f} {cy - 124:.1f})">¡ZAS!</text>')
        return "".join(a)
    out.append(loteria_card(D, 92, 48, 508, 556, "23", "La Chancla", art, "#1E3F9A", 2802))
    out.append(label(300, 540, "LA QUE NUNCA FALLA", JOS, 16, "#1A1210", ls=3, max_w=380))
    return finish_b(D, out, 2803)


# ================================================================ 28. el aguacate — a lotería card on the table, frijoles as markers
def avocado_half(D, cx, cy, s, seed, rot_=0, pit=True):
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">']
    shape = [(cx, cy - s), (cx + s * 0.42, cy - s * 0.82), (cx + s * 0.56, cy - s * 0.3), (cx + s * 0.7, cy + s * 0.25), (cx + s * 0.55, cy + s * 0.7),
             (cx, cy + s * 0.9), (cx - s * 0.55, cy + s * 0.7), (cx - s * 0.7, cy + s * 0.25), (cx - s * 0.56, cy - s * 0.3), (cx - s * 0.42, cy - s * 0.82)]
    out.append(cast(D, cx + s * 0.15, cy + s * 0.2, s * 0.8, s * 0.95, strength=0.35, seed=seed))
    out.append(painted(D, shape, ("#5A7A2A", "#2E4A14", "#142208"), seed, sk=0.15, n=10, inkw=2, hi=0.3))
    inner = [(x + (cx - x) * 0.08, y + (cy + s * 0.1 - y) * 0.08) for x, y in shape]
    out.append(f'<path d="{smooth_closed(inner)}" fill="#D8E87A"/>')
    inner2 = [(x + (cx - x) * 0.22, y + (cy + s * 0.15 - y) * 0.22) for x, y in shape]
    out.append(f'<path d="{smooth_closed(inner2)}" fill="#F2F4A8"/>')
    out.append(strokes(D.nid(), smooth_closed(inner), bbox(inner), ["#FFFFD0", "#B8D060"], seed + 1, n=24, angle=-80, length=(s * 0.1, s * 0.3), width=(1, 3), opacity=(0.2, 0.4)))
    if pit:
        out.append(painted(D, blob_pts(cx, cy + s * 0.25, s * 0.32, s * 0.34, seed + 2, 0.04, 14), ("#C8885A", "#8A4A22", "#3A1A08"), seed + 2, sdir=(0.6, 0.7), sk=0.25, n=8, inkw=1.6, hi=0.5, hik=0.12))
        out.append(f'<path d="{blob(cx - s * 0.1, cy + s * 0.12, s * 0.09, s * 0.06, seed + 3, 0.2, 8, -30)}" fill="#FFE2C0" opacity="0.7"/>')
    out.append("</g>")
    return "".join(out)


def frijol(D, cx, cy, s, seed, ang):
    out = [f'<path d="{blob(cx + 2, cy + 3, s, s * 0.62, seed, 0.06, 10, ang)}" fill="#1A0A04" opacity="0.3"/>']
    out.append(painted(D, rot(blob_pts(cx, cy, s, s * 0.62, seed, 0.06, 10), cx, cy, ang), ("#B8786A", "#7A3A2E", "#3A1410"), seed, sk=0.25, n=2, inkw=1, hi=0.5, hik=0.15))
    out.append(f'<path d="{blob(cx - s * 0.25, cy - s * 0.2, s * 0.25, s * 0.1, seed + 1, 0.2, 6, ang)}" fill="#FFFFFF" opacity="0.5"/>')
    return "".join(out)


@design("el-aguacate")
def el_aguacate():
    D = Doc2("mxlag")
    out = [wood_planks(D, -10, 610, 2901, ("#E8B884", "#B8804A", "#6A4220"), 5)]
    out.append(soft_glow(D, 260, 240, 360, "#FFF2D0", 0.35))
    # another card peeking out underneath, face down (patterned back)
    back = rot([(380, 300), (580, 300), (580, 560), (380, 560)], 480, 430, 16)
    back_pat = D.pattern(20, 20, '<rect width="20" height="20" fill="#1E3F9A"/><circle cx="10" cy="10" r="4" fill="#F6C21C"/><circle cx="0" cy="0" r="3" fill="#E6337A"/><circle cx="20" cy="20" r="3" fill="#E6337A"/>')
    out.append(cast(D, 490, 440, 130, 150, strength=0.3, seed=2902))
    out.append(f'<path d="{hg.org_poly(back, 2903, 0.6, 16, 3)}" fill="{back_pat}" stroke="#FFFDF4" stroke-width="8"/>')

    def art(x0, y0, x1, y1):
        a = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#F6D44A"/>']
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 10
        a.append(blooms(2904, ["#FFE88A", "#F2B82A"], 5, (x0, y0, x1, y1), (60, 110), (0.25, 0.4)))
        # branch with leaves and a whole avocado hanging, the halves in front
        a.append(taper(catmull([(x0 - 10, y0 + 40), (cx - 40, y0 + 52), (cx + 60, y0 + 40), (x1 + 10, y0 + 56)], 5), 8, 5, "#5A3A22"))
        for k, (lx, ly, ang) in enumerate(((cx - 120, y0 + 46, 150), (cx - 60, y0 + 52, 60), (cx + 20, y0 + 46, 120), (cx + 100, y0 + 48, 40), (cx + 150, y0 + 52, 130))):
            a.append(leaf_simple(D, lx, ly, 70, 18, ang, ("#8ACB6A", "#2E7A3A", "#14401E"), 2905 + k, inkw=1.2))
        a.append(taper([(cx + 60, y0 + 44), (cx + 66, y0 + 80)], 3, 2, "#5A3A22"))
        whole = blob_pts(cx + 68, y0 + 124, 34, 46, 2910, 0.05, 14)
        a.append(painted(D, whole, ("#4A6A2A", "#2A3E14", "#101A06"), 2910, sdir=(0.6, 0.6), sk=0.25, n=12, inkw=1.8, hi=0.35, hik=0.1))
        a.append(specks(2911, (cx + 40, y0 + 90, cx + 96, y0 + 160), ["#6A8A3A", "#1A2A0A"], 30, (0.8, 1.8), (0.5, 0.9)))
        a.append(avocado_half(D, cx - 52, cy + 40, 92, 2912, -12))
        a.append(avocado_half(D, cx + 56, cy + 64, 76, 2913, 16, pit=False))
        return "".join(a)
    out.append('<g transform="rotate(-4 280 300)">')
    out.append(loteria_card(D, 70, 44, 470, 546, "12", "El Aguacate", art, "#2E7A3A", 2914))
    out.append("</g>")
    # frijoles used as markers, scattered
    rnd = random.Random(2915)
    for k, (x, y) in enumerate(((508, 120), (526, 150), (540, 110), (494, 160), (520, 196), (548, 240))):
        out.append(frijol(D, x, y, 9, 2916 + k, rnd.uniform(0, 180)))
    out.append(frijol(D, 120, 160, 10, 2930, 30))
    return finish_b(D, out, 2931)


# ================================================================ 29. serenata — the mariachi's instruments under a lit balcony
def guitar_body(D, cx, cy, s, seed, pal=WOOD, top=("#F2C890", "#D89A5A", "#8A5428"), rosette=True, kind="guitarron"):
    """Guitar-family body (front): waisted outline, a painted rosette, bridge, strings and a long neck."""
    out = []
    if kind == "guitarron":
        prof = [(0, -1.0), (0.42, -0.95), (0.62, -0.7), (0.56, -0.38), (0.74, -0.05), (0.92, 0.38), (0.84, 0.8), (0.5, 1.0), (0, 1.04)]
    else:
        prof = [(0, -1.0), (0.48, -0.96), (0.66, -0.66), (0.5, -0.2), (0.72, 0.2), (0.8, 0.6), (0.56, 0.94), (0, 1.0)]
    pts = [(cx + x * s * 0.5, cy + y * s * 0.6) for x, y in prof]
    pts = pts + [(2 * cx - x, y) for x, y in pts[::-1][1:-1]]
    d = smooth_closed(pts)
    out.append(painted(D, pts, top, seed, sdir=(0.7, 0.4), sk=0.12, angle=-85, n=30, inkw=2, hi=0.45))
    out.append(f'<path d="{d}" fill="none" stroke="#3A1A08" stroke-width="{s * 0.04:.1f}" opacity="0.8"/>')
    if rosette:
        rx, ry = cx, cy - s * 0.12
        out.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="{s * 0.15:.1f}" fill="none" stroke="#2E7A3A" stroke-width="{s * 0.03:.1f}"/>')
        out.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="{s * 0.13:.1f}" fill="none" stroke="#C8301A" stroke-width="{s * 0.015:.1f}" stroke-dasharray="3 2"/>')
        out.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="{s * 0.11:.1f}" fill="#1A0A04"/>')
    by = cy + s * 0.36
    out.append(painted(D, rect_pts(cx - s * 0.18, by - s * 0.03, cx + s * 0.18, by + s * 0.04, 6, seed + 1, 0.3), ("#5A3A22", "#2A1A0A", "#0A0402"), seed + 1, sk=0.2, n=3, inkw=1, hi=0.3))
    return "".join(out), pts


def instrument_neck(cx, top_y, bot_y, w, seed, head=("#5A3A22", "#2A1A0A")):
    out = [f'<path d="{pd([(cx - w / 2, bot_y), (cx - w * 0.42, top_y), (cx + w * 0.42, top_y), (cx + w / 2, bot_y)])}" fill="#3A2214"/>']
    for k in range(7):
        y = bot_y - (bot_y - top_y) * (1 - 0.82 ** (k + 1))
        out.append(f'<path d="M {cx - w * 0.46:.1f} {y:.1f} L {cx + w * 0.46:.1f} {y:.1f}" stroke="#C8C0B0" stroke-width="1.2"/>')
    hp = [(cx - w * 0.7, top_y), (cx - w * 0.8, top_y - w * 2.2), (cx, top_y - w * 2.6), (cx + w * 0.8, top_y - w * 2.2), (cx + w * 0.7, top_y)]
    out.append(f'<path d="{smooth_closed(hp)}" fill="{head[0]}" stroke="{head[1]}" stroke-width="1.4"/>')
    for k in range(3):
        for sg in (-1, 1):
            out.append(f'<circle cx="{cx + sg * w * 0.95:.1f}" cy="{top_y - w * (0.5 + k * 0.6):.1f}" r="{w * 0.18:.1f}" fill="#E8D8B0"/>')
    return "".join(out)


def trumpet(D, x, y, L, ang, seed):
    out = [f'<g transform="rotate({ang:.1f} {x:.1f} {y:.1f})">']
    gold = ("#FFF0A0", "#E8B830", "#8A6008")
    out.append(cast(D, x + L * 0.5, y + L * 0.16, L * 0.55, L * 0.06, strength=0.35, seed=seed))
    out.append(taper([(x, y), (x + L * 0.72, y)], L * 0.035, L * 0.04, gold[2]))
    out.append(taper([(x, y - 1), (x + L * 0.72, y - 1)], L * 0.02, L * 0.025, gold[1]))
    loop = catmull([(x + L * 0.2, y), (x + L * 0.14, y + L * 0.1), (x + L * 0.5, y + L * 0.12), (x + L * 0.66, y + L * 0.06), (x + L * 0.6, y)], 5)
    out.append(pline(loop, gold[2], L * 0.035, seed, 1, 1))
    out.append(pline(loop, gold[1], L * 0.02, seed + 1, 1, 1))
    bell = [(x + L * 0.66, y - L * 0.03), (x + L, y - L * 0.13), (x + L, y + L * 0.13), (x + L * 0.66, y + L * 0.03)]
    out.append(painted(D, bell, gold, seed + 2, sdir=(0, 1), sk=0.2, n=6, inkw=1.4, hi=0.6, hik=0.15))
    out.append(f'<ellipse cx="{x + L:.1f}" cy="{y:.1f}" rx="{L * 0.03:.1f}" ry="{L * 0.13:.1f}" fill="{gold[2]}"/>')
    for k in range(3):
        vx = x + L * (0.3 + k * 0.08)
        out.append(painted(D, rect_pts(vx - L * 0.022, y - L * 0.12, vx + L * 0.022, y + L * 0.02, 4, seed + 3 + k, 0.2), gold, seed + 3 + k, sk=0.2, n=2, inkw=1, hi=0.5))
        out.append(f'<ellipse cx="{vx:.1f}" cy="{y - L * 0.13:.1f}" rx="{L * 0.035:.1f}" ry="{L * 0.012:.1f}" fill="#FFFDF0" stroke="{gold[2]}" stroke-width="1"/>')
    out.append(f'<path d="{blob(x - L * 0.02, y, L * 0.03, L * 0.025, seed + 9, 0.1, 8)}" fill="{gold[1]}" stroke="{gold[2]}" stroke-width="1"/>')
    out.append("</g>")
    return "".join(out)


def rose(D, cx, cy, r, seed, pal=CHILE):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.86, seed, 0.06, 14), pal, seed, sk=0.2, n=6, inkw=1.4, hi=0.4)]
    for k in range(4):
        a0 = k * 1.6
        arc = [(cx + math.cos(a0 + t) * r * (0.75 - k * 0.15), cy + math.sin(a0 + t) * r * (0.6 - k * 0.12)) for t in [i * 0.4 for i in range(7)]]
        out.append(pline(arc, dk(pal[2], 0.2), max(1.2, r * 0.08), seed + k, 0.7, 1))
    return "".join(out)


@design("serenata")
def serenata():
    D = Doc2("mxsr")
    out = [sky(D, [(0, "#0E1440"), (0.6, "#1E2A6A"), (1, "#2E3A7A")], 3001, 600, ["#2A3A8A", "#0A1030", "#3A4A9A"], 90, sop=(0.06, 0.16))]
    rnd = random.Random(3002)
    for _ in range(40):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 260):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    out.append(soft_glow(D, 96, 196, 110, "#FFF0C0", 0.4))
    out.append(f'<circle cx="96" cy="196" r="26" fill="#FFF4D0"/>')
    # the house: an adobe wall with a balcony, its window lit and curtains open
    out.append(painted(D, rect_pts(330, 160, 620, 620, 30, 3003, 0.5), ("#C88A8A", "#9A5A6A", "#4A2A3A"), 3003, sk=0.08, angle=-88, n=40, inkw=1.6, hi=0.2))
    wx0, wy0, wx1, wy1 = 388, 196, 528, 330
    out.append(f'<path d="M {wx0} {wy1} L {wx0} {wy0 + 30} Q {(wx0 + wx1) / 2} {wy0 - 20} {wx1} {wy0 + 30} L {wx1} {wy1} Z" fill="#FFD27A"/>')
    out.append(D.glow((wx0 + wx1) / 2, 270, 160, "#FFD070", 0.55))
    for sg in (-1, 1):
        cur = [((wx0 + wx1) / 2 + sg * 70, wy0 + 6), ((wx0 + wx1) / 2 + sg * 40, wy0 + 20), ((wx0 + wx1) / 2 + sg * 50, wy1 - 20), ((wx0 + wx1) / 2 + sg * 70, wy1)]
        out.append(painted(D, cur + [((wx0 + wx1) / 2 + sg * 72, wy1)], ("#FFFDF4", "#F8E8D8", "#C8A8A0"), 3004 + sg, sk=0.15, n=6, inkw=1, hi=0.3))
    # wrought-iron balcony with flowerpots
    out.append(painted(D, rect_pts(368, 330, 548, 344, 14, 3006, 0.4), ("#E8D0C0", "#C8A898", "#7A5A4A"), 3006, sk=0.2, angle=0, n=8, inkw=1.6, hi=0.3))
    out.append(f'<path d="M 372 330 L 372 282 L 544 282 L 544 330" stroke="#1A1018" stroke-width="3" fill="none"/>')
    for k in range(12):
        x = 386 + k * 14
        out.append(f'<path d="M {x} 284 L {x} 330" stroke="#1A1018" stroke-width="1.8"/>')
        if k % 2:
            out.append(f'<path d="M {x - 7} 306 q 7 -8 14 0 q -7 8 -14 0" stroke="#1A1018" stroke-width="1.4" fill="none"/>')
    for k, x in enumerate((392, 456, 520)):
        out.append(clay_pot(D, x, 282, 30, 22, 3007 + k, BARRO, neck=0.95, lip=1, handles=False, deco=None, soot=False))
        out.append(geranium(D, x, 252, 14, 3010 + k, CHILE if k != 1 else ROSA))
    out.append(bugambilia(D, catmull([(620, 170), (560, 200), (548, 270), (560, 360)], 4), 3013, 50))
    # the street: a stone bench, the instruments resting against it
    out.append(f'<rect y="470" width="600" height="140" fill="{D.lin([(0, "#3A3050"), (1, "#1A1428")])}"/>')
    for k in range(30):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(486, 600), rnd.uniform(10, 20), rnd.uniform(3, 6), rnd.randint(0, 999), 0.2, 8)}" fill="#6A5A7A" opacity="0.35"/>')
    out.append(f'<ellipse cx="420" cy="500" rx="220" ry="50" fill="{D.rad([(0, "#FFC870", 0.35), (1, "#FFC870", 0)])}"/>')
    out.append(painted(D, rect_pts(60, 452, 470, 486, 20, 3014, 0.5), ("#C8B8C8", "#8A7A8A", "#4A3A4A"), 3014, sk=0.15, angle=0, n=14, inkw=1.6, hi=0.3))
    for x in (90, 440):
        out.append(painted(D, rect_pts(x - 16, 486, x + 16, 540, 10, 3015 + x, 0.4), ("#A898A8", "#6A5A6A", "#3A2A3A"), 3015 + x, sk=0.2, n=6, inkw=1.4, hi=0.3))
    # guitarrón, leaning
    out.append('<g transform="rotate(-14 200 470)">')
    out.append(instrument_neck(200, 168, 330, 26, 3020))
    g, _ = guitar_body(D, 200, 400, 196, 3021, kind="guitarron", top=("#F6D29A", "#DCA060", "#8A5428"))
    out.append(g)
    for k in range(6):
        out.append(f'<path d="M {192 + k * 3.2:.1f} 172 L {191 + k * 3.6:.1f} 446" stroke="#F4F0E8" stroke-width="1" opacity="0.85"/>')
    out.append("</g>")
    # vihuela, leaning the other way, smaller, darker wood
    out.append('<g transform="rotate(12 340 470)">')
    out.append(instrument_neck(340, 232, 350, 18, 3022))
    g2, _ = guitar_body(D, 340, 406, 122, 3023, kind="vihuela", top=("#E8B87A", "#B8783A", "#6A3A14"))
    out.append(g2)
    for k in range(5):
        out.append(f'<path d="{"M"} {335 + k * 2.6:.1f} 236 L {334 + k * 3:.1f} 436" stroke="#F4F0E8" stroke-width="0.9" opacity="0.85"/>')
    out.append("</g>")
    # trumpet on the bench, a red rose and the moño
    out.append(trumpet(D, 344, 446, 120, -4, 3024))
    out.append(rose(D, 138, 448, 14, 3025))
    out.append(taper([(138, 456), (172, 474)], 3, 2, "#2E6A2A"))
    out.append(leaf_simple(D, 154, 464, 18, 6, 30, NOPAL, 3026, vein=False, inkw=0.8))
    for sg in (-1, 1):
        out.append(painted(D, [(470, 520), (470 + sg * 40, 500), (470 + sg * 46, 540)], CHILE, 3027 + sg, sk=0.2, n=4, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(470, 520, 9, 9, 3029, 0.05, 8), CHILE, 3029, sk=0.2, n=2, inkw=1.2, hi=0.4))
    for k in range(6):
        out.append(f'<path d="{blob(rnd.uniform(80, 520), rnd.uniform(500, 540), 4, 2.6, rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="#E8303A"/>')
    # music in the air
    for k, (x, y) in enumerate(((272, 140), (300, 120), (330, 150))):
        out.append(f'<path d="M {x} {y} l 0 -22 l 12 4" stroke="#FFE8B0" stroke-width="2" fill="none" opacity="0.8"/><ellipse cx="{x - 4}" cy="{y}" rx="5" ry="3.6" fill="#FFE8B0" opacity="0.8" transform="rotate(-20 {x - 4} {y})"/>')
    # lettering
    out.append(letters(D, 252, 112, "serenata", SERIF_IT, 90, "#FFE6B0", ["#FFF4D0", "#F2C878", "#FFFFFF"], 3030, max_w=360,
                       shadow="#0A0A20", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(252, 548, "BAJO TU VENTANA", "#FFE6B0", font=JOS, size=20, ls=6, line_w=30, gap=12, line="#E6337A"))
    return finish_b(D, out, 3031, "#FFFFFF", 0.5)


# ================================================================ 30. la cocina de mi abuela — her wall: the sign, the copper, the talavera
def copper_pot(D, cx, top, w, h, seed):
    pal = ("#FFB88A", "#D8723A", "#7A3410")
    pts = [(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.46, top + h * 0.6), (cx + w * 0.3, top + h), (cx - w * 0.3, top + h), (cx - w * 0.46, top + h * 0.6)]
    out = [painted(D, pts, pal, seed, sdir=(0.9, 0.3), sk=0.22, angle=-90, n=12, inkw=1.6, hi=0.55, hik=0.1)]
    rnd = random.Random(seed)
    for _ in range(int(w * h / 50)):
        x, y = cx + rnd.uniform(-w * 0.4, w * 0.4), top + rnd.uniform(4, h - 4)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2):.1f}" fill="{rnd.choice(["#FFD0A8", "#A8501A"])}" opacity="0.5"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.08, 0, 360, 16)[:-1])}" fill="#5A2410" stroke="{pal[2]}" stroke-width="1.6"/>')
    out.append(taper([(cx + w * 0.5, top + 2), (cx + w * 0.9, top - h * 0.2)], 6, 5, pal[2]))
    out.append(taper([(cx - w * 0.3, top + h * 0.2), (cx - w * 0.32, top + h * 0.75)], 5, 2, "#FFF0E0", 0.7))
    return "".join(out)


def wall_plate(D, cx, cy, r, seed, scheme=0):
    out = [cast(D, cx + 5, cy + 6, r * 1.02, r * 1.0, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.01, 24), ("#FFFFFF", "#F8F2E4", "#C8BCA8"), seed, sk=0.1, n=8, inkw=1.6, hi=0.4))
    B = COBALT if scheme != 1 else ("#7AD0A0", "#2E8A5A", "#145A30")
    for i in range(16):
        a = 2 * math.pi * i / 16
        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86, r * 0.09, r * 0.06, seed + i, 0.15, 8, math.degrees(a) + 90)}" fill="{B[1] if i % 2 else "#F2A41E"}"/>')
    for k in range(6):
        a = math.radians(k * 60)
        px, py = cx + math.cos(a) * r * 0.32, cy + math.sin(a) * r * 0.32
        out.append(f'<path d="{smooth_closed(rot(blob_pts(px, py, r * 0.22, r * 0.1, seed + 20 + k, 0.08, 10), px, py, k * 60))}" fill="{B[1]}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.12:.1f}" fill="#F2A41E"/>')
    out.append(f'<path d="{blob(cx - r * 0.4, cy - r * 0.45, r * 0.2, r * 0.08, seed + 40, 0.2, 8, -40)}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


@design("la-cocina-de-mi-abuela")
def la_cocina_de_mi_abuela():
    D = Doc2("mxab")
    # sunny yellow limewash wall above a talavera backsplash
    out = [sky(D, [(0, "#F8D878"), (1, "#F2C24A")], 3101, 600, ["#FFE8A0", "#D8A02A", "#FFF0B8"], 120, angle=-84, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 140, 120, 360, "#FFF8E0", 0.5))
    out.append(tile_wall(D, -18, 430, 618, 610, 46, 3102))
    out.append(f'<path d="{hg.org_rect(-10, 422, 620, 10, 3103, 0.5, 20, 1)}" fill="#1E3F9A"/>')
    # rail with hooks: copper pots and wooden spoons
    out.append(painted(D, rect_pts(40, 80, 560, 92, 20, 3104, 0.4), ("#C8A060", "#8A6A30", "#4A3410"), 3104, sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    for k, (x, w, h) in enumerate(((96, 70, 54), (182, 56, 44), (420, 60, 48), (504, 74, 56))):
        out.append(f'<path d="M {x + w * 0.9:.1f} 92 q 4 10 -2 18" stroke="#2A1A10" stroke-width="2.4" fill="none"/>')
        out.append(copper_pot(D, x, 116 - h * 0.2 + 16, w, h, 3105 + k))
    for k, x in enumerate((262, 300, 338)):
        out.append(f'<path d="M {x} 92 q 4 8 0 14" stroke="#2A1A10" stroke-width="2" fill="none"/>')
        out.append(painted(D, [(x - 3, 104), (x + 3, 104), (x + 3, 160), (x - 3, 160)], WOOD, 3110 + k, sk=0.2, n=3, inkw=1, hi=0.4))
        out.append(painted(D, blob_pts(x, 172, 11, 16, 3113 + k, 0.05, 10), WOOD, 3113 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
    # the hanging sign, centre stage
    out.append(f'<path d="M 150 196 L 220 110 M 450 196 L 380 110" stroke="#5A3A20" stroke-width="2"/>')
    out.append(f'<circle cx="220" cy="108" r="3" fill="#2A1A10"/><circle cx="380" cy="108" r="3" fill="#2A1A10"/>')
    sign = rect_pts(80, 190, 520, 352, 30, 3116, 0.8)
    out.append(cast(D, 312, 360, 230, 14, strength=0.35, seed=3117))
    out.append(painted(D, sign, ("#8A5A34", "#5E3A1E", "#2E1A0A"), 3116, sdir=(0.3, 1), sk=0.08, angle=0, n=60, slen=(40, 120), sw=(1, 3), inkw=2.4, hi=0.25))
    out.append(f'<path d="{hg.org_rect(94, 204, 412, 134, 3118, 0.6, 20, 6)}" fill="none" stroke="#F6C21C" stroke-width="2.4" stroke-dasharray="10 4"/>')
    for x, y in ((106, 216), (494, 216), (106, 326), (494, 326)):
        out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="#2A1A10"/>')
    for sg in (-1, 1):
        x = 300 + sg * 180
        for k in range(5):
            a = math.radians(k * 72 - 90)
            out.append(f'<path d="{blob(x + math.cos(a) * 8, 270 + math.sin(a) * 8, 7, 4.5, 3119 + k + sg, 0.1, 8, k * 72 - 90)}" fill="{ROSA[0] if sg < 0 else "#8EE6DC"}"/>')
        out.append(f'<circle cx="{x}" cy="270" r="4" fill="#F6C21C"/>')
    out.append(letters(D, 300, 244, "la cocina de", SERIF_IT, 44, "#FFF2D8", ["#FFFFFF", "#F2DCB8"], 3125, max_w=280, wob=0.5))
    out.append(letters(D, 300, 306, "mi abuela", SERIF_IT, 78, "#FFD27A", ["#FFE8A0", "#F2B42A", "#FFF4C8"], 3126, max_w=320,
                       shadow="#1A0A04", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 334, "AQUÍ SE COCINA CON AMOR", JOS, 16, "#F8E8C8", ls=2, max_w=340))
    # shelf with talavera plates leaning, the stove top below with olla and cazuela
    out.append(wall_plate(D, 96, 392, 34, 3130))
    out.append(wall_plate(D, 504, 392, 34, 3131, scheme=1))
    out.append(painted(D, rect_pts(-10, 462, 610, 486, 30, 3132, 0.4), ("#F2EEE6", "#C8C0B8", "#7A726A"), 3132, sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(clay_pot(D, 190, 466, 130, 96, 3133))
    out.append(steam(190, 366, 40, 3134, "#FFFFFF", 2, 24, 6, 0.5))
    out.append(clay_pot(D, 400, 466, 140, 44, 3135, BARRO, neck=1, lip=1, handles=True, deco="#FFF2DC", soot=True, inside="#7A2A10"))
    out.append(steam(400, 410, 34, 3136, "#FFFFFF", 2, 26, 6, 0.5))
    # a jar of wooden spoons and the molinillo
    out.append(jarrito(D, 520, 466, 54, 3137, drink="#3A1A0A"))
    for k, (dx, a) in enumerate(((-8, -12), (4, 6), (12, 20))):
        out.append(f'<g transform="rotate({a} {520 + dx} 420)">' + painted(D, [(520 + dx - 2.6, 420), (520 + dx + 2.6, 420), (520 + dx + 2.6, 470), (520 + dx - 2.6, 470)], WOOD, 3138 + k, sk=0.2, n=2, inkw=0.8, hi=0.4)
                   + painted(D, blob_pts(520 + dx, 414, 7, 11, 3141 + k, 0.05, 8), WOOD, 3141 + k, sk=0.2, n=2, inkw=1, hi=0.4) + "</g>")
    return finish_b(D, out, 3150)


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
