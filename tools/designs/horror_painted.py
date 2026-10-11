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


# ================================================================ gallery toolkit (2026 repaint): soft light, lost edges, ink texture
# Everything below paints in light rather than in outlines: value gradients along a light direction, blurred shadow
# cores and reflected light, crisp rims only where the eye should go, fog and clouds built from many soft puffs,
# Finlay-style stipple and engraved hatching for texture. Each design ends with gfin() (painterly varnish).
from painterly import painterly as _painterly
import re as _re


def gb(D, sd):
    """filter attribute for a gaussian blur of sd px (soft, lost edges)."""
    key = ("gb", sd)
    if key not in D.cache:
        i = D.nid()
        D.defs.append(f'<filter id="{i}" x="-200" y="-200" width="1000" height="1000" filterUnits="userSpaceOnUse">'
                      f'<feGaussianBlur stdDeviation="{sd}"/></filter>')
        D.cache[key] = f'filter="url(#{i})"'
    return D.cache[key]


def soft(D, inner, sd, op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return f'<g {gb(D, sd)}{o}>{inner}</g>'


def _unit(v):
    L = math.hypot(*v) or 1
    return v[0] / L, v[1] / L


def gform(D, pts, pal, seed, light=(-0.6, -0.8), angle=-90, n=None, core=0.3, core_op=0.75, refl=None, refl_op=0.35,
          hi_op=0.5, hik=0.07, rim=None, rim_w=2.4, rim_op=0.9, rim_blur=0.6, slen=None, sw=None, sop=(0.1, 0.3),
          cols=None, edge=None, edge_w=1.4, edge_op=0.55, lost=0, closed=True, d=None, sharp=False):
    """A form painted in light. pal = (light, mid, dark). A value gradient along the light, a soft (blurred) shadow
    core on the far side, a breath of reflected light at the very shadow edge, a soft lit crescent, form-following
    translucent strokes, an optional crisp rim light, and a broken (lost-and-found) edge line instead of an outline."""
    hi, mid, dkc = pal
    if sharp:
        closed = False
    d = d or (smooth_closed(pts) if closed else pd(pts))
    x0, y0, x1, y1 = bbox(pts)
    W, H = max(1, x1 - x0), max(1, y1 - y0)
    lx, ly = _unit(light)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = 0.5 * math.hypot(W * lx, H * ly) + 1
    g = D.lin([(0, hi), (0.42, mid), (1, dkc)], cx + lx * R, cy + ly * R, cx - lx * R, cy - ly * R, "userSpaceOnUse")
    out = []
    if lost:
        out.append(f'<path d="{d}" fill="{mid}" {gb(D, lost)} opacity="0.7"/>')
    out.append(f'<path d="{d}" fill="{g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    m = min(W, H)

    def sh(k):
        return smooth_closed(shift(pts, lx * W * k, ly * H * k)) if closed else pd(shift(pts, lx * W * k, ly * H * k))
    if core:
        inner.append(f'<path d="{d} {sh(core)}" fill-rule="evenodd" fill="{dkc}" opacity="{core_op}" {gb(D, round(max(1.5, m * 0.07), 1))}/>')
    if refl:
        inner.append(f'<path d="{d} {sh(0.05)}" fill-rule="evenodd" fill="{refl}" opacity="{refl_op}" {gb(D, round(max(1, m * 0.025), 1))}/>')
    if hi_op:
        inner.append(f'<path d="{d} {sh(-hik)}" fill-rule="evenodd" fill="{hi}" opacity="{hi_op}" {gb(D, round(max(1, m * 0.04), 1))}/>')
    n = n if n is not None else int(max(8, min(200, W * H / 110)))
    if n:
        vert = abs(math.sin(math.radians(angle))) > 0.7
        slen = slen or (0.1 * (H if vert else W), 0.35 * (H if vert else W))
        sw = sw or (max(0.6, m * 0.012), max(1.2, m * 0.035))
        inner.append(strokes(D.nid(), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), cols or [hi, dkc, mid, hi], seed + 1, n=n, angle=angle,
                             length=slen, width=sw, opacity=sop, curve=0.22))
    if rim:
        rw = rim_w
        inner.append(f'<path d="{d} {smooth_closed(shift(pts, -lx * rw, -ly * rw)) if closed else pd(shift(pts, -lx * rw, -ly * rw))}" fill-rule="evenodd" '
                     f'fill="{rim}" opacity="{rim_op}"' + (f' {gb(D, rim_blur)}' if rim_blur else "") + "/>")
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if edge:
        rnd = random.Random(seed + 7)
        dash = " ".join(f"{rnd.uniform(14, 60):.0f} {rnd.uniform(6, 34):.0f}" for _ in range(6))
        out.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{edge_w}" stroke-dasharray="{dash}" '
                   f'stroke-linecap="round" stroke-linejoin="round" opacity="{edge_op}"/>')
    return "".join(out)


def rimlit(D, pts, fill, rim, light=(-0.6, -0.8), w=2.2, op=0.9, blur=0.5, glow=None, glow_op=0.35, d=None):
    """A silhouette against light: flat dark body, a thin crisp rim on the side that faces the light and an optional
    soft halo of the light bleeding round the edge."""
    d = d or smooth_closed(pts)
    lx, ly = _unit(light)
    out = []
    if glow:
        out.append(f'<path d="{d}" fill="none" stroke="{glow}" stroke-width="{w * 4:.1f}" opacity="{glow_op}" {gb(D, w * 2.5)}/>')
    out.append(f'<path d="{d}" fill="{fill}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    out.append(f'<g {cid}><path d="{d} {smooth_closed(shift(pts, -lx * w, -ly * w))}" fill-rule="evenodd" fill="{rim}" opacity="{op}"'
               + (f' {gb(D, blur)}' if blur else "") + "/></g>")
    return "".join(out)


def union_rim(D, ds, rim, dx, dy, op=0.85, blur=0.5, glow=None, glow_op=0.3, glow_w=6):
    """Rim light on the OUTER contour of a silhouette made of several overlapping shapes (ds = path strings): a mask of
    the union minus the union shifted away from the light by (dx, dy). Returns (behind, front): an optional soft glow
    to draw before the silhouette, and the rim to draw after it."""
    mid = D.nid()
    shapes = "".join(f'<path d="{d}"/>' for d in ds)
    D.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="800" height="800"><g fill="#FFFFFF">{shapes}</g>'
                  f'<g fill="#000000" transform="translate({dx:.2f} {dy:.2f})">{shapes}</g></mask>')
    front = f'<g mask="url(#{mid})"><rect x="-20" y="-20" width="640" height="640" fill="{rim}" opacity="{op}"' + (f' {gb(D, blur)}' if blur else "") + "/></g>"
    behind = ""
    if glow:
        behind = f'<g fill="none" stroke="{glow}" stroke-width="{glow_w}" opacity="{glow_op}" {gb(D, glow_w * 0.8)}>{shapes}</g>'
    return behind, front


def limb_w(a, b, c, d, split=0.5, bulge=0.15):
    """Width profile for a two-segment limb (thigh+shin or upper arm+forearm): a at the root, b at the joint, c at the
    belly of the lower segment, d at the wrist/ankle, with a little muscle swell on the upper segment."""
    def f(t):
        if t < split:
            u = t / split
            return a + (b - a) * u + a * bulge * math.sin(math.pi * u)
        u = (t - split) / (1 - split)
        if u < 0.3:
            return b + (c - b) * (u / 0.3)
        return c + (d - c) * ((u - 0.3) / 0.7)
    return f


def crown(D, cx, cy, rx, ry, seed, cols, light=(-1, -0.4), n=70, dab=(0.12, 0.22), rim=None, soft_sd=0.6, trunk=None):
    """A broad tree crown painted from many overlapping irregular dabs: darker inside and away from the light,
    lighter on the lit side, ragged edges; optional trunk (x, base, w)."""
    rnd = random.Random(seed)
    lx, ly = _unit(light)
    out = []
    if trunk:
        tx_, tb, tw = trunk
        out.append(taper([(tx_, tb), (tx_ + rnd.uniform(-4, 4), (tb + cy) / 2), (cx, cy)], tw, tw * 0.5, cols[-1]))
    items = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        v = (math.cos(a) * lx + math.sin(a) * ly) * r
        sz = rnd.uniform(*dab) * min(rx, ry * 1.6)
        k = 0 if v > 0.35 else (1 if v > -0.2 else 2)
        items.append((v, x, y, sz, cols[min(k, len(cols) - 1)]))
    dabs = "".join(f'<path d="{blob(x, y, sz, sz * 0.7, rnd.randint(0, 9999), 0.3, 9, rnd.uniform(0, 180))}" fill="{c}" opacity="{rnd.uniform(0.8, 1):.2f}"/>'
                   for v, x, y, sz, c in sorted(items))
    out.append(soft(D, dabs, soft_sd))
    if rim:
        rr = [(x + lx * sz * 0.4, y + ly * sz * 0.4, sz) for v, x, y, sz, c in sorted(items)[-n // 5:]]
        out.append(soft(D, "".join(f'<path d="{blob(x, y, sz * 0.5, sz * 0.25, rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rim}" opacity="0.6"/>' for x, y, sz in rr), 0.6))
    return "".join(out)


def stipple(D, d, box, seed, col, n=600, light=(-0.6, -0.8), r=(0.45, 1.25), gamma=1.5, op=(0.45, 0.9), floor=0.0):
    """Virgil Finlay stipple: ink dots whose density grows away from the light (clipped to d)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    lx, ly = _unit(light)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = 0.5 * math.hypot((x1 - x0) * lx, (y1 - y0) * ly) + 1
    dots = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        t = 0.5 - ((x - cx) * lx + (y - cy) * ly) / (2 * R)
        if rnd.random() < floor + (1 - floor) * max(0, min(1, t)) ** gamma:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.2f}" opacity="{rnd.uniform(*op):.2f}"/>')
    return f'<g {D.clip(f"<path d=\"{d}\"/>")} fill="{col}">{"".join(dots)}</g>'


def hatch(D, d, box, seed, col, ang=-35, step=4.5, w=1.1, light=(-0.6, -0.8), gamma=1.3, op=0.75, cut=0.18, wob=0.6):
    """Engraved hatching: parallel tapered lines that swell in the shadow and vanish toward the light (clipped)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    lx, ly = _unit(light)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = 0.5 * math.hypot((x1 - x0) * lx, (y1 - y0) * ly) + 1
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    diag = math.hypot(x1 - x0, y1 - y0) / 2 + 4
    segs = []
    k = -diag
    while k < diag:
        px, py = cx + nx * k, cy + ny * k
        t0 = -diag
        while t0 < diag:
            t1 = t0 + 9
            mx, my = px + ux * (t0 + 4.5), py + uy * (t0 + 4.5)
            tv = 0.5 - ((mx - cx) * lx + (my - cy) * ly) / (2 * R)
            v = max(0, min(1, tv)) ** gamma
            if v > cut:
                ww = w * (0.35 + v)
                segs.append(f'<path d="M {px + ux * t0:.1f} {py + uy * t0 + rnd.uniform(-wob, wob):.1f} L {px + ux * t1:.1f} {py + uy * t1 + rnd.uniform(-wob, wob):.1f}" stroke-width="{ww:.2f}"/>')
            t0 = t1
        k += step * rnd.uniform(0.85, 1.15)
    return f'<g {D.clip(f"<path d=\"{d}\"/>")} stroke="{col}" stroke-linecap="round" fill="none" opacity="{op}">{"".join(segs)}</g>'


def gsky(D, stops, seed, cols=None, n=60, blooms=(), sop=(0.05, 0.14), x1=0, y1=0, x2=0, y2=1):
    """Painted sky: graded wash, soft colour blooms (blurred), long scumbled horizontal strokes."""
    out = [f'<rect x="-20" y="-20" width="640" height="640" fill="{D.lin(stops, x1, y1, x2, y2)}"/>']
    if blooms:
        out.append(soft(D, "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{o}"/>' for x, y, rx, ry, c, o in blooms), 30))
    if cols:
        out.append(soft(D, strokes(D.nid(), "M -20 -20 L 620 -20 L 620 620 L -20 620 Z", (-120, -20, 620, 620), cols, seed, n=n, angle=-2,
                                   length=(90, 260), width=(6, 18), opacity=sop, curve=0.08), 1.6))
    return "".join(out)


def gcloud(D, cx, cy, w, h, seed, pal, light=(-0.5, -0.8), op=1.0, n=26, lit_n=18, sd=(7, 3), flat=0.55):
    """A cloud bank from many puffs: a soft dark mass, mid-tone puffs leaning to the light, then sharper lit edges
    on the side facing the light (lost and found)."""
    lit, mid, dark = pal
    rnd = random.Random(seed)
    lx, ly = _unit(light)
    puffs = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(rnd.random())
        x = cx + math.cos(a) * w / 2 * rr
        y = cy + math.sin(a) * h / 2 * rr
        if y > cy + h * 0.25:
            y = cy + h * 0.25 - rnd.uniform(0, h * 0.1) * flat
        r = rnd.uniform(0.16, 0.3) * min(w, h * 2.2) * (1.1 - 0.5 * rr)
        puffs.append((x, y, r))
    base = "".join(f'<path d="{blob(x, y, r, r * 0.78, rnd.randint(0, 9999), 0.12, 12)}" fill="{dark}"/>' for x, y, r in puffs)
    midp = "".join(f'<path d="{blob(x + lx * r * 0.25, y + ly * r * 0.25, r * 0.78, r * 0.62, rnd.randint(0, 9999), 0.14, 12)}" fill="{mid}" opacity="0.8"/>'
                   for x, y, r in puffs)
    edges = []
    th = math.atan2(ly, lx)
    for x, y, r in sorted(puffs, key=lambda p: (p[0] - cx) * lx + (p[1] - cy) * ly)[-lit_n:]:
        a0 = th + rnd.uniform(-0.3, 0.3)
        span = rnd.uniform(0.6, 1.1)
        arc = [(x + r * 0.86 * math.cos(a0 + span * (t - 0.5)), y + r * 0.66 * math.sin(a0 + span * (t - 0.5))) for t in (0, 0.25, 0.5, 0.75, 1)]
        edges.append(taper(arc, r * 0.05, r * 0.22, lit, rnd.uniform(0.45, 0.85)))
    return (f'<g opacity="{op}">' + soft(D, base, sd[0]) + soft(D, midp, sd[1] * 1.6) + soft(D, "".join(edges), sd[1] * 0.45) + "</g>")


def gfog(D, y, h, seed, col, op=0.5, x0=-80, x1=680, n=None, sd=9, rx=(50, 140)):
    """Ground fog / mist band from many blurred lozenges."""
    rnd = random.Random(seed)
    n = n or int((x1 - x0) / 22)
    puffs = "".join(f'<ellipse cx="{rnd.uniform(x0, x1):.1f}" cy="{y + rnd.uniform(-h / 2, h / 2):.1f}" rx="{rnd.uniform(*rx):.1f}" ry="{h * rnd.uniform(0.12, 0.32):.1f}" '
                    f'fill="{col}" opacity="{rnd.uniform(0.25, 0.7):.2f}"/>' for _ in range(n))
    return soft(D, puffs, sd, op)


def gmoon(D, cx, cy, r, seed, pal=("#FFFDF2", "#EEE8D2", "#B8B096"), halo="#E8ECFF", halo_r=3.4, halo_op=0.55, ring=True,
          light=(-0.35, -0.4), maria="#9A9886"):
    """A painted moon: wide halo, a faint corona ring, a disc shaded toward the limb and soft blurred maria."""
    hi, mid, dkc = pal
    rnd = random.Random(seed)
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r * halo_r:.1f}" fill="{D.rad([(0, halo, halo_op), (0.25, halo, halo_op * 0.45), (0.6, halo, halo_op * 0.12), (1, halo, 0)])}"/>']
    if ring:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.9:.1f}" fill="none" stroke="{halo}" stroke-width="{r * 0.35:.1f}" opacity="0.12" {gb(D, r * 0.18)}/>')
    lx, ly = light
    g = D.rad([(0, hi), (0.55, mid), (1, dkc)], 0.5 + lx * 0.4, 0.5 + ly * 0.4, 0.75)
    disc = blob(cx, cy, r, r, seed, 0.006, 32)
    out.append(f'<path d="{disc}" fill="{g}"/>')
    cid = D.clip(f'<path d="{disc}"/>')
    ms = "".join(f'<path d="{blob(cx + r * mx, cy + r * my, r * mr, r * mr * 0.7, rnd.randint(0, 999), 0.3, 12, rnd.uniform(0, 180))}" fill="{maria}" opacity="{rnd.uniform(0.18, 0.35):.2f}"/>'
                 for mx, my, mr in ((-0.25, -0.2, 0.32), (0.2, -0.32, 0.22), (0.3, 0.05, 0.26), (-0.1, 0.25, 0.2), (0.05, -0.05, 0.14), (-0.42, 0.12, 0.14)))
    out.append(f'<g {cid}>{soft(D, ms, round(r * 0.05, 1))}'
               f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{D.rad([(0, "#FFFFFF", 0), (0.75, "#FFFFFF", 0), (1, dkc, 0.35)])}"/></g>')
    return "".join(out)


def gglow(D, cx, cy, r, col, s=0.7, ry=None):
    g = D.rad([(0, col, s), (0.22, col, s * 0.6), (0.5, col, s * 0.22), (1, col, 0)])
    if ry:
        return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


def folds(D, d, lines, dark, light, seed, w=(3, 1), op=0.5, sd=1.2, lw=(1.6, 0.4), lop=0.45, loff=(1.6, -1.2)):
    """Drapery folds clipped to a garment: a soft shadow valley along each fold line and a thin light ridge beside it."""
    out = []
    for i, pts in enumerate(lines):
        out.append(taper(catmull(pts, 5), w[0], w[1], dark, op))
    hi = [taper(catmull(shift(pts, *loff), 5), lw[0], lw[1], light, lop) for pts in lines]
    return f'<g {D.clip(f"<path d=\"{d}\"/>")}>' + soft(D, "".join(out), sd) + soft(D, "".join(hi), sd * 0.5) + "</g>"


def willow(D, x, base, h, seed, col, op=1.0, strands=46, lean=0):
    """A weeping willow: a short leaning trunk, a dome of limbs and long hanging curtains of fronds."""
    rnd = random.Random(seed)
    out = [taper([(x - 4, base), (x + lean * 0.3, base - h * 0.35), (x + lean, base - h * 0.62)], h * 0.09, h * 0.04, col)]
    for k in range(5):
        a = -90 + rnd.uniform(-70, 70)
        L = h * rnd.uniform(0.25, 0.45)
        sx, sy = x + lean, base - h * 0.6
        out.append(taper([(sx, sy), (sx + math.cos(math.radians(a)) * L * 0.6, sy + math.sin(math.radians(a)) * L * 0.6 - 6),
                          (sx + math.cos(math.radians(a)) * L, sy + math.sin(math.radians(a)) * L + 4)], h * 0.03, 1, col))
    for _ in range(strands):
        a = rnd.uniform(-170, -10)
        rr = h * rnd.uniform(0.2, 0.5)
        sx = x + lean + math.cos(math.radians(a)) * rr * 1.3
        sy = base - h * 0.62 + math.sin(math.radians(a)) * rr * 0.7
        L = (base - sy) * rnd.uniform(0.5, 0.95)
        out.append(taper([(sx, sy), (sx + rnd.uniform(-4, 4), sy + L * 0.5), (sx + rnd.uniform(-6, 8), sy + L)], rnd.uniform(2, 5), 0.5, col, rnd.uniform(0.6, 1)))
    return f'<g opacity="{op}">{"".join(out)}</g>'


def tube_pts(pts, w0, w1, n=6, wfn=None):
    """Outline points of a tapered limb along a smooth spine (w0 -> w1, or wfn(t) for a custom profile)."""
    path = catmull(pts, n)
    m = len(path)
    left, right = [], []
    for i, (x, y) in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / max(1, m - 1)
        w = (wfn(t) if wfn else (w0 + (w1 - w0) * t)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def limb(D, pts, w0, w1, pal, seed, light=(-0.6, -0.8), rim=None, rim_w=1.6, wfn=None, angle=None, n=10, core=0.32, edge=None):
    o = tube_pts(pts, w0, w1, wfn=wfn)
    if angle is None:
        angle = math.degrees(math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0]))
    return gform(D, o, pal, seed, light, angle=angle, n=n, core=core, rim=rim, rim_w=rim_w, hi_op=0.35, edge=edge)


def forest_band(D, top, bottom, seed, cols, x0=-20, x1=620, tip=(8, 24), light=None, density=1.0):
    """A far forest as one painted mass: a ragged crown line of spruce tips (no stick trees), lit tips on the
    left, a darker skirt, softened a touch for distance."""
    rnd = random.Random(seed)
    pts = [(x0, bottom)]
    x = x0
    while x < x1:
        w = rnd.uniform(4, 9) / density
        h = rnd.uniform(*tip)
        y = top + rnd.uniform(-4, 6)
        pts += [(x, y), (x + w * 0.45, y - h), (x + w * 0.55, y - h + 1), (x + w, y + rnd.uniform(-2, 3))]
        x += w * rnd.uniform(0.7, 1.1)
    pts.append((x1, bottom))
    d = pd(pts)
    out = [f'<path d="{d}" fill="{cols[0]}"/>']
    out.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>' + strokes(D.nid(), d, (x0, top - tip[1], x1, bottom), cols + [cols[0]], seed, n=int((x1 - x0) / 3),
                                                                   angle=-90, length=(8, 26), width=(1.5, 4), opacity=(0.3, 0.7)) + "</g>")
    if light:
        out.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}><path d="{d}" fill="none" stroke="{light}" stroke-width="2.4" opacity="0.5" transform="translate(1.2 1)"/></g>')
    return soft(D, "".join(out), 0.5)


def gfin(D, out, seed, pf_seed, edge=3.0, bristle=0.5, grain=0.2, bg="#000000", gcol="#000000", gop=0.35, freq=0.05):
    """Finish: pigment grain, then the painterly varnish (brushy edges, bristle texture, crisp text on top).
    A full-bleed ground goes under the filtered art so the displaced edges never show paper."""
    body = finish(D, out, seed, gcol, gop)
    pf = _painterly(body, seed=pf_seed, edge=edge, bristle=bristle, grain=grain, freq=freq, prefix=D.u.replace("-", "") + "pf")
    i = pf.index('aria-hidden="true">')
    head, ink_ = pf[:i], pf[i:]
    # the second (text-only) copy never shows anything but <text>: drop its hidden shapes to keep files lean
    ink_ = _re.sub(r'<(path|circle|ellipse|rect|polygon|polyline|line|stop|feGaussianBlur|feTurbulence|feDisplacementMap|'
                   r'feColorMatrix|feComposite|feBlend|use)\b[^>]*/>', "", ink_)
    for _ in range(6):
        ink_ = _re.sub(r'<(g|clipPath|linearGradient|radialGradient|filter|pattern|defs|mask)\b[^>]*>\s*</\1>', "", ink_)
    return f'<rect x="-10" y="-10" width="620" height="620" fill="{bg}"/>' + head + ink_


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


# --- repaint:dracula
def count_on_wall(D, x, y, s, seed, ang=-8, light=(-0.85, -0.5), rim="#D2DCF8"):
    """The Count seen from behind, head-first down the wall like a lizard: elbows and knees splayed, the cloak spread
    between arm and leg on each side like a bat's wings, long pale hands gripping the stones. (x, y) = nape."""
    def L(p):
        return T(p, x, y, s, False, ang)
    col = "#08070E"
    lx, ly = _unit(light)
    out = []
    arms = [[(22, 6), (58, 14), (64, 50)], [(-22, 6), (-56, 26), (-52, 62)]]
    hands = [((64, 50), (70, 66)), ((-52, 62), (-56, 78))]
    legs = [[(12, -62), (44, -100), (34, -148)], [(-12, -62), (-48, -92), (-46, -140)]]
    boots = [[(34, -146), (36, -160), (44, -170)], [(-46, -138), (-48, -152), (-56, -162)]]
    torso = [(-20, 8), (-27, 0), (-25, -16), (-17, -40), (-14, -54), (-22, -80), (-8, -86), (0, -76), (8, -86), (22, -80), (14, -54), (17, -40), (25, -16), (27, 0), (20, 8), (0, 4)]
    wings = [[(26, 2), (58, 10), (66, 48), (80, 40), (96, 22), (106, -14), (90, -20), (98, -56), (78, -62), (78, -98), (58, -90), (44, -102), (30, -86),
              (16, -60), (18, -30)],
             [(-26, 2), (-56, 22), (-54, 60), (-70, 52), (-92, 34), (-108, 0), (-92, -6), (-104, -44), (-84, -50), (-88, -86), (-66, -80), (-50, -94),
              (-30, -80), (-16, -58), (-18, -28)]]
    ribs = [[(30, 0), (70, 10), (100, 20)], [(28, -8), (66, -10), (100, -14)], [(24, -24), (60, -36), (96, -56)], [(20, -40), (52, -62), (76, -96)],
            [(-30, 4), (-70, 26), (-96, 32)], [(-28, -6), (-68, -2), (-104, 0)], [(-24, -22), (-62, -34), (-100, -44)], [(-20, -40), (-56, -62), (-86, -86)]]
    shapes = [smooth_closed(L(w)) for w in wings] + [smooth_closed(L(torso))]
    shapes += [smooth_closed(tube_pts(L(a), 15 * s, 10 * s)) for a in arms] + [smooth_closed(tube_pts(L(lg), 19 * s, 12 * s)) for lg in legs]
    shapes += [smooth_closed(tube_pts(L(b), 13 * s, 9 * s)) for b in boots]
    # the cast shadow, down and right on the stones
    out.append(f'<g transform="translate({16 * s:.1f} {12 * s:.1f})" fill="#02030A" opacity="0.55">{soft(D, "".join(f"<path d=\"{p}\"/>" for p in shapes), 4)}</g>')
    # far limbs/legs first, then the wings, the body over them
    for k, lg in enumerate(legs):
        out.append(rimlit(D, tube_pts(L(lg), 19 * s, 12 * s, wfn=lambda t: (24 - 13 * t + 5 * math.sin(t * 3.14)) * s), col, rim, light, w=1.4, op=0.6, blur=0.5))
        out.append(rimlit(D, tube_pts(L(boots[k]), 13 * s, 9 * s), "#050408", rim, light, w=1.4, op=0.85, blur=0.3))
    for k, w in enumerate(wings):
        wp = L(w)
        out.append(gform(D, wp, ("#3E3654", "#16101E", "#030206"), seed + k, light, angle=-90, n=30, core=0.28, refl="#2A2448", rim=rim, rim_w=1.8,
                         sop=(0.08, 0.2), hik=0.04, hi_op=0.3, slen=(10, 30), sw=(1, 2.4), rim_op=0.6, rim_blur=0.8))
        rb = [L(r) for r in ribs[k * 4:(k + 1) * 4]]
        out.append(folds(D, smooth_closed(wp), rb, "#000000", "#8A7EAA", seed + k, w=(7 * s, 1.2), op=0.8, sd=1.4, lw=(1.6, 0.3), lop=0.45, loff=(-1.6, -1.6)))
    out.append(gform(D, L(torso), ("#4A4258", "#1A1422", "#030206"), seed + 4, light, angle=-90, n=14, core=0.35, rim=rim, rim_w=1.3, rim_op=0.6, hi_op=0.3))
    out.append(folds(D, smooth_closed(L(torso)), [L([(-14, -6), (-6, -40), (-10, -64)]), L([(10, -2), (6, -36), (10, -62)])], "#000000", "#6A5E88", seed, w=(4 * s, 1), op=0.7))
    for k, a in enumerate(arms):
        out.append(rimlit(D, tube_pts(L(a), 15 * s, 10 * s, wfn=lambda t: (15 - 6 * t + 3 * math.sin(t * 6.28)) * s), col, rim, light, w=1.6, op=0.85, blur=0.4))
        (wx, wy), (hx, hy) = L(list(hands[k]))
        dirn = math.atan2(hy - wy, hx - wx)
        hand = []
        for f in range(4):
            fa = dirn + (f - 1.5) * 0.36
            Lf = (17 + (3 if f in (1, 2) else 0)) * s
            k1 = (wx + math.cos(fa) * 9 * s, wy + math.sin(fa) * 9 * s)
            k2 = (k1[0] + math.cos(fa) * Lf * 0.55, k1[1] + math.sin(fa) * Lf * 0.55)
            bend = 0.7 * (1 if k else -1)
            k3 = (k2[0] + math.cos(fa + bend) * Lf * 0.5, k2[1] + math.sin(fa + bend) * Lf * 0.5)
            hand.append(taper(catmull([k1, k2, k3], 4), 3.6 * s, 1.3 * s, "#D8D0C4"))
        th = dirn + (1.3 if k == 0 else -1.3)
        hand.append(taper(catmull([(wx, wy), (wx + math.cos(th) * 9 * s, wy + math.sin(th) * 9 * s), (wx + math.cos(th + 0.7) * 15 * s, wy + math.sin(th + 0.7) * 15 * s)], 4), 4.6 * s, 1.6 * s, "#D8D0C4"))
        hand.append(f'<path d="{blob(wx + math.cos(dirn) * 6 * s, wy + math.sin(dirn) * 6 * s, 7 * s, 5.5 * s, seed + k, 0.08, 10, math.degrees(dirn))}" fill="#D8D0C4"/>')
        out.append("".join(hand))
        out.append(f'<path d="{blob(wx + math.cos(dirn) * 8 * s + 2, wy + math.sin(dirn) * 8 * s + 2, 5 * s, 3.5 * s, seed + k + 3, 0.1, 8, math.degrees(dirn))}" fill="#7A6E78" opacity="0.6" {gb(D, 1.2)}/>')
    # the head, lowest of all: thick white hair catching the moon, a sliver of hooked profile and moustache
    hx, hy = L([(2, 20)])[0]
    head = blob_pts(hx, hy, 13 * s, 15 * s, seed + 3, 0.05, 14, ang)
    out.append(gform(D, head, ("#FFFFFF", "#AEAAB8", "#34303E"), seed + 5, light, angle=90 + ang, n=22, slen=(5 * s, 12 * s), sw=(0.6, 1.4), core=0.4,
                     cols=["#FFFFFF", "#7A7686", "#D8D4DC"], rim="#FFFFFF", rim_w=1.2))
    out.append(f'<path d="{smooth_closed(L([(-7, 26), (-14, 32), (-16, 40), (-10, 40), (-5, 34)]))}" fill="#D8C8C0"/>')
    out.append(taper(L([(-8, 32), (-16, 38), (-21, 46)]), 3 * s, 0.6, "#F4F2F0"))
    out.append(gform(D, L([(-18, 6), (-8, 11), (2, 8), (12, 11), (20, 6), (12, -2), (0, 0), (-12, -2)]), ("#4A4060", "#140E1C", "#000000"), seed + 8, light,
                     n=0, rim=rim, rim_w=1.2))
    return "".join(out)


def rubble_wall(D, d, box, seed, pal, light=(-0.85, -0.4), n=260, size=(16, 46), joints="#0C0C14", jn=120):
    """A stone face painted, not drawn: graded wash, many translucent stone-sized patches of warmer and cooler grey,
    broken mortar joints (lost and found), moonlit arrises and stipple in the shadow."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    cid = D.clip(f'<path d="{d}"/>')
    lx, ly = _unit(light)
    out = []
    patches = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        w = rnd.uniform(*size)
        h = w * rnd.uniform(0.45, 0.7)
        c = rnd.choice(pal)
        patches.append(f'<path d="{smooth_closed(poly_pts([(x, y), (x + w, y + rnd.uniform(-1, 1)), (x + w + rnd.uniform(-2, 2), y + h), (x + rnd.uniform(-2, 2), y + h)], 6, rnd.randint(0, 999), 1.2))}" '
                       f'fill="{c}" opacity="{rnd.uniform(0.12, 0.38):.2f}"/>')
    out.append(soft(D, "".join(patches), 0.7))
    js = []
    y = y0 + rnd.uniform(0, 10)
    while y < y1:
        h = rnd.uniform(*size) * 0.55
        x = x0 - rnd.uniform(0, 30)
        while x < x1:
            w = rnd.uniform(*size) * 1.2
            if rnd.random() < 0.75:
                js.append(f'<path d="M {x:.1f} {y:.1f} L {x + w:.1f} {y + rnd.uniform(-1.5, 1.5):.1f}" stroke-width="{rnd.uniform(0.8, 2):.1f}" opacity="{rnd.uniform(0.12, 0.45):.2f}"/>')
                js.append(f'<path d="M {x + 2:.1f} {y + 2.2:.1f} L {x + w * rnd.uniform(0.4, 0.9):.1f} {y + 2.2:.1f}" stroke="#C8D0F0" stroke-width="1" opacity="{rnd.uniform(0.1, 0.3):.2f}"/>')
            if rnd.random() < 0.6:
                js.append(f'<path d="M {x + w:.1f} {y:.1f} L {x + w + rnd.uniform(-2, 2):.1f} {y + h:.1f}" stroke-width="{rnd.uniform(0.8, 1.8):.1f}" opacity="{rnd.uniform(0.1, 0.4):.2f}"/>')
            x += w
        y += h
    out.append(f'<g stroke="{joints}" stroke-linecap="round" fill="none">{"".join(js)}</g>')
    return f'<g {cid}>{"".join(out)}</g>'


@design("dracula")
def dracula():
    D = Doc2("hr-dr")
    light = (-0.85, -0.45)
    out = [gsky(D, [(0, "#04050C"), (0.35, "#0E1430"), (0.7, "#283058"), (1, "#3A4068")], 1, ["#2A3256", "#0A0E1E", "#4A5070"], 50,
                blooms=((150, 280, 240, 170, "#6A74A0", 0.4), (60, 520, 200, 120, "#2A3050", 0.5)))]
    out.append(stars_field(2, (0, 0, 260, 330), 60))
    out.append(gmoon(D, 140, 272, 46, 3, pal=("#FFFCEC", "#ECE6CE", "#B4AC90"), halo="#D8E0FF", halo_r=4.0, halo_op=0.5))
    out.append(gcloud(D, 70, 330, 250, 26, 4, ("#C8D0F0", "#3E4670", "#1A1E36"), light=(0.4, -1), op=0.9, n=16, lit_n=9))
    out.append(gcloud(D, 230, 214, 170, 16, 5, ("#D0D8F8", "#4A5278", "#20263E"), light=(-0.7, 0.6), op=0.6, n=12, lit_n=7))
    # far Carpathian ranges, paler and bluer with distance, a gorge filling with mist
    out.append(soft(D, hill(D, ridge([(-20, 400), (40, 364), (96, 388), (150, 350), (214, 384), (270, 360), (330, 404)], 4, 9, 4), 640,
                            ("#8A94BA", "#666E94", "#4A5076"), 2, inkw=0, n=24, lit="#D0D8F8"), 1.6))
    out.append(gfog(D, 410, 56, 3, "#A4AED4", 0.7, -60, 360, sd=10))
    out.append(soft(D, hill(D, ridge([(-20, 452), (50, 430), (130, 450), (210, 430), (330, 462)], 5, 6, 4), 640, ("#4A5274", "#2A3050", "#12142A"), 3, inkw=0, n=20), 0.9))
    out.append(forest_band(D, 470, 600, 4, ["#0C0E1A", "#141828", "#10142A"], -20, 330, tip=(10, 30), light="#4A5480"))
    out.append(forest_band(D, 512, 600, 5, ["#06070E", "#0A0C16"], -20, 300, tip=(18, 44), light="#3A4470"))
    out.append(gfog(D, 500, 80, 6, "#8A94BC", 0.6, -60, 380, sd=12))
    # the crag the castle grows out of, and the tower itself, its corner toward the moon
    crag = [(226, 640), (236, 590), (262, 560), (300, 548), (360, 540), (430, 548), (520, 528), (640, 514), (640, 640)]
    out.append(gform(D, crag, ("#6A7090", "#2A2E44", "#06070E"), 7, light, angle=-70, n=80, core=0.35, rim="#B8C0E0", rim_w=2))
    out.append(stipple(D, smooth_closed(crag), bbox(crag), 7, "#000000", n=900, light=light, gamma=1.2))
    xc = 300               # the corner of the tower

    def ex(y):
        return xc + (y - 100) * 0.03
    front = [(ex(-30), -30), (640, -30), (640, 560), (ex(560), 560)]
    side = [(ex(-30) - 62, -30), (ex(-30), -30), (ex(560), 560), (ex(560) - 56, 566)]
    out.append(gform(D, side, ("#D8DCEE", "#9A9EBA", "#5A5E7C"), 8, (-1, -0.2), angle=-90, n=30, core=0.1, hi_op=0.25))
    out.append(rubble_wall(D, pd(side), (ex(-30) - 70, -30, ex(560) + 2, 570), 9, ["#F2F4FF", "#8A8EAA", "#B8BCD8", "#6A6E8A"], light, n=140, size=(10, 30), joints="#3A3E58"))
    out.append(gform(D, front, ("#7A7E9C", "#3E4058", "#0C0C14"), 10, (-1, -0.15), angle=-90, n=0, core=0.0, hi_op=0))
    out.append(rubble_wall(D, pd(front), (ex(-30), -30, 640, 570), 11, ["#9A9EBC", "#4A4C64", "#2A2C3E", "#6A6E8C", "#7A7088"], light, n=420, size=(16, 44)))
    out.append(f'<path d="{pd(front)}" fill="{D.lin([(0, "#000000", 0), (0.5, "#02020A", 0.35), (1, "#02020A", 0.75)], 0, 0, 1, 0)}"/>')
    out.append(stipple(D, pd(front), (ex(-30), -30, 640, 570), 12, "#000000", n=1600, light=(-1, 0), gamma=1.6, op=(0.3, 0.7)))
    out.append(streaks_dark(D, (ex(0), 40, 640, 520), 13))
    out.append(pline([(ex(-30), -30), (ex(560), 560)], "#1A1C2A", 2, 3, 0.7, 1))
    # string course and a buttress foot where tower meets crag
    # Jonathan's window high up, lit; the Count's own window below it, black and open
    jx, jy = 548, 214
    out.append(gglow(D, jx, jy + 20, 90, "#FFB050", 0.35))
    out.append(f'<path d="{smooth_closed(arch_pts(jx - 20, jx + 20, jy, jy + 50, 6, "pointed", 0.5))}" fill="#0A0606"/>')
    out.append(gothic_window(D, jx - 14, jx + 14, jy + 6, jy + 46, 7, frame="#16100C", point=0.5))
    out.append(cloaked(jx + 2, jy + 46, 0.24, "#1A0C08", hood=False))
    wx, wy = 412, 232
    out.append(f'<path d="{smooth_closed(arch_pts(wx - 22, wx + 22, wy, wy + 52, 6, "pointed", 0.5))}" fill="#030206"/>')
    out.append(gform(D, [(wx - 22, wy + 22), (wx - 6, wy + 16), (wx - 4, wy + 52), (wx - 22, wy + 52)], ("#3A3446", "#1A1620", "#040306"), 15, light, n=4))
    out.append(gform(D, [(wx - 30, wy + 52), (wx + 30, wy + 52), (wx + 34, wy + 60), (wx - 34, wy + 60)], ("#C8CCE0", "#6A6E86", "#22243A"), 16, light, angle=0, n=6))
    # the Count, crawling face down out of it
    out.append(count_on_wall(D, 410, 404, 0.86, 9, ang=-6, light=light))
    # mist boiling up out of the gorge around the foot of the tower
    out.append(gfog(D, 560, 90, 17, "#7A84AC", 0.55, 180, 680, sd=14))
    for (bx, by, bs, fl, a) in ((214, 298, 0.9, 0.6, -10), (250, 346, 0.6, 0.1, 8), (84, 388, 0.6, 0.8, -4), (186, 404, 0.45, 0.3, 12)):
        out.append(bat(bx, by, bs, "#05050C", fl, a))
    out.append(band(D, 0, 220, "#000000", 0.6, 0))
    out.append(band(D, 480, 600, "#000000", 0, 0.6))
    # lettering
    out.append(block(D, 300, 142, "DRACULA", ANTON, 100, "#F4ECDA", "#7A0E16", depth=9, ang=(0.7, 1.0), ls=10, max_w=430, face2="#D8C8A8", shadow="#000000"))
    out.append(spaced(300, 178, "BRAM STOKER · 1897", CINZEL, 19, "#E8D8C0", ls=5, shadow="#000000"))
    out.append(letters(D, 300, 548, "“…his cloak spreading out like great wings.”", SERIF_IT, 26, "#F2E8D8", ["#FFFFFF", "#E8D8C8"], 11, max_w=470,
                       shadow="#000000", soff=(0.02, 0.06), angle=-40, wob=0.25))
    return gfin(D, out, 12, 101, edge=2.6, bristle=0.45, grain=0.2, bg="#0A0C18")
# --- end repaint:dracula


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


# --- repaint:the-headless-horseman
def galloping_horse(D, x, y, s, seed, col="#07040A", rim="#FFB060", glow="#FFC070"):
    """A horse at full extended gallop, facing right, built from anatomical masses into one silhouette: deep chest,
    rounded croup, long arched neck carried forward, a lean wedge of a head with a defined jaw, pricked ears, slim
    legs with knees, hocks and fetlocks, and hooves; mane and tail streaming back. (x, y) = middle of the barrel.
    Returns (behind, body, front) so a rider can be put between body and rim."""
    def L(p):
        return T(p, x, y, s)
    rnd = random.Random(seed)
    lw_fore = lambda t: limb_w(13, 7.5, 6.4, 5.6, 0.42, 0.1)(t) * s
    lw_hind = lambda t: limb_w(16, 8, 6.4, 5.6, 0.45, 0.05)(t) * s
    far = [tube_pts(L([(28, 12), (44, 30), (34, 44), (24, 48)]), 12 * s, 6 * s, wfn=lw_fore),                 # far fore folded under
           tube_pts(L([(-24, 10), (-30, 32), (-18, 44), (-10, 48)]), 14 * s, 6 * s, wfn=lw_hind)]             # far hind reaching under
    far_hooves = [L([(20, 46), (28, 44), (30, 51), (22, 53)]), L([(-12, 46), (-4, 45), (-3, 52), (-12, 53)])]
    parts = [blob_pts(*L([(0, 0)])[0], 42 * s, 19 * s, seed, 0.03, 20, -2),                                   # barrel
             blob_pts(*L([(36, -2)])[0], 16 * s, 20 * s, seed + 1, 0.04, 16, 10),                             # chest
             blob_pts(*L([(-36, -5)])[0], 20 * s, 21 * s, seed + 2, 0.04, 16),                                # croup and quarters
             tube_pts(L([(30, -10), (48, -30), (64, -44)]), 34 * s, 17 * s, wfn=lambda t: (34 - 20 * t + 4 * math.sin(math.pi * t)) * s),   # neck, arched
             tube_pts(L([(64, -46), (78, -38), (93, -27)]), 17 * s, 10 * s, wfn=lambda t: (17 - 6 * t - 2 * math.sin(math.pi * t)) * s),   # head
             blob_pts(*L([(68, -38)])[0], 9 * s, 8 * s, seed + 3, 0.05, 12),                                  # jaw / cheek
             L([(62, -50), (64, -61), (68, -50)]), L([(66, -49), (70, -59), (71, -47)]),                      # ears pricked
             tube_pts(L([(34, 10), (62, 20), (84, 28), (94, 30)]), 13 * s, 5.6 * s, wfn=lw_fore),             # leading foreleg reaching
             tube_pts(L([(-34, 6), (-52, 24), (-78, 30), (-90, 32)]), 16 * s, 5.6 * s, wfn=lw_hind),          # hind leg driving back
             blob_pts(*L([(-44, 6)])[0], 12 * s, 14 * s, seed + 4, 0.05, 12)]                                 # gaskin
    hooves = [L([(92, 26), (100, 28), (99, 35), (91, 34)]), L([(-96, 28), (-88, 28), (-88, 36), (-97, 36)])]
    ds_far = [smooth_closed(p) for p in far] + [pd(h) for h in far_hooves]
    ds = [smooth_closed(p) for p in parts] + [pd(h) for h in hooves]
    # mane and tail: streaming locks
    mane, tail = [], []
    for k in range(26):
        t = k / 25
        rx_, ry_ = L([(36 + t * 28, -32 - t * 16)])[0]
        ln = rnd.uniform(14, 30) * s
        mane.append(taper([(rx_, ry_), (rx_ - ln * 0.5, ry_ - rnd.uniform(-2, 6) * s), (rx_ - ln, ry_ + rnd.uniform(-4, 8) * s)], rnd.uniform(2.4, 4.4) * s, 0.4, col))
    for k in range(20):
        t = k / 19
        p0 = L([(-52, -16 + t * 6)])[0]
        p1 = L([(-80 - rnd.uniform(0, 10), -22 + t * 10 + rnd.uniform(-4, 4))])[0]
        p2 = L([(-112 - rnd.uniform(0, 26), -14 + t * 22 + rnd.uniform(-8, 8))])[0]
        tail.append(taper([p0, p1, p2], rnd.uniform(3, 5.5) * s, 0.4, col))
    behind_glow, rim_front = union_rim(D, ds, rim, -0.6 * s, 1.6 * s, op=0.9, blur=0.5, glow=glow, glow_op=0.35, glow_w=7 * s)
    behind = (f'<g fill="#030205">' + "".join(f'<path d="{d}"/>' for d in ds_far) + "</g>" + behind_glow + "".join(tail))
    body = f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>" + "".join(mane)
    # a few lit hairs on mane and tail tips, nostril and eye glints
    lit = []
    for k in range(10):
        t = rnd.random()
        rx_, ry_ = L([(40 + t * 24, -36 - t * 14)])[0]
        lit.append(taper([(rx_, ry_ - 2), (rx_ - rnd.uniform(8, 18) * s, ry_ - rnd.uniform(0, 5) * s)], 1.2 * s, 0.3, rim, 0.6))
    ex_, ey_ = L([(72, -44)])[0]
    front = rim_front + soft(D, "".join(lit), 0.4) + f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{1.4 * s:.1f}" fill="#FFB060" opacity="0.8"/>'
    return behind, body, front


def headless_rider2(D, x, y, s, seed, col="#06040A", rim="#FFB060"):
    """The rider: a high-collared riding coat with nothing above the collar, leaning into the gallop, one arm hurling
    up the lantern-head, the other on the reins, the cloak cracking out behind. (x, y) = the saddle."""
    def L(p):
        return T(p, x, y, s)
    cloak = [(10, -60), (-6, -64), (-40, -76), (-80, -96), (-120, -100), (-98, -80), (-136, -74), (-100, -58), (-118, -40), (-74, -42), (-40, -30), (-8, -20)]
    parts = [L([(-2, -20), (-30, -4), (-22, 4), (6, 2), (22, 0), (18, -18)]),                              # coat skirts over the horse's back
             tube_pts(L([(4, -14), (12, -36), (22, -58)]), 18 * s, 24 * s, wfn=lambda t: (17 + 10 * math.sin(math.pi * min(1, t * 0.62))) * s),  # torso
             blob_pts(*L([(20, -58)])[0], 16 * s, 8 * s, seed, 0.05, 12, -28),                          # shoulders
             L([(10, -62), (7, -80), (15, -74), (20, -84), (28, -72), (32, -60)]),                       # the empty high collar
             tube_pts(L([(4, -2), (24, 4), (26, 26), (20, 40)]), 15 * s, 8 * s, wfn=lambda t: limb_w(15, 10, 10, 8, 0.5)(t) * s),   # thigh and boot
             L([(14, 36), (30, 38), (31, 45), (14, 45)]),
             tube_pts(L([(24, -58), (40, -66), (52, -76), (60, -84)]), 10 * s, 7 * s, wfn=lambda t: limb_w(10.5, 7.5, 8, 6.5, 0.45)(t) * s),  # arm up
             tube_pts(L([(18, -50), (34, -36), (50, -36)]), 10 * s, 7 * s)]                              # arm on reins
    ds = [smooth_closed(p) for p in parts]
    cd = smooth_closed(L(cloak))
    behind, front = union_rim(D, ds + [cd], rim, -0.8 * s, 1.5 * s, op=0.9, blur=0.5)
    out = [gform(D, L(cloak), ("#4A2A3A", "#1A0E18", "#040206"), seed, (0.3, -1), angle=180, n=30, core=0.3, slen=(20, 50), sw=(1, 2.6))]
    out.append(folds(D, cd, [L([(0, -60), (-50, -82), (-110, -96)]), L([(-4, -40), (-60, -56), (-120, -72)]), L([(-8, -26), (-50, -38), (-100, -48)])],
                     "#000000", "#8A5A6A", seed, w=(6 * s, 1), op=0.7, sd=1.6))
    out.append(f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(front)
    # the hollow inside the collar, a dull red glow where a neck should be
    cx_, cy_ = L([(19, -76)])[0]
    out.append(f'<path d="{blob(cx_, cy_, 9 * s, 2.6 * s, seed, 0.1, 10, -6)}" fill="#3A0E08"/>')
    out.append(f'<path d="{blob(cx_, cy_ - 0.4 * s, 6 * s, 1.4 * s, seed + 1, 0.1, 10, -6)}" fill="#8A2A10" opacity="0.6" {gb(D, 1)}/>')
    # the reins to the bit
    hx, hy = L([(50, -36)])[0]
    return "".join(out), (hx, hy)


@design("the-headless-horseman")
def the_headless_horseman():
    D = Doc2("hr-hh")
    out = [gsky(D, [(0, "#08060E"), (0.38, "#24162A"), (0.7, "#6A3A30"), (1, "#24141A")], 1, ["#2A1A2E", "#08040A", "#6A3A34"], 50,
                blooms=((300, 330, 260, 200, "#C86A3A", 0.35),))]
    out.append(stars_field(3, (0, 0, 600, 240), 60))
    out.append(gmoon(D, 300, 322, 150, 5, pal=("#FFF2C8", "#F4C278", "#C8803E"), halo="#FFB060", halo_r=1.9, halo_op=0.55, maria="#D8945A",
                     light=(0.1, -0.2)))
    out.append(gcloud(D, 100, 250, 240, 26, 4, ("#E8A070", "#4A2A3A", "#1A0E1A"), light=(1, 0.3), op=0.85, n=16, lit_n=8))
    out.append(gcloud(D, 530, 410, 200, 20, 5, ("#E89A6A", "#4A2A30", "#1A0E16"), light=(-1, -0.4), op=0.7, n=12, lit_n=6))
    # the old Dutch church on its knoll and the hollow beyond, in haze
    out.append(soft(D, hill(D, ridge([(-20, 424), (60, 404), (140, 410), (230, 432)], 3, 5, 3), 640, ("#3A2434", "#20141E", "#0A060A"), 2, inkw=0, n=10), 0.8))
    church = [sharp([(60, 412), (60, 364), (84, 354), (132, 354), (132, 412)], "#0E0810"), sharp([(52, 376), (84, 350), (138, 350), (138, 356), (84, 356), (58, 380)], "#0E0810"),
              sharp([(72, 412), (72, 330), (96, 330), (96, 412)], "#0E0810"), sharp([(68, 332), (84, 274), (100, 332)], "#0E0810"),
              taper([(84, 276), (84, 258)], 1.6, 1.2, "#0E0810"), taper([(78, 264), (90, 264)], 1.4, 1.4, "#0E0810")]
    out.append(soft(D, "".join(church), 0.5))
    out.append(gglow(D, 84, 340, 14, "#FFC060", 0.6))
    out.append(f'<rect x="82" y="334" width="4" height="10" fill="#FFD890"/>')
    for wx in (108, 122):
        out.append(f'<rect x="{wx - 2}" y="364" width="4" height="12" fill="#FFC870" opacity="0.9"/>')
    out.append(gfog(D, 420, 40, 6, "#8A5A5A", 0.5, sd=8))
    # trees framing: a great twisted oak at the right, a smaller one at the left
    out.append(crooked_tree(560, 470, 380, 7, "#07050A", w=18, lean=-12, spread=42, depth=5))
    out.append(crooked_tree(30, 470, 260, 8, "#07050A", w=12, lean=10, spread=40, depth=4))
    # the brook and the wooden bridge
    out.append(f'<path d="M -20 470 L 620 470 L 620 620 L -20 620 Z" fill="{D.lin([(0, "#4A2A30"), (0.4, "#1A1018"), (1, "#06040A")])}"/>')
    rnd = random.Random(6)
    out.append(soft(D, "".join(taper([(x_ := 300 + rnd.uniform(-130, 130), y_ := 480 + rnd.uniform(0, 110)), (x_ + rnd.uniform(14, 46), y_)], 2, 0.6, rnd.choice(["#FFC070", "#E8904A"]),
                                     rnd.uniform(0.2, 0.6)) for _ in range(46)), 0.8))
    bridge_y = 456
    out.append(gform(D, [(-20, bridge_y), (620, bridge_y), (620, bridge_y + 16), (-20, bridge_y + 16)], ("#7A5040", "#2A1A14", "#0A0604"), 8, (0, -1), angle=0, n=40,
                     sharp=True, rim="#FFB060", rim_w=1.4))
    for k in range(13):
        px = 10 + k * 50
        out.append(taper([(px, bridge_y + 14), (px + 1, bridge_y + 90)], 9, 8, "#0A0608"))
    # the horse and rider, flying over the bridge across the face of the moon
    behind, body, front = galloping_horse(D, 300, 364, 1.55, 8)
    rider, (hx, hy) = headless_rider2(D, 300 + 6 * 1.55, 364 - 22 * 1.55, 1.25, 9)
    out.append(behind + body + front)
    mx_, my_ = 300 + 92 * 1.55, 364 - 28 * 1.55
    out.append(f'<path d="M {hx:.1f} {hy:.1f} Q {(hx + mx_) / 2:.1f} {(hy + my_) / 2 + 10:.1f} {mx_:.1f} {my_:.1f}" stroke="#06040A" stroke-width="1.6" fill="none"/>')
    out.append(rider)
    # the rail in front of the hooves
    for k in range(13):
        px = 10 + k * 50
        out.append(taper([(px, bridge_y + 2), (px, bridge_y - 32)], 6, 5, "#0E080A"))
    out.append(taper([(-20, bridge_y - 30), (300, bridge_y - 33), (620, bridge_y - 30)], 5, 5, "#0E080A"))
    out.append(taper([(-20, bridge_y - 31.5), (300, bridge_y - 34.5), (620, bridge_y - 31.5)], 1.6, 1.6, "#FFB060", 0.55))
    # the lantern head, flung up, sparks streaming
    jx, jy = 300 + 6 * 1.55 + 64 * 1.25, 364 - 22 * 1.55 - 102 * 1.25
    out.append(jack_o_lantern(D, jx, jy, 24, 10))
    for _ in range(30):
        a, r = rnd.uniform(-2.6, -0.6), rnd.uniform(26, 70)
        out.append(f'<circle cx="{jx - 4 + math.cos(a) * r - 20:.1f}" cy="{jy + math.sin(a) * r * 0.6 + 20:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFD08A" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    for k in range(10):
        lx_, ly_ = rnd.uniform(60, 560), rnd.uniform(200, 440)
        out.append(f'<path d="{blob(lx_, ly_, rnd.uniform(3, 6), rnd.uniform(1.6, 3), k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8602A", "#8A3A1A", "#E89A3A"])}" opacity="0.9"/>')
    out.append(band(D, 510, 600, "#000000", 0, 0.7))
    out.append(band(D, 0, 200, "#000000", 0.45, 0))
    out.append(block(D, 300, 110, "THE HEADLESS", BEBAS, 66, "#FFD27A", "#5A1A08", depth=6, ang=(0.6, 1.0), ls=6, max_w=440, face2="#F08A2A", shadow="#000000"))
    out.append(block(D, 300, 176, "HORSEMAN", BEBAS, 80, "#FFD27A", "#5A1A08", depth=7, ang=(0.6, 1.0), ls=10, max_w=440, face2="#E8701E", shadow="#000000"))
    out.append(sub_rule(300, 548, "WASHINGTON IRVING · 1820", CINZEL, 18, "#FFE2B0", ls=3, max_w=360, line="#FFB060"))
    return gfin(D, out, 13, 110, edge=2.4, bristle=0.4, grain=0.18, bg="#140C14")
# --- end repaint:the-headless-horseman


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
# --- repaint:the-invisible-man
def bandaged_void(D, cx, cy, s, seed):
    """Bandages wound round a head that isn't there: a few spaced bands on an egg-shaped volume; through the gaps you
    see straight through to the inside of the wraps at the back, and the wall. The goggles float at eye level."""
    rnd = random.Random(seed)
    out = []
    rx, ry = 24 * s, 30 * s
    ts = (0.07, 0.2, 0.56, 0.69, 0.82, 0.94)
    bands = []
    for k, t in enumerate(ts):
        y = cy - ry + 2 * ry * t
        half = rx * math.sqrt(max(0.04, 1 - (2 * t - 1) ** 2)) * 1.02
        tilt = rnd.uniform(-3, 3) * s + (1.5 if k % 2 else -1.5) * s
        bands.append((y, half, tilt, (3.4 if t not in (0.07, 0.94) else 2.6) * s, k))
    for y, half, tilt, hw, k in bands:
        back = [(cx - half, y), (cx - half * 0.5, y - 4.5 * s + tilt * 0.4), (cx, y - 5.5 * s + tilt * 0.5), (cx + half * 0.5, y - 4.5 * s + tilt * 0.6), (cx + half, y + tilt * 0.4)]
        out.append(gform(D, tube_pts(back, hw * 2, hw * 2), ("#B8A88E", "#6A5A48", "#2A2016"), seed + 40 + k, (1, -0.2), angle=0, n=0, core=0.4, hi_op=0.3))
    for y, half, tilt, hw, k in bands:
        front = [(cx - half, y), (cx - half * 0.5, y + 5 * s + tilt * 0.4), (cx, y + 6.5 * s + tilt * 0.6), (cx + half * 0.55, y + 5 * s + tilt * 0.4), (cx + half, y + tilt * 0.4)]
        out.append(gform(D, tube_pts(front, hw * 2, hw * 2), ("#FFFAEE", "#DCCFB6", "#7A6A56"), seed + k, (-1, -0.3), angle=0, n=10, core=0.35, hi_op=0.55,
                         sw=(0.4, 1.0), slen=(6, 16), cols=["#FFFFFF", "#B8A88E", "#E8DCC6"]))
        out.append(taper(catmull([(x, y_ + hw * 0.6) for x, y_ in front], 6), 1.0, 1.0, "#6A5A48", 0.45))
    # a strip crossing diagonally over the crown, as bandages do
    cross = [(cx - rx * 0.7, cy - ry * 0.62), (cx - rx * 0.1, cy - ry * 0.94), (cx + rx * 0.55, cy - ry * 0.78), (cx + rx * 0.92, cy - ry * 0.3)]
    out.append(gform(D, tube_pts(cross, 6 * s, 6 * s), ("#FFFAEE", "#D2C4AA", "#6A5A48"), seed + 9, (-1, -0.3), n=6, core=0.3))
    # the goggles: two round smoked lenses in brass, the strap round nothing
    gy = cy - 3 * s
    out.append(taper(catmull([(cx - rx * 1.0, gy - 3 * s), (cx - rx * 0.6, gy + 1 * s), (cx + rx * 0.6, gy + 1 * s), (cx + rx * 1.0, gy - 3 * s)], 6), 3 * s, 3 * s, "#2A1E14"))
    for sg in (-1, 1):
        lx_ = cx + sg * 10.5 * s
        out.append(f'<circle cx="{lx_:.1f}" cy="{gy:.1f}" r="{8.6 * s:.1f}" fill="{D.lin([(0, "#F2D488"), (0.5, "#8A6A2A"), (1, "#3A2A0A")])}"/>')
        out.append(f'<circle cx="{lx_:.1f}" cy="{gy:.1f}" r="{6.8 * s:.1f}" fill="{D.rad([(0, "#4A4E58"), (0.7, "#14161C"), (1, "#050608")], 0.4, 0.35, 0.7)}"/>')
        out.append(f'<path d="M {lx_ - 4 * s:.1f} {gy - 3 * s:.1f} q {2 * s:.1f} {-2.4 * s:.1f} {5 * s:.1f} {-1.6 * s:.1f}" stroke="#FFFFFF" stroke-width="{1.3 * s:.1f}" fill="none" opacity="0.8" stroke-linecap="round"/>')
        out.append(f'<circle cx="{lx_ + 3.4 * s:.1f}" cy="{gy + 3.2 * s:.1f}" r="{1 * s:.1f}" fill="#FFB060" opacity="0.6"/>')
    out.append(taper([(cx - 2.4 * s, gy - 0.6 * s), (cx + 2.4 * s, gy - 0.6 * s)], 2 * s, 2 * s, "#8A6A2A"))
    return "".join(out)


def greatcoat(D, cx, top, s, seed, light=(-1, -0.25)):
    """An empty greatcoat standing as if worn: high turned-up collar, broad shoulders, sleeves with elbow folds, the
    open front showing the lining at the back of the coat, where a body should be. (cx, top) = back of collar."""
    def L(p):
        return T(p, cx, top, s)
    out = []
    pal = ("#C08060", "#3A2620", "#0A0604")
    # the inside back of the coat, seen through the open front
    out.append(gform(D, L([(-24, 18), (24, 18), (30, 150), (-30, 150)]), ("#5A3A30", "#22140E", "#060302"), seed, light, n=20, core=0.5))
    for k in range(3):
        out.append(taper(L([(-14 + k * 12, 30), (-16 + k * 13, 90), (-18 + k * 14, 150)]), 3, 4, "#000000", 0.5))
    out.append(soft(D, f'<path d="{smooth_closed(L([(-20, 18), (20, 18), (18, 60), (-18, 60)]))}" fill="#000000" opacity="0.65"/>', 6))
    # sleeves (behind the body edges at the shoulder)
    sleeves = [[(-58, 26), (-74, 80), (-74, 150)], [(58, 26), (70, 60), (52, 104), (16, 116)]]
    for k, sl in enumerate(sleeves):
        out.append(gform(D, tube_pts(L(sl), 34 * s, 26 * s, wfn=lambda t: (34 - 8 * t + (5 if k == 0 else 3) * math.sin(t * 3.14)) * s), pal, seed + 1 + k, light, angle=-80,
                         n=30, rim="#FFB060" if k == 0 else "#6A86B8", rim_w=2.2))
    out.append(folds(D, smooth_closed(tube_pts(L(sleeves[0]), 34 * s, 26 * s)), [L([(-66, 70), (-80, 76)]), L([(-70, 96), (-80, 100)]), L([(-66, 120), (-78, 126)])],
                     "#0A0604", "#C8906A", seed, w=(4, 1), op=0.7))
    out.append(folds(D, smooth_closed(tube_pts(L(sleeves[1]), 34 * s, 26 * s)), [L([(62, 58), (76, 66)]), L([(52, 90), (60, 102)]), L([(44, 98), (40, 112)])],
                     "#0A0604", "#C8906A", seed + 1, w=(4, 1), op=0.7))
    # coat body: two front panels falling from the shoulders, the right one buttoned over
    left = [(-28, 0), (-60, 18), (-66, 40), (-62, 110), (-66, 180), (-72, 260), (-30, 266), (-14, 150), (-12, 70), (-16, 30)]
    right = [(28, 0), (60, 18), (66, 40), (62, 110), (66, 180), (72, 262), (16, 266), (6, 150), (10, 70), (16, 30)]
    for k, pnl in enumerate((left, right)):
        out.append(gform(D, L(pnl), pal, seed + 5 + k, light, angle=-90, n=60, core=0.38, refl="#5A6A8A", rim="#FFB060" if k == 0 else None, rim_w=2.4,
                         sop=(0.08, 0.22)))
    out.append(folds(D, smooth_closed(L(left)), [L([(-50, 40), (-46, 140), (-54, 250)]), L([(-30, 60), (-26, 160), (-36, 256)])], "#060302", "#B88060", seed + 7,
                     w=(6, 1.5), op=0.6, sd=2))
    out.append(folds(D, smooth_closed(L(right)), [L([(48, 40), (44, 140), (52, 250)]), L([(24, 70), (22, 170), (30, 256)])], "#060302", "#8A6A70", seed + 8,
                     w=(6, 1.5), op=0.6, sd=2))
    # lapels and the high collar, turned up round no neck
    for sg in (-1, 1):
        lap = L([(sg * 16, 4), (sg * 34, 6), (sg * 30, 40), (sg * 14, 90), (sg * 12, 60), (sg * 14, 24)])
        out.append(gform(D, lap, ("#9A7A66", "#4A362C", "#140C08"), seed + 10 + sg, light, n=10, rim="#FFB060" if sg < 0 else None, rim_w=1.6))
    collar = L([(-30, 6), (-34, -14), (-24, -26), (0, -30), (24, -26), (34, -14), (30, 6), (16, 0), (0, -2), (-16, 0)])
    out.append(gform(D, collar, ("#A8826A", "#4A362C", "#100A08"), seed + 12, light, angle=-90, n=16, rim="#FFB060", rim_w=2))
    out.append(f'<path d="{smooth_closed(L([(-22, -14), (0, -20), (22, -14), (14, -2), (0, -6), (-14, -2)]))}" fill="#120806"/>')
    # buttons
    for k in range(4):
        bx, by = L([(18, 100 + k * 40)])[0]
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{4 * s:.1f}" fill="{D.rad([(0, "#5A4A3A"), (1, "#140C08")], 0.35, 0.35, 0.7)}"/>')
        out.append(f'<circle cx="{bx - 1.2 * s:.1f}" cy="{by - 1.2 * s:.1f}" r="{1.1 * s:.1f}" fill="#FFC890" opacity="0.6"/>')
    # gloves: one hanging empty from the left cuff, the right holding the loosened bandage at the breast
    gl = ("#6A4A3A", "#2A1A14", "#080404")
    gx, gy = L([(-74, 156)])[0]
    out.append(gform(D, poly_pts([(gx - 11 * s, gy - 6 * s), (gx + 11 * s, gy - 6 * s), (gx + 10 * s, gy + 18 * s), (gx + 4 * s, gy + 30 * s), (gx - 6 * s, gy + 28 * s),
                                  (gx - 12 * s, gy + 14 * s)], 6, seed, 0.6), gl, seed + 20, light, n=8, rim="#FFB060", rim_w=1.6))
    for f in range(4):
        out.append(taper([(gx - 7 * s + f * 4.4 * s, gy + 22 * s), (gx - 8 * s + f * 4.6 * s, gy + 34 * s)], 4 * s, 3 * s, gl[1]))
    hx, hy = L([(14, 112)])[0]
    out.append(gform(D, blob_pts(hx, hy, 13 * s, 10 * s, seed, 0.12, 12, -20), gl, seed + 21, light, n=6, rim="#6A86B8", rim_w=1.4))
    for f in range(4):
        out.append(taper([(hx - 10 * s, hy - 6 * s + f * 4 * s), (hx - 18 * s, hy - 10 * s + f * 4.4 * s), (hx - 16 * s, hy - 4 * s + f * 4 * s)], 4.4 * s, 3.4 * s, gl[1]))
    return "".join(out)


@design("the-invisible-man")
def the_invisible_man():
    D = Doc2("hr-im")
    light = (-1, -0.25)
    out = [f'<rect width="600" height="600" fill="#1A100C"/>']
    # the inn parlour: plaster wall warm from the fire off to the left, cold at the right by the snowy window
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#B07040"), (0.3, "#5A3420"), (0.62, "#20140E"), (1, "#0E1018")], 0, 0, 1, 0.2)}"/>')
    out.append(gsky(D, [(0, "#8A5A3A", 0), (1, "#000000", 0)], 2, ["#A86A44", "#2A1A14", "#6A4430"], 60, sop=(0.05, 0.15)))
    out.append(stipple(D, "M 0 0 L 600 0 L 600 600 L 0 600 Z", (0, 0, 600, 600), 4, "#0A0604", n=2400, light=(-1, 0.1), gamma=1.3, op=(0.2, 0.55)))
    # the wainscot
    out.append(gform(D, [(-20, 470), (620, 470), (620, 620), (-20, 620)], ("#6A4028", "#2E1A10", "#0A0604"), 3, light, angle=0, n=40))
    for k in range(7):
        x = 20 + k * 96
        out.append(f'<path d="M {x} 486 L {x} 610" stroke="#0A0604" stroke-width="2" opacity="0.6"/><path d="M {x + 2} 486 L {x + 2} 610" stroke="#C8885A" stroke-width="1" opacity="0.3"/>')
    out.append(f'<path d="M -20 470 L 620 470" stroke="#C8885A" stroke-width="2" opacity="0.5"/>')
    # the window at the right: snow falling in blue night
    wx0, wx1, wy0, wy1 = 452, 560, 150, 330
    out.append(f'<path d="M {wx0 - 12} {wy0 - 12} L {wx1 + 12} {wy0 - 12} L {wx1 + 12} {wy1 + 16} L {wx0 - 12} {wy1 + 16} Z" fill="#1A100A"/>')
    out.append(f'<path d="M {wx0 - 12} {wy0 - 12} L {wx0 - 12} {wy1 + 16}" stroke="#8A5A38" stroke-width="3" opacity="0.6"/>')
    win = f"M {wx0} {wy0} L {wx1} {wy0} L {wx1} {wy1} L {wx0} {wy1} Z"
    out.append(f'<path d="{win}" fill="{D.lin([(0, "#14203A"), (0.7, "#2A3A5A"), (1, "#5A6A8A")])}"/>')
    out.append(f'<g {D.clip(f"<path d=\"{win}\"/>")}>{snowfall(6, (wx0, wy0, wx1, wy1), 50, (0.8, 2.0), "#FFFFFF", (0.5, 0.9))}'
               f'<path d="M {wx0} {wy1 - 18} Q {(wx0 + wx1) / 2} {wy1 - 30} {wx1} {wy1 - 14} L {wx1} {wy1} L {wx0} {wy1} Z" fill="#C8D8F0"/></g>')
    out.append(f'<path d="M {(wx0 + wx1) / 2} {wy0} L {(wx0 + wx1) / 2} {wy1} M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#1A100A" stroke-width="5"/>')
    out.append(gglow(D, 506, 240, 130, "#6A86C8", 0.22))
    # the firelight itself, flickering in from the left
    out.append(gglow(D, -40, 380, 420, "#FF9A40", 0.6))
    out.append(soft(D, f'<ellipse cx="292" cy="250" rx="70" ry="80" fill="#0A0606" opacity="0.55"/>', 20))
    # a table with the brandy and a lamp-less candle; a chair back
    out.append(gform(D, [(380, 440), (600, 440), (600, 456), (380, 456)], ("#A86A40", "#4A2A16", "#140804"), 6, light, angle=0, n=20, rim="#FFC890"))
    out.append(gform(D, [(392, 456), (404, 456), (404, 600), (392, 600)], ("#7A4A2A", "#3A2010", "#0A0402"), 7, light, n=6))
    gl_ = [(452, 440), (448, 412), (462, 408), (476, 412), (472, 440)]
    out.append(f'<path d="{smooth_closed(gl_)}" fill="#E8D8C0" opacity="0.18"/><path d="M 450 424 L 474 424 L 472 440 L 452 440 Z" fill="#B8601A" opacity="0.7"/>')
    out.append(ink(smooth_closed(gl_), "#FFE8C8", 1.2, 3, 1, 0.6))
    out.append(gcandle(D, 540, 440, 46, 13, 8, glow_r=90))
    # the empty coat standing, the hat and goggles and unwinding bandages where a man should be
    out.append(soft(D, f'<ellipse cx="320" cy="600" rx="150" ry="20" fill="#000000" opacity="0.5"/>', 8))
    out.append(greatcoat(D, 292, 298, 1.22, 9, light))
    out.append(bandaged_void(D, 292, 232, 1.18, 11))
    # the loose bandage: off the head, through the gloved hand, curling to the floor
    strip = [(318, 252), (342, 262), (346, 290), (330, 322), (320, 360), (312, 400), (309, 430), (316, 456), (302, 490), (322, 530), (298, 570), (310, 620)]
    sp = tube_pts(strip, 7, 6, wfn=lambda t: 3 + 4 * abs(math.sin(t * 9)))
    out.append(gform(D, sp, ("#FFF8EA", "#D2C4AA", "#6A5A48"), 12, light, angle=-70, n=20, core=0.3, hi_op=0.5))
    out.append(ink(smooth_open(catmull(strip, 6)), "#5A4A3A", 0.8, 3, 1, 0.4))
    # the hat, floating a hand's breadth above nothing
    def H(p):
        return T(p, 292, 192, 1.18)
    hb = H([(-56, 8), (-42, 2), (0, -3), (44, 0), (58, 7), (48, 15), (2, 14), (-46, 16)])
    crown = H([(-30, 4), (-29, -22), (-18, -34), (0, -38), (19, -34), (29, -22), (31, 2)])
    out.append(soft(D, f'<ellipse cx="292" cy="218" rx="60" ry="7" fill="#000000" opacity="0.35"/>', 4))
    out.append(gform(D, crown, ("#8A6A58", "#2E221C", "#080404"), 13, light, angle=-90, n=20, rim="#FFB060", rim_w=2))
    out.append(f'<path d="{smooth_closed(H([(-30, -8), (0, -4), (31, -8), (31, 2), (0, 6), (-30, 2)]))}" fill="#120A08"/>')
    out.append(gform(D, hb, ("#9A7A66", "#3A2A22", "#0A0604"), 14, light, angle=0, n=14, rim="#FFB060", rim_w=1.6))
    out.append(soft(D, f'<path d="{smooth_closed(H([(-44, 4), (0, 0), (46, 3)]))}" fill="none" stroke="#FFC890" stroke-width="1.4" opacity="0.4"/>', 0.5))
    out.append(band(D, 470, 600, "#000000", 0, 0.75))
    out.append(band(D, 0, 140, "#000000", 0.35, 0))
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
    out.append(_t(x0 + w1, 528, "INVISIBLE", ANTON, fs, "#F2E8D8", 3, "start", ' opacity="0.16"'))
    out.append(_t(x0 + w1, 528, "INVISIBLE", ANTON, fs, "none", 3, "start", ' stroke="#F2E8D8" stroke-width="1.6" opacity="0.85"'))
    out.append(_t(x0 + w1 + w2, 528, "MAN", ANTON, fs, "#F2E8D8", 3, "start"))
    out.append(sub_rule(300, 552, "H. G. WELLS · 1897", JOST, 17, "#E0C8A0", ls=4, max_w=300))
    return gfin(D, out, 24, 105, edge=2.6, bristle=0.45, grain=0.2, bg="#1A100C")
# --- end repaint:the-invisible-man


def steam_lines(x, y, seed, col="#FFFFFF"):
    rnd = random.Random(seed)
    out = []
    for k in (-8, 0, 8):
        out.append(taper(catmull([(x + k, y), (x + k - 5, y - 10), (x + k + 4, y - 20), (x + k - 2, y - 30)], 5), 2.4, 0.6, col, 0.5))
    return "".join(out)


# ================================================================ 14. the hound of the baskervilles — out of the fog on the moor
# --- repaint:the-hound-of-the-baskervilles
def spectral_hound(D, x, y, s, seed, col="#040606", rim="#B8FFE8", glow="#7AF0C8"):
    """The hound in full leap, facing left: a mastiff's bulk (deep chest, heavy neck, broad blunt muzzle, small drop
    ears), forelegs reaching, hind legs driving, jaws open; its muzzle and hackles burning with cold phosphorescent
    fire. (x, y) = middle of the barrel."""
    def L(p):
        return T(p, x, y, s)
    rnd = random.Random(seed)
    fw = lambda t: limb_w(15, 9.5, 9, 8, 0.45, 0.1)(t) * s
    hw = lambda t: limb_w(20, 10, 8.5, 8, 0.45, 0.05)(t) * s
    far = [tube_pts(L([(-28, 12), (-48, 30), (-66, 38), (-78, 40)]), 14 * s, 7 * s, wfn=fw),
           tube_pts(L([(28, 8), (30, 26), (50, 38), (62, 44)]), 17 * s, 7 * s, wfn=hw)]
    parts = [blob_pts(*L([(0, 0)])[0], 40 * s, 17 * s, seed, 0.03, 18, 4),
             blob_pts(*L([(-34, -2)])[0], 20 * s, 23 * s, seed + 1, 0.04, 16, -10),
             blob_pts(*L([(34, -4)])[0], 19 * s, 18 * s, seed + 2, 0.04, 14),
             tube_pts(L([(-36, -10), (-48, -20), (-58, -28)]), 36 * s, 27 * s),
             blob_pts(*L([(-64, -32)])[0], 15 * s, 13 * s, seed + 3, 0.05, 14, 10),
             tube_pts(L([(-70, -30), (-80, -27), (-90, -22)]), 18 * s, 15 * s),
             tube_pts(L([(-68, -20), (-77, -14), (-86, -8)]), 10 * s, 7 * s),
             L([(-58, -42), (-49, -44), (-51, -32)]),
             tube_pts(L([(-34, 10), (-50, 22), (-74, 26), (-88, 24)]), 15 * s, 8 * s, wfn=fw),
             tube_pts(L([(36, 6), (42, 24), (64, 30), (82, 38)]), 20 * s, 8 * s, wfn=hw),
             tube_pts(L([(50, -10), (68, -18), (86, -16), (98, -20)]), 10 * s, 3 * s)]
    paws = [blob_pts(*L([(-90, 24)])[0], 6 * s, 4.4 * s, seed + 5, 0.1, 10), blob_pts(*L([(85, 39)])[0], 6.4 * s, 4.4 * s, seed + 6, 0.1, 10, 20)]
    ds = [smooth_closed(p) for p in parts + paws]
    behind, front = union_rim(D, ds, rim, 0.5 * s, 1.8 * s, op=0.75, blur=0.7, glow=glow, glow_op=0.35, glow_w=9 * s)
    out = [f'<g fill="#020303">' + "".join(f'<path d="{smooth_closed(p)}"/>' for p in far) + "</g>", behind]
    out.append(f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    # a dull sheen modelling the shoulder and haunch
    for (cx_, cy_, r_) in ((-34, -6, 16), (34, -8, 14)):
        px_, py_ = L([(cx_, cy_)])[0]
        out.append(f'<path d="{blob(px_, py_, r_ * s, r_ * 0.7 * s, seed, 0.1, 12)}" fill="#2A3A36" opacity="0.5" {gb(D, 4)}/>')
    out.append(front)
    # hackles bristling along the neck and spine
    hk = []
    for k in range(30):
        t = k / 29
        px_, py_ = L([(-58 + t * 74, -40 + t * 22 - 6 * math.sin(t * math.pi))])[0]
        hk.append(taper([(px_, py_ + 3 * s), (px_ + rnd.uniform(-1, 3) * s, py_ - rnd.uniform(4, 9) * s)], 3 * s, 0.4, col))
    out.append("".join(hk))
    # the cold fire round the jaws, along the hackles, and the burning eye
    fire = []
    for k in range(30):
        t = rnd.random()
        bx, by = L([(-90 + t * 22, -30 + t * 6 + rnd.uniform(-2, 8))])[0]
        fire.append(taper([(bx, by), (bx + rnd.uniform(-4, 6) * s, by - rnd.uniform(5, 14) * s), (bx + rnd.uniform(0, 10) * s, by - rnd.uniform(10, 22) * s)],
                          rnd.uniform(1.4, 3) * s, 0.3, rnd.choice([rim, "#FFFFFF", glow]), rnd.uniform(0.4, 0.9)))
    for k in range(20):
        t = rnd.random()
        bx, by = L([(-58 + t * 70, -46 + t * 22 - 6 * math.sin(t * math.pi))])[0]
        fire.append(taper([(bx, by), (bx + rnd.uniform(2, 8) * s, by - rnd.uniform(4, 12) * s)], rnd.uniform(1, 2.2) * s, 0.3, rim, rnd.uniform(0.3, 0.7)))
    mx_, my_ = L([(-82, -18)])[0]
    out.append(gglow(D, mx_, my_, 40 * s, glow, 0.6))
    out.append(soft(D, "".join(fire), 0.8))
    for k in range(4):
        tx_, ty_ = L([(-86 + k * 4, -21)])[0]
        out.append(f'<path d="M {tx_:.1f} {ty_:.1f} l {1.2 * s:.1f} {3.4 * s:.1f} l {1.2 * s:.1f} {-3.4 * s:.1f} Z" fill="#E8FFF4"/>')
    ex_, ey_ = L([(-68, -36)])[0]
    out.append(gglow(D, ex_, ey_, 12 * s, "#E8FF8A", 0.9))
    out.append(f'<path d="{blob(ex_, ey_, 2.6 * s, 1.6 * s, seed, 0.05, 8, -8)}" fill="#F8FFC0"/>')
    return "".join(out)


@design("the-hound-of-the-baskervilles")
def the_hound_of_the_baskervilles():
    D = Doc2("hr-hb")
    light = (0.8, -0.6)
    out = [gsky(D, [(0, "#020606"), (0.4, "#10201E"), (0.72, "#34463E"), (1, "#121C18")], 1, ["#1A2A26", "#040808", "#3A4A44"], 50,
                blooms=((450, 270, 220, 150, "#5A7066", 0.45),))]
    out.append(stars_field(3, (0, 0, 600, 260), 50))
    out.append(gmoon(D, 456, 262, 52, 4, pal=("#FFFCEC", "#E8E8D6", "#B4B8A4"), halo="#D8F0E4", halo_r=3.6, halo_op=0.5, maria="#9AA090"))
    out.append(gcloud(D, 180, 246, 300, 28, 5, ("#A8BCB0", "#24302C", "#0A1210"), light=(1, -0.2), op=0.85, n=18, lit_n=9))
    out.append(gcloud(D, 520, 330, 180, 16, 6, ("#C8D8C8", "#2A3832", "#0E1614"), light=(-0.3, -1), op=0.7, n=10, lit_n=5))
    # the moor: long low swells, Baskerville Hall far off with two lit windows, all in haze
    out.append(soft(D, hill(D, ridge([(-20, 380), (100, 362), (220, 372), (340, 354), (460, 366), (620, 352)], 3, 6, 4), 640, ("#4A5A50", "#28342E", "#0E1410"), 2,
                            inkw=0, n=40), 1.2))
    hall = [sharp([(90, 368), (90, 342), (106, 332), (130, 332), (146, 342), (146, 368)], "#0C120E"), sharp([(84, 368), (84, 324), (90, 316), (96, 324), (96, 368)], "#0C120E"),
            sharp([(140, 368), (140, 324), (146, 316), (152, 324), (152, 368)], "#0C120E")]
    out.append(soft(D, "".join(hall), 0.6))
    for wx in (110, 126):
        out.append(gglow(D, wx, 348, 10, "#FFC860", 0.6))
        out.append(f'<rect x="{wx - 2}" y="344" width="4" height="8" fill="#FFD890"/>')
    out.append(gfog(D, 372, 40, 4, "#B8C8C0", 0.6, sd=8))
    # the granite tor at the right, weathered into stacked slabs, the mire grass below
    tor = [(352, 480), (372, 410), (404, 380), (436, 368), (468, 374), (500, 356), (540, 364), (572, 392), (620, 404), (640, 480)]
    out.append(gform(D, tor, ("#9AA49A", "#3A443E", "#0E1412"), 6, light, angle=0, n=60, core=0.35, rim="#E8F2E8", rim_w=2))
    out.append(stipple(D, smooth_closed(tor), bbox(tor), 7, "#000000", n=1000, light=light, gamma=1.3))
    for k in range(5):
        y_ = 386 + k * 18
        out.append(soft(D, pline([(384 + k * 8, y_), (480, y_ + 4), (620, y_ - 2)], "#060A08", 2, k, 0.6, 1), 0.6))
        out.append(soft(D, pline([(386 + k * 8, y_ - 2.5), (480, y_ + 1.5), (620, y_ - 4.5)], "#C8D4C8", 1.2, k + 9, 0.3, 1), 0.4))
    out.append(hill(D, ridge([(-20, 452), (120, 440), (260, 456), (400, 444), (620, 460)], 6, 6, 4), 640, ("#3A4A3E", "#1A241E", "#060A08"), 7, inkw=0, n=60))
    out.append(soft(D, grass(8, (-10, 446, 610, 600), ["#2A3A2A", "#3A4A34", "#0E140E"], 200, (8, 22), op=(0.4, 0.8)), 0.4))
    # the hound, bursting out of the fog bank toward us
    out.append(gglow(D, 300, 400, 200, "#7AF0C8", 0.18))
    out.append(gfog(D, 476, 60, 8, "#A8B8B0", 0.5, sd=10))
    out.append(spectral_hound(D, 318, 420, 1.55, 7))
    out.append(gfog(D, 520, 70, 9, "#8A9A94", 0.55, sd=12))
    out.append(band(D, 0, 200, "#000000", 0.55, 0))
    out.append(band(D, 510, 600, "#000000", 0, 0.55))
    out.append(block(D, 300, 128, "THE HOUND", ANTON, 92, "#F2F8E8", "#1E5A48", depth=8, ang=(0.7, 1.0), ls=6, max_w=440, face2="#B8E8D0", shadow="#000000"))
    out.append(tx(300, 172, "of the Baskervilles", SERIF_IT, 36, "#D8F2E8", max_w=360))
    out.append(sub_rule(300, 548, "ARTHUR CONAN DOYLE · 1902", CINZEL, 17, "#D8F2E8", ls=2.5, max_w=380, line="#7AF0C8", line_w=24))
    return gfin(D, out, 25, 111, edge=2.4, bristle=0.4, grain=0.18, bg="#0A1210")
# --- end repaint:the-hound-of-the-baskervilles


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


# --- repaint:the-turn-of-the-screw
def governess(D, x, base, s, seed, col="#141020", rim="#FFD8B8"):
    """A governess of the 1840s seen from behind, eight heads tall: hair in a low knot, a shawl over narrow sloping
    shoulders, a fitted bodice, a full bell skirt to the ground. (x, base) = ground; s=1 is 100 px tall."""
    def L(p):
        return T(p, x, base, s)
    skirt = [(-24, 0), (-22, -14), (-18, -30), (-12, -44), (-7, -54), (7, -54), (12, -44), (18, -30), (22, -14), (25, 0), (12, 1.5), (0, 0.6), (-12, 1.5)]
    bodice = [(-7, -54), (-8.4, -66), (-9.6, -76), (-10.4, -81), (-6, -84.4), (-3, -86), (3, -86), (6, -84.4), (10.4, -81), (9.6, -76), (8.4, -66), (7, -54)]
    shawl = [(-11, -82), (-6, -86), (6, -86), (11, -82), (12, -74), (6, -66), (0, -62), (-6, -66), (-12, -74)]
    neck = [(-2.2, -85.6), (-2.2, -89.4), (2.2, -89.4), (2.2, -85.6)]
    head = blob_pts(*L([(0, -94.2)])[0], 5.4 * s, 6.4 * s, seed, 0.04, 14)
    knot = blob_pts(*L([(0.6, -90.6)])[0], 3.2 * s, 2.4 * s, seed + 1, 0.08, 10)
    arms = [tube_pts(L([(-10.4, -80), (-12, -68), (-10.6, -56)]), 4.4 * s, 3.4 * s), tube_pts(L([(10.4, -80), (12, -68), (10.6, -56)]), 4.4 * s, 3.4 * s)]
    ds = [smooth_closed(L(skirt)), smooth_closed(L(bodice)), smooth_closed(L(neck)), smooth_closed(head), smooth_closed(knot)] + [smooth_closed(a) for a in arms]
    behind, front = union_rim(D, ds, rim, -0.9 * s, 0.5 * s, op=0.85, blur=0.3)
    out = [behind, f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>", front]
    out.append(gform(D, L(shawl), ("#5A4A6A", "#2A2034", "#0A0810"), seed + 2, (-1, -0.3), n=6, rim=rim, rim_w=0.8))
    out.append(folds(D, smooth_closed(L(skirt)), [L([(-8, -50), (-14, -24), (-18, -2)]), L([(-2, -52), (-4, -26), (-6, 0)]), L([(6, -50), (10, -24), (14, -2)])],
                     "#000000", "#6A5A80", seed, w=(1.6 * s, 0.4), op=0.6, sd=0.8, lw=(0.8, 0.2), lop=0.5, loff=(-0.6, 0)))
    return "".join(out)


def bly_tower(D, x0, x1, top, base, seed, light=(-1, -0.2)):
    """The old square tower at Bly: rubble masonry lit on its west face by the sunset, crenellations, arrow slits, ivy."""
    rnd = random.Random(seed)
    out = []
    w = x1 - x0
    body = [(x0, base), (x0, top + 16), (x1, top + 16), (x1, base)]
    out.append(gform(D, body, ("#B89AA8", "#5A4A62", "#1E1828"), seed, light, angle=-90, n=0, core=0.4, hi_op=0.4, sharp=True))
    out.append(rubble_wall(D, pd(body), (x0, top + 16, x1, base), seed + 1, ["#E8C8C8", "#5A4A62", "#8A7A90", "#2A2236"], light, n=180, size=(8, 20), joints="#1A1424"))
    # the parapet and merlons
    merl = []
    for k in range(6):
        mx = x0 - 6 + k * (w + 12) / 5.4
        merl.append([(mx, top + 18), (mx, top), (mx + w / 9, top), (mx + w / 9, top + 18)])
    out.append(gform(D, [(x0 - 6, top + 26), (x1 + 6, top + 26), (x1 + 6, top + 12), (x0 - 6, top + 12)], ("#C8AAB8", "#6A5A72", "#241C2E"), seed + 2, light, angle=0, n=6, sharp=True))
    for k, mpts in enumerate(merl):
        out.append(gform(D, mpts, ("#C8AAB8", "#6A5A72", "#241C2E"), seed + 3 + k, light, n=0, rim="#FFD8C0", rim_w=1.2, sharp=True))
    for (sx, sy) in ((x0 + w * 0.5, top + 70), (x0 + w * 0.5, top + 150)):
        out.append(f'<path d="{smooth_closed(arch_pts(sx - 4, sx + 4, sy, sy + 26, 4))}" fill="#0E0A14"/>')
    # ivy climbing the shadowed side
    ivy = []
    for _ in range(140):
        iy = rnd.uniform(top + 60, base)
        ix = x1 - rnd.uniform(0, w * 0.45) * (1 - (base - iy) / (base - top)) ** 0.3
        ivy.append(f'<path d="{blob(ix, iy, rnd.uniform(2, 4.4), rnd.uniform(1.6, 3), rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#1A2A1E", "#2A3A26", "#0E1810", "#3A4A2E"])}"/>')
    out.append("".join(ivy))
    return "".join(out)


@design("the-turn-of-the-screw")
def the_turn_of_the_screw():
    D = Doc2("hr-ts")
    from gouache import paper
    out = [paper(D.nid(), "#2A2030", "#C8A8D8", 6)]
    out.append(vignette(D, "#000000", 0.5))
    cx, cy, rx, ry = 300, 292, 178, 200
    oval = ell_pts(cx, cy, rx, ry, 0, 360, 72)
    cid = D.clip(f'<path d="{smooth_closed(oval)}"/>')
    light = (-1, -0.15)
    sc = [gsky(D, [(0, "#3A3A5E"), (0.35, "#6A6088"), (0.6, "#C89AA4"), (0.74, "#F2C0A0"), (0.82, "#E8B49A"), (1, "#5A4A5A")], 1,
               ["#4A4A70", "#8A7090", "#F2C8B0", "#B88AA0"], 50, blooms=((150, 360, 200, 70, "#FFD8B0", 0.6), (420, 200, 200, 120, "#5A5280", 0.4)))]
    sc.append(gglow(D, 140, 380, 150, "#FFE0B8", 0.5))
    sc.append(gcloud(D, 230, 250, 260, 18, 3, ("#FFD8C0", "#8A7090", "#4A4060"), light=(-1, 0.3), op=0.8, n=12, lit_n=7))
    sc.append(gcloud(D, 420, 180, 200, 14, 4, ("#F2C8C0", "#7A6888", "#3E3658"), light=(-1, 0.4), op=0.7, n=10, lit_n=6))
    # far park: hazy trees, the lake with the last light on it
    sc.append(soft(D, forest_band(D, 404, 440, 6, ["#6A5A7A", "#7A6888", "#5A4A6A"], 100, 500, tip=(8, 22)), 1.4))
    sc.append(f'<path d="M 100 414 Q 220 404 330 412 L 330 428 Q 220 432 100 426 Z" fill="#F2C8B0" opacity="0.7" {gb(D, 1.5)}/>')
    # the long house and the old tower at Bly
    sc.append(gform(D, [(400, 430), (400, 320), (530, 320), (530, 430)], ("#A88A98", "#4A3E56", "#1A1424"), 3, light, angle=-90, n=20, sharp=True))
    sc.append(gform(D, [(392, 324), (464, 280), (538, 324)], ("#6A5A72", "#3A3048", "#14101E"), 4, light, n=10, sharp=True))
    for k in range(3):
        wx = 428 + k * 34
        if k == 1:
            sc.append(gglow(D, wx + 4, 352, 22, "#FFC870", 0.6))
            sc.append(f'<rect x="{wx}" y="344" width="9" height="18" fill="#FFD890"/>')
        else:
            sc.append(f'<rect x="{wx}" y="344" width="9" height="18" fill="#1A1424"/>')
        sc.append(f'<rect x="{wx}" y="384" width="9" height="18" fill="#1A1424"/>')
    sc.append(bly_tower(D, 336, 404, 172, 440, 5, light))
    # the man on the battlements, hatless, very still, looking down at her
    sc.append(gglow(D, 368, 150, 30, "#FFE8E0", 0.3))
    q = []
    qd = [smooth_closed(tube_pts([(368, 172), (368.4, 158), (368, 150)], 9.6, 8)), smooth_closed(blob_pts(368.2, 145, 3.4, 4.2, 3, 0.04, 12)),
          smooth_closed(tube_pts([(363.6, 158), (362.8, 165), (363.4, 171)], 3, 2.4)), smooth_closed(tube_pts([(372.6, 158), (373.4, 165), (372.8, 171)], 3, 2.4))]
    behind, front = union_rim(D, qd, "#FFD8C0", -0.8, 0.3, op=0.9, blur=0.2)
    sc.append(behind + '<g fill="#100C16">' + "".join(f'<path d="{d}"/>' for d in qd) + "</g>" + front)
    # dark cedars framing the lawn
    for (x, b_, h_, sd_) in ((70, 452, 230, 3), (150, 446, 160, 4), (568, 450, 210, 5)):
        sc.append(taper([(x, b_), (x + 3, b_ - h_ * 0.5), (x - 2, b_ - h_ * 0.85)], 9, 3, "#14101C"))
        for k in range(5):
            ty = b_ - h_ * (0.3 + 0.62 * k / 4)
            sc.append(crown(D, x + (k % 2) * 8 - 4, ty, h_ * (0.36 - 0.05 * k), h_ * 0.07, sd_ * 10 + k, ["#5A4A64", "#2A2236", "#14101C"], light, n=34, dab=(0.16, 0.3),
                            rim="#E8A8A0"))
    # the lawn, the gravel walk, and the governess stopped on it
    lawn = [(-20, 432), (200, 426), (420, 430), (620, 424), (620, 640), (-20, 640)]
    sc.append(gform(D, lawn, ("#9AA088", "#4E5A46", "#18201A"), 6, light, angle=-4, n=60, core=0.2))
    sc.append(f'<path d="M 230 640 Q 270 520 330 436 L 350 436 Q 330 520 362 640 Z" fill="#C8B4A8" opacity="0.55" {gb(D, 1)}/>')
    sc.append(soft(D, f'<ellipse cx="300" cy="468" rx="24" ry="4" fill="#000000" opacity="0.35"/>', 2))
    sc.append(governess(D, 300, 468, 0.78, 7))
    for (bx, by, bs) in ((210, 150, 0.6), (240, 136, 0.45), (480, 190, 0.5), (182, 172, 0.4), (500, 214, 0.35)):
        sc.append(bird_v(bx, by, bs * 10, "#1A1428"))
    sc.append(f'<path d="{smooth_closed(oval)}" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.5)])}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(ink(smooth_closed(oval), "#D8B060", 3, 2, 1, 0.95))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx + 11, ry + 11, 0, 360, 72)), "#D8B060", 1.4, 3, 1, 0.8))
    for k in range(52):
        a = 2 * math.pi * k / 52
        out.append(f'<circle cx="{cx + math.cos(a) * (rx + 5.5):.1f}" cy="{cy + math.sin(a) * (ry + 5.5):.1f}" r="1.7" fill="#E8C878"/>')
    for (x, y, r_) in ((92, 92, 135), (508, 92, 225), (92, 508, 45), (508, 508, -45)):
        out.append(fleuron(x, y, 18, "#D8B060", r_, 0.9))
    out.append(tx(300, 540, "The Turn of the Screw", SERIF_IT, 40, "#F2E2F2", max_w=420))
    out.append(tx(300, 70, "HENRY JAMES · 1898", CINZEL, 17, "#D8B8E0", ls=5, max_w=300))
    return gfin(D, out, 27, 109, edge=2.2, bristle=0.4, grain=0.18, bg="#2A2030", gcol="#2A1E36", gop=0.5)
# --- end repaint:the-turn-of-the-screw


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


# --- repaint:the-werewolf
def howling_wolf(D, x, base, s, seed, col="#05070E", rim="#E8F0FF"):
    """A wolf in profile on the rocks, head flung up to howl: deep chest, long legs with proper joints, bushy tail
    hanging, a ruff on the throat. Built from overlapping anatomical masses into one silhouette. Facing left."""
    def L(p):
        return T(p, x, base, s)
    light = (-0.5, -1)
    far_c = "#02030A"
    out = []
    # far legs, a shade darker
    for pts, w0, w1 in (([(-16, -50), (-14, -32), (-17, -9), (-22, 0)], 11, 6), ([(30, -56), (24, -36), (36, -18), (32, 0)], 15, 6)):
        out.append(rimlit(D, tube_pts(L(pts), w0 * s, w1 * s), far_c, rim, light, w=1.1, op=0.45))
    parts = []
    parts.append(blob_pts(*L([(12, -57)])[0], 40 * s, 15.5 * s, seed, 0.04, 18, -3))                 # barrel and loin
    parts.append(blob_pts(*L([(-22, -57)])[0], 17 * s, 19 * s, seed + 1, 0.05, 16))                 # deep chest
    parts.append(blob_pts(*L([(44, -58)])[0], 15 * s, 13 * s, seed + 2, 0.05, 14))                  # haunch
    parts.append(tube_pts(L([(-22, -64), (-30, -84), (-40, -100)]), 30 * s, 19 * s))               # neck
    parts.append(blob_pts(*L([(-42, -107)])[0], 11 * s, 9 * s, seed + 3, 0.05, 14, -40))            # skull
    parts.append(tube_pts(L([(-46, -110), (-58, -119), (-69, -128)]), 11 * s, 5 * s))              # upper jaw
    parts.append(tube_pts(L([(-48, -104), (-56, -110), (-63, -116)]), 7 * s, 3 * s))               # lower jaw, open
    parts.append(L([(-41, -113), (-35, -128), (-30, -111)]))                                         # ear
    parts.append(tube_pts(L([(-24, -50), (-26, -33), (-28, -9), (-35, 0)]), 13 * s, 6.5 * s))      # near foreleg
    parts.append(tube_pts(L([(44, -58), (36, -36), (50, -18), (46, 0)]), 20 * s, 6.5 * s,
                          wfn=lambda t: (22 - 15 * t + (4 if t < 0.45 else 0)) * s))               # near hind leg
    parts.append(tube_pts(L([(54, -64), (64, -50), (68, -30), (64, -14)]), 13 * s, 7 * s))          # tail
    ds = [smooth_closed(p) for p in parts]
    paws = [L([(-40, 0), (-28, 0), (-29, -5), (-37, -5)]), L([(39, 0), (52, 0), (51, -5), (42, -5)])]
    ds += [smooth_closed(p) for p in paws]
    behind, front = union_rim(D, ds, rim, 0.5 * s, 1.7 * s, op=0.8, blur=0.5, glow="#C8D8FF", glow_op=0.3, glow_w=5)
    out.append(behind)
    out.append(f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(front)
    # the ruff and a little rough fur along the throat and tail
    rnd = random.Random(seed)
    tufts = []
    for k in range(20):
        t = k / 19
        px_, py_ = L([(-48 + t * 26, -100 + t * 36)])[0]
        tufts.append(taper([(px_ + 2 * s, py_ - 1 * s), (px_ - rnd.uniform(3, 7) * s, py_ + rnd.uniform(1, 4) * s)], 2.6 * s, 0.4, col))
    for k in range(10):
        t = k / 9
        px_, py_ = L([(62 + t * 6, -52 + t * 36)])[0]
        tufts.append(taper([(px_, py_), (px_ + rnd.uniform(2, 5) * s, py_ + rnd.uniform(-1, 3) * s)], 2.4 * s, 0.4, col))
    out.append("".join(tufts))
    ex_, ey_ = L([(-46, -110)])[0]
    out.append(f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{1.0 * s:.1f}" fill="#C8D8FF" opacity="0.7"/>')
    return "".join(out)


def snow_pine(D, x, base, h, seed, dark="#0A1022", snow=("#FFFFFF", "#C8D4F0", "#6A7AA8"), light=(-0.5, -1)):
    """A spruce bowed under snow: dark drooping tiers, each tier capped with a painted pad of snow lit from the moon."""
    rnd = random.Random(seed)
    out = [taper([(x, base), (x, base - h * 0.95)], h * 0.05, h * 0.01, "#0A0A14")]
    tiers = int(8 + h / 30)
    pads = []
    for i in range(tiers):
        t = i / tiers
        y = base - h * 0.08 - t * h * 0.88
        w = h * 0.3 * (1 - t) ** 0.9 + 4
        sag = w * 0.35
        for sg in (-1, 1):
            tip = (x + sg * w * rnd.uniform(0.85, 1.1), y + sag * rnd.uniform(0.6, 1.0))
            out.append(taper([(x, y - 4), (x + sg * w * 0.5, y + sag * 0.15), tip], w * 0.28, 1.5, dark))
            pads.append(taper([(x, y - 6), (x + sg * w * 0.45, y - 1 + sag * 0.1), (tip[0] - sg * w * 0.12, tip[1] - 4)], w * 0.14, 1.2,
                              snow[0] if sg < 0 else snow[1], 0.95))
    return "".join(out) + "".join(pads)


@design("the-werewolf")
def the_werewolf():
    D = Doc2("hr-ww")
    out = [gsky(D, [(0, "#03050E"), (0.45, "#101C3C"), (0.8, "#24345A"), (1, "#34466C")], 1, ["#1A2A54", "#060A1A", "#3A4A72"], 50,
                blooms=((300, 270, 260, 200, "#4A5E92", 0.5),))]
    out.append(stars_field(4, (0, 0, 600, 280), 90))
    out.append(gmoon(D, 300, 262, 84, 5, pal=("#FFFFFF", "#ECF0F8", "#AEB8CC"), halo="#C8D8FF", halo_r=2.9, halo_op=0.55, maria="#98A2B6"))
    out.append(gcloud(D, 150, 330, 260, 20, 6, ("#C8D4F4", "#2E3A60", "#141C36"), light=(0.6, -1), op=0.7, n=12, lit_n=6))
    out.append(gcloud(D, 470, 300, 220, 18, 7, ("#C8D4F4", "#2E3A60", "#141C36"), light=(-0.6, -1), op=0.6, n=10, lit_n=5))
    # far forest in blue haze, the rocky knoll against the moon with the wolf howling on it
    out.append(forest_band(D, 352, 420, 3, ["#2A3A60", "#34466E", "#22305A"], -20, 620, tip=(14, 34), light="#6A80B8"))
    out.append(gfog(D, 360, 40, 4, "#8A9CC8", 0.55, sd=8))
    knoll = [(170, 400), (210, 372), (248, 352), (290, 342), (330, 346), (370, 360), (420, 392), (440, 410), (160, 410)]
    out.append(gform(D, knoll, ("#C8D4F0", "#3A4870", "#0A1022"), 8, (0, -1), angle=-10, n=30, core=0.4, rim="#FFFFFF", rim_w=2))
    out.append(howling_wolf(D, 290, 344, 0.92, 9))
    # snow pines close on both sides, the clearing between them
    for (xx, b_, h_, sd_) in ((40, 470, 240, 1), (110, 450, 190, 2), (-10, 520, 300, 3), (520, 460, 220, 4), (580, 500, 280, 5), (470, 440, 150, 6)):
        out.append(snow_pine(D, xx, b_, h_, sd_))
    snow = [(-20, 420), (160, 412), (300, 418), (460, 410), (620, 420), (620, 620), (-20, 620)]
    out.append(gform(D, snow, ("#FFFFFF", "#B8C6E6", "#4A5A88"), 10, (0, -1), angle=0, n=50, core=0.25, hi_op=0.3))
    out.append(soft(D, "".join(f'<ellipse cx="{x_}" cy="{y_}" rx="{rx_}" ry="{ry_}" fill="#5A6A98" opacity="0.35"/>' for x_, y_, rx_, ry_ in
                               ((90, 470, 120, 20), (520, 480, 130, 22), (300, 560, 220, 30))), 10))
    out.append(f'<path d="M 140 620 Q 250 480 296 420 L 312 420 Q 370 480 480 620 Z" fill="#7A8AB8" opacity="0.3" {gb(D, 4)}/>')
    # the tracks: boots at first, then something else
    steps = [(330, 590, 1.5, 0), (276, 556, 1.4, 1), (318, 520, 1.25, 0), (282, 492, 1.12, 1), (312, 468, 1.0, 0), (290, 450, 0.9, 1),
             (306, 436, 0.8, 0), (294, 426, 0.7, 1)]
    for k, (x, y, sc_, side) in enumerate(steps):
        ang = -8 if side else 8
        sh = "#3A4A78"
        g_ = f'<g {gb(D, 0.6)}>'
        if k < 3:
            out.append(g_ + bootprint(x, y, sc_, ang, sh) + "</g>")
        elif k == 3:
            out.append(g_ + bootprint(x, y, sc_, ang, sh, 0.4) + pawprint(x + 2, y - 4, sc_ * 0.95, ang, "#2A3866", 0.65) + "</g>")
        else:
            out.append(g_ + pawprint(x, y, sc_ * 1.15, ang, "#2A3866") + "</g>")
        out.append(f'<path d="{blob(x - 2, y - 14 * sc_, 9 * sc_, 2 * sc_, k, 0.2, 8)}" fill="#FFFFFF" opacity="0.5" {gb(D, 0.8)}/>')
    # the torn red scarf caught on a thorn branch
    br = crooked_tree(78, 600, 250, 9, "#05070E", w=12, lean=14, spread=34, depth=4)
    out.append(br)
    scarf = tube_pts([(150, 424), (164, 436), (174, 456), (168, 474), (176, 494)], 13, 7)
    out.append(gform(D, scarf, ("#FF5A4A", "#B01A16", "#3A0404"), 11, (-0.6, -1), n=10, core=0.4, rim="#FFC8C0", rim_w=1.2))
    out.append(gform(D, tube_pts([(150, 424), (138, 440), (142, 466)], 11, 5), ("#E83A30", "#8A1010", "#2A0202"), 12, (-0.6, -1), n=6))
    for k in range(4):
        out.append(f'<path d="M {170 + k * 3} {488 + k * 3} l {k - 2} 10" stroke="#B8201A" stroke-width="1.6"/>')
    out.append(snowfall(10, (0, 0, 600, 600), 90, (0.6, 2.2), "#FFFFFF", (0.4, 0.9)))
    out.append(band(D, 0, 180, "#000000", 0.5, 0))
    # lettering
    out.append(glow_text(D, 300, 118, "THE WEREWOLF", BEBAS, 92, "#F2F6FF", "#9AB8FF", ls=8, max_w=450, shadow="#000000"))
    out.append(tx(300, 158, "Don’t follow the tracks.", SERIF_IT, 28, "#DCE8FF", max_w=400))
    return gfin(D, out, 28, 107, edge=2.4, bristle=0.4, grain=0.18, bg="#0A1022")
# --- end repaint:the-werewolf


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
# --- repaint:la-llorona
def weeping_woman(D, x, base, s, seed, glow="#DFF6F4"):
    """The woman in white seen from behind, eight heads tall: head bowed into her hands (elbows lifted), long black hair
    under a wind-lifted veil, a high-waisted gown falling in long folds to the water. Backlit: luminous edges."""
    def L(p):
        return T(p, x, base, s)
    out = []
    body = [(-20, 0), (-17.5, -14), (-14.5, -30), (-12.6, -44), (-12.2, -51), (-11.4, -58), (-11.6, -66), (-11.4, -74), (-10.4, -79.5), (-8.4, -83.6),
            (-4, -86.5), (-4.5, -91), (-2.5, -97), (1.5, -99.5), (5, -97), (6, -92), (4, -86.5), (8.4, -84), (10.5, -80), (11.4, -74), (11.6, -66),
            (11.4, -58), (12.4, -51), (13.4, -42), (15, -27), (18.5, -12), (23, 0), (16, 2), (8, 0.6), (0, 1.8), (-9, 0.6)]
    bp = L(body)
    out.append(f'<path d="{smooth_closed(bp)}" fill="none" stroke="{glow}" stroke-width="{6 * s:.1f}" opacity="0.35" {gb(D, 4 * s)}/>')
    out.append(gform(D, bp, ("#F4FCFC", "#A8C4C8", "#3E5A64"), seed, (0.2, -1), angle=-92, n=60, core=0.32, core_op=0.6, refl="#E8FAFA", refl_op=0.5,
                     slen=(18 * s, 40 * s), sw=(0.8, 2.2), sop=(0.08, 0.22), cols=["#FFFFFF", "#7A9AA2", "#C8E0E2"]))
    # backlit: both edges glow
    for lgt in ((-1, -0.3), (1, -0.3)):
        out.append(f'<g {D.clip(f"<path d=\"{smooth_closed(bp)}\"/>")}><path d="{smooth_closed(bp)} {smooth_closed(shift(bp, -lgt[0] * 2.6 * s / 2.6, -lgt[1] * 1.6))}" '
                   f'fill-rule="evenodd" fill="#FFFFFF" opacity="0.85" {gb(D, 0.8)}/></g>')
    fl = [L([(-6, -60), (-9, -40), (-13, -20), (-16, -2)]), L([(-1, -59), (-3, -38), (-5, -18), (-6, 0)]), L([(3, -60), (4, -40), (6, -20), (8, 1)]),
          L([(6, -58), (9, -38), (13, -18), (17, 0)]), L([(-9, -46), (-11, -26), (-14, -8)]), L([(9, -44), (12, -24), (15, -6)]),
          L([(-8.2, -82), (-8.6, -70), (-8.4, -56)]), L([(8.2, -82), (8.6, -70), (8.6, -56)])]
    out.append(folds(D, smooth_closed(bp), fl, "#2A4650", "#FFFFFF", seed, w=(2.4 * s, 0.6 * s), op=0.55, sd=1.6, lw=(1.4, 0.3), lop=0.6, loff=(1.6, 0)))
    # the sash under the bust, a shadow under the shoulder blades
    out.append(soft(D, f'<path d="{smooth_closed(L([(-7.5, -62.5), (0, -61.5), (7, -62.5), (7, -60.5), (0, -59.5), (-7.5, -60.5)]))}" fill="#4A6670" opacity="0.6"/>', 0.8))
    # long black hair down the back, under the veil
    rnd = random.Random(seed)
    hl = []
    for k in range(22):
        t = k / 21
        x0 = -4 + 8 * t
        end = (-5.5 + 11 * t + rnd.uniform(-1.2, 1.2), -60 - rnd.uniform(0, 8) + 4 * abs(t - 0.5))
        hl.append(taper(L([(x0 * 0.6, -98.5), (x0 * 1.25, -88), (end[0] * 1.05 + rnd.uniform(-0.6, 0.6), -76), end]), rnd.uniform(1.6, 2.8) * s, 0.25 * s,
                        rnd.choice(["#0A0E12", "#141A20", "#05080A"]), rnd.uniform(0.85, 1)))
    out.append(f'<path d="{blob(*L([(0.6, -93)])[0], 5.4 * s, 6.6 * s, seed, 0.05, 12)}" fill="#0C1014"/>')
    out.append("".join(hl))
    out.append("".join(taper(L([(rnd.uniform(-3, 4), -97), (rnd.uniform(-4, 5), -84), (rnd.uniform(-4, 4), -70)]), 0.5 * s, 0.2, "#8AA6AE", rnd.uniform(0.25, 0.5))
                       for _ in range(9)))
    # the veil: translucent, lifting to the right in the river wind
    veil = L([(-3, -101), (3.5, -100.5), (8, -94), (12, -84), (17, -70), (23, -54), (28, -40), (20, -42), (14, -47), (6, -50), (-3, -49), (-10, -46),
              (-12, -54), (-10.5, -68), (-8, -82), (-6, -93)])
    out.append(f'<path d="{smooth_closed(veil)}" fill="{D.lin([(0, "#FFFFFF", 0.55), (0.6, "#E8F8F8", 0.35), (1, "#E8F8F8", 0.08)], 0, 0, 0.3, 1)}"/>')
    out.append(folds(D, smooth_closed(veil), [L([(0, -98), (6, -76), (16, -50)]), L([(-3, -96), (-2, -74), (2, -52)]), L([(3, -98), (11, -78), (24, -46)])],
                     "#7A9AA0", "#FFFFFF", seed + 2, w=(1.6 * s, 0.4), op=0.4, sd=1, lw=(1.2, 0.3), lop=0.7, loff=(1.2, 0)))
    out.append(ink(smooth_open(veil[1:7]), "#FFFFFF", 1.4, seed, 1, 0.6))
    return "".join(out)


@design("la-llorona")
def la_llorona():
    D = Doc2("hr-ll")
    out = [gsky(D, [(0, "#01060C"), (0.4, "#0A2230"), (0.66, "#1E4650"), (0.78, "#2E5A60"), (1, "#0A1A20")], 1, ["#1A3A44", "#04121A", "#3A6A70"], 40,
                blooms=((420, 250, 260, 160, "#4A8A8C", 0.45), (140, 180, 200, 140, "#0E2A36", 0.6)))]
    out.append(stars_field(7, (0, 0, 600, 280), 80))
    out.append(gmoon(D, 424, 236, 50, 7, pal=("#FFFFFF", "#E8F2F0", "#A8BCB8"), halo="#C8F2EE", halo_r=4.2, halo_op=0.55, maria="#8AA4A0"))
    out.append(gcloud(D, 520, 284, 220, 22, 3, ("#B8E0DC", "#2A4E56", "#0E2228"), light=(-0.4, -1), op=0.8, n=14, lit_n=8))
    out.append(gcloud(D, 120, 226, 320, 20, 4, ("#5A8A8C", "#183640", "#06141A"), light=(1, -0.3), op=0.7, n=14, lit_n=5, sd=(9, 4)))
    # far bank: low hills, a village church with one lit window, willows and huizache, all dissolving in mist
    out.append(soft(D, hill(D, ridge([(-20, 338), (90, 318), (200, 330), (330, 312), (470, 326), (620, 314)], 3, 5, 3), 380,
                            ("#3A6266", "#22444A", "#0E2428"), 2, inkw=0, n=20), 1.2))
    out.append(soft(D, poly([(132, 322), (132, 300), (150, 300), (150, 322)], "#123034") + poly([(136, 300), (136, 284), (146, 284), (146, 300)], "#123034")
                    + sharp([(134, 286), (141, 272), (148, 286)], "#123034"), 0.6))
    out.append(gglow(D, 141, 309, 16, "#FFC870", 0.6))
    out.append(f'<rect x="139.5" y="305" width="3" height="6" fill="#FFD890"/>')
    wl = "".join(willow(D, xw, 344, hw, sw_, "#0A2226", 1.0, 40, ln) for xw, hw, sw_, ln in ((40, 120, 3, 10), (88, 90, 4, -6), (548, 130, 5, -12), (500, 86, 6, 8)))
    out.append(soft(D, wl, 1.2))
    out.append(gfog(D, 344, 30, 5, "#9AC8C8", 0.55, sd=7))
    out.append(gfog(D, 352, 26, 15, "#7AAAAC", 0.6, sd=6, rx=(80, 200)))
    # the river, a long moon-path, ripples and drifting marigold petals
    river = "M -20 342 L 620 342 L 620 620 L -20 620 Z"
    out.append(f'<path d="{river}" fill="{D.lin([(0, "#2A5A60"), (0.25, "#123038"), (1, "#020A0E")])}"/>')
    rnd = random.Random(8)
    mp = []
    for k in range(70):
        y = 346 + (k / 70) ** 1.4 * 250
        w = 12 + (y - 346) * 0.55 * rnd.uniform(0.5, 1.3)
        cx_ = 424 + rnd.uniform(-8, 8) * (1 + (y - 346) / 120)
        mp.append(taper([(cx_ - w / 2, y), (cx_ + w / 2, y + rnd.uniform(-1, 1))], rnd.uniform(1, 2.5) + (y - 346) * 0.012, 0.6, rnd.choice(["#F2FFFC", "#C8EEEA", "#FFFFFF"]),
                        rnd.uniform(0.35, 0.8) * (1 - (y - 346) / 400)))
    out.append(soft(D, "".join(mp), 0.6))
    out.append(soft(D, wave_lines(9, (0, 350, 600, 600), ["#5A8A8A", "#9AC8C0", "#020A0C"], 70, (14, 44), 1.6, 1.4, (0.2, 0.5)), 0.5))
    # her reflection, broken by the ripples
    out.append(f'<g opacity="0.32" {gb(D, 2.5)}><g transform="translate(266 496) scale(2.5 -2.2) translate(0 0)">{weeping_woman(D, 0, 0, 1, 12)}</g></g>')
    for k in range(10):
        y = 504 + k * 9
        out.append(taper([(200 + rnd.uniform(-10, 10), y), (330 + rnd.uniform(-10, 10), y)], 2, 2, "#081A20", 0.5))
    # the woman, wading into the river
    out.append(gglow(D, 268, 380, 170, "#C8F2EE", 0.22))
    out.append(weeping_woman(D, 266, 496, 2.5, 11))
    out.append(gfog(D, 496, 26, 9, "#C8ECEA", 0.75, 150, 390, sd=5, rx=(30, 70)))
    for k in range(5):
        y = 498 + k * 5
        out.append(f'<path d="{blob(268, y, 60 + k * 18, 3 + k, 30 + k, 0.1, 16)}" fill="none" stroke="#C8ECEA" stroke-width="1.4" opacity="{0.45 - k * 0.07:.2f}"/>')
    for k in range(16):
        x, y = rnd.uniform(110, 540), rnd.uniform(420, 580)
        sz = 0.6 + (y - 420) / 160
        out.append(f'<path d="{blob(x, y, 3.4 * sz, 2 * sz, k, 0.3, 8, rnd.uniform(-20, 20))}" fill="{rnd.choice(["#FFA020", "#F28A10", "#FFC040"])}" opacity="0.9"/>')
    # reeds on the near banks, black against the water
    for side, x0 in ((-1, 0), (1, 600)):
        for k in range(26):
            x = x0 - side * rnd.uniform(-10, 120) ** 1 * 1
            h = rnd.uniform(60, 190) * (1 - abs(x - x0) / 260)
            out.append(taper([(x, 610), (x + side * rnd.uniform(4, 16), 610 - h * 0.6), (x + side * rnd.uniform(8, 30), 610 - h)], 4, 0.8, "#010808"))
    out.append(band(D, 0, 190, "#000000", 0.55, 0))
    out.append(band(D, 500, 600, "#000000", 0, 0.65))
    # lettering
    out.append(letters(D, 300, 120, "La Llorona", SERIF_IT, 76, "#F2FAFA", ["#FFFFFF", "#DCF2F0", "#C8E8E8"], 34, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(spaced(300, 156, "THE WEEPING WOMAN · MEXICAN FOLKLORE", CINZEL, 16, "#C8E8E4", ls=1.5, max_w=470, shadow="#000000"))
    out.append(tx(300, 548, "No te acerques al río de noche", SERIF_IT, 24, "#E8F6F2", max_w=430))
    return gfin(D, out, 34, 102, edge=2.4, bristle=0.4, grain=0.18, bg="#06161C")
# --- end repaint:la-llorona


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


# --- repaint:spring-heeled-jack
def jack_leaping(D, x, y, s, seed, col="#0E0A10", rim="#F2E4A8"):
    """Spring-heeled Jack in mid-leap over the chimneys, as the 1838 broadsides told it: a tall, lean figure in a tight
    suit and a helmet with pointed ears, a long cloak cracking out behind, clawed hands reaching, one knee drawn up and
    the other leg trailing with its spring-heeled boot. Facing right. (x, y) = the hips."""
    def L(p):
        return T(p, x, y, s)
    light = (0.7, -0.7)
    parts = []
    cloak = [(30, -50), (14, -58), (-20, -66), (-62, -76), (-112, -84), (-92, -66), (-136, -56), (-100, -42), (-120, -22), (-80, -22), (-46, -18),
             (-16, -16), (6, -30), (22, -40)]
    parts.append(tube_pts(L([(0, 0), (16, -22), (34, -44)]), 20 * s, 24 * s, wfn=lambda t: (20 - 5 * math.sin(math.pi * min(1, t * 1.4)) + 9 * max(0, t - 0.55)) * s))
    parts.append(blob_pts(*L([(30, -42)])[0], 15 * s, 11 * s, seed + 1, 0.05, 14, -40))           # chest and shoulders
    parts.append(tube_pts(L([(36, -50), (44, -58)]), 10 * s, 8.5 * s))                               # neck
    head = blob_pts(*L([(50, -64)])[0], 8.6 * s, 10 * s, seed, 0.04, 14, 30)
    parts.append(head)
    parts.append(L([(45, -70), (44, -88), (51, -73)]))                                               # pointed ears of the helmet
    parts.append(L([(52, -73), (58, -89), (58, -70)]))
    parts.append(tube_pts(L([(6, 2), (40, -6), (32, 34), (36, 44)]), 18 * s, 8 * s, wfn=lambda t: limb_w(18, 10, 11.5, 7, 0.5)(t) * s))     # near leg: knee drawn up
    parts.append(L([(30, 40), (46, 40), (48, 46), (30, 47)]))                                         # near boot
    parts.append(tube_pts(L([(-4, 4), (-34, 18), (-66, 26), (-74, 34)]), 18 * s, 8 * s, wfn=lambda t: limb_w(18, 10, 11.5, 7, 0.46)(t) * s))  # far leg trailing
    parts.append(L([(-80, 30), (-66, 30), (-66, 38), (-82, 38)]))
    parts.append(tube_pts(L([(32, -44), (56, -38), (80, -52)]), 10 * s, 6 * s, wfn=lambda t: limb_w(11, 7.5, 8.5, 6, 0.5)(t) * s))          # near arm reaching
    parts.append(tube_pts(L([(24, -48), (8, -74), (-2, -96)]), 10 * s, 6 * s, wfn=lambda t: limb_w(11, 7.5, 8.5, 6, 0.5)(t) * s))           # far arm flung up
    ds = [smooth_closed(p) for p in parts]
    cd = smooth_closed(L(cloak))
    behind, front = union_rim(D, ds + [cd], rim, -1.3 * s, 1.3 * s, op=0.9, blur=0.5, glow="#FFF2C0", glow_op=0.35, glow_w=8)
    out = [behind]
    out.append(gform(D, L(cloak), ("#3A2A44", "#140C1C", "#020104"), seed, light, angle=180, n=40, core=0.35, slen=(20, 50), sw=(1, 2.6)))
    out.append(folds(D, cd, [L([(-10, -60), (-60, -76), (-130, -86)]), L([(-12, -40), (-70, -48), (-130, -54)]), L([(-14, -28), (-60, -30), (-110, -34)])],
                     "#000000", "#7A6A9A", seed, w=(6 * s, 1), op=0.7, sd=1.8))
    out.append(f'<g fill="{col}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(front)
    # claws on both hands
    for hand, base_a in (((82, -53), -30), ((-3, -98), -120)):
        hx, hy = L([hand])[0]
        for f in range(4):
            a = math.radians(base_a + (f - 1.5) * 18)
            out.append(taper([(hx, hy), (hx + math.cos(a) * 9 * s, hy + math.sin(a) * 9 * s), (hx + math.cos(a + 0.5) * 15 * s, hy + math.sin(a + 0.5) * 15 * s)],
                             2.6 * s, 0.4, col))
    # the springs under his heels
    for (fx, fy, ang_) in ((34, 47, 6), (-76, 38, 30)):
        px_, py_ = L([(fx, fy)])[0]
        for k in range(5):
            cx_ = px_ + math.sin(math.radians(ang_)) * k * 4 * s
            cy_ = py_ + math.cos(math.radians(ang_)) * k * 4 * s + 4 * s
            out.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_:.1f}" rx="{6 * s:.1f}" ry="{2 * s:.1f}" fill="none" stroke="#2A2430" stroke-width="{1.8 * s:.1f}" '
                       f'transform="rotate({-ang_} {cx_:.1f} {cy_:.1f})"/>')
            out.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_ - 0.8:.1f}" rx="{6 * s:.1f}" ry="{2 * s:.1f}" fill="none" stroke="{rim}" stroke-width="{0.7 * s:.1f}" opacity="0.6" '
                       f'transform="rotate({-ang_} {cx_:.1f} {cy_:.1f})"/>')
    # the red eyes "like balls of fire"
    ex_, ey_ = L([(55, -66)])[0]
    out.append(gglow(D, ex_, ey_, 9 * s, "#FF5A2A", 0.9))
    out.append(f'<circle cx="{ex_:.1f}" cy="{ey_:.1f}" r="{1.8 * s:.1f}" fill="#FFD0A0"/>')
    return "".join(out)


@design("spring-heeled-jack")
def spring_heeled_jack():
    D = Doc2("hr-sj")
    from gouache import paper
    INKC = "#1E140E"
    out = [paper(D.nid(), "#E8D8B4", "#6A4A2A", 11)]
    # masthead of the penny dreadful
    out.append(f'<rect x="40" y="40" width="520" height="96" fill="none" stroke="{INKC}" stroke-width="3"/>')
    out.append(f'<rect x="46" y="46" width="508" height="84" fill="none" stroke="{INKC}" stroke-width="1"/>')
    out.append(tx(62, 74, "No. 1", DMS, 20, INKC, max_w=90, anchor="start"))
    out.append(tx(538, 74, "ONE PENNY", BEBAS, 23, "#A8201A", ls=1, max_w=110, anchor="end"))
    out.append(tx(300, 72, "THE TERROR OF LONDON", CINZEL, 16, INKC, ls=1, max_w=262))
    out.append(tx(300, 126, "Spring-Heeled Jack", DMS, 50, INKC, max_w=460))
    # the picture: London roofs and chimney pots in fog under a yellow moon, painted over an engraved line
    px0, py0, px1, py1 = 52, 148, 548, 548
    pic = f"M {px0} {py0} L {px1} {py0} L {px1} {py1} L {px0} {py1} Z"
    cid = D.clip(f'<path d="{pic}"/>')
    sc = [gsky(D, [(0, "#1E2440"), (0.45, "#4A4A66"), (0.75, "#9A8A78"), (1, "#C8A878")], 3, ["#2A3050", "#5A5470", "#B89878"], 50,
               blooms=((410, 250, 200, 160, "#E8D8A0", 0.5),))]
    sc.append(hatch(D, pic, (px0, py0, px1, py0 + 220), 3, "#141830", ang=-8, step=4.2, w=1.0, light=(0.4, 1), op=0.5))
    sc.append(gmoon(D, 412, 246, 50, 4, pal=("#FFF8D8", "#F2E2A8", "#C8A868"), halo="#FFE8A8", halo_r=3.6, halo_op=0.6, maria="#B8A070"))
    sc.append(gcloud(D, 250, 300, 300, 22, 5, ("#E8D8B0", "#5A5468", "#2A2A40"), light=(1, -0.4), op=0.85, n=14, lit_n=8))
    # rooftops: far, middle and near rows, chimney stacks with clay pots and smoke, a few lit garret windows
    rnd = random.Random(5)
    for row, (top, col_, hat_op, pot) in enumerate(((396, "#4A4458", 0.3, 0.8), (436, "#2A2232", 0.45, 1.0), (486, "#141018", 0.6, 1.3))):
        x = px0 - 30
        roofs = []
        while x < px1 + 20:
            w = rnd.uniform(60, 120) * (0.8 + row * 0.15)
            t_ = top + rnd.uniform(-14, 10)
            roofs.append((x, w, t_))
            x += w - 4
        for (x, w, t_) in roofs:
            rp = [(x, 620), (x, t_ + 24), (x + w * 0.5, t_), (x + w, t_ + 24), (x + w, 620)]
            sc.append(gform(D, rp, (lt(col_, 0.35), col_, dk(col_, 0.5)), int(x) + row, (1, -0.6), angle=-30, n=14, core=0.3, hi_op=0.3, sharp=True))
            sc.append(hatch(D, pd(rp), (x, t_, x + w, 620), int(x) + 7, "#0E0A10", ang=-30, step=4.6, w=0.9, light=(1, -0.6), op=hat_op))
            if row < 2 and rnd.random() < 0.6:
                wx = x + w * rnd.uniform(0.25, 0.75)
                sc.append(gglow(D, wx, t_ + 44, 20, "#FFC860", 0.4))
                sc.append(f'<rect x="{wx - 4:.1f}" y="{t_ + 38:.1f}" width="8" height="11" fill="#FFD27A"/>')
            if rnd.random() < 0.65:
                cx_ = x + w * rnd.uniform(0.2, 0.7)
                ch = rnd.uniform(26, 46) * pot
                cw = 18 * pot
                stack = [(cx_ - cw / 2, t_ + 12), (cx_ - cw / 2, t_ + 12 - ch), (cx_ + cw / 2, t_ + 12 - ch), (cx_ + cw / 2, t_ + 12)]
                sc.append(gform(D, stack, ("#C87A5A", "#7A3A2A", "#2A100A"), int(cx_), (1, -0.6), angle=-90, n=6, rim="#F2D8A0", rim_w=1.4, sharp=True))
                for j in range(int(ch / 7)):
                    sc.append(f'<path d="M {cx_ - cw / 2:.1f} {t_ + 12 - j * 7:.1f} L {cx_ + cw / 2:.1f} {t_ + 12 - j * 7:.1f}" stroke="#2A100A" stroke-width="1" opacity="0.5"/>')
                for j in range(2):
                    potx = cx_ - cw * 0.25 + j * cw * 0.5
                    sc.append(gform(D, [(potx - 3.4 * pot, t_ + 12 - ch), (potx - 2.6 * pot, t_ + 12 - ch - 12 * pot), (potx + 2.6 * pot, t_ + 12 - ch - 12 * pot),
                                        (potx + 3.4 * pot, t_ + 12 - ch)], ("#E8A07A", "#A8583A", "#3A180A"), int(potx), (1, -0.6), n=0, sharp=True))
                sc.append(soft(D, smoke(D, [(cx_, t_ - ch), (cx_ - 12, t_ - ch - 24), (cx_ - 36, t_ - ch - 40), (cx_ - 70, t_ - ch - 50)], 3, 14, int(cx_),
                                        "#B8B0B8", 0.4), 2))
        sc.append(gfog(D, top + 30, 50, 10 + row, "#B8A898", 0.45 - row * 0.1, sd=10))
    # a gas lamp below in the street
    sc.append(gglow(D, 120, 470, 70, "#FFE0A0", 0.6))
    sc.append(f'<path d="M 120 560 L 120 476" stroke="{INKC}" stroke-width="5"/>')
    sc.append(gform(D, [(108, 476), (132, 476), (128, 452), (112, 452)], ("#FFF4C8", "#F2C860", "#A87A2A"), 3, (0, 1), n=0, sharp=True))
    # Jack, across the moon
    sc.append(jack_leaping(D, 318, 292, 1.4, 7))
    fx, fy = 402, 200
    sc.append(gglow(D, fx + 36, fy - 8, 50, "#9AD8FF", 0.6))
    sc.append(f'<g transform="rotate(66 {fx} {fy})">{soft(D, flame_lick(fx, fy, 70, 24, 5, cols=("#4A9AE8", "#9AD8FF", "#FFFFFF")), 1.2)}</g>')
    sc.append(vignette(D, "#1A0E06", 0.45))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<path d="{pic}" fill="none" stroke="{INKC}" stroke-width="3"/>')
    out.append(f'<rect x="{px0 + 124}" y="{py1 - 34}" width="248" height="26" fill="#E8D8B4" stroke="{INKC}" stroke-width="2"/>')
    out.append(tx(300, py1 - 14, "A PENNY DREADFUL · 1838", CINZEL, 16, INKC, ls=1, max_w=236))
    return gfin(D, out, 35, 108, edge=2.2, bristle=0.35, grain=0.18, bg="#E8D8B4", gcol="#3A2A1A", gop=0.5)
# --- end repaint:spring-heeled-jack


# ================================================================ 25. bloody mary — the mirror at midnight
# --- repaint:bloody-mary
def gcandle(D, x, base, h, w, seed, wax=("#FFF6E4", "#E2CFAE", "#8A6E50"), lit=True, glow_r=110, light=(-0.4, -1), flame_h=None):
    """A painted candle: a wax column modelled by its own flame (top lit, sides falling into shadow), a rim of
    translucent wax round the cup, runs of wax down the side, a blue-rooted flame with a hot core and a wide glow."""
    rnd = random.Random(seed)
    out = []
    if lit and glow_r:
        out.append(gglow(D, x, base - h - 10, glow_r, "#FFB050", 0.55))
        out.append(gglow(D, x, base - h - 10, glow_r * 0.35, "#FFE2A0", 0.6))
    col = poly_pts([(x - w / 2, base), (x - w / 2, base - h + 3), (x - w * 0.2, base - h - 1), (x + w * 0.25, base - h + 1), (x + w / 2, base - h + 4), (x + w / 2, base)], 8, seed, 0.4)
    out.append(gform(D, col, wax, seed, (0.0, -1), angle=-90, n=14, core=0.0, hi_op=0.0))
    cid = D.clip(f'<path d="{smooth_closed(col)}"/>')
    out.append(f'<g {cid}><rect x="{x - w / 2 - 2:.1f}" y="{base - h - 4:.1f}" width="{w + 4:.1f}" height="{h + 8:.1f}" '
               f'fill="{D.lin([(0, wax[2], 0.7), (0.3, wax[1], 0), (0.62, wax[1], 0), (1, wax[2], 0.85)], 0, 0, 1, 0)}"/>'
               f'<rect x="{x - w / 2 - 2:.1f}" y="{base - h - 4:.1f}" width="{w + 4:.1f}" height="{h + 8:.1f}" '
               f'fill="{D.lin([(0, "#FFF4D8", 0.75), (0.25, "#FFE8B8", 0), (1, "#000000", 0.35)], 0, 0, 0, 1)}"/></g>')
    for k in range(rnd.randint(2, 3)):
        dx = rnd.uniform(-w * 0.4, w * 0.35)
        L_ = rnd.uniform(h * 0.15, h * 0.55)
        out.append(taper([(x + dx, base - h + 2), (x + dx + rnd.uniform(-1, 1), base - h + L_ * 0.6), (x + dx, base - h + L_)], w * 0.22, w * 0.18, wax[0], 0.85))
        out.append(f'<circle cx="{x + dx:.1f}" cy="{base - h + L_:.1f}" r="{w * 0.11:.1f}" fill="{wax[0]}"/>')
    out.append(f'<path d="{blob(x, base - h + 1, w * 0.44, w * 0.12, seed, 0.1, 10)}" fill="#FFF8E0" opacity="0.9"/>')
    out.append(f'<path d="M {x:.1f} {base - h + 1:.1f} L {x + 0.6:.1f} {base - h - 5:.1f}" stroke="#1A0E06" stroke-width="1.6" stroke-linecap="round"/>')
    if lit:
        fh = flame_h or max(14, w * 1.4)
        out.append(soft(D, flame_lick(x, base - h - 3, fh * 1.2, w * 0.7, seed, cols=("#FF8A2A", "#FFC860", "#FFF2C0")), 1.6))
        out.append(flame_lick(x, base - h - 3, fh, w * 0.5, seed, cols=("#FFB040", "#FFE6A0", "#FFFFFF")))
        out.append(f'<path d="{blob(x, base - h - 4, w * 0.16, w * 0.22, seed, 0.1, 8)}" fill="#3A60C8" opacity="0.55" {gb(D, 0.8)}/>')
    return "".join(out)


def mary_in_glass(D, x, base, s, seed):
    """The woman behind you in the glass, waist up, face hidden behind long black hair; a white nightgown, arms hanging,
    the lower body lost in the dark. Front view; (x, base) = her waist."""
    def L(p):
        return T(p, x, base, s)
    rnd = random.Random(seed)
    out = []
    gown = [(-6.4, 0), (-6, -6), (-6.6, -12), (-8.4, -18), (-9.8, -21), (-10.6, -24), (-11.2, -29), (-11, -35), (-10.6, -38.4), (-8.6, -40),
            (-4, -42.2), (0, -42), (4, -42.2), (8.6, -40), (10.6, -38.4), (11, -35), (11.2, -29), (10.6, -24), (10, -19), (10.4, -12), (11, -4),
            (12.6, 6), (14, 20), (15, 36), (-15, 36), (-14, 20), (-12.4, 6), (-11, -4)]
    gp = L(gown)
    out.append(gform(D, gp, ("#F2F0EA", "#9A9C9E", "#262628"), seed, (-0.3, -1), angle=-90, n=40, core=0.4, core_op=0.75, refl="#C8B8A8", slen=(6 * s, 16 * s),
                     sw=(0.5, 1.4), sop=(0.08, 0.22)))
    out.append(folds(D, smooth_closed(gp), [L([(-8.6, -38), (-9, -26), (-8.2, -14)]), L([(8.6, -38), (9, -26), (8.4, -14)]), L([(-3, -36), (-2, -20), (-3, -4)]),
                                              L([(4, -34), (3, -16), (4, 4)]), L([(-6, -30), (-7, -20)])], "#1A1A1C", "#FFFFFF", seed, w=(1.6 * s, 0.4 * s), op=0.5, sd=1.2,
                     lw=(1, 0.3), lop=0.45, loff=(-0.8, 0)))
    out.append(soft(D, f'<path d="{smooth_closed(L([(-3.6, -41.8), (0, -40.6), (3.6, -41.8), (3, -39.4), (0, -38.6), (-3, -39.4)]))}" fill="#3A3634" opacity="0.6"/>', 0.6))
    # pale hands at her sides
    for sg in (-1, 1):
        hx, hy = L([(sg * 10.4, -16.4)])[0]
        out.append(gform(D, blob_pts(hx, hy, 1.6 * s, 2.6 * s, seed + sg, 0.1, 10), ("#E8E4DC", "#A8A29A", "#3A3836"), seed + 3, (-0.3, -1), n=0))
        for f in range(3):
            out.append(taper(L([(sg * (9.8 + f * 0.5), -14.6), (sg * (9.6 + f * 0.6), -12)]), 0.8 * s, 0.5 * s, "#D8D4CC", 0.9))
    # the head bowed a little, the face behind a curtain of black hair to the breast
    hx, hy = L([(0.4, -48.6)])[0]
    out.append(gform(D, blob_pts(hx, hy, 4.4 * s, 5.8 * s, seed + 4, 0.04, 14, 4), ("#3A3838", "#141414", "#030303"), seed + 5, (-0.3, -1), n=0))
    hl = []
    for k in range(40):
        t = k / 39
        xa = -4.6 + 9.4 * t
        top = (0.4 + (xa - 0.4) * 0.3, -54.2 + abs(xa - 0.4) * 0.25)
        end = (xa * 1.25 + rnd.uniform(-0.8, 0.8), -32 - rnd.uniform(0, 7) + abs(t - 0.5) * 6)
        mid = (xa * 1.12 + rnd.uniform(-0.4, 0.4), -44)
        hl.append(taper(L([top, (xa * 1.05, -50), mid, end]), rnd.uniform(0.8, 1.5) * s, 0.15 * s, rnd.choice(["#050505", "#0E0E0E", "#1A1818", "#080808"]), rnd.uniform(0.8, 1)))
    out.append("".join(hl))
    for k in range(7):
        xa = rnd.uniform(-4, 4)
        out.append(taper(L([(xa * 0.4, -53.6), (xa, -48), (xa * 1.2, -40)]), 0.4 * s, 0.1, "#8A8A90", rnd.uniform(0.3, 0.6)))
    # a sliver of pale cheek and chin between the strands
    cx_, cy_ = L([(1.2, -45.4)])[0]
    out.append(soft(D, f'<path d="{blob(cx_, cy_, 0.8 * s, 2.0 * s, seed + 9, 0.1, 8)}" fill="#C8C4C0" opacity="0.75"/>', 0.6))
    return "".join(out)


@design("bloody-mary")
def bloody_mary():
    D = Doc2("hr-bm")
    out = [f'<rect width="600" height="600" fill="#0A0406"/>']
    # damask wall, warm where the candles reach it, black in the corners
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#5A2A26"), (0.35, "#3A1618"), (0.75, "#16080A"), (1, "#060203")], 0.5, 0.78, 0.8)}"/>')
    dm = []
    for r_ in range(9):
        for c in range(8):
            x, y = c * 84 + (r_ % 2) * 42 - 10, r_ * 72 - 10
            dm.append(f'<path d="M {x} {y - 24} C {x + 14} {y - 10} {x + 16} {y + 8} {x} {y + 24} C {x - 16} {y + 8} {x - 14} {y - 10} {x} {y - 24} Z '
                      f'M {x - 18} {y + 30} Q {x} {y + 16} {x + 18} {y + 30} Q {x} {y + 22} {x - 18} {y + 30} Z" fill="#6A2A30" opacity="0.32"/>')
    out.append(soft(D, "".join(dm), 0.8))
    out.append(stipple(D, "M 0 0 L 600 0 L 600 600 L 0 600 Z", (0, 0, 600, 600), 3, "#000000", n=2200, light=(0, 1), gamma=1.0, op=(0.2, 0.5)))
    # the mirror's cast shadow, then the baroque gilt frame
    cx, cy, rx, ry = 300, 292, 128, 172
    out.append(soft(D, f'<ellipse cx="{cx + 6}" cy="{cy - 14}" rx="{rx + 40}" ry="{ry + 40}" fill="#000000" opacity="0.6"/>', 14))
    frame = ell_pts(cx, cy, rx + 28, ry + 28, 0, 360, 72)
    gold = ("#FFE8A0", "#B8862E", "#3A2408")
    out.append(gform(D, frame, gold, 4, (0, 1), angle=0, n=0, core=0.0, hi_op=0))
    out.append(f'<path d="{smooth_closed(frame)}" fill="{D.rad([(0, "#FFE6A0", 0.0), (0.82, "#FFE6A0", 0), (0.9, "#FFF0C0", 0.45), (1, "#2A1804", 0.6)], 0.5, 0.5, 0.5)}"/>')
    # carved acanthus scrolls packed round the frame: dark recesses, then leaves in two rows, lit from below
    rnd = random.Random(5)
    rec = []
    for k in range(90):
        a = 2 * math.pi * k / 90
        rec.append(f'<circle cx="{cx + math.cos(a) * (rx + 17):.1f}" cy="{cy + math.sin(a) * (ry + 17):.1f}" r="{rnd.uniform(2, 4):.1f}" fill="#1A0E02" opacity="0.7"/>')
    out.append(soft(D, "".join(rec), 1.2))
    for row, (off, n_, sz) in enumerate(((24, 40, 10), (12, 52, 6.5))):
        for k in range(n_):
            a = 2 * math.pi * (k + 0.5 * row) / n_
            px_, py_ = cx + math.cos(a) * (rx + off), cy + math.sin(a) * (ry + off)
            ang_ = math.degrees(a) + 90 + (35 if k % 2 else -35)
            leaf = blob_pts(px_, py_, sz * rnd.uniform(0.8, 1.2), sz * 0.48, k + row * 99, 0.3, 10, ang_)
            out.append(gform(D, leaf, gold, 30 + k + row * 99, (0, 1), n=0, core=0.45, core_op=0.85, hi_op=0.75, hik=0.12))
            if row == 0:
                out.append(f'<path d="M {px_ - math.cos(math.radians(ang_)) * sz * 0.7:.1f} {py_ - math.sin(math.radians(ang_)) * sz * 0.7:.1f} L {px_ + math.cos(math.radians(ang_)) * sz * 0.7:.1f} {py_ + math.sin(math.radians(ang_)) * sz * 0.7:.1f}" stroke="#4A2E06" stroke-width="1.1" opacity="0.6"/>')
    out.append(f'<path d="{smooth_closed(frame)}" fill="{D.lin([(0, "#000000", 0.45), (0.5, "#000000", 0.1), (1, "#FFD890", 0.12)])}"/>')
    # crest at the top and a shell at the bottom
    for (yy, sz) in ((cy - ry - 40, 1.0), (cy + ry + 40, 0.8)):
        fan = [(cx + math.cos(math.radians(a_)) * 34 * sz, yy + math.sin(math.radians(a_)) * 22 * sz * (-1 if yy < cy else 1)) for a_ in range(200, 341, 20)] + [(cx, yy + 8 * sz * (1 if yy < cy else -1))]
        out.append(gform(D, fan, gold, 9 if yy < cy else 10, (0, 1), n=0, core=0.35, hi_op=0.6))
        for a_ in range(210, 340, 20):
            out.append(f'<path d="M {cx:.1f} {yy + 6 * sz * (1 if yy < cy else -1):.1f} L {cx + math.cos(math.radians(a_)) * 30 * sz:.1f} {yy + math.sin(math.radians(a_)) * 19 * sz * (-1 if yy < cy else 1):.1f}" stroke="#5A3A0A" stroke-width="1.4" opacity="0.6"/>')
    inner = ell_pts(cx, cy, rx + 6, ry + 6, 0, 360, 72)
    out.append(gform(D, inner, ("#3A2408", "#8A6420", "#FFE6A0"), 11, (0, -1), n=0, core=0, hi_op=0))
    # the glass: the dark room behind you, reflected
    glass = ell_pts(cx, cy, rx, ry, 0, 360, 72)
    gd = smooth_closed(glass)
    cid = D.clip(f'<path d="{gd}"/>')
    m = [f'<rect x="0" y="0" width="600" height="600" fill="{D.rad([(0, "#3A2A26"), (0.5, "#1A1214"), (1, "#060406")], 0.5, 0.75, 0.6)}"/>']
    # a doorway far behind, a faint grey light in it
    m.append(soft(D, f'<path d="M {cx + 14} {cy + 60} L {cx + 14} {cy - 110} L {cx + 92} {cy - 104} L {cx + 92} {cy + 60} Z" fill="#2E3034" opacity="0.8"/>', 3))
    m.append(soft(D, f'<path d="M {cx + 22} {cy + 60} L {cx + 22} {cy - 98} L {cx + 84} {cy - 94} L {cx + 84} {cy + 60} Z" fill="#4A5058" opacity="0.6"/>', 6))
    # her, standing behind you in the dark, fading out below the waist
    m.append(f'<g {gb(D, 0.9)}>{mary_in_glass(D, cx + 22, cy + 80, 3.0, 7)}</g>')
    m.append(f'<rect x="{cx - 200}" y="{cy + 20}" width="400" height="200" fill="{D.lin([(0, "#0A0608", 0), (0.45, "#0A0608", 0.85), (1, "#0A0608", 1)])}"/>')
    # the reflected candles, smaller and further back
    m.append(gglow(D, cx, cy + 140, 200, "#FF9A50", 0.2))
    for xx in (cx - 70, cx + 70):
        m.append(f'<g opacity="0.85">{gcandle(D, xx, cy + 150, 46, 10, int(xx), glow_r=70)}</g>')
    # old silvering: a diagonal sheen, foxing and desilvered spots creeping in from the rim
    m.append(f'<path d="M {cx - 120} {cy - 200} L {cx - 40} {cy - 200} L {cx + 60} {cy + 200} L {cx - 20} {cy + 200} Z" fill="#FFFFFF" opacity="0.05" {gb(D, 6)}/>')
    m.append(f'<path d="M {cx - 150} {cy - 200} L {cx - 128} {cy - 200} L {cx - 30} {cy + 200} L {cx - 52} {cy + 200} Z" fill="#FFFFFF" opacity="0.04" {gb(D, 3)}/>')
    fox = []
    for _ in range(140):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.78, 1.0) ** 0.5
        fx, fy = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        fox.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{rnd.uniform(0.6, 3.4):.1f}" fill="{rnd.choice(["#8A7A60", "#C8B890", "#2A2016"])}" opacity="{rnd.uniform(0.15, 0.45):.2f}"/>')
    m.append(soft(D, "".join(fox), 0.7))
    m.append(f'<path d="{gd}" fill="{D.rad([(0, "#000000", 0), (0.72, "#000000", 0), (1, "#000000", 0.7)])}"/>')
    out.append(f'<g {cid}>{"".join(m)}</g>')
    out.append(ink(gd, "#1A1004", 3, 2, 1, 0.9))
    # the real sill and the two candles in front of the glass
    sill = [(80, 486), (520, 486), (540, 506), (60, 506)]
    out.append(gform(D, sill, ("#C89A82", "#5A3428", "#140806"), 5, (0, -1), angle=0, n=30, rim="#FFC890", rim_w=1.6))
    out.append(f'<rect x="60" y="506" width="480" height="20" fill="{D.lin([(0, "#2A1210"), (1, "#060203")])}"/>')
    for x in (150, 450):
        out.append(cast(D, x + (20 if x > 300 else -20), 490, 40, 5, "#000000", 0.5, 3))
        out.append(gcandle(D, x, 490, 78, 18, int(x) + 1, glow_r=150))
        out.append(gform(D, [(x - 22, 492), (x + 22, 492), (x + 18, 482), (x - 18, 482)], ("#FFE8A0", "#A8782A", "#2A1804"), int(x), (0, -1), n=4))
    out.append(band(D, 510, 600, "#000000", 0, 0.65))
    out.append(band(D, 0, 120, "#000000", 0.5, 0))
    # lettering
    out.append(letters(D, 300, 552, "Bloody Mary", SERIF_IT, 70, "#E8343A", ["#FF5A5A", "#B8141A", "#FF8070"], 36, max_w=420,
                       shadow="#000000", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(tx(300, 78, "DON’T SAY IT THREE TIMES", CINZEL, 17, "#E8C8C8", ls=4, max_w=400))
    return gfin(D, out, 36, 104, edge=2.4, bristle=0.4, grain=0.18, bg="#0A0406")
# --- end repaint:bloody-mary


# ================================================================ 26. the banshee — keening on the rock by the cottage
# --- repaint:the-banshee
def keening_woman(D, x, base, s, seed, flip=True):
    """The bean sí in profile, eight heads tall, head thrown back in the keen, one hand at her breast; her grey gown
    and long silver hair stream away on the sea wind and the hem frays into mist. Facing left when flip."""
    def L(p):
        return T(p, x, base, s, flip)
    rnd = random.Random(seed)
    out = []
    light = (-1, -0.35) if flip else (1, -0.35)
    # the hair first (behind): long silver strands lifting and streaming back off the head
    hair = []
    for k in range(34):
        t = k / 33
        y0 = -98 + t * 16
        reach = rnd.uniform(48, 92) * (1 - 0.35 * t)
        sag = rnd.uniform(-6, 18) + t * 24
        pts = [(-7 + rnd.uniform(-1, 1), y0 + 4), (-18, y0 - 2 + rnd.uniform(-3, 3) + sag * 0.15), (-18 - reach * 0.4, y0 - 4 + sag * 0.45 + rnd.uniform(-4, 4)),
               (-18 - reach * 0.75, y0 + sag * 0.75 + rnd.uniform(-6, 6)), (-18 - reach, y0 + sag + rnd.uniform(-8, 8))]
        hair.append(taper(catmull(L(pts), 6), rnd.uniform(1.2, 2.6) * s, 0.2, rnd.choice(["#E8EEF4", "#B8C4D0", "#FFFFFF", "#8A98A8"]), rnd.uniform(0.35, 0.8)))
    out.append(soft(D, "".join(hair[:14]), 1.6))
    out.append("".join(hair[14:]))
    # the cloak: hood up, pressed to her front by the wind (bust, waist, knee show through), billowing back into wisps
    gown = [(4.6, -101.6), (6.8, -100.6), (5.2, -98.4), (3.4, -96), (2.8, -92), (3.6, -88.4), (5.2, -86.6), (7.6, -84.6), (8.8, -81), (9.4, -77),
            (8.6, -73), (6.6, -68.5), (6.4, -63), (7.6, -56), (8.2, -46), (8.6, -36), (7.6, -28), (7.4, -16), (9.6, -3), (10.4, 0),
            (-6, 1), (-20, 0), (-34, -3), (-50, -6), (-68, -4), (-56, -12), (-76, -18), (-54, -22), (-40, -28), (-30, -36), (-22, -46), (-15, -56),
            (-10, -66), (-7.6, -76), (-6.6, -83), (-7.6, -90), (-9.4, -97), (-6, -102.4), (-0.6, -104)]
    gp = L(gown)
    out.append(f'<path d="{smooth_closed(gp)}" fill="none" stroke="#C8DCFF" stroke-width="{8 * s:.1f}" opacity="0.28" {gb(D, 5 * s)}/>')
    out.append(gform(D, gp, ("#EEF4FC", "#8A9AB0", "#26303E"), seed, light, angle=180 if flip else 0, n=80, core=0.42, core_op=0.7, refl="#B8C8E0",
                     slen=(14 * s, 40 * s), sw=(0.8, 2.2), sop=(0.08, 0.24), rim="#FFFFFF", rim_w=1.6, rim_op=0.95))
    fl = [L([(2, -62), (-4, -46), (-14, -30), (-34, -14), (-56, -8)]), L([(0, -54), (-8, -38), (-22, -22), (-46, -12)]), L([(-4, -68), (-12, -52), (-26, -36)]),
          L([(6, -42), (3, -26), (-2, -8)]), L([(-3, -100), (-6, -92), (-5, -86)]), L([(1, -84), (-2, -76), (-4, -68)]), L([(5, -66), (4, -58)])]
    out.append(folds(D, smooth_closed(gp), fl, "#141C28", "#FFFFFF", seed, w=(2.6 * s, 0.6 * s), op=0.42, sd=2.4, lw=(1.4, 0.3), lop=0.5, loff=(1, -1.4)))
    # the face in the hood's mouth: lit full by the moon in front of her, mouth open in the keen
    face = [(4.4, -100.8), (6.0, -99.2), (7.0, -96.8), (7.2, -95.8), (9.4, -93.6), (8.2, -93.0), (8.5, -91.8), (7.8, -91.3), (8.1, -90.4), (7.6, -88.8),
            (5.6, -87.8), (4.6, -86.4), (3.4, -88.4), (2.8, -92), (3.4, -96), (5.0, -98.6)]
    out.append(gform(D, L(face), ("#FFFFFF", "#D2DAE6", "#6A7486"), seed + 6, light, n=0, core=0.45, core_op=0.75, hi_op=0.7))
    out.append(soft(D, f'<path d="{smooth_closed(L([(3.2, -97), (2.8, -92), (3.6, -88.4), (4.6, -90), (4.2, -95)]))}" fill="#1A2232" opacity="0.7"/>', 0.8))
    mx, my = L([(7.95, -90.9)])[0]
    out.append(f'<path d="{blob(mx, my, 0.5 * s, 0.32 * s, seed, 0.1, 8)}" fill="#141A26" opacity="0.9"/>')
    ex_, ey_ = L([(6.2, -95.4)])[0]
    out.append(soft(D, f'<path d="{blob(ex_, ey_, 0.8 * s, 0.35 * s, seed + 1, 0.1, 8, -15 if flip else 15)}" fill="#3A4456" opacity="0.7"/>', 0.5))
    for k in range(6):
        out.append(taper(L([(4.6 + k * 0.3, -100.2 + k * 0.6), (3 - k * 0.5, -99.4 + k * 0.5), (-6 - k * 2, -99 + k * 1.2)]), 0.8 * s, 0.2, "#F2F6FA", 0.75))
    # the near hand clutching the cloak at her breast
    out.append(gform(D, tube_pts(L([(-2, -83), (-3, -75), (-1, -69), (5, -75.6)]), 4.6 * s, 3.2 * s), ("#E4EAF4", "#9AAABE", "#3A4658"), seed + 2, light, n=8, core=0.45, rim="#FFFFFF", rim_w=1.2))
    hx, hy = L([(6.2, -76.6)])[0]
    out.append(gform(D, blob_pts(hx, hy, 2.2 * s, 1.8 * s, seed, 0.1, 10, 30), ("#FFFFFF", "#D0D8E4", "#7A8698"), seed + 4, light, n=0))
    for f in range(4):
        out.append(taper(L([(6.6, -77.8 + f * 0.9), (8.4, -77.4 + f * 0.95), (8.0, -76.6 + f * 0.95)]), 0.9 * s, 0.6 * s, "#EEF2F8"))
    # mist frays off the trailing hem
    for k in range(9):
        y0 = -4 - k * 3.6
        wisp = L([(-30 - k * 4, y0), (-56 - k * 5, y0 - 2 + rnd.uniform(-3, 3)), (-80 - k * 6, y0 + rnd.uniform(-4, 4)), (-100 - k * 5, y0 - 4 + rnd.uniform(-4, 4))])
        out.append(soft(D, taper(catmull(wisp, 6), rnd.uniform(4, 8) * s, 0.4, "#C8D4E4", rnd.uniform(0.25, 0.5)), 2.2))
    return "".join(out)


@design("the-banshee")
def the_banshee():
    D = Doc2("hr-bs")
    out = [gsky(D, [(0, "#03060E"), (0.4, "#121E32"), (0.7, "#2E3E54"), (1, "#1A2430")], 1, ["#24324A", "#060A14", "#46566E"], 50,
                blooms=((130, 250, 200, 150, "#5A6E8A", 0.45), (450, 330, 240, 120, "#2A3A50", 0.5)))]
    out.append(stars_field(8, (0, 0, 600, 250), 60))
    out.append(gmoon(D, 126, 238, 38, 8, pal=("#FFFFFF", "#E8EEF4", "#A8B4C0"), halo="#DCE8FF", halo_r=4.4, halo_op=0.5, maria="#8A96A4"))
    out.append(gcloud(D, 280, 262, 300, 26, 10, ("#A8B8D0", "#2A3648", "#0C1220"), light=(-1, -0.3), op=0.85, n=16, lit_n=8))
    out.append(gcloud(D, 520, 214, 200, 20, 11, ("#8A9AB4", "#1E2A3C", "#0A101A"), light=(-1, 0.2), op=0.7, n=12, lit_n=6))
    # the sea far below the headland, a moon-glitter on it
    out.append(f'<rect x="-20" y="318" width="640" height="80" fill="{D.lin([(0, "#4A5A70"), (1, "#1A2434")])}"/>')
    rnd = random.Random(5)
    out.append(soft(D, "".join(taper([(x := 126 + rnd.uniform(-60, 60), y := 320 + rnd.uniform(0, 44)), (x + rnd.uniform(10, 34), y)], 1.6, 0.6, "#E8EEF8", rnd.uniform(0.3, 0.7))
                               for _ in range(30)), 0.5))
    out.append(gfog(D, 330, 20, 4, "#8A9AB4", 0.5, sd=6))
    # the headland pasture, the cottage with one lit window (someone in that house is dying)
    out.append(hill(D, ridge([(-20, 380), (140, 352), (300, 364), (460, 348), (620, 372)], 4, 6, 4), 640, ("#4E5E4A", "#26321E", "#0A100A"), 5, inkw=0, n=60, lit="#9AAAB8"))
    cx_, cb = 150, 366
    out.append(cast(D, cx_ + 12, cb + 2, 70, 7, "#000000", 0.5, 3))
    out.append(gform(D, poly_pts([(cx_ - 52, cb), (cx_ - 52, cb - 34), (cx_ + 50, cb - 34), (cx_ + 50, cb)], 10, 3, 0.6), ("#D8DCDA", "#8A908C", "#2A302E"), 5,
                     (-1, -0.4), angle=-90, n=30, rim="#F2F6FF", rim_w=1.6))
    out.append(gform(D, poly_pts([(cx_ - 60, cb - 32), (cx_ - 42, cb - 64), (cx_ + 40, cb - 64), (cx_ + 58, cb - 32)], 10, 4, 1.2), ("#A8946A", "#5A4A2E", "#1A140A"), 6,
                     (-1, -0.6), angle=-12, n=50, slen=(10, 30), sw=(1, 2.4)))
    out.append(gform(D, [(cx_ + 20, cb - 58), (cx_ + 20, cb - 78), (cx_ + 32, cb - 78), (cx_ + 32, cb - 58)], ("#A8ACAA", "#5A5E5C", "#1A1C1C"), 7, (-1, -0.4), n=4))
    out.append(soft(D, smoke(D, [(cx_ + 26, cb - 80), (cx_ + 40, cb - 100), (cx_ + 70, cb - 112), (cx_ + 120, cb - 116)], 3, 14, 4, "#C8D0D8", 0.45), 1.5))
    out.append(gglow(D, cx_ - 22, cb - 18, 34, "#FFB850", 0.55))
    out.append(f'<path d="{smooth_closed(poly_pts([(cx_ - 30, cb - 8), (cx_ - 30, cb - 26), (cx_ - 14, cb - 26), (cx_ - 14, cb - 8)], 6, 2, 0.4))}" fill="#FFC860"/>')
    out.append(f'<path d="M {cx_ - 22} {cb - 26} L {cx_ - 22} {cb - 8} M {cx_ - 30} {cb - 17} L {cx_ - 14} {cb - 17}" stroke="#2A1A0A" stroke-width="1.6"/>')
    out.append(f'<path d="{blob(cx_ - 22, cb + 10, 30, 6, 4, 0.2, 10)}" fill="#FFB850" opacity="0.18" {gb(D, 3)}/>')
    out.append(gform(D, [(cx_ + 8, cb), (cx_ + 8, cb - 26), (cx_ + 22, cb - 26), (cx_ + 22, cb)], ("#5A4630", "#2A1E14", "#0A0604"), 8, (-1, -0.4), n=4))
    # a dry-stone wall running off across the field
    for k in range(46):
        x = 214 + k * 8.5 + rnd.uniform(-2, 2)
        y = 386 - k * 0.5 + rnd.uniform(-1.5, 1.5) + (k % 2) * 2
        out.append(gform(D, blob_pts(x, y, 5, 3.6, k, 0.2, 8), ("#B8C0C0", "#6A7270", "#1E2222"), k, (-1, -0.5), n=0, core=0.4, hi_op=0.4))
    # the near crag she stands on, wet granite with grass in the cracks
    rock = [(330, 640), (346, 520), (380, 490), (430, 476), (490, 480), (540, 500), (600, 528), (640, 560), (640, 640)]
    out.append(gform(D, rock, ("#9AA4A8", "#3E4648", "#0A0E10"), 7, (-1, -0.6), angle=-20, n=80, core=0.3, rim="#D8E2F0", rim_w=2))
    out.append(stipple(D, smooth_closed(rock), bbox(rock), 8, "#000000", n=1100, light=(-1, -0.6), gamma=1.2))
    out.append(hatch(D, smooth_closed(rock), bbox(rock), 9, "#05080A", ang=-60, step=5, w=1.0, light=(-1, -0.6), op=0.5))
    out.append(soft(D, grass(10, (-10, 400, 360, 610), ["#2A3A24", "#3A4A30", "#0E140C"], 160, (8, 20), lean=(0.1, 0.6), op=(0.3, 0.7)), 0.4))
    # the banshee
    out.append(gglow(D, 460, 380, 200, "#C8DCFF", 0.28))
    out.append(keening_woman(D, 462, 486, 2.55, 11, flip=True))
    out.append(gfog(D, 548, 80, 11, "#A8B8CC", 0.5, sd=12))
    out.append(band(D, 0, 190, "#000000", 0.55, 0))
    out.append(band(D, 510, 600, "#000000", 0, 0.6))
    # lettering
    out.append(glow_text(D, 300, 116, "THE BANSHEE", JOS, 62, "#F2F6FA", "#A8C8F0", ls=10, max_w=440, shadow="#000000"))
    out.append(tx(300, 150, "Bean Sí · Irish folklore", SERIF_IT, 24, "#C8D8E8", max_w=360))
    out.append(tx(300, 548, "IF YOU HEAR HER KEEN, GO HOME", CINZEL, 16, "#E8EEF4", ls=3, max_w=440))
    return gfin(D, out, 37, 103, edge=2.6, bristle=0.45, grain=0.2, bg="#0A101A")
# --- end repaint:the-banshee


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


# --- repaint:krampus
def fur_locks(D, pts, seed, cols, n=120, length=(8, 22), width=(2.4, 5), droop=0.7, rim=None, light=(1, -0.3), rim_n=40, out_only=True):
    """Shaggy fur: long tapered locks rooted along an outline, hanging with gravity and fanning out past the edge, so
    the silhouette is ragged; the locks on the side facing the light are tipped with a rim colour."""
    rnd = random.Random(seed)
    path = catmull(pts + pts[:1], 3)
    m = len(path)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    lx, ly = _unit(light)
    locks, lit = [], []
    for _ in range(n):
        i = rnd.randrange(m - 1)
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        t = rnd.random()
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        nx, ny = x - cx, y - cy
        L_ = math.hypot(nx, ny) or 1
        nx, ny = nx / L_, ny / L_
        dx, dy = nx * (1 - droop) + rnd.uniform(-0.2, 0.2), ny * (1 - droop) + droop
        dl = math.hypot(dx, dy) or 1
        dx, dy = dx / dl, dy / dl
        ln = rnd.uniform(*length)
        bend = rnd.uniform(-0.35, 0.35)
        p = [(x - dx * ln * 0.3, y - dy * ln * 0.3), (x + dx * ln * 0.5 + bend * ln * 0.3, y + dy * ln * 0.5), (x + dx * ln + bend * ln * 0.6, y + dy * ln)]
        locks.append(taper(p, rnd.uniform(*width), 0.3, rnd.choice(cols), rnd.uniform(0.75, 1)))
        if rim and (nx * lx + ny * ly) > 0.25 and len(lit) < rim_n:
            lit.append(taper([(p[0][0] + lx, p[0][1] + ly), (p[1][0] + lx * 1.5, p[1][1] + ly * 1.5), (p[2][0] + lx, p[2][1] + ly)], rnd.uniform(0.8, 1.8), 0.2, rim, rnd.uniform(0.5, 0.9)))
    return "".join(locks) + soft(D, "".join(lit), 0.4)


def krampus_figure(D, x, base, s, seed, warm="#FFB060", cool="#A8BCF0"):
    """Krampus of the old Alpine postcards, striding right: ibex horns sweeping back, a goat-demon head with a long red
    tongue, a hunched shaggy body, a woven basket on his back, birch switches raised in one clawed hand, a chain with
    bells in the other, reverse-jointed goat legs ending in cloven hooves."""
    def L(p):
        return T(p, x, base, s)
    rnd = random.Random(seed)
    out = []
    body_c = "#120A08"
    fur = ["#1E1410", "#2E2018", "#0A0604", "#3A2A20"]
    # the chain from the far hand, swinging down behind the legs, with two cowbells
    chain = catmull(L([(-6, -150), (-18, -110), (-36, -70), (-30, -40), (-12, -36)]), 6)
    for k in range(0, len(chain) - 1, 2):
        (ax, ay), (bx, by) = chain[k], chain[k + 1]
        out.append(f'<ellipse cx="{(ax + bx) / 2:.1f}" cy="{(ay + by) / 2:.1f}" rx="{3.2 * s:.1f}" ry="{1.8 * s:.1f}" fill="none" stroke="#5A5A62" stroke-width="{1.4 * s:.1f}" '
                   f'transform="rotate({math.degrees(math.atan2(by - ay, bx - ax)):.0f} {(ax + bx) / 2:.1f} {(ay + by) / 2:.1f})"/>')
    for (bx, by) in (chain[-1], chain[len(chain) // 2]):
        out.append(gform(D, [(bx - 6 * s, by), (bx + 6 * s, by), (bx + 8 * s, by + 14 * s), (bx - 8 * s, by + 14 * s)], ("#F2C870", "#9A6A20", "#2A1804"), seed + 50, (1, -0.4), n=0))
    # far leg (darker), then the basket, then the body
    def leg(pts, wfn, col):
        return gform(D, tube_pts(L(pts), 10 * s, 6 * s, wfn=wfn), (lt(col, 0.25), col, "#000000"), seed + 3, (1, -0.3), n=6, core=0.4, rim=warm, rim_w=1.4)
    lw = lambda t: (26 - 15 * t + 6 * math.sin(t * 6.3)) * s
    out.append(leg([(-8, -150), (-22, -108), (-40, -64), (-42, -16), (-46, -2)], lw, "#0A0604"))
    out.append(gform(D, L([(-56, 0), (-36, 0), (-38, -9), (-52, -11)]), ("#4A4440", "#1A1614", "#000000"), seed + 4, (1, -0.3), n=0))
    basket = L([(-2, -246), (-52, -232), (-62, -156), (-16, -148)])
    out.append(gform(D, basket, ("#B88A50", "#6A4A26", "#1E1208"), seed + 5, (1, -0.4), angle=-90, n=0, core=0.4))
    bc = D.clip(f'<path d="{smooth_closed(basket)}"/>')
    weave = "".join(f'<path d="{smooth_open(L([(-60 + j * 0.6, -236 + j * 7.6), (-30, -242 + j * 7.4), (-2 - j * 0.9, -248 + j * 7.4)]))}" fill="none" stroke="#2A1A0C" stroke-width="{2.2 * s:.1f}" opacity="0.7"/>'
                    for j in range(13))
    weave += "".join(f'<path d="M {L([(-50 + j * 9, -240)])[0][0]:.1f} {L([(-50 + j * 9, -240)])[0][1]:.1f} L {L([(-58 + j * 9.4, -150)])[0][0]:.1f} {L([(-58 + j * 9.4, -150)])[0][1]:.1f}" stroke="#E8C080" stroke-width="{1.2 * s:.1f}" opacity="0.35"/>' for j in range(6))
    out.append(f'<g {bc}>{weave}</g>')
    for k in range(5):
        tw = L([(-30 + k * 6, -246), (-36 + k * 5, -280 - k * 6), (-44 + k * 7, -300 - k * 4)])
        out.append(taper(tw, 2.4 * s, 0.6, "#2A1A10"))
    # the body: hunched torso, the shaggy coat
    torso = [(-4, -150), (-14, -184), (-8, -222), (8, -240), (30, -244), (46, -232), (52, -210), (44, -184), (30, -160), (16, -144)]
    out.append(gform(D, L(torso), ("#4A3428", "#1A100C", "#020101"), seed + 6, (1, -0.4), angle=-90, n=30, core=0.4, rim=warm, rim_w=2))
    out.append(fur_locks(D, L(torso), seed + 7, fur, n=140, length=(10 * s, 26 * s), width=(2.4 * s, 5 * s), rim=warm, light=(1, -0.3)))
    # near leg: fur trousers to the knee, a bare sinewy shank, a cloven hoof
    thigh = [(-6, -154), (30, -150), (42, -118), (30, -100), (10, -108)]
    out.append(leg([(10, -146), (36, -114), (24, -62), (40, -14), (46, -2)], lw, "#140C08"))
    out.append(gform(D, L(thigh), ("#4A3428", "#1A100C", "#020101"), seed + 8, (1, -0.4), n=10, rim=warm, rim_w=1.6))
    out.append(fur_locks(D, L(thigh), seed + 9, fur, n=70, length=(10 * s, 24 * s), width=(2.2 * s, 4.4 * s), rim=warm, droop=0.85))
    out.append(gform(D, L([(36, 0), (58, 0), (56, -9), (40, -11)]), ("#5A5450", "#1A1614", "#000000"), seed + 10, (1, -0.3), n=0, rim=warm, rim_w=1))
    out.append(f'<path d="M {L([(51, 0)])[0][0]:.1f} {L([(47, 0)])[0][1]:.1f} L {L([(48, -8)])[0][0]:.1f} {L([(48, -8)])[0][1]:.1f}" stroke="#000000" stroke-width="{1.6 * s:.1f}"/>')
    # far arm hanging back with the chain; near arm raising the birch switches
    fa = tube_pts(L([(14, -226), (2, -190), (-6, -152)]), 20 * s, 12 * s)
    out.append(gform(D, fa, ("#3A2A20", "#140C08", "#000000"), seed + 11, (1, -0.3), n=6, rim=warm, rim_w=1.2))
    out.append(fur_locks(D, fa, seed + 30, fur, n=40, length=(6 * s, 16 * s), width=(2 * s, 3.6 * s), rim=warm, droop=0.9))
    arm = [(34, -228), (60, -198), (84, -218), (92, -232)]
    out.append(gform(D, tube_pts(L(arm), 17 * s, 10 * s), ("#4A3428", "#1A100C", "#020101"), seed + 12, (1, -0.4), n=10, rim=warm, rim_w=1.6))
    out.append(fur_locks(D, tube_pts(L(arm[:3]), 17 * s, 12 * s), seed + 13, fur, n=40, length=(6 * s, 16 * s), width=(2 * s, 3.6 * s), rim=warm, droop=0.9))
    hx, hy = L([(94, -234)])[0]
    for f in range(4):
        out.append(taper([(hx - 3 * s, hy + (f - 1.5) * 3 * s), (hx + 6 * s, hy + (f - 1.5) * 3.4 * s - 2 * s), (hx + 4 * s, hy + (f - 1.5) * 3.4 * s + 3 * s)], 3 * s, 0.8, "#2A1A12"))
    for k in range(14):
        a = math.radians(-70 + k * 3.2 + rnd.uniform(-2, 2))
        Lr = rnd.uniform(70, 100) * s
        tip = (hx + math.cos(a) * Lr, hy + math.sin(a) * Lr)
        mid = (hx + math.cos(a) * Lr * 0.5 + rnd.uniform(-3, 3), hy + math.sin(a) * Lr * 0.5)
        out.append(taper([(hx, hy), mid, tip], rnd.uniform(1.6, 2.6) * s, 0.5, rnd.choice(["#3A2414", "#5A3A20", "#2A180C"])))
    out.append(taper([(hx - 6 * s, hy + 4 * s), (hx + 6 * s, hy - 6 * s)], 6 * s, 6 * s, "#A82020"))
    # the head: a goat-demon in profile, ears back, beard, tongue lolling, eyes lit
    head = L([(40, -246), (46, -262), (62, -274), (78, -270), (90, -262), (104, -252), (108, -244), (100, -238), (86, -236), (72, -228), (58, -226), (46, -232)])
    out.append(gform(D, head, ("#5A4030", "#1E140E", "#020101"), seed + 14, (1, -0.4), angle=0, n=20, core=0.4, rim=warm, rim_w=1.8))
    out.append(fur_locks(D, L([(46, -232), (60, -226), (74, -228), (82, -234)]), seed + 15, fur, n=30, length=(10 * s, 24 * s), width=(2 * s, 4 * s), droop=0.95,
                         rim=warm))
    for sg, col_ in ((1, "#120A08"), (0, "#1E140E")):
        ear = L([(50 - sg * 4, -262), (30 - sg * 4, -268), (40 - sg * 2, -256)])
        out.append(gform(D, ear, (lt(col_, 0.3), col_, "#000000"), seed + 16 + sg, (1, -0.4), n=0, rim=warm, rim_w=1))
    tongue = L([(98, -240), (104, -228), (102, -212), (96, -200), (92, -204), (96, -216), (94, -232)])
    out.append(gform(D, tongue, ("#FF6A6A", "#B01A1E", "#4A0606"), seed + 18, (1, -0.3), n=0, core=0.4, hi_op=0.7))
    ex_, ey_ = L([(80, -258)])[0]
    out.append(gglow(D, ex_, ey_, 9 * s, "#FFB030", 0.9))
    out.append(f'<path d="{blob(ex_, ey_, 2.6 * s, 1.6 * s, seed, 0.1, 8, -10)}" fill="#FFE070"/>')
    for k, (hx0, col_) in enumerate(((56, "#2A2420"), (64, "#4A3E34"))):
        horn = [(hx0, -270), (hx0 - 10, -300), (hx0 - 30, -326), (hx0 - 58, -332), (hx0 - 72, -318), (hx0 - 68, -306)]
        hp = tube_pts(L(horn), 13 * s, 3 * s)
        out.append(gform(D, hp, (lt(col_, 0.5), col_, "#050302"), seed + 20 + k, (1, -0.4), angle=-60, n=0, core=0.4, rim=warm if k else cool, rim_w=1.4))
        rg_ = catmull(L(horn), 4)
        for j in range(2, len(rg_) - 3, 2):
            (ax, ay), (bx, by) = rg_[j], rg_[j + 1]
            nx, ny = -(by - ay), bx - ax
            nl = math.hypot(nx, ny) or 1
            w_ = (13 - 10 * j / len(rg_)) * s * 0.5
            out.append(f'<path d="M {ax + nx / nl * w_:.1f} {ay + ny / nl * w_:.1f} L {ax - nx / nl * w_:.1f} {ay - ny / nl * w_:.1f}" stroke="#000000" stroke-width="{1 * s:.1f}" opacity="0.5"/>')
    return "".join(out)


@design("krampus")
def krampus_card():
    D = Doc2("hr-kr")
    from gouache import paper
    out = [paper(D.nid(), "#F2E8D2", "#7A5A3A", 12)]
    RED = "#B01E1E"
    out.append(f'<rect x="30" y="30" width="540" height="540" rx="16" fill="none" stroke="{RED}" stroke-width="5"/>')
    out.append(f'<rect x="42" y="42" width="516" height="516" rx="10" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    px0, py0, px1, py1 = 64, 134, 536, 512
    cid = D.clip(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" rx="10"/>')
    sc = [gsky(D, [(0, "#0A1230"), (0.55, "#22305C"), (0.8, "#4A5280"), (1, "#7A6A80")], 2, ["#1A2A5A", "#060A1E", "#3A4A7A"], 40,
               blooms=((180, 220, 200, 120, "#5A6AA0", 0.4),))]
    sc.append(stars_field(3, (px0, py0, px1, 280), 40))
    sc.append(gmoon(D, 160, 196, 26, 3, pal=("#FFFFFF", "#EEF0F8", "#B8C0D4"), halo="#C8D4FF", halo_r=4.0, halo_op=0.5))
    # the Alps: snowfields lit by the moon, rock in shadow, paler with distance
    sc.append(soft(D, hill(D, ridge([(40, 300), (120, 240), (190, 270), (260, 214), (340, 262), (420, 226), (500, 268), (570, 240)], 4, 8, 4), 600,
                           ("#EEF2FF", "#A8B4D8", "#5A6694"), 4, inkw=0, n=40, lit="#FFFFFF"), 0.8))
    sc.append(stipple(D, smooth_closed(ridge([(40, 300), (120, 240), (190, 270), (260, 214), (340, 262), (420, 226), (500, 268), (570, 240)], 4, 8, 4) + [(570, 400), (40, 400)]),
                      (40, 210, 570, 400), 5, "#3A4670", n=900, light=(-1, -0.6), gamma=1.6))
    sc.append(gfog(D, 300, 40, 6, "#C8D0F0", 0.5, sd=8))
    from paint import conifer
    rnd = random.Random(7)
    pines = "".join(conifer(rnd.uniform(60, 540), 330 + rnd.uniform(0, 30), rnd.uniform(26, 50), rnd.choice(["#141E36", "#1E2A44"]), rnd.random(), light="#6A7AA8")
                    for _ in range(26))
    sc.append(soft(D, pines, 0.6))
    # the village: chalets with deep snowy eaves and warm windows, smoke going straight up in the frost
    for k, (hx, w, h, b) in enumerate(((120, 96, 70, 400), (230, 80, 84, 392), (440, 100, 74, 398), (532, 80, 60, 404))):
        sc.append(cast(D, hx + 10, b + 3, w * 0.7, 6, "#1A2440", 0.5, k))
        wall = poly_pts([(hx - w / 2, b), (hx - w / 2, b - h), (hx + w / 2, b - h), (hx + w / 2, b)], 12, k, 0.6)
        sc.append(gform(D, wall, ("#B08058", "#5A3A24", "#1A0E06"), 10 + k, (-1, -0.5), angle=-90, n=30, core=0.35, slen=(10, 30)))
        for j in range(5):
            sc.append(f'<path d="M {hx - w / 2 + 2:.1f} {b - h + 8 + j * h / 5:.1f} L {hx + w / 2 - 2:.1f} {b - h + 8 + j * h / 5:.1f}" stroke="#1A0E06" stroke-width="1.2" opacity="0.5"/>')
        roof = poly_pts([(hx - w / 2 - 16, b - h + 6), (hx, b - h - 44), (hx + w / 2 + 16, b - h + 6), (hx + w / 2 + 12, b - h + 14), (hx, b - h - 32), (hx - w / 2 - 12, b - h + 14)], 10, k, 0.8)
        sc.append(gform(D, roof, ("#FFFFFF", "#C8D4EE", "#6A78A4"), 20 + k, (-1, -0.6), angle=-30, n=16, core=0.3, rim="#FFFFFF"))
        for j in range(2):
            wx = hx - w * 0.22 + j * w * 0.44
            sc.append(gglow(D, wx, b - h * 0.48, 34, "#FFB850", 0.55))
            wp = poly_pts([(wx - 8, b - h * 0.62), (wx + 8, b - h * 0.62), (wx + 8, b - h * 0.34), (wx - 8, b - h * 0.34)], 6, j + k, 0.4)
            sc.append(gform(D, wp, ("#FFF2C0", "#FFC860", "#C87A2A"), 30 + k + j, (0, 1), n=0, core=0.3))
            sc.append(f'<path d="M {wx} {b - h * 0.62:.1f} L {wx} {b - h * 0.34:.1f} M {wx - 8} {b - h * 0.48:.1f} L {wx + 8} {b - h * 0.48:.1f}" stroke="#2A1608" stroke-width="2"/>')
            sc.append(f'<path d="M {wx - 10} {b - h * 0.62 - 3:.1f} L {wx + 10} {b - h * 0.62 - 3:.1f}" stroke="#FFFFFF" stroke-width="3" opacity="0.85"/>')
        sc.append(soft(D, smoke(D, [(hx + w * 0.2, b - h - 30), (hx + w * 0.2 + 2, b - h - 70), (hx + w * 0.2 - 4, b - h - 110)], 3, 12, k, "#C8D0E8", 0.45), 1.5))
    # the snow street, trodden, with his hoofprints coming up it
    snow = [(40, 412), (200, 404), (380, 408), (600, 400), (600, 600), (40, 600)]
    sc.append(gform(D, snow, ("#FFFFFF", "#C8D2EC", "#6A76A0"), 30, (-0.4, -1), angle=0, n=60, core=0.2, hi_op=0.4))
    sc.append(f'<path d="M 230 600 Q 300 470 316 412 L 346 412 Q 376 470 470 600 Z" fill="#8A98C0" opacity="0.35" {gb(D, 3)}/>')
    for k in range(7):
        py_ = 590 - k * 26 + k * k * 1.6
        px_ = 320 + (k % 2) * 26 - k * 2
        sc.append(f'<path d="{blob(px_, py_, 6 - k * 0.5, 3.4 - k * 0.3, k, 0.2, 8)}" fill="#4A5680" opacity="0.6"/>')
    # Krampus himself, lit warm from the windows on the right and cold from the moon
    sc.append(soft(D, f'<ellipse cx="270" cy="500" rx="90" ry="12" fill="#2A3460" opacity="0.6"/>', 5))
    sc.append(krampus_figure(D, 246, 498, 1.04, 14))
    sc.append(snowfall(15, (px0, py0, px1, py1), 110, (0.8, 2.6), "#FFFFFF", (0.5, 1)))
    sc.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.45)])}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" rx="10" fill="none" stroke="#2A1A0E" stroke-width="2.4"/>')
    # the greeting, the stamp and its postmark
    out.append(letters(D, 244, 110, "Gruß vom Krampus!", SERIF_IT, 50, RED, ["#D02A2A", "#8A1010"], 38, max_w=340, wob=0.3))
    sx, sy = 494, 90
    out.append(f'<rect x="{sx - 26}" y="{sy - 32}" width="52" height="62" fill="#FFF8E8" stroke="#2A1A0E" stroke-width="1.4" stroke-dasharray="3 2"/>')
    out.append(f'<rect x="{sx - 20}" y="{sy - 26}" width="40" height="50" fill="#2E6A48"/>')
    out.append(tx(sx, sy + 4, "5", DMS, 26, "#F2E8D2", max_w=30))
    out.append(f'<path d="M {sx - 14} {sy + 16} L {sx + 14} {sy + 16}" stroke="#F2E8D2" stroke-width="2"/>')
    out.append(f'<circle cx="{sx - 14}" cy="{sy + 20}" r="22" fill="none" stroke="#3A2A4A" stroke-width="2" opacity="0.55"/>')
    for k in range(3):
        out.append(f'<path d="M {sx - 6} {sy + 12 + k * 7} q 8 -4 16 0 t 16 0" fill="none" stroke="#3A2A4A" stroke-width="1.6" opacity="0.5"/>')
    out.append(tx(300, 540, "ALPINE FOLKLORE · THE NIGHT OF 5 DECEMBER", CINZEL, 16, "#2A1A0E", ls=1, max_w=456))
    return gfin(D, out, 39, 106, edge=2.2, bristle=0.35, grain=0.16, bg="#F2E8D2", gcol="#3A2A1A", gop=0.45)
# --- end repaint:krampus


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
