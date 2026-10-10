"""Night Sky, hand-painted edition: zodiac constellations, zodiac glyph medallions and celestial storybook pieces.

Every magnet is painted, not drawn: brushed deep-night skies with nebula washes, stars of many sizes with soft
glows, gilded glyphs, painted moons and suns, brush-textured lettering and grain on top. The constellations are
plotted from real star coordinates (gnomonic projection, north up / east left, turned to fit), with the stars sized by
magnitude and tinted by their true colour, a faint atlas grid and ecliptic, and the sign's figure painted in gold leaf
around them. One palette for the whole series: midnight navy, indigo, violet, gold,
cream; each element (fire, earth, air, water) gets its own nebula colour story so the twelve signs never feel
interchangeable.

Run from tools/designs:  python3 night_sky_painted.py [slug ...]
"""
import math
import os
import random
import sys

from common import CINZEL, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, ink, smooth_closed, smooth_open, wash
from halloween_gouache_b import (around, arc_word, body, brush, brush_rule, bword, clip, dabs, defs, glow, grain_over, pmoon, script,
                                 shade_in)
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


# ---------------------------------------------------------------- zodiac glyphs (unit box, stroked)
GLYPH = {
    "aries": ["M 0 0.85 L 0 -0.15 C 0 -0.65 -0.25 -0.85 -0.5 -0.85 C -0.78 -0.85 -0.92 -0.6 -0.86 -0.38 C -0.8 -0.2 -0.62 -0.14 -0.52 -0.22",
              "M 0 -0.15 C 0 -0.65 0.25 -0.85 0.5 -0.85 C 0.78 -0.85 0.92 -0.6 0.86 -0.38 C 0.8 -0.2 0.62 -0.14 0.52 -0.22"],
    "taurus": ["M 0 0.92 A 0.44 0.44 0 1 1 0.001 0.92",
               "M -0.82 -0.82 C -0.72 -0.44 -0.42 -0.08 0 -0.08 C 0.42 -0.08 0.72 -0.44 0.82 -0.82"],
    "gemini": ["M -0.72 -0.82 Q 0 -0.56 0.72 -0.82", "M -0.72 0.82 Q 0 0.56 0.72 0.82", "M -0.34 -0.68 L -0.34 0.68", "M 0.34 -0.68 L 0.34 0.68"],
    "cancer": ["M -0.72 -0.3 A 0.22 0.22 0 1 1 -0.28 -0.3 A 0.22 0.22 0 1 1 -0.72 -0.3",
               "M -0.5 -0.52 C -0.1 -0.76 0.52 -0.72 0.88 -0.34",
               "M 0.72 0.3 A 0.22 0.22 0 1 1 0.28 0.3 A 0.22 0.22 0 1 1 0.72 0.3",
               "M 0.5 0.52 C 0.1 0.76 -0.52 0.72 -0.88 0.34"],
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


# ---------------------------------------------------------------- real star positions
# Each constellation is drawn from real J2000 coordinates (RA hours, Dec degrees, visual magnitude), projected
# gnomonically as seen on the sky (north up, east to the left), then turned by a fixed angle and fitted to the art box.
CAT = {
    "aries": dict(stars={"Hamal": (2.1196, 23.46, 2.0), "Sheratan": (1.9107, 20.81, 2.65), "Mesarthim": (1.8922, 19.29, 3.9),
                         "41 Ari": (2.8330, 27.26, 3.6)},
                  lines=[["41 Ari", "Hamal", "Sheratan", "Mesarthim"]], alpha="Hamal", rot=-20, box=(140, 175, 455, 250)),
    "taurus": dict(stars={"Aldebaran": (4.5987, 16.51, 0.85), "Elnath": (5.4382, 28.61, 1.65), "zeta": (5.6274, 21.14, 3.0),
                          "theta": (4.4783, 15.87, 3.4), "gamma": (4.3297, 15.63, 3.65), "delta": (4.3822, 17.54, 3.75),
                          "epsilon": (4.4769, 19.18, 3.5), "lambda": (4.0112, 12.49, 3.4), "Pleiades": (3.7914, 24.11, 2.9)},
                   lines=[["zeta", "Aldebaran", "theta", "gamma", "lambda"], ["Elnath", "epsilon", "delta", "gamma"]],
                   alpha="Aldebaran", rot=60, box=(150, 95, 450, 335)),
    "gemini": dict(stars={"Castor": (7.5767, 31.89, 1.6), "Pollux": (7.7553, 28.03, 1.15), "Alhena": (6.6285, 16.40, 1.9),
                          "Mebsuta": (6.7322, 25.13, 3.0), "Tejat": (6.3827, 22.51, 2.9), "Propus": (6.2479, 22.51, 3.3),
                          "Wasat": (7.3354, 21.98, 3.5), "kappa": (7.7408, 24.40, 3.6), "iota": (7.4287, 27.80, 3.8),
                          "tau": (7.1857, 30.25, 4.4), "theta": (6.8798, 33.96, 3.6), "xi": (6.7548, 12.90, 3.35),
                          "lambda": (7.3017, 16.54, 3.6), "Mekbuda": (7.0686, 20.57, 3.9), "nu": (6.4829, 20.21, 4.1),
                          "upsilon": (7.5985, 26.90, 4.06)},
                   lines=[["Castor", "tau", "Mebsuta", "Tejat", "Propus"], ["tau", "theta"], ["Mebsuta", "nu"],
                          ["Pollux", "upsilon", "Wasat", "Mekbuda", "Alhena"], ["upsilon", "kappa"], ["upsilon", "iota", "tau"],
                          ["Wasat", "lambda", "xi"]], alpha="Pollux", rot=60, box=(160, 106, 440, 384)),
    "cancer": dict(stars={"Acubens": (8.9748, 11.86, 4.25), "Altarf": (8.2753, 9.19, 3.5), "Asellus Australis": (8.7448, 18.15, 3.9),
                          "Asellus Borealis": (8.7215, 21.47, 4.65), "iota": (8.7782, 28.76, 4.0)},
                   lines=[["Altarf", "Asellus Australis", "Acubens"], ["Asellus Australis", "Asellus Borealis", "iota"]],
                   alpha="Altarf", rot=180, box=(150, 100, 450, 372), extra={"Beehive": (8.67, 19.67)}),
    "leo": dict(stars={"Regulus": (10.1395, 11.97, 1.35), "eta": (10.1222, 16.76, 3.5), "Algieba": (10.3329, 19.84, 2.0),
                       "Adhafera": (10.2782, 23.42, 3.4), "Rasalas": (9.8794, 26.01, 3.9), "epsilon": (9.7642, 23.77, 3.0),
                       "Zosma": (11.2351, 20.52, 2.55), "Chertan": (11.2373, 15.43, 3.3), "Denebola": (11.8177, 14.57, 2.1)},
                lines=[["Regulus", "eta", "Algieba", "Adhafera", "Rasalas", "epsilon"], ["Algieba", "Zosma", "Denebola", "Chertan", "Regulus"],
                       ["Zosma", "Chertan"]], alpha="Regulus", rot=0, box=(100, 130, 470, 365)),
    "virgo": dict(stars={"Spica": (13.4199, -11.16, 0.97), "Porrima": (12.6943, -1.45, 2.7), "delta": (12.9268, 3.40, 3.4),
                         "Vindemiatrix": (13.0363, 10.96, 2.8), "zeta": (13.5783, -0.60, 3.4), "Zavijava": (11.8448, 1.76, 3.6),
                         "Zaniah": (12.3318, -0.67, 3.9), "iota": (14.2668, -6.0, 4.1), "mu": (14.7177, -5.66, 3.9),
                         "109 Vir": (14.7706, 1.89, 3.7), "tau": (14.0273, 1.54, 4.3), "theta": (13.1658, -5.54, 4.4)},
                  lines=[["Zavijava", "Zaniah", "Porrima", "delta", "Vindemiatrix"], ["Porrima", "theta", "Spica"],
                         ["delta", "zeta", "tau", "109 Vir"], ["zeta", "Spica"], ["Spica", "iota", "mu"]], alpha="Spica", rot=-90,
                  box=(180, 100, 420, 388)),
    "libra": dict(stars={"Zubenelgenubi": (14.8480, -16.04, 2.75), "Zubeneschamali": (15.2834, -9.38, 2.6), "sigma": (15.0678, -25.28, 3.3),
                         "gamma": (15.5921, -14.79, 3.9), "upsilon": (15.6168, -28.13, 3.6), "tau": (15.6446, -29.78, 3.7)},
                  lines=[["sigma", "Zubenelgenubi", "Zubeneschamali", "gamma", "Zubenelgenubi"], ["gamma", "upsilon", "tau"]],
                  alpha="Zubeneschamali", rot=-7, box=(150, 95, 450, 375)),
    "scorpio": dict(stars={"Antares": (16.4901, -26.43, 1.05), "Acrab": (16.0906, -19.81, 2.6), "Dschubba": (16.0056, -22.62, 2.3),
                           "pi": (15.9809, -26.11, 2.9), "rho": (15.9488, -29.21, 3.9), "sigma": (16.3531, -25.59, 2.9),
                           "tau": (16.5980, -28.22, 2.8), "epsilon": (16.8361, -34.29, 2.3), "mu": (16.8645, -38.05, 3.0),
                           "zeta": (16.9097, -42.36, 3.6), "eta": (17.2026, -43.24, 3.3), "Sargas": (17.6219, -43.0, 1.85),
                           "iota": (17.7930, -40.13, 3.0), "kappa": (17.7081, -39.03, 2.4), "Shaula": (17.5601, -37.10, 1.6),
                           "Lesath": (17.5127, -37.30, 2.7), "nu": (16.1998, -19.46, 4.0)},
                    lines=[["nu", "Acrab", "Dschubba", "pi", "rho"], ["Dschubba", "sigma", "Antares", "tau", "epsilon", "mu", "zeta", "eta",
                                                                      "Sargas", "iota", "kappa", "Shaula", "Lesath"]],
                    alpha="Antares", rot=0, box=(120, 100, 455, 378)),
    "sagittarius": dict(stars={"Kaus Australis": (18.4029, -34.38, 1.85), "Kaus Media": (18.3499, -29.83, 2.7),
                               "Kaus Borealis": (18.4661, -25.42, 2.8), "Nunki": (18.9211, -26.30, 2.05), "phi": (18.7609, -26.99, 3.2),
                               "tau": (19.1157, -27.67, 3.3), "Ascella": (19.0435, -29.88, 2.6), "Alnasl": (18.0968, -30.42, 3.0),
                               "eta": (18.2938, -36.76, 3.1), "mu": (18.2297, -21.06, 3.85)},
                        lines=[["Alnasl", "Kaus Media", "Kaus Australis", "Alnasl"], ["Kaus Media", "Kaus Borealis", "phi", "Kaus Media"],
                               ["Kaus Borealis", "mu"], ["phi", "Nunki", "tau", "Ascella", "phi"], ["Ascella", "Kaus Australis"],
                               ["Kaus Australis", "eta"]], alpha="Kaus Australis", rot=0, box=(150, 110, 460, 372)),
    "capricorn": dict(stars={"Algedi": (20.3009, -12.54, 3.6), "Dabih": (20.3502, -14.78, 3.05), "psi": (20.7683, -25.27, 4.1),
                             "omega": (20.8636, -26.92, 4.1), "theta": (21.0991, -17.23, 4.1), "zeta": (21.4444, -22.41, 3.7),
                             "Nashira": (21.6682, -16.66, 3.7), "Deneb Algedi": (21.7840, -16.13, 2.85), "iota": (21.3707, -16.83, 4.3)},
                      lines=[["Algedi", "Dabih", "psi", "omega", "zeta", "Deneb Algedi", "Nashira", "iota", "theta", "Dabih"]],
                      alpha="Deneb Algedi", rot=0, box=(120, 130, 470, 360)),
    "aquarius": dict(stars={"Sadalsuud": (21.5260, -5.57, 2.9), "Sadalmelik": (22.0964, -0.32, 2.95), "Albali": (20.7946, -9.50, 3.8),
                            "Sadachbia": (22.3609, -1.39, 3.85), "zeta": (22.4806, -0.02, 3.65), "eta": (22.5891, -0.12, 4.0),
                            "pi": (22.4213, 1.38, 4.6), "theta": (22.2806, -7.78, 4.2), "lambda": (22.8769, -7.58, 3.7),
                            "Skat": (22.9108, -15.82, 3.3), "tau": (22.8266, -13.59, 4.0), "phi": (23.2384, -6.05, 4.2),
                            "psi": (23.2649, -9.09, 4.2), "88 Aqr": (23.1574, -21.17, 3.7), "98 Aqr": (23.3829, -20.10, 3.97),
                            "iota": (22.1072, -13.87, 4.3)},
                     lines=[["Albali", "Sadalsuud", "Sadalmelik", "Sadachbia", "zeta", "eta"], ["zeta", "pi"], ["Sadalsuud", "iota"],
                            ["Sadalmelik", "theta", "lambda", "tau", "Skat", "88 Aqr"], ["lambda", "phi", "psi", "98 Aqr"]],
                     alpha="Sadalsuud", rot=0, box=(120, 110, 470, 360)),
    "pisces": dict(stars={"Alrescha": (2.0341, 2.76, 3.8), "Alpherg": (1.5248, 15.35, 3.6), "omicron": (1.7566, 9.16, 4.3),
                          "tau": (1.1940, 30.09, 4.5), "upsilon": (1.3245, 27.26, 4.7), "phi": (1.2291, 24.58, 4.65),
                          "chi": (1.1915, 21.03, 4.7),
                          "gamma": (23.2864, 3.28, 3.7), "kappa": (23.4489, 1.26, 4.9), "lambda": (23.7006, 1.78, 4.5),
                          "iota": (23.6658, 5.63, 4.1), "theta": (23.4662, 6.38, 4.3), "7 Psc": (23.3381, 5.38, 5.0),
                          "omega": (23.9885, 6.86, 4.0), "delta": (0.8115, 7.59, 4.4), "epsilon": (1.0491, 7.89, 4.3),
                          "zeta": (1.2291, 7.58, 5.2), "mu": (1.5030, 6.14, 4.8), "nu": (1.6905, 5.49, 4.4)},
                   lines=[["gamma", "7 Psc", "theta", "iota", "lambda", "kappa", "gamma"],
                          ["iota", "omega", "delta", "epsilon", "zeta", "mu", "nu", "Alrescha"],
                          ["Alrescha", "omicron", "Alpherg", "chi", "phi", "upsilon", "tau", "phi"]], alpha="Alpherg", rot=0, box=(100, 104, 492, 372)),
}

# true star colours for the bright ones (spectral class), everything else is a warm white
STAR_TINT = {"Aldebaran": "#FFB97A", "Antares": "#FF9466", "Pollux": "#FFD9A0", "Hamal": "#FFD39C", "Regulus": "#D6E4FF",
             "Spica": "#C8DAFF", "Castor": "#E6EEFF", "Elnath": "#DCE6FF", "Denebola": "#EEF3FF", "Algieba": "#FFD8A0",
             "Kaus Australis": "#E4ECFF", "Nunki": "#D8E4FF", "Shaula": "#D8E4FF", "Sargas": "#FFF0C8", "Alhena": "#E8F0FF",
             "Deneb Algedi": "#F2F4FF", "Sadalsuud": "#FFF0C8", "Zubeneschamali": "#DCE8FF", "Alpherg": "#FFF2D6"}


def _gn(ra, dec, ra0, dec0):
    a, d, a0, d0 = math.radians(ra * 15), math.radians(dec), math.radians(ra0 * 15), math.radians(dec0)
    c = math.sin(d0) * math.sin(d) + math.cos(d0) * math.cos(d) * math.cos(a - a0)
    x = math.cos(d) * math.sin(a - a0) / c
    y = (math.cos(d0) * math.sin(d) - math.sin(d0) * math.cos(d) * math.cos(a - a0)) / c
    return -x, -y


def sky_map(sign):
    """-> (positions of the named stars, T(ra, dec) for any other point, magnitude dict)."""
    cfg = CAT[sign]
    st = cfg["stars"]
    ref = next(iter(st.values()))[0]

    def unwrap(r):
        while r - ref > 12:
            r -= 24
        while ref - r > 12:
            r += 24
        return r
    ra0 = sum(unwrap(v[0]) for v in st.values()) / len(st)
    dec0 = sum(v[1] for v in st.values()) / len(st)
    c, s = math.cos(math.radians(cfg["rot"])), math.sin(math.radians(cfg["rot"]))

    def raw(ra, dec):
        x, y = _gn(unwrap(ra), dec, ra0, dec0)
        return x * c - y * s, x * s + y * c
    pts = {n: raw(v[0], v[1]) for n, v in st.items()}
    xs, ys = [p[0] for p in pts.values()], [p[1] for p in pts.values()]
    x0, y0, x1, y1 = cfg["box"]
    k = min((x1 - x0) / (max(xs) - min(xs)), (y1 - y0) / (max(ys) - min(ys)))
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2

    def T(ra, dec):
        x, y = raw(ra, dec)
        return ((x - mx) * k + (x0 + x1) / 2, (y - my) * k + (y0 + y1) / 2)
    P = {n: T(v[0], v[1]) for n, v in st.items()}
    for n, (ra, dec) in cfg.get("extra", {}).items():
        P[n] = T(ra, dec)
    return P, T, {n: v[2] for n, v in st.items()}


def atlas_grid(u, T, sign):
    """Faint dashed right-ascension / declination lines and the ecliptic, as on an antique star atlas."""
    st = CAT[sign]["stars"].values()
    ras = [v[0] for v in st]
    decs = [v[1] for v in st]
    ra_c = ras[0]
    out = []

    def poly(pts):
        pts = [p for p in pts if -60 < p[0] < 660 and -60 < p[1] < 660]
        return "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) if len(pts) > 1 else ""
    d0 = int(min(decs) // 10) * 10 - 20
    for dec in range(d0, d0 + 80, 10):
        if abs(dec) >= 80:
            continue
        out.append(poly([T(ra_c + h / 10, dec) for h in range(-50, 51)]))
    for h in range(-4, 5):
        ra = round(ra_c) + h
        out.append(poly([T(ra, dec / 2) for dec in range(2 * (d0 - 10), 2 * (d0 + 80))]))
    g = (f'<g fill="none" stroke="{GOLD}" stroke-width="1.1" stroke-dasharray="1.5 5" stroke-linecap="round" opacity="0.32">'
         + "".join(f'<path d="{d}"/>' for d in out if d) + "</g>")
    ecl = []
    eps = math.radians(23.44)
    for i in range(0, 361):
        lam = math.radians(i)
        dec = math.degrees(math.asin(math.sin(eps) * math.sin(lam)))
        ra = (math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) / 15) % 24
        ecl.append(T(ra, dec))
    # keep only the run of points that is on (or near) the canvas, in order
    run, best = [], []
    for p in ecl:
        if -80 < p[0] < 680 and -80 < p[1] < 680:
            run.append(p)
            if len(run) > len(best):
                best = run
        else:
            run = []
    if len(best) > 1:
        g += (f'<path d="{L(*best)}" fill="none" stroke="{GOLD_L}" stroke-width="1.6" stroke-dasharray="8 7" '
              f'stroke-linecap="round" opacity="0.32"/>')
    return g


def star_r(m):
    return max(1.7, 1.6 + (4.6 - m) * 1.3)


def star_layer(u, sign, P, mags, label=None):
    """Gold constellation lines (a soft glow and a crisp line) and stars sized by real magnitude, in their true tints."""
    cfg = CAT[sign]
    out = [defs(rg(f"{u}-cg", [(0, GOLD_L, 0.7), (0.3, GOLD, 0.26), (1, GOLD, 0)]),
                rg(f"{u}-wg", [(0, "#FFFFFF", 0.85), (0.25, "#E8EEFF", 0.3), (1, "#C8D4FF", 0)]))]
    poly = "".join(f'<path d="M {" L ".join(f"{_f(P[n][0])} {_f(P[n][1])}" for n in ln)}"/>' for ln in cfg["lines"])
    out.append(f'<g fill="none" stroke="{GOLD_L}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" opacity="0.1">{poly}</g>')
    out.append(f'<g fill="none" stroke="#F4DB98" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity="0.95">{poly}</g>')
    alpha = cfg["alpha"]
    for n, m in sorted(mags.items(), key=lambda kv: -kv[1]):
        x, y = P[n]
        r = star_r(m)
        tint = STAR_TINT.get(n, "#FFF4DA")
        if n == "Pleiades":
            out.append(pleiades(f"{u}-m45", x, y))
            continue
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 4.6)}" fill="url(#{u}-cg)"/>')
        if n == alpha:
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="38" fill="url(#{u}-cg)"/>')
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="16" fill="{tint}" opacity="0.28"/>')
            out.append(spark(x, y, 27, "#FFFFFF", 0.95, 0.12))
            out.append(spark(x, y, 13, tint, 0.9, 0.2, 45))
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r + 1.5)}" fill="{tint}"/><circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 0.6)}" fill="#FFFFFF"/>')
        else:
            if m < 2.9:
                out.append(spark(x, y, r * 3.2, "#FFFFFF", 0.85, 0.12))
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r + 1.1)}" fill="{tint}" opacity="0.9"/>'
                       f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 0.62)}" fill="#FFFFFF"/>')
    if label:
        dx, dy, anc = label
        x, y = P[alpha]
        out.append(script(x + dx, y + dy, alpha, 19, CREAM, 200, anchor=anc, shadow="#05040E", sd=(1.5, 2)))
    return "".join(out)


def pleiades(u, x, y):
    """The Seven Sisters: a tiny blue-white cluster with a reflection-nebula haze."""
    pts = [(0, 0, 2.6), (-9, -4, 2.0), (-14, 3, 1.8), (7, -7, 1.7), (11, 2, 1.6), (-4, 8, 1.5), (3, 6, 1.3)]
    out = [glow(f"{u}-h", x - 2, y, 30, "#A8C4FF", 0.35, 0.35)]
    for dx, dy, r in pts:
        out.append(f'<circle cx="{_f(x + dx)}" cy="{_f(y + dy)}" r="{_f(r * 2.8)}" fill="#C8D8FF" opacity="0.22"/>'
                   f'<circle cx="{_f(x + dx)}" cy="{_f(y + dy)}" r="{_f(r)}" fill="#F2F6FF"/>')
    return "".join(out)


def beehive(u, x, y, seed):
    rnd = random.Random(seed)
    out = [glow(f"{u}-h", x, y, 18, "#FFF0C8", 0.35, 0.35)]
    for _ in range(14):
        out.append(f'<circle cx="{_f(x + rnd.gauss(0, 6))}" cy="{_f(y + rnd.gauss(0, 5))}" r="{rnd.uniform(0.7, 1.4):.2f}" fill="#FFF6E0" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    return "".join(out)


def gold_figure(u, fills=(), lines=(), seed=1, details=(), shade=(), angle=-35, glow_w=9, fade=None, fill_op=0.24):
    """The sign's figure painted in gold leaf: a soft glow, a translucent gold wash with brush texture inside,
    darker shade washes for volume, and hand-inked gold contours. fade=(y0, y1) dissolves it downwards."""
    out = []
    if fills:
        out.append(defs(lg(f"{u}-fg", [(0, "#FBE3A0"), (0.5, "#E2B860"), (1, "#B5873A")], 0, 0, 0.3, 1)))
        out.append(f'<g fill="none" stroke="{GOLD_L}" stroke-width="{glow_w}" stroke-linejoin="round" opacity="0.07">'
                   + "".join(f'<path d="{d}"/>' for d in fills) + "</g>")
        out.append(f'<g fill="url(#{u}-fg)" opacity="{fill_op}">' + "".join(f'<path d="{d}"/>' for d in fills) + "</g>")
        out.append(brush(f"{u}-tx", list(fills), (60, 60, 540, 420), [GOLD_L, GOLD, CREAM, "#C99A48"], seed, 560,
                         angle=angle, length=(10, 34), width=(1.2, 3.4), opacity=(0.08, 0.26), curve=0.25))
        if shade:
            out.append(shade_in(f"{u}-sh", list(fills), "".join(f'<path d="{d}" fill="{NAVY}"/>' for d in shade), NAVY, 0.3))
    for i, s in enumerate(lines):
        d, w, op = (s + (0.85,))[:3] if isinstance(s, tuple) else (s, 2.4, 0.85)
        w *= 1.15
        out.append(ink(d, GOLD_L, w * 3, seed + i, 1, 0.06))
        out.append(ink(d, GOLD, w, seed + i, 2, min(1, op * 1.08)))
    for i, s in enumerate(details):
        d, w, op = (s + (0.7,))[:3] if isinstance(s, tuple) else (s, 1.6, 0.7)
        out.append(ink(d, GOLD, w, seed + 50 + i, 1, op))
    if fade:
        y0, y1 = fade
        return (defs(lg(f"{u}-fm", [(0, "#FFFFFF"), (y0 / 600, "#FFFFFF"), (y1 / 600, "#000000"), (1, "#000000")], 0, 0, 0, 1),
                     f'<mask id="{u}-mk" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">'
                     f'<rect width="600" height="600" fill="url(#{u}-fm)"/></mask>')
                + f'<g mask="url(#{u}-mk)">' + "".join(out) + "</g>")
    return "".join(out)


def tube(pts, w0, w1):
    """Closed outline of a tapering limb along a polyline (width w0 at the start, w1 at the end)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[min(i + 1, n - 1)]
        b = pts[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return smooth_closed(left + right[::-1])


def curls(cx, cy, rx, ry, seed, n=14, r=(5, 8), clipf=None):
    """Little fleece / mane curls: open spiral hooks."""
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        x, y = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1 or (clipf and not clipf(x, y)):
            continue
        rr = rnd.uniform(*r)
        a0 = rnd.uniform(0, 6.28)
        pts = [(x + rr * (1 - t * 0.6) * math.cos(a0 + t * 4.4), y + rr * (1 - t * 0.6) * math.sin(a0 + t * 4.4)) for t in [i / 7 for i in range(8)]]
        out.append(L(*pts))
    return out


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


# ---------------------------------------------------------------- the twelve figures (screen coordinates of the fitted star maps)
def fig_aries(P):
    body_d = scallop(250, 244, 114, 56, 22, 0.07, 3)
    hp = zoom([(368, 198), (394, 186), (422, 190), (444, 206), (462, 230), (476, 254), (470, 270), (452, 276), (428, 268), (404, 258),
               (382, 252), (366, 230)], 372, 214, 1.18)
    head = C(*hp)
    neck = C((326, 204), (362, 192), (392, 218), (396, 262), (366, 280), (334, 260))
    horn, ridges = ram_horn(392, 214, 44, 19, -112, 1.22, flip=-1)
    ear = C((384, 246), (360, 258), (344, 276), (364, 274), (392, 258))
    legs = [tube([(338, 286), (366, 302), (392, 308), (400, 304)], 19, 11), tube([(166, 292), (202, 310), (242, 318), (254, 314)], 21, 11)]
    hooves = [blob(402, 304, 8, 6, 3, 0.1, 8), blob(256, 314, 8, 6, 4, 0.1, 8)]
    tail = C((138, 228), (118, 232), (108, 250), (124, 256), (138, 244))
    fleece = curls(248, 244, 98, 46, 7, 30, (5, 8))
    k = 1.18
    E = lambda x, y: (372 + (x - 372) * k, 214 + (y - 214) * k)  # noqa: E731
    eye = L(E(424, 216), E(432, 221), E(441, 218))
    nose = L(E(458, 248), E(465, 255), E(460, 262))
    mouth = L(E(444, 268), E(456, 266))
    return dict(fills=[tail, *legs, body_d, neck, head, ear, horn], lines=[tail, *[(d, 2.0) for d in legs], (body_d, 2.4), (head, 2.4), (ear, 1.8), (horn, 2.6)],
                details=[*[(r, 1.8) for r in ridges], *fleece, (eye, 2.2), nose, mouth, *hooves],
                shade=[C((130, 272), (250, 300), (390, 270), (400, 330), (120, 330))], angle=-10)


def fig_taurus(P):
    cx = 268
    face = C((cx, 192), (cx + 30, 196), (cx + 44, 214), (cx + 46, 244), (cx + 38, 278), (cx + 30, 302), (cx + 16, 324), (cx - 16, 324),
             (cx - 30, 302), (cx - 38, 278), (cx - 46, 244), (cx - 44, 214), (cx - 30, 196))
    zx, zy = P["zeta"]
    ex, ey = P["Elnath"]
    hornL = C((cx - 40, 216), (cx - 72, 202), (cx - 88, 166), (zx - 20, zy + 26), (zx, zy), (zx + 8, zy + 30), (cx - 64, 168), (cx - 48, 194), (cx - 24, 204))
    hornR = C((cx + 40, 216), (cx + 72, 202), (cx + 88, 166), (ex + 22, ey + 30), (ex, ey), (ex - 8, ey + 32), (cx + 64, 168), (cx + 48, 194), (cx + 24, 204))
    rings = [L((cx - 62 - 4 * i, 196 - 9 * i), (cx - 44 - 6 * i, 190 - 12 * i)) for i in range(3)] + \
            [L((cx + 62 + 4 * i, 196 - 9 * i), (cx + 44 + 6 * i, 190 - 12 * i)) for i in range(3)]
    earL = C((cx - 42, 224), (cx - 76, 214), (cx - 100, 226), (cx - 80, 242), (cx - 44, 240))
    earR = C((cx + 42, 224), (cx + 76, 214), (cx + 100, 226), (cx + 80, 242), (cx + 44, 240))
    muzzle = blob(cx, 308, 30, 17, 5, 0.04, 14)
    chest = C((cx - 40, 276), (cx - 76, 300), (cx - 104, 340), (cx - 116, 400), (cx + 162, 400), (cx + 156, 340), (cx + 136, 300),
              (cx + 104, 286), (cx + 70, 292), (cx + 40, 276))
    tuft = [L((cx - 16, 198), (cx - 8, 212), (cx - 16, 226)), L((cx + 2, 194), (cx + 6, 210), (cx, 226)), L((cx + 18, 198), (cx + 12, 212), (cx + 20, 224))]
    al, ep = P["Aldebaran"], P["epsilon"]
    lids = [L((al[0] - 11, al[1] - 3), (al[0], al[1] - 10), (al[0] + 10, al[1] - 4)), L((ep[0] - 10, ep[1] - 4), (ep[0], ep[1] - 10), (ep[0] + 11, ep[1] - 3))]
    nost = [L((cx - 14, 302), (cx - 8, 309), (cx - 14, 316)), L((cx + 14, 302), (cx + 8, 309), (cx + 14, 316))]
    folds = [L((cx - 52, 312), (cx - 38, 340), (cx - 30, 384)), L((cx + 52, 312), (cx + 40, 344), (cx + 34, 384)), L((cx + 100, 310), (cx + 110, 350), (cx + 120, 392))]
    return dict(fills=[chest, earL, earR, hornL, hornR, face, muzzle], lines=[(chest, 2.0, 0.55), earL, earR, (hornL, 2.6), (hornR, 2.6), (face, 2.6), (muzzle, 2)],
                details=[*rings, *tuft, *lids, *nost, *folds], angle=-80, fade=(330, 400))


def fig_gemini(P):
    pl, cs = P["Pollux"], P["Castor"]
    wx, wy = P["Wasat"]
    io = P["iota"]
    fills, lines, det = [], [], []
    # Pollux, the left twin: a lunging stance (knees at Mekbuda and lambda), one hand raised to kappa
    hP = (pl[0] - 4, pl[1] - 6)
    tunicP = C((hP[0] - 22, hP[1] + 32), (hP[0] + 20, hP[1] + 32), (hP[0] + 18, hP[1] + 66), (wx + 26, wy + 6), (wx + 30, wy + 46),
               (wx + 8, wy + 52), (wx - 14, wy + 50), (wx - 34, wy + 44), (wx - 22, wy + 4), (hP[0] - 30, hP[1] + 66))
    legP = [tube([(wx + 10, wy + 44), P["Mekbuda"], (P["Alhena"][0], P["Alhena"][1] - 8)], 16, 10),
            tube([(wx - 16, wy + 40), (P["lambda"][0] + 4, P["lambda"][1] - 2), (P["xi"][0], P["xi"][1] - 8)], 16, 10)]
    armP = [tube([(hP[0] - 20, hP[1] + 38), (hP[0] - 46, hP[1] + 58), (P["kappa"][0] - 4, P["kappa"][1] + 6)], 12, 8),
            tube([(hP[0] + 16, hP[1] + 38), (io[0] - 10, io[1] - 6), io], 12, 8)]
    # Castor, the right twin: standing tall, lyre in his outstretched hand at theta
    hC = (cs[0] - 2, cs[1] - 6)
    mx, my = P["Mebsuta"]
    tunicC = C((hC[0] - 22, hC[1] + 32), (hC[0] + 22, hC[1] + 32), (hC[0] + 26, hC[1] + 80), (mx + 26, my - 22), (mx + 30, my),
               (mx + 4, my + 4), (mx - 22, my + 2), (mx - 30, my - 20), (hC[0] - 26, hC[1] + 80))
    legC = [tube([(mx + 12, my - 4), (P["Tejat"][0] + 2, P["Tejat"][1] - 6), (P["Propus"][0] - 4, P["Propus"][1] - 6)], 16, 10),
            tube([(mx - 14, my - 4), (P["nu"][0] + 6, P["nu"][1] - 34), (P["nu"][0], P["nu"][1] - 8)], 16, 10)]
    th = P["theta"]
    armC = [tube([(hC[0] + 20, hC[1] + 38), (hC[0] + 50, hC[1] + 70), (th[0] - 14, th[1] + 4)], 12, 8),
            tube([(hC[0] - 18, hC[1] + 38), (io[0] + 10, io[1] + 4), io], 12, 8)]
    feet = [blob(P["Alhena"][0] - 2, P["Alhena"][1] - 4, 9, 5, 1, 0.1, 8), blob(P["xi"][0] - 4, P["xi"][1] - 4, 9, 5, 2, 0.1, 8),
            blob(P["Propus"][0] + 2, P["Propus"][1] - 2, 9, 5, 3, 0.1, 8), blob(P["nu"][0] - 4, P["nu"][1] - 4, 9, 5, 4, 0.1, 8)]
    heads = []
    for (hx, hy), sg in ((hP, -1), (hC, 1)):
        hair = scallop(hx - sg * 1, hy - 6, 19, 15, 9, 0.12, int(hx))
        head = blob(hx, hy + 2, 15, 17, int(hx), 0.03, 14)
        heads += [hair, head]
        det.append(L((hx - 6, hy + 2), (hx - 2, hy + 4)))
        det.append(L((hx + 3, hy + 2), (hx + 7, hy + 4)))
        det.append(L((hx - 4, hy + 12), (hx + 1, hy + 14), (hx + 6, hy + 12)))
    lyre = [L((th[0] - 6, th[1] + 26), (th[0] - 16, th[1] + 6), (th[0] - 12, th[1] - 18), (th[0] - 4, th[1] - 24)),
            L((th[0] + 14, th[1] + 26), (th[0] + 22, th[1] + 6), (th[0] + 18, th[1] - 18), (th[0] + 10, th[1] - 24)),
            L((th[0] - 12, th[1] - 12), (th[0] + 4, th[1] - 16), (th[0] + 18, th[1] - 12)), L((th[0] - 8, th[1] + 26), (th[0] + 16, th[1] + 26))]
    strings = [L((th[0] - 4 + 6 * i, th[1] - 13), (th[0] - 4 + 6 * i, th[1] + 25)) for i in range(3)]
    belts = [L((wx - 24, wy + 2), (wx + 2, wy + 10), (wx + 26, wy + 2)), L((mx - 26, my - 52), (mx + 2, my - 46), (mx + 28, my - 54))]
    folds = [L((hP[0] - 12, hP[1] + 50), (wx - 10, wy + 14), (wx - 16, wy + 46)), L((hP[0] + 8, hP[1] + 52), (wx + 12, wy + 16), (wx + 14, wy + 48)),
             L((hC[0] - 8, hC[1] + 56), (mx - 10, my - 40), (mx - 12, my)), L((hC[0] + 12, hC[1] + 54), (mx + 12, my - 40), (mx + 14, my))]
    fills = [*legP, *legC, *feet, tunicP, tunicC, *armP, *armC, *heads]
    lines = [*[(d, 2.0) for d in legP + legC + feet], (tunicP, 2.4), (tunicC, 2.4), *[(d, 2.0) for d in armP + armC], *[(d, 2.2) for d in heads]]
    det += [*belts, *folds, *[(d, 2.2) for d in lyre], *[(d, 1.2) for d in strings]]
    return dict(fills=fills, lines=lines, details=det, angle=-80)


def claw(cx, cy, ang, s):
    """Crab / scorpion pincer pointing at ang degrees: swollen hand and two curved fingers."""
    a = math.radians(ang)

    def T(x, y):
        return (cx + (x * math.cos(a) - y * math.sin(a)) * s, cy + (x * math.sin(a) + y * math.cos(a)) * s)
    hand = C(T(-0.55, 0), T(-0.2, -0.36), T(0.3, -0.34), T(0.55, -0.1), T(0.52, 0.18), T(0.2, 0.36), T(-0.3, 0.3))
    top = C(T(0.4, -0.3), T(0.85, -0.42), T(1.2, -0.22), T(1.28, 0.05), T(1.02, -0.08), T(0.6, -0.06))
    bot = C(T(0.48, 0.12), T(0.84, 0.3), T(1.06, 0.2), T(0.86, 0.08), T(0.56, 0.02))
    return hand, top, bot


def fig_cancer(P):
    cx, cy = 318, 252
    shell = C((cx - 66, cy - 8), (cx - 54, cy - 36), (cx - 20, cy - 50), (cx + 20, cy - 50), (cx + 54, cy - 36), (cx + 66, cy - 8),
              (cx + 54, cy + 26), (cx + 22, cy + 42), (cx - 22, cy + 42), (cx - 54, cy + 26))
    ax, ay = P["Altarf"]
    bx, by = P["Acubens"]
    armL = tube([(cx - 46, cy - 30), (cx - 80, cy - 62), (ax + 2, ay + 64)], 15, 11)
    armR = tube([(cx + 46, cy - 30), (cx + 66, cy - 66), (bx, by + 54)], 15, 11)
    cL = claw(ax + 2, ay + 50, -95, 46)
    cR = claw(bx, by + 40, -85, 44)
    legs, fills = [], []
    for sg in (-1, 1):
        for k in range(4):
            y0 = cy - 10 + k * 15
            x0 = cx + sg * (58 - k * 4)
            kx, ky = x0 + sg * (34 + k * 2), y0 - 16 + k * 6
            tx, ty = kx + sg * (22 - k * 2), ky + 34 + k * 4
            legs.append(tube([(x0, y0), (kx, ky), (tx, ty)], 9, 4))
    eyes = [tube([(cx - 14, cy - 46), (cx - 18, cy - 64)], 5, 4), tube([(cx + 14, cy - 46), (cx + 18, cy - 64)], 5, 4)]
    eyeb = [blob(cx - 18, cy - 68, 5.5, 5.5, 1, 0.1, 8), blob(cx + 18, cy - 68, 5.5, 5.5, 2, 0.1, 8)]
    ridges = [L((cx - 46, cy - 18), (cx, cy - 30), (cx + 46, cy - 18)), L((cx - 40, cy + 12), (cx, cy + 22), (cx + 40, cy + 12)),
              L((cx - 30, cy - 40), (cx - 40, cy - 8), (cx - 30, cy + 30)), L((cx + 30, cy - 40), (cx + 40, cy - 8), (cx + 30, cy + 30))]
    mouth = L((cx - 10, cy - 50), (cx, cy - 46), (cx + 10, cy - 50))
    return dict(fills=[*legs, armL, armR, *cL, *cR, shell, *eyes, *eyeb], lines=[*[(d, 1.8) for d in legs], armL, armR, *[(d, 2.2) for d in cL + cR],
                                                                                  (shell, 2.6), *eyes, *eyeb],
                details=[*ridges, mouth], shade=[C((cx - 70, cy + 10), (cx + 70, cy + 10), (cx + 70, cy + 60), (cx - 70, cy + 60))], angle=-90)


def fig_leo(P):
    hx, hy = 452, 202
    mane = scallop(hx - 4, hy, 64, 62, 13, 0.14, 5)
    mane_in = scallop(hx + 4, hy + 2, 44, 44, 11, 0.12, 6)
    rnd = random.Random(5)
    locks = []
    for i in range(18):
        a = 2 * math.pi * i / 18 + rnd.uniform(-0.1, 0.1)
        r0, r1 = 40, 62
        locks.append(L((hx - 4 + r0 * math.cos(a), hy + r0 * math.sin(a)),
                       (hx - 4 + (r0 + r1) / 2 * math.cos(a + 0.1), hy + (r0 + r1) / 2 * math.sin(a + 0.1)),
                       (hx - 4 + r1 * math.cos(a + 0.05), hy + r1 * math.sin(a + 0.05))))
    fx, fy = hx + 18, hy + 4
    face = C((fx - 22, fy - 30), (fx + 6, fy - 34), (fx + 26, fy - 22), (fx + 36, fy - 4), (fx + 46, fy + 10), (fx + 42, fy + 22),
             (fx + 26, fy + 34), (fx + 4, fy + 40), (fx - 18, fy + 30), (fx - 30, fy + 8), (fx - 30, fy - 14))
    ears = [blob(fx - 16, fy - 32, 9, 8, 3, 0.1, 8), blob(fx + 12, fy - 36, 8, 7, 4, 0.1, 8)]
    body_d = C((404, 222), (350, 212), (290, 212), (238, 218), (204, 232), (188, 258), (194, 290), (224, 304), (262, 300), (300, 290),
               (340, 292), (382, 304), (418, 300), (440, 272), (436, 238))
    thigh = blob(212, 280, 30, 32, 9, 0.04, 14, rot=10)
    hind = tube([(212, 300), (200, 334), (210, 360)], 22, 13)
    hind2 = tube([(250, 288), (254, 326), (248, 360)], 18, 12)
    fore = tube([(406, 272), (414, 316), (420, 360)], 26, 14)
    fore2 = tube([(378, 290), (380, 326), (374, 360)], 18, 12)
    paws = [blob(x + 7, 362, 14, 6, int(x), 0.1, 10) for x in (210, 248, 374, 420)]
    dx, dy = P["Denebola"]
    tail = tube([(192, 250), (160, 260), (132, 270), (dx + 14, dy - 8)], 9, 5)
    tuft = blob(dx + 4, dy + 2, 10, 14, 6, 0.25, 10, rot=40)
    eye = L((fx + 6, fy - 12), (fx + 14, fy - 16), (fx + 22, fy - 12))
    nose = C((fx + 38, fy + 2), (fx + 48, fy + 4), (fx + 43, fy + 13))
    mouth = L((fx + 43, fy + 14), (fx + 36, fy + 24), (fx + 22, fy + 25))
    whisk = [L((fx + 30, fy + 14), (fx + 12, fy + 12)), L((fx + 30, fy + 18), (fx + 14, fy + 24))]
    return dict(fills=[tail, tuft, hind2, fore2, body_d, thigh, hind, fore, mane, mane_in, *ears, face, *paws],
                lines=[(tail, 1.8), tuft, (hind2, 2.0), (fore2, 2.0), (body_d, 2.4), (thigh, 2.0), (hind, 2.2), (fore, 2.2),
                       (mane, 2.4), (mane_in, 1.6, 0.6), *ears, (face, 2.4), *paws],
                details=[*locks, (eye, 2.2), nose, mouth, *whisk], shade=[C((180, 292), (440, 292), (440, 380), (180, 380))], angle=-5)


def wheat_ear(x0, y0, x1, y1, n=6, size=11):
    """Wheat ear along a stalk segment: paired grains pointing to the tip, plus awns."""
    ang = math.atan2(y1 - y0, x1 - x0)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    grains, awns = [], []
    for i in range(n):
        t = i / (n - 1)
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        sz = size * (1 - 0.35 * t)
        for sg in (-1, 1):
            tip = (bx + dx * sz * 1.1 + nx * sg * sz * 0.7, by + dy * sz * 1.1 + ny * sg * sz * 0.7)
            grains.append(C((bx, by), (bx + dx * sz * 0.4 + nx * sg * sz * 0.55, by + dy * sz * 0.4 + ny * sg * sz * 0.55), tip,
                            (bx + dx * sz * 0.7 + nx * sg * sz * 0.1, by + dy * sz * 0.7 + ny * sg * sz * 0.1)))
            awns.append(L(tip, (tip[0] + dx * sz * 1.2 + nx * sg * sz * 0.5, tip[1] + dy * sz * 1.2 + ny * sg * sz * 0.5)))
    return grains, awns


def fig_virgo(P):
    hx, hy = P["Zavijava"][0], P["Zavijava"][1] + 2
    head = C((hx - 15, hy - 4), (hx - 10, hy - 16), (hx + 4, hy - 19), (hx + 14, hy - 12), (hx + 17, hy - 2), (hx + 23, hy + 5),
             (hx + 17, hy + 8), (hx + 17, hy + 13), (hx + 8, hy + 19), (hx - 6, hy + 17), (hx - 14, hy + 10))
    hair = C((hx - 8, hy - 19), (hx - 22, hy - 12), (hx - 26, hy + 10), (hx - 30, hy + 44), (hx - 40, hy + 80), (hx - 34, hy + 110),
             (hx - 22, hy + 90), (hx - 14, hy + 56), (hx - 10, hy + 26), (hx - 4, hy + 10))
    gown = C((hx - 18, hy + 34), (hx + 26, hy + 34), (hx + 36, hy + 70), (hx + 32, hy + 104), (hx + 44, hy + 150), (hx + 62, hy + 200),
             (hx + 76, hy + 250), (hx + 84, hy + 286), (hx + 30, hy + 294), (hx - 24, hy + 296), (hx - 44, hy + 284), (hx - 30, hy + 230),
             (hx - 18, hy + 170), (hx - 8, hy + 128), (hx - 16, hy + 100), (hx - 24, hy + 66))
    wl = C((hx - 10, hy + 40), (hx - 40, hy + 22), (hx - 72, hy - 2), (hx - 94, hy - 14), (hx - 88, hy + 10), (hx - 100, hy + 28),
           (hx - 80, hy + 40), (hx - 92, hy + 60), (hx - 62, hy + 66), (hx - 34, hy + 64))
    wr = C((hx + 28, hy + 40), (hx + 58, hy + 22), (hx + 90, hy - 2), (hx + 112, hy - 12), (hx + 106, hy + 12), (hx + 118, hy + 30),
           (hx + 98, hy + 42), (hx + 108, hy + 62), (hx + 78, hy + 68), (hx + 50, hy + 64))
    feathers = [L((hx - 30 - 14 * i, hy + 30 + 3 * i), (hx - 40 - 14 * i, hy + 56 - 2 * i)) for i in range(4)] + \
               [L((hx + 46 + 14 * i, hy + 30 + 3 * i), (hx + 56 + 14 * i, hy + 56 - 2 * i)) for i in range(4)]
    sx, sy = P["Spica"]
    vx, vy = P["Vindemiatrix"]
    armR = tube([(hx + 26, hy + 42), (hx + 46, hy + 96), (sx - 12, sy - 18)], 12, 8)
    handR = blob(sx - 10, sy - 16, 7, 7, 3, 0.1, 8)
    armL = tube([(hx - 16, hy + 44), (hx - 30, hy + 92), (vx + 14, vy - 2)], 12, 8)
    handL = blob(vx + 10, vy - 2, 7, 7, 4, 0.1, 8)
    grains, awns = wheat_ear(sx - 6, sy - 8, sx + 22, sy + 26, 5, 10)
    stalk = L((sx - 22, sy - 30), (sx - 12, sy - 18), (sx - 4, sy - 6))
    sprig = [L((vx + 8, vy), (vx - 10, vy + 14), (vx - 26, vy + 34))] + [L((vx - 4 - 7 * i, vy + 8 + 9 * i), (vx - 16 - 7 * i, vy + 2 + 9 * i)) for i in range(3)] + \
            [L((vx - 4 - 7 * i, vy + 8 + 9 * i), (vx + 4 - 7 * i, vy + 18 + 9 * i)) for i in range(3)]
    sash = L((hx - 14, hy + 104), (hx + 6, hy + 112), (hx + 32, hy + 100))
    folds = [L((hx + 4, hy + 116), (hx + 10, hy + 200), (hx + 6, hy + 290)), L((hx + 22, hy + 112), (hx + 40, hy + 200), (hx + 50, hy + 288)),
             L((hx - 10, hy + 120), (hx - 14, hy + 210), (hx - 26, hy + 286)), L((hx + 40, hy + 160), (hx + 62, hy + 230), (hx + 72, hy + 282))]
    neckline = L((hx - 12, hy + 38), (hx + 4, hy + 50), (hx + 22, hy + 38))
    eye = L((hx + 5, hy - 4), (hx + 10, hy - 6), (hx + 15, hy - 3))
    circlet = [spark_d(hx - 6 + 8 * i, hy - 22 + abs(i - 1) * 2, 3.5) for i in range(3)]
    return dict(fills=[wl, wr, hair, gown, head, armR, armL, handR, handL, *grains],
                lines=[(wl, 2.0), (wr, 2.0), (hair, 2.0), (gown, 2.4), (head, 2.2), (armR, 2.0), (armL, 2.0), handR, handL, *[(g, 1.4) for g in grains]],
                details=[*feathers, *folds, sash, neckline, (stalk, 2.4), *[(a, 1.2) for a in awns], *sprig, eye, *circlet], angle=-90)


def fig_libra(P):
    gx, gy = P["gamma"]
    zx, zy = P["Zubenelgenubi"]
    cx = (gx + zx) / 2
    by = (gy + zy) / 2
    beam = tube([(gx - 8, gy), (cx, by - 6), (zx + 8, zy)], 9, 9)
    column = C((cx - 7, by + 6), (cx + 7, by + 6), (cx + 9, 350), (cx - 9, 350))
    base = C((cx - 54, 384), (cx - 40, 362), (cx - 14, 352), (cx + 14, 352), (cx + 40, 362), (cx + 54, 384))
    knob = blob(cx, by - 12, 13, 13, 2, 0.03, 14)
    finial = C((cx, by - 52), (cx + 7, by - 34), (cx + 3, by - 24), (cx - 3, by - 24), (cx - 7, by - 34))
    bands = [L((cx - 10, 260), (cx + 10, 260)), L((cx - 10, 300), (cx + 10, 300)), L((cx - 12, 340), (cx + 12, 340))]
    out_f, out_l, chains = [], [], []
    for ex, ey in ((gx, gy), (zx, zy)):
        pan = C((ex - 46, 292), (ex + 46, 292), (ex + 34, 312), (ex, 320), (ex - 34, 312))
        out_f.append(pan)
        out_l.append((pan, 2.4))
        rim = L((ex - 46, 292), (ex, 286), (ex + 46, 292))
        out_l.append((rim, 1.8))
        for sx in (-40, 0, 40):
            chains.append((f"M {_f(ex)} {_f(ey + 8)} L {_f(ex + sx)} 290", 1.6))
        out_f.append(blob(ex, ey + 2, 7, 7, int(ex), 0.1, 8))
    scroll = [L((gx - 8, gy), (gx - 22, gy - 4), (gx - 24, gy - 16), (gx - 14, gy - 18)), L((zx + 8, zy), (zx + 22, zy - 4), (zx + 24, zy - 16), (zx + 14, zy - 18))]
    return dict(fills=[column, base, beam, knob, finial, *out_f], lines=[(column, 2.2), (base, 2.4), (beam, 2.2), (knob, 2.2), finial, *out_l],
                details=[*chains, *bands, *[(s, 2.0) for s in scroll]], angle=-90)


def fig_scorpio(P):
    path = [(408, 158), P["sigma"], P["Antares"], P["tau"], (306, 236), P["epsilon"], P["mu"], P["zeta"], P["eta"], P["Sargas"],
            P["iota"], P["kappa"], (P["Shaula"][0] - 4, P["Shaula"][1] + 6)]
    segs, fills = [], []
    for i in range(len(path) - 1):
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        w = 34 - i * 1.6 if i < 5 else 17 - (i - 5) * 0.8
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ln = math.hypot(x1 - x0, y1 - y0)
        segs.append(blob(mx, my, ln * 0.58, w / 2, 40 + i, 0.03, 12, rot=math.degrees(math.atan2(y1 - y0, x1 - x0))))
    head = C((404, 128), (424, 116), (444, 124), (452, 150), (446, 178), (426, 192), (404, 186), (396, 158))
    ux, uy = P["Acrab"]
    rx_, ry_ = P["rho"]
    armU = tube([(436, 128), (452, 110), (ux + 26, uy - 2)], 11, 8)
    armD = tube([(442, 182), (460, 202), (rx_ + 26, ry_ + 8)], 11, 8)
    cU = claw(ux + 30, uy - 6, -40, 34)
    cD = claw(rx_ + 30, ry_ + 10, 40, 34)
    sx, sy = P["Shaula"]
    sting = C((sx - 6, sy + 8), (sx + 2, sy - 6), (sx + 18, sy - 14), (sx + 30, sy - 12), (sx + 14, sy - 4), (sx + 6, sy + 10))
    legs = []
    for k in range(4):
        bx, by = 396 - k * 18, 160 + k * 14
        legs.append(tube([(bx, by - 8), (bx + 6, by - 40), (bx - 14, by - 58)], 7, 3.5))
        legs.append(tube([(bx + 8, by + 10), (bx + 30, by + 34), (bx + 26, by + 62)], 7, 3.5))
    eyes = [blob(436, 140, 3, 3, 1, 0.1, 6), blob(440, 168, 3, 3, 2, 0.1, 6)]
    return dict(fills=[*legs, armU, armD, *cU, *cD, *segs, head, sting], lines=[*[(d, 1.6) for d in legs], armU, armD, *[(d, 2.0) for d in cU + cD],
                                                                             *[(d, 2.0) for d in segs], (head, 2.4), (sting, 2.2)],
                details=eyes, angle=-60)


def fig_sagittarius(P):
    bx, by = P["Kaus Borealis"]
    gx, gy = P["Kaus Media"]
    ax, ay = P["Kaus Australis"]
    tx, ty = P["Alnasl"]
    # recurve bow through the three Kaus stars, string drawn back to the archer's hand, arrow tipped by Alnasl
    limb = tube([(bx - 10, by - 16), (bx - 2, by - 2), (gx - 4, gy - 40), (gx + 4, gy), (gx - 2, gy + 40), (ax - 2, ay + 2), (ax - 12, ay + 14)], 6, 6)
    grip = blob(gx + 2, gy, 8, 14, 3, 0.05, 10)
    nock = (274, 240)
    string = L((bx - 4, by - 8), nock, (ax - 6, ay + 8))
    shaft = L((nock[0] - 6, nock[1] - 0.5), (tx - 12, ty - 1))
    head_ = C((tx + 6, ty), (tx - 16, ty - 9), (tx - 11, ty), (tx - 16, ty + 9))
    ang = math.atan2(ty - nock[1], tx - nock[0])
    ca, sa = math.cos(ang), math.sin(ang)

    def A(u, v):
        return (nock[0] + u * ca - v * sa, nock[1] + u * sa + v * ca)
    fl = [C(A(-4, 0), A(4, -11), A(30, -11), A(24, 0)), C(A(-4, 0), A(4, 11), A(30, 11), A(24, 0))]
    # the centaur archer: a man's torso drawing the bow above a horse's body
    hx, hy = 290, 166
    headc = C((hx - 12, hy - 8), (hx - 4, hy - 16), (hx + 8, hy - 15), (hx + 14, hy - 6), (hx + 19, hy + 2), (hx + 14, hy + 5),
              (hx + 13, hy + 12), (hx + 4, hy + 18), (hx - 8, hy + 16), (hx - 14, hy + 6))
    hair = C((hx - 10, hy - 14), (hx + 4, hy - 20), (hx + 14, hy - 14), (hx + 2, hy - 10), (hx - 6, hy - 2), (hx - 10, hy + 12),
             (hx - 22, hy + 26), (hx - 20, hy + 6))
    band = L((hx - 12, hy - 8), (hx + 2, hy - 13), (hx + 14, hy - 9))
    torso = C((270, 190), (302, 188), (310, 216), (306, 248), (300, 278), (262, 282), (256, 250), (258, 218))
    pecs = [L((276, 214), (288, 222), (300, 214)), L((282, 244), (284, 262))]
    arm_front = tube([(304, 198), (334, 228), (gx - 8, gy - 2)], 13, 8)
    arm_back = tube([(270, 198), (240, 218), (nock[0] - 4, nock[1] - 2)], 13, 8)
    quiver = C((238, 176), (250, 172), (240, 232), (228, 234))
    q_arrows = [L((242, 176), (246, 160)), L((246, 176), (252, 162)), L((238, 176), (238, 162))]
    cape = C((272, 192), (246, 206), (220, 236), (204, 268), (226, 262), (240, 270), (256, 246), (262, 216))
    horse = C((298, 272), (290, 306), (252, 324), (196, 326), (156, 318), (138, 296), (146, 270), (180, 262), (230, 266), (262, 272))
    legs_h = [tube([(288, 302), (300, 334), (292, 372)], 14, 8), tube([(266, 316), (266, 346), (254, 372)], 12, 8),
              tube([(176, 312), (162, 340), (170, 372)], 16, 8), tube([(154, 304), (136, 334), (144, 370)], 13, 8)]
    hooves = [blob(x, 374, 7, 4, int(x), 0.1, 8) for x in (294, 254, 172, 146)]
    tail = C((144, 280), (118, 292), (104, 322), (112, 352), (122, 326), (138, 300))
    tail_l = [L((138, 288), (116, 312), (110, 340)), L((134, 296), (120, 322), (118, 346))]
    eye = L((hx + 5, hy - 3), (hx + 10, hy - 4))
    return dict(fills=[tail, *legs_h, horse, cape, quiver, torso, arm_back, hair, headc, arm_front, limb, grip, head_, *fl],
                lines=[(tail, 1.8), *[(d, 1.8) for d in legs_h], (horse, 2.2), (cape, 1.8), (quiver, 1.8), (torso, 2.2), (arm_back, 2.0),
                       (hair, 1.8), (headc, 2.2), (arm_front, 2.0), (limb, 2.6), grip, head_, *[(f, 1.8) for f in fl]],
                details=[(string, 1.6, 0.9), (shaft, 3.0, 0.95), *hooves, *q_arrows, *pecs, band, eye, *tail_l], angle=-20)


def fig_capricorn(P):
    head = C((436, 162), (444, 140), (462, 128), (480, 132), (492, 150), (500, 174), (494, 186), (476, 182), (454, 176))
    horns = tube([(452, 136), (440, 112), (418, 98), (396, 100), (384, 112)], 13, 4)
    horn2 = tube([(462, 132), (456, 108), (436, 90), (414, 88)], 10, 3)
    ear = C((446, 152), (420, 152), (408, 164), (432, 166))
    beard = C((488, 184), (496, 204), (490, 216), (482, 198))
    torso = C((446, 166), (414, 192), (370, 206), (334, 216), (322, 250), (344, 276), (390, 286), (430, 262), (452, 226), (458, 192))
    tailpts = [(350, 236), (300, 270), (246, 290), (196, 280), (160, 250), (136, 218), (126, 200)]
    tail = tube(tailpts, 62, 12)
    fin = C((132, 204), (116, 180), (96, 156), (104, 184), (88, 208), (112, 206), (98, 232), (128, 216))
    ruff = C((338, 214), (318, 228), (322, 244), (310, 258), (326, 266), (318, 282), (344, 278))
    px_, py_ = P["psi"]
    ox, oy = P["omega"]
    leg1 = tube([(414, 270), (392, 298), (px_ + 8, py_ - 4), (px_ - 8, py_ + 4)], 19, 9)
    leg2 = tube([(388, 280), (364, 312), (ox + 8, oy - 6), (ox - 8, oy + 2)], 17, 9)
    hooves = [blob(px_ - 10, py_ + 6, 7, 5, 1, 0.1, 8), blob(ox - 10, oy + 4, 7, 5, 2, 0.1, 8)]
    scales = []
    for i, (x, y) in enumerate(tailpts[1:5]):
        for off in (-12, 0, 12):
            w = 9 - i
            scales.append(L((x - w + 4, y + off - w * 0.6), (x + 4, y + off + 2), (x + w + 4, y + off - w * 0.6)))
    finlines = [L((128, 206), (106, 180)), L((124, 210), (98, 208)), L((128, 214), (106, 228))]
    eye = L((466, 150), (473, 147), (480, 152))
    fur = [L((420, 196), (410, 220)), L((432, 206), (424, 232)), L((404, 206), (396, 230)), L((388, 214), (380, 238))]
    return dict(fills=[leg2, tail, fin, torso, ruff, leg1, horns, horn2, ear, head, beard],
                lines=[(leg2, 2.0), (tail, 2.4), (fin, 2.0), (torso, 2.4), (ruff, 1.8), (leg1, 2.0), (horns, 2.2), (horn2, 2.0), ear, (head, 2.4), beard],
                details=[*scales, *finlines, (eye, 2.0), *hooves, *fur], angle=-15)


def fig_aquarius(P):
    ux, uy = 236, 150
    a = math.radians(-62)

    def T(x, y):
        return (ux + (x * math.cos(a) - y * math.sin(a)) * 50, uy + (x * math.sin(a) + y * math.cos(a)) * 50)
    urn = C(T(0.32, -1.0), T(0.3, -0.75), T(0.62, -0.4), T(0.7, 0.05), T(0.52, 0.5), T(0.2, 0.82), T(0.24, 1.0), T(-0.24, 1.0), T(-0.2, 0.82),
            T(-0.52, 0.5), T(-0.7, 0.05), T(-0.62, -0.4), T(-0.3, -0.75), T(-0.32, -1.0))
    lip = C(T(-0.42, -0.98), T(0.42, -0.98), T(0.38, -1.14), T(-0.38, -1.14))
    foot_ = C(T(-0.34, 0.98), T(0.34, 0.98), T(0.4, 1.12), T(-0.4, 1.12))
    handle = L(T(0.36, -0.7), T(0.9, -0.62), T(0.86, -0.2), T(0.62, -0.1))
    bands = [L(T(-0.66, -0.2), T(0, -0.14), T(0.66, -0.2)), L(T(-0.6, 0.3), T(0, 0.36), T(0.6, 0.3))]
    wave = L(*[T(-0.6 + 0.1 * i, 0.05 + (0.06 if i % 2 else -0.06)) for i in range(13)])
    mouth = T(0, -1.12)
    w1, c1 = ribbon([mouth, (186, 168), P["lambda"], P["tau"], P["Skat"], (164, 314), P["88 Aqr"]], 13, 6, 3, 4, 1.3)
    w2, c2 = ribbon([mouth, (166, 166), P["phi"], P["psi"], (126, 280), P["98 Aqr"]], 11, 5, 4, 4, 1.5)
    pool = [L((84, 352), (108, 344), (132, 352), (156, 344), (180, 352), (202, 346)), L((96, 366), (120, 360), (144, 366), (168, 360), (188, 366))]
    drops = [blob(x, y, 3.2, 4.5, int(x), 0.1, 8) for x, y in ((206, 326), (98, 314), (192, 342), (124, 300))]
    hx, hy = 324, 110
    head = C((hx - 14, hy - 4), (hx - 12, hy - 16), (hx + 2, hy - 20), (hx + 14, hy - 12), (hx + 16, hy + 4), (hx + 10, hy + 18),
             (hx - 2, hy + 20), (hx - 12, hy + 14), (hx - 18, hy + 8), (hx - 16, hy + 2))
    hair = scallop(hx + 4, hy - 8, 16, 12, 8, 0.14, 4)
    sx, sy = P["Sadalsuud"]
    torso = C((296, 140), (322, 132), (350, 142), (364, 170), (sx + 6, sy + 14), (356, 232), (326, 232), (306, 206), (294, 172))
    th = P["theta"]
    arm1 = tube([(300, 148), (th[0] + 6, th[1] - 8), (250, 182)], 14, 9)
    alx, aly = P["Albali"]
    arm2 = tube([(348, 150), (400, 192), (alx - 8, aly - 4)], 13, 8)
    hand2 = blob(alx - 4, aly - 2, 7, 6, 5, 0.1, 8)
    ix, iy = P["iota"]
    thigh = tube([(346, 228), (ix + 30, iy - 8), (ix, iy)], 28, 17)
    shin = tube([(ix, iy), (ix - 2, iy + 40), (ix - 6, iy + 70)], 17, 11)
    foot = blob(ix - 14, iy + 72, 13, 6, 6, 0.1, 8)
    thigh2 = tube([(364, 230), (380, 290), (384, 334)], 26, 16)
    shin2 = tube([(384, 334), (420, 338), (452, 334)], 15, 10)
    skirt = C((322, 214), (370, 208), (382, 240), (396, 278), (372, 290), (344, 282), (318, 288), (300, 270), (310, 240))
    sash = C((298, 150), (316, 140), (370, 214), (356, 222))
    skirt_f = [L((334, 236), (330, 280)), L((352, 236), (356, 284)), L((368, 232), (382, 276))]
    return dict(fills=[w1, w2, thigh2, shin2, thigh, shin, foot, torso, skirt, sash, arm2, hand2, head, hair, urn, lip, foot_, arm1],
                lines=[(w1, 1.8, 0.7), (w2, 1.8, 0.7), (thigh2, 2.0), (shin2, 2.0), (thigh, 2.0), (shin, 2.0), foot, (torso, 2.2), (skirt, 2.0),
                       (sash, 1.6), (arm2, 2.0), hand2, (head, 2.2), (hair, 1.8), (urn, 2.6), lip, foot_, (arm1, 2.0)],
                details=[handle, *bands, (wave, 1.4), (c1, 1.2, 0.6), (c2, 1.2, 0.6), *pool, *drops, *skirt_f], angle=-60)


def fish_shape(cx, cy, length, ang, seed):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def T(x, y):
        return (cx + (x * ca - y * sa) * length, cy + (x * sa + y * ca) * length)
    body_d = C(T(0.5, 0.02), T(0.36, -0.2), T(0.06, -0.27), T(-0.26, -0.16), T(-0.42, 0), T(-0.26, 0.16), T(0.06, 0.27), T(0.36, 0.2))
    tail_d = C(T(-0.38, 0), T(-0.64, -0.24), T(-0.56, 0), T(-0.64, 0.24))
    fin_t = C(T(0.1, -0.24), T(-0.04, -0.42), T(-0.2, -0.36), T(-0.16, -0.18))
    fin_b = C(T(0.0, 0.24), T(-0.1, 0.36), T(-0.2, 0.2))
    gill = L(T(0.28, -0.17), T(0.22, 0), T(0.28, 0.17))
    eye = blob(*T(0.38, -0.05), length * 0.03, length * 0.03, seed, 0.1, 8)
    sc = [L(T(x - 0.06, -0.12 + dy), T(x, dy), T(x - 0.06, 0.12 + dy)) for x in (0.14, 0.02, -0.1, -0.22) for dy in (0,)]
    fins = [L(T(-0.42, 0), T(-0.6, -0.16)), L(T(-0.42, 0), T(-0.6, 0.16)), L(T(-0.42, 0), T(-0.6, 0))]
    return [fin_t, fin_b, tail_d, body_d], [gill, *sc, *fins], eye, T


def fig_pisces(P):
    nf, nd, ne, Tn = fish_shape(224, 150, 136, -86, 1)
    wf, wd, we, Tw = fish_shape(462, 350, 128, 6, 2)
    ax, ay = P["Alrescha"]
    tn = Tn(-0.5, 0)
    tw = Tw(-0.5, 0)
    cords = []
    for path in ([tn, P["Alpherg"], P["omicron"], (ax + 4, ay - 6)], [tw, P["omega"], P["delta"], P["epsilon"], P["zeta"], P["mu"], P["nu"], (ax + 6, ay - 2)]):
        for off in (-2.5, 2.5):
            cords.append((L(*[(x, y + off) for x, y in path]), 1.6, 0.8))
    knot = [C((ax - 2, ay - 4), (ax - 22, ay - 16), (ax - 26, ay - 2), (ax - 6, ay + 2)), C((ax + 2, ay + 4), (ax - 4, ay + 26), (ax + 10, ay + 28), (ax + 8, ay + 6))]
    return dict(fills=[*nf, *wf, *knot], lines=[*[(d, 2.2) for d in nf + wf], *knot],
                details=[*nd, *wd, (ne, 2.2), (we, 2.2), *cords], angle=-20)


def scallop(cx, cy, rx, ry, n, amp, seed=1):
    """Fluffy outline: an ellipse with n soft bumps (fleece, clouds, manes)."""
    rnd = random.Random(seed)
    pts = []
    m = n * 4
    for i in range(m):
        a = 2 * math.pi * i / m
        k = 1 + amp * abs(math.sin(a * n / 2)) + rnd.uniform(-0.01, 0.01)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return smooth_closed(pts)


def ribbon(pts, w0, w1, seed, amp=4, freq=1.6):
    """A wavy tapering stream (water) along a path: densified, gently sinuous, as a closed shape and its centre line."""
    rnd = random.Random(seed)
    dense = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for t in [j / 5 for j in range(5)]:
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    dense.append(pts[-1])
    out = []
    ph = rnd.uniform(0, 6)
    for i, (x, y) in enumerate(dense):
        a = dense[min(i + 1, len(dense) - 1)]
        b = dense[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        o = amp * math.sin(i * freq + ph)
        out.append((x + nx * o, y + ny * o))
    return tube(out, w0, w1), L(*out)


def spark_d(x, y, r):
    pts = []
    for i in range(4):
        a = math.radians(-90 + 90 * i)
        b = math.radians(-45 + 90 * i)
        pts.append(f"{_f(x + r * math.cos(a))} {_f(y + r * math.sin(a))}")
        pts.append(f"{_f(x + r * 0.2 * math.cos(b))} {_f(y + r * 0.2 * math.sin(b))}")
    return f"M {pts[0]} L {' L '.join(pts[1:])} Z"


def zoom(d_pts, cx, cy, k):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in d_pts]


FIGS = dict(aries=fig_aries, taurus=fig_taurus, gemini=fig_gemini, cancer=fig_cancer, leo=fig_leo, virgo=fig_virgo, libra=fig_libra,
            scorpio=fig_scorpio, sagittarius=fig_sagittarius, capricorn=fig_capricorn, aquarius=fig_aquarius, pisces=fig_pisces)

META = {
    "aries": ("ARIES", "the Ram", "MAR 21 – APR 19"), "taurus": ("TAURUS", "the Bull", "APR 20 – MAY 20"),
    "gemini": ("GEMINI", "the Twins", "MAY 21 – JUN 20"), "cancer": ("CANCER", "the Crab", "JUN 21 – JUL 22"),
    "leo": ("LEO", "the Lion", "JUL 23 – AUG 22"), "virgo": ("VIRGO", "the Maiden", "AUG 23 – SEP 22"),
    "libra": ("LIBRA", "the Scales", "SEP 23 – OCT 22"), "scorpio": ("SCORPIO", "the Scorpion", "OCT 23 – NOV 21"),
    "sagittarius": ("SAGITTARIUS", "the Archer", "NOV 22 – DEC 21"), "capricorn": ("CAPRICORN", "the Sea-Goat", "DEC 22 – JAN 19"),
    "aquarius": ("AQUARIUS", "the Water-Bearer", "JAN 20 – FEB 18"), "pisces": ("PISCES", "the Fish", "FEB 19 – MAR 20"),
}

# per sign: nebulae (cx, cy, rx, ry, rot), milky-way band or None, alpha-star label (dx, dy, anchor)
LOOK = {
    "aries": ([(160, 120, 230, 120, -15), (470, 330, 200, 110, 25)], None, (0, -30, "middle")),
    "taurus": ([(460, 150, 210, 140, 20), (120, 330, 190, 120, -25)], (40, 80, 560, 330, 50), (-36, 44, "end")),
    "gemini": ([(130, 140, 200, 130, 25), (480, 300, 200, 130, -20)], (60, 20, 560, 380, 50), (-26, -16, "end")),
    "cancer": ([(140, 300, 210, 120, 20), (470, 160, 200, 130, -30)], None, (-34, 8, "end")),
    "leo": ([(420, 120, 240, 110, -10), (120, 160, 170, 100, 20)], None, (0, 50, "middle")),
    "virgo": ([(460, 140, 200, 120, 25), (130, 300, 200, 110, -20)], None, (22, 8, "start")),
    "libra": ([(300, 240, 260, 120, 0), (110, 120, 160, 100, 30)], None, (-20, -8, "end")),
    "scorpio": ([(200, 160, 220, 120, -30), (470, 330, 180, 100, 10)], (40, 560, 560, 40, 50), (-24, -12, "end")),
    "sagittarius": ([(450, 160, 200, 130, -20), (170, 160, 180, 110, 30)], (100, 600, 520, 0, 60), (22, 8, "start")),
    "capricorn": ([(150, 330, 200, 100, -15), (300, 110, 220, 90, 5)], None, (6, -22, "middle")),
    "aquarius": ([(440, 330, 200, 110, -20), (420, 110, 200, 90, 15)], None, (20, 26, "start")),
    "pisces": ([(360, 160, 240, 110, 10), (110, 180, 160, 100, -30)], None, (-20, 6, "end")),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def zodiac_constellation(slug, k):
    name, eng, dates = META[slug]
    el = SIGN_EL[slug]
    u = f"nsp-{slug}"
    P, T, mags = sky_map(slug)
    nebs, band, lab = LOOK[slug]
    out = [sky(u, 100 + k * 13, el, nebs, band, 110)]
    out.append(defs(lg(f"{u}-gm", [(0, "#FFFFFF"), (0.6, "#FFFFFF"), (0.7, "#000000"), (1, "#000000")], 0, 0, 0, 1),
                    f'<mask id="{u}-gk" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600"><rect width="600" height="600" fill="url(#{u}-gm)"/></mask>')
               + f'<g mask="url(#{u}-gk)">' + atlas_grid(f"{u}-ag", T, slug) + "</g>")
    fig = FIGS[slug](P)
    out.append(gold_figure(f"{u}-fg", fig.get("fills", ()), fig.get("lines", ()), 200 + k, fig.get("details", ()), fig.get("shade", ()),
                           fig.get("angle", -35), fade=fig.get("fade")))
    if slug == "cancer":
        out.append(beehive(f"{u}-m44", *P["Beehive"], 5))
    out.append(star_layer(f"{u}-cn", slug, P, mags, lab))
    if os.environ.get("NS_DEBUG"):
        out.append("".join(f'<text x="{_f(x + 5)}" y="{_f(y - 5)}" font-size="11" fill="#7FFFD4" font-family="sans-serif">{n}</text>' for n, (x, y) in P.items()))
    # type: brush-gold sign name, english name in italic, dates between two tiny glyphs
    size = fit_size(name, CINZEL, 70, 440, 8)
    out.append(bword(f"{u}-nm", 304, 466, name, CINZEL, size, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 300 + k, max_w=440, ls=8,
                     shadow="#05040E", sd=0.04, angle=-14))
    out.append(script(300, 508, eng, 30, CREAM, 360, ls=1, shadow="#05040E", sd=(1.5, 2)))
    dsz = fit_size(dates, MONO, 19, 300, 3)
    dw = measure(dates, MONO, dsz, 3)
    out.append(f'<text x="301.5" y="536" text-anchor="middle" {MONO} font-size="{dsz}" letter-spacing="3" fill="{GOLD_L}">{esc(dates)}</text>')
    for sg in (-1, 1):
        gx = 300 + sg * (dw / 2 + 24)
        out.append(gilded(f"{u}-tg{sg + 1}", glyph_d(slug, gx, 530, 10), 2.4, 1, shadow=False))
    out.append(finish(u, 400 + k))
    return "".join(out)


for _k, _slug in enumerate(META):
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
    name, eng, dates = META[sign]
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
    SP, _, mags = sky_map(sign)
    bx0, by0, bx1, by1 = CAT[sign]["box"]
    def T(p):
        return (cx + (p[0] - (bx0 + bx1) / 2) * 0.62, cy + 4 + (p[1] - (by0 + by1) / 2) * 0.62)
    poly = "".join(f'<path d="M {" L ".join(f"{_f(T(SP[q])[0])} {_f(T(SP[q])[1])}" for q in ln)}"/>' for ln in CAT[sign]["lines"])
    inner.append(f'<g fill="none" stroke="{GOLD_L}" stroke-width="1.6" opacity="0.35" stroke-linejoin="round">{poly}</g>')
    inner.append("".join(f'<circle cx="{_f(T(SP[n])[0])}" cy="{_f(T(SP[n])[1])}" r="{_f(star_r(m) * 0.5 + 0.6)}" fill="{STARC}" opacity="0.6"/>'
                         for n, m in mags.items()))
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


for _k, _slug in enumerate(META):
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
    out.append(sailboat_sil(f"{u}-boat", 468, 492, 0.95, 1004))
    out.append("".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="{GOLD_L}"/>' + glow(f"{u}-sl{i}", x, y, 7, GOLD_L, 0.6, 0.3)
                       for i, (x, y) in enumerate(((52, 437), (66, 439), (150, 440), (476, 434), (540, 437)))))
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
    out.append(night_cloud(f"{u}-c1", 150, 438, 190, 70, 1211, rim_side=1))
    out.append(night_cloud(f"{u}-c2", 476, 414, 160, 58, 1212, rim_side=-1))
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


def night_cloud(u, x, y, w, h, seed, base="#4E4C92", light="#B9B6EE", dark="#2A2860", rim=GOLD_L, rim_side=-1, op=1.0):
    """Painted night cloud: overlapping puffs graded from a moonlit top to a shadowed base, soft brushwork,
    a thin moonlit rim along the true top silhouette and faint shadow creases between the puffs."""
    rnd = random.Random(seed)
    puffs = []
    n = 6
    for i in range(n):
        t = i / (n - 1)
        r = h * (0.32 + 0.4 * math.sin(math.pi * t) ** 0.8) * rnd.uniform(0.85, 1.1)
        px = x - w / 2 + r * 0.8 + (w - r * 1.6) * t
        py = y - r * 0.55 - h * 0.1 * math.sin(math.pi * t)
        puffs.append((px, py, r))
    base_d = smooth_closed([(x - w / 2 + 6, y - h * 0.18), (x + w / 2 - 6, y - h * 0.18), (x + w / 2 - 2, y + 2), (x + w * 0.2, y + h * 0.14),
                            (x - w * 0.25, y + h * 0.12), (x - w / 2 + 2, y + 2)])
    shapes = [blob(px, py, r, r * 0.92, rnd.randrange(999), 0.04, 14) for px, py, r in puffs] + [base_d]
    gid = f"{u}-g"
    out = [f'<g opacity="{op}">', defs(f'<linearGradient id="{gid}" x1="0" y1="{_f(y - h)}" x2="0" y2="{_f(y + h * 0.15)}" gradientUnits="userSpaceOnUse">'
                                      f'<stop offset="0" stop-color="{light}"/><stop offset="0.5" stop-color="{base}"/><stop offset="1" stop-color="{dark}"/></linearGradient>')]
    out.append(f'<g fill="url(#{gid})">' + "".join(f'<path d="{d}"/>' for d in shapes) + "</g>")
    inner = [dabs([light, base, dark], seed + 3, (x - w / 2, y - h, x + w / 2, y + h * 0.2), int(w * h / 60), -4, (12, 34), (1.5, 4), (0.1, 0.28), 0.25, 10)]
    for i, (px, py, r) in enumerate(puffs):
        if 0 < i < n - 1 or True:
            a0, a1 = (math.radians(20), math.radians(120)) if rim_side < 0 else (math.radians(60), math.radians(160))
            inner.append(f'<path d="M {_f(px + r * 0.95 * math.cos(a0))} {_f(py + r * 0.95 * math.sin(a0))} A {_f(r * 0.95)} {_f(r * 0.95)} 0 0 1 '
                         f'{_f(px + r * 0.95 * math.cos(a1))} {_f(py + r * 0.95 * math.sin(a1))}" fill="none" stroke="{dark}" stroke-width="{_f(r * 0.18)}" '
                         f'stroke-linecap="round" opacity="0.28"/>')
    top = []
    for k in range(int(w) + 1):
        xx = x - w / 2 + k
        best = None
        for px, py, r in puffs:
            if abs(xx - px) < r:
                yy = py - math.sqrt(r * r - (xx - px) ** 2) * 0.92
                best = yy if best is None else min(best, yy)
        if best is not None:
            top.append((xx, best + 2.5))
    if top:
        sx = [p for p in top[::3]]
        fade = (f'<linearGradient id="{u}-rf" x1="{_f(x - w / 2)}" y1="0" x2="{_f(x + w / 2)}" y2="0" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="{rim}" stop-opacity="{0.9 if rim_side < 0 else 0.15}"/>'
                f'<stop offset="1" stop-color="{rim}" stop-opacity="{0.15 if rim_side < 0 else 0.9}"/></linearGradient>')
        inner.append(defs(fade) + f'<path d="M {" L ".join(f"{_f(a)} {_f(b)}" for a, b in sx)}" fill="none" stroke="url(#{u}-rf)" stroke-width="3" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(clip(f"{u}-c", shapes) + f'<g clip-path="url(#{u}-c)">' + "".join(inner) + "</g>")
    out.append("</g>")
    return "".join(out)


def sailboat_sil(u, x, y, s, seed):
    """Small moonlit sailboat on the water, with a broken reflection."""
    hull = C((x - 30 * s, y - 4 * s), (x + 30 * s, y - 4 * s), (x + 22 * s, y + 6 * s), (x - 22 * s, y + 6 * s))
    sail1 = f"M {_f(x - 2 * s)} {_f(y - 8 * s)} L {_f(x - 2 * s)} {_f(y - 62 * s)} Q {_f(x + 14 * s)} {_f(y - 40 * s)} {_f(x + 24 * s)} {_f(y - 8 * s)} Z"
    sail2 = f"M {_f(x - 6 * s)} {_f(y - 10 * s)} L {_f(x - 6 * s)} {_f(y - 52 * s)} Q {_f(x - 18 * s)} {_f(y - 30 * s)} {_f(x - 26 * s)} {_f(y - 10 * s)} Z"
    out = [f'<path d="{hull}" fill="#0A0C26"/>', f'<path d="{sail1}" fill="{CREAM}" opacity="0.92"/>', f'<path d="{sail2}" fill="#C8C2E8" opacity="0.85"/>',
           f'<path d="M {_f(x - 4 * s)} {_f(y - 66 * s)} L {_f(x - 4 * s)} {_f(y - 4 * s)}" stroke="#0A0C26" stroke-width="{_f(2 * s)}"/>',
           ink(sail1, GOLD_D, 1.4, seed, 1, 0.6)]
    rnd = random.Random(seed)
    for i in range(6):
        yy = y + 10 * s + i * 6 * s
        w = (26 - i * 3) * s
        out.append(f'<path d="M {_f(x - w / 2 + rnd.uniform(-3, 3))} {_f(yy)} l {_f(w)} 0" stroke="{CREAM}" stroke-width="{_f(2 * s)}" stroke-linecap="round" opacity="{0.4 - i * 0.05:.2f}"/>')
    return "".join(out)


def balloon(u, cx, cy, s, seed):
    """Painted hot-air balloon: striped envelope with shading and highlight, ropes, a wicker basket and a heart pennant."""
    env = C((cx, cy - 46 * s), (cx + 30 * s, cy - 38 * s), (cx + 40 * s, cy - 10 * s), (cx + 32 * s, cy + 20 * s), (cx + 12 * s, cy + 42 * s),
            (cx - 12 * s, cy + 42 * s), (cx - 32 * s, cy + 20 * s), (cx - 40 * s, cy - 10 * s), (cx - 30 * s, cy - 38 * s))
    out = [glow(f"{u}-gl", cx, cy, 70 * s, GOLD_L, 0.22, 0.3)]
    stripes = []
    cols = ["#E07A8E", "#F4E2B8", "#E8B04A", "#F4E2B8", "#E07A8E", "#F4E2B8", "#E8B04A"]
    for i, col in enumerate(cols):
        x0 = cx - 42 * s + i * 12 * s
        stripes.append(f'<path d="M {_f(x0)} {_f(cy - 50 * s)} Q {_f(cx + (x0 - cx) * 1.25)} {_f(cy)} {_f(cx + (x0 - cx) * 0.3)} {_f(cy + 46 * s)} '
                       f'L {_f(cx + (x0 + 12 * s - cx) * 0.3)} {_f(cy + 46 * s)} Q {_f(cx + (x0 + 12 * s - cx) * 1.25)} {_f(cy)} {_f(x0 + 12 * s)} {_f(cy - 50 * s)} Z" fill="{col}"/>')
    inner = "".join(stripes)
    inner += f'<path d="{blob(cx + 22 * s, cy + 8 * s, 30 * s, 44 * s, seed, 0.05, 12)}" fill="#2A1E58" opacity="0.35"/>'
    inner += f'<path d="M {_f(cx - 26 * s)} {_f(cy - 20 * s)} Q {_f(cx - 22 * s)} {_f(cy - 36 * s)} {_f(cx - 8 * s)} {_f(cy - 42 * s)}" stroke="#FFFFFF" stroke-width="{_f(4 * s)}" fill="none" stroke-linecap="round" opacity="0.6"/>'
    inner += dabs(["#FFFFFF", "#C0508A", "#F6D88E"], seed + 2, (cx - 40 * s, cy - 46 * s, cx + 40 * s, cy + 42 * s), 50, -90, (8 * s, 20 * s), (1, 2.5), (0.1, 0.3), 0.15)
    out.append(clip(f"{u}-ec", env) + f'<g clip-path="url(#{u}-ec)">{inner}</g>')
    out.append(ink(env, "#2A1E46", 2.4, seed, 2, 0.9))
    for dx in (-10, -3, 3, 10):
        out.append(ink(f"M {_f(cx + dx * 1.2 * s)} {_f(cy + 42 * s)} L {_f(cx + dx * 0.8 * s)} {_f(cy + 58 * s)}", "#2A1E46", 1.5, seed + 1, 1, 0.9))
    basket = C((cx - 11 * s, cy + 57 * s), (cx + 11 * s, cy + 57 * s), (cx + 9 * s, cy + 72 * s), (cx - 9 * s, cy + 72 * s))
    out.append(body(f"{u}-bk", basket, (cx - 12 * s, cy + 56 * s, cx + 12 * s, cy + 73 * s), "#B9773A", ["#8E5426", "#D9A060"], seed + 4, n=16, angle=0,
                    length=(4, 9), width=(0.8, 1.6), line="#2A1E46", lw=1.8))
    out.append(ink(f"M {_f(cx - 10 * s)} {_f(cy + 63 * s)} L {_f(cx + 10 * s)} {_f(cy + 63 * s)}", "#5A3418", 1.2, seed, 1, 0.8))
    # pennant with a heart trailing from the basket
    out.append(ink(f"M {_f(cx + 10 * s)} {_f(cy + 66 * s)} q {_f(16 * s)} {_f(4 * s)} {_f(30 * s)} {_f(-2 * s)}", CREAM, 1.4, seed, 1, 0.8))
    from common import heart
    out.append(heart(cx + 44 * s, cy + 62 * s, 7 * s, "#E07A8E"))
    return "".join(out)


@design("to-the-moon-and-back")
def d_moon_and_back():
    u = "nsc-tmb"
    mx, my, mr = 418, 176, 80
    out = [sky(u, 1401, "fire", [(400, 170, 240, 150, -15), (120, 300, 180, 110, 20)], (40, 330, 560, 60, 40), 120,
               keep=lambda x, y: math.hypot(x - mx, y - my) > mr + 12)]
    out.append(pmoon(f"{u}-mn", mx, my, mr, 1410, halo_r=2.3, halo_op=0.55))
    # a dotted orbit from the balloon, round the moon and back again
    a = math.radians(-14)
    ocx, ocy, orx, ory = 318, 196, 226, 104
    pts = []
    for i in range(0, 361, 3):
        t = math.radians(i)
        x, y = orx * math.cos(t), ory * math.sin(t)
        pts.append((ocx + x * math.cos(a) - y * math.sin(a), ocy + x * math.sin(a) + y * math.cos(a)))
    front = [p for i, p in enumerate(pts) if not (math.hypot(p[0] - mx, p[1] - my) < mr + 4 and i * 3 < 180)]
    out.append(f'<path d="{L(*front[:-1])}" fill="none" stroke="{GOLD_L}" stroke-width="2.4" stroke-dasharray="1 9" stroke-linecap="round" opacity="0.9"/>')
    for i in (14, 44, 80, 104):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        out.append(f'<path d="M -6 -5 L 3 0 L -6 5" fill="none" stroke="{GOLD_L}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" '
                   f'transform="translate({_f(x0)} {_f(y0)}) rotate({ang:.0f})" opacity="0.9"/>')
    out.append(balloon(f"{u}-bl", 132, 172, 1.2, 1420))
    for x, y, r in ((520, 330, 9), (300, 80, 7), (90, 330, 6), (250, 290, 5), (540, 70, 6)):
        out.append(spark(x, y, r, GOLD_L, 0.95))
    out.append(night_cloud(f"{u}-c1", 470, 286, 170, 64, 1430, rim_side=-1, op=0.95))
    # lettering: three lines, script / gilded caps / script
    out.append(script(300, 398, "love you", 58, CREAM, 360, shadow="#05040E", sd=(2, 3)))
    out.append(bword(f"{u}-tx", 304, 466, "TO THE MOON", CINZEL, 64, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 1440, max_w=450, ls=6,
                     shadow="#05040E", sd=0.04, angle=-14))
    out.append(label_rules(300, 520, "AND BACK", MONO, 22, GOLD_L, 7, 1450, gap=14, line_w=40))
    out.append(finish(u, 1460))
    return "".join(out)


def dandelion(u, cx, cy, r, seed, gone=(-50, 40)):
    """A dandelion clock: glowing seed head of pappus umbrellas on fine stalks, a few already blown away (angles in gone)."""
    rnd = random.Random(seed)
    out = [glow(f"{u}-gl", cx, cy, r * 1.9, "#FFF2CC", 0.32, 0.3)]
    stalks, tufts = [], []
    k = 0
    for ring, (rr, n) in enumerate(((r, 34), (r * 0.82, 26))):
        for i in range(n):
            a = 360 * i / n + rnd.uniform(-4, 4) + ring * 6
            aa = ((a + 180) % 360) - 180
            if gone[0] < aa < gone[1] and rnd.random() < 0.8:
                continue
            ar = math.radians(a)
            ex, ey = cx + rr * math.cos(ar), cy + rr * math.sin(ar)
            stalks.append(f"M {_f(cx + 6 * math.cos(ar))} {_f(cy + 6 * math.sin(ar))} L {_f(ex)} {_f(ey)}")
            for j in range(-2, 3):
                b = ar + j * 0.32
                tufts.append(f"M {_f(ex)} {_f(ey)} l {_f(9 * math.cos(b))} {_f(9 * math.sin(b))}")
            k += 1
    out.append(f'<g stroke="{CREAM}" stroke-width="1.2" opacity="0.7" stroke-linecap="round">' + "".join(f'<path d="{d}"/>' for d in stalks) + "</g>")
    out.append(f'<g stroke="#FFFFFF" stroke-width="1.3" opacity="0.85" stroke-linecap="round">' + "".join(f'<path d="{d}"/>' for d in tufts) + "</g>")
    out.append(f'<path d="{blob(cx, cy, 8, 8, seed, 0.1, 10)}" fill="{GOLD_D}"/><path d="{blob(cx - 1, cy - 1, 4.5, 4.5, seed + 1, 0.1, 8)}" fill="{GOLD_L}"/>')
    return "".join(out)


def seed_float(x, y, ang, s, op=1.0):
    """One drifting dandelion seed: stalk and umbrella."""
    a = math.radians(ang)
    tx, ty = x + 14 * s * math.cos(a), y + 14 * s * math.sin(a)
    out = [f'<path d="M {_f(x)} {_f(y)} L {_f(tx)} {_f(ty)}" stroke="{CREAM}" stroke-width="1.3" stroke-linecap="round" opacity="{op * 0.85:.2f}"/>',
           f'<circle cx="{_f(x)}" cy="{_f(y)}" r="1.6" fill="{GOLD_L}" opacity="{op:.2f}"/>']
    for j in range(-3, 4):
        b = a + j * 0.3
        out.append(f'<path d="M {_f(tx)} {_f(ty)} l {_f(8 * s * math.cos(b))} {_f(8 * s * math.sin(b))}" stroke="#FFFFFF" stroke-width="1.2" '
                   f'stroke-linecap="round" opacity="{op * 0.9:.2f}"/>')
    return "".join(out)


@design("make-a-wish")
def d_make_a_wish():
    u = "nsc-wish"
    out = [sky(u, 1501, "air", [(330, 200, 280, 130, -10), (120, 420, 160, 90, 20)], (40, 470, 560, 120, 50), 120, text_shade=False)]
    # a shooting star across the top
    sx0, sy0, sx1, sy1 = 410, 66, 520, 104
    out.append(defs(lg(f"{u}-ss", [(0, "#FFFFFF", 0), (1, "#FFF6DA", 0.9)], 0, 0, 1, 0)))
    ang = math.degrees(math.atan2(sy1 - sy0, sx1 - sx0))
    ln = math.hypot(sx1 - sx0, sy1 - sy0)
    out.append(f'<path d="M 0 -1 L {_f(ln)} -3.2 L {_f(ln)} 3.2 L 0 1 Z" fill="url(#{u}-ss)" transform="translate({sx0} {sy0}) rotate({ang:.1f})"/>')
    out.append(glow(f"{u}-sg", sx1, sy1, 26, GOLD_L, 0.6, 0.3) + spark(sx1, sy1, 14, "#FFFFFF", 1))
    # hill with grass, the dandelion clock on its stem, leaves
    hill = f'M -10 600 L -10 520 {L((-10, 520), (120, 498), (260, 512), (400, 536), (520, 526), (610, 512))[1:].replace("M", "L", 1)} L 610 600 Z'
    out.append(defs(lg(f"{u}-hl", [(0, "#1E2258"), (1, "#0A0C26")])) + f'<path d="{hill}" fill="url(#{u}-hl)"/>')
    out.append(f'<path d="{L((-10, 520), (120, 498), (260, 512), (400, 536), (520, 526), (610, 512))}" fill="none" stroke="#8A88D0" stroke-width="2" opacity="0.5"/>')
    rnd = random.Random(1502)
    blades = []
    for _ in range(140):
        x = rnd.uniform(-5, 605)
        y0 = 520 - 22 * math.sin(math.pi * min(max(x, 0), 400) / 520) + rnd.uniform(-2, 14)
        h = rnd.uniform(8, 20)
        blades.append(f'<path d="M {_f(x)} {_f(y0)} q {_f(rnd.uniform(-3, 3))} {_f(-h / 2)} {_f(rnd.uniform(-6, 6))} {_f(-h)}" stroke="{rnd.choice(["#2E3474", "#3A3E88", "#1A1E50"])}" '
                      f'stroke-width="{rnd.uniform(1.2, 2.4):.1f}" fill="none" stroke-linecap="round"/>')
    out.append("".join(blades))
    hx, hy, hr = 196, 352, 66
    stem = tube([(178, 560), (172, 500), (180, 430), (hx, hy + 8)], 7, 4)
    out.append(f'<path d="{stem}" fill="#2C3A5A"/>' + ink(stem, "#9AB2C8", 1.4, 1503, 1, 0.5))
    for side, (lx, ly, ang) in ((-1, (176, 540, -150)), (1, (180, 546, -30)), (1, (176, 556, -10))):
        pts = []
        for i in range(9):
            t = i / 8
            d = 70 * t
            w = 10 * math.sin(math.pi * t) * (1.4 if i % 2 else 0.6)
            a = math.radians(ang)
            pts.append((lx + d * math.cos(a) - w * math.sin(a), ly + d * math.sin(a) + w * math.cos(a)))
        for i in range(8, -1, -1):
            t = i / 8
            d = 70 * t
            w = 4 * math.sin(math.pi * t)
            a = math.radians(ang)
            pts.append((lx + d * math.cos(a) + w * math.sin(a), ly + d * math.sin(a) - w * math.cos(a)))
        out.append(f'<path d="{smooth_closed(pts)}" fill="#26305A"/>' + ink(smooth_closed(pts), "#7A92B8", 1.2, 1504, 1, 0.45))
    out.append(dandelion(f"{u}-dd", hx, hy, hr, 1505))
    # seeds drifting away and turning into stars
    path = [(hx + 56, hy - 26), (300, 330), (360, 316), (420, 350), (470, 330), (520, 300)]
    for i in range(16):
        t = i / 15
        seg = min(int(t * (len(path) - 1)), len(path) - 2)
        f = t * (len(path) - 1) - seg
        x = path[seg][0] + (path[seg + 1][0] - path[seg][0]) * f + rnd.uniform(-22, 22)
        y = path[seg][1] + (path[seg + 1][1] - path[seg][1]) * f + rnd.uniform(-34, 34)
        if t < 0.6:
            out.append(seed_float(x, y, -90 + rnd.uniform(-40, 40), 1.0 - 0.3 * t))
        else:
            out.append(glow(f"{u}-st{i}", x, y, 14, GOLD_L, 0.5, 0.3) + spark(x, y, 4 + 7 * (t - 0.6) * 2.5, "#FFFFFF" if i % 2 else GOLD_L, 0.95))
    # lettering: centred at the top
    out.append(script(300, 142, "make a", 60, CREAM, 360, shadow="#05040E", sd=(2, 3)))
    out.append(bword(f"{u}-tx", 306, 246, "WISH", CINZEL, 116, GOLD, [GOLD_L, GOLD_D, "#F6D88E", "#C99A48"], 1510, max_w=330, ls=14,
                     shadow="#05040E", sd=0.035, angle=-14))
    out.append(finish(u, 1520))
    return "".join(out)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
