"""Korea, hand-painted (gouache / storybook) edition: 30 magnets for Korean-American families, K-culture lovers and
travellers who fell for Korea.

Same idiom as the Brasil and Japan sets: warm hanji-paper ground, layered washes with pooled edges, brush strokes
that follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Hero words are
romanized Korean or English (the site fonts carry no Hangul); the few Hangul words (사랑해, 엄마, 할머니, 정) are
painted stroke by stroke as brush calligraphy, never set in a font. Colour story: obangsaek (the five cardinal
colours), dancheong teal and vermilion, celadon jade, persimmon orange, gochujang red and onggi brown on cream hanji.

Run from tools/designs:  python3 korea_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, leaf_simple, branch, wood_planks, heart_d,
                            steam, finish_b, bird_v, p_heart)
from japan_painted import (densify, round_poly, clipped, bark_branch, sakura_petal, long_leaf, snow_rock, chochin,
                           round_dish)
import holidays_gouache as hg
import figures

COL = "korea"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
GOCHU = ("#F2704E", "#C8281E", "#7A0E0A")       # gochujang / chili red
JEOK = ("#F07A62", "#D2382A", "#8A1612")        # obangsaek red
CHEONG = ("#5E86C8", "#1E4A9A", "#0C2458")      # obangsaek blue
HWANG = ("#FFE48A", "#F2BE2A", "#B07E0A")       # obangsaek yellow
DANCHEONG = ("#6AC0AC", "#1E8A78", "#0C4A40")   # palace teal-green
CELADON = ("#CDE4D2", "#9CC4AE", "#5E8A74")
PERSIMMON = ("#FFB46A", "#F0782A", "#A8420E")
ONGGI = ("#8A5A40", "#4E2C1C", "#24120A")
STONE = ("#B8B4AC", "#7E7A74", "#3E3A36")
BASALT = ("#7A7670", "#4A4642", "#22201E")
PINE = ("#6E9A5A", "#2E5A3A", "#123020")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
DARKWOOD = ("#9A6A44", "#5E3820", "#2A160A")
PALEWOOD = ("#F4DAAE", "#DDB078", "#9A6A38")
STEEL = ("#F4F6F8", "#C8CED6", "#7A8494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
RICE = ("#FFFFFF", "#F7F3EA", "#B8B2A8")
CABBAGE = ("#E8F0B0", "#B8D070", "#6A9A3A")
HANJI = "#F3E8D2"

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


lt, dk = hg.lt, hg.dk


# ================================================================ korea toolkit
def L(pts, ox, oy, s=1.0, flip=False):
    """Local -> page coordinates."""
    return [(ox + (-x if flip else x) * s, oy + y * s) for x, y in pts]


def hanji(D, base="#F3E8D2", fleck=FLECK, seed=1, fibres=60, fib_col="#B89A70"):
    """Mulberry paper: paper() plus long, faint fibres."""
    rnd = random.Random(seed)
    out = [paper(D.nid(), base, fleck, seed)]
    f = []
    for _ in range(fibres):
        x, y = rnd.uniform(-20, 620), rnd.uniform(-20, 620)
        a = rnd.uniform(0, 6.28)
        Ls = rnd.uniform(14, 40)
        f.append(f'<path d="M {x:.0f} {y:.0f} q {math.cos(a + 0.6) * Ls * 0.5:.1f} {math.sin(a + 0.6) * Ls * 0.5:.1f} {math.cos(a) * Ls:.1f} {math.sin(a) * Ls:.1f}" '
                 f'stroke="{fib_col}" stroke-width="{rnd.uniform(0.5, 1.1):.1f}" fill="none" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>')
    out.append("".join(f))
    return "".join(out)


def ellipse_d(cx, cy, rx, ry, n=36):
    return smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, n)[:-1])


# ---------------------------------------------------------------- Hangul, painted stroke by stroke (no font)
# Each syllable is drawn in a 100 x 100 box (y down). Strokes are polylines; ("o", cx, cy, rx, ry) is the round ㅇ.
# Only these syllables exist on purpose: every one was checked jamo by jamo.
SYL = {
    # 사 = ㅅ + ㅏ
    "사": [[(40, 14), (34, 44), (22, 68), (8, 84)], [(36, 46), (46, 62), (60, 78)],
           [(74, 6), (74, 50), (75, 94)], [(76, 48), (94, 47)]],
    # 랑 = ㄹ + ㅏ + ㅇ
    "랑": [[(12, 10), (52, 9), (52, 27)], [(14, 27), (52, 27)], [(14, 27), (14, 45), (58, 45)],
           [(72, 2), (72, 30), (72, 58)], [(73, 29), (92, 28)], ("o", 48, 78, 21, 15)],
    # 해 = ㅎ + ㅐ
    "해": [[(32, 6), (34, 18)], [(10, 28), (56, 27)], ("o", 33, 58, 19, 18),
           [(68, 10), (68, 50), (68, 88)], [(69, 48), (85, 48)], [(87, 2), (87, 50), (88, 98)]],
    # 엄 = ㅇ + ㅓ + ㅁ
    "엄": [("o", 32, 30, 19, 17), [(78, 2), (78, 30), (78, 58)], [(56, 30), (77, 30)],
           [(24, 64), (24, 96)], [(24, 64), (78, 64), (76, 96)], [(25, 95), (76, 95)]],
    # 마 = ㅁ + ㅏ
    "마": [[(10, 22), (12, 80)], [(10, 22), (54, 22), (52, 80)], [(12, 79), (52, 79)],
           [(72, 4), (72, 50), (73, 96)], [(73, 50), (94, 49)]],
    # 정 = ㅈ + ㅓ + ㅇ
    "정": [[(8, 12), (50, 11)], [(42, 12), (30, 34), (8, 54)], [(30, 34), (42, 44), (54, 52)],
           [(78, 2), (78, 32), (78, 60)], [(56, 32), (77, 32)], ("o", 46, 80, 23, 15)],
    # 할 = ㅎ + ㅏ + ㄹ
    "할": [[(30, 2), (32, 11)], [(10, 18), (52, 17)], ("o", 31, 36, 15, 12),
           [(70, 0), (70, 28), (70, 56)], [(71, 28), (90, 27)],
           [(18, 62), (80, 61), (80, 78)], [(20, 78), (80, 78)], [(20, 78), (20, 96), (84, 96)]],
    # 머 = ㅁ + ㅓ
    "머": [[(10, 22), (12, 80)], [(10, 22), (56, 22), (54, 80)], [(12, 79), (54, 79)],
           [(84, 4), (84, 50), (85, 96)], [(62, 50), (83, 50)]],
    # 니 = ㄴ + ㅣ
    "니": [[(16, 16), (16, 80), (60, 80)], [(82, 4), (82, 50), (83, 96)]],
}


def _brush_poly(pts, w, taper_end=0.55):
    """Outline of one brush stroke along pts: pressed start, slightly lean middle, lifted end."""
    cp = catmull(pts, 8) if len(pts) > 2 else [(pts[0][0] + (pts[1][0] - pts[0][0]) * t / 10, pts[0][1] + (pts[1][1] - pts[0][1]) * t / 10) for t in range(11)]
    n = len(cp)
    left, right = [], []
    for i, (x, y) in enumerate(cp):
        a, b = cp[max(i - 1, 0)], cp[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ls = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ls, dx / Ls
        t = i / max(1, n - 1)
        k = (1.12 if t < 0.1 else 1.0 - 0.18 * math.sin(math.pi * t)) * (1 - (1 - taper_end) * max(0, (t - 0.82) / 0.18))
        ww = w * k / 2
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    return left + right[::-1], cp


def hangul(D, x, y, size, word, color, seed, w=None, adv=0.96, paper_c="#FFFFFF", dry=True, anchor="middle", shadow=None):
    """Paint a Hangul word as brush strokes. (x, y) = centre / left of the baseline box's top; size = syllable box."""
    rnd = random.Random(seed)
    s = size / 100
    w = w or size * 0.105
    n = len(word)
    total = size * adv * (n - 1) + size
    x0 = x - total / 2 if anchor == "middle" else x
    polys = []
    for i, ch in enumerate(word):
        ox = x0 + i * size * adv
        for st in SYL[ch]:
            if st[0] == "o":
                _, cx, cy, rx, ry = st
                pts = []
                for j in range(42):
                    a = math.radians(-96 + 372 * j / 41)
                    pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
                cp = [(ox + px * s, y + py * s) for px, py in pts]
                left, right = [], []
                for j, (px, py) in enumerate(cp):
                    a = math.radians(-96 + 372 * j / 41)
                    k = 0.62 + 0.42 * abs(math.cos(a))
                    nx, ny = math.cos(a), math.sin(a)
                    ww = w * k / 2
                    left.append((px + nx * ww, py + ny * ww * (ry / rx)))
                    right.append((px - nx * ww, py - ny * ww * (ry / rx)))
                polys.append((left + right[::-1], cp))
            else:
                pts = [(ox + px * s + rnd.uniform(-0.6, 0.6), y + py * s + rnd.uniform(-0.6, 0.6)) for px, py in st]
                polys.append(_brush_poly(pts, w * rnd.uniform(0.94, 1.06)))
    out = []
    if shadow:
        out.append('<g transform="translate(%.1f %.1f)">' % (size * 0.025, size * 0.03)
                   + "".join(f'<path d="{smooth_closed(p)}" fill="{shadow}"/>' for p, _ in polys) + "</g>")
    for p, cp in polys:
        d = smooth_closed(p)
        out.append(f'<path d="{d}" fill="{color}"/>')
        # pressed entry of the brush
        ex, ey = cp[0]
        out.append(f'<path d="{blob(ex, ey, w * 0.6, w * 0.5, seed + int(ex), 0.12, 10)}" fill="{color}"/>')
        if dry:
            st = []
            for _ in range(3):
                off = rnd.uniform(-0.32, 0.32) * w
                a0 = rnd.randint(len(cp) // 2, max(len(cp) // 2, len(cp) - 3))
                seg = cp[a0:]
                if len(seg) < 2:
                    continue
                dx, dy = seg[-1][0] - seg[0][0], seg[-1][1] - seg[0][1]
                Ls = math.hypot(dx, dy) or 1
                nx, ny = -dy / Ls, dx / Ls
                st.append(taper([(px + nx * off, py + ny * off) for px, py in seg], 0.5, rnd.uniform(1.2, 2.6), paper_c, rnd.uniform(0.35, 0.7)))
            out.append(clipped(D, d, st))
    return "".join(out)


# ---------------------------------------------------------------- stoneware and tableware
def onggi(D, cx, base, w, h, seed, lid="dome", snow=False, pal=ONGGI, deco=True, haze=0.0, rim_light=None):
    """Onggi crock: narrow foot, swelling belly, rounded shoulder, short neck; dark glossy glaze with a finger-drawn
    grass motif (jijang) on the shoulder, throwing rings, and a dome lid with a knob (or an upturned bowl lid)."""
    hz = (lambda c: mix(c, "#C8D2E2", haze)) if haze else (lambda c: c)
    rnd = random.Random(seed)
    top = base - h
    mw = w * 0.62                      # mouth width
    pts = []
    prof = [(0.0, 0.46), (0.08, 0.5), (0.3, 0.7), (0.55, 0.88), (0.72, 0.84), (0.85, 0.68), (0.94, 0.56), (1.0, 0.56)]
    for t, k in prof:
        pts.append((cx + w * k / 2 * 1.0, base - h * t))
    body = pts + [(2 * cx - x, y) for x, y in pts[::-1]]
    out = [cast(D, cx + w * 0.12, base + 2, w * 0.6, max(6, h * 0.07), strength=0.42, seed=seed)]
    out.append(painted(D, body, tuple(hz(c) for c in pal), seed, sdir=(0.9, 0.2), sk=0.16, angle=-90, n=int(w * h / 120) + 10,
                       slen=(h * 0.1, h * 0.3), sw=(1, max(1.4, w * 0.02)), cols=[hz(pal[0]), hz(pal[2]), hz("#6A4028")],
                       inkw=max(1.2, w * 0.012), inkop=0.6, hi=0.35, hik=0.05))
    bd = smooth_closed(body)
    inner = []
    # throwing rings
    for j in range(4, 15):
        y = base - h * j / 16
        inner.append(f'<path d="M {cx - w:.1f} {y:.1f} Q {cx:.1f} {y + w * 0.06:.1f} {cx + w:.1f} {y:.1f}" stroke="{hz(pal[2])}" stroke-width="{max(0.8, w * 0.008):.1f}" fill="none" opacity="0.35"/>')
    # glossy vertical highlight + reflected light
    inner.append(taper([(cx - w * 0.27, base - h * 0.78), (cx - w * 0.32, base - h * 0.55), (cx - w * 0.26, base - h * 0.25)], max(3, w * 0.07), 1, hz("#F8E8D8"), 0.55))
    inner.append(taper([(cx - w * 0.22, base - h * 0.72), (cx - w * 0.25, base - h * 0.6)], max(1.5, w * 0.025), 0.6, "#FFFFFF", 0.7))
    if rim_light:
        inner.append(taper([(cx + w * 0.36, base - h * 0.75), (cx + w * 0.43, base - h * 0.5), (cx + w * 0.34, base - h * 0.2)], max(2, w * 0.04), 1, rim_light, 0.6))
    if deco:
        # jijang: a quick finger-drawn wave with orchid-leaf flicks across the shoulder
        yy = base - h * 0.66
        wave = [(cx - w * 0.36 + i * w * 0.72 / 10, yy + math.sin(i * 1.3 + seed) * h * 0.025) for i in range(11)]
        inner.append(pline(wave, hz("#C8A078"), max(1.6, w * 0.02), seed, 0.75, 1))
        for i in range(3):
            bx = cx - w * 0.24 + i * w * 0.24
            inner.append(taper(catmull([(bx, yy + h * 0.04), (bx + w * 0.05, yy - h * 0.06), (bx + w * 0.13, yy - h * 0.1)], 4), max(2, w * 0.022), 0.5, hz("#C8A078"), 0.7))
            inner.append(taper(catmull([(bx, yy + h * 0.04), (bx - w * 0.04, yy - h * 0.04), (bx - w * 0.1, yy - h * 0.06)], 4), max(1.6, w * 0.018), 0.5, hz("#C8A078"), 0.6))
    out.append(clipped(D, bd, inner))
    # rim
    ry = w * 0.07
    out.append(f'<path d="{ellipse_d(cx, top + 2, mw / 2 + 3, ry + 2)}" fill="{hz(pal[1])}"/>')
    out.append(f'<path d="{ellipse_d(cx, top + 2, mw / 2 - 2, ry - 1)}" fill="{hz("#1A0C06")}"/>')
    out.append(ink(ellipse_d(cx, top + 2, mw / 2 + 3, ry + 2), INK, 1.2, seed, 1, 0.6))
    if lid == "dome":
        lw = mw * 1.12
        lp = ell_pts(cx, top + 2, lw / 2, ry + 3, 0, 180, 14) + [(cx - lw / 2 + 4, top - h * 0.05), (cx - lw * 0.25, top - h * 0.1), (cx, top - h * 0.115),
                                                               (cx + lw * 0.25, top - h * 0.1), (cx + lw / 2 - 4, top - h * 0.05)][::-1][::-1]
        lp = ell_pts(cx, top + 2, lw / 2, ry + 3, 0, 180, 14)
        lp += [(cx - lw / 2 + 3, top - h * 0.04), (cx - lw * 0.28, top - h * 0.1), (cx, top - h * 0.12), (cx + lw * 0.28, top - h * 0.1), (cx + lw / 2 - 3, top - h * 0.04)]
        out.append(painted(D, lp, tuple(hz(c) for c in pal), seed + 5, sdir=(0.8, 0.6), sk=0.18, angle=0, n=12, inkw=max(1, w * 0.01), inkop=0.6, hi=0.4))
        kp = blob_pts(cx, top - h * 0.13, w * 0.07, h * 0.035, seed + 6, 0.06, 10)
        out.append(painted(D, kp, tuple(hz(c) for c in pal), seed + 6, sk=0.2, angle=0, n=4, inkw=1, inkop=0.5, hi=0.45))
        lid_top = top - h * 0.12
    elif lid == "bowl":
        lw = mw * 1.2
        lp = [(cx - lw / 2, top + 3), (cx - lw * 0.42, top - h * 0.08), (cx - lw * 0.22, top - h * 0.12), (cx + lw * 0.22, top - h * 0.12), (cx + lw * 0.42, top - h * 0.08), (cx + lw / 2, top + 3)]
        out.append(painted(D, lp, tuple(hz(c) for c in (("#B8A890", "#8A7A64", "#4A3E30") if pal == ONGGI else pal)), seed + 5, sdir=(0.8, 0.6), sk=0.18, angle=0, n=12, inkw=max(1, w * 0.01), inkop=0.6, hi=0.4))
        lid_top = top - h * 0.12
    else:
        lid_top = top
    if snow:
        sw_ = (mw * 1.18 if lid else mw) / 2
        sp = [(cx - sw_ - 2, lid_top + h * 0.06), (cx - sw_ * 0.7, lid_top - h * 0.03), (cx - sw_ * 0.2, lid_top - h * 0.06), (cx + sw_ * 0.3, lid_top - h * 0.055),
              (cx + sw_ * 0.8, lid_top - h * 0.02), (cx + sw_ + 3, lid_top + h * 0.06), (cx + sw_ * 0.5, lid_top + h * 0.035), (cx, lid_top + h * 0.045), (cx - sw_ * 0.5, lid_top + h * 0.035)]
        out.append(painted(D, sp, ("#FFFFFF", "#F4F6FC", "#AEB8D8"), seed + 7, sdir=(0.3, 1), sk=0.22, angle=0, n=6, inkw=1.1, inkc="#8A94B8", inkop=0.5, hi=0.4))
        for k in range(2):
            dx = cx + rnd.uniform(-sw_, sw_) * 0.8
            out.append(taper([(dx, lid_top + h * 0.03), (dx + 1, lid_top + h * 0.075)], 4, 1.5, "#F4F6FC", 0.95))
    return "".join(out)


def spoon_chopsticks(D, x, y, ang, L, seed, pal=STEEL, sep=16):
    """Korean sujeo: long stainless spoon with a shallow oval bowl, and flat metal chopsticks beside it."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = []
    # shadow
    out.append(taper([(x + 6, y + 8), (x + ux * L + 6, y + uy * L + 8)], 8, 5, "#1A0C06", 0.18))
    # chopsticks (flat, slightly tapering), on the far side
    for k in (1.0, 1.55):
        cx_, cy_ = x + nx * sep * k, y + ny * sep * k
        pts = [(cx_, cy_), (cx_ + ux * L * 0.98, cy_ + uy * L * 0.98 - ny * 2)]
        out.append(taper(pts, 6.5, 3.2, pal[2]))
        out.append(taper([(px - nx * 0.8, py - ny * 0.8) for px, py in pts], 4.5, 2, pal[1]))
        out.append(taper([(px - nx * 1.6, py - ny * 1.6) for px, py in pts], 1.4, 0.6, "#FFFFFF", 0.8))
        # engraved grip pattern near the top
        for j in range(3):
            t = 0.07 + j * 0.035
            px, py = cx_ + ux * L * t, cy_ + uy * L * t
            out.append(f'<path d="M {px - nx * 2.5:.1f} {py - ny * 2.5:.1f} l {nx * 5:.1f} {ny * 5:.1f}" stroke="{pal[2]}" stroke-width="1" opacity="0.6"/>')
    # spoon: handle then bowl
    hl = L * 0.72
    out.append(taper([(x, y), (x + ux * hl * 0.5, y + uy * hl * 0.5), (x + ux * hl, y + uy * hl)], 9, 4.5, pal[2]))
    out.append(taper([(x - nx * 0.6, y - ny * 0.6), (x + ux * hl, y + uy * hl)], 6.5, 3, pal[1]))
    out.append(taper([(x - nx * 1.8, y - ny * 1.8), (x + ux * hl * 0.9, y + uy * hl * 0.9)], 2, 0.8, "#FFFFFF", 0.85))
    bx, by = x + ux * (hl + L * 0.13), y + uy * (hl + L * 0.13)
    bpts = blob_pts(bx, by, L * 0.15, L * 0.085, seed, 0.02, 20, ang)
    out.append(painted(D, bpts, pal, seed, sdir=(0.6, 0.8), sk=0.2, angle=ang, n=8, inkw=1.2, inkc="#4A5260", inkop=0.6, hi=0.5))
    out.append(f'<path d="{blob(bx - ux * L * 0.03 - nx * 3, by - uy * L * 0.03 - ny * 3, L * 0.07, L * 0.03, seed + 1, 0.1, 10, ang)}" fill="#FFFFFF" opacity="0.75"/>')
    return "".join(out)


def steel_bowl(D, cx, rim_y, rx, h, seed, fill="rice", lid=False, pal=STEEL):
    """Stainless rice bowl (gonggi) seen from slightly above: tapered body with a foot ring, mirror-bright bands."""
    ry = rx * 0.32
    out = [cast(D, cx + rx * 0.15, rim_y + h + 2, rx * 1.0, 9, strength=0.4, seed=seed)]
    body = ell_pts(cx, rim_y, rx, ry, 0, 180, 16) + [(cx - rx * 0.62, rim_y + h), (cx + rx * 0.62, rim_y + h)][::-1][::-1]
    body = [(cx + rx, rim_y)] + [(cx + rx * 0.9, rim_y + h * 0.55), (cx + rx * 0.66, rim_y + h), (cx - rx * 0.66, rim_y + h), (cx - rx * 0.9, rim_y + h * 0.55), (cx - rx, rim_y)]
    body = body + ell_pts(cx, rim_y, rx, ry, 180, 360, 16)[1:-1]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{pal[1]}"/>')
    g = D.lin([(0, pal[2]), (0.18, "#FFFFFF"), (0.32, pal[1]), (0.55, pal[2]), (0.72, "#EEF2F6"), (0.86, pal[1]), (1, pal[2])], 0, 0, 1, 0)
    out.append(clipped(D, d, [f'<rect x="{cx - rx - 2:.1f}" y="{rim_y - ry:.1f}" width="{2 * rx + 4:.1f}" height="{h + ry + 4:.1f}" fill="{g}" opacity="0.9"/>',
                              strokes(D.nid(), d, (cx - rx, rim_y, cx + rx, rim_y + h), ["#FFFFFF", pal[2]], seed, n=14, angle=-88, length=(h * 0.3, h * 0.8), width=(0.8, 2), opacity=(0.15, 0.35))]))
    out.append(ink(d, "#4A5260", 1.4, seed, 1, 0.6))
    # foot ring
    out.append(f'<path d="M {cx - rx * 0.6:.1f} {rim_y + h:.1f} Q {cx:.1f} {rim_y + h + rx * 0.08:.1f} {cx + rx * 0.6:.1f} {rim_y + h:.1f}" stroke="{pal[2]}" stroke-width="2" fill="none"/>')
    # rim
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx, ry)}" fill="#EEF2F6"/>')
    out.append(f'<path d="{ellipse_d(cx, rim_y + 1.5, rx - 4, ry - 3)}" fill="{pal[2]}"/>')
    if fill == "rice":
        rnd = random.Random(seed)
        mound = ell_pts(cx, rim_y + 1, rx - 5, ry - 4, 180, 360, 16)
        mound = [(x, y - (math.sin(math.pi * (x - cx + rx) / (2 * rx)) * rx * 0.28)) for x, y in mound]
        mp = mound + ell_pts(cx, rim_y + 1.5, rx - 5, ry - 4, 0, 180, 16)[1:-1]
        md = smooth_closed(mp)
        out.append(f'<path d="{md}" fill="#FBF8F0"/>')
        grains = [shade_over(D, md, "#8A8AA0", 0.35, 0, 0, 1, 1, 0.45)]
        for _ in range(int(rx * 3)):
            gx, gy = cx + rnd.uniform(-rx, rx), rim_y + rnd.uniform(-rx * 0.4, ry)
            grains.append(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="{rnd.uniform(2.6, 3.4):.1f}" ry="1.5" fill="#FFFFFF" stroke="#D8D2C6" stroke-width="0.6" transform="rotate({rnd.uniform(0, 180):.0f} {gx:.1f} {gy:.1f})"/>')
        out.append(clipped(D, md, grains))
        out.append(ink(md, "#9A948A", 1, seed, 1, 0.5))
    out.append(ink(ellipse_d(cx, rim_y, rx, ry), "#4A5260", 1.4, seed + 1, 1, 0.6))
    if lid:
        pass
    return "".join(out)


def banchan_dish(D, cx, cy, r, kind, seed, tilt=0.55, glaze=WHITE, rim=None):
    """Small round dish of side dish seen from above at a slant (tilt = ry/rx)."""
    rnd = random.Random(seed)
    ry = r * tilt
    out = [cast(D, cx + r * 0.12, cy + ry * 0.35, r * 1.06, ry * 1.05, strength=0.35, seed=seed)]
    out.append(f'<path d="{ellipse_d(cx, cy + r * 0.08, r, ry)}" fill="{glaze[2]}"/>')
    out.append(painted(D, ell_pts(cx, cy, r, ry, 0, 360, 28)[:-1], glaze, seed, sdir=(0.6, 0.8), sk=0.06, angle=0, n=6, inkw=1.3, hi=0.3))
    if rim:
        out.append(ink(ellipse_d(cx, cy, r * 0.9, ry * 0.88), rim, max(1.4, r * 0.05), seed + 1, 1, 0.8))
    ir, iry = r * 0.74, ry * 0.7
    inside = ellipse_d(cx, cy + ry * 0.04, ir, iry)
    items = []
    if kind == "kimchi":
        items.append(f'<path d="{inside}" fill="#C8341E"/>')
        for _ in range(9):
            x, y = cx + rnd.uniform(-ir * 0.75, ir * 0.75), cy + rnd.uniform(-iry * 0.7, iry * 0.7)
            a = rnd.uniform(0, 180)
            pts = blob_pts(x, y, ir * 0.32, ir * 0.16, rnd.randint(0, 999), 0.15, 10, a)
            items.append(painted(D, pts, ("#F89A6A", "#D8452A", "#8A1A10"), rnd.randint(0, 999), sk=0.2, angle=a, n=4, inkw=0.8, inkop=0.4, hi=0.4))
            items.append(taper([(x - math.cos(math.radians(a)) * ir * 0.2, y - math.sin(math.radians(a)) * ir * 0.2), (x + math.cos(math.radians(a)) * ir * 0.2, y + math.sin(math.radians(a)) * ir * 0.2)], 2.4, 1, "#FFE8C8", 0.7))
        items.append(specks(seed + 3, (cx - ir, cy - iry, cx + ir, cy + iry), ["#7A0E0A", "#F6B07A"], int(r * 0.8), (0.6, 1.4), (0.5, 0.9)))
    elif kind == "kkakdugi":
        items.append(f'<path d="{inside}" fill="#D84A2A"/>')
        for _ in range(8):
            x, y = cx + rnd.uniform(-ir * 0.7, ir * 0.7), cy + rnd.uniform(-iry * 0.6, iry * 0.6)
            s = r * 0.22
            top = [(x - s / 2, y - s * 0.3), (x + s / 2, y - s * 0.4), (x + s * 0.55, y + s * 0.15), (x - s * 0.45, y + s * 0.25)]
            items.append(f'<path d="{pd(top)}" fill="#F08A5A"/><path d="{pd([(x - s * 0.45, y + s * 0.25), (x + s * 0.55, y + s * 0.15), (x + s * 0.55, y + s * 0.5), (x - s * 0.45, y + s * 0.6)])}" fill="#B8301A"/>')
            items.append(f'<path d="{pd(top)}" fill="none" stroke="#7A1A0A" stroke-width="0.9" opacity="0.6"/>')
    elif kind == "spinach":
        items.append(f'<path d="{inside}" fill="#2E5A1E"/>')
        for _ in range(int(r * 1.4)):
            x, y = cx + rnd.uniform(-ir * 0.8, ir * 0.8), cy + rnd.uniform(-iry * 0.7, iry * 0.7)
            a = rnd.uniform(0, 6.28)
            Ls = rnd.uniform(r * 0.2, r * 0.45)
            items.append(taper([(x, y), (x + math.cos(a) * Ls * 0.5, y + math.sin(a) * Ls * 0.5 * tilt + 2), (x + math.cos(a) * Ls, y + math.sin(a) * Ls * tilt)],
                               rnd.uniform(3, 6), 1, rnd.choice(["#4E8A2E", "#3A7020", "#6AA43A", "#245014"]), 0.95))
        items.append(specks(seed + 4, (cx - ir, cy - iry, cx + ir, cy + iry), ["#FFF6D8"], int(r * 0.6), (0.8, 1.4), (0.7, 1)))
    elif kind == "sprouts":
        items.append(f'<path d="{inside}" fill="#E8E2C0"/>')
        for _ in range(int(r * 1.2)):
            x, y = cx + rnd.uniform(-ir * 0.8, ir * 0.8), cy + rnd.uniform(-iry * 0.7, iry * 0.7)
            a = rnd.uniform(0, 6.28)
            Ls = rnd.uniform(r * 0.3, r * 0.6)
            ex, ey = x + math.cos(a) * Ls, y + math.sin(a) * Ls * tilt
            items.append(taper([(x, y), ((x + ex) / 2 + 2, (y + ey) / 2 - 2), (ex, ey)], 2.6, 1.6, rnd.choice(["#FFFDF0", "#F4EED0", "#FFFFFF"]), 1))
            items.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="2.6" ry="1.9" fill="#F2D24A"/>')
    elif kind == "beans":
        items.append(f'<path d="{inside}" fill="#2A1A10"/>')
        for _ in range(int(r * 1.3)):
            x, y = cx + rnd.uniform(-ir * 0.8, ir * 0.8), cy + rnd.uniform(-iry * 0.75, iry * 0.75)
            items.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.1:.1f}" ry="{r * 0.08:.1f}" fill="#1A100A"/><circle cx="{x - r * 0.03:.1f}" cy="{y - r * 0.03:.1f}" r="{r * 0.03:.1f}" fill="#FFFFFF" opacity="0.75"/>')
    elif kind == "fishcake":
        items.append(f'<path d="{inside}" fill="#C88A4A"/>')
        for _ in range(9):
            x, y = cx + rnd.uniform(-ir * 0.7, ir * 0.7), cy + rnd.uniform(-iry * 0.6, iry * 0.6)
            a = rnd.uniform(0, 180)
            items.append(taper([(x - math.cos(math.radians(a)) * r * 0.25, y - math.sin(math.radians(a)) * r * 0.12), (x + math.cos(math.radians(a)) * r * 0.25, y + math.sin(math.radians(a)) * r * 0.12)], 6, 5, rnd.choice(["#E8B06A", "#D8984A", "#F2C47A"]), 1))
        items.append(specks(seed + 5, (cx - ir, cy - iry, cx + ir, cy + iry), ["#2A6A1A", "#C8301A"], 12, (1, 2), (0.8, 1)))
    elif kind == "egg":
        items.append(f'<path d="{inside}" fill="#F6E2A0"/>')
        for k in range(3):
            x = cx - ir * 0.5 + k * ir * 0.5
            items.append(painted(D, rect_pts(x - r * 0.2, cy - iry * 0.45, x + r * 0.2, cy + iry * 0.5, 8, seed + k, 0.4), ("#FFF2B0", "#F6CC4A", "#B88A1A"), seed + k, sdir=(0.5, 1), sk=0.2, angle=-90, n=6, inkw=0.9, hi=0.3))
            items.append(f'<path d="M {x - r * 0.12:.1f} {cy - iry * 0.2:.1f} q {r * 0.12:.1f} {r * 0.08:.1f} {r * 0.2:.1f} 0" stroke="#E8A82A" stroke-width="1.3" fill="none"/>')
    items.append(shade_over(D, inside, "#1A0A04", 0.35, 0, 0, 0, 1, 0.4))
    out.append(clipped(D, inside, items))
    out.append(ink(inside, INK, 1, seed, 1, 0.35))
    return "".join(out)


def scallion(D, x0, y0, x1, y1, seed, w=10):
    """A green onion: white bulb end with roots at (x0, y0), green hollow leaves toward (x1, y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    Ls = math.hypot(x1 - x0, y1 - y0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = []
    for k in range(5):
        r = math.radians(-25 + k * 12)
        out.append(pline([(x0, y0), (x0 - ux * 10 + math.cos(a + math.pi + r) * 6, y0 - uy * 10 + math.sin(a + math.pi + r) * 6)], "#E8DCC0", 1.1, seed + k, 0.9, 1))
    wp = [(x0, y0), (x0 + ux * Ls * 0.35, y0 + uy * Ls * 0.35)]
    out.append(taper(wp, w * 1.1, w, "#F6F2E2"))
    out.append(taper([(px + nx * w * 0.2, py + ny * w * 0.2) for px, py in wp], w * 0.3, w * 0.25, "#D8D0B0", 0.8))
    mid = (x0 + ux * Ls * 0.35, y0 + uy * Ls * 0.35)
    out.append(taper([mid, (mid[0] + ux * Ls * 0.15, mid[1] + uy * Ls * 0.15)], w, w * 0.95, "#C8DC8A"))
    for k, (dv, Lk) in enumerate(((-0.08, 0.66), (0.0, 0.62), (0.1, 0.58))):
        bb = a + dv
        e = (mid[0] + math.cos(bb) * Ls * Lk, mid[1] + math.sin(bb) * Ls * Lk)
        m2 = ((mid[0] + e[0]) / 2 + nx * k * 3, (mid[1] + e[1]) / 2 + ny * k * 3)
        out.append(taper([mid, m2, e], w * 0.75, w * 0.25, ["#3E8A2E", "#4E9A36", "#2E7020"][k]))
        out.append(taper([(mid[0] - nx * 1.5, mid[1] - ny * 1.5), (m2[0] - nx * 1.5, m2[1] - ny * 1.5), e], w * 0.22, 0.6, "#A8D878", 0.7))
    return "".join(out)


def persimmon(D, cx, cy, r, seed, pal=PERSIMMON, calyx=True, snow=False, light=(-0.6, -0.8), ang=0, pecked=False):
    """Ripe persimmon (gam): squarish-round fruit, glossy, with a four-lobed green-brown calyx."""
    rnd = random.Random(seed)
    pts = []
    for i in range(32):
        a = 2 * math.pi * i / 32
        k = 1 + 0.06 * math.cos(4 * (a - math.radians(ang)))
        pts.append((cx + r * k * math.cos(a), cy + r * 0.88 * k * math.sin(a)))
    out = [painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-60, n=int(r * 0.8) + 6, inkw=max(1, r * 0.05), inkop=0.55, hi=0.45, hik=0.1)]
    out.append(f'<path d="{blob(cx - r * 0.36, cy - r * 0.32, r * 0.2, r * 0.12, seed + 1, 0.15, 10, -30)}" fill="#FFF0D8" opacity="0.7"/>')
    if pecked:
        out.append(f'<path d="{blob(cx + r * 0.2, cy + r * 0.2, r * 0.32, r * 0.24, seed + 9, 0.25, 10)}" fill="#E8501A"/>')
        out.append(f'<path d="{blob(cx + r * 0.22, cy + r * 0.24, r * 0.2, r * 0.13, seed + 10, 0.25, 10)}" fill="#B8300A" opacity="0.7"/>')
    if calyx:
        top = cy - r * 0.84
        for k in range(4):
            aa = math.radians(-90 + (k - 1.5) * 42)
            ex, ey = cx + math.cos(aa) * r * 0.42, top + r * 0.12 + math.sin(aa) * r * 0.1 + r * 0.1
            lp = blob_pts((cx + ex) / 2, (top + ey) / 2 + r * 0.04, r * 0.24, r * 0.1, seed + k, 0.12, 10, math.degrees(math.atan2(ey - top, ex - cx)))
            out.append(painted(D, lp, ("#A8A060", "#6A6A2E", "#3A3A14"), seed + k, sk=0.2, n=3, inkw=0.9, inkop=0.5, hi=0.3))
        out.append(taper([(cx, top + r * 0.04), (cx + r * 0.06, top - r * 0.2)], max(2.5, r * 0.14), max(1.5, r * 0.08), "#4A3A1A"))
    if snow:
        sp = [(cx - r * 0.6, cy - r * 0.62), (cx - r * 0.3, cy - r * 0.92), (cx + r * 0.25, cy - r * 0.95), (cx + r * 0.65, cy - r * 0.62), (cx + r * 0.2, cy - r * 0.7), (cx - r * 0.25, cy - r * 0.68)]
        out.append(painted(D, sp, ("#FFFFFF", "#F4F6FC", "#B8C0DC"), seed + 8, sdir=(0.3, 1), sk=0.2, angle=0, n=3, inkw=0.9, inkc="#8A94B8", inkop=0.5, hi=0.4))
    return "".join(out)


def magpie(D, ox, oy, s, seed, flip=False, beak_open=False, look=0.0):
    """Oriental magpie (kkachi) perched: black hood, white belly and shoulder patch, blue-green sheen on the wing and
    a long graduated tail. (ox, oy) = feet on the perch, facing left (flip=True faces right). s = scale (1 ~ 150 px long)."""
    def P(pts):
        return L(pts, ox, oy, s, flip)
    out = []
    # tail: long, iridescent, angled down-right behind
    tail = P([(20, -40), (34, -36), (128, 22), (136, 40), (124, 42), (16, -26)])
    out.append(painted(D, tail, ("#4A7A8A", "#1E3A46", "#0A161C"), seed, sdir=(0.3, 1), sk=0.2, angle=30, n=16, cols=["#3E8A8A", "#1A2A40", "#5A6AA8", "#0E1A20"],
                       inkw=1.4, inkc="#0A0E12", hi=0.35))
    out.append(pline(P([(24, -32), (80, 4), (128, 34)]), "#7AB8C0", 1.4, seed, 0.6, 1))
    # body
    body = P([(-26, -62), (-6, -72), (20, -66), (38, -46), (40, -30), (24, -14), (2, -8), (-16, -14), (-28, -32), (-32, -50)])
    out.append(painted(D, body, ("#4A4A58", "#1A1A22", "#08080C"), seed + 1, sdir=(0.6, 0.6), sk=0.18, angle=40, n=20, inkw=1.6, inkc="#050508", hi=0.4))
    # white belly / flank
    belly = P([(-16, -40), (6, -46), (24, -40), (28, -24), (14, -12), (-6, -10), (-18, -22)])
    out.append(painted(D, belly, ("#FFFFFF", "#F2F2EE", "#B8B8C4"), seed + 2, sdir=(0.4, 1), sk=0.2, angle=-20, n=8, inkw=1.1, inkc="#3A3A44", inkop=0.5, hi=0.3))
    # wing with white scapular patch and blue primaries
    wing = P([(-6, -64), (20, -62), (44, -46), (56, -30), (40, -26), (14, -36), (-2, -48)])
    out.append(painted(D, wing, ("#3A4A5A", "#141820", "#04060A"), seed + 3, sdir=(0.5, 0.8), sk=0.18, angle=25, n=10, inkw=1.3, inkc="#000000", hi=0.3))
    out.append(painted(D, P([(-2, -60), (14, -60), (22, -52), (10, -48), (0, -52)]), ("#FFFFFF", "#F4F4F0", "#B8B8C0"), seed + 4, sk=0.15, n=3, inkw=0.9, inkop=0.4, hi=0.2))
    out.append(taper(P([(22, -44), (40, -36), (54, -30)]), 5 * s, 1.5, "#3A7A9A", 0.85))
    out.append(taper(P([(18, -50), (36, -42)]), 3 * s, 1, "#5AA8C0", 0.6))
    # head
    look_y = look * 6
    head = P([(-46, -78 + look_y), (-38, -92 + look_y), (-22, -96 + look_y), (-8, -88 + look_y), (-4, -72), (-16, -62), (-34, -64)])
    out.append(painted(D, head, ("#4A4A58", "#1A1A22", "#08080C"), seed + 5, sdir=(0.6, 0.6), sk=0.15, angle=0, n=8, inkw=1.4, inkc="#050508", hi=0.45))
    # beak
    bx, by = P([(-46, -80 + look_y)])[0]
    sg = 1 if flip else -1
    if beak_open:
        out.append(f'<path d="{pd(P([(-44, -84 + look_y), (-64, -86 + look_y * 1.4), (-46, -80 + look_y)]))}" fill="#1A1A1E"/>')
        out.append(f'<path d="{pd(P([(-45, -79 + look_y), (-62, -74 + look_y * 1.6), (-44, -75 + look_y)]))}" fill="#26262C"/>')
    else:
        out.append(f'<path d="{pd(P([(-44, -86 + look_y), (-64, -80 + look_y * 1.4), (-44, -75 + look_y)]))}" fill="#1A1A1E"/>')
    ex, ey = P([(-30, -84 + look_y)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3.2 * s:.1f}" fill="#000000"/><circle cx="{ex - sg * 0.9 * s:.1f}" cy="{ey - 1 * s:.1f}" r="{1.1 * s:.1f}" fill="#FFFFFF"/>')
    # feet
    for dx in (-6, 6):
        fx, fy = P([(dx, -10)])[0]
        tx, ty = P([(dx - 2, 0)])[0]
        out.append(pline([(fx, fy), (tx, ty)], "#1A1A1E", 2.4 * s, seed + dx, 1, 1))
        out.append(pline([(tx - 5 * s, ty + 1), (tx + 5 * s, ty + 1)], "#1A1A1E", 2 * s, seed + dx, 1, 1))
    return "".join(out)


def needle_tuft(D, cx, cy, r, seed, pal=PINE, ang=-90, spread=150, n=26, ink_c=None):
    """A fan-shaped burst of pine needles, painted the minhwa way (dark base fan, lighter needles on top)."""
    rnd = random.Random(seed)
    out = []
    base = [(cx, cy)] + [(cx + math.cos(math.radians(ang - spread / 2 + spread * i / 12)) * r * 0.92, cy + math.sin(math.radians(ang - spread / 2 + spread * i / 12)) * r * 0.92) for i in range(13)]
    out.append(f'<path d="{smooth_closed(base)}" fill="{pal[2]}" opacity="0.9"/>')
    for i in range(n):
        a = math.radians(ang - spread / 2 + spread * i / (n - 1) + rnd.uniform(-3, 3))
        Ls = r * rnd.uniform(0.75, 1.05)
        c = pal[0] if i % 3 == 0 else pal[1]
        out.append(taper([(cx, cy), (cx + math.cos(a) * Ls, cy + math.sin(a) * Ls)], 2.4, 0.6, c, 0.95))
    if ink_c:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{max(2, r * 0.08):.1f}" fill="{ink_c}"/>')
    return "".join(out)


def giwa_row(D, x0, x1, y, h, seed, pal=("#7A7E88", "#4A4E58", "#22252C"), snow=False, end_tiles=True):
    """A ridge of Korean roof tiles seen from the front: rounded cover tiles with round end-caps (sumaksae)."""
    rnd = random.Random(seed)
    out = [f'<path d="{hg.org_rect(x0, y, x1 - x0, h, seed, 0.6, 20, 2)}" fill="{pal[1]}"/>']
    step = h * 0.9
    x = x0 + step * 0.3
    while x < x1:
        c = mix(pal[1], rnd.choice([pal[0], pal[2]]), rnd.uniform(0.05, 0.3))
        out.append(f'<path d="{blob(x, y + h * 0.55, step * 0.42, h * 0.48, seed + int(x), 0.05, 10)}" fill="{c}"/>')
        out.append(f'<path d="M {x - step * 0.3:.1f} {y + h * 0.3:.1f} q {step * 0.3:.1f} {-h * 0.2:.1f} {step * 0.6:.1f} 0" stroke="{pal[0]}" stroke-width="1.6" fill="none" opacity="0.6"/>')
        if end_tiles:
            out.append(f'<circle cx="{x:.1f}" cy="{y + h * 0.75:.1f}" r="{h * 0.22:.1f}" fill="none" stroke="{pal[2]}" stroke-width="1.2" opacity="0.7"/>')
        x += step
    out.append(f'<path d="M {x0} {y + h} L {x1} {y + h}" stroke="{pal[2]}" stroke-width="2" opacity="0.8"/>')
    if snow:
        top = [(x0 - 4, y + 4)] + [(x0 + i * (x1 - x0) / 12, y - rnd.uniform(5, 9)) for i in range(13)] + [(x1 + 4, y + 4)]
        sp = top + [(x1, y + h * 0.35)] + [(x1 - i * (x1 - x0) / 12, y + h * rnd.uniform(0.2, 0.45)) for i in range(13)]
        out.append(painted(D, sp, ("#FFFFFF", "#F4F6FC", "#B0BAD8"), seed + 3, sdir=(0.2, 1), sk=0.25, angle=0, n=12, inkw=1.1, inkc="#8A94B8", inkop=0.5, hi=0.4))
    return "".join(out)


def snowflakes(seed, n, box, avoid=()):
    return hg.flakes(seed, n, box, (1.2, 3.6), "#FFFFFF", (0.6, 1.0), avoid=avoid)


# ================================================================ 1. kimchi — kimjang day, seen from above on the yellow ondol floor
def jangpan(D, seed, base=("#F6D27A", "#E8B24A", "#B07A1E"), cell=150, rot_=-6):
    """Oiled-paper ondol floor (jangpan): glossy amber sheets laid in overlapping squares."""
    rnd = random.Random(seed)
    out = [f'<rect width="600" height="600" fill="{base[1]}"/>']
    g = []
    for j in range(-2, 7):
        for i in range(-2, 7):
            x, y = i * cell + (j % 2) * cell * 0.5, j * cell
            c = mix(base[1], rnd.choice([base[0], base[2]]), rnd.uniform(0.05, 0.22))
            g.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{cell}" height="{cell}" fill="{c}"/>')
            g.append(f'<path d="M {x:.0f} {y + 2:.0f} L {x + cell:.0f} {y + 2:.0f}" stroke="{base[0]}" stroke-width="2" opacity="0.8"/>')
            g.append(f'<path d="M {x + 1:.0f} {y:.0f} L {x + 1:.0f} {y + cell:.0f}" stroke="{base[2]}" stroke-width="1.6" opacity="0.55"/>')
            g.append(f'<path d="M {x:.0f} {y:.0f} L {x + cell:.0f} {y:.0f}" stroke="{base[2]}" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<g transform="rotate({rot_} 300 300)">{"".join(g)}</g>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), [base[0], base[2], "#FFF2C0"], seed, n=160,
                       angle=rot_ - 4, length=(60, 180), width=(3, 9), opacity=(0.06, 0.18), curve=0.06))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF6D0", 0.45), (1, "#FFF6D0", 0)], 0.3, 0.25, 0.7)}"/>')
    return "".join(out)


def capsule_pts(x0, y0, x1, y1, w0, w1=None, n=8):
    """Rounded-end capsule from (x0, y0) to (x1, y1), widths w0 -> w1 (finger, stalk, rolled cloth...)."""
    w1 = w1 if w1 is not None else w0
    a = math.atan2(y1 - y0, x1 - x0)
    pts = []
    for i in range(n + 1):
        t = a - math.pi / 2 - math.pi * i / n
        pts.append((x0 + math.cos(t) * w0 / 2, y0 + math.sin(t) * w0 / 2))
    for i in range(n + 1):
        t = a + math.pi / 2 - math.pi * i / n
        pts.append((x1 + math.cos(t) * w1 / 2, y1 + math.sin(t) * w1 / 2))
    return pts


def cabbage_half(D, cx, cy, Ls, W, ang, seed, paste=0.6):
    """Napa cabbage cut lengthwise, cut face up: from the pale core, white ribs fan out toward a crinkled green leafy
    end; `paste` > 0 smears red kimchi filling between the leaves (gochugaru paste, radish matchsticks, scallion)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux

    def at(t, s):
        return (cx + ux * Ls * (t - 0.5) + nx * s, cy + uy * Ls * (t - 0.5) + ny * s)

    def wid(t):
        return W * (0.34 + 0.66 * math.sin(math.pi * min(1, 0.2 + t * 0.62)) ** 0.8)

    N = 22
    right = [at(i / N, wid(i / N) / 2) for i in range(N + 1)]
    left = [at(i / N, -wid(i / N) / 2) for i in range(N + 1)]
    # ruffled leafy end
    tip = []
    for i in range(1, 12):
        s_ = (0.5 - i / 12) * wid(1.0)
        bulge = 0.04 + 0.03 * math.sin(i * 2.3 + seed)
        tip.append(at(1.0 + bulge, s_))
    pts = right + tip + left[::-1]
    d = smooth_closed(jitter(pts, seed, 1.0))
    out = [cast(D, cx + 9, cy + 11, Ls * 0.54, W * 0.6, strength=0.38, seed=seed)]
    # the thickness of the half-head, seen along its lower edge
    out.append(f'<path d="{smooth_closed([(x + 4, y + 9) for x, y in jitter(pts, seed, 1.0)])}" fill="{"#8A1A0E" if paste else "#9AAE5A"}"/>')
    g = D.lin([(0, "#FFF8D8"), (0.5, "#F4F2C8"), (0.72, "#D8E890"), (0.86, "#8ABE4E"), (1, "#3E7A22")], *at(0.0, 0), *at(1.05, 0), "userSpaceOnUse")
    out.append(f'<path d="{d}" fill="{g}"/>')
    inner = []
    # crinkled green leaf margin (dabs) toward the leafy end
    for _ in range(46):
        t = rnd.uniform(0.74, 1.06)
        s_ = rnd.uniform(-0.55, 0.55) * wid(min(1, t))
        x, y = at(t, s_)
        inner.append(f'<path d="{blob(x, y, W * rnd.uniform(0.06, 0.12), W * rnd.uniform(0.04, 0.08), rnd.randint(0, 999), 0.35, 10, rnd.uniform(0, 180))}" '
                     f'fill="{rnd.choice(["#2E6A1E", "#4E8A2A", "#6AA43A", "#9ACB5A", "#C8E07A"])}" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    # stacked ribs: fanning lines from the core to the leafy end, each with a pale crest and a soft shadow
    for k in range(13):
        s0 = (k / 12 - 0.5) * wid(0.0) * 0.5
        s1 = (k / 12 - 0.5) * wid(0.95) * 0.98
        line = [at(0.04, s0), at(0.35, s0 + (s1 - s0) * 0.45), at(0.7, s0 + (s1 - s0) * 0.85), at(0.93, s1)]
        line = catmull(line, 5)
        if k % 2:
            continue
        inner.append(taper(line, 8, 3, "#FFFFF4", 0.85))
        inner.append(taper([(x + nx * 5, y + ny * 5) for x, y in line], 3, 1, "#A8B070", 0.6))
    # pale golden core
    cx0, cy0 = at(0.06, 0)
    inner.append(f'<path d="{blob(cx0, cy0, W * 0.2, W * 0.13, seed + 3, 0.15, 10, ang)}" fill="#F2DC90"/>')
    inner.append(f'<path d="{blob(cx0, cy0, W * 0.1, W * 0.07, seed + 4, 0.15, 10, ang)}" fill="#E8C870"/>')
    if paste:
        # a coat of red over the whole cut face, ribs still showing through as lighter ridges
        coat = [at(0.06 + 0.86 * i / 20, wid(0.06 + 0.86 * i / 20) * 0.47) for i in range(21)] + [at(0.06 + 0.86 * i / 20, -wid(0.06 + 0.86 * i / 20) * 0.47) for i in range(20, -1, -1)]
        inner.append(f'<path d="{smooth_closed(jitter(coat, seed + 5, 3))}" fill="#C8301E" opacity="{0.5 * paste:.2f}"/>')
        # red filling: streaks laid along the ribs, then thicker smears
        for _ in range(int(40 * paste)):
            t = rnd.uniform(0.12, 0.9)
            s_ = rnd.uniform(-0.45, 0.45) * wid(t)
            x, y = at(t, s_)
            Lr = rnd.uniform(16, 40)
            inner.append(taper([(x, y), (x + ux * Lr * 0.5 + nx * 1.5, y + uy * Lr * 0.5 + ny * 1.5), (x + ux * Lr, y + uy * Lr)], rnd.uniform(5, 11), 2,
                               rnd.choice(["#C8281E", "#D8402A", "#B01E14", "#E05A32"]), rnd.uniform(0.75, 0.95)))
        for _ in range(int(9 * paste)):
            t = rnd.uniform(0.2, 0.75)
            x, y = at(t, rnd.uniform(-0.3, 0.3) * wid(t))
            inner.append(f'<path d="{blob(x, y, W * rnd.uniform(0.14, 0.24), W * rnd.uniform(0.07, 0.11), rnd.randint(0, 999), 0.35, 12, ang + rnd.uniform(-15, 15))}" '
                         f'fill="{rnd.choice(["#B81E14", "#C8281E", "#D23A22"])}" opacity="0.92"/>')
        for _ in range(int(30 * paste)):
            t = rnd.uniform(0.15, 0.85)
            x, y = at(t, rnd.uniform(-0.42, 0.42) * wid(t))
            b = a + rnd.uniform(-0.7, 0.7)
            Lr = rnd.uniform(9, 17)
            inner.append(taper([(x, y), (x + math.cos(b) * Lr, y + math.sin(b) * Lr)], 2.8, 2.2, rnd.choice(["#FFE0C8", "#F8B890", "#FFF2E2"]), 0.95))
        for _ in range(int(14 * paste)):
            t = rnd.uniform(0.2, 0.85)
            x, y = at(t, rnd.uniform(-0.4, 0.4) * wid(t))
            inner.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-6, 6):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#3E8A2E" stroke-width="3.2" stroke-linecap="round"/>')
        inner.append(specks(seed + 7, bbox(pts), ["#7A0E0A", "#5A0A06", "#F08A5A"], int(Ls * 0.6), (0.6, 1.4), (0.5, 0.9)))
    inner.append(shade_over(D, d, "#2A2A0A", 0.3, 0, 0, 1, 1, 0.45))
    inner.append(light_over(D, d, "#FFFFFF", 0.3, 0, 0, 0.6, 0.6, 0.5))
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#4A5A22", 1.6, seed, 2, 0.6))
    return "".join(out)


def rubber_glove(D, cx, cy, s, ang, seed, pal=("#FF8AA0", "#E8406A", "#9A1A3A"), paste=True):
    """Kitchen rubber glove lying flat (fingers toward `ang`), puffy rounded fingers, a rolled cuff, red smears."""
    rnd = random.Random(seed)

    def P(pts):
        return rot(L(pts, cx, cy, s), cx, cy, ang + 90)

    out = [cast(D, cx + 10, cy + 12, 66 * s, 70 * s, strength=0.3, seed=seed)]
    shapes = []
    # cuff (wide, flared), palm, four fingers close together, thumb angled out
    shapes.append((P([(-34, 22), (34, 22), (44, 96), (-42, 96)]), 0))
    for k, (fx, Lf, wf, lean) in enumerate(((-24, 52, 19, -5), (-8, 62, 19, -1), (8, 60, 19, 2), (24, 46, 17, 6))):
        p0 = P([(fx, -30)])[0]
        p1 = P([(fx + lean, -30 - Lf)])[0]
        shapes.append((capsule_pts(p0[0], p0[1], p1[0], p1[1], wf * s, wf * s * 0.92), k + 1))
    t0, t1 = P([(-30, 4)])[0], P([(-62, -32)])[0]
    shapes.append((capsule_pts(t0[0], t0[1], t1[0], t1[1], 22 * s, 18 * s), 6))
    shapes.append((P([(-36, 26), (-40, -6), (-32, -36), (34, -36), (38, -6), (36, 26)]), 7))
    for pts, k in shapes:
        out.append(painted(D, pts, pal, seed + k, sdir=(0.7, 0.6), sk=0.18, angle=ang, n=6, inkw=1.4, inkc="#6A0A24", inkop=0.6, hi=0.5, hik=0.12))
    # rolled cuff edge
    out.append(taper(P([(-44, 90), (0, 93), (46, 90)]), 9 * s, 9 * s, pal[0], 0.9))
    out.append(taper(P([(-44, 94), (0, 97), (46, 94)]), 2 * s, 2 * s, pal[2], 0.6))
    # finger creases and sheen
    for fx in (-24, -8, 8):
        out.append(pline(P([(fx + 8, -32), (fx + 8, -20)]), pal[2], 1.2, seed, 0.5, 1))
    out.append(taper(P([(-20, 10), (-10, -20), (6, -30)]), 4 * s, 1, "#FFFFFF", 0.55))
    if paste:
        for _ in range(9):
            x, y = P([(rnd.uniform(-26, 26), rnd.uniform(-80, 14))])[0]
            out.append(f'<path d="{blob(x, y, rnd.uniform(5, 11) * s, rnd.uniform(3, 6) * s, rnd.randint(0, 999), 0.35, 10, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8281E", "#B01E14", "#D8402A"])}" opacity="0.9"/>')
    return "".join(out)


def red_basin(D, cx, cy, R, seed, pal=("#F25A4A", "#D8241E", "#8A0E0A")):
    """Big round plastic kimjang basin seen from above: thick rolled rim, sloping inner wall, flat floor."""
    out = [f'<path d="{blob(cx + 14, cy + 16, R * 1.02, R * 1.0, seed, 0.02, 30)}" fill="{D.rad([(0, "#3A1A06", 0.45), (0.8, "#3A1A06", 0.3), (1, "#3A1A06", 0)])}"/>']
    outer = blob(cx, cy, R, R, seed + 1, 0.008, 40)
    out.append(f'<path d="{outer}" fill="{pal[1]}"/>')
    wall = blob(cx, cy, R * 0.9, R * 0.9, seed + 2, 0.008, 40)
    out.append(f'<path d="{wall}" fill="{D.rad([(0, pal[1]), (0.75, pal[1]), (1, dk(pal[1], 0.3))], 0.55, 0.6, 0.6)}"/>')
    floor = blob(cx + R * 0.04, cy + R * 0.05, R * 0.66, R * 0.66, seed + 3, 0.01, 36)
    out.append(f'<path d="{floor}" fill="{dk(pal[1], 0.12)}"/>')
    out.append(f'<path d="{floor}" fill="none" stroke="{dk(pal[1], 0.35)}" stroke-width="2" opacity="0.5"/>')
    # rim highlight (light from upper left) and the shadowed side of the inner wall
    out.append(taper(ell_pts(cx, cy, R * 0.95, R * 0.95, 170, 290, 16), 8, 3, pal[0], 0.85))
    out.append(taper(ell_pts(cx, cy, R * 0.96, R * 0.96, 190, 250, 10), 3, 1, "#FFFFFF", 0.7))
    out.append(taper(ell_pts(cx, cy, R * 0.86, R * 0.86, 10, 120, 14), 4, 10, "#FFFFFF", 0.18))
    out.append(ink(outer, "#5A0A06", 1.8, seed, 2, 0.6))
    out.append(ink(wall, "#7A0E0A", 1.2, seed + 1, 1, 0.5))
    return "".join(out)


def garlic_bowl(D, cx, cy, r, seed):
    out = [banchan_dish(D, cx, cy, r, "none", seed, tilt=1.0, glaze=WHITE, rim="#2E5AA8")]
    rnd = random.Random(seed)
    m = blob(cx, cy, r * 0.66, r * 0.62, seed + 2, 0.12, 14)
    out.append(f'<path d="{m}" fill="#F4ECC8"/>')
    for _ in range(int(r * 3)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.6
        out.append(f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" r="{rnd.uniform(1, 2.2):.1f}" fill="{rnd.choice(["#FFFBEA", "#E8D8A0", "#F8F0D0"])}"/>')
    out.append(ink(m, "#B8A870", 1, seed, 1, 0.5))
    return "".join(out)


def radish(D, x, y, Ls, W, ang, seed):
    """Korean radish (mu): stout white root blushing green at the shoulder, leaf stalks on top."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for i in range(13):
        t = i / 12
        w = W * (0.85 + 0.15 * math.sin(math.pi * t)) * (1 - 0.6 * max(0, t - 0.75) / 0.25)
        pts.append((x + ux * Ls * t + nx * w / 2, y + uy * Ls * t + ny * w / 2))
    pts += [(x + ux * Ls * (i / 12) - nx * W * (0.85 + 0.15 * math.sin(math.pi * i / 12)) * (1 - 0.6 * max(0, i / 12 - 0.75) / 0.25) / 2,
             y + uy * Ls * (i / 12) - ny * W * (0.85 + 0.15 * math.sin(math.pi * i / 12)) * (1 - 0.6 * max(0, i / 12 - 0.75) / 0.25) / 2) for i in range(12, -1, -1)]
    out = [cast(D, x + ux * Ls * 0.5 + 8, y + uy * Ls * 0.5 + 10, Ls * 0.55, W * 0.6, strength=0.3, seed=seed)]
    # leaves first
    for k in range(4):
        b = a + math.pi + math.radians(-30 + k * 20)
        e = (x + math.cos(b) * Ls * 0.55, y + math.sin(b) * Ls * 0.55)
        out.append(leaf_simple(D, x, y, Ls * 0.55, W * 0.28, math.degrees(b), ("#8AC04A", "#4E8A2A", "#245014"), seed + k, vein=True, inkw=1.1))
    d = smooth_closed(pts)
    g = D.lin([(0, "#C8E08A"), (0.3, "#F2F6E2"), (1, "#FFFFFF")], x, y, x + ux * Ls, y + uy * Ls, "userSpaceOnUse")
    out.append(f'<path d="{d}" fill="{g}"/>')
    out.append(clipped(D, d, [shade_over(D, d, "#6A7A9A", 0.35, 0, 0, 1, 1, 0.45),
                              strokes(D.nid(), d, bbox(pts), ["#FFFFFF", "#D8DCC8"], seed, n=20, angle=ang, length=(10, 30), width=(1, 2.4), opacity=(0.2, 0.5))]
                       + [f'<path d="M {x + ux * Ls * t - nx * W * 0.3:.1f} {y + uy * Ls * t - ny * W * 0.3:.1f} l {nx * W * 0.2:.1f} {ny * W * 0.2:.1f}" stroke="#B8B4A0" stroke-width="1" opacity="0.6"/>' for t in (0.3, 0.5, 0.65, 0.8)]))
    out.append(ink(d, "#8A8A6A", 1.5, seed, 2, 0.6))
    out.append(pline([(x + ux * Ls, y + uy * Ls), (x + ux * Ls * 1.12 + nx * 3, y + uy * Ls * 1.12 + ny * 3)], "#B8A88A", 1.2, seed, 0.8, 1))
    return "".join(out)


@design("kimchi")
def kimchi():
    D = Doc2("kr-kc")
    out = [jangpan(D, 11)]
    # the basin and three salted cabbage halves being filled
    cx, cy, R = 304, 392, 168
    out.append(red_basin(D, cx, cy, R, 12))
    out.append(cabbage_half(D, 360, 334, 230, 104, -20, 15, paste=0))
    out.append(cabbage_half(D, 238, 420, 236, 108, -64, 13, paste=1.0))
    out.append(cabbage_half(D, 368, 452, 226, 104, -126, 14, paste=0.9))
    # a heap of fresh red filling on one side of the basin
    rnd = random.Random(16)
    for _ in range(26):
        x, y = 196 + rnd.uniform(-34, 34), 300 + rnd.uniform(-20, 20)
        out.append(f'<path d="{blob(x, y, rnd.uniform(10, 18), rnd.uniform(7, 12), rnd.randint(0, 999), 0.3, 10, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8281E", "#B01E14", "#D8402A", "#A8180E"])}"/>')
    for _ in range(30):
        x, y = 196 + rnd.uniform(-36, 36), 300 + rnd.uniform(-20, 20)
        b = rnd.uniform(0, 6.28)
        out.append(taper([(x, y), (x + math.cos(b) * 12, y + math.sin(b) * 12)], 2.6, 2, rnd.choice(["#FFE0C8", "#F8B890"]), 0.95))
    out.append(specks(17, (160, 280, 232, 320), ["#3E8A2E", "#FFF2E2", "#5A0A06"], 30, (1, 2.2), (0.7, 1)))
    # radish, garlic, scallions and the pink gloves around the basin
    out.append(radish(D, 84, 290, 150, 50, 80, 18))
    out.append(garlic_bowl(D, 522, 280, 42, 19))
    out.append(scallion(D, 392, 572, 588, 468, 20, 10))
    out.append(scallion(D, 410, 586, 596, 496, 21, 9))
    out.append(rubber_glove(D, 118, 498, 0.82, -38, 22))
    out.append(rubber_glove(D, 522, 412, 0.76, 196, 23))
    # lettering
    out.append(letters(D, 300, 140, "kimchi", SERIF_IT, 128, "#A8180E", ["#C8281E", "#7A0E0A", "#E0442A"], 24, max_w=360,
                       shadow="#FFF4D0", soff=(0.022, 0.035), angle=-40, hi="#FF9A7A"))
    out.append(ruled(300, 186, "KIMJANG DAY · ALL HANDS IN", "#6A2A0A", font=JOS, size=19, ls=4, line_w=22, gap=10))
    return finish_b(D, out, 25)


# ================================================================ 2. jangdokdae — the jar terrace in winter, a persimmon left for the magpie
def stone_wall(D, x0, x1, y0, y1, seed, pal=STONE, haze=0.0):
    """Dry-stone wall (dol-dam): rounded stones set in pale mortar."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D2E2", haze)) if haze else (lambda c: c)
    d = pd([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    items = [f'<path d="{d}" fill="{hz("#D8D0C0")}"/>']
    y = y0
    row = 0
    while y < y1 + 10:
        h = rnd.uniform(16, 24)
        x = x0 - rnd.uniform(0, 20)
        while x < x1 + 20:
            w = rnd.uniform(22, 40)
            c = mix(pal[1], rnd.choice([pal[0], pal[2], "#A89A84", "#8A8478"]), rnd.uniform(0.1, 0.45))
            sp = blob_pts(x + w / 2, y + h / 2, w / 2 - 1.5, h / 2 - 1.5, rnd.randint(0, 9999), 0.12, 10)
            items.append(f'<path d="{smooth_closed(sp)}" fill="{hz(c)}"/>')
            items.append(f'<path d="{blob(x + w * 0.4, y + h * 0.35, w * 0.28, h * 0.16, rnd.randint(0, 999), 0.2, 8)}" fill="{hz(pal[0])}" opacity="0.5"/>')
            items.append(f'<path d="{smooth_closed(sp)}" fill="none" stroke="{hz(pal[2])}" stroke-width="1.1" opacity="0.55"/>')
            x += w
        y += h
        row += 1
    items.append(shade_over(D, d, "#1A1A2A", 0.3, 0, 0, 0, 1, 0.3))
    return clipped(D, d, items)


def gomusin(D, cx, cy, Ls, seed, col=WHITE, flip=1):
    """Traditional rubber shoe (gomusin) seen from above-side: boat shape with an upturned toe."""
    k = Ls / 100
    sole = L([(-50, 0), (-30, 8), (20, 8), (44, 2), (54, -10), (48, -12), (30, -8), (0, -10), (-36, -10), (-50, -6)], cx, cy, k, flip < 0)
    out = [cast(D, cx + 4, cy + 6, Ls * 0.55, 6, strength=0.35, seed=seed)]
    out.append(painted(D, sole, col, seed, sdir=(0.4, 1), sk=0.2, angle=0, n=8, inkw=1.4, inkc="#5A5A6A", hi=0.4))
    op = ell_pts(cx + (-6 if flip > 0 else 6) * k, cy - 9 * k, 34 * k, 6 * k, 0, 360, 20)[:-1]
    out.append(f'<path d="{smooth_closed(op)}" fill="#6A6A78"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx + (-6 if flip > 0 else 6) * k, cy - 8 * k, 30 * k, 4 * k, 0, 360, 20)[:-1])}" fill="#3A3A48"/>')
    return "".join(out)


@design("jangdokdae")
def jangdokdae():
    D = Doc2("kr-jd")
    out = [sky(D, [(0, "#9AAAC8"), (0.45, "#C8D2E4"), (1, "#EEF0F4")], 31, 600, ["#AAB6D2", "#FFFFFF", "#D8DCEA"], 70, angle=-4, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 120, 230, 220, "#FFF4E0", 0.5))
    # far snowy mountains
    far = ridge([(-20, 236), (80, 196), (170, 222), (270, 184), (380, 214), (470, 190), (620, 226)], 32, 10, 4)
    out.append(hill(D, far, 330, ("#D8DEEC", "#A8B4CE", "#7A88A8"), 33, inkw=1.2, inkop=0.35))
    for i in range(2, len(far) - 2, 4):
        x, y = far[i]
        out.append(f'<path d="{blob(x, y + 6, 16, 5, i, 0.3, 8)}" fill="#FFFFFF" opacity="0.55"/>')
    near = ridge([(-20, 262), (120, 244), (260, 262), (400, 240), (620, 258)], 34, 8, 4)
    out.append(hill(D, near, 330, ("#E8ECF4", "#C0C8DA", "#8A94B0"), 35, inkw=1.2, inkop=0.35))
    # the wall with its little tiled cap, snow on top
    out.append(stone_wall(D, -10, 610, 276, 336, 36))
    out.append(giwa_row(D, -10, 610, 262, 18, 37, snow=True))
    # persimmon tree reaching over the wall, two fruit left for the magpie (kkachi-bap)
    bp = catmull([(640, 196), (560, 214), (500, 232), (440, 248), (396, 270)], 5)
    out.append(bark_branch(D, bp, 16, 6, 38, pal=("#7A5A4A", "#4A3228", "#22140E")))
    out.append(bark_branch(D, catmull([(520, 224), (500, 258), (494, 286)], 4), 7, 3, 39, pal=("#7A5A4A", "#4A3228", "#22140E"), lenticels=False))
    out.append(bark_branch(D, catmull([(470, 240), (446, 218), (420, 210)], 4), 6, 2.5, 40, pal=("#7A5A4A", "#4A3228", "#22140E"), lenticels=False))
    out.append(taper([(560, 206), (500, 224), (440, 240)], 4, 2, "#FFFFFF", 0.9))
    out.append(persimmon(D, 494, 304, 17, 41, snow=True, ang=10))
    out.append(persimmon(D, 404, 286, 14, 42, snow=True, ang=-8, pecked=True))
    out.append(magpie(D, 450, 246, 0.62, 43, flip=False, look=1.0))
    # the terrace: snowy stone platform
    tp = [(-10, 352), (610, 346), (610, 610), (-10, 610)]
    out.append(f'<path d="{pd(tp)}" fill="#EEF0F6"/>')
    out.append(f'<path d="{pd(tp)}" fill="{D.lin([(0, "#B8C0DA", 0.6), (0.4, "#FFFFFF", 0), (1, "#C8D0E4", 0.4)])}"/>')
    out.append(f'<path d="M -10 340 L 610 334 L 610 352 L -10 358 Z" fill="#8A8A90"/>')
    out.append(f'<path d="M -10 336 L 610 330" stroke="#FFFFFF" stroke-width="5"/>')
    out.append(wave_lines(44, (0, 380, 600, 590), ["#C8D0E6", "#FFFFFF"], 26, (30, 80), 2, 1, (0.4, 0.8)))
    # back row of smaller jars, front row of big ones
    for k, (x, b, w, h) in enumerate(((78, 408, 74, 84), (168, 402, 88, 104), (266, 404, 70, 80), (352, 400, 92, 110), (452, 404, 76, 88), (536, 410, 72, 80))):
        out.append(onggi(D, x, b, w, h, 50 + k, lid="dome" if k % 3 else "bowl", snow=True, deco=(k % 2 == 0)))
    for k, (x, b, w, h) in enumerate(((130, 540, 150, 168), (300, 548, 168, 186), (466, 540, 148, 160))):
        out.append(onggi(D, x, b, w, h, 60 + k, lid="dome" if k != 1 else "bowl", snow=True))
    # snow drifts against the front jars and footprints / bird tracks
    for k, (x, y, rx) in enumerate(((210, 548, 40), (388, 554, 40), (560, 546, 50), (40, 546, 40))):
        out.append(f'<path d="{blob(x, y, rx, 9, 70 + k, 0.2, 12)}" fill="#FFFFFF"/>')
    rnd = random.Random(71)
    for k in range(5):
        x, y = 222 + k * 14, 572 - k * 4
        for j in (-1, 0, 1):
            out.append(f'<path d="M {x:.1f} {y:.1f} l {j * 3:.1f} -5" stroke="#9AA4C4" stroke-width="1.4" stroke-linecap="round"/>')
    # falling snow
    out.append(snowflakes(72, 110, (0, 0, 600, 600), avoid=((70, 70, 530, 190),)))
    # lettering
    out.append(letters(D, 300, 128, "jangdokdae", SERIF_IT, 104, "#24365E", ["#34497A", "#18264A", "#4E64A0"], 73, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8B8E8"))
    out.append(ruled(300, 172, "THE JAR TERRACE IN WINTER", "#A8301A", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 74, "#2A2A4A", 0.6)


# ================================================================ 3. kimchi jjigae — bubbling in a ttukbaegi, rice on the side
def ttukbaegi(D, cx, rim_y, rx, h, seed, ry=None):
    """Earthenware stew pot (ttukbaegi): thick rounded rim, dark gritty glaze, wide shallow body."""
    ry = ry or rx * 0.32
    rnd = random.Random(seed)
    bot = rim_y + h
    body = [(cx + rx + 4, rim_y)] + [(cx + rx * 0.98, rim_y + h * 0.4), (cx + rx * 0.84, rim_y + h * 0.82), (cx + rx * 0.62, bot), (cx - rx * 0.62, bot),
                                      (cx - rx * 0.84, rim_y + h * 0.82), (cx - rx * 0.98, rim_y + h * 0.4), (cx - rx - 4, rim_y)]
    body += ell_pts(cx, rim_y, rx + 4, ry + 3, 180, 360, 18)[1:-1]
    d = smooth_closed(body)
    out = [painted(D, body, ("#7A5444", "#3A2218", "#140A06"), seed, sdir=(0.9, 0.3), sk=0.2, angle=-80, n=60, slen=(10, 30), sw=(1, 3),
                   cols=["#8A6450", "#2A160E", "#5A3A2A"], inkw=2, inkop=0.6, hi=0.4, hik=0.05)]
    grit = [specks(seed + 1, (cx - rx, rim_y, cx + rx, bot), ["#B89070", "#1A0A04", "#D8B898"], int(rx * 1.2), (0.6, 1.6), (0.3, 0.7))]
    grit.append(taper([(cx - rx * 0.72, rim_y + h * 0.25), (cx - rx * 0.78, rim_y + h * 0.55), (cx - rx * 0.66, rim_y + h * 0.8)], 8, 2, "#E8C8B0", 0.45))
    grit.append(taper([(cx - rx * 0.66, rim_y + h * 0.3), (cx - rx * 0.7, rim_y + h * 0.5)], 3, 1, "#FFFFFF", 0.6))
    out.append(clipped(D, d, grit))
    # rolled rim: lit top lip
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx + 4, ry + 3)}" fill="#5A3A2A"/>')
    out.append(taper(ell_pts(cx, rim_y, rx + 2, ry + 1.5, 160, 340, 20), 5, 3, "#B08A70", 0.75))
    out.append(ink(ellipse_d(cx, rim_y, rx + 4, ry + 3), INK, 1.6, seed, 1, 0.7))
    return "".join(out)


def tofu_cube(D, cx, cy, s, seed, ang=0, sauce=0.3):
    """A soft tofu cube in 3/4 view (top face lit, two side faces), stained with red broth."""
    top = rot([(cx - s * 0.5, cy - s * 0.18), (cx + s * 0.05, cy - s * 0.42), (cx + s * 0.55, cy - s * 0.2), (cx, cy + s * 0.04)], cx, cy, ang)
    left = rot([(cx - s * 0.5, cy - s * 0.18), (cx, cy + s * 0.04), (cx, cy + s * 0.52), (cx - s * 0.48, cy + s * 0.3)], cx, cy, ang)
    right = rot([(cx, cy + s * 0.04), (cx + s * 0.55, cy - s * 0.2), (cx + s * 0.52, cy + s * 0.26), (cx, cy + s * 0.52)], cx, cy, ang)
    out = []
    for pts, col in ((left, "#EAE0C8"), (right, "#D8CCB0"), (top, "#FFFBF0")):
        dd = smooth_closed(jitter(round_poly(pts, s * 0.08, 3), seed, 0.4))
        out.append(f'<path d="{dd}" fill="{col}"/>')
        out.append(clipped(D, dd, [f'<path d="{blob(cx + s * 0.1, cy + s * 0.4, s * 0.5, s * 0.22, seed, 0.3, 10)}" fill="#E05A32" opacity="{sauce}"/>']))
        out.append(ink(dd, "#A89070", 1, seed, 1, 0.5))
    return "".join(out)


def kimchi_piece(D, x, y, s, ang, seed):
    """A curl of fermented cabbage in the stew: translucent orange leaf with a paler rib."""
    pts = rot(blob_pts(x, y, s, s * 0.45, seed, 0.18, 12), x, y, ang)
    out = [painted(D, pts, ("#FFA070", "#E0552A", "#8A2010"), seed, sdir=(0.5, 0.8), sk=0.2, angle=ang, n=5, inkw=1, inkc="#7A1A0A", inkop=0.5, hi=0.45)]
    a = math.radians(ang)
    out.append(taper([(x - math.cos(a) * s * 0.8, y - math.sin(a) * s * 0.8), (x + math.sin(a) * 2, y - math.cos(a) * 2), (x + math.cos(a) * s * 0.75, y + math.sin(a) * s * 0.75)],
                     s * 0.28, s * 0.1, "#FFD8B0", 0.75))
    return "".join(out)


def pork_slice(D, x, y, s, ang, seed):
    pts = rot(blob_pts(x, y, s, s * 0.42, seed, 0.12, 12), x, y, ang)
    out = [painted(D, pts, ("#F4D2B8", "#D8A080", "#8A5236"), seed, sdir=(0.5, 0.8), sk=0.2, angle=ang, n=5, inkw=1, inkop=0.5, hi=0.4)]
    a = math.radians(ang)
    out.append(taper([(x - math.cos(a) * s * 0.8 - math.sin(a) * s * 0.18, y - math.sin(a) * s * 0.8 + math.cos(a) * s * 0.18),
                      (x + math.cos(a) * s * 0.8 - math.sin(a) * s * 0.2, y + math.sin(a) * s * 0.8 + math.cos(a) * s * 0.2)], s * 0.22, s * 0.18, "#FFF4E8", 0.85))
    return "".join(out)


def scallion_ring(x, y, r, seed):
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.62:.1f}" fill="none" stroke="#4E9A2E" stroke-width="{max(1.6, r * 0.45):.1f}"/>'
            f'<ellipse cx="{x - r * 0.2:.1f}" cy="{y - r * 0.2:.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.25:.1f}" fill="none" stroke="#A8E07A" stroke-width="1" opacity="0.8"/>')


def stew_surface(D, cx, cy, rx, ry, seed, kind="kimchi"):
    """Red broth inside a pot rim: oily sheen, bubbles, kimchi, tofu, pork, scallion, chili slices."""
    rnd = random.Random(seed)
    sd = ellipse_d(cx, cy, rx, ry)
    items = [f'<path d="{sd}" fill="#B8240E"/>',
             f'<path d="{sd}" fill="{D.rad([(0, "#F06A2A", 0.9), (0.6, "#D0381A", 0.5), (1, "#7A1006", 0.6)], 0.42, 0.4, 0.7)}"/>']
    for _ in range(26):
        x, y = cx + rnd.uniform(-rx, rx) * 0.9, cy + rnd.uniform(-ry, ry) * 0.85
        items.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3, 9):.1f}" ry="{rnd.uniform(1.5, 4):.1f}" fill="#FFB050" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out = [clipped(D, sd, items)]
    pieces = []
    for k in range(7):
        a = rnd.uniform(0, 6.28)
        rr = math.sqrt(rnd.uniform(0.05, 0.8))
        pieces.append(("kimchi", cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr))
    for k, (dx, dy) in enumerate(((-0.35, -0.15), (0.2, 0.1), (0.45, -0.3), (-0.1, 0.4))):
        pieces.append(("tofu", cx + dx * rx, cy + dy * ry))
    for k, (dx, dy) in enumerate(((0.05, -0.45), (-0.55, 0.25), (0.55, 0.35))):
        pieces.append(("pork", cx + dx * rx, cy + dy * ry))
    pieces.sort(key=lambda p: p[2])
    for kind_, x, y in pieces:
        if kind_ == "kimchi":
            out.append(kimchi_piece(D, x, y, rx * 0.16, rnd.uniform(-40, 40), rnd.randint(0, 999)))
        elif kind_ == "tofu":
            out.append(tofu_cube(D, x, y, rx * 0.2, rnd.randint(0, 999), rnd.uniform(-10, 10)))
        else:
            out.append(pork_slice(D, x, y, rx * 0.14, rnd.uniform(-30, 30), rnd.randint(0, 999)))
    # bubbles
    for _ in range(16):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        r = rnd.uniform(3, 8)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#E8502A" stroke="#8A1A0A" stroke-width="1" opacity="0.9"/>'
                   f'<path d="M {x - r * 0.5:.1f} {y - r * 0.3:.1f} q {r * 0.3:.1f} {-r * 0.4:.1f} {r * 0.7:.1f} {-r * 0.3:.1f}" stroke="#FFF0D0" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
    for _ in range(14):
        x, y = cx + rnd.uniform(-rx, rx) * 0.8, cy + rnd.uniform(-ry, ry) * 0.7
        out.append(scallion_ring(x, y, rnd.uniform(4, 6.5), rnd.randint(0, 99)))
    for _ in range(5):
        x, y = cx + rnd.uniform(-rx, rx) * 0.7, cy + rnd.uniform(-ry, ry) * 0.6
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5" ry="3.4" fill="#D8241E" stroke="#7A0A06" stroke-width="1.2"/><circle cx="{x - 1:.1f}" cy="{y:.1f}" r="1.4" fill="#FFE08A"/>')
    out.append(specks(seed + 5, (cx - rx, cy - ry, cx + rx, cy + ry), ["#5A0A06", "#FFE0A0"], int(rx * 0.4), (0.6, 1.4), (0.5, 0.9)))
    return "".join(out)


@design("kimchi-jjigae")
def kimchi_jjigae():
    D = Doc2("kr-kj")
    # oxblood wall, warm light from the upper left
    out = [sky(D, [(0, "#6A2420"), (1, "#3A1210")], 81, 600, ["#7A2E28", "#2A0C0A", "#8A3A30"], 110, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 150, 120, 380, "#FFC890", 0.32))
    out.append(blooms(82, ["#8A3A30", "#2A0C0A"], 7, (0, 0, 600, 440), (90, 170), (0.08, 0.14)))
    # dark walnut table
    out.append(wood_planks(D, 430, 600, 83, DARKWOOD, 3))
    out.append(f'<rect y="426" width="600" height="8" fill="#1A0A06" opacity="0.6"/>')
    # woven straw trivet
    tcx, tcy = 262, 512
    out.append(cast(D, tcx + 12, tcy + 8, 176, 34, strength=0.5, seed=84))
    tr = ellipse_d(tcx, tcy, 168, 36)
    out.append(f'<path d="{tr}" fill="#C8A060"/>')
    rings = []
    for k in range(1, 9):
        rings.append(f'<path d="{ellipse_d(tcx, tcy, 168 * k / 8, 36 * k / 8)}" fill="none" stroke="{["#E8C888", "#9A7438"][k % 2]}" stroke-width="3.2" opacity="0.8"/>')
    out.append(clipped(D, tr, rings))
    out.append(ink(tr, INK, 1.6, 85, 1, 0.6))
    # the pot and its stew
    pcx, rim_y, rx = 262, 346, 140
    out.append(ttukbaegi(D, pcx, rim_y, rx, 150, 86))
    out.append(stew_surface(D, pcx, rim_y + 2, rx - 10, rx * 0.3 - 6, 87))
    # rice bowl and the spoon & chopsticks
    out.append(steel_bowl(D, 470, 420, 62, 66, 88))
    out.append(spoon_chopsticks(D, 300, 548, -8, 210, 89))
    # a small dish of kkakdugi
    out.append(banchan_dish(D, 84, 492, 46, "kkakdugi", 90, rim="#2E5AA8"))
    # steam
    out.append(steam(262, 300, 130, 91, "#FFFFFF", 3, 40, 10, 0.4))
    out.append(steam(470, 380, 60, 92, "#FFFFFF", 2, 20, 5, 0.35))
    # lettering
    out.append(letters(D, 300, 132, "kimchi jjigae", SERIF_IT, 92, "#FFE8C8", ["#FFFFFF", "#F8D0A0", "#FFE0B8"], 93, max_w=470,
                       shadow="#1A0604", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 178, "THE CURE FOR EVERYTHING", "#F6B060", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 94)


# ================================================================ 4. bibimbap — a sizzling stone bowl, before you mix it
def dolsot(D, cx, rim_y, rx, ry, depth, seed):
    """Hot stone bowl (dolsot) in 3/4 view on its wooden holder: speckled granite, thick lip."""
    rnd = random.Random(seed)
    out = []
    # wooden holder
    hy = rim_y + depth + 10
    out.append(cast(D, cx + 16, hy + 20, rx * 1.15, ry * 0.5, strength=0.55, seed=seed))
    hold = ell_pts(cx, hy, rx * 1.02, ry * 0.5, 0, 180, 20) + ell_pts(cx, hy - 16, rx * 1.02, ry * 0.5, 180, 360, 20)
    out.append(painted(D, hold, ("#C8925A", "#8A5A2E", "#4A2A12"), seed, sdir=(0.6, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(f'<path d="{ellipse_d(cx, hy - 16, rx * 1.02, ry * 0.5)}" fill="#A8743E"/>')
    out.append(strokes(D.nid(), ellipse_d(cx, hy - 16, rx * 1.02, ry * 0.5), (cx - rx * 1.1, hy - 16 - ry * 0.5, cx + rx * 1.1, hy - 16 + ry * 0.5),
                       ["#D8A870", "#7A4A22"], seed + 1, n=30, angle=0, length=(30, 80), width=(1, 2.4), opacity=(0.25, 0.5)))
    # stone body
    body = [(cx + rx, rim_y)] + [(cx + rx * 0.97, rim_y + depth * 0.5), (cx + rx * 0.82, rim_y + depth), (cx, rim_y + depth + ry * 0.35),
                                  (cx - rx * 0.82, rim_y + depth), (cx - rx * 0.97, rim_y + depth * 0.5), (cx - rx, rim_y)]
    body += ell_pts(cx, rim_y, rx, ry, 180, 360, 24)[1:-1]
    d = smooth_closed(body)
    out.append(painted(D, body, ("#6A6A70", "#34343A", "#121216"), seed + 2, sdir=(0.9, 0.3), sk=0.18, angle=-80, n=40, inkw=2, inkc="#0A0A0C", hi=0.35))
    out.append(clipped(D, d, [specks(seed + 3, (cx - rx, rim_y, cx + rx, rim_y + depth + ry), ["#9A9AA2", "#C8C8D0", "#0A0A0C"], int(rx * 2.2), (0.6, 1.6), (0.3, 0.8)),
                              taper([(cx - rx * 0.86, rim_y + depth * 0.2), (cx - rx * 0.8, rim_y + depth * 0.7)], 8, 2, "#B8B8C8", 0.4)]))
    # thick lip
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx, ry)}" fill="#4A4A52"/>')
    out.append(f'<path d="{ellipse_d(cx, rim_y + 2, rx * 0.9, ry * 0.86)}" fill="#1E1E24"/>')
    out.append(taper(ell_pts(cx, rim_y, rx * 0.95, ry * 0.93, 160, 340, 24), 6, 4, "#9A9AA8", 0.7))
    out.append(ink(ellipse_d(cx, rim_y, rx, ry), "#0A0A0C", 1.6, seed, 1, 0.7))
    return "".join(out)


def namul_sector(D, cx, cy, rx, ry, a0, a1, kind, seed):
    """One wedge of topping inside the bowl (angles in degrees; ellipse rx, ry is the food surface)."""
    rnd = random.Random(seed)
    r0 = 0.3
    pts = [(cx + math.cos(math.radians(a)) * rx * r0, cy + math.sin(math.radians(a)) * ry * r0) for a in (a0, (a0 + a1) / 2, a1)]
    pts += [(cx + math.cos(math.radians(a0 + (a1 - a0) * (1 - i / 10))) * rx, cy + math.sin(math.radians(a0 + (a1 - a0) * (1 - i / 10))) * ry) for i in range(11)][::-1][::-1]
    pts = [(cx + math.cos(math.radians(a)) * rx * r0, cy + math.sin(math.radians(a)) * ry * r0) for a in (a1, (a0 + a1) / 2, a0)]
    pts += [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / 10)) * rx * 0.98, cy + math.sin(math.radians(a0 + (a1 - a0) * i / 10)) * ry * 0.98) for i in range(11)]
    d = smooth_closed(jitter(pts, seed, 2))
    base = {"spinach": "#2E5A1E", "sprouts": "#EAE4C2", "carrot": "#E8721E", "mushroom": "#6A3E22", "zucchini": "#A8C870",
            "gosari": "#7A5230", "beef": "#4A2414", "radish": "#F2E2D8"}[kind]
    items = [f'<path d="{d}" fill="{base}"/>']
    x0, y0, x1, y1 = bbox(pts)
    n = int((x1 - x0) * (y1 - y0) / 40) + 10
    for _ in range(n):
        a = math.radians(rnd.uniform(a0, a1))
        rr = rnd.uniform(r0, 1.0)
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        b = rnd.uniform(0, 6.28)
        if kind == "spinach":
            Ls = rnd.uniform(10, 22)
            items.append(taper([(x, y), (x + math.cos(b) * Ls, y + math.sin(b) * Ls * 0.5)], rnd.uniform(3, 6), 1, rnd.choice(["#4E8A2E", "#3A7020", "#6AA43A", "#245014"]), 0.95))
        elif kind == "sprouts":
            Ls = rnd.uniform(14, 26)
            ex, ey = x + math.cos(b) * Ls, y + math.sin(b) * Ls * 0.5
            items.append(taper([(x, y), ((x + ex) / 2 + 2, (y + ey) / 2 - 2), (ex, ey)], 2.6, 1.6, rnd.choice(["#FFFDF0", "#F4EED0", "#FFFFFF"]), 1))
            items.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="2.8" ry="2" fill="#F2D24A"/>')
        elif kind == "carrot":
            Ls = rnd.uniform(14, 24)
            items.append(taper([(x, y), (x + math.cos(b) * Ls, y + math.sin(b) * Ls * 0.5)], 3, 2.4, rnd.choice(["#F2862A", "#E8681A", "#FFA850"]), 1))
        elif kind == "mushroom":
            items.append(taper([(x, y), (x + math.cos(b) * 12, y + math.sin(b) * 6)], 6, 4, rnd.choice(["#7A4A2A", "#5A3018", "#9A6A44"]), 1))
            items.append(taper([(x, y - 1), (x + math.cos(b) * 10, y + math.sin(b) * 5 - 1)], 1.5, 1, "#D8B890", 0.7))
        elif kind == "zucchini":
            items.append(f'<path d="{blob(x, y, 8, 5, rnd.randint(0, 999), 0.1, 10, math.degrees(b))}" fill="{rnd.choice(["#C8E09A", "#B0D080", "#D8EAB0"])}" stroke="#4E7A2A" stroke-width="1.6"/>')
        elif kind == "gosari":
            Ls = rnd.uniform(14, 26)
            items.append(taper([(x, y), (x + math.cos(b) * Ls * 0.5 + 3, y + math.sin(b) * Ls * 0.25 - 2), (x + math.cos(b) * Ls, y + math.sin(b) * Ls * 0.5)], 3.6, 2.4, rnd.choice(["#8A5E36", "#6A4424", "#A07448"]), 1))
        elif kind == "beef":
            items.append(f'<path d="{blob(x, y, rnd.uniform(5, 9), rnd.uniform(3, 5), rnd.randint(0, 999), 0.3, 8, math.degrees(b))}" fill="{rnd.choice(["#5A2E18", "#3A1A0C", "#7A4426"])}"/>')
        elif kind == "radish":
            Ls = rnd.uniform(14, 24)
            items.append(taper([(x, y), (x + math.cos(b) * Ls, y + math.sin(b) * Ls * 0.5)], 3, 2.4, rnd.choice(["#FFF6F0", "#F8C8B8", "#E87A6A"]), 1))
    items.append(shade_over(D, d, "#0A0604", 0.3, 0, 0, 0, 1, 0.4))
    return clipped(D, d, items) + ink(d, "#1A0E08", 0.9, seed, 1, 0.35)


def fried_egg(D, cx, cy, r, seed, squash=1.0):
    pts = blob_pts(cx, cy, r, r * squash, seed, 0.16, 20)
    out = [painted(D, pts, ("#FFFFFF", "#FBF6EA", "#C8BFAE"), seed, sdir=(0.5, 0.8), sk=0.1, angle=-30, n=10, inkw=1.2, inkc="#A89880", inkop=0.5, hi=0.4)]
    rnd = random.Random(seed)
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        out.append(taper([(cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85 * squash), (cx + math.cos(a + 0.4) * r * 0.95, cy + math.sin(a + 0.4) * r * 0.95 * squash)], 3, 1, "#E8C890", 0.6))
    yx, yy = cx + r * 0.05, cy - r * 0.05
    yp = blob_pts(yx, yy, r * 0.42, r * 0.4 * squash, seed + 1, 0.04, 16)
    out.append(painted(D, yp, ("#FFD860", "#F6A41A", "#C0640A"), seed + 1, sdir=(0.5, 0.8), sk=0.22, angle=-40, n=8, inkw=1.2, inkc="#A0500A", inkop=0.5, hi=0.45))
    out.append(f'<path d="{blob(yx - r * 0.14, yy - r * 0.14 * squash, r * 0.13, r * 0.08, seed + 2, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


@design("bibimbap")
def bibimbap():
    D = Doc2("kr-bb")
    # slate-blue backdrop, a warm pool of light on a pale wood table
    out = [sky(D, [(0, "#26323E"), (1, "#18202A")], 101, 600, ["#34424E", "#121820", "#3E4E5A"], 100, angle=-80, sop=(0.08, 0.2))]
    out.append(blooms(102, ["#3E4E5A", "#121820"], 6, (0, 0, 600, 420), (90, 170), (0.08, 0.14)))
    out.append(wood_planks(D, 420, 600, 103, PALEWOOD, 3))
    out.append(f'<rect y="416" width="600" height="8" fill="#0A0E14" opacity="0.6"/>')
    out.append(soft_glow(D, 300, 420, 300, "#FFE8B8", 0.3))
    cx, rim_y, rx, ry = 300, 362, 190, 84
    out.append(dolsot(D, cx, rim_y, rx, ry, 116, 104))
    frx, fry = rx * 0.86, ry * 0.8
    fcy = rim_y + 6
    # toppings in a wheel, the classic order of colours
    kinds = ["spinach", "carrot", "sprouts", "mushroom", "zucchini", "beef", "radish", "gosari"]
    for k, kind in enumerate(kinds):
        a0 = -112 + k * 45
        out.append(namul_sector(D, cx, fcy, frx, fry, a0, a0 + 47, kind, 110 + k))
    # sizzling crust peeking at the rim + oil bubbles
    rnd = random.Random(120)
    for _ in range(40):
        a = rnd.uniform(0, 6.28)
        x, y = cx + math.cos(a) * frx * 0.99, fcy + math.sin(a) * fry * 0.99
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.2, 2.6):.1f}" fill="none" stroke="#FFE8B0" stroke-width="1" opacity="0.8"/>')
    # egg, gochujang, sesame
    out.append(fried_egg(D, cx - 10, fcy - 6, 60, 121, squash=0.55))
    gp = blob_pts(cx + 52, fcy + 16, 22, 13, 122, 0.12, 14)
    out.append(painted(D, gp, ("#E8503A", "#B01E14", "#5A0A06"), 122, sdir=(0.5, 0.8), sk=0.22, angle=-20, n=6, inkw=1.1, inkop=0.5, hi=0.5))
    out.append(taper([(cx + 42, fcy + 10), (cx + 56, fcy + 6)], 3, 1, "#FFD0C0", 0.8))
    for _ in range(46):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * frx * rr, fcy + math.sin(a) * fry * rr
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.4" ry="1.4" fill="#FFF4D8" stroke="#A8885A" stroke-width="0.5" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    out.append(specks(123, (cx - 60, fcy - 30, cx + 60, fcy + 30), ["#2A1A10"], 14, (0.8, 1.4), (0.8, 1)))
    # spoon resting on the table, little dishes
    out.append(spoon_chopsticks(D, 70, 540, -14, 190, 124))
    out.append(banchan_dish(D, 512, 520, 38, "kimchi", 125, rim="#2E5AA8"))
    # steam lit warm
    out.append(steam(250, 300, 120, 126, "#FFF4E0", 2, 60, 9, 0.35))
    out.append(steam(370, 290, 110, 127, "#FFF4E0", 2, 40, 8, 0.3))
    # lettering
    out.append(letters(D, 300, 140, "bibimbap", SERIF_IT, 120, "#FFE6B8", ["#FFFFFF", "#F8D490", "#FFE6B8"], 128, max_w=440,
                       shadow="#0A0E14", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 186, "MIX IT LIKE YOU MEAN IT", "#F2A040", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 129)


# ================================================================ 5. kkachi horangi — the tiger and the magpie, a minhwa folk painting
def minhwa_pine(D, seed):
    """A twisting folk-painting pine: scaly red-brown trunk, branches ending in fan-shaped needle tufts."""
    rnd = random.Random(seed)
    out = []
    trunk = catmull([(120, 610), (96, 520), (130, 430), (104, 340), (150, 262), (232, 214), (330, 196)], 6)
    out.append(taper(trunk, 64, 18, "#6A3A22"))
    out.append(taper([(x - 12, y) for x, y in trunk], 22, 6, "#A86A42", 0.7))
    out.append(taper([(x + 16, y + 2) for x, y in trunk], 18, 4, "#3A1A0C", 0.6))
    # bark scales
    for i in range(2, len(trunk) - 4, 2):
        x, y = trunk[i]
        w = 64 - 46 * i / len(trunk)
        for k in range(2):
            sx = x + rnd.uniform(-w * 0.3, w * 0.3)
            out.append(f'<path d="{blob(sx, y + rnd.uniform(-6, 6), w * 0.16, w * 0.08, rnd.randint(0, 999), 0.2, 8, rnd.uniform(-20, 20))}" fill="none" stroke="#3A1A0C" stroke-width="1.6" opacity="0.7"/>')
    out.append(ink(smooth_open([(x - 30, y) for x, y in trunk[:len(trunk) // 2]]), INK, 1.6, seed, 1, 0.5))
    # branches with tufts
    br = [((136, 420), [(136, 420), (80, 380), (70, 344)]), ((112, 336), [(112, 336), (170, 318), (220, 316)]), ((210, 226), [(210, 226), (196, 200), (186, 180)]),
          ((300, 200), [(300, 200), (360, 214), (420, 210)])]
    for (sx, sy), pts in br:
        out.append(taper(catmull(pts, 5), 14, 5, "#6A3A22"))
    tufts = [(70, 340, 40, -110), (40, 372, 34, -150), (110, 360, 32, -70), (226, 312, 40, -60), (186, 318, 32, -100), (262, 318, 30, -30),
             (186, 176, 40, -90), (156, 196, 32, -140), (222, 188, 32, -50), (420, 206, 42, -60), (380, 196, 36, -100), (458, 218, 34, -20),
             (330, 188, 38, -80), (290, 196, 30, -120)]
    for k, (x, y, r, a) in enumerate(tufts):
        out.append(needle_tuft(D, x, y, r, seed + k, pal=("#7AA864", "#2E6A44", "#1A3A26"), ang=a, spread=150, n=24))
    return "".join(out)


def fur(D, d, box, seed, cols, n, angle, length=(5, 11), width=(1.2, 2.4), op=(0.35, 0.8)):
    """Short fur flicks clipped inside a form."""
    return strokes(D.nid(), d, box, cols, seed, n=n, angle=angle, length=length, width=width, opacity=op, curve=0.35)


def stripe(cx, cy, Ls, ang, w, col="#24140A", fork=False):
    """A tiger stripe: a tapered brush mark thick in the middle, optionally forked at one end."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    p0 = (cx - ux * Ls / 2, cy - uy * Ls / 2)
    p1 = (cx + ux * Ls / 2 + nx * Ls * 0.08, cy + uy * Ls / 2 + ny * Ls * 0.08)
    mid = (cx + nx * Ls * 0.06, cy + ny * Ls * 0.06)
    pts = [p0, (p0[0] * 0.5 + mid[0] * 0.5 + nx * w * 0.6, p0[1] * 0.5 + mid[1] * 0.5 + ny * w * 0.6), mid,
           (mid[0] * 0.5 + p1[0] * 0.5 + nx * w * 0.4, mid[1] * 0.5 + p1[1] * 0.5 + ny * w * 0.4), p1,
           (mid[0] * 0.5 + p1[0] * 0.5 - nx * w * 0.5, mid[1] * 0.5 + p1[1] * 0.5 - ny * w * 0.5), (mid[0] - nx * w * 0.5, mid[1] - ny * w * 0.5),
           (p0[0] * 0.5 + mid[0] * 0.5 - nx * w * 0.4, p0[1] * 0.5 + mid[1] * 0.5 - ny * w * 0.4)]
    out = f'<path d="{smooth_closed(pts)}" fill="{col}"/>'
    if fork:
        q = (p1[0] - ux * Ls * 0.25 - nx * w * 1.2, p1[1] - uy * Ls * 0.25 - ny * w * 1.2)
        out += taper([mid, q], w * 0.6, 0.6, col)
    return out


def minhwa_tiger(D, ox, oy, s, seed):
    """The folk tiger of the hojakdo: seated, big round goggling eyes turned up toward the magpie, a striped and
    furred coat, white ruff and chest, a thick banded tail curling up behind. (ox, oy) = ground under its middle."""
    rnd = random.Random(seed)

    def P(pts):
        return L(pts, ox, oy, s)

    coat = ("#FFCC78", "#EE9A32", "#A8580E")
    furc = ["#FFE0A0", "#C8701A", "#F6B050", "#A8580E"]
    out = [cast(D, ox + 14 * s, oy, 160 * s, 14 * s, strength=0.4, seed=seed)]
    # thick banded tail rising behind the haunch in an S, black tip
    tp = catmull(P([(110, -30), (156, -54), (176, -110), (156, -160), (162, -208), (192, -228)]), 7)
    out.append(taper(tp, 30 * s, 20 * s, coat[1]))
    out.append(taper([(x - 6 * s, y) for x, y in tp], 10 * s, 6 * s, coat[0], 0.7))
    out.append(taper([(x + 7 * s, y + 2 * s) for x, y in tp], 8 * s, 4 * s, coat[2], 0.55))
    for i in range(4, len(tp) - 3, 5):
        x, y = tp[i]
        dx, dy = tp[i + 1][0] - tp[i - 1][0], tp[i + 1][1] - tp[i - 1][1]
        Ls = math.hypot(dx, dy) or 1
        out.append(stripe(x, y, 30 * s * (1 - 0.3 * i / len(tp)), math.degrees(math.atan2(dy, dx)) + 90, 7 * s))
    out.append(taper(tp[-7:], 21 * s, 19 * s, "#24140A"))
    out.append(f'<path d="{blob(tp[-1][0], tp[-1][1], 10 * s, 9.5 * s, seed, 0.08, 10)}" fill="#24140A"/>')
    # body and haunch
    body = P([(-72, -150), (-30, -174), (40, -152), (100, -122), (132, -72), (126, -20), (84, 0), (20, -4), (-40, -4), (-78, -40), (-90, -100)])
    bd = smooth_closed(body)
    out.append(painted(D, body, coat, seed + 1, sdir=(0.6, 0.6), sk=0.15, angle=-60, n=40, cols=furc, inkw=0, hi=0.4))
    inner = [fur(D, bd, bbox(body), seed + 2, furc, 260, -70)]
    # haunch rounding
    hx, hy = P([(70, -66)])[0]
    inner.append(f'<path d="{blob(hx, hy, 62 * s, 58 * s, seed + 3, 0.05, 18)}" fill="none" stroke="{coat[2]}" stroke-width="{3 * s:.1f}" opacity="0.45"/>')
    inner.append(shade_over(D, bd, "#5A2A06", 0.35, 0, 0, 1, 1, 0.5))
    for (x, y, Ls, a, fk) in ((16, -150, 52, 75, True), (46, -138, 56, 78, False), (76, -122, 50, 84, True), (100, -100, 42, 96, False), (-12, -156, 36, 82, False),
                              (116, -58, 40, 120, True), (86, -76, 36, 128, False), (62, -40, 40, 140, False), (96, -30, 30, 160, False)):
        cx_, cy_ = P([(x, y)])[0]
        inner.append(stripe(cx_, cy_, Ls * s, a, 9 * s, fork=fk))
    out.append(clipped(D, bd, inner))
    out.append(ink(bd, INK, 2.2, seed + 4, 2, 0.7))
    # hind paw
    hp = blob_pts(*P([(106, -9)])[0], 32 * s, 13 * s, seed + 5, 0.1, 14)
    out.append(painted(D, hp, coat, seed + 5, sk=0.2, n=8, inkw=1.8, hi=0.4))
    for j in range(3):
        x, y = P([(92 + j * 10, -8)])[0]
        out.append(pline([(x, y - 3 * s), (x + 1, y + 5 * s)], INK, 1.3, seed + j, 0.7, 1))
    # white chest ruff
    chest = P([(-86, -124), (-54, -138), (-22, -112), (-18, -60), (-38, -20), (-76, -30), (-94, -84)])
    cd = smooth_closed(chest)
    out.append(painted(D, chest, ("#FFFFFF", "#FBF2E2", "#C8B498"), seed + 6, sdir=(0.6, 0.6), sk=0.15, angle=-80, n=14, inkw=0, hi=0.3))
    out.append(clipped(D, cd, [fur(D, cd, bbox(chest), seed + 7, ["#FFFFFF", "#D8C8B0", "#E8DCC8"], 70, -95, (6, 12))]))
    for k in range(5):
        x, y = P([(-76 + k * 10, -104 + k * 14)])[0]
        out.append(pline([(x - 7 * s, y), (x, y + 5 * s), (x + 7 * s, y)], "#B8A488", 1.3, seed + k, 0.6, 1))
    out.append(ink(cd, "#8A7A60", 1.4, seed + 8, 1, 0.5))
    # front legs with striped fronts and round white paws
    for k, lx in enumerate((-76, -34)):
        lg = P([(lx - 16, -96), (lx + 16, -96), (lx + 17, -14), (lx - 17, -14)])
        ld = smooth_closed(lg)
        out.append(painted(D, lg, coat, seed + 9 + k, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=12, cols=furc, inkw=0, hi=0.4))
        legs = [fur(D, ld, bbox(lg), seed + 11 + k, furc, 40, -95)]
        for j in range(4):
            y = -80 + j * 16
            cx_, cy_ = P([(lx - 6, y)])[0]
            legs.append(stripe(cx_, cy_, 26 * s, 8, 6 * s))
        out.append(clipped(D, ld, legs))
        out.append(ink(ld, INK, 1.9, seed + 13 + k, 1, 0.7))
        pw = blob_pts(*P([(lx + 2, -10)])[0], 22 * s, 12 * s, seed + 15 + k, 0.08, 14)
        out.append(painted(D, pw, ("#FFFFFF", "#FBF2E2", "#C8B498"), seed + 15 + k, sk=0.2, n=6, inkw=1.6, hi=0.3))
        for j in (-1, 0, 1):
            x, y = P([(lx + 2 + j * 8, -12)])[0]
            out.append(pline([(x, y - 4 * s), (x, y + 4 * s)], INK, 1.3, seed + j, 0.7, 1))
    # head with a spiky cheek ruff
    hcx, hcy = P([(-56, -184)])[0]
    for sg in (-1, 1):
        ex, ey = hcx + sg * 46 * s, hcy - 46 * s
        ep = blob_pts(ex, ey, 18 * s, 17 * s, seed + 17 + sg, 0.06, 12)
        out.append(painted(D, ep, coat, seed + 17 + sg, sk=0.2, n=4, inkw=1.6, hi=0.4))
        out.append(f'<path d="{blob(ex, ey + 2 * s, 10 * s, 10 * s, seed + 18 + sg, 0.08, 10)}" fill="#24140A"/>')
        out.append(f'<path d="{blob(ex, ey + 4 * s, 5 * s, 6 * s, seed + 19 + sg, 0.08, 10)}" fill="#FFFFFF"/>')
    # cheek ruffs: white spiky tufts flaring out at the jaw on both sides
    for sg in (-1, 1):
        tuft = [(hcx + sg * 40 * s, hcy - 14 * s)]
        for j in range(7):
            a = math.radians(-30 + j * 18)
            r = (70 if j % 2 == 0 else 58) * s
            tuft.append((hcx + sg * math.cos(a) * r, hcy + 8 * s + math.sin(a) * r * 0.8))
        tuft.append((hcx + sg * 30 * s, hcy + 44 * s))
        out.append(painted(D, tuft, ("#FFFFFF", "#F6EAD4", "#C8B498"), seed + 20 + sg, sdir=(0.6, 0.6), sk=0.12, angle=-60, n=10, inkw=1.4, inkop=0.5, hi=0.3))
    head = blob_pts(hcx, hcy, 64 * s, 56 * s, seed + 21, 0.04, 26)
    hd = smooth_closed(head)
    out.append(painted(D, head, coat, seed + 21, sdir=(0.6, 0.7), sk=0.12, angle=-30, n=30, cols=furc, inkw=0, hi=0.45))
    hs = [fur(D, hd, bbox(head), seed + 22, furc, 140, -80, (5, 9))]
    for (x, y, Ls, a) in ((-28, -40, 26, 92), (0, -48, 30, 90), (28, -40, 26, 88), (-14, -32, 16, 84), (14, -32, 16, 96),
                          (-60, -10, 28, 12), (-58, 10, 24, -12), (60, -10, 28, 168), (58, 10, 24, 192)):
        hs.append(stripe(hcx + x * s, hcy + y * s, Ls * s, a, 7 * s))
    hs.append(shade_over(D, hd, "#5A2A06", 0.3, 0, 0, 1, 1, 0.55))
    out.append(clipped(D, hd, hs))
    out.append(ink(hd, INK, 2.2, seed + 23, 2, 0.75))
    # white muzzle puffs with whisker spots, white brows
    for sg in (-1, 1):
        mp = blob_pts(hcx + sg * 17 * s, hcy + 24 * s, 22 * s, 17 * s, seed + 24 + sg, 0.06, 14)
        out.append(painted(D, mp, ("#FFFFFF", "#FBF2E2", "#C8B498"), seed + 24 + sg, sk=0.15, n=6, inkw=1.4, hi=0.3))
        for j in range(4):
            out.append(f'<circle cx="{hcx + sg * (10 + j * 6) * s:.1f}" cy="{hcy + (19 + (j % 2) * 6) * s:.1f}" r="{1.7 * s:.1f}" fill="#4A3020"/>')
        for j in range(3):
            out.append(pline([(hcx + sg * 32 * s, hcy + (22 + j * 5) * s), (hcx + sg * 50 * s, hcy + (16 + j * 7) * s), (hcx + sg * 74 * s, hcy + (12 + j * 10) * s)], "#3A2418", 1.3, seed + j, 0.75, 1))
        out.append(painted(D, blob_pts(hcx + sg * 22 * s, hcy - 25 * s, 15 * s, 6 * s, seed + 26 + sg, 0.12, 10, sg * -14), ("#FFFFFF", "#FBF2E2", "#C8B498"), seed + 26 + sg, sk=0.1, n=3, inkw=1.2, hi=0.3))
    # big round eyes, goggling up and left
    for sg in (-1, 1):
        ex, ey = hcx + sg * 22 * s, hcy - 6 * s
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{14.5 * s:.1f}" fill="#FFFDF2"/>')
        out.append(f'<circle cx="{ex - 3 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{10 * s:.1f}" fill="#F2B81C"/>')
        out.append(f'<circle cx="{ex - 3 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{10 * s:.1f}" fill="none" stroke="#A8700A" stroke-width="{1.6 * s:.1f}"/>')
        out.append(f'<circle cx="{ex - 4.5 * s:.1f}" cy="{ey - 4.5 * s:.1f}" r="{5.5 * s:.1f}" fill="#120A04"/>')
        out.append(f'<circle cx="{ex - 6.5 * s:.1f}" cy="{ey - 6.5 * s:.1f}" r="{2 * s:.1f}" fill="#FFFFFF"/>')
        out.append(ink(ellipse_d(ex, ey, 14.5 * s, 14.5 * s, 20), "#24140A", 2.8 * s, seed + sg, 1, 0.9))
    # nose, grin with little fangs
    nx_, ny_ = hcx, hcy + 12 * s
    out.append(f'<path d="{smooth_closed([(nx_ - 10 * s, ny_ - 4 * s), (nx_ + 10 * s, ny_ - 4 * s), (nx_ + 2 * s, ny_ + 6 * s), (nx_ - 2 * s, ny_ + 6 * s)])}" fill="#C85A4A" stroke="#5A1A10" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(nx_ - 3 * s, ny_ - 2 * s, 3 * s, 1.5 * s, seed, 0.1, 8)}" fill="#FFD0C0"/>')
    out.append(pline([(nx_, ny_ + 6 * s), (nx_, ny_ + 13 * s)], "#5A1A10", 1.6, seed, 0.9, 1))
    mouth = [(nx_ - 17 * s, ny_ + 15 * s), (nx_ - 7 * s, ny_ + 25 * s), (nx_ + 7 * s, ny_ + 25 * s), (nx_ + 17 * s, ny_ + 15 * s), (nx_, ny_ + 17 * s)]
    out.append(f'<path d="{smooth_closed(mouth)}" fill="#C83A3A" stroke="#5A1A10" stroke-width="1.4"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{pd([(nx_ + sg * 11 * s, ny_ + 17 * s), (nx_ + sg * 8 * s, ny_ + 23 * s), (nx_ + sg * 5 * s, ny_ + 17.5 * s)])}" fill="#FFFFFF"/>')
    return "".join(out)


def seal(D, cx, cy, s, seed, col="#C8281E", paper_c=HANJI, rot_=-2, mark="double"):
    """A square red seal with an abstract carved border motif (no characters)."""
    rnd = random.Random(seed)
    half = s / 2
    out = [f'<g transform="rotate({rot_} {cx} {cy})">', f'<path d="{hg.org_rect(cx - half, cy - half, s, s, seed, 0.8, 8, s * 0.08)}" fill="{col}" opacity="0.92"/>']
    out.append(f'<path d="{hg.org_rect(cx - half + s * 0.1, cy - half + s * 0.1, s * 0.8, s * 0.8, seed + 1, 0.5, 8, 2)}" stroke="{paper_c}" stroke-width="{s * 0.05:.1f}" fill="none"/>')
    if mark == "double":
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{s * 0.18:.1f}" fill="none" stroke="{paper_c}" stroke-width="{s * 0.07:.1f}"/>')
        out.append(f'<path d="M {cx - s * 0.28:.1f} {cy} L {cx + s * 0.28:.1f} {cy} M {cx} {cy - s * 0.28:.1f} L {cx} {cy + s * 0.28:.1f}" stroke="{paper_c}" stroke-width="{s * 0.05:.1f}"/>')
    for _ in range(int(s * 0.5)):
        out.append(f'<circle cx="{cx + rnd.uniform(-half, half):.1f}" cy="{cy + rnd.uniform(-half, half):.1f}" r="{rnd.uniform(0.4, 1.4):.1f}" fill="{paper_c}" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    out.append("</g>")
    return "".join(out)


@design("kkachi-horangi")
def kkachi_horangi():
    D = Doc2("kr-kh")
    # aged mulberry paper with foxing, mounted in an indigo silk border
    out = [hanji(D, "#EAD6AC", "#7A5A30", 141, fibres=90)]
    out.append(blooms(142, ["#C8A870", "#B89058", "#E8D0A0"], 8, (0, 0, 600, 600), (90, 180), (0.08, 0.16)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0), (0.7, "#8A6A3A", 0.05), (1, "#5A3A1A", 0.35)], 0.5, 0.5, 0.72)}"/>')
    out.append(specks(143, (40, 40, 560, 560), ["#A8804A", "#8A6030"], 40, (1, 3.5), (0.15, 0.35)))
    # ground with a few grass flicks and a rock
    out.append(f'<path d="{blob(330, 560, 300, 30, 144, 0.08, 20)}" fill="#C8B080" opacity="0.6"/>')
    rk = blob_pts(512, 520, 46, 32, 145, 0.16, 14)
    out.append(painted(D, rk, ("#A8B0A8", "#6A7A7A", "#3A4444"), 145, sdir=(0.6, 0.7), sk=0.25, angle=-40, n=14, inkw=1.8, hi=0.4))
    out.append(pline([(492, 504), (504, 520), (500, 540)], "#2A3434", 1.4, 146, 0.6, 1))
    for k, (x, y) in enumerate(((180, 548), (210, 556), (430, 552), (560, 546), (90, 550))):
        for j in range(3):
            out.append(taper([(x + j * 5, y), (x + j * 5 - 4 + j * 4, y - 16 - j * 3)], 2.6, 0.6, "#4E7A44", 0.9))
    # pine, magpie, tiger
    out.append(minhwa_pine(D, 147))
    out.append(magpie(D, 236, 314, 0.72, 148, flip=True, beak_open=True, look=0.6))
    out.append(minhwa_tiger(D, 352, 540, 1.0, 149))
    # lettering, top right like a painter's inscription
    out.append(letters(D, 400, 108, "horangi", SERIF_IT, 86, "#3A1A0C", ["#5A2E14", "#24100A"], 150, max_w=270, angle=-40, wob=0.7))
    out.append(label(410, 144, "TIGER & MAGPIE", JOS, 18, "#A8281E", ls=4, max_w=250))
    out.append(seal(D, 240, 92, 24, 151))
    # silk mounting border, bleeding off the edge
    band = 26
    frame = f"M -2 -2 L 602 -2 L 602 602 L -2 602 Z M {band} {band} L {band} {600 - band} L {600 - band} {600 - band} L {600 - band} {band} Z"
    out.append(f'<path d="{frame}" fill="#1E3A5E" fill-rule="evenodd"/>')
    rnd = random.Random(152)
    pat = []
    for i in range(0, 620, 18):
        for (x, y) in ((i, 13), (13, i), (i, 587), (587, i)):
            pat.append(f'<path d="M {x - 4} {y} L {x} {y - 4} L {x + 4} {y} L {x} {y + 4} Z" fill="#C8A048" opacity="0.55"/>')
    out.append(clipped(D, frame, pat))
    out.append(f'<rect x="{band}" y="{band}" width="{600 - 2 * band}" height="{600 - 2 * band}" fill="none" stroke="#C8A048" stroke-width="2.4"/>')
    return finish_b(D, out, 153, "#5A3A1A", 0.8)


# ================================================================ 6. saranghae — painted 사랑해 over a pair of wooden wedding ducks
def wedding_duck(D, ox, oy, s, seed, flip=False, body=("#EE7A62", "#C8301E", "#7A120A"), wing=("#6AA2D8", "#1E5AA8", "#0C2A5E"),
                 neck=("#8ACCA8", "#2E8A62", "#0E4A34")):
    """Carved, hand-painted wooden wedding duck (wonang): plump body on a little pedestal, upturned tail, thick neck,
    rounded head with a flat beak; paint in obangsaek colours over visible wood grain, worn at the edges.
    Faces left unless flip. (ox, oy) = bottom of the pedestal; s ~ 1 for a 180 px long duck."""
    rnd = random.Random(seed)

    def P(pts):
        return L(pts, ox, oy, s, flip)

    sg = -1 if not flip else 1
    out = [cast(D, ox, oy + 3 * s, 100 * s, 9 * s, strength=0.45, seed=seed)]
    # pedestal
    ped = P([(-46, -16), (46, -16), (52, 0), (-52, 0)])
    out.append(painted(D, ped, ("#C8925E", "#8A5A30", "#4A2A12"), seed, sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.3))
    out.append(pline(P([(-48, -8), (48, -8)]), "#4A2A12", 1.2, seed, 0.5, 1))
    # body: plump, flat-bottomed, tail sweeping up at the back
    bodyp = P([(-58, -40), (-40, -62), (-4, -72), (40, -68), (72, -60), (96, -86), (106, -82), (100, -50), (80, -26), (40, -14), (-20, -14), (-52, -22)])
    out.append(painted(D, bodyp, body, seed + 1, sdir=(0.6, 0.7), sk=0.16, angle=-10, n=34, inkw=2.2, inkop=0.75, hi=0.4))
    bd = smooth_closed(bodyp)
    grainl = []
    for k in range(7):
        y = -20 - k * 7
        grainl.append(pline(P([(-50, y), (0, y - 3 + rnd.uniform(-2, 2)), (60, y + 2), (100, y - 10 - k * 2)]), dk(body[1], 0.25), 1.1, seed + k, 0.35, 1))
    # worn paint showing wood along the top edge
    for _ in range(6):
        x, y = P([(rnd.uniform(-40, 80), rnd.uniform(-70, -60))])[0]
        grainl.append(f'<path d="{blob(x, y, rnd.uniform(3, 6) * s, rnd.uniform(1.5, 3) * s, rnd.randint(0, 999), 0.3, 8)}" fill="#D8AA70" opacity="0.8"/>')
    # painted cloud scrolls on the chest and flank
    for (x, y, r) in ((-38, -36, 8), (86, -52, 6)):
        c = P([(x, y)])[0]
        grainl.append(f'<path d="M {c[0] - r * s:.1f} {c[1]:.1f} a {r * s:.1f} {r * s:.1f} 0 1 1 {r * 1.6 * s:.1f} {r * 0.5 * s:.1f} a {r * 0.6 * s:.1f} {r * 0.6 * s:.1f} 0 1 0 {-r * 0.6 * s:.1f} {-r * 0.6 * s:.1f}" stroke="#F6C21C" stroke-width="{2.4 * s:.1f}" fill="none"/>')
    out.append(clipped(D, bd, grainl))
    # wing: rows of scalloped feathers outlined in white and yellow
    wingp = P([(-16, -58), (24, -66), (66, -56), (78, -38), (54, -28), (12, -26), (-12, -36)])
    out.append(painted(D, wingp, wing, seed + 2, sdir=(0.6, 0.7), sk=0.15, angle=-10, n=14, inkw=1.6, hi=0.35))
    wd = smooth_closed(wingp)
    feathers = []
    for row, (y0, x0, x1) in enumerate(((-56, -8, 60), (-46, 0, 66), (-36, 10, 70))):
        x = x0
        while x < x1:
            p = P([(x, y0), (x + 6, y0 + 9), (x + 12, y0)])
            feathers.append(pline(p, "#FFFFFF" if row % 2 == 0 else "#F6C21C", 1.8 * s, seed + int(x), 0.85, 1))
            x += 12
    out.append(clipped(D, wd, feathers))
    out.append(taper(P([(-12, -34), (30, -26), (74, -36)]), 4 * s, 2 * s, "#F6C21C", 0.9))
    # neck and head
    neckp = P([(-40, -54), (-50, -90), (-48, -118), (-30, -134), (-8, -128), (-6, -104), (-14, -80), (-6, -62)])
    out.append(painted(D, neckp, neck, seed + 6, sdir=(0.6, 0.7), sk=0.15, angle=-80, n=18, inkw=1.9, hi=0.4))
    out.append(taper(P([(-48, -86), (-30, -80), (-10, -86)]), 7 * s, 7 * s, "#FFFFFF", 0.95))
    out.append(taper(P([(-48, -92), (-30, -86), (-10, -92)]), 2.2 * s, 2.2 * s, "#C8301E", 0.9))
    headp = P([(-54, -118), (-48, -138), (-28, -146), (-8, -136), (-8, -116), (-26, -108), (-46, -108)])
    out.append(painted(D, headp, neck, seed + 7, sdir=(0.6, 0.7), sk=0.12, angle=0, n=10, inkw=1.9, hi=0.45))
    # painted face: white cheek sweep and a dark eye stripe
    out.append(taper(P([(-46, -122), (-30, -118), (-14, -124)]), 6 * s, 3 * s, "#FFFFFF", 0.9))
    out.append(taper(P([(-44, -134), (-28, -138), (-10, -132)]), 3 * s, 2 * s, "#14243A", 0.85))
    beak = P([(-52, -132), (-76, -128), (-80, -121), (-74, -117), (-52, -116)])
    out.append(painted(D, beak, ("#FFC070", "#F07A1E", "#9A3A0A"), seed + 8, sk=0.2, n=4, inkw=1.4, hi=0.45))
    out.append(pline(P([(-54, -124), (-76, -123)]), "#7A2A0A", 1.2, seed, 0.7, 1))
    ex, ey = P([(-36, -128)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5.4 * s:.1f}" fill="#FFFDF0"/><circle cx="{ex + sg * 0.6:.1f}" cy="{ey:.1f}" r="{3.4 * s:.1f}" fill="#120A04"/>'
               f'<circle cx="{ex + sg * 1.6 * s:.1f}" cy="{ey - 1.2 * s:.1f}" r="{1.1 * s:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


@design("saranghae")
def saranghae():
    D = Doc2("kr-sh")
    out = [hanji(D, "#F8E4DC", "#8A4A4A", 161, fibres=70, fib_col="#C89090")]
    out.append(blooms(162, ["#F2B8B0", "#F8D0C0", "#E8A0A0"], 7, (40, 40, 560, 560), (100, 190), (0.1, 0.18)))
    # a pale full moon behind the pair
    out.append(f'<circle cx="300" cy="400" r="176" fill="#FFF4EC" opacity="0.75"/>')
    out.append(f'<circle cx="300" cy="400" r="176" fill="none" stroke="#F0C0B4" stroke-width="2" opacity="0.7"/>')
    # patchwork bojagi laid under the ducks, seen at a slant
    cl = [(64, 488), (536, 480), (566, 556), (34, 566)]
    out.append(cast(D, 304, 548, 270, 30, strength=0.3, seed=163))
    d = pd(cl)
    out.append(f'<path d="{d}" fill="#F4F0E8"/>')
    cols = ["#C8301E", "#1E8A78", "#F2BE2A", "#1E4A9A", "#F4A0A8", "#F4F0E8", "#2E7A4A", "#E8702A"]
    patches = []
    rnd = random.Random(164)
    xs = [0, 0.18, 0.37, 0.52, 0.7, 0.86, 1.0]
    ys = [0, 0.45, 1.0]

    def Q(u, v):
        top = (cl[0][0] + (cl[1][0] - cl[0][0]) * u, cl[0][1] + (cl[1][1] - cl[0][1]) * u)
        bot = (cl[3][0] + (cl[2][0] - cl[3][0]) * u, cl[3][1] + (cl[2][1] - cl[3][1]) * u)
        return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)

    k = 0
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            u0, u1 = xs[i] + (0.04 if j else 0), xs[i + 1] + (0.04 if j else 0)
            poly = [Q(min(1, u0), ys[j]), Q(min(1, u1), ys[j]), Q(min(1, u1), ys[j + 1]), Q(min(1, u0), ys[j + 1])]
            patches.append(f'<path d="{pd(poly)}" fill="{cols[(k * 3 + j) % len(cols)]}"/>')
            k += 1
    for u in xs[1:-1]:
        for j in range(len(ys) - 1):
            uu = u + (0.04 if j else 0)
            a, b = Q(uu, ys[j]), Q(uu, ys[j + 1])
            patches.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#FFFDF6" stroke-width="2" stroke-dasharray="4 3"/>')
    a, b = Q(0, 0.45), Q(1, 0.45)
    patches.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#FFFDF6" stroke-width="2" stroke-dasharray="4 3"/>')
    patches.append(strokes(D.nid(), d, (20, 470, 580, 570), ["#FFFFFF", "#1A0A04"], 165, n=60, angle=-3, length=(20, 60), width=(1, 3), opacity=(0.08, 0.2)))
    patches.append(shade_over(D, d, "#1A0A04", 0.3, 0, 0, 0, 1, 0.3))
    out.append(clipped(D, d, patches))
    out.append(ink(d, INK, 1.8, 166, 2, 0.6))
    # the two ducks, facing each other, a red and blue thread tying them
    out.append(wedding_duck(D, 196, 512, 1.18, 167, flip=True))
    out.append(wedding_duck(D, 404, 512, 1.18, 168, flip=False, body=("#6AA2D8", "#1E5AA8", "#0C2A5E"), wing=("#EE7A62", "#C8301E", "#7A120A")))
    out.append(pline([(232, 412), (266, 430), (300, 404), (334, 430), (368, 412)], "#C8301E", 2.6, 169, 0.95, 1))
    out.append(pline([(232, 416), (266, 434), (300, 408), (334, 434), (368, 416)], "#1E5AA8", 2.2, 170, 0.85, 1))
    out.append(p_heart(D, 300, 324, 24, ("#FF8A8A", "#E0303A", "#8A0A14"), 171))
    for x, y, s in ((120, 300, 9), (482, 292, 8), (240, 296, 5), (366, 286, 6)):
        out.append(sparkle(x, y, s, "#E8606A", 0.8))
    # the painted word and its romanization
    out.append(hangul(D, 300, 62, 128, "사랑해", "#B8202A", 172, paper_c="#F8E4DC", shadow="#F2C0B4"))
    out.append(ruled(300, 246, "SARANGHAE · I LOVE YOU", "#1E3A6E", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 173, "#5A2A2A", 0.7)


# ================================================================ 7. tteokbokki — a street-stall pan glowing under a bare bulb
def rice_cake(D, x, y, Ls, w, ang, seed, sauce=True):
    """Cylindrical garae-tteok in 3/4 view, glazed in red sauce, its cut end showing white."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    p0, p1 = (x - ux * Ls / 2, y - uy * Ls / 2), (x + ux * Ls / 2, y + uy * Ls / 2)
    pts = capsule_pts(p0[0], p0[1], p1[0], p1[1], w, w * 0.98)
    pal = ("#FF9A6A", "#E04A26", "#8A1A0C") if sauce else ("#FFFFFF", "#F2EEE6", "#B8B0A4")
    out = [painted(D, pts, pal, seed, sdir=(0.3, 1), sk=0.2, angle=ang, n=5, inkw=0.9, inkc="#8A1A0A", inkop=0.4, hi=0.0)]
    # glossy highlight along the top
    nx, ny = -uy, ux
    if ny > 0:
        nx, ny = -nx, -ny
    out.append(taper([(p0[0] + nx * w * 0.22 + ux * 4, p0[1] + ny * w * 0.22 + uy * 4), (p1[0] + nx * w * 0.22 - ux * 6, p1[1] + ny * w * 0.22 - uy * 6)], w * 0.22, w * 0.1, "#FFE8D8", 0.85))
    # cut end: a pale oval at the near end
    e = p1 if (p1[1] > p0[1]) else p0
    if sauce:
        out.append(taper([(p0[0] - nx * w * 0.3 + ux * 6, p0[1] - ny * w * 0.3 + uy * 6), (p1[0] - nx * w * 0.3 - ux * 6, p1[1] - ny * w * 0.3 - uy * 6)], w * 0.25, w * 0.2, "#7A0E08", 0.35))
        return "".join(out)
    out.append(f'<path d="{blob(e[0], e[1], w * 0.36, w * 0.44, seed + 1, 0.08, 10, ang)}" fill="#FBEFE6" opacity="0.9"/>')
    out.append(f'<path d="{blob(e[0], e[1], w * 0.36, w * 0.44, seed + 1, 0.08, 10, ang)}" fill="none" stroke="#C8402A" stroke-width="1.6" opacity="0.8"/>')
    return "".join(out)


def fishcake_sheet(D, x, y, w, h, ang, seed):
    pts = rot([(x - w / 2, y - h / 2), (x + w / 2, y - h * 0.4), (x + w * 0.46, y + h / 2), (x - w * 0.5, y + h * 0.42)], x, y, ang)
    pts = jitter(densify(pts, 10), seed, 1.2)
    out = [painted(D, pts, ("#F8C890", "#D8904A", "#8A4A1A"), seed, sdir=(0.5, 0.8), sk=0.15, angle=ang, n=8, inkw=1.2, inkop=0.5, hi=0.35)]
    rnd = random.Random(seed)
    for _ in range(5):
        px, py = x + rnd.uniform(-w * 0.4, w * 0.4), y + rnd.uniform(-h * 0.3, h * 0.3)
        out.append(f'<path d="{blob(px, py, rnd.uniform(6, 12), rnd.uniform(4, 7), rnd.randint(0, 99), 0.3, 8)}" fill="#C8301E" opacity="0.75"/>')
    out.append(f'<path d="M {x - w * 0.42:.1f} {y:.1f} Q {x:.1f} {y - h * 0.12:.1f} {x + w * 0.4:.1f} {y + 2:.1f}" stroke="#A8601E" stroke-width="1.2" fill="none" opacity="0.6"/>')
    return "".join(out)


def boiled_egg(D, x, y, rx, ry, seed, sauce=0.6):
    pts = blob_pts(x, y, rx, ry, seed, 0.03, 18)
    out = [painted(D, pts, ("#FFFFFF", "#F6EEE2", "#C8B8A8"), seed, sdir=(0.5, 0.8), sk=0.2, angle=-30, n=6, inkw=1.2, inkc="#7A4A2A", inkop=0.5, hi=0.4)]
    d = smooth_closed(pts)
    out.append(clipped(D, d, [f'<path d="{blob(x + rx * 0.2, y + ry * 0.6, rx * 1.1, ry * 0.6, seed + 1, 0.2, 12)}" fill="#D8402A" opacity="{sauce}"/>']))
    out.append(f'<path d="{blob(x - rx * 0.35, y - ry * 0.35, rx * 0.25, ry * 0.15, seed + 2, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def bulb(D, cx, cy, s, seed, cord_top=-20):
    out = [soft_glow(D, cx, cy + 10 * s, 190 * s, "#FFC870", 0.55), soft_glow(D, cx, cy + 10 * s, 60 * s, "#FFF2C0", 0.8)]
    out.append(pline([(cx, cord_top), (cx + 2, cy - 30 * s)], "#1A1410", 2.2, seed, 1, 1))
    out.append(f'<path d="{hg.org_rect(cx - 8 * s, cy - 32 * s, 16 * s, 14 * s, seed, 0.3, 6, 2)}" fill="#3A3430"/>')
    out.append(f'<path d="{blob(cx, cy, 15 * s, 18 * s, seed, 0.03, 16)}" fill="#FFF6D0"/>')
    out.append(f'<path d="{blob(cx, cy, 15 * s, 18 * s, seed, 0.03, 16)}" fill="none" stroke="#E8B860" stroke-width="1.2"/>')
    out.append(pline([(cx - 4 * s, cy - 14 * s), (cx - 2 * s, cy + 2 * s), (cx + 2 * s, cy - 6 * s), (cx + 4 * s, cy + 2 * s)], "#FFB040", 1.4, seed, 0.9, 1))
    return "".join(out)


def eomuk_skewer(D, x0, y0, x1, y1, seed, folds=5):
    """Fish cake threaded on a long skewer in accordion folds (the broth-pot kind): alternating lit and shaded pleats."""
    out = [pline([(x0, y0), (x1, y1)], "#C8A070", 2.6, seed, 1, 1)]
    a = math.atan2(y1 - y0, x1 - x0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    Ls = math.hypot(x1 - x0, y1 - y0)
    half = 17
    n = folds * 2
    for i in range(n):
        t0, t1 = 0.06 + 0.56 * i / n, 0.06 + 0.56 * (i + 1) / n
        c0 = (x0 + ux * Ls * t0, y0 + uy * Ls * t0)
        c1 = (x0 + ux * Ls * t1, y0 + uy * Ls * t1)
        sk = 5 if i % 2 else -5
        q = [(c0[0] - nx * half, c0[1] - ny * half), (c0[0] + nx * half, c0[1] + ny * half),
             (c1[0] + nx * half + ux * sk, c1[1] + ny * half + uy * sk), (c1[0] - nx * half + ux * sk, c1[1] - ny * half + uy * sk)]
        col = "#F2C88A" if i % 2 else "#C8904A"
        out.append(f'<path d="{smooth_closed(q)}" fill="{col}" stroke="#8A5A2A" stroke-width="0.9" stroke-opacity="0.6"/>')
    out.append(pline([(x0 + ux * Ls * 0.62, y0 + uy * Ls * 0.62), (x1, y1)], "#D8B080", 2.4, seed, 1, 1))
    return "".join(out)


@design("tteokbokki")
def tteokbokki():
    D = Doc2("kr-tb")
    out = [sky(D, [(0, "#2A1416"), (0.6, "#3E1A16"), (1, "#22100E")], 181, 600, ["#4A2018", "#1A0A0A", "#5A2A1E"], 100, angle=-80, sop=(0.08, 0.18))]
    rnd = random.Random(182)
    for _ in range(18):
        x, y, r = rnd.uniform(0, 600), rnd.uniform(190, 320), rnd.uniform(10, 26)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{rnd.choice(["#FFB45A", "#FF7A4A", "#FFE08A", "#7AB8FF"])}" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>')
    out.append(bulb(D, 92, 230, 1.0, 183))
    # broth tray of fish-cake skewers behind, on the right
    tray = [(316, 296), (560, 292), (566, 344), (312, 348)]
    out.append(painted(D, tray, STEEL, 184, sdir=(0.3, 1), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{pd([(326, 300), (550, 296), (554, 318), (324, 322)])}" fill="#C89A5A"/>')
    for k in range(5):
        x = 352 + k * 44
        out.append(eomuk_skewer(D, x, 318, x - 46 + k * 6, 200 + (k % 2) * 16, 185 + k))
    out.append(steam(440, 288, 90, 186, "#FFFFFF", 3, 44, 8, 0.32))
    # the big pan
    out.append('<g transform="translate(300 420) scale(0.93) translate(-300 -420)">')
    rim = [(64, 330), (536, 330), (566, 506), (34, 506)]
    out.append(cast(D, 300, 526, 290, 28, strength=0.5, seed=187))
    out.append(f'<path d="{pd([(34, 506), (566, 506), (562, 530), (38, 530)])}" fill="#5A606A"/>')
    out.append(f'<path d="{pd([(34, 506), (566, 506), (564, 512), (36, 512)])}" fill="#C8CED6"/>')
    out.append(painted(D, densify(rim, 40), STEEL, 188, sdir=(0.3, 1), sk=0.05, angle=0, n=20, inkw=2, hi=0.5))
    sauce = [(86, 342), (514, 342), (540, 494), (60, 494)]
    sd = smooth_closed(densify(sauce, 30))
    out.append(f'<path d="{sd}" fill="{D.lin([(0, "#A8180E"), (0.5, "#D23A1E"), (1, "#A81A0E")])}"/>')
    items = [f'<path d="{blob(170, 384, 120, 36, 189, 0.2, 14)}" fill="#F0602A" opacity="0.4"/>',
             wave_lines(190, (60, 350, 540, 494), ["#FF9A6A", "#7A0A06"], 50, (20, 60), 2, 2, (0.3, 0.6))]
    for _ in range(20):
        x, y = rnd.uniform(90, 510), rnd.uniform(350, 490)
        items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(4, 9):.1f}" fill="#E04A26" stroke="#7A0A06" stroke-width="1"/>'
                     f'<path d="M {x - 3:.1f} {y - 2:.1f} q 2 -3 5 -2" stroke="#FFD0B0" stroke-width="1.2" fill="none"/>')
    out.append(clipped(D, sd, items))
    # chunky rice cakes, folded fish cakes and two eggs, back to front
    pieces = []
    spots = [(130, 372), (196, 362), (262, 370), (340, 364), (410, 370), (470, 380),
             (110, 414), (176, 404), (250, 420), (316, 408), (384, 418), (452, 414), (500, 440),
             (96, 458), (160, 452), (226, 470), (300, 458), (364, 470), (430, 462), (488, 478)]
    for (x, y) in spots:
        pieces.append((y + rnd.uniform(-4, 4), "tteok", x + rnd.uniform(-8, 8)))
    for (x, y) in ((228, 392), (418, 440), (140, 482)):
        pieces.append((y, "fish", x))
    for (x, y) in ((300, 396), (470, 412)):
        pieces.append((y, "egg", x))
    pieces.sort()
    k = 0
    for y, kind, x in pieces:
        k += 1
        sc = 0.82 + 0.36 * (y - 360) / 130
        if kind == "tteok":
            out.append(rice_cake(D, x, y, 58 * sc, 25 * sc, rnd.uniform(-28, 28), 200 + k))
        elif kind == "fish":
            out.append(fishcake_sheet(D, x, y, 76 * sc, 40 * sc, rnd.uniform(-15, 15), 200 + k))
        else:
            out.append(boiled_egg(D, x, y, 24 * sc, 30 * sc, 200 + k))
    # thick sauce pooling over and between the pieces, glossy
    for _ in range(26):
        x, y = rnd.uniform(90, 510), rnd.uniform(356, 490)
        out.append(f'<path d="{blob(x, y, rnd.uniform(10, 22), rnd.uniform(4, 8), rnd.randint(0, 999), 0.35, 10, rnd.uniform(-20, 20))}" fill="#B8200E" opacity="0.75"/>')
        out.append(f'<path d="{blob(x - 3, y - 2, rnd.uniform(4, 8), 1.6, rnd.randint(0, 999), 0.3, 8)}" fill="#FFB89A" opacity="0.6"/>')
    # scallion, sesame, gloss
    for _ in range(26):
        x, y = rnd.uniform(90, 510), rnd.uniform(352, 492)
        out.append(taper([(x, y), (x + rnd.uniform(-10, 10), y + rnd.uniform(-5, 5))], 5, 4, rnd.choice(["#4E9A2E", "#7AC04A", "#E8F0C0"]), 0.95))
    out.append(specks(217, (90, 352, 510, 492), ["#FFF4D8"], 40, (1, 1.8), (0.8, 1)))
    # a long spatula resting in the pan
    out.append(taper([(574, 352), (500, 404)], 10, 9, "#8A5A30"))
    out.append(taper([(572, 350), (502, 400)], 3, 2, "#C8925A", 0.8))
    out.append(painted(D, rot(rect_pts(430, 406, 512, 452, 14, 191, 0.4), 470, 428, -34), STEEL, 191, sdir=(0.3, 1), sk=0.1, angle=-34, n=6, inkw=1.4, hi=0.5))
    out.append(clipped(D, smooth_closed(rot(rect_pts(430, 406, 512, 452, 14, 191, 0.4), 470, 428, -34)),
                       [f'<path d="{blob(470, 440, 40, 12, 192, 0.3, 10, -34)}" fill="#C8281E" opacity="0.8"/>']))
    out.append('</g>')
    # lettering, like a stall sign
    out.append(letters(D, 300, 132, "TTEOKBOKKI", ANTON, 92, "#FFD25A", ["#FFE88A", "#F2A830", "#FFF2B0"], 215, ls=4, max_w=470,
                       shadow="#8A1408", soff=(0.03, 0.04), angle=-80, wob=0.5))
    out.append(ruled(300, 176, "THE TASTE OF AFTER SCHOOL", "#FFB49A", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 216)


# ================================================================ 8. pojangmacha — an orange tent glowing in the rain
def rain(seed, n, box, col="#C8D8F0", op=(0.25, 0.6), ang=100, Ls=(14, 34)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    a = math.radians(ang)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        Lr = rnd.uniform(*Ls)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * Lr:.1f} {math.sin(a) * Lr:.1f}" stroke="{col}" stroke-width="{rnd.uniform(0.9, 1.8):.1f}" stroke-linecap="round" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def clear_umbrella(D, cx, cy, r, seed):
    """Transparent vinyl umbrella dome, seen from the side, beaded with rain."""
    dome = ell_pts(cx, cy, r, r * 0.62, 180, 360, 20)
    hem = [(cx + r, cy)] + [(cx + r - 2 * r * i / 8, cy + (3 if i % 2 else -1)) for i in range(1, 8)] + [(cx - r, cy)]
    d = smooth_closed(dome + hem[1:-1][::-1][::-1])
    out = [f'<path d="{smooth_closed(dome + [(cx - r * 0.5, cy + 2), (cx, cy + 3), (cx + r * 0.5, cy + 2)][::-1])}" fill="#E8F4FF" opacity="0.35"/>']
    for k in range(-3, 4):
        out.append(pline([(cx, cy - r * 0.62), (cx + k * r * 0.3, cy - r * 0.2 * (1 - abs(k) / 4)), (cx + k * r / 3.1, cy)], "#F4FAFF", 1.2, seed + k, 0.6, 1))
    out.append(ink(smooth_open(dome), "#F4FAFF", 1.6, seed, 1, 0.8))
    out.append(pline([(cx, cy - r * 0.62), (cx, cy + r * 0.9)], "#E8E8F0", 2, seed, 0.9, 1))
    out.append(ink(f"M {cx:.1f} {cy + r * 0.9:.1f} q 0 6 -6 6", "#E8E8F0", 2, seed, 1, 0.9))
    rnd = random.Random(seed)
    for _ in range(14):
        a = rnd.uniform(math.pi, 2 * math.pi)
        rr = rnd.uniform(0.3, 0.95)
        out.append(f'<circle cx="{cx + math.cos(a) * r * rr:.1f}" cy="{cy + math.sin(a) * r * 0.62 * rr:.1f}" r="{rnd.uniform(1, 2):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("pojangmacha")
def pojangmacha():
    D = Doc2("kr-pj")
    out = [sky(D, [(0, "#0E1428"), (0.55, "#1E2240"), (1, "#2A2238")], 221, 600, ["#2A3058", "#0A0E1E"], 70, angle=-4, sop=(0.08, 0.2))]
    # city blocks behind, a few lit windows and blank shop signs
    rnd = random.Random(222)
    x = -10
    while x < 610:
        w, h = rnd.uniform(60, 110), rnd.uniform(120, 220)
        top = 410 - h
        c = rnd.choice(["#1A2038", "#222844", "#181C30", "#262A48"])
        out.append(f'<path d="{hg.org_rect(x, top, w, h + 40, rnd.randint(0, 999), 0.5, 10, 2)}" fill="{c}"/>')
        for j in range(int(h / 26)):
            for i in range(int(w / 22)):
                if rnd.random() < 0.3:
                    out.append(f'<rect x="{x + 8 + i * 22:.0f}" y="{top + 12 + j * 26:.0f}" width="10" height="13" fill="{rnd.choice(["#FFD27A", "#FFB45A", "#A8C8FF"])}" opacity="{rnd.uniform(0.4, 0.85):.2f}"/>')
        if rnd.random() < 0.5:
            out.append(f'<path d="{hg.org_rect(x + 6, top + h * 0.55, w - 12, 18, rnd.randint(0, 999), 0.4, 8, 2)}" fill="{rnd.choice(["#3A6AB8", "#B83A5A", "#2E8A7A"])}" opacity="0.7"/>')
        x += w + rnd.uniform(-4, 6)
    out.append(f'<rect y="200" width="600" height="250" fill="{D.lin([(0, "#2A2440", 0), (1, "#2A2440", 0.85)])}"/>')
    # wet street
    road = "M 0 446 L 600 446 L 600 600 L 0 600 Z"
    out.append(f'<path d="{road}" fill="{D.lin([(0, "#1E1C2C"), (1, "#0E0E18")])}"/>')
    out.append(f'<path d="M 0 446 L 600 446" stroke="#4A4668" stroke-width="3"/>')
    # mirrored glow of the tent in the wet asphalt: a soft vertical smear broken into ripples
    refl = [f'<path d="{pd([(124, 450), (476, 450), (490, 580), (110, 580)])}" fill="{D.lin([(0, "#FF9A3A", 0.4), (0.5, "#E8602A", 0.12), (1, "#E8602A", 0)])}"/>']
    for j in range(26):
        y = 456 + j * 5.5 + rnd.uniform(-1, 1)
        x0 = 120 + rnd.uniform(-10, 40)
        while x0 < 470:
            Ls = rnd.uniform(14, 50)
            refl.append(f'<path d="M {x0:.1f} {y:.1f} L {x0 + Ls:.1f} {y:.1f}" stroke="{rnd.choice(["#FFB45A", "#FF8A2A", "#FFD890"])}" stroke-width="{rnd.uniform(1.2, 2.6):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.25, 0.6) * (1 - j / 30):.2f}"/>')
            x0 += Ls + rnd.uniform(6, 26)
    out.append(clipped(D, road, refl))
    for k in range(10):
        x = rnd.uniform(0, 600)
        out.append(taper([(x, 452), (x, 452 + rnd.uniform(30, 70))], rnd.uniform(3, 6), 1, rnd.choice(["#FFD27A", "#A8C8FF"]), 0.22))
    # the tent: an arched orange tarp box with clear windows, its side panel going back
    out.append(soft_glow(D, 300, 360, 280, "#FF9A3A", 0.42))
    side = densify([(466, 300), (494, 270), (532, 282), (532, 432), (468, 446)], 12)
    out.append(painted(D, side, ("#E07A30", "#B04816", "#6A2408"), 223, sdir=(1, 0.2), sk=0.15, angle=-90, n=20, inkw=1.6, hi=0.15))
    arch = [(130 + 338 * t, 296 - 40 * math.sin(math.pi * t) ** 0.6) for t in [i / 16 for i in range(17)]]
    front = jitter(densify([(132, 446), (130, 360)] + arch + [(468, 360), (468, 446)], 16), 224, 0.6)
    fd = pd(front)
    out.append(painted(D, front, ("#FFB45A", "#F27A2A", "#A8400E"), 224, sdir=(0.2, 1), sk=0.08, angle=-90, n=40, inkw=1.9, hi=0.3))
    glow_in = [f'<path d="{fd}" fill="{D.rad([(0, "#FFE8A0", 0.75), (1, "#FFE8A0", 0)], 0.5, 0.6, 0.6)}"/>']
    # tarp seams and the faded band
    for x_ in (196, 404):
        glow_in.append(pline([(x_, 262), (x_ + 2, 446)], "#B8501A", 1.4, x_, 0.5, 1))
    glow_in.append(f'<path d="M 120 310 Q 300 290 480 310 L 480 322 Q 300 302 120 322 Z" fill="#C8401A" opacity="0.5"/>')
    out.append(clipped(D, fd, glow_in))
    # side windows: clear plastic, steamed, silhouettes of other customers
    for k, (x0, x1, fx, fdir) in enumerate(((150, 236, 194, 1), (364, 450, 404, -1))):
        wd = pd([(x0, 334), (x1, 334), (x1, 420), (x0, 420)])
        win = [f'<path d="{wd}" fill="#FFE2A0"/>', f'<path d="{wd}" fill="{D.lin([(0, "#FFF2C8"), (1, "#F2A850")])}"/>',
               figures.person(fx, 420, 70, "sit", fdir, "silhouette:#8A3A10", seed=225 + k),
               f'<path d="{wd}" fill="#FFFFFF" opacity="0.2"/>']
        for j in range(8):
            win.append(f'<path d="M {x0 + rnd.uniform(4, x1 - x0 - 4):.1f} {334 + rnd.uniform(0, 40):.1f} l {rnd.uniform(-1, 1):.1f} {rnd.uniform(12, 30):.1f}" stroke="#FFFFFF" stroke-width="1.4" opacity="0.6"/>')
        out.append(clipped(D, wd, win))
        out.append(ink(wd, "#7A2A0A", 1.8, 228 + k, 1, 0.7))
    # the open door: bright interior, a table with a green bottle, two friends
    door = [(250, 318), (350, 318), (352, 446), (248, 446)]
    dd = pd(door)
    inner = [f'<path d="{dd}" fill="#FFE2A0"/>', f'<path d="{dd}" fill="{D.lin([(0, "#FFF4C8"), (1, "#F2A850")])}"/>']
    inner.append(figures.person(268, 428, 84, "sit", 1, {"top": "#3A5A8A", "top_kind": "jacket", "bottom": "#2A2A3A", "hair_style": "short", "form": "m"}, seed=226, light=1))
    inner.append(figures.person(334, 428, 80, "sit", -1, {"top": "#C8506A", "top_kind": "long", "bottom": "#3A3A4A", "hair_style": "ponytail", "form": "f"}, seed=227, light=-1))
    inner.append(f'<path d="{pd([(276, 396), (326, 396), (324, 404), (278, 404)])}" fill="#E85A2A"/>')
    inner.append(f'<path d="{pd([(296, 404), (306, 404), (304, 446), (298, 446)])}" fill="#C8401A"/>')
    inner.append(f'<path d="{pd([(300, 396), (308, 396), (308, 374), (306, 366), (302, 366), (300, 374)])}" fill="#3E9A5A"/><path d="M 302 370 L 302 394" stroke="#B8F0C8" stroke-width="1.2" opacity="0.7"/>')
    inner.append(f'<ellipse cx="288" cy="394" rx="6" ry="2.4" fill="#FFFFFF" opacity="0.85"/><ellipse cx="316" cy="394" rx="6" ry="2.4" fill="#FFFFFF" opacity="0.85"/>')
    inner.append(steam(300, 380, 40, 229, "#FFFFFF", 2, 12, 3, 0.5))
    out.append(clipped(D, dd, inner))
    out.append(ink(dd, "#7A2A0A", 1.8, 230, 1, 0.7))
    # rolled-up clear flap over the door; a strip of light at the hem
    out.append(taper([(244, 316), (300, 320), (356, 316)], 11, 11, "#F8ECD8", 0.75))
    out.append(taper([(244, 312), (300, 316), (356, 312)], 3, 3, "#FFFFFF", 0.8))
    out.append(f'<path d="M 130 444 L 470 444" stroke="#FFD890" stroke-width="3" opacity="0.6"/>')
    # guy ropes
    for (x0, y0, x1, y1) in ((134, 304, 104, 446), (528, 288, 560, 440)):
        out.append(pline([(x0, y0), (x1, y1)], "#C8C0B0", 1.3, x0, 0.6, 1))
    # a passer-by under a clear umbrella, walking toward the tent
    out.append(figures.person(530, 478, 78, "walk", -1, {"top": "#2E3A5A", "top_kind": "coat", "bottom": "#1A1A24", "form": "f", "hair_style": "bob"}, seed=231, light=-1, rim="#FFB45A"))
    out.append(clear_umbrella(D, 532, 398, 46, 232))
    # puddle ripples
    for (x, y, r) in ((110, 520, 30), (250, 560, 40), (430, 532, 34), (520, 566, 26)):
        for kk in range(3):
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r * (1 - kk * 0.3):.1f}" ry="{r * 0.18 * (1 - kk * 0.3):.1f}" fill="none" stroke="#FFC890" stroke-width="1.2" opacity="{0.45 - kk * 0.1:.2f}"/>')
    out.append(rain(233, 320, (-40, -20, 620, 580)))
    # lettering
    out.append(letters(D, 300, 128, "pojangmacha", SERIF_IT, 100, "#FFB45A", ["#FFD27A", "#F2862A", "#FFE0A0"], 234, max_w=470,
                       shadow="#0A0A18", soff=(0.02, 0.035), angle=-40, hi="#FFF2C0"))
    out.append(ruled(300, 172, "ONE MORE ROUND IN THE RAIN", "#A8C8F0", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 235, "#0A0A18", 0.7)


# ================================================================ 9. hotteok — folded in a paper cup, the brown-sugar syrup running
def hotteok_disc(D, cx, cy, rx, ry, seed, bite=None):
    """A whole hotteok lying flat: griddle-crisp golden top, glossy, darker rim; optional bite showing syrup."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, rx, ry, seed, 0.04, 26)
    if bite:
        from summer_gouache import bite_out
        pts = bite_out(pts, *bite)
    out = [cast(D, cx + 10, cy + ry * 0.7, rx * 1.02, ry * 0.6, strength=0.4, seed=seed)]
    # thickness: a darker band under the top surface
    out.append(f'<path d="{smooth_closed([(x, y + ry * 0.22) for x, y in pts])}" fill="#A8601E"/>')
    out.append(painted(D, pts, ("#FAD890", "#E0A04A", "#9A5418"), seed, sdir=(0.5, 0.8), sk=0.15, angle=-20, n=30,
                       cols=["#FFE8B0", "#C8782A", "#F2C070"], inkw=1.6, inkop=0.6, hi=0.45))
    d = smooth_closed(pts)
    inner = []
    for _ in range(10):
        x, y = cx + rnd.uniform(-rx, rx) * 0.7, cy + rnd.uniform(-ry, ry) * 0.6
        inner.append(f'<path d="{blob(x, y, rnd.uniform(10, 22), rnd.uniform(5, 10), rnd.randint(0, 999), 0.35, 10)}" fill="#B8681E" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    inner.append(f'<path d="{blob(cx - rx * 0.3, cy - ry * 0.3, rx * 0.35, ry * 0.18, seed + 2, 0.2, 10, -10)}" fill="#FFF6E0" opacity="0.55"/>')
    inner.append(specks(seed + 3, bbox(pts), ["#6A3008", "#FFF0C8"], 30, (0.8, 2), (0.4, 0.8)))
    out.append(clipped(D, d, inner))
    if bite:
        bx, by, br = bite
        # the exposed inside along the bite edge: pale chewy dough around molten syrup with seeds, oozing out
        ex = bx - br * 0.9
        ins = blob_pts(ex, by + ry * 0.05, br * 0.34, ry * 0.5, seed + 4, 0.1, 12)
        out.append(f'<path d="{smooth_closed(ins)}" fill="#F6E0B0"/>')
        out.append(ink(smooth_closed(ins), "#B8864A", 1.2, seed + 4, 1, 0.6))
        syr = blob_pts(ex + br * 0.06, by + ry * 0.1, br * 0.24, ry * 0.32, seed + 5, 0.12, 12)
        out.append(painted(D, syr, ("#F0A040", "#A84A0E", "#5A1E04"), seed + 5, sk=0.2, n=4, inkw=0, hi=0.5))
        # syrup spilling over the lip onto the griddle
        out.append(taper([(ex + br * 0.12, by + ry * 0.1), (ex + br * 0.35, by + ry * 0.45), (ex + br * 0.4, by + ry * 1.1)], 12, 9, "#A84A0E", 0.95))
        out.append(f'<path d="{blob(ex + br * 0.45, by + ry * 1.25, br * 0.4, ry * 0.25, seed + 6, 0.2, 12)}" fill="#8A3A0A" opacity="0.9"/>')
        out.append(taper([(ex + br * 0.1, by + ry * 0.05), (ex + br * 0.3, by + ry * 0.4)], 3, 2, "#FFD08A", 0.85))
        for _ in range(6):
            x, y = ex + rnd.uniform(-br * 0.12, br * 0.2), by + rnd.uniform(-ry * 0.15, ry * 0.3)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="1.8" fill="{rnd.choice(["#F4E2B8", "#3A2A1A"])}"/>')
    return "".join(out)


@design("hotteok")
def hotteok():
    D = Doc2("kr-ht")
    out = [sky(D, [(0, "#3A3A6A"), (0.55, "#7A5A8A"), (1, "#E8A090")], 241, 600, ["#5A5A8A", "#C88A9A", "#FFC8A8"], 80, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(242)
    for _ in range(26):
        x, y, r = rnd.uniform(0, 600), rnd.uniform(160, 420), rnd.uniform(12, 34)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{rnd.choice(["#FFD27A", "#FFB45A", "#FF8A7A", "#FFF2C0"])}" opacity="{rnd.uniform(0.08, 0.22):.2f}"/>')
    # the stall's black griddle, close up
    gt = 330
    out.append(f'<path d="M 0 {gt} L 600 {gt} L 600 600 L 0 600 Z" fill="{D.lin([(0, "#3A3A44"), (1, "#121218")])}"/>')
    out.append(f'<path d="M 0 {gt} L 600 {gt}" stroke="#9A9AA8" stroke-width="4"/>')
    out.append(f'<path d="M 0 {gt + 4} L 600 {gt + 4}" stroke="#0A0A10" stroke-width="2" opacity="0.6"/>')
    out.append(strokes(D.nid(), f"M 0 {gt} L 600 {gt} L 600 600 L 0 600 Z", (-40, gt, 600, 600), ["#6A6A78", "#0A0A10"], 243, n=70, angle=-2, length=(60, 160), width=(1, 4), opacity=(0.15, 0.35)))
    for _ in range(26):
        x, y = rnd.uniform(20, 580), rnd.uniform(gt + 10, 590)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(4, 14):.1f}" ry="{rnd.uniform(1.5, 3):.1f}" fill="#E8D8A0" opacity="0.22"/>')
    out.append(soft_glow(D, 300, 420, 260, "#FFB45A", 0.18))
    # a paper cup waiting at the back
    cup = [(64, 296), (136, 296), (128, 380), (72, 380)]
    out.append(cast(D, 102, 382, 40, 6, strength=0.5, seed=249))
    out.append(painted(D, cup, ("#E8C898", "#C89A60", "#7A5A30"), 250, sdir=(0.8, 0.3), sk=0.18, angle=-88, n=12, inkw=1.6, hi=0.4))
    out.append(f'<path d="{ellipse_d(100, 296, 36, 7)}" fill="#8A6236"/>')
    for k in range(3):
        out.append(pline([(68, 316 + k * 20), (132, 315 + k * 20)], "#A87A44", 1.1, 251 + k, 0.45, 1))
    # one cake frying at the back right, one being flattened under the press
    out.append(hotteok_disc(D, 446, 392, 104, 32, 244))
    px, py = 236, 404
    out.append(hotteok_disc(D, px, py + 8, 118, 34, 245))
    out.append(f'<path d="{ellipse_d(px, py, 90, 25)}" fill="#3A3E4A"/>')
    out.append(painted(D, ell_pts(px, py - 6, 90, 25, 0, 360, 28)[:-1], STEEL, 246, sdir=(0.3, 1), sk=0.15, angle=0, n=14, inkw=1.6, inkc="#3A3E4A", hi=0.5))
    out.append(f'<path d="{ellipse_d(px, py - 8, 24, 7)}" fill="#8A909C"/>')
    out.append(taper([(px, py - 10), (px + 40, py - 44)], 12, 11, "#7A808C"))
    out.append(taper([(px + 38, py - 42), (px + 132, py - 138)], 20, 18, "#8A5A30"))
    out.append(taper([(px + 35, py - 46), (px + 128, py - 142)], 6, 5, "#C8925A", 0.8))
    out.append(taper([(px + 43, py - 37), (px + 136, py - 132)], 4, 3, "#4A2A12", 0.6))
    for k in range(14):
        a_ = rnd.uniform(0, 6.28)
        out.append(f'<circle cx="{px + math.cos(a_) * 108:.1f}" cy="{py + 8 + math.sin(a_) * 30:.1f}" r="{rnd.uniform(1.5, 3):.1f}" fill="none" stroke="#FFE8B0" stroke-width="1" opacity="0.7"/>')
    # a finished hotteok in front, bitten: the brown-sugar syrup runs out
    out.append(hotteok_disc(D, 300, 500, 158, 54, 247, bite=(452, 486, 58)))
    out.append(steam(236, 332, 110, 257, "#FFFFFF", 3, 34, 8, 0.45))
    out.append(steam(446, 352, 90, 258, "#FFFFFF", 2, 30, 7, 0.4))
    out.append(steam(330, 450, 60, 262, "#FFFFFF", 2, 26, 6, 0.4))
    out.append(snowflakes(259, 60, (0, 0, 600, 330), avoid=((70, 60, 530, 200),)))
    # lettering
    out.append(letters(D, 300, 132, "hotteok", SERIF_IT, 128, "#FFF2DA", ["#FFFFFF", "#FFE0C0", "#F8D0B0"], 260, max_w=400,
                       shadow="#2A2448", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 178, "CAREFUL, THE SYRUP IS HOT", "#FFD8A0", font=JOS, size=19, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 261, "#2A2448", 0.7)


# ================================================================ 10. bungeoppang — fish-shaped bread in a kraft paper bag
def fish_bread(D, cx, cy, s, ang, seed, bite=False):
    """Bungeoppang: golden fish-shaped waffle with moulded scales, fins, a crisp skirt; facing left.
    bite=True: the head is bitten off, showing sweet red-bean paste."""
    rnd = random.Random(seed)

    def P(pts):
        return rot(L(pts, cx, cy, s), cx, cy, ang)

    body = P([(-78, 0), (-66, -22), (-40, -34), (0, -36), (36, -30), (58, -16), (70, -26), (92, -38), (96, -6), (98, 10), (92, 36), (70, 24), (58, 16), (36, 30), (0, 36), (-40, 32), (-66, 22)])
    if bite:
        body = [p for p in body]
        bx, by = P([(-74, 0)])[0]
        from summer_gouache import bite_out
        body = bite_out(body, bx, by, 36 * s)
    pal = ("#F8C870", "#D88A2A", "#8A4A10")
    # crisp batter skirt
    skirt = [(x + rnd.uniform(-3, 3) * s, y + rnd.uniform(-3, 3) * s) for x, y in body]
    out = [cast(D, cx + 8, cy + 40 * s, 92 * s, 10 * s, strength=0.4, seed=seed)]
    out.append(f'<path d="{smooth_closed([(cx + (x - cx) * 1.06, cy + (y - cy) * 1.1) for x, y in skirt])}" fill="#E8B060" opacity="0.8"/>')
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=26, cols=["#FFE0A0", "#B8661E", "#F2B050"], inkw=1.8, inkop=0.6, hi=0.45))
    d = smooth_closed(body)
    inner = []
    # moulded scales, dorsal fin ridges, gill arc, tail rays
    for row in range(3):
        for i in range(6):
            x, y = -26 + i * 14 + (row % 2) * 7, -16 + row * 14
            p = P([(x, y - 6), (x + 6, y), (x, y + 6)])
            inner.append(pline(p, "#9A5414", 1.6 * s, seed + row * 7 + i, 0.7, 1))
            inner.append(pline([(p[0][0] - 1, p[0][1] - 1), (p[1][0] - 1, p[1][1] - 1)], "#FFE8B0", 1 * s, seed + i, 0.6, 1))
    inner.append(pline(P([(-46, -24), (-38, 0), (-46, 24)]), "#8A4A10", 2 * s, seed, 0.75, 1))
    for k in range(5):
        inner.append(pline(P([(66, -16 + k * 8), (92, -30 + k * 16)]), "#8A4A10", 1.4 * s, seed + k, 0.6, 1))
    for k in range(5):
        inner.append(pline(P([(-20 + k * 12, -34), (-14 + k * 12, -26)]), "#8A4A10", 1.4 * s, seed + k, 0.6, 1))
    inner.append(shade_over(D, d, "#5A2A06", 0.3, 0, 0, 1, 1, 0.5))
    for _ in range(14):
        x, y = P([(rnd.uniform(-60, 80), rnd.uniform(-26, 26))])[0]
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.6) * s:.1f}" fill="#A85A14" opacity="0.5"/>')
    out.append(clipped(D, d, inner))
    if not bite:
        ex, ey = P([(-56, -8)])[0]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{6 * s:.1f}" fill="#B8701E"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3 * s:.1f}" fill="#6A3408"/>'
                   f'<circle cx="{ex - 1.5 * s:.1f}" cy="{ey - 1.5 * s:.1f}" r="{1.2 * s:.1f}" fill="#FFE8B0"/>')
        out.append(pline(P([(-74, 6), (-66, 9)]), "#8A4A10", 1.6 * s, seed, 0.8, 1))
    else:
        bx, by = P([(-50, 0)])[0]
        out.append(f'<path d="{blob(bx, by, 16 * s, 22 * s, seed + 9, 0.15, 12, ang)}" fill="#5A1E14"/>')
        out.append(specks(seed + 10, (bx - 12 * s, by - 18 * s, bx + 12 * s, by + 18 * s), ["#7A2E20", "#3A0E08", "#9A4A3A"], 26, (1.2, 2.6), (0.7, 1)))
        out.append(f'<path d="{blob(bx - 4 * s, by - 8 * s, 5 * s, 3 * s, seed + 11, 0.2, 8)}" fill="#C88070" opacity="0.6"/>')
    return "".join(out)


def kraft_bag(D, x0, top, x1, bottom, seed):
    pts = [(x0, top + 6), (x0 + (x1 - x0) * 0.25, top - 4), (x0 + (x1 - x0) * 0.5, top + 4), (x0 + (x1 - x0) * 0.75, top - 6), (x1, top + 4), (x1 - 6, bottom), (x0 + 6, bottom)]
    out = [cast(D, (x0 + x1) / 2 + 10, bottom + 2, (x1 - x0) * 0.6, 10, strength=0.45, seed=seed)]
    out.append(painted(D, densify(pts, 30), ("#E8C48A", "#C8955A", "#7A5228"), seed, sdir=(0.8, 0.4), sk=0.15, angle=-88, n=40, inkw=1.8, hi=0.35))
    d = smooth_closed(densify(pts, 30))
    rnd = random.Random(seed)
    inner = []
    for _ in range(5):
        x, y = rnd.uniform(x0 + 20, x1 - 20), rnd.uniform(top + 40, bottom - 30)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(14, 26), rnd.uniform(10, 18), rnd.randint(0, 999), 0.3, 12)}" fill="#A8743A" opacity="0.3"/>')
    for k in range(3):
        y = top + 30 + k * 14
        inner.append(pline([(x0, y), ((x0 + x1) / 2, y + rnd.uniform(-3, 3)), (x1, y + 2)], "#8A6236", 1.2, seed + k, 0.4, 1))
    inner.append(pline([(x0 + 20, bottom - 8), (x1 - 20, bottom - 10)], "#8A6236", 1.4, seed, 0.5, 1))
    out.append(clipped(D, d, inner))
    return "".join(out)


def mitten(D, cx, cy, s, ang, seed, pal=("#F28A8A", "#C8303A", "#7A1018")):
    def P(pts):
        return rot(L(pts, cx, cy, s), cx, cy, ang)
    body = P([(-30, 50), (-34, 0), (-30, -40), (-10, -58), (14, -54), (28, -30), (30, 50)])
    thumb = P([(-30, 0), (-52, -12), (-58, -30), (-46, -38), (-30, -20)])
    out = [painted(D, thumb, pal, seed, sk=0.2, n=6, inkw=1.4, hi=0.4)]
    out.append(painted(D, body, pal, seed + 1, sdir=(0.6, 0.7), sk=0.18, angle=-90, n=20, inkw=1.6, hi=0.4))
    d = smooth_closed(body)
    knit = []
    for j in range(10):
        for i in range(6):
            x, y = P([(-26 + i * 10, -44 + j * 9)])[0]
            knit.append(f'<path d="M {x - 3 * s:.1f} {y - 3 * s:.1f} L {x:.1f} {y + 2 * s:.1f} L {x + 3 * s:.1f} {y - 3 * s:.1f}" stroke="{pal[2]}" stroke-width="1.2" fill="none" opacity="0.5"/>')
    for i in range(6):
        x, y = P([(-24 + i * 9, 6)])[0]
        knit.append(f'<path d="{blob(x, y, 3.4 * s, 3 * s, seed + i, 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(clipped(D, d, knit))
    cuff = P([(-32, 34), (32, 34), (32, 58), (-32, 58)])
    out.append(painted(D, cuff, ("#FFFFFF", "#F2EEE8", "#B8B0A8"), seed + 2, sk=0.15, angle=-90, n=8, inkw=1.4, hi=0.3))
    for i in range(7):
        a, b = P([(-28 + i * 9, 36)])[0], P([(-28 + i * 9, 56)])[0]
        out.append(pline([a, b], "#C8C0B8", 1.2, seed + i, 0.7, 1))
    return "".join(out)


@design("bungeoppang")
def bungeoppang():
    D = Doc2("kr-bu")
    out = [hanji(D, "#DCE8EE", "#5A7A8A", 261, fibres=50, fib_col="#8AA8B8")]
    out.append(blooms(262, ["#B8D0DC", "#C8DCE4", "#A8C4D4"], 7, (20, 20, 580, 580), (100, 190), (0.12, 0.2)))
    # snowy windowsill / counter in front
    out.append(f'<path d="{smooth_open([(-10, 470), (300, 462), (610, 470)])} L 610 610 L -10 610 Z" fill="#F4F8FA"/>')
    out.append(f'<path d="{smooth_open([(-10, 470), (300, 462), (610, 470)])} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#FFFFFF", 0), (1, "#9AB0C8", 0.45)])}"/>')
    out.append(ink(smooth_open([(-10, 470), (300, 462), (610, 470)]), "#8AA0B8", 1.6, 263, 1, 0.5))
    # breads standing in the bag, heads up
    for k, (x, y, a) in enumerate(((226, 306, -62), (300, 290, -90), (376, 306, -118))):
        out.append(fish_bread(D, x, y, 1.02, a, 264 + k))
    out.append(kraft_bag(D, 190, 352, 410, 500, 267))
    # rolled-down top edge of the bag
    out.append(painted(D, [(184, 350), (240, 340), (300, 346), (360, 338), (416, 350), (414, 374), (300, 368), (186, 376)], ("#F2D8A8", "#D8A870", "#8A6236"), 268, sk=0.2, angle=0, n=12, inkw=1.6, hi=0.4))
    for x in (230, 290, 352):
        out.append(pline([(x, 344), (x + 6, 370)], "#8A6236", 1.2, x, 0.5, 1))
    # one bread on the sill with its head already gone, and a red mitten
    out.append(fish_bread(D, 470, 512, 0.96, 8, 269, bite=True))
    out.append(mitten(D, 112, 486, 0.9, -24, 270))
    out.append(steam(300, 236, 70, 271, "#FFFFFF", 3, 30, 7, 0.55))
    out.append(snowflakes(272, 90, (0, 0, 600, 460), avoid=((60, 60, 540, 210),)))
    # lettering
    out.append(letters(D, 300, 124, "bungeoppang", DMS, 96, "#2A4A6A", ["#3A5E84", "#1A3450"], 273, max_w=470,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.6))
    out.append(ruled(300, 168, "HEAD OR TAIL FIRST?", "#C8402A", font=JOS, size=20, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 274, "#2A3A4A", 0.6)


# ================================================================ 11. uri jip — a hanok and its courtyard at dusk
def hanok_roof(D, x0, x1, eave_y, ridge_y, seed, lift=26, pal=("#7A7E8A", "#4A4E5A", "#22252E"), haze=0.0):
    """Curved hanok roof seen from the front: eaves sweeping up at the corners, tile ridges, a crested ridge line."""
    hz = (lambda c: mix(c, "#C8B8C8", haze)) if haze else (lambda c: c)
    rnd = random.Random(seed)
    W = x1 - x0
    eave = [(x0 + W * t, eave_y - lift * (abs(2 * t - 1) ** 3) + 6 * math.sin(math.pi * t)) for t in [i / 30 for i in range(31)]]
    ridge_l, ridge_r = x0 + W * 0.18, x1 - W * 0.18
    top = [(ridge_r, ridge_y), (ridge_l, ridge_y)]
    pts = eave + [(x1 - W * 0.06, eave_y - lift * 1.3), (ridge_r + W * 0.02, ridge_y + 4)] + top + [(ridge_l - W * 0.02, ridge_y + 4), (x0 + W * 0.06, eave_y - lift * 1.3)]
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{hz(pal[1])}"/>']
    inner = [f'<path d="{d}" fill="{D.lin([(0, hz(pal[0]), 0.5), (1, hz(pal[2]), 0.6)])}"/>']
    # vertical tile ridges, fanning slightly toward the corners
    n = 34
    for i in range(n + 1):
        t = i / n
        bx, by = x0 + W * t, eave_y - lift * (abs(2 * t - 1) ** 3) + 6 * math.sin(math.pi * t)
        tx = ridge_l + (ridge_r - ridge_l) * t
        tx = tx + (bx - tx) * 0.15
        inner.append(taper([(tx, ridge_y + 6), ((tx + bx) / 2, (ridge_y + by) / 2 - 3), (bx, by - 2)], 3.2, 5, hz(pal[0]), 0.7))
        inner.append(taper([(tx + 3, ridge_y + 6), ((tx + bx) / 2 + 3, (ridge_y + by) / 2 - 2), (bx + 3, by - 1)], 1.6, 2.6, hz(pal[2]), 0.6))
    out.append(clipped(D, d, inner))
    # round tile ends along the eave
    for i in range(n + 1):
        t = i / n
        bx, by = x0 + W * t, eave_y - lift * (abs(2 * t - 1) ** 3) + 6 * math.sin(math.pi * t)
        out.append(f'<circle cx="{bx + 1.5:.1f}" cy="{by:.1f}" r="3.4" fill="{hz(pal[2])}"/><circle cx="{bx + 1:.1f}" cy="{by - 0.6:.1f}" r="1.6" fill="{hz(pal[0])}" opacity="0.7"/>')
    # ridge (yongmaru) with upturned ends
    rp = [(ridge_l - W * 0.04, ridge_y - 14), (ridge_l, ridge_y - 6), (ridge_r, ridge_y - 6), (ridge_r + W * 0.04, ridge_y - 14),
          (ridge_r + W * 0.035, ridge_y + 4), (ridge_l - W * 0.035, ridge_y + 4)]
    out.append(painted(D, rp, tuple(hz(c) for c in pal), seed + 1, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.35))
    out.append(pline([(ridge_l, ridge_y - 2), (ridge_r, ridge_y - 2)], hz("#FFFFFF"), 1.6, seed, 0.5, 1))
    out.append(ink(smooth_open(eave), hz(INK), 1.6, seed, 1, 0.6))
    return "".join(out), eave


@design("uri-jip")
def uri_jip():
    D = Doc2("kr-uj")
    out = [sky(D, [(0, "#3E4A7A"), (0.5, "#C88A9A"), (1, "#F6C890")], 281, 600, ["#5A6A9A", "#E8A8A8", "#FFD8A8"], 80, angle=-4, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 250, 200, "#FFE0B0", 0.5))
    # back hills and a pine
    hl = ridge([(-20, 300), (120, 262), (260, 284), (420, 250), (620, 286)], 282, 8, 4)
    out.append(hill(D, hl, 420, ("#8A86A8", "#5E5E86", "#3A3A5E"), 283, inkw=1.0, inkop=0.3))
    # stone courtyard wall on the right edge
    # the house: stone base, pillars, paper doors glowing, maru floor
    base_y = 450
    out.append(f'<path d="{pd([(60, base_y - 6), (540, base_y - 6), (552, base_y + 22), (48, base_y + 22)])}" fill="#A8A49C"/>')
    out.append(stone_wall(D, 48, 552, base_y - 6, base_y + 22, 284))
    # back wall with doors
    wall = [(92, 330), (508, 330), (508, base_y - 40), (92, base_y - 40)]
    out.append(f'<path d="{pd(wall)}" fill="#E8DCC8"/>')
    for k in range(4):
        x0 = 112 + k * 98
        door = pd([(x0, 340), (x0 + 82, 340), (x0 + 82, base_y - 46), (x0, base_y - 46)])
        out.append(f'<path d="{door}" fill="{D.lin([(0, "#FFF2C8"), (1, "#FFD890")])}"/>')
        out.append(soft_glow(D, x0 + 41, 380, 60, "#FFE6A0", 0.5))
        lat = []
        for i in range(1, 5):
            lat.append(f'<path d="M {x0 + i * 82 / 5:.1f} 340 L {x0 + i * 82 / 5:.1f} {base_y - 46}" stroke="#7A4E2A" stroke-width="1.6"/>')
        for j in range(1, 6):
            lat.append(f'<path d="M {x0} {340 + j * (base_y - 386) / 6:.1f} L {x0 + 82} {340 + j * (base_y - 386) / 6:.1f}" stroke="#7A4E2A" stroke-width="1.6"/>')
        out.append("".join(lat))
        out.append(ink(door, "#5A3418", 2.4, 285 + k, 1, 0.9))
    # pillars
    for k in range(5):
        x = 96 + k * 102
        out.append(painted(D, rect_pts(x - 9, 312, x + 9, base_y - 8, 20, 286 + k, 0.4), ("#C8925A", "#8A5A30", "#4A2A12"), 286 + k, sdir=(1, 0), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.3))
        out.append(f'<path d="{blob(x, base_y - 6, 14, 5, 290 + k, 0.1, 10)}" fill="#8A8680"/>')
    # wooden maru floor
    maru = [(70, base_y - 42), (530, base_y - 42), (540, base_y - 26), (60, base_y - 26)]
    out.append(painted(D, maru, ("#E8B878", "#B8824A", "#6A4220"), 295, sdir=(0.3, 1), sk=0.1, angle=0, n=30, inkw=1.4, hi=0.4))
    for k in range(1, 12):
        x = 70 + k * 42
        out.append(pline([(x, base_y - 42), (x - 2, base_y - 26)], "#6A4220", 1.2, 296 + k, 0.5, 1))
    out.append(f'<path d="M 60 {base_y - 26} L 540 {base_y - 26} L 538 {base_y - 18} L 62 {base_y - 18} Z" fill="#5A3418"/>')
    # eave shadow and rafter ends under the roof
    out.append(f'<path d="{pd([(60, 300), (540, 300), (540, 336), (60, 336)])}" fill="#3A2418" opacity="0.55"/>')
    for k in range(26):
        x = 62 + k * 19
        out.append(f'<circle cx="{x:.1f}" cy="314" r="5" fill="#8A5A30"/><circle cx="{x:.1f}" cy="314" r="2.6" fill="#C8925A"/>')
    roof, eave = hanok_roof(D, 22, 578, 304, 206, 297, lift=40)
    out.append(roof)
    # a sleeping cat on the maru
    cat = blob_pts(452, base_y - 50, 30, 12, 301, 0.08, 16)
    out.append(painted(D, cat, ("#F2C890", "#D89A5A", "#8A5A2A"), 301, sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(428, base_y - 56, 12, 10, 302, 0.08, 12), ("#F2C890", "#D89A5A", "#8A5A2A"), 302, sk=0.2, n=4, inkw=1.4, hi=0.4))
    out.append(f'<path d="M 420 {base_y - 64} l 3 -8 l 4 7 Z M 430 {base_y - 66} l 4 -7 l 3 8 Z" fill="#D89A5A" stroke="{INK}" stroke-width="1"/>')
    out.append(pline([(424, base_y - 56), (428, base_y - 54)], INK, 1.2, 303, 0.8, 1))
    out.append(taper([(480, base_y - 46), (500, base_y - 44), (508, base_y - 52)], 6, 3, "#D89A5A"))
    # courtyard ground (packed earth), a flowering shrub, garden lantern glow
    out.append(f'<path d="M -10 {base_y + 22} L 610 {base_y + 22} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#D8B888"), (1, "#B08A5A")])}"/>')
    out.append(strokes(D.nid(), f"M -10 {base_y + 22} L 610 {base_y + 22} L 610 610 L -10 610 Z", (-60, base_y + 22, 600, 600), ["#E8CCA0", "#9A7448"], 304, n=50, angle=-2, length=(40, 120), width=(2, 5), opacity=(0.15, 0.35)))
    # the long stepping stone (taetdol) with a pair of white rubber shoes left neatly side by side
    stp = rect_pts(214, base_y + 26, 386, base_y + 50, 16, 305, 0.8)
    out.append(cast(D, 304, base_y + 52, 96, 8, strength=0.45, seed=305))
    out.append(painted(D, stp, ("#D8D4CC", "#9E9A92", "#5E5A54"), 305, sdir=(0.3, 1), sk=0.25, angle=0, n=14, inkw=1.6, hi=0.45))
    out.append(gomusin(D, 284, base_y + 36, 40, 306, flip=1))
    out.append(gomusin(D, 324, base_y + 38, 40, 307, flip=1))
    for k, (x, y) in enumerate(((84, 520), (528, 512))):
        out.append(dab_crown(D, x, y, 60, 40, [("#F6A8C8", "#E05A8A", "#8A1E4A"), ("#7AB06A", "#3E7A3A", "#1A4A1A")], 308 + k, n=80, size=(4, 8), inkw=1.0))
    out.append(soft_glow(D, 300, 390, 200, "#FFD890", 0.25))
    # lettering
    out.append(letters(D, 300, 126, "uri jip", SERIF_IT, 124, "#FFF2DC", ["#FFFFFF", "#FFE0C0", "#F8D0B8"], 310, max_w=380,
                       shadow="#2A2A5A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "OUR HOME", "#FFE0A8", font=JOS, size=20, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 311, "#2A2A4A", 0.6)


# ================================================================ 12. gyeongbokgung — the palace gate in autumn, ginkgo gold
def ginkgo_tree(D, x, base, h, seed, haze=0.0):
    hz = (lambda c: mix(c, "#E8D8B8", haze)) if haze else (lambda c: c)
    out = [taper([(x, base), (x + 2, base - h * 0.5), (x - 2, base - h * 0.8)], h * 0.07, h * 0.03, hz("#5A3A22"))]
    pals = [(hz("#FFF2A0"), hz("#F6C82A"), hz("#C08A0A")), (hz("#FFE88A"), hz("#E8B020"), hz("#A8700A"))]
    out.append(dab_crown(D, x, base - h * 0.62, h * 0.26, h * 0.4, pals, seed, n=int(h * 1.2), size=(4, 8), inkw=1.0))
    return "".join(out)


def ginkgo_leaf(D, x, y, s, ang, seed, pal=("#FFF2A0", "#F6C82A", "#B88A0A")):
    a = math.radians(ang)
    pts = [(x, y)]
    for i in range(13):
        t = math.radians(-60 + 120 * i / 12)
        r = s * (1 - 0.18 * (i == 6))
        pts.append((x + math.sin(t) * r, y - math.cos(t) * r * 0.9))
    pts = rot(pts, x, y, ang)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=ang - 90, n=6, inkw=1, inkop=0.5, hi=0.4)]
    for i in range(5):
        t = math.radians(-50 + 25 * i)
        e = rot([(x + math.sin(t) * s * 0.85, y - math.cos(t) * s * 0.8)], x, y, ang)[0]
        out.append(pline([(x, y), e], pal[2], 0.8, seed + i, 0.4, 1))
    st = rot([(x, y), (x + 1, y + s * 0.6)], x, y, ang)
    out.append(pline(st, "#8A6A1A", 1.6, seed, 0.9, 1))
    return "".join(out)


def dancheong_band(D, x0, x1, y, h, seed):
    """Painted bracket band under palace eaves: teal ground with repeating red, white and blue lotus motifs."""
    out = [f'<path d="{pd([(x0, y), (x1, y), (x1, y + h), (x0, y + h)])}" fill="#1E8A78"/>']
    step = h * 1.6
    x = x0 + step / 2
    k = 0
    while x < x1:
        out.append(f'<circle cx="{x:.1f}" cy="{y + h / 2:.1f}" r="{h * 0.34:.1f}" fill="{["#D2382A", "#2E5AA8"][k % 2]}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y + h / 2:.1f}" r="{h * 0.18:.1f}" fill="#FFFFFF"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y + h / 2:.1f}" r="{h * 0.08:.1f}" fill="#F2BE2A"/>')
        out.append(f'<path d="M {x + step * 0.3:.1f} {y + 1:.1f} l {step * 0.2:.1f} {h / 2 - 1:.1f} l {-step * 0.2:.1f} {h / 2 - 1:.1f}" stroke="#F4F0E8" stroke-width="1.4" fill="none"/>')
        x += step
        k += 1
    out.append(f'<path d="M {x0} {y} L {x1} {y} M {x0} {y + h} L {x1} {y + h}" stroke="#123A30" stroke-width="1.4"/>')
    return "".join(out)


def palace_roof(D, cx, eave_y, w, h, seed, lift=22):
    """Hipped palace roof in front view (darker grey tiles), with dancheong band and bracket shadows under it."""
    roof, eave = hanok_roof(D, cx - w / 2, cx + w / 2, eave_y, eave_y - h, seed, lift=lift, pal=("#8A8E98", "#545862", "#26282E"))
    return roof


@design("gyeongbokgung")
def gyeongbokgung():
    D = Doc2("kr-gb")
    out = [sky(D, [(0, "#3E7AC8"), (0.55, "#9AC4EA"), (1, "#F2E2C0")], 321, 600, ["#5A90D0", "#FFFFFF", "#B8D8F0"], 70, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 110, 236, 110, 322, pal=("#FFFFFF", "#F4F8FF", "#B8C8E0")))
    out.append(puff_cloud(D, 500, 222, 90, 323, pal=("#FFFFFF", "#F4F8FF", "#B8C8E0")))
    # Bugaksan behind, autumn coloured
    mt = ridge([(-20, 300), (90, 250), (200, 214), (300, 196), (380, 220), (480, 246), (620, 270)], 324, 10, 4)
    out.append(hill(D, mt, 420, ("#C8A888", "#8A7A6A", "#5A4E46"), 325, inkw=1.2, inkop=0.35))
    out.append(dab_crown(D, 160, 300, 120, 30, [("#E8A06A", "#C8602A", "#7A2A10"), ("#E8C870", "#B8902A", "#6A5010"), ("#8AA86A", "#4E6A3A", "#2A3E1E")], 326, n=150, size=(5, 9), inkw=0))
    out.append(dab_crown(D, 460, 310, 130, 30, [("#E8A06A", "#C8602A", "#7A2A10"), ("#E8C870", "#B8902A", "#6A5010"), ("#8AA86A", "#4E6A3A", "#2A3E1E")], 327, n=150, size=(5, 9), inkw=0))
    # flanking walls with tiled caps
    out.append('<g transform="translate(0 14)">')
    for (x0, x1) in ((-10, 140), (460, 610)):
        out.append(f'<path d="{pd([(x0, 360), (x1, 360), (x1, 430), (x0, 430)])}" fill="#D84A30"/>')
        out.append(f'<path d="{pd([(x0, 360), (x1, 360), (x1, 430), (x0, 430)])}" fill="{D.lin([(0, "#FFFFFF", 0.1), (1, "#000000", 0.2)])}"/>')
        out.append(giwa_row(D, x0, x1, 348, 14, 328 + x0))
    # stone gate platform with three arches
    plat = [(120, 330), (480, 330), (490, 440), (110, 440)]
    out.append(painted(D, plat, ("#E8E2D4", "#C8C0B0", "#8A8070"), 330, sdir=(0.5, 1), sk=0.08, angle=0, n=30, inkw=1.6, hi=0.4))
    pdp = pd(plat)
    blocks = []
    for j in range(7):
        y = 336 + j * 15
        off = (j % 2) * 18
        blocks.append(f'<path d="M 110 {y} L 490 {y}" stroke="#9A9284" stroke-width="1.2" opacity="0.7"/>')
        for i in range(12):
            x = 110 + off + i * 36
            blocks.append(f'<path d="M {x} {y} L {x} {y + 15}" stroke="#9A9284" stroke-width="1.1" opacity="0.6"/>')
    out.append(clipped(D, pdp, blocks))
    for (ax, aw, ah) in ((200, 44, 72), (300, 54, 86), (400, 44, 72)):
        arch = [(ax - aw / 2, 440)] + [(ax + math.cos(math.radians(a)) * aw / 2, 440 - ah + aw / 2 + math.sin(math.radians(a)) * aw / 2 * -1) for a in range(180, -1, -15)] + [(ax + aw / 2, 440)]
        arch = [(ax - aw / 2, 440)] + [(ax - math.cos(math.radians(a)) * aw / 2, 440 - ah + aw / 2 - math.sin(math.radians(a)) * aw / 2) for a in range(0, 181, 15)] + [(ax + aw / 2, 440)]
        out.append(f'<path d="{pd(arch)}" fill="#3A2A22"/>')
        out.append(f'<path d="{pd(arch)}" fill="none" stroke="#F4EEE0" stroke-width="3"/>')
        out.append(f'<path d="{pd([(ax - aw / 2 + 4, 440), (ax + aw / 2 - 4, 440), (ax + aw / 2 - 4, 436), (ax - aw / 2 + 4, 436)])}" fill="#C8301E" opacity="0.6"/>')
    # pavilion: lower roof, upper storey, upper roof
    out.append(f'<path d="{pd([(150, 300), (450, 300), (450, 332), (150, 332)])}" fill="#C8382A"/>')
    for k in range(9):
        x = 160 + k * 35
        out.append(f'<path d="{pd([(x, 302), (x + 8, 302), (x + 8, 332), (x, 332)])}" fill="#8A1E14"/>')
    out.append(dancheong_band(D, 150, 450, 290, 12, 331))
    out.append(palace_roof(D, 300, 292, 400, 52, 332, lift=20))
    out.append(f'<path d="{pd([(196, 236), (404, 236), (404, 262), (196, 262)])}" fill="#C8382A"/>')
    for k in range(6):
        x = 204 + k * 36
        out.append(f'<path d="{pd([(x, 238), (x + 7, 238), (x + 7, 262), (x, 262)])}" fill="#8A1E14"/>')
    out.append(dancheong_band(D, 196, 404, 226, 11, 333))
    out.append(palace_roof(D, 300, 228, 300, 56, 334, lift=18))
    out.append('</g>')
    # ginkgo trees and leaves drifting
    out.append(ginkgo_tree(D, 66, 470, 200, 335))
    out.append(ginkgo_tree(D, 540, 470, 210, 336))
    # plaza
    out.append(f'<path d="M -10 454 L 610 454 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#E8DCC0"), (1, "#C8B898")])}"/>')
    for j in range(5):
        y = 466 + j * 24 + j * j * 3
        out.append(pline([(-10, y), (610, y + 1)], "#B0A080", 1.2, 337 + j, 0.5, 1))
    for i in range(-6, 7):
        out.append(pline([(300 + i * 40, 454), (300 + i * 120, 610)], "#B0A080", 1.1, 340 + i, 0.4, 1))
    out.append(figures.person(250, 520, 52, "walk", 1, {"top_kind": "dress", "top": "#E8607A", "form": "f", "hair_style": "bun"}, seed=341, light=-1))
    out.append(figures.person(276, 524, 56, "walk", 1, {"top_kind": "long", "top": "#2E5AA8", "bottom": "#F2E6D0", "form": "m", "hair_style": "short"}, seed=342, light=-1))
    out.append(figures.person(380, 504, 34, "stand", -1, seed=343, light=-1))
    rnd = random.Random(344)
    for k in range(16):
        out.append(ginkgo_leaf(D, rnd.uniform(70, 530), rnd.uniform(450, 545), rnd.uniform(9, 14), rnd.uniform(0, 360), 345 + k))
    for k in range(7):
        out.append(ginkgo_leaf(D, rnd.uniform(80, 520), rnd.uniform(200, 420), rnd.uniform(8, 11), rnd.uniform(0, 360), 365 + k))
    # lettering
    out.append(letters(D, 300, 112, "Gyeongbokgung", SERIF_IT, 84, "#FFFFFF", ["#FFFFFF", "#E8F2FF"], 372, max_w=470,
                       shadow="#1E3A6A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 152, "SEOUL · THE PALACE IN AUTUMN", "#1E3A6A", font=JOS, size=18, ls=4, line_w=20, gap=10))
    return finish_b(D, out, 373)


# ================================================================ 13. haenyeo — Jeju's sea women at work among their orange floats
def tewak(D, cx, cy, r, seed, net=True, wl=None):
    """Orange float (tewak) bobbing at the waterline with its net bag (mangsari) hanging below, seen through the water."""
    out = []
    if net:
        npts = [(cx - r * 0.6, cy + r * 0.3), (cx + r * 0.6, cy + r * 0.3), (cx + r * 0.5, cy + r * 2.2), (cx, cy + r * 2.6), (cx - r * 0.5, cy + r * 2.2)]
        nd = smooth_closed(npts)
        out.append(f'<path d="{nd}" fill="#1E5A6A" opacity="0.55"/>')
        mesh = []
        for k in range(-4, 5):
            mesh.append(f'<path d="M {cx + k * r * 0.18:.1f} {cy + r * 0.3:.1f} L {cx + k * r * 0.1:.1f} {cy + r * 2.6:.1f}" stroke="#A8E0D8" stroke-width="1" opacity="0.5"/>')
            mesh.append(f'<path d="M {cx - r:.1f} {cy + r * (1 + k * 0.2):.1f} L {cx + r:.1f} {cy + r * (1 + k * 0.2) + 2:.1f}" stroke="#A8E0D8" stroke-width="1" opacity="0.45"/>')
        out.append(clipped(D, nd, mesh))
        out.append(f'<path d="{blob(cx, cy + r * 1.7, r * 0.3, r * 0.2, seed, 0.3, 8)}" fill="#3A2A2A" opacity="0.6"/>')
    pts = blob_pts(cx, cy, r, r * 0.92, seed, 0.03, 18)
    out.append(painted(D, pts, ("#FFB060", "#F26A1A", "#A8360A"), seed, sdir=(0.5, 0.8), sk=0.22, angle=-40, n=10, inkw=1.4, inkop=0.6, hi=0.5, hik=0.12))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.4, r * 0.25, r * 0.14, seed + 1, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
    out.append(f'<path d="M {cx - r:.1f} {cy + r * 0.2:.1f} Q {cx:.1f} {cy + r * 0.45:.1f} {cx + r:.1f} {cy + r * 0.2:.1f}" stroke="#7A2A0A" stroke-width="1.4" fill="none" opacity="0.5"/>')
    # waterline lapping over the lower half
    out.append(f'<path d="M {cx - r * 1.4:.1f} {cy + r * 0.45:.1f} q {r * 0.35:.1f} {-r * 0.18:.1f} {r * 0.7:.1f} 0 t {r * 0.7:.1f} 0 t {r * 0.7:.1f} 0 t {r * 0.7:.1f} 0" stroke="#E8FFFF" stroke-width="2" fill="none" opacity="0.8"/>')
    return "".join(out)


def diver_head(D, cx, cy, s, seed, facing=1):
    """A haenyeo's head above the water: black rubber hood, round old-style diving mask, a little face."""
    out = []
    hood = blob_pts(cx, cy, 20 * s, 22 * s, seed, 0.05, 16)
    out.append(painted(D, hood, ("#4A4E58", "#1A1C22", "#08080C"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=8, inkw=1.4, inkc="#000000", hi=0.4))
    fx = cx + facing * 4 * s
    face = blob_pts(fx, cy + 4 * s, 12 * s, 13 * s, seed + 1, 0.05, 14)
    out.append(painted(D, face, ("#F2C8A0", "#D8A07A", "#8A5A3A"), seed + 1, sk=0.2, n=4, inkw=1, hi=0.3))
    # mask: round glass in a metal rim, reflecting the sky
    mx, my = fx, cy
    out.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{10.5 * s:.1f}" fill="#C8CCD4" stroke="#5A5E68" stroke-width="{1.6 * s:.1f}"/>')
    out.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{8 * s:.1f}" fill="{D.lin([(0, "#E8F6FF"), (1, "#5AA8C8")])}"/>')
    out.append(f'<path d="M {mx - 5 * s:.1f} {my - 3 * s:.1f} q {3 * s:.1f} {-3 * s:.1f} {7 * s:.1f} {-2 * s:.1f}" stroke="#FFFFFF" stroke-width="{1.6 * s:.1f}" fill="none"/>')
    out.append(f'<path d="M {cx - 20 * s:.1f} {cy - 2 * s:.1f} L {mx - 10 * s:.1f} {my - 1 * s:.1f}" stroke="#2A2A30" stroke-width="{2.4 * s:.1f}"/>')
    # water ring
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy + 18 * s:.1f}" rx="{26 * s:.1f}" ry="{4 * s:.1f}" fill="none" stroke="#E8FFFF" stroke-width="2" opacity="0.8"/>')
    return "".join(out)


def basalt_rock(D, cx, cy, rx, ry, seed, wet=True):
    """Black porous Jeju basalt boulder: dark, pitted, a wet sheen near the water."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, rx, ry, seed, 0.14, 18)
    out = [painted(D, pts, BASALT, seed, sdir=(0.6, 0.7), sk=0.2, angle=-30, n=int(rx * 0.4) + 6, inkw=1.6, inkc="#0A0A0A", hi=0.35)]
    d = smooth_closed(pts)
    pores = []
    for _ in range(int(rx * ry / 90)):
        x, y = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        r = rnd.uniform(1.2, 3.6)
        pores.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.7:.1f}" fill="#141210"/><path d="M {x - r:.1f} {y + r * 0.5:.1f} q {r:.1f} {r * 0.6:.1f} {2 * r:.1f} 0" stroke="#8A8680" stroke-width="0.8" fill="none" opacity="0.7"/>')
    if wet:
        pores.append(f'<path d="{blob(cx - rx * 0.2, cy - ry * 0.4, rx * 0.5, ry * 0.12, seed + 2, 0.2, 10, -8)}" fill="#C8E8F0" opacity="0.3"/>')
    out.append(clipped(D, d, pores))
    return "".join(out)


def hallasan(D, base, seed, haze=0.35, x0=-20, x1=620, peak=250):
    """Hallasan: a broad, gently sloped shield volcano with a flattish summit."""
    line = [(x0, base)]
    for i in range(1, 30):
        t = i / 30
        x = x0 + (x1 - x0) * t
        u = (t - 0.5) * 2
        y = base - (base - peak) * max(0, 1 - abs(u) ** 1.6) ** 1.2
        line.append((x, y))
    line.append((x1, base))
    line = ridge(line, seed, 4, 3)
    return hill(D, line, base + 40, (mix("#9AB0C8", "#FFFFFF", haze), mix("#6A86A8", "#E8EEF6", haze), mix("#4A5E80", "#C8D4E4", haze)), seed + 1, inkw=1.0, inkop=0.3)


def haenyeo_bust(D, cx, wl, s, seed):
    """A haenyeo resting on her float: black rubber hood and suit, round mask pushed up on her forehead,
    a weathered smiling face, one arm draped over the orange tewak. (cx, wl) = head centre x, waterline y."""
    out = []
    hy = wl - 62 * s                  # head centre
    # body below the water: dark, refracted, tinted by the sea
    sub = blob_pts(cx, wl + 60 * s, 70 * s, 70 * s, seed, 0.08, 16)
    out.append(f'<path d="{smooth_closed(sub)}" fill="#0E3A4A" opacity="0.75"/>')
    # shoulders above the water
    sh = [(cx - 74 * s, wl + 4), (cx - 66 * s, wl - 22 * s), (cx - 34 * s, wl - 36 * s), (cx + 34 * s, wl - 36 * s), (cx + 66 * s, wl - 22 * s), (cx + 74 * s, wl + 4)]
    out.append(painted(D, sh, ("#4A505E", "#1A1C24", "#08080C"), seed + 1, sdir=(0.6, 0.6), sk=0.2, angle=-20, n=12, inkw=1.6, inkc="#000000", hi=0.45))
    # hood
    hood = blob_pts(cx, hy, 44 * s, 50 * s, seed + 2, 0.03, 20)
    out.append(painted(D, hood, ("#4A505E", "#1A1C24", "#08080C"), seed + 2, sdir=(0.6, 0.7), sk=0.15, angle=-60, n=14, inkw=1.6, inkc="#000000", hi=0.5))
    out.append(taper([(cx - 30 * s, hy - 34 * s), (cx - 40 * s, hy - 6 * s), (cx - 34 * s, hy + 20 * s)], 5 * s, 2, "#8A92A8", 0.6))
    # face in the hood opening
    face = blob_pts(cx, hy + 8 * s, 29 * s, 34 * s, seed + 3, 0.03, 18)
    fd = smooth_closed(face)
    out.append(painted(D, face, ("#F2C8A0", "#D89A70", "#8A5434"), seed + 3, sdir=(0.6, 0.7), sk=0.15, angle=-80, n=10, inkw=1.4, inkc="#5A3020", hi=0.35))
    out.append(clipped(D, fd, [f'<path d="{blob(cx - 14 * s, hy + 18 * s, 8 * s, 5 * s, seed + 4, 0.2, 8)}" fill="#E8706A" opacity="0.45"/>',
                               f'<path d="{blob(cx + 14 * s, hy + 18 * s, 8 * s, 5 * s, seed + 5, 0.2, 8)}" fill="#E8706A" opacity="0.45"/>']))
    # smiling crescent eyes, laugh lines, a happy open smile
    for sg in (-1, 1):
        ex, ey = cx + sg * 11 * s, hy + 8 * s
        out.append(taper([(ex - 6 * s, ey + 1 * s), (ex, ey - 3 * s), (ex + 6 * s, ey + 1 * s)], 2.6 * s, 2.6 * s, "#3A1A10", 0.95))
        out.append(pline([(ex + sg * 8 * s, ey + 1 * s), (ex + sg * 11 * s, ey + 4 * s)], "#A8644A", 1.1, seed, 0.6, 1))
    out.append(pline([(cx - 1 * s, hy + 10 * s), (cx - 3 * s, hy + 20 * s), (cx + 2 * s, hy + 21 * s)], "#A8644A", 1.4, seed, 0.7, 1))
    mouth = [(cx - 10 * s, hy + 27 * s), (cx, hy + 29 * s), (cx + 10 * s, hy + 27 * s), (cx + 6 * s, hy + 34 * s), (cx, hy + 36 * s), (cx - 6 * s, hy + 34 * s)]
    out.append(f'<path d="{smooth_closed(mouth)}" fill="#8A2A2A"/>')
    out.append(f'<path d="{pd([(cx - 7 * s, hy + 28.5 * s), (cx + 7 * s, hy + 28.5 * s), (cx + 6 * s, hy + 31 * s), (cx - 6 * s, hy + 31 * s)])}" fill="#FFFFFF"/>')
    # mask pushed up on the forehead, strap round the hood
    out.append(taper([(cx - 44 * s, hy - 14 * s), (cx, hy - 24 * s), (cx + 44 * s, hy - 14 * s)], 5 * s, 5 * s, "#2A2C34", 1))
    mx, my = cx, hy - 26 * s
    out.append(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{22 * s:.1f}" ry="{16 * s:.1f}" fill="#B8BCC8" stroke="#4A4E58" stroke-width="{2.4 * s:.1f}"/>')
    out.append(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{17 * s:.1f}" ry="{12 * s:.1f}" fill="{D.lin([(0, "#F4FCFF"), (0.5, "#9AD8E8"), (1, "#3A8AA8")])}"/>')
    out.append(f'<path d="M {mx - 11 * s:.1f} {my - 4 * s:.1f} q {6 * s:.1f} {-6 * s:.1f} {14 * s:.1f} {-4 * s:.1f}" stroke="#FFFFFF" stroke-width="{2.2 * s:.1f}" fill="none"/>')
    # water lapping at the shoulders
    out.append(f'<path d="M {cx - 96 * s:.1f} {wl:.1f} q {12 * s:.1f} {-6 * s:.1f} {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0 t {24 * s:.1f} 0" stroke="#E8FFFF" stroke-width="2.4" fill="none" opacity="0.9"/>')
    return "".join(out)


@design("haenyeo")
def haenyeo():
    D = Doc2("kr-hn")
    out = [sky(D, [(0, "#5AA8E0"), (0.6, "#A8D8F2"), (1, "#E8F6FA")], 381, 300, ["#7AC0EA", "#FFFFFF"], 50, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 474, 222, 116, 382, pal=("#FFFFFF", "#F4F8FF", "#B8C8E0")))
    out.append(hallasan(D, 286, 383, 0.3, x0=30, x1=610, peak=230))
    # sea
    sea = "M -10 284 L 610 284 L 610 610 L -10 610 Z"
    out.append(f'<path d="{sea}" fill="{D.lin([(0, "#5AC8D8"), (0.4, "#1EA0B0"), (1, "#0E5A78")])}"/>')
    out.append(clipped(D, sea, [wave_lines(384, (0, 290, 600, 600), ["#C8F8F8", "#FFFFFF", "#7ADCE0"], 120, (16, 50), 2, 2, (0.3, 0.7)),
                                f'<path d="{blob(300, 300, 320, 8, 385, 0.1, 16)}" fill="#FFFFFF" opacity="0.35"/>']))
    # far divers: floats and little heads near the horizon, one diving with fins up
    for k, (x, y, s) in enumerate(((96, 322, 0.5), (190, 314, 0.42), (520, 318, 0.46))):
        out.append(tewak(D, x, y, 16 * s / 0.5, 386 + k, net=False))
        out.append(diver_head(D, x + 26 * s / 0.5, y, s, 389 + k, facing=-1 if k == 2 else 1))
    fx, fy = 452, 352
    for k, (dx, a) in enumerate(((-5, -12), (5, 10))):
        leg = rot([(fx + dx - 4, fy), (fx + dx + 4, fy), (fx + dx + 3, fy - 24), (fx + dx - 3, fy - 24)], fx + dx, fy, a)
        out.append(painted(D, leg, ("#4A4E58", "#1A1C22", "#08080C"), 392 + k, sk=0.2, n=3, inkw=1, inkc="#000", hi=0.4))
        fin = rot([(fx + dx - 4, fy - 22), (fx + dx + 4, fy - 22), (fx + dx + 8, fy - 46), (fx + dx - 8, fy - 46)], fx + dx, fy, a)
        out.append(painted(D, fin, ("#5A5E68", "#2A2C34", "#0A0A0E"), 394 + k, sk=0.2, n=3, inkw=1, inkc="#000", hi=0.4))
    for k in range(7):
        a = math.radians(-160 + k * 23)
        out.append(taper([(fx + math.cos(a) * 9, fy - 1 + math.sin(a) * 4), (fx + math.cos(a) * 18, fy - 5 + math.sin(a) * 12)], 3, 1, "#FFFFFF", 0.85))
    out.append(f'<ellipse cx="{fx}" cy="{fy + 2}" rx="20" ry="4" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.8"/>')
    # the near haenyeo resting on her float, her catch in the net
    out.append(tewak(D, 400, 452, 52, 396, net=True))
    out.append(haenyeo_bust(D, 262, 470, 1.25, 397))
    # her arm over the float
    arm = [(320, 432), (358, 412), (392, 404), (404, 414), (372, 428), (330, 452)]
    out.append(painted(D, arm, ("#4A505E", "#1A1C22", "#08080C"), 398, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=8, inkw=1.4, inkc="#000", hi=0.45))
    hand = blob_pts(404, 410, 13, 9, 399, 0.1, 12, -20)
    out.append(painted(D, hand, ("#F2C8A0", "#D89A70", "#8A5434"), 399, sk=0.2, n=4, inkw=1.2, inkc="#5A3020", hi=0.35))
    # catch: an abalone shell and a sea urchin in the net just under the surface
    out.append(f'<path d="{blob(392, 520, 16, 11, 400, 0.15, 12, -10)}" fill="#7A8AA8"/>'
               f'<path d="{blob(392, 520, 11, 7, 401, 0.2, 10, -10)}" fill="#C8B8E0" opacity="0.7"/>')
    for k in range(16):
        a = math.radians(k * 22.5)
        out.append(f'<path d="M {414 + math.cos(a) * 6:.1f} {534 + math.sin(a) * 6:.1f} l {math.cos(a) * 8:.1f} {math.sin(a) * 8:.1f}" stroke="#3A1E4A" stroke-width="1.6"/>')
    out.append(f'<circle cx="414" cy="534" r="7" fill="#4A2A5A"/>')
    out.append(f'<path d="M 340 486 L 460 486 L 460 560 L 340 560 Z" fill="#1E8AA0" opacity="0.18"/>')
    # black basalt rocks bottom left and right, foam
    for k, (x, y, rx, ry) in enumerate(((54, 560, 100, 56), (560, 556, 90, 64))):
        out.append(basalt_rock(D, x, y, rx, ry, 402 + k))
    for k, (x, y, w) in enumerate(((120, 526, 60), (500, 510, 60))):
        out.append(f'<path d="{blob(x, y, w, 7, 404 + k, 0.3, 12)}" fill="#FFFFFF" opacity="0.75"/>')
    for k, (x, y, s) in enumerate(((120, 236, 12), (186, 220, 9), (420, 176, 8))):
        out.append(bird_v(x, y, s, "#2A3A5A", 0.8))
    # lettering
    out.append(letters(D, 300, 126, "haenyeo", SERIF_IT, 122, "#FFFFFF", ["#FFFFFF", "#E8F6FF"], 405, max_w=380,
                       shadow="#1E4A7A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "THE SEA WOMEN OF JEJU", "#0E3A6A", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 406)


# ================================================================ 14. dol hareubang — Jeju's stone grandfather among the canola flowers
def canola(D, seed, box, n=200, cols=("#FFF27A", "#F6D21C", "#D8A80A")):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    items = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        sc = 0.4 + 0.9 * (y - y0) / max(1, y1 - y0)
        items.append((y, x, sc))
    out = []
    for y, x, sc in sorted(items):
        h = 26 * sc
        out.append(pline([(x, y), (x + rnd.uniform(-3, 3), y - h)], "#5A8A2A", max(1, 1.6 * sc), int(x), 0.8, 1))
        for k in range(int(5 + 4 * sc)):
            a = rnd.uniform(0, 6.28)
            r = rnd.uniform(2, 7) * sc
            out.append(f'<circle cx="{x + math.cos(a) * r:.1f}" cy="{y - h + math.sin(a) * r * 0.8:.1f}" r="{max(1.2, 2.6 * sc):.1f}" fill="{rnd.choice(cols)}"/>')
    return "".join(out)


def stone_grandfather(D, ox, oy, s, seed):
    """Dol hareubang: porous basalt statue with a mushroom-cap hat, bulging eyes, a long broad nose, a tight smile,
    and both hands resting on the belly, one above the other."""
    rnd = random.Random(seed)

    def P(pts):
        return L(pts, ox, oy, s)

    pal = ("#8A8680", "#58544E", "#2A2724")
    out = [cast(D, ox + 14 * s, oy, 110 * s, 12 * s, strength=0.45, seed=seed)]
    # body column
    body = P([(-62, 0), (-66, -80), (-62, -160), (-56, -196), (56, -196), (62, -160), (66, -80), (62, 0)])
    out.append(painted(D, body, pal, seed, sdir=(0.7, 0.5), sk=0.18, angle=-90, n=50, inkw=2, inkc="#1A1816", hi=0.4))
    # head
    head = P([(-58, -190), (-62, -250), (-54, -294), (-30, -306), (30, -306), (54, -294), (62, -250), (58, -190)])
    out.append(painted(D, head, pal, seed + 1, sdir=(0.7, 0.5), sk=0.15, angle=-90, n=40, inkw=2, inkc="#1A1816", hi=0.45))
    # hat: brim and dome
    brim = P([(-66, -298), (-40, -312), (40, -312), (66, -298), (40, -290), (-40, -290)])
    out.append(painted(D, brim, pal, seed + 2, sdir=(0.5, 1), sk=0.2, angle=0, n=12, inkw=1.8, inkc="#1A1816", hi=0.4))
    dome = P([(-44, -308), (-46, -336), (-30, -356), (0, -362), (30, -356), (46, -336), (44, -308)])
    out.append(painted(D, dome, pal, seed + 3, sdir=(0.6, 0.6), sk=0.18, angle=-60, n=20, inkw=1.8, inkc="#1A1816", hi=0.45))
    # pores over everything
    pores = []
    for pts in (body, head, dome):
        d = smooth_closed(pts)
        x0, y0, x1, y1 = bbox(pts)
        ps = []
        for _ in range(int((x1 - x0) * (y1 - y0) / 110)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            r = rnd.uniform(1, 3.4) * s
            ps.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.75:.1f}" fill="#1E1C1A" opacity="0.85"/><path d="M {x - r:.1f} {y + r * 0.4:.1f} q {r:.1f} {r * 0.6:.1f} {2 * r:.1f} 0" stroke="#B8B2A8" stroke-width="0.8" fill="none" opacity="0.6"/>')
        for _ in range(4):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            ps.append(f'<path d="{blob(x, y, rnd.uniform(6, 14) * s, rnd.uniform(4, 8) * s, rnd.randint(0, 999), 0.35, 10)}" fill="#B8C070" opacity="0.35"/>')
        pores.append(clipped(D, d, ps))
    out += pores
    # face: bulging ringed eyes, nose, mouth
    for sg in (-1, 1):
        ex, ey = P([(sg * 28, -258)])[0]
        ep = blob_pts(ex, ey, 17 * s, 16 * s, seed + 5 + sg, 0.04, 16)
        out.append(painted(D, ep, ("#A8A49C", "#76726A", "#3A3632"), seed + 5 + sg, sdir=(0.6, 0.7), sk=0.3, n=6, inkw=1.0, inkc="#3A3632", inkop=0.5, hi=0.6, hik=0.14))
        out.append(f'<path d="{blob(ex + 3 * s, ey + 5 * s, 10 * s, 6 * s, seed + 8 + sg, 0.2, 8)}" fill="#2A2724" opacity="0.35"/>')
        out.append(f'<path d="{blob(ex - 5 * s, ey - 6 * s, 5 * s, 3 * s, seed + 7 + sg, 0.2, 8)}" fill="#C8C4BC" opacity="0.6"/>')
        # brow ridge
        out.append(taper(P([(sg * 8, -284), (sg * 28, -288), (sg * 48, -280)]), 4 * s, 3 * s, "#2A2724", 0.6))
    nose = P([(-8, -258), (8, -258), (14, -236), (22, -220), (12, -212), (0, -216), (-12, -212), (-22, -220), (-14, -236)])
    out.append(painted(D, nose, pal, seed + 9, sdir=(0.8, 0.4), sk=0.3, angle=-90, n=10, inkw=1.8, inkc="#1A1816", hi=0.5))
    for sg in (-1, 1):
        nx_, ny_ = P([(sg * 11, -216)])[0]
        out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="{4 * s:.1f}" ry="{2.6 * s:.1f}" fill="#1A1816"/>')
    out.append(taper(P([(-20, -200), (0, -197), (20, -200)]), 4 * s, 4 * s, "#1A1816", 0.85))
    out.append(taper(P([(-18, -195), (0, -192), (18, -195)]), 2 * s, 2 * s, "#9A968E", 0.6))
    # hands on the belly, carved in low relief: one forearm higher across the chest, the other lower on the belly
    for k, (y, sg) in enumerate(((-150, 1), (-100, -1))):
        arm = P([(sg * 66, y - 30), (sg * 50, y - 10), (sg * 10, y - 6), (sg * 10, y + 14), (sg * 52, y + 12), (sg * 68, y - 4)])
        out.append(painted(D, arm, ("#9A968E", "#686460", "#2A2724"), seed + 10 + k, sdir=(0.5, 1), sk=0.25, angle=0, n=10, inkw=1.8, inkc="#1A1816", hi=0.45))
        hand = P([(sg * 14, y - 8), (-sg * 22, y - 10), (-sg * 30, y - 2), (-sg * 30, y + 12), (-sg * 20, y + 18), (sg * 14, y + 16)])
        out.append(painted(D, hand, ("#A8A49C", "#76726A", "#2A2724"), seed + 12 + k, sdir=(0.5, 1), sk=0.25, angle=0, n=8, inkw=1.8, inkc="#1A1816", hi=0.5))
        for j in range(3):
            fx_, fy_ = P([(-sg * (4 + j * 9), y - 8)])[0]
            fx2, fy2 = P([(-sg * (4 + j * 9), y + 16)])[0]
            out.append(pline([(fx_, fy_), (fx2, fy2)], "#2A2724", 1.6, seed + j, 0.75, 1))
        tx, ty = P([(-sg * 4, y - 12)])[0]
        out.append(taper([(tx, ty), (tx - sg * 18 * s, ty - 4 * s)], 7 * s, 5 * s, "#76726A"))
    # base stone
    base = P([(-80, 0), (80, 0), (86, 18), (-86, 18)])
    out.append(painted(D, base, pal, seed + 12, sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.6, inkc="#1A1816", hi=0.35))
    return "".join(out)


@design("dol-hareubang")
def dol_hareubang():
    D = Doc2("kr-dh")
    out = [sky(D, [(0, "#4A9AE0"), (0.6, "#9ACCF0"), (1, "#E2F2F8")], 411, 600, ["#6AB0E8", "#FFFFFF"], 50, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 130, 250, 120, 412, pal=("#FFFFFF", "#F4F8FF", "#B8C8E0")))
    out.append(hallasan(D, 340, 413, 0.25, x0=-40, x1=520, peak=262))
    # green fields with black stone walls (batdam), then the yellow canola field
    fl = ridge([(-20, 346), (200, 336), (400, 344), (620, 332)], 414, 4, 3)
    out.append(hill(D, fl, 420, ("#B8D888", "#7AAA4A", "#4A7A2A"), 415, inkw=1.0, inkop=0.3))
    for k, (pts) in enumerate(([(0, 362), (180, 356), (320, 366)], [(260, 380), (420, 372), (610, 382)], [(-10, 398), (200, 392)])):
        out.append(taper(catmull(pts, 6), 5, 5, "#2A2826", 0.9))
        out.append(taper(catmull([(x, y - 2) for x, y in pts], 6), 1.6, 1.6, "#8A8680", 0.7))
    yf = ridge([(-20, 404), (200, 396), (420, 404), (620, 394)], 416, 4, 3)
    out.append(hill(D, yf, 610, ("#FFF27A", "#F2CC1A", "#B8900A"), 417, inkw=1.0, inkop=0.3))
    out.append(canola(D, 418, (-10, 410, 610, 470), 160))
    # the stone grandfather
    out.append(stone_grandfather(D, 300, 524, 0.96, 419))
    out.append(canola(D, 420, (-10, 470, 610, 610), 150))
    # a pair of butterflies
    for k, (x, y) in enumerate(((440, 300), (470, 270))):
        for sg in (-1, 1):
            out.append(f'<path d="{blob(x + sg * 5, y, 6, 8, 421 + k * 3 + sg, 0.2, 8, sg * 30)}" fill="#FFFFFF" stroke="#5A5A5A" stroke-width="0.8"/>')
        out.append(pline([(x, y - 6), (x, y + 6)], INK, 1.4, 422 + k, 0.9, 1))
    # lettering
    out.append(letters(D, 300, 116, "dol hareubang", SERIF_IT, 92, "#24365E", ["#34497A", "#18264A", "#4E64A0"], 423, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8B8E8"))
    out.append(ruled(300, 158, "JEJU'S STONE GRANDFATHER", "#A8501A", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 424)


# ================================================================ 15. namsan — the tower at dusk, love locks on the railing
def namsan_tower(D, cx, base, h, seed, lit=True):
    """A slender broadcast tower on a wooded summit: tapering shaft, a lit observation pod, an antenna mast."""
    out = []
    pod_y = base - h * 0.62
    # shaft
    out.append(f'<path d="{pd([(cx - h * 0.035, base), (cx + h * 0.035, base), (cx + h * 0.022, pod_y), (cx - h * 0.022, pod_y)])}" fill="#E8E2EA"/>')
    out.append(f'<path d="{pd([(cx + h * 0.005, base), (cx + h * 0.035, base), (cx + h * 0.022, pod_y), (cx + h * 0.006, pod_y)])}" fill="#A89AB8" opacity="0.6"/>')
    # observation pod: stacked discs
    for k, (w, dy, col) in enumerate(((0.1, 0.0, "#D8D0E0"), (0.12, -0.035, "#F2EAF2"), (0.11, -0.07, "#C8C0D8"), (0.085, -0.1, "#E8E2EA"))):
        y = pod_y + dy * h
        out.append(f'<path d="{ellipse_d(cx, y, w * h, 0.022 * h)}" fill="{col}"/>')
        out.append(f'<path d="{pd([(cx - w * h, y), (cx + w * h, y), (cx + w * h * 0.95, y - 0.03 * h), (cx - w * h * 0.95, y - 0.03 * h)])}" fill="{col}"/>')
    if lit:
        for k in range(9):
            x = cx - 0.1 * h + k * 0.025 * h
            out.append(f'<rect x="{x:.1f}" y="{pod_y - 0.06 * h:.1f}" width="{0.012 * h:.1f}" height="{0.014 * h:.1f}" fill="#FFE8A0"/>')
        out.append(soft_glow(D, cx, pod_y - 0.05 * h, 0.25 * h, "#FFD8F0", 0.35))
    # antenna mast with red-and-white bands
    top = pod_y - 0.13 * h
    out.append(f'<path d="{pd([(cx - 0.012 * h, top), (cx + 0.012 * h, top), (cx + 0.004 * h, base - h), (cx - 0.004 * h, base - h)])}" fill="#F4F0F4"/>')
    for k in range(4):
        y = top - (k + 0.5) * (top - (base - h)) / 5
        out.append(f'<path d="M {cx - 0.012 * h:.1f} {y:.1f} L {cx + 0.012 * h:.1f} {y:.1f}" stroke="#D8382A" stroke-width="{0.016 * h:.1f}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{base - h:.1f}" r="3" fill="#FF4A3A"/>')
    out.append(soft_glow(D, cx, base - h, 16, "#FF6A5A", 0.6))
    return "".join(out)


def padlock(D, cx, cy, s, col, seed, heart=False, ang=0):
    """A love lock: a little painted padlock (or a heart-shaped one) with its shackle."""
    pal = (lt(col, 0.4), col, dk(col, 0.4))
    out = [f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">']
    out.append(f'<path d="M {cx - 6 * s:.1f} {cy - 4 * s:.1f} L {cx - 6 * s:.1f} {cy - 12 * s:.1f} A {6 * s:.1f} {6 * s:.1f} 0 0 1 {cx + 6 * s:.1f} {cy - 12 * s:.1f} L {cx + 6 * s:.1f} {cy - 4 * s:.1f}" '
               f'stroke="#B8BCC8" stroke-width="{2.4 * s:.1f}" fill="none"/>')
    if heart:
        body = heart_d(cx, cy + 4 * s, 11 * s)
    else:
        body = rect_pts(cx - 10 * s, cy - 6 * s, cx + 10 * s, cy + 12 * s, 6, seed, 0.3)
    out.append(painted(D, body, pal, seed, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=3, inkw=1, inkop=0.6, hi=0.45))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy + 3 * s:.1f}" r="{1.8 * s:.1f}" fill="{pal[2]}"/>')
    out.append("</g>")
    return "".join(out)


@design("namsan")
def namsan():
    D = Doc2("kr-ns")
    out = [sky(D, [(0, "#2A2A6A"), (0.4, "#8A5A9A"), (0.75, "#F29A8A"), (1, "#FFD8A0")], 431, 600, ["#4A4A8A", "#E89AAA", "#FFC8A0"], 80, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(432)
    for _ in range(30):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 200):.0f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(soft_glow(D, 420, 360, 220, "#FFD8B0", 0.4))
    # far city on the hills with lights
    for k, (base, col, dens) in enumerate(((400, "#6A5A8A", 0.6), (430, "#4A3E6A", 0.8))):
        x = -10
        while x < 610:
            w, h = rnd.uniform(14, 34), rnd.uniform(16, 60) * (1.4 - k * 0.3)
            out.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h + 80:.0f}" fill="{col}"/>')
            for j in range(int(h / 8)):
                if rnd.random() < dens * 0.35:
                    out.append(f'<rect x="{x + rnd.uniform(2, w - 5):.0f}" y="{base - h + 3 + j * 8:.0f}" width="2.4" height="3" fill="#FFE0A0" opacity="0.85"/>')
            x += w + rnd.uniform(0, 4)
    # Namsan: the wooded hill and the tower
    hl = ridge([(150, 470), (260, 380), (380, 338), (470, 340), (560, 380), (640, 420)], 433, 6, 3)
    out.append(hill(D, hl, 560, ("#4A5A6A", "#2A3442", "#141A22"), 434, inkw=1.2, inkop=0.3))
    out.append(dab_crown(D, 440, 360, 110, 22, [("#5A6A72", "#36424C", "#1A222A")], 435, n=120, size=(4, 8), inkw=0, base=False))
    out.append(namsan_tower(D, 448, 344, 168, 436))
    # foreground: the railing heavy with love locks, a pink heart lock up front
    rail_y = 470
    out.append(f'<path d="M -10 {rail_y - 30} L 610 {rail_y - 40}" stroke="#2A2438" stroke-width="10"/>')
    out.append(f'<path d="M -10 {rail_y - 34} L 610 {rail_y - 44}" stroke="#8A7AA8" stroke-width="2" opacity="0.6"/>')
    for k in range(-1, 14):
        x = k * 48
        out.append(f'<path d="M {x} {rail_y - 34 - x * 0.016:.1f} L {x} 620" stroke="#2A2438" stroke-width="6"/>')
    # mesh
    mesh = []
    for k in range(-20, 30):
        mesh.append(f'<path d="M {k * 22} {rail_y - 34} L {k * 22 + 180} 620" stroke="#3A3450" stroke-width="1.6" opacity="0.7"/>')
        mesh.append(f'<path d="M {k * 22} {rail_y - 34} L {k * 22 - 180} 620" stroke="#3A3450" stroke-width="1.6" opacity="0.7"/>')
    out.append(clipped(D, f"M -10 {rail_y - 36} L 610 {rail_y - 46} L 610 610 L -10 610 Z", mesh))
    cols = ["#E8506A", "#F2BE2A", "#3E8AD8", "#2EA87A", "#F28A3A", "#B85AC8", "#FF8AB0", "#E8E2D8", "#D8382A"]
    locks = []
    for _ in range(90):
        x, y = rnd.uniform(-10, 610), rnd.uniform(rail_y - 30, 610)
        locks.append((y, x))
    for k, (y, x) in enumerate(sorted(locks)):
        sc = 0.9 + 0.8 * (y - rail_y) / 140
        out.append(padlock(D, x, y, sc, rnd.choice(cols), 437 + k, heart=rnd.random() < 0.25, ang=rnd.uniform(-20, 20)))
    out.append(padlock(D, 300, 520, 2.6, "#E8506A", 540, heart=True, ang=-6))
    out.append(f'<path d="M 278 516 q 22 -16 44 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.5"/>')
    # lettering
    out.append(letters(D, 300, 128, "Namsan", SERIF_IT, 132, "#FFF0E8", ["#FFFFFF", "#FFE0E8", "#F8D0D8"], 541, max_w=380,
                       shadow="#2A2A6A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "SEOUL · LOVE LOCKS AT DUSK", "#FFD8B0", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 542, "#1A1A3A", 0.6)


# ================================================================ 16. gyul — Jeju tangerines on the floral winter blanket
def peony_blanket(D, seed, bg="#F4E8D8"):
    """The classic Korean floral cotton blanket (ibul): big pink and red peonies with green leaves on cream."""
    rnd = random.Random(seed)
    cell = 200
    t = [f'<rect width="{cell}" height="{cell}" fill="{bg}"/>']
    for (fx, fy, r, col) in ((50, 50, 44, "#E8506A"), (150, 150, 48, "#F28AA8"), (160, 40, 26, "#C8283A"), (40, 160, 28, "#F2A8B8")):
        for dx in (-cell, 0, cell):
            for dy in (-cell, 0, cell):
                cx, cy = fx + dx, fy + dy
                if cx + 2 * r < 0 or cx - 2 * r > cell or cy + 2 * r < 0 or cy - 2 * r > cell:
                    continue
                for j in range(3):
                    a = rnd.uniform(0, 6.28) + j * 2.1
                    t.append(f'<path d="{blob(cx + math.cos(a) * r * 1.2, cy + math.sin(a) * r * 1.2, r * 0.6, r * 0.28, seed + j, 0.15, 10, math.degrees(a))}" fill="#3E8A4A"/>')
                for ring, (rr, n) in enumerate(((1.0, 8), (0.72, 7), (0.45, 5))):
                    c = dk(col, 0.12 * ring) if ring else col
                    for j in range(n):
                        a = math.radians(j * 360 / n + ring * 20)
                        t.append(f'<path d="{blob(cx + math.cos(a) * r * rr * 0.55, cy + math.sin(a) * r * rr * 0.55, r * rr * 0.5, r * rr * 0.4, seed + j + ring * 9, 0.15, 10, math.degrees(a))}" fill="{lt(c, 0.25) if j % 2 else c}"/>')
                t.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.16:.1f}" fill="#F6D24A"/>')
    for _ in range(18):
        t.append(f'<circle cx="{rnd.uniform(0, cell):.1f}" cy="{rnd.uniform(0, cell):.1f}" r="{rnd.uniform(1.5, 3):.1f}" fill="#E8A0B0" opacity="0.7"/>')
    pat = D.pattern(cell, cell, "".join(t), transform="rotate(-8)")
    out = [f'<rect width="600" height="600" fill="{pat}"/>']
    # quilting folds and soft light
    for k in range(4):
        y = 80 + k * 150 + rnd.uniform(-20, 20)
        out.append(taper([(-10, y), (300, y + rnd.uniform(-20, 20)), (610, y + rnd.uniform(-20, 20))], 30, 30, "#5A2A2A", 0.06))
        out.append(taper([(-10, y - 12), (300, y - 10), (610, y - 12)], 10, 10, "#FFFFFF", 0.12))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF6E8", 0.35), (1, "#5A2A2A", 0.2)], 0.45, 0.45, 0.75)}"/>')
    return "".join(out)


def tangerine(D, cx, cy, r, seed, leaf=False, light=(-0.6, -0.8)):
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.9, seed, 0.03, 20)
    out = [cast(D, cx + r * 0.25, cy + r * 0.7, r * 0.95, r * 0.35, strength=0.35, seed=seed)]
    out.append(painted(D, pts, ("#FFC060", "#F28A1E", "#B0500A"), seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-40, n=int(r * 0.6) + 6, inkw=max(1, r * 0.04), inkop=0.55, hi=0.45))
    d = smooth_closed(pts)
    out.append(clipped(D, d, [specks(seed + 1, (cx - r, cy - r, cx + r, cy + r), ["#C8600A", "#FFE0A0"], int(r * 2), (0.5, 1.1), (0.3, 0.7))]))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.2, r * 0.12, seed + 2, 0.15, 8, -30)}" fill="#FFF2D0" opacity="0.75"/>')
    out.append(f'<path d="{blob(cx + r * 0.05, cy - r * 0.78, r * 0.12, r * 0.08, seed + 3, 0.2, 8)}" fill="#6A7A2A"/>')
    if leaf:
        out.append(taper([(cx + r * 0.05, cy - r * 0.8), (cx + r * 0.2, cy - r * 1.05)], 3, 2, "#4A5A1A"))
        out.append(leaf_simple(D, cx + r * 0.2, cy - r * 1.05, r * 1.1, r * 0.34, -30, ("#7AB04A", "#3E7A2A", "#1E4A14"), seed + 4))
    return "".join(out)


def peeled_tangerine(D, cx, cy, r, seed):
    """Peeled into a flower: the rind opened in five petals, the fruit with its segments and white pith threads."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 8, cy + 10, r * 1.9, r * 1.3, strength=0.3, seed=seed)]
    for k in range(5):
        a = math.radians(-90 + k * 72 + rnd.uniform(-6, 6))
        tip = (cx + math.cos(a) * r * 2.0, cy + math.sin(a) * r * 1.7)
        p = [(cx + math.cos(a - 0.5) * r * 0.8, cy + math.sin(a - 0.5) * r * 0.7), (cx + math.cos(a - 0.3) * r * 1.7, cy + math.sin(a - 0.3) * r * 1.45), tip,
             (cx + math.cos(a + 0.3) * r * 1.7, cy + math.sin(a + 0.3) * r * 1.45), (cx + math.cos(a + 0.5) * r * 0.8, cy + math.sin(a + 0.5) * r * 0.7)]
        out.append(painted(D, p, ("#FFC060", "#F28A1E", "#B0500A"), seed + k, sk=0.15, n=6, inkw=1.2, inkop=0.5, hi=0.3))
        inner = [(x * 0.82 + cx * 0.18, y * 0.82 + cy * 0.18) for x, y in p]
        out.append(f'<path d="{smooth_closed(inner)}" fill="#FFF2DC" opacity="0.9"/>')
    fp = blob_pts(cx, cy, r * 0.95, r * 0.88, seed + 9, 0.04, 18)
    out.append(painted(D, fp, ("#FFC870", "#F49A30", "#C0600E"), seed + 9, sk=0.18, n=10, inkw=1.2, inkop=0.5, hi=0.4))
    for k in range(9):
        a = math.radians(k * 40 + 10)
        out.append(pline([(cx, cy), (cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.84)], "#C0600E", 1.4, seed + k, 0.6, 1))
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        out.append(pline([(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.2), (cx + math.cos(a + 0.4) * r * 0.6, cy + math.sin(a + 0.4) * r * 0.5), (cx + math.cos(a + 0.2) * r * 0.9, cy + math.sin(a + 0.2) * r * 0.8)], "#FFFDF0", 1.2, seed, 0.8, 1))
    return "".join(out)


@design("gyul")
def gyul():
    D = Doc2("kr-gy")
    out = [peony_blanket(D, 451)]
    # a round bamboo tray of tangerines
    cx, cy, R = 300, 392, 196
    out.append(cast(D, cx + 16, cy + 18, R + 6, R * 0.98, strength=0.4, seed=452))
    tray = blob(cx, cy, R, R, 453, 0.008, 40)
    out.append(f'<path d="{tray}" fill="#D8B070"/>')
    weave = []
    for k in range(-20, 21):
        weave.append(f'<path d="M {cx + k * 10} {cy - R} L {cx + k * 10} {cy + R}" stroke="{["#E8C888", "#B88A4A"][k % 2]}" stroke-width="6" opacity="0.8"/>')
    for k in range(-20, 21):
        y = cy + k * 10
        for j in range(-20, 21, 2):
            x = cx + j * 10 + (k % 2) * 10
            weave.append(f'<rect x="{x - 5}" y="{y - 4}" width="10" height="8" fill="{["#F0D498", "#C8964E"][(j // 2 + k) % 2]}" opacity="0.85"/>')
    weave.append(f'<path d="{tray}" fill="{D.rad([(0, "#FFF2D0", 0.3), (0.8, "#8A5A20", 0.1), (1, "#5A3A10", 0.5)], 0.42, 0.4, 0.62)}"/>')
    out.append(clipped(D, tray, weave))
    out.append(taper(ell_pts(cx, cy, R - 6, R - 6, 0, 360, 48), 12, 12, "#A8783A", 0.9))
    out.append(taper(ell_pts(cx, cy, R - 8, R - 8, 180, 300, 20), 4, 4, "#F4DCA8", 0.8))
    out.append(ink(tray, INK, 1.8, 454, 2, 0.6))
    # the heap
    spots = [(236, 330, 46), (322, 316, 48), (402, 352, 46), (210, 418, 48), (296, 404, 52), (384, 440, 48), (262, 486, 46), (360, 270, 40), (450, 420, 40)]
    for k, (x, y, r) in enumerate(sorted(spots, key=lambda t: t[1])):
        out.append(tangerine(D, x, y, r, 455 + k, leaf=(k in (1, 5))))
    # one peeled into a flower beside the tray, peel crumbs
    out.append(peeled_tangerine(D, 488, 516, 28, 470))
    out.append(tangerine(D, 92, 520, 36, 471, leaf=True))
    # lettering on a cream ribbon band across the top
    band = [(-10, 74), (610, 60), (610, 188), (-10, 196)]
    out.append(f'<path d="{pd(band)}" fill="#FFF8EC" opacity="0.92"/>')
    out.append(f'<path d="M -10 74 L 610 60 M -10 196 L 610 188" stroke="#E8506A" stroke-width="3"/>')
    out.append(letters(D, 300, 154, "gyul", SERIF_IT, 120, "#E8701A", ["#F28A2A", "#C8500A", "#FFA850"], 472, max_w=300,
                       shadow="#FFE0B8", soff=(0.02, 0.035), angle=-40, hi="#FFE0A0"))
    out.append(label(300, 182, "JEJU TANGERINES · PEEL & SHARE", JOS, 18, "#3E7A3A", ls=4, max_w=440))
    return finish_b(D, out, 473)


# ================================================================ 17. hanbok — a festive hanbok on a hanger by a paper door
def hanbok_on_hanger(D, cx, top, s, seed):
    """Woman's hanbok on a wooden hanger: short jeogori jacket with saekdong striped sleeves, white collar band,
    long red goreum ribbons, a full skirt (chima) with a gold-leaf hem band, and a norigae tassel."""
    rnd = random.Random(seed)

    def P(pts):
        return L(pts, cx, top, s)

    out = []
    # hanger
    out.append(ink(f"M {cx:.1f} {top - 30 * s:.1f} q {14 * s:.1f} {-4 * s:.1f} {12 * s:.1f} {-16 * s:.1f} q {-2 * s:.1f} {-10 * s:.1f} {-12 * s:.1f} {-8 * s:.1f}", "#9AA0AC", 3 * s, seed, 1, 1))
    out.append(pline([(cx, top - 30 * s), (cx, top - 8 * s)], "#9AA0AC", 3 * s, seed, 1, 1))
    # skirt: high waist under the jacket, full and flowing, pleats
    chima = P([(-80, 64), (80, 64), (124, 180), (168, 300), (186, 350), (120, 364), (0, 368), (-120, 364), (-186, 350), (-168, 300), (-124, 180)])
    out.append(cast(D, cx + 20 * s, top + 370 * s, 150 * s, 12 * s, strength=0.3, seed=seed))
    out.append(painted(D, chima, ("#F07A8A", "#D8304A", "#8A0E24"), seed + 1, sdir=(0.7, 0.5), sk=0.12, angle=-90, n=60, inkw=2, hi=0.4))
    cd = smooth_closed(chima)
    folds = []
    for k in range(-14, 15):
        x0, y0 = P([(k * 5.6, 64)])[0]
        x1, y1 = P([(k * 12.8, 360)])[0]
        folds.append(pline([(x0, y0), ((x0 + x1) / 2 + rnd.uniform(-3, 3), (y0 + y1) / 2), (x1, y1)], "#8A0E24", 1.2, seed + k, 0.35, 1))
    for k in range(-5, 6):
        x0, y0 = P([(k * 14, 66)])[0]
        x1, y1 = P([(k * 34, 356)])[0]
        folds.append(taper([(x0, y0), ((x0 + x1) / 2 + rnd.uniform(-4, 4), (y0 + y1) / 2), (x1, y1)], 3, 14 * s, "#7A0A1E" if k % 2 else "#FFB8C0", 0.3 if k % 2 else 0.35))
    folds.append(f'<path d="{blob(cx - 50 * s, top + 200 * s, 40 * s, 120 * s, seed + 30, 0.2, 12, 10)}" fill="#FFFFFF" opacity="0.12"/>')
    # gold-leaf hem band (geumbak): a band of stamped little flowers
    hb = P([(-176, 314), (176, 314), (186, 344), (-186, 344)])
    folds.append(f'<path d="{smooth_closed(hb)}" fill="#B8203A"/>')
    for k in range(17):
        x, y = P([(-160 + k * 20, 329)])[0]
        for j in range(5):
            a = math.radians(j * 72)
            folds.append(f'<circle cx="{x + math.cos(a) * 4 * s:.1f}" cy="{y + math.sin(a) * 4 * s:.1f}" r="{2.4 * s:.1f}" fill="#F6CC4A"/>')
        folds.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.6 * s:.1f}" fill="#FFF2B0"/>')
    folds.append(shade_over(D, cd, "#3A0410", 0.35, 0, 0, 1, 0, 0.5))
    out.append(clipped(D, cd, folds))
    # jacket body (jeogori), short
    jb = P([(-70, -2), (70, -2), (78, 80), (44, 94), (-44, 94), (-78, 80)])
    # sleeves hanging from the hanger: saekdong stripes across them, the soft boat-curve (baerae) underneath
    for sg in (-1, 1):
        sl = P([(sg * 60, -2), (sg * 112, 18), (sg * 160, 56), (sg * 168, 74), (sg * 140, 122), (sg * 108, 130), (sg * 84, 114), (sg * 66, 74)])
        sd = smooth_closed(sl)
        out.append(f'<path d="{sd}" fill="#FFE070"/>')
        bands = []
        stripes = ["#D8304A", "#F6C21C", "#2E8A4A", "#2E5AA8", "#F28AB0", "#FFFFFF", "#7A3AA8", "#D8304A", "#F6C21C"]
        A, B = P([(sg * 62, 34)])[0], P([(sg * 156, 96)])[0]
        ax, ay = B[0] - A[0], B[1] - A[1]
        La = math.hypot(ax, ay)
        ux, uy = ax / La, ay / La
        nx, ny = -uy, ux
        for k, c in enumerate(stripes):
            t0, t1 = 0.12 + k * 0.105, 0.12 + (k + 1) * 0.105
            q = [(A[0] + ux * La * t0 + nx * 120, A[1] + uy * La * t0 + ny * 120), (A[0] + ux * La * t1 + nx * 120, A[1] + uy * La * t1 + ny * 120),
                 (A[0] + ux * La * t1 - nx * 120, A[1] + uy * La * t1 - ny * 120), (A[0] + ux * La * t0 - nx * 120, A[1] + uy * La * t0 - ny * 120)]
            bands.append(f'<path d="{pd(q)}" fill="{c}"/>')
        bands.append(strokes(D.nid(), sd, bbox(sl), ["#FFFFFF", "#000000"], seed + 3 + sg, n=24, angle=math.degrees(math.atan2(uy, ux)), length=(10, 30), width=(1, 2.4), opacity=(0.08, 0.2)))
        bands.append(shade_over(D, sd, "#2A0A04", 0.35, 0, 0, 0, 1, 0.45))
        bands.append(taper([(A[0] + nx * 18 * sg, A[1] + ny * 18 * sg), (B[0] + nx * 22 * sg, B[1] + ny * 22 * sg)], 6, 3, "#FFFFFF", 0.25))
        out.append(clipped(D, sd, bands))
        out.append(ink(sd, INK, 1.8, seed + 4 + sg, 2, 0.7))
        cuff = P([(sg * 160, 56), (sg * 170, 72), (sg * 144, 124), (sg * 134, 116)])
        out.append(painted(D, cuff, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), seed + 5 + sg, sk=0.15, n=3, inkw=1.2, hi=0.2))
    out.append(painted(D, jb, ("#FFF4B0", "#F8DC6A", "#B8962A"), seed + 6, sdir=(0.6, 0.6), sk=0.15, angle=-80, n=30, inkw=2, hi=0.4))
    # overlapping front panel, dark collar (git) with white band (dongjeong)
    fp = P([(-6, 4), (40, 4), (66, 84), (40, 92), (-30, 92)])
    out.append(painted(D, fp, ("#FFF4B0", "#F2D25A", "#A8861A"), seed + 7, sdir=(0.8, 0.4), sk=0.15, angle=-70, n=12, inkw=1.6, hi=0.3))
    git = P([(-26, -4), (-6, -4), (36, 54), (24, 60)])
    out.append(painted(D, git, ("#5A7AD0", "#2E4AA8", "#0E1E5E"), seed + 8, sk=0.15, n=4, inkw=1.4, hi=0.3))
    git2 = P([(26, -4), (6, -4), (-20, 40), (-8, 44)])
    out.append(painted(D, git2, ("#5A7AD0", "#2E4AA8", "#0E1E5E"), seed + 9, sk=0.15, n=4, inkw=1.4, hi=0.3))
    out.append(taper(P([(-22, -6), (0, 30), (30, 56)]), 4 * s, 4 * s, "#FFFFFF", 1))
    # goreum: the bow at the chest and two long ribbons
    kx, ky = P([(30, 58)])[0]
    out.append(painted(D, P([(24, 50), (52, 46), (56, 62), (30, 66)]), ("#F07A8A", "#C8203A", "#7A0A1E"), seed + 10, sk=0.15, n=4, inkw=1.4, hi=0.4))
    out.append(painted(D, P([(32, 62), (44, 64), (40, 170), (24, 168)]), ("#F07A8A", "#C8203A", "#7A0A1E"), seed + 11, sk=0.15, angle=-90, n=6, inkw=1.4, hi=0.4))
    out.append(painted(D, P([(44, 62), (56, 64), (66, 150), (52, 152)]), ("#F07A8A", "#C8203A", "#7A0A1E"), seed + 12, sk=0.15, angle=-90, n=6, inkw=1.4, hi=0.4))
    # norigae: knot, jade piece, long tassel
    nx_, ny_ = P([(-34, 100)])[0]
    out.append(pline([(nx_, ny_ - 4 * s), (nx_, ny_ + 20 * s)], "#C8203A", 2 * s, seed, 1, 1))
    out.append(f'<path d="{blob(nx_, ny_ + 26 * s, 9 * s, 11 * s, seed + 13, 0.05, 12)}" fill="#5ABE9A" stroke="#1E6A4A" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(nx_ - 3 * s, ny_ + 22 * s, 3 * s, 4 * s, seed + 14, 0.1, 8)}" fill="#FFFFFF" opacity="0.7"/>')
    for k in range(9):
        out.append(pline([(nx_ - 5 * s + k * 1.2 * s, ny_ + 38 * s), (nx_ - 7 * s + k * 1.8 * s, ny_ + 90 * s)], ["#2E5AA8", "#4A7AD0"][k % 2], 1.6, seed + k, 0.95, 1))
    out.append(f'<path d="{hg.org_rect(nx_ - 7 * s, ny_ + 34 * s, 14 * s, 7 * s, seed + 15, 0.3, 6, 2)}" fill="#F6C21C"/>')
    # hanger bar over the shoulders
    out.append(taper(P([(-120, 6), (0, -8), (120, 6)]), 9 * s, 9 * s, "#8A5A30"))
    out.append(taper(P([(-120, 3), (0, -11), (120, 3)]), 3 * s, 3 * s, "#C8925A", 0.8))
    return "".join(out)


@design("hanbok")
def hanbok():
    D = Doc2("kr-hb")
    # paper sliding doors with wooden lattice, warm daylight through them
    out = [f'<rect width="600" height="600" fill="#F6ECD8"/>']
    out.append(soft_glow(D, 300, 340, 340, "#FFF6E0", 0.7))
    lat = []
    for k in range(40, 601, 52):
        lat.append(f'<path d="M {k} 0 L {k} 600" stroke="#C8A070" stroke-width="2.2" opacity="0.45"/>')
    for k in range(0, 601, 74):
        lat.append(f'<path d="M 0 {k} L 600 {k}" stroke="#C8A070" stroke-width="2.2" opacity="0.45"/>')
    out.append("".join(lat))
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#FFFFFF", "#E8D8B8"], 481, n=60, angle=-80, length=(40, 120), width=(3, 8), opacity=(0.08, 0.2)))
    for x in (40, 560):
        out.append(painted(D, rect_pts(x - 14, -10, x + 14, 610, 30, 482 + x, 0.4), ("#B8865A", "#7A4E2A", "#3A2010"), 482 + x, sdir=(1, 0), sk=0.25, angle=-90, n=20, inkw=1.6, hi=0.3))
    # the hanbok
    out.append(hanbok_on_hanger(D, 300, 232, 0.84, 483))
    # a soft shadow of the hanbok on the paper
    out.append(f'<path d="{blob(330, 420, 170, 190, 484, 0.1, 18)}" fill="#8A6A4A" opacity="0.08"/>')
    # lettering
    out.append(letters(D, 300, 126, "hanbok", SERIF_IT, 128, "#B8203A", ["#D8304A", "#8A0E24", "#F05A6A"], 487, max_w=380,
                       shadow="#FFF6E0", soff=(0.02, 0.035), angle=-40, hi="#FFB0B8"))
    out.append(ruled(300, 172, "WORN WITH JOY", "#2E4AA8", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 488)


# ================================================================ 18. chuseok — songpyeon on pine needles under the harvest moon
def songpyeon(D, cx, cy, s, ang, col, seed):
    """Half-moon rice cake: smooth pastel dough, a pinched seam along the curved back, a sesame-oil sheen."""
    pts = []
    for i in range(17):
        a = math.radians(180 + 180 * i / 16)
        pts.append((cx + math.cos(a) * 30 * s, cy + math.sin(a) * 22 * s))
    pts += [(cx + 26 * s, cy + 6 * s), (cx, cy + 9 * s), (cx - 26 * s, cy + 6 * s)]
    pts = rot(pts, cx, cy, ang)
    pal = (lt(col, 0.45), col, dk(col, 0.3))
    out = [cast(D, cx + 4 * s, cy + 9 * s, 30 * s, 6 * s, strength=0.35, seed=seed)]
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=ang - 20, n=6, inkw=1.2, inkop=0.5, hi=0.55, hik=0.12))
    seam = rot([(cx + math.cos(math.radians(a)) * 27 * s, cy + math.sin(math.radians(a)) * 19 * s) for a in range(200, 341, 20)], cx, cy, ang)
    out.append(pline(seam, dk(col, 0.25), 1.6 * s, seed, 0.6, 1))
    out.append(pline([(x, y + 1.5 * s) for x, y in seam], lt(col, 0.6), 1.2 * s, seed, 0.6, 1))
    hx, hy = rot([(cx - 10 * s, cy - 12 * s)], cx, cy, ang)[0]
    out.append(f'<path d="{blob(hx, hy, 8 * s, 3 * s, seed + 1, 0.2, 8, ang - 20)}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


def pine_needles(seed, cx, cy, rx, ry, n=300):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        b = rnd.uniform(0, 6.28)
        Ls = rnd.uniform(14, 30)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(b) * Ls:.1f} {math.sin(b) * Ls * 0.5:.1f}" stroke="{rnd.choice(["#2E6A3A", "#4E8A44", "#1E4A2A", "#6AA05A"])}" stroke-width="{rnd.uniform(1.2, 2.2):.1f}" stroke-linecap="round" opacity="0.95"/>')
    return "".join(out)


@design("chuseok")
def chuseok():
    D = Doc2("kr-cs")
    out = [sky(D, [(0, "#141A3A"), (0.6, "#2A2E5A"), (1, "#4A3A5A")], 491, 600, ["#2A3060", "#0A0E24"], 70, angle=-4, sop=(0.06, 0.16))]
    rnd = random.Random(492)
    for _ in range(40):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 330):.0f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # the big full moon
    out.append(soft_glow(D, 300, 290, 260, "#FFE8B0", 0.45))
    moon = blob_pts(300, 290, 112, 112, 493, 0.006, 40)
    out.append(painted(D, moon, ("#FFFBE8", "#FCEBB8", "#E0C080"), 493, sdir=(0.5, 0.6), sk=0.06, angle=-30, n=40, inkw=0, hi=0.3))
    md = smooth_closed(moon)
    out.append(clipped(D, md, [f'<path d="{blob(x, y, r, r * 0.8, int(x), 0.2, 10)}" fill="#E8D098" opacity="0.4"/>' for x, y, r in ((260, 260, 22), (330, 310, 18), (300, 240, 12), (350, 260, 10), (270, 320, 14))]))
    # hills and a village of hanok roofs in silhouette
    hl = ridge([(-20, 400), (120, 372), (260, 392), (400, 360), (620, 388)], 494, 8, 4)
    out.append(hill(D, hl, 470, ("#3A3A64", "#24244A", "#121230"), 495, inkw=1.0, inkop=0.3))
    for k, (x, w) in enumerate(((60, 70), (150, 60), (430, 80), (520, 64))):
        out.append(f'<path d="{smooth_closed([(x - w / 2 - 8, 418), (x - w / 2 + 6, 404), (x + w / 2 - 6, 404), (x + w / 2 + 8, 418), (x + w / 2, 420), (x - w / 2, 420)])}" fill="#16163A"/>')
        out.append(f'<rect x="{x - w / 2 + 6:.0f}" y="418" width="{w - 12:.0f}" height="22" fill="#1E1E44"/>')
        out.append(f'<rect x="{x - 8:.0f}" y="424" width="16" height="12" fill="#FFD27A" opacity="0.9"/>')
        out.append(soft_glow(D, x, 430, 30, "#FFC870", 0.4))
    # low wooden table (soban)
    top = [(40, 452), (560, 452), (590, 540), (10, 540)]
    out.append(f'<path d="{pd([(10, 540), (590, 540), (586, 562), (14, 562)])}" fill="#5A3418"/>')
    out.append(painted(D, densify(top, 40), ("#C8925A", "#8A5A30", "#4A2A12"), 496, sdir=(0.3, 1), sk=0.1, angle=-2, n=40, inkw=1.8, hi=0.35))
    out.append(f'<path d="{pd(top)}" fill="{D.rad([(0, "#FFE0A0", 0.35), (1, "#FFE0A0", 0)], 0.5, 0.0, 0.7)}"/>')
    # a round brass plate on a bed of pine needles, heaped with songpyeon
    pcx, pcy = 300, 492
    out.append(cast(D, pcx + 10, pcy + 14, 210, 40, strength=0.5, seed=497))
    out.append(f'<path d="{ellipse_d(pcx, pcy + 8, 200, 44)}" fill="#8A6A2A"/>')
    out.append(painted(D, ell_pts(pcx, pcy, 200, 44, 0, 360, 36)[:-1], ("#FFE8A0", "#D8B050", "#8A6A1A"), 498, sdir=(0.3, 1), sk=0.1, angle=0, n=20, inkw=1.6, hi=0.5))
    out.append(pine_needles(499, pcx, pcy - 4, 170, 34, 260))
    cols = ["#FFFFFF", "#F6B8C8", "#A8C878", "#F6D27A", "#C8A8E0", "#FFFFFF", "#A8C878", "#F6B8C8"]
    spots = [(214, 470), (262, 462), (316, 458), (370, 464), (420, 476), (190, 498), (244, 494), (300, 490), (356, 494), (410, 500),
             (232, 520), (290, 518), (350, 520), (276, 440), (330, 438)]
    for k, (x, y) in enumerate(sorted(spots, key=lambda t: t[1])):
        out.append(songpyeon(D, x, y - 6, 1.0, rnd.uniform(-20, 20), cols[k % len(cols)], 500 + k))
    for _ in range(14):
        x, y = rnd.uniform(160, 440), rnd.uniform(430, 528)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-10, 10):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#4E8A44" stroke-width="1.6" stroke-linecap="round"/>')
    # a little cup of sikhye and two chestnuts
    for k, (x, y) in enumerate(((96, 512), (122, 522))):
        out.append(painted(D, blob_pts(x, y, 14, 12, 520 + k, 0.1, 12), ("#B8784A", "#7A4420", "#3A1E0A"), 520 + k, sk=0.2, n=4, inkw=1.2, hi=0.45))
        out.append(f'<path d="{blob(x, y + 6, 10, 4, 522 + k, 0.1, 8)}" fill="#E8C898"/>')
    out.append(banchan_dish(D, 506, 506, 34, "none", 524, tilt=0.5, rim="#2E5AA8"))
    out.append(f'<path d="{ellipse_d(506, 506, 24, 10)}" fill="#F4E8C8"/>')
    for k in range(5):
        out.append(f'<ellipse cx="{500 + k * 4:.0f}" cy="{503 + (k % 2) * 4:.0f}" rx="2.4" ry="1.4" fill="#FFFFFF"/>')
    # lettering
    out.append(letters(D, 300, 116, "Chuseok", SERIF_IT, 120, "#FFE8B0", ["#FFFFFF", "#FFE0A0", "#F8D890"], 525, max_w=380,
                       shadow="#0A0E24", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 158, "SONGPYEON UNDER THE FULL MOON", "#F2C27A", font=JOS, size=17, ls=4, line_w=20, gap=10))
    return finish_b(D, out, 526, "#0A0E24", 0.6)


# ================================================================ 19. samgyeopsal — pork belly on the table grill, scissors at the ready
def pork_belly(D, x0, y0, x1, y1, w, seed, done=0.6):
    """A strip of pork belly on the grill: pink meat and white fat in layers, golden-brown grill bars."""
    rnd = random.Random(seed)
    a = math.atan2(y1 - y0, x1 - x0)
    Ls = math.hypot(x1 - x0, y1 - y0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x0 + ux * Ls * t + nx * w / 2 + rnd.uniform(-1, 1), y0 + uy * Ls * t + ny * w / 2 + rnd.uniform(-1, 1)))
    for i in range(12, -1, -1):
        t = i / 12
        pts.append((x0 + ux * Ls * t - nx * w / 2 + rnd.uniform(-1, 1), y0 + uy * Ls * t - ny * w / 2 + rnd.uniform(-1, 1)))
    d = smooth_closed(pts)
    meat = mix("#F2A890", "#C8784A", done)
    fat = mix("#FFF4EC", "#F2D29A", done)
    out = [f'<path d="{smooth_closed([(x + nx * 7, y + ny * 7) for x, y in pts])}" fill="{mix("#C8784A", "#6A3412", done)}"/>',
           f'<path d="{d}" fill="{meat}"/>']
    inner = []
    for k, (off, ww, col) in enumerate(((-0.32, 0.18, fat), (0.0, 0.1, fat), (0.3, 0.2, fat), (0.16, 0.06, mix(meat, "#8A3A1A", 0.3)))):
        inner.append(taper([(x0 + nx * w * off, y0 + ny * w * off), (x0 + ux * Ls * 0.5 + nx * w * off + nx * 2, y0 + uy * Ls * 0.5 + ny * w * off + ny * 2), (x1 + nx * w * off, y1 + ny * w * off)],
                           w * ww, w * ww, col, 0.95))
    for k in range(int(Ls / 40)):
        t = (k + 0.5) / (Ls / 40)
        cx_, cy_ = x0 + ux * Ls * t, y0 + uy * Ls * t
        inner.append(f'<path d="{blob(cx_, cy_, w * 0.5, w * 0.3, seed + k, 0.3, 10, math.degrees(a))}" fill="#A8581A" opacity="{0.4 * done + 0.05:.2f}"/>')
    inner.append(taper([(x0 - nx * w * 0.36, y0 - ny * w * 0.36), (x1 - nx * w * 0.36, y1 - ny * w * 0.36)], 2.4, 2.4, "#FFFFFF", 0.55))
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#7A3A1A", 1.3, seed, 1, 0.6))
    return "".join(out)


def bbq_scissors(D, x, y, s, ang, seed):
    def P(pts):
        return rot(L(pts, x, y, s), x, y, ang)
    out = [cast(D, x + 8, y + 10, 70 * s, 14 * s, strength=0.3, seed=seed)]
    for k, sg in enumerate((-1, 1)):
        blade = P([(0, 0), (90, sg * 3), (96, sg * 1), (6, sg * -5)])
        out.append(painted(D, blade, STEEL, seed + k, sk=0.15, n=3, inkw=1.2, inkc="#3A3E4A", hi=0.5))
        ring = P([(-6, sg * 2), (-34, sg * 14), (-60, sg * 16), (-66, sg * 6), (-40, sg * 0)])
        out.append(taper(ring + [ring[0]], 7 * s, 7 * s, "#1A1A22"))
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 * s:.1f}" fill="#8A909C" stroke="#3A3E4A" stroke-width="1.2"/>')
    return "".join(out)


def lettuce_leaf(D, x, y, Ls, W, ang, seed, pal=("#B8E07A", "#6AAE3A", "#2E6A1E")):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    right, left = [], []
    for i in range(17):
        t = i / 16
        w = W * math.sin(math.pi * min(1, 0.15 + t * 0.85)) ** 0.6 * (1 + 0.12 * math.sin(i * 2.6))
        px, py = x + ux * Ls * t, y + uy * Ls * t
        right.append((px + nx * w / 2, py + ny * w / 2))
        left.append((px - nx * w / 2 + rnd.uniform(-1, 1), py - ny * w / 2))
    pts = right + left[::-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.12, angle=ang, n=16, inkw=1.3, inkop=0.5, hi=0.4)]
    out.append(taper([(x, y), (x + ux * Ls * 0.8, y + uy * Ls * 0.8)], W * 0.12, 1.5, "#E8F6C8", 0.85))
    for k in range(5):
        t = 0.2 + k * 0.14
        px, py = x + ux * Ls * t, y + uy * Ls * t
        for sg in (-1, 1):
            out.append(pline([(px, py), (px + (ux * 0.5 + nx * sg) * W * 0.4, py + (uy * 0.5 + ny * sg) * W * 0.4)], "#E8F6C8", 1.1, seed + k, 0.55, 1))
    return "".join(out)


def green_bottle(D, x, base, h, seed):
    """A small green glass bottle with a plain cream label (no brand), condensation dots."""
    w = h * 0.3
    pts = [(x - w / 2, base), (x - w / 2, base - h * 0.62), (x - w * 0.3, base - h * 0.78), (x - w * 0.16, base - h * 0.84), (x - w * 0.16, base - h), (x + w * 0.16, base - h),
           (x + w * 0.16, base - h * 0.84), (x + w * 0.3, base - h * 0.78), (x + w / 2, base - h * 0.62), (x + w / 2, base)]
    out = [cast(D, x + 8, base + 2, w * 0.7, 5, strength=0.4, seed=seed)]
    out.append(painted(D, densify(pts, 10), ("#8AD8A8", "#2E9A5A", "#0E5A2E"), seed, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=10, inkw=1.4, inkc="#0A3A1A", hi=0.45))
    out.append(f'<path d="{pd([(x - w / 2 + 1, base - h * 0.5), (x + w / 2 - 1, base - h * 0.5), (x + w / 2 - 1, base - h * 0.24), (x - w / 2 + 1, base - h * 0.24)])}" fill="#F6F0E0"/>')
    out.append(f'<path d="M {x - w * 0.3:.1f} {base - h * 0.38:.1f} L {x + w * 0.3:.1f} {base - h * 0.38:.1f}" stroke="#2E9A5A" stroke-width="2"/>')
    out.append(taper([(x - w * 0.3, base - h * 0.6), (x - w * 0.32, base - h * 0.08)], 4, 2, "#FFFFFF", 0.6))
    out.append(f'<path d="{hg.org_rect(x - w * 0.18, base - h - 4, w * 0.36, 7, seed, 0.3, 6, 1.5)}" fill="#2E7A4A"/>')
    rnd = random.Random(seed)
    for _ in range(10):
        out.append(f'<circle cx="{x + rnd.uniform(-w * 0.45, w * 0.45):.1f}" cy="{base - rnd.uniform(4, h * 0.2):.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


def shot_glass(D, x, base, h, seed, fill=0.7):
    w = h * 0.8
    pts = [(x - w / 2, base - h), (x + w / 2, base - h), (x + w * 0.38, base), (x - w * 0.38, base)]
    out = [cast(D, x + 4, base + 2, w * 0.5, 3, strength=0.3, seed=seed)]
    out.append(f'<path d="{pd(pts)}" fill="#EAF4F4" opacity="0.6"/>')
    lq = [(x - w * 0.47, base - h * fill), (x + w * 0.47, base - h * fill), (x + w * 0.38, base - 2), (x - w * 0.38, base - 2)]
    out.append(f'<path d="{pd(lq)}" fill="#F4FCFC" opacity="0.8"/>')
    out.append(ink(pd(pts), "#7A8A90", 1.2, seed, 1, 0.8))
    out.append(f'<path d="{ellipse_d(x, base - h, w / 2, 2.4)}" fill="none" stroke="#7A8A90" stroke-width="1.2"/>')
    out.append(taper([(x - w * 0.3, base - h * 0.85), (x - w * 0.26, base - h * 0.2)], 2.4, 1, "#FFFFFF", 0.9))
    return "".join(out)


@design("samgyeopsal")
def samgyeopsal():
    D = Doc2("kr-sg")
    # warm restaurant wall and the silver vent hood coming down over the grill
    out = [sky(D, [(0, "#5A3424"), (1, "#3A2018")], 531, 600, ["#6A4030", "#2A140C"], 90, angle=-80, sop=(0.08, 0.18))]
    out.append(soft_glow(D, 300, 250, 300, "#FFC88A", 0.3))
    rnd0 = random.Random(5310)
    for _ in range(14):
        x, y, r = rnd0.uniform(0, 600), rnd0.uniform(190, 290), rnd0.uniform(10, 24)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="#FFC88A" opacity="{rnd0.uniform(0.08, 0.18):.2f}"/>')
    # table: dark stone-look top
    out.append(f'<path d="M -10 300 L 610 300 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#3A3A40"), (1, "#22222A")])}"/>')
    out.append(f'<path d="M -10 300 L 610 300" stroke="#6A6A78" stroke-width="3"/>')
    out.append(strokes(D.nid(), "M -10 300 L 610 300 L 610 610 L -10 610 Z", (-50, 300, 600, 600), ["#4A4A54", "#16161C"], 533, n=50, angle=-2, length=(60, 160), width=(2, 5), opacity=(0.15, 0.3)))
    # the round grill on its burner ring
    gcx, gcy, grx, gry = 300, 400, 196, 82
    out.append(cast(D, gcx + 12, gcy + 30, grx + 20, gry * 0.7, strength=0.6, seed=534))
    out.append(f'<path d="{ellipse_d(gcx, gcy + 18, grx * 0.86, gry * 0.8)}" fill="#1A1A1E"/>')
    out.append(f'<path d="{ellipse_d(gcx, gcy + 18, grx * 0.86, gry * 0.8)}" fill="none" stroke="#FF7A2A" stroke-width="3" opacity="0.5"/>')
    grill = ell_pts(gcx, gcy, grx, gry, 0, 360, 40)[:-1]
    out.append(painted(D, grill, ("#6A6A72", "#2E2E34", "#101014"), 535, sdir=(0.3, 1), sk=0.1, angle=0, n=20, inkw=1.8, inkc="#000", hi=0.3))
    gd = smooth_closed(grill)
    bars = []
    for k in range(-12, 13):
        x = gcx + k * 15
        bars.append(f'<path d="M {x} {gcy - gry} L {x} {gcy + gry}" stroke="#0A0A0C" stroke-width="5" opacity="0.8"/>')
        bars.append(f'<path d="M {x + 3} {gcy - gry} L {x + 3} {gcy + gry}" stroke="#8A8A94" stroke-width="1.4" opacity="0.5"/>')
    bars.append(f'<path d="{ellipse_d(gcx, gcy, grx * 0.5, gry * 0.5)}" fill="#FF6A1A" opacity="0.18"/>')
    out.append(clipped(D, gd, bars))
    out.append(taper(ell_pts(gcx, gcy, grx * 0.98, gry * 0.96, 170, 330, 20), 4, 3, "#B8B8C4", 0.6))
    # pork belly strips, garlic and kimchi grilling on the rim
    for k, (x0, y0, x1, y1, done) in enumerate(((146, 364, 330, 348, 0.75), (160, 408, 350, 392, 0.55), (186, 452, 374, 438, 0.35))):
        out.append(pork_belly(D, x0, y0, x1, y1, 36, 536 + k, done))
    for k, (x, y) in enumerate(((384, 368), (412, 380), (396, 400), (430, 410), (406, 426))):
        out.append(pork_belly(D, x - 12, y, x + 12, y - 2, 26, 540 + k, 0.8))
    rnd = random.Random(546)
    for _ in range(9):
        a = rnd.uniform(0, 6.28)
        x, y = gcx + math.cos(a) * grx * 0.86, gcy + math.sin(a) * gry * 0.8
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="7" ry="5" fill="#F6E8C0" stroke="#C8A060" stroke-width="1.2"/><ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="2" fill="#E8C878" opacity="0.7"/>')
    out.append(kimchi_piece(D, 470, 432, 26, -10, 547))
    out.append(kimchi_piece(D, 448, 452, 22, 20, 548))
    out.append(steam(250, 350, 120, 549, "#FFFFFF", 3, 50, 9, 0.35))
    for k in range(10):
        x, y = rnd.uniform(160, 420), rnd.uniform(340, 460)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="#FFE8A0" opacity="0.8"/>')
    # scissors and tongs at the ready
    out.append(bbq_scissors(D, 470, 330, 0.9, -160, 550))
    # lettuce, ssamjang, bottle and glasses in front
    out.append(lettuce_leaf(D, 46, 560, 150, 92, -36, 551))
    out.append(lettuce_leaf(D, 70, 586, 130, 80, -14, 552, pal=("#D0EA90", "#88C04A", "#3E7A22")))
    out.append(banchan_dish(D, 238, 522, 34, "none", 553, tilt=0.5, rim="#2E5AA8"))
    out.append(f'<path d="{ellipse_d(238, 522, 22, 9)}" fill="#8A4A1E"/><path d="{blob(232, 518, 6, 2, 554, 0.2, 8)}" fill="#C88A4A"/>')
    out.append(banchan_dish(D, 330, 530, 34, "none", 555, tilt=0.5, rim="#2E5AA8"))
    out.append(f'<path d="{ellipse_d(330, 530, 22, 9)}" fill="#E8C870"/>')
    out.append(green_bottle(D, 480, 542, 116, 556))
    out.append(shot_glass(D, 414, 536, 34, 557))
    out.append(shot_glass(D, 536, 512, 30, 558))
    # lettering
    out.append(letters(D, 300, 124, "samgyeopsal", SERIF_IT, 100, "#FFE8C8", ["#FFFFFF", "#F8D0A0", "#FFE0B8"], 559, max_w=470,
                       shadow="#1A0A04", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 168, "SIZZLE, SNIP, WRAP, REPEAT", "#F6B060", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 560)


# ================================================================ 20. tteokguk — the new-year rice-cake soup that makes you a year older
def bokjumeoni(D, cx, cy, s, seed, pal=("#F07A8A", "#D8304A", "#8A0E24"), band=("#5A7AD0", "#2E4AA8", "#0E1E5E")):
    """Lucky pouch: a round silk purse gathered at the top with a braided cord and tassels, a gold-stitched motif."""
    def P(pts):
        return L(pts, cx, cy, s)
    out = [cast(D, cx + 8, cy + 46 * s, 50 * s, 8 * s, strength=0.4, seed=seed)]
    body = P([(-30, -18), (-46, 6), (-44, 30), (-24, 46), (24, 46), (44, 30), (46, 6), (30, -18)])
    out.append(painted(D, body, pal, seed, sdir=(0.6, 0.7), sk=0.2, angle=-60, n=16, inkw=1.6, hi=0.45))
    bd = smooth_closed(body)
    out.append(clipped(D, bd, [f'<path d="{pd(P([(-60, 10), (60, 10), (60, 20), (-60, 20)]))}" fill="{band[1]}"/>',
                               f'<path d="{pd(P([(-60, 12), (60, 12)]), False)}" stroke="#F6CC4A" stroke-width="1.6"/>']))
    # gold flower motif
    fx, fy = P([(0, 30)])[0]
    for j in range(6):
        a = math.radians(j * 60)
        out.append(f'<circle cx="{fx + math.cos(a) * 5 * s:.1f}" cy="{fy + math.sin(a) * 5 * s:.1f}" r="{3 * s:.1f}" fill="#F6CC4A"/>')
    out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{2.4 * s:.1f}" fill="#FFF2B0"/>')
    # gathered neck and frill
    neck = P([(-30, -18), (-16, -26), (16, -26), (30, -18), (14, -14), (-14, -14)])
    out.append(painted(D, neck, pal, seed + 1, sk=0.2, n=4, inkw=1.4, hi=0.4))
    frill = P([(-24, -26), (-30, -40), (-14, -36), (0, -44), (14, -36), (30, -40), (24, -26)])
    out.append(painted(D, frill, pal, seed + 2, sk=0.2, n=4, inkw=1.4, hi=0.5))
    for j in range(5):
        out.append(pline(P([(-16 + j * 8, -18), (-18 + j * 9, -34)]), pal[2], 1.2, seed + j, 0.6, 1))
    out.append(taper(P([(-34, -22), (0, -16), (34, -22)]), 4 * s, 4 * s, band[1]))
    for sg in (-1, 1):
        kx, ky = P([(sg * 30, -20)])[0]
        out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{4 * s:.1f}" fill="{band[1]}"/>')
        for j in range(5):
            out.append(pline([(kx, ky + 3 * s), (kx + sg * (2 + j) * s, ky + (22 + j % 2 * 3) * s)], band[0] if j % 2 else band[1], 1.6, seed + j, 0.95, 1))
    return "".join(out)


def tteokguk_bowl(D, cx, rim_y, rx, h, seed):
    """Brass-rimmed white bowl of tteokguk: milky beef broth, sliced oval rice cakes, egg ribbons, seaweed, scallion."""
    rnd = random.Random(seed)
    ry = rx * 0.34
    out = [cast(D, cx + 14, rim_y + h + 6, rx * 1.05, 16, strength=0.5, seed=seed)]
    body = [(cx + rx, rim_y), (cx + rx * 0.92, rim_y + h * 0.55), (cx + rx * 0.6, rim_y + h), (cx - rx * 0.6, rim_y + h), (cx - rx * 0.92, rim_y + h * 0.55), (cx - rx, rim_y)]
    body += ell_pts(cx, rim_y, rx, ry, 180, 360, 20)[1:-1]
    out.append(painted(D, body, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), seed, sdir=(0.9, 0.3), sk=0.18, angle=-80, n=20, inkw=1.8, hi=0.5))
    bd = smooth_closed(body)
    out.append(clipped(D, bd, [f'<path d="M {cx - rx} {rim_y + h * 0.4:.1f} Q {cx} {rim_y + h * 0.56:.1f} {cx + rx} {rim_y + h * 0.4:.1f}" stroke="#2E4AA8" stroke-width="5" fill="none"/>',
                               f'<path d="M {cx - rx} {rim_y + h * 0.48:.1f} Q {cx} {rim_y + h * 0.64:.1f} {cx + rx} {rim_y + h * 0.48:.1f}" stroke="#2E4AA8" stroke-width="2" fill="none"/>']))
    out.append(f'<path d="{pd([(cx - rx * 0.56, rim_y + h), (cx + rx * 0.56, rim_y + h), (cx + rx * 0.5, rim_y + h + 10), (cx - rx * 0.5, rim_y + h + 10)])}" fill="#D8D0C4"/>')
    out.append(f'<path d="{ellipse_d(cx, rim_y, rx, ry)}" fill="#E8E2D8"/>')
    soup = ellipse_d(cx, rim_y + 3, rx * 0.93, ry * 0.86)
    out.append(f'<path d="{soup}" fill="{D.rad([(0, "#FFF8E8"), (1, "#E8D8B8")], 0.45, 0.45, 0.6)}"/>')
    items = []
    # rice-cake ovals, overlapping, some lit
    spots = []
    for _ in range(26):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.85
        spots.append((cx + math.cos(a) * rx * 0.9 * rr, rim_y + 3 + math.sin(a) * ry * 0.82 * rr))
    for x, y in sorted(spots, key=lambda p: p[1]):
        a = rnd.uniform(-30, 30)
        op = blob_pts(x, y, 20, 10, rnd.randint(0, 999), 0.04, 14, a)
        items.append(f'<path d="{smooth_closed(op)}" fill="#FFFFFF" stroke="#D8D0C0" stroke-width="1.2"/>')
        items.append(f'<path d="{blob(x - 4, y - 2, 8, 3, rnd.randint(0, 999), 0.2, 8, a)}" fill="#FFFFFF" opacity="0.9"/><path d="{blob(x + 5, y + 3, 10, 4, rnd.randint(0, 999), 0.2, 8, a)}" fill="#E8E0D0" opacity="0.6"/>')
    # egg ribbons, seaweed, beef, scallion at the centre
    for _ in range(12):
        x, y = cx + rnd.uniform(-rx * 0.35, rx * 0.35), rim_y + rnd.uniform(-ry * 0.3, ry * 0.3)
        b = rnd.uniform(0, 6.28)
        items.append(taper([(x, y), (x + math.cos(b) * 26, y + math.sin(b) * 9)], 4.4, 4, rnd.choice(["#F6CC3A", "#FFFFFF", "#F2B820"]), 1))
    for _ in range(14):
        x, y = cx + rnd.uniform(-rx * 0.3, rx * 0.3), rim_y + rnd.uniform(-ry * 0.25, ry * 0.25)
        b = rnd.uniform(0, 6.28)
        items.append(taper([(x, y), (x + math.cos(b) * 14, y + math.sin(b) * 5)], 2.4, 2, "#1A1E1A", 0.95))
    for _ in range(8):
        x, y = cx + rnd.uniform(-rx * 0.3, rx * 0.3), rim_y + rnd.uniform(-ry * 0.3, ry * 0.3)
        items.append(f'<path d="{blob(x, y, 6, 3.5, rnd.randint(0, 99), 0.3, 8)}" fill="#6A3A22"/>')
        items.append(scallion_ring(x + rnd.uniform(-20, 20), y + rnd.uniform(-6, 6), 4.5, rnd.randint(0, 99)))
    items.append(specks(seed + 3, (cx - rx * 0.5, rim_y - ry * 0.4, cx + rx * 0.5, rim_y + ry * 0.4), ["#FFF4D8", "#2A1A10"], 30, (0.8, 1.6), (0.8, 1)))
    items.append(shade_over(D, soup, "#8A6A3A", 0.25, 0, 0, 0, 1, 0.4))
    out.append(clipped(D, soup, items))
    out.append(taper(ell_pts(cx, rim_y, rx - 1, ry - 1, 165, 345, 20), 4, 3, "#FFFFFF", 0.9))
    out.append(ink(ellipse_d(cx, rim_y, rx, ry), INK, 1.6, seed + 1, 1, 0.6))
    return "".join(out)


@design("tteokguk")
def tteokguk():
    D = Doc2("kr-tg")
    # saekdong rainbow stripes behind (like the sleeves of a child's New Year hanbok), a cream table
    cols = ["#D8304A", "#F6C21C", "#2E8A4A", "#2E5AA8", "#F28AB0", "#FFFDF6", "#E8702A"]
    out = [f'<rect width="600" height="600" fill="#FFFDF6"/>']
    y = 0
    k = 0
    while y < 340:
        h = 40
        out.append(f'<rect x="0" y="{y}" width="600" height="{h}" fill="{cols[k % len(cols)]}"/>')
        y += h
        k += 1
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 340 L 0 340 Z", (-40, 0, 600, 340), ["#FFFFFF", "#000000"], 561, n=120, angle=-2, length=(60, 180), width=(2, 6), opacity=(0.05, 0.14)))
    out.append(f'<rect width="600" height="340" fill="#FFF8EC" opacity="0.3"/>')
    # text plaque
    plaque = [(70, 58), (530, 58), (530, 188), (70, 188)]
    out.append(cast(D, 306, 196, 240, 10, strength=0.3, seed=562))
    out.append(painted(D, densify(plaque, 30), ("#FFFDF6", "#F6EEDC", "#C8B494"), 563, sdir=(0.3, 1), sk=0.05, angle=0, n=20, inkw=1.6, hi=0.3))
    out.append(f'<rect x="82" y="70" width="436" height="106" fill="none" stroke="#D8304A" stroke-width="2"/>')
    # table
    out.append(f'<path d="M -10 340 L 610 340 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#C8925A"), (1, "#8A5A30")])}"/>')
    out.append(wood_planks(D, 340, 600, 564, WOOD, 3))
    out.append(f'<rect y="336" width="600" height="8" fill="#3A1A0A" opacity="0.5"/>')
    # soup, spoon, lucky pouches, a dish of kimchi
    out.append(tteokguk_bowl(D, 290, 404, 176, 120, 565))
    out.append(steam(290, 360, 130, 566, "#FFFFFF", 3, 50, 9, 0.5))
    out.append(spoon_chopsticks(D, 70, 540, -8, 190, 567))
    out.append(bokjumeoni(D, 520, 470, 1.15, 568))
    out.append(bokjumeoni(D, 470, 530, 0.9, 569, pal=("#7AC8A8", "#2E8A62", "#0E4A34"), band=("#F07A8A", "#D8304A", "#8A0E24")))
    out.append(banchan_dish(D, 82, 470, 40, "kimchi", 570, rim="#2E5AA8"))
    # lettering on the plaque
    out.append(letters(D, 300, 140, "tteokguk", SERIF_IT, 96, "#B8203A", ["#D8304A", "#8A0E24", "#F05A6A"], 571, max_w=400,
                       shadow="#F6DCC8", soff=(0.02, 0.035), angle=-40, hi="#FFB0B8"))
    out.append(label(300, 168, "ONE BOWL, ONE YEAR OLDER", JOS, 18, "#2E4AA8", ls=4, max_w=400))
    return finish_b(D, out, 572)


# ================================================================ 21. yut nori — four sticks in the air over the painted board
def yut_stick(D, cx, cy, Ls, w, ang, seed, flat_up=True):
    """A yut stick: half-round birch stick; the flat face is pale with X marks, the round back is darker."""
    a = math.radians(ang)
    p0, p1 = (cx - math.cos(a) * Ls / 2, cy - math.sin(a) * Ls / 2), (cx + math.cos(a) * Ls / 2, cy + math.sin(a) * Ls / 2)
    pts = capsule_pts(p0[0], p0[1], p1[0], p1[1], w, w, 4)
    pal = ("#FFF4DC", "#F2DCB0", "#B89A6A") if flat_up else ("#D8A870", "#A8743E", "#5E3A18")
    out = [cast(D, cx + 10, cy + 14, Ls * 0.5, w * 0.6, strength=0.25, seed=seed)]
    out.append(painted(D, pts, pal, seed, sdir=(0.4, 1), sk=0.2, angle=ang, n=8, inkw=1.4, hi=0.45))
    nx, ny = -math.sin(a), math.cos(a)
    if flat_up:
        for k in (-0.25, 0.0, 0.25):
            x, y = cx + math.cos(a) * Ls * k, cy + math.sin(a) * Ls * k
            for sg in (-1, 1):
                out.append(pline([(x - math.cos(a) * 5 + nx * sg * 5, y - math.sin(a) * 5 + ny * sg * 5), (x + math.cos(a) * 5 - nx * sg * 5, y + math.sin(a) * 5 - ny * sg * 5)], "#5A3A1A", 1.6, seed, 0.85, 1))
    else:
        for k in range(4):
            t = -0.35 + k * 0.23
            x, y = cx + math.cos(a) * Ls * t, cy + math.sin(a) * Ls * t
            out.append(pline([(x - nx * w * 0.3, y - ny * w * 0.3), (x + nx * w * 0.3, y + ny * w * 0.3)], "#4A2A10", 1.2, seed + k, 0.5, 1))
    return "".join(out)


def mal(D, cx, cy, r, seed, pal):
    """A playing piece: a little lacquered dome token."""
    pts = blob_pts(cx, cy, r, r * 0.8, seed, 0.03, 14)
    out = [cast(D, cx + 3, cy + r * 0.7, r * 0.9, r * 0.3, strength=0.4, seed=seed)]
    out.append(f'<path d="{smooth_closed([(x, y + r * 0.3) for x, y in pts])}" fill="{pal[2]}"/>')
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=-40, n=3, inkw=1.2, hi=0.55, hik=0.12))
    return "".join(out)


@design("yut-nori")
def yut_nori():
    D = Doc2("kr-yn")
    # straw mat floor
    out = [f'<rect width="600" height="600" fill="#D8B878"/>']
    rnd = random.Random(581)
    mat = []
    for k in range(0, 640, 7):
        mat.append(f'<path d="M -10 {k} L 610 {k + rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#E8CC90", "#B8945A", "#F0D8A0"])}" stroke-width="{rnd.uniform(2, 4):.1f}" opacity="0.7"/>')
    for k in range(-10, 610, 120):
        mat.append(f'<path d="M {k} -10 L {k + 4} 610" stroke="#8A6A3A" stroke-width="2.4" opacity="0.6"/>')
    out.append("".join(mat))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF4D8", 0.35), (1, "#5A3A1A", 0.3)], 0.5, 0.5, 0.75)}"/>')
    # the board: painted cloth, slightly turned
    bx0, by0, bS = 140, 214, 320
    board = rot(densify([(bx0, by0), (bx0 + bS, by0), (bx0 + bS, by0 + bS), (bx0, by0 + bS)], 20), bx0 + bS / 2, by0 + bS / 2, -6)
    out.append(cast(D, bx0 + bS / 2 + 14, by0 + bS / 2 + 16, bS * 0.6, bS * 0.56, strength=0.35, seed=582))
    out.append(painted(D, board, ("#FFFDF4", "#F4EAD2", "#C8B494"), 583, sdir=(0.3, 1), sk=0.06, angle=-6, n=50, inkw=1.8, hi=0.3))

    def B(u, v):
        return rot([(bx0 + 30 + (bS - 60) * u, by0 + 30 + (bS - 60) * v)], bx0 + bS / 2, by0 + bS / 2, -6)[0]

    # lines: square and both diagonals
    for (u0, v0, u1, v1) in ((0, 0, 1, 0), (1, 0, 1, 1), (1, 1, 0, 1), (0, 1, 0, 0), (0, 0, 1, 1), (1, 0, 0, 1)):
        out.append(pline([B(u0, v0), B(u1, v1)], "#2E4AA8", 2.6, int(u0 * 7 + v0 * 3 + u1), 0.85, 1))
    # 29 stations: corners and centre are big
    st = set()
    for i in range(5):
        for (u, v) in ((i / 5, 0), (1, i / 5), (1 - i / 5, 1), (0, 1 - i / 5)):
            st.add((round(u, 3), round(v, 3)))
    for t in (1 / 3, 2 / 3, 0.5):
        for (u, v) in ((t, t), (1 - t, t)):
            st.add((round(u, 3), round(v, 3)))
    for t in (1 / 6, 1 / 3, 2 / 3, 5 / 6):
        st.add((round(t, 3), round(t, 3)))
        st.add((round(1 - t, 3), round(t, 3)))
    st = {p for p in st if p in {(round(u, 3), round(v, 3)) for u in (0, 0.2, 0.4, 0.6, 0.8, 1) for v in (0, 0.2, 0.4, 0.6, 0.8, 1) if u in (0, 1) or v in (0, 1)}
          or abs(p[0] - p[1]) < 1e-3 or abs(p[0] + p[1] - 1) < 1e-3}
    st = {p for p in st if not (abs(p[0] - p[1]) < 1e-3 and p[0] in (0.333, 0.667)) and not (abs(p[0] + p[1] - 1) < 1e-3 and p[0] in (0.333, 0.667))}
    for (u, v) in st:
        x, y = B(u, v)
        big = (u in (0, 1) and v in (0, 1)) or (abs(u - 0.5) < 1e-3 and abs(v - 0.5) < 1e-3)
        r = 14 if big else 9
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{"#D8304A" if big else "#FFFDF6"}" stroke="#2E4AA8" stroke-width="2.4"/>')
        if big:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#F6C21C"/>')
    # tokens on the board
    for k, (u, v, pal) in enumerate(((0.2, 1.0, JEOK), (1.0, 0.6, CHEONG), (0.833, 0.833, JEOK), (0.4, 0.0, CHEONG))):
        x, y = B(u, v)
        out.append(mal(D, x, y - 4, 13, 584 + k, pal))
    # the four sticks tumbling through the air, motion flicks
    for k, (x, y, a, up) in enumerate(((176, 262, -38, True), (300, 236, 18, False), (412, 260, -66, True), (480, 352, 30, True))):
        out.append(yut_stick(D, x, y, 150, 30, a, 590 + k, up))
    for (x, y, a) in ((150, 300, -150), (276, 270, 160), (440, 300, -100), (520, 390, -140)):
        for j in range(3):
            aa = math.radians(a + (j - 1) * 14)
            out.append(taper([(x + math.cos(aa) * 10, y + math.sin(aa) * 10), (x + math.cos(aa) * 30, y + math.sin(aa) * 30)], 2.4, 0.6, "#5A3A1A", 0.5))
    # lettering
    out.append(letters(D, 300, 116, "yut nori", SERIF_IT, 118, "#2E4AA8", ["#3E5AC0", "#1E3480", "#5A7AD8"], 594, max_w=380,
                       shadow="#FFF4D8", soff=(0.02, 0.035), angle=-40, hi="#A8B8F0"))
    out.append(ruled(300, 160, "FOUR STICKS, ONE LOUD FAMILY", "#B8203A", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 595)


# ================================================================ 22. ramyeon — late night, eaten straight off the pot lid
def noodle_tangle(seed, cx, cy, rx, ry, n=80, cols=("#FFE2A0", "#F2C870", "#FFF0C0"), w=3.0, sauce=None):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        pts = [(x, y)]
        for j in range(5):
            x += rnd.uniform(-14, 14)
            y += rnd.uniform(-6, 6)
            pts.append((max(cx - rx, min(cx + rx, x)), max(cy - ry, min(cy + ry, y))))
        c = rnd.choice(cols)
        out.append(f'<path d="{smooth_open(pts)}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" opacity="0.95"/>')
        out.append(f'<path d="{smooth_open([(px, py + w * 0.5) for px, py in pts])}" stroke="#C88A3A" stroke-width="{w * 0.35:.1f}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    return "".join(out)


@design("ramyeon")
def ramyeon():
    D = Doc2("kr-ry")
    # late-night kitchen: deep blue, a window with the moon, a warm hanging lamp glow
    out = [sky(D, [(0, "#1A2448"), (1, "#2A2A4A")], 601, 600, ["#2A3460", "#0E1430"], 70, angle=-80, sop=(0.06, 0.16))]
    win = [(380, 60), (560, 60), (560, 250), (380, 250)]
    out.append(f'<path d="{pd(win)}" fill="{D.lin([(0, "#0E1A3A"), (1, "#2A3A6A")])}"/>')
    out.append(f'<circle cx="500" cy="120" r="26" fill="#FFF4D0"/>')
    out.append(soft_glow(D, 500, 120, 70, "#FFF4D0", 0.4))
    out.append(f'<path d="{pd(win)}" fill="none" stroke="#6A5A4A" stroke-width="8"/>')
    out.append(f'<path d="M 470 60 L 470 250 M 380 155 L 560 155" stroke="#6A5A4A" stroke-width="6"/>')
    out.append(soft_glow(D, 280, 380, 300, "#FFC870", 0.35))
    # counter
    out.append(f'<path d="M -10 420 L 610 420 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#C8925A"), (1, "#7A4E28")])}"/>')
    out.append(wood_planks(D, 420, 600, 602, WOOD, 3))
    out.append(f'<rect y="414" width="600" height="8" fill="#2A1408" opacity="0.6"/>')
    # trivet (a folded newspaper-ish cloth) and the dented yellow aluminium pot
    pcx, rim_y, rx, h = 248, 330, 128, 116
    out.append(cast(D, pcx + 14, rim_y + h + 8, rx * 1.1, 16, strength=0.55, seed=603))
    body = [(pcx + rx, rim_y), (pcx + rx * 0.99, rim_y + h * 0.7), (pcx + rx * 0.94, rim_y + h), (pcx - rx * 0.94, rim_y + h), (pcx - rx * 0.99, rim_y + h * 0.7), (pcx - rx, rim_y)]
    body += ell_pts(pcx, rim_y, rx, rx * 0.3, 180, 360, 20)[1:-1]
    out.append(painted(D, body, ("#FFE89A", "#E8B840", "#9A7010"), 604, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=30, inkw=1.8, hi=0.5))
    bd = smooth_closed(body)
    dents = []
    for (x, y, r) in ((pcx - 60, rim_y + 60, 16), (pcx + 40, rim_y + 80, 12), (pcx + 80, rim_y + 40, 10)):
        dents.append(f'<path d="{blob(x, y, r, r * 0.8, int(x), 0.2, 10)}" fill="#B8861A" opacity="0.45"/><path d="{blob(x - 3, y - 3, r * 0.6, r * 0.4, int(y), 0.2, 8)}" fill="#FFF4C0" opacity="0.6"/>')
    dents.append(taper([(pcx - rx * 0.8, rim_y + 14), (pcx - rx * 0.86, rim_y + h * 0.8)], 8, 3, "#FFFDE8", 0.6))
    out.append(clipped(D, bd, dents))
    for sg in (-1, 1):
        hx = pcx + sg * (rx + 2)
        out.append(ink(f"M {hx:.1f} {rim_y + 14:.1f} q {sg * 26:.1f} 0 {sg * 26:.1f} 14 q 0 12 {-sg * 22:.1f} 12", "#C8A030", 6, 605 + sg, 1, 1))
    out.append(f'<path d="{ellipse_d(pcx, rim_y, rx, rx * 0.3)}" fill="#F6D060"/>')
    soup = ellipse_d(pcx, rim_y + 3, rx * 0.93, rx * 0.26)
    out.append(f'<path d="{soup}" fill="#C8401A"/>')
    out.append(clipped(D, soup, [f'<path d="{blob(pcx - 30, rim_y, 60, 10, 606, 0.2, 10)}" fill="#F07A3A" opacity="0.6"/>',
                                 noodle_tangle(607, pcx, rim_y + 3, rx * 0.8, rx * 0.2, 60),
                                 f'<path d="{blob(pcx + 30, rim_y + 2, 30, 12, 608, 0.1, 12)}" fill="#FFFFFF"/>',
                                 f'<path d="{blob(pcx + 34, rim_y + 1, 13, 8, 609, 0.1, 10)}" fill="#F6B020"/>']))
    for _ in range(10):
        r_ = random.Random(610 + _)
        out.append(scallion_ring(pcx + r_.uniform(-rx * 0.7, rx * 0.7), rim_y + r_.uniform(-20, 22), 4.5, _))
    out.append(ink(ellipse_d(pcx, rim_y, rx, rx * 0.3), INK, 1.4, 611, 1, 0.6))
    # the lid, flipped over as a plate, noodles heaped on it, chopsticks lifting a bite
    lcx, lcy = 452, 452
    out.append(cast(D, lcx + 10, lcy + 22, 120, 18, strength=0.5, seed=612))
    out.append(f'<path d="{ellipse_d(lcx, lcy + 10, 116, 30)}" fill="#B8861A"/>')
    out.append(painted(D, ell_pts(lcx, lcy, 116, 30, 0, 360, 30)[:-1], ("#FFE89A", "#E8B840", "#9A7010"), 613, sdir=(0.3, 1), sk=0.15, angle=0, n=16, inkw=1.6, hi=0.5))
    out.append(f'<path d="{ellipse_d(lcx, lcy + 2, 96, 22)}" fill="#D8A830"/>')
    out.append(noodle_tangle(614, lcx, lcy - 6, 64, 18, 50))
    out.append(f'<path d="{blob(lcx - 10, lcy + 4, 40, 8, 615, 0.3, 10)}" fill="#C8401A" opacity="0.6"/>')
    # noodles lifted on chopsticks with steam
    out.append(noodle_tangle(616, 420, 330, 18, 46, 18, w=3.2))
    out.append(chop := "")
    out.append(taper([(520, 220), (424, 300)], 7, 4, "#C8A070"))
    out.append(taper([(534, 232), (432, 306)], 7, 4, "#B8905A"))
    out.append(steam(248, 290, 110, 617, "#FFFFFF", 3, 40, 9, 0.45))
    out.append(steam(420, 270, 60, 618, "#FFFFFF", 2, 18, 5, 0.4))
    # a small dish of kimchi
    out.append(banchan_dish(D, 92, 520, 44, "kimchi", 619, rim="#2E5AA8"))
    # lettering
    out.append(letters(D, 230, 128, "ramyeon", SERIF_IT, 112, "#FFE8B0", ["#FFFFFF", "#FFE0A0", "#F8D890"], 620, max_w=320,
                       shadow="#0A0E24", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(230, 170, "BEST EATEN OFF THE LID", JOS, 18, "#F6B060", ls=4, max_w=300))
    return finish_b(D, out, 621, "#0A0E24", 0.6)


# ================================================================ 23. jjimjilbang — the bathhouse treat: a lamb-towel, baked eggs, sikhye
def lamb_towel(D, cx, cy, s, seed, pal=("#FFC8D8", "#F28AA8", "#B04A6A")):
    """A towel folded into the 'lamb head' (yangmeori): a band with a rolled spiral bun on each side."""
    def P(pts):
        return L(pts, cx, cy, s)
    out = [cast(D, cx + 10, cy + 60 * s, 120 * s, 12 * s, strength=0.4, seed=seed)]
    band = P([(-70, -20), (0, -36), (70, -20), (76, 30), (0, 16), (-76, 30)])
    out.append(painted(D, band, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=0, n=20, inkw=1.6, hi=0.45))
    bd = smooth_closed(band)
    out.append(clipped(D, bd, [strokes(D.nid(), bd, bbox(band), ["#FFFFFF", pal[2]], seed + 1, n=60, angle=-90, length=(3, 6), width=(1, 1.6), opacity=(0.3, 0.6))]))
    for sg in (-1, 1):
        bx, by = P([(sg * 78, 26)])[0]
        bun = blob_pts(bx, by, 44 * s, 42 * s, seed + 2 + sg, 0.05, 18)
        out.append(painted(D, bun, pal, seed + 2 + sg, sdir=(0.5, 0.8), sk=0.2, angle=-40, n=16, inkw=1.6, hi=0.45))
        spiral = []
        for i in range(40):
            t = i / 39
            a = sg * t * 4.2 * math.pi
            r = 38 * s * (1 - t * 0.9)
            spiral.append((bx + math.cos(a) * r, by + math.sin(a) * r * 0.95))
        out.append(pline(spiral, pal[2], 2.4 * s, seed + sg, 0.7, 1))
        out.append(pline([(x - 2, y - 2) for x, y in spiral], "#FFFFFF", 1.2 * s, seed + sg, 0.5, 1))
        tex = strokes(D.nid(), smooth_closed(bun), bbox(bun), ["#FFFFFF", pal[2]], seed + 5 + sg, n=50, angle=-90, length=(3, 6), width=(1, 1.6), opacity=(0.3, 0.6))
        out.append(clipped(D, smooth_closed(bun), [tex]))
    return "".join(out)


def baked_egg(D, cx, cy, r, seed, cracked=False):
    pts = blob_pts(cx, cy, r * 0.8, r, seed, 0.02, 16)
    out = [cast(D, cx + 4, cy + r * 0.9, r * 0.8, r * 0.25, strength=0.35, seed=seed)]
    out.append(painted(D, pts, ("#E8B88A", "#B8784A", "#6A3A1A"), seed, sdir=(0.5, 0.8), sk=0.22, angle=-60, n=6, inkw=1.2, hi=0.45))
    out.append(specks(seed + 1, (cx - r * 0.6, cy - r * 0.8, cx + r * 0.6, cy + r * 0.8), ["#5A2A10", "#F2D2A8"], 12, (0.6, 1.4), (0.4, 0.8)))
    if cracked:
        top = [(cx - r * 0.78, cy - r * 0.1), (cx - r * 0.5, cy - r * 0.3), (cx - r * 0.3, cy - r * 0.1), (cx, cy - r * 0.32), (cx + r * 0.3, cy - r * 0.08), (cx + r * 0.5, cy - r * 0.3), (cx + r * 0.78, cy - r * 0.1)]
        white = top + [(cx + r * 0.6, cy - r * 0.9), (cx, cy - r * 1.05), (cx - r * 0.6, cy - r * 0.9)]
        out.append(painted(D, white, ("#F6E8D8", "#D8B898", "#8A6A4A"), seed + 2, sk=0.2, n=4, inkw=1.2, hi=0.4))
    return "".join(out)


@design("jjimjilbang")
def jjimjilbang():
    D = Doc2("kr-jj")
    # warm wooden sauna wall, glowing
    out = [f'<rect width="600" height="600" fill="#C8925A"/>']
    out.append(wood_planks(D, 0, 480, 631, ("#E8BA82", "#C8925A", "#7A5230"), 8, vertical=True))
    out.append(soft_glow(D, 300, 330, 320, "#FFE0A8", 0.45))
    # a bather in the house T-shirt, lamb-towel on her head, eyes shut in bliss
    cx, hy = 300, 330
    shirt = [(150, 610), (164, 500), (200, 452), (256, 432), (344, 432), (400, 452), (436, 500), (450, 610)]
    out.append(painted(D, shirt, ("#FFB890", "#F28A5A", "#A8482A"), 632, sdir=(0.6, 0.6), sk=0.15, angle=-80, n=30, inkw=1.8, hi=0.35))
    out.append(f'<path d="M 262 434 Q 300 470 338 434" stroke="#C8603A" stroke-width="4" fill="none"/>')
    neck = [(276, 380), (324, 380), (330, 440), (300, 452), (270, 440)]
    out.append(painted(D, neck, ("#F6D0B0", "#E0A880", "#9A6440"), 633, sk=0.25, angle=-90, n=6, inkw=1.4, inkc="#7A4A30", hi=0.3))
    # hair at the back of the head
    out.append(f'<path d="{blob(cx, hy - 6, 70, 74, 634, 0.04, 20)}" fill="#2A1A14"/>')
    face = blob_pts(cx, hy + 8, 60, 70, 635, 0.03, 22)
    fd = smooth_closed(face)
    out.append(painted(D, face, ("#FAD8BC", "#EDB48E", "#A8704A"), 635, sdir=(0.6, 0.7), sk=0.12, angle=-80, n=14, inkw=1.6, inkc="#7A4A30", hi=0.35))
    out.append(clipped(D, fd, [f'<path d="{blob(cx - 32, hy + 26, 14, 9, 636, 0.2, 8)}" fill="#F27A6A" opacity="0.45"/>',
                               f'<path d="{blob(cx + 32, hy + 26, 14, 9, 637, 0.2, 8)}" fill="#F27A6A" opacity="0.45"/>',
                               f'<path d="{blob(cx, hy - 40, 60, 22, 638, 0.1, 12)}" fill="#2A1A14"/>']))
    # bangs peeking under the towel
    for k in range(7):
        x = cx - 42 + k * 14
        out.append(taper([(x, hy - 50), (x + 3, hy - 32)], 10, 2, "#2A1A14"))
    for sg in (-1, 1):
        ex, ey = cx + sg * 22, hy + 8
        out.append(taper([(ex - 11, ey + 1), (ex, ey - 5), (ex + 11, ey + 1)], 3.6, 3.6, "#2A140C", 0.95))
        out.append(pline([(ex + sg * 13, ey - 1), (ex + sg * 17, ey - 4)], "#2A140C", 1.4, 639, 0.8, 1))
        out.append(taper([(ex - 10, ey - 14), (ex, ey - 17), (ex + 10, ey - 14)], 3, 2, "#3A2418", 0.8))
    out.append(pline([(cx - 2, hy + 14), (cx - 5, hy + 30), (cx + 3, hy + 32)], "#B87A54", 1.6, 640, 0.75, 1))
    out.append(f'<path d="{smooth_closed([(cx - 14, hy + 44), (cx, hy + 47), (cx + 14, hy + 44), (cx + 8, hy + 54), (cx, hy + 56), (cx - 8, hy + 54)])}" fill="#B83A3A"/>')
    # the lamb towel: band over the crown, a rolled spiral bun over each ear
    band = [(cx - 76, hy - 26), (cx - 40, hy - 70), (cx, hy - 80), (cx + 40, hy - 70), (cx + 76, hy - 26), (cx + 60, hy - 18), (cx, hy - 50), (cx - 60, hy - 18)]
    pal = ("#FFF4E8", "#F6E2CC", "#B89878")
    out.append(painted(D, band, pal, 641, sdir=(0.5, 0.8), sk=0.15, angle=-20, n=20, inkw=1.6, hi=0.45))
    bd = smooth_closed(band)
    out.append(clipped(D, bd, [strokes(D.nid(), bd, bbox(band), ["#FFFFFF", pal[2]], 642, n=80, angle=-90, length=(3, 6), width=(1, 1.6), opacity=(0.3, 0.6))]))
    for sg in (-1, 1):
        bx, by = cx + sg * 74, hy - 14
        bun = blob_pts(bx, by, 40, 38, 643 + sg, 0.05, 18)
        out.append(painted(D, bun, pal, 643 + sg, sdir=(0.5, 0.8), sk=0.2, angle=-40, n=16, inkw=1.6, hi=0.45))
        spiral = []
        for i in range(40):
            t = i / 39
            a = sg * t * 4.2 * math.pi
            r = 34 * (1 - t * 0.9)
            spiral.append((bx + math.cos(a) * r, by + math.sin(a) * r * 0.95))
        out.append(pline(spiral, pal[2], 2.4, 645 + sg, 0.75, 1))
        out.append(clipped(D, smooth_closed(bun), [strokes(D.nid(), smooth_closed(bun), bbox(bun), ["#FFFFFF", pal[2]], 647 + sg, n=50, angle=-90, length=(3, 6), width=(1, 1.6), opacity=(0.3, 0.6))]))
    # low table in front: baked eggs in a basket, a cracked one, a bowl of sikhye
    out.append(f'<path d="M -10 500 L 610 500 L 610 610 L -10 610 Z" fill="#8A5A30"/>')
    out.append(wood_planks(D, 506, 600, 650, ("#E8BA82", "#B8824A", "#6A4220"), 3))
    out.append(f'<path d="M -10 500 L 610 500 L 610 508 L -10 508 Z" fill="#E8BA82"/>')
    bcx, bcy = 446, 520
    out.append(cast(D, bcx + 10, bcy + 44, 90, 10, strength=0.45, seed=651))
    bk = [(bcx - 86, bcy - 6), (bcx + 86, bcy - 6), (bcx + 72, bcy + 42), (bcx - 72, bcy + 42)]
    out.append(painted(D, densify(bk, 20), ("#E8C888", "#B8904A", "#6A4A1A"), 652, sdir=(0.5, 1), sk=0.15, angle=0, n=20, inkw=1.6, hi=0.35))
    weave = [f'<path d="M {bcx - 90} {bcy + k * 8} L {bcx + 90} {bcy + k * 8}" stroke="#8A6A2A" stroke-width="1.4" opacity="0.6"/>' for k in range(7)]
    weave += [f'<path d="M {bcx - 90 + k * 13} {bcy - 6} L {bcx - 84 + k * 12} {bcy + 42}" stroke="#F4DCA8" stroke-width="2" opacity="0.5"/>' for k in range(15)]
    out.append(clipped(D, smooth_closed(densify(bk, 20)), weave))
    for k, (x, y, r) in enumerate(((404, 496, 24), (446, 490, 26), (488, 498, 24), (424, 512, 25), (468, 512, 25))):
        out.append(baked_egg(D, x, y, r, 653 + k))
    out.append(baked_egg(D, 360, 540, 22, 658, cracked=True))
    out.append(banchan_dish(D, 150, 540, 54, "none", 659, tilt=0.42, glaze=WHITE, rim="#2E5AA8"))
    out.append(f'<path d="{ellipse_d(150, 540, 40, 14)}" fill="#F4EAD0"/>')
    rnd = random.Random(660)
    for _ in range(18):
        x, y = 150 + rnd.uniform(-30, 30), 540 + rnd.uniform(-8, 8)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.4" ry="1.3" fill="#FFFFFF" stroke="#D8CCB0" stroke-width="0.5"/>')
    out.append(f'<ellipse cx="156" cy="536" rx="3.4" ry="2.4" fill="#F2D29A" stroke="#B8945A" stroke-width="0.8"/>')
    out.append(steam(150, 500, 40, 661, "#FFFFFF", 2, 20, 5, 0.4))
    # lettering
    out.append(letters(D, 300, 116, "jjimjilbang", SERIF_IT, 100, "#5A2A10", ["#7A3E1A", "#3A1A08"], 662, max_w=460,
                       shadow="#FFE8C0", soff=(0.02, 0.035), angle=-40, hi="#C88A5A"))
    out.append(ruled(300, 160, "EGGS, SIKHYE & A LAMB TOWEL", "#A8301A", font=JOS, size=18, ls=4, line_w=22, gap=10))
    return finish_b(D, out, 663)


# ================================================================ 24. hwaiting — exam-day yeot and sticky rice cakes, for luck
def yeot_stick(D, x, y, Ls, w, ang, seed):
    """Amber taffy stick (yeot): twisted, glossy, with sesame specks."""
    a = math.radians(ang)
    p0, p1 = (x - math.cos(a) * Ls / 2, y - math.sin(a) * Ls / 2), (x + math.cos(a) * Ls / 2, y + math.sin(a) * Ls / 2)
    pts = capsule_pts(p0[0], p0[1], p1[0], p1[1], w, w * 0.9, 5)
    out = [painted(D, pts, ("#F8D898", "#D89A4A", "#8A5418"), seed, sdir=(0.4, 1), sk=0.2, angle=ang, n=8, inkw=1.2, hi=0.5)]
    nx, ny = -math.sin(a), math.cos(a)
    for k in range(7):
        t = -0.42 + k * 0.14
        cx_, cy_ = x + math.cos(a) * Ls * t, y + math.sin(a) * Ls * t
        out.append(pline([(cx_ - nx * w * 0.45 - math.cos(a) * 4, cy_ - ny * w * 0.45 - math.sin(a) * 4), (cx_ + nx * w * 0.45 + math.cos(a) * 4, cy_ + ny * w * 0.45 + math.sin(a) * 4)], "#A8661E", 1.4, seed + k, 0.6, 1))
    out.append(taper([(p0[0] - nx * w * 0.25, p0[1] - ny * w * 0.25), (p1[0] - nx * w * 0.25, p1[1] - ny * w * 0.25)], 2.4, 1.6, "#FFF4D8", 0.8))
    return "".join(out)


def chapssaltteok(D, cx, cy, r, seed, pal=("#FFFFFF", "#F6F0E8", "#C8C0B4"), dust="#F2E2C8"):
    pts = blob_pts(cx, cy, r, r * 0.86, seed, 0.03, 18)
    out = [cast(D, cx + 5, cy + r * 0.7, r * 0.9, r * 0.25, strength=0.35, seed=seed)]
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=-40, n=6, inkw=1.1, inkop=0.5, hi=0.5))
    out.append(specks(seed + 1, (cx - r * 0.8, cy - r * 0.7, cx + r * 0.8, cy + r * 0.7), [dust, "#FFFFFF"], int(r * 1.5), (0.6, 1.3), (0.5, 0.9)))
    return "".join(out)


@design("hwaiting")
def hwaiting():
    D = Doc2("kr-hw")
    # sunny yellow with painted rays
    out = [f'<rect width="600" height="600" fill="#F8D25A"/>']
    rays = []
    for k in range(24):
        a0 = math.radians(k * 15)
        a1 = math.radians(k * 15 + 7.5)
        rays.append(f'<path d="M 300 380 L {300 + math.cos(a0) * 700:.0f} {380 + math.sin(a0) * 700:.0f} L {300 + math.cos(a1) * 700:.0f} {380 + math.sin(a1) * 700:.0f} Z" fill="#FFE68A" opacity="0.7"/>')
    out.append("".join(rays))
    out.append(soft_glow(D, 300, 380, 260, "#FFFBE0", 0.6))
    out.append(blooms(651, ["#F2B830", "#FFE07A"], 7, (0, 0, 600, 600), (90, 170), (0.08, 0.16)))
    # a wooden gift tray (exam-luck present): yeot sticks and sticky rice cakes
    tcx, tcy = 300, 452
    out.append(cast(D, tcx + 12, tcy + 64, 230, 20, strength=0.4, seed=652))
    tray = [(tcx - 220, tcy - 50), (tcx + 220, tcy - 50), (tcx + 236, tcy + 60), (tcx - 236, tcy + 60)]
    out.append(f'<path d="{pd([(tcx - 236, tcy + 60), (tcx + 236, tcy + 60), (tcx + 232, tcy + 80), (tcx - 232, tcy + 80)])}" fill="#7A4E28"/>')
    out.append(painted(D, densify(tray, 30), ("#E8BA82", "#C8925A", "#7A5230"), 653, sdir=(0.3, 1), sk=0.08, angle=-2, n=40, inkw=1.8, hi=0.4))
    for k, (x, y, a) in enumerate(((186, 436, -8), (196, 450, -4), (178, 462, -10), (200, 474, -2), (186, 486, -6))):
        out.append(yeot_stick(D, x, y, 170, 22, a, 654 + k))
    out.append(taper([(190, 420), (196, 456), (192, 500)], 12, 12, "#D8304A"))
    out.append(taper([(186, 420), (192, 456), (188, 500)], 3, 3, "#FF8A8A", 0.8))
    out.append(painted(D, [(194, 448), (160, 430), (150, 446), (192, 458), (232, 444), (226, 428)], ("#FF8A8A", "#D8304A", "#7A0E14"), 668, sk=0.2, n=6, inkw=1.4, hi=0.4))
    for k, (x, y, r, pal) in enumerate(((356, 434, 30, ("#FFFFFF", "#F6F0E8", "#C8C0B4")), (418, 434, 30, ("#E8F2C8", "#B8D088", "#6A8A3A")),
                                        (330, 482, 32, ("#FFE0E8", "#F6B0C0", "#B86A80")), (396, 486, 32, ("#FFFFFF", "#F6F0E8", "#C8C0B4")),
                                        (460, 476, 30, ("#E8F2C8", "#B8D088", "#6A8A3A")))):
        out.append(chapssaltteok(D, x, y, r, 658 + k, pal))
    # a pencil and a little note with a heart
    note = [(400, 306), (506, 296), (516, 404), (408, 414)]
    out.append(cast(D, 462, 412, 56, 6, strength=0.3, seed=663))
    out.append(painted(D, note, ("#FFFFFF", "#F6F2FF", "#C8C0D8"), 664, sdir=(0.3, 1), sk=0.08, angle=-6, n=8, inkw=1.4, hi=0.3))
    for k in range(3):
        out.append(pline([(418, 380 + k * 9 - 20), (494, 372 + k * 9 - 20)], "#B8C0E0", 1.2, 669 + k, 0.7, 1))
    out.append(p_heart(D, 458, 384, 16, ("#FF8A8A", "#E0303A", "#8A0A14"), 665, rot_=-6))
    out.append(taper([(110, 540), (330, 526)], 12, 12, "#F6C21C"))
    out.append(taper([(110, 536), (330, 522)], 4, 4, "#FFE07A", 0.8))
    out.append(f'<path d="{pd([(330, 520), (330, 532), (352, 525)])}" fill="#F2D2A8"/><path d="{pd([(344, 522), (344, 528), (352, 525)])}" fill="#2A2A2A"/>')
    out.append(f'<path d="{pd([(96, 542), (110, 546), (110, 534), (96, 538)])}" fill="#F28AB0"/>')
    for x, y, s in ((90, 230, 14), (520, 200, 12), (110, 560, 10), (520, 560, 12)):
        out.append(sparkle(x, y, s, "#FFFFFF", 0.9))
    # lettering: a big, punchy cheer
    out.append(letters(D, 300, 168, "HWAITING!", ANTON, 128, "#D8304A", ["#F0504A", "#A8182A", "#FF6A5A"], 666, ls=3, max_w=470,
                       shadow="#FFFFFF", soff=(0.025, 0.035), angle=-80, wob=0.6, rot=-4))
    out.append(ruled(300, 222, "YOU'VE GOT THIS", "#2E4AA8", font=JOS, size=20, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 667)


# ================================================================ 25. jal meokgesseumnida — the family table, seen from above
def round_bowl_top(D, cx, cy, r, seed, glaze=WHITE, rim=None, fill=None):
    """A bowl seen straight from above: rim ring, inner wall shading, contents."""
    out = [f'<circle cx="{cx + r * 0.12:.1f}" cy="{cy + r * 0.16:.1f}" r="{r * 1.04:.1f}" fill="{D.rad([(0, "#2A1406", 0.4), (0.7, "#2A1406", 0.25), (1, "#2A1406", 0)])}"/>']
    out.append(painted(D, ell_pts(cx, cy, r, r, 0, 360, 30)[:-1], glaze, seed, sdir=(0.6, 0.7), sk=0.08, angle=-40, n=8, inkw=1.4, hi=0.4))
    if rim:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.9:.1f}" fill="none" stroke="{rim}" stroke-width="{max(1.5, r * 0.05):.1f}"/>')
    ir = r * 0.8
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{ir:.1f}" fill="{D.rad([(0, glaze[1]), (0.8, glaze[1]), (1, glaze[2])], 0.6, 0.6, 0.6)}"/>')
    if fill:
        out.append(fill(cx, cy, ir * 0.92))
    return "".join(out)


def rice_top(seed, cx, cy, r):
    rnd = random.Random(seed)
    g = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#FBF8F0"/>']
    for _ in range(int(r * 4)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.95
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        g.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(2.4, 3.2):.1f}" ry="1.4" fill="#FFFFFF" stroke="#D8D2C6" stroke-width="0.5" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    g.append(f'<circle cx="{cx + r * 0.25:.1f}" cy="{cy + r * 0.25:.1f}" r="{r:.1f}" fill="#8A8AA0" opacity="0.12"/>')
    return "".join(g)


def soup_top(seed, cx, cy, r, col="#E8D8A8", bits=("#3E8A2E", "#1A1E1A", "#F2E2B8")):
    rnd = random.Random(seed)
    g = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>']
    for _ in range(int(r * 0.9)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.85
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        g.append(f'<path d="{blob(x, y, rnd.uniform(3, 7), rnd.uniform(2, 4), rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(bits)}" opacity="0.9"/>')
    g.append(f'<ellipse cx="{cx - r * 0.3:.1f}" cy="{cy - r * 0.3:.1f}" rx="{r * 0.3:.1f}" ry="{r * 0.12:.1f}" fill="#FFFFFF" opacity="0.35" transform="rotate(-30 {cx - r * 0.3:.1f} {cy - r * 0.3:.1f})"/>')
    return "".join(g)


def sujeo_top(D, x, y, ang, L_, seed):
    """Spoon and chopsticks seen from above, side by side."""
    return spoon_chopsticks(D, x, y, ang, L_, seed, sep=14)


@design("jal-meokgesseumnida")
def jal_meokgesseumnida():
    D = Doc2("kr-jm")
    out = [wood_planks(D, 0, 600, 701, ("#D8A870", "#A8743E", "#5E3A18"), 5, vertical=True)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFE8B8", 0.3), (1, "#2A1406", 0.35)], 0.5, 0.55, 0.75)}"/>')
    # stew in the middle: doenjang jjigae in a ttukbaegi
    out.append('<g transform="translate(300 400) scale(0.93) translate(-300 -416)">')
    out.append(round_bowl_top(D, 300, 380, 78, 702, glaze=("#7A5444", "#3A2218", "#140A06"),
                              fill=lambda x, y, r: soup_top(703, x, y, r, "#C8904A", ("#FFFBF0", "#3E8A2E", "#8A5A2A", "#E8C870"))))
    out.append(steam(300, 330, 70, 704, "#FFFFFF", 3, 30, 7, 0.45))
    # ring of banchan
    ring = [(150, 300, "kimchi"), (226, 254, "spinach"), (374, 254, "sprouts"), (450, 300, "beans"), (468, 400, "fishcake"), (132, 400, "egg"),
            (210, 474, "kkakdugi"), (390, 474, "spinach")]
    for k, (x, y, kind) in enumerate(ring):
        out.append(banchan_dish(D, x, y, 40, kind, 705 + k, tilt=1.0, rim="#2E5AA8" if k % 2 else None))
    # place settings for the family: rice and soup bowls, spoon and chopsticks
    for k, (x, y) in enumerate(((150, 548), (300, 560), (450, 548))):
        out.append(round_bowl_top(D, x - 34, y - 10, 34, 720 + k, glaze=STEEL, fill=lambda a, b, r, kk=k: rice_top(730 + kk, a, b, r)))
        out.append(round_bowl_top(D, x + 36, y - 10, 32, 740 + k, glaze=WHITE, rim="#2E5AA8", fill=lambda a, b, r, kk=k: soup_top(750 + kk, a, b, r, "#C83A1E", ("#F2E2B8", "#3E8A2E", "#FFFFFF"))))
    out.append(spoon_chopsticks(D, 520, 486, -96, 110, 760, sep=11))
    out.append(spoon_chopsticks(D, 84, 486, -84, 110, 761, sep=11))
    out.append('</g>')
    # a linen runner at the top carrying the words
    runner = [(-10, 66), (610, 54), (610, 196), (-10, 206)]
    out.append(cast(D, 300, 206, 300, 10, strength=0.3, seed=762))
    out.append(painted(D, densify(runner, 30), ("#FFFDF6", "#F6EEDC", "#C8B494"), 763, sdir=(0.3, 1), sk=0.06, angle=-2, n=50, inkw=1.4, hi=0.3))
    out.append(f'<path d="M -10 80 L 610 68 M -10 192 L 610 182" stroke="#2E4AA8" stroke-width="2.4" opacity="0.8"/>')
    out.append(letters(D, 300, 142, "jal meokgesseumnida", SERIF_IT, 64, "#8A2A14", ["#A8361E", "#5A1A0A"], 764, max_w=480, angle=-40, wob=0.6))
    out.append(label(300, 174, "THANK YOU FOR THE FOOD", JOS, 18, "#2E4AA8", ls=5, max_w=420))
    return finish_b(D, out, 765)


# ================================================================ 26. eomma's gimbap — picnic rolls, sliced, in a lunchbox
def gimbap_slice(D, cx, cy, r, seed, tilt=0.62):
    """A gimbap slice cut face up (3/4 view): dark seaweed ring, white rice, and the colourful fillings."""
    rnd = random.Random(seed)
    ry = r * tilt
    out = [f'<path d="{ellipse_d(cx, cy + r * 0.32, r, ry)}" fill="#141C14"/>']
    out.append(f'<path d="{pd([(cx - r, cy), (cx + r, cy), (cx + r, cy + r * 0.32), (cx - r, cy + r * 0.32)])}" fill="#1A221A"/>')
    out.append(f'<path d="{ellipse_d(cx, cy, r, ry)}" fill="#1E2A1E"/>')
    rice = ellipse_d(cx, cy, r * 0.9, ry * 0.88)
    items = [f'<path d="{rice}" fill="#FBF8F0"/>']
    for _ in range(int(r * 3)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * r * 0.9 * rr, cy + math.sin(a) * ry * 0.88 * rr
        items.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.2" ry="1.2" fill="#FFFFFF" stroke="#D8D2C6" stroke-width="0.5" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    fills = [("#F6D21C", 0.0, -0.22, 0.2), ("#F2862A", -0.3, 0.1, 0.12), ("#3E8A2E", 0.28, 0.12, 0.14), ("#F2A0B0", 0.0, 0.26, 0.14),
             ("#F6E07A", -0.26, -0.18, 0.12), ("#6A3A22", 0.26, -0.2, 0.12)]
    for k, (col, dx, dy, s_) in enumerate(fills):
        x, y = cx + dx * r * 1.4, cy + dy * ry * 1.4
        items.append(f'<path d="{blob(x, y, r * s_ * 1.3, ry * s_ * 1.2, seed + k, 0.15, 10, rnd.uniform(0, 180))}" fill="{col}"/>')
        items.append(f'<path d="{blob(x - r * 0.03, y - ry * 0.04, r * s_ * 0.6, ry * s_ * 0.4, seed + k + 9, 0.2, 8)}" fill="#FFFFFF" opacity="0.35"/>')
    items.append(f'<path d="{blob(cx - r * 0.3, cy - ry * 0.4, r * 0.25, ry * 0.12, seed + 20, 0.2, 8)}" fill="#FFFFFF" opacity="0.5"/>')
    out.append(clipped(D, rice, items))
    out.append(f'<path d="{ellipse_d(cx, cy, r * 0.97, ry * 0.95)}" fill="none" stroke="#3A4A3A" stroke-width="1.2" opacity="0.7"/>')
    for _ in range(int(r * 0.6)):
        a = rnd.uniform(0, 6.28)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.95:.1f}" cy="{cy + math.sin(a) * ry * 0.95:.1f}" r="1" fill="#F2E2B8" opacity="0.9"/>')
    return "".join(out)


@design("eommas-gimbap")
def eommas_gimbap():
    D = Doc2("kr-eg")
    # picnic: a gingham mat on grass, dappled light
    out = [f'<rect width="600" height="600" fill="#8AC06A"/>']
    out.append(grass(791, (-10, -10, 610, 610), ["#6AA44A", "#A8D07A", "#4E8A3A"], n=500, h=(8, 18), w=1.6))
    mat = [(30, 236), (580, 210), (600, 610), (0, 610)]
    md = pd(mat)
    from brasil_painted import gingham as _ging
    out.append(_ging(D, md, "#5A8AD8", "#FFFDF6", 22, rot_=-3, op=0.5))
    out.append(shade_over(D, md, "#1A2A4A", 0.25, 0, 0, 0, 1, 0.5))
    rnd = random.Random(792)
    for _ in range(9):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(220, 600), rnd.uniform(40, 80), rnd.uniform(20, 40), rnd.randint(0, 99), 0.3, 12)}" fill="#FFF6D0" opacity="0.18"/>')
    # oval wooden lunchbox, slices packed in rows
    out.append('<g transform="translate(300 400) scale(0.94) translate(-300 -414)">')
    bcx, bcy, brx, bry = 300, 420, 236, 116
    out.append(cast(D, bcx + 14, bcy + 30, brx + 10, bry * 0.8, strength=0.5, seed=793))
    out.append(f'<path d="{ellipse_d(bcx, bcy + 22, brx, bry)}" fill="#8A5A30"/>')
    out.append(painted(D, ell_pts(bcx, bcy, brx, bry, 0, 360, 40)[:-1], ("#F2CC94", "#D8A468", "#8A5A30"), 794, sdir=(0.3, 1), sk=0.08, angle=0, n=30, inkw=1.8, hi=0.4))
    inner = ellipse_d(bcx, bcy + 4, brx * 0.92, bry * 0.86)
    out.append(f'<path d="{inner}" fill="#B88A54"/>')
    slices = []
    for row, (y, n, x0) in enumerate(((356, 6, 112), (408, 7, 86), (462, 6, 112))):
        for i in range(n):
            slices.append((y, x0 + i * 63))
    sl = []
    for k, (y, x) in enumerate(sorted(slices)):
        sl.append(gimbap_slice(D, x, y, 32, 795 + k))
    out.append(clipped(D, inner, sl + [shade_over(D, inner, "#2A1406", 0.25, 0, 0, 0, 1, 0.3)]))
    out.append('</g>')
    # a whole roll beside the box, and pickled radish (danmuji) on a little dish
    out.append(cast(D, 470, 556, 90, 8, strength=0.4, seed=830))
    roll = capsule_pts(384, 540, 540, 524, 42, 42, 8)
    out.append(painted(D, roll, ("#3A4A3A", "#1A221A", "#080C08"), 831, sdir=(0.3, 1), sk=0.2, angle=-6, n=20, inkw=1.4, inkc="#000", hi=0.4))
    for k in range(6):
        x = 404 + k * 24
        out.append(pline([(x, 522 - k * 2), (x + 2, 560 - k * 2)], "#3E4E3E", 1.2, 832 + k, 0.6, 1))
    out.append(specks(833, (392, 516, 536, 556), ["#F2E2B8"], 40, (0.8, 1.4), (0.8, 1)))
    out.append(banchan_dish(D, 100, 524, 38, "none", 834, tilt=0.55, rim="#2E5AA8"))
    for k in range(5):
        out.append(f'<path d="{blob(84 + k * 8, 520 + (k % 2) * 6, 10, 5, 835 + k, 0.1, 10, 20)}" fill="#F6D21C" stroke="#C8A00A" stroke-width="1"/>')
    # a note from mom stuck to the lid, with 엄마 painted and a heart
    note = [(408, 206), (540, 196), (548, 300), (414, 310)]
    out.append(cast(D, 482, 310, 66, 7, strength=0.3, seed=840))
    out.append(painted(D, note, ("#FFFBE0", "#FFF2B0", "#C8B870"), 841, sdir=(0.3, 1), sk=0.08, angle=-4, n=8, inkw=1.4, hi=0.3))
    out.append(f'<g transform="rotate(-4 478 252)">{hangul(D, 470, 216, 54, "엄마", "#C8203A", 842, w=6.2, paper_c="#FFF2B0")}</g>')
    out.append(p_heart(D, 520, 284, 9, ("#FF8A8A", "#E0303A", "#8A0A14"), 843, rot_=-4))
    # lettering
    out.append(letters(D, 214, 128, "eomma's", SERIF_IT, 76, "#FFFFFF", ["#FFFFFF", "#F2FAE8"], 844, max_w=300,
                       shadow="#2E5A1E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 214, 194, "gimbap", SERIF_IT, 76, "#FFFFFF", ["#FFFFFF", "#F2FAE8"], 845, max_w=300,
                       shadow="#2E5A1E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(f'<path d="{hg.org_rect(64, 210, 300, 24, 847, 0.5, 10, 6)}" fill="#FFFDF0" opacity="0.92"/>')
    out.append(label(214, 228, "PICNIC DAY, PACKED WITH LOVE", JOS, 16, "#2E5A1E", ls=3, max_w=280))
    return finish_b(D, out, 846)


# ================================================================ 27. halmeoni — grandma, insisting you eat more
def halmeoni_bust(D, cx, hy, s, seed):
    """Grandma: short tight perm in silver curls, gentle smiling eyes behind round glasses, a floral blouse and a
    quilted vest; she holds out a bowl of rice heaped absurdly high."""
    rnd = random.Random(seed)
    out = []
    # blouse and quilted vest
    shirt = [(cx - 160 * s, 640), (cx - 150 * s, hy + 150 * s), (cx - 110 * s, hy + 104 * s), (cx - 46 * s, hy + 86 * s), (cx + 46 * s, hy + 86 * s),
             (cx + 110 * s, hy + 104 * s), (cx + 150 * s, hy + 150 * s), (cx + 160 * s, 640)]
    out.append(painted(D, shirt, ("#F8C8D8", "#E88AA8", "#9A3A5A"), seed, sdir=(0.6, 0.6), sk=0.12, angle=-80, n=30, inkw=1.8, hi=0.35))
    sd = smooth_closed(shirt)
    flowers = []
    for _ in range(40):
        x, y = rnd.uniform(cx - 160 * s, cx + 160 * s), rnd.uniform(hy + 90 * s, 600)
        for j in range(5):
            a = math.radians(j * 72)
            flowers.append(f'<circle cx="{x + math.cos(a) * 4:.1f}" cy="{y + math.sin(a) * 4:.1f}" r="3" fill="{rnd.choice(["#FFFFFF", "#F6D24A", "#C8304A"])}" opacity="0.85"/>')
        flowers.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#F6D24A"/>')
    out.append(clipped(D, sd, flowers))
    for sg in (-1, 1):
        vest = [(cx + sg * 160 * s, 640), (cx + sg * 150 * s, hy + 150 * s), (cx + sg * 110 * s, hy + 104 * s), (cx + sg * 60 * s, hy + 92 * s), (cx + sg * 40 * s, 640)]
        out.append(painted(D, vest, ("#6A9AD0", "#2E5AA8", "#14306A"), seed + 1 + sg, sdir=(0.6, 0.6), sk=0.15, angle=-80, n=16, inkw=1.6, hi=0.35))
        vd = smooth_closed(vest)
        quilt = [f'<path d="M {cx + sg * 30 * s:.1f} {hy + 100 * s + k * 26:.1f} L {cx + sg * 180 * s:.1f} {hy + 70 * s + k * 26:.1f}" stroke="#1E3A7A" stroke-width="1.4" stroke-dasharray="4 3" opacity="0.8"/>' for k in range(12)]
        out.append(clipped(D, vd, quilt))
    neck = [(cx - 30 * s, hy + 50 * s), (cx + 30 * s, hy + 50 * s), (cx + 34 * s, hy + 96 * s), (cx, hy + 104 * s), (cx - 34 * s, hy + 96 * s)]
    out.append(painted(D, neck, ("#F2C8A4", "#D8A07A", "#8A5A3A"), seed + 3, sk=0.25, angle=-90, n=6, inkw=1.4, inkc="#7A4A30", hi=0.3))
    # silver perm behind the head
    for _ in range(46):
        a = rnd.uniform(math.pi * 0.9, math.pi * 2.1)
        rr = rnd.uniform(0.8, 1.05)
        x, y = cx + math.cos(a) * 82 * s * rr, hy - 6 * s + math.sin(a) * 84 * s * rr
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(12, 17) * s:.1f}" fill="{rnd.choice(["#C8C4CC", "#A8A4AE", "#DAD6DE"])}"/>')
    face = blob_pts(cx, hy + 6 * s, 66 * s, 76 * s, seed + 4, 0.03, 22)
    fd = smooth_closed(face)
    out.append(painted(D, face, ("#F8D2B4", "#E6AC86", "#A06A44"), seed + 4, sdir=(0.6, 0.7), sk=0.12, angle=-80, n=14, inkw=1.6, inkc="#7A4A30", hi=0.35))
    out.append(clipped(D, fd, [f'<path d="{blob(cx - 36 * s, hy + 28 * s, 15 * s, 10 * s, seed + 5, 0.2, 8)}" fill="#F27A6A" opacity="0.45"/>',
                               f'<path d="{blob(cx + 36 * s, hy + 28 * s, 15 * s, 10 * s, seed + 6, 0.2, 8)}" fill="#F27A6A" opacity="0.45"/>']))
    # perm curls over the forehead
    for k in range(9):
        x = cx - 64 * s + k * 16 * s
        y = hy - 62 * s + abs(k - 4) * 4 * s
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{14 * s:.1f}" fill="{rnd.choice(["#C8C4CC", "#B8B4BE", "#DAD6DE"])}"/>')
        out.append(f'<path d="M {x - 6 * s:.1f} {y:.1f} a {6 * s:.1f} {6 * s:.1f} 0 1 1 {6 * s:.1f} {6 * s:.1f}" stroke="#8A8692" stroke-width="1.4" fill="none"/>')
    # smiling eyes, crow's feet, round glasses, gentle laugh lines, smile
    for sg in (-1, 1):
        ex, ey = cx + sg * 26 * s, hy + 4 * s
        out.append(taper([(ex - 11 * s, ey + 1 * s), (ex, ey - 5 * s), (ex + 11 * s, ey + 1 * s)], 3.4 * s, 3.4 * s, "#3A2014", 0.95))
        for j in range(2):
            out.append(pline([(ex + sg * 14 * s, ey - 2 * s + j * 5 * s), (ex + sg * 20 * s, ey - 4 * s + j * 7 * s)], "#A06A44", 1.2, seed + j, 0.6, 1))
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{18 * s:.1f}" fill="#FFFFFF" fill-opacity="0.12" stroke="#7A5A3A" stroke-width="{2.4 * s:.1f}"/>')
        out.append(taper([(ex - sg * 0 - 8 * s, ey - 12 * s), (ex - 2 * s, ey - 15 * s)], 2.2 * s, 1, "#FFFFFF", 0.7))
    out.append(pline([(cx - 8 * s, hy + 4 * s), (cx + 8 * s, hy + 4 * s)], "#7A5A3A", 2.2 * s, seed, 0.9, 1))
    out.append(pline([(cx - 2 * s, hy + 16 * s), (cx - 6 * s, hy + 32 * s), (cx + 4 * s, hy + 34 * s)], "#B87A54", 1.6, seed, 0.75, 1))
    for sg in (-1, 1):
        out.append(pline([(cx + sg * 26 * s, hy + 38 * s), (cx + sg * 32 * s, hy + 54 * s)], "#B87A54", 1.4, seed + sg, 0.55, 1))
    mouth = [(cx - 20 * s, hy + 46 * s), (cx, hy + 50 * s), (cx + 20 * s, hy + 46 * s), (cx + 12 * s, hy + 58 * s), (cx, hy + 61 * s), (cx - 12 * s, hy + 58 * s)]
    out.append(f'<path d="{smooth_closed(mouth)}" fill="#A83A3A"/>')
    out.append(f'<path d="{pd([(cx - 14 * s, hy + 48 * s), (cx + 14 * s, hy + 48 * s), (cx + 12 * s, hy + 52 * s), (cx - 12 * s, hy + 52 * s)])}" fill="#FFFFFF"/>')
    return "".join(out)


@design("halmeoni")
def halmeoni():
    D = Doc2("kr-hm")
    out = [hanji(D, "#F6E6CC", FLECK, 851, fibres=60)]
    out.append(blooms(852, ["#F2C8A0", "#E8B890", "#F8DCC0"], 7, (0, 200, 600, 600), (100, 190), (0.12, 0.2)))
    # strings of drying persimmons (gotgam) hanging at both sides
    for sx in (66, 534):
        out.append(pline([(sx, 190), (sx + 2, 480)], "#8A6A3A", 1.6, sx, 0.9, 1))
        for k in range(6):
            y = 214 + k * 46
            sg = 1 if k % 2 else -1
            pts = blob_pts(sx + sg * 6, y, 19, 15, 853 + k + sx, 0.14, 14, sg * 12)
            out.append(painted(D, pts, ("#F2A85A", "#D2742A", "#7A3A0E"), 853 + k + sx, sk=0.25, angle=-80, n=6, inkw=1.2, hi=0.4))
            for j in range(3):
                out.append(pline([(sx + sg * 6 - 10 + j * 8, y - 8), (sx + sg * 6 - 8 + j * 8, y + 8)], "#9A4A14", 1.1, 870 + k + j, 0.5, 1))
            out.append(f'<path d="{blob(sx + sg * 2, y - 4, 10, 6, 880 + k, 0.3, 8)}" fill="#FFF4E0" opacity="0.35"/>')
            out.append(taper([(sx, y - 14), (sx + sg * 4, y - 18)], 4, 3, "#5A4A1A"))
    out.append(halmeoni_bust(D, 300, 330, 1.0, 880))
    # her hands holding out a bowl of rice heaped impossibly high
    bcx, bry = 300, 488
    out.append(cast(D, bcx + 10, 552, 110, 12, strength=0.4, seed=881))
    body = [(bcx + 96, bry), (bcx + 84, bry + 40), (bcx + 50, bry + 62), (bcx - 50, bry + 62), (bcx - 84, bry + 40), (bcx - 96, bry)]
    body += ell_pts(bcx, bry, 96, 22, 180, 360, 20)[1:-1]
    out.append(painted(D, body, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 882, sdir=(0.9, 0.3), sk=0.18, angle=-80, n=14, inkw=1.6, hi=0.5))
    out.append(clipped(D, smooth_closed(body), [f'<path d="M {bcx - 100} {bry + 26} Q {bcx} {bry + 40} {bcx + 100} {bry + 26}" stroke="#2E5AA8" stroke-width="4" fill="none"/>']))
    mound = [(bcx - 90, bry + 2), (bcx - 84, bry - 36), (bcx - 60, bry - 72), (bcx - 20, bry - 92), (bcx + 20, bry - 92), (bcx + 60, bry - 72), (bcx + 84, bry - 36), (bcx + 90, bry + 2)]
    md = smooth_closed(mound)
    out.append(f'<path d="{md}" fill="#FBF8F0"/>')
    rnd = random.Random(883)
    grains = [shade_over(D, md, "#8A8AA0", 0.35, 0, 0, 1, 1, 0.4)]
    for _ in range(320):
        x, y = rnd.uniform(bcx - 90, bcx + 90), rnd.uniform(bry - 94, bry)
        grains.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3, 3.8):.1f}" ry="1.7" fill="#FFFFFF" stroke="#D8D2C6" stroke-width="0.6" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    out.append(clipped(D, md, grains))
    out.append(ink(md, "#A8A090", 1.3, 884, 1, 0.6))
    for sg in (-1, 1):
        hand = blob_pts(bcx + sg * 96, bry + 30, 22, 16, 886 + sg, 0.1, 12)
        out.append(painted(D, hand, ("#F2C8A4", "#D8A07A", "#8A5A3A"), 886 + sg, sk=0.2, n=4, inkw=1.4, inkc="#7A4A30", hi=0.35))
    # lettering: 할머니 painted, the romanization, her famous line
    out.append(hangul(D, 300, 56, 84, "할머니", "#8A2A14", 890, paper_c="#F6E6CC", shadow="#F2D0B0"))
    out.append(ruled(300, 176, "HALMEONI · EAT MORE, YOU LOOK THIN!", "#2E4AA8", font=JOS, size=16, ls=3, line_w=14, gap=8, max_w=440))
    return finish_b(D, out, 891)


# ================================================================ 28. jeong — apple bunnies on a mother-of-pearl tray
def apple_bunny(D, cx, cy, s, seed, flip=False):
    """An apple wedge cut 'rabbit style', seen from the side: a cream wedge whose curved back keeps its red peel;
    at the front the peel is cut in a V and lifted into two ears; a sesame-seed eye. (cx, cy) = base centre."""
    def P(pts):
        return L(pts, cx, cy, s, flip)
    out = [cast(D, cx + 6, cy + 2, 58 * s, 7 * s, strength=0.4, seed=seed)]
    body = P([(-54, 0), (-50, -16), (-34, -34), (-8, -44), (20, -40), (42, -26), (54, -8), (52, 0)])
    out.append(painted(D, body, ("#FFFBE0", "#F6EAB8", "#C8B070"), seed, sdir=(0.5, 0.8), sk=0.18, angle=0, n=8, inkw=1.4, inkc="#A8904A", hi=0.4))
    peel = P([(-52, -10), (-50, -16), (-34, -34), (-8, -44), (20, -40), (42, -26), (50, -14), (40, -14), (20, -27), (-6, -31), (-30, -24), (-46, -8)])
    out.append(painted(D, peel, ("#F07A6A", "#C8202A", "#6A0A10"), seed + 1, sdir=(0.5, 0.8), sk=0.2, angle=0, n=8, inkw=1.2, hi=0.5))
    # the V where the ears were cut free
    out.append(f'<path d="{smooth_closed(P([(8, -40), (34, -31), (22, -22)]))}" fill="#FFF6D0"/>')
    for k, (bx, tip) in enumerate(((10, (-4, -66)), (24, (10, -68)))):
        ear = P([(bx - 6, -36), (tip[0] - 7, tip[1] + 8), (tip[0], tip[1]), (tip[0] + 7, tip[1] + 6), (bx + 8, -32)])
        out.append(painted(D, ear, ("#F07A6A", "#C8202A", "#6A0A10"), seed + 2 + k, sk=0.2, n=4, inkw=1.2, hi=0.5))
        out.append(pline(P([(bx + 1, -38), (tip[0] + 1, tip[1] + 6)]), "#FFE2D0", 1.4, seed + k, 0.7, 1))
    ex, ey = P([(38, -10)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{2.4 * s:.1f}" ry="{3.2 * s:.1f}" fill="#2A1A10"/>')
    out.append(pline(P([(-44, -4), (0, -10), (40, -4)]), "#E8D28A", 1.2, seed, 0.6, 1))
    return "".join(out)


def najeon_tray(D, cx, cy, rx, ry, seed):
    """Black lacquer tray inlaid with mother-of-pearl (najeon): iridescent petals and vines on glossy black."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 14, cy + 22, rx * 1.02, ry * 0.9, strength=0.55, seed=seed)]
    out.append(f'<path d="{ellipse_d(cx, cy + 14, rx, ry)}" fill="#0A0808"/>')
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 40)[:-1], ("#3A3436", "#141012", "#000000"), seed, sdir=(0.3, 1), sk=0.08, angle=0, n=20, inkw=1.6, inkc="#000", hi=0.25))
    top = ellipse_d(cx, cy, rx * 0.92, ry * 0.88)
    inl = [f'<path d="{top}" fill="#1A1416"/>']
    nacre = ["#E8F4F0", "#C8E0F8", "#F8E0F0", "#E0F8E0", "#FFF4D8"]
    # a vine of inlaid flowers around the rim
    for k in range(18):
        a = 2 * math.pi * k / 18
        x, y = cx + math.cos(a) * rx * 0.8, cy + math.sin(a) * ry * 0.76
        for j in range(5):
            b = math.radians(j * 72 + k * 9)
            inl.append(f'<path d="{blob(x + math.cos(b) * 6, y + math.sin(b) * 4, 5, 3, seed + k * 7 + j, 0.2, 8, math.degrees(b))}" fill="{rnd.choice(nacre)}" opacity="0.9"/>')
        a2 = a + math.pi / 18
        inl.append(pline([(x, y), (cx + math.cos(a2) * rx * 0.86, cy + math.sin(a2) * ry * 0.82)], "#C8D8E8", 1.2, seed + k, 0.6, 1))
    inl.append(f'<path d="{blob(cx - rx * 0.4, cy - ry * 0.45, rx * 0.4, ry * 0.12, seed + 1, 0.2, 12, -6)}" fill="#FFFFFF" opacity="0.12"/>')
    out.append(clipped(D, top, inl))
    out.append(taper(ell_pts(cx, cy, rx * 0.99, ry * 0.98, 170, 330, 24), 4, 3, "#8A8088", 0.6))
    return "".join(out)


@design("jeong")
def jeong():
    D = Doc2("kr-jg")
    out = [hanji(D, "#F4E2C8", FLECK, 901, fibres=60)]
    out.append(blooms(902, ["#F2C8A8", "#E8D0B0", "#F8DCC8"], 7, (0, 0, 600, 600), (100, 190), (0.1, 0.18)))
    out.append(soft_glow(D, 300, 420, 280, "#FFF2D8", 0.5))
    # the tray, a white plate, three apple bunnies and a pear slice, two little fruit forks
    out.append('<g transform="translate(300 450) scale(0.92) translate(-300 -460)">')
    out.append(najeon_tray(D, 300, 452, 264, 118, 903))
    out.append(cast(D, 312, 460, 190, 62, strength=0.4, seed=904))
    out.append(f'<path d="{ellipse_d(300, 458, 194, 70)}" fill="#C8C0B4"/>')
    out.append(painted(D, ell_pts(300, 450, 194, 70, 0, 360, 36)[:-1], WHITE, 905, sdir=(0.3, 1), sk=0.06, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(ink(ellipse_d(300, 452, 172, 58), "#2E5AA8", 2, 906, 1, 0.8))
    pear = [(190, 486), (214, 470), (262, 466), (290, 478), (262, 492), (214, 494)]
    out.append(painted(D, pear, ("#FFFFF0", "#F6F0D0", "#C8B880"), 907, sk=0.15, n=4, inkw=1.2, inkc="#A89A5A", hi=0.4))
    out.append(taper([(194, 490), (240, 496), (288, 482)], 4, 3, "#D8B85A", 0.9))
    for k, (x, y, fl) in enumerate(((236, 446, False), (338, 440, True), (330, 494, False))):
        out.append(apple_bunny(D, x, y, 1.1, 908 + k, flip=fl))
    for k, (x0, y0, x1, y1) in enumerate(((448, 500, 530, 540), (456, 484, 542, 520))):
        out.append(taper([(x0, y0), (x1, y1)], 3.4, 5, "#B8BCC8"))
        out.append(taper([(x0 - 2, y0 - 1), (x0 - 18, y0 - 8)], 1.8, 1.4, "#B8BCC8"))
        out.append(taper([(x0, y0 + 2), (x0 - 16, y0 - 3)], 1.8, 1.4, "#B8BCC8"))
        out.append(f'<path d="{blob(x1, y1, 6, 4, 920 + k, 0.1, 8, 30)}" fill="#F2E8F0" stroke="#8A8A9A" stroke-width="1"/>')
    out.append('</g>')
    # lettering: 정 painted large, its romanization and meaning
    out.append(hangul(D, 300, 52, 150, "정", "#A8201A", 910, w=17, paper_c="#F4E2C8", shadow="#ECC8B0"))
    out.append(ruled(300, 244, "JEONG", "#2E4AA8", font=JOS, size=22, ls=10, line_w=40, gap=14))
    out.append(label(300, 280, "THE LOVE YOU CAN'T QUITE TRANSLATE", JOS, 17, "#7A3A1E", ls=3, max_w=440))
    return finish_b(D, out, 911)


# ================================================================ 29. mugunghwa — the national flower, a field-guide plate
def mugung_flower(D, cx, cy, r, seed, rot_=0, pal=("#FCEAF2", "#F2B8D2", "#C86A98"), heart="#C81E5A"):
    """Rose of Sharon: five broad, overlapping crinkled petals, a deep red-violet heart (dansim) with rays,
    and a white column of stamens."""
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = math.radians(rot_ + i * 72)
        pts = []
        for j in range(15):
            t = math.radians(-46 + 92 * j / 14)
            rr = r * (0.98 + 0.05 * math.sin(j * 2.1 + i))
            pts.append((cx + math.cos(a + t * 0.62) * rr * (0.55 + 0.45 * math.cos(t * 1.2)), cy + math.sin(a + t * 0.62) * rr * (0.55 + 0.45 * math.cos(t * 1.2))))
        pts = [(cx, cy)] + pts
        out.append(painted(D, pts, pal, seed + i, sdir=(0.5, 0.8), sk=0.12, angle=math.degrees(a), n=10, slen=(r * 0.2, r * 0.6), inkw=1.1, inkc="#B05A86", inkop=0.5, hi=0.4))
        pd_ = smooth_closed(pts)
        # crimson heart at the petal base with radiating streaks
        ins = [f'<path d="{blob(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.2, r * 0.26, r * 0.2, seed + i + 9, 0.2, 10, math.degrees(a))}" fill="{heart}"/>']
        for k in range(6):
            b = a + math.radians(-22 + k * 9)
            ins.append(taper([(cx + math.cos(b) * r * 0.2, cy + math.sin(b) * r * 0.2), (cx + math.cos(b) * r * 0.62, cy + math.sin(b) * r * 0.62)], 2.2, 0.5, heart, 0.75))
        for k in range(4):
            b = a + math.radians(-30 + k * 20)
            ins.append(pline([(cx + math.cos(b) * r * 0.5, cy + math.sin(b) * r * 0.5), (cx + math.cos(b) * r * 0.92, cy + math.sin(b) * r * 0.92)], "#E89AC0", 1, seed + k, 0.6, 1))
        out.append(clipped(D, pd_, ins))
    # stamen column
    out.append(taper([(cx, cy), (cx + r * 0.08, cy - r * 0.42)], r * 0.1, r * 0.07, "#FFF6F8"))
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        x, y = cx + r * 0.05 + math.cos(a) * r * 0.06, cy - r * rnd.uniform(0.2, 0.42)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.2, r * 0.03):.1f}" fill="#FFF2C8" stroke="#E8C870" stroke-width="0.6"/>')
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 20)
        out.append(f'<circle cx="{cx + r * 0.08 + math.cos(a) * r * 0.08:.1f}" cy="{cy - r * 0.46 + math.sin(a) * r * 0.05:.1f}" r="{max(1.4, r * 0.035):.1f}" fill="#F6E070"/>')
    return "".join(out)


def mugung_leaf(D, x, y, s, ang, seed):
    """Three-lobed, toothed hibiscus leaf."""
    pts = []
    loc = [(0, 0), (-0.22, -0.2), (-0.42, -0.34), (-0.3, -0.44), (-0.2, -0.62), (-0.12, -0.78), (0, -1.0), (0.12, -0.78), (0.2, -0.62), (0.3, -0.44), (0.42, -0.34), (0.22, -0.2)]
    for i, (px, py) in enumerate(loc):
        pts.append((x + (px * s) * math.cos(math.radians(ang)) - (py * s) * math.sin(math.radians(ang)), y + (px * s) * math.sin(math.radians(ang)) + (py * s) * math.cos(math.radians(ang))))
    teeth = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        teeth += [a, ((a[0] + b[0]) / 2 + (b[1] - a[1]) * 0.08, (a[1] + b[1]) / 2 - (b[0] - a[0]) * 0.08)]
    out = [painted(D, teeth, ("#8ABE5A", "#3E7A2E", "#1A4A14"), seed, sdir=(0.5, 0.8), sk=0.15, angle=ang - 90, n=10, inkw=1.2, inkop=0.6, hi=0.35)]
    tip = rot([(x, y - s * 0.95)], x, y, ang)[0]
    out.append(pline([(x, y), tip], "#C8E8A0", 1.4, seed, 0.7, 1))
    for sg in (-1, 1):
        e = rot([(x + sg * s * 0.36, y - s * 0.36)], x, y, ang)[0]
        out.append(pline([(x, y), e], "#C8E8A0", 1.1, seed + sg, 0.6, 1))
    return "".join(out)


@design("mugunghwa")
def mugunghwa():
    D = Doc2("kr-mg")
    out = [paper(D.nid(), "#F2EAD8", FLECK, 921)]
    out.append(blooms(922, ["#E8C8D8", "#D8E0C0", "#F0D8E0"], 6, (100, 120, 500, 460), (110, 180), (0.12, 0.2)))
    out.append(f'<rect x="50" y="50" width="500" height="500" fill="none" stroke="#1E3A6E" stroke-width="2.2"/>')
    out.append(f'<rect x="58" y="58" width="484" height="484" fill="none" stroke="#1E3A6E" stroke-width="1.2" opacity="0.7"/>')
    for x, y in ((50, 50), (550, 50), (50, 550), (550, 550)):
        out.append(f'<path d="{blob(x, y, 7, 7, x + y, 0.1, 8)}" fill="#C81E5A"/>')
    out.append(ruled(300, 92, "FLOWERS OF KOREA · Nº 1", "#1E3A6E", font=MONO, size=16, ls=4, line_w=26, gap=10))
    # the branch
    stem = catmull([(110, 470), (190, 420), (290, 380), (390, 330), (470, 270), (500, 200)], 6)
    out.append(branch(D, stem, 9, 4, 923, pal=("#9A8A5A", "#6A5A34", "#3A3018")))
    out.append(branch(D, catmull([(290, 380), (250, 320), (236, 250)], 5), 6, 3, 924, pal=("#9A8A5A", "#6A5A34", "#3A3018")))
    for k, (x, y, s, a) in enumerate(((150, 452, 66, -130), (330, 372, 70, 160), (420, 318, 62, -40), (260, 330, 56, -110), (480, 236, 58, 40), (210, 410, 50, 140))):
        out.append(mugung_leaf(D, x, y, s, a, 925 + k))
    # flowers: one open full-face, one turned, one white-petalled variety, buds
    out.append(mugung_flower(D, 236, 246, 70, 931, rot_=-10))
    out.append(mugung_flower(D, 392, 300, 62, 932, rot_=20, pal=("#FFFFFF", "#F6F0F2", "#C8B8C0")))
    out.append(mugung_flower(D, 160, 400, 46, 933, rot_=40))
    for k, (x, y, a) in enumerate(((488, 192, 20), (470, 270, 60), (300, 372, 100))):
        bud = rot([(x, y + 14), (x - 10, y), (x - 6, y - 16), (x, y - 24), (x + 6, y - 16), (x + 10, y)], x, y, a)
        out.append(painted(D, bud, ("#C8E0A0", "#7AA84A", "#3A5A1E"), 934 + k, sk=0.2, n=4, inkw=1.2, hi=0.4))
        tip = rot([(x - 4, y - 14), (x, y - 26), (x + 4, y - 14)], x, y, a)
        out.append(painted(D, tip, ("#FCEAF2", "#F2B8D2", "#C86A98"), 937 + k, sk=0.2, n=3, inkw=1, hi=0.4))
    # the house bee visiting
    out.append(f'<g transform="translate(470 404) rotate(-14)">'
               f'<ellipse cx="0" cy="0" rx="16" ry="11" fill="#F2A81D" stroke="#2B2118" stroke-width="2"/>'
               f'<path d="M -4 -10 L -4 10 M 6 -10 L 6 10" stroke="#2B2118" stroke-width="4"/>'
               f'<circle cx="-18" cy="0" r="7" fill="#2B2118"/>'
               f'<ellipse cx="-2" cy="-16" rx="7" ry="11" fill="#FFFFFF" stroke="#2B2118" stroke-width="1.6" opacity="0.9" transform="rotate(-20 -2 -16)"/>'
               f'<ellipse cx="8" cy="-15" rx="6" ry="10" fill="#FFFFFF" stroke="#2B2118" stroke-width="1.6" opacity="0.9" transform="rotate(20 8 -15)"/></g>')
    out.append(pline([(440, 412), (420, 420), (400, 412), (384, 418)], "#2B2118", 1.2, 940, 0.4, 1))
    # caption
    out.append(letters(D, 300, 500, "Mugunghwa", SERIF_IT, 62, "#1E3A6E", ["#2E4A8A", "#122A54"], 941, max_w=320, angle=-40, wob=0.6))
    out.append(label(300, 530, "HIBISCUS SYRIACUS", MONO, 16, "#C81E5A", ls=5))
    return finish_b(D, out, 942)


# ================================================================ 30. boseong — green tea hills in May
def tea_rows(D, seed, y_top, y_bot, x0=-30, x1=630, rows=12, pal=("#B8E07A", "#5EA84A", "#2E6A2E"), bend=40, phase=0.0, haze=0.0):
    """Contour-planted tea: rounded hedge rows curving over a hill, each lit on top with a dark furrow below."""
    hz = (lambda c: mix(c, "#D8E8D0", haze)) if haze else (lambda c: c)
    rnd = random.Random(seed)
    out = []
    for i in range(rows):
        t = i / (rows - 1)
        y = y_top + (y_bot - y_top) * t ** 1.25
        h = 8 + 26 * t ** 1.3
        line = [(x0 + (x1 - x0) * u, y - bend * math.sin(math.pi * u + phase) * (1 - 0.5 * t)) for u in [k / 30 for k in range(31)]]
        top = [(x, yy - h * 0.55) for x, yy in line]
        bot = [(x, yy + h * 0.45) for x, yy in line]
        poly = top + bot[::-1]
        d = smooth_closed(poly)
        out.append(f'<path d="{d}" fill="{hz(pal[1])}"/>')
        inner = [taper(top, h * 0.5, h * 0.5, hz(pal[0]), 0.7), taper(bot, h * 0.4, h * 0.4, hz(pal[2]), 0.6)]
        for _ in range(int(14 + 30 * t)):
            u = rnd.uniform(0, 1)
            x = x0 + (x1 - x0) * u
            yy = y - bend * math.sin(math.pi * u + phase) * (1 - 0.5 * t)
            inner.append(f'<path d="{blob(x, yy - h * 0.15, h * 0.35, h * 0.2, rnd.randint(0, 999), 0.3, 8)}" fill="{hz(rnd.choice([pal[0], "#D8F0A0", pal[1]]))}" opacity="0.7"/>')
        out.append(clipped(D, d, inner))
        out.append(ink(smooth_open(top), hz("#2E5A22"), 1.0 + t, seed + i, 1, 0.3))
    return "".join(out)


@design("boseong")
def boseong():
    D = Doc2("kr-bs")
    out = [sky(D, [(0, "#8AC0E8"), (0.6, "#D8ECF4"), (1, "#F6F8EC")], 951, 600, ["#A8D0EE", "#FFFFFF"], 60, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 470, 228, 120, 952, pal=("#FFFFFF", "#F4F8FF", "#B8C8E0")))
    # far hills in mist
    fh = ridge([(-20, 300), (120, 262), (260, 284), (400, 246), (620, 280)], 953, 8, 4)
    out.append(hill(D, fh, 380, ("#C8DCD0", "#9ABCA8", "#6A8A7A"), 954, inkw=0.8, inkop=0.25))
    out.append(f'<rect y="240" width="600" height="120" fill="{D.lin([(0, "#FFFFFF", 0), (0.7, "#FFFFFF", 0.6), (1, "#FFFFFF", 0)])}"/>')
    # tea terraces on the far slope (hazy), then the near hill
    hill_far = [(-20, 330), (160, 316), (320, 330), (480, 300), (620, 312)]
    out.append(hill(D, catmull(hill_far, 6), 460, ("#C8E6A0", "#88BE6A", "#4E8A44"), 955, inkw=0, n=10))
    out.append(tea_rows(D, 956, 330, 430, rows=8, bend=18, phase=0.3, haze=0.35))
    # a line of tall cedars along the path
    for k, x in enumerate((448, 472, 498, 524, 552, 580)):
        out.append(f'<path d="{blob(x, 330 - k * 3, 9, 46, 960 + k, 0.08, 12)}" fill="#2E5A3A"/>')
        out.append(f'<path d="{blob(x - 3, 326 - k * 3, 4, 36, 966 + k, 0.1, 10)}" fill="#5A8A5A" opacity="0.7"/>')
        out.append(f'<rect x="{x - 1.5}" y="{372 - k * 3}" width="3" height="12" fill="#4A3020"/>')
    # the near hill: bold rows sweeping across
    out.append(f'<path d="M -20 420 L 620 420 L 620 620 L -20 620 Z" fill="#2E6A2E"/>')
    out.append(tea_rows(D, 970, 420, 600, rows=9, bend=56, phase=0.0))
    # a tea picker in a sun hat with a basket, between the rows
    out.append(figures.person(214, 470, 70, "stand_34", 1, {"top": "#F2E6D0", "top_kind": "long", "bottom": "#5A6A8A", "hat_kind": "sunhat", "hat": "#E8D8A8", "form": "f"}, seed=980, light=-1))
    out.append(painted(D, [(232, 438), (256, 438), (252, 456), (236, 456)], ("#E8C888", "#B8904A", "#6A4A1A"), 981, sk=0.2, n=3, inkw=1.2, hi=0.3))
    out.append(dab_crown(D, 214, 486, 50, 12, [("#B8E07A", "#5EA84A", "#2E6A2E")], 982, n=40, size=(4, 7), inkw=0, base=False))
    # a cup of green tea in the corner, steaming
    out.append(cast(D, 512, 560, 46, 7, strength=0.45, seed=983))
    cup = [(470, 496), (548, 496), (538, 552), (480, 552)]
    out.append(painted(D, cup, CELADON, 984, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.45))
    out.append(f'<path d="{ellipse_d(509, 496, 39, 8)}" fill="#A8C870"/><path d="{ellipse_d(509, 496, 39, 8)}" fill="none" stroke="#5E8A74" stroke-width="1.6"/>')
    out.append(steam(509, 488, 50, 985, "#FFFFFF", 2, 18, 5, 0.6))
    # lettering
    out.append(letters(D, 300, 126, "Boseong", SERIF_IT, 124, "#24563A", ["#2E6A44", "#163A26", "#4A8A5A"], 986, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8D8B0"))
    out.append(ruled(300, 170, "GREEN TEA HILLS IN MAY", "#7A4A1E", font=JOS, size=19, ls=5, line_w=24, gap=12))
    return finish_b(D, out, 987)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        # the folder holds exactly this set: clear out artwork for slugs that were dropped
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
