"""Horror Classics, hand-painted edition: 30 magnets for the grown-up, spooky side of the season.

The great tales of terror and the old folklore monsters, each painted like a hand-painted 1920s-50s pulp cover,
a vintage (generic) movie poster, a Victorian penny dreadful or a gothic book plate: moonlight, fog, candle glow,
deep shadows and dramatic lettering. Dread, never gore: nothing that would upset a family kitchen.

Everything comes from the original public-domain books, plays, the 1922 silent film Nosferatu, the 1925 Phantom
and folklore (Stoker, Shelley, Poe, Irving, Stevenson, Wilde, Wells, Conan Doyle, Jacobs, James, Leroux,
Lovecraft's 1928 story, Dickens, Shakespeare), never from a modern film design: no studio makeup, no film
monsters, no modern horror characters.

Painted in the house gouache idiom (layered washes with pooled edges, brush strokes following the form, soft
glows, grain on top). Colour story: midnight blue, sickly absinthe green, blood red, bone and sepia, with candle
and lantern gold as the warm accent.

Run from tools/designs:  python3 horror_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from poster import ANTON
from fall_gouache_a import (bbox, cast, finish, grass, hill, label, letters, mix, painted, pline, ridge, shift, sky,
                            soft_glow, specks, taper, catmull, mist, glow_window, smoke)
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
import holidays_gouache as hg
from storybook_classics_painted import T, ell_pts, pd, tx, gilt, gilt_fill, stars_field, flourish, fleuron, bat, candle, skull, lightning
from fairy_tales_painted import Doc2, aurora, swell, arch_pts, bare_tree, gnarled_trunk, snowfall, tiny_cloak_figure
from mythology_painted import moon, poly, sharp, horse, robed_figure, raven_flying

COL = "horror"
INK = "#1A0E0A"

lt, dk = hg.lt, hg.dk

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def fin(D, out, seed, color="#000000", op=0.55):
    return finish(D, out, seed, color, op)


# ================================================================ toolkit: lettering
def _fit(s, font, size, max_w, ls):
    return fit_size(s, font, size, max_w, ls)


def _t(x, y, s, font, fs, fill, ls=0, anchor="middle", extra=""):
    lsa = f' letter-spacing="{ls}"' if ls else ""
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    return f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def block(D, x, y, s, font, size, face, side, depth=8, ang=(0.55, 1.0), ls=0, max_w=460, face2=None, line=None, line_w=2.0,
          hi=None, shadow=None, anchor="middle"):
    """Vintage poster block lettering: an extruded side built from stacked offsets, a graded face, an optional
    keyline around the face and a thin highlight along the top edge."""
    fs = _fit(s, font, size, max_w, ls)
    out = []
    if shadow:
        out.append(_t(x + ang[0] * (depth + 5), y + ang[1] * (depth + 5), s, font, fs, shadow, ls, anchor, ' opacity="0.45"'))
    for i in range(depth, 0, -1):
        out.append(_t(x + ang[0] * i, y + ang[1] * i, s, font, fs, side if i > 1 else dk(side, 0.25), ls, anchor))
    g = D.lin([(0, face), (1, face2 or face)], 0, y - fs * 0.75, 0, y, "userSpaceOnUse") if face2 else face
    if line:
        out.append(_t(x, y, s, font, fs, "none", ls, anchor, f' stroke="{line}" stroke-width="{line_w * 2}" stroke-linejoin="round"'))
    out.append(_t(x, y, s, font, fs, g, ls, anchor))
    if hi:
        out.append(_t(x - 0.6, y - fs * 0.012 - 0.6, s, font, fs, "none", ls, anchor, f' stroke="{hi}" stroke-width="0.9" opacity="0.55"'))
    return "".join(out)


def glow_text(D, x, y, s, font, size, fill, glow, ls=0, max_w=460, strength=1.0, anchor="middle", widths=(18, 10, 5), shadow=None):
    """Lettering that seems to give off light: soft stroked haloes under a bright face."""
    fs = _fit(s, font, size, max_w, ls)
    out = []
    if shadow:
        out.append(_t(x + fs * 0.02, y + fs * 0.04, s, font, fs, shadow, ls, anchor, ' opacity="0.6"'))
    for w, op in zip(widths, (0.08, 0.16, 0.3)):
        out.append(_t(x, y, s, font, fs, glow, ls, anchor, f' stroke="{glow}" stroke-width="{w}" stroke-linejoin="round" opacity="{op * strength:.2f}"'))
    out.append(_t(x, y, s, font, fs, fill, ls, anchor))
    return "".join(out)


DRIP_AT = {**{c: (0.24,) for c in "BDEFHKLMNPR"}, **{c: (0.5,) for c in "CGOQSUTYJVIZX"}, "A": (0.2, 0.8), "W": (0.3,), "H": (0.24, 0.76),
           "M": (0.2, 0.8), "N": (0.22, 0.78), "U": (0.5,), "L": (0.25, 0.7)}


def drip_text(D, x, y, s, font, size, stops, seed, ls=0, max_w=460, drip_len=(10, 46), every=0.75, outline=None, shadow=None, hi="#FFFFFF"):
    """Slow, heavy drips hanging from the letters (paint, wax or sea water): each drip leaves the foot of a stem with
    a little meniscus, thins, and ends in a round bead; one gradient runs through letters and drips together."""
    fs = _fit(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    rnd = random.Random(seed)
    g = D.lin(stops, 0, y - fs * 0.75, 0, y + drip_len[1] + 10, "userSpaceOnUse")
    gx = x - W / 2
    drips = []
    for ch in s:
        adv = measure(ch, font, fs)
        if ch != " ":
            for f in DRIP_AT.get(ch.upper(), (0.5,)):
                if rnd.random() < every:
                    cx = gx + adv * f + rnd.uniform(-1.5, 1.5)
                    L = rnd.uniform(*drip_len)
                    w = fs * rnd.uniform(0.07, 0.1)
                    drips.append((cx, L, w))
        gx += adv + ls
    out = []
    G = _t(x, y, s, font, fs, g, ls)
    dp = []
    for cx, L, w in drips:
        top = y - 3
        r = w * 0.62
        d = (f"M {cx - w * 0.95:.1f} {top:.1f} Q {cx - w * 0.45:.1f} {top + 2:.1f} {cx - w * 0.42:.1f} {top + L * 0.45:.1f} "
             f"L {cx - r * 0.85:.1f} {top + L:.1f} A {r:.1f} {r:.1f} 0 1 0 {cx + r * 0.85:.1f} {top + L:.1f} "
             f"L {cx + w * 0.42:.1f} {top + L * 0.45:.1f} Q {cx + w * 0.45:.1f} {top + 2:.1f} {cx + w * 0.95:.1f} {top:.1f} Z")
        dp.append((d, cx, top, L, w, r))
    if shadow:
        sh = "".join(f'<path d="{d}" fill="{shadow}" transform="translate(2.5 3.5)" opacity="0.55"/>' for d, *_ in dp)
        out.append(sh + _t(x + 2.5, y + 3.5, s, font, fs, shadow, ls, extra=' opacity="0.55"'))
    if outline:
        out.append(_t(x, y, s, font, fs, "none", ls, extra=f' stroke="{outline}" stroke-width="5" stroke-linejoin="round"'))
        out.append("".join(f'<path d="{d}" fill="none" stroke="{outline}" stroke-width="5" stroke-linejoin="round"/>' for d, *_ in dp))
    out.append(G)
    for d, cx, top, L, w, r in dp:
        out.append(f'<path d="{d}" fill="{g}"/>')
        out.append(f'<path d="M {cx - w * 0.25:.1f} {top + 6:.1f} L {cx - w * 0.22:.1f} {top + L * 0.8:.1f}" stroke="{hi}" stroke-width="{max(1.2, w * 0.16):.1f}" stroke-linecap="round" opacity="0.35"/>')
        out.append(f'<circle cx="{cx - r * 0.35:.1f}" cy="{top + L - r * 0.25:.1f}" r="{max(1.0, r * 0.25):.1f}" fill="{hi}" opacity="0.55"/>')
    return "".join(out)


def spaced(x, y, s, font, size, fill, ls=3, max_w=440, op=None, shadow=None):
    out = []
    if shadow:
        out.append(tx(x + 1.2, y + 1.6, s, font, size, shadow, ls=ls, max_w=max_w, op=0.7))
    out.append(tx(x, y, s, font, size, fill, ls=ls, max_w=max_w, op=op))
    return "".join(out)


def rule_line(x0, x1, y, col, w=1.8, op=0.9, diamond=True):
    out = [f'<path d="M {x0:.1f} {y:.1f} L {x1:.1f} {y:.1f}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>']
    if diamond:
        for xx in (x0, x1):
            out.append(f'<path d="M {xx - 4:.1f} {y:.1f} L {xx:.1f} {y - 4:.1f} L {xx + 4:.1f} {y:.1f} L {xx:.1f} {y + 4:.1f} Z" fill="{col}" opacity="{op}"/>')
    return "".join(out)


def sub_rule(x, y, s, font, size, fill, ls=3, gap=12, line_w=40, max_w=400, line=None):
    """Small caps line flanked by two short rules with diamond ends."""
    fs = _fit(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    mid = y - fs * 0.34
    lc = line or fill
    return (tx(x, y, s, font, fs, fill, ls=ls, max_w=max_w) + rule_line(x - W / 2 - gap - line_w, x - W / 2 - gap, mid, lc, 1.6)
            + rule_line(x + W / 2 + gap, x + W / 2 + gap + line_w, mid, lc, 1.6))


# ================================================================ toolkit: scenery
def night(D, stops, seed, n=70, cols=None):
    return sky(D, stops, seed, 600, cols or [stops[0][1], stops[-1][1], lt(stops[len(stops) // 2][1], 0.15)], n)


def fog(D, y, h, seed, col="#C8D4E0", op=0.5, x0=-40, x1=640):
    return mist(D, y, h, seed, col, op, x0, x1)


def vignette(D, col="#000000", op=0.6, r=0.75):
    g = D.rad([(0, col, 0), (r, col, 0), (1, col, op)], 0.5, 0.5, 0.72)
    return f'<rect width="600" height="600" fill="{g}"/>'


def band(D, y0, y1, col, op0, op1):
    g = D.lin([(0, col, op0), (1, col, op1)], 0, y0, 0, y1, "userSpaceOnUse")
    return f'<rect x="-10" y="{y0}" width="620" height="{y1 - y0}" fill="{g}"/>'


def flame_lick(cx, base, h, w, seed, cols=("#FF8A2A", "#FFD27A", "#FFF6D0")):
    """A candle / torch flame: three nested teardrops with a little sway."""
    rnd = random.Random(seed)
    sway = rnd.uniform(-0.25, 0.25) * w
    out = []
    for k, c in enumerate(cols):
        hh, ww = h * (1 - 0.28 * k), w * (1 - 0.3 * k)
        top = (cx + sway * (1 - 0.3 * k), base - hh)
        out.append(f'<path d="M {top[0]:.1f} {top[1]:.1f} C {cx + ww * 0.7:.1f} {base - hh * 0.45:.1f} {cx + ww * 0.6:.1f} {base:.1f} {cx:.1f} {base:.1f} '
                   f'C {cx - ww * 0.6:.1f} {base:.1f} {cx - ww * 0.7:.1f} {base - hh * 0.45:.1f} {top[0]:.1f} {top[1]:.1f} Z" fill="{c}"/>')
    return "".join(out)


def tentacle(D, pts, w0, w1, pal, seed, suckers=True, side=1, rim=None):
    """A great tentacle: tapered painted body, darker underside, pale sucker discs along the inner curve."""
    path = catmull(pts, 8)
    n = len(path)
    left, right = [], []
    for i, (x, y) in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * (i / (n - 1)) ** 0.8) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    outline = left + right[::-1]
    out = [painted(D, outline, pal, seed, sdir=(0.6, 0.4), sk=0.18, angle=-70, n=60, inkw=1.4, inkc="#020806", hi=0.35)]
    # underside band
    under = (right if side > 0 else left)
    mid = [((x1 + x2) / 2, (y1 + y2) / 2) for (x1, y1), (x2, y2) in zip(left, right)]
    band_pts = [((u[0] * 0.55 + m[0] * 0.45), (u[1] * 0.55 + m[1] * 0.45)) for u, m in zip(under, mid)]
    out.append(f'<path d="{smooth_closed(under + band_pts[::-1])}" fill="{pal[0]}" opacity="0.35"/>')
    if suckers:
        for i in range(2, n - 3, 3):
            t = i / (n - 1)
            w = (w0 + (w1 - w0) * t ** 0.8) / 2
            ux, uy = under[i]
            mx, my = mid[i]
            sx, sy = ux * 0.62 + mx * 0.38, uy * 0.62 + my * 0.38
            r = max(1.6, w * 0.32)
            a = math.degrees(math.atan2(uy - my, ux - mx))
            out.append(f'<path d="{blob(sx, sy, r, r * 0.7, seed + i, 0.08, 10, a)}" fill="{lt(pal[0], 0.35)}" opacity="0.9"/>')
            out.append(f'<path d="{blob(sx, sy, r * 0.5, r * 0.32, seed + i + 1, 0.08, 8, a)}" fill="{pal[2]}" opacity="0.7"/>')
    if rim:
        out.append(taper(left[1:-2], 2.2, 1, rim, 0.6))
    return "".join(out)


def stone_courses(lines_y, x_edge_fn, x1, col, w=1.4, op=0.5, seed=1, joints=True, unit=40):
    """Masonry courses: horizontal joints and staggered vertical joints between x_edge_fn(y) and x1."""
    rnd = random.Random(seed)
    out = []
    for i, y in enumerate(lines_y):
        xa = x_edge_fn(y)
        out.append(f'<path d="M {xa:.1f} {y:.1f} L {x1:.1f} {y + rnd.uniform(-1, 1):.1f}" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
        if joints and i + 1 < len(lines_y):
            y2 = lines_y[i + 1]
            h = abs(y2 - y)
            xx = xa + (i % 2) * unit * 0.5 + rnd.uniform(4, unit * 0.6)
            while xx < x1:
                out.append(f'<path d="M {xx:.1f} {y:.1f} L {xx + rnd.uniform(-1, 1):.1f} {y2:.1f}" stroke="{col}" stroke-width="{w * 0.9:.1f}" opacity="{op * 0.85:.2f}"/>')
                xx += unit * rnd.uniform(0.8, 1.25) * (h / 30 if h < 30 else 1)
    return "".join(out)


def rain(seed, n, col="#C8D0F0", op=(0.12, 0.35), ang=-7, L=22, box=(-40, 0, 640, 600)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<path d="M {rnd.uniform(x0, x1):.1f} {rnd.uniform(y0, y1):.1f} l {ang:.1f} {L}" stroke="{col}" stroke-width="1.2" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))


def crooked_tree(x, base, h, seed, col, w=10, lean=0.0, spread=40, depth=5):
    """A dead, crooked tree for horror skylines: knobbly forks and hooked twig tips."""
    rnd = random.Random(seed)
    out = []

    def br(px, py, ang, L, ww, d):
        pts = [(px, py)]
        a = ang
        for k in range(3):
            a += rnd.uniform(-22, 22)
            px += math.cos(math.radians(a)) * L / 3
            py += math.sin(math.radians(a)) * L / 3
            pts.append((px, py))
        out.append(taper(pts, ww, ww * 0.55, col))
        if d > 0:
            for k in range(rnd.choice([2, 2, 3])):
                br(px, py, a + rnd.uniform(-spread, spread), L * rnd.uniform(0.6, 0.8), ww * 0.6, d - 1)
        else:
            hook = a + rnd.choice([-1, 1]) * 50
            out.append(taper([(px, py), (px + math.cos(math.radians(hook)) * 6, py + math.sin(math.radians(hook)) * 6)], ww * 0.5, 0.6, col))
    out.append(taper([(x - w * 1.2, base + 2), (x - w * 0.3, base - h * 0.1), (x, base - h * 0.2)], w * 0.7, w * 0.5, col))
    out.append(taper([(x + w * 1.3, base + 2), (x + w * 0.3, base - h * 0.1), (x, base - h * 0.2)], w * 0.7, w * 0.5, col))
    br(x, base, -90 + lean, h * 0.34, w, depth)
    return "".join(out)


def cloaked(x, base, s, col, rim=None, flip=False, hood=True, arm=None, hem=0.0):
    """A tall cloaked figure standing (about 120*s tall), seen in silhouette; optional lantern arm."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-6, -104), (-16, -98), (-22, -84), (-24, -60), (-28, -30), (-34, 0), (-10, 2), (8, 1), (30 + hem * 20, 0), (24, -30),
                   (20, -62), (20, -86), (14, -98), (6, -104)]), col)]
    if hood:
        out.append(poly(L([(-11, -100), (-14, -114), (-8, -124), (2, -126), (11, -120), (13, -108), (9, -98)]), col))
    else:
        out.append(f'<path d="{blob(*L([(0, -112)])[0], 9 * s, 11 * s, 3, 0.06, 12)}" fill="{col}"/>')
    if arm == "lantern":
        out.append(taper(L([(16, -88), (28, -70), (34, -56)]), 8 * s, 6 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(-8, -124), (-14, -114), (-11, -100), (-20, -90), (-24, -60), (-28, -30), (-33, -2)])), rim, 1.6, 3, 1, 0.75))
    return "".join(out)


def tombstone(D, x, base, w, h, seed, kind="round", pal=("#A8AEB8", "#6A707C", "#2A2E36"), lean=0, moss=True, sdir=(0.6, 0.3)):
    if kind == "round":
        pts = arch_pts(x - w / 2, x + w / 2, base - h + w / 2, base, step=8)
    elif kind == "cross":
        a, b = w * 0.17, h
        pts = [(x - a, base), (x - a, base - b * 0.62), (x - w / 2, base - b * 0.62), (x - w / 2, base - b * 0.78), (x - a, base - b * 0.78),
               (x - a, base - b), (x + a, base - b), (x + a, base - b * 0.78), (x + w / 2, base - b * 0.78), (x + w / 2, base - b * 0.62),
               (x + a, base - b * 0.62), (x + a, base)]
        pts = poly_pts(pts, 8, seed, 0.6)
    else:
        pts = poly_pts([(x - w / 2, base), (x - w / 2, base - h * 0.8), (x, base - h), (x + w / 2, base - h * 0.8), (x + w / 2, base)], 8, seed, 0.6)
    pts = rot(pts, x, base, lean)
    out = [painted(D, pts, pal, seed, sdir=sdir, sk=0.2, angle=-90, n=20, inkw=1.4, inkc="#0A0A10", hi=0.45)]
    if moss:
        rnd = random.Random(seed)
        for k in range(5):
            out.append(f'<path d="{blob(x + rnd.uniform(-w / 2, w / 2) * 0.8, base - rnd.uniform(0, h * 0.3), rnd.uniform(3, 7), rnd.uniform(2, 4), seed + k, 0.3, 8)}" fill="#4A5A3A" opacity="0.6"/>')
    return "".join(out)


def gothic_window(D, x0, x1, spring, bottom, seed, glass=("#FFF2B8", "#FFD068", "#E8963A"), frame="#1A0E0A", point=0.6, mullion=True,
                  glow=None, glow_r=None):
    pts = arch_pts(x0, x1, spring, bottom, 6, "pointed", point)
    out = []
    if glow:
        out.append(soft_glow(D, (x0 + x1) / 2, (spring + bottom) / 2, glow_r or (x1 - x0) * 2, glow, 0.5))
    out.append(painted(D, pts, glass, seed, sdir=(0, 1), sk=0.12, angle=-90, n=8, inkw=0, hi=0.5, hik=0.12))
    if mullion:
        cx = (x0 + x1) / 2
        out.append(pline([(cx, spring - (x1 - x0) * 0.4), (cx, bottom)], frame, max(1.6, (x1 - x0) * 0.08), seed, 1, 1))
        out.append(pline([(x0, (spring + bottom) / 2), (x1, (spring + bottom) / 2)], frame, max(1.4, (x1 - x0) * 0.06), seed + 1, 1, 1))
    out.append(ink(smooth_closed(pts), frame, max(1.6, (x1 - x0) * 0.1), seed + 2, 2, 0.95))
    return "".join(out)


def lit_slit(D, x, y, w, h, col="#FFC860", glow=True):
    pts = arch_pts(x - w / 2, x + w / 2, y + w / 2, y + h, 4)
    out = []
    if glow:
        out.append(soft_glow(D, x, y + h / 2, max(w, h) * 1.6, col, 0.45))
    out.append(f'<path d="{smooth_closed(pts)}" fill="{col}"/>')
    return "".join(out)


# ================================================================ 1. dracula — face down, crawling down the castle wall
def count_crawling(D, x, y, s, seed, col="#05040A", cape=("#3A2A48", "#1A1224", "#06040A"), rim="#B8C8F0"):
    """The Count, head-first down the wall like a lizard: elbows and knees splayed, the cloak spreading out around
    him like great scalloped wings. (x, y) = chest; the head is lowest."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    # the cloak: a scalloped bat-wing cape spread flat against the stones (open around the head)
    pts = [(-14, 30)]
    for i, a in enumerate(range(118, 424, 12)):
        r = 1.0 if i % 2 == 0 else 0.84
        pts.append((math.cos(math.radians(a)) * 104 * r, -24 + math.sin(math.radians(a)) * 92 * r))
    pts.append((14, 30))
    cp = L(pts)
    out.append(painted(D, cp, cape, seed, sdir=(0.4, 0.4), sk=0.12, angle=-90, n=40, inkw=1.4, inkc="#000000", hi=0.3))
    for i, a in enumerate(range(118, 424, 24)):
        ex, ey = math.cos(math.radians(a)) * 100, -24 + math.sin(math.radians(a)) * 88
        out.append(pline(L([(0, -10), (ex * 0.5, ey * 0.5 - 6), (ex, ey)]), cape[2], 2.0, seed + i, 0.8, 1))
        out.append(pline(L([(2, -12), (ex * 0.5 + 3, ey * 0.5 - 8), (ex + 2, ey - 2)]), cape[0], 1.2, seed + i, 0.4, 1))
    out.append(ink(smooth_open(cp[1:9]), rim, 1.8, seed, 1, 0.75))
    # legs splayed up the wall, feet uppermost
    for sg in (-1, 1):
        out.append(taper(catmull(L([(sg * 8, -40), (sg * 34, -60), (sg * 40, -96)]), 6), 13 * s, 9 * s, col))
        out.append(poly(L([(sg * 40 - 7, -94), (sg * 40 + 7, -94), (sg * 42 + 5, -110), (sg * 40 - 4, -112)]), col))
    # torso
    out.append(poly(L([(-15, 26), (-17, 0), (-12, -34), (-6, -46), (6, -46), (12, -34), (17, 0), (15, 26)]), col))
    # arms splayed down like a lizard's, long pale fingers gripping the joints of the stones
    for sg in (-1, 1):
        sh, el, hd = (sg * 14, 20), (sg * 48, 26), (sg * 58, 62)
        out.append(taper(catmull(L([sh, el, hd]), 6), 11 * s, 7 * s, col))
        hx, hy = L([hd])[0]
        out.append(f'<path d="{blob(hx, hy, 5.5 * s, 4.5 * s, seed + 3 + sg, 0.1, 8)}" fill="#E2DCD0"/>')
        for f in range(4):
            fa = math.radians(90 + sg * 10 + (f - 1.5) * 22)
            out.append(taper([(hx, hy), (hx + math.cos(fa) * 8 * s, hy + math.sin(fa) * 8 * s), (hx + math.cos(fa - sg * 0.5) * 13 * s, hy + math.sin(fa - sg * 0.5) * 13 * s)],
                             2.6 * s, 1.1 * s, "#E2DCD0"))
    # the head, lowest of all, turned to look down into the abyss: pale profile, white hair and moustache
    hx, hy = L([(0, 44)])[0]
    out.append(f'<path d="{blob(hx, hy, 12 * s, 14 * s, seed, 0.06, 12)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-12, 40), (-8, 52), (-10, 58), (-4, 62), (2, 56), (0, 46), (-4, 38)]))}" fill="#D8D0C4"/>')
    out.append(f'<path d="{smooth_closed(L([(-6, 54), (-12, 58), (-2, 58)]))}" fill="#F2F0EC"/>')
    out.append(f'<path d="{blob(*L([(4, 34)])[0], 10 * s, 5 * s, seed + 1, 0.25, 10)}" fill="#E8E6E2"/>')
    out.append(f'<circle cx="{L([(-5, 47)])[0][0]:.1f}" cy="{L([(-5, 47)])[0][1]:.1f}" r="{1.4 * s:.1f}" fill="#C8201A"/>')
    if rim:
        for sg in (-1, 1):
            out.append(ink(smooth_open(L([(sg * 14, 16), (sg * 46, 21), (sg * 55, 56)])), rim, 1.4, seed + sg, 1, 0.75))
            out.append(ink(smooth_open(L([(sg * 10, -44), (sg * 33, -64), (sg * 37, -96)])), rim, 1.3, seed + sg + 4, 1, 0.65))
        out.append(ink(smooth_open(L([(-17, 0), (-12, -34), (-6, -46)])), rim, 1.3, seed + 9, 1, 0.6))
    return "".join(out)


@design("dracula")
def dracula():
    D = Doc2("hr-dr")
    out = [night(D, [(0, "#05060E"), (0.45, "#141A34"), (0.8, "#2A2E4A"), (1, "#3A3450")], 1)]
    out.append(stars_field(2, (0, 0, 300, 420), 90))
    out.append(moon(D, 150, 300, 56, 3, pal=("#FFFBEA", "#EDE6CC", "#BDB394"), glow="#E8ECFF", gs=0.5, glow_r=3.4))
    # far Carpathian peaks and the forest abyss in fog
    out.append(hill(D, ridge([(-20, 470), (40, 420), (90, 446), (150, 396), (210, 440), (260, 410), (330, 460)], 4, 9, 4), 640,
                    ("#5A6080", "#343A58", "#1A1E34"), 2, inkw=0, n=30, lit="#C8D0F0"))
    out.append(fog(D, 470, 70, 3, "#9AA4C8", 0.55, -40, 340))
    out.append(hill(D, ridge([(-20, 520), (60, 500), (140, 512), (220, 496), (320, 516)], 5, 6, 4), 640, ("#2A2E44", "#161A2A", "#06080E"), 3, inkw=0, n=20))
    rnd = random.Random(4)
    for k in range(26):
        xx = rnd.uniform(-10, 330)
        from paint import conifer
        out.append(conifer(xx, 530 + rnd.uniform(0, 30), rnd.uniform(26, 50), "#07080E", rnd.random()))
    out.append(fog(D, 560, 60, 4, "#7A84A8", 0.4, -40, 360))
    # the castle wall, seen from the window ledge looking down its face: edge leaning in toward the top
    def edge(y):
        return 262 + (y / 600) * 74
    wall = [(edge(-20), -20), (640, -20), (640, 640), (edge(640), 640)]
    out.append(painted(D, wall, ("#6A6E84", "#3E4052", "#16161E"), 5, sdir=(1, 0.2), sk=0.06, angle=-90, n=140, inkw=0, hi=0, hik=0.04))
    g = D.lin([(0, "#000000", 0.05), (1, "#000000", 0.6)], 0, 0, 1, 0)
    out.append(f'<path d="{pd(wall)}" fill="{g}"/>')
    ys = [-10 + 30 * i + i * i * 0.4 for i in range(22)]
    cid = D.clip(f'<path d="{pd(wall)}"/>')
    out.append(f'<g {cid}>{stone_courses(ys, lambda y: edge(y), 640, "#0E0E16", 2.0, 0.6, 6, unit=46)}'
               f'{stone_courses([y + 2.5 for y in ys], lambda y: edge(y), 640, "#A8ACC0", 1, 0.22, 6, joints=False)}'
               f'{strokes(D.nid(), pd(wall), (260, -20, 640, 640), ["#8A8EA4", "#1E1E2A", "#5A5E74"], 8, n=140, angle=-90, length=(20, 60), width=(2, 6), opacity=(0.1, 0.28))}</g>')
    # moonlit quoins down the corner of the tower
    for i in range(len(ys) - 1):
        y0, y1 = ys[i] + 1.5, ys[i + 1] - 1.5
        if y1 < -10 or y0 > 610:
            continue
        w0 = 26 if i % 2 == 0 else 15
        q = [(edge(y0), y0), (edge(y0) + w0, y0), (edge(y1) + w0, y1), (edge(y1), y1)]
        out.append(painted(D, poly_pts(q, 8, i, 0.6), ("#E2E6F8", "#9AA0BC", "#4A4E66"), 30 + i, sdir=(1, 0.4), sk=0.25, angle=-90, n=4, inkw=1, inkc="#14141E", hi=0.5))
    # the lit window above (Jonathan watching), its glow across the stones
    wx0, wx1, wy = 432, 482, 214
    out.append(soft_glow(D, 457, wy + 30, 110, "#FFB050", 0.45))
    out.append(f'<path d="{smooth_closed(arch_pts(wx0 - 8, wx1 + 8, wy + 16, wy + 70, 6, "pointed", 0.5))}" fill="#0E0A0C"/>')
    out.append(gothic_window(D, wx0, wx1, wy + 22, wy + 66, 7, frame="#16100C", point=0.5))
    out.append(painted(D, poly_pts([(wx0 - 14, wy + 66), (wx1 + 14, wy + 66), (wx1 + 14, wy + 76), (wx0 - 14, wy + 76)], 10, 2, 0.5), ("#9A9EB4", "#5A5E72", "#2A2C3A"), 6, sdir=(0, 1), sk=0.2, angle=0, n=6, inkw=1.2, inkc="#0A0A12", hi=0.4))
    out.append(cloaked(470, wy + 66, 0.34, "#140C0A", hood=False))
    # the Count
    out.append(count_crawling(D, 440, 402, 1.22, 9))
    # bats wheeling out of the dark
    for (bx, by, bs, fl, a) in ((224, 252, 1.0, 0.6, -10), (250, 300, 0.7, 0.1, 8), (96, 360, 0.8, 0.8, -4), (204, 372, 0.55, 0.3, 12), (110, 210, 0.5, 0.2, 0)):
        out.append(bat(bx, by, bs, "#0A0A12", fl, a))
    out.append(band(D, 0, 200, "#000000", 0.55, 0))
    # lettering
    out.append(block(D, 300, 142, "DRACULA", ANTON, 100, "#F4ECDA", "#7A0E16", depth=9, ang=(0.7, 1.0), ls=10, max_w=430, face2="#D8C8A8", shadow="#000000"))
    out.append(spaced(300, 178, "BRAM STOKER · 1897", CINZEL, 19, "#E8D8C0", ls=5, shadow="#000000"))
    out.append(letters(D, 300, 545, "“…his cloak spreading out like great wings.”", SERIF_IT, 26, "#F2E8D8", ["#FFFFFF", "#E8D8C8"], 11, max_w=470,
                       shadow="#000000", soff=(0.02, 0.06), angle=-40, wob=0.25))
    return fin(D, out, 12)


# ================================================================ 2. the headless horseman — over the bridge with his pumpkin
def jack_o_lantern(D, cx, cy, r, seed, glow=True):
    out = []
    if glow:
        out.append(soft_glow(D, cx, cy, r * 5, "#FF8A2A", 0.55))
        out.append(soft_glow(D, cx, cy, r * 2.2, "#FFD27A", 0.6))
    body = blob_pts(cx, cy, r * 1.12, r, seed, 0.04, 20)
    out.append(painted(D, body, ("#FFB060", "#E8701E", "#8A3008"), seed, sdir=(0.6, 0.6), sk=0.2, angle=-90, n=16, inkw=1.4, inkc="#3A1404", hi=0.35))
    for dx in (-0.45, 0, 0.45):
        out.append(pline([(cx + dx * r, cy - r * 0.9), (cx + dx * 1.3 * r, cy), (cx + dx * r, cy + r * 0.92)], "#8A3008", 1.2, seed, 0.6, 1))
    # carved face: slanted eyes and a jagged grin, lit from inside
    for sg in (-1, 1):
        out.append(sharp([(cx + sg * r * 0.18, cy - r * 0.12), (cx + sg * r * 0.62, cy - r * 0.34), (cx + sg * r * 0.5, cy - r * 0.02)], "#FFF2A0"))
    mouth = [(cx - r * 0.62, cy + r * 0.2), (cx - r * 0.4, cy + r * 0.3), (cx - r * 0.3, cy + r * 0.2), (cx - r * 0.15, cy + r * 0.34), (cx, cy + r * 0.22),
             (cx + r * 0.15, cy + r * 0.36), (cx + r * 0.3, cy + r * 0.22), (cx + r * 0.42, cy + r * 0.32), (cx + r * 0.62, cy + r * 0.18),
             (cx + r * 0.4, cy + r * 0.56), (cx, cy + r * 0.64), (cx - r * 0.4, cy + r * 0.56)]
    out.append(sharp(mouth, "#FFE27A"))
    out.append(taper([(cx - r * 0.05, cy - r * 0.95), (cx + r * 0.1, cy - r * 1.3), (cx + r * 0.3, cy - r * 1.4)], r * 0.22, r * 0.14, "#3A3014"))
    return "".join(out)


def headless_rider(D, x, y, s, seed, col="#06050A", rim="#FFB060"):
    """Headless rider in a high-collared coat, cloak streaming back, right arm hurling up the lantern. (x, y) = saddle."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    # cloak streaming back (to the left: the horse gallops right)
    cloak = [(-6, -66), (-30, -70), (-70, -78), (-112, -74), (-148, -86), (-124, -60), (-150, -52), (-112, -40), (-128, -24), (-80, -26), (-40, -10), (-10, -4)]
    out.append(painted(D, L(cloak), ("#3A2A3A", "#160E18", "#050208"), seed, sdir=(0.3, 0.8), sk=0.2, angle=180, n=26, inkw=1.2, inkc="#000000", hi=0.25))
    for k in range(3):
        out.append(pline(L([(-20, -60 + k * 16), (-70, -62 + k * 14), (-120, -66 + k * 12)]), "#3A2A40", 1.4, seed + k, 0.6, 1))
    # torso leaning forward, thigh and boot
    out.append(poly(L([(-14, 0), (-18, -30), (-14, -58), (-4, -72), (12, -74), (22, -64), (20, -30), (14, 0)]), col))
    out.append(taper(catmull(L([(0, -4), (22, 8), (26, 34), (18, 48)]), 5), 16 * s, 10 * s, col))
    out.append(poly(L([(10, 44), (30, 46), (32, 54), (12, 54)]), col))
    # the high collar standing open and empty where the head should be
    out.append(poly(L([(-8, -70), (-12, -88), (-2, -92), (14, -93), (26, -88), (22, -70)]), col))
    out.append(f'<path d="{smooth_closed(L([(-9, -88), (2, -95), (18, -96), (24, -89), (10, -86)]))}" fill="#2A0E0E"/>')
    out.append(ink(smooth_open(L([(-9, -88), (2, -95), (18, -96), (24, -89)])), rim or "#FFB060", 1.4, seed + 5, 1, 0.8))
    # the arm up with the pumpkin, left arm on the reins
    out.append(taper(catmull(L([(16, -66), (34, -86), (44, -112), (48, -128)]), 6), 11 * s, 8 * s, col))
    out.append(taper(catmull(L([(14, -50), (34, -36), (52, -26)]), 6), 10 * s, 7 * s, col))
    if rim:
        out.append(ink(smooth_open(L([(22, -88), (22, -70), (34, -86), (44, -112)])), rim, 1.8, seed, 1, 0.8))
        out.append(ink(smooth_open(L([(22, -64), (20, -30), (24, 6)])), rim, 1.6, seed + 1, 1, 0.65))
    return "".join(out)


@design("the-headless-horseman")
def the_headless_horseman():
    D = Doc2("hr-hh")
    out = [night(D, [(0, "#0A0816"), (0.4, "#2A1A30"), (0.72, "#6A3A34"), (1, "#2A1A20")], 1)]
    out.append(stars_field(3, (0, 0, 600, 260), 60))
    out.append(moon(D, 316, 318, 150, 5, pal=("#FFF0C0", "#F4C070", "#C88040"), glow="#FFB060", gs=0.5, glow_r=1.9))
    out.append(puff_cloud(D, 110, 236, 220, 4, ("#6A4A5A", "#3A2636", "#1A0E1A"), op=0.8))
    out.append(puff_cloud(D, 540, 420, 180, 5, ("#7A4A4A", "#3A2430", "#1A0E16"), op=0.6))
    # the old Dutch church on its knoll, far left: nave, belfry and spire
    out.append(hill(D, ridge([(-20, 424), (60, 400), (140, 408), (220, 432)], 3, 5, 3), 640, ("#3A2A3A", "#20141E", "#0A060A"), 2, inkw=0, n=10))
    out.append(poly([(60, 412), (60, 372), (84, 354), (132, 354), (132, 412)], "#0E0810"))
    out.append(sharp([(52, 376), (84, 350), (138, 350), (138, 356), (84, 356), (58, 380)], "#0E0810"))
    out.append(sharp([(72, 412), (72, 330), (96, 330), (96, 412)], "#0E0810"))
    out.append(sharp([(68, 332), (84, 274), (100, 332)], "#0E0810"))
    out.append(taper([(84, 276), (84, 258)], 1.6, 1.2, "#0E0810"))
    out.append(taper([(78, 264), (90, 264)], 1.4, 1.4, "#0E0810"))
    out.append(lit_slit(D, 84, 340, 6, 12, "#FFC060"))
    for wx in (108, 122):
        out.append(lit_slit(D, wx, 372, 6, 16, "#FFC060"))
    # trees framing: a great twisted tree at the right
    out.append(crooked_tree(560, 470, 380, 7, "#07050A", w=18, lean=-12, spread=42, depth=5))
    out.append(crooked_tree(30, 470, 260, 8, "#07050A", w=12, lean=10, spread=40, depth=4))
    # the brook and the wooden bridge
    out.append(sea(D, 470, 640, [(0, "#3A2430"), (0.5, "#1A1018"), (1, "#06040A")], 6, ["#6A3A3A", "#06040A", "#FFB060"], 60))
    out.append(f'<path d="{blob(330, 500, 90, 10, 3, 0.2, 14)}" fill="#FFC070" opacity="0.25"/>')
    out.append(wave_lines(7, (0, 480, 600, 600), ["#C8784A", "#FFC070", "#3A2430"], 50, (10, 30), 1.6, 2, (0.3, 0.6)))
    bridge_y = 456
    out.append(painted(D, poly_pts([(-20, bridge_y), (620, bridge_y), (620, bridge_y + 16), (-20, bridge_y + 16)], 20, 3, 0.5), ("#5A3A2A", "#2A1A14", "#0A0604"), 8, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.4, inkc="#000000", hi=0.3))
    for k in range(13):
        px = 10 + k * 50
        out.append(taper([(px, bridge_y + 14), (px + 1, bridge_y + 80)], 9, 8, "#0A0608"))
        out.append(taper([(px, bridge_y + 2), (px, bridge_y - 32)], 6, 5, "#0E080A"))
    out.append(taper([(-20, bridge_y - 30), (300, bridge_y - 33), (620, bridge_y - 30)], 5, 5, "#0E080A"))
    out.append(taper([(-20, bridge_y - 30), (300, bridge_y - 33), (620, bridge_y - 30)], 1.6, 1.6, "#FFB060", 0.5))
    # the horse at full gallop (facing right), the rider hurling his flaming head
    legs = [((-60, 46), (-98, 52), (-134, 36), (-14, 2), "far"), ((62, 44), (96, 58), (134, 62), (14, 4), "far"),
            ((-70, 50), (-104, 64), (-138, 58), (-14, 4), "near"), ((70, 48), (100, 66), (130, 82), (14, 6), "near")]
    hx, hy = 296, 352
    out.append(horse(D, hx, hy, 0.92, 8, ("#5A3A34", "#160C0E", "#040204"), legs, flip=True, mane="#100608", rim="#FFC070", dapple=False))
    out.append(headless_rider(D, hx - 12, hy - 20, 0.92, 9))
    out.append(jack_o_lantern(D, hx + 36, hy - 152, 26, 10))
    rnd = random.Random(11)
    for _ in range(30):
        a, r = rnd.uniform(-2.6, -0.6), rnd.uniform(26, 70)
        out.append(f'<circle cx="{hx + 34 + math.cos(a) * r - 20:.1f}" cy="{hy - 150 + math.sin(a) * r * 0.6 + 20:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFD08A" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    # flying leaves and a crow
    for k in range(10):
        lx, ly = rnd.uniform(60, 560), rnd.uniform(170, 440)
        out.append(f'<path d="{blob(lx, ly, rnd.uniform(3, 6), rnd.uniform(1.6, 3), k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8602A", "#8A3A1A", "#E89A3A"])}" opacity="0.9"/>')
    out.append(band(D, 520, 600, "#000000", 0, 0.7))
    # lettering
    out.append(block(D, 300, 110, "THE HEADLESS", BEBAS, 66, "#FFD27A", "#5A1A08", depth=6, ang=(0.6, 1.0), ls=6, max_w=440, face2="#F08A2A", shadow="#000000"))
    out.append(block(D, 300, 176, "HORSEMAN", BEBAS, 80, "#FFD27A", "#5A1A08", depth=7, ang=(0.6, 1.0), ls=10, max_w=440, face2="#E8701E", shadow="#000000"))
    out.append(sub_rule(300, 548, "WASHINGTON IRVING · 1820", CINZEL, 18, "#FFE2B0", ls=3, max_w=360, line="#FFB060"))
    return fin(D, out, 13)


# ================================================================ 3. the fall of the house of usher — the fissure and the blood-red moon
@design("the-fall-of-the-house-of-usher")
def the_fall_of_the_house_of_usher():
    D = Doc2("hr-us")
    out = [night(D, [(0, "#06080A"), (0.4, "#14201C"), (0.62, "#3A2A22"), (0.7, "#2A1E1C"), (1, "#0A0C0C")], 1)]
    out.append(puff_cloud(D, 130, 200, 260, 2, ("#3A3A34", "#1E201C", "#0A0C0A"), op=0.85))
    out.append(puff_cloud(D, 480, 180, 280, 3, ("#3A3632", "#1E1E1A", "#0A0A08"), op=0.85))
    # the blood-red moon, low, setting directly behind the house
    mx, my = 300, 300
    out.append(soft_glow(D, mx, my, 220, "#C8281A", 0.55))
    out.append(moon(D, mx, my, 74, 4, pal=("#FF8A60", "#D8402A", "#7A1410"), glow="#E8402A", gs=0.6, glow_r=2.2))
    # the house: a long, low gothic pile with two turrets; the fissure zigzags from roof to the tarn
    hb = 410
    body = [(120, hb), (120, 300), (160, 300), (160, 270), (200, 270), (200, 296), (400, 296), (400, 270), (440, 270), (440, 300), (480, 300), (480, hb)]
    roofs = [[(110, 304), (140, 250), (170, 304)], [(190, 272), (220, 218), (250, 272)], [(350, 272), (380, 218), (410, 272)], [(430, 304), (460, 250), (490, 304)],
             [(196, 300), (300, 248), (404, 300)]]
    house = [painted(D, poly_pts(body, 20, 4, 0.5), ("#5A5650", "#2E2C2A", "#0E0E0C"), 5, sdir=(0.7, 0.2), sk=0.12, angle=-90, n=90, inkw=1.6, inkc="#050504", hi=0.25)]
    for k, r_ in enumerate(roofs):
        house.append(painted(D, poly_pts(r_, 10, 5 + k, 0.4), ("#3A3634", "#1A1816", "#060504"), 6 + k, sdir=(0.7, 0.3), sk=0.15, angle=-60, n=12, inkw=1.4, inkc="#000000", hi=0.2))
    rnd = random.Random(6)
    # vacant, eye-like windows: most dark, two dimly lit
    for row, y in enumerate((320, 360)):
        for k in range(8):
            wx = 140 + k * 46 + (row % 2) * 6
            if abs(wx - 300) < 24:
                continue
            litw = (row, k) in ((0, 1), (1, 6))
            pts = arch_pts(wx - 7, wx + 7, y + 6, y + 26, 4)
            house.append(f'<path d="{smooth_closed(pts)}" fill="{"#E8B060" if litw else "#08090A"}"/>')
            if litw:
                house.append(soft_glow(D, wx, y + 16, 24, "#FFB050", 0.4))
            house.append(ink(smooth_closed(pts), "#7A7468", 1.2, k + row, 1, 0.5))
    # fungi / ivy streaks hanging from the eaves
    house.append(streaks_dark(D, (120, 296, 480, hb), 7))
    out.append("".join(house))
    # the fissure, glowing red: the moon shines through it
    fis = [(296, 252), (302, 276), (292, 300), (306, 330), (294, 362), (308, 388), (300, hb)]
    out.append(f'<path d="{pd([(x - 3 - 2 * (i % 2), y) for i, (x, y) in enumerate(fis)] + [(x + 3 + 2 * (i % 2), y) for i, (x, y) in enumerate(fis)][::-1])}" fill="#FF6A3A"/>')
    out.append(taper(fis, 2, 1, "#FFE0B0", 0.9))
    out.append(soft_glow(D, 300, 330, 40, "#FF5A2A", 0.4))
    # ground, sedge and dead trees on the banks
    out.append(hill(D, [(-20, 404), (120, 412), (300, 414), (480, 410), (620, 404)], 440, ("#2A2A22", "#141410", "#060604"), 7, inkw=0, n=10))
    out.append(crooked_tree(64, 416, 300, 8, "#050605", w=14, lean=8))
    out.append(crooked_tree(548, 416, 280, 9, "#050605", w=13, lean=-10))
    # the black tarn with the inverted house
    out.append(sea(D, 414, 640, [(0, "#1A1210"), (0.4, "#0A0806"), (1, "#020202")], 8, ["#2A1A16", "#000000", "#4A2A22"], 50))
    refl = []
    refl.append(f'<g transform="translate(0 {2 * 414}) scale(1 -1)" opacity="0.45">{"".join(house)}'
                f'<path d="{pd([(x - 3, y) for x, y in fis] + [(x + 3, y) for x, y in fis][::-1])}" fill="#FF6A3A"/></g>')
    cid = D.clip('<rect x="0" y="414" width="600" height="200"/>')
    out.append(f'<g {cid}>{"".join(refl)}</g>')
    out.append(f'<path d="{blob(300, 480, 70, 30, 2, 0.2, 14)}" fill="#E8402A" opacity="0.18"/>')
    out.append(wave_lines(9, (0, 420, 600, 560), ["#5A3A30", "#000000", "#C8503A"], 70, (16, 46), 1.6, 1.2, (0.3, 0.6)))
    for k in range(24):
        sx = rnd.choice([rnd.uniform(-10, 160), rnd.uniform(440, 610)])
        out.append(taper([(sx, 424), (sx + rnd.uniform(-6, 6), 424 - rnd.uniform(10, 26))], 2, 0.6, "#0A0A06"))
    out.append(fog(D, 418, 34, 10, "#8A9088", 0.35))
    out.append(band(D, 0, 170, "#000000", 0.55, 0))
    out.append(band(D, 500, 600, "#000000", 0, 0.7))
    # lettering: a gothic book-plate title
    out.append(tx(300, 92, "THE FALL OF THE", CINZEL, 26, "#C8B8A0", ls=8, max_w=360))
    out.append(gilt(D, 300, 150, "HOUSE OF USHER", CINZEL, 56, ls=5, max_w=470, seed=12, deboss="#000000", dop=0.85, pal="pale"))
    out.append(tx(300, 522, "“…the full, setting, and blood-red moon”", SERIF_IT, 24, "#F2C8B0", max_w=450))
    out.append(tx(300, 548, "EDGAR ALLAN POE · 1839", CINZEL, 16, "#B8A890", ls=4, max_w=300))
    return fin(D, out, 14)


def streaks_dark(D, box, seed):
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    out = []
    for _ in range(26):
        x = rnd.uniform(x0, x1)
        L = rnd.uniform(10, 60)
        out.append(taper([(x, y0 + 2), (x + rnd.uniform(-2, 2), y0 + L * 0.5), (x + rnd.uniform(-3, 3), y0 + L)], rnd.uniform(2, 5), 0.6, "#0A0C08", rnd.uniform(0.3, 0.7)))
    return "".join(out)


# ================================================================ 4. the masque of the red death — the ebony clock in the black room
def velvet_drape(D, x0, x1, top, bottom, seed, pal=("#2A2230", "#100C14", "#020104"), folds=6):
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bottom - top}" fill="{pal[1]}"/>']
    w = (x1 - x0) / folds
    for k in range(folds):
        fx = x0 + k * w + rnd.uniform(-4, 4)
        g = D.lin([(0, pal[2], 0.9), (0.35, pal[0], 0.55), (0.6, pal[1], 0.2), (1, pal[2], 0.8)], 0, 0, 1, 0)
        out.append(f'<path d="M {fx:.1f} {top} L {fx + w:.1f} {top} L {fx + w + rnd.uniform(-6, 6):.1f} {bottom} L {fx + rnd.uniform(-6, 6):.1f} {bottom} Z" fill="{g}"/>')
    return "".join(out)


def tall_clock(D, cx, base, w, h, seed, hand_m=-2, hand_h=0):
    """A gigantic ebony long-case clock: hood with a dial, waisted trunk with a brass pendulum, plinth."""
    out = [cast(D, cx + 20, base, w * 1.0, 14, "#000000", 0.6, seed)]
    eb = ("#4A3A3A", "#16100E", "#020101")
    plinth = poly_pts([(cx - w * 0.62, base), (cx - w * 0.62, base - h * 0.16), (cx + w * 0.62, base - h * 0.16), (cx + w * 0.62, base)], 14, seed, 0.4)
    trunk = poly_pts([(cx - w * 0.45, base - h * 0.16), (cx - w * 0.45, base - h * 0.62), (cx + w * 0.45, base - h * 0.62), (cx + w * 0.45, base - h * 0.16)], 14, seed + 1, 0.4)
    hood = poly_pts([(cx - w * 0.6, base - h * 0.62), (cx - w * 0.6, base - h * 0.92), (cx + w * 0.6, base - h * 0.92), (cx + w * 0.6, base - h * 0.62)], 14, seed + 2, 0.4)
    for k, p in enumerate((plinth, trunk, hood)):
        out.append(painted(D, p, eb, seed + k, sdir=(0.8, 0.2), sk=0.2, angle=-90, n=30, inkw=1.4, inkc="#000000", hi=0.4, hik=0.06))
    # broken pediment with a finial
    ped = [(cx - w * 0.68, base - h * 0.92), (cx - w * 0.1, base - h * 1.02), (cx - w * 0.1, base - h * 0.98), (cx - w * 0.5, base - h * 0.92)]
    out.append(poly(ped, "#0A0606"))
    out.append(poly([(cx + w * 0.68, base - h * 0.92), (cx + w * 0.1, base - h * 1.02), (cx + w * 0.1, base - h * 0.98), (cx + w * 0.5, base - h * 0.92)], "#0A0606"))
    out.append(f'<path d="{blob(cx, base - h * 1.0, 6, 9, seed, 0.1, 10)}" fill="#C8963A"/>')
    # red light catching the left edges
    for p in (trunk, hood, plinth):
        x0, y0, x1, y1 = bbox(p)
        out.append(taper([(x0 + 1.5, y0 + 3), (x0 + 1.5, y1 - 3)], 2, 2, "#E8503A", 0.3))
    # trunk door with a glass lenticle showing the swinging brass pendulum
    tx0, tx1, ty0, ty1 = cx - w * 0.3, cx + w * 0.3, base - h * 0.58, base - h * 0.2
    out.append(f'<rect x="{tx0:.1f}" y="{ty0:.1f}" width="{tx1 - tx0:.1f}" height="{ty1 - ty0:.1f}" rx="4" fill="#0A0606" stroke="#3A2A1A" stroke-width="2"/>')
    pcx = cx + 8
    out.append(f'<path d="M {cx:.1f} {ty0 + 4:.1f} L {pcx:.1f} {ty1 - 34:.1f}" stroke="#C8963A" stroke-width="2.4"/>')
    out.append(soft_glow(D, pcx, ty1 - 26, 30, "#FFC060", 0.35))
    out.append(painted(D, blob_pts(pcx, ty1 - 24, 14, 14, seed, 0.02, 20), ("#FFE7A0", "#C8963A", "#6A4A14"), seed + 5, sdir=(0.7, 0.6), sk=0.2, n=8, inkw=1.2, inkc="#2A1A06", hi=0.5))
    out.append(f'<path d="M {cx - 14:.1f} {ty1 - 50:.1f} A 40 40 0 0 0 {cx + 26:.1f} {ty1 - 48:.1f}" stroke="#FFC060" stroke-width="1.4" fill="none" opacity="0.35" stroke-dasharray="3 5"/>')
    # dial
    dy = base - h * 0.77
    R = w * 0.4
    out.append(f'<circle cx="{cx}" cy="{dy:.1f}" r="{R + 6:.1f}" fill="{gilt_fill(D, dy - R, dy + R)}"/>')
    out.append(painted(D, ell_pts(cx, dy, R, R, 0, 360, 30), ("#FFF8E8", "#EDE0C4", "#A89070"), seed + 6, sdir=(0.6, 0.6), sk=0.15, n=10, inkw=1.2, inkc="#3A2A1A", hi=0.4))
    for k in range(12):
        a = math.radians(-90 + k * 30)
        r1, r2 = R * 0.8, R * 0.94
        out.append(f'<path d="M {cx + math.cos(a) * r1:.1f} {dy + math.sin(a) * r1:.1f} L {cx + math.cos(a) * r2:.1f} {dy + math.sin(a) * r2:.1f}" stroke="#1A0E06" stroke-width="{3 if k % 3 == 0 else 1.6}"/>')
    am = math.radians(-90 + hand_m * 6)
    ah = math.radians(-90 + hand_h * 30 + hand_m * 0.5)
    out.append(taper([(cx, dy), (cx + math.cos(ah) * R * 0.52, dy + math.sin(ah) * R * 0.52)], 4, 1.6, "#1A0E06"))
    out.append(taper([(cx, dy), (cx + math.cos(am) * R * 0.78, dy + math.sin(am) * R * 0.78)], 3, 1.2, "#1A0E06"))
    out.append(f'<circle cx="{cx}" cy="{dy:.1f}" r="2.6" fill="#8A1A14"/>')
    return "".join(out)


def mask_on_floor(D, cx, cy, s, seed, pal=("#FFFFFF", "#E8E0D2", "#9A8E7A"), trim="#C8963A", ang=-14):
    def L(pts):
        return T(pts, cx, cy, s, False, ang)
    shape = L([(-46, -4), (-40, -16), (-22, -20), (-6, -12), (0, -10), (6, -12), (22, -20), (40, -16), (46, -4), (38, 10), (20, 14), (6, 6), (0, 4),
               (-6, 6), (-20, 14), (-38, 10)])
    out = [cast(D, cx + 6, cy + 14 * s, 50 * s, 8 * s, "#000000", 0.6, seed)]
    out.append(painted(D, shape, pal, seed, sdir=(0.7, 0.6), sk=0.2, angle=0, n=14, inkw=1.4, inkc="#2A1A10", hi=0.5))
    for sg in (-1, 1):
        out.append(f'<path d="{smooth_closed(L([(sg * 10, -6), (sg * 22, -12), (sg * 34, -8), (sg * 30, 2), (sg * 18, 4)]))}" fill="#0A0606"/>')
    out.append(ink(smooth_closed(shape), trim, 1.8, seed + 1, 1, 0.9))
    # silk ties and a fan of scarlet feathers at the temple
    out.append(taper(catmull(L([(46, -4), (66, 4), (80, 0), (96, 10)]), 5), 4, 1.4, "#8A1A1A"))
    for k, a in enumerate((-150, -128, -106, -84)):
        tip = (-38 + math.cos(math.radians(a)) * 58, -16 + math.sin(math.radians(a)) * 58)
        mid = ((-38 + tip[0]) / 2, (-16 + tip[1]) / 2)
        fp = L([(-38, -16), (mid[0] - 8, mid[1]), tip, (mid[0] + 8, mid[1])])
        out.append(painted(D, fp, ("#FF6A4A", "#C8201A", "#5A0606"), seed + 10 + k, sdir=(0.5, 0.5), sk=0.2, angle=a, n=10, inkw=0.9, inkc="#3A0404", hi=0.4))
        out.append(pline(L([(-38, -16), tip]), "#5A0606", 1.1, seed + k, 0.8, 1))
    out.append(f'<path d="{blob(*L([(-38, -16)])[0], 6 * s, 5 * s, seed, 0.1, 10)}" fill="#C8963A"/>')
    return "".join(out)


@design("the-masque-of-the-red-death")
def the_masque_of_the_red_death():
    D = Doc2("hr-mq")
    out = [f'<rect width="600" height="600" fill="#050304"/>']
    out.append(velvet_drape(D, -10, 610, -10, 470, 3))
    # the scarlet window of the seventh room, lit by a brazier beyond
    wx0, wx1, sp, bt = 70, 214, 284, 450
    out.append(soft_glow(D, 142, 330, 300, "#C81A14", 0.5))
    out.append(f'<path d="M {wx0 - 16} {bt} L {wx1 + 16} {bt} L {wx1 + 120} 610 L {wx0 - 60} 610 Z" fill="{D.lin([(0, "#E8201A", 0.35), (1, "#E8201A", 0)])}"/>')
    glass = arch_pts(wx0, wx1, sp, bt, 6, "pointed", 0.7)
    out.append(painted(D, poly_pts([(wx0 - 16, bt + 10), (wx0 - 16, sp - 40), (wx1 + 16, sp - 40), (wx1 + 16, bt + 10)], 20, 2, 0.4), ("#3A2020", "#140808", "#000000"), 4, sdir=(0.5, 0.5), sk=0.1, n=10, inkw=0, hi=0.2))
    out.append(f'<path d="{smooth_closed(arch_pts(wx0 - 10, wx1 + 10, sp, bt + 6, 6, "pointed", 0.7))}" fill="#1A0A08"/>')
    out.append(f'<path d="{smooth_closed(glass)}" fill="{D.rad([(0, "#FFB080"), (0.35, "#FF3A20"), (1, "#7A0606")], 0.5, 0.62, 0.7)}"/>')
    cid = D.clip(f'<path d="{smooth_closed(glass)}"/>')
    lead = []
    for k in range(1, 6):
        y = sp - 30 + k * 46
        lead.append(f'<path d="M {wx0} {y} L {wx1} {y}" stroke="#1A0606" stroke-width="3"/>')
    for k in range(1, 4):
        x = wx0 + k * (wx1 - wx0) / 4
        lead.append(f'<path d="M {x:.1f} {sp - 80} L {x:.1f} {bt}" stroke="#1A0606" stroke-width="3"/>')
    for k in range(10):
        lead.append(f'<path d="M {wx0 + k * 18} {sp - 80} L {wx0 + k * 18 - 60} {bt}" stroke="#1A0606" stroke-width="1.4" opacity="0.6"/>')
    # the brazier's flames seen through the glass
    lead.append(soft_glow(D, 142, 420, 70, "#FFE0A0", 0.6))
    out.append(f'<g {cid}>{"".join(lead)}</g>')
    out.append(ink(smooth_closed(glass), "#0A0202", 5, 3, 1, 1))
    out.append(taper([(wx0 + 4, sp + 10), (wx0 + 4, bt - 6)], 4, 4, "#FFB080", 0.3))
    # the black carpet floor, catching red light
    out.append(f'<path d="M -10 460 L 610 460 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#1A0A0A"), (1, "#050202")])}"/>')
    out.append(strokes(D.nid(), "M -10 460 L 610 460 L 610 610 L -10 610 Z", (-40, 460, 610, 610), ["#3A1414", "#000000", "#5A1A1A"], 4, n=60, angle=0, length=(40, 120), width=(2, 6), opacity=(0.15, 0.4)))
    out.append(f'<path d="M -10 460 L 610 460" stroke="#3A1A14" stroke-width="3"/>')
    # the clock against the west wall
    out.append(tall_clock(D, 414, 492, 116, 320, 5, hand_m=-1, hand_h=0))
    # a dropped mask on the black floor, the revel stopped
    out.append(mask_on_floor(D, 190, 500, 1.15, 6))
    rnd = random.Random(7)
    for _ in range(14):
        x, y = rnd.uniform(60, 560), rnd.uniform(480, 560)
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 4), rnd.uniform(1, 2), rnd.randint(0, 99), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8963A", "#E8402A", "#F2E8D8"])}" opacity="0.8"/>')
    out.append(vignette(D, "#000000", 0.7))
    # lettering
    out.append(tx(300, 92, "THE MASQUE OF THE", CINZEL, 26, "#E8C8B8", ls=6, max_w=400))
    out.append(block(D, 300, 152, "RED DEATH", CINZEL, 64, "#FF5A40", "#3A0404", depth=5, ang=(0.5, 0.9), ls=6, max_w=440, face2="#A8120E", shadow="#000000"))
    out.append(tx(300, 548, "EDGAR ALLAN POE · 1842", CINZEL, 17, "#E8B8A8", ls=4, max_w=320))
    return fin(D, out, 15)


# ================================================================ 5. the call of cthulhu — R'lyeh risen, a tentacle from the sea
@design("the-call-of-cthulhu")
def the_call_of_cthulhu():
    D = Doc2("hr-ct")
    out = [night(D, [(0, "#020806"), (0.35, "#0E2420"), (0.62, "#3A5A44"), (0.72, "#2A3E34"), (1, "#06100E")], 1)]
    out.append(puff_cloud(D, 120, 300, 300, 2, ("#3A5244", "#1A2A24", "#06100C"), op=0.9))
    out.append(puff_cloud(D, 470, 270, 320, 3, ("#4A6050", "#1E2E28", "#08120E"), op=0.9))
    out.append(soft_glow(D, 300, 380, 260, "#8AE0A0", 0.25))
    # R'lyeh: leaning monoliths at angles that are all wrong
    city = []
    specs = [(170, 410, 46, 150, -9), (226, 410, 40, 210, 6), (284, 410, 64, 240, -3), (352, 410, 44, 180, 11), (402, 410, 56, 130, -14), (126, 410, 30, 90, 14),
             (460, 410, 34, 100, 8)]
    for k, (x, b, w, h, lean) in enumerate(specs):
        pts = [(x - w / 2, b), (x - w / 2 + 4, b - h), (x + w * 0.1, b - h - 18), (x + w / 2, b - h + 6), (x + w / 2, b)]
        pts = rot(pts, x, b, lean)
        city.append(painted(D, poly_pts(pts, 12, k, 0.6), ("#5A7A64", "#2A4034", "#0A1410"), 3 + k, sdir=(0.7, 0.2), sk=0.2, angle=-90, n=24, inkw=1.2, inkc="#020604", hi=0.3))
        # carved relief bands: zigzags and concentric rings, nothing a human hand would carve
        for j in range(3):
            yy = b - h * (0.25 + 0.22 * j)
            zz = [(x - w * 0.4 + i * w * 0.1, yy + (4 if i % 2 else -4)) for i in range(9)]
            city.append(f'<path d="{pd(rot(zz, x, b, lean), False)}" fill="none" stroke="#9AF0B8" stroke-width="1.4" opacity="0.35"/>')
        rx_, ry_ = rot([(x + w * 0.05, b - h * 0.62)], x, b, lean)[0]
        for rr in (4, 8):
            city.append(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="{rr}" fill="none" stroke="#9AF0B8" stroke-width="1.3" opacity="0.4"/>')
    out.append("".join(city))
    # the great carved door, ajar, light spilling
    out.append(poly([(268, 410), (272, 316), (318, 300), (322, 410)], "#06100A"))
    out.append(f'<path d="M 300 410 L 304 312 L 318 304 L 322 410 Z" fill="#9AF0B8" opacity="0.35"/>')
    out.append(soft_glow(D, 306, 370, 60, "#9AF0B8", 0.4))
    # the sea, heaving
    out.append(swell(D, 420, 6, 160, 0.4, ("#3A6050", "#14302A", "#04100C"), 4, bottom=640))
    out.append(swell(D, 470, 10, 200, 1.6, ("#2E5244", "#0E2620", "#020A08"), 5, bottom=640))
    out.append(swell(D, 530, 14, 240, 2.8, ("#244438", "#0A1E18", "#010604"), 6, bottom=640))
    # the tentacle rising beside the yacht
    out.append(tentacle(D, [(498, 560), (520, 470), (510, 380), (470, 320), (466, 270), (500, 250), (520, 270)], 58, 6, ("#7AA888", "#2E5A44", "#0A2018"), 7, side=-1, rim="#C8F0D0"))
    out.append(swell(D, 548, 8, 120, 0.8, ("#2A4A3E", "#0A1E18", "#010604"), 8, bottom=640, foam=True))
    # a small steam yacht, lantern lit, pitching in the swell
    yx, yy = 168, 470
    hull = rot([(yx - 64, yy - 10), (yx + 60, yy - 12), (yx + 74, yy - 22), (yx + 52, yy + 8), (yx - 54, yy + 8)], yx, yy, -6)
    out.append(poly(hull, "#060A08"))
    out.append(poly(rot([(yx - 30, yy - 12), (yx - 30, yy - 32), (yx + 16, yy - 32), (yx + 16, yy - 12)], yx, yy, -6), "#060A08"))
    out.append(taper(rot([(yx - 4, yy - 32), (yx - 2, yy - 60)], yx, yy, -6), 8, 7, "#060A08"))
    out.append(taper(rot([(yx - 46, yy - 12), (yx - 50, yy - 92)], yx, yy, -6), 2.6, 1.8, "#060A08"))
    out.append(taper(rot([(yx + 40, yy - 14), (yx + 44, yy - 70)], yx, yy, -6), 2.4, 1.6, "#060A08"))
    out.append(smoke(D, [(yx - 4, yy - 64), (yx - 18, yy - 84), (yx - 46, yy - 96), (yx - 80, yy - 100)], 6, 16, 3, "#A8C8B4", 0.5))
    for wx in (yx - 22, yx - 8, yx + 6):
        out.append(f'<rect x="{wx:.1f}" y="{yy - 28:.1f}" width="5" height="6" fill="#FFD27A" transform="rotate(-6 {yx} {yy})"/>')
    out.append(soft_glow(D, yx - 50, yy - 40, 30, "#FFD27A", 0.7))
    out.append(f'<circle cx="{yx - 50:.1f}" cy="{yy - 44:.1f}" r="2.6" fill="#FFF2B0"/>')
    out.append(rain(5, 90, "#B8E0C8", (0.1, 0.3), -8, 24, (-40, 180, 640, 600)))
    out.append(band(D, 0, 220, "#000000", 0.6, 0))
    out.append(band(D, 480, 600, "#000000", 0, 0.95))
    out.append(band(D, 520, 600, "#020604", 0.55, 0.9))
    # lettering: sea-water dripping from the name
    out.append(spaced(300, 84, "THE CALL OF", BEBAS, 36, "#C8F0D0", ls=12, shadow="#000000"))
    out.append(drip_text(D, 300, 180, "CTHULHU", ANTON, 102, [(0, "#E8FFE8"), (0.35, "#8AE0A0"), (0.75, "#2A8A5A"), (1, "#1A5A3A")], 9, ls=6, max_w=440,
                         drip_len=(12, 40), every=0.6, shadow="#000000", hi="#F2FFF2"))
    out.append(sub_rule(300, 548, "H. P. LOVECRAFT · 1928", CINZEL, 18, "#C8F0D0", ls=3, max_w=320, line="#8AE0A0"))
    return fin(D, out, 16)


# ================================================================ 6. nosferatu — the shadow climbing the stairs
def film_wear(seed, box, n_scratch=10, n_dust=60, col="#2A1808", light="#FFF2D0"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n_scratch):
        x = rnd.uniform(x0, x1)
        ya = rnd.uniform(y0, y1 - 60)
        out.append(f'<path d="M {x:.1f} {ya:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(40, 200):.1f}" stroke="{rnd.choice([col, light])}" stroke-width="{rnd.uniform(0.6, 1.3):.1f}" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    for _ in range(n_dust):
        out.append(f'<path d="{blob(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0.6, 2.2), rnd.uniform(0.5, 1.6), rnd.randint(0, 999), 0.4, 8)}" fill="{rnd.choice([col, light])}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    return "".join(out)


def orlok_shadow(x, y, s, col):
    """The 1922 silhouette in profile climbing to the right: hunched back, long coat, bald dome with a bat ear and
    a hooked nose, one arm raised far ahead with long claw fingers. (x, y) = the lower (back) foot."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    # thin legs, the front foot a step higher
    out.append(taper(catmull(L([(14, -66), (6, -34), (0, -2)]), 5), 9 * s, 6 * s, col))
    out.append(taper(catmull(L([(50, -66), (54, -48), (46, -32)]), 5), 9 * s, 6 * s, col))
    out.append(poly(L([(-4, 2), (18, 2), (16, -6), (0, -6)]), col))
    out.append(poly(L([(42, -28), (64, -28), (62, -36), (46, -36)]), col))
    # the long coat, the hunched back
    out.append(poly(L([(6, -58), (-6, -110), (-4, -160), (10, -196), (32, -214), (54, -216), (66, -204), (64, -170), (70, -120), (78, -62), (40, -54)]), col))
    # neck craning forward, the long bald head in profile: bat ear, hooked nose, rat teeth
    out.append(taper(L([(50, -208), (62, -216), (72, -222)]), 14 * s, 12 * s, col))
    out.append(poly(L([(62, -212), (56, -232), (56, -254), (62, -270), (74, -278), (86, -274), (94, -260), (96, -246), (100, -238), (114, -224),
                       (102, -224), (97, -222), (96, -216), (92, -210), (84, -205), (72, -205)]), col))
    out.append(sharp(L([(62, -236), (46, -258), (52, -238), (60, -228)]), col))
    out.append(sharp(L([(95, -219), (99, -211), (93, -216)]), col))
    # the raised arm and the claws reaching up the stairs
    arm = catmull(L([(54, -192), (92, -192), (130, -212), (152, -230)]), 6)
    out.append(taper(arm, 14 * s, 7 * s, col))
    hx, hy = arm[-1]
    for fa, fl in ((-78, 50), (-60, 60), (-42, 62), (-24, 56), (-6, 44)):
        a = math.radians(fa)
        p1 = (hx + math.cos(a) * fl * 0.5 * s, hy + math.sin(a) * fl * 0.5 * s)
        p2 = (hx + math.cos(a + 0.22) * fl * s, hy + math.sin(a + 0.22) * fl * s)
        out.append(taper([(hx, hy), p1, p2], 5 * s, 1.0, col))
    # the other hand held close, claws hanging
    arm2 = catmull(L([(54, -196), (74, -170), (86, -150)]), 5)
    out.append(taper(arm2, 11 * s, 7 * s, col))
    bx, by = arm2[-1]
    for fa in (70, 92, 112):
        a = math.radians(fa)
        out.append(taper([(bx, by), (bx + math.cos(a - 0.3) * 14 * s, by + math.sin(a - 0.3) * 14 * s), (bx + math.cos(a) * 28 * s, by + math.sin(a) * 28 * s)], 3.4 * s, 0.8, col))
    return "".join(out)


@design("nosferatu")
def nosferatu():
    D = Doc2("hr-no")
    out = [f'<rect width="600" height="600" fill="#0A0604"/>']
    fx0, fy0, fx1, fy1 = 56, 150, 544, 500
    cid = D.clip(f'<rect x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" rx="18"/>')
    sc = [f'<rect x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" fill="{D.lin([(0, "#E8C890"), (0.6, "#C8985A"), (1, "#6A4422")], 0, 0, 1, 1)}"/>']
    sc.append(strokes(D.nid(), f"M {fx0} {fy0} L {fx1} {fy0} L {fx1} {fy1} L {fx0} {fy1} Z", (fx0, fy0, fx1, fy1), ["#F2D8A8", "#8A5A2A", "#D8B070"], 3, n=90,
                      angle=-80, length=(30, 90), width=(3, 9), opacity=(0.08, 0.22)))
    # raking light from a lamp low on the left: the wall brightest there
    sc.append(soft_glow(D, 120, 470, 300, "#FFF2D0", 0.45))
    # the staircase: steps rising to the right, a door at the top landing
    stairs = []
    sx, sy = 30, 540
    for k in range(10):
        stairs += [(sx + k * 46, sy - k * 32), (sx + (k + 1) * 46, sy - k * 32)]
    stair_poly = [(fx0 - 10, fy1 + 10)] + stairs + [(fx1 + 10, sy - 9 * 32), (fx1 + 10, fy1 + 10)]
    sc.append(f'<path d="{pd(stair_poly)}" fill="{D.lin([(0, "#5A3A1E"), (1, "#1A0E06")], 0, 0, 0.4, 1)}"/>')
    sc.append(strokes(D.nid(), pd(stair_poly), (fx0, 200, fx1, fy1), ["#7A5230", "#140A04", "#4A2E16"], 5, n=60, angle=-35, length=(20, 60), width=(2, 5), opacity=(0.15, 0.35)))
    for k in range(10):
        a, b = (sx + k * 46, sy - k * 32), (sx + (k + 1) * 46, sy - k * 32)
        sc.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="#F2D8A8" stroke-width="2.4" opacity="0.7"/>')
        sc.append(f'<path d="M {a[0]} {a[1]} L {a[0]} {a[1] + 32}" stroke="#0A0402" stroke-width="1.6" opacity="0.6"/>')
    # banister shadows: long diagonal bars on the wall
    for k in range(10):
        bx = 60 + k * 46
        by = 520 - k * 32
        sc.append(f'<path d="M {bx + 30:.1f} {by - 70:.1f} L {bx + 110:.1f} {by - 214:.1f}" stroke="#3A2210" stroke-width="5" opacity="0.25"/>')
    sc.append(f'<path d="M 60 452 L 560 104" stroke="#3A2210" stroke-width="9" opacity="0.25"/>')
    # the door on the landing, ajar: blackness beyond
    sc.append(f'<path d="M 464 252 L 464 150 L 530 150 L 530 252 Z" fill="#2A1A0C"/>')
    sc.append(f'<path d="M 476 252 L 476 158 L 530 150 L 530 252 Z" fill="#050302"/>')
    sc.append(f'<path d="M 458 254 L 458 144 L 536 144" fill="none" stroke="#3A2210" stroke-width="6"/>')
    # THE SHADOW, climbing
    sc.append(orlok_shadow(196, 446, 0.98, "#1A0E06"))
    # the iris: the frame closes in at the corners like an old lens
    sc.append(f'<rect x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" fill="{D.rad([(0, "#000000", 0), (0.62, "#000000", 0), (0.9, "#000000", 0.55), (1, "#000000", 0.9)], 0.5, 0.5, 0.72)}"/>')
    sc.append(film_wear(7, (fx0, fy0, fx1, fy1)))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" rx="18" fill="none" stroke="#E8D2A8" stroke-width="2.4"/>')
    # the intertitle frame: double rules with stepped corners
    for (ins, w, op) in ((22, 2.4, 0.9), (30, 1.2, 0.7)):
        out.append(f'<rect x="{ins}" y="{ins}" width="{600 - 2 * ins}" height="{600 - 2 * ins}" fill="none" stroke="#E8D2A8" stroke-width="{w}" opacity="{op}"/>')
    for cx_, cy_, sx_, sy_ in ((22, 22, 1, 1), (578, 22, -1, 1), (22, 578, 1, -1), (578, 578, -1, -1)):
        out.append(f'<path d="M {cx_ + sx_ * 16} {cy_ + sy_ * 4} L {cx_ + sx_ * 16} {cy_ + sy_ * 16} L {cx_ + sx_ * 4} {cy_ + sy_ * 16}" fill="none" stroke="#E8D2A8" stroke-width="2"/>')
    # lettering: sharp, leaning expressionist capitals
    fs = _fit("NOSFERATU", BEBAS, 104, 440, 8)
    out.append(f'<g transform="translate(300 132) skewX(-10) translate(-300 -132)">'
               + block(D, 300, 132, "NOSFERATU", BEBAS, 96, "#F2E2C0", "#5A3A1A", depth=5, ang=(1, 0.8), ls=8, max_w=440, face2="#D8B880") + '</g>')
    out.append(spaced(300, 540, "A SYMPHONY OF HORROR · 1922", JOST, 19, "#E8D2A8", ls=5, max_w=420))
    return fin(D, out, 17)


# ================================================================ 7. frankenstein — the giant on the Arctic ice
def ice_ship(D, x, wl, s, seed, col="#0A1420", rim="#DCF2FF"):
    def L(pts):
        return T(pts, x, wl, s)
    out = [poly(L([(-90, -8), (80, -10), (96, -30), (100, -36), (70, -8), (60, 6), (-80, 6), (-96, -16)]), col)]
    out.append(poly(L([(-96, -16), (-92, -30), (-70, -26), (-80, -8)]), col))
    for (mx, mh) in ((-50, 150), (8, 180), (58, 140)):
        out.append(taper(L([(mx, -8), (mx, -8 - mh)]), 3.2 * s, 1.8 * s, col))
        for k, yy in enumerate((0.42, 0.68, 0.88)):
            ww = (1 - yy) * 70 + 14
            out.append(taper(L([(mx - ww / 2, -8 - mh * yy), (mx + ww / 2, -8 - mh * yy)]), 2.4 * s, 2.4 * s, col))
            out.append(taper(L([(mx - ww / 2, -6 - mh * yy), (mx + ww / 2, -6 - mh * yy)]), 1.6, 1.6, rim, 0.6))
    # rigging lines
    for a, b in (((-96, -24), (-50, -158)), ((-50, -158), (8, -188)), ((8, -188), (58, -148)), ((58, -148), (100, -36)), ((-50, -158), (-80, -8)), ((8, -188), (40, -8))):
        p, q = L([a, b])
        out.append(f'<path d="M {p[0]:.1f} {p[1]:.1f} L {q[0]:.1f} {q[1]:.1f}" stroke="{col}" stroke-width="1.2" opacity="0.8"/>')
    out.append(ink(smooth_open(L([(-92, -30), (-70, -26), (80, -10), (96, -30)])), rim, 1.6, seed, 1, 0.7))
    for k in range(4):
        px, py = L([(-50 + k * 30, -2)])[0]
        out.append(soft_glow(D, px, py, 12, "#FFD27A", 0.6))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2.2 * s:.1f}" fill="#FFE8A0"/>')
    return "".join(out)


def sledge_team(x, base, s, col="#05080E", rim="#DCF2FF"):
    """A dog sledge in the far distance and the gigantic figure standing on it, driving north."""
    def L(pts):
        return T(pts, x, base, s)
    out = [taper(L([(-30, 0), (10, 0), (16, -4)]), 2.4 * s, 2 * s, col)]
    out.append(poly(L([(-28, -2), (6, -2), (6, -8), (-28, -8)]), col))
    for k in range(5):
        dx = 22 + k * 15
        out.append(poly(L([(dx, -2), (dx + 2, -8), (dx + 10, -10), (dx + 13, -14), (dx + 15, -10), (dx + 13, -6), (dx + 11, -2), (dx + 9, -6), (dx + 4, -6)]), col))
    out.append(f'<path d="M {L([(6, -6)])[0][0]:.1f} {L([(6, -6)])[0][1]:.1f} L {L([(92, -10)])[0][0]:.1f} {L([(92, -10)])[0][1]:.1f}" stroke="{col}" stroke-width="1"/>')
    # the giant: far too tall for the sledge, wrapped in rags, leaning into the wind with the reins
    out.append(taper(catmull(L([(-18, -8), (-20, -22), (-18, -36)]), 4), 5 * s, 6 * s, col))
    out.append(taper(catmull(L([(-8, -8), (-8, -22), (-10, -36)]), 4), 5 * s, 6 * s, col))
    out.append(poly(L([(-24, -34), (-26, -50), (-22, -64), (-14, -70), (-2, -70), (4, -62), (2, -48), (-2, -34)]), col))
    out.append(poly(L([(-26, -46), (-34, -30), (-28, -26), (-22, -40)]), col))
    out.append(f'<path d="{blob(*L([(-8, -77)])[0], 4.6 * s, 5.4 * s, 2, 0.06, 10)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-10, -82)])[0], 5 * s, 2.6 * s, 3, 0.3, 10)}" fill="{col}"/>')
    out.append(taper(catmull(L([(0, -64), (10, -52), (20, -44)]), 5), 4.4 * s, 3 * s, col))
    out.append(f'<path d="M {L([(20, -44)])[0][0]:.1f} {L([(20, -44)])[0][1]:.1f} L {L([(24, -10)])[0][0]:.1f} {L([(24, -10)])[0][1]:.1f}" stroke="{col}" stroke-width="0.9"/>')
    out.append(ink(smooth_open(L([(-6, -82), (-3, -76), (2, -68), (4, -60), (2, -48)])), rim, 1.3, 3, 1, 0.85))
    return "".join(out)


@design("frankenstein")
def frankenstein():
    D = Doc2("hr-fr")
    out = [night(D, [(0, "#02040C"), (0.4, "#0A1A2E"), (0.66, "#1E3A52"), (1, "#0E1A28")], 1)]
    out.append(stars_field(3, (0, 0, 600, 360), 150))
    out.append(aurora(D, 4, 140, 330, cols=("#5AF0B0", "#3AC8C0", "#A890F0")))
    # the frozen sea: a plain of ice to the horizon, pressure ridges in front
    out.append(hill(D, [(-20, 372), (200, 370), (420, 374), (620, 370)], 640, ("#B8D8F0", "#6A90B8", "#243A58"), 2, inkw=0, n=40, lit="#EAF6FF"))
    out.append(fog(D, 376, 30, 3, "#C8E8FF", 0.4))
    rnd = random.Random(5)
    for k in range(12):
        bx = rnd.uniform(-20, 620)
        by = rnd.uniform(390, 470)
        bw, bh = rnd.uniform(30, 90), rnd.uniform(12, 34)
        pts = poly_pts([(bx - bw / 2, by), (bx - bw * 0.3, by - bh), (bx + bw * 0.1, by - bh * 1.1), (bx + bw / 2, by - bh * 0.4), (bx + bw / 2 + 4, by)], 10, k, 1.2)
        out.append(painted(D, pts, ("#EAF6FF", "#9AB8D8", "#3A5878"), 10 + k, sdir=(0.8, 0.3), sk=0.25, angle=-60, n=10, inkw=1, inkc="#14243A", hi=0.6))
    # the giant on his sledge, small and far, driving out across the ice
    out.append(sledge_team(410, 378, 1.5))
    out.append(cast(D, 450, 382, 110, 5, "#0A1A2E", 0.4, 4))
    # the ship locked in the ice, lanterns lit
    out.append(ice_ship(D, 150, 430, 1.05, 6))
    out.append(hill(D, ridge([(-20, 452), (80, 436), (180, 450), (300, 440), (420, 456), (620, 444)], 7, 8, 4), 640, ("#DCEEFF", "#8AAAC8", "#2A4462"), 7, inkw=1.2, inkc="#14243A", n=60, lit="#FFFFFF"))
    for k in range(6):
        bx = 40 + k * 110 + rnd.uniform(-20, 20)
        pts = poly_pts([(bx - 40, 520), (bx - 24, 470 - rnd.uniform(0, 20)), (bx + 6, 462 - rnd.uniform(0, 26)), (bx + 36, 486), (bx + 46, 520)], 10, k + 20, 1.4)
        out.append(painted(D, pts, ("#F2FAFF", "#A8C4E0", "#3A5878"), 30 + k, sdir=(0.8, 0.4), sk=0.25, angle=-70, n=12, inkw=1.2, inkc="#14243A", hi=0.6))
    out.append(snowfall(8, (0, 0, 600, 600), 70, (0.6, 2.0), "#FFFFFF", (0.3, 0.8)))
    out.append(band(D, 480, 600, "#02040C", 0, 0.85))
    out.append(band(D, 0, 180, "#02040C", 0.5, 0))
    # lettering
    out.append(glow_text(D, 300, 128, "Frankenstein", DMS, 88, "#F2FAFF", "#7AE0F0", ls=1, max_w=450, strength=1.0, shadow="#000814"))
    out.append(tx(300, 168, "or, The Modern Prometheus", SERIF_IT, 26, "#BFE6F2", max_w=420))
    out.append(sub_rule(300, 548, "MARY SHELLEY · 1818", CINZEL, 18, "#DCF2FF", ls=4, max_w=320, line="#7AE0F0"))
    return fin(D, out, 18)


# ================================================================ 8. the phantom of the opera — the mask on the organ, the lake below the Opéra
def organ_pipes(D, x0, x1, base, top, seed, pal=("#FFE7A0", "#B8862E", "#4A3008")):
    rnd = random.Random(seed)
    out = []
    n = 9
    w = (x1 - x0) / n
    for k in range(n):
        cx = x0 + w * (k + 0.5)
        h = (base - top) * (0.55 + 0.45 * (1 - abs(k - (n - 1) / 2) / ((n - 1) / 2)) ** 1.4)
        px0, px1 = cx - w * 0.36, cx + w * 0.36
        g = D.lin([(0, pal[2]), (0.3, pal[0]), (0.55, pal[1]), (1, pal[2])], 0, 0, 1, 0)
        out.append(f'<path d="M {px0:.1f} {base} L {px0:.1f} {base - h:.1f} Q {cx:.1f} {base - h - w * 0.3:.1f} {px1:.1f} {base - h:.1f} L {px1:.1f} {base} Z" fill="{g}"/>')
        my = base - h * 0.22
        out.append(f'<path d="M {px0:.1f} {my:.1f} L {cx:.1f} {my - w * 0.4:.1f} L {px1:.1f} {my:.1f} L {px1:.1f} {my + w * 0.3:.1f} L {px0:.1f} {my + w * 0.3:.1f} Z" fill="#140A04" opacity="0.85"/>')
        out.append(ink(f"M {px0:.1f} {base} L {px0:.1f} {base - h:.1f}", "#2A1804", 1.2, seed + k, 1, 0.8))
    return "".join(out)


def black_mask(D, cx, cy, s, seed, ang=-8):
    """Erik's mask from the novel: black, covering the whole face, with eye holes; a silk cord."""
    def L(pts):
        return T(pts, cx, cy, s, False, ang)
    face = L([(0, -44), (20, -40), (32, -24), (34, 0), (28, 26), (14, 44), (0, 50), (-14, 44), (-28, 26), (-34, 0), (-32, -24), (-20, -40)])
    out = [cast(D, cx + 10, cy + 46 * s, 46 * s, 8 * s, "#000000", 0.6, seed)]
    out.append(painted(D, face, ("#5A5A6A", "#141418", "#000000"), seed, sdir=(0.7, 0.5), sk=0.22, angle=-90, n=16, inkw=1.4, inkc="#000000", hi=0.55, hik=0.1))
    for sg in (-1, 1):
        out.append(f'<path d="{smooth_closed(L([(sg * 6, -8), (sg * 14, -14), (sg * 24, -10), (sg * 20, -2), (sg * 10, -2)]))}" fill="#E8C890" opacity="0.9"/>')
    out.append(taper(L([(-4, -6), (-2, 14), (4, 16)]), 2.6 * s, 1.4 * s, "#5A5A6A", 0.7))
    out.append(taper(L([(-24, -30), (-10, -38), (8, -38)]), 3 * s, 1.2 * s, "#8A8A9A", 0.7))
    out.append(taper(catmull(L([(32, -14), (52, -6), (60, 14), (50, 30)]), 6), 2.2, 1.6, "#3A3A44"))
    return "".join(out)


@design("the-phantom-of-the-opera")
def the_phantom_of_the_opera():
    D = Doc2("hr-ph")
    out = [f'<rect width="600" height="600" fill="#08060A"/>']
    # the vaulted cellars and the lake, candles along the water
    for k, (ax, aw) in enumerate(((150, 230), (420, 230))):
        pts = arch_pts(ax - aw / 2, ax + aw / 2, 300, 420, 8)
        out.append(f'<path d="M {ax - aw / 2 - 30} 180 L {ax + aw / 2 + 30} 180 L {ax + aw / 2 + 30} 420 L {ax - aw / 2 - 30} 420 Z" fill="#2A1A14"/>')
        out.append(f'<path d="{smooth_closed(pts)}" fill="{D.rad([(0, "#5A3A24"), (0.6, "#1E120C"), (1, "#0A0604")], 0.5, 0.75, 0.7)}"/>')
        out.append(stone_courses([190 + j * 22 for j in range(11)], lambda y, a=ax, w=aw: a - w / 2 - 30, ax + aw / 2 + 30, "#0A0604", 1.4, 0.5, k, unit=30))
        out.append(ink(smooth_open(pts[len(pts) // 2 - 26:len(pts) // 2 + 26]), "#8A5A3A", 2.4, k, 1, 0.6))
    for (cx, cy) in ((54, 360), (186, 340), (300, 352)):
        out.append(candle(D, cx, cy + 40, 30, cx, w=10, glow_r=70))
    out.append(sea(D, 420, 600, [(0, "#2A1A12"), (0.5, "#120A08"), (1, "#050304")], 3, ["#5A3A24", "#000000", "#C8904A"], 50))
    for (cx, _) in ((54, 0), (186, 0), (300, 0)):
        out.append(f'<path d="{blob(cx, 452, 8, 28, cx, 0.2, 10)}" fill="#FFC860" opacity="0.3"/>')
    out.append(wave_lines(4, (0, 426, 600, 520), ["#C8904A", "#3A2418"], 40, (12, 34), 1.4, 1.5, (0.3, 0.6)))
    # the little boat drifting on the black water
    out.append(poly([(110, 446), (240, 446), (262, 432), (230, 456), (124, 456), (100, 438)], "#050304"))
    out.append(taper([(228, 446), (240, 380)], 2, 1.6, "#050304"))
    out.append(soft_glow(D, 240, 376, 22, "#FFC860", 0.7))
    out.append(f'<circle cx="240" cy="376" r="3" fill="#FFF2B0"/>')
    out.append(f'<path d="{blob(240, 470, 6, 20, 3, 0.2, 10)}" fill="#FFC860" opacity="0.3"/>')
    # the organ console in the foreground: pipes, then the keyboard with the mask laid on the keys
    out.append(organ_pipes(D, 360, 556, 470, 220, 5))
    out.append(soft_glow(D, 300, 470, 220, "#FFC060", 0.3))
    kb = poly_pts([(40, 470), (560, 470), (580, 520), (20, 520)], 20, 2, 0.4)
    out.append(painted(D, poly_pts([(10, 470), (590, 470), (600, 610), (0, 610)], 20, 3, 0.4), ("#5A2E1E", "#2A140C", "#0A0402"), 6, sdir=(0.3, 1), sk=0.1, angle=0, n=40, inkw=1.4, inkc="#000000", hi=0.3))
    keys = [f'<path d="M 46 478 L 554 478 L 568 512 L 32 512 Z" fill="#F2E8D2"/>']
    for k in range(37):
        x = 46 + k * 508 / 37
        keys.append(f'<path d="M {x:.1f} 478 L {x - (300 - x) * 0.04:.1f} 512" stroke="#8A7A62" stroke-width="1"/>')
        if k % 7 not in (2, 6):
            bx = x + 508 / 37 * 0.65
            keys.append(f'<path d="M {bx:.1f} 478 L {bx + 7:.1f} 478 L {bx + 7 - (300 - bx) * 0.024:.1f} 498 L {bx - (300 - bx) * 0.024:.1f} 498 Z" fill="#100806"/>')
    out.append("".join(keys))
    out.append(f'<path d="M 32 512 L 568 512 L 572 520 L 28 520 Z" fill="#1A0A06"/>')
    out.append(black_mask(D, 410, 470, 1.0, 7, ang=-24))
    # a page of the score, curling
    out.append(painted(D, poly_pts([(130, 472), (210, 466), (214, 506), (134, 512)], 12, 9, 0.6), ("#FFFCF0", "#EDE2C8", "#A89270"), 9, sdir=(0.6, 0.6), sk=0.15, n=8, inkw=1, inkc="#3A2A1A", hi=0.4))
    for k in range(4):
        out.append(f'<path d="M 138 {478 + k * 8} L 206 {474 + k * 8}" stroke="#3A2A1A" stroke-width="0.9" opacity="0.6"/>')
    for k in range(7):
        out.append(f'<circle cx="{146 + k * 9}" cy="{480 + (k * 5) % 22}" r="2" fill="#2A1A10"/>')
    out.append(band(D, 0, 200, "#000000", 0.7, 0))
    # lettering
    out.append(sub_rule(300, 76, "OPÉRA DE PARIS", CINZEL, 16, "#E8C890", ls=5, max_w=300))
    out.append(gilt(D, 300, 140, "THE PHANTOM", DMS, 72, ls=3, max_w=440, seed=13, deboss="#000000", dop=0.9))
    out.append(tx(300, 182, "of the Opera", SERIF_IT, 40, "#F2E2C0", max_w=300))
    out.append(tx(300, 548, "GASTON LEROUX · 1910", CINZEL, 17, "#E8C890", ls=4, max_w=320))
    return fin(D, out, 19)


# ================================================================ 9. jekyll & hyde — the draught, and the other man in the glass
def flask(D, cx, base, h, w, seed, liquid=("#C8F0A0", "#5AC85A", "#1A6A2A"), level=0.55, neck=0.32, label_txt=None):
    """A blown-glass graduated flask: liquid with a meniscus, highlights, a few rising bubbles."""
    nw = w * neck
    body = [(cx - w / 2, base), (cx - w / 2, base - h * 0.5), (cx - nw / 2, base - h * 0.78), (cx - nw / 2, base - h), (cx + nw / 2, base - h),
            (cx + nw / 2, base - h * 0.78), (cx + w / 2, base - h * 0.5), (cx + w / 2, base)]
    d = smooth_closed(jitter(body, seed, 0.4))
    out = [cast(D, cx + 10, base, w * 0.7, 6, "#000000", 0.5, seed)]
    out.append(f'<path d="{d}" fill="#DCE8F0" opacity="0.18"/>')
    ly = base - h * 0.5 * level - (h * 0.25 if level > 1 else 0)
    cid = D.clip(f'<path d="{d}"/>')
    liq = f'<rect x="{cx - w}" y="{ly:.1f}" width="{2 * w}" height="{h}" fill="{D.lin([(0, liquid[0]), (0.4, liquid[1]), (1, liquid[2])])}"/>'
    rnd = random.Random(seed)
    bub = "".join(f'<circle cx="{cx + rnd.uniform(-w * 0.35, w * 0.35):.1f}" cy="{rnd.uniform(ly + 4, base - 4):.1f}" r="{rnd.uniform(1, 3.4):.1f}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.7"/>' for _ in range(14))
    out.append(f'<g {cid}>{liq}<ellipse cx="{cx}" cy="{ly:.1f}" rx="{w * 0.6:.1f}" ry="3" fill="{liquid[0]}" opacity="0.9"/>{bub}</g>')
    out.append(soft_glow(D, cx, base - h * 0.2, w * 1.1, liquid[1], 0.45))
    out.append(ink(d, "#C8D8E0", 2, seed, 2, 0.75))
    out.append(taper([(cx - w * 0.36, base - h * 0.12), (cx - w * 0.4, base - h * 0.42)], 4, 2, "#FFFFFF", 0.6))
    out.append(taper([(cx - nw * 0.25, base - h * 0.97), (cx - nw * 0.25, base - h * 0.8)], 2, 1.4, "#FFFFFF", 0.6))
    for k in range(4):
        yy = base - h * (0.1 + 0.09 * k)
        out.append(f'<path d="M {cx + w * 0.22:.1f} {yy:.1f} l {w * 0.14:.1f} 0" stroke="#FFFFFF" stroke-width="1.2" opacity="0.5"/>')
    return "".join(out)


def hyde_silhouette(x, base, s, col):
    """A small, stooped man in a top hat and long coat, one hand clawed: Hyde as a shadow in the glass."""
    def L(pts):
        return T(pts, x, base, s)
    out = [poly(L([(-14, 0), (-12, -30), (-18, -60), (-14, -86), (0, -98), (16, -94), (24, -80), (22, -56), (16, -30), (18, 0)]), col)]
    out.append(f'<path d="{blob(*L([(12, -108)])[0], 10 * s, 11 * s, 4, 0.08, 12)}" fill="{col}"/>')
    out.append(poly(L([(0, -114), (2, -138), (24, -140), (24, -114), (30, -112), (-6, -112)]), col))
    out.append(taper(catmull(L([(18, -84), (30, -64), (40, -56)]), 5), 8 * s, 5 * s, col))
    for fa in (-20, 10, 40):
        a = math.radians(fa)
        hx, hy = L([(40, -56)])[0]
        out.append(taper([(hx, hy), (hx + math.cos(a) * 10 * s, hy + math.sin(a) * 10 * s)], 2.6 * s, 0.8, col))
    out.append(taper(L([(-10, -2), (-14, 0)]), 6 * s, 6 * s, col))
    return "".join(out)


@design("jekyll-and-hyde")
def jekyll_and_hyde():
    D = Doc2("hr-jh")
    out = [f'<rect width="600" height="600" fill="#0E0A08"/>']
    # panelled cabinet wall, warm in the lamplight
    out.append(f'<rect width="600" height="420" fill="{D.lin([(0, "#2A1A12"), (1, "#3A2418")])}"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 420 L 0 420 Z", (0, 0, 600, 420), ["#4A3020", "#1A0E08", "#5A3A26"], 3, n=120, angle=-90, length=(30, 100), width=(3, 8), opacity=(0.1, 0.3)))
    # the fog-bound window: a gas lamp in Soho
    wx0, wy0, wx1, wy1 = 66, 150, 196, 330
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#6A7A5A"), (1, "#A8A878")])}"/>')
    out.append(soft_glow(D, 120, 250, 60, "#FFE8A0", 0.6))
    out.append(taper([(120, 330), (120, 252)], 3, 2, "#1A1A14"))
    out.append(poly([(112, 252), (128, 252), (124, 236), (116, 236)], "#1A1A14"))
    out.append(f'<circle cx="120" cy="245" r="4" fill="#FFF2B0"/>')
    wc = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    out.append(f'<g {wc}>{fog(D, 290, 70, 4, "#D8D8B8", 0.6, wx0, wx1)}</g>')
    out.append(f'<path d="M {(wx0 + wx1) / 2} {wy0} L {(wx0 + wx1) / 2} {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#1A0E08" stroke-width="5"/>')
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="none" stroke="#1A0E08" stroke-width="8"/>')
    # the cheval glass: in it, the stooped shadow of another man
    mx0, my0, mx1, my1 = 330, 120, 520, 400
    mpts = arch_pts(mx0, mx1, my0 + 95, my1, 8)
    out.append(f'<path d="{smooth_closed(arch_pts(mx0 - 14, mx1 + 14, my0 + 95, my1 + 12, 8))}" fill="{D.lin([(0, "#6A4424"), (0.5, "#3A2212"), (1, "#1A0E06")], 0, 0, 1, 0)}"/>')
    out.append(f'<path d="{smooth_closed(mpts)}" fill="{D.lin([(0, "#3A4A44"), (0.6, "#1A2420"), (1, "#0A100E")], 0, 0, 0.6, 1)}"/>')
    cid = D.clip(f'<path d="{smooth_closed(mpts)}"/>')
    m_in = [soft_glow(D, 420, 360, 120, "#7AE08A", 0.3), hyde_silhouette(430, 400, 1.75, "#040806")]
    m_in.append(f'<path d="M {mx0 + 20} {my1} L {mx0 + 120} {my0} L {mx0 + 150} {my0} L {mx0 + 50} {my1} Z" fill="#FFFFFF" opacity="0.07"/>')
    m_in.append(f'<path d="M {mx0 + 70} {my1} L {mx0 + 170} {my0} L {mx0 + 180} {my0} L {mx0 + 80} {my1} Z" fill="#FFFFFF" opacity="0.06"/>')
    out.append(f'<g {cid}>{"".join(m_in)}</g>')
    out.append(ink(smooth_closed(mpts), "#C8963A", 2.4, 4, 1, 0.8))
    # the bench
    out.append(painted(D, poly_pts([(-10, 420), (610, 420), (610, 444), (-10, 444)], 20, 5, 0.4), ("#8A5A34", "#4A2A16", "#1A0C04"), 5, sdir=(0, 1), sk=0.2, angle=0, n=40, inkw=1.4, inkc="#0A0402", hi=0.5))
    out.append(f'<rect x="-10" y="444" width="620" height="170" fill="{D.lin([(0, "#1A0E08"), (1, "#050302")])}"/>')
    # a retort and a rack of phials beside the draught
    out.append(flask(D, 104, 420, 70, 46, 11, liquid=("#F2C8E8", "#A85AC8", "#4A1A6A"), level=0.5))
    for k, c in enumerate((("#F2E0A0", "#D8A030", "#6A4A10"), ("#F2A8A0", "#C83A3A", "#5A0A0A"), ("#C8E8F2", "#4A9AC8", "#1A3A5A"))):
        out.append(flask(D, 450 + k * 34, 420, 52, 18, 20 + k, liquid=c, level=0.7, neck=0.6))
    # the draught itself, boiling green
    out.append(flask(D, 300, 420, 190, 108, 7, liquid=("#E8FFB0", "#6AE04A", "#1A6A1A"), level=0.62, neck=0.3))
    out.append(smoke(D, [(300, 228), (288, 196), (310, 160), (296, 120), (318, 84)], 6, 20, 4, "#B8F0A0", 0.5))
    rnd = random.Random(9)
    for _ in range(14):
        out.append(f'<circle cx="{300 + rnd.uniform(-20, 20):.1f}" cy="{rnd.uniform(110, 230):.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="#DFFFC8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(vignette(D, "#000000", 0.6))
    # the chemist's label
    lx0, ly0, lx1, ly1 = 92, 462, 508, 548
    lab = [(lx0 + 12, ly0), (lx1 - 12, ly0), (lx1, ly0 + 12), (lx1, ly1 - 12), (lx1 - 12, ly1), (lx0 + 12, ly1), (lx0, ly1 - 12), (lx0, ly0 + 12)]
    out.append(painted(D, poly_pts(lab, 14, 3, 0.4), ("#FFF8E2", "#EFE0BC", "#B89A66"), 12, sdir=(0.6, 0.6), sk=0.1, angle=0, n=30, inkw=0, hi=0.3))
    out.append(f'<path d="{pd(poly_pts(lab, 14, 3, 0.4))}" fill="none" stroke="#2A1A0E" stroke-width="2.4"/>')
    inner = [(x + (6 if x < 300 else -6), y + (6 if y < 500 else -6)) for x, y in lab]
    out.append(f'<path d="{pd(inner)}" fill="none" stroke="#2A1A0E" stroke-width="1"/>')
    out.append(tx(300, 508, "Dr Jekyll & Mr Hyde", DMS, 42, "#1A0E06", max_w=390))
    out.append(tx(300, 534, "R. L. STEVENSON · LONDON · 1886", JOST, 16, "#6A1A14", ls=2.5, max_w=380))
    out.append(sub_rule(300, 78, "ONE DOSE ONLY", BEBAS, 28, "#C8F0A8", ls=6, max_w=300, line="#8AE07A"))
    return fin(D, out, 20)


# ================================================================ 10. the tell-tale heart — louder, louder, louder
@design("the-tell-tale-heart")
def the_tell_tale_heart():
    D = Doc2("hr-th")
    out = [f'<rect width="600" height="600" fill="#140A06"/>']
    # wide old floorboards seen from above, laid on a slant
    ang = -14
    rnd = random.Random(3)
    boards = []
    bw = 58
    for k in range(-4, 16):
        y0 = k * bw
        pts = poly_pts(rot([(-200, y0), (800, y0), (800, y0 + bw - 3), (-200, y0 + bw - 3)], 300, 300, ang), 30, k, 0.5)
        shade = rnd.choice([("#8A5A34", "#5A361C", "#2A160A"), ("#7A4E2C", "#4E2E16", "#24120A"), ("#946238", "#603A1E", "#2E1A0C")])
        boards.append(painted(D, pts, shade, 10 + k, sdir=(0, 1), sk=0.12, angle=ang, n=50, slen=(40, 160), sw=(1, 3), inkw=0, hi=0.25))
        for j in range(8):
            gx = rnd.uniform(-100, 700)
            gpts = rot([(gx, y0 + rnd.uniform(8, bw - 10)), (gx + rnd.uniform(60, 160), y0 + rnd.uniform(8, bw - 10))], 300, 300, ang)
            boards.append(pline(gpts, shade[2], 1.1, k * 9 + j, 0.4, 1))
        for nx in (60, 360):
            for ny in (8, bw - 11):
                p = rot([(nx + (k % 3) * 40, y0 + ny)], 300, 300, ang)[0]
                boards.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.2" fill="#1A0E06"/><circle cx="{p[0] - 0.6:.1f}" cy="{p[1] - 0.6:.1f}" r="0.9" fill="#C8A070" opacity="0.6"/>')
    out.append("".join(boards))
    # the loose plank, prised up a little: light and the beat leak out of the crack
    k = 6
    y0 = k * bw
    plank = rot([(150, y0 - 4), (470, y0 - 6), (470, y0 + bw - 2), (150, y0 + bw - 3)], 300, 300, ang)
    gap = rot([(150, y0 + bw - 3), (470, y0 + bw - 2), (470, y0 + bw + 6), (150, y0 + bw + 4)], 300, 300, ang)
    out.append(f'<path d="{pd(gap)}" fill="#FF6A3A"/>')
    out.append(soft_glow(D, *rot([(310, y0 + bw + 2)], 300, 300, ang)[0], 120, "#FF4A2A", 0.45))
    out.append(cast(D, *rot([(310, y0 + bw + 8)], 300, 300, ang)[0], 170, 10, "#000000", 0.5))
    plank = poly_pts(plank, 16, 3, 0.4)
    out.append(painted(D, plank, ("#A06A40", "#6A4222", "#2E1A0C"), 66, sdir=(0, -1), sk=0.15, angle=ang, n=40, inkw=1.4, inkc="#1A0A04", hi=0.4))
    # the beat: concentric rings throbbing out from under the plank
    cx_, cy_ = rot([(310, y0 + bw + 2)], 300, 300, ang)[0]
    for j, r in enumerate((40, 74, 112, 156)):
        out.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_:.1f}" rx="{r * 1.5:.1f}" ry="{r * 0.62:.1f}" transform="rotate({ang} {cx_:.1f} {cy_:.1f})" fill="none" stroke="#FF5A3A" stroke-width="{3.2 - j * 0.6:.1f}" opacity="{0.6 - j * 0.12:.2f}" stroke-dasharray="{14 - j * 2} {8 + j * 3}"/>')
    # the dark lantern on the floor, its single thread of light
    lx, ly = 112, 466
    out.append(f'<path d="M {lx + 30} {ly - 8} L 560 236 L 566 256 L {lx + 32} {ly + 2} Z" fill="{D.lin([(0, "#FFE8A0", 0.7), (1, "#FFE8A0", 0)], 0, 0, 1, 0)}"/>')
    out.append(cast(D, lx + 6, ly + 34, 52, 12, "#000000", 0.6))
    tin = ("#9A9AA4", "#4A4A54", "#14141A")
    out.append(painted(D, poly_pts([(lx - 30, ly + 32), (lx - 30, ly - 36), (lx + 26, ly - 36), (lx + 26, ly + 32)], 10, 4, 0.4), tin, 7, sdir=(-0.7, 0.3), sk=0.25, angle=-90, n=14, inkw=1.4, inkc="#000000", hi=0.5))
    for k in range(4):
        out.append(f'<path d="M {lx - 22 + k * 14} {ly - 32} L {lx - 22 + k * 14} {ly + 28}" stroke="#2A2A30" stroke-width="1" opacity="0.6"/>')
    for yy in (ly - 30, ly + 26):
        out.append(f'<path d="M {lx - 32} {yy} L {lx + 28} {yy}" stroke="#14141A" stroke-width="4"/>')
    out.append(painted(D, [(lx - 34, ly - 36), (lx - 18, ly - 58), (lx + 14, ly - 58), (lx + 30, ly - 36)], tin, 8, sdir=(-0.7, 0.4), sk=0.2, angle=0, n=8, inkw=1.4, inkc="#000000", hi=0.5))
    out.append(painted(D, poly_pts([(lx - 12, ly - 58), (lx - 12, ly - 74), (lx + 8, ly - 74), (lx + 8, ly - 58)], 6, 5, 0.3), tin, 9, sdir=(-0.7, 0.4), sk=0.2, n=6, inkw=1.2, inkc="#000000", hi=0.5))
    out.append(f'<path d="M {lx - 16} {ly - 76} L {lx + 12} {ly - 76}" stroke="#14141A" stroke-width="4"/>')
    out.append(taper(catmull([(lx - 30, ly - 20), (lx - 50, ly - 40), (lx - 40, ly - 66), (lx - 14, ly - 70)], 6), 3, 3, "#14141A"))
    # the bullseye lens, its shutter open the width of a thread
    out.append(soft_glow(D, lx + 30, ly - 2, 46, "#FFE8A0", 0.8))
    out.append(f'<ellipse cx="{lx + 28}" cy="{ly - 2}" rx="9" ry="20" fill="#FFF2B0" stroke="#14141A" stroke-width="3"/>')
    out.append(f'<ellipse cx="{lx + 26}" cy="{ly - 8}" rx="3" ry="7" fill="#FFFFFF" opacity="0.8"/>')
    # the old man's watch, ticking on the boards
    wx, wy = 470, 488
    out.append(cast(D, wx + 4, wy + 6, 30, 26, "#000000", 0.5))
    out.append(f'<circle cx="{wx}" cy="{wy}" r="25" fill="{gilt_fill(D, wy - 25, wy + 25)}"/>')
    out.append(f'<circle cx="{wx}" cy="{wy}" r="19" fill="#FFF6E0"/>')
    for j in range(12):
        a = math.radians(j * 30)
        out.append(f'<path d="M {wx + math.cos(a) * 15:.1f} {wy + math.sin(a) * 15:.1f} L {wx + math.cos(a) * 18:.1f} {wy + math.sin(a) * 18:.1f}" stroke="#2A1A0A" stroke-width="1.4"/>')
    out.append(f'<path d="M {wx} {wy} L {wx + 2} {wy - 14} M {wx} {wy} L {wx + 10} {wy + 3}" stroke="#2A1A0A" stroke-width="2" stroke-linecap="round"/>')
    out.append(f'<circle cx="{wx}" cy="{wy - 28}" r="5" fill="none" stroke="#C8963A" stroke-width="2.4"/>')
    out.append(taper(catmull([(wx + 3, wy - 32), (wx + 20, wy - 60), (wx + 60, wy - 50), (wx + 80, wy - 80)], 6), 2.2, 2.2, "#C8963A", 0.9))
    out.append(vignette(D, "#000000", 0.75))
    # lettering: the cry, growing
    for (yy, size, ls_, depth) in ((92, 40, 10, 4), (146, 54, 9, 5), (214, 76, 8, 7)):
        out.append(block(D, 300, yy, "LOUDER!", ANTON, size, "#FFE8D0", "#7A0A0A", depth=depth, ang=(0.6, 1.0), ls=ls_, max_w=440, face2="#F2B8A0", shadow="#000000"))
    out.append(sub_rule(300, 548, "THE TELL-TALE HEART · POE · 1843", CINZEL, 17, "#F2D8C0", ls=2, max_w=420, line="#FF7A5A", line_w=22))
    return fin(D, out, 21)


# ================================================================ 11. the pit and the pendulum — the crescent swinging lower
def smile_text(D, cx, cy, r, s, font, size, fill, ls=0, extra="", max_w=None):
    """Text set along the bottom of a circle centred (cx, cy), reading left to right, upright."""
    uid = D.nid()
    fs = fit_size(s, font, size, max_w, ls) if max_w else size
    W = measure(s, font, fs, ls)
    span = W / r + 0.5
    a0, a1 = math.pi / 2 + span / 2, math.pi / 2 - span / 2
    d = f"M {cx + math.cos(a0) * r:.1f} {cy + math.sin(a0) * r:.1f} A {r} {r} 0 0 0 {cx + math.cos(a1) * r:.1f} {cy + math.sin(a1) * r:.1f}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    D.defs.append(f'<path id="{uid}" d="{d}"/>')
    return f'<text {font} font-size="{fs}"{lsa} fill="{fill}"{extra}><textPath href="#{uid}" startOffset="50%" text-anchor="middle">{esc(s)}</textPath></text>'


def crescent_blade(D, px, py, L, ang, w, seed, ghost=False):
    """The pendulum: a long iron rod from the pivot and a great steel crescent at its end. ang in degrees from vertical."""
    a = math.radians(ang)
    bx, by = px + math.sin(a) * L, py + math.cos(a) * L
    out = []
    op = 0.18 if ghost else 1.0
    rod_col = "#1A1410"
    out.append(f'<path d="M {px:.1f} {py:.1f} L {bx:.1f} {by:.1f}" stroke="{rod_col}" stroke-width="{5 if not ghost else 4}" opacity="{op}"/>')
    # crescent in local coords: horns up, the razor edge a deep curve below, the rod fixed at the inner curve
    loc = [(t * w, 34 - 52 * t * t) for t in [-1 + 2 * i / 24 for i in range(25)]]
    loc += [(t * w * 0.94, 8 - 26 * t * t) for t in [1 - 2 * i / 24 for i in range(25)]]
    pts = T(loc, bx, by, 1.0, False, -ang)
    if ghost:
        out.append(f'<path d="{pd(pts)}" fill="#C8D0D8" opacity="{op}"/>')
        return "".join(out)
    out.append(f'<path d="{pd(pts)}" fill="{D.lin([(0, "#5A6068"), (0.45, "#C8D0D8"), (0.7, "#FFFFFF"), (1, "#7A8088")], 0, 0, 0, 1)}"/>')
    edge = T([(t * w, 34 - 52 * t * t) for t in [-1 + 2 * i / 24 for i in range(25)]], bx, by, 1.0, False, -ang)
    out.append(taper(edge, 1.4, 1.4, "#FFFFFF", 0.9))
    out.append(ink(pd(pts), "#14181E", 1.6, seed, 1, 0.9))
    out.append(f'<circle cx="{bx:.1f}" cy="{by + 4:.1f}" r="7" fill="#2A2420" stroke="#8A7A6A" stroke-width="1.6"/>')
    out.append(sparkle(*T([(w * 0.45, 34 - 52 * 0.2)], bx, by, 1.0, False, -ang)[0], 10, "#FFFFFF", 0.95))
    return "".join(out)


def rat(x, y, s, col="#0A0806", eye="#FF4A2A", flip=False):
    def L(pts):
        return T(pts, x, y, s, flip)
    out = [poly(L([(-20, 0), (-18, -8), (-8, -13), (6, -12), (14, -8), (22, -4), (26, -1), (20, 2), (4, 2)]), col)]
    out.append(f'<path d="{blob(*L([(4, -14)])[0], 3 * s, 3 * s, 2, 0.1, 8)}" fill="{col}"/>')
    out.append(taper(catmull(L([(-20, -2), (-34, 0), (-44, -6), (-52, -4)]), 4), 3 * s, 0.8, col))
    ex, ey = L([(18, -6)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.8 * s:.1f}" fill="{eye}"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5 * s:.1f}" fill="{eye}" opacity="0.2"/>')
    return "".join(out)


@design("the-pit-and-the-pendulum")
def the_pit_and_the_pendulum():
    D = Doc2("hr-pp")
    out = [f'<rect width="600" height="600" fill="#0E0C08"/>']
    # the dungeon: walls of iron-grey stone in a dim sulphurous light
    out.append(f'<rect width="600" height="420" fill="{D.rad([(0, "#6A6438"), (0.5, "#2E2A1A"), (1, "#0A0806")], 0.5, 0.55, 0.75)}"/>')
    out.append(stone_courses([20 + k * 34 for k in range(12)], lambda y: -10, 610, "#0A0806", 2, 0.55, 3, unit=70))
    out.append(stone_courses([22.5 + k * 34 for k in range(12)], lambda y: -10, 610, "#A8A070", 1, 0.18, 3, joints=False))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 420 L -10 420 Z", (-20, -10, 610, 420), ["#8A8458", "#14120A", "#4A462A"], 4, n=140, angle=-90, length=(20, 70), width=(3, 8), opacity=(0.08, 0.25)))
    # the floor, receding, and the black pit at its centre
    out.append(f'<path d="M -10 420 L 610 420 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#2A2618"), (1, "#0A0806")])}"/>')
    for k in range(8):
        y = 420 + k * k * 3.2
        out.append(f'<path d="M -10 {y:.1f} L 610 {y:.1f}" stroke="#0A0806" stroke-width="1.6" opacity="0.6"/>')
    for k in range(-6, 7):
        out.append(f'<path d="M {300 + k * 46} 420 L {300 + k * 120} 610" stroke="#0A0806" stroke-width="1.4" opacity="0.5"/>')
    out.append(f'<path d="{blob(300, 448, 170, 40, 3, 0.03, 30)}" fill="#6A6440" opacity="0.5"/>')
    out.append(f'<path d="{blob(300, 450, 156, 34, 4, 0.03, 30)}" fill="#000000"/>')
    out.append(f'<path d="{blob(300, 454, 120, 22, 5, 0.04, 24)}" fill="{D.rad([(0, "#000000"), (1, "#1A140A")])}"/>')
    for r_ in ((-150, 446), (150, 446), (-100, 420), (100, 420), (-60, 480), (70, 482)):
        out.append(f'<path d="{blob(300 + r_[0], r_[1], 14, 6, int(r_[0]), 0.2, 10)}" fill="#3A3420" opacity="0.8"/>')
    # rats at the brink, eyes catching the light
    out.append(rat(124, 440, 1.1))
    out.append(rat(482, 436, 1.0, flip=True))
    out.append(rat(410, 484, 0.9, flip=True))
    # the pendulum: ghosts of its swing, then the blade at the right of its arc
    px, py, L_ = 300, -90, 400
    for a_ in (-20, -12, -4):
        out.append(crescent_blade(D, px, py, L_, a_, 84, 5, ghost=True))
    for k, arc_r in enumerate((L_ + 38, L_ + 30, L_ + 22)):
        out.append(f'<path d="M {px + math.sin(math.radians(-24)) * arc_r:.1f} {py + math.cos(math.radians(-24)) * arc_r:.1f} A {arc_r} {arc_r} 0 0 0 {px + math.sin(math.radians(8)) * arc_r:.1f} {py + math.cos(math.radians(8)) * arc_r:.1f}" '
                   f'fill="none" stroke="#E8E2C8" stroke-width="{2.4 - k * 0.6:.1f}" stroke-linecap="round" opacity="{0.35 - k * 0.08:.2f}"/>')
    out.append(crescent_blade(D, px, py, L_, 12, 84, 6))
    out.append(vignette(D, "#000000", 0.7))
    # lettering: the title swings on an arc like the blade
    out.append(tx(300, 84, "EDGAR ALLAN POE · 1842", CINZEL, 18, "#E8E2C0", ls=5, max_w=360))
    out.append(smile_text(D, 300, -100, 640, "THE PIT AND THE PENDULUM", ANTON, 38, "#000000", ls=4, extra=' opacity="0.7" transform="translate(2 3)"'))
    out.append(smile_text(D, 300, -100, 640, "THE PIT AND THE PENDULUM", ANTON, 38, gilt_fill(D, 500, 545, "silver"), ls=4))
    return fin(D, out, 22)


# ================================================================ 12. the picture of dorian gray — the covered portrait in the old schoolroom
@design("the-picture-of-dorian-gray")
def the_picture_of_dorian_gray():
    D = Doc2("hr-dg")
    out = [f'<rect width="600" height="600" fill="#140C12"/>']
    # faded wallpaper of the locked schoolroom, damp-stained
    out.append(f'<rect width="600" height="460" fill="{D.lin([(0, "#3A2A34"), (1, "#24161E")])}"/>')
    rnd = random.Random(3)
    for r_ in range(9):
        for c in range(8):
            x, y = c * 80 + (r_ % 2) * 40, r_ * 56
            out.append(f'<path d="M {x} {y - 12} Q {x + 10} {y} {x} {y + 12} Q {x - 10} {y} {x} {y - 12} Z" fill="#6A4A58" opacity="0.25"/>')
    out.append(f'<path d="{blob(520, 120, 90, 140, 3, 0.25, 16)}" fill="#1A0E14" opacity="0.4"/>')
    # the great gilt frame, its canvas hidden under the purple satin coverlet
    fx0, fy0, fx1, fy1 = 166, 146, 434, 458
    out.append(cast(D, 314, 300, 190, 210, "#000000", 0.6, 2))
    out.append(f'<rect x="{fx0}" y="{fy0}" width="{fx1 - fx0}" height="{fy1 - fy0}" fill="{gilt_fill(D, fy0, fy1)}"/>')
    out.append(f'<rect x="{fx0 + 14}" y="{fy0 + 14}" width="{fx1 - fx0 - 28}" height="{fy1 - fy0 - 28}" fill="none" stroke="#6A4A14" stroke-width="3"/>')
    for k in range(36):
        t = k / 36
        for (ax, ay, bx, by) in ((fx0 + 7, fy0 + 7, fx1 - 7, fy0 + 7), (fx0 + 7, fy1 - 7, fx1 - 7, fy1 - 7)):
            out.append(f'<circle cx="{ax + (bx - ax) * t:.1f}" cy="{ay:.1f}" r="2.2" fill="#FFF0B0" opacity="0.7"/>')
    for (cx, cy) in ((fx0, fy0), (fx1, fy0), (fx0, fy1), (fx1, fy1)):
        out.append(f'<path d="{blob(cx, cy, 20, 20, int(cx + cy), 0.25, 12)}" fill="{gilt_fill(D, cy - 20, cy + 20)}"/>')
        out.append(ink(blob(cx, cy, 20, 20, int(cx + cy), 0.25, 12), "#5A3A0A", 1.4, 3, 1, 0.8))
    # the canvas itself, glimpsed under the lifted corner: something sickly glows there
    cx0, cy0, cx1, cy1 = fx0 + 22, fy0 + 22, fx1 - 22, fy1 - 22
    out.append(f'<rect x="{cx0}" y="{cy0}" width="{cx1 - cx0}" height="{cy1 - cy0}" fill="#0A0806"/>')
    out.append(soft_glow(D, cx1 - 40, cy1 - 30, 90, "#9AE07A", 0.45))
    # the coverlet: heavy folds, gold embroidery, the bottom right corner caught up
    cov = [(fx0 - 6, fy0 - 10), (fx1 + 8, fy0 - 10), (fx1 + 12, fy1 - 140), (fx1 - 30, fy1 - 92), (fx1 - 70, fy1 - 64), (fx1 - 110, fy1 - 20), (fx1 - 150, fy1 + 10),
           (fx0 + 40, fy1 + 26), (fx0 - 10, fy1 + 18)]
    cpal = ("#8A5AA0", "#4A2460", "#1A0A26")
    out.append(painted(D, cov, cpal, 4, sdir=(0.6, 0.3), sk=0.12, angle=-90, n=80, inkw=1.6, inkc="#0A0410", hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(cov)}"/>')
    folds = []
    for k in range(7):
        x = fx0 + 20 + k * 42 + rnd.uniform(-6, 6)
        g = D.lin([(0, "#1A0A26", 0.6), (0.4, "#B88AD0", 0.4), (0.6, "#6A3A80", 0.1), (1, "#1A0A26", 0.6)], 0, 0, 1, 0)
        folds.append(f'<path d="M {x - 18:.1f} {fy0 - 10} Q {x - 8:.1f} {(fy0 + fy1) / 2:.1f} {x - 24 - k * 3:.1f} {fy1 + 30} L {x + 18 - k * 3:.1f} {fy1 + 30} Q {x + 10:.1f} {(fy0 + fy1) / 2:.1f} {x + 18:.1f} {fy0 - 10} Z" fill="{g}"/>')
    for r_ in range(9):
        for c in range(7):
            x = fx0 + 14 + c * 44 + (r_ % 2) * 22
            y = fy0 + 18 + r_ * 42
            folds.append(f'<path d="M {x} {y - 6} L {x + 6} {y} L {x} {y + 6} L {x - 6} {y} Z" fill="#E8C060" opacity="0.75"/>')
            folds.append(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#4A2460"/>')
    folds.append(f'<path d="{pd([(fx0 - 10, fy0 + 26), (fx1 + 10, fy0 + 26)], False)}" stroke="#E8C060" stroke-width="2" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(folds)}</g>')
    out.append(taper(catmull([(fx1 + 12, fy1 - 140), (fx1 - 30, fy1 - 92), (fx1 - 70, fy1 - 64), (fx1 - 110, fy1 - 20), (fx1 - 150, fy1 + 10)], 6), 3, 3, "#C8A0E0", 0.6))
    # gold tassels on the corners
    for (tx_, ty_) in ((fx0 + 2, fy1 + 20), (fx1 - 150, fy1 + 12)):
        out.append(taper([(tx_, ty_), (tx_ + 1, ty_ + 22)], 7, 3, "#D8A845"))
        out.append(f'<circle cx="{tx_}" cy="{ty_}" r="5" fill="#E8C060"/>')
    # the floor, a little table with a candle and a dropped key
    out.append(f'<rect x="-10" y="460" width="620" height="150" fill="{D.lin([(0, "#2A1A14"), (1, "#0A0604")])}"/>')
    out.append(strokes(D.nid(), "M -10 460 L 610 460 L 610 610 L -10 610 Z", (-40, 460, 610, 610), ["#4A3020", "#0A0604"], 5, n=50, angle=0, length=(60, 160), width=(2, 4), opacity=(0.15, 0.35)))
    out.append(candle(D, 506, 500, 56, 7, w=14, glow_r=150))
    out.append(soft_glow(D, 470, 300, 260, "#FFB060", 0.18))
    out.append(taper(catmull([(116, 520), (140, 514), (152, 516)], 4), 3, 3, "#C8963A"))
    out.append(f'<circle cx="110" cy="521" r="7" fill="none" stroke="#C8963A" stroke-width="3"/>')
    out.append(sharp([(146, 516), (152, 524), (156, 522), (152, 514)], "#C8963A"))
    out.append(vignette(D, "#000000", 0.6))
    # lettering
    out.append(tx(300, 76, "THE PICTURE OF", CINZEL, 21, "#E8D0F0", ls=6, max_w=300))
    out.append(letters(D, 300, 548, "Dorian Gray", SERIF_IT, 70, "#F6E6C8", ["#FFFFFF", "#F2D8A0", "#E8C8F0"], 14, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(tx(300, 100, "OSCAR WILDE · 1890", JOST, 16, "#C8A8D8", ls=4, max_w=300))
    return fin(D, out, 23)


# ================================================================ 13. the invisible man — hat, blue spectacles, bandages and nobody
@design("the-invisible-man")
def the_invisible_man():
    D = Doc2("hr-im")
    out = [f'<rect width="600" height="600" fill="#1A1410"/>']
    # the inn parlour: plaster wall, a sash window full of falling snow, a dim fire to the right
    out.append(f'<rect width="600" height="430" fill="{D.lin([(0, "#4A3A2A"), (1, "#3A2C20")])}"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 430 L 0 430 Z", (0, 0, 600, 430), ["#5A4A36", "#2A1E14", "#6A5A42"], 3, n=100, angle=-90, length=(30, 90), width=(3, 8), opacity=(0.1, 0.25)))
    wx0, wy0, wx1, wy1 = 60, 150, 196, 340
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#2A3A5A"), (1, "#6A7A98")])}"/>')
    wc = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    out.append(f'<g {wc}>{snowfall(3, (wx0, wy0, wx1, wy1), 60, (0.8, 2.4), "#FFFFFF", (0.5, 1))}'
               f'<path d="M {wx0} {wy1 - 20} Q {wx0 + 60} {wy1 - 34} {wx1} {wy1 - 24} L {wx1} {wy1} L {wx0} {wy1} Z" fill="#E8F0FF"/></g>')
    for xx in ((wx0 + wx1) / 2,):
        out.append(f'<path d="M {xx} {wy0} L {xx} {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#2A1E14" stroke-width="5"/>')
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="none" stroke="#2A1E14" stroke-width="9"/>')
    out.append(soft_glow(D, 600, 420, 300, "#FF8A3A", 0.35))
    # table and the empty chair
    out.append(f'<rect x="-10" y="430" width="620" height="180" fill="{D.lin([(0, "#2A1E14"), (1, "#0E0A06")])}"/>')
    chair = ("#7A4E2C", "#4A2E18", "#1E1008")
    out.append(painted(D, poly_pts([(244, 250), (356, 250), (350, 266), (250, 266)], 10, 1, 0.4), chair, 3, sdir=(0.6, 0.6), sk=0.2, angle=0, n=10, inkw=1.4, inkc="#140A04", hi=0.4))
    for x in (258, 342):
        out.append(painted(D, poly_pts([(x - 6, 262), (x + 6, 262), (x + 6, 440), (x - 6, 440)], 12, x, 0.4), chair, x, sdir=(0.6, 0.2), sk=0.2, angle=-90, n=8, inkw=1.2, inkc="#140A04", hi=0.4))
    for k in range(4):
        out.append(painted(D, poly_pts([(266 + k * 20, 266), (274 + k * 20, 266), (274 + k * 20, 360), (266 + k * 20, 360)], 10, k, 0.4), chair, 20 + k, sdir=(0.6, 0.2), sk=0.2, angle=-90, n=4, inkw=1, inkc="#140A04", hi=0.4))
    out.append(painted(D, poly_pts([(232, 372), (368, 372), (380, 392), (220, 392)], 14, 4, 0.4), chair, 30, sdir=(0, 1), sk=0.2, angle=0, n=12, inkw=1.4, inkc="#140A04", hi=0.45))
    for x in (230, 370):
        out.append(taper([(x, 392), (x + (6 if x > 300 else -6), 470)], 9, 7, chair[2]))
    # the coat, upright on the chair, collar turned up round nothing
    coat = [(246, 384), (250, 300), (262, 252), (284, 236), (300, 244), (316, 236), (338, 252), (350, 300), (354, 384)]
    out.append(painted(D, coat, ("#5A6A80", "#2A3446", "#0E141E"), 5, sdir=(0.6, 0.3), sk=0.18, angle=-90, n=40, inkw=1.6, inkc="#06080E", hi=0.35))
    for sg in (-1, 1):
        sleeve = [(300 + sg * 34, 256), (300 + sg * 52, 290), (300 + sg * 60, 340), (300 + sg * 58, 372), (300 + sg * 44, 374), (300 + sg * 40, 330), (300 + sg * 30, 290)]
        out.append(painted(D, sleeve, ("#5A6A80", "#2A3446", "#0E141E"), 40 + sg, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=12, inkw=1.4, inkc="#06080E", hi=0.3))
        out.append(f'<path d="{blob(300 + sg * 51, 372, 9, 4, 3 + sg, 0.1, 8)}" fill="#0A0A0E"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{smooth_closed([(300, 258), (300 + sg * 22, 250), (300 + sg * 16, 300), (300 + sg * 4, 320)])}" fill="#3A4658"/>')
    out.append(f'<path d="{smooth_closed([(272, 246), (284, 210), (300, 216), (316, 210), (328, 246), (300, 256)])}" fill="#3A4658"/>')
    out.append(f'<path d="{smooth_closed([(282, 240), (290, 218), (300, 222), (310, 218), (318, 240), (300, 246)])}" fill="#0A0A0E"/>')
    for k in range(4):
        out.append(f'<circle cx="300" cy="{280 + k * 24}" r="3.2" fill="#C8B080"/>')
    out.append(pline([(300, 256), (300, 384)], "#0E141E", 1.4, 3, 0.7, 1))
    # the bandage unwinding in mid-air where the head should be
    bpath = [(300, 214), (270, 200), (262, 176), (290, 164), (328, 170), (334, 150), (300, 136), (262, 140), (248, 120), (278, 108), (330, 112)]
    pts_ = catmull(bpath, 8)
    out.append(taper(pts_, 16, 12, "#F2ECDC"))
    out.append(taper([(x, y + 3) for x, y in pts_], 6, 4, "#B8AE98", 0.6))
    for k in range(0, len(pts_) - 1, 4):
        x, y = pts_[k]
        out.append(f'<path d="M {x - 5:.1f} {y - 4:.1f} L {x + 5:.1f} {y + 4:.1f}" stroke="#C8BEA8" stroke-width="1" opacity="0.7"/>')
    out.append(ink(smooth_open(pts_), "#6A5E48", 1.2, 4, 1, 0.5))
    # the blue spectacles, floating at eye height
    sy = 178
    for sg in (-1, 1):
        out.append(f'<circle cx="{300 + sg * 18}" cy="{sy}" r="13" fill="{D.rad([(0, "#5A8AD8"), (1, "#0E1E4A")], 0.35, 0.35, 0.7)}" stroke="#C8B080" stroke-width="2.4"/>')
        out.append(f'<circle cx="{300 + sg * 18 - 4}" cy="{sy - 4}" r="3" fill="#FFFFFF" opacity="0.7"/>')
        out.append(f'<path d="M {300 + sg * 31} {sy - 2} L {300 + sg * 46} {sy - 8}" stroke="#C8B080" stroke-width="2"/>')
    out.append(f'<path d="M 295 {sy - 2} Q 300 {sy - 7} 305 {sy - 2}" stroke="#C8B080" stroke-width="2.2" fill="none"/>')
    # the hat, hovering above
    hat_y = 92
    out.append(painted(D, ell_pts(300, hat_y + 30, 62, 12, 0, 360, 28), ("#6A5A4A", "#3A2E24", "#140E0A"), 6, sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.4, inkc="#0A0604", hi=0.4))
    out.append(painted(D, [(258, hat_y + 30), (262, hat_y + 4), (280, hat_y - 10), (300, hat_y - 4), (320, hat_y - 10), (338, hat_y + 4), (342, hat_y + 30)], ("#7A6A58", "#3E3226", "#140E0A"), 7, sdir=(0.6, 0.4), sk=0.2, angle=-90, n=12, inkw=1.4, inkc="#0A0604", hi=0.45))
    out.append(f'<path d="M 260 {hat_y + 22} Q 300 {hat_y + 28} 340 {hat_y + 22} L 341 {hat_y + 28} Q 300 {hat_y + 34} 259 {hat_y + 28} Z" fill="#1A120C"/>')
    # a floating glove lifting a cup of tea
    gx, gy = 404, 300
    out.append(painted(D, [(gx - 18, gy + 20), (gx - 20, gy - 4), (gx - 12, gy - 16), (gx + 6, gy - 18), (gx + 18, gy - 8), (gx + 16, gy + 20)], ("#E8D8B8", "#B8A07A", "#5A4A30"), 8, sdir=(0.6, 0.6), sk=0.2, n=8, inkw=1.2, inkc="#2A1E10", hi=0.4))
    out.append(painted(D, poly_pts([(gx - 22, gy - 34), (gx + 22, gy - 34), (gx + 16, gy - 8), (gx - 16, gy - 8)], 8, 3, 0.4), ("#FFFFFF", "#E8E4DA", "#9A9488"), 9, sdir=(0.6, 0.6), sk=0.2, n=8, inkw=1.2, inkc="#3A3428", hi=0.4))
    out.append(f'<path d="M {gx + 21} {gy - 28} q 12 2 8 14 q -3 6 -10 4" fill="none" stroke="#E8E4DA" stroke-width="3"/>')
    out.append(steam_lines(gx, gy - 42, 3))
    out.append(band(D, 0, 200, "#000000", 0.4, 0))
    out.append(vignette(D, "#000000", 0.6))
    # lettering: the middle word is there, and it isn't
    t = "THE INVISIBLE MAN"
    fs = _fit(t, ANTON, 64, 460, 3)
    W = measure(t, ANTON, fs, 3)
    w1 = measure("THE ", ANTON, fs, 3) + 3
    w2 = measure("INVISIBLE ", ANTON, fs, 3) + 3
    x0 = 300 - W / 2
    out.append(_t(x0 + 2, 528 + 3, "THE", ANTON, fs, "#000000", 3, "start", ' opacity="0.6"'))
    out.append(_t(x0 + w1 + w2 + 2, 528 + 3, "MAN", ANTON, fs, "#000000", 3, "start", ' opacity="0.6"'))
    out.append(_t(x0, 528, "THE", ANTON, fs, "#F2E8D8", 3, "start"))
    out.append(_t(x0 + w1, 528, "INVISIBLE", ANTON, fs, "none", 3, "start", ' stroke="#F2E8D8" stroke-width="1.8" stroke-dasharray="6 4" opacity="0.9"'))
    out.append(_t(x0 + w1 + w2, 528, "MAN", ANTON, fs, "#F2E8D8", 3, "start"))
    out.append(sub_rule(300, 548, "H. G. WELLS · 1897", JOST, 16, "#C8B898", ls=4, max_w=300))
    return fin(D, out, 24)


def steam_lines(x, y, seed, col="#FFFFFF"):
    rnd = random.Random(seed)
    out = []
    for k in (-8, 0, 8):
        out.append(taper(catmull([(x + k, y), (x + k - 5, y - 10), (x + k + 4, y - 20), (x + k - 2, y - 30)], 5), 2.4, 0.6, col, 0.5))
    return "".join(out)


# ================================================================ 14. the hound of the baskervilles — out of the fog on the moor
@design("the-hound-of-the-baskervilles")
def the_hound_of_the_baskervilles():
    D = Doc2("hr-hb")
    out = [night(D, [(0, "#04080A"), (0.4, "#14242A"), (0.7, "#3A4A48"), (1, "#14201E")], 1)]
    out.append(stars_field(3, (0, 0, 600, 300), 60))
    out.append(moon(D, 452, 268, 58, 4, pal=("#FFFCEC", "#E8E8D8", "#B8BCAA"), glow="#DCF2E8", gs=0.5, glow_r=3.0))
    out.append(puff_cloud(D, 180, 250, 260, 5, ("#4A5A58", "#24302E", "#0A1210"), op=0.85))
    # the moor: low rolling land, Baskerville Hall far off with two lit windows
    out.append(hill(D, ridge([(-20, 380), (100, 360), (220, 372), (340, 352), (460, 366), (620, 350)], 3, 6, 4), 640, ("#3A4A40", "#1E2A24", "#0A100C"), 2, inkw=0, n=40))
    hx = 120
    out.append(poly([(hx - 30, 366), (hx - 30, 340), (hx - 14, 330), (hx + 10, 330), (hx + 26, 340), (hx + 26, 366)], "#0A0E0C"))
    for tx_ in (hx - 30, hx + 26):
        out.append(sharp([(tx_ - 6, 366), (tx_ - 6, 322), (tx_, 314), (tx_ + 6, 322), (tx_ + 6, 366)], "#0A0E0C"))
    for wx in (hx - 10, hx + 6):
        out.append(lit_slit(D, wx, 342, 4, 9, "#FFC860"))
    out.append(fog(D, 372, 44, 4, "#B8C8C0", 0.55))
    # a granite tor on the right, the hound bounding down from it
    tor = [(360, 470), (380, 400), (410, 372), (440, 360), (470, 366), (500, 352), (540, 360), (570, 390), (610, 400), (620, 480)]
    out.append(painted(D, poly_pts(tor, 18, 5, 2), ("#7A8478", "#3A443C", "#121814"), 6, sdir=(-0.7, 0.4), sk=0.2, angle=0, n=60, inkw=1.6, inkc="#060A08", hi=0.45))
    for k in range(5):
        y = 380 + k * 18
        out.append(pline([(390 + k * 6, y), (480, y + 4), (600, y - 2)], "#0E1410", 1.6, k, 0.6, 1))
    out.append(hill(D, ridge([(-20, 452), (120, 440), (260, 456), (400, 444), (620, 460)], 6, 6, 4), 640, ("#3A4438", "#1A221C", "#060A08"), 7, inkw=0, n=40))
    out.append(grass(8, (-10, 446, 610, 600), ["#2A3A2A", "#4A5A40", "#0E140E"], 160, (8, 22)))
    # the hound: huge, black, its muzzle and hackles outlined in pale flame
    out.append(soft_glow(D, 300, 380, 170, "#7AF0C8", 0.22))
    hp = ("#2A2E30", "#0A0C0E", "#000000")
    hound = canine_leap(D, 330, 478, 1.12, 7, hp, rim="#B8FFE8")
    out.append(hound)
    out.append(fog(D, 470, 60, 8, "#A8B8B0", 0.5))
    out.append(fog(D, 540, 70, 9, "#8A9A94", 0.4))
    out.append(band(D, 0, 200, "#000000", 0.55, 0))
    # lettering: the pulp cover title
    out.append(block(D, 300, 128, "THE HOUND", ANTON, 92, "#F2F8E8", "#1E5A48", depth=8, ang=(0.7, 1.0), ls=6, max_w=440, face2="#B8E8D0", shadow="#000000"))
    out.append(tx(300, 172, "of the Baskervilles", SERIF_IT, 36, "#D8F2E8", max_w=360))
    out.append(sub_rule(300, 548, "ARTHUR CONAN DOYLE · 1902", CINZEL, 17, "#D8F2E8", ls=2.5, max_w=380, line="#7AF0C8", line_w=24))
    return fin(D, out, 25)


def canine_leap(D, x, y, s, seed, pal, rim):
    """A huge hound in mid-bound (facing left): deep chest, heavy neck and head, forelegs reaching, hind legs
    driving, hackles up, jaws open. (x, y) ~ under the belly."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    far = dk(pal[1], 0.35)
    out.append(taper(catmull(L([(-50, -60), (-80, -40), (-112, -30), (-128, -34)]), 5), 22 * s, 9 * s, far))
    out.append(taper(catmull(L([(54, -70), (78, -44), (110, -26), (132, -24)]), 5), 26 * s, 9 * s, far))
    # tail
    out.append(taper(catmull(L([(66, -104), (96, -112), (124, -106), (146, -114)]), 6), 14 * s, 4 * s, pal[1]))
    # body: deep chest, tucked waist, powerful haunch
    body = L([(-80, -112), (-50, -124), (-10, -118), (30, -114), (66, -116), (84, -100), (82, -74), (64, -60), (36, -64), (10, -66), (-20, -54),
              (-50, -46), (-72, -56), (-86, -76)])
    out.append(painted(D, body, pal, seed, sdir=(0.3, 0.8), sk=0.2, angle=-8, n=50, inkw=1.4, inkc="#000000", hi=0.3))
    # heavy neck and the great square head thrust forward, jaws open
    neck = L([(-74, -110), (-96, -128), (-108, -134), (-120, -132), (-108, -100), (-86, -74)])
    out.append(poly(neck, pal[1]))
    head = L([(-104, -134), (-118, -146), (-136, -148), (-152, -142), (-174, -134), (-178, -126), (-170, -122), (-150, -122), (-138, -118),
              (-166, -110), (-172, -102), (-160, -98), (-136, -100), (-116, -100), (-104, -112)])
    out.append(poly(head, pal[1]))
    out.append(poly(L([(-118, -142), (-112, -162), (-104, -142)]), pal[1]))
    out.append(poly(L([(-126, -144), (-122, -160), (-116, -144)]), pal[2]))
    # fire in the jaws, the smouldering eye
    mx, my = L([(-158, -114)])[0]
    out.append(soft_glow(D, mx, my, 30 * s, "#9AFFD8", 0.6))
    out.append(sharp(L([(-138, -120), (-168, -120), (-166, -112), (-138, -110)]), "#C8FFE8"))
    for k in range(5):
        out.append(sharp(L([(-164 + k * 5, -121), (-162 + k * 5, -116), (-160 + k * 5, -121)]), "#FFFFFF"))
        out.append(sharp(L([(-162 + k * 5, -109), (-160 + k * 5, -114), (-158 + k * 5, -109)]), "#FFFFFF"))
    ex, ey = L([(-140, -136)])[0]
    out.append(soft_glow(D, ex, ey, 16 * s, "#E8FF8A", 0.9))
    out.append(f'<path d="{blob(ex, ey, 4 * s, 2.4 * s, seed, 0.05, 8, -8)}" fill="#F8FFB0"/>')
    # near legs: thick, reaching and driving
    out.append(taper(catmull(L([(-60, -62), (-92, -50), (-126, -46), (-146, -52)]), 5), 24 * s, 10 * s, pal[1]))
    out.append(f'<path d="{blob(*L([(-148, -50)])[0], 8 * s, 5 * s, seed + 3, 0.1, 8, -10)}" fill="{pal[1]}"/>')
    out.append(taper(catmull(L([(60, -76), (76, -44), (108, -20), (140, -14)]), 5), 28 * s, 10 * s, pal[1]))
    out.append(f'<path d="{blob(*L([(142, -14)])[0], 9 * s, 5 * s, seed + 4, 0.1, 8, 10)}" fill="{pal[1]}"/>')
    # hackles bristling along neck and back
    rnd = random.Random(seed)
    for k in range(18):
        t = k / 17
        bx, by = L([(-104 + t * 140, -134 + 14 * t - 4 * math.sin(t * math.pi))])[0]
        out.append(taper([(bx, by + 5), (bx + rnd.uniform(0, 5), by - rnd.uniform(6, 13) * s)], 5 * s, 0.6, pal[1]))
    # the spectral flame along muzzle, hackles and dewlap
    edge = L([(-178, -128), (-174, -134), (-152, -142), (-136, -148), (-118, -146), (-104, -138), (-80, -126), (-50, -128), (-10, -122), (30, -118), (66, -118)])
    out.append(taper(edge, 7, 2, rim, 0.35))
    out.append(taper(edge, 2.6, 1, "#FFFFFF", 0.85))
    out.append(taper(L([(-172, -102), (-160, -98), (-136, -100), (-116, -96), (-100, -86), (-86, -74)]), 4, 1.6, rim, 0.6))
    for k in range(12):
        bx, by = edge[int(k / 11 * (len(edge) - 1))]
        out.append(f'<path d="M {bx:.1f} {by:.1f} q {rnd.uniform(-3, 3):.1f} -6 {rnd.uniform(-2, 4):.1f} -12" stroke="{rim}" stroke-width="1.6" fill="none" opacity="0.6" stroke-linecap="round"/>')
    return "".join(out)


# ================================================================ 15. the monkey's paw — three wishes on the mantelpiece
def withered_paw(D, cx, cy, s, seed):
    """A small mummified paw lying on its side: furred wrist cuff to the right, leathery palm, long thin fingers
    curling to the left with dark nails. (cx, cy) = the palm."""
    def L(pts):
        return T(pts, cx, cy, s)
    pal = ("#B08A64", "#6E4A2C", "#2A180A")
    out = [cast(D, cx + 4, cy + 12 * s, 46 * s, 5 * s, "#000000", 0.5, seed)]
    # wrist with a cuff of dry fur
    out.append(painted(D, L([(14, -8), (34, -10), (46, -6), (48, 4), (34, 8), (14, 8)]), ("#8A7A5A", "#4A3A24", "#1A120A"), seed + 1, sdir=(0.6, 0.5), sk=0.2, angle=0, n=10, inkw=1, inkc="#1A0E06", hi=0.3))
    rnd = random.Random(seed)
    for k in range(14):
        px, py = L([(rnd.uniform(16, 44), rnd.uniform(-8, 6))])[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-4, -1):.1f} {rnd.uniform(-2, 2):.1f}" stroke="#C8B08A" stroke-width="0.9" opacity="0.7"/>')
    palm = L([(16, -9), (0, -12), (-14, -10), (-20, -2), (-16, 8), (0, 10), (16, 8)])
    out.append(painted(D, palm, pal, seed, sdir=(0.6, 0.5), sk=0.22, angle=0, n=12, inkw=1.2, inkc="#1A0E06", hi=0.4))
    # four fingers reaching left, joints bent; the thumb tucked under
    for k, (fy, L_, curl) in enumerate(((-10, 34, 0.5), (-4, 38, 0.65), (2, 36, 0.8), (7, 30, 1.0))):
        a, b, c = L([(-16, fy), (-16 - L_ * 0.5, fy - 4 + k), (-16 - L_ * 0.5 - L_ * 0.45 * math.cos(curl), fy + L_ * 0.45 * math.sin(curl))])
        out.append(taper([a, b], 6 * s, 4.4 * s, pal[1] if k % 2 else dk(pal[1], 0.1)))
        out.append(taper([b, c], 4.4 * s, 2.6 * s, pal[1] if k % 2 else dk(pal[1], 0.1)))
        out.append(f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="{2.4 * s:.1f}" fill="{pal[0]}" opacity="0.5"/>')
        out.append(f'<path d="{blob(c[0], c[1], 1.8 * s, 1.2 * s, seed + k, 0.1, 8)}" fill="#1A0E06"/>')
        out.append(taper([(a[0], a[1] - 1.5 * s), (b[0], b[1] - 1.5 * s)], 1.6, 1, pal[0], 0.6))
    out.append(taper(L([(0, 9), (-8, 14), (-14, 16)]), 5 * s, 2.6 * s, dk(pal[1], 0.2)))
    return "".join(out)


@design("the-monkeys-paw")
def the_monkeys_paw():
    D = Doc2("hr-mp")
    out = [f'<rect width="600" height="600" fill="#1A0E0A"/>']
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#2E1E1A"), (0.6, "#3A2218"), (1, "#140A06")])}"/>')
    # striped Victorian wallpaper
    for k in range(16):
        out.append(f'<rect x="{k * 40}" y="0" width="14" height="330" fill="#4A2E26" opacity="0.5"/>')
    out.append(soft_glow(D, 300, 450, 360, "#FF8A3A", 0.4))
    # the fireplace: mantel shelf, the hearth glowing below
    out.append(painted(D, poly_pts([(70, 330), (530, 330), (530, 600), (70, 600)], 20, 3, 0.4), ("#8A6A5A", "#4A3428", "#1A0E08"), 3, sdir=(0.6, 0.3), sk=0.12, angle=-90, n=60, inkw=1.4, inkc="#0A0402", hi=0.3))
    out.append(f'<path d="{smooth_closed(arch_pts(170, 430, 440, 610, 8))}" fill="#0A0402"/>')
    out.append(soft_glow(D, 300, 560, 140, "#FF6A1A", 0.8))
    rnd = random.Random(4)
    for k in range(10):
        ex = 220 + k * 18 + rnd.uniform(-6, 6)
        out.append(f'<path d="{blob(ex, 590 + rnd.uniform(-6, 6), rnd.uniform(10, 16), rnd.uniform(6, 9), k, 0.2, 10)}" fill="{rnd.choice(["#FF8A2A", "#E8501A", "#FFC860"])}"/>')
    for k in range(4):
        fx = 250 + k * 34
        out.append(flame_lick(fx, 590, rnd.uniform(36, 60), 14, k))
    out.append(painted(D, poly_pts([(40, 318), (560, 318), (560, 344), (40, 344)], 20, 4, 0.4), ("#B88A6A", "#6A4A34", "#2A180C"), 5, sdir=(0, 1), sk=0.2, angle=0, n=40, inkw=1.6, inkc="#0A0402", hi=0.5))
    out.append(f'<path d="M 40 344 L 560 344 L 552 352 L 48 352 Z" fill="#1A0E06"/>')
    # three candles: two already snuffed and smoking, one still burning
    for k, (cx, lit) in enumerate(((110, False), (164, False), (490, True))):
        out.append(candle(D, cx, 320, 54 - k * 6, 9 + k, w=14, flame=lit, glow_r=110))
        if not lit:
            out.append(smoke(D, [(cx, 260 + k * 6), (cx - 8, 230), (cx + 6, 200), (cx - 4, 168)], 2, 8, k, "#C8B8A8", 0.5))
    # the mantel clock, near midnight
    out.append(painted(D, [(400, 318), (400, 262), (412, 240), (440, 230), (468, 240), (480, 262), (480, 318)], ("#7A4A2A", "#3A2010", "#120804"), 6, sdir=(0.6, 0.3), sk=0.2, n=14, inkw=1.4, inkc="#0A0402", hi=0.4))
    out.append(f'<circle cx="440" cy="270" r="22" fill="#F2E8D2" stroke="#C8963A" stroke-width="3"/>')
    for j in range(12):
        a = math.radians(j * 30)
        out.append(f'<path d="M {440 + math.cos(a) * 16:.1f} {270 + math.sin(a) * 16:.1f} L {440 + math.cos(a) * 20:.1f} {270 + math.sin(a) * 20:.1f}" stroke="#2A1A0A" stroke-width="1.4"/>')
    out.append(f'<path d="M 440 270 L 438 254 M 440 270 L 437 257" stroke="#2A1A0A" stroke-width="2" stroke-linecap="round"/>')
    # the paw under its glass dome, on a velvet cushion
    cx, base = 300, 318
    out.append(painted(D, ell_pts(cx, base - 4, 70, 12, 0, 360, 24), ("#8A6A4A", "#4A3020", "#1A0E06"), 7, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, inkc="#0A0402", hi=0.4))
    out.append(painted(D, [(cx - 54, base - 8), (cx - 50, base - 26), (cx, base - 32), (cx + 50, base - 26), (cx + 54, base - 8), (cx, base - 4)], ("#C84A4A", "#7A1A22", "#3A060A"), 8, sdir=(0.5, 0.6), sk=0.2, n=10, inkw=1.2, inkc="#2A0406", hi=0.45))
    out.append(withered_paw(D, cx + 4, base - 40, 1.45, 9))
    dome = [(cx - 60, base - 8)] + ell_pts(cx, base - 110, 60, 104, 180, 360, 20)[0:] + [(cx + 60, base - 8)]
    dome_d = pd([(cx - 64, base - 8), (cx - 64, base - 80)] + ell_pts(cx, base - 80, 64, 52, 180, 360, 20) + [(cx + 64, base - 80), (cx + 64, base - 8)])
    out.append(f'<path d="{dome_d}" fill="#DCE8F0" opacity="0.1"/>')
    out.append(ink(dome_d, "#E8F2FF", 2.2, 3, 1, 0.55))
    out.append(taper([(cx - 50, base - 20), (cx - 52, base - 86), (cx - 36, base - 120)], 5, 2, "#FFFFFF", 0.4))
    out.append(taper([(cx + 50, base - 30), (cx + 52, base - 80)], 3, 1.6, "#FFFFFF", 0.25))
    out.append(soft_glow(D, cx, base - 40, 40, "#FFB060", 0.25))
    out.append(band(D, 0, 220, "#000000", 0.6, 0))
    # lettering
    out.append(gilt(D, 300, 112, "The Monkey’s Paw", DMS, 66, ls=1, max_w=450, seed=26, deboss="#000000", dop=0.9))
    out.append(tx(300, 150, "Three wishes. Choose carefully.", SERIF_IT, 26, "#F2D8C0", max_w=420))
    out.append(tx(300, 178, "W. W. JACOBS · 1902", JOST, 16, "#C8A890", ls=4, max_w=300))
    return fin(D, out, 26)


# ================================================================ 16. the turn of the screw — the figure on the tower at Bly
def victorian_lady(x, base, s, col, rim=None, flip=False):
    """A governess from behind: small waist, bell skirt, shawl, hair in a bun; about 64*s tall."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-20, 0), (-16, -14), (-10, -30), (-6, -38), (6, -38), (10, -30), (16, -14), (20, 0)]), col)]
    out.append(poly(L([(-6, -38), (-9, -48), (-10, -54), (-4, -58), (4, -58), (10, -54), (9, -48), (6, -38)]), col))
    out.append(f'<path d="{blob(*L([(0, -62)])[0], 4.2 * s, 5 * s, 2, 0.06, 10)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(0, -66)])[0], 3 * s, 2.4 * s, 3, 0.1, 8)}" fill="{col}"/>')
    if rim:
        out.append(ink(smooth_open(L([(4, -66), (5, -58), (10, -54), (9, -48), (10, -30), (16, -14), (20, 0)])), rim, 1.2, 2, 1, 0.75))
    return "".join(out)


@design("the-turn-of-the-screw")
def the_turn_of_the_screw():
    D = Doc2("hr-ts")
    from gouache import paper
    out = [paper(D.nid(), "#2A2030", "#C8A8D8", 6)]
    out.append(vignette(D, "#000000", 0.5))
    # an oval vignette, like an old engraved frontispiece
    cx, cy, rx, ry = 300, 292, 178, 200
    oval = ell_pts(cx, cy, rx, ry, 0, 360, 72)
    cid = D.clip(f'<path d="{smooth_closed(oval)}"/>')
    sc = [sky(D, [(0, "#4A4466"), (0.45, "#8A7A98"), (0.7, "#D8A8A0"), (0.82, "#C8A0A0"), (1, "#3A3446")], 1, 600, ["#5A5478", "#2A2440", "#B8A0B8"], 50)]
    sc.append(soft_glow(D, 200, 380, 170, "#FFD8B8", 0.35))
    # Bly: the old crenellated tower, a long house beside it
    tx0, tx1, ttop, tb = 340, 412, 176, 420
    sc.append(painted(D, poly_pts([(410, tb), (410, 300), (520, 300), (520, tb)], 14, 2, 0.5), ("#6A6078", "#3A3448", "#14101E"), 3, sdir=(0.8, 0.2), sk=0.15, angle=-90, n=30, inkw=1.2, inkc="#0A0810", hi=0.25))
    sc.append(sharp([(404, 304), (466, 262), (526, 304)], "#2A2436"))
    for k in range(3):
        sc.append(lit_slit(D, 432 + k * 32, 326, 8, 16, "#FFC870") if k == 1 else f'<rect x="{428 + k * 32}" y="326" width="9" height="18" fill="#14101E"/>')
    tower = [(tx0, tb), (tx0, ttop + 16), (tx0 - 6, ttop + 16), (tx0 - 6, ttop)] + sum([[(tx0 - 6 + k * 14, ttop), (tx0 - 6 + k * 14, ttop - 12), (tx0 + 3 + k * 14, ttop - 12), (tx0 + 3 + k * 14, ttop)] for k in range(6)], []) + [(tx1 + 6, ttop), (tx1 + 6, ttop + 16), (tx1, ttop + 16), (tx1, tb)]
    sc.append(painted(D, poly_pts(tower, 8, 4, 0.4), ("#7A7088", "#463E56", "#18141F"), 5, sdir=(0.8, 0.2), sk=0.15, angle=-90, n=30, inkw=1.2, inkc="#0A0810", hi=0.25))
    sc.append(stone_courses([ttop + 30 + k * 22 for k in range(11)], lambda y: tx0, tx1, "#14101E", 1.1, 0.35, 5, unit=24))
    sc.append(f'<path d="{smooth_closed(arch_pts(370, 384, 240, 270, 4))}" fill="#14101E"/>')
    # the stranger on the battlements, pale and very still
    sc.append(soft_glow(D, 376, ttop - 28, 34, "#F2E8FF", 0.35))
    sc.append(cloaked(376, ttop - 12, 0.32, "#E8E4F0", hood=False))
    # dark trees, the lawn, the gravel path, the governess stopped on it
    for (x, h, sd) in ((80, 220, 3), (150, 170, 4), (560, 200, 5)):
        sc.append(crooked_tree(x, 430, h, sd, "#1E1A2A", w=9, spread=36, depth=5))
    sc.append(hill(D, [(-20, 420), (200, 414), (420, 418), (620, 412)], 640, ("#8A9A78", "#4E5E46", "#1E281C"), 6, inkw=0, n=40))
    sc.append(f'<path d="M 230 600 Q 270 500 330 422 L 352 422 Q 330 500 360 600 Z" fill="#B8A898" opacity="0.6"/>')
    sc.append(victorian_lady(280, 452, 1.12, "#141020", rim="#FFD8B8"))
    sc.append(cast(D, 285, 454, 26, 4, "#000000", 0.4))
    for (bx, by, bs) in ((210, 150, 0.6), (240, 136, 0.45), (480, 190, 0.5), (182, 172, 0.4)):
        sc.append(bird_v(bx, by, bs * 10, "#1A1428"))
    sc.append(f'<path d="{smooth_closed(oval)}" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.45)])}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # the frame: a gilt double ring with tiny beads, fleurons at the corners of the plate
    out.append(ink(smooth_closed(oval), "#D8B060", 3, 2, 1, 0.95))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx + 11, ry + 11, 0, 360, 72)), "#D8B060", 1.4, 3, 1, 0.8))
    for k in range(52):
        a = 2 * math.pi * k / 52
        out.append(f'<circle cx="{cx + math.cos(a) * (rx + 5.5):.1f}" cy="{cy + math.sin(a) * (ry + 5.5):.1f}" r="1.7" fill="#E8C878"/>')
    for (x, y, r_) in ((92, 92, 135), (508, 92, 225), (92, 508, 45), (508, 508, -45)):
        out.append(fleuron(x, y, 18, "#D8B060", r_, 0.9))
    # lettering
    out.append(tx(300, 540, "The Turn of the Screw", SERIF_IT, 40, "#F2E2F2", max_w=420))
    out.append(tx(300, 70, "HENRY JAMES · 1898", CINZEL, 17, "#D8B8E0", ls=5, max_w=300))
    return fin(D, out, 27, "#2A1E36", 0.6)


def bird_v(x, y, s, col):
    return (pline([(x - s, y), (x - s * 0.5, y - s * 0.45), (x, y)], col, max(1.4, s * 0.18), int(x), 0.9, 1) +
            pline([(x, y), (x + s * 0.5, y - s * 0.5), (x + s, y + 0.5)], col, max(1.4, s * 0.18), int(y), 0.9, 1))


# ================================================================ 17. the werewolf — the tracks that change in the snow
def bootprint(cx, cy, s, ang, col, op=0.8):
    pts = T([(-5, -12), (0, -14), (5, -12), (5, 0), (4, 6), (0, 7), (-4, 6), (-5, 0)], cx, cy, s, False, ang)
    heel = T([(-4, 10), (4, 10), (4, 16), (-4, 16)], cx, cy, s, False, ang)
    return f'<path d="{smooth_closed(pts)}" fill="{col}" opacity="{op}"/><path d="{smooth_closed(heel)}" fill="{col}" opacity="{op}"/>'


def pawprint(cx, cy, s, ang, col, op=0.85):
    out = [f'<path d="{smooth_closed(T([(-7, 2), (0, -3), (7, 2), (6, 8), (0, 10), (-6, 8)], cx, cy, s, False, ang))}" fill="{col}" opacity="{op}"/>']
    for (dx, dy) in ((-8, -6), (-3, -11), (3, -11), (8, -6)):
        px, py = T([(dx, dy)], cx, cy, s, False, ang)[0]
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{2.6 * s:.1f}" ry="{3.4 * s:.1f}" fill="{col}" opacity="{op}" transform="rotate({ang} {px:.1f} {py:.1f})"/>')
        tx_, ty_ = T([(dx * 1.25, dy - 5)], cx, cy, s, False, ang)[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} L {tx_:.1f} {ty_:.1f}" stroke="{col}" stroke-width="{1.2 * s:.1f}" opacity="{op * 0.8:.2f}"/>')
    return "".join(out)


@design("the-werewolf")
def the_werewolf():
    D = Doc2("hr-ww")
    out = [night(D, [(0, "#04060E"), (0.5, "#142040"), (1, "#2A3A5A")], 1)]
    out.append(stars_field(4, (0, 0, 600, 300), 110))
    out.append(moon(D, 300, 262, 84, 5, pal=("#FFFFFF", "#EEF0F6", "#B8C0D0"), glow="#DCE8FF", gs=0.6, glow_r=2.6))
    # the forest: rows of snow-laden pines, darker nearer
    from paint import conifer
    rnd = random.Random(6)
    for row, (base, hmin, hmax, col) in enumerate(((330, 50, 90, "#3A4A6A"), (360, 80, 140, "#1E2A44"), (400, 140, 230, "#0A1022"))):
        xs = sorted(rnd.uniform(-30, 630) for _ in range(16 - row * 3))
        for x in xs:
            if abs(x - 300) < 60 + row * 20 and row == 2:
                continue
            h = rnd.uniform(hmin, hmax)
            out.append(conifer(x, base + rnd.uniform(-6, 6), h, col, rnd.random(), light=lt(col, 0.5)))
    out.append(fog(D, 340, 50, 7, "#C8D8F0", 0.4))
    # the snow, the path receding into the trees
    out.append(hill(D, [(-20, 400), (200, 394), (420, 398), (620, 392)], 640, ("#F2F6FF", "#B8C8E0", "#5A6A8A"), 8, inkw=0, n=60, lit="#FFFFFF"))
    out.append(f'<path d="M 120 610 Q 240 470 290 398 L 312 398 Q 380 470 500 610 Z" fill="#9AAAC8" opacity="0.45"/>')
    out.append(f'<path d="M 120 610 Q 240 470 290 398 L 300 398 Q 270 480 230 610 Z" fill="#7A8AA8" opacity="0.25"/>')
    # the tracks: boots at first, then something else
    steps = [(330, 580, 1.5, 0), (276, 548, 1.4, 1), (318, 514, 1.25, 0), (282, 488, 1.12, 1), (312, 466, 1.0, 0), (288, 448, 0.9, 1),
             (306, 432, 0.8, 0), (292, 420, 0.7, 1), (302, 410, 0.6, 0)]
    for k, (x, y, sc_, side) in enumerate(steps):
        ang = -8 if side else 8
        if k < 3:
            out.append(bootprint(x, y, sc_, ang, "#4A5A7A"))
        elif k == 3:
            out.append(bootprint(x, y, sc_, ang, "#4A5A7A", 0.45))
            out.append(pawprint(x + 2, y - 4, sc_ * 0.9, ang, "#3A4A6A", 0.6))
        else:
            out.append(pawprint(x, y, sc_ * 1.1, ang, "#2A3A5A"))
    # a torn red scarf caught on a thorn branch
    out.append(crooked_tree(78, 560, 240, 9, "#0A0E1A", w=12, lean=14, spread=34, depth=4))
    sc_pts = [(150, 420), (166, 432), (176, 452), (170, 470), (178, 488)]
    out.append(taper(catmull(sc_pts, 6), 12, 6, "#B8201A"))
    out.append(taper(catmull([(150, 420), (138, 438), (142, 462)], 6), 10, 5, "#8A1414"))
    for k in range(4):
        out.append(f'<path d="M {170 + k * 3} {482 + k * 3} l {k - 2} 10" stroke="#B8201A" stroke-width="1.6"/>')
    # snow on the branches, drifting flakes
    out.append(snowfall(10, (0, 0, 600, 600), 90, (0.6, 2.2), "#FFFFFF", (0.4, 0.9)))
    out.append(band(D, 0, 180, "#000000", 0.45, 0))
    # lettering
    out.append(glow_text(D, 300, 118, "THE WEREWOLF", BEBAS, 92, "#F2F6FF", "#9AB8FF", ls=8, max_w=450, shadow="#000000"))
    out.append(tx(300, 158, "Don’t follow the tracks.", SERIF_IT, 28, "#DCE8FF", max_w=400))
    return fin(D, out, 28)


# ================================================================ 18. the cursed tomb — the lid slid aside
GLYPHS = ["eye", "bird", "ankh", "water", "reed", "sun", "snake", "hand"]


def glyph_draw(kind, x, y, s, col):
    if kind == "eye":
        return f'<path d="M {x - 7 * s:.1f} {y:.1f} Q {x:.1f} {y - 6 * s:.1f} {x + 7 * s:.1f} {y:.1f} Q {x:.1f} {y + 5 * s:.1f} {x - 7 * s:.1f} {y:.1f} Z M {x + 1 * s:.1f} {y + 4 * s:.1f} l -2 {6 * s:.1f}" fill="none" stroke="{col}" stroke-width="1.6"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{1.8 * s:.1f}" fill="{col}"/>'
    if kind == "bird":
        return f'<path d="{smooth_closed([(x - 6 * s, y + 6 * s), (x - 4 * s, y - 2 * s), (x + 2 * s, y - 6 * s), (x + 6 * s, y - 4 * s), (x + 3 * s, y), (x + 4 * s, y + 7 * s)])}" fill="{col}"/>'
    if kind == "ankh":
        return f'<ellipse cx="{x:.1f}" cy="{y - 5 * s:.1f}" rx="{3 * s:.1f}" ry="{4 * s:.1f}" fill="none" stroke="{col}" stroke-width="1.8"/><path d="M {x - 6 * s:.1f} {y:.1f} L {x + 6 * s:.1f} {y:.1f} M {x:.1f} {y - 1:.1f} L {x:.1f} {y + 10 * s:.1f}" stroke="{col}" stroke-width="2"/>'
    if kind == "water":
        return f'<path d="M {x - 8 * s:.1f} {y:.1f} l {2.7 * s:.1f} {-3 * s:.1f} l {2.7 * s:.1f} {3 * s:.1f} l {2.7 * s:.1f} {-3 * s:.1f} l {2.7 * s:.1f} {3 * s:.1f} l {2.7 * s:.1f} {-3 * s:.1f}" fill="none" stroke="{col}" stroke-width="1.6"/>'
    if kind == "reed":
        return f'<path d="M {x:.1f} {y + 8 * s:.1f} L {x:.1f} {y - 6 * s:.1f} Q {x + 5 * s:.1f} {y - 8 * s:.1f} {x + 3 * s:.1f} {y:.1f}" fill="none" stroke="{col}" stroke-width="1.8"/>'
    if kind == "sun":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 * s:.1f}" fill="none" stroke="{col}" stroke-width="1.8"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{1.4 * s:.1f}" fill="{col}"/>'
    if kind == "snake":
        return f'<path d="M {x - 8 * s:.1f} {y + 5 * s:.1f} Q {x - 4 * s:.1f} {y - 4 * s:.1f} {x:.1f} {y + 2 * s:.1f} T {x + 7 * s:.1f} {y - 4 * s:.1f}" fill="none" stroke="{col}" stroke-width="2"/>'
    return f'<path d="M {x - 6 * s:.1f} {y + 2 * s:.1f} L {x + 6 * s:.1f} {y + 2 * s:.1f} L {x + 6 * s:.1f} {y - 3 * s:.1f} M {x - 6 * s:.1f} {y + 2 * s:.1f} L {x - 4 * s:.1f} {y - 4 * s:.1f}" fill="none" stroke="{col}" stroke-width="1.8"/>'


@design("the-cursed-tomb")
def the_cursed_tomb():
    D = Doc2("hr-tb")
    out = [f'<rect width="600" height="600" fill="#1A120A"/>']
    # painted walls, columns of hieroglyphs, torchlight from the left
    out.append(f'<rect width="600" height="440" fill="{D.rad([(0, "#C8965A"), (0.45, "#7A5430"), (1, "#24160A")], 0.18, 0.55, 0.9)}"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 440 L 0 440 Z", (0, 0, 600, 440), ["#D8A86A", "#4A3018", "#A87A44"], 3, n=120, angle=-88, length=(30, 90), width=(3, 8), opacity=(0.1, 0.25)))
    rnd = random.Random(4)
    for c in range(12):
        x = 30 + c * 50
        out.append(f'<path d="M {x - 20} 190 L {x - 20} 430" stroke="#3A2410" stroke-width="1.4" opacity="0.4"/>')
        for r_ in range(9):
            y = 206 + r_ * 26
            out.append(glyph_draw(rnd.choice(GLYPHS), x, y, 1.15, "#2A1A0A"))
    out.append(f'<path d="M 0 190 L 600 190" stroke="#2A1A0A" stroke-width="3" opacity="0.6"/>')
    for k in range(30):
        out.append(f'<rect x="{k * 20}" y="176" width="10" height="14" fill="{["#1E5A6A", "#C8963A", "#8A2A1A"][k % 3]}" opacity="0.7"/>')
    # the torch in its bracket
    out.append(taper([(70, 330), (76, 270)], 10, 12, "#3A2410"))
    out.append(soft_glow(D, 76, 240, 160, "#FFB050", 0.6))
    out.append(flame_lick(76, 268, 54, 22, 3))
    # floor
    out.append(f'<rect x="-10" y="440" width="620" height="170" fill="{D.lin([(0, "#5A3E24"), (1, "#140C06")])}"/>')
    out.append(strokes(D.nid(), "M -10 440 L 610 440 L 610 610 L -10 610 Z", (-40, 440, 610, 610), ["#7A5A3A", "#140C06"], 5, n=60, angle=0, length=(50, 140), width=(2, 5), opacity=(0.15, 0.4)))
    # the sarcophagus: a great stone chest, its lid pushed askew; something green glows inside
    sx0, sx1, st, sb = 150, 470, 380, 500
    out.append(cast(D, 330, sb + 4, 200, 16, "#000000", 0.6))
    chest = poly_pts([(sx0, sb), (sx0, st), (sx1, st), (sx1, sb)], 16, 3, 0.4)
    out.append(painted(D, chest, ("#C8B08A", "#8A7254", "#3A2A18"), 5, sdir=(0.7, 0.3), sk=0.12, angle=-90, n=40, inkw=1.6, inkc="#1A0E06", hi=0.4))
    for k in range(6):
        out.append(glyph_draw(GLYPHS[k], sx0 + 40 + k * 48, 440, 1.6, "#3A2A18"))
    out.append(f'<path d="M {sx0 + 10} 410 L {sx1 - 10} 410 M {sx0 + 10} 470 L {sx1 - 10} 470" stroke="#3A2A18" stroke-width="2" opacity="0.6"/>')
    out.append(f'<path d="M {sx0 + 6} {st} L {sx1 - 6} {st} L {sx1 - 24} {st - 18} L {sx0 + 24} {st - 18} Z" fill="#050302"/>')
    out.append(soft_glow(D, 330, st - 12, 120, "#7AF07A", 0.45))
    lid = poly_pts([(sx0 - 40, st - 26), (sx1 - 70, st - 70), (sx1 - 60, st - 46), (sx0 - 30, st - 4)], 16, 4, 0.5)
    out.append(painted(D, lid, ("#E0CCA8", "#A08A68", "#4A3A24"), 6, sdir=(0.6, 0.6), sk=0.15, angle=-12, n=30, inkw=1.6, inkc="#1A0E06", hi=0.45))
    out.append(f'<path d="{pd([(sx0 - 30, st - 4), (sx1 - 60, st - 46), (sx1 - 58, st - 36), (sx0 - 28, st + 6)])}" fill="#4A3A24"/>')
    # a strip of old linen trailing out over the edge
    out.append(taper(catmull([(390, st - 8), (420, st + 6), (430, st + 40), (452, st + 72), (446, st + 108)], 6), 12, 8, "#E8DCC0"))
    out.append(taper(catmull([(392, st - 6), (422, st + 8), (432, st + 42)], 6), 3, 2, "#A89878", 0.6))
    for k in range(6):
        out.append(f'<path d="M {418 + k * 5} {st + 10 + k * 16} l 8 3" stroke="#A89878" stroke-width="1"/>')
    # scattered treasure: a scarab and a canopic jar
    out.append(painted(D, [(536, 470), (530, 420), (540, 400), (560, 400), (570, 420), (564, 470)], ("#F2D27A", "#C8963A", "#6A4A14"), 8, sdir=(0.6, 0.4), sk=0.2, n=10, inkw=1.2, inkc="#2A1A06", hi=0.5))
    out.append(f'<path d="{blob(550, 392, 14, 10, 4, 0.1, 10)}" fill="#1E5A6A"/>')
    out.append(painted(D, blob_pts(100, 500, 18, 13, 5, 0.05, 14), ("#7AD8C8", "#1E8A8A", "#0A3A3A"), 9, sdir=(0.6, 0.6), sk=0.2, n=8, inkw=1.2, inkc="#062020", hi=0.5))
    out.append(f'<path d="M 100 488 L 100 512 M 86 500 L 114 500" stroke="#0A3A3A" stroke-width="1.6"/>')
    # the carved lintel at the top with the warning
    out.append(painted(D, poly_pts([(-10, 30), (610, 30), (610, 168), (-10, 168)], 30, 6, 0.6), ("#5A4A3A", "#2E241A", "#0E0A06"), 10, sdir=(0, 1), sk=0.15, angle=0, n=60, inkw=1.6, inkc="#1A0E06", hi=0.4))
    out.append(f'<path d="M -10 168 L 610 168 L 610 178 L -10 178 Z" fill="#2A1A0A" opacity="0.7"/>')
    out.append(gilt(D, 300, 116, "THE CURSED TOMB", CINZEL, 54, ls=4, max_w=470, seed=11, deboss="#2A1A0A", dop=0.9))
    out.append(tx(300, 150, "WHO OPENS IT · WAKES HIM", CINZEL, 17, "#E8C890", ls=4, max_w=380))
    out.append(vignette(D, "#000000", 0.6))
    out.append(tx(300, 548, "Valley of the Kings · 1922", SERIF_IT, 24, "#E8C890", max_w=400))
    return fin(D, out, 29)


# ================================================================ 19. double, double toil and trouble — a chapbook woodcut of the heath
def hatch_in(D, d, box, col, step=6, ang=-45, w=1.4, op=0.9):
    x0, y0, x1, y1 = box
    cid = D.clip(f'<path d="{d}"/>')
    L = (x1 - x0) + (y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lines = []
    k = -L
    while k < L:
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        px, py = cx - dy * k, cy + dx * k
        lines.append(f'M {px - dx * L:.1f} {py - dy * L:.1f} L {px + dx * L:.1f} {py + dy * L:.1f}')
        k += step
    return f'<g {cid}><path d="{" ".join(lines)}" stroke="{col}" stroke-width="{w}" opacity="{op}"/></g>'


def hag(x, base, s, col, flip=False, stir=False, arm_up=False):
    """A hooded, crook-backed witch in a ragged cloak (woodcut silhouette), about 120*s tall."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [poly(L([(-30, 0), (-24, -30), (-28, -60), (-18, -88), (-2, -104), (14, -108), (26, -100), (28, -84), (20, -60), (24, -30), (32, 0),
                   (22, -4), (16, 2), (6, -4), (-4, 2), (-14, -4), (-22, 2)]), col)]
    out.append(poly(L([(10, -108), (20, -122), (34, -126), (42, -116), (40, -104), (30, -96), (16, -98)]), col))
    out.append(sharp(L([(36, -118), (48, -112), (40, -108)]), col))
    if stir:
        out.append(taper(L([(22, -86), (40, -74), (56, -70)]), 8 * s, 5 * s, col))
        out.append(taper(L([(46, -98), (60, -40)]), 3 * s, 3 * s, col))
    if arm_up:
        out.append(taper(L([(20, -94), (34, -118), (40, -142)]), 8 * s, 4 * s, col))
        for fa in (-110, -80, -60):
            hx, hy = L([(40, -142)])[0]
            a = math.radians(fa if not flip else 180 - fa)
            out.append(taper([(hx, hy), (hx + math.cos(a) * 9 * s, hy + math.sin(a) * 9 * s)], 2.4 * s, 0.6, col))
    return "".join(out)


@design("double-double-toil-and-trouble")
def double_double_toil_and_trouble():
    D = Doc2("hr-dd")
    from gouache import paper
    INKC = "#1A120E"
    RED = "#B0241A"
    out = [paper(D.nid(), "#EFE4CC", "#6A4A2A", 8)]
    # the woodcut block: a heavy black border with notched corners
    x0, y0, x1, y1 = 52, 52, 548, 548
    out.append(f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="none" stroke="{INKC}" stroke-width="8"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="{INKC}" stroke-width="2"/>')
    # sky: moon and storm drawn in cut lines
    mx, my, mr = 420, 170, 44
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#F6EEDA" stroke="{INKC}" stroke-width="3"/>')
    out.append(hatch_in(D, f"M {mx - mr} {my} A {mr} {mr} 0 0 0 {mx + mr} {my} A {mr * 0.6} {mr} 0 0 1 {mx - mr} {my} Z", (mx - mr, my - mr, mx + mr, my + mr), INKC, 4, 0, 1.2, 0.7))
    rnd = random.Random(3)
    cloud = []
    for k in range(9):
        y = 90 + k * 12
        cloud.append(f'<path d="M {x0} {y} Q {150 + rnd.uniform(-20, 20)} {y - 10} {260 + k * 6} {y + rnd.uniform(-4, 4)}" fill="none" stroke="{INKC}" stroke-width="{2.4 - k * 0.15:.1f}"/>')
    out.append("".join(cloud))
    out.append(f'<path d="M 300 78 L 284 132 L 302 130 L 276 196 L 312 122 L 294 124 L 314 78 Z" fill="{INKC}"/>')
    # the blasted heath: ground line and a dead tree
    ground = smooth_open([(x0, 420), (160, 408), (300, 414), (440, 404), (x1, 412)])
    out.append(f'<path d="{ground} L {x1} {y1} L {x0} {y1} Z" fill="#EFE4CC"/>')
    out.append(hatch_in(D, f"{ground} L {x1} {y1} L {x0} {y1} Z", (x0, 400, x1, y1), INKC, 7, 0, 1.6, 0.85))
    out.append(ink(ground, INKC, 3, 2, 1, 1))
    tree = []
    out.append(crooked_tree(110, 420, 260, 6, INKC, w=12, lean=6, spread=40, depth=4))
    # the third sister behind the cauldron, then the cauldron on its fire, steam curling up
    out.append(hag(300, 392, 0.86, INKC, flip=False, arm_up=True))
    cx, cy = 300, 404
    for k in range(7):
        fx = cx - 54 + k * 18
        out.append(f'<path d="M {fx - 10} {cy + 34} Q {fx - 8} {cy + 6} {fx + rnd.uniform(-4, 4)} {cy - 6} Q {fx + 8} {cy + 8} {fx + 10} {cy + 34} Z" fill="{RED}" stroke="{INKC}" stroke-width="1.6"/>')
    pot = [(cx - 70, cy - 40), (cx + 70, cy - 40), (cx + 78, cy - 10), (cx + 66, cy + 20), (cx + 40, cy + 34), (cx - 40, cy + 34), (cx - 66, cy + 20), (cx - 78, cy - 10)]
    out.append(f'<path d="{smooth_closed(pot)}" fill="{INKC}"/>')
    out.append(f'<path d="M {cx - 50} {cy - 20} Q {cx - 60} {cy + 6} {cx - 40} {cy + 22}" fill="none" stroke="#EFE4CC" stroke-width="3"/>')
    out.append(f'<path d="M {cx - 34} {cy - 22} Q {cx - 42} {cy + 4} {cx - 26} {cy + 22}" fill="none" stroke="#EFE4CC" stroke-width="2"/>')
    out.append(f'<ellipse cx="{cx}" cy="{cy - 40}" rx="76" ry="12" fill="{INKC}"/><ellipse cx="{cx}" cy="{cy - 41}" rx="64" ry="7" fill="{RED}"/>')
    for k in range(5):
        out.append(f'<circle cx="{cx - 40 + k * 20}" cy="{cy - 42 + (k % 2) * 3}" r="{3 + k % 2}" fill="none" stroke="#EFE4CC" stroke-width="1.6"/>')
    for k, dx in enumerate((-30, 0, 30)):
        out.append(f'<path d="{smooth_open([(cx + dx, cy - 52), (cx + dx - 14, cy - 80), (cx + dx + 10, cy - 110), (cx + dx - 6, cy - 140)])}" fill="none" stroke="{INKC}" stroke-width="2.4" stroke-linecap="round"/>')
    # the three weird sisters
    out.append(hag(200, 412, 1.05, INKC, stir=True))
    out.append(hag(402, 410, 1.0, INKC, flip=True, arm_up=True))

    for (hx, hy) in ((218, 330), (390, 330)):
        out.append(hatch_in(D, blob(hx, hy, 18, 40, 3, 0.1, 12), (hx - 20, hy - 42, hx + 20, hy + 42), "#EFE4CC", 6, -60, 1, 0.5))
    # lettering: a chapbook title block on a plain cartouche
    out.append(f'<rect x="96" y="446" width="408" height="86" fill="#EFE4CC" stroke="{INKC}" stroke-width="2.4"/>')
    out.append(tx(300, 478, "Double, double", SERIF_IT, 40, INKC, max_w=420))
    out.append(tx(300, 516, "toil and trouble", SERIF_IT, 40, INKC, max_w=420))
    out.append(f'<rect x="200" y="522" width="200" height="22" fill="{RED}"/>')
    out.append(tx(300, 540, "MACBETH · 1606", CINZEL, 16, "#F6EEDA", ls=3, max_w=184))
    return fin(D, out, 30, "#3A2A1A", 0.6)


# ================================================================ 20. the house on the hill — for sale, again
def victorian_house(D, cx, base, s, seed, col="#0A0810", lit="#FFC860"):
    """A Queen Anne house in silhouette: corner turret with a witch's-cap roof, steep gables, porch, chimneys,
    a lit window or two and broken shutters."""
    def L(pts):
        return T(pts, cx, base, s)
    out = []
    body = L([(-110, 0), (-110, -120), (-70, -120), (-70, -150), (30, -150), (30, -120), (100, -120), (100, 0)])
    out.append(sharp(body, col))
    out.append(sharp(L([(-80, -150), (-20, -230), (40, -150)]), col))
    out.append(sharp(L([(20, -120), (60, -180), (110, -120)]), col))
    out.append(sharp(L([(-120, -118), (-90, -150), (-60, -118)]), col))
    out.append(sharp(L([(-150, -100), (-150, -220), (-110, -220), (-110, -100)]), col))
    out.append(sharp(L([(-156, -218), (-130, -300), (-104, -218)]), col))
    out.append(taper(L([(-130, -300), (-130, -318)]), 2, 1.4, col))
    for (x, h) in ((-40, 254), (70, 196)):
        out.append(sharp(L([(x - 7, -150), (x - 7, -h), (x + 9, -h), (x + 9, -150)]), col))
    # porch with posts and steps
    out.append(sharp(L([(-120, -50), (110, -50), (120, -42), (-130, -42)]), col))
    for k in range(7):
        out.append(taper(L([(-110 + k * 34, -42), (-110 + k * 34, 0)]), 3 * s, 3 * s, col))
    # windows: mostly black, one lit with a figure, a hanging shutter
    rnd = random.Random(seed)
    wins = [(-130, -190, False), (-130, -140, False), (-90, -100, False), (-40, -100, True), (10, -100, False), (60, -100, False), (-20, -190, True),
            (-60, -86, False), (60, -150, False)]
    for (wx, wy, on) in wins[:7]:
        w_, h_ = 14, 26
        pts = L([(wx - w_ / 2, wy), (wx + w_ / 2, wy), (wx + w_ / 2, wy + h_), (wx - w_ / 2, wy + h_)])
        if on:
            ccx, ccy = L([(wx, wy + h_ / 2)])[0]
            out.append(soft_glow(D, ccx, ccy, 40 * s, lit, 0.5))
            out.append(f'<path d="{pd(pts)}" fill="{lit}"/>')
        else:
            out.append(f'<path d="{pd(pts)}" fill="#1E1A28"/>')
    # the figure at the top window
    fx, fy = L([(-20, -166)])[0]
    out.append(f'<path d="{blob(fx, fy - 6 * s, 3.4 * s, 4 * s, 3, 0.06, 10)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed([(fx - 6 * s, fy + 2 * s), (fx - 4 * s, fy - 3 * s), (fx + 4 * s, fy - 3 * s), (fx + 6 * s, fy + 2 * s)])}" fill="{col}"/>')
    # the hanging shutter
    sx, sy = L([(-31, -100)])[0]
    out.append(f'<path d="M {sx:.1f} {sy:.1f} l {6 * s:.1f} {2 * s:.1f} l {-2 * s:.1f} {28 * s:.1f} l {-6 * s:.1f} {-2 * s:.1f} Z" fill="{col}" transform="rotate(-18 {sx:.1f} {sy:.1f})"/>')
    return "".join(out)


@design("the-house-on-the-hill")
def the_house_on_the_hill():
    D = Doc2("hr-hh2")
    out = [night(D, [(0, "#0A0618"), (0.45, "#2A1A44"), (0.75, "#6A3A5A"), (1, "#C86A4A")], 1)]
    out.append(stars_field(5, (0, 0, 600, 260), 80))
    out.append(moon(D, 160, 210, 54, 6, pal=("#FFF8E2", "#F2E2C0", "#C8B48A"), glow="#FFE8C8", gs=0.45, glow_r=3.0))
    out.append(puff_cloud(D, 470, 240, 230, 7, ("#6A4A6A", "#3A2440", "#1A0E22"), op=0.8))
    # the hill with its crooked path, iron fence and dead tree
    out.append(hill(D, ridge([(-20, 470), (120, 440), (260, 408), (360, 402), (480, 426), (620, 460)], 3, 6, 4), 640, ("#3A2A44", "#1E1426", "#08040C"), 4, inkw=0, n=40, lit="#C8806A"))
    out.append(victorian_house(D, 330, 412, 0.95, 8))
    out.append(crooked_tree(540, 450, 280, 9, "#06040A", w=14, lean=-6, spread=36, depth=5))
    out.append(crooked_tree(70, 470, 180, 10, "#06040A", w=9, lean=12, spread=40, depth=4))
    for k in range(18):
        x = 120 + k * 22
        y = 470 - (k / 17) * 10
        out.append(taper([(x, y + 26), (x, y)], 3, 2, "#06040A"))
        out.append(sharp([(x - 4, y + 2), (x, y - 8), (x + 4, y + 2)], "#06040A"))
    out.append(taper([(116, 480), (300, 474), (510, 466)], 3, 3, "#06040A"))
    for (bx, by, bs) in ((480, 140, 12), (510, 162, 9), (452, 168, 8), (540, 130, 7)):
        out.append(bird_v(bx, by, bs, "#06040A"))
    # the estate agent's sign, leaning
    sx, sy = 168, 478
    out.append(taper([(sx, sy + 60), (sx + 6, sy - 10)], 7, 6, "#2A1A12"))
    board = rot([(sx - 70, sy - 64), (sx + 70, sy - 64), (sx + 70, sy - 10), (sx - 70, sy - 10)], sx, sy - 37, -7)
    out.append(painted(D, poly_pts(board, 14, 3, 0.6), ("#F2E2C0", "#D8C098", "#7A6448"), 5, sdir=(0.5, 0.5), sk=0.15, angle=0, n=20, inkw=1.6, inkc="#1A0E06", hi=0.4))
    out.append(f'<g transform="rotate(-7 {sx} {sy - 37})">{tx(sx, sy - 34, "FOR SALE", BEBAS, 34, "#8A1A14", ls=3, max_w=120)}{tx(sx, sy - 14, "AGAIN", JOST, 16, "#2A1A12", ls=4, max_w=100)}</g>')
    out.append(band(D, 520, 600, "#000000", 0, 0.75))
    # lettering
    out.append(block(D, 300, 112, "THE HOUSE", BEBAS, 72, "#F6E8D8", "#4A1E3A", depth=6, ang=(0.6, 1.0), ls=10, max_w=420, face2="#E8B8A0", shadow="#000000"))
    out.append(tx(300, 148, "on the hill", SERIF_IT, 34, "#F2D0C0", max_w=300))
    out.append(sub_rule(300, 548, "VACANT SINCE 1888", CINZEL, 18, "#F2D0C0", ls=4, max_w=300, line="#C8806A"))
    return fin(D, out, 31)


# ================================================================ 21. the graveyard bell — it rang once at midnight
@design("the-graveyard-bell")
def the_graveyard_bell():
    D = Doc2("hr-gb")
    out = [night(D, [(0, "#060A10"), (0.45, "#18243A"), (0.75, "#2E3A50"), (1, "#141A26")], 1)]
    out.append(stars_field(6, (0, 0, 600, 300), 90))
    out.append(moon(D, 470, 170, 40, 6, pal=("#FFFCF0", "#ECEAE0", "#B8B8AA"), glow="#E8F0FF", gs=0.45, glow_r=3.0))
    # the church and lych-gate far behind, in the fog
    out.append(hill(D, ridge([(-20, 360), (160, 346), (340, 356), (620, 340)], 3, 4, 3), 640, ("#2A3446", "#161E2C", "#080C14"), 2, inkw=0, n=20))
    out.append(sharp([(60, 352), (60, 290), (110, 260), (160, 290), (160, 352)], "#0A0E18"))
    out.append(sharp([(80, 292), (80, 210), (98, 186), (116, 210), (116, 292)], "#0A0E18"))
    out.append(lit_slit(D, 98, 230, 6, 14, "#FFC870"))
    out.append(lit_slit(D, 136, 300, 7, 18, "#FFC870"))
    out.append(fog(D, 352, 50, 4, "#A8B8D0", 0.5))
    # rows of leaning headstones
    rnd = random.Random(5)
    for k, (x, base, w, h, kind) in enumerate(((210, 372, 22, 34, "round"), (260, 376, 18, 30, "cross"), (360, 370, 22, 36, "round"), (420, 374, 26, 32, "gable"),
                                                 (520, 372, 20, 30, "round"), (40, 390, 30, 44, "cross"))):
        out.append(tombstone(D, x, base, w, h, 10 + k, kind, pal=("#7A8498", "#4A5468", "#1E2434"), lean=rnd.uniform(-8, 8)))
    out.append(hill(D, [(-20, 404), (160, 396), (360, 402), (620, 394)], 640, ("#3A4A44", "#1E2A26", "#0A100E"), 5, inkw=0, n=40))
    out.append(grass(6, (-10, 400, 610, 600), ["#2A3A34", "#4A5A50", "#0E1612"], 140, (6, 18)))
    for k, (x, base, w, h, kind) in enumerate(((90, 520, 66, 110, "round"), (520, 506, 70, 128, "cross"))):
        out.append(tombstone(D, x, base, w, h, 20 + k, kind, pal=("#9AA4B4", "#5A6476", "#20263A"), lean=(-6 if k == 0 else 5)))
    out.append(tx(90, 472, "R.I.P.", CINZEL, 16, "#2A3040", ls=1, max_w=54))
    # the fresh grave, the wooden post, and the safety bell on its cord
    out.append(painted(D, blob_pts(300, 520, 150, 34, 3, 0.06, 24), ("#6A5040", "#3A2A20", "#140C08"), 6, sdir=(0.6, 0.8), sk=0.2, angle=0, n=40, inkw=1.4, inkc="#06040A", hi=0.35))
    out.append(specks(7, (170, 496, 430, 548), ["#8A6A50", "#1A100A"], 60, (1, 3), (0.4, 0.8)))
    wood = ("#8A6A4A", "#4A3424", "#1A100A")
    out.append(painted(D, poly_pts([(352, 524), (352, 292), (366, 292), (366, 524)], 14, 3, 0.4), wood, 8, sdir=(0.7, 0.2), sk=0.25, angle=-90, n=12, inkw=1.4, inkc="#06040A", hi=0.4))
    out.append(painted(D, poly_pts([(250, 292), (372, 292), (372, 308), (250, 308)], 14, 4, 0.4), wood, 9, sdir=(0, 1), sk=0.25, angle=0, n=8, inkw=1.4, inkc="#06040A", hi=0.4))
    out.append(taper([(352, 340), (318, 304)], 7, 7, wood[1]))
    # the bell, swung out, glowing in the lantern light
    bx, by = 276, 306
    out.append(f'<path d="M {bx} 306 L {bx} 318" stroke="#2A1A0A" stroke-width="3.4"/>')
    ang = -16
    k_ = 1.45
    bell = T([(-6, 0), (-8, 10), (-12, 26), (-20, 36), (20, 36), (12, 26), (8, 10), (6, 0)], bx, by + 12, k_, False, ang)
    out.append(soft_glow(D, bx + 8, by + 60, 80, "#FFD27A", 0.5))
    out.append(painted(D, bell, ("#FFE7A0", "#C8963A", "#5A3A10"), 10, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=12, inkw=1.6, inkc="#2A1A06", hi=0.55))
    cl = T([(0, 40)], bx, by + 12, k_, False, ang)[0]
    out.append(f'<circle cx="{cl[0]:.1f}" cy="{cl[1]:.1f}" r="5" fill="#5A3A10"/>')
    for k, r_ in enumerate((60, 76, 92)):
        out.append(f'<path d="M {bx + 40 + k * 6} {by + 10 + k * 2} A {r_} {r_} 0 0 1 {bx + 46 + k * 8} {by + 70 + k * 6}" fill="none" stroke="#FFE7A0" stroke-width="{2.6 - k * 0.6:.1f}" opacity="{0.75 - k * 0.2:.2f}" stroke-linecap="round"/>')
        out.append(f'<path d="M {bx - 40 - k * 6} {by + 10 + k * 2} A {r_} {r_} 0 0 0 {bx - 46 - k * 8} {by + 70 + k * 6}" fill="none" stroke="#FFE7A0" stroke-width="{2.6 - k * 0.6:.1f}" opacity="{0.75 - k * 0.2:.2f}" stroke-linecap="round"/>')
    # the cord running from the bell down into the earth, pulled taut
    out.append(f'<path d="M {cl[0]:.1f} {cl[1]:.1f} L {cl[0] - 2:.1f} 508" stroke="#C8B080" stroke-width="2.2"/>')
    out.append(f'<path d="{blob(cl[0] - 2, 510, 9, 3.4, 4, 0.2, 8)}" fill="#140C08"/>')
    # a dropped lantern by the grave
    lx, ly = 430, 520
    out.append(soft_glow(D, lx, ly - 12, 70, "#FFC870", 0.5))
    out.append(painted(D, poly_pts([(lx - 11, ly), (lx - 11, ly - 26), (lx + 11, ly - 26), (lx + 11, ly)], 8, 5, 0.3), ("#FFF2B8", "#FFC860", "#C8802A"), 11, sdir=(0.5, 0.5), sk=0.15, n=6, inkw=1.6, inkc="#1A1008", hi=0.5))
    out.append(sharp([(lx - 14, ly - 26), (lx, ly - 38), (lx + 14, ly - 26)], "#1A1008"))
    out.append(f'<path d="M {lx - 6} {ly - 40} q 6 -10 12 0" fill="none" stroke="#1A1008" stroke-width="2"/>')
    out.append(fog(D, 560, 60, 8, "#8A98B0", 0.35))
    out.append(band(D, 0, 200, "#000000", 0.5, 0))
    # lettering: a Victorian broadside
    out.append(block(D, 300, 110, "THE GRAVEYARD", ANTON, 58, "#F2EEE2", "#2A3450", depth=5, ang=(0.6, 1.0), ls=6, max_w=440, face2="#C8D0E0", shadow="#000000"))
    out.append(block(D, 300, 176, "BELL", ANTON, 70, "#FFD27A", "#5A3A10", depth=6, ang=(0.6, 1.0), ls=14, max_w=300, face2="#E8A040", shadow="#000000"))
    out.append(tx(300, 548, "It rang once, at midnight.", SERIF_IT, 26, "#E8ECF6", max_w=400))
    return fin(D, out, 32)


# ================================================================ 22. the jersey devil — the Pine Barrens extra, 1909
def jersey_devil(x, y, s, col):
    """Flying, seen from the side (facing left): a horse-like head on a long neck, leathery bat wings raised,
    thin legs with hooves tucked, a long forked tail."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    # wings
    for (wing, dy) in ((L([(-6, -10), (-20, -60), (-6, -104), (14, -80), (30, -110), (44, -72), (66, -92), (66, -48), (84, -50), (60, -8), (20, 4)]), 0),
                       (L([(4, -6), (30, -52), (64, -64), (78, -40), (100, -46), (96, -14), (118, -10), (80, 10), (30, 8)]), 0)):
        out.append(poly(wing, col))
    for (a, b) in (((-6, -10), (-6, -104)), ((6, -12), (30, -110)), ((14, -8), (66, -92)), ((20, -2), (84, -50))):
        p, q = L([a, b])
        out.append(f'<path d="M {p[0]:.1f} {p[1]:.1f} L {q[0]:.1f} {q[1]:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="0.18"/>')
    # body, neck, horse-like head with small horns
    out.append(poly(L([(-30, 4), (-16, -8), (14, -10), (40, -2), (52, 10), (30, 18), (0, 18), (-24, 14)]), col))
    out.append(taper(catmull(L([(-24, 2), (-44, -10), (-60, -24)]), 5), 14 * s, 9 * s, col))
    out.append(poly(L([(-54, -34), (-70, -38), (-92, -30), (-104, -20), (-102, -12), (-86, -10), (-70, -12), (-56, -16)]), col))
    out.append(sharp(L([(-62, -28), (-60, -42), (-56, -28)]), col))
    out.append(sharp(L([(-68, -28), (-70, -40), (-64, -28)]), col))
    out.append(f'<circle cx="{L([(-72, -24)])[0][0]:.1f}" cy="{L([(-72, -24)])[0][1]:.1f}" r="{2 * s:.1f}" fill="#E8402A"/>')
    # legs with hooves, tucked
    for (a, b, c) in (((-10, 16), (-20, 30), (-12, 40)), ((26, 16), (40, 30), (34, 44))):
        out.append(taper(catmull(L([a, b, c]), 4), 6 * s, 3.4 * s, col))
        px, py = L([c])[0]
        out.append(f'<path d="{blob(px, py, 3.6 * s, 2.6 * s, 3, 0.1, 8)}" fill="{col}"/>')
    # the long tail with a forked tip
    tail = catmull(L([(48, 10), (80, 20), (110, 10), (130, 24), (150, 22)]), 6)
    out.append(taper(tail, 5 * s, 1.6 * s, col))
    ex, ey = tail[-1]
    out.append(sharp([(ex - 2, ey - 2), (ex + 12 * s, ey - 8 * s), (ex + 6 * s, ey + 1), (ex + 12 * s, ey + 8 * s), (ex - 2, ey + 3)], col))
    return "".join(out)


@design("the-jersey-devil")
def the_jersey_devil():
    D = Doc2("hr-jd")
    from gouache import paper
    INKC = "#1A1814"
    out = [paper(D.nid(), "#E8E0CC", "#5A5040", 9)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0), (1, "#4A3A20", 0.25)])}"/>')
    # masthead
    out.append(tx(300, 92, "THE PINE BARRENS GAZETTE", DMS, 40, INKC, max_w=470))
    out.append(f'<path d="M 54 104 L 546 104 M 54 108 L 546 108" stroke="{INKC}" stroke-width="1.6"/>')
    out.append(tx(66, 125, "JANUARY 1909", MONO, 16, INKC, max_w=160, anchor="start"))
    out.append(tx(300, 125, "EXTRA!", MONO, 16, "#A8201A", ls=3, max_w=120))
    out.append(tx(534, 125, "ONE CENT", MONO, 16, INKC, max_w=160, anchor="end"))
    out.append(f'<path d="M 54 132 L 546 132" stroke="{INKC}" stroke-width="1.6"/>')
    # the headline
    out.append(tx(300, 196, "JERSEY DEVIL", ANTON, 72, INKC, ls=2, max_w=480))
    out.append(tx(300, 236, "SIGHTED OVER THE PINES", BEBAS, 38, "#A8201A", ls=4, max_w=470))
    # the halftone picture
    px0, py0, px1, py1 = 70, 254, 530, 488
    cid = D.clip(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}"/>')
    sc = [f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{D.lin([(0, "#2A2A2A"), (0.6, "#6A6A64"), (1, "#3A3A36")])}"/>']
    sc.append(soft_glow(D, 410, 320, 110, "#E8E4D8", 0.6))
    sc.append(f'<circle cx="410" cy="320" r="40" fill="#F2EEE2"/>')
    from paint import conifer
    rnd = random.Random(7)
    for x in sorted(rnd.uniform(60, 540) for _ in range(28)):
        sc.append(conifer(x, 490, rnd.uniform(50, 110), "#141412", rnd.random()))
    for x in sorted(rnd.uniform(60, 540) for _ in range(12)):
        sc.append(conifer(x, 500, rnd.uniform(90, 150), "#0A0A08", rnd.random()))
    sc.append(jersey_devil(300, 336, 1.05, "#0A0A08"))
    # halftone dot screen over the picture
    dots = D.pattern(5, 5, '<circle cx="2.5" cy="2.5" r="1.25" fill="#E8E0CC"/>', transform="rotate(45)")
    sc.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{dots}" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="none" stroke="{INKC}" stroke-width="2"/>')
    # caption and columns
    out.append(tx(300, 516, "Witnesses swear to hoofed beast with wings", SERIF_IT, 22, INKC, max_w=460))
    for k in range(3):
        y = 532 + k * 8
        out.append(f'<path d="M 70 {y} L 290 {y} M 310 {y} L 530 {y}" stroke="{INKC}" stroke-width="2.4" opacity="0.25"/>')
    out.append(f'<path d="M 54 60 L 546 60" stroke="{INKC}" stroke-width="1"/>')
    return fin(D, out, 33, "#3A3020", 0.6)


# ================================================================ 23. la llorona — by the river at night
@design("la-llorona")
def la_llorona():
    D = Doc2("hr-ll")
    out = [night(D, [(0, "#020A10"), (0.45, "#0E2A36"), (0.7, "#1E4A52"), (1, "#0A1A20")], 1)]
    out.append(stars_field(7, (0, 0, 600, 300), 100))
    out.append(moon(D, 300, 252, 62, 7, pal=("#FFFFFF", "#EEF4F2", "#B8C8C4"), glow="#DCF2F0", gs=0.5, glow_r=2.4))
    # far bank with willows and agaves
    out.append(hill(D, ridge([(-20, 340), (120, 326), (260, 334), (420, 322), (620, 336)], 3, 5, 3), 360, ("#1E3A3E", "#0E2226", "#040C0E"), 2, inkw=0, n=20))
    for (x, h) in ((70, 120), (520, 140)):
        out.append(crooked_tree(x, 340, h, int(x), "#04100E", w=10, spread=30, depth=4))
        for k in range(16):
            rnd = random.Random(x + k)
            bx = x + rnd.uniform(-50, 50)
            by = 340 - h * rnd.uniform(0.4, 0.9)
            out.append(taper([(bx, by), (bx + rnd.uniform(-4, 4), by + rnd.uniform(40, 80))], 2, 0.6, "#04100E", 0.9))
    # the river: moonpath, ripples, marigold petals drifting
    out.append(sea(D, 340, 640, [(0, "#1A3A40"), (0.5, "#0A1E24"), (1, "#020A0C")], 3, ["#4A7A7A", "#020A0C", "#9AC8C0"], 60))
    rnd = random.Random(8)
    for k in range(26):
        y = 350 + k * 9
        w = 14 + k * 3
        out.append(taper([(300 - w / 2 + rnd.uniform(-10, 10), y), (300 + w / 2 + rnd.uniform(-10, 10), y)], 1, 3 + k * 0.1, "#E8F6F2", 0.6 - k * 0.015))
    out.append(wave_lines(9, (0, 350, 600, 600), ["#6A9A98", "#C8E8E0", "#0A1E24"], 60, (12, 36), 1.6, 1.4, (0.3, 0.6)))
    for k in range(12):
        x, y = rnd.uniform(120, 520), rnd.uniform(400, 560)
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 5), rnd.uniform(2, 3), k, 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#FFA020", "#F28A10", "#FFC040"])}"/>')
    # reeds on the near bank, left and right
    for side, x0 in ((-1, 0), (1, 600)):
        for k in range(22):
            x = x0 - side * rnd.uniform(0, 140)
            h = rnd.uniform(60, 170)
            base = 600
            out.append(taper([(x, base), (x + side * rnd.uniform(4, 20), base - h * 0.6), (x + side * rnd.uniform(10, 30), base - h)], 4, 1, "#021010"))
    # the weeping woman at the water's edge: white gown and veil, long black hair, her reflection
    def woman(x, base, s, flip_y=False):
        def L(pts):
            return [(px, base + (base - py) * 0.9 if flip_y else py) for px, py in T(pts, x, base, s)]
        o = []
        gown = L([(-30, 0), (-24, -40), (-16, -80), (-12, -100), (-14, -118), (-8, -126), (8, -126), (14, -118), (12, -100), (16, -80), (26, -40), (34, 0),
                  (20, -4), (6, 2), (-8, -4), (-20, 2)])
        o.append(painted(D, gown, ("#FFFFFF", "#DCE8E8", "#7A9A9C"), 11, sdir=(0.5, 0.3), sk=0.2, angle=-90, n=20, inkw=0, hi=0.5))
        o.append(f'<path d="{smooth_closed(L([(-12, -146), (-16, -128), (-14, -100), (-20, -64), (-6, -70), (4, -100), (8, -130), (2, -150)]))}" fill="#06080A"/>')
        o.append(f'<path d="{blob(*L([(-3, -146)])[0], 9 * s, 11 * s, 4, 0.06, 10)}" fill="#06080A"/>')
        o.append(f'<path d="{smooth_closed(L([(-4, -158), (-16, -150), (-26, -100), (-34, -40), (-20, -60), (-12, -100), (6, -130), (10, -150)]))}" fill="#F2F8F8" opacity="0.45"/>')
        o.append(taper(L([(10, -112), (2, -128), (-4, -142)]), 6 * s, 4 * s, "#DCE8E8"))
        return "".join(o)
    out.append(soft_glow(D, 300, 420, 120, "#E8FFFF", 0.3))
    cid = D.clip('<rect x="0" y="470" width="600" height="140"/>')
    out.append(f'<g {cid} opacity="0.35">{woman(300, 470, 1.15, True)}</g>')
    out.append(woman(300, 470, 1.15))
    out.append(fog(D, 470, 40, 10, "#C8E8E8", 0.45))
    out.append(band(D, 0, 170, "#000000", 0.5, 0))
    # lettering
    out.append(letters(D, 300, 120, "La Llorona", SERIF_IT, 76, "#F2FAFA", ["#FFFFFF", "#DCF2F0", "#C8E8E8"], 34, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(spaced(300, 156, "THE WEEPING WOMAN · MEXICAN FOLKLORE", CINZEL, 16, "#C8E8E4", ls=1.5, max_w=470, shadow="#000000"))
    out.append(tx(300, 548, "No te acerques al río de noche", SERIF_IT, 24, "#E8F6F2", max_w=430))
    return fin(D, out, 34)


# ================================================================ 24. spring-heeled jack — a penny dreadful, hand-coloured
def leaping_jack(x, y, s, col):
    """A caped figure in mid-leap over the rooftops: tall, pointed ears, clawed hands, cloak billowing, legs tucked."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    cloak = L([(-8, -50), (-40, -56), (-80, -40), (-110, -50), (-96, -24), (-120, -10), (-84, 2), (-96, 20), (-56, 10), (-20, 20), (0, 0)])
    out.append(poly(cloak, col))
    out.append(poly(L([(-10, 30), (-14, 0), (-10, -40), (2, -54), (14, -50), (18, -20), (12, 10), (8, 30)]), col))
    out.append(f'<path d="{blob(*L([(8, -66)])[0], 10 * s, 12 * s, 3, 0.06, 10)}" fill="{col}"/>')
    out.append(sharp(L([(0, -74), (-4, -92), (6, -76)]), col))
    out.append(sharp(L([(12, -76), (14, -94), (18, -74)]), col))
    # legs: one tucked, one trailing with a coiled spring boot
    out.append(taper(catmull(L([(0, 24), (20, 40), (8, 62)]), 4), 10 * s, 7 * s, col))
    out.append(taper(catmull(L([(-6, 24), (-30, 40), (-50, 52)]), 4), 10 * s, 7 * s, col))
    for k in range(5):
        p = L([(8 + (k % 2) * 6 - 3, 64 + k * 4)])[0]
        out.append(f'<ellipse cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{6 * s:.1f}" ry="{2 * s:.1f}" fill="none" stroke="{col}" stroke-width="2"/>')
    # arms flung out with claws
    for (a, b, c) in (((12, -44), (40, -60), (62, -76)), ((-4, -40), (-20, -70), (-30, -96))):
        out.append(taper(catmull(L([a, b, c]), 4), 7 * s, 4 * s, col))
        hx, hy = L([c])[0]
        for fa in (-130, -90, -50):
            r = math.radians(fa)
            out.append(taper([(hx, hy), (hx + math.cos(r) * 11 * s, hy + math.sin(r) * 11 * s)], 2.4 * s, 0.6, col))
    return "".join(out)


@design("spring-heeled-jack")
def spring_heeled_jack():
    D = Doc2("hr-sj")
    from gouache import paper
    INKC = "#1E140E"
    out = [paper(D.nid(), "#E8D8B4", "#6A4A2A", 11)]
    # masthead of the penny dreadful
    out.append(f'<rect x="40" y="40" width="520" height="96" fill="none" stroke="{INKC}" stroke-width="3"/>')
    out.append(tx(62, 74, "No. 1", DMS, 20, INKC, max_w=90, anchor="start"))
    out.append(tx(538, 74, "ONE PENNY", BEBAS, 23, "#A8201A", ls=1, max_w=110, anchor="end"))
    out.append(tx(300, 72, "THE TERROR OF LONDON", CINZEL, 16, INKC, ls=1, max_w=262))
    out.append(tx(300, 126, "Spring-Heeled Jack", DMS, 50, INKC, max_w=460))
    # the picture: rooftops and chimney pots of Victorian London, hand-coloured over black line
    px0, py0, px1, py1 = 56, 150, 544, 544
    cid = D.clip(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}"/>')
    sc = [f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{D.lin([(0, "#3A4A7A"), (0.7, "#8A9AB8"), (1, "#C8B890")])}"/>']
    sc.append(hatch_in(D, f"M {px0} {py0} L {px1} {py0} L {px1} {py0 + 160} L {px0} {py0 + 160} Z", (px0, py0, px1, py0 + 160), "#1E2A4A", 5, 0, 1.2, 0.5))
    sc.append(f'<circle cx="420" cy="230" r="44" fill="#F2E4A8" stroke="{INKC}" stroke-width="2.4"/>')
    sc.append(soft_glow(D, 420, 230, 120, "#F2E4A8", 0.4))
    rnd = random.Random(5)
    # roof ridges and chimney stacks
    x = px0 - 20
    roofs = []
    while x < px1 + 20:
        w = rnd.uniform(60, 110)
        top = rnd.uniform(400, 440)
        roofs.append((x, w, top))
        x += w - 6
    for (x, w, top) in roofs:
        sc.append(f'<path d="M {x:.1f} 560 L {x:.1f} {top + 24:.1f} L {x + w / 2:.1f} {top:.1f} L {x + w:.1f} {top + 24:.1f} L {x + w:.1f} 560 Z" fill="#4A3A3A" stroke="{INKC}" stroke-width="2"/>')
        sc.append(hatch_in(D, f"M {x:.1f} 560 L {x:.1f} {top + 24:.1f} L {x + w / 2:.1f} {top:.1f} L {x + w:.1f} {top + 24:.1f} L {x + w:.1f} 560 Z", (x, top, x + w, 560), INKC, 5, -30, 1, 0.6))
        if rnd.random() < 0.7:
            cx = x + w * rnd.uniform(0.2, 0.7)
            ch = rnd.uniform(30, 50)
            sc.append(f'<rect x="{cx - 9:.1f}" y="{top + 6 - ch:.1f}" width="18" height="{ch:.1f}" fill="#8A3A2A" stroke="{INKC}" stroke-width="2"/>')
            for j in range(2):
                sc.append(f'<rect x="{cx - 7 + j * 8:.1f}" y="{top - ch - 4:.1f}" width="6" height="12" fill="#A85A3A" stroke="{INKC}" stroke-width="1.6"/>')
            sc.append(smoke(D, [(cx, top - ch - 6), (cx - 10, top - ch - 26), (cx - 30, top - ch - 40)], 2, 8, int(cx), "#C8C8D8", 0.45))
        for j in range(rnd.randint(0, 2)):
            wx = x + w * rnd.uniform(0.2, 0.8)
            sc.append(f'<rect x="{wx - 5:.1f}" y="{top + 40:.1f}" width="10" height="14" fill="#F2C860" stroke="{INKC}" stroke-width="1.4"/>')
    # a gas lamp
    sc.append(f'<path d="M 120 560 L 120 470" stroke="{INKC}" stroke-width="5"/>')
    sc.append(f'<path d="M 108 470 L 132 470 L 128 448 L 112 448 Z" fill="#F2C860" stroke="{INKC}" stroke-width="2"/>')
    sc.append(soft_glow(D, 120, 460, 40, "#FFE8A0", 0.6))
    # Jack, leaping across the moon, breathing blue flame
    sc.append(leaping_jack(320, 300, 1.2, INKC))
    fx, fy = 334, 218
    sc.append(soft_glow(D, fx + 40, fy, 60, "#9AD8FF", 0.6))
    sc.append(f'<g transform="rotate(80 {fx} {fy})">{flame_lick(fx, fy, 76, 26, 5, cols=("#4A9AE8", "#9AD8FF", "#FFFFFF"))}</g>')
    sc.append(f'<g transform="rotate(80 {fx} {fy})"><path d="{flame_lick(fx, fy, 76, 26, 5).split(chr(34))[1]}" fill="none" stroke="{INKC}" stroke-width="1.4"/></g>')
    sc.append(f'<ellipse cx="{fx - 6}" cy="{fy - 6}" rx="3.4" ry="2.4" fill="#E8402A"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="none" stroke="{INKC}" stroke-width="3"/>')
    out.append(f'<rect x="{px0 + 120}" y="{py1 - 34}" width="248" height="26" fill="#E8D8B4" stroke="{INKC}" stroke-width="2"/>')
    out.append(tx(300, py1 - 14, "A PENNY DREADFUL · 1838", CINZEL, 16, INKC, ls=1, max_w=236))
    return fin(D, out, 35, "#3A2A1A", 0.6)


# ================================================================ 25. bloody mary — the mirror at midnight
@design("bloody-mary")
def bloody_mary():
    D = Doc2("hr-bm")
    out = [f'<rect width="600" height="600" fill="#0A0608"/>']
    # damask wallpaper in the dark
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#3A1A22"), (0.6, "#1A0A0E"), (1, "#050204")], 0.5, 0.55, 0.7)}"/>')
    for r_ in range(8):
        for c in range(7):
            x, y = c * 96 + (r_ % 2) * 48, r_ * 84
            out.append(f'<path d="M {x} {y - 22} Q {x + 18} {y} {x} {y + 22} Q {x - 18} {y} {x} {y - 22} Z M {x - 14} {y + 28} Q {x} {y + 18} {x + 14} {y + 28}" fill="#4A1E28" opacity="0.4"/>')
    # the mirror in its baroque gilt frame
    cx, cy, rx, ry = 300, 290, 130, 176
    out.append(cast(D, cx + 8, cy + 10, rx + 30, ry + 30, "#000000", 0.6))
    frame = ell_pts(cx, cy, rx + 26, ry + 26, 0, 360, 60)
    out.append(f'<path d="{smooth_closed(frame)}" fill="{gilt_fill(D, cy - ry - 26, cy + ry + 26)}"/>')
    for k in range(24):
        a = 2 * math.pi * k / 24
        out.append(f'<path d="{blob(cx + math.cos(a) * (rx + 22), cy + math.sin(a) * (ry + 22), 10, 7, k, 0.3, 10, math.degrees(a) + 90)}" fill="#F6DC8A" opacity="0.7"/>')
        out.append(ink(blob(cx + math.cos(a) * (rx + 22), cy + math.sin(a) * (ry + 22), 10, 7, k, 0.3, 10, math.degrees(a) + 90), "#6A4A14", 1, k, 1, 0.6))
    glass = ell_pts(cx, cy, rx, ry, 0, 360, 60)
    out.append(f'<path d="{smooth_closed(glass)}" fill="{D.lin([(0, "#2A2A34"), (0.6, "#14141C"), (1, "#0A0A10")], 0, 0, 0.4, 1)}"/>')
    cid = D.clip(f'<path d="{smooth_closed(glass)}"/>')
    m = []
    # the reflected room: the two candles, and behind them, where nobody stands, a pale woman in a veil
    m.append(soft_glow(D, cx, cy + 40, 150, "#FFB070", 0.25))
    m.append(soft_glow(D, cx + 20, cy - 10, 70, "#C8E0F0", 0.3))
    fig = [(cx + 20, cy - 70), (cx + 4, cy - 62), (cx - 2, cy - 30), (cx - 14, cy + 20), (cx - 26, cy + 120), (cx + 66, cy + 120), (cx + 54, cy + 20),
           (cx + 42, cy - 30), (cx + 36, cy - 62)]
    m.append(f'<path d="{smooth_closed(fig)}" fill="#C8D4DC" opacity="0.5"/>')
    m.append(f'<path d="{blob(cx + 20, cy - 52, 15, 19, 3, 0.05, 12)}" fill="#E8F0F4" opacity="0.7"/>')
    m.append(f'<path d="{smooth_closed([(cx + 4, cy - 72), (cx + 20, cy - 80), (cx + 38, cy - 72), (cx + 48, cy - 20), (cx + 58, cy + 40), (cx + 36, cy + 10), (cx + 20, cy - 30), (cx + 4, cy + 10), (cx - 14, cy + 40), (cx - 4, cy - 20)])}" fill="#0A0A0E" opacity="0.85"/>')
    for sg in (-1, 1):
        m.append(f'<ellipse cx="{cx + 20 + sg * 6}" cy="{cy - 54}" rx="3" ry="2" fill="#0A0A10" opacity="0.8"/>')
    for (x, h) in ((cx - 76, 60), (cx + 76, 60)):
        m.append(candle(D, x, cy + 150, h, int(x), w=12, glow_r=60))
    m.append(f'<path d="M {cx - 80} {cy - ry} L {cx - 10} {cy + ry} L {cx + 10} {cy + ry} L {cx - 60} {cy - ry} Z" fill="#FFFFFF" opacity="0.05"/>')
    m.append(f'<path d="{smooth_closed(glass)}" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.6)])}"/>')
    out.append(f'<g {cid}>{"".join(m)}</g>')
    out.append(ink(smooth_closed(glass), "#4A3008", 3, 2, 1, 0.9))
    # the real candles on the sill in front of the mirror
    out.append(painted(D, poly_pts([(110, 480), (490, 480), (500, 496), (100, 496)], 20, 3, 0.4), ("#8A6A5A", "#4A3028", "#1A0E0A"), 5, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.4, inkc="#050204", hi=0.4))
    for x in (156, 444):
        out.append(candle(D, x, 486, 70, int(x) + 1, w=16, glow_r=130))
    out.append(band(D, 500, 600, "#000000", 0, 0.6))
    # lettering
    out.append(letters(D, 300, 548, "Bloody Mary", SERIF_IT, 66, "#E8343A", ["#FF5A5A", "#B8141A", "#FF8070"], 36, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(tx(300, 76, "DON’T SAY IT THREE TIMES", CINZEL, 17, "#E8C8C8", ls=4, max_w=400))
    return fin(D, out, 36)


# ================================================================ 26. the banshee — keening on the rock by the cottage
@design("the-banshee")
def the_banshee():
    D = Doc2("hr-bs")
    out = [night(D, [(0, "#060A12"), (0.45, "#1A2638"), (0.75, "#3A4A5A"), (1, "#1A2228")], 1)]
    out.append(stars_field(8, (0, 0, 600, 260), 70))
    out.append(moon(D, 120, 236, 40, 8, pal=("#FFFFFF", "#EEF2F4", "#B8C0C8"), glow="#E8F0FF", gs=0.5, glow_r=3.0))
    out.append(puff_cloud(D, 250, 290, 200, 10, ("#3A4A5A", "#1E2836", "#0C1018"), op=0.6))
    # sea far below the headland, the cottage with its one lit window
    out.append(sea(D, 330, 420, [(0, "#3A4A58"), (1, "#1A2430")], 3, ["#8A9AA8", "#0E141C"], 40))
    out.append(hill(D, ridge([(-20, 380), (140, 350), (300, 360), (460, 346), (620, 372)], 4, 6, 4), 640, ("#4A5A44", "#24301E", "#0A100A"), 5, inkw=0, n=50, lit="#B8C8D0"))
    cx_, cb = 150, 360
    out.append(painted(D, poly_pts([(cx_ - 50, cb), (cx_ - 50, cb - 34), (cx_ + 50, cb - 34), (cx_ + 50, cb)], 10, 3, 0.5), ("#C8C8BE", "#8A8A80", "#3A3A34"), 5, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=14, inkw=1.2, inkc="#141410", hi=0.4))
    out.append(painted(D, [(cx_ - 58, cb - 32), (cx_ - 40, cb - 62), (cx_ + 40, cb - 62), (cx_ + 58, cb - 32)], ("#A8946A", "#6A5A38", "#2A2214"), 6, sdir=(0.5, 0.6), sk=0.2, angle=-20, n=20, inkw=1.2, inkc="#141008", hi=0.4))
    out.append(f'<rect x="{cx_ + 22}" y="{cb - 76}" width="10" height="18" fill="#3A3A34"/>')
    out.append(smoke(D, [(cx_ + 27, cb - 78), (cx_ + 10, cb - 100), (cx_ - 20, cb - 112), (cx_ - 60, cb - 116)], 3, 12, 4, "#C8D0D8", 0.4))
    out.append(lit_slit(D, cx_ - 20, cb - 26, 12, 16, "#FFC860"))
    out.append(f'<rect x="{cx_ + 8}" y="{cb - 30}" width="14" height="30" fill="#2A2018"/>')
    # dry-stone wall running across the field
    rnd = random.Random(6)
    for k in range(40):
        x = 210 + k * 9 + rnd.uniform(-2, 2)
        y = 384 - k * 0.6 + rnd.uniform(-1, 1)
        out.append(f'<path d="{blob(x, y, 5, 3.4, k, 0.2, 8)}" fill="{rnd.choice(["#7A8278", "#5A625A", "#9AA298"])}" stroke="#1A1E18" stroke-width="0.8"/>')
    # the near rock and the banshee upon it, her long silver hair streaming in the wind
    out.append(painted(D, poly_pts([(340, 600), (360, 490), (400, 458), (450, 450), (510, 458), (560, 484), (600, 520), (610, 600)], 16, 4, 2), ("#6A7270", "#343A3A", "#0E1212"), 7, sdir=(-0.6, 0.6), sk=0.2, angle=-10, n=40, inkw=1.4, inkc="#060808", hi=0.4))
    rnd = random.Random(7)
    hx, hy = 446, 226
    out.append(soft_glow(D, hx - 10, hy + 90, 190, "#C8DCFF", 0.4))
    g_body = D.lin([(0, "#F6FAFF", 0.95), (0.55, "#DCE8F6", 0.7), (1, "#C8DCF0", 0)], 0, 0, 0, 1)
    # the long hair, streaming far out on the wind (behind her)
    for k in range(20):
        t = k / 19
        pts = [(hx - 4, hy - 12 + t * 26), (hx - 50, hy - 24 + t * 50 + rnd.uniform(-6, 6)), (hx - 130, hy - 14 + t * 80 + rnd.uniform(-8, 8)),
               (hx - 220 - rnd.uniform(0, 50), hy - 30 + t * 120 + rnd.uniform(-12, 12))]
        out.append(taper(catmull(pts, 6), rnd.uniform(3, 7), 0.6, rnd.choice(["#F2F6FA", "#C8D2DA", "#E2E8EE"]), rnd.uniform(0.55, 0.9)))
    # the gown, floating, its hem dissolving into wisps blown to the left
    gown = [(hx - 12, hy + 26), (hx - 22, hy + 70), (hx - 30, hy + 130), (hx - 50, hy + 190), (hx - 110, hy + 220), (hx - 70, hy + 222), (hx - 120, hy + 246),
            (hx - 50, hy + 240), (hx - 20, hy + 260), (hx + 10, hy + 236), (hx + 40, hy + 250), (hx + 34, hy + 200), (hx + 28, hy + 130), (hx + 22, hy + 70), (hx + 14, hy + 26)]
    out.append(f'<path d="{smooth_closed(gown)}" fill="{g_body}"/>')
    for k in range(5):
        out.append(pline([(hx - 6 + k * 6, hy + 40), (hx - 14 + k * 4, hy + 140), (hx - 40 + k * 10, hy + 220)], "#9AB0C8", 1.4, k, 0.5, 1))
    # arms flung up and out, sleeves hanging like veils
    for sg, hand in ((-1, (hx - 70, hy - 50)), (1, (hx + 64, hy - 56))):
        sh = (hx + sg * 12, hy + 30)
        el = ((sh[0] + hand[0]) / 2 + sg * 6, (sh[1] + hand[1]) / 2 + 6)
        out.append(taper(catmull([sh, el, hand], 5), 8, 4, "#EEF4FA", 0.95))
        out.append(f'<path d="{smooth_closed([sh, el, hand, (hand[0] - sg * 8, hand[1] + 40), (el[0] - sg * 20, el[1] + 70), (sh[0] - sg * 10, sh[1] + 60)])}" fill="{g_body}" opacity="0.7"/>')
        out.append(f'<path d="{blob(hand[0], hand[1], 5, 6, sg + 4, 0.1, 8)}" fill="#F6FAFF"/>')
    # her head thrown back, the keen pouring from her open mouth
    face = [(hx - 12, hy + 12), (hx - 16, hy - 6), (hx - 8, hy - 18), (hx + 6, hy - 22), (hx + 16, hy - 16), (hx + 22, hy - 12), (hx + 18, hy - 6), (hx + 22, hy),
            (hx + 16, hy + 8), (hx + 6, hy + 16), (hx - 4, hy + 18)]
    out.append(f'<path d="{smooth_closed(face)}" fill="#F6FAFF"/>')
    out.append(f'<path d="{blob(hx + 16, hy + 1, 3.4, 4.6, 3, 0.1, 8)}" fill="#1A2230"/>')
    out.append(f'<path d="M {hx + 4} {hy - 12} q 5 -2 8 1" stroke="#3A4658" stroke-width="2" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{smooth_closed([(hx - 16, hy - 8), (hx - 10, hy - 22), (hx + 4, hy - 26), (hx - 2, hy - 18), (hx - 10, hy - 4)])}" fill="#C8D2DA"/>')
    for k in range(3):
        out.append(f'<path d="M {hx + 34 + k * 16} {hy - 14 - k * 6} q 14 16 0 34" fill="none" stroke="#DCE8FF" stroke-width="{2.6 - k * 0.6:.1f}" opacity="{0.75 - k * 0.2:.2f}" stroke-linecap="round"/>')
    out.append(grass(10, (0, 420, 340, 600), ["#2A3A24", "#4A5A3A", "#0E140C"], 120, (8, 20), lean=(-0.6, -0.1)))
    out.append(fog(D, 540, 70, 11, "#A8B8C8", 0.45))
    out.append(band(D, 0, 180, "#000000", 0.5, 0))
    # lettering
    out.append(glow_text(D, 300, 116, "THE BANSHEE", JOS, 62, "#F2F6FA", "#A8C8F0", ls=10, max_w=440, shadow="#000000"))
    out.append(tx(300, 150, "Bean Sí · Irish folklore", SERIF_IT, 24, "#C8D8E8", max_w=360))
    out.append(tx(300, 548, "IF YOU HEAR HER KEEN, GO HOME", CINZEL, 16, "#E8EEF4", ls=3, max_w=440))
    return fin(D, out, 37)


# ================================================================ 27. krampus — a postcard from the Alps, 5 December
def krampus(D, x, base, s, seed, fur=("#7A5A44", "#3A261A", "#120A06")):
    """Krampus from the old postcards: long curling goat horns, shaggy fur, a bundle of birch switches, a chain and
    a basket on his back, cloven hooves; striding to the right. (x, base) = ground."""
    def L(pts):
        return T(pts, x, base, s)
    out = [cast(D, x + 10 * s, base, 60 * s, 8 * s, "#000000", 0.4, seed)]
    # basket on the back
    out.append(painted(D, L([(-58, -150), (-30, -156), (-24, -96), (-60, -92)]), ("#C8A060", "#8A6A30", "#3A2A10"), seed + 1, sdir=(0.6, 0.4), sk=0.2, angle=-90, n=10, inkw=1.2, inkc="#1A0E04", hi=0.4))
    for k in range(4):
        out.append(pline(L([(-58, -142 + k * 13), (-27, -146 + k * 13)]), "#5A3A14", 1.4, seed + k, 0.8, 1))
    # legs: goat legs with hocks and hooves
    for (a, b, c, d) in (((-12, -70), (-20, -40), (-8, -22), (-14, 0)), ((14, -70), (28, -44), (20, -24), (30, -2))):
        out.append(taper(catmull(L([a, b, c, d]), 5), 18 * s, 8 * s, fur[1]))
        hx, hy = L([d])[0]
        out.append(f'<path d="{blob(hx + 2 * s, hy - 2 * s, 7 * s, 4 * s, int(hx), 0.1, 8)}" fill="#0A0604"/>')
    # shaggy body
    body = L([(-30, -64), (-34, -100), (-30, -140), (-16, -164), (6, -170), (22, -158), (28, -130), (30, -96), (28, -64)])
    out.append(painted(D, body, fur, seed, sdir=(0.6, 0.4), sk=0.2, angle=-100, n=40, inkw=1.4, inkc="#0A0604", hi=0.35))
    rnd = random.Random(seed)
    for k in range(60):
        px, py = L([(rnd.uniform(-30, 28), rnd.uniform(-160, -60))])[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} q {rnd.uniform(-3, 3):.1f} {5 * s:.1f} {rnd.uniform(-4, 4):.1f} {10 * s:.1f}" stroke="{rnd.choice(fur)}" stroke-width="1.4" fill="none" opacity="0.8"/>')
    for k in range(9):
        px, py = L([(-30 + k * 7, -66)])[0]
        out.append(taper([(px, py), (px + rnd.uniform(-3, 3), py + 10 * s)], 5 * s, 0.6, fur[1]))
    # the head: shaggy, long ears, the great horns curling back
    hx, hy = L([(10, -182)])[0]
    out.append(painted(D, blob_pts(hx, hy, 17 * s, 19 * s, seed + 2, 0.08, 14), fur, seed + 2, sdir=(0.6, 0.4), sk=0.2, n=10, inkw=1.2, inkc="#0A0604", hi=0.35))
    out.append(poly(L([(16, -186), (36, -180), (40, -172), (30, -168), (16, -170)]), fur[1]))
    for sg, off in ((-1, -6), (1, 8)):
        horn = catmull(L([(off, -196), (off + sg * 10, -224), (off + sg * 30, -240), (off + sg * 46, -232), (off + sg * 48, -214)]), 6)
        out.append(taper(horn, 9 * s, 2 * s, "#3A2A1A" if sg < 0 else "#5A4430"))
        for k in range(1, len(horn) - 2, 3):
            px, py = horn[k]
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.6 * s:.1f}" fill="#C8A878" opacity="0.5"/>')
    ex, ey = L([(22, -186)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#FFD040"/>')
    out.append(sharp(L([(24, -170), (28, -158), (30, -170)]), "#F2E8D8"))
    # the arm raised with the bundle of birch switches, the other trailing a chain
    out.append(taper(catmull(L([(18, -150), (40, -160), (52, -184)]), 5), 14 * s, 10 * s, fur[1]))
    sx, sy = L([(52, -186)])[0]
    for k in range(9):
        a = math.radians(-70 + k * 5)
        out.append(taper([(sx, sy + 14 * s), (sx + math.cos(a) * 70 * s, sy + math.sin(a) * 70 * s)], 2.2 * s, 0.6, rnd.choice(["#5A4024", "#8A6A40", "#3A2814"])))
    out.append(f'<path d="M {sx - 4:.1f} {sy - 2:.1f} L {sx + 6:.1f} {sy + 8:.1f}" stroke="#A8201A" stroke-width="{4 * s:.1f}"/>')
    out.append(taper(catmull(L([(-24, -140), (-40, -110), (-44, -90)]), 5), 13 * s, 9 * s, fur[1]))
    cx_, cy_ = L([(-44, -88)])[0]
    for k in range(9):
        out.append(f'<ellipse cx="{cx_ + k * 3 * s:.1f}" cy="{cy_ + k * 8 * s:.1f}" rx="{2.6 * s:.1f}" ry="{4 * s:.1f}" fill="none" stroke="#B8BCC4" stroke-width="{1.6 * s:.1f}" transform="rotate({(k % 2) * 60} {cx_ + k * 3 * s:.1f} {cy_ + k * 8 * s:.1f})"/>')
    # a cow bell at the waist
    bx, by = L([(6, -72)])[0]
    out.append(f'<path d="M {bx - 6 * s:.1f} {by:.1f} L {bx + 6 * s:.1f} {by:.1f} L {bx + 8 * s:.1f} {by + 12 * s:.1f} L {bx - 8 * s:.1f} {by + 12 * s:.1f} Z" fill="#C8963A" stroke="#3A2408" stroke-width="1.2"/>')
    return "".join(out)


@design("krampus")
def krampus_card():
    D = Doc2("hr-kr")
    from gouache import paper
    out = [paper(D.nid(), "#F2E8D2", "#7A5A3A", 12)]
    RED = "#B01E1E"
    # the postcard: a red ruled border with rounded corners
    out.append(f'<rect x="30" y="30" width="540" height="540" rx="16" fill="none" stroke="{RED}" stroke-width="5"/>')
    out.append(f'<rect x="42" y="42" width="516" height="516" rx="10" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    # the picture panel
    px0, py0, px1, py1 = 70, 140, 530, 500
    cid = D.clip(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" rx="10"/>')
    sc = [sky(D, [(0, "#0E1A3A"), (0.6, "#2A3A6A"), (1, "#5A6A90")], 2, 600, ["#1A2A5A", "#060A1E", "#3A4A7A"], 40)]
    sc.append(stars_field(3, (px0, py0, px1, 300), 50))
    sc.append(hill(D, ridge([(40, 300), (140, 230), (220, 270), (310, 200), (400, 260), (480, 220), (560, 290)], 4, 8, 4), 600, ("#E8F0FF", "#9AAAD0", "#4A5A8A"), 4, inkw=0, n=30, lit="#FFFFFF"))
    # the village: chalets with lit windows and snowy roofs
    for k, (hx, w, h) in enumerate(((110, 80, 60), (200, 70, 74), (420, 90, 66), (510, 70, 56))):
        b = 420
        sc.append(painted(D, poly_pts([(hx - w / 2, b), (hx - w / 2, b - h), (hx + w / 2, b - h), (hx + w / 2, b)], 12, k, 0.4), ("#8A6A4A", "#5A3E28", "#24160C"), 10 + k, sdir=(0.6, 0.3), sk=0.2, angle=-90, n=12, inkw=1.2, inkc="#140A04", hi=0.3))
        sc.append(painted(D, [(hx - w / 2 - 12, b - h + 4), (hx, b - h - 40), (hx + w / 2 + 12, b - h + 4)], ("#FFFFFF", "#DCE6F6", "#8A9AC0"), 20 + k, sdir=(0.5, 0.6), sk=0.2, angle=-30, n=8, inkw=1.2, inkc="#2A3450", hi=0.5))
        for j in range(2):
            wx = hx - w * 0.22 + j * w * 0.44
            sc.append(soft_glow(D, wx, b - h * 0.5, 22, "#FFC860", 0.5))
            sc.append(f'<rect x="{wx - 6:.1f}" y="{b - h * 0.6:.1f}" width="12" height="14" fill="#FFD27A" stroke="#140A04" stroke-width="1.6"/>')
    sc.append(hill(D, [(40, 430), (300, 424), (560, 432)], 600, ("#FFFFFF", "#DCE6F6", "#9AAAC8"), 30, inkw=0, n=30))
    sc.append(f'<path d="M 200 520 Q 280 470 300 430 L 330 430 Q 340 470 420 520 Z" fill="#B8C8E0" opacity="0.5"/>')
    sc.append(krampus(D, 300, 470, 1.18, 14))
    sc.append(snowfall(15, (px0, py0, px1, py1), 90, (0.8, 2.6), "#FFFFFF", (0.5, 1)))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" rx="10" fill="none" stroke="#2A1A0E" stroke-width="2.4"/>')
    # the greeting, the stamp and its postmark
    out.append(letters(D, 244, 112, "Gruß vom Krampus!", SERIF_IT, 50, RED, ["#D02A2A", "#8A1010"], 38, max_w=340, wob=0.3))
    sx, sy = 494, 92
    out.append(f'<rect x="{sx - 26}" y="{sy - 32}" width="52" height="62" fill="#FFF8E8" stroke="#2A1A0E" stroke-width="1.4" stroke-dasharray="3 2"/>')
    out.append(f'<rect x="{sx - 20}" y="{sy - 26}" width="40" height="50" fill="#2E6A48"/>')
    out.append(tx(sx, sy + 4, "5", DMS, 26, "#F2E8D2", max_w=30))
    out.append(f'<path d="M {sx - 14} {sy + 16} L {sx + 14} {sy + 16}" stroke="#F2E8D2" stroke-width="2"/>')
    out.append(f'<circle cx="{sx - 14}" cy="{sy + 20}" r="22" fill="none" stroke="#3A2A4A" stroke-width="2" opacity="0.55"/>')
    for k in range(3):
        out.append(f'<path d="M {sx - 6} {sy + 12 + k * 7} q 8 -4 16 0 t 16 0" fill="none" stroke="#3A2A4A" stroke-width="1.6" opacity="0.5"/>')
    out.append(tx(300, 538, "ALPINE FOLKLORE · THE NIGHT OF 5 DECEMBER", CINZEL, 16, "#2A1A0E", ls=1, max_w=456))
    return fin(D, out, 39, "#3A2A1A", 0.55)


# ================================================================ 28. will-o'-the-wisp — never follow the lights
@design("will-o-the-wisp")
def will_o_the_wisp():
    D = Doc2("hr-wi")
    out = [night(D, [(0, "#02060A"), (0.45, "#0A1A1E"), (0.7, "#1A3434"), (1, "#081414")], 1)]
    out.append(stars_field(9, (0, 0, 600, 260), 60))
    out.append(puff_cloud(D, 300, 250, 400, 4, ("#2A3E3E", "#142424", "#060E0E"), op=0.7))
    # the bog: low far line of dead trees, mist, black pools
    out.append(hill(D, ridge([(-20, 330), (160, 322), (360, 330), (620, 320)], 3, 4, 3), 640, ("#1E3230", "#0E1C1A", "#040A0A"), 2, inkw=0, n=20))
    for (x, h) in ((80, 70), (130, 50), (470, 80), (540, 56)):
        out.append(crooked_tree(x, 330, h, int(x), "#040A0A", w=5, spread=34, depth=3))
    out.append(fog(D, 336, 50, 3, "#8AC8B8", 0.4))
    rnd = random.Random(5)
    for k in range(7):
        x, y = rnd.uniform(40, 560), rnd.uniform(380, 560)
        out.append(f'<path d="{blob(x, y, rnd.uniform(40, 90), rnd.uniform(8, 16), k, 0.2, 14)}" fill="#020606"/>')
        out.append(f'<path d="{blob(x, y - 2, rnd.uniform(20, 50), 3, k + 9, 0.2, 10)}" fill="#6AC8B0" opacity="0.15"/>')
    # the plank walk winding into the marsh
    path = [(250, 600), (290, 540), (330, 490), (310, 440), (350, 400), (380, 366)]
    for i in range(len(path) - 1):
        (ax, ay), (bx, by) = path[i], path[i + 1]
        n = 6
        for j in range(n):
            t = j / n
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            w = 40 * (y / 600) + 6
            out.append(f'<path d="M {x - w:.1f} {y:.1f} L {x + w:.1f} {y - 2:.1f}" stroke="#4A3A2A" stroke-width="{max(2, w * 0.18):.1f}" stroke-linecap="round"/>')
            out.append(f'<path d="M {x - w:.1f} {y + 1:.1f} L {x + w:.1f} {y - 1:.1f}" stroke="#8A7A5A" stroke-width="1" opacity="0.4"/>')
    # the wisps: pale lights bobbing away into the mist
    lights = [(388, 350, 10), (430, 316, 8), (470, 290, 6.5), (504, 268, 5), (534, 254, 4)]
    for k, (x, y, r) in enumerate(lights):
        out.append(soft_glow(D, x, y, r * 6, "#7AFFD8", 0.5))
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E8FFF4"/>')
        out.append(f'<path d="{blob(x, y + 70 - k * 6, r * 1.6, 2, k, 0.2, 8)}" fill="#7AFFD8" opacity="0.3"/>')
    # the traveller with his lantern, following
    tx_, ty_ = 300, 528
    out.append(tiny_cloak_figure(tx_, ty_, 1.5, "#020606", rim="#FFC870", hood=False, facing=1))
    out.append(taper([(tx_ + 12, ty_ - 52), (tx_ + 24, ty_ - 44), (tx_ + 30, ty_ - 38)], 5, 4, "#020606"))
    out.append(soft_glow(D, tx_ + 32, ty_ - 28, 46, "#FFC870", 0.7))
    out.append(f'<rect x="{tx_ + 27}" y="{ty_ - 36}" width="10" height="14" fill="#FFE8A0" stroke="#020606" stroke-width="2"/>')
    out.append(f'<path d="M {tx_ + 16} 560 L {tx_ + 50} 560" stroke="#FFC870" stroke-width="2" opacity="0.3"/>')
    # rushes in the foreground
    for side, x0 in ((-1, 0), (1, 600)):
        for k in range(18):
            x = x0 - side * rnd.uniform(0, 130)
            h = rnd.uniform(50, 150)
            out.append(taper([(x, 610), (x + side * rnd.uniform(2, 14), 610 - h * 0.6), (x + side * rnd.uniform(6, 24), 610 - h)], 3.4, 0.8, "#020606"))
            if rnd.random() < 0.3:
                ex, ey = x + side * rnd.uniform(6, 24), 610 - h
                out.append(f'<path d="{blob(ex, ey + 8, 3, 10, k, 0.1, 8)}" fill="#1A120A"/>')
    out.append(band(D, 0, 190, "#000000", 0.55, 0))
    # lettering
    out.append(glow_text(D, 300, 116, "Will-o’-the-Wisp", SERIF_IT, 70, "#F2FFF8", "#7AFFD8", ls=0, max_w=440, shadow="#000000"))
    out.append(tx(300, 152, "ENGLISH FOLKLORE", CINZEL, 16, "#B8E8D8", ls=6, max_w=300))
    out.append(tx(300, 548, "Never follow the lights.", SERIF_IT, 26, "#E8FFF4", max_w=400))
    return fin(D, out, 40)


# ================================================================ 29. the signal-man — halloa! below there!
@design("the-signal-man")
def the_signal_man():
    D = Doc2("hr-sm")
    out = [night(D, [(0, "#0A0A10"), (0.4, "#24222E"), (0.75, "#4A3E3A"), (1, "#1A1614")], 1)]
    # the deep cutting: two walls of wet rock converging on the tunnel
    vx, vy = 300, 330
    lw = [(-20, -10), (220, -10), (250, 300), (262, 420), (-20, 640)]
    rw = [(620, -10), (380, -10), (350, 300), (338, 420), (620, 640)]
    for k, wall in enumerate((lw, rw)):
        out.append(painted(D, poly_pts(wall, 30, k, 3), ("#5A5650", "#2E2C2A", "#0E0E0C"), 3 + k, sdir=(1 if k == 0 else -1, 0.2), sk=0.12, angle=-80 if k == 0 else -100, n=120, inkw=0, hi=0.25))
        rnd = random.Random(k)
        for j in range(20):
            y = rnd.uniform(0, 600)
            x0 = (0 if k == 0 else 600)
            x1 = (240 if k == 0 else 360) * (1 - y / 900) + (x0 * y / 900)
            out.append(pline([(x0, y), ((x0 + x1) / 2, y + rnd.uniform(-8, 8)), (x1, y + rnd.uniform(-6, 6))], "#0A0A08", 1.4, j, 0.4, 1))
    # the tunnel mouth: a black arch in dressed stone
    out.append(painted(D, poly_pts([(230, 420), (230, 290), (370, 290), (370, 420)], 14, 6, 0.4), ("#6A645A", "#3A362E", "#141210"), 7, sdir=(0.6, 0.3), sk=0.15, angle=-90, n=30, inkw=1.4, inkc="#060504", hi=0.3))
    out.append(f'<path d="{smooth_closed(arch_pts(254, 346, 350, 424, 6))}" fill="#020202"/>')
    for k in range(9):
        a = math.pi + math.pi * (k + 0.5) / 9
        out.append(f'<path d="M {300 + math.cos(a) * 46:.1f} {350 + math.sin(a) * 46:.1f} L {300 + math.cos(a) * 62:.1f} {350 + math.sin(a) * 62:.1f}" stroke="#141210" stroke-width="2"/>')
    # the red danger light above the tunnel
    out.append(taper([(388, 420), (388, 250)], 5, 4, "#141210"))
    out.append(f'<rect x="378" y="232" width="20" height="26" rx="3" fill="#141210"/>')
    out.append(soft_glow(D, 388, 244, 90, "#FF2A1A", 0.6))
    out.append(f'<circle cx="388" cy="244" r="7" fill="#FF6A4A"/>')
    out.append(f'<path d="M 260 420 L 340 420 L 420 600 L 180 600 Z" fill="{D.lin([(0, "#FF2A1A", 0.18), (1, "#FF2A1A", 0)])}"/>')
    # the rails and sleepers running out of the tunnel
    for k in range(14):
        y = 424 + k * k * 1.0 + k * 4
        w = 34 + (y - 424) * 0.9
        out.append(f'<path d="M {300 - w:.1f} {y:.1f} L {300 + w:.1f} {y:.1f}" stroke="#2A2018" stroke-width="{2 + k * 0.5:.1f}"/>')
    for sg in (-1, 1):
        out.append(f'<path d="M {300 + sg * 18} 424 L {300 + sg * 130} 610" stroke="#A8A49A" stroke-width="3"/>')
    # the spectre at the tunnel mouth: left arm across the face, right arm waving violently
    gx, gb = 300, 420
    out.append(soft_glow(D, gx, gb - 40, 60, "#C8D8C8", 0.3))
    out.append(poly([(gx - 12, gb), (gx - 10, gb - 40), (gx - 12, gb - 64), (gx - 4, gb - 74), (gx + 6, gb - 74), (gx + 12, gb - 64), (gx + 10, gb - 40), (gx + 12, gb)], "#B8C4B8"))
    out.append(f'<path d="{blob(gx, gb - 82, 7, 8, 3, 0.06, 10)}" fill="#B8C4B8"/>')
    out.append(taper([(gx + 8, gb - 66), (gx - 6, gb - 78), (gx - 12, gb - 84)], 6, 5, "#DCE6DC"))
    for k, a_ in enumerate((-40, -60, -80)):
        a = math.radians(a_)
        out.append(taper([(gx - 8, gb - 66), (gx - 8 - 20 * math.cos(math.radians(30)), gb - 80), (gx - 8 - 26 * math.cos(a) - 12, gb - 80 + 30 * math.sin(a))], 5, 4, "#DCE6DC", 0.9 if k == 0 else 0.25))
    # the signal-box up on the bank: a ledge of rock, a timber hut on stilts with a row of lit windows
    out.append(painted(D, poly_pts([(384, 262), (400, 250), (520, 246), (600, 250), (610, 300), (560, 290), (470, 284), (400, 280)], 14, 9, 1.5), ("#6A645A", "#3A362E", "#141210"), 12, sdir=(0.5, 0.8), sk=0.2, angle=0, n=20, inkw=1.2, inkc="#060504", hi=0.35))
    for x in (410, 446, 484):
        out.append(taper([(x, 240), (x, 256)], 4, 4, "#141210"))
    out.append(sharp([(404, 236), (404, 186), (490, 186), (490, 236)], "#141210"))
    out.append(sharp([(396, 190), (447, 164), (498, 190)], "#141210"))
    out.append(soft_glow(D, 447, 206, 60, "#FFD27A", 0.4))
    for k in range(4):
        out.append(f'<rect x="{412 + k * 19}" y="196" width="15" height="16" fill="#FFD27A"/>')
    out.append(sharp([(404, 236), (500, 236), (500, 242), (404, 242)], "#141210"))
    out.append(band(D, 0, 190, "#000000", 0.5, 0))
    out.append(band(D, 500, 600, "#000000", 0, 0.75))
    # lettering
    out.append(block(D, 300, 112, "THE SIGNAL-MAN", BEBAS, 76, "#F2E8D8", "#7A0A06", depth=6, ang=(0.6, 1.0), ls=6, max_w=440, face2="#E8C8B0", shadow="#000000"))
    out.append(tx(300, 150, "CHARLES DICKENS · 1866", CINZEL, 16, "#E8D8C8", ls=4, max_w=300))
    out.append(tx(300, 548, "“Halloa! Below there!”", SERIF_IT, 34, "#FFE8D8", max_w=420))
    return fin(D, out, 41)


# ================================================================ 30. the demeter — driven ashore at Whitby
def schooner(D, x, wl, s, seed, col="#06080C", rim="#C8D8E8", tilt=-8):
    def L(pts):
        return rot(T(pts, x, wl, s), x, wl, tilt)
    out = [poly(L([(-110, -10), (90, -14), (120, -34), (110, -8), (80, 12), (-90, 12), (-118, -20)]), col)]
    out.append(taper(L([(110, -26), (170, -46)]), 3 * s, 1.6 * s, col))
    for (mx, mh) in ((-40, 190), (30, 210)):
        out.append(taper(L([(mx, -10), (mx, -10 - mh)]), 4 * s, 2 * s, col))
        for k, yy in enumerate((0.35, 0.6, 0.82)):
            ww = (1 - yy) * 80 + 18
            out.append(taper(L([(mx - ww / 2, -10 - mh * yy), (mx + ww / 2, -10 - mh * yy)]), 2.4 * s, 2.4 * s, col))
        # torn sails flogging in the gale: ragged strips streaming from the yards
        for j, yy in enumerate((0.35, 0.6)):
            ww = (1 - yy) * 80 + 18
            top = -10 - mh * yy
            rag = L([(mx - ww / 2, top), (mx + ww / 2, top), (mx + ww / 2 + 16, top + 18), (mx + ww / 2 + 4, top + 22), (mx + 10, top + 30),
                     (mx, top + 22), (mx - 14, top + 34), (mx - 22, top + 20), (mx - ww / 2, top + 26)])
            out.append(f'<path d="{pd(rag)}" fill="#C8C2B0" opacity="0.92"/>')
            out.append(f'<path d="{pd(rag)}" fill="none" stroke="#0A0A08" stroke-width="1.2"/>')
    for a, b in (((-118, -20), (-40, -200)), ((-40, -200), (30, -220)), ((30, -220), (170, -46)), ((-40, -200), (-90, 10)), ((30, -220), (80, 10))):
        p, q = L([a, b])
        out.append(f'<path d="M {p[0]:.1f} {p[1]:.1f} L {q[0]:.1f} {q[1]:.1f}" stroke="{col}" stroke-width="1.3"/>')
    out.append(ink(smooth_open(L([(-118, -20), (-110, -10), (90, -14), (120, -34)])), rim, 1.6, seed, 1, 0.7))
    return "".join(out)


@design("the-demeter")
def the_demeter():
    D = Doc2("hr-dm")
    out = [night(D, [(0, "#04080C"), (0.45, "#14262E"), (0.75, "#2E4448"), (1, "#0E1A1E")], 1)]
    out.append(puff_cloud(D, 120, 180, 320, 2, ("#3A4E54", "#1A2A30", "#060E12"), op=0.95))
    out.append(puff_cloud(D, 470, 160, 340, 3, ("#4A5E64", "#20323A", "#081216"), op=0.95))
    out.append(lightning(520, 110, 470, 300, 4, 2))
    # the East Cliff: the ruined abbey's lancets and the old church against the storm
    out.append(hill(D, [(330, 300), (420, 270), (500, 262), (620, 258)], 640, ("#3A4440", "#1A221E", "#060A08"), 5, inkw=0, n=30))
    ab = 470
    out.append(sharp([(ab - 50, 266), (ab - 50, 196), (ab + 50, 196), (ab + 50, 266)], "#0A100E"))
    for k in range(3):
        x = ab - 30 + k * 30
        out.append(f'<path d="{smooth_closed(arch_pts(x - 8, x + 8, 212, 252, 4, "pointed", 0.8))}" fill="#3A4E54"/>')
    out.append(sharp([(ab - 50, 196), (ab - 38, 172), (ab - 26, 196)], "#0A100E"))
    out.append(sharp([(ab + 26, 196), (ab + 38, 168), (ab + 50, 196)], "#0A100E"))
    out.append(sharp([(380, 286), (380, 254), (420, 254), (420, 286)], "#0A100E"))
    out.append(sharp([(392, 254), (392, 232), (408, 232), (408, 254)], "#0A100E"))
    # the sea: great breakers
    out.append(swell(D, 330, 8, 140, 0.4, ("#4A6A6A", "#1E3638", "#061012"), 4, bottom=640))
    out.append(swell(D, 380, 12, 180, 1.4, ("#3E5E5E", "#183032", "#040C0E"), 5, bottom=640))
    # the schooner, driven in before the gale
    out.append(schooner(D, 240, 420, 1.0, 6))
    out.append(swell(D, 440, 14, 220, 2.6, ("#3A5858", "#142A2C", "#020808"), 7, bottom=640))
    # the sand and, leaping from the bow onto it, an immense dog
    out.append(hill(D, [(-20, 520), (200, 506), (420, 514), (620, 500)], 640, ("#8A8070", "#4A4438", "#1A1810"), 8, inkw=0, n=30))
    out.append(f'<path d="M -20 512 Q 160 496 300 510 Q 440 520 620 500" fill="none" stroke="#E8F2F2" stroke-width="4" opacity="0.6"/>')
    # the great dog: shaggy, heavy-chested, mid-leap from the wreck to the sand
    dg = lambda pts: T(pts, 372, 484, 1.0)
    out.append(taper(catmull(dg([(-40, -6), (-62, -14), (-80, -8)]), 5), 10, 3, "#020406"))
    out.append(poly(dg([(-44, -14), (-30, -30), (0, -34), (30, -34), (52, -40), (66, -48), (80, -48), (90, -40), (88, -30), (74, -24), (56, -6),
                        (40, 4), (14, 2), (-14, 4), (-36, 6)]), "#020406"))
    out.append(poly(dg([(60, -48), (64, -64), (72, -54)]), "#020406"))
    out.append(poly(dg([(80, -46), (98, -40), (100, -34), (86, -32)]), "#020406"))
    for (a, b, c) in (((-30, 0), (-54, 10), (-76, 8)), ((-20, 2), (-40, 18), (-60, 22)), ((40, 0), (64, 10), (88, 4)), ((30, 2), (56, 18), (80, 20))):
        out.append(taper(catmull(dg([a, b, c]), 4), 12, 6, "#020406"))
    rnd = random.Random(12)
    for k in range(14):
        px, py = dg([(rnd.uniform(-36, 60), rnd.uniform(-34, -26))])[0]
        out.append(taper([(px, py + 3), (px - 4, py - 6)], 4, 0.6, "#020406"))
    out.append(f'<circle cx="{dg([(80, -42)])[0][0]:.1f}" cy="{dg([(80, -42)])[0][1]:.1f}" r="2.4" fill="#FF4A2A"/>')
    out.append(ink(smooth_open(dg([(-30, -30), (0, -34), (30, -34), (52, -40), (66, -48), (80, -48), (90, -40)])), "#A8C8D0", 1.4, 3, 1, 0.6))
    out.append(rain(6, 140, "#C8D8E0", (0.1, 0.3), -12, 26))
    out.append(band(D, 0, 200, "#000000", 0.5, 0))
    out.append(band(D, 510, 600, "#000000", 0, 0.75))
    # lettering
    out.append(letters(D, 300, 118, "The Demeter", DMS, 78, "#F2F6F2", ["#FFFFFF", "#D8E8E8"], 41, max_w=420, shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(tx(300, 152, "LOG OF A RUSSIAN SCHOONER · WHITBY", MONO, 16, "#C8DCDC", ls=1, max_w=440))
    out.append(sub_rule(300, 548, "DRACULA · BRAM STOKER · 1897", CINZEL, 17, "#E8F2F2", ls=2, max_w=380, line="#8AB8B8", line_w=24))
    return fin(D, out, 42)


# ================================================================ build
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
