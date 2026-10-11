"""Fairy Tales & Myths, hand-painted (gouache / golden-age storybook) edition: 30 magnets.

Public-domain stories everyone grew up with (Grimm, Andersen, Perrault, Aesop, the Thousand and One Nights,
Greek and Norse myth, Arthurian and English legend), each painted as an ORIGINAL storybook plate in the mood
of the golden-age illustrators (Rackham's gnarled woods and sepia, Dulac's jewel-blue nights and gold,
Nielsen's tall elegant shapes, Bilibin's ornamental folk borders). Every scene is built from details in the
original tales (the hazel tree, the ebony window, the twenty mattresses, the walnut-shell cradle, "Open,
Sesame!"), never from any film adaptation.

Painted in the house gouache idiom (warm paper, layered washes with pooled edges, brush strokes following the
form, a warm brown pen line, soft light, grain on top). Colour story: midnight blue and teal, burnished gold,
madder red, moss green and cream vellum.

Run from tools/designs:  python3 fairy_tales_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (apple, blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps, mist, ribbon, leaf)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
from paint import conifer
import holidays_gouache as hg
from storybook_classics_painted import (T, ell_pts, pd, shade_over, light_over, tx, gilt, gilt_fill, cloth_bg, rule_frame,
                                        fleuron, flourish, laurel, candle, star4, stars_field, rose_bloom, leaf_simple,
                                        bird_v, cypress_tree)

COL = "fairy-tales"
INK = "#3A2418"
FLECK = "#8A6A4A"

lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
GOLD = ("#FBE7A4", "#D9A945", "#8A6020")
BRASS = ("#F8E08E", "#C8963A", "#6E4A14")
EBONY = ("#5E4E5A", "#1E1418", "#060306")
MADDER = ("#E8786A", "#B02A2A", "#5E0E12")
MOSS = ("#9CBB78", "#4E7A3E", "#20401E")
LEAF = ("#9CCB7A", "#4E8A3E", "#22502A")
TEAL = ("#6AB0B0", "#1E6A72", "#0C343C")
NIGHT = ("#4A5E9A", "#1C2A5A", "#0A1230")
CREAM = ("#FFFDF4", "#F2E8D2", "#C4B190")
VELLUM = "#F3E9D2"
STONE = ("#D8D2C4", "#A09888", "#585046")
WOOD = ("#C8925E", "#8E5A30", "#4E2E14")
DARKWOOD = ("#8A5A3A", "#4E2E1A", "#24140A")
FUR = ("#E2C49A", "#A87C50", "#5A3C22")
ROSE = ("#F69A9A", "#D2384A", "#7E1426")
PINK = ("#FFD2DC", "#F2A0B4", "#B8607A")
SNOW = ("#FFFFFF", "#E8EEF6", "#9AA8C0")
CREAMWALL = ("#FBF3E2", "#EADBB8", "#A8946A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Doc2(Doc):
    """fall_painted.Doc plus the Pn interface (id / lg / rg / glow) so holidays_gouache helpers work with it."""

    def id(self, p="g"):
        return self.nid()

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        return self.lin(stops, x1, y1, x2, y2, units)[5:-1]

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        return self.rad(stops, cx, cy, r, fx, fy)[5:-1]

    def glow(self, x, y, r, col, s=0.7, ry=None):
        g = self.rad([(0, col, s), (0.35, col, s * 0.5), (1, col, 0)])
        if ry:
            return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{g}"/>'


def finish_b(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


# ================================================================ toolkit
def txs(x, y, s, font, size, fill, ls=0, max_w=460, anchor="start", op=None):
    """Fitted text with a non-centred anchor."""
    return tx(x, y, s, font, size, fill, ls, max_w, anchor, op=op)


def multi(x, y, parts, font, size, max_w=460, ls=0, anchor="middle", shadow=None, sdy=2.0):
    """One line built from coloured parts [(text, fill), ...], fitted as a whole."""
    s = "".join(p for p, _ in parts)
    fs = fit_size(s, font, size, max_w, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    spans = "".join(f'<tspan fill="{c}">{esc(p)}</tspan>' for p, c in parts)
    out = []
    if shadow:
        out.append(f'<text x="{x + 1:.1f}" y="{y + sdy:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{shadow}" opacity="0.55">{esc(s)}</text>')
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa}>{spans}</text>')
    return "".join(out)


def arch_pts(x0, x1, spring, bottom, step=10, kind="round", point=0.0):
    """Window/door outline: straight jambs up to the springline, then a round (or pointed) arch."""
    r = (x1 - x0) / 2
    cx = (x0 + x1) / 2
    pts = []
    n = max(2, int((bottom - spring) / step))
    for i in range(n):
        pts.append((x0, bottom - (bottom - spring) * i / n))
    m = 24
    for i in range(m + 1):
        a = math.pi + math.pi * i / m
        y = spring + r * math.sin(a)
        if kind == "pointed":
            t = i / m
            y -= point * r * (1 - abs(2 * t - 1)) ** 2
        pts.append((cx + r * math.cos(a), y))
    for i in range(1, n + 1):
        pts.append((x1, spring + (bottom - spring) * i / n))
    return pts


def ogee_pts(x0, x1, spring, apex, bottom, step=10):
    """Moorish ogee arch opening: jambs, swelling shoulders and a reversed-curve point at the apex."""
    cx = (x0 + x1) / 2
    w = (x1 - x0) / 2
    left = [(x0, bottom - (bottom - spring) * i / 12) for i in range(12)]
    curve = []
    for i in range(25):
        t = i / 24
        x = x0 + w * t
        # swell out then pull in to the point
        y = spring - (spring - apex) * (math.sin(t * math.pi * 0.62) ** 1.6 * 0.82 + 0.18 * t ** 6)
        curve.append((x, y))
    curve[-1] = (cx, apex)
    right_curve = [(2 * cx - x, y) for x, y in curve[::-1]][1:]
    right = [(x1, spring + (bottom - spring) * i / 12) for i in range(1, 13)]
    return left + curve + right_curve + right


def snowfall(seed, box, n, r=(0.8, 2.8), col="#FFFFFF", op=(0.55, 1.0)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        rr = rnd.uniform(*r)
        out.append(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rr:.1f}" fill="{col}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def gnarled_trunk(D, x, base, top, w, seed, pal=("#6A5A4A", "#3A2E24", "#140E0A"), lean=0.0, rim=None, roots=True, branches=2, rim_side=1):
    """Rackham-style old tree trunk: twisting, knotted, bark strokes, splayed roots and crooked branch stubs."""
    rnd = random.Random(seed)
    n = 9
    spine = []
    for i in range(n + 1):
        t = i / n
        spine.append((x + lean * (base - top) * t + math.sin(t * 5 + seed) * w * 0.25, base - (base - top) * t))
    left, right = [], []
    for i, (sx, sy) in enumerate(spine):
        t = i / n
        ww = w * (1.0 - 0.45 * t) * (1 + (0.9 if (roots and t < 0.08) else 0) * (1 - t / 0.08))
        ww *= rnd.uniform(0.9, 1.08)
        left.append((sx - ww / 2, sy))
        right.append((sx + ww / 2, sy))
    pts = left + right[::-1]
    out = [painted(D, pts, pal, seed, sdir=(-rim_side, 0.1), sk=0.22, angle=-90, n=int(w * (base - top) / 60) + 10,
                   slen=((base - top) * 0.06, (base - top) * 0.2), sw=(0.8, max(1.2, w * 0.06)), inkw=1.6, inkc="#100A06", hi=0.25)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    for k in range(int(w / 6) + 2):
        fx = rnd.uniform(-0.45, 0.45)
        line = [(sx + fx * w * (1 - 0.45 * i / n), sy) for i, (sx, sy) in enumerate(spine)]
        inner.append(pline(line, pal[2], rnd.uniform(1.2, 2.4), seed + k, 0.5, 1))
    for k in range(rnd.randint(1, 3)):
        i = rnd.randint(2, n - 2)
        kx, ky = spine[i]
        kx += rnd.uniform(-0.2, 0.2) * w
        inner.append(f'<path d="{blob(kx, ky, w * 0.14, w * 0.2, seed + 50 + k, 0.2, 10)}" fill="{pal[2]}" opacity="0.8"/>')
        inner.append(ink(blob(kx, ky, w * 0.2, w * 0.27, seed + 60 + k, 0.2, 10), pal[0], 1.4, seed, 1, 0.45))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if roots:
        for sg in (-1, 1):
            rx0 = x + sg * w * 0.5
            out.append(taper(catmull([(rx0 - sg * w * 0.2, base - w * 0.4), (rx0 + sg * w * 0.25, base - w * 0.08), (rx0 + sg * w * 0.7, base + 4)], 5), w * 0.4, 3, pal[1]))
    tips = []
    for k in range(branches):
        t = 0.62 + 0.3 * k / max(1, branches - 1) if branches > 1 else 0.75
        i = min(n, int(t * n))
        bx, by = spine[i]
        sg = 1 if (k + seed) % 2 else -1
        L = w * rnd.uniform(1.6, 2.6)
        p = [(bx, by + 6), (bx + sg * L * 0.4, by - L * 0.25), (bx + sg * L * 0.8, by - L * 0.3 + rnd.uniform(-10, 10)), (bx + sg * L, by - L * 0.6)]
        out.append(taper(catmull(p, 6), w * 0.32, 2.5, pal[1]))
        out.append(pline(p[1:], pal[2], 1.2, seed + k, 0.5, 1))
        tips.append(p[-1])
    if rim:
        out.append(taper([(sx + rim_side * (w * (1 - 0.45 * i / n)) * 0.46, sy) for i, (sx, sy) in enumerate(spine)][1:], 3, 1.2, rim, 0.6))
    return "".join(out)


def bare_tree(x, base, h, seed, col, w=6, spread=34, depth=5, out=None, lean=0.0):
    """Leafless winter tree as tapered, forking branches (silhouette)."""
    own = out is None
    out = out if out is not None else []
    rnd = random.Random(seed)

    def br(px, py, ang, L, ww, d):
        ex, ey = px + math.cos(math.radians(ang)) * L, py + math.sin(math.radians(ang)) * L
        mx, my = (px + ex) / 2 + rnd.uniform(-L, L) * 0.08, (py + ey) / 2 + rnd.uniform(-L, L) * 0.08
        out.append(taper([(px, py), (mx, my), (ex, ey)], ww, ww * 0.6, col))
        if d > 0:
            for k in range(rnd.choice([2, 2, 3])):
                br(ex, ey, ang + rnd.uniform(-spread, spread), L * rnd.uniform(0.62, 0.8), ww * 0.62, d - 1)
    br(x, base, -90 + lean, h * 0.36, w, depth)
    return "".join(out) if own else ""


def tiny_cloak_figure(x, base, s, col, rim=None, hood=True, basket=False, facing=1, cloak_col=None):
    """A small cloaked storybook figure seen from behind/side, walking (Red Riding Hood, a pilgrim, a prince).
    s=1 ~ 60 px tall. Returns svg."""
    def L(pts):
        return T(pts, x, base, s, facing < 0)
    c = cloak_col or col
    out = []
    # legs and feet under the hem
    out.append(taper(L([(-4, -10), (-5, -2), (-7, 0)]), 3.2 * s, 2.6 * s, col))
    out.append(taper(L([(4, -10), (6, -3), (9, -1)]), 3.2 * s, 2.6 * s, col))
    # cloak: bell from the shoulders, hem swinging back
    cloak = L([(-3, -50), (-9, -46), (-14, -34), (-18, -20), (-22, -9), (-16, -8), (-8, -10), (2, -9), (12, -10), (16, -14), (13, -30), (9, -44), (4, -50)])
    out.append(f'<path d="{smooth_closed(cloak)}" fill="{c}"/>')
    # hood / head
    if hood:
        out.append(f'<path d="{smooth_closed(L([(-7, -48), (-8, -56), (-4, -62), (3, -63), (8, -58), (8, -50), (3, -46)]))}" fill="{c}"/>')
        out.append(f'<path d="{smooth_closed(L([(-7, -50), (-12, -48), (-8, -54)]))}" fill="{c}"/>')
    else:
        out.append(f'<path d="{blob(*L([(1, -56)])[0], 6 * s, 7 * s, 3, 0.06, 10)}" fill="{col}"/>')
    if basket:
        bx, by = L([(13, -26)])[0]
        out.append(f'<path d="{blob(bx, by, 7 * s, 4.5 * s, 4, 0.08, 10)}" fill="{col}"/>')
        out.append(ink(smooth_open(L([(7, -27), (11, -36), (17, -36), (19, -27)])), col, 1.6 * s, 2, 1, 1))
    if rim:
        out.append(ink(smooth_open(L([(4, -62), (8, -58), (9, -48), (13, -34), (16, -16)])), rim, 1.4, 3, 1, 0.75))
    return "".join(out)


def child_pair(x, base, s, col, rim=None):
    """Hansel and Gretel from behind, hand in hand: a girl in a skirt and kerchief, a boy in a cap and breeches."""
    out = []

    def L(pts, ox):
        return T(pts, ox, base, s)
    # Gretel (left)
    g = x - 12 * s
    out.append(taper(L([(-3, -14), (-3, 0)], g), 3.4 * s, 2.8 * s, col))
    out.append(taper(L([(3, -14), (4, 0)], g), 3.4 * s, 2.8 * s, col))
    out.append(f'<path d="{smooth_closed(L([(-5, -40), (-8, -30), (-13, -14), (-10, -12), (0, -11), (10, -12), (13, -14), (8, -30), (5, -40)], g))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(0, -46)], g)[0], 6 * s, 6.6 * s, 5, 0.05, 10)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-6, -48), (0, -54), (6, -48), (4, -44), (9, -40), (2, -42), (-4, -42)], g))}" fill="{col}"/>')  # kerchief knot
    out.append(taper(L([(-4, -36), (-10, -26), (-11, -18)], g), 2.8 * s, 2.2 * s, col))
    out.append(taper(L([(4, -36), (9, -28), (13, -24)], g), 2.8 * s, 2.2 * s, col))   # hand to Hansel
    # Hansel (right, a little taller)
    h = x + 12 * s
    out.append(taper(L([(-3, -18), (-3, 0)], h), 3.6 * s, 3.0 * s, col))
    out.append(taper(L([(3, -18), (4, 0)], h), 3.6 * s, 3.0 * s, col))
    out.append(f'<path d="{smooth_closed(L([(-6, -44), (-8, -30), (-7, -16), (7, -16), (8, -30), (6, -44)], h))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(0, -50)], h)[0], 6 * s, 6.6 * s, 6, 0.05, 10)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-7, -52), (-4, -58), (4, -58), (8, -52), (12, -51), (6, -50)], h))}" fill="{col}"/>')      # cap with a brim
    out.append(taper(L([(-5, -40), (-10, -32), (-13, -24)], h), 2.8 * s, 2.2 * s, col))
    out.append(taper(L([(5, -40), (9, -30), (10, -22)], h), 2.8 * s, 2.2 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(5, -40), (8, -30), (13, -14)], g)), rim, 1.2, 1, 1, 0.7))
        out.append(ink(smooth_open(L([(6, -50), (6, -44), (8, -30), (7, -18)], h)), rim, 1.2, 2, 1, 0.7))
    return "".join(out)


# ================================================================ 1. snow white — the ebony window, three drops on the snow
def embroidery_hoop(D, cx, cy, rx, ry, seed):
    out = [cast(D, cx + 8, cy + ry * 0.9, rx * 0.95, ry * 0.4, strength=0.35, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 30), ("#FFFFFF", "#F4EEE2", "#B8AE98"), seed, sdir=(0.4, 1), sk=0.12, angle=-10, n=20, inkw=0, hi=0.3))
    # linen weave
    cid = D.clip(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 30))}"/>')
    weave = []
    for k in range(-int(rx), int(rx), 4):
        weave.append(f'<path d="M {cx + k:.1f} {cy - ry:.1f} L {cx + k + ry * 0.2:.1f} {cy + ry:.1f}" stroke="#C8BCA4" stroke-width="0.6" opacity="0.5"/>')
    # half-stitched red rose and a green leaf in satin stitch
    rr = ry * 0.42
    for k in range(9):
        a = math.radians(k * 40 - 90)
        if k > 6:
            continue
        px, py = cx - rx * 0.12 + math.cos(a) * rr * 0.6, cy + math.sin(a) * rr * 0.45
        weave.append(f'<path d="{blob(px, py, rr * 0.45, rr * 0.3, seed + k, 0.1, 10, math.degrees(a))}" fill="#C0283A" opacity="0.92"/>')
        for j in range(4):
            weave.append(f'<path d="M {px - rr * 0.3 + j * rr * 0.18:.1f} {py - rr * 0.2:.1f} l {rr * 0.12:.1f} {rr * 0.4:.1f}" stroke="#7E1020" stroke-width="0.9" opacity="0.6"/>')
    weave.append(f'<path d="{blob(cx - rx * 0.12, cy, rr * 0.28, rr * 0.2, seed + 20, 0.1, 8)}" fill="#7E1020"/>')
    for j in range(2):
        lx = cx + rx * (0.25 + j * 0.2)
        weave.append(f'<path d="{blob(lx, cy + ry * 0.12 - j * 4, rr * 0.5, rr * 0.18, seed + 30 + j, 0.1, 10, -20 - j * 20)}" fill="#3E7A40"/>')
    out.append(f'<g {cid}>{"".join(weave)}</g>')
    # wooden hoop rings (back and front) with the brass screw
    for (w_, c, op) in ((7, WOOD[2], 0.9), (4.6, WOOD[1], 1), (1.8, WOOD[0], 0.9)):
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx + 2, ry + 1.5, 0, 360, 36))}" fill="none" stroke="{c}" stroke-width="{w_}" opacity="{op}"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx + 5.5, ry + 4.5, 0, 360, 36)), INK, 1.4, seed, 1, 0.6))
    out.append(painted(D, rect_pts(cx - 6, cy - ry - 14, cx + 6, cy - ry - 1, 4, seed, 0.3), BRASS, seed + 3, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.5))
    return "".join(out)


def needle_thread(D, x0, y0, x1, y1, thread_pts, seed, col="#C0283A"):
    out = [pline(thread_pts, dk(col, 0.3), 2.4, seed, 0.6, 1), pline(thread_pts, col, 1.8, seed + 1, 1, 1)]
    out.append(taper([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y1)], 2.8, 0.8, "#8A93A6"))
    out.append(taper([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y1)], 1.0, 0.4, "#FFFFFF", 0.9))
    out.append(f'<ellipse cx="{x0 + (x1 - x0) * 0.06:.1f}" cy="{y0 + (y1 - y0) * 0.06:.1f}" rx="1.6" ry="0.8" fill="#2A2A3A"/>')
    return "".join(out)


@design("snow-white")
def snow_white():
    D = Doc2("ft-sw")
    out = [paper(D.nid(), "#F2E8D4", FLECK, 31)]
    out.append(blooms(3, ["#C8B48A", "#E8D8B8"], 7, op=(0.04, 0.09)))
    out.append(rule_frame(D, 30, 30, 570, 570, "#7A1E26", 2.4, 8, 1.1, seed=3))
    # --- the ebony window
    x0, x1, spring, bot = 168, 432, 304, 414
    outer = arch_pts(x0 - 26, x1 + 26, spring, bot + 6, 12)
    inner = arch_pts(x0, x1, spring, bot, 12)
    cid = D.clip(f'<path d="{smooth_closed(inner)}"/>')
    sc = [f'<rect x="{x0}" y="100" width="{x1 - x0}" height="{bot - 100 + 10}" fill="{D.lin([(0, "#1C2850"), (0.55, "#4A5A8E"), (0.85, "#8A96C0"), (1, "#C4C8DE")])}"/>']
    sc.append(soft_glow(D, 352, 222, 70, "#E8ECFF", 0.35))
    sc.append(f'<path d="{blob(352, 222, 14, 14, 4, 0.02, 18)}" fill="#F8F4E6"/>')
    # far snowy hills, a castle on the hill, birches
    sc.append(f'<path d="{smooth_closed([(x0 - 10, 420), (x0 - 10, 318), (220, 300), (290, 314), (350, 296), (420, 306), (x1 + 10, 300), (x1 + 10, 420)])}" fill="#B4BEDA"/>')
    sc.append(pline([(x0, 318), (220, 300), (290, 314), (350, 296), (420, 306), (x1, 300)], "#FFFFFF", 1.6, 5, 0.6, 1))
    cx_ = 236
    for (tx_, tw, th, cone) in ((cx_ - 22, 12, 46, 1), (cx_, 18, 64, 1), (cx_ + 22, 12, 40, 1), (cx_ + 40, 30, 26, 0)):
        sc.append(f'<path d="{pd([(tx_ - tw / 2, 312), (tx_ - tw / 2, 312 - th), (tx_ + tw / 2, 312 - th), (tx_ + tw / 2, 312)])}" fill="#6A76A6"/>')
        if cone:
            sc.append(f'<path d="{pd([(tx_ - tw / 2 - 3, 312 - th + 1), (tx_, 312 - th - tw * 1.5), (tx_ + tw / 2 + 3, 312 - th + 1)])}" fill="#5A6496"/>')
            sc.append(f'<path d="{pd([(tx_ - 2, 312 - th - tw * 1.2), (tx_, 312 - th - tw * 1.5), (tx_ + tw / 2 + 3, 312 - th + 1), (tx_ + 2, 312 - th + 1)])}" fill="#FFFFFF" opacity="0.5"/>')
    for (wx, wy) in ((cx_ - 1, 270), (cx_ + 4, 282), (cx_ - 22, 290), (cx_ + 38, 300)):
        sc.append(f'<rect x="{wx}" y="{wy}" width="3" height="5" fill="#FFD27A"/>')
        sc.append(soft_glow(D, wx + 1.5, wy + 2.5, 9, "#FFD27A", 0.5))
    sc.append(f'<path d="{smooth_closed([(x0 - 10, 420), (x0 - 10, 352), (240, 338), (320, 350), (380, 336), (x1 + 10, 346), (x1 + 10, 420)])}" fill="#DCE2F0"/>')
    for k, bx in enumerate((190, 214, 404, 420)):
        sc.append(bare_tree(bx, 352 - (k % 2) * 6, 70 + k * 6, 40 + k, "#4A4A6A", 2.6, 30, 4))
    sc.append(snowfall(6, (x0, 120, x1, 410), 120, (0.8, 2.6)))
    sc.append(snowfall(7, (x0, 120, x1, 410), 30, (2.4, 3.6), op=(0.8, 1)))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # casement mullion and transom (ebony)
    out.append(painted(D, rect_pts(296, spring - 126, 304, bot, 12, 7, 0.3), EBONY, 7, sdir=(1, 0.2), sk=0.2, angle=-90, n=10, inkw=0.8, hi=0.4))
    out.append(painted(D, rect_pts(x0, spring - 4, x1, spring + 4, 14, 8, 0.3), EBONY, 8, sdir=(0.2, 1), sk=0.2, angle=0, n=10, inkw=0.8, hi=0.4))
    # carved ebony frame
    fd = smooth_closed(outer) + " " + smooth_closed(inner)
    out.append(f'<path d="{fd}" fill-rule="evenodd" fill="{EBONY[1]}"/>')
    fcid = D.clip(f'<path d="{fd}" clip-rule="evenodd"/>')
    fr = [strokes(D.nid(), fd, (x0 - 30, 90, x1 + 30, bot + 10), ["#3A2A34", "#0A0408", "#5A4652"], 9, n=140, angle=-90, length=(20, 60), width=(1, 3), opacity=(0.3, 0.6))]
    fr.append(ink(smooth_open(arch_pts(x0 - 13, x1 + 13, spring, bot + 6, 12)), "#6A5A68", 2.2, 10, 1, 0.65))
    fr.append(ink(smooth_open(arch_pts(x0 - 18, x1 + 18, spring, bot + 6, 12)), "#000000", 1.4, 11, 1, 0.6))
    out.append(f'<g {fcid}>{"".join(fr)}</g>')
    out.append(taper([(x0 - 20, 380), (x0 - 20, spring), (x0 + 10, spring - 90), (300, spring - 124 - 26)], 1.2, 3.6, "#B8A8C8", 0.6))
    out.append(ink(smooth_closed(outer), "#000000", 1.6, 12, 1, 0.8))
    # keystone
    out.append(painted(D, [(288, spring - 154), (312, spring - 154), (308, spring - 122), (292, spring - 122)], EBONY, 13, sk=0.2, angle=-90, n=6, inkw=1.2, hi=0.5))
    # sill with snow piled on it, and three drops of blood
    out.append(cast(D, 300, bot + 30, 230, 14, strength=0.35, seed=14))
    out.append(painted(D, rect_pts(118, bot, 482, bot + 22, 16, 14, 0.3), EBONY, 14, sdir=(0.2, 1), sk=0.25, angle=0, n=30, inkw=1.6, inkc="#000000", hi=0.45))
    out.append(taper([(122, bot + 2), (300, bot + 1), (478, bot + 2)], 2.4, 2.4, "#9A8AA0", 0.7))
    snow = [(150, bot + 2), (160, bot - 8), (196, bot - 14), (250, bot - 11), (300, bot - 15), (352, bot - 10), (402, bot - 14), (440, bot - 7), (452, bot + 2)]
    out.append(painted(D, snow + [(300, bot + 4)], SNOW, 15, sdir=(0.3, 1), sk=0.2, angle=0, n=24, inkw=1.2, inkc="#6A7898", hi=0.6))
    for (dx, dy, r) in ((322, bot - 10, 6.0), (342, bot - 7, 4.6), (331, bot - 1, 3.8)):
        out.append(f'<path d="{blob(dx, dy, r * 1.2, r * 0.75, int(dx), 0.15, 10)}" fill="#B0101E"/>')
        out.append(f'<circle cx="{dx - r * 0.35:.1f}" cy="{dy - r * 0.3:.1f}" r="{r * 0.3:.1f}" fill="#FFB0B0" opacity="0.8"/>')
    # embroidery hoop leaning on the frame, needle and red thread trailing toward the drops
    out.append(embroidery_hoop(D, 190, bot + 2, 44, 30, 16))
    out.append(needle_thread(D, 262, bot - 18, 300, bot - 30, [(262, bot - 18), (276, bot - 4), (300, bot - 2), (312, bot - 8)], 17))
    # the apple: white cheek and red cheek
    ax, ay = 418, bot - 22
    out.append(cast(D, ax + 10, bot + 1, 34, 6, strength=0.5, seed=18))
    out.append(apple(D, ax, ay, 28, ("#F27A6A", "#C41E2A", "#6A0A10"), 18, leafc="olive", blush="#F8E6C8", light=(-0.8, -0.5)))
    # lettering
    out.append(tx(300, 80, "BROTHERS GRIMM · 1812", CINZEL, 17, "#7A1E26", ls=5, max_w=360))
    out.append(letters(D, 300, 136, "Snow White", SERIF_IT, 66, "#2A1A22", ["#3A2A34", "#140A10", "#5A4652"], 19, max_w=420,
                       shadow="#C8B490", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(multi(300, 494, [("White as snow, ", "#4A5A86"), ("red as blood,", "#B0101E")], SERIF_IT, 34, max_w=440))
    out.append(multi(300, 536, [("and black as ", "#4A3A40"), ("ebony.", "#140A10")], SERIF_IT, 34, max_w=440))
    return finish_b(D, out, 20, INK, 0.7)


# ================================================================ 2. hansel and gretel — the house of bread and cake
def gingerbread_house(D, cx, base, seed):
    rnd = random.Random(seed)
    out = []
    wl, wr, wt = cx - 92, cx + 92, base - 96
    apex = (cx, base - 228)
    eaveL, eaveR = (cx - 132, base - 88), (cx + 132, base - 88)
    out.append(cast(D, cx + 10, base + 4, 150, 14, strength=0.55, seed=seed))
    # side wall (shade) for 3/4 feel
    # front wall of gingerbread
    wall = rect_pts(wl, wt, wr, base, 14, seed, 0.8)
    out.append(painted(D, wall, ("#E2A866", "#B87638", "#6E3E16"), seed + 1, sdir=(1, 0.4), sk=0.12, angle=-90, n=60, inkw=1.8, hi=0.35))
    out.append(specks(seed, (wl + 4, wt + 4, wr - 4, base - 4), ["#7E4A1E", "#F2C890"], 80, (0.8, 1.8), (0.4, 0.8)))
    # gable (cake) above the wall
    gab = [(wl, wt), apex, (wr, wt)]
    out.append(painted(D, jitter([(wl, wt + 2), (cx, apex[1] + 30), (wr, wt + 2)], seed, 0.6), ("#F2C88A", "#D0965A", "#7E4E22"), seed + 2, sk=0.12, angle=-90, n=30, inkw=1.4, hi=0.3))
    # roof: two slopes of cake tiles, iced
    for sg in (-1, 1):
        e = eaveL if sg < 0 else eaveR
        slope = [apex, (apex[0] + sg * 10, apex[1] - 4), (e[0] + sg * 6, e[1] - 6), e, (e[0] - sg * 4, e[1] + 10), (apex[0], apex[1] + 22)]
        out.append(painted(D, slope, ("#7A4A30", "#4E2614", "#24100A"), seed + 3 + sg, sdir=(sg, 0.4), sk=0.1, angle=-30 * sg, n=40, inkw=1.8, hi=0.2))
        rcid = D.clip(f'<path d="{smooth_closed(slope)}"/>')
        tiles = []
        for row in range(9):
            t = (row + 0.6) / 9
            y0 = apex[1] + (e[1] - apex[1]) * t
            xs, xe = apex[0], apex[0] + (e[0] - apex[0]) * (t + 0.05)
            n = max(2, int(abs(xe - xs) / 18))
            for j in range(n + 1):
                tx_ = xs + (xe - xs) * (j + (row % 2) * 0.5) / n
                ty_ = y0 + (tx_ - xs) * (e[1] - apex[1]) / (e[0] - apex[0]) * 0 + 0
                c = rnd.choice(["#F6C8D4", "#FFFFFF", "#F2A6BC", "#FBE6EE", "#C8885A"])
                tiles.append(f'<path d="{blob(tx_, ty_, 10, 7, seed + row * 30 + j, 0.12, 10)}" fill="{c}"/>')
                tiles.append(f'<path d="{smooth_open([(tx_ - 9, ty_ + 2), (tx_, ty_ + 7), (tx_ + 9, ty_ + 2)])}" stroke="#6A3A2A" stroke-width="1.1" fill="none" opacity="0.55"/>')
                if rnd.random() < 0.3:
                    tiles.append(f'<circle cx="{tx_ + rnd.uniform(-4, 4):.1f}" cy="{ty_ - 2:.1f}" r="1.8" fill="{rnd.choice(["#C8283A", "#3A8AC8", "#F6C21C", "#3EA05A"])}"/>')
        out.append(f'<g {rcid}>{"".join(tiles)}</g>')
        out.append(ink(smooth_closed(slope), "#24100A", 1.6, seed + 9, 1, 0.7))
        # icing drips along the eave
        drip = []
        for k in range(14):
            t = k / 13
            px, py = apex[0] + (e[0] - apex[0]) * t, apex[1] + 18 + (e[1] + 6 - apex[1] - 18) * t
            drip.append((px, py))
            if 0.1 < t < 0.98:
                L = rnd.uniform(5, 14)
                out.append(f'<path d="M {px - 3:.1f} {py:.1f} Q {px - 3:.1f} {py + L:.1f} {px:.1f} {py + L + 2:.1f} Q {px + 3:.1f} {py + L:.1f} {px + 3:.1f} {py:.1f} Z" fill="#FFFFFF"/>')
        out.append(taper(drip, 7, 6, "#FFFFFF"))
        out.append(taper(drip, 2, 2, "#D8D0E0", 0.7))
    # chimney of chocolate with smoke
    chx = cx + 52
    ch = rect_pts(chx - 12, base - 222, chx + 12, base - 168, 10, seed + 5, 0.4)
    out.append(painted(D, ch, ("#8A5A3A", "#5A3018", "#2A1408"), seed + 5, sdir=(1, 0.2), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.3))
    out.append(f'<path d="{blob(chx, base - 222, 15, 5, seed, 0.1, 10)}" fill="#FFFFFF"/>')
    out.append(taper(catmull([(chx, base - 228), (chx - 6, base - 256), (chx + 8, base - 282), (chx + 30, base - 300)], 6), 6, 18, "#C8D0E8", 0.35))
    # windows of clear sugar, glowing
    for wx in (cx - 62, cx + 34):
        wy = base - 74
        out.append(soft_glow(D, wx + 14, wy + 16, 46, "#FFC860", 0.55))
        win = rect_pts(wx, wy, wx + 28, wy + 32, 8, seed + int(wx), 0.4)
        out.append(painted(D, win, ("#FFF6C0", "#FFD060", "#E89030"), seed + int(wx), sk=0.15, angle=-60, n=8, inkw=0, hi=0.5))
        out.append(f'<path d="M {wx + 14} {wy} L {wx + 14} {wy + 32} M {wx} {wy + 16} L {wx + 28} {wy + 16}" stroke="#FFFFFF" stroke-width="3.4"/>')
        out.append(f'<path d="M {wx + 14} {wy} L {wx + 14} {wy + 32} M {wx} {wy + 16} L {wx + 28} {wy + 16}" stroke="#E2405A" stroke-width="1.6" stroke-dasharray="3 3"/>')
        out.append(f'<path d="{hg.org_rect(wx - 4, wy - 4, 36, 40, seed, 0.4, 10, 3)}" fill="none" stroke="#FFFFFF" stroke-width="4.5"/>')
        for j in range(7):
            out.append(f'<circle cx="{wx - 4 + j * 6:.1f}" cy="{wy + 38:.1f}" r="2.6" fill="#FFFFFF"/>')
    # round window in the gable: a peppermint
    pmx, pmy = cx, base - 150
    out.append(f'<circle cx="{pmx}" cy="{pmy}" r="17" fill="#FFFFFF"/>')
    for k in range(8):
        a0, a1 = math.radians(k * 45), math.radians(k * 45 + 22)
        out.append(f'<path d="M {pmx} {pmy} L {pmx + 16 * math.cos(a0):.1f} {pmy + 16 * math.sin(a0):.1f} A 16 16 0 0 1 {pmx + 16 * math.cos(a1):.1f} {pmy + 16 * math.sin(a1):.1f} Z" fill="#D8283A"/>')
    out.append(ink(blob(pmx, pmy, 17, 17, seed, 0.02, 16), "#7A1020", 1.4, seed, 1, 0.7))
    # door: chocolate with an arched top, a crack of warm light
    dx0, dx1 = cx - 16, cx + 16
    door = arch_pts(dx0, dx1, base - 48, base, 6)
    out.append(soft_glow(D, cx, base - 30, 40, "#FFB040", 0.5))
    out.append(painted(D, door, ("#8A5232", "#5A2E16", "#2A1206"), seed + 6, sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.25))
    out.append(f'<path d="M {dx1 - 3} {base - 40} L {dx1 - 3} {base}" stroke="#FFD27A" stroke-width="2.4"/>')
    out.append(f'<circle cx="{dx1 - 8}" cy="{base - 24}" r="3" fill="#F6C21C"/>')
    out.append(ink(smooth_open(arch_pts(dx0 - 4, dx1 + 4, base - 48, base, 6)), "#FFFFFF", 3.4, seed, 1, 1))
    # candies set into the wall: gumdrops, buttons, a candy-stick border
    cols = ["#E2405A", "#3EA05A", "#F6C21C", "#3A8AC8", "#F28AB0", "#FFFFFF"]
    for k in range(18):
        px = wl + 8 + (wr - wl - 16) * k / 17
        out.append(f'<path d="{blob(px, base - 6, 4.2, 3.6, seed + k, 0.1, 8)}" fill="{cols[k % len(cols)]}"/>')
        out.append(f'<circle cx="{px - 1.2:.1f}" cy="{base - 7.6:.1f}" r="1.1" fill="#FFFFFF" opacity="0.8"/>')
    for (px, py) in ((wl + 14, wt + 20), (wr - 14, wt + 20), (wl + 14, base - 40), (wr - 14, base - 40)):
        out.append(f'<circle cx="{px}" cy="{py}" r="6" fill="#FFFFFF"/><circle cx="{px}" cy="{py}" r="6" fill="none" stroke="#D8283A" stroke-width="2.4" stroke-dasharray="3 2.2"/>')
    for sg in (-1, 1):
        x = wl + 2 if sg < 0 else wr - 2
        out.append(f'<path d="M {x - 3.5:.1f} {wt + 2} L {x + 3.5:.1f} {wt + 2} L {x + 3.5:.1f} {base} L {x - 3.5:.1f} {base} Z" fill="#FFFFFF"/>')
        for j in range(int((base - wt) / 9)):
            out.append(f'<path d="M {x - 3.5:.1f} {wt + 4 + j * 9:.1f} l 7 -4" stroke="#D8283A" stroke-width="2.6"/>')
    # the white bird on the ridge
    bx, by = cx - 4, apex[1] - 2
    out.append(painted(D, [(bx - 14, by - 6), (bx - 4, by - 14), (bx + 8, by - 12), (bx + 14, by - 6), (bx + 26, by - 4), (bx + 12, by + 2), (bx - 8, by + 2)], SNOW, seed + 7, sk=0.2, angle=0, n=6, inkw=1.2, inkc="#4A5A7A", hi=0.5))
    out.append(f'<path d="{blob(bx - 12, by - 14, 6, 5.4, seed, 0.05, 10)}" fill="#FFFFFF"/>')
    out.append(f'<path d="M {bx - 18} {by - 14} l -5 1.6 l 5 1.2 Z" fill="#E8A030"/><circle cx="{bx - 14}" cy="{by - 15}" r="1.1" fill="#1A1010"/>')
    return "".join(out)


@design("hansel-and-gretel")
def hansel_and_gretel():
    D = Doc2("ft-hg")
    out = [sky(D, [(0, "#0C1A2E"), (0.45, "#1E3A4E"), (0.75, "#3A5A5E"), (1, "#14201E")], 1, 600, ["#1E3448", "#0A1420", "#2E4E5A"], 50)]
    out.append(stars_field(2, (0, 40, 600, 220), 50))
    out.append(soft_glow(D, 150, 186, 110, "#E8F0D8", 0.35))
    out.append(f'<path d="{blob(150, 186, 22, 22, 3, 0.02, 20)}" fill="#F6F0D8"/>')
    out.append(f'<path d="{blob(143, 180, 7, 5, 4, 0.2, 10)}" fill="#D8D0B0" opacity="0.6"/><path d="{blob(157, 193, 5, 4, 5, 0.2, 10)}" fill="#D8D0B0" opacity="0.6"/>')
    rnd = random.Random(4)
    # layers of forest: far, mid
    for k in range(26):
        x = -10 + k * 25 + rnd.uniform(-6, 6)
        out.append(conifer(x, 330, rnd.uniform(90, 150), "#24404A", k, width=0.34))
    out.append(mist(D, 312, 50, 5, "#9AB8B8", 0.35))
    for k in range(18):
        x = -20 + k * 36 + rnd.uniform(-8, 8)
        out.append(conifer(x, 380, rnd.uniform(110, 170), "#142A30", k + 40, width=0.36))
    # the clearing (moonlit ground)
    out.append(hill(D, [(-20, 360), (150, 352), (300, 348), (450, 352), (620, 362)], 620, ("#4E6A4E", "#2E4632", "#14241A"), 6, inkw=0, sop=(0.15, 0.35)))
    out.append(soft_glow(D, 300, 350, 220, "#FFB050", 0.28))
    out.append(gingerbread_house(D, 300, 392, 7))
    # moonlit path of white pebbles
    path = [(300, 394), (290, 420), (268, 446), (262, 466), (276, 484)]
    pp = catmull(path, 6)
    for i, (px, py) in enumerate(pp):
        sz = 1.2 + (py - 390) / 40
        for sg in (-1, 1):
            if rnd.random() < 0.8:
                qx = px + sg * (6 + (py - 390) * 0.12) + rnd.uniform(-3, 3)
                out.append(f'<path d="{blob(qx, py, sz * 1.3, sz, i * 2 + sg, 0.15, 8)}" fill="#F2F4FF"/>')
                out.append(soft_glow(D, qx, py, sz * 4, "#E8F0FF", 0.3))
    out.append(child_pair(292, 452, 0.95, "#0A1418", rim="#FFC870"))
    out.append(cast(D, 292, 452, 26, 4, strength=0.5, seed=8))
    # foreground gnarled trunks framing the scene
    out.append(gnarled_trunk(D, 34, 640, -20, 96, 9, ("#5A5E50", "#2A3028", "#0C100C"), lean=0.06, rim="#FFC870", rim_side=1, branches=2))
    out.append(gnarled_trunk(D, 574, 640, -20, 86, 10, ("#5A5E50", "#2A3028", "#0C100C"), lean=-0.06, rim="#FFC870", rim_side=-1, branches=2))
    out.append(grass(11, (0, 560, 600, 610), ["#0E1A16", "#1E2E24"], 140, (8, 22)))
    # lettering
    out.append(letters(D, 300, 108, "Hansel & Gretel", SERIF_IT, 64, "#FFE8C0", ["#FFF4DA", "#F2C88A", "#FFE0A0"], 12, max_w=430,
                       shadow="#06100E", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 504, "“Nibble, nibble, little mouse,", SERIF_IT, 30, "#FFE8C8", max_w=420))
    out.append(tx(300, 540, "who is nibbling at my house?”", SERIF_IT, 30, "#FFE8C8", max_w=420))
    return finish_b(D, out, 13, "#000000", 0.55)


# ================================================================ 3. rapunzel — the tower in the wood, the golden braid
def braid(D, pts, w, seed, pal=GOLD):
    """A thick plait along a path: alternating lobes, each painted with strands and a sheen."""
    path = catmull(pts, 10)
    out = [taper(path, w * 1.05, w * 0.55, pal[2])]
    seg = 2
    for i in range(0, len(path) - seg, seg):
        (x0, y0), (x1, y1) = path[i], path[i + seg]
        a = math.atan2(y1 - y0, x1 - x0)
        t = i / len(path)
        ww = w * (1 - 0.45 * t)
        side = 1 if (i // seg) % 2 else -1
        mx, my = (x0 + x1) / 2 - math.sin(a) * side * ww * 0.18, (y0 + y1) / 2 + math.cos(a) * side * ww * 0.18
        L = math.hypot(x1 - x0, y1 - y0)
        d = blob(mx, my, L * 0.85, ww * 0.42, seed + i, 0.08, 10, math.degrees(a) + side * 28)
        out.append(f'<path d="{d}" fill="{pal[1]}"/>')
        out.append(f'<path d="{blob(mx - math.cos(a) * L * 0.1, my - 1, L * 0.5, ww * 0.16, seed + i + 1, 0.1, 8, math.degrees(a) + side * 28)}" fill="{pal[0]}" opacity="0.85"/>')
        out.append(ink(d, pal[2], 0.9, seed + i, 1, 0.55))
    return "".join(out)


def stone_tower(D, cx, base, top, w0, w1, seed, pal=STONE, lit=-1, roof=("#8A6A9A", "#4E3A6A", "#22163A")):
    rnd = random.Random(seed)
    out = []
    body = [(cx - w0 / 2, base), (cx - w1 / 2, top), (cx + w1 / 2, top), (cx + w0 / 2, base)]
    bp = poly_pts(body, 16, seed, 0.6)
    d = smooth_closed(bp)
    out.append(painted(D, bp, pal, seed, sdir=(-lit, 0.1), sk=0.24, angle=-90, n=40, inkw=1.8, hi=0.35))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    rows = int((base - top) / 13)
    for r in range(rows):
        y = top + 6 + r * 13
        t = (y - top) / (base - top)
        ww = w1 + (w0 - w1) * t
        off = (r % 2) * 0.5
        n = 5
        for j in range(n + 1):
            u = (j + off) / n                      # around the visible half of the cylinder
            ang = math.pi * (u - 0.5)
            x = cx + math.sin(ang) * ww / 2
            inner.append(f'<path d="M {x:.1f} {y - 6:.1f} L {x + rnd.uniform(-0.6, 0.6):.1f} {y + 6:.1f}" stroke="{pal[2]}" stroke-width="1.5" opacity="0.65"/>')
            if j < n:
                xb = cx + math.sin(math.pi * ((j + 1 + off) / n - 0.5)) * ww / 2
                inner.append(f'<path d="{hg.org_rect(min(x, xb) + 1.5, y - 5, abs(xb - x) - 3, 10, seed + r * 9 + j, 0.5, 8, 2)}" fill="{rnd.choice([pal[0], "#C8BCA8", "#B0A898", "#E0D4C0"])}" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>')
        inner.append(pline([(cx - ww / 2, y + 6), (cx, y + 7.5), (cx + ww / 2, y + 6)], pal[2], 1.5, seed + r, 0.6, 1))
        if rnd.random() < 0.5:
            sx = cx + rnd.uniform(-0.4, 0.4) * ww
            inner.append(f'<path d="{blob(sx, y, rnd.uniform(5, 10), 5, seed + r * 7, 0.2, 8)}" fill="{rnd.choice([pal[0], pal[2]])}" opacity="0.35"/>')
    # cylinder shading: dark on the far side, rim of sunset light on the near edge
    g = D.lin([(0, "#2A1A3A", 0.0 if lit < 0 else 0.55), (0.35, "#2A1A3A", 0.0), (0.65, "#2A1A3A", 0.1), (1, "#2A1A3A", 0.6 if lit < 0 else 0)], 0, 0, 1, 0)
    inner.append(f'<rect x="{cx - w0 / 2 - 2:.1f}" y="{top:.1f}" width="{w0 + 4:.1f}" height="{base - top:.1f}" fill="{g}"/>')
    # ivy creeping up
    for k in range(40):
        y = base - rnd.uniform(0, (base - top) * 0.45) ** 1.0
        x = cx + w0 * rnd.uniform(-0.5, -0.1)
        inner.append(f'<path d="{blob(x, y, 4.5, 3.4, seed + k, 0.15, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#3E6A3A", "#22402A", "#5A8A48"])}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # corbelled parapet ring and a steep slate cone
    out.append(painted(D, rect_pts(cx - w1 / 2 - 8, top - 14, cx + w1 / 2 + 8, top + 2, 10, seed + 1, 0.4), pal, seed + 1, sdir=(-lit, 0.6), sk=0.2, angle=0, n=12, inkw=1.6, hi=0.4))
    for j in range(7):
        x = cx - w1 / 2 - 4 + j * (w1 + 8) / 6
        out.append(f'<path d="M {x - 3:.1f} {top + 2} L {x + 3:.1f} {top + 2} L {x:.1f} {top + 10} Z" fill="{pal[2]}" opacity="0.7"/>')
    cone = [(cx - w1 / 2 - 14, top - 12), (cx - w1 * 0.2, top - 56), (cx, top - 98), (cx + w1 * 0.2, top - 56), (cx + w1 / 2 + 14, top - 12), (cx, top - 6)]
    out.append(painted(D, cone, roof, seed + 2, sdir=(-lit, 0.2), sk=0.25, angle=-70, n=30, inkw=1.8, hi=0.4))
    ccid = D.clip(f'<path d="{smooth_closed(cone)}"/>')
    sl = []
    for r in range(8):
        y = top - 14 - r * 11
        for j in range(-6, 7):
            sl.append(f'<path d="M {cx + j * 9 + (r % 2) * 4.5 - 5:.1f} {y:.1f} q 5 4 10 0" stroke="{roof[2]}" stroke-width="1" fill="none" opacity="0.6"/>')
    out.append(f'<g {ccid}>{"".join(sl)}</g>')
    out.append(f'<path d="M {cx} {top - 98} l 0 -16" stroke="{GOLD[2]}" stroke-width="2.4"/>')
    out.append(f'<path d="M {cx} {top - 112} l 12 4 l -12 5 Z" fill="{MADDER[1]}"/>')
    return "".join(out)


def rapunzel_at_window(D, x, y, s):
    """Rapunzel leaning on the sill, lamp-lit from behind: head, shoulders, an arm on the sill."""
    def L(pts):
        return T(pts, x, y, s)
    col = "#3A1E2A"
    out = [f'<path d="{smooth_closed(L([(-11, 0), (-10, -8), (-5, -12), (5, -12), (10, -8), (11, 0)]))}" fill="{col}"/>']
    out.append(f'<path d="{blob(*L([(0, -18)])[0], 5.6 * s, 6.4 * s, 3, 0.05, 10)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-6, -22), (0, -25), (6, -22), (7, -14), (4, -10), (-4, -10), (-7, -14)]))}" fill="{GOLD[1]}"/>')
    out.append(ink(smooth_open(L([(-6, -22), (0, -25), (6, -22)])), GOLD[0], 1.2, 1, 1, 0.9))
    return "".join(out)


def prince_calling(x, base, s, col, rim=None):
    """A young prince in a short cloak and feathered cap, head tipped back, one hand cupped to his mouth; faces right."""
    def L(pts):
        return T(pts, x, base, s)
    out = []
    out.append(taper(catmull(L([(-3, -26), (-5, -12), (-6, 0)]), 4), 4.6 * s, 3.4 * s, col))
    out.append(taper(catmull(L([(3, -26), (6, -12), (8, 0)]), 4), 4.6 * s, 3.4 * s, col))
    out.append(f'<path d="{smooth_closed(L([(-8, -1), (-2, -1), (-1, 1), (-10, 1)]))}" fill="{col}"/><path d="{smooth_closed(L([(5, -1), (12, -1), (13, 1), (4, 1)]))}" fill="{col}"/>')
    # doublet and belt
    out.append(f'<path d="{smooth_closed(L([(-7, -50), (-9, -38), (-7, -24), (8, -24), (9, -38), (7, -50)]))}" fill="{col}"/>')
    # short cloak hanging from the shoulders behind him
    out.append(f'<path d="{smooth_closed(L([(-6, -52), (-11, -44), (-15, -30), (-17, -18), (-9, -20), (-5, -30), (-3, -42)]))}" fill="{col}"/>')
    # neck, head tipped back looking up at the window
    out.append(f'<path d="{smooth_closed(L([(-2, -50), (-1, -56), (4, -56), (4, -50)]))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(3, -62)])[0], 6.2 * s, 6.8 * s, 3, 0.05, 10, -30)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(8, -64), (11, -62), (9, -59)]))}" fill="{col}"/>')
    # little velvet cap with an upright plume
    out.append(f'<path d="{smooth_closed(L([(-4, -64), (-3, -70), (3, -72), (8, -69), (6, -65)]))}" fill="{col}"/>')
    out.append(taper(catmull(L([(-1, -70), (-4, -77), (-3, -83)]), 5), 2.6 * s, 0.8, col))
    # arms: one at his side, one raised to the mouth
    out.append(taper(catmull(L([(-6, -46), (-9, -36), (-8, -28)]), 4), 3.4 * s, 2.8 * s, col))
    out.append(taper(catmull(L([(6, -47), (13, -52), (10, -60)]), 4), 3.4 * s, 2.8 * s, col))
    out.append(taper(catmull(L([(3, -24), (14, -18), (20, -16)]), 3), 1.6 * s, 1.2 * s, col))   # sword
    if rim:
        out.append(ink(smooth_open(L([(8, -66), (10, -60), (7, -55), (9, -46), (9, -36), (7, -26)])), rim, 1.4, 1, 1, 0.7))
    return "".join(out)


def rampion(D, x, base, h, seed):
    """Rampion (rapunzel) bellflower: a stem of nodding violet bells — the plant the tale is named after."""
    rnd = random.Random(seed)
    lean = rnd.uniform(-0.15, 0.15)
    stem = [(x, base), (x + lean * h * 0.4, base - h * 0.5), (x + lean * h, base - h)]
    out = [pline(stem, "#2E4A2A", 1.8, seed, 0.95, 1)]
    for k in range(3):
        t = 0.15 + k * 0.12
        px, py = x + lean * h * t, base - h * t
        sg = 1 if k % 2 else -1
        out.append(f'<path d="{blob(px + sg * 7, py - 2, 8, 2.6, seed + k, 0.1, 8, sg * -30)}" fill="#3E6A3A"/>')
    for k in range(6):
        t = 0.45 + k * 0.1
        if t > 1:
            break
        px, py = x + lean * h * t, base - h * t
        sg = 1 if k % 2 else -1
        bx, by = px + sg * 6 * h / 70, py + 3
        k_ = h / 70
        bell = [(bx - 3.6 * k_, by - 3), (bx + 3.6 * k_, by - 3), (bx + 4.8 * k_, by + 6 * k_), (bx + 1.4 * k_, by + 4.6 * k_), (bx, by + 7.4 * k_), (bx - 1.4 * k_, by + 4.6 * k_), (bx - 4.8 * k_, by + 6 * k_)]
        out.append(pline([(px, py), (bx, by - 3)], "#2E4A2A", 1, seed + k, 0.9, 1))
        out.append(painted(D, bell, ("#D8C0F2", "#9A72D0", "#4E2E8A"), seed + k, sk=0.2, angle=-90, n=3, inkw=0.8, inkc="#2A1A4A", hi=0.4))
    return "".join(out)


@design("rapunzel")
def rapunzel():
    D = Doc2("ft-rp")
    out = [sky(D, [(0, "#2A2050"), (0.35, "#6A3E78"), (0.62, "#D07A80"), (0.8, "#F6B47A"), (1, "#F8D8A0")], 1, 600,
               ["#7A4A88", "#3A2A60", "#F0A08A", "#FFD0A0"], 60)]
    out.append(stars_field(2, (0, 30, 600, 150), 30))
    out.append(soft_glow(D, 420, 420, 260, "#FFD890", 0.5))
    for (cx_, cy_, w_) in ((150, 330, 220), (520, 250, 160), (130, 190, 130)):
        out.append(taper([(cx_ - w_ / 2, cy_), (cx_, cy_ - 4), (cx_ + w_ / 2, cy_ + 2)], 4, 10, "#F6B0A0", 0.45))
        out.append(taper([(cx_ - w_ / 2 + 20, cy_ + 8), (cx_ + 10, cy_ + 6), (cx_ + w_ / 2 - 10, cy_ + 10)], 3, 6, "#8A4A7A", 0.4))
    # distant hills and forest
    out.append(hill(D, [(-20, 420), (100, 396), (220, 408), (340, 392), (480, 404), (620, 390)], 620, ("#A88AB0", "#8A6E9A", "#5A4A70"), 3, inkw=0, sop=(0.1, 0.25)))
    rnd = random.Random(5)
    for k in range(30):
        x = -10 + k * 21 + rnd.uniform(-5, 5)
        out.append(conifer(x, 440, rnd.uniform(40, 70), "#6A5480", k, width=0.34))
    out.append(mist(D, 440, 40, 6, "#F2C8C0", 0.5))
    # the tower
    tcx, tbase, ttop = 420, 520, 196
    out.append(stone_tower(D, tcx, tbase, ttop, 104, 86, 7))
    # the one window, lamp-lit, with Rapunzel at the sill
    wx0, wx1 = tcx - 17, tcx + 17
    wpts = arch_pts(wx0, wx1, ttop + 30, ttop + 70, 6)
    out.append(soft_glow(D, tcx, ttop + 48, 60, "#FFC860", 0.6))
    out.append(painted(D, wpts, ("#FFF2B0", "#FFC24A", "#D07A1A"), 8, sk=0.15, angle=-90, n=6, inkw=1.6, hi=0.4))
    out.append(rapunzel_at_window(D, tcx, ttop + 68, 1.25))
    out.append(painted(D, rect_pts(wx0 - 6, ttop + 66, wx1 + 6, ttop + 74, 8, 9, 0.3), STONE, 9, sk=0.2, angle=0, n=4, inkw=1.2, hi=0.4))
    # the braid, twenty ells long, down the wall to the ground
    out.append(braid(D, [(tcx - 4, ttop + 70), (tcx - 24, ttop + 120), (tcx - 36, ttop + 190), (tcx - 30, ttop + 260), (tcx - 46, ttop + 300), (tcx - 78, ttop + 322)], 16, 10))
    # the prince calling up
    out.append(prince_calling(306, 528, 1.25, "#1A1226", rim="#FFC890"))
    out.append(cast(D, 306, 528, 34, 5, strength=0.45, seed=11))
    for k, (x, y, h) in enumerate(((76, 590, 120), (100, 596, 96), (126, 588, 110), (156, 598, 80), (196, 596, 64), (230, 600, 52), (544, 598, 70), (566, 600, 90))):
        out.append(rampion(D, x, y, h, 40 + k))
    # foreground forest around the tower's foot
    for k, (x, h) in enumerate(((330, 120), (500, 150), (548, 110), (276, 90), (590, 130), (470, 80))):
        out.append(conifer(x, 560, h, "#1E1A34", 30 + k, width=0.36, light="#8A5A7A"))
    out.append(hill(D, [(-20, 520), (150, 514), (300, 520), (460, 512), (620, 520)], 620, ("#4A3A5A", "#2A2040", "#140E22"), 12, inkw=0, sop=(0.15, 0.35)))
    out.append(grass(13, (180, 508, 600, 600), ["#1A1430", "#3A2A50", "#5A3A60"], 120, (8, 18)))
    for k in range(10):
        x, y = rnd.uniform(120, 580), rnd.uniform(530, 590)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#F2E0F0" opacity="0.8"/>')
    # lettering: left column
    out.append(tx(184, 132, "BROTHERS GRIMM", CINZEL, 18, "#FFE8D8", ls=5, max_w=230))
    out.append(letters(D, 184, 200, "Rapunzel,", SERIF_IT, 60, "#FFF0D8", ["#FFFFFF", "#FFD8B8", "#F6E0C8"], 14, max_w=240,
                       shadow="#3A1E40", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(letters(D, 184, 262, "Rapunzel,", SERIF_IT, 60, "#FFF0D8", ["#FFFFFF", "#FFD8B8", "#F6E0C8"], 15, max_w=240,
                       shadow="#3A1E40", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(184, 304, "let down", SERIF_IT, 34, "#FFE2A8", max_w=240))
    out.append(tx(184, 342, "your hair.", SERIF_IT, 34, "#FFE2A8", max_w=240))
    return finish_b(D, out, 16, "#1A0A20", 0.55)


# ================================================================ 4. the frog prince — the golden ball on the well
def frog(D, ox, oy, s, seed, flip=False, crown=True):
    """A seated frog in three-quarter view facing right (flip -> left); (ox, oy) = where it sits."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    out = [cast(D, *L([(0, 2)])[0], 46 * s, 6 * s, strength=0.45, seed=seed)]
    pal = ("#A8D07A", "#5A9A3E", "#24501E")
    # far hind leg
    out.append(painted(D, L([(-34, -4), (-22, -16), (-6, -12), (0, -2), (-14, 2)]), ("#7AA85A", "#3E7A2E", "#183A14"), seed, sk=0.2, angle=0, n=10, inkw=1.2, hi=0.2))
    body = L([(-38, -2), (-42, -16), (-34, -32), (-16, -46), (4, -54), (22, -56), (36, -50), (44, -38), (42, -28), (34, -20), (22, -8), (10, 0)])
    out.append(painted(D, body, pal, seed + 1, sdir=(0.3, 1) if not flip else (-0.3, 1), sk=0.18, angle=-30, n=50, inkw=1.8, inkc="#1A3010", hi=0.45, hik=0.08))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    rnd = random.Random(seed)
    inner = [f'<path d="{smooth_closed(L([(6, -6), (20, -14), (34, -22), (40, -32), (38, -24), (28, -10), (12, 0)]))}" fill="#F2EAB0" opacity="0.85"/>']
    for k in range(9):
        px, py = L([(rnd.uniform(-34, 20), rnd.uniform(-44, -14))])[0]
        inner.append(f'<path d="{blob(px, py, rnd.uniform(2.5, 5) * s, rnd.uniform(2, 4) * s, seed + k, 0.2, 8)}" fill="#2E5A22" opacity="0.7"/>')
    inner.append(taper(L([(-30, -30), (-10, -46), (14, -54)]), 1, 4 * s, "#E2F4B8", 0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # near hind leg folded, webbed foot
    thigh = L([(-40, -6), (-34, -20), (-16, -24), (-4, -14), (-8, -2), (-26, 0)])
    out.append(painted(D, thigh, pal, seed + 2, sdir=(0.2, 1), sk=0.18, angle=-10, n=14, inkw=1.6, inkc="#1A3010", hi=0.4))
    out.append(painted(D, L([(-12, 0), (-2, -6), (12, -4), (20, 2), (8, 3), (-6, 3)]), pal, seed + 3, sk=0.2, angle=0, n=6, inkw=1.3, inkc="#1A3010", hi=0.3))
    for k in range(3):
        a, b = L([(4 + k * 5, 0)])[0], L([(10 + k * 6, 4)])[0]
        out.append(f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="{1.8 * s:.1f}" fill="{pal[1]}" stroke="#1A3010" stroke-width="0.8"/>')
    # front leg
    out.append(taper(catmull(L([(30, -24), (34, -12), (36, -2)]), 4), 7 * s, 5 * s, pal[1]))
    out.append(pline(L([(30, -24), (34, -12), (36, -2)]), "#1A3010", 1.1, seed, 0.5, 1))
    for k, dx in enumerate((-4, 1, 6)):
        e = L([(36 + dx, 2)])[0]
        out.append(f'<circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="{2 * s:.1f}" fill="{pal[1]}" stroke="#1A3010" stroke-width="0.8"/>')
    # mouth and nostril
    out.append(pline(L([(44, -38), (36, -34), (24, -34), (14, -38)]), "#1A3010", 1.6, seed, 0.85, 1))
    nx_, ny_ = L([(40, -46)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{1.2 * s:.1f}" fill="#1A3010"/>')
    # eyes: gold irises, horizontal pupils
    for (ex, ey, r) in ((10, -58, 8.5), (28, -60, 9.5)):
        cx_, cy_ = L([(ex, ey)])[0]
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_ + 1:.1f}" r="{(r + 2) * s:.1f}" fill="{pal[1]}" stroke="#1A3010" stroke-width="1.2"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r * 0.78 * s:.1f}" fill="#E8B83A"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r * 0.78 * s:.1f}" fill="none" stroke="#7A5010" stroke-width="1"/>')
        out.append(f'<ellipse cx="{cx_ + (1.5 if not flip else -1.5) * s:.1f}" cy="{cy_:.1f}" rx="{r * 0.55 * s:.1f}" ry="{r * 0.24 * s:.1f}" fill="#0A0A06"/>')
        out.append(f'<circle cx="{cx_ - 2.5 * s:.1f}" cy="{cy_ - 2.5 * s:.1f}" r="{1.6 * s:.1f}" fill="#FFFFFF"/>')
    if crown:
        cx_, cy_ = L([(19, -70)])[0]
        cw, ch = 22 * s, 14 * s
        cr = [(cx_ - cw / 2, cy_), (cx_ - cw / 2 - 1, cy_ - ch), (cx_ - cw / 4, cy_ - ch * 0.45), (cx_, cy_ - ch * 1.15), (cx_ + cw / 4, cy_ - ch * 0.45), (cx_ + cw / 2 + 1, cy_ - ch), (cx_ + cw / 2, cy_)]
        cr = rot(cr, cx_, cy_, -12 if not flip else 12)
        out.append(painted(D, cr, GOLD, seed + 5, sk=0.2, angle=-90, n=6, inkw=1.3, inkc="#5A3A0A", hi=0.5))
        for p in (cr[1], cr[3], cr[5]):
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{2.2 * s:.1f}" fill="#FFF0B0" stroke="#8A6020" stroke-width="0.8"/>')
        mx, my = (cr[0][0] + cr[6][0]) / 2, (cr[0][1] + cr[6][1]) / 2 - ch * 0.3
        out.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{2.4 * s:.1f}" fill="#C8203A"/>')
    return "".join(out)


def golden_ball(D, cx, cy, r, seed):
    out = [soft_glow(D, cx, cy, r * 2.6, "#FFD860", 0.35), cast(D, cx + r * 0.3, cy + r * 0.9, r * 1.0, r * 0.22, strength=0.5, seed=seed)]
    g = D.rad([(0, "#FFF8D0"), (0.25, "#F6D060"), (0.7, "#C8902A"), (1, "#6A4410")], cx=0.36, cy=0.32, r=0.75)
    out.append(f'<path d="{blob(cx, cy, r, r, seed, 0.01, 28)}" fill="{g}"/>')
    out.append(strokes(D.nid(), blob(cx, cy, r, r, seed, 0.01, 28), (cx - r, cy - r, cx + r, cy + r), ["#FFF0B0", "#A8741A"], seed, n=int(r), angle=-40, length=(r * 0.2, r * 0.6), width=(0.8, r * 0.05), opacity=(0.15, 0.35), curve=0.6))
    # engraved bands
    for k in (-1, 1):
        out.append(f'<path d="M {cx - r * 0.98:.1f} {cy + k * r * 0.1:.1f} Q {cx:.1f} {cy + k * r * 0.1 + r * 0.38:.1f} {cx + r * 0.98:.1f} {cy + k * r * 0.1:.1f}" stroke="#8A5A14" stroke-width="1.3" fill="none" opacity="0.7"/>')
    out.append(f'<path d="M {cx - r * 0.98:.1f} {cy:.1f} Q {cx:.1f} {cy + r * 0.38:.1f} {cx + r * 0.98:.1f} {cy:.1f}" stroke="#FFF4C0" stroke-width="1.0" fill="none" opacity="0.6"/>')
    out.append(f'<path d="{blob(cx - r * 0.36, cy - r * 0.4, r * 0.24, r * 0.14, seed + 3, 0.1, 8, -35)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(ink(blob(cx, cy, r, r, seed, 0.01, 28), "#5A3A0A", 1.4, seed, 1, 0.7))
    return "".join(out)


def linden_leaf(D, x, y, s, ang, seed, pal=LEAF):
    """Heart-shaped lime (linden) leaf hanging from (x, y) on a short stalk."""
    pts = []
    for i in range(30):
        t = 2 * math.pi * i / 30
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((hx / 16, -hy / 16))
    pts = [(px * s * 0.95, py * s * 1.05 + s * 1.1) for px, py in pts]
    pts = T(pts, x, y, 1, False, ang)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.14, angle=ang + 60, n=int(s * 0.6) + 6, inkw=1.1, inkc="#1A3A16", inkop=0.6, hi=0.35)]
    a, b = T([(0, s * 0.2)], x, y, 1, False, ang)[0], T([(0, s * 2.0)], x, y, 1, False, ang)[0]
    out.append(pline([(x, y), a, b], lt(pal[0], 0.3), max(1, s * 0.07), seed, 0.7, 1))
    for sg in (-1, 1):
        for k in (0.6, 1.1):
            p0 = T([(0, s * k)], x, y, 1, False, ang)[0]
            p1 = T([(sg * s * 0.6, s * (k + 0.25))], x, y, 1, False, ang)[0]
            out.append(pline([p0, p1], lt(pal[0], 0.3), max(0.8, s * 0.05), seed + k * 10, 0.55, 1))
    return "".join(out)


def stone_well(D, cx, cy, rx, ry, depth, seed):
    rnd = random.Random(seed)
    out = [cast(D, cx + 16, cy + depth + ry * 0.4, rx * 1.1, ry * 0.6, strength=0.45, seed=seed)]
    # front wall of fitted stones
    wall = ell_pts(cx, cy, rx, ry, 0, 180, 24) + [(cx - rx, cy + depth)][::-1]
    body = [(cx + rx, cy)] + [(cx + rx, cy + depth)] + ell_pts(cx, cy + depth, rx, ry, 0, 180, 24)[1:-1] + [(cx - rx, cy + depth), (cx - rx, cy)] + ell_pts(cx, cy, rx, ry, 180, 360, 24)[1:-1][:0]
    body = [(cx + rx, cy), (cx + rx, cy + depth)] + ell_pts(cx, cy + depth, rx, ry, 0, 180, 24)[1:-1] + [(cx - rx, cy + depth), (cx - rx, cy)] + ell_pts(cx, cy, rx, ry, 180, 0, 24)[1:-1][::-1][::-1]
    body = [(cx + rx, cy), (cx + rx, cy + depth)] + ell_pts(cx, cy + depth, rx, ry, 0, 180, 24)[1:-1] + [(cx - rx, cy + depth), (cx - rx, cy)] + ell_pts(cx, cy, rx, ry, 180, 0, 24)[1:-1]
    d = smooth_closed(body)
    out.append(f'<path d="{d}" fill="{STONE[1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    st = []
    rows = 4
    for r in range(rows):
        y0 = cy + depth * r / rows
        n = 9
        for j in range(n):
            u0 = (j + (r % 2) * 0.5) / n
            u1 = (j + 1 + (r % 2) * 0.5) / n
            a0, a1 = math.pi * (1 - u0), math.pi * (1 - u1)
            xa, xb = cx + rx * math.cos(a0), cx + rx * math.cos(a1)
            ya, yb = y0 + ry * math.sin(a0), y0 + ry * math.sin(a1)
            hgt = depth / rows
            pts = [(xa + 1.5, ya + 2), (xb - 1.5, yb + 2), (xb - 1.5, yb + hgt - 1.5), (xa + 1.5, ya + hgt - 1.5)]
            mid = (xa + xb) / 2
            lit = 0.5 + 0.5 * math.cos(math.radians((mid - cx) / rx * 80 + 40))
            c = mix(mix(STONE[2], STONE[0], lit), rnd.choice(["#B8A890", "#9A9AA0", "#C0B0A0", "#A89880"]), 0.3)
            st.append(f'<path d="{hg.org_poly(pts, seed + r * 20 + j, 0.6, 8, 3)}" fill="{c}"/>')
            st.append(f'<path d="{hg.org_poly(pts, seed + r * 20 + j, 0.6, 8, 3)}" fill="none" stroke="#3A3028" stroke-width="1.2" opacity="0.55"/>')
            st.append(f'<path d="M {xa + 4:.1f} {ya + 4:.1f} L {xb - 4:.1f} {yb + 4:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.3"/>')
            if rnd.random() < 0.35:
                st.append(f'<path d="{blob((xa + xb) / 2, (ya + yb) / 2 + hgt * 0.5, 7, 4, seed + j + r, 0.3, 8)}" fill="#5A7A3A" opacity="0.65"/>')
    g = D.lin([(0, "#000000", 0.45), (0.3, "#000000", 0.0), (0.75, "#000000", 0.05), (1, "#000000", 0.55)], 0, 0, 1, 0)
    st.append(f'<rect x="{cx - rx:.1f}" y="{cy - ry:.1f}" width="{2 * rx:.1f}" height="{depth + 2 * ry:.1f}" fill="{g}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(ink(d, INK, 1.8, seed, 1, 0.6))
    # rim: a ring of capstones (top surface)
    ring_o = ell_pts(cx, cy, rx + 6, ry + 4, 0, 360, 40)
    ring_i = ell_pts(cx, cy + 2, rx - 18, ry - 10, 0, 360, 40)
    rd = smooth_closed(ring_o) + " " + smooth_closed(ring_i)
    out.append(f'<path d="{rd}" fill-rule="evenodd" fill="{STONE[0]}"/>')
    rcid = D.clip(f'<path d="{rd}" clip-rule="evenodd"/>')
    caps = []
    for j in range(16):
        a = 2 * math.pi * j / 16
        caps.append(f'<path d="M {cx + math.cos(a) * (rx - 20):.1f} {cy + 2 + math.sin(a) * (ry - 11):.1f} L {cx + math.cos(a) * (rx + 8):.1f} {cy + math.sin(a) * (ry + 5):.1f}" stroke="#6A6058" stroke-width="1.4" opacity="0.6"/>')
    caps.append(strokes(D.nid(), rd, (cx - rx - 8, cy - ry - 6, cx + rx + 8, cy + ry + 6), ["#FFFFFF", "#8A8070", "#C8C0B0"], seed, n=60, angle=0, length=(10, 30), width=(1, 3), opacity=(0.2, 0.45)))
    caps.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 6, rx + 6, ry + 4, 0, 360, 40))}" fill="#000000" opacity="0.0"/>')
    out.append(f'<g {rcid}>{"".join(caps)}</g>')
    out.append(ink(smooth_closed(ring_o), INK, 1.6, seed + 1, 1, 0.6))
    # the dark water inside, with a reflection of the evening sky and a ripple
    wd = smooth_closed(ring_i)
    out.append(f'<path d="{wd}" fill="{D.lin([(0, "#0A1418"), (0.6, "#1E3A40"), (1, "#3A5A5A")])}"/>')
    wcid = D.clip(f'<path d="{wd}"/>')
    wa = [f'<path d="{blob(cx + 20, cy + 8, rx * 0.5, ry * 0.3, seed, 0.1, 12)}" fill="#F2D8A0" opacity="0.25"/>']
    for k in range(3):
        wa.append(f'<path d="{smooth_closed(ell_pts(cx - 30, cy + 6, 12 + k * 14, 3 + k * 4, 0, 360, 20))}" fill="none" stroke="#C8E0D8" stroke-width="1.2" opacity="{0.5 - k * 0.13:.2f}"/>')
    wa.append(f'<path d="{smooth_closed(ell_pts(cx, cy - ry * 0.55 + 4, rx - 18, ry * 0.4, 180, 360, 20))}" fill="#000000" opacity="0.45"/>')
    out.append(f'<g {wcid}>{"".join(wa)}</g>')
    out.append(ink(wd, "#2A2018", 1.4, seed + 2, 1, 0.6))
    return "".join(out)


@design("the-frog-prince")
def frog_prince():
    D = Doc2("ft-fp")
    out = [sky(D, [(0, "#1E3A30"), (0.4, "#3E6A4A"), (0.75, "#A8B880"), (1, "#E8D8A0")], 1, 600, ["#2E5A3E", "#5A8A5A", "#C8C890"], 60)]
    out.append(soft_glow(D, 300, 300, 300, "#FFE8A8", 0.45))
    # light shafts through the old lime tree
    for k, x in enumerate((180, 260, 360, 430)):
        out.append(f'<path d="M {x - 10} 0 L {x + 14} 0 L {x + 80 + k * 10} 600 L {x + 30 + k * 10} 600 Z" fill="#FFF4C8" opacity="0.08"/>')
    # background: trunks and shrubbery
    rnd = random.Random(3)
    out.append(gnarled_trunk(D, 40, 440, -20, 104, 5, ("#8A8A6A", "#4E5440", "#1E2418"), lean=0.08, rim="#FFE8A0", rim_side=1, branches=2))
    out.append(dab_crown(D, 520, 330, 120, 90, [("#7AA868", "#3E6A3A", "#1E3A22"), ("#9AC07A", "#5A8A48", "#2A4A26")], 4, n=160, size=(6, 13), inkw=0))
    out.append(hill(D, [(-20, 420), (140, 410), (300, 418), (460, 406), (620, 414)], 620, ("#8AAA60", "#5A7E3E", "#2E4A22"), 6, inkw=0, sop=(0.15, 0.4)))
    out.append(grass(7, (0, 410, 600, 600), ["#3E6A2E", "#6A9A48", "#9AC060", "#2A4A1E"], 260, (8, 22)))
    # forget-me-nots in the grass
    for k in range(26):
        x, y = rnd.uniform(30, 570), rnd.uniform(430, 590)
        if 150 < x < 450 and y < 560:
            continue
        for j in range(5):
            a = math.radians(j * 72)
            out.append(f'<circle cx="{x + math.cos(a) * 3:.1f}" cy="{y + math.sin(a) * 3:.1f}" r="2.4" fill="#7AAAE8"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="#F6E06A"/>')
    # the well
    out.append(stone_well(D, 300, 352, 164, 48, 100, 8))
    # frog on the rim, golden ball at rest on the far side
    out.append(golden_ball(D, 384, 330, 30, 9))
    out.append(frog(D, 212, 344, 1.15, 10))
    # lime leaves hanging into the top corners
    for k, (x, y, s, a) in enumerate(((40, -6, 26, 20), (92, 10, 22, -10), (20, 60, 20, 40), (150, -8, 18, 5),
                                      (560, -6, 26, -20), (506, 8, 22, 10), (582, 66, 20, -40), (452, -10, 18, -6))):
        out.append(linden_leaf(D, x, y, s, a, 20 + k, LEAF if k % 2 else MOSS))
    out.append(taper([(0, 10), (100, 18), (160, 6)], 4, 2, "#3A2A1A"))
    out.append(taper([(600, 10), (500, 18), (440, 6)], 4, 2, "#3A2A1A"))
    # lettering
    out.append(gilt(D, 300, 150, "The Frog Prince", SERIF_IT, 62, max_w=420, seed=30, deboss="#0A1A10", dop=0.7))
    out.append(tx(300, 186, "A TALE FROM THE BROTHERS GRIMM", CINZEL, 16, "#FFF4D0", ls=3, max_w=380))
    out.append(tx(301, 543, "“In olden times, when wishing still helped…”", SERIF_IT, 26, "#0E2A10", max_w=440, op=0.5))
    out.append(tx(300, 541, "“In olden times, when wishing still helped…”", SERIF_IT, 26, "#FFF8E8", max_w=440))
    return finish_b(D, out, 31, INK, 0.6)


# ================================================================ 5. aladdin — the old lamp beneath a Moorish arch
def zellige(D, seed, base="#F2E8D2"):
    """Moroccan tile field: eight-point stars and crosses in teal, cobalt, saffron and terracotta."""
    c = 50
    cols = ["#1E6A72", "#24386A", "#D2A033", "#B0482A"]
    m = [f'<rect width="{c}" height="{c}" fill="{base}"/>']
    for (ox, oy, k) in ((0, 0, 0), (c, 0, 0), (0, c, 0), (c, c, 0), (c / 2, c / 2, 1)):
        col = cols[0] if k == 0 else cols[1]
        s = c * 0.32
        sq1 = [(ox - s, oy - s), (ox + s, oy - s), (ox + s, oy + s), (ox - s, oy + s)]
        sq2 = rot(sq1, ox, oy, 45)
        m.append(f'<path d="{pd(sq1)}" fill="{col}"/><path d="{pd(sq2)}" fill="{col}"/>')
        m.append(f'<circle cx="{ox}" cy="{oy}" r="{s * 0.5:.1f}" fill="{cols[2]}"/>')
        m.append(f'<circle cx="{ox}" cy="{oy}" r="{s * 0.2:.1f}" fill="{base}"/>')
    for (ox, oy) in ((c / 2, 0), (0, c / 2), (c, c / 2), (c / 2, c)):
        m.append(f'<path d="{pd([(ox, oy - 6), (ox + 6, oy), (ox, oy + 6), (ox - 6, oy)])}" fill="{cols[3]}"/>')
    pat = D.pattern(c, c, "".join(m))
    return pat


def oil_lamp(D, cx, base, s, seed):
    """Old brass oil lamp (the 'Aladdin' shape): low boat-shaped body, long spout, loop handle, domed lid."""
    def L(pts):
        return T(pts, cx, base, s)
    out = [cast(D, cx + 10 * s, base + 2, 110 * s, 10 * s, strength=0.55, seed=seed)]
    pal = ("#FFF0A8", "#D2A040", "#6A4410")
    # foot
    out.append(painted(D, L([(-30, 0), (-24, -10), (24, -10), (30, 0)]), pal, seed, sk=0.25, angle=0, n=8, inkw=1.4, hi=0.5))
    out.append(painted(D, L([(-14, -10), (-10, -18), (10, -18), (14, -10)]), pal, seed + 1, sk=0.25, angle=0, n=6, inkw=1.2, hi=0.5))
    # handle loop (right)
    hpath = L([(54, -40), (88, -52), (98, -34), (84, -20), (60, -24)])
    out.append(taper(catmull(hpath, 6), 9 * s, 7 * s, pal[2]))
    out.append(taper(catmull(hpath, 6), 5 * s, 4 * s, pal[1]))
    out.append(taper(catmull(hpath[:3], 6), 2 * s, 1.2 * s, pal[0], 0.9))
    # body + spout as one swelling form
    body = L([(-150, -60), (-140, -64), (-120, -58), (-96, -48), (-72, -46), (-50, -54), (-20, -58), (20, -58), (50, -52), (68, -40), (66, -26), (50, -18),
              (20, -14), (-20, -14), (-50, -20), (-80, -32), (-110, -44), (-138, -54)])
    out.append(painted(D, body, pal, seed + 2, sdir=(0.3, 1), sk=0.2, angle=-8, n=60, inkw=1.8, inkc="#3A2408", hi=0.5, hik=0.1))
    g = D.lin([(0, "#3A2408", 0), (0.55, "#3A2408", 0.0), (1, "#3A2408", 0.45)], 0, 0, 0, 1)
    out.append(f'<path d="{smooth_closed(body)}" fill="{g}"/>')
    # engraved arabesque band and fluting
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    inner = [pline(L([(-60, -46), (-20, -42), (20, -42), (58, -38)]), "#7A5210", 1.4, seed, 0.8, 1)]
    for k in range(7):
        x = -40 + k * 14
        inner.append(pline(L([(x, -44), (x + 4, -36), (x, -28), (x - 4, -36), (x, -44)]), "#8A5A14", 1.1, seed + k, 0.7, 1))
        inner.append(f'<circle cx="{L([(x + 7, -36)])[0][0]:.1f}" cy="{L([(x + 7, -36)])[0][1]:.1f}" r="{1.4 * s:.1f}" fill="#8A5A14"/>')
    inner.append(taper(L([(-130, -60), (-100, -52), (-60, -54), (-20, -60), (30, -58), (56, -50)]), 2, 4 * s, "#FFFBE0", 0.85))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # domed lid with finial
    lid = L([(-26, -58), (-22, -72), (-10, -82), (10, -82), (22, -72), (26, -58)])
    out.append(painted(D, lid, pal, seed + 3, sdir=(0.5, 0.6), sk=0.2, angle=-60, n=14, inkw=1.6, inkc="#3A2408", hi=0.55))
    out.append(painted(D, L([(-4, -82), (-6, -92), (0, -100), (6, -92), (4, -82)]), pal, seed + 4, sk=0.2, angle=-90, n=4, inkw=1.2, inkc="#3A2408", hi=0.6))
    out.append(f'<circle cx="{L([(0, -102)])[0][0]:.1f}" cy="{L([(0, -102)])[0][1]:.1f}" r="{3 * s:.1f}" fill="{pal[1]}" stroke="#3A2408" stroke-width="1"/>')
    # spout tip
    tx_, ty_ = L([(-146, -62)])[0]
    out.append(f'<ellipse cx="{tx_:.1f}" cy="{ty_:.1f}" rx="{5 * s:.1f}" ry="{3 * s:.1f}" fill="#2A1A08"/>')
    return "".join(out), (tx_, ty_)


def smoke_ribbon(D, pts, seed, w0=4, w1=26, col="#E8E0F8"):
    path = catmull(pts, 8)
    out = [taper(path, w0, w1, col, 0.22), taper(path, w0 * 0.5, w1 * 0.4, "#FFFFFF", 0.3)]
    rnd = random.Random(seed)
    for i in range(0, len(path), 3):
        px, py = path[i]
        t = i / len(path)
        if t > 0.35:
            out.append(sparkle(px + rnd.uniform(-w1, w1) * t, py + rnd.uniform(-10, 10), rnd.uniform(2, 5) * t + 1, "#FFF2C0", rnd.uniform(0.5, 1)))
    return "".join(out)


@design("aladdin")
def aladdin():
    D = Doc2("ft-al")
    pat = zellige(D, 3)
    out = [f'<rect width="600" height="600" fill="{pat}"/>']
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0.1), (1, "#1A0A04", 0.5)], r=0.75)}"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (0, 0, 600, 600), ["#FFFFFF", "#3A2A1A"], 3, n=200, angle=-80, length=(10, 40), width=(1, 3), opacity=(0.06, 0.16)))
    # the arch opening: Moorish ogee, carved plaster surround
    ap = ogee_pts(124, 476, 250, 76, 620, 10)
    sur = ogee_pts(100, 500, 250, 50, 620, 10)
    out.append(f'<path d="{smooth_closed(sur)}" fill="#F4EAD8"/>')
    scid = D.clip(f'<path d="{smooth_closed(sur)} {smooth_closed(ap)}" clip-rule="evenodd"/>')
    carve = []
    for k in range(80):
        t = k / 79
        i = int(t * (len(ap) - 1))
        x, y = ap[i]
        carve.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="none" stroke="#C8B48A" stroke-width="1.4"/>')
    carve.append(ink(smooth_open(ogee_pts(112, 488, 250, 63, 620, 10)), "#B0482A", 2.4, 4, 1, 0.8))
    out.append(f'<g {scid}>{"".join(carve)}</g>')
    out.append(ink(smooth_open(sur), "#7A5A3A", 1.8, 5, 1, 0.7))
    # the night inside the arch
    cid = D.clip(f'<path d="{smooth_closed(ap)}"/>')
    n = [f'<rect width="600" height="600" fill="{D.lin([(0, "#08102E"), (0.5, "#16306A"), (0.78, "#2E5E8A"), (1, "#5A8AA0")])}"/>']
    n.append(stars_field(5, (120, 80, 480, 360), 110))
    n.append(soft_glow(D, 300, 140, 70, "#FFF2C8", 0.45))
    n.append(f'<path d="{blob(300, 140, 22, 22, 6, 0.02, 20)}" fill="#FFF6D8"/>')
    n.append(f'<path d="{blob(310, 132, 20, 20, 7, 0.02, 20)}" fill="#0E1C48"/>')
    # city of domes and minarets
    city = "#1A2E5A"
    for (x, w, h, dome) in ((150, 46, 70, 1), (196, 30, 104, 2), (236, 64, 60, 1), (300, 40, 118, 2), (346, 70, 74, 1), (408, 34, 96, 2), (444, 50, 56, 1)):
        b = 430
        out_ = [(x - w / 2, b), (x - w / 2, b - h), (x + w / 2, b - h), (x + w / 2, b)]
        n.append(f'<path d="{pd(out_)}" fill="{city}"/>')
        if dome == 1:
            n.append(f'<path d="M {x - w / 2 + 3:.1f} {b - h:.1f} C {x - w / 2:.1f} {b - h - w * 0.6:.1f} {x - 4:.1f} {b - h - w * 0.55:.1f} {x:.1f} {b - h - w * 0.85:.1f} C {x + 4:.1f} {b - h - w * 0.55:.1f} {x + w / 2:.1f} {b - h - w * 0.6:.1f} {x + w / 2 - 3:.1f} {b - h:.1f} Z" fill="{city}"/>')
        else:
            n.append(f'<path d="{pd([(x - w / 2 + 4, b - h), (x, b - h - 34), (x + w / 2 - 4, b - h)])}" fill="{city}"/>')
            n.append(f'<rect x="{x - w / 2 - 3:.1f}" y="{b - h + 10:.1f}" width="{w + 6:.1f}" height="4" fill="{city}"/>')
        n.append(f'<path d="M {x:.1f} {b - h - (w * 0.85 if dome == 1 else 34):.1f} l 0 -10" stroke="{city}" stroke-width="2"/>')
        rnd = random.Random(int(x))
        for j in range(rnd.randint(1, 3)):
            wx, wy = x + rnd.uniform(-w / 2 + 6, w / 2 - 10), b - rnd.uniform(14, h - 10)
            n.append(f'<path d="M {wx:.1f} {wy + 8:.1f} L {wx:.1f} {wy + 2:.1f} Q {wx + 2.5:.1f} {wy - 1:.1f} {wx + 5:.1f} {wy + 2:.1f} L {wx + 5:.1f} {wy + 8:.1f} Z" fill="#FFC860"/>')
            n.append(soft_glow(D, wx + 2.5, wy + 4, 10, "#FFC860", 0.5))
    n.append(f'<rect x="0" y="380" width="600" height="60" fill="{D.lin([(0, "#5A8AA0", 0), (1, "#08102E", 0.6)])}"/>')
    out.append(f'<g {cid}>{"".join(n)}</g>')
    out.append(ink(smooth_closed(ap), "#3A2410", 2, 8, 1, 0.75))
    # marble ledge
    out.append(painted(D, rect_pts(-10, 444, 610, 470, 30, 9, 0.4), ("#FFFFFF", "#ECE2D0", "#A8988A"), 9, sdir=(0.2, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(painted(D, rect_pts(-10, 470, 610, 620, 30, 10, 0.4), ("#F8F0E0", "#E2D6C0", "#9A8A78"), 10, sdir=(0.2, 1), sk=0.08, angle=0, n=40, inkw=1.4, hi=0.2))
    for k in range(6):
        out.append(pline([(k * 110 - 20, 480 + k * 7), (k * 110 + 40, 500 + k * 4), (k * 110 + 90, 520)], "#B8A898", 1.2, k, 0.4, 1))
    # tassel cushion under the lamp (ruby velvet)
    cush = [(176, 452), (190, 434), (300, 428), (410, 434), (424, 452), (410, 466), (300, 470), (190, 466)]
    out.append(cast(D, 306, 466, 140, 10, strength=0.45, seed=11))
    out.append(painted(D, cush, ("#E2687A", "#A8203A", "#5A0A1A"), 11, sdir=(0.3, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.45))
    for (tx_, ty_) in ((182, 452), (418, 452)):
        out.append(f'<path d="M {tx_} {ty_} l -4 18 l 8 0 Z" fill="{GOLD[1]}"/><circle cx="{tx_}" cy="{ty_}" r="4" fill="{GOLD[0]}"/>')
    lamp, (sx, sy) = oil_lamp(D, 324, 436, 1.0, 12)
    out.append(lamp)
    out.append(smoke_ribbon(D, [(sx - 2, sy - 4), (sx - 14, sy - 34), (sx + 6, sy - 64), (sx + 46, sy - 84), (sx + 110, sy - 92), (sx + 170, sy - 110), (sx + 200, sy - 140)], 13))
    # lettering
    out.append(gilt(D, 300, 244, "ALADDIN", CINZEL, 48, ls=6, max_w=236, seed=14, deboss="#040818", dop=0.8))
    out.append(tx(300, 272, "THE THOUSAND AND ONE NIGHTS", CINZEL, 15, "#F2E2B8", ls=2, max_w=300))
    out.append(tx(300, 528, "“New lamps for old!”", SERIF_IT, 44, "#6A1A24", max_w=420))
    return finish_b(D, out, 15, INK, 0.6)


# ================================================================ 6. the tortoise and the hare — Aesop's plate
def tortoise(D, ox, oy, s, seed, flip=False):
    """A tortoise plodding to the right; (ox, oy) = ground under its middle; s=1 ~ 130 px long."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    skin = ("#C8B88A", "#8A7A52", "#4A3E24")
    out = [cast(D, *L([(0, 2)])[0], 70 * s, 7 * s, strength=0.45, seed=seed)]
    # far legs
    out.append(painted(D, L([(-34, -12), (-30, 0), (-20, 1), (-22, -12)]), ("#9A8A62", "#6A5A3A", "#3A2E1A"), seed, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.2))
    out.append(painted(D, L([(26, -12), (34, 0), (44, 1), (38, -14)]), ("#9A8A62", "#6A5A3A", "#3A2E1A"), seed + 1, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.2))
    # head and neck, stretched out
    neck = L([(40, -22), (58, -30), (72, -40), (84, -42), (92, -38), (94, -32), (88, -26), (76, -24), (60, -16), (44, -12)])
    out.append(painted(D, neck, skin, seed + 2, sdir=(0.2, 1), sk=0.2, angle=-20, n=16, inkw=1.5, hi=0.4))
    for k in range(4):
        out.append(pline(L([(50 + k * 7, -26 + k * 2), (52 + k * 7, -16 + k)]), skin[2], 1, seed + k, 0.5, 1))
    ex, ey = L([(84, -37)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#1A120A"/><circle cx="{ex - 0.8:.1f}" cy="{ey - 0.9:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    out.append(pline(L([(94, -32), (86, -30), (80, -31)]), "#2A1E10", 1.2, seed, 0.85, 1))
    out.append(pline(L([(78, -41), (86, -42)]), skin[2], 1.2, seed, 0.6, 1))
    # shell: high dome with a marginal rim
    shell = L([(-54, -12), (-52, -30), (-40, -50), (-18, -64), (8, -66), (32, -56), (48, -36), (52, -14), (30, -10), (0, -9), (-30, -10)])
    pal = ("#C8A060", "#8A5E2A", "#3E2A12")
    out.append(painted(D, shell, pal, seed + 3, sdir=(0.4, 1), sk=0.18, angle=-60, n=30, inkw=1.8, hi=0.45))
    cid = D.clip(f'<path d="{smooth_closed(shell)}"/>')
    inner = []
    # scutes: vertebral row along the top, costal row beneath, marginals at the rim
    vert = [(-30, -50), (-4, -60), (22, -52)]
    for k, (vx, vy) in enumerate(vert):
        hexp = L([(vx - 12, vy - 4), (vx, vy - 10), (vx + 12, vy - 4), (vx + 12, vy + 8), (vx, vy + 12), (vx - 12, vy + 8)])
        inner.append(f'<path d="{smooth_closed(hexp)}" fill="#E2B870" opacity="0.6"/>')
        inner.append(ink(smooth_closed(hexp), pal[2], 1.4, seed + k, 1, 0.75))
        sm = L([(vx - 6, vy - 1), (vx, vy - 4), (vx + 6, vy - 1), (vx + 6, vy + 5), (vx, vy + 7), (vx - 6, vy + 5)])
        inner.append(ink(smooth_closed(sm), pal[2], 1, seed + k + 5, 1, 0.45))
    for k, (vx, vy) in enumerate([(-42, -28), (-16, -34), (10, -34), (36, -26)]):
        hexp = L([(vx - 12, vy - 6), (vx + 12, vy - 8), (vx + 14, vy + 6), (vx + 10, vy + 14), (vx - 10, vy + 14), (vx - 14, vy + 4)])
        inner.append(f'<path d="{smooth_closed(hexp)}" fill="#B88444" opacity="0.5"/>')
        inner.append(ink(smooth_closed(hexp), pal[2], 1.3, seed + k + 9, 1, 0.7))
    inner.append(f'<path d="{smooth_closed(L([(-56, -12), (52, -14), (52, -20), (-56, -18)]))}" fill="#6A4A22" opacity="0.6"/>')
    for k in range(10):
        x = -50 + k * 11
        inner.append(pline(L([(x, -22), (x - 1, -10)]), pal[2], 1.2, seed + k, 0.7, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # near legs: stumpy, scaly, with claws
    for (lx, k) in ((-30, 0), (30, 1)):
        leg = L([(lx - 9, -14), (lx - 10, -2), (lx - 7, 1), (lx + 9, 1), (lx + 10, -4), (lx + 8, -16)])
        out.append(painted(D, leg, skin, seed + 7 + k, sdir=(0.5, 0.5), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.35))
        for j in range(3):
            c0 = L([(lx - 5 + j * 6, 0)])[0]
            out.append(f'<path d="M {c0[0]:.1f} {c0[1]:.1f} l {2 * s * (-1 if flip else 1):.1f} {3 * s:.1f}" stroke="#2A1E10" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(taper(L([(-54, -14), (-62, -10), (-66, -6)]), 4 * s, 1, skin[1]))
    return "".join(out)


def hare_asleep(D, ox, oy, s, seed, flip=False):
    """A brown hare curled up asleep, facing right (flip -> left); (ox, oy) = ground under its middle."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    pal = FUR
    out = [cast(D, *L([(0, 2)])[0], 62 * s, 7 * s, strength=0.45, seed=seed)]
    body = L([(-52, -8), (-56, -26), (-44, -44), (-20, -54), (10, -52), (32, -42), (44, -28), (46, -12), (36, -2), (-30, 0)])
    out.append(painted(D, body, pal, seed, sdir=(0.3, 1), sk=0.2, angle=-30, n=60, slen=(6, 16), sw=(0.6, 1.6),
                       cols=["#F2DCB4", "#8A6038", "#C49868", "#5A3C22"], inkw=1.6, hi=0.45))
    out.append(f'<path d="{smooth_closed(L([(-20, -2), (10, -6), (36, -4), (30, 1), (-10, 2)]))}" fill="#F6EAD2" opacity="0.85"/>')
    # haunch
    out.append(pline(L([(-44, -12), (-40, -34), (-24, -42), (-10, -36), (-6, -18)]), pal[2], 1.4, seed, 0.6, 1))
    # tail tuft
    out.append(f'<path d="{blob(*L([(-56, -28)])[0], 7 * s, 6 * s, seed, 0.2, 10)}" fill="#FFFFFF"/>')
    # head resting on the forepaws
    head = L([(28, -34), (44, -40), (58, -36), (66, -24), (62, -14), (48, -10), (34, -14), (26, -22)])
    out.append(painted(D, head, pal, seed + 1, sdir=(0.3, 1), sk=0.2, angle=-20, n=20, slen=(4, 10), sw=(0.5, 1.2), inkw=1.5, hi=0.45))
    out.append(painted(D, L([(40, -8), (62, -10), (70, -6), (60, -2), (40, -2)]), pal, seed + 2, sk=0.2, angle=0, n=6, inkw=1.3, hi=0.3))
    # long ears laid back along the body
    for k, (dy, c) in enumerate(((0, pal), (5, ("#C8A07A", "#8A6440", "#4A3420")))):
        ear = L([(34, -38 - dy), (14, -50 - dy), (-12, -58 - dy), (-26, -58 - dy), (-18, -52 - dy), (6, -44 - dy), (30, -32 - dy)])
        out.append(painted(D, ear, c, seed + 3 + k, sk=0.2, angle=180, n=10, inkw=1.4, hi=0.35))
        if k == 0:
            out.append(f'<path d="{smooth_closed(L([(26, -38), (6, -46), (-14, -53), (-4, -50), (14, -42)]))}" fill="#F2B8A8" opacity="0.7"/>')
        out.append(f'<path d="{smooth_closed(L([(-26, -58 - dy), (-18, -55 - dy), (-22, -52 - dy)]))}" fill="#2A1A10"/>')
    # closed eye, nose, whiskers
    out.append(pline(L([(46, -27), (50, -24), (55, -26)]), "#2A1A10", 1.6, seed, 0.9, 1))
    out.append(pline(L([(47, -25), (45, -22)]), "#2A1A10", 1, seed, 0.6, 1))
    nx_, ny_ = L([(66, -22)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{1.8 * s:.1f}" fill="#8A4A3A"/>')
    for k in range(3):
        out.append(pline(L([(64, -20 + k * 2), (78, -24 + k * 4)]), "#4A3420", 0.8, seed + k, 0.6, 1))
    return "".join(out)


def finish_post(D, x, base, h, seed):
    out = [painted(D, rect_pts(x - 3, base - h, x + 3, base, 8, seed, 0.3), WOOD, seed, sk=0.25, angle=-90, n=4, inkw=1.2, hi=0.4)]
    flag = [(x + 3, base - h + 2), (x + 34, base - h + 8), (x + 30, base - h + 16), (x + 36, base - h + 26), (x + 3, base - h + 22)]
    out.append(painted(D, flag, MADDER, seed + 1, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    out.append(f'<circle cx="{x}" cy="{base - h - 3}" r="3.4" fill="{GOLD[1]}" stroke="{GOLD[2]}" stroke-width="1"/>')
    return "".join(out)


def daisy(x, y, r, seed, col="#FFFFFF", centre="#F2C21C"):
    out = []
    for k in range(9):
        a = math.radians(k * 40 + seed * 7)
        out.append(f'<path d="{blob(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.45, r * 0.5, r * 0.18, seed + k, 0.1, 8, math.degrees(a))}" fill="{col}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.3:.1f}" fill="{centre}"/>')
    return "".join(out)


@design("the-tortoise-and-the-hare")
def tortoise_and_hare():
    D = Doc2("ft-th")
    out = [paper(D.nid(), "#F4EAD4", FLECK, 21)]
    out.append(blooms(4, ["#C8B48A", "#E8D8B8"], 7, op=(0.04, 0.09)))
    # oval vignette
    cx, cy, rx, ry = 300, 308, 236, 128
    ov = ell_pts(cx, cy, rx, ry, 0, 360, 60)
    cid = D.clip(f'<path d="{smooth_closed(ov)}"/>')
    sc = [sky(D, [(0, "#B8D4E0"), (0.6, "#E8EEDC"), (1, "#F6F0D8")], 2, 600, ["#FFFFFF", "#A8C8D8"], 30)]
    sc.append(puff_cloud(D, 200, 228, 120, 3, ("#FFFFFF", "#F6F2EA", "#C8D0D8"), op=0.95))
    sc.append(puff_cloud(D, 440, 210, 90, 4, ("#FFFFFF", "#F6F2EA", "#C8D0D8"), op=0.9))
    sc.append(hill(D, [(40, 304), (160, 284), (280, 296), (400, 276), (560, 292)], 470, ("#C8D8A0", "#A0B878", "#6A8A50"), 5, inkw=0, sop=(0.1, 0.3)))
    for k in range(9):
        sc.append(dab_crown(D, 120 + k * 46 + (k % 2) * 10, 292 - (k % 3) * 4, 14, 10, [("#9AB878", "#6A8A50", "#3E5A30")], 30 + k, n=14, size=(3, 6), inkw=0, base=False))
    sc.append(hill(D, [(40, 360), (200, 336), (340, 350), (560, 340)], 470, ("#B8D088", "#7EA05A", "#4A6A32"), 6, inkw=0, sop=(0.15, 0.35)))
    # the old oak and its shade where the hare naps
    sc.append(cast(D, 168, 392, 110, 20, color="#2A3A1A", strength=0.35, seed=7))
    sc.append(gnarled_trunk(D, 130, 392, 250, 30, 8, ("#9A7A5A", "#6A4A30", "#2E1E10"), lean=0.0, branches=2, roots=True, rim=None))
    sc.append(dab_crown(D, 140, 216, 110, 64, [("#9AC07A", "#5A8A48", "#2A4A26"), ("#B8D08A", "#7AA060", "#3E5A30")], 9, n=200, size=(6, 12), inkw=1.2))
    sc.append(hare_asleep(D, 176, 392, 1.0, 10))
    # the road, the plodding tortoise and the finishing post
    road = [(60, 470), (200, 430), (330, 410), (470, 392), (560, 380)]
    sc.append(taper(catmull(road, 8), 70, 18, "#E8D2A0", 0.9))
    sc.append(taper(catmull(road, 8), 20, 6, "#F6E6C0", 0.6))
    sc.append(finish_post(D, 474, 392, 60, 11))
    sc.append(grass(12, (40, 360, 560, 470), ["#6A8A40", "#9AB860", "#4A6A2A"], 220, (6, 16)))
    sc.append(tortoise(D, 350, 426, 0.92, 13))
    rnd = random.Random(14)
    for k in range(16):
        x, y = rnd.uniform(80, 540), rnd.uniform(400, 460)
        if 240 < x < 440 and y < 440:
            continue
        sc.append(daisy(x, y, 5, k))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(ink(smooth_closed(ov), "#5A3418", 2.6, 15, 1, 0.85))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx + 8, ry + 8, 0, 360, 60)), "#5A3418", 1.2, 16, 1, 0.7))
    # laurel sprays round the oval's foot
    out.append(laurel(D, [(250, cy + ry + 6), (170, cy + ry - 8), (110, cy + ry - 40), (80, cy + 80)], 13, MOSS, 17, side=1))
    out.append(laurel(D, [(350, cy + ry + 6), (430, cy + ry - 8), (490, cy + ry - 40), (520, cy + 80)], 13, MOSS, 18, side=-1))
    # lettering
    out.append(tx(300, 82, "AESOP’S FABLES", CINZEL, 17, "#8A5A2A", ls=6, max_w=300))
    out.append(tx(300, 134, "The Tortoise & the Hare", SERIF_IT, 46, "#3A2418", max_w=440))
    out.append(letters(D, 300, 506, "Slow and steady", SERIF_IT, 52, "#7A1E26", ["#9A2A2A", "#5E0E12", "#B8483A"], 20, max_w=440,
                       shadow="#E2CFA8", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 544, "wins the race.", SERIF_IT, 34, "#5A3418", max_w=300))
    return finish_b(D, out, 21, INK, 0.7)


# ================================================================ 7. cinderella — the palace stair inside a clock face at midnight
def glass_slipper(D, ox, oy, s, seed, ang=0):
    """Perrault's glass slipper, side view, toe to the left; (ox, oy) = under the ball of the foot."""
    def L(pts):
        return T(pts, ox, oy, s, False, ang)
    out = [cast(D, *L([(-4, 3)])[0], 66 * s, 6 * s, color="#0A1030", strength=0.45, seed=seed)]
    shoe = L([(-64, -2), (-66, -10), (-58, -20), (-40, -26), (-22, -26), (-6, -20), (10, -20), (24, -28), (38, -40), (46, -40),
              (48, -30), (46, -22), (44, -2), (40, -2), (38, -14), (30, -10), (14, -4), (-10, 0), (-40, 1)])
    d = smooth_closed(shoe)
    out.append(f'<path d="{d}" fill="{D.lin([(0, "#E8F4FF", 0.75), (0.5, "#A8C8F0", 0.55), (1, "#5A7AB8", 0.7)], 0, 0, 0, 1)}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # the foot opening (inside of the shoe seen through the glass)
    inner.append(f'<path d="{smooth_closed(L([(-26, -24), (-6, -19), (10, -19), (26, -26), (36, -36), (20, -24), (0, -14), (-20, -18)]))}" fill="#2A3A70" opacity="0.45"/>')
    # refraction bands and facets
    for k in range(5):
        x = -54 + k * 22
        inner.append(taper(L([(x, -2), (x + 6, -12), (x + 10, -22)]), 3 * s, 1, "#FFFFFF", 0.35))
    inner.append(taper(L([(-60, -12), (-44, -22), (-24, -24)]), 4 * s, 1.5, "#FFFFFF", 0.85))
    inner.append(taper(L([(28, -30), (40, -38)]), 3 * s, 1, "#FFFFFF", 0.8))
    inner.append(taper(L([(-50, -4), (-10, -3), (30, -9)]), 2 * s, 2 * s, "#DCEBFF", 0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#2A3A6A", 1.6, seed, 2, 0.75))
    # the heel, cut crystal
    heel = L([(36, -12), (44, -12), (44, 0), (36, 0)])
    out.append(f'<path d="{pd(heel)}" fill="#C8DCF8" opacity="0.8"/>')
    out.append(ink(pd(heel), "#2A3A6A", 1.2, seed, 1, 0.7))
    out.append(f'<path d="{pd(L([(38, -12), (40, 0)]), False)}" stroke="#FFFFFF" stroke-width="1.4"/>')
    # sparkles
    for (px, py, r) in ((-46, -22, 9), (34, -40, 7), (-8, -4, 5)):
        x, y = L([(px, py)])[0]
        out.append(sparkle(x, y, r * s, "#FFFFFF", 0.95))
        out.append(soft_glow(D, x, y, r * 2.5 * s, "#E8F0FF", 0.5))
    return "".join(out)


def mouse(D, ox, oy, s, seed, flip=False, pal=("#D8D4D0", "#9A949A", "#4A464E")):
    def L(pts):
        return T(pts, ox, oy, s, flip)
    out = [cast(D, *L([(0, 1)])[0], 16 * s, 2.5 * s, strength=0.4, seed=seed)]
    out.append(taper(catmull(L([(-14, -4), (-26, -2), (-34, -8), (-40, -4)]), 5), 2 * s, 0.8, "#C8A8A8"))
    body = L([(-16, -2), (-16, -10), (-8, -16), (4, -16), (12, -10), (18, -6), (14, -1), (0, 0)])
    out.append(painted(D, body, pal, seed, sk=0.2, angle=-30, n=10, inkw=1.1, inkc="#2A2630", hi=0.45))
    out.append(f'<path d="{blob(*L([(6, -16)])[0], 4.6 * s, 4.6 * s, seed, 0.05, 10)}" fill="{pal[1]}" stroke="#2A2630" stroke-width="0.8"/>')
    out.append(f'<path d="{blob(*L([(6, -16)])[0], 2.6 * s, 2.6 * s, seed, 0.05, 10)}" fill="#F2B8B8"/>')
    ex, ey = L([(12, -9)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.3 * s:.1f}" fill="#100A10"/>')
    nx_, ny_ = L([(18.5, -6)])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="{1.2 * s:.1f}" fill="#E890A0"/>')
    return "".join(out)


def pumpkin_plain(D, cx, cy, w, h, seed):
    from gouache import painted_pumpkin
    return painted_pumpkin(D.nid(), cx, cy, w, h, seed)


@design("cinderella")
def cinderella():
    D = Doc2("ft-ci")
    # midnight-blue ground scattered with gilt stars
    out = [sky(D, [(0, "#101A44"), (1, "#1E2A5E")], 1, 600, ["#24346A", "#0A1030"], 40)]
    rnd = random.Random(2)
    for _ in range(46):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 590)
        if math.hypot(x - 300, y - 262) < 214 or (90 < x < 510 and 456 < y < 566):
            continue
        out.append(star4(x, y, rnd.uniform(3, 7), "#E8C870", rnd.uniform(0.5, 0.9)))
    cx, cy, R = 300, 262, 196
    ring_in = R - 34
    # the scene inside the dial
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{ring_in}"/>')
    sc = [f'<rect width="600" height="600" fill="{D.lin([(0, "#0C1640"), (0.55, "#2A3E7E"), (1, "#5A6EA8")], 0, cy - ring_in, 0, cy + ring_in, "userSpaceOnUse")}"/>']
    sc.append(stars_field(3, (cx - ring_in, cy - ring_in, cx + ring_in, cy), 60))
    # palace: a pale facade with tall lit arched windows, high above the stair
    pal_y = 254
    sc.append(f'<path d="{pd([(140, pal_y), (140, 160), (460, 160), (460, pal_y)])}" fill="#C8CCE6"/>')
    sc.append(f'<path d="{pd([(140, 160), (460, 160), (460, 172), (140, 172)])}" fill="#A8AED0"/>')
    for k in range(9):
        x = 160 + k * 35
        sc.append(f'<path d="M {x:.1f} {pal_y - 6} L {x:.1f} 194 Q {x + 10:.1f} 178 {x + 20:.1f} 194 L {x + 20:.1f} {pal_y - 6} Z" fill="#FFD27A"/>')
        sc.append(soft_glow(D, x + 10, 220, 30, "#FFC860", 0.45))
        sc.append(f'<path d="M {x + 10:.1f} 186 L {x + 10:.1f} {pal_y - 6} M {x:.1f} 222 L {x + 20:.1f} 222" stroke="#C89A4A" stroke-width="1.4"/>')
        sc.append(f'<rect x="{x - 8:.1f}" y="172" width="5" height="{pal_y - 172}" fill="#E8ECF8"/>')
    for k in range(16):
        sc.append(f'<rect x="{140 + k * 20:.1f}" y="152" width="10" height="10" fill="#C8CCE6"/>')
    # the grand stair spilling down toward us
    steps = 9
    for i in range(steps):
        t = i / (steps - 1)
        y0 = pal_y + 4 + t ** 1.3 * 150
        h = 6 + 14 * t
        hw = 90 + 160 * t
        tread = [(cx - hw, y0), (cx + hw, y0), (cx + hw + 8, y0 + h * 0.35), (cx - hw - 8, y0 + h * 0.35)]
        riser = [(cx - hw - 8, y0 + h * 0.35), (cx + hw + 8, y0 + h * 0.35), (cx + hw + 8, y0 + h), (cx - hw - 8, y0 + h)]
        sc.append(f'<path d="{pd(riser)}" fill="{mix("#7A84B8", "#A8B0D8", t)}"/>')
        sc.append(f'<path d="{pd(tread)}" fill="{mix("#D8DCF0", "#F2F2FA", t)}"/>')
        sc.append(f'<path d="M {cx - hw:.1f} {y0:.1f} L {cx + hw:.1f} {y0:.1f}" stroke="#FFFFFF" stroke-width="1.4" opacity="0.8"/>')
        for k in range(3):
            vx = cx + rnd.uniform(-hw, hw)
            sc.append(pline([(vx, y0 + h * 0.4), (vx + rnd.uniform(-10, 10), y0 + h * 0.7), (vx + rnd.uniform(-14, 14), y0 + h)], "#6A74A8", 0.8, i * 5 + k, 0.5, 1))
    sc.append(f'<rect x="0" y="{pal_y}" width="600" height="200" fill="{D.lin([(0, "#0A1030", 0.35), (0.4, "#0A1030", 0.0), (1, "#0A1030", 0.25)])}"/>')
    # balustrades and lanterns
    for sg in (-1, 1):
        for i in range(12):
            t = i / 11
            x = cx + sg * (100 + 170 * t)
            y = pal_y + t ** 1.3 * 150
            sc.append(f'<path d="M {x - 3:.1f} {y:.1f} Q {x - 6:.1f} {y - 10:.1f} {x - 2:.1f} {y - 16 - 6 * t:.1f} L {x + 2:.1f} {y - 16 - 6 * t:.1f} Q {x + 6:.1f} {y - 10:.1f} {x + 3:.1f} {y:.1f} Z" fill="#B8BEDC"/>')
        sc.append(pline([(cx + sg * 98, pal_y - 18), (cx + sg * 190, pal_y + 50), (cx + sg * 272, pal_y + 128)], "#E8ECF8", 4, sg + 5, 1, 1))
        lx, ly = cx + sg * 104, pal_y - 30
        sc.append(f'<rect x="{lx - 2:.1f}" y="{ly:.1f}" width="4" height="14" fill="#2A2A40"/>')
        sc.append(soft_glow(D, lx, ly - 4, 26, "#FFD27A", 0.7))
        sc.append(f'<path d="{blob(lx, ly - 4, 5, 7, 3, 0.05, 10)}" fill="#FFE8A0"/>')
    # the slipper left behind on the stair, the pumpkin and two mice at the foot
    sc.append(glass_slipper(D, 250, 362, 1.25, 4, -4))
    sc.append(pumpkin_plain(D, 380, 362, 62, 44, 5))
    sc.append(mouse(D, 346, 388, 1.05, 6, flip=True))
    sc.append(mouse(D, 428, 392, 0.9, 7))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # dial ring: enamel chapter ring, Roman numerals, minute track, gilt bezel
    out.append(f'<circle cx="{cx}" cy="{cy + 6}" r="{R + 4}" fill="#000010" opacity="0.4"/>')
    ring = f'M {cx - R} {cy} A {R} {R} 0 1 0 {cx + R} {cy} A {R} {R} 0 1 0 {cx - R} {cy} Z M {cx - ring_in} {cy} A {ring_in} {ring_in} 0 1 1 {cx + ring_in} {cy} A {ring_in} {ring_in} 0 1 1 {cx - ring_in} {cy} Z'
    out.append(f'<path d="{ring}" fill-rule="evenodd" fill="#FBF4E2"/>')
    out.append(strokes(D.nid(), ring, (cx - R, cy - R, cx + R, cy + R), ["#FFFFFF", "#D8C8A8"], 8, n=120, angle=-30, length=(10, 30), width=(1, 3), opacity=(0.15, 0.35)))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = R - (13 if i % 5 == 0 else 8)
        out.append(f'<path d="M {cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0:.1f} L {cx + math.cos(a) * (R - 4):.1f} {cy + math.sin(a) * (R - 4):.1f}" stroke="#2A1A10" stroke-width="{2.2 if i % 5 == 0 else 1}"/>')
    romans = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    for i, rn in enumerate(romans):
        a = math.radians(i * 30 - 90)
        rr = R - 25
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        out.append(f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" {CINZEL} font-size="{17 if len(rn) < 4 else 14}" fill="#1A1210" transform="rotate({i * 30} {x:.1f} {y:.1f})">{rn}</text>')
    for r_, w_, c_ in ((R + 1, 7, GOLD[2]), (R + 1, 4, GOLD[1]), (R - 1, 1.4, GOLD[0]), (ring_in, 3.4, GOLD[1]), (ring_in, 1.2, GOLD[0])):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r_}" fill="none" stroke="{c_}" stroke-width="{w_}"/>')
    # both hands on XII: ornate gilt spade hands
    for (L_, w_, sp) in ((ring_in - 4, 5, 1.0), (ring_in - 48, 7, 1.4)):
        tip = cy - L_
        hand = [(cx - w_ * 0.4, cy + 18), (cx - w_ * 0.5, tip + 34 * sp), (cx - w_ * 1.8, tip + 22 * sp), (cx - w_ * 0.7, tip + 10 * sp), (cx, tip),
                (cx + w_ * 0.7, tip + 10 * sp), (cx + w_ * 1.8, tip + 22 * sp), (cx + w_ * 0.5, tip + 34 * sp), (cx + w_ * 0.4, cy + 18)]
        out.append(f'<path d="{pd(hand)}" fill="#1A1008" opacity="0.4" transform="translate(3 4)"/>')
        out.append(f'<path d="{pd(hand)}" fill="{gilt_fill(D, tip, cy + 18)}"/>')
        out.append(ink(pd(hand), "#5A3A0A", 1.2, 9, 1, 0.8))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{GOLD[1]}" stroke="#5A3A0A" stroke-width="1.4"/><circle cx="{cx - 3}" cy="{cy - 3}" r="3" fill="#FFF4C0"/>')
    # corner spandrels
    for (x, y, a) in ((40, 40, 45), (560, 40, 135), (560, 560, 225), (40, 560, 315)):
        out.append(fleuron(x + math.cos(math.radians(a)) * 18, y + math.sin(math.radians(a)) * 18, 14, GOLD[1], a + 90, 0.9))
    out.append(gilt(D, 300, 512, "Cinderella", SERIF_IT, 64, max_w=420, seed=10, deboss="#04081A", dop=0.8))
    out.append(tx(300, 539, "AT THE LAST STROKE OF MIDNIGHT", CINZEL, 15, "#E8D8B0", ls=3, max_w=380))
    return finish_b(D, out, 11, "#000010", 0.5)


# ================================================================ 8. the little mermaid — on the rock beneath the moon
def mermaid_from_behind(D, ox, oy, s, seed):
    """Andersen's little mermaid seated on a rock, seen from behind and to the side, looking right toward the ship;
    long ash-gold hair down her back, tail curled down to the left and dipping into the sea. (ox, oy) = hips."""
    def L(pts):
        return T(pts, ox, oy, s)
    out = []
    skin = ("#F8E6DA", "#D8B4A8", "#7A6070")
    hair = ("#F2E2B0", "#C8A86A", "#6A5434")
    tail = ("#8AD8C8", "#2E8A8A", "#0E3A44")
    # tail: from the hips sweeping down-left over the rock edge, fin in the water
    tl = L([(-16, -4), (-30, 10), (-52, 26), (-80, 38), (-104, 48), (-116, 60), (-112, 64), (-96, 58), (-74, 52), (-46, 42), (-20, 30), (0, 16), (14, 2)])
    out.append(painted(D, tl, tail, seed, sdir=(-0.2, 1), sk=0.2, angle=200, n=50, inkw=1.6, inkc="#0A2A30", hi=0.5, hik=0.08))
    cid = D.clip(f'<path d="{smooth_closed(tl)}"/>')
    sc = []
    rnd = random.Random(seed)
    for i in range(70):
        t = rnd.random()
        p = catmull(L([(0, 6), (-30, 24), (-70, 42), (-108, 56)]), 10)
        k = int(t * (len(p) - 1))
        px, py = p[k]
        px += rnd.uniform(-10, 10) * s
        py += rnd.uniform(-10, 10) * s
        r = (6 - 3 * t) * s
        sc.append(f'<path d="M {px - r:.1f} {py:.1f} Q {px - r:.1f} {py + r * 1.1:.1f} {px:.1f} {py + r * 1.1:.1f} Q {px + r:.1f} {py + r * 1.1:.1f} {px + r:.1f} {py:.1f}" stroke="{rnd.choice(["#BFF2E6", "#1E6A72", "#E8F8F0"])}" stroke-width="1" fill="none" opacity="0.65"/>')
    sc.append(taper(L([(-10, 0), (-40, 20), (-80, 36), (-104, 48)]), 4 * s, 1.5, "#E8FFF8", 0.55))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # tail fin (half in the water)
    fin = L([(-112, 58), (-132, 46), (-150, 44), (-140, 58), (-150, 74), (-128, 70), (-114, 64)])
    out.append(painted(D, fin, ("#B8F0E2", "#4EA8A0", "#145056"), seed + 1, sk=0.2, angle=180, n=10, inkw=1.3, inkc="#0A2A30", hi=0.4))
    for k in range(5):
        a = L([(-116, 62)])[0]
        b = L([(-136 - k * 3, 46 + k * 7)])[0]
        out.append(pline([a, b], "#E8FFF8", 0.9, seed + k, 0.6, 1))
    # back and shoulders (mostly hidden by the hair), arms
    back = L([(-14, -2), (-18, -24), (-20, -46), (-16, -62), (-6, -70), (8, -70), (16, -62), (18, -44), (16, -20), (14, 0)])
    out.append(painted(D, back, skin, seed + 2, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=14, inkw=1.4, inkc="#4A3040", hi=0.4))
    # right arm reaching down to the rock
    out.append(taper(catmull(L([(14, -62), (24, -46), (30, -26), (34, -6)]), 5), 7 * s, 5 * s, skin[1]))
    out.append(taper(catmull(L([(16, -60), (25, -44), (31, -24)]), 5), 2.4 * s, 1, skin[0], 0.8))
    out.append(f'<path d="{blob(*L([(35, -4)])[0], 5 * s, 3.6 * s, seed, 0.1, 8)}" fill="{skin[1]}"/>')
    # head turned right in profile-lost (cheek and ear just visible)
    hx, hy = L([(2, -84)])[0]
    out.append(f'<path d="{blob(hx, hy, 12.5 * s, 14 * s, seed + 3, 0.04, 14, 10)}" fill="{skin[1]}"/>')
    out.append(f'<path d="{smooth_closed(L([(10, -92), (16, -84), (14, -76), (8, -74)]))}" fill="{skin[0]}" opacity="0.9"/>')
    # hair: a long, slightly wind-lifted mass down the back to the waist, falling over the left shoulder
    hr = L([(-12, -96), (-2, -100), (10, -96), (14, -86), (12, -76), (16, -64), (20, -46), (16, -28), (10, -10), (4, 2), (-8, 4), (-20, -4), (-26, -20),
            (-32, -38), (-40, -52), (-48, -60), (-38, -62), (-28, -70), (-20, -84)])
    out.append(painted(D, hr, hair, seed + 4, sdir=(0.7, 0.2), sk=0.18, angle=95, n=70, slen=(14 * s, 40 * s), sw=(0.6, 1.8),
                       cols=["#FFF2C8", "#A88850", "#E2C88A", "#7A6038"], inkw=1.4, inkc="#4A3A20", hi=0.45, hik=0.08))
    for k in range(16):
        t = k / 15
        a = L([(-12 + 22 * t, -96 + 4 * t)])[0]
        b = L([(-34 + 40 * t + math.sin(k) * 4, -50 + 6 * t)])[0]
        c = L([(-24 + 30 * t + math.cos(k) * 5, -16)])[0]
        d_ = L([(-18 + 26 * t, 2)])[0]
        out.append(pline([a, b, c, d_], rnd.choice(["#FFF4D0", "#8A6E40", "#E8D090", "#6A5430"]), 1.3, seed + k, 0.6, 1))
    # a few loose locks lifted by the sea wind
    for k in range(3):
        a = L([(-26 - k * 6, -70 + k * 14)])[0]
        out.append(taper(catmull([a, (a[0] - 18 * s, a[1] - 6 * s), (a[0] - 34 * s, a[1] + 2 * s), (a[0] - 44 * s, a[1] - 8 * s)], 5), 3.4 * s, 0.6, hair[1], 0.9))
    # moonlight rim along the hair and shoulder
    out.append(ink(smooth_open(L([(-12, -96), (-20, -84), (-28, -70), (-40, -56)])), "#E8F2FF", 1.8, seed, 1, 0.75))
    # a pearl string wound in the hair
    for k in range(6):
        px, py = L([(-14 + k * 4, -90 + k * 1.2)])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.5 * s:.1f}" fill="#FFFFFF" stroke="#B8C0D0" stroke-width="0.5"/>')
    return "".join(out)


def tall_ship_lit(D, x, wl, s, seed):
    """A three-masted ship at night strung with coloured lanterns (the prince's birthday)."""
    def L(pts):
        return T(pts, x, wl, s)
    col = "#141A36"
    out = []
    hull = L([(-66, -20), (-58, -18), (52, -18), (66, -28), (70, -24), (58, -6), (48, 0), (-46, 0), (-56, -8)])
    out.append(f'<path d="{hg.org_poly(hull, seed, 0.3, 10, 2)}" fill="{col}"/>')
    out.append(f'<path d="{pd(L([(-66, -20), (-66, -32), (-46, -32), (-46, -18)]))}" fill="{col}"/>')   # stern castle
    out.append(f'<path d="{pd(L([(52, -18), (86, -34), (88, -32), (56, -16)]))}" fill="{col}"/>')        # bowsprit
    for k in range(9):
        px, py = L([(-40 + k * 10, -10)])[0]
        out.append(f'<rect x="{px - 1.4:.1f}" y="{py - 1.4:.1f}" width="2.8" height="2.8" fill="#FFD27A"/>')
    for k in range(3):
        px, py = L([(-62 + k * 6, -27)])[0]
        out.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="2.6" height="3.4" fill="#FFD27A"/>')
    for (mx, mh, sails) in ((-30, 86, ((22, 20), (18, 16), (13, 12))), (6, 104, ((26, 22), (21, 18), (15, 14))), (40, 76, ((20, 18), (16, 14)))):
        out.append(f'<path d="{pd(L([(mx - 1.2, -18), (mx - 1.2, -18 - mh), (mx + 1.2, -18 - mh), (mx + 1.2, -18)]))}" fill="{col}"/>')
        y = -24
        for (w, h) in sails:
            sail = L([(mx - w, y - h), (mx + w, y - h), (mx + w * 0.92, y - 1), (mx, y + 2), (mx - w * 0.92, y - 1)])
            out.append(f'<path d="{pd(sail)}" fill="#B8BCD8"/>')
            lit = L([(mx - w, y - h), (mx - w * 0.2, y - h), (mx - w * 0.2, y + 1.5), (mx - w * 0.92, y - 1)])
            out.append(f'<path d="{pd(lit)}" fill="#E8ECFA" opacity="0.8"/>')
            out.append(f'<path d="{pd(sail)}" fill="none" stroke="{col}" stroke-width="0.9"/>')
            yy = L([(mx - w - 3, y - h)])[0], L([(mx + w + 3, y - h)])[0]
            out.append(f'<path d="M {yy[0][0]:.1f} {yy[0][1]:.1f} L {yy[1][0]:.1f} {yy[1][1]:.1f}" stroke="{col}" stroke-width="1.6"/>')
            y -= h + 4
        fx, fy = L([(mx, -18 - mh)])[0]
        out.append(f'<path d="M {fx:.1f} {fy:.1f} l {9 * s:.1f} {2 * s:.1f} l {-9 * s:.1f} {3.5 * s:.1f} Z" fill="#C8303A"/>')
    # lantern strings from bowsprit over the mastheads to the stern
    rnd = random.Random(seed)
    anchors = [(-66, -32), (-30, -104), (6, -122), (40, -94), (88, -33)]
    for a, b in zip(anchors, anchors[1:]):
        pa, pb = L([a])[0], L([b])[0]
        mid = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2 + 8 * s)
        cur = catmull([pa, mid, pb], 6)
        out.append(f'<path d="{smooth_open(cur)}" stroke="{col}" stroke-width="0.8" fill="none"/>')
        for k in range(1, len(cur) - 1, 2):
            px, py = cur[k]
            c = rnd.choice(["#FF6A5A", "#FFD24A", "#7AE07A", "#6AB0FF", "#FF9AE0"])
            out.append(soft_glow(D, px, py + 2, 8, c, 0.6))
            out.append(f'<circle cx="{px:.1f}" cy="{py + 2:.1f}" r="2" fill="{c}"/>')
    # reflection
    out.append(f'<path d="{pd(L([(-50, 2), (50, 2), (40, 14), (-40, 14)]))}" fill="#FFD27A" opacity="0.15"/>')
    return "".join(out)


def firework(D, x, y, r, col, seed):
    rnd = random.Random(seed)
    out = [soft_glow(D, x, y, r * 1.6, col, 0.35)]
    for k in range(18):
        a = 2 * math.pi * k / 18 + rnd.uniform(-0.05, 0.05)
        rr = r * rnd.uniform(0.75, 1.0)
        out.append(taper([(x + math.cos(a) * rr * 0.2, y + math.sin(a) * rr * 0.2), (x + math.cos(a) * rr, y + math.sin(a) * rr + rr * 0.08)], 0.6, 2.2, col, 0.85))
        out.append(f'<circle cx="{x + math.cos(a) * rr:.1f}" cy="{y + math.sin(a) * rr + rr * 0.1:.1f}" r="1.6" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


@design("the-little-mermaid")
def little_mermaid():
    D = Doc2("ft-lm")
    out = [sky(D, [(0, "#0A1430"), (0.45, "#1E3A6A"), (0.62, "#3A6A9A")], 1, 360, ["#1E3A6A", "#0A1430", "#4A7AAA"], 40)]
    out.append(stars_field(3, (0, 0, 600, 300), 90))
    mx, my = 210, 210
    out.append(soft_glow(D, mx, my, 220, "#DCE8FF", 0.4))
    out.append(painted(D, blob_pts(mx, my, 62, 62, 3, 0.004, 40), ("#FFFFFF", "#F2EEDC", "#C8C4B0"), 3, sdir=(0.5, 0.5), sk=0.06, angle=-30, n=40, inkw=0, hi=0.3))
    for (cx_, cy_, r_) in ((192, 196, 12), (228, 226, 9), (214, 190, 6), (196, 230, 5)):
        out.append(f'<path d="{blob(cx_, cy_, r_, r_ * 0.8, int(cx_), 0.15, 10)}" fill="#C8C4B0" opacity="0.5"/>')
    for (y, w, c) in ((250, 300, "#5A7AAA"), (276, 220, "#3A5A8A")):
        out.append(taper([(mx - w / 2 - 40, y), (mx, y - 4), (mx + w / 2 + 60, y + 2)], 3, 9, c, 0.5))
    # the sea
    hz = 336
    out.append(sea(D, hz, 620, [(0, "#2E5A8A"), (0.4, "#1A3A6A"), (1, "#081838")], 4, ["#3A6AA0", "#0A2048", "#5A8AC0"], 90))
    # moon path on the water
    rnd = random.Random(5)
    for i in range(60):
        y = hz + 4 + (i / 60) ** 1.4 * 260
        w = 16 + (y - hz) * 0.5
        x = mx + rnd.uniform(-w, w) * 0.6
        out.append(taper([(x - w * 0.3, y), (x, y - 1.5), (x + w * 0.3, y)], 0.8, rnd.uniform(1.5, 3.5), "#F2F4FF", rnd.uniform(0.4, 0.9)))
    out.append(wave_lines(6, (0, hz + 6, 600, 600), ["#6A9AD0", "#A8C8F0", "#0A2048"], 70, (14, 40), 1.8, 2.5, (0.3, 0.7)))
    # the prince's ship far off, lanterns and fireworks
    out.append(tall_ship_lit(D, 474, hz + 4, 0.72, 7))
    out.append(firework(D, 418, 214, 24, "#FFB0D0", 8))
    out.append(firework(D, 530, 196, 20, "#B0E0FF", 9))
    out.append(firework(D, 486, 166, 13, "#FFE08A", 10))
    # the rock, wet and moonlit, with weed and foam
    # a second low rock behind, then the mermaid's rock: wet, barnacled, weedy, with foam breaking at its foot
    out.append(painted(D, [(400, 620), (420, 520), (470, 494), (530, 500), (590, 530), (620, 620)], ("#4A5A7A", "#222C48", "#0A1024"), 10, sdir=(0.6, 0.4), sk=0.15, angle=-60, n=30, inkw=1.4, inkc="#060A18", hi=0.25))
    rock = [(110, 620), (124, 530), (160, 478), (226, 448), (300, 440), (370, 452), (420, 488), (450, 540), (470, 620)]
    out.append(painted(D, rock, ("#7A8AA8", "#2E3A5A", "#0E1428"), 11, sdir=(0.6, 0.4), sk=0.2, angle=-60, n=80, inkw=1.8, inkc="#060A18", hi=0.3))
    rcid = D.clip(f'<path d="{smooth_closed(rock)}"/>')
    rt = []
    for k in range(12):
        x = 150 + k * 26
        rt.append(pline([(x, 452 + abs(k - 6) * 5), (x - 8 + rnd.uniform(-4, 4), 520), (x - 14, 610)], "#141C34", 1.6, k, 0.55, 1))
        rt.append(pline([(x + 3, 456 + abs(k - 6) * 5), (x - 4, 520)], "#8A9AC0", 1, k + 40, 0.35, 1))
    for k in range(60):
        x, y = rnd.uniform(130, 460), rnd.uniform(470, 600)
        rt.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="{rnd.choice(["#C8D0E0", "#5A6A8A", "#E8ECF4"])}" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    rt.append(f'<rect x="100" y="430" width="380" height="200" fill="{D.lin([(0, "#DCE8FF", 0.25), (0.3, "#DCE8FF", 0.0), (1, "#000010", 0.4)])}"/>')
    out.append(f'<g {rcid}>{"".join(rt)}</g>')
    out.append(ink(smooth_open([(124, 530), (160, 478), (226, 448), (300, 440)]), "#E8F2FF", 2.4, 12, 1, 0.65))
    for k in range(26):
        x = rnd.uniform(120, 470)
        y = 610 - rnd.uniform(0, 70) * (1 - abs(x - 290) / 220)
        out.append(taper([(x, y), (x + rnd.uniform(-8, 8), y - rnd.uniform(10, 24)), (x + rnd.uniform(-12, 12), y - rnd.uniform(26, 44))], 3.4, 1, rnd.choice(["#2E5A3E", "#3E6A4A", "#5A3A4A"]), 0.85))
    for (x, y, r_) in ((180, 560, 7), (196, 572, 5), (404, 546, 6)):
        out.append(painted(D, [(x - r_, y), (x, y - r_ * 1.2), (x + r_, y), (x, y + r_ * 0.4)], ("#FFE8E0", "#F2B8A8", "#A86A60"), int(x), sk=0.2, n=3, inkw=0.8, hi=0.4))
    for k in range(22):
        x = rnd.uniform(90, 620)
        out.append(f'<path d="{blob(x, 600 - rnd.uniform(0, 14), rnd.uniform(10, 22), rnd.uniform(3, 5), k, 0.3, 8)}" fill="#F2F6FF" opacity="{rnd.uniform(0.5, 0.85):.2f}"/>')
    out.append(mermaid_from_behind(D, 296, 444, 1.32, 13))
    out.append(soft_glow(D, 196, 520, 40, "#BFE8FF", 0.3))
    # lettering
    out.append(gilt(D, 300, 102, "The Little Mermaid", SERIF_IT, 58, max_w=440, seed=14, deboss="#04081A", dop=0.8, pal="silver"))
    out.append(tx(300, 134, "HANS CHRISTIAN ANDERSEN · 1837", CINZEL, 16, "#DCE8FF", ls=3, max_w=380))
    return finish_b(D, out, 15, "#000010", 0.5)


# ================================================================ 9. the princess and the pea — twenty mattresses
def mattress(D, x0, x1, y, h, seed, kind, cols):
    rnd = random.Random(seed)
    pts = [(x0, y + h * 0.5), (x0 + 4, y + 1), (x1 - 4, y), (x1, y + h * 0.5), (x1 - 4, y + h - 1), (x0 + 4, y + h)]
    d = smooth_closed(jitter(pts, seed, 0.8))
    c1, c2 = cols
    out = [f'<path d="{d}" fill="{c1}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    if kind == "stripe":
        for k in range(int((x1 - x0) / 9) + 2):
            inner.append(f'<rect x="{x0 + k * 9:.1f}" y="{y - 2:.1f}" width="4" height="{h + 4:.1f}" fill="{c2}" opacity="0.85"/>')
    elif kind == "dots":
        for k in range(int((x1 - x0) / 10) + 1):
            inner.append(f'<circle cx="{x0 + 5 + k * 10:.1f}" cy="{y + h * (0.35 if k % 2 else 0.65):.1f}" r="{max(1.4, h * 0.14):.1f}" fill="{c2}"/>')
    elif kind == "check":
        for k in range(int((x1 - x0) / 8) + 1):
            if k % 2:
                inner.append(f'<rect x="{x0 + k * 8:.1f}" y="{y - 2:.1f}" width="8" height="{h + 4:.1f}" fill="{c2}" opacity="0.4"/>')
        inner.append(f'<rect x="{x0:.1f}" y="{y + h * 0.3:.1f}" width="{x1 - x0:.1f}" height="{h * 0.4:.1f}" fill="{c2}" opacity="0.4"/>')
    elif kind == "flower":
        for k in range(int((x1 - x0) / 18) + 1):
            fx = x0 + 9 + k * 18
            for j in range(5):
                a = math.radians(j * 72)
                inner.append(f'<circle cx="{fx + math.cos(a) * h * 0.18:.1f}" cy="{y + h / 2 + math.sin(a) * h * 0.18:.1f}" r="{h * 0.13:.1f}" fill="{c2}"/>')
            inner.append(f'<circle cx="{fx:.1f}" cy="{y + h / 2:.1f}" r="{h * 0.1:.1f}" fill="#F6D24A"/>')
    elif kind == "zigzag":
        zz = [(x0 + k * 7, y + (h * 0.3 if k % 2 else h * 0.7)) for k in range(int((x1 - x0) / 7) + 2)]
        inner.append(f'<path d="{pd(zz, False)}" stroke="{c2}" stroke-width="{max(1.6, h * 0.16):.1f}" fill="none"/>')
    elif kind == "quilt":
        for k in range(int((x1 - x0) / 14) + 1):
            inner.append(f'<path d="M {x0 + k * 14:.1f} {y:.1f} L {x0 + k * 14:.1f} {y + h:.1f}" stroke="{c2}" stroke-width="1.2" stroke-dasharray="2 2"/>')
            inner.append(f'<circle cx="{x0 + 7 + k * 14:.1f}" cy="{y + h / 2:.1f}" r="1.3" fill="{c2}"/>')
    # puffed shading: light top, shadow underside, darker ends
    inner.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="{h:.1f}" fill="{D.lin([(0, "#FFFFFF", 0.45), (0.35, "#FFFFFF", 0.0), (0.7, "#2A1020", 0.0), (1, "#2A1020", 0.4)])}"/>')
    inner.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="{h:.1f}" fill="{D.lin([(0, "#2A1020", 0.3), (0.12, "#2A1020", 0.0), (0.88, "#2A1020", 0.0), (1, "#2A1020", 0.35)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#4A2A30", 1.1, seed, 1, 0.6))
    # tufts / buttons on the edge
    if h > 10 and rnd.random() < 0.6:
        for k in range(3):
            bx = x0 + (x1 - x0) * (0.25 + k * 0.25)
            out.append(f'<circle cx="{bx:.1f}" cy="{y + h * 0.5:.1f}" r="1.6" fill="{dk(c1, 0.3)}"/>')
    return "".join(out)


def princess_sitting_up(D, x, y, s, seed):
    """The princess sitting up in bed, wide awake, the coverlet over her knees; (x, y) = where she sits."""
    def L(pts):
        return T(pts, x, y, s)
    skin = ("#FBE6D8", "#E8C0A8", "#9A6A58")
    gown = ("#FFFFFF", "#F2E8F0", "#B8A0B8")
    hair = ("#E8B860", "#B07A30", "#5A3A14")
    out = []
    # long hair falling behind
    out.append(painted(D, L([(-12, -50), (-18, -36), (-20, -16), (-16, -2), (-6, -6), (-4, -28), (2, -44)]), hair, seed, sk=0.2, angle=95, n=14, inkw=1.2, inkc="#5A3A14", hi=0.4))
    # nightgown body, arms hugging the knees
    out.append(painted(D, L([(-10, -40), (-14, -24), (-14, -4), (14, -4), (16, -16), (10, -40)]), gown, seed + 1, sk=0.2, angle=-90, n=10, inkw=1.3, inkc="#6A4A5A", hi=0.4))
    out.append(f'<path d="{smooth_closed(L([(-6, -40), (0, -36), (6, -40), (4, -42), (-4, -42)]))}" fill="#F2B8C8"/>')
    # knees under the coverlet
    out.append(painted(D, L([(-16, -2), (-12, -14), (6, -20), (28, -14), (34, -4), (30, 2), (-14, 2)]), ("#F6C8D8", "#D88AA8", "#8A3A5A"), seed + 2, sk=0.2, angle=0, n=10, inkw=1.3, inkc="#6A2A4A", hi=0.4))
    out.append(taper(catmull(L([(8, -36), (16, -24), (20, -16)]), 4), 4.6 * s, 3.6 * s, gown[1]))
    out.append(f'<path d="{blob(*L([(20, -16)])[0], 3.2 * s, 2.6 * s, seed, 0.1, 8)}" fill="{skin[1]}"/>')
    # head
    hx, hy = L([(-2, -50)])[0]
    out.append(f'<path d="{blob(hx, hy, 8.2 * s, 9.4 * s, seed + 3, 0.04, 14)}" fill="{skin[1]}"/>')
    out.append(f'<path d="{blob(hx + 1, hy - 1, 6 * s, 7 * s, seed + 4, 0.04, 14)}" fill="{skin[0]}" opacity="0.7"/>')
    out.append(f'<path d="{smooth_closed(L([(-11, -52), (-8, -60), (0, -61), (8, -57), (7, -52), (2, -56), (-6, -55)]))}" fill="{hair[1]}"/>')
    # sleepless eyes (open, shadowed), small mouth
    for dx in (-5, 2):
        ex, ey = L([(dx, -50)])[0]
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{1.5 * s:.1f}" ry="{1.8 * s:.1f}" fill="#2A1A20"/>')
        out.append(pline([(ex - 2 * s, ey + 2.6 * s), (ex + 2 * s, ey + 2.8 * s)], "#B88A9A", 1, seed, 0.6, 1))
    out.append(pline(L([(-3, -44), (0, -44.6)]), "#A8505A", 1.2, seed, 0.9, 1))
    out.append(f'<circle cx="{L([(-7, -46)])[0][0]:.1f}" cy="{L([(-7, -46)])[0][1]:.1f}" r="{2 * s:.1f}" fill="#F29AA0" opacity="0.4"/>')
    # little crown
    cx_, cy_ = L([(-1, -61)])[0]
    cw = 12 * s
    cr = [(cx_ - cw / 2, cy_), (cx_ - cw / 2, cy_ - cw * 0.7), (cx_ - cw / 4, cy_ - cw * 0.3), (cx_, cy_ - cw * 0.8), (cx_ + cw / 4, cy_ - cw * 0.3), (cx_ + cw / 2, cy_ - cw * 0.7), (cx_ + cw / 2, cy_)]
    out.append(painted(D, cr, GOLD, seed + 5, sk=0.2, angle=-90, n=4, inkw=1, inkc="#6A4A10", hi=0.5))
    return "".join(out)


def pea(D, cx, cy, r, seed):
    out = [soft_glow(D, cx, cy, r * 3, "#C8F08A", 0.45)]
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.94, seed, 0.03, 16), ("#C8F08A", "#5AA83A", "#24601A"), seed, sk=0.2, angle=-40, n=4, inkw=1.2, inkc="#1A400E", hi=0.5))
    out.append(f'<circle cx="{cx - r * 0.35:.1f}" cy="{cy - r * 0.35:.1f}" r="{r * 0.25:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("the-princess-and-the-pea")
def princess_and_pea():
    D = Doc2("ft-pp")
    # bedchamber: rose damask wall lit by one candle
    out = [f'<rect width="600" height="600" fill="#6A2A3E"/>']
    rnd = random.Random(2)
    c = 56
    m = []
    for (ox, oy) in ((c / 2, c / 2), (0, 0), (c, 0), (0, c), (c, c)):
        m.append(f'<path d="{smooth_closed([(ox, oy - 16), (ox + 7, oy - 4), (ox + 14, oy), (ox + 7, oy + 4), (ox, oy + 16), (ox - 7, oy + 4), (ox - 14, oy), (ox - 7, oy - 4)])}" fill="#8A3E56" opacity="0.6"/>')
        m.append(f'<circle cx="{ox}" cy="{oy}" r="3" fill="#C88A6A" opacity="0.6"/>')
    tile = f'<rect width="{c}" height="{c}" fill="#6A2A3E"/>' + "".join(m)
    out.append(f'<rect width="600" height="600" fill="{D.pattern(c, c, tile)}"/>')
    out.append(soft_glow(D, 470, 250, 260, "#FFB868", 0.4))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.6, "#000000", 0.2), (1, "#100008", 0.6)], cx=0.6, cy=0.45, r=0.8)}"/>')
    # floorboards
    out.append(painted(D, rect_pts(-10, 500, 610, 620, 30, 3, 0.4), DARKWOOD, 3, sdir=(0.2, 1), sk=0.06, angle=0, n=50, inkw=1.4, hi=0.2))
    for k in range(5):
        out.append(pline([(-10, 512 + k * 22), (610, 510 + k * 22)], "#1A0C06", 1.4, k, 0.5, 1))
    # the bedstead and the twenty mattresses
    bx0, bx1 = 196, 404
    out.append(cast(D, 300, 506, 140, 12, strength=0.5, seed=4))
    for sg in (-1, 1):
        px = bx0 - 8 if sg < 0 else bx1 + 8
        out.append(painted(D, rect_pts(px - 6, 440, px + 6, 506, 8, 5 + sg, 0.3), WOOD, 5 + sg, sk=0.25, angle=-90, n=6, inkw=1.3, hi=0.4))
        out.append(painted(D, blob_pts(px, 436, 9, 9, 6 + sg, 0.05, 12), GOLD, 6 + sg, sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(painted(D, rect_pts(bx0 - 14, 470, bx1 + 14, 486, 16, 7, 0.3), WOOD, 7, sk=0.2, angle=0, n=12, inkw=1.4, hi=0.4))
    out.append(pea(D, 300, 463, 7, 8))
    kinds = ["stripe", "flower", "dots", "check", "zigzag", "quilt"]
    palette = [("#F6E6C8", "#C8506A"), ("#C8E0F2", "#FFFFFF"), ("#F2C8D8", "#8A3A5A"), ("#E8F0C8", "#6A9A4A"), ("#FFE8A8", "#D88A2A"),
               ("#D8C8F0", "#6A4AA0"), ("#F8D8C0", "#B8582A"), ("#C8F0E0", "#2E8A7A"), ("#FFFFFF", "#3A6AB0"), ("#F2D0A0", "#8A4A1A")]
    y = 456
    rnd = random.Random(9)
    for i in range(20):
        h = 13.6 if i < 10 else 12.8
        y -= h
        sway = math.sin(i * 0.7) * 5 + rnd.uniform(-2, 2)
        k = kinds[i % len(kinds)]
        cc = palette[(i * 3) % len(palette)]
        out.append(mattress(D, bx0 + sway - (6 if i >= 10 else 0), bx1 + sway + (6 if i >= 10 else 0), y, h + 1.5, 10 + i, k, cc))
    top = y
    # little ladder leaning on the stack
    lx0, ly0, lx1, ly1 = 452, 500, 412, top + 12
    for dx in (0, 16):
        out.append(taper([(lx0 + dx, ly0), (lx1 + dx, ly1)], 4, 3.4, WOOD[2]))
        out.append(taper([(lx0 + dx - 1, ly0), (lx1 + dx - 1, ly1)], 1.4, 1.2, WOOD[0], 0.7))
    for k in range(1, 14):
        t = k / 14
        ax, ay = lx0 + (lx1 - lx0) * t, ly0 + (ly1 - ly0) * t
        out.append(f'<path d="M {ax:.1f} {ay:.1f} L {ax + 16:.1f} {ay:.1f}" stroke="{WOOD[1]}" stroke-width="3" stroke-linecap="round"/>')
    # canopy fringe hanging at the top
    # the princess on top
    out.append(princess_sitting_up(D, 292, top + 4, 1.25, 11))
    # candle on a stool
    out.append(painted(D, rect_pts(486, 448, 530, 456, 10, 12, 0.3), WOOD, 12, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    for dx in (490, 524):
        out.append(taper([(dx, 456), (dx + (4 if dx > 500 else -4), 502)], 4, 3, WOOD[2]))
    out.append(candle(D, 508, 448, 40, 13, w=12, glow_r=150))
    # lettering
    out.append(tx(300, 78, "HANS CHRISTIAN ANDERSEN · 1835", CINZEL, 15, "#F6D8C0", ls=3, max_w=380))
    out.append(gilt(D, 300, 540, "The Princess & the Pea", SERIF_IT, 48, max_w=440, seed=14, deboss="#140408", dop=0.8))
    out.append(tx(300, 108, "Twenty mattresses, twenty eiderdowns", SERIF_IT, 22, "#FBE6D2", max_w=440))
    return finish_b(D, out, 15, "#000000", 0.5)


# ================================================================ 10. thumbelina — asleep in a walnut-shell cradle
def tulip(D, x, base, h, seed, pal=(("#FF9A8A", "#E2384A", "#8A1424")), lean=0.1, open_=0.6):
    """A tall tulip on a curving stem with two long leaves; the bloom opening (open_ 0..1)."""
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    stem = [(x, base), (x + lean * h * 0.2, base - h * 0.5), top]
    out = [taper(catmull(stem, 6), 7, 4.5, "#3E6A2E"), taper(catmull(stem, 6), 2.4, 1.4, "#9AC870", 0.7)]
    for sg, L_, hh in ((-1, h * 0.55, 0.12), (1, h * 0.45, 0.3)):
        bx, by = x + lean * h * hh * 0.4, base - h * hh
        tip = (bx + sg * L_ * 0.38, by - L_)
        lf = [(bx, by + 4), (bx + sg * L_ * 0.22, by - L_ * 0.45), tip, (bx + sg * L_ * 0.05, by - L_ * 0.4), (bx - sg * 4, by)]
        out.append(painted(D, lf, ("#A8D08A", "#4E8A3E", "#1E4A1E"), seed + sg + 5, sdir=(sg, 0.3), sk=0.2, angle=-90 + sg * 10, n=20, inkw=1.4, inkc="#1A3A16", hi=0.35))
        out.append(pline([(bx, by), (bx + sg * L_ * 0.12, by - L_ * 0.5), tip], "#C8E8A8", 1.2, seed, 0.6, 1))
    cx, cy = top
    r = h * 0.17
    petals = []
    for k, (dx, ang, scale, shade) in enumerate(((-0.62, -18 - 20 * open_, 0.95, 0.15), (0.62, 18 + 20 * open_, 0.95, 0.15), (0, 0, 1.05, 0.0), (-0.3, -6, 0.9, 0.3), (0.3, 6, 0.9, 0.3))):
        px = cx + dx * r * 0.6
        pts = [(px - r * 0.42 * scale, cy), (px - r * 0.55 * scale, cy - r * 0.8 * scale), (px - r * 0.25 * scale, cy - r * 1.55 * scale), (px, cy - r * 1.75 * scale),
               (px + r * 0.25 * scale, cy - r * 1.55 * scale), (px + r * 0.55 * scale, cy - r * 0.8 * scale), (px + r * 0.42 * scale, cy)]
        pts = rot(pts, px, cy, ang)
        petals.append((k, pts, shade))
    for k, pts, shade in sorted(petals, key=lambda p: -p[2]):
        col = (mix(pal[0], pal[2], shade), mix(pal[1], pal[2], shade), pal[2])
        out.append(painted(D, pts, col, seed + 10 + k, sdir=(0.4, 0.8), sk=0.15, angle=-90, n=16, inkw=1.3, inkc="#5A0A18", hi=0.4))
        out.append(pline([pts[0], pts[2], pts[3]], lt(pal[0], 0.4), 1.2, seed + k, 0.45, 1))
    return "".join(out), top


def walnut_cradle(D, cx, rim_y, rx, ry, depth, seed):
    """Half a walnut shell used as a cradle: lumpy wrinkled outer shell, smooth pale inner lip. Returns (back, front)."""
    rnd = random.Random(seed)
    back = [f'<path d="{smooth_closed(ell_pts(cx, rim_y, rx, ry, 0, 360, 36))}" fill="#6A4020"/>',
            f'<path d="{smooth_closed(ell_pts(cx, rim_y - ry * 0.1, rx * 0.94, ry * 0.8, 180, 360, 24) + [(cx + rx * 0.94, rim_y + ry * 0.3)])}" fill="#E8C898" opacity="0.55"/>']
    front = [cast(D, cx + 18, rim_y + depth + 4, rx * 1.05, 14, strength=0.5, seed=seed)]
    body = []
    for a in range(0, 181, 5):
        k = 1 + 0.035 * math.sin(math.radians(a) * 9 + seed)
        body.append((cx + rx * math.cos(math.radians(a)) * (1 + 0.01 * math.sin(a)), rim_y + ry * 0.4 + (depth - ry * 0.4) * math.sin(math.radians(a)) ** 0.7 * k))
    body += [(cx + rx * math.cos(math.radians(a)), rim_y + ry * math.sin(math.radians(a))) for a in range(180, -1, -10)]
    pal = ("#E2AA70", "#A86A32", "#4E2A10")
    d = smooth_closed(body)
    front.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.2, angle=-60, n=40, inkw=2.2, inkc="#3A1E0A", hi=0.35))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # the walnut's convolutions: rounded lumps, each lit on top and shadowed below
    for k in range(70):
        u = rnd.uniform(-0.95, 0.95)
        v = rnd.uniform(0.15, 1.0)
        x = cx + u * rx
        y = rim_y + ry * 0.6 + v * (depth - ry * 0.4) * math.sqrt(max(0.05, 1 - u * u))
        L = rnd.uniform(10, 26)
        ang = rnd.uniform(-60, 60) + 90 * (1 if rnd.random() < 0.4 else 0)
        p0 = (x - math.cos(math.radians(ang)) * L / 2, y - math.sin(math.radians(ang)) * L / 2)
        p2 = (x + math.cos(math.radians(ang)) * L / 2, y + math.sin(math.radians(ang)) * L / 2)
        p1 = (x + rnd.uniform(-5, 5), y + rnd.uniform(-5, 5))
        inner.append(taper([(p0[0], p0[1] + 2), (p1[0], p1[1] + 2.5), (p2[0], p2[1] + 2)], 2, 4, "#4A2408", 0.55))
        inner.append(taper([p0, p1, p2], 1.5, 3, "#F2C690", 0.45))
    g = D.lin([(0, "#2A1004", 0.0), (0.5, "#2A1004", 0.05), (1, "#2A1004", 0.45)], 0, 0, 1, 1)
    inner.append(f'<path d="{d}" fill="{g}"/>')
    inner.append(taper([(cx - rx * 0.3, rim_y + depth * 0.35), (cx - rx * 0.55, rim_y + depth * 0.62), (cx - rx * 0.7, rim_y + depth * 0.5)], 3, 8, "#FFE8C0", 0.3))
    front.append(f'<g {cid}>{"".join(inner)}</g>')
    # pale inner lip along the rim
    lip = ell_pts(cx, rim_y, rx, ry, 6, 174, 24)
    front.append(taper(lip, 4, 4, "#E8C898"))
    front.append(taper(lip[2:-2], 9, 9, "#E8C898"))
    front.append(taper([(x_, y_ - 1.5) for x_, y_ in lip], 3, 3, "#FFF4D8", 0.85))
    front.append(ink(smooth_open([(x_, y_ + 4) for x_, y_ in lip]), "#5A3214", 1.6, seed, 1, 0.75))
    return "".join(back), "".join(front)


def violet_leaf(D, x, y, s, ang, seed):
    pts = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + hx * s / 16, y + hy * s / 16))
    pts = rot(pts, x, y, ang)
    return painted(D, pts, ("#7AA86A", "#2E6A3A", "#143A1E"), seed, sk=0.2, angle=ang - 60, n=8, inkw=1.1, inkc="#0E2A14", hi=0.3)


def swallow(D, x, y, s, seed, flip=False):
    """A barn swallow in flight: steel-blue back, rust throat, cream belly, long forked tail; faces left."""
    def L(pts):
        return T(pts, x, y, s, flip, -8)
    out = []
    blue = ("#5A7AB8", "#24386A", "#0E1834")
    for sg, op in ((-1, 0.85), (1, 1.0)):
        wing = L([(-4, -2), (10, sg * -6 - 10 * (sg > 0) + 2), (30, -26 if sg > 0 else -16), (56, -34 if sg > 0 else -22), (70, -32 if sg > 0 else -20), (44, -14 if sg > 0 else -6), (16, 2)])
        out.append(painted(D, wing, blue if sg > 0 else (mix(blue[0], "#000000", 0.2), mix(blue[1], "#000000", 0.2), blue[2]), seed + sg, sk=0.2, angle=-20, n=8, inkw=1.1, inkc="#0A1020", hi=0.35))
    body = L([(-30, 0), (-22, -8), (-6, -10), (14, -6), (30, -2), (14, 6), (-10, 8), (-24, 6)])
    out.append(painted(D, body, blue, seed + 3, sk=0.2, angle=0, n=8, inkw=1.2, inkc="#0A1020", hi=0.4))
    out.append(painted(D, L([(-20, 4), (-6, 8), (14, 6), (4, 2), (-12, 2)]), ("#FFFBF0", "#F2E8D8", "#B8A88A"), seed + 4, sk=0.2, n=3, inkw=0, hi=0.3))
    out.append(f'<path d="{blob(*L([(-24, 2)])[0], 5 * s, 4 * s, seed, 0.1, 8)}" fill="#C8582A"/>')
    for sg in (-1, 1):
        out.append(taper(L([(26, 0), (46, sg * 6), (64, sg * 14)]), 4 * s, 0.8, blue[1]))
    out.append(f'<path d="{pd(L([(-30, -1), (-38, 1), (-30, 2)]))}" fill="#1A1A1A"/>')
    ex, ey = L([(-24, -3)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.4 * s:.1f}" fill="#0A0A0A"/>')
    return "".join(out)


@design("thumbelina")
def thumbelina():
    D = Doc2("ft-tb")
    out = [paper(D.nid(), "#F8EADF", FLECK, 41)]
    out.append(blooms(5, ["#F2B8C0", "#E8C8A8", "#F8D8D0"], 9, op=(0.08, 0.16)))
    out.append(soft_glow(D, 240, 280, 300, "#FFF4E0", 0.6))
    for (x0_, w_) in ((60, 70), (140, 70)):
        out.append(f'<path d="{pd([(x0_, 190), (x0_ + w_, 190), (x0_ + w_ + 60, 330), (x0_ + 60, 330)])}" fill="#FFFFFF" opacity="0.28"/>')
        out.append(f'<path d="{pd([(x0_, 340 - 330 + 330), (x0_ + w_, 340), (x0_ + w_ + 50, 452), (x0_ + 50, 452)])}" fill="#FFFFFF" opacity="0.0"/>')
    # sprigged wallpaper border lines
    for k in range(13):
        x = 20 + k * 47
        out.append(f'<path d="M {x} 0 L {x} 470" stroke="#E8C8C0" stroke-width="10" opacity="0.35"/>')
        for j in range(8):
            out.append(f'<circle cx="{x + 23:.1f}" cy="{30 + j * 60 + (k % 2) * 30:.1f}" r="2.6" fill="#E89AAA" opacity="0.5"/>')
    # table
    out.append(painted(D, rect_pts(-10, 460, 610, 620, 30, 3, 0.4), ("#E2B486", "#B87E4E", "#6A4020"), 3, sdir=(0.2, 1), sk=0.06, angle=0, n=60, inkw=1.6, hi=0.25))
    out.append(taper([(-10, 462), (300, 461), (610, 462)], 3, 3, "#F8DCB8", 0.8))
    out.append(f'<rect x="0" y="460" width="600" height="140" fill="{D.lin([(0, "#3A1E0A", 0.0), (1, "#3A1E0A", 0.35)])}"/>')
    # the tulip she was born from, in its pot
    px, pb = 506, 480
    out.append(cast(D, px + 10, pb, 60, 8, strength=0.45, seed=4))
    pot = [(px - 44, pb - 74), (px + 44, pb - 74), (px + 34, pb), (px - 34, pb)]
    out.append(painted(D, pot, ("#F2A880", "#C8653A", "#7A3214"), 5, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=20, inkw=1.6, hi=0.4))
    out.append(painted(D, rect_pts(px - 50, pb - 86, px + 50, pb - 70, 10, 6, 0.4), ("#F2A880", "#C8653A", "#7A3214"), 6, sdir=(0.5, 1), sk=0.25, angle=0, n=10, inkw=1.6, hi=0.45))
    out.append(f'<path d="{smooth_closed(ell_pts(px, pb - 86, 48, 6, 0, 360, 20))}" fill="#4A2A18"/>')
    tl, (tcx, tcy) = tulip(D, px - 4, pb - 86, 178, 7, lean=-0.42, open_=0.75)
    out.append(tl)
    # the swallow she nursed through the winter, come to carry her away
    out.append(swallow(D, 150, 236, 1.25, 30))
    # the cockchafer (May-bug) on the tulip leaf
    bx, by = 540, 300
    out.append(painted(D, blob_pts(bx, by, 11, 7, 8, 0.05, 12, -30), ("#C8884A", "#8A4A1E", "#3A1A08"), 8, sk=0.2, angle=-30, n=6, inkw=1.2, hi=0.4))
    out.append(f'<path d="{blob(bx - 9, by + 6, 5, 4, 9, 0.05, 10)}" fill="#2A1A10"/>')
    for k in range(3):
        out.append(pline([(bx - 4 + k * 5, by + 5), (bx - 6 + k * 6, by + 11)], "#2A1A10", 1.1, k, 0.9, 1))
    out.append(pline([(bx - 12, by + 3), (bx - 18, by - 2), (bx - 16, by - 6)], "#2A1A10", 1, 9, 0.9, 1))
    # the walnut-shell cradle
    cx, rim_y, rx, ry, depth = 248, 372, 168, 42, 108
    back, front = walnut_cradle(D, cx, rim_y, rx, ry, depth, 10)
    out.append(back)
    # bed of violet leaves, rose-petal coverlet, Thumbelina asleep
    for k, (dx, dy, s_, a) in enumerate(((-120, -6, 20, -50), (-92, -16, 22, -24), (124, -8, 21, 50), (96, -20, 22, 24), (52, -22, 20, 10), (-40, -22, 19, -8), (10, -26, 18, 0))):
        out.append(violet_leaf(D, cx + dx, rim_y + dy, s_, a, 11 + k))
    # pillow: a white petal
    out.append(painted(D, blob_pts(cx - 100, rim_y - 10, 36, 17, 12, 0.08, 14, -12), ("#FFFFFF", "#F8F0F2", "#C8B0B8"), 12, sk=0.15, angle=0, n=8, inkw=1.2, inkc="#8A6A72", hi=0.4))
    # her head and golden hair spread on the pillow
    hx, hy = cx - 94, rim_y - 22
    k_ = 1.45
    hair = blob_pts(hx - 3 * k_, hy - 3 * k_, 21 * k_, 15 * k_, 13, 0.18, 16, -10)
    out.append(painted(D, hair, ("#FFE6A0", "#E8B450", "#9A6A1E"), 13, sk=0.15, angle=200, n=20, inkw=1.2, inkc="#7A5016", hi=0.4))
    for k in range(8):
        a = math.radians(150 + k * 13)
        out.append(pline([(hx + math.cos(a) * 9 * k_, hy + math.sin(a) * 6 * k_), (hx + math.cos(a) * 24 * k_, hy + math.sin(a) * 16 * k_ + 5)], "#C8902E", 1.2, k, 0.6, 1))
    out.append(f'<path d="{blob(hx + 4 * k_, hy + 1 * k_, 11 * k_, 12 * k_, 14, 0.04, 14)}" fill="#FBE2D2"/>')
    out.append(f'<path d="{blob(hx + 6 * k_, hy + 4 * k_, 7 * k_, 7 * k_, 15, 0.06, 12)}" fill="#F2C8B8" opacity="0.45"/>')
    out.append(f'<path d="{smooth_closed([(hx - 7 * k_, hy - 3 * k_), (hx + 1 * k_, hy - 13 * k_), (hx + 14 * k_, hy - 11 * k_), (hx + 12 * k_, hy - 5 * k_), (hx + 3 * k_, hy - 7 * k_)])}" fill="#E8B450"/>')
    out.append(pline([(hx + 1 * k_, hy - 10 * k_), (hx + 8 * k_, hy - 8 * k_), (hx + 13 * k_, hy - 6 * k_)], "#FFF0B8", 1.2, 3, 0.7, 1))
    for dx in (-0.5, 8.5):
        out.append(pline([(hx + dx * k_, hy + 1 * k_), (hx + (dx + 2.5) * k_, hy + 2.8 * k_), (hx + (dx + 5) * k_, hy + 1 * k_)], "#5A3020", 1.5, int(dx), 0.9, 1))
        for j in range(3):
            out.append(pline([(hx + (dx + 1 + j * 1.6) * k_, hy + 2.4 * k_), (hx + (dx + 0.6 + j * 1.8) * k_, hy + 3.8 * k_)], "#5A3020", 0.8, j, 0.7, 1))
    out.append(f'<circle cx="{hx + 2 * k_:.1f}" cy="{hy + 6.5 * k_:.1f}" r="{3 * k_:.1f}" fill="#F29AA0" opacity="0.5"/><circle cx="{hx + 12 * k_:.1f}" cy="{hy + 6.5 * k_:.1f}" r="{2.6 * k_:.1f}" fill="#F29AA0" opacity="0.4"/>')
    out.append(pline([(hx + 6 * k_, hy + 9 * k_), (hx + 7.4 * k_, hy + 9.8 * k_), (hx + 8.6 * k_, hy + 9 * k_)], "#C05060", 1.4, 1, 0.9, 1))
    # the rose-petal coverlet (her small body a hump beneath)
    cov = [(cx - 78, rim_y - 8), (cx - 62, rim_y - 28), (cx - 10, rim_y - 34), (cx + 44, rim_y - 30), (cx + 104, rim_y - 22), (cx + 128, rim_y - 6), (cx + 96, rim_y + 8), (cx - 40, rim_y + 10)]
    out.append(painted(D, cov, ("#FFC8D4", "#F2809A", "#B03A5A"), 16, sdir=(0.3, 1), sk=0.2, angle=-10, n=34, inkw=1.5, inkc="#8A2A44", hi=0.5))
    for k in range(6):
        out.append(pline([(cx - 60 + k * 32, rim_y - 26), (cx - 50 + k * 34, rim_y - 8), (cx - 46 + k * 34, rim_y + 6)], "#C85070", 1.2, k, 0.5, 1))
    out.append(taper([(cx - 60, rim_y - 27), (cx, rim_y - 33), (cx + 60, rim_y - 27)], 2, 4, "#FFFFFF", 0.6))
    out.append(taper([(cx - 76, rim_y - 9), (cx - 70, rim_y - 20), (cx - 60, rim_y - 28)], 3, 1, "#FFFFFF", 0.5))
    # tiny hand resting on the coverlet
    out.append(f'<path d="{blob(cx - 62, rim_y - 22, 6.5, 4.2, 17, 0.1, 8, -20)}" fill="#FBE2D2" stroke="#C89080" stroke-width="0.9"/>')
    out.append(front)
    # scattered petals and a sprig of violets on the table
    rnd = random.Random(18)
    for k, (x, y, a) in enumerate(((90, 520, 30), (130, 540, -20), (380, 520, 60), (410, 548, 10))):
        out.append(painted(D, blob_pts(x, y, 13, 8, 18 + k, 0.12, 12, a), ("#FFC8D4", "#F2809A", "#B03A5A"), 18 + k, sk=0.2, n=4, inkw=1, inkc="#8A2A44", hi=0.4))
    for k in range(4):
        vx, vy = 60 + k * 14, 490 + (k % 2) * 8
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<path d="{blob(vx + math.cos(a) * 4, vy + math.sin(a) * 4, 4, 2.6, k * 5 + j, 0.1, 8, math.degrees(a))}" fill="#7A4AB8"/>')
        out.append(f'<circle cx="{vx}" cy="{vy}" r="1.6" fill="#F6D24A"/>')
    # lettering
    out.append(letters(D, 300, 120, "Thumbelina", SERIF_IT, 78, "#B03A5A", ["#C8506A", "#8A1E3A", "#E8708A"], 19, max_w=430,
                       shadow="#F2C8C8", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 160, "SCARCELY HALF AS LONG AS A THUMB", CINZEL, 16, "#7A3A4A", ls=3, max_w=360))
    out.append(tx(300, 538, "HANS CHRISTIAN ANDERSEN · 1835", CINZEL, 15, "#FFF0DC", ls=3, max_w=380))
    return finish_b(D, out, 20, INK, 0.6)


# ================================================================ 11. little red riding hood — the old wood, the wolf behind the oak
def red_hood_walker(D, x, base, s, seed):
    """Little Red Riding Hood from behind, walking up the path: red hooded cloak, basket on her arm. s=1 ~ 100 px."""
    def L(pts):
        return T(pts, x, base, s)
    red = ("#F2705A", "#C0242A", "#5E0A10")
    out = [cast(D, x + 6 * s, base + 1, 26 * s, 4 * s, strength=0.5, seed=seed)]
    # stockinged legs and little boots
    for (a, b) in (((-7, -16), (-8, -2)), ((6, -16), (8, -4))):
        out.append(taper(L([a, b]), 4.6 * s, 4 * s, "#3A2A2A"))
        bx, by = L([b])[0]
        out.append(f'<path d="{blob(bx, by + 1.5 * s, 4.4 * s, 2.8 * s, seed, 0.1, 8)}" fill="#2A1A14"/>')
    # dress hem
    out.append(painted(D, L([(-20, -24), (20, -24), (22, -12), (-22, -12)]), ("#8AA0C8", "#4A5E8A", "#1E2A4A"), seed, sk=0.2, angle=-90, n=6, inkw=1, hi=0.3))
    out.append(f'<path d="{smooth_open(L([(-22, -13), (-11, -10), (0, -13), (11, -10), (22, -13)]))}" stroke="#FFFFFF" stroke-width="{2 * s:.1f}" fill="none" opacity="0.9"/>')
    # the cloak: bell from the shoulders, deep folds
    cloak = L([(-10, -74), (-18, -64), (-24, -46), (-28, -30), (-32, -18), (-20, -20), (-6, -17), (8, -19), (22, -17), (31, -21), (26, -40), (20, -60), (12, -74)])
    out.append(painted(D, cloak, red, seed + 1, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=40, inkw=1.6, inkc="#3A0408", hi=0.45, hik=0.08))
    cid = D.clip(f'<path d="{smooth_closed(cloak)}"/>')
    inner = []
    for k, fx in enumerate((-18, -8, 2, 12, 22)):
        inner.append(taper(catmull(L([(fx * 0.4, -70), (fx * 0.8, -44), (fx, -18)]), 5), 1.5 * s, 5 * s, red[2], 0.45))
        inner.append(taper(catmull(L([(fx * 0.4 - 3, -68), (fx * 0.8 - 4, -44), (fx - 5, -20)]), 5), 1 * s, 3 * s, red[0], 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # hood, up, with a soft point and its lining edge
    hood = L([(-12, -72), (-15, -84), (-11, -96), (-2, -104), (6, -102), (14, -94), (16, -82), (13, -72), (0, -68)])
    out.append(painted(D, hood, red, seed + 2, sdir=(0.6, 0.2), sk=0.2, angle=-70, n=16, inkw=1.5, inkc="#3A0408", hi=0.45))
    out.append(pline(L([(-6, -100), (-4, -88), (-6, -76)]), red[2], 1.4, seed, 0.6, 1))
    # basket on the right arm: wicker, a white cloth and the neck of a wine bottle
    bx, by = L([(28, -40)])[0]
    out.append(ink(smooth_open(L([(18, -40), (22, -54), (34, -54), (38, -40)])), "#6A4220", 2.6 * s, seed, 1, 1))
    bask = [(bx - 13 * s, by - 2 * s), (bx + 13 * s, by - 2 * s), (bx + 10 * s, by + 10 * s), (bx - 10 * s, by + 10 * s)]
    out.append(painted(D, bask, ("#E2B47A", "#B07A3E", "#5E3A18"), seed + 3, sk=0.2, angle=0, n=8, inkw=1.2, hi=0.4))
    for k in range(3):
        out.append(pline([(bx - 12 * s, by + k * 3.6 * s), (bx + 12 * s, by + k * 3.6 * s)], "#6A4220", 0.9, seed + k, 0.7, 1))
    out.append(f'<path d="{smooth_closed([(bx - 12 * s, by - 2 * s), (bx - 4 * s, by - 7 * s), (bx + 6 * s, by - 5 * s), (bx + 12 * s, by - 2 * s)])}" fill="#FFFFFF"/>')
    out.append(f'<path d="{pd([(bx + 4 * s, by - 5 * s), (bx + 6 * s, by - 14 * s), (bx + 8.5 * s, by - 14 * s), (bx + 8 * s, by - 5 * s)])}" fill="#2E4A2A"/>')
    # rim light from the glade ahead
    out.append(ink(smooth_open(L([(-2, -104), (-11, -96), (-15, -84), (-18, -64), (-24, -46)])), "#FFE2A0", 1.6, seed, 1, 0.7))
    return "".join(out)


def wolf_peeking(D, x, y, s, seed):
    """A grey wolf's head and shoulder leaning out from behind a trunk, facing left; (x, y) = base of neck."""
    def L(pts):
        return T(pts, x, y, s)
    fur = ("#B8B0A8", "#6A645E", "#24201C")
    out = []
    neck = L([(0, 20), (-6, -6), (-14, -24), (-10, -40), (6, -46), (26, -40), (40, -10), (40, 30)])
    out.append(painted(D, neck, fur, seed, sdir=(1, 0.3), sk=0.2, angle=120, n=30, slen=(6 * s, 14 * s), sw=(0.6, 1.5), cols=["#D8D0C8", "#3A342E", "#8A8278"], inkw=1.4, inkc="#100C08", hi=0.35))
    head = L([(-12, -36), (-30, -40), (-52, -40), (-62, -36), (-60, -30), (-44, -24), (-28, -16), (-10, -16), (4, -26), (6, -44), (0, -52), (-8, -50)])
    out.append(painted(D, head, fur, seed + 1, sdir=(1, 0.4), sk=0.18, angle=180, n=30, slen=(5 * s, 12 * s), sw=(0.5, 1.3), cols=["#E8E0D8", "#3A342E", "#8A8278"], inkw=1.5, inkc="#100C08", hi=0.4))
    # pale muzzle and cheek ruff
    out.append(f'<path d="{smooth_closed(L([(-58, -32), (-44, -26), (-28, -20), (-14, -22), (-26, -28), (-46, -32)]))}" fill="#E8E2D8" opacity="0.8"/>')
    # ears
    for (a, b, c) in (((-2, -48), (4, -66), (10, -46)), ((-10, -48), (-8, -64), (-2, -50))):
        e = L([a, b, c])
        out.append(painted(D, e, fur, seed + 2, sk=0.2, angle=-90, n=4, inkw=1.2, inkc="#100C08", hi=0.3))
    out.append(f'<path d="{pd(L([(2, -50), (5, -60), (8, -48)]))}" fill="#3A2420" opacity="0.6"/>')
    # nose, mouth line, the gleaming yellow eye
    nx_, ny_ = L([(-62, -36)])[0]
    out.append(f'<path d="{blob(nx_, ny_, 4 * s, 3 * s, seed, 0.1, 8)}" fill="#100C08"/>')
    out.append(pline(L([(-58, -28), (-40, -22), (-26, -20)]), "#100C08", 1.4, seed, 0.85, 1))
    ex, ey = L([(-26, -36)])[0]
    out.append(soft_glow(D, ex, ey, 14 * s, "#FFD040", 0.5))
    out.append(f'<path d="{blob(ex, ey, 4.2 * s, 2.6 * s, seed, 0.05, 10, -12)}" fill="#F6C21C"/>')
    out.append(f'<ellipse cx="{ex - 0.6 * s:.1f}" cy="{ey:.1f}" rx="{1.1 * s:.1f}" ry="{2.2 * s:.1f}" fill="#100C08"/>')
    out.append(pline(L([(-32, -39), (-24, -40), (-18, -37)]), "#100C08", 1.6, seed, 0.9, 1))
    # forepaw curled round the bark
    out.append(painted(D, L([(-8, 24), (-14, 18), (-12, 10), (0, 8), (6, 18)]), fur, seed + 3, sk=0.2, angle=0, n=6, inkw=1.2, inkc="#100C08", hi=0.3))
    for k in range(3):
        cx_, cy_ = L([(-13 + k * 3, 21 + k)])[0]
        out.append(f'<path d="M {cx_:.1f} {cy_:.1f} l -3 2" stroke="#100C08" stroke-width="1.2" stroke-linecap="round"/>')
    return "".join(out)


def toadstool(D, x, base, h, seed, cap=MADDER):
    out = [painted(D, rect_pts(x - h * 0.12, base - h, x + h * 0.12, base, 6, seed, 0.3), ("#FFFFFF", "#EEE6D8", "#A8988A"), seed, sk=0.25, angle=-90, n=4, inkw=1, hi=0.4)]
    cp = ell_pts(x, base - h, h * 0.5, h * 0.42, 180, 360, 14) + [(x + h * 0.48, base - h + 2), (x - h * 0.48, base - h + 2)]
    out.append(painted(D, cp, cap, seed + 1, sk=0.2, angle=-60, n=6, inkw=1.1, hi=0.45))
    rnd = random.Random(seed)
    for k in range(4):
        out.append(f'<circle cx="{x + rnd.uniform(-0.3, 0.3) * h:.1f}" cy="{base - h - rnd.uniform(0.1, 0.3) * h:.1f}" r="{h * 0.06:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


@design("little-red-riding-hood")
def red_riding_hood():
    D = Doc2("ft-rr")
    out = [sky(D, [(0, "#5A6450"), (0.45, "#C8C49A"), (0.62, "#F2E2B0"), (1, "#7A7458")], 1, 600, ["#8A8A6A", "#E8DCB0", "#4A5040"], 50)]
    out.append(soft_glow(D, 300, 300, 240, "#FFF0C0", 0.7))
    rnd = random.Random(3)
    # far trunks in the haze
    for k, (x, w) in enumerate(((150, 22), (210, 16), (262, 12), (338, 12), (392, 18), (446, 22))):
        out.append(gnarled_trunk(D, x, 360, -20, w, 20 + k, ("#C8C0A0", "#A8A080", "#7A7458"), lean=rnd.uniform(-0.03, 0.03), roots=False, branches=1))
    out.append(mist(D, 330, 90, 4, "#FFF6DA", 0.6))
    # mid trunks
    for k, (x, w) in enumerate(((96, 40), (504, 44), (178, 26), (424, 28))):
        out.append(gnarled_trunk(D, x, 430, -20, w, 30 + k, ("#8A8468", "#5E5A44", "#2E2C1E"), lean=rnd.uniform(-0.05, 0.05), roots=True, branches=2, rim="#FFE8B0", rim_side=1 if x < 300 else -1))
    # forest floor and the path winding toward the light
    out.append(hill(D, [(-20, 380), (150, 372), (300, 366), (450, 372), (620, 380)], 620, ("#9A9A6A", "#6A6A44", "#34341E"), 5, inkw=0, sop=(0.15, 0.35)))
    path = [(300, 362), (290, 390), (320, 430), (276, 490), (230, 560), (200, 620)]
    pp = catmull(path, 8)
    widths = [6 + 170 * ((y - 362) / 260) ** 1.3 for _, y in pp]
    left = [(x - w / 2, y) for (x, y), w in zip(pp, widths)]
    right = [(x + w / 2, y) for (x, y), w in zip(pp, widths)]
    pts = left + right[::-1]
    out.append(painted(D, pts, ("#F6E2B0", "#D8BC84", "#8A7448"), 6, sdir=(0.2, 1), sk=0.1, angle=-80, n=60, inkw=0, hi=0.4))
    out.append(grass(7, (0, 380, 600, 600), ["#4A4A2A", "#7A7A48", "#A8A060", "#2E2E1A"], 300, (8, 24)))
    # wildflowers she stops to pick
    for k in range(30):
        x, y = rnd.uniform(20, 580), rnd.uniform(400, 590)
        c = rnd.choice(["#FFFFFF", "#F2D24A", "#C8A0E8", "#F2A0B0"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 3.6):.1f}" fill="{c}"/>')
    out.append(toadstool(D, 132, 520, 22, 8))
    out.append(toadstool(D, 152, 526, 14, 9))
    # Red Riding Hood on the path
    out.append(red_hood_walker(D, 298, 440, 1.05, 10))
    # foreground: the great oak on the right with the wolf behind it; a trunk on the left
    out.append(wolf_peeking(D, 470, 400, 1.15, 11))
    out.append(gnarled_trunk(D, 548, 640, -20, 120, 12, ("#5A5440", "#2E2A1E", "#100E08"), lean=-0.05, roots=True, branches=2, rim="#FFE0A0", rim_side=-1))
    out.append(gnarled_trunk(D, 30, 640, -20, 96, 13, ("#5A5440", "#2E2A1E", "#100E08"), lean=0.04, roots=True, branches=2, rim="#FFE0A0", rim_side=1))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.65, "#000000", 0.05), (1, "#140E04", 0.55)], r=0.75)}"/>')
    # lettering
    out.append(letters(D, 300, 102, "Little Red Riding Hood", SERIF_IT, 54, "#B0202A", ["#D03A3A", "#7E0E14", "#E8605A"], 14, max_w=440,
                       shadow="#FFF2D0", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(301, 136, "A TALE FROM PERRAULT & GRIMM", CINZEL, 15, "#100C04", ls=3, max_w=360, op=0.6))
    out.append(tx(300, 134, "A TALE FROM PERRAULT & GRIMM", CINZEL, 15, "#FFF2D8", ls=3, max_w=360))
    out.append(tx(301, 539, "“Don’t stray from the path.”", SERIF_IT, 36, "#100C04", max_w=420, op=0.55))
    out.append(tx(300, 536, "“Don’t stray from the path.”", SERIF_IT, 36, "#FFF2D8", max_w=420))
    return finish_b(D, out, 15, INK, 0.6)


# ================================================================ 12. jack and the beanstalk — up through the clouds
def beanstalk(D, pts, w0, w1, seed, leaf_every=3):
    """Twining beanstalk: two stems twisting round each other, heart-shaped bean leaves, curling tendrils, pods."""
    rnd = random.Random(seed)
    path = catmull(pts, 10)
    n = len(path)
    out = []
    strands = []
    for ph in (0, math.pi):
        sp = []
        for i, (x, y) in enumerate(path):
            a = path[max(i - 1, 0)]
            b = path[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            t = i / (n - 1)
            amp = (w0 + (w1 - w0) * t) * 0.35
            off = math.sin(i * 0.5 + ph) * amp
            sp.append((x + nx * off, y + ny * off))
        strands.append(sp)
    pal = ("#B8E07A", "#4E9A3A", "#1E5A1E")
    for k, sp in enumerate(strands):
        out.append(taper(sp, w0 * 0.75, w1 * 0.75, pal[2]))
        out.append(taper(sp, w0 * 0.55, w1 * 0.55, pal[1]))
        out.append(taper([(x - 1.5, y - 1) for x, y in sp], w0 * 0.18, w1 * 0.18, pal[0], 0.8))
    leaves, tendrils = [], []
    for i in range(4, n - 2, leaf_every):
        x, y = path[i]
        t = i / (n - 1)
        side = 1 if (i // leaf_every) % 2 else -1
        size = (w0 + (w1 - w0) * t) * rnd.uniform(1.0, 1.35) + 14
        ang = (-40 if side > 0 else -140) + rnd.uniform(-25, 25)
        lx, ly = x + math.cos(math.radians(ang)) * size * 0.6, y + math.sin(math.radians(ang)) * size * 0.6
        leaves.append((lx, ly, size, ang, i))
        if rnd.random() < 0.5:
            cx_, cy_ = x - side * size * 0.6, y - size * 0.2
            sp = [(cx_ + math.cos(a) * (8 - a) * size * 0.022 * 6, cy_ + math.sin(a) * (8 - a) * size * 0.022 * 6) for a in [j * 0.6 for j in range(12)]]
            tendrils.append(pline([(x, y)] + sp, pal[1], max(1.2, size * 0.04), seed + i, 0.9, 1))
    out += tendrils
    for (lx, ly, size, ang, i) in leaves:
        pts_ = []
        for j in range(24):
            tt = 2 * math.pi * j / 24
            hx = 16 * math.sin(tt) ** 3
            hy = -(13 * math.cos(tt) - 5 * math.cos(2 * tt) - 2 * math.cos(3 * tt) - math.cos(4 * tt))
            pts_.append((lx + hx * size / 32, ly - hy * size / 30))
        pts_ = rot(pts_, lx, ly, ang + 90)
        out.append(painted(D, pts_, rnd.choice([("#B8E07A", "#5AA83E", "#1E5A1E"), ("#C8E88A", "#6AB04A", "#2A6A26")]), seed + i, sk=0.18, angle=ang, n=10, inkw=1.2, inkc="#143A10", hi=0.35))
        out.append(pline([(lx - math.cos(math.radians(ang)) * size * 0.4, ly - math.sin(math.radians(ang)) * size * 0.4), (lx + math.cos(math.radians(ang)) * size * 0.4, ly + math.sin(math.radians(ang)) * size * 0.4)], "#D8F0A8", 1.1, seed + i, 0.6, 1))
    # dangling pods
    for i in range(10, n - 4, 17):
        x, y = path[i]
        t = i / (n - 1)
        L = 18 + 20 * (1 - t)
        out.append(painted(D, [(x, y), (x + 4, y + L * 0.4), (x + 2, y + L), (x - 3, y + L * 0.6)], ("#C8E88A", "#7AB84A", "#2A5A1A"), seed + i, sk=0.2, angle=-90, n=4, inkw=1, inkc="#143A10", hi=0.4))
    return "".join(out)


def climbing_jack(D, x, y, s, seed):
    """Jack climbing, side view facing right: both hands gripping the stalk at about (x, y), one knee drawn up with the
    foot braced on the stalk, the other leg hanging; red cap, linen shirt, green waistcoat, brown breeches."""
    def L(pts):
        return T(pts, x, y, s)
    skin = ("#FBD8C0", "#E8B090", "#8A5A40")
    shirt = ("#FFFFFF", "#ECE2CC", "#9A8A6A")
    out = []

    def limb(pts, w0, w1, col, inkc="#3A2418"):
        p = catmull(L(pts), 5)
        out.append(taper(p, w0 * s + 1.6, w1 * s + 1.6, inkc, 0.8))
        out.append(taper(p, w0 * s, w1 * s, col))
    # far leg hanging, far arm reaching highest (behind the body)
    limb([(-12, 64), (-16, 82), (-13, 100)], 8, 6, "#6A4428")
    limb([(-13, 100), (-12, 112)], 5, 4.4, "#D8D0C0")
    out.append(f'<path d="{blob(*L([(-9, 114)])[0], 6.5 * s, 3.4 * s, seed, 0.1, 8, 10)}" fill="#2A1A10"/>')
    limb([(-8, 34), (0, 14), (8, -10)], 6, 5, "#D8CCB4")
    out.append(f'<path d="{blob(*L([(9, -12)])[0], 4.4 * s, 3.8 * s, seed + 1, 0.1, 8)}" fill="{skin[2]}"/>')
    # torso: shirt with the waistcoat over it
    torso = L([(-12, 30), (-2, 28), (4, 36), (2, 52), (-2, 66), (-16, 66), (-18, 50)])
    out.append(painted(D, torso, shirt, seed, sdir=(-1, 0.3), sk=0.2, angle=-80, n=10, inkw=1.3, inkc="#4A3A2A", hi=0.4))
    vest = L([(-4, 32), (3, 38), (1, 52), (-2, 64), (-10, 64), (-8, 44)])
    out.append(painted(D, vest, ("#7ABA7A", "#2E7A4A", "#123A22"), seed + 1, sk=0.2, angle=-80, n=6, inkw=1.2, inkc="#123A22", hi=0.3))
    for k in range(3):
        bx, by = L([(1.5 - k * 0.6, 42 + k * 7)])[0]
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{1.1 * s:.1f}" fill="#F6D24A"/>')
    # breeches and the near leg drawn up, foot braced on the stalk
    out.append(painted(D, L([(-18, 60), (-2, 60), (8, 66), (12, 76), (2, 80), (-10, 76), (-18, 70)]), ("#C8965E", "#8A5A30", "#3A2410"), seed + 2, sk=0.2, angle=-20, n=6, inkw=1.3, hi=0.3))
    limb([(8, 76), (10, 88), (12, 98)], 5.6, 4.6, "#ECE2D0")
    out.append(f'<path d="{blob(*L([(16, 100)])[0], 7 * s, 3.6 * s, seed + 3, 0.1, 8, -15)}" fill="#2A1A10"/>')
    # head tipped back, looking up toward the clouds; red cap with a tassel
    hx, hy = L([(-6, 18)])[0]
    out.append(f'<path d="{blob(hx, hy, 8.4 * s, 9.2 * s, seed, 0.04, 14, -20)}" fill="{skin[1]}"/>')
    out.append(f'<path d="{blob(hx + 2 * s, hy + 1 * s, 6 * s, 6.6 * s, seed + 1, 0.05, 12)}" fill="{skin[0]}" opacity="0.75"/>')
    out.append(f'<path d="{smooth_closed(L([(-14, 18), (-16, 10), (-12, 4), (-4, 8), (-8, 14)]))}" fill="#8A4A1E"/>')   # hair at the nape
    cap = L([(-15, 12), (-14, 4), (-6, 2), (2, 6), (0, 10), (-8, 10)])
    out.append(painted(D, cap, ("#F2785A", "#C8302A", "#6A0E0A"), seed + 4, sk=0.2, angle=-30, n=4, inkw=1.2, inkc="#4A0A08", hi=0.4))
    out.append(taper(catmull(L([(-14, 6), (-20, 4), (-24, 10)]), 4), 3 * s, 2 * s, "#C8302A"))
    out.append(f'<circle cx="{L([(-24, 11)])[0][0]:.1f}" cy="{L([(-24, 11)])[0][1]:.1f}" r="{2.2 * s:.1f}" fill="#F6D24A"/>')
    ex, ey = L([(-1, 16)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{1.2 * s:.1f}" ry="{1.5 * s:.1f}" fill="#2A1A10"/>')
    out.append(pline(L([(1, 24), (-2, 25.5)]), "#9A3A2A", 1.2, seed, 0.9, 1))
    out.append(f'<circle cx="{L([(-3, 21)])[0][0]:.1f}" cy="{L([(-3, 21)])[0][1]:.1f}" r="{2 * s:.1f}" fill="#F29A8A" opacity="0.5"/>')
    out.append(pline(L([(3, 18), (4.5, 20), (2.4, 21)]), skin[2], 1, seed, 0.8, 1))   # nose
    # near arm reaching up to grip
    limb([(-4, 34), (4, 18), (10, 2)], 6, 5, shirt[0])
    out.append(f'<path d="{blob(*L([(11, 0)])[0], 4.6 * s, 4 * s, seed + 5, 0.1, 8)}" fill="{skin[1]}"/>')
    out.append(ink(blob(*L([(11, 0)])[0], 4.6 * s, 4 * s, seed + 5, 0.1, 8), "#6A3A2A", 1, seed, 1, 0.6))
    return "".join(out)


def giant_castle(D, x, base, seed, k=1.0):
    """The giant's castle on the cloud: massive grey keep, round towers, a huge door and banners."""
    rnd = random.Random(seed)
    out = []
    pal = ("#E2DCEC", "#A8A0C0", "#5A5478")
    for (tx_, tw, th, rd) in ((x - 70 * k, 44 * k, 120 * k, 1), (x + 74 * k, 40 * k, 104 * k, 1), (x, 96 * k, 92 * k, 0)):
        body = rect_pts(tx_ - tw / 2, base - th, tx_ + tw / 2, base, 14, seed + int(tx_), 0.5)
        out.append(painted(D, body, pal, seed + int(tx_), sdir=(1, 0.2), sk=0.2, angle=-90, n=20, inkw=1.6, inkc="#2A2440", hi=0.35))
        for j in range(int(tw / 10) + 1):
            out.append(f'<rect x="{tx_ - tw / 2 + j * 10 - 2:.1f}" y="{base - th - 9:.1f}" width="6" height="10" fill="{pal[1]}" stroke="#2A2440" stroke-width="0.8"/>')
        if rd:
            cone = [(tx_ - tw / 2 - 5, base - th - 8), (tx_, base - th - 8 - tw * 1.3), (tx_ + tw / 2 + 5, base - th - 8)]
            out.append(painted(D, cone, ("#8A9AD0", "#3E4A8A", "#1A2050"), seed + int(tx_) + 1, sdir=(1, 0.2), sk=0.25, angle=-70, n=8, inkw=1.4, inkc="#1A2050", hi=0.4))
            fx, fy = tx_, base - th - 8 - tw * 1.3
            out.append(f'<path d="M {fx:.1f} {fy:.1f} l 0 -14" stroke="#2A2440" stroke-width="1.6"/><path d="M {fx:.1f} {fy - 14:.1f} q 8 2 16 -1 l -3 5 l 3 5 q -8 -2 -16 0 Z" fill="#C8302A"/>')
        for j in range(2):
            wy = base - th + 24 + j * 30
            if wy < base - 20:
                out.append(f'<path d="M {tx_ - 4:.1f} {wy + 12:.1f} L {tx_ - 4:.1f} {wy:.1f} Q {tx_:.1f} {wy - 5:.1f} {tx_ + 4:.1f} {wy:.1f} L {tx_ + 4:.1f} {wy + 12:.1f} Z" fill="#2A2440"/>')
    door = arch_pts(x - 20 * k, x + 20 * k, base - 40 * k, base, 6)
    out.append(painted(D, door, ("#A8784A", "#6A4224", "#2E1A0A"), seed + 3, sk=0.2, angle=-90, n=8, inkw=1.6, inkc="#1A0E04", hi=0.3))
    return "".join(out)


@design("jack-and-the-beanstalk")
def jack_beanstalk():
    D = Doc2("ft-jb")
    out = [sky(D, [(0, "#3E7AC0"), (0.45, "#8AC0E8"), (0.8, "#D8ECF4"), (1, "#F6F0D8")], 1, 600, ["#6AA0D8", "#B8DCF2", "#FFFFFF"], 60)]
    out.append(soft_glow(D, 480, 120, 220, "#FFF8D8", 0.5))
    # little farm far below: fields, the cottage
    out.append(hill(D, [(-20, 530), (120, 516), (260, 524), (420, 512), (620, 522)], 620, ("#C8E0A0", "#8AB86A", "#4E7A3E"), 3, inkw=0, sop=(0.1, 0.3)))
    for k in range(7):
        out.append(pline([(k * 100 - 40, 540 + k % 3 * 6), (k * 100 + 60, 548 + k % 2 * 8)], "#6A9A4A", 2, k, 0.4, 1))
    cx_, cb = 130, 552
    out.append(painted(D, rect_pts(cx_ - 34, cb - 30, cx_ + 34, cb, 10, 4, 0.4), ("#FFF6E2", "#EADCC0", "#9A8A6A"), 4, sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, [(cx_ - 44, cb - 26), (cx_ - 24, cb - 52), (cx_ + 24, cb - 52), (cx_ + 44, cb - 26)], ("#F2D890", "#C8A050", "#7A5A20"), 5, sk=0.2, angle=-60, n=16, inkw=1.4, hi=0.4))
    out.append(f'<rect x="{cx_ - 6}" y="{cb - 18}" width="12" height="18" fill="#6A4224"/><rect x="{cx_ + 14}" y="{cb - 22}" width="10" height="9" fill="#5A6A8A"/>')
    out.append(steam_wisps(cx_ + 18, cb - 56, 26, 4, "#FFFFFF", 1, 0, 4, 0.6))
    # clouds at the beanstalk's middle and the cloud-land up top
    out.append(puff_cloud(D, 500, 360, 220, 6, ("#FFFFFF", "#F6F4F2", "#C8D4E2"), op=0.95))
    out.append(puff_cloud(D, 96, 410, 180, 7, ("#FFFFFF", "#F6F4F2", "#C8D4E2"), op=0.9))
    out.append(puff_cloud(D, 170, 250, 380, 9, ("#FFFFFF", "#FBF8F2", "#D0D8E8"), op=1.0, rows=2))
    out.append(giant_castle(D, 168, 222, 8, 0.82))
    for k, (x, w) in enumerate(((60, 120), (150, 110), (250, 130), (330, 90))):
        out.append(puff_cloud(D, x, 250 + (k % 2) * 6, w, 30 + k, ("#FFFFFF", "#FBF8F2", "#D0D8E8"), op=1.0, rows=1))
    # the beanstalk
    out.append(beanstalk(D, [(340, 650), (372, 560), (322, 476), (270, 410), (306, 336), (270, 284), (232, 246)], 44, 16, 10, leaf_every=4))
    out.append(puff_cloud(D, 380, 300, 120, 11, ("#FFFFFF", "#F6F4F2", "#C8D4E2"), op=0.85))
    out.append(climbing_jack(D, 296, 340, 1.45, 12))
    # golden egg glint up by the castle door
    out.append(soft_glow(D, 120, 216, 22, "#FFE070", 0.8))
    out.append(f'<path d="{blob(120, 214, 7, 9, 13, 0.02, 12)}" fill="#F6C21C" stroke="#8A6010" stroke-width="1.2"/>')
    out.append(f'<path d="{blob(118, 210, 2, 3, 14, 0.02, 8)}" fill="#FFFBE0"/>')
    for k in range(3):
        out.append(bird_v(410 + k * 28, 170 + k * 10, 6 - k, "#3A5A8A"))
    # lettering: right column
    out.append(tx(436, 128, "JACK AND THE BEANSTALK", CINZEL, 15, "#1E3A6A", ls=2, max_w=196))
    out.append(letters(D, 436, 196, "Fee-fi-", SERIF_IT, 64, "#1E3A6A", ["#2E5A9A", "#122A50", "#4A7AC0"], 14, max_w=190,
                       shadow="#FFFFFF", soff=(0.02, 0.05), angle=-40, wob=0.6))
    out.append(letters(D, 436, 258, "fo-fum!", SERIF_IT, 64, "#B0302A", ["#D04A3A", "#7E1414", "#E8705A"], 15, max_w=190,
                       shadow="#FFFFFF", soff=(0.02, 0.05), angle=-40, wob=0.6))
    return finish_b(D, out, 16, INK, 0.5)


# ================================================================ 13. sleeping beauty — the castle behind the hedge of briar roses
def briar_vine(D, pts, w, seed, col=("#6A8A4A", "#3A5A2A", "#18301A"), thorns=True):
    path = catmull(pts, 10)
    out = [taper(path, w, w * 0.5, col[2]), taper(path, w * 0.7, w * 0.35, col[1]), taper([(x - 1, y - 1) for x, y in path], w * 0.2, w * 0.1, col[0], 0.8)]
    if thorns:
        rnd = random.Random(seed)
        for i in range(2, len(path) - 1, 3):
            (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
            a = math.atan2(y1 - y0, x1 - x0)
            sg = 1 if rnd.random() < 0.5 else -1
            x, y = path[i]
            nx, ny = -math.sin(a) * sg, math.cos(a) * sg
            L = w * rnd.uniform(0.6, 1.0)
            tip = (x + nx * L + math.cos(a) * L * 0.6, y + ny * L + math.sin(a) * L * 0.6)
            out.append(f'<path d="M {x - math.cos(a) * w * 0.35:.1f} {y - math.sin(a) * w * 0.35:.1f} L {tip[0]:.1f} {tip[1]:.1f} L {x + math.cos(a) * w * 0.3:.1f} {y + math.sin(a) * w * 0.3:.1f} Z" fill="{col[2]}"/>')
    return "".join(out)


def wild_rose(D, x, y, r, seed, pal=PINK, open_=True):
    """Five-petalled briar rose (dog rose) with a golden centre; or a furled bud."""
    out = []
    if open_:
        for k in range(5):
            a = math.radians(k * 72 - 90 + seed * 13)
            px, py = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
            pts = blob_pts(px, py, r * 0.55, r * 0.5, seed + k, 0.1, 12, math.degrees(a))
            out.append(painted(D, pts, pal, seed + k, sdir=(-math.cos(a), -math.sin(a)), sk=0.25, angle=math.degrees(a), n=5, inkw=0.9, inkc="#7A2A44", hi=0.4))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.32:.1f}" fill="#F6D24A"/>')
        rnd = random.Random(seed)
        for k in range(10):
            a = rnd.uniform(0, 6.28)
            out.append(f'<circle cx="{x + math.cos(a) * r * 0.34:.1f}" cy="{y + math.sin(a) * r * 0.34:.1f}" r="{max(0.8, r * 0.06):.1f}" fill="#C88A1A"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.14:.1f}" fill="#9AB040"/>')
    else:
        bud = [(x, y - r), (x + r * 0.45, y - r * 0.2), (x + r * 0.3, y + r * 0.4), (x - r * 0.3, y + r * 0.4), (x - r * 0.45, y - r * 0.2)]
        out.append(painted(D, bud, (pal[1], pal[2], dk(pal[2], 0.3)), seed, sk=0.2, angle=-90, n=4, inkw=0.9, inkc="#5A1A30", hi=0.4))
        out.append(f'<path d="{pd([(x - r * 0.4, y + r * 0.2), (x, y + r * 0.7), (x + r * 0.4, y + r * 0.2), (x, y + r * 0.45)])}" fill="#4E7A3E"/>')
    return "".join(out)


def rose_leaflet(D, x, y, s, ang, seed):
    pts = blob_pts(x, y, s, s * 0.5, seed, 0.06, 12, ang)
    return painted(D, pts, ("#8AB86A", "#3E7A3A", "#1A401E"), seed, sk=0.2, angle=ang, n=4, inkw=0.9, inkc="#143A16", hi=0.35)


def fairy_castle(D, cx, base, seed, col=("#E8D8F2", "#B8A8D8", "#6A5A90"), roof=("#C890B8", "#8A4A80", "#4A1E4A"), lit="#FFD27A", k=1.0):
    """Tall storybook castle (Nielsen-like slender towers with steep cones)."""
    rnd = random.Random(seed)
    out = []
    towers = [(-110, 26, 150, 1), (-62, 34, 200, 1), (0, 46, 250, 1), (58, 32, 186, 1), (104, 24, 136, 1), (-30, 60, 110, 0), (34, 64, 100, 0)]
    for (dx, w, h, cone) in sorted(towers, key=lambda t: t[3]):
        x = cx + dx * k
        w *= k
        h *= k
        body = rect_pts(x - w / 2, base - h, x + w / 2, base, 14, seed + int(dx), 0.4)
        out.append(painted(D, body, col, seed + int(dx) + 200, sdir=(1, 0.2), sk=0.25, angle=-90, n=14, inkw=1.2, inkc="#3A2A50", hi=0.35))
        if cone:
            cn = [(x - w / 2 - 5 * k, base - h + 2), (x - w * 0.2, base - h - w * 1.2), (x, base - h - w * 2.3), (x + w * 0.2, base - h - w * 1.2), (x + w / 2 + 5 * k, base - h + 2)]
            out.append(painted(D, cn, roof, seed + int(dx) + 300, sdir=(1, 0.2), sk=0.25, angle=-80, n=10, inkw=1.2, inkc="#2A1030", hi=0.4))
            out.append(f'<path d="M {x:.1f} {base - h - w * 2.3:.1f} l 0 {-12 * k:.1f}" stroke="#3A2A50" stroke-width="1.6"/>')
            out.append(f'<path d="M {x:.1f} {base - h - w * 2.3 - 12 * k:.1f} l {10 * k:.1f} {3 * k:.1f} l {-10 * k:.1f} {4 * k:.1f} Z" fill="{lit}" opacity="0.9"/>')
        else:
            for j in range(int(w / (9 * k)) + 1):
                out.append(f'<rect x="{x - w / 2 + j * 9 * k:.1f}" y="{base - h - 7 * k:.1f}" width="{5 * k:.1f}" height="{8 * k:.1f}" fill="{col[1]}"/>')
        for j in range(int(h / (40 * k))):
            if rnd.random() < 0.55:
                wy = base - h + 18 * k + j * 40 * k
                ww = 5 * k
                out.append(f'<path d="M {x - ww:.1f} {wy + 14 * k:.1f} L {x - ww:.1f} {wy + 4 * k:.1f} Q {x:.1f} {wy - 2 * k:.1f} {x + ww:.1f} {wy + 4 * k:.1f} L {x + ww:.1f} {wy + 14 * k:.1f} Z" fill="{lit}"/>')
                out.append(soft_glow(D, x, wy + 8 * k, 16 * k, lit, 0.45))
    return "".join(out)


@design("sleeping-beauty")
def sleeping_beauty():
    D = Doc2("ft-sb")
    out = [sky(D, [(0, "#2A2050"), (0.4, "#6A4A88"), (0.7, "#D08AA8"), (1, "#F6C8B0")], 1, 600, ["#4A3A78", "#2A2050", "#E8A8C0", "#FFD8C0"], 60)]
    out.append(stars_field(2, (0, 0, 600, 200), 50))
    out.append(soft_glow(D, 440, 200, 80, "#FFF2E0", 0.4))
    out.append(f'<path d="{blob(440, 200, 16, 16, 3, 0.02, 18)}" fill="#FFF8E8"/><path d="{blob(447, 195, 14, 14, 4, 0.02, 18)}" fill="#8A5E9E"/>')
    out.append(soft_glow(D, 300, 420, 260, "#FFD0B0", 0.4))
    # the sleeping castle, wrapped in mist, a hundred years quiet
    out.append(fairy_castle(D, 300, 404, 5, k=0.7))
    out.append(mist(D, 400, 70, 6, "#F2D0E0", 0.55))
    # the hedge of briars: dense dark mass, rising thorn stems, roses blooming
    rnd = random.Random(7)
    hedge = [(-20, 620), (-20, 400), (40, 380), (90, 400), (150, 372), (210, 398), (260, 384), (300, 404), (350, 380), (410, 398), (470, 374), (530, 396), (620, 384), (620, 620)]
    out.append(painted(D, hedge, ("#4A6A44", "#22382A", "#0E1A12"), 8, sdir=(0, 1), sk=0.12, angle=-80, n=120, inkw=0, hi=0.25))
    for k in range(300):
        x, y = rnd.uniform(-10, 610), rnd.uniform(386, 600)
        sz, ang = rnd.uniform(6, 11), rnd.uniform(0, 360)
        lt_ = 1 - (y - 386) / 214
        c = mix(rnd.choice(["#3E7A3A", "#2E5A2E", "#4E8A46"]), "#9AC07A", 0.35 * lt_ * rnd.random())
        out.append(f'<path d="{blob(x, y, sz, sz * 0.5, 100 + k, 0.08, 10, ang)}" fill="{c}" stroke="#143A16" stroke-width="0.8" stroke-opacity="0.6"/>')
        out.append(f'<path d="M {x - math.cos(math.radians(ang)) * sz * 0.8:.1f} {y - math.sin(math.radians(ang)) * sz * 0.8:.1f} L {x + math.cos(math.radians(ang)) * sz * 0.8:.1f} {y + math.sin(math.radians(ang)) * sz * 0.8:.1f}" stroke="#B8D898" stroke-width="0.8" opacity="0.6"/>')
    # thorny stems arching up out of the hedge
    stems = [[(30, 600), (60, 420), (40, 300), (80, 200), (60, 120)], [(560, 600), (540, 420), (566, 300), (520, 190), (546, 110)],
             [(150, 600), (170, 470), (130, 390), (150, 330)], [(450, 600), (430, 470), (470, 390), (448, 320)],
             [(250, 600), (240, 470), (210, 420)], [(350, 600), (360, 470), (392, 420)]]
    for k, st in enumerate(stems):
        out.append(briar_vine(D, st, 7 if k < 2 else 5, 20 + k))
        pp = catmull(st, 8)
        for i in range(6, len(pp) - 2, 7):
            x, y = pp[i]
            out.append(rose_leaflet(D, x + rnd.choice([-12, 12]), y, 9, rnd.uniform(0, 360), 300 + k * 10 + i))
    # roses on the hedge and the stems
    spots = [(70, 420, 15), (120, 470, 18), (200, 440, 14), (260, 500, 19), (330, 450, 16), (400, 492, 18), (470, 430, 15), (530, 470, 17),
             (60, 540, 16), (170, 540, 15), (300, 560, 15), (440, 550, 16), (560, 530, 14), (58, 306, 13), (82, 214, 12), (552, 300, 13), (526, 200, 12),
             (148, 340, 11), (450, 330, 11)]
    for k, (x, y, r) in enumerate(spots):
        if 80 < x < 520 and 506 < y < 566:
            continue
        out.append(wild_rose(D, x, y, r, 40 + k, PINK if k % 3 else ("#FFF0F2", "#F8C8D4", "#C87A90")))
    out.append(f'<ellipse cx="300" cy="528" rx="250" ry="34" fill="{D.rad([(0, "#06100A", 0.55), (0.7, "#06100A", 0.3), (1, "#06100A", 0)])}"/>')
    for k, (x, y) in enumerate(((40, 250), (98, 160), (560, 250), (536, 150), (130, 380), (470, 384), (232, 430), (370, 424))):
        out.append(wild_rose(D, x, y, 9, 70 + k, PINK, open_=False))
    # lettering
    out.append(tx(300, 82, "BRIAR ROSE · BROTHERS GRIMM", CINZEL, 16, "#FFE8F0", ls=4, max_w=360))
    out.append(letters(D, 300, 140, "Sleeping Beauty", SERIF_IT, 64, "#FFF2F4", ["#FFFFFF", "#F8D0DC", "#FFE8EE"], 9, max_w=420,
                       shadow="#3A1E4A", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(301, 540, "…and the whole castle slept a hundred years.", SERIF_IT, 26, "#0A140C", max_w=440, op=0.7))
    out.append(tx(300, 538, "…and the whole castle slept a hundred years.", SERIF_IT, 26, "#FFF0F4", max_w=440))
    return finish_b(D, out, 10, "#000000", 0.5)


# ================================================================ 14. puss in boots — a gilt-framed portrait of the Master Cat
def puss(D, ox, oy, s, seed):
    """The Master Cat standing on his hind legs in cavalier boots and plumed hat, three-quarter view,
    one paw on his hip and the game-bag over his shoulder. (ox, oy) = between his boots. s=1 ~ 300 px tall."""
    def L(pts):
        return T(pts, ox, oy, s)
    fur = ("#C8C0B4", "#8A8478", "#3A362E")
    white = ("#FFFFFF", "#F2EEE6", "#B8B0A2")
    out = [cast(D, ox + 10 * s, oy + 2, 80 * s, 10 * s, strength=0.5, seed=seed)]
    # tail curling behind
    out.append(taper(catmull(L([(30, -100), (60, -96), (78, -120), (70, -150), (56, -158)]), 6), 14 * s, 9 * s, fur[2]))
    out.append(taper(catmull(L([(30, -100), (60, -96), (78, -120), (70, -150), (56, -158)]), 6), 11 * s, 7 * s, fur[1]))
    for k in range(5):
        p = L([(52 + k * 6, -96 - k * 12)])[0]
        out.append(f'<path d="{blob(p[0], p[1], 4 * s, 2 * s, seed + k, 0.2, 8, 60)}" fill="{fur[2]}" opacity="0.7"/>')
    # the game-bag (sack) over the left shoulder, hanging down his back
    sack = L([(-46, -200), (-62, -186), (-74, -150), (-68, -120), (-48, -118), (-38, -150), (-34, -188)])
    out.append(painted(D, sack, ("#E8D2A0", "#B89A62", "#6A522A"), seed, sk=0.2, angle=-80, n=16, inkw=1.6, hi=0.4))
    out.append(pline(L([(-66, -146), (-50, -138), (-40, -150)]), "#6A522A", 1.2, seed, 0.6, 1))
    # boots: tall, wide flared cuffs, square toes
    for (bx, k) in ((-22, 0), (20, 1)):
        boot = L([(bx - 16, -118), (bx - 26, -132), (bx + 26, -132), (bx + 16, -116), (bx + 12, -60), (bx + 14, -16), (bx + 30, -10), (bx + 32, 0),
                  (bx - 14, 0), (bx - 14, -20), (bx - 12, -60)])
        out.append(painted(D, boot, ("#A8743E", "#6A3E1A", "#2A140A"), seed + 1 + k, sdir=(0.8, 0.2), sk=0.2, angle=-90, n=24, inkw=1.8, inkc="#1A0A04", hi=0.45, hik=0.1))
        cuff = L([(bx - 26, -132), (bx - 30, -150), (bx + 30, -150), (bx + 26, -132)])
        out.append(painted(D, cuff, ("#C8925A", "#8A5A2E", "#3A1E0A"), seed + 3 + k, sk=0.2, angle=0, n=8, inkw=1.6, inkc="#1A0A04", hi=0.45))
        out.append(pline(L([(bx - 12, -40), (bx + 12, -40)]), "#2A140A", 1.4, seed + k, 0.6, 1))
        out.append(taper(L([(bx - 6, -110), (bx - 8, -70), (bx - 6, -30)]), 3 * s, 1.5 * s, "#E8B880", 0.6))
        sp = L([(bx - 12, -6)])[0]
        out.append(f'<path d="{blob(sp[0], sp[1], 5 * s, 3 * s, seed, 0.1, 8)}" fill="{GOLD[1]}" stroke="{GOLD[2]}" stroke-width="1"/>')
    # body: furry torso, white bib and belly; sword belt
    body = L([(-34, -150), (-40, -186), (-36, -214), (-20, -232), (20, -232), (36, -214), (40, -186), (36, -150), (20, -136), (-20, -136)])
    out.append(painted(D, body, fur, seed + 5, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=60, slen=(8 * s, 18 * s), sw=(0.6, 1.6),
                       cols=["#E2DCD2", "#4A463E", "#A8A296"], inkw=1.8, inkc="#1A1610", hi=0.4))
    bib = L([(-16, -226), (-22, -200), (-18, -164), (0, -146), (18, -164), (22, -200), (16, -226), (0, -218)])
    out.append(painted(D, bib, white, seed + 6, sk=0.15, angle=-90, n=20, slen=(6 * s, 12 * s), sw=(0.5, 1.2), inkw=0, hi=0.3))
    rnd = random.Random(seed)
    for k in range(12):
        x, y = L([(rnd.uniform(-34, 34), rnd.uniform(-226, -144))])[0]
        if abs(x - ox) > 16 * s:
            out.append(taper([(x, y), (x + 4 * s, y + 3 * s)], 3 * s, 0.6, fur[2], 0.6))
    belt = L([(-38, -160), (38, -164), (38, -154), (-38, -150)])
    out.append(painted(D, belt, ("#7A4A2A", "#4A2A14", "#1E0E04"), seed + 7, sk=0.2, angle=0, n=4, inkw=1.2, inkc="#0E0602", hi=0.3))
    bk = L([(0, -157)])[0]
    out.append(f'<rect x="{bk[0] - 7 * s:.1f}" y="{bk[1] - 6 * s:.1f}" width="{14 * s:.1f}" height="{12 * s:.1f}" fill="none" stroke="{GOLD[1]}" stroke-width="{2.6 * s:.1f}"/>')
    # rapier at his side
    out.append(taper(L([(30, -156), (74, -64), (88, -36)]), 3 * s, 1.5 * s, "#C8CCD8"))
    out.append(taper(L([(28, -160), (22, -174)]), 3 * s, 3 * s, GOLD[2]))
    out.append(ink(smooth_open(L([(18, -166), (24, -176), (36, -170), (34, -158)])), GOLD[1], 2.4 * s, seed, 1, 1))
    # arms: right paw on hip, left paw holding the sack's neck
    out.append(taper(catmull(L([(34, -214), (52, -196), (48, -170), (36, -166)]), 5), 15 * s, 12 * s, fur[1]))
    out.append(taper(catmull(L([(34, -214), (50, -198), (46, -176)]), 5), 4 * s, 2 * s, fur[0], 0.6))
    out.append(f'<path d="{blob(*L([(36, -164)])[0], 8 * s, 7 * s, seed, 0.1, 10)}" fill="{white[1]}" stroke="#4A463E" stroke-width="1"/>')
    out.append(taper(catmull(L([(-32, -214), (-46, -206), (-48, -196), (-40, -198)]), 5), 15 * s, 12 * s, fur[1]))
    out.append(f'<path d="{blob(*L([(-40, -200)])[0], 8 * s, 7 * s, seed + 1, 0.1, 10)}" fill="{white[1]}" stroke="#4A463E" stroke-width="1"/>')
    # lace collar
    for k in range(7):
        a = math.radians(200 + k * 20)
        cx_, cy_ = L([(0, -228)])[0]
        out.append(f'<path d="{blob(cx_ + math.cos(a) * 22 * s, cy_ + math.sin(a) * 6 * s + 6 * s, 8 * s, 5 * s, seed + k, 0.15, 10, math.degrees(a))}" fill="#FFFFFF" stroke="#C8C0B0" stroke-width="0.8"/>')
    # head
    head = L([(-30, -250), (-36, -268), (-32, -290), (-16, -304), (0, -308), (16, -304), (32, -290), (36, -268), (30, -250), (14, -238), (0, -236), (-14, -238)])
    out.append(painted(D, head, fur, seed + 8, sdir=(0.8, 0.4), sk=0.18, angle=-90, n=40, slen=(5 * s, 12 * s), sw=(0.5, 1.4),
                       cols=["#E2DCD2", "#4A463E", "#A8A296"], inkw=1.8, inkc="#1A1610", hi=0.45))
    # tabby stripes on the brow
    for k in range(3):
        out.append(taper(L([(-6 + k * 6, -304), (-5 + k * 5, -290)]), 3 * s, 1, fur[2], 0.8))
    for sg in (-1, 1):
        for k in range(2):
            out.append(taper(L([(sg * 34, -276 + k * 9), (sg * 22, -272 + k * 9)]), 3 * s, 1, fur[2], 0.7))
    # ears (one under the hat brim)
    for sg in (-1, 1):
        ear = L([(sg * 12, -300), (sg * 30, -330), (sg * 34, -290)])
        out.append(painted(D, ear, fur, seed + 9 + sg, sk=0.2, angle=-90, n=4, inkw=1.4, inkc="#1A1610", hi=0.3))
        out.append(f'<path d="{pd(L([(sg * 17, -298), (sg * 28, -320), (sg * 30, -296)]))}" fill="#E8A8A0" opacity="0.8"/>')
    # muzzle, nose, mouth
    out.append(f'<path d="{blob(*L([(0, -256)])[0], 18 * s, 12 * s, seed + 11, 0.08, 12)}" fill="{white[0]}"/>')
    nx_, ny_ = L([(0, -264)])[0]
    out.append(f'<path d="M {nx_ - 5 * s:.1f} {ny_ - 2 * s:.1f} L {nx_ + 5 * s:.1f} {ny_ - 2 * s:.1f} L {nx_:.1f} {ny_ + 4 * s:.1f} Z" fill="#D87A7A" stroke="#6A2A2A" stroke-width="1"/>')
    out.append(pline(L([(0, -260), (0, -254), (-6, -250)]), "#3A2A26", 1.4, seed, 0.9, 1))
    out.append(pline(L([(0, -254), (6, -250)]), "#3A2A26", 1.4, seed, 0.9, 1))
    for sg in (-1, 1):
        for k in range(3):
            out.append(pline(L([(sg * 10, -258 + k * 3), (sg * 46, -264 + k * 8)]), "#FFFFFF", 1.1, seed + k, 0.85, 1))
    # eyes: big, green-gold, clever
    for sg in (-1, 1):
        ex, ey = L([(sg * 14, -278)])[0]
        out.append(f'<path d="{blob(ex, ey, 8 * s, 7 * s, seed + sg, 0.04, 12, sg * -10)}" fill="#C8D84A" stroke="#1A1610" stroke-width="1.6"/>')
        out.append(f'<path d="{blob(ex, ey + 1 * s, 8 * s, 4 * s, seed + sg, 0.04, 12)}" fill="#8AA02A" opacity="0.5"/>')
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{2.2 * s:.1f}" ry="{6 * s:.1f}" fill="#0A0806"/>')
        out.append(f'<circle cx="{ex - 2.4 * s:.1f}" cy="{ey - 2.6 * s:.1f}" r="{1.8 * s:.1f}" fill="#FFFFFF"/>')
    # the cavalier hat, cocked, with a sweeping white-and-red plume
    brim = L([(-46, -300), (-30, -316), (0, -322), (34, -318), (52, -306), (40, -298), (0, -302), (-30, -296)])
    crown = L([(-24, -312), (-22, -338), (-6, -350), (16, -348), (28, -334), (28, -314)])
    out.append(painted(D, crown, ("#5A5A7A", "#2A2A44", "#0E0E1A"), seed + 12, sk=0.2, angle=-90, n=10, inkw=1.6, inkc="#06060E", hi=0.35))
    out.append(painted(D, L([(-23, -318), (28, -320), (28, -312), (-24, -312)]), MADDER, seed + 13, sk=0.2, angle=0, n=4, inkw=1, hi=0.4))
    out.append(painted(D, brim, ("#5A5A7A", "#2A2A44", "#0E0E1A"), seed + 14, sk=0.2, angle=0, n=10, inkw=1.6, inkc="#06060E", hi=0.35))
    plume = L([(20, -332), (44, -352), (74, -356), (96, -342), (104, -320), (92, -326), (74, -340), (50, -338), (30, -322)])
    out.append(painted(D, plume, ("#FFFFFF", "#F2ECE4", "#B8B0A6"), seed + 15, sk=0.15, angle=20, n=20, inkw=1.3, inkc="#6A6058", hi=0.4))
    for k in range(10):
        a = L([(30 + k * 7, -334 - k * 1.2)])[0]
        b = L([(34 + k * 7, -344 - k * 1.4 + (k * 0.4) ** 2)])[0]
        out.append(pline([a, b], "#A89E92", 1, seed + k, 0.6, 1))
    plume2 = L([(16, -330), (36, -346), (62, -346), (74, -336), (56, -332), (34, -324)])
    out.append(painted(D, plume2, MADDER, seed + 16, sk=0.15, angle=20, n=8, inkw=1.1, inkc="#4A0A0A", hi=0.4))
    return "".join(out)


@design("puss-in-boots")
def puss_in_boots():
    D = Doc2("ft-pb")
    # deep green velvet wall
    out = [cloth_bg(D, "#1E4A3A", 3, weave=3, vign=0.6)]
    out.append(soft_glow(D, 300, 260, 320, "#FFE8B0", 0.2))
    cx, cy, rx, ry = 300, 286, 168, 214
    ov = ell_pts(cx, cy, rx, ry, 0, 360, 64)
    # the painted portrait: the Marquis of Carabas' cornfields and the ogre's castle at golden hour
    cid = D.clip(f'<path d="{smooth_closed(ov)}"/>')
    sc = [sky(D, [(0, "#6A8AB0"), (0.5, "#E8C890"), (0.75, "#F6E0A8"), (1, "#C8A060")], 2, 600, ["#8AA0C0", "#F2D8A0", "#FFFFFF"], 40)]
    sc.append(puff_cloud(D, 220, 170, 120, 3, ("#FFF8E8", "#F6E2C0", "#C8A890"), op=0.85))
    sc.append(hill(D, [(100, 330), (200, 310), (300, 322), (400, 300), (500, 318)], 520, ("#B8C890", "#8AA068", "#4A6A3E"), 4, inkw=0, sop=(0.1, 0.3)))
    sc.append(fairy_castle(D, 408, 310, 5, col=("#E8E0D0", "#B8AC98", "#6A5E4E"), roof=("#8A9AC0", "#4A5A8A", "#1E2A50"), k=0.32))
    sc.append(hill(D, [(100, 380), (220, 356), (340, 372), (500, 350)], 520, ("#F2D890", "#D8B058", "#8A6A28"), 5, inkw=0, sop=(0.2, 0.45), cols=["#FFF0B0", "#C8962E", "#E8C060"]))
    sc.append(grass(6, (100, 360, 500, 520), ["#E8C060", "#C89A3A", "#FFF0B0", "#A87A2A"], 260, (10, 26), 1.4, (-0.2, 0.3)))
    sc.append(f'<rect x="0" y="0" width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0.05), (1, "#1A1004", 0.5)], cx=0.5, cy=0.45, r=0.42)}"/>')
    sc.append(puss(D, 296, 470, 1.0, 7))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # carved gilt frame
    for (r_add, w_, c_) in ((14, 26, GOLD[2]), (14, 20, GOLD[1]), (6, 4, GOLD[0]), (24, 3, GOLD[0]), (0, 3, GOLD[2])):
        out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx + r_add, ry + r_add, 0, 360, 64))}" fill="none" stroke="{c_}" stroke-width="{w_}"/>')
    rnd = random.Random(8)
    for k in range(48):
        a = 2 * math.pi * k / 48
        x, y = cx + math.cos(a) * (rx + 14), cy + math.sin(a) * (ry + 14)
        out.append(f'<path d="{blob(x, y, 5, 3, k, 0.1, 8, math.degrees(a) + 90)}" fill="{GOLD[0]}" opacity="0.8"/>')
        out.append(f'<circle cx="{x + math.cos(a) * 6:.1f}" cy="{y + math.sin(a) * 6:.1f}" r="1.6" fill="{GOLD[2]}"/>')
    for (a, sz) in ((-90, 22), (90, 16)):
        x, y = cx + math.cos(math.radians(a)) * (ry + 16) * 0 , cy + math.sin(math.radians(a)) * (ry + 16)
        out.append(fleuron(cx, y + (6 if a < 0 else -2), sz, GOLD[1], 0 if a > 0 else 180))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx + 27, ry + 27, 0, 360, 64)), "#2A1A04", 1.6, 9, 1, 0.7))
    # brass plaque
    out.append(cast(D, 304, 548, 140, 10, color="#000000", strength=0.5, seed=10))
    plaque = rect_pts(170, 510, 430, 552, 20, 10, 0.3)
    out.append(painted(D, plaque, BRASS, 10, sdir=(0.3, 1), sk=0.2, angle=0, n=20, inkw=1.6, inkc="#3A2408", hi=0.5))
    out.append(tx(301, 541, "PUSS IN BOOTS", CINZEL, 28, "#FFF0B0", ls=4, max_w=240, op=0.7))
    out.append(tx(300, 540, "PUSS IN BOOTS", CINZEL, 28, "#3A2408", ls=4, max_w=240))
    for x in (182, 418):
        out.append(f'<circle cx="{x}" cy="531" r="3.4" fill="{BRASS[2]}"/><circle cx="{x - 1}" cy="530" r="1.2" fill="{BRASS[0]}"/>')
    out.append(tx(300, 60, "", CINZEL, 10, "#000"))
    return finish_b(D, out, 11, "#000000", 0.5)


# ================================================================ 15. the elves and the shoemaker — finished by morning
def shoe_pair(D, cx, base, s, seed, leather=("#D87A4A", "#A0421E", "#4A1A08")):
    """A pair of fine buckled shoes, one in profile and one three-quarter behind it."""
    def L(pts, ox):
        return T(pts, ox, base, s)
    out = [cast(D, cx + 10 * s, base + 2, 110 * s, 10 * s, strength=0.55, seed=seed)]
    for k, ox in enumerate((cx + 26 * s, cx - 20 * s)):
        dk_ = 0.2 if k == 0 else 0
        pal = (mix(leather[0], "#000000", dk_ * 0.5), mix(leather[1], "#000000", dk_), leather[2])
        shoe = L([(-62, 0), (-66, -10), (-56, -22), (-36, -30), (-14, -32), (0, -28), (14, -30), (30, -40), (44, -40), (52, -32), (54, -18), (56, 0)], ox)
        out.append(painted(D, shoe, pal, seed + k, sdir=(0.4, 1), sk=0.18, angle=-10, n=24, inkw=1.6, inkc="#1E0A02", hi=0.5, hik=0.1))
        # opening, sole, heel, stitching
        out.append(f'<path d="{smooth_closed(L([(-14, -32), (0, -27), (16, -30), (30, -38), (16, -36), (0, -33)], ox))}" fill="#2A0E04"/>')
        out.append(painted(D, L([(-64, -2), (56, -2), (56, 3), (-60, 3)], ox), ("#5A3A26", "#2E1A0E", "#0E0602"), seed + 5 + k, sk=0.2, angle=0, n=4, inkw=0.8, hi=0.3))
        out.append(painted(D, L([(34, 0), (56, 0), (56, 10), (36, 10)], ox), ("#5A3A26", "#2E1A0E", "#0E0602"), seed + 6 + k, sk=0.2, angle=-90, n=4, inkw=1, hi=0.3))
        sts = catmull(L([(-60, -8), (-52, -18), (-34, -24), (-16, -24)], ox), 5)
        for j in range(0, len(sts) - 1, 1):
            out.append(f'<path d="M {sts[j][0]:.1f} {sts[j][1]:.1f} L {sts[j][0] + 2:.1f} {sts[j][1] + 0.4:.1f}" stroke="#F6D8A8" stroke-width="1.1"/>')
        # silver buckle on the tongue
        bx, by = L([(-6, -30)], ox)[0]
        out.append(f'<rect x="{bx - 8 * s:.1f}" y="{by - 7 * s:.1f}" width="{16 * s:.1f}" height="{12 * s:.1f}" rx="2" fill="none" stroke="#E8ECF2" stroke-width="{3 * s:.1f}"/>')
        out.append(f'<rect x="{bx - 8 * s:.1f}" y="{by - 7 * s:.1f}" width="{16 * s:.1f}" height="{12 * s:.1f}" rx="2" fill="none" stroke="#6A7080" stroke-width="0.8"/>')
        out.append(taper(L([(-56, -16), (-40, -26), (-20, -28)], ox), 3 * s, 1, "#FFE0C0", 0.6))
    return "".join(out)


def elf_clothes(D, x, y, seed):
    """The tiny suit the shoemaker's wife sewed: a green coat, a red waistcoat, a little shirt and a pointed cap."""
    out = []
    # little shirt folded
    out.append(painted(D, rect_pts(x - 26, y - 8, x + 24, y + 16, 8, seed, 0.6), ("#FFFFFF", "#F2EAD8", "#B8A88A"), seed, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    out.append(pline([(x - 26, y + 2), (x + 24, y + 2)], "#B8A88A", 1, seed, 0.6, 1))
    # coat laid on top: body, sleeves, buttons
    coat = [(x - 20, y - 24), (x - 6, y - 30), (x + 8, y - 30), (x + 20, y - 24), (x + 34, y - 6), (x + 22, y - 2), (x + 16, y - 14), (x + 18, y + 10), (x - 16, y + 10), (x - 14, y - 14), (x - 22, y - 2), (x - 34, y - 6)]
    out.append(painted(D, coat, ("#8ACB7A", "#2E8A4A", "#124A24"), seed + 1, sk=0.2, angle=-90, n=12, inkw=1.4, inkc="#0E2A14", hi=0.4))
    out.append(painted(D, [(x - 6, y - 28), (x + 8, y - 28), (x + 6, y + 8), (x - 4, y + 8)], ("#F28A7A", "#C8302A", "#6A0E0A"), seed + 2, sk=0.2, angle=-90, n=4, inkw=1, hi=0.4))
    for k in range(4):
        out.append(f'<circle cx="{x + 1:.1f}" cy="{y - 22 + k * 8:.1f}" r="1.6" fill="{GOLD[1]}"/>')
    # wee breeches folded beside it, and a tiny pair of buckled shoes
    br = [(x + 34, y - 6), (x + 70, y - 8), (x + 72, y + 22), (x + 60, y + 24), (x + 54, y + 6), (x + 48, y + 24), (x + 36, y + 22)]
    out.append(painted(D, br, ("#C8965E", "#8A5A30", "#3A2410"), seed + 3, sk=0.2, angle=-90, n=6, inkw=1.2, inkc="#2A1404", hi=0.4))
    out.append(pline([(x + 54, y - 6), (x + 54, y + 8)], "#3A2410", 1, seed, 0.6, 1))
    out.append(shoe_pair(D, x - 26, y + 40, 0.34, seed + 9, ("#5A5A6A", "#2A2A36", "#0A0A10")))
    return "".join(out)


def tool_awl(D, x0, y0, x1, y1, seed):
    out = [taper([(x0, y0), (x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.4)], 10, 9, WOOD[1])]
    out.append(taper([(x0, y0), (x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.4)], 3, 3, WOOD[0], 0.6))
    out.append(taper([(x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.4), (x1, y1)], 2.6, 0.6, "#B8BCC8"))
    return "".join(out)


def dancing_elf(x, base, s, col, flip=False, kick=1):
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [taper(catmull(L([(0, -18), (-4, -8), (-2, 0)]), 3), 3 * s, 2.4 * s, col),
           taper(catmull(L([(2, -18), (8 * kick, -12), (14 * kick, -14)]), 3), 3 * s, 2.4 * s, col)]
    out.append(f'<path d="{smooth_closed(L([(-5, -34), (-6, -24), (-4, -16), (6, -16), (7, -24), (5, -34)]))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(0, -40)])[0], 5 * s, 5.4 * s, 3, 0.05, 10)}" fill="{col}"/>')
    out.append(f'<path d="{pd(L([(-5, -43), (5, -43), (14, -58), (16, -54)]))}" fill="{col}"/>')
    out.append(taper(catmull(L([(-4, -32), (-12, -38), (-16, -46)]), 3), 2.4 * s, 1.8 * s, col))
    out.append(taper(catmull(L([(4, -32), (12, -30), (16, -36)]), 3), 2.4 * s, 1.8 * s, col))
    return "".join(out)


@design("the-elves-and-the-shoemaker")
def elves_shoemaker():
    D = Doc2("ft-es")
    # workshop wall: dark plaster and beams by candlelight
    out = [sky(D, [(0, "#2A1E18"), (1, "#4A3424")], 1, 600, ["#3A2A20", "#1A120C", "#5A4030"], 50)]
    out.append(painted(D, rect_pts(-10, 168, 610, 186, 30, 2, 0.4), DARKWOOD, 2, sk=0.2, angle=0, n=20, inkw=1.2, hi=0.2))
    # the moonlit window with two little elves dancing on the sill
    wx0, wy0, wx1, wy1 = 330, 190, 530, 352
    cid = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    night = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#14204A"), (1, "#4A6A9A")])}"/>',
             stars_field(4, (wx0, wy0, wx1, wy1), 30), soft_glow(D, 480, 236, 50, "#E8F0FF", 0.5),
             f'<path d="{blob(480, 236, 16, 16, 5, 0.02, 18)}" fill="#F8F4E6"/>']
    for k in range(6):
        x = wx0 + k * 30
        night.append(f'<path d="{pd([(x, wy1), (x, wy1 - 34 - (k % 3) * 10), (x + 14, wy1 - 50 - (k % 2) * 12), (x + 28, wy1 - 34), (x + 28, wy1)])}" fill="#1A2440"/>')
        night.append(f'<rect x="{x + 10:.1f}" y="{wy1 - 24:.1f}" width="6" height="7" fill="#FFD27A"/>')
    out.append(f'<g {cid}>{"".join(night)}</g>')
    out.append(f'<path d="M {wx0 + 100} {wy0} L {wx0 + 100} {wy1} M {wx0} {wy0 + 64} L {wx1} {wy0 + 64}" stroke="#3A2414" stroke-width="7"/>')
    out.append(f'<path d="{hg.org_rect(wx0 - 10, wy0 - 10, wx1 - wx0 + 20, wy1 - wy0 + 20, 6, 0.5, 20, 2)} {hg.org_rect(wx0, wy0, wx1 - wx0, wy1 - wy0, 7, 0.4, 20, 1)}" fill-rule="evenodd" fill="#4A2E1A"/>')
    out.append(painted(D, rect_pts(wx0 - 20, wy1 + 4, wx1 + 20, wy1 + 16, 20, 8, 0.3), DARKWOOD, 8, sk=0.2, angle=0, n=10, inkw=1.2, hi=0.3))
    out.append(soft_glow(D, 430, wy1 - 30, 110, "#C8D8FF", 0.25))
    out.append(dancing_elf(392, wy1 + 4, 1.55, "#0A0C1A"))
    out.append(dancing_elf(470, wy1 + 4, 1.45, "#0A0C1A", flip=True))
    # moonbeam falling into the room
    out.append(f'<path d="{pd([(wx0, wy1), (wx1, wy0 + 40), (wx1 - 60, 600), (wx0 - 240, 600)])}" fill="#C8D8FF" opacity="0.07"/>')
    # shelf with lasts and a spool
    out.append(painted(D, rect_pts(30, 262, 290, 274, 20, 9, 0.3), WOOD, 9, sk=0.2, angle=0, n=10, inkw=1.2, hi=0.3))
    for k, x in enumerate((70, 120, 170)):
        last = [(x - 22, 262), (x - 24, 252), (x - 16, 242), (x + 4, 238), (x + 22, 242), (x + 26, 252), (x + 22, 262)]
        out.append(painted(D, last, ("#E2B47A", "#B07A3E", "#5E3A18"), 10 + k, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    for k in range(3):
        out.append(painted(D, rect_pts(214 + k * 22, 234, 230 + k * 22, 262, 6, 11 + k, 0.3), ("#F2E2C0", "#D8C098", "#8A7448"), 11 + k, sk=0.2, angle=0, n=4, inkw=1, hi=0.4))
        out.append(f'<rect x="{214 + k * 22}" y="240" width="16" height="16" fill="{["#C8302A", "#2E6A9A", "#3A3A3A"][k]}"/>')
    # the bench
    out.append(painted(D, rect_pts(-10, 410, 610, 620, 30, 15, 0.4), WOOD, 15, sdir=(0.2, 1), sk=0.06, angle=0, n=80, inkw=1.6, hi=0.25))
    out.append(taper([(-10, 412), (300, 410), (610, 412)], 4, 4, "#F2C890", 0.6))
    for k in range(4):
        out.append(pline([(-10, 440 + k * 40), (610, 436 + k * 42)], "#5A3418", 1.4, k, 0.4, 1))
    out.append(soft_glow(D, 120, 330, 320, "#FFC060", 0.45))
    # candle, leather offcuts, tools, the finished shoes, the tiny suit
    out.append(candle(D, 86, 424, 92, 16, w=20, glow_r=220))
    for k, (x, y, a, c) in enumerate(((170, 520, -20, "#B85A2A"), (548, 438, 30, "#8A3A1A"))):
        out.append(painted(D, blob_pts(x, y, 40, 17, 20 + k, 0.2, 12, a), (lt(c, 0.3), c, dk(c, 0.5)), 20 + k, sk=0.2, angle=a, n=8, inkw=1.2, hi=0.3))
    out.append(tool_awl(D, 470, 560, 560, 520, 22))
    hx, hy = 520, 470
    out.append(taper([(hx - 50, hy + 26), (hx + 26, hy - 6)], 8, 7, WOOD[1]))
    out.append(painted(D, rect_pts(hx + 18, hy - 28, hx + 38, hy + 4, 6, 23, 0.3), ("#C8CCD8", "#7A8090", "#2A303A"), 23, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.5))
    out.append(shoe_pair(D, 290, 476, 1.6, 24))
    out.append(f'<g transform="translate(150 530) scale(1.25) translate(-150 -530)">{elf_clothes(D, 150, 530, 25)}</g>')
    out.append(ink(smooth_open([(330, 540), (380, 548), (430, 532), (470, 544), (500, 530)]), "#C8302A", 1.6, 26, 1, 0.9))
    out.append(taper([(500, 530), (512, 524)], 2, 1, "#B8BCC8"))
    # lettering
    out.append(tx(300, 82, "BROTHERS GRIMM", CINZEL, 16, "#F2D8A8", ls=6, max_w=300))
    out.append(letters(D, 300, 140, "The Elves & the Shoemaker", SERIF_IT, 48, "#FFE8C0", ["#FFF4DA", "#F2C88A", "#FFE0A0"], 27, max_w=460,
                       shadow="#100804", soff=(0.02, 0.05), angle=-40, wob=0.5))
    return finish_b(D, out, 28, "#000000", 0.5)


# ================================================================ 16. goldilocks — three bowls of porridge, seen from above
def porridge_bowl(D, cx, cy, r, seed, empty=False, rim=("#F2E8D8", "#D8C8B0", "#8A7A62"), band="#2E5A9A"):
    """Painted earthenware bowl seen from above, full of porridge with honey, or scraped empty."""
    out = [cast(D, cx + r * 0.16, cy + r * 0.2, r * 1.12, r * 1.08, strength=0.4, seed=seed)]
    outer = blob_pts(cx, cy, r, r, seed, 0.012, 32)
    out.append(painted(D, outer, rim, seed, sdir=(0.6, 0.7), sk=0.12, angle=-40, n=20, inkw=1.8, inkc="#4A3A2A", hi=0.5))
    # painted band and little flowers round the rim
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.9:.1f}" fill="none" stroke="{band}" stroke-width="{max(2, r * 0.05):.1f}" opacity="0.85"/>')
    for k in range(12):
        a = 2 * math.pi * k / 12
        x, y = cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.2, r * 0.03):.1f}" fill="{band}"/>')
    inner_r = r * 0.82
    if empty:
        out.append(f'<path d="{blob(cx, cy, inner_r, inner_r, seed + 1, 0.01, 28)}" fill="{D.rad([(0, "#FFFFFF"), (0.7, "#EDE2D0"), (1, "#B8A88E")], cx=0.55, cy=0.6)}"/>')
        rnd = random.Random(seed)
        for k in range(14):
            a = rnd.uniform(0, 6.28)
            rr = rnd.uniform(0.4, 0.95) * inner_r
            out.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(1.5, 3.2), rnd.uniform(1, 2), seed + k, 0.2, 8)}" fill="#E8D2A8"/>')
        out.append(taper([(cx - inner_r * 0.5, cy + inner_r * 0.5), (cx, cy + inner_r * 0.62), (cx + inner_r * 0.5, cy + inner_r * 0.5)], 1, 4, "#D8C49A", 0.6))
    else:
        out.append(f'<path d="{blob(cx, cy, inner_r, inner_r, seed + 1, 0.01, 28)}" fill="#8A7A62" opacity="0.5"/>')
        por = blob_pts(cx, cy + 1, inner_r * 0.95, inner_r * 0.95, seed + 2, 0.03, 24)
        out.append(painted(D, por, ("#FFF6DC", "#EEDCB2", "#B89A68"), seed + 2, sdir=(0.5, 0.6), sk=0.12, angle=30, n=int(r * 0.8), inkw=0, hi=0.4, curve=0.6))
        rnd = random.Random(seed)
        for k in range(int(r * 0.5)):
            a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * inner_r * 0.85
            out.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(1.5, 3), rnd.uniform(1, 2.2), seed + k, 0.2, 8)}" fill="{rnd.choice(["#FFFFFF", "#D8C090", "#C8A870"])}" opacity="0.7"/>')
        # golden honey swirl and a pat of butter melting
        sp = [(cx + math.cos(t) * inner_r * 0.06 * t, cy + math.sin(t) * inner_r * 0.06 * t) for t in [i * 0.4 for i in range(1, 30)]]
        out.append(taper(sp, 2, max(3, r * 0.08), "#E8A830", 0.85))
        out.append(taper(sp, 0.6, max(1, r * 0.03), "#FFE08A", 0.85))
        out.append(f'<path d="{hg.org_rect(cx - r * 0.12, cy - r * 0.42, r * 0.22, r * 0.16, seed, 0.3, 8, 2)}" fill="#FFF0A0"/>')
        out.append(steam_wisps(cx, cy - inner_r * 0.3, r * 0.7, seed, "#FFFFFF", 2, r * 0.35, max(3, r * 0.06), 0.6))
    return "".join(out)


def spoon(D, x, y, L, ang, seed, pal=("#F2F4F8", "#B8C0CC", "#5A6270")):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    bowl = blob_pts(x, y, L * 0.16, L * 0.11, seed, 0.02, 14, ang)
    out = [cast(D, x + 4 + ux * L * 0.4, y + 5 + uy * L * 0.4, L * 0.55, L * 0.08, strength=0.35, seed=seed)]
    out.append(taper([(x + ux * L * 0.12, y + uy * L * 0.12), (x + ux * L * 0.55, y + uy * L * 0.55), (x + ux * L, y + uy * L)], L * 0.035, L * 0.06, pal[1]))
    out.append(taper([(x + ux * L * 0.15, y + uy * L * 0.15), (x + ux * L * 0.95, y + uy * L * 0.95)], L * 0.012, L * 0.02, pal[0], 0.9))
    out.append(painted(D, bowl, pal, seed, sk=0.2, angle=ang, n=4, inkw=1.2, inkc="#3A404A", hi=0.6))
    return "".join(out)


@design("goldilocks")
def goldilocks():
    D = Doc2("ft-gl")
    # tabletop of scrubbed pine, a checked cloth runner
    out = [sky(D, [(0, "#D8A86A"), (1, "#B8844A")], 1, 600, ["#E8BC80", "#9A6A38", "#F2CC90"], 0)]
    from brasil_painted import wood_planks, cloth
    out.append(wood_planks(D, 0, 600, 3, ("#E8BC84", "#C08A50", "#6A4420"), n=5, vertical=True))
    out.append(cloth(D, [(-30, 196), (630, 166), (630, 446), (-30, 476)], "#C8302A", 4, cell=16, rot_=-3, folds=[((40, 200), (200, 330), (180, 470))]))
    # three bowls: Great Huge Bear's, Middle-sized Bear's, Little Wee Bear's (scraped clean)
    out.append(porridge_bowl(D, 170, 300, 112, 5, band="#2E5A9A"))
    out.append(spoon(D, 240, 400, 150, 18, 6))
    out.append(porridge_bowl(D, 378, 268, 82, 7, band="#3E7A4A"))
    out.append(spoon(D, 452, 330, 110, 60, 8))
    out.append(porridge_bowl(D, 494, 400, 54, 9, empty=True, band="#B8302A"))
    out.append(spoon(D, 472, 410, 72, 160, 10))
    # wildflowers in a cup, a honey pot, crumbs
    out.append(painted(D, blob_pts(76, 488, 30, 30, 11, 0.02, 20), ("#FFFFFF", "#E8E0F0", "#9A90B0"), 11, sk=0.15, n=8, inkw=1.6, hi=0.4))
    for k in range(9):
        a = math.radians(k * 40)
        out.append(daisy(76 + math.cos(a) * 16, 488 + math.sin(a) * 16, 9, 12 + k, "#FFFFFF" if k % 2 else "#C8A0E8"))
    out.append(daisy(76, 488, 11, 30))
    hx_, hy_ = 330, 470
    out.append(painted(D, blob_pts(hx_, hy_, 34, 34, 13, 0.02, 20), ("#FFE8A0", "#E8B040", "#8A5A10"), 13, sk=0.2, n=10, inkw=1.6, hi=0.5))
    out.append(f'<circle cx="{hx_}" cy="{hy_}" r="22" fill="#C88A1A"/><circle cx="{hx_ - 4}" cy="{hy_ - 4}" r="10" fill="#F6C84A" opacity="0.7"/>')
    for k in range(4):
        out.append(f'<circle cx="{hx_}" cy="{hy_}" r="{26 + k * 2}" fill="none" stroke="#8A5A10" stroke-width="0.8" opacity="0.5"/>')
    out.append(taper([(hx_ + 10, hy_ - 6), (hx_ + 40, hy_ - 30), (hx_ + 60, hy_ - 40)], 4, 7, WOOD[1]))
    rnd = random.Random(14)
    for k in range(18):
        out.append(f'<circle cx="{rnd.uniform(240, 600):.1f}" cy="{rnd.uniform(470, 560):.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="#F2DCA8"/>')
    # a long golden hair left on the cloth
    out.append(pline([(410, 196), (450, 186), (490, 200), (530, 186), (566, 194)], "#E8B840", 1.4, 15, 0.95, 1))
    # lettering: a cream band across the top, and a line on the table
    band = [(-10, 40), (610, 40), (610, 150), (-10, 158)]
    out.append(painted(D, band, ("#FFFBF0", "#F6EDDA", "#C8B898"), 16, sdir=(0, 1), sk=0.06, angle=0, n=30, inkw=1.6, inkc="#7A5A3A", hi=0.2))
    out.append(letters(D, 300, 116, "Goldilocks", SERIF_IT, 66, "#C88A1A", ["#E8B040", "#9A6410", "#F6CC60"], 17, max_w=420,
                       shadow="#E8D8B8", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 144, "AND THE THREE BEARS", CINZEL, 17, "#6A3A1A", ls=6, max_w=300))
    out.append(tx(302, 543, "“Somebody has been at my porridge!”", SERIF_IT, 32, "#2A1406", max_w=430, op=0.6))
    out.append(tx(300, 540, "“Somebody has been at my porridge!”", SERIF_IT, 32, "#FFF6E0", max_w=430))
    return finish_b(D, out, 18, INK, 0.6)


# ================================================================ 17. the ugly duckling — his reflection is a swan
def swan(D, ox, oy, s, seed, flip=False, pal=("#FFFFFF", "#F2EEE8", "#A8A8B8"), ink_c="#4A4A5A"):
    """A mute swan gliding, facing left (flip -> right); (ox, oy) = waterline under the breast. s=1 ~ 200 px long."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    out = []
    body = L([(-60, -8), (-50, -30), (-20, -44), (20, -50), (60, -48), (96, -60), (104, -54), (92, -36), (80, -20), (40, -2), (-30, 0)])
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.15, angle=-10, n=40, inkw=1.6, inkc=ink_c, hi=0.5))
    # raised wing (arched, feathers)
    wing = L([(-14, -40), (10, -64), (44, -78), (82, -82), (100, -70), (76, -56), (40, -46), (6, -36)])
    out.append(painted(D, wing, pal, seed + 1, sdir=(0.3, 1), sk=0.16, angle=-20, n=30, inkw=1.4, inkc=ink_c, hi=0.5))
    for k in range(6):
        a = L([(20 + k * 12, -56 - k * 2)])[0]
        b = L([(30 + k * 12, -46 - k * 1.5)])[0]
        out.append(pline([a, b], pal[2], 1.2, seed + k, 0.6, 1))
    # S-curved neck and head
    neck = L([(-46, -26), (-60, -50), (-66, -86), (-60, -114), (-48, -126), (-34, -122), (-38, -112), (-48, -102), (-50, -80), (-40, -52), (-28, -34)])
    out.append(painted(D, neck, pal, seed + 2, sdir=(0.6, 0.4), sk=0.18, angle=-90, n=14, inkw=1.5, inkc=ink_c, hi=0.5))
    # beak: orange with the black knob
    beak = L([(-50, -124), (-66, -118), (-78, -110), (-70, -106), (-54, -110)])
    out.append(painted(D, beak, ("#FFB070", "#E8702A", "#8A3A10"), seed + 3, sk=0.2, angle=-10, n=4, inkw=1.2, inkc="#3A1A08", hi=0.5))
    out.append(f'<path d="{blob(*L([(-52, -120)])[0], 5 * s, 6 * s, seed, 0.1, 8)}" fill="#1A1A1A"/>')
    ex, ey = L([(-44, -118)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2 * s:.1f}" fill="#1A1A1A"/>')
    return "".join(out)


def cygnet(D, ox, oy, s, seed, flip=False):
    """The 'ugly duckling': a scruffy grey cygnet floating, facing left; (ox, oy) = waterline."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    pal = ("#B8B4B0", "#7A7672", "#34302E")
    out = []
    body = L([(-34, -4), (-30, -20), (-12, -30), (12, -30), (32, -24), (44, -30), (40, -16), (30, -4), (0, 0)])
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=-20, n=40, slen=(4, 10), sw=(0.5, 1.4), cols=["#D8D4D0", "#4A4642", "#9A9690"], inkw=1.4, inkc="#24201E", hi=0.4))
    rnd = random.Random(seed)
    for k in range(14):
        x, y = L([(rnd.uniform(-28, 36), rnd.uniform(-28, -10))])[0]
        out.append(pline([(x, y), (x + rnd.uniform(-4, 4), y - rnd.uniform(3, 6))], "#5A5652", 1, seed + k, 0.8, 1))
    neck = L([(-22, -22), (-28, -38), (-26, -50), (-16, -54), (-12, -46), (-14, -34), (-10, -24)])
    out.append(painted(D, neck, pal, seed + 1, sk=0.2, angle=-90, n=10, slen=(3, 8), sw=(0.5, 1.2), inkw=1.3, inkc="#24201E", hi=0.4))
    for k in range(3):
        x, y = L([(-22 + k * 4, -54 + k)])[0]
        out.append(pline([(x, y), (x + rnd.uniform(-3, 3), y - 5)], "#5A5652", 1, seed + k, 0.8, 1))
    beak = L([(-26, -50), (-38, -46), (-36, -42), (-26, -44)])
    out.append(painted(D, beak, ("#6A6460", "#3A3632", "#1A1614"), seed + 2, sk=0.2, n=3, inkw=1, hi=0.4))
    ex, ey = L([(-20, -48)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.8 * s:.1f}" fill="#100C0A"/><circle cx="{ex - 0.5:.1f}" cy="{ey - 0.6:.1f}" r="{0.6 * s:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def cattail(D, x, base, h, seed, lean=0.0):
    top = (x + lean * h, base - h)
    out = [pline([(x, base), (x + lean * h * 0.5, base - h * 0.5), top], "#3A5A2A", 2.2, seed, 0.95, 1)]
    hx, hy = x + lean * h * 0.82, base - h * 0.82
    out.append(painted(D, [(hx - 4, hy - 16), (hx + 4, hy - 16), (hx + 5, hy + 16), (hx - 5, hy + 16)], ("#B8804A", "#7A4A22", "#3A200A"), seed, sk=0.25, angle=-90, n=4, inkw=1, hi=0.4))
    return "".join(out)


def reeds(D, x0, x1, base, seed, n=24, h=(60, 150), cols=("#5A7A3A", "#3A5A2A", "#8AA05A")):
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        x = rnd.uniform(x0, x1)
        hh = rnd.uniform(*h)
        lean = rnd.uniform(-0.25, 0.25)
        out.append(taper([(x, base), (x + lean * hh * 0.4, base - hh * 0.5), (x + lean * hh, base - hh)], 5, 0.5, rnd.choice(cols)))
    return "".join(out)


@design("the-ugly-duckling")
def ugly_duckling():
    D = Doc2("ft-ud")
    wl = 316
    out = [sky(D, [(0, "#9ABCD8"), (0.5, "#E8D8D0"), (1, "#FCE2C0")], 1, wl + 4, ["#B8D0E8", "#FFFFFF", "#F8D0B0"], 40)]
    out.append(soft_glow(D, 410, 250, 160, "#FFF0D0", 0.6))
    out.append(puff_cloud(D, 170, 200, 150, 3, ("#FFFFFF", "#FBF0EA", "#D8C8D8"), op=0.8))
    # far bank of willows and alders, misty
    out.append(hill(D, [(-20, 300), (120, 286), (260, 294), (400, 280), (620, 292)], wl + 2, ("#B8C8A8", "#98A888", "#6A7A60"), 4, inkw=0, sop=(0.1, 0.3)))
    out.append(dab_crown(D, 90, 268, 90, 34, [("#B8C8A0", "#98AA80", "#6A7A58")], 5, n=80, size=(5, 10), inkw=0))
    out.append(dab_crown(D, 520, 262, 110, 40, [("#B8C8A0", "#98AA80", "#6A7A58")], 6, n=90, size=(5, 10), inkw=0))
    out.append(mist(D, 300, 40, 7, "#FFF6EE", 0.6))
    # the water, glassy
    out.append(sea(D, wl, 620, [(0, "#C8D4DA"), (0.4, "#A8BCC8"), (1, "#6A8AA0")], 8, ["#D8E2E8", "#8AA4B8", "#FFFFFF"], 60))
    # reflection of the far bank
    out.append(f'<path d="{smooth_closed([(-20, wl), (620, wl), (620, wl + 40), (-20, wl + 30)])}" fill="#8A9A80" opacity="0.25"/>')
    # the duckling, and his reflection: a swan
    rx_, ry_ = 300, wl
    cid = D.clip(f'<rect x="0" y="{wl + 1}" width="600" height="300"/>')
    refl = swan(D, rx_ + 34, wl, 1.3, 9, flip=False, pal=("#FFFFFF", "#F2F2F4", "#B8C0CC"), ink_c="#8A94A6")
    rip = []
    for k in range(10):
        y = wl + 8 + k * 14
        rip.append(f'<path d="M 120 {y} L 480 {y}" stroke="#B8C8D4" stroke-width="{1.2 + k * 0.3:.1f}" opacity="0.4"/>')
    out.append(f'<g {cid} opacity="0.92"><g transform="translate(0 {2 * wl}) scale(1 -1)">{refl}</g>{"".join(rip)}</g>')
    out.append(soft_glow(D, rx_ - 20, wl + 70, 120, "#FFFFFF", 0.25))
    out.append(wave_lines(10, (100, wl + 6, 500, wl + 160), ["#FFFFFF", "#D8E4EC"], 40, (14, 40), 1.6, 1.5, (0.4, 0.8)))
    for k in range(3):
        out.append(f'<path d="{smooth_closed(ell_pts(rx_ + 6, wl + 2, 40 + k * 22, 4 + k * 3, 0, 360, 24))}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="{0.6 - k * 0.15:.2f}"/>')
    out.append(cygnet(D, rx_, wl + 2, 1.55, 11))
    # reeds and cattails at both edges; a dragonfly
    out.append(reeds(D, -10, 110, 600, 12, 30, (180, 320)))
    out.append(reeds(D, 490, 610, 600, 13, 30, (160, 300)))
    for k, (x, h, l) in enumerate(((40, 290, 0.08), (82, 240, 0.12), (520, 270, -0.1), (566, 300, -0.05))):
        out.append(cattail(D, x, 600, h, 14 + k, l))
    for k, (x, y, s_, a) in enumerate(((150, 540, 34, 0), (200, 572, 26, 20), (430, 556, 30, 160), (380, 582, 22, 180))):
        out.append(painted(D, blob_pts(x, y, s_, s_ * 0.36, 20 + k, 0.05, 16, a), ("#8AB86A", "#4E8A3E", "#22502A"), 20 + k, sk=0.2, n=6, inkw=1.2, hi=0.3))
    out.append(wild_rose(D, 170, 548, 9, 25, ("#FFFFFF", "#F8F0F4", "#D0B8C8")))
    # lettering
    out.append(letters(D, 300, 114, "The Ugly Duckling", SERIF_IT, 58, "#3A4A6A", ["#4A5A80", "#24304A", "#6A7AA0"], 26, max_w=430,
                       shadow="#FFF2E2", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 146, "HANS CHRISTIAN ANDERSEN · 1843", CINZEL, 15, "#4A4A60", ls=3, max_w=380))
    out.append(tx(300, 528, "He was a swan all along.", SERIF_IT, 30, "#24304A", max_w=360))
    return finish_b(D, out, 27, INK, 0.5)


# ================================================================ 18. the snow queen — her white sleigh under the northern lights
def bilibin_border(D, seed, band=34, c1="#1E3A6A", c2="#F2ECE0", c3="#C8A050", motif="snow"):
    """Ornamental storybook border in the Russian-folk manner: a solid band with repeating motifs and corner medallions."""
    out = []
    o = f"M 0 0 L 600 0 L 600 600 L 0 600 Z M {band} {band} L {band} {600 - band} L {600 - band} {600 - band} L {600 - band} {band} Z"
    out.append(f'<path d="{o}" fill="{c1}" fill-rule="evenodd"/>')
    out.append(strokes(D.nid(), o, (0, 0, 600, 600), [lt(c1, 0.2), dk(c1, 0.3)], seed, n=200, angle=0, length=(20, 60), width=(1, 3), opacity=(0.15, 0.35)))
    for r_ in (6, band - 6):
        out.append(f'<rect x="{r_}" y="{r_}" width="{600 - 2 * r_}" height="{600 - 2 * r_}" fill="none" stroke="{c3}" stroke-width="1.6"/>')
    # repeating motif along the band
    m = band / 2
    step = 38
    for k in range(int(600 / step) + 1):
        t = k * step + step / 2
        for (x, y) in ((t, m), (t, 600 - m), (m, t), (600 - m, t)):
            if (x < band * 1.6 or x > 600 - band * 1.6) and (y < band * 1.6 or y > 600 - band * 1.6):
                continue
            if motif == "snow":
                for j in range(6):
                    a = math.radians(j * 60)
                    out.append(f'<path d="M {x:.1f} {y:.1f} L {x + math.cos(a) * 8:.1f} {y + math.sin(a) * 8:.1f}" stroke="{c2}" stroke-width="1.8" stroke-linecap="round"/>')
                    out.append(f'<circle cx="{x + math.cos(a) * 9:.1f}" cy="{y + math.sin(a) * 9:.1f}" r="1.3" fill="{c2}"/>')
            out.append(f'<circle cx="{x + step / 2:.1f}" cy="{y:.1f}" r="1.8" fill="{c3}"/>' if y in (m, 600 - m) else f'<circle cx="{x:.1f}" cy="{y + step / 2:.1f}" r="1.8" fill="{c3}"/>')
    # corner medallions
    for (x, y) in ((m + 3, m + 3), (600 - m - 3, m + 3), (m + 3, 600 - m - 3), (600 - m - 3, 600 - m - 3)):
        out.append(f'<circle cx="{x}" cy="{y}" r="{band * 0.62:.1f}" fill="{c2}" stroke="{c3}" stroke-width="2"/>')
        for j in range(8):
            a = math.radians(j * 45)
            out.append(f'<path d="{blob(x + math.cos(a) * band * 0.3, y + math.sin(a) * band * 0.3, band * 0.2, band * 0.09, seed + j, 0.05, 8, j * 45)}" fill="{c1}"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="{band * 0.12:.1f}" fill="{c3}"/>')
    return "".join(out)


def aurora(D, seed, y0=90, y1=300, cols=("#7AF0C0", "#5AC8E8", "#C890F0")):
    rnd = random.Random(seed)
    out = []
    for k in range(5):
        base = y0 + (y1 - y0) * rnd.uniform(0.3, 0.8)
        pts = [(x, base + math.sin(x / 70 + k * 1.3) * 26 + rnd.uniform(-6, 6)) for x in range(-20, 640, 40)]
        col = cols[k % len(cols)]
        for i in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            h = rnd.uniform(60, 130)
            g = D.lin([(0, col, 0), (0.7, col, 0.35), (1, col, 0.0)], 0, 0, 0, 1)
            out.append(f'<path d="M {xa:.1f} {ya:.1f} L {xb:.1f} {yb:.1f} L {xb:.1f} {yb - h:.1f} L {xa:.1f} {ya - h * 0.9:.1f} Z" fill="{g}"/>')
        out.append(taper(catmull(pts, 4), 2, 2, lt(col, 0.4), 0.5))
    return "".join(out)


def ice_palace(D, cx, base, seed, k=1.0):
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, base - 60 * k, 160 * k, "#C8F0FF", 0.45)]
    spires = [(-120, 14, 60), (-86, 18, 110), (-50, 16, 80), (-18, 24, 170), (16, 20, 130), (48, 16, 96), (80, 20, 120), (116, 12, 64), (0, 30, 70)]
    for (dx, w, h) in sorted(spires, key=lambda t: -t[2]):
        x = cx + dx * k
        w *= k
        h *= k
        pts = [(x - w / 2, base), (x - w / 2, base - h * 0.72), (x, base - h), (x + w / 2, base - h * 0.72), (x + w / 2, base)]
        out.append(f'<path d="{pd(pts)}" fill="{D.lin([(0, "#F2FCFF"), (0.5, "#A8D8F0"), (1, "#6A9AD0")], 0, 0, 1, 0)}" opacity="0.92"/>')
        out.append(f'<path d="{pd([(x - w / 2, base), (x - w / 2, base - h * 0.72), (x, base - h), (x, base)])}" fill="#FFFFFF" opacity="0.35"/>')
        out.append(ink(pd(pts), "#4A7AB0", 1.1, seed + int(dx), 1, 0.7))
        out.append(f'<path d="M {x:.1f} {base - h:.1f} L {x:.1f} {base:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="0.6"/>')
    return "".join(out)


def snow_queen_sleigh(D, x, y, s, seed):
    """The Snow Queen's great white sledge flying, she tall and slender in white furs, Kay's little sledge tied behind."""
    def L(pts):
        return T(pts, x, y, s, False, -8)
    out = []
    # trail of glittering snow
    trail = catmull(L([(60, 4), (140, 18), (230, 10), (320, 30)]), 8)
    rnd = random.Random(seed)
    for (px, py) in trail:
        for _ in range(4):
            out.append(f'<circle cx="{px + rnd.uniform(-10, 10):.1f}" cy="{py + rnd.uniform(-10, 10):.1f}" r="{rnd.uniform(0.6, 2.2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    # Kay's sledge on a rope behind
    out.append(pline(L([(46, -4), (80, 2), (104, -2)]), "#E8F0FF", 1.2, seed, 0.9, 1))
    out.append(painted(D, L([(100, -10), (132, -10), (136, -4), (100, -4)]), ("#E8A870", "#B06A30", "#5A3010"), seed, sk=0.2, n=3, inkw=1, hi=0.4))
    out.append(pline(L([(96, -2), (100, 0), (138, 0), (142, -6)]), "#5A3010", 1.4, seed, 0.9, 1))
    out.append(f'<path d="{blob(*L([(116, -16)])[0], 5 * s, 6 * s, seed, 0.05, 8)}" fill="#3A2A4A"/>')
    # the sledge: swan-necked prow, white body, silver runners
    body = L([(-56, -14), (-60, -30), (-50, -44), (-40, -36), (-36, -22), (30, -20), (46, -30), (48, -10), (36, 0), (-44, 0)])
    out.append(painted(D, body, SNOW, seed + 1, sdir=(0.3, 1), sk=0.2, angle=0, n=16, inkw=1.4, inkc="#4A6A9A", hi=0.6))
    out.append(pline(L([(-64, 6), (-40, 8), (40, 6), (54, -2)]), "#C8D8F0", 2.6, seed, 1, 1))
    out.append(pline(L([(-64, 6), (-70, 0), (-66, -6)]), "#C8D8F0", 2.2, seed, 1, 1))
    # the Snow Queen: tall white fur cloak and a crown of ice
    q = L([(-14, -20), (-18, -48), (-14, -76), (-8, -92), (2, -94), (8, -84), (10, -60), (16, -40), (22, -20)])
    out.append(painted(D, q, ("#FFFFFF", "#E8F0FA", "#9AB0D0"), seed + 2, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=12, inkw=1.3, inkc="#4A6A9A", hi=0.6))
    hx, hy = L([(-2, -100)])[0]
    out.append(f'<path d="{blob(hx, hy, 6 * s, 7 * s, seed, 0.05, 10)}" fill="#F2F4FF" stroke="#4A6A9A" stroke-width="1"/>')
    for j in range(5):
        a, b = L([(-7 + j * 3.5, -105)])[0], L([(-8 + j * 4, -118 + abs(j - 2) * 4)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#DCF4FF" stroke-width="2.2" stroke-linecap="round"/>')
    out.append(soft_glow(D, hx, hy - 8, 30 * s, "#DCF4FF", 0.5))
    # long veil streaming back
    out.append(taper(catmull(L([(2, -96), (24, -92), (52, -80), (80, -76)]), 6), 6 * s, 1, "#F2F8FF", 0.75))
    return "".join(out)


@design("the-snow-queen")
def snow_queen():
    D = Doc2("ft-sq")
    out = [sky(D, [(0, "#06102A"), (0.5, "#142E5A"), (0.8, "#2E5A8A"), (1, "#7AA0C8")], 1, 600, ["#14285A", "#06102A", "#3A6A9A"], 40)]
    out.append(stars_field(2, (0, 0, 600, 380), 120))
    out.append(aurora(D, 3, 120, 330))
    # snowfields and the ice palace on the far horizon
    out.append(hill(D, [(-20, 420), (120, 404), (260, 414), (400, 398), (620, 410)], 620, ("#FFFFFF", "#C8DCF0", "#7A9ACA"), 4, inkw=0, sop=(0.1, 0.3)))
    out.append(ice_palace(D, 300, 412, 5, 0.9))
    out.append(hill(D, [(-20, 470), (180, 452), (340, 466), (500, 446), (620, 458)], 620, ("#FFFFFF", "#DCE8F6", "#8AA8D0"), 6, inkw=0, sop=(0.1, 0.25)))
    rnd = random.Random(7)
    for k in range(14):
        x = rnd.choice([rnd.uniform(40, 170), rnd.uniform(430, 560)])
        out.append(conifer(x, 480 + rnd.uniform(-8, 8), rnd.uniform(40, 80), "#1A2E50", k, width=0.34, light="#E8F2FF"))
    out.append(snowfall(8, (34, 34, 566, 566), 120, (0.8, 2.4)))
    # the sleigh crossing the sky
    out.append(snow_queen_sleigh(D, 210, 268, 1.05, 9))
    out.append(bilibin_border(D, 10))
    # title plate at the top band
    plate = rect_pts(150, 64, 450, 132, 20, 11, 0.3)
    out.append(painted(D, plate, ("#FFFFFF", "#F2ECE0", "#B8A888"), 11, sk=0.1, angle=0, n=20, inkw=1.8, inkc="#1E3A6A", hi=0.3))
    out.append(rule_frame(D, 156, 70, 444, 126, "#C8A050", 1.4, 0, seed=12))
    out.append(gilt(D, 300, 112, "The Snow Queen", SERIF_IT, 42, max_w=270, seed=13, deboss="#1E3A6A", dop=0.4, pal="gold"))
    out.append(tx(300, 537, "HANS CHRISTIAN ANDERSEN · 1844", CINZEL, 16, "#1E3A6A", ls=3, max_w=380))
    return finish_b(D, out, 14, "#000010", 0.5)


# ================================================================ 19. the fox and the grapes — Aesop: sour grapes
def grape_bunch(D, cx, top, w, h, seed, pal=("#B88AD8", "#5A2A8A", "#24083E")):
    rnd = random.Random(seed)
    berries = []
    rows = int(h / (w * 0.16))
    for r in range(rows):
        t = r / max(1, rows - 1)
        rowc = max(1, int((1 - t * 0.85) * w / (w * 0.17)))
        y = top + 10 + r * w * 0.14
        for j in range(rowc):
            x = cx - (rowc - 1) * w * 0.085 + j * w * 0.17 + rnd.uniform(-2, 2) + math.sin(r) * 3
            berries.append((x, y + rnd.uniform(-2, 2), w * rnd.uniform(0.085, 0.1)))
    out = [taper([(cx + 4, top - 14), (cx, top + 4), (cx - 2, top + h * 0.6)], 4, 1.5, "#5A3A1A")]
    for k, (x, y, r) in enumerate(sorted(berries, key=lambda b: b[1])):
        out.append(painted(D, blob_pts(x, y, r, r * 1.08, seed + k, 0.03, 12), pal, seed + k, sdir=(0.5, 0.7), sk=0.2, angle=-60, n=3, inkw=0.9, inkc="#14031E", hi=0.3))
        out.append(f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.22:.1f}" fill="#FFFFFF" opacity="0.75"/>')
        out.append(f'<path d="{blob(x + r * 0.2, y + r * 0.1, r * 0.6, r * 0.5, seed + k, 0.2, 8)}" fill="#D8C8F0" opacity="0.18"/>')
    return "".join(out)


def vine_leaf(D, x, y, s, ang, seed, pal=(("#C8C060", "#8A9A3A", "#3A4A1A"))):
    """Five-lobed grapevine leaf, base at (x, y) pointing toward ang."""
    pts = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        r = 1 + 0.17 * math.cos(5 * t) + 0.04 * math.cos(10 * t) - 0.3 * math.exp(-((t - math.pi) ** 2) / 0.03)
        pts.append((math.sin(t) * r * s * 0.6, -math.cos(t) * r * s * 0.6 - s * 0.55))
    pts = [(x + px, y + py) for px, py in pts]
    pts = rot(pts, x, y, ang + 90)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.16, angle=ang, n=int(s * 0.5) + 6, inkw=1.2, inkc="#2A3010", hi=0.35)]
    cx, cy = rot([(x, y - s * 0.55)], x, y, ang + 90)[0]
    for k in range(5):
        a = math.radians(ang + 90 - 90 + k * 72 - 144 + 180)
        out.append(pline([(cx, cy), (cx + math.cos(a) * s * 0.55, cy + math.sin(a) * s * 0.55)], lt(pal[0], 0.35), max(1, s * 0.03), seed + k, 0.6, 1))
    return "".join(out)


def fox_sitting(D, ox, oy, s, seed):
    """A red fox sitting on its haunches, side view facing right, head tipped back toward the grapes.
    (ox, oy) = ground under the forepaws. s=1 ~ 240 px tall."""
    def L(pts):
        return T(pts, ox, oy, s)
    fur = ("#F6A860", "#D0662A", "#6A2A0E")
    white = ("#FFFFFF", "#F6F0E6", "#C8B8A0")
    stock = ("#4A3A30", "#1E1410", "#000000")
    out = [cast(D, ox - 30 * s, oy + 2, 110 * s, 10 * s, strength=0.45, seed=seed)]
    # far foreleg (behind)
    out.append(painted(D, L([(-4, -96), (8, -96), (6, -4), (-6, -4)]), (mix(fur[0], "#000000", 0.2), mix(fur[1], "#000000", 0.25), fur[2]), seed, sk=0.2, angle=-90, n=4, inkw=1.2, inkc="#3A1404", hi=0.2))
    out.append(painted(D, L([(-5, -40), (7, -40), (6, -2), (12, 0), (12, 4), (-6, 4)]), stock, seed + 1, sk=0.2, n=3, inkw=1, hi=0.2))
    # body: back sweeping down to the haunch, chest upright
    body = L([(-100, -6), (-110, -40), (-104, -78), (-84, -112), (-58, -140), (-30, -164), (-6, -178), (14, -176), (24, -158), (24, -130), (20, -96), (8, -70), (-20, -40), (-50, -10)])
    out.append(painted(D, body, fur, seed + 2, sdir=(0.6, 0.6), sk=0.2, angle=-70, n=80, slen=(8 * s, 20 * s), sw=(0.6, 1.8),
                       cols=["#FFC888", "#B04A18", "#F6A860", "#7A3010"], inkw=1.8, inkc="#3A1404", hi=0.45))
    # haunch (thigh) and hind foot
    haunch = blob_pts(*L([(-62, -40)])[0], 46 * s, 40 * s, seed + 3, 0.04, 20, -10)
    out.append(painted(D, haunch, fur, seed + 3, sdir=(0.6, 0.7), sk=0.18, angle=-40, n=30, slen=(6 * s, 16 * s), sw=(0.6, 1.6), inkw=1.6, inkc="#3A1404", hi=0.45))
    out.append(painted(D, L([(-44, -8), (-10, -8), (4, -2), (2, 4), (-46, 4)]), stock, seed + 4, sk=0.2, n=3, inkw=1.1, hi=0.3))
    # tail curled round on the ground, white tip at the front
    tail = L([(-96, -14), (-130, -8), (-140, 4), (-110, 6), (-60, 6), (-10, 6), (40, 4), (62, -2), (52, -10), (10, -6), (-50, -4)])
    out.append(painted(D, tail, fur, seed + 5, sdir=(0.2, 1), sk=0.2, angle=0, n=40, slen=(8 * s, 18 * s), sw=(0.6, 1.6), inkw=1.6, inkc="#3A1404", hi=0.4))
    out.append(painted(D, L([(40, 4), (62, -2), (74, 0), (62, 6)]), white, seed + 6, sk=0.2, n=4, inkw=1.2, inkc="#3A1404", hi=0.3))
    # white chest bib
    bib = L([(10, -178), (22, -160), (22, -128), (16, -98), (8, -76), (-2, -96), (-4, -134), (0, -164)])
    out.append(painted(D, bib, white, seed + 7, sk=0.15, angle=-90, n=14, inkw=0, hi=0.3))
    # near foreleg with black stocking
    out.append(painted(D, L([(8, -100), (22, -100), (20, -4), (8, -4)]), fur, seed + 8, sk=0.2, angle=-90, n=5, inkw=1.3, inkc="#3A1404", hi=0.35))
    out.append(painted(D, L([(8, -44), (21, -44), (20, -2), (28, 0), (28, 5), (6, 5)]), stock, seed + 9, sk=0.2, n=3, inkw=1.1, hi=0.3))
    # head tipped back: skull, long muzzle up toward the grapes, tall ears laid back
    head = L([(-10, -186), (-2, -210), (16, -226), (40, -242), (64, -258), (74, -258), (72, -248), (56, -230), (44, -212), (30, -194), (14, -180)])
    out.append(painted(D, head, fur, seed + 10, sdir=(0.4, 0.8), sk=0.18, angle=-50, n=30, slen=(5 * s, 12 * s), sw=(0.5, 1.4), inkw=1.7, inkc="#3A1404", hi=0.45))
    out.append(painted(D, L([(20, -196), (40, -214), (60, -240), (70, -250), (56, -228), (44, -206), (30, -190)]), white, seed + 11, sk=0.1, n=6, inkw=0, hi=0.2))
    for (bx, by, tx_, ty_, w_) in ((-8, -206, -36, -238, 11), (2, -214, -20, -252, 11)):
        ear = L([(bx - w_ * 0.7, by + 6), (tx_, ty_), (bx + w_, by - 2)])
        out.append(painted(D, ear, ("#5A3A2A", "#2A1A10", "#000000"), seed + int(bx) + 20, sk=0.2, n=4, inkw=1.2, inkc="#000000", hi=0.3))
    out.append(f'<path d="{pd(L([(-4, -210), (-18, -238), (6, -214)]))}" fill="#F6E2D0" opacity="0.8"/>')
    nx_, ny_ = L([(72, -256)])[0]
    out.append(f'<path d="{blob(nx_, ny_, 4.6 * s, 3.6 * s, seed, 0.1, 8, -40)}" fill="#1A0E08"/>')
    ex, ey = L([(22, -214)])[0]
    out.append(f'<path d="{blob(ex, ey, 5.4 * s, 3.2 * s, seed, 0.05, 10, -40)}" fill="#F2C24A"/>')
    out.append(f'<ellipse cx="{ex + 1:.1f}" cy="{ey - 0.5:.1f}" rx="{1.3 * s:.1f}" ry="{2.8 * s:.1f}" fill="#100804" transform="rotate(-40 {ex:.1f} {ey:.1f})"/>')
    out.append(pline(L([(14, -210), (22, -219), (32, -222)]), "#1A0E08", 1.8 * s, seed, 0.9, 1))
    out.append(pline(L([(70, -250), (54, -236), (44, -230)]), "#3A1404", 1.2, seed, 0.7, 1))
    for k in range(3):
        out.append(pline(L([(60, -242 + k * 3), (90, -244 + k * 8)]), "#3A1404", 0.9, seed + k, 0.7, 1))
    return "".join(out)


@design("the-fox-and-the-grapes")
def fox_and_grapes():
    D = Doc2("ft-fg")
    out = [sky(D, [(0, "#E8A050"), (0.5, "#F6CC80"), (1, "#F8E6B8")], 1, 600, ["#F6B860", "#FFE8B0", "#E89040"], 50)]
    out.append(soft_glow(D, 120, 300, 260, "#FFF2C8", 0.6))
    # vineyard rows on the far hills
    out.append(hill(D, [(-20, 400), (140, 372), (300, 390), (460, 366), (620, 380)], 620, ("#D8C070", "#A89040", "#6A5A20"), 3, inkw=0, sop=(0.15, 0.35)))
    for k in range(12):
        y = 392 + k * 7
        out.append(pline([(-10, y + 6), (300, y - 6 + k), (610, y + 2)], "#6A7A30", 2.2, k, 0.4, 1))
    out.append(hill(D, [(-20, 470), (160, 456), (360, 466), (620, 450)], 620, ("#D8A860", "#A87A3A", "#5A3A18"), 4, inkw=0, sop=(0.2, 0.4)))
    out.append(grass(5, (0, 456, 600, 600), ["#C8A050", "#8A6A2A", "#E8C880"], 200, (8, 22)))
    # the pergola: a weathered beam and the vine draped along it
    out.append(painted(D, rect_pts(-10, 40, 610, 60, 30, 6, 0.4), WOOD, 6, sk=0.2, angle=0, n=30, inkw=1.6, hi=0.35))
    for x in (72, 556):
        out.append(painted(D, rect_pts(x - 10, 60, x + 10, 600, 20, 7 + x, 0.4), WOOD, 7 + x, sk=0.25, angle=-90, n=30, inkw=1.6, hi=0.35))
    out.append(briar_vine(D, [(-10, 70), (120, 84), (260, 66), (400, 90), (610, 72)], 8, 8, col=("#A88A5A", "#6A4A2A", "#2A1A0A"), thorns=False))
    rnd = random.Random(9)
    for k, (x, y, s_, a) in enumerate(((40, 86, 48, 80), (130, 100, 52, 100), (220, 80, 46, 60), (300, 92, 50, 110), (380, 84, 54, 70), (470, 104, 50, 120), (560, 84, 48, 80),
                                       (176, 130, 40, 150), (420, 140, 42, 30), (520, 150, 40, 100))):
        out.append(vine_leaf(D, x, y, s_, a, 10 + k, rnd.choice([("#D8C870", "#9AA040", "#3A4A1A"), ("#E8B860", "#C88A30", "#6A3A10"), ("#A8C068", "#6A8A3A", "#2A4A1A")])))
    for k in range(5):
        x0 = rnd.uniform(60, 560)
        sp = [(x0 + math.cos(t) * (14 - t) * 1.4, 110 + math.sin(t) * (14 - t) * 1.4 + t * 3) for t in [j * 0.6 for j in range(14)]]
        out.append(pline(sp, "#6A7A30", 1.4, k, 0.8, 1))
    # the grapes, just out of reach
    out.append(grape_bunch(D, 372, 104, 96, 150, 11))
    out.append(grape_bunch(D, 464, 120, 76, 120, 12))
    out.append(grape_bunch(D, 290, 112, 64, 100, 13))
    # the fox
    out.append(fox_sitting(D, 196, 544, 1.0, 14))
    # lettering
    out.append(letters(D, 420, 404, "Sour", SERIF_IT, 78, "#5A2A8A", ["#7A4AAA", "#3A0E5A", "#9A6AC8"], 15, max_w=220,
                       shadow="#FFF2D0", soff=(0.02, 0.05), angle=-40, wob=0.6))
    out.append(letters(D, 420, 472, "grapes!", SERIF_IT, 78, "#5A2A8A", ["#7A4AAA", "#3A0E5A", "#9A6AC8"], 16, max_w=220,
                       shadow="#FFF2D0", soff=(0.02, 0.05), angle=-40, wob=0.6))
    out.append(tx(420, 512, "THE FOX AND THE GRAPES", CINZEL, 16, "#2E1406", ls=2, max_w=220))
    out.append(tx(420, 534, "AESOP", CINZEL, 16, "#2E1406", ls=6, max_w=230))
    return finish_b(D, out, 17, INK, 0.6)


# ================================================================ 20. ali baba — "Open, Sesame!"
def treasure_heap(D, cx, base, w, seed):
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, base - 20, w * 0.9, "#FFD060", 0.7)]
    heap = [(cx - w / 2, base), (cx - w * 0.3, base - w * 0.18), (cx, base - w * 0.3), (cx + w * 0.3, base - w * 0.2), (cx + w / 2, base)]
    out.append(painted(D, heap, ("#FFE89A", "#E8B040", "#8A5A10"), seed, sk=0.2, angle=-20, n=20, inkw=1.2, inkc="#5A3A08", hi=0.5))
    for k in range(60):
        x = cx + rnd.uniform(-0.45, 0.45) * w
        top = base - w * 0.3 * (1 - abs(x - cx) / (w / 2)) ** 0.8
        y = rnd.uniform(top + 2, base - 2)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3, 5):.1f}" ry="{rnd.uniform(1.6, 2.6):.1f}" fill="{rnd.choice(["#FFE89A", "#F6C84A", "#C8902A"])}" stroke="#8A5A10" stroke-width="0.6"/>')
    for k in range(6):
        x, y = cx + rnd.uniform(-0.35, 0.35) * w, base - rnd.uniform(4, w * 0.2)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.4, 3.6):.1f}" fill="{rnd.choice(["#E8304A", "#3AA0E8", "#3AC86A"])}"/>')
        out.append(sparkle(x, y - 2, 7, "#FFFFFF", 0.9))
    return "".join(out)


def jar(D, cx, base, h, seed, pal=("#E8A070", "#B0603A", "#5A2A14")):
    w = h * 0.62
    pts = [(cx - w * 0.2, base - h), (cx - w * 0.5, base - h * 0.7), (cx - w * 0.48, base - h * 0.3), (cx - w * 0.2, base), (cx + w * 0.2, base), (cx + w * 0.48, base - h * 0.3), (cx + w * 0.5, base - h * 0.7), (cx + w * 0.2, base - h)]
    out = [painted(D, pts, pal, seed, sdir=(0.7, 0.3), sk=0.22, angle=-90, n=10, inkw=1.4, hi=0.4)]
    out.append(painted(D, rect_pts(cx - w * 0.26, base - h - 8, cx + w * 0.26, base - h + 2, 6, seed, 0.3), pal, seed + 1, sk=0.2, angle=0, n=3, inkw=1.2, hi=0.4))
    out.append(pline([(cx - w * 0.46, base - h * 0.55), (cx, base - h * 0.5), (cx + w * 0.46, base - h * 0.55)], pal[2], 1.4, seed, 0.6, 1))
    return "".join(out)


def donkey_rider(x, base, s, col, rim=None):
    """Ali Baba and his laden donkey: a silhouette walking left."""
    def L(pts):
        return T(pts, x, base, s)
    out = []
    body = L([(-40, -38), (-30, -52), (10, -54), (30, -48), (36, -36), (30, -28), (-30, -26), (-42, -30)])
    out.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
    for (a, b) in (((-30, -30), (-32, 0)), ((-20, -28), (-18, 0)), ((20, -30), (22, 0)), ((30, -30), (34, 0))):
        out.append(taper(L([a, b]), 4.6 * s, 3 * s, col))
    out.append(f'<path d="{smooth_closed(L([(-36, -48), (-50, -62), (-62, -62), (-66, -54), (-56, -50), (-44, -40)]))}" fill="{col}"/>')
    for (a, b) in (((-52, -62), (-50, -78)), ((-56, -62), (-58, -78))):
        out.append(taper(L([a, b]), 3.4 * s, 1.4, col))
    out.append(taper(L([(36, -42), (46, -30), (46, -20)]), 2 * s, 1, col))
    # saddlebags of gold
    out.append(f'<path d="{blob(*L([(4, -40)])[0], 14 * s, 10 * s, 3, 0.1, 10)}" fill="{col}"/>')
    # Ali Baba walking ahead, leading by the rope
    out.append(pline(L([(-60, -56), (-76, -50), (-86, -46)]), col, 1.2 * s, 2, 1, 1))
    fig = L([(-96, 0), (-92, -30), (-96, -48), (-92, -62), (-82, -62), (-78, -48), (-80, -30), (-78, 0)])
    out.append(f'<path d="{smooth_closed(fig)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-87, -70)])[0], 7 * s, 7 * s, 4, 0.1, 10)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-87, -75)])[0], 9 * s, 5 * s, 5, 0.15, 10)}" fill="{col}"/>')     # turban
    out.append(taper(L([(-82, -56), (-86, -46)]), 3 * s, 2 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(30, -48), (36, -36)])), rim, 1.4, 1, 1, 0.7))
        out.append(ink(smooth_open(L([(-78, -62), (-78, -48), (-80, -30)])), rim, 1.4, 2, 1, 0.7))
    return "".join(out)


@design("ali-baba")
def ali_baba():
    D = Doc2("ft-ab")
    out = [sky(D, [(0, "#140C30"), (0.5, "#3A1E5A"), (0.85, "#8A3A5A"), (1, "#C8604A")], 1, 600, ["#2A1A4A", "#140C30", "#6A2A5A"], 50)]
    out.append(stars_field(3, (0, 0, 600, 260), 110))
    out.append(soft_glow(D, 470, 186, 60, "#FFF2D0", 0.45))
    out.append(f'<path d="{blob(470, 186, 18, 18, 3, 0.02, 18)}" fill="#FFF4D8"/><path d="{blob(478, 180, 16, 16, 4, 0.02, 18)}" fill="#2E1A4A"/>')
    # dunes behind
    out.append(hill(D, [(-20, 360), (120, 330), (260, 352), (420, 326), (620, 344)], 620, ("#8A4A5A", "#5A2A44", "#2A1028"), 3, inkw=0, sop=(0.1, 0.3)))
    # the great rock with the hidden door
    rock = poly_pts([(-20, 620), (-20, 300), (30, 286), (60, 246), (104, 256), (140, 214), (190, 230), (236, 196), (280, 216), (326, 186), (370, 214), (420, 200),
                     (462, 240), (512, 226), (556, 268), (620, 262), (620, 620)], 14, 5, 2.4)
    out.append(painted(D, rock, ("#C87A5A", "#7A3A2E", "#2E1414"), 5, sdir=(0.6, 0.4), sk=0.08, angle=-10, n=160, inkw=2, inkc="#1A0808", hi=0.3))
    rnd = random.Random(6)
    for k in range(14):
        y = 280 + k * 22
        out.append(pline([(-10, y + rnd.uniform(-6, 6)), (200, y + rnd.uniform(-4, 4)), (330, y + rnd.uniform(-4, 4)), (610, y + rnd.uniform(-6, 6))], "#4A1E1A", 1.6, k, 0.45, 1))
        out.append(pline([(-10, y + 3), (300, y + 4), (610, y + 2)], "#E89A7A", 1.1, k + 50, 0.25, 1))
    for k in range(9):
        x = 20 + k * 68 + rnd.uniform(-10, 10)
        out.append(pline([(x, 240 + rnd.uniform(-20, 20)), (x + rnd.uniform(-10, 10), 330), (x + rnd.uniform(-14, 14), 420)], "#3A1612", 1.8, k + 80, 0.4, 1))
    out.append(ink(smooth_open([(-20, 300), (30, 286), (60, 246), (104, 256), (140, 214), (190, 230), (236, 196), (280, 216), (326, 186)]), "#F2B890", 2, 7, 1, 0.45))
    # the opening: the stone door rolled aside, treasure light pouring out
    cx, cb = 300, 470
    door = arch_pts(cx - 70, cx + 70, cb - 110, cb, 8)
    out.append(f'<path d="{pd([(cx - 80, cb), (cx - 40, cb - 150), (cx + 40, cb - 150), (cx + 80, cb), (cx + 260, 620), (cx - 260, 620)])}" fill="#FFD27A" opacity="0.18"/>')
    out.append(f'<path d="{smooth_closed(door)}" fill="{D.rad([(0, "#FFF2B0"), (0.5, "#F2B040"), (1, "#8A4A10")], cx=0.5, cy=0.7, r=0.7)}"/>')
    cid = D.clip(f'<path d="{smooth_closed(door)}"/>')
    inside = [treasure_heap(D, cx - 10, cb, 120, 8), jar(D, cx - 52, cb - 2, 50, 9), jar(D, cx + 50, cb - 4, 44, 10), jar(D, cx + 24, cb - 30, 30, 11)]
    inside.append(painted(D, rect_pts(cx + 6, cb - 34, cx + 52, cb - 8, 8, 12, 0.3), ("#C8925A", "#8A5A2E", "#3A1E0A"), 12, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    inside.append(f'<path d="M {cx + 6} {cb - 26} L {cx + 52} {cb - 26}" stroke="#F6C84A" stroke-width="2.4"/>')
    out.append(f'<g {cid}>{"".join(inside)}</g>')
    out.append(ink(smooth_closed(door), "#1A0808", 2.2, 13, 1, 0.8))
    stone = blob_pts(cx + 118, cb - 56, 46, 60, 14, 0.06, 18)
    out.append(painted(D, stone, ("#B8705A", "#6A3428", "#2A1010"), 14, sdir=(1, 0.3), sk=0.2, angle=-60, n=30, inkw=1.8, inkc="#1A0808", hi=0.35))
    out.append(ink(smooth_open(stone[10:16]), "#FFD27A", 2, 15, 1, 0.6))
    # sand foreground and the light spilling across it
    out.append(hill(D, [(-20, 500), (160, 478), (300, 472), (440, 480), (620, 500)], 620, ("#D89A6A", "#8A4A3A", "#3A1A1A"), 16, inkw=0, sop=(0.15, 0.35)))
    out.append(f'<path d="{pd([(cx - 70, 474), (cx + 70, 474), (cx + 200, 620), (cx - 200, 620)])}" fill="#FFD27A" opacity="0.22"/>')
    for k in range(12):
        out.append(f'<ellipse cx="{cx + rnd.uniform(-80, 80):.1f}" cy="{rnd.uniform(482, 520):.1f}" rx="3.4" ry="1.8" fill="#F6C84A" stroke="#8A5A10" stroke-width="0.6"/>')
    out.append(donkey_rider(150, 500, 0.9, "#1A0A18", rim="#FFC870"))
    # lettering
    out.append(letters(D, 300, 116, "“Open, Sesame!”", SERIF_IT, 66, "#FFD870", ["#FFF0B0", "#E8A830", "#FFE08A"], 17, max_w=440,
                       shadow="#0A0418", soff=(0.02, 0.05), angle=-40, wob=0.6))
    out.append(tx(300, 150, "ALI BABA AND THE FORTY THIEVES", CINZEL, 15, "#F6E2C8", ls=3, max_w=380))
    return finish_b(D, out, 18, "#000000", 0.5)


# ================================================================ 21. sinbad the sailor — the roc over the ship
def roc(x, y, s, col="#0E1A2A", rim="#F2C870"):
    """The giant roc in flight, wings spread wide with fingered primaries, a boulder in its talons; faces left."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    for sg in (-1, 1):
        arm = [(sg * 8, -12), (sg * 50, -36), (sg * 104, -48), (sg * 146, -44), (sg * 152, -14), (sg * 132, 2), (sg * 116, -2), (sg * 102, 8), (sg * 86, 2),
               (sg * 72, 12), (sg * 56, 6), (sg * 40, 16), (sg * 24, 8), (sg * 10, 14)]
        out.append(f'<path d="{smooth_closed(L(arm))}" fill="{col}"/>')
        for k in range(6):
            st = (sg * (136 - k * 3), -40 + k * 8)
            mid = (sg * (170 + k * 2), -46 + k * 11)
            en = (sg * (204 + 4 * k - k * k * 1.4), -50 + k * 15)
            out.append(taper(catmull(L([st, mid, en]), 5), 15 * s, 3 * s, col))
        out.append(ink(smooth_open(L([(sg * 8, -12), (sg * 50, -36), (sg * 104, -48), (sg * 146, -44), (sg * 190, -50)])), rim, 2, 3 + sg, 1, 0.75))
        for k in range(5):
            out.append(pline(L([(sg * (40 + k * 22), -26 - k * 3), (sg * (46 + k * 22), 4 + k)]), "#2A3A5A", 1.4, k, 0.6, 1))
    out.append(f'<path d="{smooth_closed(L([(-34, -8), (-12, -22), (30, -18), (60, -6), (70, 10), (40, 20), (0, 18), (-28, 8)]))}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(58, -4), (96, -16), (106, 0), (96, 18), (64, 12)]))}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-28, -12), (-48, -24), (-64, -24), (-76, -14), (-64, -6), (-42, -2)]))}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-74, -20), (-94, -14), (-90, -4), (-80, -8), (-72, -8)]))}" fill="{col}"/>')
    ex, ey = L([(-58, -16)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="{rim}"/>')
    out.append(ink(smooth_open(L([(-94, -14), (-76, -22), (-60, -26), (-40, -22)])), rim, 1.6, 9, 1, 0.7))
    # legs and the boulder clutched below
    out.append(taper(L([(-6, 16), (-4, 36), (-2, 48)]), 7 * s, 4 * s, col))
    out.append(taper(L([(12, 16), (14, 36), (16, 48)]), 7 * s, 4 * s, col))
    out.append(f'<path d="{blob(*L([(6, 66)])[0], 28 * s, 21 * s, 7, 0.12, 14)}" fill="#3A3440"/>')
    out.append(f'<path d="{blob(*L([(0, 60)])[0], 14 * s, 8 * s, 8, 0.2, 10)}" fill="#5A5468"/>')
    out.append(ink(blob(*L([(6, 66)])[0], 28 * s, 21 * s, 7, 0.12, 14), rim, 1.4, 8, 1, 0.5))
    for k in range(3):
        out.append(taper(L([(-8 + k * 9, 48), (-12 + k * 10, 58)]), 3 * s, 1.4, col))
    return "".join(out)


def dhow(D, x, wl, s, seed, col="#2A1A10"):
    """An Arab dhow under a lateen sail, heeling in the swell."""
    def L(pts):
        return T(pts, x, wl, s, False, -6)
    out = []
    hull = L([(-70, -14), (-60, -18), (50, -18), (80, -30), (76, -20), (56, -2), (-50, 0), (-66, -6)])
    out.append(painted(D, hull, ("#A8743E", "#6A3E1A", "#2A140A"), seed, sk=0.2, angle=0, n=12, inkw=1.6, inkc="#140A04", hi=0.4))
    out.append(pline(L([(-62, -10), (60, -12)]), "#F2C870", 1.4, seed, 0.7, 1))
    out.append(taper(L([(0, -18), (2, -110)]), 4 * s, 2.4 * s, col))
    sail = L([(-60, -40), (6, -126), (60, -24)])
    out.append(painted(D, [sail[0], ((sail[0][0] + sail[1][0]) / 2 - 6, (sail[0][1] + sail[1][1]) / 2), sail[1], ((sail[1][0] + sail[2][0]) / 2 + 10, (sail[1][1] + sail[2][1]) / 2), sail[2], (sail[2][0] - 30, sail[2][1] - 4)],
                       ("#FFF6E2", "#EADCC0", "#9A8A6A"), seed + 1, sdir=(1, 0.3), sk=0.2, angle=-50, n=14, inkw=1.4, inkc="#3A2A1A", hi=0.4))
    out.append(taper(L([(-66, -36), (8, -132)]), 3 * s, 2 * s, col))
    for k in range(3):
        px, py = L([(-30 + k * 22, -8)])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.6 * s:.1f}" fill="{col}"/>')
    return "".join(out)


def swell(D, y, amp, wl, ph, pal, seed, foam=True, bottom=640):
    """One band of rolling sea: a wavy crest, painted body darkening into the trough, lacy foam on the crests."""
    pts = [(x, y + amp * math.sin(x / wl * 2 * math.pi + ph) + amp * 0.35 * math.sin(x / wl * 5.1 + ph * 1.7)) for x in range(-20, 641, 10)]
    poly = pts + [(640, bottom), (-20, bottom)]
    out = [hill(D, pts, bottom, pal, seed, angle=-8, inkc="#06182A", inkw=1.4, inkop=0.5, sop=(0.15, 0.4), cols=[pal[0], pal[2], lt(pal[0], 0.3)])]
    if foam:
        rnd = random.Random(seed)
        for i in range(1, len(pts) - 1):
            x, yy = pts[i]
            if pts[i - 1][1] > yy < pts[i + 1][1] or rnd.random() < 0.18:
                for k in range(2):
                    fx = x + rnd.uniform(-14, 14)
                    out.append(taper([(fx - 10, yy + 4), (fx, yy - 2 + rnd.uniform(-2, 2)), (fx + 12, yy + 3)], 1, 3.4, "#F2FAFF", rnd.uniform(0.6, 0.95)))
                for k in range(4):
                    out.append(f'<circle cx="{x + rnd.uniform(-16, 16):.1f}" cy="{yy + rnd.uniform(2, 14):.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(taper(pts, 2.4, 2.4, lt(pal[0], 0.4), 0.6))
    return "".join(out)


@design("sinbad-the-sailor")
def sinbad():
    D = Doc2("ft-sn")
    out = [sky(D, [(0, "#0E2A44"), (0.45, "#2A5A7A"), (0.72, "#E8B860"), (0.82, "#F6D890")], 1, 420, ["#2A4A6A", "#0E2A44", "#F2C870"], 50)]
    out.append(soft_glow(D, 420, 360, 200, "#FFE8A0", 0.55))
    out.append(puff_cloud(D, 140, 230, 220, 3, ("#E8D0B0", "#A89090", "#4A5070"), op=0.9))
    out.append(puff_cloud(D, 500, 210, 180, 4, ("#E8D0B0", "#A89090", "#4A5070"), op=0.85))
    # the roc's shadow-shape across the sky
    out.append(roc(296, 218, 1.1, "#0A1624", "#F2C870"))
    # the sea: deep, swelling, Dulac teal
    out.append(sea(D, 380, 620, [(0, "#3A8A90"), (0.4, "#1E5A70"), (1, "#0A2A40")], 5, ["#5AAAB0", "#0A2A40", "#8AD8D0"], 90))
    out.append(wave_lines(6, (0, 386, 600, 600), ["#8AD8D0", "#FFFFFF", "#0A2A40"], 80, (14, 40), 1.8, 2.5, (0.3, 0.7)))
    out.append(swell(D, 410, 6, 140, 0.3, ("#5AAAB0", "#2A7A8A", "#0E3A50"), 20))
    out.append(dhow(D, 336, 452, 1.2, 7))
    out.append(swell(D, 470, 14, 200, 1.4, ("#4A9AA8", "#1E6478", "#0A2A40"), 21))
    out.append(f'<path d="{blob(320, 470, 120, 9, 8, 0.2, 14)}" fill="#FFFFFF" opacity="0.3"/>')
    out.append(swell(D, 520, 20, 260, 3.0, ("#3A8A9A", "#14506A", "#06203A"), 22))
    out.append(swell(D, 576, 22, 320, 4.6, ("#2E7A8A", "#0E4060", "#041830"), 23))
    # lettering
    out.append(gilt(D, 300, 106, "Sinbad the Sailor", SERIF_IT, 60, max_w=440, seed=12, deboss="#04101C", dop=0.8))
    out.append(tx(300, 138, "THE THOUSAND AND ONE NIGHTS", CINZEL, 15, "#F6E8C8", ls=3, max_w=360))
    return finish_b(D, out, 13, "#000010", 0.5)


# ================================================================ 22. icarus — against the sun
def feather(D, x, y, L, ang, seed, pal=("#FFFFFF", "#F2E8D8", "#A89A80")):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for i in range(9):
        t = i / 8
        w = L * 0.16 * math.sin(math.pi * min(1, t * 1.1)) ** 0.7
        pts.append((x + ux * L * t + nx * w, y + uy * L * t + ny * w))
    for i in range(8, -1, -1):
        t = i / 8
        w = L * 0.12 * math.sin(math.pi * min(1, t * 1.1)) ** 0.7
        pts.append((x + ux * L * t - nx * w, y + uy * L * t - ny * w))
    out = [painted(D, pts, pal, seed, sk=0.15, angle=ang + 60, n=6, inkw=1, inkc="#6A5A40", hi=0.3)]
    out.append(pline([(x - ux * 4, y - uy * 4), (x + ux * L * 0.95, y + uy * L * 0.95)], "#8A7A60", 1, seed, 0.7, 1))
    return "".join(out)


def winged_figure(x, y, s, col, wing_col=None, ang=0, spread=1.0, vein="#8A4A1A"):
    """A youth flying on wings of feathers and wax: arched wings built from overlapping long feathers, rounded
    ends giving a scalloped trailing edge; body and legs streaming behind. Silhouette with feather veins."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    wc = wing_col or col
    out = []
    for sg in (-1, 1):
        arm = [(sg * 4, -8), (sg * 30 * spread, -30 * spread), (sg * 62 * spread, -40 * spread), (sg * 92 * spread, -34 * spread)]
        arm_c = catmull(arm, 6)
        feathers = []
        n = 11
        for k in range(n):
            t = k / (n - 1)
            px, py = arm_c[min(len(arm_c) - 1, int(t * (len(arm_c) - 1)))]
            L_ = (16 + 30 * t ** 1.2) * spread
            a = math.radians(90 + sg * (-10 - 55 * t))
            ex, ey = px + math.cos(a) * L_, py + math.sin(a) * L_
            feathers.append(((px, py), (ex, ey), 5 + 3 * t))
        for (p0, p1, w) in feathers[::-1]:
            pts = []
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            Ln = math.hypot(dx, dy) or 1
            ux, uy = dx / Ln, dy / Ln
            nx, ny = -uy, ux
            for i in range(9):
                tt = i / 8
                ww = w * (0.6 + 0.4 * math.sin(math.pi * min(1, tt * 1.15)))
                pts.append((p0[0] + dx * tt + nx * ww, p0[1] + dy * tt + ny * ww))
            for i in range(8, -1, -1):
                tt = i / 8
                ww = w * (0.6 + 0.4 * math.sin(math.pi * min(1, tt * 1.15)))
                pts.append((p0[0] + dx * tt - nx * ww, p0[1] + dy * tt - ny * ww))
            out.append(f'<path d="{smooth_closed(L(pts))}" fill="{wc}"/>')
            out.append(pline(L([p0, (p0[0] + dx * 0.9, p0[1] + dy * 0.9)]), vein, 0.9, 1, 0.6, 1))
        out.append(taper(L(arm_c), 8 * s, 4 * s, wc))
    out.append(f'<path d="{smooth_closed(L([(-5, -8), (5, -8), (6, 18), (2, 34), (-2, 34), (-6, 18)]))}" fill="{col}"/>')
    out.append(taper(L([(-2, 32), (-6, 50), (-8, 62)]), 4 * s, 3 * s, col))
    out.append(taper(L([(2, 32), (8, 48), (12, 58)]), 4 * s, 3 * s, col))
    out.append(f'<path d="{blob(*L([(0, -16)])[0], 6 * s, 6.6 * s, 3, 0.05, 10)}" fill="{col}"/>')
    return "".join(out)


@design("icarus")
def icarus():
    D = Doc2("ft-ic")
    out = [sky(D, [(0, "#E86A3A"), (0.35, "#F6A848"), (0.62, "#FCE2A0"), (0.75, "#BFE0E8")], 1, 400, ["#F2904A", "#FFD890", "#FFF2D0"], 50)]
    sx, sy, sr = 300, 214, 96
    out.append(soft_glow(D, sx, sy, sr * 3.2, "#FFF2B0", 0.7))
    for k in range(24):
        a = math.radians(k * 15)
        out.append(f'<path d="M {sx + math.cos(a - 0.05) * sr * 1.1:.1f} {sy + math.sin(a - 0.05) * sr * 1.1:.1f} L {sx + math.cos(a) * sr * (1.9 if k % 2 else 1.5):.1f} {sy + math.sin(a) * sr * (1.9 if k % 2 else 1.5):.1f} L {sx + math.cos(a + 0.05) * sr * 1.1:.1f} {sy + math.sin(a + 0.05) * sr * 1.1:.1f} Z" fill="#FFE070" opacity="0.4"/>')
    out.append(painted(D, blob_pts(sx, sy, sr, sr, 3, 0.004, 40), ("#FFFBE0", "#FFE070", "#F2A030"), 3, sdir=(0.5, 0.6), sk=0.08, angle=-30, n=60, inkw=0, hi=0.4))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="none" stroke="#E8902A" stroke-width="2" opacity="0.6"/>')
    # Icarus, black against the sun, wax melting, feathers coming loose
    out.append(winged_figure(318, 200, 1.2, "#2A1408", "#3A1E0E", ang=-14, spread=1.0))
    for k in range(4):
        out.append(f'<circle cx="{320 + k * 12:.1f}" cy="{214 + k * 8:.1f}" r="2.4" fill="#F6C84A"/>')
    rnd = random.Random(4)
    for k in range(9):
        fx, fy = 340 + k * 18 + rnd.uniform(-10, 10), 260 + k * 28 + rnd.uniform(-10, 10)
        out.append(feather(D, fx, fy, rnd.uniform(18, 30), rnd.uniform(40, 160), 10 + k))
    # Daedalus flying lower, the wise middle course
    out.append(winged_figure(128, 332, 0.6, "#5A4A6A", "#6A5A7A", ang=-6, spread=0.9, vein="#A898B0"))
    # the Aegean
    hz = 392
    out.append(sea(D, hz, 620, [(0, "#4AA0C0"), (0.35, "#1E6A9A"), (1, "#0A2A5A")], 5, ["#6AC0E0", "#0A2A5A", "#FFFFFF"], 90))
    for k in range(40):
        y = hz + 4 + (k / 40) ** 1.5 * 200
        w = 8 + (y - hz) * 0.5
        x = sx + rnd.uniform(-w, w) * 0.5
        out.append(taper([(x - w * 0.3, y), (x, y - 1.5), (x + w * 0.3, y)], 0.8, rnd.uniform(1.5, 3.5), "#FFF2B0", rnd.uniform(0.4, 0.9)))
    for (x, w, h) in ((76, 150, 30), (530, 160, 36), (430, 60, 14)):
        isl = [(x - w / 2, hz + 2), (x - w * 0.36, hz - h * 0.45), (x - w * 0.2, hz - h * 0.7), (x - w * 0.08, hz - h), (x + w * 0.06, hz - h * 0.82),
               (x + w * 0.2, hz - h * 0.9), (x + w * 0.34, hz - h * 0.5), (x + w / 2, hz + 2)]
        out.append(painted(D, poly_pts(isl, 8, x, 1.2), ("#D8B8A8", "#9A8088", "#5A4A62"), x, sdir=(0.6, 0.3), sk=0.2, angle=-20, n=10, inkw=0, hi=0.35))
        if w > 100:
            for j in range(4):
                hx_ = x - w * 0.18 + j * 9
                out.append(f'<rect x="{hx_:.1f}" y="{hz - h * 0.62 + (j % 2) * 3:.1f}" width="7" height="5" fill="#FFF8F0" opacity="0.9"/>')
    out.append(wave_lines(6, (0, hz + 6, 600, 600), ["#8AD0E8", "#FFFFFF", "#0A2A5A"], 70, (14, 40), 1.8, 2.5, (0.3, 0.7)))
    # lettering
    out.append(gilt(D, 300, 100, "ICARUS", CINZEL, 52, ls=14, max_w=300, seed=12, deboss="#6A2A0A", dop=0.5))
    out.append(letters(D, 300, 506, "Fly the middle course.", SERIF_IT, 50, "#FFF6E0", ["#FFFFFF", "#FFE8B0", "#F2F8FF"], 13, max_w=440,
                       shadow="#06183A", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 538, "DAEDALUS TO HIS SON · OVID", CINZEL, 15, "#DCEFFF", ls=3, max_w=360))
    return finish_b(D, out, 14, INK, 0.5)


# ================================================================ 23. pandora's box — and Hope remained
def palmette(x, y, s, col):
    out = []
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 22)
        out.append(f'<path d="{blob(x + math.cos(a) * s * 0.6, y + math.sin(a) * s * 0.6, s * 0.42, s * 0.12, k, 0.05, 10, math.degrees(a))}" fill="{col}"/>')
    out.append(f'<path d="M {x - s * 0.5:.1f} {y + s * 0.25:.1f} Q {x:.1f} {y - s * 0.1:.1f} {x + s * 0.5:.1f} {y + s * 0.25:.1f}" stroke="{col}" stroke-width="{s * 0.1:.1f}" fill="none"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s * 0.14:.1f}" fill="{col}"/>')
    return "".join(out)


def moth_trouble(D, x, y, s, ang, seed, col=("#8A7A90", "#4A3A52", "#1E1424")):
    """One of the Troubles flying out of the box: a dusky moth with patterned wings and a trail of smoke."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = [taper(catmull(L([(0, 0), (-16, 6), (-34, 0), (-54, 10), (-70, 4)]), 5), 2 * s, 9 * s, col[1], 0.25)]
    for sg in (-1, 1):
        fw = L([(2, 0), (10, sg * 6), (14, sg * 20), (6, sg * 26), (-4, sg * 18), (-2, sg * 4)])
        hw = L([(-2, sg * 2), (-6, sg * 12), (-14, sg * 16), (-16, sg * 8), (-8, sg * 2)])
        out.append(painted(D, hw, col, seed + sg, sk=0.2, n=3, inkw=0.8, inkc="#0A060C", hi=0.3))
        out.append(painted(D, fw, col, seed + 2 + sg, sk=0.2, n=4, inkw=0.9, inkc="#0A060C", hi=0.35))
        ex, ey = L([(7, sg * 15)])[0]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="{col[2]}"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1 * s:.1f}" fill="#C8A0D0"/>')
    out.append(f'<path d="{blob(*L([(0, 0)])[0], 6 * s, 2.2 * s, seed, 0.1, 8, ang)}" fill="{col[2]}"/>')
    for sg in (-1, 1):
        out.append(pline(L([(5, sg * 1), (12, sg * 5), (15, sg * 4)]), col[2], 0.9, seed, 0.9, 1))
    return "".join(out)


def greek_chest(D, cx, base, w, h, seed, lid_open=True):
    """Pandora's casket: carved cedar with gilt meander bands and lion feet; lid thrown open."""
    out = [cast(D, cx + 12, base + 4, w * 0.62, 12, color="#000000", strength=0.55, seed=seed)]
    x0, x1 = cx - w / 2, cx + w / 2
    top = base - h
    # inside back wall (dark) and the glow from within
    inner = [(x0 + 10, top), (x1 - 10, top), (x1 - 18, top + 22), (x0 + 18, top + 22)]
    out.append(f'<path d="{pd(inner)}" fill="#0A0406"/>')
    # front
    front = poly_pts([(x0, top + 14), (x1, top + 14), (x1, base), (x0, base)], 14, seed, 0.4)
    out.append(painted(D, front, ("#C88A5A", "#8A4E2A", "#3A1A0A"), seed, sdir=(0.6, 0.3), sk=0.15, angle=0, n=40, inkw=2, inkc="#1A0A04", hi=0.35))
    # meander band
    mb_y = top + 30
    out.append(painted(D, rect_pts(x0 + 8, mb_y - 10, x1 - 8, mb_y + 12, 14, seed + 1, 0.3), GOLD, seed + 1, sk=0.2, angle=0, n=10, inkw=1.2, inkc="#5A3A08", hi=0.5))
    k = 0
    xx = x0 + 14
    while xx < x1 - 26:
        out.append(f'<path d="M {xx:.1f} {mb_y + 8:.1f} L {xx:.1f} {mb_y - 6:.1f} L {xx + 12:.1f} {mb_y - 6:.1f} L {xx + 12:.1f} {mb_y + 4:.1f} L {xx + 5:.1f} {mb_y + 4:.1f} L {xx + 5:.1f} {mb_y - 1:.1f}" stroke="#5A3A08" stroke-width="2" fill="none"/>')
        xx += 16
    # a painted panel: a black-figure palmette and two birds
    pnl = rect_pts(cx - w * 0.3, mb_y + 22, cx + w * 0.3, base - 16, 14, seed + 2, 0.3)
    out.append(painted(D, pnl, ("#F2B880", "#D88A4A", "#8A4A1E"), seed + 2, sk=0.15, angle=0, n=10, inkw=1.4, inkc="#1A0A04", hi=0.3))
    out.append(palmette(cx, (mb_y + base) / 2 + 12, 30, "#1A0A04"))
    for sg in (-1, 1):
        bx, by = cx + sg * w * 0.18, (mb_y + base) / 2 + 14
        out.append(f'<path d="{smooth_closed([(bx - sg * 12, by), (bx, by - 8), (bx + sg * 10, by - 6), (bx + sg * 16, by - 14), (bx + sg * 14, by - 4), (bx + sg * 6, by + 4)])}" fill="#1A0A04"/>')
    # corner posts and lion feet
    for xe in (x0, x1):
        out.append(painted(D, rect_pts(xe - 8, top + 12, xe + 8, base, 10, seed + int(xe), 0.3), ("#A86A3A", "#6A3A1A", "#2A1206"), seed + int(xe), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.35))
        out.append(painted(D, blob_pts(xe, base + 6, 13, 9, seed + int(xe) + 1, 0.1, 10), GOLD, seed + 3, sk=0.2, n=4, inkw=1.2, inkc="#5A3A08", hi=0.5))
    # the lid flung up and back
    lid = poly_pts([(x0 + 2, top + 4), (x1 - 2, top + 4), (x1 - 14, top - 86), (x0 + 14, top - 86)], 12, seed + 4, 0.4)
    out.append(painted(D, lid, ("#B87A4A", "#7A4220", "#2E1406"), seed + 4, sdir=(0.3, -1), sk=0.12, angle=-90, n=24, inkw=1.8, inkc="#1A0A04", hi=0.3))
    out.append(painted(D, poly_pts([(x0 + 18, top - 6), (x1 - 18, top - 6), (x1 - 26, top - 76), (x0 + 26, top - 76)], 12, seed + 5, 0.3), ("#8A5230", "#5A2E14", "#24100A"), seed + 5, sk=0.1, angle=-90, n=10, inkw=1.2, inkc="#1A0A04", hi=0.2))
    out.append(f'<path d="{pd([(x0 + 26, top - 70), (x1 - 26, top - 70), (x1 - 22, top - 14), (x0 + 22, top - 14)])}" fill="none" stroke="{GOLD[1]}" stroke-width="2.4"/>')
    out.append(palmette(cx, top - 40, 24, GOLD[1]))
    out.append(painted(D, poly_pts([(x0 - 6, top + 4), (x1 + 6, top + 4), (x1 + 6, top + 16), (x0 - 6, top + 16)], 14, seed + 6, 0.3), ("#C88A5A", "#8A4E2A", "#3A1A0A"), seed + 6, sk=0.2, angle=0, n=10, inkw=1.6, inkc="#1A0A04", hi=0.4))
    return "".join(out)


@design("pandoras-box")
def pandoras_box():
    D = Doc2("ft-pd")
    out = [sky(D, [(0, "#2A1424"), (0.6, "#5A2A2A"), (1, "#8A4A2A")], 1, 600, ["#3A1A2A", "#1A0A14", "#7A3A2A"], 50)]
    out.append(soft_glow(D, 300, 360, 260, "#E8904A", 0.35))
    # black-figure frieze band near the bottom
    out.append(painted(D, rect_pts(-10, 470, 610, 620, 30, 3, 0.4), ("#E8A86A", "#C8783A", "#7A3A14"), 3, sdir=(0.2, 1), sk=0.08, angle=0, n=40, inkw=1.6, hi=0.25))
    for x in range(0, 640, 46):
        out.append(palmette(x, 578, 22, "#1A0A04"))
        out.append(f'<path d="M {x + 12} 592 Q {x + 23} 568 {x + 34} 592" stroke="#1A0A04" stroke-width="2.4" fill="none"/>')
    for y in (482, 552):
        out.append(f'<path d="M 0 {y} L 600 {y}" stroke="#1A0A04" stroke-width="3"/>')
    k = 0
    for x in range(0, 620, 18):
        out.append(f'<path d="M {x} 500 L {x} 488 L {x + 12} 488 L {x + 12} 498 L {x + 5} 498 L {x + 5} 493" stroke="#1A0A04" stroke-width="2" fill="none"/>')
    # the casket and the escaping troubles
    cb = 452
    out.append(greek_chest(D, 300, cb, 220, 120, 5))
    rnd = random.Random(6)
    out.append(f'<path d="{smooth_closed([(220, 332), (380, 332), (470, 180), (300, 110), (130, 180)])}" fill="#2A1A2A" opacity="0.0"/>')
    for k in range(7):
        a0 = rnd.uniform(-150, -30)
        p = catmull([(300 + rnd.uniform(-40, 40), 336), (300 + math.cos(math.radians(a0)) * 90, 300 + math.sin(math.radians(a0)) * 70), (300 + math.cos(math.radians(a0)) * 220, 300 + math.sin(math.radians(a0)) * 150)], 6)
        out.append(taper(p, 6, 30, rnd.choice(["#6A5A6A", "#3A2A3A", "#8A7A86"]), 0.22))
    spots = [(150, 210, 1.2, -150), (210, 168, 1.0, -120), (380, 172, 1.05, -60), (452, 214, 1.25, -30), (110, 290, 0.95, -170), (496, 290, 1.0, -10),
             (256, 214, 0.8, -100), (344, 218, 0.8, -80), (176, 340, 0.85, 160), (430, 344, 0.85, 20), (520, 160, 0.75, -40), (80, 170, 0.7, -140)]
    for k, (x, y, sz, a) in enumerate(spots):
        out.append(moth_trouble(D, x, y, sz * 1.3, a + 180, 40 + k, rnd.choice([("#8A7A90", "#4A3A52", "#1E1424"), ("#9A8A80", "#5A4A42", "#241A16"), ("#7A8090", "#3A4252", "#141A24")])))
    # Hope: a small bright butterfly rising last from the box
    hx, hy = 300, 296
    out.append(soft_glow(D, hx, hy, 110, "#FFF2B0", 0.85))
    for sg in (-1, 1):
        out.append(f'<path d="{smooth_closed([(hx, hy), (hx + sg * 24, hy - 22), (hx + sg * 32, hy - 6), (hx + sg * 14, hy + 3)])}" fill="#FFF8DA"/>')
        out.append(f'<path d="{smooth_closed([(hx, hy + 1), (hx + sg * 19, hy + 8), (hx + sg * 14, hy + 19), (hx + sg * 3, hy + 8)])}" fill="#FFE08A"/>')
        out.append(f'<circle cx="{hx + sg * 20:.1f}" cy="{hy - 9:.1f}" r="3" fill="#F6C84A"/>')
    out.append(f'<path d="M {hx} {hy - 6} L {hx} {hy + 10}" stroke="#C8902A" stroke-width="2"/>')
    for k in range(10):
        a = rnd.uniform(0, 6.28)
        out.append(sparkle(hx + math.cos(a) * rnd.uniform(16, 50), hy + math.sin(a) * rnd.uniform(14, 40), rnd.uniform(2, 5), "#FFFFFF", 0.9))
    # lettering
    out.append(gilt(D, 300, 104, "Pandora’s Box", SERIF_IT, 62, max_w=420, seed=7, deboss="#0A0408", dop=0.8))
    out.append(tx(300, 136, "A GREEK MYTH", CINZEL, 15, "#F2D8C0", ls=6, max_w=300))
    out.append(tx(301, 536, "…and at the bottom lay Hope.", SERIF_IT, 30, "#FFF2D8", max_w=420, op=0.0))
    out.append(tx(300, 536, "…and at the bottom lay Hope.", SERIF_IT, 30, "#1A0A04", max_w=420))
    return finish_b(D, out, 8, "#000000", 0.5)


# ================================================================ 24. persephone — the pomegranate between spring and winter
def pomegranate_half(D, cx, cy, r, seed):
    """A pomegranate broken open: leathery red rind, white pith walls, jewel-like arils."""
    rnd = random.Random(seed)
    out = [cast(D, cx + r * 0.2, cy + r * 0.85, r * 1.1, r * 0.2, strength=0.5, seed=seed)]
    outer = blob_pts(cx, cy, r, r * 0.92, seed, 0.03, 26)
    out.append(painted(D, outer, ("#F27A6A", "#B8282A", "#5A0A10"), seed, sdir=(0.5, 0.7), sk=0.2, angle=-50, n=40, inkw=2, inkc="#3A0408", hi=0.4))
    # crown (calyx)
    cr = [(cx - r * 0.2, cy - r * 0.86), (cx - r * 0.24, cy - r * 1.08), (cx - r * 0.1, cy - r * 0.96), (cx, cy - r * 1.14), (cx + r * 0.1, cy - r * 0.96), (cx + r * 0.24, cy - r * 1.08), (cx + r * 0.2, cy - r * 0.86)]
    out.append(painted(D, cr, ("#E8705A", "#A8282A", "#4A0808"), seed + 1, sk=0.2, n=6, inkw=1.6, inkc="#3A0408", hi=0.4))
    # the broken face
    face = blob_pts(cx + r * 0.06, cy + r * 0.08, r * 0.76, r * 0.66, seed + 2, 0.08, 22, -8)
    out.append(painted(D, face, ("#FFF6E8", "#F2DEC0", "#C8A880"), seed + 2, sk=0.12, n=10, inkw=1.4, inkc="#7A2A20", hi=0.2))
    cid = D.clip(f'<path d="{smooth_closed(face)}"/>')
    inner = []
    for k in range(70):
        a = rnd.uniform(0, 6.28)
        rr = math.sqrt(rnd.random()) * r * 0.66
        x, y = cx + r * 0.06 + math.cos(a) * rr, cy + r * 0.08 + math.sin(a) * rr * 0.86
        ar = rnd.uniform(5, 8) * r / 110
        inner.append(painted(D, blob_pts(x, y, ar, ar * 1.2, seed + 10 + k, 0.1, 10, rnd.uniform(0, 180)), ("#FF7A8A", "#D01A3A", "#6A0418"), seed + 10 + k, sk=0.2, n=2, inkw=0.6, inkc="#4A0410", hi=0.3))
        inner.append(f'<circle cx="{x - ar * 0.3:.1f}" cy="{y - ar * 0.4:.1f}" r="{ar * 0.28:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    for k in range(4):
        a = math.radians(k * 90 + 20)
        inner.append(taper([(cx, cy), (cx + math.cos(a) * r * 0.4, cy + math.sin(a) * r * 0.35), (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.7)], 6, 2, "#FFF6E8", 0.9))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


@design("persephone")
def persephone():
    D = Doc2("ft-ps")
    split = [(300, -10), (318, 100), (288, 200), (312, 300), (286, 400), (310, 500), (296, 610)]
    left = [(-10, -10)] + split + [(-10, 610)]
    right = [(610, -10)] + split + [(610, 610)]
    # spring (left): warm meadow sky, blossom
    cl = D.clip(f'<path d="{pd(left)}"/>')
    sp = [sky(D, [(0, "#9AD0E8"), (0.6, "#E8F2D8"), (1, "#C8E0A0")], 1, 600, ["#B8E0F0", "#FFFFFF", "#D8ECC0"], 40)]
    sp.append(soft_glow(D, 120, 140, 160, "#FFF6D0", 0.6))
    sp.append(hill(D, [(-20, 470), (120, 450), (320, 466)], 620, ("#B8E08A", "#7AB050", "#3E7A2E"), 3, inkw=0, sop=(0.15, 0.35)))
    sp.append(grass(4, (0, 456, 320, 600), ["#6AA040", "#9ACC60", "#3E7A2E"], 200, (8, 22)))
    rnd = random.Random(5)
    for k in range(40):
        x, y = rnd.uniform(0, 300), rnd.uniform(470, 590)
        sp.append(daisy(x, y, rnd.uniform(4, 7), k, rnd.choice(["#FFFFFF", "#F8C8D8", "#F6E06A", "#C8A8F0"])))
    # blossoming almond branch across the top-left
    sp.append(briar_vine(D, [(-10, 160), (60, 150), (140, 120), (220, 108)], 7, 6, col=("#8A6A5A", "#5A3A30", "#2A1A14"), thorns=False))
    for k, (x, y) in enumerate(((40, 150), (80, 140), (120, 124), (160, 118), (200, 104), (100, 160), (180, 130), (60, 132))):
        sp.append(wild_rose(D, x, y, 10, 20 + k, ("#FFFFFF", "#FBE2EA", "#E8A8BC")))
    for k in range(4):
        sp.append(bird_v(80 + k * 40, 240 + (k % 2) * 16, 7, "#4A5A6A"))
    out = [f'<g {cl}>{"".join(sp)}</g>']
    # winter (right): the cold blue of the underworld months, bare trees, snow
    cr_ = D.clip(f'<path d="{pd(right)}"/>')
    wn = [sky(D, [(0, "#1E2A4A"), (0.6, "#5A6A90"), (1, "#C8D0E0")], 2, 600, ["#2A3A5A", "#8A9AB8", "#FFFFFF"], 40)]
    wn.append(hill(D, [(280, 466), (480, 446), (620, 456)], 620, ("#FFFFFF", "#DCE4F0", "#8A9AB8"), 6, inkw=0, sop=(0.1, 0.25)))
    for k, (x, h) in enumerate(((420, 200), (520, 240), (360, 150))):
        wn.append(bare_tree(x, 470, h, 30 + k, "#2A2A40", 6, 30, 5))
    wn.append(snowfall(7, (290, 0, 600, 600), 140, (0.8, 2.8)))
    out.append(f'<g {cr_}>{"".join(wn)}</g>')
    out.append(ink(smooth_open(split), "#3A2418", 2, 8, 1, 0.5))
    # the pomegranate, split, six seeds fallen
    out.append(pomegranate_half(D, 300, 330, 112, 9))
    for k, (x, y) in enumerate(((228, 468), (252, 476), (276, 470), (322, 472), (346, 478), (370, 466))):
        out.append(painted(D, blob_pts(x, y, 6, 7.4, 30 + k, 0.1, 10, rnd.uniform(0, 180)), ("#FF7A8A", "#D01A3A", "#6A0418"), 30 + k, sk=0.2, n=2, inkw=0.8, inkc="#4A0410", hi=0.3))
        out.append(f'<circle cx="{x - 2:.1f}" cy="{y - 3:.1f}" r="1.8" fill="#FFFFFF" opacity="0.85"/>')
    # lettering
    cart = poly_pts([(110, 56), (490, 56), (502, 100), (490, 144), (110, 144), (98, 100)], 16, 12, 0.6)
    out.append(cast(D, 306, 150, 200, 8, strength=0.35, seed=12))
    out.append(painted(D, cart, ("#FFFDF4", "#F6EEDC", "#C8B898"), 12, sdir=(0, 1), sk=0.08, angle=0, n=30, inkw=1.6, inkc="#7A1424", hi=0.2))
    out.append(f'<path d="{pd([(120, 64), (480, 64), (490, 100), (480, 136), (120, 136), (110, 100)])}" fill="none" stroke="#C8A050" stroke-width="1.4"/>')
    out.append(letters(D, 300, 120, "Persephone", SERIF_IT, 66, "#7A1424", ["#A8283A", "#5A0A14", "#C84A5A"], 10, max_w=350,
                       shadow="#E8D8C0", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(multi(300, 532, [("Six seeds, ", "#2A4A1A"), ("six months of winter.", "#1E2A4A")], SERIF_IT, 32, max_w=440))
    return finish_b(D, out, 11, INK, 0.5)


# ================================================================ 25. pegasus — the winged horse at dawn
def winged_horse(D, ox, oy, s, seed, pal=("#FFFFFF", "#ECEAF2", "#9A9AB8"), rim="#FFD890"):
    """Pegasus in flight, side view facing left, wings raised; (ox, oy) = middle of the belly. s=1 ~ 300 px nose to tail."""
    def L(pts):
        return T(pts, ox, oy, s)
    ink_c = "#4A4A6A"
    far = (mix(pal[0], pal[2], 0.35), mix(pal[1], pal[2], 0.4), dk(pal[2], 0.2))
    out = []
    # far wing (behind), far legs
    wing_far = L([(-30, -36), (-16, -84), (14, -130), (52, -164), (80, -170), (96, -160), (84, -130), (70, -100), (44, -66), (10, -40)])
    out.append(painted(D, wing_far, far, seed, sdir=(0.3, 1), sk=0.15, angle=-60, n=24, inkw=1.3, inkc=ink_c, hi=0.3))
    out.append(taper(catmull(L([(-56, 8), (-80, 36), (-66, 56)]), 5), 13 * s, 8 * s, far[1]))
    out.append(taper(catmull(L([(50, 12), (82, 44), (112, 60)]), 5), 16 * s, 8 * s, far[1]))
    # tail streaming
    tail = L([(80, -22), (112, -26), (146, -16), (176, 4), (190, 26), (168, 16), (140, 6), (110, 0), (84, -6)])
    out.append(painted(D, tail, pal, seed + 1, sk=0.15, angle=10, n=20, slen=(10 * s, 26 * s), sw=(0.6, 1.4), inkw=1.3, inkc=ink_c, hi=0.4))
    for k in range(5):
        out.append(pline(L([(86, -16 + k * 3), (130, -14 + k * 6), (172, 6 + k * 5)]), pal[2], 1, seed + k, 0.5, 1))
    # body
    body = L([(-82, 0), (-70, -26), (-48, -36), (0, -32), (40, -34), (66, -38), (88, -20), (90, 4), (70, 22), (30, 26), (-20, 26), (-56, 20), (-80, 14)])
    out.append(painted(D, body, pal, seed + 2, sdir=(0.3, 1), sk=0.16, angle=-10, n=40, inkw=1.6, inkc=ink_c, hi=0.5, hik=0.08))
    # neck arched forward and head
    neck = L([(-52, -30), (-70, -58), (-94, -88), (-106, -96), (-114, -84), (-116, -60), (-100, -34), (-82, -6), (-70, -12)])
    out.append(painted(D, neck, pal, seed + 3, sdir=(0.5, 0.8), sk=0.16, angle=-60, n=20, inkw=1.5, inkc=ink_c, hi=0.5))
    head = L([(-104, -98), (-118, -100), (-132, -90), (-150, -70), (-158, -60), (-154, -50), (-140, -50), (-124, -56), (-112, -62), (-102, -76)])
    out.append(painted(D, head, pal, seed + 4, sdir=(0.5, 0.8), sk=0.16, angle=-30, n=14, inkw=1.5, inkc=ink_c, hi=0.5))
    out.append(f'<path d="{smooth_closed(L([(-104, -98), (-102, -116), (-96, -100)]))}" fill="{pal[1]}" stroke="{ink_c}" stroke-width="1"/>')
    out.append(f'<path d="{smooth_closed(L([(-112, -98), (-114, -114), (-106, -100)]))}" fill="{pal[2]}"/>')
    ex, ey = L([(-128, -82)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{3 * s:.1f}" ry="{2.2 * s:.1f}" fill="#2A2A40" transform="rotate(-30 {ex:.1f} {ey:.1f})"/>')
    out.append(f'<circle cx="{ex - 0.8:.1f}" cy="{ey - 0.8:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    nx_, ny_ = L([(-150, -60)])[0]
    out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="{2.6 * s:.1f}" ry="{1.6 * s:.1f}" fill="#5A5A7A" transform="rotate(-40 {nx_:.1f} {ny_:.1f})"/>')
    out.append(pline(L([(-156, -52), (-144, -52)]), ink_c, 1.2, seed, 0.7, 1))
    # mane flowing back in locks
    rnd = random.Random(seed)
    for k in range(9):
        t = k / 8
        bx, by = L([(-104 + 50 * t, -96 + 64 * t)])[0]
        lock = [(bx, by)] + [(bx + (20 + 10 * t) * s * j / 3 + rnd.uniform(-3, 3), by - (6 - 10 * t) * s * j / 3 + j * 4 * s) for j in range(1, 4)]
        out.append(taper(catmull(lock, 4), 7 * s, 1, rnd.choice([pal[0], pal[1], "#F6E8D0"])))
        out.append(pline(lock, pal[2], 0.9, seed + k, 0.5, 1))
    # near legs: forelegs tucked, hind legs reaching back
    for (pts, w0, w1) in (([(-62, 10), (-88, 32), (-80, 54), (-94, 62)], 14, 8), ([(-40, 14), (-60, 40), (-48, 60)], 12, 7),
                          ([(60, 14), (96, 34), (126, 44)], 17, 8), ([(40, 20), (70, 46), (100, 62)], 14, 7)):
        p = catmull(L(pts), 5)
        out.append(taper(p, w0 * s + 2, w1 * s + 2, ink_c, 0.6))
        out.append(taper(p, w0 * s, w1 * s, pal[1]))
        out.append(taper([(x - 1.5, y - 1.5) for x, y in p], w0 * s * 0.3, w1 * s * 0.2, pal[0], 0.9))
        hx, hy = p[-1]
        out.append(f'<path d="{blob(hx, hy, 5 * s, 4 * s, seed, 0.1, 8)}" fill="#C8A060" stroke="{ink_c}" stroke-width="1"/>')
    # near wing, raised: coverts, secondaries, long primaries
    wing = L([(-46, -34), (-44, -70), (-30, -112), (-6, -150), (24, -176), (54, -190), (80, -192), (92, -184), (78, -176), (96, -168), (80, -160), (100, -150),
              (80, -142), (98, -130), (76, -124), (90, -110), (66, -104), (76, -90), (52, -84), (56, -68), (30, -56), (10, -38)])
    out.append(painted(D, wing, pal, seed + 5, sdir=(0.3, 1), sk=0.14, angle=-60, n=40, inkw=1.6, inkc=ink_c, hi=0.5))
    for k in range(7):
        a = L([(-34 + k * 9, -60 - k * 20)])[0]
        b = L([(-8 + k * 12, -48 - k * 18)])[0]
        out.append(pline([a, b], pal[2], 1.2, seed + k, 0.6, 1))
    for k in range(7):
        a = L([(-26 + k * 8, -100 - k * 11)])[0]
        b = L([(64 + k * 3, -96 - k * 13)])[0]
        out.append(pline([a, b], pal[2], 1.1, seed + k + 10, 0.55, 1))
    for k in range(10):
        x, y = L([(rnd.uniform(-38, 10), rnd.uniform(-90, -44))])[0]
        out.append(f'<path d="M {x - 4:.1f} {y:.1f} q 4 4 8 0" stroke="{pal[2]}" stroke-width="1" fill="none" opacity="0.6"/>')
    # golden dawn rim light
    out.append(ink(smooth_open(L([(-46, -34), (-44, -70), (-30, -112), (-6, -150), (24, -176), (54, -190)])), rim, 2, seed, 1, 0.7))
    out.append(ink(smooth_open(L([(-48, -36), (0, -32), (40, -34), (66, -38)])), rim, 1.8, seed + 1, 1, 0.6))
    out.append(ink(smooth_open(L([(-104, -98), (-118, -100), (-132, -90), (-150, -70)])), rim, 1.6, seed + 2, 1, 0.6))
    return "".join(out)


def doric_temple(D, cx, base, w, seed, col=("#FFF6E8", "#E8D8C0", "#A08A70")):
    out = []
    n = 6
    h = w * 0.42
    out.append(painted(D, rect_pts(cx - w / 2 - 8, base - 10, cx + w / 2 + 8, base, 14, seed, 0.3), col, seed, sk=0.2, angle=0, n=6, inkw=1, hi=0.4))
    for k in range(n):
        x = cx - w / 2 + 8 + k * (w - 16) / (n - 1)
        out.append(painted(D, rect_pts(x - 5, base - 10 - h, x + 5, base - 10, 10, seed + k, 0.2), col, seed + k, sdir=(1, 0.2), sk=0.3, angle=-90, n=3, inkw=0.9, hi=0.4))
    out.append(painted(D, rect_pts(cx - w / 2 - 4, base - 22 - h, cx + w / 2 + 4, base - 10 - h, 14, seed + 9, 0.3), col, seed + 9, sk=0.2, angle=0, n=4, inkw=1, hi=0.4))
    out.append(painted(D, [(cx - w / 2 - 8, base - 22 - h), (cx, base - 22 - h - w * 0.18), (cx + w / 2 + 8, base - 22 - h)], col, seed + 10, sk=0.2, angle=0, n=4, inkw=1, hi=0.4))
    return "".join(out)


@design("pegasus")
def pegasus():
    D = Doc2("ft-pg")
    out = [sky(D, [(0, "#2A3A6A"), (0.4, "#7A6A9A"), (0.7, "#F2A88A"), (0.85, "#FCD8A0"), (1, "#F8E8C0")], 1, 600, ["#4A5A8A", "#F2B89A", "#FFE8C0"], 60)]
    out.append(stars_field(2, (0, 0, 600, 180), 50))
    out.append(soft_glow(D, 470, 430, 260, "#FFE0A0", 0.6))
    out.append(puff_cloud(D, 110, 380, 200, 3, ("#FFF0E2", "#F2C8C0", "#B88AA0"), op=0.85))
    out.append(puff_cloud(D, 510, 300, 160, 4, ("#FFF0E2", "#F2C8C0", "#B88AA0"), op=0.8))
    # the sea and Mount Helicon's cliff with a little temple
    out.append(sea(D, 470, 620, [(0, "#E8B0A0"), (0.3, "#7A80B0"), (1, "#2A3A6A")], 5, ["#F2C8B0", "#3A4A7A", "#FFFFFF"], 70))
    cliff = [(-20, 620), (-20, 430), (40, 410), (110, 420), (150, 450), (180, 500), (200, 620)]
    out.append(painted(D, cliff, ("#C8A0A0", "#7A5A6A", "#3A2A3A"), 6, sdir=(1, 0.4), sk=0.2, angle=-70, n=40, inkw=1.6, hi=0.3))
    out.append(doric_temple(D, 80, 418, 92, 7))
    out.append(soft_glow(D, 470, 462, 50, "#FFF2D0", 0.8))
    # Pegasus
    out.append(winged_horse(D, 340, 352, 1.0, 8))
    rnd = random.Random(9)
    for k in range(12):
        out.append(sparkle(rnd.uniform(160, 560), rnd.uniform(120, 420), rnd.uniform(2, 5), "#FFF6D8", rnd.uniform(0.5, 1)))
    # lettering
    out.append(gilt(D, 300, 104, "PEGASUS", CINZEL, 56, ls=14, max_w=380, seed=10, deboss="#141C3A", dop=0.7))
    out.append(tx(300, 134, "THE WINGED HORSE · GREEK MYTH", CINZEL, 15, "#F6E8F2", ls=3, max_w=380))
    out.append(tx(301, 539, "Born of sea-foam, bound for the stars.", SERIF_IT, 26, "#141C3A", max_w=420, op=0.6))
    out.append(tx(300, 537, "Born of sea-foam, bound for the stars.", SERIF_IT, 26, "#FFF6EC", max_w=420))
    return finish_b(D, out, 11, INK, 0.5)


# ================================================================ 26. the trojan horse — before the gates of Troy
def wooden_horse(D, ox, oy, s, seed):
    """The great wooden horse on its wheeled platform, built of planks; (ox, oy) = ground under the platform centre."""
    def L(pts):
        return T(pts, ox, oy, s)
    wood = ("#E8B47A", "#A8703A", "#4A2A10")
    out = [cast(D, ox + 20, oy + 4, 190 * s, 14 * s, strength=0.55, seed=seed)]
    # platform and wheels
    out.append(painted(D, L([(-150, -34), (150, -34), (150, -14), (-150, -14)]), wood, seed, sk=0.2, angle=0, n=20, inkw=1.6, inkc="#1A0A04", hi=0.35))
    for wx in (-120, -50, 50, 120):
        cx_, cy_ = L([(wx, -10)])[0]
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{20 * s:.1f}" fill="{wood[2]}"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{16 * s:.1f}" fill="{wood[1]}" stroke="#1A0A04" stroke-width="1.4"/>')
        for k in range(6):
            a = math.radians(k * 60 + 15)
            out.append(f'<path d="M {cx_:.1f} {cy_:.1f} L {cx_ + math.cos(a) * 15 * s:.1f} {cy_ + math.sin(a) * 15 * s:.1f}" stroke="{wood[2]}" stroke-width="2.4"/>')
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{4 * s:.1f}" fill="{GOLD[1]}"/>')
    # legs: square posts with hoof blocks
    for (lx, k) in ((-96, 0), (-66, 1), (66, 2), (96, 3)):
        dk_ = 0.18 if k in (1, 2) else 0
        c = (mix(wood[0], "#000000", dk_), mix(wood[1], "#000000", dk_), wood[2])
        out.append(painted(D, L([(lx - 12, -150), (lx + 12, -150), (lx + 11, -48), (lx - 11, -48)]), c, seed + 1 + k, sk=0.2, angle=-90, n=8, inkw=1.4, inkc="#1A0A04", hi=0.3))
        out.append(painted(D, L([(lx - 15, -48), (lx + 15, -48), (lx + 15, -34), (lx - 15, -34)]), ("#6A4A2A", "#3A2210", "#140A04"), seed + 5 + k, sk=0.2, n=3, inkw=1.2, hi=0.3))
    # barrel of the body, planked
    body = L([(-130, -150), (-124, -200), (-90, -224), (90, -224), (124, -204), (132, -150), (100, -130), (-100, -130)])
    out.append(painted(D, body, wood, seed + 9, sdir=(0.6, 0.6), sk=0.15, angle=0, n=50, inkw=2, inkc="#1A0A04", hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    pl = []
    for k in range(8):
        y = L([(0, -218 + k * 12)])[0][1]
        x0_, x1_ = L([(-140, 0)])[0][0], L([(140, 0)])[0][0]
        pl.append(f'<path d="M {x0_:.1f} {y:.1f} L {x1_:.1f} {y + 1:.1f}" stroke="#4A2A10" stroke-width="1.6" opacity="0.7"/>')
        for j in range(6):
            nx_ = x0_ + 30 + j * 44 + (k % 2) * 20
            pl.append(f'<circle cx="{nx_:.1f}" cy="{y + 4:.1f}" r="1.4" fill="#2A1A0A"/>')
    # the hidden hatch in the belly
    hx0, hy0 = L([(-30, -148)])[0]
    pl.append(f'<rect x="{hx0:.1f}" y="{hy0 - 14 * s:.1f}" width="{60 * s:.1f}" height="{16 * s:.1f}" fill="none" stroke="#2A1408" stroke-width="2"/>')
    pl.append(f'<path d="M {hx0 + 2:.1f} {hy0 - 13 * s:.1f} L {hx0 + 60 * s - 2:.1f} {hy0 - 13 * s:.1f}" stroke="#FFC860" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<g {cid}>{"".join(pl)}</g>')
    # neck and the blocky carved head
    neck = L([(-96, -214), (-128, -280), (-138, -320), (-100, -330), (-84, -290), (-60, -222)])
    out.append(painted(D, neck, wood, seed + 10, sdir=(0.6, 0.5), sk=0.18, angle=-70, n=24, inkw=1.8, inkc="#1A0A04", hi=0.35))
    head = L([(-140, -318), (-150, -340), (-136, -356), (-104, -352), (-70, -330), (-58, -312), (-66, -300), (-96, -312), (-110, -306)])
    out.append(painted(D, head, wood, seed + 11, sdir=(0.6, 0.6), sk=0.18, angle=-20, n=20, inkw=1.8, inkc="#1A0A04", hi=0.35))
    for k in range(4):
        out.append(pline(L([(-126 + k * 18, -350 + k * 6), (-120 + k * 18, -310 + k * 4)]), "#4A2A10", 1.3, seed + k, 0.6, 1))
    out.append(f'<path d="{pd(L([(-136, -352), (-148, -380), (-126, -356)]))}" fill="{wood[1]}" stroke="#1A0A04" stroke-width="1.4"/>')
    out.append(f'<path d="{pd(L([(-120, -354), (-126, -382), (-108, -352)]))}" fill="{wood[2]}" stroke="#1A0A04" stroke-width="1.4"/>')
    ex, ey = L([(-104, -336)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5 * s:.1f}" fill="#1A0A04"/><circle cx="{ex - 1:.1f}" cy="{ey - 1:.1f}" r="{1.6 * s:.1f}" fill="#FFC860"/>')
    # carved mane of plank-fins and a bundled tail
    for k in range(8):
        t = k / 7
        a, b = L([(-136 + 44 * t, -330 + 110 * t)])[0], L([(-118 + 46 * t, -346 + 112 * t)])[0]
        out.append(painted(D, [a, b, (b[0] + 10 * s, b[1] + 6 * s), (a[0] + 10 * s, a[1] + 8 * s)], ("#C8905A", "#8A5A2A", "#3A1E0A"), seed + 20 + k, sk=0.2, n=3, inkw=1, inkc="#1A0A04", hi=0.3))
    for k in range(5):
        out.append(taper(catmull(L([(126, -196), (150, -170 + k * 6), (156 + k * 4, -110 + k * 10)]), 5), 6 * s, 3 * s, ("#C8905A", "#8A5A2A", "#6A4220")[k % 3]))
    # the torch-light rim on the side facing the gate
    out.append(ink(smooth_open(L([(90, -224), (124, -204), (132, -150)])), "#FFC870", 2.2, seed, 1, 0.75))
    return "".join(out)


def troy_walls(D, base, seed):
    rnd = random.Random(seed)
    out = []
    pal = ("#C8B8A0", "#8A7A68", "#3A3028")
    wall = [(300, base), (300, base - 150), (620, base - 160), (620, base)]
    out.append(painted(D, wall, pal, seed, sdir=(1, 0.3), sk=0.12, angle=0, n=50, inkw=1.6, hi=0.25))
    for k in range(14):
        y = base - 10 - k * 11
        out.append(pline([(300, y), (620, y - 6)], pal[2], 1.1, k, 0.5, 1))
        for j in range(10):
            x = 310 + j * 32 + (k % 2) * 16
            out.append(f'<path d="M {x} {y} l 0 -11" stroke="{pal[2]}" stroke-width="1" opacity="0.45"/>')
    for j in range(16):
        x = 302 + j * 20
        out.append(f'<rect x="{x}" y="{base - 166 - j * 0.3:.1f}" width="12" height="16" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1"/>')
    # the Scaean gate: great door, open
    gx = 460
    gate = arch_pts(gx - 44, gx + 44, base - 90, base, 8)
    out.append(f'<path d="{smooth_closed(gate)}" fill="#1A0E08"/>')
    out.append(soft_glow(D, gx, base - 40, 80, "#FFB050", 0.55))
    out.append(f'<path d="{smooth_closed(arch_pts(gx - 34, gx + 34, base - 82, base, 8))}" fill="#FFB050" opacity="0.4"/>')
    # towers
    for tx_ in (340, 560):
        out.append(painted(D, rect_pts(tx_ - 32, base - 230, tx_ + 32, base, 20, seed + tx_, 0.4), pal, seed + tx_, sdir=(1, 0.2), sk=0.2, angle=-90, n=20, inkw=1.6, hi=0.3))
        for j in range(5):
            out.append(f'<rect x="{tx_ - 32 + j * 14:.1f}" y="{base - 244}" width="9" height="16" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1"/>')
        for wy in (base - 196, base - 140):
            out.append(f'<rect x="{tx_ - 4}" y="{wy}" width="8" height="14" fill="#FFC060"/>')
            out.append(soft_glow(D, tx_, wy + 7, 18, "#FFC060", 0.5))
        # torch
        out.append(soft_glow(D, tx_ - 40, base - 120, 40, "#FF9A3A", 0.7))
        out.append(f'<path d="{blob(tx_ - 40, base - 124, 4, 8, tx_, 0.2, 8)}" fill="#FFE08A"/>')
    return "".join(out)


@design("the-trojan-horse")
def trojan_horse():
    D = Doc2("ft-tr")
    out = [sky(D, [(0, "#0A1230"), (0.6, "#24305A"), (1, "#4A3A5A")], 1, 600, ["#1A2448", "#0A1230", "#3A4A7A"], 50)]
    out.append(stars_field(2, (0, 0, 600, 300), 100))
    out.append(soft_glow(D, 110, 170, 70, "#F2F0E0", 0.45))
    out.append(f'<path d="{blob(110, 170, 26, 26, 3, 0.02, 20)}" fill="#F6F2E2"/>')
    # plain before the city
    out.append(hill(D, [(-20, 470), (200, 460), (400, 466), (620, 456)], 620, ("#6A5A50", "#3A2E2A", "#1A1210"), 4, inkw=0, sop=(0.15, 0.35)))
    out.append(troy_walls(D, 466, 5))
    out.append(soft_glow(D, 460, 430, 200, "#FF9A3A", 0.25))
    # the horse, and Trojans hauling it toward the gate
    out.append(wooden_horse(D, 224, 488, 0.92, 6))
    for k, x in enumerate((360, 392, 424)):
        out.append(pline([(300, 440), (x, 476)], "#C8A060", 1.4, k, 0.8, 1))
        out.append(tiny_cloak_figure(x + 6, 486, 0.62, "#140A08", rim="#FFB050", hood=False, facing=1))
    out.append(grass(7, (0, 480, 600, 600), ["#2A2018", "#4A3A2A"], 120, (6, 16)))
    # lettering
    out.append(gilt(D, 300, 104, "The Trojan Horse", SERIF_IT, 60, max_w=440, seed=8, deboss="#04081A", dop=0.8))
    out.append(tx(300, 134, "THE FALL OF TROY · VIRGIL", CINZEL, 15, "#E8E0F2", ls=3, max_w=360))
    out.append(tx(301, 543, "“Beware of Greeks bearing gifts.”", SERIF_IT, 32, "#000000", max_w=440, op=0.6))
    out.append(tx(300, 540, "“Beware of Greeks bearing gifts.”", SERIF_IT, 32, "#FFF0D8", max_w=440))
    return finish_b(D, out, 9, "#000000", 0.5)


# ================================================================ 27. mjölnir — Thor's hammer, as a Viking-age amulet
def knot_band(D, x0, x1, y, h, col, bg, seed):
    """A strip of two-strand interlace (Norse knotwork) between x0 and x1, centred on y."""
    out = [f'<rect x="{x0}" y="{y - h / 2:.1f}" width="{x1 - x0}" height="{h:.1f}" fill="{bg}"/>']
    period = h * 1.6
    n = int((x1 - x0) / period) + 2
    for ph, c in ((0, col), (math.pi, lt(col, 0.25))):
        pts = [(x0 + i * period / 8, y + math.sin(i * math.pi / 4 + ph) * h * 0.32) for i in range(n * 8 + 1)]
        out.append(f'<path d="{smooth_open(pts)}" stroke="#1A0E04" stroke-width="{h * 0.34:.1f}" fill="none"/>')
        out.append(f'<path d="{smooth_open(pts)}" stroke="{c}" stroke-width="{h * 0.22:.1f}" fill="none"/>')
    # over-under breaks at the crossings
    for i in range(n * 2 + 1):
        x = x0 + i * period / 2 + period / 4
        if (i % 2) == 0:
            out.append(f'<path d="M {x - h * 0.1:.1f} {y:.1f} L {x + h * 0.1:.1f} {y:.1f}" stroke="{col}" stroke-width="{h * 0.22:.1f}"/>')
    out.append(f'<path d="M {x0} {y - h / 2:.1f} L {x1} {y - h / 2:.1f} M {x0} {y + h / 2:.1f} L {x1} {y + h / 2:.1f}" stroke="{col}" stroke-width="2"/>')
    return "".join(out)


def mjolnir_amulet(D, cx, top, s, seed):
    """Thor's hammer in the shape of the Viking-age silver pendants: loop, short handle, flaring head with
    filigree knotwork and granulation, a staring boss-eye on each lobe."""
    def L(pts):
        return T(pts, cx, top, s)
    silver = ("#FFFFFF", "#C8CCD6", "#5A6070")
    out = []
    # cord loop
    out.append(f'<path d="{smooth_closed(ell_pts(*L([(0, 18)])[0], 16 * s, 18 * s, 0, 360, 20))}" fill="none" stroke="{silver[2]}" stroke-width="{9 * s:.1f}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(*L([(0, 18)])[0], 16 * s, 18 * s, 0, 360, 20))}" fill="none" stroke="{silver[1]}" stroke-width="{5 * s:.1f}"/>')
    # handle, twisted
    shaft = L([(-14, 34), (14, 34), (12, 170), (-12, 170)])
    out.append(painted(D, shaft, silver, seed, sdir=(1, 0.2), sk=0.25, angle=-90, n=12, inkw=1.6, inkc="#2A2E3A", hi=0.6))
    for k in range(10):
        y = 42 + k * 13
        out.append(pline(L([(-12, y), (12, y + 8)]), silver[2], 1.6, seed + k, 0.8, 1))
        out.append(pline(L([(-11, y - 2), (11, y + 6)]), "#FFFFFF", 1, seed + k, 0.6, 1))
    # head: flaring lobes
    head = L([(-12, 168), (-60, 172), (-96, 184), (-114, 206), (-118, 246), (-96, 230), (-60, 230), (-30, 240), (0, 252), (30, 240), (60, 230), (96, 230), (118, 246), (114, 206), (96, 184), (60, 172), (12, 168)])
    out.append(painted(D, head, silver, seed + 1, sdir=(0.6, 0.8), sk=0.18, angle=-20, n=40, inkw=2, inkc="#2A2E3A", hi=0.6, hik=0.08))
    cid = D.clip(f'<path d="{smooth_closed(head)}"/>')
    inner = []
    # gold filigree interlace on the head
    def gold_line(pts_, w=3.6):
        p = catmull(L(pts_), 6)
        inner.append(taper(p, (w + 2.4) * s, (w + 2.4) * s, "#3A2A08", 0.8))
        inner.append(taper(p, w * s, w * s, GOLD[1]))
        inner.append(taper([(x - 0.8, y - 0.8) for x, y in p], 1.2 * s, 1.2 * s, GOLD[0], 0.9))
    # a border line of gold wire following the head's outline
    gold_line([(-104, 236), (-104, 206), (-88, 190), (-50, 182), (0, 180), (50, 182), (88, 190), (104, 206), (104, 236)], 3)
    # double spirals on each lobe (S-scrolls), a triquetra knot in the middle
    for sg in (-1, 1):
        sp = [(sg * (70 + math.cos(t) * (16 - t * 1.6)), 210 + math.sin(t) * (16 - t * 1.6)) for t in [j * 0.5 for j in range(16)]]
        gold_line(sp, 3)
        gold_line([(sg * 34, 196), (sg * 50, 220), (sg * 36, 232)], 3)
    for k in range(3):
        a = math.radians(-90 + k * 120)
        a2 = math.radians(-90 + (k + 1) * 120)
        p0 = (math.cos(a) * 16, 214 + math.sin(a) * 16)
        p1 = (math.cos(a2) * 16, 214 + math.sin(a2) * 16)
        mid = ((p0[0] + p1[0]) * 0.1, 214 + ((p0[1] - 214) + (p1[1] - 214)) * 0.1)
        gold_line([p0, (mid[0] + (p0[0] + p1[0]) * 0.9, mid[1] + ((p0[1] - 214) + (p1[1] - 214)) * 0.9), p1], 3)
    cxx, cyy = L([(0, 214)])[0]
    inner.append(f'<circle cx="{cxx:.1f}" cy="{cyy:.1f}" r="{5 * s:.1f}" fill="{GOLD[1]}" stroke="#3A2A08" stroke-width="1.2"/>')
    # granulation dots along the edge
    for k in range(40):
        t = k / 39
        p = catmull(L([(-112, 238), (-96, 226), (-60, 226), (-30, 236), (0, 246), (30, 236), (60, 226), (96, 226), (112, 238)]), 6)
        x, y = p[int(t * (len(p) - 1))]
        inner.append(f'<circle cx="{x:.1f}" cy="{y - 5 * s:.1f}" r="{2 * s:.1f}" fill="{GOLD[0]}" stroke="#5A4010" stroke-width="0.6"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper(L([(-90, 200), (-60, 186), (-20, 180)]), 2, 5 * s, "#FFFFFF", 0.8))
    return "".join(out)


def lightning(x0, y0, x1, y1, seed, col="#F2F6FF"):
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    n = 8
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-18, 18), y0 + (y1 - y0) * t + rnd.uniform(-6, 6)))
    pts.append((x1, y1))
    out = [f'<path d="{pd(pts, False)}" stroke="#A8C8FF" stroke-width="7" fill="none" opacity="0.35" stroke-linejoin="round"/>',
           f'<path d="{pd(pts, False)}" stroke="{col}" stroke-width="2.4" fill="none" stroke-linejoin="round"/>']
    k = rnd.randint(2, n - 2)
    bx, by = pts[k]
    br = [(bx, by), (bx + rnd.choice([-1, 1]) * 30, by + 30), (bx + rnd.choice([-1, 1]) * 40, by + 60)]
    out.append(f'<path d="{pd(br, False)}" stroke="{col}" stroke-width="1.4" fill="none" opacity="0.8"/>')
    return "".join(out)


@design("mjolnir")
def mjolnir():
    D = Doc2("ft-mj")
    out = [sky(D, [(0, "#0A101E"), (0.5, "#1E2A40"), (1, "#3A4A60")], 1, 600, ["#2A3650", "#0A101E", "#4A5A78"], 60)]
    # storm clouds rolling, lightning
    for k, (x, y, w) in enumerate(((100, 200, 260), (480, 170, 280), (300, 120, 300), (60, 420, 220), (540, 440, 240))):
        out.append(puff_cloud(D, x, y, w, 3 + k, ("#5A6A88", "#2E3A54", "#121A2A"), op=0.9))
    out.append(lightning(120, 40, 70, 300, 4))
    out.append(lightning(500, 40, 560, 280, 5))
    out.append(soft_glow(D, 300, 330, 230, "#C8D8FF", 0.35))
    # leather cord from the top
    out.append(taper([(300, 0), (296, 80), (300, 162)], 5, 5, "#6A4A2A"))
    out.append(taper([(300, 0), (296, 80), (300, 162)], 1.6, 1.6, "#A87A4A", 0.8))
    out.append(cast(D, 312, 470, 120, 14, color="#000000", strength=0.0, seed=6))
    out.append(mjolnir_amulet(D, 300, 154, 1.0, 7))
    for k in range(10):
        a = random.Random(k).uniform(0, 6.28)
        out.append(sparkle(300 + math.cos(a) * 140, 300 + math.sin(a) * 110, 4, "#E8F0FF", 0.7))
    # knotwork bands top and bottom carry the lettering plates
    out.append(knot_band(D, -10, 610, 50, 26, "#C8A050", "#1A1208", 8))
    out.append(knot_band(D, -10, 610, 560, 26, "#C8A050", "#1A1208", 9))
    out.append(gilt(D, 300, 128, "MJÖLNIR", CINZEL, 60, ls=12, max_w=380, seed=10, deboss="#000000", dop=0.8, pal="silver"))
    out.append(tx(300, 506, "THOR’S HAMMER", CINZEL, 30, "#F2E2B8", ls=8, max_w=420))
    out.append(tx(300, 534, "FROM THE NORSE MYTHS", CINZEL, 15, "#C8D0E0", ls=5, max_w=360))
    return finish_b(D, out, 11, "#000000", 0.5)


# ================================================================ 28. yggdrasil — the world tree
def ash_tree(D, cx, base, h, seed):
    """Yggdrasil: a vast ash, its crown spreading over the sky, three great roots reaching down to three wells."""
    rnd = random.Random(seed)
    out = []
    bark = ("#C8A87A", "#7A5A3A", "#2E1E10")
    # roots
    for k, (ex, ey) in enumerate(((cx - 150, base + 60), (cx, base + 90), (cx + 150, base + 60))):
        p = catmull([(cx + (k - 1) * 20, base - 40), (cx + (k - 1) * 60, base + 10), ((cx + ex) / 2 + (k - 1) * 20, base + 40), (ex, ey)], 6)
        out.append(taper(p, 40, 8, bark[2]))
        out.append(taper(p, 32, 6, bark[1]))
        out.append(taper([(x - 3, y - 2) for x, y in p], 8, 2, bark[0], 0.6))
    # trunk: thick, fluted
    trunk = [(cx - 44, base), (cx - 32, base - h * 0.3), (cx - 26, base - h * 0.55), (cx - 40, base - h * 0.7), (cx + 40, base - h * 0.7), (cx + 26, base - h * 0.55), (cx + 32, base - h * 0.3), (cx + 44, base)]
    out.append(painted(D, trunk, bark, seed, sdir=(1, 0.2), sk=0.22, angle=-90, n=40, inkw=1.8, inkc="#140A04", hi=0.35))
    for k in range(6):
        x = cx - 30 + k * 12
        out.append(pline([(x, base - 4), (x + rnd.uniform(-6, 6), base - h * 0.35), (x * 0.5 + cx * 0.5 + (k - 2.5) * 6, base - h * 0.68)], bark[2], 1.6, seed + k, 0.6, 1))
    # main limbs
    for (ang, L_) in ((-150, 150), (-120, 130), (-90, 110), (-60, 130), (-30, 150)):
        sx, sy = cx, base - h * 0.66
        ex, ey = sx + math.cos(math.radians(ang)) * L_, sy + math.sin(math.radians(ang)) * L_ * 0.8
        out.append(taper(catmull([(sx, sy), ((sx + ex) / 2, (sy + ey) / 2 + 12), (ex, ey)], 6), 18, 4, bark[1]))
    # crown of golden-green dabs
    out.append(dab_crown(D, cx, base - h * 0.95, 200, 110, [("#E8E08A", "#9AB050", "#3E5A2A"), ("#F2D070", "#C8A040", "#6A5020"), ("#B8D88A", "#6A9A4A", "#2A4A22")],
                         seed + 1, n=420, size=(5, 10), inkw=1.2, inkc="#1A2A10"))
    return "".join(out)


def stag(x, base, s, col, flip=False):
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [f'<path d="{smooth_closed(L([(-24, -26), (-20, -38), (14, -40), (22, -34), (24, -24), (12, -20), (-18, -20)]))}" fill="{col}"/>']
    for (a, b) in (((-18, -22), (-20, 0)), ((-12, -22), (-10, 0)), ((14, -22), (16, 0)), ((20, -24), (24, 0))):
        out.append(taper(L([a, b]), 3 * s, 2 * s, col))
    out.append(f'<path d="{smooth_closed(L([(16, -36), (26, -54), (34, -60), (40, -56), (32, -48), (24, -32)]))}" fill="{col}"/>')
    for sg in (0, 1):
        base_ = (30 + sg * 4, -60)
        p = [base_, (base_[0] - 6 + sg * 10, -76), (base_[0] - 10 + sg * 14, -90)]
        out.append(taper(L(p), 2.4 * s, 1, col))
        out.append(taper(L([p[1], (p[1][0] - 8 + sg * 14, p[1][1] - 6)]), 1.8 * s, 0.8, col))
    return "".join(out)


@design("yggdrasil")
def yggdrasil():
    D = Doc2("ft-yg")
    out = [sky(D, [(0, "#0A1A24"), (1, "#14303A")], 1, 600, ["#1A3440", "#06121A"], 40)]
    rnd = random.Random(2)
    # knotwork-dotted ground pattern outside the disc
    for k in range(70):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(star4(x, y, rnd.uniform(2, 4), "#C8A050", rnd.uniform(0.3, 0.6)))
    cx, cy, R = 300, 258, 196
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{R}"/>')
    sc = [f'<rect width="600" height="600" fill="{D.rad([(0, "#2A5A6A"), (0.6, "#12303E"), (1, "#081822")], cx=0.5, cy=0.4, r=0.5)}"/>']
    sc.append(stars_field(3, (cx - R, cy - R, cx + R, cy + R), 140, cols=("#FFFFFF", "#FFF2C8", "#C8F0FF")))
    sc.append(soft_glow(D, cx, cy - 60, 200, "#F2E08A", 0.25))
    # the three wells under the roots
    for (wx, wy) in ((cx - 150, cy + 168), (cx, cy + 196), (cx + 150, cy + 168)):
        sc.append(f'<path d="{smooth_closed(ell_pts(wx, wy, 34, 10, 0, 360, 20))}" fill="#6AC8E0" opacity="0.8"/>')
        sc.append(soft_glow(D, wx, wy, 40, "#9AE8FF", 0.5))
    sc.append(ash_tree(D, cx, cy + 110, 250, 4))
    # the eagle on the crown, the stags browsing, the squirrel on the trunk, the serpent at the root
    ex, ey = cx, cy - 158
    for sg in (-1, 1):
        sc.append(f'<path d="{smooth_closed([(ex, ey - 6), (ex + sg * 20, ey - 18), (ex + sg * 44, ey - 26), (ex + sg * 52, ey - 20), (ex + sg * 46, ey - 14), (ex + sg * 50, ey - 8), (ex + sg * 40, ey - 6), (ex + sg * 42, ey), (ex + sg * 28, ey), (ex + sg * 10, ey + 4)])}" fill="#1A1206"/>')
    sc.append(f'<path d="{smooth_closed([(ex - 8, ey - 8), (ex + 8, ey - 8), (ex + 7, ey + 10), (ex + 10, ey + 20), (ex - 10, ey + 20), (ex - 7, ey + 10)])}" fill="#1A1206"/>')
    sc.append(f'<path d="{blob(ex, ey - 22, 6, 7, 5, 0.05, 10)}" fill="#1A1206"/><path d="M {ex - 2} {ey - 22} l -6 3 l 6 2 Z" fill="#E8B040"/>')
    sc.append(stag(cx - 150, cy - 70, 0.9, "#1A1206"))
    sc.append(stag(cx + 150, cy - 70, 0.9, "#1A1206", flip=True))
    sqx, sqy = cx + 26, cy + 20
    sc.append(f'<path d="{smooth_closed([(sqx, sqy), (sqx + 8, sqy - 10), (sqx + 6, sqy - 22), (sqx + 14, sqy - 30), (sqx + 22, sqy - 22), (sqx + 18, sqy - 4), (sqx + 8, sqy + 6)])}" fill="#C8602A"/>')
    sc.append(f'<path d="{smooth_closed([(sqx + 2, sqy + 2), (sqx - 12, sqy + 4), (sqx - 18, sqy - 10), (sqx - 10, sqy - 16), (sqx - 4, sqy - 6)])}" fill="#E8803A"/>')
    sc.append(f'<circle cx="{sqx + 17}" cy="{sqy - 22}" r="1.6" fill="#1A0A04"/>')
    sp = [(cx - 40 + i * 10, cy + 186 + math.sin(i * 0.9) * 10) for i in range(10)]
    sc.append(taper(sp, 10, 3, "#2E5A3A"))
    sc.append(taper([(x, y - 2) for x, y in sp], 3, 1, "#8AC88A", 0.7))
    sc.append(f'<path d="{blob(cx - 46, cy + 184, 10, 7, 9, 0.1, 10)}" fill="#2E5A3A"/><circle cx="{cx - 50}" cy="{cy + 182}" r="1.6" fill="#F2C84A"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # interlaced ring
    for (r_, w_, c_) in ((R + 4, 22, "#1A1208"), (R + 4, 16, "#C8A050"), (R + 4, 4, "#1A1208")):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r_}" fill="none" stroke="{c_}" stroke-width="{w_}"/>')
    for k in range(36):
        a = 2 * math.pi * k / 36
        x, y = cx + math.cos(a) * (R + 4), cy + math.sin(a) * (R + 4)
        out.append(f'<path d="M {x - math.sin(a) * 6:.1f} {y + math.cos(a) * 6:.1f} Q {x + math.cos(a) * 9:.1f} {y + math.sin(a) * 9:.1f} {x + math.sin(a) * 6:.1f} {y - math.cos(a) * 6:.1f}" stroke="#1A1208" stroke-width="2" fill="none"/>')
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        out.append(f'<circle cx="{cx + math.cos(a) * (R + 4):.1f}" cy="{cy + math.sin(a) * (R + 4):.1f}" r="7" fill="#F2D88A" stroke="#1A1208" stroke-width="2"/>')
    out.append(gilt(D, 300, 512, "Yggdrasil", SERIF_IT, 58, max_w=380, seed=10, deboss="#000000", dop=0.8))
    out.append(tx(300, 540, "THE WORLD TREE · NORSE MYTH", CINZEL, 15, "#C8E0E8", ls=3, max_w=380))
    return finish_b(D, out, 11, "#000000", 0.5)


# ================================================================ 29. king arthur — the sword in the stone, a snowy churchyard
def sword_upright(D, cx, tip_y, top_y, seed):
    out = []
    blade = [(cx - 7, tip_y), (cx - 7, top_y + 60), (cx + 7, top_y + 60), (cx + 7, tip_y)]
    out.append(painted(D, blade, ("#FFFFFF", "#C8D0DC", "#5A6478"), seed, sdir=(1, 0.1), sk=0.3, angle=-90, n=8, inkw=1.4, inkc="#2A303C", hi=0.6))
    out.append(f'<path d="M {cx} {tip_y} L {cx} {top_y + 60}" stroke="#7A8498" stroke-width="1.6"/>')
    # cross-guard, grip, pommel
    out.append(painted(D, rect_pts(cx - 52, top_y + 48, cx + 52, top_y + 62, 10, seed + 1, 0.3), GOLD, seed + 1, sk=0.25, angle=0, n=8, inkw=1.4, inkc="#5A3A08", hi=0.6))
    for sg in (-1, 1):
        out.append(f'<circle cx="{cx + sg * 54}" cy="{top_y + 55}" r="7" fill="{GOLD[1]}" stroke="#5A3A08" stroke-width="1.2"/>')
    out.append(painted(D, rect_pts(cx - 7, top_y + 12, cx + 7, top_y + 48, 6, seed + 2, 0.3), ("#8A4A3A", "#5A2418", "#24100A"), seed + 2, sk=0.25, angle=-90, n=4, inkw=1.2, hi=0.4))
    for k in range(5):
        out.append(f'<path d="M {cx - 7} {top_y + 16 + k * 7} L {cx + 7} {top_y + 20 + k * 7}" stroke="{GOLD[1]}" stroke-width="1.6"/>')
    out.append(painted(D, blob_pts(cx, top_y + 4, 13, 13, seed + 3, 0.02, 14), GOLD, seed + 3, sk=0.2, n=4, inkw=1.4, inkc="#5A3A08", hi=0.6))
    out.append(f'<circle cx="{cx}" cy="{top_y + 4}" r="5" fill="#C8203A"/><circle cx="{cx - 1.5}" cy="{top_y + 2.5}" r="1.6" fill="#FFB0B0"/>')
    out.append(taper([(cx - 3, top_y + 70), (cx - 3, tip_y - 6)], 2, 1, "#FFFFFF", 0.8))
    return "".join(out)


@design("king-arthur")
def king_arthur():
    D = Doc2("ft-ka")
    out = [sky(D, [(0, "#3A4A7A"), (0.5, "#A8A0C0"), (0.8, "#F2D8C0"), (1, "#FCE8D0")], 1, 600, ["#5A6A9A", "#E8D0D0", "#FFFFFF"], 50)]
    out.append(soft_glow(D, 120, 120, 240, "#FFF4D8", 0.55))
    # the great church behind: gothic west front in mist
    ch = "#8A88A8"
    out.append(f'<path d="{pd([(360, 380), (360, 180), (400, 120), (440, 180), (440, 380)])}" fill="{ch}"/>')
    out.append(f'<path d="{pd([(440, 380), (440, 230), (520, 230), (520, 380)])}" fill="{ch}"/>')
    out.append(f'<path d="{pd([(520, 380), (520, 160), (550, 110), (580, 160), (580, 380)])}" fill="{ch}"/>')
    for (x, y, w, h) in ((390, 230, 20, 60), (468, 260, 24, 70), (540, 200, 20, 60)):
        out.append(f'<path d="{smooth_closed(arch_pts(x, x + w, y + w / 2, y + h, 6, "pointed", 0.4))}" fill="#FFE2A0" opacity="0.85"/>')
        out.append(soft_glow(D, x + w / 2, y + h / 2, 30, "#FFD27A", 0.4))
    out.append(f'<path d="{pd([(400, 120), (400, 96)], False)}" stroke="{ch}" stroke-width="3"/><path d="M 392 104 L 408 104" stroke="{ch}" stroke-width="3"/>')
    out.append(mist(D, 360, 90, 4, "#F2E8EC", 0.65))
    # snowy churchyard: ground, a yew, a few headstones
    out.append(hill(D, [(-20, 420), (160, 404), (320, 412), (460, 400), (620, 410)], 620, ("#FFFFFF", "#E2E6F2", "#9AA0BE"), 5, inkw=0, sop=(0.1, 0.25)))
    for (x, h) in ((470, 34), (520, 28), (566, 38)):
        out.append(painted(D, arch_pts(x - 11, x + 11, 412 - h + 11, 412, 6), ("#C8C4D0", "#8A869A", "#4A4660"), x, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.3))
        out.append(f'<path d="{blob(x, 412 - h, 12, 3, x, 0.1, 8)}" fill="#FFFFFF"/>')
    out.append(dab_crown(D, 70, 310, 70, 110, [("#5A7A6A", "#2E4A3E", "#14281E")], 6, n=160, size=(5, 10), inkw=0))
    out.append(snowfall(7, (0, 0, 600, 600), 90, (0.8, 2.4)))
    # the light falling on the stone
    out.append(f'<path d="{pd([(60, 0), (190, 0), (380, 470), (220, 470)])}" fill="#FFF6D8" opacity="0.22"/>')
    # the stone and the anvil, the sword
    out.append(cast(D, 312, 476, 170, 16, strength=0.45, seed=8))
    stone = [(160, 478), (150, 440), (170, 396), (220, 380), (300, 376), (380, 384), (430, 404), (446, 448), (440, 478)]
    out.append(painted(D, stone, ("#D8D4DC", "#9A96A8", "#4A4658"), 9, sdir=(0.7, 0.4), sk=0.18, angle=-30, n=60, inkw=2, inkc="#2A2838", hi=0.4))
    out.append(f'<path d="{smooth_closed([(176, 400), (220, 382), (300, 378), (380, 386), (420, 400), (380, 396), (300, 390), (220, 394)])}" fill="#FFFFFF"/>')
    rnd = random.Random(10)
    for k in range(10):
        out.append(f'<path d="{blob(rnd.uniform(180, 420), rnd.uniform(420, 470), rnd.uniform(6, 14), 4, k, 0.3, 8)}" fill="#6A8A5A" opacity="0.5"/>')
    # inscription carved in gilt on the stone's face
    for (yy, s_, fs) in ((440, "RIGHTWISE KING", 25), (464, "BORN OF ALL ENGLAND", 16)):
        out.append(tx(300.8, yy + 1.2, s_, CINZEL, fs, "#FFFFFF", ls=2, max_w=240, op=0.8))
        out.append(tx(300, yy, s_, CINZEL, fs, "#2A2440", ls=2, max_w=240))
    anvil = [(232, 384), (240, 362), (210, 356), (204, 346), (380, 346), (392, 334), (396, 350), (368, 362), (368, 384)]
    out.append(painted(D, anvil, ("#8A90A0", "#4A505E", "#1A1E28"), 13, sdir=(0.6, 0.6), sk=0.2, angle=0, n=20, inkw=1.6, inkc="#0A0C10", hi=0.45))
    out.append(f'<path d="M 206 346 L 380 346" stroke="#FFFFFF" stroke-width="2.4" opacity="0.8"/>')
    out.append(soft_glow(D, 300, 250, 120, "#FFF6D0", 0.55))
    out.append(sword_upright(D, 300, 350, 150, 14))
    out.append(sparkle(300, 153, 18, "#FFFFFF", 0.95))
    # lettering
    out.append(gilt(D, 300, 108, "King Arthur", SERIF_IT, 62, max_w=360, seed=15, deboss="#141C3A", dop=0.6))
    out.append(tx(300, 528, "THE SWORD IN THE STONE", CINZEL, 22, "#2A2838", ls=4, max_w=420))
    return finish_b(D, out, 16, INK, 0.5)


# ================================================================ 30. robin hood — the split arrow in Sherwood
def arrow(D, x0, y0, x1, y1, seed, fletch=("#FFFFFF", "#E8E0D0", "#8A7A6A"), shaft="#C8925A"):
    """Arrow from nock (x0, y0) to where it sinks into the target (x1, y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = [taper([(x0, y0), (x1, y1)], 4, 3.6, "#5A3A1A"), taper([(x0, y0), (x1, y1)], 2.4, 2.2, shaft)]
    for sg in (-1, 1):
        f = [(x0 + ux * 4, y0 + uy * 4), (x0 + ux * 34 + nx * sg * 2, y0 + uy * 34 + ny * sg * 2), (x0 + ux * 26 + nx * sg * 12, y0 + uy * 26 + ny * sg * 12), (x0 + nx * sg * 10, y0 + ny * sg * 10)]
        out.append(painted(D, f, fletch, seed + sg, sk=0.2, n=3, inkw=1, inkc="#3A2A1A", hi=0.4))
    out.append(f'<path d="{pd([(x0 - ux * 2 + nx * 3, y0 - uy * 2 + ny * 3), (x0 - ux * 6, y0 - uy * 6), (x0 - ux * 2 - nx * 3, y0 - uy * 2 - ny * 3)])}" fill="#3A2A1A"/>')
    return "".join(out)


def target_butt(D, cx, cy, r, seed):
    """A straw archery butt with a painted face: gold, red, blue, black, white rings."""
    out = [cast(D, cx + 20, cy + r * 1.05, r * 0.95, 14, strength=0.45, seed=seed)]
    # tripod legs behind
    for (a, b) in (((cx - r * 0.6, cy + r * 0.3), (cx - r * 0.9, cy + r * 1.06)), ((cx + r * 0.6, cy + r * 0.3), (cx + r * 0.9, cy + r * 1.06)), ((cx, cy), (cx + 10, cy + r * 1.1))):
        out.append(taper([a, b], 12, 9, WOOD[1]))
    straw = blob_pts(cx, cy, r, r * 0.97, seed, 0.02, 30)
    out.append(painted(D, straw, ("#F2D890", "#C8A050", "#7A5A20"), seed, sdir=(0.6, 0.6), sk=0.15, angle=0, n=40, inkw=1.8, hi=0.35))
    rnd = random.Random(seed)
    for k in range(10):
        rr = r * (0.94 - k * 0.012)
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{rnd.choice(["#A8802A", "#E8C870"])}" stroke-width="1" opacity="0.5"/>')
    rings = [("#FFFFFF", 0.86), ("#1A1A1A", 0.7), ("#2E5AA8", 0.54), ("#C8282A", 0.38), ("#F6C21C", 0.2)]
    for col, f in rings:
        out.append(painted(D, blob_pts(cx, cy, r * f, r * f, seed + int(f * 100), 0.006, 30), (lt(col, 0.3), col, dk(col, 0.4)), seed + int(f * 100), sk=0.1, n=int(r * f * 0.4) + 4, inkw=1, hi=0.25))
    out.append(f'<path d="M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 0 {cx + r:.1f} {cy:.1f}" fill="none" stroke="#000000" stroke-width="0" />')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r, r, 0, 180, 30))}" fill="#000000" opacity="0.0"/>')
    sh = D.rad([(0, "#000000", 0), (0.65, "#000000", 0.0), (1, "#2A1A04", 0.4)], cx=0.38, cy=0.35, r=0.7)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sh}"/>')
    return "".join(out)


def oak_leaf(D, x, y, s, ang, seed, pal=(("#9AC07A", "#4E7A3E", "#20401E"))):
    pts = []
    for i in range(36):
        t = i / 35
        lobe = 1 + 0.32 * math.sin(t * math.pi * 9) ** 2
        w = s * 0.32 * math.sin(math.pi * t) ** 0.8 * lobe
        pts.append((t * s, w))
    pts = pts + [(px, -py) for px, py in pts[::-1]]
    pts = T(pts, x, y, 1, False, ang)
    out = [painted(D, pts, pal, seed, sk=0.16, angle=ang + 30, n=int(s * 0.3) + 4, inkw=1.1, inkc="#14301A", hi=0.35)]
    out.append(pline(T([(0, 0), (s * 0.95, 0)], x, y, 1, False, ang), lt(pal[0], 0.3), 1.1, seed, 0.6, 1))
    return "".join(out)


@design("robin-hood")
def robin_hood():
    D = Doc2("ft-rh")
    out = [sky(D, [(0, "#2E4A2A"), (0.5, "#6A8A4A"), (1, "#C8C080")], 1, 600, ["#3E5A30", "#9AB060", "#1E3A1E"], 60)]
    out.append(soft_glow(D, 300, 260, 300, "#FFF2C0", 0.5))
    rnd = random.Random(3)
    for k, (x, w) in enumerate(((60, 50), (150, 30), (450, 34), (540, 56), (230, 18), (380, 20))):
        out.append(gnarled_trunk(D, x, 470, -20, w, 10 + k, ("#8A8A60", "#5A5A3A", "#2A2A1A") if w > 25 else ("#B8B890", "#9A9A70", "#6A6A4A"), lean=rnd.uniform(-0.03, 0.03), roots=w > 25, branches=1))
    out.append(dab_crown(D, 300, 40, 380, 110, [("#9AC07A", "#5A8A48", "#2A4A26"), ("#B8D08A", "#7AA060", "#3E5A30")], 4, n=260, size=(8, 14), inkw=0))
    out.append(hill(D, [(-20, 470), (200, 460), (400, 466), (620, 456)], 620, ("#9AB060", "#5A7A3A", "#2A3A1A"), 5, inkw=0, sop=(0.15, 0.35)))
    out.append(grass(6, (0, 460, 600, 600), ["#4A6A2A", "#7A9A48", "#2A4A1A", "#A8C070"], 260, (8, 24)))
    # the target, with the famous split arrow in the gold
    tcx, tcy, tr = 300, 300, 124
    out.append(target_butt(D, tcx, tcy, tr, 7))
    out.append(arrow(D, 190, 170, 262, 262, 8, fletch=("#E8E0D0", "#B8A890", "#6A5A4A")))
    out.append(arrow(D, 420, 210, 342, 286, 9, fletch=("#8AB87A", "#4E7A3E", "#20401E")))
    out.append(arrow(D, 230, 420, 286, 336, 10, fletch=("#F28A7A", "#C8302A", "#6A0E0A")))
    # the split arrow: Robin's shaft driven through the first, which splinters
    out.append(arrow(D, 300, 150, 300, 300, 11, fletch=("#8AB87A", "#2E6A3A", "#10301A")))
    for sg in (-1, 1):
        out.append(taper([(300 + sg * 2, 214), (300 + sg * 10, 186), (300 + sg * 16, 168)], 3, 1.6, "#C8925A"))
        out.append(painted(D, [(300 + sg * 14, 168), (300 + sg * 24, 140), (300 + sg * 30, 146), (300 + sg * 20, 172)], ("#FFFFFF", "#E8E0D0", "#8A7A6A"), 12 + sg, sk=0.2, n=3, inkw=1, hi=0.4))
    out.append(sparkle(300, 300, 12, "#FFFFFF", 0.9))
    # oak leaves and acorns framing the lower corners
    for k, (x, y, s_, a) in enumerate(((30, 560, 70, -60), (70, 590, 60, -30), (110, 580, 56, -80), (570, 560, 70, -120), (530, 590, 60, -150), (490, 580, 56, -100))):
        out.append(oak_leaf(D, x, y, s_, a, 20 + k))
    from gouache import acorn as _acorn
    out.append(_acorn(120, 540, 16, -20) + _acorn(484, 540, 16, 20))
    # banner and lettering
    out.append(ribbon(D, 300, 498, 330, 46, ("#9AC07A", "#2E6A3A", "#123A1E"), 13, tail=36))
    out.append(tx(300, 506, "SHERWOOD FOREST", CINZEL, 20, "#FFF6DC", ls=4, max_w=270))
    out.append(letters(D, 300, 112, "Robin Hood", SERIF_IT, 72, "#FFF2D0", ["#FFFFFF", "#F2D890", "#FFE8B0"], 14, max_w=420,
                       shadow="#14280E", soff=(0.02, 0.05), angle=-40, wob=0.5))
    out.append(tx(300, 548, "", CINZEL, 10, "#000"))
    return finish_b(D, out, 15, INK, 0.5)


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
