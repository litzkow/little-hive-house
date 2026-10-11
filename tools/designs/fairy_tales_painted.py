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
import re
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (apple, blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps, mist, ribbon, leaf)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
from paint import conifer, rough, y_on
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


# =====================================================================================================
# GALLERY EDITION (2026-10 repaint). Every design below re-registers its slug with a new painting; the
# first-edition functions above stay in place because other generators import helpers from this file.
#
# The engine paints forms the way a painter does: a form is described by simple volumes (ellipsoids and
# tapered capsules), a light falls on them, and the picture is built from hundreds of translucent brush
# strokes whose colour comes from that light (core shadow, half-tone, light, highlight, cool reflected light,
# warm rim light), laid in passes from broad underpainting to small accents. Edges are lost on the light
# side and found on the shadow side. painterly() is the varnish on top.
# =====================================================================================================
from painterly import painterly


def _rgb3(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def ramp(cols, t):
    """Colour at t (0..1) along a list of hex colours."""
    t = max(0.0, min(1.0, t))
    k = t * (len(cols) - 1)
    i = min(int(k), len(cols) - 2)
    return mix(cols[i], cols[i + 1], k - i)


def gstop(stops, t):
    """Colour of a gradient [(offset, colour), ...] at t."""
    if t <= stops[0][0]:
        return stops[0][1]
    for (o0, c0), (o1, c1) in zip(stops, stops[1:]):
        if t <= o1:
            return mix(c0, c1, (t - o0) / max(1e-6, o1 - o0))
    return stops[-1][1]


def _norm3(v):
    L = math.sqrt(sum(a * a for a in v)) or 1.0
    return tuple(a / L for a in v)


def E(cx, cy, rx, ry, rot=0.0, k=1.0, depth=1.0):
    """Ellipsoid volume. k = priority bias, depth = how round it is toward the viewer."""
    return ("e", cx, cy, rx, ry, rot, k, depth)


def C(x1, y1, x2, y2, r1, r2=None, k=1.0):
    """Tapered capsule volume (limbs, neck, feathers, trunks)."""
    return ("c", x1, y1, x2, y2, r1, r1 if r2 is None else r2, k)


def surf(prims, x, y, soft=10.0):
    """Surface normal (nx, ny, nz), depth z and the dominant primitive at (x, y); None outside every volume.
    Normals of overlapping volumes are blended by depth (soft-max), so joins read as one continuous form."""
    hits = []
    for p in prims:
        if p[0] == "e":
            _, cx, cy, rx, ry, rot, k, depth = p
            a = math.radians(rot)
            ca, sa = math.cos(a), math.sin(a)
            dx, dy = x - cx, y - cy
            lx, ly = dx * ca + dy * sa, -dx * sa + dy * ca
            u, v = lx / rx, ly / ry
            q = u * u + v * v
            if q >= 1:
                continue
            nz = math.sqrt(1 - q)
            rz = min(rx, ry) * depth
            n = _norm3((u / rx, v / ry, nz / rz))
            nx, ny = n[0] * ca - n[1] * sa, n[0] * sa + n[1] * ca
            hits.append(((nx, ny, n[2]), rz * nz * k, p, (u, v)))
        else:
            _, x1, y1, x2, y2, r1, r2, k = p
            vx, vy = x2 - x1, y2 - y1
            L2 = vx * vx + vy * vy or 1.0
            t = max(0.0, min(1.0, ((x - x1) * vx + (y - y1) * vy) / L2))
            r = r1 + (r2 - r1) * t
            dx, dy = x - (x1 + vx * t), y - (y1 + vy * t)
            d = math.hypot(dx, dy)
            if d >= r:
                continue
            nz = math.sqrt(max(0.0, 1 - (d / r) ** 2))
            n = _norm3((dx / r, dy / r, nz))
            hits.append((n, r * nz * k, p, (t, d / r)))
    if not hits:
        return None
    zmax = max(h[1] for h in hits)
    best = max(hits, key=lambda h: h[1])
    if len(hits) == 1 or not soft:
        return (best[0], None, None, best[1], best[2], best[3])
    sx = sy = sz = 0.0
    for n, z, p, uv in hits:
        w = math.exp((z - zmax) / soft)
        sx, sy, sz = sx + n[0] * w, sy + n[1] * w, sz + n[2] * w
    return (_norm3((sx, sy, sz)), None, None, best[1], best[2], best[3])


def prim_axis(p):
    """Main axis angle (degrees) of a primitive: used for strokes that follow the form."""
    if p[0] == "e":
        return p[5] if p[3] >= p[4] else p[5] + 90
    return math.degrees(math.atan2(p[4] - p[2], p[3] - p[1]))


class Look:
    """How light falls on a form.
    cols: dark -> light ramp (core shadow ... highlight). key: direction the key light comes FROM (x, y, z),
    screen coords (y down, z toward viewer). rim: (colour, (x, y) direction of a back light, strength).
    bounce: (colour, strength) cool/warm light reflected into the shadow from below."""

    def __init__(self, cols, key=(-0.6, -0.7, 0.55), amb=0.12, wrap=0.35, rim=None, bounce=None, spec=None, jit=0.07,
                 gamma=1.0, tint=None):
        self.cols, self.key, self.amb, self.wrap = cols, _norm3(key), amb, wrap
        self.rim, self.bounce, self.spec, self.jit, self.gamma, self.tint = rim, bounce, spec, jit, gamma, tint

    def value(self, n):
        d = n[0] * self.key[0] + n[1] * self.key[1] + n[2] * self.key[2]
        v = (d + self.wrap) / (1 + self.wrap)
        v = self.amb + (1 - self.amb) * max(0.0, v)
        return v ** self.gamma

    def color(self, n, rnd, extra=0.0):
        v = self.value(n) + extra + rnd.uniform(-self.jit, self.jit)
        c = ramp(self.cols, v)
        if self.bounce and n[1] > 0.15 and v < 0.55:
            c = mix(c, self.bounce[0], self.bounce[1] * min(1.0, (n[1] - 0.15) * 1.6) * (0.55 - v) / 0.55)
        if self.rim:
            col, (rx, ry), s = self.rim
            rr = math.hypot(rx, ry) or 1
            f = max(0.0, (n[0] * rx + n[1] * ry) / rr) * max(0.0, 1 - n[2]) ** 1.6
            if f > 0.05:
                c = mix(c, col, min(1.0, f * s))
        if self.spec and v > self.spec[1]:
            c = mix(c, self.spec[0], min(1.0, (v - self.spec[1]) / max(0.01, 1 - self.spec[1])) * self.spec[2])
        if self.tint:
            c = mix(c, self.tint[0], self.tint[1])
        return c


def bstroke(x, y, ang, L, w, col, op, bend=0.0):
    """One tapered, slightly curved brush stroke centred on (x, y)."""
    a = math.radians(ang)
    dx, dy = L * math.cos(a) / 2, L * math.sin(a) / 2
    nx, ny = -math.sin(a), math.cos(a)
    x0, y0, x1, y1 = x - dx, y - dy, x + dx, y + dy
    mx, my = x + nx * bend, y + ny * bend
    return (f'<path d="M{x0:.1f} {y0:.1f}Q{mx + nx * w:.1f} {my + ny * w:.1f} {x1:.1f} {y1:.1f}'
            f'Q{mx - nx * w:.1f} {my - ny * w:.1f} {x0:.1f} {y0:.1f}Z" fill="{col}" opacity="{op:.2f}"/>')


def dab(x, y, r, col, op, rnd, squash=0.75, rot=None):
    """A loaded-brush dab: a soft irregular blot."""
    rot = math.radians(rnd.uniform(0, 180) if rot is None else rot)
    ca, sa = math.cos(rot), math.sin(rot)
    ry = r * squash
    # four quadratic lobes, written relative so the path stays short
    k = [rnd.uniform(0.85, 1.25) for _ in range(4)]
    P0 = (r * ca, r * sa)
    P1 = (-ry * sa, ry * ca)
    pts = [(P0[0], P0[1]), (P1[0], P1[1]), (-P0[0], -P0[1]), (-P1[0], -P1[1])]
    s = f'M{x + pts[0][0]:.1f} {y + pts[0][1]:.1f}'
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        cx_, cy_ = (a[0] + b[0]) * k[i], (a[1] + b[1]) * k[i]
        s += f'q{cx_ - a[0]:.1f} {cy_ - a[1]:.1f} {b[0] - a[0]:.1f} {b[1] - a[1]:.1f}'
    return f'<path d="{s}" fill="{col}" opacity="{op:.2f}"/>'


def _inpoly(pts, x, y):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def model(D, prims, look, seed, box=None, poly=None, passes=((70, (16, 34), (5, 10), (0.35, 0.6)),
                                                            (150, (8, 18), (2.4, 5), (0.45, 0.8)),
                                                            (90, (4, 9), (1.2, 2.6), (0.55, 0.9))),
          flow="axis", flow_jit=14, clip=None, density=1.0, dabs=False, edge_soft=0.0, value_fn=None, extra_fn=None):
    """Paint the volumes `prims` with brush strokes coloured by `look`.
    passes: (count per 10 000 px2, length range, half-width range, opacity range), broad to fine.
    flow: 'axis' (along each volume), 'contour' (around the form), a fixed angle, or a callable(x, y, n, p)->deg.
    poly: restrict strokes to this outline; clip: an SVG clip-path attribute for the group."""
    rnd = random.Random(seed)
    if box is None:
        xs, ys = [], []
        for p in prims:
            if p[0] == "e":
                r = max(p[3], p[4])
                xs += [p[1] - r, p[1] + r]
                ys += [p[2] - r, p[2] + r]
            else:
                r = max(p[5], p[6])
                xs += [p[1] - r, p[3] - r, p[1] + r, p[3] + r]
                ys += [p[2] - r, p[4] - r, p[2] + r, p[4] + r]
        box = (min(xs), min(ys), max(xs), max(ys))
    x0, y0, x1, y1 = box
    area = (x1 - x0) * (y1 - y0)
    out = []
    for cnt, Lr, Wr, Or in passes:
        n = int(cnt * area / 10000 * density)
        for _ in range(n):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if poly is not None and not _inpoly(poly, x, y):
                continue
            s = surf(prims, x, y)
            if s is None:
                continue
            nrm, _, _, z, p, uv = s
            ex = value_fn(x, y) if value_fn else 0.0
            col = look.color(nrm, rnd, ex)
            if extra_fn:
                col = extra_fn(x, y, col, nrm) or col
            if callable(flow):
                ang = flow(x, y, nrm, p)
            elif flow == "axis":
                ang = prim_axis(p)
            elif flow == "contour":
                ang = math.degrees(math.atan2(nrm[1], nrm[0])) + 90
            else:
                ang = flow
            ang += rnd.uniform(-flow_jit, flow_jit)
            op = rnd.uniform(*Or)
            if edge_soft:
                op *= min(1.0, nrm[2] / edge_soft + 0.15)
            if dabs:
                out.append(dab(x, y, rnd.uniform(*Wr) * 1.6, col, op, rnd))
            else:
                out.append(bstroke(x, y, ang, rnd.uniform(*Lr), rnd.uniform(*Wr), col, op, rnd.uniform(-2, 2)))
    g = "".join(out)
    if clip:
        return f'<g {clip}>{g}</g>'
    return g


def outline_normals(pts):
    """Outward 2D normals of a closed outline (works for either winding)."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        tx_, ty_ = bx - ax, by - ay
        L = math.hypot(tx_, ty_) or 1
        out.append((sgn * ty_ / L, -sgn * tx_ / L))
    return out


def vline(pts, widths, col, op):
    """A variable-width brush line through pts."""
    n = len(pts)
    if n < 2:
        return ""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    poly = left + right[::-1]
    return f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in poly)}Z" fill="{col}" opacity="{op:.2f}"/>'


def edges(pts, light, seed, dark=INK, lit=None, w=2.2, closed=True, dark_op=0.75, lit_op=0.7, lit_w=None, thresh=0.0,
          mask=None):
    """Lost-and-found edges: a dark brush line that swells where the outline turns away from `light` (x, y = the
    direction the light comes FROM) and vanishes where it faces the light; optional `lit` rim on the lit side.
    pts should be densely resampled. mask(x, y) -> False suppresses the edge there (e.g. where limbs join)."""
    rnd = random.Random(seed)
    ns = outline_normals(pts)
    lx, ly = light
    L = math.hypot(lx, ly) or 1
    lx, ly = lx / L, ly / L
    n = len(pts)
    fac = [ns[i][0] * lx + ns[i][1] * ly for i in range(n)]
    # slow random modulation so the line breaks and swells like a hand-drawn contour
    ph1, ph2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    mod = [0.75 + 0.35 * math.sin(i * 0.21 + ph1) * math.sin(i * 0.053 + ph2) for i in range(n)]
    out = []

    def runs(test):
        cur = []
        for i in range(n):
            ok = test(i) and (mask is None or mask(*pts[i]))
            if ok:
                cur.append(i)
            elif cur:
                yield cur
                cur = []
        if cur:
            yield cur
    if dark:
        for r in runs(lambda i: fac[i] < thresh):
            if len(r) < 3:
                continue
            m = len(r)
            ws = []
            for j, i in enumerate(r):
                k = min(1.0, (thresh - fac[i]) * 1.4)
                end = min(1.0, j / 4, (m - 1 - j) / 4)
                ws.append(max(0.15, w * (0.35 + 0.85 * k) * mod[i] * end))
            out.append(vline([pts[i] for i in r], ws, dark, dark_op))
    if lit:
        for r in runs(lambda i: fac[i] > 0.25):
            if len(r) < 3:
                continue
            m = len(r)
            ws = []
            for j, i in enumerate(r):
                k = min(1.0, (fac[i] - 0.25) * 1.6)
                end = min(1.0, j / 4, (m - 1 - j) / 4)
                ws.append(max(0.1, (lit_w or w) * (0.3 + 0.9 * k) * mod[i] * end))
            out.append(vline([pts[i] for i in r], ws, lit, lit_op))
    return "".join(out)


def resample(pts, step=4.0, closed=True):
    """Points every ~step px along the smooth (Catmull-Rom) curve through pts."""
    P_ = list(pts) + ([pts[0], pts[1], pts[2]] if closed else [])
    out = []
    n = len(pts) if closed else len(pts) - 1
    for i in range(n):
        p0 = P_[i - 1] if (i > 0 or closed) else P_[0]
        p1, p2 = P_[i], P_[i + 1]
        p3 = P_[i + 2] if i + 2 < len(P_) else P_[-1]
        seg = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        m = max(1, int(seg / step))
        for k in range(m):
            t = k / m
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def form(D, pts, prims, look, seed, base=None, passes=None, flow="axis", flow_jit=14, density=1.0, edge_light=None,
         edge_col=INK, edge_w=2.0, edge_op=0.7, rim_col=None, rim_w=None, rim_op=0.7, value_fn=None, extra_fn=None,
         under=True, edge_thresh=0.0, edge_mask=None):
    """A fully painted solid: underpaint wash (gradient along the light), modelled strokes clipped to the outline,
    and lost-and-found edges. pts = control points of the outline."""
    d = smooth_closed(pts)
    fine = resample(pts, 3.0)
    x0, y0, x1, y1 = bbox(fine)
    kx, ky = look.key[0], look.key[1]
    out = []
    if under:
        c_lit = ramp(look.cols, 0.68)
        c_mid = ramp(look.cols, 0.52)
        c_dk = ramp(look.cols, 0.38)
        g = D.lin([(0, c_lit), (0.5, c_mid), (1, c_dk)], 0.5 + kx * 0.5, 0.5 + ky * 0.5, 0.5 - kx * 0.5, 0.5 - ky * 0.5)
        out.append(f'<path d="{d}" fill="{base or g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    kw = {}
    if passes:
        kw["passes"] = passes
    out.append(model(D, prims, look, seed, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), fine, flow=flow, flow_jit=flow_jit, clip=cid,
                     density=density, value_fn=value_fn, extra_fn=extra_fn, **kw))
    el = edge_light or (look.key[0], look.key[1])
    out.append(edges(fine, el, seed + 5, edge_col, rim_col, edge_w, dark_op=edge_op, lit_op=rim_op, lit_w=rim_w, thresh=edge_thresh,
                     mask=edge_mask))
    return "".join(out)


# ---------------------------------------------------------------- atmosphere
def sky_paint(D, stops, seed, y0=0, y1=600, n=260, L=(60, 200), W=(4, 12), op=(0.08, 0.28), angle=0, jit=0.06, x0=-20, x1=620):
    """Graded sky + broad horizontal brushwork whose colour is sampled from the gradient (so the texture
    belongs to the sky instead of sitting on it)."""
    rnd = random.Random(seed)
    g = D.lin([(o, c) for o, c in stops], 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>']
    for _ in range(n):
        y = rnd.uniform(y0 - 10, y1 + 10)
        t = (y - y0) / max(1, y1 - y0) + rnd.uniform(-jit, jit)
        c = gstop(stops, max(0, min(1, t)))
        c = lt(c, rnd.uniform(0, 0.12)) if rnd.random() < 0.5 else dk(c, rnd.uniform(0, 0.08))
        out.append(bstroke(rnd.uniform(x0, x1), y, angle + rnd.uniform(-3, 3), rnd.uniform(*L), rnd.uniform(*W), c, rnd.uniform(*op), rnd.uniform(-3, 3)))
    return "".join(out)


def halo(D, cx, cy, r, col, s=0.8, ry=None, mid=0.4):
    g = D.rad([(0, col, s), (mid, col, s * 0.42), (1, col, 0)])
    if ry:
        return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


def cloud(D, cx, cy, w, h, seed, look, n_puffs=14, flat=0.25, density=1.0, base_col=None, size=(5, 12), op=(0.35, 0.8),
          wisps=0, wisp_col=None, puffs=None, rscale=1.0):
    """A cumulus mass painted from soft dabs coloured by the light on its puffs; edges dissolve into the sky."""
    rnd = random.Random(seed)
    prims = []
    if puffs is None:
        for i in range(n_puffs):
            t = rnd.uniform(-1, 1)
            px = cx + t * w * 0.42
            top = 1 - abs(t) ** 1.6
            py = cy - h * 0.15 - rnd.uniform(0, h * 0.42) * top
            r = rnd.uniform(0.16, 0.3) * w * (0.55 + 0.45 * top) * rscale
            prims.append(E(px, py, r, r * rnd.uniform(0.75, 0.95), rnd.uniform(-20, 20), 1.0, 0.9))
        prims.append(E(cx, cy + h * 0.1, w * 0.48, h * 0.28, 0, 0.6, 0.5))
    else:
        prims = puffs
    bottom = cy + h * (0.5 - flat)
    out = []
    # soft body
    for p in prims:
        if p[0] == "e":
            c = base_col or ramp(look.cols, 0.45)
            out.append(f'<path d="{blob(p[1], min(p[2], bottom - p[4] * 0.3), p[3] * 0.92, min(p[4] * 0.9, max(4, bottom - p[2] + p[4] * 0.2)), rnd.randint(0, 9999), 0.12, 14, p[5])}" fill="{c}" opacity="0.55"/>')
    xs = [p[1] - p[3] for p in prims if p[0] == "e"] + [p[1] + p[3] for p in prims if p[0] == "e"]
    ys = [p[2] - p[4] for p in prims if p[0] == "e"]
    box = (min(xs), min(ys), max(xs), bottom)
    area = (box[2] - box[0]) * (box[3] - box[1])
    cnt = int(area / 34 * density)
    st = []
    for _ in range(cnt):
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        s = surf(prims, x, y)
        if s is None:
            continue
        nrm = s[0]
        ex = -0.25 * max(0, (y - (bottom - h * 0.3)) / (h * 0.3))  # flat, shaded underside
        col = look.color(nrm, rnd, ex)
        o = rnd.uniform(*op) * min(1.0, nrm[2] * 2.2 + 0.1)
        st.append(dab(x, y, rnd.uniform(*size), col, o, rnd, 0.62, rnd.uniform(-25, 25)))
    out.append("".join(st))
    if wisps:
        wc = wisp_col or ramp(look.cols, 0.85)
        for i in range(wisps):
            y = bottom - rnd.uniform(0, h * 0.2)
            out.append(bstroke(cx + rnd.uniform(-w * 0.5, w * 0.5), y, rnd.uniform(-4, 4), rnd.uniform(w * 0.2, w * 0.55), rnd.uniform(1.5, 4), wc, rnd.uniform(0.2, 0.45)))
    return "".join(out)


def water_paint(D, y0, y1, stops, seed, n=420, refl=None, refl_x=300, refl_w=80, refl_col="#FFF2C8", glints=120, x0=-20, x1=620):
    """Open water: graded base, horizontal broken strokes (darker troughs, lighter crests), a broken
    reflection column under the light source and sparkling glints."""
    rnd = random.Random(seed)
    g = D.lin(stops, 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>']
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        c = gstop(stops, t)
        c = lt(c, rnd.uniform(0.05, 0.22)) if rnd.random() < 0.45 else dk(c, rnd.uniform(0.06, 0.25))
        L = rnd.uniform(10, 40) * (0.4 + t * 1.4)
        out.append(bstroke(rnd.uniform(x0, x1), y, rnd.uniform(-2, 2), L, rnd.uniform(0.6, 1.8) * (0.5 + t * 1.6), c, rnd.uniform(0.3, 0.7)))
    if refl:
        for _ in range(glints):
            y = rnd.uniform(y0, y1)
            t = (y - y0) / max(1, y1 - y0)
            spread = refl_w * (0.35 + t * 1.2)
            x = refl_x + rnd.gauss(0, spread * 0.45)
            L = rnd.uniform(6, 26) * (0.4 + t)
            out.append(bstroke(x, y, rnd.uniform(-2, 2), L, rnd.uniform(0.6, 1.8) * (0.5 + t), refl_col, rnd.uniform(0.45, 0.95)))
    return "".join(out)


def foliage_mass(D, prims, look, seed, density=1.0, size=(4, 9), op=(0.55, 0.95), leafy=True, holes=None, hole_n=0):
    """A tree crown / bush painted in clustered leaf dabs, lit by `look` (gives clumps with lit tops and dark
    undersides); optional sky holes."""
    rnd = random.Random(seed)
    xs, ys = [], []
    for p in prims:
        r = max(p[3], p[4])
        xs += [p[1] - r, p[1] + r]
        ys += [p[2] - r, p[2] + r]
    box = (min(xs), min(ys), max(xs), max(ys))
    area = (box[2] - box[0]) * (box[3] - box[1])
    out = []
    for pas, (k, sz) in enumerate(((0.012, (size[0] * 1.8, size[1] * 2.2)), (0.035, size), (0.02, (size[0] * 0.6, size[1] * 0.7)))):
        for _ in range(int(area * k * density)):
            x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
            s = surf(prims, x, y)
            if s is None:
                continue
            nrm = s[0]
            ex = 0.08 * pas
            col = look.color(nrm, rnd, ex - (0.1 if pas == 0 else 0))
            o = rnd.uniform(*op) * min(1.0, nrm[2] * 3 + 0.25)
            r = rnd.uniform(*sz)
            if leafy:
                out.append(dab(x, y, r, col, o, rnd, 0.55))
            else:
                out.append(dab(x, y, r, col, o, rnd, 0.8))
    if holes and hole_n:
        for _ in range(hole_n):
            x, y = rnd.uniform(box[0] + 10, box[2] - 10), rnd.uniform(box[1] + 10, box[3] - 10)
            s = surf(prims, x, y)
            if s is None or s[0][2] < 0.5:
                continue
            out.append(dab(x, y, rnd.uniform(1.5, 4), holes, rnd.uniform(0.6, 0.9), rnd, 0.7))
    return "".join(out)


def brushwork(seed, box, cols, n, L=(10, 30), W=(1, 3), op=(0.2, 0.5), angle=0, jit=10, poly=None):
    """Loose strokes of given colours in a box (ground texture, rock streaks, hair, grass beds)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if poly is not None and not _inpoly(poly, x, y):
            continue
        a = angle(x, y) if callable(angle) else angle
        out.append(bstroke(x, y, a + rnd.uniform(-jit, jit), rnd.uniform(*L), rnd.uniform(*W), rnd.choice(cols), rnd.uniform(*op), rnd.uniform(-2, 2)))
    return "".join(out)


def hair_strands(pts, n, spread, seed, cols, w=(0.8, 2.2), op=(0.35, 0.85), taper_end=True, jitter_amt=None):
    """Flowing strands (manes, tails, hair, smoke): many tapered curves that follow a guide path, fanned by `spread`."""
    rnd = random.Random(seed)
    out = []
    guide = resample(pts, 6, closed=False)
    ns = []
    for i in range(len(guide)):
        a, b = guide[max(0, i - 1)], guide[min(len(guide) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ns.append((-dy / L, dx / L))
    m = len(guide)
    for k in range(n):
        off = rnd.uniform(-1, 1)
        ph = rnd.uniform(0, 6.28)
        fr = rnd.uniform(0.6, 4.0)
        amp = rnd.uniform(0, 0.25)
        start = rnd.uniform(0, 0.35)
        end = rnd.uniform(0.65, 1.0)
        i0, i1 = int(start * (m - 1)), max(int(start * (m - 1)) + 2, int(end * (m - 1)))
        sp = spread if not callable(spread) else None
        line = []
        for i in range(i0, min(i1, m)):
            t = i / max(1, m - 1)
            s_ = spread(t) if callable(spread) else spread
            o = (off + amp * math.sin(ph + fr * t * 6.28)) * s_
            line.append((guide[i][0] + ns[i][0] * o, guide[i][1] + ns[i][1] * o))
        if len(line) < 2:
            continue
        ww = rnd.uniform(*w)
        out.append(taper(line, ww, 0.2 if taper_end else ww, rnd.choice(cols), rnd.uniform(*op)))
    return "".join(out)


def title_plate(D, x, y, s, font, size, pal="gold", ls=0, max_w=470, shadow="#0A0A14", sop=0.55, glow_col=None, seed=1):
    """Hero lettering that stays crisp under the varnish: soft dark halo for legibility, deboss, gilt face."""
    fs = fit_size(s, font, size, max_w, ls)
    out = []
    if glow_col:
        W = measure(s, font, fs, ls)
        out.append(halo(D, x, y - fs * 0.35, W * 0.62, glow_col, 0.55, ry=fs * 1.05, mid=0.55))
    out.append(gilt(D, x, y, s, font, fs, ls, max_w, deboss=shadow, dop=sop, pal=pal, wear=False, seed=seed))
    return "".join(out)


def shadow_text(x, y, s, font, size, fill, ls=0, max_w=460, anchor="middle", sh="#000000", sop=0.45, sdx=1.2, sdy=1.8, op=None):
    """Fitted text with a soft offset shadow for legibility on painted ground."""
    fs = fit_size(s, font, size, max_w, ls)
    return (tx(x + sdx, y + sdy, s, font, fs, sh, ls, max_w, anchor, op=sop) + tx(x, y, s, font, fs, fill, ls, max_w, anchor, op=op))


def limb(joints, cap=0.6):
    """Leg / arm outline from a joint chain [(x, y, width), ...]: returns (outline points, capsule volumes)."""
    n = len(joints)
    left, right, prims = [], [], []
    for i, (x, y, w) in enumerate(joints):
        a = joints[max(0, i - 1)]
        b = joints[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    for (x1, y1, w1), (x2, y2, w2) in zip(joints, joints[1:]):
        prims.append(C(x1, y1, x2, y2, w1 / 2, w2 / 2))
    x, y, w = joints[-1]
    px, py, _ = joints[-2]
    dx, dy = x - px, y - py
    L = math.hypot(dx, dy) or 1
    tip = (x + dx / L * w * cap, y + dy / L * w * cap)
    x, y, w = joints[0]
    px, py, _ = joints[1]
    dx, dy = x - px, y - py
    L = math.hypot(dx, dy) or 1
    top = (x + dx / L * w * 0.4, y + dy / L * w * 0.4)
    return left + [tip] + right[::-1] + [top], prims


def xf(pts, ox, oy, s=1.0, ang=0.0, flip=False):
    """Transform local points: optional mirror, scale, rotate (deg), translate."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        if flip:
            x = -x
        x, y = x * s, y * s
        out.append((ox + x * ca - y * sa, oy + x * sa + y * ca))
    return out


def feather_g(D, base, ang, L, w, look, seed, asym=0.35, curve=0.08, light_t=0.8, dark_t=0.3, shaft=True, barbs=6,
              edge_col=None, tip_round=0.5, op=1.0):
    """One flight / covert feather: curved vane with a darker shadowed base, a lit tip, barb strokes and a shaft."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bx, by = base
    pts_l, pts_r, axis = [], [], []
    m = 6
    for i in range(m + 1):
        t = i / m
        bend = curve * L * math.sin(t * math.pi * 0.9)
        cx_, cy_ = bx + ux * L * t + nx * bend, by + uy * L * t + ny * bend
        axis.append((cx_, cy_))
        prof = math.sin(math.pi * min(1, t * 1.08 + 0.04)) ** tip_round if t < 0.96 else 0.12
        prof = max(0.18, prof) if t > 0.05 else 0.25
        pts_l.append((cx_ + nx * w * prof * (1 - asym), cy_ + ny * w * prof * (1 - asym)))
        pts_r.append((cx_ - nx * w * prof * (1 + asym * 0.4), cy_ - ny * w * prof * (1 + asym * 0.4)))
    tip = (bx + ux * L * 1.03 + nx * curve * L * 0.15, by + uy * L * 1.03 + ny * curve * L * 0.15)
    pts = pts_l[1:] + [tip] + pts_r[::-1][:-1]
    d = smooth_closed(pts)
    vv = rnd.uniform(-0.06, 0.06)
    c_dark = ramp(look.cols, dark_t + vv + rnd.uniform(-0.04, 0.04))
    c_lit = ramp(look.cols, light_t + vv + rnd.uniform(-0.05, 0.03))
    g = D.lin([(0, c_dark), (0.55, mix(c_dark, c_lit, 0.75)), (1, c_lit)], round(bx, 1), round(by, 1), round(tip[0], 1), round(tip[1], 1), "userSpaceOnUse")
    o = f' opacity="{op}"' if op < 1 else ""
    out = [f'<g{o}><path d="{d}" fill="{g}"/>']
    if barbs:
        segs = []
        for k in range(barbs):
            t = rnd.uniform(0.15, 0.95)
            cx_, cy_ = axis[int(t * m)]
            side = rnd.choice((-1, 1))
            ww = w * (0.6 if side > 0 else 0.9)
            segs.append(f'M{cx_:.1f} {cy_:.1f}l{(nx * side - ux * 0.5) * ww:.1f} {(ny * side - uy * 0.5) * ww:.1f}')
        bc = ramp(look.cols, min(1, light_t + 0.08)) if rnd.random() < 0.5 else ramp(look.cols, max(0, dark_t + 0.05))
        out.append(f'<path d="{"".join(segs)}" stroke="{bc}" stroke-width="{max(0.6, w * 0.09):.1f}" stroke-linecap="round" opacity="0.5"/>')
    if shaft:
        sc = ramp(look.cols, min(1.0, light_t + 0.1))
        mx_, my_ = axis[m // 2]
        ex_, ey_ = axis[-2]
        out.append(f'<path d="M{bx:.1f} {by:.1f}Q{mx_:.1f} {my_:.1f} {ex_:.1f} {ey_:.1f}" stroke="{sc}" stroke-width="{max(0.7, w * 0.11):.1f}" fill="none" opacity="0.6"/>')
    ec = edge_col or ramp(look.cols, max(0, dark_t - 0.18))
    out.append(f'<path d="{smooth_open(pts_r[2:] + [tip])}" fill="none" stroke="{ec}" stroke-width="{max(0.7, w * 0.09):.1f}" opacity="0.28"/>')
    out.append("</g>")
    return "".join(out)


def wing_g(D, lead, n_arm, look, seed, prim=(10, (205, 255), (115, 70)), sec=(13, (165, 212), (75, 108)), scale=1.0,
           rows=((0.5, 0.22, 0.4, 0.66), (0.28, 0.2, 0.52, 0.78), (0.14, 0.17, 0.64, 0.9)), feather_w=1.0, dark=0.0,
           marg_n=26, shade_dir=(-1.0, 0.4), shade_amt=0.2, fingers=4, bone=True):
    """A bird-anatomy wing. lead = leading-edge points from the root (shoulder) to the wingtip; the first n_arm
    points are the arm (secondaries hang from it), the rest the hand (primaries). prim/sec = (count, (angle at
    start, angle at end), (length at start, length at end)). rows = covert rows (length factor, width factor,
    dark_t, light_t). Feathers away from the light (shade_dir) are painted darker; the outer `fingers` primaries
    are slotted like an eagle's."""
    rnd = random.Random(seed)
    curve = resample(lead, 3, closed=False)
    arm_len = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(lead[:n_arm], lead[1:n_arm]))
    acc, split = 0.0, len(curve) - 1
    for i in range(1, len(curve)):
        acc += math.hypot(curve[i][0] - curve[i - 1][0], curve[i][1] - curve[i - 1][1])
        if acc >= arm_len:
            split = i
            break
    arm, hand = curve[:split + 1], curve[split:]
    cxw = sum(p[0] for p in curve) / len(curve)
    cyw = sum(p[1] for p in curve) / len(curve)
    sdl = math.hypot(*shade_dir) or 1
    sdx, sdy = shade_dir[0] / sdl, shade_dir[1] / sdl
    ext = max(math.hypot(p[0] - cxw, p[1] - cyw) for p in curve) + 60 * scale

    def shade(base, ang, L):
        a = math.radians(ang)
        tx_, ty_ = base[0] + math.cos(a) * L * 0.7, base[1] + math.sin(a) * L * 0.7
        return shade_amt * max(-0.6, min(1.0, ((tx_ - cxw) * sdx + (ty_ - cyw) * sdy) / ext))

    def at(seq, t):
        return seq[min(len(seq) - 1, int(t * (len(seq) - 1)))]
    lerp = lambda a, b, t: a + (b - a) * t
    out = []
    pn, (pa0, pa1), (pl0, pl1) = prim
    for j in range(pn - 1, -1, -1):
        t = j / max(1, pn - 1)
        b = at(hand, 0.06 + t * 0.92)
        L = lerp(pl0, pl1, t) * scale * rnd.uniform(0.95, 1.05)
        ang = lerp(pa0, pa1, t) + rnd.uniform(-2.5, 2.5)
        dd = dark + shade(b, ang, L)
        finger = j >= pn - fingers
        out.append(feather_g(D, b, ang, L, L * (0.085 if finger else 0.105) * feather_w, look, seed + 100 + j,
                             asym=0.45, curve=0.07 if finger else 0.05, light_t=0.92 - dd, dark_t=0.42 - dd, barbs=5,
                             tip_round=0.35 if finger else 0.55))
    sn, (sa0, sa1), (sl0, sl1) = sec
    for j in range(sn):
        t = j / max(1, sn - 1)
        b = at(arm, 0.04 + t * 0.94)
        L = lerp(sl0, sl1, t) * scale * rnd.uniform(0.95, 1.05)
        ang = lerp(sa0, sa1, t) + rnd.uniform(-2.5, 2.5)
        dd = dark + shade(b, ang, L)
        out.append(feather_g(D, b, ang, L, L * 0.13 * feather_w, look, seed + 200 + j,
                             asym=0.2, curve=-0.05, light_t=0.9 - dd, dark_t=0.4 - dd, barbs=4))
    whole = arm + hand[1:]
    fa = len(arm) / len(whole)
    # greater coverts: one row of broad feathers over the flight-feather bases
    lf, wf, dt, lt_ = rows[0]
    cnt = int((sn + pn) * 0.9)
    edge_pts = []
    for j in range(cnt):
        t = j / max(1, cnt - 1)
        b = at(whole, 0.02 + t * 0.9)
        if t > fa:
            tt = (t - fa) / max(0.01, 1 - fa)
            ang = lerp(pa0, pa1, tt) - 4
            L = lerp(pl0, pl1, tt) * lf * scale * 0.8
        else:
            tt = t / max(0.01, fa)
            ang = lerp(sa0, sa1, tt) + 3
            L = lerp(sl0, sl1, tt) * lf * scale
        L *= rnd.uniform(0.92, 1.08)
        dd = dark + shade(b, ang, L) * 0.7
        out.append(feather_g(D, b, ang + rnd.uniform(-3, 3), L, L * wf * feather_w * 1.25, look, seed + 300 + j,
                             asym=0.25, curve=-0.04, light_t=lt_ - dd, dark_t=dt - dd, barbs=2, shaft=True, tip_round=0.8))
        a_ = math.radians(ang)
        k = rows[1][0] / lf
        edge_pts.append((b[0] + math.cos(a_) * L * k, b[1] + math.sin(a_) * L * k))
    # lesser + median coverts: a smooth, modelled mass along the arm with a scalloped trailing edge
    lead_pts = whole[::3]
    mass = lead_pts + edge_pts[::-1][::2]
    pr = []
    for j in range(0, len(edge_pts), 2):
        t = j / max(1, len(edge_pts) - 1)
        b = at(whole, 0.02 + t * 0.9)
        e = edge_pts[j]
        pr.append(C(b[0], b[1], e[0] * 0.8 + b[0] * 0.2, e[1] * 0.8 + b[1] * 0.2, 9 * scale, 6 * scale))
    dkl = Look([dk(c, dark * 0.9) for c in look.cols], key=look.key, amb=0.25, wrap=0.6, rim=look.rim, jit=0.03)
    out.append(form(D, mass, pr, dkl, seed + 700, flow=lambda x, y, n, p: prim_axis(p), flow_jit=8, edge_w=1.2, edge_op=0.35,
                    edge_col=ramp(look.cols, 0.3 - dark), passes=((60, (8, 16), (2, 4), (0.3, 0.55)), (220, (4, 9), (1, 2), (0.4, 0.75)))))
    # scallops: small overlapping feather tips painted into the mass, in rows
    for r_i in range(3):
        k = 0.3 + r_i * 0.25
        for j in range(0, len(edge_pts), 1):
            t = j / max(1, len(edge_pts) - 1)
            b = at(whole, 0.02 + t * 0.9)
            e = edge_pts[j]
            x_, y_ = b[0] + (e[0] - b[0]) * k, b[1] + (e[1] - b[1]) * k
            ang = math.degrees(math.atan2(e[1] - b[1], e[0] - b[0]))
            r_ = (4 + r_i * 1.6) * scale
            a_ = math.radians(ang)
            ux, uy = math.cos(a_), math.sin(a_)
            nx, ny = -uy, ux
            c = ramp(dkl.cols, 0.3 + r_i * 0.08 - shade(b, ang, 40) * 0.5)
            out.append(f'<path d="M{x_ - nx * r_:.1f} {y_ - ny * r_:.1f}Q{x_ + ux * r_ * 1.4:.1f} {y_ + uy * r_ * 1.4:.1f} {x_ + nx * r_:.1f} {y_ + ny * r_:.1f}" '
                       f'stroke="{c}" stroke-width="{0.9 * scale:.1f}" fill="none" opacity="0.3"/>')
    if bone:
        out.append(taper(curve[: int(len(curve) * 0.85)], 6 * scale, 1.5 * scale, ramp(look.cols, 1.0 - dark), 0.7))
    return "".join(out)


def horse_g(D, look, seed, mane_cols=None, tail_cols=None, hoof=("#9A92A6", "#4A4456", "#22202A"), far_dark=0.18):
    """A flying horse in local coordinates (facing right; buttock to chest ~215 units).
    Anatomy: deep chest, sloping shoulder, arched crest, wedge head with a big round jaw, massive haunch,
    slim legs with knees, hocks, fetlocks and hooves (flying-gallop pose: near foreleg folded high, far
    foreleg reaching, both hind legs stretched back). Returns (far_legs, near_legs, body) SVG strings in local
    coordinates: paint far legs, (far wing), near legs, body, then mane / near wing."""
    rnd = random.Random(seed)
    far_look = Look([dk(c, far_dark) for c in look.cols], key=look.key, amb=look.amb, wrap=look.wrap,
                    rim=look.rim, bounce=look.bounce, jit=look.jit)
    acc = ramp(look.cols, 0.18)
    hl_ = ramp(look.cols, 1.0)

    def leg(joints, lk, s_, top_hidden=2):
        pts, prims = limb(joints)
        ytop = joints[top_hidden][1]
        x_top = joints[top_hidden]

        def mask(x, y):
            return math.hypot(x - joints[0][0], y - joints[0][1]) > math.hypot(x_top[0] - joints[0][0], x_top[1] - joints[0][1]) * 0.8
        f = form(D, pts, prims, lk, s_, passes=((50, (12, 24), (3, 6), (0.35, 0.6)), (190, (5, 12), (1.2, 2.6), (0.45, 0.8))),
                 flow="axis", flow_jit=6, edge_w=1.7, edge_op=0.65, edge_col=acc, edge_mask=mask)
        (x2, y2, w2), (x1, y1, w1) = joints[-1], joints[-2]
        a = math.atan2(y2 - y1, x2 - x1)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        hw, hl = w2 * 0.6, w2 * 1.25
        hp = [(x2 + nx * hw * 0.8, y2 + ny * hw * 0.8), (x2 + ux * hl + nx * hw * 1.2, y2 + uy * hl + ny * hw * 1.2),
              (x2 + ux * hl * 1.1 - nx * hw * 1.0, y2 + uy * hl * 1.1 - ny * hw * 1.0), (x2 - nx * hw * 0.8, y2 - ny * hw * 0.8)]
        hd = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in jitter(hp, s_, 0.3)) + "Z"
        g = D.lin([(0, hoof[0]), (0.45, hoof[1]), (1, hoof[2])], 0, 0, 0.3, 1)
        f += f'<path d="{hd}" fill="{g}" stroke="{hoof[2]}" stroke-width="0.8" stroke-linejoin="round"/>'
        f += f'<path d="M{hp[0][0]:.1f} {hp[0][1]:.1f}L{hp[3][0]:.1f} {hp[3][1]:.1f}" stroke="{ramp(lk.cols, 0.75)}" stroke-width="2.2" stroke-linecap="round" opacity="0.7"/>'
        return f
    far = [leg([(184, 52, 30), (192, 76, 23), (220, 98, 15), (226, 104, 17), (250, 112, 10), (266, 116, 12.5), (278, 122, 9)], far_look, seed + 1),
           leg([(40, 48, 36), (44, 74, 28), (22, 88, 19), (2, 96, 13.5), (-6, 99, 15.5), (-34, 104, 10), (-50, 108, 12.5), (-62, 113, 9)], far_look, seed + 2)]
    # near lower legs (cannon, fetlock, pastern, hoof) start inside the knee / hock of the body mass
    near = [leg([(246, 86, 18), (254, 92, 17.5), (250, 112, 10.5), (243, 124, 13), (248, 136, 9.5)], look, seed + 4, top_hidden=1),
            leg([(4, 96, 18), (-8, 100, 17), (-36, 107, 10.5), (-52, 111, 13), (-64, 117, 9.5)], look, seed + 5, top_hidden=1)]
    # one continuous mass: torso, neck and head, plus the near forearm (to the knee) and near thigh/gaskin (to the hock)
    body_pts = [(14, 2), (30, -8), (48, -8), (70, -2), (96, 6), (124, 6), (144, 0), (158, -10), (172, -34), (190, -58),
                (210, -78), (228, -92), (242, -99), (254, -95), (264, -83), (274, -65), (283, -47), (290, -35), (295, -26),
                (292, -16), (281, -12), (269, -15), (258, -24), (250, -38), (246, -53), (238, -62), (230, -45), (224, -22),
                (222, 2), (226, 26), (224, 46), (230, 60), (242, 72), (254, 82), (259, 90), (252, 98), (236, 94), (218, 88),
                (202, 84), (184, 86), (152, 92), (118, 90), (92, 83), (70, 79), (56, 85), (38, 93), (20, 99), (4, 105),
                (-10, 102), (-14, 94), (-6, 82), (-2, 66), (-6, 50), (-6, 34), (2, 18)]
    prims = [E(116, 44, 72, 42, 3, 1.0, 1.0), E(166, 46, 40, 42, 0, 1.0, 1.0), E(204, 36, 26, 34, -12, 1.05, 1.0),
             E(186, 12, 22, 42, -30, 1.1, 0.8), E(38, 28, 44, 38, 10, 1.1, 1.0), C(46, 66, -4, 96, 22, 10, 1.15),
             C(206, 72, 252, 88, 14, 9, 1.15), C(192, 8, 236, -78, 31, 16, 1.0), C(180, -24, 226, -88, 13, 10, 1.05),
             E(256, -48, 17, 19, 30, 1.2, 1.0), C(256, -86, 290, -28, 12, 9, 1.15), E(289, -22, 10.5, 9.5, 0, 1.2, 1.0)]

    def hair(x, y, nrm, p):
        if p[0] == "c":
            return prim_axis(p)
        return 180 + 12 * nrm[1] if p[3] > 30 else prim_axis(p)
    body = [form(D, body_pts, prims, look, seed + 3, flow=hair, flow_jit=10, edge_w=2.0, edge_op=0.6, edge_col=acc,
                 passes=((35, (18, 36), (5, 9), (0.25, 0.45)), (220, (8, 18), (1.8, 3.8), (0.3, 0.6)), (90, (4, 9), (1, 2.2), (0.35, 0.65))))]
    # anatomy accents: scapula, triceps, ribs, point of hip, stifle/gaskin, jaw, cheek bone; lit crest and face
    for pts, w, op, col in (([(164, -6), (180, 20), (198, 44)], 2.4, 0.22, acc),
                            ([(202, 56), (196, 70), (200, 82)], 2.0, 0.25, acc),
                            ([(132, 46), (136, 62), (138, 80)], 1.6, 0.1, acc), ([(114, 50), (117, 66), (118, 82)], 1.6, 0.08, acc),
                            ([(22, 4), (46, 14), (62, 40), (62, 66)], 2.2, 0.2, acc),
                            ([(52, 80), (34, 88), (16, 96)], 1.8, 0.22, acc),
                            ([(242, -56), (254, -40), (268, -30)], 1.6, 0.35, acc),
                            ([(250, -80), (262, -68), (276, -58)], 1.3, 0.22, acc),
                            ([(156, -8), (174, -38), (196, -66), (220, -88)], 2.6, 0.38, hl_),
                            ([(264, -88), (274, -70), (284, -52), (292, -36)], 2.2, 0.5, hl_),
                            ([(208, 30), (218, 44)], 3, 0.35, hl_), ([(214, 60), (240, 76)], 2.4, 0.4, hl_)):
        body.append(taper(resample(pts, 4, closed=False), w, w * 0.3, col, op))
    # eye: dark almond under a bony brow, set on the side of the head; a small wet highlight
    ex, ey = 257, -74
    eye = smooth_closed([(ex - 5.5, ey + 1.2), (ex - 1, ey - 2.6), (ex + 4.5, ey - 1.6), (ex + 5.8, ey + 0.8), (ex + 1, ey + 2.6)])
    body.append(f'<path d="{smooth_closed([(ex - 8, ey + 2), (ex - 2, ey - 5), (ex + 7, ey - 3.5), (ex + 8, ey + 3), (ex, ey + 5.5)])}" fill="{ramp(look.cols, 0.3)}" opacity="0.55"/>')
    body.append(f'<path d="{smooth_open([(ex - 9, ey - 3), (ex - 1, ey - 8), (ex + 8, ey - 6)])}" stroke="{hl_}" stroke-width="2.6" fill="none" opacity="0.75"/>')
    body.append(f'<path d="{eye}" fill="#16121E"/>')
    body.append(f'<path d="M{ex + 0.5:.1f} {ey - 1.6:.1f} q 2 -0.6 3.2 0.4" stroke="#C8C4DC" stroke-width="1.1" fill="none" opacity="0.8"/>')
    # nostril (a flared comma), lips, chin groove
    body.append(f'<path d="{smooth_open([(286, -35), (290, -31), (289.5, -26), (286.5, -27.5)])}" stroke="{ramp(look.cols, 0.15)}" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0.6"/>')
    body.append(f'<path d="M284 -17.5 q 5 -0.5 9 -2.5" stroke="{ramp(look.cols, 0.2)}" stroke-width="1.1" fill="none" opacity="0.4"/>')
    # ears: far ear behind, near ear pricked forward; inner hollow shadowed
    for (bx, by, tipx, tipy, s_, dkk) in ((240, -95, 243, -121, 1, 0.12), (250, -96, 259, -123, 2, 0.0)):
        ep = [(bx - 7, by + 4), (bx - 6.5, by - 7), (tipx - 1.5, tipy + 3), (tipx, tipy), (tipx + 2.5, tipy + 4), (bx + 7, by - 8), (bx + 7, by + 4)]
        lkk = Look([dk(c, dkk) for c in look.cols], key=look.key, amb=look.amb, wrap=look.wrap, rim=look.rim, jit=0.03)
        body.append(form(D, ep, [E(bx + 1, by - 10, 7.5, 16, -12, 1, 1)], lkk, seed + 30 + s_, edge_w=1.0, edge_op=0.3, edge_col=acc,
                         passes=((300, (4, 8), (1, 2), (0.5, 0.8)),)))
        body.append(taper([(bx + 1.5, by - 1), ((bx + tipx) / 2 + 1.5, (by + tipy) / 2), (tipx + 0.5, tipy + 6)], 4.0, 0.8, ramp(look.cols, 0.5), 0.35))
    return "".join(far), "".join(near), "".join(body)


def mane_g(crest, seed, cols, length=(26, 40), wind=(-1.0, 0.15), n_locks=11, strands=7, look=None, D=None):
    """A mane as flowing locks rooted along the crest, streaming with the wind. Each lock is a soft painted
    ribbon (several overlapping translucent tapers, lit on top, shadowed beneath) with a few fine strands."""
    rnd = random.Random(seed)
    guide = resample(crest, 4, closed=False)
    out = []
    for i in range(n_locks):
        t = max(0, min(1, (i + rnd.uniform(-0.3, 0.3)) / max(1, n_locks - 1)))
        bx, by = guide[int(t * (len(guide) - 1))]
        L = rnd.uniform(*length) * (0.7 + 0.5 * math.sin(math.pi * t))
        ph = rnd.uniform(0, 6.28)
        pts = []
        for k in range(7):
            u = k / 6
            wav = math.sin(ph + u * 5) * L * 0.07 * u
            pts.append((bx + wind[0] * L * u, by + wind[1] * L * u - 7 * math.sin(u * math.pi) + wav))
        line = resample(pts, 4, closed=False)
        W = rnd.uniform(7, 11)
        out.append(taper(line, W, 1.0, cols[3], 0.55))                          # shadow side of the lock
        out.append(taper([(x, y - W * 0.18) for x, y in line], W * 0.75, 0.6, cols[i % 3 if i % 3 != 1 else 2], 0.8))
        out.append(taper([(x, y - W * 0.3) for x, y in line[: int(len(line) * 0.8)]], W * 0.3, 0.3, cols[0], 0.75))  # sheen
        out.append(hair_strands(pts, strands, 2.6, seed + i, [cols[0], cols[2], cols[3]], w=(0.5, 1.2), op=(0.3, 0.7)))
    return "".join(out)


def centerline(x, base, top, seed, lean=0.0, wob=0.06, n=12):
    rnd = random.Random(seed)
    h = base - top
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x + lean * h * t + (rnd.uniform(-1, 1) * wob * h * 0.3 if 0 < i < n else 0), base - h * t))
    return pts


def trunk_g(D, x, base, top, w0, w1, seed, look, lean=0.0, wob=0.05, roots=3, root_w=1.6, knots=2, bark=None,
            edge_light=None, crevices=26, branch_stubs=()):
    """A Rackham-like old trunk: wavering, tapered, buttress roots flaring into the ground, bark crevices running
    with the grain, knot holes; modelled by `look`. branch_stubs = [(t, side, length, angle)]."""
    rnd = random.Random(seed)
    cl = centerline(x, base, top, seed, lean, wob)
    n = len(cl)
    left, right, prims = [], [], []
    for i, (cx, cy) in enumerate(cl):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t ** 0.8
        if t < 0.18:
            w *= 1 + (root_w - 1) * (1 - t / 0.18) ** 2
        w *= rnd.uniform(0.9, 1.1) * (1 + 0.08 * math.sin(t * 17 + seed))
        left.append((cx - w / 2 * rnd.uniform(0.95, 1.05), cy))
        right.append((cx + w / 2 * rnd.uniform(0.95, 1.05), cy))
    for (ax, ay), (bx, by) in zip(cl, cl[1:]):
        t = (base - ay) / max(1, base - top)
        prims.append(C(ax, ay, bx, by, (w0 + (w1 - w0) * t) / 2 * 1.05))
    # outline: top-left, down the left side, across the flared root base, up the right side
    outline = list(reversed(left)) + [(x - w0 * root_w * 0.72, base + 6), (x + w0 * root_w * 0.72, base + 6)] + right
    f = form(D, outline, prims, look, seed + 1, flow=lambda x_, y_, nrm, p: prim_axis(p) + rnd.uniform(-6, 6), flow_jit=5,
             edge_w=2.0, edge_op=0.5, edge_col=ramp(look.cols, 0.0), edge_light=edge_light,
             passes=((40, (20, 46), (3, 6), (0.3, 0.55)), (160, (10, 26), (1.2, 2.6), (0.35, 0.7))))
    out = [f]
    # crevices: dark furrows following the grain, a lit lip beside each
    cid = D.clip(f'<path d="{smooth_closed(outline)}"/>')
    cr = []
    dkc = bark or ramp(look.cols, 0.0)
    ltc = ramp(look.cols, 0.85)
    for _ in range(crevices):
        t0 = rnd.uniform(0, 0.9)
        L = rnd.uniform(0.08, 0.3)
        u = rnd.uniform(-0.42, 0.42)
        line = []
        for k in range(6):
            t = min(1, t0 + L * k / 5)
            i = t * (n - 1)
            i0 = min(n - 2, int(i))
            fr = i - i0
            cx = cl[i0][0] + (cl[i0 + 1][0] - cl[i0][0]) * fr
            cy = cl[i0][1] + (cl[i0 + 1][1] - cl[i0][1]) * fr
            w = (w0 + (w1 - w0) * t) * (1 + (root_w - 1) * max(0, 1 - t / 0.18) ** 2)
            line.append((cx + u * w + math.sin(k + u * 9) * 1.5, cy))
        ww = rnd.uniform(1.2, 3.2) * (1 - abs(u))
        cr.append(taper(line, ww, 0.4, dkc, rnd.uniform(0.35, 0.7)))
        cr.append(taper([(px + 1.6, py) for px, py in line], ww * 0.5, 0.3, ltc, rnd.uniform(0.12, 0.3)))
    for _ in range(knots):
        t = rnd.uniform(0.25, 0.75)
        i = int(t * (n - 1))
        cx, cy = cl[i]
        w = w0 + (w1 - w0) * t
        kx = cx + rnd.uniform(-0.2, 0.2) * w
        r = w * rnd.uniform(0.08, 0.14)
        cr.append(f'<path d="{blob(kx, cy, r * 1.5, r * 2.3, rnd.randint(0, 999), 0.2)}" fill="{ramp(look.cols, 0.55)}" opacity="0.6"/>')
        cr.append(f'<path d="{blob(kx, cy, r * 0.8, r * 1.4, rnd.randint(0, 999), 0.2)}" fill="{dkc}" opacity="0.85"/>')
    out.append(f'<g {cid}>{"".join(cr)}</g>')
    return "".join(out)


def light_shafts(D, src, targets, col, op=0.22, seed=1):
    """God-rays: soft translucent wedges from a source point to spans on the ground [(x0, x1, y), ...]."""
    out = []
    for (x0, x1, y) in targets:
        g = D.lin([(0, col, op), (0.6, col, op * 0.5), (1, col, 0)], src[0], src[1], (x0 + x1) / 2, y, "userSpaceOnUse")
        out.append(f'<path d="M{src[0] - 4:.1f} {src[1]:.1f}L{src[0] + 4:.1f} {src[1]:.1f}L{x1:.1f} {y:.1f}L{x0:.1f} {y:.1f}Z" fill="{g}"/>')
    return "".join(out)


def mist_band(D, y, h, col, op=0.6, x0=-40, x1=640, seed=1, n=10):
    """A low drifting band of mist: overlapping very soft ellipses."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        cx = rnd.uniform(x0, x1)
        out.append(halo(D, cx, y + rnd.uniform(-h * 0.3, h * 0.3), rnd.uniform(90, 200), col, op * rnd.uniform(0.5, 1), ry=h * rnd.uniform(0.5, 1), mid=0.5))
    return "".join(out)


def fern_g(x, y, L, ang, seed, cols, n=11, curl=0.25, w=1.0):
    """A painted fern frond: a curving rachis with paired tapering pinnae."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = []
    for i in range(n + 1):
        t = i / n
        aa = a + curl * t * t * 2
        pts.append((x + math.cos(aa) * L * t, y + math.sin(aa) * L * t))
    out = [taper(pts, 2.2 * w, 0.6, cols[2], 0.9)]
    for i in range(1, n):
        t = i / n
        px, py = pts[i]
        dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        base_a = math.atan2(dy, dx)
        pl = L * 0.32 * math.sin(math.pi * (0.15 + t * 0.85)) * (1 - t * 0.4)
        for side in (-1, 1):
            pa = base_a + side * math.radians(62)
            tip = (px + math.cos(pa) * pl, py + math.sin(pa) * pl)
            mid = (px + math.cos(pa + side * 0.15) * pl * 0.5, py + math.sin(pa + side * 0.15) * pl * 0.5)
            out.append(taper([(px, py), mid, tip], pl * 0.28 * w, 0.4, rnd.choice(cols[:2]), rnd.uniform(0.7, 0.95)))
    return "".join(out)


def grass_tufts(seed, box, cols, n=60, h=(10, 26), w=(1.2, 2.6), lean=(-0.4, 0.4), op=(0.5, 0.95)):
    """Grass blades as tapered brush marks."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h)
        l = rnd.uniform(*lean)
        out.append(taper([(x, y), (x + l * hh * 0.4, y - hh * 0.5), (x + l * hh, y - hh)], rnd.uniform(*w), 0.2, rnd.choice(cols), rnd.uniform(*op)))
    return "".join(out)


# per-design painterly varnish (seed, edge, bristle, grain); every design gets its own seed
VARNISH = {}


def varnish(slug, seed, edge=3.0, bristle=0.5, grain=0.2, freq=0.05):
    VARNISH[slug] = dict(seed=seed, edge=edge, bristle=bristle, grain=grain, freq=freq)


# =====================================================================================================
# 1. PEGASUS: a white winged stallion rising over the dawn sea, toward the last stars
# =====================================================================================================
@design("pegasus")
def pegasus_g():
    D = Doc2("pg")
    varnish("pegasus", 41, edge=2.6, bristle=0.45, grain=0.18)
    out = []
    HZ = 432
    stops = [(0, "#0E1238"), (0.22, "#25285E"), (0.45, "#5A4A84"), (0.62, "#A0638A"), (0.76, "#E48C78"), (0.87, "#F8BE84"), (1, "#FFE2A8")]
    out.append(sky_paint(D, stops, 4101, 0, HZ, n=320, L=(70, 220), W=(4, 13), op=(0.08, 0.26)))
    out.append(stars_field(4102, (20, 10, 580, 170), 70, r=(0.6, 1.6), op=(0.4, 0.95)))
    for sx, sy, r in ((92, 66, 7), (500, 52, 6), (548, 120, 4.5), (60, 150, 4)):
        out.append(halo(D, sx, sy, r * 3, "#FFF4D8", 0.5) + sparkle(sx, sy, r, "#FFFBEA", 0.95))
    # sun just under the horizon at right: wide glow
    SX = 470
    out.append(halo(D, SX, HZ + 6, 300, "#FFD9A0", 0.65, ry=200))
    out.append(halo(D, SX, HZ + 4, 110, "#FFF6DC", 0.9, ry=70))
    # distant islands, hazy
    for pts, col in (([(-20, HZ), (-20, HZ - 26), (30, HZ - 40), (70, HZ - 52), (104, HZ - 44), (150, HZ - 30), (190, HZ - 14), (230, HZ)], "#9A7898"),
                     ([(250, HZ), (280, HZ - 10), (310, HZ - 16), (340, HZ - 8), (360, HZ)], "#C08E98")):
        line = rough(pts, 4111 + len(pts), 6, 3)
        out.append(f'<path d="{smooth_closed(line)}" fill="{col}" opacity="0.85"/>')
        out.append(brushwork(4115, bbox(line), [lt(col, 0.15), dk(col, 0.08)], 60, (8, 24), (1, 3), (0.2, 0.45), -4, 10, poly=line))
    # cloud banks lit from the sun at right
    clook = Look(["#4E3C6E", "#8A5A84", "#D08884", "#FBC498", "#FFF2DA"], key=(0.85, -0.35, 0.45), amb=0.1, wrap=0.45, jit=0.06)
    out.append(cloud(D, 120, 380, 300, 90, 4120, clook, n_puffs=18, density=1.0, size=(5, 13)))
    out.append(cloud(D, 560, 395, 180, 60, 4121, clook, n_puffs=10, density=1.0, size=(4, 10)))
    out.append(cloud(D, 330, 412, 170, 34, 4122, clook, n_puffs=9, density=1.0, size=(3, 8)))
    # sea with the sun path
    out.append(water_paint(D, HZ, 600, [(0, "#C48A90"), (0.25, "#7A5A82"), (0.7, "#3A3466"), (1, "#1E1E48")], 4130, n=520,
                           refl=True, refl_x=SX, refl_w=50, refl_col="#FFE4B0", glints=240))
    out.append(halo(D, SX, HZ + 40, 160, "#FFD8A0", 0.35, ry=40))
    # ---- the horse
    look = Look(["#2E2A5C", "#575190", "#9C94C4", "#E2D6E6", "#FFF0D8", "#FFFDF6"], key=(0.5, -0.55, 0.68), amb=0.0, wrap=0.25,
                rim=("#FFE0A0", (0.7, -0.7), 0.75), bounce=("#D8A8C0", 0.45), jit=0.02)
    ang, s, ox, oy = -6, 1.0, 166, 344
    ka = math.radians(-ang)   # light into the horse's local frame
    key = (look.key[0] * math.cos(ka) - look.key[1] * math.sin(ka), look.key[0] * math.sin(ka) + look.key[1] * math.cos(ka), look.key[2])
    lk = Look(look.cols, key=key, amb=look.amb, wrap=look.wrap, rim=look.rim, bounce=look.bounce, jit=look.jit)
    wl = Look([mix(c, '#FFF4E0', 0.12) for c in look.cols], key=key, amb=0.25, wrap=0.6, rim=look.rim, jit=0.03)
    far, near, body = horse_g(D, lk, 4140)
    out.append(halo(D, 330, 270, 250, '#FFF2DC', 0.3, ry=200))
    tr = f'transform="translate({ox} {oy}) rotate({ang}) scale({s})"'
    G = []
    # far wing: raised behind, peeking out ahead of the near wing (cooler, in shadow)
    G.append(wing_g(D, [(176, -14), (196, -62), (214, -110), (206, -156), (180, -200), (150, -228)], 3, wl, 4150,
                    prim=(11, (214, 250), (104, 70)), sec=(12, (170, 210), (66, 100)), scale=1.0, dark=0.24, marg_n=16,
                    rows=((0.6, 0.24, 0.4, 0.66), (0.5, 0.2, 0.52, 0.78), (0.14, 0.17, 0.64, 0.9)),
                    shade_dir=(-1, 0.6), shade_amt=0.15, bone=False))
    # tail: a painted mass streaming back, then loose strands
    tail = [(12, 4), (-8, 6), (-34, 14), (-60, 26), (-88, 30), (-118, 26)]
    tpr = [C(tail[i][0], tail[i][1], tail[i + 1][0], tail[i + 1][1], 6 + 3 * i, 6 + 3 * (i + 1)) for i in range(len(tail) - 1)]
    tl_pts = [(14, -3), (-8, 0), (-34, 4), (-62, 12), (-92, 14), (-124, 12), (-130, 30), (-110, 42), (-84, 44), (-56, 38), (-30, 26), (-6, 14), (10, 10)]
    G.append(form(D, tl_pts, tpr, Look([dk(c, 0.1) for c in lk.cols], key=key, amb=0.05, wrap=0.3, jit=0.05), 4159, flow=lambda x, y, n, p: 180 + 8 * math.sin(x * 0.05),
                  flow_jit=6, edge_w=1.2, edge_op=0.35, edge_col=ramp(lk.cols, 0.2), passes=((60, (14, 30), (2, 4), (0.3, 0.6)), (220, (8, 22), (0.8, 1.8), (0.4, 0.85)))))
    G.append(hair_strands(tail + [(-140, 34)], 46, lambda t: 6 + 22 * t, 4160, ["#B8B2D6", "#7A74A6", "#F2EEF8", "#FFFFFF", "#5A5488"], w=(0.8, 2.6), op=(0.4, 0.9)))
    G.append(far)
    G.append(near)
    G.append(body)
    # mane streaming back along the crest; forelock between the ears
    crest = [(240, -100), (226, -92), (208, -78), (190, -58), (174, -36), (160, -14)]
    G.append(mane_g(crest, 4161, ["#FFFDF6", "#C4BEE0", "#F6F0F4", "#9A94C4", "#E8DEEC"], length=(34, 52), wind=(-1.0, 0.3), n_locks=17, strands=3))
    G.append(hair_strands([(246, -101), (256, -97), (264, -88)], 12, 3, 4162, ["#FFFFFF", "#D8D2EA", "#9A94C0"], w=(0.8, 2.0)))
    # near wing: raised in the upstroke and sweeping back, the hand curling at the tip
    G.append(wing_g(D, [(160, -4), (174, -58), (182, -110), (164, -160), (128, -202), (86, -232)], 3, wl, 4170,
                    prim=(13, (196, 236), (128, 84)), sec=(16, (150, 192), (80, 128)), scale=1.0, marg_n=30, feather_w=1.15,
                    rows=((0.6, 0.24, 0.4, 0.66), (0.5, 0.2, 0.52, 0.78), (0.14, 0.17, 0.64, 0.9)),
                    shade_dir=(-1, 0.5), shade_amt=0.22))
    out.append(f'<g {tr}>{"".join(G)}</g>')
    # a few lifted feathers / sea spray drifting below
    rnd = random.Random(4180)
    for _ in range(3):
        fx, fy = rnd.uniform(140, 260), rnd.uniform(440, 470)
        out.append(feather_g(D, (fx, fy), rnd.uniform(-30, 30), 18, 3.5, wl, rnd.randint(0, 999), barbs=2))
    # lettering on the dark sea
    out.append(halo(D, 300, 512, 260, "#0E1032", 0.55, ry=60))
    out.append(title_plate(D, 300, 520, "PEGASUS", CINZEL, 60, pal="pale", ls=12, max_w=420, shadow="#0A0A24", sop=0.7))
    out.append(shadow_text(300, 548, "Born of sea-foam, bound for the stars.", SERIF_IT, 19, "#FFE8C4", max_w=440, sh="#0A0A24", sop=0.6))
    return D.render(out)


# =====================================================================================================
# 2. LITTLE RED RIDING HOOD: deep Rackham wood, a lit clearing ahead, the wolf watching from a trunk
# =====================================================================================================
def red_cloak_back(D, x, base, h, seed, rim="#FFC870"):
    """A child in a hooded red cloak seen from behind, walking away into the light (about 6 heads tall):
    pointed hood, cape flaring with the step, a basket on the left arm, white stockings and dark shoes."""
    k = h / 100.0
    P_ = lambda pts: [(x + px * k, base + py * k) for px, py in pts]
    out = []
    # legs and shoes (behind the cape hem): left leg planted, right leg pushing off, heel lifted
    for pts, w0, w1 in (([(-6, -22), (-7, -10), (-7.5, -2)], 6.5, 5.0), ([(6, -22), (8, -11), (11, -5)], 6.5, 5.0)):
        out.append(taper(P_(pts), w0 * k, w1 * k, "#E8DCCC", 1))
        out.append(taper(P_(pts), w0 * k * 0.45, w1 * k * 0.4, "#9A8A86", 0.55))
    out.append(f'<path d="{smooth_closed(P_([(-11, -3), (-4, -4), (-3, 0), (-11, 0.5)]))}" fill="#2A1A16"/>')
    out.append(f'<path d="{smooth_closed(P_([(8, -7.5), (14, -5.5), (13.5, -2), (8, -3.5)]))}" fill="#2A1A16"/>')
    # cape: hood point, shoulders, flaring hem that swings with the stride
    cape = P_([(0, -101), (5, -99), (9, -94), (10, -87), (8.5, -80), (14, -76), (19, -70), (22, -58), (25, -44), (28, -30),
               (31, -21), (24, -18), (14, -21), (4, -17), (-6, -20), (-16, -18), (-27, -20), (-26, -32), (-23, -46), (-20, -60),
               (-17, -71), (-12, -76), (-8.5, -80), (-10, -87), (-9, -94), (-5, -99)])
    prims = [E(x, base - 82 * k, 12 * k, 16 * k, 0, 1.2, 1), E(x, base - 50 * k, 22 * k, 32 * k, 0, 1, 0.8),
             E(x - 2 * k, base - 28 * k, 28 * k, 12 * k, 0, 1, 0.7)]
    lk = Look(["#2A0608", "#5A0E12", "#8E1A1C", "#C02A24", "#E2523A", "#F8946A"], key=(0.0, -0.4, -0.5), amb=0.1, wrap=0.5,
              rim=(rim, (0, -1), 1.0), jit=0.04)
    out.append(form(D, cape, prims, lk, seed, flow=lambda x_, y_, n, p: 90 + (x_ - x) * 0.6, flow_jit=6, edge_w=1.4 * k * 1.6,
                    edge_op=0.5, edge_col="#1A0204", rim_col=rim, rim_w=2.2 * k * 1.4, rim_op=0.85, edge_light=(0, -1),
                    passes=((90, (10 * k, 26 * k), (1.6 * k, 3 * k), (0.4, 0.7)), (260, (5 * k, 14 * k), (0.8 * k, 1.6 * k), (0.45, 0.85)))))
    # deep vertical folds falling from the shoulders, lit edges on their ridges
    for fx0, fx1, op in ((-8, -14, 0.55), (3, 6, 0.5), (12, 20, 0.45), (-16, -24, 0.4)):
        out.append(taper(P_([(fx0 * 0.5, -70), (fx0 * 0.8 + fx1 * 0.2, -50), (fx1, -24)]), 0.8 * k, 3.2 * k, "#2A0408", op))
        out.append(taper(P_([(fx0 * 0.5 + 2.5, -68), (fx0 * 0.8 + fx1 * 0.2 + 3, -48), (fx1 + 3.5, -24)]), 0.5 * k, 2 * k, "#E8604A", op * 0.6))
    # hood seam and the gathered neck of the hood
    out.append(taper(P_([(0, -99), (0.5, -88), (0, -78)]), 1.6 * k, 0.6 * k, "#3A0608", 0.6))
    # basket on the left forearm: wicker body, rim, cloth, arched handle
    bx, by = x - 25 * k, base - 46 * k
    bp = [(bx - 9 * k, by - 2 * k), (bx + 9 * k, by - 2 * k), (bx + 7 * k, by + 8 * k), (bx - 7 * k, by + 8 * k)]
    out.append(f'<path d="{smooth_closed(bp)}" fill="#8A5A2A"/>')
    out.append(brushwork(seed + 7, (bx - 9 * k, by - 2 * k, bx + 9 * k, by + 8 * k), ["#C08A4A", "#5A3412", "#E0B070"], 26,
                         (3 * k, 7 * k), (0.4 * k, 0.9 * k), (0.5, 0.9), 0, 25, poly=bp))
    out.append(f'<path d="M{bx - 10 * k:.1f} {by - 2 * k:.1f} Q{bx:.1f} {by - 18 * k:.1f} {bx + 10 * k:.1f} {by - 2 * k:.1f}" stroke="#5A3412" stroke-width="{1.8 * k:.1f}" fill="none"/>')
    out.append(f'<path d="{blob(bx + 1 * k, by - 2.5 * k, 8 * k, 3 * k, seed, 0.2)}" fill="#F2ECE0"/>')
    out.append(f'<path d="M{bx - 9 * k:.1f} {by - 2 * k:.1f} L{bx + 9 * k:.1f} {by - 2 * k:.1f}" stroke="{rim}" stroke-width="{1.2 * k:.1f}" opacity="0.7"/>')
    # rim light ring on the hood top
    out.append(taper(P_([(-9.5, -88), (-6, -96), (0, -100.5), (6, -97), (9.5, -88)]), 0.8 * k, 0.8 * k, rim, 0.45))
    out.append(taper(P_([(-8, -81), (0, -78.5), (8, -81)]), 1.4 * k, 1.4 * k, "#3A0608", 0.5))
    return "".join(out)


def wolf_head(D, x, y, s, seed, look, eye="#FFC24A", flip=False):
    """A grey wolf's head and ruff in profile (facing left unless flip): long muzzle, pointed upright ears,
    heavy brow, cheek ruff; lit from behind so the edges glow and the eye catches the light."""
    def T_(pts):
        return [(x + (-px if flip else px) * s, y + py * s) for px, py in pts]
    head = T_([(40, 60), (34, 30), (30, 6), (26, -12), (20, -20), (16, -24), (10, -42), (4, -26), (-6, -24), (-18, -18), (-32, -13),
               (-46, -9), (-55, -5), (-57, 0), (-54, 3), (-46, 5), (-36, 7), (-42, 10), (-38, 13), (-28, 14), (-16, 16), (-8, 24),
               (-4, 38), (0, 60)])
    prims = [E(x + (8 if not flip else -8) * s, y - 4 * s, 22 * s, 18 * s, 0, 1.1, 1),
             C(x - (10 if not flip else -10) * s, y - 8 * s, x - (52 if not flip else -52) * s, y - 2 * s, 11 * s, 6 * s, 1.2),
             C(x + (14 if not flip else -14) * s, y + 10 * s, x + (20 if not flip else -20) * s, y + 50 * s, 22 * s, 24 * s, 0.9)]
    out = [form(D, head, prims, look, seed, flow=lambda x_, y_, n, p: 200 if not flip else -20, flow_jit=25, edge_w=1.4 * s,
                edge_op=0.6, edge_col="#0A0806", rim_col=look.rim[0] if look.rim else None, rim_w=1.6 * s, rim_op=0.9,
                edge_light=look.rim[1] if look.rim else None,
                passes=((80, (6 * s, 14 * s), (1.2 * s, 2.4 * s), (0.4, 0.7)), (260, (3 * s, 8 * s), (0.6 * s, 1.2 * s), (0.45, 0.85))))]
    # far ear behind, inner ear shadow, ruff tufts, eye, nose, lip line
    out.append(f'<path d="{smooth_closed(T_([(24, -14), (22, -40), (14, -22)]))}" fill="{ramp(look.cols, 0.1)}" opacity="0.9"/>')
    out.append(taper(T_([(8, -26), (9, -36), (10, -40)]), 3 * s, 0.4 * s, ramp(look.cols, 0.0), 0.7))
    rnd = random.Random(seed)
    for _ in range(16):
        px, py = rnd.uniform(-6, 22), rnd.uniform(8, 52)
        out.append(taper(T_([(px, py), (px - 5, py + 6), (px - 8, py + 12)]), 2.2 * s, 0.3 * s, rnd.choice([ramp(look.cols, 0.15), ramp(look.cols, 0.5)]), 0.6))
    ex, ey = T_([(-16, -12)])[0]
    out.append(halo(D, ex, ey, 9 * s, eye, 0.6))
    out.append(f'<path d="{smooth_closed([(ex - 3.2 * s, ey + 0.6 * s), (ex, ey - 1.6 * s), (ex + 3.2 * s, ey - 0.3 * s), (ex + 0.2 * s, ey + 1.4 * s)])}" fill="{eye}"/>')
    out.append(f'<circle cx="{ex + (-0.6 if not flip else 0.6) * s:.1f}" cy="{ey:.1f}" r="{0.9 * s:.1f}" fill="#120804"/>')
    nx_, ny_ = T_([(-54, -3)])[0]
    out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="{3.2 * s:.1f}" ry="{2.6 * s:.1f}" fill="#0E0A08"/>')
    out.append(taper(T_([(-50, 4), (-40, 6), (-30, 8)]), 1.4 * s, 0.4 * s, "#0E0A08", 0.75))
    out.append(taper(T_([(-20, -16), (-8, -20), (4, -22)]), 1.8 * s, 0.5 * s, ramp(look.cols, 0.7), 0.5))
    return "".join(out)


@design("little-red-riding-hood")
def red_riding_hood_g():
    D = Doc2("rh")
    varnish("little-red-riding-hood", 52, edge=3.0, bristle=0.5, grain=0.22)
    out = []
    # deep wood: the far clearing glows gold-green, the trees darken toward us
    out.append(sky_paint(D, [(0, "#1E2A22"), (0.3, "#3E5238"), (0.5, "#9AA87A"), (0.62, "#D8D49A"), (0.75, "#8A9A66"), (1, "#26301E")],
                         5201, 0, 600, n=200, L=(40, 140), W=(4, 12), op=(0.08, 0.22), angle=-90))
    out.append(halo(D, 300, 300, 260, "#FFF2B8", 0.75, ry=190))
    out.append(halo(D, 300, 310, 110, "#FFFCE0", 0.85, ry=80))
    # far trunks in the glow (pale, hazy), then middle trunks
    rnd = random.Random(5202)
    for i, (tx_, w, c) in enumerate(((180, 10, "#9AA486"), (228, 7, "#AEB894"), (372, 8, "#AAB490"), (410, 12, "#98A282"), (262, 5, "#BCC4A0"),
                                     (340, 5, "#BCC4A0"), (140, 14, "#7E8A6A"), (460, 15, "#7A866A"))):
        out.append(f'<path d="{smooth_closed(jitter([(tx_ - w / 2, 330), (tx_ - w * 0.4, 200), (tx_ - w * 0.3, -10), (tx_ + w * 0.3, -10), (tx_ + w * 0.4, 200), (tx_ + w / 2, 330)], i, 1.0))}" fill="{c}" opacity="0.85"/>')
    out.append(light_shafts(D, (330, -40), [(250, 300, 420), (320, 350, 430), (190, 215, 400), (380, 410, 420)], "#FFF6C8", 0.28))
    out.append(mist_band(D, 320, 40, "#F4F2D0", 0.55, seed=5203, n=12))
    # ground: mossy floor, the path running from us into the light
    gl = Look(["#1A2414", "#2E4024", "#4E6A36", "#7E9A52", "#B8C47E", "#E8E6B0"], key=(0, -1, 0.3), amb=0.1, wrap=0.6, jit=0.08)
    gpts = [(-20, 318), (120, 312), (300, 306), (480, 312), (620, 316), (620, 620), (-20, 620)]
    g = D.lin([(0, "#AEB87A"), (0.15, "#6E8444"), (0.5, "#3A5028"), (1, "#1A2412")], 0, 306, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="{smooth_closed(gpts)}" fill="{g}"/>')
    out.append(brushwork(5204, (-20, 310, 620, 600), ["#4E6A36", "#2E4024", "#7E9A52", "#1A2414", "#A8B46E"], 520, (8, 26), (1, 3), (0.25, 0.6), 0, 6))
    path = [(300, 312), (288, 330), (292, 352), (310, 380), (300, 420), (268, 470), (262, 530), (300, 620)]
    pw = [6, 10, 16, 26, 40, 62, 90, 130]
    left_ = [(px - w / 2, py) for (px, py), w in zip(path, pw)]
    right_ = [(px + w / 2, py) for (px, py), w in zip(path, pw)]
    pp = left_ + right_[::-1]
    pg = D.lin([(0, "#FFF6CC"), (0.2, "#E8D49A"), (0.6, "#A88A5A"), (1, "#5A4428")], 0, 312, 0, 620, "userSpaceOnUse")
    out.append(f'<path d="{smooth_closed(pp)}" fill="{pg}"/>')
    out.append(brushwork(5205, (150, 310, 450, 620), ["#FFF2C0", "#C8A870", "#8A6A40", "#E8D49A"], 300, (6, 18), (0.8, 2.2), (0.3, 0.7), 4, 10, poly=pp))
    for (px, py), w in zip(resample(path, 6, closed=False), [0] * 400):
        pass
    edge_line = [p_ for p_ in resample(left_, 5, closed=False) + resample(right_, 5, closed=False) if p_[1] > 372]
    out.append("".join(taper([(ex_, ey_), (ex_ + rnd.uniform(-3, 3), ey_ - rnd.uniform(4, 12) * (0.5 + (ey_ - 300) / 200))], rnd.uniform(1, 2.4), 0.3,
                             rnd.choice(["#4E6A36", "#2E4024", "#7E9A52"]), 0.85) for ex_, ey_ in edge_line for _ in range(2)))
    out.append(dots := "".join(f'<ellipse cx="{rnd.uniform(240, 360):.1f}" cy="{(yy := rnd.uniform(420, 600)):.1f}" rx="{rnd.uniform(1.5, 4) * (yy / 400):.1f}" ry="{rnd.uniform(1, 2.4) * (yy / 400):.1f}" fill="{rnd.choice(["#FFF4D8", "#B8A07A", "#6A5434"])}" opacity="0.8"/>' for _ in range(40)))
    # flowers off the path (the temptation), bright in the shade
    for _ in range(46):
        fx, fy = rnd.uniform(60, 560), rnd.uniform(330, 470)
        if abs(fx - 300) < 40 + (fy - 320) * 0.3:
            continue
        c = rnd.choice(["#F2F0E8", "#F4D25A", "#C8A0E0", "#F2F0E8", "#E87A9A"])
        r = rnd.uniform(1.4, 3.0) * (0.6 + (fy - 320) / 200)
        out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r:.1f}" fill="{c}" opacity="0.9"/>')
    # middle-ground trunks (darker, still a little hazy)
    tl = Look(["#141A12", "#24301E", "#3E4A30", "#5E6A48", "#8E9A70", "#C8CC9A"], key=(0.2, -0.3, 0.5), amb=0.1, wrap=0.5, jit=0.05,
              rim=("#E8E6A8", (0.2, -1), 0.4))
    out.append(trunk_g(D, 196, 340, -20, 22, 16, 5206, tl, lean=0.02, crevices=12))
    out.append(trunk_g(D, 404, 336, -20, 24, 17, 5207, tl, lean=-0.02, crevices=12))
    # long shadows of the trunks thrown toward us by the light in the clearing
    for (bx_, by_, w) in ((196, 340, 22), (404, 336, 24), (40, 470, 120), (560, 470, 116), (140, 330, 14), (460, 330, 15)):
        dx, dy = bx_ - 300, by_ - 300
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        ex, ey = bx_ + ux * 700, by_ + uy * 700
        nx, ny = -uy, ux
        sp = [(bx_ - nx * w * 0.4, by_ - ny * w * 0.4), (bx_ + nx * w * 0.4, by_ + ny * w * 0.4),
              (ex + nx * w * 1.6, ey + ny * w * 1.6), (ex - nx * w * 1.6, ey - ny * w * 1.6)]
        sg = D.lin([(0, "#0A1006", 0.55), (1, "#0A1006", 0.15)], bx_, by_, ex, ey, "userSpaceOnUse")
        out.append(f'<path d="M{" L".join(f"{a:.1f} {b:.1f}" for a, b in sp)}Z" fill="{sg}"/>')
    # canopy: dark leaf masses closing over the top, lit at the edges facing the clearing
    cl_ = Look(["#040604", "#0A0E08", "#141C0E", "#24301A", "#3E4E2C", "#7E8E58"], key=(0, 0.7, 0.4), amb=0.03, wrap=0.3, jit=0.08)
    out.append(foliage_mass(D, [E(40, 20, 170, 80, 10), E(150, -10, 140, 60, 0), E(560, 30, 170, 90, -10), E(450, -20, 150, 60, 0),
                                E(300, -40, 200, 60, 0)], cl_, 5214, density=0.8, size=(4, 9)))
    # the girl on the path, walking into the light
    out.append(cast(D, 302, 391, 18, 4, "#141A0E", 0.5, 5))
    out.append(red_cloak_back(D, 302, 390, 74, 5208))
    # foreground giants: huge gnarled trunks framing the scene, rim-lit from the clearing
    fl = Look(["#050605", "#0A0D09", "#141A10", "#222A1A", "#3A4430", "#6E7656"], key=(0.8, -0.2, 0.3), amb=0.04, wrap=0.3, jit=0.04,
              rim=("#E8E2A8", (1, -0.2), 0.9))
    fr = Look(fl.cols, key=(-0.8, -0.2, 0.3), amb=0.04, wrap=0.3, jit=0.04, rim=("#E8E2A8", (-1, -0.2), 0.9))
    # the wolf, half hidden by the right-hand trunk, watching her
    wl = Look(["#0C0C0E", "#1E1C1C", "#3A3632", "#5E5850", "#8E867A", "#C8BEA8"], key=(-0.7, -0.3, 0.4), amb=0.1, wrap=0.5, jit=0.05,
              rim=("#E8E0A8", (-1, -0.3), 0.8))
    out.append(wolf_head(D, 474, 350, 1.4, 5211, wl))
    out.append(trunk_g(D, 20, 620, -40, 150, 84, 5209, fl, lean=0.07, wob=0.14, root_w=1.6, crevices=40, knots=0, edge_light=(1, 0)))
    out.append(trunk_g(D, 578, 620, -40, 140, 80, 5210, fr, lean=-0.07, wob=0.14, root_w=1.6, crevices=40, knots=0, edge_light=(-1, 0)))
    # a crooked bough reaching across the top like a claw
    bough = [(80, 70), (150, 60), (220, 78), (260, 70), (300, 82)]
    out.append(taper(bough, 18, 3, "#10140C", 0.95))
    out.append(taper([(150, 60), (176, 40), (198, 30)], 7, 1.5, "#10140C", 0.95))
    out.append(taper([(520, 100), (470, 96), (430, 112), (396, 106)], 16, 3, "#10140C", 0.95))
    # ferns and toadstools in the foreground corners
    fc = ["#3E5A2A", "#5E7E3A", "#22301A"]
    for (fx, fy, L, a, sd) in ((100, 560, 80, -60, 1), (120, 575, 70, -110, 2), (70, 540, 60, -30, 3), (500, 565, 76, -120, 4),
                               (480, 580, 66, -70, 5), (540, 548, 58, -150, 6)):
        out.append(fern_g(fx, fy, L, a, 5212 + sd, fc))
    for (mx, my, r, c) in ((150, 548, 11, "#C02A24"), (166, 556, 7, "#D84A30"), (448, 552, 9, "#C02A24")):
        out.append(f'<path d="M{mx - 2:.1f} {my:.1f}L{mx - 2.5:.1f} {my + r * 1.1:.1f}L{mx + 2.5:.1f} {my + r * 1.1:.1f}L{mx + 2:.1f} {my:.1f}Z" fill="#E8DCC0"/>')
        out.append(f'<path d="M{mx - r:.1f} {my:.1f}Q{mx:.1f} {my - r * 1.3:.1f} {mx + r:.1f} {my:.1f}Z" fill="{c}"/>')
        out.append(f'<circle cx="{mx - r * 0.3:.1f}" cy="{my - r * 0.5:.1f}" r="{r * 0.15:.1f}" fill="#FFF4E0"/><circle cx="{mx + r * 0.35:.1f}" cy="{my - r * 0.35:.1f}" r="{r * 0.12:.1f}" fill="#FFF4E0"/>')
    out.append(grass_tufts(5213, (0, 470, 600, 600), ["#3E5A2A", "#22301A", "#6E8A44", "#5E7E3A"], n=140, h=(10, 30)))
    # vignette
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.6, "#000000", 0), (1, "#000000", 0.55)], r=0.75)}"/>')
    # lettering: title arched into the canopy dark, quote on the path dark
    out.append(halo(D, 300, 84, 240, "#06080A", 0.55, ry=50))
    out.append(shadow_text(300, 98, "Little Red Riding Hood", SERIF_IT, 44, "#F2E6C8", max_w=430, sh="#000000", sop=0.65))
    out.append(shadow_text(300, 124, "A TALE FROM PERRAULT & GRIMM", CINZEL, 16, "#D8C890", ls=3, max_w=360, sh="#000000", sop=0.6))
    out.append(halo(D, 300, 534, 240, "#06080A", 0.6, ry=40))
    out.append(shadow_text(300, 542, "“Don’t stray from the path.”", SERIF_IT, 30, "#FFF0D0", max_w=420, sh="#000000", sop=0.7))
    return D.render(out)


# =====================================================================================================
# 3. PUSS IN BOOTS: the master cat on a hilltop at golden hour, surveying "the Marquis of Carabas's" lands
# =====================================================================================================
def puss_g(D, x, base, h, seed):
    """An upright tabby cat in a plumed cavalier hat, short cape, belt and rapier, and bucket-top boots, in
    profile facing left (into the low sun). h = feet to ear tips."""
    k = h / 100.0
    P_ = lambda pts: [(x + px * k, base + py * k) for px, py in pts]
    key = (-0.75, -0.35, 0.55)
    fur = Look(["#1E1612", "#3E3026", "#6A5644", "#9A8468", "#C8B08A", "#F2DEB4"], key=key, amb=0.08, wrap=0.4, jit=0.05,
               rim=("#FFD890", (-1, -0.2), 0.7), bounce=("#8A6A5A", 0.3))
    white = Look(["#5A4E46", "#8A7E72", "#BEB2A2", "#E6DCCC", "#FFF6E6", "#FFFFFF"], key=key, amb=0.1, wrap=0.45, jit=0.04,
                 rim=("#FFE0A0", (-1, -0.2), 0.6))
    leather = Look(["#1A0C06", "#3A1C0C", "#6A3416", "#9A5226", "#C8803E", "#F2B868"], key=key, amb=0.06, wrap=0.35, jit=0.04,
                   rim=("#FFD890", (-1, -0.2), 0.6), spec=("#FFE8B8", 0.85, 0.6))
    felt = Look(["#0E0A12", "#1E1624", "#34263C", "#4E3A58", "#6E5478", "#9A80A0"], key=key, amb=0.06, wrap=0.4, jit=0.04,
                rim=("#FFD890", (-1, -0.3), 0.6))
    red = Look(["#2A0608", "#560E10", "#861A18", "#B42A22", "#D8503A", "#F28A62"], key=key, amb=0.08, wrap=0.45, jit=0.04,
               rim=("#FFC880", (-1, -0.2), 0.6))
    st = lambda: ((90, (5 * k, 12 * k), (0.9 * k, 1.8 * k), (0.4, 0.7)), (300, (2.5 * k, 6 * k), (0.4 * k, 0.9 * k), (0.45, 0.85)))
    out = []
    # tail: rises behind in an S, ringed with darker bands
    tail = P_([(13, -52), (22, -50), (29, -57), (31, -68), (27, -78), (29, -88), (35, -92)])
    tl_o, tl_p = limb([(px, py, w) for (px, py), w in zip(tail, [6 * k, 5.5 * k, 5 * k, 4.6 * k, 4.3 * k, 4 * k, 3 * k])])
    out.append(form(D, tl_o, tl_p, fur, seed + 1, flow="axis", passes=st(), edge_w=1.2, edge_op=0.5, edge_col="#1A120C"))
    for i in range(1, 6):
        a, b = tail[i - 1], tail[i]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * 2.6 * k, dx / L * 2.6 * k
        out.append(taper([(mx - nx, my - ny), (mx + dx * 0.08, my + dy * 0.08), (mx + nx, my + ny)], 1.6 * k, 1.0 * k, "#2A1E16", 0.6))
    # cape flaring behind the shoulders
    cape = P_([(-4, -78), (6, -79), (14, -74), (22, -64), (27, -52), (20, -49), (16, -53), (10, -51), (8, -60), (2, -68)])
    out.append(form(D, cape, [E(x + 12 * k, base - 64 * k, 12 * k, 14 * k, 30, 1, 0.7)], red, seed + 2, flow=lambda *a: 60,
                    passes=st(), edge_w=1.2, edge_op=0.5, edge_col="#2A0406"))
    out.append(taper(P_([(8, -74), (15, -64), (18, -52)]), 0.5 * k, 1.6 * k, "#3A0608", 0.5))
    # far boot (behind, darker)
    def boot(dx, dy, lk, sd, dark=0.0):
        bp = P_([(px + dx, py + dy) for px, py in [(-16, 0.5), (-17.5, -1), (-11, -3.5), (-4.5, -6.5), (-2.2, -12), (-1.8, -20), (-2.6, -27),
                                                  (-9.5, -33.5), (-9, -38.5), (0.5, -40), (9.5, -39), (10, -33.5), (3.6, -28), (3.6, -18), (3.2, -9),
                                                  (5.2, -3), (5.6, 0.8)]])
        bpr = [E(x + (1 + dx) * k, base + (-20 + dy) * k, 3.8 * k, 15 * k, 0, 1, 1), E(x + (-6 + dx) * k, base + (-3 + dy) * k, 9 * k, 3.4 * k, -10, 1, 1),
               E(x + (0.3 + dx) * k, base + (-36 + dy) * k, 8.5 * k, 3.5 * k, -5, 1.1, 1)]
        lk2 = Look([dk(c, dark) for c in lk.cols], key=lk.key, amb=lk.amb, wrap=lk.wrap, jit=lk.jit, rim=lk.rim, spec=lk.spec)
        r = form(D, bp, bpr, lk2, sd, flow="axis", passes=st(), edge_w=1.4, edge_op=0.6, edge_col="#120602")
        # cuff turn-over line, heel, sole
        r += taper(P_([(-6.5 + dx, -34 + dy), (1 + dx, -35 + dy), (8.5 + dx, -34 + dy)]), 1.2 * k, 1.2 * k, "#1A0A04", 0.7)
        r += taper(P_([(-17 + dx, 0.3 + dy), (-6 + dx, 0.6 + dy), (5.5 + dx, 0.6 + dy)]), 1.3 * k, 1.3 * k, "#120602", 0.9)
        r += taper(P_([(4 + dx, 0.6 + dy), (4.5 + dx, -2.5 + dy)]), 2.4 * k, 2.0 * k, "#1A0A04", 0.9)
        r += taper(P_([(-12 + dx, -3 + dy), (-5 + dx, -6 + dy), (-2.8 + dx, -12 + dy), (-2.6 + dx, -24 + dy)]), 0.5 * k, 1.1 * k, "#FFE0A8", 0.6)
        return r
    out.append(boot(8, -1, leather, seed + 3, 0.25))
    # thighs (furry) above the boot cuffs
    th = P_([(-7, -38), (-8.5, -45), (-7, -52), (-2, -56), (8, -57), (14.5, -52), (15, -45), (11, -40), (8, -38)])
    out.append(form(D, th, [E(x + 3 * k, base - 47 * k, 11 * k, 9.5 * k, 10, 1, 1)], fur, seed + 4, flow=lambda *a: 100, passes=st(),
                    edge_w=1.2, edge_op=0.5, edge_col="#1A120C"))
    out.append(boot(0, 0, leather, seed + 5))
    # torso: chest thrown out, white bib; belt and sword
    tor = P_([(-6, -53), (-8.5, -59), (-11.5, -67), (-11.5, -74), (-8, -80), (1, -81), (6.5, -77), (7.5, -70), (6.5, -63), (8.5, -57), (12, -53)])
    out.append(form(D, tor, [E(x - 1 * k, base - 67 * k, 9 * k, 13 * k, -10, 1, 1), E(x - 6 * k, base - 71 * k, 6 * k, 8 * k, -10, 1.1, 1)],
                    fur, seed + 6, flow=lambda *a: 95, passes=st(), edge_w=1.2, edge_op=0.5, edge_col="#1A120C"))
    bib = P_([(-7.5, -58), (-11, -66), (-11, -74), (-7, -79.5), (-4, -74), (-4, -64), (-5, -57)])
    out.append(form(D, bib, [E(x - 7 * k, base - 68 * k, 5 * k, 10 * k, -10, 1, 1)], white, seed + 7, flow=lambda *a: 100, passes=st(),
                    edge_w=0, edge_op=0))
    # sword: scabbard slung back-down, swept hilt at the front hip
    out.append(taper(P_([(-2, -55), (10, -46), (22, -36), (31, -27)]), 2.6 * k, 2.0 * k, "#2A1A12", 1))
    out.append(taper(P_([(-1, -55), (10, -46.5), (22, -36.5), (30, -28)]), 0.8 * k, 0.6 * k, "#8A6A4A", 0.6))
    out.append(taper(P_([(-6, -59), (-3, -56.5), (0, -54)]), 1.6 * k, 1.6 * k, "#E8C878", 1))
    out.append(f'<path d="{smooth_open(P_([(-6, -55), (-9, -58), (-6, -62), (-2, -59)]))}" stroke="#D8B060" stroke-width="{1.1 * k:.1f}" fill="none"/>')
    out.append(f'<circle cx="{x - 7 * k:.1f}" cy="{base - 60.5 * k:.1f}" r="{1.4 * k:.1f}" fill="#F8E0A0"/>')
    out.append(taper(P_([(-9, -54.5), (2, -55.5), (13, -54)]), 2.6 * k, 2.6 * k, "#3A1C0C", 1))
    out.append(f'<rect x="{x - 3.5 * k:.1f}" y="{base - 56.8 * k:.1f}" width="{3.4 * k:.1f}" height="{2.8 * k:.1f}" fill="none" stroke="#E8C878" stroke-width="{0.8 * k:.1f}"/>')
    # near arm akimbo: shoulder, elbow out behind, paw on the belt
    arm_o, arm_p = limb([(x + 0.5 * k, base - 76 * k, 6 * k), (x + 1.5 * k, base - 66 * k, 4.6 * k), (x - 2 * k, base - 60 * k, 4.0 * k), (x - 5.5 * k, base - 58.5 * k, 4.6 * k)])
    out.append(form(D, arm_o, arm_p, fur, seed + 8, flow="axis", passes=st(), edge_w=1.2, edge_op=0.55, edge_col="#1A120C"))
    for t in (0.35, 0.7):
        ax_, ay_ = x + (0.5 + 1 * t) * k, base - (76 - 10 * t) * k
        out.append(taper([(ax_ - 2 * k, ay_ - 0.5 * k), (ax_, ay_ + 0.3 * k), (ax_ + 2 * k, ay_ + 1 * k)], 0.9 * k, 0.6 * k, "#2A1E16", 0.55))
    ruff = P_([(-10, -76), (-8, -82), (0, -84), (7, -80), (6, -75), (0, -77)])
    out.append(form(D, ruff, [E(x - 1 * k, base - 79 * k, 8 * k, 4.5 * k, 0, 1, 1)], fur, seed + 16, flow=lambda *a: 70, passes=st(), edge_w=0, edge_op=0))
    # neck ruff and head in profile: round skull, short nose, whisker pad, chin
    head = P_([(7, -82), (6, -90), (1, -96), (-6, -96.5), (-11, -93), (-14.5, -88.5), (-17.5, -85), (-18, -83), (-16, -81),
               (-13.5, -79), (-9, -77.5), (-3, -76), (4, -77)])
    hp = [E(x - 3 * k, base - 86 * k, 10.5 * k, 9.5 * k, 0, 1, 1), E(x - 13 * k, base - 82.5 * k, 4.5 * k, 3.6 * k, 0, 1.2, 1),
          E(x + 1 * k, base - 80 * k, 7 * k, 5 * k, 0, 0.9, 0.8)]
    out.append(form(D, head, hp, fur, seed + 9, flow=lambda x_, y_, n, p: math.degrees(math.atan2(n[1], n[0])) + 90, passes=st(),
                    edge_w=1.2, edge_op=0.55, edge_col="#1A120C"))
    muz = P_([(-17.5, -84), (-17.2, -82), (-14, -79), (-10, -78), (-9, -81), (-12, -83.5)])
    out.append(form(D, muz, [E(x - 13 * k, base - 81 * k, 4.5 * k, 3 * k, 0, 1, 1)], white, seed + 10, passes=st(), edge_w=0, edge_op=0))
    # tabby stripes: the forehead M, cheek lines, arm and thigh bars
    for pts in (([(-6, -95), (-7, -91), (-8, -89)]), ([(-2, -96), (-2.5, -91), (-3.5, -88)]), ([(2, -95), (1, -91)]),
                ([(-6, -84), (-1, -83.5), (3, -84.5)]), ([(-5, -81.5), (0, -80.5), (4, -81)]), ([(-9, -86), (-6, -87)])):
        out.append(taper(P_(pts), 1.3 * k, 0.4 * k, "#2A1E16", 0.65))
    for (yy, x0_, x1_) in ((-49, -8, 4), (-45, -8, 5), (-52, -7, 3)):
        out.append(taper(P_([(x0_, yy), ((x0_ + x1_) / 2, yy + 1), (x1_, yy + 0.5)]), 1.4 * k, 0.5 * k, "#2A1E16", 0.5))
    # eye: amber, slit pupil, catching the sun
    ex, ey = x - 11 * k, base - 88 * k
    eye = [(ex - 2.6 * k, ey + 0.4 * k), (ex - 0.2 * k, ey - 1.6 * k), (ex + 2.2 * k, ey - 0.6 * k), (ex + 0.6 * k, ey + 1.3 * k)]
    out.append(f'<path d="{smooth_closed(eye)}" fill="#E8B030"/>')
    out.append(f'<path d="{smooth_closed(eye)}" fill="none" stroke="#120A04" stroke-width="{0.7 * k:.1f}"/>')
    out.append(f'<ellipse cx="{ex - 0.3 * k:.1f}" cy="{ey - 0.1 * k:.1f}" rx="{0.45 * k:.1f}" ry="{1.3 * k:.1f}" fill="#120A04"/>')
    out.append(f'<circle cx="{ex - 1.2 * k:.1f}" cy="{ey - 0.6 * k:.1f}" r="{0.4 * k:.1f}" fill="#FFFFFF"/>')
    # nose leather, mouth, whiskers catching light
    out.append(f'<path d="{smooth_closed(P_([(-18, -84), (-16.6, -84.6), (-16.4, -83), (-17.6, -82.6)]))}" fill="#5A3A34"/>')
    out.append(taper(P_([(-17, -82), (-15.5, -80.6), (-13, -80.4)]), 0.5 * k, 0.3 * k, "#2A1A14", 0.8))
    for (a0, a1) in ((-8, -14), (-2, -10), (6, -6)):
        out.append(f'<path d="M{x - 13 * k:.1f} {base - 81.5 * k:.1f} q {-6 * k:.1f} {a0 * 0.15 * k:.1f} {-13 * k:.1f} {a1 * 0.25 * k:.1f}" stroke="#FFF4DC" stroke-width="{0.35 * k:.1f}" fill="none" opacity="0.85"/>')
    # ears: near ear forward of the hat crown, far ear peeking behind
    for (bx, by, tip, dkk, sd) in ((4, -95, (7, -104), 0.3, 11), (-7, -95.5, (-9, -105.5), 0.0, 12)):
        ep = P_([(bx - 4.5, by + 1), (tip[0], tip[1]), (bx + 4.5, by + 0.5)])
        lk2 = Look([dk(c, dkk) for c in fur.cols], key=key, amb=0.08, wrap=0.4, jit=0.04, rim=fur.rim)
        out.append(form(D, ep, [E(x + bx * k, base + (by - 4) * k, 4 * k, 6 * k, 0, 1, 1)], lk2, seed + sd, passes=st(), edge_w=1.0, edge_op=0.6, edge_col="#1A120C"))
        out.append(taper(P_([(bx, by), ((bx + tip[0]) / 2, (by + tip[1]) / 2 + 1), (tip[0] * 0.8 + bx * 0.2, tip[1] * 0.8 + by * 0.2)]), 2 * k, 0.5 * k, "#C88A7A", 0.6))
    # cavalier hat: soft crown, broad brim cocked up at the front, gold band, sweeping plume
    crown = P_([(-4, -97), (-3, -104), (2, -108), (9, -107), (12, -101), (11, -96)])
    out.append(form(D, crown, [E(x + 4 * k, base - 101 * k, 8 * k, 6 * k, 0, 1, 1)], felt, seed + 13, passes=st(), edge_w=1.2, edge_op=0.6, edge_col="#06040A"))
    out.append(taper(P_([(-4, -98.5), (4, -99.5), (11.5, -97.5)]), 1.8 * k, 1.8 * k, "#D8A848", 1))
    brim = P_([(-14, -101), (-8, -99), (0, -96.5), (10, -95), (19, -96), (20, -94), (10, -92.5), (0, -93.5), (-9, -96), (-15, -99)])
    out.append(form(D, brim, [E(x + 2 * k, base - 96 * k, 17 * k, 3 * k, -6, 1, 1)], felt, seed + 14, passes=st(), edge_w=1.2, edge_op=0.6, edge_col="#06040A"))
    plume = [(x - 2 * k, base - 103 * k), (x + 8 * k, base - 113 * k), (x + 22 * k, base - 114 * k), (x + 32 * k, base - 106 * k), (x + 36 * k, base - 96 * k)]
    out.append(hair_strands(plume, 46, lambda t: 2.5 * k + 5 * k * math.sin(math.pi * min(1, t * 1.1)), seed + 15,
                            ["#FFF8EC", "#F2E6D4", "#D8C8B4", "#FFFFFF", "#E8B0A0"], w=(0.5 * k, 1.3 * k), op=(0.5, 0.95)))
    out.append(taper(plume, 1.0 * k, 0.4 * k, "#C8B8A0", 0.8))
    return "".join(out)


@design("puss-in-boots")
def puss_in_boots_g():
    D = Doc2("pb")
    varnish("puss-in-boots", 63, edge=2.8, bristle=0.5, grain=0.2)
    out = []
    HZ = 330
    out.append(sky_paint(D, [(0, "#2E3A6A"), (0.3, "#6A6A94"), (0.55, "#C8908A"), (0.75, "#F2B67A"), (0.92, "#FFDCA0"), (1, "#FFE8B8")],
                         6301, 0, HZ + 10, n=240))
    SX, SY = 150, HZ - 10
    out.append(halo(D, SX, SY, 280, "#FFD890", 0.7, ry=200))
    out.append(halo(D, SX, SY, 60, "#FFF8E0", 0.95))
    clook = Look(["#6A5470", "#9A7480", "#D89A88", "#F8C898", "#FFEED0"], key=(-0.9, 0.1, 0.4), amb=0.1, wrap=0.5, jit=0.06)
    out.append(cloud(D, 430, 120, 260, 50, 6302, clook, n_puffs=12, size=(4, 10), flat=0.4))
    out.append(cloud(D, 520, 200, 200, 36, 6303, clook, n_puffs=9, size=(3, 8), flat=0.4))
    out.append(cloud(D, 80, 150, 180, 30, 6304, clook, n_puffs=8, size=(3, 7), flat=0.4))
    # far hills with the ogre's castle (soon the Marquis's), hazy in the sun
    far = rough([(-20, HZ - 8), (60, HZ - 30), (130, HZ - 46), (200, HZ - 38), (260, HZ - 20), (340, HZ - 26), (420, HZ - 14), (620, HZ - 18)], 6305, 6, 3)
    out.append(f'<path d="{smooth_closed(far + [(620, HZ + 20), (-20, HZ + 20)])}" fill="#C89A8A"/>')
    # castle on the far hill, backlit
    cx0, cb = 140, HZ - 44
    cs = []
    for (tx_, w, ht, cone) in ((-30, 9, 34, 16), (-14, 22, 26, 0), (4, 11, 46, 20), (22, 18, 22, 0), (36, 8, 30, 14)):
        X = cx0 + tx_
        cs.append(f'<rect x="{X - w / 2:.1f}" y="{cb - ht:.1f}" width="{w:.1f}" height="{ht + 4:.1f}" fill="#9A707A"/>')
        if cone:
            cs.append(f'<path d="M{X - w / 2 - 1.5:.1f} {cb - ht:.1f}L{X:.1f} {cb - ht - cone:.1f}L{X + w / 2 + 1.5:.1f} {cb - ht:.1f}Z" fill="#8A6070"/>')
            cs.append(f'<path d="M{X:.1f} {cb - ht - cone:.1f}l0 -6" stroke="#8A6070" stroke-width="1"/>')
        else:
            for m in range(int(w // 5)):
                cs.append(f'<rect x="{X - w / 2 + m * 5:.1f}" y="{cb - ht - 3:.1f}" width="3" height="3" fill="#9A707A"/>')
    out.append(f'<g opacity="0.9">{"".join(cs)}</g>')
    out.append(halo(D, cx0, cb - 20, 60, "#FFE6B0", 0.35))
    # rolling fields of ripe wheat, receding in bands toward the sun
    bands = [(HZ - 14, "#D8A868", "#E8C080"), (HZ + 6, "#C89048", "#F0C878"), (HZ + 34, "#B87A34", "#E8B860"), (HZ + 74, "#9A6024", "#D8A048")]
    for i, (y0, c0, c1) in enumerate(bands):
        line = rough([(-20, y0 + 10), (150, y0 - 4 + i * 3), (330, y0 + 6), (470, y0 - 8), (620, y0 + 4)], 6306 + i, 5, 3)
        g = D.lin([(0, c1), (1, c0)], 0, y0 - 10, 0, y0 + 60, "userSpaceOnUse")
        poly = line + [(620, 620), (-20, 620)]
        out.append(f'<path d="{smooth_closed(poly)}" fill="{g}"/>')
        out.append(brushwork(6310 + i, (-20, y0 - 10, 620, y0 + 60), [lt(c1, 0.25), c0, dk(c0, 0.15), "#FFE8A8"], 120 + i * 40,
                             (6 + i * 4, 18 + i * 8), (0.6 + i * 0.4, 1.4 + i * 0.8), (0.3, 0.7), lambda x_, y_: -80 + (x_ - SX) * 0.03, 8, poly=poly))
        # hedgerow / tree line at the field edge
        if i < 3:
            rr_ = random.Random(6320 + i)
            for _ in range(5 + i * 2):
                tx_ = rr_.uniform(-10, 610)
                ty_ = y_on(line, tx_) or y0
                r_ = 2.5 + i * 2.2
                tlk = Look(["#3A3020", "#5A4A2E", "#7A6A3E", "#A89058", "#E8C880"], key=(-0.9, -0.3, 0.3), amb=0.1, wrap=0.4, jit=0.06)
                out.append(foliage_mass(D, [E(tx_, ty_ - r_ * 1.1, r_ * 1.1, r_ * 1.2, 0), E(tx_ + r_ * 0.6, ty_ - r_ * 0.7, r_ * 0.9, r_ * 0.8, 0)], tlk,
                                        6330 + i * 50 + _, density=1.6, size=(0.8 + i * 0.4, 1.6 + i * 0.7)))
                out.append(f'<ellipse cx="{tx_ + r_ * 1.5:.1f}" cy="{ty_:.1f}" rx="{r_ * 1.6:.1f}" ry="{r_ * 0.25:.1f}" fill="#6A4A20" opacity="0.4"/>')
    # the road winding toward the castle, with the king's carriage on it
    road = [(250, 600), (300, 520), (250, 440), (190, 390), (170, HZ + 8)]
    rw = [60, 40, 22, 10, 3]
    rl = [(px - w / 2, py) for (px, py), w in zip(road, rw)]
    rr = [(px + w / 2, py) for (px, py), w in zip(road, rw)]
    out.append(f'<path d="{smooth_closed(rl + rr[::-1])}" fill="#E8C890" opacity="0.85"/>')
    out.append(f'<path d="{smooth_closed(rl + rr[::-1])}" fill="none" stroke="#9A6A34" stroke-width="1" opacity="0.4"/>')
    # carriage: dark box on wheels with a pair of horses, tiny on the road
    cxr, cyr = 214, 404
    out.append(f'<rect x="{cxr - 6:.1f}" y="{cyr - 9:.1f}" width="12" height="8" rx="2" fill="#3A2418"/><circle cx="{cxr - 4:.1f}" cy="{cyr:.1f}" r="2.4" fill="none" stroke="#2A1810" stroke-width="1.2"/><circle cx="{cxr + 4:.1f}" cy="{cyr:.1f}" r="2.4" fill="none" stroke="#2A1810" stroke-width="1.2"/>')
    out.append(f'<path d="M{cxr - 18:.1f} {cyr - 3:.1f} q 4 -4 9 -1 l 2 4 M{cxr - 16:.1f} {cyr - 2:.1f} l -1 4 M{cxr - 11:.1f} {cyr - 2:.1f} l 1 4" stroke="#3A2418" stroke-width="1.8" fill="none"/>')
    out.append(f'<path d="M{cxr - 3:.1f} {cyr - 9:.1f}l0 -3" stroke="#E8C060" stroke-width="1.2"/>')
    # foreground knoll where the cat stands: grass and wheat heads, rim-lit
    kn = [(250, 620), (290, 548), (350, 514), (430, 502), (520, 506), (620, 516), (620, 620)]
    kg = D.lin([(0, "#B08A3E"), (0.35, "#7A5A24"), (1, "#3A2610")], 0, 500, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="{smooth_closed(kn)}" fill="{kg}"/>')
    out.append(grass_tufts(6340, (290, 508, 620, 600), ["#A88A3A", "#6A5224", "#D8B868", "#4A3418", "#F2D488"], n=200, h=(8, 26)))
    # the master cat himself
    out.append(cast(D, 412, 512, 56, 7, "#1A120A", 0.55, 3))
    out.append(halo(D, 412, 380, 190, "#FFE0A0", 0.25))
    out.append(puss_g(D, 412, 511, 270, 6350))
    # wheat stalks in the very front, sunlit: bearded ears of tapered grains
    rnd = random.Random(6360)
    for _ in range(16):
        wx = rnd.uniform(270, 600)
        wy = rnd.uniform(570, 615)
        hh = rnd.uniform(60, 120)
        lean = rnd.uniform(-0.3, 0.12)
        top = (wx + lean * hh, wy - hh)
        out.append(taper([(wx, wy), (wx + lean * hh * 0.5, wy - hh * 0.5), top], 2.0, 0.9, rnd.choice(["#C89A48", "#A87A30"]), 0.9))
        ang = math.atan2(-hh, lean * hh)
        ux, uy = math.cos(ang), math.sin(ang)
        for j in range(9):
            t = j / 9
            gx, gy = top[0] + ux * 26 * t, top[1] + uy * 26 * t
            for sg in (-1, 1):
                a_ = ang + sg * 0.5
                g0 = (gx + math.cos(a_ + sg * 1.2) * 1.8, gy + math.sin(a_ + sg * 1.2) * 1.8)
                g1 = (g0[0] + math.cos(a_) * 7, g0[1] + math.sin(a_) * 7)
                c = rnd.choice(["#E8C060", "#F8DC88", "#C8963E", "#FFF0B0"])
                out.append(taper([g0, g1], 3.6, 0.8, c, 0.95))
                out.append(f'<path d="M{g1[0]:.1f} {g1[1]:.1f}l{math.cos(a_) * 10:.1f} {math.sin(a_) * 10:.1f}" stroke="#F2D890" stroke-width="0.6" opacity="0.7"/>')
    # a little texture and shade in the near field
    out.append(brushwork(6365, (-20, 470, 300, 620), ["#8A5A20", "#C8903E", "#6A4416", "#E8B860"], 160, (14, 40), (1, 2.6), (0.25, 0.55), -75, 10))
    out.append(f'<path d="M-20 520 Q 120 560 260 620 L -20 620 Z" fill="{D.lin([(0, "#2A1A08", 0.0), (1, "#2A1A08", 0.5)], 0, 520, 0, 620, "userSpaceOnUse")}"/>')
    # lettering
    out.append(halo(D, 300, 72, 240, "#1E2448", 0.4, ry=46))
    out.append(title_plate(D, 300, 92, "Puss in Boots", SERIF_IT, 58, pal="gold", max_w=440, shadow="#141834", sop=0.7))
    out.append(shadow_text(300, 120, "CHARLES PERRAULT · 1697", CINZEL, 16, "#FFF0D0", ls=4, max_w=320, sh="#141834", sop=0.6))
    return D.render(out)


# =====================================================================================================
# 4. JACK AND THE BEANSTALK: the stalk twisting up out of the valley into towering sunlit clouds
# =====================================================================================================
def heart_leaf(D, x, y, s, ang, seed, look, vein="#E8F0B0", inkc="#1A3010", squash=1.0, vein_op=0.45):
    """A broad heart-shaped bean leaf, modelled (lit half, shaded half, cupped), with midrib and veins.
    squash < 1 foreshortens it (seen edge-on)."""
    base = [(px, py * squash) for px, py in [(0, 0), (0.04, -0.28), (0.2, -0.48), (0.45, -0.46), (0.72, -0.28), (0.92, -0.08), (1.04, 0.0),
                                             (0.92, 0.08), (0.72, 0.28), (0.45, 0.46), (0.2, 0.48), (0.04, 0.28)]]
    pts = xf(base, x, y, s, ang)
    prims = [E(*xf([(0.45, -0.18 * squash)], x, y, s, ang)[0], s * 0.38, s * 0.22 * squash + 1, ang, 1, 0.6),
             E(*xf([(0.45, 0.18 * squash)], x, y, s, ang)[0], s * 0.38, s * 0.22 * squash + 1, ang, 1, 0.6),
             E(*xf([(0.5, 0)], x, y, s, ang)[0], s * 0.5, s * 0.1, ang, 0.8, 0.3)]
    out = [form(D, pts, prims, look, seed, flow=lambda x_, y_, n, p: ang + 40 * (1 if n[1] > 0 else -1), flow_jit=10,
                edge_w=max(0.8, s * 0.025), edge_op=0.3, edge_col=inkc,
                passes=((80, (s * 0.12, s * 0.3), (s * 0.02, s * 0.05), (0.35, 0.65)), (240, (s * 0.06, s * 0.16), (s * 0.01, s * 0.025), (0.4, 0.8))))]
    mid = xf([(0.02, 0), (0.5, 0.01), (0.98, 0)], x, y, s, ang)
    out.append(taper(mid, max(1.0, s * 0.03), 0.3, vein, vein_op * 1.3))
    for t in (0.22, 0.42, 0.62):
        for sg in (-1, 1):
            v = xf([(t, 0), (t + 0.14, sg * 0.18 * squash), (t + 0.22, sg * 0.32 * squash)], x, y, s, ang)
            out.append(taper(v, max(0.6, s * 0.018), 0.2, vein, vein_op))
    return "".join(out)


def beanstalk_g(D, guide, w0, w1, seed, look, leaf_look, leaves=14, leaf_s=(70, 26)):
    """Two stems twisting round each other up a guide curve, with heart leaves and curling tendrils."""
    rnd = random.Random(seed)
    g = resample(guide, 5, closed=False)
    n = len(g)
    out_back, out_front, leaf_parts = [], [], []
    for strand in (0, 1):
        joints = []
        for i, (px, py) in enumerate(g):
            t = i / (n - 1)
            a, b = g[max(0, i - 1)], g[min(n - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            w = w0 + (w1 - w0) * t
            ph = t * 9 + strand * math.pi
            off = math.sin(ph) * w * 0.32
            joints.append((px + nx * off, py + ny * off, w * (0.62 + 0.08 * math.cos(ph))))
        joints = joints[::2]
        o, pr = limb(joints)
        f = form(D, o, pr, look, seed + strand, flow="axis", flow_jit=4, edge_w=1.6, edge_op=0.55, edge_col="#0E2008",
                 passes=((40, (20, 40), (2.5, 5), (0.35, 0.6)), (160, (10, 24), (1, 2.2), (0.45, 0.8))))
        (out_back if strand == 0 else out_front).append(f)
        # a lit ridge running along the stem
        ridge = [(jx + 0.18 * jw, jy) for jx, jy, jw in joints]
        (out_back if strand == 0 else out_front).append(taper(ridge, max(1.0, w0 * 0.08), 0.5, ramp(look.cols, 0.95), 0.45))
    for j in range(leaves):
        t = (j + rnd.uniform(0.1, 0.9)) / leaves
        i = int(t * (n - 1))
        px, py = g[i]
        w = w0 + (w1 - w0) * t
        side = 1 if j % 2 == 0 else -1
        ang = (-20 if side > 0 else 200) + rnd.uniform(-30, 30)
        s_ = leaf_s[0] + (leaf_s[1] - leaf_s[0]) * t
        lx, ly = px + side * w * 0.4, py
        stalk = [(lx, ly), (lx + math.cos(math.radians(ang)) * s_ * 0.25, ly + math.sin(math.radians(ang)) * s_ * 0.25 - 4)]
        shade_k = rnd.uniform(-0.35, 0.15) - (0.2 if side < 0 else 0)
        ll = Look([mix(c, "#2A4A5A", max(0, -shade_k) * 1.5) if shade_k < 0 else mix(c, "#E8F0A0", shade_k) for c in leaf_look.cols],
                  key=leaf_look.key, amb=leaf_look.amb, wrap=leaf_look.wrap, jit=leaf_look.jit)
        leaf_parts.append((t, taper(stalk, max(1.5, w * 0.12), 1.0, ramp(look.cols, 0.4), 0.9) +
                           heart_leaf(D, stalk[-1][0], stalk[-1][1], s_, ang, seed + 50 + j, ll, squash=rnd.uniform(0.55, 1.0),
                                      vein=mix(ll.cols[4], "#FFFFFF", 0.3), vein_op=0.3)))
        # tendril
        if j % 2 == 1:
            tx0, ty0 = px - side * w * 0.4, py
            spiral = []
            for k in range(26):
                u = k / 25
                r = 14 * (1 - u) + 2
                a = u * 9 + rnd.uniform(0, 1)
                spiral.append((tx0 - side * 20 * u + math.cos(a) * r * u, ty0 - 16 * u + math.sin(a) * r * u))
            leaf_parts.append((t, taper(spiral, max(1.2, w * 0.06), 0.4, ramp(look.cols, 0.6), 0.9)))
    return "".join(out_back), "".join(out_front), leaf_parts


def climber(D, x, y, s, seed, col="#2A1C16", rim="#FFE4A8"):
    """A boy climbing, seen from behind and a little to the side: both hands gripping above his head, one knee
    drawn up, the other leg hanging. Painted as a dark figure with a warm rim light from the right."""
    k = s / 100.0
    P_ = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    lk = Look([dk(col, 0.4), col, lt(col, 0.15), lt(col, 0.35), lt(col, 0.55)], key=(0.8, -0.3, 0.4), amb=0.1, wrap=0.4,
              rim=(rim, (1, -0.2), 0.9), jit=0.04)
    shirt = Look(["#1E1A10", "#3A3420", "#5E5634", "#8A7E50", "#C8B478"], key=(0.8, -0.3, 0.4), amb=0.1, wrap=0.4, rim=(rim, (1, -0.2), 0.9), jit=0.04)
    out = []
    # arms raised: upper arms out and up, forearms to the grip
    for pts in (([(-9, -66), (-14, -84), (-6, -100)]), ([(9, -66), (15, -82), (8, -97)])):
        o, pr = limb([(px, py, w) for (px, py), w in zip(P_(pts), (7 * k, 6 * k, 5 * k))])
        out.append(form(D, o, pr, shirt, seed, flow="axis", edge_w=1, edge_op=0.6, edge_col="#0A0806", rim_col=rim, rim_w=1.2, edge_light=(1, -0.2),
                        passes=((400, (3 * k, 8 * k), (0.6 * k, 1.4 * k), (0.5, 0.85)),)))
    for hx, hy in ((-6, -101), (8, -98)):
        out.append(f'<path d="{blob(x + hx * k, y + hy * k, 3.2 * k, 3.6 * k, seed + hx, 0.1)}" fill="#C8906A"/>')
    # legs: right knee drawn up onto the stem, left leg hanging
    for pts, w in ((([(-5, -36), (-8, -18), (-6, 0)]), (8.5, 7, 5.5)), (([(5, -36), (16, -30), (14, -14)]), (8.5, 7, 5.5))):
        o, pr = limb([(px, py, ww * k) for (px, py), ww in zip(P_(pts), w)])
        out.append(form(D, o, pr, lk, seed + 3, flow="axis", edge_w=1, edge_op=0.6, edge_col="#0A0806", rim_col=rim, rim_w=1.2, edge_light=(1, -0.2),
                        passes=((400, (3 * k, 8 * k), (0.6 * k, 1.4 * k), (0.5, 0.85)),)))
    out.append(f'<path d="{smooth_closed(P_([(-9, 0), (-3, -1), (-1, 3), (-9, 3.5)]))}" fill="#1A1008"/>')
    out.append(f'<path d="{smooth_closed(P_([(11, -14), (17, -13), (18, -9), (11, -9)]))}" fill="#1A1008"/>')
    # torso (a belted jerkin) and head with a cap
    tor = P_([(-10, -36), (-11, -50), (-10, -64), (-6, -70), (6, -70), (10, -64), (11, -50), (10, -36)])
    out.append(form(D, tor, [E(x, y - 53 * k, 11 * k, 17 * k, 0, 1, 1)], shirt, seed + 5, flow=lambda *a: 90, edge_w=1, edge_op=0.6,
                    edge_col="#0A0806", rim_col=rim, rim_w=1.4, edge_light=(1, -0.2), passes=((300, (4 * k, 10 * k), (0.8 * k, 1.6 * k), (0.5, 0.85)),)))
    out.append(taper(P_([(-10.5, -40), (0, -39), (10.5, -40)]), 2.2 * k, 2.2 * k, "#2A1A0E", 0.95))
    out.append(f'<path d="{blob(x + 0.5 * k, y - 79 * k, 7 * k, 8 * k, seed + 7, 0.06)}" fill="#3A2416"/>')
    out.append(f'<path d="{smooth_closed(P_([(-7, -82), (-4, -90), (5, -91), (9, -84), (2, -86)]))}" fill="#4A6A2A"/>')
    out.append(f'<path d="M{x + 6.5 * k:.1f} {y - 86 * k:.1f} l {4 * k:.1f} {-3 * k:.1f}" stroke="#C83A2A" stroke-width="{1.2 * k:.1f}"/>')
    out.append(taper(P_([(7, -84), (7.5, -78), (6, -73)]), 1.2 * k, 0.6 * k, rim, 0.8))
    return "".join(out)


@design("jack-and-the-beanstalk")
def jack_beanstalk_g():
    D = Doc2("jb")
    varnish("jack-and-the-beanstalk", 74, edge=2.8, bristle=0.5, grain=0.2)
    out = []
    out.append(sky_paint(D, [(0, "#3A6AA8"), (0.35, "#6A9ACA"), (0.65, "#A8C8E0"), (1, "#E2ECEA")], 7401, 0, 600, n=220))
    out.append(halo(D, 520, 40, 260, "#FFF6DC", 0.6))
    # towering cumulus with the giant's castle on its summit, lit from the upper right
    clook = Look(["#6A7AA0", "#98A8C8", "#C8D2E2", "#F2F0EC", "#FFFFFF"], key=(0.7, -0.6, 0.4), amb=0.12, wrap=0.45, jit=0.05)
    out.append(cloud(D, 470, 250, 300, 90, 7402, clook, n_puffs=20, size=(6, 14)))
    out.append(cloud(D, 500, 176, 260, 60, 7411, clook, n_puffs=20, size=(5, 12), rscale=0.5))
    # castle: tall, pale, hazy Nielsen-like towers standing on the cloud summit
    cx0, cb = 478, 160
    cs = []
    wall = D.lin([(0, "#F2EEF4"), (0.6, "#C8C4DA"), (1, "#9A98BA")], 0, 0, 1, 0)
    for (tx_, w, ht, cone) in ((-62, 12, 48, 20), (-40, 30, 30, 0), (-14, 16, 70, 28), (8, 30, 36, 0), (34, 13, 56, 22), (54, 10, 34, 14)):
        X = cx0 + tx_
        cs.append(f'<rect x="{X - w / 2:.1f}" y="{cb - ht:.1f}" width="{w:.1f}" height="{ht + 30:.1f}" fill="{wall}"/>')
        if cone:
            cs.append(f'<path d="M{X - w / 2 - 2:.1f} {cb - ht:.1f}L{X:.1f} {cb - ht - cone:.1f}L{X + w / 2 + 2:.1f} {cb - ht:.1f}Z" fill="#8E8AB4"/>')
            cs.append(f'<path d="M{X:.1f} {cb - ht:.1f}L{X:.1f} {cb - ht - cone:.1f}L{X + w / 2 + 2:.1f} {cb - ht:.1f}Z" fill="#6E6A9A"/>')
            cs.append(f'<path d="M{X:.1f} {cb - ht - cone:.1f}l0 -7l6 2l-6 2" stroke="#6E6A9A" stroke-width="1" fill="#C8504A"/>')
        else:
            for m in range(int(w // 6)):
                cs.append(f'<rect x="{X - w / 2 + m * 6:.1f}" y="{cb - ht - 4:.1f}" width="3.6" height="4" fill="#D8D4E6"/>')
        for wy in range(int(cb - ht + 10), int(cb), 15):
            cs.append(f'<rect x="{X - 1.6:.1f}" y="{wy:.1f}" width="3.2" height="6" rx="1.6" fill="#5A5A84" opacity="0.65"/>')
    out.append(f'<g opacity="0.9">{"".join(cs)}</g>')
    out.append(halo(D, cx0 + 20, cb - 50, 120, "#FFFFFF", 0.3))
    out.append(cloud(D, 470, 214, 310, 60, 7403, clook, n_puffs=22, size=(5, 12), flat=0.5, rscale=0.45))
    # small clouds drifting far below us, and swallows for scale
    out.append(cloud(D, 90, 420, 140, 30, 7412, clook, n_puffs=8, size=(3, 8), flat=0.5))
    out.append(cloud(D, 470, 470, 180, 34, 7413, clook, n_puffs=9, size=(3, 8), flat=0.5))
    for (bx_, by_, bs) in ((380, 330, 9), (410, 352, 7), (360, 372, 6)):
        out.append(bird_v(bx_, by_, bs, "#24304A", 0.85))
    # far below: the valley, fields and the widow's cottage, hazy and blue
    out.append(halo(D, 300, 640, 420, "#C8D8C8", 0.7, ry=170))
    vl = rough([(-20, 520), (120, 506), (260, 520), (400, 508), (620, 516)], 7404, 6, 3)
    g = D.lin([(0, "#A8BC9A"), (1, "#7A9A6A")], 0, 500, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="{smooth_closed(vl + [(620, 620), (-20, 620)])}" fill="{g}"/>')
    rnd = random.Random(7405)
    for i in range(14):
        fx, fy = rnd.uniform(-10, 600), rnd.uniform(520, 600)
        out.append(f'<path d="{blob(fx, fy, rnd.uniform(30, 70), rnd.uniform(8, 16), i, 0.15, 10, rnd.uniform(-8, 8))}" fill="{rnd.choice(["#B8C88A", "#98B078", "#C8C890", "#88A070"])}" opacity="0.6"/>')
    out.append(brushwork(7406, (-20, 510, 620, 610), ["#7A9A6A", "#B8CCA0", "#6A8A5A"], 120, (10, 30), (1, 2.4), (0.25, 0.5), 0, 6))
    river = [(620, 530), (520, 540), (430, 534), (360, 552), (300, 566), (200, 580), (100, 600), (40, 620)]
    rl_ = [(px, py - 2 - (py - 520) * 0.08) for px, py in river]
    rr_ = [(px, py + 2 + (py - 520) * 0.08) for px, py in river]
    out.append(f'<path d="{smooth_closed(rl_ + rr_[::-1])}" fill="#E8F0EE" opacity="0.85"/>')
    for i in range(10):
        hy_ = 524 + i * 9 + rnd.uniform(-3, 3)
        out.append(f'<path d="M{rnd.uniform(-20, 300):.1f} {hy_:.1f} q {rnd.uniform(60, 120):.1f} {rnd.uniform(-6, 6):.1f} {rnd.uniform(160, 300):.1f} {rnd.uniform(-4, 8):.1f}" stroke="#5E7A4E" stroke-width="{1 + i * 0.2:.1f}" fill="none" opacity="0.45" stroke-dasharray="{2 + i * 0.3:.1f} {1.5 + i * 0.2:.1f}"/>')
    # cottage (tiny, thatched) where the stalk springs up
    hx, hy = 262, 560
    out.append(f'<path d="M{hx - 14} {hy} L{hx - 14} {hy - 10} L{hx + 14} {hy - 10} L{hx + 14} {hy} Z" fill="#E8DCC4"/>')
    out.append(f'<path d="M{hx - 18} {hy - 9} Q{hx} {hy - 28} {hx + 18} {hy - 9} Z" fill="#B89A5A"/><rect x="{hx - 2}" y="{hy - 7}" width="4" height="7" fill="#5A3A1E"/>')
    out.append(mist_band(D, 500, 40, "#E8EEEA", 0.5, seed=7407, n=10))
    # the beanstalk: from the cottage garden, twisting up past us into the cloud
    stalk_look = Look(["#0E2A0C", "#1E4A16", "#3A7024", "#5E9A36", "#9AC85A", "#D8EE9A"], key=(0.75, -0.5, 0.45), amb=0.06, wrap=0.4, jit=0.04,
                      bounce=("#6A9A8A", 0.3))
    leaf_look = Look(["#0A220C", "#163E16", "#2E6624", "#52923A", "#8ABE58", "#D2EC9A"], key=(0.75, -0.6, 0.4), amb=0.04, wrap=0.35, jit=0.05)
    guide2 = [(330, 176), (300, 250), (262, 300), (190, 352), (170, 420), (196, 490), (150, 610), (120, 680)]
    back2, front2, leaves2 = beanstalk_g(D, guide2, 26, 74, 7409, stalk_look, leaf_look, leaves=13, leaf_s=(30, 90))
    out.append(back2)
    for t, lp in sorted(leaves2, key=lambda a: -a[0]):
        if t > 0.5:
            out.append(lp)
    out.append(front2)
    # Jack, climbing, just below the halfway point
    out.append(climber(D, 232, 330, 64, 7410))
    for t, lp in sorted(leaves2, key=lambda a: -a[0]):
        if t <= 0.5:
            out.append(lp)
    # lettering in the open sky at left
    out.append(shadow_text(160, 98, "JACK AND THE BEANSTALK", CINZEL, 17, "#FFFFFF", ls=2, max_w=230, sh="#1A3460", sop=0.5))
    out.append(title_plate(D, 160, 160, "Fee-fi-", SERIF_IT, 64, pal="gold", max_w=230, shadow="#16305A", sop=0.6))
    out.append(title_plate(D, 176, 226, "fo-fum!", SERIF_IT, 64, pal="gold", max_w=240, shadow="#16305A", sop=0.6))
    return D.render(out)


# =====================================================================================================
# 5. THE LITTLE MERMAID: from behind, on a sea rock under the moon, watching the prince's lit ship
# =====================================================================================================
def mermaid_back(D, x, y, s, seed, rim="#DCE8FF"):
    """A mermaid seated on a rock, seen from behind and backlit by the moon: real shoulders and shoulder
    blades, a narrow waist, long wet hair down her back, the tail sweeping over the rock to a fin.
    (x, y) = where her hips meet the rock; s = scale (head about 15*s px tall)."""
    k = s
    P_ = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    key = (0.3, -0.5, -0.4)
    skin = Look(["#0E1626", "#1E2C46", "#34466A", "#56688E", "#8A9CBC", "#D0DCEE"], key=key, amb=0.22, wrap=0.6, jit=0.03,
                rim=(rim, (0.4, -1), 0.9))
    scales = Look(["#04161A", "#0A2A30", "#145048", "#22786A", "#4AA898", "#A8E8D8"], key=(0.3, -0.7, 0.3), amb=0.15, wrap=0.5, jit=0.06,
                  rim=(rim, (0.4, -1), 0.8))
    hair = Look(["#0E0A06", "#2A1C0E", "#4A3218", "#7A5428", "#B88A48", "#F2D49A"], key=key, amb=0.2, wrap=0.5, jit=0.05,
                rim=("#F8E8C0", (0.4, -1), 0.9))
    out = []
    # tail: from the hips across the rock and down to a fin trailing in the water
    tail_j = [(0, -2, 26), (14, 2, 24), (30, 8, 19), (46, 16, 14), (58, 26, 10), (66, 38, 7)]
    to, tp = limb([(x + px * k, y + py * k, w * k) for px, py, w in tail_j])
    out.append(form(D, to, tp, scales, seed, flow="contour", flow_jit=10, edge_w=1.2, edge_op=0.6, edge_col="#021012",
                    rim_col=rim, rim_w=1.4, edge_light=(0.4, -1),
                    passes=((60, (5 * k, 10 * k), (1.2 * k, 2.4 * k), (0.4, 0.7)), (260, (2 * k, 4 * k), (0.6 * k, 1.1 * k), (0.5, 0.9)))))
    # scale shimmer: rows of small arcs along the tail
    cid = D.clip(f'<path d="{smooth_closed(to)}"/>')
    rnd = random.Random(seed)
    arcs = []
    g = resample([(x + px * k, y + py * k) for px, py, _ in tail_j], 3.5 * k, closed=False)
    for i in range(1, len(g) - 1):
        (ax, ay), (bx, by) = g[i - 1], g[i + 1]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy, nx, ny = dx / L, dy / L, -dy / L, dx / L
        w = tail_j[0][2] * k * (1 - i / len(g)) * 0.5 + 3 * k
        for j in range(-3, 4):
            px, py = g[i][0] + nx * j * w / 3.5, g[i][1] + ny * j * w / 3.5
            r = 2.6 * k
            c = rnd.choice(["#7AE0C8", "#3AA090", "#C8F4E8", "#1E6A60"])
            arcs.append(f'<path d="M{px + nx * r:.1f} {py + ny * r:.1f}Q{px + ux * r * 1.3:.1f} {py + uy * r * 1.3:.1f} {px - nx * r:.1f} {py - ny * r:.1f}" '
                        f'stroke="{c}" stroke-width="{0.5 * k:.1f}" fill="none" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    out.append(f'<g {cid}>{"".join(arcs)}</g>')
    # fin: two translucent lobes with ribs
    fx, fy = x + 66 * k, y + 40 * k
    for sg in (-1, 1):
        lobe = [(fx, fy), (fx + 10 * k * sg + 8 * k, fy + 6 * k), (fx + 16 * k * sg + 14 * k, fy + 18 * k), (fx + 4 * k * sg + 8 * k, fy + 14 * k)]
        out.append(f'<path d="{smooth_closed(lobe)}" fill="#3AA090" opacity="0.75"/>')
        for t in (0.3, 0.6, 0.9):
            out.append(f'<path d="M{fx:.1f} {fy:.1f}L{fx + (16 * sg + 14) * k * t:.1f} {fy + 16 * k * t:.1f}" stroke="#A8F0E0" stroke-width="{0.5 * k:.1f}" opacity="0.6"/>')
    tilt = -5.0
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    R = lambda pts: [(x + (px * ca - py * sa) * k, y + (px * sa + py * ca) * k) for px, py in pts]
    Rp = lambda px, py: R([(px, py)])[0]
    arm_pass = ((320, (3 * k, 7 * k), (0.5 * k, 1.1 * k), (0.5, 0.85)),)
    # her left arm (our left) straight down to the rock, taking her weight
    j = [(*Rp(-10.5, -46.5), 5.6 * k), (*Rp(-14.5, -28), 4.4 * k), (*Rp(-17, -10), 3.4 * k), (*Rp(-18.5, -3), 4.2 * k)]
    ao, ap = limb(j)
    out.append(form(D, ao, ap, skin, seed + 2, flow="axis", edge_w=0.9, edge_op=0.5, edge_col="#060A14", rim_col=rim, rim_w=1.2,
                    edge_light=(0.4, -1), passes=arm_pass))
    # her right arm raised, elbow out, the hand gathering her hair behind her head
    j2 = [(*Rp(10.5, -46.5), 5.6 * k), (*Rp(19.5, -55), 4.4 * k), (*Rp(14, -64), 3.6 * k), (*Rp(7.5, -66), 3.8 * k)]
    ao2, ap2 = limb(j2)
    # back: sloping trapezius, shoulder blades, narrow waist, hips where the scales begin
    back = R([(-3.5, -55), (-7, -51.5), (-11.5, -48.5), (-12.5, -44), (-10.5, -36), (-7.5, -24), (-8, -14), (-10, -6), (-10.5, 0),
              (10.5, 0), (10, -6), (8, -14), (7.5, -24), (10.5, -36), (12.5, -44), (11.5, -48.5), (7, -51.5), (3.5, -55)])
    bp = [E(*Rp(0, -38), 11 * k, 12 * k, tilt, 1, 0.6), E(*Rp(-5.5, -40), 5.5 * k, 7 * k, tilt, 1.06, 0.7),
          E(*Rp(5.5, -40), 5.5 * k, 7 * k, tilt, 1.06, 0.7), E(*Rp(0, -20), 8 * k, 10 * k, tilt, 1, 0.6), E(*Rp(0, -5), 10.5 * k, 6 * k, tilt, 1, 0.5)]
    out.append(form(D, back, bp, skin, seed + 4, flow="contour", edge_w=0.9, edge_op=0.5, edge_col="#060A14", rim_col=rim, rim_w=1.4,
                    edge_light=(0.4, -1), passes=((120, (5 * k, 10 * k), (1 * k, 2 * k), (0.4, 0.7)), (360, (2.5 * k, 5 * k), (0.5 * k, 1 * k), (0.5, 0.85)))))
    out.append(taper(R([(0.5, -50), (0, -38), (0.3, -26), (0, -12)]), 0.6 * k, 1.2 * k, "#0E1626", 0.35))
    out.append(taper(R([(-10.5, -3), (0, -5), (10.5, -3)]), 4 * k, 4 * k, "#22786A", 0.55))
    # head, tilted toward the ship; hair swept down her back, wet and wavy
    hx, hy = Rp(1.5, -63)
    out.append(f'<path d="{blob(hx, hy, 6.3 * k, 7.6 * k, seed + 5, 0.05, rot=8)}" fill="#3A2812"/>')
    hout = R([(-5.5, -69), (-7.2, -62), (-6.6, -54), (-7.6, -46), (-8.4, -38), (-7.2, -30), (-4.8, -22), (-3.6, -14), (-1.2, -6),
              (1.0, -9), (2.6, -16), (3.4, -26), (4.6, -36), (5.6, -46), (6.4, -54), (7.0, -62), (5.8, -69), (0.6, -71)])
    hc = R([(0.5, -70), (0, -58), (-1.5, -46), (-2, -34), (-1, -22), (-0.5, -8)])
    hprim = [C(hc[i][0], hc[i][1], hc[i + 1][0], hc[i + 1][1], (7 - i * 0.7) * k, (6.6 - i * 0.8) * k) for i in range(len(hc) - 1)]
    out.append(form(D, hout, hprim, hair, seed + 6, flow="axis", flow_jit=6, edge_w=1.0, edge_op=0.5, edge_col="#050302",
                    rim_col="#F8E8C0", rim_w=1.4, edge_light=(0.4, -1),
                    passes=((100, (8 * k, 18 * k), (1 * k, 2 * k), (0.4, 0.7)), (400, (4 * k, 12 * k), (0.3 * k, 0.8 * k), (0.5, 0.9)))))
    wav = [(px + math.sin(i * 1.3) * 1.2 * k, py) for i, (px, py) in enumerate(resample(hc, 6, closed=False))]
    out.append(hair_strands(wav, 30, 4.5 * k, seed + 7, ["#F2D49A", "#B88A48", "#4A3218", "#7A5428"], w=(0.35 * k, 0.9 * k), op=(0.35, 0.8)))
    out.append(form(D, ao2, ap2, skin, seed + 3, flow="axis", edge_w=0.9, edge_op=0.5, edge_col="#060A14", rim_col=rim, rim_w=1.3,
                    edge_light=(0.4, -1), passes=arm_pass))
    # a few strands lifted by the sea breeze, and a pearl comb
    out.append(hair_strands(R([(5, -66), (14, -63), (24, -62), (32, -65)]), 8, 2.5 * k, seed + 8, ["#F2D49A", "#B88A48"], w=(0.3 * k, 0.8 * k), op=(0.4, 0.8)))
    for i in range(5):
        cx_, cy_ = Rp(-3 + i * 1.8, -67.5 + abs(i - 2) * 0.5)
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{0.85 * k:.1f}" fill="#F4F0E8"/>')
    return "".join(out)


def ship_lit(D, x, wl, s, seed):
    """A three-masted ship far off at night: dark hull, furled and set sails catching moonlight, rows of lanterns."""
    k = s
    out = []
    hull = [(x - 30 * k, wl - 6 * k), (x + 28 * k, wl - 7 * k), (x + 34 * k, wl - 12 * k), (x + 22 * k, wl + 1 * k), (x - 24 * k, wl + 1 * k)]
    out.append(f'<path d="{smooth_closed(hull)}" fill="#0A0E1C"/>')
    for i, mx in enumerate((-16, 0, 16)):
        out.append(f'<path d="M{x + mx * k:.1f} {wl - 6 * k:.1f}L{x + mx * k:.1f} {wl - (40 if i == 1 else 33) * k:.1f}" stroke="#0A0E1C" stroke-width="{0.9 * k:.1f}"/>')
        for j, (yy, ww) in enumerate(((12, 9), (22, 8), (31, 6))):
            if i != 1 and j == 2:
                continue
            sp = [(x + (mx - ww) * k, wl - (yy + 7) * k), (x + (mx + ww) * k, wl - (yy + 7) * k), (x + (mx + ww - 1) * k, wl - yy * k), (x + (mx - ww + 1) * k, wl - yy * k)]
            out.append(f'<path d="{smooth_closed(sp)}" fill="#8A96B4" opacity="0.85"/>')
            out.append(f'<path d="M{sp[0][0]:.1f} {sp[0][1]:.1f}L{sp[3][0]:.1f} {sp[3][1]:.1f}" stroke="#C8D2E8" stroke-width="{0.8 * k:.1f}" opacity="0.7"/>')
    rnd = random.Random(seed)
    for i in range(14):
        lx = x + rnd.uniform(-26, 28) * k
        ly = wl - rnd.choice((3, 5)) * k
        out.append(halo(D, lx, ly, 5 * k, "#FFD878", 0.7) + f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{0.7 * k:.1f}" fill="#FFF2C0"/>')
    # lanterns strung on the rigging
    for (a, b) in ((-16, 0), (0, 16)):
        for t in [i / 6 for i in range(1, 6)]:
            lx = x + (a + (b - a) * t) * k
            ly = wl - (36 - 6 * math.sin(math.pi * t)) * k
            out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{0.8 * k:.1f}" fill="{rnd.choice(["#FFD060", "#FF8A6A", "#B8E0FF"])}"/>')
    return "".join(out)


def firework_g(D, x, y, r, col, seed, n=26):
    rnd = random.Random(seed)
    out = [halo(D, x, y, r * 1.4, col, 0.35)]
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        L = r * rnd.uniform(0.7, 1.0)
        pts = [(x + math.cos(a) * L * t, y + math.sin(a) * L * t + 6 * t * t) for t in (0.2, 0.55, 0.85, 1.0)]
        out.append(taper(pts, 0.3, 1.4, col, rnd.uniform(0.5, 0.9)))
        out.append(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="1.1" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("the-little-mermaid")
def little_mermaid_g():
    D = Doc2("lm")
    varnish("the-little-mermaid", 85, edge=2.8, bristle=0.5, grain=0.2)
    out = []
    HZ = 352
    out.append(sky_paint(D, [(0, "#060A20"), (0.4, "#101C44"), (0.75, "#24386E"), (1, "#4A5E92")], 8501, 0, HZ, n=200))
    out.append(stars_field(8502, (10, 10, 590, 250), 90, r=(0.5, 1.4), op=(0.4, 0.9)))
    MX, MY = 214, 214
    out.append(halo(D, MX, MY, 200, "#B8C8F0", 0.45))
    out.append(halo(D, MX, MY, 70, "#E8F0FF", 0.55))
    mg = D.rad([(0, "#FFFDF4"), (0.7, "#F2EEDC"), (1, "#D8D4C2")], cx=0.42, cy=0.4, r=0.6)
    out.append(f'<circle cx="{MX}" cy="{MY}" r="36" fill="{mg}"/>')
    rnd = random.Random(8503)
    for _ in range(9):
        out.append(f'<path d="{blob(MX + rnd.uniform(-22, 22), MY + rnd.uniform(-20, 20), rnd.uniform(3, 9), rnd.uniform(3, 7), rnd.randint(0, 99), 0.2)}" fill="#C8C2B0" opacity="0.35"/>')
    # thin moonlit clouds
    clook = Look(["#18224A", "#2E3C6A", "#5A6A96", "#A8B4D4", "#E8EEF8"], key=(-0.2, -1, 0.3), amb=0.15, wrap=0.4, jit=0.05)
    out.append(cloud(D, 430, 150, 220, 26, 8504, clook, n_puffs=10, size=(3, 7), flat=0.5, rscale=0.5))
    out.append(cloud(D, 90, 290, 200, 22, 8505, clook, n_puffs=9, size=(3, 6), flat=0.5, rscale=0.45))
    # fireworks over the prince's ship
    SX = 452
    out.append(firework_g(D, 470, 218, 34, "#FFD27A", 8506))
    out.append(firework_g(D, 410, 252, 22, "#F2A0C8", 8507))
    out.append(firework_g(D, 512, 270, 18, "#A8E0FF", 8508))
    # sea: moon path, the ship's lights reflected
    out.append(water_paint(D, HZ, 600, [(0, "#3A4E84"), (0.2, "#22336A"), (0.6, "#121E46"), (1, "#080E26")], 8509, n=560,
                           refl=True, refl_x=MX, refl_w=36, refl_col="#E8EEFF", glints=260))
    for _ in range(40):
        y_ = rnd.uniform(HZ + 2, HZ + 40)
        out.append(bstroke(SX + rnd.gauss(0, 18), y_, 0, rnd.uniform(4, 12), rnd.uniform(0.5, 1.2), rnd.choice(["#FFD878", "#FFB868"]), rnd.uniform(0.4, 0.9)))
    out.append(ship_lit(D, SX, HZ + 2, 1.15, 8510))
    # the rock: dark, wet, rim-lit by the moon, with foam where the swell breaks
    rl = Look(["#020308", "#05080F", "#0A1020", "#141E34", "#26344E", "#56688A"], key=(-0.3, -0.8, 0.3), amb=0.03, wrap=0.3, jit=0.06,
              rim=("#C8D4F0", (-0.3, -1), 0.6))
    rock = [(-20, 600), (-20, 480), (30, 458), (90, 440), (150, 432), (210, 436), (260, 448), (300, 470), (340, 500), (390, 540), (430, 600)]
    rp = [E(110, 520, 150, 90, -8, 1, 0.8), E(260, 540, 110, 80, 10, 1, 0.8), E(30, 500, 70, 60, 0, 1, 0.8)]
    out.append(form(D, rock + [(430, 620), (-20, 620)], rp, rl, 8511, flow=lambda x_, y_, n, p: -30 + 60 * n[0], flow_jit=20, edge_w=1.4,
                    edge_op=0.5, edge_col="#000000", rim_col="#C8D4F0", rim_w=1.6, edge_light=(-0.3, -1),
                    passes=((40, (20, 46), (3, 6), (0.3, 0.55)), (160, (8, 22), (1, 2.6), (0.35, 0.7)))))
    # wet highlights and weed on the rock
    for _ in range(60):
        hx = rnd.uniform(20, 380)
        hy = (y_on(rock, hx) or 470) + rnd.uniform(4, 60)
        out.append(bstroke(hx, hy, rnd.uniform(-20, 10), rnd.uniform(4, 14), rnd.uniform(0.5, 1.4), rnd.choice(["#3A4A6A", "#5A6A8A", "#A8B8D8"]), rnd.uniform(0.15, 0.4)))
    for _ in range(26):
        wx = rnd.uniform(0, 400)
        wy = (y_on(rock, wx) or 470) + rnd.uniform(30, 120)
        out.append(taper([(wx, wy), (wx + rnd.uniform(-6, 6), wy + 10), (wx + rnd.uniform(-10, 10), wy + 22)], 3, 0.6, rnd.choice(["#1A3A2E", "#2A4A30", "#0E2420"]), 0.85))
    # the mermaid
    out.append(mermaid_back(D, 176, 438, 2.15, 8512))
    # foam where the swell breaks along the rock's foot: broken curling lines and a little spray
    for i in range(18):
        t = i / 17
        fx = 300 + t * 150 + rnd.uniform(-10, 10)
        fy = 470 + t * 140 + rnd.uniform(-6, 6)
        L = rnd.uniform(20, 46)
        out.append(taper([(fx - L * 0.5, fy + 2), (fx, fy - 2), (fx + L * 0.5, fy + 3)], rnd.uniform(1, 2.6), 0.4, rnd.choice(["#DCE6F8", "#A8B8D8", "#FFFFFF"]), rnd.uniform(0.4, 0.85)))
    for _ in range(50):
        fx = rnd.uniform(300, 470)
        fy = 470 + (fx - 300) * 0.9 + rnd.uniform(-20, 4)
        out.append(dab(fx, fy, rnd.uniform(0.8, 2.2), rnd.choice(["#DCE6F8", "#FFFFFF"]), rnd.uniform(0.3, 0.7), rnd, 0.6))
    # lettering
    out.append(halo(D, 300, 82, 250, "#04081A", 0.5, ry=50))
    out.append(title_plate(D, 300, 96, "The Little Mermaid", SERIF_IT, 50, pal="silver", max_w=440, shadow="#020614", sop=0.7))
    out.append(shadow_text(300, 124, "HANS CHRISTIAN ANDERSEN · 1837", CINZEL, 16, "#C8D4F0", ls=3, max_w=380, sh="#020614", sop=0.6))
    return D.render(out)


# =====================================================================================================
# GALLERY EDITION II (Oct 2026): book plates in the manner of Rackham, Dulac, Nielsen and Dore. Painted with
# paint_fairy_kit (forms modelled from drawn silhouettes, strokes coloured by the light). Each design returns
# (art, lettering): the art goes under a painterly varnish, the lettering stays crisp on top.
# =====================================================================================================
import paint_fairy_kit as K

PLATES = {}


def plate(slug, seed, edge=2.2, bristle=0.4, grain=0.18, freq=0.05):
    """Register a gallery plate: fn() -> (art, lettering)."""
    def deco(fn):
        def run():
            art, letters = fn()
            return K.varnished(art, letters, f"fv{slug.replace('-', '')}", seed, edge, freq, bristle, grain)
        DESIGNS[slug] = run
        VARNISH.pop(slug, None)
        PLATES[slug] = fn
        return fn
    return deco


# ---- plate: pegasus ----
@plate("pegasus", 41, edge=1.8, bristle=0.32, grain=0.15)
def pegasus_plate():
    """A white stallion rising out of the dawn over the sea: true equine anatomy (arched crest, sloping shoulder,
    deep girth, powerful quarters, folded forelegs, hind legs driving back), great swan wings from the withers."""
    D = K.Doc("pgs")
    out = []
    HZ = 452
    SX = 470
    stops = [(0, "#121840"), (0.25, "#283066"), (0.48, "#584C86"), (0.66, "#A0688E"), (0.8, "#DE9278"), (0.92, "#F6C489"), (1, "#FFE6B0")]
    out.append(K.sky(D, stops, 4101, 0, HZ, n=300, L=(80, 240), W=(4, 13), op=(0.07, 0.2)))
    out.append(K.stars(4102, (10, 6, 590, 170), 70, r=(0.5, 1.4), op=(0.35, 0.9)))
    for sx, sy, r in ((542, 52, 6), (566, 120, 3.5), (470, 92, 3)):
        out.append(K.halo(D, sx, sy, r * 3.2, "#FFF4D8", 0.45) + K.sparkle(sx, sy, r, "#FFFBEA", 0.95))
    out.append(K.halo(D, SX, HZ, 360, "#FFD49A", 0.55, ry=250))
    out.append(K.halo(D, SX, HZ - 2, 130, "#FFF4D6", 0.85, ry=70))
    # cloud towers lit from the sun at the right
    cl = K.Look(["#4A3A70", "#6E5288", "#A87294", "#E6A090", "#FFD2AE", "#FFF2DE"], key=(0.85, -0.35, 0.4), amb=0.1, wrap=0.45,
                jit=0.02, bounce=("#8A6A9E", 0.3))
    rnd = random.Random(4110)
    tower = [(150, 330, 70), (90, 372, 62), (210, 370, 58), (130, 268, 52), (186, 290, 46), (52, 404, 48), (262, 404, 44),
             (104, 222, 36), (160, 230, 34), (316, 420, 36), (20, 420, 40)]
    out.append(K.cumulus(D, tower, cl, 4111, flat_y=440, rim="#FFE8C0", dab_r=(5, 13), dab_op=(0.25, 0.6), density=1.3))
    bank = [(470 + rnd.uniform(-90, 120), 418 + rnd.uniform(-14, 8), rnd.uniform(18, 30)) for _ in range(9)]
    out.append(K.cumulus(D, bank, cl, 4112, flat_y=440, rim="#FFF0C8", dab_r=(2, 6)))
    out.append(K.mist(D, 444, 16, "#FFD8B0", 0.5, seed=4113, n=8, r=(80, 160)))
    # sea: violet with a broken gold path under the sun
    out.append(K.water(D, HZ, 600, [(0, "#D8A090"), (0.15, "#9A6E8E"), (0.5, "#4A3E72"), (1, "#1E1C46")], 4120, n=560,
                       refl_x=SX, refl_w=44, refl_col="#FFE2A8", glints=300))
    out.append(K.halo(D, SX, HZ + 6, 160, "#FFE2B0", 0.45, ry=14))
    # ---- the horse
    look = K.Look(["#2A2656", "#4A4482", "#8A80B4", "#C8B8D4", "#F2D8D0", "#FFE6C8", "#FFF6E6", "#FFFDF6"], key=(0.7, -0.55, 0.5), amb=0.12,
                  wrap=0.5, rim=("#FFCF7A", (1.0, -0.15), 0.95), bounce=("#8E7EC0", 0.5), jit=0.015)
    ox, oy, s, ang = 332, 268, 1.3, -7
    pose = dict(head_k=1.16, poll=(70, -66),
                hind_near=[(-124, 98, 17), (-146, 98, 12.5), (-162, 96, 12), (-168, 96, 15.5), (-181, 97, 11), (-190, 98, 12.5)],
                hind_far=[(-70, 80, 32), (-88, 94, 24), (-104, 104, 17), (-116, 108, 17), (-138, 112, 12.5), (-152, 114, 12), (-158, 115, 15.5),
                          (-170, 118, 11), (-179, 120, 12.5)])
    H = K.horse(D, ox, oy, s, ang, look, 4130, pose=pose, rim_col="#FFE2A0", edge_col="#262046", wind=(-1.0, 0.4),
                tail_guide=[(-100, 14), (-124, 26), (-150, 46), (-178, 60), (-208, 64), (-236, 58)])
    T = lambda pts: K.xform(pts, ox, oy, s, ang)
    wcols = ["#2E2C5C", "#55508A", "#8E88B8", "#C6BED8", "#ECE2E6", "#FFF6E8", "#FFFFFF"]
    # far wing (behind, cooler, reaching forward)
    S, E, W_, Tp = T([(4, -8), (-12, -42), (0, -102), (-48, -160)])
    out.append(K.wing(D, S, E, W_, Tp, wcols, 4140, trail=-1, light=(0.8, -0.4), prim_len=(84, 112), sec_len=(70, 76), ter_len=(48, 40),
                      n_prim=11, fan=0.85, dark=0.2, shade_amt=0.3, shadow_col="#1A1640", lit_rim="#FFE0A8"))
    out.append(H["far"])
    out.append(H["tail"])
    out.append(H["body"])
    out.append(H["mane"])
    # near wing: raised high in the upstroke, sweeping back
    S, E, W_, Tp = T([(-8, -2), (-38, -34), (-32, -98), (-106, -154)])
    out.append(K.wing(D, S, E, W_, Tp, wcols, 4150, trail=-1, light=(0.8, -0.4), prim_len=(88, 116), sec_len=(76, 82), ter_len=(54, 42),
                      n_prim=11, fan=0.85, shade_amt=0.34, shadow_col="#241E50", lit_rim="#FFE6B4"))
    out.append(K.feather(D, (214, 456), 200, 24, 3.6, ("#B8B0D0", "#E8E0EC", "#FFFFFF"), 4160, curve=0.1))
    art = D.render(out)
    DL = K.Doc("pgsL")
    L = [K.halo(DL, 300, 498, 250, "#100E30", 0.55, ry=56)]
    L.append(K.title(DL, 300, 508, "PEGASUS", CINZEL, 62, max_w=420, ls=12, face=("#FFF6DA", "#F2C870", "#A8742A"), shadow="#0A0820", sop=0.75))
    L.append(K.subtitle(300, 536, "Born of sea-foam, bound for the stars", SERIF_IT, 19, "#FFE8C4", max_w=420, sh="#0A0820", sop=0.7))
    return art, DL.render(L)
# ---- end plate: pegasus ----


# ---- plate: the-trojan-horse ----
def troy_wall(D, x0, x1, top, base, seed, look, warm=None, crenel=12):
    """A stretch of ancient ashlar wall: modelled face, stone courses and joints, crenellations along the top."""
    rnd = random.Random(seed)
    pts = [(x0, base), (x0, top)]
    x = x0
    up = True
    while x < x1:
        w = crenel * (1.0 if up else 0.8)
        pts += [(x, top - (8 if up else 0)), (min(x1, x + w), top - (8 if up else 0))]
        x += w
        up = not up
    pts += [(x1, top), (x1, base)]
    out = [f'<path d="{K.poly_d(pts)}" fill="{K.ramp(look.cols, 0.45)}"/>']
    cid = D.clip(K.poly_d(pts))
    st = []
    y = top + 4
    row = 0
    while y < base:
        hgt = rnd.uniform(9, 13)
        xx = x0 - rnd.uniform(0, 20)
        while xx < x1:
            w = rnd.uniform(18, 34)
            c = look.color((rnd.uniform(-0.15, 0.15), rnd.uniform(-0.1, 0.1), 1.0), rnd)
            if warm:
                c = K.mix(c, warm[0], warm[1](xx + w / 2, y + hgt / 2))
            st.append(f'<path d="{K.poly_d(K.rough([(xx, y), (xx + w, y), (xx + w, y + hgt), (xx, y + hgt), (xx, y)], rnd.randint(0, 999), 0.8, 6)[:-1])}" fill="{c}" opacity="{rnd.uniform(0.55, 0.9):.2f}"/>')
            st.append(f'<path d="M{xx:.1f} {y + hgt:.1f}H{xx + w:.1f}M{xx + w:.1f} {y:.1f}V{y + hgt:.1f}" stroke="{K.ramp(look.cols, 0.05)}" stroke-width="1.1" opacity="0.55"/>')
            if rnd.random() < 0.5:
                st.append(f'<path d="M{xx + 1:.1f} {y + 1.2:.1f}H{xx + w - 2:.1f}" stroke="{K.ramp(look.cols, 0.9)}" stroke-width="0.9" opacity="0.25"/>')
            xx += w
        y += hgt
        row += 1
    out.append(f'<g {cid}>{"".join(st)}</g>')
    return "".join(out), pts


@plate("the-trojan-horse", 77, edge=1.8, bristle=0.35, grain=0.2)
def trojan_horse_plate():
    """Doré-like night before Troy: the colossal timber horse, built plank by plank on a heavy sledge, is hauled
    toward the torchlit Scaean gate; the moon rims its back; under its belly a hatch leaks a thread of lamplight."""
    D = K.Doc("trj")
    out = []
    GY = 462
    stops = [(0, "#08101E"), (0.35, "#11223A"), (0.7, "#24344A"), (1, "#3E3A40")]
    out.append(K.sky(D, stops, 7701, 0, GY, n=220, L=(80, 220), W=(4, 12), op=(0.06, 0.18)))
    out.append(K.stars(7702, (240, 10, 590, 200), 50, r=(0.4, 1.2), op=(0.3, 0.8)))
    MX, MY = 486, 112
    out.append(K.halo(D, MX, MY, 170, "#B8CCE8", 0.35))
    out.append(f'<circle cx="{MX}" cy="{MY}" r="26" fill="{D.rad([(0, "#FFFDF0"), (0.8, "#F0EEDC"), (1, "#D8D8C8")])}"/>')
    rnd = random.Random(7703)
    for _ in range(14):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(3, 18)
        out.append(K.dab(MX + math.cos(a) * r, MY + math.sin(a) * r, rnd.uniform(2, 5), "#C8C8B4", 0.35, rnd))
    cl = K.Look(["#0E1828", "#1E2E46", "#3C4E6A", "#7A8EAA", "#C8D6EA"], key=(0.7, -0.6, 0.4), amb=0.05, wrap=0.3, jit=0.03)
    out.append(K.cumulus(D, [(390, 168, 30), (430, 160, 36), (476, 170, 30), (520, 162, 28), (560, 172, 24), (350, 176, 20)], cl, 7704,
                         flat_y=186, rim="#DCE6F6", dab_r=(3, 8), rim_w=1.6))
    out.append(K.cumulus(D, [(60, 120, 26), (100, 112, 30), (140, 124, 22), (20, 128, 20)], cl.darker(0.15), 7705, flat_y=136, dab_r=(3, 7)))
    # the city beyond the walls: roofs and a temple on the citadel, a few lamps
    city = K.Look(["#0A0C14", "#161A26", "#262A3A", "#3A3E50"], key=(0.6, -0.7, 0.5))
    out.append(f'<path d="{K.poly_d([(-10, 300), (20, 286), (40, 290), (64, 270), (96, 262), (120, 240), (150, 236), (172, 246), (200, 262), (236, 270), (262, 290), (290, 300), (290, 340), (-10, 340)])}" fill="#141824"/>')
    for (tx_, ty_) in ((128, 236),):
        out.append(f'<path d="{K.poly_d([(tx_ - 26, ty_), (tx_, ty_ - 14), (tx_ + 26, ty_)])}" fill="#1C2030"/>')
        for k in range(6):
            out.append(f'<rect x="{tx_ - 22 + k * 8.4:.1f}" y="{ty_:.1f}" width="3.2" height="16" fill="#2A2E40"/>')
    for _ in range(9):
        lx_, ly_ = rnd.uniform(10, 270), rnd.uniform(262, 300)
        out.append(K.halo(D, lx_, ly_, 7, "#FFB060", 0.5) + f'<rect x="{lx_ - 1.2:.1f}" y="{ly_ - 1.6:.1f}" width="2.4" height="3.2" fill="#FFD890"/>')
    # torchlight from the gate warms whatever is near it
    GX = 132

    def warmth(x, y):
        return max(0.0, 0.85 - math.hypot((x - GX) / 210, (y - 430) / 150))
    stone = K.Look(["#10141E", "#1E2432", "#323A4C", "#4E566A", "#7A8296"], key=(0.6, -0.7, 0.5), amb=0.2, jit=0.08)
    w1, wp = troy_wall(D, -20, 290, 318, GY + 6, 7710, stone, warm=("#E8904A", warmth))
    out.append(w1)
    # towers flanking the gate
    for tx0, tx1, ttop in ((62, 104, 270), (164, 206, 274)):
        tw, _ = troy_wall(D, tx0, tx1, ttop, GY + 6, 7711 + tx0, stone, warm=("#F0A050", warmth), crenel=9)
        out.append(tw)
        out.append(f'<path d="M{tx1:.1f} {ttop:.1f}V{GY + 6}" stroke="#05070C" stroke-width="2" opacity="0.5"/>')
    # the gate: a deep arched opening blazing with torchlight
    gate = [(106, GY + 6), (106, 378), (110, 362), (122, 350), (135, 347), (148, 350), (158, 362), (162, 378), (162, GY + 6)]
    out.append(K.halo(D, GX + 2, 420, 150, "#FF9A40", 0.35, ry=110))
    gg = D.lin([(0, "#FFE6A0"), (0.5, "#FFB050"), (1, "#C05A1E")], 0, 0, 0, 1)
    out.append(f'<path d="{K.smooth_closed(gate)}" fill="{gg}"/>')
    out.append(f'<path d="{K.smooth_closed(gate)}" fill="none" stroke="#2A1408" stroke-width="3" opacity="0.6"/>')
    for k in range(9):
        a0 = math.radians(180 + k * 22.5)
        out.append(f'<path d="M{GX + math.cos(a0) * 28:.1f} {368 + math.sin(a0) * 22:.1f}L{GX + math.cos(a0) * 36:.1f} {368 + math.sin(a0) * 30:.1f}" stroke="#1A1018" stroke-width="1.4" opacity="0.6"/>')
    # torches on the wall either side of the gate
    for fx in (96, 172):
        out.append(K.halo(D, fx, 372, 46, "#FFA040", 0.55))
        out.append(f'<path d="M{fx:.1f} 392L{fx:.1f} 378" stroke="#2A1608" stroke-width="2.4"/>')
        out.append(f'<path d="{K.smooth_closed([(fx - 4, 378), (fx - 3, 368), (fx, 360), (fx + 2, 366), (fx + 4, 378)])}" fill="#FFC060"/>')
        out.append(f'<path d="{K.smooth_closed([(fx - 2, 377), (fx - 1, 370), (fx + 1, 366), (fx + 2, 377)])}" fill="#FFF4C8"/>')
    # ground: dusty plain, torchlit near the gate, drag marks toward the gate
    gr = D.lin([(0, "#4A3A30"), (0.3, "#3A2C26"), (1, "#14100E")], 0, GY, 0, 600, "userSpaceOnUse")
    out.append(f'<rect x="-10" y="{GY}" width="620" height="150" fill="{gr}"/>')
    out.append(K.halo(D, GX, GY + 10, 220, "#E88A40", 0.4, ry=60))
    out.append(K.brushwork(7720, (-10, GY, 610, 600), lambda x, y, r: K.mix(K.mix("#5A4636", "#2A1E18", (y - GY) / 140), "#E89A58", warmth(x, y) * 0.6),
                           240, L=(10, 40), W=(1, 2.6), op=(0.25, 0.6), angle=0, jit=4))
    for k in (-1, 1):
        out.append(K.taper([(300 + k * 30, 600), (250 + k * 16, 520), (200 + k * 6, 480), (170, GY + 4)], 4, 1, "#1A120E", 0.45))
    # ---- the horse: timber on a sledge, facing the gate
    P = dict(K.HORSE_POSE)
    P.update(K.STAND_POSE)
    P.update(dict(poll=(58, -76), head_k=1.3, crest=[(0, -3), (8, -18), (18, -38), (30, -56), (42, -70), (52, -82)]))
    ox, oy, s = 370, 280, 1.28

    def legs(pts, y0):
        return [(x, y if y < y0 else y0 + (y - y0) * 0.8) for x, y in pts]
    FN = lambda dx=0, dy=0: legs(K.stand_fore(dx, dy), 60)
    HN = lambda dx=0, dy=0: legs(K.stand_hind(dx, dy), 86)

    def T(pts):
        return K.xform(pts, ox, oy, s, 0, flip=True)
    wood = K.Look(["#120A06", "#2A180E", "#4E2E18", "#7A4A26", "#A26C38", "#CC9452", "#EEBE78"], key=(-0.85, -0.25, 0.45), amb=0.06,
                  wrap=0.3, rim=("#9EB8D8", (0.55, -0.85), 0.7), jit=0.05)
    farw = wood.darker(0.3, rim=None)
    sledge_top = oy + 164 * s

    def wvf(x, y):
        return 0.25 * warmth(x, y) - 0.12

    def seams(outline, lines, col_d="#140A06", col_l="#D8A060", w=1.2, peg_every=0):
        cid = D.clip(K.smooth_closed(outline))
        st = []
        for ln in lines:
            pts = T(ln)
            st.append(f'<path d="{K.smooth_open(pts)}" fill="none" stroke="{col_d}" stroke-width="{w:.1f}" opacity="0.7"/>')
            st.append(f'<path d="{K.smooth_open([(x + 0.9, y + 1.1) for x, y in pts])}" fill="none" stroke="{col_l}" stroke-width="0.8" opacity="0.22"/>')
            if peg_every:
                fine = K.resample(pts, peg_every, closed=False)
                for (x, y) in fine[1::2]:
                    st.append(f'<circle cx="{x:.1f}" cy="{y + 3:.1f}" r="1.1" fill="#1A0E08" opacity="0.7"/>')
        return f'<g {cid}>{"".join(st)}</g>'

    def part(outline_local, lk, sd, lines, round_r=20, flow="contour", hide=None):
        o = T(outline_local)
        g = K.paint(D, o, lk, sd, round_r=round_r * s, flow=flow, flow_jit=6, edge_col="#0E0604", edge_w=2.0, edge_op=0.7,
                    rim_col="#B8CCE8", rim_w=1.4, rim_op=0.5, value_fn=wvf, edge_mask=(lambda x, y: not hide.inside(x, y + 2)) if hide else None,
                    passes=((40, (16, 34), (3, 6), (0.3, 0.55)), (200, (8, 20), (1.2, 2.6), (0.35, 0.7))))
        return g + seams(o, lines, peg_every=18)
    vlines = lambda x0, x1, y0, y1, step: [[(x, y0), (x + 0.5, (y0 + y1) / 2), (x, y1)] for x in [x0 + k * step for k in range(int((x1 - x0) / step) + 1)]]
    hlines = lambda x0, x1, y0, y1, step, bow=0.0: [[(x0, y), ((x0 + x1) / 2, y + bow), (x1, y)] for y in [y0 + k * step for k in range(int((y1 - y0) / step) + 1)]]
    # far legs
    out.append(part(HN(16, -2), farw, 7730, vlines(-120, -60, 20, 190, 7)))
    out.append(part(FN(-22, -2), farw, 7731, vlines(-10, 50, 60, 190, 7)))
    # tail of tarred hemp rope
    tg = T([(-104, 18), (-118, 40), (-124, 70), (-122, 102), (-116, 126)])
    out.append(K.hair(tg, 50, lambda t: 4 + 9 * t, 7732, ["#2A1A10", "#4E3420", "#7A5634", "#A07A50"], w=(1.4, 3.0), op=(0.6, 0.95), start=(0, 0.1), end=(0.75, 1.0)))
    # body, near hind and near fore carved as ONE mass: horizontal planking on barrel and quarters, planks
    # running up the neck and along the face, vertical staves down the legs
    body_l = K.horse_body_outline(P)
    whole = K.union_outline(polys=[T(body_l), T(HN()), T(FN())], step=2.0, smooth_px=1.0)
    bm = [(*T([(-86, 52)])[0], 28 * s, 38 * s, 10, 12 * s), (*T([(28, 30)])[0], 24 * s, 34 * s, -40, 8 * s),
          (*T([(-20, 44)])[0], 50 * s, 30 * s, 0, 6 * s), (*T([(-84, 120)])[0], 9 * s, 26 * s, 20, 4 * s)]
    out.append(K.paint(D, whole, wood, 7733, round_r=30 * s, bumps=bm, flow="contour", flow_jit=6, edge_col="#0E0604", edge_w=2.0,
                       edge_op=0.7, rim_col="#B8CCE8", rim_w=1.4, rim_op=0.5, value_fn=wvf, smooth=False,
                       passes=((40, (16, 34), (3, 6), (0.3, 0.55)), (200, (8, 20), (1.2, 2.6), (0.35, 0.7)))))
    neck_lines = []
    for k in range(-5, 6):
        off = k * 7
        neck_lines.append([(8 + off * 0.8, 50 + off * 0.5), (26 + off * 0.8, -10 + off * 0.5), (44 + off * 0.9, -60 + off * 0.5), (60 + off, -96 + off * 0.4)])
    hl_ = []
    for k in range(-1, 5):
        v = k * 7
        p0 = K.head_pt(P["poll"], P["head_th"], 6, v, P["head_k"])
        p1 = K.head_pt(P["poll"], P["head_th"], 64, v * 0.6, P["head_k"])
        hl_.append([p0, K._lerp2(p0, p1, 0.5), p1])
    out.append(seams(whole, hlines(-118, 6, -6, 40, 8, 3) + hlines(-118, 44, 46, 96, 8, 3) + vlines(-106, -72, 104, 190, 6) + vlines(12, 50, 100, 190, 6.5), peg_every=18))
    out.append(seams(T(body_l), neck_lines + hl_, peg_every=18))
    # anatomy carved into the mass: stifle, gaskin, point of hock, elbow, knee
    for pts_, w_ in (([(-56, 70), (-62, 88), (-70, 100)], 2.2), ([(-100, 96), (-98, 110), (-100, 122)], 1.8), ([(16, 64), (22, 74)], 2.0),
                     ([(24, 104), (36, 104)], 1.6), ([(-98, 128), (-80, 128)], 1.6)):
        out.append(K.taper(T(pts_), w_, 0.6, "#140A06", 0.55))
    # cropped, upstanding mane of carved boards along the crest (as on Greek bronze horses)
    crest = K.resample([(56, -88), (46, -78), (34, -62), (22, -44), (12, -24), (4, -8)], 3, closed=False)
    mane = []
    for i, (x, y) in enumerate(crest[::2]):
        hh = 8 + 2 * math.sin(i * 0.9)
        q = T([(x - 2, y + 2), (x - 6, y - hh), (x + 2, y - hh - 2), (x + 3, y + 1)])
        c = wood.color((-0.6, -0.5, 0.6), rnd, wvf(*q[0]))
        mane.append(f'<path d="{K.poly_d(q)}" fill="{c}" stroke="#120804" stroke-width="0.8" opacity="0.95"/>')
    out.append("".join(mane))
    # carved eye, nostril, mouth
    ex, ey = T([K.head_pt(P["poll"], P["head_th"], 19, 11, P["head_k"])])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="6" ry="4" fill="#0E0604" transform="rotate(-30 {ex:.1f} {ey:.1f})"/>')
    out.append(f'<ellipse cx="{ex - 1.5:.1f}" cy="{ey - 1:.1f}" rx="2.2" ry="1.4" fill="#E8A458" opacity="0.7"/>')
    nx_, ny_ = T([K.head_pt(P["poll"], P["head_th"], 57, 15, P["head_k"])])[0]
    out.append(f'<circle cx="{nx_:.1f}" cy="{ny_:.1f}" r="3" fill="#0E0604" opacity="0.8"/>')
    # the hatch in the belly, with a thread of lamplight
    hatch = T([(-46, 64), (-8, 66), (-8, 79), (-46, 78)])
    out.append(f'<path d="{K.poly_d(hatch)}" fill="none" stroke="#0A0402" stroke-width="2"/>')
    out.append(f'<path d="M{hatch[2][0]:.1f} {hatch[2][1]:.1f}L{hatch[3][0]:.1f} {hatch[3][1]:.1f}" stroke="#FFD080" stroke-width="1.6"/>')
    out.append(K.halo(D, (hatch[2][0] + hatch[3][0]) / 2, hatch[2][1] + 4, 26, "#FFC060", 0.5, ry=8))
    for hx in (0.25, 0.75):
        p = K._lerp2(hatch[0], hatch[1], hx)
        out.append(f'<rect x="{p[0] - 3:.1f}" y="{p[1] - 1:.1f}" width="6" height="3" fill="#3A3634"/>')
    # the sledge and rollers
    sl = [(ox - 150 * s, sledge_top - 2), (ox + 150 * s, sledge_top - 2), (ox + 156 * s, sledge_top + 16), (ox - 156 * s, sledge_top + 16)]
    out.append(K.paint(D, sl, wood.darker(0.1), 7740, round_r=6, flow=0, edge_col="#0A0402", edge_w=1.6, smooth=False, value_fn=wvf))
    for k in range(5):
        y = sledge_top + 2 + k * 3.4
        out.append(f'<path d="M{sl[3][0] + 4:.1f} {y:.1f}H{sl[2][0] - 4:.1f}" stroke="#140A06" stroke-width="0.9" opacity="0.5"/>')
    for rx in range(int(ox - 140 * s), int(ox + 150 * s), 34):
        out.append(f'<ellipse cx="{rx}" cy="{sledge_top + 19:.1f}" rx="6" ry="5.5" fill="#2A1A10" stroke="#0A0402" stroke-width="1.1"/>')
        out.append(f'<ellipse cx="{rx - 1.5:.1f}" cy="{sledge_top + 18:.1f}" rx="2.6" ry="2.4" fill="#6A4628" opacity="0.7"/>')
    out.append(K.halo(D, ox, sledge_top + 34, 210, "#000000", 0.5, ry=12))
    # Trojans hauling on the ropes, small against the gate light
    hand_pts = []
    for i, (fx, h, lean) in enumerate(((196, 30, -22), (220, 31, -26), (244, 29, -20), (178, 28, -18))):
        o, J = K.figure_silhouette(fx, GY + 14, h, dict(lean=lean, ua_n=70, fa_n=80, ua_f=62, fa_f=76, th_n=30, sh_n=10, th_f=-12, sh_f=-24,
                                                         robe=0.45), flip=False)
        out.append(f'<path d="{K.smooth_closed(o)}" fill="#120A08"/>')
        hand_pts.append(J["hand_n"])
    rope_end = (sl[3][0] + 6, sledge_top + 6)
    for i, hp_ in enumerate(hand_pts[:3]):
        out.append(f'<path d="M{rope_end[0]:.1f} {rope_end[1] + i * 3:.1f}Q{(rope_end[0] + hp_[0]) / 2:.1f} {max(rope_end[1], hp_[1]) + 6:.1f} {hp_[0]:.1f} {hp_[1]:.1f}" stroke="#2A1A10" stroke-width="1.4" fill="none"/>')
    art = D.render(out)
    DL = K.Doc("trjL")
    L = [K.halo(DL, 300, 80, 250, "#04060C", 0.55, ry=46)]
    L.append(K.title(DL, 300, 96, "The Trojan Horse", SERIF_IT, 52, max_w=440, face=("#FFF0C8", "#E8B65C", "#9A6420"), shadow="#04060C", sop=0.75))
    L.append(K.subtitle(300, 122, "THE FALL OF TROY · VIRGIL", CINZEL, 16, "#D8C8A8", ls=3, max_w=380, sh="#04060C", sop=0.7))
    L.append(K.halo(DL, 300, 526, 230, "#060404", 0.6, ry=34))
    L.append(K.subtitle(300, 534, "“Beware of Greeks bearing gifts.”", SERIF_IT, 23, "#FFE6B8", max_w=440, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: the-trojan-horse ----


# ---- plate: the-fox-and-the-grapes ----
def grape_bunch_painted(D, cx, top, w, h, seed, look, n=46, r=(8.5, 11), bloom="#B8A8D8"):
    """A heavy bunch of black grapes: berries packed in a tapering cone, each a lit sphere with a dusty bloom,
    a sharp highlight and the warm light passing through its rim; back berries first."""
    rnd = random.Random(seed)
    berries = []
    y = top + r[1]
    row = 0
    while y < top + h:
        t = (y - top) / h
        half = w * 0.5 * ((1 - t) ** 0.55) * (0.7 + 0.3 * min(1, t * 5)) + 3
        k = max(1, int(round(half * 2 / (r[1] * 1.45))))
        for j in range(k):
            x = cx - half + (j + 0.5 + (0.5 if row % 2 else 0)) * (half * 2 / (k + 0.5)) + rnd.uniform(-2, 2) + 3 * math.sin(t * 3)
            rr = rnd.uniform(*r) * (1 - 0.2 * t)
            for z in (rnd.uniform(0, 0.45), rnd.uniform(0.55, 1)):
                berries.append((z, x + rnd.uniform(-3, 3) * (1 - z), y + rnd.uniform(-2, 2), rr * (0.92 + 0.08 * z)))
        y += r[1] * 1.25
        row += 1
    berries.sort()
    out = []
    lx, ly = look.key[0], look.key[1]
    for z, x, y, rr in berries:
        dark = 0.25 * (1 - z)
        c0 = K.ramp(look.cols, 0.15 - dark * 0.5)
        c1 = K.ramp(look.cols, 0.45 - dark)
        c2 = K.ramp(look.cols, 0.75 - dark)
        g = D.rad([(0, c2), (0.55, c1), (1, c0)], round(0.5 + lx * 0.3, 2), round(0.5 + ly * 0.3, 2), 0.62)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr:.1f}" ry="{rr * 1.06:.1f}" fill="{g}"/>')
        out.append(f'<ellipse cx="{x - lx * rr * 0.1:.1f}" cy="{y - ly * rr * 0.1:.1f}" rx="{rr * 0.8:.1f}" ry="{rr * 0.85:.1f}" fill="{bloom}" opacity="{0.18 + 0.12 * z:.2f}"/>')
        # transmitted warm light on the rim away from the key, sharp highlight toward it
        out.append(f'<path d="M{x - lx * rr * 0.9 + ly * rr * 0.5:.1f} {y - ly * rr * 0.9 - lx * rr * 0.5:.1f}A{rr:.1f} {rr:.1f} 0 0 0 {x - lx * rr * 0.9 - ly * rr * 0.5:.1f} {y - ly * rr * 0.9 + lx * rr * 0.5:.1f}" '
                   f'transform="rotate(180 {x:.1f} {y:.1f})" stroke="#E86A8A" stroke-width="1.4" fill="none" opacity="0.5"/>')
        out.append(f'<ellipse cx="{x + lx * rr * 0.38:.1f}" cy="{y + ly * rr * 0.38:.1f}" rx="{rr * 0.2:.1f}" ry="{rr * 0.13:.1f}" fill="#FFFFFF" opacity="{0.55 + 0.35 * z:.2f}" transform="rotate(-35 {x:.1f} {y:.1f})"/>')
    return "".join(out)


def vine_leaf_painted(D, x, y, s, ang, seed, look, flip=False):
    """A grape leaf: five pointed, toothed lobes, palmate veins, lit by `look`."""
    rnd = random.Random(seed)
    pts = []
    # radius by angle: 5 lobes with sinuses, serrated
    for i in range(70):
        a = 2 * math.pi * i / 70
        lob = 0.62 + 0.38 * abs(math.cos(a * 2.5)) ** 0.7
        if 1.2 < a < 1.95:
            lob *= 0.35 + 0.65 * abs(a - 1.57) / 0.38          # petiole sinus at the bottom
        lob *= 1 + 0.06 * (i % 2)
        pts.append((math.cos(a) * lob, math.sin(a) * lob * 0.95))
    P = K.xform(pts, x, y, s, ang, flip)
    out = [K.paint(D, P, look, seed, round_r=s * 0.6, smooth=False, flow="axis", flow_jit=20, edge_col=K.ramp(look.cols, 0.0), edge_w=1.1,
                   edge_op=0.6, passes=((120, (6, 14), (1.5, 3), (0.35, 0.65)), (260, (3, 7), (0.8, 1.6), (0.45, 0.8))))]
    for a in (-90, -38, 18, 162, 218):
        q = K.xform([(0, 0.25), (math.cos(math.radians(a)) * 0.45, math.sin(math.radians(a)) * 0.45 + 0.1),
                     (math.cos(math.radians(a)) * 0.82, math.sin(math.radians(a)) * 0.82)], x, y, s, ang, flip)
        out.append(K.taper(q, 1.6, 0.4, K.ramp(look.cols, 0.85), 0.55))
    return "".join(out)


@plate("the-fox-and-the-grapes", 63, edge=1.8, bristle=0.35, grain=0.18)
def fox_grapes_plate():
    """Late-summer afternoon under an old pergola: a red fox sits looking up at the heavy bunch he cannot reach,
    every berry glowing; Aesop's lesson lettered in the warm air."""
    D = K.Doc("fxg")
    out = []
    GY = 452
    out.append(K.sky(D, [(0, "#F6D69A"), (0.5, "#F2C482"), (1, "#E8A866")], 6301, 0, GY, n=160, op=(0.06, 0.16)))
    out.append(K.halo(D, 520, 260, 300, "#FFF2C8", 0.6))
    # Mediterranean distance: hazy hills, cypresses, a farmhouse
    for k, (yb, col) in enumerate(((372, "#D8A880"), (402, "#BE9070"), (430, "#A07A58"))):
        ridge = K.rough([(-20, yb + 10), (120, yb - 16 + k * 4), (260, yb - 4), (400, yb - 22 + k * 6), (620, yb)], 6302 + k, 6, 10)
        out.append(f'<path d="{K.smooth_open(ridge)} L620 600 L-20 600Z" fill="{col}" opacity="0.9"/>')
    for cx_, h_ in ((84, 54), (100, 70), (116, 46), (470, 60), (488, 44)):
        out.append(f'<path d="{K.smooth_closed([(cx_, 420 - h_), (cx_ + 6, 420 - h_ * 0.6), (cx_ + 7, 420), (cx_ - 7, 420), (cx_ - 6, 420 - h_ * 0.6)])}" fill="#6E6A44" opacity="0.8"/>')
    out.append(f'<path d="M300 398h34v-14l-17-10-17 10Z" fill="#E8C8A0" opacity="0.75"/><path d="M296 386l21-13 21 13" stroke="#B0704A" stroke-width="3" fill="none" opacity="0.7"/>')
    # ground: dry summer grass and a dusty path
    gr = D.lin([(0, "#C89A5A"), (1, "#7A5A30")], 0, GY - 30, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 {GY - 20} Q300 {GY - 34} 610 {GY - 16} V610 H-10Z" fill="{gr}"/>')
    out.append(K.grass(6303, (-10, GY - 30, 610, 600), lambda x, y, r: r.choice(["#E2B868", "#B8883E", "#8A6A30", "#F2D088"]), n=320, h=(8, 24),
                       w=(1, 2.2), lean=(-0.3, 0.5)))
    # the old pergola: a weathered post at right, the beam across the top, the vine climbing it
    wood = K.Look(["#2A1A10", "#4E3420", "#7A5A3A", "#A88660", "#D8B88C"], key=(0.7, -0.5, 0.5), amb=0.1, wrap=0.35)
    post = [(500, 620), (498, 160), (530, 150), (536, 620)]
    out.append(K.paint(D, post, wood, 6310, round_r=10, flow=90, flow_jit=3, smooth=False, edge_col="#1A0E06"))
    beam = [(-20, 40), (620, 30), (620, 74), (-20, 84)]
    out.append(K.paint(D, beam, wood.darker(0.15), 6311, round_r=14, flow=-1, flow_jit=3, smooth=False, edge_col="#1A0E06"))
    out.append(K.brushwork(6312, (-20, 40, 620, 84), ["#2A1A10", "#C8A880"], 60, L=(30, 80), W=(0.6, 1.4), op=(0.2, 0.45), angle=-1, jit=1))
    vine = K.Look(["#2A1A10", "#4A3220", "#6E5034", "#9A7A54"], key=(0.7, -0.5, 0.5), amb=0.1)
    trunk = K.limb_outline([(520, 620, 16), (512, 500, 14), (522, 380, 12), (506, 260, 11), (516, 150, 9), (490, 90, 8), (440, 70, 7)])
    out.append(K.paint(D, trunk, vine, 6313, round_r=6, flow="contour", edge_col="#140A04", edge_w=1.4))
    # leaves along the beam (back layer, shadowed)
    leaf = K.Look(["#1E3010", "#34501E", "#56782E", "#86A24A", "#C8D07A"], key=(0.7, -0.5, 0.5), amb=0.1, wrap=0.4, jit=0.04,
                  rim=("#F8E08A", (0.8, -0.4), 0.5))
    rnd = random.Random(6320)
    for i in range(16):
        lx_ = -10 + i * 42 + rnd.uniform(-10, 10)
        out.append(vine_leaf_painted(D, lx_, 86 + rnd.uniform(-8, 22), rnd.uniform(26, 36), rnd.uniform(-30, 30), 6321 + i,
                                     leaf.darker(0.25 if i % 2 else 0.1), flip=i % 3 == 0))
    # the prize: a heavy bunch in a pool of sun
    out.append(K.shafts(D, (600, 60), [(300, 380, 600), (420, 470, 600), (150, 200, 600)], "#FFF4D0", 0.16))
    out.append(K.halo(D, 420, 200, 120, "#FFF0C0", 0.55))
    stem = [(436, 84), (430, 104), (424, 124)]
    out.append(K.taper(stem, 4, 2.4, "#4A3A20", 1))
    glook = K.Look(["#12061E", "#2E0E3E", "#5A1E5E", "#8A3A80", "#B86AA6"], key=(0.6, -0.7, 0.4))
    out.append(grape_bunch_painted(D, 420, 118, 84, 146, 6330, glook, n=78, r=(7.5, 10)))
    out.append(vine_leaf_painted(D, 470, 120, 40, 20, 6331, leaf))
    out.append(vine_leaf_painted(D, 372, 106, 34, -30, 6332, leaf.darker(0.1), flip=True))
    # ---- the fox, sitting, looking up
    ox, oy, s = 200, 452, 3.0
    HA, HO = -38, (0, -70)

    def rot(pts, ang=HA, o=HO, k=1.3):
        a = math.radians(ang)
        c, s_ = math.cos(a), math.sin(a)
        return [(o[0] + (x * c - y * s_) * k, o[1] + (x * s_ + y * c) * k) for x, y in pts]
    head_top = [(1, -8), (7, -10), (13, -8.5), (20, -5.5), (27, -3), (30, -1.2)]
    head_bot = [(29.5, 1.0), (26, 2.2), (20, 4.2), (13, 7), (6, 10.5), (0, 11)]
    body = ([(-30, 0), (-35, -9), (-34, -21), (-28, -31), (-19, -41), (-11, -51), (-7, -59)] + rot([(-5, -6)]) + rot(head_top) + rot(head_bot) +
            [(12, -61), (17, -54), (18, -44), (16, -36), (14, -26), (14, -10), (13, -4), (18, -1.5), (18, 0), (4, 0), (4, -4), (5, -20), (4, -28),
             (0, -24), (-4, -14), (-2, -4), (0, -1), (-2, 0)])
    T = lambda pts: K.xform(pts, ox, oy, s)
    inv = lambda x, y: ((x - ox) / s, (y - oy) / s)
    fur = K.Look(["#2A0C04", "#5E1E08", "#9A3A12", "#CE5E22", "#EE8A3C", "#FAB466", "#FFDCA0"], key=(0.65, -0.65, 0.45), amb=0.06, wrap=0.35,
                 rim=("#FFE0A0", (0.7, -0.6), 0.8), bounce=("#B07848", 0.3), jit=0.015)
    white = ["#B8A090", "#D8C8B8", "#EEE2D4", "#FBF4EA", "#FFFEF8"]
    black = ["#0A0606", "#1E1410", "#3A2A22", "#5E4636"]
    bib = [(11, -62), (17, -54), (18, -44), (15, -35), (10, -40), (8, -52)] + rot([(14, 9), (20, 4.6), (26, 2.4), (29, 1.0), (24, 3.6), (16, 7.5), (8, 10.5)])
    bib_v = K.Vol(T(bib), 6)

    def fur_col(x, y, col, n):
        return col

    def fur_flow(x, y, n):
        lx_, ly_ = inv(x, y)
        if n is None:
            n = (0, 0, 1)
        if ly_ < -60 and lx_ > -4:                   # head: hair runs back from the nose
            return HA + 180 + 10
        if lx_ > 2 and ly_ > -40:                     # legs: down
            return 92
        if lx_ < -20:                                 # haunch: around the curve
            return math.degrees(math.atan2(n[1], n[0])) + 90
        return 115                                    # back and flank: down and back
    # far foreleg and far ear first
    far_leg = [(6, -34), (10, -26), (10, -6), (12, -2), (13, 0), (2, 0), (2, -4), (2, -20), (1, -30)]
    out.append(K.paint(D, T([(x + 1, y) for x, y in far_leg]), K.Look(black, key=fur.key, amb=0.1), 6340, round_r=8, flow=90, edge_col="#000000"))
    ear_f = rot([(-1, -7), (-1, -17), (1, -24.5), (5, -16), (8, -8)])
    out.append(K.paint(D, T(ear_f), K.Look(black[:3] + ["#7A3A1A"], key=fur.key, amb=0.1), 6341, round_r=6, flow="contour", edge_col="#000000"))
    # the brush: the tail curled along the ground in front of the paws, white tip
    tail0 = [(-28, -8), (-36, -12), (-43, -9), (-45, -2), (-39, 3.5), (-25, 5.5), (-8, 5.5), (8, 3.5), (21, 0), (29, -5), (31, -10), (25, -13), (13, -12), (-1, -11), (-15, -10)]
    tail = K.rough(tail0 + [tail0[0]], 6352, 0.9, 2.2)[:-1]
    tv = K.Vol(T(tail), 10 * s)

    def tail_col(x, y, col, n):
        lx_, ly_ = inv(x, y)
        if lx_ > 21 + 1.5 * math.sin(ly_):
            return K.ramp(white, fur.value(n))
        return col
    # body (with head) then near ear, then tail in front
    bm = [(*T([(-22, -20)])[0], 17 * s, 19 * s, 0, 9 * s), (*T([(8, -44)])[0], 11 * s, 16 * s, 0, 4 * s), (*T(rot([(10, 2)]))[0], 9 * s, 7 * s, HA, 4 * s),
          (*T(rot([(22, -3)]))[0], 9 * s, 4 * s, HA, 2 * s)]
    out.append(K.paint(D, T(body), fur, 6342, round_r=12 * s, bumps=bm, flow=fur_flow, flow_jit=14, color_fn=fur_col, edge_col="#2A0A04",
                       edge_w=2.0, edge_op=0.65, rim_col="#FFE6A8", rim_w=1.8, rim_op=0.65,
                       passes=((50, (12, 24), (3, 6), (0.3, 0.5)), (240, (6, 13), (1.2, 2.4), (0.35, 0.7)), (160, (4, 8), (0.7, 1.3), (0.4, 0.8)))))
    # markings painted over the coat: the white bib and cheek, black stockings; fur strands feather their edges
    out.append(K.paint(D, T(bib), K.Look(white, key=fur.key, amb=0.2, wrap=0.4, jit=0.02), 6348, round_r=5 * s, flow=fur_flow, flow_jit=12,
                       edge_col=None, rim_col="#FFFFFF", rim_w=1.2, rim_op=0.4, passes=((60, (8, 16), (2, 4), (0.35, 0.6)), (260, (4, 9), (0.8, 1.6), (0.4, 0.8)))))
    bibf = K.resample(T(bib), 4)
    out.append("".join(K.taper([(x, y), (x + 2 * math.cos(math.radians(fur_flow(x, y, None))) * 3, y + 2 * math.sin(math.radians(fur_flow(x, y, None))) * 3)], 1.4, 0.3,
                                random.Random(int(x * 7 + y)).choice(["#FFF4E6", "#E8C8A8", "#C86A30"]), 0.7) for x, y in bibf))
    stock = [(14, -20), (14, -10), (13, -4), (18, -1.5), (18, 0), (4, 0), (4, -4), (5, -19)]
    out.append(K.paint(D, T(stock), K.Look(black, key=fur.key, amb=0.12, wrap=0.4), 6349, round_r=4 * s, flow=92, flow_jit=6, edge_col="#000000",
                       edge_w=1.2, rim_col="#C8885A", rim_w=1.0, rim_op=0.4, passes=((80, (8, 16), (2, 4), (0.35, 0.6)), (260, (4, 9), (0.8, 1.6), (0.4, 0.8)))))
    out.append(K.hair(T([(4.5, -24), (9, -21), (14, -24)]), 14, 3.0, 6350, ["#1A0E08", "#7A3414"], w=(0.6, 1.2), op=(0.5, 0.9)))
    # the foreleg separated from the chest by a shadowed groove; elbow
    out.append(K.taper(T([(4.5, -30), (5, -22), (5, -10)]), 2.2, 0.8, "#2A0A04", 0.55))
    ear_n = rot([(4, -8), (5, -18), (7.5, -27), (11, -18), (14, -8)])
    out.append(K.paint(D, T(ear_n), fur.darker(0.15), 6343, round_r=6, flow="contour", edge_col="#1A0604", edge_w=1.6,
                       color_fn=lambda x, y, c, n: K.ramp(black, 0.4) if inv(x, y)[0] < rot([(7, -20)])[0][0] - 0.5 else c))
    inner = rot([(6.5, -10), (7.5, -21), (10.5, -11)])
    out.append(K.taper(T(inner), 3.4 * s * 0.5, 0.8, "#F2D8B8", 0.75))
    out.append(K.hair(T(rot([(6, -10), (7.5, -17)])), 8, 2.2, 6344, ["#FFF0DC", "#E8C8A0"], w=(0.5, 1.0), op=(0.5, 0.9)))
    # eye: amber, slanted, with a dark tear line down the muzzle
    ex, ey = T(rot([(14.5, -4.5)]))[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="5.4" ry="2.9" fill="#1A0A04" transform="rotate({HA - 8} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<ellipse cx="{ex + 0.8:.1f}" cy="{ey - 0.3:.1f}" rx="3.8" ry="2.0" fill="#E8A030" transform="rotate({HA - 8} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<ellipse cx="{ex + 1.2:.1f}" cy="{ey - 0.3:.1f}" rx="0.9" ry="1.8" fill="#120604" transform="rotate({HA - 8} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<circle cx="{ex + 2.4:.1f}" cy="{ey - 1.4:.1f}" r="0.8" fill="#FFFFFF"/>')
    out.append(K.taper(T(rot([(18, -2), (22, 0.5), (25, 1.5)])), 1.6, 0.5, "#2A0A04", 0.6))
    nx_, ny_ = T(rot([(29.6, -0.4)]))[0]
    out.append(f'<ellipse cx="{nx_:.1f}" cy="{ny_:.1f}" rx="3.6" ry="2.6" fill="#140806" transform="rotate({HA} {nx_:.1f} {ny_:.1f})"/>')
    out.append(f'<circle cx="{nx_ - 0.6:.1f}" cy="{ny_ - 1.2:.1f}" r="0.9" fill="#FFFFFF" opacity="0.6"/>')
    for k in range(4):
        p0 = T(rot([(24 - k * 1.5, 1.6 + k * 0.6)]))[0]
        out.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f}l{8 + k * 2:.1f} {3 - k * 3:.1f}" stroke="#FFF4E0" stroke-width="0.6" opacity="0.6"/>')
    # paws: toes
    for px_ in (6, 11, 15):
        q = T([(px_, -1)])[0]
        out.append(f'<path d="M{q[0]:.1f} {q[1]:.1f}v{2.5:.1f}" stroke="#000000" stroke-width="1" opacity="0.5"/>')
    out.append(K.paint(D, T(tail), fur.darker(-0.05), 6345, vol=tv, flow=lambda x, y, n: 180 + 8 * math.sin(x * 0.05), flow_jit=16, color_fn=tail_col,
                       edge_col="#2A0A04", edge_w=1.8, edge_op=0.55, rim_col="#FFE6A8", rim_w=1.6,
                       passes=((60, (10, 22), (3, 6), (0.3, 0.55)), (260, (5, 12), (1.0, 2.4), (0.4, 0.8)))))
    # tufts breaking the silhouette, swept toward the tip
    rt = random.Random(6346)
    tufts = []
    for (x, y) in K.resample(T(tail0), 5):
        lx_, ly_ = inv(x, y)
        L_ = rt.uniform(4, 9)
        a = math.radians(-8 if ly_ < -4 else 8) + rt.uniform(-0.3, 0.3)
        c = "#FFF6EA" if lx_ > 21 else rt.choice(["#F6A050", "#E07A30", "#FFD08A", "#B04A18"])
        tufts.append(K.taper([(x - 3, y), (x + math.cos(a) * L_, y + math.sin(a) * L_ * 0.6 + (-3 if ly_ < -4 else 3))], 2.0, 0.3, c, 0.75))
    out.append("".join(tufts))
    # cast shadow of the fox on the dry grass, a few blades in front
    out.append(K.halo(D, ox - 20, oy + 8, 150, "#3A2410", 0.45, ry=12))
    out.append(K.grass(6347, (ox - 160, oy - 6, ox + 160, oy + 30), ["#F2D088", "#C89848", "#8A6A30"], n=60, h=(10, 22), w=(1, 2), lean=(-0.2, 0.5)))
    art = D.render(out)
    DL = K.Doc("fxgL")
    L = []
    L.append(K.halo(DL, 300, 500, 260, "#2A1808", 0.5, ry=50))
    L.append(K.title(DL, 300, 516, "Sour grapes!", SERIF_IT, 64, max_w=440, face=("#FFE6B0", "#F2B054", "#A8601E"), shadow="#2A1206", sop=0.8))
    L.append(K.subtitle(300, 545, "THE FOX AND THE GRAPES · AESOP", CINZEL, 15, "#FFF2D8", ls=3, max_w=380, sh="#2A1206", sop=0.8))
    return art, DL.render(L)
# ---- end plate: the-fox-and-the-grapes ----


# ---- plate: the-tortoise-and-the-hare ----
def tortoise_painted(D, ox, oy, s, seed, light=(-0.7, -0.6), flip=False):
    """A high-domed tortoise walking (side view): carapace of vertebral, costal and marginal scutes with growth
    rings, columnar scaly legs with claws, neck stretched forward, hooked beak, a bright patient eye."""
    rnd = random.Random(seed)
    T = lambda pts: K.xform(pts, ox, oy, s, 0, flip)
    lx, ly = light
    skin = K.Look(["#1E1A10", "#3A3420", "#5E5634", "#8A7E50", "#B8A874", "#E0D0A0"], key=(lx, ly, 0.5), amb=0.08, wrap=0.35,
                  rim=("#FFE8B0", (lx, ly), 0.4), jit=0.04)
    shell = K.Look(["#1A0E06", "#3A2410", "#68401A", "#9A6428", "#C8923E", "#ECC070"], key=(lx, ly, 0.55), amb=0.08, wrap=0.3,
                   rim=("#FFE6A8", (lx, ly), 0.5), jit=0.03)
    out = []
    # far legs (darker)
    FORE = [(12, -4), (26, -5), (29, 0), (28, 6), (31, 11), (34, 15.5), (30, 17), (22, 17.2), (17, 16.5), (18, 11), (15, 5)]
    HIND = [(-25, -3), (-40, -3), (-44, 4), (-45, 10), (-46, 16.2), (-38, 17), (-30, 16.4), (-29, 11), (-27, 6)]
    for leg in (FORE, HIND):
        lg = [(x + 8, y - 3) for x, y in leg]
        out.append(K.paint(D, T(lg), skin.darker(0.3), seed + 1 + len(out), round_r=5 * s, flow="contour", edge_col="#0E0A04"))
    # neck and head: stretched forward, slightly raised
    neck = [(22, -12), (34, -19), (44, -22), (52, -23), (60, -20), (65, -14), (63, -9), (56, -7), (46, -6), (36, -4), (26, -3), (18, -2)]
    head_c = (57, -15)
    out.append(K.paint(D, T(neck), skin, seed + 10, round_r=5 * s, bumps=[(*T([head_c])[0], 7 * s, 6 * s, 0, 3 * s)], flow="contour",
                       edge_col="#140E06", edge_w=1.6, rim_col="#FFE8B8", rim_w=1.2, rim_op=0.5,
                       passes=((80, (6, 12), (1.6, 3), (0.35, 0.6)), (300, (3, 6), (0.8, 1.5), (0.45, 0.85)))))
    # skin folds on the neck, scales on the head
    for k in range(5):
        x = 26 + k * 5
        out.append(K.taper(T([(x, -14 + k * 0.6), (x + 1.5, -9), (x, -4)]), 1.2, 0.4, "#1E1A10", 0.5))
    for _ in range(18):
        x, y = rnd.uniform(48, 62), rnd.uniform(-21, -10)
        q = T([(x, y)])[0]
        out.append(K.dab(q[0], q[1], rnd.uniform(1.2, 2.2), rnd.choice(["#2A2414", "#C8B880"]), 0.4, rnd))
    # beak line and eye
    out.append(K.taper(T([(64.5, -11.5), (60, -10.2), (55, -10.5)]), 1.4, 0.5, "#0E0A04", 0.8))
    e = T([(56, -17)])[0]
    out.append(f'<ellipse cx="{e[0]:.1f}" cy="{e[1]:.1f}" rx="{2.1 * s:.1f}" ry="{1.6 * s:.1f}" fill="#4A2A0E"/>')
    out.append(f'<ellipse cx="{e[0] + 0.3 * s:.1f}" cy="{e[1]:.1f}" rx="{1.0 * s:.1f}" ry="{1.0 * s:.1f}" fill="#0E0804"/>')
    out.append(f'<circle cx="{e[0] - 0.5 * s:.1f}" cy="{e[1] - 0.5 * s:.1f}" r="{0.35 * s:.1f}" fill="#FFFFFF" opacity="0.85"/>')
    out.append(K.taper(T([(53.5, -17.8), (56, -18.8), (58.5, -17.6)]), 2.2, 1.0, "#3A3220", 0.9))
    out.append(K.taper(T([(53, -19.5), (56, -20.2), (59, -19)]), 1.4, 0.6, "#E8D8A0", 0.6))
    # carapace
    top = [(-46, 2), (-48, -8), (-42, -22), (-30, -34), (-14, -41), (2, -42), (16, -37), (28, -26), (35, -12), (36, 0), (30, 4), (-40, 5)]
    cara = T(top)
    out.append(K.paint(D, cara, shell, seed + 20, round_r=26 * s, flow="contour", edge_col="#120802", edge_w=2.2, edge_op=0.8,
                       rim_col="#FFE2A0", rim_w=1.8, rim_op=0.6, passes=((40, (10, 20), (3, 5), (0.3, 0.5)),)))
    vol = K.Vol(cara, 26 * s)
    cid = D.clip(K.smooth_closed(cara))
    sc = []
    prof = K.resample(top[1:11], 2, closed=False)          # the dome profile from rear to front

    def top_y(x):
        best = min(prof, key=lambda p: abs(p[0] - x))
        return best[1]
    RIM = 2.0

    def P_(x, v):
        return (x, RIM - v * (RIM - top_y(x)))

    def plate(x0, x1, v0, v1):
        pts = [P_(x0 + (x1 - x0) * t / 4, v0) for t in range(5)] + [P_(x1, v0 + (v1 - v0) * t / 3) for t in range(1, 4)]
        pts += [P_(x1 - (x1 - x0) * t / 4, v1) for t in range(5)] + [P_(x0, v1 - (v1 - v0) * t / 3) for t in range(1, 3)]
        return pts
    plates = []
    xs = [-47, -39, -31, -23, -15, -7, 1, 9, 17, 25, 32, 37]
    plates += [(plate(a, b, 0.0, 0.17), 0.0) for a, b in zip(xs, xs[1:])]
    xs = [-47, -31, -12, 7, 23, 37]
    plates += [(plate(a, b, 0.17, 0.6), 0.08) for a, b in zip(xs, xs[1:])]
    xs = [-40, -24, -6, 12, 28]
    plates += [(plate(a, b, 0.6, 1.02), 0.14) for a, b in zip(xs, xs[1:])]
    for pts, lift in plates:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        c = T([(cx, cy)])[0]
        n = vol.normal(*c)
        base = shell.color(n, rnd, lift)
        PP = T(pts)
        g = D.rad([(0, K.mix(K.lt(base, 0.25), "#F0C878", 0.3)), (0.45, base), (1, K.dk(base, 0.35))], 0.5, 0.42, 0.6)
        sc.append(f'<path d="{K.poly_d(PP)}" fill="{g}"/>')
        for k in (0.78, 0.6, 0.42):
            q = T([(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts])
            sc.append(f'<path d="{K.poly_d(q)}" fill="none" stroke="#3A2008" stroke-width="0.6" opacity="0.4" stroke-linejoin="round"/>')
        q = T([(cx + (x - cx) * 0.25, cy + (y - cy) * 0.25 - 0.6) for x, y in pts])
        sc.append(f'<path d="{K.poly_d(q)}" fill="#F6D48A" opacity="0.45"/>')
        sc.append(f'<path d="{K.poly_d(PP)}" fill="none" stroke="#1A0C04" stroke-width="1.6" stroke-linejoin="round" opacity="0.85"/>')
    sc.append(K.taper(T([(-44, 2), (-10, 4), (34, 1)]), 3, 3, "#0A0602", 0.5, mid=5))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # near legs: thick scaled columns with claws
    for leg in (FORE, HIND):
        o = T(leg)
        out.append(K.paint(D, o, skin, seed + 30 + len(out), round_r=5 * s, flow="contour", edge_col="#0E0A04", edge_w=1.6, rim_col="#FFE8B8", rim_w=1.2,
                           passes=((100, (5, 10), (1.5, 3), (0.35, 0.6)), (300, (3, 6), (0.8, 1.5), (0.45, 0.85)))))
        vl = K.Vol(o, 5 * s)
        x0, y0, x1, y1 = K.bbox(o)
        cid2 = D.clip(K.smooth_closed(o))
        sl = []
        for yy in range(int(y0) + 3, int(y1) - 2, 5):
            for xx in range(int(x0) + 2, int(x1), 6):
                x, y = xx + (3 if (yy // 5) % 2 else 0) + rnd.uniform(-1, 1), yy + rnd.uniform(-1, 1)
                if vl.inside(x, y):
                    c_ = skin.color(vl.normal(x, y), rnd, 0.1)
                    sl.append(f'<path d="M{x - 3:.1f} {y + 1:.1f}q3 -5 6 0q-3 2.4 -6 0Z" fill="{c_}" stroke="#1A1408" stroke-width="0.6" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
        out.append(f'<g {cid2}>{"".join(sl)}</g>')
        xs = [p[0] for p in leg]
        for k in range(4):
            bx, by = T([(max(xs) - 1.5 - k * 3.2, 16.2)])[0]
            out.append(f'<path d="M{bx:.1f} {by - 2:.1f}q{1.6:.1f} 0.4 {2.6:.1f} 2.6" stroke="#E8DCB8" stroke-width="1.4" fill="none" stroke-linecap="round" opacity="0.85"/>')
    return "".join(out)


def hare_asleep_painted(D, ox, oy, s, seed, light=(-0.7, -0.6)):
    """A brown hare asleep in the grass: curled on its side, head on its forepaws, long black-tipped ears laid
    along its back, white belly fur, eye closed."""
    rnd = random.Random(seed)
    T = lambda pts: K.xform(pts, ox, oy, s)
    fur = K.Look(["#1E140C", "#3E2C1C", "#6A5034", "#967652", "#C2A27A", "#E8D0A8"], key=(light[0], light[1], 0.5), amb=0.08, wrap=0.4,
                 rim=("#FFE6B0", light, 0.6), jit=0.03)
    body = [(-42, 2), (-46, -8), (-42, -20), (-30, -28), (-12, -31), (4, -29), (16, -24), (24, -22), (32, -22), (40, -18), (46, -10), (46, -5),
            (40, -2), (34, 0), (24, 1), (8, 2), (-20, 3)]
    out = [K.halo(D, ox, oy + 2 * s, 56 * s, "#203010", 0.4, ry=6 * s)]
    hv = (-30, -12)
    out.append(K.paint(D, T(body), fur, seed, round_r=14 * s, bumps=[(*T([hv])[0], 16 * s, 14 * s, 0, 6 * s), (*T([(36, -12)])[0], 10 * s, 8 * s, 0, 3 * s)],
                       flow=lambda x, y, n: 170, flow_jit=18, edge_col="#140C06", edge_w=1.4, edge_op=0.6, rim_col="#FFE6B8", rim_w=1.2,
                       passes=((60, (6, 14), (1.6, 3), (0.35, 0.6)), (300, (3, 7), (0.7, 1.4), (0.45, 0.85)))))
    out.append(K.taper(T([(-30, 1.5), (-10, 0), (14, 0), (28, 0.5)]), 1.5 * s, 1.0 * s, "#E8DCC8", 0.5, mid=2.4 * s))
    # ears laid back along the back, black tips
    for k, (dy, da) in enumerate(((0, 0), (3, 8))):
        ear = [(26, -24), (16, -34 - dy), (2, -42 - dy - da * 0.4), (-8, -44 - dy - da * 0.6), (-4, -39 - dy), (8, -32 - dy), (20, -24)]
        out.append(K.paint(D, T(ear), fur.darker(0.18 * (1 - k)), seed + 2 + k, round_r=3 * s, flow=200, edge_col="#140C06", edge_w=1.3,
                           rim_col="#FFE6B8", rim_w=1.0, rim_op=0.6,
                           color_fn=lambda x, y, c, n: "#1A120C" if (x - ox) / s < -1 else c))
        if k == 1:
            out.append(K.taper(T([(20, -26), (8, -33), (-2, -38)]), 2.4, 0.6, "#E8B8A0", 0.5))
    # closed eye, nose, whiskers
    e = T([(34, -15)])[0]
    out.append(K.taper(T([(31, -15), (34, -13.8), (37, -15)]), 1.4, 1.4, "#140C06", 0.9))
    n_ = T([(45.5, -8)])[0]
    out.append(f'<ellipse cx="{n_[0]:.1f}" cy="{n_[1]:.1f}" rx="{1.4 * s:.1f}" ry="{1.0 * s:.1f}" fill="#3A2016"/>')
    for k in range(3):
        out.append(f'<path d="M{n_[0] - 2:.1f} {n_[1] + 1:.1f}q{8 + k * 3} {k * 3 - 2} {16 + k * 4} {k * 5 - 3}" stroke="#F8F0E0" stroke-width="0.6" fill="none" opacity="0.6"/>')
    # forepaws under the chin
    out.append(K.paint(D, T([(30, -2), (44, -2), (48, 1), (44, 3), (30, 2)]), fur.darker(-0.15), seed + 5, round_r=2 * s, flow=0, edge_col="#140C06", edge_w=1))
    # the white scut and the hind foot
    out.append(K.halo(D, *T([(-44, -14)])[0], 4.5 * s, "#FFFFFF", 0.9))
    out.append(K.paint(D, T([(-38, -2), (-20, -4), (-6, -2), (-8, 2), (-30, 3)]), fur.darker(0.05), seed + 6, round_r=2 * s, flow=180, edge_col="#140C06", edge_w=1))
    out.append(K.taper(T([(-28, -24), (-24, -12), (-30, -4)]), 1.6, 0.6, "#2A1A0E", 0.45))
    return "".join(out)


@plate("the-tortoise-and-the-hare", 52, edge=1.8, bristle=0.35, grain=0.18)
def tortoise_hare_plate():
    """Early morning: the tortoise plods along the dewy path, shell glowing in the low sun, while far behind him
    the hare sleeps under an old oak. The finishing post waits at the end of the lane."""
    D = K.Doc("tth")
    out = []
    out.append(K.sky(D, [(0, "#9CC0D8"), (0.5, "#D8DCC8"), (0.85, "#F6E2B0"), (1, "#FCE8B8")], 5201, 0, 380, n=160, op=(0.06, 0.16)))
    out.append(K.halo(D, 560, 320, 260, "#FFF2C8", 0.7))
    cl = K.Look(["#9AA6B8", "#C8CCD0", "#F0E8DA", "#FFF8EC"], key=(-0.8, -0.4, 0.4), amb=0.3, wrap=0.5)
    out.append(K.cumulus(D, [(400, 236, 20), (430, 228, 26), (462, 236, 20), (486, 240, 14)], cl, 5202, flat_y=246, dab_r=(3, 7), rim="#FFFFFF", rim_w=1.4))
    # rolling fields into the distance, hedgerows, the finishing post far away
    for k, (yb, col) in enumerate(((330, "#A8B888"), (350, "#8EA470"), (372, "#7A9458"))):
        ridge = K.rough([(-20, yb + 6), (150, yb - 10), (320, yb + 2), (470, yb - 12), (620, yb)], 5203 + k, 4, 10)
        out.append(f'<path d="{K.smooth_open(ridge)} L620 600 L-20 600Z" fill="{col}"/>')
        hl = K.Look(["#2A3A1A", "#4A6230", "#7A9050", "#A8B878"], key=(-0.8, -0.5, 0.5), amb=0.15)
        rr = random.Random(5206 + k)
        hedge = []
        x_ = rr.uniform(-20, 20)
        while x_ < 620:
            run = rr.uniform(30, 110)
            for xx in range(int(x_), int(x_ + run), 9):
                hedge.append((xx, K.y_on(ridge, xx) - 3 + rr.uniform(-2, 2) if hasattr(K, "y_on") else yb - 3, rr.uniform(5, 9) * (1 - k * 0.2), rr.uniform(4, 6)))
            x_ += run + rr.uniform(40, 120)
        if hedge:
            out.append(K.foliage(D, hedge, hl.darker(0.1 - k * 0.1), 5206 + k, size=(1.2, 3.0), density=1.2))
    # meadow
    gr = D.lin([(0, "#7E9A4E"), (0.5, "#5E7E36"), (1, "#3A5A22")], 0, 380, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 384 Q300 372 610 386 V610 H-10Z" fill="{gr}"/>')
    # the lane: a pale earth track curving from foreground into the distance
    lane = [(-10, 520), (120, 500), (260, 470), (380, 430), (470, 398), (540, 380), (600, 372), (600, 384), (548, 394), (480, 414), (396, 448),
            (290, 494), (150, 540), (-10, 580)]
    out.append(f'<path d="{K.smooth_closed(lane)}" fill="{D.lin([(0, "#C8A878"), (1, "#E8D0A0")], 0, 0, 1, 0)}"/>')
    out.append(K.brushwork(5210, (-10, 370, 610, 600), ["#B89868", "#E8D8B0", "#8A7048"], 160, L=(8, 26), W=(1, 2.4), op=(0.25, 0.55), angle=-12, jit=8,
                           inside=lambda x, y: K.Vol(lane, 2).inside(x, y) if False else (y > 372 + (600 - x) * 0.0) and False))
    # finishing post with a red ribbon far down the lane
    out.append(f'<path d="M552 386V350M572 386V350" stroke="#5A3A20" stroke-width="2.4"/>')
    out.append(f'<path d="M552 356Q562 361 572 356" stroke="#C8283A" stroke-width="2.2" fill="none"/>')
    out.append(f'<path d="M562 356l-3 9M562 356l4 8" stroke="#C8283A" stroke-width="1.6"/>')
    # the old oak and the hare asleep in its shade
    bark = K.Look(["#1A1410", "#2E2620", "#4A3E32", "#6E604C", "#9A8A70"], key=(-0.8, -0.5, 0.5), amb=0.1, wrap=0.3)
    trunk = K.limb_outline([(120, 436, 40), (116, 380, 30), (122, 330, 26), (112, 280, 20)], cap=0.2)
    out.append(K.halo(D, 120, 438, 150, "#1A2A0E", 0.45, ry=18))
    out.append(K.paint(D, trunk, bark, 5220, round_r=14, flow=92, flow_jit=8, edge_col="#0A0806", edge_w=1.6))
    for bpts in ([(112, 300), (70, 262), (30, 246)], [(118, 300), (160, 256), (210, 240)], [(116, 290), (120, 240), (136, 200)]):
        out.append(K.taper(bpts, 12, 4, "#2E2620", 1))
    oak = K.Look(["#142410", "#24401A", "#3C5E26", "#5E7E36", "#8EA454", "#C8CC80"], key=(-0.8, -0.5, 0.5), amb=0.06, wrap=0.35, jit=0.05)
    out.append(K.foliage(D, [(120, 236, 76, 48), (50, 262, 52, 34), (196, 256, 60, 38), (90, 200, 50, 34), (160, 204, 46, 32),
                             (10, 284, 34, 22), (240, 280, 34, 24)], oak, 5221, density=1.3, size=(2.5, 6.5), holes="#D8DCC0", hole_n=40))
    out.append(hare_asleep_painted(D, 116, 432, 1.45, 5230))
    out.append(K.grass(5231, (40, 420, 200, 442), ["#3A5A22", "#6E8E3E", "#9AB45A"], n=70, h=(6, 14), w=(1, 1.8), lean=(-0.3, 0.3)))
    # foreground: dew-heavy grass and wildflowers
    out.append(K.grass(5240, (-10, 440, 610, 610), lambda x, y, r: r.choice(["#2E4A1A", "#4E6E2A", "#7A9A44", "#A8C066"]), n=420, h=(12, 34),
                       w=(1.2, 2.6), lean=(-0.4, 0.4)))
    rnd = random.Random(5241)
    for _ in range(26):
        x, y = rnd.uniform(0, 600), rnd.uniform(440, 600)
        if 200 < x < 500 and y < 520:
            continue
        c = rnd.choice(["#FFFFFF", "#F8E070", "#E8A0C0", "#A8C0F0"])
        out.append(K.taper([(x, y + 12), (x + rnd.uniform(-3, 3), y)], 1.2, 0.8, "#3A5A22", 0.9))
        for k in range(5):
            a = k * 1.256 + rnd.uniform(0, 0.4)
            out.append(f'<ellipse cx="{x + math.cos(a) * 2.6:.1f}" cy="{y + math.sin(a) * 2.6:.1f}" rx="2.2" ry="1.3" fill="{c}" transform="rotate({math.degrees(a):.0f} {x + math.cos(a) * 2.6:.1f} {y + math.sin(a) * 2.6:.1f})"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#E8A020"/>')
    # the tortoise: hero, plodding along the lane toward the post, long morning shadow behind him
    out.append(K.halo(D, 316, 506, 130, "#1A2410", 0.45, ry=12))
    out.append(tortoise_painted(D, 330, 464, 2.6, 5250))
    out.append(K.grass(5251, (210, 500, 480, 514), ["#4E6E2A", "#7A9A44", "#A8C066"], n=40, h=(6, 14), w=(1.2, 2.2), lean=(-0.3, 0.3)))
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(450, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    art = D.render(out)
    DL = K.Doc("tthL")
    L = [K.halo(DL, 300, 96, 240, "#FFF8E8", 0.55, ry=56)]
    L.append(K.title(DL, 300, 104, "Slow and steady", SERIF_IT, 56, max_w=440, face=("#6A4A1E", "#4A3012", "#2A1A08"), shadow="#FFF6E0", sop=0.8))
    L.append(K.subtitle(300, 140, "wins the race.", SERIF_IT, 28, "#4A3012", max_w=300, sh="#FFF6E0", sop=0.7))
    L.append(K.halo(DL, 300, 534, 230, "#1A2A0E", 0.5, ry=26))
    L.append(K.subtitle(300, 540, "THE TORTOISE AND THE HARE · AESOP", CINZEL, 15, "#FFF4D8", ls=2.5, max_w=400, sh="#0E1808", sop=0.8))
    return art, DL.render(L)
# ---- end plate: the-tortoise-and-the-hare ----


# ---- plate: the-ugly-duckling ----
SWAN_BODY = [(-56, -9), (-50, -3), (-40, 0), (0, 1), (30, 0), (40, -4), (45, -12), (44, -22), (45, -34), (43, -48), (37, -60), (35, -70), (38, -78),
             (43, -81), (48, -81), (53, -79.5), (59, -76.5), (58.5, -74.5), (52, -75), (47, -75.5), (49, -77), (47, -86), (41, -91),
             (34, -89), (29, -80), (28, -68), (31, -55), (34, -42), (32, -30), (24, -20), (10, -18), (-10, -16), (-30, -14), (-46, -12)]
SWAN_WING = [(24, -18), (16, -32), (4, -43), (-12, -48), (-28, -46), (-40, -38), (-47, -33), (-44, -30), (-52, -26), (-49, -22), (-57, -18), (-53, -14), (-60, -10), (-46, -9), (-30, -10), (-8, -12), (12, -14)]


def swan_painted(D, ox, oy, s, seed, look, flip=False, reflect=None):
    """A mute swan afloat, wings half-raised over the back ('busking'), neck in a long S, head bowed: white plumage
    modelled by the light, layered wing feathers, orange bill with the black knob. reflect = (water y, colour)."""
    rnd = random.Random(seed)
    T = lambda pts: K.xform(pts, ox, oy, s, 0, flip)
    out = []
    body = T(SWAN_BODY)
    bm = [(*T([(10, -10)])[0], 44 * s, 12 * s, 0, 6 * s), (*T([(40, -84)])[0], 7 * s, 6 * s, 0, 3 * s)]
    out.append(K.paint(D, body, look, seed, round_r=10 * s, bumps=bm, flow="contour", flow_jit=10, edge_col="#3A3A5A", edge_w=1.6, edge_op=0.55,
                       rim_col="#FFE8B8", rim_w=1.6, rim_op=0.6,
                       passes=((50, (14, 28), (3, 6), (0.3, 0.5)), (220, (8, 16), (1.2, 2.6), (0.3, 0.6)), (80, (4, 8), (0.7, 1.4), (0.35, 0.65)))))
    # the raised wing: rows of feathers from the shoulder back, each row lit on top
    wing = T(SWAN_WING)
    out.append(K.paint(D, wing, look.darker(-0.04), seed + 1, round_r=12 * s, flow="contour", flow_jit=8, edge_col="#3A3A5A", edge_w=1.4,
                       edge_op=0.45, rim_col="#FFE8B8", rim_w=1.8, rim_op=0.7, passes=((50, (12, 24), (3, 6), (0.3, 0.55)), (220, (5, 12), (1, 2.2), (0.35, 0.7)))))
    cid = D.clip(K.smooth_closed(wing))
    fe = []
    # long feathers sweeping from the shoulder back to the cascading tips: soft shadow lines, light along their tops
    for k in range(9):
        t = k / 8
        y0 = -18 - 22 * t
        pts = [(18 - 10 * t, y0), (0 - 6 * t, y0 - 14 + 8 * t), (-22 - 4 * t, y0 - 10 + 12 * t), (-40 - 8 * t * 0 - 6, -20 - 10 * t + 4)]
        P = T(pts)
        fe.append(f'<path d="{K.smooth_open(P)}" fill="none" stroke="#8A8EB8" stroke-width="1.3" opacity="{0.22 + 0.1 * (k % 2):.2f}"/>')
        fe.append(f'<path d="{K.smooth_open([(x - 0.6, y - 1.4) for x, y in P])}" fill="none" stroke="#FFFFFF" stroke-width="1.0" opacity="0.4"/>')
    # the cascade of feather tips at the back: each a soft rounded tip with a shadow beneath
    for (tx_, ty_) in ((-44, -31), (-49, -24.5), (-54, -17), (-57, -11)):
        P = T([(tx_ + 10, ty_ - 3), (tx_ + 2, ty_ - 1.5), (tx_ - 1, ty_ + 1.5), (tx_ + 6, ty_ + 3)])
        fe.append(f'<path d="{K.smooth_open(P)}" fill="none" stroke="#6E72A0" stroke-width="1.4" opacity="0.4"/>')
    out.append(f'<g {cid}>{"".join(fe)}</g>')
    # bill: orange with black nail, black knob and lores
    bill = T([(47, -81.5), (53, -80), (59, -76.8), (58.4, -74.8), (52, -75.6), (47.5, -76.5)])
    out.append(f'<path d="{K.smooth_closed(bill)}" fill="{D.lin([(0, "#F09040"), (1, "#C05010")], 0, 0, 0, 1)}" stroke="#4A1A06" stroke-width="0.8"/>')
    out.append(f'<path d="{K.smooth_closed(T([(44, -83.5), (48, -86), (50, -82), (47.5, -80)]))}" fill="#14100E"/>')
    out.append(f'<path d="{K.smooth_closed(T([(57.4, -77.6), (59.2, -76.6), (58.6, -75), (57, -75.4)]))}" fill="#14100E"/>')
    out.append(K.taper(T([(49, -80.5), (54, -79), (58, -77)]), 1.0, 0.4, "#FFD0A0", 0.7))
    e = T([(43.2, -84.2)])[0]
    out.append(f'<circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="{1.1 * s:.1f}" fill="#0A0806"/>')
    out.append(f'<circle cx="{e[0] - 0.3 * s:.1f}" cy="{e[1] - 0.3 * s:.1f}" r="{0.35 * s:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@plate("the-ugly-duckling", 33, edge=1.8, bristle=0.3, grain=0.16)
def ugly_duckling_plate():
    """A still lake at sunrise, mist lifting off the water: the grown swan glides out of the reeds and meets its
    own reflection. Andersen's ending, told in light."""
    D = K.Doc("udk")
    out = []
    WY = 352
    out.append(K.sky(D, [(0, "#9AB0CC"), (0.45, "#D8C8D0"), (0.8, "#F6D8B8"), (1, "#FCE6C4")], 3301, 0, WY, n=150, op=(0.05, 0.14)))
    SX = 420
    out.append(K.halo(D, SX, WY - 40, 220, "#FFF0D0", 0.75))
    out.append(f'<circle cx="{SX}" cy="{WY - 46}" r="22" fill="#FFF8E4" opacity="0.9"/>')
    # far shore: soft tree line in the mist, two layers
    for k, (y0, col, op) in enumerate(((WY - 34, "#8A8AA0", 0.55), (WY - 14, "#5E667E", 0.75))):
        rr = random.Random(3302 + k)
        blobs = []
        x = -20
        while x < 620:
            w = rr.uniform(14, 34)
            blobs.append((x, y0 - rr.uniform(0, 34 - k * 10), w, rr.uniform(20, 36 - k * 8)))
            x += w * 0.9
        fl = K.Look([K.dk(col, 0.15), col, K.lt(col, 0.2)], key=(0.7, -0.5, 0.5), amb=0.3)
        out.append(K.foliage(D, blobs, fl, 3303 + k, size=(2, 5), density=0.8, op=(0.3, 0.6)))
        out.append(f'<rect x="-10" y="{y0:.0f}" width="620" height="{WY - y0 + 2:.0f}" fill="{col}" opacity="{op}"/>')
    out.append(K.mist(D, WY - 6, 20, "#FFF2E6", 0.6, seed=3305, n=10, r=(100, 200)))
    # water: still, catching the sky, the sun path, lily pads
    out.append(K.water(D, WY, 600, [(0, "#E8D4C8"), (0.25, "#B8B4C8"), (0.7, "#7E8AA8"), (1, "#4E5A7A")], 3306, n=420, refl_x=SX, refl_w=34,
                       refl_col="#FFF0D0", glints=160))
    look = K.Look(["#4A4E78", "#6E749E", "#A4A8C8", "#D8D8E6", "#F4EEEC", "#FFF8EC", "#FFFFFF"], key=(0.75, -0.55, 0.45), amb=0.14, wrap=0.5,
                  rim=("#FFE0A8", (0.8, -0.5), 0.75), bounce=("#9AA8D0", 0.4), jit=0.008)
    ox, oy, s = 282, WY + 80, 3.1
    # reflection first: the swan mirrored under the waterline, darker and broken by ripples
    rD = swan_painted(D, ox, oy, s, 3310, look.darker(0.18))
    cidr = D.clip(f"M-10 {oy:.0f}H610V610H-10Z")
    out.append(f'<g {cidr} opacity="0.55"><g transform="translate(0 {2 * oy:.0f}) scale(1 -1)">{rD}</g></g>')
    rnd = random.Random(3311)
    rip = []
    for _ in range(140):
        y = oy + rnd.uniform(2, 260)
        x = ox + rnd.uniform(-200, 220)
        rip.append(K.stroke(x, y, 0, rnd.uniform(14, 60), rnd.uniform(0.5, 1.6), rnd.choice(["#E8E0E0", "#6A7090", "#C8C4D4"]), rnd.uniform(0.25, 0.55)))
    out.append("".join(rip))
    # ripples spreading from the breast
    for k in range(4):
        out.append(f'<ellipse cx="{ox + 120:.0f}" cy="{oy + 2:.0f}" rx="{30 + k * 26}" ry="{3 + k * 2.4:.1f}" fill="none" stroke="#FFF4E0" stroke-width="1.2" opacity="{0.5 - k * 0.1:.2f}"/>')
    # reeds and cattails, left and right
    reed = ["#3A4A2A", "#5A6A3A", "#8A8A54", "#B8A870"]
    for side, x0, x1 in ((-1, -10, 120), (1, 470, 610)):
        rr = random.Random(3320 + side)
        for _ in range(26):
            x = rr.uniform(x0, x1)
            base = rr.uniform(WY + 40, 470)
            h = rr.uniform(90, 220)
            lean = rr.uniform(-0.15, 0.15) + side * -0.05
            pts = [(x, base), (x + lean * h * 0.4, base - h * 0.5), (x + lean * h, base - h)]
            out.append(K.taper(pts, rr.uniform(3, 6), 0.4, rr.choice(reed), 0.95))
            if rr.random() < 0.3:
                tx_, ty_ = pts[-1]
                out.append(K.taper([(tx_ - lean * 30, ty_ + 30), (tx_ - lean * 16, ty_ + 14)], 7, 6, "#4A2A14", 1))
        for _ in range(10):
            x = rr.uniform(x0, x1)
            base = rr.uniform(WY + 60, 480)
            out.append(K.taper([(x, base), (x + side * -rr.uniform(10, 40), base - rr.uniform(30, 70))], rr.uniform(5, 9), 0.5, rr.choice(reed[:2]), 0.9))
    # lily pads with a pink bloom
    for (lx_, ly_, r_) in ((150, 470, 22), (186, 486, 16), (420, 500, 26), (470, 470, 14)):
        out.append(f'<ellipse cx="{lx_}" cy="{ly_}" rx="{r_}" ry="{r_ * 0.32:.1f}" fill="#4E6A3A"/>')
        out.append(f'<ellipse cx="{lx_}" cy="{ly_ - 1}" rx="{r_ * 0.85:.1f}" ry="{r_ * 0.22:.1f}" fill="#7A9A54" opacity="0.6"/>')
        out.append(f'<path d="M{lx_} {ly_}L{lx_ + r_ * 0.9:.1f} {ly_ - r_ * 0.12:.1f}" stroke="#2E4422" stroke-width="1.2"/>')
    for k in range(7):
        a = -math.pi * (0.1 + 0.8 * k / 6)
        out.append(f'<ellipse cx="{188 + math.cos(a) * 5:.1f}" cy="{480 + math.sin(a) * 4:.1f}" rx="5" ry="2.2" fill="#F6C8D0" transform="rotate({math.degrees(a):.0f} {188 + math.cos(a) * 5:.1f} {480 + math.sin(a) * 4:.1f})"/>')
    # the swan
    out.append(swan_painted(D, ox, oy, s, 3310, look))
    out.append(K.halo(D, ox + 20, oy + 3, 180, "#5A6080", 0.25, ry=6))
    art = D.render(out)
    DL = K.Doc("udkL")
    L = [K.halo(DL, 300, 92, 240, "#FFF6EC", 0.55, ry=52)]
    L.append(K.title(DL, 300, 100, "The Ugly Duckling", SERIF_IT, 52, max_w=440, face=("#5A6A9A", "#3A4A7A", "#1E2A50"), shadow="#FFF8F0", sop=0.8))
    L.append(K.subtitle(300, 128, "HANS CHRISTIAN ANDERSEN · 1843", CINZEL, 15, "#3A4A6A", ls=2.5, max_w=380, sh="#FFF8F0", sop=0.6))
    L.append(K.halo(DL, 300, 528, 220, "#2A3450", 0.45, ry=30))
    L.append(K.subtitle(300, 536, "He was a swan all along.", SERIF_IT, 26, "#FFF6E6", max_w=420, sh="#1A2038", sop=0.7))
    return art, DL.render(L)
# ---- end plate: the-ugly-duckling ----


# ---- plate: the-frog-prince ----
def _frog_rot(pts, a=-20, o=(-22, -6)):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return [(o[0] + (x - o[0]) * c - (y - o[1]) * s, o[1] + (x - o[0]) * s + (y - o[1]) * c) for x, y in pts]


FROG = dict(
    body=_frog_rot([(37, -19), (35, -23), (30, -25), (24, -28), (16, -29), (6, -29), (-6, -30), (-16, -31), (-24, -27), (-29, -20), (-30, -12),
                    (-26, -6), (-12, -4), (4, -4), (14, -6), (22, -10), (30, -14), (35, -16)]),
    eye=_frog_rot([(17, -27), (19, -32), (24, -34), (29, -31), (29, -27), (24, -25)]),
    thigh=[(-24, -14), (-12, -14), (0, -10), (8, -5), (7, -1), (-4, -1), (-18, -3), (-28, -6), (-29, -11)],
    shin=[(6, -5), (8, -2), (-4, 0), (-22, 0.5), (-30, -1.5), (-28, -5), (-14, -4)],
    foot=[(-28, -1), (-20, 0.5), (-6, 1), (8, 1), (18, 1.5), (20, 3), (8, 3.4), (-10, 3), (-26, 2.4)],
    fore=[(10, -20), (16, -20), (19, -12), (20, -3), (25, 1), (23, 2.6), (17, 2.2), (14, 1), (13, -9)],
)


def frog_painted(D, ox, oy, s, seed, light=(0.6, -0.7), flip=False, crown=True):
    """A common frog sitting up: blunt snout, high golden eye with a horizontal pupil and a heavy lid, eardrum,
    dorsolateral fold, mottled olive skin with dark blotches and warts, pale throat, folded hind leg (thigh,
    shin, long webbed foot), slim foreleg propping the chest."""
    rnd = random.Random(seed)
    T = lambda pts: K.xform(pts, ox, oy, s, 0, flip)
    lx, ly = light
    skin = K.Look(["#141C08", "#28380E", "#46581A", "#6A7A2A", "#94A044", "#C4C878", "#ECE8B0"], key=(lx, ly, 0.5), amb=0.06, wrap=0.35,
                  rim=("#FFE8A0", (lx, ly), 0.55), spec=("#FFFFF0", 0.86, 0.6), jit=0.03)
    belly = K.Look(["#6A6448", "#A89E78", "#DCD2A8", "#F4EED0"], key=(lx, ly, 0.5), amb=0.2)
    out = []
    # far legs, darker
    out.append(K.paint(D, T([(x + 4, y - 1) for x, y in FROG["fore"]]), skin.darker(0.35), seed + 1, round_r=3 * s, flow="contour", edge_col="#0A0E04"))
    blotch_pts = [(rnd.uniform(-28, 28), rnd.uniform(-40, -10), rnd.uniform(2, 4.5)) for _ in range(26)]

    def blotch(x, y, c, n):
        lx_, ly_ = (x - ox) / s * (-1 if flip else 1), (y - oy) / s
        for (bx, by, br) in blotch_pts:
            if (lx_ - bx) ** 2 + (ly_ - by) ** 2 < br * br:
                return K.mix(c, "#2A1E0C", 0.55)
        return c
    body = T(FROG["body"])
    bm = [(*T([(14, -38)])[0], 12 * s, 8 * s, 0, 3 * s), (*T([(-18, -26)])[0], 14 * s, 10 * s, 0, 4 * s)]
    out.append(K.paint(D, body, skin, seed + 2, round_r=10 * s, bumps=bm, flow="contour", flow_jit=14, color_fn=blotch, edge_col="#0E1404",
                       edge_w=1.8, edge_op=0.7, rim_col="#FFF0B0", rim_w=1.4, rim_op=0.6,
                       passes=((60, (6, 14), (2, 4), (0.3, 0.55)), (300, (3, 7), (0.8, 1.8), (0.4, 0.8)))))
    # pale throat and belly
    thr = _frog_rot([(35, -16.5), (30, -14), (22, -10), (14, -6.5), (8, -6), (12, -9), (20, -13), (28, -16.5)])
    out.append(K.paint(D, T(thr), belly, seed + 3, round_r=2 * s, flow="contour", edge_col=None))
    # warts and the light dorsolateral fold
    for (bx, by, br) in blotch_pts:
        pass
    for _ in range(46):
        x, y = rnd.uniform(-30, 34), rnd.uniform(-44, -8)
        p = T([(x, y)])[0]
        if K.Vol(body, 4).inside(*p) if False else True:
            pass
    vb = K.Vol(body, 10 * s)
    for _ in range(60):
        x, y = rnd.uniform(-30, 34), rnd.uniform(-44, -8)
        p = T([(x, y)])[0]
        if vb.inside(*p):
            n = vb.normal(*p)
            c = skin.color(n, rnd, 0.12)
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{rnd.uniform(0.6, 1.3) * s * 0.5:.1f}" fill="{c}" opacity="0.8"/>')
            out.append(f'<circle cx="{p[0] - lx * 0.6:.1f}" cy="{p[1] - ly * 0.6:.1f}" r="{0.3 * s:.1f}" fill="#F8F4D0" opacity="0.5"/>')
    fold = T(_frog_rot([(14, -27.5), (2, -28), (-10, -28.6), (-20, -27)]))
    out.append(K.taper(fold, 1.4 * s * 0.5, 0.6, "#D8D49A", 0.7))
    # mouth line, nostril, eardrum
    out.append(K.taper(T(_frog_rot([(36, -18), (28, -16.4), (20, -15.5), (14, -16.5)])), 1.4, 0.8, "#0A0E04", 0.8))
    nst = T(_frog_rot([(31, -23.5)]))[0]
    out.append(f'<ellipse cx="{nst[0]:.1f}" cy="{nst[1]:.1f}" rx="{0.7 * s:.1f}" ry="{0.4 * s:.1f}" fill="#0A0E04"/>')
    ty_ = T(_frog_rot([(12, -22)]))[0]
    out.append(f'<circle cx="{ty_[0]:.1f}" cy="{ty_[1]:.1f}" r="{3.6 * s:.1f}" fill="{D.rad([(0, "#8A6A3A"), (0.8, "#5A4220"), (1, "#2A1E0C")])}" opacity="0.85"/>')
    out.append(K.taper(T(_frog_rot([(9, -24.5), (12, -25.6), (15, -24.2)])), 1.0, 0.4, "#E8D8A0", 0.6))
    # hind leg folded along the side, the long webbed foot on the ground; then the near foreleg
    for part_, sd in ((FROG["shin"], 5), (FROG["foot"], 6), (FROG["thigh"], 7)):
        out.append(K.paint(D, T(part_), skin.darker(0.05), seed + sd, round_r=4 * s, flow="contour", flow_jit=10, color_fn=blotch, edge_col="#0E1404",
                           edge_w=1.5, edge_op=0.7, rim_col="#FFF0B0", rim_w=1.2, rim_op=0.5,
                           passes=((80, (5, 12), (1.6, 3.2), (0.3, 0.55)), (300, (3, 6), (0.8, 1.6), (0.4, 0.8)))))
    for k in range(4):                          # thigh bars, the frog's banded legs
        p = T([(-20 + k * 7, -12 + k * 2), (-17 + k * 7, -5 + k * 1)])
        out.append(K.taper(p, 2.2 * s * 0.5, 1.2, "#2A2008", 0.45))
    for k in range(5):                          # webbed toes
        base = T([(8, 2)])[0]
        tip = T([(14 + k * 1.6, 1.6 + k * 0.7)])[0]
        out.append(K.taper([base, tip], 1.4, 0.6, "#1E2808", 0.6))
    out.append(K.paint(D, T(FROG["fore"]), skin, seed + 8, round_r=3 * s, flow="contour", color_fn=blotch, edge_col="#0E1404", edge_w=1.4,
                       rim_col="#FFF0B0", rim_w=1.2, rim_op=0.5, passes=((80, (5, 10), (1.5, 3), (0.3, 0.55)), (300, (3, 6), (0.8, 1.5), (0.4, 0.8)))))
    for k in range(4):
        b = T([(22, 1.4)])[0]
        t = T([(22 + (k - 1.5) * 2.4, 3.4 + abs(k - 1.5) * 0.3)])[0]
        out.append(K.taper([b, t], 1.2, 0.8, "#2A3410", 0.7))
        out.append(f'<circle cx="{t[0]:.1f}" cy="{t[1]:.1f}" r="{0.55 * s:.1f}" fill="#4A5420"/>')
    # the eye: golden iris, horizontal pupil, a heavy lid, wet highlight
    E = T(FROG["eye"])
    out.append(K.paint(D, E, skin.darker(-0.05), seed + 9, round_r=3 * s, flow="contour", edge_col="#0E1404", edge_w=1.2))
    ec = T(_frog_rot([(23.5, -30)]))[0]
    r_ = 3.6 * s
    out.append(f'<circle cx="{ec[0]:.1f}" cy="{ec[1]:.1f}" r="{r_:.1f}" fill="{D.rad([(0, "#F8D86A"), (0.6, "#D89A2A"), (1, "#6A4210")])}"/>')
    for k in range(10):
        a = k * 0.628
        out.append(f'<path d="M{ec[0] + math.cos(a) * r_ * 0.45:.1f} {ec[1] + math.sin(a) * r_ * 0.45:.1f}L{ec[0] + math.cos(a) * r_ * 0.9:.1f} {ec[1] + math.sin(a) * r_ * 0.9:.1f}" stroke="#8A5A14" stroke-width="0.7" opacity="0.6"/>')
    out.append(f'<ellipse cx="{ec[0]:.1f}" cy="{ec[1]:.1f}" rx="{r_ * 0.62:.1f}" ry="{r_ * 0.28:.1f}" fill="#060402" transform="rotate(-12 {ec[0]:.1f} {ec[1]:.1f})"/>')
    out.append(f'<path d="M{ec[0] - r_ * 1.1:.1f} {ec[1] - r_ * 0.2:.1f}Q{ec[0]:.1f} {ec[1] - r_ * 1.5:.1f} {ec[0] + r_ * 1.1:.1f} {ec[1] - r_ * 0.4:.1f}" stroke="#2A3410" stroke-width="{1.6 * s * 0.5:.1f}" fill="none" opacity="0.8"/>')
    out.append(f'<ellipse cx="{ec[0] + r_ * 0.35:.1f}" cy="{ec[1] - r_ * 0.45:.1f}" rx="{r_ * 0.28:.1f}" ry="{r_ * 0.16:.1f}" fill="#FFFFFF" opacity="0.9" transform="rotate(-25 {ec[0]:.1f} {ec[1]:.1f})"/>')
    if crown:
        # a small gold crown, slightly askew, set behind the eye
        cx, cy = T(_frog_rot([(10, -29.8)]))[0]
        w, h = 9.5 * s, 7.6 * s
        a = -14
        pts = [(-w / 2, 0), (-w / 2, -h * 0.55), (-w * 0.3, -h * 0.2), (-w * 0.1, -h), (w * 0.08, -h * 0.25), (w * 0.28, -h * 0.9), (w * 0.38, -h * 0.2),
               (w / 2, -h * 0.6), (w / 2, 0)]
        P = K.xform(pts, cx, cy, 1, a)
        out.append(f'<path d="{K.poly_d(K.xform([(x, y + h * 0.2) for x, y in pts], cx + 2, cy + 3, 1, a))}" fill="#0A0E04" opacity="0.35"/>')
        g = D.lin([(0, "#FFF2B0"), (0.45, "#E8B640"), (1, "#8A5A10")], 0, 0, 0.3, 1)
        out.append(f'<path d="{K.poly_d(P)}" fill="{g}" stroke="#5A3A08" stroke-width="1" stroke-linejoin="round"/>')
        band = K.xform([(-w / 2, -h * 0.05), (w / 2, -h * 0.05), (w / 2, -h * 0.28), (-w / 2, -h * 0.28)], cx, cy, 1, a)
        out.append(f'<path d="{K.poly_d(band)}" fill="#C8902A" stroke="#5A3A08" stroke-width="0.7"/>')
        for (u, col) in ((-0.25, "#C8203A"), (0.05, "#2A6AC8"), (0.32, "#C8203A")):
            q = K.xform([(w * u, -h * 0.16)], cx, cy, 1, a)[0]
            out.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{0.8 * s * 0.6:.1f}" fill="{col}"/>')
        for (u, v) in ((-0.1, -1), (0.28, -0.9), (-0.5, -0.55), (0.5, -0.6)):
            q = K.xform([(w * u, h * v)], cx, cy, 1, a)[0]
            out.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{0.7 * s * 0.6:.1f}" fill="#FFF4C0"/>')
        hl = K.xform([(-w * 0.4, -h * 0.4), (-w * 0.15, -h * 0.85)], cx, cy, 1, a)
        out.append(K.taper(hl, 1.2, 0.4, "#FFFCE0", 0.8))
    return "".join(out)


@plate("the-frog-prince", 91, edge=1.8, bristle=0.35, grain=0.18)
def frog_prince_plate():
    """Dusk in the old forest by the king's castle: a mossy well under the lime tree, a frog with a little crown
    on its rim, and the princess's golden ball shining in the moss."""
    D = K.Doc("frp")
    out = []
    out.append(K.sky(D, [(0, "#0E1E24"), (0.5, "#1E3A3A"), (1, "#3A5A44")], 9101, 0, 600, n=120, op=(0.05, 0.14)))
    # deep forest: layers of trunks fading into blue-green haze, light from a clearing at the back
    out.append(K.halo(D, 330, 300, 260, "#C8D8A0", 0.35))
    bark = K.Look(["#0A100C", "#16201A", "#26342A", "#3A4A3C", "#5A6A54"], key=(-0.5, -0.6, 0.5), amb=0.1, wrap=0.3)
    rnd = random.Random(9102)
    for layer, (n, col_t, w0) in enumerate(((7, 0.55, 18), (5, 0.3, 30))):
        lk = bark.toward("#5A7A6A", col_t)
        for i in range(n):
            x = rnd.uniform(-20, 620)
            if layer == 1 and 170 < x < 430:
                continue
            out.append(K.paint(D, K.limb_outline([(x, 620, w0 * 1.3), (x + rnd.uniform(-10, 10), 300, w0), (x + rnd.uniform(-20, 20), -20, w0 * 0.8)], cap=0.1),
                               lk, 9103 + layer * 20 + i, round_r=w0 * 0.5, flow=90, flow_jit=4, edge_col=None, smooth=True,
                               passes=((40, (20, 40), (3, 6), (0.3, 0.5)),)))
        out.append(K.mist(D, 380, 120, "#4A6A5A", 0.45 - layer * 0.15, seed=9110 + layer, n=8))
    # canopy of the lime tree overhead: heart-shaped leaves in dark masses, lit edges
    leaf = K.Look(["#0A160C", "#142A16", "#244424", "#3A6232", "#6A8E48", "#A8C070"], key=(-0.4, -0.8, 0.5), amb=0.05, wrap=0.3, jit=0.05)
    out.append(K.foliage(D, [(80, 30, 160, 70), (300, 0, 200, 60), (520, 30, 160, 80), (600, 140, 60, 80), (-10, 150, 60, 70)], leaf, 9120,
                         density=1.0, size=(4, 9), holes="#3A5A44", hole_n=60))
    # ground: moss and ferns
    gr = D.lin([(0, "#2A4026"), (1, "#121E10")], 0, 400, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 420 Q300 400 610 424 V610 H-10Z" fill="{gr}"/>')
    out.append(K.brushwork(9121, (-10, 410, 610, 600), ["#3A5A2A", "#5A7A3A", "#1E3018", "#7A9A4A"], 300, L=(6, 16), W=(1.2, 3), op=(0.3, 0.7), angle=-10, jit=30))
    # the well: a round wall of mossy stones, dark water inside, the rim the frog sits on
    WX, WY, WR, WRY = 238, 372, 160, 44
    stone = K.Look(["#0E100E", "#1E201C", "#32342C", "#4A4A40", "#6A6858", "#8E8A74"], key=(0.5, -0.8, 0.5), amb=0.08, wrap=0.35, jit=0.08)
    front = [(WX - WR, WY), (WX - WR, WY + 92)] + [(WX + math.cos(a) * WR, WY + 92 + math.sin(a) * WRY) for a in [math.pi - k * math.pi / 20 for k in range(21)]][::-1][::-1] + [(WX + WR, WY)]
    front = [(WX - WR, WY)] + [(WX - WR * math.cos(k * math.pi / 20), WY + 92 + WRY * math.sin(k * math.pi / 20)) for k in range(21)] + [(WX + WR, WY)] + \
            [(WX + WR * math.cos(k * math.pi / 20), WY + WRY * math.sin(k * math.pi / 20)) for k in range(21)]
    out.append(f'<path d="{K.poly_d(front)}" fill="#2A2C26"/>')
    cid = D.clip(K.poly_d(front))
    st = []
    for row in range(7):
        yb = WY + 4 + row * 13 + rnd.uniform(-1, 1)
        a = rnd.uniform(-0.08, 0.02)
        while a < math.pi:
            da = rnd.uniform(0.16, 0.34)
            a0, a1 = a, min(math.pi + 0.1, a + da)
            hh = rnd.uniform(10, 14)
            P = []
            for k in range(5):
                t = a0 + (a1 - a0) * k / 4
                P.append((WX - WR * math.cos(t), yb + WRY * math.sin(t) + rnd.uniform(-0.6, 0.6)))
            P += [(x + rnd.uniform(-0.8, 0.8), y + hh + rnd.uniform(-1, 1)) for x, y in P[::-1]]
            mid = (sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P))
            n_ = (-(mid[0] - WX) / WR * 0.85, -0.1, 0.55)
            c = stone.color(K.norm3(n_), rnd, rnd.uniform(-0.08, 0.06))
            st.append(f'<path d="{K.smooth_closed(P)}" fill="{c}" stroke="#080A08" stroke-width="1.6"/>')
            st.append(K.taper(P[:5], 1.2, 0.6, K.lt(c, 0.25), 0.5))
            if rnd.random() < 0.35:
                st.append(f'<path d="{K.blob(mid[0] + rnd.uniform(-6, 6), P[0][1] + 2, rnd.uniform(5, 12), rnd.uniform(2, 4), rnd.randint(0, 99), 0.3)}" fill="#4E6E2C" opacity="0.85"/>')
            a = a1 + 0.012
    out.append(f'<g {cid}>{"".join(st)}</g>')
    # rim: dark water inside, coping stones round the top
    out.append(f'<ellipse cx="{WX}" cy="{WY}" rx="{WR - 12}" ry="{WRY - 9}" fill="{D.rad([(0, "#0A1418"), (0.8, "#060A0C"), (1, "#020406")])}"/>')
    out.append(f'<ellipse cx="{WX + 30}" cy="{WY + 4}" rx="40" ry="5" fill="#5A7A8A" opacity="0.25"/>')
    for j in range(24):
        a0 = 2 * math.pi * j / 24
        a1 = 2 * math.pi * (j + 0.9) / 24
        o = [(WX + math.cos(a0) * WR, WY + math.sin(a0) * WRY), (WX + math.cos(a1) * WR, WY + math.sin(a1) * WRY),
             (WX + math.cos(a1) * (WR - 13), WY + math.sin(a1) * (WRY - 9)), (WX + math.cos(a0) * (WR - 13), WY + math.sin(a0) * (WRY - 9))]
        c = stone.color(K.norm3((0.0, -0.8, 0.6)), rnd, 0.12 if math.sin(a0) > 0 else -0.05)
        out.append(f'<path d="{K.poly_d(o)}" fill="{c}" stroke="#0E0E0C" stroke-width="1.1"/>')
    out.append(f'<path d="{K.smooth_open([(WX - WR, WY), (WX - WR * 0.5, WY + WRY * 0.86), (WX, WY + WRY), (WX + WR * 0.5, WY + WRY * 0.86), (WX + WR, WY)])}" stroke="#B8B49E" stroke-width="1.2" fill="none" opacity="0.25"/>')
    # moss cushions on the coping and the warm glow of the ball on the right side of the well
    for _ in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        out.append(f'<path d="{K.blob(WX + math.cos(a) * (WR - 6), WY + math.sin(a) * (WRY - 4), rnd.uniform(8, 18), rnd.uniform(3, 6), rnd.randint(0, 999), 0.3)}" fill="{rnd.choice(["#4A6A2A", "#6A8A3A", "#3A5A22"])}" opacity="0.85"/>')
    out.append(K.halo(D, WX + WR, WY + 60, 120, "#E8A040", 0.25))
    # ferns at the foot of the well
    fern = ["#1E3A1A", "#3A5E2A", "#5E8A3A"]
    for (fx, fy, L_, a_) in ((80, 500, 70, -140), (60, 500, 60, -110), (400, 494, 70, -50), (420, 500, 56, -20), (110, 510, 50, -160)):
        pts = [(fx + math.cos(math.radians(a_ + t * 12)) * L_ * t / 6, fy + math.sin(math.radians(a_ + t * 12)) * L_ * t / 6) for t in range(7)]
        out.append(K.taper(pts, 2.4, 0.6, fern[1], 0.95))
        for k in range(1, 6):
            px, py = pts[k]
            for sd in (-1, 1):
                aa = math.radians(a_ + k * 12 + sd * 60)
                out.append(K.taper([(px, py), (px + math.cos(aa) * 14 * (1 - k / 7), py + math.sin(aa) * 14 * (1 - k / 7))], 4, 0.5, rnd.choice(fern), 0.9))
    # the golden ball in the moss, its glow on everything near it
    BX, BY, BR = 470, 486, 34
    out.append(K.halo(D, BX, BY, 150, "#FFD070", 0.35))
    out.append(K.halo(D, BX + 6, BY + BR - 2, 50, "#000000", 0.5, ry=8))
    out.append(f'<circle cx="{BX}" cy="{BY}" r="{BR}" fill="{D.rad([(0, "#FFF6C0"), (0.25, "#F8D060"), (0.7, "#C88A20"), (1, "#5A3608")], 0.38, 0.32, 0.72)}"/>')
    out.append(f'<path d="M{BX - BR + 6} {BY + 6}Q{BX} {BY + BR * 0.9} {BX + BR - 4} {BY + 4}" stroke="#7A9A5A" stroke-width="2.4" fill="none" opacity="0.4"/>')
    out.append(f'<ellipse cx="{BX - 11}" cy="{BY - 13}" rx="9" ry="6" fill="#FFFFF0" opacity="0.85" transform="rotate(-30 {BX - 11} {BY - 13})"/>')
    out.append(f'<path d="M{BX - BR + 4} {BY - 4}Q{BX} {BY - 20} {BX + BR - 3} {BY - 2}" stroke="#8A5A10" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(K.grass(9130, (BX - 60, BY + 14, BX + 60, BY + 40), ["#3A5A2A", "#5A7A3A", "#8AAA4A"], n=40, h=(8, 18)))
    # fireflies
    for _ in range(16):
        x, y = rnd.uniform(30, 570), rnd.uniform(160, 420)
        out.append(K.halo(D, x, y, 8, "#F8F0A0", 0.6) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#FFFCE0"/>')
    # the frog on the rim, looking toward the ball
    out.append(frog_painted(D, 262, WY + WRY - 10, 3.1, 9140, light=(0.7, -0.6)))
    art = D.render(out)
    DL = K.Doc("frpL")
    L = [K.halo(DL, 300, 92, 240, "#06100C", 0.6, ry=50)]
    L.append(K.title(DL, 300, 102, "The Frog Prince", SERIF_IT, 56, max_w=440, face=("#FFF2C0", "#E8C058", "#9A6A18"), shadow="#040806", sop=0.8))
    L.append(K.subtitle(300, 130, "A TALE FROM THE BROTHERS GRIMM", CINZEL, 15, "#D8E0C0", ls=2.5, max_w=380, sh="#040806", sop=0.7))
    L.append(K.halo(DL, 300, 532, 250, "#040806", 0.55, ry=28))
    L.append(K.subtitle(300, 538, "“In olden times, when wishing still helped…”", SERIF_IT, 20, "#F2E8C0", max_w=440, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: the-frog-prince ----


# ---- plate: puss-in-boots ----
@plate("puss-in-boots", 29, edge=1.8, bristle=0.35, grain=0.18)
def puss_in_boots_plate():
    """Sunset over the Marquis of Carabas' wheat: Puss, a silver tabby with a cat's true build, sits at the
    roadside in his tall cavalier boots, plumed hat and red cape, the sack of rabbits beside him, the ogre's
    castle far off on its hill."""
    D = K.Doc("pib")
    out = []
    HZ = 330
    out.append(K.sky(D, [(0, "#3A4A7A"), (0.35, "#8A6A8A"), (0.7, "#E89A6A"), (1, "#FCD48A")], 2901, 0, HZ, n=180, op=(0.06, 0.18)))
    SX = 150
    out.append(K.halo(D, SX, HZ - 10, 300, "#FFE0A0", 0.6, ry=200))
    out.append(f'<circle cx="{SX}" cy="{HZ - 18}" r="24" fill="#FFF2C8" opacity="0.9"/>')
    cl = K.Look(["#5A4A70", "#8A6A84", "#D08A80", "#F8C090", "#FFE8C8"], key=(-0.85, 0.2, 0.4), amb=0.1, wrap=0.4, jit=0.03)
    out.append(K.cumulus(D, [(420, 150, 30), (456, 140, 38), (500, 152, 30), (540, 146, 26), (380, 160, 20)], cl, 2902, flat_y=170, rim="#FFE0B0", dab_r=(3, 8)))
    out.append(K.cumulus(D, [(60, 210, 16), (90, 204, 22), (120, 212, 16)], cl, 2903, flat_y=220, rim="#FFE0B0", dab_r=(2, 6)))
    # the ogre's castle on a far hill, hazy violet against the sunset
    hill = K.rough([(-20, HZ + 4), (300, HZ - 4), (380, HZ - 30), (470, HZ - 40), (560, HZ - 26), (620, HZ - 8)], 2904, 3, 10)
    out.append(f'<path d="{K.smooth_open(hill)} L620 400 L-20 400Z" fill="#9A7484"/>')
    cc = "#7A5A72"
    for (x, w, h, roof) in ((446, 18, 70, 18), (474, 26, 48, 0), (504, 16, 82, 20), (528, 20, 52, 0), (488, 12, 92, 22)):
        b = HZ - 36
        out.append(f'<rect x="{x - w / 2}" y="{b - h}" width="{w}" height="{h + 10}" fill="{cc}"/>')
        if roof:
            out.append(f'<path d="M{x - w / 2 - 3} {b - h}L{x} {b - h - roof}L{x + w / 2 + 3} {b - h}Z" fill="#6A4A64"/>')
        else:
            for k in range(int(w / 6)):
                out.append(f'<rect x="{x - w / 2 + k * 6}" y="{b - h - 4}" width="3.4" height="4" fill="{cc}"/>')
        out.append(f'<rect x="{x - 1.2}" y="{b - h * 0.6}" width="2.4" height="4" fill="#FFD890" opacity="0.8"/>')
    out.append(K.mist(D, HZ - 4, 18, "#F8C8A0", 0.45, seed=2905, n=8))
    # wheat to the horizon: bands of gold getting coarser toward us, the road winding to the castle
    gr = D.lin([(0, "#E8B860"), (0.4, "#D8983E"), (1, "#8A5A20")], 0, HZ, 0, 600, "userSpaceOnUse")
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="280" fill="{gr}"/>')
    rnd = random.Random(2906)
    road = [(620, 600), (560, 520), (470, 450), (430, 400), (450, 360), (476, HZ + 6), (484, HZ + 6), (462, 362), (448, 402), (494, 450), (600, 520), (640, 600)]
    out.append(f'<path d="{K.smooth_closed(road)}" fill="#E8C890" opacity="0.9"/>')
    for k in range(700):
        y = HZ + (rnd.random() ** 1.6) * 270
        t = (y - HZ) / 270
        x = rnd.uniform(-10, 610)
        h = 4 + 30 * t
        c = rnd.choice(["#F8D27A", "#E8B050", "#C88A30", "#FFE6A0", "#A86A24"])
        out.append(K.taper([(x, y), (x + rnd.uniform(-2, 3) * t, y - h)], 0.6 + 1.6 * t, 0.3, c, rnd.uniform(0.4, 0.85)))
        if t > 0.45 and rnd.random() < 0.25:
            ex, ey = x + rnd.uniform(-2, 3) * t, y - h
            out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{1.4 + 1.6 * t:.1f}" ry="{3 + 4 * t:.1f}" fill="{c}" transform="rotate({rnd.uniform(-20, 20):.0f} {ex:.1f} {ey:.1f})"/>')
    # a grassy rise at the roadside where Puss sits
    rise = [(-20, 474), (60, 458), (180, 452), (300, 458), (380, 476), (420, 506), (420, 610), (-20, 610)]
    out.append(f'<path d="{K.smooth_closed(rise)}" fill="{D.lin([(0, "#A8963E"), (0.5, "#7A6A2A"), (1, "#3E3814")], 0, 0, 0, 1)}"/>')
    out.append(K.brushwork(2908, (-20, 450, 420, 600), ["#C8B050", "#8A7A30", "#6A8A2A", "#E8D070"], 200, L=(8, 22), W=(1, 2.6), op=(0.3, 0.6), angle=-6, jit=20))
    out.append(K.grass(2907, (-20, 450, 420, 600), ["#C8B050", "#8A8A2A", "#E8D070", "#5A6A1E"], n=260, h=(8, 24), w=(1, 2.2), lean=(-0.3, 0.4)))
    # ---- Puss
    ox, oy, s = 196, 462, 3.4
    HA, HO = -4, (1, -56)

    def rot(pts, ang=HA, o=HO, k=1.3):
        a = math.radians(ang)
        c, s_ = math.cos(a), math.sin(a)
        return [(o[0] + (x * c - y * s_) * k, o[1] + (x * s_ + y * c) * k) for x, y in pts]
    T = lambda pts: K.xform(pts, ox, oy, s)
    inv = lambda x, y: ((x - ox) / s, (y - oy) / s)
    head = rot([(-3, -7), (2, -10.5), (8, -11.5), (13, -9.5), (15.5, -6), (17.5, -2.5), (17.6, 0), (16.5, 1.8), (14, 3.4), (9, 5.5), (3, 6.5), (-3, 4)])
    body = ([(-24, 0), (-29, -10), (-28, -22), (-22, -32), (-15, -40), (-9, -46), (-5, -50)] + head +
            [(13, -48), (16, -42), (16, -32), (13, -22), (13, -6), (17, -1.5), (17, 0), (5, 0), (5, -6), (5, -20), (3, -26), (-1, -20), (-4, -10), (-4, -2), (-6, 0)])
    fur = K.Look(["#121216", "#26262E", "#42424C", "#686874", "#9A96A0", "#CEC6C4", "#F6E6D2"], key=(-0.75, -0.45, 0.5), amb=0.04, wrap=0.3,
                 rim=("#FFD890", (-0.9, -0.2), 0.85), bounce=("#C8945A", 0.3), jit=0.015)
    stripes = []
    for k in range(7):
        stripes.append(((-25 + k * 3.6, -38 + k * 0.8), (-27 + k * 4.4, -14 - k * 1.5)))
    stripes += [((-4, -50), (2, -44)), ((-8, -46), (-2, -40)), ((-12, -42), (-6, -36))]

    def tabby(x, y, c, n):
        lx_, ly_ = inv(x, y)
        for (a, b) in stripes:
            vx, vy = b[0] - a[0], b[1] - a[1]
            L2 = vx * vx + vy * vy
            u = max(0, min(1, ((lx_ - a[0]) * vx + (ly_ - a[1]) * vy) / L2))
            d = math.hypot(lx_ - a[0] - vx * u, ly_ - a[1] - vy * u)
            if d < 1.3 + 0.4 * math.sin(ly_ * 0.7):
                return K.mix(c, "#141418", 0.55)
        return c

    def flow(x, y, n):
        lx_, ly_ = inv(x, y)
        if ly_ < -46 and lx_ > -6:
            return HA + 180
        if lx_ > 4 and ly_ > -36:
            return 92
        if lx_ < -16:
            return math.degrees(math.atan2(n[1], n[0])) + 90
        return 110
    # far ear, tail curled along the ground
    ear_f = rot([(0, -9.5), (0.5, -16), (2.5, -19.5), (5, -14), (7, -10.5)])
    out.append(K.paint(D, T(ear_f), fur.darker(0.3), 2910, round_r=5, flow="contour", edge_col="#0A0A0E"))
    tail = [(-26, -4), (-36, -6), (-42, -2), (-36, 3), (-16, 4), (8, 3.5), (24, 1), (27, -2.5), (23, -4), (8, -1), (-14, -1)]
    out.append(K.paint(D, T(tail), fur.darker(0.05), 2911, round_r=2.6 * s, flow=lambda x, y, n: 180, flow_jit=10, color_fn=lambda x, y, c, n: K.mix(c, "#141418", 0.5) if int((inv(x, y)[0] + 60) / 5) % 2 == 0 else c,
                       edge_col="#0A0A0E", edge_w=1.4, rim_col="#FFD890", rim_w=1.2))
    out.append(K.paint(D, T(body), fur, 2912, round_r=11 * s, bumps=[(*T([(-18, -16)])[0], 14 * s, 16 * s, 0, 7 * s), (*T(rot([(8, 0)]))[0], 10 * s, 8 * s, 0, 4 * s)],
                       flow=flow, flow_jit=10, color_fn=None, edge_col="#0E0E14", edge_w=1.9, edge_op=0.65, rim_col="#FFDC98", rim_w=1.8, rim_op=0.7,
                       accents="".join(K.taper(T([a, ((a[0] + b[0]) / 2 + 1.5, (a[1] + b[1]) / 2), b]), 3.2 * s * 0.5, 0.8, "#1A1A20", 0.42) for a, b in stripes),
                       passes=((60, (12, 22), (3, 6), (0.3, 0.5)), (320, (6, 12), (1, 2), (0.22, 0.45)))))
    out.append(K.brushwork(2925, K.bbox(T(body)), lambda x, y, r: r.choice(["#D8D0CC", "#8A8892", "#2A2A32"]), 500, L=(4, 9), W=(0.4, 0.8), op=(0.25, 0.55),
                           angle=lambda x, y: flow(x, y, (0, 0, 1)), jit=10, inside=K.Vol(T(body), 4).inside))
    # white chest and muzzle
    bib = rot([(16.5, 1.8), (14, 3.4), (9, 5.6), (4, 6.8)]) + [(9, -46), (12, -38), (12, -30), (9, -25), (7, -32), (6, -42)]
    white = K.Look(["#8A8890", "#C2C0C6", "#E6E2E4", "#FAF6F2", "#FFFFFF"], key=fur.key, amb=0.25, wrap=0.45, rim=("#FFE0A8", (-0.9, -0.2), 0.6))
    out.append(K.paint(D, T(bib), white, 2913, round_r=3 * s, flow=95, flow_jit=14, edge_col=None))
    # foreleg: white sock; near ear
    out.append(K.paint(D, T([(5, -5), (13, -5), (17, -1.5), (17, 0.4), (5, 0.4)]), white, 2914, round_r=2 * s, flow=92, edge_col="#4A4850", edge_w=1))
    out.append(K.taper(T([(5, -26), (5.4, -16), (5.2, -6)]), 1.8, 0.6, "#0E0E14", 0.5))
    ear_n = rot([(5, -10), (6.5, -16.5), (8.5, -20), (11.5, -14.5), (13, -9)])
    out.append(K.paint(D, T(ear_n), fur.darker(0.05), 2915, round_r=5, flow="contour", edge_col="#0A0A0E", edge_w=1.2, rim_col="#FFDC98", rim_w=1.4))
    out.append(K.taper(T(rot([(7, -11), (8.4, -17.5), (10.5, -12)])), 2.4, 0.5, "#E8B0A8", 0.7))
    # face: tabby M on the brow, the eye (green-gold, slit pupil), nose leather, whiskers
    # white whisker pad and chin, cheek stripes, the line of the mouth
    out.append(K.paint(D, T(rot([(13.5, -1.5), (16.5, -2.4), (17.6, 0), (16.5, 2.2), (13.5, 3.6), (11, 3), (11.5, 0.5)])), white, 2926, round_r=1.6 * s, flow=0, edge_col=None))
    for pts_ in ([(2, -9), (5, -7), (7, -9)], [(6, -10), (9, -7.5), (11, -9.5)], [(4, -1), (8, 0), (11, -1)], [(3, 2), (7, 3), (10, 2.4)], [(9, -5), (6, -6.5), (2, -6)]):
        out.append(K.taper(T(rot(pts_)), 1.6, 0.6, "#141418", 0.55))
    out.append(K.taper(T(rot([(17.2, 0.6), (16, 2.2), (14, 2.8)])), 1.0, 0.5, "#2A2228", 0.7))
    ec = T(rot([(12, -4.5)]))[0]
    out.append(f'<ellipse cx="{ec[0]:.1f}" cy="{ec[1]:.1f}" rx="{2.6 * s * 0.55:.1f}" ry="{1.9 * s * 0.55:.1f}" fill="{D.rad([(0, "#E8E070"), (0.7, "#8AAA30"), (1, "#3A4A10")])}" stroke="#0A0A0E" stroke-width="1.4"/>')
    out.append(f'<ellipse cx="{ec[0] + 0.6:.1f}" cy="{ec[1]:.1f}" rx="0.9" ry="{1.6 * s * 0.55:.1f}" fill="#060608"/>')
    out.append(f'<circle cx="{ec[0] + 1.6:.1f}" cy="{ec[1] - 1.2:.1f}" r="0.9" fill="#FFFFFF"/>')
    nz = T(rot([(17.2, -1.4)]))[0]
    out.append(f'<path d="M{nz[0] - 2.4:.1f} {nz[1] - 1.4:.1f}L{nz[0] + 1.2:.1f} {nz[1] - 1.6:.1f}L{nz[0]:.1f} {nz[1] + 1.4:.1f}Z" fill="#C88078"/>')
    for k in range(4):
        out.append(f'<path d="M{nz[0] - 4:.1f} {nz[1] + 3 + k * 0.6:.1f}q{14 + k * 3} {k * 3 - 3} {26 + k * 3} {k * 6 - 4}" stroke="#FFFFFF" stroke-width="0.7" fill="none" opacity="0.75"/>')
    # the boot on the hind leg: tan leather, a wide turned-down cuff at the knee, a buckle strap
    leather = K.Look(["#1E0E06", "#3E2210", "#6A3E1E", "#9A6232", "#C8904E", "#ECBE7E"], key=fur.key, amb=0.06, wrap=0.3, rim=("#FFD890", (-0.9, -0.2), 0.7),
                     spec=("#FFF0C8", 0.82, 0.6))
    boot = [(-4, -23), (-8, -16), (-12, -8), (-8, -4.6), (-2, -3.2), (1.6, -1.0), (0.8, 0.6), (-18, 0.6), (-19.5, -0.6), (-21.5, 0.6), (-26.5, 0.6), (-26.5, -4.5), (-24, -11), (-19, -22)]
    out.append(K.paint(D, T(boot), leather, 2916, round_r=3.6 * s, flow="contour", edge_col="#100804", edge_w=1.6, rim_col="#FFE0A0", rim_w=1.4,
                       passes=((60, (8, 16), (2, 4), (0.3, 0.55)), (240, (4, 9), (1, 2), (0.4, 0.8)))))
    cuff = [(-22, -31), (-12, -34), (-1, -30.5), (0, -22.5), (-8, -21.5), (-20, -22.5)]
    out.append(K.paint(D, T(cuff), leather.darker(-0.08), 2917, round_r=2.6 * s, flow="contour", edge_col="#100804", edge_w=1.6, rim_col="#FFE0A0", rim_w=1.4))
    out.append(K.taper(T([(-21, -24.5), (-12, -23.5), (-2, -24)]), 1.6, 1.0, "#2A1408", 0.6))
    out.append(K.taper(T([(-21, -12), (-11, -9.5)]), 2.6, 2.6, "#3A2010", 0.9))
    bq = T([(-16, -11)])[0]
    out.append(f'<rect x="{bq[0] - 3:.1f}" y="{bq[1] - 3:.1f}" width="6" height="6" fill="none" stroke="#F0D070" stroke-width="1.4"/>')
    out.append(K.taper(T([(-17.5, 0.5), (0.5, 0.4)]), 2.2, 2.2, "#140A04", 0.9))
    out.append(K.taper(T([(-26.3, 0.4), (-21.5, 0.4)]), 2.2, 2.2, "#140A04", 0.9))
    # the plumed cavalier hat, cocked over one ear
    hc = T(rot([(5, -11)]))[0]
    hat_brim = K.xform([(-16, 0), (-8, -3), (6, -3), (16, -1), (18, 2), (6, 1.5), (-8, 2), (-17, 3)], hc[0], hc[1], s * 0.95, -12)
    hat_crown = K.xform([(-7, -1), (-6, -9), (-2, -12), (4, -11.5), (7, -8), (7, -1)], hc[0], hc[1], s * 0.95, -12)
    felt = K.Look(["#120A10", "#2A1424", "#46203A", "#6A3456", "#8E4E74"], key=fur.key, amb=0.08, wrap=0.3, rim=("#FFC890", (-0.9, -0.2), 0.7))
    out.append(K.paint(D, hat_crown, felt, 2919, round_r=2.5 * s, flow="contour", edge_col="#08040A", edge_w=1.4, rim_col="#FFC890", rim_w=1.4))
    band = K.xform([(-7, -1.5), (7, -1.5), (7, -4), (-6.6, -4)], hc[0], hc[1], s * 0.95, -12)
    out.append(f'<path d="{K.poly_d(band)}" fill="#C8A040"/>')
    out.append(K.paint(D, hat_brim, felt.darker(-0.05), 2920, round_r=1.4 * s, flow=-12, edge_col="#08040A", edge_w=1.4, rim_col="#FFC890", rim_w=1.4))
    plume = K.xform([(4, -8), (-4, -18), (-16, -22), (-28, -18), (-34, -10)], hc[0], hc[1], s * 0.95, -12)
    out.append(K.taper(plume, 9, 3, "#E8E0E8", 0.9, mid=12))
    out.append(K.hair(plume, 40, lambda t: 5 + 6 * t, 2921, ["#FFFFFF", "#F0E6F0", "#C8B8D0", "#FFE8C8"], w=(0.6, 1.4), op=(0.5, 0.95)))
    for t in range(1, 12):
        p = K._lerp2(plume[min(4, t * 4 // 11)], plume[min(4, t * 4 // 11 + 1)], (t * 4 / 11) % 1)
        out.append(K.taper([p, (p[0] - 4, p[1] + 9)], 1.2, 0.3, "#FFFFFF", 0.7))
    # the sack of rabbits beside him: drawstring linen bag, two long ears peeping out
    sack = [(244, 470), (238, 440), (246, 418), (262, 408), (280, 412), (288, 434), (286, 462), (276, 476), (252, 478)]
    linen = K.Look(["#3A3020", "#6A5A40", "#9A8A66", "#C8B890", "#ECE0BC"], key=fur.key, amb=0.1, wrap=0.35, rim=("#FFE0A0", (-0.9, -0.2), 0.6))
    for (ex_, ang) in ((262, -100), (272, -78)):
        e = [(ex_ - 3, 412), (ex_ - 4 + math.cos(math.radians(ang)) * 6, 412 + math.sin(math.radians(ang)) * 30), (ex_ + 2 + math.cos(math.radians(ang)) * 6, 412 + math.sin(math.radians(ang)) * 32), (ex_ + 3, 412)]
        out.append(K.paint(D, e, K.Look(["#3A2A1A", "#7A5A3A", "#B8946A", "#E0C8A0"], key=fur.key, amb=0.1), 2922 + ex_, round_r=3, flow="axis", edge_col="#1A1008", edge_w=1))
    out.append(K.paint(D, sack, linen, 2924, round_r=14, flow="contour", edge_col="#2A2010", edge_w=1.6, rim_col="#FFE6B0", rim_w=1.4))
    out.append(K.taper([(244, 420), (262, 414), (282, 418)], 2.4, 2.4, "#4A3A20", 0.9))
    out.append(K.halo(D, 214, 470, 140, "#1A1E08", 0.45, ry=10))
    art = D.render(out)
    DL = K.Doc("pibL")
    L = [K.halo(DL, 300, 90, 240, "#2A2040", 0.45, ry=50)]
    L.append(K.title(DL, 300, 100, "Puss in Boots", SERIF_IT, 58, max_w=440, face=("#FFF0C0", "#F0C060", "#A86A1E"), shadow="#1A1028", sop=0.75))
    L.append(K.subtitle(300, 128, "CHARLES PERRAULT · 1697", CINZEL, 16, "#FFF0D8", ls=3, max_w=380, sh="#1A1028", sop=0.7))
    L.append(K.halo(DL, 300, 528, 240, "#1A2008", 0.5, ry=28))
    L.append(K.subtitle(300, 536, "“The lands of my lord, the Marquis of Carabas!”", SERIF_IT, 19, "#FFF2D0", max_w=440, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: puss-in-boots ----


# ---- plate: king-arthur ----
def sword_painted(D, x, tip_y, hilt_y, seed, blade_w=13, cross=58, light="#FFFFFF", k=1.0):
    """A knightly sword point-down: tapering steel blade with a fuller, broad crossguard, wire-bound grip,
    wheel pommel; steel modelled with a cool sky reflection on one bevel and a warm one on the other."""
    out = []
    L = tip_y - hilt_y
    bl = [(x - blade_w / 2, hilt_y), (x + blade_w / 2, hilt_y), (x + blade_w * 0.42, hilt_y + L * 0.7), (x, tip_y), (x - blade_w * 0.42, hilt_y + L * 0.7)]
    out.append(f'<path d="{K.poly_d(bl)}" fill="{D.lin([(0, "#3A4250"), (0.45, "#C8D2DC"), (0.5, "#FFFFFF"), (0.55, "#8A96A6"), (1, "#2A303A")], 0, 0, 1, 0)}"/>')
    out.append(f'<path d="M{x:.1f} {hilt_y + 4:.1f}L{x:.1f} {hilt_y + L * 0.62:.1f}" stroke="#5A6474" stroke-width="2.2"/>')
    out.append(f'<path d="M{x + 1.2:.1f} {hilt_y + 4:.1f}L{x + 1.2:.1f} {hilt_y + L * 0.62:.1f}" stroke="#F4F8FF" stroke-width="0.8" opacity="0.8"/>')
    out.append(f'<path d="{K.poly_d(bl)}" fill="none" stroke="#1A1E26" stroke-width="1.2"/>')
    # crossguard with flared ends, grip, pommel
    cg = [(x - cross / 2, hilt_y - 3 * k), (x - cross / 2 - 4 * k, hilt_y - 8 * k), (x, hilt_y - 10 * k), (x + cross / 2 + 4 * k, hilt_y - 8 * k), (x + cross / 2, hilt_y - 3 * k), (x, hilt_y + 3 * k)]
    gold = D.lin([(0, "#FFF2B8"), (0.5, "#D8A440"), (1, "#6A4410")], 0, 0, 0, 1)
    out.append(f'<path d="{K.smooth_closed(cg)}" fill="{gold}" stroke="#3A2408" stroke-width="1.2"/>')
    out.append(f'<path d="M{x - cross / 2:.1f} {hilt_y - 6:.1f}Q{x:.1f} {hilt_y - 9:.1f} {x + cross / 2:.1f} {hilt_y - 6:.1f}" stroke="#FFF8D8" stroke-width="1.2" fill="none" opacity="0.8"/>')
    gh = 34 * k
    gw = 10 * k
    out.append(f'<rect x="{x - gw / 2:.1f}" y="{hilt_y - 8 * k - gh:.1f}" width="{gw:.1f}" height="{gh:.1f}" rx="{3 * k:.1f}" fill="{D.lin([(0, "#2A1A10"), (0.4, "#6A4428"), (1, "#1A0E06")], 0, 0, 1, 0)}"/>')
    for j in range(int(9 * k)):
        yy = hilt_y - 10 * k - j * 3.6
        out.append(f'<path d="M{x - gw / 2:.1f} {yy:.1f}L{x + gw / 2:.1f} {yy - 2 * k:.1f}" stroke="#C8A060" stroke-width="1" opacity="0.7"/>')
    py = hilt_y - 8 * k - gh - 7 * k
    out.append(f'<circle cx="{x:.1f}" cy="{py:.1f}" r="{9 * k:.1f}" fill="{D.rad([(0, "#FFF4C0"), (0.5, "#D8A440"), (1, "#5A3A0C")], 0.35, 0.3, 0.7)}" stroke="#3A2408" stroke-width="1.2"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{py:.1f}" r="{4 * k:.1f}" fill="#B8202A" stroke="#4A0A0E" stroke-width="0.8"/>')
    out.append(f'<circle cx="{x - 1.2 * k:.1f}" cy="{py - 1.4 * k:.1f}" r="{1.3 * k:.1f}" fill="#FFD0D0"/>')
    return "".join(out)


@plate("king-arthur", 17, edge=1.8, bristle=0.35, grain=0.2)
def king_arthur_plate():
    """Dawn mist in a churchyard on New Year's morning: the great stone with its iron anvil, the sword driven
    through, lit by a single shaft of light; the abbey's broken arches fade into the fog behind."""
    D = K.Doc("kar")
    out = []
    out.append(K.sky(D, [(0, "#4A5A72"), (0.4, "#8A94A4"), (0.75, "#C8C2B8"), (1, "#E2D6C0")], 1701, 0, 600, n=160, op=(0.05, 0.14)))
    # the abbey ruin: tall lancet arches and a tower, ghost-pale in the fog
    ruin = "#9AA0A8"
    for (x0, w, h) in ((40, 46, 230), (100, 46, 210), (160, 46, 190)):
        out.append(f'<path d="M{x0} 420V{420 - h + w * 0.7:.0f}Q{x0 + w / 2:.0f} {420 - h - 10:.0f} {x0 + w} {420 - h + w * 0.7:.0f}V420H{x0 + w - 8}V{420 - h + w * 0.8:.0f}Q{x0 + w / 2:.0f} {420 - h + 8:.0f} {x0 + 8} {420 - h + w * 0.8:.0f}V420Z" fill="{ruin}" opacity="0.75"/>')
    out.append(f'<path d="M470 420V170L486 150L502 170V136H520V170L536 150L552 170V420Z" fill="{ruin}" opacity="0.6"/>')
    out.append(f'<path d="M500 230Q511 214 522 230V262H500Z" fill="#6A7078" opacity="0.5"/>')
    out.append(K.mist(D, 380, 120, "#E8E2D8", 0.65, seed=1702, n=12, r=(120, 240)))
    # yews and old gravestones in the fog
    yew = K.Look(["#1A2420", "#2A3A32", "#3E5246", "#5E7062"], key=(-0.6, -0.7, 0.5), amb=0.2)
    out.append(K.foliage(D, [(250, 360, 30, 70), (276, 330, 24, 60), (380, 370, 28, 60)], yew.toward("#B8BCB8", 0.45), 1703, size=(2, 5), density=0.9))
    for (gx, gh) in ((300, 30), (340, 24), (420, 34), (90, 26)):
        out.append(f'<path d="M{gx - 8} 440V{440 - gh + 8}Q{gx} {440 - gh - 4} {gx + 8} {440 - gh + 8}V440Z" fill="#8A8E92" opacity="0.6"/>')
    out.append(K.mist(D, 440, 50, "#EEE8DE", 0.55, seed=1704, n=10))
    # ground: wet grass, the stone on a low mound
    gr = D.lin([(0, "#6A7458"), (1, "#2A3424")], 0, 430, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 450 Q300 420 610 452 V610 H-10Z" fill="{gr}"/>')
    out.append(K.grass(1705, (-10, 440, 610, 600), ["#4A5A3A", "#6E7E50", "#9AA676", "#2E3A26"], n=360, h=(8, 24)))
    # the shaft of light from the upper left
    out.append(K.shafts(D, (110, -20), [(240, 380, 480), (200, 240, 470)], "#FFF4D8", 0.3))
    # the stone: a great grey boulder, lichen and moss, cracks
    rock = K.Look(["#1E2022", "#3A3C3E", "#5E5E5C", "#86847E", "#B0ACA2", "#D8D2C4"], key=(-0.55, -0.75, 0.5), amb=0.06, wrap=0.3, jit=0.05,
                  rim=("#FFF2D0", (-0.6, -0.8), 0.5))
    stone = K.rough([(80, 500), (90, 446), (124, 404), (196, 378), (300, 370), (404, 378), (470, 404), (508, 446), (516, 500), (80, 500)], 1706, 4, 10)[:-1]
    out.append(K.halo(D, 300, 504, 260, "#101410", 0.5, ry=18))
    out.append(K.paint(D, stone, rock, 1707, round_r=60, bumps=[(220, 420, 70, 40, 0, 16), (380, 426, 70, 40, 0, 14), (300, 470, 120, 30, 0, 8)], flow="contour", flow_jit=20,
                       edge_col="#0E0E0E", edge_w=2.2, edge_op=0.7, rim_col="#FFF0D0", rim_w=1.6, rim_op=0.5,
                       passes=((60, (10, 24), (3, 6), (0.3, 0.55)), (240, (5, 12), (1.2, 2.6), (0.35, 0.7)))))
    rnd = random.Random(1708)
    for _ in range(9):
        x, y = rnd.uniform(110, 490), rnd.uniform(400, 490)
        pts = [(x, y)]
        for k in range(4):
            pts.append((pts[-1][0] + rnd.uniform(-8, 8), pts[-1][1] + rnd.uniform(2, 7)))
        out.append(K.taper(pts, 1.6, 0.4, "#141414", 0.6))
    for _ in range(26):
        x, y = rnd.uniform(110, 490), rnd.uniform(386, 496)
        if K.Vol(stone, 2).inside(x, y) if False else True:
            out.append(K.dab(x, y, rnd.uniform(3, 8), rnd.choice(["#A8B070", "#C8C890", "#6E8A3A", "#4E6A2A"]), rnd.uniform(0.3, 0.6), rnd))
    out.append(K.halo(D, 300, 250, 150, "#FFF6DC", 0.55))
    out.append(sword_painted(D, 300, 370, 236, 1710, blade_w=22, cross=104, k=1.5))
    out.append(K.sparkle(309, 268, 16, "#FFFFFF", 0.95) + K.sparkle(286, 160, 8, "#FFF8D8", 0.85))
    # the anvil on the stone: dark iron, horn to the left
    anv = [(226, 392), (214, 376), (170, 362), (176, 352), (236, 350), (390, 350), (404, 360), (392, 372), (364, 374), (350, 388), (362, 396), (246, 398)]
    iron = K.Look(["#08090C", "#16181E", "#2A2E36", "#464C56", "#727A86", "#B8C0CA"], key=(-0.55, -0.8, 0.5), amb=0.05, wrap=0.25, spec=("#F0F4FF", 0.85, 0.8))
    out.append(K.paint(D, anv, iron, 1709, round_r=8, flow=0, flow_jit=4, edge_col="#000000", edge_w=1.6, rim_col="#E8ECF4", rim_w=1.2, rim_op=0.6))
    out.append(K.taper([(180, 353), (290, 351.5), (396, 353)], 2.2, 1.4, "#DDE4EE", 0.7))
    out.append(f'<ellipse cx="300" cy="352" rx="13" ry="3" fill="#000000" opacity="0.8"/>')
    # the sword driven through anvil and stone
    # ravens on the ruin
    for (bx, by, sc) in ((496, 140, 1.0), (88, 196, 0.8)):
        out.append(f'<path d="M{bx - 8 * sc:.1f} {by:.1f}q{4 * sc:.1f} -5 {8 * sc:.1f} -2q{3 * sc:.1f} -3 {7 * sc:.1f} -1l{3 * sc:.1f} 1l{-3 * sc:.1f} 2q{-2 * sc:.1f} 4 {-8 * sc:.1f} 4l{-5 * sc:.1f} 3Z" fill="#2A2C30" opacity="0.8"/>')
    art = D.render(out)
    DL = K.Doc("karL")
    L = [K.halo(DL, 300, 92, 220, "#2A3040", 0.45, ry=50)]
    L.append(K.title(DL, 300, 104, "King Arthur", SERIF_IT, 62, max_w=420, face=("#FFF2C8", "#E8C060", "#9A6A1C"), shadow="#141820", sop=0.75))
    L.append(K.subtitle(300, 133, "THE SWORD IN THE STONE", CINZEL, 17, "#F4EEE0", ls=4, max_w=380, sh="#141820", sop=0.75))
    L.append(K.halo(DL, 300, 530, 250, "#141A10", 0.5, ry=26))
    L.append(K.subtitle(300, 536, "“Whoso pulleth out this sword…”", SERIF_IT, 22, "#FFF4D8", max_w=420, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: king-arthur ----


# ---- plate: mjolnir ----
@plate("mjolnir", 13, edge=1.8, bristle=0.35, grain=0.2)
def mjolnir_plate():
    """A storm over a northern sea: on a black crag above the breakers lies Thor's hammer, short-hafted as the
    myths tell, its head carved with knotwork and runes, struck white by the lightning it calls down."""
    D = K.Doc("mjo")
    out = []
    out.append(K.sky(D, [(0, "#0A0E18"), (0.4, "#18223A"), (0.75, "#2E3E56"), (1, "#4A5A70")], 1301, 0, 600, n=200, op=(0.06, 0.16)))
    # storm clouds: low, heavy layers rolling across the sky, their undersides lit by the lightning
    cl = K.Look(["#06080E", "#121A26", "#22303E", "#3A4C60", "#6A8098", "#B8CCE0"], key=(0.1, 0.9, 0.45), amb=0.06, wrap=0.45, jit=0.03)
    rnd = random.Random(1302)
    out.append(K.cloud_bank(D, -30, 120, ["#04060A", "#0E1420", "#1E2A3A", "#3A4C62"], 1303, n=70, r=(40, 90), op=(0.3, 0.6), lit_under=("#8AA8CC", 0.35)))
    out.append(K.cloud_bank(D, 100, 230, ["#0A0E16", "#1A2434", "#34465C", "#6A84A0"], 1304, n=60, r=(30, 70), op=(0.25, 0.5), lit_under=("#B8D0EC", 0.45)))
    out.append(K.mist(D, 230, 30, "#3A4C64", 0.5, seed=1309, n=8))
    # lightning: a forked bolt from the clouds down to the hammer, with a broad glow
    bolt = [(430, 190), (418, 230), (436, 262), (410, 310), (426, 330), (400, 384)]
    out.append(K.halo(D, 420, 300, 200, "#B8D8FF", 0.45))
    for w, c, o in ((14, "#6A9AE8", 0.25), (6, "#C8E0FF", 0.6), (2.4, "#FFFFFF", 1)):
        out.append(f'<path d="M{" L".join(f"{x} {y}" for x, y in bolt)}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linejoin="round" opacity="{o}"/>')
    fork = [(436, 262), (470, 290), (476, 330), (500, 352)]
    out.append(f'<path d="M{" L".join(f"{x} {y}" for x, y in fork)}" stroke="#E0F0FF" stroke-width="1.4" fill="none" opacity="0.8"/>')
    fork2 = [(130, 210), (122, 250), (140, 270), (120, 320)]
    out.append(f'<path d="M{" L".join(f"{x} {y}" for x, y in fork2)}" stroke="#B8D0F0" stroke-width="1.2" fill="none" opacity="0.6"/>')
    # rain
    for _ in range(140):
        x, y = rnd.uniform(-20, 620), rnd.uniform(0, 600)
        out.append(f'<path d="M{x:.0f} {y:.0f}l-5 18" stroke="#9AB0CC" stroke-width="0.8" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    # the sea, breaking white on the rocks
    out.append(K.water(D, 380, 600, [(0, "#3A4A60"), (0.4, "#1E2A3A"), (1, "#0A1018")], 1304, n=400, refl_x=360, refl_w=30, refl_col="#C8DCF4", glints=90))
    for _ in range(40):
        x, y = rnd.uniform(-20, 620), rnd.uniform(390, 470)
        out.append(K.taper([(x, y), (x + rnd.uniform(20, 60), y - rnd.uniform(0, 6))], rnd.uniform(1.5, 4), 0.5, "#DCE6F2", rnd.uniform(0.3, 0.7)))
    # the crag: black basalt, wet, rim-lit by the lightning
    rock = K.Look(["#040608", "#0E1218", "#1E2430", "#34404E", "#5E6E82", "#A8BCD4"], key=(0.3, -0.9, 0.5), amb=0.05, wrap=0.3, jit=0.05,
                  rim=("#C8DCFF", (0.3, -0.9), 0.7), spec=("#E8F2FF", 0.8, 0.5))
    crag = K.rough([(-20, 600), (-20, 440), (40, 400), (110, 372), (180, 358), (300, 354), (420, 358), (490, 374), (550, 404), (620, 430), (620, 600)], 1305, 3, 10)
    out.append(K.paint(D, crag, rock, 1306, round_r=50, flow=lambda x, y, n: 10 + 30 * math.sin(x * 0.02), flow_jit=20, edge_col="#000000", edge_w=2,
                       rim_col="#DCEBFF", rim_w=2.0, rim_op=0.7, smooth=False,
                       passes=((50, (14, 30), (3, 7), (0.3, 0.55)), (200, (6, 14), (1.2, 2.6), (0.35, 0.7)))))
    for _ in range(14):
        x = rnd.uniform(20, 580)
        y = K.y_on(crag[1:-1], x) + rnd.uniform(6, 60)
        out.append(K.taper([(x, y), (x + rnd.uniform(-14, 14), y + rnd.uniform(10, 30))], 2, 0.5, "#000000", 0.5))
    for _ in range(30):                                   # spray
        x, y = rnd.uniform(-10, 610), rnd.uniform(430, 480)
        out.append(K.dab(x, y, rnd.uniform(2, 6), "#E8F0FA", rnd.uniform(0.2, 0.5), rnd))
    # ---- the hammer, lying across the crag: short haft, great head, knotwork and runes
    cx, cy, ang = 280, 318, -2
    T = lambda pts: K.xform(pts, cx, cy, 1.0, ang)
    iron = K.Look(["#06080C", "#14181E", "#262C36", "#3E4654", "#62707E", "#9AAAB8", "#E4EEF8"], key=(0.25, -0.95, 0.4), amb=0.04, wrap=0.25, jit=0.03,
                  rim=("#CFE2FF", (0.2, -0.95), 0.9), spec=("#FFFFFF", 0.88, 0.9))
    head = [(-112, -40), (-104, -46), (104, -46), (112, -40), (116, -32), (116, 32), (110, 40), (-110, 40), (-116, 32), (-116, -32)]
    out.append(K.halo(D, cx + 10, cy + 42, 160, "#000000", 0.8, ry=10))
    # haft first (it runs from under the head toward the viewer, foreshortened, to the lower right)
    haft = T([(-16, 30), (16, 28), (84, 98), (96, 110), (86, 124), (68, 120), (58, 110)])
    leather = K.Look(["#0E0806", "#24140C", "#3E2416", "#5E3A22", "#8A5A36", "#B88A5A"], key=(0.25, -0.95, 0.4), amb=0.06, wrap=0.3, rim=("#CFE2FF", (0.2, -0.95), 0.7))
    out.append(K.paint(D, haft, leather, 1307, round_r=12, flow=0, flow_jit=10, edge_col="#000000", edge_w=1.6, rim_col="#C8DCF8", rim_w=1.2))
    for k in range(10):
        t = k / 9
        p0 = (-12 + 70 * t, 40 + 76 * t)
        out.append(K.taper(T([p0, (p0[0] + 12, p0[1] - 10)]), 2.4, 1.8, "#120A06", 0.7))
    # wrist loop of braided leather
    loop = T([(90, 120), (80, 140), (98, 154), (118, 146), (116, 126), (98, 116)])
    out.append(f'<path d="{K.smooth_open(loop)}" stroke="#2A1810" stroke-width="5" fill="none"/>')
    out.append(f'<path d="{K.smooth_open(loop)}" stroke="#8A5A36" stroke-width="2" fill="none" stroke-dasharray="3 3"/>')
    # head
    H = T(head)
    out.append(K.paint(D, H, iron, 1308, round_r=22, bumps=[(*T([(0, -4)])[0], 110, 36, ang, 10)], flow=ang, flow_jit=6, smooth=False,
                       edge_col="#000000", edge_w=2.2, edge_op=0.8, rim_col="#E4F0FF", rim_w=2.4, rim_op=0.85,
                       passes=((60, (14, 30), (3, 6), (0.3, 0.55)), (240, (6, 14), (1, 2.4), (0.35, 0.7)))))
    # bevelled faces at each end
    for sx in (-1, 1):
        face = T([(sx * 116, -32), (sx * 104, -44), (sx * 104, 36), (sx * 116, 32)])
        out.append(f'<path d="{K.poly_d(face)}" fill="{"#5A6A7C" if sx < 0 else "#1E242E"}" opacity="0.8"/>')
    # the top face of the head, seen from a little above, catching the lightning
    top = T([(-110, -46), (-100, -58), (112, -58), (104, -46)])
    out.append(f'<path d="{K.poly_d(top)}" fill="{D.lin([(0, "#E8F2FF"), (0.5, "#8A9CB2"), (1, "#3A4656")], 0, 0, 0, 1)}" stroke="#000000" stroke-width="1.4" stroke-linejoin="round"/>')
    out.append(K.brushwork(1310, K.bbox(top), ["#FFFFFF", "#5A6A7E", "#B8C8DA"], 40, L=(10, 30), W=(0.5, 1.2), op=(0.2, 0.5), angle=ang, jit=3,
                           inside=lambda x, y: K._inpoly(top, x, y) if hasattr(K, "_inpoly") else True))
    # carved knotwork band and runes
    cid = D.clip(K.poly_d(H))
    kn = []
    # reflections of the storm sky across the iron face, scratches
    for k in range(6):
        y_ = -36 + k * 13 + rnd.uniform(-3, 3)
        kn.append(K.taper(T([(-110, y_), (0, y_ - 1), (110, y_ + 1)]), rnd.uniform(1, 3), rnd.uniform(1, 3), rnd.choice(["#8AA2BE", "#0A0E14"]), rnd.uniform(0.15, 0.35)))
    for _ in range(14):
        x_, y_ = rnd.uniform(-100, 100), rnd.uniform(-38, 34)
        kn.append(K.taper(T([(x_, y_), (x_ + rnd.uniform(-10, 10), y_ + rnd.uniform(-3, 3))]), 0.8, 0.3, "#C8D8EA", 0.5))
    for row, yy in enumerate((-30, 24)):
        pts = []
        for i in range(44):
            x = -92 + i * 184 / 43
            pts.append((x, yy + 5 * math.sin(i * 0.9)))
        band = T([(-96, yy - 8), (96, yy - 8), (96, yy + 8), (-96, yy + 8)])
        kn.append(f'<path d="{K.poly_d(band)}" fill="#1A2028" opacity="0.5"/>')
        kn.append(f'<path d="{K.smooth_open(T(pts))}" stroke="#7A8CA2" stroke-width="3" fill="none" opacity="0.9"/>')
        kn.append(f'<path d="{K.smooth_open(T([(x, y - 1.2) for x, y in pts]))}" stroke="#E0ECFA" stroke-width="0.9" fill="none" opacity="0.6"/>')
        pts2 = [(x, 2 * yy - y + (0 if row else 0)) for x, y in pts]
        pts2 = [(x, yy - 5 * math.sin(i * 0.9)) for i, (x, _) in enumerate(pts)]
        kn.append(f'<path d="{K.smooth_open(T(pts2))}" stroke="#5A6A80" stroke-width="3" fill="none" opacity="0.9"/>')
        kn.append(f'<path d="{K.smooth_open(T([(x, y + 1.4) for x, y in pts2]))}" stroke="#05070A" stroke-width="0.9" fill="none" opacity="0.7"/>')
    # runes in the central field (Elder Futhark strokes, carved: shadow + lit lip, faint blue glow)
    runes = [[(-58, -14), (-58, 10)], [(-58, -14), (-50, -6)], [(-58, -4), (-50, 4)],
             [(-30, -14), (-30, 10)], [(-30, -14), (-22, -8), (-30, -2), (-22, 10)],
             [(-4, -14), (-4, 10)], [(4, -14), (4, 10)], [(-4, -2), (4, -2)],
             [(24, -14), (24, 10)], [(24, -14), (32, -8), (24, -2)],
             [(50, -14), (58, 10)], [(58, -14), (50, 10)]]
    for st in runes:
        P = T(st)
        kn.append(f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in P)}" stroke="#7AB8FF" stroke-width="5" fill="none" opacity="0.25" stroke-linecap="round"/>')
        kn.append(f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in P)}" stroke="#04060A" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
        kn.append(f'<path d="M{" L".join(f"{x + 0.8:.1f} {y + 1:.1f}" for x, y in P)}" stroke="#C8E0FF" stroke-width="0.9" fill="none" stroke-linecap="round" opacity="0.8"/>')
    kn.append(K.taper(T([(-102, -44), (0, -46), (102, -44)]), 2.4, 2.4, "#F0F6FF", 0.8))
    out.append(f'<g {cid}>{"".join(kn)}</g>')
    out.append(K.sparkle(*T([(92, -44)])[0], 16, "#FFFFFF", 0.95))
    art = D.render(out)
    DL = K.Doc("mjoL")
    L = [K.halo(DL, 300, 520, 250, "#04060A", 0.6, ry=48)]
    L.append(K.title(DL, 300, 512, "MJÖLNIR", CINZEL, 60, max_w=420, ls=10, face=("#F4F8FF", "#B8C8DC", "#5A6A80"), shadow="#000000", sop=0.8))
    L.append(K.subtitle(300, 540, "Thor's hammer · from the Norse myths", SERIF_IT, 19, "#D8E4F4", max_w=420, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: mjolnir ----


# ---- plate: pandoras-box ----
def moth_sil(x, y, s, ang, seed, col, op):
    """A ragged moth-like shadow (one of the Evils): body, four torn wings."""
    rnd = random.Random(seed)
    out = []
    for side in (-1, 1):
        fw = [(0, 0), (side * 8, -9), (side * 18, -12), (side * 22, -6), (side * 16, 0), (side * 20, 4), (side * 10, 7), (side * 3, 3)]
        fw = [(px + rnd.uniform(-1.4, 1.4), py + rnd.uniform(-1.4, 1.4)) for px, py in fw]
        out.append(f'<path d="{K.smooth_closed(K.xform(fw, x, y, s, ang))}" fill="{col}" opacity="{op:.2f}"/>')
    out.append(K.taper(K.xform([(0, -6), (0, 0), (0, 9)], x, y, s, ang), 2.6 * s, 1.0 * s, col, min(1, op + 0.2)))
    return "".join(out)


@plate("pandoras-box", 87, edge=1.8, bristle=0.35, grain=0.2)
def pandoras_box_plate():
    """In a dark marble hall the bronze-bound chest stands open: golden light floods out of it, the Evils pour
    upward as moths of smoke, and on the lip one small bright winged thing remains: Hope."""
    D = K.Doc("pdb")
    out = []
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#0E0A10"/>')
    # marble wall with a painted frieze, a fluted column at left
    wall = D.lin([(0, "#1A1418"), (0.6, "#2A2024"), (1, "#3A2C2A")], 0, 0, 0, 1)
    out.append(f'<rect x="-10" y="-10" width="620" height="420" fill="{wall}"/>')
    rnd = random.Random(8701)
    for _ in range(26):
        y = rnd.uniform(0, 400)
        x = rnd.uniform(-20, 600)
        out.append(K.taper([(x, y), (x + rnd.uniform(40, 120), y + rnd.uniform(-30, 30)), (x + rnd.uniform(120, 200), y + rnd.uniform(-20, 40))], rnd.uniform(0.6, 1.6), 0.3, "#5A4A48", rnd.uniform(0.15, 0.35)))
    # frieze band with a meander (Greek key)
    fy = 168
    out.append(f'<rect x="-10" y="{fy}" width="620" height="26" fill="#3A1E18" opacity="0.8"/>')
    key = []
    for i in range(-1, 26):
        x0 = i * 24
        key.append(f'M{x0} {fy + 20}V{fy + 6}H{x0 + 16}V{fy + 16}H{x0 + 8}V{fy + 11}')
    out.append(f'<path d="{" ".join(key)}" stroke="#A86A3A" stroke-width="2" fill="none" opacity="0.7"/>')
    col = K.Look(["#120E10", "#241C1E", "#3A3030", "#5A4C48", "#8A7A70"], key=(0.8, 0.1, 0.5), amb=0.1, wrap=0.3)
    out.append(K.paint(D, [(30, -10), (96, -10), (92, 420), (34, 420)], col, 8702, round_r=30, flow=90, flow_jit=3, smooth=False, edge_col=None))
    for k in range(5):
        x = 42 + k * 11
        out.append(f'<path d="M{x} -10V420" stroke="#0A0808" stroke-width="2" opacity="0.5"/><path d="M{x + 3} -10V420" stroke="#8A7468" stroke-width="1" opacity="0.3"/>')
    # floor: marble slabs in perspective
    fl = D.lin([(0, "#2A2024"), (1, "#0A0808")], 0, 400, 0, 600, "userSpaceOnUse")
    out.append(f'<rect x="-10" y="400" width="620" height="210" fill="{fl}"/>')
    for k in range(-6, 8):
        out.append(f'<path d="M{300 + k * 30} 400L{300 + k * 120} 620" stroke="#4A3C3A" stroke-width="1" opacity="0.4"/>')
    for y in (420, 448, 488, 548):
        out.append(f'<path d="M-10 {y}H610" stroke="#4A3C3A" stroke-width="1" opacity="0.35"/>')
    # the great glow from the chest lights the whole room
    out.append(K.halo(D, 320, 300, 330, "#FFB050", 0.42))
    out.append(K.halo(D, 320, 330, 160, "#FFE6A0", 0.4))
    # ---- the chest, three-quarter view
    F = [(150, 362), (418, 362), (418, 482), (150, 482)]                 # front face
    S = [(418, 362), (496, 332), (496, 448), (418, 482)]                 # right side
    TOP = [(150, 362), (418, 362), (496, 332), (228, 332)]               # open top (the mouth)
    wood = K.Look(["#120804", "#2A1408", "#4A2410", "#743E1E", "#A26232", "#D09658"], key=(0.0, -1.0, 0.4), amb=0.08, wrap=0.3,
                  rim=("#FFD890", (0.0, -1.0), 0.6))
    out.append(K.halo(D, 330, 488, 230, "#000000", 0.6, ry=20))
    out.append(K.paint(D, S, wood.darker(0.35), 8703, round_r=8, flow=-21, flow_jit=4, smooth=False, edge_col="#000000", edge_w=1.4,
                       passes=((60, (14, 30), (2, 4), (0.3, 0.55)),)))
    out.append(K.paint(D, F, wood, 8704, round_r=10, flow=0, flow_jit=3, smooth=False, edge_col="#000000", edge_w=1.6,
                       value_fn=lambda x, y: 0.25 * max(0, 1 - (y - 362) / 60), passes=((60, (14, 30), (2, 4), (0.3, 0.55)), (200, (8, 18), (1, 2), (0.3, 0.6)))))
    # painted frieze on the front: black-figure style band with a meander, bronze corner bands and studs
    out.append(f'<rect x="166" y="384" width="236" height="58" fill="#C8783A" opacity="0.92"/>')
    out.append(f'<rect x="166" y="384" width="236" height="58" fill="none" stroke="#1A0A04" stroke-width="2"/>')
    mk = []
    for i in range(10):
        x0 = 172 + i * 23
        mk.append(f'M{x0} 438V{428}H{x0 + 14}V{434}H{x0 + 7}V{431}')
    out.append(f'<path d="{" ".join(mk)}" stroke="#1A0A04" stroke-width="1.8" fill="none"/>')
    # a frieze of running figures would be a peg-doll trap at this size: instead palmettes and a central rosette
    for i in range(5):
        cx = 192 + i * 46
        for k in range(7):
            a = math.radians(-90 + (k - 3) * 22)
            out.append(f'<path d="M{cx} 420Q{cx + math.cos(a) * 6:.1f} {420 + math.sin(a) * 14:.1f} {cx + math.cos(a) * 10:.1f} {420 + math.sin(a) * 26 + 8:.1f}" stroke="#1A0A04" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx}" cy="421" r="3" fill="#1A0A04"/>')
    bronze = D.lin([(0, "#FFE6A0"), (0.4, "#C88A30"), (1, "#5A3608")], 0, 0, 1, 1)
    for (x0, y0, x1, y1) in ((150, 362, 164, 482), (404, 362, 418, 482), (150, 362, 418, 372), (150, 470, 418, 482)):
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{bronze}" stroke="#2A1404" stroke-width="1"/>')
    for (x, y) in ((157, 380), (157, 420), (157, 460), (411, 380), (411, 420), (411, 460)):
        out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFE8A8" stroke="#3A2006" stroke-width="0.8"/>')
    out.append(f'<path d="M418 362L496 332" stroke="#FFE6A0" stroke-width="5"/><path d="M418 482L496 448" stroke="#8A5A18" stroke-width="4"/>')
    # the mouth: blinding light inside
    out.append(f'<path d="{K.poly_d(TOP)}" fill="{D.rad([(0, "#FFFFF0"), (0.5, "#FFE8A0"), (1, "#F0A040")])}"/>')
    # the lid, flung open, its underside lit gold by the light
    LID = [(228, 332), (496, 332), (470, 196), (206, 210)]
    out.append(K.paint(D, LID, wood.toward("#FFC060", 0.25), 8705, round_r=10, flow=0, flow_jit=4, smooth=False, edge_col="#1A0A04", edge_w=1.6,
                       value_fn=lambda x, y: 0.3 * max(0, (y - 210) / 120)))
    out.append(f'<path d="M206 210L470 196L474 186L208 200Z" fill="{bronze}" stroke="#2A1404" stroke-width="1"/>')
    inner = [(240, 318), (468, 318), (448, 214), (226, 226)]
    out.append(f'<path d="{K.poly_d(inner)}" fill="none" stroke="#5A3010" stroke-width="3" opacity="0.7"/>')
    out.append(f'<path d="{K.poly_d([(x + (346 - x) * 0.12, y + (268 - y) * 0.12) for x, y in inner])}" fill="none" stroke="#FFD890" stroke-width="1.2" opacity="0.6"/>')
    out.append(K.halo(D, 350, 300, 120, "#FFE6A0", 0.45, ry=50))
    # light beams up out of the chest
    out.append(K.shafts(D, (360, 340), [(150, 250, -10), (290, 430, -10), (480, 580, -10)], "#FFE8B0", 0.26))
    # the Evils: a dark smoke column of moths spiralling up and away into the hall
    smoke = []
    for i in range(14):
        t = i / 13
        x = 360 + 120 * math.sin(t * 5.2) * t + rnd.uniform(-20, 20)
        y = 330 - 290 * t
        smoke.append((x, y))
    out.append(K.hair(smoke, 30, lambda t: 10 + 70 * t, 8706, ["#1A1020", "#2E2034", "#3E2E44"], w=(4, 12), op=(0.18, 0.4), start=(0, 0.2), end=(0.6, 1.0), wave=0.5))
    for i in range(28):
        t = rnd.uniform(0.08, 1.0)
        k = int(t * 13)
        x, y = smoke[k]
        x += rnd.uniform(-40, 40) * (0.3 + t)
        y += rnd.uniform(-15, 15)
        out.append(moth_sil(x, y, rnd.uniform(0.7, 1.6) * (1.2 - t * 0.4), rnd.uniform(-40, 40), 8707 + i, rnd.choice(["#0E0810", "#1E1424", "#2A1A2E"]), rnd.uniform(0.55, 0.95)))
    # Hope: a small radiant winged thing still at the lip of the chest
    hx, hy = 300, 340
    out.append(K.halo(D, hx, hy, 70, "#FFFFFF", 0.9))
    for side in (-1, 1):
        w1 = [(hx, hy), (hx + side * 15, hy - 19), (hx + side * 28, hy - 16), (hx + side * 25, hy - 3), (hx + side * 9, hy)]
        w2 = [(hx, hy), (hx + side * 18, hy + 6), (hx + side * 20, hy + 16), (hx + side * 9, hy + 12)]
        out.append(f'<path d="{K.smooth_closed(w1)}" fill="#FFFDF0" stroke="#F8D070" stroke-width="0.8"/>')
        out.append(f'<path d="{K.smooth_closed(w2)}" fill="#FFF6D0" stroke="#F8D070" stroke-width="0.8"/>')
    out.append(K.taper([(hx, hy - 9), (hx, hy + 12)], 3.4, 1.6, "#C89040", 1))
    out.append(K.sparkle(hx, hy - 2, 40, "#FFFFFF", 0.55))
    art = D.render(out)
    DL = K.Doc("pdbL")
    L = [K.halo(DL, 300, 92, 240, "#0A0608", 0.6, ry=50)]
    L.append(K.title(DL, 300, 102, "Pandora's Box", SERIF_IT, 58, max_w=440, face=("#FFF2C8", "#F0C060", "#A86A1E"), shadow="#000000", sop=0.8))
    L.append(K.subtitle(300, 130, "A GREEK MYTH · HESIOD", CINZEL, 16, "#E8D8C0", ls=3, max_w=360, sh="#000000", sop=0.7))
    L.append(K.halo(DL, 300, 530, 240, "#000000", 0.55, ry=26))
    L.append(K.subtitle(300, 538, "…and at the bottom lay Hope.", SERIF_IT, 24, "#FFE8B8", max_w=420, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: pandoras-box ----


# ---- plate: rapunzel ----
def stone_tower_painted(D, cx, base, top, w0, w1, seed, look, roof_look, win_y, warm="#FFC870"):
    """A tall round stone tower, slightly tapering: modelled masonry courses that curve with the cylinder, one high
    arched window glowing, a conical slate roof with a finial."""
    rnd = random.Random(seed)
    out = []
    body = [(cx - w0 / 2, base), (cx - w1 / 2, top), (cx + w1 / 2, top), (cx + w0 / 2, base)]
    out.append(K.paint(D, body, look, seed, round_r=w0 * 0.5, flow=90, flow_jit=4, smooth=False, edge_col="#0A0A12", edge_w=1.6,
                       rim_col="#E8D8F0", rim_w=1.4, rim_op=0.5, passes=((50, (12, 26), (3, 6), (0.3, 0.5)),)))
    cid = D.clip(K.poly_d(body))
    st = []
    y = top + 4
    row = 0
    while y < base:
        t = (y - top) / (base - top)
        w = w1 + (w0 - w1) * t
        hh = 9 + 3 * t
        n = 9
        off = 0.5 if row % 2 else 0
        for j in range(n):
            a0 = math.pi * (j + off) / n
            a1 = math.pi * (j + off + 0.94) / n
            x0, x1 = cx - math.cos(a0) * w / 2, cx - math.cos(a1) * w / 2
            if x1 - x0 < 1.5:
                continue
            nx = -math.cos((a0 + a1) / 2)
            c = look.color(K.norm3((nx, -0.1, math.sin((a0 + a1) / 2))), rnd, rnd.uniform(-0.06, 0.06))
            st.append(f'<path d="M{x0:.1f} {y:.1f}H{x1:.1f}V{y + hh - 1:.1f}H{x0:.1f}Z" fill="{c}" opacity="0.85"/>')
        st.append(f'<path d="M{cx - w / 2:.1f} {y + hh - 0.5:.1f}H{cx + w / 2:.1f}" stroke="#0E0C14" stroke-width="1" opacity="0.6"/>')
        y += hh
        row += 1
    # ivy creeping up from the base
    for _ in range(140):
        t = rnd.random() ** 1.8
        yy = base - t * (base - top) * 0.55
        w = w1 + (w0 - w1) * ((yy - top) / (base - top))
        xx = cx + rnd.uniform(-0.5, 0.5) * w * (1 - t * 0.4) - w * 0.15
        st.append(K.dab(xx, yy, rnd.uniform(2, 4.5), rnd.choice(["#1E3A1E", "#2E5226", "#4A6E30", "#0E200E"]), rnd.uniform(0.6, 0.95), rnd, 0.6))
    out.append(f'<g {cid}>{"".join(st)}</g>')
    # corbelled parapet ring and the roof
    out.append(f'<path d="M{cx - w1 / 2 - 8:.1f} {top:.1f}H{cx + w1 / 2 + 8:.1f}V{top + 10:.1f}H{cx - w1 / 2 - 8:.1f}Z" fill="{K.ramp(look.cols, 0.45)}" stroke="#0A0A12" stroke-width="1.4"/>')
    for k in range(7):
        x = cx - w1 / 2 - 4 + k * (w1 + 8) / 6
        out.append(f'<path d="M{x - 3:.1f} {top + 10:.1f}L{x:.1f} {top + 18:.1f}L{x + 3:.1f} {top + 10:.1f}" fill="{K.ramp(look.cols, 0.3)}" stroke="#0A0A12" stroke-width="0.8"/>')
    roof = [(cx - w1 / 2 - 12, top + 2), (cx, top - w1 * 1.6), (cx + w1 / 2 + 12, top + 2)]
    out.append(K.paint(D, roof, roof_look, seed + 1, round_r=w1 * 0.5, flow=lambda x, y, n: 90 + (x - cx) * 0.6, flow_jit=3, smooth=False,
                       edge_col="#06040A", edge_w=1.6, rim_col="#F0C8E0", rim_w=1.6, rim_op=0.6))
    for k in range(1, 8):
        yy = top + 2 - k * w1 * 1.6 / 8
        half = (w1 / 2 + 12) * (1 - k / 8)
        out.append(f'<path d="M{cx - half:.1f} {yy:.1f}Q{cx:.1f} {yy + 4:.1f} {cx + half:.1f} {yy:.1f}" stroke="#1A1428" stroke-width="1" fill="none" opacity="0.5"/>')
    out.append(f'<path d="M{cx:.1f} {top - w1 * 1.6:.1f}V{top - w1 * 1.6 - 18:.1f}" stroke="#C8A050" stroke-width="2"/>')
    out.append(f'<path d="M{cx:.1f} {top - w1 * 1.6 - 16:.1f}l12 4l-12 4Z" fill="#B8304A"/>')
    # the high window, lamplit
    wx = cx + 2
    ww, wh = 22, 34
    out.append(K.halo(D, wx, win_y, 60, warm, 0.45))
    out.append(f'<path d="M{wx - ww / 2 - 4:.1f} {win_y + wh / 2 + 4:.1f}V{win_y - wh / 2 + 6:.1f}Q{wx:.1f} {win_y - wh / 2 - 12:.1f} {wx + ww / 2 + 4:.1f} {win_y - wh / 2 + 6:.1f}V{win_y + wh / 2 + 4:.1f}Z" fill="#2A2430"/>')
    out.append(f'<path d="M{wx - ww / 2:.1f} {win_y + wh / 2:.1f}V{win_y - wh / 2 + 6:.1f}Q{wx:.1f} {win_y - wh / 2 - 7:.1f} {wx + ww / 2:.1f} {win_y - wh / 2 + 6:.1f}V{win_y + wh / 2:.1f}Z" fill="{D.lin([(0, "#FFF2C0"), (1, "#F0A040")], 0, 0, 0, 1)}"/>')
    out.append(f'<path d="M{wx - ww / 2 - 6:.1f} {win_y + wh / 2 + 2:.1f}H{wx + ww / 2 + 6:.1f}V{win_y + wh / 2 + 7:.1f}H{wx - ww / 2 - 6:.1f}Z" fill="{K.ramp(look.cols, 0.6)}" stroke="#0A0A12" stroke-width="1"/>')
    return "".join(out)


def braid_painted(D, pts, w0, w1, seed, cols=("#FFF4C0", "#F2CC6A", "#C8902E", "#7A4E14")):
    """A thick golden braid: interlocking lobes alternating left and right along the path, each lit on its upper
    side, with loose flyaway hairs."""
    rnd = random.Random(seed)
    fine = K.resample(pts, 3, closed=False)
    n = len(fine)
    out = [K.taper(fine, w0, w1, cols[3], 0.95)]
    step = 3
    i = 0
    k = 0
    while i < n - 2:
        t = i / max(1, n - 1)
        w = w0 + (w1 - w0) * t
        a, b = fine[i], fine[min(n - 1, i + step)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        side = 1 if k % 2 else -1
        c = (a[0] + nx * side * w * 0.18, a[1] + ny * side * w * 0.18)
        lobe = [(c[0] - nx * side * w * 0.45 - ux * w * 0.1, c[1] - ny * side * w * 0.45 - uy * w * 0.1),
                (c[0] + ux * w * 0.5, c[1] + uy * w * 0.5),
                (c[0] + nx * side * w * 0.45 + ux * w * 0.9, c[1] + ny * side * w * 0.45 + uy * w * 0.9),
                (c[0] + nx * side * w * 0.2 + ux * w * 0.2, c[1] + ny * side * w * 0.2 + uy * w * 0.2)]
        g = D.lin([(0, cols[0]), (0.5, cols[1]), (1, cols[2])], 0, 0, 0.3, 1)
        out.append(f'<path d="{K.smooth_closed(lobe)}" fill="{g}" stroke="{cols[3]}" stroke-width="0.8" opacity="0.98"/>')
        out.append(K.taper([lobe[0], lobe[1], lobe[2]], 1.2, 0.4, cols[0], 0.6))
        i += max(1, int(w * 0.5 / 3))
        k += 1
    out.append(K.hair(fine, 30, lambda t: w0 * 0.7, seed + 1, [cols[0], cols[1]], w=(0.4, 0.9), op=(0.3, 0.7), wave=0.4))
    return "".join(out)


@plate("rapunzel", 23, edge=1.8, bristle=0.35, grain=0.18)
def rapunzel_plate():
    """Dusk in the deep wood: the witch's tower with no door and no stair rises above the trees; from its one
    lamplit window a golden braid tumbles all the way down to the meadow of rampion below."""
    D = K.Doc("rpz")
    out = []
    out.append(K.sky(D, [(0, "#1E1A44"), (0.35, "#3E3270"), (0.65, "#8A5A8E"), (0.85, "#E09A8A"), (1, "#F6C49A")], 2301, 0, 470, n=180, op=(0.06, 0.18)))
    out.append(K.stars(2302, (10, 10, 590, 200), 50, r=(0.4, 1.3), op=(0.4, 0.95)))
    out.append(K.halo(D, 470, 120, 30, "#FFF8E0", 0.6) + f'<circle cx="470" cy="120" r="12" fill="#FFF8E4"/>' + f'<circle cx="476" cy="116" r="11" fill="#2E2864"/>')
    # forest in layers, hazier and pinker into the distance
    rnd = random.Random(2303)
    for k, (yb, col) in enumerate(((430, "#7A5A80"), (458, "#4E3E62"), (492, "#2A2440"))):
        out.append(f'<rect x="-10" y="{yb - 6}" width="620" height="{620 - yb}" fill="{col}"/>')
        x = -20
        while x < 630:
            h = rnd.uniform(36, 90) * (1 + k * 0.35)
            out.append(conifer(x, yb + rnd.uniform(-4, 6), h, K.mix(col, "#000000", rnd.uniform(0, 0.12)), rnd.randint(0, 99999), width=rnd.uniform(0.26, 0.36)))
            x += rnd.uniform(8, 16) * (1 + k * 0.4)
        out.append(K.mist(D, yb - 10, 24, "#E8A8B0", 0.32 - k * 0.09, seed=2304 + k, n=8))
    # the tower
    stone = K.Look(["#141224", "#2A2640", "#46405E", "#6A6082", "#968AA8", "#C8BCD2"], key=(0.8, -0.3, 0.5), amb=0.06, wrap=0.35, jit=0.04,
                   rim=("#FFC8B0", (0.9, -0.2), 0.6))
    slate = K.Look(["#0E0A18", "#221A36", "#3A2E54", "#5A4A78", "#8A72A0"], key=(0.8, -0.3, 0.5), amb=0.06, wrap=0.35, rim=("#FFC8B0", (0.9, -0.2), 0.6))
    TX = 330
    out.append(stone_tower_painted(D, TX, 520, 200, 104, 84, 2305, stone, slate, win_y=244))
    # the braid: from the window sill down the tower face, swinging out a little, pooling on the ground
    braid = [(TX + 2, 264), (TX + 14, 306), (TX + 30, 360), (TX + 40, 414), (TX + 40, 460), (TX + 60, 496), (TX + 100, 506), (TX + 128, 500)]
    out.append(braid_painted(D, braid, 15, 9, 2306))
    out.append(K.halo(D, TX + 120, 504, 26, "#FFE8A0", 0.45))
    # meadow of rampion (bellflowers) and grass at the foot of the tower
    gr = D.lin([(0, "#2E3A2A"), (1, "#121A12")], 0, 490, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 500 Q300 486 610 502 V610 H-10Z" fill="{gr}"/>')
    out.append(K.grass(2307, (-10, 490, 610, 600), ["#2E4A2A", "#4A6A3A", "#6E8A4E", "#1E301E"], n=320, h=(10, 28)))
    for _ in range(46):
        x, y = rnd.uniform(-10, 610), rnd.uniform(500, 600)
        out.append(K.taper([(x, y + 14), (x + rnd.uniform(-3, 3), y)], 1.2, 0.6, "#3A5A2E", 0.9))
        c = rnd.choice(["#8A7AE0", "#A898F0", "#6A5AC8", "#C8B8FF"])
        out.append(f'<path d="M{x - 3:.1f} {y:.1f}Q{x:.1f} {y - 7:.1f} {x + 3:.1f} {y:.1f}L{x + 4:.1f} {y + 3:.1f}L{x - 4:.1f} {y + 3:.1f}Z" fill="{c}"/>')
    # birds going home
    for (bx, by, s_) in ((150, 140, 1.0), (178, 156, 0.8), (200, 132, 0.7)):
        out.append(f'<path d="M{bx - 8 * s_:.1f} {by:.1f}q{4 * s_:.1f} -5 {8 * s_:.1f} 0q{4 * s_:.1f} -5 {8 * s_:.1f} 0" stroke="#1A1430" stroke-width="1.6" fill="none"/>')
    art = D.render(out)
    DL = K.Doc("rpzL")
    L = [K.halo(DL, 150, 290, 170, "#1A1434", 0.45, ry=110)]
    L.append(K.title(DL, 150, 268, "Rapunzel,", SERIF_IT, 50, max_w=230, anchor="middle", face=("#FFF0C0", "#F0C060", "#A86A1E"), shadow="#0A0818", sop=0.8))
    L.append(K.title(DL, 150, 322, "Rapunzel,", SERIF_IT, 50, max_w=230, anchor="middle", face=("#FFF0C0", "#F0C060", "#A86A1E"), shadow="#0A0818", sop=0.8))
    L.append(K.subtitle(150, 362, "let down your hair.", SERIF_IT, 26, "#FFE8C8", max_w=230, sh="#0A0818", sop=0.75))
    L.append(K.subtitle(150, 228, "BROTHERS GRIMM", CINZEL, 16, "#E8D8F0", ls=3, max_w=200, sh="#0A0818", sop=0.7))
    return art, DL.render(L)
# ---- end plate: rapunzel ----


# ---- plate: robin-hood ----
@plate("robin-hood", 19, edge=1.8, bristle=0.35, grain=0.18)
def robin_hood_plate():
    """Sherwood at midsummer noon: under a vast old oak a straw archery butt stands in a shaft of sun, one arrow
    in the gold and a second arrow splitting it down the shaft; the longbow and quiver lean on the oak."""
    D = K.Doc("rbh")
    out = []
    out.append(K.sky(D, [(0, "#C8D8A0"), (0.5, "#9AB878"), (1, "#5A7A48")], 1901, 0, 600, n=100, op=(0.05, 0.12)))
    rnd = random.Random(1902)
    # far trees in sunlit haze, then nearer trunks, darker and warmer
    for k, (col, n, w) in enumerate((("#A8BC88", 9, (10, 20)), ("#6E8A58", 7, (16, 30)), ("#3E5432", 5, (26, 44)))):
        lk = K.Look([K.dk(col, 0.35), K.dk(col, 0.15), col, K.lt(col, 0.2)], key=(-0.6, -0.7, 0.5), amb=0.15, wrap=0.4)
        for i in range(n):
            x = rnd.uniform(-20, 620)
            if k == 2 and 120 < x < 500:
                continue
            wd = rnd.uniform(*w)
            out.append(K.paint(D, K.limb_outline([(x, 620, wd * 1.2), (x + rnd.uniform(-8, 8), 300, wd), (x + rnd.uniform(-14, 14), -20, wd * 0.8)], cap=0.1),
                               lk, 1903 + k * 20 + i, round_r=wd * 0.5, flow=90, flow_jit=4, edge_col=None, passes=((40, (20, 40), (3, 6), (0.3, 0.5)),)))
        out.append(K.mist(D, 380, 160, "#E8F0C8", 0.35 - k * 0.1, seed=1910 + k, n=8, r=(80, 180)))
    # canopy: dense leaves overhead with sun breaking through
    leaf = K.Look(["#0E1A0A", "#1E3214", "#34501E", "#56782E", "#88A848", "#C8D880"], key=(-0.5, -0.8, 0.5), amb=0.05, wrap=0.35, jit=0.05)
    out.append(K.foliage(D, [(60, 20, 170, 80), (330, -10, 220, 70), (560, 30, 150, 90), (620, 160, 60, 80), (200, 70, 80, 40), (460, 80, 80, 40)],
                         leaf, 1920, density=1.0, size=(4, 9), holes="#F0F4C8", hole_n=80))
    out.append(K.shafts(D, (380, -20), [(250, 330, 600), (350, 420, 600), (440, 470, 600)], "#FFF6C8", 0.28))
    # glade floor: sun-dappled grass, ferns, bracken
    gr = D.lin([(0, "#7A9A48"), (0.5, "#5A7A34"), (1, "#2E4420")], 0, 440, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 452 Q300 430 610 450 V610 H-10Z" fill="{gr}"/>')
    out.append(K.grass(1921, (-10, 440, 610, 600), ["#9AB860", "#6E8E3E", "#C8D888", "#3E5A26"], n=360, h=(8, 26)))
    for _ in range(18):
        x, y = rnd.uniform(-10, 610), rnd.uniform(470, 600)
        out.append(K.halo(D, x, y, rnd.uniform(14, 30), "#F8F8C0", 0.35, ry=rnd.uniform(4, 8)))
    # the great oak at the left
    bark = K.Look(["#120E0A", "#241C14", "#3E3224", "#5E4E3A", "#8A7A5E", "#B8A886"], key=(0.7, -0.6, 0.5), amb=0.06, wrap=0.3, jit=0.05,
                  rim=("#F8F0C0", (0.8, -0.5), 0.6))
    for b, w in (([(110, 170), (190, 128), (270, 108), (340, 84)], [40, 30, 22, 14]), ([(116, 90), (190, 46), (250, 10), (290, -20)], [34, 26, 20, 14])):
        out.append(K.trunk(D, b, w, bark, 1930 + b[0][1], crevices=10, knots=0, rim="#F8F0C0"))
    spine = [(70, 540), (78, 480), (72, 400), (84, 320), (76, 240), (90, 160), (80, 80), (96, 0), (90, -40)]
    out.append(K.trunk(D, spine, [170, 146, 128, 122, 112, 104, 96, 90, 86], bark, 1922, roots=1, root_spread=1.25, crevices=50, knots=3,
                       rim="#F8F0C0", moss=["#4A6A2A", "#6E8A3A", "#2E4A1E"]))
    # longbow and quiver leaning against the oak
    bow = [(150, 470), (162, 380), (170, 290), (168, 210)]
    out.append(f'<path d="{K.smooth_open(bow)}" stroke="#5A3418" stroke-width="5.4" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{K.smooth_open(bow)}" stroke="#C8904E" stroke-width="1.6" fill="none" opacity="0.7"/>')
    out.append(f'<path d="M150 470L168 210" stroke="#F4ECD8" stroke-width="1" opacity="0.8"/>')
    out.append(f'<rect x="161" y="330" width="9" height="16" rx="2" fill="#2A1A0E"/>')
    quiver = [(182, 466), (196, 344), (216, 348), (204, 470)]
    leather = K.Look(["#1A0C06", "#3A1E0E", "#5E3418", "#8A5428", "#B87E44"], key=(0.7, -0.6, 0.5), amb=0.06, wrap=0.35)
    out.append(K.paint(D, quiver, leather, 1923, round_r=8, flow=84, edge_col="#0A0402", edge_w=1.4, smooth=False))
    for k in range(5):
        x0 = 196 + k * 4
        out.append(f'<path d="M{x0} 346L{x0 - 6 + k} 316" stroke="#6A4A2A" stroke-width="1.4"/>')
        out.append(f'<path d="M{x0 - 6 + k} 316l-4 -12l4 2l4 -2Z" fill="{["#F2F2EA", "#C8402A", "#F2F2EA", "#3A6A3A", "#F2F2EA"][k]}"/>')
    # ---- the archery butt: woven straw boss on a trestle, painted rings, two arrows
    BX, BY, BR = 410, 330, 92
    out.append(K.halo(D, BX + 10, 470, 150, "#1A2410", 0.45, ry=14))
    wood = K.Look(["#1A1008", "#3A2414", "#5E3E22", "#8A6034", "#B8884E"], key=(-0.6, -0.7, 0.5), amb=0.08, wrap=0.35, rim=("#FFF2C0", (-0.6, -0.7), 0.5))
    for (x0, y0, x1, y1) in ((BX - 60, 470, BX - 20, 330), (BX + 60, 470, BX + 20, 330), (BX + 4, 474, BX + 30, 360)):
        out.append(K.paint(D, K.limb_outline([(x0, y0, 9), (x1, y1, 8)], cap=0.2), wood, 1924 + x0, round_r=4, flow="contour", edge_col="#0A0602", edge_w=1.2))
    straw = K.Look(["#4A3410", "#7A5A20", "#A88434", "#D2B058", "#F2DC8E"], key=(-0.6, -0.7, 0.5), amb=0.08, wrap=0.35, rim=("#FFF6C8", (-0.6, -0.7), 0.6))
    boss = [(BX + math.cos(a) * BR * 0.94, BY + math.sin(a) * BR) for a in [k * math.pi / 18 for k in range(36)]]
    out.append(K.paint(D, boss, straw, 1925, round_r=BR * 0.6, flow="contour", flow_jit=8, edge_col="#2A1A06", edge_w=2.0,
                       rim_col="#FFF6C8", rim_w=1.6, passes=((60, (10, 22), (2, 4), (0.3, 0.55)),)))
    # coils of the woven straw
    for r_ in range(12, int(BR), 9):
        out.append(f'<ellipse cx="{BX}" cy="{BY}" rx="{r_ * 0.94:.1f}" ry="{r_:.1f}" fill="none" stroke="#5A3E12" stroke-width="1.2" opacity="0.35"/>')
    # painted target face: rings of gold, red, white, black, slightly worn
    face = [(BR * 0.82, "#F2EEE0"), (BR * 0.66, "#1E1A18"), (BR * 0.5, "#E8E2D2"), (BR * 0.34, "#B8282A"), (BR * 0.18, "#F2C232")]
    for r_, c in face:
        out.append(f'<ellipse cx="{BX}" cy="{BY}" rx="{r_ * 0.94:.1f}" ry="{r_:.1f}" fill="{c}" opacity="0.92"/>')
        out.append(f'<ellipse cx="{BX}" cy="{BY}" rx="{r_ * 0.94:.1f}" ry="{r_:.1f}" fill="none" stroke="#2A1A0A" stroke-width="1" opacity="0.5"/>')
    out.append(K.brushwork(1926, (BX - BR, BY - BR, BX + BR, BY + BR), ["#C8A050", "#5A3E12", "#F2DC8E"], 160, L=(4, 12), W=(0.5, 1.2), op=(0.2, 0.45), angle=lambda x, y: math.degrees(math.atan2(y - BY, x - BX)) + 90,
                           jit=15, inside=lambda x, y: (x - BX) ** 2 / (BR * 0.82 * 0.94) ** 2 + (y - BY) ** 2 / (BR * 0.82) ** 2 < 1))
    out.append(K.halo(D, BX - 26, BY - 30, 50, "#FFFFF0", 0.25))
    # the split: first arrow in the gold, the second driven through its nock, the first shaft splintered
    ang = math.radians(-12)
    ux, uy = math.cos(ang), math.sin(ang)
    tip = (BX + 2, BY + 2)
    L = 150
    tail = (tip[0] + ux * L * 0.95, tip[1] + uy * L * 0.95 - 4)
    out.append(K.taper([tip, tail], 4.2, 4.2, "#7A4E24", 1))
    out.append(K.taper([(tip[0], tip[1] - 1.4), (tail[0], tail[1] - 1.4)], 1.2, 1.2, "#D8A868", 0.8))
    # splinters where the second arrow split the first
    for k in range(6):
        p = (tip[0] + ux * L * rnd.uniform(0.5, 0.9), tip[1] + uy * L * rnd.uniform(0.5, 0.9))
        out.append(K.taper([p, (p[0] + rnd.uniform(4, 14), p[1] + rnd.uniform(-10, 10))], 1.6, 0.3, "#E8C080", 0.85))
    # fletching of the second arrow
    for side in (-1, 1):
        f = [(tail[0] - ux * 30, tail[1] - uy * 30), (tail[0], tail[1] + side * 12), (tail[0] + ux * 6, tail[1] + side * 11), (tail[0] + ux * 2, tail[1])]
        out.append(f'<path d="{K.smooth_closed(f)}" fill="{"#F2F0E6" if side < 0 else "#C83A2A"}" stroke="#2A1A0A" stroke-width="0.8"/>')
    out.append(f'<circle cx="{tail[0] + ux * 4:.1f}" cy="{tail[1] + uy * 4:.1f}" r="2.4" fill="#2A1A0A"/>')
    out.append(K.sparkle(tip[0] - 4, tip[1] - 6, 14, "#FFFFFF", 0.9))
    art = D.render(out)
    DL = K.Doc("rbhL")
    L_ = [K.halo(DL, 330, 128, 220, "#1A2A10", 0.55, ry=56)]
    L_.append(K.title(DL, 330, 140, "Robin Hood", SERIF_IT, 62, max_w=400, face=("#FFF4C8", "#E8C060", "#9A6A1C"), shadow="#0A1206", sop=0.8))
    L_.append(K.subtitle(330, 170, "SHERWOOD FOREST", CINZEL, 17, "#F4F0D8", ls=4, max_w=320, sh="#0A1206", sop=0.75))
    L_.append(K.halo(DL, 300, 530, 250, "#0E1A08", 0.55, ry=26))
    L_.append(K.subtitle(300, 538, "Split the arrow in the gold.", SERIF_IT, 24, "#FFF4D0", max_w=420, sh="#000000", sop=0.8))
    return art, DL.render(L_)
# ---- end plate: robin-hood ----


# ---- plate: sleeping-beauty ----
def castle_painted(D, cx, base, seed, look, roof_look, k=1.0, lit="#FFD27A", windows=True):
    """A tall fairy-tale castle (Gothic, French chateau roofs): a keep with towers of different heights, conical
    slate roofs, a few lancet windows; masonry modelled by `look`. Returns svg."""
    rnd = random.Random(seed)
    out = []
    towers = [(-70, 26, 170, 54), (-36, 34, 214, 70), (0, 50, 250, 0), (40, 30, 196, 64), (74, 22, 150, 48), (14, 18, 276, 50)]
    # curtain wall first
    wall = [(cx - 100 * k, base), (cx - 100 * k, base - 90 * k), (cx + 100 * k, base - 90 * k), (cx + 100 * k, base)]
    out.append(K.paint(D, wall, look.darker(0.1), seed, round_r=20, flow=90, flow_jit=4, smooth=False, edge_col="#06040C", edge_w=1.4))
    for i in range(14):
        x = cx - 100 * k + i * 200 * k / 13
        out.append(f'<rect x="{x - 4 * k:.1f}" y="{base - 98 * k:.1f}" width="{8 * k:.1f}" height="{9 * k:.1f}" fill="{K.ramp(look.cols, 0.35)}"/>')
    for (dx, w, h, roof) in sorted(towers, key=lambda t: -t[2] if t[3] == 0 else t[2]):
        x0, x1 = cx + (dx - w / 2) * k, cx + (dx + w / 2) * k
        top = base - h * k
        body = [(x0, base), (x0, top), (x1, top), (x1, base)]
        out.append(K.paint(D, body, look, seed + dx, round_r=w * k * 0.5, flow=90, flow_jit=3, smooth=False, edge_col="#06040C", edge_w=1.4,
                           rim_col="#E8E0FF", rim_w=1.2, rim_op=0.5, passes=((60, (10, 24), (2, 5), (0.3, 0.55)),)))
        if roof:
            r = [(x0 - 5 * k, top + 2), ((x0 + x1) / 2, top - roof * k), (x1 + 5 * k, top + 2)]
            out.append(K.paint(D, r, roof_look, seed + dx + 1, round_r=w * k * 0.4, flow=90, flow_jit=3, smooth=False, edge_col="#06040C", edge_w=1.4,
                               rim_col="#E8C8F0", rim_w=1.4, rim_op=0.5))
            out.append(f'<path d="M{(x0 + x1) / 2:.1f} {top - roof * k:.1f}V{top - roof * k - 12 * k:.1f}" stroke="#C8A050" stroke-width="1.6"/>')
        else:
            for j in range(int(w / 9)):
                out.append(f'<rect x="{x0 + j * 9 * k:.1f}" y="{top - 7 * k:.1f}" width="{5 * k:.1f}" height="{7 * k:.1f}" fill="{K.ramp(look.cols, 0.4)}"/>')
        if windows:
            for _ in range(2 if h > 180 else 1):
                wy = top + rnd.uniform(0.2, 0.6) * (base - top) * 0.6 + 16 * k
                wx = (x0 + x1) / 2
                on = rnd.random() < 0.55
                if on:
                    out.append(K.halo(D, wx, wy, 18 * k, lit, 0.45))
                out.append(f'<path d="M{wx - 3.5 * k:.1f} {wy + 7 * k:.1f}V{wy - 3 * k:.1f}Q{wx:.1f} {wy - 9 * k:.1f} {wx + 3.5 * k:.1f} {wy - 3 * k:.1f}V{wy + 7 * k:.1f}Z" fill="{lit if on else "#141024"}"/>')
    return "".join(out)


def rose_painted(D, x, y, r, seed, look, ang=0):
    """An open wild/briar rose: five rounded petals in two shades with a golden boss of stamens."""
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = math.radians(ang + i * 72 + rnd.uniform(-8, 8))
        px, py = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
        c = look.color((math.cos(a) * 0.5, math.sin(a) * 0.5, 0.7), rnd)
        out.append(f'<path d="{K.blob(px, py, r * 0.62, r * 0.55, rnd.randint(0, 999), 0.15, 12, math.degrees(a))}" fill="{c}" stroke="{K.ramp(look.cols, 0.1)}" stroke-width="0.6"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.3:.1f}" fill="#F2C840"/>')
    for i in range(10):
        a = i * 0.628
        out.append(f'<circle cx="{x + math.cos(a) * r * 0.3:.1f}" cy="{y + math.sin(a) * r * 0.3:.1f}" r="{max(0.6, r * 0.06):.1f}" fill="#A86A10"/>')
    return "".join(out)


@plate("sleeping-beauty", 47, edge=1.8, bristle=0.35, grain=0.18)
def sleeping_beauty_plate():
    """A hundred years on: the castle on its hill asleep under a blue night, swallowed by a thicket of briar roses
    whose thorny canes climb to the towers; every rose open, every window but one dark."""
    D = K.Doc("slb")
    out = []
    out.append(K.sky(D, [(0, "#0A0E2A"), (0.4, "#1C2456"), (0.75, "#3E3C7A"), (1, "#6A5490")], 4701, 0, 600, n=180, op=(0.06, 0.16)))
    out.append(K.stars(4702, (10, 10, 590, 300), 110, r=(0.4, 1.4), op=(0.4, 1.0)))
    out.append(K.halo(D, 470, 150, 90, "#E8E8FF", 0.4) + '<circle cx="470" cy="150" r="22" fill="#FAF8EE"/>')
    out.append(K.cloud_bank(D, 160, 200, ["#2A2E60", "#4A4A84", "#8A84B8"], 4703, n=30, r=(30, 60), op=(0.2, 0.4), x0=300, x1=640, streaks=20))
    # hill
    hill = K.rough([(-20, 450), (100, 418), (220, 396), (330, 392), (450, 404), (620, 430)], 4704, 4, 10)
    out.append(f'<path d="{K.smooth_open(hill)} L620 610 L-20 610Z" fill="#1A1A38"/>')
    stone = K.Look(["#0E0C1E", "#1E1C36", "#34304E", "#4E4870", "#7A70A0", "#B8B0D8"], key=(0.7, -0.6, 0.5), amb=0.08, wrap=0.35, jit=0.04,
                   rim=("#E8E4FF", (0.8, -0.6), 0.6))
    slate = K.Look(["#0A0818", "#1A1430", "#2E2650", "#4A3E72", "#7A68A0"], key=(0.7, -0.6, 0.5), amb=0.06, wrap=0.35, rim=("#E8D8FF", (0.8, -0.6), 0.6))
    out.append(castle_painted(D, 300, 432, 4705, stone, slate, k=0.86))
    # the briar: thorny canes climbing the walls and towers
    rnd = random.Random(4706)
    cane = ["#0E1A10", "#1E3020", "#2E4A2A"]
    for i in range(26):
        x0 = rnd.uniform(160, 440)
        pts = [(x0, 470)]
        for k in range(8):
            px, py = pts[-1]
            pts.append((px + rnd.uniform(-22, 22), py - rnd.uniform(14, 34)))
        pts = [p for p in pts if p[1] > 200]
        out.append(K.taper(pts, rnd.uniform(3, 5), 0.8, rnd.choice(cane), 0.95))
        for (px, py) in pts[1:-1]:
            for _ in range(2):
                a = rnd.uniform(0, 6.28)
                out.append(f'<path d="M{px:.1f} {py:.1f}l{math.cos(a) * 5:.1f} {math.sin(a) * 5:.1f}" stroke="#0A120A" stroke-width="1.2"/>')
    # the thicket at the foot: dark leafy masses spangled with roses
    leaf = K.Look(["#03060A", "#0A1410", "#122218", "#1E3626", "#34503E", "#5A7468"], key=(0.7, -0.6, 0.5), amb=0.03, wrap=0.3, jit=0.05)
    out.append(K.foliage(D, [(60, 470, 110, 60), (200, 450, 100, 54), (330, 446, 110, 56), (470, 458, 110, 60), (590, 480, 70, 60),
                             (120, 540, 160, 70), (440, 540, 170, 70), (290, 560, 120, 60)], leaf, 4707, density=1.0, size=(3, 7)))
    rose = K.Look(["#4A0E2A", "#8A1E4A", "#C8406A", "#EE7A98", "#FFC0D0", "#FFE8EE"], key=(0.7, -0.6, 0.5), amb=0.1, wrap=0.4)
    for _ in range(56):
        x, y = rnd.uniform(-10, 610), rnd.uniform(420, 600)
        if 160 < x < 440 and y > 500:
            continue
        out.append(K.halo(D, x, y, 14, "#FF90B0", 0.25))
        out.append(rose_painted(D, x, y, rnd.uniform(6, 11), rnd.randint(0, 9999), rose, rnd.uniform(0, 72)))
    for _ in range(14):
        x, y = rnd.uniform(190, 410), rnd.uniform(240, 400)
        out.append(rose_painted(D, x, y, rnd.uniform(3, 5.5), rnd.randint(0, 9999), rose.darker(0.15), rnd.uniform(0, 72)))
    # drifting petals and a few fireflies of moonlight
    for _ in range(14):
        x, y = rnd.uniform(40, 560), rnd.uniform(220, 480)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="1.6" fill="#FFB8CC" opacity="0.8" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    art = D.render(out)
    DL = K.Doc("slbL")
    L = [K.halo(DL, 300, 86, 240, "#06081E", 0.6, ry=50)]
    L.append(K.subtitle(300, 62, "BRIAR ROSE · BROTHERS GRIMM", CINZEL, 15, "#D8D0F4", ls=3, max_w=380, sh="#000000", sop=0.7))
    L.append(K.title(DL, 300, 112, "Sleeping Beauty", SERIF_IT, 54, max_w=440, face=("#FFF2F6", "#F2B8CC", "#B8607A"), shadow="#04061A", sop=0.8))
    L.append(K.halo(DL, 300, 530, 260, "#04060E", 0.6, ry=26))
    L.append(K.subtitle(300, 538, "…and the whole castle slept a hundred years.", SERIF_IT, 19, "#FFE8F0", max_w=440, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: sleeping-beauty ----


# ---- plate: snow-white ----
@plate("snow-white", 71, edge=1.6, bristle=0.32, grain=0.18)
def snow_white_plate():
    """Midwinter, the queen's window: a frame of carved ebony, snow falling on a moonlit forest outside, and on
    the snowy sill three drops of blood beside the needle and an apple as red as them."""
    D = K.Doc("snw")
    out = []
    # the room: dark panelled wall around the window, warm candle glow from the left
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#140C0A"/>')
    out.append(K.halo(D, 60, 470, 300, "#C87A3A", 0.35))
    out.append(K.brushwork(7101, (-10, -10, 610, 610), ["#2A1A14", "#0A0604", "#3A2418"], 260, L=(30, 90), W=(2, 6), op=(0.2, 0.45), angle=90, jit=3))
    # the window opening (arched): outside, a moonlit winter wood
    WX0, WX1, WTOP, WBOT = 130, 470, 120, 430
    arch = [(WX0, WBOT), (WX0, WTOP + 110)] + [((WX0 + WX1) / 2 - math.cos(a) * (WX1 - WX0) / 2, WTOP + 110 - math.sin(a) * 110) for a in [k * math.pi / 24 for k in range(25)]] + [(WX1, WBOT)]
    cid = D.clip(K.poly_d(arch))
    o = []
    o.append(K.sky(D, [(0, "#0A1430"), (0.6, "#1E3058"), (1, "#3A5078")], 7102, WTOP - 10, WBOT, n=80, op=(0.05, 0.14)))
    o.append(K.halo(D, 390, 190, 90, "#DCE8FF", 0.45) + '<circle cx="390" cy="190" r="20" fill="#FAFAF0"/>')
    rnd = random.Random(7103)
    for k, (yb, col) in enumerate(((360, "#2E3E5E"), (390, "#1E2A44"), (420, "#121A2E"))):
        x = WX0 - 20
        while x < WX1 + 20:
            h = rnd.uniform(40, 110) * (1 + 0.3 * k)
            o.append(conifer(x, yb, h, col, rnd.randint(0, 9999), width=0.32))
            # snow on the boughs
            for j in range(4):
                yy = yb - h * (0.2 + 0.18 * j)
                ww = h * 0.32 * (1 - (0.2 + 0.18 * j)) * 0.9
                o.append(K.taper([(x - ww, yy + 2), (x, yy - 2), (x + ww * 0.6, yy + 1)], 2.2, 0.6, "#C8D4EC", 0.75))
            x += rnd.uniform(16, 30)
    o.append(f'<rect x="{WX0}" y="420" width="{WX1 - WX0}" height="20" fill="#B8C4DC"/>')
    for _ in range(140):
        x, y = rnd.uniform(WX0, WX1), rnd.uniform(WTOP, WBOT)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 2.2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    out.append(f'<g {cid}>{"".join(o)}</g>')
    # mullions and leaded panes
    pane = []
    for x in range(WX0, WX1 + 1, 34):
        pane.append(f'M{x} {WTOP}V{WBOT}')
    for y in range(WTOP, WBOT, 40):
        pane.append(f'M{WX0} {y}H{WX1}')
    out.append(f'<g {cid}><path d="{" ".join(pane)}" stroke="#0A0808" stroke-width="1.6" opacity="0.5"/></g>')
    out.append(f'<path d="M{(WX0 + WX1) / 2} {WTOP}V{WBOT}" stroke="#0E0A0A" stroke-width="8"/>')
    out.append(f'<path d="M{WX0} 290H{WX1}" stroke="#0E0A0A" stroke-width="6"/>')
    # the ebony frame: carved, black with a deep sheen
    ebony = K.Look(["#000000", "#060406", "#141014", "#2A2228", "#4A3E46", "#8A7A86"], key=(-0.8, 0.3, 0.5), amb=0.05, wrap=0.3,
                   rim=("#E8C090", (-0.9, 0.2), 0.7), spec=("#F8E8D8", 0.85, 0.6))
    outer = [(WX0 - 34, WBOT + 14), (WX0 - 34, WTOP + 110)] + [((WX0 + WX1) / 2 - math.cos(a) * ((WX1 - WX0) / 2 + 34), WTOP + 110 - math.sin(a) * 144) for a in [k * math.pi / 24 for k in range(25)]] + [(WX1 + 34, WBOT + 14)]
    frame = outer + arch[::-1]
    out.append(K.paint(D, frame, ebony, 7104, round_r=14, flow="contour", flow_jit=6, smooth=False, edge_col="#000000", edge_w=1.6,
                       rim_col="#E8C090", rim_w=1.6, rim_op=0.6, passes=((60, (10, 24), (2, 5), (0.3, 0.55)), (200, (5, 12), (1, 2), (0.35, 0.7)))))
    # carving: a running vine of leaves along the frame
    for k in range(40):
        t = k / 39
        a = math.pi * t
        r = (WX1 - WX0) / 2 + 17
        cx_ = (WX0 + WX1) / 2 - math.cos(a) * r
        cy_ = WTOP + 110 - math.sin(a) * (r + 10 * 0 + 17)
        if k % 2 == 0:
            out.append(f'<path d="{K.blob(cx_, cy_, 6, 2.6, k, 0.1, 10, math.degrees(a) + 60 * (1 if k % 4 else -1))}" fill="#1E181E" stroke="#000000" stroke-width="0.6"/>')
            out.append(f'<path d="{K.blob(cx_ - 1, cy_ - 1, 3, 1.0, k + 1, 0.1, 10, math.degrees(a) + 60 * (1 if k % 4 else -1))}" fill="#7A6A76" opacity="0.5"/>')
    for side in (WX0 - 17, WX1 + 17):
        vine = [(side + 4 * math.sin(k * 0.8), WTOP + 120 + k * 10) for k in range(32)]
        out.append(f'<path d="{K.smooth_open(vine)}" stroke="#000000" stroke-width="2.4" fill="none" opacity="0.8"/>')
        out.append(f'<path d="{K.smooth_open([(x - 1, y) for x, y in vine])}" stroke="#6A5A66" stroke-width="0.9" fill="none" opacity="0.6"/>')
        for k in range(2, 32, 4):
            x, y = vine[k]
            sd = 1 if (k // 4) % 2 else -1
            out.append(f'<path d="{K.blob(x + sd * 6, y, 6, 2.6, k, 0.1, 10, 30 * sd)}" fill="#1E181E" stroke="#000000" stroke-width="0.6"/>')
            out.append(f'<path d="{K.blob(x + sd * 6 - 1, y - 0.8, 3, 1, k + 1, 0.1, 10, 30 * sd)}" fill="#7A6A76" opacity="0.5"/>')
    # the sill: deep ebony ledge heaped with fresh snow
    sill = [(WX0 - 50, WBOT + 4), (WX1 + 50, WBOT + 4), (WX1 + 64, WBOT + 30), (WX0 - 64, WBOT + 30)]
    out.append(K.paint(D, sill, ebony, 7105, round_r=8, flow=0, smooth=False, edge_col="#000000", edge_w=1.6, rim_col="#E8C090", rim_w=1.4))
    snow = K.Look(["#6A7898", "#A0AECC", "#D6DEEE", "#F4F6FC", "#FFFFFF"], key=(-0.8, -0.4, 0.5), amb=0.2, wrap=0.45, rim=("#FFE0B8", (-0.9, -0.2), 0.6))
    drift = [(WX0 - 40, WBOT + 6), (WX0 - 30, WBOT - 8), (WX0 + 40, WBOT - 14), (300, WBOT - 10), (WX1 - 30, WBOT - 16), (WX1 + 40, WBOT - 6), (WX1 + 46, WBOT + 8)]
    out.append(K.paint(D, drift + [(WX0 - 40, WBOT + 10)], snow, 7106, round_r=8, flow=0, flow_jit=10, edge_col="#4A5470", edge_w=1, edge_op=0.4))
    # three drops of blood on the snow, an apple, the needle and red thread
    for (bx, by, r_) in ((236, WBOT - 8, 4.2), (252, WBOT - 5, 3.2), (266, WBOT - 9, 3.8)):
        out.append(f'<ellipse cx="{bx}" cy="{by}" rx="{r_ * 1.3:.1f}" ry="{r_ * 0.7:.1f}" fill="#9A0A14"/>')
        out.append(f'<ellipse cx="{bx - 1}" cy="{by - 1}" rx="{r_ * 0.5:.1f}" ry="{r_ * 0.22:.1f}" fill="#FF8A8A" opacity="0.8"/>')
    AX, AY, AR = 382, WBOT - 34, 30
    out.append(K.halo(D, AX + 8, AY + AR - 2, 44, "#2A3450", 0.5, ry=7))
    apple = [(AX + math.cos(a) * AR * (1 + 0.06 * math.cos(2 * a)), AY + math.sin(a) * AR * 0.94 + (4 if math.sin(a) < -0.9 else 0)) for a in [k * math.pi / 16 for k in range(32)]]
    red = K.Look(["#2A0206", "#5A0610", "#900E1C", "#C82030", "#EE5A5A", "#FFC8B8"], key=(-0.75, -0.5, 0.45), amb=0.04, wrap=0.3,
                 rim=("#FFC890", (-0.9, -0.2), 0.6), spec=("#FFFFFF", 0.9, 0.9))
    out.append(K.paint(D, apple, red, 7107, round_r=AR * 0.9, flow="contour", flow_jit=8, edge_col="#1A0204", edge_w=1.6, rim_col="#FFC890", rim_w=1.6,
                       passes=((80, (8, 16), (2, 4), (0.35, 0.6)), (300, (4, 9), (1, 2), (0.4, 0.8)))))
    out.append(f'<ellipse cx="{AX - 10}" cy="{AY - 12}" rx="7" ry="4" fill="#FFFFFF" opacity="0.8" transform="rotate(-30 {AX - 10} {AY - 12})"/>')
    out.append(K.taper([(AX + 2, AY - AR + 4), (AX + 4, AY - AR - 6), (AX + 8, AY - AR - 12)], 3, 1.6, "#3A2410", 1))
    out.append(f'<path d="{K.smooth_closed([(AX + 8, AY - AR - 6), (AX + 22, AY - AR - 16), (AX + 30, AY - AR - 10), (AX + 18, AY - AR - 2)])}" fill="#3E6A2A" stroke="#1A3010" stroke-width="0.8"/>')
    out.append(f'<path d="M{WX0 + 10} {WBOT - 14}L{WX0 + 70} {WBOT - 22}" stroke="#D8D8E0" stroke-width="1.6"/>')
    out.append(f'<path d="M{WX0 + 70} {WBOT - 22}Q{WX0 + 100} {WBOT - 40} {236} {WBOT - 10}" stroke="#B0141E" stroke-width="1.4" fill="none"/>')
    # candle on the left, its glow on frame and sill
    out.append(K.halo(D, 62, 380, 90, "#FFC060", 0.55))
    out.append(f'<rect x="54" y="392" width="16" height="70" fill="{D.lin([(0, "#E8DCC0"), (1, "#A8987A")], 0, 0, 1, 0)}"/>')
    out.append(f'<path d="{K.smooth_closed([(56, 392), (60, 374), (62, 364), (65, 374), (68, 392)])}" fill="#FFD070"/>')
    out.append(f'<path d="{K.smooth_closed([(59, 390), (61, 378), (62, 372), (64, 378), (65, 390)])}" fill="#FFF8D8"/>')
    art = D.render(out)
    DL = K.Doc("snwL")
    L = [K.halo(DL, 300, 80, 220, "#0A0606", 0.55, ry=40)]
    L.append(K.title(DL, 300, 90, "Snow White", SERIF_IT, 50, max_w=380, face=("#FFFFFF", "#E2E6F2", "#9AA2B8"), shadow="#000000", sop=0.85))
    L.append(K.subtitle(300, 112, "BROTHERS GRIMM · 1812", CINZEL, 15, "#E8D8C8", ls=3, max_w=300, sh="#000000", sop=0.7))
    L.append(K.halo(DL, 300, 520, 260, "#0A0606", 0.6, ry=34))
    L.append(K.subtitle(300, 516, "White as snow, red as blood,", SERIF_IT, 22, "#F4F0F0", max_w=420, sh="#000000", sop=0.8))
    L.append(K.subtitle(300, 540, "black as ebony.", SERIF_IT, 22, "#F4F0F0", max_w=420, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: snow-white ----


# ---- plate: cinderella ----
def glass_slipper_painted(D, x, y, s, seed):
    """A glass court shoe with a curved Louis heel, side view, toe to the right; clear glass rendered by its
    edges: a dark blue body that lets the night through, white rims along every edge that turns to the light,
    the far inner wall seen through the opening, internal streaks, refraction sparks and caustic light below."""
    rnd = random.Random(seed)
    T = lambda pts: K.xform(pts, x, y, s)
    outline = [(-52, -40), (-44, -46), (-36, -42), (-24, -30), (-8, -20), (10, -16), (28, -15), (44, -11), (56, -5), (63, 0), (60, 4),
               (40, 5), (20, 6), (4, 4), (-12, -2), (-26, -8), (-32, -7), (-34, -2), (-36, 4), (-38, 7), (-45, 7), (-46, 2), (-49, -8),
               (-54, -20), (-55, -30)]
    O = T(outline)
    out = []
    # caustic: the slipper focuses moonlight into a bright patch on the marble
    out.append(K.halo(D, x + 10 * s, y + 8 * s, 74 * s, "#DCEBFF", 0.5, ry=7 * s))
    out.append(K.halo(D, x + 24 * s, y + 8 * s, 26 * s, "#FFFFFF", 0.7, ry=2.5 * s))
    out.append(K.halo(D, x, y + 8 * s, 80 * s, "#000000", 0.35, ry=4 * s))
    g = D.lin([(0, "#D8E8FF", 0.7), (0.4, "#6A8AC8", 0.55), (1, "#1A2A5A", 0.75)], 0, 0, 0.2, 1)
    out.append(f'<path d="{K.smooth_closed(O)}" fill="{g}"/>')
    # the inside: the far wall of the shoe seen through the opening, and the insole
    inner = T([(-48, -38), (-40, -41), (-30, -32), (-14, -19), (8, -13), (30, -11), (46, -6), (40, -2), (10, -1), (-16, -9), (-38, -18), (-48, -28)])
    out.append(f'<path d="{K.smooth_closed(inner)}" fill="#9AB8F0" opacity="0.28"/>')
    out.append(K.taper(T([(-44, -14), (-24, -9), (0, -1), (20, 2), (44, 1)]), 2.6 * s, 1.0 * s, "#E8F2FF", 0.55))
    # rims of light along the edges: heavy where the edge turns toward the moon (upper left)
    fine = K.resample(O, 2)
    out.append(K.edges(fine, (-0.6, -0.8), seed, dark="#0A1430", lit="#FFFFFF", w=1.4 * s, dark_op=0.5, lit_op=0.95, lit_w=2.2 * s, lit_thresh=0.0))
    # the opening rim, a glass lip catching light along its whole length
    lip = T([(-52, -40), (-44, -46), (-36, -42), (-24, -30), (-8, -20), (10, -16), (28, -15), (44, -11)])
    out.append(K.taper(lip, 2.6 * s, 1.2 * s, "#FFFFFF", 0.95))
    out.append(K.taper(T([(-50, -36), (-40, -40), (-26, -28), (-6, -17)]), 1.2 * s, 0.4 * s, "#8AB0F0", 0.8))
    # internal streaks of reflection and the curved Louis heel catching the light
    for pts, w, o in (([(-30, -24), (-6, -12), (24, -8), (50, -3)], 1.6, 0.5), ([(-26, -14), (0, -4), (30, 0)], 1.0, 0.4),
                      ([(-46, -6), (-44, 0), (-43, 6)], 1.8, 0.85), ([(-35, -3), (-36, 2), (-37, 6)], 1.0, 0.5), ([(50, -6), (58, -1)], 1.6, 0.9)):
        out.append(K.taper(T(pts), w * s, 0.4 * s, "#FFFFFF", o))
    # toe facets
    out.append(f'<path d="{K.smooth_open(T([(36, -10), (44, -4), (48, 3)]))}" stroke="#C8DCFF" stroke-width="{0.9 * s:.1f}" fill="none" opacity="0.7"/>')
    for (px, py, r) in ((-44, -46, 12), (58, -4, 16), (-42, 7, 8), (14, -16, 7)):
        q = T([(px, py)])[0]
        out.append(K.halo(D, q[0], q[1], r * 1.6, "#DCEBFF", 0.55) + K.sparkle(q[0], q[1], r, "#FFFFFF", 0.95))
    return "".join(out)


@plate("cinderella", 61, edge=1.6, bristle=0.3, grain=0.16)
def cinderella_plate():
    """Midnight on the palace stair: behind, the great doors still blaze with the ball and the clock tower
    strikes twelve; in front of us, on a moonlit step, the glass slipper she left behind."""
    D = K.Doc("cnd")
    out = []
    out.append(K.sky(D, [(0, "#060A24"), (0.5, "#14204A"), (1, "#26345E")], 6101, 0, 600, n=120, op=(0.05, 0.14)))
    out.append(K.stars(6102, (10, 10, 590, 200), 90, r=(0.4, 1.4), op=(0.4, 1.0)))
    # out of focus behind: the palace front, the stair climbing to the glowing doors, the clock tower
    blur = D.blur(3.2)
    bg = []
    bg.append(f'<rect x="-20" y="150" width="640" height="200" fill="#3A4468"/>')
    for i in range(-1, 14):
        x = i * 48
        bg.append(f'<path d="M{x + 8} 180V270Q{x + 20} 250 {x + 32} 270V180Q{x + 20} 166 {x + 8} 180Z" fill="#FFD27A" opacity="0.8"/>')
    bg.append(f'<path d="M190 340V220Q250 170 310 220V340Z" fill="#FFE4A0"/>')
    for i in range(10):
        y = 340 + i * 13
        w = 140 + i * 40
        bg.append(f'<rect x="{250 - w:.0f}" y="{y}" width="{w * 2:.0f}" height="13" fill="{K.mix("#B8C0DC", "#4A5478", i / 10)}"/>')
        bg.append(f'<rect x="{250 - w:.0f}" y="{y}" width="{w * 2:.0f}" height="2" fill="#F0F4FF" opacity="0.7"/>')
    bg.append(f'<path d="M430 160V40H520V160Z" fill="#4A5478"/><path d="M424 40L475 0L526 40Z" fill="#2A3058"/>')
    out.append(f'<g {blur}>{"".join(bg)}</g>')
    out.append(K.halo(D, 250, 270, 190, "#FFC060", 0.5))
    CX, CY, CR = 475, 96, 30
    out.append(K.halo(D, CX, CY, 60, "#FFF2C0", 0.35))
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{CR + 4}" fill="#B89048" opacity="0.9"/>')
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{CR}" fill="{D.rad([(0, "#FFFCEC"), (1, "#EADAA8")])}" opacity="0.95"/>')
    for h in range(12):
        a = math.radians(h * 30 - 90)
        out.append(f'<path d="M{CX + math.cos(a) * CR * 0.76:.1f} {CY + math.sin(a) * CR * 0.76:.1f}L{CX + math.cos(a) * CR * 0.92:.1f} {CY + math.sin(a) * CR * 0.92:.1f}" stroke="#3A2A10" stroke-width="{2.2 if h % 3 == 0 else 1.1}" opacity="0.85"/>')
    out.append(f'<path d="M{CX} {CY + 4}V{CY - CR * 0.6}" stroke="#1A0E04" stroke-width="3" stroke-linecap="round"/><path d="M{CX} {CY + 6}V{CY - CR * 0.84}" stroke="#1A0E04" stroke-width="1.6" stroke-linecap="round"/>')
    # the near steps, sharp: marble, moonlit nosings, warm light from the doors down the middle
    marble = K.Look(["#141A30", "#283050", "#444E72", "#6A7498", "#9AA4C4", "#D8DEF0"], key=(-0.5, -0.8, 0.4), amb=0.1, wrap=0.4, jit=0.04)
    for i, (y0, y1) in enumerate(((396, 428), (428, 470), (470, 524), (524, 610))):
        tread = [(-20, y0), (620, y0), (620, y1 - 8), (-20, y1 - 8)]
        riser = [(-20, y1 - 8), (620, y1 - 8), (620, y1), (-20, y1)]
        out.append(K.paint(D, tread, marble, 6120 + i, round_r=40, flow=0, flow_jit=3, smooth=False, edge_col=None, value_fn=lambda x, y: 0.1,
                           passes=((40, (30, 80), (2, 5), (0.25, 0.5)),)))
        out.append(f'<path d="{K.poly_d(riser)}" fill="#141A30"/>')
        out.append(f'<path d="M-20 {y0 + 1}H620" stroke="#F0F4FF" stroke-width="2" opacity="0.75"/>')
        out.append(K.brushwork(6130 + i, (-20, y0, 620, y1 - 8), ["#8A94B8", "#E8ECF8", "#3A4466"], 30, L=(30, 120), W=(0.5, 1.2), op=(0.2, 0.45), angle=lambda x, y: 8 * math.sin(x * 0.02), jit=6))
    out.append(K.shafts(D, (250, 330), [(150, 360, 610)], "#FFD890", 0.18))
    # the slipper, hero of the plate
    out.append(glass_slipper_painted(D, 304, 440, 2.6, 6105))
    art = D.render(out)
    DL = K.Doc("cndL")
    L = [K.halo(DL, 210, 92, 200, "#04061A", 0.6, ry=48)]
    L.append(K.title(DL, 210, 100, "Cinderella", SERIF_IT, 58, max_w=320, face=("#F4F8FF", "#C8D8F4", "#7A8EC0"), shadow="#000010", sop=0.8))
    L.append(K.subtitle(210, 128, "AT THE STROKE OF MIDNIGHT", CINZEL, 15, "#E8E0C8", ls=2.5, max_w=310, sh="#000010", sop=0.75))
    L.append(K.halo(DL, 300, 534, 250, "#04061A", 0.55, ry=24))
    L.append(K.subtitle(300, 540, "“If the shoe fits…”", SERIF_IT, 23, "#FFF4D8", max_w=400, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: cinderella ----


# ---- plate: goldilocks ----
def bowl_painted(D, cx, cy, rx, depth, seed, glaze, band, filled=True, steam=False, light=(-0.8, -0.4)):
    """A glazed earthenware bowl seen from a little above: the rim an ellipse, the curved body modelled by the light
    from the window, a painted band, porridge inside (or a scraped-clean bowl), a soft cast shadow."""
    rnd = random.Random(seed)
    ry = rx * 0.4
    out = [K.halo(D, cx + rx * 0.25, cy + depth + ry * 0.4, rx * 1.3, "#2A1408", 0.5, ry=ry * 0.9)]
    body = [(cx - rx, cy)] + [(cx - rx * math.cos(a) * (1 - 0.15 * math.sin(a)), cy + math.sin(a) * depth) for a in [k * math.pi / 20 for k in range(1, 20)]] + [(cx + rx, cy)]
    body += [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in [k * math.pi / 20 for k in range(1, 20)]][::-1][::-1]
    body = [(cx - rx, cy)] + [(cx - rx * math.cos(a) * (1 - 0.18 * math.sin(a) ** 2), cy + math.sin(a) * depth) for a in [k * math.pi / 24 for k in range(1, 24)]] + \
           [(cx + rx, cy)] + [(cx + rx * math.cos(a), cy - ry * math.sin(a)) for a in [k * math.pi / 24 for k in range(1, 24)]]
    lk = K.Look(glaze, key=(light[0], light[1], 0.5), amb=0.1, wrap=0.4, spec=("#FFFFFF", 0.85, 0.8), rim=("#FFE6B0", light, 0.5))
    out.append(K.paint(D, body, lk, seed, round_r=rx * 0.7, flow="contour", flow_jit=6, edge_col="#2A1408", edge_w=1.4, edge_op=0.6, smooth=False,
                       passes=((60, (8, 18), (2, 4), (0.35, 0.6)), (240, (4, 9), (1, 2), (0.4, 0.8)))))
    # painted band around the belly, following the curve
    bp = [(cx - rx * math.cos(a) * 0.96, cy + math.sin(a) * depth * 0.45) for a in [k * math.pi / 24 for k in range(1, 24)]]
    out.append(f'<path d="{K.smooth_open(bp)}" stroke="{band}" stroke-width="{max(2, rx * 0.08):.1f}" fill="none" opacity="0.85"/>')
    for k in range(3, 22, 3):
        a = k * math.pi / 24
        px, py = cx - rx * math.cos(a) * 0.96, cy + math.sin(a) * depth * 0.45
        out.append(f'<circle cx="{px:.1f}" cy="{py + rx * 0.09:.1f}" r="{rx * 0.035:.1f}" fill="{band}" opacity="0.8"/>')
    # rim and inside
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry:.1f}" fill="{K.ramp(glaze, 0.75)}" stroke="#2A1408" stroke-width="1.2"/>')
    if filled:
        g = D.rad([(0, "#FFF6DC"), (0.6, "#EAD2A2"), (1, "#B8946A")], 0.4, 0.4, 0.6)
        out.append(f'<ellipse cx="{cx}" cy="{cy + ry * 0.12:.1f}" rx="{rx * 0.9:.1f}" ry="{ry * 0.78:.1f}" fill="{g}"/>')
        for _ in range(int(rx / 2)):
            a = rnd.uniform(0, 6.28)
            rr = rnd.uniform(0, 0.8)
            x, y = cx + math.cos(a) * rx * 0.85 * rr, cy + ry * 0.12 + math.sin(a) * ry * 0.7 * rr
            out.append(K.dab(x, y, rnd.uniform(1, 3), rnd.choice(["#FFFDF0", "#D8B888", "#C8A070"]), 0.5, rnd))
        out.append(f'<ellipse cx="{cx - rx * 0.2:.1f}" cy="{cy:.1f}" rx="{rx * 0.18:.1f}" ry="{ry * 0.16:.1f}" fill="#E8B040" opacity="0.8"/>')
    else:
        g = D.rad([(0, K.ramp(glaze, 0.85)), (1, K.ramp(glaze, 0.45))], 0.5, 0.3, 0.7)
        out.append(f'<ellipse cx="{cx}" cy="{cy + ry * 0.12:.1f}" rx="{rx * 0.9:.1f}" ry="{ry * 0.78:.1f}" fill="{g}"/>')
        for k in range(4):
            out.append(f'<path d="M{cx - rx * 0.5 + k * 6:.1f} {cy - ry * 0.2:.1f}q{rx * 0.3:.1f} {ry * 0.6:.1f} {rx * 0.7:.1f} {ry * 0.2:.1f}" stroke="#E8D2A8" stroke-width="1.4" fill="none" opacity="0.6"/>')
    out.append(f'<path d="M{cx - rx * 0.8:.1f} {cy - ry * 0.55:.1f}Q{cx - rx * 0.2:.1f} {cy - ry * 1.1:.1f} {cx + rx * 0.5:.1f} {cy - ry * 0.75:.1f}" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.7"/>')
    if steam:
        for k in range(3):
            x0 = cx - rx * 0.3 + k * rx * 0.3
            pts = [(x0 + 6 * math.sin(t * 1.3 + k), cy - 6 - t * 12) for t in range(7)]
            out.append(K.taper(pts, 5, 1, "#FFFFFF", 0.35))
    return "".join(out)


def spoon_painted(D, x0, y0, x1, y1, w, seed):
    """A carved wooden spoon from handle end (x0, y0) to bowl (x1, y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    L = math.hypot(x1 - x0, y1 - y0)
    out = [K.taper([(x0, y0), (x0 + ux * L * 0.7, y0 + uy * L * 0.7)], w * 0.5, w * 0.35, "#8A5A2A", 1)]
    out.append(K.taper([(x0 - nx, y0 - ny), (x0 + ux * L * 0.7 - nx, y0 + uy * L * 0.7 - ny)], w * 0.2, w * 0.1, "#E8B878", 0.7))
    bx, by = x0 + ux * L * 0.86, y0 + uy * L * 0.86
    out.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{L * 0.15:.1f}" ry="{w * 0.9:.1f}" fill="{D.rad([(0, "#E8B878"), (1, "#7A4A20")])}" transform="rotate({math.degrees(a):.1f} {bx:.1f} {by:.1f})" stroke="#3A1E08" stroke-width="0.8"/>')
    return "".join(out)


@plate("goldilocks", 37, edge=1.6, bristle=0.35, grain=0.2)
def goldilocks_plate():
    """The bears' cottage on a summer morning: three bowls of porridge on the scrubbed table in the window light,
    the great bowl steaming, the middle one too cold, the little one scraped clean, a spoon left in it; the little
    chair behind, broken."""
    D = K.Doc("gdl")
    out = []
    # back wall: whitewashed plaster over timber, a deep window full of green woodland light
    out.append(f'<rect x="-10" y="-10" width="620" height="420" fill="{D.lin([(0, "#E8D8B8"), (1, "#B89C74")], 0, 0, 1, 0)}"/>')
    out.append(K.brushwork(3701, (-10, -10, 610, 410), ["#F4E8CC", "#C8B08A", "#D8C4A0"], 200, L=(20, 60), W=(3, 8), op=(0.15, 0.35), angle=lambda x, y: 20 * math.sin(y * 0.03), jit=30))
    beam = K.Look(["#1E120A", "#3A2414", "#5E3C22", "#8A5E36"], key=(-0.8, -0.3, 0.5), amb=0.1)
    out.append(K.paint(D, [(-10, 20), (610, 20), (610, 50), (-10, 50)], beam, 3702, round_r=10, flow=0, smooth=False, edge_col="#0E0804"))
    for x in (40, 560):
        out.append(K.paint(D, [(x - 14, 50), (x + 14, 50), (x + 14, 410), (x - 14, 410)], beam, 3703 + x, round_r=10, flow=90, smooth=False, edge_col="#0E0804"))
    WX0, WX1, WY0, WY1 = 90, 330, 80, 300
    out.append(f'<rect x="{WX0 - 10}" y="{WY0 - 10}" width="{WX1 - WX0 + 20}" height="{WY1 - WY0 + 20}" fill="#5A3A20"/>')
    cid = D.clip(f"M{WX0} {WY0}H{WX1}V{WY1}H{WX0}Z")
    o = [K.sky(D, [(0, "#F4F8E0"), (0.6, "#C8DCA0"), (1, "#8AAA60")], 3704, WY0, WY1, n=60, op=(0.05, 0.12))]
    rnd = random.Random(3705)
    fl = K.Look(["#2A4420", "#4A6A30", "#7A9A48", "#B8CC78", "#E8F0B8"], key=(-0.6, -0.7, 0.5), amb=0.1, wrap=0.4)
    o.append(K.foliage(D, [(WX0 + 30, WY0 + 40, 60, 50), (WX0 + 140, WY0 + 20, 70, 40), (WX1 - 20, WY0 + 70, 50, 60), (WX0 + 80, WY1 - 20, 90, 40)], fl.toward("#F0F4D0", 0.35),
                        3706, size=(2.5, 6), density=0.9))
    for x in (WX0 + 70, WX0 + 170):
        o.append(f'<rect x="{x}" y="{WY0}" width="10" height="{WY1 - WY0}" fill="#5A4430" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(o)}</g>')
    out.append(f'<path d="M{(WX0 + WX1) / 2} {WY0}V{WY1}M{WX0} {(WY0 + WY1) / 2}H{WX1}" stroke="#4A2E18" stroke-width="7"/>')
    out.append(f'<rect x="{WX0 - 20}" y="{WY1 + 4}" width="{WX1 - WX0 + 40}" height="14" fill="#7A5230"/>')
    # sunlight falling through the window across the room
    out.append(K.shafts(D, (WX0 + 40, WY0 + 20), [(330, 600, 470), (260, 380, 470)], "#FFF4C8", 0.3))
    # the little chair against the wall, one leg broken off
    ch = K.Look(["#2A180C", "#4E3018", "#7A5028", "#A8743E", "#D0A06A"], key=(-0.8, -0.4, 0.5), amb=0.1, wrap=0.35)
    for (x0, y0, x1, y1, w) in ((452, 230, 456, 336, 7), (506, 228, 504, 336, 7), (454, 300, 470, 340, 6), (504, 300, 500, 340, 6)):
        out.append(K.paint(D, K.limb_outline([(x0, y0, w), (x1, y1, w)], cap=0.2), ch, 3710 + x0 + y0, round_r=3, flow="contour", edge_col="#140A04", edge_w=1))
    out.append(K.paint(D, [(444, 296), (516, 292), (520, 304), (440, 308)], ch, 3711, round_r=4, flow=0, smooth=False, edge_col="#140A04"))
    for k in range(3):
        out.append(f'<path d="M{458 + k * 16} 240V292" stroke="#5E3A1C" stroke-width="4"/>')
    out.append(f'<path d="M450 236Q480 226 510 234" stroke="#7A5028" stroke-width="7" fill="none"/>')
    out.append(K.paint(D, K.limb_outline([(520, 360, 6), (560, 352, 5)], cap=0.2), ch, 3712, round_r=3, flow="contour", edge_col="#140A04"))
    # the table: scrubbed pale wood, seen from a little above, running out of the bottom of the picture
    top = [(-20, 372), (620, 372), (640, 610), (-40, 610)]
    tw = K.Look(["#4A2E16", "#7A5430", "#A88050", "#CCA878", "#ECD2A4"], key=(-0.8, -0.5, 0.6), amb=0.15, wrap=0.4)
    out.append(K.paint(D, top, tw, 3713, round_r=60, flow=0, flow_jit=3, smooth=False, edge_col="#2A1608", edge_w=1.4,
                       value_fn=lambda x, y: 0.15 * max(0, 1 - abs(x - 400) / 300), passes=((60, (30, 80), (2, 5), (0.3, 0.55)), (200, (14, 40), (0.8, 1.8), (0.3, 0.6)))))
    for k in range(6):
        y = 396 + k * 40
        out.append(f'<path d="M-20 {y}H620" stroke="#5A3A1C" stroke-width="1.2" opacity="0.4"/>')
    out.append(f'<rect x="-20" y="364" width="640" height="10" fill="#6A4424"/>')
    # three bowls: great, middle, little (scraped clean, spoon in it); a honey pot
    out.append(bowl_painted(D, 154, 420, 108, 74, 3720, ["#1E2A44", "#34466A", "#5A72A0", "#8EA6CC", "#D8E4F4"], "#E8D8A0", steam=True))
    out.append(bowl_painted(D, 356, 440, 80, 56, 3721, ["#3E1A10", "#6E3020", "#A85038", "#D88A68", "#F4C8A8"], "#F2E0B0"))
    out.append(bowl_painted(D, 486, 466, 54, 38, 3722, ["#2A3A1E", "#46602E", "#6E8E48", "#A8C080", "#E0EAC8"], "#F8F0D0", filled=False))
    out.append(spoon_painted(D, 548, 430, 484, 470, 9, 3723))
    out.append(spoon_painted(D, 260, 410, 190, 416, 11, 3724))
    # honey pot and a fallen golden hair on the table
    hp = [(78, 372), (66, 344), (74, 322), (108, 322), (116, 344), (104, 372)]
    out.append(K.paint(D, hp, K.Look(["#3A2008", "#7A4810", "#C88A20", "#F2C050", "#FFE8A0"], key=(-0.8, -0.5, 0.5), amb=0.1, spec=("#FFFFFF", 0.85, 0.8)),
                       3725, round_r=16, flow="contour", edge_col="#2A1404"))
    out.append(f'<path d="M{250} 506Q{310} 488 {360} 504T{440} 500" stroke="#F2C650" stroke-width="1.4" fill="none" opacity="0.9"/>')
    art = D.render(out)
    DL = K.Doc("gdlL")
    L = [K.halo(DL, 438, 116, 140, "#FFF6E0", 0.6, ry=70)]
    L.append(K.title(DL, 438, 120, "Goldilocks", SERIF_IT, 52, max_w=200, face=("#E8B848", "#B07818", "#6A4208"), shadow="#FFF6E0", sop=0.8))
    L.append(K.subtitle(438, 150, "AND THE THREE BEARS", CINZEL, 15, "#4A2E14", ls=2, max_w=200, sh="#FFF6E0", sop=0.6))
    L.append(K.halo(DL, 300, 534, 260, "#2A1608", 0.5, ry=24))
    L.append(K.subtitle(300, 540, "“This porridge is just right!”", SERIF_IT, 23, "#FFF4D8", max_w=420, sh="#1A0A02", sop=0.85))
    return art, DL.render(L)
# ---- end plate: goldilocks ----


# ---- plate: aladdin ----
def oil_lamp_painted(D, cx, cy, s, seed, look):
    """A brass oil lamp (the classic 'magic lamp'): low oval body, long tapering spout with a wick, a curled
    handle, a domed lid with a finial; polished metal with sharp highlights and warm reflections."""
    T = lambda pts: K.xform(pts, cx, cy, s)
    out = [K.halo(D, cx, cy + 18 * s, 70 * s, "#000000", 0.5, ry=8 * s)]
    handle = T([(-44, -4), (-60, -12), (-64, -24), (-56, -32), (-46, -26), (-50, -18), (-42, -12)])
    out.append(K.paint(D, handle, look.darker(0.1), seed + 1, round_r=3 * s, flow="contour", edge_col="#2A1404", edge_w=1.2))
    body = T([(-48, 0), (-44, -12), (-30, -20), (-6, -22), (14, -18), (30, -12), (52, -16), (74, -22), (88, -24), (90, -20), (78, -14), (56, -4),
              (40, 4), (20, 10), (-10, 12), (-34, 10)])
    out.append(K.paint(D, body, look, seed, round_r=12 * s, bumps=[(*T([(-8, -4)])[0], 34 * s, 14 * s, 0, 6 * s)], flow="contour", flow_jit=6,
                       edge_col="#2A1404", edge_w=1.6, rim_col="#FFF0B0", rim_w=1.4, rim_op=0.6,
                       passes=((60, (8, 18), (2, 4), (0.35, 0.6)), (240, (4, 9), (1, 2), (0.4, 0.8)))))
    foot = T([(-22, 10), (16, 10), (12, 18), (-18, 18)])
    out.append(K.paint(D, foot, look.darker(0.15), seed + 2, round_r=3 * s, flow=0, edge_col="#2A1404", edge_w=1.2, smooth=False))
    lid = T([(-26, -18), (-20, -30), (-8, -36), (6, -34), (14, -22)])
    out.append(K.paint(D, lid, look.darker(-0.05), seed + 3, round_r=5 * s, flow="contour", edge_col="#2A1404", edge_w=1.2, rim_col="#FFF0B0", rim_w=1.2))
    fin = T([(-6, -36), (-4, -44), (-1, -48), (2, -44), (4, -36)])
    out.append(K.paint(D, fin, look, seed + 4, round_r=2 * s, flow="contour", edge_col="#2A1404", edge_w=1))
    # engraved arabesque band, highlights
    out.append(f'<path d="{K.smooth_open(T([(-40, -6), (-20, -10), (0, -10), (20, -6), (36, -2)]))}" stroke="#7A4A10" stroke-width="{1.2 * s:.1f}" fill="none" opacity="0.7"/>')
    for k in range(6):
        p = T([(-34 + k * 12, -8 + (2 if k % 2 else 0))])[0]
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{1.4 * s:.1f}" fill="none" stroke="#7A4A10" stroke-width="0.8"/>')
    out.append(K.taper(T([(-30, -16), (-8, -19), (10, -16)]), 2.2 * s, 0.8 * s, "#FFFCE8", 0.9))
    out.append(K.taper(T([(56, -14), (76, -20), (86, -22)]), 1.4 * s, 0.6 * s, "#FFFCE8", 0.85))
    return "".join(out)


@plate("aladdin", 11, edge=1.6, bristle=0.32, grain=0.18)
def aladdin_plate():
    """Down in the enchanted cave under the hills: heaps of gold and gems in a blue darkness, light falling from
    the opening far above; on the highest heap the old brass lamp, a thread of blue smoke curling up from its spout."""
    D = K.Doc("ald")
    out = []
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#06101C"/>')
    # cave walls, rock modelled by cool light from above
    rock = K.Look(["#02060C", "#081422", "#122438", "#1E3A52", "#2E5470", "#4A7896"], key=(0.2, -0.95, 0.4), amb=0.05, wrap=0.3, jit=0.05)
    for pts, sd in (([(-20, -20), (180, -20), (150, 60), (120, 160), (90, 300), (60, 420), (-20, 460)], 1101),
                    ([(620, -20), (430, -20), (470, 80), (500, 180), (520, 320), (560, 420), (620, 460)], 1102)):
        out.append(K.paint(D, K.rough(pts + [pts[0]], sd, 6, 12)[:-1], rock, sd, round_r=60, flow="contour", flow_jit=30, edge_col="#000000", edge_w=1.4,
                           passes=((40, (20, 40), (3, 7), (0.3, 0.55)), (160, (8, 20), (1.2, 3), (0.3, 0.6)))))
    # the opening far above: a shaft of moonlight
    out.append(K.shafts(D, (300, -20), [(200, 420, 520)], "#B8E0FF", 0.28))
    out.append(K.halo(D, 300, 0, 120, "#DCF0FF", 0.5, ry=40))
    # gems glinting in the walls
    rnd = random.Random(1103)
    for _ in range(40):
        x = rnd.choice([rnd.uniform(10, 150), rnd.uniform(450, 590)])
        y = rnd.uniform(40, 440)
        c = rnd.choice(["#3AE0C0", "#E83A6A", "#F2C840", "#5A8AF0", "#9AF07A"])
        out.append(K.halo(D, x, y, 7, c, 0.6) + f'<path d="M{x:.1f} {y - 3:.1f}l3 3l-3 3l-3 -3Z" fill="{c}"/>')
    # heaps of treasure: coins as overlapping lit ellipses, cups, a casket
    gold = ["#3A2002", "#7A4A08", "#C88A18", "#F2C040", "#FFE89A", "#FFFBE0"]
    for (cx, cy, w, h, n) in ((300, 470, 300, 110, 900), (110, 520, 200, 80, 400), (500, 520, 220, 80, 420)):
        heap = [(cx + math.cos(a) * w / 2, cy - max(0, math.sin(-a)) * h) for a in [math.pi + k * math.pi / 20 for k in range(21)]] + [(cx + w / 2, cy + 30), (cx - w / 2, cy + 30)]
        out.append(f'<path d="{K.smooth_closed(heap)}" fill="{D.lin([(0, "#E8B030"), (1, "#5A3406")], 0, 0, 0, 1)}"/>')
        for _ in range(n):
            t = rnd.random()
            x = cx + rnd.uniform(-0.5, 0.5) * w * (1 - t * 0.6)
            yt = cy - h * (1 - (2 * (x - cx) / w) ** 2) if abs(x - cx) < w / 2 else cy
            y = rnd.uniform(yt, cy + 30)
            lit = 0.25 + 0.7 * (1 - (y - yt) / max(1, cy + 30 - yt)) + rnd.uniform(-0.15, 0.15)
            r = rnd.uniform(3, 6.5)
            c = K.ramp(gold, lit)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.45:.1f}" fill="{c}" stroke="{K.ramp(gold, lit - 0.3)}" stroke-width="0.6" transform="rotate({rnd.uniform(-25, 25):.0f} {x:.1f} {y:.1f})"/>')
            if rnd.random() < 0.06:
                out.append(K.sparkle(x, y - 1, rnd.uniform(4, 8), "#FFFFFF", 0.9))
    # jewels spilling over the gold: a few cut stones
    for _ in range(18):
        x, y = rnd.uniform(150, 450), rnd.uniform(410, 520)
        c = rnd.choice(["#18A8A0", "#C8103A", "#2A5AE0", "#20A040"])
        out.append(f'<path d="M{x:.1f} {y - 5:.1f}l5 4l-2 5h-6l-2 -5Z" fill="{c}" stroke="#000" stroke-width="0.5"/><path d="M{x - 2:.1f} {y - 3:.1f}l2 -1.5l2 1.5" stroke="#FFFFFF" stroke-width="0.8" fill="none"/>')
    # the lamp on the summit of the heap, catching the shaft of light
    out.append(K.halo(D, 300, 350, 110, "#FFE6A0", 0.35))
    brass = K.Look(["#2A1402", "#5A3008", "#946018", "#C89030", "#ECC060", "#FFF0B0"], key=(0.15, -0.95, 0.4), amb=0.05, wrap=0.3,
                   spec=("#FFFFFF", 0.86, 0.9), rim=("#C8E8FF", (0.1, -1.0), 0.5))
    out.append(oil_lamp_painted(D, 284, 360, 2.0, 1104, brass))
    # the thread of blue smoke from the spout, curling up into a vast faint swirl
    sp = (284 + 90 * 2.0, 360 - 23 * 2.0)
    smoke = [sp]
    for k in range(1, 18):
        t = k / 17
        smoke.append((sp[0] + 40 * math.sin(t * 6) * t - 60 * t, sp[1] - 300 * t))
    out.append(K.hair(smoke, 40, lambda t: 2 + 40 * t ** 1.5, 1105, ["#6AD8F0", "#3A9AD8", "#B8F0FF", "#8A6AE8"], w=(1.2, 4), op=(0.15, 0.45), start=(0, 0.1), end=(0.6, 1.0), wave=0.6))
    out.append(K.taper(smoke[:8], 3.2, 1.2, "#A8F0FF", 0.7))
    for _ in range(26):
        k = rnd.randint(3, 17)
        x, y = smoke[k]
        out.append(f'<circle cx="{x + rnd.uniform(-30, 30):.1f}" cy="{y + rnd.uniform(-10, 10):.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="#E8FCFF" opacity="0.8"/>')
    art = D.render(out)
    DL = K.Doc("aldL")
    L = [K.halo(DL, 300, 92, 220, "#030810", 0.6, ry=48)]
    L.append(K.title(DL, 300, 102, "ALADDIN", CINZEL, 58, max_w=400, ls=10, face=("#FFF4C8", "#F0C050", "#9A6410"), shadow="#000000", sop=0.8))
    L.append(K.subtitle(300, 130, "THE THOUSAND AND ONE NIGHTS", CINZEL, 15, "#C8E8F0", ls=2.5, max_w=380, sh="#000000", sop=0.75))
    L.append(K.halo(DL, 300, 534, 220, "#030810", 0.6, ry=24))
    L.append(K.subtitle(300, 540, "“New lamps for old!”", SERIF_IT, 24, "#FFEFC0", max_w=400, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: aladdin ----


# ---- plate: ali-baba ----
@plate("ali-baba", 31, edge=1.8, bristle=0.35, grain=0.2)
def ali_baba_plate():
    """Dusk in a red desert canyon: at the word the great round stone has rolled aside from the cliff, and the
    robbers' cave blazes with lamplight and treasure; the oil jars of the forty thieves wait in a line outside."""
    D = K.Doc("alb")
    out = []
    out.append(K.sky(D, [(0, "#1A1240"), (0.4, "#4A2A68"), (0.75, "#C8607A"), (1, "#F8B080")], 3101, 0, 300, n=140, op=(0.06, 0.16)))
    out.append(K.stars(3102, (10, 10, 590, 160), 60, r=(0.4, 1.3), op=(0.4, 0.95)))
    out.append(f'<path d="M462 70a18 18 0 1 0 14 30a14 14 0 1 1 -14 -30Z" fill="#FFF4D8"/>')
    out.append(K.halo(D, 462, 88, 40, "#FFF0D0", 0.35))
    # far mesas
    for k, (pts, col) in enumerate((([(-20, 300), (40, 250), (120, 248), (150, 280), (260, 286), (300, 240), (380, 236), (420, 280), (620, 290), (620, 320), (-20, 320)], "#7A4A6A"),)):
        out.append(f'<path d="{K.poly_d(K.rough(pts, 3103, 2, 8))}" fill="{col}"/>')
    # the canyon walls: banded sandstone, lit warm at the top, deep shadow below
    rock = K.Look(["#1A0808", "#3A140E", "#6A2A18", "#A04A28", "#D47A44", "#F4B07A"], key=(-0.6, -0.8, 0.4), amb=0.05, wrap=0.3, jit=0.05,
                  rim=("#FFC890", (-0.7, -0.7), 0.6))
    cliff = K.rough([(-20, 610), (-20, 300), (40, 268), (100, 214), (170, 186), (260, 172), (350, 168), (430, 184), (500, 220), (560, 262), (620, 280), (620, 610)], 3104, 5, 12)
    out.append(K.paint(D, cliff, rock, 3105, round_r=90, flow=lambda x, y, n: 4 * math.sin(y * 0.05), flow_jit=8, smooth=False, edge_col="#0A0202", edge_w=2,
                       rim_col="#FFC890", rim_w=2, rim_op=0.6, value_fn=lambda x, y: -0.35 * max(0, (y - 300) / 300) + 0.25 * max(0, 1 - math.hypot(x - 320, y - 400) / 160),
                       passes=((40, (30, 70), (3, 7), (0.3, 0.55)), (160, (14, 36), (1.2, 3), (0.3, 0.6)))))
    cid = D.clip(K.poly_d(cliff))
    bands = []
    rnd = random.Random(3106)
    for y in range(200, 610, 14):
        pts = [(x, y + 5 * math.sin(x * 0.02 + y)) for x in range(-20, 640, 20)]
        bands.append(f'<path d="{K.smooth_open(pts)}" stroke="{rnd.choice(["#2A0E08", "#E89A60", "#7A3418"])}" stroke-width="{rnd.uniform(1, 3):.1f}" fill="none" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    out.append(f'<g {cid}>{"".join(bands)}</g>')
    # the cave mouth, blazing
    CX, CY = 320, 400
    mouth = [(CX - 70, 470), (CX - 72, CY - 10), (CX - 50, CY - 60), (CX, CY - 80), (CX + 50, CY - 60), (CX + 72, CY - 10), (CX + 70, 470)]
    out.append(K.halo(D, CX, CY + 20, 200, "#FFB040", 0.5))
    out.append(f'<path d="{K.smooth_closed(mouth)}" fill="{D.rad([(0, "#FFFCE0"), (0.4, "#FFD070"), (0.8, "#E87A20"), (1, "#7A2A08")], 0.5, 0.7, 0.7)}"/>')
    inner = []
    for _ in range(160):
        x = rnd.uniform(CX - 60, CX + 60)
        y = rnd.uniform(CY + 20, 470)
        if abs(x - CX) < 60 - (470 - y) * 0.1:
            inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(2, 5):.1f}" ry="{rnd.uniform(1, 2):.1f}" fill="{rnd.choice(["#FFF4C0", "#F2B830", "#C87810"])}"/>')
    out.append("".join(inner))
    for (x, y, c) in ((CX - 30, 440, "#E83A5A"), (CX + 22, 446, "#3AC8B8"), (CX - 4, 430, "#5A8AF0")):
        out.append(K.sparkle(x, y, 8, "#FFFFFF", 0.9) + f'<circle cx="{x}" cy="{y}" r="3" fill="{c}"/>')
    # the great stone door, rolled aside
    stone = [(CX + 70 + math.cos(a) * 64, CY + 6 + math.sin(a) * 64) for a in [k * math.pi / 16 for k in range(32)]]
    sl = K.Look(["#1A0A06", "#3A1A10", "#6A3420", "#9A5A36", "#C8885A"], key=(-0.8, -0.5, 0.5), amb=0.05, wrap=0.3, rim=("#FFC060", (-1, 0), 0.8))
    out.append(K.paint(D, stone, sl, 3107, round_r=60, flow="contour", flow_jit=20, edge_col="#0A0202", edge_w=2, rim_col="#FFC060", rim_w=2.4, rim_op=0.8))
    out.append(K.halo(D, CX + 70, CY + 70, 70, "#000000", 0.45, ry=8))
    # the ground: sand, light spilling out in a fan across it
    gr = D.lin([(0, "#7A3A20"), (1, "#2A100A")], 0, 460, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 470 Q300 456 610 470 V610 H-10Z" fill="{gr}"/>')
    out.append(f'<g {D.blur(6)}><path d="M{CX - 70} 470L{CX - 200} 610H{CX + 200}L{CX + 70} 470Z" fill="{D.lin([(0, "#FFC060", 0.5), (1, "#FFC060", 0)], 0, 0, 0, 1)}"/></g>')
    out.append(K.brushwork(3108, (-10, 470, 610, 610), ["#A8603A", "#5A2A16", "#E8A070"], 140, L=(10, 40), W=(1, 2.4), op=(0.2, 0.5), angle=0, jit=6))
    # oil jars in a line, the light catching their shoulders
    jar = K.Look(["#1A0804", "#3A1A0C", "#6A3418", "#9A5A30", "#D08A50"], key=(0.2, -0.9, 0.5), amb=0.05, wrap=0.3, rim=("#FFC060", (0.5, -0.8), 0.7))
    for i, (jx, jh) in enumerate(((60, 62), (110, 70), (500, 70), (552, 64), (160, 58))):
        jy = 498 + (i % 2) * 6
        jp = [(jx - 8, jy - jh), (jx - 12, jy - jh + 8), (jx - 26, jy - jh * 0.5), (jx - 22, jy - 6), (jx - 10, jy), (jx + 10, jy), (jx + 22, jy - 6),
              (jx + 26, jy - jh * 0.5), (jx + 12, jy - jh + 8), (jx + 8, jy - jh)]
        out.append(K.paint(D, jp, jar, 3110 + i, round_r=20, flow="contour", edge_col="#0A0402", edge_w=1.4, rim_col="#FFC870", rim_w=1.6))
        out.append(f'<ellipse cx="{jx}" cy="{jy - jh}" rx="9" ry="3" fill="#0A0402"/>')
        out.append(K.halo(D, jx, jy + 2, 30, "#000000", 0.45, ry=5))
    art = D.render(out)
    DL = K.Doc("albL")
    L = [K.halo(DL, 300, 92, 240, "#120A26", 0.55, ry=50)]
    L.append(K.title(DL, 300, 104, "“Open, Sesame!”", SERIF_IT, 56, max_w=430, face=("#FFF0C8", "#F2B860", "#A8601E"), shadow="#0A0418", sop=0.8))
    L.append(K.subtitle(300, 132, "ALI BABA AND THE FORTY THIEVES", CINZEL, 15, "#F4D8D0", ls=2.5, max_w=400, sh="#0A0418", sop=0.75))
    return art, DL.render(L)
# ---- end plate: ali-baba ----


# ---- plate: hansel-and-gretel ----
@plate("hansel-and-gretel", 53, edge=1.8, bristle=0.35, grain=0.2)
def hansel_gretel_plate():
    """Deep in the black forest by moonlight: a clearing, and in it the little house made of bread, its roof of
    cake, its windows of clear sugar glowing gold; the trail of white pebbles shines all the way to its door."""
    D = K.Doc("hng")
    out = []
    out.append(K.sky(D, [(0, "#060A18"), (0.5, "#101A30"), (1, "#1E2A3E")], 5301, 0, 600, n=100, op=(0.05, 0.14)))
    out.append(K.halo(D, 300, 80, 80, "#DCE6FF", 0.4) + '<circle cx="300" cy="80" r="20" fill="#F8F8EC"/>')
    bark = K.Look(["#020304", "#080A0E", "#121620", "#202836", "#34404E"], key=(0.3, -0.9, 0.5), amb=0.05, wrap=0.3, rim=("#9AB0D0", (0.2, -1), 0.5))
    rnd = random.Random(5302)
    # rows of black trunks, the far ones misted
    for k, (n, w, fog) in enumerate(((12, (10, 18), 0.6), (8, (18, 30), 0.3), (5, (40, 70), 0.0))):
        lk = bark.toward("#3A4A62", fog)
        for i in range(n):
            x = rnd.uniform(-30, 630)
            if k == 2 and 110 < x < 490:
                continue
            wd = rnd.uniform(*w)
            spine = [(x, 640), (x + rnd.uniform(-10, 10), 400), (x + rnd.uniform(-20, 20), 160), (x + rnd.uniform(-30, 30), -30)]
            out.append(K.trunk(D, spine, [wd * 1.3, wd, wd * 0.85, wd * 0.7], lk, 5303 + k * 30 + i, crevices=6 + k * 6, knots=k, edge_col=None if k < 2 else "#000000",
                               rim="#8AA0C8" if k == 2 else None))
        out.append(K.mist(D, 380, 120, "#2A3A54", 0.5 - k * 0.15, seed=5320 + k, n=8))
    # gnarled bare branches reaching across the top
    for (x0, y0, x1, y1) in ((-20, 120, 200, 60), (620, 90, 420, 40), (-20, 240, 120, 200), (620, 220, 500, 180)):
        pts = [(x0, y0), ((x0 * 2 + x1) / 3, (y0 * 2 + y1) / 3 + rnd.uniform(-20, 20)), ((x0 + x1 * 2) / 3, (y0 + y1 * 2) / 3 + rnd.uniform(-20, 20)), (x1, y1)]
        out.append(K.taper(pts, 14, 2, "#04060A", 1))
        for k in range(1, 3):
            p = pts[k]
            out.append(K.taper([p, (p[0] + rnd.uniform(-40, 40), p[1] - rnd.uniform(20, 50))], 5, 1, "#04060A", 1))
    # the clearing floor
    gr = D.lin([(0, "#1A2430"), (1, "#06080C")], 0, 420, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 440 Q300 410 610 440 V610 H-10Z" fill="{gr}"/>')
    out.append(K.grass(5321, (-10, 430, 610, 600), ["#1A2A2A", "#2A3A3A", "#3E5050", "#0A1414"], n=240, h=(8, 22)))
    # ---- the house of bread and cake
    HX, HB = 300, 440
    out.append(K.halo(D, HX, HB - 80, 220, "#FFB050", 0.35))
    bread = K.Look(["#2A1206", "#5A2A0E", "#8E4A1E", "#BE7434", "#E2A060", "#F8D098"], key=(0.2, -0.95, 0.5), amb=0.06, wrap=0.35,
                   rim=("#C8D8F4", (0.2, -1), 0.5), jit=0.04)
    walls = [(HX - 110, HB), (HX - 110, HB - 110), (HX + 110, HB - 110), (HX + 110, HB)]
    out.append(K.paint(D, walls, bread, 5330, round_r=24, flow=0, flow_jit=8, smooth=False, edge_col="#1A0802", edge_w=1.6,
                       value_fn=lambda x, y: -0.1, passes=((60, (10, 24), (3, 6), (0.3, 0.55)), (240, (5, 12), (1.2, 2.6), (0.35, 0.7)))))
    # gingerbread planks with icing seams and sugar buttons
    for k in range(1, 6):
        y = HB - k * 20
        out.append(f'<path d="M{HX - 110} {y}H{HX + 110}" stroke="#F8F4EC" stroke-width="2.2" opacity="0.85" stroke-dasharray="1 5" stroke-linecap="round"/>')
    for _ in range(26):
        x, y = rnd.uniform(HX - 100, HX + 100), rnd.uniform(HB - 104, HB - 8)
        c = rnd.choice(["#E83A5A", "#F2E040", "#5AC8E8", "#FFFFFF", "#8AE07A"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 3.6):.1f}" fill="{c}" stroke="#1A0802" stroke-width="0.5"/>')
    # roof of cake slabs thick with white icing that drips over the eaves
    roof = [(HX - 140, HB - 104), (HX, HB - 220), (HX + 140, HB - 104)]
    cake = K.Look(["#2A1006", "#5A260E", "#8E441C", "#BC6A30", "#E09A5A"], key=(0.2, -0.95, 0.5), amb=0.06, wrap=0.35, rim=("#C8D8F4", (0.2, -1), 0.5))
    out.append(K.paint(D, roof, cake, 5331, round_r=30, flow="contour", smooth=False, edge_col="#1A0802", edge_w=1.6))
    icing = [(HX - 146, HB - 102), (HX, HB - 228), (HX + 146, HB - 102)]
    drips = []
    for k in range(29):
        t = k / 28
        x = HX - 146 + 292 * t
        y = HB - 102 - (1 - abs(t - 0.5) * 2) * 126
        drips.append((x, y))
    ic = [(HX - 146, HB - 102)] + [(x, y - 4) for x, y in drips[1:-1]] + [(HX + 146, HB - 102)]
    lower = []
    for i, (x, y) in enumerate(drips[::-1]):
        d = 10 + (14 if i % 3 == 0 else 4) + rnd.uniform(-2, 4)
        lower.append((x, y + d))
    out.append(f'<path d="{K.smooth_closed(ic + lower)}" fill="#F8F6F0" stroke="#B8C0D4" stroke-width="1"/>')
    out.append(K.taper(ic[1:-1], 2.4, 2.4, "#FFFFFF", 0.8))
    # candy on the roof
    for k in range(10):
        t = rnd.uniform(0.12, 0.88)
        x = HX - 120 + 240 * t
        ytop = HB - 104 - (1 - abs(t - 0.5) * 2) * 116
        y = rnd.uniform(ytop + 26, HB - 112)
        c = rnd.choice(["#E83A5A", "#5AC8E8", "#F2E040", "#8AE07A"])
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6" ry="4" fill="{c}" stroke="#2A0A04" stroke-width="0.6"/><path d="M{x - 3:.1f} {y - 1.5:.1f}h4" stroke="#FFFFFF" stroke-width="1" opacity="0.7"/>')
    # chimney of rock candy with a curl of smoke
    out.append(f'<path d="M{HX + 50} {HB - 170}V{HB - 210}H{HX + 74}V{HB - 146}Z" fill="#C83A5A" stroke="#2A0A04" stroke-width="1.2"/>')
    for k in range(5):
        out.append(f'<path d="M{HX + 50} {HB - 205 + k * 9}L{HX + 74} {HB - 210 + k * 9}" stroke="#FFFFFF" stroke-width="3"/>')
    out.append(K.hair([(HX + 62, HB - 212), (HX + 54, HB - 250), (HX + 70, HB - 290), (HX + 50, HB - 330)], 12, lambda t: 3 + 14 * t, 5332, ["#8A9AB8", "#C8D4E8"], w=(1.4, 3), op=(0.15, 0.35)))
    # windows of clear sugar, glowing, and the door
    for wx in (HX - 70, HX + 70):
        out.append(K.halo(D, wx, HB - 64, 40, "#FFC860", 0.6))
        out.append(f'<path d="M{wx - 18} {HB - 44}V{HB - 78}Q{wx} {HB - 96} {wx + 18} {HB - 78}V{HB - 44}Z" fill="{D.lin([(0, "#FFF6C8"), (1, "#F0A040")], 0, 0, 0, 1)}" stroke="#F8F4EC" stroke-width="4"/>')
        out.append(f'<path d="M{wx} {HB - 92}V{HB - 44}M{wx - 18} {HB - 64}H{wx + 18}" stroke="#E84A6A" stroke-width="2.4"/>')
    out.append(f'<path d="M{HX - 22} {HB}V{HB - 56}Q{HX} {HB - 78} {HX + 22} {HB - 56}V{HB}Z" fill="#5A2A0E" stroke="#F8F4EC" stroke-width="4"/>')
    out.append(f'<circle cx="{HX + 12}" cy="{HB - 28}" r="3" fill="#F2E040"/>')
    # lollipop and candy-cane fence posts
    for (fx, c) in ((HX - 150, "#E83A5A"), (HX - 128, "#5AC8E8"), (HX + 128, "#F2E040"), (HX + 150, "#E83A5A")):
        out.append(f'<path d="M{fx} {HB + 10}V{HB - 40}" stroke="#F8F4EC" stroke-width="3"/>')
        out.append(f'<circle cx="{fx}" cy="{HB - 46}" r="10" fill="{c}" stroke="#2A0A04" stroke-width="1"/>')
        out.append(f'<path d="M{fx - 6} {HB - 46}a6 6 0 1 1 6 6" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.8"/>')
    # the trail of white pebbles shining in the moonlight, from the foreground to the door
    for i in range(36):
        t = i / 35
        x = HX - 6 + (1 - t) ** 1.6 * (-150) + math.sin(t * 9) * 20 * (1 - t)
        y = HB + 4 + (1 - t) ** 1.2 * 150
        r = 1.5 + 4.5 * (1 - t)
        out.append(K.halo(D, x, y, r * 3, "#E8F0FF", 0.45))
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.6:.1f}" fill="#F4F8FF"/>')
    art = D.render(out)
    DL = K.Doc("hngL")
    L = [K.halo(DL, 300, 112, 240, "#04060E", 0.6, ry=40)]
    L.append(K.title(DL, 300, 124, "Hansel & Gretel", SERIF_IT, 52, max_w=430, face=("#FFF0C8", "#F0B858", "#A8601E"), shadow="#000000", sop=0.8))
    L.append(K.halo(DL, 300, 528, 260, "#020406", 0.65, ry=34))
    L.append(K.subtitle(300, 522, "“Nibble, nibble, little mouse,", SERIF_IT, 21, "#F4ECD8", max_w=420, sh="#000000", sop=0.85))
    L.append(K.subtitle(300, 546, "who is nibbling at my house?”", SERIF_IT, 21, "#F4ECD8", max_w=420, sh="#000000", sop=0.85))
    return art, DL.render(L)
# ---- end plate: hansel-and-gretel ----


# ---- plate: the-snow-queen ----
def snowflake_painted(x, y, r, ang, col, w=1.6, op=0.9):
    """A six-armed dendrite crystal with side branches."""
    out = []
    for k in range(6):
        a = math.radians(ang + k * 60)
        ux, uy = math.cos(a), math.sin(a)
        out.append(f'<path d="M{x:.1f} {y:.1f}L{x + ux * r:.1f} {y + uy * r:.1f}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round" opacity="{op}"/>')
        for t, L in ((0.4, 0.32), (0.68, 0.24)):
            bx, by = x + ux * r * t, y + uy * r * t
            for sd in (-1, 1):
                b = a + sd * math.radians(60)
                out.append(f'<path d="M{bx:.1f} {by:.1f}l{math.cos(b) * r * L:.1f} {math.sin(b) * r * L:.1f}" stroke="{col}" stroke-width="{w * 0.8:.1f}" stroke-linecap="round" opacity="{op}"/>')
    return "".join(out)


@plate("the-snow-queen", 67, edge=1.6, bristle=0.32, grain=0.18)
def snow_queen_plate():
    """The Snow Queen's palace far in the north: walls of drifted snow and windows of cutting wind, spires of
    blue ice under the northern lights, the frozen 'mirror of reason' lake before it, crystals falling."""
    D = K.Doc("snq")
    out = []
    out.append(K.sky(D, [(0, "#030616"), (0.4, "#0A1A3A"), (0.8, "#163A5A"), (1, "#2A5A76")], 6701, 0, 430, n=120, op=(0.05, 0.14)))
    out.append(K.stars(6702, (10, 10, 590, 300), 120, r=(0.4, 1.4), op=(0.4, 1.0)))
    # aurora: hanging curtains of green and violet light, made of fine vertical strokes
    rnd = random.Random(6703)
    for band, (yb, amp, cols) in enumerate(((150, 50, ["#7AF0C0", "#4AD8A0", "#A8FFE0"]), (110, 40, ["#B890F0", "#7AF0C0", "#E0C8FF"]))):
        for i in range(140):
            x = rnd.uniform(-20, 620)
            y = yb + amp * math.sin(x * 0.012 + band * 2) + rnd.uniform(-6, 6)
            h = rnd.uniform(40, 130)
            g = D.lin([(0, rnd.choice(cols), 0), (0.7, cols[0], round(rnd.uniform(0.1, 0.28), 2)), (1, cols[0], 0)], x, y - h, x, y, "userSpaceOnUse")
            out.append(f'<path d="M{x:.1f} {y:.1f}v{-h:.1f}" stroke="{g}" stroke-width="{rnd.uniform(2, 5):.1f}"/>')
        out.append(K.halo(D, 300, yb, 340, cols[0], 0.12, ry=60))
    # far snowfields and ice hills
    for k, (yb, col) in enumerate(((380, "#3A5A7A"), (410, "#5A7A98"))):
        ridge = K.rough([(-20, yb), (120, yb - 30 + k * 10), (260, yb - 10), (400, yb - 40 + k * 14), (620, yb - 6)], 6704 + k, 4, 10)
        out.append(f'<path d="{K.smooth_open(ridge)} L620 610 L-20 610Z" fill="{col}"/>')
    # the ice palace: crystalline spires, faceted, light glowing from inside
    ice = K.Look(["#0A1A34", "#1E3E66", "#3A6A98", "#6A9ACA", "#A8D0F0", "#E8F8FF"], key=(-0.3, -0.9, 0.5), amb=0.1, wrap=0.35, jit=0.04,
                 rim=("#C8FFE8", (0.0, -1.0), 0.6))
    out.append(K.halo(D, 300, 330, 200, "#9AE0FF", 0.3))
    spires = [(300, 150, 34), (250, 210, 26), (350, 200, 28), (210, 260, 22), (392, 250, 22), (172, 300, 18), (430, 292, 18), (280, 236, 18), (322, 228, 18)]
    for (x, top, w) in sorted(spires, key=lambda t: t[1]):
        base = 420
        sp = [(x - w / 2, base), (x - w / 2, top + w * 1.6), (x, top), (x + w / 2, top + w * 1.6), (x + w / 2, base)]
        out.append(K.paint(D, sp, ice, 6705 + x, round_r=w * 0.4, flow=90, flow_jit=4, smooth=False, edge_col="#06122A", edge_w=1.2,
                           rim_col="#E8FFFF", rim_w=1.4, rim_op=0.7, passes=((80, (10, 24), (1.5, 3), (0.35, 0.6)),)))
        out.append(f'<path d="M{x:.1f} {top:.1f}L{x:.1f} {base}" stroke="#E8F8FF" stroke-width="1" opacity="0.45"/>')
        out.append(f'<path d="M{x - w / 2:.1f} {top + w * 1.6:.1f}L{x:.1f} {top + w * 2.4:.1f}L{x + w / 2:.1f} {top + w * 1.6:.1f}" stroke="#E8F8FF" stroke-width="1" fill="none" opacity="0.5"/>')
        for _ in range(2):
            wy = rnd.uniform(top + w * 2.6, base - 20)
            out.append(K.halo(D, x, wy, w * 0.6, "#C8F4FF", 0.6) + f'<path d="M{x - 3:.1f} {wy + 6:.1f}V{wy - 2:.1f}L{x:.1f} {wy - 7:.1f}L{x + 3:.1f} {wy - 2:.1f}V{wy + 6:.1f}Z" fill="#F0FCFF"/>')
    # the frozen lake in front, the palace and aurora reflected, cracked ice
    lake = D.lin([(0, "#6A9AC0"), (0.5, "#2A4A6E"), (1, "#0E1E36")], 0, 420, 0, 520, "userSpaceOnUse")
    out.append(f'<path d="M-10 424 Q300 414 610 424 L610 520 Q300 530 -10 520Z" fill="{lake}"/>')
    for _ in range(18):
        x = rnd.uniform(0, 600)
        pts = [(x, 430)]
        for k in range(4):
            pts.append((pts[-1][0] + rnd.uniform(-30, 30), pts[-1][1] + rnd.uniform(6, 22)))
        out.append(f'<path d="M{" L".join(f"{p[0]:.0f} {p[1]:.0f}" for p in pts if p[1] < 520)}" stroke="#C8E8FF" stroke-width="0.8" fill="none" opacity="0.5"/>')
    out.append(K.halo(D, 300, 450, 150, "#9AE0FF", 0.25, ry=20))
    # snowbank foreground
    snow = K.Look(["#2A3E5E", "#4A6488", "#7A98BE", "#B8D0EA", "#EAF4FF"], key=(-0.3, -0.9, 0.5), amb=0.15, wrap=0.45)
    bank = K.rough([(-20, 610), (-20, 512), (100, 500), (220, 520), (360, 506), (500, 520), (620, 504), (620, 610)], 6706, 4, 10)
    out.append(K.paint(D, bank, snow, 6707, round_r=40, flow=0, flow_jit=10, smooth=False, edge_col="#1A2A44", edge_w=1, edge_op=0.4))
    # crystals falling: a few large painted snowflakes, many small
    for (x, y, r, a) in ((92, 230, 22, 10), (520, 300, 18, 25), (120, 420, 12, 0), (470, 180, 12, 15), (540, 470, 14, 5)):
        out.append(K.halo(D, x, y, r * 1.4, "#E8F8FF", 0.3) + snowflake_painted(x, y, r, a, "#F4FCFF", 1.8))
    for _ in range(120):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    art = D.render(out)
    DL = K.Doc("snqL")
    L = [K.halo(DL, 300, 86, 240, "#02040E", 0.5, ry=36)]
    L.append(K.title(DL, 300, 98, "The Snow Queen", SERIF_IT, 54, max_w=430, face=("#FFFFFF", "#D8F0FF", "#7AA8D0"), shadow="#000000", sop=0.8))
    L.append(K.halo(DL, 300, 538, 240, "#0A1428", 0.5, ry=22))
    L.append(K.subtitle(300, 544, "HANS CHRISTIAN ANDERSEN · 1844", CINZEL, 15, "#E8F4FF", ls=2.5, max_w=400, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: the-snow-queen ----


# ---- plate: the-princess-and-the-pea ----
@plate("the-princess-and-the-pea", 43, edge=1.6, bristle=0.32, grain=0.18)
def princess_pea_plate():
    """The queen's test by candlelight: twenty mattresses and twenty eiderdowns piled to the ceiling of the royal
    bedchamber, a little ladder against them, and right at the bottom, on the bare bedstead, one green pea."""
    D = K.Doc("ppe")
    out = []
    # the chamber: damask wall, a tall arched window with the stormy night outside
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#2A0E1A"/>')
    pat = []
    rnd = random.Random(4301)
    for y in range(0, 600, 40):
        for x in range((y // 40 % 2) * 20, 620, 40):
            pat.append(f'M{x} {y - 8}q6 8 0 16q-6 -8 0 -16Z')
    out.append(f'<path d="{" ".join(pat)}" fill="#5A1A30" opacity="0.6"/>')
    out.append(K.halo(D, 520, 380, 260, "#FFB060", 0.35))
    out.append(f'<path d="M40 330V120Q80 70 120 120V330Z" fill="#0E1428"/>')
    out.append(f'<path d="M48 324V124Q80 84 112 124V324Z" fill="{D.lin([(0, "#1A2A4A"), (1, "#0A1020")], 0, 0, 0, 1)}"/>')
    out.append(f'<path d="M66 150l-6 30l10 -2l-8 34" stroke="#C8D8FF" stroke-width="1.4" fill="none" opacity="0.7"/>')
    for _ in range(30):
        x, y = rnd.uniform(50, 110), rnd.uniform(130, 320)
        out.append(f'<path d="M{x:.0f} {y:.0f}l-3 9" stroke="#8AA0C8" stroke-width="0.8" opacity="0.5"/>')
    out.append(f'<path d="M80 100V330M44 210H116" stroke="#2A0E1A" stroke-width="4"/>')
    # floor
    out.append(f'<rect x="-10" y="520" width="620" height="90" fill="{D.lin([(0, "#3A1A10"), (1, "#140806")], 0, 0, 0, 1)}"/>')
    for k in range(-4, 10):
        out.append(f'<path d="M{300 + k * 30} 520L{300 + k * 90} 610" stroke="#1A0A06" stroke-width="1.4" opacity="0.6"/>')
    # the bedstead and posts
    wood = K.Look(["#120604", "#2A1008", "#4A2010", "#7A3A1C", "#A86030", "#D89A5A"], key=(0.8, -0.3, 0.5), amb=0.06, wrap=0.3, rim=("#FFC880", (1, -0.2), 0.7))
    BX0, BX1, BB = 190, 470, 520
    for px in (BX0 - 6, BX1 + 6):
        out.append(K.paint(D, [(px - 9, BB + 6), (px - 7, 60), (px + 7, 60), (px + 9, BB + 6)], wood, 4302 + px, round_r=8, flow=90, smooth=False, edge_col="#080202"))
        out.append(f'<circle cx="{px}" cy="56" r="11" fill="{D.rad([(0, "#F8D070"), (1, "#7A4A10")], 0.35, 0.35, 0.7)}" stroke="#2A1404" stroke-width="1"/>')
    # canopy drape at the top
    out.append(f'<path d="M150 40H510V70Q470 96 430 70Q390 96 350 70Q310 96 270 70Q230 96 190 70Q170 84 150 70Z" fill="#7A1A32" stroke="#2A0610" stroke-width="1.4"/>')
    out.append(f'<path d="M150 40H510" stroke="#E8B850" stroke-width="5"/>')
    frame = [(BX0 - 10, BB - 30), (BX1 + 10, BB - 30), (BX1 + 10, BB), (BX0 - 10, BB)]
    out.append(K.paint(D, frame, wood, 4303, round_r=10, flow=0, smooth=False, edge_col="#080202", edge_w=1.4, rim_col="#FFC880", rim_w=1.2))
    # the pea on the bare boards, under everything, glowing a little
    out.append(K.halo(D, 330, BB - 36, 26, "#C8FF80", 0.55))
    out.append(f'<circle cx="330" cy="{BB - 36}" r="6.5" fill="{D.rad([(0, "#E8FFB0"), (0.6, "#6AC040"), (1, "#2A6A18")], 0.35, 0.35, 0.7)}"/>')
    out.append(f'<circle cx="328" cy="{BB - 38}" r="1.8" fill="#FFFFFF" opacity="0.8"/>')
    # the stack: mattresses (striped ticking) alternating with eiderdowns (puffy, floral), each slightly askew
    fabrics = [("#F2E6D0", "#8A3A4A"), ("#E8C8D8", "#6A2A5A"), ("#F4EED8", "#3A5A8A"), ("#D8E8D0", "#4A6A3A"), ("#F8E0C0", "#A8602A"),
               ("#E0D8F0", "#5A4A8A"), ("#F2D8D0", "#9A3A3A"), ("#F4F0E0", "#C8A040")]
    y = BB - 44
    i = 0
    while y > 150:
        h = 15 if i % 2 == 0 else 19
        sk = rnd.uniform(-6, 6)
        x0, x1 = BX0 - 4 + sk, BX1 + 4 + sk
        base_c, pat_c = fabrics[i % len(fabrics)]
        lk = K.Look([K.dk(base_c, 0.55), K.dk(base_c, 0.3), K.dk(base_c, 0.1), base_c, K.lt(base_c, 0.5)], key=(0.8, -0.4, 0.5), amb=0.08, wrap=0.4,
                    rim=("#FFD8A0", (1, -0.1), 0.5))
        bul = rnd.uniform(1.5, 4) if i % 2 else 1
        pts = [(x0 + 8, y + 0.5), (x0 + 2, y - h * 0.18), (x0, y - h * 0.5), (x0 + 2, y - h * 0.82), (x0 + 8, y - h - 0.5), ((x0 + x1) / 2, y - h - bul),
               (x1 - 8, y - h - 0.5), (x1 - 2, y - h * 0.82), (x1, y - h * 0.5), (x1 - 2, y - h * 0.18), (x1 - 8, y + 0.5), ((x0 + x1) / 2, y + bul * 0.5)]
        out.append(K.paint(D, pts, lk, 4310 + i, round_r=h * 0.5, flow=0, flow_jit=4, edge_col=K.dk(base_c, 0.7), edge_w=1.2, edge_op=0.6,
                           passes=((120, (10, 26), (1.5, 3), (0.3, 0.55)),)))
        cid = D.clip(K.smooth_closed(pts))
        if i % 2 == 0:
            st = "".join(f'<path d="M{x0} {y - h * t:.1f}H{x1}" stroke="{pat_c}" stroke-width="1.6" opacity="0.6"/>' for t in (0.3, 0.5, 0.7))
        else:
            st = "".join(f'<circle cx="{x0 + 12 + k * 22:.0f}" cy="{y - h / 2:.1f}" r="3" fill="{pat_c}" opacity="0.7"/>' for k in range(int((x1 - x0) / 22)))
            st += "".join(f'<path d="M{x0 + 23 + k * 22:.0f} {y - h + 2:.1f}V{y - 2:.1f}" stroke="{K.dk(base_c, 0.3)}" stroke-width="1" opacity="0.6"/>' for k in range(int((x1 - x0) / 22)))
        out.append(f'<g {cid}>{st}</g>')
        y -= h - 1
        i += 1
    # a little ladder leaning on the pile, and a candle on a stand glowing at the right
    lad = "#B8803E"
    out.append(f'<path d="M500 {BB}L452 160M528 {BB}L480 158" stroke="{lad}" stroke-width="4"/>')
    for k in range(14):
        t = k / 13
        out.append(f'<path d="M{500 - 48 * t:.1f} {BB - (BB - 160) * t:.1f}L{528 - 48 * t:.1f} {BB - (BB - 158) * t:.1f}" stroke="{lad}" stroke-width="3"/>')
    out.append(K.halo(D, 560, 300, 90, "#FFC060", 0.55))
    out.append(f'<rect x="554" y="310" width="12" height="54" fill="#F2E8D0"/><path d="M548 364H572L566 520H554Z" fill="#7A4A1A"/>')
    out.append(f'<path d="{K.smooth_closed([(555, 310), (558, 296), (560, 288), (563, 296), (565, 310)])}" fill="#FFD070"/>')
    art = D.render(out)
    DL = K.Doc("ppeL")
    L = [K.halo(DL, 300, 140, 0, "#000000", 0)]
    L.append(K.halo(DL, 300, 528, 260, "#120604", 0.6, ry=34))
    L.append(K.title(DL, 300, 534, "The Princess & the Pea", SERIF_IT, 42, max_w=440, face=("#FFF0C8", "#F0C060", "#A86A1E"), shadow="#000000", sop=0.85))
    L.append(K.halo(DL, 300, 22, 0, "#000000", 0))
    return art, DL.render(L)
# ---- end plate: the-princess-and-the-pea ----


# ---- plate: persephone ----
def aril(D, x, y, r, rnd, light=(-0.6, -0.7)):
    """One pomegranate seed: a faceted ruby droplet with a pale core and a wet highlight."""
    lx, ly = light
    g = D.rad([(0, "#FF8A9A"), (0.5, "#D01838"), (1, "#5A0414")], round(0.5 + lx * 0.25, 2), round(0.5 + ly * 0.25, 2), 0.65)
    a = rnd.uniform(0, 180)
    o = f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.8:.1f}" fill="{g}" transform="rotate({a:.0f} {x:.1f} {y:.1f})" stroke="#3A0208" stroke-width="0.5"/>'
    o += f'<ellipse cx="{x + 0.2 * r:.1f}" cy="{y + 0.15 * r:.1f}" rx="{r * 0.28:.1f}" ry="{r * 0.2:.1f}" fill="#FFE0D8" opacity="0.5"/>'
    o += f'<circle cx="{x + lx * r * 0.45:.1f}" cy="{y + ly * r * 0.45:.1f}" r="{r * 0.2:.1f}" fill="#FFFFFF" opacity="0.9"/>'
    return o


@plate("persephone", 59, edge=1.6, bristle=0.32, grain=0.18)
def persephone_plate():
    """A still life on a marble ledge: the pomegranate of the underworld broken open, its ruby seeds spilling;
    behind it the year divides, almond blossom in warm spring light on one side, bare frosted branches and falling
    snow on the other. Six seeds lie apart, the six months of winter."""
    D = K.Doc("prs")
    out = []
    # the divided year: warm spring at left grading into cold winter at right
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="{D.lin([(0, "#E8D8A0"), (0.3, "#D0C890"), (0.5, "#8A8E9A"), (0.7, "#4A5878"), (1, "#1E2A48")], 0, 0, 1, 0)}"/>')
    out.append(K.halo(D, 90, 160, 260, "#FFF6D0", 0.6))
    rnd = random.Random(5901)
    # spring: an almond branch in blossom reaching in from the left
    br = [(-20, 120), (60, 150), (140, 170), (200, 210)]
    out.append(K.taper(br, 12, 3, "#3A2418", 1))
    out.append(K.taper([(80, 154), (120, 110), (160, 90)], 5, 1.5, "#3A2418", 1))
    out.append(K.taper([(130, 168), (150, 220), (170, 250)], 4, 1.4, "#3A2418", 1))
    for _ in range(26):
        t = rnd.random()
        seg = rnd.choice([br, [(80, 154), (120, 110), (160, 90)], [(130, 168), (150, 220), (170, 250)]])
        k = min(len(seg) - 2, int(t * (len(seg) - 1)))
        p = K._lerp2(seg[k], seg[k + 1], t * (len(seg) - 1) - k)
        x, y = p[0] + rnd.uniform(-10, 10), p[1] + rnd.uniform(-10, 10)
        for j in range(5):
            a = j * 1.2566 + rnd.uniform(0, 0.3)
            out.append(f'<ellipse cx="{x + math.cos(a) * 5:.1f}" cy="{y + math.sin(a) * 5:.1f}" rx="5" ry="3.6" fill="{rnd.choice(["#FFFFFF", "#FCE8EE", "#F8D0DC"])}" stroke="#E0A8B8" stroke-width="0.5" transform="rotate({math.degrees(a):.0f} {x + math.cos(a) * 5:.1f} {y + math.sin(a) * 5:.1f})"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#C83A5A"/>')
    for _ in range(14):
        x, y = rnd.uniform(20, 260), rnd.uniform(220, 380)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.4" ry="2" fill="#FCE8EE" opacity="0.85" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    # winter: bare black branches with frost, snow falling
    for b in ([(620, 100), (520, 140), (440, 160), (400, 190)], [(620, 220), (540, 230), (480, 270)], [(520, 140), (500, 90), (470, 60)]):
        out.append(K.taper(b, 9, 2, "#0E121C", 1))
        out.append(K.taper([(x, y - 2) for x, y in b], 3, 0.6, "#E8F0FF", 0.7))
        for k in range(len(b) - 1):
            p = K._lerp2(b[k], b[k + 1], 0.5)
            out.append(K.taper([p, (p[0] - rnd.uniform(10, 30), p[1] - rnd.uniform(10, 30))], 3, 0.6, "#0E121C", 1))
    for _ in range(90):
        x, y = rnd.uniform(330, 610), rnd.uniform(0, 420)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    # the marble ledge
    marble = K.Look(["#2A2A30", "#5A5A64", "#8A8A94", "#B8B8C0", "#E2E0E4", "#FAF8F6"], key=(-0.6, -0.8, 0.5), amb=0.15, wrap=0.4)
    ledge = [(-20, 400), (620, 400), (620, 610), (-20, 610)]
    out.append(K.paint(D, ledge, marble, 5902, round_r=80, flow=0, flow_jit=4, smooth=False, edge_col=None,
                       value_fn=lambda x, y: 0.1 * (1 - x / 600) - 0.15 * (x / 600), passes=((40, (30, 80), (2, 5), (0.25, 0.45)),)))
    for _ in range(8):
        x = rnd.uniform(0, 600)
        out.append(K.taper([(x, 400), (x + rnd.uniform(-60, 60), 480), (x + rnd.uniform(-80, 80), 610)], 1.2, 0.4, "#8A8A96", 0.4))
    out.append(f'<rect x="-20" y="396" width="640" height="6" fill="#F4F2F0" opacity="0.8"/>')
    # the whole pomegranate behind
    skin = K.Look(["#2A0206", "#5A0810", "#8E1420", "#C02A30", "#E2604A", "#F8A880"], key=(-0.6, -0.7, 0.5), amb=0.05, wrap=0.3,
                  rim=("#FFE0B0", (-0.7, -0.6), 0.6), spec=("#FFFFFF", 0.88, 0.7), jit=0.03)
    WX, WY, WR = 380, 330, 82
    whole = [(WX + math.cos(a) * WR * (1 + 0.04 * math.cos(5 * a)), WY + math.sin(a) * WR * 0.94) for a in [k * math.pi / 20 for k in range(40)]]
    out.append(K.halo(D, WX + 20, 410, 110, "#000000", 0.4, ry=10))
    out.append(K.paint(D, whole, skin, 5903, round_r=WR * 0.85, flow="contour", flow_jit=10, edge_col="#1A0204", edge_w=1.8, rim_col="#FFE0B0", rim_w=1.6,
                       passes=((60, (10, 24), (3, 6), (0.3, 0.55)), (240, (5, 12), (1.2, 2.4), (0.35, 0.7)))))
    crown = [(WX - 18, WY - WR * 0.9), (WX - 22, WY - WR - 18), (WX - 10, WY - WR - 6), (WX - 4, WY - WR - 22), (WX + 4, WY - WR - 6), (WX + 14, WY - WR - 20),
             (WX + 18, WY - WR * 0.9)]
    out.append(f'<ellipse cx="{WX}" cy="{WY - WR * 0.9:.1f}" rx="20" ry="6" fill="#3A0408"/>')
    for k, (dx, h, lean) in enumerate(((-17, 18, -0.5), (-9, 24, -0.2), (0, 20, 0.0), (9, 25, 0.2), (17, 17, 0.5))):
        b = WY - WR * 0.9
        sep = [(WX + dx - 5, b + 2), (WX + dx + lean * h * 0.6, b - h), (WX + dx + 5, b + 2)]
        out.append(K.paint(D, sep, skin.darker(0.1 if k % 2 else 0), 5910 + k, round_r=4, flow=90, edge_col="#2A0204", edge_w=1.1, smooth=False))
    # the broken half in front, cut face toward us: pale pith membranes, chambers packed with seeds
    HX, HY, HR = 250, 420, 92
    out.append(K.halo(D, HX + 10, 470, 130, "#000000", 0.45, ry=12))
    rind = [(HX + math.cos(a) * HR, HY + math.sin(a) * HR * 0.55) for a in [k * math.pi / 20 for k in range(21)]]
    rind = [(HX - HR, HY)] + [(HX - math.cos(a) * HR * 1.02, HY + math.sin(a) * HR * 0.62) for a in [k * math.pi / 20 for k in range(1, 20)]] + [(HX + HR, HY)]
    out.append(K.paint(D, rind + [(HX + HR * 0.8, HY - 6), (HX - HR * 0.8, HY - 6)], skin, 5904, round_r=30, flow="contour", edge_col="#1A0204", edge_w=1.8, smooth=False))
    face = [(HX + math.cos(a) * HR * 0.98, HY - 10 + math.sin(a) * HR * 0.8) for a in [k * math.pi / 24 for k in range(48)]]
    out.append(f'<path d="{K.poly_d(face)}" fill="#F2DCB8" stroke="#A82A2A" stroke-width="3"/>')
    cid = D.clip(K.poly_d(face))
    seeds = []
    for _ in range(420):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.05, 1.0) ** 0.6
        x, y = HX + math.cos(a) * HR * 0.9 * rr, HY - 10 + math.sin(a) * HR * 0.74 * rr
        if abs(math.sin(a * 3 - 0.6)) < 0.07:          # leave the pith walls between chambers
            continue
        seeds.append(aril(D, x, y, rnd.uniform(6.2, 8.2), rnd))
    out.append(f'<g {cid}>{"".join(seeds)}</g>')
    for k in range(6):
        a = k * math.pi / 3 + 0.2
        out.append(f'<path d="M{HX:.1f} {HY - 10:.1f}L{HX + math.cos(a) * HR * 0.92:.1f} {HY - 10 + math.sin(a) * HR * 0.76:.1f}" stroke="#F8E0B8" stroke-width="1.6" opacity="0.55"/>')
    # six seeds lying apart on the marble
    for (x, y) in ((402, 476), (424, 490), (446, 474), (470, 492), (494, 478), (516, 494)):
        out.append(K.halo(D, x + 2, y + 5, 9, "#000000", 0.35, ry=3) + aril(D, x, y, 7, rnd))
    art = D.render(out)
    DL = K.Doc("prsL")
    L = [K.halo(DL, 300, 84, 230, "#FFF8E8", 0.0, ry=40)]
    L.append(K.title(DL, 300, 96, "Persephone", SERIF_IT, 58, max_w=420, face=("#C8203A", "#8A0E22", "#4A0410"), shadow="#FFF4E0", sop=0.7, glow="#FFF8EC", glow_op=0.55))
    L.append(K.subtitle(300, 124, "A GREEK MYTH · THE HYMN TO DEMETER", CINZEL, 14, "#3A1A1A", ls=2, max_w=380, sh="#FFF8EC", sop=0.6))
    L.append(K.halo(DL, 300, 538, 250, "#1A1A22", 0.55, ry=22))
    L.append(K.subtitle(300, 544, "Six seeds, six months of winter.", SERIF_IT, 23, "#FFF4EC", max_w=420, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: persephone ----


# ---- plate: thumbelina ----
def swallow_painted(D, x, y, s, seed, flip=False):
    """A barn swallow perched: glossy blue-black back and folded pointed wings that reach past the tail, long tail
    streamers, rust-red forehead and throat, cream breast, tiny bill, dark eye with a gleam."""
    T = lambda pts: K.xform(pts, x, y, s, 0, flip)
    blue = K.Look(["#04060E", "#0A1430", "#14285A", "#2A4A8A", "#5A7AC0", "#A8C0F0"], key=(-0.5, -0.8, 0.5), amb=0.05, wrap=0.3, spec=("#C8E0FF", 0.8, 0.7))
    cream = K.Look(["#8A7A6A", "#C8B8A0", "#EEE2CC", "#FFF8EC"], key=(-0.5, -0.8, 0.5), amb=0.2)
    out = []
    tail = T([(-14, -2), (-30, 6), (-52, 18), (-50, 16), (-30, 3), (-46, 22), (-44, 19), (-26, 2), (-12, 2)])
    out.append(f'<path d="{K.poly_d(tail)}" fill="#0A1430" stroke="#04060E" stroke-width="0.6"/>')
    body = T([(-14, 0), (-8, -7), (2, -11), (10, -12), (16, -10), (19, -6), (18, -1), (12, 4), (2, 6), (-8, 5)])
    out.append(K.paint(D, body, cream, seed, round_r=6 * s, flow="contour", edge_col="#2A2018", edge_w=1))
    back = T([(-14, -1), (-8, -8), (2, -12), (10, -13), (15, -11), (12, -8), (4, -6), (-4, -3), (-10, 0)])
    out.append(K.paint(D, back, blue, seed + 1, round_r=4 * s, flow="contour", edge_col="#04060E", edge_w=1))
    wing = T([(6, -9), (-6, -6), (-22, -2), (-40, 4), (-36, 4), (-20, 2), (-4, -1), (6, -4)])
    out.append(K.paint(D, wing, blue.darker(-0.05), seed + 2, round_r=3 * s, flow=200, edge_col="#04060E", edge_w=1))
    head = T([(10, -12), (15, -15), (20, -14), (23, -11), (22, -7), (17, -5), (12, -7)])
    out.append(K.paint(D, head, blue, seed + 3, round_r=4 * s, flow="contour", edge_col="#04060E", edge_w=1))
    throat = T([(19, -7), (22, -8), (21, -3), (16, -2), (16, -6)])
    out.append(f'<path d="{K.smooth_closed(throat)}" fill="#B8441E"/>')
    out.append(f'<path d="{K.smooth_closed(T([(21, -12.5), (23, -12), (23, -10.5), (21, -10.5)]))}" fill="#B8441E"/>')
    bill = T([(23, -11), (27, -10), (23, -9)])
    out.append(f'<path d="{K.poly_d(bill)}" fill="#0A0806"/>')
    e = T([(18.6, -11.4)])[0]
    out.append(f'<circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="{1.4 * s:.1f}" fill="#040404"/><circle cx="{e[0] - 0.4 * s:.1f}" cy="{e[1] - 0.4 * s:.1f}" r="{0.45 * s:.1f}" fill="#FFFFFF"/>')
    for k in range(2):
        f = T([(4 + k * 3, 5), (5 + k * 3, 9)])
        out.append(K.taper(f, 1.2, 1.0, "#2A1A10", 1))
    return "".join(out)


@plate("thumbelina", 79, edge=1.6, bristle=0.32, grain=0.18)
def thumbelina_plate():
    """Morning on a cottage windowsill: a polished walnut shell for a cradle, a violet leaf for a mattress, a
    rose petal for a blanket and, peeping out, one golden curl; the tulip she was born from opens beside it and
    the swallow who will carry her away waits on the frame."""
    D = K.Doc("thb")
    out = []
    # the window: soft spring garden beyond, the sill in front, light from the left
    out.append(K.sky(D, [(0, "#CCE0F0"), (0.6, "#E8F0E0"), (1, "#F4F0D8")], 7901, 0, 380, n=60, op=(0.05, 0.12)))
    fl = K.Look(["#4A6A3A", "#6E8E4E", "#9AB872", "#C8DCA0", "#F0F4D8"], key=(-0.7, -0.6, 0.5), amb=0.2, wrap=0.45)
    out.append(K.foliage(D, [(80, 300, 120, 80), (300, 320, 160, 70), (520, 290, 120, 90)], fl.toward("#E8F0E0", 0.4), 7902, size=(3, 7), density=0.7))
    rnd = random.Random(7903)
    for _ in range(30):
        x, y = rnd.uniform(0, 600), rnd.uniform(240, 360)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 4):.1f}" fill="{rnd.choice(["#F8C8D8", "#FFFFFF", "#F8E890", "#C8A8F0"])}" opacity="0.8"/>')
    frame = K.Look(["#6A5A48", "#9A8A74", "#C8BAA2", "#ECE2CE", "#FFFAF0"], key=(-0.7, -0.6, 0.5), amb=0.2, wrap=0.4)
    for pts in ([(-20, 0), (40, 0), (40, 380), (-20, 380)], [(560, 0), (620, 0), (620, 380), (560, 380)], [(-20, -20), (620, -20), (620, 30), (-20, 30)],
                [(290, 30), (310, 30), (310, 380), (290, 380)]):
        out.append(K.paint(D, pts, frame, 7904 + int(pts[0][0]), round_r=10, flow=90 if pts[1][0] - pts[0][0] < 80 else 0, smooth=False, edge_col="#4A3E30", edge_w=1,
                           passes=((30, (30, 60), (3, 6), (0.2, 0.4)),)))
    sill = [(-20, 380), (620, 380), (620, 610), (-20, 610)]
    out.append(K.paint(D, sill, frame, 7905, round_r=60, flow=0, smooth=False, edge_col=None, value_fn=lambda x, y: -0.15 * (y - 380) / 230,
                       passes=((30, (40, 90), (3, 6), (0.2, 0.4)),)))
    out.append(f'<rect x="-20" y="376" width="640" height="8" fill="#FFFCF4"/>')
    out.append(K.shafts(D, (-40, 40), [(160, 420, 600)], "#FFF6D8", 0.22))
    # the tulip in a clay pot on the right
    pot = K.Look(["#4A1E0E", "#7A3418", "#AE5A2E", "#D8885A", "#F2B892"], key=(-0.7, -0.6, 0.5), amb=0.1, wrap=0.4)
    out.append(K.halo(D, 470, 512, 70, "#3A2A1A", 0.45, ry=8))
    out.append(K.paint(D, [(420, 420), (520, 420), (508, 510), (432, 510)], pot, 7906, round_r=30, flow=90, smooth=False, edge_col="#2A0E04", edge_w=1.4))
    out.append(K.paint(D, [(412, 408), (528, 408), (528, 426), (412, 426)], pot.darker(-0.05), 7907, round_r=6, flow=0, smooth=False, edge_col="#2A0E04", edge_w=1.4))
    stem = [(470, 410), (468, 330), (472, 250), (476, 196)]
    out.append(K.taper(stem, 6, 4, "#4A7A2E", 1))
    lf = K.Look(["#1E3A14", "#2E5420", "#4A7A30", "#7AA250", "#B8D088"], key=(-0.7, -0.6, 0.5), amb=0.1, wrap=0.4)
    for pts in ([(468, 410), (440, 340), (430, 270), (444, 300), (462, 360)], [(472, 406), (500, 330), (512, 280), (500, 330), (478, 380)]):
        out.append(K.paint(D, pts, lf, 7908 + pts[2][0], round_r=8, flow="contour", edge_col="#14280C", edge_w=1))
    tl = K.Look(["#5A0A1A", "#9A1A2E", "#D23A48", "#F2786A", "#FFC0A8"], key=(-0.7, -0.6, 0.5), amb=0.08, wrap=0.4, rim=("#FFE8C8", (-0.8, -0.5), 0.5))
    for k, pts in enumerate(([(476, 200), (452, 186), (446, 150), (456, 124), (472, 150)], [(476, 200), (500, 186), (506, 150), (496, 124), (480, 150)],
                             [(476, 202), (462, 170), (470, 120), (484, 170)])):
        out.append(K.paint(D, pts, tl.darker(0.1 if k < 2 else -0.05), 7910 + k, round_r=10, flow=90, edge_col="#4A0410", edge_w=1.2))
    # the walnut-shell cradle on the sill
    WX, WY = 230, 470
    nut = K.Look(["#2A1408", "#4E2A12", "#7A4A24", "#A87444", "#D4A472"], key=(-0.7, -0.6, 0.5), amb=0.08, wrap=0.35, spec=("#FFF0D8", 0.85, 0.5))
    out.append(K.halo(D, WX + 10, WY + 46, 110, "#3A2A1A", 0.45, ry=10))
    shell = [(WX - 96, WY), (WX - 92, WY + 22), (WX - 70, WY + 40), (WX - 30, WY + 50), (WX + 20, WY + 50), (WX + 64, WY + 42), (WX + 90, WY + 24), (WX + 96, WY)]
    out.append(K.paint(D, shell, nut, 7920, round_r=34, flow="contour", flow_jit=14, smooth=True, edge_col="#140802", edge_w=1.6,
                       passes=((80, (8, 18), (2, 4), (0.35, 0.6)), (260, (4, 9), (1, 2), (0.4, 0.8)))))
    for k in range(9):          # the walnut's wrinkled ridges
        x0 = WX - 80 + k * 20
        out.append(K.taper([(x0, WY + 6), (x0 + 6 * math.sin(k), WY + 24), (x0 - 4, WY + 42)], 2.2, 0.6, "#2A1408", 0.5))
    out.append(f'<ellipse cx="{WX}" cy="{WY}" rx="96" ry="16" fill="#3A1E0C" stroke="#140802" stroke-width="1.4"/>')
    # violet-leaf mattress, rose-petal blanket, and one golden curl
    out.append(f'<path d="{K.smooth_closed([(WX - 84, WY - 2), (WX - 40, WY - 12), (WX + 40, WY - 12), (WX + 86, WY - 2), (WX + 40, WY + 6), (WX - 40, WY + 6)])}" fill="#3E6E2A" stroke="#1E3A12" stroke-width="1"/>')
    petal = K.Look(["#7A1A3A", "#B83A5E", "#E07A92", "#F8B8C8", "#FFE4EC"], key=(-0.7, -0.6, 0.5), amb=0.1, wrap=0.45)
    out.append(K.paint(D, [(WX - 50, WY - 4), (WX - 30, WY - 26), (WX + 20, WY - 32), (WX + 66, WY - 20), (WX + 74, WY - 4), (WX + 20, WY + 4)], petal, 7921,
                       round_r=16, flow="contour", edge_col="#7A1A3A", edge_w=1.2))
    out.append(f'<ellipse cx="{WX - 62}" cy="{WY - 10}" rx="16" ry="10" fill="#FFF4F0" stroke="#D8C8C0" stroke-width="0.8"/>')
    out.append(f'<path d="M{WX - 70} {WY - 18}q6 -6 12 0q4 6 -2 8" stroke="#E8B030" stroke-width="2.4" fill="none"/>')
    # the swallow on the window frame, watching
    out.append(swallow_painted(D, 330, 372, 2.4, 7930))
    art = D.render(out)
    DL = K.Doc("thbL")
    L = [K.halo(DL, 170, 120, 160, "#FFFAF0", 0.55, ry=70)]
    L.append(K.title(DL, 170, 130, "Thumbelina", SERIF_IT, 50, max_w=240, face=("#E8607A", "#B8304A", "#6A1424"), shadow="#FFF6EE", sop=0.8))
    L.append(K.subtitle(170, 160, "HANS CHRISTIAN ANDERSEN · 1835", CINZEL, 15, "#4A2A20", ls=1.5, max_w=240, sh="#FFF8F0", sop=0.6))
    L.append(K.halo(DL, 300, 536, 240, "#3A2A1A", 0.45, ry=20))
    L.append(K.subtitle(300, 540, "Scarcely half as long as a thumb", SERIF_IT, 21, "#FFF6EA", max_w=400, sh="#2A1A0A", sop=0.8))
    return art, DL.render(L)
# ---- end plate: thumbelina ----


# ---- plate: the-elves-and-the-shoemaker ----
def shoe_painted(D, x, y, s, seed, look, flip=False, buckle=True):
    """A finished buckled shoe of the old style (side view): rounded toe, low stacked heel, tongue, a silver buckle;
    polished leather with a bright highlight along the toe."""
    T = lambda pts: K.xform(pts, x, y, s, 0, flip)
    out = [K.halo(D, x, y + 2 * s, 46 * s, "#000000", 0.5, ry=5 * s)]
    sole = T([(-40, 0), (40, 0), (44, -3), (38, -5), (-36, -5), (-41, -3)])
    out.append(f'<path d="{K.smooth_closed(sole)}" fill="#1A0C06"/>')
    heel = T([(-40, 0), (-24, 0), (-26, -9), (-40, -9)])
    out.append(f'<path d="{K.poly_d(heel)}" fill="#2A140A" stroke="#0A0402" stroke-width="0.8"/>')
    upper = T([(-40, -8), (-42, -22), (-36, -30), (-20, -28), (-4, -24), (6, -32), (14, -30), (12, -22), (26, -18), (40, -12), (46, -6), (40, -4), (-36, -6)])
    out.append(K.paint(D, upper, look, seed, round_r=10 * s, flow="contour", flow_jit=6, edge_col="#0A0402", edge_w=1.4, rim_col="#FFE0B0", rim_w=1.2,
                       passes=((80, (6, 14), (2, 4), (0.35, 0.6)), (260, (3, 7), (1, 2), (0.4, 0.8)))))
    out.append(K.taper(T([(16, -18), (30, -14), (42, -8)]), 2.4 * s, 0.6 * s, "#FFF4DC", 0.8))
    out.append(K.taper(T([(-38, -24), (-28, -27), (-18, -26)]), 1.4 * s, 0.4 * s, "#FFF4DC", 0.6))
    for k in range(9):
        p = T([(-36 + k * 8, -7.5)])[0]
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{0.6 * s:.1f}" fill="#E8D0A0" opacity="0.7"/>')
    if buckle:
        b = T([(-2, -27), (10, -29), (11, -20), (-1, -18)])
        out.append(f'<path d="{K.poly_d(b)}" fill="none" stroke="#E8ECF4" stroke-width="{2.2 * s * 0.5:.1f}"/>')
        out.append(f'<path d="{K.poly_d(b)}" fill="none" stroke="#6A7280" stroke-width="{0.8 * s * 0.5:.1f}"/>')
    return "".join(out)


@plate("the-elves-and-the-shoemaker", 97, edge=1.6, bristle=0.35, grain=0.2)
def elves_shoemaker_plate():
    """Christmas night in the poor shoemaker's shop: on the bench by the candle, where he left only cut leather,
    a pair of shoes so finely stitched they glow; tools laid out, thread, a last, and in the leather dust a trail
    of tiny footprints leading away."""
    D = K.Doc("els")
    out = []
    out.append(f'<rect x="-10" y="-10" width="620" height="620" fill="#140A06"/>')
    # back wall of rough plaster and timber, a shelf of lasts, the snowy window
    out.append(K.brushwork(9701, (-10, -10, 610, 380), ["#2A1A10", "#3A2416", "#1A0E08"], 240, L=(30, 80), W=(3, 8), op=(0.25, 0.5), angle=lambda x, y: 15 * math.sin(y * 0.02), jit=30))
    WX0, WX1, WY0, WY1 = 330, 540, 80, 300
    cid = D.clip(f"M{WX0} {WY0}H{WX1}V{WY1}H{WX0}Z")
    o = [K.sky(D, [(0, "#0A1430"), (1, "#24345A")], 9702, WY0, WY1, n=40, op=(0.05, 0.12))]
    for (hx, hw, hh) in ((350, 50, 60), (410, 60, 80), (480, 50, 56)):
        o.append(f'<path d="M{hx - hw / 2} 300V{300 - hh}L{hx} {300 - hh - 26}L{hx + hw / 2} {300 - hh}V300Z" fill="#141C30"/>')
        o.append(f'<path d="M{hx - hw / 2 - 4} {300 - hh + 2}L{hx} {300 - hh - 26}L{hx + hw / 2 + 4} {300 - hh + 2}" stroke="#E8F0FF" stroke-width="4" fill="none"/>')
        o.append(f'<rect x="{hx - 6}" y="{300 - hh + 18}" width="10" height="12" fill="#FFC860"/>')
    rnd = random.Random(9703)
    for _ in range(60):
        o.append(f'<circle cx="{rnd.uniform(WX0, WX1):.1f}" cy="{rnd.uniform(WY0, WY1):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(f'<g {cid}>{"".join(o)}</g>')
    out.append(f'<path d="M{WX0} {WY0}H{WX1}V{WY1}H{WX0}Z M{(WX0 + WX1) / 2} {WY0}V{WY1} M{WX0} {(WY0 + WY1) / 2}H{WX1}" stroke="#2A1A0E" stroke-width="8" fill="none"/>')
    out.append(f'<path d="M{WX0 + 4} {WY1 - 6}H{WX1 - 4}" stroke="#E8F0FF" stroke-width="6" opacity="0.8"/>')
    # the candle's warm pool of light
    CX, CY = 140, 330
    out.append(K.halo(D, CX, CY + 40, 320, "#FFA040", 0.45))
    out.append(K.halo(D, CX, CY, 110, "#FFD890", 0.6))
    # the workbench: old scrubbed wood, worn, seen from slightly above
    bench = K.Look(["#1A0C06", "#3A2010", "#5E381C", "#8A5A30", "#B8844E", "#E0B07A"], key=(-0.9, -0.3, 0.6), amb=0.06, wrap=0.35, jit=0.04)
    top = [(-20, 380), (620, 380), (640, 610), (-40, 610)]
    out.append(K.paint(D, top, bench, 9706, round_r=60, flow=0, flow_jit=3, smooth=False, edge_col=None,
                       value_fn=lambda x, y: 0.35 * max(0, 1 - math.hypot(x - CX, y - 400) / 380) - 0.15, passes=((50, (40, 90), (3, 6), (0.3, 0.5)), (160, (20, 50), (1, 2), (0.3, 0.55)))))
    for k in range(5):
        out.append(f'<path d="M-20 {400 + k * 44}H620" stroke="#0E0602" stroke-width="1.4" opacity="0.5"/>')
    out.append(f'<rect x="-20" y="372" width="640" height="10" fill="#4A2A14"/>')
    # the candle in a pewter stick
    out.append(f'<ellipse cx="{CX}" cy="402" rx="30" ry="9" fill="#5A5A60" stroke="#202024" stroke-width="1"/>')
    out.append(f'<rect x="{CX - 9}" y="330" width="18" height="70" fill="{D.lin([(0, "#E8DCC0"), (0.5, "#FFF6E0"), (1, "#A8987A")], 0, 0, 1, 0)}"/>')
    out.append(f'<path d="M{CX - 9} 336q4 10 0 22" stroke="#F8F0DC" stroke-width="3" fill="none"/>')
    out.append(f'<path d="{K.smooth_closed([(CX - 5, 330), (CX - 3, 312), (CX, 300), (CX + 3, 312), (CX + 5, 330)])}" fill="#FFC050"/>')
    out.append(f'<path d="{K.smooth_closed([(CX - 2.4, 328), (CX - 1, 316), (CX, 308), (CX + 1, 316), (CX + 2.4, 328)])}" fill="#FFFAE0"/>')
    # the finished shoes, the hero of the plate, glowing a little
    leather = K.Look(["#120404", "#3A0E08", "#6A2210", "#9A3E1C", "#C86A34", "#F0A868"], key=(-0.9, -0.4, 0.5), amb=0.05, wrap=0.3,
                     spec=("#FFF0D8", 0.85, 0.8), rim=("#FFD890", (-0.9, -0.3), 0.6))
    out.append(K.halo(D, 350, 430, 130, "#FFD890", 0.28))
    out.append(shoe_painted(D, 320, 440, 2.3, 9707, leather))
    out.append(shoe_painted(D, 420, 470, 2.3, 9708, leather.darker(0.06)))
    # tools: awl, hammer, a spool of thread, scraps, and a sparkle on the needle
    out.append(K.taper([(470, 540), (560, 520)], 5, 3, "#7A5030", 1) + K.taper([(560, 520), (588, 514)], 2, 0.6, "#D8DCE4", 1))
    out.append(K.taper([(200, 520), (280, 508)], 6, 5, "#6A4426", 1))
    out.append(f'<path d="{K.poly_d([(274, 492), (292, 490), (296, 520), (278, 522)])}" fill="#5A5E66" stroke="#202024" stroke-width="1"/>')
    out.append(f'<ellipse cx="96" cy="470" rx="22" ry="10" fill="#C8A060"/><rect x="74" y="446" width="44" height="24" fill="#2E6A3A"/><ellipse cx="96" cy="446" rx="22" ry="10" fill="#E0B878"/><ellipse cx="96" cy="446" rx="5" ry="2" fill="#4A2A10"/>')
    for k in range(5):
        out.append(f'<path d="M74 {450 + k * 4}H118" stroke="#1E4A28" stroke-width="1" opacity="0.6"/>')
    out.append(f'<path d="M118 452Q180 470 230 520" stroke="#3E8A4E" stroke-width="1.2" fill="none"/>')
    for (px, py, a, c) in ((210, 440, 20, "#8A3A1A"), (240, 570, -10, "#6A2A10"), (520, 420, 40, "#A04A20")):
        out.append(f'<path d="{K.blob(px, py, 26, 12, int(px), 0.3, 12, a)}" fill="{c}" opacity="0.8"/>')
    # tiny footprints in the leather dust, trailing off the edge of the bench
    for k in range(9):
        fx = 470 + k * 16
        fy = 486 + k * 6 + (4 if k % 2 else -4)
        out.append(f'<ellipse cx="{fx}" cy="{fy}" rx="3.4" ry="1.6" fill="#2A1408" opacity="0.6" transform="rotate(20 {fx} {fy})"/>')
    art = D.render(out)
    DL = K.Doc("elsL")
    L = [K.halo(DL, 300, 60, 260, "#0A0402", 0.0)]
    L.append(K.subtitle(170, 92, "BROTHERS GRIMM", CINZEL, 15, "#E8D0B0", ls=3, max_w=240, sh="#000000", sop=0.7))
    L.append(K.title(DL, 170, 140, "The Elves", SERIF_IT, 40, max_w=250, face=("#FFF0C8", "#F0C060", "#A86A1E"), shadow="#000000", sop=0.8))
    L.append(K.title(DL, 170, 182, "& the Shoemaker", SERIF_IT, 32, max_w=250, face=("#FFF0C8", "#F0C060", "#A86A1E"), shadow="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: the-elves-and-the-shoemaker ----


# ---- plate: yggdrasil ----
@plate("yggdrasil", 89, edge=1.8, bristle=0.35, grain=0.2)
def yggdrasil_plate():
    """The World Ash under the turning stars: a trunk wider than a hall, its crown spread over the heavens with an
    eagle at the top, its great roots plunging into the misty glowing well of Urd where the Norns water it."""
    D = K.Doc("ygg")
    out = []
    out.append(K.sky(D, [(0, "#04081A"), (0.45, "#0E1E40"), (0.8, "#1E3A52"), (1, "#2A4A50")], 8901, 0, 600, n=140, op=(0.05, 0.14)))
    out.append(K.stars(8902, (0, 0, 600, 420), 200, r=(0.4, 1.5), op=(0.4, 1.0)))
    rnd = random.Random(8903)
    # the turning heavens: faint concentric star trails around the crown
    for r in (150, 200, 250, 300):
        out.append(f'<circle cx="300" cy="200" r="{r}" fill="none" stroke="#9AB8E0" stroke-width="0.8" stroke-dasharray="{rnd.uniform(4, 20):.0f} {rnd.uniform(8, 30):.0f}" opacity="0.25"/>')
    out.append(K.halo(D, 300, 200, 260, "#F2D890", 0.3))
    # the branches: a recursive crown from the top of the trunk
    bark = K.Look(["#06080A", "#141814", "#262C24", "#3E4632", "#5E6648", "#8A9068"], key=(0.0, 1.0, 0.4), amb=0.08, wrap=0.4, jit=0.05,
                  rim=("#F8E0A0", (0, -1), 0.5))
    limbs = []
    tips = []

    def grow(x, y, ang, L, w, depth):
        a = math.radians(ang)
        pts = [(x, y)]
        for k in range(1, 5):
            t = k / 4
            pts.append((x + math.cos(a) * L * t + rnd.uniform(-4, 4) * depth, y + math.sin(a) * L * t + rnd.uniform(-4, 4) * depth))
        limbs.append((pts, w, w * 0.62))
        ex, ey = pts[-1]
        if depth <= 1:
            tips.append((ex, ey))
            return
        for da in (-28, 22) if depth % 2 else (-20, 26):
            grow(ex, ey, ang + da + rnd.uniform(-10, 10), L * rnd.uniform(0.62, 0.78), w * 0.62, depth - 1)
    for ang in (-168, -140, -112, -68, -40, -12):
        grow(300, 300, ang, 96 if abs(ang + 90) < 60 else 116, 28, 4)
    for pts, w0, w1 in limbs:
        out.append(K.taper(pts, w0, w1, "#10140F", 1))
        out.append(K.taper([(x, y - w0 * 0.2) for x, y in pts], w0 * 0.25, w1 * 0.2, "#4E5640", 0.35))
    # foliage: clusters of ash leaves at every tip, lit gold from the heavens above
    leaf = K.Look(["#06100A", "#12261A", "#24402A", "#3E6236", "#6E8E46", "#C8C870"], key=(0.0, -1.0, 0.5), amb=0.05, wrap=0.3, jit=0.05)
    clumps = []
    for _ in range(46):
        a = rnd.uniform(math.pi, 2 * math.pi)
        rr = rnd.uniform(0.35, 1.0) ** 0.6
        clumps.append((300 + math.cos(a) * 250 * rr, 250 + math.sin(a) * 175 * rr, rnd.uniform(30, 52), rnd.uniform(22, 34)))
    clumps += [(x + rnd.uniform(-6, 6), y + rnd.uniform(-6, 6), rnd.uniform(22, 34), rnd.uniform(16, 24)) for (x, y) in tips if 40 < y < 330]
    clumps.sort(key=lambda c: c[1])
    back = K.Look([K.dk(c, 0.35) for c in leaf.cols], key=leaf.key, amb=0.05, wrap=0.3)
    out.append(K.foliage(D, clumps[::2], back, 8908, density=0.8, size=(3, 7)))
    out.append(K.foliage(D, clumps[1::2], leaf, 8904, density=1.0, size=(3, 7), holes="#F2D890", hole_n=40))
    # lower limbs visible beneath the canopy
    for pts, w0, w1 in limbs[:12]:
        if pts[-1][1] > 230:
            out.append(K.taper(pts, w0, w1, "#10140F", 0.9))
    # the eagle at the very top
    ex, ey = 300, 82
    out.append(f'<path d="M{ex - 34} {ey - 6}Q{ex - 18} {ey - 18} {ex - 6} {ey - 4}L{ex} {ey - 12}L{ex + 6} {ey - 4}Q{ex + 18} {ey - 18} {ex + 34} {ey - 6}Q{ex + 18} {ey - 8} {ex + 8} {ey + 4}L{ex + 4} {ey + 14}H{ex - 4}L{ex - 8} {ey + 4}Q{ex - 18} {ey - 8} {ex - 34} {ey - 6}Z" fill="#0A0C10" stroke="#F2D890" stroke-width="1" stroke-opacity="0.6"/>')
    # the trunk: vast, deeply fluted, splitting into roots at the bottom
    spine = [(300, 470), (296, 420), (304, 370), (300, 300), (302, 250), (300, 216)]
    out.append(K.trunk(D, spine, [130, 100, 86, 72, 56, 30], bark.toward("#2A3A3A", 0.1), 8905, roots=1, root_spread=1.6, crevices=50, knots=3,
                       rim="#F8E0A0", moss=["#3A5A3A", "#5A7A4A"]))
    # roots plunging down and out to the three wells
    gr = D.lin([(0, "#14241E"), (1, "#04080A")], 0, 460, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 470Q300 450 610 470V610H-10Z" fill="{gr}"/>')
    out.append(K.halo(D, 300, 490, 200, "#9AF0E0", 0.35, ry=50))
    out.append(f'<ellipse cx="300" cy="490" rx="76" ry="13" fill="{D.rad([(0, "#E8FFF8"), (0.6, "#8AE0D0"), (1, "#2A6A6A")])}"/>')
    out.append(K.mist(D, 470, 30, "#C8F0E8", 0.3, seed=8907, n=8, r=(60, 140)))
    # great roots snaking out over the ground toward the well
    for (tx, ty, w, bend) in ((40, 486, 30, -20), (140, 500, 26, 10), (470, 500, 26, -10), (566, 486, 30, 20)):
        sp = [(300 + (tx - 300) * 0.15, 452), (300 + (tx - 300) * 0.45, 468 + bend * 0.3), (300 + (tx - 300) * 0.75, 476 + bend * 0.2), (tx, ty)]
        out.append(K.trunk(D, sp, [w, w * 0.75, w * 0.5, w * 0.25], bark, 8906 + tx, crevices=6, knots=0, rim="#9AF0E0", edge_col="#000000"))
    # Ratatoskr the squirrel running down the trunk
    sx, sy = 330, 370
    out.append(f'<path d="M{sx} {sy}q6 -2 8 4q2 6 -2 10l-6 2q-4 -6 0 -16Z" fill="#8A4A1E"/><path d="M{sx + 2} {sy + 14}q10 6 6 18q-10 -4 -6 -18Z" fill="#A85A28"/>')
    art = D.render(out)
    DL = K.Doc("yggL")
    L = [K.halo(DL, 300, 524, 220, "#02040A", 0.55, ry=34)]
    L.append(K.title(DL, 300, 520, "Yggdrasil", SERIF_IT, 50, max_w=400, face=("#FFF4C8", "#F2C860", "#9A6A1C"), shadow="#000000", sop=0.85))
    L.append(K.subtitle(300, 544, "THE WORLD TREE · NORSE MYTH", CINZEL, 15, "#E0ECE0", ls=3, max_w=360, sh="#000000", sop=0.8))
    return art, DL.render(L)
# ---- end plate: yggdrasil ----


# ---- plate: icarus ----
def winged_man(x, y, h, ang, seed, spread=1.0):
    """Icarus in silhouette: a man about 7 heads tall, arms flung up and out with wings of feathers bound along
    them, body arched in the fall, legs trailing. Returns (outline points of the body, list of feather polygons)."""
    rnd = random.Random(seed)
    pose = dict(lean=-18, head=-30, ua_n=100, fa_n=112, ua_f=-96, fa_f=-108, th_n=20, sh_n=-30, th_f=-10, sh_f=-50, foot=0.6)
    far, near, head, J = K.figure_parts(0, 0, h, pose)
    polys = [[(px, py) for px, py in p] for p in far + near]
    c = head[0]
    outline = K.union_outline([(c[0], c[1], head[1], head[2], head[3])], polys, step=1.0, smooth_px=0.6)
    feathers = []
    # each wing: a fan of long feathers hanging off the arm from shoulder to hand
    sh = J["shoulder"]
    for hand in (J["hand_n"], J["hand_f"]):
        for k in range(12):
            t = k / 11
            bx, by = sh[0] + (hand[0] - sh[0]) * (0.2 + 0.85 * t), sh[1] + (hand[1] - sh[1]) * (0.2 + 0.85 * t)
            dx, dy = hand[0] - sh[0], hand[1] - sh[1]
            L0 = math.hypot(dx, dy) or 1
            nx, ny = dy / L0, -dx / L0          # trailing side
            if ny < 0:
                nx, ny = -nx, -ny
            L = h * (0.42 + 0.3 * t) * spread * rnd.uniform(0.9, 1.1)
            ax = (nx * 0.8 + dx / L0 * 0.45 * t, ny * 0.8 + dy / L0 * 0.45 * t)
            al = math.hypot(*ax) or 1
            ux, uy = ax[0] / al, ax[1] / al
            w = h * 0.06
            tip = (bx + ux * L, by + uy * L)
            feathers.append([(bx - uy * w, by + ux * w), (bx + ux * L * 0.6 - uy * w * 1.2, by + uy * L * 0.6 + ux * w * 1.2), tip,
                             (bx + ux * L * 0.6 + uy * w, by + uy * L * 0.6 - ux * w), (bx + uy * w, by - ux * w)])
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    rot = lambda pts: [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    return rot(outline), [rot(f) for f in feathers]


@plate("icarus", 7, edge=1.6, bristle=0.32, grain=0.18)
def icarus_plate():
    """High over the wine-dark Aegean the sun blazes; Icarus, too near it, tumbles in silhouette against the
    disc, the wax running and his feathers scattering on the wind; far below and away, Daedalus flies on."""
    D = K.Doc("icr")
    out = []
    out.append(K.sky(D, [(0, "#F8C878"), (0.35, "#F6A85A"), (0.7, "#E8784A"), (1, "#B85848")], 701, 0, 400, n=160, op=(0.06, 0.16)))
    SX, SY = 300, 210
    out.append(K.halo(D, SX, SY, 300, "#FFF4C0", 0.75))
    out.append(K.halo(D, SX, SY, 160, "#FFFFF0", 0.85))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="112" fill="{D.rad([(0, "#FFFFF8"), (0.7, "#FFF6C8"), (1, "#FFE08A")])}"/>')
    # sun rays, long and faint
    rnd = random.Random(702)
    for k in range(36):
        a = k * math.pi / 18 + rnd.uniform(-0.05, 0.05)
        out.append(f'<path d="M{SX + math.cos(a) * 120:.1f} {SY + math.sin(a) * 120:.1f}L{SX + math.cos(a) * 420:.1f} {SY + math.sin(a) * 420:.1f}" stroke="#FFF6D8" stroke-width="{rnd.uniform(2, 8):.1f}" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>')
    out.append(K.cloud_bank(D, 330, 390, ["#F8C890", "#E89070", "#B86A6A"], 703, n=40, r=(30, 70), op=(0.2, 0.45), streaks=20))
    # the sea far below, the islands, the sun's path
    out.append(K.water(D, 392, 600, [(0, "#F2B080"), (0.2, "#A85A6A"), (0.6, "#3A2E5A"), (1, "#1A1A3A")], 704, n=460, refl_x=SX, refl_w=40, refl_col="#FFF0C8", glints=220))
    for (ix, iw, ih) in ((80, 90, 18), (500, 120, 22), (420, 40, 9)):
        out.append(f'<path d="{K.smooth_closed([(ix - iw / 2, 394), (ix - iw * 0.2, 394 - ih), (ix + iw * 0.15, 394 - ih * 0.8), (ix + iw / 2, 394)])}" fill="#6A4A6A"/>')
    # Daedalus, small and far, flying steadily on
    dsil, dfe = winged_man(486, 300, 34, -84, 705, 0.9)
    for f in dfe:
        out.append(f'<path d="{K.poly_d(f)}" fill="#3A2A3A" opacity="0.85"/>')
    out.append(f'<path d="{K.smooth_closed(dsil)}" fill="#3A2A3A"/>')
    # Icarus against the sun: dark figure with a burning rim, wings losing feathers
    sil, fe = winged_man(SX - 10, SY + 6, 120, 128, 706, 1.0)
    for i, f in enumerate(fe):
        if i % 4 == 1:
            continue                                  # gaps where feathers have already gone
        out.append(f'<path d="{K.poly_d(f)}" fill="#2A140E"/>')
        out.append(f'<path d="{K.poly_d(f)}" fill="none" stroke="#FFB850" stroke-width="1" opacity="0.6"/>')
    out.append(f'<path d="{K.smooth_closed(sil)}" fill="#1E0E0A"/>')
    out.append(K.edges(K.resample(sil, 2), (0, 1), 707, dark=None, lit="#FFC870", w=1.6, lit_op=0.9, lit_thresh=-0.3))
    # drops of melting wax and scattered feathers drifting down and away
    for _ in range(12):
        x, y = rnd.uniform(SX - 80, SX + 80), rnd.uniform(SY + 40, SY + 160)
        out.append(f'<path d="M{x:.1f} {y:.1f}q2 5 0 8q-2 -3 0 -8Z" fill="#FFE8A0" opacity="0.9"/>')
    for _ in range(16):
        x, y = rnd.uniform(140, 470), rnd.uniform(250, 380)
        a = rnd.uniform(0, 360)
        L = rnd.uniform(12, 24)
        out.append(K.feather(D, (x, y), a, L, L * 0.16, ("#4A2A1E", "#8A5A40", "#E8C090"), rnd.randint(0, 9999), curve=0.12, barbs=3))
    art = D.render(out)
    DL = K.Doc("icrL")
    L = [K.halo(DL, 300, 90, 0, "#000000", 0)]
    L.append(K.title(DL, 300, 96, "ICARUS", CINZEL, 58, max_w=380, ls=12, face=("#7A2A10", "#5A1A08", "#3A0E04"), shadow="#FFF4D8", sop=0.6))
    L.append(K.halo(DL, 300, 528, 250, "#141030", 0.55, ry=30))
    L.append(K.subtitle(300, 524, "Fly the middle course.", SERIF_IT, 26, "#FFF0D8", max_w=420, sh="#000000", sop=0.8))
    L.append(K.subtitle(300, 546, "DAEDALUS TO HIS SON · OVID", CINZEL, 13, "#E8D8C8", ls=2, max_w=300, sh="#000000", sop=0.7))
    return art, DL.render(L)
# ---- end plate: icarus ----


# ---- plate: sinbad-the-sailor ----
def dhow_painted(D, x, wl, s, seed, light=(0.8, -0.4)):
    """An Arab dhow riding the swell: raked stem, high stern, a great lateen sail bellied by the wind, rigging."""
    T = lambda pts: K.xform(pts, x, wl, s)
    out = []
    hull_l = K.Look(["#0A0604", "#1E120A", "#3A2414", "#5E3E22", "#8A6034"], key=(light[0], light[1], 0.5), amb=0.06, wrap=0.3, rim=("#FFC880", light, 0.6))
    hull = T([(-60, -6), (-52, -16), (-40, -12), (30, -10), (64, -24), (58, -10), (40, 4), (-44, 4)])
    out.append(K.paint(D, hull, hull_l, seed, round_r=8 * s, flow=0, edge_col="#000000", edge_w=1.2, rim_col="#FFC880", rim_w=1.2))
    out.append(K.taper(T([(-50, -10), (0, -8), (50, -14)]), 1.2 * s, 1.2 * s, "#C88A50", 0.7))
    out.append(f'<path d="M{T([(-4, -10)])[0][0]:.1f} {T([(-4, -10)])[0][1]:.1f}L{T([(0, -96)])[0][0]:.1f} {T([(0, -96)])[0][1]:.1f}" stroke="#1A0E06" stroke-width="{2.4 * s * 0.5:.1f}"/>')
    sail = T([(-48, -24), (-20, -56), (10, -88), (42, -106), (40, -70), (34, -24), (-6, -20)])
    sl = K.Look(["#5A4A3A", "#8A7660", "#B8A288", "#E2D2B4", "#FFF4DE"], key=(light[0], light[1], 0.5), amb=0.15, wrap=0.4, rim=("#FFE0A0", light, 0.6))
    out.append(K.paint(D, sail, sl, seed + 1, round_r=20 * s, bumps=[(*T([(14, -50)])[0], 30 * s, 26 * s, 0, 8 * s)], flow="contour", edge_col="#2A1E14", edge_w=1.2,
                       rim_col="#FFE6B0", rim_w=1.4))
    yard = T([(-54, -20), (46, -110)])
    out.append(f'<path d="M{yard[0][0]:.1f} {yard[0][1]:.1f}L{yard[1][0]:.1f} {yard[1][1]:.1f}" stroke="#1A0E06" stroke-width="{1.8 * s * 0.5:.1f}"/>')
    for a, b in (([0, -96], [56, -22]), ([0, -96], [-56, -10]), ([30, -60], [50, -14])):
        p, q = T([a])[0], T([b])[0]
        out.append(f'<path d="M{p[0]:.1f} {p[1]:.1f}L{q[0]:.1f} {q[1]:.1f}" stroke="#1A0E06" stroke-width="0.8" opacity="0.8"/>')
    return "".join(out)


@plate("sinbad-the-sailor", 3, edge=1.8, bristle=0.35, grain=0.2)
def sinbad_plate():
    """The Roc: over a storm-dark sea at sunset the monstrous bird spreads wings that blot out the sky, a boulder
    clutched in its talons, while below, Sinbad's dhow runs before the wind."""
    D = K.Doc("snb")
    out = []
    out.append(K.sky(D, [(0, "#1A1428"), (0.35, "#4A2A3A"), (0.65, "#B8604A"), (0.85, "#F2A860"), (1, "#FCD890")], 301, 0, 400, n=160, op=(0.06, 0.18)))
    out.append(K.halo(D, 470, 380, 240, "#FFD890", 0.6, ry=120))
    out.append(K.cloud_bank(D, 260, 360, ["#3A2234", "#6A3A44", "#B8604A", "#F2A860"], 302, n=50, r=(30, 70), op=(0.25, 0.5), lit_under=("#FFD890", 0.5)))
    # the sea: heavy swells, white crests
    out.append(K.water(D, 380, 600, [(0, "#C8806A"), (0.15, "#6A3E4A"), (0.6, "#1E2236"), (1, "#0A0E1A")], 303, n=500, refl_x=470, refl_w=40, refl_col="#FFE0A0", glints=160))
    rnd = random.Random(304)
    for row in range(7):
        y = 400 + row * 30
        pts = [(x, y + 8 * math.sin(x * 0.03 + row)) for x in range(-20, 640, 16)]
        out.append(f'<path d="{K.smooth_open(pts)} L640 {y + 40} L-20 {y + 40}Z" fill="{K.mix("#2A2A40", "#0A0E1A", row / 7)}" opacity="0.6"/>')
        for x in range(-20, 640, 40):
            if rnd.random() < 0.5:
                yy = y + 8 * math.sin(x * 0.03 + row) - 2
                out.append(K.taper([(x, yy), (x + rnd.uniform(14, 30), yy - rnd.uniform(0, 4))], rnd.uniform(1.5, 3.5), 0.4, "#F4ECE0", rnd.uniform(0.5, 0.9)))
    # the dhow
    out.append(dhow_painted(D, 400, 430, 1.6, 305))
    for _ in range(14):
        x = rnd.uniform(300, 520)
        out.append(K.taper([(x, 434), (x + rnd.uniform(-20, 20), 428)], 2, 0.5, "#FFFFFF", 0.7))
    # ---- the roc, seen from below, wings spread across the sky
    BX, BY = 270, 186
    plum = ["#06040A", "#140C10", "#28181A", "#3E2A24", "#5E4232", "#8A6448", "#C89A6A"]
    for side in (-1, 1):
        S = (BX + side * 20, BY - 20)
        E = (BX + side * 100, BY - 34)
        W_ = (BX + side * 184, BY - 40)
        Tp = (BX + side * 270, BY - 24)
        out.append(K.wing(D, S, E, W_, Tp, plum, 306 + side, trail=side, light=(0.6, 0.8),
                          prim_len=(70, 110), sec_len=(78, 84), ter_len=(56, 48), n_prim=10, n_sec=12, fan=0.7, shade_amt=0.25, dark=0.05,
                          shadow_col="#000000", lit_rim="#FFB060", glaze=0.3, rim_op=0.6))
    # tail fan
    for k in range(9):
        a = math.radians(90 + (k - 4) * 9)
        out.append(K.feather(D, (BX, BY + 20), math.degrees(a), 84, 10, ("#0A0608", "#2A1A16", "#6A4A32"), 307 + k, curve=0.02, barbs=4, rim="#FFB060", rim_op=0.5))
    # body, head and hooked beak
    roc_l = K.Look(plum, key=(0.6, 0.8, 0.4), amb=0.05, wrap=0.3, rim=("#FFB060", (0.6, 0.8), 0.6))
    body = [(BX - 22, BY - 30), (BX - 14, BY - 50), (BX, BY - 56), (BX + 14, BY - 50), (BX + 22, BY - 30), (BX + 26, BY - 4),
            (BX + 18, BY + 26), (BX + 8, BY + 40), (BX - 8, BY + 40), (BX - 18, BY + 26), (BX - 26, BY - 4)]
    out.append(K.paint(D, body, roc_l, 308, round_r=20, flow=90, flow_jit=12, edge_col="#000000", edge_w=1.4, rim_col="#FFB060", rim_w=1.6))
    head = [(BX - 11, BY - 50), (BX - 10, BY - 66), (BX, BY - 74), (BX + 10, BY - 66), (BX + 11, BY - 50)]
    out.append(K.paint(D, head, roc_l.darker(-0.05), 309, round_r=8, flow="contour", edge_col="#000000", edge_w=1.2, rim_col="#FFB060", rim_w=1.2))
    out.append(f'<path d="M{BX - 5} {BY - 72}Q{BX} {BY - 90} {BX + 6} {BY - 78}Q{BX + 2} {BY - 76} {BX + 4} {BY - 70}Z" fill="#C8A040" stroke="#3A2408" stroke-width="1"/>')
    # talons gripping a great boulder
    rock = K.Look(["#0A0808", "#1E1A18", "#3A3430", "#5E564E", "#8A8070"], key=(0.6, -0.7, 0.5), amb=0.06, wrap=0.3, rim=("#FFC880", (0.8, -0.4), 0.6))
    boulder = K.rough([(BX - 34, BY + 70), (BX - 20, BY + 48), (BX + 14, BY + 46), (BX + 36, BY + 64), (BX + 30, BY + 96), (BX - 10, BY + 104), (BX - 34, BY + 90), (BX - 34, BY + 70)], 310, 3, 6)[:-1]
    out.append(K.paint(D, boulder, rock, 311, round_r=24, flow="contour", flow_jit=20, edge_col="#000000", edge_w=1.4, rim_col="#FFC880", rim_w=1.4))
    for side in (-1, 1):
        for k in range(3):
            base = (BX + side * 10, BY + 46)
            tip = (BX + side * (14 + k * 8), BY + 56 + k * 6)
            out.append(K.taper([base, ((base[0] + tip[0]) / 2 + side * 4, (base[1] + tip[1]) / 2), tip], 5, 1.4, "#C8A040", 1))
    art = D.render(out)
    DL = K.Doc("snbL")
    L = [K.halo(DL, 300, 530, 250, "#060810", 0.6, ry=30)]
    L.append(K.title(DL, 300, 526, "Sinbad the Sailor", SERIF_IT, 46, max_w=440, face=("#FFF0C8", "#F0B858", "#A8601E"), shadow="#000000", sop=0.85))
    L.append(K.subtitle(300, 548, "THE THOUSAND AND ONE NIGHTS", CINZEL, 13, "#E8D8C8", ls=2.5, max_w=360, sh="#000000", sop=0.75))
    return art, DL.render(L)
# ---- end plate: sinbad-the-sailor ----


# ---- plate: jack-and-the-beanstalk ----
def heart_leaf_k(D, x, y, s, ang, seed, look):
    """A broad bean leaf: heart-shaped, pointed tip, midrib and veins, modelled by `look`."""
    pts = [(0, 0), (-0.5, -0.35), (-0.95, -0.2), (-1.0, 0.25), (-0.7, 0.75), (0, 1.35), (0.7, 0.75), (1.0, 0.25), (0.95, -0.2), (0.5, -0.35)]
    P = K.xform([(px, py) for px, py in pts], x, y, s, ang)
    out = [K.paint(D, P, look, seed, round_r=s * 0.5, flow="axis", flow_jit=25, edge_col=K.ramp(look.cols, 0.0), edge_w=1.1,
                   passes=((140, (6, 14), (1.5, 3), (0.35, 0.65)), (300, (3, 7), (0.8, 1.5), (0.4, 0.8))))]
    out.append(K.taper(K.xform([(0, -0.1), (0, 0.6), (0, 1.25)], x, y, s, ang), 1.8, 0.4, K.ramp(look.cols, 0.9), 0.6))
    for sd in (-1, 1):
        for t in (0.2, 0.5, 0.8):
            out.append(K.taper(K.xform([(0, t), (sd * 0.45, t + 0.12), (sd * 0.75, t + 0.05)], x, y, s, ang), 1.0, 0.3, K.ramp(look.cols, 0.85), 0.45))
    return "".join(out)


@plate("jack-and-the-beanstalk", 27, edge=1.8, bristle=0.35, grain=0.18)
def jack_beanstalk_plate():
    """From the cottage garden, looking straight up: the beanstalk that grew overnight, three stems twisted into
    one, climbs past the clouds to the giant's castle shining in the sky; far up the stalk, a small figure climbs."""
    D = K.Doc("jbs")
    out = []
    out.append(K.sky(D, [(0, "#3A6AB0"), (0.4, "#6A9AD0"), (0.8, "#B8D4EC"), (1, "#E8F0F4")], 2701, 0, 600, n=160, op=(0.05, 0.14)))
    cl = K.Look(["#6A7A9A", "#9AA8C0", "#C8D2E2", "#ECF0F6", "#FFFFFF"], key=(-0.6, -0.7, 0.5), amb=0.25, wrap=0.45, jit=0.02)
    # the cloud bank the castle stands on
    rnd = random.Random(2702)
    bank = [(rnd.uniform(240, 600), rnd.uniform(150, 190), rnd.uniform(26, 50)) for _ in range(16)]
    # the giant's castle, vast and pale in the sky
    castle_l = K.Look(["#6A6A8A", "#8A8AA8", "#B0B0C8", "#D8D8E8", "#F4F4FC"], key=(-0.6, -0.7, 0.5), amb=0.3, wrap=0.4)
    for (cx, w, h, roof) in ((380, 30, 86, 28), (430, 44, 116, 0), (480, 30, 96, 30), (520, 22, 72, 24), (340, 20, 64, 20), (456, 16, 134, 24)):
        base = 186
        out.append(K.paint(D, [(cx - w / 2, base), (cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w / 2, base)], castle_l, 2703 + cx, round_r=w * 0.5,
                           flow=90, smooth=False, edge_col="#5A5A78", edge_w=1, edge_op=0.4, passes=((80, (10, 24), (2, 4), (0.3, 0.5)),)))
        if roof:
            out.append(f'<path d="M{cx - w / 2 - 4} {base - h + 1}L{cx} {base - h - roof}L{cx + w / 2 + 4} {base - h + 1}Z" fill="#8A7AAA" stroke="#5A5A78" stroke-width="1"/>')
        else:
            for k in range(int(w / 8)):
                out.append(f'<rect x="{cx - w / 2 + k * 8}" y="{base - h - 6}" width="4.5" height="6" fill="#B0B0C8"/>')
        out.append(f'<rect x="{cx - 3}" y="{base - h * 0.6:.0f}" width="6" height="10" fill="#FFD890"/>')
    out.append(K.halo(D, 440, 120, 160, "#FFF6D8", 0.35))
    out.append(K.cumulus(D, bank, cl, 2704, flat_y=200, dab_r=(4, 10), rim="#FFFFFF", rim_w=1.4))
    out.append(K.cumulus(D, [(60, 300, 28), (100, 292, 34), (140, 304, 26), (30, 310, 20)], cl, 2705, flat_y=318, dab_r=(3, 8), rim="#FFFFFF", rim_w=1.2))
    out.append(K.cumulus(D, [(470, 360, 24), (504, 352, 30), (540, 362, 22)], cl, 2706, flat_y=376, dab_r=(3, 8), rim="#FFFFFF", rim_w=1.2))
    # the beanstalk: three stems twisting round each other, thick at the root, thinning into the clouds
    stem_l = K.Look(["#0E2A0E", "#1E4A1A", "#2E6A26", "#4E8E36", "#82B456", "#C8E08A"], key=(-0.6, -0.7, 0.5), amb=0.06, wrap=0.35, jit=0.04,
                    rim=("#F0F8C0", (-0.7, -0.6), 0.5))
    guide = []
    for k in range(40):
        t = k / 39
        guide.append((270 + 110 * math.sin(t * 6.0) * (1 - t) ** 0.7 + 100 * t, 620 - t * 450))
    for strand in range(3):
        ph = strand * 2.1
        pts = []
        widths = []
        for k, (gx, gy) in enumerate(guide):
            t = k / 39
            w = 58 * (1 - t) ** 0.8 + 9
            pts.append((gx + math.sin(t * 22 + ph) * w * 0.35, gy))
            widths.append(w * 0.55)
        out.append(K.trunk(D, pts[::2], widths[::2], stem_l, 2707 + strand, crevices=8, knots=0, edge_col="#06180A", rim="#E8F8B0"))
    # leaves along the stalk, tendrils curling out
    leaf = K.Look(["#0E2A0E", "#1E4E1C", "#367A2C", "#5EA040", "#9CCB6A", "#D8F0A8"], key=(-0.6, -0.7, 0.5), amb=0.06, wrap=0.35, jit=0.04)
    for k in range(3, 38, 4):
        gx, gy = guide[k]
        t = k / 39
        side = 1 if (k // 4) % 2 else -1
        s_ = 26 * (1 - t) + 12
        px, py = gx + side * (26 * (1 - t) + 8), gy
        out.append(K.taper([(gx + side * 6, gy + 4), (px, py - 4)], 2.4, 1.6, "#2E6A26", 1))
        out.append(heart_leaf_k(D, px, py - 4, s_, -side * rnd.uniform(30, 60), 2710 + k, leaf.darker(0.1 * (k % 2))))
        if k % 6 == 0:
            tx0, ty0 = gx - side * 20, gy
            curl = [(tx0 - side * (6 + 4 * j) * math.cos(j * 0.9), ty0 - 4 * j - 6 * math.sin(j * 0.9)) for j in range(9)]
            out.append(K.taper(curl, 2.4, 0.6, "#4E8E36", 0.9))
    # bean pods hanging
    for k in (9, 21, 30):
        gx, gy = guide[k]
        out.append(f'<path d="{K.smooth_closed([(gx + 14, gy), (gx + 24, gy + 20), (gx + 22, gy + 40), (gx + 16, gy + 30), (gx + 12, gy + 12)])}" fill="#6AA040" stroke="#1E4A1A" stroke-width="1"/>')
    # Jack, a small figure climbing high on the stalk
    jx, jy = guide[24]
    o, J = K.figure_silhouette(jx + 8, jy + 18, 30, dict(lean=-6, ua_n=170, fa_n=175, ua_f=150, fa_f=170, th_n=60, sh_n=-10, th_f=10, sh_f=-20, foot=0.6))
    out.append(f'<path d="{K.smooth_closed(o)}" fill="#2A1A10"/>')
    out.append(K.edges(K.resample(o, 1.5), (-0.7, -0.7), 2720, dark=None, lit="#FFE8B0", w=1.0, lit_op=0.8))
    # the ground: the widow's garden, the cottage, birds
    gr = D.lin([(0, "#6A9A4A"), (1, "#2E4A22")], 0, 540, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="M-10 556 Q300 532 610 556 V610 H-10Z" fill="{gr}"/>')
    out.append(f'<path d="M40 556V512L80 486L120 512V556Z" fill="#E8D8B8" stroke="#4A3A2A" stroke-width="1.2"/><path d="M32 514L80 478L128 514" stroke="#8A6A3A" stroke-width="8" fill="none"/>')
    out.append(f'<rect x="72" y="526" width="12" height="20" fill="#5A3A1E"/><rect x="96" y="520" width="12" height="12" fill="#FFD890"/>')
    out.append(K.grass(2721, (-10, 540, 610, 600), ["#4E7A30", "#7AAA4E", "#A8CC70"], n=200, h=(6, 18)))
    for (bx, by, s_) in ((180, 260, 1.0), (206, 276, 0.8), (520, 250, 0.9)):
        out.append(f'<path d="M{bx - 8 * s_:.1f} {by:.1f}q{4 * s_:.1f} -5 {8 * s_:.1f} 0q{4 * s_:.1f} -5 {8 * s_:.1f} 0" stroke="#2A3A5A" stroke-width="1.6" fill="none"/>')
    art = D.render(out)
    DL = K.Doc("jbsL")
    L = [K.halo(DL, 150, 120, 140, "#1E3A6A", 0.45, ry=80)]
    L.append(K.subtitle(150, 74, "JACK AND THE BEANSTALK", CINZEL, 14, "#FFFFFF", ls=2, max_w=220, sh="#0A1A3A", sop=0.7))
    L.append(K.title(DL, 150, 122, "Fee-fi-", SERIF_IT, 50, max_w=220, face=("#FFF4C8", "#F0C050", "#A8701E"), shadow="#0A1A3A", sop=0.8))
    L.append(K.title(DL, 150, 172, "fo-fum!", SERIF_IT, 50, max_w=220, face=("#FFF4C8", "#F0C050", "#A8701E"), shadow="#0A1A3A", sop=0.8))
    return art, DL.render(L)
# ---- end plate: jack-and-the-beanstalk ----


# ---- plate: the-little-mermaid ----
@plate("the-little-mermaid", 37, edge=1.6, bristle=0.32, grain=0.18)
def little_mermaid_plate():
    """The night of the prince's birthday: the little mermaid has surfaced for the first time and sits on a dark
    rock with her back to us, long hair lifting in the sea wind, her tail curled down into the moonlit water,
    watching the lit ship and the fireworks blossoming over it."""
    D = K.Doc("lmd")
    out = []
    HZ = 330
    out.append(K.sky(D, [(0, "#060A24"), (0.5, "#142048"), (0.85, "#2A3A6A"), (1, "#4A5A84")], 3701, 0, HZ, n=120, op=(0.05, 0.14)))
    out.append(K.stars(3702, (10, 10, 590, 260), 90, r=(0.4, 1.4), op=(0.4, 1.0)))
    MX, MY = 150, 150
    out.append(K.halo(D, MX, MY, 120, "#DCE4FF", 0.4))
    out.append(f'<circle cx="{MX}" cy="{MY}" r="30" fill="{D.rad([(0, "#FFFFF4"), (0.8, "#F0F0E0"), (1, "#D8DACC")])}"/>')
    rnd = random.Random(3703)
    for _ in range(10):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(4, 22)
        out.append(K.dab(MX + math.cos(a) * r, MY + math.sin(a) * r, rnd.uniform(3, 6), "#C8CAC0", 0.35, rnd))
    out.append(K.cloud_bank(D, 160, 240, ["#1A2244", "#3A4A78", "#8A94C0"], 3704, n=30, r=(30, 60), op=(0.2, 0.4), x0=240, x1=640, streaks=16))
    # fireworks over the ship
    for (fx, fy, r, c) in ((450, 150, 40, "#FFD86A"), (520, 200, 30, "#FF8AB0"), (400, 210, 26, "#8AE0FF")):
        out.append(K.halo(D, fx, fy, r * 1.6, c, 0.3))
        for k in range(26):
            a = k * 2 * math.pi / 26
            out.append(f'<path d="M{fx + math.cos(a) * r * 0.2:.1f} {fy + math.sin(a) * r * 0.2:.1f}Q{fx + math.cos(a) * r * 0.7:.1f} {fy + math.sin(a) * r * 0.7 + 3:.1f} {fx + math.cos(a) * r:.1f} {fy + math.sin(a) * r + 6:.1f}" stroke="{c}" stroke-width="1.2" fill="none" opacity="0.85"/>')
            out.append(f'<circle cx="{fx + math.cos(a) * r:.1f}" cy="{fy + math.sin(a) * r + 6:.1f}" r="1.4" fill="#FFFFFF"/>')
    # the sea: moon path, the lit ship on the horizon
    out.append(K.water(D, HZ, 600, [(0, "#4A5A84"), (0.3, "#24305A"), (1, "#080C1E")], 3705, n=520, refl_x=MX, refl_w=36, refl_col="#E8ECFF", glints=220))
    SX = 470
    out.append(K.halo(D, SX, HZ - 4, 70, "#FFC860", 0.45, ry=24))
    out.append(f'<path d="M{SX - 40} {HZ - 2}L{SX + 44} {HZ - 2}L{SX + 36} {HZ + 8}L{SX - 34} {HZ + 8}Z" fill="#14100E"/>')
    for (mx, mh) in ((SX - 18, 56), (SX + 6, 66), (SX + 28, 50)):
        out.append(f'<path d="M{mx} {HZ - 2}V{HZ - mh}" stroke="#14100E" stroke-width="1.6"/>')
        for k in range(3):
            y = HZ - mh + 8 + k * 15
            out.append(f'<path d="M{mx - 10 + k} {y}Q{mx} {y + 5} {mx + 10 - k} {y}V{y + 10}H{mx - 10 + k}Z" fill="#3A3438" opacity="0.9"/>')
    for k in range(12):
        x = SX - 36 + k * 7
        out.append(f'<circle cx="{x}" cy="{HZ + 2}" r="1.6" fill="#FFE08A"/>')
        out.append(f'<path d="M{x} {HZ + 9}v{rnd.uniform(6, 16):.0f}" stroke="#FFD070" stroke-width="1.4" opacity="0.6"/>')
    for k in range(8):
        a = math.pi * (0.1 + 0.8 * k / 7)
        x = SX - 40 + k * 12
        out.append(f'<circle cx="{x}" cy="{HZ - 30 - 18 * math.sin(a):.1f}" r="1.4" fill="#FFE8A0"/>')
    # ---- the rock and the mermaid
    rock = K.Look(["#020306", "#080C14", "#141C2A", "#26324A", "#44587A", "#8A9EC8"], key=(-0.8, -0.5, 0.4), amb=0.05, wrap=0.3, jit=0.05,
                  rim=("#DCE6FF", (-0.9, -0.4), 0.7))
    R = K.rough([(-20, 610), (-20, 470), (40, 440), (110, 428), (190, 432), (260, 446), (320, 474), (380, 520), (420, 610)], 3706, 4, 10)
    out.append(K.paint(D, R, rock, 3707, round_r=60, flow=lambda x, y, n: 20 * math.sin(x * 0.03), flow_jit=20, smooth=False, edge_col="#000000", edge_w=2,
                       rim_col="#DCE6FF", rim_w=2, rim_op=0.7, passes=((50, (14, 30), (3, 6), (0.3, 0.55)), (200, (6, 14), (1.2, 2.6), (0.35, 0.7)))))
    for _ in range(26):
        x = rnd.uniform(300, 430)
        y = K.y_on(R[1:-1], x) + rnd.uniform(-4, 10)
        out.append(K.taper([(x, y), (x + rnd.uniform(10, 30), y - rnd.uniform(0, 8))], rnd.uniform(1.5, 3.5), 0.4, "#E8F0FF", rnd.uniform(0.4, 0.8)))
    ox, oy, s = 190, 434, 2.5
    T = lambda pts: K.xform(pts, ox, oy, s)
    skin = K.Look(["#2A2440", "#4E4668", "#7E7498", "#B4A8C4", "#E2D8E4", "#FFF4F0"], key=(-0.8, -0.5, 0.45), amb=0.05, wrap=0.35,
                  rim=("#E8F0FF", (-0.9, -0.4), 0.8), bounce=("#5A6A9A", 0.3), jit=0.015)
    tailL = K.Look(["#04141A", "#0A2A30", "#145048", "#22786A", "#4AA894", "#A8E8D0"], key=(-0.8, -0.5, 0.45), amb=0.05, wrap=0.3,
                   rim=("#C8FFF0", (-0.9, -0.4), 0.7), spec=("#F0FFFA", 0.85, 0.7))
    # tail: from the hips down over the rock to the right, the fluke dipping in the sea
    tail = [(-12, -2), (-6, 6), (8, 14), (28, 18), (50, 20), (68, 26), (78, 36), (84, 30), (72, 16), (52, 8), (30, 4), (12, -2)]
    out.append(K.paint(D, T(tail), tailL, 3708, round_r=6 * s, flow="contour", flow_jit=8, edge_col="#02080A", edge_w=1.4, rim_col="#C8FFF0", rim_w=1.4,
                       passes=((80, (8, 18), (2, 4), (0.35, 0.6)), (260, (4, 9), (1, 2), (0.4, 0.8)))))
    tv = K.Vol(T(tail), 6 * s)
    sc = []
    for k in range(120):
        u = rnd.uniform(-8, 76)
        v = rnd.uniform(-6, 16)
        p = T([(u, v + u * 0.22)])[0]
        if tv.inside(*p):
            sc.append(f'<path d="M{p[0] - 3:.1f} {p[1]:.1f}q3 4 6 0" stroke="#A8F0E0" stroke-width="0.8" fill="none" opacity="{rnd.uniform(0.2, 0.55):.2f}"/>')
    out.append(f'<g {D.clip(K.smooth_closed(T(tail)))}>{"".join(sc)}</g>')
    fluke = T([(74, 30), (86, 24), (104, 30), (96, 40), (106, 52), (88, 46), (80, 40)])
    out.append(f'<path d="{K.smooth_closed(fluke)}" fill="#4AA894" opacity="0.6" stroke="#C8FFF0" stroke-width="1" stroke-opacity="0.6"/>')
    for k in range(6):
        a = T([(80, 34)])[0]
        b = T([(96 + k * 1.6, 28 + k * 4)])[0]
        out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="#C8FFF0" stroke-width="0.7" opacity="0.5"/>')
    # torso from behind: back, shoulder blades, the far arm leaning on the rock
    arm_n = T([(12, -48), (17, -44), (21, -32), (24, -20), (28, -8), (30, -4), (25, -3), (20, -14), (16, -26), (12, -36)])
    out.append(K.paint(D, arm_n, skin.darker(0.05), 3709, round_r=2.6 * s, flow="contour", edge_col="#141026", edge_w=1.2, rim_col="#E8F0FF", rim_w=1.2))
    back = T([(-12, -2), (-10, -12), (-9, -22), (-12, -34), (-15, -46), (-9, -53), (-3, -55), (3, -55), (9, -53), (15, -46), (12, -34), (9, -22), (10, -12), (12, -2)])
    out.append(K.paint(D, back, skin, 3710, round_r=9 * s, bumps=[(*T([(-7, -42)])[0], 6 * s, 8 * s, 0, 2 * s), (*T([(7, -42)])[0], 6 * s, 8 * s, 0, 2 * s)],
                       flow="contour", flow_jit=8, edge_col="#141026", edge_w=1.4, rim_col="#F0F4FF", rim_w=1.6, rim_op=0.7))
    out.append(K.taper(T([(0, -52), (0.6, -36), (0, -16)]), 1.8, 0.6, "#2A2440", 0.5))
    neck = T([(-3, -55), (-3.4, -62), (3.4, -62), (3, -55)])
    out.append(f'<path d="{K.poly_d(neck)}" fill="{K.ramp(skin.cols, 0.45)}"/>')
    # hair: a long auburn-gold mass down her back, locks lifting to the left in the wind
    hc = T([(0, -68)])[0]
    out.append(f'<ellipse cx="{hc[0]:.1f}" cy="{hc[1]:.1f}" rx="{7.6 * s:.1f}" ry="{8.4 * s:.1f}" fill="#3A1C14"/>')

    hairL = K.Look(["#2A0E08", "#5A2412", "#8E4422", "#C07040", "#E8A468", "#FFD8A0"], key=(-0.8, -0.5, 0.45), amb=0.05, wrap=0.35,
                   rim=("#F0E8FF", (-0.9, -0.4), 0.7), jit=0.03)
    mass = T([(-8, -78), (0, -80), (8, -77), (11, -68), (10, -58), (9, -46), (12, -34), (10, -22), (6, -14), (3, -6), (-2, -9), (-6, -3), (-11, -9),
              (-16, -6), (-19, -13), (-24, -12), (-23, -20), (-27, -26), (-24, -32), (-27, -40), (-23, -46), (-24, -54), (-18, -62), (-13, -72)])
    out.append(K.paint(D, mass, hairL, 3711, round_r=7 * s, flow=lambda x, y, n: 98 + 12 * math.sin(y * 0.05), flow_jit=8, edge_col="#1A0804", edge_w=1.2,
                       rim_col="#F0E8FF", rim_w=1.4, rim_op=0.6, passes=((80, (16, 34), (2, 4), (0.35, 0.6)), (300, (10, 24), (0.8, 1.6), (0.4, 0.8)))))
    # wavy strands over the mass and a few loose locks lifting off to the left in the sea wind
    for k in range(16):
        x0 = -12 + k * 1.4
        pts = T([(x0, -77 + abs(k - 8) * 0.4), (x0 - 1 + math.sin(k) * 2.4, -60), (x0 - 3 + math.sin(k * 1.7) * 3.2, -44), (x0 - 4 + math.sin(k * 0.9) * 3, -28), (x0 - 7, -12)])
        out.append(K.taper(pts, 2.2, 0.4, ["#FFD8A0", "#5A2412", "#C07040", "#3A1408"][k % 4], 0.5))
    # a string of pearls in her hair
    for k in range(7):
        p = T([(-6 + k * 2, -74 + abs(k - 3) * 0.8)])[0]
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1.6" fill="#F8F4FF" stroke="#8A8AA8" stroke-width="0.4"/>')
    art = D.render(out)
    DL = K.Doc("lmdL")
    L = [K.halo(DL, 300, 76, 240, "#04061A", 0.55, ry=38)]
    L.append(K.title(DL, 300, 86, "The Little Mermaid", SERIF_IT, 48, max_w=440, face=("#FFFFFF", "#D8E4F8", "#8A9ACC"), shadow="#000010", sop=0.8))
    L.append(K.subtitle(300, 110, "HANS CHRISTIAN ANDERSEN · 1837", CINZEL, 14, "#C8D4F0", ls=2.5, max_w=360, sh="#000010", sop=0.7))
    return art, DL.render(L)
# ---- end plate: the-little-mermaid ----


#@@PLATES@@


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        body = fn()
        if slug in VARNISH:
            v = VARNISH[slug]
            body = painterly(body, seed=v["seed"], edge=v["edge"], bristle=v["bristle"], grain=v["grain"], freq=v["freq"],
                             prefix=f"ft{slug.replace('-', '')}")
            # the second (text-only) copy never shows its shapes: drop them so the file is not twice as big
            k = body.index('aria-hidden="true">')
            ink_copy = re.sub(r"<(path|circle|ellipse|rect|polygon|polyline|line|stop)\b[^>]*/>", "", body[k:])
            ink_copy = re.sub(r"<(linearGradient|radialGradient|pattern|filter)\b[^>]*>.*?</\1>", "", ink_copy, flags=re.S)
            ink_copy = re.sub(r"<g[^>]*>(\s*)</g>", "", ink_copy)
            ink_copy = re.sub(r"<g[^>]*>(\s*)</g>", "", ink_copy)
            body = body[:k] + ink_copy
        body = re.sub(r"(\d)\.0(?=[^\d])", r"\1", body)        # 12.0 -> 12: smaller files
        if len(body) > 1_400_000:
            # very dense paintings: brush-stroke coordinates to whole pixels (invisible under the painterly filter)
            body = re.sub(r' d="([^"]*)"', lambda m: ' d="' + re.sub(r"-?\d+\.\d+", lambda n: str(round(float(n.group(0)))), m.group(1)) + '"', body)
        save(COL, slug, body)
    if not only:
        # the folder holds exactly this set: clear out artwork for slugs that were dropped
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
