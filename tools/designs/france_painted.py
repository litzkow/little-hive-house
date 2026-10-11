"""France, hand-painted (gouache / storybook) edition: 30 magnets for French expats, francophiles and Francophone
families. Everyday French life, the little things: the morning baguette, the café crème on the zinc, Mamie's
cocotte, the goûter, the Sunday market, the apéro under the plane trees.

Same painted idiom as the Brasil and Italia sets (brasil_painted.py, italia_painted.py): warm paper, layered washes
with pooled edges, brush strokes that follow each form, a warm brown pen line, hand-placed brush lettering, soft light
and paper grain. Colour story: bleu de France and Provençal shutter blue, crust gold and butter, tomato red, lavender,
sunflower yellow, zinc grey, tuffeau cream and slate. French first (with the right accents and French spacing before
! and ?), English never needed.

Run from tools/designs:  python3 france_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash, maple_leaf
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, stripes_in, sea, seagull
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, gingham, cloth, leaf_simple, bird_v, heart_d,
                            p_heart, steam, wood_planks, cup_saucer, wicker_basket, flag_string)
import holidays_gouache as hg
import figures

COL = "france"
INK = "#3A2418"
FLECK = "#8A6A4A"
NB = " "   # French puts a (non-breaking) space before ! ? : ;

# (light, base, dark) gouache palettes
BLEU = ("#7FA2DA", "#2F5AA6", "#142C62")        # bleu de France
PROV = ("#A8D0EA", "#5A96C8", "#285A8A")        # Provençal shutter blue
ROUGE = ("#F48A7A", "#D2302C", "#82121A")
LAV = ("#C8B6EC", "#8A6CC8", "#463286")
SUN = ("#FFE58A", "#F4C02C", "#B8820C")
CREME = ("#FFFDF4", "#F3E8D2", "#C6B08C")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
CRUST = ("#F6CA82", "#CF8A3A", "#7E4614")
BUTTER = ("#FFF4C0", "#F6DC84", "#C8A048")
ZINC = ("#EEF1F4", "#A9B1BA", "#59616C")
SAGE = ("#C6D2A8", "#8A9E6A", "#4C5E36")
STONE = ("#F6EBD2", "#DCC8A0", "#9A8460")
SLATE = ("#8E9CB0", "#56667C", "#2A3444")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
OAK = ("#EACB98", "#C8995E", "#7E5A30")
NOCE = ("#B07A4E", "#7A4A28", "#3E220E")
COPPER = ("#F8BC8A", "#CA743E", "#7A3816")
FLAME = ("#FFB46A", "#E8641E", "#8A2808")       # enamelled cast-iron "volcanic" orange
LEAFG = ("#9ACB7A", "#4A8A3E", "#1E4E1E")
CHOC = ("#8A5A3E", "#4E2A16", "#24100A")
PINK = ("#FFC6CC", "#F08A9A", "#B04A5E")

lt, dk = hg.lt, hg.dk

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def finish_f(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


def pal3(c, a=0.35, b=0.35):
    return (lt(c, a), c, dk(c, b))


# ================================================================ france toolkit
def along(x0, y0, x1, y1, prof, n=40):
    """Closed outline of a long rounded form around the axis (x0,y0)->(x1,y1); prof(t) gives the half width."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        w = prof(t)
        px, py = x0 + ux * L * t, y0 + uy * L * t
        top.append((px + nx * w, py + ny * w))
        bot.append((px - nx * w, py - ny * w))
    return top + bot[::-1][1:-1]


def reid(frag, tag):
    """Copy of an SVG fragment with every id it defines renamed (and its own references updated), so a fragment can
    be drawn twice (e.g. a reflection) without duplicate ids."""
    import re
    for i in set(re.findall(r'id="([^"]+)"', frag)):
        frag = frag.replace(f'id="{i}"', f'id="{i}{tag}"').replace(f'url(#{i})', f'url(#{i}{tag})')
    return frag


def pointed(t, W, tip=0.12, blunt=0.18):
    """Half-width profile with tapered (pointed but rounded) ends, like a baguette or a leek."""
    e = min(t, 1 - t)
    if e < tip:
        k = e / tip
        return W * (blunt + (1 - blunt) * math.sin(k * math.pi / 2) ** 0.8)
    return W


def chalk_text(x, y, s, font, size, fill="#F4F0E6", ls=0, max_w=300, anchor="middle", rot_=0, op=0.92):
    fs = fit_size(s, font, size, max_w, ls)
    tr = f' transform="rotate({rot_} {x} {y})"' if rot_ else ""
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{fill}" opacity="{op}"{tr}>{esc(s)}</text>')


def croissant(D, cx, cy, w, seed, rot_=0, dunk=False, glaze=True):
    """A French butter croissant seen from the front-top: a plump crescent rolled in visible bands, the middle roll
    on top, outer rolls tucked under toward the horns, glossy egg-wash, flaky darker edges."""
    rnd = random.Random(seed)
    out = [cast(D, cx + w * 0.04, cy + w * 0.2, w * 0.56, w * 0.09, strength=0.4, seed=seed)]
    h = w * 0.42
    segs = []
    n = 7
    for i in range(n):
        t = -1 + 2 * i / (n - 1)
        x = cx + t * w * 0.42
        y = cy + h * 0.32 * t * t - h * 0.05
        r = h * 0.5 * (1 - 0.62 * abs(t) ** 1.3)
        ang = math.degrees(math.atan2(2 * h * 0.32 * t, w * 0.42))
        segs.append((abs(t), x, y, r, ang, t))
    pal = ("#FCD592", "#DD9338", "#8E4A12")
    order = sorted(segs, key=lambda s: -s[0])
    for k, (at, x, y, r, ang, t) in enumerate(order):
        rx = w * 0.42 / (n - 1) * 1.05 + r * 0.25
        pts = rot(blob_pts(x, y, rx, r, seed + k * 7, 0.04, 16), x, y, ang)
        out.append(painted(D, rot(pts, cx, cy, rot_), pal, seed + k, sdir=(0.3, 1), sk=0.24, angle=-90 + ang, n=10,
                           slen=(r * 0.3, r * 0.9), sw=(0.8, max(1.2, r * 0.08)), cols=["#FFE6AE", "#B8661E", "#F2B45A"],
                           inkw=1.5, inkop=0.6, hi=0.5, hik=0.14))
        # flaky lamination lines across each roll
        for j in range(3):
            a = math.radians(ang + 90)
            ox = (j - 1) * rx * 0.45
            p0 = (x + math.cos(math.radians(ang)) * ox - math.cos(a) * r * 0.75, y + math.sin(math.radians(ang)) * ox - math.sin(a) * r * 0.75)
            p1 = (x + math.cos(math.radians(ang)) * ox + math.cos(a) * r * 0.6, y + math.sin(math.radians(ang)) * ox + math.sin(a) * r * 0.6)
            mid = ((p0[0] + p1[0]) / 2 + rx * 0.12, (p0[1] + p1[1]) / 2)
            out.append(pline(rot([p0, mid, p1], cx, cy, rot_), "#9A5214", max(0.9, w * 0.006), seed + k * 3 + j, 0.35, 1))
        if glaze:
            hp = rot([(x - rx * 0.4, y - r * 0.55), (x, y - r * 0.78), (x + rx * 0.3, y - r * 0.6)], x, y, ang)
            out.append(taper(rot(hp, cx, cy, rot_), max(1.2, r * 0.06), max(2, r * 0.14), "#FFF4D6", 0.75))
    # a few crisp flakes
    for _ in range(int(w * 0.08)):
        a = rnd.uniform(0, 6.28)
        x, y = cx + math.cos(a) * w * rnd.uniform(0.5, 0.6), cy + h * 0.45 + abs(math.sin(a)) * h * 0.2
        out.append(f'<path d="{blob(x, y, rnd.uniform(1.2, 2.6), rnd.uniform(0.8, 1.6), rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#D8923A", "#F2C070", "#B8702A"])}"/>')
    if dunk:
        tip = order[0]
        out.append(f'<path d="{blob(tip[1], tip[2], tip[3] * 1.3, tip[3] * 1.1, seed, 0.1, 10)}" fill="#7A4A22" opacity="0.4"/>')
    return "".join(out)


def sugar_cube(D, x, y, s, seed, wrap=None):
    """A sugar cube (or one wrapped in paper with a coloured band)."""
    top = [(x, y - s * 0.3), (x + s * 0.55, y - s * 0.55), (x + s * 1.1, y - s * 0.3), (x + s * 0.55, y - s * 0.05)]
    left = [(x, y - s * 0.3), (x + s * 0.55, y - s * 0.05), (x + s * 0.55, y + s * 0.6), (x, y + s * 0.35)]
    right = [(x + s * 0.55, y - s * 0.05), (x + s * 1.1, y - s * 0.3), (x + s * 1.1, y + s * 0.35), (x + s * 0.55, y + s * 0.6)]
    out = [cast(D, x + s * 0.7, y + s * 0.6, s * 0.9, s * 0.2, strength=0.3, seed=seed)]
    out.append(f'<path d="{hg.org_poly(top, seed, 0.3, 6, 1)}" fill="#FFFFFF"/>')
    out.append(f'<path d="{hg.org_poly(left, seed + 1, 0.3, 6, 1)}" fill="#E8E2D8"/>')
    out.append(f'<path d="{hg.org_poly(right, seed + 2, 0.3, 6, 1)}" fill="#CFC8BC"/>')
    if wrap:
        out.append(f'<path d="{pd([(x, y + s * 0.05), (x + s * 0.55, y + s * 0.3), (x + s * 0.55, y + s * 0.42), (x, y + s * 0.17)])}" fill="{wrap}" opacity="0.9"/>')
        out.append(f'<path d="{pd([(x + s * 0.55, y + s * 0.3), (x + s * 1.1, y + s * 0.05), (x + s * 1.1, y + s * 0.17), (x + s * 0.55, y + s * 0.42)])}" fill="{dk(wrap, 0.2)}" opacity="0.9"/>')
    else:
        out.append(specks(seed, (x + 2, y - s * 0.5, x + s, y + s * 0.5), ["#FFFFFF", "#D8D0C4"], int(s), (0.5, 1.1), (0.5, 0.9)))
    out.append(ink(pd(top + [top[0]], False) + " " + pd([left[1], left[2]], False), "#9A8A7A", 1.1, seed, 1, 0.7))
    out.append(ink(hg.org_poly([top[0], top[1], top[2], right[2], right[3], left[3]], seed + 3, 0.3, 6, 1), "#8A7A6A", 1.2, seed, 1, 0.6))
    return "".join(out)


def tile_floor(D, y0, y1, seed, cols=("#C86A3E", "#B85A30", "#D27A4A"), size=46, vanish=(300, -300)):
    """Terracotta tomettes (hexagonal floor tiles) in light perspective."""
    rnd = random.Random(seed)
    out = [f'<rect x="-10" y="{y0}" width="620" height="{y1 - y0 + 10}" fill="{cols[1]}"/>']
    r = size / 2
    row = 0
    y = y0
    while y < y1 + r:
        k = 0.45 + 0.55 * (y - y0) / max(1, y1 - y0)
        rr = r * k
        x = -rr * (row % 2) * 1.7
        while x < 620:
            pts = [(x + rr * math.cos(math.radians(a)), y + rr * 0.55 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
            out.append(f'<path d="{hg.org_poly(pts, rnd.randint(1, 9999), 0.6, 8, 2)}" fill="{rnd.choice(cols)}" stroke="#F2E2CC" stroke-width="{max(1.2, 2.4 * k):.1f}" stroke-opacity="0.75"/>')
            x += rr * 3.4
        y += rr * 0.55 * 0.87 * 2 / 1.0 * 0.5 + rr * 0.48
        row += 1
    return "".join(out)


# ================================================================ 1. la baguette — still warm, the heel already gone
def baguette(D, x0, y0, x1, y1, W, seed, torn=True, flour=True):
    """A traditional baguette along (x0,y0)->(x1,y1): pointed ends, golden crust darker underneath, five slanted
    grignes (score marks) with lifted pale ears, a dusting of flour; if `torn`, the far end is ripped off and shows
    the airy crumb."""
    rnd = random.Random(seed)
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux                          # 'n' points to the underside when the loaf runs left to right

    def P(t, s):
        return (x0 + ux * L * t + nx * W * s, y0 + uy * L * t + ny * W * s)

    def prof(t):
        e = min(t, 1 - t) if not torn else t
        if torn and t > 0.985:
            return W * 0.96
        if e < 0.1:
            k = e / 0.1
            return W * (0.22 + 0.78 * math.sin(k * math.pi / 2) ** 0.75)
        return W * (1 + 0.04 * math.sin(t * 19 + seed))

    pts = along(x0, y0, x1, y1, prof, 60)
    if torn:
        # ragged torn end
        end = [P(1.0 + rnd.uniform(-0.006, 0.01), s) for s in (0.95, 0.6, 0.25, -0.1, -0.45, -0.8)]
        k = len(pts) // 2
        pts = pts[:k + 1][:-2] + [(x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2)) for x, y in end[::-1]] + pts[k + 1:][1:]
    d = smooth_closed(pts)
    out = [cast(D, (x0 + x1) / 2 + nx * W * 1.2, (y0 + y1) / 2 + ny * W * 1.3, L * 0.5, W * 0.5, strength=0.4, seed=seed)]
    out.append(painted(D, pts, CRUST, seed, sdir=(nx, ny), sk=0.22, angle=ang, n=int(L * 0.4), slen=(L * 0.03, L * 0.1),
                       sw=(1, 3), cols=["#FFE0A0", "#B8662A", "#E8A85A", "#9A5418"], inkw=2.2, inkop=0.75, hi=0.45, hik=0.1, curve=0.1))
    cid = D.clip(f'<path d="{d}"/>')
    inner = [shade_over(D, d, "#4A1E04", 0.45, 0.5 - nx * 0.5, 0.5 - ny * 0.5, 0.5 + nx * 0.5, 0.5 + ny * 0.5, 0.45)]
    # grignes: slanted score marks with lifted ears
    for i in range(5):
        t = 0.17 + i * 0.155
        c = P(t, -0.08)
        a = ang - 18
        gl, gw = L * 0.11, W * 0.34
        g = rot(blob_pts(c[0], c[1], gl, gw, seed + 20 + i, 0.06, 14), c[0], c[1], a)
        inner.append(f'<path d="{smooth_closed(g)}" fill="#F2D49A"/>')
        inner.append(strokes(D.nid(), smooth_closed(g), bbox(g), ["#FFF0C8", "#E8B870", "#FFFFFF"], seed + 30 + i, n=10, angle=a,
                             length=(gl * 0.3, gl * 0.9), width=(0.8, 2), opacity=(0.3, 0.6)))
        ear = rot([(c[0] - gl * 0.95, c[1] + gw * 0.2), (c[0], c[1] - gw * 1.25), (c[0] + gl * 0.95, c[1] - gw * 0.1)], c[0], c[1], a)
        inner.append(taper(ear, 3, 7, "#8A4410", 0.55))
        ear2 = rot([(c[0] - gl * 0.9, c[1] + gw * 0.05), (c[0], c[1] - gw * 0.95), (c[0] + gl * 0.9, c[1] - gw * 0.2)], c[0], c[1], a)
        inner.append(taper(ear2, 1.5, 3.5, "#FFE6B0", 0.85))
        low = rot([(c[0] - gl * 0.8, c[1] + gw * 0.8), (c[0], c[1] + gw * 1.05), (c[0] + gl * 0.85, c[1] + gw * 0.45)], c[0], c[1], a)
        inner.append(taper(low, 2.5, 1, "#7A3A0E", 0.5))
    if flour:
        for _ in range(int(L * 0.5)):
            t, s = rnd.uniform(0.04, 0.96), rnd.uniform(-1, 0.1)
            x, y = P(t, s)
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.5, 1.5):.1f}" fill="#FFFBF0" opacity="{rnd.uniform(0.35, 0.85):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if torn:
        # the crumb at the torn end: creamy, holey, a crust lip around it
        c = P(0.99, 0.05)
        face = rot(blob_pts(c[0], c[1], W * 0.36, W * 0.9, seed + 50, 0.12, 16), c[0], c[1], ang)
        out.append(f'<path d="{smooth_closed(face)}" fill="#FBF0D6"/>')
        fid = D.clip(f'<path d="{smooth_closed(face)}"/>')
        holes = []
        for _ in range(16):
            hx, hy = c[0] + rnd.uniform(-W * 0.3, W * 0.3), c[1] + rnd.uniform(-W * 0.8, W * 0.8)
            holes.append(f'<path d="{blob(hx, hy, rnd.uniform(1.5, 4.5), rnd.uniform(1.2, 3.2), rnd.randint(1, 999), 0.25, 8, ang + 70)}" fill="#D8BC88" opacity="0.8"/>')
        holes.append(shade_over(D, smooth_closed(face), "#B08A50", 0.4, 0, 0, 1, 1, 0.4))
        out.append(f'<g {fid}>{"".join(holes)}</g>')
        out.append(ink(smooth_closed(face), "#A8783A", 1.4, seed + 51, 1, 0.7))
    return "".join(out)


def paper_sleeve(D, x0, y0, x1, y1, W, t0, t1, seed, band=BLEU[1]):
    """The thin white bakery paper sleeve wrapped around part of a baguette, crinkled open mouth, printed wheat ears."""
    rnd = random.Random(seed)
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux

    def P(t, s):
        return (x0 + ux * L * t + nx * W * s, y0 + uy * L * t + ny * W * s)

    top = [P(t0 + (t1 - t0) * i / 10, -1.22 - 0.03 * math.sin(i)) for i in range(11)]
    mouth = [P(t1 + rnd.uniform(-0.012, 0.012) + 0.012 * math.sin(k * 2.3), -1.3 + k * 0.26) for k in range(11)]
    bot = [P(t1 - (t1 - t0) * i / 10, 1.22 + 0.03 * math.sin(i)) for i in range(11)]
    pts = [P(t0 - 0.03, -0.6), P(t0 - 0.045, 0)] + [P(t0 - 0.03, 0.6)][::-1][:0] + top + mouth + bot + [P(t0 - 0.03, 0.6)]
    d = smooth_closed(pts)
    out = [painted(D, pts, ("#FFFFFF", "#F6F1E6", "#C8BEAE"), seed, sdir=(nx, ny), sk=0.12, angle=ang, n=40, slen=(L * 0.03, L * 0.09),
                   sw=(0.8, 2), cols=["#FFFFFF", "#E2DACB"], inkw=1.8, inkop=0.6, hi=0.5, hik=0.06)]
    cid = D.clip(f'<path d="{d}"/>')
    inner = [shade_over(D, d, "#5A4A3A", 0.3, 0.5 - nx * 0.5, 0.5 - ny * 0.5, 0.5 + nx * 0.5, 0.5 + ny * 0.5, 0.5)]
    # crinkles
    for i in range(14):
        t = rnd.uniform(t0, t1)
        a, b = P(t, -1.2), P(t + rnd.uniform(-0.02, 0.02), rnd.uniform(-0.2, 1.2))
        inner.append(taper([a, ((a[0] + b[0]) / 2 + rnd.uniform(-3, 3), (a[1] + b[1]) / 2), b], 2.4, 0.6, "#B8AC98", 0.35))
    # printed band and wheat ears
    for s in (-0.55, 0.55):
        inner.append(taper([P(t0, s), P((t0 + t1) / 2, s + 0.02), P(t1, s)], 3, 3, band, 0.7))
    for i in range(3):
        t = t0 + (t1 - t0) * (0.2 + 0.3 * i)
        c = P(t, 0)
        for j in range(5):
            gx, gy = rot([(c[0] - 10 + j * 5, c[1] - 2 - abs(j - 2) * 0.5)], c[0], c[1], ang)[0]
            inner.append(f'<path d="{blob(gx, gy, 3.4, 1.8, seed + i * 9 + j, 0.1, 8, ang + 35 * (1 if j % 2 else -1))}" fill="{band}" opacity="0.65"/>')
        inner.append(pline([rot([(c[0] - 16, c[1])], c[0], c[1], ang)[0], rot([(c[0] + 12, c[1])], c[0], c[1], ang)[0]], band, 1.4, seed + i, 0.6, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(smooth_open(mouth), "#9A8A74", 1.6, seed + 3, 1, 0.7))
    return "".join(out)


@design("la-baguette")
def la_baguette():
    D = Doc2("fr-bq")
    # morning wall: warm limewash, a slanted patch of window light with the mullion's shadow
    out = [sky(D, [(0, "#F6E2C2"), (1, "#EBCFA2")], 101, 600, ["#FFF0D8", "#E2BE8A", "#F8E6C8"], 90, angle=-80, sop=(0.05, 0.14))]
    out.append(f'<path d="{pd([(330, 40), (600, 10), (600, 330), (380, 360)])}" fill="#FFF6DE" opacity="0.55"/>')
    out.append(f'<path d="{pd([(456, 26), (474, 24), (500, 345), (482, 347)])}" fill="#C89A62" opacity="0.18"/>')
    out.append(f'<path d="{pd([(340, 192), (600, 170), (600, 186), (346, 208)])}" fill="#C89A62" opacity="0.16"/>')
    out.append(blooms(102, ["#E2B47A", "#F6D6A8", "#D8A46A"], 7, (0, 0, 600, 380), (90, 170), (0.05, 0.1)))
    # pale oak table, front edge
    out.append(wood_planks(D, 352, 600, 103, OAK, 3))
    out.append(f'<rect y="346" width="600" height="10" fill="#7E5A30" opacity="0.45"/>')
    out.append(soft_glow(D, 320, 430, 260, "#FFF2C8", 0.45))
    # linen tea towel under the bread, blue stripe near the hem
    tw = [(30, 392), (300, 374), (570, 400), (556, 556), (300, 578), (44, 562)]
    twd = smooth_closed(poly_pts(tw, 30, 104, 1.2))
    out.append(f'<path d="{twd}" fill="#F4ECDA"/>')
    out.append(strokes(D.nid(), twd, (30, 390, 570, 590), ["#FFFFFF", "#D8CCB4", "#E8DCC6"], 105, n=120, angle=-2, length=(20, 60), width=(0.6, 1.4), opacity=(0.3, 0.6)))
    tcid = D.clip(f'<path d="{twd}"/>')
    bands = "".join(taper([(20, 530 + dy), (300, 552 + dy), (580, 534 + dy)], w_, w_, BLEU[1], 0.85) for dy, w_ in ((-6, 9), (8, 4)))
    out.append(f'<g {tcid}>{bands}</g>')
    out.append(shade_over(D, twd, "#5A3A1A", 0.3, 0, 0, 0.3, 1, 0.5))
    out.append(ink(twd, "#9A8462", 1.4, 107, 1, 0.6))
    # a butter dish behind, salted butter already dented by a knife
    bx, by = 132, 362
    out.append(cast(D, bx + 8, by + 6, 62, 8, strength=0.35, seed=120))
    out.append(painted(D, ell_pts(bx, by, 62, 13, 0, 360, 24), WHITE, 121, sdir=(0.3, 1), sk=0.15, n=8, inkw=1.5, hi=0.4))
    out.append(pline(ell_pts(bx, by, 52, 9, 10, 170, 12), BLEU[1], 2, 122, 0.8, 1))
    butter = [(bx - 40, by - 4), (bx - 36, by - 26), (bx + 26, by - 30), (bx + 40, by - 8), (bx + 30, by + 2), (bx - 30, by + 2)]
    out.append(painted(D, butter, BUTTER, 123, sdir=(0.6, 0.8), sk=0.2, angle=0, n=10, inkw=1.5, hi=0.5))
    out.append(f'<path d="{blob(bx - 6, by - 24, 16, 4, 124, 0.2, 10)}" fill="#E8C460" opacity="0.7"/>')
    out.append(taper([(bx + 10, by - 18), (bx + 54, by - 52), (bx + 70, by - 70)], 4, 6, "#B8BCC4"))
    out.append(taper([(bx + 54, by - 52), (bx + 70, by - 70), (bx + 86, by - 88)], 7, 7, "#7A4A28"))
    # crumbs and the torn-off heel
    rnd = random.Random(108)
    for _ in range(26):
        x, y = rnd.uniform(400, 540), rnd.uniform(440, 540)
        out.append(f'<path d="{blob(x, y, rnd.uniform(1, 3.2), rnd.uniform(0.8, 2.2), rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#D8923A", "#F6E6C2", "#B8702A", "#FFF4DC"])}"/>')
    hx, hy = 478, 500
    heel = rot([(hx - 30, hy - 14), (hx - 6, hy - 18), (hx + 20, hy - 12), (hx + 34, hy - 2), (hx + 30, hy + 10), (hx + 4, hy + 16), (hx - 26, hy + 14), (hx - 34, hy)], hx, hy, -20)
    out.append(cast(D, hx + 6, hy + 18, 44, 7, strength=0.35, seed=109))
    out.append(painted(D, heel, CRUST, 110, sdir=(0.3, 1), sk=0.22, angle=-20, n=16, inkw=1.8, hi=0.45))
    face = rot(blob_pts(hx - 26, hy, 8, 15, 111, 0.15, 12), hx - 26, hy, -20)
    out.append(f'<path d="{smooth_closed(face)}" fill="#FBF0D6"/>' + specks(112, (hx - 32, hy - 12, hx - 20, hy + 12), ["#D8BC88"], 8, (1, 2.2), (0.6, 0.9)))
    out.append(ink(smooth_closed(face), "#A8783A", 1.2, 113, 1, 0.7))
    out.append(f'<path d="{blob(hx + 8, hy - 8, 14, 3, 114, 0.2, 8, -20)}" fill="#FFE8B8" opacity="0.6"/>')
    # the baguette, diagonal, in its sleeve
    bx0, by0, bx1, by1, W = -40, 548, 488, 258, 33
    out.append(baguette(D, bx0, by0, bx1, by1, W, 115, torn=True))
    out.append(paper_sleeve(D, bx0, by0, bx1, by1, W, 0.0, 0.5, 116))
    # wisps of warmth from the torn end
    out.append(steam(494, 236, 26, 117, "#FFFFFF", 2, 16, 5, 0.6))
    # lettering
    out.append(letters(D, 300, 140, "la baguette", SERIF_IT, 118, "#8A3A14", ["#B0561E", "#6A280A", "#C86A2E"], 118, max_w=440,
                       shadow="#FFF4DC", soff=(0.02, 0.035), angle=-40, hi="#F6B878"))
    out.append(ruled(300, 188, "LE QUIGNON, C’EST POUR MOI", BLEU[2], font=JOS, size=19, ls=4, line_w=26, gap=12, max_w=380))
    return finish_f(D, out, 119)


# ================================================================ 2. café crème — au comptoir, on the zinc
def zinc_counter(D, y_top, y_edge, seed):
    """A bistro zinc: pewter top catching the light (soft reflections), the rolled front lip, wood below."""
    out = [f'<path d="M -10 {y_top} L 610 {y_top} L 610 {y_edge} L -10 {y_edge} Z" fill="{D.lin([(0, "#9AA2AC"), (0.5, "#C8CED6"), (1, "#8A929C")])}"/>']
    d = f"M -10 {y_top} L 610 {y_top} L 610 {y_edge} L -10 {y_edge} Z"
    out.append(strokes(D.nid(), d, (-60, y_top, 610, y_edge), ["#FFFFFF", "#7A828C", "#DDE2E8"], seed, n=90, angle=0, length=(40, 160), width=(1, 4), opacity=(0.1, 0.35), curve=0.05))
    rnd = random.Random(seed)
    for _ in range(5):
        x = rnd.uniform(0, 560)
        out.append(f'<path d="{blob(x, rnd.uniform(y_top + 10, y_edge - 10), rnd.uniform(30, 70), rnd.uniform(4, 8), rnd.randint(1, 999), 0.2, 10)}" fill="#FFFFFF" opacity="0.18"/>')
    # rolled lip
    out.append(f'<path d="M -10 {y_edge - 4} L 610 {y_edge - 4} L 610 {y_edge + 22} L -10 {y_edge + 22} Z" fill="{D.lin([(0, "#E8ECF0"), (0.35, "#FFFFFF"), (0.6, "#8A929C"), (1, "#4A525C")])}"/>')
    out.append(ink(f"M -10 {y_edge - 4} L 610 {y_edge - 4}", "#4A525C", 1.6, seed, 1, 0.7))
    out.append(ink(f"M -10 {y_edge + 22} L 610 {y_edge + 22}", "#2A3038", 2, seed + 1, 1, 0.8))
    out.append(wood_planks(D, y_edge + 22, 610, seed + 2, NOCE, 5, vertical=True))
    out.append(f'<rect x="-10" y="{y_edge + 22}" width="620" height="16" fill="#1A0E06" opacity="0.35"/>')
    return "".join(out)


def cloche(D, cx, base, w, h, seed, inside=""):
    """A glass cake dome on a stand (croissants kept under it on the bar)."""
    out = [cast(D, cx + 6, base + 2, w * 0.55, 6, strength=0.35, seed=seed)]
    out.append(painted(D, ell_pts(cx, base - 8, w * 0.55, 9, 0, 360, 24), WHITE, seed, sk=0.15, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, [(cx - 6, base - 6), (cx - 4, base + 2), (cx + 4, base + 2), (cx + 6, base - 6)], WHITE, seed + 1, sk=0.1, n=2, inkw=1, hi=0.3))
    out.append(inside)
    dome = [(cx - w / 2, base - 10)] + [(cx - w / 2 * math.cos(math.radians(a)), base - 10 - h * math.sin(math.radians(a)) ** 0.85) for a in range(10, 171, 10)] + [(cx + w / 2, base - 10)]
    dd = smooth_closed(dome)
    out.append(f'<path d="{dd}" fill="#E8F2F6" opacity="0.22"/>')
    out.append(taper([(cx - w * 0.36, base - 20), (cx - w * 0.42, base - h * 0.5), (cx - w * 0.2, base - h * 0.88)], 3, 7, "#FFFFFF", 0.65))
    out.append(taper([(cx + w * 0.38, base - h * 0.3), (cx + w * 0.3, base - h * 0.7)], 2, 3, "#FFFFFF", 0.4))
    out.append(ink(dd, "#7A8E98", 1.6, seed + 2, 2, 0.6))
    out.append(painted(D, blob_pts(cx, base - 10 - h - 5, 8, 6, seed + 3, 0.05, 10), WHITE, seed + 3, sk=0.2, n=3, inkw=1.2, hi=0.5))
    return "".join(out)


@design("cafe-creme")
def cafe_creme():
    D = Doc2("fr-cc")
    # bistro back wall: deep bottle-green boiserie, warm lamp light
    out = [sky(D, [(0, "#24463A"), (1, "#16302A")], 201, 600, ["#2E5A48", "#0E221C", "#3A6A56"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 460, 250, 300, "#FFD898", 0.32))
    for x0 in (-20, 300):
        out.append(f'<path d="{hg.org_rect(x0 + 40, 236, 240, 150, 202 + x0, 0.6, 20, 4)}" fill="none" stroke="#0E201A" stroke-width="5" opacity="0.5"/>')
        out.append(f'<path d="{hg.org_rect(x0 + 43, 239, 240, 150, 203 + x0, 0.6, 20, 4)}" fill="none" stroke="#5A8A72" stroke-width="2" opacity="0.4"/>')
    # globe lamp glow upper right
    out.append(soft_glow(D, 538, 236, 90, "#FFE6B0", 0.7))
    out.append(f'<circle cx="538" cy="236" r="22" fill="#FFF4D8" opacity="0.95"/>')
    out.append(ink(f"M 538 60 L 538 214", "#B8924A", 2.4, 204, 1, 0.8))
    out.append(painted(D, blob_pts(538, 214, 10, 5, 205, 0.05, 10), ("#F2D488", "#C8A050", "#7A5A20"), 205, sk=0.2, n=3, inkw=1.2, hi=0.5))
    # the ardoise (chalkboard) of the day
    bx0, by0, bx1, by1 = 64, 222, 244, 380
    out.append(painted(D, rect_pts(bx0 - 9, by0 - 9, bx1 + 9, by1 + 9, 20, 206, 0.5), WOOD, 206, sdir=(1, 1), sk=0.12, angle=0, n=30, inkw=1.8, hi=0.4))
    board = rect_pts(bx0, by0, bx1, by1, 20, 207, 0.4)
    out.append(f'<path d="{smooth_closed(board)}" fill="#2A302E"/>')
    out.append(strokes(D.nid(), smooth_closed(board), (bx0, by0, bx1, by1), ["#5A6260", "#9AA09C", "#3A403E"], 208, n=60, angle=-10, length=(20, 60), width=(3, 9), opacity=(0.06, 0.16)))
    out.append(chalk_text((bx0 + bx1) / 2, by0 + 30, "Ardoise du jour", SERIF_IT, 21, "#F6E6B8", max_w=160))
    out.append(pline([(bx0 + 30, by0 + 40), ((bx0 + bx1) / 2, by0 + 42), (bx1 - 30, by0 + 39)], "#F6E6B8", 1.6, 209, 0.7, 1))
    rows = [("Café", "1,50"), ("Crème", "3,00"), ("Croissant", "1,40"), ("Tartine", "2,50")]
    for k, (a, b) in enumerate(rows):
        y = by0 + 70 + k * 25
        out.append(chalk_text(bx0 + 12, y, a, JOST, 18, anchor="start", max_w=96))
        out.append(chalk_text(bx1 - 12, y, b, JOST, 18, anchor="end", max_w=60))
        out.append(f'<path d="M {bx0 + 98} {y - 5} L {bx1 - 50} {y - 5}" stroke="#F4F0E6" stroke-width="1.6" stroke-dasharray="1.5 5" stroke-linecap="round" opacity="0.6"/>')
    # zinc counter
    out.append(zinc_counter(D, 400, 494, 210))
    # brass foot rail along the bottom of the bar
    out.append(taper([(-10, 566), (610, 566)], 12, 12, "#B8903A"))
    out.append(taper([(-10, 562), (610, 562)], 3, 3, "#FFE8A0", 0.85))
    for x in (110, 300, 490):
        out.append(painted(D, [(x - 8, 560), (x - 6, 540), (x + 6, 540), (x + 8, 560)], ("#F2D488", "#C8A048", "#7A5A20"), 230 + x, sk=0.2, n=3, inkw=1.2, hi=0.5))
    # the croissant of the day on a little plate, front right
    out.append(cast(D, 474, 484, 82, 12, strength=0.35, seed=224))
    out.append(painted(D, ell_pts(470, 472, 80, 20, 0, 360, 28), WHITE, 225, sdir=(0.3, 1), sk=0.15, n=10, inkw=1.4, hi=0.4))
    out.append(pline(ell_pts(470, 472, 68, 14, 15, 165, 12), BLEU[1], 1.8, 226, 0.7, 1))
    out.append(croissant(D, 470, 446, 146, 227, rot_=-4))
    # the café crème: big white cup on its saucer, milky foam
    cx, base, w = 292, 488, 134
    out.append(cup_saucer(D, cx, base, w, 215, rim=BLEU, coffee="#B87E4A"))
    top = base - 8 - w * 0.62
    foam = smooth_closed(ell_pts(cx, top + 1.5, w / 2 - 6, w * 0.08, 0, 360, 24))
    out.append(f'<path d="{foam}" fill="#E8CBA0"/>')
    out.append(f'<path d="{blob(cx + 6, top + 2, w * 0.3, w * 0.05, 216, 0.15, 12)}" fill="#F6E4C4"/>')
    rnd = random.Random(217)
    for _ in range(24):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.6, 0.95)
        out.append(f'<circle cx="{cx + math.cos(a) * (w / 2 - 8) * rr:.1f}" cy="{top + 1.5 + math.sin(a) * w * 0.07 * rr:.1f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFF6E6" opacity="0.8"/>')
    out.append(ink(foam, "#9A6A3A", 1.2, 218, 1, 0.5))
    out.append(steam(cx + 10, top - 8, 34, 219, "#FFFFFF", 2, 26, 6, 0.55))
    # spoon and two wrapped sugar cubes on the zinc
    out.append(taper([(cx - w * 0.44, base - 6), (cx - w * 0.62, base - 2), (cx - w * 0.8, base + 2)], 5, 3, "#B8BCC4"))
    out.append(taper([(cx - w * 0.44, base - 7), (cx - w * 0.8, base + 1)], 1.4, 0.8, "#FFFFFF", 0.8))
    out.append(sugar_cube(D, 92, 452, 26, 220, wrap=ROUGE[1]))
    out.append(sugar_cube(D, 120, 466, 26, 221, wrap=BLEU[1]))
    # lettering
    out.append(letters(D, 300, 136, "café crème", SERIF_IT, 110, "#FFF2DA", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 222, max_w=440,
                       shadow="#0A1A14", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "AU COMPTOIR, S’IL VOUS PLAÎT", "#F2C860", font=JOS, size=18, ls=4, line_w=22, gap=11, max_w=390))
    return finish_f(D, out, 223)


# ================================================================ 3. le fromage — the board, before dessert
def cheese_wedge(D, cx, cy, s, seed, body=("#FFF2B8", "#F4D978", "#C8A848"), rind=("#D8A868", "#A8743A", "#5E3A14"), holes=False, crystals=True):
    """A tall wedge of hard mountain cheese (Comté style) seen in 3/4: cut faces pale, rind on the back."""
    rnd = random.Random(seed)
    A = (cx - s * 0.9, cy + s * 0.25)      # tip
    B = (cx + s * 0.55, cy - s * 0.35)
    C = (cx + s * 0.75, cy + s * 0.32)
    top_h = s * 0.5
    front = [A, C, (C[0], C[1] - top_h), (A[0], A[1] - top_h * 0.95)]
    side = [C, (C[0] + s * 0.12, C[1] - s * 0.22), (C[0] + s * 0.12, C[1] - s * 0.22 - top_h), (C[0], C[1] - top_h)]
    topf = [(A[0], A[1] - top_h * 0.95), (C[0], C[1] - top_h), (C[0] + s * 0.12, C[1] - s * 0.22 - top_h), (B[0], B[1] - top_h)]
    out = [cast(D, cx, cy + s * 0.35, s * 0.95, s * 0.12, strength=0.4, seed=seed)]
    out.append(f'<path d="{hg.org_poly(side, seed, 0.6, 8, 2)}" fill="{rind[1]}"/>')
    out.append(strokes(D.nid(), hg.org_poly(side, seed, 0.6, 8, 2), bbox(side), [rind[0], rind[2]], seed, n=14, angle=-90, length=(6, 16), width=(1, 3), opacity=(0.3, 0.6)))
    out.append(painted(D, poly_pts(front, 12, seed + 1, 0.5), body, seed + 1, sdir=(0.2, 1), sk=0.1, angle=-12, n=30, inkw=1.8, hi=0.4))
    out.append(painted(D, poly_pts(topf, 12, seed + 2, 0.5), (lt(body[0], 0.4), lt(body[1], 0.2), body[1]), seed + 2, sdir=(0.2, 1), sk=0.08, angle=-20, n=20, inkw=1.6, hi=0.5))
    # rind lip along the back edge of the top face
    out.append(taper([topf[3], topf[2]], 5, 6, rind[1]))
    out.append(taper([C, (C[0], C[1] - top_h)], 4, 4, rind[1], 0.9))
    if crystals:
        for _ in range(int(s * 0.3)):
            t, u = rnd.random(), rnd.random()
            x = A[0] + (C[0] - A[0]) * t
            y = A[1] + (C[1] - A[1]) * t - top_h * 0.9 * u
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.7, 1.5):.1f}" fill="#FFFDF0" opacity="0.9"/>')
    if holes:
        for _ in range(5):
            t, u = rnd.uniform(0.25, 0.9), rnd.uniform(0.2, 0.8)
            x = A[0] + (C[0] - A[0]) * t
            y = A[1] + (C[1] - A[1]) * t - top_h * u
            out.append(f'<path d="{blob(x, y, rnd.uniform(3, 6), rnd.uniform(2.5, 4.5), rnd.randint(1, 99), 0.1, 10)}" fill="{body[2]}" opacity="0.7"/>')
    return "".join(out)


def camembert(D, cx, cy, r, seed, cut=True):
    """A soft bloomy-rind round in its little poplar-wood box, one wedge cut and oozing."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + r * 0.5, r * 1.15, r * 0.3, strength=0.4, seed=seed)]
    # box rim (lower half visible below the cheese)
    out.append(painted(D, ell_pts(cx, cy + r * 0.18, r * 1.1, r * 0.48, 0, 360, 30), ("#F6E0B4", "#DCB880", "#9A7844"), seed, sdir=(0.3, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    for k in range(5):
        out.append(pline(ell_pts(cx, cy + r * 0.18 + k * 1.5, r * 1.1 - k * 0.6, r * 0.48 - k * 0.3, 15, 165, 12), "#B08A54", 0.9, seed + k, 0.5, 1))
    # the cheese (top), rind white with grey-cream bloom
    top = ell_pts(cx, cy, r, r * 0.42, 0, 360, 36)
    if cut:
        # remove a wedge toward the viewer
        top = [p for p in top if not (40 < math.degrees(math.atan2((p[1] - cy) / 0.42, p[0] - cx)) % 360 < 100)]
        top = top + [(cx, cy)]
    out.append(painted(D, top, ("#FFFFFF", "#F6F0E2", "#C8BCA4"), seed + 1, sdir=(0.3, 1), sk=0.12, angle=-10, n=40, inkw=1.6, hi=0.4))
    tid = D.clip(f'<path d="{smooth_closed(top)}"/>')
    bloom = specks(seed + 2, (cx - r, cy - r * 0.5, cx + r, cy + r * 0.5), ["#E2D8C0", "#D0C4A8", "#FFFFFF"], int(r * 2), (0.8, 2.4), (0.3, 0.7))
    out.append(f'<g {tid}>{bloom}</g>')
    if cut:
        # the cut face: creamy yellow paste oozing over the box edge
        a1, a2 = math.radians(40), math.radians(100)
        p1 = (cx + r * math.cos(a1), cy + r * 0.42 * math.sin(a1))
        p2 = (cx + r * math.cos(a2), cy + r * 0.42 * math.sin(a2))
        face = [(cx, cy), p1, (p1[0] + 2, p1[1] + r * 0.16), (cx + 2, cy + r * 0.16), (p2[0], p2[1] + r * 0.16), p2]
        out.append(painted(D, face, ("#FFF2C4", "#F6DC8A", "#C8A048"), seed + 3, sdir=(0, 1), sk=0.15, angle=-80, n=8, inkw=1.4, hi=0.5))
        ooze = [(cx - r * 0.05, cy + r * 0.16), (cx + r * 0.25, cy + r * 0.2), (cx + r * 0.35, cy + r * 0.36), (cx + r * 0.2, cy + r * 0.48), (cx + r * 0.02, cy + r * 0.38)]
        out.append(painted(D, ooze, ("#FFF6D0", "#F8E29A", "#D0AA50"), seed + 4, sk=0.1, n=4, inkw=1.2, hi=0.6))
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {p1[0]:.1f} {p1[1]:.1f} M {cx:.1f} {cy:.1f} L {p2[0]:.1f} {p2[1]:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>')
    return "".join(out)


def chevre_log(D, x0, y0, x1, y1, R, seed):
    """A log of ash-coated goat cheese, one end sliced to show the chalky white paste and the grey ash line."""
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    pts = along(x0, y0, x1, y1, lambda t: R * (0.96 + 0.04 * math.sin(t * 9)), 30)
    out = [cast(D, (x0 + x1) / 2 + 4, (y0 + y1) / 2 + R * 0.9, L * 0.55, R * 0.3, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#B8B8B0", "#6E706C", "#2E302E"), seed, sdir=(0, 1), sk=0.25, angle=ang, n=40, slen=(6, 20), sw=(1, 3),
                       cols=["#D8D8D0", "#4A4C4A", "#9A9C96"], inkw=1.8, hi=0.35))
    out.append(specks(seed + 1, bbox(pts), ["#FFFFFF", "#E8E8E0"], int(L * 0.4), (0.6, 1.4), (0.3, 0.7)))
    end = rot(ell_pts(x1, y1, R * 0.3, R, 0, 360, 22), x1, y1, ang)
    out.append(f'<path d="{smooth_closed(end)}" fill="#3A3C3A"/>')
    inner = rot(ell_pts(x1 + 1, y1, R * 0.26, R * 0.88, 0, 360, 22), x1, y1, ang)
    out.append(f'<path d="{smooth_closed(inner)}" fill="#FBFAF4"/>')
    out.append(f'<path d="{smooth_closed(rot(ell_pts(x1 + 1, y1, R * 0.03, R * 0.6, 0, 360, 12), x1, y1, ang))}" fill="#9A9A92" opacity="0.6"/>')
    # a slice cut off, lying flat
    sx, sy = x1 + R * 1.4, y1 + R * 0.7
    out.append(cast(D, sx + 3, sy + 6, R * 0.95, R * 0.3, strength=0.35, seed=seed + 2))
    out.append(f'<path d="{smooth_closed(ell_pts(sx, sy, R * 0.98, R * 0.42, 0, 360, 24))}" fill="#3A3C3A"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(sx, sy - 1, R * 0.88, R * 0.36, 0, 360, 24))}" fill="#FBFAF4"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(sx, sy - 1, R * 0.5, R * 0.03, 0, 360, 12))}" fill="#9A9A92" opacity="0.6"/>')
    out.append(ink(smooth_closed(ell_pts(sx, sy, R * 0.98, R * 0.42, 0, 360, 24)), INK, 1.2, seed + 3, 1, 0.6))
    return "".join(out)


def blue_wedge(D, cx, cy, s, seed):
    """A wedge of sheep's-milk blue: ivory paste marbled with blue-green veins."""
    rnd = random.Random(seed)
    A, B, C = (cx - s * 0.7, cy + s * 0.3), (cx + s * 0.6, cy - s * 0.1), (cx + s * 0.5, cy + s * 0.45)
    h = s * 0.42
    front = [A, C, (C[0], C[1] - h), (A[0], A[1] - h * 0.9)]
    topf = [(A[0], A[1] - h * 0.9), (C[0], C[1] - h), (B[0], B[1] - h)]
    out = [cast(D, cx, cy + s * 0.45, s * 0.8, s * 0.1, strength=0.4, seed=seed)]
    for k, f in enumerate((front, topf)):
        pts = poly_pts(f, 10, seed + k, 0.5)
        out.append(painted(D, pts, ("#FFFEF6", "#F2EEDC", "#C4BCA0"), seed + k, sdir=(0.2, 1), sk=0.08 if k else 0.12, angle=-12, n=14, inkw=1.6, hi=0.4))
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        v = []
        for _ in range(int(s * 0.4)):
            x0_, y0_ = rnd.uniform(*bbox(f)[0::2]), rnd.uniform(*bbox(f)[1::2])
            pts_v = [(x0_, y0_), (x0_ + rnd.uniform(-8, 8), y0_ + rnd.uniform(-4, 4)), (x0_ + rnd.uniform(-12, 12), y0_ + rnd.uniform(-6, 6))]
            v.append(taper(pts_v, rnd.uniform(1.5, 3.5), 0.5, rnd.choice(["#4A6A7A", "#2E4E5E", "#6A8A8A"]), rnd.uniform(0.5, 0.9)))
        out.append(f'<g {cid}>{"".join(v)}</g>')
    return "".join(out)


def grape_cluster(D, x, y, s, seed, pal=("#B88AC8", "#6A3A7A", "#30123E")):
    rnd = random.Random(seed)
    out = []
    pts = []
    for row in range(5):
        n = 5 - row
        for i in range(n):
            pts.append((x + (i - (n - 1) / 2) * s * 1.6 + rnd.uniform(-1.5, 1.5), y + row * s * 1.35 + rnd.uniform(-1, 1)))
    for (px, py) in pts:
        out.append(painted(D, blob_pts(px, py, s, s * 1.08, rnd.randint(1, 999), 0.04, 12), pal, rnd.randint(1, 999), sdir=(0.6, 0.7), sk=0.25, n=4, inkw=1, hi=0.4))
        out.append(f'<circle cx="{px - s * 0.35:.1f}" cy="{py - s * 0.4:.1f}" r="{s * 0.22:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(taper([(x, y - s), (x + 3, y - s * 2.2), (x + 10, y - s * 3)], 3, 2, "#6A5A2A"))
    return "".join(out)


def walnut(D, x, y, r, seed, half=False):
    rnd = random.Random(seed)
    out = [cast(D, x + 2, y + r * 0.8, r, r * 0.25, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(x, y, r, r * 0.85, seed, 0.08, 14), ("#E8C08A", "#B88A52", "#6A4620"), seed, sk=0.25, n=8, inkw=1.2, hi=0.4))
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        out.append(pline([(x + math.cos(a) * r * 0.2, y + math.sin(a) * r * 0.2), (x + math.cos(a + 0.4) * r * 0.75, y + math.sin(a + 0.4) * r * 0.6)], "#7A5226", 1, rnd.randint(1, 99), 0.6, 1))
    out.append(pline([(x, y - r * 0.85), (x + 1, y), (x, y + r * 0.85)], "#6A4620", 1.4, seed, 0.7, 1))
    return "".join(out)


def knife(D, x0, y0, x1, y1, seed, handle=("#C8925A", "#8A5A2E", "#4A2A10"), bl=0.55):
    """A cheese knife: steel blade with a forked tip and a wooden handle with brass rivets."""
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    mx, my = x0 + (x1 - x0) * bl, y0 + (y1 - y0) * bl
    blade = along(x0, y0, mx, my, lambda t: 7 * (0.55 + 0.45 * t) if t > 0.06 else 4, 14)
    out = [painted(D, blade, ZINC, seed, sdir=(0, 1), sk=0.2, angle=ang, n=8, inkw=1.4, hi=0.6)]
    hdl = along(mx, my, x1, y1, lambda t: 6.5 if 0.05 < t < 0.95 else 5, 14)
    out.append(painted(D, hdl, handle, seed + 1, sdir=(0, 1), sk=0.25, angle=ang, n=10, inkw=1.4, hi=0.4))
    for t in (0.25, 0.75):
        px, py = mx + (x1 - mx) * t, my + (y1 - my) * t
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#F2D488" stroke="#8A6A2A" stroke-width="0.8"/>')
    return "".join(out)


@design("le-fromage")
def le_fromage():
    D = Doc2("fr-fm")
    # slate-blue kitchen table in low evening light
    out = [sky(D, [(0, "#3E4A5A"), (1, "#2A3240")], 301, 600, ["#4E5A6C", "#1E2430", "#5A687A"], 120, angle=-6, sop=(0.06, 0.15))]
    out.append(soft_glow(D, 200, 330, 330, "#FFE6B8", 0.28))
    out.append(blooms(302, ["#5A687A", "#1E2430"], 6, (0, 200, 600, 600), (100, 180), (0.08, 0.14)))
    # olive-wood board (round, 3/4 view)
    cx, cy, rx, ry = 300, 412, 244, 142
    out.append(cast(D, cx + 16, cy + 28, rx + 4, ry * 0.9, strength=0.55, seed=303))
    out.append(painted(D, ell_pts(cx, cy + 14, rx, ry, 0, 360, 48), ("#C89A62", "#8A5A2E", "#4A2A10"), 304, sdir=(0, 1), sk=0.15, angle=0, n=30, inkw=2, hi=0.3))
    bd = smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 48))
    out.append(f'<path d="{bd}" fill="#D8AE74"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(305)
    gr = []
    for k in range(16):
        r1 = 20 + k * 15
        gr.append(f'<path d="{blob(cx + 40 + rnd.uniform(-6, 6), cy + 10, r1, r1 * 0.55, 306 + k, 0.08, 20)}" fill="none" stroke="{rnd.choice(["#A8783E", "#8A5E2A", "#C8955A"])}" stroke-width="{rnd.uniform(1, 2.6):.1f}" opacity="0.45"/>')
    gr.append(light_over(D, bd, "#FFF0D0", 0.35, 0, 0, 0.7, 0.8))
    gr.append(shade_over(D, bd, "#3A1A06", 0.35, 0, 0, 1, 1, 0.55))
    out.append(f'<g {cid}>{"".join(gr)}</g>')
    out.append(ink(bd, INK, 2, 307, 2, 0.7))
    # cheeses and their company
    out.append(knife(D, 120, 330, 250, 296, 323))
    out.append(camembert(D, 190, 384, 82, 310))
    out.append(cheese_wedge(D, 392, 366, 100, 311))
    out.append(grape_cluster(D, 486, 418, 10, 314))
    out.append(blue_wedge(D, 166, 478, 66, 313))
    out.append(chevre_log(D, 290, 486, 402, 462, 26, 312))
    for k, (x, y) in enumerate(((84, 430), (98, 458), (444, 504))):
        out.append(walnut(D, x, y, 12, 315 + k))
    # a fig cut open
    fx, fy = 286, 412
    out.append(painted(D, blob_pts(fx, fy, 20, 18, 320, 0.08, 14), ("#A87AA8", "#6A3A6A", "#30122E"), 320, sk=0.2, n=6, inkw=1.4, hi=0.3))
    out.append(f'<path d="{blob(fx + 2, fy + 1, 14, 12, 321, 0.1, 12)}" fill="#E25A5A"/>' + specks(322, (fx - 9, fy - 8, fx + 12, fy + 9), ["#FFF0C8", "#F6C8A0"], 20, (0.6, 1.3), (0.7, 1)))
    # crumbs of comté
    for _ in range(8):
        x, y = rnd.uniform(330, 450), rnd.uniform(404, 426)
        out.append(f'<path d="{blob(x, y, 2.6, 1.9, rnd.randint(1, 999), 0.3, 6)}" fill="#F4D978"/>')
    # lettering
    out.append(letters(D, 300, 152, "le fromage", SERIF_IT, 116, "#FFF0C8", ["#FFFFFF", "#F6DC8A", "#FFE8B0"], 330, max_w=440,
                       shadow="#141A24", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 198, "TOUJOURS AVANT LE DESSERT", "#F2C860", font=JOS, size=19, ls=4, line_w=26, gap=12, max_w=380))
    return finish_f(D, out, 331, "#1A1A24")


# ================================================================ 4. Mamie — the orange cocotte on the stove
def cocotte(D, cx, base, w, h, seed, pal=FLAME):
    """Round enamelled cast-iron casserole: flame-gradient enamel (light at the top), black rim, loop handles, a domed
    lid with a cream knob, set slightly ajar; a wooden spoon resting in it."""
    out = [cast(D, cx + 10, base + 2, w * 0.62, 12, strength=0.5, seed=seed)]
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    body = [(l, top + 8), (l - 4, top + h * 0.45), (l + 6, base - 12), (l + 30, base), (r - 30, base), (r - 6, base - 12), (r + 4, top + h * 0.45), (r, top + 8)]
    # side handles
    for sg in (-1, 1):
        hx = cx + sg * (w / 2 + 2)
        hp = [(hx, top + 18), (hx + sg * 22, top + 14), (hx + sg * 28, top + 26), (hx + sg * 20, top + 34), (hx, top + 34)]
        out.append(painted(D, hp, pal, seed + 10 + sg, sdir=(0.5, 1), sk=0.25, n=5, inkw=1.6, hi=0.4))
        out.append(f'<path d="{blob(hx + sg * 14, top + 25, 6, 4, seed + sg, 0.1, 8)}" fill="#2A1206"/>')
    bd = smooth_closed(body)
    g = D.lin([(0, "#FFC060"), (0.25, pal[1]), (0.75, dk(pal[1], 0.15)), (1, pal[2])])
    out.append(f'<path d="{bd}" fill="{g}"/>')
    out.append(strokes(D.nid(), bd, bbox(body), [pal[0], pal[2], "#FFD08A"], seed, n=60, angle=-88, length=(14, 40), width=(1, 4), opacity=(0.15, 0.4)))
    out.append(shade_over(D, bd, "#3A0A00", 0.5, 0, 0, 1, 0, 0.5))
    out.append(taper([(l + 14, top + 22), (l + 10, top + h * 0.5), (l + 20, base - 18)], 4, 10, "#FFE6B8", 0.55))
    out.append(ink(bd, INK, 2.2, seed + 1, 2, 0.75))
    # black enamel rim band
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 8, w / 2 + 1, 12, 0, 360, 30))}" fill="#1E1A1A"/>')
    # stew peeking under the ajar lid
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 8, w / 2 - 5, 9, 0, 360, 20))}" fill="#8A2A14"/>')
    for k in range(5):
        x = cx - w * 0.44 + k * w * 0.05
        out.append(f'<path d="{blob(x, top + 6 + (k % 2) * 2, 5, 3.2, seed + 20 + k, 0.2, 8)}" fill="{["#E8781E", "#C83A1A", "#F2B04A", "#6E8A2E"][k % 4]}"/>')
    # lid, lifted on the right
    lid_tr = f'translate({w * 0.07:.1f} -3)'
    lid = [(l - 4, top + 2), (l + w * 0.1, top - 22), (cx, top - 34), (r - w * 0.1, top - 22), (r + 4, top + 2), (cx, top + 10)]
    out.append(f'<g transform="{lid_tr}">')
    lg = D.lin([(0, "#FFC878"), (0.5, pal[1]), (1, pal[2])])
    ld = smooth_closed(lid)
    out.append(f'<path d="{ld}" fill="{lg}"/>')
    out.append(strokes(D.nid(), ld, bbox(lid), [pal[0], pal[2]], seed + 3, n=24, angle=-10, length=(14, 40), width=(1, 3), opacity=(0.15, 0.4)))
    out.append(taper([(l + w * 0.12, top - 14), (cx - w * 0.1, top - 28), (cx + w * 0.1, top - 30)], 3, 7, "#FFE8C0", 0.6))
    out.append(ink(ld, INK, 2, seed + 4, 2, 0.75))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 2, w / 2 + 4, 6, 0, 180, 14) + [(l - 4, top + 2)])}" fill="#1E1A1A"/>')
    # knob
    out.append(painted(D, [(cx - 16, top - 32), (cx - 12, top - 48), (cx + 12, top - 48), (cx + 16, top - 32)], CREME, seed + 5, sk=0.2, n=5, inkw=1.6, hi=0.5))
    out.append(painted(D, ell_pts(cx, top - 48, 13, 4, 0, 360, 16), CREME, seed + 6, sk=0.1, n=3, inkw=1.2, hi=0.5))
    out.append("</g>")
    return "".join(out)


def wall_tiles(D, x0, y0, x1, y1, s, seed, ground="#F8F4EA", motif="#3A6AB0"):
    """Small square kitchen tiles with a hand-painted blue flower in every other tile (carreaux de faïence)."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#D8CCB4"/>']
    j = 0
    y = y0
    while y < y1:
        x = x0
        i = 0
        while x < x1:
            c = mix(ground, rnd.choice(["#FFFFFF", "#E8DFCC"]), rnd.uniform(0, 0.5))
            out.append(f'<path d="{hg.org_rect(x + 1.5, y + 1.5, s - 3, s - 3, rnd.randint(1, 9999), 0.4, 10, 2)}" fill="{c}"/>')
            if (i + j) % 2 == 0:
                fx, fy = x + s / 2, y + s / 2
                for k in range(4):
                    a = math.radians(45 + k * 90)
                    out.append(f'<path d="{blob(fx + math.cos(a) * s * 0.14, fy + math.sin(a) * s * 0.14, s * 0.13, s * 0.07, rnd.randint(1, 999), 0.1, 8, math.degrees(a))}" fill="{motif}" opacity="0.85"/>')
                out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{s * 0.06:.1f}" fill="#E8B830"/>')
            else:
                for (cx_, cy_) in ((x + 3, y + 3), (x + s - 3, y + 3), (x + 3, y + s - 3), (x + s - 3, y + s - 3)):
                    out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{s * 0.06:.1f}" fill="{motif}" opacity="0.6"/>')
            out.append(f'<path d="M {x + 4:.1f} {y + 5:.1f} l {s * 0.3:.1f} 0" stroke="#FFFFFF" stroke-width="2" opacity="0.6" stroke-linecap="round"/>')
            x += s
            i += 1
        y += s
        j += 1
    return "".join(out)


def copper_pan(D, x, hook_y, r, seed, handle_len=70):
    """A copper saucepan hanging by its long iron handle: rosy copper, bright tin-lined rim showing."""
    out = []
    hx, hy = x, hook_y
    by = hook_y + handle_len
    out.append(taper([(hx, hy), (hx, by - r * 0.7)], 7, 7, "#3A3A40"))
    out.append(taper([(hx - 1.5, hy), (hx - 1.5, by - r * 0.7)], 1.6, 1.6, "#9AA0A8", 0.8))
    out.append(f'<circle cx="{hx}" cy="{hy + 6}" r="4" fill="none" stroke="#F4EAD8" stroke-width="2.4"/>')
    pan = blob_pts(x, by + r * 0.3, r, r, seed, 0.03, 20)
    out.append(cast(D, x + 8, by + r * 0.4, r * 1.05, r * 1.0, strength=0.25, seed=seed))
    out.append(painted(D, pan, COPPER, seed, sdir=(0.7, 0.5), sk=0.25, angle=-60, n=20, inkw=1.8, hi=0.5, hik=0.1))
    out.append(f'<path d="{blob(x, by + r * 0.3, r * 0.7, r * 0.7, seed + 1, 0.03, 16)}" fill="none" stroke="#E8A070" stroke-width="2" opacity="0.6"/>')
    out.append(taper([(x - r * 0.55, by + r * 0.0), (x - r * 0.4, by - r * 0.35)], 3, 6, "#FFE2C8", 0.8))
    for k in range(3):
        out.append(f'<circle cx="{hx + (k - 1) * 5:.1f}" cy="{by - r * 0.62:.1f}" r="1.8" fill="#5A3A20"/>')
    return "".join(out)


def herb_bunch(D, x, y, L, seed, pal=SAGE):
    """A bunch of dried herbs (thyme, bay) hanging upside down from a string."""
    rnd = random.Random(seed)
    out = [ink(f"M {x} {y - 30} L {x} {y}", "#C8A878", 1.6, seed, 1, 0.9)]
    for k in range(14):
        a = math.radians(90 + rnd.uniform(-22, 22))
        x1, y1 = x + math.cos(a) * L * rnd.uniform(0.7, 1), y + math.sin(a) * L * rnd.uniform(0.7, 1)
        out.append(pline([(x, y), ((x + x1) / 2 + rnd.uniform(-3, 3), (y + y1) / 2), (x1, y1)], "#6A5A3A", 1.3, seed + k, 0.8, 1))
        for j in range(5):
            t = 0.3 + j * 0.14
            px, py = x + (x1 - x) * t, y + (y1 - y) * t
            out.append(f'<path d="{blob(px + rnd.uniform(-3, 3), py, rnd.uniform(2.4, 4), rnd.uniform(1.2, 2), rnd.randint(1, 999), 0.15, 8, rnd.uniform(40, 140))}" fill="{rnd.choice(pal)}" opacity="0.9"/>')
    out.append(f'<path d="{hg.org_rect(x - 7, y - 4, 14, 8, seed, 0.3, 6, 2)}" fill="#C8382E"/>')
    return "".join(out)


@design("mamie")
def mamie():
    D = Doc2("fr-mm")
    out = [paper(D.nid(), "#F6EBDA", FLECK, 401)]
    out.append(wall_tiles(D, -10, 230, 610, 452, 34, 402))
    out.append(shade_over(D, "M -10 230 L 610 230 L 610 452 L -10 452 Z", "#3A2A1A", 0.3, 0, 0, 1, 0, 0.5))
    out.append(soft_glow(D, 300, 340, 260, "#FFE8B0", 0.4))
    # cream plaster above with a wooden rail for the pans
    out.append(painted(D, rect_pts(-10, 222, 610, 236, 30, 403, 0.4), WOOD, 403, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.4))
    out.append(copper_pan(D, 470, 236, 34, 404, 50) + copper_pan(D, 530, 236, 26, 405, 60))
    out.append(herb_bunch(D, 90, 260, 54, 406))
    out.append(herb_bunch(D, 132, 252, 46, 407, ("#7A8A4A", "#A8B070", "#5E6A30")))
    # stove top: black enamel range top, cream enamel front, chrome rail
    out.append(painted(D, rect_pts(-10, 456, 610, 478, 30, 408, 0.4), ("#4A4A50", "#262628", "#0E0E10"), 408, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.6, hi=0.3))
    front = "M -10 478 L 610 478 L 610 620 L -10 620 Z"
    out.append(f'<path d="{front}" fill="{D.lin([(0, "#F6EEDC"), (1, "#DCCCAC")])}"/>')
    out.append(strokes(D.nid(), front, (-40, 478, 610, 620), ["#FFFFFF", "#C8B490"], 409, n=60, angle=-2, length=(30, 90), width=(1, 3), opacity=(0.15, 0.35)))
    # oven door with rounded corners, a temperature dial, the chrome handle bar
    door = hg.org_rect(96, 516, 408, 110, 410, 0.6, 20, 14)
    out.append(f'<path d="{door}" fill="#EFE4CC"/>')
    out.append(shade_over(D, door, "#5A4A2A", 0.3, 0, 0, 0, 1, 0.3))
    out.append(ink(door, "#8A7A5A", 2, 411, 2, 0.7))
    out.append(f'<path d="{hg.org_rect(112, 532, 376, 4, 412, 0.3, 20, 2)}" fill="#FFFFFF" opacity="0.6"/>')
    win = hg.org_rect(150, 546, 180, 50, 424, 0.5, 14, 8)
    out.append(f'<path d="{win}" fill="{D.lin([(0, "#3A2010"), (0.6, "#C8601E"), (1, "#FFB050")])}"/>')
    out.append(soft_glow(D, 240, 580, 80, "#FFB050", 0.4))
    out.append(taper([(160, 552), (190, 552)], 3, 3, "#FFFFFF", 0.5))
    out.append(ink(win, "#5A4A3A", 2.2, 425, 1, 0.8))
    for x in (60, 540):
        out.append(painted(D, ell_pts(x, 498, 11, 11, 0, 360, 14), ("#3A3A40", "#1E1E22", "#0A0A0C"), 413 + x, sk=0.2, n=3, inkw=1.2, hi=0.4))
        out.append(f'<path d="M {x} 498 l 0 -8" stroke="#E8E8E8" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(taper([(110, 500), (490, 500)], 8, 8, "#9AA0A8"))
    out.append(taper([(110, 498), (490, 498)], 2.4, 2.4, "#FFFFFF", 0.85))
    for x in (110, 490):
        out.append(painted(D, rect_pts(x - 5, 494, x + 5, 512, 6, 414 + x, 0.2), ZINC, 414 + x, sk=0.2, n=2, inkw=1, hi=0.5))
    # red checked torchon folded over the handle bar
    tw = [(372, 496), (432, 494), (440, 560), (430, 588), (384, 592), (368, 562)]
    out.append(cloth(D, tw, ROUGE[1], 415, cell=10, rot_=4, light=(0, 0, 1, 1), folds=[((392, 502), (398, 542), (394, 584))]))
    out.append(ink(smooth_open([(368, 500), (402, 492), (440, 498)]), INK, 1.8, 416, 1, 0.7))
    # the cocotte, simmering, a wooden spoon slipped under the lid
    out.append(cocotte(D, 300, 458, 226, 150, 417))
    out.append(taper([(212, 318), (176, 268), (160, 238)], 9, 7, "#C8925A"))
    out.append(taper([(210, 317), (174, 267), (158, 237)], 2.2, 1.6, "#F2D0A0", 0.8))
    out.append(ink(smooth_open([(214, 318), (178, 268), (162, 238)]), INK, 1.2, 423, 1, 0.5))
    # a saucer with a taste of the stew, left
    out.append(cast(D, 108, 456, 46, 6, strength=0.35, seed=418))
    out.append(painted(D, ell_pts(104, 450, 46, 10, 0, 360, 20), WHITE, 419, sk=0.15, n=6, inkw=1.4, hi=0.4))
    out.append(f'<path d="{blob(104, 448, 22, 5, 420, 0.2, 10)}" fill="#8A2A14" opacity="0.85"/>')
    for k in range(4):
        out.append(f'<path d="{blob(94 + k * 7, 447, 3, 2, 421 + k, 0.2, 6)}" fill="{["#E8781E", "#F2B04A", "#6E8A2E", "#C83A1A"][k]}"/>')
    out.append(steam(222, 296, 60, 422, "#FFFFFF", 2, 26, 7, 0.6))
    # lettering
    out.append(letters(D, 300, 152, "Mamie", SERIF_IT, 138, ROUGE[2], [ROUGE[1], "#5A0A0A", "#E8564A"], 421, max_w=360,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#F8A090"))
    out.append(ruled(300, 200, "RESSERS-TOI, MON CHÉRI", BLEU[2], font=JOS, size=19, ls=4, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 422)


# ================================================================ 5. Cocorico ! — the rooster on the gate at sunrise
def rooster(D, ox, oy, s, seed):
    """A French farm rooster crowing, facing left, head thrown back: red comb and wattles, golden-orange hackles
    over the shoulders, chestnut saddle, iridescent green-black sickle tail, blue-black breast, slate legs with
    spurs gripping a rail. (ox, oy) = feet on the rail, s = scale (about 1.7 s tall)."""
    rnd = random.Random(seed)
    P = lambda x, y: (ox + x * s, oy + y * s)
    out = []
    TAIL = [("#2E6A4A", "#123A2A", "#06140E"), ("#2A4E7A", "#122A4A", "#060E1E")]
    # tail: big sickles arching up and over to the right, coverts below
    base = P(0.38, -0.82)
    for k in range(11):
        sw_ = k / 10
        top = P(0.55 + sw_ * 0.45, -1.62 + sw_ * 0.55)
        end = P(0.8 + sw_ * 0.42, -0.95 + sw_ * 0.5 + rnd.uniform(-0.05, 0.05))
        mid = ((base[0] + top[0]) / 2 - s * 0.06, (base[1] + top[1]) / 2 - s * 0.05)
        pal = TAIL[k % 2]
        c = catmull([base, mid, top, end], 6)
        out.append(taper(c, s * 0.16, s * 0.025, pal[1 if k % 3 else 2]))
        out.append(taper([(x - 1.5, y - 1.5) for x, y in c[:len(c) * 2 // 3]], s * 0.035, s * 0.01, "#7ACB9A" if k % 2 == 0 else "#8AB0E8", 0.55))
    for k in range(7):
        a = math.radians(-60 + k * 14)
        tip = (base[0] + math.cos(a) * s * 0.5, base[1] + math.sin(a) * s * 0.42)
        out.append(taper([(base[0] - s * 0.05, base[1] + s * 0.05), ((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2 - s * 0.03), tip], s * 0.1, s * 0.02, rnd.choice(["#1E3A2E", "#0E1E1A", "#24405A"])))
    # body: an egg tilted up toward the breast
    body = rot(blob_pts(ox + 0.05 * s, oy - 0.66 * s, 0.5 * s, 0.32 * s, seed, 0.03, 20), ox + 0.05 * s, oy - 0.66 * s, -18)
    out.append(painted(D, body, ("#D87A42", "#9A3E1A", "#481406"), seed, sdir=(0.2, 1), sk=0.22, angle=-15, n=40, inkw=2, hi=0.35))
    # saddle hackles: long chestnut-gold feathers draping down the back
    for k in range(12):
        x0 = 0.05 + k * 0.035
        out.append(taper([P(x0, -0.95 + k * 0.005), P(x0 + 0.1, -0.78), P(x0 + 0.14, -0.58)], s * 0.06, s * 0.012, rnd.choice(["#F2A040", "#C8621E", "#FFD27A"]), 0.85))
    # wing folded on the side
    wing = rot(blob_pts(ox + 0.1 * s, oy - 0.62 * s, 0.33 * s, 0.16 * s, seed + 1, 0.04, 16), ox + 0.1 * s, oy - 0.62 * s, -10)
    out.append(painted(D, wing, ("#E89A4A", "#A8501A", "#4A1806"), seed + 2, sdir=(0.2, 1), sk=0.25, angle=-10, n=20, inkw=1.6, hi=0.4))
    for k in range(4):
        y = -0.68 + k * 0.045
        out.append(pline([P(-0.15, y - 0.02), P(0.1, y), P(0.38, y + 0.04)], "#3E1206", 1.3, seed + 3 + k, 0.45, 1))
    out.append(taper([P(-0.1, -0.5), P(0.2, -0.47), P(0.44, -0.54)], s * 0.09, s * 0.02, "#1E3A4A", 0.9))
    # breast, blue-black, puffed forward
    breast = rot(blob_pts(ox - 0.3 * s, oy - 0.74 * s, 0.25 * s, 0.33 * s, seed + 4, 0.04, 16), ox - 0.3 * s, oy - 0.74 * s, -25)
    out.append(painted(D, breast, ("#46567A", "#1A2238", "#06080E"), seed + 5, sdir=(0.6, 0.8), sk=0.22, angle=-70, n=24, inkw=1.6, hi=0.35))
    # neck, stretched up and back, cape of golden hackles over the shoulders
    neck = [P(-0.6, -1.4), P(-0.45, -1.52), P(-0.3, -1.38), P(-0.12, -1.0), P(-0.02, -0.86), P(-0.3, -0.8), P(-0.5, -0.92), P(-0.6, -1.15)]
    out.append(painted(D, neck, ("#FFD884", "#F09A2E", "#A8501A"), seed + 6, sdir=(0.6, 0.6), sk=0.18, angle=-105, n=30, inkw=1.8, hi=0.45))
    for k in range(20):
        t = k / 19
        x0, y0 = -0.58 + t * 0.32, -1.36 + t * 0.12
        out.append(taper([P(x0, y0), P(x0 + 0.06 + t * 0.06, y0 + 0.28), P(x0 + 0.1 + t * 0.12, y0 + 0.56 - t * 0.08)], s * 0.055, s * 0.008, rnd.choice(["#FFE8A8", "#C8621E", "#F6B04A", "#E8862A"]), 0.85))
    # head, tipped back, beak open to the sky
    head = rot(blob_pts(ox - 0.5 * s, oy - 1.47 * s, 0.12 * s, 0.1 * s, seed + 7, 0.05, 14), ox - 0.5 * s, oy - 1.47 * s, -30)
    out.append(painted(D, head, ("#FFC870", "#E8862A", "#9A4A14"), seed + 8, sk=0.15, n=8, inkw=1.6, hi=0.4))
    comb = [P(-0.6, -1.55), P(-0.62, -1.68), P(-0.55, -1.62), P(-0.52, -1.76), P(-0.46, -1.64), P(-0.4, -1.74), P(-0.37, -1.6), P(-0.3, -1.64), P(-0.34, -1.5), P(-0.48, -1.53)]
    out.append(painted(D, comb, ("#FF8A7A", "#E0261E", "#8A0A0A"), seed + 9, sdir=(0.3, 1), sk=0.2, n=12, inkw=1.5, hi=0.45))
    beak_u = [P(-0.6, -1.5), P(-0.78, -1.66), P(-0.58, -1.44)]
    beak_l = [P(-0.6, -1.42), P(-0.78, -1.5), P(-0.57, -1.38)]
    for k, bk in enumerate((beak_u, beak_l)):
        out.append(painted(D, bk, ("#FFE8A0", "#E8C050", "#9A7A20"), seed + 10 + k, sk=0.15, n=3, inkw=1.3, hi=0.5))
    out.append(f'<path d="{pd([P(-0.59, -1.44), P(-0.72, -1.57), P(-0.71, -1.5)])}" fill="#8A1A1A"/>')
    wattle = [P(-0.58, -1.38), P(-0.56, -1.24), P(-0.47, -1.22), P(-0.44, -1.34)]
    out.append(painted(D, wattle, ("#FF8A7A", "#E0261E", "#8A0A0A"), seed + 12, sk=0.2, n=4, inkw=1.3, hi=0.4))
    out.append(f'<path d="{blob(*P(-0.4, -1.42), s * 0.05, s * 0.04, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    ex, ey = P(-0.49, -1.5)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.032:.1f}" fill="#F6A81C"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.017:.1f}" fill="#1A0A04"/>')
    # feathered thighs, slate shanks, spurs, toes round the rail
    for k, lx in enumerate((-0.14, 0.12)):
        out.append(painted(D, rot(blob_pts(ox + (lx + 0.02) * s, oy - 0.4 * s, 0.1 * s, 0.13 * s, seed + 20 + k, 0.05, 12), ox + lx * s, oy - 0.4 * s, -10),
                           ("#C86A3A", "#7A2E12", "#3A1006"), seed + 20 + k, sk=0.2, n=4, inkw=1.2, hi=0.3))
        knee, foot = P(lx, -0.3), P(lx - 0.03, -0.02)
        out.append(taper([knee, foot], s * 0.06, s * 0.045, "#8A98A8"))
        out.append(taper([(knee[0] - 1.5, knee[1]), (foot[0] - 1.5, foot[1])], s * 0.015, s * 0.01, "#D8E0E8", 0.7))
        out.append(taper([P(lx + 0.01, -0.12), P(lx + 0.08, -0.15)], s * 0.03, s * 0.008, "#5A6878"))
        for t in (-0.1, 0.0, 0.09):
            out.append(taper([foot, (foot[0] + t * s, foot[1] + s * 0.035)], s * 0.035, s * 0.022, "#6A7888"))
    return "".join(out)


def church_steeple(D, x, base, h, col, seed, cock=True):
    """A village church in silhouette: nave, square tower, slate spire topped with a weathercock."""
    w = h * 0.22
    out = [f'<path d="{pd([(x - h * 0.5, base), (x - h * 0.5, base - h * 0.3), (x - h * 0.1, base - h * 0.42), (x + w, base - h * 0.42), (x + w, base)])}" fill="{col}"/>']
    out.append(f'<path d="{pd([(x - w / 2, base), (x - w / 2, base - h * 0.62), (x + w / 2, base - h * 0.62), (x + w / 2, base)])}" fill="{col}"/>')
    out.append(f'<path d="{pd([(x - w / 2 - 2, base - h * 0.62), (x, base - h), (x + w / 2 + 2, base - h * 0.62)])}" fill="{col}"/>')
    out.append(f'<path d="M {x} {base - h} l 0 {-h * 0.06:.1f}" stroke="{col}" stroke-width="1.6"/>')
    if cock:
        cx_, cy_ = x, base - h * 1.07
        out.append(f'<path d="{pd([(cx_ - 5, cy_), (cx_ - 1, cy_ - 4), (cx_ + 1, cy_ - 7), (cx_ + 3, cy_ - 4), (cx_ + 6, cy_ - 6), (cx_ + 6, cy_), (cx_ + 1, cy_ + 1)])}" fill="{col}"/>')
    return "".join(out)


@design("cocorico")
def cocorico():
    D = Doc2("fr-co")
    out = [sky(D, [(0, "#6A8AC8"), (0.35, "#F2B8A0"), (0.6, "#FFD89A"), (0.8, "#FFF0C8")], 501, 470, ["#FFE0B8", "#F2A890", "#FFF4D8"], 70, angle=-3, sop=(0.05, 0.14))]
    sx, sy = 420, 396
    out.append(soft_glow(D, sx, sy, 300, "#FFF0B0", 0.85))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="44" fill="#FFF6D0"/>')
    for k, (x, y, w) in enumerate(((120, 250, 140), (470, 236, 110))):
        out.append(puff_cloud(D, x, y, w, 502 + k, pal=("#FFF0E0", "#F8C8B0", "#D89090"), op=0.7, rows=1))
    # distant fields and a village with its church
    out.append(hill(D, ridge([(-20, 400), (150, 386), (320, 396), (480, 382), (620, 392)], 503, 5), 470, ("#C8B8A8", "#A898A0", "#887888"), 504, inkw=0, n=20))
    rnd = random.Random(505)
    for k in range(8):
        x = 360 + k * 24 + rnd.uniform(-4, 4)
        hh = rnd.uniform(10, 16)
        out.append(f'<path d="{pd([(x, 398), (x, 398 - hh), (x + 9, 398 - hh - 7), (x + 18, 398 - hh), (x + 18, 398)])}" fill="#8A7480"/>')
        if rnd.random() < 0.5:
            out.append(f'<rect x="{x + 6:.1f}" y="{398 - hh * 0.6:.1f}" width="3" height="3.5" fill="#FFE2A0"/>')
    out.append(church_steeple(D, 486, 398, 84, "#7A6474", 506))
    out.append(hill(D, ridge([(-20, 432), (160, 420), (330, 430), (500, 414), (620, 424)], 507, 4), 520, ("#D8C878", "#B0A050", "#6E6A2E"), 508, inkw=1, inkop=0.35, n=60, lit="#FFF0A0"))
    # hedgerow
    for k in range(14):
        out.append(dab_crown(D, -10 + k * 48, 432 + rnd.uniform(-4, 4), rnd.uniform(18, 26), rnd.uniform(9, 13), [("#8AA060", "#5E7A3E", "#34502A")], 509 + k, n=16, size=(4, 7), inkw=0))
    # front: grass and the wooden farm gate
    out.append(hill(D, ridge([(-20, 470), (200, 462), (400, 468), (620, 460)], 530, 3), 620, ("#A8C060", "#6E9A3E", "#3A5E22"), 531, inkw=1.4, n=120, lit="#FFF0A0"))
    out.append(grass(532, (0, 470, 600, 610), ["#4E7A2E", "#8AB050", "#C8D870", "#3A5E22"], 260, (10, 26)))
    gate = OAK
    for x in (64, 536):
        out.append(painted(D, rect_pts(x - 13, 420, x + 13, 600, 20, 533 + x, 0.6), ("#B89A70", "#8A6A44", "#4A3418"), 533 + x, sdir=(1, 0), sk=0.25, angle=-90, n=20, inkw=2, hi=0.3))
        out.append(painted(D, [(x - 15, 424), (x, 410), (x + 15, 424)], ("#B89A70", "#8A6A44", "#4A3418"), 534 + x, sk=0.2, n=3, inkw=1.6, hi=0.3))
    brace = along(84, 556, 520, 474, lambda t: 8, 20)
    out.append(painted(D, brace, ("#D8BE94", "#A88A62", "#5E4628"), 549, sdir=(0, 1), sk=0.25, angle=-11, n=30, inkw=1.8, hi=0.4))
    for y in (470, 512, 554):
        out.append(painted(D, rect_pts(70, y - 9, 530, y + 9, 24, 540 + y, 0.6), ("#E8D2A8", "#BFA078", "#6E5434"), 540 + y, sdir=(0, 1), sk=0.25, angle=0, n=30, inkw=1.8, hi=0.45))
        for x in (90, 510):
            out.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#4A3418"/>')
    # the rooster on the top rail, crowing toward the sun
    out.append(rooster(D, 232, 462, 150, 551))
    # his song: little dashes rising from the open beak
    for k in range(3):
        x, y = 104 - k * 4, 222 - k * 14
        out.append(taper([(x + 8, y + 6), (x - 8, y - 4)], 4, 1.5, "#8A3418", 0.7))
    # lettering
    out.append(letters(D, 300, 140, f"Cocorico{NB}!", SERIF_IT, 120, BLEU[2], [BLEU[1], "#0A1A4A", "#4A70C0"], 552, max_w=440,
                       shadow="#FFF4DC", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 186, "LE COQ GAULOIS", ROUGE[2], font=JOS, size=19, ls=6, line_w=34, gap=14, max_w=380))
    return finish_f(D, out, 553)


# ================================================================ 6. Mont-Saint-Michel — at high tide, golden hour
def mont(D, cx, wl, s, seed):
    """The Mont seen from the south at sunset (light from the west / left): the granite island rising as a
    pyramid; ramparts and round towers along the foot; the village's stacked roofs climbing the south-east flank;
    trees on the north-west; the abbey in tiers (buttressed walls with tall lancets), the church with its slender
    neo-Gothic spire and the gilded archangel at the very top."""
    rnd = random.Random(seed)
    P = lambda x, y: (cx + x * s, wl - y * s)
    out = []
    lit = ("#F6D2B0", "#D8A890", "#8A6470")       # sunset-lit stone
    roof_c = "#5A4A62"
    rock_c = ("#B8908A", "#8A6470", "#4A3448")
    # granite rock: a broad cone
    rock = [P(-0.95, 0), P(-0.8, 0.12), P(-0.62, 0.24), P(-0.44, 0.42), P(-0.3, 0.52), P(0.3, 0.52), P(0.44, 0.38), P(0.62, 0.22), P(0.82, 0.1), P(0.98, 0)]
    out.append(painted(D, rock, rock_c, seed, sdir=(1, 0.2), sk=0.18, angle=-60, n=50, inkw=1.2, inkop=0.45, hi=0.35))
    # trees on the right (north-west is behind; here a wooded slope on the right flank)
    out.append(dab_crown(D, *P(0.52, 0.2), s * 0.24, s * 0.1, [("#8A9A72", "#5E6E52", "#36423A")], seed + 1, n=34, size=(3, 6), inkw=0))
    # village roofs climbing the left flank, in rows
    for row in range(6):
        y = 0.1 + row * 0.065
        x0 = -0.82 + row * 0.085
        x1 = -0.12 - row * 0.02
        x = x0
        while x < x1:
            w = rnd.uniform(0.05, 0.075)
            h = rnd.uniform(0.035, 0.06)
            bx, by = P(x, y)
            col = rnd.choice([lit[0], lit[1], "#E8C0A0"])
            out.append(f'<path d="{pd([(bx, by + 2), (bx, by - h * s), (bx + w * s, by - h * s), (bx + w * s, by + 2)])}" fill="{col}"/>')
            out.append(f'<path d="{pd([(bx - 1, by - h * s), (bx + w * s * 0.5, by - h * s - w * s * 0.42), (bx + w * s + 1, by - h * s)])}" fill="{roof_c}"/>')
            out.append(f'<path d="{pd([(bx + w * s * 0.5, by - h * s - w * s * 0.42), (bx + w * s + 1, by - h * s), (bx + w * s * 0.6, by - h * s)])}" fill="#3A2E46" opacity="0.6"/>')
            if rnd.random() < 0.5:
                out.append(f'<rect x="{bx + w * s * 0.35:.1f}" y="{by - h * s * 0.7:.1f}" width="2.2" height="3" fill="#FFE6A8"/>')
            x += w + rnd.uniform(0.0, 0.02)
    # abbey in tiers: lower monastic buildings, La Merveille, the church
    tiers = [(-0.36, 0.34, 0.42, 0.64), (-0.28, 0.27, 0.64, 0.84), (-0.2, 0.17, 0.84, 0.96)]
    for k, (xa, xb, ya, yb) in enumerate(tiers):
        pts = poly_pts([P(xa, ya), P(xa, yb), P(xb, yb), P(xb, ya)], 10, seed + 3 + k, 0.4)
        out.append(painted(D, pts, lit, seed + 3 + k, sdir=(1, 0.1), sk=0.14, angle=-90, n=20, inkw=1.3, inkop=0.55, hi=0.45))
        d = smooth_closed(pts)
        out.append(shade_over(D, d, "#3A2448", 0.5, 0, 0, 1, 0, 0.45))
        nb = int((xb - xa) / 0.06)
        for j in range(nb + 1):
            bx_, by_ = P(xa + j * (xb - xa) / nb, ya)
            out.append(f'<path d="M {bx_:.1f} {by_:.1f} L {bx_:.1f} {by_ - (yb - ya) * s * 0.92:.1f}" stroke="#7A5468" stroke-width="2" opacity="0.45"/>')
            if j < nb and (j + k) % 2 == 0:
                wx, wy = P(xa + (j + 0.5) * (xb - xa) / nb, ya + (yb - ya) * 0.75)
                out.append(f'<path d="M {wx - 1.6:.1f} {wy + (yb - ya) * s * 0.5:.1f} L {wx - 1.6:.1f} {wy:.1f} Q {wx:.1f} {wy - 4:.1f} {wx + 1.6:.1f} {wy:.1f} L {wx + 1.6:.1f} {wy + (yb - ya) * s * 0.5:.1f} Z" fill="#5A3E5A" opacity="0.75"/>')
        out.append(pline([P(xa, yb), P(xb, yb)], "#FFE8C8", 1.6, seed + k, 0.7, 1))
    # church roof, crossing tower, spire with little crockets, the archangel
    out.append(f'<path d="{pd([P(-0.21, 0.96), P(-0.05, 1.04), P(0.18, 0.96)])}" fill="{roof_c}"/>')
    tw = poly_pts([P(-0.055, 0.96), P(-0.055, 1.13), P(0.055, 1.13), P(0.055, 0.96)], 6, seed + 7, 0.3)
    out.append(painted(D, tw, lit, seed + 7, sdir=(1, 0), sk=0.3, n=4, inkw=1.1, inkop=0.6, hi=0.5))
    for k in range(3):
        wx, wy = P(-0.03 + k * 0.03, 1.08)
        out.append(f'<rect x="{wx - 1.2:.1f}" y="{wy - 4:.1f}" width="2.4" height="8" fill="#5A3E5A"/>')
    out.append(f'<path d="{pd([P(-0.05, 1.13), P(0.0, 1.66), P(0.05, 1.13)])}" fill="{roof_c}"/>')
    out.append(f'<path d="{pd([P(0.0, 1.13), P(0.0, 1.66), P(0.05, 1.13)])}" fill="#3A2E46"/>')
    out.append(pline([P(-0.05, 1.13), P(0.0, 1.66)], "#F2C8A8", 1.2, seed + 8, 0.8, 1))
    for k in range(7):
        t = 0.1 + k * 0.12
        x, y = P(-0.05 * (1 - t), 1.13 + 0.53 * t)
        out.append(f'<path d="M {x:.1f} {y:.1f} l -2.4 -1" stroke="{roof_c}" stroke-width="1.6" stroke-linecap="round"/>')
        x, y = P(0.05 * (1 - t), 1.13 + 0.53 * t)
        out.append(f'<path d="M {x:.1f} {y:.1f} l 2.4 -1" stroke="{roof_c}" stroke-width="1.6" stroke-linecap="round"/>')
    gx, gy = P(0, 1.7)
    out.append(soft_glow(D, gx, gy, 16, "#FFE07A", 0.9))
    out.append(f'<path d="{pd([(gx - 2, gy + 5), (gx - 1.4, gy - 3), (gx, gy - 6), (gx + 1.4, gy - 3), (gx + 2, gy + 5)])}" fill="#F6C21C"/>')
    out.append(f'<path d="M {gx + 0.6} {gy - 3} l 4 -6" stroke="#F6C21C" stroke-width="1.4"/>')
    out.append(f'<path d="M {gx - 2} {gy - 1} l -4 -3 M {gx + 2} {gy - 1} l 4 -3" stroke="#F6C21C" stroke-width="1.2"/>')
    # ramparts with round towers along the foot
    ram = poly_pts([P(-0.95, 0), P(-0.95, 0.075), P(0.92, 0.075), P(0.92, 0)], 14, seed + 9, 0.4)
    out.append(painted(D, ram, lit, seed + 9, sdir=(1, 0.2), sk=0.12, angle=0, n=30, inkw=1.2, inkop=0.5, hi=0.4))
    for k in range(46):
        bx, by = P(-0.94 + k * 0.04, 0.075)
        out.append(f'<rect x="{bx:.1f}" y="{by - 3:.1f}" width="{s * 0.022:.1f}" height="3" fill="{lit[1]}"/>')
    for x in (-0.9, -0.52, -0.16, 0.24, 0.62):
        tx, ty = P(x, 0)
        out.append(painted(D, rect_pts(tx - s * 0.04, ty - s * 0.12, tx + s * 0.04, ty, 6, int(x * 100) + seed, 0.3), lit, seed + int(x * 100), sdir=(1, 0), sk=0.3, angle=-90, n=4, inkw=1, inkop=0.5, hi=0.5))
        out.append(f'<path d="{pd([(tx - s * 0.045, ty - s * 0.12), (tx, ty - s * 0.18), (tx + s * 0.045, ty - s * 0.12)])}" fill="{roof_c}"/>')
    # sunset rim on the west faces
    out.append(pline([P(-0.95, 0.02), P(-0.62, 0.25), P(-0.44, 0.42)], "#FFD8A0", 2, seed + 10, 0.55, 1))
    return "".join(out)


@design("mont-saint-michel")
def mont_saint_michel():
    D = Doc2("fr-ms")
    out = [sky(D, [(0, "#4E5E9E"), (0.3, "#A888B4"), (0.6, "#F2A890"), (0.82, "#FFD49A")], 601, 430, ["#FFD8B8", "#C898B8", "#FFE8C8"], 80, angle=-3, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 104, 380, 240, "#FFE8A8", 0.8))
    out.append(f'<circle cx="104" cy="386" r="26" fill="#FFF4D0" opacity="0.95"/>')
    for k, (x, y, w) in enumerate(((470, 200, 150), (150, 130, 120), (520, 300, 90), (210, 280, 80))):
        out.append(puff_cloud(D, x, y, w, 602 + k, pal=("#FFE8D8", "#F2B8A8", "#B088A0"), op=0.72, rows=1))
    for (x, y, sz) in ((448, 268, 9), (474, 284, 7), (200, 330, 6)):
        out.append(seagull(x, y, sz, "#3E3448", 0.85))
    # flat horizon of the bay, distant coast
    out.append(f'<path d="{smooth_closed([(-10, 404), (120, 398), (280, 402), (420, 396), (610, 400), (610, 414), (-10, 414)])}" fill="#9A8AA0" opacity="0.7"/>')
    # high-tide sea with a golden path toward the sun
    wl = 412
    out.append(sea(D, wl - 2, 610, [(0, "#E8B0A0"), (0.35, "#8A90B8"), (1, "#2E3E6E")], 603, ["#FFE0C0", "#5A6A9A", "#B8A8C8"], 120))
    rnd = random.Random(604)
    for k in range(28):
        y = wl + 4 + k * 5 + rnd.uniform(0, 4)
        w = 26 + k * 2.2
        x = 104 + rnd.uniform(-w * 0.4, w * 0.4) + k * 1.2
        out.append(taper([(x - w / 2, y), (x + w / 2, y + rnd.uniform(-1, 1))], 1, 2.4 + k * 0.05, "#FFE8B0", rnd.uniform(0.4, 0.8)))
    # the Mont and its reflection
    cx, s = 318, 168
    m = mont(D, cx, wl, s, 605)
    out.append(f'<g transform="translate(0 {2 * wl}) scale(1 -1)" opacity="0.32">{reid(m, "r")}</g>')
    out.append(f'<rect x="0" y="{wl}" width="600" height="200" fill="{D.lin([(0, "#2E3E6E", 0.1), (0.5, "#2E3E6E", 0.45), (1, "#2E3E6E", 0.7)])}"/>')
    out.append(wave_lines(606, (0, wl + 4, 600, 600), ["#FFE0C0", "#C8B0C8", "#2E3E6A"], 70, (20, 60), 2.0, 2))
    out.append(m)
    # the footbridge on stilts reaching ashore to the right
    for k in range(10):
        x = cx + 0.4 * s + k * 20
        y = wl + 3 + k * 3.4
        out.append(f'<path d="M {x:.1f} {y:.1f} l 0 9" stroke="#3E3448" stroke-width="2" opacity="0.7"/>')
    out.append(taper([(cx + 0.4 * s, wl + 1), (cx + 0.4 * s + 200, wl + 35)], 3.5, 5.5, "#4A3E54", 0.9))
    out.append(taper([(cx + 0.4 * s, wl - 0.5), (cx + 0.4 * s + 200, wl + 32)], 1.2, 1.8, "#FFD8A8", 0.8))
    # lettering, low over the water
    out.append(letters(D, 300, 524, "Mont-Saint-Michel", SERIF_IT, 84, "#FFF6E6", ["#FFFFFF", "#FFE8D0"], 607, max_w=450,
                       shadow="#1A1A3A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 560, "À MARÉE HAUTE", "#FFE6B8", font=JOS, size=19, ls=6, line_w=34, gap=14, max_w=380))
    return finish_f(D, out, 608, "#2A1A3A")


# ================================================================ 7. Bon appétit ! — ratatouille in its tian
def indienne_tile(cell, bg, flower, leaf, dot, seed):
    """One tile of a Provençal indienne print: a small five-petal flower with leaves, sprigs and dots."""
    rnd = random.Random(seed)
    out = [f'<rect width="{cell}" height="{cell}" fill="{bg}"/>']
    for (fx, fy, s) in ((0.25, 0.25, 1.0), (0.75, 0.75, 1.0), (0.75, 0.25, 0.55), (0.25, 0.75, 0.55)):
        for dx in (-cell, 0, cell):
            for dy in (-cell, 0, cell):
                cx, cy = fx * cell + dx, fy * cell + dy
                r = cell * 0.09 * s
                if cx + 4 * r < 0 or cx - 4 * r > cell or cy + 4 * r < 0 or cy - 4 * r > cell:
                    continue
                if s > 0.8:
                    for j in range(2):
                        a = math.radians(30 + j * 180 + seed)
                        out.append(f'<path d="{blob(cx + math.cos(a) * r * 2.1, cy + math.sin(a) * r * 2.1, r * 1.3, r * 0.5, seed + j, 0.1, 8, math.degrees(a))}" fill="{leaf}"/>')
                    for j in range(5):
                        a = math.radians(j * 72 - 90)
                        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85, r * 0.7, r * 0.55, seed + j, 0.1, 8, math.degrees(a))}" fill="{flower}"/>')
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.45:.1f}" fill="{dot}"/>')
                else:
                    for j in range(3):
                        a = math.radians(j * 120 + 20)
                        out.append(f'<circle cx="{cx + math.cos(a) * r:.1f}" cy="{cy + math.sin(a) * r:.1f}" r="{r * 0.55:.1f}" fill="{dot}"/>')
    return "".join(out)


def veg_slice(D, cx, cy, r, kind, ang, seed):
    """One slice standing in the tian, seen from above at an angle: skin rim, flesh, seeds, roasted edge."""
    rnd = random.Random(seed)
    skins = {"courgette": ("#7AAA4A", "#2E6A22", "#F2EEC0"), "aubergine": ("#8A5AA8", "#3E1A4E", "#F4E8C8"),
             "tomate": ("#F26A4A", "#C8281E", "#E8402A"), "jaune": ("#FFE070", "#E8B020", "#FFF0B0")}
    sk, dark, flesh = skins[kind]
    pts = rot(ell_pts(cx, cy, r, r * 0.62, 0, 360, 18)[:-1], cx, cy, ang)
    out = [f'<path d="{smooth_closed(pts)}" fill="{dark}"/>']
    inner = rot(ell_pts(cx - 1, cy - 1.2, r * 0.84, r * 0.5, 0, 360, 18)[:-1], cx, cy, ang)
    out.append(f'<path d="{smooth_closed(inner)}" fill="{flesh}"/>')
    if kind == "tomate":
        for j in range(3):
            a = math.radians(ang + 60 + j * 120)
            out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.35, cy + math.sin(a) * r * 0.22, r * 0.25, r * 0.14, seed + j, 0.2, 8, math.degrees(a))}" fill="#FFB89A" opacity="0.8"/>')
    elif kind in ("courgette", "jaune"):
        out.append(f'<path d="{smooth_closed(rot(ell_pts(cx - 1, cy - 1, r * 0.45, r * 0.25, 0, 360, 12)[:-1], cx, cy, ang))}" fill="{lt(flesh, 0.4)}" opacity="0.8"/>')
        for j in range(5):
            a = rnd.uniform(0, 6.28)
            out.append(f'<circle cx="{cx + math.cos(a) * r * 0.3:.1f}" cy="{cy + math.sin(a) * r * 0.18:.1f}" r="1" fill="#C8B870"/>')
    else:
        for j in range(6):
            a = rnd.uniform(0, 6.28)
            out.append(f'<circle cx="{cx + math.cos(a) * r * 0.4:.1f}" cy="{cy + math.sin(a) * r * 0.25:.1f}" r="1.2" fill="#8A7A5A"/>')
    out.append(f'<path d="{smooth_closed(pts)}" fill="none" stroke="#3A1A0A" stroke-width="1.4" opacity="0.45"/>')
    out.append(taper(rot([(cx - r * 0.6, cy - r * 0.4), (cx, cy - r * 0.58), (cx + r * 0.5, cy - r * 0.42)], cx, cy, ang), 1.2, 2, "#FFFFFF", 0.55))
    return "".join(out)


def tian(D, cx, cy, R, seed):
    """A round terracotta tian of ratatouille: rings of overlapping vegetable slices spiralling inward, thyme, oil."""
    rnd = random.Random(seed)
    k = 0.8
    out = [cast(D, cx + 14, cy + 20, R * 1.08, R * k * 1.02, strength=0.5, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy + 10, R, R * k, 0, 360, 40), ("#F2A27A", "#C8643C", "#7A3218"), seed, sdir=(0.5, 0.8), sk=0.15, angle=0, n=30, inkw=2, hi=0.35))
    out.append(painted(D, ell_pts(cx, cy, R, R * k, 0, 360, 40), ("#F6B48A", "#D8784A", "#8A3A1A"), seed + 1, sdir=(0.5, 0.8), sk=0.1, angle=-30, n=30, inkw=2, hi=0.4))
    inner = ell_pts(cx, cy + 2, R - 14, (R - 14) * k, 0, 360, 40)
    idd = smooth_closed(inner)
    out.append(f'<path d="{idd}" fill="#8A2A14"/>')
    cid = D.clip(f'<path d="{idd}"/>')
    sl = []
    kinds = ["courgette", "tomate", "aubergine", "jaune"]
    rings = [(R - 30, 26), (R - 66, 20), (R - 98, 14), (R - 124, 9)]
    for ri, (rr, n_) in enumerate(rings):
        if rr <= 0:
            continue
        for i in range(n_):
            a = 2 * math.pi * i / n_ + ri * 0.3
            x, y = cx + math.cos(a) * rr, cy + 2 + math.sin(a) * rr * k
            sl.append(veg_slice(D, x, y, 21 - ri * 1.5, kinds[(i + ri) % 4], math.degrees(a) + 90, seed + ri * 50 + i))
    sl.append(veg_slice(D, cx, cy + 2, 18, "tomate", 20, seed + 999))
    for _ in range(40):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * (R - 20)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * k
        sl.append(f'<path d="{blob(x, y, 2.2, 1.2, rnd.randint(1, 999), 0.2, 6, rnd.uniform(0, 180))}" fill="#4A6A2A"/>')
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * (R - 20)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * k
        sl.append(f'<path d="{blob(x, y, 3, 1.4, rnd.randint(1, 999), 0.2, 6, -20)}" fill="#FFFFFF" opacity="0.7"/>')
    sl.append(shade_over(D, idd, "#2A0A00", 0.4, 0, 0, 1, 1, 0.5))
    out.append(f'<g {cid}>{"".join(sl)}</g>')
    out.append(ink(idd, "#5A1A08", 1.6, seed + 3, 1, 0.6))
    out.append(taper(ell_pts(cx, cy, R - 4, (R - 4) * k, 195, 260, 10), 2, 4, "#FFE2C8", 0.7))
    # thyme sprigs laid on top
    for k2, (x, y, a) in enumerate(((cx - 40, cy - 30, -20), (cx + 30, cy + 20, 30))):
        out.append(pline([(x, y), (x + math.cos(math.radians(a)) * 40, y + math.sin(math.radians(a)) * 40)], "#5A4A2A", 1.6, seed + k2, 0.9, 1))
        for j in range(8):
            t = j / 8
            px, py = x + math.cos(math.radians(a)) * 40 * t, y + math.sin(math.radians(a)) * 40 * t
            for sg in (-1, 1):
                out.append(f'<path d="{blob(px + sg * 2.5, py + sg * 1.5, 2.6, 1.3, seed + j * 3 + sg, 0.15, 6, a + sg * 40)}" fill="#6E8A3E"/>')
    return "".join(out)


def wine_glass_top(D, cx, cy, r, seed, wine=("#FFC8C0", "#F2908A", "#B85058")):
    """A stemmed glass of rosé seen from above at an angle: rim ellipse, the wine surface, the foot beneath."""
    out = [cast(D, cx + 10, cy + r * 0.9, r * 0.9, r * 0.35, strength=0.35, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + r * 0.85, r * 0.7, r * 0.25, 0, 360, 20))}" fill="#E8F2F4" opacity="0.6"/>')
    out.append(pline([(cx, cy + r * 0.2), (cx, cy + r * 0.85)], "#C8D8DC", 2.2, seed, 0.8, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r, r * 0.42, 0, 360, 24))}" fill="#F2F8FA" opacity="0.5"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + r * 0.08, r * 0.82, r * 0.3, 0, 360, 24))}" fill="{wine[1]}" opacity="0.9"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy + r * 0.04, r * 0.3, r * 0.08, seed, 0.2, 8)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, r, r * 0.42, 0, 360, 24)), "#7A9AA2", 1.4, seed, 2, 0.7))
    return "".join(out)


@design("bon-appetit")
def bon_appetit():
    D = Doc2("fr-ba")
    # Provençal indienne tablecloth: deep blue ground, yellow flowers
    pat = D.pattern(72, 72, indienne_tile(72, "#22487E", "#E8B830", "#5E8A3E", "#DCD0B0", 7), transform="rotate(-6)")
    out = [f'<rect width="600" height="600" fill="{pat}"/>', f'<rect width="600" height="600" fill="#1A3A6A" opacity="0.38"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#FFFFFF", "#0E2A5A"], 701, n=90, angle=-6, length=(40, 140), width=(2, 6), opacity=(0.04, 0.1)))
    out.append(soft_glow(D, 300, 360, 300, "#FFF0C8", 0.3))
    out.append(f'<ellipse cx="300" cy="150" rx="280" ry="86" fill="{D.rad([(0, "#0A1A3A", 0.75), (0.6, "#0A1A3A", 0.45), (1, "#0A1A3A", 0)])}"/>')
    # two plates waiting, left and right
    for k, (x, y) in enumerate(((60, 506), (544, 470))):
        out.append(cast(D, x + 10, y + 12, 96, 54, strength=0.4, seed=703 + k))
        out.append(painted(D, ell_pts(x, y, 96, 56, 0, 360, 36), WHITE, 704 + k, sdir=(0.5, 0.8), sk=0.1, n=20, inkw=1.8, hi=0.4))
        out.append(ink(smooth_closed(ell_pts(x, y + 2, 66, 38, 0, 360, 30)), "#C8C0B4", 1.4, 705 + k, 1, 0.7))
        out.append(pline(ell_pts(x, y, 88, 51, 0, 360, 36), BLEU[1], 2, 706 + k, 0.7, 1))
    # forks
    for k, (x0, y0, x1, y1) in enumerate(((150, 560, 136, 430), (452, 420, 470, 300))):
        out.append(taper([(x0, y0), (x1, y1)], 6, 5, "#B8BCC4"))
        out.append(taper([(x0 - 1, y0), (x1 - 1, y1)], 1.6, 1.2, "#FFFFFF", 0.8))
    # glass of rosé, bread
    out.append(wine_glass_top(D, 478, 252, 40, 707))
    for k, (x, y, a) in enumerate(((108, 300, -20), (150, 330, 10))):
        pts = rot(blob_pts(x, y, 26, 18, 708 + k, 0.08, 14), x, y, a)
        out.append(painted(D, pts, CRUST, 708 + k, sk=0.2, n=8, inkw=1.6, hi=0.4))
        out.append(f'<path d="{blob(x - 2, y - 2, 18, 11, 709 + k, 0.15, 12, a)}" fill="#FBEFD4"/>' + specks(710 + k, (x - 14, y - 9, x + 12, y + 7), ["#D8BC88"], 10, (0.8, 2), (0.6, 0.9)))
    # the tian, center stage
    out.append(tian(D, 300, 392, 158, 711))
    out.append(steam(300, 300, 60, 712, "#FFFFFF", 3, 40, 7, 0.5))
    # lettering, cream on the blue cloth
    out.append(letters(D, 300, 140, f"Bon appétit{NB}!", SERIF_IT, 106, "#FFF4D6", ["#FFFFFF", "#FFE6A8"], 713, max_w=450,
                       shadow="#0A1A3A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 186, "RATATOUILLE MAISON", "#F4C02C", font=JOS, size=19, ls=6, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 714, "#0A1A3A")


# ================================================================ 8. le marché — the Sunday basket
def tomato_fr(D, cx, cy, r, seed, pal=("#FF9A72", "#E23A26", "#8E140C"), squash=0.86):
    rnd = random.Random(seed)
    pts = []
    for i in range(30):
        a = 2 * math.pi * i / 30
        k = 1 + 0.04 * math.cos(5 * a + seed) + rnd.uniform(-0.01, 0.01)
        pts.append((cx + r * k * math.cos(a), cy + r * squash * k * math.sin(a)))
    out = [painted(D, pts, pal, seed, sdir=(0.6, 0.75), sk=0.2, angle=-40, n=int(r), inkw=max(1.2, r * 0.045), inkop=0.7, hi=0.4, hik=0.08, curve=0.5)]
    out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.32, r * 0.2, r * 0.11, seed + 3, 0.15, 10, -35)}" fill="#FFFFFF" opacity="0.7"/>')
    top = (cx, cy - r * squash * 0.82)
    for k in range(5):
        a = math.radians(-90 + k * 72 + rnd.uniform(-12, 12))
        L = r * rnd.uniform(0.32, 0.46)
        tip = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.55 + L * 0.12)
        out.append(taper([top, tip], max(3, r * 0.13), 0.8, "#3E7A2A"))
    return "".join(out)


def leek(D, x0, y0, x1, y1, W, seed):
    """A leek: white shaft with root tuft at the bottom (x0,y0), fanning blue-green leaves at the top."""
    rnd = random.Random(seed)
    out = []
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    mx, my = x0 + ux * L * 0.5, y0 + uy * L * 0.5
    for j in range(4):
        da = (j - 1.5) * 9
        a = math.radians(ang + da)
        tip = (mx + math.cos(a) * L * 0.62, my + math.sin(a) * L * 0.62)
        pts = along(mx, my, tip[0], tip[1], lambda t: W * 0.75 * (1 - t * 0.55), 14)
        out.append(painted(D, pts, ("#9AC8A0", "#4E8A62", "#1E4A34"), seed + j, sdir=(0, 1), sk=0.25, angle=ang + da, n=10, inkw=1.3, hi=0.4))
        out.append(pline([(mx, my), ((mx + tip[0]) / 2, (my + tip[1]) / 2), tip], "#C8E8C8", 1, seed + j, 0.4, 1))
    shaft = along(x0, y0, mx, my, lambda t: W * (0.92 + 0.08 * t) if t > 0.04 else W * 0.7, 16)
    g = D.lin([(0, "#FFFFF4"), (0.6, "#F2F2DA"), (1, "#B8D8A0")], x0, y0, mx, my, "userSpaceOnUse")
    sd = smooth_closed(shaft)
    out.append(f'<path d="{sd}" fill="{g}"/>')
    out.append(strokes(D.nid(), sd, bbox(shaft), ["#FFFFFF", "#D8D8B8"], seed, n=14, angle=ang, length=(L * 0.08, L * 0.2), width=(0.6, 1.4), opacity=(0.3, 0.6)))
    out.append(ink(sd, "#7A8A5A", 1.4, seed, 1, 0.6))
    for _ in range(9):
        a = math.radians(ang + 180 + rnd.uniform(-50, 50))
        out.append(pline([(x0, y0), (x0 + math.cos(a) * W * 0.9, y0 + math.sin(a) * W * 0.9)], "#E8DCC0", 1.1, rnd.randint(1, 99), 0.9, 1))
    return "".join(out)


def melon(D, cx, cy, r, seed):
    """A Charentais (Cavaillon) melon: pale grey-green skin with dark green sutures, the stalk end."""
    out = [painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.03, 20), ("#E8EEC8", "#B8C890", "#6E7A4A"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=int(r), inkw=1.8, hi=0.4)]
    cid = D.clip(f'<path d="{blob(cx, cy, r, r * 0.92, seed, 0.03, 20)}"/>')
    lines = []
    for k in range(-4, 5):
        x = cx + k * r * 0.24
        lines.append(taper([(x * 0.6 + cx * 0.4, cy - r), (x + k * 3, cy), (x * 0.6 + cx * 0.4, cy + r)], 3, 3, "#4E6A3A", 0.75))
    out.append(f'<g {cid}>{"".join(lines)}</g>')
    out.append(taper([(cx, cy - r * 0.9), (cx + 4, cy - r * 1.08)], 4, 3, "#7A6A3A"))
    return "".join(out)


def radish_bunch(D, x, y, seed):
    rnd = random.Random(seed)
    out = []
    for k in range(5):
        a = math.radians(-120 + k * 14)
        lx, ly = x + math.cos(a) * 56, y + math.sin(a) * 56
        out.append(leaf_simple(D, x, y, 58, 11, math.degrees(a), LEAFG, seed + k, inkw=1))
    for k in range(5):
        rx_, ry_ = x - 16 + k * 8 + rnd.uniform(-3, 3), y + 14 + rnd.uniform(-4, 6)
        pts = [(rx_, ry_ - 9), (rx_ + 8, ry_ - 4), (rx_ + 6, ry_ + 6), (rx_, ry_ + 12), (rx_ - 6, ry_ + 6), (rx_ - 8, ry_ - 4)]
        out.append(painted(D, pts, ("#FF8AA0", "#D8284A", "#7A0A22"), seed + 10 + k, sk=0.25, n=4, inkw=1.2, hi=0.4))
        out.append(f'<path d="{blob(rx_, ry_ + 9, 4, 3, seed + k, 0.1, 6)}" fill="#FFFFFF"/>')
        out.append(pline([(rx_, ry_ + 12), (rx_ + 1, ry_ + 22)], "#E8D8C8", 1, seed + k, 0.9, 1))
    return "".join(out)


@design("le-marche")
def le_marche():
    D = Doc2("fr-mc")
    # the market behind, softly out of focus: striped awnings, crates, morning light
    out = [sky(D, [(0, "#CFE4F0"), (1, "#F6EAD0")], 801, 330, ["#FFFFFF", "#B8D0E0"], 50, angle=-3, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 470, 140, 280, "#FFF4D0", 0.6))
    for k, (x0, x1, top, col) in enumerate(((-20, 230, 230, "#C8382E"), (210, 420, 216, "#2F5AA6"), (400, 640, 236, "#3E8A4E"))):
        aw = [(x0, top), (x1, top), (x1 + 10, top + 46), (x0 - 10, top + 46)]
        ad = smooth_closed(poly_pts(aw, 20, 802 + k, 0.6))
        out.append(f'<path d="{ad}" fill="#FFFDF4"/>')
        out.append(stripes_in(D, ad, bbox(aw), 0, [18, 18], [col, None], 803 + k, 0.85))
        for i in range(int((x1 - x0) / 22) + 1):
            x = x0 - 10 + i * 22
            out.append(f'<path d="M {x} {top + 46} q 11 12 22 0" fill="{col if i % 2 else "#FFFDF4"}" stroke="{dk(col, 0.3)}" stroke-width="1" opacity="0.9"/>')
        out.append(f'<rect x="{x0}" y="{top + 56}" width="{x1 - x0}" height="80" fill="{dk(col, 0.55)}" opacity="0.18"/>')
    rnd = random.Random(804)
    for k in range(18):
        x = rnd.uniform(-10, 590)
        y = rnd.uniform(300, 336)
        out.append(f'<path d="{blob(x, y, rnd.uniform(14, 22), rnd.uniform(8, 12), k, 0.2, 10)}" fill="{rnd.choice(["#E85A3A", "#F2B03A", "#7AAA4A", "#C8382E", "#F6D86A"])}" opacity="0.55"/>')
    for k, x in enumerate((80, 330, 520)):
        out.append(figures.person(x, 350, 74, "walk", 1 if k % 2 else -1, seed=805 + k, tint=("#E8D8C8", 0.45), shadow=0.12))
    out.append(f'<rect x="0" y="200" width="600" height="160" fill="#F6EEDC" opacity="0.32"/>')
    # cobbles
    out.append(f'<rect x="-10" y="350" width="620" height="260" fill="#B8A88E"/>')
    for row in range(14):
        y = 352 + row * (8 + row * 1.6)
        h = 7 + row * 1.6
        x = -rnd.uniform(0, 30)
        while x < 610:
            w = h * rnd.uniform(1.3, 1.8)
            out.append(f'<path d="{blob(x + w / 2, y + h / 2, w / 2 - 1.2, h / 2 - 1.2, rnd.randint(1, 9999), 0.12, 10)}" fill="{rnd.choice(["#C8B898", "#A89878", "#D8C8A8", "#B8A484"])}"/>')
            out.append(f'<path d="{blob(x + w / 2 - w * 0.12, y + h / 2 - h * 0.15, w * 0.25, h * 0.15, rnd.randint(1, 9999), 0.2, 8)}" fill="#FFFFFF" opacity="0.2"/>')
            x += w
    out.append(f'<rect x="-10" y="350" width="620" height="40" fill="{D.lin([(0, "#F6EEDC", 0.6), (1, "#F6EEDC", 0)])}"/>')
    # the wicker basket with leather handles
    cx, rim_y, rx, ry, bottom = 300, 404, 172, 40, 548
    out.append(cast(D, cx + 20, bottom + 8, 210, 22, strength=0.5, seed=806))
    for sg in (-1, 1):
        hp = [(cx + sg * 120, rim_y - 6), (cx + sg * 110, rim_y - 130), (cx + sg * 40, rim_y - 170)]
        out.append(taper(catmull(hp, 6), 12, 12, "#7A4A28"))
        out.append(taper(catmull([(x - 2, y) for x, y in hp], 6), 3, 3, "#C8925A", 0.7))
    out.append(taper(catmull([(cx - 40, rim_y - 170), (cx, rim_y - 178), (cx + 40, rim_y - 170)], 6), 12, 12, "#7A4A28"))
    out.append(f'<path d="{blob(cx, rim_y, rx - 4, ry - 4, 807, 0.01, 24)}" fill="#5E3A16"/>')
    # produce, back to front
    out.append(leek(D, 216, 410, 96, 236, 15, 808))
    out.append(leek(D, 236, 414, 140, 226, 14, 809))
    out.append(radish_bunch(D, 432, 372, 810))
    # a round lettuce
    rnd2 = random.Random(830)
    for k in range(14):
        a = rnd2.uniform(0, 6.28)
        out.append(painted(D, rot(blob_pts(170 + math.cos(a) * 18, 372 + math.sin(a) * 12, 26, 18, 831 + k, 0.2, 12), 170, 372, math.degrees(a)),
                           ("#D8F0A0", "#8AC04E", "#3E7A2A"), 831 + k, sk=0.2, n=4, inkw=1, inkop=0.5, hi=0.45))
    out.append(painted(D, blob_pts(172, 368, 20, 14, 850, 0.15, 12), ("#F0FAC8", "#C8E07A", "#7AA03E"), 850, sk=0.15, n=4, inkw=1, hi=0.5))
    for k, (x, y) in enumerate(((330, 388), (390, 386), (196, 392))):
        out.append(painted(D, blob_pts(x, y, 26, 18, 860 + k, 0.08, 12), ("#C8E8A0", "#7AB04E", "#3E6A2A"), 860 + k, sk=0.2, n=4, inkw=1, hi=0.4))
    out.append(melon(D, 352, 362, 54, 811))
    for k, (x, y, r) in enumerate(((236, 370, 30), (300, 384, 26))):
        out.append(painted(D, blob_pts(x, y, r, r * 0.9, 812 + k * 3, 0.05, 16), ("#FFD88A", "#F2A23A", "#B8601A"), 812 + k * 3, sk=0.2, n=8, inkw=1.4, hi=0.4))
        out.append(f'<path d="{blob(x + 8, y - 8, r * 0.4, r * 0.55, 813 + k, 0.1, 10, 20)}" fill="#E8602A" opacity="0.4"/>')
        out.append(pline([(x, y - r * 0.85), (x + 3, y + r * 0.3)], "#C8702A", 1.4, 814 + k, 0.5, 1))
    for k, (x, y, r) in enumerate(((158, 398, 30), (262, 402, 32), (414, 404, 31), (470, 396, 24))):
        out.append(tomato_fr(D, x, y, r, 816 + k))
    out.append(wicker_basket(D, cx, rim_y, rx, ry, bottom, 132, 815))
    # a little slate price tag stuck in the tomatoes
    tx, ty = 486, 310
    out.append(pline([(tx, ty + 34), (tx - 4, ty + 70)], "#7A5A3A", 2.4, 816, 1, 1))
    out.append(painted(D, rect_pts(tx - 40, ty - 4, tx + 40, ty + 36, 10, 817, 0.4), WOOD, 817, sk=0.1, n=6, inkw=1.4, hi=0.4))
    out.append(f'<path d="{hg.org_rect(tx - 35, ty + 1, 70, 30, 818, 0.4, 10, 2)}" fill="#2A302E"/>')
    out.append(chalk_text(tx, ty + 23, "3 €/kg", JOST, 18, max_w=64))
    # a fallen apricot on the cobbles
    out.append(painted(D, blob_pts(118, 560, 18, 16, 819, 0.05, 14), ("#FFD88A", "#F2A23A", "#B8601A"), 819, sk=0.2, n=6, inkw=1.4, hi=0.4))
    out.append(f'<path d="{blob(124, 556, 8, 10, 820, 0.1, 10, 20)}" fill="#E8602A" opacity="0.4"/>')
    # lettering
    out.append(letters(D, 300, 132, "le marché", SERIF_IT, 120, "#2E5A2E", ["#3E7A3E", "#1A3E1A", "#5A9A4A"], 821, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8D890"))
    out.append(ruled(300, 176, "LE DIMANCHE MATIN", ROUGE[2], font=JOS, size=19, ls=6, line_w=32, gap=12, max_w=380))
    return finish_f(D, out, 822)


# ================================================================ 9. crêpes — la Chandeleur, one flipped mid-air
def crepe_disc(D, cx, cy, rx, ry, seed, tilt=0, curl=0.12):
    """A thin golden crêpe tossed in the air: a wavy, floppy disc in perspective with lacy brown 'dentelle' freckles,
    a paler rim, the thin underside showing along the lower edge and one side curling over."""
    rnd = random.Random(seed)
    pts = rot([(cx + rx * math.cos(a) * (1 + 0.04 * math.sin(5 * a + seed)), cy + ry * math.sin(a) - curl * ry * math.cos(a) ** 2 + ry * 0.12 * math.sin(3 * a))
               for a in [i * 2 * math.pi / 48 for i in range(48)]], cx, cy, tilt)
    d = smooth_closed(pts)
    # underside band (the crêpe's thickness, paler, visible below)
    out = [f'<path d="{d}" fill="#E8B866" transform="translate(0 5)"/>']
    out.append(f'<path d="{d}" fill="#F6CE80"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{d}" fill="{D.rad([(0, "#E09A40"), (0.65, "#F2C070"), (1, "#FFE6B0")])}"/>']
    for _ in range(int(rx * 3.2)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.92
        x, y = rot([(cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr)], cx, cy, tilt)[0]
        s_ = rnd.uniform(1.6, 4.5)
        col = rnd.choice(["#A8561A", "#B8662A", "#8A4410", "#C8782E"])
        if rnd.random() < 0.6:
            inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{s_:.1f}" ry="{s_ * ry / rx + 0.8:.1f}" fill="none" stroke="{col}" stroke-width="1.3" opacity="{rnd.uniform(0.35, 0.75):.2f}"/>')
        else:
            inner.append(f'<path d="{blob(x, y, s_ * 0.8, s_ * 0.5 + 0.5, rnd.randint(1, 9999), 0.3, 8)}" fill="{col}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    inner.append(taper(rot([(cx - rx * 0.6, cy - ry * 0.5), (cx - rx * 0.1, cy - ry * 0.75), (cx + rx * 0.4, cy - ry * 0.6)], cx, cy, tilt), 2, 4, "#FFF0C8", 0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#9A5A1A", 1.5, seed, 2, 0.6))
    # the right edge curling over: pale underside flap
    fx, fy = rot([(cx + rx * 0.78, cy - ry * 0.05)], cx, cy, tilt)[0]
    flap = rot([(cx + rx * 0.62, cy - ry * 0.75), (cx + rx * 0.98, cy - ry * 0.55), (cx + rx * 1.08, cy - ry * 0.05), (cx + rx * 0.96, cy + ry * 0.55), (cx + rx * 0.66, cy + ry * 0.62), (cx + rx * 0.8, cy)], cx, cy, tilt)
    out.append(painted(D, flap, ("#FFEAB8", "#F2CC84", "#B8803A"), seed + 5, sdir=(-1, 0.3), sk=0.2, angle=-80, n=6, inkw=1.4, inkop=0.6, hi=0.5))
    out.append(specks(seed + 6, bbox(flap), ["#C8823A"], 10, (0.8, 1.8), (0.3, 0.6)))
    return "".join(out)


def folded_crepe(D, cx, cy, s, seed, rot_=0):
    """A crêpe folded in four (a fan-shaped quarter), sugar sparkling on top."""
    rnd = random.Random(seed)
    pts = [(cx - s, cy + s * 0.25)] + [(cx - s + 2 * s * (i / 12), cy + s * 0.25 - s * 0.62 * math.sin(math.pi * i / 12) ** 0.7) for i in range(1, 12)] + [(cx + s, cy + s * 0.25), (cx, cy + s * 0.42)]
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, ("#FFE2A0", "#EEB45A", "#A8641E"), seed, sdir=(0.3, 1), sk=0.2, angle=-20 + rot_, n=12, inkw=1.6, hi=0.45)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    sp = []
    for _ in range(int(s * 1.2)):
        x, y = rnd.uniform(cx - s, cx + s), rnd.uniform(cy - s * 0.4, cy + s * 0.4)
        sp.append(f'<path d="{blob(x, y, rnd.uniform(1.4, 3.6), rnd.uniform(1, 2.6), rnd.randint(1, 999), 0.3, 6)}" fill="#B8641E" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    for _ in range(int(s * 1.5)):
        x, y = rnd.uniform(cx - s, cx + s), rnd.uniform(cy - s * 0.5, cy + s * 0.3)
        sp.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="1.8" height="1.8" fill="#FFFFFF" opacity="0.9" transform="rotate({rnd.uniform(0, 90):.0f} {x:.1f} {y:.1f})"/>')
    out.append(f'<g {cid}>{"".join(sp)}</g>')
    edge = rot([(cx - s * 0.9, cy + s * 0.27), (cx, cy + s * 0.4), (cx + s * 0.9, cy + s * 0.27)], cx, cy, rot_)
    out.append(taper(edge, 3, 3, "#FFF0C8", 0.8))
    return "".join(out)


@design("crepes")
def crepes():
    D = Doc2("fr-cr")
    # warm buttery kitchen wall with a shelf of Breton bowls
    out = [sky(D, [(0, "#FBEFD2"), (1, "#F2DCB0")], 901, 600, ["#FFFFFF", "#E8C890"], 80, angle=-80, sop=(0.04, 0.12))]
    out.append(blooms(902, ["#E8C890", "#F6E2B8"], 6, (0, 0, 600, 600), (100, 180), (0.06, 0.12)))
    out.append(soft_glow(D, 300, 300, 280, "#FFFFFF", 0.5))
    # worktop: blue-and-white Breton striped oilcloth
    top = "M -10 452 L 610 452 L 610 610 L -10 610 Z"
    out.append(f'<path d="{top}" fill="#FFFDF4"/>')
    out.append(stripes_in(D, top, (-10, 452, 610, 610), 0, [22, 22], [BLEU[1], None], 903, 0.9))
    out.append(shade_over(D, top, "#1A2A4A", 0.35, 0, 0, 0, 1, 0.3))
    out.append(f'<rect x="-10" y="444" width="620" height="10" fill="#8A6A3A" opacity="0.5"/>')
    # bowl of batter with a whisk, left
    bx, bb = 92, 476
    out.append(cast(D, bx + 8, bb + 4, 66, 9, strength=0.4, seed=960))
    out.append(painted(D, [(bx - 62, bb - 54), (bx + 62, bb - 54), (bx + 50, bb - 14), (bx + 24, bb), (bx - 24, bb), (bx - 50, bb - 14)], ("#FFFFFF", "#F2EDE4", "#B0A898"), 961, sdir=(1, 0.3), sk=0.2, n=10, inkw=1.8, hi=0.4))
    out.append(pline([(bx - 58, bb - 42), (bx, bb - 36), (bx + 58, bb - 42)], ROUGE[1], 2.6, 962, 0.9, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(bx, bb - 54, 62, 11, 0, 360, 24))}" fill="#E8DFD0"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(bx, bb - 53, 55, 8, 0, 360, 24))}" fill="#F6DC94"/>')
    out.append(f'<path d="{blob(bx - 12, bb - 54, 18, 3, 963, 0.2, 10)}" fill="#FFF2C0"/>')
    out.append(taper([(bx + 10, bb - 56), (bx + 46, bb - 110), (bx + 60, bb - 136)], 5, 5, "#B8BCC4"))
    for k in range(5):
        a = (k - 2) * 7
        out.append(ink(smooth_open(rot([(bx + 12, bb - 56), (bx + 2, bb - 76), (bx + 12, bb - 96), (bx + 30, bb - 86), (bx + 12, bb - 56)], bx + 12, bb - 56, a + 30)), "#9AA0A8", 1.4, 964 + k, 1, 0.9))
    # the crêpe pan on the counter, long handle, a knob of butter sizzling
    px, py = 268, 488
    out.append(cast(D, px + 16, py + 22, 150, 28, strength=0.5, seed=904))
    out.append(taper([(px + 120, py + 14), (px + 220, py + 46), (px + 300, py + 70)], 15, 12, "#2A2A2E"))
    out.append(taper([(px + 122, py + 10), (px + 300, py + 66)], 3, 2, "#6A6A72", 0.8))
    out.append(painted(D, ell_pts(px, py + 12, 146, 46, 0, 360, 36), ("#4A4A50", "#1E1E22", "#08080A"), 905, sdir=(0, 1), sk=0.15, n=20, inkw=2, hi=0.3))
    out.append(f'<path d="{smooth_closed(ell_pts(px, py, 134, 38, 0, 360, 36))}" fill="#34343A"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(px, py + 2, 120, 32, 0, 360, 36))}" fill="#26262C"/>')
    out.append(taper(ell_pts(px, py, 132, 36, 195, 300, 12), 2, 4, "#8A8A92", 0.7))
    out.append(f'<path d="{blob(px - 10, py + 4, 22, 7, 906, 0.2, 12)}" fill="#F6DC84" opacity="0.8"/>')
    for k in range(6):
        out.append(f'<circle cx="{px - 30 + k * 12:.1f}" cy="{py + 4 + (k % 2) * 3:.1f}" r="1.6" fill="#FFF4C0" opacity="0.8"/>')
    # the flipped crêpe high in the air: thin, floppy, lacy; motion arcs and a few drops of butter
    for k, (r0, op) in enumerate(((150, 0.6), (172, 0.4))):
        arc = [(px - 40 + r0 * math.cos(math.radians(a)), 420 + r0 * 0.75 * math.sin(math.radians(a))) for a in range(196, 250, 6)]
        out.append(taper(arc, 2, 6, "#FFFFFF", op))
        out.append(taper([(x + 2, y + 2) for x, y in arc], 1, 3, "#C8A070", op * 0.6))
    out.append(crepe_disc(D, 296, 300, 138, 50, 907, tilt=-12, curl=0.3))
    for (x, y) in ((420, 360), (440, 336), (190, 368)):
        out.append(f'<path d="{blob(x, y, 3, 4, int(x), 0.2, 8)}" fill="#F6DC84"/>')
    # stack of crêpes on a plate, a folded sugar one on top, a lemon half
    sx, sy = 484, 486
    out.append(cast(D, sx + 10, sy + 18, 86, 14, strength=0.4, seed=908))
    out.append(painted(D, ell_pts(sx, sy + 8, 80, 20, 0, 360, 30), WHITE, 909, sk=0.12, n=10, inkw=1.6, hi=0.4))
    for k in range(6):
        out.append(painted(D, ell_pts(sx, sy - k * 5, 66 - k, 15, 0, 360, 30), ("#FFE6A8", "#EEB45A", "#A8641E"), 910 + k, sk=0.2, n=5, inkw=1.1, hi=0.3))
    out.append(folded_crepe(D, sx - 4, sy - 42, 48, 916, rot_=-4))
    # a gold coin, for luck (you flip with a coin in your other hand)
    out.append(cast(D, 214, 566, 22, 5, strength=0.35, seed=970))
    out.append(painted(D, ell_pts(210, 562, 18, 7, 0, 360, 18), ("#FFF0A0", "#E8B830", "#8A6A10"), 971, sk=0.2, n=4, inkw=1.2, hi=0.6))
    out.append(f'<path d="{smooth_closed(ell_pts(210, 561, 12, 4.4, 0, 360, 14))}" fill="none" stroke="#B8901E" stroke-width="1.2"/>')
    out.append(sparkle(228, 552, 7, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 134, "crêpes", SERIF_IT, 128, BLEU[2], [BLEU[1], "#0A1A4A", "#4A70C0"], 932, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 182, "C’EST LA CHANDELEUR", "#B8601A", font=JOS, size=19, ls=5, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 933)


# ================================================================ 10. la marinière — on the blue door, hortensias below
def mariniere(D, cx, top, w, h, seed):
    """A Breton striped top on a wooden hanger: wide boat neck, long sleeves hanging down along the body,
    navy stripes on white (the sleeves striped too), soft folds."""
    sh = w * 0.5                                       # half shoulder width
    body = [(cx - w * 0.22, top + 6), (cx, top + 12), (cx + w * 0.22, top + 6), (cx + sh, top + 16), (cx + sh - 12, top + h * 0.34),
            (cx + sh - 14, top + h * 0.98), (cx + sh * 0.2, top + h + 5), (cx - sh * 0.2, top + h + 5), (cx - sh + 14, top + h * 0.98),
            (cx - sh + 12, top + h * 0.34), (cx - sh, top + 16)]
    d = smooth_closed(jitter(body, seed, 0.6))
    out = [f'<path d="{d}" fill="#000000" opacity="0.18" transform="translate(9 9)"/>']
    out.append(f'<path d="{d}" fill="#FFFDF6"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    y = top + 34
    k = 0
    while y < top + h + 10:
        inner.append(taper([(cx - w, y + 2), (cx - w * 0.2, y + 4 + (k % 2)), (cx + w * 0.3, y + 3), (cx + w, y + 1)], 9, 9, "#1E2E5A", 0.95))
        y += 21
        k += 1
    inner.append(strokes(D.nid(), d, (cx - w, top, cx + w, top + h), ["#FFFFFF", "#D8D0C4"], seed, n=60, angle=-90, length=(20, 60), width=(1, 3), opacity=(0.1, 0.3)))
    inner.append(shade_over(D, d, "#1A1A3A", 0.3, 0, 0, 1, 0.3, 0.45))
    for (a_, b_) in (((cx - w * 0.1, top + 40), (cx - w * 0.16, top + h)), ((cx + w * 0.18, top + 50), (cx + w * 0.12, top + h))):
        inner.append(taper([a_, b_], 10, 3, "#1A1A3A", 0.16))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # sleeves hanging straight down in front of the body's sides
    for sg in (-1, 1):
        sl = [(cx + sg * (sh - 6), top + 14), (cx + sg * (sh + 12), top + 26), (cx + sg * (sh + 44), top + h * 0.84), (cx + sg * (sh + 30), top + h * 0.9),
              (cx + sg * (sh + 4), top + h * 0.88), (cx + sg * (sh - 26), top + 50)]
        sd = smooth_closed(jitter(sl, seed + sg, 0.6))
        out.append(f'<path d="{sd}" fill="#FFFDF6"/>')
        scid = D.clip(f'<path d="{sd}"/>')
        st = []
        yy = top + 36
        while yy < top + h:
            st.append(taper([(cx + sg * (sh - 40), yy - 4), (cx + sg * (sh + 60), yy + 8)], 9, 9, "#1E2E5A", 0.95))
            yy += 21
        st.append(shade_over(D, sd, "#1A1A3A", 0.35, 0.5 - sg * 0.5, 0, 0.5 + sg * 0.5, 0, 0.3))
        out.append(f'<g {scid}>{"".join(st)}</g>')
        out.append(ink(sd, INK, 1.8, seed + 5 + sg, 2, 0.65))
        out.append(ink(smooth_open([(cx + sg * (sh + 4), top + h * 0.86), (cx + sg * (sh + 42), top + h * 0.82)]), "#1E2E5A", 2.2, seed + 7, 1, 0.6))
    out.append(ink(d, INK, 2, seed, 2, 0.7))
    out.append(ink(smooth_open([(cx - w * 0.22, top + 6), (cx, top + 14), (cx + w * 0.22, top + 6)]), "#1E2E5A", 2.4, seed + 1, 1, 0.8))
    # hanger
    out.append(taper([(cx - sh + 4, top + 18), (cx - w * 0.22, top + 4), (cx, top - 2), (cx + w * 0.22, top + 4), (cx + sh - 4, top + 18)], 8, 8, "#C8925A"))
    out.append(taper([(cx - sh + 4, top + 15), (cx, top - 5), (cx + sh - 4, top + 15)], 2, 2, "#F2D0A0", 0.7))
    out.append(ink(smooth_open([(cx, top - 4), (cx, top - 18), (cx + 8, top - 28), (cx + 1, top - 36), (cx - 5, top - 30)]), "#7A7A82", 2.6, seed + 2, 1, 0.9))
    return "".join(out)


def cire(D, cx, top, seed):
    """A yellow fisherman's oilskin (ciré) hanging from a hook by its collar loop: hood behind, raglan shoulders,
    sleeves, toggle buttons, two pocket flaps."""
    Y = ("#FFE66A", "#F6C21C", "#B8820C")
    out = [ink(f"M {cx} {top - 6} l 0 -14 q 0 -6 6 -6", "#4A4A50", 3, seed, 1, 0.9)]
    hood = [(cx - 26, top + 6), (cx - 30, top - 12), (cx, top - 22), (cx + 30, top - 12), (cx + 26, top + 6)]
    out.append(painted(D, hood, (dk(Y[0], 0.05), dk(Y[1], 0.12), dk(Y[2], 0.1)), seed, sk=0.25, n=6, inkw=1.6, hi=0.3))
    body = [(cx - 24, top + 2), (cx + 24, top + 2), (cx + 52, top + 30), (cx + 58, top + 196), (cx - 58, top + 196), (cx - 52, top + 30)]
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="#000000" opacity="0.18" transform="translate(7 7)"/>')
    out.append(painted(D, body, Y, seed + 1, sdir=(1, 0.2), sk=0.18, angle=-90, n=30, inkw=2, hi=0.5, hik=0.06))
    for sg in (-1, 1):
        sl = [(cx + sg * 50, top + 30), (cx + sg * 64, top + 60), (cx + sg * 66, top + 170), (cx + sg * 44, top + 172), (cx + sg * 40, top + 60)]
        out.append(painted(D, sl, Y, seed + 2 + sg, sdir=(sg, 0.2), sk=0.25, angle=-90, n=10, inkw=1.6, hi=0.4))
        out.append(pline([(cx + sg * 44, top + 160), (cx + sg * 66, top + 158)], Y[2], 2, seed + sg, 0.7, 1))
        out.append(painted(D, rect_pts(cx + sg * 36 - 16, top + 118, cx + sg * 36 + 16, top + 128, 6, seed + 5 + sg, 0.3), Y, seed + 5 + sg, sk=0.3, n=3, inkw=1.2, hi=0.4))
    collar = [(cx - 26, top + 2), (cx, top + 18), (cx + 26, top + 2), (cx + 18, top - 4), (cx, top + 6), (cx - 18, top - 4)]
    out.append(painted(D, collar, Y, seed + 8, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(pline([(cx, top + 18), (cx + 2, top + 196)], Y[2], 1.8, seed + 9, 0.8, 1))
    for k in range(4):
        out.append(painted(D, rect_pts(cx - 5, top + 40 + k * 34, cx + 9, top + 44 + k * 34, 4, seed + 10 + k, 0.2), ("#FFFDF4", "#E8DCC0", "#8A7A5A"), seed + 10 + k, sk=0.2, n=2, inkw=1, hi=0.5))
    return "".join(out)


def hydrangea(D, cx, cy, r, seed, pal=(("#C8D8FF", "#7A9AE8", "#3A5AB0"), ("#D8C8F8", "#9A86E0", "#5A46A0"))):
    """A mophead hortensia: a dome of tiny four-petal florets in Breton blue and mauve."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy, r, r * 0.86, seed, 0.1, 16)}" fill="{pal[0][2]}"/>']
    items = []
    for _ in range(int(r * 1.6)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.95
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.86
        lit = -(math.cos(a) * -0.6 + math.sin(a) * -0.8) * rr / r
        items.append((lit, x, y))
    for lit, x, y in sorted(items):
        p = rnd.choice(pal)
        c = p[0] if lit > 0.3 else (p[2] if lit < -0.4 else p[1])
        s = rnd.uniform(3.5, 5.5)
        for j in range(4):
            a = math.radians(j * 90 + rnd.uniform(0, 90))
            out.append(f'<path d="{blob(x + math.cos(a) * s * 0.6, y + math.sin(a) * s * 0.6, s * 0.6, s * 0.45, rnd.randint(1, 9999), 0.15, 6, math.degrees(a))}" fill="{c}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("la-mariniere")
def la_mariniere():
    D = Doc2("fr-mr")
    # Breton granite cottage wall
    out = [f'<rect width="600" height="600" fill="#BDB4A6"/>']
    rnd = random.Random(1001)
    for _ in range(80):
        x, y = rnd.uniform(-20, 620), rnd.uniform(-20, 620)
        w, h = rnd.uniform(30, 70), rnd.uniform(18, 34)
        out.append(painted(D, blob_pts(x, y, w / 2, h / 2, rnd.randint(1, 9999), 0.12, 12), rnd.choice([("#E2DACE", "#C8BEB0", "#8A8070"), ("#D8CCC0", "#B8AC9C", "#7A6E60"), ("#E8DAD0", "#CAB8AA", "#8A7468")]),
                           rnd.randint(1, 9999), sk=0.25, n=4, inkw=1, inkop=0.35, hi=0.3))
    out.append(specks(1002, (0, 0, 600, 600), ["#FFFFFF", "#5A5048", "#E8C8B8"], 300, (0.6, 1.4), (0.3, 0.7)))
    # the blue door in a granite frame
    dx0, dx1, dy0 = 130, 470, 236
    out.append(painted(D, rect_pts(dx0 - 26, dy0 - 26, dx1 + 26, 620, 30, 1003, 0.8), ("#EEE6DA", "#D0C4B4", "#8A7E70"), 1003, sdir=(1, 0.3), sk=0.12, n=40, inkw=1.6, hi=0.4))
    door = rect_pts(dx0, dy0, dx1, 620, 30, 1004, 0.5)
    dd = smooth_closed(door)
    out.append(f'<path d="{dd}" fill="{PROV[1]}"/>')
    out.append(wood_planks(D, dy0, 620, 1005, PROV, 6, vertical=True, x0=dx0, x1=dx1))
    out.append(shade_over(D, dd, "#0A2440", 0.45, 0, 0, 1, 0.2, 0.3))
    out.append(f'<path d="{pd([(dx0, dy0), (dx1, dy0), (dx1, dy0 + 14), (dx0, dy0 + 14)])}" fill="#0A2440" opacity="0.35"/>')
    for y in (300, 560):
        out.append(painted(D, rect_pts(dx0 + 10, y, dx1 - 10, y + 16, 20, 1006 + y, 0.4), PROV, 1006 + y, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(ink(dd, INK, 2, 1008, 2, 0.6))
    # wrought-iron latch and a nail with the hanger
    out.append(painted(D, rect_pts(dx1 - 40, 420, dx1 - 26, 470, 8, 1009, 0.3), ("#5A5A62", "#2A2A30", "#0A0A0E"), 1009, sk=0.2, n=3, inkw=1.2, hi=0.3))
    out.append(taper([(dx1 - 60, 446), (dx1 - 30, 446)], 5, 5, "#2A2A30"))
    out.append(f'<circle cx="300" cy="258" r="4" fill="#3A3A40"/>')
    # the marinière
    out.append(mariniere(D, 296, 286, 176, 214, 1010))
    # a yellow oilskin ciré on a hook to the right of the door
    out.append('<g transform="translate(512 300) scale(0.82) translate(-512 -300)">' + cire(D, 512, 300, 1011) + '</g>')
    # hortensias spilling in front of the door
    for k, (x, y, r) in enumerate(((66, 530, 74), (170, 572, 64), (440, 574, 64), (546, 532, 74))):
        for j in range(3):
            a = math.radians(-160 + j * 70 + k * 10)
            out.append(leaf_simple(D, x, y + 10, r * 0.9, r * 0.3, math.degrees(a), ("#8ABA6A", "#3E7A3A", "#1A4A1E"), 1014 + k * 5 + j, inkw=1))
        pal = ((("#C8D8FF", "#7A9AE8", "#3A5AB0"), ("#D8C8F8", "#9A86E0", "#5A46A0")) if k % 2 == 0 else
               (("#F8C8E0", "#E088B8", "#A04878"), ("#D8C8F8", "#9A86E0", "#5A46A0")))
        out.append(hydrangea(D, x, y - 6, r * 0.62, 1030 + k, pal))
    # lettering on a sunny granite lintel band
    band = rect_pts(40, 64, 560, 210, 30, 1031, 0.6)
    out.append(f'<path d="{smooth_closed(band)}" fill="#F6F0E6" opacity="0.88"/>')
    out.append(ink(smooth_closed(band), "#8A7E70", 1.6, 1032, 1, 0.5))
    out.append(letters(D, 300, 154, "la marinière", SERIF_IT, 100, "#1E2E5A", ["#2E4A8A", "#0A1A3A", "#4A6AB0"], 1033, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 192, "BRETAGNE · TOUJOURS DANS LE VENT", "#C8382E", font=JOS, size=17, ls=3, line_w=18, gap=10, max_w=420))
    return finish_f(D, out, 1034)


# ================================================================ 11. les bouquinistes — a green box open on the parapet
def book_spine(D, x, base, w, h, col, seed, lean=0):
    rnd = random.Random(seed)
    pts = rot(rect_pts(x, base - h, x + w, base, 8, seed, 0.3), x + w / 2, base, lean)
    out = [painted(D, pts, pal3(col, 0.3, 0.35), seed, sdir=(1, 0.1), sk=0.25, angle=-90, n=4, inkw=1.1, hi=0.35)]
    for t in (0.14, 0.86):
        a, b = rot([(x + 2, base - h * t), (x + w - 2, base - h * t)], x + w / 2, base, lean)
        out.append(pline([a, b], "#F2D488", 1.6, seed, 0.8, 1))
    if rnd.random() < 0.6:
        a, b = rot([(x + w / 2, base - h * 0.3), (x + w / 2, base - h * 0.7)], x + w / 2, base, lean)
        out.append(pline([a, b], "#F6E6C0", 1.4, seed + 1, 0.6, 1))
    return "".join(out)


@design("les-bouquinistes")
def les_bouquinistes():
    D = Doc2("fr-bk")
    # soft grey-blue Paris morning, the far quay in haze, the river
    out = [sky(D, [(0, "#B8C8D8"), (1, "#E8E2D4")], 1101, 380, ["#FFFFFF", "#A8B8C8"], 50, angle=-3, sop=(0.05, 0.12))]
    rnd = random.Random(1102)
    x = -10
    while x < 610:
        w = rnd.uniform(60, 110)
        h = rnd.uniform(70, 100)
        out.append(f'<path d="{pd([(x, 330), (x, 330 - h), (x + 6, 330 - h - 16), (x + w - 6, 330 - h - 16), (x + w, 330 - h), (x + w, 330)])}" fill="#C8C4BC" opacity="0.8"/>')
        for i in range(int(w / 16)):
            for j in range(4):
                out.append(f'<rect x="{x + 6 + i * 16:.1f}" y="{330 - h + 8 + j * 18:.1f}" width="7" height="10" fill="#9AA0A8" opacity="0.6"/>')
        x += w + 2
    out.append(f'<rect x="0" y="230" width="600" height="110" fill="#E8E2D4" opacity="0.45"/>')
    out.append(sea(D, 330, 400, [(0, "#9AAAB0"), (1, "#6E8088")], 1103, ["#C8D4D8", "#5A6A70"], 40))
    # plane-tree branch and leaves overhead
    out.append(taper(catmull([(620, 40), (540, 62), (470, 60), (430, 74)], 6), 14, 4, "#8A7A5E"))
    for k, (lx, ly, ls_, r_) in enumerate(((588, 74, 32, 200), (556, 92, 28, 160), (520, 70, 30, 215), (486, 96, 24, 175), (448, 82, 22, 195))):
        out.append(maple_leaf(lx, ly, ls_, ["#8AB05A", "#7AA04E", "#9AC06A"][k % 3], "#3E6A2A", r_, 1104 + k, "#E8F4C8"))
    # stone parapet
    out.append(painted(D, rect_pts(-10, 396, 610, 420, 30, 1105, 0.5), STONE, 1105, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.5))
    out.append(f'<rect x="-10" y="420" width="620" height="200" fill="#CDBB98"/>')
    for row in range(5):
        y = 420 + row * 38
        off = (row % 2) * 60
        for i in range(-1, 6):
            x0 = i * 120 + off
            sc = rnd.choice([STONE, ("#F0E2C8", "#D2BE98", "#9A8460"), ("#EADCC6", "#CCB898", "#8E7A5A"), ("#F4E8D4", "#DCCCAE", "#A08C6C")])
            out.append(painted(D, rect_pts(x0 + 2, y + 2, x0 + 118, y + 36, 20, 1106 + row * 10 + i, 0.6), sc, 1106 + row * 10 + i, sdir=(0.5, 1), sk=0.15, n=8, inkw=1.2, inkop=0.45, hi=0.35))
            if rnd.random() < 0.3:
                out.append(f'<path d="{blob(x0 + rnd.uniform(20, 100), y + 30, rnd.uniform(10, 20), 4, rnd.randint(1, 999), 0.3, 8)}" fill="#8A9A5A" opacity="0.45"/>')
    # the bouquiniste's box: green front, lid propped open with prints pinned inside
    bx0, bx1, by = 92, 508, 404
    green = ("#4E8A62", "#1E5A3A", "#0A2E1A")
    lid = [(bx0 - 6, by - 66), (bx1 + 6, by - 66), (bx1 - 6, by - 212), (bx0 + 6, by - 212)]
    out.append(painted(D, poly_pts(lid, 20, 1107, 0.4), green, 1107, sdir=(1, 0.2), sk=0.1, angle=-90, n=30, inkw=2, hi=0.3))
    inside = poly_pts([(bx0 + 10, by - 76), (bx1 - 10, by - 76), (bx1 - 18, by - 202), (bx0 + 18, by - 202)], 20, 1108, 0.4)
    out.append(f'<path d="{smooth_closed(inside)}" fill="#163E28"/>')
    # pinned prints: a botanical plate, an old map of the river, a postcard with a boat
    def print_card(x, y, w, h, seed, art):
        o = [f'<path d="{hg.org_rect(x + 4, y + 5, w, h, seed, 0.4, 10, 1)}" fill="#000000" opacity="0.25"/>',
             painted(D, rect_pts(x, y, x + w, y + h, 10, seed, 0.4), ("#FFFAEE", "#F2E6CC", "#C0AA88"), seed, sk=0.1, n=6, inkw=1.2, hi=0.3), art]
        o.append(f'<circle cx="{x + w / 2:.1f}" cy="{y + 5:.1f}" r="2.6" fill="#C8382E"/>')
        return "".join(o)
    a1 = "".join(leaf_simple(D, 152, 314 - k * 22, 30, 7, -60 - k * 30, ("#9AC07A", "#5A8A4A", "#2E5A2A"), 1110 + k, inkw=0.9) for k in range(3))
    a1 += pline([(152, 322), (152, 262)], "#5A6A3A", 1.6, 1113, 0.9, 1) + p_heart(D, 152, 258, 8, ROUGE, 1114, inkw=0.8)
    out.append(print_card(120, 232, 66, 100, 1115, a1))
    a2 = (f'<rect x="222" y="232" width="150" height="74" fill="#EFE2C2"/>' + pline([(226, 284), (270, 266), (320, 278), (368, 256)], "#4A7AB0", 5, 1116, 0.8, 1) +
          "".join(f'<rect x="{230 + k * 14}" y="{242 + (k % 3) * 10}" width="8" height="6" fill="#B8A07A"/>' for k in range(10)))
    out.append(print_card(214, 226, 166, 86, 1117, a2))
    a3 = (f'<rect x="410" y="236" width="70" height="52" fill="#A8C8E0"/>' + f'<path d="M 410 272 L 480 272 L 480 288 L 410 288 Z" fill="#4A7AA0"/>' +
          f'<path d="M 436 270 L 446 244 L 446 270 Z" fill="#FFFFFF"/>' + taper([(426, 272), (458, 272)], 5, 5, "#8A3A1A"))
    out.append(print_card(404, 230, 82, 92, 1118, a3))
    # front of the box with the tray of books
    front = poly_pts([(bx0, by - 70), (bx1, by - 70), (bx1, by + 8), (bx0, by + 8)], 20, 1119, 0.4)
    for k in range(30):
        x = bx0 + 8 + k * 13.4
        h = rnd.uniform(40, 62)
        col = rnd.choice(["#8A2A2A", "#2E4A7A", "#C8902A", "#3E6A3A", "#6A3A5A", "#B85A2A", "#E8DCC0", "#4A3A2A"])
        out.append(book_spine(D, x, by - 64, 12, h, col, 1120 + k, lean=rnd.uniform(-3, 3)))
    out.append(painted(D, front, green, 1121, sdir=(1, 0.4), sk=0.12, angle=0, n=30, inkw=2.2, hi=0.3))
    out.append(taper([(bx0 + 6, by - 66), (bx1 - 6, by - 66)], 3, 3, "#7ABA8A", 0.7))
    out.append(painted(D, rect_pts(296, by - 46, 314, by - 20, 6, 1122, 0.2), ("#F2D488", "#C8A048", "#7A5A20"), 1122, sk=0.2, n=3, inkw=1.2, hi=0.5))
    out.append(cast(D, 300, by + 12, 220, 8, strength=0.45, seed=1123))
    # a few books laid flat on the parapet and a sleepy pigeon
    for k, (x, w_, col) in enumerate(((40, 70, "#8A2A2A"), (518, 60, "#2E4A7A"))):
        for j in range(3):
            out.append(painted(D, rect_pts(x + j * 3, 380 - j * 12, x + w_ + j * 2, 392 - j * 12, 10, 1124 + k * 5 + j, 0.3),
                               pal3(["#E8DCC0", col, "#3E6A3A"][j], 0.3, 0.3), 1124 + k * 5 + j, sk=0.2, n=3, inkw=1.1, hi=0.4))
    # a pigeon strutting on the parapet
    gx, gy = 548, 392
    out.append(cast(D, gx, gy + 2, 22, 4, strength=0.35, seed=1130))
    out.append(painted(D, [(gx - 26, gy - 18), (gx - 10, gy - 30), (gx + 12, gy - 30), (gx + 22, gy - 20), (gx + 10, gy - 6), (gx - 12, gy - 6)], ("#C8CCD8", "#8A90A2", "#4A5062"), 1131, sdir=(0.3, 1), sk=0.25, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(gx + 16, gy - 36, 9, 8, 1132, 0.05, 10), ("#A8B0C4", "#6A7088", "#3A3E52"), 1132, sk=0.2, n=3, inkw=1.2, hi=0.4))
    out.append(f'<path d="{blob(gx + 14, gy - 26, 7, 6, 1133, 0.1, 8)}" fill="#7AA08A" opacity="0.8"/>')
    out.append(f'<path d="M {gx + 24} {gy - 37} l 6 2 l -6 1 Z" fill="#3A3A3A"/><circle cx="{gx + 19}" cy="{gy - 38}" r="1.6" fill="#E86A2A"/>')
    out.append(f'<path d="{pd([(gx - 22, gy - 18), (gx - 40, gy - 22), (gx - 34, gy - 12)])}" fill="#4A5062"/>')
    for dx in (-4, 4):
        out.append(pline([(gx + dx, gy - 6), (gx + dx, gy)], "#D8606A", 2, 1134 + dx, 1, 1))
    out.append(taper([(gx - 10, gy - 20), (gx + 8, gy - 16)], 3, 1, "#3A3E52", 0.6))
    # lettering
    out.append(letters(D, 290, 128, "les bouquinistes", SERIF_IT, 84, "#1E4A30", ["#2E6A44", "#0A2A18", "#4A8A5E"], 1125, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8D8B8"))
    out.append(ruled(290, 168, "LE LONG DE LA SEINE", "#3A2A1A", font=JOS, size=18, ls=5, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 1126)


# ================================================================ 12. macarons — a box of every colour
MAC = {"framboise": ("#FFB0C0", "#E8607E", "#A02A48"), "pistache": ("#D8EAA8", "#A8C870", "#5E7A34"),
       "chocolat": ("#A8785A", "#6A3E26", "#341A0C"), "citron": ("#FFF4A8", "#F6DC5A", "#B8980E"),
       "vanille": ("#FFFBEA", "#F2E8CC", "#B8A884"), "lavande": ("#DCCCF2", "#B09AD8", "#6A5A9A"),
       "caramel": ("#F6CE96", "#D89A50", "#8A5420"), "rose": ("#FFD8DC", "#F4A8B4", "#B86A7A")}
FILL = {"framboise": "#C8284A", "pistache": "#7A9A3A", "chocolat": "#3A1A0A", "citron": "#FFF0A0", "vanille": "#FFFDF0",
        "lavande": "#F4ECFA", "caramel": "#A8601E", "rose": "#FFF0F2"}


def macaron(D, cx, cy, r, flavour, seed, tilt=0.55, bite=False):
    """A macaron seen from the front-top: smooth domed top shell, the frilly 'pied' and the filling at the waist,
    the bottom shell below."""
    pal = MAC[flavour]
    rnd = random.Random(seed)
    out = [cast(D, cx + r * 0.15, cy + r * 0.85, r * 1.05, r * 0.3, strength=0.4, seed=seed)]
    # bottom shell and its pied
    out.append(painted(D, ell_pts(cx, cy + r * 0.42, r * 0.98, r * tilt * 0.9, 0, 360, 28), pal, seed, sdir=(0.3, 1), sk=0.2, n=6, inkw=1.2, hi=0.3))
    pied = []
    for i in range(29):
        a = math.radians(i * 180 / 28)
        rr = r * (1.0 + 0.04 * (i % 2))
        pied.append((cx + rr * math.cos(a), cy + r * 0.3 + r * tilt * 0.9 * math.sin(a) + (i % 2) * 1.6))
    out.append(f'<path d="{smooth_open(pied)}" stroke="{lt(pal[1], 0.25)}" stroke-width="{r * 0.14:.1f}" fill="none" stroke-linecap="round"/>')
    out.append(specks(seed + 1, (cx - r, cy + r * 0.2, cx + r, cy + r * 0.6), [pal[2], lt(pal[1], 0.5)], int(r * 0.8), (0.6, 1.3), (0.4, 0.8)))
    # filling
    out.append(f'<path d="{smooth_open([(cx + r * 0.96 * math.cos(math.radians(a)), cy + r * 0.18 + r * tilt * 0.9 * math.sin(math.radians(a))) for a in range(0, 181, 10)])}" stroke="{FILL[flavour]}" stroke-width="{r * 0.16:.1f}" fill="none" stroke-linecap="round"/>')
    # top shell pied
    pied2 = [(cx + r * (1.02 + 0.04 * (i % 2)) * math.cos(math.radians(i * 180 / 28)), cy + r * 0.08 + r * tilt * math.sin(math.radians(i * 180 / 28)) + (i % 2) * 1.4) for i in range(29)]
    out.append(f'<path d="{smooth_open(pied2)}" stroke="{lt(pal[1], 0.2)}" stroke-width="{r * 0.13:.1f}" fill="none" stroke-linecap="round"/>')
    # top shell dome
    top = ell_pts(cx, cy, r, r * tilt, 0, 360, 30)[:-1]
    out.append(painted(D, top, pal, seed + 2, sdir=(0.4, 0.9), sk=0.18, angle=-20, n=10, slen=(r * 0.3, r * 0.8), sw=(0.6, 1.6), inkw=1.3, inkop=0.55, hi=0.55, hik=0.12, curve=0.4))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * tilt * 0.4, r * 0.32, r * tilt * 0.18, seed + 3, 0.15, 10, -15)}" fill="#FFFFFF" opacity="0.55"/>')
    if flavour == "pistache":
        out.append(specks(seed + 4, (cx - r * 0.5, cy - r * 0.3, cx + r * 0.5, cy + r * 0.2), ["#5E8A2A", "#8AB04A"], 6, (1, 1.8), (0.7, 1)))
    if flavour == "lavande":
        out.append(specks(seed + 4, (cx - r * 0.5, cy - r * 0.3, cx + r * 0.5, cy + r * 0.2), ["#6A4A9A"], 5, (0.8, 1.4), (0.7, 1)))
    if flavour == "chocolat":
        out.append(pline([(cx - r * 0.5, cy - r * 0.05), (cx - r * 0.1, cy - r * 0.2), (cx + r * 0.4, cy - r * 0.02)], "#2A1006", 2, seed, 0.6, 1))
    return "".join(out)


@design("macarons")
def macarons():
    D = Doc2("fr-mac")
    # pâtisserie wallpaper: celadon with fine vertical stripes and little gilt dots
    out = [sky(D, [(0, "#D8ECE2"), (1, "#C2DED2")], 1201, 600, ["#FFFFFF", "#A8CCBC"], 60, angle=-80, sop=(0.04, 0.12))]
    for k in range(-1, 21):
        x = k * 32
        out.append(f'<path d="M {x} 0 L {x} 600" stroke="#FFFFFF" stroke-width="7" opacity="0.4"/>')
        out.append(f'<path d="M {x + 16} 0 L {x + 16} 600" stroke="#9AC4B0" stroke-width="1.4" opacity="0.6"/>')
    out.append(soft_glow(D, 300, 380, 280, "#FFFFFF", 0.5))
    # marble shelf
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FBF8F2"), (1, "#DCD4C8")])}"/>')
    rnd = random.Random(1202)
    for k in range(6):
        y = 480 + rnd.uniform(0, 110)
        x = rnd.uniform(-40, 500)
        out.append(pline([(x, y), (x + 80, y + rnd.uniform(-10, 10)), (x + 170, y + rnd.uniform(-14, 14))], "#B8B0A6", rnd.uniform(0.8, 1.6), k, 0.5, 1))
    out.append(painted(D, rect_pts(-10, 464, 610, 476, 30, 1203, 0.4), ("#FFFFFF", "#EEE8DE", "#B8AE9E"), 1203, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    # the open box: lid propped behind, tray of two rows, a satin ribbon untied
    lid = [(126, 262), (474, 262), (466, 388), (134, 388)]
    out.append(painted(D, poly_pts(lid, 20, 1204, 0.4), ("#FFFFFF", "#F6F0E4", "#C8BCA8"), 1204, sdir=(0.3, 1), sk=0.12, angle=0, n=20, inkw=1.8, hi=0.4))
    out.append(f'<path d="{hg.org_rect(142, 276, 316, 98, 1205, 0.4, 20, 4)}" fill="none" stroke="#C8A048" stroke-width="2.4" opacity="0.8"/>')
    for x in (160, 440):
        out.append(sparkle(x, 324, 6, "#C8A048", 0.8))
    # a satin bow on the lid
    bwx, bwy = 300, 322
    for sg in (-1, 1):
        loop = [(bwx, bwy), (bwx + sg * 30, bwy - 26), (bwx + sg * 52, bwy - 18), (bwx + sg * 48, bwy + 8), (bwx + sg * 20, bwy + 8)]
        out.append(painted(D, loop, ("#FFB0C0", "#E8607E", "#A02A48"), 1240 + sg, sdir=(0.3, 1), sk=0.25, n=8, inkw=1.4, hi=0.5))
        tail = [(bwx, bwy + 4), (bwx + sg * 12, bwy + 40), (bwx + sg * 26, bwy + 52), (bwx + sg * 30, bwy + 42), (bwx + sg * 8, bwy + 4)]
        out.append(painted(D, tail, ("#FFB0C0", "#E8607E", "#A02A48"), 1242 + sg, sdir=(0.3, 1), sk=0.25, n=6, inkw=1.3, hi=0.4))
    out.append(painted(D, blob_pts(bwx, bwy, 10, 9, 1244, 0.05, 10), ("#FFB0C0", "#E8607E", "#A02A48"), 1244, sk=0.2, n=3, inkw=1.3, hi=0.5))
    box = [(70, 384), (530, 384), (552, 492), (48, 492)]
    out.append(cast(D, 310, 498, 280, 16, strength=0.5, seed=1206))
    out.append(painted(D, poly_pts(box, 20, 1207, 0.4), ("#FFFFFF", "#F4EEE2", "#C0B4A0"), 1207, sdir=(0.3, 1), sk=0.12, angle=0, n=20, inkw=1.8, hi=0.4))
    out.append(f'<path d="{smooth_closed(poly_pts([(84, 392), (516, 392), (534, 480), (66, 480)], 20, 1208, 0.3))}" fill="#E8DCC8"/>')
    flavours = ["framboise", "pistache", "chocolat", "citron", "lavande", "caramel", "rose", "vanille"]
    for row, y in enumerate((410, 456)):
        for i in range(5):
            x = 128 + i * 86 + (row - 0.5) * 6
            f = flavours[(i + row * 3) % 8]
            out.append(macaron(D, x, y, 38, f, 1210 + row * 10 + i, tilt=0.5))
    out.append(painted(D, poly_pts([(48, 482), (552, 482), (552, 500), (48, 500)], 20, 1230, 0.3), ("#FFFFFF", "#F4EEE2", "#C0B4A0"), 1230, sk=0.2, n=10, inkw=1.6, hi=0.4))
    out.append(taper([(48, 490), (552, 490)], 4, 4, "#C8A048", 0.8))
    # the satin ribbon, untied, trailing on the marble
    rib = catmull([(60, 494), (44, 532), (96, 560), (170, 540), (230, 572)], 6)
    out.append(taper([(x + 2, y + 4) for x, y in rib], 26, 20, "#A02A48", 0.6))
    out.append(taper(rib, 26, 20, "#E8607E"))
    out.append(taper([(x, y - 5) for x, y in rib], 6, 4, "#FFC8D4", 0.8))
    # two macarons waiting outside the box
    out.append(macaron(D, 404, 556, 36, "framboise", 1231, tilt=0.55))
    out.append(macaron(D, 492, 548, 32, "pistache", 1232, tilt=0.55))
    for x, y, s in ((90, 240, 9), (520, 260, 8), (60, 380, 6)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.9))
    # lettering
    out.append(letters(D, 300, 148, "macarons", SERIF_IT, 132, "#C83A62", ["#E8607E", "#8A1A3A", "#F08AA0"], 1233, max_w=430,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC8D4"))
    out.append(ruled(300, 196, "UN DE CHAQUE COULEUR", "#3E7A5E", font=JOS, size=19, ls=5, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 1234)


# ================================================================ 13. galette des rois — qui a la fève ?
def galette(D, cx, cy, rx, ry, seed, cut=(28, 68)):
    """A puff-pastry galette seen at 3/4: deep golden glaze, the classic curved 'rosace' scoring, scalloped edge;
    one slice removed (angles in degrees) showing the frangipane and the flaky layers."""
    rnd = random.Random(seed)
    th = 26
    a0, a1 = cut

    def E(a, r=1.0, dy=0.0):
        return (cx + rx * r * math.cos(math.radians(a)), cy + ry * r * math.sin(math.radians(a)) + dy)

    rim = [E(a + 2.5 * math.sin(a * 0.7854 * 2), 1 + 0.018 * math.cos(math.radians(a) * 16)) for a in range(a1, a0 + 360, 4)]
    top = rim + [(cx, cy)]
    out = [cast(D, cx + 10, cy + th + 14, rx * 1.05, ry * 0.9, strength=0.5, seed=seed)]
    # side wall (flaky layers)
    side = [E(a, 1, th) for a in range(max(a1, 0), 181, 4)] + [E(a, 1) for a in range(180, max(a1, 0) - 1, -4)]
    out.append(painted(D, side, ("#F6C878", "#C8822E", "#7A4410"), seed, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.8, hi=0.35))
    for k in range(5):
        out.append(pline([E(a, 1, 5 + k * 4.4) for a in range(max(a1, 0) + 2, 180, 8)], rnd.choice(["#FFE6A8", "#A8601E"]), 1.2, seed + k, 0.6, 1))
    # the cut faces
    for a, sgn in ((a1, 1), (a0, -1)):
        face = [(cx, cy), E(a), E(a, 1, th), (cx, cy + th)]
        out.append(painted(D, face, ("#FFDC98", "#E8A850", "#9A5A1A"), seed + int(a), sdir=(0, 1), sk=0.15, n=8, inkw=1.4, hi=0.3))
        fid = D.clip(f'<path d="{smooth_closed(face)}"/>')
        fl = []
        for t, col, w_ in ((0.18, "#FFF0C8", 1.6), (0.3, "#B8701E", 1.2), (0.7, "#B8701E", 1.2), (0.82, "#FFF0C8", 1.6)):
            fl.append(pline([(cx, cy + th * t), E(a, 1, th * t)], col, w_, seed + int(t * 10), 0.8, 1))
        fl.append(taper([(cx, cy + th * 0.5), ((cx + E(a)[0]) / 2, (cy + E(a)[1]) / 2 + th * 0.5), E(a, 1, th * 0.5)], 8, 8, "#F6E0A0", 0.95))
        out.append(f'<g {fid}>{"".join(fl)}</g>')
    # top: glazed dome with rosace scoring
    td = smooth_closed(top)
    out.append(f'<path d="{td}" fill="{D.rad([(0, "#FFD27A"), (0.6, "#E8A040"), (1, "#B8661E")], 0.45, 0.4, 0.65)}"/>')
    cid = D.clip(f'<path d="{td}"/>')
    sc = []
    for k in range(18):
        b = k * 20
        pts = []
        for i in range(12):
            t = i / 11
            a = b + 70 * t
            r = 0.08 + 0.9 * t
            pts.append(E(a, r))
        sc.append(taper(pts, 1.2, 3.4, "#8A4610", 0.7))
        sc.append(taper([(x - 2, y - 1.5) for x, y in pts], 0.8, 2.2, "#FFE6A8", 0.7))
    sc.append(strokes(D.nid(), td, (cx - rx, cy - ry, cx + rx, cy + ry), ["#FFE6A8", "#B8661E"], seed, n=60, angle=-20, length=(10, 30), width=(1, 3), opacity=(0.1, 0.3)))
    sc.append(f'<path d="{blob(cx - rx * 0.35, cy - ry * 0.4, rx * 0.3, ry * 0.18, seed, 0.2, 12, -15)}" fill="#FFF4D0" opacity="0.45"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(ink(td, "#7A3A0E", 2, seed + 3, 2, 0.7))
    return "".join(out)


def paper_crown(D, cx, base, w, h, seed, tilt=0):
    """The gold card crown that comes with the galette: zigzag points with little balls, embossed jewels."""
    n = 6
    pts = [(cx - w / 2, base)]
    for i in range(n * 2 + 1):
        x = cx - w / 2 + w * i / (n * 2)
        y = base - h * (1.0 if i % 2 == 0 else 0.45)
        pts.append((x, y))
    pts.append((cx + w / 2, base))
    pts = rot(pts, cx, base, tilt)
    out = [painted(D, pts, ("#FFF0A0", "#E8B830", "#8A6A10"), seed, sdir=(0.6, 0.6), sk=0.18, angle=-80, n=20, inkw=1.8, hi=0.5)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    for i in range(n * 2 + 1):
        x = cx - w / 2 + w * i / (n * 2)
        inner.append(taper(rot([(x, base), (x, base - h * (1.0 if i % 2 == 0 else 0.45))], cx, base, tilt), 1.4, 1, "#FFFFFF", 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper(rot([(cx - w / 2, base - h * 0.2), (cx + w / 2, base - h * 0.2)], cx, base, tilt), 3, 3, "#B8901E", 0.7))
    for i in range(0, n * 2 + 1, 2):
        x = cx - w / 2 + w * i / (n * 2)
        p = rot([(x, base - h - 4)], cx, base, tilt)[0]
        out.append(painted(D, blob_pts(p[0], p[1], 4.4, 4.4, seed + i, 0.05, 10), ("#FFF6C0", "#F2C83A", "#8A6A10"), seed + i, sk=0.2, n=2, inkw=1, hi=0.6))
    for k, col in enumerate((ROUGE[1], BLEU[1], "#2E8A4E", ROUGE[1], BLEU[1])):
        x = cx - w * 0.36 + k * w * 0.18
        p = rot([(x, base - h * 0.32)], cx, base, tilt)[0]
        out.append(painted(D, blob_pts(p[0], p[1], 5, 4, seed + 20 + k, 0.05, 10), pal3(col, 0.4, 0.4), seed + 20 + k, sk=0.25, n=2, inkw=1, hi=0.6))
    return "".join(out)


@design("galette-des-rois")
def galette_des_rois():
    D = Doc2("fr-gr")
    # January evening: deep blue with gilt stars
    out = [sky(D, [(0, "#1E2E5E"), (1, "#2E3E72")], 1301, 600, ["#3A4A8A", "#141E44"], 90, angle=-6, sop=(0.06, 0.15))]
    out.append(soft_glow(D, 300, 380, 300, "#FFE6A0", 0.35))
    rnd = random.Random(1302)
    for _ in range(30):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 300)
        out.append(sparkle(x, y, rnd.uniform(2.5, 6), "#F6D88A", rnd.uniform(0.5, 0.95)))
    # linen tablecloth edge
    tc = "M -10 400 L 610 400 L 610 610 L -10 610 Z"
    out.append(f'<path d="{tc}" fill="#F4ECDA"/>')
    out.append(strokes(D.nid(), tc, (-40, 400, 610, 610), ["#FFFFFF", "#D8CCB4"], 1303, n=80, angle=-2, length=(30, 90), width=(1, 3), opacity=(0.2, 0.4)))
    out.append(shade_over(D, tc, "#2A1A0A", 0.3, 0, 0, 0, 1, 0.4))
    for y in (416, 424):
        out.append(taper([(-10, y), (610, y)], 3, 3, ROUGE[1], 0.75))
    # wooden board, the galette with a slice removed
    out.append(painted(D, ell_pts(282, 418, 236, 86, 0, 360, 40), ("#D8A06A", "#A86A3A", "#5E3618"), 1304, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=2, hi=0.3))
    out.append(galette(D, 276, 376, 200, 72, 1305))
    # the crown leaning on the galette, the slice on a little plate with the fève
    out.append(paper_crown(D, 430, 330, 160, 64, 1306, tilt=8))
    sx, sy = 470, 520
    out.append(cast(D, sx + 8, sy + 16, 82, 14, strength=0.4, seed=1307))
    out.append(painted(D, ell_pts(sx, sy + 6, 80, 22, 0, 360, 30), WHITE, 1308, sk=0.12, n=10, inkw=1.6, hi=0.4))
    out.append(pline(ell_pts(sx, sy + 6, 68, 16, 15, 165, 12), "#C8A048", 2, 1309, 0.8, 1))
    sl = [(sx - 56, sy + 6), (sx + 40, sy - 18), (sx + 48, sy - 2), (sx + 48, sy + 14), (sx - 52, sy + 22)]
    out.append(painted(D, sl, ("#FFDC98", "#E8A850", "#9A5A1A"), 1310, sk=0.15, n=8, inkw=1.4, hi=0.3))
    for k, (dy, col) in enumerate(((2, "#FFF0C8"), (5, "#B8701E"), (12, "#B8701E"), (15, "#FFF0C8"))):
        out.append(pline([(sx - 52, sy + 6 + dy), (sx + 46, sy - 16 + dy)], col, 1.3, 1311 + k, 0.8, 1))
    out.append(taper([(sx - 50, sy + 15), (sx + 46, sy - 7)], 6, 6, "#F6E0A0", 0.95))
    top = [(sx - 58, sy + 4), (sx - 10, sy - 12), (sx + 40, sy - 20), (sx + 30, sy - 26), (sx - 20, sy - 14)]
    out.append(painted(D, top, ("#FFD27A", "#E8A040", "#8A4610"), 1315, sk=0.2, n=6, inkw=1.4, hi=0.5))
    # the fève: a little glazed porcelain sun
    fx, fy = sx - 76, sy + 30
    out.append(cast(D, fx + 3, fy + 8, 14, 4, strength=0.4, seed=1316))
    for k in range(10):
        a = math.radians(k * 36)
        out.append(f'<path d="{pd([(fx + math.cos(a) * 9, fy + math.sin(a) * 9 * 0.8), (fx + math.cos(a + 0.18) * 15, fy + math.sin(a + 0.18) * 15 * 0.8), (fx + math.cos(a + 0.36) * 9, fy + math.sin(a + 0.36) * 9 * 0.8)])}" fill="#F2C83A" stroke="#8A6A10" stroke-width="0.8"/>')
    out.append(painted(D, blob_pts(fx, fy, 10, 8.5, 1317, 0.03, 12), ("#FFF6D0", "#F6D460", "#A8801E"), 1317, sk=0.2, n=3, inkw=1.2, hi=0.6))
    out.append(f'<circle cx="{fx - 3}" cy="{fy - 3}" r="2" fill="#FFFFFF" opacity="0.9"/>')
    out.append(sparkle(fx + 16, fy - 14, 7, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 128, "galette des rois", SERIF_IT, 92, "#F6D88A", ["#FFF0B0", "#E8B830", "#FFE07A"], 1318, max_w=450,
                       shadow="#0A1230", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 174, f"QUI A LA FÈVE{NB}?", "#FFF4DC", font=JOS, size=19, ls=6, line_w=34, gap=14, max_w=380))
    return finish_f(D, out, 1319, "#0A1230")


# ================================================================ 14. le goûter — 16 h 30, home from school
def pain_au_chocolat(D, cx, cy, w, seed, rot_=0):
    """A rectangular laminated roll, glossy top, layered ends with two dark chocolate bars peeking out."""
    h = w * 0.42
    pts = rot([(cx - w / 2, cy + h * 0.3), (cx - w / 2 + 4, cy - h * 0.3), (cx - w * 0.2, cy - h * 0.55), (cx + w * 0.2, cy - h * 0.55), (cx + w / 2 - 4, cy - h * 0.3),
               (cx + w / 2, cy + h * 0.3), (cx + w * 0.2, cy + h * 0.45), (cx - w * 0.2, cy + h * 0.45)], cx, cy, rot_)
    out = [cast(D, cx + 6, cy + h * 0.55, w * 0.55, h * 0.2, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#FCD592", "#DD9338", "#8E4A12"), seed, sdir=(0.3, 1), sk=0.22, angle=rot_, n=20, inkw=1.8, hi=0.5, hik=0.12))
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    for k in range(3):
        y = cy - h * 0.2 + k * h * 0.2
        inner.append(taper(rot([(cx - w / 2, y), (cx - w * 0.25, y - 2), (cx + w * 0.25, y - 2), (cx + w / 2, y)], cx, cy, rot_), 1.4, 1.4, "#9A5214", 0.35))
    inner.append(f'<path d="{blob(cx - w * 0.1, cy - h * 0.32, w * 0.3, h * 0.12, seed, 0.2, 10, rot_)}" fill="#FFF0C8" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for sg in (-1, 1):
        for k, dy in enumerate((-0.12, 0.16)):
            p = rot([(cx + sg * (w / 2 - 3), cy + h * dy)], cx, cy, rot_)[0]
            out.append(painted(D, rot(rect_pts(p[0] - 7, p[1] - 5, p[0] + 7, p[1] + 5, 4, seed + k, 0.2), p[0], p[1], rot_), CHOC, seed + 10 + k + sg, sk=0.2, n=2, inkw=1.2, hi=0.4))
    return "".join(out)


def tartine(D, cx, cy, w, seed, rot_=0, jam=("#F06A6A", "#C8202E", "#6A0A12")):
    """A long slice of baguette cut lengthways: crust edge, butter, a glossy layer of strawberry jam."""
    h = w * 0.24
    outer = rot(along(cx - w / 2, cy, cx + w / 2, cy, lambda t: h / 2 * (0.75 + 0.25 * math.sin(math.pi * t) ** 0.4), 24), cx, cy, rot_)
    out = [cast(D, cx + 6, cy + h * 0.6, w * 0.55, h * 0.3, strength=0.4, seed=seed)]
    out.append(painted(D, outer, CRUST, seed, sk=0.2, n=10, inkw=1.6, hi=0.3))
    crumb = rot(along(cx - w / 2 + 7, cy - 1, cx + w / 2 - 7, cy - 1, lambda t: (h / 2 - 5) * (0.75 + 0.25 * math.sin(math.pi * t) ** 0.4), 24), cx, cy, rot_)
    out.append(f'<path d="{smooth_closed(crumb)}" fill="#FBEFD4"/>')
    out.append(specks(seed + 5, bbox(crumb), ["#D8BC88"], int(w * 0.2), (0.8, 2), (0.5, 0.9)))
    out.append(f'<path d="{smooth_closed(crumb)}" fill="#FFF2B0" opacity="0.45"/>')
    jamp = rot(blob_pts(cx + 6, cy - 1, w / 2 - 22, h / 2 - 9, seed + 2, 0.1, 22), cx, cy, rot_)
    out.append(painted(D, jamp, jam, seed + 2, sk=0.2, n=10, inkw=1.2, inkop=0.5, hi=0.45))
    rnd = random.Random(seed)
    for _ in range(8):
        x, y = rot([(cx + rnd.uniform(-w * 0.35, w * 0.35), cy + rnd.uniform(-h * 0.2, h * 0.2))], cx, cy, rot_)[0]
        out.append(f'<path d="{blob(x, y, 3, 2.4, rnd.randint(1, 99), 0.2, 6)}" fill="{jam[2]}" opacity="0.6"/>')
    out.append(taper(rot([(cx - w * 0.3, cy - h * 0.18), (cx, cy - h * 0.24), (cx + w * 0.25, cy - h * 0.16)], cx, cy, rot_), 2, 3, "#FFFFFF", 0.7))
    return "".join(out)


def bol(D, cx, base, w, seed, glaze=("#FFFFFF", "#F4F0E8", "#B8B0A6"), dots=ROUGE[1], drink=("#A8704A", "#6A3A1E", "#3A1A0A")):
    """A French breakfast bowl (no handle): wide, polka dots, hot chocolate inside with a little skin of foam."""
    h = w * 0.52
    top = base - h
    body = [(cx - w / 2, top), (cx - w / 2 + 4, top + h * 0.45), (cx - w * 0.3, base - 4), (cx - w * 0.18, base), (cx + w * 0.18, base), (cx + w * 0.3, base - 4), (cx + w / 2 - 4, top + h * 0.45), (cx + w / 2, top)]
    out = [cast(D, cx + 8, base + 4, w * 0.5, 9, strength=0.45, seed=seed)]
    out.append(painted(D, body, glaze, seed, sdir=(1, 0.3), sk=0.18, angle=-90, n=12, inkw=1.8, hi=0.5, hik=0.06))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    rnd = random.Random(seed)
    dts = []
    for j in range(4):
        for i in range(9):
            x = cx - w / 2 + 6 + i * w / 8 + (j % 2) * w / 16
            y = top + 12 + j * h * 0.22
            dts.append(f'<path d="{blob(x, y, 4.6, 4, rnd.randint(1, 999), 0.12, 8)}" fill="{dots}" opacity="0.9"/>')
    dts.append(shade_over(D, smooth_closed(body), "#2A1A10", 0.35, 0, 0, 1, 0, 0.45))
    out.append(f'<g {cid}>{"".join(dts)}</g>')
    out.append(taper([(cx - w * 0.4, top + 10), (cx - w * 0.36, top + h * 0.6)], 3, 6, "#FFFFFF", 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.11, 0, 360, 30))}" fill="{glaze[1]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 2, w / 2 - 5, w * 0.09, 0, 360, 30))}" fill="{drink[1]}"/>')
    out.append(f'<path d="{blob(cx + 6, top + 2, w * 0.3, w * 0.05, seed + 1, 0.2, 12)}" fill="{drink[0]}" opacity="0.7"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top, w / 2, w * 0.11, 0, 360, 30)), INK, 1.4, seed + 2, 1, 0.7))
    return "".join(out)


def cartable(D, x, y, w, h, seed):
    """A leather school satchel: rounded flap, two buckled straps, a ruler sticking out."""
    out = [cast(D, x + w * 0.55, y + h + 4, w * 0.6, 9, strength=0.45, seed=seed)]
    # a pencil and a ruler poking out of the flap
    out.append(painted(D, rot(rect_pts(x + w * 0.62, y - 34, x + w * 0.62 + 9, y + 6, 6, seed + 8, 0.2), x + w * 0.62, y, 14), ("#FFF06A", "#F2C21C", "#9A7A0A"), seed + 8, sk=0.2, n=3, inkw=1.2, hi=0.4))
    out.append(painted(D, rot(rect_pts(x + w * 0.2, y - 26, x + w * 0.2 + 14, y + 6, 6, seed + 9, 0.2), x + w * 0.2, y, -10), ("#F6F0E0", "#E0D4B8", "#9A8A6A"), seed + 9, sk=0.2, n=3, inkw=1.2, hi=0.4))
    body = rect_pts(x, y, x + w, y + h, 16, seed, 0.6)
    out.append(painted(D, body, ("#D8955A", "#A85E2A", "#5A2E10"), seed, sdir=(1, 0.3), sk=0.18, angle=-80, n=20, inkw=2, hi=0.4))
    flap = [(x - 2, y - 4), (x + w + 2, y - 4), (x + w + 2, y + h * 0.55), (x + w - 14, y + h * 0.62), (x + 14, y + h * 0.62), (x - 2, y + h * 0.55)]
    out.append(painted(D, flap, ("#E8A86A", "#B86A32", "#6A3414"), seed + 1, sdir=(1, 0.6), sk=0.2, angle=-10, n=16, inkw=1.8, hi=0.45))
    for k in range(2):
        sx = x + w * (0.28 + 0.44 * k)
        out.append(taper([(sx, y - 2), (sx, y + h * 0.75)], 9, 9, "#6A3414"))
        out.append(painted(D, rect_pts(sx - 8, y + h * 0.66, sx + 8, y + h * 0.82, 6, seed + 3 + k, 0.2), ("#FFF0A0", "#C8A048", "#7A5A10"), seed + 3 + k, sk=0.2, n=2, inkw=1.2, hi=0.6))
    out.append(taper([(x + w * 0.3, y), (x + w * 0.5, y - 26), (x + w * 0.7, y)], 6, 6, "#7A4018"))
    out.append(pline([(x + 6, y + h * 0.5), (x + w - 6, y + h * 0.5)], "#FFE2B8", 1.2, seed + 5, 0.4, 1))
    return "".join(out)


@design("le-gouter")
def le_gouter():
    D = Doc2("fr-gt")
    # pale-blue kitchen wall, afternoon sun through the window
    out = [sky(D, [(0, "#D6E6F0"), (1, "#C4D8E6")], 1401, 600, ["#FFFFFF", "#A8C4D8"], 70, angle=-80, sop=(0.05, 0.14))]
    out.append(f'<path d="{pd([(360, -10), (610, -10), (610, 330), (430, 380)])}" fill="#FFF6DA" opacity="0.4"/>')
    out.append(soft_glow(D, 460, 220, 260, "#FFF2C8", 0.45))
    # oilcloth on the table: red cherries on white
    tc = "M -10 340 L 610 340 L 610 610 L -10 610 Z"

    def cherry_tile(c):
        t = [f'<rect width="{c}" height="{c}" fill="#FFFDF6"/>']
        for (fx, fy) in ((0.25, 0.3), (0.75, 0.8)):
            x, y = fx * c, fy * c
            t.append(f'<path d="M {x:.1f} {y:.1f} q 4 -14 12 -18 M {x + 10:.1f} {y + 2:.1f} q 0 -12 2 -20" stroke="#4A6A2A" stroke-width="1.4" fill="none"/>')
            t.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#D8282E"/><circle cx="{x + 10:.1f}" cy="{y + 2:.1f}" r="5" fill="#C8202A"/>')
            t.append(f'<circle cx="{x - 1.5:.1f}" cy="{y - 1.5:.1f}" r="1.4" fill="#FFFFFF" opacity="0.8"/>')
            t.append(f'<path d="M {x + 12:.1f} {y - 18:.1f} q 8 -4 12 2 q -8 4 -12 -2 Z" fill="#6A9A3A"/>')
        return "".join(t)
    pat = D.pattern(64, 64, cherry_tile(64))
    out.append(f'<path d="{tc}" fill="{pat}"/>')
    out.append(f'<path d="{tc}" fill="{D.lin([(0, "#3A2A1A", 0.25), (0.3, "#3A2A1A", 0.05), (1, "#3A2A1A", 0.15)])}"/>')
    out.append(f'<rect x="-10" y="334" width="620" height="10" fill="#8A6A4A" opacity="0.45"/>')
    # the satchel dropped by the table, right
    out.append(cartable(D, 420, 280, 136, 96, 1402))
    # bowl of hot chocolate, steam
    out.append(bol(D, 210, 450, 170, 1403))
    out.append(steam(210, 350, 70, 1404, "#FFFFFF", 3, 30, 7, 0.6))
    # pain au chocolat on a paper napkin, tartine in front
    nap = rot(rect_pts(350, 410, 520, 500, 16, 1405, 0.6), 435, 455, -6)
    out.append(painted(D, nap, ("#FFFFFF", "#F6F2EA", "#C8C0B4"), 1405, sk=0.12, n=10, inkw=1.4, hi=0.4))
    out.append(pain_au_chocolat(D, 438, 450, 130, 1406, rot_=-8))
    out.append(tartine(D, 290, 536, 250, 1407, rot_=-6))
    # a few crumbs and a dropped spoon
    rnd = random.Random(1408)
    for _ in range(14):
        x, y = rnd.uniform(330, 560), rnd.uniform(500, 560)
        out.append(f'<path d="{blob(x, y, rnd.uniform(1, 2.6), rnd.uniform(0.8, 2), rnd.randint(1, 999), 0.3, 6)}" fill="{rnd.choice(["#D8923A", "#F2C070"])}"/>')
    out.append(taper([(70, 520), (100, 498), (124, 482)], 4, 3, "#B8BCC4"))
    out.append(painted(D, rot(blob_pts(62, 528, 11, 7, 1409, 0.05, 10), 62, 528, -35), ZINC, 1409, sk=0.2, n=3, inkw=1.2, hi=0.5))
    # lettering
    out.append(letters(D, 300, 140, "le goûter", SERIF_IT, 126, "#C8282E", ["#E8504A", "#8A0A12", "#F27A6A"], 1410, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A8"))
    out.append(ruled(300, 186, "16 H 30, APRÈS L’ÉCOLE", BLEU[2], font=JOS, size=19, ls=5, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 1411)


# ================================================================ 15. L'heure de l'apéro — under the plane trees
def plane_trunk(D, x, base, top, w, seed):
    """A plane-tree trunk with its camouflage bark: cream, olive and grey patches peeling."""
    rnd = random.Random(seed)
    pts = [(x - w / 2, base), (x - w / 2 + 4, (base + top) / 2), (x - w * 0.42, top), (x + w * 0.42, top), (x + w / 2 - 4, (base + top) / 2), (x + w / 2 + 6, base)]
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="#C8C0A0"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for _ in range(int((base - top) * w / 260)):
        px, py = rnd.uniform(x - w / 2, x + w / 2), rnd.uniform(top, base)
        inner.append(f'<path d="{blob(px, py, rnd.uniform(6, 16), rnd.uniform(8, 22), rnd.randint(1, 9999), 0.3, 10)}" fill="{rnd.choice(["#E8E2C8", "#9A9A72", "#7A7A62", "#D8D0B0", "#B8B48A"])}" opacity="0.9"/>')
    inner.append(shade_over(D, d, "#2A2A1A", 0.5, 0, 0, 1, 0, 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#4A4A32", 1.8, seed, 2, 0.6))
    return "".join(out)


def anise_glass(D, cx, base, h, seed, fill=0.72):
    """A tall tumbler of anise apéritif turned cloudy pale yellow with water, two ice cubes."""
    w0, w1 = h * 0.3, h * 0.24
    gl = [(cx - w0, base - h), (cx + w0, base - h), (cx + w1, base), (cx - w1, base)]
    out = [cast(D, cx + 6, base + 2, w0 * 1.2, 6, strength=0.35, seed=seed)]
    liq_top = base - h * fill
    wl = w1 + (w0 - w1) * fill
    liq = [(cx - wl, liq_top), (cx + wl, liq_top), (cx + w1 - 1.5, base - 3), (cx - w1 + 1.5, base - 3)]
    out.append(f'<path d="{smooth_closed(liq)}" fill="{D.lin([(0, "#FBEFA8"), (1, "#E8CC5A")])}" opacity="0.95"/>')
    rnd = random.Random(seed)
    for k in range(2):
        ix, iy = cx - wl * 0.4 + k * wl * 0.7, liq_top + 4 + k * 8
        out.append(f'<path d="{hg.org_rect(ix - 9, iy - 6, 17, 14, seed + k, 0.4, 6, 3)}" fill="#FFFFFF" opacity="0.65" transform="rotate({rnd.uniform(-20, 20):.0f} {ix} {iy})"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, liq_top, wl, 3.5, 0, 360, 16))}" fill="#FFFBE0"/>')
    out.append(f'<path d="{smooth_closed(gl)}" fill="#E8F4F4" opacity="0.18"/>')
    out.append(taper([(cx - w0 * 0.7, base - h + 6), (cx - w1 * 0.7, base - 6)], 3, 2, "#FFFFFF", 0.8))
    out.append(ink(smooth_closed(gl), "#7A9A9A", 1.6, seed, 2, 0.7))
    out.append(ink(smooth_closed(ell_pts(cx, base - h, w0, 4, 0, 360, 16)), "#7A9A9A", 1.4, seed + 1, 1, 0.7))
    return "".join(out)


def carafe(D, cx, base, h, seed):
    """A bistro water carafe: round belly, tall neck, water line, highlights."""
    pts = [(cx - h * 0.12, base - h), (cx + h * 0.12, base - h), (cx + h * 0.1, base - h * 0.62), (cx + h * 0.3, base - h * 0.32), (cx + h * 0.28, base - 4),
           (cx - h * 0.28, base - 4), (cx - h * 0.3, base - h * 0.32), (cx - h * 0.1, base - h * 0.62)]
    out = [cast(D, cx + 6, base + 2, h * 0.34, 6, strength=0.35, seed=seed)]
    water = [(cx - h * 0.22, base - h * 0.48), (cx + h * 0.22, base - h * 0.48), (cx + h * 0.3, base - h * 0.32), (cx + h * 0.27, base - 6), (cx - h * 0.27, base - 6), (cx - h * 0.3, base - h * 0.32)]
    out.append(f'<path d="{smooth_closed(water)}" fill="#C8E4EC" opacity="0.55"/>')
    out.append(f'<path d="{smooth_closed(pts)}" fill="#E8F4F4" opacity="0.22"/>')
    out.append(taper([(cx - h * 0.2, base - h * 0.36), (cx - h * 0.22, base - h * 0.12)], 3, 5, "#FFFFFF", 0.8))
    out.append(taper([(cx - h * 0.06, base - h * 0.95), (cx - h * 0.06, base - h * 0.66)], 2, 2, "#FFFFFF", 0.7))
    out.append(ink(smooth_closed(pts), "#7A9A9A", 1.8, seed, 2, 0.7))
    return "".join(out)


@design("l-heure-de-l-apero")
def l_heure_de_l_apero():
    D = Doc2("fr-ap")
    # golden-hour village square: warm stone, green shutters, dappled light
    out = [sky(D, [(0, "#F6C88A"), (1, "#F2DCB0")], 1501, 600, ["#FFE8C0", "#E8A870"], 70, angle=-80, sop=(0.05, 0.14))]
    # one window with green shutters, geraniums on the sill
    x0 = 70
    out.append(painted(D, rect_pts(x0, 262, x0 + 96, 352, 20, 1502, 0.5), ("#F6D8A8", "#E8C088", "#A88050"), 1502, sk=0.1, n=10, inkw=1.2, inkop=0.4, hi=0.3))
    out.append(f'<path d="{hg.org_rect(x0 + 8, 270, 80, 76, 1508, 0.4, 14, 2)}" fill="#3A3A40" opacity="0.75"/>')
    out.append(f'<path d="{hg.org_rect(x0 + 46, 270, 4, 76, 1509, 0.2, 14, 1)}" fill="#E8C088"/>')
    for sg in (0, 1):
        sx = x0 - 30 + sg * 126
        out.append(painted(D, rect_pts(sx, 264, sx + 30, 350, 10, 1504 + sg, 0.4), ("#8AB89A", "#4E8A6A", "#24503A"), 1504 + sg, sdir=(1, 0.2), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.4))
        for k in range(6):
            out.append(pline([(sx + 4, 276 + k * 12), (sx + 26, 278 + k * 12)], "#24503A", 1.6, 1506 + k, 0.7, 1))
    out.append(painted(D, rect_pts(x0 - 6, 350, x0 + 102, 360, 10, 1520, 0.3), STONE, 1520, sk=0.2, n=4, inkw=1.2, hi=0.4))
    for k in range(5):
        out.append(painted(D, blob_pts(x0 + 10 + k * 19, 342, 10, 8, 1521 + k, 0.2, 10), ("#FF7A6A", "#E0281E", "#8A0A0A"), 1521 + k, sk=0.2, n=3, inkw=1, hi=0.4))
    # dappled shade from the leaves above
    rnd = random.Random(1509)
    for _ in range(26):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(0, 360), rnd.uniform(20, 46), rnd.uniform(12, 26), rnd.randint(1, 999), 0.3, 10)}" fill="#8A5A2A" opacity="0.12"/>')
    for _ in range(14):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(0, 360), rnd.uniform(10, 22), rnd.uniform(6, 12), rnd.randint(1, 999), 0.3, 10)}" fill="#FFF6D0" opacity="0.4"/>')
    out.append(plane_trunk(D, 556, 400, -10, 62, 1510))
    # gravel ground
    out.append(f'<rect x="-10" y="372" width="620" height="240" fill="{D.lin([(0, "#E2C898"), (1, "#C8A878")])}"/>')
    out.append(specks(1511, (0, 372, 600, 600), ["#A88A60", "#FFF0D0", "#8A6A48"], 300, (0.8, 2.2), (0.4, 0.9)))
    # the round bistro table
    tx, ty = 300, 470
    out.append(cast(D, tx + 30, 592, 170, 12, strength=0.4, seed=1512))
    out.append(taper([(tx, ty + 20), (tx, 586)], 10, 10, "#2E5A3E"))
    out.append(taper([(tx - 60, 594), (tx, 582), (tx + 60, 594)], 6, 6, "#2E5A3E"))
    out.append(painted(D, ell_pts(tx, ty + 10, 220, 56, 0, 360, 40), ("#5E9A72", "#2E6A4A", "#123A24"), 1513, sdir=(0, 1), sk=0.2, n=20, inkw=2, hi=0.3))
    out.append(painted(D, ell_pts(tx, ty, 220, 56, 0, 360, 40), ("#7AB88E", "#3E8A5E", "#1A4A30"), 1514, sdir=(0.3, 1), sk=0.12, n=30, inkw=2, hi=0.45))
    # leaf shadows on the tabletop
    tid = D.clip(f'<path d="{smooth_closed(ell_pts(tx, ty, 220, 56, 0, 360, 40))}"/>')
    sh = "".join(f'<path d="{blob(rnd.uniform(100, 500), rnd.uniform(ty - 50, ty + 50), rnd.uniform(14, 30), rnd.uniform(6, 12), rnd.randint(1, 999), 0.3, 10)}" fill="#0A2A18" opacity="0.18"/>' for _ in range(10))
    out.append(f'<g {tid}>{sh}</g>')
    # olives, saucisson on its little board, the carafe and two glasses
    ox_, oy_ = 150, 474
    out.append(painted(D, ell_pts(ox_, oy_, 48, 16, 0, 360, 20), ("#FFFFFF", "#F2EADC", "#B8AE9E"), 1515, sk=0.12, n=4, inkw=1.4, hi=0.4))
    for k in range(11):
        a = k * 0.7
        x, y = ox_ + math.cos(a) * 30 * (k % 3) / 2, oy_ - 6 + math.sin(a) * 6
        out.append(painted(D, blob_pts(x, y, 9, 6.5, 1516 + k, 0.05, 10), rnd.choice([("#B8B060", "#7A7A2A", "#3E3E12"), ("#6A5A6A", "#3A2A3A", "#1A0E1A")]), 1516 + k, sk=0.2, n=2, inkw=1, hi=0.5))
        out.append(f'<circle cx="{x - 2:.1f}" cy="{y - 2:.1f}" r="1.4" fill="#FFFFFF" opacity="0.8"/>')
    bx = 424
    out.append(painted(D, rot(rect_pts(bx - 66, 466, bx + 66, 496, 12, 1525, 0.4), bx, 481, -4), OAK, 1525, sk=0.2, n=8, inkw=1.4, hi=0.4))
    sau = along(bx - 60, 476, bx + 8, 470, lambda t: 11 if 0.04 < t < 0.96 else 7, 14)
    out.append(painted(D, sau, ("#C88A7A", "#8A3A32", "#4A1416"), 1526, sdir=(0, 1), sk=0.25, angle=-5, n=8, inkw=1.4, hi=0.3))
    out.append(specks(1527, (bx - 58, 464, bx + 6, 482), ["#FFFFFF", "#E8D8C8"], 24, (0.6, 1.2), (0.5, 0.9)))
    for k in range(4):
        sxx = bx + 22 + k * 13
        out.append(painted(D, ell_pts(sxx, 476 + (k % 2) * 2, 8.5, 5.4, 0, 360, 14), ("#E8A098", "#B85A50", "#6A2420"), 1528 + k, sk=0.15, n=2, inkw=1, hi=0.3))
        out.append(specks(1532 + k, (sxx - 6, 472, sxx + 6, 481), ["#FFFFFF"], 6, (0.6, 1.1), (0.7, 1)))
    out.append(carafe(D, 268, 470, 128, 1536))
    out.append(anise_glass(D, 346, 476, 86, 1537))
    out.append(anise_glass(D, 212, 488, 80, 1538))
    # lettering
    out.append(letters(D, 290, 100, "L’heure de", SERIF_IT, 62, "#7A2E14", ["#A8461E", "#5A1E0A", "#C8602E"], 1539, max_w=320,
                       shadow="#FFF0D0", soff=(0.02, 0.035), angle=-40, hi="#F2A870"))
    out.append(letters(D, 290, 204, "l’apéro", SERIF_IT, 120, "#7A2E14", ["#A8461E", "#5A1E0A", "#C8602E"], 1540, max_w=400,
                       shadow="#FFF0D0", soff=(0.02, 0.035), angle=-40, hi="#F2A870"))
    out.append(ruled(290, 252, "SOUS LES PLATANES", "#24503A", font=JOS, size=18, ls=5, line_w=28, gap=12, max_w=320))
    return finish_f(D, out, 1541)


# ================================================================ 16. la madeleine — the taste of memory
def toile_tile(c, ink_c="#B8566A", bg="#FBF0EC"):
    """A toile-de-Jouy-style tile: little engraved scenes in one colour — a tree, a cottage, a bird on a branch."""
    t = [f'<rect width="{c}" height="{c}" fill="{bg}"/>']
    g = f'stroke="{ink_c}" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.7"'
    # tree
    x, y = c * 0.25, c * 0.42
    t.append(f'<path d="M {x} {y + 22} L {x} {y}" {g}/>')
    for k in range(7):
        a = math.radians(k * 51)
        t.append(f'<circle cx="{x + math.cos(a) * 9:.1f}" cy="{y - 6 + math.sin(a) * 7:.1f}" r="6" {g}/>')
    t.append(f'<path d="M {x - 22} {y + 22} q 22 -6 44 0" {g}/>')
    # cottage
    x, y = c * 0.72, c * 0.82
    t.append(f'<path d="M {x - 12} {y} L {x - 12} {y - 12} L {x} {y - 22} L {x + 12} {y - 12} L {x + 12} {y} Z M {x - 3} {y} L {x - 3} {y - 7} L {x + 3} {y - 7} L {x + 3} {y}" {g}/>')
    t.append(f'<path d="M {x - 26} {y + 2} q 26 -5 52 0" {g}/>')
    # bird on a sprig
    x, y = c * 0.75, c * 0.22
    t.append(f'<path d="M {x - 16} {y + 8} q 16 -4 30 2 M {x} {y + 5} q -4 -10 -12 -12" {g}/>')
    t.append(f'<path d="M {x - 4} {y + 3} q 6 -12 16 -6 q -4 8 -16 6 Z M {x + 12} {y - 3} l 5 -1" {g}/>')
    t.append(f'<path d="M {c * 0.2} {c * 0.9} q 4 -6 8 0 q 4 -6 8 0" {g}/>')
    return "".join(t)


def madeleine(D, cx, cy, w, seed, side="shell", rot_=0):
    """A madeleine: shell side shows the fanned ridges, golden at the edges; 'hump' side shows the famous bosse."""
    h = w * 0.62
    pts = rot([(cx - w * 0.5, cy - h * 0.05), (cx - w * 0.42, cy - h * 0.38), (cx - w * 0.1, cy - h * 0.52), (cx + w * 0.3, cy - h * 0.42), (cx + w * 0.5, cy - h * 0.1),
               (cx + w * 0.4, cy + h * 0.28), (cx + w * 0.1, cy + h * 0.44), (cx - w * 0.3, cy + h * 0.36)], cx, cy, rot_)
    out = [cast(D, cx + 6, cy + h * 0.45, w * 0.55, h * 0.18, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#FFE2A0", "#E8A84A", "#9A5A1A"), seed, sdir=(0.4, 0.9), sk=0.22, angle=-30 + rot_, n=14, inkw=1.8, hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    hinge = rot([(cx + w * 0.5, cy + h * 0.02)], cx, cy, rot_)[0] if side == "shell" else None
    if side == "shell":
        for k in range(11):
            a = math.radians(150 + k * 6)
            tip = (hinge[0] + math.cos(a + math.radians(rot_)) * w * 1.05, hinge[1] + math.sin(a + math.radians(rot_)) * w * 0.9)
            inner.append(taper([hinge, ((hinge[0] + tip[0]) / 2, (hinge[1] + tip[1]) / 2), tip], 1, 6, "#9A5014", 0.7))
            inner.append(taper([(hinge[0], hinge[1] - 3), ((hinge[0] + tip[0]) / 2, (hinge[1] + tip[1]) / 2 - 4), (tip[0], tip[1] - 5)], 0.8, 3.2, "#FFF0C8", 0.75))
        inner.append(f'<path d="{smooth_closed(pts)}" fill="{D.rad([(0, "#FFE6A8", 0), (0.7, "#C87A2A", 0.1), (1, "#8A4A10", 0.55)])}"/>')
    else:
        inner.append(f'<path d="{blob(cx, cy - h * 0.05, w * 0.28, h * 0.22, seed + 1, 0.1, 12, rot_)}" fill="#FFF2C8" opacity="0.6"/>')
        inner.append(taper(rot([(cx - w * 0.25, cy - h * 0.05), (cx, cy - h * 0.12), (cx + w * 0.22, cy - h * 0.04)], cx, cy, rot_), 2, 3, "#B8701E", 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def linden_sprig(D, x, y, seed, ang=0):
    """A sprig of lime-tree blossom (tilleul): heart-shaped leaf, the pale bract and its little flower cluster."""
    out = [leaf_simple(D, x, y, 70, 26, ang - 40, ("#B8D890", "#7AA858", "#3E6A2A"), seed, inkw=1.2)]
    a = math.radians(ang + 20)
    bx, by = x + math.cos(a) * 60, y + math.sin(a) * 60
    out.append(leaf_simple(D, x, y, 66, 10, ang + 20, ("#F2F0C0", "#D8DC90", "#9AA050"), seed + 1, vein=True, inkw=1))
    for k in range(5):
        fx, fy = bx * 0.6 + x * 0.4 + math.cos(k * 1.3) * 12, by * 0.6 + y * 0.4 + 14 + math.sin(k * 1.3) * 8
        out.append(pline([(bx * 0.55 + x * 0.45, by * 0.55 + y * 0.45 + 4), (fx, fy)], "#A8A060", 1, seed + k, 0.8, 1))
        out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3.6" fill="#F6EEA8" stroke="#B8A850" stroke-width="0.8"/>')
    return "".join(out)


@design("la-madeleine")
def la_madeleine():
    D = Doc2("fr-md")
    pat = D.pattern(150, 150, toile_tile(150))
    out = [f'<rect width="600" height="600" fill="{pat}"/>']
    out.append(soft_glow(D, 300, 330, 320, "#FFF8F0", 0.55))
    # a little round lace-covered side table
    out.append(f'<path d="M -10 420 L 610 420 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#B07A58"), (1, "#7A4A30")])}"/>')
    out.append(wood_planks(D, 420, 610, 1601, ("#C89070", "#9A6244", "#5A3420"), 3))
    rnd = random.Random(1602)
    lace = [(40, 430), (300, 418), (560, 432), (570, 560), (300, 580), (30, 566)]
    ld = smooth_closed(poly_pts(lace, 24, 1603, 1))
    out.append(f'<path d="{ld}" fill="#FFFDF8"/>')
    lid = D.clip(f'<path d="{ld}"/>')
    holes = []
    for row in range(8):
        for i in range(18):
            x = 30 + i * 32 + (row % 2) * 16
            y = 440 + row * 18
            holes.append(f'<circle cx="{x}" cy="{y}" r="4.2" fill="none" stroke="#E8DCD0" stroke-width="1.6"/>')
            holes.append(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#E2D2C4"/>')
    holes.append(shade_over(D, ld, "#5A3A2A", 0.25, 0, 0, 0.3, 1, 0.5))
    out.append(f'<g {lid}>{"".join(holes)}</g>')
    out.append(ink(ld, "#C8B8A8", 1.4, 1604, 1, 0.7))
    # porcelain cup of tilleul, gold rim, little rose
    out.append(cup_saucer(D, 196, 486, 132, 1605, rim=("#F2D488", "#C8A048", "#7A5A20"), coffee="#D8B860"))
    out.append(f'<path d="{blob(196, 396, 10, 7, 1606, 0.2, 10)}" fill="#E88A9A" opacity="0.8"/>')
    out.append(steam(196, 384, 80, 1607, "#FFFFFF", 2, 28, 6, 0.65))
    # three madeleines on a small plate, one dipped
    px, py = 416, 506
    out.append(cast(D, px + 10, py + 12, 124, 18, strength=0.35, seed=1608))
    out.append(painted(D, ell_pts(px, py, 124, 30, 0, 360, 36), WHITE, 1609, sk=0.12, n=10, inkw=1.6, hi=0.4))
    out.append(pline(ell_pts(px, py, 110, 24, 15, 165, 14), "#C8A048", 2, 1610, 0.8, 1))
    out.append(madeleine(D, 364, 474, 116, 1611, "shell", rot_=-14))
    out.append(madeleine(D, 470, 466, 112, 1612, "hump", rot_=12))
    out.append(madeleine(D, 418, 502, 124, 1613, "shell", rot_=4))
    for _ in range(10):
        x, y = rnd.uniform(300, 520), rnd.uniform(500, 530)
        out.append(f'<path d="{blob(x, y, rnd.uniform(1, 2.4), rnd.uniform(0.8, 1.8), rnd.randint(1, 999), 0.3, 6)}" fill="#E8A84A"/>')
    out.append(linden_sprig(D, 82, 410, 1614, ang=-20))
    # lettering on an oval vignette
    out.append(f'<ellipse cx="300" cy="170" rx="250" ry="104" fill="#FFFAF6" opacity="0.88"/>')
    out.append(ink(smooth_closed(ell_pts(300, 170, 250, 104, 0, 360, 48)), "#B8566A", 1.8, 1615, 2, 0.6))
    out.append(ink(smooth_closed(ell_pts(300, 170, 240, 96, 0, 360, 48)), "#B8566A", 1, 1616, 1, 0.5))
    out.append(letters(D, 300, 180, "la madeleine", SERIF_IT, 92, "#8A3A2A", ["#B0563E", "#5A1E10", "#C8704E"], 1617, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#F2B8A0"))
    out.append(ruled(300, 222, "LE GOÛT DES SOUVENIRS", "#B8566A", font=JOS, size=17, ls=5, line_w=24, gap=10, max_w=360))
    return finish_f(D, out, 1618)


# ================================================================ 17. mon petit chou — the cream puff and the cabbage
def cream_puff(D, cx, base, w, seed):
    """A chou à la crème: a golden craquelin-cracked choux bun cut open, a generous swirl of whipped cream piped in
    tiers, the little cap perched on top at a jaunty angle, a snow of icing sugar."""
    rnd = random.Random(seed)
    CHX = ("#FFD898", "#E0963A", "#8A4A12")
    out = [cast(D, cx + 8, base + 4, w * 0.5, w * 0.07, strength=0.45, seed=seed)]
    bot = [(cx - w * 0.42, base - w * 0.2), (cx - w * 0.36, base - w * 0.05), (cx - w * 0.18, base + 2), (cx + w * 0.18, base + 2), (cx + w * 0.36, base - w * 0.05), (cx + w * 0.42, base - w * 0.2), (cx, base - w * 0.24)]
    out.append(painted(D, bot, CHX, seed, sdir=(0.4, 1), sk=0.2, n=14, inkw=1.8, hi=0.4))
    bid = D.clip(f'<path d="{smooth_closed(bot)}"/>')
    cr0 = []
    for _ in range(12):
        x, y = rnd.uniform(cx - w * 0.4, cx + w * 0.4), rnd.uniform(base - w * 0.18, base - w * 0.02)
        cr0.append(taper([(x, y), (x + rnd.uniform(-8, 8), y + rnd.uniform(-4, 4))], 2.2, 0.6, "#8A4A12", 0.5))
    out.append(f'<g {bid}>{"".join(cr0)}</g>')
    # whipped cream piped in three tiers of rosettes, the top tier smaller
    tiers = [(6, 0.42, 0.24, 0.1), (5, 0.36, 0.38, 0.095), (4, 0.28, 0.5, 0.085)]
    for ti, (n, half, yy, rr) in enumerate(tiers):
        for i in range(n):
            x = cx - w * half + i * (2 * w * half) / (n - 1)
            y = base - w * yy - (math.sin(math.pi * i / (n - 1)) * w * 0.03)
            r = w * rr
            out.append(painted(D, blob_pts(x, y, r, r * 0.92, seed + ti * 9 + i, 0.1, 12), ("#FFFFFF", "#FBF6EC", "#D8CCB8"), seed + ti * 9 + i, sdir=(0.4, 0.9), sk=0.22, n=4, inkw=1.1, inkop=0.45, hi=0.5))
            out.append(pline([(x - r * 0.65, y + r * 0.1), (x - r * 0.1, y - r * 0.45), (x + r * 0.55, y - r * 0.05), (x + r * 0.1, y + r * 0.3)], "#D0C4AE", 1.1, seed + i, 0.7, 1))
    # the cap, smaller than the base, set slightly askew
    ccx, ccy = cx + w * 0.04, base - w * 0.66
    cap = rot([(ccx - w * 0.3, ccy + w * 0.06), (ccx - w * 0.26, ccy - w * 0.08), (ccx - w * 0.06, ccy - w * 0.16), (ccx + w * 0.16, ccy - w * 0.14), (ccx + w * 0.3, ccy - w * 0.04), (ccx + w * 0.3, ccy + w * 0.07), (ccx, ccy + w * 0.1)], ccx, ccy, -10)
    out.append(painted(D, cap, CHX, seed + 30, sdir=(0.4, 1), sk=0.22, n=16, inkw=1.9, hi=0.5, hik=0.1))
    cid = D.clip(f'<path d="{smooth_closed(cap)}"/>')
    cr = []
    for _ in range(18):
        x, y = rnd.uniform(ccx - w * 0.28, ccx + w * 0.28), rnd.uniform(ccy - w * 0.16, ccy + w * 0.06)
        L = rnd.uniform(6, 14)
        a = rnd.uniform(0, 3.14)
        cr.append(taper([(x, y), (x + math.cos(a) * L * 0.5 + rnd.uniform(-2, 2), y + math.sin(a) * L * 0.5), (x + math.cos(a) * L, y + math.sin(a) * L)], 2.6, 0.6, "#8A4A12", 0.6))
        cr.append(taper([(x - 1, y - 1.5), (x + math.cos(a) * L - 1, y + math.sin(a) * L - 1.5)], 1.6, 0.4, "#FFF0C8", 0.7))
    for _ in range(120):
        x, y = rnd.uniform(ccx - w * 0.3, ccx + w * 0.3), rnd.uniform(ccy - w * 0.17, ccy - w * 0.02)
        cr.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    out.append(f'<g {cid}>{"".join(cr)}</g>')
    for _ in range(30):
        x, y = rnd.uniform(cx - w * 0.5, cx + w * 0.5), rnd.uniform(base - w * 0.02, base + 8)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def cabbage(D, cx, cy, r, seed):
    """A little green cabbage (savoy): crinkled outer leaves opening round a tight heart, pale veins."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 5, cy + r * 0.8, r * 1.1, r * 0.22, strength=0.4, seed=seed)]
    for k in range(7):
        a = -160 + k * 23
        lx, ly = cx + math.cos(math.radians(a)) * r * 0.55, cy + math.sin(math.radians(a)) * r * 0.45 + r * 0.1
        pts = rot(blob_pts(lx, ly, r * 0.62, r * 0.45, seed + k, 0.12, 14), lx, ly, a + 90)
        out.append(painted(D, pts, ("#C8E8A0", "#7AB05A", "#3A6A2A"), seed + k, sk=0.25, n=8, inkw=1.3, inkop=0.6, hi=0.35))
        out.append(pline([(cx, cy + r * 0.2), (lx, ly), (lx + math.cos(math.radians(a)) * r * 0.4, ly + math.sin(math.radians(a)) * r * 0.3)], "#F2F8D8", 1.4, seed + k, 0.6, 1))
    out.append(painted(D, blob_pts(cx, cy, r * 0.56, r * 0.5, seed + 20, 0.08, 14), ("#E8F6C8", "#A8D07A", "#5E8A3A"), seed + 20, sk=0.2, n=8, inkw=1.4, hi=0.45))
    for k in range(4):
        out.append(pline([(cx - r * 0.3 + k * r * 0.2, cy - r * 0.4), (cx - r * 0.2 + k * r * 0.16, cy), (cx - r * 0.3 + k * r * 0.2, cy + r * 0.35)], "#6E9A4A", 1.3, seed + 30 + k, 0.5, 1))
    return "".join(out)


@design("mon-petit-chou")
def mon_petit_chou():
    D = Doc2("fr-ch")
    out = [paper(D.nid(), "#FBE4E2", "#A85A5A", 1701)]
    out.append(blooms(1702, ["#F6C2C4", "#FFE8E4", "#F0B0B8"], 7, (0, 0, 600, 600), (100, 190), (0.1, 0.18)))
    rnd = random.Random(1703)
    for _ in range(22):
        x, y = rnd.uniform(30, 570), rnd.uniform(220, 560)
        if 150 < x < 450 and 280 < y < 520:
            continue
        out.append(p_heart(D, x, y, rnd.uniform(7, 12), ("#FFB8C4", "#F07A90", "#B04060"), rnd.randint(1, 999), rot_=rnd.uniform(-25, 25), inkw=0.9))
    # cake stand
    sx, sy = 280, 500
    out.append(cast(D, sx + 10, 572, 110, 12, strength=0.4, seed=1704))
    out.append(painted(D, [(sx - 30, 572), (sx - 14, 520), (sx + 14, 520), (sx + 30, 572)], WHITE, 1705, sdir=(1, 0.2), sk=0.2, n=4, inkw=1.6, hi=0.5))
    out.append(painted(D, ell_pts(sx, sy + 12, 150, 26, 0, 360, 40), WHITE, 1706, sk=0.12, n=12, inkw=1.8, hi=0.4))
    for i in range(30):
        a = math.radians(i * 12)
        out.append(f'<circle cx="{sx + math.cos(a) * 140:.1f}" cy="{sy + 16 + math.sin(a) * 23:.1f}" r="2.4" fill="#F07A90" opacity="0.7"/>')
    out.append(cream_puff(D, sx, sy + 4, 240, 1707))
    # a raspberry on top and a tiny heart pick
    rx_, ry_ = sx + 14, sy - 186
    out.append(painted(D, blob_pts(rx_, ry_, 15, 14, 1708, 0.05, 12), ("#FF8AA0", "#D8284A", "#7A0A22"), 1708, sk=0.2, n=4, inkw=1.2, hi=0.4))
    for k in range(10):
        a = math.radians(k * 36)
        out.append(f'<circle cx="{rx_ + math.cos(a) * 8:.1f}" cy="{ry_ + math.sin(a) * 7:.1f}" r="3.2" fill="#E8405A" stroke="#8A1A2E" stroke-width="0.6"/>')
    out.append(f'<path d="M {rx_ - 2} {ry_ - 13} q 6 -8 12 -6" stroke="#4A8A3A" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    # the other chou: a little green cabbage, a wink
    out.append(cabbage(D, 474, 524, 62, 1709))
    out.append(p_heart(D, 474, 438, 13, ("#FFB8C4", "#F07A90", "#B04060"), 1710, inkw=1))
    # lettering
    out.append(letters(D, 300, 132, "mon petit chou", SERIF_IT, 92, "#B03050", ["#D8506E", "#7A1030", "#F07A90"], 1711, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC8D4"))
    out.append(ruled(300, 178, "JE T’AIME GROS COMME ÇA", "#5A8A3E", font=JOS, size=19, ls=4, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 1712, "#6A2A3A")


# ================================================================ 18. Oh là là ! — in front of the pâtisserie window
def eclair(D, x, y, L, seed, icing=CHOC):
    """An éclair from the side: long golden choux with a glossy fondant icing on top."""
    body = along(x, y, x + L, y, lambda t: 9 if 0.08 < t < 0.92 else 7, 16)
    out = [cast(D, x + L / 2 + 4, y + 11, L * 0.55, 4, strength=0.35, seed=seed)]
    out.append(painted(D, [(px, py + 3) for px, py in body], ("#FFD898", "#E0963A", "#8A4A12"), seed, sdir=(0, 1), sk=0.25, angle=0, n=6, inkw=1.4, hi=0.3))
    ic = along(x + 2, y - 3, x + L - 2, y - 3, lambda t: 6 if 0.06 < t < 0.94 else 4, 16)
    out.append(painted(D, ic, icing, seed + 1, sdir=(0, 1), sk=0.2, angle=0, n=4, inkw=1.2, hi=0.5, hik=0.2))
    out.append(taper([(x + L * 0.15, y - 6), (x + L * 0.75, y - 7)], 1.4, 2.4, "#FFFFFF", 0.7))
    return "".join(out)


def tart(D, cx, cy, r, seed, kind="fraise"):
    """A round tart seen at 3/4: fluted pastry shell, filled — strawberries in rows, or lemon with torched meringue peaks."""
    rnd = random.Random(seed)
    k = 0.42
    out = [cast(D, cx + 6, cy + r * k + 8, r * 1.05, r * 0.2, strength=0.4, seed=seed)]
    side = [(cx + r * math.cos(math.radians(a)) * (1 + 0.025 * math.cos(math.radians(a) * 24)), cy + r * k * math.sin(math.radians(a)) + 12) for a in range(0, 181, 5)] + \
           [(cx + r * math.cos(math.radians(a)), cy + r * k * math.sin(math.radians(a))) for a in range(180, -1, -5)]
    out.append(painted(D, side, ("#FFE2A0", "#E0A04A", "#8A5418"), seed, sdir=(0, 1), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.35))
    for a in range(10, 180, 15):
        x = cx + r * math.cos(math.radians(a))
        out.append(pline([(x, cy + r * k * math.sin(math.radians(a))), (x, cy + r * k * math.sin(math.radians(a)) + 11)], "#A86A2A", 1.1, a, 0.6, 1))
    out.append(painted(D, ell_pts(cx, cy, r, r * k, 0, 360, 30), ("#FFE2A0", "#E0A04A", "#8A5418"), seed + 1, sk=0.1, n=6, inkw=1.4, hi=0.4))
    if kind == "fraise":
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r - 5, r * k - 3, 0, 360, 30))}" fill="#FFF0D0"/>')
        for row in range(3):
            for i in range(5 - row):
                x = cx - r * 0.62 + (i + row * 0.5) * r * 0.31
                y = cy + r * k * 0.35 - row * r * k * 0.42
                out.append(painted(D, [(x - 7, y - 4), (x, y - 10), (x + 7, y - 4), (x + 5, y + 5), (x, y + 8), (x - 5, y + 5)], ("#FF8A8A", "#E02A3A", "#7A0A16"), seed + row * 9 + i, sk=0.2, n=3, inkw=1, hi=0.5))
                out.append(specks(seed + i, (x - 5, y - 6, x + 5, y + 5), ["#FFE680"], 4, (0.5, 0.9), (0.8, 1)))
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r - 5, r * k - 3, 0, 360, 30))}" fill="#FFFFFF" opacity="0.12"/>')
    else:
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r - 5, r * k - 3, 0, 360, 30))}" fill="#FFE460"/>')
        for i in range(9):
            a = rnd.uniform(0, 6.28)
            rr = rnd.uniform(0, 0.7)
            x, y = cx + math.cos(a) * r * rr, cy + math.sin(a) * r * k * rr
            pk = [(x - 9, y + 4), (x - 4, y - 8), (x, y - 16), (x + 3, y - 8), (x + 9, y + 4)]
            out.append(painted(D, pk, ("#FFFFFF", "#F6EEDC", "#C8A070"), seed + 40 + i, sk=0.2, n=3, inkw=1, hi=0.5))
            out.append(f'<path d="{blob(x + 1, y - 13, 3, 3.4, seed + i, 0.2, 6)}" fill="#C8782A" opacity="0.8"/>')
    return "".join(out)


def religieuse(D, cx, base, s, seed, icing=("#C8A0E0", "#9A6AC0", "#5A2A80")):
    """A religieuse: big choux below, small choux on top, glossy fondant, a ruff of buttercream at the neck."""
    out = [cast(D, cx + 4, base + 2, s * 0.6, s * 0.08, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, base - s * 0.28, s * 0.5, s * 0.3, seed, 0.04, 16), ("#FFD898", "#E0963A", "#8A4A12"), seed, sk=0.2, n=6, inkw=1.4, hi=0.3))
    out.append(painted(D, [(cx - s * 0.48, base - s * 0.34), (cx - s * 0.3, base - s * 0.56), (cx + s * 0.3, base - s * 0.56), (cx + s * 0.48, base - s * 0.34), (cx + s * 0.2, base - s * 0.4), (cx, base - s * 0.32), (cx - s * 0.2, base - s * 0.4)], icing, seed + 1, sk=0.2, n=4, inkw=1.2, hi=0.55, hik=0.15))
    out.append(painted(D, blob_pts(cx, base - s * 0.78, s * 0.28, s * 0.2, seed + 2, 0.04, 14), ("#FFD898", "#E0963A", "#8A4A12"), seed + 2, sk=0.2, n=4, inkw=1.3, hi=0.3))
    out.append(painted(D, blob_pts(cx, base - s * 0.86, s * 0.26, s * 0.12, seed + 3, 0.05, 14), icing, seed + 3, sk=0.2, n=3, inkw=1.1, hi=0.55, hik=0.15))
    for k in range(7):
        x = cx - s * 0.24 + k * s * 0.08
        out.append(f'<path d="{blob(x, base - s * 0.6, s * 0.05, s * 0.07, seed + k, 0.15, 8)}" fill="#FFFDF0" stroke="#D8CCB4" stroke-width="0.8"/>')
    out.append(f'<path d="{blob(cx, base - s * 0.97, s * 0.05, s * 0.04, seed + 9, 0.15, 8)}" fill="#FFFDF0"/>')
    return "".join(out)


def mille_feuille(D, x, base, w, seed):
    """A mille-feuille slice: three flaky pastry layers, two layers of cream, white fondant with chocolate feathering."""
    h = w * 0.62
    out = [cast(D, x + w / 2 + 4, base + 2, w * 0.6, 5, strength=0.35, seed=seed)]
    layers = [(0, 0.16, "pastry"), (0.16, 0.38, "cream"), (0.38, 0.52, "pastry"), (0.52, 0.76, "cream"), (0.76, 0.9, "pastry"), (0.9, 1.0, "icing")]
    for k, (a, b, kind) in enumerate(layers):
        y0, y1 = base - h * b, base - h * a
        pal = {"pastry": ("#FFD898", "#D88A34", "#7A4010"), "cream": ("#FFFBEA", "#F6E8BE", "#C8B07A"), "icing": ("#FFFFFF", "#F8F4EC", "#C8C0B4")}[kind]
        out.append(painted(D, rect_pts(x, y0, x + w, y1, 8, seed + k, 0.5), pal, seed + k, sk=0.2, angle=0, n=4, inkw=1.1, inkop=0.6, hi=0.3))
        if kind == "pastry":
            for j in range(3):
                out.append(pline([(x + 2, y0 + (y1 - y0) * (0.3 + j * 0.2)), (x + w - 2, y0 + (y1 - y0) * (0.3 + j * 0.2))], "#A85A1A", 0.9, seed + j, 0.6, 1))
    for j in range(4):
        out.append(pline([(x + 4 + j * w * 0.24, base - h + 1), (x + 10 + j * w * 0.24, base - h * 0.92)], "#4A2614", 1.6, seed + j, 0.8, 1))
    return "".join(out)


@design("oh-la-la")
def oh_la_la():
    D = Doc2("fr-ol")
    # the shop front: deep blue painted wood fascia with gilt edging (the sign carries the words)
    out = [f'<rect width="600" height="600" fill="#1E3A6A"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#2E4E8A", "#122648"], 1801, n=120, angle=-88, length=(40, 120), width=(3, 8), opacity=(0.1, 0.25)))
    out.append(f'<path d="{hg.org_rect(36, 40, 528, 172, 1802, 0.6, 20, 6)}" fill="none" stroke="#E8C060" stroke-width="3"/>')
    out.append(f'<path d="{hg.org_rect(46, 50, 508, 152, 1803, 0.6, 20, 4)}" fill="none" stroke="#E8C060" stroke-width="1.4" opacity="0.7"/>')
    # the window: glass with warm interior light, shelves of pastries
    wx0, wy0, wx1, wy1 = 46, 234, 554, 560
    win = rect_pts(wx0, wy0, wx1, wy1, 30, 1804, 0.4)
    wd = smooth_closed(win)
    out.append(f'<path d="{wd}" fill="{D.lin([(0, "#FFF4DC"), (1, "#F6DCB4")])}"/>')
    wid = D.clip(f'<path d="{wd}"/>')
    inside = [soft_glow(D, 300, 300, 300, "#FFFFFF", 0.6)]
    # mirrored back wall and two marble shelves
    for y in (382, 512):
        inside.append(painted(D, rect_pts(wx0 - 10, y, wx1 + 10, y + 14, 30, 1805 + y, 0.3), ("#FFFFFF", "#ECE6DC", "#B8AE9E"), 1805 + y, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.2, hi=0.5))
        inside.append(f'<rect x="{wx0 - 10}" y="{y + 14}" width="{wx1 - wx0 + 20}" height="12" fill="#3A2A1A" opacity="0.18"/>')
    # top shelf: tarts and religieuses
    inside.append(tart(D, 136, 350, 70, 1806, "fraise"))
    inside.append(religieuse(D, 252, 382, 92, 1807))
    inside.append(religieuse(D, 334, 382, 80, 1808, icing=("#A8785A", "#6A3E26", "#341A0C")))
    inside.append(tart(D, 462, 352, 70, 1809, "citron"))
    # bottom shelf: éclairs in a row, mille-feuilles, a paris-brest
    for k in range(3):
        inside.append(eclair(D, 68 + k * 5, 462 + k * 16, 128, 1810 + k, icing=[CHOC, ("#E8C8A0", "#B88A5A", "#6A4420"), PINK][k]))
    inside.append(mille_feuille(D, 222, 512, 72, 1813))
    inside.append(mille_feuille(D, 302, 512, 72, 1814))
    pbx, pby = 462, 482
    ring = ell_pts(pbx, pby, 64, 24, 0, 360, 30)
    inside.append(cast(D, pbx + 4, pby + 28, 66, 6, strength=0.35, seed=1815))
    inside.append(painted(D, [(x, y + 10) for x, y in ring], ("#FFD898", "#E0963A", "#8A4A12"), 1815, sk=0.2, n=8, inkw=1.4, hi=0.3))
    for k in range(10):
        a = math.radians(k * 36)
        inside.append(painted(D, blob_pts(pbx + math.cos(a) * 44, pby + math.sin(a) * 14, 12, 9, 1816 + k, 0.1, 10), ("#F6E0C0", "#D8B080", "#8A6A40"), 1816 + k, sk=0.2, n=2, inkw=0.8, hi=0.4))
    inside.append(painted(D, ell_pts(pbx, pby - 6, 62, 20, 0, 360, 30), ("#FFD898", "#E0963A", "#8A4A12"), 1830, sk=0.2, n=8, inkw=1.4, hi=0.4))
    inside.append(f'<path d="{smooth_closed(ell_pts(pbx, pby - 8, 28, 8, 0, 360, 20))}" fill="#7A4A22"/>')
    inside.append(specks(1831, (pbx - 58, pby - 22, pbx + 58, pby + 8), ["#FFFFFF", "#F2E2C8", "#C8A070"], 60, (0.8, 2), (0.6, 1)))
    # doilies and reflections on the glass
    for k in range(5):
        x = 60 + k * 120
        inside.append(taper([(x, wy1 + 10), (x + 120, wy0 - 10)], 22, 30, "#FFFFFF", 0.12))
    inside.append(taper([(wx0 + 20, wy1 - 40), (wx0 + 120, wy0 + 20)], 6, 10, "#FFFFFF", 0.3))
    out.append(f'<g {wid}>{"".join(inside)}</g>')
    out.append(ink(wd, "#0E1E3A", 3, 1832, 2, 0.8))
    # gilt arched word painted on the glass, and the brass window rail
    out.append(label(300, 278, "PÂTISSERIE", CINZEL, 24, "#C8A040", ls=8, max_w=320))
    out.append(taper([(wx0, wy1 - 2), (wx1, wy1 - 2)], 8, 8, "#C8A048"))
    out.append(taper([(wx0, wy1 - 4), (wx1, wy1 - 4)], 2, 2, "#FFF0B0", 0.8))
    out.append(f'<rect x="-10" y="{wy1 + 4}" width="620" height="60" fill="#14284C"/>')
    # lettering on the fascia
    out.append(letters(D, 300, 162, f"Oh là là{NB}!", SERIF_IT, 120, "#F6D488", ["#FFF0B0", "#E8B830", "#FFE07A"], 1833, max_w=440,
                       shadow="#0A1430", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    for x in (78, 522):
        out.append(sparkle(x, 128, 9, "#F6D488", 0.9))
    return finish_f(D, out, 1834, "#0A1430")


# ================================================================ 19. Bonjour ! — the boulangerie at seven in the morning
def standing_baguettes(D, x0, x1, base, seed, n=9):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n + rnd.uniform(-3, 3)
        h = rnd.uniform(90, 120)
        lean = rnd.uniform(-8, 8)
        pts = rot(along(x, base, x, base - h, lambda t: 8 * (0.35 + 0.65 * math.sin(min(t, 1 - t) / 0.12 * math.pi / 2) ** 0.7) if min(t, 1 - t) < 0.12 else 8, 16), x, base, lean)
        out.append(painted(D, pts, CRUST, seed + k, sdir=(1, 0), sk=0.25, angle=-90 + lean, n=6, inkw=1.2, hi=0.4))
        for j in range(3):
            c = rot([(x, base - h * (0.3 + j * 0.2))], x, base, lean)[0]
            out.append(f'<path d="{blob(c[0], c[1], 3, 7, seed + k * 5 + j, 0.1, 8, lean - 20)}" fill="#F6D8A0"/>')
    return "".join(out)


def round_loaf(D, cx, cy, r, seed, flour=True):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.66, seed, 0.05, 16), ("#E8B06A", "#B8702E", "#6A3410"), seed, sdir=(0.3, 1), sk=0.25, n=10, inkw=1.4, hi=0.35)]
    out.append(taper([(cx - r * 0.6, cy - r * 0.1), (cx, cy - r * 0.3), (cx + r * 0.6, cy - r * 0.1)], 3, 3, "#6A3410", 0.6))
    out.append(taper([(cx - r * 0.55, cy - r * 0.15), (cx, cy - r * 0.35), (cx + r * 0.55, cy - r * 0.15)], 2, 2, "#FFE6B0", 0.7))
    if flour:
        out.append(specks(seed + 1, (cx - r * 0.7, cy - r * 0.5, cx + r * 0.7, cy), ["#FFFBF0"], int(r * 0.8), (0.6, 1.4), (0.5, 0.9)))
    return "".join(out)


@design("bonjour")
def bonjour():
    D = Doc2("fr-bj")
    # upper façade: pale stone in early light, courses and a cornice
    out = [sky(D, [(0, "#F4E6D0"), (1, "#E8D2B0")], 1901, 600, ["#FFF6E6", "#D8BC94"], 60, angle=-3, sop=(0.05, 0.12))]
    for k in range(9):
        y = 20 + k * 26
        out.append(pline([(-10, y), (300, y + 1), (610, y)], "#C8AE88", 1.4, 1902 + k, 0.5, 1))
    out.append(soft_glow(D, 120, 40, 260, "#FFE8C8", 0.5))
    # shopfront in boulangerie red, gilt fascia
    sf = "M -10 226 L 610 226 L 610 560 L -10 560 Z"
    out.append(f'<path d="{sf}" fill="#8A2028"/>')
    out.append(strokes(D.nid(), sf, (-40, 226, 610, 560), ["#A83038", "#5A0E14"], 1903, n=90, angle=-88, length=(30, 90), width=(2, 6), opacity=(0.15, 0.3)))
    out.append(painted(D, rect_pts(-10, 226, 610, 286, 30, 1904, 0.4), ("#B83A40", "#8A2028", "#4A0A10"), 1904, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=2, hi=0.3))
    out.append(f'<path d="{hg.org_rect(30, 234, 540, 44, 1905, 0.4, 20, 3)}" fill="none" stroke="#E8C060" stroke-width="2"/>')
    out.append(label(300, 268, "BOULANGERIE", CINZEL, 30, "#F2D488", ls=10, max_w=440))
    # the big window, lit from inside
    wx0, wy0, wx1, wy1 = 40, 300, 382, 530
    wd = smooth_closed(rect_pts(wx0, wy0, wx1, wy1, 24, 1906, 0.4))
    out.append(f'<path d="{wd}" fill="{D.lin([(0, "#FFE6A8"), (1, "#F2B860")])}"/>')
    wid = D.clip(f'<path d="{wd}"/>')
    inside = [soft_glow(D, 210, 380, 220, "#FFFFFF", 0.6)]
    inside.append(painted(D, rect_pts(wx0 - 10, 360, wx1 + 10, 370, 20, 1907, 0.3), WOOD, 1907, sk=0.2, angle=0, n=6, inkw=1, hi=0.4))
    # wicker baskets of standing baguettes, round loaves on the shelf, croissants on a tray in front
    for k, (x0, x1) in enumerate(((52, 150), (160, 270))):
        inside.append(standing_baguettes(D, x0 + 6, x1 - 6, 470, 1908 + k * 20, 6))
        inside.append(painted(D, rect_pts(x0, 440, x1, 490, 12, 1909 + k, 0.5), ("#E8B870", "#B8823E", "#6A4418"), 1909 + k, sdir=(1, 0.3), sk=0.2, angle=0, n=14, inkw=1.4, hi=0.4))
        for j in range(4):
            inside.append(pline([(x0 + 2, 448 + j * 11), (x1 - 2, 448 + j * 11)], "#7A4A1A", 1.2, 1910 + j, 0.5, 1))
    for k, x in enumerate((300, 346)):
        inside.append(round_loaf(D, x, 350, 24, 1912 + k))
    inside.append(round_loaf(D, 322, 336, 22, 1914))
    inside.append(painted(D, rect_pts(276, 482, 378, 496, 10, 1915, 0.3), ZINC, 1915, sk=0.2, angle=0, n=4, inkw=1.2, hi=0.5))
    for k in range(3):
        inside.append(croissant(D, 296 + k * 30, 478 - (k % 2) * 4, 40, 1916 + k, rot_=-6 + k * 5))
    for k in range(4):
        inside.append(taper([(wx0 + k * 100 - 20, wy1 + 10), (wx0 + k * 100 + 60, wy0 - 10)], 16, 24, "#FFFFFF", 0.13))
    out.append(f'<g {wid}>{"".join(inside)}</g>')
    out.append(ink(wd, "#2A0608", 3, 1920, 2, 0.8))
    out.append(taper([(wx0, wy1), (wx1, wy1)], 8, 8, "#E8C060"))
    # the door, its glass glowing, a little brass bell
    dx0, dx1 = 404, 556
    out.append(painted(D, rect_pts(dx0, 300, dx1, 560, 20, 1921, 0.4), ("#B83A40", "#8A2028", "#4A0A10"), 1921, sdir=(1, 0.2), sk=0.15, angle=-90, n=20, inkw=2, hi=0.3))
    gd = smooth_closed(rect_pts(dx0 + 18, 318, dx1 - 18, 456, 16, 1922, 0.3))
    out.append(f'<path d="{gd}" fill="{D.lin([(0, "#FFE6A8"), (1, "#F2B860")])}"/>')
    out.append(f'<path d="{hg.org_rect(dx0 + 18, 468, dx1 - dx0 - 36, 72, 1923, 0.4, 12, 2)}" fill="none" stroke="#5A0E14" stroke-width="2.4"/>')
    out.append(ink(gd, "#2A0608", 2, 1924, 1, 0.8))
    out.append(label((dx0 + dx1) / 2, 396, "OUVERT", JOS, 20, ROUGE[2], ls=4, max_w=100))
    out.append(painted(D, rect_pts(dx1 - 34, 470, dx1 - 26, 506, 6, 1925, 0.2), ("#FFF0A0", "#C8A048", "#7A5A10"), 1925, sk=0.2, n=2, inkw=1, hi=0.5))
    out.append(painted(D, [(dx0 + 4, 318), (dx0 + 12, 306), (dx0 + 20, 318)], ("#FFF0A0", "#C8A048", "#7A5A10"), 1926, sk=0.2, n=2, inkw=1, hi=0.5))
    # pavement, warm light spilling out
    out.append(f'<rect x="-10" y="556" width="620" height="60" fill="#8A8A90"/>')
    out.append(f'<path d="{smooth_closed([(40, 560), (382, 560), (430, 610), (0, 610)])}" fill="#FFD890" opacity="0.35"/>')
    for k in range(9):
        out.append(pline([(k * 70 - 10, 562), (k * 70 + 10, 600)], "#6A6A72", 1.4, 1927 + k, 0.5, 1))
    # the sandwich-board ardoise on the pavement, left
    ax, ay = 96, 528
    out.append('<g transform="translate(96 528) scale(0.82) translate(-96 -528)">')
    out.append(pline([(ax - 36, 588), (ax - 26, ay)], "#7A4A28", 4, 1928, 1, 1) + pline([(ax + 36, 588), (ax + 26, ay)], "#7A4A28", 4, 1929, 1, 1))
    out.append(painted(D, [(ax - 40, ay - 64), (ax + 40, ay - 64), (ax + 46, ay + 54), (ax - 46, ay + 54)], WOOD, 1930, sk=0.15, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{hg.org_poly([(ax - 33, ay - 57), (ax + 33, ay - 57), (ax + 38, ay + 47), (ax - 38, ay + 47)], 1931, 0.4, 10, 2)}" fill="#2A302E"/>')
    out.append(chalk_text(ax, ay - 30, "Pain", SERIF_IT, 22, "#F6E6B8", max_w=70))
    out.append(chalk_text(ax, ay - 6, "chaud", SERIF_IT, 22, "#F6E6B8", max_w=70))
    out.append(chalk_text(ax, ay + 28, "7 h", JOST, 20, max_w=60))
    out.append("</g>")
    # lettering, on the stone above the shop
    out.append(letters(D, 300, 152, f"Bonjour{NB}!", SERIF_IT, 132, "#8A2028", ["#B83A40", "#5A0E14", "#D8504E"], 1932, max_w=440,
                       shadow="#FFF6E6", soff=(0.02, 0.035), angle=-40, hi="#F2A0A0"))
    out.append(ruled(300, 200, "LE PAIN EST ENCORE CHAUD", BLEU[2], font=JOS, size=18, ls=5, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 1933)


# ================================================================ 20. C'est la vie — the bike, a basket of sunflowers
def wheel(D, cx, cy, r, seed, tire="#2A2A2E", rim="#C8CCD4"):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{tire}" stroke-width="{r * 0.1:.1f}"/>']
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.9:.1f}" fill="none" stroke="{rim}" stroke-width="3"/>')
    for k in range(18):
        a = math.radians(k * 20)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * r * 0.88:.1f} {cy + math.sin(a) * r * 0.88:.1f}" stroke="#9AA0AA" stroke-width="1.5" opacity="0.9"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.1:.1f}" fill="#8A909A" stroke="#4A4E56" stroke-width="1.4"/>')
    out.append(taper(ell_pts(cx, cy, r * 0.96, r * 0.96, 200, 260, 8), 1.5, 2.5, "#FFFFFF", 0.6))
    return "".join(out)


def sunflower(D, cx, cy, r, seed, rot_=0, face=1.0):
    """A sunflower head: pointed golden petals in two rings, a dark seed disc with a spiral of dots."""
    rnd = random.Random(seed)
    out = []
    for ring, (n, L, cols) in enumerate(((18, 1.0, ("#F6B81C", "#E8941A")), (16, 0.85, ("#FFD84A", "#F6C21C")))):
        for k in range(n):
            a = math.radians(k * 360 / n + ring * 10 + rot_)
            bx, by = cx + math.cos(a) * r * 0.48, cy + math.sin(a) * r * 0.48 * face
            tx, ty = cx + math.cos(a) * r * (0.48 + L * 0.62), cy + math.sin(a) * r * (0.48 + L * 0.62) * face
            nx, ny = -math.sin(a) * r * 0.13, math.cos(a) * r * 0.13 * face
            pts = [(bx + nx, by + ny), ((bx + tx) / 2 + nx * 1.1, (by + ty) / 2 + ny * 1.1), (tx, ty), ((bx + tx) / 2 - nx * 1.1, (by + ty) / 2 - ny * 1.1), (bx - nx, by - ny)]
            out.append(f'<path d="{smooth_closed(pts)}" fill="{cols[k % 2]}" stroke="#A8601A" stroke-width="0.8" stroke-opacity="0.6"/>')
            out.append(pline([(bx, by), ((bx + tx) / 2, (by + ty) / 2)], "#FFF0A0", 1, seed + k, 0.5, 1))
    disc = ell_pts(cx, cy, r * 0.52, r * 0.52 * face, 0, 360, 24)[:-1]
    out.append(painted(D, disc, ("#8A5A2A", "#4A2810", "#1E0E04"), seed, sk=0.2, n=6, inkw=1.4, hi=0.3))
    for i in range(int(r * 2.2)):
        a = i * 2.39996
        rr = math.sqrt(i / (r * 2.2)) * r * 0.48
        out.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr * face:.1f}" r="{max(0.8, r * 0.035):.1f}" fill="{"#C8862E" if rr < r * 0.25 else "#2A1406"}" opacity="0.85"/>')
    return "".join(out)


@design("c-est-la-vie")
def c_est_la_vie():
    D = Doc2("fr-cv")
    # sunny ochre village wall, afternoon light from the right
    out = [sky(D, [(0, "#F6D8A0"), (1, "#EEC488")], 2001, 600, ["#FFF0C8", "#D8A060"], 90, angle=-80, sop=(0.05, 0.14))]
    out.append(blooms(2002, ["#E8B070", "#FFE8B8", "#D89858"], 8, (0, 0, 600, 520), (90, 170), (0.06, 0.12)))
    rnd = random.Random(2003)
    for _ in range(20):
        x, y = rnd.uniform(0, 600), rnd.uniform(220, 500)
        out.append(f'<path d="{blob(x, y, rnd.uniform(16, 34), rnd.uniform(10, 18), rnd.randint(1, 999), 0.2, 10)}" fill="#C8904A" opacity="0.12"/>')
    # cobbled lane
    out.append(f'<rect x="-10" y="526" width="620" height="110" fill="#B8A488"/>')
    for row in range(4):
        y = 530 + row * 18
        x = -rnd.uniform(0, 20)
        while x < 610:
            w = rnd.uniform(24, 34)
            out.append(f'<path d="{blob(x + w / 2, y + 8, w / 2 - 1.5, 7, rnd.randint(1, 9999), 0.12, 10)}" fill="{rnd.choice(["#C8B898", "#A89878", "#D8C8A8"])}"/>')
            x += w
    out.append(f'<rect x="-10" y="520" width="620" height="10" fill="#7A5A3A" opacity="0.35"/>')
    # the bike's long afternoon shadow on the wall
    shadow = '<g opacity="0.16" transform="translate(-50 -20) skewX(-18)">' + f'<circle cx="190" cy="440" r="64" fill="none" stroke="#3A2010" stroke-width="10"/><circle cx="430" cy="440" r="64" fill="none" stroke="#3A2010" stroke-width="10"/><path d="M 190 440 L 290 440 L 400 330 M 290 440 L 250 330 L 400 330 M 430 440 L 400 330 L 390 300" stroke="#3A2010" stroke-width="10" fill="none"/>' + '</g>'
    out.append(shadow)
    # a pot of lavender by the wall, right
    px = 512
    out.append(painted(D, [(px - 34, 460), (px + 34, 460), (px + 26, 526), (px - 26, 526)], ("#F2A27A", "#C8643C", "#7A3218"), 2004, sdir=(1, 0.2), sk=0.2, n=8, inkw=1.6, hi=0.4))
    for k in range(16):
        a = math.radians(-90 + (k - 7.5) * 6)
        L = rnd.uniform(60, 90)
        x1, y1 = px + math.cos(a) * L, 460 + math.sin(a) * L
        out.append(pline([(px + (k - 7.5) * 2, 460), (x1, y1)], "#6E8A5A", 1.6, 2005 + k, 0.9, 1))
        for j in range(5):
            t = 0.7 + j * 0.07
            out.append(f'<path d="{blob(px + (x1 - px) * t, 460 + (y1 - 460) * t, 3, 4.4, 2006 + k * 5 + j, 0.15, 6)}" fill="{rnd.choice(["#8A6CC8", "#6A4AA8", "#A890D8"])}"/>')
    # the bicycle (step-through town bike), leaning on its stand, basket of sunflowers in front
    cream = ("#F2F0E0", "#C8D8C4", "#6A8A7A")
    rx_, fx_, wy = 190, 430, 462
    R = 62
    out.append(cast(D, 310, 526, 200, 8, strength=0.45, seed=2007))
    out.append(wheel(D, rx_, wy, R, 2008))
    out.append(wheel(D, fx_, wy, R, 2009))
    # mudguards
    out.append(ink(smooth_open(ell_pts(rx_, wy, R + 6, R + 6, 180, 330, 16)), cream[1], 6, 2010, 1, 1))
    out.append(ink(smooth_open(ell_pts(fx_, wy, R + 6, R + 6, 200, 340, 16)), cream[1], 6, 2011, 1, 1))
    # frame tubes
    bb = (290, 466)
    seat_top = (258, 354)
    head = (398, 358)
    for a, b, w_ in ((bb, seat_top, 9), (bb, (rx_, wy), 7), (seat_top, (rx_, wy), 6), ((head[0] + 4, head[1] + 20), (fx_, wy), 7)):
        out.append(taper([a, b], w_, w_, cream[2]))
        out.append(taper([a, b], w_ - 3, w_ - 3, cream[1]))
        out.append(taper([(a[0] - 1, a[1] - 1), (b[0] - 1, b[1] - 1)], 1.6, 1.6, "#FFFFFF", 0.6))
    step = catmull([bb, (320, 442), (360, 402), head], 6)
    out.append(taper(step, 10, 9, cream[2]))
    out.append(taper(step, 7, 6, cream[1]))
    out.append(taper([(x - 1, y - 1.5) for x, y in step], 1.6, 1.6, "#FFFFFF", 0.6))
    out.append(taper([head, (head[0] + 4, head[1] + 24)], 11, 11, cream[2]))
    # chain ring and pedal
    out.append(f'<circle cx="{bb[0]}" cy="{bb[1]}" r="14" fill="none" stroke="#5A5E66" stroke-width="3"/>')
    out.append(pline([(bb[0] + 14, bb[1] - 2), (rx_ + 8, wy - 4)], "#4A4E56", 2, 2012, 0.9, 1) + pline([(bb[0] + 12, bb[1] + 8), (rx_ + 6, wy + 6)], "#4A4E56", 2, 2013, 0.9, 1))
    out.append(taper([bb, (bb[0] + 12, bb[1] + 22)], 5, 5, "#4A4E56") + painted(D, rect_pts(bb[0] + 4, bb[1] + 22, bb[0] + 24, bb[1] + 28, 6, 2014, 0.2), ("#5A5E66", "#2A2E36", "#0A0E14"), 2014, sk=0.2, n=2, inkw=1, hi=0.3))
    # saddle and handlebar
    out.append(taper([seat_top, (seat_top[0] - 4, seat_top[1] - 16)], 5, 5, "#8A909A"))
    out.append(painted(D, [(seat_top[0] - 30, seat_top[1] - 22), (seat_top[0] + 14, seat_top[1] - 26), (seat_top[0] + 22, seat_top[1] - 18), (seat_top[0] - 6, seat_top[1] - 12), (seat_top[0] - 28, seat_top[1] - 12)], ("#B07A4A", "#7A4A28", "#3E220E"), 2015, sk=0.25, n=4, inkw=1.4, hi=0.4))
    out.append(taper([(head[0] - 2, head[1]), (head[0] - 6, head[1] - 26)], 5, 5, "#8A909A"))
    bar = catmull([(head[0] - 40, head[1] - 34), (head[0] - 10, head[1] - 26), (head[0] + 10, head[1] - 30)], 5)
    out.append(taper(bar, 5, 5, "#8A909A"))
    out.append(taper([(head[0] - 52, head[1] - 36), (head[0] - 36, head[1] - 34)], 8, 8, "#7A4A28"))
    out.append(f'<circle cx="{head[0] - 20}" cy="{head[1] - 30}" r="5" fill="#E8C060" stroke="#8A6A10" stroke-width="1"/>')
    # basket on the front rack, full of sunflowers
    bx, btop = 448, 326
    stems = [(-48, -96, 38, 0.95), (-4, -112, 40, 0.9), (40, -90, 36, 0.92), (-30, -58, 32, 0.85), (28, -50, 30, 0.9)]
    for k, (dx, dy, r, f) in enumerate(stems):
        out.append(pline([(bx + dx * 0.3, btop + 10), (bx + dx * 0.7, btop + dy * 0.5), (bx + dx, btop + dy)], "#4E7A2E", 4, 2016 + k, 1, 1))
    for k, (x, y, a) in enumerate(((bx - 60, btop - 40, -150), (bx + 56, btop - 30, -30))):
        out.append(leaf_simple(D, bx + (x - bx) * 0.2, btop, 70, 24, a, LEAFG, 2021 + k, inkw=1.2))
    for k, (dx, dy, r, f) in enumerate(sorted(stems, key=lambda s: s[1])):
        out.append(sunflower(D, bx + dx, btop + dy, r, 2023 + k, rot_=k * 7, face=f))
    out.append(wicker_basket(D, bx, btop, 64, 14, btop + 70, 52, 2028))
    out.append(taper([(bx - 40, btop + 72), (head[0] + 6, head[1] + 30)], 4, 4, "#8A909A"))
    # one petal fallen on the cobbles
    out.append(f'<path d="{blob(240, 556, 10, 3.6, 2029, 0.15, 8, 30)}" fill="#F6C21C" stroke="#A8601A" stroke-width="0.6"/>')
    # lettering
    out.append(letters(D, 300, 128, "C’est la vie", SERIF_IT, 116, "#8A3A12", ["#B8561E", "#5A1E06", "#D8702E"], 2030, max_w=440,
                       shadow="#FFF4DC", soff=(0.02, 0.035), angle=-40, hi="#F6B878"))
    out.append(ruled(300, 172, "ET ELLE EST BELLE", "#2E5A8A", font=JOS, size=19, ls=6, line_w=34, gap=14, max_w=380))
    return finish_f(D, out, 2031)


# ================================================================ 21. Joie de vivre — a guinguette by the river at dusk
@design("joie-de-vivre")
def joie_de_vivre():
    D = Doc2("fr-jv")
    out = [sky(D, [(0, "#2E2E6A"), (0.4, "#8A5A9A"), (0.75, "#F2A07A"), (1, "#FFD49A")], 2101, 400, ["#B87AA8", "#4A3A7A", "#FFC8A0"], 70, angle=-3, sop=(0.05, 0.14))]
    rnd = random.Random(2102)
    for _ in range(18):
        out.append(f'<circle cx="{rnd.uniform(20, 580):.0f}" cy="{rnd.uniform(20, 160):.0f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFF6E0" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    # far bank: poplars and willows in silhouette, the river catching the sunset
    for k in range(12):
        x = -20 + k * 56 + rnd.uniform(-10, 10)
        h = rnd.uniform(80, 140)
        out.append(dab_crown(D, x, 330 - h / 2, rnd.uniform(18, 30), h / 2, [("#5A4A6A", "#3E3252", "#241C36")], 2103 + k, n=26, size=(5, 9), inkw=0))
    out.append(f'<rect x="-10" y="326" width="620" height="16" fill="#3A2E4A"/>')
    out.append(sea(D, 340, 420, [(0, "#E8A890"), (1, "#5A4A7A")], 2116, ["#FFD8B0", "#3A2E5A"], 50))
    for k in range(14):
        y = 346 + k * 5
        out.append(taper([(300 - 60 + rnd.uniform(-20, 20), y), (300 + 60 + rnd.uniform(-20, 20), y)], 1, 2.4, "#FFE0B0", 0.5))
    # a rowing boat on the water
    out.append(painted(D, [(120, 372), (210, 372), (198, 384), (132, 384)], ("#F2C8A0", "#C86A3A", "#6A2A14"), 2117, sk=0.25, n=4, inkw=1.4, hi=0.4))
    out.append(pline([(150, 372), (176, 360)], "#3A2A1A", 2, 2118, 0.9, 1) + pline([(180, 374), (220, 386)], "#3A2A1A", 2, 2119, 0.9, 1))
    # the wooden dance floor and its posts
    out.append(f'<path d="M -10 416 L 610 404 L 610 610 L -10 610 Z" fill="#8A5A3A"/>')
    out.append(wood_planks(D, 412, 610, 2120, ("#C8925A", "#9A6238", "#5A3418"), 6))
    out.append(f'<path d="M -10 416 L 610 404 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#2A1A3A", 0.2), (1, "#2A1A3A", 0.0)])}"/>')
    out.append(soft_glow(D, 300, 420, 300, "#FFD890", 0.35))
    for x in (40, 560):
        out.append(painted(D, rect_pts(x - 7, 210, x + 7, 470, 20, 2121 + x, 0.5), ("#8A6A4A", "#5A3E28", "#2A1A0E"), 2121 + x, sdir=(1, 0), sk=0.25, angle=-90, n=10, inkw=1.6, hi=0.3))
    # strings of bulbs, zigzag
    for k, (a, b, sag) in enumerate((((40, 222), (560, 222), 70), ((40, 222), (300, 200), 40), ((300, 200), (560, 222), 40))):
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)) for t in [i / 24 for i in range(25)]]
        out.append(ink(smooth_open(pts), "#2A1A2A", 1.6, 2122 + k, 1, 0.9))
        for i in range(2, 24, 3):
            x, y = pts[i]
            out.append(soft_glow(D, x, y + 6, 18, "#FFE29A", 0.75))
            out.append(f'<path d="{blob(x, y + 7, 4.2, 5.4, 2130 + i + k * 30, 0.05, 8)}" fill="#FFF4C8"/>')
    # dancing couples in warm silhouette, and a couple of tables with checked cloths
    for k, (x, base, h, f) in enumerate(((236, 452, 104, 1), (392, 440, 86, -1))):
        out.append(figures.person(x, base, h, "couple", f, palette="silhouette:#3A2440", seed=2140 + k, rim="#FFC890", light=-1, shadow=0.25))
    for k, (x, y) in enumerate(((140, 500), (462, 506))):
        out.append(cast(D, x + 8, y + 62, 60, 8, strength=0.4, seed=2149 + k))
        out.append(taper([(x, y), (x, y + 60)], 7, 7, "#3A2A1A"))
        out.append(taper([(x - 22, y + 62), (x + 22, y + 62)], 5, 5, "#3A2A1A"))
        out.append(cloth(D, ell_pts(x, y, 70, 18, 0, 360, 24)[:-1] + [(x + 70, y + 18), (x - 70, y + 18)], ROUGE[1], 2150 + k, cell=9, inkw=1.4))
        for j, gx in enumerate((x - 24, x + 22)):
            out.append(f'<path d="M {gx - 7} {y - 26} L {gx + 7} {y - 26} L {gx + 4} {y - 12} L {gx - 4} {y - 12} Z" fill="#F2E8E8" opacity="0.6" stroke="#6A5A6A" stroke-width="1"/>')
            out.append(f'<path d="M {gx - 6} {y - 20} L {gx + 6} {y - 20} L {gx + 4} {y - 12} L {gx - 4} {y - 12} Z" fill="#B8283A" opacity="0.85"/>')
            out.append(pline([(gx, y - 12), (gx, y - 2)], "#8A7A8A", 1.4, 2152 + j, 0.9, 1))
    # an accordion resting on a chair at the left (the music goes on)
    ax, ay = 96, 470
    out.append(painted(D, rect_pts(ax - 26, ay - 30, ax - 10, ay + 10, 6, 2155, 0.3), ROUGE, 2155, sk=0.2, n=3, inkw=1.2, hi=0.4))
    for k in range(5):
        out.append(painted(D, rect_pts(ax - 10 + k * 6, ay - 28, ax - 4 + k * 6, ay + 8, 6, 2156 + k, 0.2), ("#4A4A50", "#2A2A30", "#0A0A0E") if k % 2 else ("#F6F0E0", "#D8D0C0", "#8A8070"), 2156 + k, sk=0.2, n=2, inkw=0.8, hi=0.4))
    out.append(painted(D, rect_pts(ax + 20, ay - 30, ax + 36, ay + 10, 6, 2161, 0.3), ROUGE, 2161, sk=0.2, n=3, inkw=1.2, hi=0.4))
    for k in range(4):
        out.append(f'<circle cx="{ax + 28}" cy="{ay - 22 + k * 9}" r="2" fill="#F6F0E0"/>')
    # lettering
    out.append(letters(D, 300, 132, "Joie de vivre", SERIF_IT, 112, "#FFF0D0", ["#FFFFFF", "#FFE0A8"], 2162, max_w=450,
                       shadow="#1A1A4A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "UN SOIR À LA GUINGUETTE", "#FFD49A", font=JOS, size=18, ls=5, line_w=26, gap=12, max_w=380))
    return finish_f(D, out, 2163, "#1A1A3A")


# ================================================================ 22. On tire ou on pointe ? — pétanque under the plane trees
def boule(D, cx, cy, r, seed, light=(-0.6, -0.7)):
    """A steel pétanque boule: polished, sky reflected on top, gravel below, engraved grooves."""
    out = [cast(D, cx + r * 0.3, cy + r * 0.85, r * 1.1, r * 0.25, strength=0.5, seed=seed)]
    g = D.rad([(0, "#FFFFFF"), (0.25, "#D8DCE2"), (0.6, "#8A9098"), (1, "#3A3E46")], 0.35, 0.3, 0.75)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{g}"/>')
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    inner = [f'<path d="{blob(cx, cy + r * 0.75, r * 0.9, r * 0.3, seed, 0.1, 12)}" fill="#C8A878" opacity="0.4"/>']
    for k in range(3):
        a = 0.35 + k * 0.28
        inner.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * a:.1f}" ry="{r:.1f}" fill="none" stroke="#3A3E46" stroke-width="1.6" opacity="0.5" transform="rotate(30 {cx} {cy})"/>')
    inner.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.42, r * 0.28, r * 0.14, seed + 1, 0.2, 10, -30)}" fill="#FFFFFF" opacity="0.9"/>')
    inner.append(f'<path d="{blob(cx - r * 0.1, cy - r * 0.62, r * 0.4, r * 0.1, seed + 2, 0.2, 10, -10)}" fill="#A8C8E8" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(f"M {cx - r} {cy} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0", "#2A2E36", 1.8, seed, 1, 0.7))
    return "".join(out)


@design("on-tire-ou-on-pointe")
def on_tire_ou_on_pointe():
    D = Doc2("fr-pt")
    # the square under the plane trees: trunks, a café with its chairs, dappled late light
    out = [sky(D, [(0, "#E8E0B8"), (1, "#E2C890")], 2201, 600, ["#FFF6D8", "#C8B080"], 60, angle=-3, sop=(0.05, 0.12))]
    out.append(painted(D, rect_pts(-10, 244, 610, 340, 30, 2202, 0.5), ("#F6E2C0", "#E2C49A", "#A88A60"), 2202, sk=0.1, n=20, inkw=0, hi=0.2))
    for k, x in enumerate((60, 200, 340, 480)):
        out.append(painted(D, rect_pts(x, 268, x + 70, 340, 12, 2203 + k, 0.4), ("#8AB8C8", "#4E8AA0", "#24506A"), 2203 + k, sk=0.15, n=8, inkw=1.2, inkop=0.4, hi=0.3))
    out.append(f'<path d="M -10 246 L 610 246 L 610 262 L -10 262 Z" fill="#C8382E"/>')
    out.append(stripes_in(D, "M -10 246 L 610 246 L 610 262 L -10 262 Z", (-10, 246, 610, 262), 0, [20, 20], ["#FFFDF4", None], 2207, 0.9))
    rnd = random.Random(2208)
    for k in range(6):
        x = 40 + k * 100 + rnd.uniform(-10, 10)
        out.append(pline([(x, 330), (x, 300), (x + 18, 300), (x + 18, 330)], "#3A3A40", 2.4, 2209 + k, 0.8, 1))
        out.append(pline([(x + 18, 300), (x + 20, 280)], "#3A3A40", 2.4, 2215 + k, 0.8, 1))
    out.append(f'<rect x="-10" y="244" width="620" height="100" fill="#E8DCC0" opacity="0.4"/>')
    for x, w in ((70, 46), (520, 52)):
        out.append(plane_trunk(D, x, 380, -10, w, 2240 + x))
    # canopy of plane leaves across the top
    for k in range(14):
        out.append(dab_crown(D, -20 + k * 48, 40 + rnd.uniform(-20, 20), 60, 46, [("#C8D88A", "#8AA850", "#4E6A2A")], 2220 + k, n=50, size=(6, 11), inkw=0))
    out.append(f'<rect x="-10" y="-10" width="620" height="262" fill="#F6EEC8" opacity="0.62"/>')
    # gravel ground, receding
    out.append(f'<path d="M -10 340 L 610 340 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#E8D2A0"), (1, "#C8A870")])}"/>')
    for _ in range(500):
        y = rnd.uniform(340, 600)
        s = 0.6 + (y - 340) / 260 * 2.6
        out.append(f'<path d="{blob(rnd.uniform(-10, 610), y, s, s * 0.7, rnd.randint(1, 9999), 0.25, 6)}" fill="{rnd.choice(["#B89870", "#F6E6C0", "#9A7A50", "#D8BC90"])}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    for _ in range(20):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(350, 600), rnd.uniform(20, 50), rnd.uniform(8, 16), rnd.randint(1, 999), 0.3, 10)}" fill="#6A4A20" opacity="0.1"/>')
    # a line drawn in the gravel (the throwing circle), the cochonnet and the boules
    out.append(ink(smooth_closed(ell_pts(120, 560, 70, 18, 0, 360, 24)), "#8A6A40", 2.4, 2250, 1, 0.6))
    cx_, cy_ = 300, 452
    out.append(cast(D, cx_ + 4, cy_ + 9, 14, 4, strength=0.4, seed=2251))
    out.append(painted(D, blob_pts(cx_, cy_, 11, 11, 2252, 0.03, 12), ("#FF8A6A", "#E0401E", "#7A1406"), 2252, sk=0.25, n=3, inkw=1.3, hi=0.5))
    out.append(boule(D, 252, 466, 34, 2253))
    out.append(boule(D, 362, 436, 28, 2254))
    out.append(boule(D, 440, 512, 52, 2255))
    out.append(boule(D, 170, 534, 60, 2256))
    # the tape measure, because it's close
    # a little tuft of grass breaking the gravel, a fallen plane leaf
    out.append(grass(2261, (480, 560, 560, 574), ["#8AA050", "#5E7A3A"], 26, (8, 16)))
    out.append(maple_leaf(520, 430, 22, "#C8A050", "#7A5A20", 30, 2262, "#F6E0A0"))
    # lettering
    out.append(letters(D, 300, 104, "On tire", SERIF_IT, 92, "#2E4A1A", ["#4A6A2A", "#1A2E0A", "#6A8A3A"], 2258, max_w=320,
                       shadow="#FFF8E0", soff=(0.02, 0.035), angle=-40, hi="#C8E0A0"))
    out.append(letters(D, 300, 184, f"ou on pointe{NB}?", SERIF_IT, 84, "#2E4A1A", ["#4A6A2A", "#1A2E0A", "#6A8A3A"], 2259, max_w=430,
                       shadow="#FFF8E0", soff=(0.02, 0.035), angle=-40, hi="#C8E0A0"))
    out.append(ruled(300, 230, "LA PÉTANQUE", "#7A3A12", font=JOS, size=19, ls=7, line_w=34, gap=14, max_w=300))
    return finish_f(D, out, 2260)


# ================================================================ 23. Petit à petit, l'oiseau fait son nid
def sparrow(D, ox, oy, s, seed, flip=1, twig=True):
    """A house sparrow (moineau) perched, facing left: chestnut back streaked dark, grey crown, black bib, buff belly."""
    P = lambda x, y: (ox + x * s * flip, oy + y * s)
    out = []
    tail = [P(0.45, -0.32), P(0.95, -0.2), P(0.98, -0.1), P(0.45, -0.2)]
    out.append(painted(D, tail, ("#A8846A", "#6A4A32", "#3A2416"), seed, sk=0.25, n=4, inkw=1.3, hi=0.3))
    body = [P(-0.42, -0.62), P(-0.1, -0.7), P(0.3, -0.56), P(0.58, -0.3), P(0.4, -0.12), P(0.0, -0.06), P(-0.36, -0.2), P(-0.5, -0.4)]
    out.append(painted(D, body, ("#E8D8C0", "#C8B49A", "#8A7660"), seed + 1, sdir=(0.3, 1), sk=0.2, n=14, inkw=1.6, hi=0.4))
    wing = [P(-0.16, -0.62), P(0.2, -0.6), P(0.6, -0.34), P(0.42, -0.24), P(0.0, -0.3), P(-0.18, -0.42)]
    out.append(painted(D, wing, ("#C8925A", "#8A5A30", "#4A2A12"), seed + 2, sdir=(0.3, 1), sk=0.25, angle=-20 * flip, n=14, inkw=1.4, hi=0.4))
    for k in range(5):
        a, b = P(-0.08 + k * 0.12, -0.56 + k * 0.03), P(0.04 + k * 0.12, -0.44 + k * 0.03)
        out.append(taper([a, b], 3, 1, "#2A1606", 0.6))
    out.append(taper([P(-0.1, -0.44), P(0.3, -0.38)], 3.5, 2, "#FFFFFF", 0.8))
    head = blob_pts(*P(-0.46, -0.78), s * 0.24, s * 0.22, seed + 3, 0.04, 14)
    out.append(painted(D, head, ("#C8925A", "#8A5A30", "#4A2A12"), seed + 3, sk=0.2, n=6, inkw=1.4, hi=0.3))
    crown = blob_pts(*P(-0.44, -0.9), s * 0.18, s * 0.1, seed + 4, 0.06, 12)
    out.append(f'<path d="{smooth_closed(crown)}" fill="#8A8E96"/>')
    out.append(f'<path d="{blob(*P(-0.56, -0.74), s * 0.1, s * 0.07, seed + 5, 0.1, 10)}" fill="#E8E2D8"/>')
    out.append(f'<path d="{blob(*P(-0.58, -0.58), s * 0.12, s * 0.12, seed + 6, 0.12, 10)}" fill="#1E1A18"/>')
    ex, ey = P(-0.55, -0.82)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.04:.1f}" fill="#120A06"/><circle cx="{ex - s * 0.012 * flip:.1f}" cy="{ey - s * 0.012:.1f}" r="{s * 0.014:.1f}" fill="#FFFFFF"/>')
    beak = [P(-0.66, -0.8), P(-0.82, -0.76), P(-0.66, -0.7)]
    out.append(painted(D, beak, ("#6A6A6A", "#3A3A3A", "#1A1A1A"), seed + 7, sk=0.2, n=2, inkw=1, hi=0.4))
    for dx in (-0.1, 0.08):
        out.append(pline([P(dx, -0.1), P(dx - 0.02, 0.02)], "#B88A6A", 2.2, seed + int(dx * 100), 1, 1))
        out.append(pline([P(dx - 0.08, 0.02), P(dx + 0.08, 0.02)], "#B88A6A", 1.8, seed + 3, 1, 1))
    if twig:
        out.append(taper([P(-0.78, -0.76), P(-1.1, -0.66), P(-1.4, -0.7)], 2.4, 1.4, "#9A7A4A"))
        out.append(taper([P(-0.78, -0.74), P(-0.9, -0.9), P(-1.0, -1.0)], 1.8, 1, "#B8945A"))
        out.append(taper([P(-1.1, -0.66), P(-1.2, -0.54)], 1.6, 0.8, "#9A7A4A"))
    return "".join(out)


def nest(D, cx, cy, rx, ry, seed, eggs=3):
    """A twig-and-straw nest in 3/4 view with speckled pale-blue eggs."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + ry * 0.9, rx * 1.05, ry * 0.4, strength=0.4, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 30))}" fill="#6A4A28"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy - 2, rx * 0.72, ry * 0.6, 0, 360, 24))}" fill="#3A2412"/>')
    for k in range(eggs):
        ex, ey = cx - rx * 0.3 + k * rx * 0.3, cy - 4 + (k % 2) * 4
        out.append(painted(D, blob_pts(ex, ey, rx * 0.17, rx * 0.13, seed + k, 0.04, 12), ("#E8F4F4", "#B8D8DC", "#6A9AA0"), seed + k, sk=0.2, n=3, inkw=1.1, hi=0.55))
        out.append(specks(seed + 10 + k, (ex - rx * 0.12, ey - rx * 0.1, ex + rx * 0.12, ey + rx * 0.1), ["#6A5A4A"], 8, (0.6, 1.2), (0.6, 0.9)))
    front = ell_pts(cx, cy + 2, rx, ry, 0, 180, 20) + ell_pts(cx, cy + ry * 0.9, rx * 0.8, ry * 0.9, 180, 0, 20)[1:-1]
    out.append(painted(D, front, ("#C8A06A", "#8A6A3A", "#4A3218"), seed + 20, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.2, hi=0.3))
    for _ in range(int(rx * 1.4)):
        a = rnd.uniform(0, math.pi)
        x0, y0 = cx + math.cos(a) * rx * rnd.uniform(0.6, 1.05), cy + 2 + math.sin(a) * ry * rnd.uniform(0.4, 1.4)
        L = rnd.uniform(14, 34)
        t = rnd.uniform(-0.5, 0.5)
        out.append(pline([(x0 - L / 2, y0 - t * L * 0.3), (x0, y0 + rnd.uniform(-2, 2)), (x0 + L / 2, y0 + t * L * 0.3)], rnd.choice(["#E8C88A", "#A8804A", "#6A4A22", "#F6E0A8"]), rnd.uniform(1, 2), rnd.randint(1, 999), 0.9, 1))
    return "".join(out)


def blossom_fr(D, cx, cy, r, seed, col=("#FFFFFF", "#FBE4EA", "#E8A8B8")):
    out = []
    for k in range(5):
        a = math.radians(k * 72 + seed * 7)
        out.append(painted(D, blob_pts(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, r * 0.55, r * 0.46, seed + k, 0.1, 10), col, seed + k, sk=0.2, n=2, inkw=0.9, inkop=0.5, hi=0.5))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.22:.1f}" fill="#F2C83A"/>')
    for k in range(6):
        a = math.radians(k * 60)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.3:.1f}" cy="{cy + math.sin(a) * r * 0.3:.1f}" r="1.2" fill="#C8601A"/>')
    return "".join(out)


@design("petit-a-petit")
def petit_a_petit():
    D = Doc2("fr-pp")
    out = [sky(D, [(0, "#BCDCEA"), (1, "#E8F2E0")], 2301, 600, ["#FFFFFF", "#9ACCE0"], 60, angle=-3, sop=(0.05, 0.14))]
    out.append(blooms(2302, ["#FFFFFF", "#C8E4D8"], 7, (0, 200, 600, 600), (90, 160), (0.1, 0.2)))
    for k, (x, y, w) in enumerate(((110, 300, 110), (500, 260, 90))):
        out.append(puff_cloud(D, x, y, w, 2303 + k, op=0.8, rows=1))
    # the apple branch in blossom
    br = catmull([(-20, 530), (120, 496), (260, 480), (400, 440), (520, 392), (620, 368)], 8)
    out.append(taper(br, 26, 10, "#6A4A32"))
    out.append(taper([(x, y - 4) for x, y in br], 5, 2, "#A8805A", 0.7))
    twig1 = catmull([(200, 476), (226, 420), (214, 372)], 6)
    twig2 = catmull([(430, 424), (476, 466), (540, 492)], 6)
    for t in (twig1, twig2):
        out.append(taper(t, 8, 3, "#6A4A32"))
    rnd = random.Random(2304)
    for k, (x, y, a) in enumerate(((150, 482, -120), (300, 460, -70), (360, 446, 40), (500, 392, -100), (560, 376, 30), (214, 380, -150), (520, 490, 20), (90, 500, 60))):
        out.append(leaf_simple(D, x, y, 48, 15, a, ("#B8E08A", "#6AAA4A", "#2E6A2A"), 2305 + k, inkw=1.1))
    for k, (x, y, r) in enumerate(((210, 362, 16), (236, 390, 13), (546, 488, 15), (110, 470, 14), (470, 410, 13), (586, 350, 15), (40, 506, 14))):
        out.append(blossom_fr(D, x, y, r, 2315 + k))
    for k, (x, y) in enumerate(((190, 352), (560, 470), (500, 400))):
        out.append(painted(D, blob_pts(x, y, 5, 7, 2325 + k, 0.1, 8), PINK, 2325 + k, sk=0.2, n=2, inkw=0.8, hi=0.4))
    # the nest in the fork of the branch, the sparrow bringing one more twig
    out.append(nest(D, 300, 452, 96, 30, 2330))
    out.append(sparrow(D, 456, 420, 136, 2331, flip=1))
    # a falling blossom petal
    out.append(f'<path d="{blob(140, 560, 6, 4, 2332, 0.15, 8, 20)}" fill="#FBE4EA" stroke="#E8A8B8" stroke-width="0.8"/>')
    # lettering
    out.append(letters(D, 300, 128, "Petit à petit", SERIF_IT, 110, "#2E5A3A", ["#3E7A4E", "#1A3E26", "#5A9A6A"], 2333, max_w=450,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#B8E0C0"))
    out.append(letters(D, 300, 190, "l’oiseau fait son nid", SERIF_IT, 50, "#8A4A2A", ["#A8603A", "#5A2A10"], 2334, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.5))
    return finish_f(D, out, 2335)


# ================================================================ 24. Bisous — combien de bises ?
FRANCE_LL = [(2.37, 51.05), (1.85, 50.95), (1.6, 50.7), (1.55, 50.2), (1.08, 49.92), (0.4, 49.75), (0.1, 49.5), (-0.3, 49.32), (-1.1, 49.37),
             (-1.25, 49.7), (-1.94, 49.72), (-1.6, 49.2), (-1.5, 48.63), (-2.0, 48.65), (-3.0, 48.82), (-4.0, 48.72), (-4.77, 48.4), (-4.5, 48.2),
             (-4.73, 48.04), (-4.1, 47.8), (-3.37, 47.7), (-2.8, 47.5), (-2.2, 47.27), (-2.05, 46.9), (-1.8, 46.5), (-1.15, 46.15), (-1.1, 45.6),
             (-1.2, 44.65), (-1.35, 44.0), (-1.55, 43.45), (-1.78, 43.36), (-1.4, 43.05), (-0.5, 42.8), (0.7, 42.85), (1.4, 42.6), (2.2, 42.43),
             (3.17, 42.45), (3.05, 43.0), (3.15, 43.2), (3.6, 43.35), (4.0, 43.5), (4.6, 43.38), (5.35, 43.3), (5.95, 43.1), (6.6, 43.15),
             (7.27, 43.7), (7.5, 43.78), (7.0, 44.2), (6.9, 44.85), (7.1, 45.25), (6.85, 45.85), (6.95, 46.05), (6.2, 46.3), (6.1, 46.6),
             (6.9, 47.4), (7.55, 47.58), (7.6, 48.0), (7.8, 48.6), (8.2, 48.97), (7.4, 49.17), (6.7, 49.18), (6.1, 49.47), (5.5, 49.5),
             (4.85, 49.8), (4.8, 50.15), (4.2, 49.95), (3.7, 50.3), (3.2, 50.7), (2.6, 50.85)]
CORSE_LL = [(9.4, 43.0), (9.55, 42.6), (9.4, 42.0), (9.2, 41.4), (8.8, 41.6), (8.6, 42.0), (8.6, 42.4), (8.95, 42.65), (9.3, 42.85)]


@design("bisous")
def bisous():
    D = Doc2("fr-bi")
    # an old school wall map on cream paper
    out = [paper(D.nid(), "#F6EEDC", FLECK, 2401)]
    out.append(blooms(2402, ["#E8D8B8", "#D8C49A"], 6, (0, 0, 600, 600), (100, 190), (0.08, 0.14)))
    out.append(f'<path d="{hg.org_rect(26, 26, 548, 548, 2403, 0.6, 30, 3)}" fill="none" stroke="#2F5AA6" stroke-width="3"/>')
    out.append(f'<path d="{hg.org_rect(36, 36, 528, 528, 2404, 0.6, 30, 3)}" fill="none" stroke="#2F5AA6" stroke-width="1.2"/>')
    k = 25
    X = lambda lon: 112 + (lon + 5) * k
    Y = lambda lat: 202 + (51.05 - lat) * k * 1.42
    fr = [(X(a), Y(b)) for a, b in FRANCE_LL]
    co = [(X(a), Y(b)) for a, b in CORSE_LL]
    frd = smooth_closed(jitter(fr, 2405, 0.6))
    cod = smooth_closed(co)
    # sea hatching around the coast
    for i in range(4):
        out.append(f'<path d="{frd}" fill="none" stroke="#8AB0D8" stroke-width="{12 - i * 3}" opacity="{0.12 + i * 0.05:.2f}"/>')
    out.append(f'<path d="{frd}" fill="#FBF6EA"/>')
    out.append(f'<path d="{cod}" fill="#FBF6EA"/>')
    cid = D.clip(f'<path d="{frd} {cod}"/>')
    zones = []
    two = ("#F6C8C8", "#E88A8A")
    zones.append(f'<rect x="0" y="0" width="600" height="600" fill="#F8D8D0"/>')
    # 4 bises: the north-west and the Loire; 3 bises: the south (Languedoc, Drôme, Ardèche, Aveyron); 1: Finistère
    z4 = smooth_closed([(X(-1.7), Y(49.8)), (X(1.6), Y(50.2)), (X(2.4), Y(48.9)), (X(2.4), Y(47.2)), (X(0.6), Y(46.4)), (X(-1.6), Y(46.6)), (X(-2.3), Y(47.4)), (X(-1.4), Y(48.4))])
    z3 = smooth_closed([(X(1.6), Y(44.6)), (X(3.4), Y(45.2)), (X(5.2), Y(45.0)), (X(5.5), Y(43.9)), (X(4.6), Y(43.3)), (X(3.0), Y(42.6)), (X(1.8), Y(43.0)), (X(1.2), Y(43.8))])
    z1 = smooth_closed([(X(-5.2), Y(48.8)), (X(-3.6), Y(48.9)), (X(-3.4), Y(47.6)), (X(-5.2), Y(47.6))])
    zones.append(f'<path d="{z4}" fill="#F6C46A" opacity="0.75"/>')
    zones.append(f'<path d="{z3}" fill="#A8C8E8" opacity="0.85"/>')
    zones.append(f'<path d="{z1}" fill="#B8D8A0" opacity="0.9"/>')
    zones.append(strokes(D.nid(), f"{frd} {cod}", (60, 180, 560, 580), ["#FFFFFF", "#D8B898"], 2406, n=160, angle=-30, length=(20, 60), width=(2, 5), opacity=(0.1, 0.25)))
    # rivers, faint
    for pts in ([(X(-2.1), Y(47.3)), (X(0.0), Y(47.4)), (X(2.0), Y(47.8)), (X(3.0), Y(46.8)), (X(4.0), Y(45.5))],
                [(X(0.1), Y(49.45)), (X(1.5), Y(49.1)), (X(2.35), Y(48.85)), (X(4.0), Y(48.3))],
                [(X(4.7), Y(43.4)), (X(4.85), Y(44.5)), (X(4.85), Y(45.75)), (X(6.1), Y(46.2))],
                [(X(-1.1), Y(45.55)), (X(0.0), Y(44.8)), (X(1.4), Y(43.6))]):
        zones.append(pline(pts, "#6A9AD0", 1.6, 2407, 0.6, 1))
    out.append(f'<g {cid}>{"".join(zones)}</g>')
    out.append(ink(frd, "#2A3A6A", 2.2, 2408, 2, 0.85))
    out.append(ink(cod, "#2A3A6A", 1.8, 2409, 2, 0.85))
    # numbers of bises, in little rosettes
    def badge(x, y, n, col):
        o = [f'<circle cx="{x + 1.5:.1f}" cy="{y + 2:.1f}" r="19" fill="#3A2418" opacity="0.2"/>',
             painted(D, blob_pts(x, y, 19, 19, int(x + y), 0.03, 14), pal3(col, 0.35, 0.3), int(x + y), sk=0.15, n=3, inkw=1.4, hi=0.5)]
        o.append(f'<text x="{x:.1f}" y="{y + 10:.1f}" text-anchor="middle" {DMS} font-size="30" fill="#FFFDF4">{n}</text>')
        return "".join(o)
    out.append(badge(X(-3.85), Y(48.2), 1, "#4E8A3E"))
    out.append(badge(X(0.3), Y(48.1), 4, "#D8901E"))
    out.append(badge(X(3.4), Y(44.0), 3, "#2F5AA6"))
    out.append(badge(X(5.6), Y(48.4), 2, "#C8382E"))
    out.append(badge(X(0.5), Y(44.4), 2, "#C8382E"))
    out.append(badge(X(9.05), Y(42.15), 2, "#C8382E"))
    # Paris: a little red heart
    out.append(p_heart(D, X(2.35), Y(48.86) + 2, 9, ROUGE, 2410, inkw=1))
    # a compass rose, bottom-left
    cx_, cy_ = 520, 284
    for kk in range(8):
        a = math.radians(kk * 45 - 90)
        L = 30 if kk % 2 == 0 else 16
        out.append(f'<path d="{pd([(cx_, cy_), (cx_ + math.cos(a + 0.3) * 6, cy_ + math.sin(a + 0.3) * 6), (cx_ + math.cos(a) * L, cy_ + math.sin(a) * L), (cx_ + math.cos(a - 0.3) * 6, cy_ + math.sin(a - 0.3) * 6)])}" fill="{"#2F5AA6" if kk % 2 == 0 else "#C8382E"}" opacity="0.85"/>')
    out.append(label(cx_, cy_ - 34, "N", CINZEL, 16, "#2A3A6A"))
    # lettering
    out.append(letters(D, 300, 132, "Bisous", SERIF_IT, 132, ROUGE[1], [ROUGE[0], ROUGE[2], "#E8504A"], 2411, max_w=360,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC0B0"))
    out.append(ruled(300, 176, f"COMBIEN DE BISES{NB}?", "#2A3A6A", font=JOS, size=18, ls=5, line_w=30, gap=12, max_w=360))
    out.append(label(132, 486, "ÇA DÉPEND", MONO, 16, "#5A4A3A", ls=2, max_w=150))
    out.append(label(132, 508, "DE LA RÉGION", MONO, 16, "#5A4A3A", ls=2, max_w=150))
    rh = random.Random(2413)
    for (hx, hy, hs) in ((84, 300, 9), (110, 262, 6), (500, 470, 8), (470, 214, 6), (90, 400, 6)):
        out.append(p_heart(D, hx, hy, hs, ROUGE, rh.randint(1, 999), rot_=rh.uniform(-20, 20), inkw=0.9))
    return finish_f(D, out, 2412)


# ================================================================ 25. Val de Loire — a château on the water, morning mist
def cone_turret(D, x, base, wall_top, w, roof_h, seed, stone=STONE, slate=SLATE):
    """A round tower: shaded cylinder in tuffeau stone, a steep conical slate roof (poivrière) and a lead finial."""
    out = []
    body = [(x - w / 2, base), (x - w / 2, wall_top), (x + w / 2, wall_top), (x + w / 2, base)]
    bd = smooth_closed(poly_pts(body, 10, seed, 0.3))
    out.append(f'<path d="{bd}" fill="{D.lin([(0, stone[0]), (0.45, stone[1]), (1, stone[2])], 0, 0, 1, 0)}"/>')
    for k in range(2):
        y = wall_top + (base - wall_top) * (0.3 + k * 0.35)
        out.append(painted(D, rect_pts(x - w * 0.12, y, x + w * 0.12, y + (base - wall_top) * 0.16, 6, seed + k, 0.2), ("#8A9AB0", "#4A5A72", "#1E2A3A"), seed + k, sk=0.2, n=2, inkw=1, hi=0.4))
    out.append(ink(bd, "#8A7A5A", 1.4, seed, 1, 0.6))
    cone = [(x - w / 2 - 4, wall_top + 2), (x, wall_top - roof_h), (x + w / 2 + 4, wall_top + 2)]
    out.append(f'<path d="{smooth_closed(cone)}" fill="{D.lin([(0, slate[0]), (0.5, slate[1]), (1, slate[2])], 0, 0, 1, 0)}"/>')
    for k in range(4):
        t = 0.2 + k * 0.2
        y = wall_top - roof_h * t
        hw = (w / 2 + 4) * (1 - t)
        out.append(pline([(x - hw, y + 2), (x, y + 4), (x + hw, y + 2)], "#2A3444", 1, seed + k, 0.4, 1))
    out.append(ink(smooth_open(cone), "#1E2A3A", 1.4, seed + 5, 1, 0.7))
    out.append(pline([(x, wall_top - roof_h), (x, wall_top - roof_h - 14)], "#3A4454", 2, seed + 6, 1, 1))
    out.append(f'<circle cx="{x}" cy="{wall_top - roof_h - 8}" r="2.4" fill="#C8A048"/>')
    return "".join(out)


def chateau(D, cx, wl, s, seed):
    """A Loire château: a main logis with a steep slate roof, tall carved dormers and chimneys, round corner
    turrets, and a two-storey gallery striding across the river on arches."""
    out = []
    P = lambda x, y: (cx + x * s, wl - y * s)
    # gallery on arches over the water, to the right
    gx0, gx1 = 0.55, 1.6
    gal = poly_pts([P(gx0, 0.08), P(gx0, 0.62), P(gx1, 0.62), P(gx1, 0.08)], 12, seed, 0.3)
    out.append(painted(D, gal, STONE, seed, sdir=(1, 0.2), sk=0.1, angle=-90, n=20, inkw=1.4, inkop=0.5, hi=0.3))
    for k in range(5):
        ax = gx0 + 0.1 + k * 0.22
        a0, a1 = P(ax, 0.0), P(ax + 0.14, 0.0)
        out.append(f'<path d="M {a0[0]:.1f} {wl + 2:.1f} L {a0[0]:.1f} {wl - 0.12 * s:.1f} Q {(a0[0] + a1[0]) / 2:.1f} {wl - 0.28 * s:.1f} {a1[0]:.1f} {wl - 0.12 * s:.1f} L {a1[0]:.1f} {wl + 2:.1f} Z" fill="#3E4A5A" opacity="0.85"/>')
        for row in (0.36, 0.5):
            wx, wy = P(ax + 0.03, row + 0.08)
            out.append(painted(D, rect_pts(wx, wy, wx + 0.07 * s, wy + 0.1 * s, 4, seed + k * 3 + int(row * 10), 0.2), ("#9AAAC0", "#4A5A72", "#1E2A3A"), seed + k + int(row * 10), sk=0.2, n=2, inkw=0.9, hi=0.5))
    groof = [P(gx0 - 0.02, 0.62), P(gx0 + 0.06, 0.8), P(gx1 - 0.06, 0.8), P(gx1 + 0.02, 0.62)]
    out.append(painted(D, groof, SLATE, seed + 2, sdir=(1, 0.3), sk=0.15, angle=0, n=10, inkw=1.2, hi=0.3))
    for k in range(4):
        dx = gx0 + 0.18 + k * 0.26
        d0 = P(dx, 0.62)
        out.append(painted(D, [(d0[0] - 8, d0[1]), (d0[0] - 8, d0[1] - 0.14 * s), (d0[0], d0[1] - 0.22 * s), (d0[0] + 8, d0[1] - 0.14 * s), (d0[0] + 8, d0[1])], STONE, seed + 10 + k, sk=0.2, n=3, inkw=1, hi=0.4))
        out.append(f'<rect x="{d0[0] - 4:.1f}" y="{d0[1] - 0.12 * s:.1f}" width="8" height="{0.1 * s:.1f}" fill="#4A5A72"/>')
    # main logis
    lg_ = poly_pts([P(-0.6, 0.0), P(-0.6, 0.78), P(0.6, 0.78), P(0.6, 0.0)], 12, seed + 3, 0.3)
    out.append(painted(D, lg_, STONE, seed + 3, sdir=(1, 0.2), sk=0.1, angle=-90, n=30, inkw=1.6, inkop=0.5, hi=0.35))
    for row in (0.2, 0.48):
        for k in range(4):
            x = -0.48 + k * 0.3
            wx, wy = P(x, row + 0.2)
            out.append(painted(D, rect_pts(wx, wy, wx + 0.12 * s, wy + 0.18 * s, 5, seed + 20 + k + int(row * 10), 0.2), ("#9AAAC0", "#4A5A72", "#1E2A3A"), seed + 20 + k + int(row * 10), sk=0.2, n=2, inkw=1, hi=0.5))
            out.append(pline([(wx + 0.06 * s, wy), (wx + 0.06 * s, wy + 0.18 * s)], STONE[0], 1.4, seed + k, 0.8, 1))
            out.append(pline([(wx, wy + 0.08 * s), (wx + 0.12 * s, wy + 0.08 * s)], STONE[0], 1.4, seed + k, 0.8, 1))
    for y in (0.4, 0.72):
        out.append(pline([P(-0.6, y), P(0.6, y)], "#B8A07A", 2, seed + int(y * 10), 0.6, 1))
    roof = [P(-0.64, 0.78), P(-0.5, 1.26), P(0.5, 1.26), P(0.64, 0.78)]
    out.append(f'<path d="{smooth_closed(poly_pts(roof, 12, seed + 4, 0.3))}" fill="{D.lin([(0, SLATE[0]), (1, SLATE[2])])}"/>')
    for k in range(6):
        y = 0.82 + k * 0.08
        out.append(pline([P(-0.62 + k * 0.02, y), P(0.62 - k * 0.02, y)], "#2A3444", 1, seed + k, 0.35, 1))
    out.append(ink(smooth_closed(roof), "#1E2A3A", 1.6, seed + 5, 1, 0.7))
    # tall carved dormers
    for k in range(3):
        x = -0.32 + k * 0.32
        d0 = P(x, 0.76)
        dw = 0.13 * s
        dorm = [(d0[0] - dw / 2, d0[1]), (d0[0] - dw / 2, d0[1] - 0.26 * s), (d0[0] - dw * 0.3, d0[1] - 0.3 * s), (d0[0], d0[1] - 0.44 * s), (d0[0] + dw * 0.3, d0[1] - 0.3 * s), (d0[0] + dw / 2, d0[1] - 0.26 * s), (d0[0] + dw / 2, d0[1])]
        out.append(painted(D, dorm, STONE, seed + 30 + k, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(painted(D, rect_pts(d0[0] - dw * 0.28, d0[1] - 0.24 * s, d0[0] + dw * 0.28, d0[1] - 0.04 * s, 4, seed + 33 + k, 0.2), ("#9AAAC0", "#4A5A72", "#1E2A3A"), seed + 33 + k, sk=0.2, n=2, inkw=1, hi=0.5))
        out.append(pline([(d0[0], d0[1] - 0.44 * s), (d0[0], d0[1] - 0.52 * s)], "#3A4454", 1.6, seed + k, 1, 1))
    for x in (-0.46, 0.46):
        c0 = P(x, 1.1)
        out.append(painted(D, rect_pts(c0[0] - 7, c0[1] - 0.3 * s, c0[0] + 7, c0[1], 4, seed + 40 + int(x * 10), 0.2), STONE, seed + 40 + int(x * 10), sk=0.2, n=3, inkw=1.1, hi=0.4))
        out.append(painted(D, rect_pts(c0[0] - 9, c0[1] - 0.32 * s, c0[0] + 9, c0[1] - 0.28 * s, 4, seed + 42, 0.2), STONE, seed + 42, sk=0.2, n=2, inkw=1, hi=0.4))
    # corner turrets
    out.append(cone_turret(D, P(-0.66, 0)[0], wl, P(0, 0.9)[1], 0.26 * s, 0.52 * s, seed + 50))
    out.append(cone_turret(D, P(0.66, 0)[0], wl, P(0, 0.9)[1], 0.26 * s, 0.52 * s, seed + 51))
    return "".join(out)


@design("val-de-loire")
def val_de_loire():
    D = Doc2("fr-vl")
    out = [sky(D, [(0, "#9CC0E0"), (0.6, "#E2EAEE"), (1, "#F6EEDC")], 2501, 420, ["#FFFFFF", "#B8D0E8"], 60, angle=-3, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 470, 230, 260, "#FFF6DC", 0.7))
    for k, (x, y, w) in enumerate(((110, 250, 120), (480, 200, 100))):
        out.append(puff_cloud(D, x, y, w, 2502 + k, op=0.85, rows=1))
    # wooded far bank
    for k in range(16):
        x = -20 + k * 42
        out.append(dab_crown(D, x, 396, 28, 22 + (k % 3) * 6, [("#B8C8A8", "#8AA088", "#5E7A68")], 2503 + k, n=24, size=(4, 8), inkw=0))
    wl = 426
    out.append(sea(D, wl - 4, 610, [(0, "#D8E4E8"), (0.4, "#9AB8C8"), (1, "#5A7E92")], 2520, ["#FFFFFF", "#7A9AAE"], 90))
    cx, s = 206, 158
    c = chateau(D, cx, wl, s, 2521)
    out.append(f'<g transform="translate(0 {2 * wl}) scale(1 -1)" opacity="0.32">{reid(c, "r")}</g>')
    out.append(f'<rect x="0" y="{wl}" width="600" height="190" fill="{D.lin([(0, "#5A7E92", 0.1), (1, "#5A7E92", 0.55)])}"/>')
    out.append(wave_lines(2522, (0, wl + 6, 600, 600), ["#FFFFFF", "#7A9AAE", "#C8D8E0"], 60, (20, 60), 2.0, 2))
    out.append(c)
    out.append(f'<rect x="-10" y="{wl - 6}" width="620" height="18" fill="{D.lin([(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0.35), (1, "#FFFFFF", 0)])}"/>')
    # a willow and a boat on the near bank
    out.append(hill(D, ridge([(-20, 560), (120, 548), (260, 560), (400, 574), (620, 566)], 2524, 3), 620, ("#A8C878", "#6E9A4A", "#3A5E2A"), 2525, inkw=1.2, n=40))
    out.append(grass(2526, (0, 548, 600, 610), ["#4E7A2E", "#8AB050", "#C8D870"], 120, (8, 18)))
    tr = [(548, 560), (544, 470), (530, 400)]
    out.append(taper(catmull(tr, 6), 14, 6, "#5A4A3A"))
    rnd = random.Random(2527)
    for k in range(26):
        x0 = 520 + rnd.uniform(-40, 60)
        y0 = 360 + rnd.uniform(-20, 30)
        L = rnd.uniform(80, 150)
        out.append(taper([(x0, y0), (x0 - 6 + rnd.uniform(-4, 4), y0 + L * 0.5), (x0 - 10 + rnd.uniform(-8, 8), y0 + L)], 6, 1.5, rnd.choice(["#9AB868", "#6E9A4A", "#C8D890", "#4E7A3A"]), 0.85))
    # two swans gliding on the moat
    for k, (x, y, sc) in enumerate(((330, 492, 1.0), (408, 478, 0.8))):
        out.append(f'<path d="{blob(x, y + 12 * sc, 30 * sc, 4 * sc, 2528 + k, 0.1, 10)}" fill="#3A5A6A" opacity="0.25"/>')
        out.append(painted(D, [(x - 28 * sc, y), (x - 6 * sc, y - 14 * sc), (x + 22 * sc, y - 10 * sc), (x + 30 * sc, y - 2 * sc), (x + 22 * sc, y + 8 * sc), (x - 20 * sc, y + 8 * sc)], ("#FFFFFF", "#F2F2EE", "#B8B8B4"), 2529 + k, sk=0.2, n=4, inkw=1.3, hi=0.5))
        out.append(taper(catmull([(x - 18 * sc, y - 4 * sc), (x - 26 * sc, y - 24 * sc), (x - 20 * sc, y - 40 * sc), (x - 28 * sc, y - 44 * sc)], 6), 7 * sc, 5 * sc, "#F6F6F2"))
        out.append(ink(smooth_open(catmull([(x - 18 * sc, y - 4 * sc), (x - 26 * sc, y - 24 * sc), (x - 20 * sc, y - 40 * sc)], 6)), "#9A9A96", 1, 2531 + k, 1, 0.6))
        out.append(f'<path d="{pd([(x - 28 * sc, y - 46 * sc), (x - 40 * sc, y - 42 * sc), (x - 28 * sc, y - 40 * sc)])}" fill="#F2702A"/>')
        out.append(f'<circle cx="{x - 25 * sc:.1f}" cy="{y - 44 * sc:.1f}" r="{1.6 * sc:.1f}" fill="#1A1A1A"/>')
    # lettering
    out.append(letters(D, 300, 118, "Val de Loire", SERIF_IT, 112, "#2A3A5A", ["#3E5A8A", "#141E36", "#5A7AAA"], 2531, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#C8D8F0"))
    out.append(ruled(300, 162, "LE JARDIN DE LA FRANCE", "#5A6A3A", font=JOS, size=19, ls=5, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 2532)


# ================================================================ 26. Le 14 juillet — bal et feu d'artifice
@design("le-14-juillet")
def le_14_juillet():
    D = Doc2("fr-14")
    out = [sky(D, [(0, "#0E1436"), (0.7, "#22305E"), (1, "#3E3A6A")], 2601, 600, ["#2A3A6E", "#0A0E26"], 80, angle=-3, sop=(0.05, 0.14))]
    rnd = random.Random(2602)
    for _ in range(40):
        out.append(f'<circle cx="{rnd.uniform(10, 590):.0f}" cy="{rnd.uniform(10, 400):.0f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    # fireworks in blue, white and red
    for k, (x, y, r, col, c2) in enumerate(((150, 282, 88, "#5A8AF0", "#FFFFFF"), (320, 262, 100, "#FFFFFF", "#F6D86A"), (480, 300, 82, "#F0504A", "#FFC8A0"), (240, 352, 46, "#F0504A", None), (420, 362, 42, "#5A8AF0", None))):
        out.append(hg.firework(D, x, y, r, col, 2603 + k, rays=24 if r > 60 else 16, col2=c2, w=3.4 if r > 60 else 2.4))
    for k, (x0, y0, x1, y1) in enumerate(((150, 420, 150, 290), (320, 420, 322, 272), (480, 420, 478, 310))):
        out.append(taper([(x0, y0), (x1 + 4, (y0 + y1) / 2), (x1, y1 + 20)], 0.5, 2, "#FFE8A0", 0.35))
    # village roofs and the church in silhouette, lit windows
    sil = [(-10, 470), (-10, 430), (40, 430), (60, 412), (80, 430), (120, 430), (120, 404), (150, 386), (180, 404), (180, 432), (230, 432), (250, 414), (270, 432),
           (300, 432), (300, 380), (306, 380), (306, 330), (318, 300), (330, 330), (330, 380), (336, 380), (336, 432), (380, 432), (400, 410), (420, 432), (460, 432),
           (460, 402), (490, 386), (520, 402), (520, 430), (560, 430), (580, 414), (610, 430), (610, 470)]
    out.append(f'<path d="{pd(sil)}" fill="#141836"/>')
    out.append(f'<path d="M 318 300 l 0 -12 M 312 292 l 12 0" stroke="#141836" stroke-width="2.4"/>')
    for _ in range(18):
        x = rnd.uniform(0, 600)
        y = rnd.uniform(414, 446)
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="5" height="7" fill="#FFD890" opacity="0.85"/>')
    # the square: plane-tree silhouettes, bunting, paper lanterns and the crowd
    out.append(f'<path d="M -10 466 L 610 466 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#2A2440"), (1, "#3E2E3A")])}"/>')
    out.append(soft_glow(D, 300, 520, 300, "#FFB070", 0.35))
    out.append(flag_string(D, 20, 380, 580, 380, 50, 13, [BLEU[1], "#FFFFFF", ROUGE[1]], 2610, size=24, rope="#C8B898"))
    for k in range(6):
        x = 70 + k * 92
        y = 400 + 48 * 4 * ((x - 20) / 560) * (1 - (x - 20) / 560) + 34
        col = [ROUGE[1], BLEU[1], "#F6C21C"][k % 3]
        out.append(pline([(x, y - 20), (x, y - 8)], "#C8B898", 1.4, 2620 + k, 1, 1))
        out.append(soft_glow(D, x, y + 6, 30, lt(col, 0.4), 0.6))
        out.append(painted(D, blob_pts(x, y + 6, 14, 16, 2621 + k, 0.04, 14), pal3(col, 0.45, 0.35), 2621 + k, sk=0.2, n=4, inkw=1.2, hi=0.6))
        for j in (-6, 0, 6):
            out.append(pline([(x - 13, y + 6 + j), (x + 13, y + 6 + j)], dk(col, 0.3), 0.9, 2630 + k, 0.5, 1))
    crowd = []
    for k in range(13):
        x = 20 + k * 46 + rnd.uniform(-8, 8)
        h = rnd.uniform(96, 128)
        crowd.append(figures.person(x, 620, h, "stand_back", 1, palette="silhouette:#1A1428", seed=2640 + k, rim="#FFB070", light=1, shadow=0))
    out.append("".join(crowd))
    out.append(figures.person(400, 620, 150, "child_on_shoulders", 1, palette="silhouette:#1A1428", seed=2660, rim="#FFB070", light=1, shadow=0))
    # lettering
    out.append(letters(D, 300, 124, "Le 14 juillet", SERIF_IT, 106, "#FFF4E0", ["#FFFFFF", "#F2D8C8"], 2661, max_w=440,
                       shadow="#0A0E26", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 168, "BAL ET FEU D’ARTIFICE", "#F6D86A", font=JOS, size=18, ls=5, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 2662, "#0A0E26")


# ================================================================ 27. Porte-bonheur — le muguet du 1er mai
def muguet_sprig(D, x, base, h, seed, lean=0.0, bells=8):
    """A sprig of lily of the valley: an arching green stem with a row of nodding white bells."""
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    stem = catmull([(x, base), (x + lean * h * 0.3, base - h * 0.55), top, (top[0] + h * 0.22, top[1] + h * 0.06)], 8)
    out = [taper(stem, 4.4, 2, "#5E8A3E")]
    n = len(stem)
    for k in range(bells):
        i = int(n * 0.35 + k * (n * 0.62) / bells)
        i = min(i, n - 1)
        sx, sy = stem[i]
        r = 13 - k * 0.6
        bx, by = sx + rnd.uniform(-2, 2), sy + 16 + r * 0.6
        out.append(pline([(sx, sy), (sx + 1, (sy + by) / 2), (bx, by - r)], "#6E9A4A", 1.4, seed + k, 1, 1))
        bell = [(bx - r * 0.9, by + r * 0.4), (bx - r * 0.95, by - r * 0.2), (bx - r * 0.5, by - r * 0.95), (bx + r * 0.5, by - r * 0.95), (bx + r * 0.95, by - r * 0.2),
                (bx + r * 0.9, by + r * 0.4), (bx + r * 0.6, by + r * 0.62), (bx + r * 0.3, by + r * 0.42), (bx, by + r * 0.66), (bx - r * 0.3, by + r * 0.42), (bx - r * 0.6, by + r * 0.62)]
        out.append(painted(D, bell, ("#FFFFFF", "#F6F8F0", "#B8C8B0"), seed + 10 + k, sdir=(0.6, 0.7), sk=0.22, n=3, inkw=1.2, inkop=0.6, hi=0.6))
    return "".join(out)


def ladybird(D, x, y, s, seed, rot_=0):
    out = [painted(D, rot(blob_pts(x, y, s, s * 0.85, seed, 0.03, 14), x, y, rot_), ("#FF7A6A", "#E0201A", "#7A0A06"), seed, sk=0.25, n=3, inkw=1.2, hi=0.6)]
    hx, hy = rot([(x - s * 0.95, y)], x, y, rot_)[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{s * 0.42:.1f}" fill="#1A1A1A"/>')
    a, b = rot([(x - s * 0.7, y), (x + s, y)], x, y, rot_)
    out.append(pline([a, b], "#1A1A1A", 1.2, seed, 0.9, 1))
    for (dx, dy) in ((-0.2, -0.45), (0.35, -0.4), (-0.2, 0.45), (0.35, 0.4), (0.7, 0)):
        px, py = rot([(x + dx * s, y + dy * s)], x, y, rot_)[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{s * 0.16:.1f}" fill="#1A1A1A"/>')
    return "".join(out)


@design("porte-bonheur")
def porte_bonheur():
    D = Doc2("fr-mu")
    out = [paper(D.nid(), "#F2F4E6", "#6A7A5A", 2701)]
    out.append(blooms(2702, ["#D8E8C8", "#E8F0DC", "#C8DCB8"], 7, (0, 0, 600, 600), (100, 190), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 380, 280, "#FFFFFF", 0.6))
    cx, base = 300, 556
    # broad leaves fanning out behind the sprigs
    for k, (dx, a, L, W) in enumerate(((-30, -128, 270, 62), (34, -52, 262, 60), (-10, -104, 300, 56))):
        out.append(leaf_simple(D, cx + dx * 0.4, base, L, W, a, ("#A8D88A", "#4E9A4A", "#1E5A2A"), 2703 + k, inkw=1.8))
    # arching sprigs of bells, out to both sides
    for k, (dx, h, lean, nb) in enumerate(((-24, 300, -0.42, 10), (-6, 330, -0.14, 11), (12, 316, 0.1, 10), (26, 270, 0.4, 9))):
        out.append(muguet_sprig(D, cx + dx * 0.3, base - 30, h, 2710 + k * 20, lean=lean, bells=nb))
    out.append(leaf_simple(D, cx + 10, base, 250, 44, -84, ("#B8E09A", "#5EAA5A", "#2A6A34"), 2706, inkw=1.8))
    # ribbon bow
    rb = ROUGE
    by = 470
    for sg in (-1, 1):
        loop = [(cx, by), (cx + sg * 36, by - 30), (cx + sg * 60, by - 18), (cx + sg * 54, by + 10), (cx + sg * 20, by + 8)]
        out.append(painted(D, loop, rb, 2750 + sg, sk=0.25, n=6, inkw=1.5, hi=0.5))
        tail = [(cx, by + 4), (cx + sg * 14, by + 56), (cx + sg * 36, by + 78), (cx + sg * 42, by + 64), (cx + sg * 12, by + 4)]
        out.append(painted(D, tail, rb, 2752 + sg, sk=0.25, n=5, inkw=1.4, hi=0.4))
    out.append(painted(D, rect_pts(cx - 34, by - 10, cx + 34, by + 10, 8, 2754, 0.3), rb, 2754, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(painted(D, blob_pts(cx, by, 13, 12, 2755, 0.05, 10), rb, 2755, sk=0.2, n=3, inkw=1.3, hi=0.5))
    # a ladybird for extra luck, and one fallen bell
    out.append(ladybird(D, 196, 360, 13, 2756, rot_=-50))
    # lettering
    out.append(letters(D, 300, 128, "Porte-bonheur", SERIF_IT, 102, "#2E6A3A", ["#3E8A4E", "#1A4A26", "#5AAA6A"], 2758, max_w=450,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#C8E8C8"))
    out.append(ruled(300, 174, "LE MUGUET DU 1ER MAI", ROUGE[2], font=JOS, size=19, ls=5, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 2759)


# ================================================================ 28. Papi — le potager
def lettuce(D, x, y, r, seed):
    out = [cast(D, x + 3, y + r * 0.5, r * 1.1, r * 0.25, strength=0.35, seed=seed)]
    rnd = random.Random(seed)
    for k in range(9):
        a = math.radians(-180 + k * 22.5)
        lx, ly = x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.32
        out.append(painted(D, rot(blob_pts(lx, ly, r * 0.6, r * 0.38, seed + k, 0.18, 12), lx, ly, math.degrees(a) + 90), ("#D8F0A0", "#8AC04E", "#3E7A2A"), seed + k, sk=0.22, n=3, inkw=1, inkop=0.5, hi=0.45))
    out.append(painted(D, blob_pts(x, y - r * 0.12, r * 0.42, r * 0.3, seed + 20, 0.15, 12), ("#F0FAC8", "#C8E07A", "#7AA03E"), seed + 20, sk=0.15, n=3, inkw=1, hi=0.5))
    return "".join(out)


def tomato_plant(D, x, base, h, seed):
    """A staked tomato plant: a cane, the stems tied on, leaves and trusses of red and green tomatoes."""
    rnd = random.Random(seed)
    out = [taper([(x, base + 4), (x + 2, base - h)], 5, 4, "#B8945A")]
    for k in range(7):
        y = base - h * (0.15 + k * 0.12)
        sg = 1 if k % 2 else -1
        out.append(leaf_simple(D, x, y, h * 0.24, h * 0.07, -90 + sg * 60 + rnd.uniform(-10, 10), LEAFG, seed + k, inkw=0.9))
    for k in range(4):
        y = base - h * (0.25 + k * 0.17)
        sg = -1 if k % 2 else 1
        for j in range(3):
            col = ("#FF8A6A", "#E0301E", "#7A0E06") if j < 2 or k < 2 else ("#C8E08A", "#7AAA3A", "#3E6A1A")
            out.append(painted(D, blob_pts(x + sg * (10 + j * 9), y + j * 6, 8, 7.4, seed + 30 + k * 3 + j, 0.04, 12), col, seed + 30 + k * 3 + j, sk=0.2, n=2, inkw=1, hi=0.5))
    for k in range(3):
        y = base - h * (0.3 + k * 0.25)
        out.append(pline([(x - 4, y), (x + 6, y + 2)], "#E8DCC0", 2, seed + k, 0.9, 1))
    return "".join(out)


def watering_can(D, cx, base, w, seed):
    """A galvanised watering can (arrosoir): oval body, long spout with a rose, a hoop handle."""
    h = w * 0.62
    out = [cast(D, cx + 6, base + 2, w * 0.6, 7, strength=0.4, seed=seed)]
    out.append(taper([(cx + w * 0.3, base - h * 0.35), (cx + w * 0.7, base - h * 0.85), (cx + w * 0.86, base - h * 1.05)], 9, 6, "#8A949E"))
    out.append(painted(D, rot(blob_pts(cx + w * 0.9, base - h * 1.08, 9, 7, seed + 1, 0.05, 10), cx + w * 0.9, base - h * 1.08, -40), ZINC, seed + 1, sk=0.2, n=2, inkw=1.2, hi=0.5))
    body = [(cx - w * 0.42, base - h), (cx + w * 0.38, base - h), (cx + w * 0.42, base - h * 0.2), (cx + w * 0.36, base), (cx - w * 0.36, base), (cx - w * 0.44, base - h * 0.2)]
    out.append(painted(D, body, ("#E8EEF2", "#A8B2BC", "#5A646E"), seed, sdir=(1, 0.3), sk=0.2, angle=-90, n=14, inkw=1.8, hi=0.5))
    for y in (0.3, 0.7):
        out.append(pline([(cx - w * 0.43, base - h * y), (cx + w * 0.4, base - h * y)], "#6A747E", 1.6, seed + int(y * 10), 0.6, 1))
    out.append(ink(smooth_open([(cx - w * 0.3, base - h), (cx - w * 0.1, base - h * 1.5), (cx + w * 0.2, base - h)]), "#6A747E", 5, seed + 3, 1, 1))
    out.append(ink(smooth_open([(cx - w * 0.3, base - h), (cx - w * 0.1, base - h * 1.5), (cx + w * 0.2, base - h)]), "#C8D0D8", 1.6, seed + 4, 1, 0.8))
    return "".join(out)


@design("papi")
def papi():
    D = Doc2("fr-pa")
    out = [sky(D, [(0, "#A8CCE8"), (1, "#E8F0E0")], 2801, 300, ["#FFFFFF", "#9AC0E0"], 50, angle=-3, sop=(0.05, 0.14))]
    out.append(puff_cloud(D, 470, 238, 120, 2802, op=0.85, rows=1))
    # garden wall, the shed with its blue door, a fruit tree
    out.append(hill(D, ridge([(-20, 300), (200, 292), (400, 300), (620, 290)], 2803, 3), 340, ("#C8D8A8", "#9AB078", "#5E7A48"), 2804, inkw=0, n=20))
    out.append(painted(D, rect_pts(-10, 286, 610, 318, 30, 2805, 0.6), STONE, 2805, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.4, hi=0.4))
    sx = 452
    out.append(painted(D, rect_pts(sx, 222, sx + 110, 318, 12, 2806, 0.5), ("#D8B890", "#A8805A", "#5A3E22"), 2806, sdir=(1, 0.3), sk=0.15, angle=-90, n=14, inkw=1.6, hi=0.3))
    out.append(wood_planks(D, 222, 318, 2807, ("#D8B890", "#A8805A", "#5A3E22"), 6, vertical=True, x0=sx, x1=sx + 110))
    out.append(painted(D, [(sx - 10, 228), (sx + 55, 196), (sx + 120, 228)], ("#E88A5A", "#C0582E", "#7A2E14"), 2808, sk=0.2, n=8, inkw=1.6, hi=0.3))
    out.append(painted(D, rect_pts(sx + 34, 246, sx + 76, 318, 8, 2809, 0.3), PROV, 2809, sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.4))
    out.append(f'<circle cx="{sx + 70}" cy="284" r="2.4" fill="#2A2A2A"/>')
    out.append(taper([(120, 316), (126, 250)], 10, 7, "#6A4A32"))
    out.append(dab_crown(D, 126, 236, 66, 42, [("#B8D88A", "#7AAA4E", "#3E6A2A")], 2810, n=80, size=(5, 9), inkw=1.2))
    for k in range(7):
        a = k * 0.9
        out.append(painted(D, blob_pts(126 + math.cos(a) * 44, 238 + math.sin(a) * 24, 6, 6, 2811 + k, 0.05, 10), ("#FFB870", "#E8701E", "#8A3008"), 2811 + k, sk=0.2, n=2, inkw=0.9, hi=0.5))
    # the beds: dark earth in rows receding
    out.append(f'<path d="M -10 316 L 610 316 L 610 610 L -10 610 Z" fill="#8A6A44"/>')
    rows = [(330, 344, 0.55), (360, 382, 0.7), (402, 432, 0.85), (456, 500, 1.0)]
    for k, (y0, y1, sc) in enumerate(rows):
        bed = f"M -10 {y0} L 610 {y0 - 4} L 610 {y1} L -10 {y1 + 4} Z"
        out.append(f'<path d="{bed}" fill="#5A3E24"/>')
        out.append(strokes(D.nid(), bed, (-40, y0 - 4, 610, y1 + 4), ["#7A5A3A", "#3E2814", "#9A7A54"], 2812 + k, n=60, angle=-2, length=(10, 40), width=(1, 3), opacity=(0.3, 0.6)))
    # lettuces, leeks... front row bigger
    for i in range(7):
        out.append(lettuce(D, 30 + i * 90, 340, 14, 2820 + i))
    for i in range(11):
        x = 10 + i * 58
        for j in range(3):
            out.append(taper([(x + j * 6 - 6, 380), (x + j * 6 - 8 + j * 3, 350)], 3, 1.5, "#6E9A5A"))
    out.append(tomato_plant(D, 90, 470, 150, 2830))
    out.append(tomato_plant(D, 200, 470, 160, 2831))
    for i in range(5):
        out.append(lettuce(D, 300 + i * 66, 476, 24, 2840 + i))
    # straw hat on the cane, watering can, wheelbarrow handle
    out.append(painted(D, ell_pts(203, 318, 34, 9, 0, 360, 20), ("#FFE6A0", "#E2B65A", "#9A7A2A"), 2850, sk=0.2, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(203, 308, 18, 12, 2851, 0.05, 12), ("#FFE6A0", "#E2B65A", "#9A7A2A"), 2851, sk=0.2, n=6, inkw=1.4, hi=0.4))
    out.append(taper([(186, 314), (220, 314)], 4, 4, "#2F5AA6"))
    out.append(watering_can(D, 120, 576, 88, 2852))
    out.append(wicker_basket(D, 300, 548, 54, 12, 590, 44, 2857))
    for k, (x, y) in enumerate(((282, 542), (304, 538), (324, 544), (292, 528), (314, 526))):
        out.append(tomato_fr(D, x, y, 12, 2858 + k))
    out.append(wicker_basket(D, 300, 548, 54, 12, 590, 44, 2857) if False else "")
    # a robin on the handle of the spade
    out.append(taper([(486, 600), (500, 470)], 8, 6, "#B8945A"))
    out.append(painted(D, rect_pts(488, 560, 514, 610, 6, 2853, 0.2), ZINC, 2853, sk=0.2, n=2, inkw=1.2, hi=0.5))
    out.append(taper([(488, 468), (516, 468)], 8, 8, "#8A6A3A"))
    out.append(sparrow(D, 512, 466, 48, 2854, flip=1, twig=False))
    # lettering
    out.append(letters(D, 300, 140, "Papi", SERIF_IT, 140, "#2E5A2A", ["#3E7A3A", "#1A3A16", "#5A9A4A"], 2855, max_w=300,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#C8E8B8"))
    out.append(ruled(300, 186, "LE POTAGER DE PAPI", "#8A3A14", font=JOS, size=19, ls=5, line_w=30, gap=12, max_w=380))
    return finish_f(D, out, 2856)


# ================================================================ 29. Ma petite maison — a stone mas in Provence
def canal_roof(D, x0, x1, y_top, y_bot, seed):
    """A Provençal roof of curved canal tiles: rows of rounded tile crowns, a génoise frieze under the eave."""
    rnd = random.Random(seed)
    d = pd([(x0 - 14, y_bot), (x0 + 30, y_top), (x1 - 30, y_top), (x1 + 14, y_bot)])
    out = [f'<path d="{d}" fill="#B8603A"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    x = x0 - 20
    while x < x1 + 20:
        c = rnd.choice(["#E8905A", "#D8784A", "#C86A3A", "#F0A070", "#B85A30"])
        inner.append(taper([(x, y_top - 4), (x + 1, y_bot + 4)], 13, 15, c))
        inner.append(taper([(x - 3, y_top - 4), (x - 2, y_bot + 4)], 3, 4, "#FFD0A8", 0.6))
        inner.append(taper([(x + 7, y_top - 4), (x + 8, y_bot + 4)], 2, 3, "#6A2A10", 0.5))
        x += 17
    for y in range(int(y_top) + 12, int(y_bot), 14):
        inner.append(pline([(x0 - 20, y), (x1 + 20, y)], "#7A3418", 1.2, y, 0.4, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#6A2A10", 1.8, seed, 1, 0.7))
    for k in range(2):
        out.append(taper([(x0 - 14, y_bot + 4 + k * 7), (x1 + 14, y_bot + 4 + k * 7)], 6, 6, "#E8D4B0" if k == 0 else "#D8B890"))
        for i in range(int((x1 - x0 + 28) / 12)):
            out.append(f'<path d="{blob(x0 - 10 + i * 12, y_bot + 4 + k * 7, 5, 3, seed + i + k * 50, 0.1, 8)}" fill="{"#C86A3A" if k == 0 else "#B85A30"}"/>')
    return "".join(out)


def shutter(D, x, y, w, h, seed, pal=PROV, open_=False):
    """A louvred Provençal shutter (persienne): frame and slanted slats, a little pale wear."""
    pts = rect_pts(x, y, x + w, y + h, 10, seed, 0.4)
    out = [painted(D, pts, pal, seed, sdir=(1, 0.2), sk=0.15, angle=-90, n=10, inkw=1.6, hi=0.4)]
    for k in range(int((h - 16) / 10)):
        yy = y + 10 + k * 10
        out.append(taper([(x + 5, yy), (x + w - 5, yy + 3)], 3, 3, pal[2], 0.6))
        out.append(taper([(x + 5, yy - 2), (x + w - 5, yy + 1)], 1.4, 1.4, pal[0], 0.7))
    out.append(pline([(x + 4, y + h * 0.5), (x + w - 4, y + h * 0.5)], pal[2], 3, seed, 0.6, 1))
    return "".join(out)


def cat_sleeping(D, cx, cy, s, seed, pal=("#F6C890", "#E0903A", "#8A4A14")):
    body = blob_pts(cx, cy, s, s * 0.55, seed, 0.05, 16)
    out = [cast(D, cx + 4, cy + s * 0.5, s * 1.1, s * 0.15, strength=0.35, seed=seed)]
    out.append(painted(D, body, pal, seed, sk=0.25, n=8, inkw=1.4, hi=0.4))
    head = blob_pts(cx - s * 0.75, cy + s * 0.05, s * 0.42, s * 0.36, seed + 1, 0.05, 12)
    out.append(painted(D, head, pal, seed + 1, sk=0.2, n=4, inkw=1.3, hi=0.4))
    for sg in (-1, 1):
        ex = cx - s * 0.75 + sg * s * 0.22
        out.append(painted(D, [(ex - s * 0.12, cy - s * 0.2), (ex, cy - s * 0.48), (ex + s * 0.12, cy - s * 0.22)], pal, seed + 2 + sg, sk=0.2, n=2, inkw=1.1, hi=0.3))
        out.append(pline([(ex - s * 0.1, cy + s * 0.04), (ex, cy + s * 0.08), (ex + s * 0.08, cy + s * 0.04)], "#3A2010", 1.4, seed + sg, 0.9, 1))
    for k in range(4):
        out.append(taper([(cx - s * 0.1 + k * s * 0.25, cy - s * 0.48), (cx + k * s * 0.25, cy - s * 0.2)], 3, 1, pal[2], 0.6))
    out.append(taper(catmull([(cx + s * 0.9, cy + s * 0.2), (cx + s * 0.6, cy + s * 0.55), (cx - s * 0.4, cy + s * 0.55)], 6), s * 0.16, s * 0.12, pal[1]))
    return "".join(out)


@design("ma-petite-maison")
def ma_petite_maison():
    D = Doc2("fr-mp")
    out = [sky(D, [(0, "#5AA0DA"), (0.5, "#C8E4F2"), (1, "#E8F2F4")], 2901, 600, ["#FFFFFF", "#7AB8E8"], 60, angle=-3, sop=(0.05, 0.14))]
    out.append(hill(D, ridge([(-20, 470), (150, 456), (300, 466), (450, 452), (620, 462)], 2986, 4), 600, ("#C8D8A8", "#9AB078", "#5E7A48"), 2987, inkw=0, n=30))
    # the house: warm stone walls, canal-tile roof, blue shutters and door
    wall = rect_pts(70, 250, 530, 560, 30, 2902, 0.8)
    out.append(painted(D, wall, ("#F6E2C0", "#E2C49A", "#A88A60"), 2902, sdir=(1, 0.3), sk=0.08, angle=-90, n=60, inkw=1.6, hi=0.3))
    wd = smooth_closed(wall)
    wid = D.clip(f'<path d="{wd}"/>')
    rnd = random.Random(2903)
    st = []
    for _ in range(46):
        x, y = rnd.uniform(70, 530), rnd.uniform(250, 560)
        st.append(f'<path d="{blob(x, y, rnd.uniform(14, 26), rnd.uniform(8, 13), rnd.randint(1, 9999), 0.15, 10)}" fill="none" stroke="#B89A6E" stroke-width="1.4" opacity="0.5"/>')
        st.append(f'<path d="{blob(x, y, rnd.uniform(12, 22), rnd.uniform(6, 11), rnd.randint(1, 9999), 0.15, 10)}" fill="{rnd.choice(["#F2D8B0", "#E8C898", "#D8B888"])}" opacity="0.4"/>')
    st.append(shade_over(D, wd, "#5A3A1A", 0.25, 0, 0, 1, 0, 0.6))
    out.append(f'<g {wid}>{"".join(st)}</g>')
    out.append(canal_roof(D, 70, 530, 210, 258, 2904))
    # chimney
    out.append(painted(D, rect_pts(430, 172, 462, 222, 8, 2905, 0.3), ("#F6E2C0", "#E2C49A", "#A88A60"), 2905, sk=0.2, n=4, inkw=1.4, hi=0.3))
    out.append(painted(D, rect_pts(424, 166, 468, 176, 8, 2906, 0.3), ("#E8905A", "#C86A3A", "#7A3418"), 2906, sk=0.2, n=3, inkw=1.2, hi=0.3))
    # windows with open shutters, door in the middle
    for k, wx in enumerate((150, 410)):
        out.append(painted(D, rect_pts(wx - 34, 300, wx + 34, 392, 10, 2907 + k, 0.4), ("#4A5A6A", "#2A3440", "#121820"), 2907 + k, sk=0.1, n=4, inkw=1.6, hi=0.2))
        out.append(f'<path d="{hg.org_rect(wx - 30, 304, 28, 84, 2909 + k, 0.4, 10, 2)}" fill="#F6F0E0" opacity="0.18"/>')
        out.append(pline([(wx, 300), (wx, 392)], "#F6EEDC", 3, 2911 + k, 0.9, 1))
        out.append(pline([(wx - 34, 346), (wx + 34, 346)], "#F6EEDC", 3, 2913 + k, 0.9, 1))
        out.append(shutter(D, wx - 74, 296, 38, 100, 2915 + k))
        out.append(shutter(D, wx + 36, 296, 38, 100, 2917 + k))
        out.append(painted(D, rect_pts(wx - 42, 392, wx + 42, 402, 10, 2919 + k, 0.3), STONE, 2919 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
        # a pot of red geraniums on each sill
        out.append(painted(D, [(wx - 22, 392), (wx + 22, 392), (wx + 16, 372), (wx - 16, 372)][::-1], ("#F2A27A", "#C8643C", "#7A3218"), 2921 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
        for j in range(5):
            out.append(painted(D, blob_pts(wx - 18 + j * 9, 362 - (j % 2) * 6, 7, 6, 2923 + k * 5 + j, 0.2, 8), ("#FF7A6A", "#E0281E", "#8A0A0A"), 2923 + k * 5 + j, sk=0.2, n=2, inkw=0.9, hi=0.4))
    # the door, with a little arched fanlight
    dx0, dx1, dy0 = 252, 348, 424
    out.append(painted(D, rect_pts(dx0 - 10, dy0 - 10, dx1 + 10, 562, 20, 2930, 0.5), STONE, 2930, sk=0.15, n=8, inkw=1.4, hi=0.4))
    door = rect_pts(dx0, dy0, dx1, 562, 16, 2931, 0.4)
    out.append(painted(D, door, PROV, 2931, sdir=(1, 0.2), sk=0.12, angle=-90, n=16, inkw=1.8, hi=0.4))
    out.append(wood_planks(D, dy0 + 4, 560, 2932, PROV, 4, vertical=True, x0=dx0 + 4, x1=dx1 - 4))
    out.append(f'<circle cx="{dx1 - 16}" cy="{dy0 + 70}" r="4" fill="#C8A048" stroke="#7A5A10" stroke-width="1"/>')
    # wisteria over the door
    out.append(taper(catmull([(70, 560), (60, 420), (110, 300), (220, 266), (330, 274), (420, 262)], 8), 6, 3, "#6A4A32"))
    for k in range(9):
        x = 90 + k * 40 + rnd.uniform(-8, 8)
        y = 268 + rnd.uniform(-4, 10)
        for j in range(8):
            out.append(f'<path d="{blob(x + rnd.uniform(-4, 4), y + j * 6, 5 - j * 0.4, 4 - j * 0.3, rnd.randint(1, 9999), 0.2, 6)}" fill="{rnd.choice(["#B8A0E8", "#9A80D0", "#D8C8F6"])}"/>')
        out.append(leaf_simple(D, x, y - 2, 22, 6, rnd.choice([-20, -160]), LEAFG, 2940 + k, inkw=0.8))
    # lavender in pots by the door, the bench and the cat
    for k, px in enumerate((206, 394)):
        out.append(painted(D, [(px - 26, 516), (px + 26, 516), (px + 20, 566), (px - 20, 566)], ("#F2A27A", "#C8643C", "#7A3218"), 2950 + k, sk=0.2, n=5, inkw=1.5, hi=0.4))
        for j in range(12):
            a = math.radians(-90 + (j - 5.5) * 8)
            L = rnd.uniform(46, 66)
            x1, y1 = px + math.cos(a) * L, 516 + math.sin(a) * L
            out.append(pline([(px + (j - 5.5) * 2, 516), (x1, y1)], "#6E8A5A", 1.4, 2952 + j + k * 20, 0.9, 1))
            for i in range(4):
                t = 0.72 + i * 0.08
                out.append(f'<path d="{blob(px + (x1 - px) * t, 516 + (y1 - 516) * t, 2.6, 3.8, rnd.randint(1, 9999), 0.15, 6)}" fill="{rnd.choice(["#8A6CC8", "#6A4AA8", "#A890D8"])}"/>')
    out.append(painted(D, rect_pts(430, 506, 524, 518, 10, 2980, 0.4), WOOD, 2980, sk=0.2, n=4, inkw=1.4, hi=0.4))
    for x in (440, 514):
        out.append(taper([(x, 518), (x, 552)], 5, 5, "#5E3618"))
    out.append(cat_sleeping(D, 486, 494, 28, 2981))
    # ground: pale gravel
    out.append(f'<path d="M -10 560 L 610 560 L 610 610 L -10 610 Z" fill="#E8D8B8"/>')
    out.append(specks(2982, (0, 560, 600, 600), ["#B89A6E", "#FFFFFF"], 80, (0.8, 2), (0.5, 0.9)))
    out.append(f'<rect x="-10" y="556" width="620" height="8" fill="#7A5A3A" opacity="0.3"/>')
    for x in (30, 572):
        out.append(cypress_fr(D, x, 560, 260, 2983 + x))
    # lettering
    out.append(letters(D, 300, 116, "Ma petite maison", SERIF_IT, 84, "#FFFFFF", ["#FFFFFF", "#E8F2FA"], 2984, max_w=450,
                       shadow="#1E4A7A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 158, "ON EST BIEN CHEZ SOI", "#FFF6E0", font=JOS, size=19, ls=5, line_w=28, gap=12, max_w=380))
    return finish_f(D, out, 2985)


def cypress_fr(D, x, base, h, seed):
    w = h * 0.12
    pts = [(x, base - h)] + [(x + w * math.sin(math.pi * t) ** 0.7 * (1 if True else 1), base - h + h * t) for t in [i / 12 for i in range(1, 12)]] + [(x + w * 0.5, base), (x - w * 0.5, base)] + \
          [(x - w * math.sin(math.pi * t) ** 0.7, base - h + h * t) for t in [i / 12 for i in range(11, 0, -1)]]
    return painted(D, jitter(pts, seed, 1.6), ("#5E8A4A", "#2E5232", "#14281A"), seed, sdir=(1, 0.2), sk=0.25, angle=-80, n=30, inkw=1.4, hi=0.35)


# ================================================================ 30. Bonne fête — Maman: a posy of wildflowers and a pasta necklace
def poppy(D, cx, cy, r, seed, rot_=0):
    rnd = random.Random(seed)
    out = []
    for k in range(4):
        a = math.radians(k * 90 + 45 + rot_)
        out.append(painted(D, blob_pts(cx + math.cos(a) * r * 0.42, cy + math.sin(a) * r * 0.42, r * 0.66, r * 0.58, seed + k, 0.14, 12), ("#FF7A5A", "#E0261A", "#8A0A06"), seed + k, sk=0.25, n=3, inkw=1.1, inkop=0.5, hi=0.45))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.28:.1f}" fill="#1A1A1A"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.36:.1f}" cy="{cy + math.sin(a) * r * 0.36:.1f}" r="1.6" fill="#2A2A2A"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.14:.1f}" fill="#6A7A4A"/>')
    return "".join(out)


def daisy_fr(D, cx, cy, r, seed):
    out = []
    for k in range(14):
        a = math.radians(k * 360 / 14 + seed)
        bx, by = cx + math.cos(a) * r * 0.3, cy + math.sin(a) * r * 0.3
        tx, ty = cx + math.cos(a) * r, cy + math.sin(a) * r
        out.append(taper([(bx, by), (tx, ty)], r * 0.22, r * 0.18, "#FFFFFF"))
        out.append(pline([(bx, by), (tx, ty)], "#C8C8B8", 0.9, seed + k, 0.5, 1))
    out.append(painted(D, blob_pts(cx, cy, r * 0.3, r * 0.3, seed, 0.05, 10), ("#FFE06A", "#F2B81C", "#A8780A"), seed, sk=0.2, n=2, inkw=1, hi=0.5))
    return "".join(out)


def cornflower(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    out = []
    for k in range(9):
        a = math.radians(k * 40 + rnd.uniform(-8, 8))
        tx, ty = cx + math.cos(a) * r, cy + math.sin(a) * r
        pts = [(cx, cy), (tx + math.cos(a + 1.6) * r * 0.25, ty + math.sin(a + 1.6) * r * 0.25), (tx, ty), (tx + math.cos(a - 1.6) * r * 0.25, ty + math.sin(a - 1.6) * r * 0.25)]
        out.append(f'<path d="{smooth_closed(pts)}" fill="{rnd.choice(["#4A7AE8", "#2E5AC8", "#6A9AF0"])}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.25:.1f}" fill="#1E2E7A"/>')
    return "".join(out)


@design("bonne-fete")
def bonne_fete():
    D = Doc2("fr-bf")
    out = [paper(D.nid(), "#FBEAE4", "#A87A6A", 3001)]
    out.append(blooms(3002, ["#F6D0C8", "#FFF0E8", "#F2C0B8"], 7, (0, 0, 600, 600), (100, 190), (0.1, 0.18)))
    # a child's card, propped on the left, crayon heart and "Maman"
    card = rot(rect_pts(60, 300, 236, 520, 16, 3003, 0.8), 148, 410, -6)
    out.append(f'<path d="{smooth_closed(card)}" fill="#3A2418" opacity="0.15" transform="translate(7 8)"/>')
    out.append(painted(D, card, ("#FFFFFF", "#FFFCF2", "#D8CCB8"), 3003, sk=0.1, n=10, inkw=1.6, hi=0.3))
    cg = rot([(148, 392)], 148, 410, -6)[0]
    out.append(p_heart(D, cg[0], cg[1], 44, ("#FF9AAA", "#E8405A", "#9A1A30"), 3004, rot_=-6, inkw=1.4))
    rnd = random.Random(3005)
    for _ in range(26):
        x, y = cg[0] + rnd.uniform(-34, 34), cg[1] + rnd.uniform(-30, 30)
        out.append(pline([(x, y), (x + 8, y - 6)], "#C8203A", 1.6, rnd.randint(1, 999), 0.35, 1))
    lab = rot([(148, 476)], 148, 410, -6)[0]
    out.append(f'<text x="{lab[0]:.1f}" y="{lab[1]:.1f}" text-anchor="middle" {SERIF_IT} font-size="{fit_size("Maman", SERIF_IT, 40, 150)}" fill="#2F5AA6" transform="rotate(-6 {lab[0]:.1f} {lab[1]:.1f})">Maman</text>')
    for k, (x, y, c) in enumerate(((84, 330, "#F6C21C"), (212, 324, "#3E9A4E"), (212, 500, "#F6C21C"))):
        out.append(sparkle(*rot([(x, y)], 148, 410, -6)[0], 8, c, 0.9))
    # the wildflower posy: poppies, daisies and cornflowers, wrapped in brown paper with a string bow
    bx, by = 404, 456
    heads = [(-84, -196, "c"), (-44, -232, "p"), (6, -246, "d"), (54, -226, "c"), (96, -188, "p"), (-108, -146, "d"), (-24, -182, "d"), (30, -170, "p"),
             (112, -128, "d"), (-64, -106, "c"), (2, -122, "p"), (74, -112, "c"), (-120, -96, "p"), (128, -76, "c"), (-40, -150, "c")]
    for k, (dx, dy, t) in enumerate(heads):
        out.append(pline([(bx + dx * 0.15, by), (bx + dx * 0.55, by + dy * 0.5), (bx + dx, by + dy)], "#5E8A3E", 2.4, 3006 + k, 1, 1))
    for k, (dx, a) in enumerate(((-70, -130), (70, -50), (-30, -110), (40, -70))):
        out.append(leaf_simple(D, bx + dx * 0.3, by - 60, 70, 9, a, LEAFG, 3020 + k, inkw=1))
    for k, (dx, dy, t) in enumerate(sorted(heads, key=lambda h: h[1])):
        x, y = bx + dx, by + dy
        if t == "p":
            out.append(poppy(D, x, y, 30, 3030 + k, rot_=k * 20))
        elif t == "d":
            out.append(daisy_fr(D, x, y, 26, 3030 + k))
        else:
            out.append(cornflower(D, x, y, 21, 3030 + k))
    wrap = [(bx - 70, by - 70), (bx + 74, by - 74), (bx + 30, by + 80), (bx + 10, by + 96), (bx - 14, by + 96), (bx - 34, by + 80)]
    out.append(painted(D, wrap, ("#E8C890", "#C89A5A", "#7A5428"), 3050, sdir=(1, 0.3), sk=0.2, angle=-70, n=16, inkw=1.8, hi=0.4))
    for k in range(3):
        out.append(pline([(bx - 50 + k * 30, by - 64), (bx - 10 + k * 12, by + 86)], "#9A7240", 1.4, 3051 + k, 0.5, 1))
    out.append(pline([(bx - 36, by + 20), (bx, by + 26), (bx + 34, by + 20)], "#F6F0E0", 3, 3054, 1, 1))
    for sg in (-1, 1):
        out.append(ink(smooth_open([(bx, by + 24), (bx + sg * 20, by + 10), (bx + sg * 26, by + 26), (bx, by + 24)]), "#F6F0E0", 2.6, 3055 + sg, 1, 1))
        out.append(pline([(bx, by + 26), (bx + sg * 10, by + 50)], "#F6F0E0", 2.4, 3057 + sg, 1, 1))
    # the pasta necklace, painted every colour, curled in front
    neck = [(250 + 170 * math.cos(math.radians(a)), 470 + 70 * math.sin(math.radians(a))) for a in range(20, 161, 6)]
    out.append(ink(smooth_open(neck), "#C8382E", 2, 3060, 1, 0.9))
    cols = [ROUGE[1], "#F6C21C", BLEU[1], "#3E9A4E", "#E86AA0", "#F28A2A"]
    for k, (x, y) in enumerate(neck[1:-1]):
        c = cols[k % len(cols)]
        a_ = math.degrees(math.atan2(neck[k + 2][1] - neck[k][1], neck[k + 2][0] - neck[k][0]))
        out.append(painted(D, rot(rect_pts(x - 9, y - 5.5, x + 9, y + 5.5, 4, 3061 + k, 0.3), x, y, a_), pal3(c, 0.35, 0.3), 3061 + k, sk=0.25, n=2, inkw=1.1, hi=0.5))
        for j in (-4, 0, 4):
            out.append(pline(rot([(x + j, y - 5), (x + j, y + 5)], x, y, a_), dk(c, 0.35), 1, 3090 + k, 0.6, 1))
    # lettering
    out.append(letters(D, 300, 140, "Bonne fête", SERIF_IT, 122, "#C8304A", ["#E8506A", "#8A1030", "#F07A8A"], 3100, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC8D0"))
    out.append(ruled(300, 188, "MAMAN, JE T’AIME", BLEU[2], font=JOS, size=19, ls=6, line_w=32, gap=12, max_w=380))
    return finish_f(D, out, 3101)


# ================================================================ END DESIGNS
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
