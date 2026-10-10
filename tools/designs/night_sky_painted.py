"""Night Sky, hand-painted edition: zodiac constellations, zodiac glyph medallions and celestial storybook pieces.

Every magnet is painted, not drawn: brushed deep-night skies with nebula washes, stars of many sizes with soft
glows, gold constellation lines over a delicate gold-ink figure of the sign, gilded glyphs, painted moons and suns,
brush-textured lettering and grain on top. One palette for the whole series: midnight navy, indigo, violet, gold,
cream; each element (fire, earth, air, water) gets its own nebula colour story so the twelve signs never feel
interchangeable.

Run from tools/designs:  python3 night_sky_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, ink, jitter, smooth_closed, smooth_open, wash
from halloween_gouache_b import (around, arc_word, body, brush, brush_rule, bword, clip, cloud, dabs, defs, eglow, glow,
                                 grain_over, pmoon, puff_cloud, rim_lit, script, shade_in, swirl, twinkle)
from paint import lg, rg

COL = "night-sky"

# ---------------------------------------------------------------- palette
NAVY = "#0C1030"
MID = "#141A44"
INDIGO = "#232A66"
VIOLET = "#4A3A80"
PLUM = "#5E3F86"
GOLD = "#E8C36A"
GOLD_D = "#B88A36"
GOLD_DD = "#7A5420"
GOLD_L = "#FBE6AE"
CREAM = "#F6EDD6"
STARC = "#FFF6DE"
INKN = "#0A0820"

# element colour stories for the nebulae (sky stops, nebula glows, brush tints)
ELEMENTS = {
    "fire": dict(sky=[(0, "#0B0D2A"), (0.45, "#1E1B4E"), (0.8, "#3A2558"), (1, "#24183E")],
                 neb=["#C0508A", "#E58A62", "#8A3E8A"], tint=["#3A2A66", "#4E2E6A", "#28204E", "#6A3A78"]),
    "earth": dict(sky=[(0, "#0A1028"), (0.45, "#14224A"), (0.8, "#1E3450"), (1, "#141C38")],
                  neb=["#3E8A7E", "#9AAE62", "#2E6A78"], tint=["#1E3458", "#24405A", "#18284A", "#2E4A62"]),
    "air": dict(sky=[(0, "#0C0E2E"), (0.45, "#1E2058"), (0.8, "#34306E"), (1, "#1C1A44")],
                neb=["#8E7AE0", "#6A9AE6", "#B08AD8"], tint=["#2A2A6A", "#3A3478", "#20225A", "#4A3E86"]),
    "water": dict(sky=[(0, "#081030"), (0.45, "#102252"), (0.8, "#1A3866"), (1, "#101C44")],
                  neb=["#2E8AB0", "#46B4B8", "#4A62C0"], tint=["#16305E", "#1C3C6A", "#10224E", "#244A78"]),
}
SIGN_EL = {"aries": "fire", "leo": "fire", "sagittarius": "fire", "taurus": "earth", "virgo": "earth", "capricorn": "earth",
           "gemini": "air", "libra": "air", "aquarius": "air", "cancer": "water", "scorpio": "water", "pisces": "water"}


def _f(v):
    return f"{v:.1f}"


def L(*pts):
    return smooth_open(list(pts))


def C(*pts):
    return smooth_closed(list(pts))


# ---------------------------------------------------------------- sky
def nebula(u, cx, cy, rx, ry, cols, seed, rot=0, op=0.42, n=230):
    """A soft painted nebula: stacked radial washes, cloudy brush strokes flowing along it, wisps and dark dust lanes."""
    rnd = random.Random(seed)
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for k, c in enumerate(cols):
        dx, dy = rnd.uniform(-rx * 0.3, rx * 0.3), rnd.uniform(-ry * 0.3, ry * 0.3)
        out.append(defs(rg(f"{u}-n{k}", [(0, c, op), (0.45, c, op * 0.45), (1, c, 0)]))
                   + f'<ellipse cx="{_f(cx + dx)}" cy="{_f(cy + dy)}" rx="{_f(rx * rnd.uniform(0.7, 1))}" ry="{_f(ry * rnd.uniform(0.7, 1))}" '
                     f'fill="url(#{u}-n{k})" transform="rotate({rot} {_f(cx)} {_f(cy)})"/>')
    ph = rnd.uniform(0, 6)
    g = []
    for i in range(n):
        lx, ly = rnd.gauss(0, rx * 0.42), rnd.gauss(0, ry * 0.4)
        x, y = cx + lx * ca - ly * sa, cy + lx * sa + ly * ca
        a = rot + 22 * math.sin(lx / rx * 3 + ph) + rnd.uniform(-8, 8)
        fall = math.exp(-((lx / rx) ** 2 + (ly / ry) ** 2) * 1.4)
        col = rnd.choice(cols + [CREAM] if i % 7 == 0 else cols)
        g.append(dabs([col], rnd.randrange(9999), (x, y, x + 0.1, y + 0.1), 1, a, (50, 130), (9, 22), (0.02 + 0.07 * fall, 0.04 + 0.11 * fall), 0.18, 4))
    for i in range(3):
        lx, ly = rnd.gauss(0, rx * 0.3), rnd.gauss(0, ry * 0.2)
        x, y = cx + lx * ca - ly * sa, cy + lx * sa + ly * ca
        g.append(dabs([NAVY], rnd.randrange(9999), (x, y, x + 0.1, y + 0.1), 1, rot + rnd.uniform(-15, 15), (80, 150), (6, 12), (0.12, 0.2), 0.2, 4))
    out.append("".join(g))
    return "".join(out)


def dust_band(u, x0, y0, x1, y1, width, seed, n=320, col=STARC, op=0.5):
    """Milky-way band: a hazy wash plus hundreds of tiny star grains scattered along a line."""
    rnd = random.Random(seed)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    length = math.hypot(x1 - x0, y1 - y0)
    out = [defs(rg(f"{u}-db", [(0, "#C9C4F0", 0.16), (0.6, "#9A94D8", 0.06), (1, "#9A94D8", 0)]))
           + f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(length / 2)}" ry="{_f(width)}" fill="url(#{u}-db)" transform="rotate({ang:.1f} {_f(cx)} {_f(cy)})"/>']
    g = []
    for _ in range(n):
        t = rnd.uniform(0, 1)
        off = rnd.gauss(0, width * 0.45)
        nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        x = x0 + (x1 - x0) * t + nx * off
        y = y0 + (y1 - y0) * t + ny * off
        g.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(0.4, 1.3):.2f}" opacity="{rnd.uniform(0.2, 0.8):.2f}"/>')
    out.append(f'<g fill="{col}" opacity="{op}">' + "".join(g) + "</g>")
    return "".join(out)


def field_stars(u, seed, n, box=(0, 0, 600, 600), keep=None, big=6, col=STARC, glow_c=GOLD_L, r=(0.5, 1.9)):
    """Stars of many sizes: tiny grains, mid dabs with soft glows, and a few big four-point twinkles."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [defs(rg(f"{u}-sg", [(0, glow_c, 0.55), (0.35, glow_c, 0.18), (1, glow_c, 0)]))]
    k = tries = 0
    while k < n and tries < n * 10:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        k += 1
        rr = rnd.uniform(*r) * (1.6 if rnd.random() < 0.12 else 1)
        if rr > 1.5:
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(rr * 5)}" fill="url(#{u}-sg)"/>')
        out.append(f'<path d="{blob(x, y, rr, rr * rnd.uniform(0.75, 1), rnd.randrange(999), 0.2, 6)}" fill="{col}" opacity="{rnd.uniform(0.45, 1):.2f}"/>')
    k = 0
    while k < big and tries < n * 20:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        k += 1
        s = rnd.uniform(6, 11)
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(s * 2.4)}" fill="url(#{u}-sg)"/>' + spark(x, y, s, col, rnd.uniform(0.8, 1)))
    return "".join(out)


def spark(x, y, r, col, op=1.0, thin=0.16, rot=0):
    """Four-point star with concave sides (like a painted twinkle)."""
    pts = []
    for i in range(4):
        a = math.radians(rot - 90 + 90 * i)
        b = math.radians(rot - 45 + 90 * i)
        pts.append(f"{_f(x + r * math.cos(a))} {_f(y + r * math.sin(a))}")
        pts.append(f"{_f(x + r * thin * math.cos(b))} {_f(y + r * thin * math.sin(b))}")
    d = f"M {pts[0]} Q {pts[1]} {pts[2]} Q {pts[3]} {pts[4]} Q {pts[5]} {pts[6]} Q {pts[7]} {pts[0]} Z"
    return f'<path d="{d}" fill="{col}" opacity="{op:.2f}"/>'


def sky(u, seed, el, nebulae=(), band=None, n_stars=110, keep=None, text_shade=True, stops=None):
    E = ELEMENTS[el]
    out = [defs(lg(f"{u}-sky", stops or E["sky"])), f'<rect width="600" height="600" fill="url(#{u}-sky)"/>',
           dabs(E["tint"], seed, (-80, -10, 610, 610), 300, -6, (50, 150), (4, 11), (0.12, 0.32), 0.12, 8)]
    for i, (cx, cy, rx, ry, rot) in enumerate(nebulae):
        out.append(nebula(f"{u}-nb{i}", cx, cy, rx, ry, E["neb"][i % 3:] + E["neb"][:i % 3], seed + 11 * i, rot))
    if band:
        out.append(dust_band(f"{u}-band", *band, seed + 5))
    out.append(field_stars(f"{u}-fs", seed + 7, n_stars, keep=keep))
    if text_shade:
        out.append(defs(lg(f"{u}-ts", [(0, NAVY, 0), (0.45, NAVY, 0.55), (1, NAVY, 0.8)])) + f'<rect y="390" width="600" height="210" fill="url(#{u}-ts)"/>')
    return "".join(out)


def finish(u, seed=9):
    """Vignette and paper grain over everything."""
    return (defs(rg(f"{u}-vg", [(0, "#000000", 0), (0.7, "#000000", 0), (1, "#02020C", 0.55)], r=0.75))
            + f'<rect width="600" height="600" fill="url(#{u}-vg)"/>' + grain_over(f"{u}-gr", seed, "#05040E", "#FFFFFF", 1.0))


# ---------------------------------------------------------------- constellation pieces
def figure(u, strokes, seed, col=GOLD, w=2.3, op=0.62, fills=(), fill_op=0.1):
    """Delicate gold-ink figure behind the stars: faint gold wash in closed shapes and hand-inked lines."""
    out = []
    for d in fills:
        out.append(f'<path d="{d}" fill="{col}" opacity="{fill_op}"/>')
    g = []
    for i, s in enumerate(strokes):
        if isinstance(s, tuple):
            d, ww = s
        else:
            d, ww = s, w
        g.append(ink(d, col, ww, seed + i, 2, op))
    out.append("".join(g))
    return "".join(out)


def constellation(u, lines, stars, bright, col=GOLD, star_col=STARC, lw=2.4):
    """Gold constellation lines (drawn twice: a soft wide glow and a crisp line) and glowing stars."""
    out = [defs(rg(f"{u}-cg", [(0, GOLD_L, 0.75), (0.3, GOLD, 0.3), (1, GOLD, 0)]))]
    poly = "".join(f'<path d="M {" L ".join(f"{_f(x)} {_f(y)}" for x, y in ln)}"/>' for ln in lines)
    out.append(f'<g fill="none" stroke="{GOLD_L}" stroke-width="{lw * 3.2:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.12">{poly}</g>')
    out.append(f'<g fill="none" stroke="{col}" stroke-width="{lw}" stroke-linecap="round" stroke-linejoin="round" opacity="0.92">{poly}</g>')
    for i, (x, y, r) in enumerate(stars):
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 4.2)}" fill="url(#{u}-cg)"/>')
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r + 1.4)}" fill="{GOLD}" opacity="0.9"/>')
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}" fill="{star_col}"/>')
    bx, by = bright
    out.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="30" fill="url(#{u}-cg)"/>')
    out.append(spark(bx, by, 24, STARC, 0.95, 0.14))
    out.append(spark(bx, by, 12, GOLD_L, 0.9, 0.2, 45))
    out.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="4.5" fill="#FFFFFF"/>')
    return "".join(out)


# ---------------------------------------------------------------- zodiac glyphs (unit box, stroked)
GLYPH = {
    "aries": ["M 0 0.85 L 0 -0.15 C 0 -0.65 -0.25 -0.85 -0.5 -0.85 C -0.78 -0.85 -0.92 -0.6 -0.86 -0.38 C -0.8 -0.2 -0.62 -0.14 -0.52 -0.22",
              "M 0 -0.15 C 0 -0.65 0.25 -0.85 0.5 -0.85 C 0.78 -0.85 0.92 -0.6 0.86 -0.38 C 0.8 -0.2 0.62 -0.14 0.52 -0.22"],
    "taurus": ["M 0 0.92 A 0.44 0.44 0 1 1 0.001 0.92",
               "M -0.82 -0.82 C -0.72 -0.44 -0.42 -0.08 0 -0.08 C 0.42 -0.08 0.72 -0.44 0.82 -0.82"],
    "gemini": ["M -0.72 -0.82 Q 0 -0.56 0.72 -0.82", "M -0.72 0.82 Q 0 0.56 0.72 0.82", "M -0.34 -0.68 L -0.34 0.68", "M 0.34 -0.68 L 0.34 0.68"],
    "cancer": ["M -0.82 -0.18 A 0.27 0.27 0 1 1 -0.28 -0.2 M -0.82 -0.2 C -0.7 -0.62 -0.3 -0.8 0.12 -0.76 C 0.46 -0.73 0.72 -0.58 0.88 -0.4",
               "M 0.82 0.18 A 0.27 0.27 0 1 1 0.28 0.2 M 0.82 0.2 C 0.7 0.62 0.3 0.8 -0.12 0.76 C -0.46 0.73 -0.72 0.58 -0.88 0.4"],
    "leo": ["M -0.36 0.5 A 0.26 0.26 0 1 1 -0.36 0.49 M -0.12 0.38 C -0.32 0.02 -0.34 -0.44 -0.06 -0.7 C 0.2 -0.92 0.62 -0.82 0.66 -0.44 "
            "C 0.7 -0.08 0.34 0.2 0.32 0.5 C 0.3 0.78 0.56 0.92 0.82 0.72"],
    "virgo": ["M -0.88 -0.56 C -0.72 -0.66 -0.6 -0.56 -0.6 -0.4 L -0.6 0.66",
              "M -0.6 -0.32 C -0.6 -0.66 -0.2 -0.66 -0.2 -0.36 L -0.2 0.66",
              "M -0.2 -0.32 C -0.2 -0.66 0.2 -0.66 0.2 -0.36 L 0.2 0.5 C 0.2 0.84 0.56 0.92 0.7 0.62 C 0.82 0.36 0.68 0.02 0.46 0.04 "
              "C 0.24 0.06 0.2 0.32 0.32 0.54 C 0.4 0.7 0.5 0.82 0.56 0.9"],
    "libra": ["M -0.86 0.62 L 0.86 0.62",
              "M -0.86 0.2 L -0.36 0.2 C -0.5 0.02 -0.52 -0.2 -0.4 -0.38 C -0.28 -0.58 -0.12 -0.66 0 -0.66 C 0.12 -0.66 0.28 -0.58 0.4 -0.38 "
              "C 0.52 -0.2 0.5 0.02 0.36 0.2 L 0.86 0.2"],
    "scorpio": ["M -0.9 -0.56 C -0.74 -0.66 -0.62 -0.56 -0.62 -0.4 L -0.62 0.66",
                "M -0.62 -0.32 C -0.62 -0.66 -0.24 -0.66 -0.24 -0.36 L -0.24 0.66",
                "M -0.24 -0.32 C -0.24 -0.66 0.14 -0.66 0.14 -0.36 L 0.14 0.5 C 0.14 0.72 0.3 0.78 0.5 0.72 L 0.78 0.6",
                "M 0.56 0.44 L 0.8 0.6 L 0.58 0.84"],
    "sagittarius": ["M -0.78 0.78 L 0.76 -0.76", "M 0.14 -0.78 L 0.78 -0.78 L 0.78 -0.14", "M -0.5 -0.06 L 0.06 0.5"],
    "capricorn": ["M -0.92 -0.62 C -0.78 -0.68 -0.66 -0.6 -0.6 -0.46 L -0.3 0.42 L -0.06 -0.44 C 0.04 -0.74 0.4 -0.72 0.36 -0.34 "
                  "L 0.26 0.4 C 0.24 0.66 0.44 0.82 0.64 0.72 C 0.86 0.6 0.86 0.3 0.66 0.22 C 0.44 0.14 0.24 0.3 0.24 0.54 "
                  "C 0.22 0.8 0.0 0.9 -0.22 0.84"],
    "aquarius": ["M -0.88 -0.12 L -0.58 -0.42 L -0.28 -0.12 L 0.02 -0.42 L 0.32 -0.12 L 0.62 -0.42 L 0.88 -0.16",
                 "M -0.88 0.42 L -0.58 0.12 L -0.28 0.42 L 0.02 0.12 L 0.32 0.42 L 0.62 0.12 L 0.88 0.38"],
    "pisces": ["M -0.62 -0.86 C -0.2 -0.5 -0.2 0.5 -0.62 0.86", "M 0.62 -0.86 C 0.2 -0.5 0.2 0.5 0.62 0.86", "M -0.62 0 L 0.62 0"],
}


def glyph_d(sign, cx, cy, s):
    """Scale a unit-box glyph path to (cx, cy) with half-size s."""
    out = []
    for d in GLYPH[sign]:
        toks = d.replace(",", " ").split()
        res, i, cmd, nums = [], 0, None, []
        for t in toks:
            if t.isalpha():
                res.append(t)
                cmd = t
                nums = []
                continue
            v = float(t)
            if cmd == "A":
                nums.append(v)
                k = len(nums) % 7
                if k in (1, 2):
                    res.append(_f(v * s))
                elif k in (3, 4, 5):
                    res.append(f"{v:g}")
                elif k == 6:
                    res.append(_f(cx + v * s))
                else:
                    res.append(_f(cy + v * s))
            else:
                nums.append(v)
                res.append(_f(cx + v * s) if len(nums) % 2 == 1 else _f(cy + v * s))
        out.append(" ".join(res))
    return out


def gilded(u, ds, w, seed, light=(-1, -1), dark_line=INKN, shadow=True):
    """Gilded stroke lettering: dark under-stroke, a gold gradient body, a pale highlight, sparkle dabs."""
    out = [defs(lg(f"{u}-gg", [(0, "#FFF0C0"), (0.35, "#F2CF78"), (0.62, "#D9A84A"), (1, "#A8752E")], 0, 0, 0.4, 1))]
    if shadow:
        out.append(f'<g fill="none" stroke="#02020A" stroke-width="{w + 6:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.45" '
                   f'transform="translate({w * 0.22:.1f} {w * 0.28:.1f})">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(f'<g fill="none" stroke="{GOLD_DD}" stroke-width="{w + 4:.1f}" stroke-linecap="round" stroke-linejoin="round">'
               + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(f'<g fill="none" stroke="url(#{u}-gg)" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round">'
               + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(f'<g fill="none" stroke="#FFF7DA" stroke-width="{max(1.2, w * 0.2):.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.75" '
               f'transform="translate({light[0] * w * 0.2:.1f} {light[1] * w * 0.2:.1f})">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    return "".join(out)


# ---------------------------------------------------------------- the twelve constellations
# lines, stars (x, y, r), the brightest star, and the gold figure (strokes, closed fills)
def ram_horn(cx, cy, r0, w0, a0=-120, turns=1.2, flip=1):
    """Curled ram horn: outer and inner edges of a tapering spiral plus ridge lines."""
    outer, inner, ridges = [], [], []
    n = 30
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + flip * 360 * turns * t)
        r = r0 * (1 - 0.7 * t)
        w = w0 * (1 - 0.72 * t)
        outer.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        inner.append((cx + (r - w) * math.cos(a), cy + (r - w) * math.sin(a)))
        if 0 < i < n - 3 and i % 3 == 0:
            ridges.append(L(outer[-1], ((outer[-1][0] + inner[-1][0]) / 2 + math.cos(a + 1.2) * 1.5, (outer[-1][1] + inner[-1][1]) / 2), inner[-1]))
    shape = smooth_closed(outer + inner[::-1])
    return shape, ridges


def fig_aries():
    # scalloped fleece: bumps around an ellipse
    cx, cy, rx, ry = 352, 264, 106, 56
    n = 16
    pts = []
    for i in range(n * 4 + 1):
        a = math.pi * 2 * i / (n * 4)
        bump = 1 + 0.08 * abs(math.sin(a * n / 2))
        pts.append((cx + rx * bump * math.cos(a), cy + ry * bump * math.sin(a)))
    fleece = smooth_closed(pts)
    curls = [L((cx + dx - 8, cy + dy), (cx + dx, cy + dy - 7), (cx + dx + 8, cy + dy)) for dx, dy in
             ((-50, -22), (-10, -32), (32, -26), (70, -12), (-30, 8), (12, 2), (52, 14), (-4, 34), (38, 38), (-56, 30))]
    head = C((226, 204), (204, 196), (182, 204), (160, 222), (140, 246), (136, 262), (148, 274), (170, 276), (196, 270), (224, 276), (246, 262), (248, 230))
    horn, ridges = ram_horn(214, 222, 36, 15, -125, 1.15)
    neck = L((246, 262), (262, 296), (290, 312))
    legs = [L((284, 310), (280, 345), (282, 378)), L((310, 316), (310, 348), (314, 380)), L((398, 314), (402, 346), (398, 378)),
            L((424, 308), (430, 342), (430, 376))]
    hooves = [L((x - 7, y), (x + 7, y)) for x, y in ((282, 380), (314, 382), (398, 380), (430, 378))]
    tail = L((456, 246), (472, 252), (474, 268), (464, 274))
    eye = "M 162 236 q 6 -4 12 0"
    nose = L((140, 258), (146, 262), (142, 268))
    return ([(fleece, 2.4), head, (horn, 2.6), *ridges, neck, *curls, *legs, *hooves, tail, eye, nose], [fleece, head, horn])


def fig_taurus():
    face = C((250, 204), (256, 262), (266, 316), (258, 346), (278, 364), (300, 368), (322, 364), (342, 346), (334, 316), (344, 262), (350, 204), (300, 190))
    hornL = C((256, 200), (214, 190), (176, 160), (160, 112), (172, 130), (200, 162), (240, 180), (262, 186))
    hornR = C((344, 200), (386, 190), (424, 160), (440, 112), (428, 130), (400, 162), (360, 180), (338, 186))
    earL = C((252, 222), (222, 214), (196, 226), (220, 242), (254, 244))
    earR = C((348, 222), (378, 214), (404, 226), (380, 242), (346, 244))
    tuft = [L((276, 196), (284, 214), (278, 230)), L((298, 192), (302, 214), (296, 232)), L((320, 196), (316, 214), (324, 228))]
    nost = [L((282, 344), (288, 338), (292, 346)), L((318, 344), (312, 338), (308, 346))]
    neck = [L((236, 246), (206, 300), (186, 388)), L((364, 246), (394, 300), (414, 388))]
    eyes = ["M 262 254 q 7 -5 14 0", "M 324 254 q 7 -5 14 0"]
    return ([face, hornL, hornR, earL, earR, *tuft, *nost, *neck, *eyes], [face, hornL, hornR])


def fig_gemini():
    out, fills = [], []
    for hx, sgn in ((246, -1), (354, 1)):
        head = blob(hx, 136, 20, 23, int(hx), 0.03, 14)
        hair = [L((hx - 20, 130), (hx - 12, 112), (hx + 6, 110), (hx + 20, 122)), L((hx - 14, 116), (hx - 4, 106), (hx + 12, 112))]
        neck = L((hx - 6, 158), (hx - 6, 168))
        robe = C((hx - 34, 178), (hx - 40, 230), (hx - 46, 300), (hx - 54, 338), (hx, 344), (hx + 54, 338), (hx + 46, 300), (hx + 40, 230), (hx + 34, 178), (hx, 168))
        folds = [L((hx - 18, 220), (hx - 22, 280), (hx - 28, 336)), L((hx + 6, 214), (hx + 8, 280), (hx + 10, 340)), L((hx + 24, 240), (hx + 30, 290), (hx + 34, 336))]
        legs = [L((hx - 18, 344), (hx - 22, 378)), L((hx + 18, 344), (hx + 22, 378))]
        outer = L((hx + sgn * 34, 182), (hx + sgn * 52, 228), (hx + sgn * 56, 272), (hx + sgn * 50, 290))
        belt = L((hx - 40, 236), (hx, 244), (hx + 40, 236))
        collar = L((hx - 20, 172), (hx, 186), (hx + 20, 172))
        hem = L((hx - 50, 326), (hx - 20, 332), (hx + 10, 328), (hx + 48, 330))
        curls = [blob(hx + dx, 122 + dy, 5, 5, int(hx + dx), 0.15, 8) for dx, dy in ((-16, 2), (-8, -8), (4, -11), (15, -4))]
        out += [head, *hair, *curls, neck, robe, *folds, *legs, outer, belt, collar, hem]
        fills += [head, robe]
    arms = L((280, 186), (292, 210), (300, 222), (308, 210), (320, 186))
    clasp = blob(300, 224, 8, 6, 3, 0.1, 8)
    star_staff = L((196, 290), (190, 232), (182, 190))
    return (out + [arms, clasp], fills)


def fig_cancer():
    shell = C((236, 250), (248, 214), (300, 198), (352, 214), (364, 250), (350, 290), (300, 306), (250, 290))
    ridge = [L((256, 238), (300, 226), (344, 238)), L((262, 268), (300, 280), (338, 268))]
    eyes = [L((282, 204), (276, 182)), L((318, 204), (324, 182))]
    eyeb = [blob(276, 178, 5, 5, 1, 0.1, 8), blob(324, 178, 5, 5, 2, 0.1, 8)]
    out = [shell, *ridge, *eyes, *eyeb]
    for s in (-1, 1):
        arm = L((300 + s * 52, 222), (300 + s * 92, 196), (300 + s * 116, 160))
        arm2 = L((300 + s * 56, 232), (300 + s * 96, 206), (300 + s * 120, 172))
        out += [arm, arm2, *pincer(300 + s * 124, 150, -90 + s * 30, 44)]
        for k in range(4):
            y0 = 246 + k * 14
            out.append(L((300 + s * 62, y0), (300 + s * (108 + k * 6), y0 - 14 + k * 8), (300 + s * (132 + k * 4), y0 + 30 + k * 8)))
    return (out, [shell])


def fig_leo():
    mane_pts = []
    cx, cy = 222, 198
    for i in range(40):
        a = 2 * math.pi * i / 40
        rr = 62 + (10 if i % 2 else 0)
        mane_pts.append((cx + rr * math.cos(a), cy + rr * 0.95 * math.sin(a)))
    mane = smooth_closed(mane_pts)
    face = C((206, 160), (176, 170), (150, 194), (142, 214), (156, 230), (184, 236), (212, 232), (230, 210), (228, 180))
    back = L((272, 166), (330, 178), (400, 196), (452, 214), (474, 246), (470, 290), (476, 330), (494, 344))
    belly = L((262, 300), (330, 318), (412, 318), (448, 312))
    hind = L((448, 312), (440, 334), (452, 346), (494, 346))
    fore = [L((248, 252), (240, 300), (206, 336), (150, 340), (138, 352), (170, 356), (226, 352), (268, 330), (288, 316)),
            L((282, 268), (276, 316), (250, 346))]
    tail = L((470, 236), (498, 242), (516, 270), (512, 304), (520, 318))
    tuft = blob(518, 322, 7, 10, 4, 0.2, 8, rot=20)
    eye = "M 176 196 q 6 -4 12 0"
    nose = L((146, 210), (152, 216), (146, 222))
    mouth = L((152, 226), (164, 230), (176, 226))
    return ([(mane, 2.2), face, back, belly, hind, *fore, tail, tuft, eye, nose, mouth], [mane, face])


def wheat_ear(x0, y0, x1, y1, n=6, size=11):
    """Wheat ear along a stalk segment: paired grains pointing to the tip, plus awns."""
    ang = math.atan2(y1 - y0, x1 - x0)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    out = []
    for i in range(n):
        t = i / (n - 1)
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        sz = size * (1 - 0.35 * t)
        for sg in (-1, 1):
            tip = (bx + dx * sz * 1.1 + nx * sg * sz * 0.7, by + dy * sz * 1.1 + ny * sg * sz * 0.7)
            out.append(C((bx, by), (bx + dx * sz * 0.4 + nx * sg * sz * 0.55, by + dy * sz * 0.4 + ny * sg * sz * 0.55), tip,
                         (bx + dx * sz * 0.7 + nx * sg * sz * 0.1, by + dy * sz * 0.7 + ny * sg * sz * 0.1)))
            out.append(L(tip, (tip[0] + dx * sz * 1.2 + nx * sg * sz * 0.5, tip[1] + dy * sz * 1.2 + ny * sg * sz * 0.5)))
    return out


def fig_virgo():
    head = C((236, 110), (254, 114), (262, 126), (268, 138), (262, 142), (264, 148), (258, 157), (244, 162), (228, 156), (218, 140), (222, 122))
    bun = blob(214, 120, 13, 12, 7, 0.08, 10)
    hair = [L((222, 132), (206, 164), (200, 204), (190, 244), (198, 276)), L((218, 146), (214, 190), (206, 232), (212, 258)),
            L((232, 112), (222, 124), (224, 140))]
    circlet = [blob(x, y, 2.6, 2.6, int(x), 0.1, 6) for x, y in ((232, 112), (242, 111), (251, 114))]
    eye = "M 252 132 q 4 -2 7 1"
    neck = [L((238, 162), (236, 182)), L((252, 160), (256, 178))]
    gown = C((226, 186), (214, 250), (206, 320), (220, 384), (330, 394), (440, 384), (360, 350), (312, 300), (288, 240), (272, 188), (250, 180))
    folds = [L((238, 214), (236, 290), (254, 386)), L((264, 228), (282, 310), (318, 390)), L((300, 290), (340, 346), (390, 386)),
             L((226, 300), (240, 340), (232, 388))]
    sash = L((218, 236), (250, 246), (288, 240))
    arm = [L((268, 192), (294, 232), (330, 262)), L((262, 206), (286, 240), (326, 270))]
    hand = blob(334, 266, 8, 7, 3, 0.1, 8)
    stalk = L((312, 236), (350, 278), (392, 322))
    ear = wheat_ear(372, 300, 402, 334, 5, 10)
    return ([head, bun, *hair, *circlet, eye, *neck, gown, *folds, sash, *arm, hand, stalk, *ear], [head, bun, gown])


def fig_libra():
    post = C((294, 148), (306, 148), (308, 350), (292, 350))
    base = C((252, 378), (266, 356), (334, 356), (348, 378))
    beam = L((166, 172), (230, 166), (300, 160), (370, 166), (434, 172))
    finial = blob(300, 136, 11, 11, 4, 0.04, 12)
    out = [post, base, (beam, 3.0), finial]
    fills = [base, post]
    for bx in (166, 434):
        out.append(blob(bx, 172, 5, 5, bx, 0.1, 8))
        out += [L((bx, 174), (bx - 44, 296)), L((bx, 174), (bx, 296)), L((bx, 174), (bx + 44, 296))]
        pan = C((bx - 54, 296), (bx + 54, 296), (bx + 36, 318), (bx, 326), (bx - 36, 318))
        out.append(pan)
        fills.append(pan)
    return (out, fills)


def pincer(cx, cy, ang, s):
    """Crab / scorpion claw: a swollen hand and two curved jaws, pointing at ang degrees."""
    a = math.radians(ang)
    def T(x, y):
        return (cx + (x * math.cos(a) - y * math.sin(a)) * s, cy + (x * math.sin(a) + y * math.cos(a)) * s)
    hand = C(T(-0.3, 0), T(-0.05, -0.32), T(0.35, -0.3), T(0.5, 0), T(0.35, 0.3), T(-0.05, 0.3))
    top = C(T(0.4, -0.22), T(0.8, -0.42), T(1.15, -0.25), T(1.22, 0.02), T(1.0, -0.14), T(0.62, -0.08))
    bot = C(T(0.42, 0.18), T(0.78, 0.34), T(1.04, 0.22), T(0.86, 0.12), T(0.6, 0.08))
    return [hand, top, bot]


def fig_scorpio():
    ceph = C((176, 172), (196, 156), (222, 160), (236, 182), (226, 206), (198, 212), (180, 198))
    segs = []
    pts = [(236, 200), (262, 226), (284, 256), (298, 290), (304, 328), (324, 362), (366, 380), (404, 366), (420, 336), (414, 306)]
    for i, (x, y) in enumerate(pts):
        w = 22 - i * 1.6
        segs.append(blob(x, y, w * 0.85, w * 0.6, 50 + i, 0.05, 10,
                         rot=math.degrees(math.atan2(pts[min(i + 1, len(pts) - 1)][1] - y, pts[min(i + 1, len(pts) - 1)][0] - x + 0.01))))
    sting = L((414, 300), (404, 280), (386, 276))
    out = [ceph, *segs, (sting, 2.8)]
    for a in (-1, 1):
        pass
    clawU = [L((190, 160), (178, 138), (166, 124)), L((198, 162), (186, 140), (172, 128)), *pincer(160, 112, -120, 34)]
    clawL = [L((178, 192), (156, 204), (138, 212)), L((180, 200), (158, 212), (140, 220)), *pincer(124, 214, 175, 34)]
    legs = []
    for k in range(4):
        x0, y0 = 220 + k * 16, 196 + k * 18
        legs.append(L((x0, y0), (x0 + 30, y0 - 26), (x0 + 50, y0 - 18)))
        legs.append(L((x0 - 6, y0 + 10), (x0 - 34, y0 + 30), (x0 - 40, y0 + 52)))
    return (out + clawU + clawL + legs, [ceph] + segs)


def bow_geom():
    N = (172, 352)
    T = (452, 106)
    dx, dy = T[0] - N[0], T[1] - N[1]
    ln = math.hypot(dx, dy)
    d = (dx / ln, dy / ln)
    p = (-d[1], d[0])
    G = (N[0] + dx * 0.6, N[1] + dy * 0.6)
    t1 = (G[0] + 150 * p[0] - 30 * d[0], G[1] + 150 * p[1] - 30 * d[1])
    t2 = (G[0] - 150 * p[0] - 30 * d[0], G[1] - 150 * p[1] - 30 * d[1])
    nock = (G[0] - 92 * d[0], G[1] - 92 * d[1])
    return N, T, d, p, G, t1, t2, nock


def fig_sagittarius():
    N, T, d, p, G, t1, t2, nock = bow_geom()
    def at(base, a, b):
        return (base[0] + a * d[0] + b * p[0], base[1] + a * d[1] + b * p[1])
    limb = C(at(t2, 6, -4), at(G, 6, -122), at(G, 30, -66), at(G, 22, 0), at(G, 30, 66), at(G, 6, 122), at(t1, 6, 4),
             at(t1, 1, 0), at(G, 0, 116), at(G, 20, 64), at(G, 10, 0), at(G, 20, -64), at(G, 0, -116), at(t2, 1, 0))
    limb_out = limb
    limb_in = L(at(G, 25, -40), at(G, 16, 0), at(G, 25, 40))
    tips = [L(at(t2, 5, -4), at(t2, 18, -14), at(t2, 30, -12)), L(at(t1, 5, 4), at(t1, 18, 14), at(t1, 30, 12))]
    string = L(t2, nock, t1)
    shaft = L(nock, T)
    head = C(T, at(T, -26, 10), at(T, -18, 0), at(T, -26, -10))
    fl = [C(at(nock, 4, 0), at(nock, 14, -14), at(nock, 40, -14), at(nock, 34, 0)),
          C(at(nock, 4, 0), at(nock, 14, 14), at(nock, 40, 14), at(nock, 34, 0))]
    grip = C(at(G, -2, -16), at(G, 12, -16), at(G, 12, 16), at(G, -2, 16))
    return ([(limb_out, 2.6), limb_in, *tips, (string, 1.8), (shaft, 2.6), head, *fl, grip], [limb, limb, head])


def fig_capricorn():
    head = C((206, 150), (186, 148), (160, 162), (140, 184), (144, 198), (164, 200), (186, 192), (212, 186))
    horns = [L((206, 150), (220, 118), (246, 96), (276, 92), (296, 104)), L((212, 158), (230, 128), (256, 110), (286, 108), (300, 118))]
    ear = C((214, 166), (240, 168), (252, 182), (230, 182))
    beard = L((150, 198), (156, 222), (164, 230))
    neck = [L((212, 186), (222, 230), (236, 262)), L((226, 154), (262, 176), (300, 200))]
    leg1 = L((236, 262), (204, 280), (168, 290), (152, 310))
    leg2 = L((262, 272), (236, 304), (212, 320), (206, 344))
    tail = L((300, 200), (372, 216), (436, 246), (470, 290), (466, 336), (432, 364), (392, 362), (370, 340), (378, 316), (402, 312))
    under = L((262, 272), (320, 296), (380, 300), (420, 312))
    fin = C((402, 312), (430, 292), (462, 302), (440, 322), (468, 340), (430, 342), (402, 322))
    scales = [L((x - 10, y), (x, y + 8), (x + 10, y)) for x, y in ((330, 236), (362, 248), (394, 262), (346, 268), (378, 280), (420, 286), (442, 316))]
    eye = "M 176 172 q 6 -4 12 0"
    return ([head, *horns, ear, beard, *neck, leg1, leg2, tail, under, fin, *scales, eye], [head, fin])


def fig_aquarius():
    cx, cy, k, rot = 222, 196, 72, 58
    a = math.radians(rot)
    def T(x, y):
        return (cx + (x * math.cos(a) - y * math.sin(a)) * k, cy + (x * math.sin(a) + y * math.cos(a)) * k)
    urn = C(T(0.18, -0.95), T(0.2, -0.7), T(0.5, -0.45), T(0.6, -0.05), T(0.45, 0.45), T(0.16, 0.8), T(0.2, 0.96), T(-0.2, 0.96), T(-0.16, 0.8),
            T(-0.45, 0.45), T(-0.6, -0.05), T(-0.5, -0.45), T(-0.2, -0.7), T(-0.18, -0.95))
    lip = C(T(-0.3, -0.95), T(0.3, -0.95), T(0.28, -1.05), T(-0.28, -1.05))
    handles = [L(T(-0.2, -0.78), T(-0.55, -0.82), T(-0.62, -0.5), T(-0.5, -0.38)), L(T(0.2, -0.78), T(0.55, -0.82), T(0.62, -0.5), T(0.5, -0.38))]
    bands = [L(T(-0.5, -0.3), T(0, -0.24), T(0.5, -0.3)), L(T(-0.56, 0.08), T(0, 0.14), T(0.56, 0.08)), L(T(-0.44, 0.4), T(0, 0.46), T(0.44, 0.4))]
    zig = L(T(-0.5, -0.12), T(-0.3, -0.02), T(-0.1, -0.12), T(0.1, -0.02), T(0.3, -0.12), T(0.5, -0.02))
    mouth = T(0, -1.05)
    waves = []
    for j, off in enumerate((-14, 0, 14)):
        pts = []
        for i in range(13):
            t = i / 12
            x = mouth[0] + 8 + t * 168 + off * (1 - t * 0.4)
            y = mouth[1] + 4 + (t ** 1.5) * 240 + off * 0.3
            pts.append((x + 7 * math.sin(t * 9 + j * 1.3), y))
        waves.append(L(*pts))
    pool = [L((404, 384), (430, 376), (456, 384), (482, 376), (508, 384)), L((386, 396), (414, 390), (442, 396), (470, 390))]
    drops = [blob(x, y, 4, 5.5, x, 0.1, 8) for x, y in ((376, 352), (492, 352), (506, 330), (388, 324))]
    return ([urn, lip, *handles, *bands, zig, *waves, *pool, *drops], [urn, lip])


def fish(cx, cy, length, ang, seed):
    """A gold-ink fish outline (unit fish rotated to ang degrees)."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    def T(x, y):
        return (cx + (x * ca - y * sa) * length, cy + (x * sa + y * ca) * length)
    body_d = C(T(0.5, 0), T(0.3, -0.2), T(0, -0.24), T(-0.3, -0.14), T(-0.42, 0), T(-0.3, 0.14), T(0, 0.24), T(0.3, 0.2))
    tail_d = C(T(-0.4, 0), T(-0.62, -0.2), T(-0.56, 0), T(-0.62, 0.2))
    fin = C(T(0.02, -0.22), T(-0.08, -0.38), T(-0.18, -0.2))
    gill = L(T(0.28, -0.16), T(0.22, 0), T(0.28, 0.16))
    eye = blob(*T(0.38, -0.05), length * 0.025, length * 0.025, seed, 0.1, 8)
    sc = [L(T(x - 0.05, -0.08), T(x, 0), T(x - 0.05, 0.08)) for x in (0.12, 0.0, -0.12, -0.24)]
    return [body_d, tail_d, fin, gill, eye, *sc], [body_d, tail_d], T


def fig_pisces():
    a, fa, Ta = fish(232, 132, 150, -60, 1)
    b, fb, Tb = fish(430, 300, 150, 10, 2)
    k = (176, 362)
    cord1 = L(Ta(-0.6, 0), (196, 270), (184, 320), k)
    cord2 = L(Tb(-0.6, 0), (330, 330), (250, 350), k)
    knot = blob(176, 362, 8, 7, 9, 0.15, 8)
    return (a + b + [cord1, cord2, knot], fa + fb)


SIGNS = {
    # slug: name, english, dates, figure fn, lines, stars, bright, nebulae, band
    "aries": ("ARIES", "the Ram", "MAR 21 – APR 19", fig_aries,
              [[(440, 218), (236, 186), (196, 204), (176, 236)]],
              [(440, 218, 4), (236, 186, 6), (196, 204, 4.5), (176, 236, 3.5)], (236, 186),
              [(150, 150, 220, 130, -20), (470, 330, 200, 120, 30)], (40, 400, 560, 60, 40)),
    "taurus": ("TAURUS", "the Bull", "APR 20 – MAY 20", fig_taurus,
               [[(166, 114), (268, 252), (300, 302), (332, 252), (434, 114)], [(300, 302), (300, 350), (270, 392)], [(268, 252), (284, 270)]],
               [(166, 114, 5.5), (268, 252, 4), (284, 270, 3), (300, 302, 4), (434, 114, 4.5), (300, 350, 3.5), (270, 392, 3.5), (332, 252, 7),
                (452, 316, 2.6), (462, 306, 2.2), (470, 318, 2.8), (458, 328, 2.2), (446, 324, 2), (474, 306, 1.8)], (332, 252),
               [(460, 140, 230, 130, 15), (130, 330, 200, 120, -25)], (60, 60, 560, 380, 40)),
    "gemini": ("GEMINI", "the Twins", "MAY 21 – JUN 20", fig_gemini,
               [[(246, 124), (240, 196), (232, 266), (226, 336), (210, 378)], [(354, 128), (360, 200), (366, 266), (376, 336), (392, 376)],
                [(240, 196), (196, 186)], [(360, 200), (404, 186)], [(232, 266), (300, 230), (366, 266)]],
               [(246, 124, 5.5), (354, 128, 7), (240, 196, 4), (232, 266, 4.5), (226, 336, 4), (210, 378, 4), (360, 200, 4), (366, 266, 4.5),
                (376, 336, 5), (392, 376, 4), (196, 186, 3.5), (404, 186, 3.5), (300, 230, 3)], (354, 128),
               [(140, 130, 210, 130, 25), (470, 300, 210, 130, -20)], (30, 260, 570, 120, 40)),
    "cancer": ("CANCER", "the Crab", "JUN 21 – JUL 22", fig_cancer,
               [[(284, 150), (296, 236), (306, 274), (348, 368)], [(306, 274), (230, 332)], [(296, 236), (420, 128)]],
               [(284, 150, 4.5), (296, 236, 4.5), (306, 274, 4.5), (348, 368, 6), (230, 332, 5.5), (420, 128, 3.5),
                (296, 254, 1.6), (304, 250, 1.4), (300, 260, 1.6), (292, 262, 1.2), (310, 258, 1.2)], (348, 368),
               [(150, 300, 220, 120, 20), (460, 150, 210, 130, -30)], (40, 120, 560, 420, 40)),
    "leo": ("LEO", "the Lion", "JUL 23 – AUG 22", fig_leo,
            [[(226, 302), (220, 256), (240, 214), (232, 174), (206, 154), (180, 166)], [(240, 214), (392, 198), (466, 236), (390, 258), (226, 302)],
             [(392, 198), (390, 258)]],
            [(226, 302, 7), (220, 256, 4), (240, 214, 5.5), (232, 174, 4), (206, 154, 4), (180, 166, 4), (392, 198, 4.5), (466, 236, 5.5),
             (390, 258, 4)], (226, 302),
            [(430, 140, 240, 130, -15), (120, 360, 180, 110, 20)], (60, 380, 560, 100, 40)),
    "virgo": ("VIRGO", "the Maiden", "AUG 23 – SEP 22", fig_virgo,
              [[(250, 150), (252, 204), (300, 240), (348, 270), (400, 326)], [(300, 240), (330, 206), (362, 168)], [(348, 270), (330, 330), (300, 372)],
               [(252, 204), (200, 240)]],
              [(250, 150, 4), (252, 204, 4.5), (300, 240, 5), (348, 270, 4.5), (400, 326, 7), (330, 206, 4), (362, 168, 4.5), (330, 330, 4),
               (300, 372, 3.5), (200, 240, 3.5)], (400, 326),
              [(450, 150, 220, 130, 20), (140, 340, 200, 120, -20)], (40, 300, 560, 100, 40)),
    "libra": ("LIBRA", "the Scales", "SEP 23 – OCT 22", fig_libra,
              [[(166, 174), (300, 134), (434, 174), (300, 238), (166, 174)], [(166, 174), (150, 306)], [(434, 174), (446, 310)]],
              [(166, 174, 5.5), (300, 134, 7), (434, 174, 5), (300, 238, 4), (150, 306, 4), (446, 310, 4)], (300, 134),
              [(300, 250, 260, 120, 0), (120, 120, 160, 100, 30)], (40, 120, 560, 300, 40)),
    "scorpio": ("SCORPIO", "the Scorpion", "OCT 23 – NOV 21", fig_scorpio,
                [[(150, 96), (196, 160), (130, 210)], [(196, 160), (240, 196), (264, 228), (286, 258), (298, 292), (304, 330), (324, 362),
                                                      (366, 380), (404, 366), (420, 336), (414, 306), (398, 282)]],
                [(150, 96, 4), (196, 160, 4.5), (130, 210, 4), (240, 196, 4), (264, 228, 7.5), (286, 258, 4), (298, 292, 4), (304, 330, 4),
                 (324, 362, 4.5), (366, 380, 4), (404, 366, 4.5), (420, 336, 4.5), (414, 306, 4), (398, 282, 5)], (264, 228),
                [(420, 170, 240, 140, -30), (150, 380, 200, 100, 10)], (60, 520, 540, 60, 40)),
    "sagittarius": ("SAGITTARIUS", "the Archer", "NOV 22 – DEC 21", fig_sagittarius,
                    [[(240, 150), (338, 222), (446, 112)], [(338, 222), (392, 334), (282, 312), (268, 256), (338, 222)], [(268, 256), (240, 150)],
                     [(268, 256), (206, 246), (214, 300), (282, 312)]],
                    [(240, 150, 4.5), (338, 222, 4.5), (446, 112, 4.5), (392, 334, 7), (282, 312, 4.5), (268, 256, 4), (206, 246, 5), (214, 300, 4)],
                    (392, 334),
                    [(170, 150, 220, 140, 30), (460, 300, 200, 140, -10)], (80, 560, 520, 40, 40)),
    "capricorn": ("CAPRICORN", "the Sea-Goat", "DEC 22 – JAN 19", fig_capricorn,
                  [[(186, 150), (204, 186), (240, 262), (292, 318), (362, 302), (456, 222), (424, 218), (332, 214), (204, 186)]],
                  [(186, 150, 4.5), (204, 186, 5), (240, 262, 4), (292, 318, 4), (362, 302, 4.5), (456, 222, 6.5), (424, 218, 4.5), (332, 214, 3.5)],
                  (456, 222),
                  [(130, 330, 220, 120, -15), (470, 120, 200, 120, 20)], (60, 80, 560, 440, 40)),
    "aquarius": ("AQUARIUS", "the Water-Bearer", "JAN 20 – FEB 18", fig_aquarius,
                 [[(150, 206), (236, 168), (296, 128), (318, 110)], [(296, 128), (334, 140)], [(236, 168), (330, 222), (370, 290), (402, 336), (448, 368)],
                  [(370, 290), (330, 330)]],
                 [(150, 206, 4.5), (236, 168, 6.5), (296, 128, 4), (318, 110, 3.5), (334, 140, 3.5), (330, 222, 4), (370, 290, 4.5), (402, 336, 4),
                  (448, 368, 4.5), (330, 330, 3.5)], (236, 168),
                 [(440, 160, 230, 130, -20), (140, 360, 200, 110, 15)], (40, 380, 560, 120, 40)),
    "pisces": ("PISCES", "the Fish", "FEB 19 – MAR 20", fig_pisces,
               [[(176, 362), (196, 296), (206, 226), (226, 166), (244, 118)], [(176, 362), (262, 344), (340, 322), (392, 306)],
                [(392, 306), (414, 286), (446, 284), (466, 300), (450, 320), (414, 322), (392, 306)]],
               [(176, 362, 6.5), (196, 296, 4), (206, 226, 4), (226, 166, 4), (244, 118, 4.5), (262, 344, 4), (340, 322, 4), (392, 306, 4),
                (414, 286, 3.5), (446, 284, 3.5), (466, 300, 3.5), (450, 320, 3.5), (414, 322, 3.5)], (176, 362),
               [(460, 140, 230, 140, 10), (140, 250, 180, 110, -30)], (60, 560, 540, 40, 40)),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def zodiac_constellation(slug, k):
    name, eng, dates, figfn, lines, st, bright, nebs, band = SIGNS[slug]
    el = SIGN_EL[slug]
    u = f"nsp-{slug}"
    strokes, fills = figfn()
    out = [sky(u, 100 + k * 13, el, nebs, band, 120)]
    out.append(figure(f"{u}-fg", strokes, 200 + k, fills=fills))
    out.append(constellation(f"{u}-cn", lines, st, bright))
    # type: brush-gold sign name, english name in italic, dates between two tiny glyphs
    size = fit_size(name, CINZEL, 70, 440, 8)
    out.append(bword(f"{u}-nm", 304, 462, name, CINZEL, size, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 300 + k, max_w=440, ls=8,
                     shadow="#05040E", sd=0.04, angle=-14))
    out.append(script(300, 500, eng, 30, CREAM, 360, ls=1))
    dsz = fit_size(dates, MONO, 19, 300, 3)
    dw = measure(dates, MONO, dsz, 3)
    out.append(f'<text x="{301.5:.1f}" y="535" text-anchor="middle" {MONO} font-size="{dsz}" letter-spacing="3" fill="{GOLD_L}">{esc(dates)}</text>')
    for sg in (-1, 1):
        gx = 300 + sg * (dw / 2 + 24)
        out.append(gilded(f"{u}-tg{sg + 1}", glyph_d(slug, gx, 529, 10), 2.4, 1, shadow=False))
    out.append(finish(u, 400 + k))
    return "".join(out)


for _k, _slug in enumerate(SIGNS):
    design(_slug)((lambda s, kk: (lambda: zodiac_constellation(s, kk)))(_slug, _k))


# ---------------------------------------------------------------- zodiac symbol medallions
TRAITS = {
    "aries": "BOLD · BRAVE · DRIVEN", "taurus": "STEADY · LOYAL · GROUNDED", "gemini": "CURIOUS · WITTY · BRIGHT",
    "cancer": "CARING · INTUITIVE · TENDER", "leo": "RADIANT · GENEROUS · CONFIDENT", "virgo": "KIND · THOUGHTFUL · PRECISE",
    "libra": "FAIR · GRACEFUL · CHARMING", "scorpio": "PASSIONATE · FEARLESS · TRUE", "sagittarius": "FREE · JOYFUL · ADVENTUROUS",
    "capricorn": "WISE · PATIENT · DETERMINED", "aquarius": "ORIGINAL · CLEVER · VISIONARY", "pisces": "DREAMY · GENTLE · CREATIVE",
}


def phase_d(cx, cy, r, f, lit_right=True):
    """Lit part of a moon at lit fraction f (0 new .. 1 full)."""
    if f >= 0.995:
        return blob(cx, cy, r, r, 1, 0.0, 24)
    rx = max(0.01, r * abs(1 - 2 * f))
    top, bot = f"{_f(cx)} {_f(cy - r)}", f"{_f(cx)} {_f(cy + r)}"
    if lit_right:
        return f"M {top} A {_f(r)} {_f(r)} 0 0 1 {bot} A {_f(rx)} {_f(r)} 0 0 {0 if f < 0.5 else 1} {top} Z"
    return f"M {top} A {_f(r)} {_f(r)} 0 0 0 {bot} A {_f(rx)} {_f(r)} 0 0 {1 if f < 0.5 else 0} {top} Z"


def little_moon(u, cx, cy, r, f, lit_right, seed, dark="#1A1E4A", lit=CREAM, edge=GOLD, glow_on=True):
    """A small painted moon in a given phase: dark disc with a gold rim, cream lit part with soft craters."""
    rnd = random.Random(seed)
    disc = blob(cx, cy, r, r, seed, 0.01, 20)
    out = []
    if glow_on:
        out.append(glow(f"{u}-g", cx, cy, r * 2.4, GOLD_L, 0.18 + 0.3 * f, 0.3))
    out.append(f'<path d="{disc}" fill="{dark}" opacity="0.92"/>')
    ld = phase_d(cx, cy, r, f, lit_right)
    inner = [defs(rg(f"{u}-l", [(0, "#FFFBEA"), (0.7, lit), (1, "#E8D6A8")], 0.42, 0.4, 0.62)), f'<path d="{ld}" fill="url(#{u}-l)"/>']
    for _ in range(3):
        a, dd = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.6) * r
        rr = r * rnd.uniform(0.1, 0.2)
        inner.append(f'<path d="{blob(cx + dd * math.cos(a), cy + dd * math.sin(a), rr, rr, rnd.randrange(999), 0.15, 8)}" fill="#C9B07A" opacity="0.35"/>')
    out.append(clip(f"{u}-c", ld) + f'<g clip-path="url(#{u}-c)">' + "".join(inner) + "</g>")
    out.append(ink(disc, edge, max(1.4, r * 0.09), seed, 1, 0.75))
    return "".join(out)


def moon_arc(u, cx, cy, R, seed, angles=(-150, -130, -110, -90, -70, -50, -30), sizes=None):
    fr = [0.18, 0.5, 0.78, 1.0, 0.78, 0.5, 0.18]
    out = []
    for i, a in enumerate(angles):
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        r = (sizes or [12, 12.5, 13, 17, 13, 12.5, 12])[i]
        out.append(little_moon(f"{u}-m{i}", x, y, r, fr[i], i < 3, seed + i))
    return "".join(out)


def leaf_d(x, y, ang, L_, w):
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    tip = (x + dx * L_, y + dy * L_)
    return C((x, y), (x + dx * L_ * 0.5 + nx * w, y + dy * L_ * 0.5 + ny * w), tip, (x + dx * L_ * 0.5 - nx * w, y + dy * L_ * 0.5 - ny * w))


def ornament(u, el, cx, cy, R, seed):
    """Element ornament around the medallion: fire rays, an earth laurel, an air orbit, water waves."""
    rnd = random.Random(seed)
    out = []
    if el == "fire":
        for i in range(36):
            a = math.radians(i * 10 + 5)
            if -158 < (i * 10 + 5 - 360 if i * 10 + 5 > 180 else i * 10 + 5) < -22:
                continue
            L_ = 26 if i % 2 else 14
            r0 = R + 6
            x0, y0 = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
            x1, y1 = cx + (r0 + L_) * math.cos(a), cy + (r0 + L_) * math.sin(a)
            nx, ny = -math.sin(a) * 4, math.cos(a) * 4
            out.append(f'<path d="M {_f(x0 + nx)} {_f(y0 + ny)} Q {_f((x0 + x1) / 2 + nx * 0.6)} {_f((y0 + y1) / 2 + ny * 0.6)} {_f(x1)} {_f(y1)} '
                       f'Q {_f((x0 + x1) / 2 - nx * 0.6)} {_f((y0 + y1) / 2 - ny * 0.6)} {_f(x0 - nx)} {_f(y0 - ny)} Z" fill="{GOLD if i % 2 else GOLD_L}" opacity="0.85"/>')
    elif el == "earth":
        for sg in (-1, 1):
            pts = []
            for i in range(15):
                a = math.radians(90 - sg * (12 + i * 9))
                pts.append((cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a)))
            out.append(ink(L(*pts), GOLD, 2.4, seed + sg, 1, 0.9))
            for i in range(1, 14):
                a = 90 - sg * (12 + i * 9)
                x, y = cx + (R + 12) * math.cos(math.radians(a)), cy + (R + 12) * math.sin(math.radians(a))
                tang = a - sg * 90
                for side in (-1, 1):
                    la = tang + side * 38 - sg * 0
                    d = leaf_d(x, y, la + (180 if sg > 0 else 0), 18 - i * 0.4, 5)
                    out.append(f'<path d="{d}" fill="{GOLD if (i + side) % 2 else "#D3AE5E"}" opacity="0.9"/>')
    elif el == "air":
        for rr, op in ((R + 10, 0.85), (R + 30, 0.5)):
            a0, a1 = math.radians(14), math.radians(166)
            out.append(f'<path d="M {_f(cx + rr * math.cos(a0))} {_f(cy + rr * math.sin(a0))} A {rr} {rr} 0 0 1 {_f(cx + rr * math.cos(a1))} {_f(cy + rr * math.sin(a1))}" '
                       f'fill="none" stroke="{GOLD}" stroke-width="1.8" opacity="{op}" stroke-dasharray="{"14 6 2 6" if rr > R + 20 else "none"}" stroke-linecap="round"/>')
        for i in range(11):
            a = math.radians(18 + i * 14.4)
            out.append(spark(cx + (R + 20) * math.cos(a), cy + (R + 20) * math.sin(a), 8 if i % 2 == 0 else 5, GOLD_L if i % 2 == 0 else GOLD, 0.95))
    else:  # water
        for row in range(3):
            pts = []
            rr = R + 12 + row * 11
            for i in range(97):
                a = math.radians(20 + row * 6 + i * (140 - row * 12) / 96)
                k = rr + 3.2 * math.sin(i * math.pi / 4 + row * 1.6)
                pts.append((cx + k * math.cos(a), cy + k * math.sin(a)))
            out.append(f'<path d="{L(*pts)}" fill="none" stroke="{GOLD if row != 1 else GOLD_L}" stroke-width="{2.2 - row * 0.3:.1f}" '
                       f'stroke-linecap="round" opacity="{0.9 - row * 0.22:.2f}"/>')
    return "".join(out)


def zodiac_symbol(sign, k):
    el = SIGN_EL[sign]
    u = f"nsg-{sign}"
    name, eng, dates = SIGNS[sign][0], SIGNS[sign][1], SIGNS[sign][2]
    cx, cy, R = 300, 262, 148
    E = ELEMENTS[el]
    nebs = [(140 + (k % 3) * 40, 120, 220, 120, -20 + k * 7), (460 - (k % 2) * 40, 420, 220, 120, 25 - k * 4)]
    out = [sky(u, 700 + k * 17, el, nebs, None, 90, keep=lambda x, y: math.hypot(x - cx, y - cy) > R + 30)]
    out.append(glow(f"{u}-hg", cx, cy, R * 1.55, E["neb"][0], 0.35, 0.5))
    out.append(ornament(f"{u}-or", el, cx, cy, R, 800 + k))
    # medallion disc
    disc = blob(cx, cy, R, R, 810 + k, 0.006, 40)
    out.append(f'<path d="{blob(cx + 5, cy + 8, R, R, 811 + k, 0.006, 40)}" fill="#02020A" opacity="0.45"/>')
    out.append(defs(rg(f"{u}-dg", [(0, E["tint"][3]), (0.65, E["tint"][2]), (1, NAVY)], 0.5, 0.45, 0.6)))
    inner = [f'<rect x="{cx - R}" y="{cy - R}" width="{2 * R}" height="{2 * R}" fill="url(#{u}-dg)"/>',
             dabs(E["tint"] + [E["neb"][0]], 820 + k, (cx - R, cy - R, cx + R, cy + R), 160, around(cx, cy), (30, 80), (4, 10), (0.1, 0.3), 0.1, 10),
             nebula(f"{u}-dn", cx + 30, cy - 40, R * 0.8, R * 0.45, E["neb"], 830 + k, -25, 0.3, 120)]
    # the sign's constellation, faint, behind the glyph
    lines, st = SIGNS[sign][4], SIGNS[sign][5]
    def T(p):
        return (cx + (p[0] - 300) * 0.6, cy + 6 + (p[1] - 245) * 0.6)
    poly = "".join(f'<path d="M {" L ".join(f"{_f(T(q)[0])} {_f(T(q)[1])}" for q in ln)}"/>' for ln in lines)
    inner.append(f'<g fill="none" stroke="{GOLD_L}" stroke-width="1.6" opacity="0.35" stroke-linejoin="round">{poly}</g>')
    inner.append("".join(f'<circle cx="{_f(T((x, y))[0])}" cy="{_f(T((x, y))[1])}" r="{_f(r * 0.55 + 0.6)}" fill="{STARC}" opacity="0.6"/>' for x, y, r in st))
    inner.append(field_stars(f"{u}-is", 840 + k, 40, (cx - R, cy - R, cx + R, cy + R), big=3))
    out.append(clip(f"{u}-dc", disc) + f'<g clip-path="url(#{u}-dc)">' + "".join(inner) + "</g>")
    # ring band with the dates on its lower arc
    band = blob(cx, cy, R, R, 812 + k, 0.004, 40)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 14}" fill="none" stroke="{NAVY}" stroke-width="28" opacity="0.72"/>')
    out.append(ink(band, GOLD, 3.2, 850 + k, 2, 0.95))
    out.append(ink(blob(cx, cy, R - 28, R - 28, 813 + k, 0.004, 40), GOLD, 2.0, 851 + k, 1, 0.85))
    for a in range(-60, 241, 15):
        if 30 <= a <= 150:
            continue
        x, y = cx + (R - 14) * math.cos(math.radians(a)), cy + (R - 14) * math.sin(math.radians(a))
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{2.6 if a % 45 == 0 else 1.6}" fill="{GOLD_L}" opacity="0.85"/>')
    out.append(arc_word(dates, cx, cy, R + 5, MONO, 17, GOLD_L, ls=2.5, uid=f"{u}-dt", top=False, dy=0))
    # moon phases riding the top of the medallion
    out.append(moon_arc(f"{u}-ma", cx, cy, R + 34, 860 + k))
    # the glyph, gilded
    out.append(glow(f"{u}-gl", cx, cy, 110, GOLD_L, 0.28, 0.35))
    out.append(gilded(f"{u}-gy", glyph_d(sign, cx, cy - 4, 74), 16, 870 + k))
    out.append(spark(cx + 74, cy - 70, 10, STARC, 0.95))
    out.append(spark(cx - 80, cy + 64, 7, GOLD_L, 0.85))
    # name and traits
    size = fit_size(name, CINZEL, 54, 440, 10)
    out.append(bword(f"{u}-nm", 305, 482, name, CINZEL, size, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 880 + k, max_w=440, ls=10,
                     shadow="#05040E", sd=0.04, angle=-14))
    tr = TRAITS[sign]
    tsz = fit_size(tr, JOST, 20, 430, 3)
    out.append(f'<text x="{301.5:.1f}" y="524" text-anchor="middle" {JOST} font-size="{tsz}" letter-spacing="3" fill="{CREAM}">{esc(tr)}</text>')
    out.append(finish(u, 890 + k))
    return "".join(out)


for _k, _slug in enumerate(SIGNS):
    design(f"{_slug}-symbol")((lambda s, kk: (lambda: zodiac_symbol(s, kk)))(_slug, _k))


# ---------------------------------------------------------------- celestial storybook pieces
def sea(u, horizon, seed, glit_x=300, glit_w=(10, 120), stops=None):
    """Calm night sea: graded water, horizontal brush strokes, and a moon-glitter path."""
    rnd = random.Random(seed)
    out = [defs(lg(f"{u}-sw", stops or [(0, "#2A3070"), (0.25, "#1A2050"), (1, "#080C24")])),
           f'<rect y="{horizon}" width="600" height="{600 - horizon}" fill="url(#{u}-sw)"/>',
           dabs(["#2E3A7A", "#141A44", "#3A4488", "#0E1234"], seed, (-40, horizon + 2, 620, 610), 160, 0, (30, 90), (1.5, 4), (0.25, 0.55), 0.05, 2)]
    g = []
    for i in range(70):
        t = (i / 70) ** 1.4
        y = horizon + 3 + t * (600 - horizon)
        w = glit_w[0] + (glit_w[1] - glit_w[0]) * t
        for _ in range(2):
            x = glit_x + rnd.gauss(0, w * 0.35)
            L_ = rnd.uniform(6, 18) * (0.5 + t)
            g.append(dab(x - L_ / 2, y, L_, rnd.uniform(0.8, 2.2), 0, rnd.choice([GOLD_L, CREAM, GOLD, "#FFFFFF"]), rnd.uniform(0.35, 0.9) * (1 - 0.5 * t), 0.05, rnd))
    out.append("".join(g))
    out.append(f'<path d="M 0 {horizon} L 600 {horizon}" stroke="#6A70B8" stroke-width="1.6" opacity="0.5"/>')
    return "".join(out)


@design("phases-of-the-moon")
def d_phases():
    u = "nsc-ph"
    cx, cy, R = 300, 420, 236
    angs = [-158 + 17 * i for i in range(9)]
    sizes = [17, 20, 23, 26, 34, 26, 23, 20, 17]
    fr = [0.04, 0.22, 0.5, 0.8, 1, 0.8, 0.5, 0.22, 0.04]
    out = [sky(u, 1001, "air", [(300, 190, 280, 130, 0), (90, 420, 160, 80, -20)], None, 130,
               keep=lambda x, y: y < 436, text_shade=False)]
    # far shore silhouettes at the horizon
    out.append(f'<path d="{L((-10, 444), (40, 432), (90, 428), (150, 436), (190, 444))} L 190 446 L -10 446 Z" fill="#141846"/>')
    out.append(f'<path d="{L((420, 444), (470, 430), (530, 426), (580, 434), (610, 440))} L 610 446 L 420 446 Z" fill="#141846"/>')
    out.append(sea(f"{u}-sea", 444, 1003))
    # dotted orbit through the moons
    a0, a1 = math.radians(angs[0]), math.radians(angs[-1])
    out.append(f'<path d="M {_f(cx + R * math.cos(a0))} {_f(cy + R * math.sin(a0))} A {R} {R} 0 0 1 {_f(cx + R * math.cos(a1))} {_f(cy + R * math.sin(a1))}" '
               f'fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="1 8" stroke-linecap="round" opacity="0.8"/>')
    for i, a in enumerate(angs):
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        if i == 4:
            out.append(pmoon(f"{u}-full", x, y, sizes[i], 1010, halo_r=2.4, halo_op=0.5))
        else:
            out.append(little_moon(f"{u}-m{i}", x, y, sizes[i], fr[i], i < 4, 1020 + i))
    # lettering cradled under the arc
    out.append(script(300, 300, "phases", 56, CREAM, 300, shadow="#05040E", sd=(2, 3)))
    out.append(label_rules(300, 336, "OF THE", MONO, 19, GOLD_L, 6, 1030))
    out.append(bword(f"{u}-mn", 306, 418, "MOON", CINZEL, 92, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 1031, max_w=330, ls=12,
                     shadow="#05040E", sd=0.035, angle=-14))
    out.append(finish(u, 1040))
    return "".join(out)


def label_rules(x, y, s, font, size, fill, ls, seed, gap=12, line_w=34):
    size = fit_size(s, font, size, 400, ls)
    w = measure(s, font, size, ls) - ls
    out = [f'<text x="{_f(x + ls / 2)}" y="{_f(y)}" text-anchor="middle" {font} font-size="{size}" letter-spacing="{ls}" fill="{fill}">{esc(s)}</text>']
    mid = y - size * 0.36
    for sg in (-1, 1):
        a = x + sg * (w / 2 + gap)
        b = a + sg * line_w
        out.append(brush_rule(min(a, b), max(a, b), mid, fill, seed + sg, 2.6, 0.85))
        out.append(spark(b + sg * 7, mid, 6, fill, 0.95))
    return "".join(out)


def dab(x, y, L_, w, a_deg, col, op, curve, rnd):
    a = math.radians(a_deg)
    dx, dy = L_ * math.cos(a), L_ * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    bend = L_ * curve * rnd.uniform(-1, 1)
    mx, my = x + dx / 2 + nx * bend, y + dy / 2 + ny * bend
    return (f'<path d="M {_f(x)} {_f(y)} Q {_f(mx + nx * w)} {_f(my + ny * w)} {_f(x + dx)} {_f(y + dy)} '
            f'Q {_f(mx - nx * w)} {_f(my - ny * w)} {_f(x)} {_f(y)} Z" fill="{col}" opacity="{op:.2f}"/>')


# ---------------------------------------------------------------- sun & moon
def sun_face(u, cx, cy, r, seed):
    out = []
    # flame rays and short rays, gilded
    out.append(defs(rg(f"{u}-rg", [(0, "#FFF1C0"), (0.5, "#F6CC66"), (1, "#D9962E")], 0.5, 0.5, 0.5)))
    rays = []
    for i in range(16):
        a = math.radians(i * 22.5 - 90)
        b0, b1 = a - math.radians(8), a + math.radians(8)
        r0, r1 = r + 2, r + 50 + (6 if i % 2 else 0)
        mid = a + math.radians(7 * (1 if i % 2 else -1))
        tip = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        p0 = (cx + r0 * math.cos(b0), cy + r0 * math.sin(b0))
        p1 = (cx + r0 * math.cos(b1), cy + r0 * math.sin(b1))
        m = (cx + (r0 + r1) / 2 * math.cos(mid), cy + (r0 + r1) / 2 * math.sin(mid))
        rays.append(C(p0, (m[0] + (p0[0] - p1[0]) * 0.18, m[1] + (p0[1] - p1[1]) * 0.18), tip, (m[0] - (p0[0] - p1[0]) * 0.18, m[1] - (p0[1] - p1[1]) * 0.18), p1))
        a2 = a + math.radians(11.25)
        sr = r + 30
        q0 = (cx + (r - 2) * math.cos(a2 - 0.09), cy + (r - 2) * math.sin(a2 - 0.09))
        q1 = (cx + (r - 2) * math.cos(a2 + 0.09), cy + (r - 2) * math.sin(a2 + 0.09))
        rays.append(f"M {_f(q0[0])} {_f(q0[1])} L {_f(cx + sr * math.cos(a2))} {_f(cy + sr * math.sin(a2))} L {_f(q1[0])} {_f(q1[1])} Z")
    out.append(f'<g fill="{GOLD_DD}" stroke="{GOLD_DD}" stroke-width="4" stroke-linejoin="round">' + "".join(f'<path d="{d}"/>' for d in rays) + "</g>")
    out.append(f'<g fill="url(#{u}-rg)">' + "".join(f'<path d="{d}" transform="translate(-0.5 -0.5)"/>' for d in rays) + "</g>")
    out.append(brush(f"{u}-rb", rays, (cx - r - 60, cy - r - 60, cx + r + 60, cy + r + 60), [GOLD_L, "#E9A93E", "#FFE7A0"], seed, 160,
                     angle=lambda x, y: math.degrees(math.atan2(y - cy, x - cx)), length=(10, 26), width=(1.2, 3), opacity=(0.25, 0.55), curve=0.1))
    disc = blob(cx, cy, r, r, seed, 0.012, 28)
    out.append(defs(rg(f"{u}-dg", [(0, "#FFF4CC"), (0.6, "#FAD77E"), (1, "#E9A93E")], 0.42, 0.4, 0.62)))
    out.append(f'<path d="{disc}" fill="url(#{u}-dg)"/>')
    out.append(brush(f"{u}-db", disc, (cx - r, cy - r, cx + r, cy + r), ["#FFF6D8", "#F2BE58", "#FFE7A0", "#E0A040"], seed + 1, 120,
                     angle=around(cx, cy), length=(12, 34), width=(1.5, 4), opacity=(0.2, 0.45), curve=0.15))
    out.append(ink(disc, "#A8661E", 3, seed + 2, 2, 0.85))
    fc = "#7A3E12"
    # serene face: closed eyes with lashes, brows, nose, smile, rosy cheeks
    for sg in (-1, 1):
        ex = cx + sg * r * 0.36
        ey = cy - r * 0.1
        out.append(ink(f"M {_f(ex - r * 0.16)} {_f(ey)} Q {_f(ex)} {_f(ey + r * 0.13)} {_f(ex + r * 0.16)} {_f(ey)}", fc, 3, seed + 3 + sg, 2, 0.9))
        for k in (-0.1, 0, 0.1):
            lx = ex + k * r
            out.append(ink(f"M {_f(lx)} {_f(ey + r * 0.07)} l {_f(k * r * 0.4)} {_f(r * 0.07)}", fc, 1.8, seed + 5, 1, 0.8))
        out.append(ink(f"M {_f(ex - r * 0.18)} {_f(ey - r * 0.18)} Q {_f(ex)} {_f(ey - r * 0.3)} {_f(ex + r * 0.18)} {_f(ey - r * 0.2)}", fc, 2.4, seed + 6 + sg, 1, 0.75))
        out.append(f'<path d="{blob(cx + sg * r * 0.48, cy + r * 0.22, r * 0.15, r * 0.1, seed + 7 + sg, 0.1, 10)}" fill="#F08A6A" opacity="0.45"/>')
    out.append(ink(f"M {_f(cx + r * 0.02)} {_f(cy - r * 0.08)} Q {_f(cx - r * 0.08)} {_f(cy + r * 0.12)} {_f(cx + r * 0.04)} {_f(cy + r * 0.16)}", fc, 2.4, seed + 8, 1, 0.8))
    out.append(ink(f"M {_f(cx - r * 0.2)} {_f(cy + r * 0.34)} Q {_f(cx)} {_f(cy + r * 0.5)} {_f(cx + r * 0.2)} {_f(cy + r * 0.34)}", fc, 3, seed + 9, 2, 0.9))
    return "".join(out)


def moon_face(u, seed, k=1.0, ox=0, oy=0):
    """Crescent moon whose inner edge is a profile face looking left."""
    P = lambda *pts: [(ox + x * k, oy + y * k) for x, y in pts]  # noqa: E731
    outer = P((330, 128), (392, 136), (446, 172), (478, 236), (474, 300), (444, 350), (392, 380), (332, 380))
    inner = P((332, 380), (372, 356), (388, 336), (378, 320), (390, 310), (384, 302), (392, 294), (388, 284), (366, 272), (388, 256),
              (398, 238), (392, 222), (400, 200), (388, 170), (330, 128))
    d = smooth_closed(outer + inner[1:-1])
    out = [glow(f"{u}-mg", ox + 420 * k, oy + 255 * k, 170 * k, "#BFC8FF", 0.3, 0.35)]
    out.append(defs(rg(f"{u}-cg", [(0, "#FFFBEE"), (0.55, "#EDE4CC"), (1, "#B8B0D8")], 0.35, 0.45, 0.75)))
    out.append(f'<path d="{d}" fill="url(#{u}-cg)"/>')
    out.append(brush(f"{u}-cb", d, (ox + 320 * k, oy + 120 * k, ox + 490 * k, oy + 390 * k), ["#FFFFFF", "#D8D0EC", "#F6EED8", "#B8AED6"], seed, 110,
                     angle=around(ox + 340 * k, oy + 255 * k), length=(12, 34), width=(1.5, 4), opacity=(0.2, 0.5), curve=0.15))
    rnd = random.Random(seed)
    cr = []
    for x, y, r in ((440, 200, 9), (456, 270, 7), (430, 334, 10), (420, 240, 5), (446, 312, 5)):
        cr.append(f'<path d="{blob(ox + x * k, oy + y * k, r * k, r * k, rnd.randrange(999), 0.12, 10)}" fill="#A8A0CC" opacity="0.4"/>')
    out.append(clip(f"{u}-cc", d) + f'<g clip-path="url(#{u}-cc)">' + "".join(cr)
               + f'<path d="{d}" fill="none" stroke="#8E86C0" stroke-width="{14 * k:.1f}" opacity="0.25" transform="translate({8 * k:.1f} 0)"/></g>')
    out.append(ink(d, "#4A4278", 2.8, seed + 1, 2, 0.85))
    fc = "#4A3A6A"
    ex, ey = ox + 412 * k, oy + 236 * k
    out.append(ink(f"M {_f(ex - 11 * k)} {_f(ey)} Q {_f(ex)} {_f(ey + 9 * k)} {_f(ex + 11 * k)} {_f(ey - 1 * k)}", fc, 2.6, seed + 2, 2, 0.9))
    for dx in (-6, 0, 6):
        out.append(ink(f"M {_f(ex + dx * k)} {_f(ey + 5 * k)} l {_f(dx * 0.4 * k)} {_f(6 * k)}", fc, 1.6, seed + 3, 1, 0.8))
    out.append(ink(f"M {_f(ex - 12 * k)} {_f(ey - 14 * k)} Q {_f(ex)} {_f(ey - 22 * k)} {_f(ex + 12 * k)} {_f(ey - 16 * k)}", fc, 2.2, seed + 4, 1, 0.7))
    out.append(f'<path d="{blob(ox + 412 * k, oy + 288 * k, 12 * k, 8 * k, seed + 5, 0.1, 10)}" fill="#E89AA8" opacity="0.5"/>')
    out.append(ink(f"M {_f(ox + 392 * k)} {_f(oy + 302 * k)} q {_f(6 * k)} {_f(3 * k)} {_f(11 * k)} {_f(-1 * k)}", fc, 2.2, seed + 6, 1, 0.8))
    return "".join(out)


@design("sun-and-moon")
def d_sun_and_moon():
    u = "nsc-sm"
    out = [sky(u, 1101, "fire", [(200, 250, 260, 200, 10), (480, 200, 160, 120, -20)], None, 120,
               keep=lambda x, y: math.hypot(x - 238, y - 252) > 150 or y > 420)]
    out.append(glow(f"{u}-sg", 238, 252, 250, "#F6B860", 0.45, 0.35))
    out.append(sun_face(f"{u}-sun", 238, 252, 88, 1110))
    out.append(moon_face(f"{u}-moon", 1120, 1.0, 14, -2))
    for x, y, r in ((510, 110, 10), (470, 400, 8), (110, 420, 7), (530, 300, 6), (92, 96, 8)):
        out.append(spark(x, y, r, GOLD_L, 0.95))
    # lettering: SUN & MOON on one line
    s1, s2 = "SUN", "MOON"
    fs = 62
    w1, w2 = measure(s1, CINZEL, fs, 6), measure(s2, CINZEL, fs, 6)
    wa = measure("&", SERIF_IT, 84)
    gap = 18
    tot = w1 + wa + w2 + 2 * gap
    x0 = 300 - tot / 2
    out.append(bword(f"{u}-w1", x0, 508, s1, CINZEL, fs, GOLD, [GOLD_L, GOLD_D, "#F6D88E"], 1130, max_w=300, ls=6, anchor="start", shadow="#05040E", sd=0.04))
    out.append(script(x0 + w1 + gap + wa / 2, 514, "&", 84, CREAM, 200, shadow="#05040E", sd=(2, 3)))
    out.append(bword(f"{u}-w2", x0 + w1 + wa + 2 * gap, 508, s2, CINZEL, fs, GOLD, [GOLD_L, GOLD_D, "#F6D88E"], 1131, max_w=300, ls=6, anchor="start",
                     shadow="#05040E", sd=0.04))
    out.append(finish(u, 1140))
    return "".join(out)


# ---------------------------------------------------------------- over the moon
def painted_crescent(u, cx, cy, r, off, seed, rot=0, halo=True):
    from halloween_gouache_b import crescent_d
    d = crescent_d(cx, cy, r, off)
    out = []
    if halo:
        out.append(glow(f"{u}-h", cx - r * 0.2, cy, r * 1.9, GOLD_L, 0.4, 0.3))
    g = [wash(d, "#F6DE9E", seed, 3, 1.2, 0.5)]
    inner = [f'<path d="M {_f(cx - r)} {_f(cy - r)} L {_f(cx + r)} {_f(cy - r)} L {_f(cx + r)} {_f(cy + r)} L {_f(cx - r)} {_f(cy + r)} Z" fill="url(#{u}-cg)"/>',
             dabs(["#FFF3CC", "#E9C373", "#FBE8B4", "#DDB060"], seed + 1, (cx - r, cy - r, cx + r, cy + r), int(r * 1.6), around(cx, cy), (r * 0.12, r * 0.35),
                  (r * 0.015, r * 0.035), (0.2, 0.5), 0.1, 14)]
    rnd = random.Random(seed)
    for _ in range(7):
        a = rnd.uniform(math.pi * 0.6, math.pi * 1.4)
        dd = rnd.uniform(0.55, 0.9) * r
        rr = r * rnd.uniform(0.04, 0.09)
        x, y = cx + dd * math.cos(a), cy + dd * math.sin(a)
        inner.append(f'<path d="{blob(x, y, rr, rr, rnd.randrange(999), 0.15, 8)}" fill="#C4924A" opacity="0.4"/>'
                     f'<path d="M {_f(x - rr * 0.6)} {_f(y + rr * 0.9)} Q {_f(x + rr)} {_f(y + rr * 0.9)} {_f(x + rr * 0.95)} {_f(y - rr * 0.5)}" fill="none" '
                     f'stroke="#FFF6DA" stroke-width="{_f(max(1, rr * 0.3))}" opacity="0.65" stroke-linecap="round"/>')
    g.append(defs(rg(f"{u}-cg", [(0, "#FFF6D6", 0), (0.7, "#E9C373", 0.15), (1, "#C4924A", 0.5)], 0.5, 0.5, 0.5)))
    g.append(clip(f"{u}-cc", d) + f'<g clip-path="url(#{u}-cc)">' + "".join(inner) + "</g>")
    g.append(ink(d, "#B07E38", 2.6, seed + 2, 2, 0.75))
    out.append(f'<g transform="rotate({rot} {cx} {cy})">' + "".join(g) + "</g>")
    return "".join(out)


def cow(u, seed, ox=0, oy=0):
    from halloween_gouache_b import limb_d
    W, SH, PAT, PINK, LN = "#F8F2E6", "#C9C0E0", "#2C2646", "#F2A9A4", "#231C3C"
    T = lambda *pts: [(x + ox, y + oy) for x, y in pts]  # noqa: E731
    out = []
    # far legs (behind), darker
    for pts in (T((340, 166), (364, 190), (384, 206)), T((262, 168), (238, 192), (214, 204))):
        d = limb_d(pts, 15, 10, seed)
        out.append(f'<path d="{d}" fill="#D8D0E8"/>' + ink(d, LN, 2, seed, 1, 0.8))
        ex, ey = pts[-1]
        out.append(f'<path d="{blob(ex + (4 if ex > 300 else -4), ey + 2, 7, 6, seed, 0.1, 8)}" fill="{PAT}"/>')
    # tail
    tail = L(*T((224, 130), (206, 112), (196, 96), (182, 88)))
    out.append(ink(tail, LN, 4.5, seed, 1, 0.95) + ink(tail, W, 2.4, seed, 1, 1))
    out.append(f'<path d="{blob(180 + ox, 86 + oy, 9, 7, seed + 1, 0.2, 10, rot=-30)}" fill="{PAT}"/>')
    body_d = C(*T((222, 132), (244, 108), (300, 100), (358, 106), (384, 126), (382, 158), (352, 176), (292, 180), (242, 174), (218, 156)))
    out.append(f'<path d="{body_d}" fill="{W}"/>')
    inner = [f'<path d="{blob(262 + ox, 128 + oy, 30, 22, seed + 2, 0.18, 12, rot=10)}" fill="{PAT}"/>',
             f'<path d="{blob(334 + ox, 150 + oy, 24, 18, seed + 3, 0.2, 12, rot=-20)}" fill="{PAT}"/>',
             f'<path d="{blob(306 + ox, 104 + oy, 14, 9, seed + 4, 0.2, 10)}" fill="{PAT}"/>',
             f'<path d="M {200 + ox} {166 + oy} Q {300 + ox} {150 + oy} {400 + ox} {164 + oy} L {400 + ox} {200 + oy} L {200 + ox} {200 + oy} Z" fill="{SH}" opacity="0.55"/>',
             dabs(["#FFFFFF", "#E8E0F0", "#D6CDE8"], seed + 5, (210 + ox, 98 + oy, 390 + ox, 182 + oy), 70, 0, (10, 26), (1.2, 3), (0.2, 0.5), 0.15)]
    out.append(clip(f"{u}-bc", body_d) + f'<g clip-path="url(#{u}-bc)">' + "".join(inner) + "</g>")
    out.append(ink(body_d, LN, 2.6, seed + 6, 2, 0.9))
    # udder, near legs
    out.append(f'<path d="{blob(300 + ox, 180 + oy, 14, 8, seed + 7, 0.1, 10)}" fill="{PINK}"/>' + ink(blob(300 + ox, 180 + oy, 14, 8, seed + 7, 0.1, 10), LN, 1.6, seed, 1, 0.7))
    for pts in (T((360, 160), (388, 176), (418, 184)), T((246, 162), (216, 176), (186, 180))):
        d = limb_d(pts, 17, 11, seed + 8)
        out.append(f'<path d="{d}" fill="{W}"/>' + ink(d, LN, 2.2, seed, 1, 0.9))
        ex, ey = pts[-1]
        out.append(f'<path d="{blob(ex + (5 if ex > 300 else -5), ey + 1, 7.5, 7, seed + 9, 0.1, 8)}" fill="{PAT}"/>')
    # collar and bell
    out.append(ink(L(*T((376, 120), (384, 140), (382, 160))), "#7A4AA8", 6, seed, 1, 1))
    bell = C(*T((376, 158), (390, 158), (394, 176), (372, 176)))
    out.append(f'<path d="{bell}" fill="{GOLD}"/>' + ink(bell, GOLD_DD, 1.8, seed, 1, 0.9) + f'<circle cx="{383 + ox}" cy="{178 + oy}" r="3" fill="{GOLD_DD}"/>')
    # head
    ears = [C(*T((386, 100), (364, 88), (356, 96), (380, 108))), C(*T((420, 92), (444, 80), (448, 90), (426, 102)))]
    for e in ears:
        out.append(f'<path d="{e}" fill="{W}"/>' + ink(e, LN, 2, seed, 1, 0.85))
    for hx, hy, dx in ((396, 90, -6), (414, 88, 6)):
        out.append(ink(f"M {hx + ox} {hy + oy + 4} q {dx * 0.3:.1f} -8 {dx} -12", "#EADFC6", 5, seed, 1, 1) + ink(f"M {hx + ox} {hy + oy + 4} q {dx * 0.3:.1f} -8 {dx} -12", LN, 1.4, seed, 1, 0.6))
    head = blob(404 + ox, 114 + oy, 28, 24, seed + 10, 0.05, 14, rot=-15)
    out.append(f'<path d="{head}" fill="{W}"/>' + clip(f"{u}-hc", head) + f'<g clip-path="url(#{u}-hc)"><path d="{blob(392 + ox, 102 + oy, 12, 10, seed + 11, 0.2, 10)}" fill="{PAT}"/></g>')
    out.append(ink(head, LN, 2.4, seed + 12, 2, 0.9))
    muz = blob(426 + ox, 128 + oy, 19, 14, seed + 13, 0.05, 12, rot=-15)
    out.append(f'<path d="{muz}" fill="{PINK}"/>' + ink(muz, LN, 2, seed, 1, 0.85))
    out.append(f'<circle cx="{420 + ox}" cy="{128 + oy}" r="2.4" fill="{LN}"/><circle cx="{433 + ox}" cy="{124 + oy}" r="2.4" fill="{LN}"/>')
    out.append(ink(f"M {402 + ox} {110 + oy} q 6 5 12 0", LN, 2.6, seed, 1, 1))
    out.append(f'<path d="{blob(398 + ox, 124 + oy, 6, 4, seed, 0.1, 8)}" fill="{PINK}" opacity="0.6"/>')
    # motion swooshes
    for k, (x, y) in enumerate(((168, 140), (160, 160), (176, 120))):
        out.append(ink(f"M {x + ox} {y + oy} q -24 4 -44 16", CREAM, 2.4, seed + k, 1, 0.55))
    return "".join(out)


@design("over-the-moon")
def d_over_the_moon():
    u = "nsc-otm"
    out = [sky(u, 1201, "air", [(300, 300, 280, 160, -10), (480, 120, 160, 100, 20)], None, 120,
               keep=lambda x, y: not (200 < x < 460 and 80 < y < 220))]
    out.append(painted_crescent(f"{u}-cr", 300, 328, 122, 64, 1210))
    out.append(puff_cloud(f"{u}-c1", 150, 436, 170, 46, 1211, "#6A6AAE", ["#8A88C8", "#5A5A9E", "#A8A6DC"], line=None, light="#C8C6F0"))
    out.append(puff_cloud(f"{u}-c2", 470, 410, 150, 40, 1212, "#5E5EA4", ["#8A88C8", "#4E4E92", "#A8A6DC"], line=None, light="#C8C6F0"))
    out.append(cow(f"{u}-cow", 1220, 0, 6))
    for x, y, r in ((470, 74, 9), (100, 220, 8), (520, 250, 7), (90, 90, 6)):
        out.append(spark(x, y, r, GOLD_L, 0.95))
    out.append(bword(f"{u}-tx", 300, 528, "over the moon", SERIF_IT, 72, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 1230, max_w=440,
                     shadow="#05040E", sd=0.035, angle=-20))
    out.append(finish(u, 1240))
    return "".join(out)


# ---------------------------------------------------------------- shoot for the moon
def rocket(u, cx, cy, k, rot, seed):
    LN = "#1E1638"
    def T(x, y):
        a = math.radians(rot)
        return (cx + (x * math.cos(a) - y * math.sin(a)) * k, cy + (x * math.sin(a) + y * math.cos(a)) * k)
    out = []
    # flame
    for (w, h, col, op) in ((30, 92, "#E8792E", 0.85), (22, 70, GOLD, 0.95), (12, 44, "#FFF3C8", 1)):
        fd = C(T(-w, 92), T(-w * 0.6, 92 + h * 0.5), T(0, 92 + h), T(w * 0.6, 92 + h * 0.5), T(w, 92))
        out.append(f'<path d="{fd}" fill="{col}" opacity="{op}"/>')
    out.append(glow(f"{u}-fg", *T(0, 140), 70 * k, "#FFB54A", 0.55, 0.3))
    fins = [C(T(-34, 26), T(-70, 70), T(-70, 104), T(-30, 84)), C(T(34, 26), T(70, 70), T(70, 104), T(30, 84))]
    for i, f in enumerate(fins):
        out.append(body(f"{u}-fn{i}", f, (cx - 120, cy - 120, cx + 120, cy + 120), "#C0508A", ["#E07AA6", "#8A2E66", "#F2A0C0"], seed + i, n=24,
                        angle=rot - 90, length=(8, 20), width=(1.5, 3.5), line=LN, lw=2.4))
    noz = C(T(-20, 80), T(20, 80), T(26, 98), T(-26, 98))
    out.append(f'<path d="{noz}" fill="#4A4470"/>' + ink(noz, LN, 2.2, seed, 1, 0.9))
    hull = C(T(0, -112), T(28, -76), T(40, -14), T(36, 50), T(24, 86), T(-24, 86), T(-36, 50), T(-40, -14), T(-28, -76))
    out.append(body(f"{u}-hl", hull, (cx - 130, cy - 130, cx + 130, cy + 130), "#F4ECDA", ["#FFFFFF", "#E0D6C2", "#FFF8EA", "#D2C6E0"], seed + 3, n=70,
                    angle=rot - 90, length=(10, 30), width=(1.5, 4), line=None))
    shade = (f'<path d="M {_f(T(14, -120)[0])} {_f(T(14, -120)[1])} L {_f(T(60, -120)[0])} {_f(T(60, -120)[1])} L {_f(T(60, 100)[0])} {_f(T(60, 100)[1])} '
             f'L {_f(T(14, 100)[0])} {_f(T(14, 100)[1])} Z" fill="#A89CC8"/>')
    nose = (f'<path d="M {_f(T(-60, -130)[0])} {_f(T(-60, -130)[1])} L {_f(T(60, -130)[0])} {_f(T(60, -130)[1])} L {_f(T(60, -66)[0])} {_f(T(60, -66)[1])} '
            f'Q {_f(T(0, -56)[0])} {_f(T(0, -56)[1])} {_f(T(-60, -66)[0])} {_f(T(-60, -66)[1])} Z" fill="#C0508A"/>')
    stripe = (f'<path d="M {_f(T(-60, 40)[0])} {_f(T(-60, 40)[1])} Q {_f(T(0, 48)[0])} {_f(T(0, 48)[1])} {_f(T(60, 40)[0])} {_f(T(60, 40)[1])} '
              f'L {_f(T(60, 54)[0])} {_f(T(60, 54)[1])} Q {_f(T(0, 62)[0])} {_f(T(0, 62)[1])} {_f(T(-60, 54)[0])} {_f(T(-60, 54)[1])} Z" fill="{GOLD}"/>')
    out.append(clip(f"{u}-hc", hull) + f'<g clip-path="url(#{u}-hc)">{nose}<g opacity="0.4">{shade}</g>{stripe}'
               + dabs(["#E07AA6", "#8A2E66"], seed + 4, (cx - 80, cy - 120, cx + 80, cy), 20, rot - 90, (8, 18), (1.2, 3), (0.2, 0.5), 0.2) + "</g>")
    out.append(ink(L(T(-24, -62), T(0, -58), T(24, -62)), LN, 1.8, seed, 1, 0.6))
    out.append(ink(hull, LN, 2.8, seed + 5, 2, 0.95))
    # porthole
    pc = T(0, -20)
    out.append(f'<circle cx="{_f(pc[0])}" cy="{_f(pc[1])}" r="{_f(21 * k)}" fill="{GOLD}"/>' + ink(blob(pc[0], pc[1], 21 * k, 21 * k, seed, 0.01, 16), LN, 2.2, seed, 1, 0.9))
    out.append(defs(rg(f"{u}-pg", [(0, "#6A7AD8"), (0.7, "#2A2E78"), (1, "#141846")], 0.4, 0.38, 0.7))
               + f'<circle cx="{_f(pc[0])}" cy="{_f(pc[1])}" r="{_f(14 * k)}" fill="url(#{u}-pg)"/>')
    out.append(f'<path d="M {_f(pc[0] - 8 * k)} {_f(pc[1] - 2 * k)} A {_f(9 * k)} {_f(9 * k)} 0 0 1 {_f(pc[0] + 1 * k)} {_f(pc[1] - 9 * k)}" stroke="#FFFFFF" stroke-width="{_f(3 * k)}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    out.append(spark(pc[0] + 3 * k, pc[1] + 3 * k, 5 * k, GOLD_L, 0.9))
    # rivets
    for y in (6, 22):
        for x in (-28, 28):
            p = T(x, y)
            out.append(f'<circle cx="{_f(p[0])}" cy="{_f(p[1])}" r="1.8" fill="{LN}" opacity="0.5"/>')
    return "".join(out)


def smoke_trail(u, pts, r0, r1, seed, cols=("#E8E2F4", "#C8C0E2", "#F8F4FF"), shade="#9A90C8"):
    rnd = random.Random(seed)
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        r = r0 + (r1 - r0) * t
        for _ in range(2):
            px, py = x + rnd.uniform(-r * 0.4, r * 0.4), y + rnd.uniform(-r * 0.4, r * 0.4)
            d = blob(px, py, r, r * 0.9, rnd.randrange(999), 0.08, 12)
            out.append(f'<path d="{d}" fill="{shade}" opacity="{0.5 * (1 - t * 0.6):.2f}" transform="translate(3 4)"/>')
            out.append(f'<path d="{d}" fill="{rnd.choice(cols)}" opacity="{0.92 * (1 - t * 0.55):.2f}"/>')
            out.append(f'<path d="{blob(px - r * 0.25, py - r * 0.3, r * 0.5, r * 0.4, rnd.randrange(999), 0.1, 10)}" fill="#FFFFFF" opacity="{0.6 * (1 - t):.2f}"/>')
    return "".join(out)


def ringed_planet(u, cx, cy, r, seed):
    d = blob(cx, cy, r, r, seed, 0.01, 18)
    ring_back = f'<path d="M {_f(cx - r * 1.8)} {_f(cy)} A {_f(r * 1.8)} {_f(r * 0.5)} 0 0 1 {_f(cx + r * 1.8)} {_f(cy)}" fill="none" stroke="{GOLD}" stroke-width="{_f(r * 0.22)}" opacity="0.9"/>'
    ring_front = f'<path d="M {_f(cx - r * 1.8)} {_f(cy)} A {_f(r * 1.8)} {_f(r * 0.5)} 0 0 0 {_f(cx + r * 1.8)} {_f(cy)}" fill="none" stroke="{GOLD_L}" stroke-width="{_f(r * 0.22)}"/>'
    out = [f'<g transform="rotate(-18 {cx} {cy})">', ring_back,
           body(f"{u}-pl", d, (cx - r, cy - r, cx + r, cy + r), "#8A6AC8", ["#A88AE0", "#5E44A0", "#C0A8EC"], seed, n=40, angle=-4, length=(r * 0.3, r * 0.8),
                width=(1.5, 3.5), line=INKN, lw=2),
           shade_in(f"{u}-ps", d, f'<circle cx="{_f(cx + r * 0.5)}" cy="{_f(cy + r * 0.5)}" r="{_f(r)}" fill="#2A1E58"/>', "#000", 0.5),
           ring_front, "</g>"]
    return "".join(out)


@design("shoot-for-the-moon")
def d_shoot_for_the_moon():
    u = "nsc-sfm"
    out = [sky(u, 1301, "fire", [(420, 160, 220, 140, 20), (140, 430, 220, 120, -30)], None, 130, text_shade=False)]
    out.append(pmoon(f"{u}-mn", 448, 152, 74, 1310, halo_r=2.2, halo_op=0.5))
    out.append(ringed_planet(f"{u}-pl", 478, 470, 26, 1311))
    trail = []
    for i in range(12):
        t = i / 11
        trail.append((262 - t * 230 + 30 * math.sin(t * 3.4), 470 + t * 120 - 40 * math.sin(t * 2.6)))
    out.append(smoke_trail(f"{u}-sm", trail, 18, 42, 1312))
    out.append(rocket(f"{u}-rk", 330, 368, 0.92, 42, 1320))
    for x, y, r in ((560, 300, 8), (330, 70, 7), (90, 330, 6), (250, 300, 6)):
        out.append(spark(x, y, r, GOLD_L, 0.95))
    # stacked lettering, top-left
    out.append(script(174, 136, "shoot", 74, CREAM, 230, shadow="#05040E", sd=(2, 3)))
    out.append(label_rules(176, 176, "FOR THE", MONO, 20, GOLD_L, 6, 1330, gap=10, line_w=22))
    out.append(bword(f"{u}-mn2", 178, 250, "MOON", CINZEL, 70, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 1331, max_w=232, ls=6,
                     shadow="#05040E", sd=0.04, angle=-14))
    out.append(finish(u, 1340))
    return "".join(out)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
